from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping, Sequence

from .statgate import hoeffding_interval, wilson_interval
from .terminal_mechanisms import to_float, to_int

POPULATION_RAW_SUMMARY_KEYS: tuple[str, ...] = (
    "source_revision",
    "arm_id",
    "starting_life",
    "size_axis",
    "counter_policy_axis",
    "threat_policy_axis",
    "target_deck_size",
    "opponent_deck_size",
    "target",
    "opponent",
)

POPULATION_SOURCE_SUMMARY_KEYS: tuple[str, ...] = tuple(
    key for key in POPULATION_RAW_SUMMARY_KEYS if key != "source_revision"
)

POPULATION_SUMMARY_COMPARE_COLUMNS: tuple[str, ...] = (
    "games",
    "target_mean_score_draw_half",
    "target_score_lcb_95",
    "target_score_ucb_95",
    "target_terminal_win_rate",
    "target_terminal_win_lcb_95",
    "target_terminal_win_ucb_95",
    "target_terminal_wins",
    "target_terminal_losses",
    "target_draws",
    "truncations",
    "truncation_rate",
    "target_library_out_wins",
    "target_life_total_wins",
    "opponent_library_out_losses",
    "target_library_out_losses",
    "library_out_win_share",
    "mean_decisions",
    "median_decisions",
    "mean_turn_number",
    "median_turn_number",
)


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def source_qualified_game_id(row: Mapping[str, Any]) -> str:
    """Return the globally stable game id used by lineage audits.

    The rev0069 and rev0070 population runners each emitted local
    ``cpp_shadow_game_id`` values.  At least one local id is reused across
    source revisions, so archive-wide joins must qualify it with the source
    revision rather than treating it as a global primary key.
    """

    source = str(row.get("source_revision") or row.get("simulator_revision") or "unknown")
    local = str(row.get("cpp_shadow_game_id") or row.get("seed") or "")
    return f"{source}:{local}"


