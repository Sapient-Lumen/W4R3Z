from __future__ import annotations

from pathlib import Path
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.desktop_session_contract import summarize_desktop_session_contract
from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract
from vhk.project.macro_proof_contract import summarize_macro_proof_contract
from vhk.project.runtime_state_cache import summarize_runtime_instance_witness_from_cache, write_runtime_state_cache


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "acceptance"
    (proj / "macros").mkdir(parents=True)
    (proj / "logs").mkdir(parents=True)
    (proj / "review").mkdir(parents=True)

    (proj / "macros" / "steady.yaml").write_text(
        yaml.safe_dump({"name": "steady", "steps": [{"type": "TypeText", "text": "steady"}]})
    )
    (proj / "macros" / "prompty.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "prompty",
                "steps": [
                    {"type": "PromptForm", "fields": [{"name": "reason", "kind": "text"}]},
                    {"type": "TypeText", "text": "prompty"},
                ],
            }
        )
    )
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "acceptance",
                "settings": {"event_log": True, "log_dir": "logs"},
                "macros": {
                    "steady": "macros/steady.yaml",
                    "prompty": "macros/prompty.yaml",
                },
            }
        )
    )

    steady_sidecar = proj / "macros" / "steady.window-context.yaml"
    steady_sidecar.write_text(
        yaml.safe_dump(
            {
                "segments": [
                    {"selector_kind": "exact", "transition_reason": "focus", "anchor": {"mode": "window"}},
                ]
            },
            sort_keys=False,
        )
    )
    os.utime(steady_sidecar, (1000, 1000))
    os.utime(proj / "macros" / "steady.yaml", (2000, 2000))

    steady_proof_contract = summarize_macro_proof_contract(proj, "steady")
    with (proj / "logs" / "run_steady.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "run_start", "macro": "steady", "run_id": "run-steady", "ts": 1.0, "macro_proof_contract": steady_proof_contract}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "steady", "run_id": "run-steady", "ts": 2.0, "ok": True}) + "\n")

    (proj / "review" / "macro_acceptance.yaml").write_text(
        yaml.safe_dump(
            {
                "macros": {
                    "steady": {
                        "review_acceptances": [
                            {
                                "issue_code": "stale_recording_sidecar",
                                "accepted_by": "operator",
                                "accepted_at": "2026-03-20T22:30:00Z",
                                "note": "source edit was commentary only",
                            },
                            {
                                "issue_code": "exact_segments",
                                "accepted_by": "operator",
                                "accepted_at": "2026-03-20T22:30:00Z",
                            },
                        ],
                        "runtime_acceptance": {
                            "posture_id": "warm_dispatch_ready",
                            "accepted_by": "operator",
                            "accepted_at": "2026-03-20T22:31:00Z",
                            "note": "known-good on the primary i3 desktop",
                        },
                    },
                    "prompty": {
                        "review_acceptances": [
                            {
                                "issue_code": "missing_recording_sidecar",
                                "accepted_by": "",
                                "accepted_at": "",
                                "note": "left intentionally incomplete",
                            }
                        ]
                    },
                }
            },
            sort_keys=False,
        )
    )
    write_runtime_state_cache(
        project_root=proj,
        xdg_runtime_dir=None,
        payload={
            'pid': 4242,
            'watchers': ['hotkeys'],
            'runtime_state': {'runtime_epoch_id': 'epoch-a', 'reload_count': 0},
            'runtime_contract': {'digest': 'runtime-contract-a'},
        },
    )
    return proj


def test_macro_acceptance_ledger_json_normalizes_review_and_runtime_signoff(tmp_path: Path):
    proj = _make_project(tmp_path)

    res = runner.invoke(app, ["macro-acceptance-ledger-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["stack_kind"] == "vhk.project.macro_acceptance_ledger"
    assert payload["project"]["accepted_macro_count"] == 2
    assert payload["ledger_source"]["relative_path"] == "review/macro_acceptance.yaml"
    assert payload["summary"]["accepted_issue_counts_by_code"]["stale_recording_sidecar"] == 1
    assert payload["summary"]["accepted_issue_counts_by_code"]["exact_segments"] == 1
    assert payload["summary"]["incomplete_issue_counts_by_code"]["missing_recording_sidecar"] == 1
    assert payload["summary"]["runtime_acceptance_counts_by_posture_id"]["warm_dispatch_ready"] == 1
    assert payload["summary"]["current_runtime_signoff_macro_count"] == 0
    assert payload["summary"]["stale_runtime_acceptance_macro_count"] == 1

    macros = {item["name"]: item for item in payload["macros"]}
    steady = macros["steady"]
    assert steady["accepted_review_issue_codes"] == ["exact_segments", "stale_recording_sidecar"]
    assert steady["runtime_acceptance"]["status"] == "accepted"
    assert steady["runtime_acceptance"]["signoff_complete"] is True
    assert steady["runtime_signoff"]["status"] == "stale"
    assert steady["runtime_signoff"]["contract_status"] == "missing"
    assert steady["runtime_signoff"]["stale_reason_id"] == "proof_contract_missing"
    assert steady["current_runtime_acceptance_contract"]["digest"]

    prompty = macros["prompty"]
    assert prompty["accepted_review_issue_codes"] == []
    assert prompty["incomplete_review_issue_codes"] == ["missing_recording_sidecar"]
    assert prompty["review_acceptances"][0]["status"] == "incomplete"


def test_acceptance_ledger_suppresses_signed_off_review_debt_without_hiding_it(tmp_path: Path):
    proj = _make_project(tmp_path)

    author_res = runner.invoke(app, ["macro-author-queue-json", str(proj), "--no-pretty"])
    assert author_res.exit_code == 0, author_res.output
    author_payload = json.loads(author_res.stdout)

    runtime_res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert runtime_res.exit_code == 0, runtime_res.output
    runtime_payload = json.loads(runtime_res.stdout)

    loop_res = runner.invoke(app, ["macro-author-loop-json", str(proj), "steady", "--no-pretty"])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)

    assert author_payload["project"]["review_debt_macro_count"] == 1
    assert author_payload["project"]["accepted_review_debt_macro_count"] == 1
    steady_author = next(item for item in author_payload["macros"] if item["name"] == "steady")
    assert steady_author["review_debt"]["active_counts"]["needs_review_count"] == 0
    assert steady_author["review_debt"]["accepted_counts"]["accepted_issue_count"] == 2
    assert steady_author["next_step"]["id"] == "dispatch_or_run"

    assert runtime_payload["project"]["resident_runtime_macro_count"] == 1
    steady_runtime = next(item for item in runtime_payload["macros"] if item["name"] == "steady")
    assert steady_runtime["runtime_posture"]["id"] == "warm_dispatch_ready"
    assert steady_runtime["acceptance"]["runtime_signoff"]["status"] == "stale"
    assert steady_runtime["acceptance"]["runtime_signoff"]["contract_status"] == "missing"
    assert steady_runtime["acceptance"]["accepted_review_issue_codes"] == ["exact_segments", "stale_recording_sidecar"]

    macro_review = loop_payload["review"]["macro_review"]
    assert macro_review["counts"]["needs_review_count"] == 2
    assert macro_review["active_counts"]["needs_review_count"] == 0
    assert macro_review["accepted_counts"]["accepted_issue_count"] == 2
    assert loop_payload["acceptance"]["runtime_acceptance"]["posture_id"] == "warm_dispatch_ready"
    assert loop_payload["acceptance"]["runtime_signoff"]["status"] == "stale"
    assert loop_payload["acceptance"]["current_runtime_acceptance_contract"]["digest"]
    assert loop_payload["next_step"]["id"] == "dispatch_or_run"


def test_runtime_acceptance_becomes_current_when_proof_contract_is_stored(tmp_path: Path):
    proj = _make_project(tmp_path)

    loop_res = runner.invoke(app, ["macro-author-loop-json", str(proj), "steady", "--no-pretty"])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)
    current_contract = dict(loop_payload["acceptance"]["current_runtime_acceptance_contract"])
    assert current_contract["digest"]

    ledger_path = proj / "review" / "macro_acceptance.yaml"
    ledger = yaml.safe_load(ledger_path.read_text()) or {}
    ledger["macros"]["steady"]["runtime_acceptance"]["proof_contract"] = current_contract
    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False))

    runtime_res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert runtime_res.exit_code == 0, runtime_res.output
    runtime_payload = json.loads(runtime_res.stdout)
    steady_runtime = next(item for item in runtime_payload["macros"] if item["name"] == "steady")
    assert steady_runtime["acceptance"]["runtime_signoff"]["status"] == "accepted"
    assert steady_runtime["acceptance"]["runtime_signoff"]["matches_current_contract"] is True

    ledger_res = runner.invoke(app, ["macro-acceptance-ledger-json", str(proj), "--no-pretty"])
    assert ledger_res.exit_code == 0, ledger_res.output
    ledger_payload = json.loads(ledger_res.stdout)
    assert ledger_payload["summary"]["current_runtime_signoff_macro_count"] == 1
    assert ledger_payload["summary"]["stale_runtime_acceptance_macro_count"] == 0


