from __future__ import annotations

import pytest

from micromax_editor.buffer import Cursor
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.screen_consumer import validate_screen_contract_v1


def _selection_starts(ed: Editor) -> list[tuple[int, int]]:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    out: list[tuple[int, int]] = []
    for i in range(len(eb.cursors)):
        rng = ed.selection_range(i)
        assert rng is not None
        out.append((int(rng[0].line), int(rng[0].col)))
    return out


def _cursor_columns(ed: Editor) -> list[int]:
    eb = ed.cur()
    ed._normalize_cursor_lists(eb)
    return [int(cursor.col) for cursor in eb.cursors]


def test_repeated_select_skip_edit_journey_is_visible_atomic_and_undoable() -> None:
    ed = Editor()
    ed.new_buffer("journey.mx", "foo foo foo foo", path="journey.mx")

    # One invocation keeps Micromax's established convenience: select the word
    # under the primary cursor and add the next occurrence.
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert _selection_starts(ed) == [(0, 0), (0, 4)]

    # Repeating the action must advance from the newest selected occurrence,
    # not attempt to add the second occurrence forever.
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert _selection_starts(ed) == [(0, 0), (0, 4), (0, 8)]

    # Skip moves only the newest occurrence, preserving the earlier choices.
    assert ed.run_action("SkipMultiCursor") is True
    assert _selection_starts(ed) == [(0, 0), (0, 4), (0, 12)]

    contract = ed.screen_contract(8, 40)
    assert validate_screen_contract_v1(contract) == contract
    selection_cues = [cue for cue in contract["cues"] if str(cue["kind"]).startswith("selection-")]
    assert selection_cues == [
        {"kind": "selection-primary", "y": 0, "x": 0, "end": 3},
        {"kind": "selection-secondary", "y": 0, "x": 4, "end": 7},
        {"kind": "selection-secondary", "y": 0, "x": 12, "end": 15},
    ]

    ed.input["text"] = "bar"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "bar bar foo bar"
    assert _cursor_columns(ed) == [3, 7, 15]
    assert ed.has_selection() is False

    assert ed.run_action("Undo") is True
    assert ed.cur().buf.get_text() == "foo foo foo foo"
    assert _selection_starts(ed) == [(0, 0), (0, 4), (0, 12)]

    assert ed.run_action("Redo") is True
    assert ed.cur().buf.get_text() == "bar bar foo bar"
    assert _cursor_columns(ed) == [3, 7, 15]


def test_spawn_multicursor_select_exhaustion_is_not_phantom_success() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "foo foo foo")

    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert ed.run_action("SpawnMultiCursorSelect") is True
    before = ed._snapshot_buffer_state(ed.cur())

    assert ed.run_action("SpawnMultiCursorSelect") is False
    assert ed._snapshot_buffer_state(ed.cur()) == before


def test_multicursor_occurrence_continuation_is_derived_from_active_buffer() -> None:
    ed = Editor()
    ed.new_buffer("a", "foo foo foo foo")
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert ed.run_action("SpawnMultiCursorSelect") is True

    ed.new_buffer("b", "bar bar bar")
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert _selection_starts(ed) == [(0, 0), (0, 4), (0, 8)]
    assert not hasattr(ed, "_mc_last_match_start")


def test_unique_occurrence_selection_reports_the_real_state_change_once() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "solo")

    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert ed.selection_range() == (Cursor(0, 0), Cursor(0, 4))
    before = ed._snapshot_buffer_state(ed.cur())

    assert ed.run_action("SpawnMultiCursorSelect") is False
    assert ed._snapshot_buffer_state(ed.cur()) == before


def test_occurrence_progress_respects_ignorecase_without_hidden_state() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "Foo foo FOO")
    assert ed.exec_command_line("set ignorecase true") is True

    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert _selection_starts(ed) == [(0, 0), (0, 4)]
    assert ed.run_action("SpawnMultiCursorSelect") is True
    assert _selection_starts(ed) == [(0, 0), (0, 4), (0, 8)]

    before = ed._snapshot_buffer_state(ed.cur())
    assert ed.run_action("SpawnMultiCursorSelect") is False
    assert ed._snapshot_buffer_state(ed.cur()) == before


