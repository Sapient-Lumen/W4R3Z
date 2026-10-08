from __future__ import annotations

import math
from typing import Any, Iterable

from .util import canonical_json, sha256_text

PARTICLE_BANK_POLICY = "lacuna.particle-bank.v1"
PARTICLE_UPDATE_METHOD = "likelihood-reweight-v1"
PARTICLE_RECONCILIATION_POLICY = "lacuna.particle-reconciliation.v1"
PARTICLE_RECONCILIATION_METHOD = "factor-ledger-log-replay-v1"

# Any of these events can change the eligible population, a world's explicit
# valuation/custody, or the authored prior.  Evidence assertions and particle
# updates do not start a new epoch: the former are factor inputs and the latter
# are the immutable factor ledger itself.
PARTICLE_EPOCH_BOUNDARY_EVENTS = frozenset(
    {
        "world.created",
        "world.assigned",
        "world.revised",
        "world.commitment_raised",
        "world.weight_set",
        "world.status_set",
    }
)


def _assignment_valuation(assignment: dict[str, Any]) -> dict[str, Any]:
    """Return only the explicit ontic proposition represented by an assignment.

    Commitment, confidence, provenance, and record identity deliberately do not
    define valuation equivalence. Two worlds can therefore be valuation-equivalent
    while retaining different custody and planning histories.
    """
    return {
        "claim_id": str(assignment["claim_id"]),
        "truth": str(assignment["truth"]),
        "timeline_id": str(assignment.get("timeline_id", "main")),
        "valid_from": assignment.get("valid_from"),
        "valid_to": assignment.get("valid_to"),
    }


def _assignment_custody(assignment: dict[str, Any]) -> dict[str, Any]:
    """Return the state that should stale a reviewed particle population."""
    return {
        "assignment_id": str(assignment["assignment_id"]),
        **_assignment_valuation(assignment),
        "commitment": str(assignment.get("commitment", "tentative")),
        "commitment_basis": str(assignment.get("commitment_basis", "legacy")),
        "commitment_source_id": assignment.get("commitment_source_id"),
        "confidence": assignment.get("confidence"),
        "source_assertion_id": assignment.get("source_assertion_id"),
        "inherited_from_assignment_id": assignment.get("inherited_from_assignment_id"),
        "revision_of_assignment_id": assignment.get("revision_of_assignment_id"),
    }


def world_valuation_sha256(assignments: Iterable[dict[str, Any]]) -> str:
    records = sorted(
        (_assignment_valuation(item) for item in assignments),
        key=lambda item: (
            item["claim_id"],
            item["timeline_id"],
            -1 if item["valid_from"] is None else int(item["valid_from"]),
            -1 if item["valid_to"] is None else int(item["valid_to"]),
            item["truth"],
        ),
    )
    return sha256_text(canonical_json({"schema": "lacuna.world-valuation.v1", "assignments": records}))


def world_custody_sha256(assignments: Iterable[dict[str, Any]]) -> str:
    records = sorted(
        (_assignment_custody(item) for item in assignments),
        key=lambda item: item["assignment_id"],
    )
    return sha256_text(canonical_json({"schema": "lacuna.world-custody.v1", "assignments": records}))


def distribution_statistics(probabilities: Iterable[float]) -> dict[str, float]:
    values = [float(value) for value in probabilities]
    if not values:
        return {
            "effective_sample_size": 0.0,
            "entropy_nats": 0.0,
            "normalized_entropy": 0.0,
            "maximum_probability": 0.0,
        }
    square_sum = math.fsum(value * value for value in values)
    ess = 0.0 if square_sum <= 0.0 else 1.0 / square_sum
    entropy = -math.fsum(value * math.log(value) for value in values if value > 0.0)
    normalized_entropy = 1.0 if len(values) == 1 else entropy / math.log(len(values))
    return {
        "effective_sample_size": ess,
        "entropy_nats": entropy,
        "normalized_entropy": normalized_entropy,
        "maximum_probability": max(values),
    }


