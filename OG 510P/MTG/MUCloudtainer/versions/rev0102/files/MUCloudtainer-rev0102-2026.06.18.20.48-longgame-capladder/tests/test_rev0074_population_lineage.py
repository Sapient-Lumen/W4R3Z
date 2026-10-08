from __future__ import annotations

from src.muc5.population_lineage import (
    compare_recomputed_to_source_summaries,
    raw_population_lineage_checks,
    source_qualified_game_id,
    summarize_population_raw_games,
)


def _game(source_revision: str, local_id: str, seed: int, score: float, result: str, *, target_seat: int, starting_player: int) -> dict[str, object]:
    return {
        "source_revision": source_revision,
        "simulator_revision": source_revision,
        "cpp_shadow_game_id": local_id,
        "seed": seed,
        "transition_seed": seed + 1000,
        "agent_seed": seed + 2000,
        "arm_id": "A_guard_vs_closure_counter40_vs_threat40",
        "starting_life": 20,
        "starting_player": starting_player,
        "target_seat": target_seat,
        "rep": 0,
        "size_axis": "counter40_vs_threat40",
        "counter_policy_axis": "public_counter_guard",
        "threat_policy_axis": "library_aware_threat_closure_targetguarded",
        "target_deck_size": 40,
        "opponent_deck_size": 40,
        "target": "guard_counter_wall40",
        "opponent": "pub_threat40_closure",
        "focus_target_score": score,
        "focus_target_result": result,
        "focus_terminal_mechanism": "library_out" if result == "target_win" else "life_total",
        "focus_is_library_out_win": result == "target_win",
        "focus_is_life_total_win": False,
        "terminal_clean_status": "terminal",
        "is_truncation": False,
        "decisions": 10 + seed % 3,
        "turn_number": 4 + seed % 2,
    }


def test_source_qualified_game_id_fixes_cross_revision_local_collision() -> None:
    a = _game("rev0069", "g00000", 1, 1.0, "target_win", target_seat=0, starting_player=0)
    b = _game("rev0070", "g00000", 2, 0.0, "target_loss", target_seat=0, starting_player=0)
    assert a["cpp_shadow_game_id"] == b["cpp_shadow_game_id"]
    assert source_qualified_game_id(a) == "rev0069:g00000"
    assert source_qualified_game_id(b) == "rev0070:g00000"


def test_raw_lineage_allows_local_id_duplicates_but_requires_qualified_seed_uniqueness() -> None:
    rows = [
        _game("rev0069", "g00000", 1, 1.0, "target_win", target_seat=0, starting_player=0),
        _game("rev0069", "g00001", 2, 0.0, "target_loss", target_seat=0, starting_player=1),
        _game("rev0069", "g00002", 3, 0.0, "target_loss", target_seat=1, starting_player=0),
        _game("rev0069", "g00003", 4, 1.0, "target_win", target_seat=1, starting_player=1),
        _game("rev0070", "g00000", 5, 1.0, "target_win", target_seat=0, starting_player=0),
        _game("rev0070", "g00004", 6, 0.0, "target_loss", target_seat=0, starting_player=1),
        _game("rev0070", "g00005", 7, 0.0, "target_loss", target_seat=1, starting_player=0),
        _game("rev0070", "g00006", 8, 1.0, "target_win", target_seat=1, starting_player=1),
    ]
    audit = raw_population_lineage_checks(rows)
    assert audit["local_cpp_shadow_game_id_duplicates"] == 1
    assert audit["source_qualified_game_id_duplicates"] == 0
    assert audit["seed_duplicates"] == 0
    assert audit["imbalanced_groups"] == 0
    assert audit["passed"] is True


def test_recomputed_raw_summary_matches_source_summary_columns() -> None:
    rows = [
        _game("rev0069", "g00000", 1, 1.0, "target_win", target_seat=0, starting_player=0),
        _game("rev0069", "g00001", 2, 0.0, "target_loss", target_seat=0, starting_player=1),
        _game("rev0069", "g00002", 3, 0.0, "target_loss", target_seat=1, starting_player=0),
        _game("rev0069", "g00003", 4, 1.0, "target_win", target_seat=1, starting_player=1),
    ]
    [summary] = summarize_population_raw_games(rows)
    assert summary["games"] == 4
    assert summary["target_mean_score_draw_half"] == 0.5
    assert summary["target_terminal_wins"] == 2
    assert summary["target_terminal_losses"] == 2
    assert summary["target_library_out_wins"] == 2
    source_summary = [{k: v for k, v in summary.items() if k != "source_revision"}]
    assert compare_recomputed_to_source_summaries([summary], source_summary) == []
    source_summary[0]["games"] = 5
    mismatches = compare_recomputed_to_source_summaries([summary], source_summary)
    assert mismatches and mismatches[0]["column"] == "games"
