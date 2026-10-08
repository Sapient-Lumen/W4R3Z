"""Interest-mixing pressure for provider probes.

Provider proof handshakes are necessary because provider records are claims, not
semantic truth.  They are also dangerous: a probe reveals timing, route shape,
and sometimes the content key.  This module keeps that hard tradeoff visible by
planning and assessing mixed probe rounds before live transport exists.

This does not claim private retrieval or anonymity.  It says: a real provider
probe should have an explicit metadata budget, cover targets, family caps, and
replay memory before the DHT makes provider confirmation a default behavior.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping

from .bencode import BValue, bencode
from .familydiversity import FamilyDiversityPolicy, analyze_family_diversity
from .ids import DOMAIN, sha256
from .privateprovider import (
    PrivateProbeBudget,
    PrivateProbeDecisionKind,
    PrivateProviderProbe,
    PrivateProviderProbePlan,
    ProviderCandidate,
    assess_private_probe_plan,
    plan_private_provider_probes,
)

INTEREST_MIX_DOMAIN = DOMAIN + b":interest-mix-v1:"


class InterestTargetKind(str, Enum):
    REAL = "real"
    COVER = "cover"


class InterestMixDecisionKind(str, Enum):
    ACCEPT_MIXED_ROUND = "accept_mixed_round"
    HOLD_NO_REAL_TARGETS = "hold_no_real_targets"
    HOLD_TOO_MANY_REAL_TARGETS = "hold_too_many_real_targets"
    HOLD_INSUFFICIENT_COVER = "hold_insufficient_cover"
    HOLD_LINKABLE_REPEAT = "hold_linkable_repeat"
    HOLD_PRIVATE_PROBE_PRESSURE = "hold_private_probe_pressure"
    REDUCE_RAW_KEY_EXPOSURE = "reduce_raw_key_exposure"
    QUARANTINE_PROBE_FAMILY_MONOCULTURE = "quarantine_probe_family_monoculture"


@dataclass(frozen=True)
class InterestTarget:
    namespace: str
    content_key: bytes
    kind: InterestTargetKind
    label: str = ""
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.namespace:
            raise ValueError("interest target namespace must not be empty")
        if len(self.content_key) != 32:
            raise ValueError("interest target content key must be 32 bytes")
        if self.priority < 0:
            raise ValueError("interest target priority must be non-negative")

    @property
    def target_digest(self) -> bytes:
        return sha256(INTEREST_MIX_DOMAIN + b":target:" + self.namespace.encode("utf-8") + self.kind.value.encode("utf-8") + self.content_key)

    def bvalue(self, *, reveal_key: bool = False) -> dict[bytes, BValue]:
        out: dict[bytes, BValue] = {
            b"namespace": self.namespace,
            b"kind": self.kind.value,
            b"target_digest": self.target_digest,
            b"label": self.label,
            b"priority": self.priority,
        }
        if reveal_key:
            out[b"content_key"] = self.content_key
        return out


@dataclass(frozen=True)
class InterestMixPolicy:
    max_real_targets: int = 2
    min_cover_targets: int = 2
    min_cover_per_real: int = 1
    max_raw_key_exposures: int = 2
    min_probe_families: int = 3
    max_per_probe_family: int = 4
    repeat_window_rounds: int = 8
    max_real_repeats_in_window: int = 2
    require_private_probe_acceptance: bool = True

    def validate(self) -> None:
        for value in (
            self.max_real_targets,
            self.min_cover_targets,
            self.min_cover_per_real,
            self.max_raw_key_exposures,
            self.min_probe_families,
            self.max_per_probe_family,
            self.repeat_window_rounds,
            self.max_real_repeats_in_window,
        ):
            if value < 0:
                raise ValueError("interest mix policy thresholds must be non-negative")
        if self.max_real_targets <= 0 or self.min_probe_families <= 0 or self.max_per_probe_family <= 0:
            raise ValueError("interest mix policy needs positive real/family thresholds")


@dataclass
class InterestMixHistory:
    """Local-only exposure memory for linkability pressure."""

    real_rounds_by_key: dict[bytes, list[int]] = field(default_factory=dict)

    def exposures_in_window(self, target: InterestTarget, *, round_id: int, window: int) -> int:
        if target.kind is not InterestTargetKind.REAL:
            return 0
        lower = round_id - max(0, window)
        return sum(1 for seen in self.real_rounds_by_key.get(target.content_key, []) if lower <= seen <= round_id)

    def record_round(self, mix_round: "InterestMixRound") -> None:
        for target in mix_round.targets:
            if target.kind is InterestTargetKind.REAL:
                self.real_rounds_by_key.setdefault(target.content_key, []).append(mix_round.round_id)


@dataclass(frozen=True)
class InterestProbeBundle:
    target: InterestTarget
    plan: PrivateProviderProbePlan

    @property
    def probes(self) -> tuple[PrivateProviderProbe, ...]:
        return self.plan.probes

    @property
    def bundle_digest(self) -> bytes:
        return sha256(INTEREST_MIX_DOMAIN + b":bundle:" + self.target.target_digest + self.plan.content_key_commitment + b"".join(probe.commitment for probe in self.plan.probes))

    def witness_bvalue(self) -> dict[bytes, BValue]:
        # This is the witness-visible shape: target digest and probe commitments,
        # not raw content keys or labels that would identify the real interest.
        return {
            b"target_kind": self.target.kind.value,
            b"target_digest": self.target.target_digest,
            b"plan_commitment": self.plan.content_key_commitment,
            b"probe_commitments": [probe.commitment for probe in self.plan.probes],
            b"families": sorted(self.plan.probe_families),
        }


@dataclass(frozen=True)
class InterestMixRound:
    round_id: int
    issued_at: int
    bundles: tuple[InterestProbeBundle, ...]
    omitted_real_count: int
    omitted_cover_count: int

    @property
    def targets(self) -> tuple[InterestTarget, ...]:
        return tuple(bundle.target for bundle in self.bundles)

    @property
    def real_bundles(self) -> tuple[InterestProbeBundle, ...]:
        return tuple(bundle for bundle in self.bundles if bundle.target.kind is InterestTargetKind.REAL)

    @property
    def cover_bundles(self) -> tuple[InterestProbeBundle, ...]:
        return tuple(bundle for bundle in self.bundles if bundle.target.kind is InterestTargetKind.COVER)

    @property
    def probes(self) -> tuple[PrivateProviderProbe, ...]:
        return tuple(probe for bundle in self.bundles for probe in bundle.probes)

    @property
    def raw_key_exposure_count(self) -> int:
        return sum(bundle.plan.content_key_exposure_count for bundle in self.bundles)

    @property
    def probe_family_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for probe in self.probes:
            counts[probe.family_id] = counts.get(probe.family_id, 0) + 1
        return counts

    @property
    def witness_payload(self) -> bytes:
        return INTEREST_MIX_DOMAIN + b":witness-round:" + bencode({
            b"round_id": self.round_id,
            b"issued_at": self.issued_at,
            b"bundles": [bundle.witness_bvalue() for bundle in self.bundles],
        })

    @property
    def transcript_digest(self) -> bytes:
        return sha256(INTEREST_MIX_DOMAIN + b":round:" + bencode({
            b"round_id": self.round_id,
            b"issued_at": self.issued_at,
            b"bundles": [bundle.bundle_digest for bundle in self.bundles],
            b"omitted_real": self.omitted_real_count,
            b"omitted_cover": self.omitted_cover_count,
        }))


@dataclass(frozen=True)
class InterestMixDecision:
    kind: InterestMixDecisionKind
    accept: bool
    reason: str


@dataclass(frozen=True)
class InterestMixReport:
    mix_round: InterestMixRound
    decision: InterestMixDecision
    private_probe_kinds: tuple[PrivateProbeDecisionKind, ...]
    repeated_targets: tuple[bytes, ...]
    family_counts: Mapping[str, int]
    digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision.kind.value.startswith("quarantine_")


def _sort_targets(targets: Iterable[InterestTarget]) -> tuple[InterestTarget, ...]:
    return tuple(sorted(targets, key=lambda item: (-item.priority, item.namespace, item.target_digest)))


def _target_nonce(seed_nonce: bytes, *, round_id: int, target: InterestTarget, index: int) -> bytes:
    return sha256(INTEREST_MIX_DOMAIN + b":target-nonce:" + seed_nonce + round_id.to_bytes(8, "big") + index.to_bytes(4, "big") + target.target_digest)


def plan_interest_mix_round(
    real_targets: Iterable[InterestTarget],
    cover_targets: Iterable[InterestTarget],
    candidates: Iterable[ProviderCandidate],
    *,
    round_id: int,
    issued_at: int,
    seed_nonce: bytes,
    policy: InterestMixPolicy | None = None,
    probe_budget: PrivateProbeBudget | None = None,
) -> InterestMixRound:
    policy = policy or InterestMixPolicy()
    policy.validate()
    probe_budget = probe_budget or PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=1, require_decoy=True)
    if len(seed_nonce) != 32:
        raise ValueError("interest mix seed nonce must be 32 bytes")
    real_sorted = tuple(target for target in _sort_targets(real_targets) if target.kind is InterestTargetKind.REAL)
    cover_sorted = tuple(target for target in _sort_targets(cover_targets) if target.kind is InterestTargetKind.COVER)
    selected_real = real_sorted[:policy.max_real_targets]
    needed_cover = max(policy.min_cover_targets, len(selected_real) * policy.min_cover_per_real)
    selected_cover = cover_sorted[:needed_cover]
    selected = selected_real + selected_cover
    candidate_tuple = tuple(candidates)
    bundles: list[InterestProbeBundle] = []
    for index, target in enumerate(selected):
        nonce = _target_nonce(seed_nonce, round_id=round_id, target=target, index=index)
        plan = plan_private_provider_probes(candidate_tuple, namespace=target.namespace, content_key=target.content_key, nonce=nonce, issued_at=issued_at, budget=probe_budget)
        bundles.append(InterestProbeBundle(target=target, plan=plan))
    return InterestMixRound(round_id=round_id, issued_at=issued_at, bundles=tuple(bundles), omitted_real_count=max(0, len(real_sorted) - len(selected_real)), omitted_cover_count=max(0, len(cover_sorted) - len(selected_cover)))


def assess_interest_mix_round(
    mix_round: InterestMixRound,
    *,
    policy: InterestMixPolicy | None = None,
    probe_budget: PrivateProbeBudget | None = None,
    history: InterestMixHistory | None = None,
) -> InterestMixReport:
    policy = policy or InterestMixPolicy()
    policy.validate()
    probe_budget = probe_budget or PrivateProbeBudget(max_real_probes=2, max_decoy_probes=1, min_families=2, max_per_family=1, max_content_key_exposures=1, require_decoy=True)
    real_count = len(mix_round.real_bundles)
    cover_count = len(mix_round.cover_bundles)
    private_kinds = tuple(assess_private_probe_plan(bundle.plan, budget=probe_budget).kind for bundle in mix_round.bundles)
    repeated: list[bytes] = []
    if history is not None:
        for bundle in mix_round.real_bundles:
            if history.exposures_in_window(bundle.target, round_id=mix_round.round_id, window=policy.repeat_window_rounds) >= policy.max_real_repeats_in_window:
                repeated.append(bundle.target.target_digest)

    diversity = analyze_family_diversity(mix_round.probes, family_of=lambda probe: probe.family_id, policy=FamilyDiversityPolicy(min_families=policy.min_probe_families, max_per_family=policy.max_per_probe_family))

    if real_count == 0:
        decision = InterestMixDecision(InterestMixDecisionKind.HOLD_NO_REAL_TARGETS, False, "mixed round has no real target to protect or confirm")
    elif mix_round.omitted_real_count > 0:
        decision = InterestMixDecision(InterestMixDecisionKind.HOLD_TOO_MANY_REAL_TARGETS, False, "too many real targets requested for one metadata budgeted round")
    elif cover_count < policy.min_cover_targets or cover_count < real_count * policy.min_cover_per_real:
        decision = InterestMixDecision(InterestMixDecisionKind.HOLD_INSUFFICIENT_COVER, False, "real provider probes do not have enough cover targets")
    elif repeated:
        decision = InterestMixDecision(InterestMixDecisionKind.HOLD_LINKABLE_REPEAT, False, "real target was probed too often inside the local repeat window")
    elif policy.require_private_probe_acceptance and any(kind is not PrivateProbeDecisionKind.ACCEPT_PRESSURED_PLAN for kind in private_kinds):
        decision = InterestMixDecision(InterestMixDecisionKind.HOLD_PRIVATE_PROBE_PRESSURE, False, "one or more underlying private-provider probe plans failed pressure assessment")
    elif mix_round.raw_key_exposure_count > policy.max_raw_key_exposures:
        decision = InterestMixDecision(InterestMixDecisionKind.REDUCE_RAW_KEY_EXPOSURE, False, "mixed round exceeds raw content-key exposure budget")
    elif not diversity.passes(FamilyDiversityPolicy(policy.min_probe_families, policy.max_per_probe_family)):
        decision = InterestMixDecision(InterestMixDecisionKind.QUARANTINE_PROBE_FAMILY_MONOCULTURE, False, "mixed round probe traffic is too family-concentrated")
    else:
        decision = InterestMixDecision(InterestMixDecisionKind.ACCEPT_MIXED_ROUND, True, "real probes are covered, bounded, and family-spread enough for this local policy")

    digest = sha256(INTEREST_MIX_DOMAIN + b":report:" + bencode({
        b"round": mix_round.transcript_digest,
        b"decision": decision.kind.value,
        b"private_kinds": [kind.value for kind in private_kinds],
        b"repeated": repeated,
        b"family_counts": {family: count for family, count in sorted(mix_round.probe_family_counts.items())},
    }))
    return InterestMixReport(mix_round, decision, private_kinds, tuple(repeated), dict(mix_round.probe_family_counts), digest)
