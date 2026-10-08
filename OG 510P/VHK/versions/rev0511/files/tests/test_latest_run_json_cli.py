from __future__ import annotations

from pathlib import Path
import json

import yaml
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


def test_latest_run_json_reports_latest_log_and_artifacts(tmp_path: Path):
    proj = _make_project(tmp_path)
    log_path = proj / "logs" / "run_demo.jsonl"
    shot = proj / "logs" / "error_sig_s1.png"
    diff = proj / "logs" / "diff_assert.png"
    shot.write_bytes(b"png")
    diff.write_bytes(b"png")
    log_path.write_text(
        "\n".join(
            [
                json.dumps({"type": "run_start", "ts": 1.0, "run_id": "demo", "macro": "sig"}),
                json.dumps({"type": "wait_attempt", "kind": "image", "ts": 1.2}),
                json.dumps({"type": "step_end", "ts": 1.4, "step_id": "s1", "step_type": "Click", "ok": False, "duration_ms": 250, "screenshot": str(shot), "error": "boom", "error_type": "AssertionError"}),
                json.dumps({"type": "visual_diff_artifact", "ts": 1.5, "mode": "assert", "path": str(diff)}),
                json.dumps({"type": "run_end", "ts": 2.0, "run_id": "demo", "macro": "sig", "ok": False}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    res = runner.invoke(app, ["latest-run-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.latest_run"
    assert payload["project"]["name"] == "p"
    latest = payload["latest_run"]
    assert latest["run_id"] == "demo"
    assert latest["macro"] == "sig"
    assert latest["ok"] is False
    assert latest["error_count"] == 1
    assert latest["wait_attempt_total"] == 1
    assert latest["log"]["relative_to_project"] == "logs/run_demo.jsonl"
    assert latest["artifacts"]["trace_default_out"]["relative_to_project"] == "build/traces/latest.trace.json"
    assert latest["artifacts"]["error_screenshots"][0]["relative_to_project"] == "logs/error_sig_s1.png"
    assert latest["artifacts"]["visual_diff_artifacts"][0]["relative_to_project"] == "logs/diff_assert.png"
    assert latest["artifacts"]["visual_diff_artifacts"][0]["mode"] == "assert"


def test_latest_run_json_handles_missing_logs(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["latest-run-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["latest_run"] is None
    assert payload["default_trace_out"]["relative_to_project"] == "build/traces/latest.trace.json"
