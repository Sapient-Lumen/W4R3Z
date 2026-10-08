from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple

from .reward_guard import audit_payoff_like_row


REQUIRED_PAYOFF_COLUMNS: Tuple[str, ...] = (
    "simulator_revision",
    "strategy0",
    "strategy1",
    "deck0",
    "deck1",
    "agent0",
    "agent1",
    "mulligan0",
    "mulligan1",
    "starting_life",
    "starting_player",
    "seed",
    "winner",
    "p0_score",
    "p1_score",
    "p0_terminal_win",
    "p1_terminal_win",
    "is_nonterminal_draw",
    "is_truncation",
    "loss_reason",
    "decisions",
    "reward_convention",
    "interface",
)


@dataclass(frozen=True)
class PromotionGateConfig:
    """Minimum provenance/reward/replay requirements before rows can promote agents.

    This is not a statistical theorem. It is a practical guardrail: no method
    should be compared or promoted from rows that hide truncation, simulator
    revision, reward convention, or whether the agent used the public interface.
    """

    simulator_revision: str = "rev0012"
    required_interface: str = "public_decision_frame"
    reward_convention: str = "draw_half_reporting_terminal_only_training"
    min_rows: int = 1
    max_truncation_rate: float = 0.25
    require_replay_sample: bool = True
    min_replay_traces: int = 4

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PromotionGateReport:
    passed: bool
    row_count: int
    truncation_rate: float
    replay_count: int
    replay_passed: int
    errors: Tuple[str, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    config: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "row_count": self.row_count,
            "truncation_rate": self.truncation_rate,
            "replay_count": self.replay_count,
            "replay_passed": self.replay_passed,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "config": dict(self.config),
        }


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def audit_promotion_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    replay_results: Sequence[Mapping[str, Any]] = (),
    config: PromotionGateConfig | None = None,
) -> PromotionGateReport:
    config = config or PromotionGateConfig()
    errors: List[str] = []
    warnings: List[str] = []
    row_count = len(rows)
    if row_count < config.min_rows:
        errors.append(f"row_count {row_count} below min_rows {config.min_rows}")

    if rows:
        missing = sorted(set(REQUIRED_PAYOFF_COLUMNS) - set(rows[0].keys()))
        if missing:
            errors.append("missing required payoff columns: " + ", ".join(missing))

    truncations = 0
    for idx, row in enumerate(rows):
        if row.get("simulator_revision") != config.simulator_revision:
            errors.append(f"row {idx}: simulator_revision={row.get('simulator_revision')!r} expected {config.simulator_revision!r}")
        if row.get("interface") != config.required_interface:
            errors.append(f"row {idx}: interface={row.get('interface')!r} expected {config.required_interface!r}")
        if row.get("reward_convention") != config.reward_convention:
            errors.append(f"row {idx}: reward_convention={row.get('reward_convention')!r} expected {config.reward_convention!r}")
        ok, row_errors = audit_payoff_like_row(row)
        if not ok:
            errors.extend(f"row {idx}: {e}" for e in row_errors)
        truncations += 1 if _truthy(row.get("is_truncation")) else 0
        try:
            p0 = float(row.get("p0_score", 0.0))
            p1 = float(row.get("p1_score", 0.0))
            if abs((p0 + p1) - 1.0) > 1e-9:
                errors.append(f"row {idx}: p0_score+p1_score != 1")
        except Exception:
            errors.append(f"row {idx}: p0_score/p1_score not numeric")

    truncation_rate = truncations / row_count if row_count else 0.0
    if truncation_rate > config.max_truncation_rate:
        errors.append(f"truncation_rate {truncation_rate:.3f} exceeds {config.max_truncation_rate:.3f}")
    elif truncation_rate > 0:
        warnings.append(f"truncation_rate {truncation_rate:.3f}; do not use draw-half rows as training reward")

    replay_count = len(replay_results)
    replay_passed = sum(1 for r in replay_results if r.get("passed") is True)
    if config.require_replay_sample:
        if replay_count < config.min_replay_traces:
            errors.append(f"replay_count {replay_count} below min_replay_traces {config.min_replay_traces}")
        if replay_passed != replay_count:
            errors.append(f"only {replay_passed}/{replay_count} replay samples passed")

    return PromotionGateReport(
        passed=not errors,
        row_count=row_count,
        truncation_rate=truncation_rate,
        replay_count=replay_count,
        replay_passed=replay_passed,
        errors=tuple(errors),
        warnings=tuple(warnings),
        config=config.as_dict(),
    )


def read_csv_rows(path: str | Path) -> List[Dict[str, str]]:
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True))


def strategy_standings(rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Symmetric standings from seat-specific payoff rows.

    For a row where strategy appears as player 0 we use p0_score; as player 1 we
    use p1_score. This supports simple smoke comparisons without pretending to
    solve the empirical game.
    """

    buckets: Dict[str, List[float]] = {}
    terminal_wins: Dict[str, int] = {}
    games: Dict[str, int] = {}
    truncs: Dict[str, int] = {}
    for row in rows:
        s0 = str(row["strategy0"])
        s1 = str(row["strategy1"])
        p0 = float(row["p0_score"])
        p1 = float(row["p1_score"])
        buckets.setdefault(s0, []).append(p0)
        buckets.setdefault(s1, []).append(p1)
        games[s0] = games.get(s0, 0) + 1
        games[s1] = games.get(s1, 0) + 1
        terminal_wins[s0] = terminal_wins.get(s0, 0) + (1 if float(row.get("p0_terminal_win", 0.0)) > 0.5 else 0)
        terminal_wins[s1] = terminal_wins.get(s1, 0) + (1 if float(row.get("p1_terminal_win", 0.0)) > 0.5 else 0)
        if _truthy(row.get("is_truncation")):
            truncs[s0] = truncs.get(s0, 0) + 1
            truncs[s1] = truncs.get(s1, 0) + 1
    out = []
    for strategy, scores in buckets.items():
        n = len(scores)
        out.append(
            {
                "strategy": strategy,
                "games": n,
                "mean_score_draw_half": sum(scores) / n if n else 0.0,
                "terminal_win_rate": terminal_wins.get(strategy, 0) / n if n else 0.0,
                "truncation_rate": truncs.get(strategy, 0) / n if n else 0.0,
            }
        )
    out.sort(key=lambda r: (r["mean_score_draw_half"], r["terminal_win_rate"], -r["truncation_rate"]), reverse=True)
    for rank, row in enumerate(out, 1):
        row["rank"] = rank
    return out
