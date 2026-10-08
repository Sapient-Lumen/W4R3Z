"""rev0101 routing-table storage after I2P routing anchor acceptance.

A routing anchor says a contact lease looked locally valid.  This module decides
whether that contact may enter a local routing bucket, replacement cache, or
stale-eviction plan without treating a garden/introducer as authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

ROUTE_STORAGE_DOMAIN = DOMAIN + b":route-storage-v1:"
ALLOWED_BUCKET_PURPOSES = {"bootstrap", "lookup", "provider", "garden"}


class RouteStorageDecisionKind(str, Enum):
    ACCEPT_ROUTE_STORAGE = "accept_route_storage"
    HOLD_REPLACEMENT_CACHE = "hold_replacement_cache"
    HOLD_STALE_EVICTION_PROBE = "hold_stale_eviction_probe"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_BUCKET_OR_LEASE = "quarantine_bucket_or_lease"
    QUARANTINE_AUTHORITY_OR_RAW_ENDPOINT = "quarantine_authority_or_raw_endpoint"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class RouteStorageCapsule:
    component: str
    profile: str
    bucket_id: str
    bucket_purpose: str
    request_id: str
    sequence: int
    previous_digest: bytes
    routing_anchor_digest: bytes
    destination_digest: bytes
    node_id_digest: bytes
    bucket_region_digest: bytes
    lease_expires_at: int
    now: int
    bucket_size: int
    bucket_capacity: int
    replacement_cache_size: int
    replacement_cache_capacity: int
    stale_contact_digest: bytes
    stale_contact_probe_required: bool
    destination_bound_node_id: bool
    endpoint_is_i2p_destination: bool
    raw_ip_endpoint_present: bool
    garden_or_introducer_claims_authority: bool
    preserve_route_gossip_memory: bool
    preserve_contact_lease_memory: bool
    preserve_stale_contact_memory: bool
    preserve_witness_memory: bool
    contact_family_id: str
    introducer_family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(ROUTE_STORAGE_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"bucket": self.bucket_id,
            b"purpose": self.bucket_purpose,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"anchor": self.routing_anchor_digest,
            b"destination": self.destination_digest,
            b"node_id": self.node_id_digest,
            b"region": self.bucket_region_digest,
            b"expires": self.lease_expires_at,
            b"now": self.now,
            b"bucket_size": self.bucket_size,
            b"bucket_capacity": self.bucket_capacity,
            b"replacement_size": self.replacement_cache_size,
            b"replacement_capacity": self.replacement_cache_capacity,
            b"stale_contact": self.stale_contact_digest,
            b"stale_probe": 1 if self.stale_contact_probe_required else 0,
            b"bound_node": 1 if self.destination_bound_node_id else 0,
            b"i2p_destination": 1 if self.endpoint_is_i2p_destination else 0,
            b"raw_ip": 1 if self.raw_ip_endpoint_present else 0,
            b"authority_claim": 1 if self.garden_or_introducer_claims_authority else 0,
            b"preserve_gossip": 1 if self.preserve_route_gossip_memory else 0,
            b"preserve_lease": 1 if self.preserve_contact_lease_memory else 0,
            b"preserve_stale": 1 if self.preserve_stale_contact_memory else 0,
            b"preserve_witness": 1 if self.preserve_witness_memory else 0,
            b"contact_family": self.contact_family_id,
            b"introducer_family": self.introducer_family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class RouteStorageReport:
    decision_kind: RouteStorageDecisionKind
    accepted: bool
    route_stored: bool
    replacement_cached: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    routing_anchor_digest: bytes
    destination_digest: bytes
    node_id_digest: bytes
    contact_family_count: int
    introducer_family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(ROUTE_STORAGE_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"stored": 1 if self.route_stored else 0,
            b"replacement": 1 if self.replacement_cached else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"anchor": self.routing_anchor_digest,
            b"destination": self.destination_digest,
            b"node_id": self.node_id_digest,
            b"contact_families": self.contact_family_count,
            b"introducer_families": self.introducer_family_count,
            b"path_families": self.path_family_count,
        }))


def assess_route_storage(
    routing_anchor: object,
    capsule: RouteStorageCapsule,
    *,
    previous: RouteStorageCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_contact_families: tuple[str, ...] = (),
    observed_introducer_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_contact_families: int = 2,
    min_introducer_families: int = 2,
    min_path_families: int = 2,
) -> RouteStorageReport:
    contact_families = set(observed_contact_families or (capsule.contact_family_id,))
    introducer_families = set(observed_introducer_families or (capsule.introducer_family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: RouteStorageDecisionKind, accepted: bool, replacement: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> RouteStorageReport:
        return RouteStorageReport(
            kind, accepted, accepted and not replacement, replacement, quarantine, watch, obligations,
            capsule.capsule_digest, capsule.routing_anchor_digest, capsule.destination_digest,
            capsule.node_id_digest, len(contact_families), len(introducer_families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(RouteStorageDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("route-storage-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(RouteStorageDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, ("route-storage-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(RouteStorageDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, ("route-storage-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(RouteStorageDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, ("route-storage-previous-link-mismatch",))
    if len(contact_families) < min_contact_families or len(path_families) < min_path_families:
        return report(RouteStorageDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("route-storage-low-diversity",))
    if len(introducer_families) < min_introducer_families:
        return report(RouteStorageDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, ("route-storage-introducer-monoculture",))
    if not getattr(routing_anchor, "accepted", False) or not getattr(routing_anchor, "route_anchor_accepted", False):
        return report(RouteStorageDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, False, True, ("routing-anchor-not-ready",))
    if capsule.routing_anchor_digest != getattr(routing_anchor, "report_digest", b""):
        return report(RouteStorageDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, ("route-storage-anchor-digest-drift",))
    if capsule.bucket_purpose not in ALLOWED_BUCKET_PURPOSES or capsule.lease_expires_at <= capsule.now or len(capsule.bucket_region_digest) != 32:
        return report(RouteStorageDecisionKind.QUARANTINE_BUCKET_OR_LEASE, False, False, True, False, ("route-storage-bucket-or-lease-drift",))
    if not capsule.destination_bound_node_id or not capsule.endpoint_is_i2p_destination or capsule.raw_ip_endpoint_present or capsule.garden_or_introducer_claims_authority:
        return report(RouteStorageDecisionKind.QUARANTINE_AUTHORITY_OR_RAW_ENDPOINT, False, False, True, False, ("route-storage-authority-or-raw-endpoint",))
    if not all((capsule.preserve_route_gossip_memory, capsule.preserve_contact_lease_memory, capsule.preserve_stale_contact_memory, capsule.preserve_witness_memory)):
        return report(RouteStorageDecisionKind.QUARANTINE_MEMORY_DROP, False, False, True, False, ("route-storage-memory-drop",))
    if capsule.bucket_size >= capsule.bucket_capacity:
        if capsule.stale_contact_probe_required:
            return report(RouteStorageDecisionKind.HOLD_STALE_EVICTION_PROBE, False, False, False, True, ("route-storage-stale-eviction-probe",))
        if capsule.replacement_cache_size < capsule.replacement_cache_capacity:
            return report(RouteStorageDecisionKind.HOLD_REPLACEMENT_CACHE, True, True, False, True, ("route-storage-replacement-cache",))
        return report(RouteStorageDecisionKind.QUARANTINE_BUCKET_OR_LEASE, False, False, True, False, ("route-storage-bucket-and-replacement-full",))
    return report(RouteStorageDecisionKind.ACCEPT_ROUTE_STORAGE, True, False, False, False, ())
