from __future__ import annotations

from pathlib import Path
import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "macro_latest_dispatch"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": [{"type": "TypeText", "text": "sig"}]}))
    (proj / "macros" / "other.yaml").write_text(yaml.safe_dump({"name": "other", "steps": [{"type": "TypeText", "text": "other"}]}))
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "macro_latest_dispatch",
                "settings": {"event_log": False},
                "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
                "macros": {"sig": "macros/sig.yaml", "other": "macros/other.yaml"},
            }
        )
    )
    return proj


def test_macro_latest_dispatch_json_prefers_matching_macro_receipt_over_newer_other_macro(tmp_path: Path):
    proj = _make_project(tmp_path)
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)

    sig_receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-sig-1",
        "recorded_at": "2026-03-22T15:00:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "blocked",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": False, "blockers": ["latest_run_proof_not_clean"], "blocker_details": [], "reason": "inspect latest run first", "decision_id": "inspect_before_dispatch", "preferred_execution_mode": "warm_runtime_dispatch"},
    }
    other_receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-other-2",
        "recorded_at": "2026-03-22T15:10:00Z",
        "project_root": str(proj),
        "macro": "other",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"other"}', "valid_json": True, "json": {"macro": "other"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
    }

    (history_root / "dispatch-sig-1.json").write_text(json.dumps(sig_receipt), encoding="utf-8")
    (history_root / "dispatch-other-2.json").write_text(json.dumps(other_receipt), encoding="utf-8")
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(other_receipt), encoding="utf-8")

    res = runner.invoke(app, ["macro-latest-dispatch-json", str(proj), "sig", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_latest_dispatch"
    assert payload["macro"]["name"] == "sig"
    assert payload["latest_dispatch"]["macro"] == "sig"
    assert payload["latest_dispatch"]["receipt_id"] == "dispatch-sig-1"
    assert payload["latest_dispatch"]["result"] == "blocked"
    assert payload["latest_dispatch"]["receipt_path"]["relative_to_project"] == "build/dispatch_receipts/history/dispatch-sig-1.json"
    assert payload["preferred_entrypoints"]["macro_latest_dispatch_json"] == "macro_latest_dispatch_json.sh sig"
    assert payload["preferred_entrypoints"]["latest_dispatch_json"] == "latest_dispatch_json.sh"
    assert payload["non_claims"][1].startswith("It intentionally ignores newer receipts for other macros")


def test_macro_latest_dispatch_json_rejects_unknown_macro(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-latest-dispatch-json", str(proj), "missing", "--no-pretty"])
    assert res.exit_code == 2
    assert "Unknown macro" in res.output



def test_macro_latest_dispatch_json_keeps_macro_scoped_followup_when_current(tmp_path: Path):
    from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract
    from vhk.project.desktop_session_contract import summarize_desktop_session_contract
    from vhk.project.runtime_state_cache import write_runtime_state_cache, summarize_runtime_instance_witness_from_cache

    proj = _make_project(tmp_path)
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "pid": 5100,
            "watchers": ["hotkey"],
            "runtime_contract": {"digest": "digest-a"},
            "runtime_state": {"runtime_epoch_id": "epoch-a", "reload_count": 0},
        },
        xdg_runtime_dir=None,
    )
    runtime_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    contract = summarize_dispatch_receipt_contract(
        proj,
        "sig",
        bus_event="hotkey",
        gate_payload={"preferred_execution_mode": "warm_runtime_dispatch", "dispatch_contract": {"bus_payload_minimal": {"macro": "sig"}}, "dispatch_readiness": {"desktop_target": {}}},
    )
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-sig-current",
        "recorded_at": "2026-03-22T15:00:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "dispatch_receipt_contract": contract,
        "desktop_session_contract": summarize_desktop_session_contract(),
        "dispatch_runtime_witness": runtime_witness,
    }
    (history_root / "dispatch-sig-current.json").write_text(json.dumps(receipt), encoding="utf-8")

    res = runner.invoke(app, ["macro-latest-dispatch-json", str(proj), "sig", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    evidence = payload["latest_dispatch"]["warm_runtime_evidence"]
    assert payload["latest_dispatch"]["scope_id"] == "selected_macro_latest_dispatch"
    assert payload["latest_dispatch"]["scope_command"] == "macro_latest_dispatch_json.sh sig"
    assert evidence["status_id"] == "current_warm_runtime_evidence"
    assert evidence["receipt_scope_id"] == "selected_macro_latest_dispatch"
    assert evidence["receipt_scope_command"] == "macro_latest_dispatch_json.sh sig"
    assert evidence["recommended"]["source_id"] == "macro_latest_dispatch.dispatch_runtime_witness"
    assert evidence["recommended"]["receipt_scope_id"] == "selected_macro_latest_dispatch"
    assert evidence["followup"][-1] == "macro_latest_dispatch_json.sh sig"
    assert "latest_dispatch_json.sh" not in evidence["followup"]
    assert payload["next_step"]["followup"][-1] == "macro_latest_dispatch_json.sh sig"
    assert payload["stage_completion"]["completion_id"] == "receipt_disposition_explicit"
    assert payload["stage_completion"]["completion_command"] == "macro_dispatch_gate_json.sh sig"
    assert payload["execution_cutover"]["cutover_id"] == "inspect_current_receipt_before_reemit"
    assert payload["execution_cutover"]["recommended_command"] == "macro_latest_dispatch_json.sh sig"
    assert payload["execution_cutover"]["receipt_disposition_required"] is True
    assert payload["execution_cutover"]["redundant_resident_dispatch_risk"] is True



def test_macro_latest_dispatch_json_keeps_macro_scoped_followup_when_currentness_is_unknown(tmp_path: Path):
    proj = _make_project(tmp_path)
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-sig-unknown",
        "recorded_at": "2026-03-22T15:00:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "blocked",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": False, "blockers": ["latest_run_proof_not_clean"], "blocker_details": [], "reason": "inspect latest run first", "decision_id": "inspect_before_dispatch", "preferred_execution_mode": "warm_runtime_dispatch"},
    }
    (history_root / "dispatch-sig-unknown.json").write_text(json.dumps(receipt), encoding="utf-8")

    res = runner.invoke(app, ["macro-latest-dispatch-json", str(proj), "sig", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    evidence = payload["latest_dispatch"]["warm_runtime_evidence"]
    assert evidence["status_id"] == "refresh_dispatch_gate_after_contract_change"
    assert evidence["followup"][-1] == "macro_latest_dispatch_json.sh sig"
    assert payload["next_step"]["followup"][-1] == "macro_latest_dispatch_json.sh sig"


def test_macro_latest_dispatch_json_marks_stale_contract_receipt_as_stale_cutover(tmp_path: Path):
    from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract

    proj = _make_project(tmp_path)
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    contract = summarize_dispatch_receipt_contract(
        proj,
        "sig",
        bus_event="hotkey",
        gate_payload={"preferred_execution_mode": "warm_runtime_dispatch", "dispatch_contract": {"bus_payload_minimal": {"macro": "sig"}}, "dispatch_readiness": {"desktop_target": {}}},
    )
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-sig-stale-contract",
        "recorded_at": "2026-03-22T15:00:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "dispatch_receipt_contract": contract,
    }
    (history_root / "dispatch-sig-stale-contract.json").write_text(json.dumps(receipt), encoding="utf-8")
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": [{"type": "TypeText", "text": "sig changed"}]}), encoding="utf-8")

    res = runner.invoke(app, ["macro-latest-dispatch-json", str(proj), "sig", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    evidence = payload["latest_dispatch"]["warm_runtime_evidence"]
    assert evidence["status_id"] == "refresh_dispatch_gate_after_contract_change"
    assert evidence["current"] is False
    assert payload["stage_completion"]["completion_id"] == "stale_receipt_disposition_explicit"
    assert payload["execution_cutover"]["cutover_id"] == "inspect_stale_receipt_before_runtime_reuse"
    assert payload["execution_cutover"]["recommended_command"] == "macro_latest_dispatch_json.sh sig"
    assert payload["execution_cutover"]["receipt_disposition_required"] is True
    assert payload["execution_cutover"]["redundant_resident_dispatch_risk"] is True
