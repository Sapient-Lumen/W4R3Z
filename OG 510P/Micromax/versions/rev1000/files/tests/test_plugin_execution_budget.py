from __future__ import annotations

from pathlib import Path

import pytest

from micromax import VM
from micromax.vm import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_execution_budget import (
    DEFAULT_PLUGIN_EXECUTION_STEP_BUDGET,
    effective_plugin_execution_step_budget,
)
from micromax_editor.plugins import PluginManager


def _manager(*, budget: int = 40) -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    ed.vm.editor_plugin_execution_step_budget = int(budget)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


def _plugin(root: Path, name: str, source: str) -> Path:
    path = root / name
    path.mkdir()
    (path / "init.mx").write_text(source, encoding="utf-8")
    return path


def test_eval_host_budget_cannot_be_cleared_by_set_budget() -> None:
    vm = VM(load_stdlib=False)

    with pytest.raises(MicromaxError, match="Execution budget exceeded") as err:
        vm.eval(
            "-1 set-budget [ 1 ] [ ] while",
            filename="<host-budget-bypass>",
            step_budget=20,
        )

    assert err.value.code == -100
    assert vm._host_budget_stack == []
    assert vm._base_step_budget is None
    assert vm._budget_stack == []


def test_set_budget_only_changes_base_inside_with_budget() -> None:
    vm = VM(load_stdlib=False)

    vm.eval("[ 5 [ -1 set-budget [ 1 ] [ ] while ] with-budget ] catch")

    assert vm.stack == [-100]
    assert vm._base_step_budget is None
    assert vm._budget_stack == []


