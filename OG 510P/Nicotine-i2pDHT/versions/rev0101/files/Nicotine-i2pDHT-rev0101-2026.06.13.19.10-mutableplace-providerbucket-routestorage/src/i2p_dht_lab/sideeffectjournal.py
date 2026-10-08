"""Append-only side-effect journal for the no-network public edge.

rev0053 does not run handlers or send network bytes.  It does, however, model
restart-safe local memory for future side effects.  A profile-edge acceptance or
handler capsule acceptance is not enough: a prepare/commit/abort entry must bind
the exact action, idempotency key, payload, components, and previous journal
entry before sticky side-effect memory advances.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .liveadapter import LiveAdapterMode
from .moderationquarantine import ZERO_DIGEST

SIDE_EFFECT_JOURNAL_DOMAIN = DOMAIN + b":side-effect-journal-v1:"


class SideEffectAction(str, Enum):
    INBOUND_HANDLER_WORK = "inbound_handler_work"
    OUTBOUND_PUBLIC_SEND = "outbound_public_send"
    BIDIRECTIONAL_BRIDGE_TICK = "bidirectional_bridge_tick"


class SideEffectPhase(str, Enum):
    PREPARE = "prepare"
    COMMIT = "commit"
    ABORT = "abort"


class SideEffectJournalDecisionKind(str, Enum):
    ACCEPT_PREPARE = "accept_prepare"
    ACCEPT_COMMIT = "accept_commit"
    ACCEPT_ABORT = "accept_abort"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_PROFILE_EDGE = "hold_profile_edge"
    HOLD_LIVE_ADAPTER = "hold_live_adapter"
    HOLD_HANDLER_CAPSULE = "hold_handler_capsule"
    HOLD_SAM_CANARY = "hold_sam_canary"
    HOLD_COMPONENT_WATCH = "hold_component_watch"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    EMPTY_NO_ENTRIES = "empty_no_entries"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_PHASE_REGRESSION = "quarantine_phase_regression"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_ACTION_DRIFT = "quarantine_action_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_IDEMPOTENCY_CONFLICT = "quarantine_idempotency_conflict"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


_PHASE_ORDER = {SideEffectPhase.PREPARE: 0, SideEffectPhase.COMMIT: 1, SideEffectPhase.ABORT: 1}


@dataclass(frozen=True)
class SideEffectJournalEntry:
    phase: SideEffectPhase
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    side_effect_target_digest: bytes
    profile_edge_digest: bytes
    live_adapter_digest: bytes
    handler_capsule_digest: bytes
    sam_canary_digest: bytes
    hard_negative_count: int
    sequence: int
    previous_entry_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "phase", SideEffectPhase(self.phase))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("side-effect journal entry needs profile/service/family/path")
        if self.hard_negative_count < 0 or self.sequence < 0:
            raise ValueError("counts and sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("side_effect_target_digest", self.side_effect_target_digest),
            ("profile_edge_digest", self.profile_edge_digest),
            ("live_adapter_digest", self.live_adapter_digest),
            ("handler_capsule_digest", self.handler_capsule_digest),
            ("sam_canary_digest", self.sam_canary_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"phase": self.phase.value,
            b"action": self.action.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"target": self.side_effect_target_digest,
            b"profile_edge": self.profile_edge_digest,
            b"live_adapter": self.live_adapter_digest,
            b"handler": self.handler_capsule_digest,
            b"sam_canary": self.sam_canary_digest,
            b"hard_negatives": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return SIDE_EFFECT_JOURNAL_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(SIDE_EFFECT_JOURNAL_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(SIDE_EFFECT_JOURNAL_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class SideEffectJournalReport:
    decision_kind: SideEffectJournalDecisionKind
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
    family_count: int
    path_family_count: int
    highest_sequence: int
    final_phase: SideEffectPhase | None
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "canary_digest", "transcript_digest"):
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


def make_side_effect_entry(
    *,
    keypair: DhtKeypair,
    phase: SideEffectPhase,
    action: SideEffectAction,
    profile_id: str,
    service_name: str,
    scope_digest: bytes,
    request_digest: bytes,
    payload_digest: bytes,
    idempotency_key: bytes,
    side_effect_target_digest: bytes,
    profile_edge_report: Any,
    live_adapter_report: Any,
    handler_capsule_report: Any | None = None,
    sam_canary_report: Any | None = None,
    hard_negative_count: int,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> SideEffectJournalEntry:
    unsigned = SideEffectJournalEntry(
        phase=phase,
        action=action,
        profile_id=profile_id,
        service_name=service_name,
        scope_digest=scope_digest,
        request_digest=request_digest,
        payload_digest=payload_digest,
        idempotency_key=idempotency_key,
        side_effect_target_digest=side_effect_target_digest,
        profile_edge_digest=_digest(profile_edge_report),
        live_adapter_digest=_digest(live_adapter_report),
        handler_capsule_digest=_digest(handler_capsule_report),
        sam_canary_digest=_digest(sam_canary_report),
        hard_negative_count=hard_negative_count,
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def _report(kind: SideEffectJournalDecisionKind, accept: bool, watch: bool, reason: str, *, action: SideEffectAction, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, accepted: SideEffectJournalEntry | None = None, entries: Iterable[SideEffectJournalEntry] = (), components: Iterable[bytes] = ()) -> SideEffectJournalReport:
    entry_t = tuple(entries)
    digests = tuple(entry.entry_digest for entry in entry_t)
    families = {entry.family_id for entry in entry_t}
    paths = {entry.path_family for entry in entry_t}
    highest = max((entry.sequence for entry in entry_t), default=-1)
    accepted_digest = accepted.entry_digest if accepted else ZERO_DIGEST
    final_phase = accepted.phase if accepted else None
    component_t = tuple(components)
    digest = sha256(SIDE_EFFECT_JOURNAL_DOMAIN + b":report:" + bencode({
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
        b"components": list(component_t),
        b"families": len(families),
        b"paths": len(paths),
        b"highest": highest,
        b"phase": final_phase.value if final_phase else "none",
    }))
    return SideEffectJournalReport(kind, accept, watch, reason, action, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_digest, digests, component_t, len(families), len(paths), highest, final_phase, digest)


def _action_needs_handler(action: SideEffectAction) -> bool:
    return action in (SideEffectAction.INBOUND_HANDLER_WORK, SideEffectAction.BIDIRECTIONAL_BRIDGE_TICK)


def _action_needs_sam(action: SideEffectAction) -> bool:
    return action in (SideEffectAction.OUTBOUND_PUBLIC_SEND, SideEffectAction.BIDIRECTIONAL_BRIDGE_TICK)


def assess_side_effect_journal(
    entries: Iterable[SideEffectJournalEntry],
    *,
    profile_edge_report: Any,
    live_adapter_report: Any,
    handler_capsule_report: Any | None = None,
    sam_canary_report: Any | None = None,
    now: int,
    expected_action: SideEffectAction,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    expected_idempotency_key: bytes,
    expected_side_effect_target_digest: bytes,
    previous_seen_entry_digests: Iterable[bytes] = (),
    highest_seen_sequence: int | None = None,
    allow_component_watch: bool = False,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SideEffectJournalReport:
    entry_t = tuple(entries)
    action = SideEffectAction(expected_action)
    components = (_digest(profile_edge_report), _digest(live_adapter_report), _digest(handler_capsule_report), _digest(sam_canary_report))
    common = dict(action=action, profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, idempotency_key=expected_idempotency_key, entries=entry_t, components=components)
    if not entry_t:
        return _report(SideEffectJournalDecisionKind.EMPTY_NO_ENTRIES, False, False, "side-effect journal needs entries", **common)
    if not _accept(profile_edge_report) or _quarantined(profile_edge_report):
        return _report(SideEffectJournalDecisionKind.HOLD_PROFILE_EDGE if not _quarantined(profile_edge_report) else SideEffectJournalDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "profile edge must accept", **common)
    if not _accept(live_adapter_report) or _quarantined(live_adapter_report):
        return _report(SideEffectJournalDecisionKind.HOLD_LIVE_ADAPTER if not _quarantined(live_adapter_report) else SideEffectJournalDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "live adapter must accept", **common)
    if _action_needs_handler(action) and (not _accept(handler_capsule_report) or _quarantined(handler_capsule_report)):
        return _report(SideEffectJournalDecisionKind.HOLD_HANDLER_CAPSULE if not _quarantined(handler_capsule_report) else SideEffectJournalDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "handler capsule must accept", **common)
    if _action_needs_sam(action) and (not _accept(sam_canary_report) or _quarantined(sam_canary_report)):
        return _report(SideEffectJournalDecisionKind.HOLD_SAM_CANARY if not _quarantined(sam_canary_report) else SideEffectJournalDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "SAM canary must accept", **common)
    if any(_watch(component) for component in (profile_edge_report, live_adapter_report, handler_capsule_report, sam_canary_report)) and not allow_component_watch:
        return _report(SideEffectJournalDecisionKind.HOLD_COMPONENT_WATCH, False, True, "component watch pressure must be carried", **common)

    seen = set(previous_seen_entry_digests)
    by_sequence: dict[int, SideEffectJournalEntry] = {}
    by_idem: dict[bytes, tuple[bytes, SideEffectAction]] = {}
    for entry in entry_t:
        if not entry.verifies():
            return _report(SideEffectJournalDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad side-effect journal signature", **common)
        if not entry.live(now):
            return _report(SideEffectJournalDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "expired or future journal entry", **common)
        if entry.entry_digest in seen:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_REPLAY, False, False, "side-effect journal replay", **common)
        if highest_seen_sequence is not None and entry.sequence < highest_seen_sequence:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "side-effect sequence rollback", **common)
        prior = by_sequence.get(entry.sequence)
        if prior is not None and prior.entry_core_digest != entry.entry_core_digest:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence side-effect fork", **common)
        by_sequence[entry.sequence] = entry
        idem_prior = by_idem.get(entry.idempotency_key)
        idem_signature = (entry.payload_digest + entry.side_effect_target_digest, entry.action)
        if idem_prior is not None and idem_prior != idem_signature:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, False, "idempotency key reused with different effect", **common)
        by_idem[entry.idempotency_key] = idem_signature
        if entry.profile_id != expected_profile_id:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_PROFILE_DRIFT, False, False, "profile drift", **common)
        if entry.service_name != expected_service_name:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_SERVICE_DRIFT, False, False, "service drift", **common)
        if entry.action is not action:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_ACTION_DRIFT, False, False, "action drift", **common)
        if entry.scope_digest != expected_scope_digest:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, "scope drift", **common)
        if entry.request_digest != expected_request_digest:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_REQUEST_DRIFT, False, False, "request drift", **common)
        if entry.payload_digest != expected_payload_digest:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "payload drift", **common)
        if entry.idempotency_key != expected_idempotency_key:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_IDEMPOTENCY_CONFLICT, False, False, "unexpected idempotency key", **common)
        if entry.side_effect_target_digest != expected_side_effect_target_digest:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, False, "target drift", **common)
        if (entry.profile_edge_digest, entry.live_adapter_digest, entry.handler_capsule_digest, entry.sam_canary_digest) != components:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", **common)
        if entry.hard_negative_count:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block side effect", **common)
    ordered = sorted(by_sequence.values(), key=lambda item: item.sequence)
    for left, right in zip(ordered, ordered[1:]):
        if right.sequence == left.sequence + 1 and right.previous_entry_digest != left.entry_digest:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "journal previous-link mismatch", **common)
        if _PHASE_ORDER[right.phase] < _PHASE_ORDER[left.phase]:
            return _report(SideEffectJournalDecisionKind.QUARANTINE_PHASE_REGRESSION, False, False, "journal phase regressed", **common)
    families = len({entry.family_id for entry in ordered})
    paths = len({entry.path_family for entry in ordered})
    if families < min_family_count:
        return _report(SideEffectJournalDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "journal needs more family diversity", **common)
    if paths < min_path_family_count:
        return _report(SideEffectJournalDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "journal needs more path diversity", **common)
    latest = ordered[-1]
    component_watch = any(_watch(component) for component in (profile_edge_report, live_adapter_report, handler_capsule_report, sam_canary_report))
    if component_watch:
        return _report(SideEffectJournalDecisionKind.ACCEPT_WITH_WATCH, True, True, "side effect accepted with watch", accepted=latest, **common)
    if latest.phase is SideEffectPhase.PREPARE:
        kind = SideEffectJournalDecisionKind.ACCEPT_PREPARE
    elif latest.phase is SideEffectPhase.COMMIT:
        kind = SideEffectJournalDecisionKind.ACCEPT_COMMIT
    else:
        kind = SideEffectJournalDecisionKind.ACCEPT_ABORT
    return _report(kind, True, False, "side-effect journal accepted", accepted=latest, **common)


def action_from_live_adapter_mode(mode: LiveAdapterMode) -> SideEffectAction:
    mode = LiveAdapterMode(mode)
    if mode is LiveAdapterMode.INBOUND_HANDLER_WORK:
        return SideEffectAction.INBOUND_HANDLER_WORK
    if mode is LiveAdapterMode.OUTBOUND_PUBLIC_SEND:
        return SideEffectAction.OUTBOUND_PUBLIC_SEND
    return SideEffectAction.BIDIRECTIONAL_BRIDGE_TICK
