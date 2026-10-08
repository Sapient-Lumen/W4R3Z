from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any, Mapping, Sequence

from .cpp_rollout import CppShadowGameSpec
from .payoff import StrategyBundle
from .statgate import hoeffding_interval, wilson_interval


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _score_for_strategy(row: Mapping[str, Any], strategy: str) -> float | None:
    if str(row.get("strategy0")) == strategy:
        return float(row.get("p0_score", 0.0))
    if str(row.get("strategy1")) == strategy:
        return float(row.get("p1_score", 0.0))
    return None


def _terminal_win_for_strategy(row: Mapping[str, Any], strategy: str) -> float | None:
    if str(row.get("strategy0")) == strategy:
        return float(row.get("p0_terminal_win", 0.0))
    if str(row.get("strategy1")) == strategy:
        return float(row.get("p1_terminal_win", 0.0))
    return None


def strategy_ids_from_claims(
    claim_rows: Sequence[Mapping[str, Any]],
    *,
    labels: Sequence[str] = ("robust_candidate", "life_sensitive_candidate"),
    top_n: int = 3,
) -> list[str]:
    """Select the strategies that deserve deeper terminal-clean repetitions.

    The claim ledger is an agenda, not a theorem.  This helper keeps the agenda
    explicit by pulling robust/life-sensitive rows first, then filling by
    meta-rank/mean score if the requested budget is not met.
    """

    wanted_labels = {str(x) for x in labels}
    chosen: list[str] = []
    for row in claim_rows:
        if str(row.get("claim_label")) in wanted_labels and str(row.get("strategy")) not in chosen:
            chosen.append(str(row["strategy"]))
        if len(chosen) >= top_n:
            return chosen[:top_n]
    for row in sorted(
        claim_rows,
        key=lambda r: (
            float(r.get("meta_rank_mass", 0.0)),
            float(r.get("mean_score_draw_half", 0.0)),
            -float(r.get("meta_rank", 9999) or 9999),
        ),
        reverse=True,
    ):
        s = str(row.get("strategy"))
        if s and s not in chosen:
            chosen.append(s)
        if len(chosen) >= top_n:
            break
    return chosen[:top_n]


def targeted_strategy_pair_specs(
    strategies: Sequence[StrategyBundle],
    *,
    target_ids: Sequence[str],
    simulator_revision: str,
    life_totals: Sequence[int] = (20, 40),
    reps: int = 2,
    base_seed: int = 5100000,
    max_decisions: int = 900,
) -> tuple[CppShadowGameSpec, ...]:
    """Build an ordered payoff grid focused on selected target strategies.

    The grid includes every ordered pair where at least one side is a target,
    across life totals, starting-player positions, and reps.  This spends extra
    sample budget where the previous terminal-clean claim ledger asked for it,
    while preserving the same public DecisionFrame / C++ shadow rollout path.
    """

    target_set = set(map(str, target_ids))
    specs: list[CppShadowGameSpec] = []
    k = 0
    for life in life_totals:
        for i, left in enumerate(strategies):
            for j, right in enumerate(strategies):
                if left.strategy_id not in target_set and right.strategy_id not in target_set:
                    continue
                for starting_player in (0, 1):
                    for rep in range(reps):
                        specs.append(
                            CppShadowGameSpec(
                                game_id=f"g{k:05d}_life{int(life)}_sp{starting_player}_{left.strategy_id}_vs_{right.strategy_id}_r{rep}",
                                strategy0=left.strategy_id,
                                strategy1=right.strategy_id,
                                deck0_name=left.deck_name,
                                deck1_name=right.deck_name,
                                deck0=left.deck,
                                deck1=right.deck,
                                agent0=left.agent_name,
                                agent1=right.agent_name,
                                mulligan0=str(left.mulligan_policy),
                                mulligan1=str(right.mulligan_policy),
                                seed=int(base_seed + k),
                                starting_player=int(starting_player),
                                starting_life=int(life),
                                max_decisions=int(max_decisions),
                                simulator_revision=simulator_revision,
                            )
                        )
                        k += 1
    return tuple(specs)


