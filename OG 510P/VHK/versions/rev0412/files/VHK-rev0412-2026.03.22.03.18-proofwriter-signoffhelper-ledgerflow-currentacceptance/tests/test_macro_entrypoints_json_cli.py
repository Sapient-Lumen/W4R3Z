from __future__ import annotations

from pathlib import Path
import os
import json

import yaml
from typer.testing import CliRunner

from vhk.cli import app
from vhk.project.dispatch_receipt_contract import summarize_dispatch_receipt_contract
from vhk.project.macro_proof_contract import summarize_macro_proof_contract


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "entrypoints"
    (proj / "macros").mkdir(parents=True)
    (proj / "macros" / "deploy.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "deploy",
                "group": "ops",
                "tags": ["shell", "ops"],
                "presets": [{"name": "staging", "vars": {"env": "staging"}}],
                "steps": [
                    {"type": "PromptForm", "profile_key": "deploy.run", "fields": [{"name": "reason", "kind": "text"}]},
                    {"type": "RunShell", "command": "echo deploy"},
                ],
            }
        )
    )
    (proj / "macros" / "ping.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "ping",
                "tags": ["text"],
                "steps": [{"type": "TypeText", "text": "hello"}],
            }
        )
    )
    (proj / "project.yaml").write_text(yaml.safe_dump({"name": "entrypoints", "macros": {"deploy": "macros/deploy.yaml", "ping": "macros/ping.yaml"}}))
    return proj