def particle_bank_sha256(particles: Iterable[dict[str, Any]]) -> str:
    """Hash the complete bank custody surface without requiring world prose."""
    records = sorted(
        (
            {
                "world_id": str(item["world_id"]),
                "status": str(item["status"]),
                "raw_weight": float(item["raw_weight"]),
                "valuation_sha256": str(item["valuation_sha256"]),
                "custody_sha256": str(item["custody_sha256"]),
            }
            for item in particles
        ),
        key=lambda item: item["world_id"],
    )
    return sha256_text(
        canonical_json({"policy": PARTICLE_BANK_POLICY, "particles": records})
    )


def build_particle_bank_from_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Normalize already-fingerprinted particle records deterministically.

    This shared constructor is used for both the live bank and historical
    baselines reconstructed from immutable update receipts.  It deliberately
    treats normalized probabilities as a projection and keeps raw weights in
    the digest surface.
    """
    particles: list[dict[str, Any]] = []
    for record in records:
        raw_weight = float(record["raw_weight"])
        if not math.isfinite(raw_weight) or raw_weight < 0.0:
            raise ValueError("particle raw weights must be finite and nonnegative")
        particles.append(
            {
                "world_id": str(record["world_id"]),
                "label": str(record.get("label", record["world_id"])),
                "status": str(record["status"]),
                "raw_weight": raw_weight,
                "valuation_sha256": str(record["valuation_sha256"]),
                "custody_sha256": str(record["custody_sha256"]),
                "assignment_count": record.get("assignment_count"),
            }
        )
    particles.sort(key=lambda item: item["world_id"])
    weight_sum = math.fsum(item["raw_weight"] for item in particles)
    normalized = weight_sum > 0.0
    for item in particles:
        item["probability"] = item["raw_weight"] / weight_sum if normalized else None

    groups: dict[str, list[dict[str, Any]]] = {}
    for item in particles:
        groups.setdefault(item["valuation_sha256"], []).append(item)
    valuation_groups = []
    for fingerprint, members in sorted(groups.items()):
        mass = None
        if normalized:
            mass = math.fsum(float(item["probability"]) for item in members)
        valuation_groups.append(
            {
                "valuation_sha256": fingerprint,
                "world_ids": [item["world_id"] for item in members],
                "world_count": len(members),
                "probability_mass": mass,
            }
        )

    stats = (
        distribution_statistics(float(item["probability"]) for item in particles)
        if normalized
        else distribution_statistics([])
    )
    return {
        "schema": "lacuna.particle-bank.v1",
        "policy": PARTICLE_BANK_POLICY,
        "bank_sha256": particle_bank_sha256(particles),
        "normalization_status": "normalized" if normalized else "zero-mass",
        "world_count": len(particles),
        "raw_weight_sum": weight_sum,
        **stats,
        "valuation_group_count": len(valuation_groups),
        "duplicate_valuation_group_count": sum(
            1 for item in valuation_groups if item["world_count"] > 1
        ),
        "particles": particles,
        "valuation_groups": valuation_groups,
        "nonclaim": (
            "Weights and likelihoods are authored planning quantities, not certified probabilities. "
            "Valuation equivalence covers only explicit assignments and does not prove complete-world identity."
        ),
    }


def build_particle_bank(worlds: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic normalized view over live candidate worlds.

    Raw weights remain part of custody. The returned normalized probabilities are
    a projection; this function never mutates or prunes a world.
    """
    records: list[dict[str, Any]] = []
    for world in worlds:
        assignments = list(world.get("assignments", []))
        records.append(
            {
                "world_id": str(world["world_id"]),
                "label": str(world.get("label", world["world_id"])),
                "status": str(world["status"]),
                "raw_weight": float(world["weight"]),
                "valuation_sha256": world_valuation_sha256(assignments),
                "custody_sha256": world_custody_sha256(assignments),
                "assignment_count": len(assignments),
            }
        )
    return build_particle_bank_from_records(records)


