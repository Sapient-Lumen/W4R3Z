"""Absence-gate pressure for DHT negative answers.

The riskiest provider/mutable lookup answer is often not a lie about bytes; it
is a convenient absence claim.  This module treats "not found" as typed local
pressure, not truth.  A signed empty answer may feed a short negative cache or a
request for more paths, but durable absence needs tombstone/fork/witness context.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .identity import DhtKeypair, verify_signature

ABSENCE_GATE_DOMAIN = DOMAIN + b":absence-gate-v1:"


class AbsenceObservationKind(str, Enum):
    EMPTY_PROVIDER = "empty_provider"
    EMPTY_MUTABLE = "empty_mutable"
    TOMBSTONE_SEEN = "tombstone_seen"
    TIMEOUT = "timeout"
    USEFUL_REFUSAL = "useful_refusal"
    POSITIVE_PROVIDER = "positive_provider"
    POSITIVE_MUTABLE_HEAD = "positive_mutable_head"


class AbsenceDecisionKind(str, Enum):
    ACCEPT_DURABLE_TOMBSTONE_ABSENCE = "accept_durable_tombstone_absence"
    ACCEPT_SOFT_NEGATIVE_CACHE = "accept_soft_negative_cache"
    CONTINUE_MORE_PATHS = "continue_more_paths"
    CONTINUE_TIMEOUT_PRESSURE = "continue_timeout_pressure"
    QUARANTINE_FAST_EMPTY_CAPTURE = "quarantine_fast_empty_capture"
    QUARANTINE_POSITIVE_CONFLICT = "quarantine_positive_conflict"
    QUARANTINE_BAD_OBSERVATION = "quarantine_bad_observation"


EMPTY_KINDS = frozenset({AbsenceObservationKind.EMPTY_PROVIDER, AbsenceObservationKind.EMPTY_MUTABLE})
POSITIVE_KINDS = frozenset({AbsenceObservationKind.POSITIVE_PROVIDER, AbsenceObservationKind.POSITIVE_MUTABLE_HEAD})


@dataclass(frozen=True)
class AbsenceObservation:
    observer_public_key: bytes
    target_digest: bytes
    kind: AbsenceObservationKind
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    latency_ms: int = 0
    evidence_digest: bytes = b"\x00" * 32
    signature: bytes = b""

    def __post_init__(self) -> None:
        if len(self.observer_public_key) != 32 or len(self.target_digest) != 32 or len(self.evidence_digest) != 32:
            raise ValueError("absence observation keys/digests must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("absence observation needs source/path family hints")
        if self.issued_at < 0 or self.expires_at <= self.issued_at or self.latency_ms < 0:
            raise ValueError("absence observation time/latency invalid")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        target_digest: bytes,
        kind: AbsenceObservationKind,
        source_family: str,
        path_family: str,
        issued_at: int,
        ttl: int = 900,
        latency_ms: int = 0,
        evidence_digest: bytes | None = None,
    ) -> "AbsenceObservation":
        if ttl <= 0:
            raise ValueError("absence observation ttl must be positive")
        unsigned = cls(
            observer_public_key=keypair.public_key_bytes,
            target_digest=target_digest,
            kind=kind,
            source_family=source_family,
            path_family=path_family,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            latency_ms=latency_ms,
            evidence_digest=evidence_digest or b"\x00" * 32,
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, object]:
        return {
            b"observer_public_key": self.observer_public_key,
            b"target_digest": self.target_digest,
            b"kind": self.kind.value,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"latency_ms": self.latency_ms,
            b"evidence_digest": self.evidence_digest,
        }

    def unsigned_payload(self) -> bytes:
        return ABSENCE_GATE_DOMAIN + b":observation-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def observation_digest(self) -> bytes:
        return sha256(ABSENCE_GATE_DOMAIN + b":observation:" + self.unsigned_payload() + self.signature)

    def verify(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at and verify_signature(self.observer_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class AbsencePolicy:
    min_empty_families: int = 3
    min_empty_paths: int = 3
    min_tombstone_families: int = 2
    fast_window_ms: int = 250
    max_fast_family_share: float = 0.66
    soft_negative_ttl: int = 120

    def validate(self) -> None:
        if self.min_empty_families <= 0 or self.min_empty_paths <= 0 or self.min_tombstone_families <= 0:
            raise ValueError("absence policy minimums must be positive")
        if not (0.0 < self.max_fast_family_share <= 1.0):
            raise ValueError("absence policy max_fast_family_share invalid")
        if self.fast_window_ms < 0 or self.soft_negative_ttl <= 0:
            raise ValueError("absence policy timing invalid")


@dataclass(frozen=True)
class AbsenceAssessment:
    decision_kind: AbsenceDecisionKind
    accept: bool
    reason: str
    valid_observation_count: int
    empty_family_count: int
    empty_path_count: int
    tombstone_family_count: int
    positive_count: int
    timeout_count: int
    fast_empty_family_share: float
    negative_cache_ttl: int
    quarantine_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _family_share(observations: tuple[AbsenceObservation, ...]) -> float:
    if not observations:
        return 0.0
    counts: dict[str, int] = {}
    for obs in observations:
        counts[obs.source_family] = counts.get(obs.source_family, 0) + 1
    return max(counts.values()) / len(observations)


def assess_absence_window(
    target_digest: bytes,
    observations: tuple[AbsenceObservation, ...],
    *,
    now: int,
    policy: AbsencePolicy | None = None,
) -> AbsenceAssessment:
    """Assess whether an absence-looking lookup window can influence local state."""
    if len(target_digest) != 32:
        raise ValueError("target digest must be 32 bytes")
    policy = policy or AbsencePolicy()
    policy.validate()

    valid: list[AbsenceObservation] = []
    bad: list[bytes] = []
    for obs in observations:
        if obs.target_digest != target_digest or not obs.verify(now=now):
            bad.append(obs.observation_digest)
        else:
            valid.append(obs)

    if bad and not valid:
        decision = AbsenceDecisionKind.QUARANTINE_BAD_OBSERVATION
        reason = "all absence observations were invalid, expired, or target-mismatched"
    else:
        positive = [obs for obs in valid if obs.kind in POSITIVE_KINDS]
        empty = [obs for obs in valid if obs.kind in EMPTY_KINDS]
        tombstones = [obs for obs in valid if obs.kind is AbsenceObservationKind.TOMBSTONE_SEEN]
        timeouts = [obs for obs in valid if obs.kind is AbsenceObservationKind.TIMEOUT]
        fast_empty = tuple(obs for obs in empty if obs.latency_ms <= policy.fast_window_ms)
        fast_share = _family_share(fast_empty)
        empty_families = {obs.source_family for obs in empty}
        empty_paths = {obs.path_family for obs in empty}
        tomb_families = {obs.source_family for obs in tombstones}

        if positive:
            decision = AbsenceDecisionKind.QUARANTINE_POSITIVE_CONFLICT
            reason = "absence window contains positive provider/head evidence"
        elif len(fast_empty) >= policy.min_empty_families and fast_share > policy.max_fast_family_share:
            decision = AbsenceDecisionKind.QUARANTINE_FAST_EMPTY_CAPTURE
            reason = "fast empty answers are dominated by one source family"
        elif len(empty_families) >= policy.min_empty_families and len(empty_paths) >= policy.min_empty_paths and len(tomb_families) >= policy.min_tombstone_families:
            decision = AbsenceDecisionKind.ACCEPT_DURABLE_TOMBSTONE_ABSENCE
            reason = "diverse empty answers are supported by diverse tombstone evidence"
        elif len(empty_families) >= policy.min_empty_families and len(empty_paths) >= policy.min_empty_paths:
            decision = AbsenceDecisionKind.ACCEPT_SOFT_NEGATIVE_CACHE
            reason = "diverse empty answers can enter only a short soft negative cache"
        elif timeouts and len(empty_families) + len({obs.source_family for obs in timeouts}) >= policy.min_empty_families:
            decision = AbsenceDecisionKind.CONTINUE_TIMEOUT_PRESSURE
            reason = "timeouts plus empties request more paths, not absence truth"
        else:
            decision = AbsenceDecisionKind.CONTINUE_MORE_PATHS
            reason = "absence evidence is under-diverse"

    valid_tuple = tuple(valid)
    empty_tuple = tuple(obs for obs in valid_tuple if obs.kind in EMPTY_KINDS)
    tombstone_tuple = tuple(obs for obs in valid_tuple if obs.kind is AbsenceObservationKind.TOMBSTONE_SEEN)
    positive_count = sum(1 for obs in valid_tuple if obs.kind in POSITIVE_KINDS)
    timeout_count = sum(1 for obs in valid_tuple if obs.kind is AbsenceObservationKind.TIMEOUT)
    fast_share = _family_share(tuple(obs for obs in empty_tuple if obs.latency_ms <= policy.fast_window_ms))
    accept = decision in {AbsenceDecisionKind.ACCEPT_DURABLE_TOMBSTONE_ABSENCE, AbsenceDecisionKind.ACCEPT_SOFT_NEGATIVE_CACHE}
    negative_ttl = policy.soft_negative_ttl if decision is AbsenceDecisionKind.ACCEPT_SOFT_NEGATIVE_CACHE else 0
    report_digest = sha256(ABSENCE_GATE_DOMAIN + b":report:" + bencode({
        b"decision": decision.value,
        b"valid": len(valid_tuple),
        b"empty_families": len({obs.source_family for obs in empty_tuple}),
        b"empty_paths": len({obs.path_family for obs in empty_tuple}),
        b"tombstone_families": len({obs.source_family for obs in tombstone_tuple}),
        b"positive": positive_count,
        b"timeouts": timeout_count,
        b"fast_share_ppm": int(fast_share * 1_000_000),
        b"bad": bad,
    }))
    return AbsenceAssessment(
        decision_kind=decision,
        accept=accept,
        reason=reason,
        valid_observation_count=len(valid_tuple),
        empty_family_count=len({obs.source_family for obs in empty_tuple}),
        empty_path_count=len({obs.path_family for obs in empty_tuple}),
        tombstone_family_count=len({obs.source_family for obs in tombstone_tuple}),
        positive_count=positive_count,
        timeout_count=timeout_count,
        fast_empty_family_share=fast_share,
        negative_cache_ttl=negative_ttl,
        quarantine_digests=tuple(bad) + tuple(obs.observation_digest for obs in valid_tuple if decision.value.startswith("quarantine_")),
        report_digest=report_digest,
    )
