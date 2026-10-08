from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os

import yaml
from typer.testing import CliRunner

from vhk.cli import app


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "author_queue"
    (proj / "macros").mkdir(parents=True)
    (proj / "build" / "dispatch_receipts" / "history").mkdir(parents=True)
    (proj / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "steps": [
                    {"type": "PromptForm", "profile_key": "deploy.run", "fields": [{"name": "reason", "kind": "text"}]},
                    {"type": "RunShell", "command": "echo deploy"},
                ],
            }
        )
    )
    (proj / "macros" / "ping.yaml").write_text(
        yaml.safe_dump({"name": "ping", "steps": [{"type": "TypeText", "text": "ping"}]})
    )
    (proj / "macros" / "steady.yaml").write_text(
        yaml.safe_dump({"name": "steady", "steps": [{"type": "TypeText", "text": "steady"}]})
    )
    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "author_queue",
                "macros": {
                    "deploy": "macros/deploy.yaml",
                    "ping": "macros/ping.yaml",
                    "steady": "macros/steady.yaml",
                },
            }
        )
    )
    return proj


def _write_receipt(project: Path, receipt_id: str, *, macro: str, recorded_at: datetime, result: str, force_override: bool = False, route: str = "checked_dispatch") -> None:
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
        "gate": {"available": True, "decision_id": "dispatch_now" if result == "emitted" else "inspect_before_dispatch", "blockers": ["latest_run_proof_not_clean"] if result == "blocked" else []},
    }
    path = project / "build" / "dispatch_receipts" / "history" / f"{receipt_id}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_macro_author_queue_json_ranks_macros_for_llm_triage(tmp_path: Path):
    proj = _make_project(tmp_path)

    ping_sidecar = proj / "macros" / "ping.window-context.yaml"
    ping_sidecar.write_text(
        yaml.safe_dump(
            {
                "segments": [
                    {"selector_kind": "exact", "transition_reason": "title"},
                ]
            },
            sort_keys=False,
        )
    )
    steady_sidecar = proj / "macros" / "steady.window-context.yaml"
    steady_sidecar.write_text(
        yaml.safe_dump(
            {
                "segments": [
                    {"selector_kind": "stable", "transition_reason": "focus"},
                ]
            },
            sort_keys=False,
        )
    )

    os.utime(ping_sidecar, (1000, 1000))
    os.utime(proj / "macros" / "ping.yaml", (2000, 2000))
    os.utime(steady_sidecar, (3000, 3000))
    os.utime(proj / "macros" / "steady.yaml", (3000, 3000))

    res = runner.invoke(app, ["macro-author-queue-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["stack_kind"] == "vhk.project.macro_author_queue"
    assert payload["project"]["macro_count"] == 3
    assert payload["project"]["interactive_macro_count"] == 1
    assert payload["project"]["review_debt_macro_count"] == 2
    assert payload["summary"]["primary_macro_name"] == "deploy"
    assert payload["summary"]["primary_action_id"] == "record_first_pass"
    assert payload["summary"]["counts_by_action_id"]["record_first_pass"] == 1
    assert payload["summary"]["counts_by_action_id"]["refresh_recording_review"] == 1

    names = [item["name"] for item in payload["macros"]]
    assert names == ["deploy", "ping", "steady"]

    deploy = payload["macros"][0]
    assert deploy["priority"]["rank"] == 0
    assert deploy["priority"]["authoring_phase"] == "record"
    assert deploy["preferred_execution_mode"] == "direct_run"
    assert deploy["preferred_entrypoints"]["author_loop"] == "macro_author_loop_json.sh deploy"
    assert deploy["preferred_entrypoints"]["direct_run"] == "run_macro.sh deploy"
    assert deploy["preferred_entrypoints"]["latest_report"] == "macro_report_latest.sh deploy"
    assert deploy["next_step"]["id"] == "record_first_pass"
    assert deploy["next_step"]["command"] == "record_macro.sh deploy 5000"

    ping = payload["macros"][1]
    assert ping["priority"]["authoring_phase"] == "recording_review"
    assert ping["recording"]["freshness_status"] == "source_newer_than_recording"
    assert ping["review_debt"]["needs_review_count"] >= 1
    assert ping["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert ping["next_step"]["id"] == "refresh_recording_review"
    assert ping["preferred_entrypoints"]["recording_review"] == "macro_recording_json.sh ping"
    assert ping["preferred_entrypoints"]["warm_runtime_checked"] == "dispatch_macro_checked.sh ping"
    assert ping["preferred_entrypoints"]["warm_runtime_gate"] == "macro_dispatch_gate_json.sh ping"
    assert ping["preferred_entrypoints"]["latest_trace"] == "macro_trace_latest.sh ping"

    steady = payload["macros"][2]
    assert steady["recording"]["freshness_status"] == "aligned"
    assert steady["next_step"]["id"] in {"run_current_macro", "dispatch_or_run"}
    assert steady["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert steady["preferred_entrypoints"]["latest_run"] == "macro_latest_run_json.sh steady"


def test_macro_author_queue_json_escalates_dispatch_attention_in_execute_lane(tmp_path: Path):
    proj = _make_project(tmp_path)
    now = datetime.now(timezone.utc)

    for name in ["deploy", "ping", "steady"]:
        sidecar = proj / "macros" / f"{name}.window-context.yaml"
        sidecar.write_text(
            yaml.safe_dump({"segments": [{"selector_kind": "stable", "transition_reason": "focus"}]}, sort_keys=False)
        )
        os.utime(sidecar, (4000, 4000))
        os.utime(proj / "macros" / f"{name}.yaml", (4000, 4000))

    _write_receipt(proj, "blocked-new", macro="ping", recorded_at=now - timedelta(minutes=10), result="blocked")
    _write_receipt(proj, "blocked-old", macro="ping", recorded_at=now - timedelta(minutes=40), result="blocked")
    _write_receipt(proj, "forced", macro="steady", recorded_at=now - timedelta(minutes=20), result="emitted", force_override=True, route="checked_dispatch_forced")

    res = runner.invoke(app, ["macro-author-queue-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["project"]["dispatch_attention_macro_count"] == 2
    assert payload["project"]["dispatch_pressure_escalated_macro_count"] == 2
    assert payload["summary"]["primary_macro_name"] == "ping"
    assert payload["summary"]["primary_dispatch_attention_id"] == "repeated_run_proof_gap"
    assert payload["summary"]["counts_by_dispatch_attention_id"]["repeated_run_proof_gap"] == 1
    assert payload["summary"]["counts_by_dispatch_attention_id"]["forced_override_review"] == 1

    names = [item["name"] for item in payload["macros"]]
    assert names[:3] == ["ping", "steady", "deploy"]

    ping = payload["macros"][0]
    assert ping["dispatch_attention"]["id"] == "repeated_run_proof_gap"
    assert ping["dispatch_attention"]["source_blocker_class_id"] == "run_proof_gap"
    assert ping["dispatch_attention"]["command"] == "run_macro.sh ping"
    assert ping["priority"]["rank"] == 6
    assert ping["priority"]["dispatch_pressure_rank"] == 4
    assert ping["priority"]["effective_rank"] == 4
    assert ping["priority"]["authoring_phase"] == "dispatch_stabilization"
    assert ping["priority"]["escalated_by_dispatch_pressure"] is True
    assert ping["next_step"]["id"] == "run_current_macro"

    steady = next(item for item in payload["macros"] if item["name"] == "steady")
    assert steady["dispatch_attention"]["id"] == "forced_override_review"
    assert steady["dispatch_attention"]["command"] == "run_macro.sh steady"
    assert steady["priority"]["rank"] == 6
    assert steady["priority"]["dispatch_pressure_rank"] == 5
    assert steady["priority"]["effective_rank"] == 5
    assert steady["priority"]["escalated_by_dispatch_pressure"] is True

    deploy = next(item for item in payload["macros"] if item["name"] == "deploy")
    assert deploy["dispatch_attention"]["id"] == "none"
    assert deploy["priority"]["dispatch_pressure_rank"] is None
    assert deploy["priority"]["effective_rank"] == deploy["priority"]["rank"]
