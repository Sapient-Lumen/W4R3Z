"""Key-crisis route gating for sticky I2P entrances.

Key-crisis notices are useful only if they join back to routes, contact leases,
succession records, revocations, and tombstones before a caller uses a new
entrance.  Otherwise a compromised key can keep advertising stale routes or an
attacker can launder a crisis into arbitrary successor routing.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .contactlease import ContactLease
from .ids import DOMAIN, sha256
from .keycrisis import KeyCrisisGateDecisionKind, KeyCrisisGateReport
from .succession import SuccessionVerdict, SuccessionVerdictKind

CRISIS_ROUTE_DOMAIN = DOMAIN + b":crisis-route-v1:"
ZERO_DIGEST = b"\x00" * 32


class CrisisRouteDecisionKind(str, Enum):
    ACCEPT_UNGATED_ROUTE = "accept_ungated_route"
    ACCEPT_SUCCESSOR_ROUTE = "accept_successor_route"
    WATCH_DESTINATION_LOST_ROUTE = "watch_destination_lost_route"
    BLOCK_CRISIS_GATE = "block_crisis_gate"
    QUARANTINE_ROUTE_KEY_MISMATCH = "quarantine_route_key_mismatch"
    QUARANTINE_SUCCESSION_MISMATCH = "quarantine_succession_mismatch"
    QUARANTINE_REVOCATION_PRESENT = "quarantine_revocation_present"
    QUARANTINE_TOMBSTONE_PRESENT = "quarantine_tombstone_present"
    QUARANTINE_LEASE_INVALID = "quarantine_lease_invalid"


@dataclass(frozen=True)
class CrisisRoutePolicy:
    require_successor_for_compromise: bool = True
    allow_destination_lost_watch: bool = True


@dataclass(frozen=True)
class CrisisRouteAssessment:
    decision_kind: CrisisRouteDecisionKind
    accept: bool
    reason: str
    subject_public_key: bytes
    route_public_key: bytes
    route_digest: bytes
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_crisis_route(
    *,
    gate: KeyCrisisGateReport,
    route_lease: ContactLease,
    now: int,
    successor_public_key: bytes = b"",
    succession_verdict: SuccessionVerdict | None = None,
    revocation_digests: Iterable[bytes] = (),
    tombstone_digests: Iterable[bytes] = (),
    policy: CrisisRoutePolicy | None = None,
) -> CrisisRouteAssessment:
    policy = policy or CrisisRoutePolicy()
    revocations = tuple(sorted(revocation_digests))
    tombstones = tuple(sorted(tombstone_digests))
    if not route_lease.verify(now=now):
        return _assessment(CrisisRouteDecisionKind.QUARANTINE_LEASE_INVALID, False, "route contact lease failed before crisis gate", gate, route_lease, revocations + tombstones)
    if revocations:
        return _assessment(CrisisRouteDecisionKind.QUARANTINE_REVOCATION_PRESENT, False, "route attempt is blocked by live revocation evidence", gate, route_lease, revocations)
    if tombstones:
        return _assessment(CrisisRouteDecisionKind.QUARANTINE_TOMBSTONE_PRESENT, False, "route attempt is blocked by live tombstone evidence", gate, route_lease, tombstones)

    route_key = route_lease.public_key
    subject = gate.subject_public_key
    if gate.decision_kind is KeyCrisisGateDecisionKind.ACCEPT_NO_LIVE_CRISIS:
        if route_key != subject:
            return _assessment(CrisisRouteDecisionKind.QUARANTINE_ROUTE_KEY_MISMATCH, False, "ungated route key does not match the subject key", gate, route_lease, ())
        return _assessment(CrisisRouteDecisionKind.ACCEPT_UNGATED_ROUTE, True, "no live crisis gates the subject route key", gate, route_lease, ())

    if gate.decision_kind is KeyCrisisGateDecisionKind.WATCH_DESTINATION_LOST:
        if not policy.allow_destination_lost_watch:
            return _assessment(CrisisRouteDecisionKind.BLOCK_CRISIS_GATE, False, "destination-lost watch is disabled by policy", gate, route_lease, (gate.active_notice_digest,))
        if route_key not in {subject, successor_public_key}:
            return _assessment(CrisisRouteDecisionKind.QUARANTINE_ROUTE_KEY_MISMATCH, False, "destination-lost alternate route does not bind subject or successor key", gate, route_lease, (gate.active_notice_digest,))
        return _assessment(CrisisRouteDecisionKind.WATCH_DESTINATION_LOST_ROUTE, True, "destination-loss crisis accepts route only with watch pressure", gate, route_lease, (gate.active_notice_digest,))

    if gate.decision_kind is KeyCrisisGateDecisionKind.ACCEPT_SUCCESSION_RECOVERY:
        if route_key != successor_public_key or not successor_public_key:
            return _assessment(CrisisRouteDecisionKind.QUARANTINE_ROUTE_KEY_MISMATCH, False, "successor route does not bind the successor key from crisis evidence", gate, route_lease, (gate.active_notice_digest,))
        if not _succession_ok(succession_verdict, subject, successor_public_key):
            return _assessment(CrisisRouteDecisionKind.QUARANTINE_SUCCESSION_MISMATCH, False, "successor route lacks accepted co-signed succession evidence", gate, route_lease, (gate.active_notice_digest,))
        return _assessment(CrisisRouteDecisionKind.ACCEPT_SUCCESSOR_ROUTE, True, "crisis gate, successor route, and succession evidence agree", gate, route_lease, (gate.active_notice_digest, succession_verdict.old_public_key if succession_verdict else ZERO_DIGEST))

    if gate.blocked:
        if policy.require_successor_for_compromise:
            return _assessment(CrisisRouteDecisionKind.BLOCK_CRISIS_GATE, False, gate.reason, gate, route_lease, (gate.active_notice_digest,))
        return _assessment(CrisisRouteDecisionKind.BLOCK_CRISIS_GATE, False, gate.reason, gate, route_lease, (gate.active_notice_digest,))

    return _assessment(CrisisRouteDecisionKind.BLOCK_CRISIS_GATE, False, "unknown crisis gate state is fail-closed", gate, route_lease, (gate.active_notice_digest,))


def _succession_ok(verdict: SuccessionVerdict | None, subject: bytes, successor: bytes) -> bool:
    if verdict is None or not verdict.accepted:
        return False
    if verdict.kind not in {SuccessionVerdictKind.ACCEPT_FIRST, SuccessionVerdictKind.ACCEPT_ADVANCE, SuccessionVerdictKind.ACCEPT_REFRESH}:
        return False
    return verdict.old_public_key == subject and verdict.current_public_key == successor


def _assessment(kind: CrisisRouteDecisionKind, accept: bool, reason: str, gate: KeyCrisisGateReport, route_lease: ContactLease, pressures: Iterable[bytes]) -> CrisisRouteAssessment:
    pressure_tuple = tuple(sorted(d for d in pressures if d))
    digest = sha256(CRISIS_ROUTE_DOMAIN + b":assessment:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"gate": gate.report_digest,
        b"subject": gate.subject_public_key,
        b"route": route_lease.lease_hash,
        b"route_key": route_lease.public_key,
        b"pressures": pressure_tuple,
    }))
    return CrisisRouteAssessment(kind, accept, reason, gate.subject_public_key, route_lease.public_key, route_lease.lease_hash, pressure_tuple, digest)
