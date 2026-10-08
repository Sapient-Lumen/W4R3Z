from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _call_host(ed: Editor, name: str) -> None:
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<test>")


@pytest.mark.parametrize(
    ("host", "arg", "message"),
    [
        ("ed.open-url", "https://example.com/", "ed.open-url disabled"),
        ("ed.shell", "echo hi", "ed.shell disabled"),
        ("ed.fs-read", "note.txt", "ed.fs-read disabled"),
        ("ed.fs-list", ".", "ed.fs-list disabled"),
        ("ed.fs-stat", ".", "ed.fs-stat disabled"),
        ("ed.open", "note.txt", "ed.open disabled"),
        ("ed.require", "plugin.mx", "ed.require disabled"),
    ],
)
def test_capability_denied_hostcalls_preserve_operation_argument(host: str, arg: str, message: str) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.append(arg)
    with pytest.raises(MicromaxError, match=message):
        _call_host(ed, host)

    assert ed.vm.stack == [arg]


def test_disabled_plugin_reload_preserves_name_inside_script_context() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ed.vm.stack.append("demo")
        _call_host(ed, "plugin.reload")

    assert ed.vm.stack == ["demo", 0]
    assert ed.messages[-1] == "plugin reload: disabled for scripts (cap.fs-require)"


def test_script_blocked_opt_set_preserves_name_and_value() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    with ed.script_context():
        ed.vm.stack.extend(["cap.fs-save", "true"])
        with pytest.raises(MicromaxError, match="script context cannot modify capability option"):
            _call_host(ed, "ed.opt-set")

    assert ed.vm.stack == ["cap.fs-save", "true"]


def test_type_preflight_for_enabled_hostcall_preserves_bad_argument() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("set cap.fs-read true")

    ed.vm.stack.append(123)
    with pytest.raises(MicromaxError, match="ed.fs-read: expected str"):
        _call_host(ed, "ed.fs-read")

    assert ed.vm.stack == [123]


@pytest.mark.parametrize(
    ("host", "args", "message"),
    [
        ("ed.disk-states", ["all"], "ed.disk-states: expected int"),
        ("ed.diff", ["many"], "ed.diff: expected int"),
        ("ed.revert", ["force"], "ed.revert: expected int"),
        ("ed.save-info", ["force"], "ed.save-info: expected int"),
        ("ed.save-as-info", ["target.txt", "force"], "ed.save-as-info: expected int"),
        ("ed.save-as-info", [123, 1], "ed.save-as-info: expected str"),
    ],
)
def test_structured_file_hostcall_type_errors_preserve_arguments(
    host: str,
    args: list[object],
    message: str,
) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack.extend(args)
    with pytest.raises(MicromaxError, match=message):
        _call_host(ed, host)

    assert ed.vm.stack == args


def test_script_idempotent_keybind_repetition_is_noop_not_ownership_change() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    before = ed.keymap.get_binding_exact("UpArrow", mode="prompt")
    assert before is not None
    assert before.script_context is False

    with ed.script_context():
        ed.bind_key_checked("UpArrow", "PromptSuggestPrev|PromptHistoryPrev", mode="prompt")

    after = ed.keymap.get_binding_exact("UpArrow", mode="prompt")
    assert after is before
    assert after.script_context is False

    with ed.script_context():
        with pytest.raises(PermissionError, match="trusted registration"):
            ed.bind_key_checked("UpArrow", "CursorUp", mode="prompt")

    assert ed.keymap.get_binding_exact("UpArrow", mode="prompt") is before


def test_runtime_registration_denials_preserve_hostcall_operands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    assert ed.exec_command_line("bind F40 command:help")
    trusted = ed.keymap.get_binding_exact("F40")
    assert trusted is not None

    with ed.script_context():
        ed.vm.stack[:] = ["F40", "command:quit"]
        with pytest.raises(MicromaxError, match="cannot modify keybinding: F40"):
            _call_host(ed, "ed.bind")
        assert ed.vm.stack == ["F40", "command:quit"]

    with ed.script_context():
        ed.vm.stack[:] = ["F40", "spoofed"]
        with pytest.raises(MicromaxError, match="cannot modify keybinding: F40"):
            _call_host(ed, "ed.bind-doc")
        assert ed.vm.stack == ["F40", "spoofed"]

    with ed.script_context():
        ed.vm.stack[:] = ["F40"]
        with pytest.raises(MicromaxError, match="cannot modify keybinding: F40"):
            _call_host(ed, "ed.unbind")
        assert ed.vm.stack == ["F40"]

    assert ed.keymap.get_binding_exact("F40") is trusted

    ed.vm.eval(": fake-save ( args -- ok ) drop 1 ;", filename="<script>")
    xt = ed.vm.find_word("fake-save")
    original = ed.command_dispatcher.get("save")
    assert original is not None

    with ed.script_context():
        ed.vm.stack[:] = [xt, "save", "fake save"]
        with pytest.raises(MicromaxError, match="cannot modify command: save"):
            _call_host(ed, "ed.cmd-add")
        assert ed.vm.stack == [xt, "save", "fake save"]

    with ed.script_context():
        ed.vm.stack[:] = ["save"]
        with pytest.raises(MicromaxError, match="cannot modify command: save"):
            _call_host(ed, "ed.cmd-rm")
        assert ed.vm.stack == ["save"]

    assert ed.command_dispatcher.get("save") is original


