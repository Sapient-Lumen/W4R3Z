from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("*hooks*", "")
    return ed


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack[:] = list(args)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<hook-authority-test>")
    return list(ed.vm.stack)


def test_script_hook_inventory_hides_trusted_handlers_but_keeps_public_hook_name() -> None:
    ed = _editor()
    ed.vm.eval(
        ': trusted_handler "trusted" "ed.msg" hostcall ; '
        "' trusted_handler hook-add ed.pre-action",
        filename="<trusted-hook>",
    )

    with ed.script_context(origin_id="script-a"):
        assert "ed.pre-action" in ed._prompt_hook_names()
        assert ed.hook_inventory_rows("ed.pre-action") == []
        assert _hostcall(ed, "ed.hook-inventory-rows", "ed.pre-action")[-1] == []
        ed.vm.eval("hook-detail ed.pre-action", filename="<script>")
        assert ed.vm.stack.pop() == []

    assert ed.exec_command_line("set cap.hook-read true") is True
    with ed.script_context(origin_id="script-a"):
        rows = _hostcall(ed, "ed.hook-inventory-rows", "ed.pre-action")[-1]

    assert rows and rows[0][0] == "trusted_handler"
    assert rows[0][1] == 0
    assert rows[0][2][:2] == ["<trusted-hook>", 1]


def test_dynamic_trusted_hook_name_is_public_but_handler_and_source_are_hidden() -> None:
    ed = _editor()
    ed.vm.eval(
        'hook guarded-hook : trusted_handler "trusted" "ed.msg" hostcall ; '
        "' trusted_handler hook-add guarded-hook",
        filename="<trusted-hook>",
    )

    with ed.script_context(origin_id="script-a"):
        assert "guarded-hook" in ed._prompt_hook_names()
        assert ed.hook_inventory_rows("guarded-hook") == []
        assert _hostcall(ed, "ed.hook-detail-row", "guarded-hook")[-1] == [
            "guarded-hook",
            "guarded-hook",
            0,
            0,
            0,
            0,
        ]

    assert ed.exec_command_line("set cap.hook-read true") is True
    with ed.script_context(origin_id="script-a"):
        row = _hostcall(ed, "ed.hook-detail-row", "guarded-hook")[-1]
    assert row[1:3] == ["guarded-hook", 1]
    assert row[3] == "trusted_handler"
    assert str(row[4]).startswith("trusted_handler@<trusted-hook>:1:")
    assert row[5][:2] == ["<trusted-hook>", 1]


def test_same_origin_script_hook_is_visible_and_other_script_origin_is_hidden() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.vm.eval(
            'hook owned-hook : owned_handler "owned" "ed.msg" hostcall ; '
            "' owned_handler hook-add owned-hook",
            filename="<script-a>",
        )
        assert ed.hook_detail_row("owned-hook") is not None
        own_rows = ed.hook_inventory_rows("owned-hook")
        assert own_rows and own_rows[0][0] == "owned_handler"
        assert own_rows[0][1] == 0
        assert own_rows[0][2][:2] == ["<script-a>", 1]
        ed.vm.eval("owned-hook", filename="<script-a>")

    assert ed.messages[-1] == "owned"

    with ed.script_context(origin_id="script-b"):
        assert "owned-hook" in ed._prompt_hook_names()
        assert ed.hook_inventory_rows("owned-hook") == []
        assert ed.hook_detail_row("owned-hook") == ["owned-hook", "owned-hook", 0, 0, 0, 0]
        ed.vm.eval("owned-hook", filename="<script-b>")

    assert ed.messages.count("owned") == 1


def test_script_cannot_fire_trusted_hook_handler_without_explicit_capability() -> None:
    ed = _editor()
    ed.vm.eval(
        ': trusted_handler "trusted fired" "ed.msg" hostcall ; '
        "' trusted_handler hook-add ed.pre-action",
        filename="<trusted-hook>",
    )

    with ed.script_context(origin_id="script-a"):
        ed.vm.eval("ed.pre-action", filename="<script>")
    assert "trusted fired" not in ed.messages

    assert ed.exec_command_line("set cap.hook-read true") is True
    with ed.script_context(origin_id="script-a"):
        ed.vm.eval("ed.pre-action", filename="<script>")
    assert "trusted fired" not in ed.messages

    assert ed.exec_command_line("set cap.hook-fire true") is True
    with ed.script_context(origin_id="script-a"):
        ed.vm.eval("ed.pre-action", filename="<script>")
    assert ed.messages[-1] == "trusted fired"


def test_hook_read_and_fire_capabilities_are_advertised_separately() -> None:
    ed = _editor()
    rows = {str(row[0]): row for row in _hostcall(ed, "host.capabilities")[-1]}
    assert rows["ed.hook-read"][1] == "cap.hook-read"
    assert rows["ed.hook-read"][3] == 0
    assert rows["ed.hook-fire"][1] == "cap.hook-fire"
    assert rows["ed.hook-fire"][3] == 0

    assert ed.exec_command_line("set cap.hook-fire true") is True
    rows = {str(row[0]): row for row in _hostcall(ed, "host.capabilities")[-1]}
    assert rows["ed.hook-fire"][3] == 1


def test_core_hook_read_words_filter_protected_handlers_and_groups() -> None:
    ed = _editor()
    ed.vm.eval(
        'hook guarded-hook "trusted-group" hook-group! '
        ': trusted_handler "trusted" "ed.msg" hostcall ; '
        "' trusted_handler hook-add guarded-hook 0 hook-group!",
        filename="<trusted-hook>",
    )

    with ed.script_context(origin_id="script-a"):
        ed.vm.eval("hook-rows guarded-hook", filename="<script>")
        assert ed.vm.stack.pop() == []
        ed.vm.eval("hook-detail guarded-hook", filename="<script>")
        assert ed.vm.stack.pop() == []
        ed.vm.eval("hook-groups guarded-hook", filename="<script>")
        assert ed.vm.stack.pop() == []
        ed.vm.eval("hook@ guarded-hook", filename="<script>")
        assert ed.vm.stack.pop() == []

    assert ed.exec_command_line("set cap.hook-read true") is True
    with ed.script_context(origin_id="script-a"):
        ed.vm.eval("hook-detail guarded-hook", filename="<script>")
        rows = ed.vm.stack.pop()
        ed.vm.eval("hook-groups guarded-hook", filename="<script>")
        groups = ed.vm.stack.pop()
        ed.vm.eval("hook@ guarded-hook", filename="<script>")
        xts = ed.vm.stack.pop()

    assert rows and rows[0][0:2] == ["trusted_handler", "trusted-group"]
    assert rows[0][2][:2] == ["<trusted-hook>", 1]
    assert groups == ["trusted-group"]
    assert xts == []

    assert ed.exec_command_line("set cap.hook-fire true") is True
    with ed.script_context(origin_id="script-a"):
        ed.vm.eval("hook@ guarded-hook", filename="<script>")
        xts = ed.vm.stack.pop()
        ed.vm.stack.append(xts[0])
        ed.vm.eval("execute", filename="<script>")

    assert ed.messages[-1] == "trusted"


def test_core_hooks_listing_keeps_hook_names_public_without_handler_metadata(capsys) -> None:
    ed = _editor()
    ed.vm.eval("hook private-hook", filename="<trusted-hook>")

    with ed.script_context(origin_id="script-a"):
        ed.vm.eval("hooks", filename="<script>")
    captured = capsys.readouterr().out
    assert "private-hook" in captured
    assert "ed.pre-action" in captured
    assert "<trusted-hook>" not in captured