def test_runtime_acceptance_becomes_stale_when_dispatch_history_changes(tmp_path: Path):
    proj = _make_project(tmp_path)

    loop_res = runner.invoke(app, ["macro-author-loop-json", str(proj), "steady", "--no-pretty"])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)
    current_contract = dict(loop_payload["acceptance"]["current_runtime_acceptance_contract"])
    assert current_contract["dispatch_history_posture_id"] == "no_dispatch_history"

    ledger_path = proj / "review" / "macro_acceptance.yaml"
    ledger = yaml.safe_load(ledger_path.read_text()) or {}
    ledger["macros"]["steady"]["runtime_acceptance"]["proof_contract"] = current_contract
    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False))

    receipt_dir = proj / "build" / "dispatch_receipts" / "history"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    (receipt_dir / "steady-clean.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "stack_kind": "vhk.project.dispatch_receipt",
                "receipt_id": "steady-clean",
                "recorded_at": "2026-03-22T02:00:00Z",
                "project_root": str(proj),
                "macro": "steady",
                "bus_event": "hotkey",
                "result": "emitted",
                "route": "checked_dispatch",
                "checked_gate": True,
                "force_override": False,
                "payload": {"raw_json": json.dumps({"macro": "steady"}), "valid_json": True, "json": {"macro": "steady"}},
                "gate": {"available": True, "decision_id": "dispatch_now", "blockers": []},
            }
        ),
        encoding="utf-8",
    )

    runtime_res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert runtime_res.exit_code == 0, runtime_res.output
    runtime_payload = json.loads(runtime_res.stdout)
    steady_runtime = next(item for item in runtime_payload["macros"] if item["name"] == "steady")
    assert steady_runtime["acceptance"]["runtime_signoff"]["status"] == "stale"
    assert steady_runtime["acceptance"]["runtime_signoff"]["contract_status"] == "drifted"
    assert steady_runtime["acceptance"]["runtime_signoff"]["stale_reason_id"] == "proof_contract_drift"
    assert "warm dispatch history posture changed since durable signoff" in steady_runtime["acceptance"]["runtime_signoff"]["contract_reasons"]



