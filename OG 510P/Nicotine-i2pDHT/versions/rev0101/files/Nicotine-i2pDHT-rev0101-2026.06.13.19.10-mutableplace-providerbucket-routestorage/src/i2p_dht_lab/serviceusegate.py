"""Join service catalog, load, withdrawal, and relay evidence before use.

A future client should not use a garden service merely because a catalog was
signed or a relay report looked diverse.  The side effect boundary is the exact
service request.  This module joins the local reports that are most likely to
be mis-bound during implementation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .loadsheath import LoadSheathReport
from .servicecatalog import GardenServiceClass, ServiceCatalogReport
from .servicerelay import ServiceRelayReport
from .servicewithdrawal import ServiceWithdrawalReport

SERVICE_USE_GATE_DOMAIN = DOMAIN + b":service-use-gate-v1:"


class ServiceUseDecisionKind(str, Enum):
    ACCEPT_SERVICE_USE = "accept_service_use"
    ACCEPT_WITH_USEFUL_REFUSAL_PRESSURE = "accept_with_useful_refusal_pressure"
    HOLD_LOW_RELAY_DIVERSITY = "hold_low_relay_diversity"
    HOLD_WITHDRAWN_SERVICE = "hold_withdrawn_service"
    QUARANTINE_CATALOG_REPORT = "quarantine_catalog_report"
    QUARANTINE_LOAD_REPORT = "quarantine_load_report"
    QUARANTINE_RELAY_REPORT = "quarantine_relay_report"
    QUARANTINE_DIGEST_MISMATCH = "quarantine_digest_mismatch"
    QUARANTINE_SERVICE_NOT_ADVERTISED = "quarantine_service_not_advertised"
    QUARANTINE_REQUEST_REPLAY = "quarantine_request_replay"


@dataclass(frozen=True)
class ServiceUseIntent:
    request_digest: bytes
    catalog_digest: bytes
    service: GardenServiceClass
    purpose: str
    max_metadata_units: int = 0

    def __post_init__(self) -> None:
        if len(self.request_digest) != 32 or len(self.catalog_digest) != 32:
            raise ValueError("service use intent digests must be 32 bytes")
        if self.max_metadata_units < 0:
            raise ValueError("metadata budget must be non-negative")
        if len(self.purpose.encode("utf-8")) > 96:
            raise ValueError("service use purpose is too large")

    @property
    def intent_digest(self) -> bytes:
        return sha256(SERVICE_USE_GATE_DOMAIN + b":intent:" + bencode({
            b"request": self.request_digest,
            b"catalog": self.catalog_digest,
            b"service": self.service.value,
            b"purpose": self.purpose,
            b"max_metadata_units": self.max_metadata_units,
        }))


@dataclass(frozen=True)
class ServiceUseGateReport:
    decision_kind: ServiceUseDecisionKind
    accept: bool
    reason: str
    request_digest: bytes
    catalog_digest: bytes
    service: str
    joined_report_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceUseDecisionKind, accept: bool, reason: str, *, intent: ServiceUseIntent, joined: tuple[bytes, ...], pressures: tuple[bytes, ...] = ()) -> ServiceUseGateReport:
    joined_t = tuple(sorted(set(joined)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(SERVICE_USE_GATE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"request": intent.request_digest,
        b"catalog": intent.catalog_digest,
        b"service": intent.service.value,
        b"joined": list(joined_t),
        b"pressures": list(pressure_t),
    }))
    return ServiceUseGateReport(kind, accept, reason, intent.request_digest, intent.catalog_digest, intent.service.value, joined_t, pressure_t, digest)


def assess_service_use_gate(
    intent: ServiceUseIntent,
    *,
    catalog_report: ServiceCatalogReport,
    load_report: LoadSheathReport,
    relay_report: ServiceRelayReport,
    withdrawal_report: ServiceWithdrawalReport | None = None,
    previously_seen_requests: tuple[bytes, ...] = (),
) -> ServiceUseGateReport:
    """Join local reports before a service-use side effect is attempted."""
    joined = (catalog_report.report_digest, load_report.report_digest, relay_report.report_digest) + ((withdrawal_report.report_digest,) if withdrawal_report else ())
    if intent.request_digest in set(previously_seen_requests):
        return _report(ServiceUseDecisionKind.QUARANTINE_REQUEST_REPLAY, False, "service request replayed", intent=intent, joined=joined, pressures=(intent.request_digest,))
    if not catalog_report.accept or catalog_report.quarantined:
        return _report(ServiceUseDecisionKind.QUARANTINE_CATALOG_REPORT, False, "service use requires accepted catalog report", intent=intent, joined=joined, pressures=(catalog_report.report_digest,))
    if not load_report.accept or load_report.quarantined:
        return _report(ServiceUseDecisionKind.QUARANTINE_LOAD_REPORT, False, "service use requires accepted load sheath report", intent=intent, joined=joined, pressures=(load_report.report_digest,))
    if relay_report.quarantined:
        return _report(ServiceUseDecisionKind.QUARANTINE_RELAY_REPORT, False, "quarantined relay evidence blocks service use", intent=intent, joined=joined, pressures=(relay_report.report_digest,))
    if intent.catalog_digest != catalog_report.catalog_digest or intent.catalog_digest != load_report.catalog_digest or intent.catalog_digest != relay_report.catalog_digest:
        return _report(ServiceUseDecisionKind.QUARANTINE_DIGEST_MISMATCH, False, "service use reports are not bound to one catalog digest", intent=intent, joined=joined, pressures=(intent.catalog_digest, catalog_report.catalog_digest, load_report.catalog_digest, relay_report.catalog_digest))
    if intent.service.value not in catalog_report.accepted_services:
        return _report(ServiceUseDecisionKind.QUARANTINE_SERVICE_NOT_ADVERTISED, False, "requested service is not in the accepted catalog", intent=intent, joined=joined, pressures=(catalog_report.report_digest,))
    if withdrawal_report is not None and withdrawal_report.active_withdrawal:
        if not withdrawal_report.affected_services or intent.service.value in withdrawal_report.affected_services:
            return _report(ServiceUseDecisionKind.HOLD_WITHDRAWN_SERVICE, False, "live withdrawal report affects requested service", intent=intent, joined=joined, pressures=(withdrawal_report.report_digest,))
    if not relay_report.accept:
        return _report(ServiceUseDecisionKind.HOLD_LOW_RELAY_DIVERSITY, False, "relay evidence has not yet reached diversity threshold", intent=intent, joined=joined, pressures=(relay_report.report_digest,))
    if load_report.refused_digests or relay_report.decision_kind.value.endswith("refusal"):
        return _report(ServiceUseDecisionKind.ACCEPT_WITH_USEFUL_REFUSAL_PRESSURE, True, "service use accepted with visible useful-refusal pressure", intent=intent, joined=joined, pressures=load_report.refused_digests)
    return _report(ServiceUseDecisionKind.ACCEPT_SERVICE_USE, True, "service use accepted after catalog/load/relay/withdrawal join", intent=intent, joined=joined)
