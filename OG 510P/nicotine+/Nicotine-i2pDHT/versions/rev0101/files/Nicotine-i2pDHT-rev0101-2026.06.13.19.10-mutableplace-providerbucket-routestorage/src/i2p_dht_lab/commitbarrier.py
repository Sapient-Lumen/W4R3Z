"""No-network public commit barrier.

rev0049 made public publication safer by adding dry-runs, public outbox staging,
witness/audit compaction, and scoped restart journals.  rev0050 adds the next
boundary: a public commit candidate.  This is still not a network publisher.  It
is the local, signed, exact-scope receipt that says a future publisher may be
allowed to consider one side effect *only after* dry-run, outbox, audit-gap,
egress, and journal reports all bind to the same boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .publicoutbox import PublicOutboxAction

COMMIT_BARRIER_DOMAIN = DOMAIN + b":commit-barrier-v1:"


class PublicCommitAction(str, Enum):
    COMMIT_REFRESH = "commit_refresh"
    COMMIT_WITHDRAW = "commit_withdraw"
    COMMIT_REPAIR = "commit_repair"


OUTBOX_TO_COMMIT_ACTION = {
    PublicOutboxAction.QUEUE_REFRESH: PublicCommitAction.COMMIT_REFRESH,
    PublicOutboxAction.QUEUE_WITHDRAW: PublicCommitAction.COMMIT_WITHDRAW,
    PublicOutboxAction.QUEUE_REPAIR: PublicCommitAction.COMMIT_REPAIR,
}


class CommitBarrierDecisionKind(str, Enum):
    ACCEPT_COMMIT_READY = "accept_commit_ready"
    ACCEPT_IDEMPOTENT_REPLAY = "accept_idempotent_replay"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_CANDIDATES = "empty_no_candidates"
    HOLD_DRY_RUN = "hold_dry_run"
    HOLD_OUTBOX = "hold_outbox"
    HOLD_AUDIT_GAP = "hold_audit_gap"
    HOLD_EGRESS = "hold_egress"
    HOLD_SCOPE_JOURNAL = "hold_scope_journal"
    HOLD_WATCH_DEBT = "hold_watch_debt"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_DRY_RUN = "quarantine_dry_run"
    QUARANTINE_OUTBOX = "quarantine_outbox"
    QUARANTINE_AUDIT_GAP = "quarantine_audit_gap"
    QUARANTINE_EGRESS = "quarantine_egress"
    QUARANTINE_SCOPE_JOURNAL = "quarantine_scope_journal"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_SUBJECT_DRIFT = "quarantine_subject_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"


@dataclass(frozen=True)
class PublicCommitCandidate:
    action: PublicCommitAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    public_payload_digest: bytes
    dry_run_digest: bytes
    outbox_digest: bytes
    audit_gap_digest: bytes
    egress_digest: bytes
    scope_journal_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    sequence: int
    previous_commit_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "action", PublicCommitAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("public commit candidate needs profile/service/family/path")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("subject_digest", self.subject_digest),
            ("public_payload_digest", self.public_payload_digest),
            ("dry_run_digest", self.dry_run_digest),
            ("outbox_digest", self.outbox_digest),
            ("audit_gap_digest", self.audit_gap_digest),
            ("egress_digest", self.egress_digest),
            ("scope_journal_digest", self.scope_journal_digest),
            ("idempotency_key", self.idempotency_key),
            ("public_effect_digest", self.public_effect_digest),
            ("previous_commit_digest", self.previous_commit_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"subject": self.subject_digest,
            b"payload": self.public_payload_digest,
            b"dry_run": self.dry_run_digest,
            b"outbox": self.outbox_digest,
            b"audit_gap": self.audit_gap_digest,
            b"egress": self.egress_digest,
            b"journal": self.scope_journal_digest,
            b"idem": self.idempotency_key,
            b"effect": self.public_effect_digest,
            b"seq": self.sequence,
            b"prev": self.previous_commit_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return COMMIT_BARRIER_DOMAIN + b":candidate-sig:" + bencode(self.unsigned_bvalue())

    @property
    def candidate_core_digest(self) -> bytes:
        return sha256(COMMIT_BARRIER_DOMAIN + b":candidate-core:" + bencode(self.unsigned_bvalue()))

    @property
    def candidate_digest(self) -> bytes:
        return sha256(COMMIT_BARRIER_DOMAIN + b":candidate-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class CommitBarrierReport:
    decision_kind: CommitBarrierDecisionKind
    accept: bool
    watch: bool
    reason: str
    profile_id: str
    service_name: str
    action: PublicCommitAction
    scope_digest: bytes
    request_digest: bytes
    subject_digest: bytes
    public_payload_digest: bytes
    accepted_candidate_digest: bytes
    idempotency_key: bytes
    public_effect_digest: bytes
    dry_run_digest: bytes
    outbox_digest: bytes
    audit_gap_digest: bytes
    egress_digest: bytes
    scope_journal_digest: bytes
    family_count: int
    path_family_count: int
    highest_sequence: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def allow(self) -> bool:
        return self.accept


def _component_digest(report: Any, *, attr_fallback: str = "report_digest") -> bytes:
    for attr in (attr_fallback, "report_digest", "transcript_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component report lacks a 32-byte digest")


def _component_accept(report: Any) -> bool:
    return bool(getattr(report, "accept", False))


def _component_watch(report: Any) -> bool:
    return bool(getattr(report, "watch", False))


def _component_quarantined(report: Any) -> bool:
    return bool(getattr(report, "quarantined", False))


def make_public_commit_candidate(
    *,
    keypair: DhtKeypair,
    action: PublicCommitAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    subject_digest: bytes,
    public_payload_digest: bytes,
    dry_run: Any,
    outbox: Any,
    audit_gap: Any,
    egress: Any,
    scope_journal: Any,
    idempotency_key: bytes,
    public_effect_digest: bytes,
    sequence: int,
    previous_commit_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> PublicCommitCandidate:
    candidate = PublicCommitCandidate(
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        subject_digest=subject_digest,
        public_payload_digest=public_payload_digest,
        dry_run_digest=_component_digest(dry_run),
        outbox_digest=_component_digest(outbox),
        audit_gap_digest=_component_digest(audit_gap),
        egress_digest=_component_digest(egress),
        scope_journal_digest=_component_digest(scope_journal),
        idempotency_key=idempotency_key,
        public_effect_digest=public_effect_digest,
        sequence=sequence,
        previous_commit_digest=previous_commit_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(candidate, signature=keypair.sign(candidate.signature_payload()))


def _report(
    kind: CommitBarrierDecisionKind,
    accept: bool,
    watch: bool,
    reason: str,
    *,
    profile_id: str,
    service_name: str,
    action: PublicCommitAction,
    scope_digest: bytes,
    request_digest: bytes,
    subject_digest: bytes,
    public_payload_digest: bytes,
    dry_run_digest: bytes,
    outbox_digest: bytes,
    audit_gap_digest: bytes,
    egress_digest: bytes,
    scope_journal_digest: bytes,
    candidates: Iterable[PublicCommitCandidate] = (),
    selected: PublicCommitCandidate | None = None,
    idempotency_key: bytes = ZERO_DIGEST,
    public_effect_digest: bytes = ZERO_DIGEST,
) -> CommitBarrierReport:
    candidate_tuple = tuple(sorted(candidates, key=lambda item: (item.sequence, item.candidate_digest)))
    families = len({item.family_id for item in candidate_tuple})
    paths = len({item.path_family for item in candidate_tuple})
    highest = selected.sequence if selected else max((item.sequence for item in candidate_tuple), default=-1)
    accepted = selected.candidate_digest if selected and accept else ZERO_DIGEST
    if selected is not None:
        idempotency_key = selected.idempotency_key
        public_effect_digest = selected.public_effect_digest
    digest = sha256(COMMIT_BARRIER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"action": action.value,
        b"scope": scope_digest,
        b"request": request_digest,
        b"subject": subject_digest,
        b"payload": public_payload_digest,
        b"accepted": accepted,
        b"idem": idempotency_key,
        b"effect": public_effect_digest,
        b"dry_run": dry_run_digest,
        b"outbox": outbox_digest,
        b"audit_gap": audit_gap_digest,
        b"egress": egress_digest,
        b"journal": scope_journal_digest,
        b"families": families,
        b"paths": paths,
        b"highest": highest,
        b"candidates": [item.candidate_digest for item in candidate_tuple],
    }))
    return CommitBarrierReport(kind, accept, watch, reason, profile_id, service_name, action, scope_digest, request_digest, subject_digest, public_payload_digest, accepted, idempotency_key, public_effect_digest, dry_run_digest, outbox_digest, audit_gap_digest, egress_digest, scope_journal_digest, families, paths, highest, digest)


def assess_commit_barrier(
    candidates: Iterable[PublicCommitCandidate],
    *,
    dry_run: Any,
    outbox: Any,
    audit_gap: Any,
    egress: Any,
    scope_journal: Any,
    now: int,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_subject_digest: bytes,
    expected_public_payload_digest: bytes,
    expected_action: PublicCommitAction | None = None,
    previous_highest_sequence: int = -1,
    previous_commit_digest: bytes = ZERO_DIGEST,
    previously_seen_candidates: Iterable[bytes] = (),
    committed_idempotency_effects: dict[bytes, bytes] | None = None,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    allow_watch_debt: bool = False,
) -> CommitBarrierReport:
    candidate_tuple = tuple(sorted(candidates, key=lambda item: (item.sequence, item.candidate_digest)))
    committed_idempotency_effects = committed_idempotency_effects or {}
    action = PublicCommitAction(expected_action or OUTBOX_TO_COMMIT_ACTION.get(getattr(outbox, "action", PublicOutboxAction.QUEUE_REFRESH), PublicCommitAction.COMMIT_REFRESH))
    component_digests = {
        "dry_run": _component_digest(dry_run),
        "outbox": _component_digest(outbox),
        "audit_gap": _component_digest(audit_gap),
        "egress": _component_digest(egress),
        "scope_journal": _component_digest(scope_journal),
    }

    if not candidate_tuple:
        return _report(CommitBarrierDecisionKind.EMPTY_NO_CANDIDATES, False, True, "no commit candidates supplied", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, **{k + "_digest": v for k, v in component_digests.items()})

    component_checks = (
        (dry_run, CommitBarrierDecisionKind.HOLD_DRY_RUN, CommitBarrierDecisionKind.QUARANTINE_DRY_RUN, "dry run"),
        (outbox, CommitBarrierDecisionKind.HOLD_OUTBOX, CommitBarrierDecisionKind.QUARANTINE_OUTBOX, "public outbox"),
        (audit_gap, CommitBarrierDecisionKind.HOLD_AUDIT_GAP, CommitBarrierDecisionKind.QUARANTINE_AUDIT_GAP, "audit gap"),
        (egress, CommitBarrierDecisionKind.HOLD_EGRESS, CommitBarrierDecisionKind.QUARANTINE_EGRESS, "egress"),
        (scope_journal, CommitBarrierDecisionKind.HOLD_SCOPE_JOURNAL, CommitBarrierDecisionKind.QUARANTINE_SCOPE_JOURNAL, "scope journal"),
    )
    for component, hold_kind, quarantine_kind, label in component_checks:
        if _component_quarantined(component):
            return _report(quarantine_kind, False, True, f"{label} quarantined", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if not _component_accept(component):
            return _report(hold_kind, False, _component_watch(component), f"{label} did not accept", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
    if not allow_watch_debt and any(_component_watch(component) for component, *_ in component_checks):
        return _report(CommitBarrierDecisionKind.HOLD_WATCH_DEBT, False, True, "component watch debt blocks public commit", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})

    seen = set(previously_seen_candidates)
    core_by_seq: dict[int, bytes] = {}
    selected: PublicCommitCandidate | None = None
    for candidate in candidate_tuple:
        if not candidate.verifies():
            return _report(CommitBarrierDecisionKind.QUARANTINE_BAD_SIGNATURE, False, True, "bad commit candidate signature", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if not candidate.live(now):
            return _report(CommitBarrierDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, True, "commit candidate expired or future", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.candidate_digest in seen:
            return _report(CommitBarrierDecisionKind.QUARANTINE_REPLAY, False, True, "commit candidate replay", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.sequence <= previous_highest_sequence:
            return _report(CommitBarrierDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, True, "commit candidate sequence rollback", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if previous_highest_sequence >= 0 and candidate.previous_commit_digest != previous_commit_digest:
            return _report(CommitBarrierDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, True, "commit previous digest mismatch", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        prev = core_by_seq.setdefault(candidate.sequence, candidate.candidate_core_digest)
        if prev != candidate.candidate_core_digest:
            return _report(CommitBarrierDecisionKind.QUARANTINE_SEQUENCE_FORK, False, True, "commit same-sequence fork", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.profile_id != expected_profile_id:
            return _report(CommitBarrierDecisionKind.QUARANTINE_PROFILE_DRIFT, False, True, "commit profile drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.service_name != expected_service_name:
            return _report(CommitBarrierDecisionKind.QUARANTINE_SERVICE_DRIFT, False, True, "commit service drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.scope_digest != expected_scope_digest:
            return _report(CommitBarrierDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "commit scope drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.request_digest != expected_request_digest:
            return _report(CommitBarrierDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "commit request drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.subject_digest != expected_subject_digest:
            return _report(CommitBarrierDecisionKind.QUARANTINE_SUBJECT_DRIFT, False, True, "commit subject drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.public_payload_digest != expected_public_payload_digest:
            return _report(CommitBarrierDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "commit payload drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if candidate.action is not action:
            return _report(CommitBarrierDecisionKind.QUARANTINE_ACTION_DRIFT, False, True, "commit action drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        if (
            candidate.dry_run_digest != component_digests["dry_run"]
            or candidate.outbox_digest != component_digests["outbox"]
            or candidate.audit_gap_digest != component_digests["audit_gap"]
            or candidate.egress_digest != component_digests["egress"]
            or candidate.scope_journal_digest != component_digests["scope_journal"]
        ):
            return _report(CommitBarrierDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, True, "commit component digest drift", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
        already = committed_idempotency_effects.get(candidate.idempotency_key)
        if already is not None:
            if already != candidate.public_effect_digest:
                return _report(CommitBarrierDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, True, "idempotency key maps to a different public effect", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, selected=candidate, **{k + "_digest": v for k, v in component_digests.items()})
            return _report(CommitBarrierDecisionKind.ACCEPT_IDEMPOTENT_REPLAY, True, True, "idempotent public commit replay with same effect", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, selected=candidate, **{k + "_digest": v for k, v in component_digests.items()})
        selected = candidate if selected is None or (candidate.sequence, candidate.candidate_digest) > (selected.sequence, selected.candidate_digest) else selected

    if len({item.family_id for item in candidate_tuple}) < min_family_diversity:
        return _report(CommitBarrierDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "commit candidate family diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
    if len({item.path_family for item in candidate_tuple}) < min_path_diversity:
        return _report(CommitBarrierDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "commit candidate path diversity too low", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, **{k + "_digest": v for k, v in component_digests.items()})
    assert selected is not None
    watch = any(_component_watch(component) for component, *_ in component_checks)
    return _report(CommitBarrierDecisionKind.ACCEPT_WITH_WATCH if watch else CommitBarrierDecisionKind.ACCEPT_COMMIT_READY, True, watch, "public commit candidate binds dry-run, outbox, audit-gap, egress, and journal at exact scope", profile_id=expected_profile_id, service_name=expected_service_name, action=action, scope_digest=expected_scope_digest, request_digest=expected_request_digest, subject_digest=expected_subject_digest, public_payload_digest=expected_public_payload_digest, candidates=candidate_tuple, selected=selected, **{k + "_digest": v for k, v in component_digests.items()})
