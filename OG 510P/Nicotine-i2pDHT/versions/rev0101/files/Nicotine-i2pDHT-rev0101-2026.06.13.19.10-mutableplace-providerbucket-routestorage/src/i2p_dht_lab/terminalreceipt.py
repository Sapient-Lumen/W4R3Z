"""Terminal receipt lane after finality ledger acceptance.

rev0059 treats terminality as two separate permissions: the finality ledger may
accept a terminal marker, but a future cleanup/side-effect boundary should carry
a small receipt that binds that finality to the exact request, payload,
idempotency key, prune-guard state, and local diversity.  This avoids a later
restart or compaction lane turning "finality once looked okay" into authority
without the component digests still being present.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Iterable

from .bencode import BValue, bencode
from .finalityledger import FinalityLedgerDecisionKind
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .pruneguard import PruneGuardDecisionKind
from .sideeffectjournal import SideEffectAction, SideEffectPhase

TERMINAL_RECEIPT_DOMAIN = DOMAIN + b":terminal-receipt-v1:"


class TerminalReceiptKind(str, Enum):
    TERMINAL_COMMIT = "terminal_commit"
    TERMINAL_ABORT = "terminal_abort"


class TerminalReceiptDecisionKind(str, Enum):
    ACCEPT_TERMINAL_COMMIT_RECEIPT = "accept_terminal_commit_receipt"
    ACCEPT_TERMINAL_ABORT_RECEIPT = "accept_terminal_abort_receipt"
    EMPTY_NO_RECEIPTS = "empty_no_receipts"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_NOT_ACCEPTED = "quarantine_component_not_accepted"
    QUARANTINE_NONTERMINAL_FINALITY = "quarantine_nonterminal_finality"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class TerminalReceipt:
    receipt_kind: TerminalReceiptKind
    action: SideEffectAction
    final_phase: SideEffectPhase
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    finality_digest: bytes
    accepted_marker_digest: bytes
    prune_guard_digest: bytes
    plan_digest: bytes
    hard_negative_count: int
    sequence: int
    previous_receipt_digest: bytes
    issued_at: int
    expires_at: int
    family_id: str
    path_family: str
    signer_public_key: bytes
    signature: bytes = b""

    def __post_init__(self) -> None:
        object.__setattr__(self, "receipt_kind", TerminalReceiptKind(self.receipt_kind))
        object.__setattr__(self, "action", SideEffectAction(self.action))
        object.__setattr__(self, "final_phase", SideEffectPhase(self.final_phase))
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("terminal receipt needs profile/service/family/path")
        if min(self.hard_negative_count, self.sequence, self.issued_at, self.expires_at) < 0:
            raise ValueError("counts/times/sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("expires_at must follow issued_at")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("idempotency_key", self.idempotency_key),
            ("finality_digest", self.finality_digest),
            ("accepted_marker_digest", self.accepted_marker_digest),
            ("prune_guard_digest", self.prune_guard_digest),
            ("plan_digest", self.plan_digest),
            ("previous_receipt_digest", self.previous_receipt_digest),
            ("signer_public_key", self.signer_public_key),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.signature and len(self.signature) != 64:
            raise ValueError("signature must be empty or Ed25519-sized")

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"kind": self.receipt_kind.value,
            b"action": self.action.value,
            b"phase": self.final_phase.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"finality": self.finality_digest,
            b"marker": self.accepted_marker_digest,
            b"prune": self.prune_guard_digest,
            b"plan": self.plan_digest,
            b"hard": self.hard_negative_count,
            b"seq": self.sequence,
            b"prev": self.previous_receipt_digest,
            b"issued": self.issued_at,
            b"expires": self.expires_at,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"signer": self.signer_public_key,
        }

    def signature_payload(self) -> bytes:
        return TERMINAL_RECEIPT_DOMAIN + b":receipt-sig:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_core_digest(self) -> bytes:
        return sha256(TERMINAL_RECEIPT_DOMAIN + b":receipt-core:" + bencode(self.unsigned_bvalue()))

    @property
    def receipt_digest(self) -> bytes:
        return sha256(TERMINAL_RECEIPT_DOMAIN + b":receipt-digest:" + self.signature_payload() + self.signature)

    def verifies(self) -> bool:
        return verify_signature(self.signer_public_key, self.signature_payload(), self.signature)

    def live(self, now: int) -> bool:
        return self.issued_at <= now < self.expires_at


@dataclass(frozen=True)
class TerminalReceiptReport:
    decision_kind: TerminalReceiptDecisionKind
    accept: bool
    watch: bool
    terminal: bool
    reason: str
    receipt_kind: TerminalReceiptKind | None
    action: SideEffectAction
    final_phase: SideEffectPhase | None
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    accepted_receipt_digest: bytes
    receipt_digests: tuple[bytes, ...]
    component_digests: tuple[bytes, ...]
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


def kind_for_finality(finality_report: Any) -> TerminalReceiptKind:
    decision = getattr(finality_report, "decision_kind", None)
    if decision == FinalityLedgerDecisionKind.ACCEPT_TERMINAL_COMMIT:
        return TerminalReceiptKind.TERMINAL_COMMIT
    if decision == FinalityLedgerDecisionKind.ACCEPT_TERMINAL_ABORT:
        return TerminalReceiptKind.TERMINAL_ABORT
    raise ValueError("finality report is not terminal")


def make_terminal_receipt(
    *,
    keypair: DhtKeypair,
    finality_report: Any,
    prune_guard_report: Any,
    sequence: int,
    previous_receipt_digest: bytes = ZERO_DIGEST,
    issued_at: int,
    expires_at: int,
    family_id: str,
    path_family: str,
) -> TerminalReceipt:
    receipt = TerminalReceipt(
        receipt_kind=kind_for_finality(finality_report),
        action=getattr(finality_report, "action"),
        final_phase=getattr(finality_report, "final_phase"),
        profile_id=getattr(finality_report, "profile_id"),
        service_name=getattr(finality_report, "service_name"),
        scope_digest=getattr(finality_report, "scope_digest"),
        request_digest=getattr(finality_report, "request_digest"),
        payload_digest=getattr(finality_report, "payload_digest"),
        idempotency_key=getattr(finality_report, "idempotency_key"),
        finality_digest=_digest(finality_report),
        accepted_marker_digest=getattr(finality_report, "accepted_marker_digest"),
        prune_guard_digest=_digest(prune_guard_report),
        plan_digest=getattr(prune_guard_report, "plan_digest"),
        hard_negative_count=int(getattr(finality_report, "hard_negative_count", 0) or 0) + int(getattr(prune_guard_report, "hard_negative_count", 0) or 0),
        sequence=sequence,
        previous_receipt_digest=previous_receipt_digest,
        issued_at=issued_at,
        expires_at=expires_at,
        family_id=family_id,
        path_family=path_family,
        signer_public_key=keypair.public_key_bytes,
    )
    return replace(receipt, signature=keypair.sign(receipt.signature_payload()))


def assess_terminal_receipts(
    receipts: Iterable[TerminalReceipt],
    *,
    finality_report: Any,
    prune_guard_report: Any,
    now: int,
    previous_seen_receipt_digests: Iterable[bytes] = (),
    min_family_count: int = 2,
    min_path_family_count: int = 2,
) -> TerminalReceiptReport:
    action = SideEffectAction(getattr(finality_report, "action"))
    final_phase_raw = getattr(finality_report, "final_phase", None)
    final_phase = SideEffectPhase(final_phase_raw) if final_phase_raw is not None else None
    profile_id = getattr(finality_report, "profile_id")
    service_name = getattr(finality_report, "service_name")
    scope_digest = getattr(finality_report, "scope_digest")
    request_digest = getattr(finality_report, "request_digest")
    payload_digest = getattr(finality_report, "payload_digest")
    idempotency_key = getattr(finality_report, "idempotency_key")
    component_digests = (_digest(finality_report), _digest(prune_guard_report))
    common = dict(action=action, final_phase=final_phase, profile_id=profile_id, service_name=service_name, scope_digest=scope_digest, request_digest=request_digest, payload_digest=payload_digest, idempotency_key=idempotency_key, component_digests=component_digests)
    if not _accept(finality_report) or _quarantined(finality_report) or not _accept(prune_guard_report) or _quarantined(prune_guard_report):
        return _report(TerminalReceiptDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "component did not accept", **common)
    if not bool(getattr(finality_report, "terminal", False)) or _watch(finality_report):
        return _report(TerminalReceiptDecisionKind.QUARANTINE_NONTERMINAL_FINALITY, False, False, False, "finality report is not terminal", **common)
    if getattr(prune_guard_report, "decision_kind", None) != PruneGuardDecisionKind.ACCEPT_TERMINAL_SOFT_PRUNE:
        return _report(TerminalReceiptDecisionKind.QUARANTINE_COMPONENT_NOT_ACCEPTED, False, False, False, "prune guard is not terminal soft prune", **common)
    hard = int(getattr(finality_report, "hard_negative_count", 0) or 0) + int(getattr(prune_guard_report, "hard_negative_count", 0) or 0)
    if hard:
        return _report(TerminalReceiptDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "hard negatives block terminal receipt", hard_negative_count=hard, **common)
    ordered = sorted(tuple(receipts), key=lambda receipt: (receipt.sequence, receipt.receipt_digest))
    if not ordered:
        return _report(TerminalReceiptDecisionKind.EMPTY_NO_RECEIPTS, False, True, False, "no terminal receipts", **common)
    seen = set(previous_seen_receipt_digests)
    seq_to_core: dict[int, bytes] = {}
    prev = ZERO_DIGEST
    families: set[str] = set()
    paths: set[str] = set()
    highest: TerminalReceipt | None = None
    expected_kind = kind_for_finality(finality_report)
    for receipt in ordered:
        if not receipt.live(now):
            return _report(TerminalReceiptDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, False, False, "expired or future receipt", **common)
        if not receipt.verifies():
            return _report(TerminalReceiptDecisionKind.QUARANTINE_BAD_SIGNATURE, False, False, False, "bad receipt signature", **common)
        if receipt.receipt_digest in seen:
            return _report(TerminalReceiptDecisionKind.QUARANTINE_REPLAY, False, False, False, "replayed terminal receipt", **common)
        if receipt.sequence in seq_to_core and seq_to_core[receipt.sequence] != receipt.receipt_core_digest:
            return _report(TerminalReceiptDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, "same-sequence receipt fork", **common)
        seq_to_core[receipt.sequence] = receipt.receipt_core_digest
        if receipt.sequence == 0:
            if receipt.previous_receipt_digest != ZERO_DIGEST:
                return _report(TerminalReceiptDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "first receipt has previous link", **common)
        elif receipt.previous_receipt_digest != prev:
            return _report(TerminalReceiptDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, "receipt previous link mismatch", **common)
        prev = receipt.receipt_digest
        highest = receipt
        families.add(receipt.family_id)
        paths.add(receipt.path_family)
    assert highest is not None
    for attr, expected in (("action", action), ("final_phase", final_phase), ("profile_id", profile_id), ("service_name", service_name), ("scope_digest", scope_digest), ("request_digest", request_digest), ("payload_digest", payload_digest), ("idempotency_key", idempotency_key)):
        if getattr(highest, attr) != expected:
            return _report(TerminalReceiptDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, f"{attr} drift", **common)
    if highest.receipt_kind is not expected_kind:
        return _report(TerminalReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "receipt kind drift", **common)
    if highest.finality_digest != component_digests[0] or highest.prune_guard_digest != component_digests[1] or highest.accepted_marker_digest != getattr(finality_report, "accepted_marker_digest") or highest.plan_digest != getattr(prune_guard_report, "plan_digest"):
        return _report(TerminalReceiptDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, "component digest drift", **common)
    if highest.hard_negative_count:
        return _report(TerminalReceiptDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, "receipt carries hard negatives", hard_negative_count=highest.hard_negative_count, **common)
    if len(families) < min_family_count:
        return _report(TerminalReceiptDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, "low receipt family diversity", receipt_kind=highest.receipt_kind, accepted_receipt_digest=highest.receipt_digest, receipt_digests=tuple(r.receipt_digest for r in ordered), highest_sequence=highest.sequence, family_count=len(families), path_family_count=len(paths), **common)
    if len(paths) < min_path_family_count:
        return _report(TerminalReceiptDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, "low receipt path diversity", receipt_kind=highest.receipt_kind, accepted_receipt_digest=highest.receipt_digest, receipt_digests=tuple(r.receipt_digest for r in ordered), highest_sequence=highest.sequence, family_count=len(families), path_family_count=len(paths), **common)
    if highest.receipt_kind is TerminalReceiptKind.TERMINAL_COMMIT:
        return _report(TerminalReceiptDecisionKind.ACCEPT_TERMINAL_COMMIT_RECEIPT, True, False, True, "terminal commit receipt accepted", receipt_kind=highest.receipt_kind, accepted_receipt_digest=highest.receipt_digest, receipt_digests=tuple(r.receipt_digest for r in ordered), highest_sequence=highest.sequence, family_count=len(families), path_family_count=len(paths), **common)
    return _report(TerminalReceiptDecisionKind.ACCEPT_TERMINAL_ABORT_RECEIPT, True, False, True, "terminal abort receipt accepted", receipt_kind=highest.receipt_kind, accepted_receipt_digest=highest.receipt_digest, receipt_digests=tuple(r.receipt_digest for r in ordered), highest_sequence=highest.sequence, family_count=len(families), path_family_count=len(paths), **common)


def _report(kind: TerminalReceiptDecisionKind, accept: bool, watch: bool, terminal: bool, reason: str, *, action: SideEffectAction, final_phase: SideEffectPhase | None, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, idempotency_key: bytes, component_digests: tuple[bytes, ...], receipt_kind: TerminalReceiptKind | None = None, accepted_receipt_digest: bytes = ZERO_DIGEST, receipt_digests: tuple[bytes, ...] = (), highest_sequence: int = -1, family_count: int = 0, path_family_count: int = 0, hard_negative_count: int = 0) -> TerminalReceiptReport:
    digest = sha256(TERMINAL_RECEIPT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"terminal": 1 if terminal else 0,
        b"reason": reason,
        b"receipt_kind": b"" if receipt_kind is None else receipt_kind.value,
        b"action": action.value,
        b"phase": b"" if final_phase is None else final_phase.value,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"idem": idempotency_key,
        b"accepted": accepted_receipt_digest,
        b"receipts": receipt_digests,
        b"components": component_digests,
        b"seq": highest_sequence,
        b"families": family_count,
        b"paths": path_family_count,
        b"hard": hard_negative_count,
    }))
    return TerminalReceiptReport(kind, accept, watch, terminal, reason, receipt_kind, action, final_phase, profile_id, service_name, scope_digest, request_digest, payload_digest, idempotency_key, accepted_receipt_digest, receipt_digests, component_digests, highest_sequence, family_count, path_family_count, hard_negative_count, digest)
