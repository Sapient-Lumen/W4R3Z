from __future__ import annotations

import random

import pytest

from micromax_editor.buffer import BufferEditConflict, Cursor
from micromax_editor.editor import Editor
from micromax_editor.simultaneous_edits import (
    SimultaneousTextEdit,
    line_start_offsets,
    offset_to_cursor,
    plan_simultaneous_edits,
    replay_simultaneous_edit_witness,
    replay_simultaneous_edit_witness_lines,
)


def _install_cursors(editor: Editor, cursors: list[Cursor]) -> None:
    eb = editor.cur()
    eb.cursors[:] = [Cursor(int(cur.line), int(cur.col)) for cur in cursors]
    eb.sel_anchors[:] = [None for _cur in cursors]
    eb.cursor_ids[:] = list(range(1, len(cursors) + 1))
    eb.primary = 0
    editor._normalize_cursor_lists(eb)


def test_line_vector_replay_matches_flat_oracle_for_seeded_unicode_plans() -> None:
    rng = random.Random(990)
    source_alphabet = "ab Ω\n"
    replacement_alphabet = "XY λ\n"

    for _case in range(2_000):
        source = "".join(
            rng.choice(source_alphabet) for _ in range(rng.randrange(0, 120))
        )
        starts = line_start_offsets(source)
        flat: list[tuple[int, int, str]] = []
        source_at = 0
        while source_at <= len(source) and len(flat) < 15:
            source_at += rng.randrange(0, 8)
            if source_at > len(source):
                break
            end = min(len(source), source_at + rng.randrange(0, 8))
            replacement = "".join(
                rng.choice(replacement_alphabet)
                for _ in range(rng.randrange(0, 8))
            )
            flat.append((source_at, end, replacement))
            source_at = max(source_at + 1, end)

        requests = [
            SimultaneousTextEdit(
                offset_to_cursor(source, starts, start),
                offset_to_cursor(source, starts, end),
                replacement,
                owner=index,
            )
            for index, (start, end, replacement) in enumerate(flat)
        ]
        plan = plan_simultaneous_edits(source, requests, source_starts=starts)
        witness = plan.compact_history_witness()

        forward_lines = replay_simultaneous_edit_witness_lines(
            source.split("\n"),
            witness,
            undo=False,
        )
        forward = "\n".join(forward_lines)
        assert forward == replay_simultaneous_edit_witness(
            source,
            witness,
            undo=False,
        )
        assert forward == plan.new_text

        restored_lines = replay_simultaneous_edit_witness_lines(
            plan.new_text.split("\n"),
            witness,
            undo=True,
        )
        restored = "\n".join(restored_lines)
        assert restored == replay_simultaneous_edit_witness(
            plan.new_text,
            witness,
            undo=True,
        )
        assert restored == source


def test_line_vector_replay_reuses_complete_untouched_line_objects() -> None:
    source_lines = [
        "".join(("untouched", "-head")),
        "".join(("target", "-one")),
        "".join(("target", "-two")),
        "".join(("untouched", "-tail")),
    ]
    source = "\n".join(source_lines)
    plan = plan_simultaneous_edits(
        source,
        [
            SimultaneousTextEdit(Cursor(1, 2), Cursor(1, 5), "X", owner=0),
            SimultaneousTextEdit(Cursor(2, 1), Cursor(2, 4), "Y\nZ", owner=1),
        ],
    )

    result = replay_simultaneous_edit_witness_lines(
        source_lines,
        plan.compact_history_witness(),
        undo=False,
    )

    assert "\n".join(result) == plan.new_text
    assert result[0] is source_lines[0]
    assert result[-1] is source_lines[-1]


def test_line_vector_replay_validates_all_targets_before_returning_result() -> None:
    source = "alpha\nbeta\ngamma\ndelta"
    plan = plan_simultaneous_edits(
        source,
        [
            SimultaneousTextEdit(Cursor(0, 1), Cursor(0, 3), "XX", owner=0),
            SimultaneousTextEdit(Cursor(2, 1), Cursor(2, 4), "YY", owner=1),
        ],
    )
    witness = plan.compact_history_witness()
    changed_lines = plan.new_text.split("\n")
    changed_lines[2] = "gQYa"
    before = list(changed_lines)

    with pytest.raises(BufferEditConflict, match="splice 2"):
        replay_simultaneous_edit_witness_lines(changed_lines, witness, undo=True)

    assert changed_lines == before


def test_editor_sparse_undo_redo_never_materializes_complete_text(monkeypatch) -> None:
    source_lines = [f"line-{index:05d}-" + ("a" * 80) for index in range(4_000)]
    source = "\n".join(source_lines)
    editor = Editor()
    editor.new_buffer("line-vector-replay", source)
    _install_cursors(editor, [Cursor(101, 7), Cursor(3_701, 13)])
    eb = editor.cur()
    eb.buf.set_fastdirty(True)

    editor.input["text"] = "X\nY"
    assert editor.run_action("InsertText") is True
    edited = eb.buf.get_text()
    assert editor.undo.depth() == 1

    def forbidden_full_text(*_args, **_kwargs):
        raise AssertionError("sparse history replay materialized complete text")

    commit_versions: list[int] = []
    original_replace_lines = eb.buf.replace_lines

    def counted_replace_lines(lines):
        original_replace_lines(lines)
        commit_versions.append(int(eb.buf.version))

    monkeypatch.setattr(eb.buf, "get_text", forbidden_full_text)
    monkeypatch.setattr(eb.buf, "set_text", forbidden_full_text)
    monkeypatch.setattr(eb.buf, "replace_lines", counted_replace_lines)

    version_after_edit = int(eb.buf.version)
    assert editor.undo_feedback() is True
    assert "\n".join(eb.buf.lines) == source
    assert int(eb.buf.version) == version_after_edit + 1

    assert editor.redo_feedback() is True
    assert "\n".join(eb.buf.lines) == edited
    assert int(eb.buf.version) == version_after_edit + 2
    assert commit_versions == [version_after_edit + 1, version_after_edit + 2]
