"""Ingress gate for requests caused by service announcements.

An announcement invites work.  The ingress gate turns that invitation into a
bounded local window before load-sheath scheduling.  It catches replayed
requests, family floods, unadvertised services, and metadata exposure before
work becomes a side effect.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .loadsheath import LoadSheathPolicy, ServiceDemand, assess_load_sheath
from .serviceannounce import ServiceAnnouncementCapsule, ServiceAnnouncementReport
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule, ServiceCatalogReport

INGRESS_GATE_DOMAIN = DOMAIN + b":ingress-gate-v1:"


class IngressGateDecisionKind(str, Enum):
    ACCEPT_INGRESS_WINDOW = "accept_ingress_window"
    ACCEPT_WITH_USEFUL_REFUSALS = "accept_with_useful_refusals"
    HOLD_FAMILY_FLOOD = "hold_family_flood"
    HOLD_LOAD_SHEATH = "hold_load_sheath"
    QUARANTINE_ANNOUNCEMENT = "quarantine_announcement"
    QUARANTINE_BINDING_MISMATCH = "quarantine_binding_mismatch"
    QUARANTINE_REPLAYED_REQUEST = "quarantine_replayed_request"
    QUARANTINE_UNADVERTISED_SERVICE = "quarantine_unadvertised_service"
    QUARANTINE_METADATA_BUDGET = "quarantine_metadata_budget"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"


@dataclass(frozen=True)
class IngressRequest:
    service: GardenServiceClass
    request_id: bytes
    requester_family: str
    path_family: str
    scope_digest: bytes
    object_digest: bytes
    units: int
    priority: int
    raw_key_exposures: int
    issued_at: int
    expires_at: int
    stream_cost: int = 1

    def __post_init__(self) -> None:
        for name, value in (("request_id", self.request_id), ("scope_digest", self.scope_digest), ("object_digest", self.object_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.units < 0 or self.priority < 0 or self.raw_key_exposures < 0 or self.stream_cost < 0:
            raise ValueError("ingress request costs must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("ingress request expires_at must be after issued_at")
        if not self.requester_family or not self.path_family:
            raise ValueError("ingress request needs requester/path family hints")

    @property
    def request_digest(self) -> bytes:
        return sha256(INGRESS_GATE_DOMAIN + b":request:" + bencode({
            b"service": self.service.value,
            b"request_id": self.request_id,
            b"requester_family": self.requester_family,
            b"path_family": self.path_family,
            b"scope": self.scope_digest,
            b"object": self.object_digest,
            b"units": self.units,
            b"priority": self.priority,
            b"raw_key_exposures": self.raw_key_exposures,
            b"stream_cost": self.stream_cost,
        }))

    def to_demand(self) -> ServiceDemand:
        return ServiceDemand(self.service, self.requester_family, self.units, stream_cost=self.stream_cost, priority=self.priority, raw_key_exposures=self.raw_key_exposures)


@dataclass(frozen=True)
class IngressPolicy:
    window_id: bytes
    catalog_digest: bytes
    announcement_digest: bytes
    allowed_services: tuple[GardenServiceClass, ...]
    max_raw_key_exposures: int = 0
    max_requests_per_requester_family: int = 8
    max_requests_per_path_family: int = 8

    def __post_init__(self) -> None:
        for name, value in (("window_id", self.window_id), ("catalog_digest", self.catalog_digest), ("announcement_digest", self.announcement_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.max_raw_key_exposures < 0 or self.max_requests_per_requester_family < 0 or self.max_requests_per_path_family < 0:
            raise ValueError("ingress policy limits must be non-negative")

    @property
    def policy_digest(self) -> bytes:
        return sha256(INGRESS_GATE_DOMAIN + b":policy:" + bencode({
            b"window": self.window_id,
            b"catalog": self.catalog_digest,
            b"announcement": self.announcement_digest,
            b"allowed": [service.value for service in self.allowed_services],
            b"raw": self.max_raw_key_exposures,
            b"requester_cap": self.max_requests_per_requester_family,
            b"path_cap": self.max_requests_per_path_family,
        }))


@dataclass(frozen=True)
class IngressGateReport:
    decision_kind: IngressGateDecisionKind
    accept: bool
    reason: str
    window_id: bytes
    accepted_request_digests: tuple[bytes, ...]
    refused_request_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: IngressGateDecisionKind, accept: bool, reason: str, *, policy: IngressPolicy, accepted: Iterable[bytes] = (), refused: Iterable[bytes] = (), pressures: Iterable[bytes] = ()) -> IngressGateReport:
    accepted_t = tuple(sorted(set(accepted)))
    refused_t = tuple(sorted(set(refused)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(INGRESS_GATE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"window": policy.window_id,
        b"accepted": list(accepted_t),
        b"refused": list(refused_t),
        b"pressures": list(pressure_t),
    }))
    return IngressGateReport(kind, accept, reason, policy.window_id, accepted_t, refused_t, pressure_t, digest)


def assess_ingress_window(
    requests: Iterable[IngressRequest],
    *,
    policy: IngressPolicy,
    catalog: ServiceCatalogCapsule,
    catalog_report: ServiceCatalogReport,
    load_policy: LoadSheathPolicy,
    now: int,
    announcement: ServiceAnnouncementCapsule | None = None,
    announcement_report: ServiceAnnouncementReport | None = None,
    previously_seen_request_ids: Iterable[bytes] = (),
) -> IngressGateReport:
    reqs = tuple(requests)
    if announcement is None or announcement_report is None or not announcement_report.accept or announcement_report.quarantined:
        return _report(IngressGateDecisionKind.QUARANTINE_ANNOUNCEMENT, False, "ingress requires an accepted service announcement", policy=policy, pressures=(policy.announcement_digest,))
    if policy.catalog_digest != catalog.catalog_digest or load_policy.catalog_digest != catalog.catalog_digest or policy.announcement_digest != announcement.announcement_digest or announcement_report.announcement_digest != announcement.announcement_digest:
        return _report(IngressGateDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "ingress policy/catalog/announcement/load binding drift", policy=policy, pressures=(policy.policy_digest, catalog.catalog_digest, announcement.announcement_digest, load_policy.catalog_digest))
    seen_ids = set(previously_seen_request_ids)
    allowed = set(policy.allowed_services)
    visible = {GardenServiceClass(value) for value in announcement_report.visible_services}
    raw = 0
    requester_counts: dict[str, int] = {}
    path_counts: dict[str, int] = {}
    for req in reqs:
        if req.request_id in seen_ids:
            return _report(IngressGateDecisionKind.QUARANTINE_REPLAYED_REQUEST, False, "ingress request id replayed", policy=policy, pressures=(req.request_id,))
        if now < req.issued_at or now >= req.expires_at:
            return _report(IngressGateDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "ingress request outside local clock window", policy=policy, pressures=(req.request_digest,))
        if req.service not in allowed or req.service not in visible:
            return _report(IngressGateDecisionKind.QUARANTINE_UNADVERTISED_SERVICE, False, "ingress request targets unadvertised or disallowed service", policy=policy, pressures=(req.request_digest, announcement.announcement_digest))
        raw += req.raw_key_exposures
        if raw > policy.max_raw_key_exposures:
            return _report(IngressGateDecisionKind.QUARANTINE_METADATA_BUDGET, False, "ingress raw-key exposure budget exceeded", policy=policy, pressures=(req.request_digest, policy.policy_digest))
        requester_counts[req.requester_family] = requester_counts.get(req.requester_family, 0) + 1
        path_counts[req.path_family] = path_counts.get(req.path_family, 0) + 1
        if requester_counts[req.requester_family] > policy.max_requests_per_requester_family or path_counts[req.path_family] > policy.max_requests_per_path_family:
            return _report(IngressGateDecisionKind.HOLD_FAMILY_FLOOD, False, "ingress family flood needs backoff", policy=policy, pressures=(req.request_digest, policy.policy_digest))

    demand_by_digest = {req.to_demand().digest: req for req in reqs}
    load_report = assess_load_sheath(load_policy, (req.to_demand() for req in reqs), catalog=catalog, catalog_report=catalog_report)
    if not load_report.accept or load_report.quarantined:
        return _report(IngressGateDecisionKind.HOLD_LOAD_SHEATH, False, "load sheath did not accept ingress window", policy=policy, pressures=(load_report.report_digest,))
    accepted = [demand_by_digest[digest].request_digest for digest in load_report.accepted_digests if digest in demand_by_digest]
    refused = [demand_by_digest[digest].request_digest for digest in load_report.refused_digests if digest in demand_by_digest]
    if refused:
        return _report(IngressGateDecisionKind.ACCEPT_WITH_USEFUL_REFUSALS, True, "ingress accepted some requests and usefully refused overflow", policy=policy, accepted=accepted, refused=refused)
    return _report(IngressGateDecisionKind.ACCEPT_INGRESS_WINDOW, True, "ingress window accepted inside announcement and load policy", policy=policy, accepted=accepted)
