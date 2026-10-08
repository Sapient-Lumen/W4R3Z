from __future__ import annotations

from micromax_editor.buffer import Buffer, Cursor
from micromax_editor.editor import Editor, search_match_spans
from micromax_editor.search import (
    PackedOffsets,
    PackedSearchSpans,
    SearchState,
    navigate_search,
    scan_buffer,
)


def _quiet_view(ed: Editor) -> None:
    eb = ed.cur()
    ed.options.set("statusline", "false", local=eb.local_options)
    ed.options.set("infobar", "false", local=eb.local_options)
    ed.options.set("hlsearch", "true", local=eb.local_options)


def test_repeated_search_wraps_forward_and_backward_with_explicit_boundary_feedback() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two one")

    assert ed.find("one", literal=True, announce=True) is True
    assert ed.primary_cursor() == Cursor(0, 0)
    assert ed.messages[-1] == "find: *t* @ 1:0 (1/2)"

    assert ed.find_next() is True
    assert ed.primary_cursor() == Cursor(0, 8)
    assert ed.messages[-1] == "findnext: *t* @ 1:8 (2/2)"

    assert ed.find_next() is True
    assert ed.primary_cursor() == Cursor(0, 0)
    assert ed.messages[-1] == "findnext: *t* @ 1:0 (1/2) [wrapped to top]"

    assert ed.find_prev() is True
    assert ed.primary_cursor() == Cursor(0, 8)
    assert ed.messages[-1] == "findprev: *t* @ 1:8 (2/2) [wrapped to bottom]"


def test_initial_find_wraps_from_after_the_last_match_with_explicit_feedback() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two")
    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 7)

    assert ed.find("one", literal=True, announce=True) is True
    assert ed.primary_cursor() == Cursor(0, 0)
    assert ed.messages[-1] == "find: *t* @ 1:0 (1/1) [wrapped to top]"


def test_one_match_does_not_report_a_phantom_move() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one two")
    assert ed.find("one", literal=True) is True

    assert ed.find_next() is False
    assert ed.primary_cursor() == Cursor(0, 0)
    assert ed.messages[-1] == "findnext: *t* @ 1:0 (1/1) [only match]"

    assert ed.find_prev() is False
    assert ed.primary_cursor() == Cursor(0, 0)
    assert ed.messages[-1] == "findprev: *t* @ 1:0 (1/1) [only match]"


def test_overlapping_literal_candidates_do_not_disagree_across_surfaces() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "aaa")
    _quiet_view(ed)

    assert ed.find("aa", literal=True) is True
    assert ed.search_position_model()["summary"] == "1/1"
    assert ed.search_rows_model(3, 10)["rows"][0]["spans"] == [[0, 2]]
    assert ed.find_next() is False
    assert ed.messages[-1].endswith("(1/1) [only match]")


def test_newline_starting_matches_advance_without_cursor_clamp_rediscovery() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "a\nb\nc")

    assert ed.find("\n", literal=True, announce=True) is True
    assert ed.primary_cursor() == Cursor(0, 1)
    assert ed.messages[-1].endswith("(1/2)")

    assert ed.find_next() is True
    assert ed.primary_cursor() == Cursor(1, 1)
    assert ed.messages[-1].endswith("(2/2)")

    assert ed.find_next() is True
    assert ed.primary_cursor() == Cursor(0, 1)
    assert ed.messages[-1].endswith("(1/2) [wrapped to top]")


def test_ignorecase_literal_offsets_stay_in_original_unicode_coordinates() -> None:
    text = "Straße STRASSE"
    assert search_match_spans(
        text,
        "strasse",
        literal=True,
        case_sensitive=False,
    ) == [(7, 14)]

    ed = Editor()
    ed.new_buffer("*t*", text)
    _quiet_view(ed)
    assert ed.find("strasse", literal=True) is True
    assert ed.primary_cursor() == Cursor(0, 7)
    assert ed.search_position_model()["summary"] == "1/1"
    assert ed.search_rows_model(3, 20)["rows"][0]["spans"] == [[7, 14]]


def test_adjacent_regex_matches_and_zero_width_policy_are_shared() -> None:
    assert search_match_spans("12", r"\d", literal=False, case_sensitive=True) == [
        (0, 1),
        (1, 2),
    ]
    assert search_match_spans("abc", r"^", literal=False, case_sensitive=True) == []

    ed = Editor()
    ed.new_buffer("*t*", "12")
    _quiet_view(ed)
    assert ed.find(r"\d", literal=False) is True
    assert ed.search_position_model()["summary"] == "1/2"
    assert ed.search_rows_model(3, 10)["rows"][0]["spans"] == [[0, 1], [1, 2]]
    assert ed.find_next() is True
    assert ed.primary_cursor() == Cursor(0, 1)
    assert ed.search_position_model()["summary"] == "2/2"

    assert ed.find(r"^", literal=False) is False
    assert ed.search_position_model()["summary"] == "0/0"
    assert ed.search_rows_model(3, 10)["rows"][0]["spans"] == []


