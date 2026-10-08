"""Signed garden service catalogs bound to accepted start profiles.

rev0036 treats "I am a garden/bridge" as too vague.  A future node should
advertise a short, signed service catalog that is bound to the accepted start
profile, router harness, and launch/start report.  The catalog is not global
truth and not a reputation object; it is a local dispatch surface that says
what this node is volunteering to do this epoch and what it refuses to imply.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .launchquorum import LaunchMode
from .routerharness import RouterHarnessReport
from .startmatrix import StartMatrixReport, StartProfile

SERVICE_CATALOG_DOMAIN = DOMAIN + b":service-catalog-v1:"
ZERO_DIGEST = b"\x00" * 32


class GardenServiceClass(str, Enum):
    SEED_GATE = "seed_gate"
    HEAD_WATCH = "head_watch"
    WITNESS_QUERY = "witness_query"
    REGION_REPROVIDE = "region_reprovide"
    BULK_PROVIDER = "bulk_provider"
    WAKE_COURIER = "wake_courier"
    BRIDGE_GATEWAY = "bridge_gateway"
    DIAGNOSTIC_MIRROR = "diagnostic_mirror"


class ServiceCatalogDecisionKind(str, Enum):
    ACCEPT_SERVICE_CATALOG = "accept_service_catalog"
    ACCEPT_LEAF_MINIMAL_CATALOG = "accept_leaf_minimal_catalog"
    HOLD_SERVICE_COUNT = "hold_service_count"
    HOLD_PROFILE_NOT_GIVING = "hold_profile_not_giving"
    QUARANTINE_START_PROFILE = "quarantine_start_profile"
    QUARANTINE_ROUTER_HARNESS = "quarantine_router_harness"
    QUARANTINE_BINDING_MISMATCH = "quarantine_binding_mismatch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_BUDGET_OVERCLAIM = "quarantine_budget_overclaim"
    QUARANTINE_BRIDGE_DRIFT = "quarantine_bridge_drift"


@dataclass(frozen=True)
class ServiceDescriptor:
    service: GardenServiceClass
    max_streams: int
    max_units: int
    reserve_units: int = 0
    public: bool = False
    metadata_cost: str = "normal"
    note: str = ""

    def __post_init__(self) -> None:
        if self.max_streams < 0 or self.max_units < 0 or self.reserve_units < 0:
            raise ValueError("service budgets must be non-negative")
        if self.reserve_units > self.max_units:
            raise ValueError("reserve units cannot exceed max units")
        if self.metadata_cost not in {"low", "normal", "power", "lab"}:
            raise ValueError("unknown metadata cost level")
        if len(self.note.encode("utf-8")) > 160:
            raise ValueError("service note is too large for catalog capsule")

    @property
    def giving(self) -> bool:
        return self.max_streams > 0 or self.max_units > 0

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"service": self.service.value,
            b"max_streams": self.max_streams,
            b"max_units": self.max_units,
            b"reserve_units": self.reserve_units,
            b"public": 1 if self.public else 0,
            b"metadata_cost": self.metadata_cost,
            b"note": self.note,
        }


@dataclass(frozen=True)
class ServiceCatalogCapsule:
    issuer_node_id: bytes
    issuer_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    profile_digest: bytes
    start_report_digest: bytes
    router_report_digest: bytes
    router_profile_digest: bytes
    mode: LaunchMode
    services: tuple[ServiceDescriptor, ...]
    previous_catalog_digest: bytes = ZERO_DIGEST
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("issuer_node_id", self.issuer_node_id),
            ("issuer_public_key", self.issuer_public_key),
            ("profile_digest", self.profile_digest),
            ("start_report_digest", self.start_report_digest),
            ("router_report_digest", self.router_report_digest),
            ("router_profile_digest", self.router_profile_digest),
            ("previous_catalog_digest", self.previous_catalog_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("catalog sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("catalog expires_at must be after issued_at")
        if len(self.services) > 32:
            raise ValueError("catalog service list is too large for the capsule")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        issuer_node_id: bytes,
        sequence: int,
        issued_at: int,
        expires_at: int,
        profile: StartProfile,
        start_report: StartMatrixReport,
        router_report: RouterHarnessReport,
        services: Iterable[ServiceDescriptor],
        previous_catalog_digest: bytes = ZERO_DIGEST,
    ) -> "ServiceCatalogCapsule":
        unsigned = cls(
            issuer_node_id=issuer_node_id,
            issuer_public_key=keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            profile_digest=profile.profile_digest,
            start_report_digest=start_report.report_digest,
            router_report_digest=router_report.report_digest,
            router_profile_digest=router_report.profile_digest,
            mode=profile.mode,
            services=tuple(services),
            previous_catalog_digest=previous_catalog_digest,
            signature=b"",
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"issuer_node_id": self.issuer_node_id,
            b"issuer_public_key": self.issuer_public_key,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"profile_digest": self.profile_digest,
            b"start_report_digest": self.start_report_digest,
            b"router_report_digest": self.router_report_digest,
            b"router_profile_digest": self.router_profile_digest,
            b"mode": self.mode.value,
            b"services": [service.bvalue() for service in self.services],
            b"previous_catalog_digest": self.previous_catalog_digest,
        })

    @property
    def catalog_digest(self) -> bytes:
        return sha256(SERVICE_CATALOG_DOMAIN + b":catalog:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)

    @property
    def service_classes(self) -> frozenset[GardenServiceClass]:
        return frozenset(item.service for item in self.services)

    @property
    def giving_service_count(self) -> int:
        return sum(1 for item in self.services if item.giving)

    @property
    def total_units(self) -> int:
        return sum(item.max_units for item in self.services)

    @property
    def total_streams(self) -> int:
        return sum(item.max_streams for item in self.services)

    @property
    def public_bridge(self) -> bool:
        return any(item.service is GardenServiceClass.BRIDGE_GATEWAY and item.public for item in self.services)


@dataclass(frozen=True)
class ServiceCatalogReport:
    decision_kind: ServiceCatalogDecisionKind
    accept: bool
    reason: str
    catalog_digest: bytes
    profile_digest: bytes
    start_report_digest: bytes
    router_report_digest: bytes
    accepted_services: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceCatalogDecisionKind, accept: bool, reason: str, *, catalog: ServiceCatalogCapsule, pressures: Iterable[bytes] = ()) -> ServiceCatalogReport:
    pressure_t = tuple(sorted(set(pressures)))
    services = tuple(sorted(service.service.value for service in catalog.services)) if accept else ()
    digest = sha256(SERVICE_CATALOG_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"catalog": catalog.catalog_digest,
        b"profile": catalog.profile_digest,
        b"start": catalog.start_report_digest,
        b"router": catalog.router_report_digest,
        b"services": list(services),
        b"pressures": list(pressure_t),
    }))
    return ServiceCatalogReport(kind, accept, reason, catalog.catalog_digest, catalog.profile_digest, catalog.start_report_digest, catalog.router_report_digest, services, pressure_t, digest)


def assess_service_catalog(
    catalog: ServiceCatalogCapsule,
    *,
    profile: StartProfile,
    start_report: StartMatrixReport,
    router_report: RouterHarnessReport,
    now: int,
    highest_seen_sequence: int | None = None,
    same_sequence_digest: bytes | None = None,
    previously_seen_catalogs: Iterable[bytes] = (),
    max_total_units_normal: int = 100_000,
    max_total_streams_normal: int = 96,
) -> ServiceCatalogReport:
    """Classify a service catalog before it is used for dispatch or gossip."""
    if catalog.catalog_digest in set(previously_seen_catalogs):
        return _report(ServiceCatalogDecisionKind.QUARANTINE_REPLAY, False, "service catalog digest replayed", catalog=catalog, pressures=(catalog.catalog_digest,))
    if highest_seen_sequence is not None and catalog.sequence < highest_seen_sequence:
        return _report(ServiceCatalogDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "service catalog sequence rolled back", catalog=catalog, pressures=(catalog.catalog_digest,))
    if same_sequence_digest is not None and catalog.sequence == highest_seen_sequence and catalog.catalog_digest != same_sequence_digest:
        return _report(ServiceCatalogDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence service catalog fork", catalog=catalog, pressures=(catalog.catalog_digest, same_sequence_digest))
    if now < catalog.issued_at or now >= catalog.expires_at:
        return _report(ServiceCatalogDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "service catalog is not live in this local clock window", catalog=catalog, pressures=(catalog.catalog_digest,))
    if not catalog.verify():
        return _report(ServiceCatalogDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "service catalog signature did not verify", catalog=catalog, pressures=(catalog.catalog_digest,))
    if not start_report.accept or start_report.quarantined:
        return _report(ServiceCatalogDecisionKind.QUARANTINE_START_PROFILE, False, "start matrix did not accept before service catalog", catalog=catalog, pressures=(start_report.report_digest,))
    if not router_report.accept or router_report.quarantined:
        return _report(ServiceCatalogDecisionKind.QUARANTINE_ROUTER_HARNESS, False, "router harness did not accept before service catalog", catalog=catalog, pressures=(router_report.report_digest,))
    expected = (profile.profile_digest, start_report.report_digest, router_report.report_digest, router_report.profile_digest)
    observed = (catalog.profile_digest, catalog.start_report_digest, catalog.router_report_digest, catalog.router_profile_digest)
    if expected != observed or catalog.mode is not profile.mode:
        return _report(ServiceCatalogDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "service catalog is not bound to the accepted start/router reports", catalog=catalog, pressures=expected + observed)
    if profile.mode is LaunchMode.LEAF:
        if catalog.services:
            return _report(ServiceCatalogDecisionKind.HOLD_PROFILE_NOT_GIVING, False, "leaf profile cannot advertise garden service catalog without profile upgrade", catalog=catalog, pressures=(catalog.catalog_digest,))
        return _report(ServiceCatalogDecisionKind.ACCEPT_LEAF_MINIMAL_CATALOG, True, "leaf minimal empty service catalog accepted", catalog=catalog)
    if catalog.giving_service_count < profile.garden_service_count:
        return _report(ServiceCatalogDecisionKind.HOLD_SERVICE_COUNT, False, "catalog gives fewer services than the accepted start profile declared", catalog=catalog, pressures=(catalog.catalog_digest, profile.profile_digest))
    if profile.mode is LaunchMode.BRIDGE and (not profile.public_bridge_enabled or not catalog.public_bridge):
        return _report(ServiceCatalogDecisionKind.QUARANTINE_BRIDGE_DRIFT, False, "bridge start profile requires explicit public bridge service in catalog", catalog=catalog, pressures=(catalog.catalog_digest, profile.profile_digest))
    if profile.metadata_budget_level != "power" and (catalog.total_units > max_total_units_normal or catalog.total_streams > max_total_streams_normal):
        return _report(ServiceCatalogDecisionKind.QUARANTINE_BUDGET_OVERCLAIM, False, "non-power profile overclaimed service catalog capacity", catalog=catalog, pressures=(catalog.catalog_digest, profile.profile_digest))
    return _report(ServiceCatalogDecisionKind.ACCEPT_SERVICE_CATALOG, True, "service catalog accepted as local giving surface", catalog=catalog)
