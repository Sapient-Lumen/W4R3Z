from __future__ import annotations

from pathlib import Path
import copy
import json
import subprocess

import yaml
from typer.testing import CliRunner

from vhk.cli import app, _render_i3_stack_state_json_script, _render_i3_stack_state_script, _render_i3_stack_warm_runtime_ticket_script


runner = CliRunner()


def _make_project(tmp_path: Path) -> Path:
    proj = tmp_path / "p"
    (proj / "macros").mkdir(parents=True)

    (proj / "macros" / "sig.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "sig",
                "steps": [{"type": "Return", "value_expr": '"OK"', "out_var": "return_value"}],
            }
        )
    )

    (proj / "project.yaml").write_text(
        yaml.safe_dump(
            {
                "name": "p",
                "settings": {"event_log": False, "bus_socket": "bus.sock"},
                "bindings": [{"keys": "Mod4+Shift+S", "macro": "sig"}],
                "macros": {"sig": "macros/sig.yaml"},
                "bus_watchers": [{"name": "hotkeys", "event": "hotkey", "dispatch": True}],
            }
        )
    )
    return proj


def _write_json_stub(path: Path, payload: dict) -> None:
    path.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "cat <<'JSON'\n"
        f"{json.dumps(payload)}\n"
        "JSON\n"
    )
    path.chmod(0o755)


def _deep_merge(base: dict, overrides: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _base_helper_payloads(proj: Path) -> dict[str, dict]:
    acceptance_path = proj / "acceptance" / "macro_acceptance.yaml"
    return {
        "check_runtime_json.sh": {
            "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
            "env": {"session_ready": True},
            "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
            "capabilities": {"warm_runtime": True},
            "health": {"blockers": [], "warnings": []},
            "session_attachment": {"status": "ready", "commands": {"sync_activation_environment": "dbus-update-activation-environment --systemd DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS XDG_RUNTIME_DIR I3SOCK"}},
            "activation_environment": {"status": "in_sync"},
        },
        "status_runtime_json.sh": {
            "health": {"ready": True, "issues": []},
            "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"},
            "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}},
        },
        "latest_runtime_repair_json.sh": {"latest_runtime_repair": {"recent": False, "ok": True, "action": None, "receipt_status": None}},
        "latest_run_json.sh": {"latest_run": {"macro": "sig", "ok": True}},
        "latest_dispatch_json.sh": {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch", "recorded_at": "2026-03-22T14:50:00Z", "warm_runtime_evidence": {"status_id": "current_warm_runtime_evidence", "current": True, "summary": "The newest dispatch receipt is still current evidence for the resident warm path.", "recommended": {"command": "macro_dispatch_gate_json.sh sig"}, "followup": ["macro_dispatch_gate_json.sh sig", "dispatch_macro_checked.sh sig", "latest_dispatch_json.sh"]}}},
        "macro_latest_dispatch_json.sh": {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch", "recorded_at": "2026-03-22T14:50:00Z", "warm_runtime_evidence": {"status_id": "current_warm_runtime_evidence", "current": True, "summary": "The newest dispatch receipt is still current evidence for the resident warm path.", "recommended": {"command": "macro_dispatch_gate_json.sh sig"}, "followup": ["macro_dispatch_gate_json.sh sig", "dispatch_macro_checked.sh sig", "macro_latest_dispatch_json.sh sig"]}}},
        "latest_run_health_json.sh": {"health": {"verdict": "ok", "ready_to_iterate": True}},
        "macro_inventory_json.sh": {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]},
        "macro_entrypoints_json.sh": {
            "project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0},
            "macros": [
                {
                    "name": "sig",
                    "execution": {"preferred_mode": "warm_runtime_dispatch"},
                    "preferred_entrypoints": {
                        "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig",
                        "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig",
                        "direct_run": "./bin/run_macro.sh sig",
                        "record_runtime_acceptance": "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>",
                        "latest_run": "./bin/macro_latest_run_json.sh sig",
                        "latest_report": "./bin/macro_report_latest.sh sig",
                        "latest_trace": "./bin/macro_trace_latest.sh sig",
                        "author_loop": "./bin/macro_author_loop_json.sh sig",
                        "source": "./bin/macro_source_json.sh sig",
                        "contract": "./bin/macro_contract_json.sh sig",
                        "recording_review": "./bin/macro_recording_json.sh sig",
                        "latest_dispatch": "./bin/macro_latest_dispatch_json.sh sig",
                    },
                    "source": {"path": str(proj / "macros" / "sig.yaml"), "relative_path": "macros/sig.yaml", "exists": True, "format": "yaml"},
                }
            ],
        },
        "macro_author_queue_json.sh": {
            "summary": {"primary_macro_name": "sig"},
            "primary_macro": {"name": "sig"},
            "macros": [{"name": "sig"}],
        },
        "macro_dispatch_gate_json.sh": {
            "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"},
            "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"},
            "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None},
            "preferred_execution_mode": "warm_runtime_dispatch",
        },
        "macro_latest_run_json.sh": {
            "latest_run": {"macro": "sig", "run_id": "run-123", "ok": True},
            "latest_run_health": {"verdict": "healthy", "summary": "looks good"},
            "replay_posture": {"id": "verified_recent"},
            "next_step": {"id": "repeat_or_trace", "command": "./bin/macro_report_latest.sh sig"},
            "preferred_entrypoints": {
                "latest_run_json": "./bin/macro_latest_run_json.sh sig",
                "latest_report": "./bin/macro_report_latest.sh sig",
                "history": "./bin/history_runs.sh --macro sig --limit 5",
            },
        },
        "macro_contract_json.sh": {
            "macro": {"name": "sig", "source": {"path": str(proj / "macros" / "sig.yaml"), "relative_path": "macros/sig.yaml", "exists": True, "format": "yaml"}, "desktop_target": {"summary": "Firefox on workspace 2"}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}},
            "invocation": {
                "generated_stack": {
                    "dispatch_checked_wrapper": "./bin/dispatch_macro_checked.sh sig",
                    "report_latest_wrapper": "./bin/macro_report_latest.sh sig",
                    "trace_latest_wrapper": "./bin/macro_trace_latest.sh sig",
                    "latest_run_wrapper": "./bin/macro_latest_run_json.sh sig",
                    "author_loop_wrapper": "./bin/macro_author_loop_json.sh sig",
                    "latest_dispatch_wrapper": "./bin/macro_latest_dispatch_json.sh sig",
                    "source_wrapper": "./bin/macro_source_json.sh sig",
                    "recording_review_wrapper": "./bin/macro_recording_json.sh sig",
                    "contract_wrapper": "./bin/macro_contract_json.sh sig",
                }
            },
        },
        "macro_author_loop_json.sh": {
            "macro": {"name": "sig"},
            "source": {"path": str(proj / "macros" / "sig.yaml"), "relative_path": "macros/sig.yaml", "exists": True, "format": "yaml"},
            "execution": {
                "preferred_execution_mode": "warm_runtime_dispatch",
                "runtime_signoff": {"status": "accepted", "contract_status": "current"},
                "dispatch_gate": {"dispatch_readiness": {"can_emit_minimal_payload_now": True}},
                "preferred_entrypoints": {
                    "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig",
                    "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig",
                    "direct_run": "./bin/run_macro.sh sig",
                    "record_runtime_acceptance": "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
                }
            },
            "llm_handoff": {"authoritative_inputs": ["macro_source_json", "macro_recording_json", "macro_contract_json"]},
            "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"},
        },
        "macro_recording_json.sh": {
            "macro": {"name": "sig"},
            "recording": {
                "exists": True,
                "has_recorded_context": True,
                "freshness": {"status": "current"},
                "selector_summary": {"selector_source_id": "macro_when", "exact_segment_count": 0, "title_segment_count": 0, "workspace_segment_count": 0},
                "transition_reason_counts": {"title": 0, "workspace": 0},
            },
            "review": {
                "commands": {
                    "record_shell": "./bin/record_macro.sh sig",
                    "cleanup_review_shell": "./bin/optimize_macro.sh sig",
                    "cleanup_apply_shell": "./bin/apply_optimize_macro.sh sig",
                },
                "generated_stack": {
                    "record": "./bin/record_macro.sh sig",
                    "recording_review": "./bin/macro_recording_json.sh sig",
                    "cleanup_review": "./bin/optimize_macro.sh sig",
                    "cleanup_apply": "./bin/apply_optimize_macro.sh sig",
                },
            },
        },
        "macro_replay_board_json.sh": {
            "summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}},
            "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}},
            "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}, "latest_run": {"run_id": "run-123"}, "latest_run_health": {"verdict": "healthy"}}],
        },
        "macro_runtime_board_json.sh": {
            "summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}},
            "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "accepted", "matches_current_posture": True, "matches_current_contract": True, "contract_status": "current", "posture_id": "warm_dispatch_ready", "current_proof_contract": {"digest": "proof-123"}, "current_proof_contract_digest": "proof-123", "proof_contract_digest": "proof-123"}}},
            "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "accepted", "matches_current_posture": True, "matches_current_contract": True, "contract_status": "current", "posture_id": "warm_dispatch_ready", "current_proof_contract": {"digest": "proof-123"}, "current_proof_contract_digest": "proof-123", "proof_contract_digest": "proof-123"}}}],
        },
        "macro_dispatch_history_board_json.sh": {
            "summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0},
            "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"result": "emitted", "route": "checked_dispatch"}}, "llm_workbench": {"source_id": "macro_dispatch_history_board.llm_workbench", "source_command": "./bin/macro_dispatch_history_board_json.sh", "mode_id": "inspect_current_receipt_before_reemit", "recommended_command": "./bin/macro_latest_dispatch_json.sh sig"}},
            "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}, "llm_workbench": {"source_id": "macro_dispatch_history_board.llm_workbench", "source_command": "./bin/macro_dispatch_history_board_json.sh", "mode_id": "inspect_current_receipt_before_reemit", "recommended_command": "./bin/macro_latest_dispatch_json.sh sig"}}],
        },
        "macro_dispatch_catalog_json.sh": {
            "runtime": {"bus_event": "hotkey"},
            "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1},
            "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"route": "checked_dispatch"}},
            "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"route": "checked_dispatch", "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig"}}],
        },
        "macro_acceptance_ledger_json.sh": {
            "ledger_source": {"path": str(acceptance_path), "relative_path": "acceptance/macro_acceptance.yaml", "exists": True, "format": "yaml"},
            "summary": {"accepted_macro_count": 1, "review_acceptance_macro_count": 0, "runtime_acceptance_macro_count": 1},
            "macros": [{"name": "sig", "review_acceptances": [], "accepted_review_issue_codes": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "warm_dispatch_ready"}}],
        },
        "macro_review_queue_json.sh": {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []},
        "next_action_json.sh": {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "recommendation_trace": {"selected_action_id": "dispatch_now"}},
        "startup_handoff_status_json.sh": {"startup_handoff": {"verdict": "primary_owner_ready", "autostart": {"state": "hidden"}, "counts": {"enabled_unit_count": 1}}},
        "startup_handoff_drift_json.sh": {"drift": {"verdict": "stable", "previous_verdict": "stable"}, "history": {"sample_count": 1}},
    }


