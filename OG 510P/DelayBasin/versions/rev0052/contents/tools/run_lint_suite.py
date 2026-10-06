import pathlib
import runpy
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
tools = [
    "check_discovery.py",
    "check_registry_ids.py",
    "check_revision_sync.py",
    "check_prompt_pair_contract.py",
    "check_release_hygiene.py",
    "gen_context_pack.py",
    "check_context_pack_budget.py",
    "check_context_pack_fidelity.py",
    "check_context_pack_contract.py",
    "check_core_lexicon_contract.py",
    "check_move_registry_contract.py",
    "check_promotion_contract.py",
    "check_decay_watch_contract.py",
    "check_recovery_kernel_contract.py",
    "check_revision_receipt_contract.py",
    "check_counterfactual_shadow_contract.py",
    "check_regime_probe_contract.py",
    "check_public_hidden_state_contract.py",
    "check_belief_state_contract.py",
    "check_innovation_packet_contract.py",
    "check_rate_distortion_contract.py",
    "check_revision_gain_contract.py",
    "check_witness_set_contract.py",
    "check_hold_packet_contract.py",
    "check_sentinel_panel_contract.py",
    "check_identification_packet_contract.py",
    "check_timescale_lane_contract.py",
    "check_phase_boundary_contract.py",
    "check_gauge_discipline_contract.py",
    "check_loop_closure_contract.py",
    "check_continuation_margin_contract.py",
    "check_control_authority_contract.py",
    "check_balanced_archive_contract.py",
    "check_memory_vs_reentry_contract.py",
    "check_predictive_state_contract.py",
    "check_future_equivalence_contract.py",
    "check_intervention_equivalence_contract.py",
    "check_homing_packet_contract.py",
    "check_probe_economics_contract.py",
    "check_stopping_packet_contract.py",
    "check_continuation_monitor_contract.py",
    "check_observer_actuator_split_contract.py",
    "check_negative_control_handle_contract.py",
    "check_blind_packet_contract.py",
    "check_execution_witness_contract.py",
    "check_assistant_echo_filter_contract.py",
    "check_reasoning_firebreak_contract.py",
    "check_dependence_adjusted_witness_contract.py",
    "check_rewrite_witness_contract.py",
    "check_conformance_witness_contract.py",
    "check_necessity_witness_contract.py",
    "check_sufficiency_witness_contract.py",
    "check_trajectory_map_open_questions.py",
]

for tool in tools:
    print(f"== {tool} ==", flush=True)
    try:
        runpy.run_path(str(ROOT / "tools" / tool), run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code != 0:
            raise

print("run_lint_suite: OK")
