from __future__ import annotations

from pathlib import Path
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "dispatch_catalog"
    (proj / "macros").mkdir(parents=True)
    (proj / "logs").mkdir(parents=True)
    (proj / "macros" / "ready.yaml").write_text(yaml.safe_dump({"name": "ready", "steps": [{"type": "TypeText", "text": "ready"}]}))
    (proj / "macros" / "candidate.yaml").write_text(yaml.safe_dump({"name": "candidate", "steps": [{"type": "TypeText", "text": "candidate"}]}))
    (proj / "macros" / "prompty.yaml").write_text(yaml.safe_dump({"name": "prompty", "steps": [{"type": "PromptForm", "fields": [{"name": "name", "label": "Name"}]}, {"type": "TypeText", "text": "hi"}]}))
    (proj / "macros" / "stale.yaml").write_text(yaml.safe_dump({"name": "stale", "steps": [{"type": "TypeText", "text": "stale"}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "dispatch_catalog", "settings": {"event_log": True, "log_dir": "logs"}, "bus_watchers": [{"name": "hotkeys", "event": "hotkey.fast", "dispatch": True}], "macros": {"ready": "macros/ready.yaml", "candidate": "macros/candidate.yaml", "prompty": "macros/prompty.yaml", "stale": "macros/stale.yaml"}}))
    sidecar_payload = {"segments": [{"selector_kind": "stable", "transition_reason": "focus", "anchor": {"mode": "window"}}]}
    for name, ts in [("ready", 3000), ("candidate", 3000), ("prompty", 3000)]:
        sidecar = proj / "macros" / f"{name}.window-context.yaml"
        sidecar.write_text(yaml.safe_dump(sidecar_payload, sort_keys=False))
        os.utime(sidecar, (ts, ts))
        os.utime(proj / "macros" / f"{name}.yaml", (ts, ts))
    os.utime(proj / "macros" / "stale.yaml", (3000, 3000))
    with (proj / "logs" / "run_ready.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "run_start", "macro": "ready", "run_id": "run-ready", "ts": 1.0}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "ready", "run_id": "run-ready", "ts": 2.0, "ok": True}) + "\n")
    return proj


def test_macro_dispatch_catalog_json_reports_project_dispatch_contract(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-dispatch-catalog-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_dispatch_catalog"
    assert payload["runtime"]["bus_event"] == "hotkey.fast"
    assert payload["project"]["dispatch_ready_now_count"] == 1
    assert payload["summary"]["thin_dispatch_macro_count"] == 3
    assert payload["summary"]["primary_macro_name"] == "ready"
    ready = payload["macros"][0]
    assert ready["dispatch_readiness"]["can_emit_minimal_payload_now"] is True
    assert ready["dispatch_contract"]["bus_payload_minimal"] == {"macro": "ready"}
    assert ready["dispatch_contract"]["generated_stack_command"] == "dispatch_macro.sh ready"
    assert ready["dispatch_contract"]["generated_stack_checked_command"] == "dispatch_macro_checked.sh ready"
    assert ready["dispatch_contract"]["generated_stack_gate_command"] == "macro_dispatch_gate_json.sh ready"
    assert "hotkey.fast" in ready["dispatch_contract"]["emit_bus_command"]
    candidate = payload["macros"][1]
    assert candidate["dispatch_readiness"]["blockers"] == ["latest_run_proof_not_clean"]
    prompty = payload["macros"][2]
    assert prompty["preferred_execution_mode"] == "direct_run"
    assert prompty["dispatch_readiness"]["blockers"] == ["interactive_inputs_require_direct_run"]
    stale = payload["macros"][3]
    assert stale["dispatch_readiness"]["blockers"] == ["recorder_or_review_debt_active"]


def test_macro_dispatch_catalog_json_accepts_explicit_bus_event_override(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-dispatch-catalog-json", str(proj), "--bus-event", "hotkey.override", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["runtime"]["bus_event"] == "hotkey.override"
    assert payload["runtime"]["bus_event_source"] == "explicit"
    assert "hotkey.override" in payload["primary_macro"]["dispatch_contract"]["emit_bus_command"]
