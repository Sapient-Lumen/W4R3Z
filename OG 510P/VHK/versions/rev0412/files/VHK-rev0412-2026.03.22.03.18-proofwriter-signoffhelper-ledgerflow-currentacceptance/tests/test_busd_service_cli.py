from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "sig.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sig",
                "steps": [{"type": "Return", "value_expr": '"OK"', "out_var": "return_value"}],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": False},
                "macros": {"sig": "macros/sig.yaml"},
                "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
            }
        )
    )
    return proj


def test_gen_vhk_busd_service_writes_unit(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "units"

    res = runner.invoke(app, ["gen-vhk-busd-service", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    # default name should include vhk-busd-p
    candidates = list(out_dir.glob("vhk-busd-*.service"))
    assert candidates, "expected a service file"
    text = candidates[0].read_text()
    assert "ExecStart=" in text
    assert "vhk" in text
    assert "busd" in text
    assert str(proj) in text
    assert "--watcher" in text
    assert "hotkeys" in text
    assert "PartOf=graphical-session.target" in text
    assert "BindsTo=graphical-session.target" in text
    assert "WantedBy=graphical-session.target" in text
