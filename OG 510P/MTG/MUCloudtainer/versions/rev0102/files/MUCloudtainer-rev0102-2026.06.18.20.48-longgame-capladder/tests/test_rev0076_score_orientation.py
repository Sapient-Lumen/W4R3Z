from __future__ import annotations

from src.muc5.population_score_audit import audit_population_score_orientation_rows
from src.muc5.terminal_mechanisms import annotate_focus_target_from_seat, target_score_from_seat
from src.muc5.threat_response import annotate_threat_response_rows


def _row(*, seat: int, p0: float, p1: float, winner: int, loss_reason: str) -> dict[str, object]:
    score = p0 if seat == 0 else p1
    return {
        "simulator_revision": "revtest",
        "cpp_shadow_game_id": f"g-seat{seat}",
        "target_seat": seat,
        "focus_target_seat": seat,
        "p0_score": p0,
        "p1_score": p1,
        "winner": winner,
        "loss_reason": loss_reason,
        "terminal_clean_status": "terminal",
        "focus_target_score": score,
        "focus_target_result": "target_win" if score > 0.5 else "target_loss",
        "focus_terminal_mechanism": "library_out" if "library" in loss_reason else "life_total",
        "focus_terminal_loser": 1 - winner,
        "focus_terminal_loser_role": "opponent" if winner == seat else "target",
        "focus_is_library_out_win": score > 0.5 and "library" in loss_reason,
        "focus_is_life_total_win": score > 0.5 and "life" in loss_reason,
    }


def test_canonical_target_score_uses_target_seat_not_left_player() -> None:
    row = _row(seat=1, p0=1.0, p1=0.0, winner=0, loss_reason="player_1_attempted_to_draw_from_empty_library")
    assert target_score_from_seat(row, 1) == 0.0
    annotated = annotate_focus_target_from_seat(row)
    assert annotated["focus_target_seat"] == 1
    assert annotated["focus_target_score"] == 0.0
    assert annotated["focus_target_result"] == "target_loss"
    assert annotated["focus_terminal_loser_role"] == "target"


def test_threat_response_annotator_uses_shared_focus_orientation_helper() -> None:
    raw = {
        "cpp_shadow_game_id": "gid",
        "p0_score": 0.0,
        "p1_score": 1.0,
        "winner": 1,
        "loss_reason": "player_0_life_total_zero_or_less",
        "terminal_clean_status": "terminal",
    }
    meta = {"gid": {"target_seat": 1, "arm_id": "A"}}
    annotated = annotate_threat_response_rows([raw], meta)[0]
    assert annotated["focus_target_score"] == 1.0
    assert annotated["focus_target_result"] == "target_win"
    assert annotated["focus_terminal_loser_role"] == "opponent"
    assert annotated["focus_is_life_total_win"] is True


def test_score_orientation_audit_detects_seat_flipped_score_error() -> None:
    row = _row(seat=1, p0=1.0, p1=0.0, winner=0, loss_reason="player_1_life_total_zero_or_less")
    row["focus_target_score"] = 1.0  # the dangerous hand-rolled p0-score mistake
    mismatches, summary = audit_population_score_orientation_rows([row], source_file="unit.csv")
    assert summary["passed"] is False
    assert summary["mismatches"] >= 1
    assert any(m["check"] == "focus_target_score" for m in mismatches)


def test_score_orientation_audit_passes_balanced_seat_pair() -> None:
    rows = [
        _row(seat=0, p0=1.0, p1=0.0, winner=0, loss_reason="player_1_attempted_to_draw_from_empty_library"),
        _row(seat=1, p0=0.0, p1=1.0, winner=1, loss_reason="player_0_attempted_to_draw_from_empty_library"),
    ]
    mismatches, summary = audit_population_score_orientation_rows(rows, source_file="unit.csv")
    assert mismatches == []
    assert summary["passed"] is True
    assert summary["target_seat_counts"] == {"0": 1, "1": 1}
