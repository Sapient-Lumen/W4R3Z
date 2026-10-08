"""Joined scope ledger for sticky entrance and repair decisions.

rev0032 turns a repeated bug class into a first-class test surface: a scope
fence can pass, a probe ledger can pass, and obligation evidence can be good,
while the *join* between those reports is still unsafe.  This module stores a
small signed observation that binds the exact scope/object/request/purpose to
report digests and then asks whether the joined window is diverse, monotonic,
non-replayed, and not quietly carrying proof debt.

It is deliberately local memory.  It does not decide global truth.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .obligationdebt import ObligationDebtReport
from .probeledger import ProbeLedgerAssessment
from .scopefence import ScopeFenceReport, ScopePurpose

SCOPE_LEDGER_DOMAIN = DOMAIN + b":scope-ledger-v1:"
ZERO_DIGEST = b"\x00" * 32


class ScopeLedgerDecisionKind(str, Enum):
    ACCEPT_STICKY_SCOPE_ADVANCE = "accept_sticky_scope_advance"
    ACCEPT_WITH_PROOF_DEBT = "accept_with_proof_debt"
    HOLD_NEED_MORE_SOURCE_DIVERSITY = "hold_need_more_source_diversity"
    HOLD_NEED_MORE_PATH_DIVERSITY = "hold_need_more_path_diversity"
    HOLD_OPEN_OBLIGATIONS = "hold_open_obligations"
    QUARANTINE_SCOPE_FENCE = "quarantine_scope_fence"
    QUARANTINE_PROBE_LEDGER = "quarantine_probe_ledger"
    QUARANTINE_OBLIGATION_REPORT = "quarantine_obligation_report"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"
    QUARANTINE_OBJECT_MISMATCH = "quarantine_object_mismatch"
    QUARANTINE_REQUEST_MISMATCH = "quarantine_request_mismatch"
    QUARANTINE_PURPOSE_MIX = "quarantine_purpose_mix"
    QUARANTINE_REPLAYED_OBSERVATION = "quarantine_replayed_observation"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_EXPIRED_OBSERVATION = "quarantine_expired_observation"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"


@dataclass(frozen=True)
class ScopeLedgerPolicy:
    min_observations: int = 2
    min_source_families: int = 2
    min_path_families: int = 2
    max_open_obligations_for_watch: int = 0
    allow_accept_with_debt: bool = False

    def validate(self) -> None:
        if self.min_observations <= 0 or self.min_source_families <= 0 or self.min_path_families <= 0:
            raise ValueError("scope ledger diversity thresholds must be positive")
        if self.max_open_obligations_for_watch < 0:
            raise ValueError("scope ledger open-obligation allowance must be non-negative")


@dataclass(frozen=True)
class ScopeLedgerObservation:
    actor_public_key: bytes
    scope_id: bytes
    object_digest: bytes
    request_id: bytes
    purpose: ScopePurpose
    source_family: str
    path_family: str
    sequence: int
    issued_at: int
    expires_at: int
    scope_report_digest: bytes
    scope_report_accept: bool
    probe_report_digest: bytes
    probe_report_accept: bool
    obligation_report_digest: bytes = ZERO_DIGEST
    open_obligation_count: int = 0
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("actor_public_key", self.actor_public_key),
            ("scope_id", self.scope_id),
            ("object_digest", self.object_digest),
            ("request_id", self.request_id),
            ("scope_report_digest", self.scope_report_digest),
            ("probe_report_digest", self.probe_report_digest),
            ("obligation_report_digest", self.obligation_report_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"scope ledger {name} must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("scope ledger observation needs source/path families")
        if self.sequence < 0 or self.open_obligation_count < 0:
            raise ValueError("scope ledger counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("scope ledger observation expiry must follow issue time")
        if self.signature and len(self.signature) != 64:
            raise ValueError("scope ledger signature must be empty or 64 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        scope_id: bytes,
        object_digest: bytes,
        request_id: bytes,
        purpose: ScopePurpose,
        source_family: str,
        path_family: str,
        sequence: int,
        issued_at: int,
        ttl: int,
        scope_report: ScopeFenceReport,
        probe_report: ProbeLedgerAssessment,
        obligation_report: ObligationDebtReport | None = None,
        note: str = "",
    ) -> "ScopeLedgerObservation":
        if ttl <= 0:
            raise ValueError("scope ledger ttl must be positive")
        unsigned = cls(
            actor_public_key=keypair.public_key_bytes,
            scope_id=scope_id,
            object_digest=object_digest,
            request_id=request_id,
            purpose=purpose,
            source_family=source_family,
            path_family=path_family,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            scope_report_digest=scope_report.report_digest,
            scope_report_accept=scope_report.accept,
            probe_report_digest=probe_report.report_digest,
            probe_report_accept=probe_report.accept and not probe_report.quarantined,
            obligation_report_digest=ZERO_DIGEST if obligation_report is None else obligation_report.report_digest,
            open_obligation_count=0 if obligation_report is None else len(obligation_report.open_obligation_digests),
            note=note[:160],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    @property
    def observation_digest(self) -> bytes:
        return sha256(SCOPE_LEDGER_DOMAIN + b":observation:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"actor": self.actor_public_key,
            b"scope": self.scope_id,
            b"object": self.object_digest,
            b"request": self.request_id,
            b"purpose": self.purpose.value,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"scope_report": self.scope_report_digest,
            b"scope_accept": 1 if self.scope_report_accept else 0,
            b"probe_report": self.probe_report_digest,
            b"probe_accept": 1 if self.probe_report_accept else 0,
            b"obligation_report": self.obligation_report_digest,
            b"open_obligations": self.open_obligation_count,
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return SCOPE_LEDGER_DOMAIN + b":observation-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.actor_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class ScopeLedgerReport:
    decision_kind: ScopeLedgerDecisionKind
    accept: bool
    reason: str
    observation_digests: tuple[bytes, ...]
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    open_obligation_count: int
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: ScopeLedgerDecisionKind, accept: bool, reason: str, observations: tuple[ScopeLedgerObservation, ...], pressures: Iterable[bytes] = ()) -> ScopeLedgerReport:
    obs_digests = tuple(sorted({item.observation_digest for item in observations}))
    source_families = tuple(sorted({item.source_family for item in observations}))
    path_families = tuple(sorted({item.path_family for item in observations}))
    pressure_t = tuple(sorted(set(pressures)))
    open_count = sum(item.open_obligation_count for item in observations)
    digest = sha256(SCOPE_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"observations": list(obs_digests),
        b"source_families": list(source_families),
        b"path_families": list(path_families),
        b"open": open_count,
        b"pressures": list(pressure_t),
        b"reason": reason,
    }))
    return ScopeLedgerReport(kind, accept, reason, obs_digests, source_families, path_families, open_count, pressure_t, digest)


def assess_scope_ledger(
    observations: Iterable[ScopeLedgerObservation],
    *,
    expected_scope_id: bytes,
    expected_object_digest: bytes,
    expected_request_id: bytes,
    expected_purpose: ScopePurpose,
    now: int,
    policy: ScopeLedgerPolicy | None = None,
    previously_seen_observation_digests: Iterable[bytes] = (),
) -> ScopeLedgerReport:
    policy = policy or ScopeLedgerPolicy()
    policy.validate()
    obs = tuple(observations)
    if not obs:
        return _report(ScopeLedgerDecisionKind.EMPTY_NO_OBSERVATIONS, False, "no joined scope observations supplied", obs)

    prior = set(previously_seen_observation_digests)
    seen: set[bytes] = set()
    actor_seq: dict[tuple[bytes, int], bytes] = {}
    for item in obs:
        digest = item.observation_digest
        if digest in seen or digest in prior:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_REPLAYED_OBSERVATION, False, "joined scope observation was replayed", obs, (digest,))
        seen.add(digest)
        fork_key = (item.actor_public_key, item.sequence)
        if fork_key in actor_seq and actor_seq[fork_key] != digest:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "same actor emitted two different scope-ledger observations at one sequence", obs, (actor_seq[fork_key], digest))
        actor_seq[fork_key] = digest
        if not item.live(now=now):
            return _report(ScopeLedgerDecisionKind.QUARANTINE_EXPIRED_OBSERVATION, False, "scope-ledger observation expired or from the future", obs, (digest,))
        if not item.verify():
            return _report(ScopeLedgerDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "scope-ledger observation signature failed", obs, (digest,))
        if item.scope_id != expected_scope_id:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_SCOPE_MISMATCH, False, "joined observation scope id does not match caller expectation", obs, (digest,))
        if item.object_digest != expected_object_digest:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_OBJECT_MISMATCH, False, "joined observation object digest does not match caller expectation", obs, (digest,))
        if item.request_id != expected_request_id:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_REQUEST_MISMATCH, False, "joined observation request id does not match caller expectation", obs, (digest,))
        if item.purpose is not expected_purpose:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_PURPOSE_MIX, False, "joined observation purpose does not match caller expectation", obs, (digest,))
        if not item.scope_report_accept:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_SCOPE_FENCE, False, "scope fence did not accept, so joined ledger cannot advance", obs, (item.scope_report_digest,))
        if not item.probe_report_accept:
            return _report(ScopeLedgerDecisionKind.QUARANTINE_PROBE_LEDGER, False, "probe ledger did not accept, so joined ledger cannot advance", obs, (item.probe_report_digest,))

    if len(obs) < policy.min_observations:
        return _report(ScopeLedgerDecisionKind.HOLD_NEED_MORE_SOURCE_DIVERSITY, False, "not enough joined observations for sticky advance", obs)
    if len({item.source_family for item in obs}) < policy.min_source_families:
        return _report(ScopeLedgerDecisionKind.HOLD_NEED_MORE_SOURCE_DIVERSITY, False, "joined scope observations lack source-family diversity", obs)
    if len({item.path_family for item in obs}) < policy.min_path_families:
        return _report(ScopeLedgerDecisionKind.HOLD_NEED_MORE_PATH_DIVERSITY, False, "joined scope observations lack path-family diversity", obs)

    open_count = sum(item.open_obligation_count for item in obs)
    if open_count:
        if policy.allow_accept_with_debt and open_count <= policy.max_open_obligations_for_watch:
            return _report(ScopeLedgerDecisionKind.ACCEPT_WITH_PROOF_DEBT, True, "sticky scope advances but leaves explicit proof-obligation debt", obs)
        return _report(ScopeLedgerDecisionKind.HOLD_OPEN_OBLIGATIONS, False, "joined scope observations still carry open proof obligations", obs)

    return _report(ScopeLedgerDecisionKind.ACCEPT_STICKY_SCOPE_ADVANCE, True, "scope/probe/obligation reports are joined, diverse, fresh, and monotonic", obs)