def test_plugin_source_loop_is_bounded_and_transaction_rolls_back(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(root, "loop", "-1 set-budget [ 1 ] [ ] while\n")

    ed, pm = _manager(budget=30)
    assert pm.load_tree(root) == []

    assert "loop" not in pm.plugins
    assert "loop" not in ed.vm.modules
    assert any(name == "loop" and "Execution budget exceeded" in detail for name, detail in pm.load_errors)
    assert ed.vm.wordlist_access_scope is None
    assert getattr(ed.vm, "current_plugin_name", None) is None
    assert ed.vm._host_budget_stack == []


def test_plugin_lifecycle_loop_is_bounded_and_candidate_is_not_committed(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "loop",
        ": init -1 set-budget [ 1 ] [ ] while ;\n",
    )

    ed, pm = _manager(budget=30)
    assert pm.load_tree(root) == []

    assert "loop" not in pm.plugins
    assert "loop" not in ed.vm.modules
    assert any(name == "loop" and "Execution budget exceeded" in detail for name, detail in pm.load_errors)
    assert ed.vm.wordlist_access_scope is None
    assert ed.vm._host_budget_stack == []


def test_delayed_plugin_callback_loop_returns_control_and_rolls_back_side_effects(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "loop",
        "\n".join(
            [
                ": leaked drop 1 ;",
                ": run drop",
                "  ' leaked \"leaked\" \"must roll back\" \"ed.cmd-add\" hostcall drop",
                "  -1 set-budget [ 1 ] [ ] while",
                "  1 ;",
                "' run \"loop-run\" \"bounded callback\" \"ed.cmd-add\" hostcall drop",
            ]
        )
        + "\n",
    )

    ed, pm = _manager(budget=55)
    assert [plugin.name for plugin in pm.load_tree(root)] == ["loop"]

    assert ed.exec_command_line("loop-run") is False
    assert ed.command_dispatcher.get("leaked") is None
    assert any("Execution budget exceeded" in message for message in ed.messages)
    assert ed.vm.wordlist_access_scope is None
    assert getattr(ed.vm, "current_plugin_name", None) is None
    assert ed.vm._host_budget_stack == []

    # The shared VM remains usable after the interrupted callback.
    ed.vm.eval("20 22 +", filename="<after-plugin-budget>")
    assert ed.vm.pop_int() == 42


def test_plugin_turn_restores_shared_script_budget_state(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "budgeter",
        "\n".join(
            [
                "999999 set-budget",
                ": run drop 888888 set-budget 1 ;",
                "' run \"budgeter-run\" \"budget isolation\" \"ed.cmd-add\" hostcall drop",
            ]
        )
        + "\n",
    )

    ed, pm = _manager(budget=200)
    ed.vm.eval("123 set-budget", filename="<trusted-base-budget>")
    assert ed.vm._base_step_budget == 123

    assert [plugin.name for plugin in pm.load_tree(root)] == ["budgeter"]
    assert ed.vm._base_step_budget == 123

    assert ed.exec_command_line("budgeter-run") is True
    assert ed.vm._base_step_budget == 123
    assert ed.vm._budget_stack == []
    assert ed.vm._host_budget_stack == []


def test_plugin_budget_tuning_defaults_and_explicit_disable() -> None:
    vm = VM(load_stdlib=False)
    assert effective_plugin_execution_step_budget(vm) == DEFAULT_PLUGIN_EXECUTION_STEP_BUDGET

    for malformed in ("malformed", 0.5, False, None):
        vm.editor_plugin_execution_step_budget = malformed
        assert effective_plugin_execution_step_budget(vm) == DEFAULT_PLUGIN_EXECUTION_STEP_BUDGET

    vm.editor_plugin_execution_step_budget = "0"
    assert effective_plugin_execution_step_budget(vm) is None


def test_plugin_keybinding_callback_uses_fresh_protected_budget(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "keyloop",
        "\n".join(
            [
                ": spin -1 set-budget [ 1 ] [ ] while ;",
                '"F24" "mx: spin" "ed.bind" hostcall',
            ]
        )
        + "\n",
    )

    ed, pm = _manager(budget=45)
    assert [plugin.name for plugin in pm.load_tree(root)] == ["keyloop"]

    assert ed.dispatch_key("F24") is False
    assert any("Execution budget exceeded" in message for message in ed.messages)
    assert ed.vm._host_budget_stack == []
    assert ed.vm._budget_stack == []


def test_plugin_timer_callback_uses_fresh_protected_budget(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "timerloop",
        "\n".join(
            [
                ": spin -1 set-budget [ 1 ] [ ] while ;",
                '0 [ spin ] "ed.after" hostcall drop',
            ]
        )
        + "\n",
    )

    ed, pm = _manager(budget=45)
    assert [plugin.name for plugin in pm.load_tree(root)] == ["timerloop"]
    assert ed.timers.pending_count() == 1

    assert ed.pump_timers() == 1
    assert ed.timers.pending_count() == 0
    assert any("Execution budget exceeded" in message for message in ed.messages)
    assert ed.vm._host_budget_stack == []
    assert ed.vm._budget_stack == []


def test_plugin_hook_callback_uses_fresh_protected_budget(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "hookloop",
        "\n".join(
            [
                ": spin-hook 2drop -1 set-budget [ 1 ] [ ] while ;",
                "' spin-hook hook-add ed.on-action",
            ]
        )
        + "\n",
    )

    ed, pm = _manager(budget=45)
    assert [plugin.name for plugin in pm.load_tree(root)] == ["hookloop"]

    assert ed.run_action("Noop") is False
    assert any("Execution budget exceeded" in message for message in ed.messages)
    assert ed.vm._host_budget_stack == []
    assert ed.vm._budget_stack == []


def test_host_budget_rejects_fractional_or_boolean_counts() -> None:
    vm = VM(load_stdlib=False)

    for invalid in (0.5, True):
        with pytest.raises(MicromaxError, match="step_budget must be an integer"):
            with vm.host_step_budget(invalid):  # type: ignore[arg-type]
                pass

    assert vm._host_budget_stack == []


def test_nested_host_evaluation_cannot_reset_outer_budget() -> None:
    vm = VM(load_stdlib=False)

    def nested(inner: VM) -> None:
        inner.eval("1 drop " * 200, filename="<nested-budget>", step_budget=10_000)

    vm.register_host("nested", nested)
    with pytest.raises(MicromaxError, match="Execution budget exceeded"):
        vm.eval('"nested" hostcall', filename="<outer-budget>", step_budget=12)

    assert vm._host_budget_stack == []


def test_plugin_deinit_loop_cannot_block_unload_and_keeps_plugin_live(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "deinitloop",
        ": deinit -1 set-budget [ 1 ] [ ] while ;\n",
    )

    ed, pm = _manager(budget=45)
    assert [plugin.name for plugin in pm.load_tree(root)] == ["deinitloop"]
    original = pm.plugins["deinitloop"]

    with pytest.raises(MicromaxError, match="Execution budget exceeded"):
        pm.unload("deinitloop")

    assert pm.plugins["deinitloop"] is original
    assert ed.vm.modules["deinitloop"] == original.wid
    assert ed.vm._host_budget_stack == []
    ed.vm.eval("6 7 *", filename="<after-deinit-budget>")
    assert ed.vm.pop_int() == 42

    # The host-owned recovery lane does not execute the hostile deinit again.
    pm.unload("deinitloop", force=True)
    assert "deinitloop" not in pm.plugins


def test_plugin_string_amplification_is_denied_before_native_allocation(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    source = "a" * 64
    replacement = "b" * 64
    _plugin(
        root,
        "amplifier",
        "\n".join(
            [
                f': run drop "{source}" "a" "{replacement}" s-replace drop 1 ;',
                "' run \"amplify\" \"bounded native string allocation\" "
                '"ed.cmd-add" hostcall drop',
            ]
        )
        + "\n",
    )

    ed, pm = _manager(budget=200)
    assert [plugin.name for plugin in pm.load_tree(root)] == ["amplifier"]
    ed.vm.hostcall_result_max_bytes = 128

    assert ed.exec_command_line("amplify") is False
    assert any(
        "hostcall result budget exceeded: s-replace: 4096 bytes > 128" in message
        for message in ed.messages
    )
    assert ed.vm.wordlist_access_scope is None
    assert getattr(ed.vm, "current_plugin_name", None) is None
    assert ed.vm._host_budget_stack == []

    ed.vm.eval("6 7 *", filename="<after-plugin-allocation-budget>")
    assert ed.vm.pop_int() == 42


def test_plugin_integer_amplification_is_checked_before_python_bigint_growth(
    tmp_path: Path,
) -> None:
    root = tmp_path / "plugins"
    root.mkdir()
    _plugin(
        root,
        "intamplifier",
        "\n".join(
            [
                ': run drop 2 dup * dup * dup * dup * dup * dup * 1 ;',
                "' run \"amplify-int\" \"checked integer amplification\" "
                '"ed.cmd-add" hostcall drop',
            ]
        )
        + "\n",
    )

    ed, pm = _manager(budget=200)
    assert [plugin.name for plugin in pm.load_tree(root)] == ["intamplifier"]

    assert ed.exec_command_line("amplify-int") is False
    assert any(
        "integer overflow: * exceeds signed 64-bit range" in message
        for message in ed.messages
    )
    assert ed.vm.wordlist_access_scope is None
    assert getattr(ed.vm, "current_plugin_name", None) is None
    assert ed.vm._host_budget_stack == []

    ed.vm.eval("20 22 +", filename="<after-plugin-integer-overflow>")
    assert ed.vm.pop_int() == 42
