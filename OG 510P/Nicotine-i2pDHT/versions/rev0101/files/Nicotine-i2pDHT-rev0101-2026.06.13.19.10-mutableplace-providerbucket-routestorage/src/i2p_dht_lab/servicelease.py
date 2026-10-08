"""Service leases after joined garden-service continuity.

rev0039 adds the next boundary after service-continuity acceptance.  A garden
may have a catalog, announcement, ingress report, ticket, receipt, use-gate, and
continuity report that all look locally valid, but ongoing service still needs a
short-lived lease before repeated side effects are allowed.  The lease binds the
caller, service, scope, object, request, catalog, and continuity report to a
sequence/previous-link memory lane.  It is not currency and not reputation; it is
one local permission to continue spending a bounded garden-service budget.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .servicecatalog import GardenServiceClass
from .servicecontinuity import ServiceContinuityReport

SERVICE_LEASE_DOMAIN = DOMAIN + b":service-lease-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceLeaseDecisionKind(str, Enum):
    ACCEPT_SERVICE_LEASE = "accept_service_lease"
    ACCEPT_RENEWED_SERVICE_LEASE = "accept_renewed_service_lease"
    HOLD_CONTINUITY_NOT_ACCEPTED = "hold_continuity_not_accepted"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_SEQUENCE_ROLLBACK = "quarantine_sequence_rollback"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_PREVIOUS_LINK = "quarantine_previous_link"
    QUARANTINE_BINDING_MISMATCH = "quarantine_binding_mismatch"
    QUARANTINE_BUDGET_OVERCLAIM = "quarantine_budget_overclaim"
    QUARANTINE_CALLER_MISMATCH = "quarantine_caller_mismatch"


@dataclass(frozen=True)
class ServiceLeaseCapsule:
    issuer_node_id: bytes
    issuer_public_key: bytes
    sequence: int
    issued_at: int
    expires_at: int
    continuity_report_digest: bytes
    catalog_digest: bytes
    service: GardenServiceClass
    caller_node_id: bytes
    scope_digest: bytes
    object_digest: bytes
    request_digest: bytes
    granted_units: int
    granted_streams: int
    raw_key_budget: int
    previous_lease_digest: bytes = ZERO_DIGEST
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("issuer_node_id", self.issuer_node_id),
            ("issuer_public_key", self.issuer_public_key),
            ("continuity_report_digest", self.continuity_report_digest),
            ("catalog_digest", self.catalog_digest),
            ("caller_node_id", self.caller_node_id),
            ("scope_digest", self.scope_digest),
            ("object_digest", self.object_digest),
            ("request_digest", self.request_digest),
            ("previous_lease_digest", self.previous_lease_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if self.sequence < 0:
            raise ValueError("service lease sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("service lease expires_at must be after issued_at")
        if self.granted_units < 0 or self.granted_streams < 0 or self.raw_key_budget < 0:
            raise ValueError("service lease budgets must be non-negative")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        issuer_node_id: bytes,
        sequence: int,
        issued_at: int,
        expires_at: int,
        continuity: ServiceContinuityReport,
        service: GardenServiceClass,
        caller_node_id: bytes,
        object_digest: bytes,
        granted_units: int,
        granted_streams: int,
        raw_key_budget: int,
        previous_lease_digest: bytes = ZERO_DIGEST,
    ) -> "ServiceLeaseCapsule":
        unsigned = cls(
            issuer_node_id=issuer_node_id,
            issuer_public_key=keypair.public_key_bytes,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            continuity_report_digest=continuity.report_digest,
            catalog_digest=continuity.catalog_digest or ZERO_DIGEST,
            service=service,
            caller_node_id=caller_node_id,
            scope_digest=continuity.scope_digest or ZERO_DIGEST,
            object_digest=object_digest,
            request_digest=continuity.request_digest or ZERO_DIGEST,
            granted_units=granted_units,
            granted_streams=granted_streams,
            raw_key_budget=raw_key_budget,
            previous_lease_digest=previous_lease_digest,
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
            b"continuity_report_digest": self.continuity_report_digest,
            b"catalog_digest": self.catalog_digest,
            b"service": self.service.value,
            b"caller_node_id": self.caller_node_id,
            b"scope_digest": self.scope_digest,
            b"object_digest": self.object_digest,
            b"request_digest": self.request_digest,
            b"granted_units": self.granted_units,
            b"granted_streams": self.granted_streams,
            b"raw_key_budget": self.raw_key_budget,
            b"previous_lease_digest": self.previous_lease_digest,
        })

    @property
    def lease_digest(self) -> bytes:
        return sha256(SERVICE_LEASE_DOMAIN + b":lease:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.issuer_public_key, self.unsigned_payload(), self.signature)

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"issuer_node_id": self.issuer_node_id,
            b"issuer_public_key": self.issuer_public_key,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"continuity_report_digest": self.continuity_report_digest,
            b"catalog_digest": self.catalog_digest,
            b"service": self.service.value,
            b"caller_node_id": self.caller_node_id,
            b"scope_digest": self.scope_digest,
            b"object_digest": self.object_digest,
            b"request_digest": self.request_digest,
            b"granted_units": self.granted_units,
            b"granted_streams": self.granted_streams,
            b"raw_key_budget": self.raw_key_budget,
            b"previous_lease_digest": self.previous_lease_digest,
        }


@dataclass(frozen=True)
class ServiceLeaseReport:
    decision_kind: ServiceLeaseDecisionKind
    accept: bool
    reason: str
    lease_digest: bytes
    continuity_report_digest: bytes
    catalog_digest: bytes
    caller_node_id: bytes
    scope_digest: bytes
    object_digest: bytes
    request_digest: bytes
    service: GardenServiceClass
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


@dataclass(frozen=True)
class ServiceLeasePolicy:
    max_units: int
    max_streams: int
    max_raw_key_budget: int
    max_clock_skew: int = 120

    def __post_init__(self) -> None:
        if self.max_units < 0 or self.max_streams < 0 or self.max_raw_key_budget < 0 or self.max_clock_skew < 0:
            raise ValueError("lease policy budgets must be non-negative")


def _report(
    kind: ServiceLeaseDecisionKind,
    accept: bool,
    reason: str,
    *,
    lease: ServiceLeaseCapsule,
    pressures: Iterable[bytes] = (),
) -> ServiceLeaseReport:
    pressure_tuple = tuple(sorted(set(pressures)))
    digest = sha256(SERVICE_LEASE_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"lease": lease.lease_digest,
        b"continuity": lease.continuity_report_digest,
        b"catalog": lease.catalog_digest,
        b"caller": lease.caller_node_id,
        b"scope": lease.scope_digest,
        b"object": lease.object_digest,
        b"request": lease.request_digest,
        b"service": lease.service.value,
        b"pressures": list(pressure_tuple),
    }))
    return ServiceLeaseReport(
        kind,
        accept,
        reason,
        lease.lease_digest,
        lease.continuity_report_digest,
        lease.catalog_digest,
        lease.caller_node_id,
        lease.scope_digest,
        lease.object_digest,
        lease.request_digest,
        lease.service,
        pressure_tuple,
        digest,
    )


def assess_service_lease(
    lease: ServiceLeaseCapsule,
    *,
    continuity: ServiceContinuityReport,
    policy: ServiceLeasePolicy,
    now: int,
    expected_caller_node_id: bytes | None = None,
    expected_object_digest: bytes | None = None,
    expected_service: GardenServiceClass | None = None,
    previous_lease: ServiceLeaseCapsule | None = None,
    previously_seen_leases: Iterable[bytes] = (),
) -> ServiceLeaseReport:
    """Assess whether an ongoing-service lease may advance local side effects."""
    if not continuity.accept or continuity.quarantined:
        return _report(ServiceLeaseDecisionKind.HOLD_CONTINUITY_NOT_ACCEPTED, False, "continuity report did not accept", lease=lease, pressures=(continuity.report_digest,))
    if not lease.verify():
        return _report(ServiceLeaseDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "service lease signature failed", lease=lease)
    if lease.issued_at > now + policy.max_clock_skew or lease.expires_at < now:
        return _report(ServiceLeaseDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "service lease is expired or too far in the future", lease=lease)
    if lease.lease_digest in set(previously_seen_leases):
        return _report(ServiceLeaseDecisionKind.QUARANTINE_REPLAY, False, "service lease was replayed", lease=lease, pressures=(lease.lease_digest,))
    if lease.continuity_report_digest != continuity.report_digest:
        return _report(ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "continuity digest drift", lease=lease, pressures=(continuity.report_digest,))
    if lease.catalog_digest != (continuity.catalog_digest or ZERO_DIGEST) or lease.scope_digest != (continuity.scope_digest or ZERO_DIGEST) or lease.request_digest != (continuity.request_digest or ZERO_DIGEST):
        return _report(ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "catalog/scope/request binding drift", lease=lease, pressures=(continuity.report_digest,))
    if expected_caller_node_id is not None and lease.caller_node_id != expected_caller_node_id:
        return _report(ServiceLeaseDecisionKind.QUARANTINE_CALLER_MISMATCH, False, "caller binding mismatch", lease=lease, pressures=(expected_caller_node_id,))
    if expected_object_digest is not None and lease.object_digest != expected_object_digest:
        return _report(ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "object binding mismatch", lease=lease, pressures=(expected_object_digest,))
    if expected_service is not None and lease.service is not expected_service:
        return _report(ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "service binding mismatch", lease=lease)
    if lease.granted_units > policy.max_units or lease.granted_streams > policy.max_streams or lease.raw_key_budget > policy.max_raw_key_budget:
        return _report(ServiceLeaseDecisionKind.QUARANTINE_BUDGET_OVERCLAIM, False, "service lease budget overclaim", lease=lease)
    if previous_lease is not None:
        if lease.sequence < previous_lease.sequence:
            return _report(ServiceLeaseDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK, False, "service lease sequence rollback", lease=lease, pressures=(previous_lease.lease_digest,))
        if lease.sequence == previous_lease.sequence and lease.lease_digest != previous_lease.lease_digest:
            return _report(ServiceLeaseDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same-sequence service lease fork", lease=lease, pressures=(previous_lease.lease_digest, lease.lease_digest))
        if lease.sequence > previous_lease.sequence and lease.previous_lease_digest != previous_lease.lease_digest:
            return _report(ServiceLeaseDecisionKind.QUARANTINE_PREVIOUS_LINK, False, "renewed service lease does not link previous lease", lease=lease, pressures=(previous_lease.lease_digest,))
        if lease.issuer_node_id != previous_lease.issuer_node_id or lease.issuer_public_key != previous_lease.issuer_public_key:
            return _report(ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "lease issuer drift during renewal", lease=lease, pressures=(previous_lease.lease_digest,))
        if lease.catalog_digest != previous_lease.catalog_digest or lease.caller_node_id != previous_lease.caller_node_id or lease.scope_digest != previous_lease.scope_digest or lease.object_digest != previous_lease.object_digest or lease.request_digest != previous_lease.request_digest or lease.service is not previous_lease.service:
            return _report(ServiceLeaseDecisionKind.QUARANTINE_BINDING_MISMATCH, False, "lease renewal changed exact service boundary", lease=lease, pressures=(previous_lease.lease_digest,))
        return _report(ServiceLeaseDecisionKind.ACCEPT_RENEWED_SERVICE_LEASE, True, "renewed service lease accepted", lease=lease)
    return _report(ServiceLeaseDecisionKind.ACCEPT_SERVICE_LEASE, True, "service lease accepted", lease=lease)