def test_cross_line_match_projects_to_each_visible_source_fragment() -> None:
    ed = Editor()
    ed.new_buffer("cross.txt", "ab\ncd")
    _quiet_view(ed)

    assert ed.find("b\nc", literal=True, announce=True) is True
    model = ed.search_rows_model(4, 10)
    assert model["match_rows"] == 2
    assert model["rows"][0]["spans"] == [[1, 2]]
    assert model["rows"][1]["spans"] == [[0, 1]]
    assert model["rows"][0]["current_spans"] == [[1, 2]]
    assert model["rows"][1]["current_spans"] == [[0, 1]]

    cues = ed.viewport_cues_model(4, 10)
    assert cues["rows"][0]["current_search_spans"] == [[1, 2]]
    assert cues["rows"][1]["current_search_spans"] == [[0, 1]]


def test_softwrap_continuation_does_not_invent_regex_anchor_match() -> None:
    ed = Editor()
    ed.new_buffer("wrap.txt", "xxxxfoo")
    _quiet_view(ed)
    eb = ed.cur()
    ed.options.set("softwrap", "true", local=eb.local_options)

    assert ed.find(r"^foo", literal=False) is False
    rows = ed.search_rows_model(4, 4)["rows"]
    assert [row["text"] for row in rows[:2]] == ["xxxx", "foo"]
    assert rows[0]["spans"] == []
    assert rows[1]["spans"] == []


def test_horizontal_scroll_fragment_does_not_invent_regex_anchor_match() -> None:
    ed = Editor()
    ed.new_buffer("scroll.txt", "xxxxfoo")
    _quiet_view(ed)
    eb = ed.cur()
    eb.cursors[eb.primary] = Cursor(0, 6)

    assert ed.find(r"^foo", literal=False) is False
    row = ed.search_rows_model(3, 3)["rows"][0]
    assert row["start_col"] == 4
    assert row["text"] == "foo"
    assert row["spans"] == []


def test_stale_search_snapshot_is_rejected_after_buffer_mutation() -> None:
    ed = Editor()
    ed.new_buffer("*t*", "one")
    state = SearchState(query="one", literal=True, case_sensitive=True)
    snapshot = scan_buffer(ed.cur().buf, state)
    assert snapshot.spans == ((0, 3),)

    ed.cur().buf.insert(Cursor(0, 0), "one ")
    result = navigate_search(
        ed.cur().buf,
        state,
        start=Cursor(0, 0),
        direction="forward",
        include_start=False,
        wrap=False,
        snapshot=snapshot,
    )
    assert result is not None
    assert result.cursor == Cursor(0, 4)
    assert result.match_count == 2


def test_search_snapshot_is_rejected_for_a_different_same_version_buffer() -> None:
    state = SearchState(query="one", literal=True, case_sensitive=True)
    first = Buffer("one x")
    second = Buffer("x one")
    snapshot = scan_buffer(first, state)

    result = navigate_search(
        second,
        state,
        start=Cursor(0, 0),
        direction="forward",
        include_start=True,
        wrap=False,
        snapshot=snapshot,
    )

    assert result is not None
    assert result.cursor == Cursor(0, 2)
    assert result.start == 2


