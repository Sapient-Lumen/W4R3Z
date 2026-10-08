"""Probeable garden service health without pretending probes are free.

rev0037 adds a small service-probe lane.  A service catalog can advertise that a
garden gives seed gates, head watches, witness queries, bridge gateways, and so
on.  A future client will want to probe those services before trusting them.
The hard part is that probes reveal interest and can become a cheap oracle for
attackers or a load-amplifier against gardens.

This module keeps probes typed, bounded, cover-mixed, and catalog-bound.  Probe
receipts are signed observations, not reputation and not global truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule, ServiceCatalogReport

SERVICE_PROBE_DOMAIN = DOMAIN + b":service-probe-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceProbeStatus(str, Enum):
    HEALTHY = "healthy"
    USEFULLY_REFUSED = "usefully_refused"
    OVERLOADED = "overloaded"
    UNKNOWN = "unknown"


class ServiceProbeDecisionKind(str, Enum):
    ACCEPT_PROBE_PLAN = "accept_probe_plan"
    ACCEPT_HEALTHY_RECEIPT = "accept_healthy_receipt"
    ACCEPT_USEFUL_REFUSAL_RECEIPT = "accept_useful_refusal_receipt"
    HOLD_OVERLOADED_RECEIPT = "hold_overloaded_receipt"
    HOLD_CATALOG_REPORT = "hold_catalog_report"
    HOLD_SERVICE_NOT_ADVERTISED = "hold_service_not_advertised"
    HOLD_PUBLIC_SERVICE_REQUIRED = "hold_public_service_required"
    HOLD_COVER_MISSING = "hold_cover_missing"
    QUARANTINE_RAW_KEY_EXPOSURE = "quarantine_raw_key_exposure"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_TIME_WINDOW = "quarantine_time_window"
    QUARANTINE_RECEIPT_SIGNATURE = "quarantine_receipt_signature"
    QUARANTINE_RECEIPT_PLAN_MISMATCH = "quarantine_receipt_plan_mismatch"
    QUARANTINE_RECEIPT_CATALOG_MISMATCH = "quarantine_receipt_catalog_mismatch"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"


@dataclass(frozen=True)
class ServiceProbePlan:
    request_id: bytes
    catalog_digest: bytes
    service: GardenServiceClass
    scope_digest: bytes
    object_hint_digest: bytes = ZERO_DIGEST
    cover_target_count: int = 2
    raw_key_exposures: int = 0
    source_family: str = "unknown-source"
    path_family: str = "unknown-path"
    require_public: bool = False
    issued_at: int = 0
    expires_at: int = 300

    def __post_init__(self) -> None:
        for name, value in (("request_id", self.request_id), ("catalog_digest", self.catalog_digest), ("scope_digest", self.scope_digest), ("object_hint_digest", self.object_hint_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.cover_target_count < 0 or self.raw_key_exposures < 0:
            raise ValueError("probe cover/raw exposure counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("probe plan expires_at must be after issued_at")
        if not self.source_family or not self.path_family:
            raise ValueError("probe plan needs family hints")

    @property
    def plan_digest(self) -> bytes:
        return sha256(SERVICE_PROBE_DOMAIN + b":plan:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"request_id": self.request_id,
            b"catalog_digest": self.catalog_digest,
            b"service": self.service.value,
            b"scope_digest": self.scope_digest,
            b"object_hint_digest": self.object_hint_digest,
            b"cover_target_count": self.cover_target_count,
            b"raw_key_exposures": self.raw_key_exposures,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"require_public": 1 if self.require_public else 0,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }


@dataclass(frozen=True)
class ServiceProbeReceipt:
    signer_public_key: bytes
    request_id: bytes
    catalog_digest: bytes
    service: GardenServiceClass
    status: ServiceProbeStatus
    sequence: int
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    latency_ms: int = 0
    retry_after_seconds: int = 0
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("signer_public_key", self.signer_public_key), ("request_id", self.request_id), ("catalog_digest", self.catalog_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0 or self.latency_ms < 0 or self.retry_after_seconds < 0:
            raise ValueError("probe receipt counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("probe receipt time window invalid")
        if not self.source_family or not self.path_family:
            raise ValueError("probe receipt needs source/path family hints")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        plan: ServiceProbePlan,
        status: ServiceProbeStatus,
        sequence: int,
        source_family: str,
        path_family: str,
        issued_at: int,
        ttl: int = 300,
        latency_ms: int = 0,
        retry_after_seconds: int = 0,
    ) -> "ServiceProbeReceipt":
        if ttl <= 0:
            raise ValueError("probe receipt ttl must be positive")
        unsigned = cls(
            signer_public_key=keypair.public_key_bytes,
            request_id=plan.request_id,
            catalog_digest=plan.catalog_digest,
            service=plan.service,
            status=status,
            sequence=sequence,
            source_family=source_family,
            path_family=path_family,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            latency_ms=latency_ms,
            retry_after_seconds=retry_after_seconds,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"request_id": self.request_id,
            b"catalog_digest": self.catalog_digest,
            b"service": self.service.value,
            b"status": self.status.value,
            b"sequence": self.sequence,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"latency_ms": self.latency_ms,
            b"retry_after_seconds": self.retry_after_seconds,
        }

    def unsigned_payload(self) -> bytes:
        return SERVICE_PROBE_DOMAIN + b":receipt-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def receipt_digest(self) -> bytes:
        return sha256(SERVICE_PROBE_DOMAIN + b":receipt:" + self.unsigned_payload() + self.signature)

    def verify(self) -> bool:
        return verify_signature(self.signer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ServiceProbeReport:
    decision_kind: ServiceProbeDecisionKind
    accept: bool
    reason: str
    plan_digest: bytes
    receipt_digest: bytes
    catalog_digest: bytes
    service: str
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceProbeDecisionKind, accept: bool, reason: str, *, plan: ServiceProbePlan, receipt: ServiceProbeReceipt | None = None, pressures: Iterable[bytes] = ()) -> ServiceProbeReport:
    pressure_t = tuple(sorted(set(pressures)))
    receipt_digest = receipt.receipt_digest if receipt is not None else ZERO_DIGEST
    digest = sha256(SERVICE_PROBE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"plan": plan.plan_digest,
        b"receipt": receipt_digest,
        b"catalog": plan.catalog_digest,
        b"service": plan.service.value,
        b"pressures": list(pressure_t),
    }))
    return ServiceProbeReport(kind, accept, reason, plan.plan_digest, receipt_digest, plan.catalog_digest, plan.service.value, pressure_t, digest)


def _service_public(catalog: ServiceCatalogCapsule, service: GardenServiceClass) -> bool:
    return any(item.service is service and item.public for item in catalog.services)


def assess_probe_plan(plan: ServiceProbePlan, *, catalog: ServiceCatalogCapsule, catalog_report: ServiceCatalogReport, now: int, seen_request_ids: Iterable[bytes] = (), max_raw_key_exposures: int = 0, min_cover_targets: int = 1) -> ServiceProbeReport:
    """Assess a service-probe plan before spending network metadata."""
    if plan.request_id in set(seen_request_ids):
        return _report(ServiceProbeDecisionKind.QUARANTINE_REPLAY, False, "service probe request id replayed", plan=plan, pressures=(plan.request_id,))
    if not (plan.issued_at <= now < plan.expires_at):
        return _report(ServiceProbeDecisionKind.QUARANTINE_TIME_WINDOW, False, "service probe plan is outside its local time window", plan=plan, pressures=(plan.plan_digest,))
    if not catalog_report.accept or catalog_report.quarantined:
        return _report(ServiceProbeDecisionKind.HOLD_CATALOG_REPORT, False, "service catalog was not accepted before probing", plan=plan, pressures=(catalog_report.report_digest,))
    if plan.catalog_digest != catalog.catalog_digest or plan.catalog_digest != catalog_report.catalog_digest:
        return _report(ServiceProbeDecisionKind.QUARANTINE_RECEIPT_CATALOG_MISMATCH, False, "probe plan catalog digest does not match accepted catalog", plan=plan, pressures=(plan.catalog_digest, catalog.catalog_digest, catalog_report.catalog_digest))
    if plan.service.value not in catalog_report.accepted_services:
        return _report(ServiceProbeDecisionKind.HOLD_SERVICE_NOT_ADVERTISED, False, "probe targets a service not accepted in the catalog report", plan=plan, pressures=(plan.plan_digest, catalog_report.report_digest))
    if plan.require_public and not _service_public(catalog, plan.service):
        return _report(ServiceProbeDecisionKind.HOLD_PUBLIC_SERVICE_REQUIRED, False, "probe requires a public service but catalog service is not public", plan=plan, pressures=(plan.plan_digest, catalog.catalog_digest))
    if plan.raw_key_exposures > max_raw_key_exposures:
        return _report(ServiceProbeDecisionKind.QUARANTINE_RAW_KEY_EXPOSURE, False, "service probe exceeds raw-key exposure budget", plan=plan, pressures=(plan.object_hint_digest, plan.plan_digest))
    if plan.cover_target_count < min_cover_targets:
        return _report(ServiceProbeDecisionKind.HOLD_COVER_MISSING, False, "service probe needs cover targets before spending interest", plan=plan, pressures=(plan.plan_digest,))
    return _report(ServiceProbeDecisionKind.ACCEPT_PROBE_PLAN, True, "service probe plan accepted within catalog and metadata budget", plan=plan)


def assess_probe_receipt(plan: ServiceProbePlan, receipt: ServiceProbeReceipt, *, catalog: ServiceCatalogCapsule, catalog_report: ServiceCatalogReport, now: int, seen_receipt_families: Iterable[str] = ()) -> ServiceProbeReport:
    """Assess a signed service-probe receipt as evidence, not truth."""
    plan_report = assess_probe_plan(plan, catalog=catalog, catalog_report=catalog_report, now=now)
    if not plan_report.accept:
        return plan_report
    if not (receipt.issued_at <= now < receipt.expires_at):
        return _report(ServiceProbeDecisionKind.QUARANTINE_TIME_WINDOW, False, "service probe receipt is outside its local time window", plan=plan, receipt=receipt, pressures=(receipt.receipt_digest,))
    if not receipt.verify():
        return _report(ServiceProbeDecisionKind.QUARANTINE_RECEIPT_SIGNATURE, False, "service probe receipt signature is invalid", plan=plan, receipt=receipt, pressures=(receipt.receipt_digest,))
    if receipt.request_id != plan.request_id or receipt.service is not plan.service:
        return _report(ServiceProbeDecisionKind.QUARANTINE_RECEIPT_PLAN_MISMATCH, False, "service probe receipt does not match plan request/service", plan=plan, receipt=receipt, pressures=(receipt.receipt_digest, plan.plan_digest))
    if receipt.catalog_digest != plan.catalog_digest:
        return _report(ServiceProbeDecisionKind.QUARANTINE_RECEIPT_CATALOG_MISMATCH, False, "service probe receipt catalog digest does not match plan", plan=plan, receipt=receipt, pressures=(receipt.catalog_digest, plan.catalog_digest))
    families = set(seen_receipt_families)
    families.add(receipt.source_family)
    if len(families) < 2 and receipt.status is ServiceProbeStatus.HEALTHY:
        return _report(ServiceProbeDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "one-family healthy service receipts are capture pressure", plan=plan, receipt=receipt, pressures=(receipt.receipt_digest,))
    if receipt.status is ServiceProbeStatus.HEALTHY:
        return _report(ServiceProbeDecisionKind.ACCEPT_HEALTHY_RECEIPT, True, "healthy service receipt accepted as local evidence", plan=plan, receipt=receipt)
    if receipt.status is ServiceProbeStatus.USEFULLY_REFUSED:
        return _report(ServiceProbeDecisionKind.ACCEPT_USEFUL_REFUSAL_RECEIPT, True, "useful refusal receipt accepted as capacity evidence, not success", plan=plan, receipt=receipt)
    if receipt.status is ServiceProbeStatus.OVERLOADED:
        return _report(ServiceProbeDecisionKind.HOLD_OVERLOADED_RECEIPT, False, "overloaded service receipt asks caller to back off", plan=plan, receipt=receipt, pressures=(receipt.receipt_digest,))
    return _report(ServiceProbeDecisionKind.HOLD_OVERLOADED_RECEIPT, False, "unknown service receipt is not healthy enough to advance", plan=plan, receipt=receipt, pressures=(receipt.receipt_digest,))
