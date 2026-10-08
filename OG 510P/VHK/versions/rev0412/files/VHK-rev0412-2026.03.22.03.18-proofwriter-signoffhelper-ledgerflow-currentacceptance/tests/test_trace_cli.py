from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _write_jsonl(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


def test_trace_exports_chrome_trace_json(tmp_path: Path) -> None:
    log = tmp_path / "run_test.jsonl"
    _write_jsonl(
        log,
        [
            {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "main", "dry_run": False},
            {"ts": 1.1, "type": "step_start", "macro": "main", "step_id": "0", "step_type": "WaitForImage", "attempt": 1},
            {"ts": 1.11, "type": "wait_start", "kind": "image", "timeout_ms": 1000},
            {"ts": 1.12, "type": "wait_attempt", "kind": "image", "attempt": 1, "score": 0.1, "threshold": 0.8},
            {"ts": 1.20, "type": "wait_end", "kind": "image", "ok": True, "attempts": 1, "score": 0.9, "x": 10, "y": 20},
            {"ts": 1.21, "type": "step_end", "macro": "main", "step_id": "0", "step_type": "WaitForImage", "ok": True, "attempt": 1, "duration_ms": 110},
            {"ts": 1.3, "type": "run_end", "run_id": "r1", "ok": True},
        ],
    )

    res = runner.invoke(app, ["trace", str(log)])
    assert res.exit_code == 0
    payload = json.loads(res.output)
    assert "traceEvents" in payload
    events = payload["traceEvents"]
    # Should include a step slice and wait slice.
    assert any(e.get("ph") == "X" and e.get("name") == "WaitForImage" and e.get("cat") == "vhk.step" for e in events)
    assert any(e.get("ph") == "X" and e.get("name") == "wait:image" and e.get("cat") == "vhk.wait" for e in events)
    assert any(e.get("ph") == "i" and str(e.get("name", "")).startswith("attempt:image") for e in events)


def test_trace_infers_missing_step_start(tmp_path: Path) -> None:
    log = tmp_path / "run_test2.jsonl"
    _write_jsonl(
        log,
        [
            {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m", "dry_run": False},
            {"ts": 2.0, "type": "step_end", "macro": "m", "step_id": "0", "step_type": "Delay", "ok": True, "attempt": 1, "duration_ms": 1000},
            {"ts": 2.2, "type": "run_end", "run_id": "r1", "ok": True},
        ],
    )
    res = runner.invoke(app, ["trace", str(log)])
    assert res.exit_code == 0
    payload = json.loads(res.output)
    assert any(e.get("ph") == "X" and e.get("name") == "Delay" for e in payload["traceEvents"])


def test_trace_check_exit_code(tmp_path: Path) -> None:
    log = tmp_path / "run_fail.jsonl"
    _write_jsonl(
        log,
        [
            {"ts": 1.0, "type": "run_start", "run_id": "r1", "project": "p", "macro": "m", "dry_run": False},
            {"ts": 1.2, "type": "run_end", "run_id": "r1", "ok": False, "error": "boom"},
        ],
    )
    res = runner.invoke(app, ["trace", str(log), "--check"])
    assert res.exit_code == 1
