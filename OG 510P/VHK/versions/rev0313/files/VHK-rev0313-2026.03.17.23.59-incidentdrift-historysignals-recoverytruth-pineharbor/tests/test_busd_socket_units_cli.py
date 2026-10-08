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

    # Force a stable bus socket path inside the project dir (so tests don't
    # depend on XDG_RUNTIME_DIR / %t substitution).
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": False, "bus_socket": "bus.sock"},
                "macros": {"sig": "macros/sig.yaml"},
                "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
            }
        )
    )

    return proj


def test_gen_vhk_busd_socket_units_writes_files(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "units"

    res = runner.invoke(app, ["gen-vhk-busd-socket-units", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    sockets = list(out_dir.glob("vhk-busd-*.socket"))
    services = list(out_dir.glob("vhk-busd-*.service"))
    assert sockets, "expected a .socket unit"
    assert services, "expected a .service unit"

    sock_text = sockets[0].read_text()
    assert "ListenDatagram=" in sock_text
    assert "bus.sock" in sock_text

    svc_text = services[0].read_text()
    assert "ExecStart=" in svc_text
    assert "busd" in svc_text
    assert str(proj) in svc_text
    assert "--watcher" in svc_text
    assert "hotkeys" in svc_text
    assert "Requires=" in svc_text