@pytest.mark.parametrize(
    ("action", "replacement", "expected"),
    [
        ("InsertText", "X", "X X"),
        ("InsertNewline", None, "\n \n"),
        ("InsertTab", None, "\t \t"),
    ],
)
def test_selected_occurrences_are_replaced_exactly_once(
    action: str,
    replacement: str | None,
    expected: str,
) -> None:
    ed = Editor()
    ed.new_buffer("*t*", "foo foo")
    ed.exec_command_line("set autoindent false")
    ed.exec_command_line("set tabstospaces false")
    assert ed.run_action("SpawnMultiCursorSelect") is True

    if replacement is not None:
        ed.input["text"] = replacement
    assert ed.run_action(action) is True
    assert ed.cur().buf.get_text() == expected
    assert ed.has_selection() is False


def test_simultaneous_insert_rebases_every_cursor_to_its_own_result() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "ab cd")
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 0), Cursor(0, 3)]
    eb.sel_anchors[:] = [None, None]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "Xab Xcd"
    assert _cursor_columns(ed) == [1, 5]


def test_paste_and_hostcall_use_the_same_simultaneous_replacement_geometry() -> None:
    ed = Editor()
    ed.new_buffer("paste", "foo foo")
    assert ed.run_action("SpawnMultiCursorSelect") is True
    ed.set_clipboard_items(["A", "BBBB"], kind="items")

    assert ed.run_action("Paste") is True
    assert ed.cur().buf.get_text() == "A BBBB"
    assert _cursor_columns(ed) == [1, 6]

    ed2 = Editor()
    ed2.new_buffer("hostcall", "foo foo")
    install_editor_hostcalls(ed2)
    assert ed2.run_action("SpawnMultiCursorSelect") is True
    ed2.vm.stack.append(["A", "BBBB"])
    ed2.vm.stack.append("ed.replace-selections")
    ed2.vm.eval("hostcall")
    col = ed2.vm.pop_int()
    line = ed2.vm.pop_int()

    assert (line, col) == (0, 1)
    assert ed2.cur().buf.get_text() == "A BBBB"
    assert _cursor_columns(ed2) == [1, 6]


@pytest.mark.parametrize(
    ("action", "cursors"),
    [
        ("Backspace", [Cursor(0, 1), Cursor(0, 4)]),
        ("Delete", [Cursor(0, 0), Cursor(0, 3)]),
    ],
)
def test_multicursor_character_delete_rebases_later_cursor(
    action: str,
    cursors: list[Cursor],
) -> None:
    ed = Editor()
    ed.new_buffer("*t*", "ab cd")
    eb = ed.cur()
    eb.cursors[:] = list(cursors)
    eb.sel_anchors[:] = [None, None]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0

    assert ed.run_action(action) is True
    assert ed.cur().buf.get_text() == "b d"
    assert _cursor_columns(ed) == [0, 2]


def test_single_cursor_owned_edit_uses_direct_one_touch_splice(monkeypatch) -> None:
    """Ordinary typing must not flatten/rebuild the whole document."""

    import micromax_editor.editor as editor_module

    ed = Editor()
    ed.new_buffer("*t*", "abc\ndef")
    eb = ed.cur()
    eb.sel_anchors[0] = Cursor(0, 1)
    eb.cursors[0] = Cursor(1, 2)
    before_version = int(eb.buf.version)
    range_reads = 0
    original_range_text = eb.buf.get_range_text

    def counted_range_text(start, end):
        nonlocal range_reads
        range_reads += 1
        return original_range_text(start, end)

    def unexpected_planner(*_args, **_kwargs):
        raise AssertionError("single-cursor edit entered the simultaneous planner")

    monkeypatch.setattr(eb.buf, "get_range_text", counted_range_text)
    monkeypatch.setattr(
        editor_module,
        "plan_simultaneous_edits_lines",
        unexpected_planner,
    )
    ed.input["text"] = "X\nY"
    assert ed.run_action("InsertText") is True

    assert eb.buf.get_text() == "aX\nYf"
    assert eb.buf.version == before_version + 1
    assert range_reads == 1
    assert eb.cursors == [Cursor(1, 1)]
    assert eb.sel_anchors == [None]

    assert ed.run_action("Undo") is True
    assert eb.buf.get_text() == "abc\ndef"
    assert eb.cursors == [Cursor(1, 2)]
    assert eb.sel_anchors == [Cursor(0, 1)]