def valuation_likelihood_divergence_groups(
    members: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Surface likelihood disagreement between explicit-valuation equivalents."""
    likelihoods_by_valuation: dict[str, set[float]] = {}
    worlds_by_valuation: dict[str, list[str]] = {}
    for item in members:
        fingerprint = str(item["valuation_sha256"])
        likelihoods_by_valuation.setdefault(fingerprint, set()).add(float(item["likelihood"]))
        worlds_by_valuation.setdefault(fingerprint, []).append(str(item["world_id"]))
    return [
        {
            "valuation_sha256": fingerprint,
            "world_ids": sorted(worlds_by_valuation[fingerprint]),
            "likelihoods": sorted(values),
        }
        for fingerprint, values in sorted(likelihoods_by_valuation.items())
        if len(values) > 1
    ]


def compute_likelihood_update(
    bank: dict[str, Any],
    assessments: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if bank["normalization_status"] != "normalized":
        raise ValueError("particle bank has zero prior mass")
    members: list[dict[str, Any]] = []
    for particle in bank["particles"]:
        world_id = str(particle["world_id"])
        assessment = assessments[world_id]
        prior_probability = float(particle["probability"])
        likelihood = float(assessment["likelihood"])
        unnormalized = prior_probability * likelihood
        members.append(
            {
                "world_id": world_id,
                "world_status": str(particle["status"]),
                "prior_weight": float(particle["raw_weight"]),
                "prior_probability": prior_probability,
                "likelihood": likelihood,
                "unnormalized_weight": unnormalized,
                "posterior_probability": 0.0,
                "rationale": assessment.get("rationale"),
                "valuation_sha256": particle["valuation_sha256"],
                "custody_sha256": particle["custody_sha256"],
            }
        )
    normalization_constant = math.fsum(item["unnormalized_weight"] for item in members)
    if normalization_constant <= 0.0:
        raise ValueError("all assessed worlds have zero posterior mass")
    for item in members:
        item["posterior_probability"] = item["unnormalized_weight"] / normalization_constant

    prior_stats = distribution_statistics(item["prior_probability"] for item in members)
    posterior_stats = distribution_statistics(item["posterior_probability"] for item in members)
    information_gain = math.fsum(
        item["posterior_probability"]
        * math.log(item["posterior_probability"] / item["prior_probability"])
        for item in members
        if item["posterior_probability"] > 0.0 and item["prior_probability"] > 0.0
    )

    return {
        "method": PARTICLE_UPDATE_METHOD,
        "normalization_constant": normalization_constant,
        "prior_effective_sample_size": prior_stats["effective_sample_size"],
        "posterior_effective_sample_size": posterior_stats["effective_sample_size"],
        "prior_entropy_nats": prior_stats["entropy_nats"],
        "posterior_entropy_nats": posterior_stats["entropy_nats"],
        "information_gain_nats": information_gain,
        "zero_likelihood_world_count": sum(1 for item in members if item["likelihood"] == 0.0),
        "valuation_likelihood_divergence_groups": valuation_likelihood_divergence_groups(members),
        "members": members,
    }


def particle_factor_set_sha256(
    *,
    baseline_update_id: str,
    boundary: dict[str, Any] | None,
    included_factors: Iterable[dict[str, Any]],
    excluded_factors: Iterable[dict[str, Any]],
) -> str:
    """Hash one deterministic factor-ledger selection without its calculated weights."""
    core = {
        "policy": PARTICLE_RECONCILIATION_POLICY,
        "baseline_update_id": baseline_update_id,
        "boundary": boundary,
        "included_factors": [
            {
                "update_id": str(item["update_id"]),
                "evidence_assertion_id": str(item["evidence_assertion_id"]),
                "created_seq": int(item["created_seq"]),
            }
            for item in included_factors
        ],
        "excluded_factors": [
            {
                "update_id": str(item["update_id"]),
                "evidence_assertion_id": str(item["evidence_assertion_id"]),
                "created_seq": int(item["created_seq"]),
                "evidence_ended_seq": int(item["evidence_ended_seq"]),
                "exclusion_reason": str(item["exclusion_reason"]),
            }
            for item in excluded_factors
        ],
    }
    return sha256_text(canonical_json(core))


def particle_reconciliation_review_sha256(
    *,
    cube_id: str,
    head: str,
    review_core: dict[str, Any],
) -> str:
    """Bind a reconciliation authorization to one ledger head and complete result."""
    return sha256_text(
        canonical_json(
            {
                "policy": PARTICLE_RECONCILIATION_POLICY,
                "cube_id": cube_id,
                "head": head,
                "review_core": review_core,
            }
        )
    )


def _particle_identity(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(item["status"]),
        str(item["valuation_sha256"]),
        str(item["custody_sha256"]),
    )


def factor_reconciliation_blockers(
    *,
    baseline_bank: dict[str, Any],
    current_bank: dict[str, Any],
    included_factors: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return deterministic population/custody blockers for factor replay."""
    blockers: list[dict[str, Any]] = []
    baseline = {str(item["world_id"]): item for item in baseline_bank["particles"]}
    current = {str(item["world_id"]): item for item in current_bank["particles"]}
    if set(baseline) != set(current):
        blockers.append(
            {
                "code": "particle-reconciliation-population-mismatch",
                "missing_current_world_ids": sorted(set(baseline) - set(current)),
                "new_current_world_ids": sorted(set(current) - set(baseline)),
            }
        )
    for world_id in sorted(set(baseline) & set(current)):
        if _particle_identity(baseline[world_id]) != _particle_identity(current[world_id]):
            blockers.append(
                {
                    "code": "particle-reconciliation-current-custody-mismatch",
                    "world_id": world_id,
                    "baseline": {
                        "status": baseline[world_id]["status"],
                        "valuation_sha256": baseline[world_id]["valuation_sha256"],
                        "custody_sha256": baseline[world_id]["custody_sha256"],
                    },
                    "current": {
                        "status": current[world_id]["status"],
                        "valuation_sha256": current[world_id]["valuation_sha256"],
                        "custody_sha256": current[world_id]["custody_sha256"],
                    },
                }
            )
    for factor in included_factors:
        assessments = {
            str(item["world_id"]): item for item in factor.get("assessments", [])
        }
        if set(assessments) != set(baseline):
            blockers.append(
                {
                    "code": "particle-reconciliation-factor-population-mismatch",
                    "update_id": str(factor["update_id"]),
                    "missing_world_ids": sorted(set(baseline) - set(assessments)),
                    "extra_world_ids": sorted(set(assessments) - set(baseline)),
                }
            )
            continue
        for world_id in sorted(baseline):
            assessment = assessments[world_id]
            factor_identity = (
                str(assessment["world_status"]),
                str(assessment["valuation_sha256"]),
                str(assessment["custody_sha256"]),
            )
            if factor_identity != _particle_identity(baseline[world_id]):
                blockers.append(
                    {
                        "code": "particle-reconciliation-factor-custody-mismatch",
                        "update_id": str(factor["update_id"]),
                        "world_id": world_id,
                    }
                )
    return blockers


def compute_factor_reconciliation(
    *,
    baseline_bank: dict[str, Any],
    current_bank: dict[str, Any],
    included_factors: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Replay complete authorized likelihood factors from a fixed base in log space.

    Zero base mass or a zero likelihood extinguishes a member without introducing
    non-finite JSON values.  Positive members are normalized with a max-shifted
    log-sum-exp calculation, preventing long chains of tiny factors from silently
    underflowing before normalization.
    """
    factors = list(included_factors)
    blockers = factor_reconciliation_blockers(
        baseline_bank=baseline_bank,
        current_bank=current_bank,
        included_factors=factors,
    )
    if blockers:
        raise ValueError("particle factor ledger is not compatible with the current population")
    if baseline_bank["normalization_status"] != "normalized":
        raise ValueError("particle reconciliation baseline has zero mass")

    current_by_world = {
        str(item["world_id"]): item for item in current_bank["particles"]
    }
    factor_maps = [
        {
            str(item["world_id"]): item
            for item in factor.get("assessments", [])
        }
        for factor in factors
    ]
    members: list[dict[str, Any]] = []
    finite_log_scores: list[float] = []
    for particle in baseline_bank["particles"]:
        world_id = str(particle["world_id"])
        base_probability = float(particle["probability"])
        log_factor_terms: list[float] = []
        extinguished_by_update_id: str | None = None
        if base_probability <= 0.0:
            log_score: float | None = None
        else:
            for factor, factor_map in zip(factors, factor_maps):
                likelihood = float(factor_map[world_id]["likelihood"])
                if likelihood <= 0.0:
                    extinguished_by_update_id = str(factor["update_id"])
                    break
                log_factor_terms.append(math.log(likelihood))
            if extinguished_by_update_id is None:
                log_factor_sum = math.fsum(log_factor_terms)
                log_score = math.log(base_probability) + log_factor_sum
                finite_log_scores.append(log_score)
            else:
                log_score = None
        current = current_by_world[world_id]
        members.append(
            {
                "world_id": world_id,
                "world_status": str(particle["status"]),
                "current_weight": float(current["raw_weight"]),
                "current_probability": float(current["probability"]),
                "base_weight": float(particle["raw_weight"]),
                "base_probability": base_probability,
                "log_factor_sum": (
                    None
                    if log_score is None
                    else log_score - math.log(base_probability)
                ),
                "extinguished_by_update_id": extinguished_by_update_id,
                "log_score": log_score,
                "posterior_probability": 0.0,
                "valuation_sha256": particle["valuation_sha256"],
                "custody_sha256": particle["custody_sha256"],
            }
        )
    if not finite_log_scores:
        raise ValueError("all reconciled worlds have zero posterior mass")
    maximum_log_score = max(finite_log_scores)
    scaled_by_world: dict[str, float] = {}
    for item in members:
        log_score = item["log_score"]
        scaled_by_world[item["world_id"]] = (
            0.0 if log_score is None else math.exp(float(log_score) - maximum_log_score)
        )
    scaled_sum = math.fsum(scaled_by_world.values())
    if not math.isfinite(scaled_sum) or scaled_sum <= 0.0:
        raise ValueError("particle reconciliation normalization failed")
    for item in members:
        item["posterior_probability"] = scaled_by_world[item["world_id"]] / scaled_sum
        # log_score is an internal calculation. The separately stored base and
        # log-factor sum are sufficient to reproduce it and avoid redundant state.
        item.pop("log_score")

    base_stats = distribution_statistics(item["base_probability"] for item in members)
    current_stats = distribution_statistics(item["current_probability"] for item in members)
    posterior_stats = distribution_statistics(item["posterior_probability"] for item in members)
    information_gain = math.fsum(
        item["posterior_probability"]
        * math.log(item["posterior_probability"] / item["base_probability"])
        for item in members
        if item["posterior_probability"] > 0.0 and item["base_probability"] > 0.0
    )
    total_variation = 0.5 * math.fsum(
        abs(item["posterior_probability"] - item["current_probability"])
        for item in members
    )
    return {
        "method": PARTICLE_RECONCILIATION_METHOD,
        "log_normalization_constant": maximum_log_score + math.log(scaled_sum),
        "base_effective_sample_size": base_stats["effective_sample_size"],
        "current_effective_sample_size": current_stats["effective_sample_size"],
        "posterior_effective_sample_size": posterior_stats["effective_sample_size"],
        "base_entropy_nats": base_stats["entropy_nats"],
        "current_entropy_nats": current_stats["entropy_nats"],
        "posterior_entropy_nats": posterior_stats["entropy_nats"],
        "information_gain_from_base_nats": information_gain,
        "current_to_posterior_total_variation": total_variation,
        "extinguished_world_count": sum(
            1 for item in members if item["extinguished_by_update_id"] is not None
        ),
        "members": members,
    }
