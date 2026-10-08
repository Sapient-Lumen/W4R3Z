from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _write_jsonl(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


def test_report_outputs_slowest_steps(tmp_path: Path) -> None:
    log = tmp_path / "run_test.jsonl"
    _write_jsonl(
        log,
        [
            {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m", "dry_run": False},
            {"ts": 1.1, "type": "step_end", "macro": "m", "step_id": "0", "step_type": "Delay", "ok": True, "attempt": 1, "duration_ms": 120},
            {"ts": 1.2, "type": "step_retry", "macro": "m", "step_id": "1", "step_type": "WaitForImage", "attempt": 1},
            {"ts": 1.21, "type": "wait_start", "macro": "m", "kind": "image"},
            {"ts": 1.3, "type": "step_end", "macro": "m", "step_id": "1", "step_type": "WaitForImage", "ok": True, "attempt": 2, "duration_ms": 500},
            {"ts": 1.31, "type": "wait_attempt", "kind": "image", "attempt": 1, "found": False},
            {"ts": 1.32, "type": "wait_attempt", "kind": "image", "attempt": 2, "found": True},
            {"ts": 1.33, "type": "wait_end", "macro": "m", "kind": "image", "ok": True, "attempts": 2},
            {"ts": 1.4, "type": "run_end", "run_id": "r1", "ok": True},
        ],
    )

    res = runner.invoke(app, ["report", str(log), "--durations", "5", "--durations-min", "0"]) 
    assert res.exit_code == 0
    assert "VHK report" in res.output
    assert "Slowest steps" in res.output
    # WaitForImage should appear above Delay.
    assert "WaitForImage" in res.output
    assert "Delay" in res.output
    assert "Wait attempts" in res.output
    assert "Wait durations" in res.output


def test_report_json_and_check_exit_code(tmp_path: Path) -> None:
    log = tmp_path / "run_fail.jsonl"
    _write_jsonl(
        log,
        [
            {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m", "dry_run": False},
            {"ts": 1.1, "type": "step_end", "macro": "m", "step_id": "0", "step_type": "Delay", "ok": False, "attempt": 1, "duration_ms": 10, "error": "boom", "error_type": "RuntimeError"},
            {"ts": 1.2, "type": "run_end", "run_id": "r1", "ok": False, "error": "boom"},
        ],
    )

    res = runner.invoke(app, ["report", str(log), "--json"]) 
    assert res.exit_code == 0
    payload = json.loads(res.output)
    assert payload["run"]["ok"] is False
    assert payload["counts"]["error_steps"] == 1

    res2 = runner.invoke(app, ["report", str(log), "--json", "--check"]) 
    assert res2.exit_code == 1


def test_report_latest_from_project(tmp_path: Path) -> None:
    project_dir = tmp_path / "proj"
    (project_dir / "macros").mkdir(parents=True)
    (project_dir / "macros" / "m.yaml").write_text(yaml.safe_dump({"name": "m", "steps": [{"type": "Delay", "ms": 1}]}))
    (project_dir / "project.yaml").write_text(yaml.safe_dump({"name": "proj", "macros": {"m": "macros/m.yaml"}}))

    log_dir = project_dir / "logs"
    older = log_dir / "run_older.jsonl"
    newer = log_dir / "run_newer.jsonl"
    _write_jsonl(older, [{"ts": 1.0, "type": "run_start"}, {"ts": 2.0, "type": "run_end", "ok": True}])
    _write_jsonl(newer, [{"ts": 1.0, "type": "run_start"}, {"ts": 2.0, "type": "run_end", "ok": True}])
    # Ensure mtime differs.
    import os
    os.utime(older, (10, 10))
    os.utime(newer, (20, 20))

    res = runner.invoke(app, ["report", "--project", str(project_dir), "--latest", "--durations-min", "0"]) 
    assert res.exit_code == 0
    assert "run_newer.jsonl" in res.output


def test_report_shows_optimization_advice(tmp_path: Path) -> None:
    log = tmp_path / "run_advice.jsonl"
    _write_jsonl(log, [
        {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m", "dry_run": False},
        {"ts": 1.1, "type": "step_end", "macro": "m", "step_id": "0", "step_type": "Delay", "ok": True, "attempt": 1, "duration_ms": 2200},
        {"ts": 1.2, "type": "step_retry", "macro": "m", "step_id": "1", "step_type": "WaitForImage", "attempt": 1},
        {"ts": 1.21, "type": "step_retry", "macro": "m", "step_id": "1", "step_type": "WaitForImage", "attempt": 2},
        {"ts": 1.22, "type": "step_retry", "macro": "m", "step_id": "1", "step_type": "WaitForImage", "attempt": 3},
        {"ts": 1.23, "type": "wait_start", "macro": "m", "kind": "image"},
        {"ts": 4.23, "type": "step_end", "macro": "m", "step_id": "1", "step_type": "WaitForImage", "ok": True, "attempt": 4, "duration_ms": 3000},
        {"ts": 4.24, "type": "wait_attempt", "kind": "image", "attempt": 1, "found": False},
        {"ts": 4.25, "type": "wait_attempt", "kind": "image", "attempt": 2, "found": False},
        {"ts": 4.26, "type": "wait_attempt", "kind": "image", "attempt": 3, "found": True},
        {"ts": 4.27, "type": "wait_end", "macro": "m", "kind": "image", "ok": True, "attempts": 3},
        {"ts": 4.3, "type": "step_end", "macro": "m", "step_id": "2", "step_type": "TypeText", "ok": True, "attempt": 1, "duration_ms": 1500},
        {"ts": 6.0, "type": "run_end", "run_id": "r1", "ok": True},
    ])
    res = runner.invoke(app, ["report", str(log), "--durations-min", "0"])
    assert res.exit_code == 0
    assert "Optimization advice" in res.output
    assert "Fixed delays are a noticeable" in res.output
    assert "Polling waits dominate this" in res.output
    assert "Text entry is a measurable cost" in res.output


def test_report_json_includes_step_types_and_advice(tmp_path: Path) -> None:
    log = tmp_path / "run_json_advice.jsonl"
    _write_jsonl(log, [
        {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m", "dry_run": False},
        {"ts": 1.1, "type": "step_end", "macro": "m", "step_id": "0", "step_type": "Delay", "ok": True, "attempt": 1, "duration_ms": 1800},
        {"ts": 3.0, "type": "run_end", "run_id": "r1", "ok": True},
    ])
    res = runner.invoke(app, ["report", str(log), "--json"])
    assert res.exit_code == 0
    payload = json.loads(res.output)
    assert any(item["step_type"] == "Delay" for item in payload["step_types"])
    assert any(item["id"] == "delay-heavy" for item in payload["advice"])
