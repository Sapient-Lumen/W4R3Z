from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Mapping

from .evidence_index import sha256_file

IDENTIFIER_FIELDS = {
    "game_index",
    "decision_id",
    "step",
    "player",
    "agent_name",
    "starting_player",
    "starting_life",
    "action_index",
    "action_count",
    "chosen",
    "action",
    "trace_id",
    "case_id",
    "skipped_reason",
}


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _float_or_none(value: object) -> float | None:
    try:
        text = str(value).strip()
        if text == "":
            return None
        return float(text)
    except (TypeError, ValueError):
        return None


def _top(counter: Counter[str], *, limit: int = 20) -> dict[str, int]:
    return dict(counter.most_common(limit))


def summarize_ranker_training_dataset(path: str | Path) -> dict[str, Any]:
    """Create a compact profile for the bulky rev0021 ranker training table."""

    source = Path(path)
    action_rows = 0
    chosen_rows = 0
    decision_ids: set[str] = set()
    game_ids: set[str] = set()
    agents: Counter[str] = Counter()
    life_totals: Counter[str] = Counter()
    chosen_actions: Counter[str] = Counter()
    offered_actions: Counter[str] = Counter()
    action_count_values: list[float] = []
    chosen_numeric_sums: defaultdict[str, float] = defaultdict(float)
    chosen_numeric_counts: defaultdict[str, int] = defaultdict(int)
    feature_columns: list[str] = []

    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        feature_columns = [name for name in fieldnames if name not in IDENTIFIER_FIELDS]
        for row in reader:
            action_rows += 1
            decision_ids.add(str(row.get("decision_id", "")))
            game_ids.add(str(row.get("game_index", "")))
            agents[str(row.get("agent_name", ""))] += 1
            life_totals[str(row.get("starting_life", ""))] += 1
            action = str(row.get("action", ""))
            offered_actions[action] += 1
            count = _float_or_none(row.get("action_count"))
            if count is not None:
                action_count_values.append(count)
            if _truthy(row.get("chosen")):
                chosen_rows += 1
                chosen_actions[action] += 1
                for name in feature_columns:
                    value = _float_or_none(row.get(name))
                    if value is None:
                        continue
                    chosen_numeric_sums[name] += value
                    chosen_numeric_counts[name] += 1

    chosen_feature_means = {
        name: chosen_numeric_sums[name] / chosen_numeric_counts[name]
        for name in sorted(chosen_numeric_sums)
        if chosen_numeric_counts[name]
    }
    nonzero_chosen_feature_means = {
        name: value for name, value in chosen_feature_means.items() if abs(value) > 1e-12
    }
    return {
        "source_path": source.as_posix(),
        "source_bytes": source.stat().st_size,
        "source_sha256": sha256_file(source),
        "derivative_kind": "ranker_training_dataset_profile",
        "rows": action_rows,
        "unique_decision_ids": len(decision_ids),
        "unique_game_indices": len(game_ids),
        "chosen_rows": chosen_rows,
        "offered_rows_per_chosen_row": (action_rows / chosen_rows) if chosen_rows else None,
        "mean_action_count": mean(action_count_values) if action_count_values else None,
        "max_action_count": max(action_count_values) if action_count_values else None,
        "agents_by_row": _top(agents),
        "starting_life_by_row": _top(life_totals),
        "top_offered_actions": _top(offered_actions),
        "top_chosen_actions": _top(chosen_actions),
        "feature_column_count": len(feature_columns),
        "chosen_feature_means_nonzero": nonzero_chosen_feature_means,
        "profile_note": "Compact derivative: enough to audit shape, action coverage, chosen-action distribution, and chosen-row feature means without retaining the full training rows in the linked core.",
    }


def summarize_cpp_batch_trace_rows(path: str | Path) -> dict[str, Any]:
    """Create a compact profile for the rev0021 C++ batch trace-row table."""

    source = Path(path)
    rows = 0
    trace_ids: set[str] = set()
    supported = 0
    cpp_matches = 0
    python_pre_ok = 0
    python_post_ok = 0
    action_kinds: Counter[str] = Counter()
    skipped_reasons: Counter[str] = Counter()
    rows_by_trace: Counter[str] = Counter()

    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows += 1
            trace = str(row.get("trace_id", ""))
            trace_ids.add(trace)
            rows_by_trace[trace] += 1
            action_kinds[str(row.get("action_kind", ""))] += 1
            if _truthy(row.get("supported_by_cpp")):
                supported += 1
            else:
                skipped_reasons[str(row.get("skipped_reason", ""))] += 1
            if _truthy(row.get("cpp_match")):
                cpp_matches += 1
            if _truthy(row.get("python_pre_fingerprint_ok")):
                python_pre_ok += 1
            if _truthy(row.get("python_post_fingerprint_ok")):
                python_post_ok += 1

    return {
        "source_path": source.as_posix(),
        "source_bytes": source.stat().st_size,
        "source_sha256": sha256_file(source),
        "derivative_kind": "cpp_batch_trace_rows_profile",
        "rows": rows,
        "trace_count": len(trace_ids),
        "supported_by_cpp_rows": supported,
        "unsupported_rows": rows - supported,
        "cpp_match_rows": cpp_matches,
        "cpp_mismatch_rows": max(0, supported - cpp_matches),
        "python_pre_fingerprint_failures": max(0, rows - python_pre_ok),
        "python_post_fingerprint_failures": max(0, rows - python_post_ok),
        "action_kind_counts": _top(action_kinds),
        "skipped_reason_counts": _top(skipped_reasons),
        "rows_by_trace_top": _top(rows_by_trace),
        "profile_note": "Compact derivative: enough to audit support, C++ match status, fingerprint status, trace coverage, and action-kind mix without retaining the full trace-row table in the linked core.",
    }


def write_json(path: str | Path, obj: Mapping[str, Any]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_rev0071_derivatives(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    data = root_path / "data"
    ranker_source = data / ("rev0021_" + "ranker_training_dataset.csv")
    trace_source = data / ("rev0021_" + "cpp_batch_trace_rows.csv")
    ranker_out = data / "rev0021_ranker_summary.json"
    trace_out = data / "rev0021_cpp_batch_summary.json"
    ranker_summary = summarize_ranker_training_dataset(ranker_source)
    trace_summary = summarize_cpp_batch_trace_rows(trace_source)
    write_json(ranker_out, ranker_summary)
    write_json(trace_out, trace_summary)
    return {
        "revision": "rev0071",
        "created_derivatives": [
            ranker_out.relative_to(root_path).as_posix(),
            trace_out.relative_to(root_path).as_posix(),
        ],
        "source_bytes_profiled": int(ranker_source.stat().st_size + trace_source.stat().st_size),
        "ranker_rows": int(ranker_summary["rows"]),
        "ranker_unique_decisions": int(ranker_summary["unique_decision_ids"]),
        "trace_rows": int(trace_summary["rows"]),
        "trace_cpp_mismatch_rows": int(trace_summary["cpp_mismatch_rows"]),
    }


__all__ = [
    "summarize_cpp_batch_trace_rows",
    "summarize_ranker_training_dataset",
    "write_rev0071_derivatives",
]