def _digest_values(values: Iterable[Any]) -> str:
    material = [str(value) for value in values]
    payload = json.dumps(sorted(material), separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def population_raw_lineage_index(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    """Build a compact, source-qualified lineage table for raw population games."""

    out: list[dict[str, object]] = []
    for row in rows:
        item = {
            "source_revision": str(row.get("source_revision") or row.get("simulator_revision") or ""),
            "simulator_revision": str(row.get("simulator_revision") or ""),
            "source_qualified_game_id": source_qualified_game_id(row),
            "cpp_shadow_game_id": str(row.get("cpp_shadow_game_id") or ""),
            "seed": to_int(row.get("seed"), -1),
            "transition_seed": to_int(row.get("transition_seed"), -1),
            "agent_seed": to_int(row.get("agent_seed"), -1),
            "arm_id": str(row.get("arm_id") or ""),
            "starting_life": to_int(row.get("starting_life"), 0),
            "starting_player": to_int(row.get("starting_player"), -1),
            "target_seat": to_int(row.get("target_seat"), -1),
            "rep": to_int(row.get("rep"), -1),
            "size_axis": str(row.get("size_axis") or ""),
            "counter_policy_axis": str(row.get("counter_policy_axis") or ""),
            "threat_policy_axis": str(row.get("threat_policy_axis") or ""),
            "focus_target_score": to_float(row.get("focus_target_score"), float("nan")),
            "focus_target_result": str(row.get("focus_target_result") or ""),
            "focus_terminal_mechanism": str(row.get("focus_terminal_mechanism") or ""),
            "terminal_clean_status": str(row.get("terminal_clean_status") or ""),
            "is_truncation": truthy(row.get("is_truncation")),
        }
        out.append(item)
    return sorted(out, key=lambda r: (str(r["source_revision"]), int(r["seed"]), str(r["source_qualified_game_id"])))


def summarize_population_raw_games(
    rows: Iterable[Mapping[str, Any]],
    *,
    keys: Sequence[str] = POPULATION_RAW_SUMMARY_KEYS,
) -> list[dict[str, object]]:
    """Recompute population arm summaries from raw game rows.

    This deliberately mirrors the rev0069/rev0070 arm summary columns so stale
    or edited summary tables can be caught by comparing back to raw games.
    """

    buckets: dict[tuple[object, ...], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        buckets[tuple(row.get(key) for key in keys)].append(row)

    out: list[dict[str, object]] = []
    for key, bucket in sorted(buckets.items(), key=lambda item: tuple(str(x) for x in item[0])):
        n = len(bucket)
        scores = [to_float(row.get("focus_target_score"), 0.0) for row in bucket]
        mean_score = sum(scores) / n if n else 0.0
        score_ci = hoeffding_interval(mean_score, n)
        target_wins = sum(1 for row in bucket if str(row.get("focus_target_result")) == "target_win")
        target_losses = sum(1 for row in bucket if str(row.get("focus_target_result")) == "target_loss")
        target_draws = sum(1 for row in bucket if str(row.get("focus_target_result")) == "draw")
        win_ci = wilson_interval(target_wins, n)
        target_library_wins = sum(1 for row in bucket if truthy(row.get("focus_is_library_out_win")))
        target_life_wins = sum(1 for row in bucket if truthy(row.get("focus_is_life_total_win")))
        target_library_losses = sum(
            1
            for row in bucket
            if str(row.get("focus_terminal_mechanism")) == "library_out"
            and str(row.get("focus_target_result")) == "target_loss"
        )
        truncations = sum(1 for row in bucket if truthy(row.get("is_truncation")))
        decisions = [to_int(row.get("decisions"), 0) for row in bucket]
        turns = [to_int(row.get("turn_number"), 0) for row in bucket]
        item: dict[str, object] = {str(axis): value for axis, value in zip(keys, key)}
        item.update(
            {
                "games": n,
                "target_mean_score_draw_half": mean_score,
                "target_score_lcb_95": score_ci.low,
                "target_score_ucb_95": score_ci.high,
                "target_terminal_win_rate": target_wins / n if n else 0.0,
                "target_terminal_win_lcb_95": win_ci.low,
                "target_terminal_win_ucb_95": win_ci.high,
                "target_terminal_wins": target_wins,
                "target_terminal_losses": target_losses,
                "target_draws": target_draws,
                "truncations": truncations,
                "truncation_rate": truncations / n if n else 0.0,
                "target_library_out_wins": target_library_wins,
                "target_life_total_wins": target_life_wins,
                "opponent_library_out_losses": target_library_wins,
                "target_library_out_losses": target_library_losses,
                "library_out_win_share": target_library_wins / target_wins if target_wins else 0.0,
                "mean_decisions": sum(decisions) / n if n else 0.0,
                "median_decisions": statistics.median(decisions) if decisions else 0.0,
                "mean_turn_number": sum(turns) / n if n else 0.0,
                "median_turn_number": statistics.median(turns) if turns else 0.0,
                "seed_digest": _digest_values(row.get("seed") for row in bucket),
                "source_qualified_game_digest": _digest_values(source_qualified_game_id(row) for row in bucket),
            }
        )
        out.append(item)
    return out


def compare_recomputed_to_source_summaries(
    recomputed_rows: Sequence[Mapping[str, Any]],
    source_summary_rows: Sequence[Mapping[str, Any]],
    *,
    tolerance: float = 1e-12,
) -> list[dict[str, object]]:
    """Compare source arm summaries with recomputed raw summaries."""

    source_by_key = {
        tuple(str(row.get(key, "")) for key in POPULATION_SOURCE_SUMMARY_KEYS): row
        for row in source_summary_rows
    }
    mismatches: list[dict[str, object]] = []
    for row in recomputed_rows:
        key = tuple(str(row.get(key, "")) for key in POPULATION_SOURCE_SUMMARY_KEYS)
        source = source_by_key.get(key)
        if source is None:
            mismatches.append({"kind": "missing_source_summary", "key": "|".join(key)})
            continue
        for column in POPULATION_SUMMARY_COMPARE_COLUMNS:
            left = row.get(column)
            right = source.get(column)
            try:
                left_f = float(left)  # type: ignore[arg-type]
                right_f = float(right)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                if str(left) != str(right):
                    mismatches.append({"kind": "value_mismatch", "key": "|".join(key), "column": column, "recomputed": left, "source": right})
                continue
            if abs(left_f - right_f) > tolerance:
                mismatches.append({"kind": "value_mismatch", "key": "|".join(key), "column": column, "recomputed": left_f, "source": right_f})
    recomputed_keys = {tuple(str(row.get(key, "")) for key in POPULATION_SOURCE_SUMMARY_KEYS) for row in recomputed_rows}
    for key in sorted(set(source_by_key) - recomputed_keys):
        mismatches.append({"kind": "extra_source_summary", "key": "|".join(key)})
    return mismatches


def raw_population_lineage_checks(rows: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    """Audit raw population-game identity, seed, balance, and terminal status."""

    material = [dict(row) for row in rows]
    local_ids = [str(row.get("cpp_shadow_game_id") or "") for row in material]
    qualified_ids = [source_qualified_game_id(row) for row in material]
    seeds = [str(row.get("seed") or "") for row in material]
    transition_seeds = [str(row.get("transition_seed") or "") for row in material]
    agent_seeds = [str(row.get("agent_seed") or "") for row in material]
    local_dupe_count = sum(max(0, count - 1) for count in Counter(local_ids).values())
    qualified_dupe_count = sum(max(0, count - 1) for count in Counter(qualified_ids).values())
    seed_dupe_count = sum(max(0, count - 1) for count in Counter(seeds).values())
    transition_seed_dupe_count = sum(max(0, count - 1) for count in Counter(transition_seeds).values())
    agent_seed_dupe_count = sum(max(0, count - 1) for count in Counter(agent_seeds).values())
    truncations = sum(1 for row in material if truthy(row.get("is_truncation")))
    nonterminal = sum(1 for row in material if str(row.get("terminal_clean_status")) != "terminal")

    balance_groups: dict[tuple[str, str, int], Counter[tuple[int, int]]] = defaultdict(Counter)
    for row in material:
        key = (str(row.get("source_revision") or row.get("simulator_revision") or ""), str(row.get("arm_id") or ""), to_int(row.get("starting_life"), 0))
        balance_groups[key][(to_int(row.get("target_seat"), -1), to_int(row.get("starting_player"), -1))] += 1
    imbalanced = []
    for key, counts in sorted(balance_groups.items(), key=lambda item: tuple(str(x) for x in item[0])):
        observed = sorted(counts.values())
        if not observed or observed[0] != observed[-1] or set(counts) != {(0, 0), (0, 1), (1, 0), (1, 1)}:
            imbalanced.append({"source_revision": key[0], "arm_id": key[1], "starting_life": key[2], "counts": {f"seat{s}_sp{p}": c for (s, p), c in counts.items()}})

    return {
        "raw_games": len(material),
        "source_revisions": sorted({str(row.get("source_revision") or row.get("simulator_revision") or "") for row in material}),
        "local_cpp_shadow_game_id_duplicates": local_dupe_count,
        "source_qualified_game_id_duplicates": qualified_dupe_count,
        "seed_duplicates": seed_dupe_count,
        "transition_seed_duplicates": transition_seed_dupe_count,
        "agent_seed_duplicates": agent_seed_dupe_count,
        "truncations": truncations,
        "nonterminal_clean_status_rows": nonterminal,
        "balance_groups": len(balance_groups),
        "imbalanced_groups": len(imbalanced),
        "imbalanced_examples": imbalanced[:10],
        "passed": qualified_dupe_count == 0 and seed_dupe_count == 0 and transition_seed_dupe_count == 0 and agent_seed_dupe_count == 0 and truncations == 0 and nonterminal == 0 and not imbalanced,
    }


__all__ = [
    "POPULATION_RAW_SUMMARY_KEYS",
    "POPULATION_SOURCE_SUMMARY_KEYS",
    "POPULATION_SUMMARY_COMPARE_COLUMNS",
    "compare_recomputed_to_source_summaries",
    "population_raw_lineage_index",
    "raw_population_lineage_checks",
    "source_qualified_game_id",
    "summarize_population_raw_games",
    "truthy",
]
