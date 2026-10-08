"""Scope-bound SAM-shadow trace joins before live I2P transport.

``samwire.py`` can prove a no-network SAM script is ordered and destination-
stable. ``transportshadow.py`` can prove report frames are parse-safe and kind-
bound. ``scopefence.py`` and ``egressmeter.py`` can accept their own local
surfaces.  rev0032 joins those facts so a future handler cannot spend SAM egress
for a different scope/object/request than the validated intent.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .egressmeter import EgressWindowReport
from .ids import DOMAIN, sha256
from .samwire import SamWireDecisionKind, SamWireScriptReport
from .scopefence import ScopeFenceReport
from .transportshadow import ShadowValidationKind, ShadowValidationReport

SAM_TRACE_DOMAIN = DOMAIN + b":sam-trace-join-v1:"


class SamTraceDecisionKind(str, Enum):
    ACCEPT_SCOPE_BOUND_TRACE = "accept_scope_bound_trace"
    ACCEPT_WITH_RECONNECT_WATCH = "accept_with_reconnect_watch"
    HOLD_EGRESS_WATCH = "hold_egress_watch"
    QUARANTINE_SCOPE_FENCE = "quarantine_scope_fence"
    QUARANTINE_SAM_SCRIPT = "quarantine_sam_script"
    QUARANTINE_SHADOW_REPORT = "quarantine_shadow_report"
    QUARANTINE_EGRESS = "quarantine_egress"
    QUARANTINE_REQUEST_MISMATCH = "quarantine_request_mismatch"
    QUARANTINE_OBJECT_MISMATCH = "quarantine_object_mismatch"
    QUARANTINE_SEND_COUNT_MISMATCH = "quarantine_send_count_mismatch"
    EMPTY_NO_SHADOW_REPORTS = "empty_no_shadow_reports"


@dataclass(frozen=True)
class SamTracePolicy:
    require_one_send_per_shadow: bool = True
    allow_reconnect_watch: bool = True
    allow_egress_accept_with_watch: bool = False


@dataclass(frozen=True)
class SamTraceReport:
    decision_kind: SamTraceDecisionKind
    accept: bool
    reason: str
    scope_report_digest: bytes
    sam_report_digest: bytes
    egress_report_digest: bytes
    shadow_report_digests: tuple[bytes, ...]
    send_count: int
    reconnect_count: int
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: SamTraceDecisionKind,
    accept: bool,
    reason: str,
    *,
    scope_report: ScopeFenceReport,
    sam_report: SamWireScriptReport,
    egress_report: EgressWindowReport,
    shadow_reports: tuple[ShadowValidationReport, ...],
    pressures: Iterable[bytes] = (),
) -> SamTraceReport:
    shadow_digests = tuple(sorted({item.report_digest for item in shadow_reports}))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(SAM_TRACE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"scope": scope_report.report_digest,
        b"sam": sam_report.transcript_digest,
        b"egress": egress_report.report_digest,
        b"shadow": list(shadow_digests),
        b"send_count": sam_report.send_count,
        b"reconnect_count": sam_report.reconnect_count,
        b"pressures": list(pressure_t),
        b"reason": reason,
    }))
    return SamTraceReport(kind, accept, reason, scope_report.report_digest, sam_report.transcript_digest, egress_report.report_digest, shadow_digests, sam_report.send_count, sam_report.reconnect_count, pressure_t, digest)


def assess_sam_trace(
    *,
    scope_report: ScopeFenceReport,
    sam_report: SamWireScriptReport,
    egress_report: EgressWindowReport,
    shadow_reports: Iterable[ShadowValidationReport],
    expected_request_id: bytes,
    expected_object_digest: bytes,
    policy: SamTracePolicy | None = None,
) -> SamTraceReport:
    policy = policy or SamTracePolicy()
    shadows = tuple(shadow_reports)
    if not shadows:
        return _report(SamTraceDecisionKind.EMPTY_NO_SHADOW_REPORTS, False, "no shadow report frames supplied", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows)
    if not scope_report.accept:
        return _report(SamTraceDecisionKind.QUARANTINE_SCOPE_FENCE, False, "scope fence did not accept before SAM trace", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=scope_report.quarantine_digests)
    if not sam_report.accept or sam_report.quarantined:
        return _report(SamTraceDecisionKind.QUARANTINE_SAM_SCRIPT, False, "SAM-shadow script did not accept", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=(sam_report.transcript_digest,))
    if not egress_report.accept:
        return _report(SamTraceDecisionKind.QUARANTINE_EGRESS, False, "egress budget did not accept before SAM trace", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=(egress_report.report_digest,))
    bad_shadow = [item for item in shadows if item.validation.kind is not ShadowValidationKind.ACCEPT_SHADOW or not item.validation.accept or item.payload is None]
    if bad_shadow:
        return _report(SamTraceDecisionKind.QUARANTINE_SHADOW_REPORT, False, "one or more shadow report frames failed parse/kind/digest validation", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=(item.report_digest for item in bad_shadow))
    request_mismatch = [item for item in shadows if item.frame.request_id != expected_request_id]
    if request_mismatch:
        return _report(SamTraceDecisionKind.QUARANTINE_REQUEST_MISMATCH, False, "shadow frame request id does not match scope-fenced intent", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=(item.report_digest for item in request_mismatch))
    object_mismatch = [item for item in shadows if item.payload is not None and item.payload.subject_digest != expected_object_digest]
    if object_mismatch:
        return _report(SamTraceDecisionKind.QUARANTINE_OBJECT_MISMATCH, False, "shadow payload subject digest does not match scope-fenced object", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=(item.report_digest for item in object_mismatch))
    if policy.require_one_send_per_shadow and sam_report.send_count < len(shadows):
        return _report(SamTraceDecisionKind.QUARANTINE_SEND_COUNT_MISMATCH, False, "SAM-shadow script carried fewer sends than validated report frames", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=(sam_report.transcript_digest,))
    if egress_report.decision_kind.value == "accept_with_watch" and not policy.allow_egress_accept_with_watch:
        return _report(SamTraceDecisionKind.HOLD_EGRESS_WATCH, False, "egress accepted only with watch and policy refuses side effects", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows, pressures=(egress_report.report_digest,))
    if sam_report.decision_kind is SamWireDecisionKind.WATCH_RECONNECT_SAME_DESTINATION:
        return _report(SamTraceDecisionKind.ACCEPT_WITH_RECONNECT_WATCH if policy.allow_reconnect_watch else SamTraceDecisionKind.QUARANTINE_SAM_SCRIPT, policy.allow_reconnect_watch, "SAM trace preserved destination across reconnect but remains watch-listed", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows)
    return _report(SamTraceDecisionKind.ACCEPT_SCOPE_BOUND_TRACE, True, "SAM trace is scope-bound, egress-budgeted, shadow-validated, and request/object exact", scope_report=scope_report, sam_report=sam_report, egress_report=egress_report, shadow_reports=shadows)
