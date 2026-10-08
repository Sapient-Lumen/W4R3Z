from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.runtime_state_cache import write_runtime_state_cache, summarize_runtime_instance_witness_from_cache
from vhk.project.macro_proof_contract import summarize_macro_proof_contract
from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract
from vhk.project.desktop_session_contract import summarize_desktop_session_contract


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
        fh.write(json.dumps({"type": "run_start", "macro": "ready", "run_id": "run-ready", "ts": 1.0, "macro_proof_contract": summarize_macro_proof_contract(proj, "ready")}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "ready", "run_id": "run-ready", "ts": 2.0, "ok": True}) + "\n")
    return proj


def test_macro_dispatch_gate_json_prefers_stale_dispatch_evidence_before_reemit(tmp_path: Path):
    proj = _make_project(tmp_path)
    receipt_observed_at = datetime.now(timezone.utc).replace(microsecond=0)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "runtime_state": {"runtime_epoch_id": "epoch-a", "reload_count": 0},
            "runtime_contract": {"digest": "runtime-contract-1"},
            "dispatch_probe_observation": {
                "status": "ok",
                "ok": True,
                "observed_at": receipt_observed_at.isoformat().replace('+00:00', 'Z'),
                "roundtrip_latency_ms": 16.0,
                "latency_status": "within_budget",
                "latency_budget_ms": 60.0,
                "ack_pid": 1234,
                "probe_id": "probe-before-reload",
            },
        },
    )
    receipt_witness = summarize_runtime_instance_witness_from_cache(project_root=proj)
    initial = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert initial.exit_code == 0, initial.output
    initial_payload = json.loads(initial.stdout)
    gate_payload = {
        "preferred_execution_mode": initial_payload["preferred_execution_mode"],
        "dispatch_contract": dict(initial_payload.get("dispatch_contract") or {}),
        "dispatch_readiness": {"desktop_target": dict((initial_payload.get("dispatch_readiness") or {}).get("desktop_target") or {})},
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, "ready", bus_event="hotkey.fast", gate_payload=gate_payload)
    observed_desktop_session_contract = summarize_desktop_session_contract()
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-stale-ready",
        "recorded_at": (receipt_observed_at + timedelta(seconds=1)).isoformat().replace('+00:00', 'Z'),
        "project_root": str(proj),
        "macro": "ready",
        "bus_event": "hotkey.fast",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"ready"}', "valid_json": True, "json": {"macro": "ready"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "dispatch_receipt_contract": observed_contract,
        "desktop_session_contract": observed_desktop_session_contract,
        "dispatch_runtime_witness": receipt_witness,
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    (history_root / "dispatch-stale-ready.json").write_text(json.dumps(receipt), encoding="utf-8")

    write_runtime_state_cache(
        project_root=proj,
        payload={
            "runtime_state": {"runtime_epoch_id": "epoch-b", "reload_count": 1},
            "runtime_contract": {"digest": "runtime-contract-1"},
            "dispatch_probe_observation": {
                "status": "ok",
                "ok": True,
                "observed_at": (receipt_observed_at + timedelta(seconds=5)).isoformat().replace('+00:00', 'Z'),
                "roundtrip_latency_ms": 14.0,
                "latency_status": "within_budget",
                "latency_budget_ms": 60.0,
                "ack_pid": 1234,
                "probe_id": "probe-after-reload",
            },
        },
    )

    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["dispatch_readiness"]["can_emit_minimal_payload_now"] is True
    assert payload["dispatch_readiness"]["current_dispatch_evidence_available"] is False
    assert payload["dispatch_readiness"]["stale_dispatch_evidence_available"] is True
    assert payload["dispatch_readiness"]["latest_dispatch_evidence_status_id"] == "repair_runtime_before_reusing_receipt"
    assert payload["dispatch_readiness"]["latest_dispatch_evidence_current"] is False
    assert payload["dispatch_readiness"]["latest_dispatch_recommended_command"] == "warm_runtime_ticket.sh"
    assert payload["decision"]["id"] == "inspect_stale_dispatch_evidence"
    assert payload["decision"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert "warm_runtime_ticket.sh" in payload["decision"]["followup"]
    assert payload["repair_action"]["id"] == "inspect_stale_dispatch_evidence"
    assert payload["repair_action"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert payload["dispatch_history_workbench"]["source_id"] == "macro_dispatch_history_board.llm_workbench"
    assert payload["selected_handoff"]["source_kind"] == "dispatch_history_workbench"
    assert payload["selected_handoff"]["workbench_mode_id"] == "inspect_stale_dispatch_receipt"
    assert payload["selected_handoff"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert payload["dispatch_readiness"]["selected_handoff_source_kind"] == "dispatch_history_workbench"
    assert payload["dispatch_readiness"]["selected_handoff_mode_id"] == "inspect_stale_dispatch_receipt"
    assert payload["dispatch_readiness"]["selected_handoff_command"] == "macro_latest_dispatch_json.sh ready"


def test_macro_dispatch_gate_json_prefers_current_dispatch_evidence_before_reemit(tmp_path: Path):
    proj = _make_project(tmp_path)
    observed_at = datetime.now(timezone.utc).replace(microsecond=0)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "runtime_state": {"runtime_epoch_id": "epoch-1", "reload_count": 0},
            "runtime_contract": {"digest": "runtime-contract-1"},
            "dispatch_probe_observation": {
                "status": "ok",
                "ok": True,
                "observed_at": observed_at.isoformat().replace('+00:00', 'Z'),
                "roundtrip_latency_ms": 18.5,
                "latency_status": "within_budget",
                "latency_budget_ms": 60.0,
                "ack_pid": 1234,
                "probe_id": "probe-current",
            },
        },
    )
    observed_witness = summarize_runtime_instance_witness_from_cache(project_root=proj)
    initial = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert initial.exit_code == 0, initial.output
    initial_payload = json.loads(initial.stdout)
    assert initial_payload["dispatch_readiness"]["can_emit_minimal_payload_now"] is True
    gate_payload = {
        "preferred_execution_mode": initial_payload["preferred_execution_mode"],
        "dispatch_contract": dict(initial_payload.get("dispatch_contract") or {}),
        "dispatch_readiness": {"desktop_target": dict((initial_payload.get("dispatch_readiness") or {}).get("desktop_target") or {})},
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, "ready", bus_event="hotkey.fast", gate_payload=gate_payload)
    observed_desktop_session_contract = summarize_desktop_session_contract()
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-current-ready",
        "recorded_at": (observed_at + timedelta(seconds=1)).isoformat().replace('+00:00', 'Z'),
        "project_root": str(proj),
        "macro": "ready",
        "bus_event": "hotkey.fast",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"ready"}', "valid_json": True, "json": {"macro": "ready"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "dispatch_receipt_contract": observed_contract,
        "desktop_session_contract": observed_desktop_session_contract,
        "dispatch_runtime_witness": observed_witness,
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    (history_root / "dispatch-current-ready.json").write_text(json.dumps(receipt), encoding="utf-8")

    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["dispatch_readiness"]["can_emit_minimal_payload_now"] is True
    assert payload["dispatch_readiness"]["current_dispatch_evidence_available"] is True
    assert payload["dispatch_readiness"]["latest_dispatch_evidence_status_id"] == "current_warm_runtime_evidence"
    assert payload["dispatch_readiness"]["latest_dispatch_result"] == "emitted"
    assert payload["dispatch_readiness"]["latest_dispatch_route"] == "checked_dispatch"
    assert payload["dispatch_readiness"]["latest_dispatch_recommended_command"] == "macro_dispatch_gate_json.sh ready"
    assert payload["dispatch_contract"]["latest_dispatch_command"] == "macro_latest_dispatch_json.sh ready"
    assert payload["decision"]["id"] == "inspect_current_dispatch_evidence"
    assert payload["decision"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert payload["repair_action"]["id"] == "inspect_current_dispatch_evidence"
    assert payload["repair_action"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert payload["selected_handoff"]["source_kind"] == "dispatch_history_workbench"
    assert payload["selected_handoff"]["workbench_mode_id"] == "inspect_current_receipt_before_reemit"
    assert payload["selected_handoff"]["command"] == "macro_latest_dispatch_json.sh ready"


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
    assert payload["selected_handoff"]["source_kind"] == "execution_ticket"
    assert payload["selected_handoff"]["command"] == "dispatch_macro_checked.sh ready"
    assert payload["dispatch_readiness"]["desktop_target"]["selector_source_id"] == "macro_when"
    assert payload["dispatch_readiness"]["desktop_target"]["selector"] == {"app_id_regex": False, "title_regex": False, "class": "Alacritty", "workspace": "2"}
    assert payload["target_authority"]["status_id"] == "target_contract_defined_without_probe"
    assert payload["target_authority"]["proof_family"] == "selector_contract_only"
    assert payload["target_authority"]["selector_source_id"] == "macro_when"
    assert payload["target_authority"]["match_verdict"] == "unknown"
    assert payload["target_authority"]["recommended"]["command"] == "macro_dispatch_gate_json.sh ready"
    assert payload["dispatch_readiness"]["target_authority_status_id"] == "target_contract_defined_without_probe"
    assert payload["dispatch_readiness"]["target_authority_recommended_command"] == "macro_dispatch_gate_json.sh ready"
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


def test_macro_dispatch_gate_json_blocks_checked_dispatch_when_runtime_probe_is_over_budget(tmp_path: Path):
    proj = _make_project(tmp_path)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "runtime_state": {"runtime_epoch_id": "epoch-1"},
            "runtime_contract": {"digest": "runtime-contract-1"},
            "dispatch_probe_observation": {
                "status": "ok",
                "ok": True,
                "observed_at": "2026-03-22T11:00:00Z",
                "roundtrip_latency_ms": 91.4,
                "latency_status": "over_budget",
                "latency_budget_ms": 60.0,
                "ack_pid": 1234,
                "probe_id": "probe-over-budget",
            },
        },
    )

    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["dispatch_readiness"]["can_emit_minimal_payload_now"] is False
    assert payload["dispatch_readiness"]["latency_attention_required"] is True
    assert payload["dispatch_readiness"]["warm_runtime_probe_latency_status"] == "over_budget"
    assert payload["dispatch_readiness"]["warm_runtime_probe_latency_ms"] == 91.4
    assert payload["dispatch_readiness"]["warm_runtime_probe_latency_budget_ms"] == 60.0
    assert payload["dispatch_readiness"]["blockers"] == ["warm_runtime_probe_latency_attention"]
    assert payload["dispatch_readiness"]["primary_blocker_class_id"] == "runtime_latency_attention"
    assert payload["dispatch_readiness"]["blocker_details"][0]["class_id"] == "runtime_latency_attention"
    assert payload["decision"]["id"] == "inspect_runtime_latency_before_dispatch"
    assert payload["decision"]["command"] == "warm_runtime_ticket.sh"
    assert payload["repair_action"]["id"] == "inspect_runtime_latency"
    assert payload["repair_action"]["command"] == "warm_runtime_ticket.sh"
    assert payload["dispatch_contract"]["warm_runtime_ticket_command"] == "warm_runtime_ticket.sh"
    assert "latency=91.4ms" in payload["dispatch_readiness"]["blocked_message"]