def test_identical_single_cursor_replacement_clears_selection_without_false_text_mutation() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")
    eb = ed.cur()
    eb.sel_anchors[0] = Cursor(0, 0)
    eb.cursors[0] = Cursor(0, 3)
    before_version = int(eb.buf.version)

    ed.input["text"] = "abc"
    assert ed.run_action("InsertText") is True
    assert eb.buf.get_text() == "abc"
    assert eb.buf.version == before_version
    assert eb.cursors == [Cursor(0, 3)]
    assert eb.sel_anchors == [None]

    # Cursor/selection state is still a real, reversible editor change even
    # though the document bytes and mutation witness stayed unchanged.
    assert ed.run_action("Undo") is True
    assert eb.buf.get_text() == "abc"
    assert eb.cursors == [Cursor(0, 3)]
    assert eb.sel_anchors == [Cursor(0, 0)]


def test_exact_duplicate_multicursor_ranges_coalesce_to_one_text_edit() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "foo bar")
    eb = ed.cur()
    # Opposite selection directions keep two distinct cursor positions while
    # still describing the exact same immutable source range.
    eb.cursors[:] = [Cursor(0, 3), Cursor(0, 0)]
    eb.sel_anchors[:] = [Cursor(0, 0), Cursor(0, 3)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert eb.buf.get_text() == "X bar"
    # Both owners land at the same replacement end, then the editor's standing
    # duplicate-cursor invariant intentionally collapses them.
    assert eb.cursors == [Cursor(0, 1)]
    assert eb.sel_anchors == [None]

    assert ed.run_action("Undo") is True
    assert eb.buf.get_text() == "foo bar"
    assert len(eb.cursors) == 2
    assert _selection_starts(ed) == [(0, 0), (0, 0)]


def test_overlapping_multicursor_ranges_fail_closed_before_any_mutation() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abcdef")
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 3), Cursor(0, 5)]
    eb.sel_anchors[:] = [Cursor(0, 0), Cursor(0, 2)]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0
    before = ed._snapshot_buffer_state(eb)
    before_version = int(eb.buf.version)
    before_undo_depth = ed.undo.depth()

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is False
    assert ed._snapshot_buffer_state(eb) == before
    assert eb.buf.version == before_version
    assert ed.undo.depth() == before_undo_depth


def test_multicursor_planner_reuses_source_index_and_scans_each_document_once(
    monkeypatch,
) -> None:
    """Index source and result vectors once without flat-document scans."""

    import micromax_editor.editor as editor_module
    import micromax_editor.simultaneous_edits as simultaneous_module

    editor_calls = 0
    planner_calls = 0
    original_editor_index = editor_module.simultaneous_line_start_offsets_for_lines
    original_planner_index = simultaneous_module.compact_line_start_offsets_for_lines

    def editor_index(lines):
        nonlocal editor_calls
        editor_calls += 1
        return original_editor_index(lines)

    def planner_index(lines):
        nonlocal planner_calls
        planner_calls += 1
        return original_planner_index(lines)

    monkeypatch.setattr(
        editor_module,
        "simultaneous_line_start_offsets_for_lines",
        editor_index,
    )
    monkeypatch.setattr(
        simultaneous_module,
        "compact_line_start_offsets_for_lines",
        planner_index,
    )

    ed = Editor()
    ed.new_buffer("*t*", "ab\ncd")
    eb = ed.cur()
    eb.cursors[:] = [Cursor(0, 1), Cursor(1, 1)]
    eb.sel_anchors[:] = [None, None]
    eb.cursor_ids[:] = [1, 2]
    eb.primary = 0

    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert eb.buf.get_text() == "aXb\ncXd"
    assert editor_calls == 1  # authoritative source vector
    assert planner_calls == 2  # one source index + one retained result index


