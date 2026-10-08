"""Joined service-continuity boundary for folded garden-service branchlets.

rev0038 folds several service branchlets that were previously useful but
separate: catalog wire exposure, service probes, withdrawal/relay/use gates,
service handoff, veiled receipts, announcements, ingress, tickets, and receipts.
The hard guess is that each lane can pass locally while the combined side effect
is still unsafe.  This module keeps those reports as typed local signals and
only advances service continuity when catalog, scope, request, withdrawal, and
required-branch pressure all agree.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Protocol, runtime_checkable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

SERVICE_CONTINUITY_DOMAIN = DOMAIN + b":service-continuity-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceContinuityDecisionKind(str, Enum):
    ACCEPT_SERVICE_CONTINUITY = "accept_service_continuity"
    HOLD_MISSING_REQUIRED_BRANCH = "hold_missing_required_branch"
    HOLD_REFUSAL_ONLY_OR_WATCH_ONLY = "hold_refusal_only_or_watch_only"
    QUARANTINE_BRANCH_REPORT = "quarantine_branch_report"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_DUPLICATE_BRANCH = "quarantine_duplicate_branch"
    QUARANTINE_ACTIVE_WITHDRAWAL = "quarantine_active_withdrawal"
    QUARANTINE_CATALOG_DRIFT = "quarantine_catalog_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_BRANCH_COUNT = "quarantine_branch_count"


@runtime_checkable
class _ReportLike(Protocol):
    accept: bool
    report_digest: bytes


@dataclass(frozen=True)
class ServiceContinuitySignal:
    """A normalized local report from one garden-service branch.

    The branch name is deliberately a plain string so branchlets can be folded
    without changing the record algebra.  A signal can be accepted, held, or
    quarantined; an active withdrawal is accepted negative evidence that blocks
    service use rather than proving global truth.
    """

    branch: str
    report_digest: bytes
    accept: bool
    reason: str = ""
    quarantined: bool = False
    catalog_digest: bytes | None = None
    scope_digest: bytes | None = None
    request_digest: bytes | None = None
    service_name: str | None = None
    active_withdrawal: bool = False
    refused_usefully: bool = False
    watch_only: bool = False
    pressure_digests: tuple[bytes, ...] = ()

    def __post_init__(self) -> None:
        if not self.branch or len(self.branch.encode("utf-8")) > 80:
            raise ValueError("continuity branch must be short and non-empty")
        if len(self.report_digest) != 32:
            raise ValueError("continuity report_digest must be 32 bytes")
        for name, value in (("catalog_digest", self.catalog_digest), ("scope_digest", self.scope_digest), ("request_digest", self.request_digest)):
            if value is not None and len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes when present")
        if self.service_name is not None and len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name too large")
        for digest in self.pressure_digests:
            if len(digest) != 32:
                raise ValueError("pressure digests must be 32 bytes")

    @classmethod
    def from_report(
        cls,
        branch: str,
        report: _ReportLike,
        *,
        catalog_digest: bytes | None = None,
        scope_digest: bytes | None = None,
        request_digest: bytes | None = None,
        service_name: str | None = None,
        watch_only: bool = False,
    ) -> "ServiceContinuitySignal":
        """Normalize an existing branchlet report without importing every type."""
        decision = getattr(report, "decision_kind", None)
        decision_value = getattr(decision, "value", str(decision or ""))
        service = getattr(report, "service", None)
        service_value = getattr(service, "value", service_name)
        return cls(
            branch=branch,
            report_digest=getattr(report, "report_digest"),
            accept=bool(getattr(report, "accept")),
            reason=str(getattr(report, "reason", decision_value)),
            quarantined=bool(getattr(report, "quarantined", str(decision_value).startswith("quarantine_"))),
            catalog_digest=catalog_digest if catalog_digest is not None else getattr(report, "catalog_digest", None),
            scope_digest=scope_digest if scope_digest is not None else getattr(report, "scope_id", None),
            request_digest=request_digest if request_digest is not None else getattr(report, "request_digest", None),
            service_name=str(service_value) if service_value is not None else None,
            active_withdrawal=bool(getattr(report, "active_withdrawal", False)),
            refused_usefully=bool(getattr(report, "refused_usefully", False)),
            watch_only=watch_only,
            pressure_digests=tuple(getattr(report, "pressure_digests", ()) or ()),
        )

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"branch": self.branch,
            b"report": self.report_digest,
            b"accept": 1 if self.accept else 0,
            b"quarantined": 1 if self.quarantined else 0,
            b"catalog": self.catalog_digest or b"",
            b"scope": self.scope_digest or b"",
            b"request": self.request_digest or b"",
            b"service": self.service_name or "",
            b"active_withdrawal": 1 if self.active_withdrawal else 0,
            b"refused_usefully": 1 if self.refused_usefully else 0,
            b"watch_only": 1 if self.watch_only else 0,
            b"pressures": list(self.pressure_digests),
        }


@dataclass(frozen=True)
class ServiceContinuityPolicy:
    required_branches: tuple[str, ...]
    min_distinct_branches: int = 4
    allow_active_withdrawal: bool = False
    allow_duplicate_branches: bool = False
    require_positive_non_refusal_branch: bool = True

    def __post_init__(self) -> None:
        if not self.required_branches:
            raise ValueError("service continuity requires at least one required branch")
        if self.min_distinct_branches <= 0:
            raise ValueError("min_distinct_branches must be positive")
        if self.min_distinct_branches < len(set(self.required_branches)):
            object.__setattr__(self, "min_distinct_branches", len(set(self.required_branches)))


@dataclass(frozen=True)
class ServiceContinuityReport:
    decision_kind: ServiceContinuityDecisionKind
    accept: bool
    reason: str
    branches: tuple[str, ...]
    catalog_digest: bytes | None
    scope_digest: bytes | None
    request_digest: bytes | None
    accepted_signal_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: ServiceContinuityDecisionKind,
    accept: bool,
    reason: str,
    *,
    signals: Iterable[ServiceContinuitySignal],
    catalog_digest: bytes | None = None,
    scope_digest: bytes | None = None,
    request_digest: bytes | None = None,
    pressures: Iterable[bytes] = (),
) -> ServiceContinuityReport:
    signal_tuple = tuple(signals)
    branches = tuple(sorted({signal.branch for signal in signal_tuple}))
    accepted = tuple(sorted(signal.report_digest for signal in signal_tuple if signal.accept))
    pressure_tuple = tuple(sorted(set(pressures) | {digest for signal in signal_tuple for digest in signal.pressure_digests}))
    digest = sha256(SERVICE_CONTINUITY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"branches": list(branches),
        b"catalog": catalog_digest or b"",
        b"scope": scope_digest or b"",
        b"request": request_digest or b"",
        b"accepted": list(accepted),
        b"pressures": list(pressure_tuple),
    }))
    return ServiceContinuityReport(kind, accept, reason, branches, catalog_digest, scope_digest, request_digest, accepted, pressure_tuple, digest)


def assess_service_continuity(
    signals: Iterable[ServiceContinuitySignal],
    *,
    policy: ServiceContinuityPolicy,
    expected_catalog_digest: bytes | None = None,
    expected_scope_digest: bytes | None = None,
    expected_request_digest: bytes | None = None,
    previously_seen_reports: Iterable[bytes] = (),
) -> ServiceContinuityReport:
    """Join service branch reports before advancing a garden-service side effect."""
    signal_tuple = tuple(signals)
    if not signal_tuple:
        return _report(ServiceContinuityDecisionKind.HOLD_MISSING_REQUIRED_BRANCH, False, "no service-continuity signals supplied", signals=())

    seen_reports = set(previously_seen_reports)
    branches_seen: dict[str, bytes] = {}
    for signal in signal_tuple:
        if signal.report_digest in seen_reports:
            return _report(ServiceContinuityDecisionKind.QUARANTINE_REPLAY, False, "service-continuity signal replayed", signals=signal_tuple, pressures=(signal.report_digest,))
        if not policy.allow_duplicate_branches and signal.branch in branches_seen:
            return _report(ServiceContinuityDecisionKind.QUARANTINE_DUPLICATE_BRANCH, False, "duplicate branch report in one continuity window", signals=signal_tuple, pressures=(branches_seen[signal.branch], signal.report_digest))
        branches_seen[signal.branch] = signal.report_digest
        if signal.quarantined:
            return _report(ServiceContinuityDecisionKind.QUARANTINE_BRANCH_REPORT, False, f"branch {signal.branch} is quarantined", signals=signal_tuple, pressures=(signal.report_digest,))
        if signal.active_withdrawal and not policy.allow_active_withdrawal:
            return _report(ServiceContinuityDecisionKind.QUARANTINE_ACTIVE_WITHDRAWAL, False, "active withdrawal blocks service continuity", signals=signal_tuple, pressures=(signal.report_digest,))

    branches = set(branches_seen)
    missing = tuple(branch for branch in policy.required_branches if branch not in branches)
    if missing:
        return _report(ServiceContinuityDecisionKind.HOLD_MISSING_REQUIRED_BRANCH, False, "missing required branches: " + ",".join(missing), signals=signal_tuple)
    if len(branches) < policy.min_distinct_branches:
        return _report(ServiceContinuityDecisionKind.QUARANTINE_BRANCH_COUNT, False, "too few distinct service-continuity branches", signals=signal_tuple)

    catalog_values = {signal.catalog_digest for signal in signal_tuple if signal.catalog_digest is not None}
    if expected_catalog_digest is not None:
        catalog_values.add(expected_catalog_digest)
    if len(catalog_values) > 1:
        return _report(ServiceContinuityDecisionKind.QUARANTINE_CATALOG_DRIFT, False, "service-continuity catalog digests drifted", signals=signal_tuple, pressures=[digest for digest in catalog_values if digest is not None])
    scope_values = {signal.scope_digest for signal in signal_tuple if signal.scope_digest is not None}
    if expected_scope_digest is not None:
        scope_values.add(expected_scope_digest)
    if len(scope_values) > 1:
        return _report(ServiceContinuityDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "service-continuity scope digests drifted", signals=signal_tuple, pressures=[digest for digest in scope_values if digest is not None])
    request_values = {signal.request_digest for signal in signal_tuple if signal.request_digest is not None}
    if expected_request_digest is not None:
        request_values.add(expected_request_digest)
    if len(request_values) > 1:
        return _report(ServiceContinuityDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "service-continuity request digests drifted", signals=signal_tuple, pressures=[digest for digest in request_values if digest is not None])

    if any(not signal.accept for signal in signal_tuple):
        return _report(ServiceContinuityDecisionKind.HOLD_REFUSAL_ONLY_OR_WATCH_ONLY, False, "one or more service-continuity branches is hold/watch-only", signals=signal_tuple)
    if policy.require_positive_non_refusal_branch and not any(signal.accept and not signal.refused_usefully and not signal.watch_only for signal in signal_tuple):
        return _report(ServiceContinuityDecisionKind.HOLD_REFUSAL_ONLY_OR_WATCH_ONLY, False, "all accepted signals are refusals or watch-only evidence", signals=signal_tuple)

    catalog = next(iter(catalog_values)) if catalog_values else None
    scope = next(iter(scope_values)) if scope_values else None
    request = next(iter(request_values)) if request_values else None
    return _report(ServiceContinuityDecisionKind.ACCEPT_SERVICE_CONTINUITY, True, "service-continuity branches agree on local side-effect boundary", signals=signal_tuple, catalog_digest=catalog, scope_digest=scope, request_digest=request)
