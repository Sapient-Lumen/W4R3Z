"""Repeated service-epoch ledger for garden service continuity.

rev0038 joined many service reports at one request boundary.  rev0039 treats the
next seam as risky: one locally accepted service window must not automatically
make a garden sticky across future epochs.  This module keeps tiny, typed epoch
observations and asks whether continuity is stable, still watching, or poisoned
by replay, fork, drift, stale withdrawal, or refusal-only service.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .servicecontinuity import ServiceContinuitySignal

SERVICE_EPOCH_LEDGER_DOMAIN = DOMAIN + b":service-epoch-ledger-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceEpochOutcome(str, Enum):
    COMPLETED = "completed"
    USEFUL_REFUSAL = "useful_refusal"
    WATCH_ONLY = "watch_only"
    ACTIVE_WITHDRAWAL = "active_withdrawal"
    QUARANTINED = "quarantined"


class ServiceEpochLedgerDecisionKind(str, Enum):
    ACCEPT_STABLE_SERVICE = "accept_stable_service"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    HOLD_NEEDS_MORE_EPOCHS = "hold_needs_more_epochs"
    HOLD_REFUSAL_BACKOFF = "hold_refusal_backoff"
    HOLD_WATCH_ONLY = "hold_watch_only"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_EPOCH_ROLLBACK = "quarantine_epoch_rollback"
    QUARANTINE_EPOCH_FORK = "quarantine_epoch_fork"
    QUARANTINE_GAP = "quarantine_gap"
    QUARANTINE_ACTIVE_WITHDRAWAL = "quarantine_active_withdrawal"
    QUARANTINE_BRANCH_REPORT = "quarantine_branch_report"
    QUARANTINE_CATALOG_DRIFT = "quarantine_catalog_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_REQUEST_DRIFT = "quarantine_request_drift"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REFUSAL_ONLY_LOOP = "quarantine_refusal_only_loop"


@dataclass(frozen=True)
class ServiceEpochObservation:
    epoch: int
    observed_at: int
    expires_at: int
    service_name: str
    catalog_digest: bytes
    scope_digest: bytes
    request_digest: bytes
    report_digest: bytes
    outcome: ServiceEpochOutcome
    branch_count: int
    family_id: str = "unknown"
    pressure_digests: tuple[bytes, ...] = ()

    def __post_init__(self) -> None:
        if self.epoch < 0:
            raise ValueError("service epoch must be non-negative")
        if self.expires_at <= self.observed_at:
            raise ValueError("service epoch observation expires_at must be after observed_at")
        if not self.service_name or len(self.service_name.encode("utf-8")) > 80:
            raise ValueError("service_name must be short and non-empty")
        if not self.family_id or len(self.family_id.encode("utf-8")) > 80:
            raise ValueError("family_id must be short and non-empty")
        for name, value in (
            ("catalog_digest", self.catalog_digest),
            ("scope_digest", self.scope_digest),
            ("request_digest", self.request_digest),
            ("report_digest", self.report_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for digest in self.pressure_digests:
            if len(digest) != 32:
                raise ValueError("pressure digests must be 32 bytes")

    @classmethod
    def from_continuity_signals(
        cls,
        *,
        epoch: int,
        observed_at: int,
        expires_at: int,
        service_name: str,
        catalog_digest: bytes,
        scope_digest: bytes,
        request_digest: bytes,
        signals: Iterable[ServiceContinuitySignal],
        family_id: str = "local",
    ) -> "ServiceEpochObservation":
        signal_tuple = tuple(signals)
        branch_count = len({signal.branch for signal in signal_tuple})
        pressure = tuple(sorted({digest for signal in signal_tuple for digest in signal.pressure_digests}))
        if any(signal.active_withdrawal for signal in signal_tuple):
            outcome = ServiceEpochOutcome.ACTIVE_WITHDRAWAL
        elif any(signal.quarantined or not signal.accept for signal in signal_tuple):
            outcome = ServiceEpochOutcome.QUARANTINED
        elif signal_tuple and all(signal.refused_usefully for signal in signal_tuple):
            outcome = ServiceEpochOutcome.USEFUL_REFUSAL
        elif signal_tuple and all(signal.watch_only for signal in signal_tuple):
            outcome = ServiceEpochOutcome.WATCH_ONLY
        else:
            outcome = ServiceEpochOutcome.COMPLETED
        report_digest = sha256(SERVICE_EPOCH_LEDGER_DOMAIN + b":from-continuity:" + bencode({
            b"epoch": epoch,
            b"service": service_name,
            b"catalog": catalog_digest,
            b"scope": scope_digest,
            b"request": request_digest,
            b"signals": [signal.report_digest for signal in signal_tuple],
            b"outcome": outcome.value,
        }))
        return cls(epoch, observed_at, expires_at, service_name, catalog_digest, scope_digest, request_digest, report_digest, outcome, branch_count, family_id, pressure)

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"epoch": self.epoch,
            b"observed_at": self.observed_at,
            b"expires_at": self.expires_at,
            b"service": self.service_name,
            b"catalog": self.catalog_digest,
            b"scope": self.scope_digest,
            b"request": self.request_digest,
            b"report": self.report_digest,
            b"outcome": self.outcome.value,
            b"branch_count": self.branch_count,
            b"family": self.family_id,
            b"pressures": list(self.pressure_digests),
        }


@dataclass(frozen=True)
class ServiceEpochLedgerPolicy:
    min_epochs: int = 3
    min_completed_epochs: int = 2
    min_distinct_families: int = 2
    min_branch_count: int = 4
    max_refusal_streak: int = 2
    max_gap: int = 1
    allow_watch_accept: bool = True


@dataclass(frozen=True)
class ServiceEpochLedgerReport:
    decision_kind: ServiceEpochLedgerDecisionKind
    accept: bool
    reason: str
    highest_epoch: int
    completed_epochs: int
    refusal_streak: int
    families: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def watch_only(self) -> bool:
        return self.decision_kind is ServiceEpochLedgerDecisionKind.ACCEPT_WITH_WATCH


def _report(kind: ServiceEpochLedgerDecisionKind, accept: bool, reason: str, observations: tuple[ServiceEpochObservation, ...], pressures: Iterable[bytes] = ()) -> ServiceEpochLedgerReport:
    sorted_obs = tuple(sorted(observations, key=lambda item: (item.epoch, item.report_digest)))
    completed = sum(1 for obs in sorted_obs if obs.outcome is ServiceEpochOutcome.COMPLETED)
    families = tuple(sorted({obs.family_id for obs in sorted_obs}))
    refusal_streak = 0
    for obs in reversed(sorted_obs):
        if obs.outcome is ServiceEpochOutcome.USEFUL_REFUSAL:
            refusal_streak += 1
        else:
            break
    pressure_t = tuple(sorted(set(pressures) | {digest for obs in sorted_obs for digest in obs.pressure_digests}))
    highest = max((obs.epoch for obs in sorted_obs), default=-1)
    digest = sha256(SERVICE_EPOCH_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"highest": highest,
        b"observations": [obs.bvalue() for obs in sorted_obs],
        b"pressures": list(pressure_t),
    }))
    return ServiceEpochLedgerReport(kind, accept, reason, highest, completed, refusal_streak, families, pressure_t, digest)


def assess_service_epoch_ledger(
    observations: Iterable[ServiceEpochObservation],
    *,
    policy: ServiceEpochLedgerPolicy | None = None,
    now: int,
    expected_service_name: str | None = None,
    expected_catalog_digest: bytes | None = None,
    expected_scope_digest: bytes | None = None,
    expected_request_digest: bytes | None = None,
    previously_seen_reports: Iterable[bytes] = (),
    previous_highest_epoch: int | None = None,
) -> ServiceEpochLedgerReport:
    policy = policy or ServiceEpochLedgerPolicy()
    obs = tuple(sorted(observations, key=lambda item: (item.epoch, item.report_digest)))
    if not obs:
        return _report(ServiceEpochLedgerDecisionKind.HOLD_NEEDS_MORE_EPOCHS, False, "no observations", obs)
    seen_reports = set(previously_seen_reports)
    if any(item.report_digest in seen_reports for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_REPLAY, False, "replayed service epoch observation", obs)
    if any(item.observed_at > now or item.expires_at <= now for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "epoch observation outside local time window", obs)
    if previous_highest_epoch is not None and max(item.epoch for item in obs) < previous_highest_epoch:
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_EPOCH_ROLLBACK, False, "service epoch rollback against local memory", obs)
    by_epoch: dict[int, set[bytes]] = {}
    for item in obs:
        by_epoch.setdefault(item.epoch, set()).add(item.report_digest)
    if any(len(digests) > 1 for digests in by_epoch.values()):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_EPOCH_FORK, False, "same epoch has conflicting observations", obs)
    epochs = sorted(by_epoch)
    for left, right in zip(epochs, epochs[1:]):
        if right - left > policy.max_gap + 1:
            return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_GAP, False, "epoch ledger has an unbounded gap", obs)
    if expected_service_name and any(item.service_name != expected_service_name for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "service name drift", obs)
    if expected_catalog_digest is not None and any(item.catalog_digest != expected_catalog_digest for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_CATALOG_DRIFT, False, "catalog digest drift", obs)
    if expected_scope_digest is not None and any(item.scope_digest != expected_scope_digest for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_SCOPE_DRIFT, False, "scope digest drift", obs)
    if expected_request_digest is not None and any(item.request_digest != expected_request_digest for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_REQUEST_DRIFT, False, "request digest drift", obs)
    if any(item.outcome is ServiceEpochOutcome.ACTIVE_WITHDRAWAL for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_ACTIVE_WITHDRAWAL, False, "active withdrawal observed", obs)
    if any(item.outcome is ServiceEpochOutcome.QUARANTINED or item.branch_count < policy.min_branch_count for item in obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_BRANCH_REPORT, False, "quarantined or weak branch report observed", obs)
    if len(obs) < policy.min_epochs:
        return _report(ServiceEpochLedgerDecisionKind.HOLD_NEEDS_MORE_EPOCHS, False, "not enough service epochs", obs)
    families = {item.family_id for item in obs}
    completed = sum(1 for item in obs if item.outcome is ServiceEpochOutcome.COMPLETED)
    refusals = sum(1 for item in obs if item.outcome is ServiceEpochOutcome.USEFUL_REFUSAL)
    watches = sum(1 for item in obs if item.outcome is ServiceEpochOutcome.WATCH_ONLY)
    if refusals == len(obs):
        return _report(ServiceEpochLedgerDecisionKind.QUARANTINE_REFUSAL_ONLY_LOOP, False, "refusal-only service history", obs)
    trailing_refusals = 0
    for item in reversed(obs):
        if item.outcome is ServiceEpochOutcome.USEFUL_REFUSAL:
            trailing_refusals += 1
        else:
            break
    if trailing_refusals > policy.max_refusal_streak:
        return _report(ServiceEpochLedgerDecisionKind.HOLD_REFUSAL_BACKOFF, False, "too many trailing useful refusals", obs)
    if watches == len(obs):
        return _report(ServiceEpochLedgerDecisionKind.HOLD_WATCH_ONLY, False, "watch-only service history", obs)
    if completed >= policy.min_completed_epochs and len(families) >= policy.min_distinct_families:
        return _report(ServiceEpochLedgerDecisionKind.ACCEPT_STABLE_SERVICE, True, "stable multi-epoch service", obs)
    if policy.allow_watch_accept and completed >= 1 and len(families) >= policy.min_distinct_families:
        return _report(ServiceEpochLedgerDecisionKind.ACCEPT_WITH_WATCH, True, "partial service continuity accepted with watch", obs)
    return _report(ServiceEpochLedgerDecisionKind.HOLD_NEEDS_MORE_EPOCHS, False, "insufficient completions or family diversity", obs)
