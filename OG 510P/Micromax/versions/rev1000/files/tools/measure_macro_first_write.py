#!/usr/bin/env python3
"""Measure macro replay's first-write owner against the eager reference.

Both paths execute the same current Micromax runtime and the same recorded macro
steps:

* ``eager_snapshot_reference`` reproduces the pre-rev0987 macro transaction,
  which joined every open buffer before playback.
* ``first_write_product`` calls the shipped rev0992 ``Editor.play_macro`` path,
  which shallow-copies a pre-existing buffer's line vector on first mutation.

The success cases preserve the same aggregate transaction semantics while the
product retains shared line vectors instead of complete document strings. Failure
restores exact editor/history state and records no row.  The navigation case is a
separate product witness because navigation-only macros intentionally do not
consume undo history and now require no complete document joins.

Measurements use CPython ``tracemalloc``.  They are not RSS, allocator-arena,
native-memory, latency, durability, or cross-platform bounds.

Examples:
  PYTHONPATH=src python tools/measure_macro_first_write.py
  PYTHONPATH=src python tools/measure_macro_first_write.py \
      --chars 250000 --buffers 4 --samples 1 --output /tmp/witness.json
"""

from __future__ import annotations

import argparse
import gc
import json
import platform
import statistics
import sys
import time
import tracemalloc
from contextlib import ExitStack
from pathlib import Path
from typing import Any, Callable

from micromax_editor.buffer import Buffer
from micromax_editor.editor import Editor, MacroStep

SCHEMA = "micromax.macro-first-write-witness.v2"


def _action(name: str, *, text: str | None = None) -> MacroStep:
    payload: dict[str, object] = {"input": {}}
    if text is not None:
        payload = {"input": {"text": str(text)}}
    return MacroStep(kind="action", name=str(name), payload=payload)