def test_runtime_acceptance_becomes_stale_when_resident_runtime_changes(tmp_path: Path):
    proj = _make_project(tmp_path)

    loop_res = runner.invoke(app, ["macro-author-loop-json", str(proj), "steady", "--no-pretty"])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)
    current_contract = dict(loop_payload["acceptance"]["current_runtime_acceptance_contract"])
    assert current_contract["resident_runtime_epoch_id"] == "epoch-a"
    assert current_contract["resident_runtime_contract_digest"] == "runtime-contract-a"

    ledger_path = proj / "review" / "macro_acceptance.yaml"
    ledger = yaml.safe_load(ledger_path.read_text()) or {}
    ledger["macros"]["steady"]["runtime_acceptance"]["proof_contract"] = current_contract
    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False))

    write_runtime_state_cache(
        project_root=proj,
        xdg_runtime_dir=None,
        payload={
            'pid': 5252,
            'watchers': ['hotkeys'],
            'runtime_state': {'runtime_epoch_id': 'epoch-b', 'reload_count': 1},
            'runtime_contract': {'digest': 'runtime-contract-b'},
        },
    )

    runtime_res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert runtime_res.exit_code == 0, runtime_res.output
    runtime_payload = json.loads(runtime_res.stdout)
    steady_runtime = next(item for item in runtime_payload["macros"] if item["name"] == "steady")
    runtime_signoff = steady_runtime["acceptance"]["runtime_signoff"]
    assert runtime_signoff["status"] == "stale"
    assert runtime_signoff["contract_status"] == "drifted"
    assert runtime_signoff["stale_reason_id"] == "proof_contract_drift"
    assert "resident runtime epoch changed since durable signoff" in runtime_signoff["contract_reasons"]
    assert "resident runtime contract changed since durable signoff" in runtime_signoff["contract_reasons"]



