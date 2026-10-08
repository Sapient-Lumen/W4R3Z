from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import (
    Editor,
    TYPING_HISTORY_GROUP_MAX_CHARS,
    TypingHistorySpan,
)
from micromax_editor.undo import Edit, RetainedTextCharge, UndoManager


def _editor(text: str = "", *, col: int = 0) -> tuple[Editor, list[float]]:
    editor = Editor()
    editor.new_buffer("main", text)
    editor.cur().cursors[0] = Cursor(0, col)
    now = [0.0]
    editor._now_fn = lambda: now[0]
    return editor, now


def _type(editor: Editor, now: list[float], text: str, *, step: float = 0.1) -> None:
    for char in text:
        assert editor.dispatch_key(char) is True
        now[0] += float(step)


def _run_repeated(
    editor: Editor,
    now: list[float],
    action: str,
    count: int,
    *,
    step: float = 0.1,
) -> None:
    for _ in range(int(count)):
        assert editor.run_action(action) is True
        now[0] += float(step)


def _row(editor: Editor) -> Edit:
    row = editor.undo.peek_undo()
    assert row is not None
    return row


def _edit(name: str, owner: object, byte_count: int) -> Edit:
    return Edit(
        undo=lambda: None,
        redo=lambda: None,
        description=name,
        retained_text=(
            RetainedTextCharge(
                owner=owner,
                label="owner",
                byte_count=byte_count,
            ),
        ),
    )


def test_printable_dispatch_burst_is_one_exact_guarded_undo_row() -> None:
    editor, now = _editor()

    _type(editor, now, "hé🙂lo")

    eb = editor.cur()
    assert eb.buf.get_text() == "hé🙂lo"
    assert editor.undo.depth() == 1
    assert editor.undo.retained_text_bytes(eb) == len("hé🙂lo".encode("utf-8"))
    row = _row(editor)
    assert row.description == "insert 5"
    assert isinstance(row.history_group, TypingHistorySpan)
    assert row.history_group.new_text == "hé🙂lo"

    assert editor.undo_feedback() is True
    assert eb.buf.get_text() == ""
    assert editor.primary_cursor() == Cursor(0, 0)
    assert editor.redo_feedback() is True
    assert eb.buf.get_text() == "hé🙂lo"
    assert editor.primary_cursor() == Cursor(0, 5)


def test_pause_at_group_delay_starts_a_new_user_visible_undo_step() -> None:
    editor, now = _editor()
    _type(editor, now, "ab")
    # The second character was stamped at 0.1, so 0.6 is the exact 500 ms
    # boundary.  Equality must split rather than depend on scheduler jitter.
    now[0] = 0.6
    _type(editor, now, "cd")

    assert editor.undo.depth() == 2
    assert editor.undo.snapshot().undo[0].description == "insert 2"
    assert editor.undo.snapshot().undo[1].description == "insert 2"
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "ab"
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == ""


def test_intervening_noop_or_cursor_motion_breaks_typing_groups() -> None:
    editor, now = _editor()
    _type(editor, now, "ab")
    assert editor.run_action("Noop") is False
    _type(editor, now, "c")
    assert editor.undo.depth() == 2
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "ab"

    # A real cursor move also starts a fresh row and preserves its exact cursor
    # restoration rather than smearing movement into the earlier typing burst.
    assert editor.run_action("CursorLeft") is True
    _type(editor, now, "X")
    assert editor.cur().buf.get_text() == "aXb"
    assert editor.undo.depth() == 2
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "ab"
    assert editor.primary_cursor() == Cursor(0, 1)


def test_command_execution_is_a_boundary_even_when_it_does_not_edit() -> None:
    editor, now = _editor()
    _type(editor, now, "ab")
    assert editor.exec_command_line("pwd") is True
    _type(editor, now, "c")

    assert editor.undo.depth() == 2
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "ab"


def test_bound_save_key_is_a_boundary_across_the_product_dispatch_path(
    tmp_path: Path,
) -> None:
    path = tmp_path / "typing-boundary.txt"
    path.write_text("", encoding="utf-8")

    editor, now = _editor()
    editor.cur().buf.path = str(path)
    editor._refresh_buffer_disk_signature(editor.cur())
    editor.install_default_keybindings()

    _type(editor, now, "ab")
    assert editor.dispatch_key("Ctrl-s") is True
    assert path.read_text(encoding="utf-8") == "ab"
    _type(editor, now, "c")

    assert editor.undo.depth() == 2
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "ab"


