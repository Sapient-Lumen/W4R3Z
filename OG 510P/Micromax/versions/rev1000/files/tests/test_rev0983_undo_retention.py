from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from micromax_editor.buffer import Buffer, BufferEditConflict, Cursor
from micromax_editor.undo import Edit, UndoManager

ROOT = Path(__file__).resolve().parents[1]


def test_buffer_splice_witness_roundtrips_multiline_text_exactly() -> None:
    buffer = Buffer("alpha\nbeta\ngamma")

    forward = buffer.replace_range_with_witness(
        Cursor(0, 2),
        Cursor(1, 2),
        "X\nY",
    )

    assert forward.start == Cursor(0, 2)
    assert forward.old_end == Cursor(1, 2)
    assert forward.new_end == Cursor(1, 1)
    assert forward.old_text == "pha\nbe"
    assert forward.new_text == "X\nY"
    assert forward.changed is True
    assert buffer.get_text() == "alX\nYta\ngamma"

    inverse = buffer.replace_range_with_witness(
        forward.start,
        forward.new_end,
        forward.old_text,
        expected_old_text=forward.new_text,
    )
    assert inverse.new_end == forward.old_end
    assert buffer.get_text() == "alpha\nbeta\ngamma"

    buffer.replace_range_with_witness(
        forward.start,
        forward.old_end,
        forward.new_text,
        expected_old_text=forward.old_text,
    )
    assert buffer.get_text() == "alX\nYta\ngamma"


def test_buffer_splice_witness_refuses_a_stale_exact_target() -> None:
    buffer = Buffer("abcdef")
    witness = buffer.replace_range_with_witness(Cursor(0, 1), Cursor(0, 3), "XY")
    buffer.replace_range(Cursor(0, 1), Cursor(0, 3), "ZZ")

    with pytest.raises(BufferEditConflict, match="buffer splice conflict"):
        buffer.replace_range_with_witness(
            witness.start,
            witness.new_end,
            witness.old_text,
            expected_old_text=witness.new_text,
        )

    assert buffer.get_text() == "aZZdef"


def test_undo_manager_keeps_stack_membership_when_callbacks_raise() -> None:
    undo = UndoManager()

    def fail_undo() -> None:
        raise RuntimeError("undo failed")

    undo.record(Edit(undo=fail_undo, redo=lambda: None, description="failure"))
    with pytest.raises(RuntimeError, match="undo failed"):
        undo.undo()
    assert undo.depth() == 1
    assert undo.redo_depth() == 0

    undo = UndoManager()

    def fail_redo() -> None:
        raise RuntimeError("redo failed")

    undo.record(Edit(undo=lambda: None, redo=fail_redo, description="failure"))
    assert undo.undo() is True
    assert undo.depth() == 0
    assert undo.redo_depth() == 1
    with pytest.raises(RuntimeError, match="redo failed"):
        undo.redo()
    assert undo.depth() == 0
    assert undo.redo_depth() == 1


def test_undo_retention_witness_compares_compact_and_snapshot_shapes() -> None:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(ROOT / "src") + (os.pathsep + existing if existing else "")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "measure_undo_retention.py"),
            "--chars",
            "1100000",
            "--edits",
            "5",
            "--samples",
            "1",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )

    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["schema"] == "micromax.undo-retention-witness.v1"
    compact = payload["compact_splice"]
    snapshot = payload["snapshot_reference"]
    comparison = payload["comparison"]

    assert compact["many_edits"]["roundtrip_exact"] is True
    assert snapshot["many_edits"]["roundtrip_exact"] is True
    assert compact["many_edits"]["max_history_closure_string_chars"] <= 1
    assert snapshot["many_edits"]["max_history_closure_string_chars"] >= 1_100_000
    assert (
        snapshot["additional_history"]["traced_current_growth_bytes"]
        > compact["additional_history"]["traced_current_growth_bytes"]
    )
    assert comparison["many_edit_current_reduction_percent"] > 50
    assert comparison["additional_history_reduction_percent"] > 90
