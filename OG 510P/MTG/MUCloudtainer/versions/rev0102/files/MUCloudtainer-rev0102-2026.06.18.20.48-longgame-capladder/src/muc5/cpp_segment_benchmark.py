from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Dict, Sequence

from .cpp_segment import (
    CppNoChoiceSegmentSpec,
    cpp_segment_signatures,
    cpp_segment_tool_status,
    play_public_game_collect_nochoice_segments,
)
from .cpp_transition import cpp_transition_signatures, cpp_transition_tool_status


@dataclass(frozen=True)
class CppSegmentBenchmarkSummary:
    revision: str
    games: int
    segments: int
    forced_actions: int
    segment_cpp_seconds: float
    one_action_cpp_seconds: float
    segment_records_per_second: float
    one_action_records_per_second: float
    segment_invocations: int
    one_action_invocations: int
    segment_mismatches: int
    skipped_events: int
    estimated_decision_compression_ratio: float
    notes: tuple[str, ...]
    segment_tool_status: Dict[str, object]
    transition_tool_status: Dict[str, object]

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def benchmark_cpp_segment_vs_one_action(
    specs: Sequence[CppNoChoiceSegmentSpec],
    *,
    revision: str = "rev0037",
) -> tuple[list[dict[str, object]], list[dict[str, object]], CppSegmentBenchmarkSummary]:
    """Compare C++ no-choice segment batch with one-action C++ micro batch.

    Python remains the semantic authority.  This benchmark is about the C++
    subprocess/kernel shape, not a cutover to C++ tournament execution.
    """

    game_rows: list[dict[str, object]] = []
    segment_rows_raw = []
    prepared = []
    agent_cache: dict[str, object] = {}
    mulligan_cache: dict[str, object] = {}
    for spec in specs:
        game_row, rows, records = play_public_game_collect_nochoice_segments(
            spec,
            agent_cache=agent_cache,
            mulligan_cache=mulligan_cache,
            finalize_cpp=False,
        )
        game_rows.append(game_row.as_dict())
        segment_rows_raw.extend(rows)
        prepared.extend(records)

    t0 = time.perf_counter()
    segment_sigs = cpp_segment_signatures(prepared) if prepared else {}
    segment_seconds = time.perf_counter() - t0

    micro_records = [p.record for p in prepared]
    t1 = time.perf_counter()
    micro_sigs = cpp_transition_signatures(micro_records) if micro_records else []
    micro_seconds = time.perf_counter() - t1

    finalized_segments: list[dict[str, object]] = []
    mismatches = 0
    skipped_events = 0
    for row in segment_rows_raw:
        got = segment_sigs.get(row.segment_id)
        match = None if row.skipped_events else (got == row.expected_end_signature)
        if match is False:
            mismatches += 1
        skipped_events += int(row.skipped_events)
        out = row.as_dict()
        out["cpp_end_signature"] = got
        out["cpp_match"] = match
        finalized_segments.append(out)

    forced_actions = sum(int(r.get("length", 0)) for r in finalized_segments)
    decisions = sum(int(g.get("decisions", 0)) for g in game_rows)
    choice_frames = sum(int(g.get("choice_frames", 0)) for g in game_rows)
    estimated_steps = choice_frames + len(finalized_segments)
    summary = CppSegmentBenchmarkSummary(
        revision=revision,
        games=len(game_rows),
        segments=len(finalized_segments),
        forced_actions=int(forced_actions),
        segment_cpp_seconds=float(segment_seconds),
        one_action_cpp_seconds=float(micro_seconds),
        segment_records_per_second=float(len(finalized_segments) / max(segment_seconds, 1e-9)),
        one_action_records_per_second=float(len(micro_sigs) / max(micro_seconds, 1e-9)),
        segment_invocations=1 if prepared else 0,
        one_action_invocations=1 if micro_records else 0,
        segment_mismatches=int(mismatches),
        skipped_events=int(skipped_events),
        estimated_decision_compression_ratio=float(decisions / max(1, estimated_steps)),
        notes=(
            "Both paths are single coarse subprocess calls; this measures kernel/transport shape, not per-action subprocess overhead.",
            "Segment C++ outputs one end signature per forced run; one-action C++ outputs one signature per forced action.",
            "Python remains semantic authority and supplies pre/post signatures.",
        ),
        segment_tool_status=cpp_segment_tool_status().as_dict(),
        transition_tool_status=cpp_transition_tool_status().as_dict(),
    )
    return game_rows, finalized_segments, summary