def _container_strings(value):
    """Yield strings retained through plain closure containers only."""

    if isinstance(value, str):
        yield value
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _container_strings(key)
            yield from _container_strings(item)
        return
    if isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from _container_strings(item)


def test_single_cursor_history_retains_compact_splices_not_document_snapshots(
    monkeypatch,
) -> None:
    document = "a" * 1_100_000
    ed = Editor()
    ed.new_buffer("*large*", document)
    eb = ed.cur()
    assert eb.buf.fastdirty is True
    eb.cursors[0] = Cursor(0, len(document) // 2)

    def unexpected_full_snapshot(_eb):
        raise AssertionError("ordinary one-cursor edit copied the whole document")

    monkeypatch.setattr(ed, "_snapshot_buffer_state", unexpected_full_snapshot)
    # This is a retained-row shape test, not a typing-group test. Advance the
    # injected clock beyond rev0988's 500 ms continuity window so each compact
    # splice remains an independent row for callback-retention inspection.
    now = 0.0

    def next_history_time() -> float:
        nonlocal now
        now += 1.0
        return now

    ed._now_fn = next_history_time
    for _ in range(10):
        ed.input["text"] = "x"
        assert ed.run_action("InsertText") is True

    assert ed.undo.depth() == 10
    for edit in ed.undo.snapshot().undo:
        for callback in (edit.undo, edit.redo):
            retained = [
                text
                for cell in (callback.__closure__ or ())
                for text in _container_strings(cell.cell_contents)
            ]
            assert max((len(text) for text in retained), default=0) <= 1

    for _ in range(10):
        assert ed.undo_feedback() is True
    assert eb.buf.get_text() == document
    for _ in range(10):
        assert ed.redo_feedback() is True
    assert eb.buf.get_text() == document[: len(document) // 2] + "x" * 10 + document[len(document) // 2 :]


def test_identical_single_cursor_replacement_undo_is_sidecar_only() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")
    eb = ed.cur()
    eb.sel_anchors[0] = Cursor(0, 0)
    eb.cursors[0] = Cursor(0, 3)
    version_before = int(eb.buf.version)

    ed.input["text"] = "abc"
    assert ed.run_action("InsertText") is True
    assert eb.buf.version == version_before
    assert eb.sel_anchors == [None]

    assert ed.undo_feedback() is True
    assert eb.buf.version == version_before
    assert eb.cursors == [Cursor(0, 3)]
    assert eb.sel_anchors == [Cursor(0, 0)]

    assert ed.redo_feedback() is True
    assert eb.buf.version == version_before
    assert eb.cursors == [Cursor(0, 3)]
    assert eb.sel_anchors == [None]


def test_compact_undo_refuses_stale_target_and_keeps_history_membership() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "abc")
    ed.input["text"] = "X"
    assert ed.run_action("InsertText") is True
    assert ed.cur().buf.get_text() == "Xabc"
    assert ed.undo.depth() == 1

    # Simulate an embedder mutating the exact inverse range without recording an
    # editor undo row.  Position-only replay must fail closed rather than erase Q.
    ed.cur().buf.replace_range(Cursor(0, 0), Cursor(0, 1), "Q")
    assert ed.cur().buf.get_text() == "Qabc"

    assert ed.undo_feedback() is False
    assert ed.cur().buf.get_text() == "Qabc"
    assert ed.undo.depth() == 1
    assert ed.undo.redo_depth() == 0
    assert ed.messages[-1].startswith("undo: refused stale edit (")
