"""Dead-letter lane for ambiguous post-restart effects.

rev0057 treats a prepared-only, ambiguous, or watch-carrying effect as sticky
protocol data.  A dead-letter entry is not a failure log.  It is signed,
previous-linked local memory that prevents cleanup/retry/reconcile code from
quietly reinterpreting a public-edge side effect after restart.
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
from .sideeffectjournal import SideEffectAction, SideEffectPhase

DEAD_LETTER_DOMAIN = DOMAIN + b":dead-letter-v1:"


class DeadLetterKind(str, Enum):
    PREPARED_ONLY = "prepared_only"
    AMBIGUOUS_COMMIT = "ambiguous_commit"
    AMBIGUOUS_ABORT = "ambiguous_abort"
    COMPONENT_WATCH = "component_watch"
    RETRY_EXHAUSTED = "retry_exhausted"
    HARD_NEGATIVE = "hard_negative"


class DeadLetterDecisionKind(str, Enum):
    ACCEPT_DEAD_LETTER = "accept_dead_letter"
    ACCEPT_WITH_RETRY_WATCH = "accept_with_retry_watch"
    EMPTY_NO_ENTRIES = "empty_no_entries"
    HOLD_CHAOS_BUDGET = "hold_chaos_budget"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_PHASE_DRIFT = "quarantine_phase_drift"
    QUARANTINE_MISSING_DEAD_LETTER_BUDGET = "quarantine_missing_dead_letter_budget"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class DeadLetterEntry:
    kind: DeadLetterKind
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    effect_seal_digest: bytes
    recovery_mesh_digest: bytes
    side_effect_journal_digest: bytes
    chaos_budget_digest: bytes
    observed_phase: SideEffectPhase | None
    hard_negative_count: int
    retry_after: int
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", DeadLetterKind(self.kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if self.observed_phase is not None:
            object.__setattr__(self, "observed_phase", SideEffectPhase(self.observed_phase))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("dead-letter entry needs profile/service/family/path")
        if min(self.hard_negative_count, self.retry_after, self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("dead-letter counts and times must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("dead-letter expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("effect_seal_digest", self.effect_seal_digest),
            ("recovery_mesh_digest", self.recovery_mesh_digest),
            ("side_effect_journal_digest", self.side_effect_journal_digest),
            ("chaos_budget_digest", self.chaos_budget_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.kind.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"effect_seal": self.effect_seal_digest,
            b"recovery": self.recovery_mesh_digest,
            b"journal": self.side_effect_journal_digest,
            b"chaos": self.chaos_budget_digest,
            b"phase": b"" if self.observed_phase is None else self.observed_phase.value,
            b"hard": self.hard_negative_count,
            b"retry_after": self.retry_after,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return DEAD_LETTER_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(DEAD_LETTER_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(DEAD_LETTER_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class DeadLetterReport:
    decision_kind: DeadLetterDecisionKind
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
    accepted_entry_digest: bytes
    entry_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    kinds: tuple[DeadLetterKind, ...]
    observed_phase: SideEffectPhase | None
    highest_sequence: int
    retry_after: int
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
    for attr in ("report_digest", "entry_digest", "seal_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def make_dead_letter_entry(
    *,
    keypair: DhtKeypair,
    kind: DeadLetterKind,
    effect_seal_report: Any,
    recovery_mesh_report: Any,
    side_effect_journal_report: Any,
    chaos_budget_report: Any,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    retry_after: int = 0,
    hard_negative_count: int = 0,
    observed_phase: SideEffectPhase | None = None,
) -> DeadLetterEntry:
    phase = observed_phase
    if phase is None:
        raw_phase = getattr(side_effect_journal_report, "final_phase", None) or getattr(effect_seal_report, "final_phase", None)
        phase = SideEffectPhase(raw_phase) if raw_phase is not None else None
    unsigned = DeadLetterEntry(
        kind=kind,
        action=SideEffectAction(getattr(effect_seal_report, "action")),
        profile_id=getattr(effect_seal_report, "profile_id"),
        service_name=getattr(effect_seal_report, "service_name"),
        scope_digest=getattr(effect_seal_report, "scope_digest"),
        request_digest=getattr(effect_seal_report, "request_digest"),
        payload_digest=getattr(effect_seal_report, "payload_digest"),
        idempotency_key=getattr(effect_seal_report, "idempotency_key"),
        effect_seal_digest=_digest(effect_seal_report),
        recovery_mesh_digest=_digest(recovery_mesh_report),
        side_effect_journal_digest=_digest(side_effect_journal_report),
        chaos_budget_digest=_digest(chaos_budget_report),
        observed_phase=phase,
        hard_negative_count=hard_negative_count,
        retry_after=retry_after,
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_dead_letter(
    entries: Iterable[DeadLetterEntry],
    *,
    effect_seal_report: Any,
    recovery_mesh_report: Any,
    side_effect_journal_report: Any,
    chaos_budget_report: Any,
    now: int,
    previous_seen_entry_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
    require_dead_letter_budget: bool = True,
) -> DeadLetterReport:
    entry_t = tuple(entries)
    action = SideEffectAction(getattr(effect_seal_report, "action"))
    profile_id = getattr(effect_seal_report, "profile_id")
    service_name = getattr(effect_seal_report, "service_name")
    scope_digest = getattr(effect_seal_report, "scope_digest")
    request_digest = getattr(effect_seal_report, "request_digest")
    payload_digest = getattr(effect_seal_report, "payload_digest")
    idempotency_key = getattr(effect_seal_report, "idempotency_key")
    component_digests = (_digest(effect_seal_report), _digest(recovery_mesh_report), _digest(side_effect_journal_report), _digest(chaos_budget_report))
    common = dict(action=action, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not entry_t:
        return _report(DeadLetterDecisionKind.EMPTY_NO_ENTRIES, False, False, "dead-letter lane needs entries", entries=entry_t, **common)
    if not _accept(chaos_budget_report) or _quarantined(chaos_budget_report):
        return _report(DeadLetterDecisionKind.HOLD_CHAOS_BUDGET, False, True, "chaos budget did not accept", entries=entry_t, **common)
    lanes = tuple(getattr(chaos_budget_report, "lanes", ()))
    if require_dead_letter_budget and ChaosLane.DEAD_LETTER not in lanes:
        return _report(DeadLetterDecisionKind.QUARANTINE_MISSING_DEAD_LETTER_BUDGET, False, False, "dead-letter budget lane missing", entries=entry_t, **common)
    seen = set(previous_seen_entry_digests)
    by_sequence: dict[int, DeadLetterEntry] = {}
    for entry in entry_t:
        if not entry.verifies():
            return _report(DeadLetterDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad dead-letter signature", entries=entry_t, **common)
        if not entry.live(now):
            return _report(DeadLetterDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future dead-letter entry", entries=entry_t, **common)
        if entry.entry_digest in seen:
            return _report(DeadLetterDecisionKind.QUARANTINE_REPLAY, False, False, "replayed dead-letter entry", entries=entry_t, **common)
        if highest_seen_sequence is not None and entry.sequence < highest_seen_sequence:
            return _report(DeadLetterDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "dead-letter sequence rollback", entries=entry_t, **common)
        prior = by_sequence.get(entry.sequence)
        if prior is not None and prior.entry_core_digest != entry.entry_core_digest:
            return _report(DeadLetterDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence dead-letter fork", entries=entry_t, **common)
        by_sequence[entry.sequence] = entry
        if (entry.profile_id, entry.service_name, entry.action) != (profile_id, service_name, action):
            return _report(DeadLetterDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "profile/service/action drift", entries=entry_t, **common)
        if (entry.scope_digest, entry.request_digest, entry.payload_digest, entry.idempotency_key) != (scope_digest, request_digest, payload_digest, idempotency_key):
            return _report(DeadLetterDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "scope/request/payload/idempotency drift", entries=entry_t, **common)
        if (entry.effect_seal_digest, entry.recovery_mesh_digest, entry.side_effect_journal_digest, entry.chaos_budget_digest) != component_digests:
            return _report(DeadLetterDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", entries=entry_t, **common)
        if entry.hard_negative_count:
            return _report(DeadLetterDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block dead-letter acceptance", entries=entry_t, **common)
        phase = getattr(side_effect_journal_report, "final_phase", None) or getattr(effect_seal_report, "final_phase", None)
        if phase is not None and entry.observed_phase is not None and SideEffectPhase(phase) is not entry.observed_phase:
            return _report(DeadLetterDecisionKind.QUARANTINE_PHASE_DRIFT, False, False, "observed phase drift", entries=entry_t, **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_entry_digest != left.entry_digest:
            return _report(DeadLetterDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "dead-letter previous-link mismatch", entries=entry_t, **common)
    families = {entry.family_id for entry in entry_t}
    paths = {entry.path_family for entry in entry_t}
    if len(families) < min_family_count:
        return _report(DeadLetterDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "dead-letter needs family diversity", entries=entry_t, **common)
    if len(paths) < min_path_family_count:
        return _report(DeadLetterDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "dead-letter needs path diversity", entries=entry_t, **common)
    if any(_watch(component) for component in (effect_seal_report, recovery_mesh_report, side_effect_journal_report, chaos_budget_report)):
        return _report(DeadLetterDecisionKind.ACCEPT_WITH_RETRY_WATCH, True, True, "dead-letter accepted carrying retry watch", entries=entry_t, accepted=ordered[-1], **common)
    return _report(DeadLetterDecisionKind.ACCEPT_DEAD_LETTER, True, False, "dead-letter accepted", entries=entry_t, accepted=ordered[-1], **common)


def _report(kind: DeadLetterDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], entries: Iterable[DeadLetterEntry], accepted: DeadLetterEntry | None = None) -> DeadLetterReport:
    entry_t = tuple(entries)
    digests = tuple(entry.entry_digest for entry in entry_t)
    kinds = tuple(sorted({entry.kind for entry in entry_t}, key=lambda item: item.value))
    highest = max((entry.sequence for entry in entry_t), default=-1)
    retry_after = max((entry.retry_after for entry in entry_t), default=0)
    families = {entry.family_id for entry in entry_t}
    paths = {entry.path_family for entry in entry_t}
    hard = sum(entry.hard_negative_count for entry in entry_t)
    phase = accepted.observed_phase if accepted else None
    accepted_digest = accepted.entry_digest if accepted else ZERO_DIGEST
    digest = sha256(DEAD_LETTER_DOMAIN + b":report:" + bencode({
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
        b"entries": list(digests),
        b"components": list(component_digests),
        b"kinds": [item.value for item in kinds],
        b"phase": b"" if phase is None else phase.value,
        b"highest": highest,
        b"retry_after": retry_after,
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
    }))
    return DeadLetterReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_digest, digests, component_digests, kinds, phase, highest, retry_after, len(families), len(paths), hard, digest)
