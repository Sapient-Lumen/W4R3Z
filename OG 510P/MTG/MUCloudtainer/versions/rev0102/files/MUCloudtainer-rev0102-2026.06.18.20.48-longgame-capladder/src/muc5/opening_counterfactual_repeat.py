from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, replace
from random import Random
from typing import Dict, List, Mapping, Sequence, Tuple

from .cards import CARD_ORDER
from .cpp_transition import (
    TransitionMicroRecord,
    cpp_transition_signatures,
    cpp_transition_tool_status,
    is_supported_transition,
    state_signature,
    transition_record_from_state_action,
    with_jace_ultimate_shuffle_transport,
)
from .deckspace import DeckVector
from .engine import deck_to_library
from .mulligan_ranker import opening_hand_quality
from .opening_counterfactual import (
    CounterfactualPairSpec,
    CounterfactualTransitionRow,
    _counts_row,
    _first_seven_counts,
    make_forced_branch,
    make_opponent_pregame,
    play_counterfactual_branch,
)


@dataclass(frozen=True)
class RepeatedCounterfactualResult:
    """Repeated keep-vs-mulligan opening counterfactual outputs.

    ``branch_rows`` contains one game per branch rollout.  ``paired_rows`` is one
    row per opening situation after averaging repeated keep and mulligan branch
    rollouts.  ``transition_rows`` is a C++ shadow-check sample of every branch
    transition recorded by the panel.
    """

    branch_rows: Tuple[Dict[str, object], ...]
    paired_rows: Tuple[Dict[str, object], ...]
    transition_rows: Tuple[CounterfactualTransitionRow, ...]
    summary: Dict[str, object]


def _mean(xs: Sequence[float]) -> float:
    return float(sum(xs) / len(xs)) if xs else 0.0


