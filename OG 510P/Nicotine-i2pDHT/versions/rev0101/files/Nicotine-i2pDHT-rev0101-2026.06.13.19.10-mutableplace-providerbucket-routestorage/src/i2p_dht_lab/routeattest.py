"""Route-attestation pressure for contact leases.

A fresh contact lease says a node currently advertises an entrance purpose.  It
does not say how that lease reached us, whether one garden captured the route
repair path, or whether many attestations are actually independent.  This module
adds a small signed attestation layer for the seam between contact leases,
route-gossip, and seed portfolios.

Attestations remain evidence, not truth.  They are useful when they are fresh,
signed, purpose-bound, lease-bound, and diverse across attester and path
families.  They are dangerous when they replay old sequences, fork at the same
sequence, or make one introducer family look like a whole network.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .contactlease import ContactLease, ContactLeaseBook, ContactLeasePurpose
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity, select_family_capped
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256, xor_distance

ROUTE_ATTEST_DOMAIN = DOMAIN + b":route-attest-v1:"
MAX_ATTEST_TTL_SECONDS = 24 * 3600


class RouteAttestationDecisionKind(str, Enum):
    ACCEPT_ATTESTED_ROUTE_SET = "accept_attested_route_set"
    CONTINUE_NO_VALID_ATTESTATIONS = "continue_no_valid_attestations"
    CONTINUE_LOW_CONTACT_DIVERSITY = "continue_low_contact_diversity"
    CONTINUE_LOW_ATTESTER_DIVERSITY = "continue_low_attester_diversity"
    CONTINUE_LOW_PATH_DIVERSITY = "continue_low_path_diversity"
    CONTINUE_LOW_PURPOSE_COVERAGE = "continue_low_purpose_coverage"
    QUARANTINE_LEASE_FORK_PRESSURE = "quarantine_lease_fork_pressure"
    QUARANTINE_ATTESTATION_FORK = "quarantine_attestation_fork"
    QUARANTINE_ATTESTER_MONOCULTURE = "quarantine_attester_monoculture"


class RouteAttestationVerdictKind(str, Enum):
    ACCEPT_FIRST = "accept_first"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_REFRESH = "accept_refresh"
    REJECT_BAD_SIGNATURE_OR_TIME = "reject_bad_signature_or_time"
    REJECT_MISSING_OR_INVALID_LEASE = "reject_missing_or_invalid_lease"
    REJECT_PURPOSE_MISMATCH = "reject_purpose_mismatch"
    REJECT_STALE_ROLLBACK = "reject_stale_rollback"
    QUARANTINE_SAME_SEQ_FORK = "quarantine_same_seq_fork"


@dataclass(frozen=True)
class RouteAttestation:
    lease_hash: bytes
    contact_node_id: bytes
    contact_public_key: bytes
    purpose: ContactLeasePurpose
    attester_node_id: bytes
    attester_public_key: bytes
    attester_family: str
    path_family: str
    sequence: int
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.lease_hash) != 32 or len(self.contact_node_id) != 32 or len(self.contact_public_key) != 32:
            raise ValueError("route attestation contact fields must be 32-byte digests/keys")
        if len(self.attester_node_id) != 32 or len(self.attester_public_key) != 32:
            raise ValueError("route attestation attester fields must be 32 bytes")
        if not self.attester_family or not self.path_family:
            raise ValueError("route attestation needs attester and path family hints")
        if self.sequence < 0 or self.expires_at <= self.issued_at or self.expires_at - self.issued_at > MAX_ATTEST_TTL_SECONDS:
            raise ValueError("route attestation sequence/time window is invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        attester_node_id: bytes,
        attester_family: str,
        path_family: str,
        lease: ContactLease,
        purpose: ContactLeasePurpose,
        sequence: int,
        issued_at: int,
        ttl: int = 3600,
    ) -> "RouteAttestation":
        if ttl <= 0:
            raise ValueError("route attestation ttl must be positive")
        unsigned = cls(
            lease_hash=lease.lease_hash,
            contact_node_id=lease.node_id,
            contact_public_key=lease.public_key,
            purpose=purpose,
            attester_node_id=attester_node_id,
            attester_public_key=keypair.public_key_bytes,
            attester_family=attester_family,
            path_family=path_family,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + min(ttl, MAX_ATTEST_TTL_SECONDS),
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"lease_hash": self.lease_hash,
            b"contact_node_id": self.contact_node_id,
            b"contact_public_key": self.contact_public_key,
            b"purpose": self.purpose.value,
            b"attester_node_id": self.attester_node_id,
            b"attester_public_key": self.attester_public_key,
            b"attester_family": self.attester_family,
            b"path_family": self.path_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return ROUTE_ATTEST_DOMAIN + b":unsigned:" + bencode(self.bvalue())

    @property
    def attestation_digest(self) -> bytes:
        return sha256(ROUTE_ATTEST_DOMAIN + b":digest:" + self.unsigned_payload() + self.signature)

    @property
    def state_key(self) -> tuple[bytes, bytes, str]:
        return (self.attester_public_key, self.lease_hash, self.purpose.value)

    def live(self, *, now: int, max_future_skew: int = 300) -> bool:
        return self.issued_at - max_future_skew <= now < self.expires_at + max_future_skew

    def signature_valid(self) -> bool:
        return verify_signature(self.attester_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class RouteAttestationState:
    highest_sequence: int
    accepted_digest: bytes
    fork_digests: frozenset[bytes] = frozenset()

    @property
    def forked(self) -> bool:
        return bool(self.fork_digests)


@dataclass(frozen=True)
class RouteAttestationVerdict:
    kind: RouteAttestationVerdictKind
    accepted: bool
    reason: str
    attestation_digest: bytes
    known_sequence: int | None = None

    @property
    def risky(self) -> bool:
        return not self.accepted or self.kind is RouteAttestationVerdictKind.QUARANTINE_SAME_SEQ_FORK


@dataclass
class RouteAttestationBook:
    states: dict[tuple[bytes, bytes, str], RouteAttestationState] = field(default_factory=dict)
    fork_pressure: bool = False

    def observe(self, attestation: RouteAttestation, *, now: int, max_future_skew: int = 300) -> RouteAttestationVerdict:
        known = self.states.get(attestation.state_key)
        known_seq = None if known is None else known.highest_sequence
        if not attestation.live(now=now, max_future_skew=max_future_skew) or not attestation.signature_valid():
            return RouteAttestationVerdict(RouteAttestationVerdictKind.REJECT_BAD_SIGNATURE_OR_TIME, False, "attestation signature or time window is invalid", attestation.attestation_digest, known_seq)
        if known is None:
            self.states[attestation.state_key] = RouteAttestationState(attestation.sequence, attestation.attestation_digest)
            return RouteAttestationVerdict(RouteAttestationVerdictKind.ACCEPT_FIRST, True, "first fresh attestation for lease/purpose/attester", attestation.attestation_digest, None)
        if attestation.sequence < known.highest_sequence:
            return RouteAttestationVerdict(RouteAttestationVerdictKind.REJECT_STALE_ROLLBACK, False, "attestation sequence rolled back", attestation.attestation_digest, known.highest_sequence)
        if attestation.sequence == known.highest_sequence and attestation.attestation_digest != known.accepted_digest:
            self.fork_pressure = True
            self.states[attestation.state_key] = RouteAttestationState(known.highest_sequence, known.accepted_digest, known.fork_digests | frozenset({attestation.attestation_digest}))
            return RouteAttestationVerdict(RouteAttestationVerdictKind.QUARANTINE_SAME_SEQ_FORK, False, "attester emitted a same-sequence fork for this lease/purpose", attestation.attestation_digest, known.highest_sequence)
        if attestation.sequence == known.highest_sequence:
            return RouteAttestationVerdict(RouteAttestationVerdictKind.ACCEPT_REFRESH, True, "attestation refreshed an already-known sequence", attestation.attestation_digest, known.highest_sequence)
        self.states[attestation.state_key] = RouteAttestationState(attestation.sequence, attestation.attestation_digest)
        return RouteAttestationVerdict(RouteAttestationVerdictKind.ACCEPT_ADVANCE, True, "attestation advanced monotonically", attestation.attestation_digest, known.highest_sequence)


@dataclass(frozen=True)
class RouteAttestationPolicy:
    required_purposes: frozenset[ContactLeasePurpose] = frozenset({ContactLeasePurpose.ROUTE})
    min_valid_attestations: int = 4
    min_contact_families: int = 3
    min_attester_families: int = 3
    min_path_families: int = 2
    max_per_contact_family: int = 2
    max_per_attester_family: int = 2
    max_per_path_family: int = 3
    min_work_bits: int = 0
    max_future_skew: int = 300

    def validate(self) -> None:
        for value in (self.min_valid_attestations, self.min_contact_families, self.min_attester_families, self.min_path_families, self.max_per_contact_family, self.max_per_attester_family, self.max_per_path_family):
            if value <= 0:
                raise ValueError("route attestation diversity thresholds must be positive")
        if self.min_work_bits < 0 or self.max_future_skew < 0:
            raise ValueError("route attestation work/skew thresholds must be non-negative")


@dataclass(frozen=True)
class RouteAttestationDecision:
    kind: RouteAttestationDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class RouteAttestationReport:
    selected_attestations: tuple[RouteAttestation, ...]
    invalid_attestations: tuple[RouteAttestation, ...]
    verdicts: tuple[RouteAttestationVerdict, ...]
    contact_family_counts: Mapping[str, int]
    attester_family_counts: Mapping[str, int]
    path_family_counts: Mapping[str, int]
    purpose_counts: Mapping[str, int]
    decision: RouteAttestationDecision
    transcript_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _counts(values: Iterable[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return out


def assess_route_attestations(
    attestations: Iterable[RouteAttestation],
    leases: Iterable[ContactLease],
    *,
    now: int,
    target: bytes | None = None,
    policy: RouteAttestationPolicy | None = None,
    attestation_book: RouteAttestationBook | None = None,
    lease_book: ContactLeaseBook | None = None,
) -> RouteAttestationReport:
    policy = policy or RouteAttestationPolicy()
    policy.validate()
    book = attestation_book or RouteAttestationBook()
    lbook = lease_book or ContactLeaseBook()
    lease_by_hash = {lease.lease_hash: lease for lease in leases}
    valid: list[RouteAttestation] = []
    invalid: list[RouteAttestation] = []
    verdicts: list[RouteAttestationVerdict] = []
    for attestation in attestations:
        verdict = book.observe(attestation, now=now, max_future_skew=policy.max_future_skew)
        lease = lease_by_hash.get(attestation.lease_hash)
        if verdict.accepted and lease is None:
            verdict = RouteAttestationVerdict(RouteAttestationVerdictKind.REJECT_MISSING_OR_INVALID_LEASE, False, "attestation references an unknown lease", attestation.attestation_digest, verdict.known_sequence)
        elif verdict.accepted and (lease.node_id != attestation.contact_node_id or lease.public_key != attestation.contact_public_key or not lease.has_purpose(attestation.purpose)):
            verdict = RouteAttestationVerdict(RouteAttestationVerdictKind.REJECT_PURPOSE_MISMATCH, False, "attestation is not bound to the advertised lease contact/purpose", attestation.attestation_digest, verdict.known_sequence)
        elif verdict.accepted and lease is not None:
            lease_verdict = lbook.observe(lease, now=now, min_work_bits=policy.min_work_bits)
            if not lease_verdict.accepted and lease_verdict.kind.value != "accept_refresh":
                verdict = RouteAttestationVerdict(RouteAttestationVerdictKind.REJECT_MISSING_OR_INVALID_LEASE, False, "attestation references a lease that failed local validation", attestation.attestation_digest, verdict.known_sequence)
        verdicts.append(verdict)
        if verdict.accepted:
            valid.append(attestation)
        else:
            invalid.append(attestation)

    target = target or b"\x00" * 32
    selected_by_contact = select_family_capped(
        valid,
        family_of=lambda item: lease_by_hash[item.lease_hash].family_id,
        sort_key=lambda item: (xor_distance(item.contact_node_id, target), item.attester_family, item.path_family, item.attestation_digest),
        limit=max(policy.min_valid_attestations, policy.min_contact_families * policy.max_per_contact_family, policy.min_attester_families * policy.max_per_attester_family),
        max_per_family=policy.max_per_contact_family,
    )
    selected = tuple(select_family_capped(
        selected_by_contact,
        family_of=lambda item: item.attester_family,
        sort_key=lambda item: (xor_distance(item.contact_node_id, target), item.path_family, item.attestation_digest),
        limit=max(policy.min_valid_attestations, policy.min_attester_families * policy.max_per_attester_family),
        max_per_family=policy.max_per_attester_family,
    ))
    contact_diversity = analyze_family_diversity(selected, family_of=lambda item: lease_by_hash[item.lease_hash].family_id, policy=FamilyDiversityPolicy(policy.min_contact_families, policy.max_per_contact_family))
    attester_diversity = analyze_family_diversity(selected, family_of=lambda item: item.attester_family, policy=FamilyDiversityPolicy(policy.min_attester_families, policy.max_per_attester_family))
    path_counts = _counts(item.path_family for item in selected)
    purpose_counts = _counts(item.purpose.value for item in selected)

    if lbook.fork_pressure:
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.QUARANTINE_LEASE_FORK_PRESSURE, False, "contact-lease fork pressure present while evaluating route attestations")
    elif book.fork_pressure:
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.QUARANTINE_ATTESTATION_FORK, False, "attestation fork pressure present")
    elif not selected:
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.CONTINUE_NO_VALID_ATTESTATIONS, False, "no valid route attestations survived lease/signature checks")
    elif len(selected) < policy.min_valid_attestations or not contact_diversity.passes(FamilyDiversityPolicy(policy.min_contact_families, policy.max_per_contact_family)):
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.CONTINUE_LOW_CONTACT_DIVERSITY, False, "route attestations do not cover enough contact families")
    elif not attester_diversity.passes(FamilyDiversityPolicy(policy.min_attester_families, policy.max_per_attester_family)):
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.CONTINUE_LOW_ATTESTER_DIVERSITY, False, "route attestations do not cover enough attester families")
    elif len(path_counts) < policy.min_path_families:
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.QUARANTINE_ATTESTER_MONOCULTURE, False, "attester diversity arrived through too few path families")
    elif any(purpose_counts.get(purpose.value, 0) <= 0 for purpose in policy.required_purposes):
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.CONTINUE_LOW_PURPOSE_COVERAGE, False, "attestations lack required route/seed/garden purposes")
    else:
        decision = RouteAttestationDecision(RouteAttestationDecisionKind.ACCEPT_ATTESTED_ROUTE_SET, True, "leases and attestations have enough contact/attester/path diversity for local route repair")

    digest = sha256(ROUTE_ATTEST_DOMAIN + b":report:" + bencode({
        b"selected": [item.attestation_digest for item in selected],
        b"invalid": [item.attestation_digest for item in invalid],
        b"verdicts": [item.kind.value for item in verdicts],
        b"contact_families": {family: count for family, count in sorted(contact_diversity.family_counts.items())},
        b"attester_families": {family: count for family, count in sorted(attester_diversity.family_counts.items())},
        b"path_families": {family: count for family, count in sorted(path_counts.items())},
        b"purpose_counts": {purpose: count for purpose, count in sorted(purpose_counts.items())},
        b"decision": decision.kind.value,
    }))
    return RouteAttestationReport(selected, tuple(invalid), tuple(verdicts), contact_diversity.family_counts, attester_diversity.family_counts, path_counts, purpose_counts, decision, digest)