def test_runtime_acceptance_becomes_stale_when_desktop_session_changes(tmp_path: Path, monkeypatch):
    proj = _make_project(tmp_path)

    monkeypatch.setenv('DISPLAY', ':0')
    monkeypatch.setenv('I3SOCK', '/run/user/1000/i3/ipc-socket.1000')
    monkeypatch.setenv('XDG_RUNTIME_DIR', '/run/user/1000')

    loop_res = runner.invoke(app, ['macro-author-loop-json', str(proj), 'steady', '--no-pretty'])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)
    current_contract = dict(loop_payload['acceptance']['current_runtime_acceptance_contract'])
    assert current_contract['desktop_session_contract_digest']

    ledger_path = proj / 'review' / 'macro_acceptance.yaml'
    ledger = yaml.safe_load(ledger_path.read_text()) or {}
    ledger['macros']['steady']['runtime_acceptance']['proof_contract'] = current_contract
    ledger_path.write_text(yaml.safe_dump(ledger, sort_keys=False))

    monkeypatch.setenv('DISPLAY', ':1')
    monkeypatch.setenv('I3SOCK', '/run/user/1000/i3/ipc-socket.2000')

    runtime_res = runner.invoke(app, ['macro-runtime-board-json', str(proj)])
    assert runtime_res.exit_code == 0, runtime_res.output
    runtime_payload = json.loads(runtime_res.stdout)
    steady_runtime = next(item for item in runtime_payload['macros'] if item['name'] == 'steady')
    runtime_signoff = steady_runtime['acceptance']['runtime_signoff']
    assert runtime_signoff['status'] == 'stale'
    assert runtime_signoff['contract_status'] == 'drifted'
    assert runtime_signoff['stale_reason_id'] == 'proof_contract_drift'
    assert 'desktop session changed since durable signoff' in runtime_signoff['contract_reasons']


