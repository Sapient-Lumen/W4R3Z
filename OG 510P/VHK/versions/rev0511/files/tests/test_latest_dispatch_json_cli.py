from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone
import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "dispatch_receipts"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": [{"type": "TypeText", "text": "hi"}]}))
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "dispatch_receipts", "macros": {"sig": "macros/sig.yaml"}}))
    return proj


def test_latest_dispatch_json_reports_latest_receipt(tmp_path: Path):
    proj = _make_project(tmp_path)
    receipts = proj / "build" / "dispatch_receipts" / "history"
    receipts.mkdir(parents=True)
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-1-sig",
        "recorded_at": "2026-03-20T23:58:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "blocked",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": False, "blockers": ["latest_run_proof_not_clean"], "blocker_details": [{"id": "latest_run_proof_not_clean", "class_id": "desktop_state_mismatch", "class_rank": 1, "summary": "state mismatch", "reason": "inspect latest run first", "desktop_target_hint": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "summary": "Warm dispatch expects the macro's explicit when: selector to match the focused X11/i3 target."}, "live_probe_hint": {"id": "window_event_probe", "summary": "Latest matching run failed around `WaitForWindowEvent`, after `window_event` waits x2.", "step_type": "WaitForWindowEvent", "wait_kind": "window_event", "wait_count": 2, "observation": {"source_id": "wait_attempt", "kind": "window_event", "attempt": 3, "summary": "Latest matching run preserved a failed live wait observation (matched=False, workspace=2, wm=i3, event=focus).", "observed": {"matched": False, "workspace": "2", "wm": "i3", "event": "focus"}}}}], "desktop_target": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "summary": "Warm dispatch expects the macro's explicit when: selector to match the focused X11/i3 target."}, "live_probe_hint": {"id": "window_event_probe", "summary": "Latest matching run failed around `WaitForWindowEvent`, after `window_event` waits x2.", "step_type": "WaitForWindowEvent", "wait_kind": "window_event", "wait_count": 2, "observation": {"source_id": "wait_attempt", "kind": "window_event", "attempt": 3, "summary": "Latest matching run preserved a failed live wait observation (matched=False, workspace=2, wm=i3, event=focus).", "observed": {"matched": False, "workspace": "2", "wm": "i3", "event": "focus"}}}, "primary_blocker_class_id": "desktop_state_mismatch", "reason": "inspect latest run first", "decision_id": "inspect_before_dispatch", "preferred_execution_mode": "warm_runtime_dispatch"},
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    (receipts / "dispatch-1-sig.json").write_text(json.dumps(receipt), encoding="utf-8")

    res = runner.invoke(app, ["latest-dispatch-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.latest_dispatch"
    assert payload["latest_dispatch"]["macro"] == "sig"
    assert payload["latest_dispatch"]["result"] == "blocked"
    assert payload["latest_dispatch"]["route"] == "checked_dispatch"
    assert payload["latest_dispatch"]["gate"]["blockers"] == ["latest_run_proof_not_clean"]
    assert payload["latest_dispatch"]["gate"]["primary_blocker_class_id"] == "desktop_state_mismatch"
    assert payload["latest_dispatch"]["gate"]["live_probe_hint"]["id"] == "window_event_probe"
    assert payload["latest_dispatch"]["gate"]["repair_action"]["id"] == "inspect_live_desktop_target"
    assert payload["latest_dispatch"]["gate"]["repair_action"]["command"] == "macro_report_latest.sh sig"
    assert payload["latest_dispatch"]["gate"]["live_probe_hint"]["observation"]["observed"]["event"] == "focus"
    assert "inspect latest run first" in payload["latest_dispatch"]["gate"]["blocked_message"]
    assert "window_event" in payload["latest_dispatch"]["gate"]["blocked_message"]
    assert payload["latest_dispatch"]["gate"]["desktop_target"]["selector"] == {"class": "Alacritty", "workspace": "2"}
    assert payload["latest_dispatch"]["receipt_path"]["relative_to_project"] == "build/dispatch_receipts/latest.json"


def test_latest_dispatch_json_classifies_current_warm_runtime_evidence(tmp_path: Path):
    proj = _make_project(tmp_path)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': '2026-03-22T01:05:00Z',
                'roundtrip_latency_ms': 24.0,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    observed_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    gate_payload = {
        'preferred_execution_mode': 'warm_runtime_dispatch',
        'dispatch_contract': {'bus_payload_minimal': {'macro': 'sig'}},
        'dispatch_readiness': {'desktop_target': {}},
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, 'sig', bus_event='hotkey', gate_payload=gate_payload)
    observed_desktop_session_contract = summarize_desktop_session_contract()
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'dispatch-current-sig',
        'recorded_at': '2026-03-22T01:06:00Z',
        'project_root': str(proj),
        'macro': 'sig',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch',
        'checked_gate': True,
        'force_override': False,
        'payload': {'raw_json': '{"macro":"sig"}', 'valid_json': True, 'json': {'macro': 'sig'}},
        'gate': {'available': True, 'can_emit_minimal_payload_now': True, 'blockers': [], 'blocker_details': [], 'reason': 'ready', 'decision_id': 'dispatch_now', 'preferred_execution_mode': 'warm_runtime_dispatch'},
        'dispatch_receipt_contract': observed_contract,
        'desktop_session_contract': observed_desktop_session_contract,
        'dispatch_runtime_witness': observed_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    (proj / 'build' / 'dispatch_receipts' / 'history').mkdir(parents=True, exist_ok=True)
    ((proj / 'build' / 'dispatch_receipts' / 'history') / 'dispatch-current-sig.json').write_text(json.dumps(receipt), encoding='utf-8')

    res = runner.invoke(app, ['latest-dispatch-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    evidence = payload['latest_dispatch']['warm_runtime_evidence']
    assert payload['latest_dispatch']['scope_id'] == 'project_global_latest_dispatch'
    assert payload['latest_dispatch']['scope_command'] == 'latest_dispatch_json.sh'
    assert evidence['status_id'] == 'current_warm_runtime_evidence'
    assert evidence['current'] is True
    assert evidence['receipt_scope_id'] == 'project_global_latest_dispatch'
    assert evidence['receipt_scope_command'] == 'latest_dispatch_json.sh'
    assert evidence['recommended']['command'] == 'macro_dispatch_gate_json.sh sig'
    assert evidence['recommended']['source_id'] == 'latest_dispatch.dispatch_runtime_witness'
    assert evidence['recommended']['receipt_scope_id'] == 'project_global_latest_dispatch'
    assert 'dispatch_macro_checked.sh sig' in evidence['followup']


def test_latest_dispatch_json_handles_missing_receipts(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["latest-dispatch-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["latest_dispatch"] is None
    assert payload["dispatch_receipts_root"]["relative_to_project"] == "build/dispatch_receipts"


from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract
from vhk.project.desktop_session_contract import summarize_desktop_session_contract
from vhk.project.runtime_state_cache import write_runtime_state_cache, summarize_runtime_instance_witness_from_cache


def test_latest_dispatch_json_reports_stale_contract_after_macro_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    gate_payload = {
        "preferred_execution_mode": "warm_runtime_dispatch",
        "dispatch_contract": {"bus_payload_minimal": {"macro": "sig"}},
        "dispatch_readiness": {"desktop_target": {"selector_source_id": "recording_stable_selector", "selector": {"class": "Alacritty", "workspace": "2"}}},
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, "sig", bus_event="hotkey", gate_payload=gate_payload)
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-2-sig",
        "recorded_at": "2026-03-21T00:10:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "dispatch_receipt_contract": observed_contract,
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    (proj / "build" / "dispatch_receipts" / "history").mkdir(parents=True, exist_ok=True)
    ((proj / "build" / "dispatch_receipts" / "history") / "dispatch-2-sig.json").write_text(json.dumps(receipt), encoding="utf-8")
    (proj / "macros" / "sig.yaml").write_text(yaml.safe_dump({"name": "sig", "steps": [{"type": "TypeText", "text": "changed"}]}))

    res = runner.invoke(app, ["latest-dispatch-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    status = payload["latest_dispatch"]["dispatch_receipt_contract"]
    assert status["status"] == "drifted"
    assert status["macro_proof_contract_changed"] is True
    assert "macro or recorder contract changed since latest warm dispatch receipt" in status["reasons"]
    evidence = payload['latest_dispatch']['warm_runtime_evidence']
    assert evidence['status_id'] == 'refresh_dispatch_gate_after_contract_change'
    assert evidence['current'] is False
    assert evidence['recommended']['command'] == 'macro_dispatch_gate_json.sh sig'


def test_latest_dispatch_json_reports_runtime_witness_stale_after_daemon_epoch_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "pid": 4100,
            "watchers": ["hotkey"],
            "runtime_contract": {"digest": "digest-a"},
            "runtime_state": {"runtime_epoch_id": "epoch-a", "reload_count": 0},
        },
        xdg_runtime_dir=None,
    )
    observed_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-3-sig",
        "recorded_at": "2026-03-22T00:30:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "dispatch_runtime_witness": observed_witness,
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    (proj / "build" / "dispatch_receipts" / "history").mkdir(parents=True, exist_ok=True)
    ((proj / "build" / "dispatch_receipts" / "history") / "dispatch-3-sig.json").write_text(json.dumps(receipt), encoding="utf-8")
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "pid": 4200,
            "watchers": ["hotkey"],
            "runtime_contract": {"digest": "digest-a"},
            "runtime_state": {"runtime_epoch_id": "epoch-b", "reload_count": 1},
        },
        xdg_runtime_dir=None,
    )

    res = runner.invoke(app, ["latest-dispatch-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    status = payload["latest_dispatch"]["dispatch_runtime_witness"]
    assert status["status"] == "runtime_epoch_drift"
    assert status["in_sync"] is False
    assert status["epoch_changed"] is True
    assert "older resident-runtime epoch" in status["summary"]


def test_latest_dispatch_json_reports_session_stale_after_desktop_session_change(tmp_path: Path, monkeypatch):
    proj = _make_project(tmp_path)
    monkeypatch.setenv("DISPLAY", ":1")
    monkeypatch.setenv("XAUTHORITY", "/tmp/xauth-current")
    monkeypatch.setenv("I3SOCK", "/tmp/i3-current.sock")
    monkeypatch.setenv("XDG_SESSION_TYPE", "x11")
    monkeypatch.setenv("XDG_CURRENT_DESKTOP", "i3")
    observed_session = summarize_desktop_session_contract({
        "DISPLAY": ":0",
        "XAUTHORITY": "/tmp/xauth-old",
        "I3SOCK": "/tmp/i3-old.sock",
        "XDG_SESSION_TYPE": "x11",
        "XDG_CURRENT_DESKTOP": "i3",
    })
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-4-sig",
        "recorded_at": "2026-03-22T00:40:00Z",
        "project_root": str(proj),
        "macro": "sig",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"sig"}', "valid_json": True, "json": {"macro": "sig"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "desktop_session_contract": observed_session,
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    (proj / "build" / "dispatch_receipts" / "history").mkdir(parents=True, exist_ok=True)
    ((proj / "build" / "dispatch_receipts" / "history") / "dispatch-4-sig.json").write_text(json.dumps(receipt), encoding="utf-8")

    res = runner.invoke(app, ["latest-dispatch-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    status = payload["latest_dispatch"]["desktop_session_contract"]
    assert status["status"] == "drifted"
    assert status["in_sync"] is False
    assert status["display_changed"] is True
    assert status["i3sock_changed"] is True
    assert "different X11/i3 desktop session" in status["summary"]



def test_latest_dispatch_json_reports_runtime_witness_stale_after_daemon_session_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'desktop_session_contract': summarize_desktop_session_contract({
                'DISPLAY': ':0',
                'XAUTHORITY': '/tmp/xauth-old',
                'I3SOCK': '/tmp/i3-old.sock',
                'XDG_SESSION_TYPE': 'x11',
                'XDG_CURRENT_DESKTOP': 'i3',
            }),
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
        },
        xdg_runtime_dir=None,
    )
    observed_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'dispatch-5-sig',
        'recorded_at': '2026-03-22T00:50:00Z',
        'project_root': str(proj),
        'macro': 'sig',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch',
        'checked_gate': True,
        'force_override': False,
        'payload': {'raw_json': '{"macro":"sig"}', 'valid_json': True, 'json': {'macro': 'sig'}},
        'gate': {'available': True, 'can_emit_minimal_payload_now': True, 'blockers': [], 'blocker_details': [], 'reason': 'ready', 'decision_id': 'dispatch_now', 'preferred_execution_mode': 'warm_runtime_dispatch'},
        'dispatch_runtime_witness': observed_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    (proj / 'build' / 'dispatch_receipts' / 'history').mkdir(parents=True, exist_ok=True)
    ((proj / 'build' / 'dispatch_receipts' / 'history') / 'dispatch-5-sig.json').write_text(json.dumps(receipt), encoding='utf-8')
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'desktop_session_contract': summarize_desktop_session_contract({
                'DISPLAY': ':1',
                'XAUTHORITY': '/tmp/xauth-new',
                'I3SOCK': '/tmp/i3-new.sock',
                'XDG_SESSION_TYPE': 'x11',
                'XDG_CURRENT_DESKTOP': 'i3',
            }),
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
        },
        xdg_runtime_dir=None,
    )

    res = runner.invoke(app, ['latest-dispatch-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    status = payload['latest_dispatch']['dispatch_runtime_witness']
    assert status['status'] == 'runtime_desktop_session_drift'
    assert status['in_sync'] is False
    assert status['desktop_session_contract_changed'] is True
    assert status['desktop_session_contract']['display_changed'] is True
    assert status['desktop_session_contract']['i3sock_changed'] is True
    assert 'different X11/i3 desktop session' in status['summary']


def test_latest_dispatch_json_reports_runtime_witness_stale_after_probe_freshness_attention_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': (now - timedelta(seconds=120)).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
                'roundtrip_latency_ms': 24.0,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    observed_witness = {
        'available': True,
        'pid': 4100,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-a',
        'latest_dispatch_probe_status': 'ok',
        'latest_dispatch_probe_freshness_status': 'fresh',
        'latest_dispatch_probe_latency_status': 'within_budget',
    }
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'dispatch-6-sig',
        'recorded_at': '2026-03-22T01:00:00Z',
        'project_root': str(proj),
        'macro': 'sig',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch',
        'checked_gate': True,
        'force_override': False,
        'payload': {'raw_json': '{"macro":"sig"}', 'valid_json': True, 'json': {'macro': 'sig'}},
        'gate': {'available': True, 'can_emit_minimal_payload_now': True, 'blockers': [], 'blocker_details': [], 'reason': 'ready', 'decision_id': 'dispatch_now', 'preferred_execution_mode': 'warm_runtime_dispatch'},
        'dispatch_runtime_witness': observed_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    (proj / 'build' / 'dispatch_receipts' / 'history').mkdir(parents=True, exist_ok=True)
    ((proj / 'build' / 'dispatch_receipts' / 'history') / 'dispatch-6-sig.json').write_text(json.dumps(receipt), encoding='utf-8')

    res = runner.invoke(app, ['latest-dispatch-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    status = payload['latest_dispatch']['dispatch_runtime_witness']
    assert status['status'] == 'runtime_probe_freshness_drift'
    assert status['in_sync'] is False
    assert status['runtime_probe_freshness_attention_changed'] is True
    assert status['current_probe_refresh_attention'] is True
    assert 'freshness posture' in status['summary']
    evidence = payload['latest_dispatch']['warm_runtime_evidence']
    assert evidence['status_id'] == 'refresh_runtime_probe_before_reusing_receipt'
    assert evidence['current'] is False
    assert evidence['recommended']['command'] == 'warm_runtime_ticket.sh'


def test_latest_dispatch_json_reports_probe_result_variant_drift_within_failures(tmp_path: Path) -> None:
    proj = _make_project(tmp_path)
    now = datetime(2026, 3, 22, 1, 0, 0, tzinfo=timezone.utc)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'invalid_ack',
                'ok': False,
                'observed_at': now.replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
                'roundtrip_latency_ms': None,
                'latency_status': 'not_measured',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    observed_witness = {
        'available': True,
        'pid': 4100,
        'watchers': ['hotkey'],
        'runtime_epoch_id': 'epoch-a',
        'runtime_contract_digest': 'digest-a',
        'latest_dispatch_probe_status': 'ack_timeout',
        'latest_dispatch_probe_freshness_status': 'missing',
        'latest_dispatch_probe_latency_status': 'not_measured',
    }
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'dispatch-7-sig',
        'recorded_at': '2026-03-22T01:00:00Z',
        'project_root': str(proj),
        'macro': 'sig',
        'bus_event': 'hotkey',
        'result': 'blocked',
        'route': 'checked_dispatch',
        'checked_gate': True,
        'force_override': False,
        'payload': {'raw_json': '{"macro":"sig"}', 'valid_json': True, 'json': {'macro': 'sig'}},
        'gate': {'available': True, 'can_emit_minimal_payload_now': False, 'blockers': ['runtime_not_ready'], 'blocker_details': [], 'reason': 'runtime not ready', 'decision_id': 'repair_runtime_first', 'preferred_execution_mode': 'warm_runtime_dispatch'},
        'dispatch_runtime_witness': observed_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    (proj / 'build' / 'dispatch_receipts' / 'history').mkdir(parents=True, exist_ok=True)
    ((proj / 'build' / 'dispatch_receipts' / 'history') / 'dispatch-7-sig.json').write_text(json.dumps(receipt), encoding='utf-8')

    res = runner.invoke(app, ['latest-dispatch-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    status = payload['latest_dispatch']['dispatch_runtime_witness']
    assert status['status'] == 'runtime_probe_status_drift'
    assert status['in_sync'] is False
    assert status['runtime_probe_status_changed'] is True
    assert status['runtime_probe_failure_changed'] is False
    assert status['current_probe_status'] == 'invalid_ack'
    assert status['observed_probe_status'] == 'ack_timeout'
    evidence = payload['latest_dispatch']['warm_runtime_evidence']
    assert evidence['status_id'] == 'inspect_runtime_probe_result_before_reusing_receipt'
    assert evidence['current'] is False
    assert evidence['recommended']['command'] == 'warm_runtime_ticket.sh'



def test_latest_dispatch_json_classifies_current_target_authority_receipt(tmp_path: Path):
    proj = _make_project(tmp_path)
    (proj / 'macros' / 'sig.yaml').write_text(yaml.safe_dump({"name": "sig", "when": {"class": "Alacritty", "workspace": "2"}, "steps": [{"type": "TypeText", "text": "hi"}]}), encoding='utf-8')
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': '2026-03-22T01:05:00Z',
                'roundtrip_latency_ms': 24.0,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    observed_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    gate_payload = {
        'preferred_execution_mode': 'warm_runtime_dispatch',
        'dispatch_contract': {'bus_payload_minimal': {'macro': 'sig'}},
        'dispatch_readiness': {
            'desktop_target': {
                'selector_source_id': 'macro_when',
                'selector': {'class': 'Alacritty', 'workspace': '2'},
                'summary': 'Warm dispatch expects the macro selector to match the focused i3/X11 target.',
            }
        },
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, 'sig', bus_event='hotkey', gate_payload=gate_payload)
    observed_desktop_session_contract = summarize_desktop_session_contract()
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'dispatch-target-sig',
        'recorded_at': '2026-03-22T01:06:00Z',
        'project_root': str(proj),
        'macro': 'sig',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch',
        'checked_gate': True,
        'force_override': False,
        'payload': {'raw_json': '{"macro":"sig"}', 'valid_json': True, 'json': {'macro': 'sig'}},
        'gate': {
            'available': True,
            'can_emit_minimal_payload_now': True,
            'blockers': [],
            'blocker_details': [],
            'desktop_target': {
                'selector_source_id': 'macro_when',
                'selector': {'class': 'Alacritty', 'workspace': '2'},
                'summary': 'Warm dispatch expects the macro selector to match the focused i3/X11 target.',
            },
            'live_probe_hint': {
                'id': 'window_event_probe',
                'summary': 'Latest probe observed the focused target matching the macro selector.',
                'step_type': 'WaitForWindowEvent',
                'wait_kind': 'window_event',
                'wait_count': 1,
                'observation': {
                    'source_id': 'wait_attempt',
                    'summary': 'Latest matching run preserved a successful live wait observation.',
                    'observed': {'matched': True, 'workspace': '2', 'wm': 'i3', 'event': 'focus'},
                },
            },
            'target_authority': {
                'status_id': 'target_contract_match_observed',
                'proof_family': 'selector_plus_live_probe',
                'action_bias': 'gate_then_checked_dispatch',
                'selector_source_id': 'macro_when',
                'selector_field_names': ['class', 'workspace'],
                'match_verdict': 'matched',
                'summary': 'A bounded live probe observed the expected X11/i3 target contract for this macro.',
                'recommended': {'command': 'macro_dispatch_gate_json.sh sig'},
            },
            'reason': 'ready',
            'decision_id': 'dispatch_now',
            'preferred_execution_mode': 'warm_runtime_dispatch',
        },
        'dispatch_receipt_contract': observed_contract,
        'desktop_session_contract': observed_desktop_session_contract,
        'dispatch_runtime_witness': observed_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    (proj / 'build' / 'dispatch_receipts' / 'history').mkdir(parents=True, exist_ok=True)
    ((proj / 'build' / 'dispatch_receipts' / 'history') / 'dispatch-target-sig.json').write_text(json.dumps(receipt), encoding='utf-8')

    res = runner.invoke(app, ['latest-dispatch-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload['latest_dispatch']['gate']['target_authority_status_id'] == 'target_contract_match_observed'
    assert payload['latest_dispatch']['gate']['target_authority_match_verdict'] == 'matched'
    target_evidence = payload['latest_dispatch']['target_authority_evidence']
    assert target_evidence['status_id'] == 'current_target_authority_receipt'
    assert target_evidence['current'] is True
    assert target_evidence['match_verdict'] == 'matched'
    assert target_evidence['recommended']['command'] == 'macro_dispatch_gate_json.sh sig'


def test_latest_dispatch_json_classifies_current_forced_dispatch_evidence(tmp_path: Path):
    proj = _make_project(tmp_path)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': '2026-03-22T01:05:00Z',
                'roundtrip_latency_ms': 24.0,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    observed_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    gate_payload = {
        'preferred_execution_mode': 'warm_runtime_dispatch',
        'dispatch_contract': {'bus_payload_minimal': {'macro': 'sig'}},
        'dispatch_readiness': {'desktop_target': {}},
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, 'sig', bus_event='hotkey', gate_payload=gate_payload)
    observed_desktop_session_contract = summarize_desktop_session_contract()
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'dispatch-forced-sig',
        'recorded_at': '2026-03-22T01:06:00Z',
        'project_root': str(proj),
        'macro': 'sig',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch_forced',
        'checked_gate': True,
        'force_override': True,
        'payload': {'raw_json': '{\"macro\":\"sig\"}', 'valid_json': True, 'json': {'macro': 'sig'}},
        'gate': {'available': True, 'can_emit_minimal_payload_now': False, 'blockers': [], 'blocker_details': [], 'reason': 'forced emit', 'decision_id': 'dispatch_now', 'preferred_execution_mode': 'warm_runtime_dispatch'},
        'dispatch_receipt_contract': observed_contract,
        'desktop_session_contract': observed_desktop_session_contract,
        'dispatch_runtime_witness': observed_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    history_root = proj / 'build' / 'dispatch_receipts' / 'history'
    history_root.mkdir(parents=True, exist_ok=True)
    (history_root / 'dispatch-forced-sig.json').write_text(json.dumps(receipt), encoding='utf-8')

    res = runner.invoke(app, ['latest-dispatch-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    evidence = payload['latest_dispatch']['warm_runtime_evidence']
    assert payload['latest_dispatch']['force_override'] is True
    assert payload['latest_dispatch']['clean_replacement_required'] is True
    assert evidence['status_id'] == 'current_forced_dispatch_evidence'
    assert evidence['current'] is True
    assert evidence['force_override'] is True
    assert evidence['clean_replacement_required'] is True
    assert evidence['recommended']['command'] == 'latest_dispatch_json.sh'
    assert 'dispatch_macro_checked.sh sig' in evidence['followup']



def test_macro_latest_dispatch_json_marks_current_forced_receipt_as_clean_replacement_debt(tmp_path: Path):
    proj = _make_project(tmp_path)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': '2026-03-22T01:05:00Z',
                'roundtrip_latency_ms': 24.0,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    observed_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    gate_payload = {
        'preferred_execution_mode': 'warm_runtime_dispatch',
        'dispatch_contract': {'bus_payload_minimal': {'macro': 'sig'}},
        'dispatch_readiness': {'desktop_target': {}},
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, 'sig', bus_event='hotkey', gate_payload=gate_payload)
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'dispatch-forced-sig-current',
        'recorded_at': '2026-03-22T01:06:00Z',
        'project_root': str(proj),
        'macro': 'sig',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch_forced',
        'checked_gate': True,
        'force_override': True,
        'payload': {'raw_json': '{\"macro\":\"sig\"}', 'valid_json': True, 'json': {'macro': 'sig'}},
        'gate': {'available': True, 'can_emit_minimal_payload_now': False, 'blockers': [], 'blocker_details': [], 'reason': 'forced emit', 'decision_id': 'dispatch_now', 'preferred_execution_mode': 'warm_runtime_dispatch'},
        'dispatch_receipt_contract': observed_contract,
        'desktop_session_contract': summarize_desktop_session_contract(),
        'dispatch_runtime_witness': observed_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    history_root = proj / 'build' / 'dispatch_receipts' / 'history'
    history_root.mkdir(parents=True, exist_ok=True)
    (history_root / 'dispatch-forced-sig-current.json').write_text(json.dumps(receipt), encoding='utf-8')

    res = runner.invoke(app, ['macro-latest-dispatch-json', str(proj), 'sig', '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload['stage_completion']['completion_id'] == 'forced_receipt_disposition_and_clean_replacement_explicit'
    assert payload['execution_cutover']['cutover_id'] == 'inspect_forced_receipt_before_clean_replacement'
    assert payload['execution_cutover']['receipt_disposition_required'] is True
    assert payload['execution_cutover']['clean_replacement_required'] is True
    assert payload['execution_cutover'].get('signoff_ready') is False
    assert 'record_runtime_acceptance.sh sig' not in payload['execution_cutover'].get('allowed_after_receipt_disposition', [])
    assert 'still current resident evidence' in payload['next_step']['summary']
