from __future__ import annotations

from pathlib import Path

import pytest

import vhk.system.systemd_units as mod


def _mkexe(tmp_path: Path, name: str) -> Path:
    p = tmp_path / name
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)
    return p


def test_get_systemd_unit_state_parses_show_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "systemctl")
    monkeypatch.setenv("PATH", str(tmp_path))

    def fake_run(cmd, capture_output=True, text=True, check=False, env=None):
        assert cmd[:4] == [str(tmp_path / "systemctl"), "--user", "show", "demo.service"]

        class R:
            returncode = 0
            stdout = "\n".join([
                "Id=demo.service",
                "LoadState=loaded",
                "ActiveState=active",
                "SubState=running",
                "UnitFileState=enabled",
                "FragmentPath=/tmp/demo.service",
                "Description=Demo Service",
            ]) + "\n"
            stderr = ""

        return R()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    sample = mod.get_systemd_unit_state("demo.service", scope="user")
    assert sample.scope == "user"
    assert sample.status == "ok"
    assert sample.active_state == "active"
    assert sample.sub_state == "running"
    assert sample.unit_file_state == "enabled"
    assert sample.fragment_path == "/tmp/demo.service"
    assert sample.description == "Demo Service"


def test_get_systemd_unit_state_classifies_missing_manager(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _mkexe(tmp_path, "systemctl")
    monkeypatch.setenv("PATH", str(tmp_path))

    def fake_run(cmd, capture_output=True, text=True, check=False, env=None):
        class R:
            returncode = 1
            stdout = ""
            stderr = "Failed to connect to bus: No medium found\n"

        return R()

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    sample = mod.get_systemd_unit_state("demo.service", scope="user")
    assert sample.status == "manager_unavailable"
    assert "No medium found" in (sample.error or "")


def test_wait_for_systemd_unit_state_retries_until_match(monkeypatch: pytest.MonkeyPatch):
    values = iter([
        mod.SystemdUnitSample("demo.service", "user", "inactive", load_state="loaded", active_state="inactive", sub_state="dead"),
        mod.SystemdUnitSample("demo.service", "user", "activating", load_state="loaded", active_state="activating", sub_state="start"),
        mod.SystemdUnitSample("demo.service", "user", "ok", load_state="loaded", active_state="active", sub_state="running"),
    ])
    monkeypatch.setattr(mod, "get_systemd_unit_state", lambda *a, **k: next(values))

    attempts: list[tuple[int, str, str | None, bool]] = []
    sample = mod.wait_for_systemd_unit_state(
        "demo.service",
        scope="user",
        active_state="active",
        sub_state="running",
        timeout_ms=100,
        poll_ms=0,
        max_attempts=5,
        on_attempt=lambda attempt, cur, ok: attempts.append((attempt, cur.status, cur.active_state, ok)),
    )
    assert sample.status == "ok"
    assert attempts == [
        (1, "inactive", "inactive", False),
        (2, "activating", "activating", False),
        (3, "ok", "active", True),
    ]


def test_wait_for_systemd_unit_state_times_out(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        mod,
        "get_systemd_unit_state",
        lambda *a, **k: mod.SystemdUnitSample("demo.service", "user", "inactive", load_state="loaded", active_state="inactive", sub_state="dead"),
    )
    with pytest.raises(TimeoutError):
        mod.wait_for_systemd_unit_state("demo.service", scope="user", active_state="active", timeout_ms=10, poll_ms=0, max_attempts=2)
