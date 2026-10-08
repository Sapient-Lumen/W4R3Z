"""Settlement lane after effect reconciliation.

rev0058 introduces a small post-reconcile ledger.  Reconciliation can say commit,
abort, retry, or keep dead-letter memory.  Settlement decides whether that local
observation may become sticky restart state, and it refuses to treat retry as a
clean terminal state.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .attestationpack import AttestationPackReport
from .bencode import BValue, bencode
from .deadletter import DeadLetterDecisionKind
from .effectreconcile import EffectReconcileDecisionKind
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction, SideEffectPhase

SETTLEMENT_DOMAIN = DOMAIN + b":settlement-lane-v1:"


class SettlementKind(str, Enum):
    COMMIT_SETTLED = "commit_settled"
    ABORT_SETTLED = "abort_settled"
    RETRY_HELD = "retry_held"
    DEAD_LETTER_HELD = "dead_letter_held"
    QUARANTINED = "quarantined"


class SettlementDecisionKind(str, Enum):
    ACCEPT_TERMINAL_SETTLEMENT = "accept_terminal_settlement"
    ACCEPT_RETRY_HOLD = "accept_retry_hold"
    ACCEPT_DEAD_LETTER_HOLD = "accept_dead_letter_hold"
    HOLD_MISSING_ATTESTATION = "hold_missing_attestation"
    HOLD_ATTESTATION_WATCH = "hold_attestation_watch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_COMPONENT_DIGEST_DRIFT = "quarantine_component_digest_drift"
    QUARANTINE_RETRY_DROPS_DEAD_LETTER = "quarantine_retry_drops_dead_letter"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class SettlementEntry:
    settlement_kind: SettlementKind
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    effect_reconcile_digest: bytes
    dead_letter_digest: bytes
    retry_quorum_digest: bytes
    attestation_pack_digest: bytes
    dead_letter_required: bool
    retry_required: bool
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
        object.__setattr__(self, "settlement_kind", SettlementKind(self.settlement_kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if self.final_phase is not None:
            object.__setattr__(self, "final_phase", SideEffectPhase(self.final_phase))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("settlement entry needs profile/service/family/path")
        if min(self.hard_negative_count, self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("settlement counts/times must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("settlement expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("effect_reconcile_digest", self.effect_reconcile_digest),
            ("dead_letter_digest", self.dead_letter_digest),
            ("retry_quorum_digest", self.retry_quorum_digest),
            ("attestation_pack_digest", self.attestation_pack_digest),
            ("previous_entry_digest", self.previous_entry_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.settlement_kind.value,
            b"action": self.action.value,
            b"phase": b"" if self.final_phase is None else self.final_phase.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"reconcile": self.effect_reconcile_digest,
            b"dead": self.dead_letter_digest,
            b"retry": self.retry_quorum_digest,
            b"pack": self.attestation_pack_digest,
            b"dead_required": 1 if self.dead_letter_required else 0,
            b"retry_required": 1 if self.retry_required else 0,
            b"hard": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_entry_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return SETTLEMENT_DOMAIN + b":entry-sig:" + bencode(self.unsigned_bvalue())

    @property
    def entry_core_digest(self) -> bytes:
        return sha256(SETTLEMENT_DOMAIN + b":entry-core:" + bencode(self.unsigned_bvalue()))

    @property
    def entry_digest(self) -> bytes:
        return sha256(SETTLEMENT_DOMAIN + b":entry-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class SettlementReport:
    decision_kind: SettlementDecisionKind
    accept: bool
    watch: bool
    reason: str
    settlement_kind: SettlementKind | None
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_entry_digest: bytes
    entry_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    highest_sequence: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    dead_letter_required: bool
    retry_required: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "entry_digest", "pack_digest"):
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


def settlement_kind_from_reconcile(effect_reconcile_report: Any) -> SettlementKind:
    kind = getattr(effect_reconcile_report, "decision_kind")
    if kind == EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT:
        return SettlementKind.COMMIT_SETTLED
    if kind == EffectReconcileDecisionKind.ACCEPT_RECONCILED_ABORT:
        return SettlementKind.ABORT_SETTLED
    if kind == EffectReconcileDecisionKind.ACCEPT_RETRY:
        return SettlementKind.RETRY_HELD
    if kind == EffectReconcileDecisionKind.ACCEPT_KEEP_DEAD_LETTER:
        return SettlementKind.DEAD_LETTER_HELD
    return SettlementKind.QUARANTINED


def make_settlement_entry(
    *,
    keypair: DhtKeypair,
    effect_reconcile_report: Any,
    dead_letter_report: Any,
    retry_quorum_report: Any | None = None,
    attestation_pack_report: Any | None = None,
    sequence: int,
    previous_entry_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
    settlement_kind: SettlementKind | None = None,
) -> SettlementEntry:
    settlement_kind = settlement_kind or settlement_kind_from_reconcile(effect_reconcile_report)
    unsigned = SettlementEntry(
        settlement_kind=settlement_kind,
        action=SideEffectAction(getattr(effect_reconcile_report, "action")),
        final_phase=getattr(effect_reconcile_report, "final_phase", None),
        profile_id=getattr(effect_reconcile_report, "profile_id"),
        service_name=getattr(effect_reconcile_report, "service_name"),
        scope_digest=getattr(effect_reconcile_report, "scope_digest"),
        request_digest=getattr(effect_reconcile_report, "request_digest"),
        payload_digest=getattr(effect_reconcile_report, "payload_digest"),
        idempotency_key=getattr(effect_reconcile_report, "idempotency_key"),
        effect_reconcile_digest=_digest(effect_reconcile_report),
        dead_letter_digest=_digest(dead_letter_report),
        retry_quorum_digest=_digest(retry_quorum_report),
        attestation_pack_digest=_digest(attestation_pack_report),
        dead_letter_required=bool(getattr(effect_reconcile_report, "dead_letter_required", False)),
        retry_required=bool(getattr(effect_reconcile_report, "retry_required", False)),
        hard_negative_count=int(getattr(effect_reconcile_report, "hard_negative_count", 0) or 0),
        sequence=sequence,
        previous_entry_digest=previous_entry_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(unsigned, signature=keypair.sign(unsigned.signature_payload()))


def assess_settlement_entries(
    entries: Iterable[SettlementEntry],
    *,
    effect_reconcile_report: Any,
    dead_letter_report: Any,
    retry_quorum_report: Any | None = None,
    attestation_pack_report: Any | None = None,
    now: int,
    require_attestation_pack: bool = True,
    previous_highest_sequence: int = -1,
    previous_seen_entry_digests: Iterable[bytes] = (),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> SettlementReport:
    entry_tuple = tuple(entries)
    action = SideEffectAction(getattr(effect_reconcile_report, "action"))
    final_phase = getattr(effect_reconcile_report, "final_phase", None)
    if final_phase is not None:
        final_phase = SideEffectPhase(final_phase)
    profile_id = getattr(effect_reconcile_report, "profile_id")
    service_name = getattr(effect_reconcile_report, "service_name")
    scope_digest = getattr(effect_reconcile_report, "scope_digest")
    request_digest = getattr(effect_reconcile_report, "request_digest")
    payload_digest = getattr(effect_reconcile_report, "payload_digest")
    idempotency_key = getattr(effect_reconcile_report, "idempotency_key")
    common = dict(action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key)
    components = (effect_reconcile_report, dead_letter_report, retry_quorum_report, attestation_pack_report)
    component_digests = tuple(_digest(c) for c in components)
    for component in (effect_reconcile_report, dead_letter_report):
        if not _accept(component) or _quarantined(component):
            return _report(SettlementDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "required component did not accept", settlement_kind=None, accepted_entry_digest=ZERO_DIGEST, entry_digests=(), component_digests=component_digests, highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, hard_negative_count=int(getattr(effect_reconcile_report, "hard_negative_count", 0) or 0), dead_letter_required=True, retry_required=False, **common)
    expected_kind = settlement_kind_from_reconcile(effect_reconcile_report)
    if require_attestation_pack and attestation_pack_report is None:
        return _report(SettlementDecisionKind.HOLD_MISSING_ATTESTATION, False, True, "missing attestation pack", settlement_kind=None, accepted_entry_digest=ZERO_DIGEST, entry_digests=(), component_digests=component_digests, highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, hard_negative_count=0, dead_letter_required=True, retry_required=bool(getattr(effect_reconcile_report, "retry_required", False)), **common)
    if attestation_pack_report is not None:
        if not _accept(attestation_pack_report) or _quarantined(attestation_pack_report):
            return _report(SettlementDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, "attestation pack not accepted", settlement_kind=None, accepted_entry_digest=ZERO_DIGEST, entry_digests=(), component_digests=component_digests, highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, hard_negative_count=int(getattr(attestation_pack_report, "hard_negative_count", 0) or 0), dead_letter_required=True, retry_required=False, **common)
        if _watch(attestation_pack_report) and expected_kind in (SettlementKind.COMMIT_SETTLED, SettlementKind.ABORT_SETTLED):
            return _report(SettlementDecisionKind.HOLD_ATTESTATION_WATCH, False, True, "terminal settlement cannot ignore attestation watch pressure", settlement_kind=None, accepted_entry_digest=ZERO_DIGEST, entry_digests=(), component_digests=component_digests, highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, hard_negative_count=0, dead_letter_required=True, retry_required=bool(getattr(effect_reconcile_report, "retry_required", False)), **common)
    hard = sum(int(getattr(component, "hard_negative_count", 0) or 0) for component in components if component is not None)
    if hard:
        return _report(SettlementDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, "hard negatives block settlement", settlement_kind=None, accepted_entry_digest=ZERO_DIGEST, entry_digests=(), component_digests=component_digests, highest_sequence=previous_highest_sequence, family_count=0, path_family_count=0, hard_negative_count=hard, dead_letter_required=True, retry_required=False, **common)
    valid: list[SettlementEntry] = []
    seen = set(previous_seen_entry_digests)
    for entry in entry_tuple:
        if not entry.verifies():
            return _entry_report(SettlementDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, "bad settlement signature", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if not entry.live(now):
            return _entry_report(SettlementDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, "settlement expired or from future", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if entry.entry_digest in seen:
            return _entry_report(SettlementDecisionKind.QUARANTINE_REPLAY, False, False, "settlement replay", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if entry.sequence <= previous_highest_sequence:
            return _entry_report(SettlementDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, False, "settlement sequence rollback", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if entry.settlement_kind is not expected_kind:
            return _entry_report(SettlementDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "settlement kind does not match reconcile", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if entry.action is not action or entry.profile_id != profile_id or entry.service_name != service_name:
            return _entry_report(SettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "action/profile/service drift", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if entry.scope_digest != scope_digest or entry.request_digest != request_digest or entry.payload_digest != payload_digest or entry.idempotency_key != idempotency_key:
            return _entry_report(SettlementDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, "scope/request/payload/idempotency drift", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if entry.effect_reconcile_digest != _digest(effect_reconcile_report) or entry.dead_letter_digest != _digest(dead_letter_report) or entry.retry_quorum_digest != _digest(retry_quorum_report) or entry.attestation_pack_digest != _digest(attestation_pack_report):
            return _entry_report(SettlementDecisionKind.QUARANTINE_COMPONENT_DIGEST_DRIFT, False, False, "component digest drift", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        if expected_kind is SettlementKind.RETRY_HELD and not entry.dead_letter_required:
            return _entry_report(SettlementDecisionKind.QUARANTINE_RETRY_DROPS_DEAD_LETTER, False, False, "retry settlement drops dead-letter memory", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        valid.append(entry)
    ordered = sorted(valid, key=lambda e: e.sequence)
    by_seq: dict[int, bytes] = {}
    for entry in ordered:
        prior = by_seq.get(entry.sequence)
        if prior is not None and prior != entry.entry_core_digest:
            return _entry_report(SettlementDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, "same-sequence settlement fork", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
        by_seq[entry.sequence] = entry.entry_core_digest
    for prev, nxt in zip(ordered, ordered[1:]):
        if nxt.previous_entry_digest != prev.entry_digest:
            return _entry_report(SettlementDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, "settlement previous-link mismatch", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
    families = {entry.family_id for entry in valid}
    paths = {entry.path_family for entry in valid}
    if len(families) < min_family_count:
        return _entry_report(SettlementDecisionKind.HOLD_MISSING_ATTESTATION, False, True, "low settlement family diversity", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
    if len(paths) < min_path_family_count:
        return _entry_report(SettlementDecisionKind.HOLD_MISSING_ATTESTATION, False, True, "low settlement path diversity", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)
    if expected_kind is SettlementKind.COMMIT_SETTLED or expected_kind is SettlementKind.ABORT_SETTLED:
        decision = SettlementDecisionKind.ACCEPT_TERMINAL_SETTLEMENT
        watch = False
    elif expected_kind is SettlementKind.RETRY_HELD:
        decision = SettlementDecisionKind.ACCEPT_RETRY_HOLD
        watch = True
    else:
        decision = SettlementDecisionKind.ACCEPT_DEAD_LETTER_HOLD
        watch = True
    return _entry_report(decision, True, watch, "settlement accepted", expected_kind, entry_tuple, valid, component_digests=component_digests, hard_negative_count=hard, **common)


def _entry_report(kind: SettlementDecisionKind, accept: bool, watch: bool, reason: str, settlement_kind: SettlementKind | None, all_entries: tuple[SettlementEntry, ...], valid: list[SettlementEntry], *, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], hard_negative_count: int) -> SettlementReport:
    entry_digests = tuple(entry.entry_digest for entry in valid)
    accepted = entry_digests[-1] if accept and entry_digests else ZERO_DIGEST
    highest = max((entry.sequence for entry in valid), default=-1)
    dead_required = any(entry.dead_letter_required for entry in valid) or kind in (SettlementDecisionKind.ACCEPT_RETRY_HOLD, SettlementDecisionKind.ACCEPT_DEAD_LETTER_HOLD)
    retry_required = any(entry.retry_required for entry in valid) or kind is SettlementDecisionKind.ACCEPT_RETRY_HOLD
    return _report(kind, accept, watch, reason, settlement_kind=settlement_kind, action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, accepted_entry_digest=accepted, entry_digests=entry_digests, component_digests=component_digests, highest_sequence=highest, family_count=len({e.family_id for e in valid}), path_family_count=len({e.path_family for e in valid}), hard_negative_count=hard_negative_count, dead_letter_required=dead_required, retry_required=retry_required)


def _report(kind: SettlementDecisionKind, accept: bool, watch: bool, reason: str, *, settlement_kind: SettlementKind | None, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, accepted_entry_digest: bytes, entry_digests: tuple[bytes, ...], component_digests: tuple[bytes, ...], highest_sequence: int, family_count: int, path_family_count: int, hard_negative_count: int, dead_letter_required: bool, retry_required: bool) -> SettlementReport:
    body = {
        b"kind": kind.value,
        b"settlement": b"" if settlement_kind is None else settlement_kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"action": SideEffectAction(action).value,
        b"phase": b"" if final_phase is None else SideEffectPhase(final_phase).value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_entry_digest,
        b"entries": list(entry_digests),
        b"components": list(component_digests),
        b"highest": highest_sequence,
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
        b"dead_required": 1 if dead_letter_required else 0,
        b"retry_required": 1 if retry_required else 0,
    }
    return SettlementReport(kind, accept, watch, reason, settlement_kind, SideEffectAction(action), final_phase, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_entry_digest, entry_digests, component_digests, highest_sequence, family_count, path_family_count, hard_negative_count, dead_letter_required, retry_required, sha256(SETTLEMENT_DOMAIN + b":report:" + bencode(body)))
