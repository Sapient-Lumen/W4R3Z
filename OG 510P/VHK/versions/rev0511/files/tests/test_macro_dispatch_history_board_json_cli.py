from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "dispatch_history"
    (proj / "macros").mkdir(parents=True)
    (proj / "build" / "dispatch_receipts" / "history").mkdir(parents=True)

    for name in ["steady", "blocked", "forced", "stale", "none"]:
        (proj / "macros" / f"{name}.yaml").write_text(
            yaml.safe_dump({"name": name, "steps": [{"type": "TypeText", "text": name}]})
        )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "dispatch_history",
                "macros": {
                    "steady": "macros/steady.yaml",
                    "blocked": "macros/blocked.yaml",
                    "forced": "macros/forced.yaml",
                    "stale": "macros/stale.yaml",
                    "none": "macros/none.yaml",
                },
            }
        )
    )
    return proj


def _write_receipt(project: Path, receipt_id: str, *, macro: str, recorded_at: datetime, result: str, force_override: bool = False, route: str = "checked_dispatch") -> None:
    from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract
    gate_payload = {"preferred_execution_mode": "warm_runtime_dispatch", "dispatch_contract": {"bus_payload_minimal": {"macro": macro}}, "dispatch_readiness": {"desktop_target": {}}}
    payload = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": receipt_id,
        "recorded_at": recorded_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": str(project),
        "macro": macro,
        "bus_event": "hotkey",
        "result": result,
        "route": route,
        "checked_gate": True,
        "force_override": force_override,
        "payload": {"raw_json": json.dumps({"macro": macro}), "valid_json": True, "json": {"macro": macro}},
        "gate": {"available": True, "decision_id": "dispatch_now" if result == "emitted" else "inspect_before_dispatch", "blockers": ["latest_run_proof_not_clean"] if result == "blocked" else [], "blocker_details": [{"id": "latest_run_proof_not_clean", "class_id": "desktop_state_mismatch", "class_rank": 1, "summary": "state mismatch", "reason": "inspect latest run first", "desktop_target_hint": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "summary": "Warm dispatch expects the macro's explicit when: selector to match the focused X11/i3 target."}}] if result == "blocked" else [], "desktop_target": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "summary": "Warm dispatch expects the macro's explicit when: selector to match the focused X11/i3 target."} if result == "blocked" else None},
        "dispatch_receipt_contract": summarize_dispatch_receipt_contract(project, macro, bus_event="hotkey", gate_payload=gate_payload),
    }
    path = project / "build" / "dispatch_receipts" / "history" / f"{receipt_id}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")