def annotate_focus_rows(rows: Sequence[Mapping[str, Any]], target_ids: Sequence[str]) -> list[dict[str, Any]]:
    target_set = set(map(str, target_ids))
    out: list[dict[str, Any]] = []
    for row in rows:
        r = dict(row)
        s0 = str(r.get("strategy0"))
        s1 = str(r.get("strategy1"))
        targets = [s for s in (s0, s1) if s in target_set]
        r["focus_targets"] = ";".join(targets)
        if s0 in target_set and s1 in target_set:
            kind = "target_vs_target"
        elif s0 in target_set:
            kind = "target_as_p0"
        elif s1 in target_set:
            kind = "target_as_p1"
        else:
            kind = "field_only"
        r["focus_kind"] = kind
        out.append(r)
    return out


@dataclass(frozen=True)
class DeepClaimGate:
    passed: bool
    revision: str
    targets: tuple[str, ...]
    raw_rows: int
    truncations: int
    cpp_mismatches: int
    cpp_skipped: int
    min_target_games: int
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def deep_claim_gate(
    rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    target_ids: Sequence[str],
    cpp_summary: Mapping[str, Any] | None = None,
    min_rows: int = 300,
    min_target_games: int = 96,
) -> DeepClaimGate:
    errors: list[str] = []
    warnings: list[str] = []
    if len(rows) < min_rows:
        errors.append(f"raw_rows {len(rows)} below min_rows {min_rows}")
    truncations = sum(1 for r in rows if _truthy(r.get("is_truncation")) or str(r.get("loss_reason")) == "max_decisions_reached")
    if truncations:
        errors.append(f"{truncations} truncation rows in deep terminal-clean panel")
    per_target = {}
    for target in target_ids:
        n = sum(1 for r in rows if _score_for_strategy(r, str(target)) is not None)
        per_target[str(target)] = n
        if n < min_target_games:
            errors.append(f"target {target} has {n} games below {min_target_games}")
    cpp_mismatches = int((cpp_summary or {}).get("mismatches", 0))
    cpp_skipped = int((cpp_summary or {}).get("skipped_events", 0))
    if cpp_mismatches:
        errors.append(f"C++ shadow mismatches: {cpp_mismatches}")
    if cpp_skipped:
        errors.append(f"C++ skipped events: {cpp_skipped}")
    if len(target_ids) < 2:
        warnings.append("only one target selected; life/pair deep claims will be narrow")
    return DeepClaimGate(
        passed=not errors,
        revision=str(revision),
        targets=tuple(map(str, target_ids)),
        raw_rows=len(rows),
        truncations=truncations,
        cpp_mismatches=cpp_mismatches,
        cpp_skipped=cpp_skipped,
        min_target_games=min(per_target.values()) if per_target else 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _status(mean_score: float, lcb: float, life_delta: float, games: int) -> str:
    if games < 96:
        return "needs_more_games"
    if lcb >= 0.50 and mean_score >= 0.60 and abs(life_delta) <= 0.10:
        return "deep_robust_signal"
    if mean_score >= 0.56 and abs(life_delta) >= 0.15:
        return "deep_life_sensitive_signal"
    if mean_score >= 0.55:
        return "deep_field_signal"
    return "deep_watchlist"


def deep_target_summary_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    target_ids: Sequence[str],
    previous_claim_rows: Sequence[Mapping[str, Any]] = (),
    life_totals: Sequence[int] = (20, 40),
) -> list[dict[str, Any]]:
    prev = {str(r.get("strategy")): r for r in previous_claim_rows}
    out: list[dict[str, Any]] = []
    for target in map(str, target_ids):
        scores = []
        wins = []
        by_life: dict[int, list[float]] = {int(l): [] for l in life_totals}
        by_life_wins: dict[int, list[float]] = {int(l): [] for l in life_totals}
        for row in rows:
            sc = _score_for_strategy(row, target)
            tw = _terminal_win_for_strategy(row, target)
            if sc is None:
                continue
            scores.append(sc)
            wins.append(0.0 if tw is None else tw)
            life = int(row.get("starting_life", -1))
            if life in by_life:
                by_life[life].append(sc)
                by_life_wins[life].append(0.0 if tw is None else tw)
        n = len(scores)
        mean_score = mean(scores) if scores else 0.0
        win_rate = mean(wins) if wins else 0.0
        ci = hoeffding_interval(mean_score, n)
        wci = wilson_interval(sum(wins), n)
        row: dict[str, Any] = {
            "strategy": target,
            "games": n,
            "mean_score_draw_half": mean_score,
            "score_lcb_95": ci.low,
            "score_ucb_95": ci.high,
            "terminal_win_rate": win_rate,
            "terminal_win_lcb_95": wci.low,
            "previous_claim_label": str(prev.get(target, {}).get("claim_label", "")),
            "previous_meta_rank": prev.get(target, {}).get("meta_rank", ""),
            "previous_meta_rank_mass": prev.get(target, {}).get("meta_rank_mass", ""),
        }
        life_means = {}
        for life in map(int, life_totals):
            vals = by_life.get(life, [])
            win_vals = by_life_wins.get(life, [])
            life_means[life] = mean(vals) if vals else 0.0
            row[f"games_life{life}"] = len(vals)
            row[f"score_life{life}"] = life_means[life]
            row[f"terminal_win_life{life}"] = mean(win_vals) if win_vals else 0.0
        lives = list(map(int, life_totals))
        if len(lives) >= 2:
            lo, hi = lives[0], lives[-1]
            row["score_life_delta_hi_minus_lo"] = life_means[hi] - life_means[lo]
            row["abs_score_life_delta"] = abs(life_means[hi] - life_means[lo])
            row["life_bias"] = "life40" if life_means[hi] > life_means[lo] + 1e-12 else ("life20" if life_means[lo] > life_means[hi] + 1e-12 else "flat")
        else:
            row["score_life_delta_hi_minus_lo"] = 0.0
            row["abs_score_life_delta"] = 0.0
            row["life_bias"] = "flat"
        row["deep_claim_label"] = _status(mean_score, ci.low, float(row["score_life_delta_hi_minus_lo"]), n)
        out.append(row)
    out.sort(key=lambda r: (r["score_lcb_95"], r["mean_score_draw_half"]), reverse=True)
    return out


