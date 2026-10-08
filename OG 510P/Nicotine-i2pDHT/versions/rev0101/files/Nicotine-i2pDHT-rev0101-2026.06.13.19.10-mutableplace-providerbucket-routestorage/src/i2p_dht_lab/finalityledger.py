"""Finality ledger after effect reconciliation.

rev0058 treats terminality as another signed local observation.  An effect that
reconciled as commit/abort may be marked terminal; an effect that reconciled as
retry/dead-letter remains sticky watch memory.  The ledger exists to stop a
future cleanup or retry lane from turning an unresolved side effect into
accidental finality after restart.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .effectreconcile import EffectReconcileDecisionKind
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction, SideEffectPhase

FINALITY_LEDGER_DOMAIN = DOMAIN + b":finality-ledger-v1:"


class FinalityMarkerKind(str, Enum):
    TERMINAL_COMMIT = "terminal_commit"
    TERMINAL_ABORT = "terminal_abort"
    RETRY_PENDING = "retry_pending"
    DEAD_LETTER_HELD = "dead_letter_held"


class FinalityLedgerDecisionKind(str, Enum):
    ACCEPT_TERMINAL_COMMIT = "accept_terminal_commit"
    ACCEPT_TERMINAL_ABORT = "accept_terminal_abort"
    ACCEPT_RETRY_PENDING = "accept_retry_pending"
    ACCEPT_DEAD_LETTER_HELD = "accept_dead_letter_held"
    EMPTY_NO_MARKERS = "empty_no_markers"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_UNRESOLVED_RECONCILE = "hold_unresolved_reconcile"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_PREMATURE_TERMINALITY = "quarantine_premature_terminality"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"


@dataclass(frozen=True)
class FinalityMarker:
    marker_kind: FinalityMarkerKind
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    reconcile_digest: bytes
    dead_letter_digest: bytes
    retry_quorum_digest: bytes
    journal_digest: bytes
    hard_negative_count: int
    sequence: int
    previous_marker_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "marker_kind", FinalityMarkerKind(self.marker_kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        if self.final_phase is not None:
            object.__setattr__(self, "final_phase", SideEffectPhase(self.final_phase))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("finality marker needs profile/service/family/path")
        if min(self.hard_negative_count, self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("counts/times/sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("reconcile_digest", self.reconcile_digest),
            ("dead_letter_digest", self.dead_letter_digest),
            ("retry_quorum_digest", self.retry_quorum_digest),
            ("journal_digest", self.journal_digest),
            ("previous_marker_digest", self.previous_marker_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.marker_kind.value,
            b"action": self.action.value,
            b"phase": b"" if self.final_phase is None else self.final_phase.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"reconcile": self.reconcile_digest,
            b"dead": self.dead_letter_digest,
            b"retry": self.retry_quorum_digest,
            b"journal": self.journal_digest,
            b"hard": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_marker_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return FINALITY_LEDGER_DOMAIN + b":marker-sig:" + bencode(self.unsigned_bvalue())

    @property
    def marker_core_digest(self) -> bytes:
        return sha256(FINALITY_LEDGER_DOMAIN + b":marker-core:" + bencode(self.unsigned_bvalue()))

    @property
    def marker_digest(self) -> bytes:
        return sha256(FINALITY_LEDGER_DOMAIN + b":marker-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class FinalityLedgerReport:
    decision_kind: FinalityLedgerDecisionKind
    accept: bool
    watch: bool
    terminal: bool
    reason: str
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_marker_digest: bytes
    marker_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
    highest_sequence: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    retry_required: bool
    dead_letter_required: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    value = getattr(report, "report_digest", None)
    if isinstance(value, bytes) and len(value) == 32:
        return value
    raise ValueError("component report lacks report_digest")


def _accept(report: Any | None) -> bool:
    return bool(getattr(report, "accept", False)) if report is not None else False


def _watch(report: Any | None) -> bool:
    return bool(getattr(report, "watch", False)) if report is not None else False


def _quarantined(report: Any | None) -> bool:
    return bool(getattr(report, "quarantined", False)) if report is not None else False


def marker_kind_for_reconcile(reconcile_report: Any) -> FinalityMarkerKind:
    decision = getattr(reconcile_report, "decision_kind", None)
    if decision == EffectReconcileDecisionKind.ACCEPT_RECONCILED_COMMIT:
        return FinalityMarkerKind.TERMINAL_COMMIT
    if decision == EffectReconcileDecisionKind.ACCEPT_RECONCILED_ABORT:
        return FinalityMarkerKind.TERMINAL_ABORT
    if decision == EffectReconcileDecisionKind.ACCEPT_RETRY:
        return FinalityMarkerKind.RETRY_PENDING
    return FinalityMarkerKind.DEAD_LETTER_HELD


def make_finality_marker(
    *,
    keypair: DhtKeypair,
    marker_kind: FinalityMarkerKind,
    effect_reconcile_report: Any,
    dead_letter_report: Any | None = None,
    retry_quorum_report: Any | None = None,
    side_effect_journal_report: Any | None = None,
    sequence: int,
    previous_marker_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> FinalityMarker:
    marker = FinalityMarker(
        marker_kind=marker_kind,
        action=getattr(effect_reconcile_report, "action"),
        final_phase=getattr(effect_reconcile_report, "final_phase", None),
        profile_id=getattr(effect_reconcile_report, "profile_id"),
        service_name=getattr(effect_reconcile_report, "service_name"),
        scope_digest=getattr(effect_reconcile_report, "scope_digest"),
        request_digest=getattr(effect_reconcile_report, "request_digest"),
        payload_digest=getattr(effect_reconcile_report, "payload_digest"),
        idempotency_key=getattr(effect_reconcile_report, "idempotency_key"),
        reconcile_digest=_digest(effect_reconcile_report),
        dead_letter_digest=_digest(dead_letter_report),
        retry_quorum_digest=_digest(retry_quorum_report),
        journal_digest=_digest(side_effect_journal_report),
        hard_negative_count=int(getattr(effect_reconcile_report, "hard_negative_count", 0) or 0),
        sequence=sequence,
        previous_marker_digest=previous_marker_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(marker, signature=keypair.sign(marker.signature_payload()))


def assess_finality_ledger(
    markers: Iterable[FinalityMarker],
    *,
    effect_reconcile_report: Any,
    dead_letter_report: Any | None = None,
    retry_quorum_report: Any | None = None,
    side_effect_journal_report: Any | None = None,
    now: int,
    previous_seen_marker_digests: Iterable[bytes] = (),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> FinalityLedgerReport:
    action = SideEffectAction(getattr(effect_reconcile_report, "action"))
    final_phase_raw = getattr(effect_reconcile_report, "final_phase", None)
    final_phase = SideEffectPhase(final_phase_raw) if final_phase_raw is not None else None
    profile_id = getattr(effect_reconcile_report, "profile_id")
    service_name = getattr(effect_reconcile_report, "service_name")
    scope_digest = getattr(effect_reconcile_report, "scope_digest")
    request_digest = getattr(effect_reconcile_report, "request_digest")
    payload_digest = getattr(effect_reconcile_report, "payload_digest")
    idempotency_key = getattr(effect_reconcile_report, "idempotency_key")
    component_digests = tuple(_digest(component) for component in (effect_reconcile_report, dead_letter_report, retry_quorum_report, side_effect_journal_report))
    retry_required = bool(getattr(effect_reconcile_report, "retry_required", False))
    dead_letter_required = bool(getattr(effect_reconcile_report, "dead_letter_required", False))
    common = dict(action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests, retry_required=retry_required, dead_letter_required=dead_letter_required)
    if not _accept(effect_reconcile_report) or _quarantined(effect_reconcile_report):
        return _report(FinalityLedgerDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "effect reconcile did not accept", **common)
    hard = int(getattr(effect_reconcile_report, "hard_negative_count", 0) or 0)
    if hard:
        return _report(FinalityLedgerDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "hard negatives block finality", hard_negative_count=hard, **common)
    live = list(markers)
    if not live:
        return _report(FinalityLedgerDecisionKind.EMPTY_NO_MARKERS, False, True, False, "no finality markers", **common)
    seen = set(previous_seen_marker_digests)
    ordered = sorted(live, key=lambda marker: (marker.sequence, marker.marker_digest))
    highest: FinalityMarker | None = None
    seq_to_core: dict[int, bytes] = {}
    previous_digest = ZERO_DIGEST
    family_ids: set[str] = set()
    path_families: set[str] = set()
    for marker in ordered:
        if not marker.live(now):
            return _report(FinalityLedgerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, False, "expired or future marker", **common)
        if not marker.verifies():
            return _report(FinalityLedgerDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, False, "bad marker signature", **common)
        if marker.marker_digest in seen:
            return _report(FinalityLedgerDecisionKind.QUARANTINE_REPLAY, False, False, False, "replayed finality marker", **common)
        if marker.sequence in seq_to_core and seq_to_core[marker.sequence] != marker.marker_core_digest:
            return _report(FinalityLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-sequence finality fork", **common)
        seq_to_core[marker.sequence] = marker.marker_core_digest
        if marker.sequence == 0:
            if marker.previous_marker_digest != ZERO_DIGEST:
                return _report(FinalityLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "first marker has nonzero previous", **common)
        elif marker.previous_marker_digest != previous_digest:
            return _report(FinalityLedgerDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "marker previous link mismatch", **common)
        previous_digest = marker.marker_digest
        highest = marker
        family_ids.add(marker.family_id)
        path_families.add(marker.path_family)
    assert highest is not None
    expected_kind = marker_kind_for_reconcile(effect_reconcile_report)
    if highest.marker_kind is not expected_kind:
        if highest.marker_kind in (FinalityMarkerKind.TERMINAL_COMMIT, FinalityMarkerKind.TERMINAL_ABORT) and (retry_required or dead_letter_required or _watch(effect_reconcile_report)):
            return _report(FinalityLedgerDecisionKind.QUARANTINE_PREMATURE_TERMINALITY, False, False, False, "terminal marker on unresolved reconcile", **common)
        return _report(FinalityLedgerDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "marker kind does not match reconcile decision", **common)
    for attr, expected in (("action", action), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
        if getattr(highest, attr) != expected:
            return _report(FinalityLedgerDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, f"{attr} drift", **common)
    if highest.reconcile_digest != component_digests[0] or highest.dead_letter_digest != component_digests[1] or highest.retry_quorum_digest != component_digests[2] or highest.journal_digest != component_digests[3]:
        return _report(FinalityLedgerDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "component digest drift", **common)
    if highest.hard_negative_count:
        return _report(FinalityLedgerDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "marker carries hard negatives", hard_negative_count=highest.hard_negative_count, **common)
    terminal = highest.marker_kind in (FinalityMarkerKind.TERMINAL_COMMIT, FinalityMarkerKind.TERMINAL_ABORT)
    if len(family_ids) < min_family_count:
        return _report(FinalityLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low finality family diversity", accepted_marker_digest=highest.marker_digest, marker_digests=tuple(marker.marker_digest for marker in ordered), highest_sequence=highest.sequence, family_count=len(family_ids), path_family_count=len(path_families), **common)
    if len(path_families) < min_path_family_count:
        return _report(FinalityLedgerDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low finality path diversity", accepted_marker_digest=highest.marker_digest, marker_digests=tuple(marker.marker_digest for marker in ordered), highest_sequence=highest.sequence, family_count=len(family_ids), path_family_count=len(path_families), **common)
    if terminal and (retry_required or dead_letter_required):
        return _report(FinalityLedgerDecisionKind.QUARANTINE_PREMATURE_TERMINALITY, False, False, False, "terminal marker while retry/dead-letter required", **common)
    if highest.marker_kind is FinalityMarkerKind.TERMINAL_COMMIT:
        return _report(FinalityLedgerDecisionKind.ACCEPT_TERMINAL_COMMIT, True, False, True, "terminal commit finality accepted", accepted_marker_digest=highest.marker_digest, marker_digests=tuple(marker.marker_digest for marker in ordered), highest_sequence=highest.sequence, family_count=len(family_ids), path_family_count=len(path_families), **common)
    if highest.marker_kind is FinalityMarkerKind.TERMINAL_ABORT:
        return _report(FinalityLedgerDecisionKind.ACCEPT_TERMINAL_ABORT, True, False, True, "terminal abort finality accepted", accepted_marker_digest=highest.marker_digest, marker_digests=tuple(marker.marker_digest for marker in ordered), highest_sequence=highest.sequence, family_count=len(family_ids), path_family_count=len(path_families), **common)
    if highest.marker_kind is FinalityMarkerKind.RETRY_PENDING:
        return _report(FinalityLedgerDecisionKind.ACCEPT_RETRY_PENDING, True, True, False, "retry finality remains pending", accepted_marker_digest=highest.marker_digest, marker_digests=tuple(marker.marker_digest for marker in ordered), highest_sequence=highest.sequence, family_count=len(family_ids), path_family_count=len(path_families), **common)
    if highest.marker_kind is FinalityMarkerKind.DEAD_LETTER_HELD:
        return _report(FinalityLedgerDecisionKind.ACCEPT_DEAD_LETTER_HELD, True, True, False, "dead-letter finality remains held", accepted_marker_digest=highest.marker_digest, marker_digests=tuple(marker.marker_digest for marker in ordered), highest_sequence=highest.sequence, family_count=len(family_ids), path_family_count=len(path_families), **common)
    return _report(FinalityLedgerDecisionKind.HOLD_UNRESOLVED_RECONCILE, False, True, False, "unresolved reconcile", **common)


def _report(kind: FinalityLedgerDecisionKind, accept: bool, watch: bool, terminal: bool, reason: str, *, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], retry_required: bool, dead_letter_required: bool, accepted_marker_digest: bytes = ZERO_DIGEST, marker_digests: tuple[bytes, ...] = (), highest_sequence: int = -1, family_count: int = 0, path_family_count: int = 0, hard_negative_count: int = 0) -> FinalityLedgerReport:
    digest = sha256(FINALITY_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"terminal": 1 if terminal else 0,
        b"reason": reason,
        b"action": action.value,
        b"phase": b"" if final_phase is None else final_phase.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_marker_digest,
        b"markers": marker_digests,
        b"components": component_digests,
        b"seq": highest_sequence,
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
        b"retry_required": 1 if retry_required else 0,
        b"dead_required": 1 if dead_letter_required else 0,
    }))
    return FinalityLedgerReport(kind, accept, watch, terminal, reason, action, final_phase, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_marker_digest, marker_digests, component_digests, highest_sequence, family_count, path_family_count, hard_negative_count, retry_required, dead_letter_required, digest)
