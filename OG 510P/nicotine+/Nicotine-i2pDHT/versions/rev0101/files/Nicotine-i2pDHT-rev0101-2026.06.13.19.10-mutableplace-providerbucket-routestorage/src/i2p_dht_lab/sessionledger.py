"""Repeated service-session ledger pressure.

A service lease makes one ongoing boundary explicit, but repeated service windows
can still drift: receipts can replay, refusals can launder health, one family can
own the whole story, or completed units can exceed the current lease budget.
This module keeps the model deliberately local and deterministic.  It does not
score global reputation; it decides whether one caller/garden service session may
advance sticky local memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .servicecatalog import GardenServiceClass
from .servicelease import ServiceLeaseReport

SESSION_LEDGER_DOMAIN = DOMAIN + b":session-ledger-v1:"


class SessionLedgerDecisionKind(str, Enum):
    ACCEPT_SESSION_ADVANCE = "accept_session_advance"
    ACCEPT_SESSION_ADVANCE_WITH_WATCH = "accept_session_advance_with_watch"
    HOLD_INSUFFICIENT_WINDOWS = "hold_insufficient_windows"
    HOLD_REFUSAL_ONLY_LOOP = "hold_refusal_only_loop"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    QUARANTINE_LEASE_REPORT = "quarantine_lease_report"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_WINDOW_FORK = "quarantine_window_fork"
    QUARANTINE_BINDING_DRIFT = "quarantine_binding_drift"
    QUARANTINE_ACTIVE_WITHDRAWAL = "quarantine_active_withdrawal"
    QUARANTINE_QUOTA_OVERSPEND = "quarantine_quota_overspend"
    QUARANTINE_NEGATIVE_AFTER_SUCCESS = "quarantine_negative_after_success"


@dataclass(frozen=True)
class ServiceSessionObservation:
    window_id: int
    event_digest: bytes
    lease_digest: bytes
    continuity_report_digest: bytes
    catalog_digest: bytes
    caller_node_id: bytes
    scope_digest: bytes
    object_digest: bytes
    request_digest: bytes
    service: GardenServiceClass
    completed_units: int = 0
    refused_units: int = 0
    accept: bool = True
    active_withdrawal: bool = False
    hard_negative: bool = False
    source_family: str = "unknown-source"
    path_family: str = "unknown-path"
    pressure_digests: tuple[bytes, ...] = ()

    def __post_init__(self) -> None:
        for name, value in (
            ("event_digest", self.event_digest),
            ("lease_digest", self.lease_digest),
            ("continuity_report_digest", self.continuity_report_digest),
            ("catalog_digest", self.catalog_digest),
            ("caller_node_id", self.caller_node_id),
            ("scope_digest", self.scope_digest),
            ("object_digest", self.object_digest),
            ("request_digest", self.request_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.window_id < 0:
            raise ValueError("session observation window_id must be non-negative")
        if self.completed_units < 0 or self.refused_units < 0:
            raise ValueError("session observation units must be non-negative")
        if not self.source_family or not self.path_family:
            raise ValueError("session observation families must be non-empty")
        for digest in self.pressure_digests:
            if len(digest) != 32:
                raise ValueError("pressure digests must be 32 bytes")

    @classmethod
    def from_lease_report(
        cls,
        lease_report: ServiceLeaseReport,
        *,
        window_id: int,
        event_digest: bytes,
        completed_units: int = 0,
        refused_units: int = 0,
        accept: bool | None = None,
        active_withdrawal: bool = False,
        hard_negative: bool = False,
        source_family: str = "unknown-source",
        path_family: str = "unknown-path",
    ) -> "ServiceSessionObservation":
        return cls(
            window_id=window_id,
            event_digest=event_digest,
            lease_digest=lease_report.lease_digest,
            continuity_report_digest=lease_report.continuity_report_digest,
            catalog_digest=lease_report.catalog_digest,
            caller_node_id=lease_report.caller_node_id,
            scope_digest=lease_report.scope_digest,
            object_digest=lease_report.object_digest,
            request_digest=lease_report.request_digest,
            service=lease_report.service,
            completed_units=completed_units,
            refused_units=refused_units,
            accept=lease_report.accept if accept is None else accept,
            active_withdrawal=active_withdrawal,
            hard_negative=hard_negative,
            source_family=source_family,
            path_family=path_family,
            pressure_digests=lease_report.pressure_digests,
        )

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"window_id": self.window_id,
            b"event_digest": self.event_digest,
            b"lease_digest": self.lease_digest,
            b"continuity_report_digest": self.continuity_report_digest,
            b"catalog_digest": self.catalog_digest,
            b"caller_node_id": self.caller_node_id,
            b"scope_digest": self.scope_digest,
            b"object_digest": self.object_digest,
            b"request_digest": self.request_digest,
            b"service": self.service.value,
            b"completed_units": self.completed_units,
            b"refused_units": self.refused_units,
            b"accept": 1 if self.accept else 0,
            b"active_withdrawal": 1 if self.active_withdrawal else 0,
            b"hard_negative": 1 if self.hard_negative else 0,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"pressures": list(self.pressure_digests),
        }


@dataclass(frozen=True)
class SessionLedgerPolicy:
    min_windows: int = 2
    min_source_families: int = 2
    min_path_families: int = 2
    max_refusal_streak: int = 2
    max_completed_units: int = 100
    require_completed_units: bool = True
    allow_active_withdrawal: bool = False

    def __post_init__(self) -> None:
        if self.min_windows <= 0 or self.min_source_families <= 0 or self.min_path_families <= 0:
            raise ValueError("session ledger minima must be positive")
        if self.max_refusal_streak < 0 or self.max_completed_units < 0:
            raise ValueError("session ledger maxima must be non-negative")


@dataclass(frozen=True)
class SessionLedgerReport:
    decision_kind: SessionLedgerDecisionKind
    accept: bool
    reason: str
    windows: tuple[int, ...]
    completed_units: int
    refused_units: int
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(
    kind: SessionLedgerDecisionKind,
    accept: bool,
    reason: str,
    *,
    observations: Iterable[ServiceSessionObservation],
    pressures: Iterable[bytes] = (),
) -> SessionLedgerReport:
    obs = tuple(observations)
    pressure_tuple = tuple(sorted(set(pressures) | {item for observation in obs for item in observation.pressure_digests}))
    windows = tuple(sorted({observation.window_id for observation in obs}))
    source_families = tuple(sorted({observation.source_family for observation in obs}))
    path_families = tuple(sorted({observation.path_family for observation in obs}))
    completed = sum(observation.completed_units for observation in obs)
    refused = sum(observation.refused_units for observation in obs)
    digest = sha256(SESSION_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"windows": list(windows),
        b"completed": completed,
        b"refused": refused,
        b"source_families": list(source_families),
        b"path_families": list(path_families),
        b"pressures": list(pressure_tuple),
    }))
    return SessionLedgerReport(kind, accept, reason, windows, completed, refused, source_families, path_families, pressure_tuple, digest)


def assess_session_ledger(
    observations: Iterable[ServiceSessionObservation],
    *,
    policy: SessionLedgerPolicy,
    lease_report: ServiceLeaseReport,
    previously_seen_events: Iterable[bytes] = (),
) -> SessionLedgerReport:
    """Join repeated service observations before sticky session memory advances."""
    obs = tuple(observations)
    if not lease_report.accept or lease_report.quarantined:
        return _report(SessionLedgerDecisionKind.QUARANTINE_LEASE_REPORT, False, "lease report did not accept", observations=obs, pressures=(lease_report.report_digest,))
    seen_events = set(previously_seen_events)
    by_window: dict[int, bytes] = {}
    refusal_streak = 0
    max_refusal_streak = 0
    for observation in sorted(obs, key=lambda item: item.window_id):
        if observation.event_digest in seen_events:
            return _report(SessionLedgerDecisionKind.QUARANTINE_REPLAY, False, "session observation replayed", observations=obs, pressures=(observation.event_digest,))
        if observation.window_id in by_window and by_window[observation.window_id] != observation.event_digest:
            return _report(SessionLedgerDecisionKind.QUARANTINE_WINDOW_FORK, False, "same window has conflicting session events", observations=obs, pressures=(by_window[observation.window_id], observation.event_digest))
        by_window[observation.window_id] = observation.event_digest
        if observation.lease_digest != lease_report.lease_digest or observation.continuity_report_digest != lease_report.continuity_report_digest or observation.catalog_digest != lease_report.catalog_digest or observation.caller_node_id != lease_report.caller_node_id or observation.scope_digest != lease_report.scope_digest or observation.object_digest != lease_report.object_digest or observation.request_digest != lease_report.request_digest or observation.service is not lease_report.service:
            return _report(SessionLedgerDecisionKind.QUARANTINE_BINDING_DRIFT, False, "session observation drifted from lease boundary", observations=obs, pressures=(lease_report.report_digest, observation.event_digest))
        if observation.active_withdrawal and not policy.allow_active_withdrawal:
            return _report(SessionLedgerDecisionKind.QUARANTINE_ACTIVE_WITHDRAWAL, False, "active withdrawal inside session ledger", observations=obs, pressures=(observation.event_digest,))
        if observation.hard_negative and observation.completed_units > 0:
            return _report(SessionLedgerDecisionKind.QUARANTINE_NEGATIVE_AFTER_SUCCESS, False, "hard negative and completed work in one window", observations=obs, pressures=(observation.event_digest,))
        if observation.refused_units > 0 and observation.completed_units == 0:
            refusal_streak += 1
            max_refusal_streak = max(max_refusal_streak, refusal_streak)
        else:
            refusal_streak = 0

    if len({item.window_id for item in obs}) < policy.min_windows:
        return _report(SessionLedgerDecisionKind.HOLD_INSUFFICIENT_WINDOWS, False, "not enough service windows", observations=obs)

    completed = sum(item.completed_units for item in obs)
    if completed > policy.max_completed_units:
        return _report(SessionLedgerDecisionKind.QUARANTINE_QUOTA_OVERSPEND, False, "completed units exceed lease/session budget", observations=obs, pressures=(lease_report.lease_digest,))
    if policy.require_completed_units and completed <= 0:
        return _report(SessionLedgerDecisionKind.HOLD_REFUSAL_ONLY_LOOP, False, "session window only contains refusals/watch evidence", observations=obs)
    if max_refusal_streak > policy.max_refusal_streak:
        return _report(SessionLedgerDecisionKind.HOLD_REFUSAL_ONLY_LOOP, False, "too many consecutive refusal-only windows", observations=obs)

    source_families = {item.source_family for item in obs}
    path_families = {item.path_family for item in obs}
    if len(source_families) < policy.min_source_families or len(path_families) < policy.min_path_families:
        return _report(SessionLedgerDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "session lacks family/path diversity", observations=obs)

    if any(item.hard_negative for item in obs):
        return _report(SessionLedgerDecisionKind.ACCEPT_SESSION_ADVANCE_WITH_WATCH, True, "session accepted with retained negative pressure", observations=obs)
    return _report(SessionLedgerDecisionKind.ACCEPT_SESSION_ADVANCE, True, "session ledger accepted", observations=obs)
