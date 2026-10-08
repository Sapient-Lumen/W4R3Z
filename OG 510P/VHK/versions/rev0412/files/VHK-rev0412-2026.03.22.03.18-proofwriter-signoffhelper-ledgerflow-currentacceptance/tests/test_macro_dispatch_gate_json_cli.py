from __future__ import annotations

from pathlib import Path
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "dispatch_gate"
    (proj / "macros").mkdir(parents=True)
    (proj / "logs").mkdir(parents=True)
    (proj / "macros" / "ready.yaml").write_text(yaml.safe_dump({"name": "ready", "when": {"class": "Alacritty", "workspace": "2"}, "steps": [{"type": "TypeText", "text": "ready"}]}))
    (proj / "macros" / "prompty.yaml").write_text(yaml.safe_dump({"name": "prompty", "steps": [{"type": "PromptForm", "fields": [{"name": "name", "label": "Name"}]}, {"type": "TypeText", "text": "hi"}]}))
    (proj / "macros" / "stale.yaml").write_text(yaml.safe_dump({"name": "stale", "steps": [{"type": "TypeText", "text": "stale"}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "dispatch_gate", "settings": {"event_log": True, "log_dir": "logs"}, "bus_watchers": [{"name": "hotkeys", "event": "hotkey.fast", "dispatch": True}], "macros": {"ready": "macros/ready.yaml", "prompty": "macros/prompty.yaml", "stale": "macros/stale.yaml"}}))
    sidecar_payload = {"suggested": {"stable": {"class": "Alacritty", "workspace": "2"}}, "segments": [{"selector_kind": "stable", "transition_reason": "focus", "anchor": {"mode": "window"}}]}
    for name, ts in [("ready", 3000), ("prompty", 3000)]:
        sidecar = proj / "macros" / f"{name}.window-context.yaml"
        sidecar.write_text(yaml.safe_dump(sidecar_payload, sort_keys=False))
        os.utime(sidecar, (ts, ts))
        os.utime(proj / "macros" / f"{name}.yaml", (ts, ts))
    os.utime(proj / "macros" / "stale.yaml", (3000, 3000))
    with (proj / "logs" / "run_ready.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "run_start", "macro": "ready", "run_id": "run-ready", "ts": 1.0}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "ready", "run_id": "run-ready", "ts": 2.0, "ok": True}) + "\n")
    return proj


def test_macro_dispatch_gate_json_reports_checked_dispatch_for_ready_macro(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_dispatch_gate"
    assert payload["dispatch_readiness"]["can_emit_minimal_payload_now"] is True
    assert payload["decision"]["id"] == "dispatch_now"
    assert payload["dispatch_contract"]["checked_dispatch_command"] == "dispatch_macro_checked.sh ready"
    assert payload["dispatch_contract"]["gate_command"] == "macro_dispatch_gate_json.sh ready"
    assert payload["dispatch_contract"]["raw_dispatch_command"] == "dispatch_macro.sh ready"
    assert payload["dispatch_contract"]["bus_payload_minimal"] == {"macro": "ready"}
    assert payload["repair_action"]["id"] == "ready_to_dispatch"
    assert payload["repair_action"]["command"] == "dispatch_macro_checked.sh ready"
    assert payload["dispatch_readiness"]["repair_action"]["id"] == "ready_to_dispatch"
    assert payload["dispatch_readiness"]["desktop_target"]["selector_source_id"] == "recording_stable_selector"
    assert payload["dispatch_readiness"]["desktop_target"]["selector"] == {"class": "Alacritty", "workspace": "2"}
    assert payload["force_override"]["flag"] == "--force"


def test_macro_dispatch_gate_json_falls_back_to_direct_run_for_interactive_macro(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "prompty", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["preferred_execution_mode"] == "direct_run"
    assert payload["decision"]["id"] == "direct_run_only"
    assert payload["decision"]["command"] == "run_macro.sh prompty"
    assert payload["dispatch_readiness"]["blockers"] == ["interactive_inputs_require_direct_run"]
    assert payload["dispatch_readiness"]["primary_blocker_class_id"] == "direct_run_required"
    assert payload["dispatch_readiness"]["blocker_details"][0]["class_id"] == "direct_run_required"
    assert payload["repair_action"]["id"] == "use_direct_run"
    assert payload["repair_action"]["command"] == "run_macro.sh prompty"


def test_macro_dispatch_gate_json_requires_stabilization_when_recorder_debt_is_active(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "stale", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["decision"]["id"] == "stabilize_before_dispatch"
    assert payload["dispatch_readiness"]["can_emit_minimal_payload_now"] is False
    assert payload["dispatch_readiness"]["blockers"] == ["recorder_or_review_debt_active"]
    assert payload["dispatch_readiness"]["primary_blocker_class_id"] == "contract_debt"
    assert payload["dispatch_readiness"]["blocker_details"][0]["class_id"] == "contract_debt"
    assert payload["repair_action"]["id"] == "repair_recorder_contract"
    assert payload["repair_action"]["command"] == "record_macro.sh stale 5000"
    assert payload["dispatch_readiness"]["blocked_message"].startswith("dispatch gate blocked for stale: recorder_or_review_debt_active")
    assert payload["decision"]["command"] == "macro_author_loop_json.sh stale"


def test_macro_dispatch_gate_json_carries_live_probe_hint_for_unhealthy_matching_run(tmp_path: Path):
    proj = _make_project(tmp_path)
    with (proj / "logs" / "run_ready.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "run_start", "macro": "ready", "run_id": "run-ready", "ts": 1.0}) + "\n")
        fh.write(json.dumps({"type": "wait_attempt", "kind": "window_event", "ts": 1.1, "attempt": 1, "matched": False, "event": "focus", "name": "window::focus", "wm": "i3", "workspace": "2", "selector": {"class": "Alacritty", "workspace": "2"}}) + "\n")
        fh.write(json.dumps({"type": "step_end", "macro": "ready", "ts": 1.4, "step_id": "s1", "step_type": "WaitForWindowEvent", "ok": False, "duration_ms": 250, "error": "focused window did not match", "error_type": "AssertionError"}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "ready", "run_id": "run-ready", "ts": 2.0, "ok": False}) + "\n")

    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["decision"]["id"] == "inspect_before_dispatch"
    assert payload["dispatch_readiness"]["primary_blocker_class_id"] == "desktop_state_mismatch"
    assert payload["dispatch_readiness"]["live_probe_hint"]["id"] == "window_event_probe"
    assert payload["dispatch_readiness"]["live_probe_hint"]["step_type"] == "WaitForWindowEvent"
    assert payload["repair_action"]["id"] == "inspect_live_desktop_target"
    assert payload["repair_action"]["command"] == "macro_report_latest.sh ready"
    assert payload["dispatch_readiness"]["live_probe_hint"]["observation"]["source_id"] == "wait_attempt"
    assert payload["dispatch_readiness"]["live_probe_hint"]["observation"]["observed"]["event"] == "focus"
    assert payload["dispatch_readiness"]["blocker_details"][0]["live_probe_hint"]["wait_kind"] == "window_event"
    assert payload["dispatch_readiness"]["blocker_details"][0]["live_probe_hint"]["observation"]["observed"]["workspace"] == "2"
    assert "window_event" in payload["dispatch_readiness"]["blocked_message"]
