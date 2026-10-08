"""Retry quorum after recovery/dead-letter watch.

rev0057 keeps retries local and exact-boundary.  Multiple signed retry
observations can request another attempt, but they do not erase dead-letter
memory, hard negatives, or idempotency boundaries.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .chaosbudget import ChaosLane
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

RETRY_QUORUM_DOMAIN = DOMAIN + b":retry-quorum-v1:"


class RetryVoteKind(str, Enum):
    RETRY_READY = "retry_ready"
    RETRY_AFTER = "retry_after"
    STILL_DEAD_LETTER = "still_dead_letter"
    REFUSE_USEFULLY = "refuse_usefully"
    HARD_NEGATIVE = "hard_negative"


class RetryQuorumDecisionKind(str, Enum):
    ACCEPT_RETRY_QUORUM = "accept_retry_quorum"
    ACCEPT_REFUSAL_BACKOFF = "accept_refusal_backoff"
    HOLD_NOT_ENOUGH_READY = "hold_not_enough_ready"
    HOLD_DEAD_LETTER = "hold_dead_letter"
    HOLD_CHAOS_BUDGET = "hold_chaos_budget"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_VOTES = "empty_no_votes"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_MISSING_RETRY_BUDGET = "quarantine_missing_retry_budget"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class RetryVote:
    vote_kind: RetryVoteKind
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    recovery_mesh_digest: bytes
    dead_letter_digest: bytes
    chaos_budget_digest: bytes
    attempt_number: int
    retry_after: int
    hard_negative_count: int
    sequence: int
    previous_vote_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "vote_kind", RetryVoteKind(self.vote_kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("retry vote needs profile/service/family/path")
        if min(self.attempt_number, self.retry_after, self.hard_negative_count, self.sequence) < 0:
            raise ValueError("retry counts must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("retry vote expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("recovery_mesh_digest", self.recovery_mesh_digest),
            ("dead_letter_digest", self.dead_letter_digest),
            ("chaos_budget_digest", self.chaos_budget_digest),
            ("previous_vote_digest", self.previous_vote_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"vote": self.vote_kind.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"recovery": self.recovery_mesh_digest,
            b"dead": self.dead_letter_digest,
            b"chaos": self.chaos_budget_digest,
            b"attempt": self.attempt_number,
            b"retry_after": self.retry_after,
            b"hard": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_vote_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return RETRY_QUORUM_DOMAIN + b":vote-sig:" + bencode(self.unsigned_bvalue())

    @property
    def vote_core_digest(self) -> bytes:
        return sha256(RETRY_QUORUM_DOMAIN + b":vote-core:" + bencode(self.unsigned_bvalue()))

    @property
    def vote_digest(self) -> bytes:
        return sha256(RETRY_QUORUM_DOMAIN + b":vote-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class RetryQuorumReport:
    decision_kind: RetryQuorumDecisionKind
    accept: bool
    watch: bool
    reason: str
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_vote_digest: bytes
    vote_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    attempt_number: int
    ready_count: int
    refusal_count: int
    retry_after: int
    highest_sequence: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "vote_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def make_retry_vote(
    *,
    keypair: DhtKeypair,
    vote_kind: RetryVoteKind,
    recovery_mesh_report: Any,
    dead_letter_report: Any,
    chaos_budget_report: Any,
    attempt_number: int,
    sequence: int,
    previous_vote_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    retry_after: int = 0,
    hard_negative_count: int = 0,
) -> RetryVote:
    unsigned = RetryVote(
        vote_kind=vote_kind,
        action=SideEffectAction(getattr(recovery_mesh_report, "action")),
        profile_id=getattr(recovery_mesh_report, "profile_id"),
        service_name=getattr(recovery_mesh_report, "service_name"),
        scope_digest=getattr(recovery_mesh_report, "scope_digest"),
        request_digest=getattr(recovery_mesh_report, "request_digest"),
        payload_digest=getattr(recovery_mesh_report, "payload_digest"),
        idempotency_key=getattr(recovery_mesh_report, "idempotency_key"),
        recovery_mesh_digest=_digest(recovery_mesh_report),
        dead_letter_digest=_digest(dead_letter_report),
        chaos_budget_digest=_digest(chaos_budget_report),
        attempt_number=attempt_number,
        retry_after=retry_after,
        hard_negative_count=hard_negative_count,
        sequence=sequence,
        previous_vote_digest=previous_vote_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_retry_quorum(
    votes: Iterable[RetryVote],
    *,
    recovery_mesh_report: Any,
    dead_letter_report: Any,
    chaos_budget_report: Any,
    now: int,
    previous_seen_vote_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    min_ready_votes: int = 2,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
    require_retry_budget: bool = True,
) -> RetryQuorumReport:
    vote_t = tuple(votes)
    action = SideEffectAction(getattr(recovery_mesh_report, "action"))
    profile_id = getattr(recovery_mesh_report, "profile_id")
    service_name = getattr(recovery_mesh_report, "service_name")
    scope_digest = getattr(recovery_mesh_report, "scope_digest")
    request_digest = getattr(recovery_mesh_report, "request_digest")
    payload_digest = getattr(recovery_mesh_report, "payload_digest")
    idempotency_key = getattr(recovery_mesh_report, "idempotency_key")
    component_digests = (_digest(recovery_mesh_report), _digest(dead_letter_report), _digest(chaos_budget_report))
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not vote_t:
        return _report(RetryQuorumDecisionKind.EMPTY_NO_VOTES, False, False, "retry quorum needs votes", votes=vote_t, **common)
    if not _accept(dead_letter_report) or _quarantined(dead_letter_report):
        return _report(RetryQuorumDecisionKind.HOLD_DEAD_LETTER, False, True, "dead-letter report did not accept", votes=vote_t, **common)
    if not _accept(chaos_budget_report) or _quarantined(chaos_budget_report):
        return _report(RetryQuorumDecisionKind.HOLD_CHAOS_BUDGET, False, True, "chaos budget did not accept", votes=vote_t, **common)
    lanes = tuple(getattr(chaos_budget_report, "lanes", ()))
    if require_retry_budget and ChaosLane.RETRY_PROBE not in lanes:
        return _report(RetryQuorumDecisionKind.QUARANTINE_MISSING_RETRY_BUDGET, False, False, "retry probe budget lane missing", votes=vote_t, **common)
    seen = set(previous_seen_vote_digests)
    by_sequence: dict[int, RetryVote] = {}
    for vote in vote_t:
        if not vote.verifies():
            return _report(RetryQuorumDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad retry vote signature", votes=vote_t, **common)
        if not vote.live(now):
            return _report(RetryQuorumDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future retry vote", votes=vote_t, **common)
        if vote.vote_digest in seen:
            return _report(RetryQuorumDecisionKind.QUARANTINE_REPLAY, False, False, "replayed retry vote", votes=vote_t, **common)
        if highest_seen_sequence is not None and vote.sequence < highest_seen_sequence:
            return _report(RetryQuorumDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "retry sequence rollback", votes=vote_t, **common)
        prior = by_sequence.get(vote.sequence)
        if prior is not None and prior.vote_core_digest != vote.vote_core_digest:
            return _report(RetryQuorumDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence retry fork", votes=vote_t, **common)
        by_sequence[vote.sequence] = vote
        if (vote.profile_id, vote.service_name, vote.action) != (profile_id, service_name, action):
            return _report(RetryQuorumDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "profile/service/action drift", votes=vote_t, **common)
        if (vote.scope_digest, vote.request_digest, vote.payload_digest, vote.idempotency_key) != (scope_digest, request_digest, payload_digest, idempotency_key):
            return _report(RetryQuorumDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "scope/request/payload/idempotency drift", votes=vote_t, **common)
        if (vote.recovery_mesh_digest, vote.dead_letter_digest, vote.chaos_budget_digest) != component_digests:
            return _report(RetryQuorumDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", votes=vote_t, **common)
        if vote.hard_negative_count:
            return _report(RetryQuorumDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block retry", votes=vote_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_vote_digest != left.vote_digest:
            return _report(RetryQuorumDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "retry previous-link mismatch", votes=vote_t, **common)
    families = {vote.family_id for vote in vote_t}
    paths = {vote.path_family for vote in vote_t}
    if len(families) < min_family_count:
        return _report(RetryQuorumDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "retry quorum needs family diversity", votes=vote_t, **common)
    if len(paths) < min_path_family_count:
        return _report(RetryQuorumDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "retry quorum needs path diversity", votes=vote_t, **common)
    ready = sum(1 for vote in vote_t if vote.vote_kind is RetryVoteKind.RETRY_READY)
    refusals = sum(1 for vote in vote_t if vote.vote_kind is RetryVoteKind.REFUSE_USEFULLY)
    if ready >= min_ready_votes:
        return _report(RetryQuorumDecisionKind.ACCEPT_RETRY_QUORUM, True, False, "retry quorum accepted", votes=vote_t, accepted=ordered[-1], **common)
    if refusals and ready == 0:
        return _report(RetryQuorumDecisionKind.ACCEPT_REFUSAL_BACKOFF, True, True, "useful refusal backoff accepted", votes=vote_t, accepted=ordered[-1], **common)
    return _report(RetryQuorumDecisionKind.HOLD_NOT_ENOUGH_READY, False, True, "not enough retry-ready votes", votes=vote_t, **common)


def _report(kind: RetryQuorumDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], votes: Iterable[RetryVote], accepted: RetryVote | None = None) -> RetryQuorumReport:
    vote_t = tuple(votes)
    digests = tuple(vote.vote_digest for vote in vote_t)
    ready = sum(1 for vote in vote_t if vote.vote_kind is RetryVoteKind.RETRY_READY)
    refusals = sum(1 for vote in vote_t if vote.vote_kind is RetryVoteKind.REFUSE_USEFULLY)
    retry_after = max((vote.retry_after for vote in vote_t), default=0)
    highest = max((vote.sequence for vote in vote_t), default=-1)
    families = {vote.family_id for vote in vote_t}
    paths = {vote.path_family for vote in vote_t}
    hard = sum(vote.hard_negative_count for vote in vote_t)
    attempt = max((vote.attempt_number for vote in vote_t), default=0)
    accepted_digest = accepted.vote_digest if accepted else ZERO_DIGEST
    digest = sha256(RETRY_QUORUM_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": action.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_digest,
        b"votes": list(digests),
        b"components": list(component_digests),
        b"attempt": attempt,
        b"ready": ready,
        b"refusals": refusals,
        b"retry_after": retry_after,
        b"highest": highest,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return RetryQuorumReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_digest, digests, component_digests, attempt, ready, refusals, retry_after, highest, len(families), len(paths), hard, digest)
