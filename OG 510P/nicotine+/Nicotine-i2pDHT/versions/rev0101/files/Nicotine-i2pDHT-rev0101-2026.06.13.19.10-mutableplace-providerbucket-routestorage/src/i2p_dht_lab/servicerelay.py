"""Third-party relay/gossip pressure for service catalogs.

A garden's own signed catalog is necessary but not sufficient.  rev0037 adds a
small relay surface so clients can reason about what other nodes claim to have
observed: catalog visibility, useful refusal, bad service, and withdrawal
awareness.  Relay observations are evidence; they are not global reputation.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .servicecatalog import GardenServiceClass, ServiceCatalogCapsule
from .servicewithdrawal import ServiceWithdrawalReport

SERVICE_RELAY_DOMAIN = DOMAIN + b":service-relay-v1:"


class ServiceRelayObservationKind(str, Enum):
    CATALOG_SEEN = "catalog_seen"
    SERVICE_SERVED = "service_served"
    USEFUL_REFUSAL = "useful_refusal"
    WITHDRAWAL_SEEN = "withdrawal_seen"
    BAD_SERVICE = "bad_service"
    STALE_CATALOG = "stale_catalog"


POSITIVE_KINDS = {
    ServiceRelayObservationKind.CATALOG_SEEN,
    ServiceRelayObservationKind.SERVICE_SERVED,
    ServiceRelayObservationKind.USEFUL_REFUSAL,
}
NEGATIVE_KINDS = {
    ServiceRelayObservationKind.BAD_SERVICE,
    ServiceRelayObservationKind.STALE_CATALOG,
    ServiceRelayObservationKind.WITHDRAWAL_SEEN,
}


class ServiceRelayDecisionKind(str, Enum):
    ACCEPT_RELAY_DIVERSE = "accept_relay_diverse"
    ACCEPT_RELAY_WITH_REFUSAL = "accept_relay_with_refusal"
    HOLD_LOW_DIVERSITY = "hold_low_diversity"
    HOLD_WITHDRAWAL_SEEN = "hold_withdrawal_seen"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"
    QUARANTINE_CATALOG_DIGEST_MISMATCH = "quarantine_catalog_digest_mismatch"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_OBSERVER_FORK = "quarantine_observer_fork"
    QUARANTINE_NEGATIVE_EVIDENCE = "quarantine_negative_evidence"
    QUARANTINE_FAMILY_MONOCULTURE = "quarantine_family_monoculture"


@dataclass(frozen=True)
class ServiceRelayObservation:
    observer_public_key: bytes
    observer_node_id: bytes
    source_family: str
    path_family: str
    sequence: int
    issued_at: int
    expires_at: int
    catalog_digest: bytes
    kind: ServiceRelayObservationKind
    service: GardenServiceClass | None = None
    evidence_digest: bytes = b"\x00" * 32
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (("observer_public_key", self.observer_public_key), ("observer_node_id", self.observer_node_id), ("catalog_digest", self.catalog_digest), ("evidence_digest", self.evidence_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("relay observation needs source and path families")
        if self.sequence < 0:
            raise ValueError("relay observation sequence must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("relay observation expires_at must be after issued_at")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        observer_node_id: bytes,
        source_family: str,
        path_family: str,
        sequence: int,
        issued_at: int,
        expires_at: int,
        catalog_digest: bytes,
        kind: ServiceRelayObservationKind,
        service: GardenServiceClass | None = None,
        evidence_digest: bytes = b"\x00" * 32,
    ) -> "ServiceRelayObservation":
        unsigned = cls(
            observer_public_key=keypair.public_key_bytes,
            observer_node_id=observer_node_id,
            source_family=source_family,
            path_family=path_family,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=expires_at,
            catalog_digest=catalog_digest,
            kind=kind,
            service=service,
            evidence_digest=evidence_digest,
            signature=b"",
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_payload(self) -> bytes:
        return bencode({
            b"observer_public_key": self.observer_public_key,
            b"observer_node_id": self.observer_node_id,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"catalog_digest": self.catalog_digest,
            b"kind": self.kind.value,
            b"service": self.service.value if self.service is not None else "",
            b"evidence_digest": self.evidence_digest,
        })

    @property
    def observation_digest(self) -> bytes:
        return sha256(SERVICE_RELAY_DOMAIN + b":observation:" + self.unsigned_payload())

    def verify(self) -> bool:
        return verify_signature(self.observer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ServiceRelayPolicy:
    min_positive_families: int = 2
    max_observations_per_source_family: int = 2
    require_path_diversity: bool = True
    allow_useful_refusal_as_positive: bool = True

    def __post_init__(self) -> None:
        if self.min_positive_families < 0 or self.max_observations_per_source_family < 1:
            raise ValueError("relay diversity knobs must be non-negative")


@dataclass(frozen=True)
class ServiceRelayReport:
    decision_kind: ServiceRelayDecisionKind
    accept: bool
    reason: str
    catalog_digest: bytes
    positive_observation_digests: tuple[bytes, ...]
    negative_observation_digests: tuple[bytes, ...]
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ServiceRelayDecisionKind, accept: bool, reason: str, *, catalog_digest: bytes, positives: Iterable[bytes] = (), negatives: Iterable[bytes] = (), source_families: Iterable[str] = (), path_families: Iterable[str] = (), pressures: Iterable[bytes] = ()) -> ServiceRelayReport:
    positive_t = tuple(sorted(set(positives)))
    negative_t = tuple(sorted(set(negatives)))
    source_t = tuple(sorted(set(source_families)))
    path_t = tuple(sorted(set(path_families)))
    pressure_t = tuple(sorted(set(pressures)))
    digest = sha256(SERVICE_RELAY_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"catalog": catalog_digest,
        b"positives": list(positive_t),
        b"negatives": list(negative_t),
        b"source_families": list(source_t),
        b"path_families": list(path_t),
        b"pressures": list(pressure_t),
    }))
    return ServiceRelayReport(kind, accept, reason, catalog_digest, positive_t, negative_t, source_t, path_t, pressure_t, digest)


def assess_service_relay(
    observations: Iterable[ServiceRelayObservation],
    *,
    catalog: ServiceCatalogCapsule,
    now: int,
    policy: ServiceRelayPolicy | None = None,
    withdrawal_report: ServiceWithdrawalReport | None = None,
    previously_seen_observations: Iterable[bytes] = (),
) -> ServiceRelayReport:
    """Assess relayed service evidence without turning it into reputation."""
    policy = policy or ServiceRelayPolicy()
    seen = set(previously_seen_observations)
    observations_t = tuple(observations)
    source_counts: dict[str, int] = {}
    per_observer_sequence: dict[tuple[bytes, int], bytes] = {}
    positives: list[bytes] = []
    negatives: list[bytes] = []
    positive_sources: set[str] = set()
    positive_paths: set[str] = set()
    all_sources: set[str] = set()
    all_paths: set[str] = set()
    refusal_positive = False

    if withdrawal_report is not None and withdrawal_report.active_withdrawal:
        return _report(ServiceRelayDecisionKind.HOLD_WITHDRAWAL_SEEN, False, "live withdrawal report blocks relay promotion", catalog_digest=catalog.catalog_digest, pressures=(withdrawal_report.report_digest,))

    for obs in observations_t:
        if obs.observation_digest in seen:
            return _report(ServiceRelayDecisionKind.QUARANTINE_REPLAY, False, "relay observation replayed", catalog_digest=catalog.catalog_digest, pressures=(obs.observation_digest,))
        if obs.catalog_digest != catalog.catalog_digest:
            return _report(ServiceRelayDecisionKind.QUARANTINE_CATALOG_DIGEST_MISMATCH, False, "relay observation names a different catalog", catalog_digest=catalog.catalog_digest, pressures=(obs.catalog_digest, catalog.catalog_digest))
        if now < obs.issued_at or now >= obs.expires_at:
            return _report(ServiceRelayDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "relay observation is outside local clock window", catalog_digest=catalog.catalog_digest, pressures=(obs.observation_digest,))
        if not obs.verify():
            return _report(ServiceRelayDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "relay observation signature did not verify", catalog_digest=catalog.catalog_digest, pressures=(obs.observation_digest,))
        key = (obs.observer_public_key, obs.sequence)
        previous = per_observer_sequence.get(key)
        if previous is not None and previous != obs.observation_digest:
            return _report(ServiceRelayDecisionKind.QUARANTINE_OBSERVER_FORK, False, "observer emitted same-sequence relay fork", catalog_digest=catalog.catalog_digest, pressures=(previous, obs.observation_digest))
        per_observer_sequence[key] = obs.observation_digest
        source_counts[obs.source_family] = source_counts.get(obs.source_family, 0) + 1
        if source_counts[obs.source_family] > policy.max_observations_per_source_family:
            return _report(ServiceRelayDecisionKind.QUARANTINE_FAMILY_MONOCULTURE, False, "too many relay observations from one source family", catalog_digest=catalog.catalog_digest, pressures=(obs.observation_digest,))
        all_sources.add(obs.source_family)
        all_paths.add(obs.path_family)
        if obs.kind in NEGATIVE_KINDS:
            negatives.append(obs.observation_digest)
        elif obs.kind is ServiceRelayObservationKind.USEFUL_REFUSAL:
            if policy.allow_useful_refusal_as_positive:
                positives.append(obs.observation_digest)
                positive_sources.add(obs.source_family)
                positive_paths.add(obs.path_family)
                refusal_positive = True
        elif obs.kind in POSITIVE_KINDS:
            positives.append(obs.observation_digest)
            positive_sources.add(obs.source_family)
            positive_paths.add(obs.path_family)

    if negatives:
        return _report(ServiceRelayDecisionKind.QUARANTINE_NEGATIVE_EVIDENCE, False, "negative relay evidence must be handled before promotion", catalog_digest=catalog.catalog_digest, positives=positives, negatives=negatives, source_families=all_sources, path_families=all_paths, pressures=negatives)
    if len(positive_sources) < policy.min_positive_families or (policy.require_path_diversity and len(positive_paths) < policy.min_positive_families):
        return _report(ServiceRelayDecisionKind.HOLD_LOW_DIVERSITY, False, "relay observations lack source/path diversity", catalog_digest=catalog.catalog_digest, positives=positives, source_families=all_sources, path_families=all_paths, pressures=positives)
    kind = ServiceRelayDecisionKind.ACCEPT_RELAY_WITH_REFUSAL if refusal_positive else ServiceRelayDecisionKind.ACCEPT_RELAY_DIVERSE
    return _report(kind, True, "relay evidence accepted as local diversity signal", catalog_digest=catalog.catalog_digest, positives=positives, source_families=positive_sources, path_families=positive_paths)