def _variance(xs: Sequence[float]) -> float:
    if len(xs) <= 1:
        return 0.0
    m = _mean(xs)
    return float(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def _boolish(x: object) -> bool:
    return str(x).lower() in {"true", "1", "yes"}


def _retag_transition_rows(rows: List[CounterfactualTransitionRow], *, revision_pair_id: str) -> None:
    """Retag transition pair ids in-place for readability if needed."""

    # Currently transition rows are emitted with the rollout-specific pair id.
    # Keep that detail; this hook remains for future segment grouping.
    return None


def run_repeated_opening_counterfactual_panel(
    specs: Sequence[CounterfactualPairSpec],
    *,
    rollout_reps: int = 4,
    rollout_seed_stride: int = 7919,
    revision: str = "rev0030",
) -> RepeatedCounterfactualResult:
    """Run repeated branch rollouts for the same first seven-card looks.

    The pregame branch construction is held fixed for each ``spec``: same first
    opening seven, same opponent pregame hand/library, same forced first keep or
    mulligan decision, and same fallback mulligan policy after that first
    decision.  Only the gameplay rollout seeds vary across reps.

    This gives a less noisy label than the rev0028/rev0029 one-rollout-per-branch
    counterfactual data.
    """

    branch_rows: List[Dict[str, object]] = []
    paired_rows: List[Dict[str, object]] = []
    transition_rows: List[CounterfactualTransitionRow] = []
    records: List[TransitionMicroRecord] = []
    expected: List[str] = []
    row_indices: List[int] = []

    for spec in specs:
        deck_rng0 = Random(spec.seed + 11)
        deck_rng1 = Random(spec.seed + 97)
        initial_library0 = deck_to_library(spec.deck0, deck_rng0)
        initial_library1 = deck_to_library(spec.deck1, deck_rng1)
        first7 = _first_seven_counts(initial_library0)
        first7_quality = opening_hand_quality(first7, spec.deck0.counts(), spec.starting_life, 0)
        opponent = make_opponent_pregame(
            initial_library=initial_library1,
            agent=spec.mulligan1,
            player=1,
            seed=spec.seed + 1009,
            starting_life=spec.starting_life,
            deck_counts=spec.deck1.counts(),
        )
        branches = {
            "keep": make_forced_branch(
                branch="keep",
                initial_library=initial_library0,
                agent=spec.fallback_mulligan0,
                player=0,
                seed=spec.seed + 2003,
                starting_life=spec.starting_life,
                deck_counts=spec.deck0.counts(),
            ),
            "mulligan": make_forced_branch(
                branch="mulligan",
                initial_library=initial_library0,
                agent=spec.fallback_mulligan0,
                player=0,
                seed=spec.seed + 2003,
                starting_life=spec.starting_life,
                deck_counts=spec.deck0.counts(),
            ),
        }
        by_branch_scores: Dict[str, List[float]] = {"keep": [], "mulligan": []}
        by_branch_trunc: Dict[str, int] = {"keep": 0, "mulligan": 0}
        by_branch_decisions: Dict[str, List[float]] = {"keep": [], "mulligan": []}
        by_branch_wins: Dict[str, int] = {"keep": 0, "mulligan": 0}
        by_branch_mulls: Dict[str, int] = {}
        by_branch_kept_size: Dict[str, int] = {}

        for rep_i in range(int(rollout_reps)):
            rollout_seed = spec.seed + 73000 + rep_i * int(rollout_seed_stride)
            for branch_name, branch in branches.items():
                rollout_spec = replace(
                    spec,
                    pair_id=f"{spec.pair_id}_rep{rep_i:02d}",
                    seed=rollout_seed,
                )
                row = play_counterfactual_branch(
                    rollout_spec,
                    branch,
                    opponent,
                    transition_rows=transition_rows,
                    records=records,
                    expected=expected,
                    row_indices=row_indices,
                )
                row.update(
                    {
                        "base_pair_id": spec.pair_id,
                        "rollout_rep": rep_i,
                        "initial_hand_quality": first7_quality,
                        **_counts_row("initial_hand", first7),
                    }
                )
                branch_rows.append(row)
                score = float(row["p0_score"])
                by_branch_scores[branch_name].append(score)
                by_branch_decisions[branch_name].append(float(row.get("decisions", 0) or 0))
                by_branch_trunc[branch_name] += 1 if _boolish(row.get("is_truncation")) else 0
                by_branch_wins[branch_name] += 1 if str(row.get("winner")) == "0" else 0
                by_branch_mulls[branch_name] = int(row["branch_mulligans_taken"])
                by_branch_kept_size[branch_name] = int(row["branch_kept_hand_size"])

        keep_scores = by_branch_scores["keep"]
        mull_scores = by_branch_scores["mulligan"]
        keep_mean = _mean(keep_scores)
        mull_mean = _mean(mull_scores)
        delta = mull_mean - keep_mean
        paired_rows.append(
            {
                "pair_id": spec.pair_id,
                "deck0": spec.deck0_name,
                "deck1": spec.deck1_name,
                "agent0": spec.agent0,
                "agent1": spec.agent1,
                "fallback_mulligan0": spec.fallback_mulligan0,
                "mulligan1": spec.mulligan1,
                "starting_life": int(spec.starting_life),
                "starting_player": int(spec.starting_player),
                "seed": int(spec.seed),
                "rollout_reps": int(rollout_reps),
                "initial_hand_quality": float(first7_quality),
                **_counts_row("initial_hand", first7),
                "keep_score_mean": keep_mean,
                "mulligan_score_mean": mull_mean,
                "mulligan_minus_keep_mean": delta,
                "keep_score_var": _variance(keep_scores),
                "mulligan_score_var": _variance(mull_scores),
                "keep_win_rate": by_branch_wins["keep"] / max(1, int(rollout_reps)),
                "mulligan_win_rate": by_branch_wins["mulligan"] / max(1, int(rollout_reps)),
                "keep_truncations": by_branch_trunc["keep"],
                "mulligan_truncations": by_branch_trunc["mulligan"],
                "keep_decisions_mean": _mean(by_branch_decisions["keep"]),
                "mulligan_decisions_mean": _mean(by_branch_decisions["mulligan"]),
                "keep_mulligans_taken": by_branch_mulls.get("keep", 0),
                "mulligan_mulligans_taken": by_branch_mulls.get("mulligan", 0),
                "keep_kept_hand_size": by_branch_kept_size.get("keep", 7),
                "mulligan_kept_hand_size": by_branch_kept_size.get("mulligan", 6),
                "better_branch_mean": "mulligan" if delta > 0 else ("keep" if delta < 0 else "tie"),
                "abs_delta_mean": abs(delta),
                "label_confidence_proxy": abs(delta) / max(0.125, (_variance(keep_scores) + _variance(mull_scores)) ** 0.5),
            }
        )

    mismatches = 0
    if records:
        actual = cpp_transition_signatures(records)
        for rec_i, (got, want) in enumerate(zip(actual, expected)):
            row_idx = row_indices[rec_i]
            old = transition_rows[row_idx]
            ok = got == want
            if not ok:
                mismatches += 1
            transition_rows[row_idx] = CounterfactualTransitionRow(
                pair_id=old.pair_id,
                branch=old.branch,
                step=old.step,
                player=old.player,
                frame=old.frame,
                pending_choice_kind=old.pending_choice_kind,
                stack_depth=old.stack_depth,
                action_kind=old.action_kind,
                action=old.action,
                supported_by_cpp=old.supported_by_cpp,
                cpp_match=ok,
                case_id=old.case_id,
            )
    events = len(transition_rows)
    supported = sum(1 for r in transition_rows if r.supported_by_cpp)
    summary: Dict[str, object] = {
        "revision": revision,
        "specs": len(specs),
        "rollout_reps": int(rollout_reps),
        "branch_games": len(branch_rows),
        "paired_rows": len(paired_rows),
        "transition_events": events,
        "supported_cpp_events": supported,
        "skipped_cpp_events": events - supported,
        "cpp_mismatches": mismatches,
        "cpp_support_rate": 0.0 if events == 0 else supported / events,
        "cpp_match_rate_on_supported": 1.0 if supported == 0 else (supported - mismatches) / supported,
        "truncations": sum(1 for r in branch_rows if _boolish(r.get("is_truncation"))),
        "mulligan_better_pairs": sum(1 for r in paired_rows if r["better_branch_mean"] == "mulligan"),
        "keep_better_pairs": sum(1 for r in paired_rows if r["better_branch_mean"] == "keep"),
        "tie_pairs": sum(1 for r in paired_rows if r["better_branch_mean"] == "tie"),
        "mean_mulligan_minus_keep": _mean([float(r["mulligan_minus_keep_mean"]) for r in paired_rows]),
        "mean_abs_delta": _mean([float(r["abs_delta_mean"]) for r in paired_rows]),
        "mean_label_confidence_proxy": _mean([float(r["label_confidence_proxy"]) for r in paired_rows]),
        "tool_status": cpp_transition_tool_status().as_dict(),
    }
    return RepeatedCounterfactualResult(
        branch_rows=tuple(branch_rows),
        paired_rows=tuple(paired_rows),
        transition_rows=tuple(transition_rows),
        summary=summary,
    )