def test_macro_dispatch_gate_json_requires_fresh_runtime_probe_before_checked_dispatch(tmp_path: Path):
    proj = _make_project(tmp_path)
    observed_at = (datetime.now(timezone.utc) - timedelta(seconds=120)).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "runtime_state": {"runtime_epoch_id": "epoch-1"},
            "runtime_contract": {"digest": "runtime-contract-1"},
            "dispatch_probe_observation": {
                "status": "ok",
                "ok": True,
                "observed_at": observed_at,
                "roundtrip_latency_ms": 21.7,
                "latency_status": "within_budget",
                "latency_budget_ms": 60.0,
                "ack_pid": 1234,
                "probe_id": "probe-stale",
            },
        },
    )

    res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "ready", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["dispatch_readiness"]["can_emit_minimal_payload_now"] is False
    assert payload["dispatch_readiness"]["refresh_probe_attention_required"] is True
    assert payload["dispatch_readiness"]["warm_runtime_probe_freshness_status"] == "stale"
    assert payload["dispatch_readiness"]["warm_runtime_probe_age_s"] is not None
    assert payload["dispatch_readiness"]["warm_runtime_probe_freshness_window_s"] == 45.0
    assert payload["dispatch_readiness"]["blockers"] == ["warm_runtime_probe_refresh_required"]
    assert payload["dispatch_readiness"]["primary_blocker_class_id"] == "runtime_probe_refresh"
    assert payload["dispatch_readiness"]["blocker_details"][0]["class_id"] == "runtime_probe_refresh"
    assert payload["decision"]["id"] == "refresh_runtime_probe_before_dispatch"
    assert payload["decision"]["command"] == "check_runtime_json.sh"
    assert payload["repair_action"]["id"] == "refresh_runtime_probe"
    assert payload["repair_action"]["command"] == "check_runtime_json.sh"
    assert "freshness=stale" in payload["dispatch_readiness"]["blocked_message"]
