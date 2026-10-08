from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.macro_proof_contract import summarize_macro_proof_contract
from vhk.project.runtime_state_cache import write_runtime_state_cache


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)
    (proj / "logs").mkdir(parents=True)
    (proj / "build" / "dispatch_receipts" / "history").mkdir(parents=True)

    (proj / "macros" / "ready.yaml").write_text(
        yaml.safe_dump({"name": "ready", "steps": [{"type": "TypeText", "text": "ready"}]})
    )
    (proj / "macros" / "candidate.yaml").write_text(
        yaml.safe_dump({"name": "candidate", "steps": [{"type": "TypeText", "text": "candidate"}]})
    )
    (proj / "macros" / "prompty.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "prompty",
                "steps": [
                    {"type": "PromptForm", "fields": [{"name": "name", "label": "Name"}]},
                    {"type": "TypeText", "text": "hi"},
                ],
            }
        )
    )
    (proj / "macros" / "stale.yaml").write_text(
        yaml.safe_dump({"name": "stale", "steps": [{"type": "TypeText", "text": "stale"}]})
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": True, "log_dir": "logs"},
                "macros": {
                    "ready": "macros/ready.yaml",
                    "candidate": "macros/candidate.yaml",
                    "prompty": "macros/prompty.yaml",
                    "stale": "macros/stale.yaml",
                },
            }
        )
    )

    sidecar_payload = {"segments": [{"selector_kind": "stable", "transition_reason": "focus", "anchor": {"mode": "window"}}]}
    for name, ts in [("ready", 3000), ("candidate", 3000), ("prompty", 3000)]:
        sidecar = proj / "macros" / f"{name}.window-context.yaml"
        sidecar.write_text(yaml.safe_dump(sidecar_payload, sort_keys=False))
        os.utime(sidecar, (ts, ts))
        os.utime(proj / "macros" / f"{name}.yaml", (ts, ts))
    os.utime(proj / "macros" / "stale.yaml", (3000, 3000))

    with (proj / "logs" / "run_ready.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "run_start", "macro": "ready", "run_id": "run-ready", "ts": 1.0, "macro_proof_contract": summarize_macro_proof_contract(proj, "ready")}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "ready", "run_id": "run-ready", "ts": 2.0, "ok": True}) + "\n")

    return proj


def _write_receipt(project: Path, receipt_id: str, *, macro: str, recorded_at: datetime, result: str, route: str = "checked_dispatch") -> None:
    from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract

    gate_payload = {
        "preferred_execution_mode": "warm_runtime_dispatch",
        "dispatch_contract": {"bus_payload_minimal": {"macro": macro}},
        "dispatch_readiness": {"desktop_target": {}},
    }
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
        "force_override": False,
        "payload": {"raw_json": json.dumps({"macro": macro}), "valid_json": True, "json": {"macro": macro}},
        "gate": {"available": True, "decision_id": "dispatch_now" if result == "emitted" else "inspect_before_dispatch", "blockers": []},
        "dispatch_receipt_contract": summarize_dispatch_receipt_contract(project, macro, bus_event="hotkey", gate_payload=gate_payload),
    }
    path = project / "build" / "dispatch_receipts" / "history" / f"{receipt_id}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_macro_runtime_board_json_reports_execution_posture(tmp_path: Path):
    proj = _make_project(tmp_path)

    res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["stack_kind"] == "vhk.project.macro_runtime_board"
    assert payload["project"]["macro_count"] == 4
    assert payload["project"]["resident_runtime_macro_count"] == 2
    assert payload["summary"]["primary_macro_name"] == "ready"
    assert payload["summary"]["primary_posture_id"] == "warm_dispatch_ready"
    assert payload["summary"]["counts_by_posture_id"]["warm_dispatch_ready"] == 1
    assert payload["summary"]["counts_by_posture_id"]["warm_dispatch_candidate"] == 1
    assert payload["summary"]["counts_by_posture_id"]["direct_run_only"] == 1
    assert payload["summary"]["counts_by_posture_id"]["stabilize_first"] == 1

    assert [item["name"] for item in payload["macros"]] == ["ready", "candidate", "prompty", "stale"]

    ready = payload["macros"][0]
    assert ready["runtime_posture"]["id"] == "warm_dispatch_ready"
    assert ready["runtime_posture"]["dispatch_safe_now"] is True
    assert ready["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert ready["preferred_entrypoints"]["warm_runtime"] == "dispatch_macro.sh ready"
    assert ready["preferred_entrypoints"]["warm_runtime_checked"] == "dispatch_macro_checked.sh ready"
    assert ready["preferred_entrypoints"]["warm_runtime_gate"] == "macro_dispatch_gate_json.sh ready"

    candidate = payload["macros"][1]
    assert candidate["runtime_posture"]["id"] == "warm_dispatch_candidate"
    assert candidate["recording"]["freshness_status"] == "aligned"
    assert candidate["latest_run_context"]["scope"] == "none"
    assert candidate["latest_run_context"]["replay_posture_id"] == "unverified"

    prompty = payload["macros"][2]
    assert prompty["runtime_posture"]["id"] == "direct_run_only"
    assert prompty["preferred_execution_mode"] == "direct_run"
    assert prompty["preferred_entrypoints"]["direct_run"] == "run_macro.sh prompty"

    stale = payload["macros"][3]
    assert stale["runtime_posture"]["id"] == "stabilize_first"
    assert stale["runtime_posture"]["command"] == "record_macro.sh stale 5000"


def test_macro_runtime_board_json_projects_primary_llm_workbench_from_author_loop(tmp_path: Path):
    proj = _make_project(tmp_path)

    res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    workbench = payload["primary_macro_llm_workbench"]
    assert workbench["macro_name"] == "ready"
    assert workbench["source_id"] == "macro_author_loop.llm_workbench"
    assert workbench["source_command"] == "macro_author_loop_json.sh ready"
    assert workbench["mode_id"] == "execute_on_resident_runtime"
    assert workbench["recommended_command"] == "dispatch_macro_checked.sh ready"
    assert payload["summary"]["primary_llm_workbench_source_id"] == "macro_author_loop.llm_workbench"
    assert payload["summary"]["primary_llm_workbench_mode_id"] == "execute_on_resident_runtime"
    assert payload["summary"]["primary_llm_workbench_command"] == "dispatch_macro_checked.sh ready"
    assert payload["summary"]["primary_llm_workbench_surface"] == "macro_author_loop_json.sh ready"

    ready = next(item for item in payload["macros"] if item["name"] == "ready")
    assert ready["llm_workbench"]["source_id"] == "macro_author_loop.llm_workbench"
    assert ready["llm_workbench"]["source_command"] == "macro_author_loop_json.sh ready"


def test_macro_runtime_board_json_stales_signoff_when_runtime_probe_latency_goes_over_budget(tmp_path: Path):
    proj = _make_project(tmp_path)

    initial = runner.invoke(app, ['macro-runtime-board-json', str(proj)])
    assert initial.exit_code == 0, initial.output
    initial_payload = json.loads(initial.stdout)
    ready = next(item for item in initial_payload['macros'] if item['name'] == 'ready')
    current_contract = dict((ready.get('acceptance') or {}).get('current_runtime_acceptance_contract') or {})
    assert current_contract.get('digest')

    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4444,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': current_contract.get('resident_runtime_contract_digest') or 'contract-a'},
            'runtime_state': {'runtime_epoch_id': current_contract.get('resident_runtime_epoch_id') or 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': (datetime.now(timezone.utc) - timedelta(seconds=5)).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
                'roundtrip_latency_ms': 91.4,
                'latency_status': 'over_budget',
                'latency_budget_ms': 60.0,
                'ack_pid': 4444,
                'ack_handled_at': (datetime.now(timezone.utc) - timedelta(seconds=5)).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
                'probe_id': 'probe-123',
            },
        },
        xdg_runtime_dir=None,
    )
    (proj / 'review').mkdir(parents=True, exist_ok=True)
    (proj / 'review' / 'macro_acceptance.yaml').write_text(
        yaml.safe_dump({
            'macros': {
                'ready': {
                    'runtime_acceptance': {
                        'posture_id': 'warm_dispatch_ready',
                        'accepted_by': 'operator',
                        'accepted_at': '2026-03-22T10:50:00Z',
                        'note': 'accepted before latency regression',
                        'proof_contract': current_contract,
                    }
                }
            }
        }, sort_keys=False)
    )

    res = runner.invoke(app, ['macro-runtime-board-json', str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    ready = next(item for item in payload['macros'] if item['name'] == 'ready')
    runtime_signoff = dict((ready.get('acceptance') or {}).get('runtime_signoff') or {})
    current_contract = dict((ready.get('acceptance') or {}).get('current_runtime_acceptance_contract') or {})

    assert runtime_signoff['status'] == 'stale'
    assert runtime_signoff['contract_status'] == 'drifted'
    assert current_contract['warm_runtime_probe_latency_attention_id'] == 'inspect_runtime_latency'
    assert 'warm runtime latency attention changed since durable signoff' in runtime_signoff['contract_reasons']


def test_macro_runtime_board_json_stales_signoff_when_runtime_probe_witness_is_stale(tmp_path: Path):
    proj = _make_project(tmp_path)

    initial = runner.invoke(app, ['macro-runtime-board-json', str(proj)])
    assert initial.exit_code == 0, initial.output
    initial_payload = json.loads(initial.stdout)
    ready = next(item for item in initial_payload['macros'] if item['name'] == 'ready')
    current_contract = dict((ready.get('acceptance') or {}).get('current_runtime_acceptance_contract') or {})
    assert current_contract.get('digest')

    observed_at = (datetime.now(timezone.utc) - timedelta(seconds=120)).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    write_runtime_state_cache(
        project_root=proj,
        payload={
            'pid': 4444,
            'watchers': ['hotkey'],
            'runtime_contract': {'digest': current_contract.get('resident_runtime_contract_digest') or 'contract-a'},
            'runtime_state': {'runtime_epoch_id': current_contract.get('resident_runtime_epoch_id') or 'epoch-a', 'reload_count': 0},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': observed_at,
                'roundtrip_latency_ms': 19.1,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
                'ack_pid': 4444,
                'ack_handled_at': observed_at,
                'probe_id': 'probe-stale',
            },
        },
        xdg_runtime_dir=None,
    )
    (proj / 'review').mkdir(parents=True, exist_ok=True)
    (proj / 'review' / 'macro_acceptance.yaml').write_text(
        yaml.safe_dump({
            'macros': {
                'ready': {
                    'runtime_acceptance': {
                        'posture_id': 'warm_dispatch_ready',
                        'accepted_by': 'operator',
                        'accepted_at': '2026-03-22T10:50:00Z',
                        'note': 'accepted before probe went stale',
                        'proof_contract': current_contract,
                    }
                }
            }
        }, sort_keys=False)
    )

    res = runner.invoke(app, ['macro-runtime-board-json', str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    ready = next(item for item in payload['macros'] if item['name'] == 'ready')
    runtime_signoff = dict((ready.get('acceptance') or {}).get('runtime_signoff') or {})
    current_contract = dict((ready.get('acceptance') or {}).get('current_runtime_acceptance_contract') or {})

    assert runtime_signoff['status'] == 'stale'
    assert runtime_signoff['contract_status'] == 'drifted'
    assert current_contract['warm_runtime_probe_freshness_attention_id'] == 'refresh_runtime_probe'
    assert 'warm runtime probe freshness attention changed since durable signoff' in runtime_signoff['contract_reasons']


def test_macro_runtime_board_json_carries_macro_scoped_receipt_observability(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
    _write_receipt(proj, "r-ready", macro="ready", recorded_at=now - timedelta(minutes=20), result="emitted")
    _write_receipt(proj, "r-candidate", macro="candidate", recorded_at=now - timedelta(minutes=5), result="blocked")

    res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["summary"]["project_latest_dispatch_macro_name"] == "candidate"
    assert payload["summary"]["project_latest_dispatch_result"] == "blocked"
    assert payload["summary"]["project_latest_dispatch_matches_primary_macro"] is False
    assert payload["receipt_surfaces"]["project_latest_dispatch"]["command"] == "latest_dispatch_json.sh"
    assert payload["receipt_surfaces"]["primary_macro_latest_dispatch"]["macro_name"] == "ready"
    assert payload["receipt_surfaces"]["primary_macro_latest_dispatch"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert payload["receipt_surfaces"]["primary_macro_latest_dispatch"]["matches_project_latest_dispatch"] is False
    assert payload["receipt_surfaces"]["macro_latest_dispatch_template"]["command"] == "macro_latest_dispatch_json.sh <macro>"

    ready = next(item for item in payload["macros"] if item["name"] == "ready")
    assert ready["receipt_observability"]["macro_latest_dispatch"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert ready["receipt_observability"]["macro_latest_dispatch"]["macro_name"] == "ready"
    assert ready["receipt_observability"]["macro_latest_dispatch"]["available"] is True
    assert ready["preferred_entrypoints"]["latest_dispatch"] == "macro_latest_dispatch_json.sh ready"
    assert ready["preferred_entrypoints"]["macro_latest_dispatch"] == "macro_latest_dispatch_json.sh ready"
    assert ready["preferred_entrypoints"]["project_latest_dispatch"] == "latest_dispatch_json.sh"
    assert ready["dispatch_attention"]["id"] == "none"
    assert ready["dispatch_attention"]["command"] == "macro_latest_dispatch_json.sh ready"
    assert ready["receipt_observability"]["macro_latest_dispatch"]["stage_completion_id"] == "stale_receipt_disposition_explicit"
    assert ready["receipt_observability"]["macro_latest_dispatch"]["execution_cutover_id"] == "inspect_stale_receipt_before_runtime_reuse"
    assert ready["receipt_observability"]["macro_latest_dispatch"]["execution_cutover_command"] == "macro_latest_dispatch_json.sh ready"
    assert ready["receipt_observability"]["macro_latest_dispatch"]["receipt_disposition_required"] is True
    assert ready["receipt_observability"]["macro_latest_dispatch"]["redundant_resident_dispatch_risk"] is True

    candidate = next(item for item in payload["macros"] if item["name"] == "candidate")
    assert candidate["dispatch_attention"]["needs_attention"] is True
    assert candidate["dispatch_attention"]["command"] == "macro_latest_dispatch_json.sh candidate"
    assert candidate["dispatch_attention"]["command_scope_id"] == "macro_latest_dispatch"
    assert candidate["receipt_observability"]["macro_latest_dispatch"]["command"] == "macro_latest_dispatch_json.sh candidate"


def test_macro_runtime_board_json_carries_checked_dispatch_handoff_for_ready_macro(tmp_path: Path):
    proj = _make_project(tmp_path)

    res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["summary"]["primary_handoff_id"] == "checked_dispatch_ready"
    assert payload["summary"]["primary_handoff_command"] == "dispatch_macro_checked.sh ready"

    ready = next(item for item in payload["macros"] if item["name"] == "ready")
    handoff = dict(ready.get("runtime_handoff") or {})
    assert handoff["id"] == "checked_dispatch_ready"
    assert handoff["command"] == "dispatch_macro_checked.sh ready"
    assert handoff["command_scope_id"] == "warm_runtime_checked"
    assert handoff["dispatch_safe_now"] is True
    assert handoff["selected_receipt_command"] == "macro_latest_dispatch_json.sh ready"
    assert "macro_latest_dispatch_json.sh ready" in handoff["followup"]


def test_macro_runtime_board_json_prefers_receipt_lane_handoff_when_current_macro_receipt_exists(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)
    _write_receipt(proj, "r-ready", macro="ready", recorded_at=now - timedelta(minutes=2), result="emitted")

    res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    ready = next(item for item in payload["macros"] if item["name"] == "ready")
    handoff = dict(ready.get("runtime_handoff") or {})
    assert handoff["id"] == "inspect_receipt_lane"
    assert handoff["command"] == "macro_latest_dispatch_json.sh ready"
    assert handoff["command_scope_id"] == "macro_latest_dispatch"
    assert handoff["selected_receipt_scope_id"] == "macro_latest_dispatch"
    assert handoff["selected_receipt_command"] == "macro_latest_dispatch_json.sh ready"
    assert handoff["selected_receipt_status_id"] == "latest_dispatch_currentness_unknown"
    assert handoff["execution_cutover_id"] == "inspect_stale_receipt_before_runtime_reuse"
    assert handoff["execution_cutover_command"] == "macro_latest_dispatch_json.sh ready"
    assert handoff["receipt_disposition_required"] is True
    assert handoff["redundant_resident_dispatch_risk"] is True
    assert payload["summary"]["primary_handoff_id"] == "inspect_receipt_lane"
    assert payload["summary"]["primary_handoff_command"] == "macro_latest_dispatch_json.sh ready"
    assert payload["summary"]["primary_stage_completion_id"] == "stale_receipt_disposition_explicit"
    assert payload["summary"]["primary_execution_cutover_id"] == "inspect_stale_receipt_before_runtime_reuse"
    assert payload["summary"]["primary_execution_cutover_command"] == "macro_latest_dispatch_json.sh ready"
