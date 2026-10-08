from __future__ import annotations

from pathlib import Path

import pytest

from micromax.vm import MicromaxError
from micromax_editor.editor import Editor
from micromax_editor.micromax_bridge import install_editor_hostcalls
from micromax_editor.plugins import PluginManager, _collect_plugin_worker_result


def _sleeping_snapshot_worker(*args, **kwargs) -> None:  # type: ignore[no-untyped-def]
    import time

    time.sleep(60)


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


def test_plugin_discovery_uses_bounded_list_probe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "plugins"
    plug = root / "probe"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(': probe-word "ok" ;\n', encoding="utf-8")

    import micromax_editor.plugins as plugins_mod

    real_list = plugins_mod.list_dir_contained_bounded
    calls: list[tuple[str, str | None, int | None, float | None]] = []

    def recording_list(path, *, containment_root=None, limit=None, timeout_seconds=None):  # type: ignore[no-untyped-def]
        calls.append((str(path), None if containment_root is None else str(containment_root), limit, timeout_seconds))
        return real_list(
            path,
            containment_root=containment_root,
            limit=limit,
            timeout_seconds=timeout_seconds,
        )

    monkeypatch.setattr(plugins_mod, "list_dir_contained_bounded", recording_list)

    _ed, pm = _manager()
    pm.plugin_discovery_max_dirs = 8
    pm.plugin_discovery_timeout_seconds = 0

    assert pm.scan_tree(root) == ["probe"]
    assert calls == [(str(root.resolve()), str(root.resolve()), 9, 0.0)]


@pytest.mark.skipif(__import__("os").name != "posix", reason="fork worker timeout regression is POSIX-only")
def test_plugin_snapshot_timeout_worker_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import multiprocessing

    root = tmp_path / "plugins"
    plug = root / "probe"
    plug.mkdir(parents=True)
    (plug / "init.mx").write_text(': probe-word "ok" ;\n', encoding="utf-8")

    _ed, pm = _manager()
    assert pm.scan_tree(root) == ["probe"]
    pm.package_fingerprint_timeout_seconds = 0.01

    import micromax_editor.plugins as plugins_mod

    monkeypatch.setattr(
        plugins_mod,
        "_plugin_package_snapshot_worker",
        _sleeping_snapshot_worker,
    )
    monkeypatch.setattr(
        plugins_mod,
        "_plugin_worker_context",
        lambda: multiprocessing.get_context("spawn"),
    )

    with pytest.raises(MicromaxError, match="plugin snapshot timed out"):
        pm.grant_load("probe")

    assert "probe" not in pm.load_grants


class _StartedWorker:
    pid = 4242
    exitcode = 0

    def __init__(self) -> None:
        self.started = False
        self.alive = False
        self.terminated = False
        self.closed = False

    def start(self) -> None:
        self.started = True
        self.alive = True

    def is_alive(self) -> bool:
        return self.alive

    def terminate(self) -> None:
        self.terminated = True
        self.alive = False

    def join(self, timeout: float | None = None) -> None:
        del timeout

    def close(self) -> None:
        self.closed = True


def test_plugin_worker_missing_frame_terminates_child_and_closes_channel() -> None:
    from micromax import worker_process

    proc = _StartedWorker()
    channel = worker_process.create_worker_result_channel(max_bytes=1024)
    channel.sender.close()

    with pytest.raises(MicromaxError, match="plugin snapshot worker result failed: probe"):
        _collect_plugin_worker_result(  # type: ignore[arg-type]
            proc,
            channel,
            timeout=1.0,
            operation="plugin snapshot",
            plugin="probe",
        )

    assert proc.started is True
    assert proc.terminated is True
    assert proc.alive is False
    assert proc.closed is True
    assert channel.receiver.fileno() == -1


def test_plugin_worker_collector_replaces_infinite_deadline(monkeypatch) -> None:
    import micromax_editor.plugins as plugins_mod
    from micromax_editor.plugin_package import PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS

    seen: list[float] = []

    def collect(_proc, _channel, **kwargs):  # type: ignore[no-untyped-def]
        seen.append(float(kwargs["timeout_seconds"]))
        return ("ok", "digest", 1)

    monkeypatch.setattr(plugins_mod, "collect_worker_result", collect)
    payload = _collect_plugin_worker_result(  # type: ignore[arg-type]
        object(),
        object(),
        timeout=float("inf"),
        operation="plugin snapshot",
        plugin="probe",
    )

    assert payload == ("ok", "digest", 1)
    assert seen == [PLUGIN_PACKAGE_FINGERPRINT_TIMEOUT_SECONDS]
