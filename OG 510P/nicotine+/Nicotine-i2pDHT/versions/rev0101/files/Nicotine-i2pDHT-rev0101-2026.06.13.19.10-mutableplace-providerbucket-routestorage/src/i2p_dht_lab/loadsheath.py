"""Per-service load sheath for garden catalogs.

A service catalog says what a garden is willing to do.  A load sheath says how
that willingness sheds work when demand exceeds a bounded budget.  This module
keeps useful refusals useful: refusal-only service is not healthy, protected
services get reserves, and catalog mismatch cannot authorize work.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule, ServiceCatalogReport

LOAD_SHEATH_DOMAIN = DOMAIN + b":load-sheath-v1:"


class LoadSheathDecisionKind(str, Enum):
    ACCEPT_LOAD_SHEATH = "accept_load_sheath"
    ACCEPT_WITH_USEFUL_REFUSALS = "accept_with_useful_refusals"
    HOLD_PROTECTED_STARVATION = "hold_protected_starvation"
    HOLD_REFUSAL_ONLY_LOOP = "hold_refusal_only_loop"
    QUARANTINE_CATALOG_REPORT = "quarantine_catalog_report"
    QUARANTINE_CATALOG_DIGEST_MISMATCH = "quarantine_catalog_digest_mismatch"
    QUARANTINE_MISSING_SERVICE_BUDGET = "quarantine_missing_service_budget"
    QUARANTINE_REPLAYED_WINDOW = "quarantine_replayed_window"
    QUARANTINE_BUDGET_OVERFLOW = "quarantine_budget_overflow"


@dataclass(frozen=True)
class ServiceDemand:
    service: GardenServiceClass
    family_id: str
    units: int
    stream_cost: int = 1
    priority: int = 0
    raw_key_exposures: int = 0

    def __post_init__(self) -> None:
        if self.units < 0 or self.stream_cost < 0 or self.raw_key_exposures < 0:
            raise ValueError("demand costs must be non-negative")
        if not self.family_id:
            raise ValueError("demand needs a family id")

    @property
    def digest(self) -> bytes:
        return sha256(LOAD_SHEATH_DOMAIN + b":demand:" + bencode({
            b"service": self.service.value,
            b"family": self.family_id,
            b"units": self.units,
            b"streams": self.stream_cost,
            b"priority": self.priority,
            b"raw_key_exposures": self.raw_key_exposures,
        }))


@dataclass(frozen=True)
class ServiceLoadBudget:
    service: GardenServiceClass
    max_units_per_window: int
    max_streams_per_window: int
    reserve_units: int = 0
    max_refusals_per_window: int = 16
    protected: bool = False

    def __post_init__(self) -> None:
        if self.max_units_per_window < 0 or self.max_streams_per_window < 0 or self.reserve_units < 0 or self.max_refusals_per_window < 0:
            raise ValueError("load budgets must be non-negative")
        if self.reserve_units > self.max_units_per_window:
            raise ValueError("reserve exceeds service budget")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"service": self.service.value,
            b"max_units": self.max_units_per_window,
            b"max_streams": self.max_streams_per_window,
            b"reserve_units": self.reserve_units,
            b"max_refusals": self.max_refusals_per_window,
            b"protected": 1 if self.protected else 0,
        }


@dataclass(frozen=True)
class LoadSheathPolicy:
    window_id: bytes
    catalog_digest: bytes
    budgets: tuple[ServiceLoadBudget, ...]
    max_raw_key_exposures: int = 0
    min_protected_accepts: int = 1

    def __post_init__(self) -> None:
        if len(self.window_id) != 32 or len(self.catalog_digest) != 32:
            raise ValueError("load sheath window/catalog digests must be 32 bytes")
        if self.max_raw_key_exposures < 0 or self.min_protected_accepts < 0:
            raise ValueError("load sheath metadata/protected knobs must be non-negative")
        services = [budget.service for budget in self.budgets]
        if len(set(services)) != len(services):
            raise ValueError("duplicate service load budget")

    @property
    def policy_digest(self) -> bytes:
        return sha256(LOAD_SHEATH_DOMAIN + b":policy:" + bencode({
            b"window": self.window_id,
            b"catalog": self.catalog_digest,
            b"budgets": [budget.bvalue() for budget in self.budgets],
            b"max_raw_key_exposures": self.max_raw_key_exposures,
            b"min_protected_accepts": self.min_protected_accepts,
        }))


@dataclass(frozen=True)
class LoadSheathReport:
    decision_kind: LoadSheathDecisionKind
    accept: bool
    reason: str
    window_id: bytes
    catalog_digest: bytes
    accepted_digests: tuple[bytes, ...]
    refused_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: LoadSheathDecisionKind, accept: bool, reason: str, *, policy: LoadSheathPolicy, accepted: Iterable[bytes] = (), refused: Iterable[bytes] = (), pressures: Iterable[bytes] = ()) -> LoadSheathReport:
    accepted_t = tuple(sorted(set(accepted)))
    refused_t = tuple(sorted(set(refused)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(LOAD_SHEATH_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"window": policy.window_id,
        b"catalog": policy.catalog_digest,
        b"accepted": list(accepted_t),
        b"refused": list(refused_t),
        b"pressures": list(pressure_t),
    }))
    return LoadSheathReport(kind, accept, reason, policy.window_id, policy.catalog_digest, accepted_t, refused_t, pressure_t, digest)


def assess_load_sheath(
    policy: LoadSheathPolicy,
    demands: Iterable[ServiceDemand],
    *,
    catalog: ServiceCatalogCapsule,
    catalog_report: ServiceCatalogReport,
    previously_seen_windows: Iterable[bytes] = (),
) -> LoadSheathReport:
    """Select local accepts/refusals for a service window without side effects."""
    if policy.window_id in set(previously_seen_windows):
        return _report(LoadSheathDecisionKind.QUARANTINE_REPLAYED_WINDOW, False, "load sheath window replayed", policy=policy, pressures=(policy.window_id,))
    if not catalog_report.accept or catalog_report.quarantined:
        return _report(LoadSheathDecisionKind.QUARANTINE_CATALOG_REPORT, False, "load sheath requires accepted service catalog report", policy=policy, pressures=(catalog_report.report_digest,))
    if policy.catalog_digest != catalog.catalog_digest or catalog_report.catalog_digest != catalog.catalog_digest:
        return _report(LoadSheathDecisionKind.QUARANTINE_CATALOG_DIGEST_MISMATCH, False, "load sheath policy/report/catalog digests do not match", policy=policy, pressures=(policy.catalog_digest, catalog.catalog_digest, catalog_report.catalog_digest))
    budgets = {budget.service: budget for budget in policy.budgets}
    catalog_services = {service.service for service in catalog.services}
    if not catalog_services.issubset(set(budgets)):
        return _report(LoadSheathDecisionKind.QUARANTINE_MISSING_SERVICE_BUDGET, False, "every advertised service needs a load budget", policy=policy, pressures=(catalog.catalog_digest, policy.policy_digest))

    raw_exposures = 0
    used_units = {service: 0 for service in budgets}
    used_streams = {service: 0 for service in budgets}
    refusals = {service: 0 for service in budgets}
    accepted: list[bytes] = []
    refused: list[bytes] = []
    protected_accepts = 0
    sorted_demands = sorted(tuple(demands), key=lambda demand: (-demand.priority, demand.service.value, demand.family_id, demand.digest))
    for demand in sorted_demands:
        if demand.service not in budgets:
            refused.append(demand.digest)
            continue
        budget = budgets[demand.service]
        raw_exposures += demand.raw_key_exposures
        would_units = used_units[demand.service] + demand.units
        would_streams = used_streams[demand.service] + demand.stream_cost
        if raw_exposures > policy.max_raw_key_exposures:
            return _report(LoadSheathDecisionKind.QUARANTINE_BUDGET_OVERFLOW, False, "load sheath raw-key exposure budget overflow", policy=policy, accepted=accepted, refused=refused, pressures=(demand.digest, policy.policy_digest))
        if would_units <= budget.max_units_per_window and would_streams <= budget.max_streams_per_window:
            used_units[demand.service] = would_units
            used_streams[demand.service] = would_streams
            accepted.append(demand.digest)
            if budget.protected:
                protected_accepts += 1
        else:
            refusals[demand.service] += 1
            refused.append(demand.digest)
            if refusals[demand.service] > budget.max_refusals_per_window:
                return _report(LoadSheathDecisionKind.HOLD_REFUSAL_ONLY_LOOP, False, "service window exceeded useful-refusal budget", policy=policy, accepted=accepted, refused=refused, pressures=(demand.digest, policy.policy_digest))

    protected_budgets = [budget for budget in budgets.values() if budget.protected]
    if protected_budgets and protected_accepts < policy.min_protected_accepts:
        return _report(LoadSheathDecisionKind.HOLD_PROTECTED_STARVATION, False, "protected service work starved in load sheath window", policy=policy, accepted=accepted, refused=refused, pressures=(policy.policy_digest,))
    if refused:
        return _report(LoadSheathDecisionKind.ACCEPT_WITH_USEFUL_REFUSALS, True, "load sheath accepted protected work and usefully refused overflow", policy=policy, accepted=accepted, refused=refused)
    return _report(LoadSheathDecisionKind.ACCEPT_LOAD_SHEATH, True, "load sheath accepted all demands inside window budgets", policy=policy, accepted=accepted, refused=refused)