def _generate_stack_payload(tmp_path: Path, *, overrides: dict[str, dict]) -> tuple[dict, str]:
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    helper_payloads = _base_helper_payloads(proj)
    for name, override in overrides.items():
        helper_payloads[name] = _deep_merge(helper_payloads.get(name, {}), override)

    bin_dir = out_dir / "bin"
    for name, payload in helper_payloads.items():
        _write_json_stub(bin_dir / name, payload)

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    return payload, summary


def test_primary_macro_work_ticket_prefers_recording_before_other_lanes(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "macro_recording_json.sh": {
                "recording": {"freshness": {"status": "stale"}, "has_recorded_context": False},
            },
            "macro_review_queue_json.sh": {
                "counts": {"needs_review_count": 1},
                "queue": {"stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}]},
                "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}],
            },
            "macro_acceptance_ledger_json.sh": {
                "summary": {"accepted_macro_count": 0, "review_acceptance_macro_count": 0, "runtime_acceptance_macro_count": 0},
                "macros": [],
            },
            "macro_runtime_board_json.sh": {
                "primary_macro": {"acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}},
                "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}}],
            },
            "next_action_json.sh": {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}},
        },
    )

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "recording"
    assert ticket["source_ticket_id"] == "primary_macro_recording_ticket"
    assert ticket["status_id"] == "record_first"
    assert ticket["recommended"]["command"] == "./bin/record_macro.sh sig"
    assert ticket["llm_workbench"]["mode_id"] == "capture_recording_context"
    assert ticket["llm_workbench"]["recommended_command"] == "./bin/record_macro.sh sig"
    assert ticket["llm_workbench"]["inspect_first"][0] == "./bin/macro_recording_json.sh sig"
    assert ticket["llm_workbench"]["edit_loop"]["source"] == "./bin/macro_source_json.sh sig"
    assert "recording review" in ticket["llm_workbench"]["stop_condition"].lower()
    transition = ticket["lane_transition"]
    assert transition["transition_id"] == "capture_recording_then_return_to_yaml"
    assert transition["current_lane_id"] == "capture_recording"
    assert transition["next_actuation_kind"] == "capture_recording"
    assert transition["next_actuation_command"] == "./bin/record_macro.sh sig"
    assert transition["barrier_ids"] == ["recording_review_debt"]
    assert ticket["llm_workbench"]["lane_transition"]["transition_id"] == "capture_recording_then_return_to_yaml"
    stage_completion = ticket["stage_completion"]
    assert stage_completion["completion_id"] == "recording_context_current"
    assert stage_completion["completion_command"] == "./bin/record_macro.sh sig"
    assert ticket["llm_workbench"]["stage_completion"]["completion_id"] == "recording_context_current"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_work_ticket_stage_id"] == "recording"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_work_ticket_status_id"] == "record_first"
    assert "primary_macro_work_ticket_stage=recording" in summary
    assert "primary_macro_work_ticket_llm_mode=capture_recording_context" in summary
    assert "primary_macro_work_ticket_command=./bin/record_macro.sh sig" in summary


def test_primary_macro_work_ticket_prefers_acceptance_after_proof_is_current(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "macro_acceptance_ledger_json.sh": {
                "summary": {"accepted_macro_count": 1, "review_acceptance_macro_count": 1, "runtime_acceptance_macro_count": 0},
                "macros": [{"name": "sig", "review_acceptances": [{"issue_code": "exact_recording_segments", "signoff_complete": True}], "accepted_review_issue_codes": ["exact_recording_segments"], "incomplete_review_issue_codes": [], "runtime_acceptance": None}],
            },
            "macro_runtime_board_json.sh": {
                "primary_macro": {"acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}},
                "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}}],
            },
        },
    )

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "acceptance"
    assert ticket["source_ticket_id"] == "primary_macro_acceptance_ticket"
    assert ticket["status_id"] == "ready_for_signoff"
    assert ticket["recommended"]["command"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
    stage_completion = ticket["stage_completion"]
    assert stage_completion["completion_id"] == "runtime_signoff_current"
    assert stage_completion["completion_command"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
    assert ticket["llm_workbench"]["stage_completion"]["completion_id"] == "runtime_signoff_current"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_work_ticket_stage_id"] == "acceptance"
    assert "primary_macro_work_ticket_stage=acceptance" in summary
    assert "primary_macro_work_ticket_status=ready_for_signoff" in summary




def test_compact_resident_tickets_carry_inline_selected_handoff_contract(tmp_path: Path):
    payload, _ = _generate_stack_payload(tmp_path, overrides={})

    warm_contract = payload["warm_runtime_ticket"]["contract"]["selected_handoff_projection"]
    assert warm_contract["field_path"] == "warm_runtime_ticket.selected_macro_handoff"
    assert warm_contract["projection_rule"] == "preserve_selected_macro_receipt_runtime_signoff_contract"
    assert "execution_cutover_id" in warm_contract["projected_fields"]["execution_cutover"]
    assert "runtime_handoff_id" in warm_contract["projected_fields"]["selected_macro_handoff"]

    work_contract = payload["primary_macro_work_ticket"]["contract"]["selected_handoff_projection"]
    assert work_contract["field_path"] == "primary_macro_work_ticket.selected_macro_handoff"
    assert work_contract["projection_rule"] == "preserve_selected_macro_receipt_runtime_signoff_contract"
    assert "execution_ticket_handoff.command" in work_contract["projected_fields"]["execution_ticket_handoff"]
    assert "signoff_ready" in work_contract["projected_fields"]["execution_cutover"]

def test_primary_macro_work_ticket_prefers_runtime_repair_before_checked_dispatch(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "check_runtime_json.sh": {
                "session_attachment": {"status": "activation_environment_drift"},
                "activation_environment": {"status": "drift"},
            },
        },
    )

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "runtime"
    assert ticket["source_ticket_id"] == "warm_runtime_ticket"
    assert ticket["status_id"] == "warm_runtime_then_selected_macro"
    assert ticket["recommended"]["command"].startswith("dbus-update-activation-environment --systemd")
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_stage_id"] == "runtime"
    assert "primary_macro_work_ticket_stage=runtime" in summary
    assert "primary_macro_work_ticket_status=warm_runtime_then_selected_macro" in summary



def test_primary_macro_work_ticket_prefers_runtime_latency_attention_before_checked_dispatch(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "check_runtime_json.sh": {
                "dispatch_path_summary": {
                    "status": "ok",
                    "ok": True,
                    "env_in_sync": True,
                    "desktop_session_contract_in_sync": True,
                    "watchers_in_sync": True,
                    "runtime_contract_in_sync": True,
                    "roundtrip_latency_ms": 91.4,
                    "latency_budget_ms": 60.0,
                    "latency_status": "over_budget",
                    "latency_within_budget": False,
                },
            },
        },
    )

    runtime_ticket = payload["warm_runtime_ticket"]
    assert runtime_ticket["status_id"] == "inspect_runtime_latency"
    assert runtime_ticket["route_id"] == "probe_latency_then_dispatch"
    assert runtime_ticket["recommended"]["command"] == "./bin/check_runtime_json.sh"
    assert runtime_ticket["signals"]["dispatch_path_probe_latency_status"] == "over_budget"
    assert runtime_ticket["signals"]["dispatch_path_probe_latency_ms"] == 91.4
    assert runtime_ticket["signals"]["dispatch_path_probe_latency_budget_ms"] == 60.0

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "runtime"
    assert ticket["source_ticket_id"] == "warm_runtime_ticket"
    assert ticket["status_id"] == "warm_runtime_then_selected_macro"
    assert ticket["recommended"]["command"] == "./bin/check_runtime_json.sh"
    assert ticket["execution_handoff"]["warm_runtime_probe_latency_status"] == "over_budget"
    assert ticket["execution_handoff"]["warm_runtime_probe_latency_ms"] == 91.4
    assert ticket["execution_handoff"]["warm_runtime_probe_latency_budget_ms"] == 60.0
    assert ticket["execution_handoff"]["latency_attention_required"] is True
    assert ticket["execution_handoff"]["inspect_runtime_latency_command"] == "./bin/check_runtime_json.sh"
    assert "warm_runtime_ticket_probe_latency_status=over_budget" in summary
    assert "primary_macro_work_ticket_warm_runtime_probe_latency_status=over_budget" in summary
    assert "primary_macro_work_ticket_latency_attention_required=True" in summary


