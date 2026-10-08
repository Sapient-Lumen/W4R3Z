"""Store-debt ledger joining replica, custody, tombstone, and repair pressure.

A DHT can accumulate many individually-valid store facts: accepted leases,
custody proofs, useful refusals, tombstones, and repair plans.  rev0032 adds a
small signed store-debt observation so restart/retry code cannot treat one
convenient fact as enough to suppress repair or resurrect stale storage.

The ledger is not a storage consensus protocol.  It is local repair pressure.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable

from .bencode import BValue, bencode
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .storerepair import StoreRepairActionKind, StoreRepairPlan

STORE_DEBT_DOMAIN = DOMAIN + b":store-debt-v1:"
ZERO_DIGEST = b"\x00" * 32


class StoreDebtDecisionKind(str, Enum):
    ACCEPT_NO_STORE_DEBT = "accept_no_store_debt"
    PLAN_REPAIR_REPLICAS = "plan_repair_replicas"
    PLAN_CUSTODY_AUDIT = "plan_custody_audit"
    HOLD_USEFUL_REFUSAL_BACKOFF = "hold_useful_refusal_backoff"
    HOLD_NEED_FAMILY_DIVERSITY = "hold_need_family_diversity"
    QUARANTINE_REPAIR_PLAN = "quarantine_repair_plan"
    QUARANTINE_LIVE_TOMBSTONE = "quarantine_live_tombstone"
    QUARANTINE_SCOPE_MISMATCH = "quarantine_scope_mismatch"
    QUARANTINE_TARGET_MISMATCH = "quarantine_target_mismatch"
    QUARANTINE_RECORD_MISMATCH = "quarantine_record_mismatch"
    QUARANTINE_REPLAYED_OBSERVATION = "quarantine_replayed_observation"
    QUARANTINE_SEQUENCE_FORK = "quarantine_sequence_fork"
    QUARANTINE_BAD_SIGNATURE = "quarantine_bad_signature"
    QUARANTINE_EXPIRED_OBSERVATION = "quarantine_expired_observation"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"


@dataclass(frozen=True)
class StoreDebtPolicy:
    min_replica_receipts: int = 3
    min_custody_proofs: int = 2
    min_families: int = 2
    allow_renew_soon_as_debt: bool = True

    def validate(self) -> None:
        if self.min_replica_receipts <= 0 or self.min_custody_proofs <= 0 or self.min_families <= 0:
            raise ValueError("store debt thresholds must be positive")


@dataclass(frozen=True)
class StoreDebtObservation:
    actor_public_key: bytes
    scope_digest: bytes
    target: bytes
    record_digest: bytes
    source_family: str
    path_family: str
    sequence: int
    issued_at: int
    expires_at: int
    repair_action: StoreRepairActionKind
    repair_plan_digest: bytes
    accepted_replica_count: int
    custody_proof_count: int
    store_report_digest: bytes = ZERO_DIGEST
    custody_report_digest: bytes = ZERO_DIGEST
    tombstone_digests: tuple[bytes, ...] = ()
    note: str = ""
    signature: bytes = b""

    def __post_init__(self) -> None:
        for name, value in (
            ("actor_public_key", self.actor_public_key),
            ("scope_digest", self.scope_digest),
            ("target", self.target),
            ("record_digest", self.record_digest),
            ("repair_plan_digest", self.repair_plan_digest),
            ("store_report_digest", self.store_report_digest),
            ("custody_report_digest", self.custody_report_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"store debt {name} must be 32 bytes")
        if any(len(item) != 32 for item in self.tombstone_digests):
            raise ValueError("store debt tombstone digests must be 32 bytes")
        if not self.source_family or not self.path_family:
            raise ValueError("store debt observation needs source/path families")
        if self.sequence < 0 or self.accepted_replica_count < 0 or self.custody_proof_count < 0:
            raise ValueError("store debt counters must be non-negative")
        if self.expires_at <= self.issued_at:
            raise ValueError("store debt observation expiry must follow issue time")
        if self.signature and len(self.signature) != 64:
            raise ValueError("store debt signature must be empty or 64 bytes")

    @classmethod
    def create(
        cls,
        *,
        keypair: DhtKeypair,
        scope_digest: bytes,
        target: bytes,
        record_digest: bytes,
        source_family: str,
        path_family: str,
        sequence: int,
        issued_at: int,
        ttl: int,
        repair_plan: StoreRepairPlan,
        accepted_replica_count: int,
        custody_proof_count: int,
        store_report_digest: bytes = ZERO_DIGEST,
        custody_report_digest: bytes = ZERO_DIGEST,
        tombstone_digests: Iterable[bytes] = (),
        note: str = "",
    ) -> "StoreDebtObservation":
        if ttl <= 0:
            raise ValueError("store debt ttl must be positive")
        unsigned = cls(
            actor_public_key=keypair.public_key_bytes,
            scope_digest=scope_digest,
            target=target,
            record_digest=record_digest,
            source_family=source_family,
            path_family=path_family,
            sequence=sequence,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
            repair_action=repair_plan.action,
            repair_plan_digest=repair_plan.digest,
            accepted_replica_count=accepted_replica_count,
            custody_proof_count=custody_proof_count,
            store_report_digest=store_report_digest,
            custody_report_digest=custody_report_digest,
            tombstone_digests=tuple(sorted(tombstone_digests)),
            note=note[:160],
        )
        return replace(unsigned, signature=keypair.sign(unsigned.unsigned_payload()))

    def live(self, *, now: int) -> bool:
        return self.issued_at <= now < self.expires_at

    @property
    def observation_digest(self) -> bytes:
        return sha256(STORE_DEBT_DOMAIN + b":observation:" + self.unsigned_payload() + self.signature)

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"actor": self.actor_public_key,
            b"scope": self.scope_digest,
            b"target": self.target,
            b"record": self.record_digest,
            b"source_family": self.source_family,
            b"path_family": self.path_family,
            b"sequence": self.sequence,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
            b"repair_action": self.repair_action.value,
            b"repair_plan": self.repair_plan_digest,
            b"replicas": self.accepted_replica_count,
            b"custody": self.custody_proof_count,
            b"store_report": self.store_report_digest,
            b"custody_report": self.custody_report_digest,
            b"tombstones": list(self.tombstone_digests),
            b"note": self.note,
        }

    def unsigned_payload(self) -> bytes:
        return STORE_DEBT_DOMAIN + b":observation-unsigned:" + bencode(self.unsigned_bvalue())

    def verify(self) -> bool:
        return verify_signature(self.actor_public_key, self.unsigned_payload(), self.signature)


@dataclass(frozen=True)
class StoreDebtReport:
    decision_kind: StoreDebtDecisionKind
    accept: bool
    reason: str
    observation_digests: tuple[bytes, ...]
    source_families: tuple[str, ...]
    path_families: tuple[str, ...]
    max_replica_count: int
    max_custody_count: int
    tombstone_digests: tuple[bytes, ...]
    pressure_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _report(kind: StoreDebtDecisionKind, accept: bool, reason: str, observations: tuple[StoreDebtObservation, ...], pressures: Iterable[bytes] = ()) -> StoreDebtReport:
    obs_digests = tuple(sorted({item.observation_digest for item in observations}))
    source_families = tuple(sorted({item.source_family for item in observations}))
    path_families = tuple(sorted({item.path_family for item in observations}))
    tombstones = tuple(sorted({digest for item in observations for digest in item.tombstone_digests}))
    pressure_t = tuple(sorted(set(pressures)))
    max_replica = max((item.accepted_replica_count for item in observations), default=0)
    max_custody = max((item.custody_proof_count for item in observations), default=0)
    digest = sha256(STORE_DEBT_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"observations": list(obs_digests),
        b"source_families": list(source_families),
        b"path_families": list(path_families),
        b"replicas": max_replica,
        b"custody": max_custody,
        b"tombstones": list(tombstones),
        b"pressures": list(pressure_t),
        b"reason": reason,
    }))
    return StoreDebtReport(kind, accept, reason, obs_digests, source_families, path_families, max_replica, max_custody, tombstones, pressure_t, digest)


def assess_store_debt(
    observations: Iterable[StoreDebtObservation],
    *,
    expected_scope_digest: bytes,
    expected_target: bytes,
    expected_record_digest: bytes,
    now: int,
    policy: StoreDebtPolicy | None = None,
    previously_seen_observation_digests: Iterable[bytes] = (),
) -> StoreDebtReport:
    policy = policy or StoreDebtPolicy()
    policy.validate()
    obs = tuple(observations)
    if not obs:
        return _report(StoreDebtDecisionKind.EMPTY_NO_OBSERVATIONS, False, "no store-debt observations supplied", obs)

    prior = set(previously_seen_observation_digests)
    seen: set[bytes] = set()
    actor_seq: dict[tuple[bytes, int], bytes] = {}
    for item in obs:
        digest = item.observation_digest
        if digest in seen or digest in prior:
            return _report(StoreDebtDecisionKind.QUARANTINE_REPLAYED_OBSERVATION, False, "store-debt observation replayed", obs, (digest,))
        seen.add(digest)
        fork_key = (item.actor_public_key, item.sequence)
        if fork_key in actor_seq and actor_seq[fork_key] != digest:
            return _report(StoreDebtDecisionKind.QUARANTINE_SEQUENCE_FORK, False, "store-debt observation forked at one actor sequence", obs, (actor_seq[fork_key], digest))
        actor_seq[fork_key] = digest
        if not item.live(now=now):
            return _report(StoreDebtDecisionKind.QUARANTINE_EXPIRED_OBSERVATION, False, "store-debt observation expired or future-dated", obs, (digest,))
        if not item.verify():
            return _report(StoreDebtDecisionKind.QUARANTINE_BAD_SIGNATURE, False, "store-debt observation signature failed", obs, (digest,))
        if item.scope_digest != expected_scope_digest:
            return _report(StoreDebtDecisionKind.QUARANTINE_SCOPE_MISMATCH, False, "store-debt scope digest does not match expected scope", obs, (digest,))
        if item.target != expected_target:
            return _report(StoreDebtDecisionKind.QUARANTINE_TARGET_MISMATCH, False, "store-debt target does not match expected target", obs, (digest,))
        if item.record_digest != expected_record_digest:
            return _report(StoreDebtDecisionKind.QUARANTINE_RECORD_MISMATCH, False, "store-debt record digest does not match expected record", obs, (digest,))

    tombstones = tuple(sorted({digest for item in obs for digest in item.tombstone_digests}))
    if tombstones:
        return _report(StoreDebtDecisionKind.QUARANTINE_LIVE_TOMBSTONE, False, "live tombstone pressure blocks store acceptance and repair suppression", obs, tombstones)
    if any(item.repair_action is StoreRepairActionKind.QUARANTINE_RECORD for item in obs):
        return _report(StoreDebtDecisionKind.QUARANTINE_REPAIR_PLAN, False, "repair planner already quarantined the record", obs, (item.repair_plan_digest for item in obs if item.repair_action is StoreRepairActionKind.QUARANTINE_RECORD))
    if any(item.repair_action is StoreRepairActionKind.HOLD_FOR_BACKOFF for item in obs):
        return _report(StoreDebtDecisionKind.HOLD_USEFUL_REFUSAL_BACKOFF, False, "useful refusals create repair backoff debt", obs)
    if len({item.source_family for item in obs}) < policy.min_families or len({item.path_family for item in obs}) < policy.min_families:
        return _report(StoreDebtDecisionKind.HOLD_NEED_FAMILY_DIVERSITY, False, "store-debt observations lack source/path-family diversity", obs)
    max_replica = max(item.accepted_replica_count for item in obs)
    max_custody = max(item.custody_proof_count for item in obs)
    if max_replica < policy.min_replica_receipts or any(item.repair_action is StoreRepairActionKind.CAST_TO_RESERVES for item in obs):
        return _report(StoreDebtDecisionKind.PLAN_REPAIR_REPLICAS, False, "replica receipts are below local durability threshold or repair wants reserves", obs)
    if max_custody < policy.min_custody_proofs or any(item.repair_action is StoreRepairActionKind.RENEW_SOON for item in obs):
        if any(item.repair_action is StoreRepairActionKind.RENEW_SOON for item in obs) and policy.allow_renew_soon_as_debt:
            return _report(StoreDebtDecisionKind.PLAN_CUSTODY_AUDIT, False, "leases are near renewal; custody/renewal debt remains", obs)
        return _report(StoreDebtDecisionKind.PLAN_CUSTODY_AUDIT, False, "custody proofs are below local audit threshold", obs)
    if any(item.repair_action is StoreRepairActionKind.ASK_GARDEN_SENTINELS for item in obs):
        return _report(StoreDebtDecisionKind.HOLD_NEED_FAMILY_DIVERSITY, False, "repair planner requested garden sentinel family diversity", obs)
    return _report(StoreDebtDecisionKind.ACCEPT_NO_STORE_DEBT, True, "store evidence is diverse, non-tombstoned, and above local custody thresholds", obs)