def test_macro_runtime_accept_writes_current_proof_contract(tmp_path: Path):
    proj = _make_project(tmp_path)

    res = runner.invoke(
        app,
        [
            "macro-runtime-accept",
            str(proj),
            "steady",
            "--accepted-by",
            "llm-operator",
            "--accepted-at",
            "2026-03-22T02:40:00Z",
            "--note",
            "current warm busd proof looks good",
            "--force",
            "--no-pretty",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.runtime_acceptance_write_receipt"
    assert payload["macro"]["name"] == "steady"
    assert payload["written_runtime_acceptance"]["accepted_by"] == "llm-operator"
    assert payload["written_runtime_acceptance"]["proof_contract_digest"] == payload["current_runtime_acceptance_contract"]["digest"]

    ledger = yaml.safe_load((proj / "review" / "macro_acceptance.yaml").read_text()) or {}
    runtime_acceptance = ledger["macros"]["steady"]["runtime_acceptance"]
    assert runtime_acceptance["accepted_by"] == "llm-operator"
    assert runtime_acceptance["accepted_at"] == "2026-03-22T02:40:00Z"
    assert runtime_acceptance["note"] == "current warm busd proof looks good"
    assert runtime_acceptance["proof_contract"]["digest"] == payload["current_runtime_acceptance_contract"]["digest"]
    assert runtime_acceptance["force_override"] is True

    ledger_res = runner.invoke(app, ["macro-acceptance-ledger-json", str(proj), "--no-pretty"])
    assert ledger_res.exit_code == 0, ledger_res.output
    ledger_payload = json.loads(ledger_res.stdout)
    steady = next(item for item in ledger_payload["macros"] if item["name"] == "steady")
    assert steady["runtime_signoff"]["status"] == "forced_review"
    assert steady["runtime_signoff"]["matches_current_contract"] is True
    assert steady["runtime_signoff"]["force_review_required"] is True



def test_macro_runtime_accept_dry_run_does_not_write_ledger(tmp_path: Path):
    proj = _make_project(tmp_path)
    before = (proj / "review" / "macro_acceptance.yaml").read_text()

    res = runner.invoke(
        app,
        [
            "macro-runtime-accept",
            str(proj),
            "steady",
            "--accepted-by",
            "llm-operator",
            "--note",
            "preview only",
            "--force",
            "--dry-run",
            "--no-pretty",
        ],
    )
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["dry_run"] is True
    assert payload["written_runtime_acceptance"]["accepted_by"] == "llm-operator"
    assert (proj / "review" / "macro_acceptance.yaml").read_text() == before


def test_runtime_acceptance_signoff_readiness_blocks_target_unproven_replay(tmp_path: Path):
    proj = _make_project(tmp_path)

    (proj / "macros" / "steady.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "steady",
                "when": {"class": "Alacritty", "workspace": "2"},
                "steps": [{"type": "TypeText", "text": "steady"}],
            }
        ),
        encoding="utf-8",
    )
    os.utime(proj / "macros" / "steady.yaml", (4000, 4000))
    contract = summarize_macro_proof_contract(proj, "steady")
    (proj / "logs" / "run_steady.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "run_start",
                        "macro": "steady",
                        "run_id": "run-steady-target",
                        "ts": 10.0,
                        "macro_proof_contract": contract,
                        "desktop_session_contract": summarize_desktop_session_contract(),
                    }
                ),
                json.dumps({"type": "run_end", "macro": "steady", "run_id": "run-steady-target", "ts": 11.0, "ok": True}),
            ]
        ) + "\n",
        encoding="utf-8",
    )

    write_runtime_state_cache(
        project_root=proj,
        xdg_runtime_dir=None,
        payload={
            "pid": 4242,
            "watchers": ["hotkeys"],
            "runtime_state": {"runtime_epoch_id": "epoch-a", "reload_count": 0},
            "runtime_contract": {"digest": "runtime-contract-a"},
            "dispatch_probe_observation": {
                "status": "ok",
                "ok": True,
                "observed_at": "2026-03-23T01:00:00Z",
                "roundtrip_latency_ms": 12.0,
                "latency_status": "within_budget",
                "latency_budget_ms": 60.0,
                "ack_pid": 4242,
                "probe_id": "probe-steady",
            },
        },
    )
    runtime_witness = summarize_runtime_instance_witness_from_cache(project_root=proj)

    gate_res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "steady", "--no-pretty"])
    assert gate_res.exit_code == 0, gate_res.output
    gate_payload = json.loads(gate_res.stdout)
    observed_contract = summarize_dispatch_receipt_contract(
        proj,
        "steady",
        bus_event="hotkey",
        gate_payload={
            "preferred_execution_mode": gate_payload["preferred_execution_mode"],
            "dispatch_contract": dict(gate_payload.get("dispatch_contract") or {}),
            "dispatch_readiness": {"desktop_target": dict((gate_payload.get("dispatch_readiness") or {}).get("desktop_target") or {})},
        },
    )
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "steady-current",
        "recorded_at": "2026-03-23T01:00:01Z",
        "project_root": str(proj),
        "macro": "steady",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"steady"}', "valid_json": True, "json": {"macro": "steady"}},
        "gate": {
            "available": True,
            "can_emit_minimal_payload_now": True,
            "blockers": [],
            "blocker_details": [],
            "reason": "ready",
            "decision_id": "dispatch_now",
            "preferred_execution_mode": "warm_runtime_dispatch",
        },
        "dispatch_receipt_contract": observed_contract,
        "desktop_session_contract": summarize_desktop_session_contract(),
        "dispatch_runtime_witness": runtime_witness,
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    (history_root / "steady-current.json").write_text(json.dumps(receipt), encoding="utf-8")

    loop_res = runner.invoke(app, ["macro-author-loop-json", str(proj), "steady", "--no-pretty"])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)
    readiness = dict((loop_payload.get("acceptance") or {}).get("runtime_signoff_readiness") or {})
    assert readiness["status_id"] == "blocked_by_replay_target_authority"
    assert readiness["ready"] is False
    assert readiness["command"] == "macro_dispatch_gate_json.sh steady"
    assert loop_payload["llm_workbench"]["mode_id"] == "inspect_replay_target_authority"
    assert loop_payload["execution"]["latest_dispatch_handoff"]["status_id"] == "current_warm_runtime_evidence"

    runtime_res = runner.invoke(app, ["macro-runtime-board-json", str(proj)])
    assert runtime_res.exit_code == 0, runtime_res.output
    runtime_payload = json.loads(runtime_res.stdout)
    steady_runtime = next(item for item in runtime_payload["macros"] if item["name"] == "steady")
    assert steady_runtime["acceptance"]["runtime_signoff_readiness"]["status_id"] == "blocked_by_replay_target_authority"

    blocked = runner.invoke(
        app,
        [
            "macro-runtime-accept",
            str(proj),
            "steady",
            "--accepted-by",
            "llm-operator",
            "--note",
            "current warm busd proof looks good",
            "--no-pretty",
        ],
    )
    assert blocked.exit_code != 0
    assert "blocked_by_replay_target_authority" in blocked.output
    assert "macro_dispatch_gate_json.sh steady" in blocked.output

    forced = runner.invoke(
        app,
        [
            "macro-runtime-accept",
            str(proj),
            "steady",
            "--accepted-by",
            "llm-operator",
            "--note",
            "force while target proof is still partial",
            "--force",
            "--dry-run",
            "--no-pretty",
        ],
    )
    assert forced.exit_code == 0, forced.output
    forced_payload = json.loads(forced.stdout)
    assert forced_payload["force"] is True
    assert forced_payload["runtime_signoff_readiness"]["status_id"] == "blocked_by_replay_target_authority"