def test_full_screen_reuses_one_search_snapshot_for_status_and_highlights(monkeypatch) -> None:
    import micromax_editor.editor as editor_module

    ed = Editor()
    ed.new_buffer("*t*", "alpha beta alpha")
    eb = ed.cur()
    ed.options.set("hlsearch", "true", local=eb.local_options)

    real_scan = editor_module.scan_buffer
    calls = 0

    def counted_scan(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_scan(*args, **kwargs)

    monkeypatch.setattr(editor_module, "scan_buffer", counted_scan)
    assert ed.find("alpha", literal=True) is True
    model = ed.screen_model(8, 40)

    # The candidate scan committed by find is the exact immutable snapshot used
    # by status and highlighting; unchanged literal repaint performs no rescan.
    assert calls == 1
    assert model["search_rows"]["rows"][0]["spans"] == [[0, 5], [11, 16]]
    assert ed.status_model()["search_summary"] == "1/2"
    assert calls == 1

    eb.buf.insert(Cursor(0, len(eb.buf.lines[0])), " alpha")
    changed = ed.screen_model(8, 40)
    assert calls == 2
    assert changed["search_rows"]["rows"][0]["spans"] == [
        [0, 5],
        [11, 16],
        [17, 22],
    ]
    ed.status_model()
    assert calls == 2


def test_risky_regex_timeout_is_visible_nonmutating_and_reused_across_repaint(
    monkeypatch,
) -> None:
    import micromax_editor.search as search_module
    from micromax.regex_runtime import RegexWorkerTimeoutError

    calls = 0

    def timed_out(*args, **kwargs):
        nonlocal calls
        calls += 1
        raise RegexWorkerTimeoutError("regex timed out after 0.25s")

    monkeypatch.setattr(search_module, "bounded_regex_spans", timed_out)

    ed = Editor()
    ed.new_buffer("risk.txt", ("a" * 80) + "!")
    _quiet_view(ed)
    before = ed.primary_cursor()

    assert ed.find(r"(a+)+$", literal=False) is False
    assert ed.primary_cursor() == before
    assert ed.messages[-1] == "find: regex timed out after 0.25s"
    assert calls == 1

    first = ed.screen_model(5, 40)
    second = ed.screen_model(5, 40)
    assert calls == 1
    assert first["search_rows"]["match_rows"] == 0
    assert second["search_rows"]["match_rows"] == 0

    # A failed candidate does not replace the replayable search register, so
    # repaint and later buffer generations do not retry the rejected regex.
    assert ed.search.query == ""
    ed.cur().buf.insert(Cursor(0, len(ed.cur().buf.lines[0])), "x")
    ed.screen_model(5, 40)
    assert calls == 1


def test_invalid_regex_is_not_misreported_as_not_found() -> None:
    ed = Editor()
    ed.new_buffer("invalid.txt", "alpha")
    before = ed.primary_cursor()

    assert ed.find("(", literal=False) is False
    assert ed.primary_cursor() == before
    assert ed.messages[-1].startswith("find: invalid regex:")
    assert "not found" not in ed.messages[-1]


def test_editor_search_match_budget_failure_is_visible_and_nonmutating() -> None:
    ed = Editor()
    ed.new_buffer("dense.txt", "a a a")
    ed.search_max_matches = 2
    before = ed.primary_cursor()

    assert ed.find("a", literal=True) is False
    assert ed.primary_cursor() == before
    assert ed.messages[-1] == "find: search match limit exceeded: more than 2 matches"


def test_direct_editor_risky_regex_uses_real_worker_for_success_and_timeout() -> None:
    state = SearchState(
        query=r"(a+)+$",
        literal=False,
        case_sensitive=True,
    )

    success = scan_buffer(Buffer("aaaa"), state, timeout_seconds=1.0)
    assert success.worker_routed is True
    assert success.error == ""
    assert success.spans == ((0, 4),)

    timeout = scan_buffer(
        Buffer(("a" * 24) + "!"),
        state,
        timeout_seconds=0.000001,
    )
    assert timeout.worker_routed is True
    assert timeout.timed_out is True
    assert timeout.error.startswith("regex timed out after ")
    assert timeout.spans == ()

def test_literal_search_snapshot_retains_compact_native_coordinate_arrays() -> None:
    matches = 10_000
    snapshot = scan_buffer(
        Buffer("x " * matches),
        SearchState(query="x", literal=True, case_sensitive=True),
        max_matches=matches,
    )

    assert isinstance(snapshot.line_starts, PackedOffsets)
    assert isinstance(snapshot.spans, PackedSearchSpans)
    assert len(snapshot.spans) == matches
    assert snapshot.spans[0] == (0, 1)
    assert snapshot.spans[-1] == ((matches - 1) * 2, ((matches - 1) * 2) + 1)
    assert snapshot.storage_bytes == snapshot.line_starts.storage_bytes + (matches * 16)


def test_packed_coordinate_repr_is_bounded_for_dense_search_snapshots() -> None:
    offsets = PackedOffsets(range(100_000))
    spans = PackedSearchSpans((index, index + 1) for index in range(100_000))

    rendered_offsets = repr(offsets)
    rendered_spans = repr(spans)
    assert len(rendered_offsets) < 180
    assert len(rendered_spans) < 220
    assert "count=100000" in rendered_offsets
    assert "count=100000" in rendered_spans
    assert "99999" in rendered_offsets
    assert "(99999, 100000)" in rendered_spans