@pytest.mark.parametrize("separator", ["InsertNewline", "InsertTab"])
def test_structural_insertion_is_an_explicit_boundary(separator: str) -> None:
    editor, now = _editor()
    _type(editor, now, "ab")
    assert editor.run_action(separator) is True
    _type(editor, now, "cd")

    assert editor.undo.depth() == 3
    assert isinstance(editor.undo.snapshot().undo[0].history_group, TypingHistorySpan)
    assert editor.undo.snapshot().undo[1].history_group is None
    assert isinstance(editor.undo.snapshot().undo[2].history_group, TypingHistorySpan)


def test_selection_replacement_and_multicursor_edit_do_not_join_typing() -> None:
    editor, now = _editor("hello", col=4)
    eb = editor.cur()
    eb.sel_anchors[0] = Cursor(0, 1)
    editor.input["text"] = "X"
    assert editor.run_action("InsertText") is True
    assert eb.buf.get_text() == "hXo"
    assert _row(editor).history_group is None

    _type(editor, now, "Y")
    assert eb.buf.get_text() == "hXYo"
    assert editor.undo.depth() == 2

    editor2, _ = _editor("abcd", col=1)
    eb2 = editor2.cur()
    eb2.cursors[:] = [Cursor(0, 1), Cursor(0, 3)]
    eb2.sel_anchors[:] = [None, None]
    eb2.cursor_ids[:] = [1, 2]
    eb2.primary = 0
    editor2.input["text"] = "Z"
    assert editor2.run_action("InsertText") is True
    assert eb2.buf.get_text() == "aZbcZd"
    assert editor2.undo.depth() == 1
    assert _row(editor2).history_group is None


def test_repeated_backspace_is_one_exact_bounded_span() -> None:
    editor, now = _editor("abcdef", col=6)
    _run_repeated(editor, now, "Backspace", 3)

    eb = editor.cur()
    assert eb.buf.get_text() == "abc"
    assert editor.undo.depth() == 1
    assert editor.undo.retained_text_bytes(eb) == 3
    row = _row(editor)
    assert row.description == "backspace 3"
    assert isinstance(row.history_group, TypingHistorySpan)
    assert row.history_group.old_text == "def"

    assert editor.undo_feedback() is True
    assert eb.buf.get_text() == "abcdef"
    assert editor.primary_cursor() == Cursor(0, 6)
    assert editor.redo_feedback() is True
    assert eb.buf.get_text() == "abc"
    assert editor.primary_cursor() == Cursor(0, 3)


def test_repeated_forward_delete_extends_original_range_exactly() -> None:
    editor, now = _editor("abcdef", col=2)
    _run_repeated(editor, now, "Delete", 3)

    eb = editor.cur()
    assert eb.buf.get_text() == "abf"
    assert editor.undo.depth() == 1
    row = _row(editor)
    assert row.description == "delete 3"
    assert isinstance(row.history_group, TypingHistorySpan)
    assert row.history_group.start == Cursor(0, 2)
    assert row.history_group.old_end == Cursor(0, 5)
    assert row.history_group.old_text == "cde"

    assert editor.undo_feedback() is True
    assert eb.buf.get_text() == "abcdef"
    assert editor.primary_cursor() == Cursor(0, 2)
    assert editor.redo_feedback() is True
    assert eb.buf.get_text() == "abf"


def test_edit_kind_switch_never_cancels_into_the_same_history_row() -> None:
    editor, now = _editor()
    _type(editor, now, "abc")
    assert editor.run_action("Backspace") is True

    assert editor.cur().buf.get_text() == "ab"
    assert editor.undo.depth() == 2
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "abc"
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == ""


def test_long_key_repeat_is_chunked_by_a_hard_character_ceiling() -> None:
    editor, now = _editor()
    count = TYPING_HISTORY_GROUP_MAX_CHARS + 1
    _type(editor, now, "x" * count, step=0.0)

    rows = editor.undo.snapshot().undo
    assert len(rows) == 2
    assert rows[0].description == f"insert {TYPING_HISTORY_GROUP_MAX_CHARS}"
    assert rows[1].description == "insert 1"
    assert editor.undo.retained_text_bytes(editor.cur()) == count

    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "x" * TYPING_HISTORY_GROUP_MAX_CHARS
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == ""


