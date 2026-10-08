"""Redacted service announcements for garden catalogs.

A catalog is local capacity truth for one node.  An announcement is the smaller,
redacted surface a garden is willing to gossip: a subset of services, a
visibility class, and only bounded hint counts.  Public announcements must not
accidentally expose private services or bridge gateways.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .launchquorum import LaunchMode
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule, ServiceCatalogReport
from .startmatrix import StartProfile

SERVICE_ANNOUNCE_DOMAIN = DOMAIN + b":service-announce-v1:"
ZERO_DIGEST = b"\x00" * 32


class AnnouncementVisibility(str, Enum):
    PUBLIC = "public"
    FRIEND = "friend"
    INVITE = "invite"


class ServiceAnnouncementDecisionKind(str, Enum):
    ACCEPT_PUBLIC_ANNOUNCEMENT = "accept_public_announcement"
    ACCEPT_PRIVATE_ANNOUNCEMENT = "accept_private_announcement"
    HOLD_METADATA_OVEREXPOSURE = "hold_metadata_overexposure"
    QUARANTINE_CATALOG_REPORT = "quarantine_catalog_report"
    QUARANTINE_BINDING_MISMATCH = "quarantine_binding_mismatch"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_TTL_EXCESS = "quarantine_ttl_excess"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_UNKNOWN_SERVICE = "quarantine_unknown_service"
    QUARANTINE_PUBLIC_HIDDEN_SERVICE = "quarantine_public_hidden_service"
    QUARANTINE_PUBLIC_BRIDGE_EXPOSURE = "quarantine_public_bridge_exposure"


@dataclass(frozen=True)
class AnnouncementPolicy:
    allow_public_bridge: bool = False
    max_ttl: int = 1_800
    max_hint_count: int = 32
    max_label_hashes: int = 8


@dataclass(frozen=True)
class ServiceAnnouncementCapsule:
    issuer_node_id: bytes
    issuer_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    visibility: AnnouncementVisibility
    catalog_digest: bytes
    catalog_report_digest: bytes
    profile_digest: bytes
    mode: LaunchMode
    services: tuple[GardenServiceClass, ...]
    label_hashes: tuple[bytes, ...] = ()
    hint_count: int = 0
    previous_announcement_digest: bytes = ZERO_DIGEST
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("issuer_node_id", self.issuer_node_id),
            ("issuer_public_key", self.issuer_public_key),
            ("catalog_digest", self.catalog_digest),
            ("catalog_report_digest", self.catalog_report_digest),
            ("profile_digest", self.profile_digest),
            ("previous_announcement_digest", self.previous_announcement_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        for label in self.label_hashes:
            if len(label) != 32:
                raise ValueError("label hashes must be 32 bytes")
        if self.sequence < 0 or self.hint_count < 0:
            raise ValueError("announcement sequence/hints must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("announcement expires_at must be after issued_at")
        if len(set(self.services)) != len(self.services):
            raise ValueError("announcement services must be unique")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        issuer_node_id: bytes,
        sequence: int,
        issued_at: int,
        expires_at: int,
        visibility: AnnouncementVisibility,
        catalog: ServiceCatalogCapsule,
        catalog_report: ServiceCatalogReport,
        profile: StartProfile,
        services: Iterable[GardenServiceClass],
        label_hashes: Iterable[bytes] = (),
        hint_count: int = 0,
        previous_announcement_digest: bytes = ZERO_DIGEST,
    ) -> "ServiceAnnouncementCapsule":
        unsigned = cls(
            issuer_node_id=issuer_node_id,
            issuer_public_key=keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            visibility=visibility,
            catalog_digest=catalog.catalog_digest,
            catalog_report_digest=catalog_report.report_digest,
            profile_digest=profile.profile_digest,
            mode=profile.mode,
            services=tuple(services),
            label_hashes=tuple(label_hashes),
            hint_count=hint_count,
            previous_announcement_digest=previous_announcement_digest,
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
            b"visibility": self.visibility.value,
            b"catalog_digest": self.catalog_digest,
            b"catalog_report_digest": self.catalog_report_digest,
            b"profile_digest": self.profile_digest,
            b"mode": self.mode.value,
            b"services": [service.value for service in self.services],
            b"label_hashes": list(self.label_hashes),
            b"hint_count": self.hint_count,
            b"previous_announcement_digest": self.previous_announcement_digest,
        })

    @property
    def announcement_digest(self) -> bytes:
        return sha256(SERVICE_ANNOUNCE_DOMAIN + b":announcement:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)

    def bvalue(self) -> dict[bytes, BValue]:
        return {b"announcement": self.announcement_digest, b"visibility": self.visibility.value}


@dataclass(frozen=True)
class ServiceAnnouncementReport:
    decision_kind: ServiceAnnouncementDecisionKind
    accept: bool
    reason: str
    announcement_digest: bytes
    catalog_digest: bytes
    visible_services: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceAnnouncementDecisionKind, accept: bool, reason: str, *, announcement: ServiceAnnouncementCapsule, pressures: Iterable[bytes] = ()) -> ServiceAnnouncementReport:
    pressure_t = tuple(sorted(set(pressures)))
    visible = tuple(sorted(service.value for service in announcement.services)) if accept else ()
    digest = sha256(SERVICE_ANNOUNCE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"announcement": announcement.announcement_digest,
        b"catalog": announcement.catalog_digest,
        b"visible": list(visible),
        b"pressures": list(pressure_t),
    }))
    return ServiceAnnouncementReport(kind, accept, reason, announcement.announcement_digest, announcement.catalog_digest, visible, pressure_t, digest)


def assess_service_announcement(
    announcement: ServiceAnnouncementCapsule,
    *,
    catalog: ServiceCatalogCapsule,
    catalog_report: ServiceCatalogReport,
    profile: StartProfile,
    now: int,
    policy: AnnouncementPolicy = AnnouncementPolicy(),
    highest_seen_sequence: int | None = None,
    same_sequence_digest: bytes | None = None,
    previously_seen_announcements: Iterable[bytes] = (),
) -> ServiceAnnouncementReport:
    if announcement.announcement_digest in set(previously_seen_announcements):
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_REPLAY, False, "service announcement replayed", announcement=announcement, pressures=(announcement.announcement_digest,))
    if highest_seen_sequence is not None and announcement.sequence < highest_seen_sequence:
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "service announcement sequence rollback", announcement=announcement, pressures=(announcement.announcement_digest,))
    if same_sequence_digest is not None and announcement.sequence == highest_seen_sequence and announcement.announcement_digest != same_sequence_digest:
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence service announcement fork", announcement=announcement, pressures=(announcement.announcement_digest, same_sequence_digest))
    if now < announcement.issued_at or now >= announcement.expires_at:
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "announcement is not live in this local clock window", announcement=announcement, pressures=(announcement.announcement_digest,))
    if announcement.expires_at - announcement.issued_at > policy.max_ttl:
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_TTL_EXCESS, False, "announcement TTL exceeds local policy", announcement=announcement, pressures=(announcement.announcement_digest,))
    if not announcement.verify():
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "service announcement signature did not verify", announcement=announcement, pressures=(announcement.announcement_digest,))
    if not catalog_report.accept or catalog_report.quarantined:
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_CATALOG_REPORT, False, "announcement requires accepted service catalog report", announcement=announcement, pressures=(catalog_report.report_digest,))
    if announcement.catalog_digest != catalog.catalog_digest or announcement.catalog_report_digest != catalog_report.report_digest or announcement.profile_digest != profile.profile_digest or announcement.mode is not profile.mode:
        return _report(ServiceAnnouncementDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "announcement/catalog/profile binding drift", announcement=announcement, pressures=(announcement.catalog_digest, catalog.catalog_digest, announcement.profile_digest, profile.profile_digest))
    if announcement.hint_count > policy.max_hint_count or len(announcement.label_hashes) > policy.max_label_hashes:
        return _report(ServiceAnnouncementDecisionKind.HOLD_METADATA_OVEREXPOSURE, False, "announcement leaks too many hints for local policy", announcement=announcement, pressures=(announcement.announcement_digest,))
    catalog_by_service = {descriptor.service: descriptor for descriptor in catalog.services}
    for service in announcement.services:
        if service not in catalog_by_service or service.value not in catalog_report.accepted_services:
            return _report(ServiceAnnouncementDecisionKind.QUARANTINE_UNKNOWN_SERVICE, False, "announcement exposes a service not accepted by catalog", announcement=announcement, pressures=(announcement.announcement_digest, catalog.catalog_digest))
        if announcement.visibility is AnnouncementVisibility.PUBLIC and not catalog_by_service[service].public:
            return _report(ServiceAnnouncementDecisionKind.QUARANTINE_PUBLIC_HIDDEN_SERVICE, False, "public announcement exposes a non-public service", announcement=announcement, pressures=(announcement.announcement_digest, catalog.catalog_digest))
        if announcement.visibility is AnnouncementVisibility.PUBLIC and service is GardenServiceClass.BRIDGE_GATEWAY and not policy.allow_public_bridge:
            return _report(ServiceAnnouncementDecisionKind.QUARANTINE_PUBLIC_BRIDGE_EXPOSURE, False, "public bridge exposure requires explicit local policy", announcement=announcement, pressures=(announcement.announcement_digest, catalog.catalog_digest))
    kind = ServiceAnnouncementDecisionKind.ACCEPT_PUBLIC_ANNOUNCEMENT if announcement.visibility is AnnouncementVisibility.PUBLIC else ServiceAnnouncementDecisionKind.ACCEPT_PRIVATE_ANNOUNCEMENT
    return _report(kind, True, "service announcement accepted as redacted local discovery surface", announcement=announcement)
