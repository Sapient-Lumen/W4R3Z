"""Clock guards for signed observation windows.

The hard bug is accepting a signed record as fresh simply because its signature
validates. This module models local time/sequence memory: first observation,
monotonic advance, rollback, same-sequence fork, time-regression, future-skew,
expiration, and TTL excess are separate decisions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .ids import DOMAIN, sha256

CLOCK_GUARD_DOMAIN = DOMAIN + b":clock-guard-v2:"


class ClockDecisionKind(str, Enum):
    ACCEPT_FIRST = "accept_first"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_REFRESH = "accept_refresh"
    HOLD_FUTURE_SKEW = "hold_future_skew"
    REJECT_EXPIRED = "reject_expired"
    REJECT_TTL_EXCESS = "reject_ttl_excess"
    QUARANTINE_ROLLBACK = "quarantine_rollback"
    QUARANTINE_SAME_SEQ_FORK = "quarantine_same_seq_fork"
    QUARANTINE_TIME_REGRESSION = "quarantine_time_regression"
    EMPTY = "empty"


@dataclass(frozen=True)
class TimedObservation:
    authority_id: bytes
    scope_id: bytes
    purpose: str
    sequence: int
    issued_at: int
    expires_at: int
    observed_at: int
    record_digest: bytes
    source_family: str

    def __post_init__(self) -> None:
        for value in (self.authority_id, self.scope_id, self.record_digest):
            if len(value) != 32:
                raise ValueError("timed observation ids/digests must be 32 bytes")
        if not self.purpose or not self.source_family:
            raise ValueError("timed observation purpose and source family are required")
        if min(self.sequence, self.issued_at, self.expires_at, self.observed_at) < 0:
            raise ValueError("timed observation counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("timed observation expires_at must follow issued_at")

    @property
    def key(self) -> tuple[bytes, bytes, str]:
        return (self.authority_id, self.scope_id, self.purpose)

    @property
    def digest(self) -> bytes:
        return sha256(CLOCK_GUARD_DOMAIN + b":observation:" + bencode(self.bvalue()))

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"authority_id": self.authority_id,
            b"scope_id": self.scope_id,
            b"purpose": self.purpose,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"observed_at": self.observed_at,
            b"record_digest": self.record_digest,
            b"source_family": self.source_family,
        }


@dataclass(frozen=True)
class ClockPolicy:
    max_ttl_seconds: int = 3600
    max_future_skew_seconds: int = 120
    max_issued_regression_seconds: int = 120

    def validate(self) -> None:
        if self.max_ttl_seconds <= 0 or self.max_future_skew_seconds < 0 or self.max_issued_regression_seconds < 0:
            raise ValueError("clock policy thresholds invalid")


@dataclass(frozen=True)
class ClockEntry:
    highest_sequence: int
    accepted_digest: bytes
    latest_issued_at: int


@dataclass
class ClockMemory:
    entries: dict[tuple[bytes, bytes, str], ClockEntry] = field(default_factory=dict)

    def remember(self, obs: TimedObservation) -> None:
        self.entries[obs.key] = ClockEntry(obs.sequence, obs.digest, obs.issued_at)


@dataclass(frozen=True)
class ClockDecision:
    kind: ClockDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class ClockVerdict:
    observation: TimedObservation
    decision: ClockDecision


@dataclass(frozen=True)
class ClockWindowReport:
    verdicts: tuple[ClockVerdict, ...]
    family_counts: dict[str, int]
    digest: bytes

    @property
    def accept_count(self) -> int:
        return sum(1 for item in self.verdicts if item.decision.accept)

    @property
    def held_count(self) -> int:
        return sum(1 for item in self.verdicts if item.decision.kind is ClockDecisionKind.HOLD_FUTURE_SKEW)


def _assess_one(obs: TimedObservation, *, now: int, memory: ClockMemory, policy: ClockPolicy) -> ClockDecision:
    if obs.issued_at - now > policy.max_future_skew_seconds:
        return ClockDecision(ClockDecisionKind.HOLD_FUTURE_SKEW, False, "observation is too far in the future")
    if now >= obs.expires_at:
        return ClockDecision(ClockDecisionKind.REJECT_EXPIRED, False, "observation is expired")
    if obs.expires_at - obs.issued_at > policy.max_ttl_seconds:
        return ClockDecision(ClockDecisionKind.REJECT_TTL_EXCESS, False, "observation ttl exceeds local maximum")
    known = memory.entries.get(obs.key)
    if known is None:
        memory.remember(obs)
        return ClockDecision(ClockDecisionKind.ACCEPT_FIRST, True, "first local observation for authority/scope/purpose")
    if obs.sequence < known.highest_sequence:
        return ClockDecision(ClockDecisionKind.QUARANTINE_ROLLBACK, False, "sequence rolled back after higher local memory")
    if obs.sequence == known.highest_sequence and obs.digest != known.accepted_digest:
        return ClockDecision(ClockDecisionKind.QUARANTINE_SAME_SEQ_FORK, False, "same sequence has a different record digest/window")
    if obs.sequence > known.highest_sequence and known.latest_issued_at - obs.issued_at > policy.max_issued_regression_seconds:
        return ClockDecision(ClockDecisionKind.QUARANTINE_TIME_REGRESSION, False, "higher sequence has a suspiciously older issued_at")
    if obs.sequence == known.highest_sequence:
        return ClockDecision(ClockDecisionKind.ACCEPT_REFRESH, True, "same digest refreshed")
    memory.remember(obs)
    return ClockDecision(ClockDecisionKind.ACCEPT_ADVANCE, True, "sequence advanced monotonically")


def assess_clock_window(observations: Iterable[TimedObservation], *, now: int, memory: ClockMemory | None = None, policy: ClockPolicy | None = None) -> ClockWindowReport:
    policy = policy or ClockPolicy()
    policy.validate()
    memory = memory or ClockMemory()
    obs_tuple = tuple(observations)
    verdicts = tuple(ClockVerdict(obs, _assess_one(obs, now=now, memory=memory, policy=policy)) for obs in obs_tuple)
    family_counts: dict[str, int] = {}
    for verdict in verdicts:
        if verdict.decision.accept:
            family_counts[verdict.observation.source_family] = family_counts.get(verdict.observation.source_family, 0) + 1
    digest = sha256(CLOCK_GUARD_DOMAIN + b":report:" + bencode({
        b"observations": [obs.digest for obs in obs_tuple],
        b"decisions": [item.decision.kind.value for item in verdicts],
        b"families": {family: count for family, count in sorted(family_counts.items())},
    }))
    return ClockWindowReport(verdicts, family_counts, digest)
