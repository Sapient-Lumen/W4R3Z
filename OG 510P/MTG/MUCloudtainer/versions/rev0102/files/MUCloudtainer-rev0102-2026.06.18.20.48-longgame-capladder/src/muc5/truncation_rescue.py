from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, Mapping, Sequence


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


@dataclass(frozen=True)
class TruncationRescueSummary:
    revision: str
    baseline_rows: int
    rescued_rows: int
    baseline_truncations: int
    final_truncations: int
    resolved_truncations: int
    new_truncations: int
    baseline_truncation_rate: float
    final_truncation_rate: float
    rescued_terminal_rate: float
    max_decisions_baseline: int
    max_decisions_final: int

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def row_key(row: Mapping[str, Any]) -> tuple[Any, ...]:
    """Stable key for matching the same scheduled payoff game across runs."""
    return (
        str(row.get("strategy0")),
        str(row.get("strategy1")),
        int(row.get("starting_life")),
        int(row.get("starting_player")),
        int(row.get("seed")),
    )


def annotate_rescued_rows(
    baseline_rows: Sequence[Mapping[str, Any]],
    final_rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    baseline_max_decisions: int,
    final_max_decisions: int,
) -> list[dict[str, Any]]:
    """Merge baseline truncation labels into a higher-ceiling payoff table.

    The higher-ceiling rows are authoritative for scores.  The baseline rows are
    used only to expose whether a game was previously truncated and whether the
    larger ceiling resolved it.  Matching is by strategy pair, life total,
    starting player, and seed.  This keeps truncation handling explicit instead
    of silently changing the reporting table.
    """
    baseline_by_key = {row_key(row): dict(row) for row in baseline_rows}
    out: list[dict[str, Any]] = []
    for final in final_rows:
        row = dict(final)
        base = baseline_by_key.get(row_key(row))
        baseline_trunc = truthy(base.get("is_truncation")) if base else False
        final_trunc = truthy(row.get("is_truncation"))
        row["simulator_revision"] = revision
        row["baseline_simulator_revision"] = "" if base is None else str(base.get("simulator_revision", ""))
        row["baseline_max_decisions"] = int(baseline_max_decisions)
        row["final_max_decisions"] = int(final_max_decisions)
        row["baseline_decisions"] = "" if base is None else int(float(base.get("decisions", 0)))
        row["baseline_loss_reason"] = "" if base is None else str(base.get("loss_reason", ""))
        row["baseline_winner"] = "" if base is None else str(base.get("winner", ""))
        row["baseline_p0_score"] = "" if base is None else base.get("p0_score", "")
        row["baseline_p1_score"] = "" if base is None else base.get("p1_score", "")
        row["baseline_is_truncation"] = bool(baseline_trunc)
        row["final_is_truncation"] = bool(final_trunc)
        row["resolved_from_truncation"] = bool(baseline_trunc and not final_trunc)
        row["new_truncation_after_rescue"] = bool((not baseline_trunc) and final_trunc)
        if base is None:
            status = "no_baseline_match"
        elif baseline_trunc and final_trunc:
            status = "still_truncated"
        elif baseline_trunc and not final_trunc:
            status = "resolved_terminal"
        elif (not baseline_trunc) and final_trunc:
            status = "new_truncation_unexpected"
        else:
            status = "already_terminal"
        row["truncation_rescue_status"] = status
        out.append(row)
    return out


def summarize_rescue(
    annotated_rows: Sequence[Mapping[str, Any]],
    *,
    revision: str,
    baseline_max_decisions: int,
    final_max_decisions: int,
) -> TruncationRescueSummary:
    n = len(annotated_rows)
    baseline_trunc = sum(1 for r in annotated_rows if truthy(r.get("baseline_is_truncation")))
    final_trunc = sum(1 for r in annotated_rows if truthy(r.get("final_is_truncation")) or truthy(r.get("is_truncation")))
    resolved = sum(1 for r in annotated_rows if truthy(r.get("resolved_from_truncation")))
    new = sum(1 for r in annotated_rows if truthy(r.get("new_truncation_after_rescue")))
    return TruncationRescueSummary(
        revision=revision,
        baseline_rows=n,
        rescued_rows=n,
        baseline_truncations=baseline_trunc,
        final_truncations=final_trunc,
        resolved_truncations=resolved,
        new_truncations=new,
        baseline_truncation_rate=baseline_trunc / n if n else 0.0,
        final_truncation_rate=final_trunc / n if n else 0.0,
        rescued_terminal_rate=resolved / baseline_trunc if baseline_trunc else 0.0,
        max_decisions_baseline=int(baseline_max_decisions),
        max_decisions_final=int(final_max_decisions),
    )


def truncation_by_strategy(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, float]] = defaultdict(lambda: {"games": 0, "baseline_truncations": 0, "final_truncations": 0, "resolved_truncations": 0})
    for row in rows:
        for seat, strategy_key in ((0, "strategy0"), (1, "strategy1")):
            sid = str(row[strategy_key])
            b = buckets[sid]
            b["games"] += 1
            b["baseline_truncations"] += 1 if truthy(row.get("baseline_is_truncation")) else 0
            b["final_truncations"] += 1 if (truthy(row.get("final_is_truncation")) or truthy(row.get("is_truncation"))) else 0
            b["resolved_truncations"] += 1 if truthy(row.get("resolved_from_truncation")) else 0
    out = []
    for strategy, vals in buckets.items():
        games = int(vals["games"])
        out.append({
            "strategy": strategy,
            "games": games,
            "baseline_truncations": int(vals["baseline_truncations"]),
            "final_truncations": int(vals["final_truncations"]),
            "resolved_truncations": int(vals["resolved_truncations"]),
            "baseline_truncation_rate": vals["baseline_truncations"] / games if games else 0.0,
            "final_truncation_rate": vals["final_truncations"] / games if games else 0.0,
        })
    out.sort(key=lambda r: (r["final_truncation_rate"], r["baseline_truncation_rate"], r["strategy"]), reverse=True)
    return out


def truncation_by_pair(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: {"games": 0, "baseline_truncations": 0, "final_truncations": 0, "resolved_truncations": 0})
    for row in rows:
        key = (str(row.get("strategy0")), str(row.get("strategy1")))
        b = buckets[key]
        b["games"] += 1
        b["baseline_truncations"] += 1 if truthy(row.get("baseline_is_truncation")) else 0
        b["final_truncations"] += 1 if (truthy(row.get("final_is_truncation")) or truthy(row.get("is_truncation"))) else 0
        b["resolved_truncations"] += 1 if truthy(row.get("resolved_from_truncation")) else 0
    out = []
    for (s0, s1), vals in buckets.items():
        games = int(vals["games"])
        out.append({
            "strategy0": s0,
            "strategy1": s1,
            "games": games,
            "baseline_truncations": int(vals["baseline_truncations"]),
            "final_truncations": int(vals["final_truncations"]),
            "resolved_truncations": int(vals["resolved_truncations"]),
            "baseline_truncation_rate": vals["baseline_truncations"] / games if games else 0.0,
            "final_truncation_rate": vals["final_truncations"] / games if games else 0.0,
        })
    out.sort(key=lambda r: (r["final_truncation_rate"], r["baseline_truncation_rate"], r["strategy0"], r["strategy1"]), reverse=True)
    return out
