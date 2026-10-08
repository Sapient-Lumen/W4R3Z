"""rev0100 routing-anchor gate for I2P DHT contacts.

A routing/contact record is not useful just because it parsed and was signed.
It must bind an I2P destination, node id, lease, route attestation, and
introducer/path diversity without leaking back to raw-IP or native transport
assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256

ROUTING_ANCHOR_DOMAIN = DOMAIN + b":routing-anchor-v1:"
ALLOWED_PURPOSES = {"bootstrap", "find_node", "provider_announce", "garden_seed", "route_repair"}


class RoutingAnchorDecisionKind(str, Enum):
    ACCEPT_ROUTING_ANCHOR = "accept_routing_anchor"
    HOLD_COMPONENT_NOT_READY = "hold_component_not_ready"
    QUARANTINE_NOT_ROUTING_INGRESS = "quarantine_not_routing_ingress"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_DESTINATION_OR_NODE_DRIFT = "quarantine_destination_or_node_drift"
    QUARANTINE_EXPIRED_OR_PURPOSE_DRIFT = "quarantine_expired_or_purpose_drift"
    QUARANTINE_RAW_IP_OR_NATIVE_TRANSPORT = "quarantine_raw_ip_or_native_transport"
    QUARANTINE_INTRODUCER_MONOCULTURE = "quarantine_introducer_monoculture"
    QUARANTINE_MEMORY_DROP = "quarantine_memory_drop"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class RoutingAnchorCapsule:
    component: str
    profile: str
    purpose: str
    request_id: str
    sequence: int
    previous_digest: bytes
    record_ingress_digest: bytes
    contact_lease_digest: bytes
    route_attestation_digest: bytes
    destination_digest: bytes
    node_id_digest: bytes
    expected_node_id_digest: bytes
    lease_expires_at: int
    now: int
    signed_contact_lease: bool
    signed_route_attestation: bool
    route_gossip_bound: bool
    endpoint_is_i2p_destination: bool
    raw_ip_endpoint_present: bool
    native_transport_attempted: bool
    preserve_contact_lease_memory: bool
    preserve_route_gossip_memory: bool
    preserve_tombstone_memory: bool
    preserve_witness_memory: bool
    contact_family_id: str
    introducer_family_id: str
    path_family_id: str
    note: str = ""

    @property
    def capsule_digest(self) -> bytes:
        return sha256(ROUTING_ANCHOR_DOMAIN + b":capsule:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"purpose": self.purpose,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"ingress": self.record_ingress_digest,
            b"lease": self.contact_lease_digest,
            b"attestation": self.route_attestation_digest,
            b"destination": self.destination_digest,
            b"node_id": self.node_id_digest,
            b"expected_node_id": self.expected_node_id_digest,
            b"expires": self.lease_expires_at,
            b"now": self.now,
            b"signed_lease": 1 if self.signed_contact_lease else 0,
            b"signed_attestation": 1 if self.signed_route_attestation else 0,
            b"gossip_bound": 1 if self.route_gossip_bound else 0,
            b"i2p_destination": 1 if self.endpoint_is_i2p_destination else 0,
            b"raw_ip": 1 if self.raw_ip_endpoint_present else 0,
            b"native_transport": 1 if self.native_transport_attempted else 0,
            b"preserve_lease": 1 if self.preserve_contact_lease_memory else 0,
            b"preserve_gossip": 1 if self.preserve_route_gossip_memory else 0,
            b"preserve_tombstone": 1 if self.preserve_tombstone_memory else 0,
            b"preserve_witness": 1 if self.preserve_witness_memory else 0,
            b"contact_family": self.contact_family_id,
            b"introducer_family": self.introducer_family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class RoutingAnchorReport:
    decision_kind: RoutingAnchorDecisionKind
    accepted: bool
    route_anchor_accepted: bool
    quarantine: bool
    watch: bool
    obligations: tuple[str, ...]
    capsule_digest: bytes
    record_ingress_digest: bytes
    destination_digest: bytes
    node_id_digest: bytes
    contact_family_count: int
    introducer_family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(ROUTING_ANCHOR_DOMAIN + b":report:" + bencode({
            b"decision": self.decision_kind.value,
            b"accepted": 1 if self.accepted else 0,
            b"route_anchor": 1 if self.route_anchor_accepted else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"watch": 1 if self.watch else 0,
            b"obligations": list(self.obligations),
            b"capsule": self.capsule_digest,
            b"ingress": self.record_ingress_digest,
            b"destination": self.destination_digest,
            b"node_id": self.node_id_digest,
            b"contact_families": self.contact_family_count,
            b"introducer_families": self.introducer_family_count,
            b"path_families": self.path_family_count,
        }))


def assess_routing_anchor(
    record_ingress: object,
    contact_lease: object,
    route_attestation: object,
    capsule: RoutingAnchorCapsule,
    *,
    previous: RoutingAnchorCapsule | None = None,
    prior_capsule_digests: tuple[bytes, ...] = (),
    observed_contact_families: tuple[str, ...] = (),
    observed_introducer_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_contact_families: int = 2,
    min_introducer_families: int = 2,
    min_path_families: int = 2,
) -> RoutingAnchorReport:
    contact_families = set(observed_contact_families or (capsule.contact_family_id,))
    introducer_families = set(observed_introducer_families or (capsule.introducer_family_id,))
    path_families = set(observed_path_families or (capsule.path_family_id,))

    def report(kind: RoutingAnchorDecisionKind, accepted: bool, quarantine: bool, watch: bool, obligations: tuple[str, ...]) -> RoutingAnchorReport:
        return RoutingAnchorReport(
            kind, accepted, accepted, quarantine, watch, obligations, capsule.capsule_digest,
            capsule.record_ingress_digest, capsule.destination_digest, capsule.node_id_digest,
            len(contact_families), len(introducer_families), len(path_families)
        )

    if capsule.capsule_digest in prior_capsule_digests:
        return report(RoutingAnchorDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("routing-anchor-replay",))
    if previous is not None:
        if capsule.sequence < previous.sequence:
            return report(RoutingAnchorDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, True, False, ("routing-anchor-rollback",))
        if capsule.sequence == previous.sequence and capsule.capsule_digest != previous.capsule_digest:
            return report(RoutingAnchorDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, True, False, ("routing-anchor-same-sequence-fork",))
        if capsule.sequence > previous.sequence and capsule.previous_digest != previous.capsule_digest:
            return report(RoutingAnchorDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, True, False, ("routing-anchor-prev-link",))
    if len(contact_families) < min_contact_families or len(path_families) < min_path_families:
        return report(RoutingAnchorDecisionKind.QUARANTINE_LOW_DIVERSITY, False, True, False, ("routing-anchor-low-diversity",))
    if len(introducer_families) < min_introducer_families:
        return report(RoutingAnchorDecisionKind.QUARANTINE_INTRODUCER_MONOCULTURE, False, True, False, ("routing-anchor-introducer-monoculture",))
    if not getattr(record_ingress, "accepted", False) or not getattr(record_ingress, "record_admitted", False):
        return report(RoutingAnchorDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("routing-ingress-not-ready",))
    if getattr(record_ingress, "record_kind", "") not in {"routing", "garden_seed"}:
        return report(RoutingAnchorDecisionKind.QUARANTINE_NOT_ROUTING_INGRESS, False, True, False, ("not-routing-ingress",))
    if not getattr(contact_lease, "accepted", False) or not getattr(route_attestation, "accepted", False):
        return report(RoutingAnchorDecisionKind.HOLD_COMPONENT_NOT_READY, False, False, True, ("route-components-not-ready",))
    if capsule.record_ingress_digest != getattr(record_ingress, "report_digest", b"") or capsule.contact_lease_digest != getattr(contact_lease, "report_digest", b"") or capsule.route_attestation_digest != getattr(route_attestation, "report_digest", b""):
        return report(RoutingAnchorDecisionKind.QUARANTINE_DIGEST_DRIFT, False, True, False, ("routing-anchor-component-digest-drift",))
    if capsule.node_id_digest != capsule.expected_node_id_digest or len(capsule.destination_digest) != 32 or len(capsule.node_id_digest) != 32:
        return report(RoutingAnchorDecisionKind.QUARANTINE_DESTINATION_OR_NODE_DRIFT, False, True, False, ("routing-anchor-node-or-destination-drift",))
    if capsule.purpose not in ALLOWED_PURPOSES or capsule.lease_expires_at <= capsule.now or not capsule.signed_contact_lease or not capsule.signed_route_attestation or not capsule.route_gossip_bound:
        return report(RoutingAnchorDecisionKind.QUARANTINE_EXPIRED_OR_PURPOSE_DRIFT, False, True, False, ("routing-anchor-expired-or-purpose-drift",))
    if not capsule.endpoint_is_i2p_destination or capsule.raw_ip_endpoint_present or capsule.native_transport_attempted:
        return report(RoutingAnchorDecisionKind.QUARANTINE_RAW_IP_OR_NATIVE_TRANSPORT, False, True, False, ("routing-anchor-raw-ip-or-native-transport",))
    if not all((capsule.preserve_contact_lease_memory, capsule.preserve_route_gossip_memory, capsule.preserve_tombstone_memory, capsule.preserve_witness_memory)):
        return report(RoutingAnchorDecisionKind.QUARANTINE_MEMORY_DROP, False, True, False, ("routing-anchor-memory-drop",))
    return report(RoutingAnchorDecisionKind.ACCEPT_ROUTING_ANCHOR, True, False, False, ())
