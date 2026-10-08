"""Signed withdrawal/retirement notices for garden service catalogs.

rev0037 treats an accepted service catalog as dangerous if it can never be
withdrawn.  Catalogs are intentionally short-lived, but "wait for expiry" is
not enough when a garden changes profile, loses keys, pauses a bridge, or wants
clients to stop sending protected work now.  This module models a tiny signed
withdrawal surface that is local evidence, not global truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule, ServiceCatalogReport

SERVICE_WITHDRAWAL_DOMAIN = DOMAIN + b":service-withdrawal-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceWithdrawalKind(str, Enum):
    RETIRE_CATALOG = "retire_catalog"
    SUSPEND_SERVICE = "suspend_service"
    SUCCESSOR_CATALOG = "successor_catalog"


class ServiceWithdrawalDecisionKind(str, Enum):
    ACCEPT_CATALOG_RETIRED = "accept_catalog_retired"
    ACCEPT_SERVICE_SUSPENDED = "accept_service_suspended"
    ACCEPT_SUCCESSOR_POINTER = "accept_successor_pointer"
    HOLD_CATALOG_REPORT = "hold_catalog_report"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_ISSUER_MISMATCH = "quarantine_issuer_mismatch"
    QUARANTINE_CATALOG_DIGEST_MISMATCH = "quarantine_catalog_digest_mismatch"
    QUARANTINE_UNKNOWN_SERVICE = "quarantine_unknown_service"
    QUARANTINE_SUCCESSOR_MISSING = "quarantine_successor_missing"


@dataclass(frozen=True)
class ServiceWithdrawalNotice:
    issuer_node_id: bytes
    issuer_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    catalog_digest: bytes
    kind: ServiceWithdrawalKind
    service: GardenServiceClass | None = None
    successor_catalog_digest: bytes = ZERO_DIGEST
    previous_notice_digest: bytes = ZERO_DIGEST
    reason_code: str = "operator_request"
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("issuer_node_id", self.issuer_node_id),
            ("issuer_public_key", self.issuer_public_key),
            ("catalog_digest", self.catalog_digest),
            ("successor_catalog_digest", self.successor_catalog_digest),
            ("previous_notice_digest", self.previous_notice_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("withdrawal sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("withdrawal expires_at must be after issued_at")
        if len(self.reason_code.encode("utf-8")) > 96:
            raise ValueError("withdrawal reason_code is too large")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        catalog: ServiceCatalogCapsule,
        sequence: int,
        issued_at: int,
        expires_at: int,
        kind: ServiceWithdrawalKind,
        service: GardenServiceClass | None = None,
        successor_catalog_digest: bytes = ZERO_DIGEST,
        previous_notice_digest: bytes = ZERO_DIGEST,
        reason_code: str = "operator_request",
    ) -> "ServiceWithdrawalNotice":
        unsigned = cls(
            issuer_node_id=catalog.issuer_node_id,
            issuer_public_key=keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            catalog_digest=catalog.catalog_digest,
            kind=kind,
            service=service,
            successor_catalog_digest=successor_catalog_digest,
            previous_notice_digest=previous_notice_digest,
            reason_code=reason_code,
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
            b"catalog_digest": self.catalog_digest,
            b"kind": self.kind.value,
            b"service": self.service.value if self.service is not None else "",
            b"successor_catalog_digest": self.successor_catalog_digest,
            b"previous_notice_digest": self.previous_notice_digest,
            b"reason_code": self.reason_code,
        })

    @property
    def notice_digest(self) -> bytes:
        return sha256(SERVICE_WITHDRAWAL_DOMAIN + b":notice:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ServiceWithdrawalReport:
    decision_kind: ServiceWithdrawalDecisionKind
    accept: bool
    reason: str
    catalog_digest: bytes
    notice_digest: bytes
    affected_services: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def active_withdrawal(self) -> bool:
        return self.accept and self.decision_kind in {
            ServiceWithdrawalDecisionKind.ACCEPT_CATALOG_RETIRED,
            ServiceWithdrawalDecisionKind.ACCEPT_SERVICE_SUSPENDED,
            ServiceWithdrawalDecisionKind.ACCEPT_SUCCESSOR_POINTER,
        }


def _report(kind: ServiceWithdrawalDecisionKind, accept: bool, reason: str, *, notice: ServiceWithdrawalNotice, affected: Iterable[str] = (), pressures: Iterable[bytes] = ()) -> ServiceWithdrawalReport:
    affected_t = tuple(sorted(set(affected)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(SERVICE_WITHDRAWAL_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"catalog": notice.catalog_digest,
        b"notice": notice.notice_digest,
        b"affected": list(affected_t),
        b"pressures": list(pressure_t),
    }))
    return ServiceWithdrawalReport(kind, accept, reason, notice.catalog_digest, notice.notice_digest, affected_t, pressure_t, digest)


def assess_service_withdrawal(
    notice: ServiceWithdrawalNotice,
    *,
    catalog: ServiceCatalogCapsule,
    catalog_report: ServiceCatalogReport,
    now: int,
    highest_seen_sequence: int | None = None,
    same_sequence_digest: bytes | None = None,
    previously_seen_notices: Iterable[bytes] = (),
) -> ServiceWithdrawalReport:
    """Classify a signed withdrawal before stale service state is used."""
    seen = set(previously_seen_notices)
    if notice.notice_digest in seen:
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_REPLAY, False, "withdrawal notice replayed", notice=notice, pressures=(notice.notice_digest,))
    if highest_seen_sequence is not None and notice.sequence < highest_seen_sequence:
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "withdrawal sequence rolled back", notice=notice, pressures=(notice.notice_digest,))
    if same_sequence_digest is not None and notice.sequence == highest_seen_sequence and notice.notice_digest != same_sequence_digest:
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence withdrawal fork", notice=notice, pressures=(notice.notice_digest, same_sequence_digest))
    if now < notice.issued_at or now >= notice.expires_at:
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "withdrawal notice is not live in this clock window", notice=notice, pressures=(notice.notice_digest,))
    if not notice.verify():
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "withdrawal signature did not verify", notice=notice, pressures=(notice.notice_digest,))
    if not catalog_report.accept or catalog_report.quarantined:
        return _report(ServiceWithdrawalDecisionKind.HOLD_CATALOG_REPORT, False, "withdrawal needs an accepted catalog report for local binding", notice=notice, pressures=(catalog_report.report_digest,))
    if notice.catalog_digest != catalog.catalog_digest or catalog_report.catalog_digest != catalog.catalog_digest:
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_CATALOG_DIGEST_MISMATCH, False, "withdrawal/catalog/report digests do not match", notice=notice, pressures=(notice.catalog_digest, catalog.catalog_digest, catalog_report.catalog_digest))
    if notice.issuer_node_id != catalog.issuer_node_id or notice.issuer_public_key != catalog.issuer_public_key:
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_ISSUER_MISMATCH, False, "withdrawal issuer does not match catalog issuer", notice=notice, pressures=(notice.notice_digest, catalog.catalog_digest))
    if notice.kind is ServiceWithdrawalKind.RETIRE_CATALOG:
        return _report(ServiceWithdrawalDecisionKind.ACCEPT_CATALOG_RETIRED, True, "catalog retirement accepted as local negative evidence", notice=notice, affected=tuple(service.value for service in catalog.service_classes))
    if notice.kind is ServiceWithdrawalKind.SUSPEND_SERVICE:
        if notice.service is None or notice.service not in catalog.service_classes:
            return _report(ServiceWithdrawalDecisionKind.QUARANTINE_UNKNOWN_SERVICE, False, "service suspension does not name an advertised service", notice=notice, pressures=(notice.notice_digest, catalog.catalog_digest))
        return _report(ServiceWithdrawalDecisionKind.ACCEPT_SERVICE_SUSPENDED, True, "single service suspension accepted as local negative evidence", notice=notice, affected=(notice.service.value,))
    if notice.successor_catalog_digest == ZERO_DIGEST or notice.successor_catalog_digest == catalog.catalog_digest:
        return _report(ServiceWithdrawalDecisionKind.QUARANTINE_SUCCESSOR_MISSING, False, "successor withdrawal needs a distinct successor catalog digest", notice=notice, pressures=(notice.notice_digest,))
    return _report(ServiceWithdrawalDecisionKind.ACCEPT_SUCCESSOR_POINTER, True, "successor catalog pointer accepted as local transition evidence", notice=notice, affected=tuple(service.value for service in catalog.service_classes), pressures=(notice.successor_catalog_digest,))
