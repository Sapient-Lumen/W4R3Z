"""Service handoff ledger for catalog successor transitions.

Garden service handoff is a high-risk continuation boundary: a retired catalog,
a successor catalog, and a few helpful witnesses can all be valid observations
while still being the wrong successor, one-family capture, replay, or a route
that lacks proof that the successor can actually serve.  This module keeps the
handoff tiny and local: it decides whether a handoff may be used, watched, or
quarantined; it does not elect a global successor.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .serviceepochledger import ServiceEpochLedgerDecisionKind, ServiceEpochLedgerReport

SERVICE_HANDOFF_LEDGER_DOMAIN = DOMAIN + b":service-handoff-ledger-v1:"
ZERO_DIGEST = b"\x00" * 32


class ServiceHandoffDecisionKind(str, Enum):
    ACCEPT_HANDOFF = "accept_handoff"
    ACCEPT_HANDOFF_WITH_WATCH = "accept_handoff_with_watch"
    HOLD_MISSING_PROOF = "hold_missing_proof"
    HOLD_INSUFFICIENT_DIVERSITY = "hold_insufficient_diversity"
    QUARANTINE_REPLAY = "quarantine_replay"
    QUARANTINE_DIGEST_MISMATCH = "quarantine_digest_mismatch"
    QUARANTINE_PREDECESSOR_NOT_RETIRED = "quarantine_predecessor_not_retired"
    QUARANTINE_SUCCESSOR_UNSTABLE = "quarantine_successor_unstable"
    QUARANTINE_WITNESS_FORK = "quarantine_witness_fork"
    QUARANTINE_ONE_FAMILY = "quarantine_one_family"
    QUARANTINE_EXPIRED_OR_FUTURE = "quarantine_expired_or_future"


@dataclass(frozen=True)
class ServiceHandoffWitness:
    witness_id: str
    family_id: str
    observed_at: int
    expires_at: int
    predecessor_catalog_digest: bytes
    successor_catalog_digest: bytes
    withdrawal_notice_digest: bytes
    route_report_digest: bytes = ZERO_DIGEST
    continuity_report_digest: bytes = ZERO_DIGEST
    fork_evidence_digest: bytes = ZERO_DIGEST

    def __post_init__(self) -> None:
        if not self.witness_id or len(self.witness_id.encode("utf-8")) > 80:
            raise ValueError("witness_id must be short and non-empty")
        if not self.family_id or len(self.family_id.encode("utf-8")) > 80:
            raise ValueError("family_id must be short and non-empty")
        if self.expires_at <= self.observed_at:
            raise ValueError("handoff witness expires_at must be after observed_at")
        for name, value in (
            ("predecessor_catalog_digest", self.predecessor_catalog_digest),
            ("successor_catalog_digest", self.successor_catalog_digest),
            ("withdrawal_notice_digest", self.withdrawal_notice_digest),
            ("route_report_digest", self.route_report_digest),
            ("continuity_report_digest", self.continuity_report_digest),
            ("fork_evidence_digest", self.fork_evidence_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @property
    def witness_digest(self) -> bytes:
        return sha256(SERVICE_HANDOFF_LEDGER_DOMAIN + b":witness:" + bencode(self.bvalue()))

    @property
    def has_route(self) -> bool:
        return self.route_report_digest != ZERO_DIGEST

    @property
    def has_fork(self) -> bool:
        return self.fork_evidence_digest != ZERO_DIGEST

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"witness": self.witness_id,
            b"family": self.family_id,
            b"observed_at": self.observed_at,
            b"expires_at": self.expires_at,
            b"predecessor": self.predecessor_catalog_digest,
            b"successor": self.successor_catalog_digest,
            b"withdrawal": self.withdrawal_notice_digest,
            b"route": self.route_report_digest,
            b"continuity": self.continuity_report_digest,
            b"fork": self.fork_evidence_digest,
        }


@dataclass(frozen=True)
class ServiceHandoffPolicy:
    min_witnesses: int = 3
    min_witness_families: int = 2
    require_route_proof: bool = True
    allow_watch_on_partial_successor: bool = True


@dataclass(frozen=True)
class ServiceHandoffReport:
    decision_kind: ServiceHandoffDecisionKind
    accept: bool
    reason: str
    predecessor_catalog_digest: bytes
    successor_catalog_digest: bytes
    witness_families: tuple[str, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")

    @property
    def watch_only(self) -> bool:
        return self.decision_kind is ServiceHandoffDecisionKind.ACCEPT_HANDOFF_WITH_WATCH


def _report(kind: ServiceHandoffDecisionKind, accept: bool, reason: str, *, predecessor: bytes, successor: bytes, witnesses: tuple[ServiceHandoffWitness, ...], pressures: Iterable[bytes] = ()) -> ServiceHandoffReport:
    families = tuple(sorted({w.family_id for w in witnesses}))
    pressure_t = tuple(sorted(set(pressures) | {w.witness_digest for w in witnesses if w.has_fork}))
    digest = sha256(SERVICE_HANDOFF_LEDGER_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"reason": reason,
        b"predecessor": predecessor,
        b"successor": successor,
        b"witnesses": [w.bvalue() for w in sorted(witnesses, key=lambda item: item.witness_digest)],
        b"pressures": list(pressure_t),
    }))
    return ServiceHandoffReport(kind, accept, reason, predecessor, successor, families, pressure_t, digest)


def assess_service_handoff(
    witnesses: Iterable[ServiceHandoffWitness],
    *,
    now: int,
    predecessor_catalog_digest: bytes,
    successor_catalog_digest: bytes,
    withdrawal_notice_digest: bytes,
    predecessor_retired: bool,
    successor_epoch_report: ServiceEpochLedgerReport | None,
    policy: ServiceHandoffPolicy | None = None,
    previously_seen_witnesses: Iterable[bytes] = (),
) -> ServiceHandoffReport:
    policy = policy or ServiceHandoffPolicy()
    witness_t = tuple(witnesses)
    seen = set(previously_seen_witnesses)
    if any(w.witness_digest in seen for w in witness_t):
        return _report(ServiceHandoffDecisionKind.QUARANTINE_REPLAY, False, "replayed handoff witness", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if any(w.observed_at > now or w.expires_at <= now for w in witness_t):
        return _report(ServiceHandoffDecisionKind.QUARANTINE_EXPIRED_OR_FUTURE, False, "handoff witness outside local time window", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if any(w.predecessor_catalog_digest != predecessor_catalog_digest or w.successor_catalog_digest != successor_catalog_digest or w.withdrawal_notice_digest != withdrawal_notice_digest for w in witness_t):
        return _report(ServiceHandoffDecisionKind.QUARANTINE_DIGEST_MISMATCH, False, "handoff witness digest mismatch", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if any(w.has_fork for w in witness_t):
        return _report(ServiceHandoffDecisionKind.QUARANTINE_WITNESS_FORK, False, "handoff fork evidence observed", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if not predecessor_retired:
        return _report(ServiceHandoffDecisionKind.QUARANTINE_PREDECESSOR_NOT_RETIRED, False, "predecessor catalog not locally retired", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if len(witness_t) < policy.min_witnesses:
        return _report(ServiceHandoffDecisionKind.HOLD_MISSING_PROOF, False, "not enough handoff witnesses", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    families = {w.family_id for w in witness_t}
    if len(families) == 1:
        return _report(ServiceHandoffDecisionKind.QUARANTINE_ONE_FAMILY, False, "one-family handoff witness capture", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if len(families) < policy.min_witness_families:
        return _report(ServiceHandoffDecisionKind.HOLD_INSUFFICIENT_DIVERSITY, False, "insufficient handoff witness diversity", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if policy.require_route_proof and not any(w.has_route for w in witness_t):
        return _report(ServiceHandoffDecisionKind.HOLD_MISSING_PROOF, False, "handoff lacks successor route proof", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if successor_epoch_report is None or successor_epoch_report.quarantined:
        return _report(ServiceHandoffDecisionKind.QUARANTINE_SUCCESSOR_UNSTABLE, False, "successor continuity report is missing or quarantined", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if successor_epoch_report.accept and successor_epoch_report.decision_kind is ServiceEpochLedgerDecisionKind.ACCEPT_STABLE_SERVICE:
        return _report(ServiceHandoffDecisionKind.ACCEPT_HANDOFF, True, "stable successor handoff", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t)
    if policy.allow_watch_on_partial_successor and successor_epoch_report.accept:
        return _report(ServiceHandoffDecisionKind.ACCEPT_HANDOFF_WITH_WATCH, True, "successor handoff accepted with watch", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t, pressures=(successor_epoch_report.report_digest,))
    return _report(ServiceHandoffDecisionKind.HOLD_MISSING_PROOF, False, "successor service continuity not yet strong enough", predecessor=predecessor_catalog_digest, successor=successor_catalog_digest, witnesses=witness_t, pressures=(successor_epoch_report.report_digest if successor_epoch_report else ZERO_DIGEST,))
