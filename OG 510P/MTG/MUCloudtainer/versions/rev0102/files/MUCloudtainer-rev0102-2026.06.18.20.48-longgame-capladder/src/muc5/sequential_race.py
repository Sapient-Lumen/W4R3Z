from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence

from .deckspace import DeckVector
from .mulligan import POLICY_LAND_BAND, POLICY_LAND_BAND_BUSINESS
from .payoff import StrategyBundle
from .public_payoff import play_public_strategy_pair_row
from .statgate import statistical_standings


@dataclass(frozen=True)
class RaceStage:
    stage: int
    reps_this_stage: int
    raw_rows_after_stage: int
    alive_before: int
    alive_after: int
    best_strategy: str
    best_lcb: float
    eliminated: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def bundle_from_mapelite_row(row: Mapping[str, object], idx: int) -> StrategyBundle:
    deck = DeckVector(
        int(row["deck_size"]),
        int(row["island"]),
        int(row["counterspell"]),
        int(row["force"]),
        int(row["jace"]),
        int(row["overlord"]),
    )
    deck.validate()
    jace = int(row["jace"])
    overlord = int(row["overlord"])
    force = int(row["force"])
    if jace >= overlord and jace > 0:
        agent = "code_jace_lock_rev0013"
    elif force >= 8:
        agent = "code_force_conservative_rev0013"
    else:
        agent = "code_overlord_clock_rev0013"
    policy = POLICY_LAND_BAND_BUSINESS if deck.size == 40 or force >= 8 else POLICY_LAND_BAND
    cell = str(row.get("cell_id", f"cell_{idx}"))
    compact_cell = cell.replace("|", "_").replace("/", "_")[:80]
    return StrategyBundle(
        strategy_id=f"mapelite_{idx:02d}_{compact_cell}",
        deck_name=f"mapelite_{idx:02d}",
        deck=deck,
        agent_name=agent,
        mulligan_policy=policy,
    )


def load_mapelite_bundles(path: str | Path, *, limit: int = 6) -> List[StrategyBundle]:
    bundles: List[StrategyBundle] = []
    with Path(path).open(newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            bundles.append(bundle_from_mapelite_row(row, idx))
            if len(bundles) >= limit:
                break
    return bundles


def play_candidate_probe_rows(
    candidates: Sequence[StrategyBundle],
    opponents: Sequence[StrategyBundle],
    *,
    simulator_revision: str,
    stage: int,
    reps: int,
    base_seed: int,
    life_totals: Sequence[int] = (20, 40),
    max_decisions: int = 500,
) -> List[dict[str, object]]:
    rows: List[dict[str, object]] = []
    k = 0
    for cand in candidates:
        for opp in opponents:
            for life in life_totals:
                for starting_player in (0, 1):
                    for rep in range(reps):
                        seed = base_seed + k
                        left = play_public_strategy_pair_row(
                            cand,
                            opp,
                            simulator_revision=simulator_revision,
                            seed=seed,
                            starting_player=starting_player,
                            starting_life=int(life),
                            max_decisions=max_decisions,
                        )
                        left.update({"stage": stage, "stage_rep": rep, "candidate_side": 0, "candidate": cand.strategy_id})
                        rows.append(left)
                        k += 1
                        seed = base_seed + k
                        right = play_public_strategy_pair_row(
                            opp,
                            cand,
                            simulator_revision=simulator_revision,
                            seed=seed,
                            starting_player=starting_player,
                            starting_life=int(life),
                            max_decisions=max_decisions,
                        )
                        right.update({"stage": stage, "stage_rep": rep, "candidate_side": 1, "candidate": cand.strategy_id})
                        rows.append(right)
                        k += 1
    return rows


def race_candidates(
    candidates: Sequence[StrategyBundle],
    opponents: Sequence[StrategyBundle],
    *,
    simulator_revision: str,
    stage_reps: Sequence[int] = (1, 2),
    base_seed: int = 161600,
    max_decisions: int = 500,
    eliminate_after_games: int = 16,
    slack: float = 0.0,
) -> tuple[List[dict[str, object]], List[RaceStage], List[dict[str, object]]]:
    """Small sequential-racing scaffold.

    This is not a formal racing algorithm yet. It is a cautious cloudtainer-bound
    pruning tool: gather a stage of games, compute conservative bounded-score
    intervals, and eliminate only candidates whose UCB is below the best LCB.
    """

    alive = list(candidates)
    all_rows: List[dict[str, object]] = []
    stages: List[RaceStage] = []
    standings: List[dict[str, object]] = []
    for stage_idx, reps in enumerate(stage_reps, 1):
        before = len(alive)
        rows = play_candidate_probe_rows(
            alive,
            opponents,
            simulator_revision=simulator_revision,
            stage=stage_idx,
            reps=int(reps),
            base_seed=base_seed + stage_idx * 100000,
            max_decisions=max_decisions,
        )
        all_rows.extend(rows)
        candidate_ids = {c.strategy_id for c in alive}
        standings_all = statistical_standings(all_rows, alpha=0.10, min_games_for_claim=eliminate_after_games)
        standings = [r for r in standings_all if r["strategy"] in candidate_ids]
        best_lcb = max((float(r["score_lcb_95"]) for r in standings), default=0.0)
        best_strategy = next((str(r["strategy"]) for r in standings if float(r["score_lcb_95"]) == best_lcb), "")
        eliminate = []
        if stage_idx < len(stage_reps):
            for r in standings:
                if int(r["games"]) >= eliminate_after_games and float(r["score_ucb_95"]) + slack < best_lcb:
                    eliminate.append(str(r["strategy"]))
        alive = [c for c in alive if c.strategy_id not in set(eliminate)]
        stages.append(
            RaceStage(
                stage=stage_idx,
                reps_this_stage=int(reps),
                raw_rows_after_stage=len(all_rows),
                alive_before=before,
                alive_after=len(alive),
                best_strategy=best_strategy,
                best_lcb=best_lcb,
                eliminated=tuple(eliminate),
            )
        )
        if not alive:
            break
    return all_rows, stages, standings