def test_unrecorded_buffer_version_change_forces_a_boundary() -> None:
    editor, now = _editor()
    _type(editor, now, "a")
    eb = editor.cur()

    # A host mutation at the cursor preserves geometry but advances the buffer
    # version.  It must not be swallowed by a later typed inverse.
    eb.buf.insert(Cursor(0, 1), "X")
    _type(editor, now, "b")
    assert eb.buf.get_text() == "abX"
    assert editor.undo.depth() == 2

    assert editor.undo_feedback() is True
    assert eb.buf.get_text() == "aX"
    assert editor.undo_feedback() is True
    assert eb.buf.get_text() == "X"


def test_merged_inverse_refuses_stale_text_without_losing_history() -> None:
    editor, now = _editor()
    _type(editor, now, "abc")
    eb = editor.cur()
    eb.buf.replace_range(Cursor(0, 1), Cursor(0, 2), "Z")

    assert editor.undo_feedback() is False
    assert eb.buf.get_text() == "aZc"
    assert editor.undo.depth() == 1
    assert editor.undo.redo_depth() == 0
    assert "undo: refused stale edit" in editor.messages[-1]


def test_nested_action_is_not_mistaken_for_adjacent_top_level_typing() -> None:
    editor, now = _editor()

    def nested_insert(current: Editor) -> bool:
        current.input["text"] = "b"
        return current.run_action("InsertText")

    editor.actions.register("Rev0988NestedInsert", nested_insert)
    _type(editor, now, "a")
    assert editor.run_action("Rev0988NestedInsert") is True
    _type(editor, now, "c")

    assert editor.cur().buf.get_text() == "abc"
    assert editor.undo.depth() == 3
    assert isinstance(editor.undo.snapshot().undo[0].history_group, TypingHistorySpan)
    assert editor.undo.snapshot().undo[1].history_group is None
    assert isinstance(editor.undo.snapshot().undo[2].history_group, TypingHistorySpan)


def test_runtime_authority_change_is_a_hard_group_boundary() -> None:
    editor, now = _editor()
    _type(editor, now, "a")
    with editor.script_context("rev0988-script"):
        _type(editor, now, "b")
    _type(editor, now, "c")

    rows = editor.undo.snapshot().undo
    assert len(rows) == 3
    assert rows[0].authority.script_context is False  # type: ignore[union-attr]
    assert rows[1].authority.script_context is True  # type: ignore[union-attr]
    assert rows[1].authority.script_origin_id == "rev0988-script"  # type: ignore[union-attr]
    assert rows[2].authority.script_context is False  # type: ignore[union-attr]


def test_coalesced_row_growth_respects_complete_row_history_budget() -> None:
    editor, now = _editor()
    eb = editor.cur()
    assert editor.set_option_value("undobytes", "4", local=True) == 4

    _type(editor, now, "xy")
    now[0] += 1.0
    _type(editor, now, "abcd")

    assert eb.buf.get_text() == "xyabcd"
    assert editor.undo.depth() == 1
    assert editor.undo.retained_text_bytes(eb) == 4
    assert [message for message in editor.messages if "undo: trimmed" in message] == [
        "undo: trimmed 1 oldest change (2 retained text bytes)"
    ]
    assert editor.undo_feedback() is True
    assert eb.buf.get_text() == "xy"
    assert editor.undo_feedback() is False


def test_new_branch_after_undo_does_not_rejoin_or_retain_redo() -> None:
    editor, now = _editor()
    _type(editor, now, "ab")
    assert editor.undo_feedback() is True
    assert editor.undo.redo_depth() == 1

    _type(editor, now, "X")
    assert editor.cur().buf.get_text() == "X"
    assert editor.undo.depth() == 1
    assert editor.undo.redo_depth() == 0
    assert _row(editor).description == "insert 1"


def test_lost_replacement_lease_falls_back_to_nonoverlapping_current_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor, now = _editor()
    _type(editor, now, "a")

    monkeypatch.setattr(editor.undo, "replace_last", lambda expected, edit: False)
    _type(editor, now, "b")

    rows = editor.undo.snapshot().undo
    assert [row.description for row in rows] == ["insert 1", "insert 1"]
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == "a"
    assert editor.undo_feedback() is True
    assert editor.cur().buf.get_text() == ""