def deep_pair_rows(rows: Sequence[Mapping[str, Any]], *, target_ids: Sequence[str]) -> list[dict[str, Any]]:
    """Seat-symmetric target-vs-opponent rows for focused human review."""

    target_set = set(map(str, target_ids))
    buckets: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    wins: dict[tuple[str, str, int], list[float]] = defaultdict(list)
    for row in rows:
        life = int(row.get("starting_life", -1))
        for side in (0, 1):
            target = str(row.get(f"strategy{side}"))
            if target not in target_set:
                continue
            opp = str(row.get(f"strategy{1-side}"))
            key = (target, opp, life)
            buckets[key].append(float(row.get(f"p{side}_score", 0.0)))
            wins[key].append(float(row.get(f"p{side}_terminal_win", 0.0)))
    out: list[dict[str, Any]] = []
    for (target, opp, life), vals in sorted(buckets.items()):
        n = len(vals)
        mean_score = mean(vals) if vals else 0.0
        ci = hoeffding_interval(mean_score, n)
        out.append(
            {
                "target": target,
                "opponent": opp,
                "starting_life": life,
                "games": n,
                "mean_score_draw_half": mean_score,
                "score_lcb_95": ci.low,
                "score_ucb_95": ci.high,
                "terminal_win_rate": mean(wins[(target, opp, life)]) if wins[(target, opp, life)] else 0.0,
                "pair_signal": "favored" if ci.low > 0.5 else ("unfavored" if ci.high < 0.5 else "uncertain"),
            }
        )
    out.sort(key=lambda r: (r["target"], r["starting_life"], -r["mean_score_draw_half"], r["opponent"]))
    return out
