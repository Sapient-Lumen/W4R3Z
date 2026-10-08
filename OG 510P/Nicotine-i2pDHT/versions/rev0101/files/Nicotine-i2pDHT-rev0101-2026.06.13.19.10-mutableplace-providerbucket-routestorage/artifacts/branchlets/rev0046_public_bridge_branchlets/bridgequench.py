"""Public bridge publication quench and cooldown pressure.

Publication creates memory. Withdrawal does not instantly erase it, and repeated
refresh/withdraw loops can launder a bridge into public visibility even when
individual capsules looked valid. This module gives the local node a small
ledger-level pressure check over accepted bridge-publication reports.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .bridgepublish import BridgePublicationReport, BridgePublishAction, ExposureClass
from .ids import DOMAIN, sha256

BRIDGE_QUENCH_DOMAIN = DOMAIN + b":bridge-quench-v1:"


class QuenchDecisionKind(str, Enum):
    ACCEPT_PUBLICATION_WINDOW = "accept_publication_window"
    ACCEPT_WITH_COOLDOWN = "accept_with_cooldown"
    HOLD_WITHDRAWAL_CONFIRMATION = "hold_withdrawal_confirmation"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_COMPONENT_REJECTED = "quarantine_component_rejected"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_PROFILE_DRIFT = "quarantine_profile_drift"
    QUARANTINE_SERVICE_DRIFT = "quarantine_service_drift"
    QUARANTINE_REFRESH_STORM = "quarantine_refresh_storm"
    QUARANTINE_WITHDRAW_REFRESH_OSCILLATION = "quarantine_withdraw_refresh_oscillation"
    QUARANTINE_STALE_PUBLIC_UNQUENCHED = "quarantine_stale_public_unquenched"
    QUARANTINE_HARD_NEGATIVE_UNQUENCHED = "quarantine_hard_negative_unquenched"
    QUARANTINE_EXPOSURE_CLASS_DRIFT = "quarantine_exposure_class_drift"


@dataclass(frozen=True)
class BridgeQuenchReport:
    decision_kind: QuenchDecisionKind
    accepted: bool
    reason: str
    profile_id: str
    service_name: str
    scope_digest: bytes
    request_digest: bytes
    report_digests: tuple[bytes, ...]
    refresh_count: int
    withdraw_count: int
    repair_count: int
    family_count: int
    path_count: int
    cooldown: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: QuenchDecisionKind, accepted: bool, reason: str, *, profile_id: str, service_name: str, scope_digest: bytes, request_digest: bytes, reports: tuple[BridgePublicationReport, ...], cooldown: bool = False) -> BridgeQuenchReport:
    report_digests = tuple(sorted(report.report_digest for report in reports))
    families = {report.family_id for report in reports}
    paths = {report.path_family for report in reports}
    refresh_count = sum(1 for report in reports if report.action is BridgePublishAction.PUBLIC_REFRESH)
    withdraw_count = sum(1 for report in reports if report.action is BridgePublishAction.PUBLIC_WITHDRAW)
    repair_count = sum(1 for report in reports if report.action is BridgePublishAction.PUBLIC_REPAIR)
    digest = sha256(BRIDGE_QUENCH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"scope": scope_digest,
        b"request": request_digest,
        b"reports": report_digests,
        b"refresh": refresh_count,
        b"withdraw": withdraw_count,
        b"repair": repair_count,
        b"families": len(families),
        b"paths": len(paths),
        b"cooldown": 1 if cooldown else 0,
    }))
    return BridgeQuenchReport(kind, accepted, reason, profile_id, service_name, scope_digest, request_digest, report_digests, refresh_count, withdraw_count, repair_count, len(families), len(paths), cooldown, digest)


def assess_bridge_quench(
    reports: Iterable[BridgePublicationReport],
    *,
    expected_profile_id: str,
    expected_service_name: str,
    expected_scope_digest: bytes,
    expected_request_digest: bytes,
    min_family_diversity: int = 2,
    min_path_diversity: int = 2,
    max_refreshes_without_withdraw: int = 2,
    max_oscillation_pairs: int = 1,
    stale_public_announcement_digests: Iterable[bytes] = (),
    hard_negative_digests: Iterable[bytes] = (),
) -> BridgeQuenchReport:
    if len(expected_scope_digest) != 32 or len(expected_request_digest) != 32:
        raise ValueError("expected digests must be 32 bytes")
    report_tuple = tuple(reports)
    if not report_tuple:
        return _report(QuenchDecisionKind.HOLD_WITHDRAWAL_CONFIRMATION, False, "no publication reports to evaluate", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=())
    for report in report_tuple:
        if report.profile_id != expected_profile_id:
            return _report(QuenchDecisionKind.QUARANTINE_PROFILE_DRIFT, False, "profile drift inside publication window", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
        if report.service_name != expected_service_name:
            return _report(QuenchDecisionKind.QUARANTINE_SERVICE_DRIFT, False, "service drift inside publication window", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
        if report.scope_digest != expected_scope_digest:
            return _report(QuenchDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "scope drift inside publication window", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
        if report.request_digest != expected_request_digest:
            return _report(QuenchDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "request drift inside publication window", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
        if not report.accepted or report.quarantined:
            return _report(QuenchDecisionKind.QUARANTINE_COMPONENT_REJECTED, False, "component publication report rejected", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
        if report.action is BridgePublishAction.PUBLIC_WITHDRAW and report.exposure_class is not ExposureClass.WITHDRAWAL_ONLY:
            return _report(QuenchDecisionKind.QUARANTINE_EXPOSURE_CLASS_DRIFT, False, "withdraw report carries live exposure class", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
    families = {report.family_id for report in report_tuple}
    paths = {report.path_family for report in report_tuple}
    if len(families) < min_family_diversity:
        return _report(QuenchDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "publication window lacks family diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
    if len(paths) < min_path_diversity:
        return _report(QuenchDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, "publication window lacks path diversity", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
    refresh_count = sum(1 for report in report_tuple if report.action is BridgePublishAction.PUBLIC_REFRESH)
    withdraw_count = sum(1 for report in report_tuple if report.action is BridgePublishAction.PUBLIC_WITHDRAW)
    repair_count = sum(1 for report in report_tuple if report.action is BridgePublishAction.PUBLIC_REPAIR)
    if hard_negative_digests and withdraw_count == 0:
        return _report(QuenchDecisionKind.QUARANTINE_HARD_NEGATIVE_UNQUENCHED, False, "hard-negative pressure requires withdrawal evidence", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
    if stale_public_announcement_digests and withdraw_count == 0 and repair_count == 0:
        return _report(QuenchDecisionKind.QUARANTINE_STALE_PUBLIC_UNQUENCHED, False, "stale public announcement lacks repair or withdrawal", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
    if refresh_count > max_refreshes_without_withdraw and withdraw_count == 0:
        return _report(QuenchDecisionKind.QUARANTINE_REFRESH_STORM, False, "too many refreshes without quench evidence", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
    ordered = tuple(sorted(report_tuple, key=lambda item: item.sequence))
    oscillations = 0
    last_action: BridgePublishAction | None = None
    for report in ordered:
        if last_action is not None and report.action is not last_action and {last_action, report.action} == {BridgePublishAction.PUBLIC_REFRESH, BridgePublishAction.PUBLIC_WITHDRAW}:
            oscillations += 1
        last_action = report.action
    if oscillations > max_oscillation_pairs:
        return _report(QuenchDecisionKind.QUARANTINE_WITHDRAW_REFRESH_OSCILLATION, False, "refresh/withdraw oscillation exceeds local budget", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple)
    cooldown = bool(withdraw_count or repair_count or stale_public_announcement_digests)
    return _report(QuenchDecisionKind.ACCEPT_WITH_COOLDOWN if cooldown else QuenchDecisionKind.ACCEPT_PUBLICATION_WINDOW, True, "publication window accepted locally", profile_id=expected_profile_id, service_name=expected_service_name, scope_digest=expected_scope_digest, request_digest=expected_request_digest, reports=report_tuple, cooldown=cooldown)
