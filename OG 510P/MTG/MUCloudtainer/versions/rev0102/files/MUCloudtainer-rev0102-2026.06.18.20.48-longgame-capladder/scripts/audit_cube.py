from __future__ import annotations

import csv
import gzip
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.muc5.cards import CARD_ORDER
from src.muc5.deckspace import DeckVector, deck_count, total_deck_count
from src.muc5.env import MUC5SlotEnv
from src.muc5.features import feature_names
from src.muc5.imitation import action_ranker_feature_names
from src.muc5.invariants import card_conservation_report
from src.muc5.gametable import MUC5GameTable, SeatSpec, load_table, save_table
from src.muc5.mulligan import MULLIGAN_POLICY_NAMES, POLICY_LAND_BAND, RuleMulliganAgent
from src.muc5.decision import PublicHeuristicAgent, build_decision_frame, apply_decision_index
from src.muc5.engine import PendingChoice
from src.muc5.fairness import audit_observation_shape, all_checks_pass
from src.muc5.probability import deck_probe
from src.muc5.payoff import default_strategy_bundles, mulligan_strategy_bundles
from src.muc5.perf import benchmark_agent_games, benchmark_public_decision_games
from src.muc5.tournament import LIFE_TOTAL_OPTIONS, known_life_config, standard_life_configs, unknown_life_config
from src.muc5.replay import read_trace_jsonl, replay_public_decision_trace, record_public_decision_trace, state_fingerprint
from src.muc5.reward_guard import audit_reward_packet, audit_payoff_like_row, reward_packet_from_state
from src.muc5.public_agents import make_public_agent
from src.muc5.promotion import PromotionGateConfig, audit_promotion_rows
from src.muc5.oracle_seed import generate_oracle_candidates
from src.muc5.agents import play_public_agent_game
from src.muc5.code_policy import code_policy_catalog, make_code_policy_agent, smoke_lint_code_policy
from src.muc5.action_schema import Action
from src.muc5.statgate import audit_statistical_gate, pairwise_stat_rows, read_csv_rows as read_stat_csv_rows, statistical_standings
from src.muc5.map_elites import deck_descriptor
from src.muc5.strategy_sets import statgate_probe_strategy_bundles, mlp_ranker_probe_bundles, mulligan_policy_gate_bundles, learned_mulligan_gate_bundles, outcome_ranker_probe_bundles, mulligan_outcome_gate_bundles, counterfactual_mulligan_gate_bundles, repeated_counterfactual_mulligan_gate_bundles, counterfactual_action_ranker_probe_bundles, scaled_counterfactual_action_ranker_bundles, budgeted_counterfactual_action_ranker_bundles, adaptive_counterfactual_action_ranker_bundles, disagreement_counterfactual_action_ranker_bundles
from src.muc5.cpp_accel import cpp_toolchain_status
from src.muc5.cpp_legal import cpp_legal_tool_status
from src.muc5.cpp_transition import cpp_transition_tool_status
from src.muc5.cpp_segment import cpp_segment_tool_status
from src.muc5.cpp_trace import prepare_public_traces_for_cpp
from src.muc5.ranker_policy import load_linear_ranker_model, load_mlp_ranker_model, MLPActionRankerAgent
from src.muc5.mulligan_ranker import load_mulligan_ranker_model, LinearMulliganRankerAgent, mulligan_ranker_feature_names, MODEL_NAME, OUTCOME_MODEL_NAME, COUNTERFACTUAL_MODEL_NAME, model_path_for_name, make_mulligan_agent
from src.muc5.metarank import meta_rank_from_aggregate
from src.muc5.action_features import action_feature_names, action_feature_vector
from src.muc5.imitation import action_ranker_feature_names
from src.muc5.mulligan_counterfactual import load_counterfactual_mulligan_model, load_repeated_counterfactual_mulligan_agent
from src.muc5.terminal_clean import summarize_terminal_clean_rows
from src.muc5.evidence_tiering import catalog_row_count, find_tiering_catalog, load_tiering_catalog, validate_core_tiering
from src.muc5.population_frontier import summarize_population_precision_gate


def count_csv_rows_gz(path: Path) -> int:
    with gzip.open(path, "rt") as f:
        return max(0, sum(1 for _ in f) - 1)


def count_csv_rows(path: Path) -> int:
    with path.open() as f:
        return max(0, sum(1 for _ in f) - 1)


def count_csv_rows_or_catalog(path: Path) -> int:
    if path.exists():
        return count_csv_rows(path)
    try:
        relative = path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return -1
    catalog_count = catalog_row_count(ROOT, relative)
    return -1 if catalog_count is None else catalog_count


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def add(checks: list[dict], name: str, passed: bool, details: dict) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})


def main() -> None:
    checks: list[dict] = []
    card_pool = load_json(ROOT / "data" / "card_pool.json")
    add(checks, "card_pool_order_matches_code", card_pool.get("card_order") == CARD_ORDER, {"json_card_order": card_pool.get("card_order"), "code_card_order": CARD_ORDER})

    expected_total = total_deck_count()
    actual_rows = count_csv_rows_gz(ROOT / "data" / "deck_space_all.csv.gz")
    add(checks, "deck_space_csv_row_count", actual_rows == expected_total, {"actual_rows": actual_rows, "expected_rows": expected_total, "count40": deck_count(40), "count60": deck_count(60)})

    probe_summary_path = ROOT / "data" / "probe_summary.json"
    add(checks, "probe_summary_exists", probe_summary_path.exists(), {"path": str(probe_summary_path.relative_to(ROOT))})
    probe_csv = ROOT / "data" / "probe_rankings_top100.csv"
    if probe_csv.exists():
        rows = list(csv.DictReader(probe_csv.open()))
        sorted_desc = all(float(rows[i]["crude_probe_score"]) >= float(rows[i + 1]["crude_probe_score"]) for i in range(len(rows) - 1))
        add(checks, "probe_top100_sorted", len(rows) == 100 and sorted_desc, {"rows": len(rows), "sorted_desc": sorted_desc})
    else:
        add(checks, "probe_top100_sorted", False, {"reason": "missing"})

    seed = DeckVector(40, 24, 6, 4, 3, 3)
    score = deck_probe(seed).crude_probe_score
    add(checks, "seed_probe_score_stable", abs(score - 0.6661702922375548) < 1e-12, {"score": score})

    env20 = MUC5SlotEnv(seed, seed, max_action_slots=64, max_decisions=20, starting_life=20)
    obs20 = env20.reset(seed=17)
    env40 = MUC5SlotEnv(seed, seed, max_action_slots=64, max_decisions=20, starting_life=40)
    obs40 = env40.reset(seed=17)
    add(checks, "slot_env_action_mask_shape", len(obs20.action_mask) == 64 and sum(obs20.action_mask) == len(obs20.action_strings) and len(obs20.feature_vector) == len(obs20.feature_names), {"mask_len": len(obs20.action_mask), "legal_actions": len(obs20.action_strings), "feature_len": len(obs20.feature_vector)})
    fd40 = dict(zip(obs40.feature_names, obs40.feature_vector))
    add(checks, "starting_life_40_visible_to_features", obs40.raw.get("starting_life") == 40 and fd40.get("starting_life") == 40.0 and fd40.get("self_life_fraction") == 1.0, {"raw_starting_life": obs40.raw.get("starting_life"), "feature_starting_life": fd40.get("starting_life"), "self_life_fraction": fd40.get("self_life_fraction")})

    env_mull = MUC5SlotEnv(seed, seed, max_action_slots=64, max_decisions=20, starting_life=20, mulligan_policy=POLICY_LAND_BAND)
    obs_mull = env_mull.reset(seed=19)
    inv = card_conservation_report(env_mull.state)  # type: ignore[arg-type]
    fd_mull = dict(zip(obs_mull.feature_names, obs_mull.feature_vector))
    add(checks, "mulligan_policy_plumbed_and_conserves_cards", env_mull.state is not None and len(env_mull.state.mulligan_log) == 2 and inv.passed and "self_mulligans_taken" in fd_mull, {"mulligan_log": [] if env_mull.state is None else env_mull.state.mulligan_log, "invariant_errors": inv.errors, "has_feature": "self_mulligans_taken" in fd_mull})

    env_mull_agent = MUC5SlotEnv(seed, seed, max_action_slots=64, max_decisions=20, starting_life=20, mulligan_agents=(RuleMulliganAgent(POLICY_LAND_BAND), RuleMulliganAgent(POLICY_LAND_BAND)))
    obs_mull_agent = env_mull_agent.reset(seed=23)
    inv_agent = card_conservation_report(env_mull_agent.state)  # type: ignore[arg-type]
    add(checks, "mulligan_agents_plumbed_with_decision_log", env_mull_agent.state is not None and len(env_mull_agent.state.mulligan_log) == 2 and len(env_mull_agent.state.mulligan_decision_log) >= 2 and inv_agent.passed and "self_mulligans_taken" in obs_mull_agent.feature_names, {"mulligan_log": [] if env_mull_agent.state is None else env_mull_agent.state.mulligan_log, "decision_events": 0 if env_mull_agent.state is None else len(env_mull_agent.state.mulligan_decision_log), "invariant_errors": inv_agent.errors})

    names = feature_names()
    add(checks, "feature_names_stable_nonempty_unique", len(names) > 40 and len(names) == len(set(names)) and "starting_life" in names and "self_life_fraction" in names and "self_mulligans_taken" in names, {"feature_count": len(names)})

    add(checks, "tournament_life_config_contract", LIFE_TOTAL_OPTIONS == (20, 40) and known_life_config(40).construction_knows_life and not unknown_life_config(40).construction_knows_life and len(standard_life_configs()) == 4, {"life_options": LIFE_TOTAL_OPTIONS, "configs": [c.as_dict() for c in standard_life_configs()]})

    arena_path = ROOT / "data" / "rev0003_tiny_arena.csv"
    arena_summary_path = ROOT / "data" / "rev0003_tiny_arena_summary.json"
    arena_rows = count_csv_rows(arena_path) if arena_path.exists() else -1
    add(checks, "rev0003_tiny_arena_rows", arena_rows == 128 and arena_summary_path.exists(), {"arena_rows": arena_rows, "summary_exists": arena_summary_path.exists()})

    life_arena_path = ROOT / "data" / "rev0004_life_dial_arena.csv"
    life_summary_path = ROOT / "data" / "rev0004_life_dial_arena_summary.json"
    life_rows = count_csv_rows(life_arena_path) if life_arena_path.exists() else -1
    life_summary = load_json(life_summary_path)
    add(checks, "rev0004_life_dial_arena_rows", life_rows == 512 and life_summary_path.exists() and life_summary.get("games") == 512, {"life_rows": life_rows, "summary_exists": life_summary_path.exists(), "summary_games": life_summary.get("games")})

    shortlist_path = ROOT / "data" / "rev0004_life_constructor_shortlists.csv"
    shortlist_summary_path = ROOT / "data" / "rev0004_life_constructor_shortlists_summary.json"
    shortlist_rows = count_csv_rows(shortlist_path) if shortlist_path.exists() else -1
    shortlist_summary = load_json(shortlist_summary_path)
    add(checks, "rev0004_life_constructor_shortlists", shortlist_rows == 75 and shortlist_summary_path.exists() and shortlist_summary.get("rows") == 75, {"shortlist_rows": shortlist_rows, "summary_exists": shortlist_summary_path.exists(), "summary_rows": shortlist_summary.get("rows")})

    constructor_arena_path = ROOT / "data" / "rev0004_life_constructor_arena.csv"
    constructor_arena_summary_path = ROOT / "data" / "rev0004_life_constructor_arena_summary.json"
    constructor_arena_rows = count_csv_rows(constructor_arena_path) if constructor_arena_path.exists() else -1
    constructor_arena_summary = load_json(constructor_arena_summary_path)
    add(checks, "rev0004_life_constructor_arena_rows", constructor_arena_rows == 128 and constructor_arena_summary_path.exists() and constructor_arena_summary.get("games") == 128, {"constructor_arena_rows": constructor_arena_rows, "summary_exists": constructor_arena_summary_path.exists(), "summary_games": constructor_arena_summary.get("games")})

    mulligan_path = ROOT / "data" / "rev0005_mulligan_probe.csv"
    mulligan_summary_path = ROOT / "data" / "rev0005_mulligan_probe_summary.json"
    mulligan_rows = count_csv_rows(mulligan_path) if mulligan_path.exists() else -1
    mulligan_summary = load_json(mulligan_summary_path)
    add(checks, "rev0005_mulligan_probe", mulligan_rows == 24 and mulligan_summary.get("rows") == 24 and tuple(mulligan_summary.get("policies", [])) == MULLIGAN_POLICY_NAMES, {"rows": mulligan_rows, "summary_rows": mulligan_summary.get("rows"), "policies": mulligan_summary.get("policies")})

    action_path = ROOT / "data" / "rev0005_action_space_audit.csv"
    action_summary_path = ROOT / "data" / "rev0005_action_space_audit_summary.json"
    action_rows = count_csv_rows(action_path) if action_path.exists() else -1
    action_summary = load_json(action_summary_path)
    add(checks, "rev0005_action_space_audit", action_rows == action_summary.get("decision_rows") and action_summary.get("max_legal_action_count", 999) <= 64 and action_summary.get("games") == 56, {"rows": action_rows, "summary_rows": action_summary.get("decision_rows"), "max_legal_action_count": action_summary.get("max_legal_action_count"), "games": action_summary.get("games")})

    agency_path = ROOT / "data" / "rev0006_mulligan_agency_probe.csv"
    agency_events_path = ROOT / "data" / "rev0006_mulligan_decision_events.csv"
    agency_summary_path = ROOT / "data" / "rev0006_mulligan_agency_probe_summary.json"
    agency_rows = count_csv_rows(agency_path) if agency_path.exists() else -1
    agency_event_rows = count_csv_rows(agency_events_path) if agency_events_path.exists() else -1
    agency_summary = load_json(agency_summary_path)
    add(checks, "rev0006_mulligan_agency_probe", agency_rows == 18000 and agency_summary.get("rows") == 18000 and agency_event_rows == agency_summary.get("event_rows") and tuple(agency_summary.get("policies", [])) == MULLIGAN_POLICY_NAMES, {"rows": agency_rows, "event_rows": agency_event_rows, "summary_rows": agency_summary.get("rows"), "summary_events": agency_summary.get("event_rows"), "policies": agency_summary.get("policies")})

    mull_life_path = ROOT / "data" / "rev0006_mulligan_life_arena.csv"
    mull_life_summary_path = ROOT / "data" / "rev0006_mulligan_life_arena_summary.json"
    mull_life_rows = count_csv_rows(mull_life_path) if mull_life_path.exists() else -1
    mull_life_summary = load_json(mull_life_summary_path)
    add(checks, "rev0006_mulligan_life_arena", mull_life_rows == 768 and mull_life_summary.get("games") == 768 and tuple(mull_life_summary.get("mulligan_policies", [])) == MULLIGAN_POLICY_NAMES, {"rows": mull_life_rows, "summary_games": mull_life_summary.get("games"), "policies": mull_life_summary.get("mulligan_policies")})


    table = MUC5GameTable(
        seed,
        seed,
        seats=(SeatSpec.external(), SeatSpec.from_agent_name("heuristic")),
        seed=707,
        starting_life=20,
        mulligan_policy=POLICY_LAND_BAND,
        max_decisions=40,
    ).start()
    table_snap = table.snapshot()
    add(checks, "rev0007_gametable_external_stops", table.external_to_act() and table_snap.external_to_act and len(table_snap.legal_actions) > 0 and table_snap.perspective_player == 0, {"external_to_act": table.external_to_act(), "legal_actions": table_snap.legal_actions[:5], "perspective": table_snap.perspective_player})
    first_index = 0
    post_snap = table.apply_external_action(first_index)
    with tempfile.TemporaryDirectory() as td:
        table_path = Path(td) / "table.pkl"
        save_table(table, table_path)
        loaded_table = load_table(table_path)
        loaded_snap = loaded_table.snapshot()
    add(checks, "rev0007_gametable_action_and_serialization", post_snap.turn_number >= 1 and loaded_snap.starting_life == 20 and isinstance(loaded_snap.legal_actions, list), {"post_turn": post_snap.turn_number, "loaded_starting_life": loaded_snap.starting_life, "loaded_legal_count": len(loaded_snap.legal_actions)})

    sample_frame = ROOT / "data" / "rev0007_gametable_initial_frame.md"
    sample_snap = load_json(ROOT / "data" / "rev0007_gametable_initial_snapshot.json")
    after_frame = ROOT / "data" / "rev0007_gametable_after_action1.md"
    after_snap = load_json(ROOT / "data" / "rev0007_gametable_after_action1_snapshot.json")
    add(checks, "rev0007_gametable_sample_artifacts", sample_frame.exists() and after_frame.exists() and bool(sample_snap.get("legal_actions")) and "legal_actions" in after_snap, {"sample_frame_exists": sample_frame.exists(), "after_frame_exists": after_frame.exists(), "sample_legal_count": len(sample_snap.get("legal_actions", [])), "after_has_legal": "legal_actions" in after_snap})

    spar_path = ROOT / "data" / "rev0007_sparring_agent_probe.csv"
    spar_summary_path = ROOT / "data" / "rev0007_sparring_agent_probe_summary.json"
    spar_rows = count_csv_rows(spar_path) if spar_path.exists() else -1
    spar_summary = load_json(spar_summary_path)
    add(checks, "rev0007_sparring_agent_probe", spar_rows == 512 and spar_summary.get("games") == 512 and set(spar_summary.get("agents", [])) == {"random", "heuristic", "counter_happy", "threat_rush"}, {"rows": spar_rows, "summary_games": spar_summary.get("games"), "agents": spar_summary.get("agents")})


    payoff_games_path = ROOT / "data" / "rev0008_payoff_games.csv"
    payoff_agg_path = ROOT / "data" / "rev0008_payoff_aggregate.csv"
    payoff_summary_path = ROOT / "data" / "rev0008_payoff_summary.json"
    payoff_rows = count_csv_rows(payoff_games_path) if payoff_games_path.exists() else -1
    payoff_agg_rows = count_csv_rows(payoff_agg_path) if payoff_agg_path.exists() else -1
    payoff_summary = load_json(payoff_summary_path)
    add(checks, "rev0008_payoff_table", payoff_rows == 256 and payoff_agg_rows == 128 and payoff_summary.get("games") == 256 and payoff_summary.get("aggregate_rows") == 128, {"payoff_rows": payoff_rows, "aggregate_rows": payoff_agg_rows, "summary_games": payoff_summary.get("games"), "summary_aggregate_rows": payoff_summary.get("aggregate_rows")})

    profile_summary_path = ROOT / "data" / "rev0008_simulator_profile_summary.json"
    cprofile_path = ROOT / "data" / "rev0008_cprofile_top.txt"
    profile_summary = load_json(profile_summary_path)
    fast = profile_summary.get("fast_unvalidated", {})
    validated = profile_summary.get("validated", {})
    logged = profile_summary.get("logged_unvalidated", {})
    add(checks, "rev0008_profile_outputs", profile_summary_path.exists() and cprofile_path.exists() and fast.get("decisions_per_second", 0) > 0 and validated.get("decisions_per_second", 0) > 0 and logged.get("decisions_per_second", 0) > 0, {"profile_exists": profile_summary_path.exists(), "cprofile_exists": cprofile_path.exists(), "fast_dps": fast.get("decisions_per_second"), "validated_dps": validated.get("decisions_per_second"), "logged_dps": logged.get("decisions_per_second")})

    bench = benchmark_agent_games(seed, seed, games=2, max_decisions=20, validate_actions=False, record_log=False)
    add(checks, "rev0008_benchmark_helper_runs", bench.games == 2 and bench.games_per_second > 0 and bench.decisions_per_second > 0, bench.as_dict())

    bundles = default_strategy_bundles(ROOT / "data" / "seed_decks.json")
    add(checks, "rev0008_default_strategy_population", len(bundles) == 8 and {b.agent_name for b in bundles} == {"heuristic", "counter_happy", "threat_rush"}, {"bundle_count": len(bundles), "agents": sorted({b.agent_name for b in bundles})})

    # rev0009: cloudtainer-bound office, leakage guard, and public DecisionFrame path.
    state_leak = env20.state
    if state_leak is not None:
        state_leak.pending_choice = PendingChoice(0, "jace_plus2", {"target_player": 1, "seen_top_card": "JaceTheMindSculptor", "resume": "MAIN"})
        leak_checks = audit_observation_shape(state_leak, 0) + audit_observation_shape(state_leak, 1)
        actor_seen = state_leak.observation(0)["pending_choice_data"].get("seen_top_card") == "JaceTheMindSculptor"
        non_actor_redacted = state_leak.observation(1)["pending_choice_data"].get("redacted") is True
    else:
        leak_checks = []
        actor_seen = False
        non_actor_redacted = False
    add(checks, "rev0009_observation_leak_guard", bool(leak_checks) and all_checks_pass(leak_checks) and actor_seen and non_actor_redacted, {"checks": len(leak_checks), "actor_seen": actor_seen, "non_actor_redacted": non_actor_redacted})

    state_frame = MUC5SlotEnv(seed, seed, max_action_slots=64, max_decisions=20, starting_life=20, mulligan_policy=POLICY_LAND_BAND).reset(seed=909)
    # Use a raw engine state for the revision guard test.
    from src.muc5.engine import start_game as _start_game
    raw_state = _start_game(seed, seed, seed=909, mulligan_policy=POLICY_LAND_BAND, record_log=False)
    frame = build_decision_frame(raw_state)
    idx = PublicHeuristicAgent().choose_action_index(frame, __import__("random").Random(1))
    apply_decision_index(raw_state, frame, idx, __import__("random").Random(1))
    stale_rejected = False
    try:
        apply_decision_index(raw_state, frame, idx, __import__("random").Random(1))
    except ValueError:
        stale_rejected = True
    add(checks, "rev0009_decision_frame_revision_guard", stale_rejected and raw_state.revision >= 1, {"stale_rejected": stale_rejected, "revision": raw_state.revision})

    public_bench = benchmark_public_decision_games(seed, seed, games=2, max_decisions=20, record_log=False)
    add(checks, "rev0009_public_decision_benchmark_runs", public_bench.games == 2 and public_bench.games_per_second > 0 and public_bench.decisions_per_second > 0, public_bench.as_dict())

    cloud_tools = load_json(ROOT / "data" / "rev0009_cloudtainer_tools.json")
    add(checks, "rev0009_cloudtainer_tools_recorded", bool(cloud_tools.get("python")) and bool(cloud_tools.get("packages")) and "numpy" in cloud_tools.get("packages", {}), {"has_python": bool(cloud_tools.get("python")), "package_count": len(cloud_tools.get("packages", {}))})

    leak_report = load_json(ROOT / "data" / "rev0009_leakage_audit.json")
    add(checks, "rev0009_leakage_audit_passed", leak_report.get("overall_passed") is True and leak_report.get("non_actor_pending_data_redacted") is True, {"overall_passed": leak_report.get("overall_passed"), "non_actor_pending_data_redacted": leak_report.get("non_actor_pending_data_redacted")})

    df_profile = load_json(ROOT / "data" / "rev0009_decisionframe_profile_summary.json")
    add(checks, "rev0009_decisionframe_profile_recorded", bool(df_profile.get("public_decision_frame")) and df_profile.get("public_decision_frame", {}).get("decisions_per_second", 0) > 0, {"public_dps": df_profile.get("public_decision_frame", {}).get("decisions_per_second")})

    mb_path = ROOT / "data" / "rev0009_mulligan_bundle_payoff_games.csv"
    mb_agg_path = ROOT / "data" / "rev0009_mulligan_bundle_payoff_aggregate.csv"
    mb_summary_path = ROOT / "data" / "rev0009_mulligan_bundle_payoff_summary.json"
    mb_rows = count_csv_rows(mb_path) if mb_path.exists() else -1
    mb_agg_rows = count_csv_rows(mb_agg_path) if mb_agg_path.exists() else -1
    mb_summary = load_json(mb_summary_path)
    expected_strategies = len(mulligan_strategy_bundles(ROOT / "data" / "seed_decks.json"))
    add(checks, "rev0009_mulligan_bundle_payoff", expected_strategies == 9 and mb_rows == 9 * 9 * 2 * 2 and mb_agg_rows == 9 * 9 * 2 and mb_summary.get("games") == mb_rows, {"strategies": expected_strategies, "rows": mb_rows, "aggregate_rows": mb_agg_rows, "summary_games": mb_summary.get("games")})


    # rev0010: simulator readiness, directed rules scenarios, public-frame fuzzing, and trigger/target-state fixes.
    rules_rows = count_csv_rows(ROOT / "data" / "rev0010_rules_scenarios.csv") if (ROOT / "data" / "rev0010_rules_scenarios.csv").exists() else -1
    rules_summary = load_json(ROOT / "data" / "rev0010_rules_scenarios_summary.json")
    add(checks, "rev0010_rules_scenarios", rules_rows == 5 and rules_summary.get("scenario_count") == 5 and rules_summary.get("failed") == 0 and rules_summary.get("all_passed") is True, {"rows": rules_rows, "scenario_count": rules_summary.get("scenario_count"), "failed": rules_summary.get("failed"), "all_passed": rules_summary.get("all_passed")})

    fuzz_summary = load_json(ROOT / "data" / "rev0010_fuzz_summary.json")
    add(checks, "rev0010_public_decision_fuzz", fuzz_summary.get("games") == 300 and fuzz_summary.get("failures") == 0 and fuzz_summary.get("invariant_checks", 0) > 0 and fuzz_summary.get("observation_checks", 0) > 0, {"games": fuzz_summary.get("games"), "decisions": fuzz_summary.get("decisions"), "failures": fuzz_summary.get("failures"), "invariant_checks": fuzz_summary.get("invariant_checks"), "observation_checks": fuzz_summary.get("observation_checks"), "truncations": fuzz_summary.get("truncations")})

    rev10_profile = load_json(ROOT / "data" / "rev0010_simulator_profile_summary.json")
    rev10_public = rev10_profile.get("public_decision_frame", {})
    add(checks, "rev0010_profile_recorded", (ROOT / "data" / "rev0010_cprofile_top.txt").exists() and rev10_public.get("decisions_per_second", 0) > 0, {"cprofile_exists": (ROOT / "data" / "rev0010_cprofile_top.txt").exists(), "public_dps": rev10_public.get("decisions_per_second")})

    readiness = load_json(ROOT / "data" / "rev0010_simulator_readiness.json")
    levels = {row.get("level"): row.get("status") for row in readiness.get("readiness_levels", [])}
    add(checks, "rev0010_readiness_summary", readiness.get("revision") == "rev0010" and levels.get("A: automated-play smoke simulator") == "green" and levels.get("B: learning-loop beta simulator") == "yellow", {"revision": readiness.get("revision"), "levels": levels, "evidence": readiness.get("evidence")})



    # rev0011: deterministic replay lab, reward/truncation guard, and question bank.
    replay_rows = count_csv_rows(ROOT / "data" / "rev0011_replay_probe.csv") if (ROOT / "data" / "rev0011_replay_probe.csv").exists() else -1
    replay_summary = load_json(ROOT / "data" / "rev0011_replay_probe_summary.json")
    traces_path = ROOT / "data" / "rev0011_replay_traces.jsonl"
    traces = read_trace_jsonl(traces_path) if traces_path.exists() else []
    replay_sample_ok = False
    if traces:
        replay_sample_ok = replay_public_decision_trace(traces[0]).passed
    add(checks, "rev0011_replay_probe", replay_rows == 24 and replay_summary.get("trace_count") == 24 and replay_summary.get("all_replays_passed") is True and replay_sample_ok, {"rows": replay_rows, "trace_count": replay_summary.get("trace_count"), "all_replays_passed": replay_summary.get("all_replays_passed"), "sample_replay_ok": replay_sample_ok, "total_recorded_decisions": replay_summary.get("total_recorded_decisions")})

    reward_summary = load_json(ROOT / "data" / "rev0011_reward_guard_summary.json")
    reward_rows = count_csv_rows(ROOT / "data" / "rev0011_reward_guard_packets.csv") if (ROOT / "data" / "rev0011_reward_guard_packets.csv").exists() else -1
    add(checks, "rev0011_reward_guard_outputs", reward_rows == 4 and reward_summary.get("forced_truncation_detected") is True and reward_summary.get("payoff_rows_passed") is True, {"reward_rows": reward_rows, "forced_truncation_detected": reward_summary.get("forced_truncation_detected"), "payoff_rows_checked": reward_summary.get("payoff_rows_checked"), "payoff_rows_passed": reward_summary.get("payoff_rows_passed")})

    qbank = load_json(ROOT / "data" / "rev0011_question_bank.json")
    add(checks, "rev0011_question_bank", qbank.get("revision") == "rev0011" and len(qbank.get("questions", [])) >= 10 and any(q.get("id") == "q003_truncation_stall_hack" for q in qbank.get("questions", [])), {"revision": qbank.get("revision"), "question_count": len(qbank.get("questions", []))})

    # Quick live smoke for new modules, independent of generated artifacts.
    live_trace = record_public_decision_trace(seed, seed, PublicHeuristicAgent(), PublicHeuristicAgent(), seed=1201, max_decisions=12, mulligan_policy=POLICY_LAND_BAND)
    live_replay = replay_public_decision_trace(live_trace)
    packet = reward_packet_from_state(raw_state, 0)
    packet_ok, packet_errors = audit_reward_packet(packet, allow_truncation_training_reward=True)
    add(checks, "rev0011_live_replay_and_reward_smoke", live_replay.passed and packet_ok and bool(state_fingerprint(raw_state)), {"live_replay_passed": live_replay.passed, "packet_ok": packet_ok, "packet_errors": packet_errors})

    # rev0012: public-agent payoff promotion gate and response-oracle seeding.
    public_payoff_path = ROOT / "data" / "rev0012_public_payoff_games.csv"
    public_rows = list(csv.DictReader(public_payoff_path.open())) if public_payoff_path.exists() else []
    public_summary = load_json(ROOT / "data" / "rev0012_public_payoff_summary.json")
    replay_results_path = ROOT / "data" / "rev0012_public_payoff_replay_results.json"
    replay_results = json.loads(replay_results_path.read_text()) if replay_results_path.exists() else []
    gate_live = audit_promotion_rows(public_rows, replay_results=replay_results, config=PromotionGateConfig(min_rows=324, min_replay_traces=6)) if public_rows else None
    add(checks, "rev0012_public_payoff_promotion_gate", len(public_rows) == 324 and public_summary.get("promotion_gate", {}).get("passed") is True and gate_live is not None and gate_live.passed and len(replay_results) == 6, {"rows": len(public_rows), "summary_gate_passed": public_summary.get("promotion_gate", {}).get("passed"), "live_gate_passed": None if gate_live is None else gate_live.passed, "replay_results": len(replay_results)})

    oracle_candidates_rows = count_csv_rows(ROOT / "data" / "rev0012_oracle_seed_candidates.csv") if (ROOT / "data" / "rev0012_oracle_seed_candidates.csv").exists() else -1
    oracle_games_rows = count_csv_rows(ROOT / "data" / "rev0012_oracle_seed_games.csv") if (ROOT / "data" / "rev0012_oracle_seed_games.csv").exists() else -1
    oracle_summary = load_json(ROOT / "data" / "rev0012_oracle_seed_summary.json")
    add(checks, "rev0012_oracle_seed_outputs", oracle_candidates_rows == 10 and oracle_games_rows == 288 and oracle_summary.get("games") == 288 and oracle_summary.get("candidate_decks") == 10, {"candidate_rows": oracle_candidates_rows, "game_rows": oracle_games_rows, "summary_games": oracle_summary.get("games"), "candidate_decks": oracle_summary.get("candidate_decks")})

    state_pub, result_pub = play_public_agent_game(seed, seed, make_public_agent("heuristic"), make_public_agent("counter_happy"), seed=1212, max_decisions=24, mulligan_policies=(POLICY_LAND_BAND, POLICY_LAND_BAND))
    inv_pub = card_conservation_report(state_pub)
    add(checks, "rev0012_live_public_agent_smoke", result_pub.decisions > 0 and inv_pub.passed and getattr(make_public_agent("threat_rush"), "name", "").startswith("public_"), {"decisions": result_pub.decisions, "winner": result_pub.winner, "loss_reason": result_pub.loss_reason, "invariant_errors": inv_pub.errors})

    live_candidates = generate_oracle_candidates([seed], seed=99, random_samples=30, mutations_per_base=3, keep=3)
    add(checks, "rev0012_live_oracle_candidate_smoke", len(live_candidates) == 3 and all(c.deck.threats >= 1 and c.deck.interaction >= 1 for c in live_candidates), {"candidate_count": len(live_candidates), "decks": [c.deck.as_tuple() for c in live_candidates]})

    qbank12 = load_json(ROOT / "data" / "rev0012_question_bank.json")
    add(checks, "rev0012_question_bank", qbank12.get("revision") == "rev0012" and len(qbank12.get("questions", [])) >= 12 and any(q.get("id") == "q006_code_policy_oracle" for q in qbank12.get("questions", [])), {"revision": qbank12.get("revision"), "question_count": len(qbank12.get("questions", []))})



    # rev0013: readable code-policy oracles and public-vs-trusted diagnostic gap.
    code_games_path = ROOT / "data" / "rev0013_code_policy_payoff_games.csv"
    code_agg_path = ROOT / "data" / "rev0013_code_policy_payoff_aggregate.csv"
    code_standings_path = ROOT / "data" / "rev0013_code_policy_payoff_standings.csv"
    code_lint_path = ROOT / "data" / "rev0013_code_policy_lint.csv"
    code_summary = load_json(ROOT / "data" / "rev0013_code_policy_payoff_summary.json")
    code_rows = list(csv.DictReader(code_games_path.open())) if code_games_path.exists() else []
    code_replay_path = ROOT / "data" / "rev0013_code_policy_replay_results.json"
    code_replay = json.loads(code_replay_path.read_text()) if code_replay_path.exists() else []
    code_gate_live = audit_promotion_rows(code_rows, replay_results=code_replay, config=PromotionGateConfig(simulator_revision="rev0013", min_rows=144, min_replay_traces=6)) if code_rows else None
    lint_rows = list(csv.DictReader(code_lint_path.open())) if code_lint_path.exists() else []
    add(checks, "rev0013_code_policy_payoff_gate", len(code_rows) == 144 and count_csv_rows(code_agg_path) == 72 and count_csv_rows(code_standings_path) == 6 and code_summary.get("promotion_gate", {}).get("passed") is True and code_gate_live is not None and code_gate_live.passed and len(code_replay) == 6, {"rows": len(code_rows), "aggregate_rows": count_csv_rows(code_agg_path) if code_agg_path.exists() else -1, "standings_rows": count_csv_rows(code_standings_path) if code_standings_path.exists() else -1, "summary_gate": code_summary.get("promotion_gate", {}).get("passed"), "live_gate": None if code_gate_live is None else code_gate_live.passed, "replay_results": len(code_replay)})
    add(checks, "rev0013_code_policy_lint", len(lint_rows) == 3 and all(str(r.get("ok")).lower() == "true" for r in lint_rows) and len(code_policy_catalog()) >= 3, {"lint_rows": len(lint_rows), "catalog": code_policy_catalog()})

    gap_path = ROOT / "data" / "rev0013_public_trusted_gap.csv"
    gap_summary_csv = ROOT / "data" / "rev0013_public_trusted_gap_summary.csv"
    gap_summary = load_json(ROOT / "data" / "rev0013_public_trusted_gap_summary.json")
    gap_rows = count_csv_rows(gap_path) if gap_path.exists() else -1
    gap_summary_rows = list(csv.DictReader(gap_summary_csv.open())) if gap_summary_csv.exists() else []
    exact = next((r for r in gap_summary_rows if r.get("comparison") == "heuristic_exact"), {})
    add(checks, "rev0013_public_trusted_gap", gap_rows == 256 and gap_summary.get("rows") == 256 and float(exact.get("same_winner_rate", 0)) == 1.0 and float(exact.get("mean_abs_decision_delta", -1)) == 0.0, {"rows": gap_rows, "summary_rows": gap_summary.get("rows"), "heuristic_exact": exact})

    qbank13 = load_json(ROOT / "data" / "rev0013_question_bank.json")
    add(checks, "rev0013_question_bank", qbank13.get("revision") == "rev0013" and len(qbank13.get("questions", [])) >= 12 and any(q.get("id") == "q008_map_elites" for q in qbank13.get("questions", [])), {"revision": qbank13.get("revision"), "question_count": len(qbank13.get("questions", []))})

    live_code_agent = make_public_agent("code_jace_lock_rev0013")
    state_code, result_code = play_public_agent_game(seed, seed, live_code_agent, make_public_agent("code_overlord_clock_rev0013"), seed=1313, max_decisions=24, mulligan_policies=(POLICY_LAND_BAND, POLICY_LAND_BAND))
    code_inv = card_conservation_report(state_code)
    live_frame = build_decision_frame(_start_game(seed, seed, seed=1314, mulligan_policy=POLICY_LAND_BAND, record_log=False))
    lint_ok, lint_errors = smoke_lint_code_policy(make_code_policy_agent("code_force_conservative_rev0013"), [live_frame])
    add(checks, "rev0013_live_code_policy_smoke", result_code.decisions > 0 and code_inv.passed and lint_ok and live_code_agent.name == "code_jace_lock_rev0013", {"decisions": result_code.decisions, "winner": result_code.winner, "invariant_errors": code_inv.errors, "lint_errors": lint_errors})



    # rev0014: statistical uncertainty gate, static MAP-Elites archive, and public-agent parameter-name refactor.
    stat_games_path = ROOT / "data" / "rev0014_statgate_payoff_games.csv"
    stat_rows = list(csv.DictReader(stat_games_path.open())) if stat_games_path.exists() else []
    stat_standings_path = ROOT / "data" / "rev0014_statgate_standings.csv"
    stat_pair_path = ROOT / "data" / "rev0014_statgate_pairwise.csv"
    stat_summary = load_json(ROOT / "data" / "rev0014_statgate_summary.json")
    stat_standings = list(csv.DictReader(stat_standings_path.open())) if stat_standings_path.exists() else []
    stat_pairs = list(csv.DictReader(stat_pair_path.open())) if stat_pair_path.exists() else []
    live_stat_gate = audit_statistical_gate(stat_rows, statistical_standings(stat_rows, min_games_for_claim=60), pairwise_stat_rows(stat_rows, min_games_for_claim=6), min_raw_rows=768, max_truncation_rate=0.10) if stat_rows else None
    add(checks, "rev0014_statgate_outputs", len(stat_rows) == 768 and count_csv_rows(ROOT / "data" / "rev0014_statgate_payoff_aggregate.csv") == 128 and len(stat_standings) == 8 and len(stat_pairs) == 128 and stat_summary.get("statistical_gate", {}).get("passed") is True and live_stat_gate is not None and live_stat_gate.passed, {"rows": len(stat_rows), "aggregate_rows": count_csv_rows(ROOT / "data" / "rev0014_statgate_payoff_aggregate.csv") if (ROOT / "data" / "rev0014_statgate_payoff_aggregate.csv").exists() else -1, "standings": len(stat_standings), "pairs": len(stat_pairs), "summary_gate": stat_summary.get("statistical_gate", {}).get("passed"), "live_gate": None if live_stat_gate is None else live_stat_gate.passed})
    top_lcb_sorted = all(float(stat_standings[i]["score_lcb_95"]) >= float(stat_standings[i + 1]["score_lcb_95"]) for i in range(max(0, len(stat_standings) - 1))) if stat_standings else False
    add(checks, "rev0014_statgate_lcb_sorted", top_lcb_sorted and int(stat_summary.get("claim_ready_strategy_count", 0)) >= 0, {"sorted": top_lcb_sorted, "claim_ready_strategy_count": stat_summary.get("claim_ready_strategy_count"), "top": stat_standings[:2]})

    map_path = ROOT / "data" / "rev0014_map_elites_archive.csv"
    map_summary = load_json(ROOT / "data" / "rev0014_map_elites_summary.json")
    map_rows = count_csv_rows(map_path) if map_path.exists() else -1
    seed_desc = deck_descriptor(seed)
    add(checks, "rev0014_map_elites_archive", map_rows == map_summary.get("cells") and map_rows >= 40 and "land_bin" in seed_desc and map_summary.get("best_quality", 0) >= map_summary.get("worst_quality", 0), {"rows": map_rows, "summary_cells": map_summary.get("cells"), "best_quality": map_summary.get("best_quality"), "seed_descriptor": seed_desc})

    pub_agent = __import__("src.muc5.public_agents", fromlist=["PublicProfileAgent"]).PublicProfileAgent("heuristic")
    score_pitch_force = pub_agent.score_action({"frame": "RESPONSE", "starting_life": 20, "public_self": {"life": 20}, "public_opponent": {}, "own_hand": {}}, Action("CAST", {"card": "ForceOfWill", "target_card": "JaceTheMindSculptor", "payment": "pitch", "pitch_card": "ForceOfWill"}))
    score_pitch_jace = pub_agent.score_action({"frame": "RESPONSE", "starting_life": 20, "public_self": {"life": 20}, "public_opponent": {}, "own_hand": {}}, Action("CAST", {"card": "ForceOfWill", "target_card": "JaceTheMindSculptor", "payment": "pitch", "pitch_card": "JaceTheMindSculptor"}))
    block_none = pub_agent.score_action({"frame": "BLOCK", "starting_life": 20, "public_self": {"life": 3}, "public_opponent": {}, "own_hand": {}}, Action("BLOCK", {"block_player_attackers": 0, "block_jace_attackers": 0}))
    block_face = pub_agent.score_action({"frame": "BLOCK", "starting_life": 20, "public_self": {"life": 3}, "public_opponent": {}, "own_hand": {}}, Action("BLOCK", {"block_player_attackers": 1, "block_jace_attackers": 0}))
    add(checks, "rev0014_public_agent_param_fix", score_pitch_jace > score_pitch_force and block_face > block_none and len(statgate_probe_strategy_bundles(ROOT / "data" / "seed_decks.json")) == 8, {"score_pitch_force": score_pitch_force, "score_pitch_jace": score_pitch_jace, "block_none": block_none, "block_face": block_face})



    # rev0015: C++ probe bridge, selected MAP-Elites gameplay eval, stall adversary, and action-feature encoder.
    cpp_summary = load_json(ROOT / "data" / "rev0015_cpp_probe_benchmark.json")
    cpp_top_rows = count_csv_rows(ROOT / "data" / "rev0015_cpp_probe_top10.csv") if (ROOT / "data" / "rev0015_cpp_probe_top10.csv").exists() else -1
    live_cpp_status = cpp_toolchain_status(try_build=True).as_dict()
    add(checks, "rev0015_cpp_probe_bridge", cpp_summary.get("toolchain_status", {}).get("usable") is True and live_cpp_status.get("usable") is True and cpp_summary.get("max_abs_diff_vs_python_sample", 1.0) < 1e-12 and cpp_summary.get("cpp_rows_per_second", 0) > 0 and cpp_top_rows == 10, {"summary_usable": cpp_summary.get("toolchain_status", {}).get("usable"), "live_usable": live_cpp_status.get("usable"), "max_abs_diff": cpp_summary.get("max_abs_diff_vs_python_sample"), "cpp_rps": cpp_summary.get("cpp_rows_per_second"), "top_rows": cpp_top_rows})

    map15_games = list(csv.DictReader((ROOT / "data" / "rev0015_mapelite_eval_games.csv").open())) if (ROOT / "data" / "rev0015_mapelite_eval_games.csv").exists() else []
    map15_summary = load_json(ROOT / "data" / "rev0015_mapelite_eval_summary.json")
    map15_replay = json.loads((ROOT / "data" / "rev0015_mapelite_eval_replay_results.json").read_text()) if (ROOT / "data" / "rev0015_mapelite_eval_replay_results.json").exists() else []
    map15_gate = audit_promotion_rows(map15_games, replay_results=map15_replay, config=PromotionGateConfig(simulator_revision="rev0015", min_rows=288, min_replay_traces=6, max_truncation_rate=0.20)) if map15_games else None
    add(checks, "rev0015_mapelite_eval_gate", len(map15_games) == 288 and count_csv_rows(ROOT / "data" / "rev0015_mapelite_eval_aggregate.csv") == 72 and count_csv_rows(ROOT / "data" / "rev0015_mapelite_eval_standings.csv") == 6 and map15_summary.get("promotion_gate", {}).get("passed") is True and map15_summary.get("statistical_gate", {}).get("passed") is True and map15_gate is not None and map15_gate.passed and len(map15_replay) == 6, {"games": len(map15_games), "aggregate_rows": count_csv_rows(ROOT / "data" / "rev0015_mapelite_eval_aggregate.csv") if (ROOT / "data" / "rev0015_mapelite_eval_aggregate.csv").exists() else -1, "standings": count_csv_rows(ROOT / "data" / "rev0015_mapelite_eval_standings.csv") if (ROOT / "data" / "rev0015_mapelite_eval_standings.csv").exists() else -1, "summary_promo": map15_summary.get("promotion_gate", {}).get("passed"), "summary_stat": map15_summary.get("statistical_gate", {}).get("passed"), "live_gate": None if map15_gate is None else map15_gate.passed, "replays": len(map15_replay)})

    stall_summary = load_json(ROOT / "data" / "rev0015_stall_adversary_summary.json")
    stall_rows = count_csv_rows(ROOT / "data" / "rev0015_stall_adversary_games.csv") if (ROOT / "data" / "rev0015_stall_adversary_games.csv").exists() else -1
    add(checks, "rev0015_stall_adversary_detected", stall_rows == 128 and stall_summary.get("guard_detected_stall_truncation") is True and stall_summary.get("strict_promotion_gate_expected_to_fail", {}).get("passed") is False and stall_summary.get("truncation_games", 0) > 0, {"rows": stall_rows, "guard_detected": stall_summary.get("guard_detected_stall_truncation"), "strict_gate_passed": stall_summary.get("strict_promotion_gate_expected_to_fail", {}).get("passed"), "truncation_games": stall_summary.get("truncation_games")})

    af_names = action_feature_names()
    af_vec = action_feature_vector(Action("CAST", {"card": "ForceOfWill", "target_card": "JaceTheMindSculptor", "payment": "pitch", "pitch_card": "OverlordOfTheFloodpits"}), {"frame": "RESPONSE"})
    af = dict(zip(af_names, af_vec))
    stall_agent = make_public_agent("stall")
    stall_play_land = stall_agent.score_action({"frame": "MAIN", "starting_life": 20, "public_self": {"life": 20}, "public_opponent": {}}, Action("PLAY_ISLAND", {}))
    stall_jace = stall_agent.score_action({"frame": "MAIN", "starting_life": 20, "public_self": {"life": 20}, "public_opponent": {}}, Action("CAST", {"card": "JaceTheMindSculptor"}))
    add(checks, "rev0015_action_features_and_stall_live", len(af_names) >= 40 and len(af_names) == len(af_vec) and af.get("cast_force") == 1.0 and af.get("target_jace") == 1.0 and af.get("pitch_overlord") == 1.0 and stall_play_land > stall_jace, {"feature_count": len(af_names), "cast_force": af.get("cast_force"), "target_jace": af.get("target_jace"), "pitch_overlord": af.get("pitch_overlord"), "stall_play_land_score": stall_play_land, "stall_jace_score": stall_jace})

    qbank15 = load_json(ROOT / "data" / "rev0015_question_bank.json")
    add(checks, "rev0015_question_bank", qbank15.get("revision") == "rev0015" and len(qbank15.get("questions", [])) >= 10 and any(q.get("id") == "q001_cpp_legal_menu" for q in qbank15.get("questions", [])), {"revision": qbank15.get("revision"), "question_count": len(qbank15.get("questions", []))})

    # rev0016: C++ legal-menu differential harness and sequential racing scaffold.
    legal_status = cpp_legal_tool_status(try_build=True).as_dict()
    add(checks, "rev0016_cpp_legal_tool_status", bool(legal_status.get("usable")) and bool(legal_status.get("gpp")), legal_status)

    legal_diff_summary = load_json(ROOT / "data" / "rev0016_cpp_legal_diff_summary.json")
    legal_diff_mismatches = load_json(ROOT / "data" / "rev0016_cpp_legal_diff_mismatches.json")
    legal_diff_rows = count_csv_rows(ROOT / "data" / "rev0016_cpp_legal_diff_games.csv") if (ROOT / "data" / "rev0016_cpp_legal_diff_games.csv").exists() else -1
    add(
        checks,
        "rev0016_cpp_legal_diff",
        legal_diff_summary.get("mismatches") == 0
        and legal_diff_summary.get("decision_records", 0) >= 10000
        and legal_diff_rows == legal_diff_summary.get("games")
        and not legal_diff_mismatches
        and {"MAIN", "RESPONSE", "ATTACK"}.issubset(set(legal_diff_summary.get("frame_counts", {}).keys())),
        {
            "games": legal_diff_rows,
            "decision_records": legal_diff_summary.get("decision_records"),
            "mismatches": legal_diff_summary.get("mismatches"),
            "frames": legal_diff_summary.get("frame_counts"),
            "pending": legal_diff_summary.get("pending_choice_counts"),
        },
    )

    seq_summary = load_json(ROOT / "data" / "rev0016_sequential_race_summary.json")
    seq_games = count_csv_rows(ROOT / "data" / "rev0016_sequential_race_games.csv") if (ROOT / "data" / "rev0016_sequential_race_games.csv").exists() else -1
    seq_standings = count_csv_rows(ROOT / "data" / "rev0016_sequential_race_standings.csv") if (ROOT / "data" / "rev0016_sequential_race_standings.csv").exists() else -1
    seq_stage_path = ROOT / "data" / "rev0016_sequential_race_stages.json"
    add(
        checks,
        "rev0016_sequential_race",
        seq_games == seq_summary.get("games")
        and seq_summary.get("stage_count") == 2
        and seq_summary.get("promotion_style_statistical_gate", {}).get("passed") is True
        and seq_summary.get("truncations") == 0
        and seq_standings >= seq_summary.get("candidate_count", 0)
        and seq_stage_path.exists(),
        {
            "games": seq_games,
            "standings": seq_standings,
            "stage_count": seq_summary.get("stage_count"),
            "candidate_count": seq_summary.get("candidate_count"),
            "truncations": seq_summary.get("truncations"),
            "gate": seq_summary.get("promotion_style_statistical_gate"),
        },
    )



    # rev0017: C++ transition microkernel differential harness and meta-rank adapter.
    trans_status = cpp_transition_tool_status(try_build=True).as_dict()
    add(checks, "rev0017_cpp_transition_tool_status", bool(trans_status.get("usable")) and bool(trans_status.get("gpp")), trans_status)

    trans_summary = load_json(ROOT / "data" / "rev0017_cpp_transition_diff_summary.json")
    trans_mismatch_path = ROOT / "data" / "rev0017_cpp_transition_mismatches.json"
    trans_mismatches = json.loads(trans_mismatch_path.read_text()) if trans_mismatch_path.exists() else None
    trans_cases_rows = count_csv_rows(ROOT / "data" / "rev0017_cpp_transition_cases.csv") if (ROOT / "data" / "rev0017_cpp_transition_cases.csv").exists() else -1
    add(
        checks,
        "rev0017_cpp_transition_diff",
        trans_summary.get("mismatches") == 0
        and trans_cases_rows == trans_summary.get("total_cases")
        and trans_summary.get("total_cases", 0) >= 1000
        and trans_summary.get("directed_cases", 0) >= 12
        and trans_summary.get("sampled_cases", 0) >= 1000
        and trans_mismatches == [],
        {
            "cases": trans_cases_rows,
            "total_cases": trans_summary.get("total_cases"),
            "directed_cases": trans_summary.get("directed_cases"),
            "sampled_cases": trans_summary.get("sampled_cases"),
            "mismatches": trans_summary.get("mismatches"),
            "action_kinds": trans_summary.get("action_kinds"),
        },
    )

    mr_games_path = ROOT / "data" / "rev0017_metarank_payoff_games.csv"
    mr_agg_path = ROOT / "data" / "rev0017_metarank_payoff_aggregate.csv"
    mr_rows = list(csv.DictReader(mr_games_path.open())) if mr_games_path.exists() else []
    mr_agg_rows = list(csv.DictReader(mr_agg_path.open())) if mr_agg_path.exists() else []
    mr_summary = load_json(ROOT / "data" / "rev0017_metarank_summary.json")
    mr_replay_path = ROOT / "data" / "rev0017_metarank_replay_results.json"
    mr_replay = json.loads(mr_replay_path.read_text()) if mr_replay_path.exists() else []
    mr_gate = audit_promotion_rows(mr_rows, replay_results=mr_replay, config=PromotionGateConfig(simulator_revision="rev0017", min_rows=512, min_replay_traces=8, max_truncation_rate=0.25)) if mr_rows else None
    mr_live = [r.as_dict() for r in meta_rank_from_aggregate(mr_agg_rows)] if mr_agg_rows else []
    mr_all_rows = count_csv_rows(ROOT / "data" / "rev0017_metarank_all.csv") if (ROOT / "data" / "rev0017_metarank_all.csv").exists() else -1
    add(
        checks,
        "rev0017_metarank_outputs",
        len(mr_rows) == 512
        and len(mr_agg_rows) == 128
        and mr_all_rows == 8
        and mr_summary.get("promotion_gate", {}).get("passed") is True
        and mr_summary.get("statistical_gate", {}).get("passed") is True
        and mr_gate is not None and mr_gate.passed
        and len(mr_replay) == 8
        and len(mr_live) == 8
        and abs(sum(float(r["meta_rank_mass"]) for r in mr_live) - 1.0) < 1e-9,
        {
            "games": len(mr_rows),
            "aggregate_rows": len(mr_agg_rows),
            "metarank_rows": mr_all_rows,
            "summary_promo": mr_summary.get("promotion_gate", {}).get("passed"),
            "summary_stat": mr_summary.get("statistical_gate", {}).get("passed"),
            "live_gate": None if mr_gate is None else mr_gate.passed,
            "replays": len(mr_replay),
            "live_meta_mass_sum": None if not mr_live else sum(float(r["meta_rank_mass"]) for r in mr_live),
            "top_live_meta": mr_live[:2],
        },
    )



    trans18_summary = load_json(ROOT / "data" / "rev0018_cpp_transition_diff_summary.json")
    trans18_cases = count_csv_rows(ROOT / "data" / "rev0018_cpp_transition_cases.csv") if (ROOT / "data" / "rev0018_cpp_transition_cases.csv").exists() else -1
    trans18_mismatches = load_json(ROOT / "data" / "rev0018_cpp_transition_mismatches.json") if (ROOT / "data" / "rev0018_cpp_transition_mismatches.json").exists() else []
    add(
        checks,
        "rev0018_cpp_transition_stack_choice_diff",
        trans18_summary.get("mismatches") == 0
        and trans18_summary.get("total_cases") == 10022
        and trans18_summary.get("directed_cases") == 22
        and trans18_summary.get("sampled_cases") == 10000
        and trans18_summary.get("response_pass_resolution_cases", 0) >= 800
        and trans18_summary.get("choice_cases", 0) >= 700
        and trans18_summary.get("attack_action_cases", 0) >= 50
        and trans18_cases == trans18_summary.get("total_cases")
        and trans18_mismatches == [],
        {
            "total_cases": trans18_summary.get("total_cases"),
            "directed_cases": trans18_summary.get("directed_cases"),
            "sampled_cases": trans18_summary.get("sampled_cases"),
            "mismatches": trans18_summary.get("mismatches"),
            "response_pass_resolution_cases": trans18_summary.get("response_pass_resolution_cases"),
            "choice_cases": trans18_summary.get("choice_cases"),
            "attack_action_cases": trans18_summary.get("attack_action_cases"),
            "cases_csv_rows": trans18_cases,
            "mismatches_json_len": len(trans18_mismatches) if isinstance(trans18_mismatches, list) else None,
        },
    )

    cov18_summary = load_json(ROOT / "data" / "rev0018_cpp_transition_coverage_summary.json")
    cov18_rows = count_csv_rows(ROOT / "data" / "rev0018_cpp_transition_coverage_rows.csv") if (ROOT / "data" / "rev0018_cpp_transition_coverage_rows.csv").exists() else -1
    add(
        checks,
        "rev0018_cpp_transition_coverage_probe",
        cov18_summary.get("games") == 48
        and cov18_summary.get("decisions") == 13598
        and cov18_summary.get("chosen_support_rate") == 1.0
        and cov18_summary.get("legal_action_support_rate") == 1.0
        and cov18_rows > 0,
        {
            "games": cov18_summary.get("games"),
            "decisions": cov18_summary.get("decisions"),
            "chosen_support_rate": cov18_summary.get("chosen_support_rate"),
            "legal_action_support_rate": cov18_summary.get("legal_action_support_rate"),
            "coverage_rows": cov18_rows,
            "unsupported_examples": cov18_summary.get("unsupported_chosen_examples"),
        },
    )


    # rev0019: C++ recorded public-trace transition checker.
    trace19_summary_path = ROOT / "data" / "rev0019_cpp_trace_summary.json"
    trace19_rows_path = ROOT / "data" / "rev0019_cpp_trace_rows.csv"
    trace19_traces_path = ROOT / "data" / "rev0019_public_traces.jsonl"
    trace19_summary = load_json(trace19_summary_path)
    trace19_rows = count_csv_rows(trace19_rows_path) if trace19_rows_path.exists() else -1
    unsupported = trace19_summary.get("unsupported_examples", []) or []
    unsupported_only_jace_ultimate = all(
        str(row.get("action", "")).startswith("ACTIVATE_JACE(mode=ultimate")
        for row in unsupported
    )
    add(
        checks,
        "rev0019_cpp_trace_checker",
        trace19_summary_path.exists()
        and trace19_rows_path.exists()
        and trace19_traces_path.exists()
        and trace19_summary.get("events", 0) >= 8000
        and trace19_rows == trace19_summary.get("events")
        and trace19_summary.get("mismatches") == 0
        and trace19_summary.get("python_replay_errors") == 0
        and trace19_summary.get("support_rate", 0) >= 0.99
        and trace19_summary.get("cpp_match_rate_on_supported") == 1.0
        and unsupported_only_jace_ultimate,
        {
            "summary_exists": trace19_summary_path.exists(),
            "rows": trace19_rows,
            "traces_file_exists": trace19_traces_path.exists(),
            "events": trace19_summary.get("events"),
            "supported_events": trace19_summary.get("supported_events"),
            "skipped_events": trace19_summary.get("skipped_events"),
            "mismatches": trace19_summary.get("mismatches"),
            "python_replay_errors": trace19_summary.get("python_replay_errors"),
            "support_rate": trace19_summary.get("support_rate"),
            "cpp_match_rate_on_supported": trace19_summary.get("cpp_match_rate_on_supported"),
            "unsupported_only_jace_ultimate": unsupported_only_jace_ultimate,
        },
    )


    # rev0020: Jace ultimate explicit shuffle transport and action-ranker seed.
    trace20_summary_path = ROOT / "data" / "rev0020_cpp_trace_summary.json"
    trace20_rows_path = ROOT / "data" / "rev0020_cpp_trace_rows.csv"
    trace20_traces_path = ROOT / "data" / "rev0020_public_traces.jsonl"
    trace20_summary = load_json(trace20_summary_path)
    trace20_rows = count_csv_rows(trace20_rows_path) if trace20_rows_path.exists() else -1
    add(
        checks,
        "rev0020_cpp_ultimate_trace_transport",
        trace20_summary_path.exists()
        and trace20_rows_path.exists()
        and trace20_traces_path.exists()
        and trace20_rows == trace20_summary.get("events")
        and trace20_summary.get("events", 0) >= 8000
        and trace20_summary.get("supported_events") == trace20_summary.get("events")
        and trace20_summary.get("skipped_events") == 0
        and trace20_summary.get("mismatches") == 0
        and trace20_summary.get("python_replay_errors") == 0
        and trace20_summary.get("support_rate") == 1.0
        and trace20_summary.get("cpp_match_rate_on_supported") == 1.0
        and trace20_summary.get("jace_ultimate_events", 0) > 0
        and trace20_summary.get("jace_ultimate_supported_events") == trace20_summary.get("jace_ultimate_events"),
        {
            "rows": trace20_rows,
            "events": trace20_summary.get("events"),
            "supported_events": trace20_summary.get("supported_events"),
            "skipped_events": trace20_summary.get("skipped_events"),
            "mismatches": trace20_summary.get("mismatches"),
            "python_replay_errors": trace20_summary.get("python_replay_errors"),
            "support_rate": trace20_summary.get("support_rate"),
            "jace_ultimate_events": trace20_summary.get("jace_ultimate_events"),
            "jace_ultimate_supported_events": trace20_summary.get("jace_ultimate_supported_events"),
        },
    )

    ranker_summary_path = ROOT / "data" / "rev0020_action_ranker_summary.json"
    ranker_dataset_path = ROOT / "data" / "rev0020_action_ranker_dataset.csv"
    ranker_coef_path = ROOT / "data" / "rev0020_action_ranker_coefficients.csv"
    ranker_summary = load_json(ranker_summary_path)
    ranker_rows = count_csv_rows(ranker_dataset_path) if ranker_dataset_path.exists() else -1
    collection = ranker_summary.get("collection", {}) if isinstance(ranker_summary.get("collection", {}), dict) else {}
    metrics = ranker_summary.get("ranker_metrics", {}) if isinstance(ranker_summary.get("ranker_metrics", {}), dict) else {}
    add(
        checks,
        "rev0020_action_ranker_seed",
        ranker_summary_path.exists()
        and ranker_dataset_path.exists()
        and ranker_coef_path.exists()
        and ranker_rows == collection.get("rows")
        and collection.get("decisions", 0) >= 10000
        and collection.get("chosen_rows") == collection.get("decisions")
        and ranker_summary.get("feature_count") == 81
        and metrics.get("test_top1_accuracy", 0) > metrics.get("random_slot_baseline_accuracy", 1)
        and metrics.get("test_mean_reciprocal_rank", 0) >= metrics.get("test_top1_accuracy", 0),
        {
            "rows": ranker_rows,
            "collection": collection,
            "feature_count": ranker_summary.get("feature_count"),
            "metrics": metrics,
        },
    )


    # rev0021: batched C++ trace seam and frozen public action-ranker policy.
    batch21_path = ROOT / "data" / "rev0021_cpp_batch_benchmark.json"
    batch21 = load_json(batch21_path)
    finalize21 = batch21.get("cpp_finalize_summary", {}) if isinstance(batch21.get("cpp_finalize_summary", {}), dict) else {}
    add(
        checks,
        "rev0021_cpp_batch_trace_benchmark",
        batch21_path.exists()
        and int(batch21.get("records", 0) or 0) >= 8800
        and int(batch21.get("cpp_batch_mismatches", -1)) == 0
        and int(finalize21.get("mismatches", -1)) == 0
        and int(finalize21.get("skipped_events", -1)) == 0
        and float(batch21.get("cpp_batch_records_per_second", 0.0) or 0.0) > 0
        and float(batch21.get("estimated_subprocess_overhead_ratio_vs_batch_per_record", 0.0) or 0.0) > 10.0,
        {
            "exists": batch21_path.exists(),
            "records": batch21.get("records"),
            "cpp_batch_mismatches": batch21.get("cpp_batch_mismatches"),
            "finalize_mismatches": finalize21.get("mismatches"),
            "skipped_events": finalize21.get("skipped_events"),
            "cpp_batch_rps": batch21.get("cpp_batch_records_per_second"),
            "overhead_ratio": batch21.get("estimated_subprocess_overhead_ratio_vs_batch_per_record"),
        },
    )
    try:
        traces20 = read_trace_jsonl(ROOT / "data" / "rev0020_public_traces.jsonl")
        prep21 = prepare_public_traces_for_cpp(traces20[:2], revision="rev0021_audit_sample")
        prep_ok = prep21.trace_count == 2 and prep21.events > 0 and prep21.supported_events == prep21.events and not prep21.python_errors
        prep_details = prep21.as_dict()
    except Exception as exc:
        prep_ok = False
        prep_details = {"error": repr(exc)}
    add(checks, "rev0021_cpp_trace_prepare_api", prep_ok, prep_details)

    rank21_summary_path = ROOT / "data" / "rev0021_ranker_policy_summary.json"
    rank21_model_path = ROOT / "data" / "rev0021_linear_ranker_model.json"
    rank21_games_path = ROOT / "data" / "rev0021_ranker_policy_games.csv"
    rank21_summary = load_json(rank21_summary_path)
    train21 = rank21_summary.get("training_metrics", {}) if isinstance(rank21_summary.get("training_metrics", {}), dict) else {}
    promo21 = rank21_summary.get("promotion_gate", {}) if isinstance(rank21_summary.get("promotion_gate", {}), dict) else {}
    stat21 = rank21_summary.get("statistical_gate", {}) if isinstance(rank21_summary.get("statistical_gate", {}), dict) else {}
    rank21_rows = count_csv_rows(rank21_games_path) if rank21_games_path.exists() else -1
    try:
        model21 = load_linear_ranker_model(rank21_model_path)
        model_ok = len(model21.feature_names) == len(action_ranker_feature_names()) and len(model21.coefficients) == len(model21.feature_names)
        model_details = {"model_id": model21.model_id, "feature_count": len(model21.feature_names)}
    except Exception as exc:
        model_ok = False
        model_details = {"error": repr(exc)}
    add(
        checks,
        "rev0021_linear_ranker_policy_eval",
        rank21_summary_path.exists()
        and model_ok
        and rank21_rows == 256
        and rank21_summary.get("ranker_strategy_count") == 3
        and promo21.get("passed") is True
        and stat21.get("passed") is True
        and float(train21.get("test_top1_accuracy", 0.0) or 0.0) > float(train21.get("random_slot_baseline_accuracy", 1.0) or 1.0),
        {
            "summary_exists": rank21_summary_path.exists(),
            "model": model_details,
            "rows": rank21_rows,
            "ranker_strategy_count": rank21_summary.get("ranker_strategy_count"),
            "promotion_passed": promo21.get("passed"),
            "stat_gate_passed": stat21.get("passed"),
            "test_top1": train21.get("test_top1_accuracy"),
            "random_baseline": train21.get("random_slot_baseline_accuracy"),
        },
    )


    # rev0022: blended ranker policies, staged race, and MAP-Elites same-deck pilot variants.
    try:
        blend_agent = make_public_agent("ranker_blend_threat_rev0022")
        blend_ok = getattr(blend_agent, "name", "") == "ranker_blend_threat_rush_rev0022"
        blend_details = {"name": getattr(blend_agent, "name", ""), "type": type(blend_agent).__name__}
    except Exception as exc:
        blend_ok = False
        blend_details = {"error": repr(exc)}
    add(checks, "rev0022_blended_ranker_factory", blend_ok, blend_details)

    race22_path = ROOT / "data" / "rev0022_ranker_race_games.csv"
    race22_summary_path = ROOT / "data" / "rev0022_ranker_race_summary.json"
    race22_cpp_path = ROOT / "data" / "rev0022_ranker_race_cpp_trace_summary.json"
    race22_rows = count_csv_rows(race22_path) if race22_path.exists() else -1
    race22 = load_json(race22_summary_path)
    race22_promo = race22.get("promotion_gate", {}) if isinstance(race22.get("promotion_gate", {}), dict) else {}
    race22_stat = race22.get("statistical_gate", {}) if isinstance(race22.get("statistical_gate", {}), dict) else {}
    race22_cpp = load_json(race22_cpp_path)
    add(
        checks,
        "rev0022_ranker_sequential_race",
        race22_path.exists()
        and race22_rows == race22.get("raw_games")
        and race22_rows >= 600
        and race22.get("candidate_count") == 6
        and race22.get("opponent_count") == 6
        and race22_promo.get("passed") is True
        and race22_stat.get("passed") is True
        and int(race22_cpp.get("mismatches", -1)) == 0
        and int(race22_cpp.get("skipped_events", -1)) == 0
        and int(race22_cpp.get("python_replay_errors", -1)) == 0
        and race22.get("replay_passed") == race22.get("replay_count")
        and len(race22.get("stages", [])) == 2,
        {
            "rows": race22_rows,
            "raw_games": race22.get("raw_games"),
            "candidate_count": race22.get("candidate_count"),
            "opponent_count": race22.get("opponent_count"),
            "promotion_passed": race22_promo.get("passed"),
            "stat_passed": race22_stat.get("passed"),
            "cpp": {k: race22_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
            "stages": race22.get("stages"),
        },
    )

    map22_path = ROOT / "data" / "rev0022_mapelite_ranker_variants_games.csv"
    map22_same_path = ROOT / "data" / "rev0022_mapelite_ranker_variants_same_deck_pilots.csv"
    map22_summary_path = ROOT / "data" / "rev0022_mapelite_ranker_variants_summary.json"
    map22_cpp_path = ROOT / "data" / "rev0022_mapelite_ranker_variants_cpp_trace_summary.json"
    map22_rows = count_csv_rows(map22_path) if map22_path.exists() else -1
    map22_same_rows = count_csv_rows(map22_same_path) if map22_same_path.exists() else -1
    map22 = load_json(map22_summary_path)
    map22_promo = map22.get("promotion_gate", {}) if isinstance(map22.get("promotion_gate", {}), dict) else {}
    map22_stat = map22.get("statistical_gate", {}) if isinstance(map22.get("statistical_gate", {}), dict) else {}
    map22_cpp = load_json(map22_cpp_path)
    add(
        checks,
        "rev0022_mapelite_ranker_variants",
        map22_path.exists()
        and map22_rows == map22.get("games")
        and map22_rows == 576
        and map22.get("strategy_count") == 12
        and map22_same_rows == 12
        and map22_promo.get("passed") is True
        and map22_stat.get("passed") is True
        and int(map22_cpp.get("mismatches", -1)) == 0
        and int(map22_cpp.get("skipped_events", -1)) == 0
        and int(map22_cpp.get("python_replay_errors", -1)) == 0
        and map22.get("replay_passed") == map22.get("replay_count"),
        {
            "rows": map22_rows,
            "same_deck_rows": map22_same_rows,
            "strategy_count": map22.get("strategy_count"),
            "promotion_passed": map22_promo.get("passed"),
            "stat_passed": map22_stat.get("passed"),
            "cpp": {k: map22_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
        },
    )


    # rev0023: non-linear public ranker and mulligan policy gate.
    mlp_model_path = ROOT / "data" / "rev0023_mlp_ranker_model.json"
    mlp_summary = load_json(ROOT / "data" / "rev0023_mlp_ranker_summary.json")
    if mlp_model_path.exists():
        mlp_model = load_mlp_ranker_model(mlp_model_path)
        mlp_feature_match = len(mlp_model.feature_names) == len(action_ranker_feature_names())
        from src.muc5.engine import start_game as _rev23_start_game
        rev23_state = _rev23_start_game(seed, seed, seed=232323, record_log=False)
        rev23_frame = build_decision_frame(rev23_state)
        rev23_idx = MLPActionRankerAgent(mlp_model).choose_action_index(rev23_frame, __import__("random").Random(23))
        mlp_agent_legal = 0 <= rev23_idx < rev23_frame.action_count
    else:
        mlp_model = None
        mlp_feature_match = False
        mlp_agent_legal = False
    mlp_cpp = mlp_summary.get("cpp_trace_summary", {})
    mlp_train = mlp_summary.get("training_metrics", {})
    mlp_promo = mlp_summary.get("promotion_gate", {})
    mlp_stat = mlp_summary.get("statistical_gate", {})
    add(
        checks,
        "rev0023_mlp_ranker_model_and_gates",
        mlp_model_path.exists()
        and mlp_feature_match
        and mlp_agent_legal
        and mlp_summary.get("games") == 256
        and mlp_promo.get("passed") is True
        and mlp_stat.get("passed") is True
        and mlp_cpp.get("mismatches") == 0
        and mlp_cpp.get("skipped_events") == 0
        and mlp_cpp.get("python_replay_errors") == 0
        and float(mlp_train.get("test_top1_accuracy", 0.0)) > float(mlp_train.get("random_slot_baseline_accuracy", 1.0)),
        {
            "model_exists": mlp_model_path.exists(),
            "feature_match": mlp_feature_match,
            "agent_legal": mlp_agent_legal,
            "games": mlp_summary.get("games"),
            "top1": mlp_train.get("test_top1_accuracy"),
            "random_baseline": mlp_train.get("random_slot_baseline_accuracy"),
            "promotion_passed": mlp_promo.get("passed"),
            "stat_passed": mlp_stat.get("passed"),
            "cpp": {k: mlp_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
        },
    )
    mlp_bundles = mlp_ranker_probe_bundles(ROOT / "data" / "seed_decks.json")
    add(
        checks,
        "rev0023_mlp_strategy_population",
        len(mlp_bundles) == 8 and any(b.agent_name == "mlp_ranker_rev0023" for b in mlp_bundles),
        {"bundle_count": len(mlp_bundles), "agents": sorted({b.agent_name for b in mlp_bundles})},
    )

    mull_gate_summary = load_json(ROOT / "data" / "rev0023_mulligan_policy_gate_summary.json")
    mull_gate_cpp = mull_gate_summary.get("cpp_trace_summary", {})
    mull_gate_promo = mull_gate_summary.get("promotion_gate", {})
    mull_gate_stat = mull_gate_summary.get("statistical_gate", {})
    mull_gate_bundles = mulligan_policy_gate_bundles(ROOT / "data" / "seed_decks.json")
    add(
        checks,
        "rev0023_mulligan_policy_gate",
        len(mull_gate_bundles) == 9
        and set(mull_gate_summary.get("mulligan_policies", [])) == set(MULLIGAN_POLICY_NAMES)
        and mull_gate_summary.get("games") == 324
        and mull_gate_promo.get("passed") is True
        and mull_gate_stat.get("passed") is True
        and mull_gate_cpp.get("mismatches") == 0
        and mull_gate_cpp.get("skipped_events") == 0
        and mull_gate_cpp.get("python_replay_errors") == 0,
        {
            "bundle_count": len(mull_gate_bundles),
            "policies": mull_gate_summary.get("mulligan_policies"),
            "games": mull_gate_summary.get("games"),
            "promotion_passed": mull_gate_promo.get("passed"),
            "stat_passed": mull_gate_stat.get("passed"),
            "cpp": {k: mull_gate_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
        },
    )



    # rev0024: learned mulligan ranker over explicit pregame legal actions.
    mull_rank_model_path = ROOT / "data" / "rev0024_mulligan_ranker_model.json"
    mull_rank_summary = load_json(ROOT / "data" / "rev0024_learned_mulligan_summary.json")
    if mull_rank_model_path.exists():
        mull_rank_model = load_mulligan_ranker_model(mull_rank_model_path)
        mull_rank_feature_match = len(mull_rank_model.feature_names) == len(mulligan_ranker_feature_names())
        from src.muc5.mulligan import MulliganObservation, MULLIGAN_KEEP, MULLIGAN_TAKE
        test_obs = MulliganObservation(
            player=0,
            stage="keep_or_mulligan",
            mulligans_taken=0,
            hand={"Island": 3, "JaceTheMindSculptor": 1, "Counterspell": 2, "ForceOfWill": 1},
            hand_size=7,
            library_count=33,
            starting_life=20,
            deck_counts={"Island": 24, "Counterspell": 6, "ForceOfWill": 4, "JaceTheMindSculptor": 3, "OverlordOfTheFloodpits": 3},
        )
        mull_rank_agent = LinearMulliganRankerAgent(mull_rank_model)
        mull_rank_action = mull_rank_agent.choose_mulligan_action(test_obs, [MULLIGAN_KEEP, MULLIGAN_TAKE], __import__("random").Random(24))
        mull_rank_agent_legal = mull_rank_action in [MULLIGAN_KEEP, MULLIGAN_TAKE]
    else:
        mull_rank_feature_match = False
        mull_rank_agent_legal = False
    learned_cpp = mull_rank_summary.get("cpp_trace_summary", {})
    learned_promo = mull_rank_summary.get("promotion_gate", {})
    learned_stat = mull_rank_summary.get("statistical_gate", {})
    learned_train = mull_rank_summary.get("training_metrics", {})
    learned_bundles = learned_mulligan_gate_bundles(ROOT / "data" / "seed_decks.json")
    add(
        checks,
        "rev0024_learned_mulligan_ranker_and_gate",
        mull_rank_model_path.exists()
        and mull_rank_feature_match
        and mull_rank_agent_legal
        and len(learned_bundles) == 12
        and MODEL_NAME in set(mull_rank_summary.get("mulligan_policies", []))
        and mull_rank_summary.get("games") == 576
        and learned_promo.get("passed") is True
        and learned_stat.get("passed") is True
        and learned_cpp.get("mismatches") == 0
        and learned_cpp.get("skipped_events") == 0
        and learned_cpp.get("python_replay_errors") == 0
        and float(learned_train.get("keep_accuracy", 0.0)) > 0.85
        and float(learned_train.get("bottom_top1_accuracy", 0.0)) > float(learned_train.get("bottom_random_slot_baseline_accuracy", 1.0)),
        {
            "model_exists": mull_rank_model_path.exists(),
            "feature_match": mull_rank_feature_match,
            "agent_legal": mull_rank_agent_legal,
            "bundle_count": len(learned_bundles),
            "policies": mull_rank_summary.get("mulligan_policies"),
            "games": mull_rank_summary.get("games"),
            "keep_accuracy": learned_train.get("keep_accuracy"),
            "bottom_top1_accuracy": learned_train.get("bottom_top1_accuracy"),
            "bottom_random_baseline": learned_train.get("bottom_random_slot_baseline_accuracy"),
            "promotion_passed": learned_promo.get("passed"),
            "stat_passed": learned_stat.get("passed"),
            "cpp": {k: learned_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
        },
    )


    # rev0025: outcome-weighted public gameplay action ranker.
    outcome_model_path = ROOT / "data" / "rev0025_outcome_ranker_model.json"
    outcome_summary = load_json(ROOT / "data" / "rev0025_outcome_ranker_summary.json")
    outcome_train_rows_path = ROOT / "data" / "rev0025_outcome_ranker_training_dataset.csv"
    outcome_train_rows = list(csv.DictReader(outcome_train_rows_path.open())) if outcome_train_rows_path.exists() else []
    if outcome_model_path.exists():
        outcome_model = load_linear_ranker_model(outcome_model_path)
        outcome_feature_match = len(outcome_model.feature_names) == len(action_ranker_feature_names())
        test_state = __import__("src.muc5.engine", fromlist=["start_game"]).start_game(seed, seed, seed=252525, record_log=False)
        test_frame = build_decision_frame(test_state)
        test_agent = make_public_agent("outcome_linear_ranker_rev0025")
        outcome_agent_legal = 0 <= test_agent.choose_action_index(test_frame, __import__("random").Random(25)) < test_frame.action_count
    else:
        outcome_feature_match = False
        outcome_agent_legal = False
    outcome_cpp = outcome_summary.get("cpp_trace_summary", {})
    outcome_promo = outcome_summary.get("promotion_gate", {})
    outcome_stat = outcome_summary.get("statistical_gate", {})
    outcome_train = outcome_summary.get("training_metrics", {})
    outcome_collection = outcome_summary.get("collection", {})
    outcome_bundles = outcome_ranker_probe_bundles(ROOT / "data" / "seed_decks.json")
    zero_weighted_truncations = all(
        not (str(r.get("terminal")) in {"0", "False", "false"} and float(r.get("outcome_weight", 0.0)) > 0.0)
        for r in outcome_train_rows[: min(len(outcome_train_rows), 5000)]
    )
    add(
        checks,
        "rev0025_outcome_ranker_and_gate",
        outcome_model_path.exists()
        and outcome_feature_match
        and outcome_agent_legal
        and len(outcome_bundles) == 8
        and outcome_summary.get("games") == 256
        and outcome_summary.get("aggregate_rows") == 128
        and outcome_collection.get("games") == 112
        and outcome_collection.get("truncated_games") == 0
        and count_csv_rows(outcome_train_rows_path) == outcome_collection.get("rows")
        and zero_weighted_truncations
        and outcome_promo.get("passed") is True
        and outcome_stat.get("passed") is True
        and outcome_cpp.get("mismatches") == 0
        and outcome_cpp.get("skipped_events") == 0
        and outcome_cpp.get("python_replay_errors") == 0
        and float(outcome_train.get("test_top1_accuracy", 0.0)) > float(outcome_train.get("random_slot_baseline_accuracy", 1.0)),
        {
            "model_exists": outcome_model_path.exists(),
            "feature_match": outcome_feature_match,
            "agent_legal": outcome_agent_legal,
            "bundle_count": len(outcome_bundles),
            "games": outcome_summary.get("games"),
            "training_rows": outcome_collection.get("rows"),
            "training_games": outcome_collection.get("games"),
            "truncated_training_games": outcome_collection.get("truncated_games"),
            "zero_weighted_truncations_sample": zero_weighted_truncations,
            "test_top1": outcome_train.get("test_top1_accuracy"),
            "random_baseline": outcome_train.get("random_slot_baseline_accuracy"),
            "promotion_passed": outcome_promo.get("passed"),
            "stat_passed": outcome_stat.get("passed"),
            "cpp": {k: outcome_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
        },
    )

    # rev0026: split RNG and C++ shadow rollout seam.
    shadow_summary_path = ROOT / "data" / "rev0026_cpp_shadow_rollout_summary.json"
    shadow_summary = load_json(shadow_summary_path)
    shadow_cpp = shadow_summary.get("cpp_shadow_summary", {})
    shadow_promo = shadow_summary.get("promotion_gate", {})
    shadow_stat = shadow_summary.get("statistical_gate", {})
    shadow_games_path = ROOT / "data" / "rev0026_cpp_shadow_rollout_games.csv"
    shadow_transitions_path = ROOT / "data" / "rev0026_cpp_shadow_rollout_transitions.csv"
    shadow_games = count_csv_rows(shadow_games_path) if shadow_games_path.exists() else -1
    shadow_transitions = count_csv_rows(shadow_transitions_path) if shadow_transitions_path.exists() else -1
    rng_contract = shadow_summary.get("rng_contract", {})
    add(
        checks,
        "rev0026_cpp_shadow_rollout_and_rng_split",
        shadow_summary_path.exists()
        and shadow_games == 144
        and shadow_summary.get("games") == 144
        and shadow_summary.get("strategy_count") == 6
        and shadow_transitions == shadow_cpp.get("events")
        and shadow_cpp.get("events", 0) >= 40000
        and shadow_cpp.get("supported_events") == shadow_cpp.get("events")
        and shadow_cpp.get("skipped_events") == 0
        and shadow_cpp.get("mismatches") == 0
        and shadow_cpp.get("python_errors") == 0
        and shadow_summary.get("replay_count") == 8
        and shadow_summary.get("replay_passed") == 8
        and shadow_promo.get("passed") is True
        and shadow_stat.get("passed") is True
        and rng_contract.get("transition_seed") == "seed"
        and rng_contract.get("agent_seed") == "seed+1000003"
        and rng_contract.get("public_payoff_split_rng") is True,
        {
            "summary_exists": shadow_summary_path.exists(),
            "games": shadow_games,
            "strategy_count": shadow_summary.get("strategy_count"),
            "transition_rows": shadow_transitions,
            "cpp": {k: shadow_cpp.get(k) for k in ("events", "supported_events", "skipped_events", "mismatches", "python_errors", "truncations")},
            "replay_count": shadow_summary.get("replay_count"),
            "replay_passed": shadow_summary.get("replay_passed"),
            "promotion_passed": shadow_promo.get("passed"),
            "stat_passed": shadow_stat.get("passed"),
            "rng_contract": rng_contract,
        },
    )


    # rev0027: outcome-weighted mulligan learning and cached mulligan agents.
    mull_outcome_summary_path = ROOT / "data" / "rev0027_mulligan_outcome_summary.json"
    mull_outcome_summary = load_json(mull_outcome_summary_path)
    mull_outcome_model_path = model_path_for_name(OUTCOME_MODEL_NAME)
    if mull_outcome_model_path.exists():
        mull_outcome_model = load_mulligan_ranker_model(mull_outcome_model_path)
        mull_outcome_feature_match = len(mull_outcome_model.feature_names) == len(mulligan_ranker_feature_names())
        mull_outcome_agent = make_mulligan_agent(OUTCOME_MODEL_NAME)
        mull_outcome_agent_name = getattr(mull_outcome_agent, "name", "")
    else:
        mull_outcome_feature_match = False
        mull_outcome_agent_name = "missing"
    mull_outcome_bundles = mulligan_outcome_gate_bundles(ROOT / "data" / "seed_decks.json") if mull_outcome_model_path.exists() else []
    mull_outcome_keep_rows = count_csv_rows(ROOT / "data" / "rev0027_mulligan_outcome_keep_training.csv") if (ROOT / "data" / "rev0027_mulligan_outcome_keep_training.csv").exists() else -1
    mull_outcome_bottom_rows = count_csv_rows(ROOT / "data" / "rev0027_mulligan_outcome_bottom_training.csv") if (ROOT / "data" / "rev0027_mulligan_outcome_bottom_training.csv").exists() else -1
    mull_outcome_games_rows = count_csv_rows(ROOT / "data" / "rev0027_mulligan_outcome_games.csv") if (ROOT / "data" / "rev0027_mulligan_outcome_games.csv").exists() else -1
    mull_outcome_collection = mull_outcome_summary.get("collection", {})
    mull_outcome_training = mull_outcome_summary.get("training_metrics", {})
    mull_outcome_promo = mull_outcome_summary.get("promotion_gate", {})
    mull_outcome_stat = mull_outcome_summary.get("statistical_gate", {})
    mull_outcome_cpp = mull_outcome_summary.get("cpp_trace_summary", {})
    add(
        checks,
        "rev0027_mulligan_outcome_ranker_and_cache",
        mull_outcome_summary_path.exists()
        and mull_outcome_model_path.exists()
        and mull_outcome_feature_match
        and mull_outcome_agent_name == OUTCOME_MODEL_NAME
        and len(mull_outcome_bundles) == 15
        and OUTCOME_MODEL_NAME in {str(b.mulligan_policy) for b in mull_outcome_bundles}
        and mull_outcome_keep_rows == mull_outcome_collection.get("keep_rows")
        and mull_outcome_bottom_rows == mull_outcome_collection.get("bottom_rows")
        and mull_outcome_collection.get("games") == 288
        and mull_outcome_collection.get("truncated_games") == 0
        and mull_outcome_games_rows == 900
        and mull_outcome_summary.get("games") == 900
        and mull_outcome_summary.get("aggregate_rows") == 450
        and mull_outcome_summary.get("replay_count") == 8
        and mull_outcome_summary.get("replay_passed") == 8
        and mull_outcome_promo.get("passed") is True
        and mull_outcome_stat.get("passed") is True
        and mull_outcome_cpp.get("mismatches") == 0
        and mull_outcome_cpp.get("skipped_events") == 0
        and mull_outcome_cpp.get("python_replay_errors") == 0
        and float(mull_outcome_training.get("bottom_top1_accuracy", 0.0)) > float(mull_outcome_training.get("bottom_random_slot_baseline_accuracy", 1.0))
        and mull_outcome_summary.get("public_payoff_refactor", {}).get("mulligan_agent_cache") is True,
        {
            "summary_exists": mull_outcome_summary_path.exists(),
            "model_exists": mull_outcome_model_path.exists(),
            "feature_match": mull_outcome_feature_match,
            "agent_name": mull_outcome_agent_name,
            "bundle_count": len(mull_outcome_bundles),
            "training_games": mull_outcome_collection.get("games"),
            "decision_events": mull_outcome_collection.get("decision_events"),
            "keep_rows": mull_outcome_keep_rows,
            "bottom_rows": mull_outcome_bottom_rows,
            "payoff_games": mull_outcome_games_rows,
            "keep_accuracy": mull_outcome_training.get("keep_accuracy"),
            "bottom_top1": mull_outcome_training.get("bottom_top1_accuracy"),
            "bottom_random": mull_outcome_training.get("bottom_random_slot_baseline_accuracy"),
            "promotion_passed": mull_outcome_promo.get("passed"),
            "stat_passed": mull_outcome_stat.get("passed"),
            "cpp": {k: mull_outcome_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
            "cache_refactor": mull_outcome_summary.get("public_payoff_refactor"),
        },
    )


    # rev0028: opening-hand keep-vs-mulligan counterfactuals.
    cf_summary_path = ROOT / "data" / "rev0028_opening_counterfactual_summary.json"
    cf_summary = load_json(cf_summary_path)
    cf_branch_rows = count_csv_rows(ROOT / "data" / "rev0028_opening_counterfactual_branch_games.csv") if (ROOT / "data" / "rev0028_opening_counterfactual_branch_games.csv").exists() else -1
    cf_pair_rows = count_csv_rows(ROOT / "data" / "rev0028_opening_counterfactual_pairs.csv") if (ROOT / "data" / "rev0028_opening_counterfactual_pairs.csv").exists() else -1
    cf_context_rows = count_csv_rows(ROOT / "data" / "rev0028_opening_counterfactual_context_summary.csv") if (ROOT / "data" / "rev0028_opening_counterfactual_context_summary.csv").exists() else -1
    cf_transition_rows = count_csv_rows_or_catalog(ROOT / "data" / "rev0028_opening_counterfactual_cpp_transitions.csv")
    add(
        checks,
        "rev0028_opening_counterfactual_panel",
        cf_summary_path.exists()
        and cf_branch_rows == 144
        and cf_pair_rows == 72
        and cf_context_rows >= 12
        and cf_transition_rows == cf_summary.get("transition_events")
        and cf_summary.get("branch_games") == 144
        and cf_summary.get("paired_rows") == 72
        and cf_summary.get("specs") == 72
        and cf_summary.get("skipped_cpp_events") == 0
        and cf_summary.get("cpp_mismatches") == 0
        and cf_summary.get("supported_cpp_events") == cf_summary.get("transition_events")
        and cf_summary.get("truncations") == 0
        and (cf_summary.get("keep_better_pairs", 0) + cf_summary.get("mulligan_better_pairs", 0) + cf_summary.get("tie_pairs", 0)) == 72,
        {
            "summary_exists": cf_summary_path.exists(),
            "branch_rows": cf_branch_rows,
            "pair_rows": cf_pair_rows,
            "context_rows": cf_context_rows,
            "transition_rows": cf_transition_rows,
            "summary": {k: cf_summary.get(k) for k in ("branch_games", "paired_rows", "transition_events", "supported_cpp_events", "skipped_cpp_events", "cpp_mismatches", "truncations", "mean_mulligan_minus_keep", "keep_better_pairs", "mulligan_better_pairs", "tie_pairs")},
        },
    )


    # rev0029: first-look counterfactual mulligan ranker and no-choice segment audit.
    cfm_summary_path = ROOT / "data" / "rev0029_counterfactual_mulligan_summary.json"
    cfm_summary = load_json(cfm_summary_path)
    cfm_model_path = ROOT / "data" / "rev0029_counterfactual_mulligan_model.json"
    cfm_train_rows = count_csv_rows(ROOT / "data" / "rev0029_counterfactual_mulligan_training_rows.csv") if (ROOT / "data" / "rev0029_counterfactual_mulligan_training_rows.csv").exists() else -1
    cfm_games_rows = count_csv_rows(ROOT / "data" / "rev0029_counterfactual_mulligan_games.csv") if (ROOT / "data" / "rev0029_counterfactual_mulligan_games.csv").exists() else -1
    cfm_same_shell_rows = count_csv_rows(ROOT / "data" / "rev0029_counterfactual_mulligan_same_shell.csv") if (ROOT / "data" / "rev0029_counterfactual_mulligan_same_shell.csv").exists() else -1
    cfm_nochoice_rows = count_csv_rows(ROOT / "data" / "rev0029_nochoice_segment_audit.csv") if (ROOT / "data" / "rev0029_nochoice_segment_audit.csv").exists() else -1
    cfm_nochoice = load_json(ROOT / "data" / "rev0029_nochoice_segment_summary.json")
    try:
        cfm_model = load_counterfactual_mulligan_model(cfm_model_path)
        cfm_model_loaded = True
        cfm_feature_count = len(cfm_model.feature_names)
    except Exception as exc:
        cfm_model_loaded = False
        cfm_feature_count = -1
    try:
        cfm_agent_name = make_mulligan_agent(COUNTERFACTUAL_MODEL_NAME).name
    except Exception as exc:
        cfm_agent_name = f"ERROR:{exc}"
    cfm_bundles = counterfactual_mulligan_gate_bundles(ROOT / "data" / "seed_decks.json")
    cfm_training = cfm_summary.get("training_metrics", {})
    cfm_promo = cfm_summary.get("promotion_gate", {})
    cfm_stat = cfm_summary.get("statistical_gate", {})
    cfm_cpp = cfm_summary.get("cpp_trace_summary", {})
    add(
        checks,
        "rev0029_counterfactual_mulligan_and_nochoice_segments",
        cfm_summary_path.exists()
        and cfm_model_path.exists()
        and cfm_model_loaded
        and cfm_feature_count == len(mulligan_ranker_feature_names())
        and cfm_agent_name == COUNTERFACTUAL_MODEL_NAME
        and len(cfm_bundles) == 18
        and COUNTERFACTUAL_MODEL_NAME in {str(b.mulligan_policy) for b in cfm_bundles}
        and cfm_train_rows == 72
        and cfm_training.get("rows") == 72
        and cfm_training.get("tie_rows") == 39
        and cfm_games_rows == 432
        and cfm_same_shell_rows == 18
        and cfm_summary.get("games") == 432
        and cfm_summary.get("aggregate_rows") == 216
        and cfm_summary.get("replay_count") == 8
        and cfm_summary.get("replay_passed") == 8
        and cfm_promo.get("passed") is True
        and cfm_stat.get("passed") is True
        and cfm_cpp.get("mismatches") == 0
        and cfm_cpp.get("skipped_events") == 0
        and cfm_cpp.get("python_replay_errors") == 0
        and cfm_nochoice_rows == cfm_nochoice.get("games")
        and cfm_nochoice.get("games") == 24
        and cfm_nochoice.get("forced_frames", 0) > 0
        and cfm_nochoice.get("estimated_compression_ratio", 0) > 1.0,
        {
            "summary_exists": cfm_summary_path.exists(),
            "model_exists": cfm_model_path.exists(),
            "model_loaded": cfm_model_loaded,
            "agent_name": cfm_agent_name,
            "bundle_count": len(cfm_bundles),
            "training_rows": cfm_train_rows,
            "payoff_games": cfm_games_rows,
            "same_shell_rows": cfm_same_shell_rows,
            "training_metrics": {k: cfm_training.get(k) for k in ("rows", "keep_better_rows", "mulligan_better_rows", "tie_rows", "test_decision_accuracy_ties_count_as_correct", "test_non_tie_sign_accuracy")},
            "promotion_passed": cfm_promo.get("passed"),
            "stat_passed": cfm_stat.get("passed"),
            "cpp": {k: cfm_cpp.get(k) for k in ("events", "skipped_events", "mismatches", "python_replay_errors")},
            "nochoice": {k: cfm_nochoice.get(k) for k in ("games", "decisions", "forced_frames", "forced_runs", "estimated_compression_ratio", "truncations")},
        },
    )




    # rev0030: repeated opening-hand counterfactuals and no-choice segment fingerprints.
    rep_cf_summary = load_json(ROOT / "data" / "rev0030_repeated_opening_counterfactual_summary.json")
    rep_branch_rows = count_csv_rows(ROOT / "data" / "rev0030_repeated_opening_counterfactual_branch_games.csv") if (ROOT / "data" / "rev0030_repeated_opening_counterfactual_branch_games.csv").exists() else -1
    rep_pair_rows = count_csv_rows(ROOT / "data" / "rev0030_repeated_opening_counterfactual_pairs.csv") if (ROOT / "data" / "rev0030_repeated_opening_counterfactual_pairs.csv").exists() else -1
    rep_trans_rows = count_csv_rows_or_catalog(ROOT / "data" / "rev0030_repeated_opening_counterfactual_cpp_transitions.csv")
    add(
        checks,
        "rev0030_repeated_opening_counterfactual_panel",
        rep_cf_summary.get("paired_rows", 0) >= 20
        and rep_cf_summary.get("rollout_reps") == 2
        and rep_branch_rows == rep_cf_summary.get("branch_games")
        and rep_pair_rows == rep_cf_summary.get("paired_rows")
        and rep_trans_rows == rep_cf_summary.get("transition_events")
        and rep_cf_summary.get("skipped_cpp_events") == 0
        and rep_cf_summary.get("cpp_mismatches") == 0,
        {
            "paired_rows": rep_cf_summary.get("paired_rows"),
            "branch_games": rep_cf_summary.get("branch_games"),
            "rollout_reps": rep_cf_summary.get("rollout_reps"),
            "transition_events": rep_cf_summary.get("transition_events"),
            "skipped_cpp_events": rep_cf_summary.get("skipped_cpp_events"),
            "cpp_mismatches": rep_cf_summary.get("cpp_mismatches"),
            "csv_rows": {"branch": rep_branch_rows, "pairs": rep_pair_rows, "transitions": rep_trans_rows},
        },
    )

    repeat_summary = load_json(ROOT / "data" / "rev0030_repeated_counterfactual_mulligan_summary.json")
    repeat_games = count_csv_rows(ROOT / "data" / "rev0030_repeated_counterfactual_mulligan_games.csv") if (ROOT / "data" / "rev0030_repeated_counterfactual_mulligan_games.csv").exists() else -1
    repeat_same_shell = count_csv_rows(ROOT / "data" / "rev0030_repeated_counterfactual_mulligan_same_shell.csv") if (ROOT / "data" / "rev0030_repeated_counterfactual_mulligan_same_shell.csv").exists() else -1
    repeat_model_path = ROOT / "data" / "rev0030_repeated_counterfactual_mulligan_model.json"
    try:
        repeat_agent = load_repeated_counterfactual_mulligan_agent(repeat_model_path)
        repeat_agent_name = repeat_agent.name
    except Exception as exc:  # pragma: no cover - audit diagnostic
        repeat_agent_name = f"ERROR:{type(exc).__name__}:{exc}"
    add(
        checks,
        "rev0030_repeated_counterfactual_mulligan_gate",
        repeat_games == repeat_summary.get("games")
        and repeat_summary.get("promotion_gate", {}).get("passed") is True
        and repeat_summary.get("statistical_gate", {}).get("passed") is True
        and repeat_summary.get("cpp_trace_summary", {}).get("skipped_events") == 0
        and repeat_summary.get("cpp_trace_summary", {}).get("mismatches") == 0
        and repeat_summary.get("replay_passed") == repeat_summary.get("replay_count")
        and repeat_same_shell >= 21
        and repeat_model_path.exists()
        and repeat_agent_name == "mulligan_repeated_counterfactual_ranker_rev0030",
        {
            "games": repeat_games,
            "summary_games": repeat_summary.get("games"),
            "same_shell_rows": repeat_same_shell,
            "promotion": repeat_summary.get("promotion_gate", {}).get("passed"),
            "statistical": repeat_summary.get("statistical_gate", {}).get("passed"),
            "cpp": repeat_summary.get("cpp_trace_summary"),
            "replays": [repeat_summary.get("replay_passed"), repeat_summary.get("replay_count")],
            "agent_name": repeat_agent_name,
        },
    )

    seg_summary = load_json(ROOT / "data" / "rev0030_nochoice_segment_fingerprint_summary.json")
    seg_rows = count_csv_rows(ROOT / "data" / "rev0030_nochoice_segment_fingerprints.csv") if (ROOT / "data" / "rev0030_nochoice_segment_fingerprints.csv").exists() else -1
    seg_game_rows = count_csv_rows(ROOT / "data" / "rev0030_nochoice_segment_games.csv") if (ROOT / "data" / "rev0030_nochoice_segment_games.csv").exists() else -1
    add(
        checks,
        "rev0030_nochoice_segment_fingerprints",
        seg_summary.get("games", 0) >= 20
        and seg_rows == seg_summary.get("segments")
        and seg_game_rows == seg_summary.get("games")
        and seg_summary.get("segments", 0) > 0
        and seg_summary.get("total_forced_actions", 0) >= seg_summary.get("segments", 0)
        and seg_summary.get("truncations") == 0,
        {
            "games": seg_summary.get("games"),
            "segments": seg_summary.get("segments"),
            "segment_rows": seg_rows,
            "game_rows": seg_game_rows,
            "total_forced_actions": seg_summary.get("total_forced_actions"),
            "compression": seg_summary.get("estimated_decision_compression_ratio"),
            "truncations": seg_summary.get("truncations"),
        },
    )



    # rev0031: C++ no-choice segment checker and scaled repeated counterfactual label budget.
    seg31_summary = load_json(ROOT / "data" / "rev0031_cpp_segment_summary.json")
    seg31_games = count_csv_rows(ROOT / "data" / "rev0031_cpp_segment_games.csv") if (ROOT / "data" / "rev0031_cpp_segment_games.csv").exists() else -1
    seg31_rows = count_csv_rows(ROOT / "data" / "rev0031_cpp_segment_rows.csv") if (ROOT / "data" / "rev0031_cpp_segment_rows.csv").exists() else -1
    seg31_status = cpp_segment_tool_status(try_build=True).as_dict()
    add(
        checks,
        "rev0031_cpp_nochoice_segment_checker",
        bool(seg31_status.get("usable"))
        and seg31_summary.get("games", 0) >= 40
        and seg31_games == seg31_summary.get("games")
        and seg31_rows == seg31_summary.get("segments")
        and seg31_summary.get("checked_segments") == seg31_summary.get("segments")
        and seg31_summary.get("forced_actions", 0) >= seg31_summary.get("segments", 0)
        and seg31_summary.get("skipped_events") == 0
        and seg31_summary.get("cpp_segment_mismatches") == 0
        and seg31_summary.get("cpp_match_rate_on_checked_segments") == 1.0
        and seg31_summary.get("estimated_decision_compression_ratio", 0) > 1.0
        and seg31_summary.get("truncations") == 0,
        {
            "tool_status": seg31_status,
            "games": seg31_summary.get("games"),
            "game_rows": seg31_games,
            "segments": seg31_summary.get("segments"),
            "segment_rows": seg31_rows,
            "checked_segments": seg31_summary.get("checked_segments"),
            "forced_actions": seg31_summary.get("forced_actions"),
            "skipped_events": seg31_summary.get("skipped_events"),
            "mismatches": seg31_summary.get("cpp_segment_mismatches"),
            "compression": seg31_summary.get("estimated_decision_compression_ratio"),
            "max_segment_length": seg31_summary.get("max_segment_length"),
            "truncations": seg31_summary.get("truncations"),
        },
    )

    cf31_summary = load_json(ROOT / "data" / "rev0031_repeated_cf_scale_summary.json")
    cf31_branch = count_csv_rows(ROOT / "data" / "rev0031_repeated_cf_scale_branch_games.csv") if (ROOT / "data" / "rev0031_repeated_cf_scale_branch_games.csv").exists() else -1
    cf31_pairs = count_csv_rows(ROOT / "data" / "rev0031_repeated_cf_scale_pairs.csv") if (ROOT / "data" / "rev0031_repeated_cf_scale_pairs.csv").exists() else -1
    cf31_trans = count_csv_rows_or_catalog(ROOT / "data" / "rev0031_repeated_cf_scale_cpp_transitions.csv")
    add(
        checks,
        "rev0031_repeated_counterfactual_scale_probe",
        cf31_summary.get("paired_rows", 0) >= 36
        and cf31_summary.get("rollout_reps") == 3
        and cf31_branch == cf31_summary.get("branch_games")
        and cf31_pairs == cf31_summary.get("paired_rows")
        and cf31_trans == cf31_summary.get("transition_events")
        and cf31_summary.get("skipped_cpp_events") == 0
        and cf31_summary.get("cpp_mismatches") == 0
        and cf31_summary.get("truncations") == 0,
        {
            "paired_rows": cf31_summary.get("paired_rows"),
            "branch_games": cf31_summary.get("branch_games"),
            "rollout_reps": cf31_summary.get("rollout_reps"),
            "non_tie_pairs": cf31_summary.get("non_tie_pairs"),
            "confident_pairs": cf31_summary.get("confident_abs_delta_ge_025_pairs"),
            "transition_events": cf31_summary.get("transition_events"),
            "skipped_cpp_events": cf31_summary.get("skipped_cpp_events"),
            "cpp_mismatches": cf31_summary.get("cpp_mismatches"),
            "csv_rows": {"branch": cf31_branch, "pairs": cf31_pairs, "transitions": cf31_trans},
        },
    )


    # rev0032: batched C++ no-choice segment shadow payoff over MAP-Elites variants.
    seg32_summary = load_json(ROOT / "data" / "rev0032_segment_shadow_summary.json")
    seg32_games = count_csv_rows(ROOT / "data" / "rev0032_segment_shadow_games.csv") if (ROOT / "data" / "rev0032_segment_shadow_games.csv").exists() else -1
    seg32_segments = count_csv_rows_or_catalog(ROOT / "data" / "rev0032_segment_shadow_segments.csv")
    seg32_same_deck = count_csv_rows(ROOT / "data" / "rev0032_segment_shadow_same_deck.csv") if (ROOT / "data" / "rev0032_segment_shadow_same_deck.csv").exists() else -1
    seg32_gate = seg32_summary.get("promotion_gate", {})
    seg32_stat = seg32_summary.get("statistical_gate", {})
    seg32_seg_payload = seg32_summary.get("segment_summary", {})
    add(
        checks,
        "rev0032_batched_segment_shadow_maprace",
        seg32_summary.get("revision") == "rev0032"
        and seg32_games == seg32_summary.get("games")
        and seg32_games >= 96
        and seg32_segments == seg32_summary.get("segments")
        and seg32_same_deck == seg32_summary.get("strategy_count")
        and seg32_summary.get("batch_cpp_invocations") == 1
        and seg32_summary.get("cpp_segment_mismatches") == 0
        and seg32_summary.get("cpp_skipped_events") == 0
        and seg32_summary.get("truncations") == 0
        and seg32_summary.get("replay_passed") == seg32_summary.get("replay_samples")
        and seg32_summary.get("replay_samples", 0) >= 6
        and seg32_gate.get("passed") is True
        and seg32_stat.get("passed") is True
        and seg32_seg_payload.get("estimated_decision_compression_ratio", 0) > 1.0,
        {
            "games": seg32_games,
            "segments": seg32_segments,
            "same_deck_rows": seg32_same_deck,
            "strategy_count": seg32_summary.get("strategy_count"),
            "batch_cpp_invocations": seg32_summary.get("batch_cpp_invocations"),
            "mismatches": seg32_summary.get("cpp_segment_mismatches"),
            "skipped": seg32_summary.get("cpp_skipped_events"),
            "truncations": seg32_summary.get("truncations"),
            "replay": [seg32_summary.get("replay_passed"), seg32_summary.get("replay_samples")],
            "promotion_passed": seg32_gate.get("passed"),
            "statistical_passed": seg32_stat.get("passed"),
            "compression": seg32_seg_payload.get("estimated_decision_compression_ratio"),
        },
    )



    # rev0033: gameplay action counterfactuals and C++ combat sentinel fix.
    rev0033_summary = load_json(ROOT / "data" / "rev0033_action_counterfactual_summary.json")
    cf_coll = rev0033_summary.get("counterfactual_collection", {})
    cf_cpp = rev0033_summary.get("cpp_shadow_summary", {})
    add(checks, "rev0033_action_counterfactual_collection",
        cf_coll.get("sampled_situations", 0) >= 18
        and cf_coll.get("candidate_actions", 0) >= 40
        and cf_coll.get("branch_games", 0) >= 90
        and cf_coll.get("cpp_checked_transitions", 0) >= 19000
        and cf_coll.get("cpp_skipped_transitions") == 0
        and cf_coll.get("cpp_mismatches") == 0,
        {"collection": cf_coll})
    model_path = ROOT / "data" / "rev0033_counterfactual_action_ranker_model.json"
    model_ok = False
    model_details = {"exists": model_path.exists()}
    if model_path.exists():
        try:
            m = load_linear_ranker_model(model_path)
            model_ok = (m.model_id == "counterfactual_linear_ranker_rev0033" and len(m.feature_names) == len(action_ranker_feature_names()))
            model_details.update({"model_id": m.model_id, "feature_count": len(m.feature_names)})
        except Exception as exc:
            model_details["error"] = repr(exc)
    add(checks, "rev0033_counterfactual_ranker_model_loads", model_ok, model_details)
    try:
        cf_agent = make_public_agent("counterfactual_linear_ranker_rev0033")
        blended_agent = make_public_agent("counterfactual_ranker_blend_counter_rev0033")
        agent_ok = getattr(cf_agent, "name", "") == "counterfactual_linear_ranker_rev0033" and "counterfactual_ranker_blend" in getattr(blended_agent, "name", "")
    except Exception as exc:
        agent_ok = False
        model_details["agent_error"] = repr(exc)
    add(checks, "rev0033_counterfactual_agents_load", agent_ok, {"details": model_details})
    add(checks, "rev0033_counterfactual_payoff_gates",
        rev0033_summary.get("promotion_gate", {}).get("passed") is True
        and rev0033_summary.get("statistical_gate", {}).get("passed") is True
        and rev0033_summary.get("replay_passed", 0) >= 8
        and cf_cpp.get("mismatches") == 0
        and cf_cpp.get("skipped_events") == 0
        and cf_cpp.get("events", 0) >= 39000,
        {"promotion": rev0033_summary.get("promotion_gate"), "statistical": rev0033_summary.get("statistical_gate"), "cpp": cf_cpp})
    add(checks, "rev0033_required_output_rows",
        count_csv_rows(ROOT / "data" / "rev0033_action_counterfactual_candidates.csv") >= 47
        and count_csv_rows(ROOT / "data" / "rev0033_action_counterfactual_branch_games.csv") >= 94
        and count_csv_rows(ROOT / "data" / "rev0033_counterfactual_ranker_games.csv") >= 144,
        {
            "candidate_rows": count_csv_rows(ROOT / "data" / "rev0033_action_counterfactual_candidates.csv") if (ROOT / "data" / "rev0033_action_counterfactual_candidates.csv").exists() else -1,
            "branch_rows": count_csv_rows(ROOT / "data" / "rev0033_action_counterfactual_branch_games.csv") if (ROOT / "data" / "rev0033_action_counterfactual_branch_games.csv").exists() else -1,
            "game_rows": count_csv_rows(ROOT / "data" / "rev0033_counterfactual_ranker_games.csv") if (ROOT / "data" / "rev0033_counterfactual_ranker_games.csv").exists() else -1,
        })

    # rev0034: scaled gameplay action-counterfactual labels and label-noise diagnostics.
    rev0034_summary = load_json(ROOT / "data" / "rev0034_scaled_action_counterfactual_summary.json")
    cf34_coll = rev0034_summary.get("counterfactual_collection", {})
    cf34_label = rev0034_summary.get("label_audit", {})
    cf34_cpp = rev0034_summary.get("cpp_shadow_summary", {})
    add(checks, "rev0034_scaled_action_counterfactual_collection",
        cf34_coll.get("sampled_situations", 0) >= 24
        and cf34_coll.get("candidate_actions", 0) >= 55
        and cf34_coll.get("branch_games", 0) >= 160
        and cf34_coll.get("branch_rollouts_per_action") == 3
        and cf34_coll.get("cpp_checked_transitions", 0) >= 20000
        and cf34_coll.get("cpp_skipped_transitions") == 0
        and cf34_coll.get("cpp_mismatches") == 0,
        {"collection": cf34_coll})
    add(checks, "rev0034_label_audit_present",
        cf34_label.get("situations", 0) >= 24
        and "mean_label_confidence_proxy" in cf34_label
        and cf34_label.get("decisive_situations", 0) + cf34_label.get("tie_situations", 0) == cf34_label.get("situations", -1),
        {"label_audit": cf34_label})
    model34_path = ROOT / "data" / "rev0034_counterfactual_action_ranker_model.json"
    model34_ok = False
    model34_details = {"exists": model34_path.exists()}
    if model34_path.exists():
        try:
            m34 = load_linear_ranker_model(model34_path)
            model34_ok = (m34.model_id == "counterfactual_linear_ranker_rev0034" and len(m34.feature_names) == len(action_ranker_feature_names()))
            model34_details.update({"model_id": m34.model_id, "feature_count": len(m34.feature_names), "source_revision": m34.source_revision})
        except Exception as exc:
            model34_details["error"] = repr(exc)
    add(checks, "rev0034_counterfactual_ranker_model_loads", model34_ok, model34_details)
    try:
        cf34_agent = make_public_agent("counterfactual_linear_ranker_rev0034")
        cf34_blend = make_public_agent("counterfactual_ranker_blend_counter_rev0034")
        agent34_ok = getattr(cf34_agent, "name", "") == "counterfactual_linear_ranker_rev0034" and getattr(cf34_blend, "name", "").endswith("rev0034")
    except Exception as exc:
        agent34_ok = False
        model34_details["agent_error"] = repr(exc)
    add(checks, "rev0034_counterfactual_agents_load", agent34_ok, {"details": model34_details})
    bundles34 = scaled_counterfactual_action_ranker_bundles(ROOT / "data" / "seed_decks.json")
    add(checks, "rev0034_strategy_panel", len(bundles34) == 8 and any(b.agent_name.endswith("rev0034") for b in bundles34), {"bundle_count": len(bundles34), "agents": sorted({b.agent_name for b in bundles34})})
    add(checks, "rev0034_scaled_counterfactual_payoff_gates",
        rev0034_summary.get("promotion_gate", {}).get("passed") is True
        and rev0034_summary.get("statistical_gate", {}).get("passed") is True
        and rev0034_summary.get("replay_passed", 0) >= 8
        and cf34_cpp.get("mismatches") == 0
        and cf34_cpp.get("skipped_events") == 0
        and cf34_cpp.get("events", 0) >= 20000,
        {"promotion": rev0034_summary.get("promotion_gate"), "statistical": rev0034_summary.get("statistical_gate"), "cpp": cf34_cpp})
    add(checks, "rev0034_required_output_rows",
        count_csv_rows(ROOT / "data" / "rev0034_action_counterfactual_candidates.csv") >= 55
        and count_csv_rows(ROOT / "data" / "rev0034_action_counterfactual_branch_games.csv") >= 160
        and count_csv_rows(ROOT / "data" / "rev0034_scaled_counterfactual_ranker_games.csv") >= 144,
        {
            "candidate_rows": count_csv_rows(ROOT / "data" / "rev0034_action_counterfactual_candidates.csv") if (ROOT / "data" / "rev0034_action_counterfactual_candidates.csv").exists() else -1,
            "branch_rows": count_csv_rows(ROOT / "data" / "rev0034_action_counterfactual_branch_games.csv") if (ROOT / "data" / "rev0034_action_counterfactual_branch_games.csv").exists() else -1,
            "game_rows": count_csv_rows(ROOT / "data" / "rev0034_scaled_counterfactual_ranker_games.csv") if (ROOT / "data" / "rev0034_scaled_counterfactual_ranker_games.csv").exists() else -1,
        })


    # rev0035: budgeted high-branch gameplay action-counterfactual labels.
    rev0035_summary = load_json(ROOT / "data" / "rev0035_budgeted_action_counterfactual_summary.json")
    cf35_coll = rev0035_summary.get("counterfactual_collection", {})
    cf35_label = rev0035_summary.get("label_audit", {})
    cf35_cpp = rev0035_summary.get("cpp_shadow_summary", {})
    add(checks, "rev0035_budgeted_action_counterfactual_collection",
        cf35_coll.get("sampled_situations", 0) >= 24
        and cf35_coll.get("candidate_actions", 0) >= 80
        and cf35_coll.get("branch_games", 0) >= 160
        and cf35_coll.get("budgeted_situations", 0) >= 5
        and cf35_coll.get("branch_terminal_games", 0) >= 150
        and cf35_coll.get("branch_truncations") == 0
        and cf35_coll.get("cpp_checked_transitions", 0) >= 30000
        and cf35_coll.get("cpp_skipped_transitions") == 0
        and cf35_coll.get("cpp_mismatches") == 0,
        {"collection": cf35_coll})
    add(checks, "rev0035_budgeted_label_audit_present",
        cf35_label.get("situations", 0) >= 24
        and cf35_label.get("subset_situations", 0) >= 1
        and cf35_label.get("max_full_action_count", 0) > cf35_label.get("max_branched_action_count", 999)
        and "budget_reason_counts" in cf35_label,
        {"label_audit": cf35_label})
    model35_path = ROOT / "data" / "rev0035_counterfactual_action_ranker_model.json"
    model35_ok = False
    model35_details = {"exists": model35_path.exists()}
    if model35_path.exists():
        try:
            m35 = load_linear_ranker_model(model35_path)
            model35_ok = (m35.model_id == "counterfactual_linear_ranker_rev0035" and len(m35.feature_names) == len(action_ranker_feature_names()))
            model35_details.update({"model_id": m35.model_id, "feature_count": len(m35.feature_names), "source_revision": m35.source_revision})
        except Exception as exc:
            model35_details["error"] = repr(exc)
    add(checks, "rev0035_counterfactual_ranker_model_loads", model35_ok, model35_details)
    try:
        cf35_agent = make_public_agent("counterfactual_linear_ranker_rev0035")
        cf35_blend = make_public_agent("counterfactual_ranker_blend_counter_rev0035")
        agent35_ok = getattr(cf35_agent, "name", "") == "counterfactual_linear_ranker_rev0035" and getattr(cf35_blend, "name", "").endswith("rev0035")
    except Exception as exc:
        agent35_ok = False
        model35_details["agent_error"] = repr(exc)
    add(checks, "rev0035_counterfactual_agents_load", agent35_ok, {"details": model35_details})
    bundles35 = budgeted_counterfactual_action_ranker_bundles(ROOT / "data" / "seed_decks.json")
    add(checks, "rev0035_strategy_panel", len(bundles35) == 8 and any(b.agent_name.endswith("rev0035") for b in bundles35), {"bundle_count": len(bundles35), "agents": sorted({b.agent_name for b in bundles35})})
    add(checks, "rev0035_budgeted_counterfactual_payoff_gates",
        rev0035_summary.get("promotion_gate", {}).get("passed") is True
        and rev0035_summary.get("statistical_gate", {}).get("passed") is True
        and rev0035_summary.get("replay_passed", 0) >= 8
        and cf35_cpp.get("mismatches") == 0
        and cf35_cpp.get("skipped_events") == 0
        and cf35_cpp.get("events", 0) >= 40000,
        {"promotion": rev0035_summary.get("promotion_gate"), "statistical": rev0035_summary.get("statistical_gate"), "cpp": cf35_cpp})
    add(checks, "rev0035_required_output_rows",
        count_csv_rows(ROOT / "data" / "rev0035_action_counterfactual_candidates.csv") >= 80
        and count_csv_rows(ROOT / "data" / "rev0035_action_counterfactual_branch_games.csv") >= 160
        and count_csv_rows(ROOT / "data" / "rev0035_budgeted_counterfactual_ranker_games.csv") >= 144,
        {
            "candidate_rows": count_csv_rows(ROOT / "data" / "rev0035_action_counterfactual_candidates.csv") if (ROOT / "data" / "rev0035_action_counterfactual_candidates.csv").exists() else -1,
            "branch_rows": count_csv_rows(ROOT / "data" / "rev0035_action_counterfactual_branch_games.csv") if (ROOT / "data" / "rev0035_action_counterfactual_branch_games.csv").exists() else -1,
            "game_rows": count_csv_rows(ROOT / "data" / "rev0035_budgeted_counterfactual_ranker_games.csv") if (ROOT / "data" / "rev0035_budgeted_counterfactual_ranker_games.csv").exists() else -1,
        })


    # rev0036: adaptive/racing gameplay action-counterfactual labels.
    rev0036_summary = load_json(ROOT / "data" / "rev0036_adaptive_action_counterfactual_summary.json")
    cf36_coll = rev0036_summary.get("counterfactual_summary", {})
    cf36_label = rev0036_summary.get("label_audit", {})
    cf36_cpp = rev0036_summary.get("cpp_shadow_summary", {})
    add(checks, "rev0036_adaptive_action_counterfactual_collection",
        cf36_coll.get("sampled_situations", 0) >= 10
        and cf36_coll.get("candidate_actions", 0) >= 20
        and cf36_coll.get("branch_games", 0) >= 40
        and cf36_coll.get("adaptive_extra_rollouts", 0) > 0
        and cf36_coll.get("branch_terminal_games", 0) == cf36_coll.get("branch_games", -1)
        and cf36_coll.get("branch_truncations") == 0
        and cf36_coll.get("cpp_checked_transitions", 0) >= 9000
        and cf36_coll.get("cpp_skipped_transitions") == 0
        and cf36_coll.get("cpp_mismatches") == 0,
        {"collection": cf36_coll})
    add(checks, "rev0036_adaptive_label_audit_present",
        cf36_label.get("situations", 0) >= 10
        and cf36_label.get("decisive_situations", 0) >= 1
        and cf36_label.get("mean_adaptive_extra_rollouts", 0) > 0
        and "budget_reason_counts" in cf36_label,
        {"label_audit": cf36_label})
    model36_path = ROOT / "data" / "rev0036_counterfactual_action_ranker_model.json"
    model36_ok = False
    model36_details = {"exists": model36_path.exists()}
    if model36_path.exists():
        try:
            m36 = load_linear_ranker_model(model36_path)
            model36_ok = (m36.model_id == "counterfactual_linear_ranker_rev0036" and len(m36.feature_names) == len(action_ranker_feature_names()))
            model36_details.update({"model_id": m36.model_id, "feature_count": len(m36.feature_names), "source_revision": m36.source_revision})
        except Exception as exc:
            model36_details["error"] = repr(exc)
    add(checks, "rev0036_counterfactual_ranker_model_loads", model36_ok, model36_details)
    try:
        cf36_agent = make_public_agent("counterfactual_linear_ranker_rev0036")
        cf36_blend = make_public_agent("counterfactual_ranker_blend_threat_rev0036")
        agent36_ok = getattr(cf36_agent, "name", "") == "counterfactual_linear_ranker_rev0036" and getattr(cf36_blend, "name", "").endswith("rev0036")
    except Exception as exc:
        agent36_ok = False
        model36_details["agent_error"] = repr(exc)
    add(checks, "rev0036_generic_counterfactual_agents_load", agent36_ok, {"details": model36_details})
    bundles36 = adaptive_counterfactual_action_ranker_bundles(ROOT / "data" / "seed_decks.json")
    add(checks, "rev0036_strategy_panel", len(bundles36) == 8 and any(b.agent_name.endswith("rev0036") for b in bundles36), {"bundle_count": len(bundles36), "agents": sorted({b.agent_name for b in bundles36})})
    add(checks, "rev0036_adaptive_counterfactual_payoff_gates",
        rev0036_summary.get("promotion_gate", {}).get("passed") is True
        and rev0036_summary.get("statistical_gate", {}).get("passed") is True
        and rev0036_summary.get("replay_passed", 0) >= 8
        and cf36_cpp.get("mismatches") == 0
        and cf36_cpp.get("skipped_events") == 0
        and cf36_cpp.get("events", 0) >= 18000,
        {"promotion": rev0036_summary.get("promotion_gate"), "statistical": rev0036_summary.get("statistical_gate"), "cpp": cf36_cpp})
    add(checks, "rev0036_required_output_rows",
        count_csv_rows(ROOT / "data" / "rev0036_adaptive_action_counterfactual_candidates.csv") >= 20
        and count_csv_rows(ROOT / "data" / "rev0036_adaptive_action_counterfactual_branch_games.csv") >= 40
        and count_csv_rows(ROOT / "data" / "rev0036_adaptive_counterfactual_ranker_games.csv") >= 64,
        {
            "candidate_rows": count_csv_rows(ROOT / "data" / "rev0036_adaptive_action_counterfactual_candidates.csv") if (ROOT / "data" / "rev0036_adaptive_action_counterfactual_candidates.csv").exists() else -1,
            "branch_rows": count_csv_rows(ROOT / "data" / "rev0036_adaptive_action_counterfactual_branch_games.csv") if (ROOT / "data" / "rev0036_adaptive_action_counterfactual_branch_games.csv").exists() else -1,
            "game_rows": count_csv_rows(ROOT / "data" / "rev0036_adaptive_counterfactual_ranker_games.csv") if (ROOT / "data" / "rev0036_adaptive_counterfactual_ranker_games.csv").exists() else -1,
        })


    rev37_summary_path = ROOT / "data" / "rev0037_matched_label_segment_summary.json"
    rev37_summary = load_json(rev37_summary_path)
    rev37_label = rev37_summary.get("matched_label_summary", {})
    rev37_segment = rev37_summary.get("segment_benchmark_summary", {})
    rev37_candidates = count_csv_rows(ROOT / "data" / "rev0037_matched_label_candidates.csv") if (ROOT / "data" / "rev0037_matched_label_candidates.csv").exists() else -1
    rev37_branches = count_csv_rows(ROOT / "data" / "rev0037_matched_label_branch_games.csv") if (ROOT / "data" / "rev0037_matched_label_branch_games.csv").exists() else -1
    rev37_compare = count_csv_rows(ROOT / "data" / "rev0037_matched_label_comparison.csv") if (ROOT / "data" / "rev0037_matched_label_comparison.csv").exists() else -1
    rev37_seg_rows = count_csv_rows_or_catalog(ROOT / "data" / "rev0037_segment_benchmark_segments.csv")
    add(checks, "rev0037_matched_label_outputs", rev37_summary_path.exists() and rev37_candidates == rev37_summary.get("label_candidate_rows") and rev37_branches == rev37_summary.get("label_branch_rows") and rev37_compare == rev37_summary.get("label_comparison_rows"), {"summary_exists": rev37_summary_path.exists(), "candidate_rows": rev37_candidates, "summary_candidate_rows": rev37_summary.get("label_candidate_rows"), "branch_rows": rev37_branches, "summary_branch_rows": rev37_summary.get("label_branch_rows"), "comparison_rows": rev37_compare, "summary_comparison_rows": rev37_summary.get("label_comparison_rows")})
    add(checks, "rev0037_label_audit_clean_cpp", rev37_label.get("sampled_situations", 0) >= 8 and rev37_label.get("branch_truncations") == 0 and rev37_label.get("cpp_skipped_transitions") == 0 and rev37_label.get("cpp_mismatches") == 0 and 0.0 <= float(rev37_label.get("best_set_agreement_rate", -1)) <= 1.0, {"sampled_situations": rev37_label.get("sampled_situations"), "branch_truncations": rev37_label.get("branch_truncations"), "cpp_skipped": rev37_label.get("cpp_skipped_transitions"), "cpp_mismatches": rev37_label.get("cpp_mismatches"), "best_set_agreement_rate": rev37_label.get("best_set_agreement_rate")})
    add(checks, "rev0037_segment_benchmark_clean_cpp", rev37_seg_rows == rev37_summary.get("segment_rows") and rev37_segment.get("games", 0) >= 24 and rev37_segment.get("forced_actions", 0) >= rev37_segment.get("segments", 1) and rev37_segment.get("segment_mismatches") == 0 and rev37_segment.get("skipped_events") == 0, {"segment_rows": rev37_seg_rows, "summary_segment_rows": rev37_summary.get("segment_rows"), "games": rev37_segment.get("games"), "segments": rev37_segment.get("segments"), "forced_actions": rev37_segment.get("forced_actions"), "mismatches": rev37_segment.get("segment_mismatches"), "skipped": rev37_segment.get("skipped_events")})



    rev38_summary_path = ROOT / "data" / "rev0038_disagreement_screened_counterfactual_summary.json"
    rev38_summary = load_json(rev38_summary_path)
    rev38_cf = rev38_summary.get("counterfactual_summary", {})
    rev38_label = rev38_summary.get("label_audit", {})
    rev38_train = rev38_summary.get("training_summary", {})
    rev38_cpp = rev38_summary.get("cpp_shadow_summary", {})
    rev38_candidates = count_csv_rows(ROOT / "data" / "rev0038_disagreement_action_counterfactual_candidates.csv") if (ROOT / "data" / "rev0038_disagreement_action_counterfactual_candidates.csv").exists() else -1
    rev38_branches = count_csv_rows(ROOT / "data" / "rev0038_disagreement_action_counterfactual_branch_games.csv") if (ROOT / "data" / "rev0038_disagreement_action_counterfactual_branch_games.csv").exists() else -1
    rev38_votes = count_csv_rows(ROOT / "data" / "rev0038_disagreement_action_counterfactual_screen_votes.csv") if (ROOT / "data" / "rev0038_disagreement_action_counterfactual_screen_votes.csv").exists() else -1
    rev38_games = count_csv_rows(ROOT / "data" / "rev0038_disagreement_counterfactual_ranker_games.csv") if (ROOT / "data" / "rev0038_disagreement_counterfactual_ranker_games.csv").exists() else -1
    add(checks, "rev0038_disagreement_outputs", rev38_summary_path.exists() and rev38_candidates == rev38_label.get("candidate_rows") and rev38_branches == rev38_cf.get("branch_games") and rev38_votes == rev38_label.get("screen_rows") and rev38_games == rev38_summary.get("payoff_games"), {"summary_exists": rev38_summary_path.exists(), "candidate_rows": rev38_candidates, "summary_candidate_rows": rev38_label.get("candidate_rows"), "branch_rows": rev38_branches, "summary_branch_games": rev38_cf.get("branch_games"), "screen_votes": rev38_votes, "summary_screen_rows": rev38_label.get("screen_rows"), "game_rows": rev38_games, "summary_payoff_games": rev38_summary.get("payoff_games")})
    add(checks, "rev0038_disagreement_label_clean_cpp", rev38_cf.get("sampled_situations", 0) >= 8 and rev38_cf.get("screen_frames_with_disagreement", 0) >= rev38_cf.get("sampled_situations", 0) and rev38_cf.get("cpp_skipped_transitions") == 0 and rev38_cf.get("cpp_mismatches") == 0 and rev38_label.get("mean_unique_screen_votes", 0) >= 2.0, {"sampled_situations": rev38_cf.get("sampled_situations"), "screen_disagreement": rev38_cf.get("screen_frames_with_disagreement"), "cpp_skipped": rev38_cf.get("cpp_skipped_transitions"), "cpp_mismatches": rev38_cf.get("cpp_mismatches"), "mean_unique_votes": rev38_label.get("mean_unique_screen_votes")})
    model38_ok = False
    model38_details = {"path": "data/rev0038_counterfactual_action_ranker_model.json"}
    try:
        model38 = load_linear_ranker_model(ROOT / "data" / "rev0038_counterfactual_action_ranker_model.json")
        model38_ok = model38.model_id == "counterfactual_linear_ranker_rev0038" and len(model38.feature_names) == len(action_ranker_feature_names())
        model38_details.update({"model_id": model38.model_id, "feature_count": len(model38.feature_names)})
    except Exception as exc:
        model38_details["error"] = repr(exc)
    add(checks, "rev0038_counterfactual_ranker_model_loads", model38_ok, model38_details)
    try:
        cf38_agent = make_public_agent("counterfactual_linear_ranker_rev0038")
        cf38_blend = make_public_agent("counterfactual_ranker_blend_counter_rev0038")
        agent38_ok = getattr(cf38_agent, "name", "") == "counterfactual_linear_ranker_rev0038" and getattr(cf38_blend, "name", "").endswith("rev0038")
    except Exception as exc:
        agent38_ok = False
        model38_details["agent_error"] = repr(exc)
    add(checks, "rev0038_generic_counterfactual_agents_load", agent38_ok, {"details": model38_details})
    bundles38 = disagreement_counterfactual_action_ranker_bundles(ROOT / "data" / "seed_decks.json")
    add(checks, "rev0038_strategy_panel", len(bundles38) >= 6 and any(b.agent_name.endswith("rev0038") for b in bundles38), {"bundle_count": len(bundles38), "agents": sorted({b.agent_name for b in bundles38})})
    add(checks, "rev0038_payoff_gates",
        rev38_summary.get("promotion_gate", {}).get("passed") is True
        and rev38_summary.get("statistical_gate", {}).get("passed") is True
        and rev38_summary.get("replay_passed", 0) >= 6
        and rev38_cpp.get("mismatches") == 0
        and rev38_cpp.get("skipped_events") == 0
        and rev38_cpp.get("events", 0) >= 10000,
        {"promotion": rev38_summary.get("promotion_gate"), "statistical": rev38_summary.get("statistical_gate"), "cpp": rev38_cpp, "replay_passed": rev38_summary.get("replay_passed")})

    rev39_summary_path = ROOT / "data" / "rev0039_matched_screen_summary.json"
    rev39_summary = load_json(rev39_summary_path)
    rev39_cf = rev39_summary.get("counterfactual_summary", {})
    rev39_label = rev39_summary.get("label_audit", {})
    rev39_candidates = count_csv_rows(ROOT / "data" / "rev0039_matched_screen_candidates.csv") if (ROOT / "data" / "rev0039_matched_screen_candidates.csv").exists() else -1
    rev39_methods = count_csv_rows(ROOT / "data" / "rev0039_matched_screen_methods.csv") if (ROOT / "data" / "rev0039_matched_screen_methods.csv").exists() else -1
    rev39_branches = count_csv_rows(ROOT / "data" / "rev0039_matched_screen_branch_games.csv") if (ROOT / "data" / "rev0039_matched_screen_branch_games.csv").exists() else -1
    rev39_votes = count_csv_rows(ROOT / "data" / "rev0039_matched_screen_votes.csv") if (ROOT / "data" / "rev0039_matched_screen_votes.csv").exists() else -1
    rev39_pivot = count_csv_rows(ROOT / "data" / "rev0039_matched_screen_situation_pivot.csv") if (ROOT / "data" / "rev0039_matched_screen_situation_pivot.csv").exists() else -1
    add(checks, "rev0039_matched_screen_outputs",
        rev39_summary_path.exists()
        and rev39_candidates == rev39_label.get("candidate_rows")
        and rev39_methods == rev39_cf.get("method_rows")
        and rev39_branches == rev39_cf.get("branch_games")
        and rev39_votes == rev39_label.get("screen_vote_rows")
        and rev39_pivot == rev39_label.get("pivot_rows"),
        {"summary_exists": rev39_summary_path.exists(), "candidate_rows": rev39_candidates, "summary_candidate_rows": rev39_label.get("candidate_rows"), "method_rows": rev39_methods, "summary_method_rows": rev39_cf.get("method_rows"), "branch_rows": rev39_branches, "summary_branch_games": rev39_cf.get("branch_games"), "screen_votes": rev39_votes, "summary_screen_votes": rev39_label.get("screen_vote_rows"), "pivot_rows": rev39_pivot, "summary_pivot_rows": rev39_label.get("pivot_rows")})
    add(checks, "rev0039_matched_screen_clean_cpp",
        rev39_cf.get("sampled_situations", 0) >= 8
        and rev39_cf.get("frames_with_disagreement", 0) >= rev39_cf.get("sampled_situations", 0)
        and rev39_cf.get("branch_truncations") == 0
        and rev39_cf.get("cpp_skipped_transitions") == 0
        and rev39_cf.get("cpp_mismatches") == 0
        and rev39_cf.get("cpp_checked_transitions", 0) >= 10000,
        {"sampled_situations": rev39_cf.get("sampled_situations"), "frames_with_disagreement": rev39_cf.get("frames_with_disagreement"), "branch_truncations": rev39_cf.get("branch_truncations"), "cpp_skipped": rev39_cf.get("cpp_skipped_transitions"), "cpp_mismatches": rev39_cf.get("cpp_mismatches"), "cpp_checked": rev39_cf.get("cpp_checked_transitions")})
    add(checks, "rev0039_matched_screen_label_audit",
        rev39_cf.get("union_decisive_situations", 0) >= 1
        and 0.0 <= float(rev39_cf.get("screened_hits_union_best_rate", -1)) <= 1.0
        and 0.0 <= float(rev39_cf.get("unscreened_hits_union_best_rate", -1)) <= 1.0
        and rev39_label.get("method_counts", {}).get("unscreened_budget") == rev39_cf.get("sampled_situations")
        and rev39_label.get("method_counts", {}).get("screened_vote_budget") == rev39_cf.get("sampled_situations"),
        {"union_decisive_situations": rev39_cf.get("union_decisive_situations"), "screened_hits": rev39_cf.get("screened_hits_union_best_rate"), "unscreened_hits": rev39_cf.get("unscreened_hits_union_best_rate"), "screened_minus_unscreened": rev39_cf.get("mean_screened_minus_unscreened_best_score"), "method_counts": rev39_label.get("method_counts")})



    rev40_summary_path = ROOT / "data" / "rev0040_hybrid_selector_summary.json"
    rev40_summary = load_json(rev40_summary_path)
    rev40_cf = rev40_summary.get("counterfactual_summary", {})
    rev40_label = rev40_summary.get("selector_audit", {})
    rev40_candidates = count_csv_rows(ROOT / "data" / "rev0040_hybrid_selector_candidates.csv") if (ROOT / "data" / "rev0040_hybrid_selector_candidates.csv").exists() else -1
    rev40_methods = count_csv_rows(ROOT / "data" / "rev0040_hybrid_selector_methods.csv") if (ROOT / "data" / "rev0040_hybrid_selector_methods.csv").exists() else -1
    rev40_branches = count_csv_rows(ROOT / "data" / "rev0040_hybrid_selector_branch_games.csv") if (ROOT / "data" / "rev0040_hybrid_selector_branch_games.csv").exists() else -1
    rev40_votes = count_csv_rows(ROOT / "data" / "rev0040_hybrid_selector_votes.csv") if (ROOT / "data" / "rev0040_hybrid_selector_votes.csv").exists() else -1
    rev40_pivot = count_csv_rows(ROOT / "data" / "rev0040_hybrid_selector_situation_pivot.csv") if (ROOT / "data" / "rev0040_hybrid_selector_situation_pivot.csv").exists() else -1
    add(checks, "rev0040_hybrid_selector_outputs",
        rev40_summary_path.exists()
        and rev40_candidates == rev40_label.get("candidate_rows")
        and rev40_methods == rev40_cf.get("method_rows")
        and rev40_branches == rev40_cf.get("branch_games")
        and rev40_votes == rev40_label.get("screen_vote_rows")
        and rev40_pivot == rev40_label.get("pivot_rows"),
        {"summary_exists": rev40_summary_path.exists(), "candidate_rows": rev40_candidates, "summary_candidate_rows": rev40_label.get("candidate_rows"), "method_rows": rev40_methods, "summary_method_rows": rev40_cf.get("method_rows"), "branch_rows": rev40_branches, "summary_branch_games": rev40_cf.get("branch_games"), "screen_votes": rev40_votes, "summary_screen_votes": rev40_label.get("screen_vote_rows"), "pivot_rows": rev40_pivot, "summary_pivot_rows": rev40_label.get("pivot_rows")})
    add(checks, "rev0040_hybrid_selector_clean_cpp",
        rev40_cf.get("sampled_situations", 0) >= 8
        and rev40_cf.get("frames_with_disagreement", 0) >= rev40_cf.get("sampled_situations", 0)
        and rev40_cf.get("branch_truncations") == 0
        and rev40_cf.get("cpp_skipped_transitions") == 0
        and rev40_cf.get("cpp_mismatches") == 0
        and rev40_cf.get("cpp_checked_transitions", 0) >= 10000,
        {"sampled_situations": rev40_cf.get("sampled_situations"), "frames_with_disagreement": rev40_cf.get("frames_with_disagreement"), "branch_truncations": rev40_cf.get("branch_truncations"), "cpp_skipped": rev40_cf.get("cpp_skipped_transitions"), "cpp_mismatches": rev40_cf.get("cpp_mismatches"), "cpp_checked": rev40_cf.get("cpp_checked_transitions")})
    add(checks, "rev0040_hybrid_selector_label_audit",
        rev40_cf.get("union_decisive_situations", 0) >= 1
        and 0.0 <= float(rev40_cf.get("hybrid_hits_union_best_rate", -1)) <= 1.0
        and 0.0 <= float(rev40_cf.get("unscreened_hits_union_best_rate", -1)) <= 1.0
        and 0.0 <= float(rev40_cf.get("screened_hits_union_best_rate", -1)) <= 1.0
        and rev40_label.get("method_counts", {}).get("unscreened_budget") == rev40_cf.get("sampled_situations")
        and rev40_label.get("method_counts", {}).get("screened_vote_budget") == rev40_cf.get("sampled_situations")
        and rev40_label.get("method_counts", {}).get("hybrid_vote_diverse_ranker") == rev40_cf.get("sampled_situations"),
        {"union_decisive_situations": rev40_cf.get("union_decisive_situations"), "hybrid_hits": rev40_cf.get("hybrid_hits_union_best_rate"), "screened_hits": rev40_cf.get("screened_hits_union_best_rate"), "unscreened_hits": rev40_cf.get("unscreened_hits_union_best_rate"), "hybrid_minus_unscreened": rev40_cf.get("mean_hybrid_minus_unscreened_best_score"), "hybrid_minus_screened": rev40_cf.get("mean_hybrid_minus_screened_best_score"), "method_counts": rev40_label.get("method_counts")})


    # rev0041: public-only hard-frame queue for branch-label selector audits.
    hard41_summary = load_json(ROOT / "data" / "rev0041_hard_frame_summary.json")
    hard41_core = hard41_summary.get("hard_frame_summary", {})
    hard41_audit = hard41_summary.get("selector_audit", {})
    hard41_selected = count_csv_rows(ROOT / "data" / "rev0041_hard_frame_selected.csv") if (ROOT / "data" / "rev0041_hard_frame_selected.csv").exists() else -1
    hard41_candidates = count_csv_rows(ROOT / "data" / "rev0041_hard_frame_candidates.csv") if (ROOT / "data" / "rev0041_hard_frame_candidates.csv").exists() else -1
    hard41_methods = count_csv_rows(ROOT / "data" / "rev0041_hard_frame_methods.csv") if (ROOT / "data" / "rev0041_hard_frame_methods.csv").exists() else -1
    hard41_branches = count_csv_rows(ROOT / "data" / "rev0041_hard_frame_branch_games.csv") if (ROOT / "data" / "rev0041_hard_frame_branch_games.csv").exists() else -1
    hard41_trans = count_csv_rows_or_catalog(ROOT / "data" / "rev0041_hard_frame_cpp_transitions.csv")
    hard41_pivot = count_csv_rows(ROOT / "data" / "rev0041_hard_frame_pivot.csv") if (ROOT / "data" / "rev0041_hard_frame_pivot.csv").exists() else -1
    add(
        checks,
        "rev0041_hard_frame_selector_audit",
        hard41_summary.get("revision") == "rev0041"
        and hard41_core.get("selected_situations", 0) >= 8
        and hard41_core.get("high_action_selected", 0) >= 6
        and hard41_core.get("subset_situations", 0) >= 6
        and hard41_core.get("branch_truncations") == 0
        and hard41_core.get("cpp_skipped_transitions") == 0
        and hard41_core.get("cpp_mismatches") == 0
        and hard41_core.get("cpp_checked_transitions", 0) >= 10000
        and hard41_selected == hard41_core.get("selected_situations")
        and hard41_methods == hard41_core.get("method_rows")
        and hard41_branches == hard41_core.get("branch_games")
        and hard41_trans == hard41_core.get("cpp_checked_transitions")
        and hard41_pivot == hard41_core.get("selected_situations")
        and hard41_candidates >= hard41_methods
        and set(hard41_audit.get("method_counts", {}).keys()) == {"unscreened_budget", "screened_vote_budget", "hybrid_vote_diverse_ranker"},
        {
            "selected_rows": hard41_selected,
            "candidate_rows": hard41_candidates,
            "method_rows": hard41_methods,
            "branch_rows": hard41_branches,
            "transition_rows": hard41_trans,
            "pivot_rows": hard41_pivot,
            "selected_situations": hard41_core.get("selected_situations"),
            "high_action_selected": hard41_core.get("high_action_selected"),
            "subset_situations": hard41_core.get("subset_situations"),
            "cpp_checked": hard41_core.get("cpp_checked_transitions"),
            "cpp_skipped": hard41_core.get("cpp_skipped_transitions"),
            "cpp_mismatches": hard41_core.get("cpp_mismatches"),
            "method_counts": hard41_audit.get("method_counts"),
        },
    )


    # rev0042: hard-frame queue plus fixed-vs-adaptive label-budget racing audit.
    hard42_summary = load_json(ROOT / "data" / "rev0042_hard_racing_summary.json")
    hard42_core = hard42_summary.get("hard_frame_summary", {})
    hard42_race = hard42_summary.get("label_race_summary", {})
    hard42_audit = hard42_summary.get("audit", {})
    hard42_selected = count_csv_rows(ROOT / "data" / "rev0042_hard_racing_selected.csv") if (ROOT / "data" / "rev0042_hard_racing_selected.csv").exists() else -1
    hard42_candidates = count_csv_rows(ROOT / "data" / "rev0042_hard_racing_candidates.csv") if (ROOT / "data" / "rev0042_hard_racing_candidates.csv").exists() else -1
    hard42_methods = count_csv_rows(ROOT / "data" / "rev0042_hard_racing_methods.csv") if (ROOT / "data" / "rev0042_hard_racing_methods.csv").exists() else -1
    hard42_branches = count_csv_rows(ROOT / "data" / "rev0042_hard_racing_branch_games.csv") if (ROOT / "data" / "rev0042_hard_racing_branch_games.csv").exists() else -1
    hard42_trans = count_csv_rows_or_catalog(ROOT / "data" / "rev0042_hard_racing_cpp_transitions.csv")
    hard42_race_detail = count_csv_rows(ROOT / "data" / "rev0042_hard_racing_label_methods.csv") if (ROOT / "data" / "rev0042_hard_racing_label_methods.csv").exists() else -1
    hard42_race_pivot = count_csv_rows(ROOT / "data" / "rev0042_hard_racing_label_pivot.csv") if (ROOT / "data" / "rev0042_hard_racing_label_pivot.csv").exists() else -1
    add(
        checks,
        "rev0042_hard_racing_outputs",
        hard42_summary.get("revision") == "rev0042"
        and hard42_core.get("selected_situations", 0) >= 8
        and hard42_core.get("high_action_selected", 0) >= 6
        and hard42_core.get("branch_truncations") == 0
        and hard42_core.get("cpp_skipped_transitions") == 0
        and hard42_core.get("cpp_mismatches") == 0
        and hard42_core.get("cpp_checked_transitions", 0) >= 10000
        and hard42_selected == hard42_core.get("selected_situations")
        and hard42_methods == hard42_core.get("method_rows")
        and hard42_branches == hard42_core.get("branch_games")
        and hard42_trans == hard42_core.get("cpp_checked_transitions")
        and hard42_candidates >= hard42_methods,
        {
            "selected_rows": hard42_selected,
            "candidate_rows": hard42_candidates,
            "method_rows": hard42_methods,
            "branch_rows": hard42_branches,
            "transition_rows": hard42_trans,
            "selected_situations": hard42_core.get("selected_situations"),
            "high_action_selected": hard42_core.get("high_action_selected"),
            "cpp_checked": hard42_core.get("cpp_checked_transitions"),
            "cpp_skipped": hard42_core.get("cpp_skipped_transitions"),
            "cpp_mismatches": hard42_core.get("cpp_mismatches"),
        },
    )
    add(
        checks,
        "rev0042_label_race_audit",
        hard42_race.get("situations", 0) == hard42_core.get("selected_situations", -1)
        and hard42_race_detail == 2 * hard42_race.get("situations", 0)
        and hard42_race_pivot == hard42_race.get("situations", 0)
        and hard42_race.get("adaptive_rollout_savings", 0) > 0
        and 0.0 <= float(hard42_race.get("best_set_agreement_rate", -1)) <= 1.0
        and hard42_race.get("fixed_decisive_situations", 0) >= 0
        and hard42_race.get("adaptive_decisive_situations", 0) >= 0
        and hard42_audit.get("branch_truncations") == 0,
        {
            "race_situations": hard42_race.get("situations"),
            "race_detail_rows": hard42_race_detail,
            "race_pivot_rows": hard42_race_pivot,
            "fixed_rollouts": hard42_race.get("fixed_rollouts_spent"),
            "adaptive_rollouts": hard42_race.get("adaptive_rollouts_spent"),
            "savings": hard42_race.get("adaptive_rollout_savings"),
            "agreement": hard42_race.get("best_set_agreement_rate"),
            "fixed_decisive": hard42_race.get("fixed_decisive_situations"),
            "adaptive_decisive": hard42_race.get("adaptive_decisive_situations"),
            "branch_truncations": hard42_audit.get("branch_truncations"),
        },
    )



    # rev0043: live hard-frame online adaptive/racing branch collector.
    hard43_summary = load_json(ROOT / "data" / "rev0043_hard_online_racing_summary.json")
    hard43_core = hard43_summary.get("summary", {})
    hard43_audit = hard43_summary.get("audit", {})
    hard43_selected = count_csv_rows(ROOT / "data" / "rev0043_hard_online_racing_selected.csv") if (ROOT / "data" / "rev0043_hard_online_racing_selected.csv").exists() else -1
    hard43_candidates = count_csv_rows(ROOT / "data" / "rev0043_hard_online_racing_candidates.csv") if (ROOT / "data" / "rev0043_hard_online_racing_candidates.csv").exists() else -1
    hard43_branches = count_csv_rows(ROOT / "data" / "rev0043_hard_online_racing_branch_games.csv") if (ROOT / "data" / "rev0043_hard_online_racing_branch_games.csv").exists() else -1
    hard43_alloc = count_csv_rows(ROOT / "data" / "rev0043_hard_online_racing_allocations.csv") if (ROOT / "data" / "rev0043_hard_online_racing_allocations.csv").exists() else -1
    hard43_votes = count_csv_rows(ROOT / "data" / "rev0043_hard_online_racing_votes.csv") if (ROOT / "data" / "rev0043_hard_online_racing_votes.csv").exists() else -1
    hard43_trans = count_csv_rows_or_catalog(ROOT / "data" / "rev0043_hard_online_racing_cpp_transitions.csv")
    hard43_situations = count_csv_rows(ROOT / "data" / "rev0043_hard_online_racing_situation_summary.csv") if (ROOT / "data" / "rev0043_hard_online_racing_situation_summary.csv").exists() else -1
    add(
        checks,
        "rev0043_hard_online_racing_outputs",
        hard43_summary.get("revision") == "rev0043"
        and hard43_summary.get("codename") == "hardonline-racecollector"
        and hard43_core.get("selected_situations", 0) >= 8
        and hard43_core.get("high_action_selected", 0) >= 8
        and hard43_core.get("branch_truncations") == 0
        and hard43_core.get("cpp_skipped_transitions") == 0
        and hard43_core.get("cpp_mismatches") == 0
        and hard43_core.get("cpp_checked_transitions", 0) >= 8000
        and hard43_selected == hard43_core.get("selected_situations")
        and hard43_situations == hard43_core.get("selected_situations")
        and hard43_candidates == hard43_core.get("candidate_actions")
        and hard43_branches == hard43_core.get("branch_games")
        and hard43_alloc == hard43_core.get("branch_games")
        and hard43_trans == hard43_core.get("cpp_checked_transitions")
        and hard43_votes >= hard43_selected,
        {
            "selected_rows": hard43_selected,
            "candidate_rows": hard43_candidates,
            "branch_rows": hard43_branches,
            "allocation_rows": hard43_alloc,
            "vote_rows": hard43_votes,
            "transition_rows": hard43_trans,
            "situation_rows": hard43_situations,
            "selected_situations": hard43_core.get("selected_situations"),
            "high_action_selected": hard43_core.get("high_action_selected"),
            "cpp_checked": hard43_core.get("cpp_checked_transitions"),
            "cpp_skipped": hard43_core.get("cpp_skipped_transitions"),
            "cpp_mismatches": hard43_core.get("cpp_mismatches"),
        },
    )
    add(
        checks,
        "rev0043_live_racing_label_density",
        hard43_core.get("adaptive_extra_rollouts", 0) > 0
        and hard43_core.get("early_stops", 0) >= 0
        and hard43_core.get("decisive_situations", 0) >= 1
        and hard43_core.get("decisive_per_100_rollouts", 0) > 0
        and hard43_core.get("mean_rollouts_per_action", 0) >= 1.0
        and hard43_audit.get("branch_truncations") == 0,
        {
            "adaptive_extra_rollouts": hard43_core.get("adaptive_extra_rollouts"),
            "early_stops": hard43_core.get("early_stops"),
            "decisive_situations": hard43_core.get("decisive_situations"),
            "decisive_per_100_rollouts": hard43_core.get("decisive_per_100_rollouts"),
            "mean_rollouts_per_action": hard43_core.get("mean_rollouts_per_action"),
            "mean_best_minus_chosen": hard43_core.get("mean_best_minus_chosen"),
            "branch_truncations": hard43_audit.get("branch_truncations"),
        },
    )



    # rev0044: margin-seeking public hard-frame screen plus refactored branch racer seam.
    hard44_summary = load_json(ROOT / "data" / "rev0044_margin_screen_racing_summary.json")
    hard44_core = hard44_summary.get("summary", {})
    hard44_audit = hard44_summary.get("audit", {})
    hard44_model = hard44_summary.get("model", {})
    hard44_selected = count_csv_rows(ROOT / "data" / "rev0044_margin_online_racing_selected.csv") if (ROOT / "data" / "rev0044_margin_online_racing_selected.csv").exists() else -1
    hard44_candidates = count_csv_rows(ROOT / "data" / "rev0044_margin_online_racing_candidates.csv") if (ROOT / "data" / "rev0044_margin_online_racing_candidates.csv").exists() else -1
    hard44_branches = count_csv_rows(ROOT / "data" / "rev0044_margin_online_racing_branch_games.csv") if (ROOT / "data" / "rev0044_margin_online_racing_branch_games.csv").exists() else -1
    hard44_alloc = count_csv_rows(ROOT / "data" / "rev0044_margin_online_racing_allocations.csv") if (ROOT / "data" / "rev0044_margin_online_racing_allocations.csv").exists() else -1
    hard44_trans = count_csv_rows_or_catalog(ROOT / "data" / "rev0044_margin_online_racing_cpp_transitions.csv")
    hard44_holdout = count_csv_rows(ROOT / "data" / "rev0044_margin_screen_holdout_eval.csv") if (ROOT / "data" / "rev0044_margin_screen_holdout_eval.csv").exists() else -1
    add(
        checks,
        "rev0044_margin_screen_outputs",
        hard44_summary.get("revision") == "rev0044"
        and hard44_summary.get("codename") == "marginscreen-labelseeker"
        and hard44_audit.get("history_situation_rows", 0) >= 40
        and hard44_model.get("train_rows", 0) > 0
        and hard44_model.get("holdout_rows", 0) == hard44_holdout
        and hard44_core.get("selected_situations", 0) >= 8
        and hard44_core.get("high_action_selected", 0) >= 8
        and hard44_core.get("branch_truncations") == 0
        and hard44_core.get("cpp_skipped_transitions") == 0
        and hard44_core.get("cpp_mismatches") == 0
        and hard44_core.get("cpp_checked_transitions", 0) >= 8000
        and hard44_selected == hard44_core.get("selected_situations")
        and hard44_candidates == hard44_core.get("candidate_actions")
        and hard44_branches == hard44_core.get("branch_games")
        and hard44_alloc == hard44_core.get("branch_games")
        and hard44_trans == hard44_core.get("cpp_checked_transitions"),
        {
            "history_rows": hard44_audit.get("history_situation_rows"),
            "train_rows": hard44_model.get("train_rows"),
            "holdout_rows": hard44_model.get("holdout_rows"),
            "holdout_csv_rows": hard44_holdout,
            "selected_rows": hard44_selected,
            "candidate_rows": hard44_candidates,
            "branch_rows": hard44_branches,
            "allocation_rows": hard44_alloc,
            "transition_rows": hard44_trans,
            "selected_situations": hard44_core.get("selected_situations"),
            "high_action_selected": hard44_core.get("high_action_selected"),
            "cpp_checked": hard44_core.get("cpp_checked_transitions"),
            "cpp_skipped": hard44_core.get("cpp_skipped_transitions"),
            "cpp_mismatches": hard44_core.get("cpp_mismatches"),
        },
    )
    add(
        checks,
        "rev0044_margin_screen_label_density",
        hard44_core.get("adaptive_extra_rollouts", 0) > 0
        and hard44_core.get("decisive_situations", 0) >= 1
        and hard44_core.get("decisive_per_100_rollouts", 0) > 0
        and hard44_audit.get("mean_predicted_margin_selected", 0) >= hard44_audit.get("mean_pool_predicted_margin", 0) - 1e-9
        and hard44_audit.get("branch_truncations") == 0,
        {
            "adaptive_extra_rollouts": hard44_core.get("adaptive_extra_rollouts"),
            "decisive_situations": hard44_core.get("decisive_situations"),
            "decisive_per_100_rollouts": hard44_core.get("decisive_per_100_rollouts"),
            "mean_predicted_selected": hard44_audit.get("mean_predicted_margin_selected"),
            "mean_predicted_pool": hard44_audit.get("mean_pool_predicted_margin"),
            "branch_truncations": hard44_audit.get("branch_truncations"),
        },
    )


    # rev0045: matched margin-screen vs hard-screen queue audit.
    hard45_summary = load_json(ROOT / "data" / "rev0045_margin_match_summary.json")
    hard45_core = hard45_summary.get("summary", {})
    hard45_short = hard45_summary.get("short_read", {})
    hard45_pool = count_csv_rows(ROOT / "data" / "rev0045_margin_match_pool.csv") if (ROOT / "data" / "rev0045_margin_match_pool.csv").exists() else -1
    hard45_hard_rank = count_csv_rows(ROOT / "data" / "rev0045_margin_match_hard_rank.csv") if (ROOT / "data" / "rev0045_margin_match_hard_rank.csv").exists() else -1
    hard45_margin_rank = count_csv_rows(ROOT / "data" / "rev0045_margin_match_margin_rank.csv") if (ROOT / "data" / "rev0045_margin_match_margin_rank.csv").exists() else -1
    hard45_selected = count_csv_rows(ROOT / "data" / "rev0045_margin_match_selected.csv") if (ROOT / "data" / "rev0045_margin_match_selected.csv").exists() else -1
    hard45_methods = count_csv_rows(ROOT / "data" / "rev0045_margin_match_methods.csv") if (ROOT / "data" / "rev0045_margin_match_methods.csv").exists() else -1
    hard45_candidates = count_csv_rows(ROOT / "data" / "rev0045_margin_match_candidates.csv") if (ROOT / "data" / "rev0045_margin_match_candidates.csv").exists() else -1
    hard45_branches = count_csv_rows(ROOT / "data" / "rev0045_margin_match_branch_games.csv") if (ROOT / "data" / "rev0045_margin_match_branch_games.csv").exists() else -1
    hard45_alloc = count_csv_rows(ROOT / "data" / "rev0045_margin_match_allocations.csv") if (ROOT / "data" / "rev0045_margin_match_allocations.csv").exists() else -1
    hard45_trans = count_csv_rows_or_catalog(ROOT / "data" / "rev0045_margin_match_cpp_transitions.csv")
    add(
        checks,
        "rev0045_margin_match_outputs",
        hard45_summary.get("revision") == "rev0045"
        and hard45_summary.get("codename") == "marginmatch-queueaudit"
        and hard45_core.get("pool_rows") == hard45_pool
        and hard45_core.get("hard_selected") == 10
        and hard45_core.get("margin_selected") == 10
        and hard45_hard_rank == 10
        and hard45_margin_rank == 10
        and hard45_selected == hard45_core.get("union_selected")
        and hard45_methods == 20
        and hard45_candidates > 0
        and hard45_branches == hard45_core.get("branch_games")
        and hard45_alloc == hard45_core.get("branch_games")
        and hard45_trans == hard45_core.get("cpp_checked_transitions")
        and hard45_core.get("branch_truncations") == 0
        and hard45_core.get("cpp_skipped_transitions") == 0
        and hard45_core.get("cpp_mismatches") == 0
        and hard45_core.get("cpp_checked_transitions", 0) >= 10000,
        {
            "pool_rows": hard45_pool,
            "hard_rank_rows": hard45_hard_rank,
            "margin_rank_rows": hard45_margin_rank,
            "selected_rows": hard45_selected,
            "method_rows": hard45_methods,
            "candidate_rows": hard45_candidates,
            "branch_rows": hard45_branches,
            "allocation_rows": hard45_alloc,
            "transition_rows": hard45_trans,
            "core": {k: hard45_core.get(k) for k in ("pool_rows", "union_selected", "branch_games", "cpp_checked_transitions", "cpp_skipped_transitions", "cpp_mismatches")},
        },
    )
    add(
        checks,
        "rev0045_margin_match_comparison_signal",
        hard45_core.get("overlap_selected", 0) >= 1
        and hard45_core.get("hard_only_selected", 0) >= 1
        and hard45_core.get("margin_only_selected", 0) >= 1
        and hard45_core.get("hard_stats", {}).get("decisive_situations", 0) >= 1
        and hard45_core.get("margin_stats", {}).get("decisive_situations", 0) >= 1
        and hard45_core.get("hard_stats", {}).get("branch_rollouts", 0) > 0
        and hard45_core.get("margin_stats", {}).get("branch_rollouts", 0) > 0,
        {
            "overlap": hard45_core.get("overlap_selected"),
            "hard_only": hard45_core.get("hard_only_selected"),
            "margin_only": hard45_core.get("margin_only_selected"),
            "hard_decisive": hard45_core.get("hard_stats", {}).get("decisive_situations"),
            "margin_decisive": hard45_core.get("margin_stats", {}).get("decisive_situations"),
            "margin_minus_hard_decisive_per_100": hard45_short.get("margin_minus_hard_decisive_per_100"),
            "margin_minus_hard_mean_margin": hard45_core.get("margin_minus_hard_mean_margin"),
        },
    )



    # rev0046: label-yield screen vs hard/margin matched queue audit.
    y46_summary = load_json(ROOT / "data" / "rev0046_yield_match_summary.json")
    y46_core = y46_summary.get("summary", {})
    y46_short = y46_summary.get("short_read", {})
    y46_pool = count_csv_rows(ROOT / "data" / "rev0046_yield_match_pool.csv") if (ROOT / "data" / "rev0046_yield_match_pool.csv").exists() else -1
    y46_hard_rank = count_csv_rows(ROOT / "data" / "rev0046_yield_match_hard_rank.csv") if (ROOT / "data" / "rev0046_yield_match_hard_rank.csv").exists() else -1
    y46_margin_rank = count_csv_rows(ROOT / "data" / "rev0046_yield_match_margin_rank.csv") if (ROOT / "data" / "rev0046_yield_match_margin_rank.csv").exists() else -1
    y46_yield_rank = count_csv_rows(ROOT / "data" / "rev0046_yield_match_yield_rank.csv") if (ROOT / "data" / "rev0046_yield_match_yield_rank.csv").exists() else -1
    y46_selected = count_csv_rows(ROOT / "data" / "rev0046_yield_match_selected.csv") if (ROOT / "data" / "rev0046_yield_match_selected.csv").exists() else -1
    y46_methods = count_csv_rows(ROOT / "data" / "rev0046_yield_match_methods.csv") if (ROOT / "data" / "rev0046_yield_match_methods.csv").exists() else -1
    y46_candidates = count_csv_rows(ROOT / "data" / "rev0046_yield_match_candidates.csv") if (ROOT / "data" / "rev0046_yield_match_candidates.csv").exists() else -1
    y46_branches = count_csv_rows(ROOT / "data" / "rev0046_yield_match_branch_games.csv") if (ROOT / "data" / "rev0046_yield_match_branch_games.csv").exists() else -1
    y46_alloc = count_csv_rows(ROOT / "data" / "rev0046_yield_match_allocations.csv") if (ROOT / "data" / "rev0046_yield_match_allocations.csv").exists() else -1
    y46_trans = count_csv_rows_or_catalog(ROOT / "data" / "rev0046_yield_match_cpp_transitions.csv")
    y46_model_path = ROOT / "data" / "rev0046_yield_screen_model.json"
    y46_model = load_json(y46_model_path)
    add(
        checks,
        "rev0046_yield_match_outputs",
        y46_summary.get("revision") == "rev0046"
        and y46_summary.get("codename") == "yieldscreen-queuegate"
        and y46_model_path.exists()
        and y46_model.get("revision") == "rev0046"
        and y46_core.get("pool_rows") == y46_pool
        and y46_core.get("hard_selected") == 10
        and y46_core.get("margin_selected") == 10
        and y46_core.get("yield_selected") == 10
        and y46_hard_rank == 10
        and y46_margin_rank == 10
        and y46_yield_rank == 10
        and y46_selected == y46_core.get("union_selected")
        and y46_methods == 30
        and y46_candidates > 0
        and y46_branches == y46_core.get("branch_games")
        and y46_alloc == y46_core.get("branch_games")
        and y46_trans == y46_core.get("cpp_checked_transitions")
        and y46_core.get("branch_truncations") == 0
        and y46_core.get("cpp_skipped_transitions") == 0
        and y46_core.get("cpp_mismatches") == 0
        and y46_core.get("cpp_checked_transitions", 0) >= 10000,
        {
            "pool_rows": y46_pool,
            "rank_rows": {"hard": y46_hard_rank, "margin": y46_margin_rank, "yield": y46_yield_rank},
            "selected_rows": y46_selected,
            "method_rows": y46_methods,
            "candidate_rows": y46_candidates,
            "branch_rows": y46_branches,
            "allocation_rows": y46_alloc,
            "transition_rows": y46_trans,
            "core": {k: y46_core.get(k) for k in ("pool_rows", "union_selected", "branch_games", "cpp_checked_transitions", "cpp_skipped_transitions", "cpp_mismatches")},
            "model_metrics": y46_model.get("metrics"),
        },
    )
    add(
        checks,
        "rev0046_yield_match_label_density",
        y46_core.get("overlap_all_three", 0) >= 1
        and y46_core.get("yield_stats", {}).get("decisive_situations", 0) >= 1
        and y46_core.get("yield_stats", {}).get("branch_rollouts", 0) > 0
        and y46_model.get("metrics", {}).get("top_quartile_yield_per_100", 0) >= y46_model.get("metrics", {}).get("baseline_yield_per_100", 0)
        and y46_short.get("yield_decisive_per_100_rollouts", 0) > 0,
        {
            "overlap_all_three": y46_core.get("overlap_all_three"),
            "hard_decisive_per_100": y46_short.get("hard_decisive_per_100_rollouts"),
            "margin_decisive_per_100": y46_short.get("margin_decisive_per_100_rollouts"),
            "yield_decisive_per_100": y46_short.get("yield_decisive_per_100_rollouts"),
            "yield_minus_hard": y46_short.get("yield_minus_hard_decisive_per_100"),
            "yield_minus_margin": y46_short.get("yield_minus_margin_decisive_per_100"),
            "model_top_quartile_yield": y46_model.get("metrics", {}).get("top_quartile_yield_per_100"),
            "model_baseline_yield": y46_model.get("metrics", {}).get("baseline_yield_per_100"),
        },
    )


    # rev0047 yield-screened online action-counterfactual collector and ranker.
    rev47_details = {"path": "data/rev0047_yield_online_counterfactual_summary.json"}
    rev47_summary_path = ROOT / "data" / "rev0047_yield_online_counterfactual_summary.json"
    if rev47_summary_path.exists():
        rev47 = json.loads(rev47_summary_path.read_text())
        coll = rev47.get("collection_summary", {})
        lab = rev47.get("label_audit", {})
        pay = rev47.get("payoff_summary", {})
        rev47_details.update({
            "candidate_rows": lab.get("candidate_rows"),
            "situations": lab.get("situations"),
            "decisive_situations": lab.get("decisive_situations"),
            "collection_cpp_checked": coll.get("cpp_checked_transitions"),
            "collection_cpp_skipped": coll.get("cpp_skipped_transitions"),
            "collection_cpp_mismatches": coll.get("cpp_mismatches"),
            "payoff_games": pay.get("games"),
            "payoff_cpp_events": pay.get("cpp_shadow_events"),
            "payoff_cpp_skipped": pay.get("cpp_skipped_events"),
            "payoff_cpp_mismatches": pay.get("cpp_mismatches"),
            "promotion_passed": pay.get("promotion_passed"),
            "statistical_gate_passed": pay.get("statistical_gate_passed"),
            "truncations": pay.get("truncations"),
        })
        add(checks, "rev0047_summary_exists", True, rev47_details)
        add(checks, "rev0047_yield_collection_has_rows", int(lab.get("candidate_rows", 0) or 0) >= 40 and int(lab.get("situations", 0) or 0) >= 8, rev47_details)
        add(checks, "rev0047_yield_collection_cpp_clean", int(coll.get("cpp_checked_transitions", 0) or 0) >= 10000 and int(coll.get("cpp_skipped_transitions", 0) or 0) == 0 and int(coll.get("cpp_mismatches", 0) or 0) == 0, rev47_details)
        add(checks, "rev0047_ranker_payoff_gates_pass", bool(pay.get("promotion_passed")) and bool(pay.get("statistical_gate_passed")), rev47_details)
        add(checks, "rev0047_ranker_payoff_cpp_clean", int(pay.get("cpp_shadow_events", 0) or 0) >= 10000 and int(pay.get("cpp_skipped_events", 0) or 0) == 0 and int(pay.get("cpp_mismatches", 0) or 0) == 0, rev47_details)
    else:
        add(checks, "rev0047_summary_exists", False, rev47_details)

    rev47_model_path = ROOT / "data" / "rev0047_counterfactual_action_ranker_model.json"
    rev47_model_details = {"path": "data/rev0047_counterfactual_action_ranker_model.json"}
    if rev47_model_path.exists():
        m47 = load_linear_ranker_model(rev47_model_path)
        rev47_model_details.update({"model_id": m47.model_id, "feature_count": len(m47.feature_names), "source_revision": m47.source_revision})
        add(checks, "rev0047_ranker_model_loads", m47.model_id == "counterfactual_linear_ranker_rev0047" and len(m47.feature_names) == len(action_ranker_feature_names()), rev47_model_details)
    else:
        add(checks, "rev0047_ranker_model_loads", False, rev47_model_details)

    # rev0048: higher-ceiling truncation rescue for the rev0047 yield-ranker payoff panel.
    r48_summary = load_json(ROOT / "data" / "rev0048_truncation_rescue_summary.json")
    r48_rescue = r48_summary.get("rescue_summary", {})
    r48_games = count_csv_rows(ROOT / "data" / "rev0048_truncation_rescue_games.csv") if (ROOT / "data" / "rev0048_truncation_rescue_games.csv").exists() else -1
    r48_cpp_rows = count_csv_rows_or_catalog(ROOT / "data" / "rev0048_truncation_rescue_cpp_transitions.csv")
    r48_trace_rows = count_csv_rows(ROOT / "data" / "rev0048_truncation_rescue_cpp_trace_rows.csv") if (ROOT / "data" / "rev0048_truncation_rescue_cpp_trace_rows.csv").exists() else -1
    add(checks, "rev0048_truncation_rescue_terminal_gate", r48_games == 144 and r48_rescue.get("baseline_truncations") == 30 and r48_rescue.get("final_truncations") == 0 and r48_rescue.get("resolved_truncations") == 30 and r48_summary.get("promotion", {}).get("passed") is True and r48_summary.get("statistical_gate", {}).get("passed") is True, {"games": r48_games, "rescue": r48_rescue, "promotion_passed": r48_summary.get("promotion", {}).get("passed"), "stat_gate_passed": r48_summary.get("statistical_gate", {}).get("passed")})
    add(checks, "rev0048_cpp_shadow_and_trace_clean", r48_summary.get("cpp_shadow_summary", {}).get("mismatches") == 0 and r48_summary.get("cpp_shadow_summary", {}).get("skipped_events") == 0 and r48_summary.get("cpp_shadow_summary", {}).get("supported_events", 0) >= 40000 and r48_summary.get("cpp_trace_summary", {}).get("mismatches") == 0 and r48_summary.get("cpp_trace_summary", {}).get("skipped_events") == 0 and r48_trace_rows >= 2000, {"cpp_rows": r48_cpp_rows, "trace_rows": r48_trace_rows, "cpp_shadow": r48_summary.get("cpp_shadow_summary", {}), "cpp_trace": r48_summary.get("cpp_trace_summary", {})})

    # rev0049: terminal-clean yield-screened ranker refresh.
    r49_summary = load_json(ROOT / "data" / "rev0049_terminal_clean_yield_summary.json")
    r49_games_path = ROOT / "data" / "rev0049_terminal_clean_yield_games.csv"
    r49_games = count_csv_rows(r49_games_path) if r49_games_path.exists() else -1
    r49_candidates = count_csv_rows(ROOT / "data" / "rev0049_yield_online_candidates.csv") if (ROOT / "data" / "rev0049_yield_online_candidates.csv").exists() else -1
    r49_cpp_rows = count_csv_rows_or_catalog(ROOT / "data" / "rev0049_terminal_clean_yield_cpp_transitions.csv")
    r49_trace_rows = count_csv_rows(ROOT / "data" / "rev0049_terminal_clean_yield_cpp_trace_rows.csv") if (ROOT / "data" / "rev0049_terminal_clean_yield_cpp_trace_rows.csv").exists() else -1
    r49_terminal = r49_summary.get("terminal_clean_summary", {})
    r49_payoff = r49_summary.get("payoff_summary", {})
    add(checks, "rev0049_terminal_clean_yield_payoff", r49_games == 144 and r49_terminal.get("terminal_clean") is True and r49_terminal.get("truncation_rows") == 0 and r49_payoff.get("promotion_passed") is True and r49_payoff.get("statistical_gate_passed") is True, {"games": r49_games, "terminal": r49_terminal, "payoff": r49_payoff})
    add(checks, "rev0049_yield_collection_and_model", r49_candidates >= 50 and (ROOT / "data" / "rev0049_counterfactual_action_ranker_model.json").exists() and r49_summary.get("collection_summary", {}).get("cpp_mismatches") == 0 and r49_summary.get("collection_summary", {}).get("cpp_skipped_transitions") == 0, {"candidate_rows": r49_candidates, "model_exists": (ROOT / "data" / "rev0049_counterfactual_action_ranker_model.json").exists(), "collection": r49_summary.get("collection_summary", {})})
    add(checks, "rev0049_cpp_shadow_and_trace_clean", r49_payoff.get("cpp_mismatches") == 0 and r49_payoff.get("cpp_skipped_events") == 0 and r49_payoff.get("cpp_shadow_events", 0) >= 30000 and r49_payoff.get("cpp_trace_mismatches") == 0 and r49_payoff.get("cpp_trace_skipped") == 0 and r49_trace_rows >= 1500, {"cpp_rows": r49_cpp_rows, "trace_rows": r49_trace_rows, "payoff": r49_payoff})



    # rev0050: terminal-clean meta-rank / claim ledger over the full yield panel.
    r50_summary = load_json(ROOT / "data" / "rev0050_terminal_meta_summary.json")
    r50_games_path = ROOT / "data" / "rev0050_terminal_meta_games.csv"
    r50_games = count_csv_rows(r50_games_path) if r50_games_path.exists() else -1
    r50_meta_rows = count_csv_rows(ROOT / "data" / "rev0050_terminal_meta_metarank.csv") if (ROOT / "data" / "rev0050_terminal_meta_metarank.csv").exists() else -1
    r50_claim_rows = count_csv_rows(ROOT / "data" / "rev0050_terminal_meta_claim_ledger.csv") if (ROOT / "data" / "rev0050_terminal_meta_claim_ledger.csv").exists() else -1
    r50_cpp_rows = count_csv_rows_or_catalog(ROOT / "data" / "rev0050_terminal_meta_cpp_transitions.csv")
    r50_trace_rows = count_csv_rows(ROOT / "data" / "rev0050_terminal_meta_cpp_trace_rows.csv") if (ROOT / "data" / "rev0050_terminal_meta_cpp_trace_rows.csv").exists() else -1
    r50_terminal = r50_summary.get("terminal_clean_summary", {})
    r50_meta_gate = r50_summary.get("terminal_meta_gate", {})
    r50_cpp = r50_summary.get("cpp_shadow_summary", {})
    r50_trace = r50_summary.get("cpp_trace_summary", {})
    add(checks, "rev0050_terminal_meta_panel", r50_games == 256 and r50_summary.get("strategies") == 8 and r50_terminal.get("terminal_clean") is True and r50_terminal.get("truncation_rows") == 0 and r50_summary.get("promotion", {}).get("passed") is True and r50_summary.get("statistical_gate", {}).get("passed") is True and r50_meta_gate.get("passed") is True, {"games": r50_games, "strategies": r50_summary.get("strategies"), "terminal": r50_terminal, "meta_gate": r50_meta_gate, "promotion": r50_summary.get("promotion", {}), "stat_gate": r50_summary.get("statistical_gate", {})})
    add(checks, "rev0050_meta_rank_and_claim_outputs", r50_meta_rows == 24 and r50_claim_rows == 8 and abs(float(r50_meta_gate.get("meta_mass_sum", 0.0)) - 1.0) < 1e-9 and r50_summary.get("robust_candidate_count", 0) >= 1, {"meta_rows": r50_meta_rows, "claim_rows": r50_claim_rows, "meta_mass_sum": r50_meta_gate.get("meta_mass_sum"), "robust_candidate_count": r50_summary.get("robust_candidate_count")})
    add(checks, "rev0050_cpp_shadow_and_trace_clean", r50_cpp.get("mismatches") == 0 and r50_cpp.get("skipped_events") == 0 and r50_cpp.get("supported_events", 0) >= 70000 and r50_trace.get("mismatches") == 0 and r50_trace.get("skipped_events") == 0 and r50_trace_rows >= 1500, {"cpp_rows": r50_cpp_rows, "trace_rows": r50_trace_rows, "cpp_shadow": r50_cpp, "cpp_trace": r50_trace})


    # rev0051: focused terminal-clean deep repetitions around rev0050 claim-ledger agenda.
    r51_summary = load_json(ROOT / "data" / "rev0051_deep_claim_summary.json")
    r51_games_path = ROOT / "data" / "rev0051_deep_claim_games.csv"
    r51_games = count_csv_rows(r51_games_path) if r51_games_path.exists() else -1
    r51_target_rows = count_csv_rows(ROOT / "data" / "rev0051_deep_claim_target_summary.csv") if (ROOT / "data" / "rev0051_deep_claim_target_summary.csv").exists() else -1
    r51_pair_rows = count_csv_rows(ROOT / "data" / "rev0051_deep_claim_target_pairs.csv") if (ROOT / "data" / "rev0051_deep_claim_target_pairs.csv").exists() else -1
    r51_cpp_rows = count_csv_rows_or_catalog(ROOT / "data" / "rev0051_deep_claim_cpp_transitions.csv")
    r51_trace_rows = count_csv_rows(ROOT / "data" / "rev0051_deep_claim_cpp_trace_rows.csv") if (ROOT / "data" / "rev0051_deep_claim_cpp_trace_rows.csv").exists() else -1
    r51_terminal = r51_summary.get("terminal_clean_summary", {})
    r51_deep_gate = r51_summary.get("deep_claim_gate", {})
    r51_cpp = r51_summary.get("cpp_shadow_summary", {})
    r51_trace = r51_summary.get("cpp_trace_summary", {})
    add(checks, "rev0051_deep_claim_panel", r51_games == 312 and len(r51_summary.get("target_ids", [])) == 3 and r51_target_rows == 3 and r51_pair_rows >= 40 and r51_terminal.get("terminal_clean") is True and r51_terminal.get("truncation_rows") == 0, {"games": r51_games, "targets": r51_summary.get("target_ids"), "target_rows": r51_target_rows, "pair_rows": r51_pair_rows, "terminal": r51_terminal})
    add(checks, "rev0051_deep_claim_gates", r51_summary.get("promotion", {}).get("passed") is True and r51_summary.get("statistical_gate", {}).get("passed") is True and r51_summary.get("terminal_meta_gate", {}).get("passed") is True and r51_deep_gate.get("passed") is True and r51_deep_gate.get("min_target_games", 0) >= 120, {"promotion": r51_summary.get("promotion", {}), "stat_gate": r51_summary.get("statistical_gate", {}), "meta_gate": r51_summary.get("terminal_meta_gate", {}), "deep_gate": r51_deep_gate})
    add(checks, "rev0051_cpp_shadow_and_trace_clean", r51_cpp.get("mismatches") == 0 and r51_cpp.get("skipped_events") == 0 and r51_cpp.get("supported_events", 0) >= 80000 and r51_trace.get("mismatches") == 0 and r51_trace.get("skipped_events") == 0 and r51_trace_rows >= 1000, {"cpp_rows": r51_cpp_rows, "trace_rows": r51_trace_rows, "cpp_shadow": r51_cpp, "cpp_trace": r51_trace})


    # rev0052: focused life-split target/opponent cell retest.
    rev0052_summary = load_json(ROOT / "data" / "rev0052_life_flip_summary.json")
    rev0052_gate = rev0052_summary.get("life_flip_gate", {})
    rev0052_promo = rev0052_summary.get("promotion", {})
    rev0052_stat = rev0052_summary.get("statistical_gate", {})
    rev0052_cpp = rev0052_summary.get("cpp_shadow_summary", {})
    rev0052_trace = rev0052_summary.get("cpp_trace_summary", {})
    add(checks, "rev0052_life_flip_terminal_clean_gates", rev0052_summary.get("games") == 256 and rev0052_summary.get("terminal_clean_summary", {}).get("truncation_rows") == 0 and rev0052_promo.get("passed") is True and rev0052_stat.get("passed") is True and rev0052_gate.get("passed") is True, {"games": rev0052_summary.get("games"), "truncations": rev0052_summary.get("terminal_clean_summary", {}).get("truncation_rows"), "promotion": rev0052_promo.get("passed"), "statistical": rev0052_stat.get("passed"), "life_flip_gate": rev0052_gate.get("passed")})
    add(checks, "rev0052_life_flip_cpp_and_replay_clean", rev0052_cpp.get("events", 0) >= 50000 and rev0052_cpp.get("mismatches") == 0 and rev0052_cpp.get("skipped_events") == 0 and rev0052_trace.get("mismatches") == 0 and rev0052_trace.get("skipped_events") == 0 and rev0052_summary.get("replay_passed") == rev0052_summary.get("replay_samples") == 8, {"cpp_events": rev0052_cpp.get("events"), "cpp_mismatches": rev0052_cpp.get("mismatches"), "cpp_skipped": rev0052_cpp.get("skipped_events"), "trace_events": rev0052_trace.get("events"), "trace_mismatches": rev0052_trace.get("mismatches"), "trace_skipped": rev0052_trace.get("skipped_events"), "replay_passed": rev0052_summary.get("replay_passed"), "replay_samples": rev0052_summary.get("replay_samples")})
    rev0052_selected_rows = count_csv_rows(ROOT / "data" / "rev0052_life_flip_selected_matchups.csv") if (ROOT / "data" / "rev0052_life_flip_selected_matchups.csv").exists() else -1
    rev0052_cell_rows = count_csv_rows(ROOT / "data" / "rev0052_life_flip_target_life_cells.csv") if (ROOT / "data" / "rev0052_life_flip_target_life_cells.csv").exists() else -1
    rev0052_flip_rows = count_csv_rows(ROOT / "data" / "rev0052_life_flip_retest.csv") if (ROOT / "data" / "rev0052_life_flip_retest.csv").exists() else -1
    add(checks, "rev0052_life_flip_artifact_shape", rev0052_selected_rows == 4 and rev0052_cell_rows == 8 and rev0052_flip_rows == 4 and rev0052_gate.get("min_cell_games") == 32, {"selected_rows": rev0052_selected_rows, "cell_rows": rev0052_cell_rows, "flip_rows": rev0052_flip_rows, "min_cell_games": rev0052_gate.get("min_cell_games")})

    # rev0053: concrete cell-confirmation / confluence retest.
    rev0053_summary = load_json(ROOT / "data" / "rev0053_cell_confirm_summary.json")
    rev0053_gate = rev0053_summary.get("cell_confirmation_gate", {})
    rev0053_promo = rev0053_summary.get("promotion", {})
    rev0053_stat = rev0053_summary.get("statistical_gate", {})
    rev0053_cpp = rev0053_summary.get("cpp_shadow_summary", {})
    rev0053_trace = rev0053_summary.get("cpp_trace_summary", {})
    add(checks, "rev0053_cell_confirm_terminal_clean_gates", rev0053_summary.get("games") == 288 and rev0053_summary.get("terminal_clean_summary", {}).get("truncation_rows") == 0 and rev0053_promo.get("passed") is True and rev0053_stat.get("passed") is True and rev0053_gate.get("passed") is True, {"games": rev0053_summary.get("games"), "truncations": rev0053_summary.get("terminal_clean_summary", {}).get("truncation_rows"), "promotion": rev0053_promo.get("passed"), "statistical": rev0053_stat.get("passed"), "cell_confirmation_gate": rev0053_gate.get("passed")})
    add(checks, "rev0053_cell_confirm_cpp_and_replay_clean", rev0053_cpp.get("events", 0) >= 80000 and rev0053_cpp.get("mismatches") == 0 and rev0053_cpp.get("skipped_events") == 0 and rev0053_trace.get("mismatches") == 0 and rev0053_trace.get("skipped_events") == 0 and rev0053_summary.get("replay_passed") == rev0053_summary.get("replay_samples") == 8, {"cpp_events": rev0053_cpp.get("events"), "cpp_mismatches": rev0053_cpp.get("mismatches"), "cpp_skipped": rev0053_cpp.get("skipped_events"), "trace_events": rev0053_trace.get("events"), "trace_mismatches": rev0053_trace.get("mismatches"), "trace_skipped": rev0053_trace.get("skipped_events"), "replay_passed": rev0053_summary.get("replay_passed"), "replay_samples": rev0053_summary.get("replay_samples")})
    rev0053_agenda_rows = count_csv_rows(ROOT / "data" / "rev0053_cell_confirm_agenda.csv") if (ROOT / "data" / "rev0053_cell_confirm_agenda.csv").exists() else -1
    rev0053_cell_rows = count_csv_rows(ROOT / "data" / "rev0053_cell_confirm_target_life_cells.csv") if (ROOT / "data" / "rev0053_cell_confirm_target_life_cells.csv").exists() else -1
    rev0053_confirm_rows = count_csv_rows(ROOT / "data" / "rev0053_cell_confirm_confirmation.csv") if (ROOT / "data" / "rev0053_cell_confirm_confirmation.csv").exists() else -1
    add(checks, "rev0053_cell_confirm_artifact_shape", rev0053_agenda_rows == 3 and rev0053_cell_rows == 6 and rev0053_confirm_rows == 3 and rev0053_gate.get("min_cell_games") == 48 and rev0053_gate.get("favored_or_confirmed_cells", 0) >= 1, {"agenda_rows": rev0053_agenda_rows, "cell_rows": rev0053_cell_rows, "confirmation_rows": rev0053_confirm_rows, "min_cell_games": rev0053_gate.get("min_cell_games"), "favored_or_confirmed_cells": rev0053_gate.get("favored_or_confirmed_cells")})


    # rev0054: concrete matchup-claim dossier for cf34_counter_wall vs pub_threat_overlord.
    rev0054_summary = load_json(ROOT / "data" / "rev0054_matchup_claim_summary.json")
    rev0054_gate = rev0054_summary.get("matchup_claim_gate", {})
    rev0054_promo = rev0054_summary.get("promotion", {})
    rev0054_stat = rev0054_summary.get("statistical_gate", {})
    rev0054_cpp = rev0054_summary.get("cpp_shadow_summary", {})
    rev0054_trace = rev0054_summary.get("cpp_trace_summary", {})
    rev0054_terminal = rev0054_summary.get("terminal_clean_summary", {})
    add(checks, "rev0054_matchup_claim_terminal_clean_gates", rev0054_summary.get("games") == 160 and rev0054_terminal.get("truncation_rows") == 0 and rev0054_promo.get("passed") is True and rev0054_stat.get("passed") is True and rev0054_gate.get("passed") is True, {"games": rev0054_summary.get("games"), "truncations": rev0054_terminal.get("truncation_rows"), "promotion": rev0054_promo.get("passed"), "statistical": rev0054_stat.get("passed"), "claim_gate": rev0054_gate.get("passed")})
    add(checks, "rev0054_matchup_claim_cpp_and_replay_clean", rev0054_cpp.get("events", 0) >= 40000 and rev0054_cpp.get("mismatches") == 0 and rev0054_cpp.get("skipped_events") == 0 and rev0054_trace.get("mismatches") == 0 and rev0054_trace.get("skipped_events") == 0 and rev0054_summary.get("replay_passed") == rev0054_summary.get("replay_samples") == 8, {"cpp_events": rev0054_cpp.get("events"), "cpp_mismatches": rev0054_cpp.get("mismatches"), "cpp_skipped": rev0054_cpp.get("skipped_events"), "trace_events": rev0054_trace.get("events"), "trace_mismatches": rev0054_trace.get("mismatches"), "trace_skipped": rev0054_trace.get("skipped_events"), "replay_passed": rev0054_summary.get("replay_passed"), "replay_samples": rev0054_summary.get("replay_samples")})
    rev0054_agenda_rows = count_csv_rows(ROOT / "data" / "rev0054_matchup_claim_agenda.csv") if (ROOT / "data" / "rev0054_matchup_claim_agenda.csv").exists() else -1
    rev0054_cell_rows = count_csv_rows(ROOT / "data" / "rev0054_matchup_claim_target_life_cells.csv") if (ROOT / "data" / "rev0054_matchup_claim_target_life_cells.csv").exists() else -1
    rev0054_claim_rows = count_csv_rows(ROOT / "data" / "rev0054_matchup_claim_claim_rows.csv") if (ROOT / "data" / "rev0054_matchup_claim_claim_rows.csv").exists() else -1
    rev0054_labels = rev0054_summary.get("claim_label_counts", {})
    add(checks, "rev0054_matchup_claim_artifact_shape", rev0054_agenda_rows == 1 and rev0054_cell_rows == 2 and rev0054_claim_rows == 1 and rev0054_gate.get("claim_candidate_count") == 1 and rev0054_labels.get("life_sensitive_matchup_claim_candidate") == 1, {"agenda_rows": rev0054_agenda_rows, "cell_rows": rev0054_cell_rows, "claim_rows": rev0054_claim_rows, "claim_candidate_count": rev0054_gate.get("claim_candidate_count"), "labels": rev0054_labels})



    # rev0055: life-cell claim decomposition of the rev0054 life-sensitive dossier.
    rev0055_summary = load_json(ROOT / "data" / "rev0055_life_cell_summary.json")
    rev0055_gate = rev0055_summary.get("life_cell_claim_gate", {})
    rev0055_promo = rev0055_summary.get("promotion", {})
    rev0055_stat = rev0055_summary.get("statistical_gate", {})
    rev0055_cpp = rev0055_summary.get("cpp_shadow_summary", {})
    rev0055_trace = rev0055_summary.get("cpp_trace_summary", {})
    rev0055_terminal = rev0055_summary.get("terminal_clean_summary", {})
    add(checks, "rev0055_life_cell_terminal_clean_gates", rev0055_summary.get("games") == 256 and rev0055_terminal.get("truncation_rows") == 0 and rev0055_promo.get("passed") is True and rev0055_stat.get("passed") is True and rev0055_gate.get("passed") is True, {"games": rev0055_summary.get("games"), "truncations": rev0055_terminal.get("truncation_rows"), "promotion": rev0055_promo.get("passed"), "statistical": rev0055_stat.get("passed"), "life_cell_gate": rev0055_gate})
    add(checks, "rev0055_life_cell_cpp_and_replay_clean", rev0055_cpp.get("events", 0) >= 70000 and rev0055_cpp.get("mismatches") == 0 and rev0055_cpp.get("skipped_events") == 0 and rev0055_trace.get("mismatches") == 0 and rev0055_trace.get("skipped_events") == 0 and rev0055_summary.get("replay_passed") == rev0055_summary.get("replay_samples") == 8, {"cpp_events": rev0055_cpp.get("events"), "cpp_mismatches": rev0055_cpp.get("mismatches"), "cpp_skipped": rev0055_cpp.get("skipped_events"), "trace_events": rev0055_trace.get("events"), "trace_mismatches": rev0055_trace.get("mismatches"), "trace_skipped": rev0055_trace.get("skipped_events"), "replay_passed": rev0055_summary.get("replay_passed"), "replay_samples": rev0055_summary.get("replay_samples")})
    rev0055_agenda_rows = count_csv_rows(ROOT / "data" / "rev0055_life_cell_agenda.csv") if (ROOT / "data" / "rev0055_life_cell_agenda.csv").exists() else -1
    rev0055_current_rows = count_csv_rows(ROOT / "data" / "rev0055_life_cell_current_cells.csv") if (ROOT / "data" / "rev0055_life_cell_current_cells.csv").exists() else -1
    rev0055_cumulative_rows = count_csv_rows(ROOT / "data" / "rev0055_life_cell_cumulative_cells.csv") if (ROOT / "data" / "rev0055_life_cell_cumulative_cells.csv").exists() else -1
    rev0055_current_labels = rev0055_summary.get("current_cell_signal_counts", {})
    rev0055_cum_labels = rev0055_summary.get("cumulative_cell_signal_counts", {})
    add(checks, "rev0055_life_cell_artifact_shape", rev0055_agenda_rows == 2 and rev0055_current_rows == 2 and rev0055_cumulative_rows == 2 and rev0055_gate.get("claim_cell_count") == 2 and rev0055_cum_labels.get("life_cell_claim_candidate") == 2, {"agenda_rows": rev0055_agenda_rows, "current_rows": rev0055_current_rows, "cumulative_rows": rev0055_cumulative_rows, "current_labels": rev0055_current_labels, "cumulative_labels": rev0055_cum_labels, "claim_cell_count": rev0055_gate.get("claim_cell_count")})


    rev56_summary_path = ROOT / "data" / "rev0056_life_cell_replication_summary.json"
    rev56_games_path = ROOT / "data" / "rev0056_life_cell_replication_games.csv"
    rev56_holdout_path = ROOT / "data" / "rev0056_life_cell_replication_holdout_cells.csv"
    rev56_compare_path = ROOT / "data" / "rev0056_life_cell_replication_comparison.csv"
    rev56_summary = load_json(rev56_summary_path)
    rev56_gate = rev56_summary.get("life_cell_replication_gate", {})
    rev56_cpp = rev56_summary.get("cpp_shadow_summary", {})
    rev56_trace = rev56_summary.get("cpp_trace_summary", {})
    rev56_rows = count_csv_rows(rev56_games_path) if rev56_games_path.exists() else -1
    rev56_holdout_rows = count_csv_rows(rev56_holdout_path) if rev56_holdout_path.exists() else -1
    rev56_compare_rows = count_csv_rows(rev56_compare_path) if rev56_compare_path.exists() else -1
    add(checks, "rev0056_life_cell_replication_holdout", rev56_rows == 192 and rev56_holdout_rows == 2 and rev56_compare_rows == 2 and rev56_summary.get("games") == 192 and rev56_gate.get("passed") is True and rev56_gate.get("replicated_claim_cells", 0) >= 2 and rev56_cpp.get("skipped_events") == 0 and rev56_cpp.get("mismatches") == 0 and rev56_trace.get("skipped_events") == 0 and rev56_trace.get("mismatches") == 0, {"rows": rev56_rows, "holdout_rows": rev56_holdout_rows, "comparison_rows": rev56_compare_rows, "summary_games": rev56_summary.get("games"), "gate": rev56_gate, "cpp_skipped": rev56_cpp.get("skipped_events"), "cpp_mismatches": rev56_cpp.get("mismatches"), "trace_skipped": rev56_trace.get("skipped_events"), "trace_mismatches": rev56_trace.get("mismatches")})

    required_files = [
        "src/muc5/mulligan.py",
        "src/muc5/invariants.py",
        "tests/test_rev0005_mulligan_actionspace.py",
        "scripts/run_mulligan_probe.py",
        "scripts/audit_action_space.py",
        "docs/mulligan_rev0005.md",
        "docs/action_space_audit_rev0005.md",
        "docs/research_rev0005.md",
        "docs/refactor_audit_rev0005.md",
        "docs/simulator_rev0005.md",
        "tests/test_rev0006_mulligan_agency.py",
        "scripts/run_mulligan_agency_probe.py",
        "scripts/run_mulligan_life_arena.py",
        "docs/mulligan_agency_rev0006.md",
        "docs/research_rev0006.md",
        "docs/simulator_rev0006.md",
        "docs/refactor_audit_rev0006.md",
        "docs/experiment_matrix_rev0006.md",
        "docs/research_sources_rev0006.md",
        "src/muc5/gametable.py",
        "tests/test_rev0007_gametable.py",
        "scripts/gametable_cli.py",
        "scripts/run_rev0007_sparring_probe.py",
        "docs/gametable_rev0007.md",
        "docs/simulator_rev0007.md",
        "docs/sparring_agents_rev0007.md",
        "docs/research_rev0007.md",
        "docs/refactor_audit_rev0007.md",
        "docs/experiment_matrix_rev0007.md",
        "src/muc5/payoff.py",
        "src/muc5/perf.py",
        "tests/test_rev0008_payoff_perf.py",
        "scripts/run_rev0008_payoff_table.py",
        "scripts/profile_simulator_rev0008.py",
        "docs/payoff_table_rev0008.md",
        "docs/performance_rev0008.md",
        "docs/research_rev0008.md",
        "docs/simulator_rev0008.md",
        "docs/refactor_audit_rev0008.md",
        "docs/experiment_matrix_rev0008.md",
        "src/muc5/decision.py",
        "src/muc5/fairness.py",
        "tests/test_rev0009_decision_leakguard.py",
        "scripts/inspect_cloudtainer_tools.py",
        "scripts/audit_leakage_rev0009.py",
        "scripts/profile_decisionframe_rev0009.py",
        "scripts/run_rev0009_mulligan_bundle_payoff.py",
        "docs/cloudtainer_office_rev0009.md",
        "docs/leak_guard_rev0009.md",
        "docs/decision_frame_rev0009.md",
        "docs/performance_rev0009.md",
        "docs/research_rev0009.md",
        "docs/refactor_audit_rev0009.md",
        "docs/experiment_matrix_rev0009.md",
        "src/muc5/readiness.py",
        "tests/test_rev0010_simulator_readiness.py",
        "scripts/run_rev0010_rules_scenarios.py",
        "scripts/fuzz_simulator_rev0010.py",
        "scripts/profile_simulator_rev0010.py",
        "scripts/simulator_readiness_rev0010.py",
        "docs/simulator_readiness_rev0010.md",
        "docs/rules_scenarios_rev0010.md",
        "docs/fuzzing_rev0010.md",
        "docs/performance_rev0010.md",
        "docs/research_rev0010.md",
        "docs/refactor_audit_rev0010.md",
        "docs/experiment_matrix_rev0010.md",
        "src/muc5/replay.py",
        "src/muc5/reward_guard.py",
        "tests/test_rev0011_replay_rewardguard.py",
        "scripts/run_rev0011_replay_probe.py",
        "scripts/audit_reward_guard_rev0011.py",
        "scripts/build_rev0011_question_bank.py",
        "docs/replay_lab_rev0011.md",
        "docs/reward_guard_rev0011.md",
        "docs/research_rev0011.md",
        "docs/refactor_audit_rev0011.md",
        "docs/experiment_matrix_rev0011.md",
        "docs/simulator_rev0011.md",
        "src/muc5/public_agents.py",
        "src/muc5/promotion.py",
        "src/muc5/oracle_seed.py",
        "tests/test_rev0012_promotion_public_oracle.py",
        "scripts/run_rev0012_public_payoff_promotion.py",
        "scripts/run_rev0012_oracle_seed.py",
        "docs/promotion_gate_rev0012.md",
        "docs/public_agents_rev0012.md",
        "docs/oracle_seed_rev0012.md",
        "docs/method_leak_inventory_rev0012.md",
        "docs/research_rev0012.md",
        "docs/cloudtainer_bound_method_rev0012.md",
        "docs/refactor_audit_rev0012.md",
        "docs/experiment_matrix_rev0012.md",
        "src/muc5/code_policy.py",
        "src/muc5/public_payoff.py",
        "tests/test_rev0013_code_policy_gap.py",
        "scripts/run_rev0013_code_policy_payoff.py",
        "scripts/run_rev0013_public_trusted_gap.py",
        "docs/code_policy_oracles_rev0013.md",
        "docs/public_trusted_gap_rev0013.md",
        "docs/research_rev0013.md",
        "docs/refactor_audit_rev0013.md",
        "docs/experiment_matrix_rev0013.md",
        "data/rev0013_question_bank.json",
        "src/muc5/statgate.py",
        "src/muc5/map_elites.py",
        "src/muc5/strategy_sets.py",
        "tests/test_rev0014_statgate_mapelite.py",
        "scripts/run_rev0014_statgate_payoff.py",
        "scripts/run_rev0014_map_elites_seed.py",
        "docs/statistical_gate_rev0014.md",
        "docs/map_elites_rev0014.md",
        "docs/research_rev0014.md",
        "docs/refactor_audit_rev0014.md",
        "docs/experiment_matrix_rev0014.md",
        "data/rev0014_question_bank.json",
        "cpp/muc5_probe_kernel.cpp",
        "src/muc5/cpp_accel.py",
        "src/muc5/action_features.py",
        "tests/test_rev0015_cpp_stall_features.py",
        "scripts/benchmark_cpp_probe_rev0015.py",
        "scripts/run_rev0015_mapelite_eval.py",
        "scripts/run_rev0015_stall_adversary.py",
        "docs/cpp_bridge_rev0015.md",
        "docs/stall_adversary_rev0015.md",
        "docs/action_features_rev0015.md",
        "docs/mapelite_eval_rev0015.md",
        "docs/refactor_audit_rev0015.md",
        "docs/experiment_matrix_rev0015.md",
        "docs/priority_reconsideration_rev0015.md",
        "data/rev0015_question_bank.json",
        "cpp/muc5_legal_menu.cpp",
        "src/muc5/cpp_legal.py",
        "src/muc5/sequential_race.py",
        "tests/test_rev0016_cpplegal_seqrace.py",
        "scripts/run_rev0016_cpp_legal_diff.py",
        "scripts/run_rev0016_sequential_race.py",
        "docs/cpp_core_plan_rev0016.md",
        "docs/cpp_legal_menu_rev0016.md",
        "docs/sequential_race_rev0016.md",
        "docs/refactor_audit_rev0016.md",
        "docs/priority_reconsideration_rev0016.md",
        "docs/experiment_matrix_rev0016.md",
        "data/rev0016_question_bank.json",
        "cpp/muc5_transition_micro.cpp",
        "src/muc5/cpp_transition.py",
        "src/muc5/metarank.py",
        "tests/test_rev0017_cpptransition_metarank.py",
        "scripts/run_rev0017_cpp_transition_diff.py",
        "scripts/run_rev0017_metarank_payoff.py",
        "docs/cpp_transition_micro_rev0017.md",
        "docs/metarank_rev0017.md",
        "docs/refactor_audit_rev0017.md",
        "docs/priority_reconsideration_rev0017.md",
        "docs/experiment_matrix_rev0017.md",
        "data/rev0017_question_bank.json",
        "src/muc5/cpp_coverage.py",
        "tests/test_rev0018_cpptransition_choices.py",
        "scripts/run_rev0018_cpp_transition_expansion.py",
        "scripts/run_rev0018_cpp_coverage_probe.py",
        "docs/cpp_transition_micro_rev0018.md",
        "docs/cpp_coverage_rev0018.md",
        "docs/refactor_audit_rev0018.md",
        "docs/priority_reconsideration_rev0018.md",
        "docs/experiment_matrix_rev0018.md",
        "docs/cpp_core_plan_rev0018.md",
        "data/rev0018_question_bank.json",
        "src/muc5/cpp_trace.py",
        "tests/test_rev0019_cpptrace.py",
        "scripts/run_rev0019_cpp_trace_check.py",
        "docs/cpp_trace_checker_rev0019.md",
        "docs/cpp_cutover_readiness_rev0019.md",
        "docs/refactor_audit_rev0019.md",
        "docs/priority_reconsideration_rev0019.md",
        "docs/experiment_matrix_rev0019.md",
        "docs/simulator_rev0019.md",
        "docs/cpp_core_plan_rev0019.md",
        "data/rev0019_question_bank.json",
        "src/muc5/imitation.py",
        "tests/test_rev0020_cppultimate_rankerseed.py",
        "scripts/run_rev0020_cpp_ultimate_trace_check.py",
        "scripts/run_rev0020_action_ranker_seed.py",
        "docs/cpp_ultimate_transport_rev0020.md",
        "docs/action_ranker_seed_rev0020.md",
        "docs/refactor_audit_rev0020.md",
        "docs/priority_reconsideration_rev0020.md",
        "docs/simulator_rev0020.md",
        "docs/experiment_matrix_rev0020.md",
        "docs/cpp_core_plan_rev0020.md",
        "data/rev0020_cpp_trace_summary.json",
        "data/rev0020_action_ranker_summary.json",
        "data/rev0020_question_bank.json",
        "src/muc5/ranker_policy.py",
        "tests/test_rev0021_ranker_batch.py",
        "scripts/benchmark_rev0021_cpp_trace_batch.py",
        "scripts/run_rev0021_ranker_policy_eval.py",
        "docs/cpp_batch_trace_rev0021.md",
        "docs/ranker_policy_rev0021.md",
        "docs/refactor_audit_rev0021.md",
        "docs/priority_reconsideration_rev0021.md",
        "docs/experiment_matrix_rev0021.md",
        "docs/simulator_rev0021.md",
        "docs/cpp_core_plan_rev0021.md",
        "data/rev0021_cpp_batch_benchmark.json",
        "data/rev0021_ranker_policy_summary.json",
        "data/rev0021_linear_ranker_model.json",
        "data/rev0021_question_bank.json",
        "tests/test_rev0022_ranker_race.py",
        "scripts/run_rev0022_ranker_sequential_race.py",
        "scripts/run_rev0022_mapelite_ranker_variants.py",
        "docs/ranker_blends_rev0022.md",
        "docs/ranker_sequential_race_rev0022.md",
        "docs/mapelite_ranker_variants_rev0022.md",
        "docs/performance_refactor_rev0022.md",
        "docs/refactor_audit_rev0022.md",
        "docs/priority_reconsideration_rev0022.md",
        "docs/experiment_matrix_rev0022.md",
        "docs/cpp_core_plan_rev0022.md",
        "docs/simulator_rev0022.md",
        "docs/ranker_race_results_rev0022.md",
        "data/rev0022_ranker_race_summary.json",
        "data/rev0022_mapelite_ranker_variants_summary.json",
        "data/rev0022_question_bank.json",
        "tests/test_rev0023_mlpranker_mullgate.py",
        "scripts/run_rev0023_mlp_ranker_eval.py",
        "scripts/run_rev0023_mulligan_policy_gate.py",
        "docs/mlp_ranker_rev0023.md",
        "docs/mulligan_policy_gate_rev0023.md",
        "docs/cpp_core_plan_rev0023.md",
        "docs/refactor_audit_rev0023.md",
        "docs/priority_reconsideration_rev0023.md",
        "docs/experiment_matrix_rev0023.md",
        "docs/simulator_rev0023.md",
        "docs/ranker_mulligan_results_rev0023.md",
        "data/rev0023_mlp_ranker_summary.json",
        "data/rev0023_mlp_ranker_model.json",
        "data/rev0023_mulligan_policy_gate_summary.json",
        "data/rev0023_question_bank.json",
        "src/muc5/mulligan_ranker.py",
        "tests/test_rev0024_mulligan_ranker.py",
        "scripts/run_rev0024_mulligan_ranker.py",
        "docs/learned_mulligan_ranker_rev0024.md",
        "docs/mulligan_agency_refactor_rev0024.md",
        "docs/cpp_core_plan_rev0024.md",
        "docs/refactor_audit_rev0024.md",
        "docs/priority_reconsideration_rev0024.md",
        "docs/experiment_matrix_rev0024.md",
        "docs/simulator_rev0024.md",
        "data/rev0024_mulligan_ranker_model.json",
        "data/rev0024_learned_mulligan_summary.json",
        "data/rev0024_question_bank.json",
        "src/muc5/outcome_training.py",
        "tests/test_rev0025_outcome_ranker.py",
        "scripts/run_rev0025_outcome_ranker.py",
        "docs/outcome_weighted_ranker_rev0025.md",
        "docs/trajectory_audit_rev0025.md",
        "docs/cpp_core_plan_rev0025.md",
        "docs/refactor_audit_rev0025.md",
        "docs/priority_reconsideration_rev0025.md",
        "docs/experiment_matrix_rev0025.md",
        "docs/simulator_rev0025.md",
        "docs/outcomeranker_results_rev0025.md",
        "data/rev0025_outcome_ranker_model.json",
        "data/rev0025_outcome_ranker_summary.json",
        "data/rev0025_question_bank.json",
        "src/muc5/cpp_rollout.py",
        "tests/test_rev0026_cpprollout_rng.py",
        "scripts/run_rev0026_cpp_shadow_rollout.py",
        "docs/cpp_shadow_rollout_rev0026.md",
        "docs/rng_split_rev0026.md",
        "docs/cpp_core_plan_rev0026.md",
        "docs/refactor_audit_rev0026.md",
        "docs/priority_reconsideration_rev0026.md",
        "docs/experiment_matrix_rev0026.md",
        "docs/simulator_rev0026.md",
        "docs/cpp_shadow_results_rev0026.md",
        "data/rev0026_cpp_shadow_rollout_summary.json",
        "data/rev0026_question_bank.json",
        "src/muc5/mulligan_outcome_training.py",
        "tests/test_rev0027_mulligan_outcome.py",
        "scripts/run_rev0027_mulligan_outcome_ranker.py",
        "docs/mulligan_outcome_ranker_rev0027.md",
        "docs/public_payoff_cache_refactor_rev0027.md",
        "docs/cpp_core_plan_rev0027.md",
        "docs/refactor_audit_rev0027.md",
        "docs/priority_reconsideration_rev0027.md",
        "docs/experiment_matrix_rev0027.md",
        "docs/simulator_rev0027.md",
        "docs/mulligan_outcome_results_rev0027.md",
        "data/rev0027_mulligan_outcome_ranker_model.json",
        "data/rev0027_mulligan_outcome_summary.json",
        "data/rev0027_question_bank.json",
        "src/muc5/opening_counterfactual.py",
        "tests/test_rev0028_opening_counterfactual.py",
        "scripts/run_rev0028_opening_counterfactual.py",
        "docs/opening_counterfactual_rev0028.md",
        "docs/pregame_state_refactor_rev0028.md",
        "docs/cpp_core_plan_rev0028.md",
        "docs/refactor_audit_rev0028.md",
        "docs/priority_reconsideration_rev0028.md",
        "docs/experiment_matrix_rev0028.md",
        "docs/simulator_rev0028.md",
        "data/rev0028_opening_counterfactual_summary.json",
        "data/rev0028_question_bank.json",
        "src/muc5/mulligan_counterfactual.py",
        "src/muc5/nochoice_segments.py",
        "tests/test_rev0029_counterfactual_mulligan.py",
        "scripts/run_rev0029_counterfactual_mulligan_ranker.py",
        "docs/counterfactual_mulligan_ranker_rev0029.md",
        "docs/nochoice_segment_audit_rev0029.md",
        "docs/cpp_core_plan_rev0029.md",
        "docs/refactor_audit_rev0029.md",
        "docs/priority_reconsideration_rev0029.md",
        "docs/experiment_matrix_rev0029.md",
        "docs/simulator_rev0029.md",
        "data/rev0029_counterfactual_mulligan_summary.json",
        "data/rev0029_counterfactual_mulligan_model.json",
        "data/rev0029_nochoice_segment_summary.json",
        "data/rev0029_question_bank.json",
        "src/muc5/opening_counterfactual_repeat.py",
        "tests/test_rev0030_repeated_counterfactual.py",
        "scripts/run_rev0030_repeated_counterfactual_mulligan.py",
        "docs/repeated_counterfactual_mulligan_rev0030.md",
        "docs/nochoice_segment_fingerprints_rev0030.md",
        "docs/cpp_core_plan_rev0030.md",
        "docs/refactor_audit_rev0030.md",
        "docs/priority_reconsideration_rev0030.md",
        "docs/experiment_matrix_rev0030.md",
        "docs/simulator_rev0030.md",
        "data/rev0030_repeated_opening_counterfactual_summary.json",
        "data/rev0030_repeated_counterfactual_mulligan_summary.json",
        "data/rev0030_repeated_counterfactual_mulligan_model.json",
        "data/rev0030_nochoice_segment_fingerprint_summary.json",
        "data/rev0030_question_bank.json",
        "cpp/muc5_transition_segment.cpp",
        "src/muc5/cpp_segment.py",
        "tests/test_rev0031_cpp_segment.py",
        "scripts/run_rev0031_cpp_segment_check.py",
        "scripts/run_rev0031_repeated_cf_scale.py",
        "docs/cpp_nochoice_segment_checker_rev0031.md",
        "docs/repeated_counterfactual_scale_rev0031.md",
        "docs/cpp_core_plan_rev0031.md",
        "docs/refactor_audit_rev0031.md",
        "docs/priority_reconsideration_rev0031.md",
        "docs/experiment_matrix_rev0031.md",
        "docs/simulator_rev0031.md",
        "data/rev0031_cpp_segment_summary.json",
        "data/rev0031_repeated_cf_scale_summary.json",
        "data/rev0031_question_bank.json",
        "tests/test_rev0032_segment_shadow.py",
        "scripts/run_rev0032_segment_shadow_maprace.py",
        "docs/segment_shadow_maprace_rev0032.md",
        "docs/cpp_segment_batch_refactor_rev0032.md",
        "docs/cpp_core_plan_rev0032.md",
        "docs/refactor_audit_rev0032.md",
        "docs/priority_reconsideration_rev0032.md",
        "docs/experiment_matrix_rev0032.md",
        "docs/simulator_rev0032.md",
        "data/rev0032_segment_shadow_summary.json",
        "data/rev0032_question_bank.json",
        "src/muc5/action_counterfactual.py",
        "tests/test_rev0033_action_counterfactual.py",
        "scripts/run_rev0033_action_counterfactual.py",
        "docs/action_counterfactual_ranker_rev0033.md",
        "docs/cpp_combat_sentinel_fix_rev0033.md",
        "docs/cpp_core_plan_rev0033.md",
        "docs/refactor_audit_rev0033.md",
        "docs/priority_reconsideration_rev0033.md",
        "docs/experiment_matrix_rev0033.md",
        "docs/simulator_rev0033.md",
        "data/rev0033_action_counterfactual_summary.json",
        "data/rev0033_counterfactual_action_ranker_model.json",
        "data/rev0033_question_bank.json",
        "tests/test_rev0034_scaled_actioncf.py",
        "scripts/run_rev0034_scaled_action_counterfactual.py",
        "docs/scaled_action_counterfactual_rev0034.md",
        "docs/action_counterfactual_labelgate_rev0034.md",
        "docs/cpp_core_plan_rev0034.md",
        "docs/refactor_audit_rev0034.md",
        "docs/priority_reconsideration_rev0034.md",
        "docs/experiment_matrix_rev0034.md",
        "docs/simulator_rev0034.md",
        "data/rev0034_scaled_action_counterfactual_summary.json",
        "data/rev0034_counterfactual_action_ranker_model.json",
        "data/rev0034_question_bank.json",
        "src/muc5/action_budget.py",
        "tests/test_rev0035_budgeted_actioncf.py",
        "scripts/run_rev0035_budgeted_action_counterfactual.py",
        "docs/budgeted_action_counterfactual_rev0035.md",
        "docs/action_budget_selector_rev0035.md",
        "docs/budgeted_counterfactual_results_rev0035.md",
        "docs/cpp_core_plan_rev0035.md",
        "docs/refactor_audit_rev0035.md",
        "docs/priority_reconsideration_rev0035.md",
        "docs/experiment_matrix_rev0035.md",
        "docs/simulator_rev0035.md",
        "data/rev0035_budgeted_action_counterfactual_summary.json",
        "data/rev0035_counterfactual_action_ranker_model.json",
        "data/rev0035_question_bank.json",
        "src/muc5/action_racing.py",
        "tests/test_rev0036_adaptive_actioncf.py",
        "scripts/run_rev0036_adaptive_action_counterfactual.py",
        "docs/adaptive_action_counterfactual_rev0036.md",
        "docs/action_racing_rev0036.md",
        "docs/adaptive_racing_results_rev0036.md",
        "docs/cpp_core_plan_rev0036.md",
        "docs/refactor_audit_rev0036.md",
        "docs/priority_reconsideration_rev0036.md",
        "docs/experiment_matrix_rev0036.md",
        "docs/simulator_rev0036.md",
        "data/rev0036_adaptive_action_counterfactual_summary.json",
        "data/rev0036_counterfactual_action_ranker_model.json",
        "data/rev0036_question_bank.json",
        "src/muc5/action_label_compare.py",
        "src/muc5/cpp_segment_benchmark.py",
        "tests/test_rev0037_matched_label_segment.py",
        "scripts/run_rev0037_matched_label_and_segment_benchmark.py",
        "docs/matched_label_audit_rev0037.md",
        "docs/cpp_segment_benchmark_rev0037.md",
        "docs/cpp_core_plan_rev0037.md",
        "docs/refactor_audit_rev0037.md",
        "docs/priority_reconsideration_rev0037.md",
        "docs/experiment_matrix_rev0037.md",
        "docs/simulator_rev0037.md",
        "data/rev0037_matched_label_segment_summary.json",
        "data/rev0037_question_bank.json",
        "src/muc5/action_disagreement.py",
        "tests/test_rev0038_disagreement_screened.py",
        "scripts/run_rev0038_disagreement_screened_counterfactual.py",
        "docs/disagreement_screened_counterfactual_rev0038.md",
        "docs/disagreement_screened_results_rev0038.md",
        "docs/cpp_core_plan_rev0038.md",
        "docs/refactor_audit_rev0038.md",
        "docs/priority_reconsideration_rev0038.md",
        "docs/experiment_matrix_rev0038.md",
        "docs/simulator_rev0038.md",
        "data/rev0038_disagreement_screened_counterfactual_summary.json",
        "data/rev0038_counterfactual_action_ranker_model.json",
        "data/rev0038_question_bank.json",
        "src/muc5/action_screen_compare.py",
        "tests/test_rev0039_matched_screen.py",
        "scripts/run_rev0039_matched_screen_compare.py",
        "docs/matched_screen_comparison_rev0039.md",
        "docs/screenmatch_results_rev0039.md",
        "docs/cpp_core_plan_rev0039.md",
        "docs/refactor_audit_rev0039.md",
        "docs/priority_reconsideration_rev0039.md",
        "docs/experiment_matrix_rev0039.md",
        "docs/simulator_rev0039.md",
        "data/rev0039_matched_screen_summary.json",
        "data/rev0039_question_bank.json",

        "src/muc5/action_hybrid_selector.py",
        "src/muc5/action_hybrid_compare.py",
        "tests/test_rev0040_hybrid_selector.py",
        "scripts/run_rev0040_hybrid_selector_compare.py",
        "docs/hybrid_selector_rev0040.md",
        "docs/hybrid_selector_results_rev0040.md",
        "docs/cpp_core_plan_rev0040.md",
        "docs/refactor_audit_rev0040.md",
        "docs/priority_reconsideration_rev0040.md",
        "docs/experiment_matrix_rev0040.md",
        "docs/simulator_rev0040.md",
        "data/rev0040_hybrid_selector_summary.json",
        "data/rev0040_question_bank.json",

        "src/muc5/action_hard_frame.py",
        "tests/test_rev0041_hard_frame.py",
        "scripts/run_rev0041_hard_frame_selector.py",
        "docs/hard_frame_selector_rev0041.md",
        "docs/hard_frame_results_rev0041.md",
        "docs/cpp_core_plan_rev0041.md",
        "docs/refactor_audit_rev0041.md",
        "docs/priority_reconsideration_rev0041.md",
        "docs/experiment_matrix_rev0041.md",
        "docs/simulator_rev0041.md",
        "data/rev0041_hard_frame_summary.json",
        "data/rev0041_question_bank.json",

        "src/muc5/action_race_audit.py",
        "tests/test_rev0042_hard_racing.py",
        "scripts/run_rev0042_hardframe_racing_audit.py",
        "docs/hard_racing_labeldensity_rev0042.md",
        "docs/label_racing_audit_rev0042.md",
        "docs/cpp_core_plan_rev0042.md",
        "docs/refactor_audit_rev0042.md",
        "docs/priority_reconsideration_rev0042.md",
        "docs/experiment_matrix_rev0042.md",
        "docs/simulator_rev0042.md",
        "data/rev0042_hard_racing_summary.json",
        "data/rev0042_question_bank.json",

        "src/muc5/action_hard_racing.py",
        "tests/test_rev0043_hard_online_racing.py",
        "scripts/run_rev0043_hardframe_online_racer.py",
        "docs/hard_online_racer_rev0043.md",
        "docs/online_racing_results_rev0043.md",
        "docs/cpp_core_plan_rev0043.md",
        "docs/refactor_audit_rev0043.md",
        "docs/priority_reconsideration_rev0043.md",
        "docs/experiment_matrix_rev0043.md",
        "docs/simulator_rev0043.md",
        "data/rev0043_hard_online_racing_summary.json",
        "data/rev0043_question_bank.json",

        "src/muc5/action_margin_screen.py",
        "tests/test_rev0044_margin_screen.py",
        "scripts/run_rev0044_margin_screen_racer.py",
        "docs/margin_screen_rev0044.md",
        "docs/margin_screen_results_rev0044.md",
        "docs/cpp_core_plan_rev0044.md",
        "docs/refactor_audit_rev0044.md",
        "docs/priority_reconsideration_rev0044.md",
        "docs/experiment_matrix_rev0044.md",
        "docs/simulator_rev0044.md",
        "data/rev0044_margin_screen_racing_summary.json",
        "data/rev0044_margin_screen_model.json",
        "data/rev0044_question_bank.json",

        "src/muc5/action_margin_compare.py",
        "tests/test_rev0045_margin_match.py",
        "scripts/run_rev0045_margin_match_queue.py",
        "docs/margin_match_queueaudit_rev0045.md",
        "docs/cpp_core_plan_rev0045.md",
        "docs/refactor_audit_rev0045.md",
        "docs/priority_reconsideration_rev0045.md",
        "docs/experiment_matrix_rev0045.md",
        "docs/simulator_rev0045.md",
        "data/rev0045_margin_match_summary.json",
        "data/rev0045_margin_match_method_summary.csv",
        "data/rev0045_question_bank.json",

        "src/muc5/action_yield_screen.py",
        "tests/test_rev0046_yield_screen.py",
        "scripts/run_rev0046_yield_match_queue.py",
        "docs/yield_screen_rev0046.md",
        "docs/yield_match_results_rev0046.md",
        "docs/cpp_core_plan_rev0046.md",
        "docs/refactor_audit_rev0046.md",
        "docs/priority_reconsideration_rev0046.md",
        "docs/experiment_matrix_rev0046.md",
        "docs/simulator_rev0046.md",
        "data/rev0046_yield_match_summary.json",
        "data/rev0046_yield_match_method_summary.csv",
        "data/rev0046_yield_screen_model.json",
        "data/rev0046_question_bank.json",

        "src/muc5/action_yield_collect.py",
        "tests/test_rev0047_yield_online.py",
        "scripts/run_rev0047_yield_online_counterfactual.py",
        "docs/yield_online_counterfactual_rev0047.md",
        "docs/yield_ranker_policy_rev0047.md",
        "docs/yield_ranker_results_rev0047.md",
        "docs/cpp_core_plan_rev0047.md",
        "docs/refactor_audit_rev0047.md",
        "docs/priority_reconsideration_rev0047.md",
        "docs/experiment_matrix_rev0047.md",
        "docs/simulator_rev0047.md",
        "data/rev0047_yield_online_counterfactual_summary.json",
        "data/rev0047_counterfactual_action_ranker_model.json",
        "data/rev0047_question_bank.json",

        "src/muc5/truncation_rescue.py",
        "tests/test_rev0048_truncation_rescue.py",
        "scripts/run_rev0048_truncation_rescue.py",
        "docs/truncation_rescue_rev0048.md",
        "docs/terminal_gate_results_rev0048.md",
        "docs/cpp_core_plan_rev0048.md",
        "docs/refactor_audit_rev0048.md",
        "docs/priority_reconsideration_rev0048.md",
        "docs/experiment_matrix_rev0048.md",
        "docs/simulator_rev0048.md",
        "data/rev0048_truncation_rescue_summary.json",
        "data/rev0048_question_bank.json",

        "src/muc5/terminal_clean.py",
        "tests/test_rev0049_terminal_clean_yield.py",
        "scripts/run_rev0049_terminal_clean_yieldboost.py",
        "docs/terminal_clean_default_rev0049.md",
        "docs/yieldboost_ranker_rev0049.md",
        "docs/yieldboost_results_rev0049.md",
        "docs/cpp_core_plan_rev0049.md",
        "docs/refactor_audit_rev0049.md",
        "docs/priority_reconsideration_rev0049.md",
        "docs/experiment_matrix_rev0049.md",
        "docs/simulator_rev0049.md",
        "data/rev0049_terminal_clean_yield_summary.json",
        "data/rev0049_counterfactual_action_ranker_model.json",
        "data/rev0049_question_bank.json",

        "src/muc5/terminal_meta.py",
        "tests/test_rev0050_terminal_meta.py",
        "scripts/run_rev0050_terminal_meta_claimgate.py",
        "docs/terminal_meta_claimgate_rev0050.md",
        "docs/terminal_meta_results_rev0050.md",
        "docs/cpp_core_plan_rev0050.md",
        "docs/refactor_audit_rev0050.md",
        "docs/priority_reconsideration_rev0050.md",
        "docs/experiment_matrix_rev0050.md",
        "docs/simulator_rev0050.md",
        "data/rev0050_terminal_meta_summary.json",
        "data/rev0050_question_bank.json",

        "src/muc5/terminal_deep.py",
        "tests/test_rev0051_terminal_deep.py",
        "scripts/run_rev0051_deep_claim_reps.py",
        "docs/deep_claim_reps_rev0051.md",
        "docs/deep_claim_results_rev0051.md",
        "docs/cpp_core_plan_rev0051.md",
        "docs/refactor_audit_rev0051.md",
        "docs/priority_reconsideration_rev0051.md",
        "docs/experiment_matrix_rev0051.md",
        "docs/simulator_rev0051.md",
        "data/rev0051_deep_claim_summary.json",
        "data/rev0051_question_bank.json",

        "src/muc5/terminal_matchup.py",
        "tests/test_rev0052_terminal_matchup.py",
        "scripts/run_rev0052_life_flip_matchups.py",
        "docs/life_flip_matchup_retest_rev0052.md",
        "docs/life_flip_results_rev0052.md",
        "docs/cpp_core_plan_rev0052.md",
        "docs/refactor_audit_rev0052.md",
        "docs/priority_reconsideration_rev0052.md",
        "docs/experiment_matrix_rev0052.md",
        "docs/simulator_rev0052.md",
        "data/rev0052_life_flip_summary.json",
        "data/rev0052_life_flip_retest.csv",
        "data/rev0052_question_bank.json",

        "src/muc5/terminal_cell_confirm.py",
        "tests/test_rev0053_cell_confirm.py",
        "scripts/run_rev0053_cell_confirmation.py",
        "docs/cell_confirmation_rev0053.md",
        "docs/cell_confirmation_results_rev0053.md",
        "docs/cpp_core_plan_rev0053.md",
        "docs/refactor_audit_rev0053.md",
        "docs/priority_reconsideration_rev0053.md",
        "docs/experiment_matrix_rev0053.md",
        "docs/simulator_rev0053.md",
        "data/rev0053_cell_confirm_summary.json",
        "data/rev0053_cell_confirm_confirmation.csv",
        "data/rev0053_question_bank.json",

        "src/muc5/terminal_matchup_claim.py",
        "tests/test_rev0054_matchup_claim.py",
        "scripts/run_rev0054_matchup_claim_dossier.py",
        "docs/matchup_claim_dossier_rev0054.md",
        "docs/matchup_claim_results_rev0054.md",
        "docs/cpp_core_plan_rev0054.md",
        "docs/refactor_audit_rev0054.md",
        "docs/priority_reconsideration_rev0054.md",
        "docs/experiment_matrix_rev0054.md",
        "docs/simulator_rev0054.md",
        "data/rev0054_matchup_claim_summary.json",
        "data/rev0054_matchup_claim_claim_rows.csv",
        "data/rev0054_question_bank.json",

        "src/muc5/terminal_life_cell_claim.py",
        "tests/test_rev0055_life_cell_claim.py",
        "scripts/run_rev0055_life_cell_claims.py",
        "docs/life_cell_claim_dossier_rev0055.md",
        "docs/life_cell_claim_results_rev0055.md",
        "docs/cpp_core_plan_rev0055.md",
        "docs/refactor_audit_rev0055.md",
        "docs/priority_reconsideration_rev0055.md",
        "docs/experiment_matrix_rev0055.md",
        "docs/simulator_rev0055.md",
        "data/rev0055_life_cell_summary.json",
        "data/rev0055_life_cell_cumulative_cells.csv",
        "data/rev0055_question_bank.json",

        "src/muc5/terminal_life_cell_replicate.py",
        "tests/test_rev0056_life_cell_replication.py",
        "scripts/run_rev0056_life_cell_replication.py",
        "docs/life_cell_replication_holdout_rev0056.md",
        "docs/life_cell_replication_results_rev0056.md",
        "docs/cpp_core_plan_rev0056.md",
        "docs/refactor_audit_rev0056.md",
        "docs/priority_reconsideration_rev0056.md",
        "docs/experiment_matrix_rev0056.md",
        "docs/simulator_rev0056.md",
        "data/rev0056_life_cell_replication_summary.json",
        "data/rev0056_life_cell_replication_comparison.csv",
        "data/rev0056_question_bank.json",
    ]
    missing = [path for path in required_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_through_rev0056", not missing, {"missing": missing})

    required_rev0069_files = [
        "src/muc5/population_frontier.py",
        "src/muc5/evidence_index.py",
        "tests/test_rev0069_population_frontier.py",
        "scripts/run_rev0069_population_frontier.py",
        "scripts/run_rev0069_evidence_index.py",
        "docs/population_frontier_rev0069.md",
        "docs/evidence_migration_audit_rev0069.md",
        "docs/refactor_audit_rev0069.md",
        "docs/priority_reconsideration_rev0069.md",
        "docs/experiment_matrix_rev0069.md",
        "data/rev0069_population_frontier_summary.json",
        "data/rev0069_population_frontier_security.csv",
        "data/rev0069_population_frontier_arm_summary.csv",
        "data/rev0069_population_frontier_cpp_transition_sample.csv",
        "data/rev0069_evidence_index.json",
        "data/rev0069_evidence_index.csv",
    ]
    missing_rev0069 = [path for path in required_rev0069_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0069", not missing_rev0069, {"missing": missing_rev0069})

    pop_summary = load_json(ROOT / "data" / "rev0069_population_frontier_summary.json")
    pop_security_rows = count_csv_rows(ROOT / "data" / "rev0069_population_frontier_security.csv") if (ROOT / "data" / "rev0069_population_frontier_security.csv").exists() else -1
    inherited_rows = count_csv_rows(ROOT / "data" / "rev0069_population_frontier_inherited_completeness.csv") if (ROOT / "data" / "rev0069_population_frontier_inherited_completeness.csv").exists() else -1
    add(checks, "rev0069_population_frontier_complete_pilot",
        pop_summary.get("games") == 144
        and pop_summary.get("arms") == 18
        and pop_summary.get("complete_population_cells") == 6
        and pop_summary.get("python_errors") == 0
        and pop_summary.get("truncations") == 0
        and pop_summary.get("cpp_shadow_summary", {}).get("mismatches") == 0
        and pop_security_rows == 6
        and inherited_rows == 6,
        {
            "games": pop_summary.get("games"),
            "arms": pop_summary.get("arms"),
            "complete_cells": pop_summary.get("complete_population_cells"),
            "inherited_complete_before_rev0069": pop_summary.get("inherited_complete_population_cells_before_rev0069_run"),
            "mismatches": pop_summary.get("cpp_shadow_summary", {}).get("mismatches"),
            "security_rows": pop_security_rows,
            "inherited_rows": inherited_rows,
        })
    add(checks, "rev0069_population_frontier_closes_inherited_gap",
        pop_summary.get("inherited_complete_population_cells_before_rev0069_run") == 0
        and pop_summary.get("complete_population_cells") == 6,
        {
            "before": pop_summary.get("inherited_complete_population_cells_before_rev0069_run"),
            "after": pop_summary.get("complete_population_cells"),
        })

    evidence_index = load_json(ROOT / "data" / "rev0069_evidence_index.json")
    evidence_summary = evidence_index.get("summary", {}) if isinstance(evidence_index, dict) else {}
    classes = evidence_summary.get("records_by_retention_class", {}) if isinstance(evidence_summary, dict) else {}
    add(checks, "rev0069_evidence_index_bulk_scan",
        evidence_summary.get("records", 0) >= 70
        and evidence_summary.get("bytes", 0) > 800 * 1024 * 1024
        and classes.get("blocked_by_live_reference", 0) > 0
        and classes.get("evidence_archive_candidate", 0) > 0,
        {
            "records": evidence_summary.get("records"),
            "bytes_mib": evidence_summary.get("bytes_mib"),
            "retention_classes": classes,
        })

    required_rev0070_files = [
        "scripts/run_rev0070_population_precision.py",
        "scripts/run_rev0070_evidence_index.py",
        "tests/test_rev0070_population_precision.py",
        "docs/population_precision_rev0070.md",
        "docs/evidence_bridge_refactor_rev0070.md",
        "docs/refactor_audit_rev0070.md",
        "docs/priority_reconsideration_rev0070.md",
        "docs/experiment_matrix_rev0070.md",
        "data/rev0070_population_precision_summary.json",
        "data/rev0070_population_precision_gate.csv",
        "data/rev0070_population_precision_security.csv",
        "data/rev0070_population_precision_arm_summary.csv",
        "data/rev0070_population_precision_cpp_transition_sample.csv",
        "data/rev0070_evidence_index.json",
        "data/rev0070_evidence_index.csv",
    ]
    missing_rev0070 = [path for path in required_rev0070_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0070", not missing_rev0070, {"missing": missing_rev0070})

    precision_summary = load_json(ROOT / "data" / "rev0070_population_precision_summary.json")
    precision_gate_rows = count_csv_rows(ROOT / "data" / "rev0070_population_precision_gate.csv") if (ROOT / "data" / "rev0070_population_precision_gate.csv").exists() else -1
    precision_security_rows = count_csv_rows(ROOT / "data" / "rev0070_population_precision_security.csv") if (ROOT / "data" / "rev0070_population_precision_security.csv").exists() else -1
    gate_counts = precision_summary.get("precision_gate_summary", {}).get("status_counts", {}) if isinstance(precision_summary.get("precision_gate_summary", {}), dict) else {}
    add(checks, "rev0070_population_precision_gate_fail_closed",
        precision_summary.get("games") == 288
        and precision_summary.get("arms") == 18
        and precision_summary.get("complete_population_cells") == 6
        and precision_summary.get("min_games_per_population_cell") == 8
        and precision_summary.get("precision_gate_summary", {}).get("gate_passed_cells") == 0
        and gate_counts.get("precision_target_not_met") == 6
        and precision_summary.get("python_errors") == 0
        and precision_summary.get("truncations") == 0
        and precision_summary.get("cpp_shadow_summary", {}).get("mismatches") == 0
        and precision_summary.get("cpp_shadow_records_checked") == 30000
        and precision_summary.get("raw_cpp_transition_rows_generated_but_not_shipped", 0) > 50000
        and precision_gate_rows == 6
        and precision_security_rows == 6,
        {
            "games": precision_summary.get("games"),
            "complete_cells": precision_summary.get("complete_population_cells"),
            "min_games": precision_summary.get("min_games_per_population_cell"),
            "gate_counts": gate_counts,
            "gate_passed": precision_summary.get("precision_gate_summary", {}).get("gate_passed_cells") if isinstance(precision_summary.get("precision_gate_summary", {}), dict) else None,
            "cpp_checked": precision_summary.get("cpp_shadow_records_checked"),
            "raw_transitions": precision_summary.get("raw_cpp_transition_rows_generated_but_not_shipped"),
            "gate_rows": precision_gate_rows,
            "security_rows": precision_security_rows,
        })

    evidence70 = load_json(ROOT / "data" / "rev0070_evidence_index.json")
    evidence70_summary = evidence70.get("summary", {}) if isinstance(evidence70, dict) else {}
    classes70 = evidence70_summary.get("records_by_retention_class", {}) if isinstance(evidence70_summary, dict) else {}
    add(checks, "rev0070_evidence_index_active_vs_historical_refs",
        evidence70_summary.get("records", 0) >= 78
        and evidence70_summary.get("bytes", 0) > 800 * 1024 * 1024
        and classes70.get("blocked_by_live_reference", 999) < classes.get("blocked_by_live_reference", 0)
        and classes70.get("blocked_missing_compact_derivative", 0) > 0
        and evidence70_summary.get("historical_reference_edges", 0) > 0
        and evidence70_summary.get("active_reference_edges", 0) > 0,
        {
            "records": evidence70_summary.get("records"),
            "bytes_mib": evidence70_summary.get("bytes_mib"),
            "rev0069_retention_classes": classes,
            "rev0070_retention_classes": classes70,
            "active_reference_edges": evidence70_summary.get("active_reference_edges"),
            "historical_reference_edges": evidence70_summary.get("historical_reference_edges"),
        })


    required_rev0071_files = [
        "src/muc5/evidence_derivatives.py",
        "scripts/run_rev0071_population_power_floor.py",
        "scripts/run_rev0071_evidence_derivatives.py",
        "scripts/run_rev0071_evidence_index.py",
        "tests/test_rev0071_powerfloor_derivatives.py",
        "docs/population_power_floor_rev0071.md",
        "docs/evidence_derivative_bridge_rev0071.md",
        "docs/refactor_audit_rev0071.md",
        "docs/priority_reconsideration_rev0071.md",
        "docs/experiment_matrix_rev0071.md",
        "data/rev0071_population_power_floor_summary.json",
        "data/rev0071_population_power_floor_gate.csv",
        "data/rev0071_population_power_floor_security.csv",
        "data/rev0071_population_power_floor_pooled_arm_summary.csv",
        "data/rev0071_evidence_derivatives_summary.json",
        "data/rev0021_ranker_summary.json",
        "data/rev0021_cpp_batch_summary.json",
        "data/rev0071_evidence_index.json",
        "data/rev0071_evidence_index.csv",
    ]
    missing_rev0071 = [path for path in required_rev0071_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0071", not missing_rev0071, {"missing": missing_rev0071})

    power71 = load_json(ROOT / "data" / "rev0071_population_power_floor_summary.json")
    power_gate_rows = count_csv_rows(ROOT / "data" / "rev0071_population_power_floor_gate.csv") if (ROOT / "data" / "rev0071_population_power_floor_gate.csv").exists() else -1
    power_security_rows = count_csv_rows(ROOT / "data" / "rev0071_population_power_floor_security.csv") if (ROOT / "data" / "rev0071_population_power_floor_security.csv").exists() else -1
    power_counts = power71.get("precision_gate_summary", {}).get("status_counts", {}) if isinstance(power71.get("precision_gate_summary", {}), dict) else {}
    add(checks, "rev0071_population_power_floor_quarantines_after_precision",
        power71.get("source_population_games") == 432
        and power71.get("source_cpp_checked_transitions") == 54533
        and power71.get("pooled_gate_rows") == 3
        and power71.get("min_games_per_population_cell_observed", 0) >= 24
        and float(power71.get("max_ci_width_observed", 999.0)) <= 0.60
        and power71.get("precision_gate_summary", {}).get("gate_passed_cells") == 0
        and power_counts.get("quarantined_low_security_floor") == 3
        and power_counts.get("precision_target_not_met", 0) == 0
        and power_gate_rows == 3
        and power_security_rows == 3,
        {
            "source_games": power71.get("source_population_games"),
            "source_cpp_checked": power71.get("source_cpp_checked_transitions"),
            "pooled_gate_rows": power71.get("pooled_gate_rows"),
            "min_games": power71.get("min_games_per_population_cell_observed"),
            "max_ci_width": power71.get("max_ci_width_observed"),
            "gate_counts": power_counts,
            "gate_rows": power_gate_rows,
            "security_rows": power_security_rows,
        })

    derivatives71 = load_json(ROOT / "data" / "rev0071_evidence_derivatives_summary.json")
    evidence71 = load_json(ROOT / "data" / "rev0071_evidence_index.json")
    evidence71_summary = evidence71.get("summary", {}) if isinstance(evidence71, dict) else {}
    classes71 = evidence71_summary.get("records_by_retention_class", {}) if isinstance(evidence71_summary, dict) else {}
    add(checks, "rev0071_evidence_derivatives_unlock_missing_blockers",
        derivatives71.get("source_bytes_profiled", 0) > 16 * 1024 * 1024
        and derivatives71.get("ranker_rows") == 33184
        and derivatives71.get("trace_cpp_mismatch_rows") == 0
        and classes71.get("blocked_missing_compact_derivative", 0) == 0
        and classes71.get("evidence_archive_candidate", 0) >= 5
        and classes71.get("blocked_by_live_reference") == classes70.get("blocked_by_live_reference"),
        {
            "derivatives": derivatives71,
            "rev0070_retention_classes": classes70,
            "rev0071_retention_classes": classes71,
            "archive_candidate_bytes": evidence71_summary.get("bytes_by_retention_class", {}).get("evidence_archive_candidate") if isinstance(evidence71_summary.get("bytes_by_retention_class", {}), dict) else None,
        })

    required_rev0072_files = [
        "src/muc5/archive_contract.py",
        "src/muc5/evidence_tiering.py",
        "scripts/build_linked_archive.py",
        "scripts/audit_linked_archive.py",
        "scripts/run_rev0072_evidence_tiering.py",
        "scripts/materialize_evidence.py",
        "tests/test_rev0072_archive_tiering.py",
        "docs/archive_and_evidence_tiering_rev0072.md",
        "docs/refactor_audit_rev0072.md",
        "data/rev0072_evidence_tiering_catalog.json",
        "data/rev0072_evidence_bundle_audit.json",
    ]
    missing_rev0072 = [path for path in required_rev0072_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0072", not missing_rev0072, {"missing": missing_rev0072})

    tier72_path = ROOT / "data" / "rev0072_evidence_tiering_catalog.json"
    tier72 = load_tiering_catalog(tier72_path) if tier72_path.exists() else {}
    tier72_summary = tier72.get("summary", {}) if isinstance(tier72, dict) else {}
    tier72_bundle = tier72.get("bundle", {}) if isinstance(tier72, dict) else {}
    tier72_core = validate_core_tiering(ROOT, tier72) if tier72 else {"passed": False, "errors": ["missing catalog"]}
    bundle72_audit = load_json(ROOT / "data" / "rev0072_evidence_bundle_audit.json")
    add(checks, "rev0072_evidence_tiering_core_is_lean_and_reversible",
        tier72_summary.get("records") == 78
        and tier72_summary.get("hot_core_records") == 6
        and tier72_summary.get("cold_sidecar_records") == 72
        and tier72_summary.get("cold_sidecar_bytes", 0) > 790 * 1024 * 1024
        and tier72_core.get("passed") is True
        and tier72_core.get("hot_present") == 6
        and tier72_core.get("cold_absent") == 72,
        {
            "summary": tier72_summary,
            "core_validation": tier72_core,
        })
    add(checks, "rev0072_evidence_bundle_is_content_verified",
        bundle72_audit.get("passed") is True
        and bundle72_audit.get("expected_records") == 72
        and bundle72_audit.get("checked_records") == 72
        and bundle72_audit.get("bundle_sha256") == tier72_bundle.get("sha256")
        and bundle72_audit.get("bundle_bytes") == tier72_bundle.get("bytes")
        and 0 < int(bundle72_audit.get("bundle_bytes", 0)) < 64 * 1024 * 1024,
        {
            "bundle_audit": bundle72_audit,
            "catalog_bundle": tier72_bundle,
        })

    required_rev0073_files = [
        "scripts/run_rev0073_pool_robustness.py",
        "tests/test_rev0073_exactmaximin_poolrobustness.py",
        "docs/population_pool_robustness_rev0073.md",
        "docs/refactor_audit_rev0073.md",
        "data/rev0073_population_pool_robustness_summary.json",
        "data/rev0073_population_pool_robustness_gate.csv",
        "data/rev0073_population_pool_robustness_security.csv",
        "data/rev0073_population_pool_robustness_pooled_arm_summary.csv",
        "data/rev0073_evidence_tiering_catalog.json",
        "data/rev0073_evidence_bundle_audit.json",
    ]
    missing_rev0073 = [path for path in required_rev0073_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0073", not missing_rev0073, {"missing": missing_rev0073})

    robust73 = load_json(ROOT / "data" / "rev0073_population_pool_robustness_summary.json")
    robust73_gate_rows = count_csv_rows(ROOT / "data" / "rev0073_population_pool_robustness_gate.csv") if (ROOT / "data" / "rev0073_population_pool_robustness_gate.csv").exists() else -1
    robust73_security_rows = count_csv_rows(ROOT / "data" / "rev0073_population_pool_robustness_security.csv") if (ROOT / "data" / "rev0073_population_pool_robustness_security.csv").exists() else -1
    robust73_counts = robust73.get("gate_summary", {}).get("status_counts", {}) if isinstance(robust73.get("gate_summary", {}), dict) else {}
    add(checks, "rev0073_population_robustness_quarantines_every_cut_with_exact_solver",
        robust73.get("source_population_games") == 432
        and robust73.get("evaluation_count") == 15
        and robust73.get("gate_rows") == 15
        and robust73_gate_rows == 15
        and robust73_security_rows == 15
        and robust73.get("exact_gate_rows") == 15
        and robust73.get("mixed_solution_methods") == ["exact_two_row"]
        and robust73.get("gate_passed_cells") == 0
        and robust73_counts.get("quarantined_low_security_floor") == 15
        and robust73.get("precision_target_not_met_cells") == 0
        and robust73.get("underpowered_min_games_cells") == 0
        and float(robust73.get("max_ci_width_observed", 999.0)) <= 0.60,
        {
            "summary": robust73,
            "gate_rows": robust73_gate_rows,
            "security_rows": robust73_security_rows,
            "status_counts": robust73_counts,
        })

    tier73_path = find_tiering_catalog(ROOT)
    tier73 = load_tiering_catalog(tier73_path) if tier73_path is not None else {}
    tier73_summary = tier73.get("summary", {}) if isinstance(tier73, dict) else {}
    tier73_core = validate_core_tiering(ROOT, tier73) if tier73 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0073_evidence_catalog_discovery_prefers_latest_revision_catalog",
        tier73_path is not None
        and tier73_path.name.endswith("_evidence_tiering_catalog.json")
        and tier73_path.name >= "rev0073_evidence_tiering_catalog.json"
        and tier73.get("source_cube") == ROOT.name
        and tier73_summary.get("cold_sidecar_records") == 72
        and tier73_core.get("passed") is True,
        {
            "catalog": tier73_path.name if tier73_path is not None else None,
            "source_cube": tier73.get("source_cube") if isinstance(tier73, dict) else None,
            "summary": tier73_summary,
            "core_validation": tier73_core,
        })

    required_rev0074_files = [
        "src/muc5/population_lineage.py",
        "scripts/run_rev0074_population_lineage_audit.py",
        "tests/test_rev0074_population_lineage.py",
        "docs/population_lineage_audit_rev0074.md",
        "docs/refactor_audit_rev0074.md",
        "docs/priority_reconsideration_rev0074.md",
        "docs/experiment_matrix_rev0074.md",
        "data/rev0074_population_lineage_audit_summary.json",
        "data/rev0074_population_lineage_index.csv",
        "data/rev0074_population_raw_recomputed_arm_summary.csv",
        "data/rev0074_population_source_summary_comparison_mismatches.csv",
        "data/rev0074_population_raw_fine_security.csv",
        "data/rev0074_population_raw_fine_gate.csv",
        "data/rev0074_evidence_tiering_catalog.json",
        "data/rev0074_evidence_bundle_audit.json",
    ]
    missing_rev0074 = [path for path in required_rev0074_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0074", not missing_rev0074, {"missing": missing_rev0074})

    lineage74 = load_json(ROOT / "data" / "rev0074_population_lineage_audit_summary.json")
    raw_checks74 = lineage74.get("raw_lineage_checks", {}) if isinstance(lineage74.get("raw_lineage_checks", {}), dict) else {}
    fine_counts74 = lineage74.get("fine_gate_status_counts", {}) if isinstance(lineage74.get("fine_gate_status_counts", {}), dict) else {}
    mismatch_rows74 = count_csv_rows(ROOT / "data" / "rev0074_population_source_summary_comparison_mismatches.csv") if (ROOT / "data" / "rev0074_population_source_summary_comparison_mismatches.csv").exists() else -1
    lineage_index_rows74 = count_csv_rows(ROOT / "data" / "rev0074_population_lineage_index.csv") if (ROOT / "data" / "rev0074_population_lineage_index.csv").exists() else -1
    recomputed_rows74 = count_csv_rows(ROOT / "data" / "rev0074_population_raw_recomputed_arm_summary.csv") if (ROOT / "data" / "rev0074_population_raw_recomputed_arm_summary.csv").exists() else -1
    fine_gate_rows74 = count_csv_rows(ROOT / "data" / "rev0074_population_raw_fine_gate.csv") if (ROOT / "data" / "rev0074_population_raw_fine_gate.csv").exists() else -1
    add(checks, "rev0074_population_raw_lineage_recomputes_source_summaries",
        lineage74.get("raw_games") == 432
        and lineage74.get("source_summary_rows") == 72
        and lineage74.get("recomputed_arm_summary_rows") == 72
        and lineage74.get("summary_mismatch_rows") == 0
        and mismatch_rows74 == 0
        and lineage_index_rows74 == 432
        and recomputed_rows74 == 72
        and raw_checks74.get("passed") is True
        and raw_checks74.get("seed_duplicates") == 0
        and raw_checks74.get("transition_seed_duplicates") == 0
        and raw_checks74.get("agent_seed_duplicates") == 0
        and raw_checks74.get("truncations") == 0
        and raw_checks74.get("nonterminal_clean_status_rows") == 0
        and raw_checks74.get("imbalanced_groups") == 0,
        {
            "summary": lineage74,
            "raw_checks": raw_checks74,
            "mismatch_rows": mismatch_rows74,
            "lineage_index_rows": lineage_index_rows74,
            "recomputed_rows": recomputed_rows74,
        })
    add(checks, "rev0074_population_lineage_uses_source_qualified_game_ids",
        raw_checks74.get("local_cpp_shadow_game_id_duplicates") == 1
        and raw_checks74.get("source_qualified_game_id_duplicates") == 0,
        {
            "local_cpp_shadow_game_id_duplicates": raw_checks74.get("local_cpp_shadow_game_id_duplicates"),
            "source_qualified_game_id_duplicates": raw_checks74.get("source_qualified_game_id_duplicates"),
        })
    add(checks, "rev0074_raw_fine_strata_are_complete_but_not_promotable",
        lineage74.get("fine_population_cells") == 12
        and lineage74.get("fine_complete_cells") == 12
        and lineage74.get("fine_gate_rows") == 12
        and fine_gate_rows74 == 12
        and lineage74.get("fine_gate_passed_cells") == 0
        and fine_counts74.get("underpowered_min_games") == 12
        and lineage74.get("fine_point_floor_ge_0_50_rows") == 4
        and lineage74.get("fine_high_point_floor_max_min_games") == 8,
        {
            "fine_gate_status_counts": fine_counts74,
            "fine_gate_rows": fine_gate_rows74,
            "fine_best_point_floor": lineage74.get("fine_best_point_floor"),
            "fine_high_point_floor_max_min_games": lineage74.get("fine_high_point_floor_max_min_games"),
        })

    tier74_path = find_tiering_catalog(ROOT)
    tier74 = load_tiering_catalog(tier74_path) if tier74_path is not None else {}
    tier74_summary = tier74.get("summary", {}) if isinstance(tier74, dict) else {}
    tier74_core = validate_core_tiering(ROOT, tier74) if tier74 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0074_evidence_catalog_is_latest_and_core_stays_lean",
        tier74_path is not None
        and tier74_path.name >= "rev0074_evidence_tiering_catalog.json"
        and tier74.get("source_cube") == ROOT.name
        and tier74_summary.get("hot_core_records") == 6
        and tier74_summary.get("cold_sidecar_records") == 72
        and tier74_core.get("passed") is True,
        {
            "catalog": tier74_path.name if tier74_path is not None else None,
            "source_cube": tier74.get("source_cube") if isinstance(tier74, dict) else None,
            "summary": tier74_summary,
            "core_validation": tier74_core,
        })


    required_rev0075_files = [
        "src/muc5/population_stratum_challenge.py",
        "scripts/run_rev0075_stratum_challenge.py",
        "scripts/run_rev0075_artifact_audit.py",
        "tests/test_rev0075_stratum_challenge.py",
        "docs/stratum_challenge_rev0075.md",
        "docs/refactor_audit_rev0075.md",
        "docs/priority_reconsideration_rev0075.md",
        "docs/experiment_matrix_rev0075.md",
        "data/rev0075_stratum_challenge_summary.json",
        "data/rev0075_stratum_challenge_games.csv",
        "data/rev0075_stratum_challenge_arm_summary.csv",
        "data/rev0075_stratum_challenge_pre_gate.csv",
        "data/rev0075_stratum_challenge_post_gate.csv",
        "data/rev0075_stratum_challenge_comparison.csv",
        "data/rev0075_stratum_challenge_cpp_transition_sample.csv",
        "data/rev0075_stratum_challenge_selected_cells.json",
        "data/rev0075_artifact_audit.json",
        "data/rev0075_evidence_tiering_catalog.json",
        "data/rev0075_evidence_bundle_audit.json",
    ]
    missing_rev0075 = [path for path in required_rev0075_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0075", not missing_rev0075, {"missing": missing_rev0075})

    challenge75 = load_json(ROOT / "data" / "rev0075_stratum_challenge_summary.json")
    pre75 = challenge75.get("pre_gate_summary", {}) if isinstance(challenge75.get("pre_gate_summary", {}), dict) else {}
    post75 = challenge75.get("post_gate_summary", {}) if isinstance(challenge75.get("post_gate_summary", {}), dict) else {}
    post_counts75 = post75.get("status_counts", {}) if isinstance(post75.get("status_counts", {}), dict) else {}
    pre_counts75 = pre75.get("status_counts", {}) if isinstance(pre75.get("status_counts", {}), dict) else {}
    selected75 = challenge75.get("selected_cells", []) if isinstance(challenge75.get("selected_cells", []), list) else []
    post_gate_rows75 = count_csv_rows(ROOT / "data" / "rev0075_stratum_challenge_post_gate.csv") if (ROOT / "data" / "rev0075_stratum_challenge_post_gate.csv").exists() else -1
    pre_gate_rows75 = count_csv_rows(ROOT / "data" / "rev0075_stratum_challenge_pre_gate.csv") if (ROOT / "data" / "rev0075_stratum_challenge_pre_gate.csv").exists() else -1
    comparison_rows75 = count_csv_rows(ROOT / "data" / "rev0075_stratum_challenge_comparison.csv") if (ROOT / "data" / "rev0075_stratum_challenge_comparison.csv").exists() else -1
    games_rows75 = count_csv_rows(ROOT / "data" / "rev0075_stratum_challenge_games.csv") if (ROOT / "data" / "rev0075_stratum_challenge_games.csv").exists() else -1
    cpp_sample_rows75 = count_csv_rows(ROOT / "data" / "rev0075_stratum_challenge_cpp_transition_sample.csv") if (ROOT / "data" / "rev0075_stratum_challenge_cpp_transition_sample.csv").exists() else -1
    cpp75 = challenge75.get("cpp_shadow_summary", {}) if isinstance(challenge75.get("cpp_shadow_summary", {}), dict) else {}
    add(checks, "rev0075_targeted_stratum_challenge_turns_underpowered_cells_into_low_floor_quarantine",
        challenge75.get("games") == 288
        and games_rows75 == 288
        and len(selected75) == 3
        and pre_gate_rows75 == 3
        and post_gate_rows75 == 3
        and comparison_rows75 == 3
        and pre_counts75.get("underpowered_min_games") == 3
        and post_counts75.get("quarantined_low_security_floor") == 3
        and post75.get("gate_passed_cells") == 0
        and float(post75.get("max_ci_width_observed", 999)) <= 0.60
        and float(post75.get("best_conservative_pure_security_lcb", 999)) < 0.50
        and int(challenge75.get("raw_cpp_transition_rows_generated_but_not_shipped", 0)) == 52956
        and int(challenge75.get("cpp_shadow_records_checked", 0)) == 30000
        and int(cpp75.get("mismatches", -1)) == 0
        and int(challenge75.get("truncations", -1)) == 0,
        {
            "selected_cells": selected75,
            "pre_gate_summary": pre75,
            "post_gate_summary": post75,
            "pre_gate_rows": pre_gate_rows75,
            "post_gate_rows": post_gate_rows75,
            "comparison_rows": comparison_rows75,
            "games_rows": games_rows75,
            "cpp_sample_rows": cpp_sample_rows75,
            "cpp_shadow_summary": cpp75,
        })

    gate75_rows = []
    gate75_path = ROOT / "data" / "rev0075_stratum_challenge_post_gate.csv"
    if gate75_path.exists():
        with gate75_path.open(newline="", encoding="utf-8") as handle:
            gate75_rows = list(csv.DictReader(handle))
    csv_gate_summary75 = summarize_population_precision_gate(gate75_rows)
    add(checks, "rev0075_gate_summary_is_csv_bool_safe_and_context_normalized",
        csv_gate_summary75.get("gate_passed_cells") == 0
        and csv_gate_summary75.get("rows") == 3
        and post_gate_rows75 == len(selected75),
        {
            "csv_gate_summary": csv_gate_summary75,
            "post_gate_rows": post_gate_rows75,
            "selected_cells": len(selected75),
        })

    artifact75 = load_json(ROOT / "data" / "rev0075_artifact_audit.json")
    add(checks, "rev0075_artifact_audit_keeps_raw_bulk_out_of_core",
        artifact75.get("passed") is True
        and not artifact75.get("forbidden_present")
        and not artifact75.get("row_limit_violations")
        and cpp_sample_rows75 == 360,
        {"artifact_audit": artifact75, "cpp_sample_rows": cpp_sample_rows75})

    tier75_path = ROOT / "data" / "rev0075_evidence_tiering_catalog.json"
    tier75 = load_tiering_catalog(tier75_path) if tier75_path.exists() else {}
    tier75_summary = tier75.get("summary", {}) if isinstance(tier75, dict) else {}
    tier75_core = validate_core_tiering(ROOT, tier75) if tier75 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0075_evidence_catalog_remains_valid_after_later_carry_forward",
        tier75_path.exists()
        and tier75.get("source_cube") == "MUCloudtainer-rev0075-2026.06.18.02.15-stratumchallenge-boolgate"
        and tier75_summary.get("hot_core_records") == 6
        and tier75_summary.get("cold_sidecar_records") == 72
        and tier75_core.get("passed") is True,
        {
            "catalog": tier75_path.name if tier75_path.exists() else None,
            "source_cube": tier75.get("source_cube") if isinstance(tier75, dict) else None,
            "summary": tier75_summary,
            "core_validation": tier75_core,
        })


    required_rev0076_files = [
        "src/muc5/population_score_audit.py",
        "src/muc5/terminal_mechanisms.py",
        "src/muc5/threat_response.py",
        "scripts/run_rev0076_score_orientation_audit.py",
        "scripts/run_rev0076_artifact_audit.py",
        "tests/test_rev0076_score_orientation.py",
        "docs/score_orientation_audit_rev0076.md",
        "docs/refactor_audit_rev0076.md",
        "docs/priority_reconsideration_rev0076.md",
        "docs/experiment_matrix_rev0076.md",
        "data/rev0076_score_orientation_summary.json",
        "data/rev0076_score_orientation_by_source.csv",
        "data/rev0076_score_orientation_mismatches.csv",
        "data/rev0076_artifact_audit.json",
        "data/rev0076_evidence_tiering_catalog.json",
        "data/rev0076_evidence_bundle_audit.json",
    ]
    missing_rev0076 = [path for path in required_rev0076_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0076", not missing_rev0076, {"missing": missing_rev0076})

    score76 = load_json(ROOT / "data" / "rev0076_score_orientation_summary.json")
    mismatch_rows76 = count_csv_rows(ROOT / "data" / "rev0076_score_orientation_mismatches.csv") if (ROOT / "data" / "rev0076_score_orientation_mismatches.csv").exists() else -1
    by_source_rows76 = count_csv_rows(ROOT / "data" / "rev0076_score_orientation_by_source.csv") if (ROOT / "data" / "rev0076_score_orientation_by_source.csv").exists() else -1
    target_seats76 = score76.get("target_seat_counts", {}) if isinstance(score76.get("target_seat_counts", {}), dict) else {}
    mechanisms76 = score76.get("expected_terminal_mechanism_counts", {}) if isinstance(score76.get("expected_terminal_mechanism_counts", {}), dict) else {}
    add(checks, "rev0076_score_orientation_audits_all_live_population_raw_games",
        score76.get("passed") is True
        and score76.get("rows") == 720
        and score76.get("sources") == 3
        and score76.get("mismatches") == 0
        and mismatch_rows76 == 0
        and by_source_rows76 == 3
        and target_seats76.get("0") == 360
        and target_seats76.get("1") == 360
        and mechanisms76.get("library_out") == 466
        and mechanisms76.get("life_total") == 254,
        {
            "summary": score76,
            "mismatch_rows": mismatch_rows76,
            "by_source_rows": by_source_rows76,
        })

    artifact76 = load_json(ROOT / "data" / "rev0076_artifact_audit.json")
    add(checks, "rev0076_artifact_audit_keeps_score_orientation_audit_compact",
        artifact76.get("passed") is True
        and not artifact76.get("forbidden_present")
        and not artifact76.get("row_limit_violations")
        and mismatch_rows76 == 0,
        {"artifact_audit": artifact76, "mismatch_rows": mismatch_rows76})

    tier76_path = ROOT / "data" / "rev0076_evidence_tiering_catalog.json"
    tier76 = load_tiering_catalog(tier76_path) if tier76_path.exists() else {}
    tier76_summary = tier76.get("summary", {}) if isinstance(tier76, dict) else {}
    tier76_core = validate_core_tiering(ROOT, tier76) if tier76 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0076_evidence_catalog_remains_valid_after_later_carry_forward",
        tier76_path.exists()
        and tier76.get("source_cube") == "MUCloudtainer-rev0076-2026.06.18.02.54-scoreorientation-terminalaudit"
        and tier76_summary.get("hot_core_records") == 6
        and tier76_summary.get("cold_sidecar_records") == 72
        and tier76_core.get("passed") is True,
        {
            "catalog_path": tier76_path.name if tier76_path.exists() else None,
            "source_cube": tier76.get("source_cube") if isinstance(tier76, dict) else None,
            "summary": tier76_summary,
            "core_validation": tier76_core,
        })


    required_rev0077_files = [
        "src/muc5/population_sampling.py",
        "scripts/run_rev0077_adaptive_pooling_guard.py",
        "scripts/run_rev0077_artifact_audit.py",
        "tests/test_rev0077_adaptive_pooling.py",
        "docs/adaptive_pooling_guard_rev0077.md",
        "docs/refactor_audit_rev0077.md",
        "docs/priority_reconsideration_rev0077.md",
        "docs/experiment_matrix_rev0077.md",
        "data/rev0077_adaptive_pooling_guard_summary.json",
        "data/rev0077_sampling_frame_summary.csv",
        "data/rev0077_population_pool_eligible_arm_summary.csv",
        "data/rev0077_population_pool_eligible_gate.csv",
        "data/rev0077_population_pool_naive_adaptive_gate.csv",
        "data/rev0077_population_pool_life_gate_comparison.csv",
        "data/rev0077_population_pool_guard_comparison.csv",
        "data/rev0077_artifact_audit.json",
        "data/rev0077_evidence_tiering_catalog.json",
        "data/rev0077_evidence_bundle_audit.json",
    ]
    missing_rev0077 = [path for path in required_rev0077_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0077", not missing_rev0077, {"missing": missing_rev0077})

    adaptive77 = load_json(ROOT / "data" / "rev0077_adaptive_pooling_guard_summary.json")
    guard77 = adaptive77.get("sampling_guard", {}) if isinstance(adaptive77.get("sampling_guard", {}), dict) else {}
    eligible77 = adaptive77.get("eligible_global_gate_summary", {}) if isinstance(adaptive77.get("eligible_global_gate_summary", {}), dict) else {}
    naive77 = adaptive77.get("naive_adaptive_global_gate_summary", {}) if isinstance(adaptive77.get("naive_adaptive_global_gate_summary", {}), dict) else {}
    frame_rows77 = count_csv_rows(ROOT / "data" / "rev0077_sampling_frame_summary.csv") if (ROOT / "data" / "rev0077_sampling_frame_summary.csv").exists() else -1
    eligible_arm_rows77 = count_csv_rows(ROOT / "data" / "rev0077_population_pool_eligible_arm_summary.csv") if (ROOT / "data" / "rev0077_population_pool_eligible_arm_summary.csv").exists() else -1
    eligible_gate_rows77 = count_csv_rows(ROOT / "data" / "rev0077_population_pool_eligible_gate.csv") if (ROOT / "data" / "rev0077_population_pool_eligible_gate.csv").exists() else -1
    naive_gate_rows77 = count_csv_rows(ROOT / "data" / "rev0077_population_pool_naive_adaptive_gate.csv") if (ROOT / "data" / "rev0077_population_pool_naive_adaptive_gate.csv").exists() else -1
    life_gate_rows77 = count_csv_rows(ROOT / "data" / "rev0077_population_pool_life_gate_comparison.csv") if (ROOT / "data" / "rev0077_population_pool_life_gate_comparison.csv").exists() else -1
    comparison_rows77 = count_csv_rows(ROOT / "data" / "rev0077_population_pool_guard_comparison.csv") if (ROOT / "data" / "rev0077_population_pool_guard_comparison.csv").exists() else -1
    add(checks, "rev0077_adaptive_pooling_guard_excludes_targeted_challenge_from_broad_pool",
        guard77.get("global_pool_guard_passed") is True
        and guard77.get("eligible_rows") == 72
        and guard77.get("eligible_summary_game_rows") == 432
        and guard77.get("ineligible_rows") == 18
        and guard77.get("ineligible_summary_game_rows") == 288
        and guard77.get("unknown_sampling_rows") == 0
        and adaptive77.get("summary_rows_total") == 90
        and adaptive77.get("summary_rows_global_pool_eligible") == 72
        and adaptive77.get("summary_rows_excluded_from_global_pool") == 18,
        {"summary": adaptive77, "frame_rows": frame_rows77})

    add(checks, "rev0077_guarded_pool_quarantines_without_adaptive_contamination",
        eligible77.get("gate_passed_cells") == 0
        and eligible77.get("status_counts", {}).get("quarantined_low_security_floor") == 1
        and naive77.get("gate_passed_cells") == 0
        and naive77.get("status_counts", {}).get("quarantined_low_security_floor") == 1
        and float(adaptive77.get("naive_minus_eligible_global_lcb_delta", 0.0)) > 0.10
        and float(adaptive77.get("naive_minus_eligible_global_mean_floor_delta", 0.0)) > 0.09
        and eligible_arm_rows77 == 6
        and eligible_gate_rows77 == 1
        and naive_gate_rows77 == 1
        and life_gate_rows77 == 4
        and comparison_rows77 == 4,
        {
            "eligible_gate": eligible77,
            "naive_gate": naive77,
            "lcb_delta": adaptive77.get("naive_minus_eligible_global_lcb_delta"),
            "mean_delta": adaptive77.get("naive_minus_eligible_global_mean_floor_delta"),
            "rows": {
                "eligible_arm": eligible_arm_rows77,
                "eligible_gate": eligible_gate_rows77,
                "naive_gate": naive_gate_rows77,
                "life_gate": life_gate_rows77,
                "comparison": comparison_rows77,
            },
        })

    artifact77 = load_json(ROOT / "data" / "rev0077_artifact_audit.json")
    add(checks, "rev0077_artifact_audit_keeps_adaptive_pooling_guard_compact",
        artifact77.get("passed") is True
        and not artifact77.get("forbidden_present")
        and not artifact77.get("row_limit_violations")
        and frame_rows77 == 3,
        {"artifact_audit": artifact77})

    tier77_path = ROOT / "data" / "rev0077_evidence_tiering_catalog.json"
    tier77 = load_tiering_catalog(tier77_path) if tier77_path.exists() else {}
    tier77_summary = tier77.get("summary", {}) if isinstance(tier77, dict) else {}
    tier77_core = validate_core_tiering(ROOT, tier77) if tier77 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0077_evidence_catalog_remains_valid_after_later_carry_forward",
        tier77_path.exists()
        and tier77.get("source_cube") == "MUCloudtainer-rev0077-2026.06.18.03.42-adaptivepooling-leakguard"
        and tier77_summary.get("hot_core_records") == 6
        and tier77_summary.get("cold_sidecar_records") == 72
        and tier77_core.get("passed") is True,
        {
            "catalog_path": tier77_path.name if tier77_path.exists() else None,
            "source_cube": tier77.get("source_cube") if isinstance(tier77, dict) else None,
            "summary": tier77_summary,
            "core_validation": tier77_core,
        })


    required_rev0078_files = [
        "src/muc5/population_frontier.py",
        "scripts/run_rev0078_familywise_gate_audit.py",
        "scripts/run_rev0078_artifact_audit.py",
        "tests/test_rev0078_familywise_gate.py",
        "docs/familywise_gate_rev0078.md",
        "docs/refactor_audit_rev0078.md",
        "docs/priority_reconsideration_rev0078.md",
        "docs/experiment_matrix_rev0078.md",
        "data/rev0078_familywise_gate_summary.json",
        "data/rev0078_familywise_global_gate.csv",
        "data/rev0078_familywise_life_gate.csv",
        "data/rev0078_familywise_naive_adaptive_gate.csv",
        "data/rev0078_familywise_gate_comparison.csv",
        "data/rev0078_artifact_audit.json",
        "data/rev0078_evidence_tiering_catalog.json",
        "data/rev0078_evidence_bundle_audit.json",
    ]
    missing_rev0078 = [path for path in required_rev0078_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0078", not missing_rev0078, {"missing": missing_rev0078})

    family78 = load_json(ROOT / "data" / "rev0078_familywise_gate_summary.json")
    ordinary78 = family78.get("ordinary_global_gate_summary", {}) if isinstance(family78.get("ordinary_global_gate_summary", {}), dict) else {}
    familywise78 = family78.get("familywise_global_gate_summary", {}) if isinstance(family78.get("familywise_global_gate_summary", {}), dict) else {}
    life_family78 = family78.get("familywise_by_life_gate_summary", {}) if isinstance(family78.get("familywise_by_life_gate_summary", {}), dict) else {}
    naive_family78 = family78.get("familywise_naive_adaptive_gate_summary", {}) if isinstance(family78.get("familywise_naive_adaptive_gate_summary", {}), dict) else {}
    global_rows78 = count_csv_rows(ROOT / "data" / "rev0078_familywise_global_gate.csv") if (ROOT / "data" / "rev0078_familywise_global_gate.csv").exists() else -1
    life_rows78 = count_csv_rows(ROOT / "data" / "rev0078_familywise_life_gate.csv") if (ROOT / "data" / "rev0078_familywise_life_gate.csv").exists() else -1
    naive_rows78 = count_csv_rows(ROOT / "data" / "rev0078_familywise_naive_adaptive_gate.csv") if (ROOT / "data" / "rev0078_familywise_naive_adaptive_gate.csv").exists() else -1
    comparison_rows78 = count_csv_rows(ROOT / "data" / "rev0078_familywise_gate_comparison.csv") if (ROOT / "data" / "rev0078_familywise_gate_comparison.csv").exists() else -1
    add(checks, "rev0078_familywise_gate_strengthens_matrix_uncertainty_without_promotion",
        family78.get("eligible_summary_rows") == 72
        and family78.get("eligible_summary_game_rows") == 432
        and family78.get("family_cell_count") == 6
        and abs(float(family78.get("per_cell_alpha", 0.0)) - (0.05 / 6.0)) < 1e-15
        and ordinary78.get("gate_passed_cells") == 0
        and familywise78.get("gate_passed_cells") == 0
        and familywise78.get("status_counts", {}).get("quarantined_low_security_floor") == 1
        and float(family78.get("familywise_minus_ordinary_global_lcb_delta", 0.0)) < -0.02
        and float(family78.get("familywise_minus_ordinary_global_width_delta", 0.0)) > 0.05
        and float(familywise78.get("best_conservative_pure_security_lcb", 1.0)) < float(ordinary78.get("best_conservative_pure_security_lcb", 0.0))
        and global_rows78 == 1,
        {
            "summary": family78,
            "rows": {
                "global": global_rows78,
                "life": life_rows78,
                "naive": naive_rows78,
                "comparison": comparison_rows78,
            },
        })

    add(checks, "rev0078_familywise_life_and_naive_cuts_remain_quarantined",
        life_family78.get("gate_passed_cells") == 0
        and life_family78.get("status_counts", {}).get("quarantined_low_security_floor") == 2
        and naive_family78.get("gate_passed_cells") == 0
        and naive_family78.get("status_counts", {}).get("quarantined_low_security_floor") == 1
        and life_rows78 == 2
        and naive_rows78 == 1
        and comparison_rows78 == 4,
        {
            "life_familywise": life_family78,
            "naive_familywise": naive_family78,
            "rows": {"life": life_rows78, "naive": naive_rows78, "comparison": comparison_rows78},
        })

    artifact78 = load_json(ROOT / "data" / "rev0078_artifact_audit.json")
    add(checks, "rev0078_artifact_audit_keeps_familywise_gate_compact",
        artifact78.get("passed") is True
        and not artifact78.get("forbidden_present")
        and not artifact78.get("row_limit_violations")
        and global_rows78 == 1
        and comparison_rows78 == 4,
        {"artifact_audit": artifact78})

    tier78_path = ROOT / "data" / "rev0078_evidence_tiering_catalog.json"
    tier78 = load_tiering_catalog(tier78_path) if tier78_path.exists() else {}
    tier78_summary = tier78.get("summary", {}) if isinstance(tier78, dict) else {}
    tier78_core = validate_core_tiering(ROOT, tier78) if tier78 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0078_evidence_catalog_remains_valid_after_later_carry_forward",
        tier78_path.exists()
        and tier78.get("source_cube") == "MUCloudtainer-rev0078-2026.06.18.03.44-familywisegate-fallbacksolver"
        and tier78_summary.get("hot_core_records") == 6
        and tier78_summary.get("cold_sidecar_records") == 72
        and tier78_core.get("passed") is True,
        {
            "catalog_path": tier78_path.name if tier78_path.exists() else None,
            "source_cube": tier78.get("source_cube") if isinstance(tier78, dict) else None,
            "summary": tier78_summary,
            "core_validation": tier78_core,
        })


    required_rev0079_files = [
        "src/muc5/population_frontier.py",
        "scripts/run_rev0079_hierarchical_gate_audit.py",
        "scripts/run_rev0079_artifact_audit.py",
        "tests/test_rev0079_hierarchical_gate.py",
        "docs/hierarchical_gate_rev0079.md",
        "docs/refactor_audit_rev0079.md",
        "docs/priority_reconsideration_rev0079.md",
        "docs/experiment_matrix_rev0079.md",
        "data/rev0079_hierarchical_gate_summary.json",
        "data/rev0079_hierarchical_familywise_gate.csv",
        "data/rev0079_hierarchical_gate_layer_summary.csv",
        "data/rev0079_solver_diagnostic.csv",
        "data/rev0079_artifact_audit.json",
        "data/rev0079_evidence_tiering_catalog.json",
        "data/rev0079_evidence_bundle_audit.json",
    ]
    missing_rev0079 = [path for path in required_rev0079_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0079", not missing_rev0079, {"missing": missing_rev0079})

    hierarchy79 = load_json(ROOT / "data" / "rev0079_hierarchical_gate_summary.json")
    h_summary79 = hierarchy79.get("hierarchy_summary", {}) if isinstance(hierarchy79.get("hierarchy_summary", {}), dict) else {}
    h_layers79 = h_summary79.get("hierarchy_layers", {}) if isinstance(h_summary79.get("hierarchy_layers", {}), dict) else {}
    h_status79 = h_summary79.get("hierarchy_layer_status_counts", {}) if isinstance(h_summary79.get("hierarchy_layer_status_counts", {}), dict) else {}
    h_gate_rows79 = count_csv_rows(ROOT / "data" / "rev0079_hierarchical_familywise_gate.csv") if (ROOT / "data" / "rev0079_hierarchical_familywise_gate.csv").exists() else -1
    h_layer_rows79 = count_csv_rows(ROOT / "data" / "rev0079_hierarchical_gate_layer_summary.csv") if (ROOT / "data" / "rev0079_hierarchical_gate_layer_summary.csv").exists() else -1
    solver_rows79 = count_csv_rows(ROOT / "data" / "rev0079_solver_diagnostic.csv") if (ROOT / "data" / "rev0079_solver_diagnostic.csv").exists() else -1
    add(checks, "rev0079_hierarchical_gate_blocks_aggregate_only_promotion_path",
        hierarchy79.get("eligible_summary_rows") == 72
        and hierarchy79.get("eligible_summary_game_rows") == 432
        and h_gate_rows79 == 12
        and h_layer_rows79 == 4
        and h_layers79 == {"global": 1, "by_life": 2, "by_size": 3, "by_size_life": 6}
        and h_summary79.get("gate_passed_cells") == 0
        and h_summary79.get("mandatory_gate_passed_rows") == 0
        and h_summary79.get("mandatory_all_passed") is False
        and h_status79.get("global", {}).get("quarantined_low_security_floor") == 1
        and h_status79.get("by_life", {}).get("quarantined_low_security_floor") == 2
        and h_status79.get("by_size", {}).get("precision_target_not_met") == 3
        and h_status79.get("by_size_life", {}).get("underpowered_min_games") == 6,
        {
            "summary": hierarchy79,
            "rows": {"hierarchical_gate": h_gate_rows79, "layer_summary": h_layer_rows79, "solver": solver_rows79},
        })

    add(checks, "rev0079_exact_support_solver_covers_future_three_policy_surface",
        solver_rows79 == 2
        and hierarchy79.get("solver_exact_method") == "exact_support_enumeration"
        and abs(float(hierarchy79.get("solver_exact_value", 0.0)) - 0.5) < 1e-12
        and abs(float(hierarchy79.get("solver_exact_value_gap", 1.0))) < 1e-12
        and float(hierarchy79.get("solver_fictitious_play_value_gap_200_iterations", 0.0)) > 0.004
        and float(hierarchy79.get("solver_exact_minus_fp_guarantee", 0.0)) > 0.001,
        {
            "summary": hierarchy79,
            "solver_rows": solver_rows79,
        })

    artifact79 = load_json(ROOT / "data" / "rev0079_artifact_audit.json")
    add(checks, "rev0079_artifact_audit_keeps_hierarchical_gate_compact",
        artifact79.get("passed") is True
        and not artifact79.get("forbidden_present")
        and not artifact79.get("row_limit_violations")
        and h_gate_rows79 == 12
        and h_layer_rows79 == 4
        and solver_rows79 == 2,
        {"artifact_audit": artifact79})

    tier79_path = ROOT / "data" / "rev0079_evidence_tiering_catalog.json"
    tier79 = load_tiering_catalog(tier79_path) if tier79_path.exists() else {}
    tier79_summary = tier79.get("summary", {}) if isinstance(tier79, dict) else {}
    tier79_core = validate_core_tiering(ROOT, tier79) if tier79 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0079_evidence_catalog_remains_valid_after_later_carry_forward",
        tier79_path.exists()
        and tier79.get("source_cube") == "MUCloudtainer-rev0079-2026.06.18.04.32-hierarchicalgate-exactfallback"
        and tier79_summary.get("hot_core_records") == 6
        and tier79_summary.get("cold_sidecar_records") == 72
        and tier79_core.get("passed") is True,
        {
            "catalog_path": tier79_path.name if tier79_path.exists() else None,
            "source_cube": tier79.get("source_cube") if isinstance(tier79, dict) else None,
            "summary": tier79_summary,
            "core_validation": tier79_core,
        })

    required_rev0080_files = [
        "src/muc5/population_power.py",
        "src/muc5/population_sampling.py",
        "scripts/run_rev0080_size_ladder_power_audit.py",
        "scripts/run_rev0080_artifact_audit.py",
        "tests/test_rev0080_size_ladder_power.py",
        "docs/size_ladder_power_rev0080.md",
        "docs/refactor_audit_rev0080.md",
        "docs/priority_reconsideration_rev0080.md",
        "docs/experiment_matrix_rev0080.md",
        "data/rev0080_size_ladder_power_summary.json",
        "data/rev0080_size_ladder_games.csv",
        "data/rev0080_size_ladder_arm_summary.csv",
        "data/rev0080_size_ladder_mechanisms.csv",
        "data/rev0080_size_ladder_cpp_transition_sample.csv",
        "data/rev0080_pre_power_ladder.csv",
        "data/rev0080_post_power_ladder.csv",
        "data/rev0080_post_hierarchical_familywise_gate.csv",
        "data/rev0080_sampling_frame_summary.csv",
        "data/rev0080_post_pooled_size_summary.csv",
        "data/rev0080_post_pooled_fine_summary.csv",
        "data/rev0080_artifact_audit.json",
        "data/rev0080_evidence_tiering_catalog.json",
        "data/rev0080_evidence_bundle_audit.json",
    ]
    missing_rev0080 = [path for path in required_rev0080_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0080", not missing_rev0080, {"missing": missing_rev0080})

    size80 = load_json(ROOT / "data" / "rev0080_size_ladder_power_summary.json")
    hierarchy80 = size80.get("hierarchy_summary", {}) if isinstance(size80.get("hierarchy_summary", {}), dict) else {}
    statuses80 = hierarchy80.get("hierarchy_layer_status_counts", {}) if isinstance(hierarchy80.get("hierarchy_layer_status_counts", {}), dict) else {}
    post_gate_rows80 = count_csv_rows(ROOT / "data" / "rev0080_post_hierarchical_familywise_gate.csv") if (ROOT / "data" / "rev0080_post_hierarchical_familywise_gate.csv").exists() else -1
    pre_ladder_rows80 = count_csv_rows(ROOT / "data" / "rev0080_pre_power_ladder.csv") if (ROOT / "data" / "rev0080_pre_power_ladder.csv").exists() else -1
    post_ladder_rows80 = count_csv_rows(ROOT / "data" / "rev0080_post_power_ladder.csv") if (ROOT / "data" / "rev0080_post_power_ladder.csv").exists() else -1
    games_rows80 = count_csv_rows(ROOT / "data" / "rev0080_size_ladder_games.csv") if (ROOT / "data" / "rev0080_size_ladder_games.csv").exists() else -1
    arm_rows80 = count_csv_rows(ROOT / "data" / "rev0080_size_ladder_arm_summary.csv") if (ROOT / "data" / "rev0080_size_ladder_arm_summary.csv").exists() else -1
    add(checks, "rev0080_size_ladder_clears_power_blockers_without_promotion",
        size80.get("games") == 720
        and size80.get("prior_eligible_summary_game_rows") == 432
        and size80.get("post_eligible_summary_game_rows") == 1152
        and size80.get("pre_all_layer_complete_panel_reps_needed") == 5
        and size80.get("pre_mandatory_complete_panel_reps_needed") == 1
        and size80.get("post_all_layer_complete_panel_reps_needed") == 0
        and size80.get("post_mandatory_complete_panel_reps_needed") == 0
        and hierarchy80.get("gate_passed_cells") == 0
        and hierarchy80.get("status_counts", {}).get("quarantined_low_security_floor") == 12
        and statuses80.get("by_size", {}).get("quarantined_low_security_floor") == 3
        and statuses80.get("by_size_life", {}).get("quarantined_low_security_floor") == 6
        and post_gate_rows80 == 12
        and pre_ladder_rows80 == 12
        and post_ladder_rows80 == 12
        and games_rows80 == 720
        and arm_rows80 == 36,
        {
            "summary": size80,
            "rows": {"post_gate": post_gate_rows80, "pre_ladder": pre_ladder_rows80, "post_ladder": post_ladder_rows80, "games": games_rows80, "arm_summary": arm_rows80},
        })

    cpp80 = size80.get("cpp_shadow_summary", {}) if isinstance(size80.get("cpp_shadow_summary", {}), dict) else {}
    terminal80 = size80.get("terminal_clean_summary", {}) if isinstance(size80.get("terminal_clean_summary", {}), dict) else {}
    add(checks, "rev0080_outcome_ladder_terminal_and_cpp_shadow_clean",
        terminal80.get("terminal_clean") is True
        and terminal80.get("rows") == 720
        and terminal80.get("truncation_rows") == 0
        and size80.get("python_errors") == 0
        and size80.get("truncations") == 0
        and size80.get("cpp_shadow_records_checked") == 15000
        and cpp80.get("mismatches") == 0
        and cpp80.get("skipped_events") == 0
        and cpp80.get("truncations") == 0,
        {"terminal": terminal80, "cpp": cpp80})

    sampling80_rows = count_csv_rows(ROOT / "data" / "rev0080_sampling_frame_summary.csv") if (ROOT / "data" / "rev0080_sampling_frame_summary.csv").exists() else -1
    sampling80 = []
    if (ROOT / "data" / "rev0080_sampling_frame_summary.csv").exists():
        with (ROOT / "data" / "rev0080_sampling_frame_summary.csv").open(newline="", encoding="utf-8") as handle:
            sampling80 = [dict(row) for row in csv.DictReader(handle)]
    sampling80_by_rev = {str(row.get("source_revision")): row for row in sampling80}
    add(checks, "rev0080_sampling_frame_whitelists_complete_panel_and_keeps_targeted_challenge_separate",
        sampling80_rows == 4
        and sampling80_by_rev.get("rev0080", {}).get("sampling_frame") == "complete_population_panel"
        and str(sampling80_by_rev.get("rev0080", {}).get("global_pool_eligible")).lower() == "true"
        and sampling80_by_rev.get("rev0075", {}).get("sampling_frame") == "targeted_stratum_challenge"
        and str(sampling80_by_rev.get("rev0075", {}).get("global_pool_eligible")).lower() == "false",
        {"sampling_rows": sampling80})

    artifact80 = load_json(ROOT / "data" / "rev0080_artifact_audit.json")
    add(checks, "rev0080_artifact_audit_keeps_size_ladder_compact",
        artifact80.get("passed") is True
        and not artifact80.get("forbidden_present")
        and not artifact80.get("row_limit_violations")
        and games_rows80 == 720
        and post_gate_rows80 == 12,
        {"artifact_audit": artifact80})

    tier80_path = ROOT / "data" / "rev0080_evidence_tiering_catalog.json"
    tier80 = load_tiering_catalog(tier80_path) if tier80_path.exists() else {}
    tier80_summary = tier80.get("summary", {}) if isinstance(tier80, dict) else {}
    tier80_core = validate_core_tiering(ROOT, tier80) if tier80 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0080_evidence_catalog_remains_valid_after_later_carry_forward",
        tier80_path.exists()
        and tier80_path.name == "rev0080_evidence_tiering_catalog.json"
        and tier80.get("source_cube") == "MUCloudtainer-rev0080-2026.06.18.05.05-sizeladder-poweraudit"
        and tier80_summary.get("hot_core_records") == 6
        and tier80_summary.get("cold_sidecar_records") == 72
        and tier80_core.get("passed") is True,
        {
            "catalog_path": tier80_path.name if tier80_path.exists() else None,
            "source_cube": tier80.get("source_cube") if isinstance(tier80, dict) else None,
            "summary": tier80_summary,
            "core_validation": tier80_core,
        })


    required_rev0081_files = [
        "src/muc5/population_frontier.py",
        "scripts/run_rev0081_opponent_frontier_audit.py",
        "scripts/run_rev0081_artifact_audit.py",
        "tests/test_rev0081_opponent_frontier.py",
        "docs/opponent_frontier_rev0081.md",
        "docs/refactor_audit_rev0081.md",
        "docs/priority_reconsideration_rev0081.md",
        "docs/experiment_matrix_rev0081.md",
        "data/rev0081_opponent_frontier_summary.json",
        "data/rev0081_opponent_frontier_familywise.csv",
        "data/rev0081_opponent_frontier_layer_summary.csv",
        "data/rev0081_opponent_frontier_hierarchical_gate_reference.csv",
        "data/rev0081_sampling_frame_summary.csv",
        "data/rev0081_artifact_audit.json",
        "data/rev0081_evidence_tiering_catalog.json",
        "data/rev0081_evidence_bundle_audit.json",
    ]
    missing_rev0081 = [path for path in required_rev0081_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0081", not missing_rev0081, {"missing": missing_rev0081})

    frontier81 = load_json(ROOT / "data" / "rev0081_opponent_frontier_summary.json")
    frontier_summary81 = frontier81.get("frontier_summary", {}) if isinstance(frontier81.get("frontier_summary", {}), dict) else {}
    layer_counts81 = frontier_summary81.get("hierarchy_layer_status_counts", {}) if isinstance(frontier_summary81.get("hierarchy_layer_status_counts", {}), dict) else {}
    threat_counts81 = frontier_summary81.get("threat_status_counts", {}) if isinstance(frontier_summary81.get("threat_status_counts", {}), dict) else {}
    frontier_rows81 = count_csv_rows(ROOT / "data" / "rev0081_opponent_frontier_familywise.csv") if (ROOT / "data" / "rev0081_opponent_frontier_familywise.csv").exists() else -1
    layer_rows81 = count_csv_rows(ROOT / "data" / "rev0081_opponent_frontier_layer_summary.csv") if (ROOT / "data" / "rev0081_opponent_frontier_layer_summary.csv").exists() else -1
    gate_ref_rows81 = count_csv_rows(ROOT / "data" / "rev0081_opponent_frontier_hierarchical_gate_reference.csv") if (ROOT / "data" / "rev0081_opponent_frontier_hierarchical_gate_reference.csv").exists() else -1
    sampling_rows81 = count_csv_rows(ROOT / "data" / "rev0081_sampling_frame_summary.csv") if (ROOT / "data" / "rev0081_sampling_frame_summary.csv").exists() else -1
    add(checks, "rev0081_opponent_frontier_resolves_threat_columns_without_false_answer",
        frontier81.get("eligible_summary_game_rows") == 1152
        and frontier81.get("adaptive_summary_rows_excluded") == 18
        and frontier81.get("frontier_rows") == 36
        and frontier81.get("global_frontier_rows") == 3
        and frontier81.get("mandatory_frontier_rows") == 18
        and frontier81.get("mandatory_column_answer_passed_rows") == 0
        and frontier_summary81.get("column_answer_passed_rows") == 0
        and frontier_summary81.get("status_counts", {}).get("no_credible_counter_answer_for_threat_column") == 36
        and frontier81.get("weak_threat_axis_count") == 3
        and float(frontier81.get("max_ci_width_observed", 1.0)) <= 0.60
        and int(frontier81.get("min_games_per_observed_column_cell", 0)) >= 24
        and frontier_rows81 == 36
        and layer_rows81 == 4
        and gate_ref_rows81 == 12
        and sampling_rows81 == 4,
        {
            "summary": frontier81,
            "rows": {"frontier": frontier_rows81, "layer": layer_rows81, "gate_reference": gate_ref_rows81, "sampling": sampling_rows81},
        })

    add(checks, "rev0081_opponent_frontier_covers_all_layers_and_threat_axes",
        layer_counts81.get("global", {}).get("no_credible_counter_answer_for_threat_column") == 3
        and layer_counts81.get("by_life", {}).get("no_credible_counter_answer_for_threat_column") == 6
        and layer_counts81.get("by_size", {}).get("no_credible_counter_answer_for_threat_column") == 9
        and layer_counts81.get("by_size_life", {}).get("no_credible_counter_answer_for_threat_column") == 18
        and len(threat_counts81) == 3
        and all(counts.get("no_credible_counter_answer_for_threat_column") == 12 for counts in threat_counts81.values()),
        {
            "layer_counts": layer_counts81,
            "threat_counts": threat_counts81,
        })

    artifact81 = load_json(ROOT / "data" / "rev0081_artifact_audit.json")
    add(checks, "rev0081_artifact_audit_keeps_opponent_frontier_compact",
        artifact81.get("passed") is True
        and not artifact81.get("forbidden_present")
        and not artifact81.get("row_limit_violations")
        and frontier_rows81 == 36,
        {"artifact_audit": artifact81})

    tier81_path = ROOT / "data" / "rev0081_evidence_tiering_catalog.json"
    tier81 = load_tiering_catalog(tier81_path) if tier81_path.exists() else {}
    tier81_summary = tier81.get("summary", {}) if isinstance(tier81, dict) else {}
    tier81_core = validate_core_tiering(ROOT, tier81) if tier81 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0081_evidence_catalog_remains_valid_after_later_carry_forward",
        tier81_path.exists()
        and tier81_path.name == "rev0081_evidence_tiering_catalog.json"
        and tier81.get("source_cube") == "MUCloudtainer-rev0081-2026.06.18.05.33-opponentfrontier-threataudit"
        and tier81_summary.get("hot_core_records") == 6
        and tier81_summary.get("cold_sidecar_records") == 72
        and tier81_core.get("passed") is True,
        {
            "catalog_path": tier81_path.name if tier81_path.exists() else None,
            "source_cube": tier81.get("source_cube") if isinstance(tier81, dict) else None,
            "summary": tier81_summary,
            "core_validation": tier81_core,
        })

    required_rev0082_files = [
        "src/muc5/population_frontier.py",
        "scripts/run_rev0082_counterset_rescue_audit.py",
        "scripts/run_rev0082_artifact_audit.py",
        "tests/test_rev0082_counterset_rescue.py",
        "docs/counterset_rescue_rev0082.md",
        "docs/refactor_audit_rev0082.md",
        "docs/priority_reconsideration_rev0082.md",
        "docs/experiment_matrix_rev0082.md",
        "data/rev0082_counterset_rescue_summary.json",
        "data/rev0082_counterset_rescue_envelope.csv",
        "data/rev0082_counterset_rescue_layer_summary.csv",
        "data/rev0082_artifact_audit.json",
        "data/rev0082_evidence_tiering_catalog.json",
        "data/rev0082_evidence_bundle_audit.json",
    ]
    missing_rev0082 = [path for path in required_rev0082_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0082", not missing_rev0082, {"missing": missing_rev0082})

    rescue82 = load_json(ROOT / "data" / "rev0082_counterset_rescue_summary.json")
    rescue_summary82 = rescue82.get("summary", {}) if isinstance(rescue82.get("summary", {}), dict) else {}
    rescue_rows82 = count_csv_rows(ROOT / "data" / "rev0082_counterset_rescue_envelope.csv") if (ROOT / "data" / "rev0082_counterset_rescue_envelope.csv").exists() else -1
    rescue_layer_rows82 = count_csv_rows(ROOT / "data" / "rev0082_counterset_rescue_layer_summary.csv") if (ROOT / "data" / "rev0082_counterset_rescue_layer_summary.csv").exists() else -1
    global_rescue82 = rescue82.get("global_rescue_status_counts", {}) if isinstance(rescue82.get("global_rescue_status_counts", {}), dict) else {}
    weakest82 = rescue82.get("weakest_ucb_case", {}) if isinstance(rescue82.get("weakest_ucb_case", {}), dict) else {}
    add(checks, "rev0082_rescue_envelope_prioritizes_counter_invention_without_false_certification",
        rescue82.get("source_frontier_rows") == 36
        and rescue82.get("rescue_rows") == 36
        and rescue82.get("existing_counter_certified_rows") == 0
        and rescue82.get("current_counter_set_deficient_rows") == 1
        and rescue82.get("mandatory_current_counter_set_deficient_rows") == 0
        and rescue82.get("mandatory_certification_limited_rows") == 11
        and rescue82.get("mandatory_mean_below_rescuable_rows") == 7
        and global_rescue82.get("certification_limited_existing_counter_candidate") == 2
        and global_rescue82.get("mean_below_threshold_but_upper_bound_allows_rescue") == 1
        and rescue_rows82 == 36
        and rescue_layer_rows82 == 4,
        {
            "summary": rescue82,
            "rows": {"rescue": rescue_rows82, "layer": rescue_layer_rows82},
        })

    add(checks, "rev0082_identifies_only_fine_cell_as_upper_bound_counter_set_deficient",
        weakest82.get("hierarchy_layer") == "by_size_life"
        and weakest82.get("size_axis") == "counter40_vs_threat40"
        and str(weakest82.get("starting_life")) == "20"
        and weakest82.get("threat_policy_axis") == "library_aware_threat_closure_targetguarded"
        and float(weakest82.get("ucb_gap_to_threshold", 1.0)) < 0.0
        and rescue_summary82.get("ucb_rescue_possible_rows") == 35
        and rescue_summary82.get("rescue_status_counts", {}).get("current_counter_set_deficient_even_by_upper_bound") == 1,
        {
            "weakest": weakest82,
            "rescue_summary": rescue_summary82,
        })

    artifact82 = load_json(ROOT / "data" / "rev0082_artifact_audit.json")
    add(checks, "rev0082_artifact_audit_keeps_rescue_envelope_compact",
        artifact82.get("passed") is True
        and not artifact82.get("forbidden_present")
        and not artifact82.get("row_limit_violations")
        and rescue_rows82 == 36,
        {"artifact_audit": artifact82})

    tier82_path = ROOT / "data" / "rev0082_evidence_tiering_catalog.json"
    tier82 = load_tiering_catalog(tier82_path) if tier82_path.exists() else {}
    tier82_summary = tier82.get("summary", {}) if isinstance(tier82, dict) else {}
    tier82_core = validate_core_tiering(ROOT, tier82) if tier82 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0082_evidence_catalog_remains_valid_after_later_carry_forward",
        tier82_path.exists()
        and tier82_path.name == "rev0082_evidence_tiering_catalog.json"
        and tier82.get("source_cube") == "MUCloudtainer-rev0082-2026.06.18.06.05-rescueenvelope-countersetaudit"
        and tier82_summary.get("hot_core_records") == 6
        and tier82_summary.get("cold_sidecar_records") == 72
        and tier82_core.get("passed") is True,
        {
            "catalog_path": tier82_path.name,
            "source_cube": tier82.get("source_cube") if isinstance(tier82, dict) else None,
            "summary": tier82_summary,
            "core_validation": tier82_core,
        })

    required_rev0083_files = [
        "src/muc5/public_agents.py",
        "src/muc5/population_counterprobe.py",
        "scripts/run_rev0083_deficient_cell_counterprobe.py",
        "scripts/run_rev0083_artifact_audit.py",
        "tests/test_rev0083_deficient_cell_counterprobe.py",
        "docs/deficient_cell_counterprobe_rev0083.md",
        "docs/refactor_audit_rev0083.md",
        "docs/priority_reconsideration_rev0083.md",
        "docs/experiment_matrix_rev0083.md",
        "data/rev0083_deficient_cell_counterprobe_summary.json",
        "data/rev0083_deficient_cell_counterprobe_games.csv",
        "data/rev0083_deficient_cell_counterprobe_arm_summary.csv",
        "data/rev0083_deficient_cell_counterprobe_policy_deltas.csv",
        "data/rev0083_deficient_cell_counterprobe_frontier.csv",
        "data/rev0083_deficient_cell_counterprobe_rescue.csv",
        "data/rev0083_deficient_cell_counterprobe_seed_balance.csv",
        "data/rev0083_deficient_cell_counterprobe_paired_outcome_delta.csv",
        "data/rev0083_artifact_audit.json",
        "data/rev0083_evidence_tiering_catalog.json",
        "data/rev0083_evidence_bundle_audit.json",
    ]
    missing_rev0083 = [path for path in required_rev0083_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0083", not missing_rev0083, {"missing": missing_rev0083})

    counterprobe83 = load_json(ROOT / "data" / "rev0083_deficient_cell_counterprobe_summary.json")
    candidate83 = counterprobe83.get("candidate_summary", {}) if isinstance(counterprobe83.get("candidate_summary", {}), dict) else {}
    paired83 = counterprobe83.get("paired_outcome_summary", {}) if isinstance(counterprobe83.get("paired_outcome_summary", {}), dict) else {}
    paired_counts83 = paired83.get("comparison_counts", {}) if isinstance(paired83.get("comparison_counts", {}), dict) else {}
    frontier83_rows = count_csv_rows(ROOT / "data" / "rev0083_deficient_cell_counterprobe_frontier.csv") if (ROOT / "data" / "rev0083_deficient_cell_counterprobe_frontier.csv").exists() else -1
    rescue83_rows = count_csv_rows(ROOT / "data" / "rev0083_deficient_cell_counterprobe_rescue.csv") if (ROOT / "data" / "rev0083_deficient_cell_counterprobe_rescue.csv").exists() else -1
    games83_rows = count_csv_rows(ROOT / "data" / "rev0083_deficient_cell_counterprobe_games.csv") if (ROOT / "data" / "rev0083_deficient_cell_counterprobe_games.csv").exists() else -1
    delta83_rows = count_csv_rows(ROOT / "data" / "rev0083_deficient_cell_counterprobe_policy_deltas.csv") if (ROOT / "data" / "rev0083_deficient_cell_counterprobe_policy_deltas.csv").exists() else -1
    add(checks, "rev0083_deficient_cell_counterprobe_challenges_upper_bound_label_without_false_promotion",
        counterprobe83.get("games") == 192
        and counterprobe83.get("arms") == 3
        and counterprobe83.get("python_errors") == 0
        and counterprobe83.get("cpp_shadow_checked_events") == 12000
        and counterprobe83.get("cpp_shadow_mismatches") == 0
        and counterprobe83.get("seed_balance_rows") == 64
        and counterprobe83.get("seed_balance_complete_rows") == 64
        and games83_rows == 192
        and delta83_rows == 3
        and frontier83_rows == 1
        and rescue83_rows == 1
        and counterprobe83.get("broad_pool_eligible") is False
        and counterprobe83.get("status") == "candidate_counter_repair_certification_limited"
        and candidate83.get("counter_set_deficient_even_by_upper_bound") is False
        and candidate83.get("candidate_certified") is False,
        {
            "summary": counterprobe83,
            "rows": {"games": games83_rows, "deltas": delta83_rows, "frontier": frontier83_rows, "rescue": rescue83_rows},
        })

    add(checks, "rev0083_seed_paired_candidate_ties_current_guard_not_a_broad_rescue",
        counterprobe83.get("candidate_axis") == "public_counter_life20_stabilizer"
        and abs(float(counterprobe83.get("candidate_mean", -1.0)) - 0.53125) < 1e-12
        and abs(float(counterprobe83.get("best_old_mean", -1.0)) - 0.53125) < 1e-12
        and abs(float(counterprobe83.get("candidate_minus_best_old_mean", 1.0))) < 1e-12
        and paired83.get("rows") == 64
        and paired83.get("same_score_rows") == 58
        and paired83.get("candidate_better_rows") == 3
        and paired83.get("guard_better_rows") == 3
        and paired_counts83.get("same_score") == 58,
        {
            "candidate_mean": counterprobe83.get("candidate_mean"),
            "best_old_mean": counterprobe83.get("best_old_mean"),
            "paired_outcome_summary": paired83,
        })

    artifact83 = load_json(ROOT / "data" / "rev0083_artifact_audit.json")
    add(checks, "rev0083_artifact_audit_keeps_counterprobe_compact",
        artifact83.get("passed") is True
        and not artifact83.get("forbidden_present")
        and not artifact83.get("row_limit_violations")
        and games83_rows == 192,
        {"artifact_audit": artifact83})

    tier83_path = ROOT / "data" / "rev0083_evidence_tiering_catalog.json"
    tier83 = load_tiering_catalog(tier83_path) if tier83_path.exists() else {}
    tier83_summary = tier83.get("summary", {}) if isinstance(tier83, dict) else {}
    tier83_core = validate_core_tiering(ROOT, tier83) if tier83 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0083_evidence_catalog_remains_valid_after_candidate_transfer_carry_forward",
        tier83_path.exists()
        and tier83_path.name == "rev0083_evidence_tiering_catalog.json"
        and tier83.get("source_cube") == "MUCloudtainer-rev0083-2026.06.18.06.44-deficientcell-counterprobe"
        and tier83_summary.get("hot_core_records") == 6
        and tier83_summary.get("cold_sidecar_records") == 72
        and tier83_core.get("passed") is True,
        {
            "catalog_path": tier83_path.name,
            "source_cube": tier83.get("source_cube") if isinstance(tier83, dict) else None,
            "summary": tier83_summary,
            "core_validation": tier83_core,
        })

    required_rev0084_files = [
        "src/muc5/population_candidate_transfer.py",
        "scripts/run_rev0084_candidate_transfer_audit.py",
        "scripts/run_rev0084_artifact_audit.py",
        "tests/test_rev0084_candidate_transfer.py",
        "docs/candidate_transfer_audit_rev0084.md",
        "docs/refactor_audit_rev0084.md",
        "docs/priority_reconsideration_rev0084.md",
        "docs/experiment_matrix_rev0084.md",
        "data/rev0084_candidate_transfer_summary.json",
        "data/rev0084_candidate_transfer_games.csv",
        "data/rev0084_candidate_transfer_arm_summary.csv",
        "data/rev0084_candidate_transfer_paired_deltas.csv",
        "data/rev0084_candidate_transfer_context_summary.csv",
        "data/rev0084_candidate_transfer_axis_summary.csv",
        "data/rev0084_artifact_audit.json",
        "data/rev0084_evidence_tiering_catalog.json",
        "data/rev0084_evidence_bundle_audit.json",
    ]
    missing_rev0084 = [path for path in required_rev0084_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0084", not missing_rev0084, {"missing": missing_rev0084})

    transfer84 = load_json(ROOT / "data" / "rev0084_candidate_transfer_summary.json")
    overall84 = transfer84.get("overall_summary", {}) if isinstance(transfer84.get("overall_summary", {}), dict) else {}
    holdout84 = transfer84.get("holdout_summary", {}) if isinstance(transfer84.get("holdout_summary", {}), dict) else {}
    transfer_panel84 = transfer84.get("transfer_summary", {}) if isinstance(transfer84.get("transfer_summary", {}), dict) else {}
    games84_rows = count_csv_rows(ROOT / "data" / "rev0084_candidate_transfer_games.csv") if (ROOT / "data" / "rev0084_candidate_transfer_games.csv").exists() else -1
    pairs84_rows = count_csv_rows(ROOT / "data" / "rev0084_candidate_transfer_paired_deltas.csv") if (ROOT / "data" / "rev0084_candidate_transfer_paired_deltas.csv").exists() else -1
    context84_rows = count_csv_rows(ROOT / "data" / "rev0084_candidate_transfer_context_summary.csv") if (ROOT / "data" / "rev0084_candidate_transfer_context_summary.csv").exists() else -1
    add(checks, "rev0084_candidate_transfer_quarantines_adaptive_stabilizer",
        transfer84.get("games") == 480
        and transfer84.get("complete_pairs") == 240
        and transfer84.get("python_errors") == 0
        and transfer84.get("cpp_shadow_checked_events") == 14000
        and transfer84.get("cpp_shadow_mismatches") == 0
        and transfer84.get("candidate_axis") == "public_counter_life20_stabilizer"
        and transfer84.get("baseline_axis") == "public_counter_guard"
        and transfer84.get("candidate_broad_pool_eligible") is False
        and transfer84.get("candidate_pool_eligible") is False
        and transfer84.get("status") == "candidate_quarantined_transfer_or_holdout_risk"
        and games84_rows == 480
        and pairs84_rows == 240
        and context84_rows == 19,
        {
            "summary": transfer84,
            "rows": {"games": games84_rows, "pairs": pairs84_rows, "contexts": context84_rows},
        })

    add(checks, "rev0084_seed_disjoint_holdout_detects_negative_transfer",
        overall84.get("status") == "candidate_quarantined_negative_transfer"
        and holdout84.get("status") == "candidate_quarantined_negative_transfer"
        and transfer_panel84.get("status") == "candidate_quarantined_negative_transfer"
        and int(overall84.get("guard_better_pairs", -1)) > int(overall84.get("candidate_better_pairs", 999))
        and float(overall84.get("candidate_mean_delta", 1.0)) < 0.0
        and int(holdout84.get("guard_better_pairs", -1)) > int(holdout84.get("candidate_better_pairs", 999))
        and float(holdout84.get("candidate_mean_delta", 1.0)) < 0.0,
        {
            "overall": overall84,
            "holdout": holdout84,
            "transfer": transfer_panel84,
        })

    artifact84 = load_json(ROOT / "data" / "rev0084_artifact_audit.json")
    add(checks, "rev0084_artifact_audit_keeps_candidate_transfer_compact",
        artifact84.get("passed") is True
        and not artifact84.get("forbidden_present")
        and not artifact84.get("row_limit_violations")
        and games84_rows == 480,
        {"artifact_audit": artifact84})

    tier84_path = ROOT / "data" / "rev0084_evidence_tiering_catalog.json"
    tier84 = load_tiering_catalog(tier84_path) if tier84_path.exists() else {}
    tier84_summary = tier84.get("summary", {}) if isinstance(tier84, dict) else {}
    tier84_core = validate_core_tiering(ROOT, tier84) if tier84 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0084_evidence_catalog_remains_valid_after_pair_forensics_carry_forward",
        tier84_path.exists()
        and tier84_path.name == "rev0084_evidence_tiering_catalog.json"
        and tier84.get("source_cube") == "MUCloudtainer-rev0084-2026.06.18.07.24-holdouttransfer-candidatequarantine"
        and tier84_summary.get("hot_core_records") == 6
        and tier84_summary.get("cold_sidecar_records") == 72
        and tier84_core.get("passed") is True,
        {
            "catalog_path": tier84_path.name,
            "source_cube": tier84.get("source_cube") if isinstance(tier84, dict) else None,
            "summary": tier84_summary,
            "core_validation": tier84_core,
        })

    required_rev0085_files = [
        "src/muc5/population_pair_forensics.py",
        "scripts/run_rev0085_pair_integrity_tie_forensics.py",
        "scripts/run_rev0085_artifact_audit.py",
        "tests/test_rev0085_pair_integrity.py",
        "docs/pair_integrity_tie_forensics_rev0085.md",
        "docs/refactor_audit_rev0085.md",
        "docs/priority_reconsideration_rev0085.md",
        "docs/experiment_matrix_rev0085.md",
        "data/rev0085_pair_integrity_summary.json",
        "data/rev0085_pair_integrity_rows.csv",
        "data/rev0085_primary_sign_tests.csv",
        "data/rev0085_context_sign_tests.csv",
        "data/rev0085_tie_mechanism_forensics.csv",
        "data/rev0085_artifact_audit.json",
        "data/rev0085_evidence_tiering_catalog.json",
        "data/rev0085_evidence_bundle_audit.json",
    ]
    missing_rev0085 = [path for path in required_rev0085_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0085", not missing_rev0085, {"missing": missing_rev0085})

    pair85 = load_json(ROOT / "data" / "rev0085_pair_integrity_summary.json")
    integ85 = pair85.get("pair_integrity", {}) if isinstance(pair85.get("pair_integrity", {}), dict) else {}
    pair85_rows = count_csv_rows(ROOT / "data" / "rev0085_pair_integrity_rows.csv") if (ROOT / "data" / "rev0085_pair_integrity_rows.csv").exists() else -1
    primary85_rows = count_csv_rows(ROOT / "data" / "rev0085_primary_sign_tests.csv") if (ROOT / "data" / "rev0085_primary_sign_tests.csv").exists() else -1
    context85_rows = count_csv_rows(ROOT / "data" / "rev0085_context_sign_tests.csv") if (ROOT / "data" / "rev0085_context_sign_tests.csv").exists() else -1
    tie85_rows = count_csv_rows(ROOT / "data" / "rev0085_tie_mechanism_forensics.csv") if (ROOT / "data" / "rev0085_tie_mechanism_forensics.csv").exists() else -1
    add(checks, "rev0085_pair_integrity_confirms_seedpaired_design",
        pair85.get("input_revision") == "rev0084"
        and pair85.get("games") == 480
        and pair85.get("paired_delta_rows") == 240
        and integ85.get("passed") is True
        and integ85.get("complete_pairs") == 240
        and integ85.get("seed_mismatches") == 0
        and integ85.get("context_mismatches") == 0
        and integ85.get("broad_pool_eligible_rows") == 0
        and integ85.get("candidate_pool_eligible_rows") == 0
        and pair85_rows == 240
        and primary85_rows == 3
        and context85_rows == 40
        and tie85_rows == 43,
        {
            "summary": pair85,
            "rows": {"pairs": pair85_rows, "primary": primary85_rows, "context": context85_rows, "tie": tie85_rows},
        })

    add(checks, "rev0085_exact_sign_test_refines_negative_transfer_claim",
        pair85.get("status") == "candidate_quarantined_transfer_panel_exact_sign_negative_transfer"
        and pair85.get("candidate_dominance_supported_primary_rows") == 0
        and pair85.get("negative_transfer_supported_primary_rows") == 1
        and pair85.get("transfer_familywise_negative_supported") is True
        and pair85.get("holdout_familywise_negative_supported") is False
        and pair85.get("overall_familywise_negative_supported") is False
        and abs(float(pair85.get("transfer_one_sided_p_candidate_worse", 1.0)) - 0.003692626953125) < 1e-15
        and abs(float(pair85.get("holdout_one_sided_p_candidate_worse", 0.0)) - 0.40726470947265625) < 1e-15
        and abs(float(pair85.get("overall_one_sided_p_candidate_worse", 0.0)) - 0.01754101668484509) < 1e-15,
        {
            "status": pair85.get("status"),
            "primary_sign_tests": pair85.get("primary_sign_tests"),
        })

    add(checks, "rev0085_tie_forensics_blocks_false_equivalence",
        pair85.get("overall_same_score_pairs") == 207
        and pair85.get("overall_same_score_mechanism_flip_pairs") == 18
        and pair85.get("tie_equivalence_warning") is True
        and abs(float(pair85.get("overall_mechanism_flip_share_of_ties", -1.0)) - 0.08695652173913043) < 1e-15,
        {
            "same_score_pairs": pair85.get("overall_same_score_pairs"),
            "mechanism_flip_pairs": pair85.get("overall_same_score_mechanism_flip_pairs"),
            "mechanism_flip_share": pair85.get("overall_mechanism_flip_share_of_ties"),
        })

    artifact85 = load_json(ROOT / "data" / "rev0085_artifact_audit.json")
    add(checks, "rev0085_artifact_audit_keeps_forensics_compact",
        artifact85.get("passed") is True
        and not artifact85.get("forbidden_present")
        and not artifact85.get("row_limit_violations")
        and pair85_rows == 240,
        {"artifact_audit": artifact85})

    tier85_path = ROOT / "data" / "rev0085_evidence_tiering_catalog.json"
    tier85 = load_tiering_catalog(tier85_path) if tier85_path.exists() else {}
    tier85_summary = tier85.get("summary", {}) if isinstance(tier85, dict) else {}
    tier85_core = validate_core_tiering(ROOT, tier85) if tier85 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0085_evidence_catalog_remains_valid_after_mechanism_drift_carry_forward",
        tier85_path.exists()
        and tier85_path.name == "rev0085_evidence_tiering_catalog.json"
        and tier85.get("source_cube") == "MUCloudtainer-rev0085-2026.06.18.07.52-pairintegrity-tieforensics"
        and tier85_summary.get("hot_core_records") == 6
        and tier85_summary.get("cold_sidecar_records") == 72
        and tier85_core.get("passed") is True,
        {
            "catalog_path": tier85_path.name if tier85_path.exists() else None,
            "source_cube": tier85.get("source_cube") if isinstance(tier85, dict) else None,
            "summary": tier85_summary,
            "core_validation": tier85_core,
        })

    # rev0086: mechanism-aware tie contract for adaptive candidate transfer.
    required_rev0086_files = [
        "src/muc5/population_pair_forensics.py",
        "scripts/run_rev0086_mechanism_drift_audit.py",
        "scripts/run_rev0086_artifact_audit.py",
        "tests/test_rev0086_mechanism_drift.py",
        "docs/mechanism_drift_tiecontract_rev0086.md",
        "docs/refactor_audit_rev0086.md",
        "docs/priority_reconsideration_rev0086.md",
        "docs/experiment_matrix_rev0086.md",
        "data/rev0086_mechanism_drift_summary.json",
        "data/rev0086_primary_mechanism_drift.csv",
        "data/rev0086_context_mechanism_drift.csv",
        "data/rev0086_same_score_mechanism_flips.csv",
        "data/rev0086_artifact_audit.json",
        "data/rev0086_evidence_tiering_catalog.json",
        "data/rev0086_evidence_bundle_audit.json",
    ]
    missing_rev0086 = [path for path in required_rev0086_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0086", not missing_rev0086, {"missing": missing_rev0086})

    drift86 = load_json(ROOT / "data" / "rev0086_mechanism_drift_summary.json")
    primary86_rows = count_csv_rows(ROOT / "data" / "rev0086_primary_mechanism_drift.csv") if (ROOT / "data" / "rev0086_primary_mechanism_drift.csv").exists() else -1
    context86_rows = count_csv_rows(ROOT / "data" / "rev0086_context_mechanism_drift.csv") if (ROOT / "data" / "rev0086_context_mechanism_drift.csv").exists() else -1
    flips86_rows = count_csv_rows(ROOT / "data" / "rev0086_same_score_mechanism_flips.csv") if (ROOT / "data" / "rev0086_same_score_mechanism_flips.csv").exists() else -1
    add(checks, "rev0086_mechanism_drift_tightens_score_tie_contract",
        drift86.get("input_revision") == "rev0084"
        and drift86.get("paired_delta_rows") == 240
        and drift86.get("overall_same_score_pairs") == 207
        and drift86.get("overall_score_and_mechanism_equivalent_pairs") == 189
        and drift86.get("overall_same_score_mechanism_flip_pairs") == 18
        and drift86.get("overall_life_to_library_flips") == 16
        and drift86.get("overall_library_to_life_flips") == 2
        and abs(float(drift86.get("overall_one_sided_p_candidate_library_shift", 1.0)) - 0.0006561279296875) < 1e-15
        and primary86_rows == 3
        and context86_rows == 40
        and flips86_rows == 18,
        {
            "paired_delta_rows": drift86.get("paired_delta_rows"),
            "score_ties": drift86.get("overall_same_score_pairs"),
            "score_and_mechanism_equivalent": drift86.get("overall_score_and_mechanism_equivalent_pairs"),
            "mechanism_flips": drift86.get("overall_same_score_mechanism_flip_pairs"),
            "life_to_library": drift86.get("overall_life_to_library_flips"),
            "library_to_life": drift86.get("overall_library_to_life_flips"),
            "p_candidate_library_shift": drift86.get("overall_one_sided_p_candidate_library_shift"),
            "primary_rows": primary86_rows,
            "context_rows": context86_rows,
            "flip_rows": flips86_rows,
        })
    add(checks, "rev0086_candidate_stays_quarantined_for_mechanism_drift_not_score_equivalence",
        drift86.get("candidate_broad_pool_eligible") is False
        and drift86.get("candidate_pool_eligible") is False
        and drift86.get("overall_candidate_library_shift_familywise_supported") is True
        and drift86.get("holdout_candidate_library_shift_familywise_supported") is True
        and drift86.get("transfer_candidate_library_shift_familywise_supported") is False
        and drift86.get("candidate_library_shift_supported_primary_rows") == 2
        and drift86.get("candidate_life_shift_supported_primary_rows") == 0
        and drift86.get("status") == "candidate_quarantined_score_tie_library_out_drift",
        {
            "status": drift86.get("status"),
            "overall_supported": drift86.get("overall_candidate_library_shift_familywise_supported"),
            "holdout_supported": drift86.get("holdout_candidate_library_shift_familywise_supported"),
            "transfer_supported": drift86.get("transfer_candidate_library_shift_familywise_supported"),
            "library_shift_supported_rows": drift86.get("candidate_library_shift_supported_primary_rows"),
            "life_shift_supported_rows": drift86.get("candidate_life_shift_supported_primary_rows"),
        })

    artifact86 = load_json(ROOT / "data" / "rev0086_artifact_audit.json")
    add(checks, "rev0086_artifact_audit_keeps_mechanism_drift_compact",
        artifact86.get("passed") is True
        and not artifact86.get("forbidden_present")
        and not artifact86.get("row_limit_violations")
        and flips86_rows == 18,
        {"artifact_audit": artifact86})

    tier86_path = ROOT / "data" / "rev0086_evidence_tiering_catalog.json"
    tier86 = load_tiering_catalog(tier86_path) if tier86_path.exists() else {}
    tier86_summary = tier86.get("summary", {}) if isinstance(tier86, dict) else {}
    tier86_core = validate_core_tiering(ROOT, tier86) if tier86 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0086_evidence_catalog_remains_valid_after_candidate_gate_carry_forward",
        tier86_path.exists()
        and tier86_path.name == "rev0086_evidence_tiering_catalog.json"
        and tier86.get("source_cube") == "MUCloudtainer-rev0086-2026.06.18.08.26-mechanismdrift-tiecontract"
        and tier86_summary.get("hot_core_records") == 6
        and tier86_summary.get("cold_sidecar_records") == 72
        and tier86_core.get("passed") is True,
        {
            "catalog_path": tier86_path.name if tier86_path.exists() else None,
            "source_cube": tier86.get("source_cube") if isinstance(tier86, dict) else None,
            "summary": tier86_summary,
            "core_validation": tier86_core,
        })

    # rev0087: mechanism-aware candidate firewall for adaptive counter candidates.
    required_rev0087_files = [
        "src/muc5/population_candidate_gate.py",
        "scripts/run_rev0087_candidate_gate_audit.py",
        "scripts/run_rev0087_artifact_audit.py",
        "tests/test_rev0087_candidate_gate.py",
        "docs/mechanismgate_candidatefirewall_rev0087.md",
        "docs/refactor_audit_rev0087.md",
        "docs/priority_reconsideration_rev0087.md",
        "docs/experiment_matrix_rev0087.md",
        "data/rev0087_candidate_gate_summary.json",
        "data/rev0087_candidate_gate_rows.csv",
        "data/rev0087_candidate_gate_component_rows.csv",
        "data/rev0087_candidate_gate_leak_audit.csv",
        "data/rev0087_artifact_audit.json",
        "data/rev0087_evidence_tiering_catalog.json",
        "data/rev0087_evidence_bundle_audit.json",
    ]
    missing_rev0087 = [path for path in required_rev0087_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0087", not missing_rev0087, {"missing": missing_rev0087})

    gate87 = load_json(ROOT / "data" / "rev0087_candidate_gate_summary.json")
    gate87_row = gate87.get("candidate_gate", {}) if isinstance(gate87, dict) else {}
    gate87_rows = count_csv_rows(ROOT / "data" / "rev0087_candidate_gate_rows.csv") if (ROOT / "data" / "rev0087_candidate_gate_rows.csv").exists() else -1
    gate87_component_rows = count_csv_rows(ROOT / "data" / "rev0087_candidate_gate_component_rows.csv") if (ROOT / "data" / "rev0087_candidate_gate_component_rows.csv").exists() else -1
    gate87_leak_rows = count_csv_rows(ROOT / "data" / "rev0087_candidate_gate_leak_audit.csv") if (ROOT / "data" / "rev0087_candidate_gate_leak_audit.csv").exists() else -1
    add(checks, "rev0087_candidate_gate_rejects_adaptive_stabilizer_executably",
        gate87.get("input_revision") == "rev0084"
        and gate87_row.get("paired_delta_rows") == 240
        and gate87_row.get("game_rows") == 480
        and gate87_row.get("primary_component_rows") == 6
        and gate87_row.get("score_hard_fail_rows") == 1
        and gate87_row.get("mechanism_hard_fail_rows") == 2
        and gate87_row.get("pool_leak_fail_rows") == 0
        and gate87_row.get("score_gate_passed") is False
        and gate87_row.get("mechanism_gate_passed") is False
        and gate87_row.get("pool_leak_gate_passed") is True
        and gate87_row.get("candidate_pool_eligible") is False
        and gate87_row.get("broad_pool_eligible") is False
        and gate87_row.get("status") == "candidate_rejected_score_and_mechanism_firewall"
        and gate87_rows == 1
        and gate87_component_rows == 6
        and gate87_leak_rows == 8,
        {
            "gate": gate87_row,
            "gate_rows": gate87_rows,
            "component_rows": gate87_component_rows,
            "leak_rows": gate87_leak_rows,
        })

    reasons87 = set(gate87_row.get("hard_fail_reasons", [])) if isinstance(gate87_row, dict) else set()
    add(checks, "rev0087_candidate_firewall_records_score_mechanism_and_no_leak",
        reasons87 == {"score_transfer_familywise_negative", "score_tie_mechanism_drift_familywise_supported"}
        and gate87.get("candidate_rejected") is True
        and gate87.get("score_hard_fail_rows") == 1
        and gate87.get("mechanism_hard_fail_rows") == 2
        and gate87.get("pool_leak_fail_rows") == 0
        and gate87.get("same_score_mechanism_flip_rows_across_primary_components") == 36,
        {
            "hard_fail_reasons": sorted(reasons87),
            "candidate_rejected": gate87.get("candidate_rejected"),
            "score_hard_fail_rows": gate87.get("score_hard_fail_rows"),
            "mechanism_hard_fail_rows": gate87.get("mechanism_hard_fail_rows"),
            "pool_leak_fail_rows": gate87.get("pool_leak_fail_rows"),
            "same_score_mechanism_flip_rows_across_primary_components": gate87.get("same_score_mechanism_flip_rows_across_primary_components"),
        })

    artifact87 = load_json(ROOT / "data" / "rev0087_artifact_audit.json")
    add(checks, "rev0087_artifact_audit_keeps_candidate_firewall_compact",
        artifact87.get("passed") is True
        and not artifact87.get("forbidden_present")
        and not artifact87.get("row_limit_violations")
        and gate87_rows == 1
        and gate87_component_rows == 6
        and gate87_leak_rows == 8,
        {"artifact_audit": artifact87})

    tier87_path = ROOT / "data" / "rev0087_evidence_tiering_catalog.json"
    tier87 = load_tiering_catalog(tier87_path) if tier87_path.exists() else {}
    tier87_summary = tier87.get("summary", {}) if isinstance(tier87, dict) else {}
    tier87_core = validate_core_tiering(ROOT, tier87) if tier87 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0087_evidence_catalog_remains_valid_after_designfamily_carry_forward",
        tier87_path.exists()
        and tier87_path.name == "rev0087_evidence_tiering_catalog.json"
        and tier87.get("source_cube") == "MUCloudtainer-rev0087-2026.06.18.09.04-mechanismgate-candidatefirewall"
        and tier87_summary.get("hot_core_records") == 6
        and tier87_summary.get("cold_sidecar_records") == 72
        and tier87_core.get("passed") is True,
        {
            "catalog_path": tier87_path.name if tier87_path.exists() else None,
            "source_cube": tier87.get("source_cube") if isinstance(tier87, dict) else None,
            "summary": tier87_summary,
            "core_validation": tier87_core,
        })

    # rev0088: dynamic design-family correction and explicit schema contract for adaptive candidates.
    required_rev0088_files = [
        "src/muc5/population_candidate_gate.py",
        "scripts/run_rev0088_candidate_designfamily_audit.py",
        "scripts/run_rev0088_artifact_audit.py",
        "tests/test_rev0088_designfamily_candidate_schema.py",
        "docs/designfamily_candidateschema_rev0088.md",
        "docs/refactor_audit_rev0088.md",
        "docs/priority_reconsideration_rev0088.md",
        "docs/experiment_matrix_rev0088.md",
        "data/rev0088_candidate_designfamily_summary.json",
        "data/rev0088_candidate_designfamily_gate_rows.csv",
        "data/rev0088_candidate_designfamily_component_rows.csv",
        "data/rev0088_candidate_designfamily_leak_audit.csv",
        "data/rev0088_candidate_designfamily_schema_rows.csv",
        "data/rev0088_artifact_audit.json",
        "data/rev0088_evidence_tiering_catalog.json",
        "data/rev0088_evidence_bundle_audit.json",
    ]
    missing_rev0088 = [path for path in required_rev0088_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0088", not missing_rev0088, {"missing": missing_rev0088})

    design88 = load_json(ROOT / "data" / "rev0088_candidate_designfamily_summary.json")
    gate88 = design88.get("candidate_gate", {}) if isinstance(design88, dict) else {}
    contract88 = design88.get("evidence_contract", {}) if isinstance(design88, dict) else {}
    gate88_rows = count_csv_rows(ROOT / "data" / "rev0088_candidate_designfamily_gate_rows.csv") if (ROOT / "data" / "rev0088_candidate_designfamily_gate_rows.csv").exists() else -1
    component88_rows = count_csv_rows(ROOT / "data" / "rev0088_candidate_designfamily_component_rows.csv") if (ROOT / "data" / "rev0088_candidate_designfamily_component_rows.csv").exists() else -1
    leak88_rows = count_csv_rows(ROOT / "data" / "rev0088_candidate_designfamily_leak_audit.csv") if (ROOT / "data" / "rev0088_candidate_designfamily_leak_audit.csv").exists() else -1
    schema88_rows = count_csv_rows(ROOT / "data" / "rev0088_candidate_designfamily_schema_rows.csv") if (ROOT / "data" / "rev0088_candidate_designfamily_schema_rows.csv").exists() else -1
    add(checks, "rev0088_candidate_design_family_gate_still_rejects_stabilizer",
        design88.get("input_revision") == "rev0084"
        and design88.get("sampling_design_groups") == 3
        and design88.get("family_tests_used") == 3
        and design88.get("component_rows") == 6
        and gate88.get("paired_delta_rows") == 240
        and gate88.get("game_rows") == 480
        and gate88.get("score_hard_fail_rows") == 1
        and gate88.get("mechanism_hard_fail_rows") == 2
        and gate88.get("pool_leak_fail_rows") == 0
        and gate88.get("candidate_pool_eligible") is False
        and gate88.get("broad_pool_eligible") is False
        and gate88.get("status") == "candidate_rejected_score_and_mechanism_firewall"
        and gate88_rows == 1
        and component88_rows == 6
        and leak88_rows == 8,
        {
            "sampling_design_groups": design88.get("sampling_design_groups"),
            "family_tests_used": design88.get("family_tests_used"),
            "gate": gate88,
            "gate_rows": gate88_rows,
            "component_rows": component88_rows,
            "leak_rows": leak88_rows,
        })

    add(checks, "rev0088_candidate_schema_contract_fails_closed_without_ballast",
        contract88.get("passed") is True
        and contract88.get("hard_fail_rows") == 0
        and contract88.get("contract_rows") == 4
        and schema88_rows == 4
        and set(design88.get("family_group_labels", [])) == {"overall", "selected_cell_holdout", "transfer_panel"},
        {
            "contract": contract88,
            "schema_rows": schema88_rows,
            "family_group_labels": design88.get("family_group_labels"),
        })

    artifact88 = load_json(ROOT / "data" / "rev0088_artifact_audit.json")
    add(checks, "rev0088_artifact_audit_keeps_designfamily_schema_compact",
        artifact88.get("passed") is True
        and not artifact88.get("forbidden_present")
        and not artifact88.get("row_limit_violations")
        and gate88_rows == 1
        and component88_rows == 6
        and leak88_rows == 8
        and schema88_rows == 4,
        {"artifact_audit": artifact88})

    tier88_path = ROOT / "data" / "rev0088_evidence_tiering_catalog.json"
    tier88 = load_tiering_catalog(tier88_path) if tier88_path.exists() else {}
    tier88_summary = tier88.get("summary", {}) if isinstance(tier88, dict) else {}
    tier88_core = validate_core_tiering(ROOT, tier88) if tier88 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0088_evidence_catalog_remains_valid_after_replay_guard_carry_forward",
        tier88_path.exists()
        and tier88_path.name == "rev0088_evidence_tiering_catalog.json"
        and tier88.get("source_cube") == "MUCloudtainer-rev0088-2026.06.18.09.42-designfamily-candidateschema"
        and tier88_summary.get("hot_core_records") == 6
        and tier88_summary.get("cold_sidecar_records") == 72
        and tier88_core.get("passed") is True,
        {
            "catalog_path": tier88_path.name if tier88_path.exists() else None,
            "source_cube": tier88.get("source_cube") if isinstance(tier88, dict) else None,
            "summary": tier88_summary,
            "core_validation": tier88_core,
        })

    # rev0089: deterministic policy replay and runtime drift guard for name-only historical evidence.
    required_rev0089_files = [
        "src/muc5/population_replay_guard.py",
        "scripts/run_rev0089_policy_replay_drift_guard.py",
        "scripts/run_rev0089_artifact_audit.py",
        "tests/test_rev0089_policy_replay_guard.py",
        "docs/policyreplay_driftguard_rev0089.md",
        "docs/refactor_audit_rev0089.md",
        "docs/priority_reconsideration_rev0089.md",
        "docs/experiment_matrix_rev0089.md",
        "data/rev0089_policy_replay_summary.json",
        "data/rev0089_policy_runtime_identity.json",
        "data/rev0089_policy_replay_sample_rows.csv",
        "data/rev0089_policy_replay_check_rows.csv",
        "data/rev0089_policy_identity_coverage.csv",
        "data/rev0089_artifact_audit.json",
        "data/rev0089_evidence_tiering_catalog.json",
        "data/rev0089_evidence_bundle_audit.json",
    ]
    missing_rev0089 = [path for path in required_rev0089_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0089", not missing_rev0089, {"missing": missing_rev0089})

    replay89 = load_json(ROOT / "data" / "rev0089_policy_replay_summary.json")
    summary89 = replay89.get("summary", {}) if isinstance(replay89, dict) else {}
    runtime89 = replay89.get("runtime_identity", {}) if isinstance(replay89, dict) else {}
    replay89_rows = count_csv_rows(ROOT / "data" / "rev0089_policy_replay_check_rows.csv") if (ROOT / "data" / "rev0089_policy_replay_check_rows.csv").exists() else -1
    sample89_rows = count_csv_rows(ROOT / "data" / "rev0089_policy_replay_sample_rows.csv") if (ROOT / "data" / "rev0089_policy_replay_sample_rows.csv").exists() else -1
    coverage89_rows = count_csv_rows(ROOT / "data" / "rev0089_policy_identity_coverage.csv") if (ROOT / "data" / "rev0089_policy_identity_coverage.csv").exists() else -1
    add(checks, "rev0089_policy_replay_guard_reproduces_historical_sample",
        replay89.get("revision") == "rev0089"
        and replay89.get("source_row_counts") == {"rev0069": 144, "rev0070": 288, "rev0080": 720, "rev0084": 480}
        and summary89.get("total_source_rows") == 1632
        and summary89.get("sampled_rows") == 64
        and summary89.get("replayed_rows") == 64
        and summary89.get("python_errors") == 0
        and summary89.get("terminal_replay_mismatch_rows") == 0
        and summary89.get("terminal_replay_exact_match_rows") == 64
        and summary89.get("passed") is True
        and replay89_rows == 64
        and sample89_rows == 64,
        {
            "source_row_counts": replay89.get("source_row_counts"),
            "summary": summary89,
            "replay_rows": replay89_rows,
            "sample_rows": sample89_rows,
            "by_source_mismatches": replay89.get("by_source_mismatches"),
        })

    add(checks, "rev0089_policy_identity_gap_is_explicit_and_future_rows_are_guarded",
        runtime89.get("schema") == "muc5.policy_replay_guard.v1"
        and runtime89.get("file_count") == 10
        and runtime89.get("missing") == []
        and isinstance(runtime89.get("digest"), str)
        and len(runtime89.get("digest", "")) == 64
        and summary89.get("source_rows_missing_policy_identity") == 1632
        and summary89.get("legacy_identity_gap_present") is True
        and coverage89_rows == 4,
        {
            "runtime_identity": runtime89,
            "source_rows_missing_policy_identity": summary89.get("source_rows_missing_policy_identity"),
            "coverage_rows": coverage89_rows,
        })

    artifact89 = load_json(ROOT / "data" / "rev0089_artifact_audit.json")
    add(checks, "rev0089_artifact_audit_keeps_policy_replay_compact",
        artifact89.get("passed") is True
        and not artifact89.get("forbidden_present")
        and not artifact89.get("row_limit_violations")
        and replay89_rows == 64
        and sample89_rows == 64
        and coverage89_rows == 4,
        {"artifact_audit": artifact89})

    tier89_path = ROOT / "data" / "rev0089_evidence_tiering_catalog.json"
    tier89 = load_tiering_catalog(tier89_path) if tier89_path.exists() else {}
    tier89_summary = tier89.get("summary", {}) if isinstance(tier89, dict) else {}
    tier89_core = validate_core_tiering(ROOT, tier89) if tier89 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0089_evidence_catalog_remains_valid_after_mission_carry_forward",
        tier89_path.exists()
        and tier89_path.name == "rev0089_evidence_tiering_catalog.json"
        and tier89.get("source_cube") == "MUCloudtainer-rev0089-2026.06.18.10.18-policyreplay-driftguard"
        and tier89_summary.get("hot_core_records") == 6
        and tier89_summary.get("cold_sidecar_records") == 72
        and tier89_core.get("passed") is True,
        {
            "catalog_path": tier89_path.name if tier89_path.exists() else None,
            "source_cube": tier89.get("source_cube") if isinstance(tier89, dict) else None,
            "summary": tier89_summary,
            "core_validation": tier89_core,
        })

    # rev0090: canonical mission reassessment and information-state debt ledger.
    required_rev0090_files = [
        "docs/CURRENT_MISSION.md",
        "scripts/audit_mission_debt.py",
        "data/rev0090_mission_reassessment.json",
        "data/rev0090_structure_inventory.json",
        "data/rev0090_artifact_audit.json",
        "data/rev0090_evidence_tiering_catalog.json",
        "data/rev0090_evidence_bundle_audit.json",
    ]
    missing_rev0090 = [path for path in required_rev0090_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0090", not missing_rev0090, {"missing": missing_rev0090})

    mission90 = load_json(ROOT / "data" / "rev0090_mission_reassessment.json")
    findings90 = {
        str(row.get("id"))
        for row in mission90.get("critical_findings", [])
        if isinstance(row, dict)
    }
    expected_findings90 = {
        "INFO-STATE-001",
        "JACE-MEMORY-001",
        "PUBLIC-EVENT-001",
        "SPEC-DRIFT-001",
        "CLAIM-LEDGER-DRIFT-001",
        "CPP-INDEPENDENCE-001",
        "AGENT-CACHE-001",
        "SIDECAR-PROVENANCE-001",
        "VALIDATION-MUTATION-001",
        "POLICY-REPLAY-COVERAGE-001",
    }
    scope90 = mission90.get("revision_scope", {}) if isinstance(mission90, dict) else {}
    add(checks, "rev0090_mission_reassessment_names_semantic_blockers_without_new_claims",
        mission90.get("schema") == "muc5.mission_reassessment.v1"
        and mission90.get("revision") == "rev0090"
        and expected_findings90.issubset(findings90)
        and scope90.get("game_semantics_changed") is False
        and scope90.get("strategic_evidence_generated") is False,
        {
            "observed_finding_ids": sorted(findings90),
            "missing_finding_ids": sorted(expected_findings90 - findings90),
            "revision_scope": scope90,
        })

    inventory90 = load_json(ROOT / "data" / "rev0090_structure_inventory.json")
    inv90 = inventory90.get("summary", {}) if isinstance(inventory90, dict) else {}
    add(checks, "rev0090_structure_inventory_quantifies_cognitive_and_storage_debt",
        inventory90.get("schema") == "muc5.structure_inventory.v1"
        and inv90.get("files", 0) >= 2300
        and inv90.get("revision_stamped_docs", 0) >= 500
        and inv90.get("one_off_run_rev_scripts", 0) >= 120
        and inv90.get("audit_cube_lines", 0) >= 4800
        and inv90.get("hot_evidence_records") == 6
        and inv90.get("hot_evidence_bytes", 0) > 49_000_000,
        {"summary": inv90})

    artifact90 = load_json(ROOT / "data" / "rev0090_artifact_audit.json")
    add(checks, "rev0090_canonical_mission_artifacts_are_compact_and_no_boilerplate_returns",
        artifact90.get("passed") is True
        and not artifact90.get("missing")
        and not artifact90.get("errors")
        and not artifact90.get("forbidden_present")
        and not artifact90.get("forbidden_raw_strategic_artifacts"),
        {"artifact_audit": artifact90})

    bundle90 = load_json(ROOT / "data" / "rev0090_evidence_bundle_audit.json")
    verify90 = bundle90.get("current_revision_verification", {}) if isinstance(bundle90, dict) else {}
    availability90 = bundle90.get("availability", {}) if isinstance(bundle90, dict) else {}
    add(checks, "rev0090_sidecar_status_separates_historical_integrity_from_current_availability",
        bundle90.get("schema") == "muc5.evidence_bundle_status.v2"
        and bundle90.get("passed") is None
        and verify90.get("mode") == "carried_forward_hash_contract"
        and verify90.get("bundle_physically_present") is False
        and verify90.get("physically_reverified_this_revision") is False
        and availability90.get("status") == "external_bundle_required"
        and availability90.get("included_in_linked_core") is False
        and "durable_uri" in availability90,
        {"current_revision_verification": verify90, "availability": availability90})

    tier90_path = ROOT / "data" / "rev0090_evidence_tiering_catalog.json"
    tier90 = load_tiering_catalog(tier90_path) if tier90_path.exists() else {}
    tier90_summary = tier90.get("summary", {}) if isinstance(tier90, dict) else {}
    tier90_core = validate_core_tiering(ROOT, tier90) if tier90 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0090_evidence_catalog_core_stays_lean",
        tier90_path.exists()
        and str(tier90.get("source_cube", "")).startswith("MUCloudtainer-rev0090-")
        and tier90_summary.get("hot_core_records") == 6
        and tier90_summary.get("cold_sidecar_records") == 72
        and tier90_core.get("passed") is True,
        {
            "catalog_path": tier90_path.name if tier90_path.exists() else None,
            "source_cube": tier90.get("source_cube") if isinstance(tier90, dict) else None,
            "summary": tier90_summary,
            "core_validation": tier90_core,
        })

    # rev0091: executable information-state repair, not a new strategic-policy tournament.
    required_rev0091_files = [
        "docs/CURRENT_SPEC.md",
        "scripts/run_rev0091_information_state_audit.py",
        "tests/test_rev0091_information_state.py",
        "data/rev0091_information_state_audit.json",
        "data/rev0091_evidence_tiering_catalog.json",
    ]
    missing_rev0091 = [path for path in required_rev0091_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0091", not missing_rev0091, {"missing": missing_rev0091})

    info91 = load_json(ROOT / "data" / "rev0091_information_state_audit.json")
    info91_summary = info91.get("summary", {}) if isinstance(info91, dict) else {}
    info91_check_names = {str(row.get("name")) for row in info91.get("checks", []) if isinstance(row, dict)}
    expected_info91 = {
        "jace_plus2_pending_private_card_only_for_actor",
        "jace_plus2_observation_allowlist",
        "jace_plus2_leave_persists_after_choice_resolution",
        "jace_plus2_bottom_clears_known_top",
        "force_pitch_identity_is_public_exile_and_event",
        "replay_trace_records_and_checks_information_state_hash",
    }
    add(checks, "rev0091_information_state_audit_passes_with_expected_semantic_cases",
        info91.get("schema") == "muc5.information_state_audit.v1"
        and info91.get("revision") == "rev0091"
        and info91.get("passed") is True
        and expected_info91.issubset(info91_check_names)
        and info91_summary.get("check_count", 0) >= 6,
        {
            "summary": info91_summary,
            "observed_checks": sorted(info91_check_names),
            "missing_checks": sorted(expected_info91 - info91_check_names),
        })

    engine91 = (ROOT / "src" / "muc5" / "engine.py").read_text()
    decision91 = (ROOT / "src" / "muc5" / "decision.py").read_text()
    replay91 = (ROOT / "src" / "muc5" / "replay.py").read_text()
    spec91 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    add(checks, "rev0091_information_state_contract_is_in_code_and_spec",
        "def information_state" in engine91
        and "public_events" in engine91
        and "private_events" in engine91
        and "known_top_cards" in engine91
        and "information_state:" in decision91
        and "information_state_fingerprint" in replay91
        and "SPEC-INFO-003" in spec91
        and "SPEC-INFO-006" in spec91,
        {
            "engine_has_information_state": "def information_state" in engine91,
            "engine_has_event_streams": "public_events" in engine91 and "private_events" in engine91,
            "engine_has_known_top": "known_top_cards" in engine91,
            "decision_frame_has_information_state": "information_state:" in decision91,
            "replay_has_info_hash": "information_state_fingerprint" in replay91,
            "spec_rule_ids_present": "SPEC-INFO-003" in spec91 and "SPEC-INFO-006" in spec91,
        })

    tier91_path = ROOT / "data" / "rev0091_evidence_tiering_catalog.json"
    tier91 = load_tiering_catalog(tier91_path) if tier91_path.exists() else {}
    tier91_summary = tier91.get("summary", {}) if isinstance(tier91, dict) else {}
    tier91_core = validate_core_tiering(ROOT, tier91) if tier91 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0091_evidence_catalog_is_latest_and_no_raw_strategic_rows_added",
        tier91_path.exists()
        and tier91_path.name == "rev0091_evidence_tiering_catalog.json"
        and str(tier91.get("source_cube", "")).startswith("MUCloudtainer-rev0091-")
        and tier91_summary.get("hot_core_records") == 6
        and tier91_summary.get("cold_sidecar_records") == 72
        and tier91_core.get("passed") is True
        and not list(ROOT.glob("data/rev0091_*.csv"))
        and not list(ROOT.glob("data/rev0091_*.jsonl")),
        {
            "catalog_path": tier91_path.name if tier91_path.exists() else None,
            "source_cube": tier91.get("source_cube") if isinstance(tier91, dict) else None,
            "summary": tier91_summary,
            "core_validation": tier91_core,
            "rev0091_csv_rows": [p.name for p in ROOT.glob("data/rev0091_*.csv")],
            "rev0091_jsonl_rows": [p.name for p in ROOT.glob("data/rev0091_*.jsonl")],
        })

    # rev0092: episode-safe learning boundary and first executable finite-oracle PSRO expansion.
    required_rev0092_files = [
        "src/muc5/agent_lifecycle.py",
        "src/muc5/psro.py",
        "scripts/run_rev0092_psro_bootstrap.py",
        "tests/test_rev0092_psro_lifecycle.py",
        "docs/CURRENT_METHODS.md",
        "docs/CURRENT_MISSION.md",
        "docs/CURRENT_SPEC.md",
        "data/rev0092_psro_round.json",
        "data/rev0092_psro_bootstrap_audit.json",
        "data/rev0092_psro_games.csv",
        "data/rev0092_psro_candidate_catalog.csv",
        "data/rev0092_psro_candidate_scores.csv",
        "data/rev0092_psro_matrix.csv",
        "data/rev0092_psro_expanded_matrix.csv",
        "data/rev0092_psro_expanded_game.json",
        "data/rev0092_information_ablation.json",
        "data/rev0092_psro_replay_traces.jsonl",
        "data/rev0092_psro_replay_results.json",
        "data/rev0092_evidence_tiering_catalog.json",
    ]
    missing_rev0092 = [path for path in required_rev0092_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0092", not missing_rev0092, {"missing": missing_rev0092})

    lifecycle92 = (ROOT / "src" / "muc5" / "agent_lifecycle.py").read_text()
    agents92 = (ROOT / "src" / "muc5" / "agents.py").read_text()
    replay92 = (ROOT / "src" / "muc5" / "replay.py").read_text()
    payoff92 = (ROOT / "src" / "muc5" / "public_payoff.py").read_text()
    psro92_source = (ROOT / "src" / "muc5" / "psro.py").read_text()
    add(checks, "rev0092_episode_lifecycle_is_seat_scoped_and_replay_consistent",
        "class EpisodeContext" in lifecycle92
        and "def require_distinct_seat_objects" in lifecycle92
        and "reset_episode(agent0" in agents92
        and "end_episode(" in agents92
        and "require_distinct_seat_objects(agent0, agent1)" in replay92
        and "reset_episode(agent0" in replay92
        and "Dict[tuple[str, int], PublicDecisionAgent]" in payoff92
        and "strategy_signature(strategy)" in psro92_source,
        {
            "episode_context": "class EpisodeContext" in lifecycle92,
            "distinct_seat_guard": "def require_distinct_seat_objects" in lifecycle92,
            "game_reset": "reset_episode(agent0" in agents92,
            "replay_reset": "reset_episode(agent0" in replay92,
            "payoff_seat_cache": "Dict[tuple[str, int], PublicDecisionAgent]" in payoff92,
            "psro_signature_cache": "strategy_signature(strategy)" in psro92_source,
        })

    round92 = load_json(ROOT / "data" / "rev0092_psro_round.json")
    bootstrap92 = load_json(ROOT / "data" / "rev0092_psro_bootstrap_audit.json")
    confirmation92 = (round92.get("oracle_confirmation") or [{}])[0]
    ablation92 = round92.get("information_state_ablation", {}) if isinstance(round92, dict) else {}
    expanded92 = round92.get("expanded_restricted_game", {}) if isinstance(round92, dict) else {}
    efficiency92 = round92.get("evaluation_efficiency", {}) if isinstance(round92, dict) else {}
    solver92 = expanded92.get("solver", {}) if isinstance(expanded92, dict) else {}
    add(checks, "rev0092_psro_round_confirms_then_expands_without_strategic_promotion",
        round92.get("schema") == "muc5.psro_round.v2"
        and round92.get("status") == "exploratory_population_expanded"
        and confirmation92.get("confirmation_pass") is True
        and confirmation92.get("candidate_strategy") == "oracle_map_08_60_mixed_threats_counter_wall"
        and float(confirmation92.get("mixture_ci_low", 0.0)) > float(confirmation92.get("confirmation_threshold", 1.0))
        and len(expanded92.get("strategy_ids", [])) == 9
        and expanded92.get("scope") == "exploratory population expansion; no strategic promotion claim"
        and bootstrap92.get("passed") is True,
        {
            "status": round92.get("status"),
            "confirmation": confirmation92,
            "expanded_population_size": len(expanded92.get("strategy_ids", [])),
            "expanded_scope": expanded92.get("scope"),
            "bootstrap_passed": bootstrap92.get("passed"),
        })

    add(checks, "rev0092_information_wrapper_is_action_relevant_but_gets_no_unearned_outcome_credit",
        ablation92.get("schema") == "muc5.paired_information_ablation.v1"
        and ablation92.get("all_seeds_paired") is True
        and ablation92.get("paired_games") == 96
        and abs(float(ablation92.get("paired_mean_score_delta", 99.0))) <= 1e-12
        and ablation92.get("nonzero_score_deltas") == 0
        and "information state" in (ROOT / "docs" / "CURRENT_METHODS.md").read_text().lower(),
        {
            "paired_games": ablation92.get("paired_games"),
            "paired_mean_score_delta": ablation92.get("paired_mean_score_delta"),
            "nonzero_score_deltas": ablation92.get("nonzero_score_deltas"),
        })

    games92_rows = count_csv_rows(ROOT / "data" / "rev0092_psro_games.csv")
    candidate92_rows = count_csv_rows(ROOT / "data" / "rev0092_psro_candidate_catalog.csv")
    matrix92_rows = count_csv_rows(ROOT / "data" / "rev0092_psro_matrix.csv")
    expanded_matrix92_rows = count_csv_rows(ROOT / "data" / "rev0092_psro_expanded_matrix.csv")
    replay92_results = load_json(ROOT / "data" / "rev0092_psro_replay_results.json")
    seed_overlaps92 = bootstrap92.get("checks", {}).get("seed_overlap_counts", {}) if isinstance(bootstrap92, dict) else {}
    add(checks, "rev0092_oracle_evidence_is_complete_replayable_and_seed_disjoint",
        games92_rows == 1824
        and candidate92_rows == 16
        and matrix92_rows == 64
        and expanded_matrix92_rows == 81
        and isinstance(replay92_results, list)
        and len(replay92_results) == 4
        and all(row.get("passed") is True for row in replay92_results)
        and seed_overlaps92
        and all(int(value) == 0 for value in seed_overlaps92.values())
        and bootstrap92.get("checks", {}).get("truncations") == 0,
        {
            "game_rows": games92_rows,
            "candidate_rows": candidate92_rows,
            "restricted_matrix_rows": matrix92_rows,
            "expanded_matrix_rows": expanded_matrix92_rows,
            "replay_rows": len(replay92_results) if isinstance(replay92_results, list) else None,
            "seed_overlap_counts": seed_overlaps92,
            "truncations": bootstrap92.get("checks", {}).get("truncations"),
        })

    add(checks, "rev0092_support_pruning_removes_only_mathematically_irrelevant_rollouts",
        efficiency92.get("restricted_mixture_support_size") == 2
        and efficiency92.get("population_size") == 8
        and efficiency92.get("support_only_game_rows") == 800
        and efficiency92.get("zero_weight_game_rows_avoided") == 2400
        and abs(float(efficiency92.get("support_stage_reduction_fraction", 0.0)) - 0.75) <= 1e-12
        and abs(float(efficiency92.get("whole_round_reduction_fraction", 0.0)) - (25.0 / 44.0)) <= 1e-12
        and "positive_mixture_support" in psro92_source
        and "omitted_zero_weight" in psro92_source,
        {"evaluation_efficiency": efficiency92})

    mission92 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods92 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec92 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    add(checks, "rev0092_current_docs_replace_stale_blockers_with_executable_method_roadmap",
        "rev0092" in mission92
        and "The important negative result" in mission92
        and "PSRO / double oracle" in methods92
        and "gameplay-driven MAP-Elites" in methods92
        and "SPEC-AGENT-001" in spec92
        and "SPEC-ORACLE-006" in spec92
        and "there is no canonical information state" not in mission92.lower(),
        {
            "mission_current": "rev0092" in mission92,
            "methods_has_psro": "PSRO / double oracle" in methods92,
            "spec_has_lifecycle": "SPEC-AGENT-001" in spec92,
            "spec_has_oracle": "SPEC-ORACLE-006" in spec92,
        })

    tier92_path = ROOT / "data" / "rev0092_evidence_tiering_catalog.json"
    tier92 = load_tiering_catalog(tier92_path) if tier92_path.exists() else {}
    tier92_summary = tier92.get("summary", {}) if isinstance(tier92, dict) else {}
    tier92_core = validate_core_tiering(ROOT, tier92) if tier92 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0092_evidence_catalog_is_latest_and_core_stays_lean",
        tier92_path.exists()
        and tier92_path.name == "rev0092_evidence_tiering_catalog.json"
        and str(tier92.get("source_cube", "")).startswith("MUCloudtainer-rev0092-")
        and tier92_summary.get("hot_core_records") == 6
        and tier92_summary.get("cold_sidecar_records") == 72
        and tier92_core.get("passed") is True,
        {
            "catalog_path": tier92_path.name if tier92_path.exists() else None,
            "source_cube": tier92.get("source_cube") if isinstance(tier92, dict) else None,
            "summary": tier92_summary,
            "core_validation": tier92_core,
        })

    # rev0093: reduced tabular CFR calibration and shared PSRO support-pruning helper.
    required_rev0093_files = [
        "src/muc5/reduced_cfr.py",
        "scripts/run_rev0093_reduced_cfr.py",
        "tests/test_rev0093_reduced_cfr.py",
        "tests/test_rev0092_psro_lifecycle.py",
        "docs/reduced_cfr_rev0093.md",
        "docs/CURRENT_MISSION.md",
        "docs/CURRENT_METHODS.md",
        "docs/CURRENT_SPEC.md",
        "data/rev0093_reduced_cfr_summary.json",
        "data/rev0093_reduced_cfr_audit.json",
        "data/rev0093_reduced_cfr_convergence.csv",
        "data/rev0093_reduced_cfr_strategy.csv",
        "data/rev0093_evidence_tiering_catalog.json",
    ]
    missing_rev0093 = [path for path in required_rev0093_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0093", not missing_rev0093, {"missing": missing_rev0093})

    reduced93_source = (ROOT / "src" / "muc5" / "reduced_cfr.py").read_text()
    psro93_source = (ROOT / "src" / "muc5" / "psro.py").read_text()
    tests93_source = (ROOT / "tests" / "test_rev0093_reduced_cfr.py").read_text()
    add(checks, "rev0093_reduced_cfr_is_independent_and_information_set_safe",
        "class ReducedMUCCFRGame" in reduced93_source
        and "class TabularCFRSolver" in reduced93_source
        and "def best_response_value" in reduced93_source
        and "states_by_infoset" in reduced93_source
        and "concrete" in reduced93_source and "information set" in reduced93_source
        and "ReducedMUCState" in tests93_source
        and "known_top" in tests93_source
        and "force_pitch" in tests93_source,
        {
            "game_class": "class ReducedMUCCFRGame" in reduced93_source,
            "solver_class": "class TabularCFRSolver" in reduced93_source,
            "grouped_best_response": "states_by_infoset" in reduced93_source,
            "privacy_tests": "known_top" in tests93_source and "force_pitch" in tests93_source,
        })

    reduced93_summary = load_json(ROOT / "data" / "rev0093_reduced_cfr_summary.json")
    reduced93_audit = load_json(ROOT / "data" / "rev0093_reduced_cfr_audit.json")
    reduced93_checks = reduced93_audit.get("checks", {}) if isinstance(reduced93_audit, dict) else {}
    convergence93_rows = count_csv_rows(ROOT / "data" / "rev0093_reduced_cfr_convergence.csv")
    strategy93_rows = count_csv_rows(ROOT / "data" / "rev0093_reduced_cfr_strategy.csv")
    projection93 = reduced93_checks.get("projection", {}) if isinstance(reduced93_checks, dict) else {}
    add(checks, "rev0093_reduced_cfr_converges_without_hidden_state_leakage",
        reduced93_audit.get("passed") is True
        and reduced93_summary.get("schema") == "muc5.reduced_cfr_summary.v1"
        and convergence93_rows == 6
        and strategy93_rows == 64
        and int(reduced93_checks.get("chance_deals", 0)) == 6
        and int(reduced93_checks.get("infosets", 0)) == 33
        and float(reduced93_checks.get("final_exploitability", 1.0)) < 1e-5
        and float(reduced93_checks.get("exploitability_reduction_factor", 0.0)) > 1000.0
        and int(reduced93_checks.get("pressure_jace_top_leak_rows", 99)) == 0
        and projection93.get("p0_jace_infoset_distinguishes_seen_top") is True
        and projection93.get("p1_bottom_infoset_redacts_seen_top") is True
        and projection93.get("p1_leave_infoset_redacts_seen_top") is True
        and projection93.get("p1_force_infoset_reveals_pitch_identity") is True,
        {
            "audit_passed": reduced93_audit.get("passed"),
            "convergence_rows": convergence93_rows,
            "strategy_rows": strategy93_rows,
            "checks": reduced93_checks,
        })

    add(checks, "rev0093_psro_support_pruning_refactor_is_centralized_and_tested",
        "class MixtureSupport" in psro93_source
        and "def positive_mixture_support" in psro93_source
        and "support.as_dict()" in psro93_source
        and "test_positive_mixture_support_normalizes" in (ROOT / "tests" / "test_rev0092_psro_lifecycle.py").read_text(),
        {
            "mixture_support_dataclass": "class MixtureSupport" in psro93_source,
            "helper_present": "def positive_mixture_support" in psro93_source,
            "serialized_support": "support.as_dict()" in psro93_source,
        })

    mission93 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods93 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec93 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    reduced_doc93 = (ROOT / "docs" / "reduced_cfr_rev0093.md").read_text()
    add(checks, "rev0093_current_docs_make_cfr_calibration_actionable_without_promotion",
        "rev0093" in mission93
        and "reduced equilibrium reference" in mission93
        and "rev0093 result" in methods93
        and "SPEC-CFR-002" in spec93
        and "not a full MUC-5 solve" in reduced_doc93
        and "full MUC-5 solution" in spec93,
        {
            "mission_rev": "rev0093" in mission93,
            "methods_result": "rev0093 result" in methods93,
            "spec_cfr": "SPEC-CFR-002" in spec93,
            "scope_note": "not a full MUC-5 solve" in reduced_doc93,
        })

    tier93_path = ROOT / "data" / "rev0093_evidence_tiering_catalog.json"
    tier93 = load_tiering_catalog(tier93_path) if tier93_path.exists() else {}
    tier93_summary = tier93.get("summary", {}) if isinstance(tier93, dict) else {}
    tier93_core = validate_core_tiering(ROOT, tier93) if tier93 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0093_evidence_catalog_is_latest_and_core_stays_lean",
        tier93_path.exists()
        and tier93_path.name == "rev0093_evidence_tiering_catalog.json"
        and str(tier93.get("source_cube", "")).startswith("MUCloudtainer-rev0093-")
        and tier93_summary.get("hot_core_records") == 6
        and tier93_summary.get("cold_sidecar_records") == 72
        and tier93_core.get("passed") is True,
        {
            "catalog_path": tier93_path.name if tier93_path.exists() else None,
            "source_cube": tier93.get("source_cube") if isinstance(tier93, dict) else None,
            "summary": tier93_summary,
            "core_validation": tier93_core,
        })



    # rev0094: second-oracle PSRO stress panel and effective-support pruning with error bounds.
    required_rev0094_files = [
        "src/muc5/psro_catalog.py",
        "scripts/run_rev0094_psro_stress.py",
        "tests/test_rev0094_psro_stress.py",
        "docs/psro_stress_rev0094.md",
        "data/rev0094_psro_stress_summary.json",
        "data/rev0094_psro_stress_audit.json",
        "data/rev0094_psro_challenge_games.csv",
        "data/rev0094_psro_challenge_scores.csv",
        "data/rev0094_psro_challenge_catalog.csv",
        "data/rev0094_psro_incumbent_stress.csv",
        "data/rev0094_evidence_tiering_catalog.json",
    ]
    missing_rev0094 = [path for path in required_rev0094_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0094", not missing_rev0094, {"missing": missing_rev0094})

    psro94_source = (ROOT / "src" / "muc5" / "psro.py").read_text()
    catalog94_source = (ROOT / "src" / "muc5" / "psro_catalog.py").read_text()
    tests94_source = (ROOT / "tests" / "test_rev0094_psro_stress.py").read_text()
    add(checks, "rev0094_effective_support_pruning_is_bounded_and_tested",
        "omitted_weight" in psro94_source
        and "max_score_error_from_pruning" in psro94_source
        and "support_tolerance" in psro94_source
        and "current_response_population" in catalog94_source
        and "duplicate_signatures" in catalog94_source
        and "test_effective_mixture_support_reports_tiny_pruning_error_bound" in tests94_source,
        {
            "omitted_weight_field": "omitted_weight" in psro94_source,
            "error_bound_field": "max_score_error_from_pruning" in psro94_source,
            "catalog_population": "current_response_population" in catalog94_source,
            "catalog_duplicate_guard": "duplicate_signatures" in catalog94_source,
        })

    stress94 = load_json(ROOT / "data" / "rev0094_psro_stress_summary.json")
    stress94_audit = load_json(ROOT / "data" / "rev0094_psro_stress_audit.json")
    stress94_checks = stress94_audit.get("checks", {}) if isinstance(stress94_audit, dict) else {}
    support94 = stress94.get("effective_support", {}) if isinstance(stress94, dict) else {}
    incumbent94 = stress94.get("incumbent_stress", {}) if isinstance(stress94, dict) else {}
    add(checks, "rev0094_second_oracle_stress_runs_without_promoting_or_refuting_prematurely",
        stress94_audit.get("passed") is True
        and stress94.get("schema") == "muc5.rev0094_psro_stress.v1"
        and stress94.get("status") == "second_oracle_no_confirmed_response"
        and stress94.get("strategic_policy_promoted") is False
        and support94.get("strategy_ids") == ["oracle_map_08_60_mixed_threats_counter_wall"]
        and float(support94.get("max_score_error_from_pruning", 1.0)) < 0.001
        and stress94.get("confirmed_response") is None
        and float(incumbent94.get("admitted_min_mean_score_vs_incumbents", 0.0)) > 0.55,
        {
            "audit_passed": stress94_audit.get("passed"),
            "status": stress94.get("status"),
            "effective_support": support94,
            "confirmed_response": stress94.get("confirmed_response"),
            "incumbent_stress": incumbent94,
        })

    challenge94_rows = count_csv_rows(ROOT / "data" / "rev0094_psro_challenge_games.csv")
    scores94_rows = count_csv_rows(ROOT / "data" / "rev0094_psro_challenge_scores.csv")
    catalog94_rows = count_csv_rows(ROOT / "data" / "rev0094_psro_challenge_catalog.csv")
    incumbent94_rows = count_csv_rows(ROOT / "data" / "rev0094_psro_incumbent_stress.csv")
    seed_overlaps94 = stress94_checks.get("seed_overlap_counts", {}) if isinstance(stress94_checks, dict) else {}
    stage_rows94 = stress94_checks.get("stage_game_rows", {}) if isinstance(stress94_checks, dict) else {}
    add(checks, "rev0094_stress_evidence_is_complete_seed_disjoint_and_truncation_free",
        challenge94_rows == 944
        and scores94_rows == 35
        and catalog94_rows == 23
        and incumbent94_rows == 8
        and stage_rows94.get("rev0094_challenge_selection") == 368
        and stage_rows94.get("rev0094_challenge_holdout") == 192
        and stage_rows94.get("rev0094_incumbent_stress") == 384
        and all(int(value) == 0 for value in seed_overlaps94.values())
        and stress94_checks.get("truncations") == 0,
        {
            "challenge_rows": challenge94_rows,
            "score_rows": scores94_rows,
            "catalog_rows": catalog94_rows,
            "incumbent_rows": incumbent94_rows,
            "stage_rows": stage_rows94,
            "seed_overlap_counts": seed_overlaps94,
            "truncations": stress94_checks.get("truncations"),
        })

    mission94 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods94 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec94 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    stress_doc94 = (ROOT / "docs" / "psro_stress_rev0094.md").read_text()
    add(checks, "rev0094_docs_capture_stress_result_and_next_oracle_priority",
        "rev0094" in mission94
        and "second-oracle stress panel" in mission94
        and "gameplay-driven generative oracle" in methods94
        and "Tiny nonzero solver residue" in spec94
        and "not a promotion claim" in stress_doc94,
        {
            "mission_rev0094": "rev0094" in mission94,
            "mission_stress": "second-oracle stress panel" in mission94,
            "methods_generative": "gameplay-driven generative oracle" in methods94,
            "spec_residue": "Tiny nonzero solver residue" in spec94,
            "doc_scope": "not a promotion claim" in stress_doc94,
        })

    tier94_path = ROOT / "data" / "rev0094_evidence_tiering_catalog.json"
    tier94 = load_tiering_catalog(tier94_path) if tier94_path.exists() else {}
    tier94_summary = tier94.get("summary", {}) if isinstance(tier94, dict) else {}
    tier94_core = validate_core_tiering(ROOT, tier94) if tier94 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0094_evidence_catalog_is_latest_and_core_stays_lean",
        tier94_path.exists()
        and tier94_path.name == "rev0094_evidence_tiering_catalog.json"
        and str(tier94.get("source_cube", "")).startswith("MUCloudtainer-rev0094-")
        and tier94_summary.get("hot_core_records") == 6
        and tier94_summary.get("cold_sidecar_records") == 72
        and tier94_core.get("passed") is True,
        {
            "catalog_path": None if tier94_path is None else tier94_path.name,
            "source_cube": tier94.get("source_cube") if isinstance(tier94, dict) else None,
            "summary": tier94_summary,
            "core_validation": tier94_core,
        })


    # rev0095: gameplay-driven generative MAP-Elites oracle forge.
    required_rev0095_files = [
        "src/muc5/gameplay_map_elites.py",
        "scripts/run_rev0095_gameplay_map_elites.py",
        "tests/test_rev0095_gameplay_map_elites.py",
        "docs/gameplay_map_elites_rev0095.md",
        "data/rev0095_gameplay_map_elites_summary.json",
        "data/rev0095_gameplay_map_elites_audit.json",
        "data/rev0095_gameplay_map_elites_games.csv",
        "data/rev0095_gameplay_map_elites_scores.csv",
        "data/rev0095_gameplay_map_elites_archive.csv",
        "data/rev0095_gameplay_map_elites_catalog.csv",
        "data/rev0095_evidence_tiering_catalog.json",
    ]
    missing_rev0095 = [path for path in required_rev0095_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0095", not missing_rev0095, {"missing": missing_rev0095})

    gme95_source = (ROOT / "src" / "muc5" / "gameplay_map_elites.py").read_text()
    runner95_source = (ROOT / "scripts" / "run_rev0095_gameplay_map_elites.py").read_text()
    tests95_source = (ROOT / "tests" / "test_rev0095_gameplay_map_elites.py").read_text()
    add(checks, "rev0095_gameplay_map_elites_is_generational_gameplay_scored_and_tested",
        "update_archive" in gme95_source
        and "mixture_mean_score" in gme95_source
        and "truncation penalty" in gme95_source
        and "mutate_candidate" in gme95_source
        and "random_candidate" in gme95_source
        and "generation" in runner95_source
        and "holdout_response_pass" in runner95_source
        and "test_update_archive_keeps_best_gameplay_score_per_cell" in tests95_source
        and "test_dedupe_candidates_rejects_existing_strategy_signatures" in tests95_source,
        {
            "gameplay_quality": "mixture_mean_score" in gme95_source,
            "mutator": "mutate_candidate" in gme95_source,
            "random_source": "random_candidate" in gme95_source,
            "holdout_gate": "holdout_response_pass" in runner95_source,
            "archive_test": "test_update_archive_keeps_best_gameplay_score_per_cell" in tests95_source,
            "duplicate_test": "test_dedupe_candidates_rejects_existing_strategy_signatures" in tests95_source,
        })

    gme95 = load_json(ROOT / "data" / "rev0095_gameplay_map_elites_summary.json")
    gme95_audit = load_json(ROOT / "data" / "rev0095_gameplay_map_elites_audit.json")
    gme95_checks = gme95_audit.get("checks", {}) if isinstance(gme95_audit, dict) else {}
    target95 = gme95.get("target", {}) if isinstance(gme95, dict) else {}
    support95 = target95.get("effective_support", {}) if isinstance(target95, dict) else {}
    best_holdout95 = gme95.get("holdout", [{}])[0] if isinstance(gme95.get("holdout"), list) and gme95.get("holdout") else {}
    add(checks, "rev0095_generative_oracle_runs_without_promotion_or_duplicate_leakage",
        gme95_audit.get("passed") is True
        and gme95.get("schema") == "muc5.rev0095_gameplay_map_elites.v1"
        and gme95.get("strategic_policy_promoted") is False
        and support95.get("strategy_ids") == ["oracle_map_08_60_mixed_threats_counter_wall"]
        and int(gme95.get("evaluated_candidates", 0)) == 44
        and int(gme95.get("archive_cells", 0)) == 26
        and gme95.get("confirmed_response") is None
        and float(best_holdout95.get("mixture_mean_score", 0.0)) > 0.5
        and float(best_holdout95.get("mixture_ci_low", 1.0)) < float(target95.get("challenge_threshold_with_pruning_bound", 0.0))
        and not gme95.get("duplicates_against_expanded_population"),
        {
            "audit_passed": gme95_audit.get("passed"),
            "status": gme95.get("status"),
            "strategic_policy_promoted": gme95.get("strategic_policy_promoted"),
            "effective_support": support95,
            "evaluated_candidates": gme95.get("evaluated_candidates"),
            "archive_cells": gme95.get("archive_cells"),
            "best_holdout": best_holdout95,
            "confirmed_response": gme95.get("confirmed_response"),
            "duplicates": gme95.get("duplicates_against_expanded_population"),
        })

    games95_rows = count_csv_rows(ROOT / "data" / "rev0095_gameplay_map_elites_games.csv")
    scores95_rows = count_csv_rows(ROOT / "data" / "rev0095_gameplay_map_elites_scores.csv")
    archive95_rows = count_csv_rows(ROOT / "data" / "rev0095_gameplay_map_elites_archive.csv")
    catalog95_rows = count_csv_rows(ROOT / "data" / "rev0095_gameplay_map_elites_catalog.csv")
    seed_overlaps95 = gme95_checks.get("seed_overlap_counts", {}) if isinstance(gme95_checks, dict) else {}
    stage_rows95 = gme95_checks.get("stage_game_rows", {}) if isinstance(gme95_checks, dict) else {}
    add(checks, "rev0095_generative_evidence_is_complete_seed_disjoint_and_truncation_free",
        games95_rows == 592
        and scores95_rows == 49
        and archive95_rows == 26
        and catalog95_rows == 44
        and stage_rows95.get("rev0095_gme_selection_g0") == 144
        and stage_rows95.get("rev0095_gme_selection_g1") == 112
        and stage_rows95.get("rev0095_gme_selection_g2") == 96
        and stage_rows95.get("rev0095_gme_holdout") == 240
        and all(int(value) == 0 for value in seed_overlaps95.values())
        and gme95_checks.get("truncations") == 0,
        {
            "games_rows": games95_rows,
            "score_rows": scores95_rows,
            "archive_rows": archive95_rows,
            "catalog_rows": catalog95_rows,
            "stage_rows": stage_rows95,
            "seed_overlap_counts": seed_overlaps95,
            "truncations": gme95_checks.get("truncations"),
        })

    mission95 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods95 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec95 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    gme_doc95 = (ROOT / "docs" / "gameplay_map_elites_rev0095.md").read_text()
    add(checks, "rev0095_docs_capture_generating_oracle_and_nonpromotion_scope",
        "rev0095" in mission95
        and "gameplay-driven generative MAP-Elites oracle" in mission95
        and "rev0095 result: gameplay-driven MAP-Elites oracle" in methods95
        and "SPEC-ORACLE-007" in spec95
        and "not a promotion gate" in gme_doc95,
        {
            "mission_rev0095": "rev0095" in mission95,
            "mission_gme": "gameplay-driven generative MAP-Elites oracle" in mission95,
            "methods_result": "rev0095 result: gameplay-driven MAP-Elites oracle" in methods95,
            "spec_oracle_007": "SPEC-ORACLE-007" in spec95,
            "doc_scope": "not a promotion gate" in gme_doc95,
        })

    tier95_path = ROOT / "data" / "rev0095_evidence_tiering_catalog.json"
    tier95 = load_tiering_catalog(tier95_path) if tier95_path.exists() else {}
    tier95_summary = tier95.get("summary", {}) if isinstance(tier95, dict) else {}
    tier95_core = validate_core_tiering(ROOT, tier95) if tier95 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0095_evidence_catalog_is_latest_and_core_stays_lean",
        tier95_path.exists()
        and tier95_path.name == "rev0095_evidence_tiering_catalog.json"
        and str(tier95.get("source_cube", "")).startswith("MUCloudtainer-rev0095-")
        and tier95_summary.get("hot_core_records") == 6
        and tier95_summary.get("cold_sidecar_records") == 72
        and tier95_core.get("passed") is True,
        {
            "catalog_path": None if tier95_path is None else tier95_path.name,
            "source_cube": tier95.get("source_cube") if isinstance(tier95, dict) else None,
            "summary": tier95_summary,
            "core_validation": tier95_core,
        })



    # rev0096: frozen-MLP neural response oracle and shared runner-reporting spine.
    required_rev0096_files = [
        "src/muc5/neural_oracle.py",
        "src/muc5/oracle_reporting.py",
        "scripts/run_rev0096_neural_oracle.py",
        "tests/test_rev0096_neural_oracle.py",
        "docs/neural_oracle_rev0096.md",
        "data/rev0096_neural_oracle_summary.json",
        "data/rev0096_neural_oracle_audit.json",
        "data/rev0096_neural_oracle_games.csv",
        "data/rev0096_neural_oracle_scores.csv",
        "data/rev0096_neural_oracle_catalog.csv",
        "data/rev0096_neural_oracle_deck_sources.csv",
        "data/rev0096_evidence_tiering_catalog.json",
    ]
    missing_rev0096 = [path for path in required_rev0096_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0096", not missing_rev0096, {"missing": missing_rev0096})

    neural96_source = (ROOT / "src" / "muc5" / "neural_oracle.py").read_text()
    reporting96_source = (ROOT / "src" / "muc5" / "oracle_reporting.py").read_text()
    runner95_refactor_source = (ROOT / "scripts" / "run_rev0095_gameplay_map_elites.py").read_text()
    runner96_source = (ROOT / "scripts" / "run_rev0096_neural_oracle.py").read_text()
    tests96_source = (ROOT / "tests" / "test_rev0096_neural_oracle.py").read_text()
    add(checks, "rev0096_neural_oracle_and_reporting_spine_are_bounded_and_tested",
        "NEURAL_AGENT_NAMES" in neural96_source
        and "neural_model_audit" in neural96_source
        and "neural_response_candidates" in neural96_source
        and "forbidden_signatures" in neural96_source
        and "stage_seed_overlaps" in reporting96_source
        and "flatten_score_rows" in reporting96_source
        and "from src.muc5.oracle_reporting import" in runner95_refactor_source
        and "neural_oracle_no_holdout_response" in runner96_source
        and "test_neural_model_audit_reports_frozen_mlp_shape" in tests96_source
        and "test_oracle_reporting_flattens_scores_and_detects_seed_overlap" in tests96_source,
        {
            "neural_agents": "NEURAL_AGENT_NAMES" in neural96_source,
            "model_audit": "neural_model_audit" in neural96_source,
            "candidate_generator": "neural_response_candidates" in neural96_source,
            "reporting_seed_helper": "stage_seed_overlaps" in reporting96_source,
            "rev0095_imports_reporting": "from src.muc5.oracle_reporting import" in runner95_refactor_source,
            "tests_model_audit": "test_neural_model_audit_reports_frozen_mlp_shape" in tests96_source,
        })

    neural96 = load_json(ROOT / "data" / "rev0096_neural_oracle_summary.json")
    neural96_audit = load_json(ROOT / "data" / "rev0096_neural_oracle_audit.json")
    neural96_checks = neural96_audit.get("checks", {}) if isinstance(neural96_audit, dict) else {}
    target96 = neural96.get("target", {}) if isinstance(neural96, dict) else {}
    support96 = target96.get("effective_support", {}) if isinstance(target96, dict) else {}
    model96 = neural96.get("model_audit", {}) if isinstance(neural96, dict) else {}
    best_holdout96 = neural96.get("best_holdout", {}) if isinstance(neural96, dict) else {}
    add(checks, "rev0096_frozen_mlp_oracle_runs_as_negative_control_without_promotion",
        neural96_audit.get("passed") is True
        and neural96.get("schema") == "muc5.rev0096_neural_oracle.v1"
        and neural96.get("status") == "neural_oracle_no_holdout_response"
        and neural96.get("strategic_policy_promoted") is False
        and support96.get("strategy_ids") == ["oracle_map_08_60_mixed_threats_counter_wall"]
        and int(model96.get("feature_count", 0)) == 81
        and int(model96.get("hidden_size", 0)) == 32
        and int(neural96.get("candidate_count", 0)) == 40
        and neural96.get("confirmed_response") is None
        and float(best_holdout96.get("mixture_mean_score", 1.0)) < 0.5
        and not neural96.get("duplicates_against_expanded_population"),
        {
            "audit_passed": neural96_audit.get("passed"),
            "status": neural96.get("status"),
            "strategic_policy_promoted": neural96.get("strategic_policy_promoted"),
            "effective_support": support96,
            "model_audit": model96,
            "candidate_count": neural96.get("candidate_count"),
            "best_holdout": best_holdout96,
            "confirmed_response": neural96.get("confirmed_response"),
            "duplicates": neural96.get("duplicates_against_expanded_population"),
        })

    games96_rows = count_csv_rows(ROOT / "data" / "rev0096_neural_oracle_games.csv")
    scores96_rows = count_csv_rows(ROOT / "data" / "rev0096_neural_oracle_scores.csv")
    catalog96_rows = count_csv_rows(ROOT / "data" / "rev0096_neural_oracle_catalog.csv")
    sources96_rows = count_csv_rows(ROOT / "data" / "rev0096_neural_oracle_deck_sources.csv")
    seed_overlaps96 = neural96_checks.get("seed_overlap_counts", {}) if isinstance(neural96_checks, dict) else {}
    stage_rows96 = neural96_checks.get("stage_game_rows", {}) if isinstance(neural96_checks, dict) else {}
    add(checks, "rev0096_neural_evidence_is_complete_seed_disjoint_and_truncation_free",
        games96_rows == 560
        and scores96_rows == 45
        and catalog96_rows == 40
        and sources96_rows == 11
        and stage_rows96.get("rev0096_neural_selection") == 320
        and stage_rows96.get("rev0096_neural_holdout") == 240
        and all(int(value) == 0 for value in seed_overlaps96.values())
        and neural96_checks.get("truncations") == 0,
        {
            "games_rows": games96_rows,
            "score_rows": scores96_rows,
            "catalog_rows": catalog96_rows,
            "deck_source_rows": sources96_rows,
            "stage_rows": stage_rows96,
            "seed_overlap_counts": seed_overlaps96,
            "truncations": neural96_checks.get("truncations"),
        })

    mission96 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods96 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec96 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    neural_doc96 = (ROOT / "docs" / "neural_oracle_rev0096.md").read_text()
    add(checks, "rev0096_docs_capture_frozen_mlp_negative_control_and_next_training_priority",
        "rev0096" in mission96
        and "frozen MLP" in mission96
        and "rev0096 result: frozen MLP neural oracle" in methods96
        and "SPEC-ORACLE-008" in spec96
        and "not a promotion gate" in neural_doc96
        and "train directly against the solved opponent mixture" in neural_doc96,
        {
            "mission_rev0096": "rev0096" in mission96,
            "mission_frozen_mlp": "frozen MLP" in mission96,
            "methods_result": "rev0096 result: frozen MLP neural oracle" in methods96,
            "spec_oracle_008": "SPEC-ORACLE-008" in spec96,
            "doc_scope": "not a promotion gate" in neural_doc96,
            "doc_next_training": "train directly against the solved opponent mixture" in neural_doc96,
        })

    tier96_path = ROOT / "data" / "rev0096_evidence_tiering_catalog.json"
    tier96 = load_tiering_catalog(tier96_path) if tier96_path.exists() else {}
    tier96_summary = tier96.get("summary", {}) if isinstance(tier96, dict) else {}
    tier96_core = validate_core_tiering(ROOT, tier96) if tier96 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0096_evidence_catalog_is_latest_and_core_stays_lean",
        tier96_path.exists()
        and tier96_path.name == "rev0096_evidence_tiering_catalog.json"
        and str(tier96.get("source_cube", "")).startswith("MUCloudtainer-rev0096-")
        and tier96_summary.get("hot_core_records") == 6
        and tier96_summary.get("cold_sidecar_records") == 72
        and tier96_core.get("passed") is True,
        {
            "catalog_path": tier96_path.name if tier96_path.exists() else None,
            "source_cube": tier96.get("source_cube") if isinstance(tier96, dict) else None,
            "summary": tier96_summary,
            "core_validation": tier96_core,
        })



    # rev0097: rollout-searched learned response oracle and information-state learned-agent registry.
    required_rev0097_files = [
        "src/muc5/learned_response_oracle.py",
        "scripts/run_rev0097_learned_response_oracle.py",
        "tests/test_rev0097_learned_response_oracle.py",
        "docs/learned_response_oracle_rev0097.md",
        "data/rev0097_learned_response_agent_registry.json",
        "data/rev0097_learned_response_oracle_summary.json",
        "data/rev0097_learned_response_oracle_audit.json",
        "data/rev0097_learned_response_oracle_games.csv",
        "data/rev0097_learned_response_oracle_scores.csv",
        "data/rev0097_learned_response_oracle_catalog.csv",
        "data/rev0097_learned_response_agent_registry.csv",
        "data/rev0097_learned_response_deck_sources.csv",
        "data/rev0097_evidence_tiering_catalog.json",
    ]
    missing_rev0097 = [path for path in required_rev0097_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0097", not missing_rev0097, {"missing": missing_rev0097})

    learned97_source = (ROOT / "src" / "muc5" / "learned_response_oracle.py").read_text()
    public_agents97_source = (ROOT / "src" / "muc5" / "public_agents.py").read_text()
    runner97_source = (ROOT / "scripts" / "run_rev0097_learned_response_oracle.py").read_text()
    tests97_source = (ROOT / "tests" / "test_rev0097_learned_response_oracle.py").read_text()
    add(checks, "rev0097_learned_oracle_is_registry_backed_infostate_and_tested",
        "LEARNED_FEATURE_NAMES" in learned97_source
        and "learned_feature_dict" in learned97_source
        and "frame.information_state" in learned97_source
        and "write_registry" in learned97_source
        and "sampled_learned_models" in learned97_source
        and "load_learned_response_agent" in public_agents97_source
        and "rev0097_learned_g0_training" in runner97_source
        and "test_learned_features_exercise_information_state_known_top_cards" in tests97_source,
        {
            "feature_names": "LEARNED_FEATURE_NAMES" in learned97_source,
            "uses_information_state": "frame.information_state" in learned97_source,
            "registry_writer": "write_registry" in learned97_source,
            "public_factory": "load_learned_response_agent" in public_agents97_source,
            "training_stage": "rev0097_learned_g0_training" in runner97_source,
            "infostate_feature_test": "test_learned_features_exercise_information_state_known_top_cards" in tests97_source,
        })

    learned97 = load_json(ROOT / "data" / "rev0097_learned_response_oracle_summary.json")
    learned97_audit = load_json(ROOT / "data" / "rev0097_learned_response_oracle_audit.json")
    learned97_checks = learned97_audit.get("checks", {}) if isinstance(learned97_audit, dict) else {}
    target97 = learned97.get("target", {}) if isinstance(learned97, dict) else {}
    support97 = target97.get("effective_support", {}) if isinstance(target97, dict) else {}
    learner97 = learned97.get("learner", {}) if isinstance(learned97, dict) else {}
    best_training97 = learned97.get("best_training", {}) if isinstance(learned97, dict) else {}
    best_selection97 = learned97.get("best_selection", {}) if isinstance(learned97, dict) else {}
    best_holdout97 = learned97.get("best_holdout", {}) if isinstance(learned97, dict) else {}
    add(checks, "rev0097_learned_response_oracle_runs_and_rejects_overfit_screen",
        learned97_audit.get("passed") is True
        and learned97.get("schema") == "muc5.rev0097_learned_response_oracle.v1"
        and learned97.get("status") == "learned_response_oracle_no_holdout_response"
        and learned97.get("strategic_policy_promoted") is False
        and support97.get("strategy_ids") == ["oracle_map_08_60_mixed_threats_counter_wall"]
        and int(learner97.get("feature_count", 0)) == 47
        and int(learned97.get("training_candidate_count", 0)) == 12
        and int(learned97.get("candidate_count", 0)) == 44
        and learned97.get("confirmed_response") is None
        and float(best_training97.get("mixture_mean_score", 0.0)) >= 0.75
        and float(best_selection97.get("mixture_mean_score", 0.0)) >= 0.50
        and float(best_holdout97.get("mixture_mean_score", 1.0)) < 0.5
        and not learned97.get("duplicates_against_expanded_population"),
        {
            "audit_passed": learned97_audit.get("passed"),
            "status": learned97.get("status"),
            "strategic_policy_promoted": learned97.get("strategic_policy_promoted"),
            "effective_support": support97,
            "feature_count": learner97.get("feature_count"),
            "training_candidate_count": learned97.get("training_candidate_count"),
            "candidate_count": learned97.get("candidate_count"),
            "best_training": best_training97,
            "best_selection": best_selection97,
            "best_holdout": best_holdout97,
            "confirmed_response": learned97.get("confirmed_response"),
        })

    games97_rows = count_csv_rows(ROOT / "data" / "rev0097_learned_response_oracle_games.csv")
    scores97_rows = count_csv_rows(ROOT / "data" / "rev0097_learned_response_oracle_scores.csv")
    catalog97_rows = count_csv_rows(ROOT / "data" / "rev0097_learned_response_oracle_catalog.csv")
    registry97_rows = count_csv_rows(ROOT / "data" / "rev0097_learned_response_agent_registry.csv")
    decks97_rows = count_csv_rows(ROOT / "data" / "rev0097_learned_response_deck_sources.csv")
    seed_overlaps97 = learned97_checks.get("seed_overlap_counts", {}) if isinstance(learned97_checks, dict) else {}
    stage_rows97 = learned97_checks.get("stage_game_rows", {}) if isinstance(learned97_checks, dict) else {}
    add(checks, "rev0097_learned_evidence_is_complete_seed_disjoint_and_truncation_free",
        games97_rows == 608
        and scores97_rows == 61
        and catalog97_rows == 44
        and registry97_rows == 14
        and decks97_rows == 2
        and stage_rows97.get("rev0097_learned_g0_training") == 96
        and stage_rows97.get("rev0097_learned_selection") == 352
        and stage_rows97.get("rev0097_learned_holdout") == 160
        and all(int(value) == 0 for value in seed_overlaps97.values())
        and learned97_checks.get("truncations") == 0,
        {
            "games_rows": games97_rows,
            "score_rows": scores97_rows,
            "catalog_rows": catalog97_rows,
            "registry_rows": registry97_rows,
            "deck_rows": decks97_rows,
            "stage_rows": stage_rows97,
            "seed_overlap_counts": seed_overlaps97,
            "truncations": learned97_checks.get("truncations"),
        })

    mission97 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods97 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec97 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    learned_doc97 = (ROOT / "docs" / "learned_response_oracle_rev0097.md").read_text()
    add(checks, "rev0097_docs_capture_learned_oracle_and_overfit_rejection",
        "rev0097 learned response oracle" in mission97
        and "rev0097 result: rollout-searched learned response oracle" in methods97
        and "SPEC-ORACLE-009" in spec97
        and "screen-versus-holdout failure" in learned_doc97
        and "not a promotion gate" in learned_doc97,
        {
            "mission_rev0097": "rev0097 learned response oracle" in mission97,
            "methods_result": "rev0097 result: rollout-searched learned response oracle" in methods97,
            "spec_oracle_009": "SPEC-ORACLE-009" in spec97,
            "doc_holdout_failure": "screen-versus-holdout failure" in learned_doc97,
            "doc_scope": "not a promotion gate" in learned_doc97,
        })

    tier97_path = ROOT / "data" / "rev0097_evidence_tiering_catalog.json"
    tier97 = load_tiering_catalog(tier97_path) if tier97_path.exists() else {}
    tier97_summary = tier97.get("summary", {}) if isinstance(tier97, dict) else {}
    tier97_core = validate_core_tiering(ROOT, tier97) if tier97 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0097_evidence_catalog_remains_valid_as_historical_catalog",
        tier97_path.exists()
        and tier97_path.name == "rev0097_evidence_tiering_catalog.json"
        and str(tier97.get("source_cube", "")).startswith("MUCloudtainer-rev0097-")
        and tier97_summary.get("hot_core_records") == 6
        and tier97_summary.get("cold_sidecar_records") == 72
        and tier97_core.get("passed") is True,
        {
            "catalog_path": tier97_path.name if tier97_path.exists() else None,
            "source_cube": tier97.get("source_cube") if isinstance(tier97, dict) else None,
            "summary": tier97_summary,
            "core_validation": tier97_core,
        })

    # rev0098: cross-oracle selection-bias audit and common-target frontier retest.
    required_rev0098_files = [
        "src/muc5/oracle_selection_audit.py",
        "scripts/run_rev0098_selection_audit.py",
        "tests/test_rev0098_oracle_selection_audit.py",
        "docs/selection_audit_rev0098.md",
        "data/rev0098_oracle_selection_audit_summary.json",
        "data/rev0098_oracle_selection_audit.json",
        "data/rev0098_oracle_selection_branch_summary.csv",
        "data/rev0098_oracle_selection_candidate_pairs.csv",
        "data/rev0098_frontier_retest_scores.csv",
        "data/rev0098_frontier_retest_games.csv",
        "data/rev0098_evidence_tiering_catalog.json",
    ]
    missing_rev0098 = [path for path in required_rev0098_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0098", not missing_rev0098, {"missing": missing_rev0098})

    selection98_source = (ROOT / "src" / "muc5" / "oracle_selection_audit.py").read_text()
    runner98_source = (ROOT / "scripts" / "run_rev0098_selection_audit.py").read_text()
    tests98_source = (ROOT / "tests" / "test_rev0098_oracle_selection_audit.py").read_text()
    add(checks, "rev0098_selection_bias_audit_is_cross_oracle_and_tested",
        "default_branch_specs" in selection98_source
        and "CandidateOptimism" in selection98_source
        and "top_holdout_strategy_rows" in selection98_source
        and "run_frontier_retest" in runner98_source
        and "test_selection_bias_audit_detects_learned_optimism_without_promotion" in tests98_source,
        {
            "branch_specs": "default_branch_specs" in selection98_source,
            "optimism_dataclass": "CandidateOptimism" in selection98_source,
            "frontier_rows": "top_holdout_strategy_rows" in selection98_source,
            "runner_retest": "run_frontier_retest" in runner98_source,
            "test_present": "test_selection_bias_audit_detects_learned_optimism_without_promotion" in tests98_source,
        })

    selection98 = load_json(ROOT / "data" / "rev0098_oracle_selection_audit_summary.json")
    selection98_audit = load_json(ROOT / "data" / "rev0098_oracle_selection_audit.json")
    bias98 = selection98.get("selection_bias", {}) if isinstance(selection98, dict) else {}
    aggregate98 = bias98.get("aggregate", {}) if isinstance(bias98, dict) else {}
    frontier98 = selection98.get("frontier_retest", {}) if isinstance(selection98, dict) else {}
    best_frontier98 = frontier98.get("best_challenger", {}) if isinstance(frontier98, dict) else {}
    add(checks, "rev0098_selection_bias_and_frontier_retest_reject_population_admission",
        selection98_audit.get("passed") is True
        and selection98.get("schema") == "muc5.rev0098_selection_audit_frontier_retest.v1"
        and selection98.get("status") == "selection_bias_audited_frontier_retest_complete_no_population_admission"
        and selection98.get("strategic_policy_promoted") is False
        and aggregate98.get("branches") == 4
        and aggregate98.get("heldout_candidate_pairs") == 19
        and aggregate98.get("no_branch_cleared_holdout_ci_threshold") is True
        and aggregate98.get("worst_branch_best_screen_to_holdout_gap_branch") == "learned_response_rev0097"
        and frontier98.get("game_rows") == 480
        and frontier98.get("truncations") == 0
        and frontier98.get("no_challenger_clears_half_by_ci_low") is True
        and float(best_frontier98.get("mean_score", 1.0)) < 0.5,
        {
            "audit_passed": selection98_audit.get("passed"),
            "status": selection98.get("status"),
            "strategic_policy_promoted": selection98.get("strategic_policy_promoted"),
            "aggregate": aggregate98,
            "frontier_game_rows": frontier98.get("game_rows"),
            "frontier_truncations": frontier98.get("truncations"),
            "best_frontier_challenger": best_frontier98,
        })

    branch98_rows = count_csv_rows(ROOT / "data" / "rev0098_oracle_selection_branch_summary.csv")
    pair98_rows = count_csv_rows(ROOT / "data" / "rev0098_oracle_selection_candidate_pairs.csv")
    score98_rows = count_csv_rows(ROOT / "data" / "rev0098_frontier_retest_scores.csv")
    game98_rows = count_csv_rows(ROOT / "data" / "rev0098_frontier_retest_games.csv")
    frontier_seed_overlaps98 = frontier98.get("seed_overlap_counts", {}) if isinstance(frontier98, dict) else {}
    add(checks, "rev0098_evidence_is_complete_seed_disjoint_and_truncation_free",
        branch98_rows == 4
        and pair98_rows == 19
        and score98_rows == 5
        and game98_rows == 480
        and frontier98.get("truncations") == 0
        and all(int(value) == 0 for value in frontier_seed_overlaps98.values()),
        {
            "branch_rows": branch98_rows,
            "pair_rows": pair98_rows,
            "score_rows": score98_rows,
            "game_rows": game98_rows,
            "seed_overlap_counts": frontier_seed_overlaps98,
            "truncations": frontier98.get("truncations"),
        })

    mission98 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods98 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec98 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    selection_doc98 = (ROOT / "docs" / "selection_audit_rev0098.md").read_text()
    add(checks, "rev0098_docs_capture_selection_bias_frontier_retest_and_nonpromotion",
        "rev0098 selection-bias audit" in mission98
        and "rev0098 result: oracle selection audit" in methods98
        and "SPEC-ORACLE-010" in spec98
        and "No population admission" in selection_doc98
        and "winner's-curse" in selection_doc98,
        {
            "mission_rev0098": "rev0098 selection-bias audit" in mission98,
            "methods_result": "rev0098 result: oracle selection audit" in methods98,
            "spec_oracle_010": "SPEC-ORACLE-010" in spec98,
            "doc_nonpromotion": "No population admission" in selection_doc98,
            "doc_winners_curse": "winner's-curse" in selection_doc98,
        })

    tier98_path = find_tiering_catalog(ROOT)
    tier98 = load_tiering_catalog(tier98_path) if tier98_path is not None else {}
    tier98_summary = tier98.get("summary", {}) if isinstance(tier98, dict) else {}
    tier98_core = validate_core_tiering(ROOT, tier98) if tier98 else {"passed": False, "errors": ["missing catalog"]}
    rev0098_tier_path = ROOT / "data" / "rev0098_evidence_tiering_catalog.json"
    rev0098_tier = load_tiering_catalog(rev0098_tier_path) if rev0098_tier_path.exists() else {}
    rev0098_tier_summary = rev0098_tier.get("summary", {}) if isinstance(rev0098_tier, dict) else {}
    rev0098_tier_core = validate_core_tiering(ROOT, rev0098_tier) if rev0098_tier else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0098_evidence_catalog_remains_valid_as_historical_catalog",
        rev0098_tier_path.exists()
        and rev0098_tier_summary.get("hot_core_records") == 6
        and rev0098_tier_summary.get("cold_sidecar_records") == 72
        and rev0098_tier_core.get("passed") is True,
        {
            "catalog_path": rev0098_tier_path.name,
            "source_cube": rev0098_tier.get("source_cube") if isinstance(rev0098_tier, dict) else None,
            "summary": rev0098_tier_summary,
            "core_validation": rev0098_tier_core,
        })

    # rev0099: balanced focal-pair evaluation design and expanded-matrix refresh.
    required_rev0099_files = [
        "src/muc5/evaluation_design.py",
        "scripts/run_rev0099_matrix_refresh.py",
        "tests/test_rev0099_evaluation_design.py",
        "docs/matrix_refresh_rev0099.md",
        "data/rev0099_expanded_matrix_refresh_summary.json",
        "data/rev0099_expanded_matrix_refresh_audit.json",
        "data/rev0099_expanded_matrix_games.csv",
        "data/rev0099_expanded_matrix_cells.csv",
        "data/rev0099_expanded_matrix_pair_estimates.csv",
        "data/rev0099_expanded_matrix_strategy_summary.csv",
        "data/rev0099_pair_symmetry_summary.csv",
        "data/rev0099_evidence_tiering_catalog.json",
    ]
    missing_rev0099 = [path for path in required_rev0099_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0099", not missing_rev0099, {"missing": missing_rev0099})

    eval_design99_source = (ROOT / "src" / "muc5" / "evaluation_design.py").read_text()
    psro99_source = (ROOT / "src" / "muc5" / "psro.py").read_text()
    runner99_source = (ROOT / "scripts" / "run_rev0099_matrix_refresh.py").read_text()
    tests99_source = (ROOT / "tests" / "test_rev0099_evaluation_design.py").read_text()
    add(checks, "rev0099_balanced_evaluation_design_is_shared_and_tested",
        "balanced_pair_cells" in eval_design99_source
        and "audit_balanced_focal_rows" in eval_design99_source
        and "pair_symmetry_rows" in eval_design99_source
        and "balanced_pair_cells(config.life_totals, config.reps)" in psro99_source
        and "run_rev0099_matrix_refresh" in str(ROOT / "scripts" / "run_rev0099_matrix_refresh.py")
        and "test_empirical_evaluator_emits_canonical_balanced_rows" in tests99_source,
        {
            "balanced_pair_cells": "balanced_pair_cells" in eval_design99_source,
            "balance_audit": "audit_balanced_focal_rows" in eval_design99_source,
            "pair_symmetry": "pair_symmetry_rows" in eval_design99_source,
            "psro_uses_helper": "balanced_pair_cells(config.life_totals, config.reps)" in psro99_source,
            "runner_has_refresh": "build_symmetric_empirical_game" in runner99_source,
            "test_present": "test_empirical_evaluator_emits_canonical_balanced_rows" in tests99_source,
        })

    matrix99 = load_json(ROOT / "data" / "rev0099_expanded_matrix_refresh_summary.json")
    matrix99_audit = load_json(ROOT / "data" / "rev0099_expanded_matrix_refresh_audit.json")
    checks99 = matrix99.get("audit_checks", {}) if isinstance(matrix99, dict) else {}
    admitted99 = matrix99.get("admitted_response_summary", {}) if isinstance(matrix99, dict) else {}
    add(checks, "rev0099_expanded_matrix_refresh_is_balanced_constant_sum_and_nonpromotional",
        matrix99_audit.get("passed") is True
        and matrix99.get("schema") == "muc5.rev0099_expanded_matrix_refresh.v1"
        and matrix99.get("status") == "balanced_expanded_population_matrix_refreshed"
        and matrix99.get("strategic_policy_promoted") is False
        and checks99.get("strategy_count") == 9
        and checks99.get("pair_estimates") == 36
        and checks99.get("game_rows") == 2880
        and checks99.get("truncations") == 0
        and checks99.get("balance_passed") is True
        and float(checks99.get("antisymmetry_error", 1.0)) <= 1e-12
        and float(checks99.get("diagonal_error", 1.0)) <= 1e-12
        and matrix99.get("effective_support_1e_3") == ["oracle_map_08_60_mixed_threats_counter_wall"]
        and abs(float(admitted99.get("pure_floor_vs_population", -1.0)) - 0.5) <= 1e-12,
        {
            "audit_passed": matrix99_audit.get("passed"),
            "status": matrix99.get("status"),
            "strategic_policy_promoted": matrix99.get("strategic_policy_promoted"),
            "audit_checks": checks99,
            "effective_support_1e_3": matrix99.get("effective_support_1e_3"),
            "admitted_summary": admitted99,
        })

    games99_rows = count_csv_rows(ROOT / "data" / "rev0099_expanded_matrix_games.csv")
    cells99_rows = count_csv_rows(ROOT / "data" / "rev0099_expanded_matrix_cells.csv")
    pair99_rows = count_csv_rows(ROOT / "data" / "rev0099_expanded_matrix_pair_estimates.csv")
    strategy99_rows = count_csv_rows(ROOT / "data" / "rev0099_expanded_matrix_strategy_summary.csv")
    symmetry99_rows = count_csv_rows(ROOT / "data" / "rev0099_pair_symmetry_summary.csv")
    add(checks, "rev0099_evidence_tables_have_expected_matrix_shape",
        games99_rows == 2880
        and cells99_rows == 81
        and pair99_rows == 36
        and strategy99_rows == 9
        and symmetry99_rows == 36,
        {
            "games_rows": games99_rows,
            "matrix_cell_rows": cells99_rows,
            "pair_estimate_rows": pair99_rows,
            "strategy_summary_rows": strategy99_rows,
            "pair_symmetry_rows": symmetry99_rows,
        })

    mission99 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods99 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec99 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    matrix_doc99 = (ROOT / "docs" / "matrix_refresh_rev0099.md").read_text()
    add(checks, "rev0099_docs_capture_matrix_refresh_and_nonpromotion",
        "What rev0099 adds" in mission99
        and "rev0099 result: matrix refresh" in methods99
        and "SPEC-ORACLE-011" in spec99
        and "not a strategic promotion" in matrix_doc99
        and "2,880" in matrix_doc99,
        {
            "mission_rev0099": "What rev0099 adds" in mission99,
            "methods_result": "rev0099 result: matrix refresh" in methods99,
            "spec_oracle_011": "SPEC-ORACLE-011" in spec99,
            "doc_nonpromotion": "not a strategic promotion" in matrix_doc99,
            "doc_game_rows": "2,880" in matrix_doc99,
        })

    tier99_path = ROOT / "data" / "rev0099_evidence_tiering_catalog.json"
    tier99 = load_tiering_catalog(tier99_path) if tier99_path.exists() else {}
    tier99_summary = tier99.get("summary", {}) if isinstance(tier99, dict) else {}
    tier99_core = validate_core_tiering(ROOT, tier99) if tier99 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0099_evidence_catalog_remains_valid_as_historical_catalog",
        tier99_path.exists()
        and tier99_summary.get("hot_core_records") == 6
        and tier99_summary.get("cold_sidecar_records") == 72
        and tier99_core.get("passed") is True,
        {
            "catalog_path": tier99_path.name,
            "source_cube": tier99.get("source_cube") if isinstance(tier99, dict) else None,
            "summary": tier99_summary,
            "core_validation": tier99_core,
        })

    # rev0100: confidence floor and self-diagonal disambiguation for admitted PSRO response.
    required_rev0100_files = [
        "src/muc5/confidence_floor.py",
        "scripts/run_rev0100_confidence_floor.py",
        "tests/test_rev0100_confidence_floor.py",
        "docs/confidence_floor_rev0100.md",
        "data/rev0100_confidence_floor_summary.json",
        "data/rev0100_confidence_floor_audit.json",
        "data/rev0100_confidence_floor_games.csv",
        "data/rev0100_confidence_floor_pair_estimates.csv",
        "data/rev0100_confidence_floor_pair_symmetry.csv",
        "data/rev0100_confidence_floor_strategies.csv",
        "data/rev0100_evidence_tiering_catalog.json",
    ]
    missing_rev0100 = [path for path in required_rev0100_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0100", not missing_rev0100, {"missing": missing_rev0100})

    confidence100_source = (ROOT / "src" / "muc5" / "confidence_floor.py").read_text() if (ROOT / "src" / "muc5" / "confidence_floor.py").exists() else ""
    runner100_source = (ROOT / "scripts" / "run_rev0100_confidence_floor.py").read_text() if (ROOT / "scripts" / "run_rev0100_confidence_floor.py").exists() else ""
    tests100_source = (ROOT / "tests" / "test_rev0100_confidence_floor.py").read_text() if (ROOT / "tests" / "test_rev0100_confidence_floor.py").exists() else ""
    add(checks, "rev0100_confidence_floor_helpers_are_executable_and_tested",
        "compare_matrix_self_floor" in confidence100_source
        and "floor_from_estimates" in confidence100_source
        and "require_no_seed_overlap" in confidence100_source
        and "rev0100_incumbent_confidence_floor" in runner100_source
        and "test_matrix_floor_distinguishes_self_diagonal_from_opponents" in tests100_source,
        {
            "has_self_floor_helper": "compare_matrix_self_floor" in confidence100_source,
            "has_floor_helper": "floor_from_estimates" in confidence100_source,
            "has_seed_overlap_helper": "require_no_seed_overlap" in confidence100_source,
            "runner_stage": "rev0100_incumbent_confidence_floor" in runner100_source,
            "test_present": "test_matrix_floor_distinguishes_self_diagonal_from_opponents" in tests100_source,
        })

    floor100 = load_json(ROOT / "data" / "rev0100_confidence_floor_summary.json")
    floor100_audit = load_json(ROOT / "data" / "rev0100_confidence_floor_audit.json")
    checks100 = floor100.get("audit_checks", {}) if isinstance(floor100, dict) else {}
    floor100_summary = floor100.get("floor_summary", {}) if isinstance(floor100, dict) else {}
    matrix100_comparison = floor100.get("matrix_self_floor_comparison", {}) if isinstance(floor100, dict) else {}
    add(checks, "rev0100_confidence_floor_audit_is_balanced_nonpromotional_and_clears_incumbent_floor",
        floor100_audit.get("passed") is True
        and floor100.get("schema") == "muc5.rev0100_confidence_floor.v1"
        and floor100.get("status") == "admitted_response_confidence_floor_audited"
        and floor100.get("strategic_policy_promoted") is False
        and checks100.get("game_rows") == 2160
        and checks100.get("games_per_pair") == 240
        and checks100.get("truncations") == 0
        and checks100.get("balance_passed") is True
        and checks100.get("seed_overlap_passed") is True
        and checks100.get("self_diagonal_is_rev0099_floor") is True
        and abs(float(checks100.get("rev0099_floor_with_self", -1.0)) - 0.5) <= 1e-12
        and float(checks100.get("rev0099_floor_without_self", 0.0)) > 0.6
        and float(checks100.get("rev0100_min_incumbent_ci_low", 0.0)) > 0.5
        and checks100.get("confidence_floor_cleared") is True
        and floor100.get("confidence_floor_cleared") is True,
        {
            "audit_passed": floor100_audit.get("passed"),
            "status": floor100.get("status"),
            "strategic_policy_promoted": floor100.get("strategic_policy_promoted"),
            "audit_checks": checks100,
            "floor_summary": floor100_summary,
            "matrix_self_floor_comparison": matrix100_comparison,
        })

    games100_rows = count_csv_rows(ROOT / "data" / "rev0100_confidence_floor_games.csv")
    pair100_rows = count_csv_rows(ROOT / "data" / "rev0100_confidence_floor_pair_estimates.csv")
    symmetry100_rows = count_csv_rows(ROOT / "data" / "rev0100_confidence_floor_pair_symmetry.csv")
    strategy100_rows = count_csv_rows(ROOT / "data" / "rev0100_confidence_floor_strategies.csv")
    add(checks, "rev0100_evidence_tables_have_expected_confidence_floor_shape",
        games100_rows == 2160
        and pair100_rows == 9
        and symmetry100_rows == 9
        and strategy100_rows == 9,
        {
            "games_rows": games100_rows,
            "pair_estimate_rows": pair100_rows,
            "pair_symmetry_rows": symmetry100_rows,
            "strategy_rows": strategy100_rows,
        })

    mission100 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods100 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec100 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    floor_doc100 = (ROOT / "docs" / "confidence_floor_rev0100.md").read_text() if (ROOT / "docs" / "confidence_floor_rev0100.md").exists() else ""
    add(checks, "rev0100_docs_capture_confidence_floor_and_self_diagonal_scope",
        "What rev0100 adds" in mission100
        and "rev0100 result: confidence floor audit" in methods100
        and "SPEC-ORACLE-012" in spec100
        and "self diagonal" in floor_doc100.lower()
        and "not a strategic promotion" in floor_doc100,
        {
            "mission_rev0100": "What rev0100 adds" in mission100,
            "methods_result": "rev0100 result: confidence floor audit" in methods100,
            "spec_oracle_012": "SPEC-ORACLE-012" in spec100,
            "doc_self_diagonal": "self diagonal" in floor_doc100.lower(),
            "doc_nonpromotion": "not a strategic promotion" in floor_doc100,
        })

    tier100_path = ROOT / "data" / "rev0100_evidence_tiering_catalog.json"
    tier100 = load_tiering_catalog(tier100_path) if tier100_path.exists() else {}
    tier100_summary = tier100.get("summary", {}) if isinstance(tier100, dict) else {}
    tier100_core = validate_core_tiering(ROOT, tier100) if tier100 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0100_evidence_catalog_remains_valid_as_historical_catalog",
        tier100_path.exists()
        and tier100_path.name == "rev0100_evidence_tiering_catalog.json"
        and tier100_summary.get("hot_core_records") == 6
        and tier100_summary.get("cold_sidecar_records") == 72
        and tier100_core.get("passed") is True,
        {
            "catalog_path": tier100_path.name if tier100_path.exists() else None,
            "source_cube": tier100.get("source_cube") if isinstance(tier100, dict) else None,
            "summary": tier100_summary,
            "core_validation": tier100_core,
        })



    # rev0101: out-of-distribution transfer stress for admitted PSRO response.
    required_rev0101_files = [
        "src/muc5/transfer_stress.py",
        "scripts/run_rev0101_transfer_stress.py",
        "tests/test_rev0101_transfer_stress.py",
        "docs/transfer_stress_rev0101.md",
        "data/rev0101_transfer_stress_summary.json",
        "data/rev0101_transfer_stress_audit.json",
        "data/rev0101_transfer_stress_panel.csv",
        "data/rev0101_transfer_stress_games.csv",
        "data/rev0101_transfer_stress_pair_estimates.csv",
        "data/rev0101_transfer_stress_family_summary.csv",
        "data/rev0101_transfer_stress_pair_symmetry.csv",
        "data/rev0101_transfer_stress_self_control.csv",
        "data/rev0101_transfer_stress_truncation_rescue.csv",
        "data/rev0101_evidence_tiering_catalog.json",
    ]
    missing_rev0101 = [path for path in required_rev0101_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0101", not missing_rev0101, {"missing": missing_rev0101})

    transfer101_source = (ROOT / "src" / "muc5" / "transfer_stress.py").read_text() if (ROOT / "src" / "muc5" / "transfer_stress.py").exists() else ""
    runner101_source = (ROOT / "scripts" / "run_rev0101_transfer_stress.py").read_text() if (ROOT / "scripts" / "run_rev0101_transfer_stress.py").exists() else ""
    tests101_source = (ROOT / "tests" / "test_rev0101_transfer_stress.py").read_text() if (ROOT / "tests" / "test_rev0101_transfer_stress.py").exists() else ""
    add(checks, "rev0101_transfer_stress_helpers_are_executable_and_tested",
        "rev0101_transfer_stress_panel" in transfer101_source
        and "audit_transfer_stress_panel" in transfer101_source
        and "summarize_transfer_stress" in transfer101_source
        and "rescue_truncated_cells" in runner101_source
        and "test_rev0101_panel_is_legal_unique_and_not_target_duplicate" in tests101_source,
        {
            "has_panel_builder": "rev0101_transfer_stress_panel" in transfer101_source,
            "has_panel_audit": "audit_transfer_stress_panel" in transfer101_source,
            "has_summary": "summarize_transfer_stress" in transfer101_source,
            "runner_has_rescue": "rescue_truncated_cells" in runner101_source,
            "test_present": "test_rev0101_panel_is_legal_unique_and_not_target_duplicate" in tests101_source,
        })

    transfer101 = load_json(ROOT / "data" / "rev0101_transfer_stress_summary.json")
    transfer101_audit = load_json(ROOT / "data" / "rev0101_transfer_stress_audit.json")
    transfer101_summary = transfer101.get("summary", {}) if isinstance(transfer101, dict) else {}
    transfer101_rescue = transfer101.get("truncation_rescue", {}) if isinstance(transfer101, dict) else {}
    transfer101_panel_audit = transfer101.get("panel_audit", {}) if isinstance(transfer101, dict) else {}
    add(checks, "rev0101_transfer_stress_is_balanced_structural_audit_and_nonpromotional",
        transfer101_audit.get("passed") is True
        and transfer101.get("schema") == "muc5.rev0101.transfer_stress_summary.v1"
        and transfer101.get("status") == "ood_mean_floor_survives_but_truncation_or_confidence_floor_remains_open"
        and transfer101.get("strategic_policy_promoted") is False
        and transfer101_summary.get("panel_size") == 13
        and transfer101_summary.get("total_games") == 2080
        and transfer101.get("ood_game_rows") == 2080
        and transfer101.get("self_control_rows") == 160
        and transfer101.get("total_game_rows") == 2240
        and transfer101.get("design_audit_passed") is True
        and transfer101.get("self_design_audit_passed") is True
        and transfer101.get("seed_audit_passed") is True
        and transfer101_panel_audit.get("passed") is True
        and transfer101_summary.get("confidence_floor_cleared") is False
        and transfer101_summary.get("min_mean_score") > 0.5
        and transfer101_summary.get("min_ci_low") < 0.5
        and transfer101_summary.get("weakest_ci_opponent") == "ood_counter_jace40"
        and transfer101_rescue.get("attempted") is True
        and transfer101_rescue.get("original_truncated_rows") == 1
        and transfer101_rescue.get("remaining_truncations_after_rescue") == 1,
        {
            "audit_passed": transfer101_audit.get("passed"),
            "status": transfer101.get("status"),
            "strategic_policy_promoted": transfer101.get("strategic_policy_promoted"),
            "summary": transfer101_summary,
            "truncation_rescue": transfer101_rescue,
            "panel_audit": transfer101_panel_audit,
        })

    games101_rows = count_csv_rows(ROOT / "data" / "rev0101_transfer_stress_games.csv")
    pair101_rows = count_csv_rows(ROOT / "data" / "rev0101_transfer_stress_pair_estimates.csv")
    panel101_rows = count_csv_rows(ROOT / "data" / "rev0101_transfer_stress_panel.csv")
    family101_rows = count_csv_rows(ROOT / "data" / "rev0101_transfer_stress_family_summary.csv")
    symmetry101_rows = count_csv_rows(ROOT / "data" / "rev0101_transfer_stress_pair_symmetry.csv")
    self101_rows = count_csv_rows(ROOT / "data" / "rev0101_transfer_stress_self_control.csv")
    rescue101_rows = count_csv_rows(ROOT / "data" / "rev0101_transfer_stress_truncation_rescue.csv")
    add(checks, "rev0101_evidence_tables_have_expected_transfer_stress_shape",
        games101_rows == 2080
        and pair101_rows == 13
        and panel101_rows == 13
        and family101_rows == 4
        and symmetry101_rows == 14
        and self101_rows == 1
        and rescue101_rows == 1,
        {
            "games_rows": games101_rows,
            "pair_estimate_rows": pair101_rows,
            "panel_rows": panel101_rows,
            "family_rows": family101_rows,
            "pair_symmetry_rows": symmetry101_rows,
            "self_control_rows": self101_rows,
            "rescue_rows": rescue101_rows,
        })

    mission101 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods101 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec101 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    stress_doc101 = (ROOT / "docs" / "transfer_stress_rev0101.md").read_text() if (ROOT / "docs" / "transfer_stress_rev0101.md").exists() else ""
    add(checks, "rev0101_docs_capture_ood_transfer_scope_and_open_axis",
        "What rev0101 adds" in mission101
        and "rev0101 result: OOD transfer stress" in methods101
        and "SPEC-ORACLE-013" in spec101
        and "not a strategic promotion" in stress_doc101
        and "ood_counter_jace40" in stress_doc101,
        {
            "mission_rev0101": "What rev0101 adds" in mission101,
            "methods_result": "rev0101 result: OOD transfer stress" in methods101,
            "spec_oracle_013": "SPEC-ORACLE-013" in spec101,
            "doc_nonpromotion": "not a strategic promotion" in stress_doc101,
            "doc_weak_axis": "ood_counter_jace40" in stress_doc101,
        })

    tier101_path = ROOT / "data" / "rev0101_evidence_tiering_catalog.json"
    tier101 = load_tiering_catalog(tier101_path) if tier101_path.exists() else {}
    tier101_summary = tier101.get("summary", {}) if isinstance(tier101, dict) else {}
    tier101_core = validate_core_tiering(ROOT, tier101) if tier101 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0101_evidence_catalog_remains_valid_as_historical_catalog",
        tier101_path.exists()
        and tier101_path.name == "rev0101_evidence_tiering_catalog.json"
        and str(tier101.get("source_cube", "")).startswith("MUCloudtainer-rev0101-")
        and tier101_summary.get("hot_core_records") == 6
        and tier101_summary.get("cold_sidecar_records") == 72
        and tier101_core.get("passed") is True,
        {
            "catalog_path": tier101_path.name if tier101_path.exists() else None,
            "source_cube": tier101.get("source_cube") if isinstance(tier101, dict) else None,
            "summary": tier101_summary,
            "core_validation": tier101_core,
        })



    # rev0102: counter-control/Jace long-game cap ladder and axis refresh.
    required_rev0102_files = [
        "src/muc5/longgame.py",
        "scripts/run_rev0102_longgame_cap_ladder.py",
        "tests/test_rev0102_longgame_cap_ladder.py",
        "docs/longgame_cap_ladder_rev0102.md",
        "data/rev0102_longgame_cap_ladder_summary.json",
        "data/rev0102_longgame_cap_ladder_audit.json",
        "data/rev0102_longgame_cap_ladder_rows.csv",
        "data/rev0102_counter_jace_axis_games.csv",
        "data/rev0102_counter_jace_axis_pair_estimate.csv",
        "data/rev0102_counter_jace_axis_pair_symmetry.csv",
        "data/rev0102_evidence_tiering_catalog.json",
    ]
    missing_rev0102 = [path for path in required_rev0102_files if not (ROOT / path).exists()]
    add(checks, "required_files_present_rev0102", not missing_rev0102, {"missing": missing_rev0102})

    longgame102_source = (ROOT / "src" / "muc5" / "longgame.py").read_text() if (ROOT / "src" / "muc5" / "longgame.py").exists() else ""
    runner102_source = (ROOT / "scripts" / "run_rev0102_longgame_cap_ladder.py").read_text() if (ROOT / "scripts" / "run_rev0102_longgame_cap_ladder.py").exists() else ""
    tests102_source = (ROOT / "tests" / "test_rev0102_longgame_cap_ladder.py").read_text() if (ROOT / "tests" / "test_rev0102_longgame_cap_ladder.py").exists() else ""
    add(checks, "rev0102_longgame_helpers_are_executable_and_tested",
        "longgame_snapshot" in longgame102_source
        and "run_cap_ladder_cell" in longgame102_source
        and "evaluate_focal_pair_with_snapshots" in longgame102_source
        and "COUNTER_AXIS_ID" in runner102_source
        and "test_rev0102_cap_ladder_replays_same_seed_across_caps" in tests102_source,
        {
            "has_snapshot": "longgame_snapshot" in longgame102_source,
            "has_cap_ladder": "run_cap_ladder_cell" in longgame102_source,
            "has_snapshot_pair_eval": "evaluate_focal_pair_with_snapshots" in longgame102_source,
            "runner_counter_axis": "COUNTER_AXIS_ID" in runner102_source,
            "test_present": "test_rev0102_cap_ladder_replays_same_seed_across_caps" in tests102_source,
        })

    long102 = load_json(ROOT / "data" / "rev0102_longgame_cap_ladder_summary.json")
    long102_audit = load_json(ROOT / "data" / "rev0102_longgame_cap_ladder_audit.json")
    axis102 = long102.get("axis_summary", {}) if isinstance(long102, dict) else {}
    cap102 = long102.get("cap_ladder", {}) if isinstance(long102, dict) else {}
    add(checks, "rev0102_longgame_audit_is_structural_nonpromotional_and_blocks_overclaim",
        long102_audit.get("passed") is True
        and long102.get("schema") == "muc5.rev0102.longgame_cap_ladder_summary.v1"
        and long102.get("opponent_strategy") == "ood_counter_jace40"
        and long102.get("strategic_policy_promoted") is False
        and long102.get("snapshot_leakage_violations") == 0
        and long102.get("status") == "counter_jace_axis_still_open_due_to_confidence_or_persistent_cap"
        and axis102.get("games") == 192
        and axis102.get("truncations") == 1
        and axis102.get("ci_low") > 0.5
        and axis102.get("confidence_floor_cleared") is False
        and cap102.get("rows") == 5
        and cap102.get("remaining_truncated_at_max_cap") is True
        and cap102.get("resolved") is False,
        {
            "audit_passed": long102_audit.get("passed"),
            "status": long102.get("status"),
            "axis_summary": axis102,
            "cap_ladder": cap102,
            "strategic_policy_promoted": long102.get("strategic_policy_promoted"),
        })

    cap102_rows = count_csv_rows(ROOT / "data" / "rev0102_longgame_cap_ladder_rows.csv")
    axis102_rows = count_csv_rows(ROOT / "data" / "rev0102_counter_jace_axis_games.csv")
    pair102_rows = count_csv_rows(ROOT / "data" / "rev0102_counter_jace_axis_pair_estimate.csv")
    symmetry102_rows = count_csv_rows(ROOT / "data" / "rev0102_counter_jace_axis_pair_symmetry.csv")
    add(checks, "rev0102_evidence_tables_have_expected_longgame_shape",
        cap102_rows == 5
        and axis102_rows == 192
        and pair102_rows == 1
        and symmetry102_rows == 1,
        {
            "cap_ladder_rows": cap102_rows,
            "axis_game_rows": axis102_rows,
            "pair_estimate_rows": pair102_rows,
            "symmetry_rows": symmetry102_rows,
        })

    mission102 = (ROOT / "docs" / "CURRENT_MISSION.md").read_text()
    methods102 = (ROOT / "docs" / "CURRENT_METHODS.md").read_text()
    spec102 = (ROOT / "docs" / "CURRENT_SPEC.md").read_text()
    long_doc102 = (ROOT / "docs" / "longgame_cap_ladder_rev0102.md").read_text() if (ROOT / "docs" / "longgame_cap_ladder_rev0102.md").exists() else ""
    add(checks, "rev0102_docs_capture_longgame_scope_and_no_adjudication",
        "What rev0102 adds" in mission102
        and "rev0102 result: long-game cap ladder" in methods102
        and "SPEC-ORACLE-014" in spec102
        and "does **not** promote a strategy" in long_doc102
        and "does **not** replace terminal scoring" in long_doc102,
        {
            "mission_rev0102": "What rev0102 adds" in mission102,
            "methods_result": "rev0102 result: long-game cap ladder" in methods102,
            "spec_oracle_014": "SPEC-ORACLE-014" in spec102,
            "doc_nonpromotion": "does **not** promote a strategy" in long_doc102,
            "doc_no_adjudication": "does **not** replace terminal scoring" in long_doc102,
        })

    tier102_path = find_tiering_catalog(ROOT)
    tier102 = load_tiering_catalog(tier102_path) if tier102_path is not None else {}
    tier102_summary = tier102.get("summary", {}) if isinstance(tier102, dict) else {}
    tier102_core = validate_core_tiering(ROOT, tier102) if tier102 else {"passed": False, "errors": ["missing catalog"]}
    add(checks, "rev0102_evidence_catalog_is_latest_and_core_stays_lean",
        tier102_path is not None
        and tier102_path.name == "rev0102_evidence_tiering_catalog.json"
        and tier102.get("source_cube") == ROOT.name
        and tier102_summary.get("hot_core_records") == 6
        and tier102_summary.get("cold_sidecar_records") == 72
        and tier102_core.get("passed") is True,
        {
            "catalog_path": None if tier102_path is None else tier102_path.name,
            "source_cube": tier102.get("source_cube") if isinstance(tier102, dict) else None,
            "summary": tier102_summary,
            "core_validation": tier102_core,
        })

    passed = all(c["passed"] for c in checks)
    report = {
        "revision": "rev0102",
        "audit_focus": "Inherited controls plus rev0092 episode/PSRO safety, rev0093 reduced CFR calibration, rev0094 effective-support stress, rev0095 MAP-Elites oracle, rev0096 frozen-MLP negative control, rev0097 learned-response oracle, rev0098 selection-bias/frontier retest, rev0099 balanced-design expanded-matrix refresh, rev0100 confidence-floor/self-diagonal audit, rev0101 OOD transfer-stress audit, and rev0102 long-game cap-ladder audit.",
        "passed": passed,
        "checks": checks,
    }
    out = ROOT / "data" / "rev0102_audit.json"
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
