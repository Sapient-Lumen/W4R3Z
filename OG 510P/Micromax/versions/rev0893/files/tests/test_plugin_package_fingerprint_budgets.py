from __future__ import annotations

from pathlib import Path

import pytest

from micromax.vm import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager


def _manager() -> tuple[Editor, PluginManager]:
    ed = Editor()
    install_editor_hostcalls(ed)
    pm = PluginManager(ed.vm)
    ed.plugin_manager = pm
    return ed, pm


def test_plugin_fingerprint_rejects_too_many_package_files(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "probe"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(': probe-word "ok" ;\n', encoding="utf-8")
    for index in range(3):
        (plug / f"extra-{index}.mx").write_text(f": helper-{index} {index} ;\n", encoding="utf-8")

    _ed, pm = _manager()
    assert pm.scan_tree(root) == ["probe"]
    pm.package_fingerprint_max_files = 3

    with pytest.raises(MicromaxError, match="too many files"):
        pm.grant_load("probe")

    assert "probe" not in pm.load_grants


def test_plugin_fingerprint_rejects_excess_total_package_bytes(tmp_path: Path) -> None:
    root = tmp_path / "plugins"
    plug = root / "probe"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(': probe-word "ok" ;\n', encoding="utf-8")
    (plug / "big.txt").write_text("x" * 80, encoding="utf-8")

    _ed, pm = _manager()
    assert pm.scan_tree(root) == ["probe"]
    pm.package_fingerprint_max_total_bytes = 64

    with pytest.raises(MicromaxError, match="package too large"):
        pm.grant_load("probe")

    assert "probe" not in pm.load_grants