def test_primary_macro_work_ticket_prefers_probe_observation_before_generic_execution(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "latest_dispatch_json.sh": {
                "latest_dispatch": {
                    "macro": "sig",
                    "result": "blocked",
                    "route": "checked_dispatch",
                    "warm_runtime_evidence": {
                        "status_id": "runtime_probe_status_drift",
                        "current": False,
                        "summary": "The newest receipt no longer matches the daemon's current probe posture.",
                        "recommended": {"command": "warm_runtime_ticket.sh"},
                    },
                }
            },
            "macro_dispatch_gate_json.sh": {
                "decision": {"id": "inspect_before_dispatch", "command": "./bin/macro_report_latest.sh sig"},
                "repair_action": {
                    "id": "inspect_live_desktop_target",
                    "command": "./bin/macro_report_latest.sh sig",
                    "source_blocker_class_id": "desktop_state_mismatch",
                },
                "dispatch_readiness": {
                    "can_emit_minimal_payload_now": False,
                    "primary_blocker_class_id": "desktop_state_mismatch",
                    "desktop_target": {
                        "selector_source_id": "macro_when",
                        "selector": {"class": "Alacritty", "workspace": "2"},
                        "summary": "Warm dispatch expects the macro's explicit when: selector to match the focused X11/i3 target.",
                    },
                    "live_probe_hint": {
                        "id": "window_event_probe",
                        "summary": "Latest matching run failed around `WaitForWindowEvent`, after `window_event` waits x2.",
                        "step_type": "WaitForWindowEvent",
                        "wait_kind": "window_event",
                        "wait_count": 2,
                        "observation": {
                            "source_id": "wait_attempt",
                            "summary": "Latest matching run preserved a failed live wait observation (matched=False, workspace=2, wm=i3, event=focus).",
                            "observed": {"matched": False, "workspace": "2", "wm": "i3", "event": "focus", "selector": {"class": "Alacritty", "workspace": "2"}},
                        },
                    },
                },
            },
            "macro_latest_run_json.sh": {
                "latest_run_health": {
                    "verdict": "healthy",
                    "summary": "looks good",
                },
                "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"},
            },
        },
    )

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "probe"
    assert ticket["source_ticket_id"] == "primary_macro_probe_observation"
    assert ticket["status_id"] == "observation_available"
    assert ticket["route_id"] == "inspect_live_probe_before_execution"
    assert ticket["recommended"]["command"] == "./bin/macro_report_latest.sh sig"
    assert ticket["probe_handoff"]["status_id"] == "observation_available"
    assert ticket["probe_handoff"]["probe_id"] == "window_event_probe"
    assert ticket["probe_handoff"]["recommended_command"] == "./bin/macro_report_latest.sh sig"
    assert ticket["probe_handoff"]["observed"]["workspace"] == "2"
    assert ticket["probe_handoff"]["blocker_class_id"] == "desktop_state_mismatch"
    assert ticket["target_handoff"]["status_id"] == "target_contract_mismatch_observed"
    assert ticket["target_handoff"]["proof_family"] == "selector_plus_live_probe"
    assert ticket["target_handoff"]["match_verdict"] == "mismatch"
    assert ticket["target_handoff"]["recommended_command"] == "./bin/macro_report_latest.sh sig"
    assert ticket["contract"]["target_handoff_projection"]["projection_rule"] == "preserve_x11_i3_target_authority_handoff"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_probe_status_id"] == "observation_available"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_target_status_id"] == "target_contract_mismatch_observed"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_probe_command"] == "./bin/macro_report_latest.sh sig"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_target_command"] == "./bin/macro_report_latest.sh sig"
    assert "primary_macro_work_ticket_stage=probe" in summary
    assert "primary_macro_work_ticket_status=observation_available" in summary
    assert "primary_macro_work_ticket_probe_status=observation_available" in summary
    assert "primary_macro_work_ticket_probe_command=./bin/macro_report_latest.sh sig" in summary
    assert "primary_macro_work_ticket_target_status=target_contract_mismatch_observed" in summary
    assert "primary_macro_work_ticket_target_command=./bin/macro_report_latest.sh sig" in summary


