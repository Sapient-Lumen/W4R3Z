"""Private-ish provider probing and metadata budget pressure.

This module attacks a hard DHT question before live transport exists:
provider records need semantic confirmation, but every confirmation probe can
leak interest, route shape, and timing.  The code does not claim private
retrieval.  It turns the tradeoff into explicit, testable objects:

* real probes expose the content key to selected providers;
* decoy probes spend bandwidth to blur probe shape;
* witness-visible material can be reduced to commitments;
* family caps stop a single fast/captured family from receiving the whole probe
  budget;
* acceptance is based on exposure and diversity pressure, not comfort.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .ids import DOMAIN, sha256, xor_distance

PRIVATE_PROVIDER_DOMAIN = DOMAIN + b":private-provider-v1:"


class ProbePurpose(str, Enum):
    REAL = "real"
    DECOY = "decoy"


class ProbeVisibility(str, Enum):
    RAW_CONTENT_KEY = "raw_content_key"
    COMMITMENT_ONLY = "commitment_only"


class PrivateProbeDecisionKind(str, Enum):
    ACCEPT_PRESSURED_PLAN = "accept_pressured_plan"
    REJECT_NO_CANDIDATES = "reject_no_candidates"
    CONTINUE_INSUFFICIENT_FAMILIES = "continue_insufficient_families"
    CONTINUE_FAMILY_MONOCULTURE = "continue_family_monoculture"
    REDUCE_KEY_EXPOSURE = "reduce_key_exposure"
    ADD_DECOYS_OR_COMMITMENTS = "add_decoys_or_commitments"


@dataclass(frozen=True)
class ProviderCandidate:
    provider_node_id: bytes
    family_id: str
    distance_rank: int
    latency_ms: int
    reliability_score: int = 0
    supports_commitment_probe: bool = True

    def sort_key(self, target: bytes) -> tuple[int, int, int]:
        # Prefer closeness and stable responders, but never let this override the
        # family-cap planner.  distance_rank is kept so tests can construct
        # deterministic frontiers without calculating XOR every time.
        distance = xor_distance(self.provider_node_id, target) if len(self.provider_node_id) == len(target) else 2**256 - 1
        return (self.distance_rank, distance, self.latency_ms - self.reliability_score)


@dataclass(frozen=True)
class PrivateProbeBudget:
    max_real_probes: int = 3
    max_decoy_probes: int = 2
    min_families: int = 2
    max_per_family: int = 1
    max_content_key_exposures: int = 2
    require_decoy: bool = True
    prefer_commitment_witnessing: bool = True

    def validate(self) -> None:
        if self.max_real_probes <= 0:
            raise ValueError("max_real_probes must be positive")
        if self.max_decoy_probes < 0:
            raise ValueError("max_decoy_probes must be non-negative")
        if self.min_families <= 0 or self.max_per_family <= 0:
            raise ValueError("family thresholds must be positive")
        if self.max_content_key_exposures <= 0:
            raise ValueError("max_content_key_exposures must be positive")


@dataclass(frozen=True)
class PrivateProviderProbe:
    provider_node_id: bytes
    family_id: str
    namespace: str
    purpose: ProbePurpose
    visibility: ProbeVisibility
    commitment: bytes
    nonce: bytes
    issued_at: int
    content_key: bytes = b""

    @property
    def exposes_content_key(self) -> bool:
        return self.purpose is ProbePurpose.REAL and self.visibility is ProbeVisibility.RAW_CONTENT_KEY and bool(self.content_key)

    @property
    def wire_hint(self) -> dict[str, str | int]:
        # A transport-neutral hint for tests/transcripts; intentionally omits raw
        # content_key when the probe is commitment-only.
        out: dict[str, str | int] = {
            "provider_node_id": self.provider_node_id.hex(),
            "family_id": self.family_id,
            "purpose": self.purpose.value,
            "visibility": self.visibility.value,
            "commitment": self.commitment.hex(),
            "issued_at": self.issued_at,
        }
        if self.exposes_content_key:
            out["content_key"] = self.content_key.hex()
        return out


@dataclass(frozen=True)
class PrivateProviderProbePlan:
    namespace: str
    content_key_commitment: bytes
    probes: tuple[PrivateProviderProbe, ...]
    omitted_candidate_count: int

    @property
    def real_probes(self) -> tuple[PrivateProviderProbe, ...]:
        return tuple(probe for probe in self.probes if probe.purpose is ProbePurpose.REAL)

    @property
    def decoy_probes(self) -> tuple[PrivateProviderProbe, ...]:
        return tuple(probe for probe in self.probes if probe.purpose is ProbePurpose.DECOY)

    @property
    def content_key_exposure_count(self) -> int:
        return sum(1 for probe in self.probes if probe.exposes_content_key)

    @property
    def real_families(self) -> frozenset[str]:
        return frozenset(probe.family_id for probe in self.real_probes)

    @property
    def probe_families(self) -> frozenset[str]:
        return frozenset(probe.family_id for probe in self.probes)


@dataclass(frozen=True)
class PrivateProbeAssessment:
    kind: PrivateProbeDecisionKind
    accept: bool
    reason: str
    exposed_keys: int
    real_families: int
    decoy_count: int


def provider_probe_commitment(*, namespace: str, content_key: bytes, nonce: bytes, provider_node_id: bytes, purpose: ProbePurpose) -> bytes:
    if not namespace:
        raise ValueError("namespace must not be empty")
    if len(content_key) != 32 or len(provider_node_id) != 32:
        raise ValueError("content key and provider id must be 32 bytes")
    return sha256(
        PRIVATE_PROVIDER_DOMAIN
        + b":commitment:"
        + namespace.encode("utf-8")
        + b":"
        + purpose.value.encode("utf-8")
        + b":"
        + content_key
        + nonce
        + provider_node_id
    )


def decoy_key(*, namespace: str, content_key: bytes, nonce: bytes, counter: int) -> bytes:
    return sha256(PRIVATE_PROVIDER_DOMAIN + b":decoy-key:" + namespace.encode("utf-8") + content_key + nonce + counter.to_bytes(4, "big"))


def _select_family_capped(candidates: Iterable[ProviderCandidate], *, target: bytes, count: int, max_per_family: int) -> tuple[ProviderCandidate, ...]:
    selected: list[ProviderCandidate] = []
    family_counts: dict[str, int] = {}
    for candidate in sorted(candidates, key=lambda item: item.sort_key(target)):
        if family_counts.get(candidate.family_id, 0) >= max_per_family:
            continue
        selected.append(candidate)
        family_counts[candidate.family_id] = family_counts.get(candidate.family_id, 0) + 1
        if len(selected) >= count:
            break
    return tuple(selected)


def plan_private_provider_probes(
    candidates: Iterable[ProviderCandidate],
    *,
    namespace: str,
    content_key: bytes,
    nonce: bytes,
    issued_at: int,
    budget: PrivateProbeBudget | None = None,
) -> PrivateProviderProbePlan:
    budget = budget or PrivateProbeBudget()
    budget.validate()
    if len(content_key) != 32:
        raise ValueError("content_key must be 32 bytes")
    candidate_tuple = tuple(candidates)
    real_candidates = _select_family_capped(candidate_tuple, target=content_key, count=budget.max_real_probes, max_per_family=budget.max_per_family)
    probes: list[PrivateProviderProbe] = []
    for candidate in real_candidates:
        visibility = ProbeVisibility.COMMITMENT_ONLY if budget.prefer_commitment_witnessing and candidate.supports_commitment_probe else ProbeVisibility.RAW_CONTENT_KEY
        # Even when a provider-side protocol must ultimately reveal the content
        # key, the witness/sentinel surface can remain commitment-only.  For
        # pressure tests, unsupported commitment probes represent raw-key probes.
        raw_key = content_key if visibility is ProbeVisibility.RAW_CONTENT_KEY else b""
        probes.append(PrivateProviderProbe(
            provider_node_id=candidate.provider_node_id,
            family_id=candidate.family_id,
            namespace=namespace,
            purpose=ProbePurpose.REAL,
            visibility=visibility,
            commitment=provider_probe_commitment(namespace=namespace, content_key=content_key, nonce=nonce, provider_node_id=candidate.provider_node_id, purpose=ProbePurpose.REAL),
            nonce=nonce,
            issued_at=issued_at,
            content_key=raw_key,
        ))

    used = {candidate.provider_node_id for candidate in real_candidates}
    decoy_candidates = _select_family_capped((candidate for candidate in candidate_tuple if candidate.provider_node_id not in used), target=sha256(content_key + nonce), count=budget.max_decoy_probes, max_per_family=budget.max_per_family)
    for idx, candidate in enumerate(decoy_candidates):
        fake_key = decoy_key(namespace=namespace, content_key=content_key, nonce=nonce, counter=idx)
        probes.append(PrivateProviderProbe(
            provider_node_id=candidate.provider_node_id,
            family_id=candidate.family_id,
            namespace=namespace,
            purpose=ProbePurpose.DECOY,
            visibility=ProbeVisibility.COMMITMENT_ONLY,
            commitment=provider_probe_commitment(namespace=namespace, content_key=fake_key, nonce=nonce, provider_node_id=candidate.provider_node_id, purpose=ProbePurpose.DECOY),
            nonce=nonce,
            issued_at=issued_at,
            content_key=b"",
        ))

    return PrivateProviderProbePlan(
        namespace=namespace,
        content_key_commitment=sha256(PRIVATE_PROVIDER_DOMAIN + b":content-key-commitment:" + namespace.encode("utf-8") + content_key + nonce),
        probes=tuple(probes),
        omitted_candidate_count=max(0, len(candidate_tuple) - len(probes)),
    )


def assess_private_probe_plan(plan: PrivateProviderProbePlan, *, budget: PrivateProbeBudget | None = None) -> PrivateProbeAssessment:
    budget = budget or PrivateProbeBudget()
    budget.validate()
    if not plan.probes:
        return PrivateProbeAssessment(PrivateProbeDecisionKind.REJECT_NO_CANDIDATES, False, "no providers selected", 0, 0, 0)
    exposed = plan.content_key_exposure_count
    real_families = len(plan.real_families)
    decoy_count = len(plan.decoy_probes)
    if real_families < budget.min_families:
        return PrivateProbeAssessment(PrivateProbeDecisionKind.CONTINUE_INSUFFICIENT_FAMILIES, False, "real probes do not cross enough families", exposed, real_families, decoy_count)
    if len(plan.probe_families) < budget.min_families:
        return PrivateProbeAssessment(PrivateProbeDecisionKind.CONTINUE_FAMILY_MONOCULTURE, False, "all probe traffic is family-monoculture", exposed, real_families, decoy_count)
    if exposed > budget.max_content_key_exposures:
        return PrivateProbeAssessment(PrivateProbeDecisionKind.REDUCE_KEY_EXPOSURE, False, "raw content-key exposure exceeds budget", exposed, real_families, decoy_count)
    if budget.require_decoy and decoy_count == 0:
        return PrivateProbeAssessment(PrivateProbeDecisionKind.ADD_DECOYS_OR_COMMITMENTS, False, "probe shape has no decoy traffic", exposed, real_families, decoy_count)
    return PrivateProbeAssessment(PrivateProbeDecisionKind.ACCEPT_PRESSURED_PLAN, True, "enough family diversity and bounded exposure for a probe attempt", exposed, real_families, decoy_count)
