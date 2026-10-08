from __future__ import annotations

from pathlib import Path
import json
import os

import yaml

from vhk.project.macro_proof_contract import summarize_macro_proof_contract
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "logs").mkdir(parents=True)
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": []}))
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": True, "log_dir": "logs"},
                "macros": {"sig": "macros/sig.yaml"},
            }
        )
    )
    return proj


def test_latest_run_health_json_handles_missing_logs(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["latest-run-health-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.latest_run_health"
    assert payload["health"]["verdict"] == "unknown"
    assert payload["health"]["ready_to_iterate"] is False


def test_latest_run_health_json_reports_failure_and_next_step(tmp_path: Path):
    proj = _make_project(tmp_path)
    log_path = proj / "logs" / "run_demo.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 1.0, "run_id": "demo", "macro": "sig"}),
                json.dumps({"type": "wait_attempt", "kind": "window", "ts": 1.1, "attempt": 2, "matched": False, "workspace": "2", "wm": "i3", "selector": {"class": "Alacritty", "workspace": "2"}}),
                json.dumps({"type": "step_end", "ts": 1.4, "step_id": "s1", "step_type": "WaitForWindow", "ok": False, "duration_ms": 250, "error": "boom", "error_type": "AssertionError"}),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "demo", "macro": "sig", "ok": False}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    res = runner.invoke(app, ["latest-run-health-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["health"]["verdict"] == "fail"
    assert payload["health"]["ready_to_iterate"] is False
    assert payload["health"]["signals"]["error_count"] == 1
    assert payload["health"]["probe_hint"]["id"] == "window_wait_probe"
    assert payload["health"]["probe_hint"]["step_type"] == "WaitForWindow"
    assert payload["health"]["probe_hint"]["wait_kind"] == "window"
    assert payload["health"]["probe_hint"]["observation"]["source_id"] == "wait_attempt"
    assert payload["health"]["probe_hint"]["observation"]["observed"]["workspace"] == "2"
    assert payload["health"]["probe_hint"]["observation"]["observed"]["selector"] == {"class": "Alacritty", "workspace": "2"}
    assert payload["health"]["next_step"]["id"] == "inspect_failures"


def test_latest_run_health_json_reports_warn_when_run_ok_but_advice_warns(tmp_path: Path):
    proj = _make_project(tmp_path)
    log_path = proj / "logs" / "run_demo.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 1.0, "run_id": "demo", "macro": "sig"}),
                json.dumps({"type": "wait_start", "kind": "image", "ts": 1.1}),
                json.dumps({"type": "wait_end", "kind": "image", "ts": 4.0, "ok": True}),
                json.dumps({"type": "run_end", "ts": 5.0, "run_id": "demo", "macro": "sig", "ok": True}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    res = runner.invoke(app, ["latest-run-health-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["health"]["verdict"] == "warn"
    assert payload["health"]["ready_to_iterate"] is True
    assert payload["health"]["signals"]["warn_advice_count"] >= 1
    assert payload["health"]["next_step"]["id"] == "review_warnings"


def test_latest_run_health_json_marks_replay_stale_after_session_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    log_path = proj / "logs" / "run_demo.jsonl"
    log_path.write_text(
        "\n".join(
            [
                json.dumps({
                    "type": "run_start",
                    "ts": 1.0,
                    "run_id": "demo",
                    "macro": "sig",
                    "macro_proof_contract": summarize_macro_proof_contract(proj, "sig"),
                    "desktop_session_contract": {
                        "display": ":0",
                        "xauthority": "/tmp/xauth0",
                        "i3sock": "/tmp/i3-0.sock",
                        "session_type": "x11",
                        "current_desktop": "i3",
                    },
                }),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "demo", "macro": "sig", "ok": True}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    env = {**os.environ, "DISPLAY": ":1", "XAUTHORITY": "/tmp/xauth1", "I3SOCK": "/tmp/i3-1.sock", "XDG_SESSION_TYPE": "x11", "XDG_CURRENT_DESKTOP": "i3"}
    res = runner.invoke(app, ["latest-run-health-json", str(proj), "--no-pretty"], env=env)
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["health"]["verdict"] == "stale"
    assert payload["health"]["next_step"]["id"] == "rerun_after_session_change"
    assert payload["health"]["desktop_session_contract"]["in_sync"] is False
    assert payload["health"]["desktop_session_contract"]["i3sock_changed"] is True
