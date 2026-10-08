"""Audit-gap repair planning for public bridge publication shadows.

The public bridge lane now has many local observations: shadow plans, audit
quorum receipts, redress/moderation retention, and a no-network outbox.  A gap
between these observations must not silently become either publication or
forgetting.  rev0049 models a small, local repair plan surface that asks for
withdraw/repair/watch actions without treating audits as global truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .auditquorum import AuditQuorumReport
from .bencode import bencode
from .bridgeshadow import BridgeShadowReport
from .ids import DOMAIN, sha256
from .publicoutbox import PublicOutboxReport
from .redressgc import RedressGcReport

AUDIT_GAP_DOMAIN = DOMAIN + b":audit-gap-v1:"


class AuditGapSignalKind(str, Enum):
    STALE_PUBLIC_RECORD = "stale_public_record"
    PAYLOAD_MISMATCH = "payload_mismatch"
    REDRESS_GAP = "redress_gap"
    SHADOW_ACCEPTED = "shadow_accepted"
    OUTBOX_STAGED = "outbox_staged"
    PUBLICATION_OBSERVED = "publication_observed"


class AuditGapDecisionKind(str, Enum):
    ACCEPT_NO_GAP = "accept_no_gap"
    ACCEPT_REPAIR_PLAN = "accept_repair_plan"
    ACCEPT_WITHDRAW_PLAN = "accept_withdraw_plan"
    HOLD_WATCH_DEBT = "hold_watch_debt"
    HOLD_OUTBOX_NOT_STAGED = "hold_outbox_not_staged"
    HOLD_LOW_SIGNAL_DIVERSITY = "hold_low_signal_diversity"
    QUARANTINE_SHADOW = "quarantine_shadow"
    QUARANTINE_AUDIT = "quarantine_audit"
    QUARANTINE_REDRESS = "quarantine_redress"
    QUARANTINE_OUTBOX = "quarantine_outbox"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PAYLOAD_DRIFT = "quarantine_payload_drift"
    QUARANTINE_SIGNAL_CONFLICT = "quarantine_signal_conflict"
    QUARANTINE_REPAIR_WITH_HARD_NEGATIVE = "quarantine_repair_with_hard_negative"


@dataclass(frozen=True)
class AuditGapSignal:
    kind: AuditGapSignalKind
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    evidence_digest: bytes
    family_id: str
    path_family: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", AuditGapSignalKind(self.kind))
        if not self.family_id or not self.path_family:
            raise ValueError("audit gap signal needs family/path")
        for name, value in (
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("payload_digest", self.payload_digest),
            ("evidence_digest", self.evidence_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @property
    def signal_digest(self) -> bytes:
        return sha256(AUDIT_GAP_DOMAIN + b":signal:" + bencode({
            b"kind": self.kind.value,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"evidence": self.evidence_digest,
            b"family": self.family_id,
            b"path": self.path_family,
        }))


@dataclass(frozen=True)
class AuditGapReport:
    decision_kind: AuditGapDecisionKind
    accept: bool
    watch: bool
    reason: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    repair: bool
    withdraw: bool
    signal_count: int
    family_count: int
    path_family_count: int
    hard_negative_count: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: AuditGapDecisionKind, accept: bool, watch: bool, reason: str, *, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, signals: Iterable[AuditGapSignal] = (), repair: bool = False, withdraw: bool = False, hard_negative_count: int = 0) -> AuditGapReport:
    signal_tuple = tuple(sorted(signals, key=lambda item: item.signal_digest))
    families = len({item.family_id for item in signal_tuple})
    paths = len({item.path_family for item in signal_tuple})
    digest = sha256(AUDIT_GAP_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"scope": scope_digest,
        b"request": request_digest,
        b"payload": payload_digest,
        b"repair": 1 if repair else 0,
        b"withdraw": 1 if withdraw else 0,
        b"signals": [item.signal_digest for item in signal_tuple],
        b"families": families,
        b"paths": paths,
        b"hard": hard_negative_count,
    }))
    return AuditGapReport(kind, accept, watch, reason, scope_digest, request_digest, payload_digest, repair, withdraw, len(signal_tuple), families, paths, hard_negative_count, digest)


def assess_audit_gap(
    signals: Iterable[AuditGapSignal],
    *,
    bridge_shadow: BridgeShadowReport,
    audit_quorum: AuditQuorumReport,
    redress_gc: RedressGcReport,
    outbox: PublicOutboxReport | None,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    expected_payload_digest: bytes,
    min_signal_family_diversity: int = 2,
    require_outbox_for_repair: bool = True,
) -> AuditGapReport:
    signal_tuple = tuple(sorted(signals, key=lambda item: item.signal_digest))
    if bridge_shadow.quarantined or not bridge_shadow.accept:
        return _report(AuditGapDecisionKind.QUARANTINE_SHADOW, False, True, "bridge shadow not locally usable", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple)
    if audit_quorum.quarantined or not audit_quorum.accept:
        return _report(AuditGapDecisionKind.QUARANTINE_AUDIT, False, True, "audit quorum not locally usable", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple)
    if redress_gc.quarantined or not redress_gc.accept:
        return _report(AuditGapDecisionKind.QUARANTINE_REDRESS, False, True, "redress GC not locally usable", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
    if outbox is not None and outbox.quarantined:
        return _report(AuditGapDecisionKind.QUARANTINE_OUTBOX, False, True, "outbox report quarantined", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)

    kinds = {signal.kind for signal in signal_tuple}
    core_by_kind_family: dict[tuple[AuditGapSignalKind, str], bytes] = {}
    for signal in signal_tuple:
        if signal.scope_digest != expected_scope_digest:
            return _report(AuditGapDecisionKind.QUARANTINE_SCOPE_DRIFT, False, True, "audit gap signal scope drift", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
        if signal.request_digest != expected_request_digest:
            return _report(AuditGapDecisionKind.QUARANTINE_REQUEST_DRIFT, False, True, "audit gap signal request drift", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
        if signal.payload_digest != expected_payload_digest:
            return _report(AuditGapDecisionKind.QUARANTINE_PAYLOAD_DRIFT, False, True, "audit gap signal payload drift", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
        prev = core_by_kind_family.setdefault((signal.kind, signal.family_id), signal.evidence_digest)
        if prev != signal.evidence_digest and signal.kind in {AuditGapSignalKind.PAYLOAD_MISMATCH, AuditGapSignalKind.STALE_PUBLIC_RECORD, AuditGapSignalKind.REDRESS_GAP}:
            return _report(AuditGapDecisionKind.QUARANTINE_SIGNAL_CONFLICT, False, True, "contradictory negative audit-gap signal", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)

    negative = kinds & {AuditGapSignalKind.STALE_PUBLIC_RECORD, AuditGapSignalKind.PAYLOAD_MISMATCH, AuditGapSignalKind.REDRESS_GAP}
    if not negative:
        return _report(AuditGapDecisionKind.ACCEPT_NO_GAP, True, audit_quorum.watch or bridge_shadow.watch or redress_gc.watch, "no audit gap observed", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
    if len({signal.family_id for signal in signal_tuple if signal.kind in negative}) < min_signal_family_diversity:
        return _report(AuditGapDecisionKind.HOLD_LOW_SIGNAL_DIVERSITY, False, True, "negative audit gap lacks family diversity", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
    if redress_gc.hard_negative_count and AuditGapSignalKind.PAYLOAD_MISMATCH in negative:
        return _report(AuditGapDecisionKind.QUARANTINE_REPAIR_WITH_HARD_NEGATIVE, False, True, "payload repair blocked by live hard-negative pressure", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
    if require_outbox_for_repair and (outbox is None or not outbox.accept):
        return _report(AuditGapDecisionKind.HOLD_OUTBOX_NOT_STAGED, False, True, "audit-gap repair needs a staged outbox entry", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)
    if AuditGapSignalKind.STALE_PUBLIC_RECORD in negative:
        return _report(AuditGapDecisionKind.ACCEPT_WITHDRAW_PLAN, True, True, "stale public record should withdraw/refresh under watch", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, withdraw=True, hard_negative_count=redress_gc.hard_negative_count)
    if AuditGapSignalKind.PAYLOAD_MISMATCH in negative or AuditGapSignalKind.REDRESS_GAP in negative:
        return _report(AuditGapDecisionKind.ACCEPT_REPAIR_PLAN, True, True, "audit gap repair accepted under watch", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, repair=True, hard_negative_count=redress_gc.hard_negative_count)
    return _report(AuditGapDecisionKind.HOLD_WATCH_DEBT, False, True, "unclassified audit gap watch debt", scope_digest=expected_scope_digest, request_digest=expected_request_digest, payload_digest=expected_payload_digest, signals=signal_tuple, hard_negative_count=redress_gc.hard_negative_count)


def gap_signal(kind: AuditGapSignalKind, *, scope_digest: bytes, request_digest: bytes, payload_digest: bytes, evidence_digest: bytes | None = None, family_id: str, path_family: str) -> AuditGapSignal:
    return AuditGapSignal(kind, scope_digest, request_digest, payload_digest, evidence_digest or sha256(AUDIT_GAP_DOMAIN + b":auto-evidence:" + kind.value.encode()), family_id, path_family)
