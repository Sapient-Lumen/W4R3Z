"""rev0069 audit export boundary after retention proof.

Export is deliberately not live publication.  It is a redacted local bundle that
may later be shown to an operator, garden, or test harness.  The risk is that an
export of a closed public-edge event becomes a metadata leak or a new authority
surface.  This lane keeps export exact-boundary, redacted, sequenced, and bound
to closure-seal plus retention-proof reports.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST
from .sideeffectjournal import SideEffectAction

AUDIT_EXPORT_DOMAIN = DOMAIN + b":audit-export-v1:"


class AuditExportAudience(str, Enum):
    LOCAL_OPERATOR = "local_operator"
    GARDEN_WITNESS = "garden_witness"
    PUBLIC_REDACTED = "public_redacted"


class AuditExportDecisionKind(str, Enum):
    ACCEPT_EXPORT_PREPARED = "accept_export_prepared"
    HOLD_RETENTION_PENDING = "hold_retention_pending"
    HOLD_CLOSURE_SEAL_PENDING = "hold_closure_seal_pending"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_BOUNDARY_DRIFT = "quarantine_boundary_drift"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_RAW_BOUNDARY_EXPOSURE = "quarantine_raw_boundary_exposure"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_MISMATCH = "quarantine_previous_mismatch"
    QUARANTINE_CONTRADICTION_DROPPED = "quarantine_contradiction_dropped"
    QUARANTINE_HARD_NEGATIVE_PRESSURE = "quarantine_hard_negative_pressure"


@dataclass(frozen=True)
class AuditExportBundle:
    audience: AuditExportAudience
    sequence: int
    previous_digest: bytes
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    closure_seal_digest: bytes
    retention_proof_digest: bytes
    redacted_summary_digest: bytes
    contradiction_carried: bool
    raw_boundary_exposed: bool
    raw_payload_exposed: bool
    family_id: str
    path_family_id: str
    hard_negative_count: int = 0

    @property
    def bundle_digest(self) -> bytes:
        return sha256(AUDIT_EXPORT_DOMAIN + b":bundle:" + bencode({
            b"audience": self.audience.value,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"action": SideEffectAction(self.action).value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"payload": self.payload_digest,
            b"idem": self.idempotency_key,
            b"retry_idem": self.retry_idempotency_key,
            b"seal": self.closure_seal_digest,
            b"retention": self.retention_proof_digest,
            b"summary": self.redacted_summary_digest,
            b"contradiction": 1 if self.contradiction_carried else 0,
            b"raw_boundary": 1 if self.raw_boundary_exposed else 0,
            b"raw_payload": 1 if self.raw_payload_exposed else 0,
            b"family": self.family_id,
            b"path": self.path_family_id,
            b"hard": self.hard_negative_count,
        }))


@dataclass(frozen=True)
class AuditExportReport:
    decision_kind: AuditExportDecisionKind
    accept: bool
    watch: bool
    export_prepared: bool
    contradiction_carried: bool
    redacted: bool
    reason: str
    audience: AuditExportAudience
    action: SideEffectAction
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    payload_digest: bytes
    idempotency_key: bytes
    retry_idempotency_key: bytes
    closure_seal_digest: bytes
    retention_proof_digest: bytes
    accepted_bundle_digest: bytes
    bundle_digests: tuple[bytes, ...]
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
    for attr in ("report_digest", "accepted_item_digest", "accepted_entry_digest", "accepted_marker_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("component lacks digest")


def _boundary(report: Any) -> tuple[Any, ...]:
    return (SideEffectAction(getattr(report, "action")), getattr(report, "profile_id"), getattr(report, "service_name"), getattr(report, "scope_digest"), getattr(report, "request_digest"), getattr(report, "payload_digest"), getattr(report, "idempotency_key"))


def _bundle_boundary(bundle: AuditExportBundle) -> tuple[Any, ...]:
    return (SideEffectAction(bundle.action), bundle.profile_id, bundle.service_name, bundle.scope_digest, bundle.request_digest, bundle.payload_digest, bundle.idempotency_key)


def make_audit_export_bundle(*, audience: AuditExportAudience, sequence: int, closure_seal_report: Any, retention_proof_report: Any, previous_digest: bytes = ZERO_DIGEST, redacted_summary_digest: bytes | None = None, contradiction_carried: bool | None = None, raw_boundary_exposed: bool = False, raw_payload_exposed: bool = False, family_id: str = "audit-export-family-a", path_family_id: str = "audit-export-path-a", hard_negative_count: int = 0) -> AuditExportBundle:
    contradiction = bool(getattr(retention_proof_report, "contradiction_preserved", False)) if contradiction_carried is None else bool(contradiction_carried)
    summary = redacted_summary_digest or sha256(AUDIT_EXPORT_DOMAIN + b":summary:" + _digest(retention_proof_report))
    return AuditExportBundle(
        audience=AuditExportAudience(audience),
        sequence=sequence,
        previous_digest=previous_digest,
        action=SideEffectAction(getattr(retention_proof_report, "action")),
        profile_id=getattr(retention_proof_report, "profile_id"),
        service_name=getattr(retention_proof_report, "service_name"),
        scope_digest=getattr(retention_proof_report, "scope_digest"),
        request_digest=getattr(retention_proof_report, "request_digest"),
        payload_digest=getattr(retention_proof_report, "payload_digest"),
        idempotency_key=getattr(retention_proof_report, "idempotency_key"),
        retry_idempotency_key=getattr(retention_proof_report, "retry_idempotency_key", ZERO_DIGEST),
        closure_seal_digest=_digest(closure_seal_report),
        retention_proof_digest=_digest(retention_proof_report),
        redacted_summary_digest=summary,
        contradiction_carried=contradiction,
        raw_boundary_exposed=raw_boundary_exposed,
        raw_payload_exposed=raw_payload_exposed,
        family_id=family_id,
        path_family_id=path_family_id,
        hard_negative_count=hard_negative_count,
    )


def _report(kind: AuditExportDecisionKind, accept: bool, watch: bool, prepared: bool, contradiction: bool, redacted: bool, reason: str, *, closure_seal_report: Any, retention_proof_report: Any, bundles: tuple[AuditExportBundle, ...], audience: AuditExportAudience = AuditExportAudience.LOCAL_OPERATOR, accepted_bundle_digest: bytes = ZERO_DIGEST) -> AuditExportReport:
    digests = tuple(bundle.bundle_digest for bundle in bundles)
    families = {bundle.family_id for bundle in bundles}
    paths = {bundle.path_family_id for bundle in bundles}
    hard = int(getattr(closure_seal_report, "hard_negative_count", 0) or 0) + int(getattr(retention_proof_report, "hard_negative_count", 0) or 0) + sum(bundle.hard_negative_count for bundle in bundles)
    report_digest = sha256(AUDIT_EXPORT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"prepared": 1 if prepared else 0,
        b"contradiction": 1 if contradiction else 0,
        b"redacted": 1 if redacted else 0,
        b"audience": AuditExportAudience(audience).value,
        b"action": SideEffectAction(getattr(retention_proof_report, "action")).value,
        b"profile": getattr(retention_proof_report, "profile_id"),
        b"service": getattr(retention_proof_report, "service_name"),
        b"scope": getattr(retention_proof_report, "scope_digest"),
        b"request": getattr(retention_proof_report, "request_digest"),
        b"payload": getattr(retention_proof_report, "payload_digest"),
        b"idem": getattr(retention_proof_report, "idempotency_key"),
        b"retry_idem": getattr(retention_proof_report, "retry_idempotency_key", ZERO_DIGEST),
        b"seal": _digest(closure_seal_report),
        b"retention": _digest(retention_proof_report),
        b"accepted": accepted_bundle_digest,
        b"bundles": list(digests),
        b"families": len(families),
        b"paths": len(paths),
        b"hard": hard,
        b"reason": reason,
    }))
    return AuditExportReport(kind, accept, watch, prepared, contradiction, redacted, reason, AuditExportAudience(audience), SideEffectAction(getattr(retention_proof_report, "action")), getattr(retention_proof_report, "profile_id"), getattr(retention_proof_report, "service_name"), getattr(retention_proof_report, "scope_digest"), getattr(retention_proof_report, "request_digest"), getattr(retention_proof_report, "payload_digest"), getattr(retention_proof_report, "idempotency_key"), getattr(retention_proof_report, "retry_idempotency_key", ZERO_DIGEST), _digest(closure_seal_report), _digest(retention_proof_report), accepted_bundle_digest, digests, len(families), len(paths), hard, report_digest)


def assess_audit_export(*, closure_seal_report: Any, retention_proof_report: Any, bundles: tuple[AuditExportBundle, ...] = (), previous_digest: bytes = ZERO_DIGEST, min_family_count: int = 2, min_path_family_count: int = 2) -> AuditExportReport:
    if not bool(getattr(closure_seal_report, "accept", False)) or not bool(getattr(closure_seal_report, "closure_sealed", False)):
        return _report(AuditExportDecisionKind.HOLD_CLOSURE_SEAL_PENDING, False, True, False, False, False, "closure seal pending", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles)
    if not bool(getattr(retention_proof_report, "accept", False)) or not bool(getattr(retention_proof_report, "retention_proved", False)):
        return _report(AuditExportDecisionKind.HOLD_RETENTION_PENDING, False, True, False, False, False, "retention proof pending", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles)
    if _boundary(closure_seal_report) != _boundary(retention_proof_report):
        return _report(AuditExportDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "component boundary drift", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles)
    if int(getattr(closure_seal_report, "hard_negative_count", 0) or 0) or int(getattr(retention_proof_report, "hard_negative_count", 0) or 0):
        return _report(AuditExportDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "component hard-negative pressure", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles)
    if not bundles:
        return _report(AuditExportDecisionKind.HOLD_RETENTION_PENDING, False, True, False, False, False, "no export bundles", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles)
    for bundle in bundles:
        if _bundle_boundary(bundle) != _boundary(retention_proof_report):
            return _report(AuditExportDecisionKind.QUARANTINE_BOUNDARY_DRIFT, False, False, False, False, False, "bundle boundary drift", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=bundle.audience)
        if bundle.closure_seal_digest != _digest(closure_seal_report) or bundle.retention_proof_digest != _digest(retention_proof_report):
            return _report(AuditExportDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, False, False, False, "bundle component digest drift", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=bundle.audience)
        if bundle.raw_boundary_exposed or bundle.raw_payload_exposed:
            return _report(AuditExportDecisionKind.QUARANTINE_RAW_BOUNDARY_EXPOSURE, False, False, False, False, False, "raw boundary or payload exposure", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=bundle.audience)
        if bundle.hard_negative_count:
            return _report(AuditExportDecisionKind.QUARANTINE_HARD_NEGATIVE_PRESSURE, False, False, False, False, False, "bundle hard-negative pressure", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=bundle.audience)
    sorted_bundles = sorted(bundles, key=lambda bundle: bundle.sequence)
    last_digest = previous_digest
    by_seq: dict[int, bytes] = {}
    for bundle in sorted_bundles:
        digest = bundle.bundle_digest
        if bundle.sequence in by_seq and by_seq[bundle.sequence] != digest:
            return _report(AuditExportDecisionKind.QUARANTINE_SEQUENCE_FORK, False, False, False, False, False, "same sequence different export", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=bundle.audience)
        by_seq[bundle.sequence] = digest
        if bundle.previous_digest != last_digest:
            return _report(AuditExportDecisionKind.QUARANTINE_PREVIOUS_MISMATCH, False, False, False, False, False, "previous digest mismatch", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=bundle.audience)
        last_digest = digest
    families = {bundle.family_id for bundle in bundles}
    paths = {bundle.path_family_id for bundle in bundles}
    if len(families) < min_family_count:
        return _report(AuditExportDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, False, any(b.contradiction_carried for b in bundles), True, "not enough export family diversity", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=sorted_bundles[-1].audience)
    if len(paths) < min_path_family_count:
        return _report(AuditExportDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, False, any(b.contradiction_carried for b in bundles), True, "not enough export path diversity", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=sorted_bundles[-1].audience)
    contradiction = any(bundle.contradiction_carried for bundle in bundles)
    if bool(getattr(retention_proof_report, "contradiction_preserved", False)) and not contradiction:
        return _report(AuditExportDecisionKind.QUARANTINE_CONTRADICTION_DROPPED, False, False, False, False, True, "contradiction memory missing from export", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=sorted_bundles[-1].audience)
    accepted = sorted_bundles[-1]
    return _report(AuditExportDecisionKind.ACCEPT_EXPORT_PREPARED, True, False, True, contradiction, True, "audit export prepared", closure_seal_report=closure_seal_report, retention_proof_report=retention_proof_report, bundles=bundles, audience=accepted.audience, accepted_bundle_digest=accepted.bundle_digest)