def test_undo_manager_identity_guarded_replacement_updates_caches_and_branch() -> None:
    manager = UndoManager()
    owner = object()
    first = _edit("first", owner, 3)
    abandoned = _edit("abandoned", owner, 7)
    manager.record(first)
    manager.record(abandoned)
    assert manager.undo() is True
    assert manager.depth() == 1
    assert manager.redo_depth() == 1
    assert manager.retained_text_bytes(owner) == 10

    replacement = _edit("replacement", owner, 5)
    assert manager.replace_last(first, replacement) is True
    assert manager.depth() == 1
    assert manager.redo_depth() == 0
    assert manager.retained_text_bytes(owner) == 5
    assert manager.peek_undo() is replacement

    mismatch = _edit("mismatch", owner, 11)
    assert manager.replace_last(first, mismatch) is False
    assert manager.peek_undo() is replacement
    assert manager.retained_text_bytes(owner) == 5

    with manager.suppress_recording():
        assert manager.replace_last(replacement, mismatch) is False
    assert manager.peek_undo() is replacement
    assert manager.retained_text_bytes(owner) == 5


class _IndependentTypingRowsEditor(Editor):
    """Current editor with only rev0988 automatic row joining disabled."""

    def _typing_history_span_for_splice(self, *args: Any, **kwargs: Any) -> None:
        return None


def _editor_state(
    editor: Editor,
) -> tuple[str, tuple[Cursor, ...], tuple[Cursor | None, ...], tuple[int, ...], int]:
    eb = editor.cur()
    return (
        eb.buf.get_text(),
        tuple(eb.cursors),
        tuple(eb.sel_anchors),
        tuple(eb.cursor_ids),
        int(eb.primary),
    )


@pytest.mark.parametrize("seed", range(12))
def test_randomized_grouped_replay_matches_independent_row_oracle(seed: int) -> None:
    """Exercise grouping geometry against the previous one-row-per-edit path."""

    rng = random.Random(seed)
    grouped = Editor()
    reference = _IndependentTypingRowsEditor()
    for editor in (grouped, reference):
        editor.new_buffer("main", "seed")
        editor.cur().cursors[0] = Cursor(0, 2)

    now = [0.0]
    grouped._now_fn = lambda: now[0]
    reference._now_fn = lambda: now[0]
    printable = "abc XYZ🙂"

    for _ in range(180):
        operation = rng.choices(
            ["insert", "backspace", "delete", "left", "right", "noop", "pause"],
            weights=[36, 17, 17, 10, 10, 5, 5],
            k=1,
        )[0]
        if operation == "pause":
            now[0] += rng.choice((0.5, 0.75, 1.0))
            continue

        if operation == "insert":
            char = rng.choice(printable)
            results = []
            for editor in (grouped, reference):
                editor.input["text"] = char
                results.append(editor.run_action("InsertText"))
        else:
            action = {
                "backspace": "Backspace",
                "delete": "Delete",
                "left": "CursorLeft",
                "right": "CursorRight",
                "noop": "Noop",
            }[operation]
            results = [editor.run_action(action) for editor in (grouped, reference)]

        assert results[0] is results[1]
        assert _editor_state(grouped) == _editor_state(reference)
        now[0] += rng.choice((0.0, 0.05, 0.1, 0.2))

    grouped_rows = grouped.undo.snapshot().undo
    row_edit_counts = []
    for row in grouped_rows:
        span = row.history_group
        row_edit_counts.append(
            len(span.old_text) + len(span.new_text)
            if isinstance(span, TypingHistorySpan)
            else 1
        )

    assert reference.undo.depth() == sum(row_edit_counts)
    assert grouped.undo.retained_text_bytes(grouped.cur()) == (
        reference.undo.retained_text_bytes(reference.cur())
    )

    for edit_count in reversed(row_edit_counts):
        assert grouped.undo.undo() is True
        for _ in range(edit_count):
            assert reference.undo.undo() is True
        assert _editor_state(grouped) == _editor_state(reference)

    assert grouped.undo.depth() == 0
    assert reference.undo.depth() == 0

    for edit_count in row_edit_counts:
        assert grouped.undo.redo() is True
        for _ in range(edit_count):
            assert reference.undo.redo() is True
        assert _editor_state(grouped) == _editor_state(reference)
