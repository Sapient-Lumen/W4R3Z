from __future__ import annotations

import pytest

from micromax.vm import MicromaxError
from micromax_editor.buffer import Buffer
from micromax_editor.editor import (
    Editor,
    MacroReplayBufferSnapshot,
    MacroReplaySnapshot,
    MacroStep,
)
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _snapshot_for_name(
    snapshot: MacroReplaySnapshot,
    name: str,
) -> MacroReplayBufferSnapshot:
    return next(row for row in snapshot.buffers if row.name == name)


def _forbid_join(buffer: Buffer, monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden() -> str:
        raise AssertionError("aggregate line-vector path joined the complete document")

    monkeypatch.setattr(buffer, "get_text", forbidden)


def _capture_transaction_rows(
    editor: Editor,
    monkeypatch: pytest.MonkeyPatch,
) -> list[tuple[MacroReplaySnapshot, MacroReplaySnapshot, str]]:
    captured: list[tuple[MacroReplaySnapshot, MacroReplaySnapshot, str]] = []
    original = editor._record_buffer_transaction_snapshot

    def recording(
        before: MacroReplaySnapshot,
        after: MacroReplaySnapshot,
        description: str,
    ) -> None:
        captured.append((before, after, str(description)))
        original(before, after, description)

    monkeypatch.setattr(editor, "_record_buffer_transaction_snapshot", recording)
    return captured


def test_with_undo_retains_shared_line_vectors_without_complete_text_joins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    install_editor_hostcalls(editor)
    source = "\n".join(
        f"row-{index:05d}-" + (chr(97 + index % 26) * 96)
        for index in range(4096)
    )
    editor.new_buffer("main", source)
    buffer = editor.cur().buf
    buffer.fastdirty = True
    buffer.dirty = False
    original_lines = buffer.snapshot_lines()
    expected_after = ("X" + original_lines[0], *original_lines[1:])
    captured = _capture_transaction_rows(editor, monkeypatch)
    _forbid_join(buffer, monkeypatch)

    editor.vm.eval(
        '"line-vector" [ "X" "ed.insert" hostcall ] "ed.with-undo" hostcall',
        filename="<rev0992-test>",
    )

    assert editor.vm.stack == [1]
    assert buffer.snapshot_lines() == expected_after
    assert len(captured) == 1
    before, after, description = captured[0]
    assert description == "line-vector"
    before_buffer = _snapshot_for_name(before, "main")
    after_buffer = _snapshot_for_name(after, "main")
    assert before_buffer.text == after_buffer.text == ""
    assert before_buffer.text_captured is after_buffer.text_captured is False
    assert before_buffer.line_vector is not None
    assert after_buffer.line_vector is not None
    assert before_buffer.line_vector == original_lines
    assert after_buffer.line_vector == expected_after
    assert before_buffer.line_vector[0] is original_lines[0]
    assert after_buffer.line_vector[0] is not original_lines[0]
    assert all(
        before_buffer.line_vector[index]
        is after_buffer.line_vector[index]
        is original_lines[index]
        for index in range(1, len(original_lines))
    )

    row = editor.undo.peek_undo()
    assert row is not None
    assert len(row.retained_text) == 1
    expected_charge = (
        sum(len(line) for line in original_lines)
        + len(expected_after[0])
        + (2 * (len(original_lines) - 1))
    )
    assert row.retained_text[0].byte_count == expected_charge
    assert expected_charge < (len(source) + len("X" + source))

    assert editor.undo.undo() is True
    assert buffer.snapshot_lines() == original_lines
    assert buffer.last_change is None
    assert editor.undo.redo() is True
    assert buffer.snapshot_lines() == expected_after
    assert buffer.last_change is None


def test_line_vector_restore_notifies_an_enclosing_first_write_observer() -> None:
    buffer = Buffer("before")
    observed: list[tuple[str, ...]] = []

    with buffer.observe_before_text_mutation(
        lambda current: observed.append(current.snapshot_lines()),
        once=True,
    ):
        buffer._restore_lines_snapshot(("after",))

    assert observed == [("before",)]
    assert buffer.snapshot_lines() == ("after",)


def test_macro_undoing_an_aggregate_row_captures_the_true_outer_entry_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    install_editor_hostcalls(editor)
    editor.new_buffer("main", "seed")
    buffer = editor.cur().buf
    buffer.fastdirty = True
    buffer.dirty = False

    editor.vm.eval(
        '"seed aggregate" [ "X" "ed.insert" hostcall ] "ed.with-undo" hostcall',
        filename="<rev0992-test>",
    )
    assert buffer.snapshot_lines() == ("Xseed",)
    assert editor.undo.depth() == 1

    editor.set_macro(
        "replace-aggregate",
        [
            MacroStep(kind="action", name="Undo", payload={"input": {}}),
            MacroStep(
                kind="action",
                name="InsertText",
                payload={"input": {"text": "Y"}},
            ),
        ],
    )
    captured = _capture_transaction_rows(editor, monkeypatch)
    _forbid_join(buffer, monkeypatch)

    assert editor.play_macro("replace-aggregate") is True
    assert buffer.snapshot_lines() == ("Yseed",)
    assert editor.undo.depth() == 2
    assert len(captured) == 1
    before, after, description = captured[0]
    assert description == "macro replace-aggregate x1"
    assert _snapshot_for_name(before, "main").line_vector == ("Xseed",)
    assert _snapshot_for_name(after, "main").line_vector == ("Yseed",)

    assert editor.undo.undo() is True
    assert buffer.snapshot_lines() == ("Xseed",)
    assert editor.undo.undo() is True
    assert buffer.snapshot_lines() == ("seed",)
    assert editor.undo.redo() is True
    assert buffer.snapshot_lines() == ("Xseed",)
    assert editor.undo.redo() is True
    assert buffer.snapshot_lines() == ("Yseed",)


def test_failed_with_undo_rolls_back_line_vectors_without_joining(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    install_editor_hostcalls(editor)
    source_lines = tuple(f"line-{index:04d}" for index in range(2048))
    editor.new_buffer("main", "\n".join(source_lines))
    buffer = editor.cur().buf
    buffer.fastdirty = True
    buffer.dirty = False
    initial_version = buffer.version
    initial_saved_sig = buffer._saved_sig
    _forbid_join(buffer, monkeypatch)

    with pytest.raises(MicromaxError, match="Unknown word: nope"):
        editor.vm.eval(
            '"rollback" [ "X" "ed.insert" hostcall nope ] "ed.with-undo" hostcall',
            filename="<rev0992-test>",
        )

    assert buffer.snapshot_lines() == source_lines
    assert buffer.version == initial_version
    assert buffer.dirty is False
    assert buffer._saved_sig == initial_saved_sig
    assert buffer.last_change is None
    assert editor.undo.depth() == 0
    assert editor.undo.redo_depth() == 0


def test_unicode_line_vector_accounting_uses_logical_utf8_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    install_editor_hostcalls(editor)
    editor.options.set("undobytes", "0")
    editor.new_buffer("main", "é\n🐍\ntail")
    buffer = editor.cur().buf
    buffer.fastdirty = True
    buffer.dirty = False
    before_lines = buffer.snapshot_lines()
    _forbid_join(buffer, monkeypatch)

    editor.vm.eval(
        '"unicode" [ "Z" "ed.insert" hostcall ] "ed.with-undo" hostcall',
        filename="<rev0992-test>",
    )

    after_lines = buffer.snapshot_lines()
    row = editor.undo.peek_undo()
    assert row is not None
    expected = (
        sum(len(line.encode("utf-8")) for line in before_lines)
        + len(after_lines[0].encode("utf-8"))
        + (2 * (len(before_lines) - 1))
    )
    assert row.retained_text[0].byte_count == expected


def test_rewound_multiwrite_macro_cannot_masquerade_as_one_splice_for_undobytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = Editor()
    install_editor_hostcalls(editor)
    editor.options.set("undobytes", "0")
    editor.new_buffer("main", "base0\nbase1\nbase2")
    buffer = editor.cur().buf
    buffer.fastdirty = True
    buffer.dirty = False

    editor.vm.eval(
        '"seed aggregate" [ "X" "ed.insert" hostcall ] "ed.with-undo" hostcall',
        filename="<rev0992-test>",
    )
    before_lines = buffer.snapshot_lines()
    before_version = int(buffer.version)

    editor.set_macro(
        "rewind-multiwrite",
        [
            MacroStep(kind="action", name="Undo", payload={"input": {}}),
            MacroStep(
                kind="action",
                name="InsertText",
                payload={"input": {"text": "A"}},
            ),
            MacroStep(kind="action", name="CursorDown", payload={"input": {}}),
            MacroStep(kind="action", name="CursorDown", payload={"input": {}}),
            MacroStep(
                kind="action",
                name="InsertText",
                payload={"input": {"text": "B"}},
            ),
        ],
    )
    captured = _capture_transaction_rows(editor, monkeypatch)
    _forbid_join(buffer, monkeypatch)

    assert editor.play_macro("rewind-multiwrite") is True
    after_lines = buffer.snapshot_lines()
    # Undo rewinds one version and two edits advance twice. Version arithmetic
    # alone therefore looks exactly like one monotonic splice even though the
    # final document changed in two separated regions.
    assert buffer.version == before_version + 1
    assert buffer.last_change is not None
    assert buffer.last_change.start_line == 2

    assert len(captured) == 1
    before, after, _description = captured[0]
    before_buffer = _snapshot_for_name(before, "main")
    after_buffer = _snapshot_for_name(after, "main")
    assert before_buffer.line_vector == before_lines
    assert after_buffer.line_vector == after_lines
    assert after_buffer.line_vector_mutation_count == 2

    row = editor.undo.peek_undo()
    assert row is not None
    expected_conservative = (
        sum(len(line) for line in before_lines)
        + max(0, len(before_lines) - 1)
        + sum(len(line) for line in after_lines)
        + max(0, len(after_lines) - 1)
    )
    assert row.retained_text[0].byte_count == expected_conservative
    assert expected_conservative > (
        sum(len(line) for line in before_lines)
        + max(0, len(before_lines) - 1)
        + max(0, len(after_lines) - 1)
        + len(after_lines[buffer.last_change.start_line])
    )