def test_runtime_acceptance_signoff_readiness_blocks_forced_dispatch_receipt(tmp_path: Path):
    proj = _make_project(tmp_path)

    write_runtime_state_cache(
        project_root=proj,
        xdg_runtime_dir=None,
        payload={
            'pid': 4242,
            'watchers': ['hotkeys'],
            'runtime_state': {'runtime_epoch_id': 'epoch-clean', 'reload_count': 0},
            'runtime_contract': {'digest': 'runtime-contract-clean'},
            'dispatch_probe_observation': {
                'status': 'ok',
                'ok': True,
                'observed_at': '2026-03-23T01:05:00Z',
                'roundtrip_latency_ms': 12.0,
                'latency_status': 'within_budget',
                'latency_budget_ms': 60.0,
            },
        },
    )
    runtime_witness = summarize_runtime_instance_witness_from_cache(project_root=proj, xdg_runtime_dir=None)
    gate_payload = {
        'preferred_execution_mode': 'warm_runtime_dispatch',
        'dispatch_contract': {'bus_payload_minimal': {'macro': 'steady'}},
        'dispatch_readiness': {'desktop_target': {}},
    }
    observed_contract = summarize_dispatch_receipt_contract(proj, 'steady', bus_event='hotkey', gate_payload=gate_payload)
    receipt = {
        'schema_version': 1,
        'stack_kind': 'vhk.project.dispatch_receipt',
        'receipt_id': 'steady-current-forced',
        'recorded_at': '2026-03-23T01:06:00Z',
        'project_root': str(proj),
        'macro': 'steady',
        'bus_event': 'hotkey',
        'result': 'emitted',
        'route': 'checked_dispatch_forced',
        'checked_gate': True,
        'force_override': True,
        'payload': {'raw_json': '{\"macro\":\"steady\"}', 'valid_json': True, 'json': {'macro': 'steady'}},
        'gate': {
            'available': True,
            'can_emit_minimal_payload_now': False,
            'blockers': [],
            'blocker_details': [],
            'reason': 'forced emit',
            'decision_id': 'dispatch_now',
            'preferred_execution_mode': 'warm_runtime_dispatch',
        },
        'dispatch_receipt_contract': observed_contract,
        'desktop_session_contract': summarize_desktop_session_contract(),
        'dispatch_runtime_witness': runtime_witness,
    }
    latest_path = proj / 'build' / 'dispatch_receipts' / 'latest.json'
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding='utf-8')
    history_root = proj / 'build' / 'dispatch_receipts' / 'history'
    history_root.mkdir(parents=True, exist_ok=True)
    (history_root / 'steady-current-forced.json').write_text(json.dumps(receipt), encoding='utf-8')

    loop_res = runner.invoke(app, ['macro-author-loop-json', str(proj), 'steady', '--no-pretty'])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)
    readiness = dict((loop_payload.get('acceptance') or {}).get('runtime_signoff_readiness') or {})
    assert readiness['status_id'] == 'blocked_by_forced_dispatch_receipt'
    assert readiness['ready'] is False
    assert readiness['command'] == 'macro_latest_dispatch_json.sh steady'
    assert loop_payload['llm_workbench']['mode_id'] == 'replace_forced_dispatch_receipt'
    assert loop_payload['llm_workbench']['lane_transition']['transition_id'] == 'inspect_forced_receipt_before_clean_replacement'
    assert loop_payload['llm_workbench']['stage_completion']['completion_id'] == 'forced_receipt_disposition_and_clean_replacement_explicit'
    assert loop_payload['llm_workbench']['execution_cutover']['cutover_id'] == 'inspect_forced_receipt_before_clean_replacement'
    assert loop_payload['execution']['latest_dispatch_handoff']['status_id'] == 'current_forced_dispatch_evidence'
    assert loop_payload['execution']['latest_dispatch_handoff']['clean_replacement_required'] is True

    blocked = runner.invoke(
        app,
        [
            'macro-runtime-accept',
            str(proj),
            'steady',
            '--accepted-by',
            'llm-operator',
            '--note',
            'forced checked-dispatch receipt should not sign off cleanly',
            '--no-pretty',
        ],
    )
    assert blocked.exit_code != 0
    assert 'blocked_by_forced_dispatch_receipt' in blocked.output