def test_macro_entrypoints_json_reports_preferred_routes(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-entrypoints-json", str(proj), "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_entrypoints"
    assert payload["project"]["macro_count"] == 2
    assert payload["project"]["interactive_macro_count"] == 1
    assert payload["project"]["preset_enabled_macro_count"] == 1
    deploy = next(item for item in payload["macros"] if item["name"] == "deploy")
    assert deploy["preferred_entrypoints"]["source"] == "macro_source_json.sh deploy"
    assert deploy["preferred_entrypoints"]["author_loop"] == "macro_author_loop_json.sh deploy"
    assert deploy["preferred_entrypoints"]["recording_review"] == "macro_recording_json.sh deploy"
    assert deploy["preferred_entrypoints"]["render_review"] == "render_macro.sh deploy"
    assert deploy["preferred_entrypoints"]["lint_review"] == "lint_macro.sh deploy"
    assert deploy["preferred_entrypoints"]["cleanup_review"] == "optimize_macro.sh deploy"
    assert deploy["preferred_entrypoints"]["cleanup_apply"] == "apply_optimize_macro.sh deploy"
    assert deploy["preferred_entrypoints"]["retime"] == "retime_macro.sh deploy"
    assert deploy["preferred_entrypoints"]["warm_runtime"] == "dispatch_macro.sh deploy"
    assert deploy["preferred_entrypoints"]["warm_runtime_checked"] == "dispatch_macro_checked.sh deploy"
    assert deploy["preferred_entrypoints"]["warm_runtime_gate"] == "macro_dispatch_gate_json.sh deploy"
    assert deploy["preferred_entrypoints"]["direct_run"] == "run_macro.sh deploy"
    assert deploy["hints"]["has_interactive_inputs"] is True
    assert deploy["hints"]["best_for_minimal_bus_dispatch"] is False
    assert deploy["preset_names"] == ["staging"]
    assert deploy["prompt_profile_keys"] == ["deploy.run"]
    assert deploy["invocation"]["direct_run"]["argv"][:4] == ["vhk", "run", str(proj.resolve()), "deploy"]
    assert deploy["source"]["relative_path"] == "macros/deploy.yaml"
    assert deploy["source"]["review"]["render_command"] == ["vhk", "render", str(proj.resolve()), "deploy"]
    ping = next(item for item in payload["macros"] if item["name"] == "ping")
    assert ping["hints"]["best_for_minimal_bus_dispatch"] is True
    assert ping["recommended_examples"]["dispatch_now"] == "dispatch_macro.sh ping"
    assert ping["recommended_examples"]["dispatch_now_checked"] == "dispatch_macro_checked.sh ping"
    assert ping["recommended_examples"]["dispatch_gate"] == "macro_dispatch_gate_json.sh ping"
    assert ping["recommended_examples"]["show_source"] == "macro_source_json.sh ping"
    assert ping["recommended_examples"]["author_loop"] == "macro_author_loop_json.sh ping"
    assert ping["recommended_examples"]["recording_review"] == "macro_recording_json.sh ping"


def test_macro_source_json_reports_edit_and_review_contract(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-source-json", str(proj), "deploy", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_source"
    assert payload["project"]["name"] == "entrypoints"
    assert payload["macro"]["name"] == "deploy"
    source = payload["source"]
    assert source["relative_path"] == "macros/deploy.yaml"
    assert source["editable"] is True
    assert source["exists"] is True
    assert source["review"]["lint_command"][-1] == "--json"
    assert source["recording_sidecar"]["relative_path"] == "macros/deploy.window-context.yaml"
    assert source["recording_sidecar"]["freshness"]["status"] == "missing"
    assert source["recording_sidecar"]["freshness"]["stale_for_source_review"] is False
    assert source["review"]["record_defaults"]["coord_mode_mouse"] == "window"
    assert source["review"]["cleanup_review_command"][1:4] == ["optimize", str((proj / "macros" / "deploy.yaml").resolve()), "--diff"]
    assert source["review"]["cleanup_apply_command"][1:4] == ["optimize", str((proj / "macros" / "deploy.yaml").resolve()), "--in-place"]
    assert source["review"]["retime_command_prefix"][:2] == ["vhk", "retime"]
    assert "--speed <multiplier>" in source["review"]["retime_common_options"]
    assert source["generated_stack"]["recording_review_wrapper"] == "macro_recording_json.sh deploy"
    assert source["generated_stack"]["render_wrapper"] == "render_macro.sh deploy"
    assert source["generated_stack"]["cleanup_review_wrapper"] == "optimize_macro.sh deploy"
    assert source["generated_stack"]["cleanup_apply_wrapper"] == "apply_optimize_macro.sh deploy"
    assert source["generated_stack"]["retime_wrapper"] == "retime_macro.sh deploy"


def test_macro_recording_json_reports_sidecar_summary(tmp_path: Path):
    proj = _make_project(tmp_path)
    sidecar = proj / "macros" / "deploy.window-context.yaml"
    sidecar.write_text(
        yaml.safe_dump(
            {
                "suggested": {"stable": {"class": "Firefox"}},
                "samples": [{"title": "Deploy"}, {"title": "Deploy"}],
                "segments": [
                    {"selector_kind": "stable", "transition_reason": "focus", "stable_selector": {"class": "Firefox"}, "relative_mouse_anchor": {"mode": "window"}},
                    {"selector_kind": "exact", "transition_reason": "title", "exact_selector": {"class": "Firefox", "title": "Deploy"}},
                ],
                "window_guard_scope": "active",
                "window_guard_mode": "event",
                "segment_on_title_change": True,
            },
            sort_keys=False,
        )
    )
    res = runner.invoke(app, ["macro-recording-json", str(proj), "deploy", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_recording"
    assert payload["recording"]["relative_path"] == "macros/deploy.window-context.yaml"
    assert payload["recording"]["exists"] is True
    assert payload["recording"]["segment_count"] == 2
    assert payload["recording"]["selector_kind_counts"] == {"exact": 1, "stable": 1}
    assert payload["recording"]["transition_reason_counts"] == {"focus": 1, "title": 1}
    assert payload["recording"]["window_guard_mode"] == "event"
    assert payload["recording"]["relative_mouse_mode"] == "window"
    assert payload["recording"]["selector_summary"]["selector_source_id"] == "recording_stable_selector"
    assert payload["recording"]["selector_summary"]["selector"]["class"] == "Firefox"
    assert payload["recording"]["selector_summary"]["exact_segment_count"] == 1
    assert payload["review"]["generated_stack"]["recording_review"] == "macro_recording_json.sh deploy"


def test_macro_recording_json_selector_summary_prefers_macro_when(tmp_path: Path):
    proj = _make_project(tmp_path)
    macro_path = proj / "macros" / "deploy.yaml"
    macro_doc = yaml.safe_load(macro_path.read_text())
    macro_doc["when"] = {"class": "Alacritty", "workspace": "2"}
    macro_path.write_text(yaml.safe_dump(macro_doc, sort_keys=False))
    sidecar = proj / "macros" / "deploy.window-context.yaml"
    sidecar.write_text(
        yaml.safe_dump(
            {
                "suggested": {"stable": {"class": "Firefox", "workspace": "9"}},
                "segments": [
                    {"selector_kind": "stable", "transition_reason": "workspace", "stable_selector": {"class": "Firefox", "workspace": "9"}},
                ],
            },
            sort_keys=False,
        )
    )
    res = runner.invoke(app, ["macro-recording-json", str(proj), "deploy", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    selector_summary = payload["recording"]["selector_summary"]
    assert selector_summary["selector_source_id"] == "macro_when"
    assert selector_summary["selector"]["class"] == "Alacritty"
    assert selector_summary["selector"]["workspace"] == "2"
    assert selector_summary["recording_stable_selector"]["class"] == "Firefox"
    assert selector_summary["workspace_expected"] is True



def test_macro_recording_json_reports_source_drift_when_macro_newer_than_sidecar(tmp_path: Path):
    proj = _make_project(tmp_path)
    sidecar = proj / "macros" / "deploy.window-context.yaml"
    sidecar.write_text(yaml.safe_dump({"suggested": {"stable": {"class": "Firefox"}}, "segments": [{"selector_kind": "stable", "transition_reason": "focus"}]}, sort_keys=False))
    macro = proj / "macros" / "deploy.yaml"
    os.utime(sidecar, (1000, 1000))
    os.utime(macro, (2000, 2000))
    res = runner.invoke(app, ["macro-recording-json", str(proj), "deploy", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    freshness = payload["recording"]["freshness"]
    assert freshness["status"] == "source_newer_than_recording"
    assert freshness["stale_for_source_review"] is True
    assert freshness["mtime_delta_ms"] < 0
    assert "stale" in freshness["review_notes"][0].lower()


def test_macro_author_loop_json_fuses_macro_review_contract(tmp_path: Path):
    proj = _make_project(tmp_path)
    res = runner.invoke(app, ["macro-author-loop-json", str(proj), "deploy", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)
    assert payload["stack_kind"] == "vhk.project.macro_author_loop"
    assert payload["macro"]["name"] == "deploy"
    assert payload["source"]["relative_path"] == "macros/deploy.yaml"
    assert payload["recording"]["freshness"]["status"] == "missing"
    assert payload["review"]["macro_review"]["counts"]["missing_recording_sidecars"] == 1
    assert payload["next_step"]["id"] == "record_first_pass"
    assert payload["next_step"]["command"] == "record_macro.sh deploy 5000"
    assert payload["llm_handoff"]["preferred_entrypoint"] == "macro_author_loop_json.sh deploy"
    assert payload["llm_handoff"]["authoritative_inputs"]["macro_source_json"] == "macro_source_json.sh deploy"
    assert payload["llm_handoff"]["execution_review_inputs"]["macro_dispatch_gate_json"] == "macro_dispatch_gate_json.sh deploy"
    assert payload["llm_handoff"]["execution_review_inputs"]["macro_dispatch_history_board_json"] == "macro_dispatch_history_board_json.sh"
    assert payload["llm_handoff"]["preferred_execution_mode"] == "direct_run"
    assert payload["contract"]["recommended_examples"]["author_loop"] == "macro_author_loop_json.sh deploy"
    assert payload["execution"]["runtime_posture"]["id"] == "direct_run_only"
    assert payload["execution"]["runtime_signoff"]["status"] == "missing"
    assert payload["acceptance"]["current_runtime_acceptance_contract"]["digest"]
    assert payload["acceptance"]["runtime_signoff"]["status"] == "missing"
    assert payload["execution"]["dispatch_gate"]["decision"]["id"] == "direct_run_only"
    assert payload["execution"]["dispatch_gate"]["decision"]["command"] == "run_macro.sh deploy"
    assert payload["execution"]["dispatch_gate"]["repair_action"]["id"] == "use_direct_run"
    assert payload["execution"]["dispatch_gate"]["dispatch_readiness"]["blockers"] == ["interactive_inputs_require_direct_run"]
    assert payload["execution"]["dispatch_gate"]["dispatch_contract"]["gate_command"] == "macro_dispatch_gate_json.sh deploy"
    assert payload["execution"]["dispatch_history"]["posture"]["id"] == "no_dispatch_history"
    assert payload["execution"]["preferred_entrypoints"]["direct_run"] == "run_macro.sh deploy"


def test_macro_author_loop_json_carries_runtime_and_dispatch_history_context(tmp_path: Path):
    proj = _make_project(tmp_path)
    sidecar = proj / "macros" / "ping.window-context.yaml"
    sidecar.write_text(yaml.safe_dump({"segments": [{"selector_kind": "stable", "transition_reason": "focus", "relative_mouse_anchor": {"mode": "window"}}]}, sort_keys=False))
    os.utime(sidecar, (3000, 3000))
    os.utime(proj / "macros" / "ping.yaml", (3000, 3000))

    gate_payload = {"preferred_execution_mode": "warm_runtime_dispatch", "dispatch_contract": {"bus_payload_minimal": {"macro": "ping"}}, "dispatch_readiness": {"desktop_target": {}}}
    receipts = proj / "build" / "dispatch_receipts" / "history"
    receipts.mkdir(parents=True)
    receipt = {
        "schema_version": 1,
        "stack_kind": "vhk.project.dispatch_receipt",
        "receipt_id": "dispatch-1-ping",
        "recorded_at": "2026-03-20T23:58:00Z",
        "project_root": str(proj),
        "macro": "ping",
        "bus_event": "hotkey",
        "result": "emitted",
        "route": "checked_dispatch",
        "checked_gate": True,
        "force_override": False,
        "payload": {"raw_json": '{"macro":"ping"}', "valid_json": True, "json": {"macro": "ping"}},
        "gate": {"available": True, "can_emit_minimal_payload_now": True, "blockers": [], "reason": "ready", "decision_id": "dispatch_now", "preferred_execution_mode": "warm_runtime_dispatch"},
        "dispatch_receipt_contract": summarize_dispatch_receipt_contract(proj, "ping", bus_event="hotkey", gate_payload=gate_payload),
    }
    (receipts / "dispatch-1-ping.json").write_text(json.dumps(receipt), encoding="utf-8")

    logs = proj / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    with (logs / "run_ping.jsonl").open("w", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "run_start", "macro": "ping", "run_id": "run-ping", "ts": 1.0, "macro_proof_contract": summarize_macro_proof_contract(proj, "ping")}) + "\n")
        fh.write(json.dumps({"type": "run_end", "macro": "ping", "run_id": "run-ping", "ts": 2.0, "ok": True}) + "\n")

    res = runner.invoke(app, ["macro-author-loop-json", str(proj), "ping", "--no-pretty"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.stdout)

    assert payload["execution"]["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert payload["execution"]["runtime_posture"]["id"] == "warm_dispatch_ready"
    assert payload["execution"]["runtime_posture"]["dispatch_safe_now"] is True
    assert payload["execution"]["dispatch_gate"]["decision"]["id"] == "dispatch_now"
    assert payload["execution"]["dispatch_gate"]["decision"]["command"] == "dispatch_macro_checked.sh ping"
    assert payload["execution"]["dispatch_gate"]["repair_action"]["id"] == "ready_to_dispatch"
    assert payload["execution"]["dispatch_gate"]["repair_action"]["command"] == "dispatch_macro_checked.sh ping"
    assert payload["execution"]["dispatch_gate"]["dispatch_readiness"]["can_emit_minimal_payload_now"] is True
    assert payload["execution"]["dispatch_gate"]["dispatch_contract"]["checked_dispatch_command"] == "dispatch_macro_checked.sh ping"
    assert payload["execution"]["dispatch_history"]["posture"]["id"] == "clean_recent_dispatch"
    assert payload["execution"]["dispatch_history"]["summary"]["latest_receipt"]["result"] == "emitted"
    assert payload["execution"]["preferred_entrypoints"]["warm_runtime"] == "dispatch_macro.sh ping"
    assert payload["execution"]["preferred_entrypoints"]["warm_runtime_gate"] == "macro_dispatch_gate_json.sh ping"
