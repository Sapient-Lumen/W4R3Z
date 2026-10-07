#!/usr/bin/env python3
"""Build a compact external-hostile-review packet for the State/MUCC/MC-EQ/CPPC/endpoint/Boss-Fight lane.

The archive already has internal recomputation checks.  This packet is different:
it is the smallest reviewer-facing bundle of inputs, arithmetic traps, expected
non-transfer boundaries, and signoff requirements needed for a human or
independent tool to attack the risky next-lane claims without navigating the
whole cube first.  It is deliberately non-authorizing; a ready packet is not an
external review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_hostile_review_vectors as hostile_vectors  # noqa: E402
import check_threat_transfer_matrix as threat_matrix  # noqa: E402

PACKET_JSON = pathlib.Path("release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.json")
PACKET_MD = pathlib.Path("release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.md")
PACKET_VERSION = "external-hostile-review-packet-v10"


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def surface_digest(root: pathlib.Path, rel: str) -> dict[str, Any]:
    path = root / rel
    return {"path": rel, "sha256": sha256_file(path), "bytes": path.stat().st_size}


def vector_extract(hostile_report: dict[str, Any]) -> dict[str, Any]:
    targets = hostile_report.get("targets", []) if isinstance(hostile_report.get("targets"), list) else []
    out: dict[str, Any] = {}
    for target in targets:
        if not isinstance(target, dict):
            continue
        target_name = str(target.get("target", ""))
        if "State" in target_name:
            label = "state"
        elif "MUCC" in target_name:
            label = "mucc"
        elif "CPPC" in target_name:
            label = "cppc"
        elif "Endpoint" in target_name:
            label = "endpoint"
        elif "Boss Fight" in target_name:
            label = "bossfight"
        else:
            label = "mceq"
        out[label] = {
            "target": target.get("target"),
            "source_tex": target.get("source_tex"),
            "source_sha256": target.get("source_sha256"),
            "evidence_card": target.get("evidence_card"),
            "vector_ids_checked": target.get("vector_ids_checked", []),
            "recomputed_values": target.get("recomputed_values", {}),
            "status": target.get("status"),
        }
    return out


def build(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    hostile_report = hostile_vectors.check(root)
    transfer_report = threat_matrix.check(root)
    vectors = vector_extract(hostile_report)
    state = vectors.get("state", {})
    mucc = vectors.get("mucc", {})
    mceq = vectors.get("mceq", {})
    cppc = vectors.get("cppc", {})
    endpoint = vectors.get("endpoint", {})
    bossfight = vectors.get("bossfight", {})
    transfer_rows = transfer_report.get("matrix", []) if isinstance(transfer_report.get("matrix"), list) else []
    external_transfer_rows = [row for row in transfer_rows if isinstance(row, dict) and row.get("system_id") != "native_mucc_committee_contact_floor"]

    required_surfaces = [
        "release_queue/HOSTILE_REVIEW_VECTORS.json",
        "release_queue/evidence_packs/2026.06.16-state-dependent-anonymity/STATE_ANONYMITY_CARD.json",
        "release_queue/evidence_packs/2026.06.16-committee-contact-set-privacy-in-anonymous-dht-lookups/MUCC_CONTACT_FLOOR_CARD.json",
        "series/anondht_state_series/paper1_state_dependent_anonymity/paper.tex",
        "series/anondht_state_series/paper2_mucc_committee_contact_privacy/paper.tex",
        "series/release_and_destination/paperB_mceq_coversketch_destination_privacy/paper.tex",
        "series/anondht_state_series/paper3_closed_view_auditing_cppc/paper.tex",
        "series/anonymity_series/paperA_odds_inflation_anonymity/paper.tex",
        "series/synthesis/paper5_endpoint_metrics_bridge/paper.tex",
        "release_queue/hold/2026.03.16-paperA-posterior-mass-true-odds-repair-hold.md",
        "series/evaluation_series/paper3_calibration_recipes_anondht/paper.tex",
        "release_queue/hold/2026.03.17-paper3-closed-view-alert-cap-repair-hold.md",
        "published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/paper.tex",
        "published/citation_heads.json",
        "series/synthesis/paper17_worked_example_receipt_interlock/artifacts/example_receipt.json",
        "series/synthesis/paper17_worked_example_receipt_interlock/tools/materialize_example.py",
        "series/synthesis/paper17_worked_example_receipt_interlock/tools/validate_example.py",
        "publishing/check_hostile_review_vectors.py",
        "publishing/check_threat_transfer_matrix.py",
        "series/bossfight_series/paperA_bossfight_budgets/paper.tex",
        "series/bossfight_series/paperB_anondht_dial_sheet/paper.tex",
        "series/bossfight_series/paperB_addendum_evidence_tables/paper.tex",
        "series/bossfight_series/paperC_proof_carrying_budgets/paper.tex",
        "series/synthesis/paper11_observation_attenuation/paper.tex",
        "series/synthesis/paper15_tiered_observation_vectors/paper.tex",
        "series/synthesis/paper12_receipt_line_items_schema/paper.tex",
        "series/synthesis/paper4_threat_windows_anondht/paper.tex",
        "series/evaluation_series/paper2_advantage_contracts_stealth_audits/paper.tex",
        "release_queue/candidates/2026.03.16-paper2-advantage-contracts-candidate.md",
        "series/synthesis/paper17_worked_example_receipt_interlock/paper.tex",
        "release_queue/hold/2026.03.16-paper17-worked-example-hold.md",
        "release_queue/hold/2026.03.16-paperA-bossfight-observation-channel-repair-hold.md",
        "release_queue/hold/2026.03.17-paperB-observation-channel-witness-hold.md",
        "release_queue/hold/2026.03.16-paperB-addendum-independence-scenario-hold.md",
        "release_queue/hold/2026.03.17-paperC-model-binding-gate-hold.md",
    ]

    return {
        "packet_format": PACKET_VERSION,
        "packet_id": f"{release['revision']}-state-mucc-mceq-cppc-endpoint-bossfight-external-hostile-review",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "external_review_status": "packet_ready_signoff_missing",
        "external_reviewer_signoff": {
            "status": "missing",
            "reviewer": None,
            "signed_digest": None,
            "review_date": None,
            "countersignature_path": None,
        },
        "blocking_rule": "This packet only prepares external review. Publication remains blocked until a named external/adversarial reviewer or independent tool countersigns a reviewed packet or supplies a reviewed failure report.",
        "required_surfaces": [surface_digest(root, rel) for rel in required_surfaces],
        "internal_recomputation_summary": hostile_report.get("summary", {}),
        "state_review_target": state,
        "mucc_review_target": mucc,
        "mceq_review_target": mceq,
        "cppc_review_target": cppc,
        "endpoint_review_target": endpoint,
        "bossfight_review_target": bossfight,
        "threat_transfer_target": {
            "source_tex": transfer_report.get("source_tex"),
            "source_sha256": transfer_report.get("source_sha256"),
            "native_theorem_row_count": transfer_report.get("summary", {}).get("native_theorem_rows"),
            "external_transfer_authorized_rows": transfer_report.get("summary", {}).get("external_transfer_authorized_rows"),
            "external_rows_to_reject_as_theorem_transfer": [
                {
                    "system_id": row.get("system_id"),
                    "claim_status": row.get("claim_status"),
                    "transfer_rule": row.get("transfer_rule"),
                    "publication_blocker_if_used": row.get("publication_blocker_if_used"),
                }
                for row in external_transfer_rows
            ],
        },
        "review_tasks": [
            {
                "id": "state_nat_bit_boundary",
                "must_recompute": ["epsilon_nat", "epsilon_bits", "horizon_bits", "per_epoch_odds"],
                "must_break": ["copy_nat_value_as_bit_exponent", "multiply_by_ln2_instead_of_dividing", "zero_delta_sanity_control"],
                "acceptance_rule": "A reviewer must independently derive the bit conversion from the nat-bound source parameters and reject nat-as-bit or multiply-by-ln2 substitutions.",
            },
            {
                "id": "mucc_contact_floor_arithmetic",
                "must_recompute": ["p_floor", "expected_contact_floor"],
                "must_break": ["beta_instead_of_one_minus_beta", "drop_alpha_denominator", "multiply_by_alpha_instead_of_dividing", "round_down_expected_contact_floor", "underbudget_three_round_schedule"],
                "acceptance_rule": "A reviewer must independently derive the expected contact floor and show that each listed shortcut underestimates or misstates the bound.",
            },
            {
                "id": "mucc_liveness_substitution_boundary",
                "must_recompute": ["lower_bound_liveness_guard", "live_factor_non_substitution_guard", "inner_alpha_lower_recomputed", "forbidden_outer_as_inner_alpha", "nested_quorum_alpha_overstatement_ratio"],
                "must_break": ["lower_bound_liveness_as_theorem_evidence", "live_yield_alpha_vs_lookup_concurrency_alpha", "outer_d_t_as_inner_n_h_alpha_calibration"],
                "acceptance_rule": "A reviewer must reject lower-bound liveness evidence as theorem evidence, reject lookup-concurrency alpha as live-yield alpha, and keep outer (d,t) distinct from inner (n,h,q,rho). The pinned drill must reproduce 0.3288404125 from (16,11,0.6,0), reject 0.8263296 from the forbidden outer-as-inner substitution, and confirm that no separate churn_alpha_table.tex artifact is claimed.",
            },
            {
                "id": "mucc_approximate_equalization_boundary",
                "must_recompute": ["approximate_mucc_required_destination_contact_average_A", "one_sided_counterexample_expected_total_contacts", "one_sided_counterexample_global_marginal_diameter", "two_sided_radius_implied_diameter", "two_sided_radius_correct_contact_floor"],
                "must_break": ["one_sided_marginal_ceiling_as_approx_mucc", "two_sided_radius_without_factor_two"],
                "acceptance_rule": "A reviewer must reproduce the destination-only counterexample to a one-sided marginal ceiling, then derive the diameter floor dA+(M-d)(A-delta)_+ and apply delta<=2eta for a two-sided center radius. For eta=0.05 the reviewer must obtain 127.2, not 139.6 or the legacy 139.2 expression.",
            },
            {
                "id": "mucc_necessity_not_sufficiency_boundary",
                "must_recompute": ["iid_binomial_success_at_universal_floor", "iid_binomial_success_at_predecessor", "iid_binomial_minimum_integer_contacts", "thinned_hypergeom_success_at_universal_floor", "thinned_hypergeom_success_at_predecessor", "thinned_hypergeom_minimum_integer_contacts"],
                "must_break": ["universal_floor_as_success_certificate"],
                "acceptance_rule": "A reviewer must reject the 152-contact universal Markov expectation floor as a 0.95 success certificate and independently verify that both named optimistic joint models fail at 227 and first pass at 228.",
            },
            {
                "id": "mucc_joint_assumption_sufficiency_ladder",
                "must_recompute": ["mucc_marginal_independent_success_at_optimistic_minimum", "mucc_marginal_independent_success_at_predecessor", "mucc_marginal_independent_minimum_integer_contacts", "mean_only_liveness_success_lower_bound_at_full_contact", "mean_only_liveness_required_contacts_unclipped"],
                "must_break": ["optimistic_joint_model_as_mucc_marginal_certificate", "independent_liveness_as_correlation_robust_certificate", "upper_yield_alpha_as_sufficiency_input"],
                "acceptance_rule": "A reviewer must derive the lower-convex-envelope guarantee from MUCC marginals, verify failure at 249 and first pass at 250 under exact independent liveness, then show that mean-only correlated liveness certifies only 0.68 at full contact and would require 310 contacts for a 0.95 bound. The reviewer must also check that alpha's evidentiary direction is not reversed.",
            },
            {
                "id": "mucc_joint_privacy_nonclaim_boundary",
                "must_recompute": ["perfect_leakage_fixed_contact_count", "perfect_leakage_contact_marginal", "perfect_leakage_support_intersection_size", "perfect_leakage_total_variation_distance", "perfect_leakage_bayes_recovery", "perfect_leakage_mutual_information_bits", "perfect_leakage_success_probability_D0", "perfect_leakage_success_probability_D1"],
                "must_break": ["exact_mucc_as_joint_contact_privacy"],
                "acceptance_rule": "A reviewer must enumerate the two 256-shift orbit supports, verify exact 250/256 contact marginals for every label, verify zero support intersection and therefore TV=1/perfect destination recovery, and independently recompute success 0.9628928 and 0.9628032 under alpha=0.8. The k0=250 sufficiency row must be accepted only as availability, never as anonymity evidence.",
            },
            {
                "id": "mceq_tv_support_ratio_boundary",
                "must_recompute": ["one_step_maximal_leakage_bits", "one_step_uniform_prior_recovery", "repeated_maximal_leakage_bits", "repeated_uniform_prior_recovery", "support_contained_maximal_leakage_bound_bits", "support_contained_pairwise_max_divergence_bound_bits"],
                "must_break": ["tv_as_finite_reference_ratio_without_support_containment", "pairwise_tv_as_alphabet_free_maximal_leakage", "repeated_off_support_tag_horizon", "support_contained_uniform_cover_bound", "singleton_tv_factor_two_overstatement"],
                "acceptance_rule": "A reviewer must derive the N-destination off-support tag family, verify TV(P_d,Q)=TV(P_d,P_d')=delta, verify infinite D_infinity to Q, and reproduce 2.608809242676 bits plus 0.023828125 recovery at N=256, delta=0.02. The six-step attack must reproduce 4.912180044586 bits and 0.117617940936 recovery. The reviewer must then verify that the finite ratio bounds require support containment and q>0, yielding 0.339501170198 and 0.692863304520 bits for k=8, epsilon=0.005, T=6.",
            },
            {
                "id": "mceq_worked_binding_nonclaim",
                "must_recompute": ["worked_fallback_observation_sum", "worked_fallback_publication_eligible"],
                "must_break": ["worked_fallback_vector_as_mceq_certificate"],
                "acceptance_rule": "A reviewer must trace 0.056345507023 to the three maintained observation-attenuation terms, confirm that the retired MC-EQ horizon/slack fields do not exist, and reject the row as MC-EQ or joint-channel MaxL evidence because its composition evidence is assumption-only and publication_eligible=false.",
            },
            {
                "id": "cppc_alert_necessity_sufficiency_boundary",
                "must_recompute": ["alpha_0_02_beta_0_10_two_sided_floor_bits", "natural_log_mislabeled_value", "correct_bit_value", "reverse_direction_example_forward_bits", "reverse_direction_example_reverse_bits", "reverse_direction_example_two_sided_bits", "alpha_0_01_beta_0_10_two_sided_floor_bits"],
                "must_break": ["one_sided_lower_bound_as_cap_certificate", "natural_log_values_labeled_as_bits", "missing_reverse_direction", "six_bit_target_impossibility", "published_calibration_inherited_alert_claim"],
                "acceptance_rule": "A reviewer must derive both weighted-error inequalities in bit units, reproduce the 5.491853 lower bound and the zero-probability counterexample showing it is not a certificate, recover 2.890372 nats versus 4.169925 bits for the unit trap, and verify that the missing reverse direction changes the (beta,alpha)=(0.01,0.05) row from 4.307429 to 6.569856 bits. The immutable public calibration row must remain withdrawn rather than silently repaired in place.",
            },
            {
                "id": "cppc_mechanism_composition_and_artifact_boundary",
                "must_recompute": ["rr_q_0_1_one_slot_bits", "rr_q_0_1_two_slot_bits"],
                "must_break": ["rr_q_target_incompatibility", "rr_fixed_slot_composition", "delay_as_eventual_privacy_amplification", "bare_hash_as_hiding_commitment"],
                "acceptance_rule": "A reviewer must prove the randomized-response upper guarantee, verify q=0.1 gives 3.169925001 bits for one slot and 6.339850003 for two, reject any 0.02 false-alarm target under that q, and confirm that delay alone does not discount an eventual plaintext transcript and that a bare hash of a low-entropy alert is not a hiding commitment. No deployment CPPC may be inferred from the illustrative card.",
            },
            {
                "id": "endpoint_pml_mass_true_odds_boundary",
                "must_recompute": ["deterministic_reveal_pml_bits", "deterministic_reveal_true_odds", "uniform_4096_mass_factor", "uniform_4096_true_odds_factor", "uniform_4096_true_odds_bits"],
                "must_break": ["pml_mass_as_true_odds", "prior_cap_true_odds_conversion", "published_legacy_odds_wording_as_true_odds"],
                "acceptance_rule": "A reviewer must derive that log2(pi(i|o)/pi(i)) is posterior-mass inflation/PML, not one-vs-complement odds; verify deterministic binary revelation has one bit of PML but infinite true odds; and reproduce the guarded N=4096, epsilon=0.75 conversion 1.681792830507 -> 1.682072885510, or 0.750240220031 bits. The reviewer must reject any finite prior-independent odds conversion and confirm that immutable legacy wording is withdrawn from true-odds reuse rather than silently rewritten.",
            },
            {
                "id": "endpoint_hockey_stick_tail_boundary",
                "must_recompute": ["hockey_stick_counterexample_slack", "hockey_stick_counterexample_positive_loss_tail", "hockey_stick_tail_to_slack_ratio"],
                "must_break": ["hockey_stick_delta_as_tail_probability", "tail_implies_hockey_stick_not_converse"],
                "acceptance_rule": "A reviewer must evaluate P1=(0.51,0.49), P2=(0.49,0.51), P=(0.5,0.5), verify E_1(P_i||P)=TV=0.01 while the positive-loss event has probability 0.51, and prove only the forward implication tail<=eta => hockey-stick<=eta. Hockey-stick delta must not be described as a bad-transcript probability without a separate tail theorem.",
            },
            {
                "id": "endpoint_tv_singleton_and_hot_lane_regression",
                "must_recompute": ["singleton_tv_corrected_bits", "singleton_tv_legacy_double_bits", "published_ready_sources_scanned", "published_ready_semantic_alias_violations"],
                "must_break": ["singleton_tv_factor_two_overpayment", "published_ready_semantic_alias_scan"],
                "acceptance_rule": "A reviewer must use the singleton event consequence |P(o)-Q(o)|<=TV(P,Q), reproduce 0.289506617195 bits for q_min=0.1 and delta=0.01, and reject the legacy doubled-deviation value 0.584962500721 bits as unnecessary payment. The reviewer must also rerun the Published-ready semantic scan and obtain zero known PML-as-odds aliases.",
            },
            {
                "id": "bossfight_scalar_observation_and_contact_correlation",
                "must_recompute": ["cyclic_reveal_scalar_erasure_bits", "cyclic_reveal_actual_maximal_leakage_bits", "cyclic_reveal_scalar_exact_guess", "cyclic_reveal_actual_exact_guess", "independent_any_hit_probability", "equal_marginal_any_hit_lower", "equal_marginal_any_hit_upper"],
                "must_break": ["equal_observation_marginals_not_independent_erasure", "correlated_contacts_break_independent_any_hit"],
                "acceptance_rule": "A reviewer must enumerate the three-secret cyclic-reveal channel, verify equal reveal probability 1/2, recover one bit of actual maximal leakage and exact guessing 2/3, and contrast them with 0.321928094887 bits and 5/12 under the independent-erasure model. The reviewer must also prove that rho=0.1 and m=10 permit any-hit probability from 0.1 to 1 under equal marginals, while 0.6513215599 requires independence.",
            },
            {
                "id": "bossfight_partial_visibility_filter_and_allocation_boundary",
                "must_recompute": ["partial_subset_target_in_probability", "partial_subset_target_erased_probability", "retrospective_overshoot_bits"],
                "must_break": ["partial_subset_target_can_be_erased", "retrospective_pml_not_no_overshoot_filter", "equal_share_not_empirical_average"],
                "acceptance_rule": "A reviewer must verify in the N=5,k=2,m=1,q=0.2 partial-subset drill that the target-erased branch has probability 0.064 rather than zero and the target-observed branch has probability 0.128. The reviewer must then show that a one-bit triggering output crosses a 0.5-bit cap before a retrospective odometer can stop it, and distinguish B/Q as an optional equal-share design from a history-uniform per-round theorem.",
            },
            {
                "id": "bossfight_model_binding_and_joint_tier_boundary",
                "must_recompute": ["cyclic_reveal_scalar_erasure_bits", "cyclic_reveal_actual_maximal_leakage_bits", "tier_synergy_joint_bits"],
                "must_break": ["arithmetic_verifier_without_channel_binding", "marginal_tiers_can_have_joint_synergy"],
                "acceptance_rule": "A reviewer must show that the same scalar model tuple can make a deterministic arithmetic checker pass for two deployments with different actual channels, so the honest verdict is arithmetic-valid-under-model-digest rather than deployment anonymous. The reviewer must also reproduce the one-time-pad tier construction in which each marginal tier has zero maximal leakage but the joint pair leaks one bit, and reject marginal-vector composition without a joint witness.",
            },
            {
                "id": "bossfight_active_consumer_propagation_audit",
                "must_recompute": ["independent_any_hit_probability", "equal_marginal_any_hit_lower", "equal_marginal_any_hit_upper", "cyclic_reveal_actual_maximal_leakage_bits"],
                "must_break": ["equal_observation_marginals_not_independent_erasure", "correlated_contacts_break_independent_any_hit", "arithmetic_verifier_without_channel_binding"],
                "acceptance_rule": "A reviewer must inspect the active Eval 2 source/note and Synthesis 17 source/note, verify that 0.871488 and approximately 0.992 are labeled independent-control sensitivity values rather than deployment evidence, and verify that 0.056345507023 and 0.26590 are labeled non-authorizing arithmetic with composition_evidence_status=assumption_only_no_joint_channel_witness and publication_eligible=false. Any active consumer that shortens these to an observation probability, anonymity certificate, or published privacy total fails the review.",
            },
            {
                "id": "threat_transfer_nonclaim_boundary",
                "must_recompute": ["native_theorem_row_count", "external_transfer_authorized_rows", "key_independence_counterexample_global_marginal_diameter"],
                "must_break": [row.get("system_id") for row in external_transfer_rows] + ["key_independence_as_mucc_label_uniformity"],
                "acceptance_rule": "A reviewer must reject IPFS, delegated-routing, Peer2PIR, OHTTP, Tor, and I2P rows as theorem-bearing MUCC transfers until each has a new source-bound model/card. The reviewer must also reject destination-independence or DP-style stability as committee-label-uniform MUCC unless a symmetry or global marginal-diameter bridge is proved, and reject any MUCC-only row as joint contact-set privacy.",
            },
        ],
        "minimum_return_artifact": {
            "kind": "external_review_result",
            "required_fields": ["reviewer_identity_or_tool", "reviewed_packet_sha256", "surface_digests_checked", "findings", "state_result", "mucc_result", "mceq_result", "cppc_result", "endpoint_result", "bossfight_result", "threat_transfer_result", "signature_or_reproducible_command"],
            "allowed_outcomes": ["pass_with_countersignature", "fail_with_counterexample", "inconclusive_with_blockers"],
            "no_silent_pass_rule": "A pass without named reviewer/tool identity and packet digest is treated as missing, not as external review.",
        },
        "fail_closed_rule": "If any input digest changes, rebuild this packet before review. If external review is absent, inconclusive, or unsigned, keep publication_authorized=false.",
    }


def render_md(packet: dict[str, Any]) -> str:
    lines = [
        "# External hostile review packet",
        "",
        f"- Packet format: `{packet.get('packet_format')}`",
        f"- Generated for revision: `{packet.get('generated_for_revision')}`",
        f"- Checked bundle: `{packet.get('checked_bundle')}`",
        f"- External review status: `{packet.get('external_review_status')}`",
        f"- Publication authorized: `{str(packet.get('publication_authorized')).lower()}`",
        "",
        "## Why this exists",
        "",
        packet.get("blocking_rule", "Publication remains blocked until external review exists."),
        "",
        "## Required reviewer attacks",
        "",
    ]
    for task in packet.get("review_tasks", []):
        lines.extend([
            f"### `{task.get('id')}`",
            "",
            f"- Must recompute: `{', '.join(task.get('must_recompute', []))}`",
            f"- Must try to break: `{', '.join(task.get('must_break', []))}`",
            f"- Acceptance rule: {task.get('acceptance_rule')}",
            "",
        ])
    lines.extend([
        "## Current internal values for independent recomputation",
        "",
        f"- State target: `{packet.get('state_review_target', {}).get('source_tex')}`",
        f"- State recomputed values: `{json.dumps(packet.get('state_review_target', {}).get('recomputed_values', {}), sort_keys=True)}`",
        f"- MUCC target: `{packet.get('mucc_review_target', {}).get('source_tex')}`",
        f"- MUCC recomputed values: `{json.dumps(packet.get('mucc_review_target', {}).get('recomputed_values', {}), sort_keys=True)}`",
        f"- MC-EQ target: `{packet.get('mceq_review_target', {}).get('source_tex')}`",
        f"- MC-EQ recomputed values: `{json.dumps(packet.get('mceq_review_target', {}).get('recomputed_values', {}), sort_keys=True)}`",
        f"- CPPC target: `{packet.get('cppc_review_target', {}).get('source_tex')}`",
        f"- CPPC recomputed values: `{json.dumps(packet.get('cppc_review_target', {}).get('recomputed_values', {}), sort_keys=True)}`",
        f"- Endpoint target: `{packet.get('endpoint_review_target', {}).get('source_tex')}`",
        f"- Endpoint recomputed values: `{json.dumps(packet.get('endpoint_review_target', {}).get('recomputed_values', {}), sort_keys=True)}`",
        f"- Boss Fight target: `{packet.get('bossfight_review_target', {}).get('source_tex')}`",
        f"- Boss Fight recomputed values: `{json.dumps(packet.get('bossfight_review_target', {}).get('recomputed_values', {}), sort_keys=True)}`",
        f"- External theorem-transfer rows authorized: `{packet.get('threat_transfer_target', {}).get('external_transfer_authorized_rows')}`",
        "",
        "## Minimum return artifact",
        "",
        f"Required fields: `{', '.join(packet.get('minimum_return_artifact', {}).get('required_fields', []))}`",
        "",
        "## Rule",
        "",
        packet.get("fail_closed_rule", "No publication without external review."),
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-json", default=str(PACKET_JSON))
    parser.add_argument("--write-md", default=str(PACKET_MD))
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    packet = build(root)
    if args.write_json:
        out = root / args.write_json
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.write_md:
        out_md = root / args.write_md
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_md(packet), encoding="utf-8")
    print(json.dumps({"status": "pass", "written_json": args.write_json, "written_md": args.write_md, "review_task_count": len(packet.get("review_tasks", [])), "external_review_status": packet.get("external_review_status")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