def test_active_keymode_and_reserved_group_denials_preserve_operands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.set_key_mode("trusted-capture", capture=True)

    for host in ["ed.keymode!", "ed.keymode-push", "ed.keymode-push-once", "ed.prefix-mode"]:
        with ed.script_context():
            ed.vm.stack[:] = ["script-mode"]
            with pytest.raises(MicromaxError, match="trusted active mode"):
                _call_host(ed, host)
            assert ed.vm.stack == ["script-mode"]

    with ed.script_context():
        ed.vm.stack[:] = ["plugin:spoof"]
        with pytest.raises(MicromaxError, match="reserved editor group"):
            _call_host(ed, "ed.group!")
        assert ed.vm.stack == ["plugin:spoof"]


def test_clipboard_and_macro_mutation_type_errors_preserve_operands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    ed.vm.stack[:] = [123]
    with pytest.raises(MicromaxError, match="ed.set-clipboard: expected str"):
        _call_host(ed, "ed.set-clipboard")
    assert ed.vm.stack == [123]
    assert ed.clipboard_text() == ""

    ed.vm.stack[:] = [["x"], "badkind"]
    with pytest.raises(MicromaxError, match="kind must be items"):
        _call_host(ed, "ed.set-clipboard-items")
    assert ed.vm.stack == [["x"], "badkind"]

    ed.vm.stack[:] = ["not-list", "demo"]
    with pytest.raises(MicromaxError, match="macro: expected list"):
        _call_host(ed, "ed.macro-set")
    assert ed.vm.stack == ["not-list", "demo"]

    ed.vm.stack[:] = ["demo", "twice"]
    with pytest.raises(MicromaxError, match="ed.macro-play: expected int"):
        _call_host(ed, "ed.macro-play")
    assert ed.vm.stack == ["demo", "twice"]


def test_control_hostcall_type_errors_preserve_operands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    for host, args, message in [
        ("ed.run", [123], "ed.run: expected str"),
        ("ed.press-key", [123], "ed.press-key: expected str"),
        ("ed.command", [123], "ed.command: expected str"),
        ("ed.command-edit", [123], "ed.command-edit: expected str"),
        ("ed.topic-prompt", [123], "ed.topic-prompt: expected str"),
        ("ed.binding-prompt", [123], "ed.binding-prompt: expected str"),
    ]:
        ed.vm.stack[:] = list(args)
        with pytest.raises(MicromaxError, match=message):
            _call_host(ed, host)
        assert ed.vm.stack == args


def test_scope_quote_hostcall_type_errors_preserve_operands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)

    for host in ["ed.with-viewport", "ed.with-messages", "ed.capture-messages", "ed.with-cursorstate"]:
        ed.vm.stack[:] = ["not-a-quotation"]
        with pytest.raises(MicromaxError, match=f"{host}: expected quotation"):
            _call_host(ed, host)
        assert ed.vm.stack == ["not-a-quotation"]


def test_timer_hostcall_type_errors_preserve_operands() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval("[ 1 drop ]", filename="<q>")
    q = ed.vm.stack.pop()

    ed.vm.stack[:] = ["bad-delay", q]
    with pytest.raises(MicromaxError, match="ed.after: expected int"):
        _call_host(ed, "ed.after")
    assert ed.vm.stack == ["bad-delay", q]
    assert ed.timers.pending_count() == 0

    ed.vm.stack[:] = [100, "not-a-quotation"]
    with pytest.raises(MicromaxError, match="ed.after: expected quotation"):
        _call_host(ed, "ed.after")
    assert ed.vm.stack == [100, "not-a-quotation"]
    assert ed.timers.pending_count() == 0

    ed.vm.stack[:] = ["not-an-id"]
    with pytest.raises(MicromaxError, match="ed.cancel-timer: expected int"):
        _call_host(ed, "ed.cancel-timer")
    assert ed.vm.stack == ["not-an-id"]


