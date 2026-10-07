#!/usr/bin/env python3
"""Recompute State/MUCC/MC-EQ/CPPC hostile-review vectors from bound surfaces.

The evidence-pack integrity checker already requires hostile rows to exist.  This
checker is narrower and harsher: it recomputes the adversarial arithmetic rows
from the source-bound cards and fails if a row merely declares ``status: pass``
without matching the independent calculation here.  It intentionally remains
non-authorizing: an internal pass does not replace external hostile review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import sys
from typing import Any

STATE_CARD = "release_queue/evidence_packs/2026.06.16-state-dependent-anonymity/STATE_ANONYMITY_CARD.json"
MUCC_CARD = "release_queue/evidence_packs/2026.06.16-committee-contact-set-privacy-in-anonymous-dht-lookups/MUCC_CONTACT_FLOOR_CARD.json"
HOSTILE_OVERLAY = "release_queue/HOSTILE_REVIEW_VECTORS.json"

STATE_SOURCE = "series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex"
MUCC_SOURCE = "series/anondht_state_series/paper2_mucc_committee_contact_privacy/paper.tex"
MCEQ_SOURCE = "series/release_and_destination/paperB_mceq_coversketch_destination_privacy/paper.tex"
CPPC_SOURCE = "series/anondht_state_series/paper3_closed_view_auditing_cppc/paper.tex"
CPPC_HOLD_NOTE = "release_queue/hold/2026.03.17-paper3-closed-view-alert-cap-repair-hold.md"
EVAL_CALIBRATION_SOURCE = "series/evaluation_series/paper3_calibration_recipes_anondht/paper.tex"
WORKED_RECEIPT = "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_receipt.json"
PUBLISHED_CALIBRATION_SOURCE = "published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/paper.tex"
PUBLISHED_CALIBRATION_RECEIPT = "published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/PUBLICATION_RECEIPT.json"
PUBLISHED_CALIBRATION_QUEUE_NOTE = "release_queue/published/2026.06.16-paper3-calibration-recipes-published.md"
CITATION_HEADS = "published/citation_heads.json"
ENDPOINT_SOURCE = "series/anonymity_series/paperA_odds_inflation_anonymity/paper.tex"
ENDPOINT_BRIDGE_SOURCE = "series/synthesis/paper5_endpoint_metrics_bridge/paper.tex"
ENDPOINT_HOLD_NOTE = "release_queue/hold/2026.03.16-paperA-posterior-mass-true-odds-repair-hold.md"
ENDPOINT_OLD_PUBLISHED_READY_NOTE = "release_queue/published_ready/2026.03.16-paperA-odds-inflation-published-ready.md"
BOSSFIGHT_SOURCE = "series/bossfight_series/paperA_bossfight_budgets/paper.tex"
BOSSFIGHT_DIAL_SOURCE = "series/bossfight_series/paperB_anondht_dial_sheet/paper.tex"
BOSSFIGHT_ADDENDUM_SOURCE = "series/bossfight_series/paperB_addendum_evidence_tables/paper.tex"
BOSSFIGHT_VERIFIER_SOURCE = "series/bossfight_series/paperC_proof_carrying_budgets/paper.tex"
OBS_WRAPPER_SOURCE = "series/synthesis/paper11_observation_attenuation/paper.tex"
TIERED_OBS_SOURCE = "series/synthesis/paper15_tiered_observation_vectors/paper.tex"
RECEIPT_SCHEMA_SOURCE = "series/synthesis/paper12_receipt_line_items_schema/paper.tex"
THREAT_WINDOW_SOURCE = "series/synthesis/paper4_threat_windows_anondht/paper.tex"
EVAL2_SOURCE = "series/evaluation_series/paper2_advantage_contracts_stealth_audits/paper.tex"
EVAL2_QUEUE_NOTE = "release_queue/candidates/2026.03.16-paper2-advantage-contracts-candidate.md"
WORKED_EXAMPLE_SOURCE = "series/synthesis/paper17_worked_example_receipt_interlock/paper.tex"
WORKED_EXAMPLE_HOLD_NOTE = "release_queue/hold/2026.03.16-paper17-worked-example-hold.md"
BOSSFIGHT_HOLD_NOTES = [
    "release_queue/hold/2026.03.16-paperA-bossfight-observation-channel-repair-hold.md",
    "release_queue/hold/2026.03.17-paperB-observation-channel-witness-hold.md",
    "release_queue/hold/2026.03.16-paperB-addendum-independence-scenario-hold.md",
    "release_queue/hold/2026.03.17-paperC-model-binding-gate-hold.md",
]
BOSSFIGHT_RETIRED_NOTES = [
    "release_queue/published_ready/2026.03.16-paperA-bossfight-budgets-published-ready.md",
    "release_queue/published_ready/2026.03.17-paperB-anondht-dial-sheet-published-ready.md",
    "release_queue/candidates/2026.03.16-paperB-addendum-evidence-tables-candidate.md",
    "release_queue/published_ready/2026.03.17-paperC-proof-carrying-budgets-published-ready.md",
]

STATE_VECTOR_IDS = {
    "copy_nat_value_as_bit_exponent",
    "multiply_by_ln2_instead_of_dividing",
    "zero_delta_sanity_control",
}
MUCC_VECTOR_IDS = {
    "beta_instead_of_one_minus_beta",
    "drop_alpha_denominator",
    "multiply_by_alpha_instead_of_dividing",
    "round_down_expected_contact_floor",
    "underbudget_three_round_schedule",
    "universal_floor_as_success_certificate",
    "optimistic_joint_model_as_mucc_marginal_certificate",
    "independent_liveness_as_correlation_robust_certificate",
    "one_sided_marginal_ceiling_as_approx_mucc",
    "two_sided_radius_without_factor_two",
    "lower_bound_liveness_as_theorem_evidence",
    "upper_yield_alpha_as_sufficiency_input",
    "live_yield_alpha_vs_lookup_concurrency_alpha",
    "outer_d_t_as_inner_n_h_alpha_calibration",
    "key_independence_as_mucc_label_uniformity",
    "exact_mucc_as_joint_contact_privacy",
}

MCEQ_VECTOR_IDS = {
    "tv_as_finite_reference_ratio_without_support_containment",
    "pairwise_tv_as_alphabet_free_maximal_leakage",
    "repeated_off_support_tag_horizon",
    "worked_fallback_vector_as_mceq_certificate",
    "support_contained_uniform_cover_bound",
    "singleton_tv_factor_two_overstatement",
    "published_calibration_inherited_mceq_claim",
}

CPPC_VECTOR_IDS = {
    "one_sided_lower_bound_as_cap_certificate",
    "natural_log_values_labeled_as_bits",
    "missing_reverse_direction",
    "rr_q_target_incompatibility",
    "rr_fixed_slot_composition",
    "fixed_slot_cap_inversion",
    "six_bit_target_impossibility",
    "delay_as_eventual_privacy_amplification",
    "bare_hash_as_hiding_commitment",
    "published_calibration_inherited_alert_claim",
}

ENDPOINT_VECTOR_IDS = {
    "pml_mass_as_true_odds",
    "prior_cap_true_odds_conversion",
    "hockey_stick_delta_as_tail_probability",
    "tail_implies_hockey_stick_not_converse",
    "singleton_tv_factor_two_overpayment",
    "published_legacy_odds_wording_as_true_odds",
    "published_ready_semantic_alias_scan",
}

BOSSFIGHT_VECTOR_IDS = {
    "equal_observation_marginals_not_independent_erasure",
    "correlated_contacts_break_independent_any_hit",
    "partial_subset_target_can_be_erased",
    "retrospective_pml_not_no_overshoot_filter",
    "equal_share_not_empirical_average",
    "arithmetic_verifier_without_channel_binding",
    "marginal_tiers_can_have_joint_synergy",
}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def approx(actual: Any, expected: float, *, tolerance: float = 1e-12) -> bool:
    try:
        return abs(float(actual) - float(expected)) <= tolerance
    except Exception:
        return False



def binom_tail(n: int, q: float, threshold: int) -> float:
    q = max(0.0, min(1.0, float(q)))
    if threshold <= 0:
        return 1.0
    if threshold > n:
        return 0.0
    return sum(math.comb(n, i) * (q ** i) * ((1.0 - q) ** (n - i)) for i in range(threshold, n + 1))


def nested_committee_alpha_lower(n: int, h: int, q: float, rho: float = 0.0) -> float:
    """Independent inner-quorum liveness calibration; never substitute outer d,t."""
    if n < 0 or h < 0 or h > n:
        return 0.0
    return max(0.0, min(1.0, 1.0 - float(rho))) * binom_tail(n, q, h)


def binomial_minimum_integer_contacts(M: int, d: int, t: int, alpha: float, beta: float) -> tuple[int, float]:
    target = 1.0 - beta
    for k in range(0, M + 1):
        tail = binom_tail(d, (k / M) * alpha if M else 0.0, t)
        if tail + 1e-15 >= target:
            return k, tail
    return M, binom_tail(d, alpha, t)


def hypergeom_choose(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def hypergeom_pmf(M: int, successes: int, draws: int, hits: int) -> float:
    denom = hypergeom_choose(M, draws)
    if denom == 0:
        return 0.0
    return (hypergeom_choose(successes, hits) * hypergeom_choose(M - successes, draws - hits)) / denom


def thinned_hypergeom_tail(M: int, d: int, k: int, alpha: float, threshold: int) -> float:
    alpha = max(0.0, min(1.0, float(alpha)))
    total = 0.0
    for hits in range(0, min(d, k) + 1):
        hprob = hypergeom_pmf(M, k, d, hits)
        if hprob == 0.0:
            continue
        live_tail = sum(math.comb(hits, live) * (alpha ** live) * ((1.0 - alpha) ** (hits - live)) for live in range(threshold, hits + 1))
        total += hprob * live_tail
    return total


def thinned_hypergeom_minimum_contacts(M: int, d: int, t: int, alpha: float, beta: float) -> tuple[int, float]:
    target = 1.0 - beta
    for k in range(0, M + 1):
        tail = thinned_hypergeom_tail(M, d, k, alpha, t)
        if tail + 1e-15 >= target:
            return k, tail
    return M, thinned_hypergeom_tail(M, d, M, alpha, t)

def mucc_marginal_independent_liveness_lower_bound(d: int, t: int, alpha: float, mean_destination_contacts: float) -> tuple[float, dict[str, float | int]]:
    """Independently compute the lower convex envelope of Binomial tails."""
    mean = max(0.0, min(float(d), float(mean_destination_contacts)))
    values = [binom_tail(h, alpha, t) for h in range(d + 1)]
    best = float("inf")
    witness: dict[str, float | int] = {"lower_support": 0, "upper_support": 0, "upper_weight": 0.0}
    tol = 1e-12
    for lo in range(d + 1):
        for hi in range(lo, d + 1):
            if lo == hi:
                if abs(mean - lo) > tol:
                    continue
                candidate = values[lo]
                upper_weight = 0.0
            else:
                if mean < lo - tol or mean > hi + tol:
                    continue
                upper_weight = (mean - lo) / (hi - lo)
                candidate = (1.0 - upper_weight) * values[lo] + upper_weight * values[hi]
            if candidate < best - tol:
                best = candidate
                witness = {"lower_support": lo, "upper_support": hi, "upper_weight": upper_weight}
    if best == float("inf"):
        raise ValueError(f"no convex-envelope witness for mean={mean}")
    return best, witness


def mucc_marginal_independent_minimum_contacts(M: int, d: int, t: int, alpha: float, beta: float) -> tuple[int, float, dict[str, float | int]]:
    target = 1.0 - beta
    for k in range(M + 1):
        value, witness = mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * k / M if M else 0.0)
        if value + 1e-15 >= target:
            return k, value, witness
    value, witness = mucc_marginal_independent_liveness_lower_bound(d, t, alpha, float(d))
    return M, value, witness


def mean_only_liveness_success_lower_bound(d: int, t: int, expected_live_responses_lower: float) -> float:
    if t <= 0:
        return 1.0
    if t > d:
        return 0.0
    return max(0.0, min(1.0, (float(expected_live_responses_lower) - (t - 1)) / (d - t + 1)))


def mean_only_required_contacts_unclipped(M: int, d: int, t: int, alpha: float, beta: float) -> int:
    target_mean_live = (t - 1) + (d - t + 1) * (1.0 - beta)
    if alpha <= 0.0 or d <= 0:
        return M + 1
    return math.ceil((M * target_mean_live / (alpha * d)) - 1e-12)



def approximate_mucc_diameter_contact_floor(M: int, d: int, t: int, alpha: float, beta: float, delta: float) -> tuple[float, float, bool]:
    """Sharp contact floor from a global marginal-diameter contract."""
    if alpha <= 0.0 or d <= 0:
        return float("inf"), float("inf"), False
    A = ((1.0 - beta) * t) / (alpha * d)
    if A > 1.0 + 1e-15:
        return A, float("inf"), False
    floor = d * A + max(0, M - d) * max(0.0, A - max(0.0, float(delta)))
    return A, floor, True


def one_sided_public_counterexample(M: int, d: int, t: int, alpha: float, beta: float) -> dict[str, float]:
    """Recompute the explicit public-card one-sided-envelope attack."""
    if alpha <= 0.0 or d <= 0:
        return {
            "one_sided_p": 0.0,
            "one_sided_eta": 0.0,
            "destination_contact_marginal": 0.0,
            "nondestination_contact_marginal": 0.0,
            "success_probability": max(0.0, 1.0 - beta),
            "live_marginal": 0.0,
            "conditional_live_yield": 0.0,
            "extra_contact_probability_on_success_nonlive_destination": 0.0,
            "expected_total_contacts": 0.0,
            "wrong_Mp_cover_floor": 0.0,
            "global_marginal_diameter": 0.0,
        }
    A = ((1.0 - beta) * t) / (alpha * d)
    success = 1.0 - beta
    live_fraction_on_success = t / d
    denominator = 1.0 - live_fraction_on_success
    extra_contact_probability = 0.0 if denominator <= 0.0 else (A / success - live_fraction_on_success) / denominator
    live_marginal = success * live_fraction_on_success
    return {
        "one_sided_p": A,
        "one_sided_eta": 0.0,
        "destination_contact_marginal": A,
        "nondestination_contact_marginal": 0.0,
        "success_probability": success,
        "live_marginal": live_marginal,
        "conditional_live_yield": live_marginal / A if A > 0.0 else 0.0,
        "extra_contact_probability_on_success_nonlive_destination": extra_contact_probability,
        "expected_total_contacts": d * A,
        "wrong_Mp_cover_floor": M * A,
        "global_marginal_diameter": A,
    }


def exact_mucc_full_leakage_attack(M: int, d: int, t: int, alpha: float) -> dict[str, Any]:
    """Independent enumeration of the two-orbit counterexample in the MUCC source."""
    if M != 256 or d != 8 or t != 4:
        raise ValueError("full-leakage attack is pinned to the public MUCC tuple")
    universe = frozenset(range(M))
    destination_rows = (frozenset(range(8)), frozenset(range(8, 16)))
    template_rows = (frozenset((0, 1, 2, 3, 4, 5)), frozenset((0, 1, 2, 3, 4, 6)))
    supports: list[set[frozenset[int]]] = []
    all_marginals: list[float] = []
    successes: list[float] = []
    y_rows: list[dict[str, int]] = []
    for destination, template in zip(destination_rows, template_rows):
        support: set[frozenset[int]] = set()
        contact_tallies = [0] * M
        y_tallies: dict[int, int] = {}
        success_total = 0.0
        for u in range(M):
            omissions = frozenset((u + a) % M for a in template)
            contacts = universe.difference(omissions)
            support.add(contacts)
            for j in contacts:
                contact_tallies[j] += 1
            y = len(contacts.intersection(destination))
            y_tallies[y] = y_tallies.get(y, 0) + 1
            success_total += binom_tail(y, alpha, t)
        supports.append(support)
        all_marginals.extend(count / M for count in contact_tallies)
        successes.append(success_total / M)
        y_rows.append({str(k): v for k, v in sorted(y_tallies.items())})
    overlap = len(supports[0] & supports[1])
    return {
        "fixed_contact_count": M - len(template_rows[0]),
        "contact_marginal": (M - len(template_rows[0])) / M,
        "minimum_contact_marginal": min(all_marginals),
        "maximum_contact_marginal": max(all_marginals),
        "exact_mucc_marginals": max(all_marginals) - min(all_marginals) <= 1e-15,
        "conditional_support_size_D0": len(supports[0]),
        "conditional_support_size_D1": len(supports[1]),
        "conditional_support_intersection_size": overlap,
        "total_variation_distance": 1.0 if overlap == 0 else 0.0,
        "bayes_optimal_destination_recovery": 1.0 if overlap == 0 else None,
        "mutual_information_bits_uniform_binary_destination": 1.0 if overlap == 0 else None,
        "success_probability_D0": successes[0],
        "success_probability_D1": successes[1],
        "destination_contact_count_multiplicities": y_rows,
    }

def vector_map(hostile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    vectors = hostile.get("vectors", []) if isinstance(hostile.get("vectors"), list) else []
    out: dict[str, dict[str, Any]] = {}
    for row in vectors:
        if isinstance(row, dict) and row.get("id"):
            out[str(row["id"])] = row
    return out


def base_hostile_failures(hostile: dict[str, Any], required_ids: set[str], label: str) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    vectors = vector_map(hostile)
    missing = sorted(required_ids - set(vectors))
    failed = sorted(row_id for row_id, row in vectors.items() if row.get("status") != "pass")
    if hostile.get("status") != "pass":
        failures.append({"category": f"{label}_hostile_status_not_pass", "status": hostile.get("status")})
    if hostile.get("review_class") != "internal_hostile_arithmetic_vectors":
        failures.append({"category": f"{label}_wrong_review_class", "review_class": hostile.get("review_class")})
    if hostile.get("external_reviewer_signoff") != "missing":
        failures.append({"category": f"{label}_external_signoff_not_missing", "external_reviewer_signoff": hostile.get("external_reviewer_signoff")})
    if hostile.get("blocking_publication_until_external_review") is not True:
        failures.append({"category": f"{label}_external_review_not_publication_blocking"})
    if missing:
        failures.append({"category": f"{label}_missing_vector_ids", "missing": missing})
    if failed:
        failures.append({"category": f"{label}_vector_status_not_pass", "failed_vector_ids": failed})
    return failures


def require(row: dict[str, Any], checks: list[tuple[str, bool, Any, Any]], failures: list[dict[str, Any]], vector_id: str) -> None:
    for field, ok, expected, actual in checks:
        if not ok:
            failures.append({
                "category": "hostile_vector_value_mismatch",
                "vector_id": vector_id,
                "field": field,
                "expected": expected,
                "actual": actual,
            })


def check_state(root: pathlib.Path, release: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    card = load_json(root / STATE_CARD)
    values = card.get("card_values", {}) if isinstance(card.get("card_values"), dict) else {}
    source_hash = sha256_file(root / STATE_SOURCE)
    if card.get("source_tex") != STATE_SOURCE:
        failures.append({"category": "state_card_source_path_mismatch", "actual": card.get("source_tex"), "expected": STATE_SOURCE})
    if card.get("source_sha256") != source_hash:
        failures.append({"category": "state_card_source_sha256_mismatch", "actual": card.get("source_sha256"), "expected": source_hash})

    overlay_entry = next((row for row in overlay.get("entries", []) if isinstance(row, dict) and row.get("source_tex") == STATE_SOURCE), None)
    if not isinstance(overlay_entry, dict):
        failures.append({"category": "state_overlay_entry_missing", "overlay": HOSTILE_OVERLAY})
        hostile: dict[str, Any] = {}
    else:
        if overlay_entry.get("source_sha256") != source_hash:
            failures.append({"category": "state_overlay_source_sha256_mismatch", "actual": overlay_entry.get("source_sha256"), "expected": source_hash})
        hostile = overlay_entry.get("hostile_review", {}) if isinstance(overlay_entry.get("hostile_review"), dict) else {}

    failures.extend(base_hostile_failures(hostile, STATE_VECTOR_IDS, "state"))
    vectors = vector_map(hostile)
    delta = float(values.get("delta", 0.0))
    tau = float(values.get("temperature_tau", 0.0))
    epochs = int(values.get("horizon_epochs", 0))
    eps_nat = 2.0 * delta / tau if tau else 0.0
    eps_bits = eps_nat / math.log(2.0) if eps_nat else 0.0
    horizon_bits = epochs * eps_bits
    expected_odds = 2.0 ** eps_bits if eps_bits else 1.0

    row = vectors.get("copy_nat_value_as_bit_exponent", {})
    require(row, [
        ("wrong_epsilon_bits", approx(row.get("wrong_epsilon_bits"), eps_nat), eps_nat, row.get("wrong_epsilon_bits")),
        ("correct_epsilon_bits", approx(row.get("correct_epsilon_bits"), eps_bits), eps_bits, row.get("correct_epsilon_bits")),
        ("wrong_horizon_bits", approx(row.get("wrong_horizon_bits"), epochs * eps_nat), epochs * eps_nat, row.get("wrong_horizon_bits")),
        ("correct_horizon_bits", approx(row.get("correct_horizon_bits"), horizon_bits), horizon_bits, row.get("correct_horizon_bits")),
        ("wrong_per_epoch_odds", approx(row.get("wrong_per_epoch_odds"), 2.0 ** eps_nat if eps_nat else 1.0), 2.0 ** eps_nat if eps_nat else 1.0, row.get("wrong_per_epoch_odds")),
        ("correct_per_epoch_odds", approx(row.get("correct_per_epoch_odds"), expected_odds), expected_odds, row.get("correct_per_epoch_odds")),
        ("understatement_bits_per_epoch", approx(row.get("understatement_bits_per_epoch"), eps_bits - eps_nat), eps_bits - eps_nat, row.get("understatement_bits_per_epoch")),
        ("understatement_bits_over_horizon", approx(row.get("understatement_bits_over_horizon"), horizon_bits - epochs * eps_nat), horizon_bits - epochs * eps_nat, row.get("understatement_bits_over_horizon")),
    ], failures, "copy_nat_value_as_bit_exponent")

    row = vectors.get("multiply_by_ln2_instead_of_dividing", {})
    wrong_bits = eps_nat * math.log(2.0)
    require(row, [
        ("wrong_epsilon_bits", approx(row.get("wrong_epsilon_bits"), wrong_bits), wrong_bits, row.get("wrong_epsilon_bits")),
        ("correct_epsilon_bits", approx(row.get("correct_epsilon_bits"), eps_bits), eps_bits, row.get("correct_epsilon_bits")),
        ("wrong_horizon_bits", approx(row.get("wrong_horizon_bits"), epochs * wrong_bits), epochs * wrong_bits, row.get("wrong_horizon_bits")),
        ("correct_horizon_bits", approx(row.get("correct_horizon_bits"), horizon_bits), horizon_bits, row.get("correct_horizon_bits")),
        ("wrong_per_epoch_odds", approx(row.get("wrong_per_epoch_odds"), 2.0 ** wrong_bits if wrong_bits else 1.0), 2.0 ** wrong_bits if wrong_bits else 1.0, row.get("wrong_per_epoch_odds")),
        ("correct_per_epoch_odds", approx(row.get("correct_per_epoch_odds"), expected_odds), expected_odds, row.get("correct_per_epoch_odds")),
        ("understatement_bits_per_epoch", approx(row.get("understatement_bits_per_epoch"), eps_bits - wrong_bits), eps_bits - wrong_bits, row.get("understatement_bits_per_epoch")),
        ("understatement_bits_over_horizon", approx(row.get("understatement_bits_over_horizon"), horizon_bits - epochs * wrong_bits), horizon_bits - epochs * wrong_bits, row.get("understatement_bits_over_horizon")),
    ], failures, "multiply_by_ln2_instead_of_dividing")

    row = vectors.get("zero_delta_sanity_control", {})
    require(row, [
        ("delta", approx(row.get("delta"), 0.0), 0.0, row.get("delta")),
        ("epsilon_nat", approx(row.get("epsilon_nat"), 0.0), 0.0, row.get("epsilon_nat")),
        ("epsilon_bits", approx(row.get("epsilon_bits"), 0.0), 0.0, row.get("epsilon_bits")),
        ("per_epoch_odds", approx(row.get("per_epoch_odds"), 1.0), 1.0, row.get("per_epoch_odds")),
    ], failures, "zero_delta_sanity_control")

    return {
        "target": "State-Dependent Anonymity nat/bit accountant boundary",
        "source_tex": STATE_SOURCE,
        "source_sha256": source_hash,
        "evidence_card": STATE_CARD,
        "hostile_vector_source": HOSTILE_OVERLAY,
        "status": "pass" if not failures else "fail",
        "vector_ids_checked": sorted(STATE_VECTOR_IDS),
        "recomputed_values": {
            "epsilon_nat": eps_nat,
            "epsilon_bits": eps_bits,
            "horizon_epochs": epochs,
            "horizon_bits": horizon_bits,
            "per_epoch_odds": expected_odds,
        },
        "failures": failures,
    }


def check_mucc(root: pathlib.Path, release: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    card = load_json(root / MUCC_CARD)
    values = card.get("card_values", {}) if isinstance(card.get("card_values"), dict) else {}
    source_hash = sha256_file(root / MUCC_SOURCE)
    if card.get("generated_for_revision") != release.get("revision"):
        failures.append({"category": "mucc_card_revision_not_current", "actual": card.get("generated_for_revision"), "expected": release.get("revision")})
    if card.get("checked_bundle") != release.get("bundle"):
        failures.append({"category": "mucc_card_bundle_not_current", "actual": card.get("checked_bundle"), "expected": release.get("bundle")})
    if card.get("source_tex") != MUCC_SOURCE:
        failures.append({"category": "mucc_card_source_path_mismatch", "actual": card.get("source_tex"), "expected": MUCC_SOURCE})
    if card.get("source_sha256") != source_hash:
        failures.append({"category": "mucc_card_source_sha256_mismatch", "actual": card.get("source_sha256"), "expected": source_hash})

    hostile = values.get("hostile_review", {}) if isinstance(values.get("hostile_review"), dict) else {}
    failures.extend(base_hostile_failures(hostile, MUCC_VECTOR_IDS, "mucc"))
    vectors = vector_map(hostile)

    M = int(values.get("committee_universe_M", 0))
    d = int(values.get("destination_replication_d", 0))
    t = int(values.get("live_threshold_t", 0))
    alpha = float(values.get("alpha", 0.0))
    beta = float(values.get("beta", 0.0))
    correct_p = (1.0 - beta) * t / (alpha * d) if alpha and d else 0.0
    correct_k0 = M * correct_p
    success_target = 1.0 - beta
    ceil_floor = math.ceil(correct_k0 - 1e-12)

    iid_tail_at_universal = binom_tail(d, (ceil_floor / M) * alpha if M else 0.0, t)
    iid_min_k, iid_min_tail = binomial_minimum_integer_contacts(M, d, t, alpha, beta)
    iid_predecessor_k = max(0, iid_min_k - 1)
    iid_predecessor_tail = binom_tail(d, (iid_predecessor_k / M) * alpha if M else 0.0, t)

    hypergeom_tail_at_universal = thinned_hypergeom_tail(M, d, ceil_floor, alpha, t)
    hypergeom_min_k, hypergeom_min_tail = thinned_hypergeom_minimum_contacts(M, d, t, alpha, beta)
    hypergeom_predecessor_k = max(0, hypergeom_min_k - 1)
    hypergeom_predecessor_tail = thinned_hypergeom_tail(M, d, hypergeom_predecessor_k, alpha, t)

    robust_tail_at_universal, robust_universal_witness = mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * ceil_floor / M if M else 0.0)
    robust_tail_at_optimistic, robust_optimistic_witness = mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * iid_min_k / M if M else 0.0)
    robust_min_k, robust_min_tail, robust_min_witness = mucc_marginal_independent_minimum_contacts(M, d, t, alpha, beta)
    robust_predecessor_k = max(0, robust_min_k - 1)
    robust_predecessor_tail, robust_predecessor_witness = mucc_marginal_independent_liveness_lower_bound(d, t, alpha, d * robust_predecessor_k / M if M else 0.0)

    mean_only_full_contact = mean_only_liveness_success_lower_bound(d, t, alpha * d)
    mean_only_required = mean_only_required_contacts_unclipped(M, d, t, alpha, beta)
    approx_attack = one_sided_public_counterexample(M, d, t, alpha, beta)
    perfect_leakage_attack = exact_mucc_full_leakage_attack(M, d, t, alpha)
    approx_radius_eta = 0.05
    approx_A, approx_diameter_floor, approx_feasible = approximate_mucc_diameter_contact_floor(M, d, t, alpha, beta, 2.0 * approx_radius_eta)
    _, approx_wrong_single_factor_floor, _ = approximate_mucc_diameter_contact_floor(M, d, t, alpha, beta, approx_radius_eta)
    approx_legacy_M_eta_value = M * approx_A - M * approx_radius_eta

    inner_n = int(values.get("inner_committee_members_n", 0))
    inner_h = int(values.get("inner_quorum_h", 0))
    inner_q = float(values.get("inner_member_reachability_q", 0.0))
    inner_rho = float(values.get("inner_common_outage_rho", 0.0))
    correct_inner_alpha = nested_committee_alpha_lower(inner_n, inner_h, inner_q, inner_rho)
    forbidden_outer_as_inner_alpha = nested_committee_alpha_lower(d, t, inner_q, inner_rho)
    nested_alpha_overstatement = forbidden_outer_as_inner_alpha - correct_inner_alpha
    nested_alpha_overstatement_ratio = (forbidden_outer_as_inner_alpha / correct_inner_alpha) if correct_inner_alpha > 0.0 else float("inf")

    underbudget = int(values.get("underbudget_total_contacts", 0))
    exact_upper_guard = values.get("exact_or_upper_yield_guard_present") is True
    lower_bound_guard = values.get("lower_bound_non_theorem_guard_present") is True
    live_factor_guard = values.get("live_factor_non_substitution_guard_present") is True
    alpha_direction_guard = values.get("alpha_direction_non_substitution_guard_present") is True
    nested_quorum_guard = values.get("nested_quorum_parameter_guard_present") is True
    label_uniformity_guard = values.get("key_independence_label_uniformity_guard_present") is True
    joint_privacy_guard = values.get("joint_contact_privacy_nonclaim_guard_present") is True
    phantom_churn_table_pointer_removed = values.get("phantom_churn_table_pointer_removed") is True

    row = vectors.get("beta_instead_of_one_minus_beta", {})
    wrong_p = beta * t / (alpha * d) if alpha and d else 0.0
    require(row, [
        ("wrong_p_floor", approx(row.get("wrong_p_floor"), wrong_p), wrong_p, row.get("wrong_p_floor")),
        ("wrong_expected_contact_floor", approx(row.get("wrong_expected_contact_floor"), M * wrong_p), M * wrong_p, row.get("wrong_expected_contact_floor")),
        ("correct_p_floor", approx(row.get("correct_p_floor"), correct_p), correct_p, row.get("correct_p_floor")),
        ("correct_expected_contact_floor", approx(row.get("correct_expected_contact_floor"), correct_k0), correct_k0, row.get("correct_expected_contact_floor")),
        ("understatement_contacts", approx(row.get("understatement_contacts"), correct_k0 - M * wrong_p), correct_k0 - M * wrong_p, row.get("understatement_contacts")),
    ], failures, "beta_instead_of_one_minus_beta")

    row = vectors.get("drop_alpha_denominator", {})
    no_alpha = M * (1.0 - beta) * t / d if d else 0.0
    require(row, [
        ("wrong_expected_contact_floor", approx(row.get("wrong_expected_contact_floor"), no_alpha), no_alpha, row.get("wrong_expected_contact_floor")),
        ("correct_expected_contact_floor", approx(row.get("correct_expected_contact_floor"), correct_k0), correct_k0, row.get("correct_expected_contact_floor")),
        ("understatement_contacts", approx(row.get("understatement_contacts"), correct_k0 - no_alpha), correct_k0 - no_alpha, row.get("understatement_contacts")),
    ], failures, "drop_alpha_denominator")

    row = vectors.get("multiply_by_alpha_instead_of_dividing", {})
    alpha_mult = M * (1.0 - beta) * t * alpha / d if d else 0.0
    require(row, [
        ("wrong_expected_contact_floor", approx(row.get("wrong_expected_contact_floor"), alpha_mult), alpha_mult, row.get("wrong_expected_contact_floor")),
        ("correct_expected_contact_floor", approx(row.get("correct_expected_contact_floor"), correct_k0), correct_k0, row.get("correct_expected_contact_floor")),
        ("understatement_contacts", approx(row.get("understatement_contacts"), correct_k0 - alpha_mult), correct_k0 - alpha_mult, row.get("understatement_contacts")),
    ], failures, "multiply_by_alpha_instead_of_dividing")

    row = vectors.get("round_down_expected_contact_floor", {})
    require(row, [
        ("wrong_expected_contact_floor", approx(row.get("wrong_expected_contact_floor"), math.floor(correct_k0)), math.floor(correct_k0), row.get("wrong_expected_contact_floor")),
        ("correct_expected_contact_floor_ceiling", int(row.get("correct_expected_contact_floor_ceiling", -1)) == ceil_floor, ceil_floor, row.get("correct_expected_contact_floor_ceiling")),
        ("correct_expected_contact_floor", approx(row.get("correct_expected_contact_floor"), correct_k0), correct_k0, row.get("correct_expected_contact_floor")),
    ], failures, "round_down_expected_contact_floor")

    row = vectors.get("underbudget_three_round_schedule", {})
    require(row, [
        ("wrong_expected_total_contacts", int(row.get("wrong_expected_total_contacts", -1)) == underbudget, underbudget, row.get("wrong_expected_total_contacts")),
        ("correct_expected_contact_floor", approx(row.get("correct_expected_contact_floor"), correct_k0), correct_k0, row.get("correct_expected_contact_floor")),
        ("understatement_contacts", approx(row.get("understatement_contacts"), correct_k0 - underbudget), correct_k0 - underbudget, row.get("understatement_contacts")),
    ], failures, "underbudget_three_round_schedule")

    row = vectors.get("universal_floor_as_success_certificate", {})
    require(row, [
        ("wrong_expected_contact_floor", int(row.get("wrong_expected_contact_floor", -1)) == ceil_floor, ceil_floor, row.get("wrong_expected_contact_floor")),
        ("claimed_success_floor", approx(row.get("claimed_success_floor"), success_target), success_target, row.get("claimed_success_floor")),
        ("iid_binomial_success_at_universal_floor", approx(row.get("iid_binomial_success_at_universal_floor"), iid_tail_at_universal), iid_tail_at_universal, row.get("iid_binomial_success_at_universal_floor")),
        ("iid_binomial_predecessor_contacts", int(row.get("iid_binomial_predecessor_contacts", -1)) == iid_predecessor_k, iid_predecessor_k, row.get("iid_binomial_predecessor_contacts")),
        ("iid_binomial_success_at_predecessor", approx(row.get("iid_binomial_success_at_predecessor"), iid_predecessor_tail), iid_predecessor_tail, row.get("iid_binomial_success_at_predecessor")),
        ("iid_binomial_minimum_integer_contacts", int(row.get("iid_binomial_minimum_integer_contacts", -1)) == iid_min_k, iid_min_k, row.get("iid_binomial_minimum_integer_contacts")),
        ("iid_binomial_success_at_minimum", approx(row.get("iid_binomial_success_at_minimum"), iid_min_tail), iid_min_tail, row.get("iid_binomial_success_at_minimum")),
        ("thinned_hypergeom_success_at_universal_floor", approx(row.get("thinned_hypergeom_success_at_universal_floor"), hypergeom_tail_at_universal), hypergeom_tail_at_universal, row.get("thinned_hypergeom_success_at_universal_floor")),
        ("thinned_hypergeom_predecessor_contacts", int(row.get("thinned_hypergeom_predecessor_contacts", -1)) == hypergeom_predecessor_k, hypergeom_predecessor_k, row.get("thinned_hypergeom_predecessor_contacts")),
        ("thinned_hypergeom_success_at_predecessor", approx(row.get("thinned_hypergeom_success_at_predecessor"), hypergeom_predecessor_tail), hypergeom_predecessor_tail, row.get("thinned_hypergeom_success_at_predecessor")),
        ("thinned_hypergeom_minimum_integer_contacts", int(row.get("thinned_hypergeom_minimum_integer_contacts", -1)) == hypergeom_min_k, hypergeom_min_k, row.get("thinned_hypergeom_minimum_integer_contacts")),
        ("thinned_hypergeom_success_at_minimum", approx(row.get("thinned_hypergeom_success_at_minimum"), hypergeom_min_tail), hypergeom_min_tail, row.get("thinned_hypergeom_success_at_minimum")),
        ("mucc_marginal_independent_success_at_universal_floor", approx(row.get("mucc_marginal_independent_success_at_universal_floor"), robust_tail_at_universal), robust_tail_at_universal, row.get("mucc_marginal_independent_success_at_universal_floor")),
        ("understatement_contacts_vs_iid_sufficiency_floor", approx(row.get("understatement_contacts_vs_iid_sufficiency_floor"), iid_min_k - ceil_floor), iid_min_k - ceil_floor, row.get("understatement_contacts_vs_iid_sufficiency_floor")),
    ], failures, "universal_floor_as_success_certificate")

    row = vectors.get("optimistic_joint_model_as_mucc_marginal_certificate", {})
    require(row, [
        ("wrong_expected_contact_floor", int(row.get("wrong_expected_contact_floor", -1)) == iid_min_k, iid_min_k, row.get("wrong_expected_contact_floor")),
        ("mucc_marginal_independent_success_lower_bound_at_wrong_floor", approx(row.get("mucc_marginal_independent_success_lower_bound_at_wrong_floor"), robust_tail_at_optimistic), robust_tail_at_optimistic, row.get("mucc_marginal_independent_success_lower_bound_at_wrong_floor")),
        ("correct_mucc_marginal_independent_minimum_integer_contacts", int(row.get("correct_mucc_marginal_independent_minimum_integer_contacts", -1)) == robust_min_k, robust_min_k, row.get("correct_mucc_marginal_independent_minimum_integer_contacts")),
        ("correct_success_at_minimum", approx(row.get("correct_success_at_minimum"), robust_min_tail), robust_min_tail, row.get("correct_success_at_minimum")),
        ("predecessor_contacts", int(row.get("predecessor_contacts", -1)) == robust_predecessor_k, robust_predecessor_k, row.get("predecessor_contacts")),
        ("success_at_predecessor", approx(row.get("success_at_predecessor"), robust_predecessor_tail), robust_predecessor_tail, row.get("success_at_predecessor")),
        ("convex_envelope_witness_at_minimum", row.get("convex_envelope_witness_at_minimum") == robust_min_witness, robust_min_witness, row.get("convex_envelope_witness_at_minimum")),
    ], failures, "optimistic_joint_model_as_mucc_marginal_certificate")

    row = vectors.get("independent_liveness_as_correlation_robust_certificate", {})
    require(row, [
        ("wrong_expected_contact_floor", int(row.get("wrong_expected_contact_floor", -1)) == robust_min_k, robust_min_k, row.get("wrong_expected_contact_floor")),
        ("mean_only_success_lower_bound_at_full_contact", approx(row.get("mean_only_success_lower_bound_at_full_contact"), mean_only_full_contact), mean_only_full_contact, row.get("mean_only_success_lower_bound_at_full_contact")),
        ("mean_only_required_contacts_unclipped", int(row.get("mean_only_required_contacts_unclipped", -1)) == mean_only_required, mean_only_required, row.get("mean_only_required_contacts_unclipped")),
        ("committee_universe_M", int(row.get("committee_universe_M", -1)) == M, M, row.get("committee_universe_M")),
        ("certificate_possible_within_committee_universe", row.get("certificate_possible_within_committee_universe") is (mean_only_required <= M), mean_only_required <= M, row.get("certificate_possible_within_committee_universe")),
    ], failures, "independent_liveness_as_correlation_robust_certificate")

    row = vectors.get("one_sided_marginal_ceiling_as_approx_mucc", {})
    require(row, [
        ("one_sided_p", approx(row.get("one_sided_p"), approx_attack["one_sided_p"]), approx_attack["one_sided_p"], row.get("one_sided_p")),
        ("one_sided_eta", approx(row.get("one_sided_eta"), 0.0), 0.0, row.get("one_sided_eta")),
        ("destination_contact_marginal", approx(row.get("destination_contact_marginal"), approx_attack["destination_contact_marginal"]), approx_attack["destination_contact_marginal"], row.get("destination_contact_marginal")),
        ("nondestination_contact_marginal", approx(row.get("nondestination_contact_marginal"), 0.0), 0.0, row.get("nondestination_contact_marginal")),
        ("success_probability", approx(row.get("success_probability"), 1.0 - beta), 1.0 - beta, row.get("success_probability")),
        ("conditional_live_yield", approx(row.get("conditional_live_yield"), alpha), alpha, row.get("conditional_live_yield")),
        ("extra_contact_probability_on_success_nonlive_destination", approx(row.get("extra_contact_probability_on_success_nonlive_destination"), approx_attack["extra_contact_probability_on_success_nonlive_destination"]), approx_attack["extra_contact_probability_on_success_nonlive_destination"], row.get("extra_contact_probability_on_success_nonlive_destination")),
        ("expected_total_contacts", approx(row.get("expected_total_contacts"), approx_attack["expected_total_contacts"]), approx_attack["expected_total_contacts"], row.get("expected_total_contacts")),
        ("wrong_Mp_cover_floor", approx(row.get("wrong_Mp_cover_floor"), approx_attack["wrong_Mp_cover_floor"]), approx_attack["wrong_Mp_cover_floor"], row.get("wrong_Mp_cover_floor")),
        ("global_marginal_diameter", approx(row.get("global_marginal_diameter"), approx_attack["global_marginal_diameter"]), approx_attack["global_marginal_diameter"], row.get("global_marginal_diameter")),
    ], failures, "one_sided_marginal_ceiling_as_approx_mucc")

    row = vectors.get("two_sided_radius_without_factor_two", {})
    require(row, [
        ("two_sided_center_radius_eta", approx(row.get("two_sided_center_radius_eta"), approx_radius_eta), approx_radius_eta, row.get("two_sided_center_radius_eta")),
        ("implied_diameter_bound", approx(row.get("implied_diameter_bound"), 2.0 * approx_radius_eta), 2.0 * approx_radius_eta, row.get("implied_diameter_bound")),
        ("required_destination_contact_average_A", approx(row.get("required_destination_contact_average_A"), approx_A), approx_A, row.get("required_destination_contact_average_A")),
        ("wrong_floor_treating_radius_as_diameter", approx(row.get("wrong_floor_treating_radius_as_diameter"), approx_wrong_single_factor_floor), approx_wrong_single_factor_floor, row.get("wrong_floor_treating_radius_as_diameter")),
        ("legacy_one_factor_M_eta_expression", approx(row.get("legacy_one_factor_M_eta_expression"), approx_legacy_M_eta_value), approx_legacy_M_eta_value, row.get("legacy_one_factor_M_eta_expression")),
        ("correct_diameter_contact_floor", approx(row.get("correct_diameter_contact_floor"), approx_diameter_floor), approx_diameter_floor, row.get("correct_diameter_contact_floor")),
        ("overstatement_contacts", approx(row.get("overstatement_contacts"), approx_wrong_single_factor_floor - approx_diameter_floor), approx_wrong_single_factor_floor - approx_diameter_floor, row.get("overstatement_contacts")),
    ], failures, "two_sided_radius_without_factor_two")

    for vector_id, guard_expected in [
        ("lower_bound_liveness_as_theorem_evidence", bool(lower_bound_guard and exact_upper_guard)),
        ("live_yield_alpha_vs_lookup_concurrency_alpha", bool(live_factor_guard)),
    ]:
        row = vectors.get(vector_id, {})
        require(row, [
            ("guard_present", row.get("guard_present") is guard_expected, guard_expected, row.get("guard_present")),
            ("theorem_authorized_under_wrong_rule", row.get("theorem_authorized_under_wrong_rule") is False, False, row.get("theorem_authorized_under_wrong_rule")),
        ], failures, vector_id)

    row = vectors.get("upper_yield_alpha_as_sufficiency_input", {})
    require(row, [
        ("guard_present", row.get("guard_present") is alpha_direction_guard, alpha_direction_guard, row.get("guard_present")),
        ("sufficiency_authorized_under_wrong_rule", row.get("sufficiency_authorized_under_wrong_rule") is False, False, row.get("sufficiency_authorized_under_wrong_rule")),
    ], failures, "upper_yield_alpha_as_sufficiency_input")

    row = vectors.get("outer_d_t_as_inner_n_h_alpha_calibration", {})
    require(row, [
        ("outer_destination_replication_d", int(row.get("outer_destination_replication_d", -1)) == d, d, row.get("outer_destination_replication_d")),
        ("outer_live_threshold_t", int(row.get("outer_live_threshold_t", -1)) == t, t, row.get("outer_live_threshold_t")),
        ("inner_committee_members_n", int(row.get("inner_committee_members_n", -1)) == inner_n, inner_n, row.get("inner_committee_members_n")),
        ("inner_quorum_h", int(row.get("inner_quorum_h", -1)) == inner_h, inner_h, row.get("inner_quorum_h")),
        ("inner_member_reachability_q", approx(row.get("inner_member_reachability_q"), inner_q), inner_q, row.get("inner_member_reachability_q")),
        ("inner_common_outage_rho", approx(row.get("inner_common_outage_rho"), inner_rho), inner_rho, row.get("inner_common_outage_rho")),
        ("correct_inner_alpha_lower", approx(row.get("correct_inner_alpha_lower"), correct_inner_alpha), correct_inner_alpha, row.get("correct_inner_alpha_lower")),
        ("forbidden_outer_as_inner_alpha", approx(row.get("forbidden_outer_as_inner_alpha"), forbidden_outer_as_inner_alpha), forbidden_outer_as_inner_alpha, row.get("forbidden_outer_as_inner_alpha")),
        ("alpha_overstatement", approx(row.get("alpha_overstatement"), nested_alpha_overstatement), nested_alpha_overstatement, row.get("alpha_overstatement")),
        ("alpha_overstatement_ratio", approx(row.get("alpha_overstatement_ratio"), nested_alpha_overstatement_ratio), nested_alpha_overstatement_ratio, row.get("alpha_overstatement_ratio")),
        ("guard_present", row.get("guard_present") is bool(nested_quorum_guard and phantom_churn_table_pointer_removed), bool(nested_quorum_guard and phantom_churn_table_pointer_removed), row.get("guard_present")),
        ("theorem_authorized_under_wrong_rule", row.get("theorem_authorized_under_wrong_rule") is False, False, row.get("theorem_authorized_under_wrong_rule")),
    ], failures, "outer_d_t_as_inner_n_h_alpha_calibration")

    row = vectors.get("exact_mucc_as_joint_contact_privacy", {})
    require(row, [
        ("fixed_contact_count", int(row.get("fixed_contact_count", -1)) == perfect_leakage_attack["fixed_contact_count"], perfect_leakage_attack["fixed_contact_count"], row.get("fixed_contact_count")),
        ("contact_marginal", approx(row.get("contact_marginal"), perfect_leakage_attack["contact_marginal"]), perfect_leakage_attack["contact_marginal"], row.get("contact_marginal")),
        ("minimum_contact_marginal", approx(row.get("minimum_contact_marginal"), perfect_leakage_attack["minimum_contact_marginal"]), perfect_leakage_attack["minimum_contact_marginal"], row.get("minimum_contact_marginal")),
        ("maximum_contact_marginal", approx(row.get("maximum_contact_marginal"), perfect_leakage_attack["maximum_contact_marginal"]), perfect_leakage_attack["maximum_contact_marginal"], row.get("maximum_contact_marginal")),
        ("exact_mucc_marginals", row.get("exact_mucc_marginals") is True, True, row.get("exact_mucc_marginals")),
        ("conditional_support_size_D0", int(row.get("conditional_support_size_D0", -1)) == 256, 256, row.get("conditional_support_size_D0")),
        ("conditional_support_size_D1", int(row.get("conditional_support_size_D1", -1)) == 256, 256, row.get("conditional_support_size_D1")),
        ("conditional_support_intersection_size", int(row.get("conditional_support_intersection_size", -1)) == 0, 0, row.get("conditional_support_intersection_size")),
        ("total_variation_distance", approx(row.get("total_variation_distance"), 1.0), 1.0, row.get("total_variation_distance")),
        ("bayes_optimal_destination_recovery", approx(row.get("bayes_optimal_destination_recovery"), 1.0), 1.0, row.get("bayes_optimal_destination_recovery")),
        ("mutual_information_bits_uniform_binary_destination", approx(row.get("mutual_information_bits_uniform_binary_destination"), 1.0), 1.0, row.get("mutual_information_bits_uniform_binary_destination")),
        ("success_probability_D0", approx(row.get("success_probability_D0"), perfect_leakage_attack["success_probability_D0"]), perfect_leakage_attack["success_probability_D0"], row.get("success_probability_D0")),
        ("success_probability_D1", approx(row.get("success_probability_D1"), perfect_leakage_attack["success_probability_D1"]), perfect_leakage_attack["success_probability_D1"], row.get("success_probability_D1")),
        ("destination_contact_count_multiplicities", row.get("destination_contact_count_multiplicities") == perfect_leakage_attack["destination_contact_count_multiplicities"], perfect_leakage_attack["destination_contact_count_multiplicities"], row.get("destination_contact_count_multiplicities")),
        ("guard_present", row.get("guard_present") is joint_privacy_guard, joint_privacy_guard, row.get("guard_present")),
        ("privacy_authorized_under_wrong_rule", row.get("privacy_authorized_under_wrong_rule") is False, False, row.get("privacy_authorized_under_wrong_rule")),
    ], failures, "exact_mucc_as_joint_contact_privacy")

    row = vectors.get("key_independence_as_mucc_label_uniformity", {})
    require(row, [
        ("counterexample_contact_set", row.get("counterexample_contact_set") == [1], [1], row.get("counterexample_contact_set")),
        ("q_fixed_committee", approx(row.get("q_fixed_committee"), 1.0), 1.0, row.get("q_fixed_committee")),
        ("q_other_committee", approx(row.get("q_other_committee"), 0.0), 0.0, row.get("q_other_committee")),
        ("contact_set_law_destination_independent", row.get("contact_set_law_destination_independent") is True, True, row.get("contact_set_law_destination_independent")),
        ("mucc_committee_label_uniformity", row.get("mucc_committee_label_uniformity") is False, False, row.get("mucc_committee_label_uniformity")),
        ("global_marginal_diameter", approx(row.get("global_marginal_diameter"), 1.0), 1.0, row.get("global_marginal_diameter")),
        ("guard_present", row.get("guard_present") is label_uniformity_guard, label_uniformity_guard, row.get("guard_present")),
        ("theorem_authorized_under_wrong_rule", row.get("theorem_authorized_under_wrong_rule") is False, False, row.get("theorem_authorized_under_wrong_rule")),
    ], failures, "key_independence_as_mucc_label_uniformity")

    if not (
        iid_tail_at_universal < success_target
        and hypergeom_tail_at_universal < success_target
        and robust_tail_at_universal < success_target
        and iid_predecessor_tail < success_target <= iid_min_tail
        and hypergeom_predecessor_tail < success_target <= hypergeom_min_tail
        and robust_tail_at_optimistic < success_target
        and robust_predecessor_tail < success_target <= robust_min_tail
        and robust_min_k > iid_min_k
        and mean_only_full_contact < success_target
        and mean_only_required > M
        and approx_feasible
        and approx(approx_attack["conditional_live_yield"], alpha)
        and approx_attack["expected_total_contacts"] < approx_attack["wrong_Mp_cover_floor"]
        and approx_diameter_floor < approx_wrong_single_factor_floor
        and (inner_n, inner_h, inner_q, inner_rho) == (16, 11, 0.6, 0.0)
        and approx(correct_inner_alpha, 0.3288404125089791)
        and approx(forbidden_outer_as_inner_alpha, 0.8263296)
        and forbidden_outer_as_inner_alpha > correct_inner_alpha
        and nested_alpha_overstatement > 0.0
        and nested_alpha_overstatement_ratio > 1.0
        and nested_quorum_guard
        and label_uniformity_guard
        and joint_privacy_guard
        and perfect_leakage_attack["exact_mucc_marginals"]
        and perfect_leakage_attack["conditional_support_intersection_size"] == 0
        and approx(perfect_leakage_attack["total_variation_distance"], 1.0)
        and perfect_leakage_attack["success_probability_D0"] > success_target
        and perfect_leakage_attack["success_probability_D1"] > success_target
        and phantom_churn_table_pointer_removed
    ):
        failures.append({"category": "mucc_sufficiency_ladder_recomputed_condition_failed"})

    required_guard_fields = [
        "universal_floor_not_sufficiency_guard_present",
        "sharp_sufficiency_ladder_present",
        "alpha_direction_non_substitution_guard_present",
        "approximate_mucc_diameter_guard_present",
        "nested_quorum_parameter_guard_present",
        "key_independence_label_uniformity_guard_present",
        "joint_contact_privacy_nonclaim_guard_present",
        "phantom_churn_table_pointer_removed",
    ]
    for field in required_guard_fields:
        if values.get(field) is not True:
            failures.append({"category": "mucc_card_guard_missing", "field": field, "actual": values.get(field)})

    expected_card_values: list[tuple[str, Any]] = [
        ("iid_binomial_success_at_universal_floor", iid_tail_at_universal),
        ("iid_binomial_predecessor_contacts", iid_predecessor_k),
        ("iid_binomial_success_at_predecessor", iid_predecessor_tail),
        ("iid_binomial_minimum_integer_contacts_for_success", iid_min_k),
        ("iid_binomial_success_at_minimum_integer_contacts", iid_min_tail),
        ("thinned_hypergeom_success_at_universal_floor", hypergeom_tail_at_universal),
        ("thinned_hypergeom_predecessor_contacts", hypergeom_predecessor_k),
        ("thinned_hypergeom_success_at_predecessor", hypergeom_predecessor_tail),
        ("thinned_hypergeom_minimum_integer_contacts_for_success", hypergeom_min_k),
        ("thinned_hypergeom_success_at_minimum_integer_contacts", hypergeom_min_tail),
        ("mucc_marginal_independent_success_at_universal_floor", robust_tail_at_universal),
        ("mucc_marginal_independent_witness_at_universal_floor", robust_universal_witness),
        ("mucc_marginal_independent_success_at_optimistic_minimum", robust_tail_at_optimistic),
        ("mucc_marginal_independent_witness_at_optimistic_minimum", robust_optimistic_witness),
        ("mucc_marginal_independent_predecessor_contacts", robust_predecessor_k),
        ("mucc_marginal_independent_success_at_predecessor", robust_predecessor_tail),
        ("mucc_marginal_independent_witness_at_predecessor", robust_predecessor_witness),
        ("mucc_marginal_independent_minimum_integer_contacts_for_success", robust_min_k),
        ("mucc_marginal_independent_success_at_minimum_integer_contacts", robust_min_tail),
        ("mucc_marginal_independent_witness_at_minimum", robust_min_witness),
        ("mean_only_liveness_success_lower_bound_at_full_contact", mean_only_full_contact),
        ("mean_only_liveness_required_contacts_unclipped", mean_only_required),
        ("mean_only_liveness_target_certifiable_within_M", mean_only_required <= M),
        ("approximate_mucc_required_destination_contact_average_A", approx_A),
        ("one_sided_counterexample_expected_total_contacts", approx_attack["expected_total_contacts"]),
        ("one_sided_counterexample_wrong_Mp_cover_floor", approx_attack["wrong_Mp_cover_floor"]),
        ("one_sided_counterexample_global_marginal_diameter", approx_attack["global_marginal_diameter"]),
        ("two_sided_radius_example_eta", approx_radius_eta),
        ("two_sided_radius_implied_diameter", 2.0 * approx_radius_eta),
        ("two_sided_radius_correct_contact_floor", approx_diameter_floor),
        ("inner_committee_members_n", inner_n),
        ("inner_quorum_h", inner_h),
        ("inner_member_reachability_q", inner_q),
        ("inner_common_outage_rho", inner_rho),
        ("inner_alpha_lower_recomputed", correct_inner_alpha),
        ("forbidden_outer_as_inner_alpha", forbidden_outer_as_inner_alpha),
        ("nested_quorum_alpha_overstatement", nested_alpha_overstatement),
        ("nested_quorum_alpha_overstatement_ratio", nested_alpha_overstatement_ratio),
        ("perfect_leakage_fixed_contact_count", perfect_leakage_attack["fixed_contact_count"]),
        ("perfect_leakage_contact_marginal", perfect_leakage_attack["contact_marginal"]),
        ("perfect_leakage_support_intersection_size", perfect_leakage_attack["conditional_support_intersection_size"]),
        ("perfect_leakage_total_variation_distance", perfect_leakage_attack["total_variation_distance"]),
        ("perfect_leakage_bayes_recovery", perfect_leakage_attack["bayes_optimal_destination_recovery"]),
        ("perfect_leakage_mutual_information_bits", perfect_leakage_attack["mutual_information_bits_uniform_binary_destination"]),
        ("perfect_leakage_success_probability_D0", perfect_leakage_attack["success_probability_D0"]),
        ("perfect_leakage_success_probability_D1", perfect_leakage_attack["success_probability_D1"]),
        ("perfect_leakage_destination_contact_count_multiplicities", perfect_leakage_attack["destination_contact_count_multiplicities"]),
    ]
    for field, expected in expected_card_values:
        actual = values.get(field)
        if isinstance(expected, bool):
            ok = actual is expected
        elif isinstance(expected, int):
            try:
                ok = int(actual) == expected
            except Exception:
                ok = False
        elif isinstance(expected, float):
            ok = approx(actual, expected)
        else:
            ok = actual == expected
        if not ok:
            failures.append({"category": "mucc_card_ladder_value_mismatch", "field": field, "expected": expected, "actual": actual})

    return {
        "target": "MUCC contact-cost, joint-privacy nonclaim, nested-quorum, and label-symmetry boundary",
        "source_tex": MUCC_SOURCE,
        "source_sha256": source_hash,
        "evidence_card": MUCC_CARD,
        "hostile_vector_source": MUCC_CARD,
        "status": "pass" if not failures else "fail",
        "vector_ids_checked": sorted(MUCC_VECTOR_IDS),
        "recomputed_values": {
            "M": M,
            "d": d,
            "t": t,
            "alpha": alpha,
            "beta": beta,
            "p_floor": correct_p,
            "expected_contact_floor": correct_k0,
            "underbudget_total_contacts": underbudget,
            "universal_expected_contact_floor_ceiling": ceil_floor,
            "claimed_success_floor": success_target,
            "iid_binomial_success_at_universal_floor": iid_tail_at_universal,
            "iid_binomial_predecessor_contacts": iid_predecessor_k,
            "iid_binomial_success_at_predecessor": iid_predecessor_tail,
            "iid_binomial_minimum_integer_contacts": iid_min_k,
            "iid_binomial_success_at_minimum": iid_min_tail,
            "thinned_hypergeom_success_at_universal_floor": hypergeom_tail_at_universal,
            "thinned_hypergeom_predecessor_contacts": hypergeom_predecessor_k,
            "thinned_hypergeom_success_at_predecessor": hypergeom_predecessor_tail,
            "thinned_hypergeom_minimum_integer_contacts": hypergeom_min_k,
            "thinned_hypergeom_success_at_minimum": hypergeom_min_tail,
            "mucc_marginal_independent_success_at_universal_floor": robust_tail_at_universal,
            "mucc_marginal_independent_success_at_optimistic_minimum": robust_tail_at_optimistic,
            "mucc_marginal_independent_predecessor_contacts": robust_predecessor_k,
            "mucc_marginal_independent_success_at_predecessor": robust_predecessor_tail,
            "mucc_marginal_independent_minimum_integer_contacts": robust_min_k,
            "mucc_marginal_independent_success_at_minimum": robust_min_tail,
            "mean_only_liveness_success_lower_bound_at_full_contact": mean_only_full_contact,
            "mean_only_liveness_required_contacts_unclipped": mean_only_required,
            "mean_only_liveness_target_certifiable_within_M": mean_only_required <= M,
            "approximate_mucc_required_destination_contact_average_A": approx_A,
            "one_sided_counterexample_expected_total_contacts": approx_attack["expected_total_contacts"],
            "one_sided_counterexample_wrong_Mp_cover_floor": approx_attack["wrong_Mp_cover_floor"],
            "one_sided_counterexample_global_marginal_diameter": approx_attack["global_marginal_diameter"],
            "two_sided_radius_example_eta": approx_radius_eta,
            "two_sided_radius_implied_diameter": 2.0 * approx_radius_eta,
            "two_sided_radius_correct_contact_floor": approx_diameter_floor,
            "inner_committee_members_n": inner_n,
            "inner_quorum_h": inner_h,
            "inner_member_reachability_q": inner_q,
            "inner_common_outage_rho": inner_rho,
            "inner_alpha_lower_recomputed": correct_inner_alpha,
            "forbidden_outer_as_inner_alpha": forbidden_outer_as_inner_alpha,
            "nested_quorum_alpha_overstatement": nested_alpha_overstatement,
            "nested_quorum_alpha_overstatement_ratio": nested_alpha_overstatement_ratio,
            "key_independence_counterexample_global_marginal_diameter": 1.0,
            "perfect_leakage_fixed_contact_count": perfect_leakage_attack["fixed_contact_count"],
            "perfect_leakage_contact_marginal": perfect_leakage_attack["contact_marginal"],
            "perfect_leakage_support_intersection_size": perfect_leakage_attack["conditional_support_intersection_size"],
            "perfect_leakage_total_variation_distance": perfect_leakage_attack["total_variation_distance"],
            "perfect_leakage_bayes_recovery": perfect_leakage_attack["bayes_optimal_destination_recovery"],
            "perfect_leakage_mutual_information_bits": perfect_leakage_attack["mutual_information_bits_uniform_binary_destination"],
            "perfect_leakage_success_probability_D0": perfect_leakage_attack["success_probability_D0"],
            "perfect_leakage_success_probability_D1": perfect_leakage_attack["success_probability_D1"],
        },
        "failures": failures,
    }



def check_mceq(root: pathlib.Path, release: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    source_hash = sha256_file(root / MCEQ_SOURCE)
    overlay_entry = next((row for row in overlay.get("entries", []) if isinstance(row, dict) and row.get("source_tex") == MCEQ_SOURCE), None)
    if not isinstance(overlay_entry, dict):
        failures.append({"category": "mceq_overlay_entry_missing", "overlay": HOSTILE_OVERLAY})
        hostile: dict[str, Any] = {}
    else:
        if overlay_entry.get("source_sha256") != source_hash:
            failures.append({"category": "mceq_overlay_source_sha256_mismatch", "actual": overlay_entry.get("source_sha256"), "expected": source_hash})
        if overlay_entry.get("evidence_card") is not None:
            failures.append({"category": "mceq_ghost_deployment_card_present", "actual": overlay_entry.get("evidence_card")})
        hostile = overlay_entry.get("hostile_review", {}) if isinstance(overlay_entry.get("hostile_review"), dict) else {}

    failures.extend(base_hostile_failures(hostile, MCEQ_VECTOR_IDS, "mceq"))
    vectors = vector_map(hostile)
    N = 256
    delta = 0.02
    T = 6
    no_tag_probability = (1.0 - delta) ** T
    one_step_ml = math.log2(1.0 + (N - 1) * delta)
    one_step_recovery = delta + (1.0 - delta) / N
    repeated_ml = math.log2(N - (N - 1) * no_tag_probability)
    repeated_recovery = 1.0 - no_tag_probability + no_tag_probability / N
    k = 8
    epsilon = 0.005
    steps = 6
    support_ml = steps * math.log2(1.0 + k * epsilon)
    support_dinf = steps * math.log2((1.0 + k * epsilon) / (1.0 - k * epsilon))

    receipt = load_json(root / WORKED_RECEIPT)
    item = next((row for row in receipt.get("line_items", []) if isinstance(row, dict) and row.get("name") == "fallback_tiered_vector"), {})
    knobs = item.get("knobs", {}) if isinstance(item.get("knobs"), dict) else {}
    obs_model = item.get("obs_model", {}) if isinstance(item.get("obs_model"), dict) else {}
    vector_terms = obs_model.get("vector", []) if isinstance(obs_model.get("vector"), list) else []
    term_sum = sum(float(row.get("effective_b", 0.0)) for row in vector_terms if isinstance(row, dict))
    retired_fields = sorted(name for name in ("mc_eq_session_T", "per_step_epsilon_t", "conditional_independence_assumption") if name in knobs)

    row = vectors.get("tv_as_finite_reference_ratio_without_support_containment", {})
    require(row, [
        ("N", int(row.get("N", -1)) == N, N, row.get("N")),
        ("delta", approx(row.get("delta"), delta), delta, row.get("delta")),
        ("tv_to_reference", approx(row.get("tv_to_reference"), delta), delta, row.get("tv_to_reference")),
        ("pairwise_tv", approx(row.get("pairwise_tv"), delta), delta, row.get("pairwise_tv")),
        ("reference_max_divergence", row.get("reference_max_divergence") == "infinite", "infinite", row.get("reference_max_divergence")),
        ("off_support_mass", approx(row.get("off_support_mass"), delta), delta, row.get("off_support_mass")),
        ("wrong_rule_authorized", row.get("wrong_rule_authorized") is False, False, row.get("wrong_rule_authorized")),
    ], failures, "tv_as_finite_reference_ratio_without_support_containment")

    row = vectors.get("pairwise_tv_as_alphabet_free_maximal_leakage", {})
    require(row, [
        ("N", int(row.get("N", -1)) == N, N, row.get("N")),
        ("pairwise_tv", approx(row.get("pairwise_tv"), delta), delta, row.get("pairwise_tv")),
        ("maximal_leakage_bits", approx(row.get("maximal_leakage_bits"), one_step_ml), one_step_ml, row.get("maximal_leakage_bits")),
        ("uniform_prior_recovery", approx(row.get("uniform_prior_recovery"), one_step_recovery), one_step_recovery, row.get("uniform_prior_recovery")),
        ("prior_recovery", approx(row.get("prior_recovery"), 1.0 / N), 1.0 / N, row.get("prior_recovery")),
        ("multiplicative_recovery_gain", approx(row.get("multiplicative_recovery_gain"), 1.0 + (N - 1) * delta), 1.0 + (N - 1) * delta, row.get("multiplicative_recovery_gain")),
        ("wrong_rule_authorized", row.get("wrong_rule_authorized") is False, False, row.get("wrong_rule_authorized")),
    ], failures, "pairwise_tv_as_alphabet_free_maximal_leakage")

    row = vectors.get("repeated_off_support_tag_horizon", {})
    require(row, [
        ("steps", int(row.get("steps", -1)) == T, T, row.get("steps")),
        ("no_tag_probability", approx(row.get("no_tag_probability"), no_tag_probability), no_tag_probability, row.get("no_tag_probability")),
        ("maximal_leakage_bits", approx(row.get("maximal_leakage_bits"), repeated_ml), repeated_ml, row.get("maximal_leakage_bits")),
        ("uniform_prior_recovery", approx(row.get("uniform_prior_recovery"), repeated_recovery), repeated_recovery, row.get("uniform_prior_recovery")),
        ("wrong_linear_tv_to_maxleakage_rule_authorized", row.get("wrong_linear_tv_to_maxleakage_rule_authorized") is False, False, row.get("wrong_linear_tv_to_maxleakage_rule_authorized")),
    ], failures, "repeated_off_support_tag_horizon")

    row = vectors.get("worked_fallback_vector_as_mceq_certificate", {})
    require(row, [
        ("receipt_path", row.get("receipt_path") == WORKED_RECEIPT, WORKED_RECEIPT, row.get("receipt_path")),
        ("line_item", row.get("line_item") == "fallback_tiered_vector", "fallback_tiered_vector", row.get("line_item")),
        ("declared_budget_value", approx(row.get("declared_budget_value"), float(item.get("budget_value", -1.0))), item.get("budget_value"), row.get("declared_budget_value")),
        ("recomputed_observation_attenuation_sum", approx(row.get("recomputed_observation_attenuation_sum"), term_sum), term_sum, row.get("recomputed_observation_attenuation_sum")),
        ("semantic_scope", row.get("semantic_scope") == "illustrative_tiered_observation_attenuation_not_mceq", "illustrative_tiered_observation_attenuation_not_mceq", row.get("semantic_scope")),
        ("composition_evidence_status", row.get("composition_evidence_status") == "assumption_only_no_joint_channel_witness", "assumption_only_no_joint_channel_witness", row.get("composition_evidence_status")),
        ("publication_eligible", row.get("publication_eligible") is False, False, row.get("publication_eligible")),
        ("retired_mceq_fields_present", row.get("retired_mceq_fields_present") == [], [], row.get("retired_mceq_fields_present")),
        ("mceq_certificate_authorized", row.get("mceq_certificate_authorized") is False, False, row.get("mceq_certificate_authorized")),
    ], failures, "worked_fallback_vector_as_mceq_certificate")

    row = vectors.get("support_contained_uniform_cover_bound", {})
    require(row, [
        ("cover_size_k", int(row.get("cover_size_k", -1)) == k, k, row.get("cover_size_k")),
        ("tv_slack_epsilon", approx(row.get("tv_slack_epsilon"), epsilon), epsilon, row.get("tv_slack_epsilon")),
        ("steps", int(row.get("steps", -1)) == steps, steps, row.get("steps")),
        ("reference_floor_q", approx(row.get("reference_floor_q"), 1.0 / k), 1.0 / k, row.get("reference_floor_q")),
        ("maximal_leakage_bound_bits", approx(row.get("maximal_leakage_bound_bits"), support_ml), support_ml, row.get("maximal_leakage_bound_bits")),
        ("pairwise_max_divergence_bound_bits", approx(row.get("pairwise_max_divergence_bound_bits"), support_dinf), support_dinf, row.get("pairwise_max_divergence_bound_bits")),
        ("support_containment_required", row.get("support_containment_required") is True, True, row.get("support_containment_required")),
        ("positive_reference_floor_required", row.get("positive_reference_floor_required") is True, True, row.get("positive_reference_floor_required")),
    ], failures, "support_contained_uniform_cover_bound")

    row = vectors.get("singleton_tv_factor_two_overstatement", {})
    require(row, [
        ("tv_slack_delta", approx(row.get("tv_slack_delta"), delta), delta, row.get("tv_slack_delta")),
        ("correct_singleton_deviation_bound", approx(row.get("correct_singleton_deviation_bound"), delta), delta, row.get("correct_singleton_deviation_bound")),
        ("legacy_loose_l1_bound", approx(row.get("legacy_loose_l1_bound"), 2.0 * delta), 2.0 * delta, row.get("legacy_loose_l1_bound")),
        ("correct_bound_used_by_repaired_theorem", row.get("correct_bound_used_by_repaired_theorem") is True, True, row.get("correct_bound_used_by_repaired_theorem")),
    ], failures, "singleton_tv_factor_two_overstatement")

    published_text = (root / PUBLISHED_CALIBRATION_SOURCE).read_text(encoding="utf-8", errors="replace")
    published_receipt = load_json(root / PUBLISHED_CALIBRATION_RECEIPT)
    published_queue_note = (root / PUBLISHED_CALIBRATION_QUEUE_NOTE).read_text(encoding="utf-8", errors="replace")
    citation_heads = load_json(root / CITATION_HEADS)
    published_sha = sha256_file(root / PUBLISHED_CALIBRATION_SOURCE)
    published_snapshot_immutable = published_sha == published_receipt.get("published_tex_sha256")
    published_claim_present = "T\\log_2(1+2k\\delta_{eq})" in published_text and "3.55" in published_text
    queue_correction_present = "Rev0897 MC-EQ correction" in published_queue_note
    citation_warning_present = any("rev0897 MC-EQ correction" in str(warning) for warning in citation_heads.get("operator_warnings", []))
    row = vectors.get("published_calibration_inherited_mceq_claim", {})
    require(row, [
        ("published_tex_path", row.get("published_tex_path") == PUBLISHED_CALIBRATION_SOURCE, PUBLISHED_CALIBRATION_SOURCE, row.get("published_tex_path")),
        ("published_tex_sha256", row.get("published_tex_sha256") == published_sha, published_sha, row.get("published_tex_sha256")),
        ("publication_receipt_path", row.get("publication_receipt_path") == PUBLISHED_CALIBRATION_RECEIPT, PUBLISHED_CALIBRATION_RECEIPT, row.get("publication_receipt_path")),
        ("published_snapshot_immutable", row.get("published_snapshot_immutable") is True and published_snapshot_immutable, True, row.get("published_snapshot_immutable")),
        ("legacy_mceq_claim_present", row.get("legacy_mceq_claim_present") is True and published_claim_present, True, row.get("legacy_mceq_claim_present")),
        ("queue_correction_notice_present", row.get("queue_correction_notice_present") is True and queue_correction_present, True, row.get("queue_correction_notice_present")),
        ("citation_head_warning_present", row.get("citation_head_warning_present") is True and citation_warning_present, True, row.get("citation_head_warning_present")),
        ("legacy_claim_reuse_authorized", row.get("legacy_claim_reuse_authorized") is False, False, row.get("legacy_claim_reuse_authorized")),
    ], failures, "published_calibration_inherited_mceq_claim")

    source_text = (root / MCEQ_SOURCE).read_text(encoding="utf-8", errors="replace")
    required_source_fragments = [
        "No deployment MC-EQ certificate is shipped",
        "support disciplined",
        "Alphabet-amplified off-support tag attack",
        "illustrative_tiered_observation_attenuation_not_mceq",
    ]
    for fragment in required_source_fragments:
        if fragment not in source_text:
            failures.append({"category": "mceq_source_guard_missing", "fragment": fragment})
    if retired_fields:
        failures.append({"category": "worked_receipt_retired_mceq_fields_present", "fields": retired_fields})
    if not approx(term_sum, float(item.get("budget_value", -1.0))):
        failures.append({"category": "worked_receipt_observation_sum_mismatch", "sum": term_sum, "declared": item.get("budget_value")})

    return {
        "target": "MC-EQ TV/support/ratio and worked-binding boundary",
        "source_tex": MCEQ_SOURCE,
        "source_sha256": source_hash,
        "evidence_card": None,
        "hostile_vector_source": HOSTILE_OVERLAY,
        "status": "pass" if not failures else "fail",
        "vector_ids_checked": sorted(MCEQ_VECTOR_IDS),
        "recomputed_values": {
            "N": N,
            "delta": delta,
            "one_step_maximal_leakage_bits": one_step_ml,
            "one_step_uniform_prior_recovery": one_step_recovery,
            "steps": T,
            "repeated_maximal_leakage_bits": repeated_ml,
            "repeated_uniform_prior_recovery": repeated_recovery,
            "support_contained_maximal_leakage_bound_bits": support_ml,
            "support_contained_pairwise_max_divergence_bound_bits": support_dinf,
            "worked_fallback_observation_sum": term_sum,
            "worked_fallback_publication_eligible": knobs.get("publication_eligible"),
            "published_calibration_snapshot_sha256": published_sha,
            "published_calibration_legacy_claim_present": published_claim_present,
            "published_calibration_correction_notice_present": queue_correction_present and citation_warning_present,
        },
        "failures": failures,
    }


def check_cppc(root: pathlib.Path, release: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    source_hash = sha256_file(root / CPPC_SOURCE)
    overlay_entry = next((row for row in overlay.get("entries", []) if isinstance(row, dict) and row.get("source_tex") == CPPC_SOURCE), None)
    if overlay_entry is None:
        return {
            "target": "CPPC alert necessity/sufficiency, units, composition, and artifact boundary",
            "source_tex": CPPC_SOURCE,
            "source_sha256": source_hash,
            "evidence_card": None,
            "hostile_vector_source": HOSTILE_OVERLAY,
            "status": "fail",
            "vector_ids_checked": sorted(CPPC_VECTOR_IDS),
            "recomputed_values": {},
            "failures": [{"category": "cppc_overlay_entry_missing"}],
        }
    if overlay_entry.get("source_sha256") != source_hash:
        failures.append({"category": "cppc_overlay_source_sha256_mismatch", "actual": overlay_entry.get("source_sha256"), "expected": source_hash})
    hostile = overlay_entry.get("hostile_review", {}) if isinstance(overlay_entry.get("hostile_review"), dict) else {}
    failures.extend(base_hostile_failures(hostile, CPPC_VECTOR_IDS, "cppc"))
    vectors = vector_map(hostile)

    alpha = 0.02
    beta = 0.10
    delta = 0.0
    cap = 6.0
    necessary = max(math.log2((1.0 - beta - delta) / alpha), math.log2((1.0 - alpha - delta) / beta))
    row = vectors.get("one_sided_lower_bound_as_cap_certificate", {})
    require(row, [
        ("alpha", approx(row.get("alpha"), alpha), alpha, row.get("alpha")),
        ("beta", approx(row.get("beta"), beta), beta, row.get("beta")),
        ("delta", approx(row.get("delta"), delta), delta, row.get("delta")),
        ("policy_cap_bits", approx(row.get("policy_cap_bits"), cap), cap, row.get("policy_cap_bits")),
        ("necessary_lower_bound_bits", approx(row.get("necessary_lower_bound_bits"), necessary), necessary, row.get("necessary_lower_bound_bits")),
        ("counterexample_p_alarm_state0", approx(row.get("counterexample_p_alarm_state0"), 0.0), 0.0, row.get("counterexample_p_alarm_state0")),
        ("counterexample_p_alarm_state1", approx(row.get("counterexample_p_alarm_state1"), 0.9), 0.9, row.get("counterexample_p_alarm_state1")),
        ("counterexample_minimum_delta_for_finite_epsilon", approx(row.get("counterexample_minimum_delta_for_finite_epsilon"), 0.9), 0.9, row.get("counterexample_minimum_delta_for_finite_epsilon")),
        ("target_errors_satisfied", row.get("target_errors_satisfied") is True, True, row.get("target_errors_satisfied")),
        ("cap_certificate_authorized", row.get("cap_certificate_authorized") is False, False, row.get("cap_certificate_authorized")),
    ], failures, "one_sided_lower_bound_as_cap_certificate")

    nat_alpha = 0.05
    nat_beta = 0.10
    wrong_nat = math.log((1.0 - nat_beta) / nat_alpha)
    correct_bits = math.log2((1.0 - nat_beta) / nat_alpha)
    row = vectors.get("natural_log_values_labeled_as_bits", {})
    require(row, [
        ("alpha", approx(row.get("alpha"), nat_alpha), nat_alpha, row.get("alpha")),
        ("beta", approx(row.get("beta"), nat_beta), nat_beta, row.get("beta")),
        ("wrong_natural_log_value", approx(row.get("wrong_natural_log_value"), wrong_nat), wrong_nat, row.get("wrong_natural_log_value")),
        ("correct_bit_value", approx(row.get("correct_bit_value"), correct_bits), correct_bits, row.get("correct_bit_value")),
        ("wrong_label", row.get("wrong_label") == "bits", "bits", row.get("wrong_label")),
    ], failures, "natural_log_values_labeled_as_bits")

    rev_alpha = 0.05
    rev_beta = 0.01
    forward = math.log2((1.0 - rev_beta) / rev_alpha)
    reverse = math.log2((1.0 - rev_alpha) / rev_beta)
    two_sided = max(forward, reverse)
    row = vectors.get("missing_reverse_direction", {})
    require(row, [
        ("alpha", approx(row.get("alpha"), rev_alpha), rev_alpha, row.get("alpha")),
        ("beta", approx(row.get("beta"), rev_beta), rev_beta, row.get("beta")),
        ("forward_only_bits", approx(row.get("forward_only_bits"), forward), forward, row.get("forward_only_bits")),
        ("reverse_bits", approx(row.get("reverse_bits"), reverse), reverse, row.get("reverse_bits")),
        ("correct_two_sided_bits", approx(row.get("correct_two_sided_bits"), two_sided), two_sided, row.get("correct_two_sided_bits")),
    ], failures, "missing_reverse_direction")

    q = 0.1
    target_alpha = 0.02
    eps_rr = math.log2((1.0 - q) / q)
    row = vectors.get("rr_q_target_incompatibility", {})
    require(row, [
        ("q", approx(row.get("q"), q), q, row.get("q")),
        ("false_alarm_target", approx(row.get("false_alarm_target"), target_alpha), target_alpha, row.get("false_alarm_target")),
        ("minimum_public_false_alarm_with_perfect_internal_detector", approx(row.get("minimum_public_false_alarm_with_perfect_internal_detector"), q), q, row.get("minimum_public_false_alarm_with_perfect_internal_detector")),
        ("target_achievable", row.get("target_achievable") is False, False, row.get("target_achievable")),
    ], failures, "rr_q_target_incompatibility")

    row = vectors.get("rr_fixed_slot_composition", {})
    require(row, [
        ("q", approx(row.get("q"), q), q, row.get("q")),
        ("policy_cap_bits", approx(row.get("policy_cap_bits"), cap), cap, row.get("policy_cap_bits")),
        ("one_slot_upper_bound_bits", approx(row.get("one_slot_upper_bound_bits"), eps_rr), eps_rr, row.get("one_slot_upper_bound_bits")),
        ("two_slot_upper_bound_bits", approx(row.get("two_slot_upper_bound_bits"), 2.0 * eps_rr), 2.0 * eps_rr, row.get("two_slot_upper_bound_bits")),
        ("one_slot_fits", row.get("one_slot_fits") is True, True, row.get("one_slot_fits")),
        ("two_slots_fit", row.get("two_slots_fit") is False, False, row.get("two_slots_fit")),
    ], failures, "rr_fixed_slot_composition")

    hard_alpha = 0.01
    hard_beta = 0.10
    hard_floor = max(math.log2((1.0 - hard_beta) / hard_alpha), math.log2((1.0 - hard_alpha) / hard_beta))
    q_min = 1.0 / (1.0 + 2.0 ** (cap / 2.0))
    row = vectors.get("fixed_slot_cap_inversion", {})
    require(row, [
        ("slots", row.get("slots") == 2, 2, row.get("slots")),
        ("policy_cap_bits", approx(row.get("policy_cap_bits"), cap), cap, row.get("policy_cap_bits")),
        ("minimum_q_for_generic_certificate", approx(row.get("minimum_q_for_generic_certificate"), q_min), q_min, row.get("minimum_q_for_generic_certificate")),
        ("per_slot_upper_bound_bits_at_minimum_q", approx(row.get("per_slot_upper_bound_bits_at_minimum_q"), cap / 2.0), cap / 2.0, row.get("per_slot_upper_bound_bits_at_minimum_q")),
        ("composed_upper_bound_bits_at_minimum_q", approx(row.get("composed_upper_bound_bits_at_minimum_q"), cap), cap, row.get("composed_upper_bound_bits_at_minimum_q")),
        ("minimum_public_error_with_perfect_internal_detector", approx(row.get("minimum_public_error_with_perfect_internal_detector"), q_min), q_min, row.get("minimum_public_error_with_perfect_internal_detector")),
        ("q_0_1_generic_certificate_fits", row.get("q_0_1_generic_certificate_fits") is False, False, row.get("q_0_1_generic_certificate_fits")),
        ("generic_upper_bound_is_exact_loss_claim", row.get("generic_upper_bound_is_exact_loss_claim") is False, False, row.get("generic_upper_bound_is_exact_loss_claim")),
    ], failures, "fixed_slot_cap_inversion")

    row = vectors.get("six_bit_target_impossibility", {})
    require(row, [
        ("alpha", approx(row.get("alpha"), hard_alpha), hard_alpha, row.get("alpha")),
        ("beta", approx(row.get("beta"), hard_beta), hard_beta, row.get("beta")),
        ("policy_cap_bits", approx(row.get("policy_cap_bits"), cap), cap, row.get("policy_cap_bits")),
        ("necessary_lower_bound_bits", approx(row.get("necessary_lower_bound_bits"), hard_floor), hard_floor, row.get("necessary_lower_bound_bits")),
        ("target_possible_under_cap", row.get("target_possible_under_cap") is False, False, row.get("target_possible_under_cap")),
    ], failures, "six_bit_target_impossibility")

    row = vectors.get("delay_as_eventual_privacy_amplification", {})
    require(row, [
        ("eventual_plaintext_unchanged", row.get("eventual_plaintext_unchanged") is True, True, row.get("eventual_plaintext_unchanged")),
        ("delay_discount_authorized", row.get("delay_discount_authorized") is False, False, row.get("delay_discount_authorized")),
        ("later_plaintext_is_separate_release", row.get("later_plaintext_is_separate_release") is True, True, row.get("later_plaintext_is_separate_release")),
    ], failures, "delay_as_eventual_privacy_amplification")

    row = vectors.get("bare_hash_as_hiding_commitment", {})
    require(row, [
        ("low_entropy_enumeration_attack_applies", row.get("low_entropy_enumeration_attack_applies") is True, True, row.get("low_entropy_enumeration_attack_applies")),
        ("bare_hash_hiding_claim_authorized", row.get("bare_hash_hiding_claim_authorized") is False, False, row.get("bare_hash_hiding_claim_authorized")),
        ("explicit_hiding_property_required", row.get("explicit_hiding_property_required") is True, True, row.get("explicit_hiding_property_required")),
    ], failures, "bare_hash_as_hiding_commitment")

    published_text = (root / PUBLISHED_CALIBRATION_SOURCE).read_text(encoding="utf-8", errors="replace")
    published_sha = sha256_file(root / PUBLISHED_CALIBRATION_SOURCE)
    published_receipt = load_json(root / PUBLISHED_CALIBRATION_RECEIPT)
    published_snapshot_immutable = published_sha == published_receipt.get("published_tex_sha256")
    legacy_formula_present = "\\log_2((1-\\beta)/\\alpha)" in published_text or "\\log_2\\!\\left(\\frac{1-\\beta}{\\alpha}\\right)" in published_text
    legacy_431_present = "0.01 & 0.05  & 4.31" in published_text
    queue_text = (root / PUBLISHED_CALIBRATION_QUEUE_NOTE).read_text(encoding="utf-8", errors="replace")
    queue_correction = "Rev0898 alert-tax correction" in queue_text
    citation_heads = load_json(root / CITATION_HEADS)
    citation_warning = any("rev0898 alert-tax correction" in str(warning) for warning in citation_heads.get("operator_warnings", []))
    row = vectors.get("published_calibration_inherited_alert_claim", {})
    require(row, [
        ("published_tex_path", row.get("published_tex_path") == PUBLISHED_CALIBRATION_SOURCE, PUBLISHED_CALIBRATION_SOURCE, row.get("published_tex_path")),
        ("published_tex_sha256", row.get("published_tex_sha256") == published_sha, published_sha, row.get("published_tex_sha256")),
        ("legacy_one_direction_formula_present", row.get("legacy_one_direction_formula_present") is True and legacy_formula_present, True, row.get("legacy_one_direction_formula_present")),
        ("legacy_4_31_row_present", row.get("legacy_4_31_row_present") is True and legacy_431_present, True, row.get("legacy_4_31_row_present")),
        ("queue_correction_notice_present", row.get("queue_correction_notice_present") is True and queue_correction, True, row.get("queue_correction_notice_present")),
        ("citation_head_warning_present", row.get("citation_head_warning_present") is True and citation_warning, True, row.get("citation_head_warning_present")),
        ("legacy_claim_reuse_authorized", row.get("legacy_claim_reuse_authorized") is False, False, row.get("legacy_claim_reuse_authorized")),
    ], failures, "published_calibration_inherited_alert_claim")
    if not published_snapshot_immutable:
        failures.append({"category": "published_calibration_snapshot_not_immutable", "actual_sha256": published_sha, "receipt_sha256": published_receipt.get("published_tex_sha256")})

    source_text = (root / CPPC_SOURCE).read_text(encoding="utf-8", errors="replace")
    hold_text = (root / CPPC_HOLD_NOTE).read_text(encoding="utf-8", errors="replace")
    eval_text = (root / EVAL_CALIBRATION_SOURCE).read_text(encoding="utf-8", errors="replace")
    required_source_fragments = [
        "Equation~(1) is a \\emph{necessary} lower bound",
        "Randomized-response upper guarantee",
        "Delay is not eventual-observer amplification",
        "bare hash of a low-entropy alert transcript is not a hiding commitment",
        "No deployment CPPC is claimed in this archive",
    ]
    for fragment in required_source_fragments:
        if fragment not in source_text:
            failures.append({"category": "cppc_source_guard_missing", "fragment": fragment})
    for fragment in ["Corrected theorem boundary", "Hold / publication-blocked"]:
        if fragment not in hold_text:
            failures.append({"category": "cppc_hold_guard_missing", "fragment": fragment})
    eval_sha = sha256_file(root / EVAL_CALIBRATION_SOURCE)
    if eval_sha != published_sha or eval_text != published_text:
        failures.append({
            "category": "historical_calibration_series_snapshot_drift",
            "series_sha256": eval_sha,
            "published_sha256": published_sha,
            "note": "post-publication corrections must remain in citation-head/queue withdrawal surfaces rather than silently rewriting the historical series source",
        })
    if "historical series source, immutable published `paper.tex`, and rev0884 receipt remain byte-identical" not in queue_text:
        failures.append({"category": "historical_calibration_withdrawal_boundary_missing"})
    if "Figure omitted in source-only archive" in source_text:
        failures.append({"category": "cppc_ghost_figure_placeholder_present"})

    return {
        "target": "CPPC alert necessity/sufficiency, units, composition, and artifact boundary",
        "source_tex": CPPC_SOURCE,
        "source_sha256": source_hash,
        "evidence_card": None,
        "hostile_vector_source": HOSTILE_OVERLAY,
        "status": "pass" if not failures else "fail",
        "vector_ids_checked": sorted(CPPC_VECTOR_IDS),
        "recomputed_values": {
            "alpha_0_02_beta_0_10_two_sided_floor_bits": necessary,
            "natural_log_mislabeled_value": wrong_nat,
            "correct_bit_value": correct_bits,
            "reverse_direction_example_forward_bits": forward,
            "reverse_direction_example_reverse_bits": reverse,
            "reverse_direction_example_two_sided_bits": two_sided,
            "rr_q_0_1_one_slot_bits": eps_rr,
            "rr_q_0_1_two_slot_bits": 2.0 * eps_rr,
            "rr_two_slot_six_bit_minimum_q": q_min,
            "rr_two_slot_six_bit_minimum_public_error": q_min,
            "alpha_0_01_beta_0_10_two_sided_floor_bits": hard_floor,
            "published_calibration_snapshot_sha256": published_sha,
            "published_calibration_alert_correction_notice_present": queue_correction and citation_warning,
        },
        "failures": failures,
    }


def _current_published_ready_sources(root: pathlib.Path) -> list[str]:
    import re

    paths: list[str] = []
    for note in sorted((root / "release_queue" / "published_ready").glob("*.md")):
        match = re.search(r"^- Source paper: `([^`]+)`", note.read_text(encoding="utf-8", errors="replace"), flags=re.M)
        if match:
            paths.append(match.group(1))
    return paths


def _endpoint_semantic_alias_violations(root: pathlib.Path) -> list[dict[str, Any]]:
    import re

    patterns = {
        "pml_as_realized_odds_alias": re.compile(r"(?:realized\s+odds[- ]inflation\s*/\s*PML|PML\s*/\s*realized\s+odds[- ]inflation)", re.I),
        "pml_as_posterior_odds_endpoint": re.compile(r"posterior[- ]odds\s+inflation\s+is\s+the\s+endpoint", re.I),
        "pml_odds_slash_alias": re.compile(r"PML\s*/\s*odds[- ]inflation", re.I),
        "maxl_odds_slash_alias": re.compile(r"MaxL\s*/\s*odds[- ]inflation", re.I),
    }
    violations: list[dict[str, Any]] = []
    for rel in _current_published_ready_sources(root):
        path = root / rel
        if not path.exists():
            violations.append({"source_tex": rel, "pattern": "source_missing"})
            continue
        candidate = path.read_text(encoding="utf-8", errors="replace")
        for pattern_id, pattern in patterns.items():
            if pattern.search(candidate):
                violations.append({"source_tex": rel, "pattern": pattern_id})
    return violations


def check_endpoint(root: pathlib.Path, release: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    source_hash = sha256_file(root / ENDPOINT_SOURCE)
    overlay_entry = next((row for row in overlay.get("entries", []) if isinstance(row, dict) and row.get("source_tex") == ENDPOINT_SOURCE), None)
    if not isinstance(overlay_entry, dict):
        failures.append({"category": "endpoint_overlay_entry_missing", "overlay": HOSTILE_OVERLAY})
        hostile: dict[str, Any] = {}
    else:
        if overlay_entry.get("source_sha256") != source_hash:
            failures.append({"category": "endpoint_overlay_source_sha256_mismatch", "actual": overlay_entry.get("source_sha256"), "expected": source_hash})
        hostile = overlay_entry.get("hostile_review", {}) if isinstance(overlay_entry.get("hostile_review"), dict) else {}

    failures.extend(base_hostile_failures(hostile, ENDPOINT_VECTOR_IDS, "endpoint"))
    vectors = vector_map(hostile)

    # Deterministic-reveal separation: finite PML, infinite true odds.
    row = vectors.get("pml_mass_as_true_odds", {})
    require(row, [
        ("prior_probability", approx(row.get("prior_probability"), 0.5), 0.5, row.get("prior_probability")),
        ("posterior_probability_after_reveal", approx(row.get("posterior_probability_after_reveal"), 1.0), 1.0, row.get("posterior_probability_after_reveal")),
        ("pml_bits", approx(row.get("pml_bits"), 1.0), 1.0, row.get("pml_bits")),
        ("posterior_mass_factor", approx(row.get("posterior_mass_factor"), 2.0), 2.0, row.get("posterior_mass_factor")),
        ("true_odds_factor", row.get("true_odds_factor") == "infinite", "infinite", row.get("true_odds_factor")),
        ("legacy_alias_authorized", row.get("legacy_alias_authorized") is False, False, row.get("legacy_alias_authorized")),
    ], failures, "pml_mass_as_true_odds")

    N = 4096
    epsilon = 0.75
    p = 1.0 / N
    mass_factor = 2.0 ** epsilon
    true_odds_factor = mass_factor * (1.0 - p) / (1.0 - p * mass_factor)
    true_odds_bits = math.log2(true_odds_factor)
    row = vectors.get("prior_cap_true_odds_conversion", {})
    require(row, [
        ("candidate_count", int(row.get("candidate_count", -1)) == N, N, row.get("candidate_count")),
        ("prior_cap", approx(row.get("prior_cap"), p), p, row.get("prior_cap")),
        ("pml_cap_bits", approx(row.get("pml_cap_bits"), epsilon), epsilon, row.get("pml_cap_bits")),
        ("posterior_mass_factor", approx(row.get("posterior_mass_factor"), mass_factor), mass_factor, row.get("posterior_mass_factor")),
        ("no_saturation_guard", row.get("no_saturation_guard") is True, True, row.get("no_saturation_guard")),
        ("true_odds_factor", approx(row.get("true_odds_factor"), true_odds_factor), true_odds_factor, row.get("true_odds_factor")),
        ("true_odds_cap_bits", approx(row.get("true_odds_cap_bits"), true_odds_bits), true_odds_bits, row.get("true_odds_cap_bits")),
    ], failures, "prior_cap_true_odds_conversion")

    hs_delta = 0.01
    positive_tail = 0.51
    row = vectors.get("hockey_stick_delta_as_tail_probability", {})
    require(row, [
        ("epsilon_bits", approx(row.get("epsilon_bits"), 0.0), 0.0, row.get("epsilon_bits")),
        ("hockey_stick_slack", approx(row.get("hockey_stick_slack"), hs_delta), hs_delta, row.get("hockey_stick_slack")),
        ("positive_loss_tail_probability", approx(row.get("positive_loss_tail_probability"), positive_tail), positive_tail, row.get("positive_loss_tail_probability")),
        ("positive_loss_bits", approx(row.get("positive_loss_bits"), math.log2(1.02)), math.log2(1.02), row.get("positive_loss_bits")),
        ("tail_to_slack_ratio", approx(row.get("tail_to_slack_ratio"), 51.0), 51.0, row.get("tail_to_slack_ratio")),
        ("hockey_stick_as_tail_authorized", row.get("hockey_stick_as_tail_authorized") is False, False, row.get("hockey_stick_as_tail_authorized")),
    ], failures, "hockey_stick_delta_as_tail_probability")

    row = vectors.get("tail_implies_hockey_stick_not_converse", {})
    require(row, [
        ("forward_implication", row.get("forward_implication") == "tail_probability_at_most_eta_implies_hockey_stick_at_most_eta", "tail_probability_at_most_eta_implies_hockey_stick_at_most_eta", row.get("forward_implication")),
        ("converse_counterexample_hockey_stick", approx(row.get("converse_counterexample_hockey_stick"), hs_delta), hs_delta, row.get("converse_counterexample_hockey_stick")),
        ("converse_counterexample_tail", approx(row.get("converse_counterexample_tail"), positive_tail), positive_tail, row.get("converse_counterexample_tail")),
        ("converse_authorized", row.get("converse_authorized") is False, False, row.get("converse_authorized")),
    ], failures, "tail_implies_hockey_stick_not_converse")

    q_min = 0.10
    tv_delta = 0.01
    corrected = math.log2((q_min + tv_delta) / (q_min - tv_delta))
    legacy = math.log2((q_min + 2.0 * tv_delta) / (q_min - 2.0 * tv_delta))
    row = vectors.get("singleton_tv_factor_two_overpayment", {})
    require(row, [
        ("reference_floor", approx(row.get("reference_floor"), q_min), q_min, row.get("reference_floor")),
        ("tv_slack", approx(row.get("tv_slack"), tv_delta), tv_delta, row.get("tv_slack")),
        ("correct_singleton_deviation", approx(row.get("correct_singleton_deviation"), tv_delta), tv_delta, row.get("correct_singleton_deviation")),
        ("legacy_double_deviation", approx(row.get("legacy_double_deviation"), 2.0 * tv_delta), 2.0 * tv_delta, row.get("legacy_double_deviation")),
        ("corrected_ratio_bound_bits", approx(row.get("corrected_ratio_bound_bits"), corrected), corrected, row.get("corrected_ratio_bound_bits")),
        ("legacy_ratio_bound_bits", approx(row.get("legacy_ratio_bound_bits"), legacy), legacy, row.get("legacy_ratio_bound_bits")),
        ("legacy_factor_two_authorized", row.get("legacy_factor_two_authorized") is False, False, row.get("legacy_factor_two_authorized")),
    ], failures, "singleton_tv_factor_two_overpayment")

    citation_heads = load_json(root / CITATION_HEADS)
    citation_warning = any("rev0899 endpoint terminology correction" in str(warning).lower() for warning in citation_heads.get("operator_warnings", []))
    row = vectors.get("published_legacy_odds_wording_as_true_odds", {})
    require(row, [
        ("citation_head_warning_present", row.get("citation_head_warning_present") is True and citation_warning, True, row.get("citation_head_warning_present")),
        ("legacy_wording_reuse_as_true_odds_authorized", row.get("legacy_wording_reuse_as_true_odds_authorized") is False, False, row.get("legacy_wording_reuse_as_true_odds_authorized")),
        ("immutable_published_sources_rewritten", row.get("immutable_published_sources_rewritten") is False, False, row.get("immutable_published_sources_rewritten")),
    ], failures, "published_legacy_odds_wording_as_true_odds")

    violations = _endpoint_semantic_alias_violations(root)
    current_sources = _current_published_ready_sources(root)
    row = vectors.get("published_ready_semantic_alias_scan", {})
    require(row, [
        ("sources_scanned", row.get("sources_scanned") == current_sources, current_sources, row.get("sources_scanned")),
        ("violation_count", int(row.get("violation_count", -1)) == len(violations), len(violations), row.get("violation_count")),
        ("violations", row.get("violations") == violations, violations, row.get("violations")),
    ], failures, "published_ready_semantic_alias_scan")
    if violations:
        failures.append({"category": "published_ready_endpoint_semantic_aliases_present", "violations": violations})

    source_text = (root / ENDPOINT_SOURCE).read_text(encoding="utf-8", errors="replace")
    bridge_text = (root / ENDPOINT_BRIDGE_SOURCE).read_text(encoding="utf-8", errors="replace")
    hold_text = (root / ENDPOINT_HOLD_NOTE).read_text(encoding="utf-8", errors="replace") if (root / ENDPOINT_HOLD_NOTE).exists() else ""
    required_source_fragments = [
        "Posterior-Mass Inflation Anonymity",
        "One bit of PML can coexist with infinite true-odds inflation",
        "What $\\delta$ does and does not mean",
        r"\frac{Q_{\min}+\delta}{Q_{\min}-\delta}",
        "The result is a corrected endpoint theorem, not a deployment certificate",
    ]
    for fragment in required_source_fragments:
        if fragment not in source_text:
            failures.append({"category": "endpoint_source_guard_missing", "fragment": fragment})
    if "Posterior-mass inflation is PML, not posterior odds" not in bridge_text:
        failures.append({"category": "endpoint_bridge_guard_missing"})
    for fragment in ["Hold / publication-blocked", "model-level terminology and theorem-boundary repair"]:
        if fragment not in hold_text:
            failures.append({"category": "endpoint_hold_guard_missing", "fragment": fragment})
    if (root / ENDPOINT_OLD_PUBLISHED_READY_NOTE).exists():
        failures.append({"category": "endpoint_old_published_ready_note_still_present", "path": ENDPOINT_OLD_PUBLISHED_READY_NOTE})
    if not citation_warning:
        failures.append({"category": "endpoint_published_legacy_warning_missing"})

    return {
        "target": "Endpoint PML/mass/true-odds and hockey-stick/tail boundary",
        "source_tex": ENDPOINT_SOURCE,
        "source_sha256": source_hash,
        "evidence_card": None,
        "hostile_vector_source": HOSTILE_OVERLAY,
        "status": "pass" if not failures else "fail",
        "vector_ids_checked": sorted(ENDPOINT_VECTOR_IDS),
        "recomputed_values": {
            "deterministic_reveal_pml_bits": 1.0,
            "deterministic_reveal_true_odds": "infinite",
            "uniform_4096_mass_factor": mass_factor,
            "uniform_4096_true_odds_factor": true_odds_factor,
            "uniform_4096_true_odds_bits": true_odds_bits,
            "hockey_stick_counterexample_slack": hs_delta,
            "hockey_stick_counterexample_positive_loss_tail": positive_tail,
            "hockey_stick_tail_to_slack_ratio": positive_tail / hs_delta,
            "singleton_tv_corrected_bits": corrected,
            "singleton_tv_legacy_double_bits": legacy,
            "published_ready_sources_scanned": len(current_sources),
            "published_ready_semantic_alias_violations": len(violations),
        },
        "failures": failures,
    }



def check_bossfight(root: pathlib.Path, release: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    source_hash = sha256_file(root / BOSSFIGHT_SOURCE)
    overlay_entry = next((row for row in overlay.get("entries", []) if isinstance(row, dict) and row.get("source_tex") == BOSSFIGHT_SOURCE), None)
    if not isinstance(overlay_entry, dict):
        failures.append({"category": "bossfight_overlay_entry_missing", "overlay": HOSTILE_OVERLAY})
        hostile: dict[str, Any] = {}
    else:
        if overlay_entry.get("source_sha256") != source_hash:
            failures.append({"category": "bossfight_overlay_source_sha256_mismatch", "actual": overlay_entry.get("source_sha256"), "expected": source_hash})
        hostile = overlay_entry.get("hostile_review", {}) if isinstance(overlay_entry.get("hostile_review"), dict) else {}

    failures.extend(base_hostile_failures(hostile, BOSSFIGHT_VECTOR_IDS, "bossfight"))
    vectors = vector_map(hostile)

    # Equal reveal marginals do not identify an independent erasure channel.
    K, w, p = 3, 1, 0.5
    scalar_exponent = (1.0 - p) + p * K / (w + 1)
    scalar_bits = math.log2(scalar_exponent)
    actual_exponent = 0.5 + 3.0 * 0.5
    actual_bits = math.log2(actual_exponent)
    scalar_guess = scalar_exponent / K
    actual_guess = actual_exponent / K
    row = vectors.get("equal_observation_marginals_not_independent_erasure", {})
    require(row, [
        ("secret_count", int(row.get("secret_count", -1)) == K, K, row.get("secret_count")),
        ("dummy_count", int(row.get("dummy_count", -1)) == w, w, row.get("dummy_count")),
        ("per_secret_reveal_probability", approx(row.get("per_secret_reveal_probability"), p), p, row.get("per_secret_reveal_probability")),
        ("scalar_erasure_bits", approx(row.get("scalar_erasure_bits"), scalar_bits), scalar_bits, row.get("scalar_erasure_bits")),
        ("actual_maximal_leakage_bits", approx(row.get("actual_maximal_leakage_bits"), actual_bits), actual_bits, row.get("actual_maximal_leakage_bits")),
        ("scalar_exact_guess", approx(row.get("scalar_exact_guess"), scalar_guess), scalar_guess, row.get("scalar_exact_guess")),
        ("actual_exact_guess", approx(row.get("actual_exact_guess"), actual_guess), actual_guess, row.get("actual_exact_guess")),
        ("independent_erasure_inference_authorized", row.get("independent_erasure_inference_authorized") is False, False, row.get("independent_erasure_inference_authorized")),
    ], failures, "equal_observation_marginals_not_independent_erasure")

    # Equal contact marginals leave a sharp correlation interval.
    rho, m = 0.1, 10
    independent_any_hit = 1.0 - (1.0 - rho) ** m
    row = vectors.get("correlated_contacts_break_independent_any_hit", {})
    require(row, [
        ("rho", approx(row.get("rho"), rho), rho, row.get("rho")),
        ("contacts", int(row.get("contacts", -1)) == m, m, row.get("contacts")),
        ("independent_any_hit", approx(row.get("independent_any_hit"), independent_any_hit), independent_any_hit, row.get("independent_any_hit")),
        ("equal_marginal_sharp_lower", approx(row.get("equal_marginal_sharp_lower"), rho), rho, row.get("equal_marginal_sharp_lower")),
        ("equal_marginal_sharp_upper", approx(row.get("equal_marginal_sharp_upper"), min(1.0, m * rho)), min(1.0, m * rho), row.get("equal_marginal_sharp_upper")),
        ("perfect_positive_correlation_any_hit", approx(row.get("perfect_positive_correlation_any_hit"), rho), rho, row.get("perfect_positive_correlation_any_hit")),
        ("upper_bounds_only_lower_endpoint", approx(row.get("upper_bounds_only_lower_endpoint"), 0.0), 0.0, row.get("upper_bounds_only_lower_endpoint")),
        ("independent_formula_as_generic_bound_authorized", row.get("independent_formula_as_generic_bound_authorized") is False, False, row.get("independent_formula_as_generic_bound_authorized")),
    ], failures, "correlated_contacts_break_independent_any_hit")

    # In the partial-subset model the true target may be erased while dummies remain visible.
    N, k, observed_m, q = 5, 2, 1, 0.2
    denominator = math.comb(N - 1, k)
    p_target_in = (q ** observed_m) * ((1.0 - q) ** (k + 1 - observed_m)) * math.comb(N - observed_m, k - observed_m + 1) / denominator
    p_target_out = (q ** observed_m) * ((1.0 - q) ** (k + 1 - observed_m)) * math.comb(N - observed_m - 1, k - observed_m) / denominator
    row = vectors.get("partial_subset_target_can_be_erased", {})
    require(row, [
        ("N", int(row.get("N", -1)) == N, N, row.get("N")),
        ("dummy_count", int(row.get("dummy_count", -1)) == k, k, row.get("dummy_count")),
        ("observed_subset_size", int(row.get("observed_subset_size", -1)) == observed_m, observed_m, row.get("observed_subset_size")),
        ("visibility_probability", approx(row.get("visibility_probability"), q), q, row.get("visibility_probability")),
        ("probability_when_target_observed", approx(row.get("probability_when_target_observed"), p_target_in), p_target_in, row.get("probability_when_target_observed")),
        ("probability_when_target_erased", approx(row.get("probability_when_target_erased"), p_target_out), p_target_out, row.get("probability_when_target_erased")),
        ("likelihood_ratio", approx(row.get("likelihood_ratio"), p_target_in / p_target_out), p_target_in / p_target_out, row.get("likelihood_ratio")),
        ("target_erasure_probability_positive", row.get("target_erasure_probability_positive") is True, True, row.get("target_erasure_probability_positive")),
    ], failures, "partial_subset_target_can_be_erased")

    # A realized increment is visible only after the triggering release.
    cap, trigger = 0.5, 1.0
    row = vectors.get("retrospective_pml_not_no_overshoot_filter", {})
    require(row, [
        ("policy_cap_bits", approx(row.get("policy_cap_bits"), cap), cap, row.get("policy_cap_bits")),
        ("retrospective_spend_before_bits", approx(row.get("retrospective_spend_before_bits"), 0.0), 0.0, row.get("retrospective_spend_before_bits")),
        ("triggering_output_increment_bits", approx(row.get("triggering_output_increment_bits"), trigger), trigger, row.get("triggering_output_increment_bits")),
        ("retrospective_spend_after_bits", approx(row.get("retrospective_spend_after_bits"), trigger), trigger, row.get("retrospective_spend_after_bits")),
        ("overshoot_bits", approx(row.get("overshoot_bits"), trigger - cap), trigger - cap, row.get("overshoot_bits")),
        ("prospective_release_allowed", row.get("prospective_release_allowed") is False, False, row.get("prospective_release_allowed")),
        ("retrospective_log_as_preventive_filter_authorized", row.get("retrospective_log_as_preventive_filter_authorized") is False, False, row.get("retrospective_log_as_preventive_filter_authorized")),
    ], failures, "retrospective_pml_not_no_overshoot_filter")

    # B/Q is one design split, not an empirical per-round theorem.
    budget, rounds = 1.0, 2
    allocation = budget / rounds
    nonuniform = [0.8, 0.2]
    row = vectors.get("equal_share_not_empirical_average", {})
    require(row, [
        ("budget_bits", approx(row.get("budget_bits"), budget), budget, row.get("budget_bits")),
        ("round_cap", int(row.get("round_cap", -1)) == rounds, rounds, row.get("round_cap")),
        ("equal_share_bits", approx(row.get("equal_share_bits"), allocation), allocation, row.get("equal_share_bits")),
        ("valid_nonuniform_sequence", row.get("valid_nonuniform_sequence") == nonuniform, nonuniform, row.get("valid_nonuniform_sequence")),
        ("valid_nonuniform_sum_bits", approx(row.get("valid_nonuniform_sum_bits"), sum(nonuniform)), sum(nonuniform), row.get("valid_nonuniform_sum_bits")),
        ("first_round_exceeds_equal_share", row.get("first_round_exceeds_equal_share") is True, True, row.get("first_round_exceeds_equal_share")),
        ("equal_share_as_empirical_certificate_authorized", row.get("equal_share_as_empirical_certificate_authorized") is False, False, row.get("equal_share_as_empirical_certificate_authorized")),
    ], failures, "equal_share_not_empirical_average")

    # Identical model bytes can be presented by a different deployment channel.
    row = vectors.get("arithmetic_verifier_without_channel_binding", {})
    require(row, [
        ("declared_model_bits", approx(row.get("declared_model_bits"), scalar_bits), scalar_bits, row.get("declared_model_bits")),
        ("actual_channel_bits", approx(row.get("actual_channel_bits"), actual_bits), actual_bits, row.get("actual_channel_bits")),
        ("same_declared_tuple", row.get("same_declared_tuple") is True, True, row.get("same_declared_tuple")),
        ("arithmetic_checker_can_pass", row.get("arithmetic_checker_can_pass") is True, True, row.get("arithmetic_checker_can_pass")),
        ("deployment_privacy_certificate_authorized", row.get("deployment_privacy_certificate_authorized") is False, False, row.get("deployment_privacy_certificate_authorized")),
        ("required_verdict", row.get("required_verdict") == "arithmetic_valid_under_model_digest", "arithmetic_valid_under_model_digest", row.get("required_verdict")),
    ], failures, "arithmetic_verifier_without_channel_binding")

    # Marginally independent-looking tiers may reveal jointly through shared randomness.
    row = vectors.get("marginal_tiers_can_have_joint_synergy", {})
    require(row, [
        ("tier1_maximal_leakage_bits", approx(row.get("tier1_maximal_leakage_bits"), 0.0), 0.0, row.get("tier1_maximal_leakage_bits")),
        ("tier2_maximal_leakage_bits", approx(row.get("tier2_maximal_leakage_bits"), 0.0), 0.0, row.get("tier2_maximal_leakage_bits")),
        ("joint_maximal_leakage_bits", approx(row.get("joint_maximal_leakage_bits"), 1.0), 1.0, row.get("joint_maximal_leakage_bits")),
        ("secret_recovered_by_xor", row.get("secret_recovered_by_xor") is True, True, row.get("secret_recovered_by_xor")),
        ("marginal_sum_as_joint_certificate_authorized", row.get("marginal_sum_as_joint_certificate_authorized") is False, False, row.get("marginal_sum_as_joint_certificate_authorized")),
    ], failures, "marginal_tiers_can_have_joint_synergy")

    source_guards = {
        BOSSFIGHT_SOURCE: ["Equal observation rates do not identify an erasure channel", "outcome-uniform conditional envelope", "equal-share allocation", "true target can be erased"],
        BOSSFIGHT_DIAL_SOURCE: ["Cyclic reveal defeats scalar attenuation", "sharp marginal range", "non-certifying sensitivity scenario"],
        BOSSFIGHT_VERIFIER_SOURCE: ["model-binding gate", r"\textsf{VALID-UNDER-MODEL}"],
        OBS_WRAPPER_SOURCE: ["secret- and transcript-independent gate", "Scalar telemetry remains useful"],
        TIERED_OBS_SOURCE: ["Two zero-leakage tiers with one bit of joint leakage"],
        RECEIPT_SCHEMA_SOURCE: ["smuggle a scalar observation rate in place of the channel witness", "arithmetic may be valid under a model digest"],
        THREAT_WINDOW_SOURCE: ["A committee-hit calculation, not an observation channel", "telemetry, not substitutes for the channel"],
        EVAL2_SOURCE: ["Neither number is deployment evidence", "Equal contact marginals permit any-hit probabilities throughout", "independent-contact and independent-erasure control assumptions"],
        EVAL2_QUEUE_NOTE: ["control-model sensitivity statement", "Neither number is deployment evidence"],
        WORKED_EXAMPLE_SOURCE: ["Illustrative arithmetic slice, not a channel certificate", "assumption_only_no_joint_channel_witness", "publication_eligible=false"],
        WORKED_EXAMPLE_HOLD_NOTE: ["Correct arithmetic replay does not supply", "publication_eligible=false"],
    }
    for path, fragments in source_guards.items():
        text = (root / path).read_text(encoding="utf-8", errors="replace")
        for fragment in fragments:
            if fragment not in text:
                failures.append({"category": "bossfight_source_guard_missing", "path": path, "fragment": fragment})
    for path in BOSSFIGHT_HOLD_NOTES:
        if not (root / path).exists():
            failures.append({"category": "bossfight_hold_note_missing", "path": path})
    for path in BOSSFIGHT_RETIRED_NOTES:
        if (root / path).exists():
            failures.append({"category": "bossfight_retired_queue_note_still_present", "path": path})

    return {
        "target": "Boss Fight observation-channel, composition, filter, and model-binding boundary",
        "source_tex": BOSSFIGHT_SOURCE,
        "source_sha256": source_hash,
        "evidence_card": None,
        "hostile_vector_source": HOSTILE_OVERLAY,
        "status": "pass" if not failures else "fail",
        "vector_ids_checked": sorted(BOSSFIGHT_VECTOR_IDS),
        "recomputed_values": {
            "cyclic_reveal_scalar_erasure_bits": scalar_bits,
            "cyclic_reveal_actual_maximal_leakage_bits": actual_bits,
            "cyclic_reveal_scalar_exact_guess": scalar_guess,
            "cyclic_reveal_actual_exact_guess": actual_guess,
            "independent_any_hit_probability": independent_any_hit,
            "equal_marginal_any_hit_lower": rho,
            "equal_marginal_any_hit_upper": min(1.0, m * rho),
            "partial_subset_target_in_probability": p_target_in,
            "partial_subset_target_erased_probability": p_target_out,
            "retrospective_overshoot_bits": trigger - cap,
            "tier_synergy_joint_bits": 1.0,
        },
        "failures": failures,
    }

def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    overlay = load_json(root / HOSTILE_OVERLAY)
    failures: list[dict[str, Any]] = []
    if overlay.get("generated_for_revision") != release.get("revision"):
        failures.append({"category": "overlay_revision_mismatch", "actual": overlay.get("generated_for_revision"), "expected": release.get("revision")})
    if overlay.get("checked_bundle") != release.get("bundle"):
        failures.append({"category": "overlay_bundle_mismatch", "actual": overlay.get("checked_bundle"), "expected": release.get("bundle")})
    if overlay.get("publication_authorized") is not False:
        failures.append({"category": "overlay_publication_authorized_not_false"})

    state = check_state(root, release, overlay)
    mucc = check_mucc(root, release, overlay)
    mceq = check_mceq(root, release, overlay)
    cppc = check_cppc(root, release, overlay)
    endpoint = check_endpoint(root, release, overlay)
    bossfight = check_bossfight(root, release, overlay)
    for row in [state, mucc, mceq, cppc, endpoint, bossfight]:
        for failure in row.get("failures", []):
            failures.append({"target": row.get("target"), **failure})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "independent_hostile_vector_recomputation",
        "checked_surfaces": [HOSTILE_OVERLAY, STATE_CARD, MUCC_CARD, MCEQ_SOURCE, WORKED_RECEIPT, PUBLISHED_CALIBRATION_SOURCE, PUBLISHED_CALIBRATION_RECEIPT, PUBLISHED_CALIBRATION_QUEUE_NOTE, CITATION_HEADS, CPPC_SOURCE, CPPC_HOLD_NOTE, EVAL_CALIBRATION_SOURCE, ENDPOINT_SOURCE, ENDPOINT_BRIDGE_SOURCE, ENDPOINT_HOLD_NOTE, BOSSFIGHT_SOURCE, BOSSFIGHT_DIAL_SOURCE, BOSSFIGHT_ADDENDUM_SOURCE, BOSSFIGHT_VERIFIER_SOURCE, OBS_WRAPPER_SOURCE, TIERED_OBS_SOURCE, RECEIPT_SCHEMA_SOURCE, THREAT_WINDOW_SOURCE, EVAL2_SOURCE, EVAL2_QUEUE_NOTE, WORKED_EXAMPLE_SOURCE, WORKED_EXAMPLE_HOLD_NOTE, *BOSSFIGHT_HOLD_NOTES],
        "targets": [state, mucc, mceq, cppc, endpoint, bossfight],
        "summary": {
            "checks_failed": len(failures),
            "targets_checked": 6,
            "state_vector_count": len(STATE_VECTOR_IDS),
            "mucc_vector_count": len(MUCC_VECTOR_IDS),
            "mceq_vector_count": len(MCEQ_VECTOR_IDS),
            "cppc_vector_count": len(CPPC_VECTOR_IDS),
            "endpoint_vector_count": len(ENDPOINT_VECTOR_IDS),
            "bossfight_vector_count": len(BOSSFIGHT_VECTOR_IDS),
            "external_reviewer_signoff": "missing",
            "publication_blocking_external_review": True,
        },
        "failures": failures[:80],
        "fail_closed_rule": "If hostile-vector recomputation fails, the State/MUCC/MC-EQ/CPPC/endpoint/Boss-Fight freeze evidence is not safe to promote; if it passes, publication is still blocked until external hostile review/countersignature exists.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
