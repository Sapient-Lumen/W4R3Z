"""Mutable namespace-policy epoch heads.

rev0023 made namespace policies local dispatch safety.  This module turns the
next risky guess into executable pressure: policy rollout itself needs signed
mutable heads with local epoch memory, previous-head links, family-diverse
observations, rollback/fork detection, and digest binding to the actual
namespace policy being activated.

This is not global governance.  A node may subscribe to an authority's policy
head, but local memory still decides whether an observation advances safely.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .identity import DhtKeypair, verify_signature
from .ids import DOMAIN, sha256
from .namespaceregistry import NamespacePolicy

POLICY_EPOCH_DOMAIN = DOMAIN + b":policy-epoch-v1:"


class PolicyEpochDecisionKind(str, Enum):
    ACCEPT_GENESIS = "accept_genesis"
    ACCEPT_ADVANCE = "accept_advance"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    CONTINUE_NO_VALID_HEADS = "continue_no_valid_heads"
    CONTINUE_NEED_FAMILY_DIVERSITY = "continue_need_family_diversity"
    REJECT_BAD_SIGNATURE_OR_TIME = "reject_bad_signature_or_time"
    REJECT_POLICY_DIGEST_MISMATCH = "reject_policy_digest_mismatch"
    REJECT_POLICY_NOT_LIVE = "reject_policy_not_live"
    REJECT_ROLLBACK = "reject_rollback"
    QUARANTINE_SAME_EPOCH_FORK = "quarantine_same_epoch_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_SCOPE_MIXING = "quarantine_scope_mixing"


@dataclass(frozen=True)
class PolicyEpochHead:
    namespace: str
    authority_public_key: bytes
    policy_digest: bytes
    epoch: int
    previous_head_digest: bytes
    purpose: str
    issued_at: int
    expires_at: int
    signature: bytes = b""

    def __post_init__(self) -> None:
        if not self.namespace or not self.purpose:
            raise ValueError("policy epoch namespace/purpose required")
        if len(self.authority_public_key) != 32 or len(self.policy_digest) != 32:
            raise ValueError("policy epoch authority/policy digest must be 32 bytes")
        if self.previous_head_digest not in (b"",) and len(self.previous_head_digest) != 32:
            raise ValueError("previous_head_digest must be empty or 32 bytes")
        if self.epoch < 0 or self.expires_at <= self.issued_at:
            raise ValueError("policy epoch counters invalid")

    @classmethod
    def create(
        cls,
        *,
        authority: DhtKeypair,
        namespace: str,
        policy_digest: bytes,
        epoch: int,
        previous_head_digest: bytes,
        issued_at: int,
        ttl: int,
        purpose: str = "namespace_policy",
    ) -> "PolicyEpochHead":
        if ttl <= 0:
            raise ValueError("policy epoch ttl must be positive")
        unsigned = cls(
            namespace=namespace,
            authority_public_key=authority.public_key_bytes,
            policy_digest=policy_digest,
            epoch=epoch,
            previous_head_digest=previous_head_digest,
            purpose=purpose,
            issued_at=issued_at,
            expires_at=issued_at + ttl,
        )
        return replace(unsigned, signature=authority.sign(unsigned.unsigned_payload()))

    def unsigned_bvalue(self) -> dict[bytes, BValue]:
        return {
            b"namespace": self.namespace,
            b"authority_public_key": self.authority_public_key,
            b"policy_digest": self.policy_digest,
            b"epoch": self.epoch,
            b"previous_head_digest": self.previous_head_digest,
            b"purpose": self.purpose,
            b"issued_at": self.issued_at,
            b"expires_at": self.expires_at,
        }

    def unsigned_payload(self) -> bytes:
        return POLICY_EPOCH_DOMAIN + b":head-unsigned:" + bencode(self.unsigned_bvalue())

    @property
    def head_digest(self) -> bytes:
        return sha256(POLICY_EPOCH_DOMAIN + b":head:" + self.unsigned_payload() + self.signature)

    def signature_valid(self) -> bool:
        return verify_signature(self.authority_public_key, self.unsigned_payload(), self.signature)

    def live(self, *, now: int, max_future_skew: int = 300) -> bool:
        return self.issued_at - max_future_skew <= now < self.expires_at + max_future_skew


@dataclass(frozen=True)
class PolicyEpochObservation:
    head: PolicyEpochHead
    source_family: str

    def __post_init__(self) -> None:
        if not self.source_family:
            raise ValueError("policy epoch observation source_family required")

    @property
    def observation_digest(self) -> bytes:
        return sha256(POLICY_EPOCH_DOMAIN + b":observation:" + self.head.head_digest + self.source_family.encode("utf-8"))


@dataclass(frozen=True)
class PolicyEpochMemory:
    highest_epoch_by_namespace: Mapping[str, int]
    latest_head_digest_by_namespace: Mapping[str, bytes]
    seen_head_digests_by_epoch: Mapping[tuple[str, int], frozenset[bytes]]

    @classmethod
    def empty(cls) -> "PolicyEpochMemory":
        return cls(highest_epoch_by_namespace={}, latest_head_digest_by_namespace={}, seen_head_digests_by_epoch={})


@dataclass(frozen=True)
class PolicyEpochPolicy:
    min_families: int = 2
    max_per_family: int = 1
    max_future_skew: int = 300
    require_previous_link: bool = True
    allow_watch_without_memory: bool = True

    def family_policy(self) -> FamilyDiversityPolicy:
        return FamilyDiversityPolicy(min_families=self.min_families, max_per_family=self.max_per_family)


@dataclass(frozen=True)
class PolicyEpochDecision:
    kind: PolicyEpochDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class PolicyEpochAssessment:
    decision: PolicyEpochDecision
    chosen_head: PolicyEpochHead | None
    valid_observations: tuple[PolicyEpochObservation, ...]
    invalid_observations: tuple[PolicyEpochObservation, ...]
    family_counts: dict[str, int]
    digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def memory_from_policy_epoch_heads(heads: Iterable[PolicyEpochHead]) -> PolicyEpochMemory:
    highest: dict[str, int] = {}
    latest: dict[str, bytes] = {}
    seen: dict[tuple[str, int], set[bytes]] = {}
    for head in heads:
        seen.setdefault((head.namespace, head.epoch), set()).add(head.head_digest)
        old = highest.get(head.namespace, -1)
        if head.epoch > old or (head.epoch == old and head.head_digest > latest.get(head.namespace, b"")):
            highest[head.namespace] = head.epoch
            latest[head.namespace] = head.head_digest
    return PolicyEpochMemory(
        highest_epoch_by_namespace=highest,
        latest_head_digest_by_namespace=latest,
        seen_head_digests_by_epoch={key: frozenset(value) for key, value in seen.items()},
    )


def _assessment(
    decision: PolicyEpochDecision,
    *,
    chosen_head: PolicyEpochHead | None = None,
    valid_observations: Iterable[PolicyEpochObservation] = (),
    invalid_observations: Iterable[PolicyEpochObservation] = (),
    family_counts: dict[str, int] | None = None,
) -> PolicyEpochAssessment:
    valid = tuple(valid_observations)
    invalid = tuple(invalid_observations)
    counts = dict(sorted((family_counts or {}).items()))
    digest = sha256(POLICY_EPOCH_DOMAIN + b":assessment:" + bencode({
        b"decision": decision.kind.value,
        b"accept": 1 if decision.accept else 0,
        b"chosen": b"" if chosen_head is None else chosen_head.head_digest,
        b"valid": [obs.observation_digest for obs in valid],
        b"invalid": [obs.observation_digest for obs in invalid],
        b"families": counts,
    }))
    return PolicyEpochAssessment(decision, chosen_head, valid, invalid, counts, digest)


def assess_policy_epoch(
    observations: Iterable[PolicyEpochObservation],
    *,
    expected_policy: NamespacePolicy,
    memory: PolicyEpochMemory | None,
    now: int,
    policy: PolicyEpochPolicy | None = None,
) -> PolicyEpochAssessment:
    policy = policy or PolicyEpochPolicy()
    memory = memory or PolicyEpochMemory.empty()
    incoming = tuple(observations)
    valid: list[PolicyEpochObservation] = []
    invalid: list[PolicyEpochObservation] = []
    for obs in incoming:
        head = obs.head
        if head.signature_valid() and head.live(now=now, max_future_skew=policy.max_future_skew):
            valid.append(obs)
        else:
            invalid.append(obs)
    if not expected_policy.signature_valid() or not expected_policy.live(now=now, max_future_skew=policy.max_future_skew):
        return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.REJECT_POLICY_NOT_LIVE, False, "expected namespace policy is not live/signature-valid"), valid_observations=valid, invalid_observations=invalid)
    if not valid:
        kind = PolicyEpochDecisionKind.REJECT_BAD_SIGNATURE_OR_TIME if invalid else PolicyEpochDecisionKind.CONTINUE_NO_VALID_HEADS
        return _assessment(PolicyEpochDecision(kind, False, "no valid live policy epoch heads"), invalid_observations=invalid)
    namespaces = {obs.head.namespace for obs in valid}
    purposes = {obs.head.purpose for obs in valid}
    if namespaces != {expected_policy.namespace} or len(purposes) != 1:
        return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.QUARANTINE_SCOPE_MIXING, False, "policy epoch observations mix namespaces or purposes"), valid_observations=valid, invalid_observations=invalid)
    diversity = analyze_family_diversity(valid, family_of=lambda obs: obs.source_family, policy=policy.family_policy())
    if not diversity.passes(policy.family_policy()):
        return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY, False, "policy epoch observations need source-family diversity"), valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)

    max_epoch = max(obs.head.epoch for obs in valid)
    top = [obs.head for obs in valid if obs.head.epoch == max_epoch]
    top_digests = {head.head_digest for head in top}
    if len(top_digests) > 1:
        return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.QUARANTINE_SAME_EPOCH_FORK, False, "same-epoch policy head fork"), chosen_head=top[0], valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)
    chosen = top[0]
    if chosen.policy_digest != expected_policy.policy_digest:
        return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.REJECT_POLICY_DIGEST_MISMATCH, False, "policy epoch does not point at expected policy digest"), chosen_head=chosen, valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)

    namespace = expected_policy.namespace
    highest = memory.highest_epoch_by_namespace.get(namespace, -1)
    if chosen.epoch < highest:
        return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.REJECT_ROLLBACK, False, "policy epoch rolls back local memory"), chosen_head=chosen, valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)
    seen = set(memory.seen_head_digests_by_epoch.get((namespace, chosen.epoch), frozenset()))
    if seen and chosen.head_digest not in seen:
        return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.QUARANTINE_SAME_EPOCH_FORK, False, "policy epoch conflicts with locally seen digest"), chosen_head=chosen, valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)
    if policy.require_previous_link:
        latest = memory.latest_head_digest_by_namespace.get(namespace)
        if highest >= 0 and chosen.epoch > highest and chosen.previous_head_digest != latest:
            return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, "policy epoch does not link to local latest head"), chosen_head=chosen, valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)
        if highest < 0 and chosen.epoch > 0 and chosen.previous_head_digest and policy.allow_watch_without_memory:
            return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.ACCEPT_WITH_WATCH, True, "policy epoch is plausible but local previous history is absent"), chosen_head=chosen, valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)
        if highest < 0 and chosen.epoch > 0 and chosen.previous_head_digest and not policy.allow_watch_without_memory:
            return _assessment(PolicyEpochDecision(PolicyEpochDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, "policy epoch requires previous history local node does not have"), chosen_head=chosen, valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)

    kind = PolicyEpochDecisionKind.ACCEPT_GENESIS if highest < 0 else PolicyEpochDecisionKind.ACCEPT_ADVANCE
    return _assessment(PolicyEpochDecision(kind, True, "policy epoch advances local policy view"), chosen_head=chosen, valid_observations=valid, invalid_observations=invalid, family_counts=diversity.family_counts)
