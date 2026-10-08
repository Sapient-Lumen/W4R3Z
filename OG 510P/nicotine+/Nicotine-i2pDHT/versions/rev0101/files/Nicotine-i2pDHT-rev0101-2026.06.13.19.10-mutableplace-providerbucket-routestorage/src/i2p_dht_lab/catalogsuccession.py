"""Service-catalog succession under key-crisis pressure.

Service catalogs are signed by a DHT key.  When that key rotates, a future node
must not accept a new giving surface merely because the new catalog verifies.
The key-crisis assessment, previous catalog link, profile/router binding, and
sequence advance all need to join at the same scope.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .keycrisis import KeyCrisisAssessment
from .servicecatalog import ServiceCatalogCapsule

CATALOG_SUCCESSION_DOMAIN = DOMAIN + b":catalog-succession-v1:"


class CatalogSuccessionDecisionKind(str, Enum):
    ACCEPT_CATALOG_SUCCESSION = "accept_catalog_succession"
    HOLD_KEY_CRISIS = "hold_key_crisis"
    QUARANTINE_NEW_CATALOG_SIGNATURE = "quarantine_new_catalog_signature"
    QUARANTINE_WRONG_SUCCESSOR_KEY = "quarantine_wrong_successor_key"
    QUARANTINE_PREVIOUS_CATALOG_MISMATCH = "quarantine_previous_catalog_mismatch"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_BINDING_DRIFT = "quarantine_binding_drift"
    QUARANTINE_SERVICE_DOWNGRADE = "quarantine_service_downgrade"


@dataclass(frozen=True)
class CatalogSuccessionReport:
    decision_kind: CatalogSuccessionDecisionKind
    accept: bool
    reason: str
    old_catalog_digest: bytes
    new_catalog_digest: bytes
    accepted_public_key: bytes | None
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: CatalogSuccessionDecisionKind, accept: bool, reason: str, *, old: ServiceCatalogCapsule, new: ServiceCatalogCapsule, accepted_key: bytes | None, pressures: tuple[bytes, ...] = ()) -> CatalogSuccessionReport:
    pressure_tuple = tuple(sorted(set(pressures)))
    digest = sha256(CATALOG_SUCCESSION_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"old": old.catalog_digest,
        b"new": new.catalog_digest,
        b"accepted_key": accepted_key or b"",
        b"pressures": list(pressure_tuple),
    }))
    return CatalogSuccessionReport(kind, accept, reason, old.catalog_digest, new.catalog_digest, accepted_key if accept else None, pressure_tuple, digest)


def assess_catalog_succession(
    *,
    old_catalog: ServiceCatalogCapsule,
    new_catalog: ServiceCatalogCapsule,
    crisis: KeyCrisisAssessment,
    require_no_service_downgrade: bool = True,
) -> CatalogSuccessionReport:
    if not crisis.accept or crisis.accepted_new_public_key is None or crisis.quarantined:
        return _report(CatalogSuccessionDecisionKind.HOLD_KEY_CRISIS, False, crisis.reason, old=old_catalog, new=new_catalog, accepted_key=None, pressures=(crisis.report_digest,))
    if not new_catalog.verify():
        return _report(CatalogSuccessionDecisionKind.QUARANTINE_NEW_CATALOG_SIGNATURE, False, "successor catalog signature failed", old=old_catalog, new=new_catalog, accepted_key=crisis.accepted_new_public_key, pressures=(new_catalog.catalog_digest,))
    if new_catalog.issuer_public_key != crisis.accepted_new_public_key:
        return _report(CatalogSuccessionDecisionKind.QUARANTINE_WRONG_SUCCESSOR_KEY, False, "successor catalog is not signed by the accepted crisis successor key", old=old_catalog, new=new_catalog, accepted_key=crisis.accepted_new_public_key, pressures=(new_catalog.issuer_public_key, crisis.accepted_new_public_key))
    if new_catalog.previous_catalog_digest != old_catalog.catalog_digest:
        return _report(CatalogSuccessionDecisionKind.QUARANTINE_PREVIOUS_CATALOG_MISMATCH, False, "successor catalog does not link to the previous catalog digest", old=old_catalog, new=new_catalog, accepted_key=crisis.accepted_new_public_key, pressures=(new_catalog.previous_catalog_digest, old_catalog.catalog_digest))
    if new_catalog.sequence <= old_catalog.sequence:
        return _report(CatalogSuccessionDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "successor catalog did not advance the catalog sequence", old=old_catalog, new=new_catalog, accepted_key=crisis.accepted_new_public_key, pressures=(new_catalog.catalog_digest, old_catalog.catalog_digest))
    old_binding = (old_catalog.profile_digest, old_catalog.start_report_digest, old_catalog.router_report_digest, old_catalog.router_profile_digest, old_catalog.mode.value)
    new_binding = (new_catalog.profile_digest, new_catalog.start_report_digest, new_catalog.router_report_digest, new_catalog.router_profile_digest, new_catalog.mode.value)
    if old_binding != new_binding:
        return _report(CatalogSuccessionDecisionKind.QUARANTINE_BINDING_DRIFT, False, "successor catalog drifted away from the accepted start/router binding", old=old_catalog, new=new_catalog, accepted_key=crisis.accepted_new_public_key, pressures=old_binding[:4] + new_binding[:4])
    if require_no_service_downgrade and new_catalog.giving_service_count < old_catalog.giving_service_count:
        return _report(CatalogSuccessionDecisionKind.QUARANTINE_SERVICE_DOWNGRADE, False, "successor catalog drops giving services without an explicit withdrawal lane", old=old_catalog, new=new_catalog, accepted_key=crisis.accepted_new_public_key, pressures=(old_catalog.catalog_digest, new_catalog.catalog_digest))
    return _report(CatalogSuccessionDecisionKind.ACCEPT_CATALOG_SUCCESSION, True, "catalog succession accepted under key-crisis pressure", old=old_catalog, new=new_catalog, accepted_key=crisis.accepted_new_public_key)