def test_macro_dispatch_history_board_json_reports_attention_and_clean_history(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)

    _write_receipt(proj, "r1-steady", macro="steady", recorded_at=now - timedelta(hours=2), result="emitted")
    _write_receipt(proj, "r2-blocked-new", macro="blocked", recorded_at=now - timedelta(hours=1), result="blocked")
    _write_receipt(proj, "r3-blocked-old", macro="blocked", recorded_at=now - timedelta(hours=4), result="blocked")
    _write_receipt(proj, "r4-forced", macro="forced", recorded_at=now - timedelta(hours=3), result="emitted", force_override=True, route="checked_dispatch_forced")
    _write_receipt(proj, "r5-stale", macro="stale", recorded_at=now - timedelta(days=5), result="emitted")

    res = runner.invoke(app, ["macro-dispatch-history-board-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["stack_kind"] == "vhk.project.macro_dispatch_history_board"
    assert payload["project"]["macro_count"] == 5
    assert payload["summary"]["attention_macro_count"] == 2
    assert payload["summary"]["unresolved_force_override_macro_count"] == 1
    assert payload["summary"]["counts_by_posture_id"]["blocked_repeated_recently"] == 1
    assert payload["summary"]["counts_by_posture_id"]["forced_override_pending_review"] == 1
    assert payload["summary"]["counts_by_posture_id"]["clean_recent_dispatch"] == 1
    assert payload["summary"]["counts_by_posture_id"]["dispatch_history_stale"] == 1
    assert payload["summary"]["counts_by_posture_id"]["no_dispatch_history"] == 1
    assert payload["summary"]["counts_by_primary_blocker_class_id"]["desktop_state_mismatch"] == 1

    assert [item["name"] for item in payload["macros"]][:2] == ["blocked", "forced"]

    blocked = next(item for item in payload["macros"] if item["name"] == "blocked")
    assert blocked["dispatch_history_posture"]["id"] == "blocked_repeated_recently"
    assert blocked["dispatch_history_posture"]["attention_id"] == "repeated_desktop_state_mismatch"
    assert blocked["dispatch_history"]["blocked_streak"] == 2
    assert blocked["dispatch_history"]["blocked_recent_count"] == 2
    assert blocked["dispatch_history"]["primary_blocked_class_id"] == "desktop_state_mismatch"
    assert blocked["dispatch_history"]["latest_blocked_receipt"]["gate"]["desktop_target"]["selector"] == {"class": "Alacritty", "workspace": "2"}
    assert blocked["llm_workbench"]["source_id"] == "macro_dispatch_history_board.llm_workbench"
    assert blocked["llm_workbench"]["source_command"] == "macro_dispatch_history_board_json.sh"
    assert blocked["llm_workbench"]["recommended_command"] == "macro_latest_dispatch_json.sh blocked"
    assert blocked["llm_workbench"]["edit_loop"]["dispatch_history_board"] == "macro_dispatch_history_board_json.sh"

    forced = next(item for item in payload["macros"] if item["name"] == "forced")
    assert forced["dispatch_history_posture"]["id"] == "forced_override_pending_review"
    assert forced["dispatch_history"]["unresolved_force_override"] is True
    assert forced["dispatch_history"]["latest_force_override"]["route"] == "checked_dispatch_forced"

    steady = next(item for item in payload["macros"] if item["name"] == "steady")
    assert steady["dispatch_history_posture"]["id"] == "clean_recent_dispatch"
    assert steady["dispatch_history"]["emitted_recent_count"] == 1

    stale = next(item for item in payload["macros"] if item["name"] == "stale")
    assert stale["dispatch_history_posture"]["id"] == "dispatch_history_stale"

    none = next(item for item in payload["macros"] if item["name"] == "none")
    assert none["dispatch_history_posture"]["id"] == "no_dispatch_history"
    assert none["dispatch_history"]["receipt_count"] == 0
    assert none["llm_workbench"]["mode_id"] == "produce_first_dispatch_receipt"
    assert none["llm_workbench"]["recommended_command"] == "macro_author_loop_json.sh none"

    assert payload["primary_macro_llm_workbench"]["source_id"] == "macro_dispatch_history_board.llm_workbench"
    assert payload["summary"]["primary_llm_workbench_command"] == "macro_latest_dispatch_json.sh blocked"


from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract
from vhk.project.desktop_session_contract import summarize_desktop_session_contract
from vhk.project.runtime_state_cache import write_runtime_state_cache, summarize_runtime_instance_witness_from_cache


def test_macro_dispatch_history_board_json_marks_receipt_stale_after_macro_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
    gate_payload = {
        "preferred_execution_mode": "warm_runtime_dispatch",
        "dispatch_contract": {"bus_payload_minimal": {"macro": "steady"}},
        "dispatch_readiness": {"desktop_target": {"selector_source_id": "recording_stable_selector", "selector": {"class": "Alacritty", "workspace": "2"}}},
    }
    contract = summarize_dispatch_receipt_contract(proj, "steady", bus_event="hotkey", gate_payload=gate_payload)
    payload = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "r-contract-steady",
        "recorded_at": (now - timedelta(hours=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": str(proj),
        "macro": "steady",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": json.dumps({"macro": "steady"}), "valid_json": True, "json": {"macro": "steady"}},
        "gate": {"available": True, "decision_id": "dispatch_now", "blockers": [], "blocker_details": []},
        "dispatch_receipt_contract": contract,
    }
    (proj / "build" / "dispatch_receipts" / "history" / "r-contract-steady.json").write_text(json.dumps(payload), encoding="utf-8")
    (proj / "macros" / "steady.yaml").write_text(yaml.safe_dump({"name": "steady", "steps": [{"type": "TypeText", "text": "steady changed"}]}))

    res = runner.invoke(app, ["macro-dispatch-history-board-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    steady = next(item for item in payload["macros"] if item["name"] == "steady")
    assert steady["dispatch_history_posture"]["id"] == "dispatch_receipt_contract_stale"
    assert steady["dispatch_history"]["latest_receipt_contract_status"]["status"] == "drifted"
    assert steady["dispatch_history"]["latest_receipt_contract_status"]["macro_proof_contract_changed"] is True


def test_macro_dispatch_history_board_json_marks_receipt_stale_after_runtime_epoch_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
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
    contract = summarize_dispatch_receipt_contract(proj, "steady", bus_event="hotkey", gate_payload={"preferred_execution_mode": "warm_runtime_dispatch", "dispatch_contract": {"bus_payload_minimal": {"macro": "steady"}}, "dispatch_readiness": {"desktop_target": {}}})
    payload = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "r-runtime-steady",
        "recorded_at": (now - timedelta(hours=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": str(proj),
        "macro": "steady",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": json.dumps({"macro": "steady"}), "valid_json": True, "json": {"macro": "steady"}},
        "gate": {"available": True, "decision_id": "dispatch_now", "blockers": [], "blocker_details": []},
        "dispatch_receipt_contract": contract,
        "dispatch_runtime_witness": runtime_witness,
    }
    (proj / "build" / "dispatch_receipts" / "history" / "r-runtime-steady.json").write_text(json.dumps(payload), encoding="utf-8")
    write_runtime_state_cache(
        project_root=proj,
        payload={
            "pid": 5200,
            "watchers": ["hotkey"],
            "runtime_contract": {"digest": "digest-a"},
            "runtime_state": {"runtime_epoch_id": "epoch-b", "reload_count": 1},
        },
        xdg_runtime_dir=None,
    )

    res = runner.invoke(app, ["macro-dispatch-history-board-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    steady = next(item for item in payload["macros"] if item["name"] == "steady")
    assert steady["dispatch_history_posture"]["id"] == "dispatch_receipt_runtime_stale"
    status = steady["dispatch_history"]["latest_receipt_runtime_witness_status"]
    assert status["status"] == "runtime_epoch_drift"
    assert status["epoch_changed"] is True


def test_macro_dispatch_history_board_json_marks_receipt_stale_after_desktop_session_change(tmp_path: Path, monkeypatch):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
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
    contract = summarize_dispatch_receipt_contract(proj, "steady", bus_event="hotkey", gate_payload={"preferred_execution_mode": "warm_runtime_dispatch", "dispatch_contract": {"bus_payload_minimal": {"macro": "steady"}}, "dispatch_readiness": {"desktop_target": {}}})
    payload = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "r-session-steady",
        "recorded_at": (now - timedelta(hours=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "project_root": str(proj),
        "macro": "steady",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": json.dumps({"macro": "steady"}), "valid_json": True, "json": {"macro": "steady"}},
        "gate": {"available": True, "decision_id": "dispatch_now", "blockers": [], "blocker_details": []},
        "dispatch_receipt_contract": contract,
        "desktop_session_contract": observed_session,
    }
    (proj / "build" / "dispatch_receipts" / "history" / "r-session-steady.json").write_text(json.dumps(payload), encoding="utf-8")

    res = runner.invoke(app, ["macro-dispatch-history-board-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    steady = next(item for item in payload["macros"] if item["name"] == "steady")
    assert steady["dispatch_history_posture"]["id"] == "dispatch_receipt_session_stale"
    status = steady["dispatch_history"]["latest_receipt_desktop_session_status"]
    assert status["status"] == "drifted"
    assert status["display_changed"] is True
    assert status["i3sock_changed"] is True


def test_macro_dispatch_history_board_json_marks_receipt_stale_after_runtime_probe_latency_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 5100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': now.replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
                'roundtrip_latency_ms': 91.4,
                'latency_status': 'over_budget',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    payload = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'r-runtime-latency-steady',
        'recorded_at': (now - timedelta(hours=1)).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'project_root': str(proj),
        'macro': 'steady',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch',
        'checked_gate': True,
        'force_override': False,
        'payload': {'raw_json': json.dumps({'macro': 'steady'}), 'valid_json': True, 'json': {'macro': 'steady'}},
        'gate': {'available': True, 'decision_id': 'dispatch_now', 'blockers': [], 'blocker_details': []},
        'dispatch_receipt_contract': summarize_dispatch_receipt_contract(proj, 'steady', bus_event='hotkey', gate_payload={'preferred_execution_mode': 'warm_runtime_dispatch', 'dispatch_contract': {'bus_payload_minimal': {'macro': 'steady'}}, 'dispatch_readiness': {'desktop_target': {}}}),
        'dispatch_runtime_witness': {
            'available': True,
            'pid': 5100,
            'watchers': ['hotkey'],
            'runtime_epoch_id': 'epoch-a',
            'runtime_contract_digest': 'digest-a',
            'latest_dispatch_probe_status': 'ok',
            'latest_dispatch_probe_freshness_status': 'fresh',
            'latest_dispatch_probe_latency_status': 'within_budget',
        },
    }
    (proj / 'build' / 'dispatch_receipts' / 'history' / 'r-runtime-latency-steady.json').write_text(json.dumps(payload), encoding='utf-8')

    res = runner.invoke(app, ['macro-dispatch-history-board-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    steady = next(item for item in payload['macros'] if item['name'] == 'steady')
    assert steady['dispatch_history_posture']['id'] == 'dispatch_receipt_runtime_latency_stale'
    assert steady['dispatch_history_posture']['attention_id'] == 'refresh_dispatch_after_runtime_latency_change'
    status = steady['dispatch_history']['latest_receipt_runtime_witness_status']
    assert status['status'] == 'runtime_probe_latency_drift'
    assert status['runtime_probe_latency_attention_changed'] is True


def test_macro_dispatch_history_board_marks_probe_result_variant_drift_within_failures(tmp_path: Path) -> None:
    proj = _make_project(tmp_path)
    now = datetime(2026, 3, 22, 12, 0, tzinfo=timezone.utc)
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 5100,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': 'digest-a'},
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'invalid_ack',
                'ok': False,
                'observed_at': now.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'latency_status': 'not_measured',
                'latency_budget_ms': 60.0,
            },
        },
        xdg_runtime_dir=None,
    )
    payload = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'r-runtime-status-steady',
        'recorded_at': (now - timedelta(hours=1)).astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'project_root': str(proj),
        'macro': 'steady',
        'bus_event': 'hotkey',
        'result': 'blocked',
        'route': 'checked_dispatch',
        'checked_gate': True,
        'force_override': False,
        'payload': {'raw_json': json.dumps({'macro': 'steady'}), 'valid_json': True, 'json': {'macro': 'steady'}},
        'gate': {'available': True, 'decision_id': 'repair_runtime_first', 'blockers': ['runtime_not_ready'], 'blocker_details': []},
        'dispatch_receipt_contract': summarize_dispatch_receipt_contract(proj, 'steady', bus_event='hotkey', gate_payload={'preferred_execution_mode': 'warm_runtime_dispatch', 'dispatch_contract': {'bus_payload_minimal': {'macro': 'steady'}}, 'dispatch_readiness': {'desktop_target': {}}}),
        'dispatch_runtime_witness': {
            'available': True,
            'pid': 5100,
            'watchers': ['hotkey'],
            'runtime_epoch_id': 'epoch-a',
            'runtime_contract_digest': 'digest-a',
            'latest_dispatch_probe_status': 'ack_timeout',
            'latest_dispatch_probe_freshness_status': 'missing',
            'latest_dispatch_probe_latency_status': 'not_measured',
        },
    }
    history_dir = proj / 'build' / 'dispatch_receipts' / 'history'
    history_dir.mkdir(parents=True, exist_ok=True)
    (history_dir / 'r-runtime-status-steady.json').write_text(json.dumps(payload), encoding='utf-8')

    res = runner.invoke(app, ['macro-dispatch-history-board-json', str(proj), '--no-pretty'])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    steady = next(item for item in payload['macros'] if item['name'] == 'steady')
    assert steady['dispatch_history_posture']['id'] == 'dispatch_receipt_runtime_probe_status_stale'
    assert steady['dispatch_history_posture']['attention_id'] == 'refresh_dispatch_after_runtime_probe_result_change'
    status = steady['dispatch_history']['latest_receipt_runtime_witness_status']
    assert status['status'] == 'runtime_probe_status_drift'
    assert status['runtime_probe_status_changed'] is True
    assert status['runtime_probe_failure_changed'] is False



def test_macro_dispatch_history_board_json_separates_project_global_and_primary_macro_receipt_lanes(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)

    _write_receipt(proj, "r-blocked-new", macro="blocked", recorded_at=now - timedelta(hours=2), result="blocked")
    _write_receipt(proj, "r-blocked-old", macro="blocked", recorded_at=now - timedelta(hours=5), result="blocked")
    _write_receipt(proj, "r-steady-newest", macro="steady", recorded_at=now - timedelta(minutes=30), result="emitted")

    res = runner.invoke(app, ["macro-dispatch-history-board-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["summary"]["primary_macro_name"] == "blocked"
    assert payload["summary"]["project_latest_dispatch_macro_name"] == "steady"
    assert payload["summary"]["project_latest_dispatch_result"] == "emitted"
    assert payload["summary"]["project_latest_dispatch_matches_primary_macro"] is False
    assert payload["receipt_surfaces"]["project_latest_dispatch"]["command"] == "latest_dispatch_json.sh"
    assert payload["receipt_surfaces"]["project_latest_dispatch"]["receipt_macro"] == "steady"
    assert payload["receipt_surfaces"]["primary_macro_latest_dispatch"]["macro_name"] == "blocked"
    assert payload["receipt_surfaces"]["primary_macro_latest_dispatch"]["command"] == "macro_latest_dispatch_json.sh blocked"
    assert payload["receipt_surfaces"]["primary_macro_latest_dispatch"]["matches_project_latest_dispatch"] is False
    assert payload["receipt_surfaces"]["macro_latest_dispatch_template"]["command"] == "macro_latest_dispatch_json.sh <macro>"

    blocked = next(item for item in payload["macros"] if item["name"] == "blocked")
    assert blocked["dispatch_history_posture"]["command"] == "macro_dispatch_gate_json.sh blocked"
    assert blocked["dispatch_history_posture"]["command_scope_id"] == "dispatch_gate"
    assert blocked["preferred_entrypoints"]["project_latest_dispatch"] == "latest_dispatch_json.sh"
    assert blocked["preferred_entrypoints"]["macro_latest_dispatch"] == "macro_latest_dispatch_json.sh blocked"
    assert blocked["receipt_observability"]["macro_latest_dispatch"]["command"] == "macro_latest_dispatch_json.sh blocked"

    steady = next(item for item in payload["macros"] if item["name"] == "steady")
    assert steady["dispatch_history_posture"]["command"] == "macro_latest_dispatch_json.sh steady"
    assert steady["dispatch_history_posture"]["command_scope_id"] == "macro_latest_dispatch"
    assert steady["dispatch_history"]["latest_receipt_warm_runtime_evidence"]["followup"][-1] == "macro_latest_dispatch_json.sh steady"

    none = next(item for item in payload["macros"] if item["name"] == "none")
    assert none["dispatch_history_posture"]["command"] == "macro_dispatch_gate_json.sh none"
    assert none["dispatch_history_posture"]["command_scope_id"] == "dispatch_gate"
