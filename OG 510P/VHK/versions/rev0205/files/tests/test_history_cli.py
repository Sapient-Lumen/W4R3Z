from __future__ import annotations

import json
import os
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _write_jsonl(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


def _make_project(tmp_path: Path) -> Path:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "m.yaml").write_text(yaml.safe_dump({"name": "m", "steps": [{"type": "Delay", "ms": 1}]}))
    (project_dir / "project.yaml").write_text(yaml.safe_dump({"name": "proj", "macros": {"m": "macros/m.yaml"}}))
    return project_dir


def test_history_lists_recent_runs_and_filters(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    log_dir = project_dir / "logs"

    ok_log = log_dir / "run_ok.jsonl"
    fail_log = log_dir / "run_fail.jsonl"

    _write_jsonl(
        ok_log,
        [
            {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m"},
            {"ts": 2.0, "type": "run_end", "run_id": "r1", "ok": True},
        ],
    )
    _write_jsonl(
        fail_log,
        [
            {"ts": 3.0, "type": "run_start", "run_id": "r2", "project": "p", "macro": "m"},
            {"ts": 4.5, "type": "run_end", "run_id": "r2", "ok": False, "error": "boom"},
        ],
    )

    os.utime(ok_log, (10, 10))
    os.utime(fail_log, (20, 20))

    # Rich tables can truncate long columns in captured output; validate ordering
    # and filtering via the JSON mode.
    res = runner.invoke(app, ["history", str(project_dir), "--limit", "10", "--json"])
    assert res.exit_code == 0
    payload0 = json.loads(res.output)
    assert payload0["count"] == 2
    assert payload0["runs"][0]["path"].endswith("run_fail.jsonl")
    assert payload0["runs"][1]["path"].endswith("run_ok.jsonl")

    res2 = runner.invoke(app, ["history", str(project_dir), "--status", "fail", "--json"])
    assert res2.exit_code == 0
    payload = json.loads(res2.output)
    assert payload["count"] == 1
    assert payload["runs"][0]["ok"] is False


def test_history_check_and_csv(tmp_path: Path) -> None:
    project_dir = _make_project(tmp_path)
    log_dir = project_dir / "logs"
    log = log_dir / "run_fail.jsonl"
    _write_jsonl(
        log,
        [
            {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m"},
            {"ts": 2.0, "type": "run_end", "run_id": "r1", "ok": False, "error": "boom"},
        ],
    )

    csv_out = tmp_path / "out.csv"
    res = runner.invoke(app, ["history", str(project_dir), "--csv", str(csv_out), "--json", "--check"])
    assert res.exit_code == 1
    assert csv_out.exists()
    assert "runs" in json.loads(res.output)