def _source_text(chars: int, marker: str) -> str:
    target = max(1, int(chars))
    row = (str(marker) * 79) + "\n"
    repeats = max(1, target // len(row))
    text = row * repeats
    remainder = target - len(text)
    if remainder > 0:
        text += str(marker) * remainder
    return text


def _build_editor(
    *,
    chars: int,
    buffer_count: int,
    case: str,
) -> tuple[Editor, dict[str, str]]:
    editor = Editor()
    editor.options.set("undobytes", "0")
    sources: dict[str, str] = {}
    for index in range(max(1, int(buffer_count))):
        name = f"buffer-{index + 1}"
        marker = chr(ord("a") + (index % 26))
        source = _source_text(chars, marker)
        sources[name] = source
        editor.new_buffer(name, source)
        editor.buffers[name].buf.fastdirty = True
        editor.buffers[name].buf.dirty = False
    if not editor.switch_buffer("buffer-1"):
        raise RuntimeError("could not select macro witness buffer")

    if case == "success":
        steps = [_action("InsertText", text="X")]
    elif case == "failure":
        steps = [
            _action("InsertText", text="X"),
            _action("rev0987-missing-action"),
        ]
    elif case == "navigation":
        steps = [
            _action("CursorRight"),
            _action("CursorRight"),
            _action("CursorLeft"),
        ]
    else:
        raise ValueError(f"unknown macro witness case: {case}")
    editor.set_macro("witness", steps)
    return editor, sources


def _instrument_text_joins(editor: Editor) -> tuple[dict[str, int], Callable[[], None]]:
    counts = {"calls": 0, "chars": 0}
    instrumented: list[Buffer] = []
    for eb in editor.buffers.values():
        buffer = eb.buf
        original = buffer.get_text

        def counted(*, _original: Callable[[], str] = original) -> str:
            text = _original()
            counts["calls"] += 1
            counts["chars"] += len(text)
            return text

        buffer.get_text = counted  # type: ignore[method-assign]
        instrumented.append(buffer)

    def restore() -> None:
        for buffer in instrumented:
            buffer.__dict__.pop("get_text", None)

    return counts, restore


def _texts_match(editor: Editor, expected: dict[str, str]) -> bool:
    return set(editor.buffers) == set(expected) and all(
        editor.buffers[name].buf.get_text() == text
        for name, text in expected.items()
    )


def _play_macro_eager_reference(editor: Editor, *, name: str, count: int = 1) -> bool:
    """Execute the historical eager macro transaction in the current runtime."""

    steps = list(editor.macros[name])
    snapshot = editor._macro_replay_snapshot()
    suppress_step_undo = editor._macro_replay_can_suppress_step_undo(steps)
    editor._macro_playing = True
    editor._macro_play_name = str(name)
    editor._macro_play_steps = len(steps)
    replay_step_index = 0
    try:
        with ExitStack() as stack:
            if suppress_step_undo:
                stack.enter_context(editor.undo.suppress_recording())
            for _ in range(max(1, int(count))):
                for step in steps:
                    replay_step_index += 1
                    ok = False
                    detail = ""
                    try:
                        ok = bool(editor._execute_macro_replay_step(step))
                    except Exception as exc:
                        detail = editor._macro_replay_step_error_detail(step, exc)
                    if not ok:
                        if not detail:
                            detail = editor._macro_replay_step_failure_detail(step)
                        editor._restore_macro_replay_snapshot(snapshot)
                        editor.message(
                            f"macro: aborted at step {replay_step_index}: {detail}"
                        )
                        return False

        try:
            after = editor._macro_replay_snapshot(
                reuse_unchanged_text_from=snapshot,
            )
            editor.undo.restore(snapshot.undo)
            if editor._macro_replay_has_undoable_change(snapshot, after):
                editor._record_buffer_transaction_snapshot(
                    snapshot,
                    after,
                    f"macro {name} x{count}",
                )
        except Exception as exc:
            editor._restore_macro_replay_snapshot(snapshot)
            editor.message(f"macro: aborted during transaction finalization: {exc}")
            return False
    finally:
        editor._macro_playing = False
        editor._macro_play_name = ""
        editor._macro_play_steps = 0
        editor.input = dict(snapshot.input)
    step_word = "step" if len(steps) == 1 else "steps"
    editor.message(f"macro: played {name} x{count} ({len(steps)} {step_word})")
    return True


def _measure_once(
    *,
    chars: int,
    buffer_count: int,
    case: str,
    product: bool,
) -> dict[str, Any]:
    editor, sources = _build_editor(
        chars=chars,
        buffer_count=buffer_count,
        case=case,
    )
    before_expected = dict(sources)
    after_expected = dict(sources)
    if case == "success":
        after_expected["buffer-1"] = "X" + after_expected["buffer-1"]

    joins, restore_joins = _instrument_text_joins(editor)
    gc.collect()
    tracemalloc.start()
    tracemalloc.reset_peak()
    baseline_current, _ = tracemalloc.get_traced_memory()
    started = time.perf_counter()
    if product:
        ok = bool(editor.play_macro("witness"))
    else:
        ok = bool(_play_macro_eager_reference(editor, name="witness"))
    elapsed = time.perf_counter() - started

    joined_calls = int(joins["calls"])
    joined_chars = int(joins["chars"])
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    restore_joins()

    if case == "success":
        expected_ok = True
        forward_exact = _texts_match(editor, after_expected)
        row = editor.undo.peek_undo()
        if row is None:
            raise RuntimeError("successful macro witness produced no undo row")
        retained_bytes = sum(int(charge.byte_count) for charge in row.retained_text)
        retained_rows = len(row.retained_text)
        if not editor.undo.undo():
            raise RuntimeError("successful macro witness undo failed")
        undo_exact = _texts_match(editor, before_expected)
        if not editor.undo.redo():
            raise RuntimeError("successful macro witness redo failed")
        redo_exact = _texts_match(editor, after_expected)
    elif case == "failure":
        expected_ok = False
        forward_exact = _texts_match(editor, before_expected)
        retained_bytes = editor.undo.retained_text_bytes()
        retained_rows = 0
        undo_exact = editor.undo.depth() == 0
        redo_exact = editor.undo.redo_depth() == 0
    else:
        expected_ok = True
        forward_exact = _texts_match(editor, before_expected)
        retained_bytes = editor.undo.retained_text_bytes()
        retained_rows = 0
        undo_exact = editor.undo.depth() == 0
        redo_exact = editor.undo.redo_depth() == 0
        if editor.primary_cursor().col != 1:
            raise RuntimeError("navigation macro witness lost cursor state")

    return {
        "document_chars_per_buffer": len(next(iter(sources.values()))),
        "open_buffers": len(sources),
        "elapsed_seconds": round(float(elapsed), 6),
        "traced_current_bytes": max(0, int(current - baseline_current)),
        "traced_peak_bytes": max(0, int(peak - baseline_current)),
        "joined_text_calls": joined_calls,
        "joined_text_chars": joined_chars,
        "capture_representation": ("line-vector" if product else "joined-text"),
        "retained_text_charge_rows": int(retained_rows),
        "accounted_retained_text_bytes": int(retained_bytes),
        "return_value_exact": bool(ok is expected_ok),
        "forward_or_rollback_exact": bool(forward_exact),
        "undo_exact": bool(undo_exact),
        "redo_exact": bool(redo_exact),
    }


def _median_case(
    *,
    chars: int,
    buffer_count: int,
    samples: int,
    case: str,
    product: bool,
) -> dict[str, Any]:
    rows = [
        _measure_once(
            chars=chars,
            buffer_count=buffer_count,
            case=case,
            product=product,
        )
        for _ in range(max(1, int(samples)))
    ]
    first = rows[0]
    stable_fields = (
        "document_chars_per_buffer",
        "open_buffers",
        "joined_text_calls",
        "joined_text_chars",
        "capture_representation",
        "retained_text_charge_rows",
        "accounted_retained_text_bytes",
    )
    for field in stable_fields:
        if any(row[field] != first[field] for row in rows[1:]):
            raise RuntimeError(f"macro witness field was not stable: {field}")
    return {
        **{field: first[field] for field in stable_fields},
        "samples": len(rows),
        "elapsed_seconds_median": round(
            float(statistics.median(float(row["elapsed_seconds"]) for row in rows)),
            6,
        ),
        "traced_current_bytes_median": int(
            statistics.median(int(row["traced_current_bytes"]) for row in rows)
        ),
        "traced_peak_bytes_median": int(
            statistics.median(int(row["traced_peak_bytes"]) for row in rows)
        ),
        "return_value_exact": all(bool(row["return_value_exact"]) for row in rows),
        "forward_or_rollback_exact": all(
            bool(row["forward_or_rollback_exact"]) for row in rows
        ),
        "undo_exact": all(bool(row["undo_exact"]) for row in rows),
        "redo_exact": all(bool(row["redo_exact"]) for row in rows),
    }


def _reduction_percent(reference: int | float, product: int | float) -> float:
    ref = float(reference)
    if ref <= 0:
        return 0.0
    return round((1.0 - (float(product) / ref)) * 100.0, 3)


def _case_report(args: argparse.Namespace, case: str) -> dict[str, Any]:
    common = {
        "chars": int(args.chars),
        "buffer_count": int(args.buffers),
        "samples": int(args.samples),
        "case": str(case),
    }
    reference = _median_case(**common, product=False)
    product = _median_case(**common, product=True)
    return {
        "eager_snapshot_reference": reference,
        "first_write_product": product,
        "reductions_percent": {
            "joined_text_calls": _reduction_percent(
                reference["joined_text_calls"],
                product["joined_text_calls"],
            ),
            "joined_text_chars": _reduction_percent(
                reference["joined_text_chars"],
                product["joined_text_chars"],
            ),
            "accounted_retained_text_bytes": _reduction_percent(
                reference["accounted_retained_text_bytes"],
                product["accounted_retained_text_bytes"],
            ),
            "traced_peak_bytes_median": _reduction_percent(
                reference["traced_peak_bytes_median"],
                product["traced_peak_bytes_median"],
            ),
            "elapsed_seconds_median": _reduction_percent(
                reference["elapsed_seconds_median"],
                product["elapsed_seconds_median"],
            ),
        },
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "measurement_scope": (
            "same-runtime pre-rev0987 eager macro reference versus rev0992 "
            "line-vector macro replay; Python tracemalloc only, with fastdirty "
            "enabled to isolate transaction capture"
        ),
        "success": _case_report(args, "success"),
        "failure": _case_report(args, "failure"),
        "navigation_only": _case_report(args, "navigation"),
        "notes": [
            "Both paths preserve exact macro, rollback, Undo, and Redo semantics; rev0992 replaces complete transaction strings with shallow immutable line vectors.",
            "The eager reference is executable historical control flow in the current runtime, not a shipped product mode.",
            "Joined characters count complete strings returned by Buffer.get_text during macro playback only.",
            "Logical retained-byte accounting excludes pointer-vector and Python-object overhead and conservatively charges the after vector's changed middle.",
            "Failure includes exact in-memory rollback but does not model process crash or durable recovery.",
            "Navigation-only replay is deliberately not an undo event and short-circuits before content materialization.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chars", type=int, default=1_000_000)
    parser.add_argument("--buffers", type=int, default=8)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build_report(args)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
