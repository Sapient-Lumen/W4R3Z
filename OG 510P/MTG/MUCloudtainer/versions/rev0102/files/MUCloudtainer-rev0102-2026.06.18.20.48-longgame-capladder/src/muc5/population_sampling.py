from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping, Sequence

from .terminal_mechanisms import to_int

COMPLETE_POPULATION_PANEL = "complete_population_panel"
TARGETED_STRATUM_CHALLENGE = "targeted_stratum_challenge"
UNKNOWN_SAMPLING_FRAME = "unknown_sampling_frame"

COMPLETE_PANEL_REVISIONS = frozenset({"rev0069", "rev0070", "rev0080"})
TARGETED_CHALLENGE_REVISIONS = frozenset({"rev0075"})

SAMPLING_FRAME_COLUMNS: tuple[str, ...] = (
    "source_revision",
    "sampling_frame",
    "global_pool_eligible",
    "selection_risk",
    "rows",
    "game_rows",
    "summary_game_rows",
    "size_axes",
    "starting_lives",
)


def source_revision(row: Mapping[str, Any]) -> str:
    return str(row.get("source_revision") or row.get("simulator_revision") or "").strip()


def _nonempty(value: Any) -> bool:
    return value not in {None, ""}


def sampling_frame_for_row(row: Mapping[str, Any]) -> str:
    """Classify a population row by the design that produced it.

    rev0069 and rev0070 are rectangular seed-disjoint population panels.  rev0075
    is intentionally different: it was selected after looking at prior
    high-point/underpowered strata, so it is valid for challenging those strata
    but must not be silently folded into a broad population pool.
    """

    revision = source_revision(row)
    if revision in TARGETED_CHALLENGE_REVISIONS or any(
        _nonempty(row.get(key))
        for key in ("stress_cell", "stress_seed_disjoint", "stress_selected_from", "stress_selection_rule")
    ):
        return TARGETED_STRATUM_CHALLENGE
    if revision in COMPLETE_PANEL_REVISIONS:
        return COMPLETE_POPULATION_PANEL
    return UNKNOWN_SAMPLING_FRAME


def sampling_frame_reason(frame: str) -> str:
    if frame == COMPLETE_POPULATION_PANEL:
        return "eligible for broad population pooling; rectangular source panel with preregistered arms"
    if frame == TARGETED_STRATUM_CHALLENGE:
        return "not eligible for broad population pooling; adaptive follow-up selected after inspecting prior strata"
    return "not eligible for broad population pooling; sampling design is not known to be rectangular/preregistered"


def global_pool_eligible(row: Mapping[str, Any]) -> bool:
    return sampling_frame_for_row(row) == COMPLETE_POPULATION_PANEL


def annotate_sampling_frame_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        item = dict(row)
        frame = sampling_frame_for_row(item)
        item["sampling_frame"] = frame
        item["global_pool_eligible"] = frame == COMPLETE_POPULATION_PANEL
        item["selection_risk"] = sampling_frame_reason(frame)
        out.append(item)
    return out


def global_pool_source_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    return [row for row in annotate_sampling_frame_rows(rows) if row["global_pool_eligible"] is True]


def _row_game_weight(row: Mapping[str, Any]) -> int:
    games = to_int(row.get("games"), -1)
    return games if games >= 0 else 1


def sampling_frame_summary_rows(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, object]]:
    annotated = annotate_sampling_frame_rows(rows)
    buckets: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for row in annotated:
        buckets[(source_revision(row), str(row.get("sampling_frame")))] .append(row)

    out: list[dict[str, object]] = []
    for (revision, frame), bucket in sorted(buckets.items()):
        item = {
            "source_revision": revision,
            "sampling_frame": frame,
            "global_pool_eligible": frame == COMPLETE_POPULATION_PANEL,
            "selection_risk": sampling_frame_reason(frame),
            "rows": len(bucket),
            "game_rows": len(bucket),
            "summary_game_rows": sum(_row_game_weight(row) for row in bucket),
            "size_axes": ";".join(sorted({str(row.get("size_axis")) for row in bucket if _nonempty(row.get("size_axis"))})),
            "starting_lives": ";".join(str(x) for x in sorted({to_int(row.get("starting_life"), -1) for row in bucket if to_int(row.get("starting_life"), -1) >= 0})),
        }
        out.append(item)
    return out


def adaptive_pooling_guard(rows: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    annotated = annotate_sampling_frame_rows(rows)
    counts = Counter(str(row.get("sampling_frame")) for row in annotated)
    ineligible = [row for row in annotated if row.get("global_pool_eligible") is not True]
    targeted = [row for row in annotated if row.get("sampling_frame") == TARGETED_STRATUM_CHALLENGE]
    unknown = [row for row in annotated if row.get("sampling_frame") == UNKNOWN_SAMPLING_FRAME]
    eligible = [row for row in annotated if row.get("global_pool_eligible") is True]
    return {
        "rows": len(annotated),
        "summary_game_rows": sum(_row_game_weight(row) for row in annotated),
        "sampling_frame_counts": dict(sorted(counts.items())),
        "eligible_rows": len(eligible),
        "eligible_summary_game_rows": sum(_row_game_weight(row) for row in eligible),
        "ineligible_rows": len(ineligible),
        "ineligible_summary_game_rows": sum(_row_game_weight(row) for row in ineligible),
        "targeted_challenge_rows": len(targeted),
        "targeted_challenge_summary_game_rows": sum(_row_game_weight(row) for row in targeted),
        "unknown_sampling_rows": len(unknown),
        "global_pool_guard_passed": len(unknown) == 0 and all(row.get("global_pool_eligible") is False for row in targeted),
        "guard_read": "adaptive follow-up evidence is retained for targeted strata but excluded from broad pooled promotion gates",
    }


__all__ = [
    "COMPLETE_POPULATION_PANEL",
    "TARGETED_STRATUM_CHALLENGE",
    "UNKNOWN_SAMPLING_FRAME",
    "SAMPLING_FRAME_COLUMNS",
    "adaptive_pooling_guard",
    "annotate_sampling_frame_rows",
    "global_pool_eligible",
    "global_pool_source_rows",
    "sampling_frame_for_row",
    "sampling_frame_reason",
    "sampling_frame_summary_rows",
    "source_revision",
]