def test_primary_macro_work_ticket_prefers_stale_dispatch_receipt_before_generic_execution(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "latest_dispatch_json.sh": {
                "latest_dispatch": {
                    "macro": "sig",
                    "result": "blocked",
                    "route": "checked_dispatch",
                    "recorded_at": "2026-03-22T15:05:00Z",
                    "warm_runtime_evidence": {
                        "status_id": "repair_runtime_before_reusing_receipt",
                        "current": False,
                        "summary": "The newest dispatch receipt is no longer current warm-runtime evidence on this resident lane.",
                        "reason": "The resident runtime witness changed after the newest receipt, so inspect that receipt before retrying warm dispatch.",
                        "recommended": {"command": "warm_runtime_ticket.sh"},
                        "followup": ["warm_runtime_ticket.sh", "macro_dispatch_gate_json.sh sig", "dispatch_macro_checked.sh sig"],
                    },
                }
            },
            "macro_latest_dispatch_json.sh": {
                "latest_dispatch": {
                    "macro": "sig",
                    "result": "blocked",
                    "route": "checked_dispatch",
                    "recorded_at": "2026-03-22T15:05:00Z",
                    "warm_runtime_evidence": {
                        "status_id": "repair_runtime_before_reusing_receipt",
                        "current": False,
                        "summary": "The newest dispatch receipt is no longer current warm-runtime evidence on this resident lane.",
                        "reason": "The resident runtime witness changed after the newest receipt, so inspect that receipt before retrying warm dispatch.",
                        "recommended": {"command": "warm_runtime_ticket.sh"},
                        "followup": ["warm_runtime_ticket.sh", "macro_dispatch_gate_json.sh sig", "dispatch_macro_checked.sh sig"],
                    },
                }
            },
            "macro_dispatch_history_board_json.sh": {
                "summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1},
                "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}}, "llm_workbench": {"source_id": "macro_dispatch_history_board.llm_workbench", "source_command": "./bin/macro_dispatch_history_board_json.sh", "mode_id": "inspect_stale_dispatch_receipt", "recommended_command": "./bin/macro_latest_dispatch_json.sh sig"}},
                "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch", "unresolved_force_override": False}, "llm_workbench": {"source_id": "macro_dispatch_history_board.llm_workbench", "source_command": "./bin/macro_dispatch_history_board_json.sh", "mode_id": "inspect_stale_dispatch_receipt", "recommended_command": "./bin/macro_latest_dispatch_json.sh sig"}}],
            },
        },
    )

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "receipt"
    assert ticket["source_ticket_id"] == "primary_macro_latest_dispatch"
    assert ticket["status_id"] == "stale_dispatch_evidence_available"
    assert ticket["route_id"] == "inspect_stale_dispatch_evidence_before_repair"
    assert ticket["recommended"]["command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["latest_dispatch_handoff"]["scope_id"] == "selected_macro_latest_dispatch"
    assert ticket["latest_dispatch_handoff"]["scope_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["latest_dispatch_handoff"]["status_id"] == "repair_runtime_before_reusing_receipt"
    assert ticket["latest_dispatch_handoff"]["current"] is False
    assert ticket["latest_dispatch_handoff"]["recommended_command"] == "warm_runtime_ticket.sh"
    assert ticket["dispatch_history_workbench"]["mode_id"] == "inspect_stale_dispatch_receipt"
    assert ticket["dispatch_history_workbench"]["recommended_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["selected_macro_handoff"]["source_kind"] == "dispatch_history_workbench"
    assert ticket["selected_macro_handoff"]["workbench_mode_id"] == "inspect_stale_dispatch_receipt"
    assert ticket["selected_macro_handoff"]["workbench_surface"] == "./bin/macro_dispatch_history_board_json.sh"
    assert ticket["selected_macro_handoff"]["command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_stage_id"] == "receipt"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_latest_dispatch_evidence_status_id"] == "repair_runtime_before_reusing_receipt"
    assert payload["primary_macro_latest_dispatch"]["warm_runtime_evidence_status_id"] == "repair_runtime_before_reusing_receipt"
    assert payload["primary_macro_latest_dispatch"]["warm_runtime_evidence_current"] is False
    assert payload["primary_macro_latest_dispatch"]["warm_runtime_evidence_command"] == "warm_runtime_ticket.sh"
    assert "primary_macro_work_ticket_stage=receipt" in summary
    assert "primary_macro_work_ticket_status=stale_dispatch_evidence_available" in summary
    assert "primary_macro_work_ticket_latest_dispatch_evidence_status=repair_runtime_before_reusing_receipt" in summary
    assert "primary_macro_work_ticket_latest_dispatch_scope=selected_macro_latest_dispatch" in summary
    assert "primary_macro_work_ticket_latest_dispatch_scope_command=./bin/macro_latest_dispatch_json.sh sig" in summary
    assert "primary_macro_work_ticket_latest_dispatch_command=warm_runtime_ticket.sh" in summary
    assert "primary_macro_work_ticket_dispatch_history_mode=inspect_stale_dispatch_receipt" in summary
    assert "primary_macro_work_ticket_selected_handoff_source=dispatch_history_workbench" in summary
    assert "primary_macro_work_ticket_selected_handoff_mode=inspect_stale_dispatch_receipt" in summary
    assert "primary_macro_work_ticket_selected_handoff_surface=./bin/macro_dispatch_history_board_json.sh" in summary
    assert "primary_macro_work_ticket_selected_handoff_command=./bin/macro_latest_dispatch_json.sh sig" in summary


def test_primary_macro_work_ticket_falls_through_to_execution_when_stack_is_clear(tmp_path: Path):
    payload, summary = _generate_stack_payload(tmp_path, overrides={})

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "execution"
    assert ticket["source_ticket_id"] == "primary_macro_execution_ticket"
    assert ticket["status_id"] == "current_dispatch_evidence_available"
    assert ticket["recommended"]["command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["editable_source"]["relative_path"] == "macros/sig.yaml"
    assert ticket["editable_source"]["format"] == "yaml"
    assert ticket["entrypoints"]["source"] == "./bin/macro_source_json.sh sig"
    assert ticket["entrypoints"]["author_loop"] == "./bin/macro_author_loop_json.sh sig"
    assert ticket["entrypoints"]["warm_runtime_checked"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["entrypoints"]["warm_runtime_gate"] == "./bin/macro_dispatch_gate_json.sh sig"
    assert ticket["entrypoints"]["direct_run"] == "./bin/run_macro.sh sig"
    assert ticket["entrypoints"]["record_runtime_acceptance"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
    assert ticket["entrypoints"]["latest_dispatch"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["llm_workbench"]["mode_id"] == "inspect_current_receipt_before_reemit"
    assert ticket["llm_workbench"]["recommended_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["llm_workbench"]["inspect_first"][0] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["llm_workbench"]["edit_loop"]["author_loop"] == "./bin/macro_author_loop_json.sh sig"
    assert ticket["llm_workbench"]["execute_when_clear"]["warm_runtime_checked"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["llm_workbench"]["execute_when_clear"]["latest_dispatch"] == "./bin/macro_latest_dispatch_json.sh sig"
    boundary = ticket["authoring_boundary"]
    assert boundary["policy_id"] == "macro_yaml_source_only"
    assert boundary["canonical_edit_surface"]["surface_class"] == "canonical_project_source"
    assert boundary["canonical_edit_surface"]["relative_path"] == "macros/sig.yaml"
    assert boundary["inspect_surfaces"]["author_loop"]["surface_class"] == "runtime_snapshot"
    assert boundary["inspect_surfaces"]["latest_dispatch"]["surface_class"] == "runtime_observability"
    assert boundary["actuation_surfaces"]["warm_runtime_checked"]["command"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["llm_workbench"]["authoring_boundary"]["canonical_edit_surface"]["command"] == "./bin/macro_source_json.sh sig"
    assert ticket["execution_handoff"]["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert ticket["execution_handoff"]["warm_runtime_ready_now"] is True
    assert ticket["execution_handoff"]["runtime_signoff_status"] == "accepted"
    assert ticket["latest_dispatch_handoff"]["scope_id"] == "selected_macro_latest_dispatch"
    assert ticket["latest_dispatch_handoff"]["scope_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["latest_dispatch_handoff"]["status_id"] == "current_warm_runtime_evidence"
    assert ticket["latest_dispatch_handoff"]["current"] is True
    assert ticket["latest_dispatch_handoff"]["result"] == "emitted"
    assert ticket["latest_dispatch_handoff"]["route"] == "checked_dispatch"
    assert ticket["latest_dispatch_handoff"]["recommended_command"] == "macro_dispatch_gate_json.sh sig"
    assert ticket["execution_ticket_handoff"]["source_kind"] == "dispatch_history_workbench"
    assert ticket["execution_ticket_handoff"]["workbench_mode_id"] == "inspect_current_receipt_before_reemit"
    assert ticket["execution_ticket_handoff"]["command"] == "./bin/macro_latest_dispatch_json.sh sig"
    transition = ticket["lane_transition"]
    assert transition["transition_id"] == "inspect_current_receipt_before_reemit"
    assert transition["current_lane_id"] == "inspect_evidence"
    assert transition["next_actuation_kind"] == "checked_warm_dispatch"
    assert transition["next_actuation_command"] == "./bin/dispatch_macro_checked.sh sig"
    assert transition["barrier_ids"] == ["current_receipt_attention"]
    assert ticket["llm_workbench"]["lane_transition"]["transition_id"] == "inspect_current_receipt_before_reemit"
    stage_completion = ticket["stage_completion"]
    assert stage_completion["completion_id"] == "receipt_disposition_explicit"
    assert stage_completion["completion_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["llm_workbench"]["stage_completion"]["completion_id"] == "receipt_disposition_explicit"
    assert ticket["desktop_target_summary"] == "Firefox on workspace 2"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_stage_id"] == "execution"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_execution_handoff_source_kind"] == "dispatch_history_workbench"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_execution_handoff_workbench_mode_id"] == "inspect_current_receipt_before_reemit"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_execution_handoff_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_transition_id"] == "inspect_current_receipt_before_reemit"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_transition_lane_id"] == "inspect_evidence"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_next_actuation_kind"] == "checked_warm_dispatch"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_next_actuation_command"] == "./bin/dispatch_macro_checked.sh sig"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_transition_id"] == "inspect_current_receipt_before_reemit"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_transition_lane_id"] == "inspect_evidence"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_next_actuation_kind"] == "checked_warm_dispatch"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_next_actuation_command"] == "./bin/dispatch_macro_checked.sh sig"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_macro_work_ticket_latest_dispatch_evidence_status_id"] == "current_warm_runtime_evidence"
    assert payload["primary_macro_latest_dispatch"]["warm_runtime_evidence_status_id"] == "current_warm_runtime_evidence"
    assert payload["primary_macro_latest_dispatch"]["warm_runtime_evidence_command"] == "macro_dispatch_gate_json.sh sig"
    assert "primary_macro_work_ticket_stage=execution" in summary
    assert "primary_macro_work_ticket_status=current_dispatch_evidence_available" in summary
    assert "editable_source_relative_path=macros/sig.yaml" in summary
    assert "source_command=./bin/macro_source_json.sh sig" in summary
    assert "warm_runtime_checked_command=./bin/dispatch_macro_checked.sh sig" in summary
    assert "direct_run_command=./bin/run_macro.sh sig" in summary
    assert "record_runtime_acceptance_command=./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>" in summary
    assert "primary_macro_work_ticket_llm_mode=inspect_current_receipt_before_reemit" in summary
    assert "primary_macro_work_ticket_llm_recommended_command=./bin/macro_latest_dispatch_json.sh sig" in summary
    assert "primary_macro_work_ticket_transition=inspect_current_receipt_before_reemit" in summary
    assert "primary_macro_work_ticket_transition_lane=inspect_evidence" in summary
    assert "primary_macro_work_ticket_next_actuation_kind=checked_warm_dispatch" in summary
    assert "primary_macro_work_ticket_next_actuation_command=./bin/dispatch_macro_checked.sh sig" in summary
    assert "primary_macro_work_ticket_preferred_execution_mode=warm_runtime_dispatch" in summary
    assert "primary_macro_work_ticket_latest_dispatch_evidence_status=current_warm_runtime_evidence" in summary
    assert "primary_macro_work_ticket_latest_dispatch_scope=selected_macro_latest_dispatch" in summary
    assert "primary_macro_work_ticket_latest_dispatch_scope_command=./bin/macro_latest_dispatch_json.sh sig" in summary
    assert "primary_macro_work_ticket_latest_dispatch_command=macro_dispatch_gate_json.sh sig" in summary
    assert "primary_macro_work_ticket_execution_handoff_source=dispatch_history_workbench" in summary
    assert "primary_macro_work_ticket_execution_handoff_mode=inspect_current_receipt_before_reemit" in summary
    assert "primary_macro_work_ticket_execution_handoff_surface=./bin/macro_dispatch_history_board_json.sh" in summary
    assert "primary_macro_work_ticket_execution_handoff_command=./bin/macro_latest_dispatch_json.sh sig" in summary


def test_primary_macro_work_ticket_prefers_selected_macro_receipt_when_global_latest_receipt_is_for_another_macro(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "latest_dispatch_json.sh": {
                "latest_dispatch": {
                    "macro": "other",
                    "result": "emitted",
                    "route": "checked_dispatch",
                    "warm_runtime_evidence": {
                        "status_id": "current_warm_runtime_evidence",
                        "current": True,
                        "recommended": {"command": "macro_dispatch_gate_json.sh other"},
                    },
                }
            }
        },
    )

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["source_ticket_id"] == "primary_macro_latest_dispatch"
    assert ticket["status_id"] == "current_dispatch_evidence_available"
    assert ticket["recommended"]["command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["latest_dispatch_handoff"]["scope_id"] == "selected_macro_latest_dispatch"
    assert ticket["latest_dispatch_handoff"]["scope_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert ticket["latest_dispatch_handoff"]["status_id"] == "current_warm_runtime_evidence"
    assert ticket["latest_dispatch_handoff"]["current"] is True
    assert payload["primary_macro_latest_dispatch"]["warm_runtime_evidence_status_id"] == "current_warm_runtime_evidence"
    assert payload["sources"]["helpers"]["next_action_json"].get("selected_macro_work_ticket_latest_dispatch_evidence_status_id") == "current_warm_runtime_evidence"
    assert "primary_macro_work_ticket_status=current_dispatch_evidence_available" in summary


def test_primary_macro_work_ticket_helper_extracts_selected_macro_ticket(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    helper_payloads = _base_helper_payloads(proj)
    helper_payloads["macro_acceptance_ledger_json.sh"] = _deep_merge(
        helper_payloads["macro_acceptance_ledger_json.sh"],
        {
            "summary": {"accepted_macro_count": 1, "review_acceptance_macro_count": 1, "runtime_acceptance_macro_count": 0},
            "macros": [{"name": "sig", "review_acceptances": [{"issue_code": "exact_recording_segments", "signoff_complete": True}], "accepted_review_issue_codes": ["exact_recording_segments"], "incomplete_review_issue_codes": [], "runtime_acceptance": None}],
        },
    )
    helper_payloads["macro_runtime_board_json.sh"] = _deep_merge(
        helper_payloads["macro_runtime_board_json.sh"],
        {
            "primary_macro": {"acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}},
            "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}}],
        },
    )
    bin_dir = out_dir / "bin"
    for name, payload in helper_payloads.items():
        _write_json_stub(bin_dir / name, payload)

    payload = json.loads(subprocess.check_output([str(bin_dir / "primary_macro_work_ticket_json.sh")], text=True))
    assert payload["stack_kind"] == "vhk.i3_x11.primary_macro_work_ticket"
    assert payload["selected_macro_name"] == "sig"
    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "acceptance"
    assert ticket["status_id"] == "ready_for_signoff"
    assert ticket["editable_source"]["relative_path"] == "macros/sig.yaml"
    assert ticket["entrypoints"]["author_loop"] == "./bin/macro_author_loop_json.sh sig"
    assert ticket["entrypoints"]["record_runtime_acceptance"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
    assert ticket["latest_dispatch_handoff"]["status_id"] == "current_warm_runtime_evidence"
    assert ticket["latest_dispatch_handoff"]["recommended_command"] == "macro_dispatch_gate_json.sh sig"
    assert ticket["execution_handoff"]["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert ticket["llm_workbench"]["mode_id"] == "record_runtime_signoff"
    assert ticket["llm_workbench"]["recommended_command"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
    assert ticket["stage_completion"]["completion_id"] == "runtime_signoff_current"
    assert ticket["stage_completion"]["completion_command"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
    assert ticket["recommended"]["command"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"

    summary = subprocess.check_output([str(bin_dir / "primary_macro_work_ticket.sh")], text=True)
    assert "stage_id=acceptance" in summary
    assert "editable_source_relative_path=macros/sig.yaml" in summary
    assert "author_loop_command=./bin/macro_author_loop_json.sh sig" in summary
    assert "record_runtime_acceptance_command=./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>" in summary
    assert "preferred_execution_mode=warm_runtime_dispatch" in summary
    assert "llm_mode=record_runtime_signoff" in summary
    assert "llm_recommended_command=./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>" in summary
    assert "next command: ./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>" in summary
    assert "selected_handoff_projection_field_path=primary_macro_work_ticket.selected_macro_handoff" in summary
    assert "selected_handoff_projection_rule=preserve_selected_macro_receipt_runtime_signoff_contract" in summary
    assert "selected_handoff_projection_execution_ticket_handoff_fields=execution_ticket_handoff.source_kind,execution_ticket_handoff.workbench_mode_id,execution_ticket_handoff.workbench_surface,execution_ticket_handoff.command" in summary


def test_warm_runtime_ticket_helper_extracts_runtime_repair_ticket(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    helper_payloads = _base_helper_payloads(proj)
    helper_payloads["check_runtime_json.sh"] = _deep_merge(
        helper_payloads["check_runtime_json.sh"],
        {
            "dispatch_path_summary": {
                "status": "ok",
                "ok": True,
                "env_in_sync": True,
                "desktop_session_contract_in_sync": False,
                "daemon_desktop_session_contract_status": {"status": "drifted", "reasons": ["DISPLAY differs"]},
                "watchers_in_sync": True,
                "runtime_contract_in_sync": True,
            }
        },
    )
    helper_payloads["next_action_json.sh"] = {"primary_action": {"id": "inspect_runtime", "command": "./bin/check_runtime_json.sh"}, "recommendation_trace": {"selected_action_id": "inspect_runtime"}}
    bin_dir = out_dir / "bin"
    for name, payload in helper_payloads.items():
        _write_json_stub(bin_dir / name, payload)

    payload = json.loads(subprocess.check_output([str(bin_dir / "warm_runtime_ticket_json.sh")], text=True))
    assert payload["stack_kind"] == "vhk.i3_x11.warm_runtime_ticket"
    ticket = payload["warm_runtime_ticket"]
    assert ticket["status_id"] == "restart_runtime_for_daemon_desktop_session"
    assert ticket["recommended"]["command"] == "./bin/restart_runtime_json.sh"

    summary = subprocess.check_output([str(bin_dir / "warm_runtime_ticket.sh")], text=True)
    assert "status_id=restart_runtime_for_daemon_desktop_session" in summary
    assert "next command: ./bin/restart_runtime_json.sh" in summary
    assert "selected_handoff_projection_field_path=warm_runtime_ticket.selected_macro_handoff" in summary
    assert "selected_handoff_projection_rule=preserve_selected_macro_receipt_runtime_signoff_contract" in summary
    assert "selected_handoff_projection_execution_cutover_fields=execution_cutover_id,execution_cutover_command,receipt_disposition_required,signoff_ready,repair_required,redundant_resident_dispatch_risk,clean_replacement_required" in summary


def test_warm_runtime_ticket_helper_projects_primary_macro_llm_workbench(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_runtime_ticket_llm"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    helper_payloads = _base_helper_payloads(proj)
    helper_payloads["macro_author_loop_json.sh"] = _deep_merge(
        helper_payloads["macro_author_loop_json.sh"],
        {
            "llm_workbench": {
                "mode_id": "inspect_current_receipt_before_reemit",
                "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
                "inspect_first": ["./bin/macro_latest_dispatch_json.sh sig"],
            }
        },
    )
    helper_payloads["macro_runtime_board_json.sh"] = _deep_merge(
        helper_payloads["macro_runtime_board_json.sh"],
        {
            "summary": {
                "primary_llm_workbench_source_id": "macro_author_loop.llm_workbench",
                "primary_llm_workbench_mode_id": "inspect_current_receipt_before_reemit",
                "primary_llm_workbench_command": "./bin/macro_latest_dispatch_json.sh sig",
                "primary_llm_workbench_surface": "./bin/macro_author_loop_json.sh sig",
            },
            "primary_macro_llm_workbench": {
                "macro_name": "sig",
                "source_id": "macro_author_loop.llm_workbench",
                "source_command": "./bin/macro_author_loop_json.sh sig",
                "mode_id": "inspect_current_receipt_before_reemit",
                "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
            },
            "primary_macro": {
                "llm_workbench": {
                    "macro_name": "sig",
                    "source_id": "macro_author_loop.llm_workbench",
                    "source_command": "./bin/macro_author_loop_json.sh sig",
                    "mode_id": "inspect_current_receipt_before_reemit",
                    "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
                }
            },
            "macros": [
                {
                    "name": "sig",
                    "runtime_posture": {"id": "warm_dispatch_ready"},
                    "runtime_handoff": {"id": "inspect_receipt_lane", "command": "./bin/macro_latest_dispatch_json.sh sig"},
                    "llm_workbench": {
                        "macro_name": "sig",
                        "source_id": "macro_author_loop.llm_workbench",
                        "source_command": "./bin/macro_author_loop_json.sh sig",
                        "mode_id": "inspect_current_receipt_before_reemit",
                        "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
                    },
                }
            ],
        },
    )
    helper_payloads["next_action_json.sh"] = _deep_merge(
        helper_payloads["next_action_json.sh"],
        {
            "primary_macro_llm_workbench": {
                "source_id": "primary_macro_author_loop.llm_workbench",
                "source_helper": "macro_author_loop_json",
                "source_command": "./bin/macro_author_loop_json.sh sig",
                "mode_id": "inspect_current_receipt_before_reemit",
                "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
            },
            "recommendation_trace": {
                "selected_llm_workbench_source_id": "primary_macro_author_loop.llm_workbench",
                "selected_llm_workbench_mode_id": "inspect_current_receipt_before_reemit",
                "selected_llm_workbench_command": "./bin/macro_latest_dispatch_json.sh sig",
            },
        },
    )
    helper_payloads["macro_dispatch_history_board_json.sh"] = _deep_merge(
        helper_payloads["macro_dispatch_history_board_json.sh"],
        {
            "summary": {
                "primary_llm_workbench_source_id": "macro_dispatch_history_board.llm_workbench",
                "primary_llm_workbench_mode_id": "inspect_current_receipt_before_reemit",
                "primary_llm_workbench_command": "./bin/macro_latest_dispatch_json.sh sig",
                "primary_llm_workbench_surface": "./bin/macro_dispatch_history_board_json.sh",
            },
            "primary_macro_llm_workbench": {
                "macro_name": "sig",
                "source_id": "macro_dispatch_history_board.llm_workbench",
                "source_command": "./bin/macro_dispatch_history_board_json.sh",
                "mode_id": "inspect_current_receipt_before_reemit",
                "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
            },
            "primary_macro": {
                "name": "sig",
                "dispatch_history_posture": {"id": "dispatch_clean_recently"},
                "dispatch_history": {"latest_receipt": {"result": "emitted", "route": "checked_dispatch"}},
                "llm_workbench": {
                    "macro_name": "sig",
                    "source_id": "macro_dispatch_history_board.llm_workbench",
                    "source_command": "./bin/macro_dispatch_history_board_json.sh",
                    "mode_id": "inspect_current_receipt_before_reemit",
                    "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
                },
            },
            "macros": [
                {
                    "name": "sig",
                    "dispatch_history_posture": {"id": "dispatch_clean_recently"},
                    "dispatch_history": {"latest_receipt": {"result": "emitted", "route": "checked_dispatch"}},
                    "llm_workbench": {
                        "macro_name": "sig",
                        "source_id": "macro_dispatch_history_board.llm_workbench",
                        "source_command": "./bin/macro_dispatch_history_board_json.sh",
                        "mode_id": "inspect_current_receipt_before_reemit",
                        "recommended_command": "./bin/macro_latest_dispatch_json.sh sig",
                    },
                }
            ],
        },
    )
    bin_dir = out_dir / "bin"
    for name, payload in helper_payloads.items():
        _write_json_stub(bin_dir / name, payload)

    payload = json.loads(subprocess.check_output([str(bin_dir / "warm_runtime_ticket_json.sh")], text=True))
    workbench = payload["primary_macro_llm_workbench"]
    assert workbench["source_id"] == "primary_macro_author_loop.llm_workbench"
    assert workbench["mode_id"] == "inspect_current_receipt_before_reemit"
    assert workbench["recommended_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert workbench["source_command"] == "./bin/macro_author_loop_json.sh sig"
    assert payload["primary_macro_runtime_board"]["llm_workbench"]["mode_id"] == "inspect_current_receipt_before_reemit"
    dispatch_history_workbench = payload["primary_macro_dispatch_history_workbench"]
    assert dispatch_history_workbench["source_id"] == "macro_dispatch_history_board.llm_workbench"
    assert dispatch_history_workbench["mode_id"] == "inspect_current_receipt_before_reemit"
    assert dispatch_history_workbench["recommended_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert payload["primary_macro_dispatch_history"]["llm_workbench"]["source_command"] == "./bin/macro_dispatch_history_board_json.sh"
    handoff = payload["warm_runtime_ticket"]["selected_macro_handoff"]
    assert handoff["source_kind"] == "dispatch_history_workbench"
    assert handoff["workbench_mode_id"] == "inspect_current_receipt_before_reemit"
    assert handoff["workbench_surface"] == "./bin/macro_dispatch_history_board_json.sh"
    assert handoff["command"] == "./bin/macro_latest_dispatch_json.sh sig"

    summary = subprocess.check_output([str(bin_dir / "warm_runtime_ticket.sh")], text=True)
    assert "primary_macro_llm_workbench_source=primary_macro_author_loop.llm_workbench" in summary
    assert "primary_macro_llm_workbench_mode=inspect_current_receipt_before_reemit" in summary
    assert "primary_macro_llm_workbench_command=./bin/macro_latest_dispatch_json.sh sig" in summary
    assert "primary_macro_llm_workbench_surface=./bin/macro_author_loop_json.sh sig" in summary
    assert "primary_macro_dispatch_history_workbench_source=macro_dispatch_history_board.llm_workbench" in summary
    assert "primary_macro_dispatch_history_workbench_mode=inspect_current_receipt_before_reemit" in summary
    assert "primary_macro_dispatch_history_workbench_command=./bin/macro_latest_dispatch_json.sh sig" in summary
    assert "primary_macro_dispatch_history_workbench_surface=./bin/macro_dispatch_history_board_json.sh" in summary
    assert "selected_macro_handoff_source=dispatch_history_workbench" in summary
    assert "selected_macro_handoff_mode=inspect_current_receipt_before_reemit" in summary
    assert "selected_macro_handoff_surface=./bin/macro_dispatch_history_board_json.sh" in summary
    assert "selected_macro_handoff_command=./bin/macro_latest_dispatch_json.sh sig" in summary


def test_rendered_warm_runtime_ticket_surfaces_expose_execution_ticket_fallback() -> None:
    state_json = _render_i3_stack_state_json_script(project_dir=Path("/tmp/project"), unit_base="vhk-i3-busd-hotkeys", vhk_cmd="python -m vhk")
    assert "selected_warm_runtime_ticket_handoff_selection_basis" in state_json
    assert "selected_warm_runtime_ticket_execution_handoff_source_kind" in state_json
    assert "selected_warm_runtime_ticket_execution_handoff_command" in state_json

    state_summary = _render_i3_stack_state_script(project_dir=Path("/tmp/project"))
    assert "warm_runtime_ticket_selected_macro_basis=" in state_summary
    assert "warm_runtime_ticket_execution_handoff_source=" in state_summary
    assert "warm_runtime_ticket_execution_handoff_command=" in state_summary

    warm_ticket = _render_i3_stack_warm_runtime_ticket_script(project_dir=Path("/tmp/project"))
    assert "selected_macro_handoff_basis=" in warm_ticket
    assert "execution_ticket_handoff_source=" in warm_ticket
    assert "execution_ticket_handoff_command=" in warm_ticket


def test_warm_runtime_ticket_helper_reports_probe_latency_attention(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_latency"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    helper_payloads = _base_helper_payloads(proj)
    helper_payloads["check_runtime_json.sh"] = _deep_merge(
        helper_payloads["check_runtime_json.sh"],
        {
            "dispatch_path_summary": {
                "status": "ok",
                "ok": True,
                "env_in_sync": True,
                "desktop_session_contract_in_sync": True,
                "daemon_desktop_session_contract_status": {"status": "in_sync", "reasons": []},
                "watchers_in_sync": True,
                "runtime_contract_in_sync": True,
                "roundtrip_latency_ms": 88.2,
                "latency_budget_ms": 60.0,
                "latency_status": "over_budget",
                "latency_within_budget": False,
            }
        },
    )
    bin_dir = out_dir / "bin"
    for name, payload in helper_payloads.items():
        _write_json_stub(bin_dir / name, payload)

    payload = json.loads(subprocess.check_output([str(bin_dir / "warm_runtime_ticket_json.sh")], text=True))
    ticket = payload["warm_runtime_ticket"]
    assert ticket["status_id"] == "inspect_runtime_latency"
    assert ticket["recommended"]["command"] == "./bin/check_runtime_json.sh"
    assert ticket["signals"]["dispatch_path_probe_latency_status"] == "over_budget"
    assert ticket["signals"]["dispatch_path_probe_latency_ms"] == 88.2
    assert ticket["signals"]["dispatch_path_probe_latency_budget_ms"] == 60.0

    summary = subprocess.check_output([str(bin_dir / "warm_runtime_ticket.sh")], text=True)
    assert "status_id=inspect_runtime_latency" in summary
    assert "dispatch_path_probe_latency_status=over_budget" in summary
    assert "dispatch_path_probe_latency_ms=88.2" in summary
    assert "dispatch_path_probe_latency_budget_ms=60.0" in summary
    assert "next command: ./bin/check_runtime_json.sh" in summary


def test_primary_macro_work_ticket_prefers_runtime_probe_refresh_before_checked_dispatch(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "check_runtime_json.sh": {
                "dispatch_path_summary": {
                    "status": "ok",
                    "ok": True,
                    "env_in_sync": True,
                    "desktop_session_contract_in_sync": True,
                    "watchers_in_sync": True,
                    "runtime_contract_in_sync": True,
                    "probe_freshness_status": "stale",
                    "probe_age_s": 120.0,
                    "probe_freshness_window_s": 45.0,
                    "roundtrip_latency_ms": 19.4,
                    "latency_budget_ms": 60.0,
                    "latency_status": "within_budget",
                    "latency_within_budget": True,
                },
            },
        },
    )

    runtime_ticket = payload["warm_runtime_ticket"]
    assert runtime_ticket["status_id"] == "refresh_runtime_probe"
    assert runtime_ticket["route_id"] == "probe_freshness_then_dispatch"
    assert runtime_ticket["recommended"]["command"] == "./bin/check_runtime_json.sh"
    assert runtime_ticket["signals"]["dispatch_path_probe_freshness_status"] == "stale"
    assert runtime_ticket["signals"]["dispatch_path_probe_age_s"] == 120.0
    assert runtime_ticket["signals"]["dispatch_path_probe_freshness_window_s"] == 45.0

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "runtime"
    assert ticket["source_ticket_id"] == "warm_runtime_ticket"
    assert ticket["status_id"] == "warm_runtime_then_selected_macro"
    assert ticket["recommended"]["command"] == "./bin/check_runtime_json.sh"
    assert ticket["execution_handoff"]["warm_runtime_probe_freshness_status"] == "stale"
    assert ticket["execution_handoff"]["warm_runtime_probe_age_s"] == 120.0
    assert ticket["execution_handoff"]["warm_runtime_probe_freshness_window_s"] == 45.0
    assert ticket["execution_handoff"]["refresh_probe_attention_required"] is True
    assert ticket["execution_handoff"]["refresh_runtime_probe_command"] == "./bin/check_runtime_json.sh"
    assert "warm_runtime_ticket_probe_freshness_status=stale" in summary
    assert "primary_macro_work_ticket_warm_runtime_probe_freshness_status=stale" in summary
    assert "primary_macro_work_ticket_refresh_probe_attention_required=True" in summary


def test_warm_runtime_ticket_helper_reports_probe_freshness_attention(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_probe_freshness"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    helper_payloads = _base_helper_payloads(proj)
    helper_payloads["check_runtime_json.sh"] = _deep_merge(
        helper_payloads["check_runtime_json.sh"],
        {
            "dispatch_path_summary": {
                "status": "ok",
                "ok": True,
                "env_in_sync": True,
                "desktop_session_contract_in_sync": True,
                "daemon_desktop_session_contract_status": {"status": "in_sync", "reasons": []},
                "watchers_in_sync": True,
                "runtime_contract_in_sync": True,
                "probe_freshness_status": "stale",
                "probe_age_s": 120.0,
                "probe_freshness_window_s": 45.0,
                "roundtrip_latency_ms": 18.0,
                "latency_budget_ms": 60.0,
                "latency_status": "within_budget",
                "latency_within_budget": True,
            }
        },
    )
    bin_dir = out_dir / "bin"
    for name, payload in helper_payloads.items():
        _write_json_stub(bin_dir / name, payload)

    payload = json.loads(subprocess.check_output([str(bin_dir / "warm_runtime_ticket_json.sh")], text=True))
    ticket = payload["warm_runtime_ticket"]
    assert ticket["status_id"] == "refresh_runtime_probe"
    assert ticket["recommended"]["command"] == "./bin/check_runtime_json.sh"
    assert ticket["signals"]["dispatch_path_probe_freshness_status"] == "stale"
    assert ticket["signals"]["dispatch_path_probe_age_s"] == 120.0
    assert ticket["signals"]["dispatch_path_probe_freshness_window_s"] == 45.0

    summary = subprocess.check_output([str(bin_dir / "warm_runtime_ticket.sh")], text=True)
    assert "status_id=refresh_runtime_probe" in summary
    assert "dispatch_path_probe_freshness_status=stale" in summary
    assert "dispatch_path_probe_age_s=120.0" in summary
    assert "dispatch_path_probe_freshness_window_s=45.0" in summary
    assert "next command: ./bin/check_runtime_json.sh" in summary


def test_primary_macro_work_ticket_prefers_runtime_board_handoff_before_generic_execution(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "macro_dispatch_gate_json.sh": {
                "decision": {"id": "inspect_before_dispatch", "command": "./bin/macro_dispatch_gate_json.sh sig"},
                "repair_action": {"id": None, "command": None, "summary": None, "reason": None},
                "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": None},
            },
            "macro_latest_run_json.sh": {
                "latest_run_health": {"verdict": "ok", "summary": "looks good"},
                "next_step": {"id": "dispatch_or_run", "command": "./bin/macro_author_loop_json.sh sig"},
            },
            "macro_runtime_board_json.sh": {
                "summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "primary_handoff_id": "checked_dispatch_ready", "primary_handoff_command": "./bin/dispatch_macro_checked.sh sig"},
                "primary_macro": {
                    "name": "sig",
                    "runtime_posture": {"id": "warm_dispatch_ready"},
                    "acceptance": {"runtime_signoff": {"status": "accepted", "matches_current_posture": True, "matches_current_contract": True, "contract_status": "current", "posture_id": "warm_dispatch_ready", "current_proof_contract": {"digest": "proof-123"}, "current_proof_contract_digest": "proof-123", "proof_contract_digest": "proof-123"}},
                    "runtime_handoff": {
                        "id": "checked_dispatch_ready",
                        "summary": "The resident runtime is ready for a checked selected-macro dispatch.",
                        "reason": "The runtime board already bounded the next move for the selected macro.",
                        "command": "./bin/dispatch_macro_checked.sh sig",
                        "followup": ["./bin/macro_latest_dispatch_json.sh sig", "./bin/macro_latest_run_json.sh sig"],
                        "runtime_posture_id": "warm_dispatch_ready",
                        "selected_receipt_scope_id": "selected_macro_latest_dispatch",
                        "selected_receipt_status_id": "latest_dispatch_currentness_unknown",
                        "selected_receipt_command": "./bin/macro_latest_dispatch_json.sh sig",
                    },
                },
                "macros": [
                    {
                        "name": "sig",
                        "runtime_posture": {"id": "warm_dispatch_ready"},
                        "acceptance": {"runtime_signoff": {"status": "accepted", "matches_current_posture": True, "matches_current_contract": True, "contract_status": "current", "posture_id": "warm_dispatch_ready", "current_proof_contract": {"digest": "proof-123"}, "current_proof_contract_digest": "proof-123", "proof_contract_digest": "proof-123"}},
                        "runtime_handoff": {
                            "id": "checked_dispatch_ready",
                            "summary": "The resident runtime is ready for a checked selected-macro dispatch.",
                            "reason": "The runtime board already bounded the next move for the selected macro.",
                            "command": "./bin/dispatch_macro_checked.sh sig",
                            "followup": ["./bin/macro_latest_dispatch_json.sh sig", "./bin/macro_latest_run_json.sh sig"],
                            "runtime_posture_id": "warm_dispatch_ready",
                            "selected_receipt_scope_id": "selected_macro_latest_dispatch",
                            "selected_receipt_status_id": "latest_dispatch_currentness_unknown",
                            "selected_receipt_command": "./bin/macro_latest_dispatch_json.sh sig",
                        },
                    }
                ],
            },
        },
    )

    ticket = payload["primary_macro_work_ticket"]
    assert ticket["stage_id"] == "execution"
    assert ticket["source_ticket_id"] == "primary_macro_runtime_board"
    assert ticket["status_id"] == "checked_dispatch_ready"
    assert ticket["route_id"] == "follow_runtime_handoff_before_generic_execution"
    assert ticket["recommended"]["command"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["runtime_handoff"]["status_id"] == "checked_dispatch_ready"
    assert ticket["runtime_handoff"]["recommended_command"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["runtime_handoff"]["selected_receipt_scope_id"] == "selected_macro_latest_dispatch"
    assert ticket["runtime_handoff"]["selected_receipt_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_runtime_handoff_id"] == "checked_dispatch_ready"
    assert payload["sources"]["helpers"]["primary_macro_work_ticket_json"]["selected_macro_work_ticket_runtime_handoff_command"] == "./bin/dispatch_macro_checked.sh sig"
    assert "primary_macro_work_ticket_runtime_handoff=checked_dispatch_ready" in summary
    assert "primary_macro_work_ticket_runtime_handoff_command=./bin/dispatch_macro_checked.sh sig" in summary



def test_primary_macro_work_ticket_threads_latest_dispatch_target_handoff(tmp_path: Path):
    payload, _summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "macro_latest_dispatch_json.sh": {
                "latest_dispatch": {
                    "target_authority_evidence": {
                        "status_id": "current_target_authority_receipt",
                        "current": True,
                        "match_verdict": "matched",
                        "recommended": {"command": "./bin/macro_dispatch_gate_json.sh sig"},
                    }
                }
            }
        },
    )
    ticket = payload["primary_macro_work_ticket"]
    assert ticket["latest_dispatch_handoff"]["target_status_id"] == "current_target_authority_receipt"
    assert ticket["latest_dispatch_handoff"]["target_current"] is True
    assert ticket["latest_dispatch_handoff"]["target_match_verdict"] == "matched"
    assert ticket["latest_dispatch_handoff"]["target_recommended_command"] == "./bin/macro_dispatch_gate_json.sh sig"


def test_primary_macro_work_ticket_selected_handoff_carries_current_receipt_cutover_contract(tmp_path: Path):
    payload, summary = _generate_stack_payload(tmp_path, overrides={})

    ticket = payload["primary_macro_work_ticket"]
    handoff = ticket["selected_macro_handoff"]
    assert handoff["source_kind"] == "dispatch_history_workbench"
    assert handoff["stage_completion_id"] == "receipt_disposition_explicit"
    assert handoff["stage_completion_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert handoff["execution_cutover_id"] == "inspect_current_receipt_before_reemit"
    assert handoff["execution_cutover_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert handoff["receipt_disposition_required"] is True
    assert handoff["redundant_resident_dispatch_risk"] is True
    work_ticket_helper = payload["sources"]["helpers"]["primary_macro_work_ticket_json"]
    assert work_ticket_helper["selected_macro_work_ticket_handoff_execution_cutover_id"] == "inspect_current_receipt_before_reemit"
    assert work_ticket_helper["selected_macro_work_ticket_handoff_execution_cutover_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert work_ticket_helper["selected_macro_work_ticket_handoff_receipt_disposition_required"] is True
    assert "primary_macro_work_ticket_selected_handoff_execution_cutover=inspect_current_receipt_before_reemit" in summary
    assert "primary_macro_work_ticket_selected_handoff_receipt_disposition_required=True" in summary


def test_primary_macro_work_ticket_selected_handoff_carries_runtime_repair_truth(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            "latest_dispatch_json.sh": {
                "latest_dispatch": {
                    "macro": "sig",
                    "result": "blocked",
                    "route": "checked_dispatch",
                    "recorded_at": "2026-03-22T15:05:00Z",
                    "warm_runtime_evidence": {
                        "status_id": "repair_runtime_before_reusing_receipt",
                        "current": False,
                        "summary": "The newest dispatch receipt is no longer current warm-runtime evidence on this resident lane.",
                        "reason": "The resident runtime witness changed after the newest receipt, so inspect that receipt before retrying warm dispatch.",
                        "recommended": {"command": "warm_runtime_ticket.sh"},
                    },
                }
            },
            "macro_latest_dispatch_json.sh": {
                "latest_dispatch": {
                    "macro": "sig",
                    "result": "blocked",
                    "route": "checked_dispatch",
                    "recorded_at": "2026-03-22T15:05:00Z",
                    "warm_runtime_evidence": {
                        "status_id": "repair_runtime_before_reusing_receipt",
                        "current": False,
                        "summary": "The newest dispatch receipt is no longer current warm-runtime evidence on this resident lane.",
                        "reason": "The resident runtime witness changed after the newest receipt, so inspect that receipt before retrying warm dispatch.",
                        "recommended": {"command": "warm_runtime_ticket.sh"},
                    },
                }
            },
            "macro_dispatch_history_board_json.sh": {
                "summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1},
                "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}}, "llm_workbench": {"source_id": "macro_dispatch_history_board.llm_workbench", "source_command": "./bin/macro_dispatch_history_board_json.sh", "mode_id": "inspect_stale_dispatch_receipt", "recommended_command": "./bin/macro_latest_dispatch_json.sh sig"}},
                "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch", "unresolved_force_override": False}, "llm_workbench": {"source_id": "macro_dispatch_history_board.llm_workbench", "source_command": "./bin/macro_dispatch_history_board_json.sh", "mode_id": "inspect_stale_dispatch_receipt", "recommended_command": "./bin/macro_latest_dispatch_json.sh sig"}}],
            },
        },
    )

    handoff = payload["primary_macro_work_ticket"]["selected_macro_handoff"]
    assert handoff["execution_cutover_id"] == "inspect_stale_receipt_before_runtime_reuse"
    assert handoff["execution_cutover_command"] == "./bin/macro_latest_dispatch_json.sh sig"
    assert handoff["receipt_disposition_required"] is True
    assert handoff["repair_required"] is True
    assert handoff["redundant_resident_dispatch_risk"] is True
    work_ticket_helper = payload["sources"]["helpers"]["primary_macro_work_ticket_json"]
    assert work_ticket_helper["selected_macro_work_ticket_handoff_execution_cutover_id"] == "inspect_stale_receipt_before_runtime_reuse"
    assert work_ticket_helper["selected_macro_work_ticket_handoff_repair_required"] is True
    assert "primary_macro_work_ticket_selected_handoff_execution_cutover=inspect_stale_receipt_before_runtime_reuse" in summary
    assert "primary_macro_work_ticket_selected_handoff_repair_required=True" in summary


def test_primary_macro_work_ticket_threads_forced_dispatch_receipt_handoff(tmp_path: Path):
    payload, summary = _generate_stack_payload(
        tmp_path,
        overrides={
            'latest_dispatch_json.sh': {
                'latest_dispatch': {
                    'macro': 'sig',
                    'result': 'emitted',
                    'route': 'checked_dispatch_forced',
                    'force_override': True,
                    'clean_replacement_required': True,
                    'warm_runtime_evidence': {
                        'status_id': 'current_forced_dispatch_evidence',
                        'current': True,
                        'summary': 'The newest dispatch receipt is still current resident evidence, but it was recorded with --force and still needs a clean checked-dispatch replacement.',
                        'recommended': {'command': './bin/macro_latest_dispatch_json.sh sig'},
                        'followup': ['./bin/macro_latest_dispatch_json.sh sig', './bin/macro_dispatch_gate_json.sh sig', './bin/dispatch_macro_checked.sh sig'],
                        'clean_replacement_required': True,
                        'force_override': True,
                    },
                }
            },
            'macro_latest_dispatch_json.sh': {
                'latest_dispatch': {
                    'macro': 'sig',
                    'result': 'emitted',
                    'route': 'checked_dispatch_forced',
                    'force_override': True,
                    'clean_replacement_required': True,
                    'warm_runtime_evidence': {
                        'status_id': 'current_forced_dispatch_evidence',
                        'current': True,
                        'summary': 'The newest dispatch receipt is still current resident evidence, but it was recorded with --force and still needs a clean checked-dispatch replacement.',
                        'recommended': {'command': './bin/macro_latest_dispatch_json.sh sig'},
                        'followup': ['./bin/macro_latest_dispatch_json.sh sig', './bin/macro_dispatch_gate_json.sh sig', './bin/dispatch_macro_checked.sh sig'],
                        'clean_replacement_required': True,
                        'force_override': True,
                    },
                }
            },
        },
    )

    ticket = payload['primary_macro_work_ticket']
    assert ticket['latest_dispatch_handoff']['status_id'] == 'current_forced_dispatch_evidence'
    assert ticket['latest_dispatch_handoff']['current'] is True
    assert ticket['latest_dispatch_handoff']['force_override'] is True
    assert ticket['latest_dispatch_handoff']['clean_replacement_required'] is True
    assert ticket['selected_macro_handoff']['source_kind'] in {'llm_workbench', 'dispatch_history_workbench'}
    assert ticket['selected_macro_handoff']['selected_receipt_status_id'] == 'current_forced_dispatch_evidence'
    assert ticket['selected_macro_handoff']['workbench_mode_id'] == 'inspect_forced_dispatch_receipt'
    assert ticket['selected_macro_handoff']['stage_completion_id'] == 'forced_receipt_disposition_and_clean_replacement_explicit'
    assert ticket['selected_macro_handoff']['execution_cutover_id'] == 'inspect_forced_receipt_before_clean_replacement'
    assert ticket['selected_macro_handoff']['clean_replacement_required'] is True
    assert 'primary_macro_work_ticket_latest_dispatch_evidence_status=current_forced_dispatch_evidence' in summary
    assert 'primary_macro_work_ticket_selected_handoff_execution_cutover=inspect_forced_receipt_before_clean_replacement' in summary
