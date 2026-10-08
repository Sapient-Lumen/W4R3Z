from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "runtime_repair_receipts"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": [{"type": "TypeText", "text": "hi"}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "runtime_repair_receipts", "macros": {"sig": "macros/sig.yaml"}}))
    return proj


def _write_runtime_repair_receipt(proj: Path, *, action: str, receipt_id: str, recorded_at: datetime, status: str, ok: bool, helper_command: str) -> None:
    receipts_root = proj / "build" / "runtime_control_receipts" / action
    history_root = receipts_root / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "stack_kind": f"vhk.project.runtime_{action}_receipt",
        "receipt_id": receipt_id,
        "recorded_at": recorded_at.isoformat().replace("+00:00", "Z"),
        "runtime_control": {
            "action": action,
            "recorded_at": recorded_at.isoformat().replace("+00:00", "Z"),
            "receipt_id": receipt_id,
            "helper_command": helper_command,
            "receipt_path": f"build/runtime_control_receipts/{action}/history/{receipt_id}.json",
        },
        "receipt": {
            "ok": ok,
            "status": status,
            "summary": f"{action} -> {status}",
            "recommended_followup": {"id": "inspect_runtime", "command": "./bin/check_runtime_json.sh"},
            f"{action}_command": helper_command,
        },
    }
    (history_root / f"{receipt_id}.json").write_text(json.dumps(payload), encoding="utf-8")
    (receipts_root / "latest.json").write_text(json.dumps(payload), encoding="utf-8")



def test_latest_runtime_repair_json_handles_missing_receipts(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["latest-runtime-repair-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.latest_runtime_repair"
    assert payload["latest_runtime_repair"] is None
    assert payload["runtime_control_receipts_root"]["relative_to_project"] == "build/runtime_control_receipts"
    assert payload["reload"]["available"] is False
    assert payload["restart"]["available"] is False



def test_latest_runtime_repair_json_prefers_newest_receipt_and_marks_recent(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
    _write_runtime_repair_receipt(
        proj,
        action="reload",
        receipt_id="reload-1",
        recorded_at=now - timedelta(minutes=20),
        status="runtime_contract_drift",
        ok=False,
        helper_command="./bin/reload_runtime_json.sh",
    )
    _write_runtime_repair_receipt(
        proj,
        action="restart",
        receipt_id="restart-1",
        recorded_at=now - timedelta(minutes=2),
        status="runtime_ready",
        ok=True,
        helper_command="./bin/restart_runtime_json.sh",
    )

    res = runner.invoke(app, ["latest-runtime-repair-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    latest = payload["latest_runtime_repair"]
    assert latest["action"] == "restart"
    assert latest["receipt_status"] == "runtime_ready"
    assert latest["ok"] is True
    assert latest["recent"] is True
    assert latest["helper_command"] == "./bin/restart_runtime_json.sh"
    assert latest["recommended_followup"]["command"] == "./bin/check_runtime_json.sh"
    assert latest["receipt_path"]["relative_to_project"] == "build/runtime_control_receipts/restart/latest.json"
    assert payload["reload"]["recent"] is False
    assert payload["restart"]["recent"] is True
