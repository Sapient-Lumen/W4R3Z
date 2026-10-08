from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "logs").mkdir(parents=True)
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": []}))
    (proj / "macros" / "alt.yaml").write_text(yaml.safe_dump({"name": "alt", "steps": []}))
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": True, "log_dir": "logs", "bus_socket": "bus.sock"},
                "bindings": [{"keys": "Mod4+Shift+S", "macro": "sig"}],
                "macros": {"sig": "macros/sig.yaml", "alt": "macros/alt.yaml"},
                "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
            }
        )
    )
    return proj


def _write_log(path: Path, *, run_id: str, macro: str, ok: bool, end_ts: float) -> None:
    path.write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": end_ts - 1.0, "run_id": run_id, "macro": macro}),
                json.dumps({"type": "step_end", "ts": end_ts - 0.5, "step_id": "s1", "step_type": "Return", "ok": ok, "duration_ms": 25}),
                json.dumps({"type": "run_end", "ts": end_ts, "run_id": run_id, "macro": macro, "ok": ok}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_generated_macro_latest_run_wrappers_use_matching_macro_log(tmp_path: Path):
    proj = _make_project(tmp_path)
    _write_log(proj / "logs" / "run_sig.jsonl", run_id="sig-run", macro="sig", ok=True, end_ts=2.0)
    _write_log(proj / "logs" / "run_alt.jsonl", run_id="alt-run", macro="alt", ok=False, end_ts=3.0)

    out_dir = tmp_path / "stack"
    wrapper = tmp_path / "vhk-wrapper.sh"
    wrapper.write_text(f"#!/usr/bin/env sh\nexec {sys.executable} -m vhk.cli \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)
    repo_src = Path(__file__).resolve().parents[1] / "src"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys", "--vhk-cmd", str(wrapper), "--vhk-pythonpath", str(repo_src)])
    assert res.exit_code == 0, res.output

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_src)
    bin_dir = out_dir / "bin"

    latest = subprocess.run([str(bin_dir / "macro_latest_run_json.sh"), "sig", "--no-pretty"], capture_output=True, text=True, env=env, check=False)
    assert latest.returncode == 0, latest.stderr
    payload = json.loads(latest.stdout)
    assert payload["latest_run"]["macro"] == "sig"
    assert payload["latest_run"]["run_id"] == "sig-run"

    report = subprocess.run([str(bin_dir / "macro_report_latest.sh"), "sig", "--json"], capture_output=True, text=True, env=env, check=False)
    assert report.returncode == 0, report.stderr
    report_payload = json.loads(report.stdout)
    assert report_payload["path"].endswith("run_sig.jsonl")
    assert report_payload["run"]["macro"] == "sig"

    trace_out = tmp_path / "sig.trace.json"
    trace = subprocess.run([str(bin_dir / "macro_trace_latest.sh"), "sig", str(trace_out)], capture_output=True, text=True, env=env, check=False)
    assert trace.returncode == 0, trace.stderr
    trace_payload = json.loads(trace_out.read_text(encoding="utf-8"))
    assert isinstance(trace_payload.get("traceEvents"), list)
    assert trace_out.exists()
