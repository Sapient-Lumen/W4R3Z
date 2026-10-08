from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from vhk.core.runner import Runner
from vhk.project.loader import load_project


def _write_project(tmp_path: Path, manifest: dict, macros: dict[str, dict]) -> Path:
    proj = tmp_path / "proj"
    (proj / "macros").mkdir(parents=True)
    (proj / "assets").mkdir(parents=True)
    for name, data in macros.items():
        (proj / "macros" / f"{name}.yaml").write_text(yaml.safe_dump(data))
    (proj / "project.yaml").write_text(yaml.safe_dump(manifest))
    return proj


def test_runner_get_and_wait_for_systemd_unit_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "GetSystemdUnitState", "unit": "demo.service", "scope": "user", "out_var": "before"},
                    {
                        "type": "WaitForSystemdUnitState",
                        "unit": "demo.service",
                        "scope": "user",
                        "active_state": ["active", "reloading"],
                        "sub_state": "running",
                        "poll_ms": 0,
                        "max_attempts": 1,
                        "out_var": "after",
                    },
                    {"type": "Return", "value_expr": "after['active_state']"},
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    monkeypatch.setattr(
        runner_mod.systemd_units_mod,
        "get_systemd_unit_state",
        lambda *a, **k: runner_mod.systemd_units_mod.SystemdUnitSample(
            "demo.service", "user", "inactive", load_state="loaded", active_state="inactive", sub_state="dead", unit_file_state="enabled"
        ),
    )
    monkeypatch.setattr(
        runner_mod.systemd_units_mod,
        "wait_for_systemd_unit_state",
        lambda *a, **k: runner_mod.systemd_units_mod.SystemdUnitSample(
            "demo.service", "user", "ok", load_state="loaded", active_state="active", sub_state="running", unit_file_state="enabled"
        ),
    )

    res = Runner(load_project(proj)).run("m")
    assert res.ok, res.error
    assert res.vars["before"]["active_state"] == "inactive"
    assert res.vars["systemd_status"] == "ok"
    assert res.vars["systemd_active_state"] == "active"
    assert res.vars["systemd_sub_state"] == "running"
    assert res.vars["systemd_unit_file_state"] == "enabled"
    assert res.vars["return_value"] == "active"


def test_wait_for_systemd_unit_state_timeout_surfaces_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    proj = _write_project(
        tmp_path,
        {"name": "p", "settings": {"event_log": False}, "macros": {"m": "macros/m.yaml"}},
        {
            "m": {
                "name": "m",
                "steps": [
                    {"type": "WaitForSystemdUnitState", "unit": "demo.service", "scope": "user", "active_state": "active", "timeout_ms": 20, "poll_ms": 0, "max_attempts": 1}
                ],
            }
        },
    )

    import vhk.core.runner as runner_mod

    def fake_wait(*a, **k):
        raise TimeoutError("timed out after 20ms (last status='inactive' active_state='inactive' sub_state='dead')")

    monkeypatch.setattr(runner_mod.systemd_units_mod, "wait_for_systemd_unit_state", fake_wait)

    res = Runner(load_project(proj)).run("m")
    assert not res.ok
    assert "WaitForSystemdUnitState" in (res.error or "") or "timed out" in (res.error or "")
