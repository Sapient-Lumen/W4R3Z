from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\n")
    return ed


def _hostcall(ed: Editor, name: str, *args: object) -> list[object]:
    ed.vm.stack.clear()
    for arg in args:
        ed.vm.stack.append(arg)
    ed.vm.stack.append(str(name))
    ed.vm.eval("hostcall", filename="<prompt-authority-test>")
    return list(ed.vm.stack)


def test_script_cannot_read_trusted_prompt_text_or_status() -> None:
    ed = _editor()
    ed.enter_prompt("command", prefill="save /secret/path")

    with ed.script_context(origin_id="script-a"):
        assert ed.status_model()["prompt_text"] == ""
        interaction = ed.interaction_status_model()
        assert "secret" not in interaction["interaction_line"]
        assert interaction["interaction_summary"] == ":<prompt>"
        assert _hostcall(ed, "ed.prompt-text")[-1] == ""
        assert _hostcall(ed, "ed.prompt-kind")[-1] == ""

    assert ed.prompt is not None
    assert ed.prompt.text == "save /secret/path"


def test_script_cannot_submit_trusted_prompt_without_capability() -> None:
    ed = _editor()
    ed.enter_prompt("command", prefill="showstatus")

    with ed.script_context(origin_id="script-a"):
        assert ed.submit_prompt() is False

    assert ed.prompt is not None
    assert ed.prompt.text == "showstatus"
    assert any("cap.prompt-write" in str(msg) for msg in ed.messages)


def test_script_prompt_set_taints_trusted_prompt_but_does_not_reveal_old_text() -> None:
    ed = _editor()
    ed.enter_prompt("command", prefill="save /secret/path")

    _hostcall(ed, "ed.prompt-set", "showstatus")

    assert ed.prompt is not None
    assert ed.prompt.text == "showstatus"
    assert bool(getattr(ed.prompt, "script_context", False)) is True
    assert "secret" not in "\n".join(str(msg) for msg in ed.messages)
    assert _hostcall(ed, "ed.prompt-submit")[-1] == 1
    assert ed.prompt is None


def test_same_origin_script_can_read_mutate_and_submit_own_prompt() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.enter_prompt("command", prefill="showstatus")
        assert ed.status_model()["prompt_text"] == "showstatus"
        assert _hostcall(ed, "ed.prompt-text")[-1] == "showstatus"
        assert ed.set_prompt_text("showstatus") is True
        assert ed.submit_prompt() is True

    assert ed.prompt is None
    assert ed.messages[-1].startswith("mode=")


def test_independent_script_cannot_read_or_submit_other_script_prompt() -> None:
    ed = _editor()

    with ed.script_context(origin_id="script-a"):
        ed.enter_prompt("command", prefill="showstatus")

    with ed.script_context(origin_id="script-b"):
        assert ed.status_model()["prompt_text"] == ""
        assert ed.submit_prompt() is False

    assert ed.prompt is not None
    assert ed.prompt.text == "showstatus"
    assert "different script origin" in ed.messages[-1]


def test_prompt_read_and_write_capabilities_are_separate() -> None:
    ed = _editor()
    ed.enter_prompt("command", prefill="showstatus")
    assert ed.exec_command_line("set cap.prompt-read true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.status_model()["prompt_text"] == "showstatus"
        assert ed.submit_prompt() is False

    assert ed.prompt is not None
    assert ed.prompt.text == "showstatus"
    assert ed.exec_command_line("set cap.prompt-write true") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.submit_prompt() is True

    assert ed.prompt is None