def test_bridge_hostcalls_do_not_use_consuming_vm_pop_helpers() -> None:
    """Bridge hostcalls should preflight operands before removing them.

    The VM's legacy pop helpers remove a value before checking its type.  The
    editor bridge is a policy boundary, so malformed script calls should keep
    their operation operands available as evidence.
    """

    from pathlib import Path

    text = Path("src/micromax_editor/micromax_bridge.py").read_text(encoding="utf-8")
    forbidden = ["vm.pop_", "vm.pop()", "vm.stack.pop"]
    assert [needle for needle in forbidden if needle in text] == []


@pytest.mark.parametrize(
    ("host", "args", "message"),
    [
        ("ed.screen-model", [10, "wide"], "ed.screen-model: expected int"),
        ("ed.statusline-text", ["wide"], "ed.statusline-text: expected int"),
        ("ed.command-palette-rows", [123], "ed.command-palette-rows: expected str"),
        ("ed.prompt-complete", ["next"], "ed.prompt-complete: expected int"),
        ("ed.input-set", [123, "value"], "ed.input-set: expected str"),
        ("ed.with-messages", ["not-a-quotation"], "ed.with-messages: expected quotation"),
    ],
)
def test_bridge_hostcall_type_errors_preserve_operands(
    host: str,
    args: list[object],
    message: str,
) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.stack[:] = list(args)

    with pytest.raises(MicromaxError, match=message):
        _call_host(ed, host)

    assert ed.vm.stack == args


def test_timer_schedule_type_error_preserves_delay_and_quotation() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval("[ 1 drop ]", filename="<quote>")
    quote = ed.vm.stack.pop()
    ed.vm.stack[:] = ["not-ms", quote]

    with pytest.raises(MicromaxError, match="ed.after: expected int"):
        _call_host(ed, "ed.after")

    assert ed.vm.stack == ["not-ms", quote]
    assert getattr(ed.timers, "_tasks") == {}


def test_viewport_store_type_error_preserves_operands_and_viewport() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("viewport-boundary", "hello")
    ed.set_viewport(top_line=7, left_col=3, height=11, width=22, follow_cursor=False)
    before = dict(ed.viewport_model())
    args: list[object] = [1, "left", 9, 40]
    ed.vm.stack[:] = list(args)

    with pytest.raises(MicromaxError, match="ed.viewport!: expected int"):
        _call_host(ed, "ed.viewport!")

    assert ed.vm.stack == args
    assert dict(ed.viewport_model()) == before



def test_cancel_timer_denial_preserves_timer_id() -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.eval('1000 [ 1 drop ] "ed.after" hostcall', filename="<trusted-timer>")
    tid = ed.vm.pop_int()
    assert ed.timers.pending_count() == 1

    with ed.script_context():
        ed.vm.stack[:] = [tid]
        with pytest.raises(MicromaxError, match="cannot modify timer"):
            _call_host(ed, "ed.cancel-timer")
        assert ed.vm.stack == [tid]

    assert ed.timers.pending_count() == 1


@pytest.mark.parametrize(
    ("host", "args", "message"),
    [
        ("ed.command-detail-row", [123], "ed.command-detail-row: expected str"),
        ("ed.action-detail-row", [123], "ed.action-detail-row: expected str"),
        ("ed.binding-detail-row", [123], "ed.binding-detail-row: expected str"),
        ("ed.resolve-key", [123], "ed.resolve-key: expected str"),
        ("ed.keymode-detail-row", [123], "ed.keymode-detail-row: expected str"),
        ("ed.hook-detail-row", [123], "ed.hook-detail-row: expected str"),
        ("ed.command-palette", [123], "ed.command-palette: expected str"),
        ("ed.apropos-section-summary-rows", [123], "ed.apropos-section-summary-rows: expected str"),
        ("ed.jump-detail-row", [123], "ed.jump-detail-row: expected str"),
        ("ed.find", [123], "ed.find: expected str"),
        ("ed.option-detail-row", [123], "ed.option-detail-row: expected str"),
        ("ed.opt-get", [123], "ed.opt-get: expected str"),
        ("ed.input-get", [123], "ed.input-get: expected str"),
    ],
)
def test_query_and_prompt_hostcall_type_errors_preserve_operands(
    host: str,
    args: list[object],
    message: str,
) -> None:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("query-boundary", "alpha beta")
    ed.input["text"] = "safe"

    ed.vm.stack[:] = list(args)
    with pytest.raises(MicromaxError, match=message):
        _call_host(ed, host)

    assert ed.vm.stack == args
    if host == "ed.command-palette":
        assert ed.prompt is None
    if host == "ed.input-get":
        assert ed.input == {"text": "safe"}
