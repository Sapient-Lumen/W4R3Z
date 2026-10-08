"""Repeated-round probe ledger for bootstrap and negative-space pressure.

rev0031 treats bootstrap and liveness probing as restart-sensitive protocol
memory.  A single accepted peerbook, live probe, clean no-router skip, or empty
answer can be locally valid and still unsafe if the same captured family keeps
winning the fast window across rounds.

This module is intentionally small and deterministic.  It does not claim to
model I2P latency.  It records typed round observations and asks whether the
recent window is diverse enough, stale-negative-loop free, and replay free before
callers advance sticky entrance state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .bootstrapjoin import BootstrapJoinReport
from .egressmeter import EgressWindowReport
from .ids import DOMAIN, sha256

PROBE_LEDGER_DOMAIN = DOMAIN + b":probe-ledger-v1:"
ZERO_DIGEST = b"\x00" * 32


class ProbeLedgerDecisionKind(str, Enum):
    ACCEPT_REPEATED_DIVERSE_PROGRESS = "accept_repeated_diverse_progress"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_NEEDS_MORE_ROUNDS = "continue_needs_more_rounds"
    CONTINUE_NEEDS_FAMILY_DIVERSITY = "continue_needs_family_diversity"
    CONTINUE_NEEDS_PATH_DIVERSITY = "continue_needs_path_diversity"
    QUARANTINE_REPLAYED_ROUND = "quarantine_replayed_round"
    QUARANTINE_ABSENCE_ONLY_LOOP = "quarantine_absence_only_loop"
    QUARANTINE_FAST_FAMILY_CAPTURE = "quarantine_fast_family_capture"
    QUARANTINE_NEGATIVE_CONTRADICTION = "quarantine_negative_contradiction"
    QUARANTINE_BOOTSTRAP_FAILURE = "quarantine_bootstrap_failure"
    QUARANTINE_EXPIRED_ROUND = "quarantine_expired_round"


@dataclass(frozen=True)
class ProbeLedgerRound:
    round_id: bytes
    source_family: str
    path_family: str
    issued_at: int
    expires_at: int
    bootstrap_digest: bytes = ZERO_DIGEST
    bootstrap_accept: bool = False
    live_probe_digests: tuple[bytes, ...] = ()
    absence_digest: bytes = ZERO_DIGEST
    absence_accept: bool = False
    egress_digest: bytes = ZERO_DIGEST
    egress_accept: bool = True
    positive_evidence_digests: tuple[bytes, ...] = ()
    fast_window_winner: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        for name, value in (
            ("round_id", self.round_id),
            ("bootstrap_digest", self.bootstrap_digest),
            ("absence_digest", self.absence_digest),
            ("egress_digest", self.egress_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"probe ledger {name} must be 32 bytes")
        for digest in self.live_probe_digests + self.positive_evidence_digests:
            if len(digest) != 32:
                raise ValueError("probe ledger embedded digests must be 32 bytes")
        if not self.source_family or not self.path_family or self.expires_at <= self.issued_at:
            raise ValueError("probe ledger family/time fields invalid")

    @classmethod
    def from_bootstrap(
        cls,
        *,
        round_id: bytes,
        source_family: str,
        path_family: str,
        issued_at: int,
        ttl: int,
        bootstrap: BootstrapJoinReport,
        egress: EgressWindowReport | None = None,
        live_probe_digests: Iterable[bytes] = (),
        absence_digest: bytes = ZERO_DIGEST,
        absence_accept: bool = False,
        positive_evidence_digests: Iterable[bytes] = (),
        fast_window_winner: bool = False,
        note: str = "",
    ) -> "ProbeLedgerRound":
        if ttl <= 0:
            raise ValueError("probe ledger ttl must be positive")
        return cls(
            round_id=round_id,
            source_family=source_family,
            path_family=path_family,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            bootstrap_digest=bootstrap.transcript_digest,
            bootstrap_accept=bootstrap.accept and not bootstrap.quarantined,
            live_probe_digests=tuple(sorted(live_probe_digests)),
            absence_digest=absence_digest,
            absence_accept=absence_accept,
            egress_digest=ZERO_DIGEST if egress is None else egress.report_digest,
            egress_accept=True if egress is None else (egress.accept and not egress.quarantined),
            positive_evidence_digests=tuple(sorted(positive_evidence_digests)),
            fast_window_winner=fast_window_winner,
            note=note[:160],
        )

    @property
    def live_probe_count(self) -> int:
        return len(self.live_probe_digests)

    @property
    def absence_only(self) -> bool:
        return self.absence_accept and not self.bootstrap_accept and self.live_probe_count == 0 and not self.positive_evidence_digests

    @property
    def round_digest(self) -> bytes:
        return sha256(PROBE_LEDGER_DOMAIN + b":round:" + bencode(self.bvalue()))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    def bvalue(self) -> dict[bytes, BValue]:
        return {
            b"round_id": self.round_id,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"bootstrap_digest": self.bootstrap_digest,
            b"bootstrap_accept": 1 if self.bootstrap_accept else 0,
            b"live_probe_digests": self.live_probe_digests,
            b"absence_digest": self.absence_digest,
            b"absence_accept": 1 if self.absence_accept else 0,
            b"egress_digest": self.egress_digest,
            b"egress_accept": 1 if self.egress_accept else 0,
            b"positive_evidence": self.positive_evidence_digests,
            b"fast_window_winner": 1 if self.fast_window_winner else 0,
            b"note": self.note,
        }


@dataclass(frozen=True)
class ProbeLedgerPolicy:
    min_progress_rounds: int = 2
    min_source_families: int = 2
    min_path_families: int = 2
    max_absence_only_rounds: int = 1
    max_fast_family_share_numerator: int = 2
    max_fast_family_share_denominator: int = 3
    accept_with_watch_on_clean_skip: bool = True

    def validate(self) -> None:
        if self.min_progress_rounds <= 0 or self.min_source_families <= 0 or self.min_path_families <= 0:
            raise ValueError("probe ledger diversity thresholds must be positive")
        if self.max_absence_only_rounds < 0:
            raise ValueError("probe ledger absence threshold invalid")
        if self.max_fast_family_share_numerator <= 0 or self.max_fast_family_share_denominator <= 0:
            raise ValueError("probe ledger fast-family ratio invalid")
        if self.max_fast_family_share_numerator > self.max_fast_family_share_denominator:
            raise ValueError("probe ledger fast-family numerator cannot exceed denominator")


@dataclass(frozen=True)
class ProbeLedgerAssessment:
    decision_kind: ProbeLedgerDecisionKind
    accept: bool
    reason: str
    progress_round_count: int
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def assess_probe_ledger(
    rounds: Iterable[ProbeLedgerRound],
    *,
    now: int,
    policy: ProbeLedgerPolicy | None = None,
    previously_seen_round_digests: Iterable[bytes] = (),
) -> ProbeLedgerAssessment:
    policy = policy or ProbeLedgerPolicy()
    policy.validate()
    round_tuple = tuple(rounds)
    prior = set(previously_seen_round_digests)
    pressures: list[bytes] = []

    if any(not entry.live(now=now) for entry in round_tuple):
        pressures.extend(entry.round_digest for entry in round_tuple if not entry.live(now=now))
        return _assessment(ProbeLedgerDecisionKind.QUARANTINE_EXPIRED_ROUND, False, "probe ledger contains expired or future round evidence", round_tuple, pressures)

    seen: set[bytes] = set()
    replayed: list[bytes] = []
    for entry in round_tuple:
        digest = entry.round_digest
        if digest in seen or digest in prior:
            replayed.append(digest)
        seen.add(digest)
    if replayed:
        return _assessment(ProbeLedgerDecisionKind.QUARANTINE_REPLAYED_ROUND, False, "probe ledger round replayed in current or previous window", round_tuple, replayed)

    failed = [entry for entry in round_tuple if not entry.egress_accept]
    if failed:
        pressures.extend(entry.egress_digest for entry in failed)
        return _assessment(ProbeLedgerDecisionKind.QUARANTINE_BOOTSTRAP_FAILURE, False, "egress failure joined into probe ledger", round_tuple, pressures)

    negative_with_positive = [entry for entry in round_tuple if entry.absence_accept and entry.positive_evidence_digests]
    if negative_with_positive:
        pressures.extend(digest for entry in negative_with_positive for digest in entry.positive_evidence_digests)
        return _assessment(ProbeLedgerDecisionKind.QUARANTINE_NEGATIVE_CONTRADICTION, False, "absence-only pressure contradicted by positive evidence in the same window", round_tuple, pressures)

    absence_only_count = sum(1 for entry in round_tuple if entry.absence_only)
    if absence_only_count > policy.max_absence_only_rounds:
        pressures.extend(entry.absence_digest for entry in round_tuple if entry.absence_only)
        return _assessment(ProbeLedgerDecisionKind.QUARANTINE_ABSENCE_ONLY_LOOP, False, "repeated absence-only rounds would turn no-answer into sticky state", round_tuple, pressures)

    fast = [entry for entry in round_tuple if entry.fast_window_winner]
    if len(fast) >= policy.min_progress_rounds:
        counts: dict[str, int] = {}
        for entry in fast:
            counts[entry.source_family] = counts.get(entry.source_family, 0) + 1
        if any(count * policy.max_fast_family_share_denominator >= len(fast) * policy.max_fast_family_share_numerator for count in counts.values()):
            pressures.extend(entry.round_digest for entry in fast)
            return _assessment(ProbeLedgerDecisionKind.QUARANTINE_FAST_FAMILY_CAPTURE, False, "one family dominates repeated fast probe windows", round_tuple, pressures)

    progress = [entry for entry in round_tuple if entry.bootstrap_accept and entry.egress_accept and (entry.live_probe_count > 0 or policy.accept_with_watch_on_clean_skip)]
    if len(progress) < policy.min_progress_rounds:
        return _assessment(ProbeLedgerDecisionKind.CONTINUE_NEEDS_MORE_ROUNDS, False, "not enough positive bootstrap/probe rounds yet", round_tuple, pressures)
    source_families = {entry.source_family for entry in progress}
    if len(source_families) < policy.min_source_families:
        return _assessment(ProbeLedgerDecisionKind.CONTINUE_NEEDS_FAMILY_DIVERSITY, False, "positive rounds lack source-family diversity", round_tuple, pressures)
    path_families = {entry.path_family for entry in progress}
    if len(path_families) < policy.min_path_families:
        return _assessment(ProbeLedgerDecisionKind.CONTINUE_NEEDS_PATH_DIVERSITY, False, "positive rounds lack path-family diversity", round_tuple, pressures)
    if any(entry.live_probe_count == 0 for entry in progress):
        return _assessment(ProbeLedgerDecisionKind.ACCEPT_WITH_WATCH, True, "repeated rounds are diverse but include clean-skip/watch evidence", round_tuple, pressures)
    return _assessment(ProbeLedgerDecisionKind.ACCEPT_REPEATED_DIVERSE_PROGRESS, True, "repeated bootstrap/probe rounds are locally diverse and bounded", round_tuple, pressures)


def _assessment(kind: ProbeLedgerDecisionKind, accept: bool, reason: str, rounds: tuple[ProbeLedgerRound, ...], pressures: Iterable[bytes]) -> ProbeLedgerAssessment:
    progress = tuple(entry for entry in rounds if entry.bootstrap_accept and entry.egress_accept)
    source_families = tuple(sorted({entry.source_family for entry in progress}))
    path_families = tuple(sorted({entry.path_family for entry in progress}))
    pressure_tuple = tuple(sorted(pressures))
    digest = sha256(PROBE_LEDGER_DOMAIN + b":assessment:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"rounds": [entry.round_digest for entry in rounds],
        b"progress_count": len(progress),
        b"source_families": source_families,
        b"path_families": path_families,
        b"pressures": pressure_tuple,
    }))
    return ProbeLedgerAssessment(kind, accept, reason, len(progress), source_families, path_families, pressure_tuple, digest)
