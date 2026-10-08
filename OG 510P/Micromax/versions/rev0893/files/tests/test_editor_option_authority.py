from __future__ import annotations

import pytest

from micromax import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls


def _editor() -> Editor:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.new_buffer("main", "alpha\n")
    return ed


def _call_host(ed: Editor, name: str) -> None:
    ed.vm.stack.append(name)
    ed.vm.eval("hostcall", filename="<option-authority-test>")


def test_script_cannot_opt_get_capability_value_without_capability() -> None:
    ed = _editor()
    assert ed.exec_command_line("set cap.fs-root /secret/root") is True

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["cap.fs-root"]
        with pytest.raises(MicromaxError, match="cannot read capability option: cap.fs-root"):
            _call_host(ed, "ed.opt-get")
        assert ed.vm.stack == ["cap.fs-root"]


def test_script_cannot_opt_get_host_adjacent_option_without_capability() -> None:
    ed = _editor()
    assert ed.exec_command_line("set clipboard.external.cmd /secret/bin/copy") is True

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["clipboard.external.cmd"]
        with pytest.raises(MicromaxError, match="cannot read protected option: clipboard.external.cmd"):
            _call_host(ed, "ed.opt-get")
        assert ed.vm.stack == ["clipboard.external.cmd"]


def test_script_option_rows_redact_protected_values_but_keep_names() -> None:
    ed = _editor()
    assert ed.exec_command_line("set cap.fs-root /secret/root") is True
    assert ed.exec_command_line("set clipboard.external.cmd /secret/bin/copy") is True

    with ed.script_context(origin_id="script-a"):
        rows = {str(row[0]): row for row in ed.option_inventory_rows()}
        assert rows["cap.fs-root"][1] == "<protected>"
        assert rows["clipboard.external.cmd"][1] == "<protected>"
        assert rows["ignorecase"][1] in {"true", "false"}

        detail = ed.option_detail_row("cap.fs-root")
        assert detail is not None
        assert detail[0] == "cap.fs-root"
        assert detail[2] == "<protected>"
        assert "/secret" not in str(detail)

    direct = ed.option_detail_row("cap.fs-root")
    assert direct is not None
    assert direct[2] == "/secret/root"


def test_statusformat_opt_directive_does_not_leak_protected_option_values() -> None:
    ed = _editor()
    assert ed.exec_command_line("set cap.fs-root /secret/root") is True

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["root=$(opt:cap.fs-root) branch=$(if:opt:cap.fs-root|yes|no)"]
        _call_host(ed, "ed.statusfmt")
        rendered = str(ed.vm.stack[-1])

    assert "/secret/root" not in rendered
    assert rendered == "root= branch=no"


def test_cap_option_read_allows_explicit_protected_option_reads() -> None:
    ed = _editor()
    assert ed.exec_command_line("set cap.fs-root /secret/root") is True
    assert ed.exec_command_line("set cap.option-read true") is True

    with ed.script_context(origin_id="script-a"):
        ed.vm.stack[:] = ["cap.fs-root"]
        _call_host(ed, "ed.opt-get")
        assert ed.vm.stack == ["/secret/root"]
        detail = ed.option_detail_row("cap.fs-root")
        assert detail is not None
        assert detail[2] == "/secret/root"


def test_script_command_show_redacts_protected_option_value() -> None:
    ed = _editor()
    assert ed.exec_command_line("set cap.fs-root /secret/root") is True

    with ed.script_context(origin_id="script-a"):
        assert ed.exec_command_line("show cap.fs-root") is True

    assert "<protected>" in ed.messages[-1]
    assert "/secret/root" not in ed.messages[-1]


def test_option_read_capability_is_advertised() -> None:
    ed = _editor()
    ed.vm.stack.clear()
    _call_host(ed, "host.capabilities")
    features = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert "ed.option-read" in features
    assert features["ed.option-read"][1] == "cap.option-read"
    assert features["ed.option-read"][3] == 0

    assert ed.exec_command_line("set cap.option-read true") is True
    ed.vm.stack.clear()
    _call_host(ed, "host.capabilities")
    features = {str(row[0]): row for row in ed.vm.stack[-1]}
    assert features["ed.option-read"][3] == 1
