from __future__ import annotations

from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugin_runtime import cleanup_plugin_generation_state, cleanup_runtime_group, retag_runtime_group
from micromax_editor.plugins import PluginManager


def _editor_with_manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


def test_cleanup_runtime_group_reports_surface_failures_and_keeps_sweeping() -> None:
    ed, _pm = _editor_with_manager()
    seen: list[str] = []

    def broken_search_cleanup(group: str) -> int:
        seen.append(str(group))
        raise RuntimeError("search cleanup broke")

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]

    report = cleanup_runtime_group(ed.vm, "plugin:broken")

    assert report.action == "cleanup"
    assert report.group == "plugin:broken"
    assert not report.ok
    assert seen == ["plugin:broken"]
    failures = report.failures
    assert len(failures) == 1
    assert failures[0].surface == "search"
    assert failures[0].action == "remove_search_group"
    assert "search cleanup broke" in failures[0].detail
    assert any(row.surface == "help_history" and row.status == "ok" for row in report.operations)


def test_retag_runtime_group_reports_counts_and_manager_retains_evidence() -> None:
    ed, pm = _editor_with_manager()
    ed.vm.eval(
        "\n".join(
            [
                ": staged-hook ( -- ) ;",
                "' staged-hook hook-add ed.pre-action",
            ]
        ),
        filename="<retag-report>",
    )
    for handler in ed.vm.find_word("ed.pre-action").handlers:  # type: ignore[union-attr]
        handler.group = "plugin:alpha#reload1"

    report = pm._retag_group("plugin:alpha#reload1", "plugin:alpha")

    assert report.ok
    assert report.action == "retag"
    assert report.group == "plugin:alpha#reload1"
    assert report.target_group == "plugin:alpha"
    hook_row = next(row for row in report.operations if row.surface == "vm.hooks")
    assert hook_row.status == "ok"
    assert hook_row.count == 1
    assert pm.runtime_group_reports[-1] is report
    assert pm.runtime_group_failures() == []


def test_generation_cleanup_reports_surface_failures_and_keeps_sweeping() -> None:
    ed, _pm = _editor_with_manager()
    seen_help: list[tuple[object, object]] = []

    def broken_search_generation(plugin_root: object, generation: object) -> int:
        raise RuntimeError(f"search generation cleanup broke for {plugin_root}:{generation}")

    def help_history_seen(plugin_root: object, generation: object) -> int:
        seen_help.append((plugin_root, generation))
        return 0

    ed.remove_plugin_search_generation = broken_search_generation  # type: ignore[method-assign]
    ed.remove_plugin_help_history_generation = help_history_seen  # type: ignore[method-assign]

    report = cleanup_plugin_generation_state(
        ed.vm,
        group="plugin:alpha",
        plugin_load_root="/plugins/alpha",
        plugin_generation=7,
    )

    assert report.action == "generation-cleanup"
    assert report.group == "plugin:alpha"
    assert report.target_group == "generation:7"
    assert not report.ok
    failures = report.failures
    assert len(failures) == 1
    assert failures[0].surface == "search"
    assert failures[0].action == "remove_plugin_search_generation"
    assert "search generation cleanup broke" in failures[0].detail
    assert seen_help == [("/plugins/alpha", 7)]


def test_manager_runtime_group_failure_rows_are_small_and_filterable() -> None:
    ed, pm = _editor_with_manager()

    def broken_search_cleanup(group: str) -> int:
        raise RuntimeError("search cleanup broke for rows")

    ed.remove_search_group = broken_search_cleanup  # type: ignore[method-assign]
    pm._cleanup_group("plugin:alpha")
    pm._cleanup_group("plugin:beta#reload1")

    rows = pm.runtime_group_failure_rows()
    assert [row[0] for row in rows] == ["alpha", "beta"]
    assert rows[0][1:6] == ["cleanup", "plugin:alpha", "", "search", "remove_search_group"]
    assert "search cleanup broke for rows" in str(rows[0][6])
    assert [row[0] for row in pm.runtime_group_failure_rows("beta")] == ["beta"]
