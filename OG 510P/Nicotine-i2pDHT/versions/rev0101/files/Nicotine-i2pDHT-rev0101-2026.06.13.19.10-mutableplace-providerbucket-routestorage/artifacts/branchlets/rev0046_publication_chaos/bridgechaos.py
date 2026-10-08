"""Repeated public bridge epoch/announcement replay pressure.

A one-shot bridge epoch or shadow-fire gate can look safe while repeated restarts
keep reintroducing stale public announcements, one-family refreshes, or epoch
forks. This module is a deterministic chaos ledger for that local repeated-round
pressure. It does not model the network; it models the evidence shape we want to
preserve before live transport.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

BRIDGE_CHAOS_DOMAIN = DOMAIN + b":bridge-chaos-v1:"


class BridgeChaosSignalKind(str, Enum):
    EPOCH_ACCEPTED = "epoch_accepted"
    SHADOW_FIRE_ACCEPTED = "shadow_fire_accepted"
    STALE_ANNOUNCEMENT_SEEN = "stale_announcement_seen"
    WITHDRAWAL_SEEN = "withdrawal_seen"
    REPAIR_SEEN = "repair_seen"
    HARD_NEGATIVE_SEEN = "hard_negative_seen"


class BridgeChaosDecisionKind(str, Enum):
    ACCEPT_STABLE_BRIDGE_WINDOW = "accept_stable_bridge_window"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_MORE_ROUNDS = "continue_more_rounds"
    HOLD_REPAIR_NOT_OBSERVED = "hold_repair_not_observed"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_REPLAYED_ROUND = "quarantine_replayed_round"
    QUARANTINE_EPOCH_FORK = "quarantine_epoch_fork"
    QUARANTINE_STALE_REPLAY_LOOP = "quarantine_stale_replay_loop"
    QUARANTINE_HARD_NEGATIVE = "quarantine_hard_negative"
    QUARANTINE_STALE_AFTER_WITHDRAWAL = "quarantine_stale_after_withdrawal"


@dataclass(frozen=True)
class BridgeChaosObservation:
    round_id: int
    kind: BridgeChaosSignalKind
    profile_id: str
    service_name: str
    epoch_sequence: int
    epoch_digest: bytes
    announcement_digest: bytes
    family_id: str
    path_family: str
    accepted: bool = True

    def __post_init__(self) -> None:
        if self.round_id < 0 or self.epoch_sequence < 0:
            raise ValueError("round and epoch sequence must be non-negative")
        for name, value in (("epoch_digest", self.epoch_digest), ("announcement_digest", self.announcement_digest)):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")
        if not self.profile_id or not self.service_name or not self.family_id or not self.path_family:
            raise ValueError("ids/families must be non-empty")
        object.__setattr__(self, "kind", BridgeChaosSignalKind(self.kind))

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"round": self.round_id,
            b"kind": self.kind.value,
            b"profile": self.profile_id,
            b"service": self.service_name,
            b"epoch_seq": self.epoch_sequence,
            b"epoch": self.epoch_digest,
            b"announcement": self.announcement_digest,
            b"family": self.family_id,
            b"path_family": self.path_family,
            b"accepted": 1 if self.accepted else 0,
        }

    @property
    def observation_digest(self) -> bytes:
        return sha256(BRIDGE_CHAOS_DOMAIN + b":observation:" + bencode(self.bvalue()))


@dataclass(frozen=True)
class BridgeChaosPolicy:
    min_rounds: int = 3
    min_family_diversity: int = 3
    min_path_diversity: int = 2
    max_stale_rounds_without_repair: int = 1
    allow_watch_without_repair: bool = False


@dataclass(frozen=True)
class BridgeChaosReport:
    decision_kind: BridgeChaosDecisionKind
    accepted: bool
    reason: str
    profile_id: str
    service_name: str
    rounds_seen: tuple[int, ...]
    family_count: int
    path_family_count: int
    stale_count: int
    repair_count: int
    observation_digests: tuple[bytes, ...]
    watch: bool
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: BridgeChaosDecisionKind, accepted: bool, reason: str, *, observations: tuple[BridgeChaosObservation, ...], profile_id: str, service_name: str, watch: bool = False) -> BridgeChaosReport:
    rounds = tuple(sorted({item.round_id for item in observations}))
    families = {item.family_id for item in observations if item.accepted}
    paths = {item.path_family for item in observations if item.accepted}
    stale_count = sum(1 for item in observations if item.kind is BridgeChaosSignalKind.STALE_ANNOUNCEMENT_SEEN)
    repair_count = sum(1 for item in observations if item.kind is BridgeChaosSignalKind.REPAIR_SEEN)
    digests = tuple(sorted(item.observation_digest for item in observations))
    digest = sha256(BRIDGE_CHAOS_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accepted": 1 if accepted else 0,
        b"reason": reason,
        b"profile": profile_id,
        b"service": service_name,
        b"rounds": list(rounds),
        b"families": len(families),
        b"paths": len(paths),
        b"stale": stale_count,
        b"repair": repair_count,
        b"observations": list(digests),
        b"watch": 1 if watch else 0,
    }))
    return BridgeChaosReport(kind, accepted, reason, profile_id, service_name, rounds, len(families), len(paths), stale_count, repair_count, digests, watch, digest)


def assess_bridge_chaos(observations: Iterable[BridgeChaosObservation], *, expected_profile_id: str, expected_service_name: str, policy: BridgeChaosPolicy = BridgeChaosPolicy(), previously_seen_round_digests: Iterable[bytes] = ()) -> BridgeChaosReport:
    obs = tuple(observations)
    seen_rounds = set(previously_seen_round_digests)
    if not obs:
        return _report(BridgeChaosDecisionKind.CONTINUE_MORE_ROUNDS, False, "no observations yet", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
    for item in obs:
        if item.profile_id != expected_profile_id or item.service_name != expected_service_name:
            return _report(BridgeChaosDecisionKind.QUARANTINE_REPLAYED_ROUND, False, "profile/service drift in chaos observations", observations=(item,), profile_id=expected_profile_id, service_name=expected_service_name)
        if item.observation_digest in seen_rounds:
            return _report(BridgeChaosDecisionKind.QUARANTINE_REPLAYED_ROUND, False, "replayed chaos observation", observations=(item,), profile_id=expected_profile_id, service_name=expected_service_name)
    by_seq: dict[int, bytes] = {}
    for item in obs:
        if item.kind in {BridgeChaosSignalKind.EPOCH_ACCEPTED, BridgeChaosSignalKind.SHADOW_FIRE_ACCEPTED}:
            prior = by_seq.get(item.epoch_sequence)
            if prior is not None and prior != item.epoch_digest:
                return _report(BridgeChaosDecisionKind.QUARANTINE_EPOCH_FORK, False, "same epoch sequence forked across repeated rounds", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
            by_seq[item.epoch_sequence] = item.epoch_digest
    if any(item.kind is BridgeChaosSignalKind.HARD_NEGATIVE_SEEN for item in obs):
        return _report(BridgeChaosDecisionKind.QUARANTINE_HARD_NEGATIVE, False, "hard negative seen during bridge chaos rounds", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
    withdrawals = {item.announcement_digest for item in obs if item.kind is BridgeChaosSignalKind.WITHDRAWAL_SEEN}
    if any(item.kind is BridgeChaosSignalKind.STALE_ANNOUNCEMENT_SEEN and item.announcement_digest in withdrawals for item in obs):
        return _report(BridgeChaosDecisionKind.QUARANTINE_STALE_AFTER_WITHDRAWAL, False, "stale public announcement replayed after withdrawal", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
    rounds = {item.round_id for item in obs}
    if len(rounds) < policy.min_rounds:
        return _report(BridgeChaosDecisionKind.CONTINUE_MORE_ROUNDS, False, "not enough repeated rounds", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
    families = {item.family_id for item in obs if item.accepted}
    paths = {item.path_family for item in obs if item.accepted}
    if len(families) < policy.min_family_diversity:
        return _report(BridgeChaosDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, "bridge chaos rounds lack family diversity", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
    if len(paths) < policy.min_path_diversity:
        return _report(BridgeChaosDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, "bridge chaos rounds lack path diversity", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
    stale_count = sum(1 for item in obs if item.kind is BridgeChaosSignalKind.STALE_ANNOUNCEMENT_SEEN)
    repair_count = sum(1 for item in obs if item.kind is BridgeChaosSignalKind.REPAIR_SEEN)
    if stale_count > policy.max_stale_rounds_without_repair and repair_count == 0:
        return _report(BridgeChaosDecisionKind.QUARANTINE_STALE_REPLAY_LOOP, False, "stale public announcement repeated without repair", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
    if stale_count and repair_count == 0:
        if policy.allow_watch_without_repair:
            return _report(BridgeChaosDecisionKind.ACCEPT_WITH_WATCH, True, "stable enough but stale pressure remains unrepaired", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name, watch=True)
        return _report(BridgeChaosDecisionKind.HOLD_REPAIR_NOT_OBSERVED, False, "stale announcement observed but repair not observed", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name, watch=True)
    return _report(BridgeChaosDecisionKind.ACCEPT_STABLE_BRIDGE_WINDOW, True, "repeated bridge rounds are diverse and not replay-poisoned", observations=obs, profile_id=expected_profile_id, service_name=expected_service_name)
