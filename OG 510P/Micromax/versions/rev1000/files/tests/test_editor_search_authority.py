from __future__ import annotations

import pytest

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import restore_plugin_callback_state, snapshot_plugin_callback_state


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\nbeta\nalpha\ngamma\n")
    return ed


def _cursor_tuple(ed: Editor) -> tuple[int, int]:
    c = ed.primary_cursor()
    return (int(c.line), int(c.col))


def test_script_cannot_read_or_replay_trusted_active_search_without_capability() -> None:
    ed = _editor()
    assert ed.find("alpha", literal=True, announce=True) is True
    assert ed.search_position_model()["query"] == "alpha"
    before = _cursor_tuple(ed)

    with ed.script_context(origin_id="script-a"):
        assert ed.search_position_model()["query"] == ""
        assert ed.status_model()["search_query"] == ""
        rows = ed.search_rows_model(8, 40)
        assert rows["query"] == ""
        assert rows["active"] == 0
        assert ed.find_next() is False

    assert _cursor_tuple(ed) == before
    assert "script context cannot replay active search: findnext" in ed.messages[-1]
    assert "cap.search-replay" in ed.messages[-1]


def test_denied_script_find_hostcall_preserves_query_operand_and_trusted_search() -> None:
    ed = _editor()
    assert ed.find("alpha", literal=True) is True

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["beta", "ed.find"]
        with pytest.raises(Exception, match="script context cannot replay active search: replace"):
            ed.vm.eval("hostcall", filename="<search-authority-test>")

    assert "beta" in ed.vm.stack
    assert ed.search.query == "alpha"


def test_script_can_read_and_replay_own_active_search() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        assert ed.find("alpha", literal=True) is True
        assert ed.search_position_model()["query"] == "alpha"
        assert ed.find_next() is True
        assert _cursor_tuple(ed) == (2, 0)


def test_independent_scripts_cannot_replay_each_others_search() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        assert ed.find("alpha", literal=True) is True

    before = _cursor_tuple(ed)
    with ed.script_context(origin_id="script-b"):
        assert ed.search_position_model()["query"] == ""
        assert ed.find_next() is False

    assert _cursor_tuple(ed) == before
    assert "different script origin" in ed.messages[-1]


def test_search_read_and_replay_capabilities_are_separate() -> None:
    ed = _editor()
    assert ed.find("alpha", literal=True) is True
    assert ed.exec_command_line("set cap.search-read true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.search_position_model()["query"] == "alpha"
        assert ed.find_next() is False

    assert _cursor_tuple(ed) == (0, 0)
    assert ed.exec_command_line("set cap.search-replay true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.find_next() is True

    assert _cursor_tuple(ed) == (2, 0)


def test_search_replay_capability_allows_replace_but_not_cross_origin_read() -> None:
    ed = _editor()
    assert ed.find("alpha", literal=True) is True
    assert ed.exec_command_line("set cap.search-replay true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.find("beta", literal=True) is True
        assert ed.search_position_model()["query"] == "beta"

    # The replacement search is now script-owned, so the same script may read it
    # even without cap.search-read.  A different script still cannot.
    with ed.script_context(origin_id="script-b"):
        assert ed.search_position_model()["query"] == ""


def test_script_cannot_change_trusted_search_flavor_through_find_prompt_action() -> None:
    ed = _editor()
    assert ed.find("alpha", literal=True) is True
    assert ed.search.literal is True

    with ed.script_context(origin_id="script-a"):
        assert ed.run_action("FindRegex") is False

    assert ed.search.literal is True
    assert "script context cannot replay active search: set-literal" in ed.messages[-1]


def test_plugin_callback_rollback_restores_active_search_register() -> None:
    ed = _editor()
    assert ed.find("alpha", literal=True) is True
    snap = snapshot_plugin_callback_state(ed.vm)

    # Simulate a failed callback's shared-runtime rollback after the callback
    # changed search state under trusted/editor authority.  The real plugin path
    # uses the same snapshot/restore helpers when an exception escapes.
    assert ed.exec_command_line("set cap.search-replay true") is True
    assert ed.find("beta", literal=True) is True
    restore_plugin_callback_state(ed.vm, snap)

    assert ed.search.query == "alpha"
    assert ed.search_position_model()["query"] == "alpha"
