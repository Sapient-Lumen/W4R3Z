"""Joined service handoff before handler side effects.

rev0036 made service advertisements explicit: service catalog capsules say what a
node is willing to do and load sheaths decide which demands fit the current
window.  The next risky seam is handoff.  A handler must not receive work just
because one upstream surface looked good: the catalog, load-sheath decision,
optional relay/egress budget, exact scope/object, source/path diversity, and
replay memory all have to bind to the same intent.

This is deliberately no-network and local-only.  It does not decide global
truth, and it does not execute the handler.  It emits a typed local report that
future code can use before dispatching work to a garden service.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .egressmeter import EgressWindowReport
from .ids import DOMAIN, sha256
from .loadsheath import LoadSheathReport
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule, ServiceCatalogReport

HANDOFF_DOMAIN = DOMAIN + b":service-handoff-v1:"


class HandoffDecisionKind(str, Enum):
    ACCEPT_SERVICE_HANDOFF = "accept_service_handoff"
    ACCEPT_REFUSAL_HANDOFF = "accept_refusal_handoff"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    HOLD_MISSING_EGRESS_REPORT = "hold_missing_egress_report"
    QUARANTINE_CATALOG = "quarantine_catalog"
    QUARANTINE_SHEATH = "quarantine_sheath"
    QUARANTINE_CATALOG_SHEATH_MISMATCH = "quarantine_catalog_sheath_mismatch"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"
    QUARANTINE_UNADVERTISED_SERVICE = "quarantine_unadvertised_service"
    QUARANTINE_UNSCHEDULED_WORK = "quarantine_unscheduled_work"
    QUARANTINE_EGRESS_REPORT = "quarantine_egress_report"
    QUARANTINE_EGRESS_BINDING = "quarantine_egress_binding"


EGRESS_REQUIRED_SERVICES = frozenset({
    GardenServiceClass.BRIDGE_GATEWAY,
    GardenServiceClass.WAKE_COURIER,
    GardenServiceClass.REGION_REPROVIDE,
    GardenServiceClass.BULK_PROVIDER,
})


@dataclass(frozen=True)
class ServiceWorkIntent:
    service: GardenServiceClass
    scope_id: bytes
    object_digest: bytes
    payload_digest: bytes
    request_id: bytes
    actor_public_key: bytes
    source_family: str
    path_family: str
    demand_digest: bytes
    byte_cost: int = 0
    stream_cost: int = 1
    raw_key_exposure: int = 0

    def __post_init__(self) -> None:
        for name, value in (
            ("scope_id", self.scope_id),
            ("object_digest", self.object_digest),
            ("payload_digest", self.payload_digest),
            ("request_id", self.request_id),
            ("actor_public_key", self.actor_public_key),
            ("demand_digest", self.demand_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"handoff intent {name} must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("handoff intent needs source and path family hints")
        if self.byte_cost < 0 or self.stream_cost < 0 or self.raw_key_exposure < 0:
            raise ValueError("handoff intent costs must be non-negative")

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"service": self.service.value,
            b"scope": self.scope_id,
            b"object": self.object_digest,
            b"payload": self.payload_digest,
            b"request": self.request_id,
            b"actor": self.actor_public_key,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"demand": self.demand_digest,
            b"bytes": self.byte_cost,
            b"streams": self.stream_cost,
            b"raw": self.raw_key_exposure,
        }

    @property
    def intent_digest(self) -> bytes:
        return sha256(HANDOFF_DOMAIN + b":intent:" + bencode(self.bvalue()))


@dataclass(frozen=True)
class ServiceHandoffPolicy:
    min_path_families_for_public_or_egress: int = 2
    require_egress_report_for_services: tuple[GardenServiceClass, ...] = tuple(sorted(EGRESS_REQUIRED_SERVICES, key=lambda item: item.value))
    allow_refusal_handoff: bool = True

    def validate(self) -> None:
        if self.min_path_families_for_public_or_egress <= 0:
            raise ValueError("handoff path diversity threshold must be positive")


@dataclass(frozen=True)
class ServiceHandoffReport:
    decision_kind: HandoffDecisionKind
    accept: bool
    reason: str
    catalog_digest: bytes
    sheath_report_digest: bytes
    egress_report_digest: bytes | None
    accepted_intent_digests: tuple[bytes, ...]
    refused_intent_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def refused_usefully(self) -> bool:
        return self.decision_kind is HandoffDecisionKind.ACCEPT_REFUSAL_HANDOFF


def _report(
    kind: HandoffDecisionKind,
    accept: bool,
    reason: str,
    *,
    catalog_digest: bytes,
    sheath_report_digest: bytes,
    egress_report_digest: bytes | None = None,
    accepted: Iterable[bytes] = (),
    refused: Iterable[bytes] = (),
    pressures: Iterable[bytes] = (),
) -> ServiceHandoffReport:
    accepted_t = tuple(sorted(set(accepted)))
    refused_t = tuple(sorted(set(refused)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(HANDOFF_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"catalog": catalog_digest,
        b"sheath": sheath_report_digest,
        b"egress": b"" if egress_report_digest is None else egress_report_digest,
        b"accepted": list(accepted_t),
        b"refused": list(refused_t),
        b"pressures": list(pressure_t),
    }))
    return ServiceHandoffReport(kind, accept, reason, catalog_digest, sheath_report_digest, egress_report_digest, accepted_t, refused_t, pressure_t, digest)


def assess_service_handoff(
    intents: Iterable[ServiceWorkIntent],
    *,
    catalog: ServiceCatalogCapsule,
    catalog_report: ServiceCatalogReport,
    sheath_report: LoadSheathReport,
    egress_report: EgressWindowReport | None = None,
    expected_scope_id: bytes | None = None,
    previously_seen_intents: Iterable[bytes] = (),
    policy: ServiceHandoffPolicy | None = None,
) -> ServiceHandoffReport:
    """Join service catalog, load sheath, optional egress, and exact intents."""
    policy = policy or ServiceHandoffPolicy()
    policy.validate()
    intent_tuple = tuple(intents)
    intent_digests = tuple(intent.intent_digest for intent in intent_tuple)
    if any(digest in set(previously_seen_intents) for digest in intent_digests):
        return _report(HandoffDecisionKind.QUARANTINE_REPLAY, False, "handoff intent replayed", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=intent_digests)
    if not catalog_report.accept or catalog_report.quarantined or catalog_report.catalog_digest != catalog.catalog_digest:
        return _report(HandoffDecisionKind.QUARANTINE_CATALOG, False, "handoff requires accepted matching service catalog", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=(catalog_report.report_digest, catalog.catalog_digest))
    if not sheath_report.accept or sheath_report.quarantined:
        return _report(HandoffDecisionKind.QUARANTINE_SHEATH, False, "handoff requires accepted load sheath", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=(sheath_report.report_digest,))
    if sheath_report.catalog_digest != catalog.catalog_digest or sheath_report.catalog_digest != catalog_report.catalog_digest:
        return _report(HandoffDecisionKind.QUARANTINE_CATALOG_SHEATH_MISMATCH, False, "catalog report, catalog capsule, and load sheath disagree", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=(catalog.catalog_digest, sheath_report.catalog_digest, catalog_report.catalog_digest))
    if expected_scope_id is not None and any(intent.scope_id != expected_scope_id for intent in intent_tuple):
        return _report(HandoffDecisionKind.QUARANTINE_SCOPE_MISMATCH, False, "handoff intent scope does not match caller scope", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=intent_digests)
    advertised = catalog.service_classes
    if any(intent.service not in advertised for intent in intent_tuple):
        return _report(HandoffDecisionKind.QUARANTINE_UNADVERTISED_SERVICE, False, "handoff attempted service absent from catalog", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=intent_digests)

    scheduled_accepts = set(sheath_report.accepted_digests)
    scheduled_refusals = set(sheath_report.refused_digests)
    accepted: list[bytes] = []
    refused: list[bytes] = []
    for intent in intent_tuple:
        if intent.demand_digest in scheduled_accepts:
            accepted.append(intent.intent_digest)
        elif intent.demand_digest in scheduled_refusals and policy.allow_refusal_handoff:
            refused.append(intent.intent_digest)
        else:
            return _report(HandoffDecisionKind.QUARANTINE_UNSCHEDULED_WORK, False, "intent is neither an accepted nor usefully-refused sheath demand", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=(intent.intent_digest, intent.demand_digest))

    requires_egress = any(intent.service in set(policy.require_egress_report_for_services) for intent in intent_tuple)
    public_or_egress = requires_egress or any(next((desc.public for desc in catalog.services if desc.service is intent.service), False) for intent in intent_tuple)
    if public_or_egress and len({intent.path_family for intent in intent_tuple}) < policy.min_path_families_for_public_or_egress:
        return _report(HandoffDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, "public/egress handoff lacks path-family diversity", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=intent_digests)
    if requires_egress:
        if egress_report is None:
            return _report(HandoffDecisionKind.HOLD_MISSING_EGRESS_REPORT, False, "egress-requiring service lacks egress report", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, pressures=intent_digests)
        if not egress_report.accept or egress_report.quarantined:
            return _report(HandoffDecisionKind.QUARANTINE_EGRESS_REPORT, False, "egress report rejected or quarantined", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, egress_report_digest=egress_report.report_digest, pressures=(egress_report.report_digest,))
        if egress_report.total_bytes < sum(intent.byte_cost for intent in intent_tuple) or egress_report.total_streams < sum(intent.stream_cost for intent in intent_tuple):
            return _report(HandoffDecisionKind.QUARANTINE_EGRESS_BINDING, False, "egress report does not cover handoff byte/stream costs", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, egress_report_digest=egress_report.report_digest, pressures=(egress_report.report_digest,))
    if refused and not accepted:
        return _report(HandoffDecisionKind.ACCEPT_REFUSAL_HANDOFF, True, "handoff carries only useful refusals, not handler success", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, egress_report_digest=None if egress_report is None else egress_report.report_digest, refused=refused)
    return _report(HandoffDecisionKind.ACCEPT_SERVICE_HANDOFF, True, "service work accepted by catalog, load sheath, scope, diversity, and egress gates", catalog_digest=catalog.catalog_digest, sheath_report_digest=sheath_report.report_digest, egress_report_digest=None if egress_report is None else egress_report.report_digest, accepted=accepted, refused=refused)