def test_forced_runtime_acceptance_stays_visible_as_clean_replacement_debt(tmp_path: Path):
    proj = _make_project(tmp_path)

    (proj / "macros" / "steady.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "steady",
                "when": {"class": "Alacritty", "workspace": "2"},
                "steps": [{"type": "TypeText", "text": "steady"}],
            }
        ),
        encoding="utf-8",
    )
    os.utime(proj / "macros" / "steady.yaml", (4100, 4100))
    contract = summarize_macro_proof_contract(proj, "steady")
    (proj / "logs" / "run_steady.jsonl").write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "run_start",
                        "macro": "steady",
                        "run_id": "run-steady-forced-signoff",
                        "ts": 10.0,
                        "macro_proof_contract": contract,
                        "desktop_session_contract": summarize_desktop_session_contract(),
                    }
                ),
                json.dumps({"type": "run_end", "macro": "steady", "run_id": "run-steady-forced-signoff", "ts": 11.0, "ok": True}),
            ]
        ) + "\n",
        encoding="utf-8",
    )

    write_runtime_state_cache(
        project_root=proj,
        xdg_runtime_dir=None,
        payload={
            "pid": 5252,
            "watchers": ["hotkeys"],
            "runtime_state": {"runtime_epoch_id": "epoch-forced", "reload_count": 0},
            "runtime_contract": {"digest": "runtime-contract-forced"},
            "dispatch_probe_observation": {
                "status": "ok",
                "ok": True,
                "observed_at": "2026-03-23T01:10:00Z",
                "roundtrip_latency_ms": 9.0,
                "latency_status": "within_budget",
                "latency_budget_ms": 60.0,
                "ack_pid": 5252,
                "probe_id": "probe-forced-signoff",
            },
        },
    )
    runtime_witness = summarize_runtime_instance_witness_from_cache(project_root=proj)

    gate_res = runner.invoke(app, ["macro-dispatch-gate-json", str(proj), "steady", "--no-pretty"])
    assert gate_res.exit_code == 0, gate_res.output
    gate_payload = json.loads(gate_res.stdout)
    observed_contract = summarize_dispatch_receipt_contract(
        proj,
        "steady",
        bus_event="hotkey",
        gate_payload={
            "preferred_execution_mode": gate_payload["preferred_execution_mode"],
            "dispatch_contract": dict(gate_payload.get("dispatch_contract") or {}),
            "dispatch_readiness": {"desktop_target": dict((gate_payload.get("dispatch_readiness") or {}).get("desktop_target") or {})},
        },
    )
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "steady-forced-signoff-current",
        "recorded_at": "2026-03-23T01:10:01Z",
        "project_root": str(proj),
        "macro": "steady",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"steady"}', "valid_json": True, "json": {"macro": "steady"}},
        "gate": {
            "available": True,
            "can_emit_minimal_payload_now": True,
            "blockers": [],
            "blocker_details": [],
            "reason": "ready",
            "decision_id": "dispatch_now",
            "preferred_execution_mode": "warm_runtime_dispatch",
        },
        "dispatch_receipt_contract": observed_contract,
        "desktop_session_contract": summarize_desktop_session_contract(),
        "dispatch_runtime_witness": runtime_witness,
    }
    latest_path = proj / "build" / "dispatch_receipts" / "latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(json.dumps(receipt), encoding="utf-8")
    history_root = proj / "build" / "dispatch_receipts" / "history"
    history_root.mkdir(parents=True, exist_ok=True)
    (history_root / "steady-forced-signoff-current.json").write_text(json.dumps(receipt), encoding="utf-8")

    forced = runner.invoke(
        app,
        [
            "macro-runtime-accept",
            str(proj),
            "steady",
            "--accepted-by",
            "llm-operator",
            "--note",
            "force while target proof is still partial",
            "--accepted-at",
            "2026-03-23T01:11:00Z",
            "--force",
            "--no-pretty",
        ],
    )
    assert forced.exit_code == 0, forced.output
    forced_payload = json.loads(forced.stdout)
    assert forced_payload["written_runtime_acceptance"]["force_override"] is True
    assert forced_payload["written_runtime_acceptance"]["forced_readiness_status_id"] == "blocked_by_replay_target_authority"

    ledger_res = runner.invoke(app, ["macro-acceptance-ledger-json", str(proj), "--no-pretty"])
    assert ledger_res.exit_code == 0, ledger_res.output
    ledger_payload = json.loads(ledger_res.stdout)
    steady = next(item for item in ledger_payload["macros"] if item["name"] == "steady")
    assert ledger_payload["summary"]["forced_runtime_acceptance_macro_count"] == 1
    assert ledger_payload["summary"]["current_runtime_signoff_macro_count"] == 0
    assert steady["runtime_acceptance"]["force_override"] is True
    assert steady["runtime_signoff"]["status"] == "forced_review"
    assert steady["runtime_signoff"]["force_review_required"] is True
    assert steady["runtime_signoff"]["stale_reason_id"] == "forced_signoff_requires_clean_replacement"
    assert steady["runtime_signoff"]["forced_readiness_status_id"] == "blocked_by_replay_target_authority"
    assert "forced runtime signoff still needs clean replacement" in steady["runtime_signoff"]["contract_reasons"][0]

    loop_res = runner.invoke(app, ["macro-author-loop-json", str(proj), "steady", "--no-pretty"])
    assert loop_res.exit_code == 0, loop_res.output
    loop_payload = json.loads(loop_res.stdout)
    assert loop_payload["acceptance"]["runtime_signoff"]["status"] == "forced_review"
    assert loop_payload["acceptance"]["runtime_signoff"]["force_review_required"] is True
