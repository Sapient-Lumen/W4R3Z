from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess
import sys
import shlex

import yaml
from typer.testing import CliRunner

from vhk.cli import app


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


def test_gen_i3_busd_stack_writes_flagship_runtime_handoff(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    readme = (out_dir / "README.md").read_text()
    assert "flagship warm-runtime lane" in readme
    assert "graphical-session.target" in readme
    assert "private LLM" in readme
    assert "control-plane.json" in readme
    assert "list_macros.sh" in readme
    assert "macro_source_json.sh" in readme
    assert "macro_author_loop_json.sh" in readme
    assert "macro_author_queue_json.sh" in readme
    assert "macro_replay_board_json.sh" in readme
    assert "macro_runtime_board_json.sh" in readme
    assert "macro_dispatch_history_board_json.sh" in readme
    assert "macro_dispatch_catalog_json.sh" in readme
    assert "macro_dispatch_gate_json.sh" in readme
    assert "dispatch_macro_checked.sh" in readme
    assert "macro_acceptance_ledger_json.sh" in readme
    assert "macro_recording_json.sh" in readme
    assert "macro_entrypoints_json.sh" in readme
    assert "macro_contract_json.sh" in readme
    assert "render_macro.sh" in readme
    assert "lint_macro.sh" in readme
    assert "validate_project.sh" in readme
    assert "optimize_macro.sh" in readme
    assert "apply_optimize_macro.sh" in readme
    assert "retime_macro.sh" in readme
    assert "run_macro.sh" in readme
    assert "dispatch_macro.sh" in readme
    assert "record_macro.sh" in readme
    assert "report_latest.sh" in readme
    assert "latest_run_json.sh" in readme
    assert "latest_dispatch_json.sh" in readme
    assert "latest_run_health_json.sh" in readme
    assert "latest_artifacts.sh" in readme
    assert "trace_latest.sh" in readme
    assert "history_runs.sh" in readme
    assert "stack_state_json.sh" in readme
    assert "stack_state.sh" in readme

    i3_snippet = (out_dir / "i3" / "vhk-busd.conf").read_text()
    assert "vhk-emit" in i3_snippet
    assert "hotkey" in i3_snippet

    sock = (out_dir / "systemd-user" / "vhk-busd-p.socket").read_text()
    svc = (out_dir / "systemd-user" / "vhk-busd-p.service").read_text()
    assert "WantedBy=graphical-session.target" in sock
    assert "BindsTo=graphical-session.target" in svc
    assert "ExecStart=" in svc

    control_manifest = (out_dir / "control-plane.json")
    list_macros = (out_dir / "bin" / "list_macros.sh")
    macro_inventory_json = (out_dir / "bin" / "macro_inventory_json.sh")
    macro_source_json = (out_dir / "bin" / "macro_source_json.sh")
    macro_author_loop_json = (out_dir / "bin" / "macro_author_loop_json.sh")
    macro_author_queue_json = (out_dir / "bin" / "macro_author_queue_json.sh")
    macro_replay_board_json = (out_dir / "bin" / "macro_replay_board_json.sh")
    macro_runtime_board_json = (out_dir / "bin" / "macro_runtime_board_json.sh")
    macro_dispatch_history_board_json = (out_dir / "bin" / "macro_dispatch_history_board_json.sh")
    macro_dispatch_catalog_json = (out_dir / "bin" / "macro_dispatch_catalog_json.sh")
    macro_dispatch_gate_json = (out_dir / "bin" / "macro_dispatch_gate_json.sh")
    macro_acceptance_ledger_json = (out_dir / "bin" / "macro_acceptance_ledger_json.sh")
    macro_recording_json = (out_dir / "bin" / "macro_recording_json.sh")
    macro_entrypoints_json = (out_dir / "bin" / "macro_entrypoints_json.sh")
    macro_contract_json = (out_dir / "bin" / "macro_contract_json.sh")
    render_macro = (out_dir / "bin" / "render_macro.sh")
    lint_macro = (out_dir / "bin" / "lint_macro.sh")
    validate_project = (out_dir / "bin" / "validate_project.sh")
    optimize_macro = (out_dir / "bin" / "optimize_macro.sh")
    apply_optimize_macro = (out_dir / "bin" / "apply_optimize_macro.sh")
    retime_macro = (out_dir / "bin" / "retime_macro.sh")
    run_macro = (out_dir / "bin" / "run_macro.sh")
    dispatch = (out_dir / "bin" / "dispatch_macro.sh")
    dispatch_checked = (out_dir / "bin" / "dispatch_macro_checked.sh")
    record_macro = (out_dir / "bin" / "record_macro.sh")
    report_latest = (out_dir / "bin" / "report_latest.sh")
    latest_run_json = (out_dir / "bin" / "latest_run_json.sh")
    latest_dispatch_json = (out_dir / "bin" / "latest_dispatch_json.sh")
    latest_run_health_json = (out_dir / "bin" / "latest_run_health_json.sh")
    latest_artifacts = (out_dir / "bin" / "latest_artifacts.sh")
    trace_latest = (out_dir / "bin" / "trace_latest.sh")
    history_runs = (out_dir / "bin" / "history_runs.sh")
    status = (out_dir / "bin" / "status_runtime.sh")
    status_json = (out_dir / "bin" / "status_runtime_json.sh")
    logs = (out_dir / "bin" / "logs_runtime.sh")
    check_json = (out_dir / "bin" / "check_runtime_json.sh")
    startup_handoff_status_json = (out_dir / "bin" / "startup_handoff_status_json.sh")
    startup_handoff_drift_json = (out_dir / "bin" / "startup_handoff_drift_json.sh")
    assert_ready = (out_dir / "bin" / "assert_runtime_ready.sh")
    next_action_json = (out_dir / "bin" / "next_action_json.sh")
    next_action = (out_dir / "bin" / "next_action.sh")
    stack_state_json = (out_dir / "bin" / "stack_state_json.sh")
    stack_state = (out_dir / "bin" / "stack_state.sh")
    reload_runtime = (out_dir / "bin" / "reload_runtime.sh")
    reload_runtime_json = (out_dir / "bin" / "reload_runtime_json.sh")
    stop_runtime = (out_dir / "bin" / "stop_runtime.sh")
    assert control_manifest.exists()
    assert list_macros.exists()
    assert macro_inventory_json.exists()
    assert macro_source_json.exists()
    assert macro_author_loop_json.exists()
    assert macro_author_queue_json.exists()
    assert macro_replay_board_json.exists()
    assert macro_runtime_board_json.exists()
    assert macro_dispatch_history_board_json.exists()
    assert macro_dispatch_catalog_json.exists()
    assert macro_dispatch_gate_json.exists()
    assert macro_acceptance_ledger_json.exists()
    assert macro_recording_json.exists()
    assert macro_entrypoints_json.exists()
    assert macro_contract_json.exists()
    assert render_macro.exists()
    assert lint_macro.exists()
    assert validate_project.exists()
    assert optimize_macro.exists()
    assert apply_optimize_macro.exists()
    assert retime_macro.exists()
    assert run_macro.exists()
    assert dispatch.exists()
    assert dispatch_checked.exists()
    assert record_macro.exists()
    assert report_latest.exists()
    assert latest_run_json.exists()
    assert latest_dispatch_json.exists()
    assert latest_run_health_json.exists()
    assert latest_artifacts.exists()
    assert trace_latest.exists()
    assert history_runs.exists()
    assert status.exists()
    assert status_json.exists()
    assert logs.exists()
    assert check_json.exists()
    assert startup_handoff_status_json.exists()
    assert startup_handoff_drift_json.exists()
    assert assert_ready.exists()
    assert next_action_json.exists()
    assert next_action.exists()
    assert stack_state_json.exists()
    assert stack_state.exists()
    assert reload_runtime.exists()
    assert reload_runtime_json.exists()
    assert stop_runtime.exists()
    assert list_macros.stat().st_mode & 0o111
    assert macro_inventory_json.stat().st_mode & 0o111
    assert macro_source_json.stat().st_mode & 0o111
    assert macro_author_loop_json.stat().st_mode & 0o111
    assert macro_author_queue_json.stat().st_mode & 0o111
    assert macro_replay_board_json.stat().st_mode & 0o111
    assert macro_runtime_board_json.stat().st_mode & 0o111
    assert macro_dispatch_history_board_json.stat().st_mode & 0o111
    assert macro_dispatch_catalog_json.stat().st_mode & 0o111
    assert macro_dispatch_gate_json.stat().st_mode & 0o111
    assert macro_acceptance_ledger_json.stat().st_mode & 0o111
    assert macro_recording_json.stat().st_mode & 0o111
    assert macro_entrypoints_json.stat().st_mode & 0o111
    assert macro_contract_json.stat().st_mode & 0o111
    assert render_macro.stat().st_mode & 0o111
    assert lint_macro.stat().st_mode & 0o111
    assert validate_project.stat().st_mode & 0o111
    assert optimize_macro.stat().st_mode & 0o111
    assert apply_optimize_macro.stat().st_mode & 0o111
    assert retime_macro.stat().st_mode & 0o111
    assert run_macro.stat().st_mode & 0o111
    assert dispatch.stat().st_mode & 0o111
    assert dispatch_checked.stat().st_mode & 0o111
    assert record_macro.stat().st_mode & 0o111
    assert report_latest.stat().st_mode & 0o111
    assert latest_run_json.stat().st_mode & 0o111
    assert latest_dispatch_json.stat().st_mode & 0o111
    assert latest_run_health_json.stat().st_mode & 0o111
    assert latest_artifacts.stat().st_mode & 0o111
    assert trace_latest.stat().st_mode & 0o111
    assert history_runs.stat().st_mode & 0o111
    assert status.stat().st_mode & 0o111
    assert status_json.stat().st_mode & 0o111
    assert check_json.stat().st_mode & 0o111
    assert reload_runtime.read_text().count("bus-reload") >= 1
    assert "runtime_reload_receipt" in reload_runtime_json.read_text()
    assert startup_handoff_status_json.stat().st_mode & 0o111
    assert startup_handoff_drift_json.stat().st_mode & 0o111
    assert assert_ready.stat().st_mode & 0o111
    assert next_action_json.stat().st_mode & 0o111
    assert next_action.stat().st_mode & 0o111
    assert stack_state_json.stat().st_mode & 0o111
    assert stack_state.stat().st_mode & 0o111
    assert reload_runtime_json.stat().st_mode & 0o111


    manifest = json.loads(control_manifest.read_text())
    assert manifest["stack_kind"] == "vhk.i3_x11.warm_runtime"
    assert manifest["project"]["name"] == "p"
    assert manifest["runtime"]["session_bound"] is True
    assert manifest["runtime"]["bus_event"] == "hotkey"
    assert manifest["runtime"]["bus_socket"].endswith("bus.sock")
    product_contract = manifest["product_contract"]
    assert product_contract["primary_target"]["window_manager"] == "i3"
    assert product_contract["primary_target"]["display_server"] == "x11"
    assert product_contract["runtime_shape"]["mode"] == "session_bound_long_lived_user_service"
    assert product_contract["authoring_loop"]["preferred_sequence"][:3] == ["record", "cleanup", "replay"]
    assert "broad_wayland_parity" in product_contract["vault_or_demote"]
    llm_authoring_contract = manifest["llm_authoring_contract"]
    assert llm_authoring_contract["preferred_project_triage_entrypoints"][0] == "bin/stack_state_json.sh"
    assert llm_authoring_contract["dispatch_policy"]["preferred"] == "bin/dispatch_macro_checked.sh <macro>"
    assert llm_authoring_contract["edit_review_execute_loop"][0] == "bin/macro_source_json.sh <macro>"
    session_activation_contract = manifest["session_activation_contract"]
    assert session_activation_contract["required"] is True
    assert session_activation_contract["preferred_command"].startswith("dbus-update-activation-environment --systemd")
    assert "DISPLAY" in session_activation_contract["bridge_variables"]
    assert "XAUTHORITY" in session_activation_contract["bridge_variables"]
    control_plane = manifest["control_plane"]
    script_names = {item["name"] for item in control_plane["scripts"]}
    assert {"list_macros", "macro_inventory_json", "macro_review_queue_json", "macro_acceptance_ledger_json", "macro_source_json", "macro_author_loop_json", "macro_author_queue_json", "macro_replay_board_json", "macro_runtime_board_json", "macro_dispatch_history_board_json", "macro_dispatch_catalog_json", "macro_dispatch_gate_json", "macro_recording_json", "macro_entrypoints_json", "macro_contract_json", "render_macro", "lint_macro", "validate_project", "optimize_macro", "apply_optimize_macro", "retime_macro", "run_macro", "dispatch_macro", "dispatch_macro_checked", "record_macro", "report_latest", "latest_run_json", "latest_dispatch_json", "latest_run_health_json", "latest_artifacts", "trace_latest", "history_runs", "reload_runtime", "reload_runtime_json", "stop_runtime", "status_runtime", "status_runtime_json", "check_runtime_json", "startup_handoff_status_json", "startup_handoff_drift_json", "assert_runtime_ready", "next_action_json", "next_action", "stack_state_json", "stack_state", "logs_runtime"}.issubset(script_names)
    assert control_plane["surface_classes"]["canonical_project_source"]["authority"] == "checked_in_source"
    assert control_plane["surface_classes"]["runtime_snapshot"]["refresh"] == "refresh_each_call"
    assert control_plane["non_claims"][0].startswith("Generated review helpers")
    scripts_by_name = {item["name"]: item for item in control_plane["scripts"]}
    assert scripts_by_name["macro_source_json"]["surface_class"] == "canonical_project_source"
    assert scripts_by_name["macro_author_loop_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_author_queue_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_replay_board_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_runtime_board_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_dispatch_history_board_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_dispatch_catalog_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_dispatch_gate_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_acceptance_ledger_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["macro_source_json"]["llm_mode"] == "edit_source"
    assert scripts_by_name["macro_author_loop_json"]["llm_mode"] == "author"
    assert scripts_by_name["macro_author_queue_json"]["llm_mode"] == "triage"
    assert scripts_by_name["macro_replay_board_json"]["llm_mode"] == "triage"
    assert scripts_by_name["macro_runtime_board_json"]["llm_mode"] == "triage"
    assert scripts_by_name["macro_dispatch_history_board_json"]["llm_mode"] == "inspect"
    assert scripts_by_name["macro_dispatch_catalog_json"]["llm_mode"] == "dispatch"
    assert scripts_by_name["macro_dispatch_gate_json"]["llm_mode"] == "gate"
    assert scripts_by_name["macro_acceptance_ledger_json"]["llm_mode"] == "audit"
    assert scripts_by_name["macro_review_queue_json"]["surface_class"] == "runtime_snapshot"
    assert scripts_by_name["dispatch_macro"]["surface_class"] == "runtime_actuation"
    assert scripts_by_name["dispatch_macro"]["llm_mode"] == "dispatch"
    assert scripts_by_name["dispatch_macro_checked"]["surface_class"] == "runtime_actuation"
    assert scripts_by_name["dispatch_macro_checked"]["llm_mode"] == "dispatch"
    assert scripts_by_name["reload_runtime_json"]["surface_class"] == "runtime_actuation"
    assert scripts_by_name["reload_runtime_json"]["llm_mode"] == "runtime_control"
    assert scripts_by_name["stack_state_json"]["surface_class"] == "runtime_snapshot"

    list_text = list_macros.read_text()
    assert 'list-macros "$PROJECT_ROOT"' in list_text

    inventory_text = macro_inventory_json.read_text()
    assert 'macro-inventory-json "$PROJECT_ROOT"' in inventory_text

    source_text = macro_source_json.read_text()
    assert 'macro-source-json "$PROJECT_ROOT" "$MACRO_NAME"' in source_text
    assert 'usage: macro_source_json.sh <macro-name>' in source_text

    author_loop_text = macro_author_loop_json.read_text()
    assert 'macro-author-loop-json "$PROJECT_ROOT" "$MACRO_NAME"' in author_loop_text
    assert 'usage: macro_author_loop_json.sh <macro-name>' in author_loop_text

    author_queue_text = macro_author_queue_json.read_text()
    assert 'macro-author-queue-json "$PROJECT_ROOT"' in author_queue_text

    replay_board_text = macro_replay_board_json.read_text()
    assert 'macro-replay-board-json "$PROJECT_ROOT"' in replay_board_text

    runtime_board_text = macro_runtime_board_json.read_text()
    assert 'macro-runtime-board-json "$PROJECT_ROOT"' in runtime_board_text

    dispatch_catalog_text = macro_dispatch_catalog_json.read_text()
    assert 'macro-dispatch-catalog-json "$PROJECT_ROOT" --bus-event "$BUS_EVENT"' in dispatch_catalog_text

    dispatch_gate_text = macro_dispatch_gate_json.read_text()
    assert 'macro-dispatch-gate-json "$PROJECT_ROOT" "$MACRO_NAME" --bus-event "$BUS_EVENT"' in dispatch_gate_text
    assert 'usage: macro_dispatch_gate_json.sh <macro-name>' in dispatch_gate_text

    acceptance_ledger_text = macro_acceptance_ledger_json.read_text()
    assert 'macro-acceptance-ledger-json "$PROJECT_ROOT"' in acceptance_ledger_text

    recording_text = macro_recording_json.read_text()
    assert 'macro-recording-json "$PROJECT_ROOT" "$MACRO_NAME"' in recording_text
    assert 'usage: macro_recording_json.sh <macro-name>' in recording_text

    entrypoints_text = macro_entrypoints_json.read_text()
    assert 'macro-entrypoints-json "$PROJECT_ROOT"' in entrypoints_text

    contract_text = macro_contract_json.read_text()
    assert 'macro-contract-json "$PROJECT_ROOT" "$MACRO_NAME" "$@"' in contract_text
    assert 'usage: macro_contract_json.sh <macro-name> [extra macro-contract-json args...]' in contract_text

    render_text = render_macro.read_text()
    assert 'render "$PROJECT_ROOT" "$MACRO_NAME"' in render_text
    assert 'usage: render_macro.sh <macro-name>' in render_text

    lint_text = lint_macro.read_text()
    assert 'lint "$MACRO_PATH" --json "$@"' in lint_text
    assert 'usage: lint_macro.sh <macro-name> [extra lint args...]' in lint_text
    assert 'resolve_macro_path' in lint_text

    validate_text = validate_project.read_text()
    assert 'lint-project "$PROJECT_ROOT" --json "$@"' in validate_text

    optimize_text = optimize_macro.read_text()
    assert 'optimize "$MACRO_PATH" --diff --compress-text --promote-paste-text --segment-paste-text "$@"' in optimize_text
    assert 'usage: optimize_macro.sh <macro-name> [extra optimize args...]' in optimize_text
    assert 'resolve_macro_path' in optimize_text

    apply_optimize_text = apply_optimize_macro.read_text()
    assert 'optimize "$MACRO_PATH" --in-place --compress-text --promote-paste-text --segment-paste-text "$@"' in apply_optimize_text
    assert 'usage: apply_optimize_macro.sh <macro-name> [extra optimize args...]' in apply_optimize_text

    retime_text = retime_macro.read_text()
    assert 'retime "$MACRO_PATH" "$@"' in retime_text
    assert 'retime_macro.sh requires retime arguments' in retime_text
    assert 'usage: retime_macro.sh <macro-name> [retime args...]' in retime_text

    run_text = run_macro.read_text()
    assert 'run "$PROJECT_ROOT" "$MACRO_NAME" "$@"' in run_text
    assert 'usage: run_macro.sh <macro-name> [extra run args...]' in run_text
    assert 'macro not found in project: $MACRO_NAME' in run_text
    assert 'list-macros "$PROJECT_ROOT" | grep -Fx -- "$MACRO_NAME"' in run_text

    dispatch_text = dispatch.read_text()
    assert 'emit-bus' in dispatch_text
    assert 'python3 - "$MACRO_NAME"' in dispatch_text
    assert 'BUS_EVENT=hotkey' in dispatch_text
    assert 'macro not found in project: $MACRO_NAME' in dispatch_text

    dispatch_checked_text = dispatch_checked.read_text()
    assert 'macro_dispatch_gate_json.sh "$MACRO_NAME" --no-pretty' in dispatch_checked_text
    assert 'usage: dispatch_macro_checked.sh [--force] <macro-name> [json-payload]' in dispatch_checked_text

    record_text = record_macro.read_text()
    assert 'record-x11' in record_text
    assert '--segment-by-window-context' in record_text
    assert '--window-guard-mode event' in record_text
    assert '--coord-mode-mouse "${VHK_RECORD_COORD_MODE_MOUSE:-window}"' in record_text
    assert '--window-context-out "$SIDECAR_PATH"' in record_text
    assert 'resolve_macro_recording_sidecar_path' in record_text
    assert '--apply-window-context' in record_text
    assert '--optimize-promote-paste-text' in record_text

    report_text = report_latest.read_text()
    assert 'report --project "$PROJECT_ROOT" --latest' in report_text

    latest_run_json_text = latest_run_json.read_text()
    assert 'latest-run-json "$PROJECT_ROOT"' in latest_run_json_text

    latest_dispatch_json_text = latest_dispatch_json.read_text()
    assert 'latest-dispatch-json "$PROJECT_ROOT"' in latest_dispatch_json_text

    latest_run_health_json_text = latest_run_health_json.read_text()
    assert 'latest-run-health-json "$PROJECT_ROOT"' in latest_run_health_json_text

    latest_artifacts_text = latest_artifacts.read_text()
    assert 'latest_run_json.sh' in latest_artifacts_text
    assert 'trace_default_out=' in latest_artifacts_text
    assert 'error_screenshot=' in latest_artifacts_text

    trace_text = trace_latest.read_text()
    assert 'trace --project "$PROJECT_ROOT" --latest --out "$OUT_PATH"' in trace_text
    assert 'DEFAULT_OUT="$PROJECT_ROOT/build/traces/latest.trace.json"' in trace_text

    history_text = history_runs.read_text()
    assert 'history "$PROJECT_ROOT" "$@"' in history_text

    status_text = status.read_text()
    assert 'systemctl --user show -p FragmentPath -p LoadState -p ActiveState -p SubState -p Result -p NRestarts -p ExecMainCode -p ExecMainStatus' in status_text
    assert 'BUS_EVENT=hotkey' in status_text

    status_json_text = status_json.read_text()
    assert 'bus_socket_exists' in status_json_text
    assert 'health' in status_json_text
    assert 'systemctl' in status_json_text
    assert 'exec python3 - "$PROJECT_ROOT" "$BUS_EVENT" "$SOCKET_UNIT" "$SERVICE_UNIT" "$BUS_SOCKET"' in status_json_text

    check_json_text = check_json.read_text()
    assert 'stack_kind' in check_json_text
    assert 'warm_runtime.check' in check_json_text
    assert 'session_attachment' in check_json_text
    assert 'summarize_session_attachment' in check_json_text
    assert 'expected_watchers' in check_json_text
    assert 'watchers_in_sync' in check_json_text
    assert 'dispatch watcher contract drift' in check_json_text
    assert 'xdotool' in check_json_text
    assert 'clipboard_fastpath' in check_json_text

    assert_ready_text = assert_ready.read_text()
    assert 'runtime not ready' in assert_ready_text
    assert 'BLOCKER:' in assert_ready_text
    assert 'check_runtime_json.sh' in assert_ready_text
    assert 'json.loads(sys.argv[1])' in assert_ready_text

    next_action_json_text = next_action_json.read_text()
    assert 'warm_runtime.next_action' in next_action_json_text
    assert 'enable_runtime_socket' in next_action_json_text
    assert 'record_first_macro' in next_action_json_text
    assert 'Run directly now:' in next_action_json_text
    assert 'macro_review_queue' in next_action_json_text
    assert 'refresh_recording_evidence' in next_action_json_text
    assert 'review_exact_recording_segments' in next_action_json_text

    next_action_text = next_action.read_text()
    assert 'primary_action' in next_action_text
    assert 'next command:' in next_action_text
    assert 'Path(sys.argv[1]).read_text' in next_action_text
    assert 'mktemp' in next_action_text
    assert 'review_queue_source=' in next_action_text
    assert 'queue:' in next_action_text

    stack_state_json_text = stack_state_json.read_text()
    assert 'vhk.i3_x11.warm_runtime.state' in stack_state_json_text
    assert 'recommended_entrypoints' in stack_state_json_text
    assert 'macro_entrypoints_json.sh' in stack_state_json_text
    assert 'macro_author_loop_json.sh' in stack_state_json_text
    assert 'macro_replay_board_json.sh' in stack_state_json_text
    assert 'macro_runtime_board_json.sh' in stack_state_json_text
    assert 'macro_dispatch_history_board_json.sh' in stack_state_json_text
    assert 'macro_acceptance_ledger_json.sh' in stack_state_json_text
    assert 'macro_recording_json.sh' in stack_state_json_text
    assert 'macro_contract_json.sh' in stack_state_json_text
    assert 'macro_names' in stack_state_json_text
    assert 'subprocess.run(argv' in stack_state_json_text
    assert 'helper_error_count' in stack_state_json_text
    assert 'macro_inventory' in stack_state_json_text
    assert 'recording_sidecar_stale_count' in stack_state_json_text
    assert 'macros_with_exact_recording_segments' in stack_state_json_text
    assert 'preset_total' in stack_state_json_text
    assert 'latest_run_health' in stack_state_json_text
    assert 'next_action_json.sh' in stack_state_json_text
    assert 'optimize_macro.sh <macro>' in stack_state_json_text
    assert 'helper_surface_contracts' in stack_state_json_text
    assert 'dispatch_watchers_in_sync' in stack_state_json_text
    assert 'dispatch_missing_expected_watchers' in stack_state_json_text
    assert 'warm_runtime_ticket' in stack_state_json_text
    assert 'startup_handoff_repair_ticket' in stack_state_json_text
    assert 'next_action_trace' in stack_state_json_text
    assert 'macro_acceptance_ledger' in stack_state_json_text
    assert 'macro_dispatch_gate' in stack_state_json_text
    assert 'macro_dispatch_gate_json' in stack_state_json_text
    assert 'primary_macro_latest_run' in stack_state_json_text
    assert 'macro_latest_run_json' in stack_state_json_text
    assert 'primary_macro_contract' in stack_state_json_text
    assert 'macro_contract_json' in stack_state_json_text
    assert 'primary_macro_author_loop' in stack_state_json_text
    assert 'macro_author_loop_json' in stack_state_json_text
    assert 'primary_macro_recording' in stack_state_json_text
    assert 'macro_recording_json' in stack_state_json_text
    assert 'primary_macro_cleanup_ticket' in stack_state_json_text
    assert 'primary_macro_replay_ticket' in stack_state_json_text
    assert 'primary_macro_entrypoints' in stack_state_json_text
    assert 'primary_macro_replay_board' in stack_state_json_text
    assert 'primary_macro_runtime_board' in stack_state_json_text
    assert 'primary_macro_dispatch_history' in stack_state_json_text
    assert 'primary_macro_dispatch_catalog' in stack_state_json_text
    assert 'primary_macro_acceptance' in stack_state_json_text
    assert 'primary_macro_acceptance_ticket' in stack_state_json_text
    assert 'primary_macro_review_queue' in stack_state_json_text
    assert 'primary_macro_latest_dispatch' in stack_state_json_text
    assert 'primary_macro_command_palette' in stack_state_json_text
    assert 'primary_macro_execution_brief' in stack_state_json_text
    assert 'primary_macro_execution_ticket' in stack_state_json_text
    assert 'primary_macro_consistency' in stack_state_json_text
    assert 'primary_macro_repair_recipe' in stack_state_json_text
    assert 'primary_macro_probe_observation' in stack_state_json_text

    stack_state_text = stack_state.read_text()
    assert 'preset_total=' in stack_state_text
    assert 'group_count=' in stack_state_text
    assert 'tag_count=' in stack_state_text
    assert 'overall_ready=' in stack_state_text
    assert 'warm_runtime_ticket_status=' in stack_state_text
    assert 'startup_handoff_repair_ticket_status=' in stack_state_text
    assert 'warm_runtime_ticket_route=' in stack_state_text
    assert 'primary_action=' in stack_state_text
    assert 'stack_state_json.sh' in stack_state_text
    assert 'recommendation_trace_selected_action=' in stack_state_text
    assert 'primary_macro_execution_ticket_status=' in stack_state_text
    assert 'primary_macro_cleanup_ticket_status=' in stack_state_text
    assert 'primary_macro_replay_ticket_status=' in stack_state_text
    assert 'review_queue_accepted_issue_count=' in stack_state_text
    assert 'acceptance_ledger_macro_count=' in stack_state_text
    assert 'primary_macro_acceptance_ticket_status=' in stack_state_text
    assert 'dispatch_gate_decision=' in stack_state_text
    assert 'primary_macro_probe_observation_status=' in stack_state_text

    logs_text = logs.read_text()
    assert 'journalctl --user --no-pager -n "$LINES" -u "$SOCKET_UNIT" -u "$SERVICE_UNIT" "$@"' in logs_text

    assert 'bus-reload' in reload_runtime.read_text()
    assert 'bus-stop' in stop_runtime.read_text()


def test_generated_next_action_helpers_execute(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"
    wrapper = tmp_path / "vhk-wrapper.sh"
    wrapper.write_text(f"#!/usr/bin/env sh\nexec {sys.executable} -m vhk.cli \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)

    repo_src = Path(__file__).resolve().parents[1] / "src"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys", "--vhk-cmd", str(wrapper), "--vhk-pythonpath", str(repo_src)])
    assert res.exit_code == 0, res.output

    env = os.environ.copy()
    env["DISPLAY"] = env.get("DISPLAY", ":0")
    env["XDG_RUNTIME_DIR"] = env.get("XDG_RUNTIME_DIR", str(tmp_path / "runtime"))
    env["PYTHONPATH"] = str(repo_src)
    Path(env["XDG_RUNTIME_DIR"]).mkdir(parents=True, exist_ok=True)

    next_json = subprocess.run([str(out_dir / "bin" / "next_action_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert next_json.returncode == 0, next_json.stderr
    payload = json.loads(next_json.stdout)
    assert payload["stack_kind"] == "vhk.i3_x11.warm_runtime.next_action"
    assert payload["primary_action"]["id"] in {"enable_runtime_socket", "clear_prereq_blockers", "runtime_ready"}
    assert payload["recommendation_trace"]["selected_action_id"] == payload["primary_action"]["id"]
    assert payload["review_queue_source"]["mode"] in {"authoritative_helper", "inventory_fallback", "unavailable"}

    next_text = subprocess.run([str(out_dir / "bin" / "next_action.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert next_text.returncode == 0, next_text.stderr
    assert next_text.stdout.strip()

    stack_state_json = subprocess.run([str(out_dir / "bin" / "stack_state_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert stack_state_json.returncode == 0, stack_state_json.stderr
    state_payload = json.loads(stack_state_json.stdout)
    assert state_payload["stack_kind"] == "vhk.i3_x11.warm_runtime.state"
    assert state_payload["project"]["macro_count"] == 1
    assert state_payload["macro_inventory"]["preset_total"] == 0
    assert state_payload["macro_inventory"]["recording_sidecar_missing_count"] == 1
    assert state_payload["macro_inventory"]["recording_sidecar_stale_count"] == 0
    assert state_payload["macro_inventory"]["macros"][0]["name"] == "sig"
    assert state_payload["macro_entrypoints"]["macro_count"] == 1
    assert state_payload["macro_entrypoints"]["interactive_macro_count"] == 0
    assert state_payload["macro_entrypoints"]["preset_enabled_macro_count"] == 0
    assert state_payload["macro_entrypoints"]["macros"][0]["preferred_entrypoints"]["warm_runtime"] == "dispatch_macro.sh sig"
    assert state_payload["macro_entrypoints"]["macros"][0]["preferred_entrypoints"]["recording_review"] == "macro_recording_json.sh sig"
    assert state_payload["macro_author_queue"]["primary_macro"]["name"] == "sig"
    assert state_payload["primary_macro_entrypoints"]["macro_name"] == "sig"
    assert state_payload["primary_macro_entrypoints"]["preferred_entrypoints"]["warm_runtime"] == "dispatch_macro.sh sig"
    assert state_payload["macro_dispatch_catalog"]["runtime"]["bus_event"] == "hotkey"
    assert state_payload["control_plane"]["preferred_for_llm"] is True
    assert state_payload["control_plane"]["product_contract"]["primary_target"]["window_manager"] == "i3"
    assert state_payload["control_plane"]["llm_authoring_contract"]["dispatch_policy"]["preferred"] == "bin/dispatch_macro_checked.sh <macro>"
    assert state_payload["control_plane"]["session_activation_contract"]["preferred_command"].startswith("dbus-update-activation-environment --systemd")
    assert state_payload["control_plane"]["surface_classes"]["runtime_snapshot"]["authority"] == "live_runtime_state"
    assert state_payload["control_plane"]["non_claims"][0].startswith("Generated review helpers")
    assert state_payload["next_action_trace"]["selected_action_id"] == state_payload["next_action"]["id"]

    entrypoints_json = subprocess.run([str(out_dir / "bin" / "macro_entrypoints_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert entrypoints_json.returncode == 0, entrypoints_json.stderr
    entrypoints_payload = json.loads(entrypoints_json.stdout)
    assert entrypoints_payload["stack_kind"] == "vhk.project.macro_entrypoints"
    assert entrypoints_payload["project"]["macro_count"] == 1
    assert entrypoints_payload["macros"][0]["preferred_entrypoints"]["warm_runtime"] == "dispatch_macro.sh sig"

    contract_json = subprocess.run([str(out_dir / "bin" / "macro_contract_json.sh"), "sig"], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert contract_json.returncode == 0, contract_json.stderr
    contract_payload = json.loads(contract_json.stdout)
    assert contract_payload["stack_kind"] == "vhk.project.macro_contract"
    assert contract_payload["macro"]["name"] == "sig"

    run_now = subprocess.run([str(out_dir / "bin" / "run_macro.sh"), "sig", "--print-return"], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert run_now.returncode == 0, run_now.stderr
    assert run_now.stdout.strip() == "OK"

    stack_state_text = subprocess.run([str(out_dir / "bin" / "stack_state.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert stack_state_text.returncode == 0, stack_state_text.stderr
    assert "preset_total=0" in stack_state_text.stdout
    assert "group_count=0" in stack_state_text.stdout
    assert "tag_count=0" in stack_state_text.stdout
    assert "recording_sidecar_count=0" in stack_state_text.stdout
    assert "recording_sidecar_stale_count=0" in stack_state_text.stdout
    assert "interactive_macro_count=0" in stack_state_text.stdout
    assert "preset_enabled_macro_count=0" in stack_state_text.stdout
    assert "dispatch_ready_now_count=" in stack_state_text.stdout
    assert "overall_ready=" in stack_state_text.stdout
    assert "helper_error_count=0" in stack_state_text.stdout
    assert "recommendation_trace_selected_action=" in stack_state_text.stdout

    latest_json = subprocess.run([str(out_dir / "bin" / "latest_run_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert latest_json.returncode == 0, latest_json.stderr
    latest_payload = json.loads(latest_json.stdout)
    assert latest_payload["stack_kind"] == "vhk.project.latest_run"
    assert latest_payload["latest_run"] is None

    latest_health_json = subprocess.run([str(out_dir / "bin" / "latest_run_health_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert latest_health_json.returncode == 0, latest_health_json.stderr
    latest_health_payload = json.loads(latest_health_json.stdout)
    assert latest_health_payload["stack_kind"] == "vhk.project.latest_run_health"
    assert latest_health_payload["health"]["verdict"] == "unknown"

    latest_text = subprocess.run([str(out_dir / "bin" / "latest_artifacts.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert latest_text.returncode == 0, latest_text.stderr
    assert "latest_run: none" in latest_text.stdout

    state_json_text = (out_dir / "bin" / "stack_state_json.sh").read_text()
    assert 'VHK_PYTHONPATH=' in state_json_text
    assert 'export PYTHONPATH="$VHK_PYTHONPATH:$PYTHONPATH"' in state_json_text

    ready = subprocess.run([str(out_dir / "bin" / "assert_runtime_ready.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert ready.returncode != 0
    assert "runtime not ready" in ready.stderr



def _write_json_shell(path: Path, payload: dict[str, object]) -> None:
    path.write_text(
        "#!/usr/bin/env sh\ncat <<'JSON'\n" + json.dumps(payload) + "\nJSON\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def test_generated_next_action_helper_surfaces_macro_review_queue(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"
    wrapper = tmp_path / "vhk-wrapper.sh"
    wrapper.write_text(f"#!/usr/bin/env sh\nexec {sys.executable} -m vhk.cli \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)

    repo_src = Path(__file__).resolve().parents[1] / "src"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys", "--vhk-cmd", str(wrapper), "--vhk-pythonpath", str(repo_src)])
    assert res.exit_code == 0, res.output

    _write_json_shell(out_dir / "bin" / "check_runtime_json.sh", {
        "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
        "env": {"session_ready": True},
        "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
        "capabilities": {"warm_runtime": True},
        "health": {"blockers": [], "warnings": []},
    })
    _write_json_shell(out_dir / "bin" / "status_runtime_json.sh", {"health": {"ready": True}})
    _write_json_shell(out_dir / "bin" / "macro_inventory_json.sh", {
        "project": {
            "macro_count": 1,
            "recording_sidecar_missing_count": 0,
            "recording_sidecar_stale_count": 1,
            "recording_sidecar_newer_than_source_count": 0,
        },
        "macros": [{
            "name": "sig",
            "source": {
                "recording_sidecar": {
                    "freshness": {"status": "source_newer_than_recording"},
                    "exact_segment_count": 1,
                    "transition_reason_counts": {"title": 1},
                }
            },
        }],
    })
    _write_json_shell(out_dir / "bin" / "latest_run_health_json.sh", {
        "health": {
            "verdict": "healthy",
            "summary": "Latest run is healthy.",
            "reasons": ["run_end reported ok=true"],
            "next_step": {"command": "./bin/trace_latest.sh"},
        }
    })
    _write_json_shell(out_dir / "bin" / "macro_review_queue_json.sh", {
        "counts": {
            "missing_recording_sidecars": 0,
            "stale_recording_sidecars": 1,
            "recording_newer_than_source": 0,
            "exact_segment_macros": 1,
            "title_segment_macros": 1,
            "needs_review_count": 1,
        },
        "queue": {
            "missing_recording_sidecars": [],
            "stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
            "recording_newer_than_source": [],
            "exact_segment_macros": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
            "title_segment_macros": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
        },
        "ordered": [{"name": "sig", "kind": "stale_recording_sidecar"}],
    })
    _write_json_shell(out_dir / "bin" / "macro_author_queue_json.sh", {
        "summary": {"primary_macro_name": "sig", "primary_action_id": "refresh_recording_review"},
        "primary_macro": {
            "name": "sig",
            "preferred_execution_mode": "warm_runtime_dispatch",
            "next_step": {
                "id": "refresh_recording_review",
                "summary": "Review or refresh recorder evidence because the macro source is newer than the sidecar.",
                "reason": "Recorder context may be stale relative to the editable macro source.",
                "command": "macro_recording_json.sh sig",
                "followup": ["record_macro.sh sig 5000", "optimize_macro.sh sig"],
            },
            "dispatch_attention": {"id": "none", "needs_attention": False},
            "priority": {"effective_rank": 1},
        },
        "macros": [{"name": "sig"}],
    })
    _write_json_shell(out_dir / "bin" / "macro_dispatch_gate_json.sh", {
        "repair_action": {"id": "repair_recorder_contract", "command": "macro_recording_json.sh sig"},
        "decision": {"id": "stabilize_before_dispatch", "command": "macro_author_loop_json.sh sig"},
        "dispatch_readiness": {"can_emit_minimal_payload_now": False},
    })

    next_json = subprocess.run([str(out_dir / "bin" / "next_action_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), check=False)
    assert next_json.returncode == 0, next_json.stderr
    payload = json.loads(next_json.stdout)
    assert payload["primary_action"]["id"] == "refresh_recording_review"
    assert payload["primary_action"]["command"] == "./bin/macro_recording_json.sh sig"
    assert payload["recommendation_trace"]["selected_action_id"] == "refresh_recording_review"
    assert payload["review_queue_source"]["mode"] == "authoritative_helper"
    assert payload["macro_author_queue"]["primary_macro"]["name"] == "sig"
    assert payload["macro_review_queue"]["stale_recording_sidecars"][0]["name"] == "sig"
    assert payload["macro_review_queue"]["exact_segment_macros"][0]["name"] == "sig"
    assert payload["macro_review_queue"]["title_segment_macros"][0]["name"] == "sig"

    next_text = subprocess.run([str(out_dir / "bin" / "next_action.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), check=False)
    assert next_text.returncode == 0, next_text.stderr
    assert "queue: stale recorder evidence=1 (sig)" in next_text.stdout
    assert "queue: exact recorder segments=1 (sig)" in next_text.stdout


def test_generated_next_action_helper_prioritizes_latest_failures_over_review_queue(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"
    wrapper = tmp_path / "vhk-wrapper.sh"
    wrapper.write_text(f"#!/usr/bin/env sh\nexec {sys.executable} -m vhk.cli \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)

    repo_src = Path(__file__).resolve().parents[1] / "src"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys", "--vhk-cmd", str(wrapper), "--vhk-pythonpath", str(repo_src)])
    assert res.exit_code == 0, res.output

    _write_json_shell(out_dir / "bin" / "check_runtime_json.sh", {
        "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
        "env": {"session_ready": True},
        "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
        "capabilities": {"warm_runtime": True},
        "health": {"blockers": [], "warnings": []},
    })
    _write_json_shell(out_dir / "bin" / "status_runtime_json.sh", {"health": {"ready": True}})
    _write_json_shell(out_dir / "bin" / "macro_inventory_json.sh", {
        "project": {"macro_count": 1, "recording_sidecar_missing_count": 0, "recording_sidecar_stale_count": 1},
        "macros": [{"name": "sig", "source": {"recording_sidecar": {"freshness": {"status": "source_newer_than_recording"}, "exact_segment_count": 1, "transition_reason_counts": {}}}}],
    })
    _write_json_shell(out_dir / "bin" / "latest_run_health_json.sh", {
        "health": {
            "verdict": "fail",
            "summary": "Latest run failed.",
            "reasons": ["error_count=2"],
            "next_step": {"command": "./bin/report_latest.sh --show-errors --show-waits --show-advice"},
        }
    })
    _write_json_shell(out_dir / "bin" / "macro_review_queue_json.sh", {
        "counts": {
            "missing_recording_sidecars": 0,
            "stale_recording_sidecars": 1,
            "recording_newer_than_source": 0,
            "exact_segment_macros": 1,
            "title_segment_macros": 0,
            "needs_review_count": 1,
        },
        "queue": {
            "missing_recording_sidecars": [],
            "stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
            "recording_newer_than_source": [],
            "exact_segment_macros": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
            "title_segment_macros": [],
        },
        "ordered": [{"name": "sig", "kind": "stale_recording_sidecar"}],
    })
    _write_json_shell(out_dir / "bin" / "macro_author_queue_json.sh", {
        "summary": {"primary_macro_name": "sig", "primary_action_id": "inspect_latest_failures"},
        "primary_macro": {
            "name": "sig",
            "preferred_execution_mode": "warm_runtime_dispatch",
            "next_step": {
                "id": "inspect_latest_failures",
                "summary": "Inspect the newest failing run before editing this macro further.",
                "reason": "The latest run for this macro recorded failures.",
                "command": "report_latest.sh --show-errors --show-waits --show-advice",
                "followup": ["macro_latest_run_json.sh sig", "trace_latest.sh sig"],
            },
            "dispatch_attention": {"id": "none", "needs_attention": False},
            "priority": {"effective_rank": 2},
        },
        "macros": [{"name": "sig"}],
    })

    next_json = subprocess.run([str(out_dir / "bin" / "next_action_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), check=False)
    assert next_json.returncode == 0, next_json.stderr
    payload = json.loads(next_json.stdout)
    assert payload["primary_action"]["id"] == "inspect_latest_failures"
    assert payload["primary_action"]["command"] == "./bin/report_latest.sh --show-errors --show-waits --show-advice"
    assert payload["macro_review_queue"]["stale_recording_sidecars"][0]["name"] == "sig"
    assert payload["review_queue_source"]["mode"] == "authoritative_helper"
    assert payload["recommendation_trace"]["review_queue_source"]["mode"] == "authoritative_helper"
    assert payload["macro_author_queue"]["primary_macro"]["name"] == "sig"



def test_generated_stack_state_json_carries_primary_macro_contract(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_contract"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 1, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "repeat_or_trace"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector", "selector": {"class": "Alacritty", "workspace": "2"}}, "hints": {"has_interactive_inputs": True}, "prompt_steps": [{"type": "PromptForm"}]}, "invocation": {"generated_stack": {"run_wrapper": "run_macro.sh sig", "dispatch_checked_wrapper": "dispatch_macro_checked.sh sig"}}, "authoring": {"workflow": {"preferred_loop": ["source", "recording_review", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "direct_run_only", "counts_by_posture_id": {"direct_run_only": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "direct_run_only"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "direct_run_only"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "no_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 0}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "direct_run_only", "command": "./bin/run_macro.sh sig"}, "repair_action": {"id": "use_direct_run", "command": "./bin/run_macro.sh sig"}, "dispatch_readiness": {"primary_blocker_class_id": "direct_run_required"}, "preferred_execution_mode": "direct_run"})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "use_direct_run", "command": "./bin/run_macro.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_contract"]["macro_name"] == "sig"
    assert payload["primary_macro_contract"]["macro"]["desktop_target"]["selector"]["class"] == "Alacritty"
    assert payload["primary_macro_contract"]["preferred_execution_mode"] == "direct_run"
    assert payload["sources"]["helpers"]["macro_contract_json"]["interactive_inputs"] is True
    assert payload["sources"]["helpers"]["macro_contract_json"]["prompt_step_count"] == 1

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_contract_macro=sig" in summary
    assert "primary_macro_contract_target_source=recording_stable_selector" in summary
    assert "primary_macro_contract_execution_mode=direct_run" in summary


def test_generated_stack_state_json_carries_control_plane_contracts(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_control_plane_contracts"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"warm_runtime_checked": "dispatch_macro_checked.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_or_run"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector"}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {"generated_stack": {"dispatch_checked_wrapper": "dispatch_macro_checked.sh sig"}}, "authoring": {"workflow": {"preferred_loop": ["source", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_or_run"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}, "selector_summary": {"selector_source_id": "recording_stable_selector"}}, "review": {}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "no_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "blockers": [], "blocker_details": []}, "preferred_execution_mode": "warm_runtime_dispatch"})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "recommendation_trace": {"selected_action_id": "ready_to_dispatch"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    contracts = payload["control_plane"]
    assert contracts["product_contract"]["primary_target"]["window_manager"] == "i3"
    assert contracts["product_contract"]["runtime_shape"]["mode"] == "session_bound_long_lived_user_service"
    assert contracts["llm_authoring_contract"]["dispatch_policy"]["preferred"] == "bin/dispatch_macro_checked.sh <macro>"
    assert contracts["llm_authoring_contract"]["edit_review_execute_loop"][0] == "bin/macro_source_json.sh <macro>"
    assert contracts["session_activation_contract"]["required"] is True
    assert "DISPLAY" in contracts["session_activation_contract"]["bridge_variables"]
    assert contracts["session_activation_contract"]["preferred_command"].startswith("dbus-update-activation-environment --systemd")


def test_generated_stack_state_json_carries_primary_macro_entrypoints(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_entrypoints"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "ok", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {
        "project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0},
        "macros": [{
            "name": "sig",
            "execution": {"preferred_mode": "warm_runtime_dispatch"},
            "preferred_entrypoints": {
                "author_loop": "macro_author_loop_json.sh sig",
                "warm_runtime": "dispatch_macro.sh sig",
                "warm_runtime_checked": "dispatch_macro_checked.sh sig",
                "direct_run": "run_macro.sh sig",
            },
        }],
    })
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_or_run"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector"}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {}, "authoring": {"workflow": {"preferred_loop": ["source", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_or_run"}, "authoring": {"workflow": {"preferred_entrypoint": "macro_author_loop_json.sh sig"}}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}, "selector_summary": {"selector_source_id": "recording_stable_selector"}}, "review": {}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "no_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "dispatch_now"}, "repair_action": {"id": "ready_to_dispatch"}, "dispatch_readiness": {"primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "recommendation_trace": {"selected_action_id": "ready_to_dispatch"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_entrypoints"]["macro_name"] == "sig"
    assert payload["primary_macro_entrypoints"]["execution_mode"] == "warm_runtime_dispatch"
    assert payload["primary_macro_entrypoints"]["preferred_entrypoints"]["author_loop"] == "macro_author_loop_json.sh sig"
    assert payload["primary_macro_entrypoints"]["preferred_entrypoints"]["warm_runtime_checked"] == "dispatch_macro_checked.sh sig"
    assert payload["primary_macro_entrypoints"]["preferred_entrypoints"]["direct_run"] == "run_macro.sh sig"
    assert payload["sources"]["helpers"]["macro_entrypoints_json"]["primary_macro_name"] == "sig"
    assert payload["sources"]["helpers"]["macro_entrypoints_json"]["primary_execution_mode"] == "warm_runtime_dispatch"
    assert payload["sources"]["helpers"]["macro_entrypoints_json"]["primary_warm_runtime_entrypoint"] == "dispatch_macro_checked.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_entrypoints_macro=sig" in summary
    assert "primary_macro_entrypoints_execution_mode=warm_runtime_dispatch" in summary
    assert "primary_macro_entrypoints_author_loop=macro_author_loop_json.sh sig" in summary
    assert "primary_macro_entrypoints_warm_runtime=dispatch_macro_checked.sh sig" in summary
    assert "primary_macro_entrypoints_direct_run=run_macro.sh sig" in summary


def test_generated_stack_state_json_carries_primary_macro_recording(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_recording"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "repeat_or_trace"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector"}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {}, "authoring": {"workflow": {"preferred_loop": ["source", "recording_review"]}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}}, "next_step": {"id": "dispatch_or_run"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {
        "macro": {"name": "sig"},
        "recording": {
            "path": "/tmp/fake/sig.recording.yaml",
            "relative_path": "build/recordings/sig.recording.yaml",
            "exists": True,
            "freshness": {"status": "source_newer_than_recording"},
            "selector_summary": {"selector_source_id": "recording_stable_selector"},
            "transition_reason_counts": {"title": 1, "workspace": 1},
            "exact_segment_count": 2,
        },
        "review": {"preferred_loop": ["record", "recording_review", "cleanup_review"]},
    })
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "no_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "no_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "dispatch_now"}, "repair_action": {"id": "ready_to_dispatch"}, "dispatch_readiness": {"primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 1}, "queue": {"stale_recording_sidecars": [{"name": "sig"}]}, "ordered": [{"name": "sig", "kind": "stale_recording_sidecar"}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_recording"]["macro_name"] == "sig"
    assert payload["primary_macro_recording"]["recording"]["freshness"]["status"] == "source_newer_than_recording"
    assert payload["primary_macro_recording"]["recording"]["exact_segment_count"] == 2
    assert payload["sources"]["helpers"]["macro_recording_json"]["freshness_status"] == "source_newer_than_recording"
    assert payload["sources"]["helpers"]["macro_recording_json"]["exact_segment_count"] == 2
    assert payload["sources"]["helpers"]["macro_recording_json"]["transition_reason_counts"]["title"] == 1
    assert payload["sources"]["helpers"]["macro_recording_json"]["selector_source_id"] == "recording_stable_selector"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_recording_macro=sig" in summary
    assert "primary_macro_recording_freshness=source_newer_than_recording" in summary
    assert "primary_macro_recording_selector_source=recording_stable_selector" in summary


def test_generated_stack_state_json_carries_primary_macro_author_loop(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_author_loop"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": False}, "latest_run_health": {"verdict": "warn"}, "replay_posture": {"id": "warning_recent"}, "next_step": {"id": "trace_latest"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector"}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {}, "authoring": {"workflow": {"preferred_loop": ["source", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {
        "macro": {"name": "sig"},
        "source": {"editable": {"path": "macros/sig.yaml"}},
        "recording": {"freshness": {"status": "aligned"}},
        "review": {"status": {"id": "ready_for_execution"}},
        "latest_run": {"health": {"verdict": "warn"}},
        "execution": {
            "runtime_posture": {"id": "warm_dispatch_candidate"},
            "dispatch_gate": {"decision": {"id": "inspect_before_dispatch"}, "repair_action": {"id": "inspect_live_desktop_target"}},
            "dispatch_history": {"id": "repeated_desktop_state_mismatch"},
        },
        "next_step": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig"},
        "authoring": {"workflow": {"preferred_entrypoint": "macro_author_loop_json.sh sig"}},
    })
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent", "counts_by_posture_id": {"warning_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_candidate", "counts_by_posture_id": {"warm_dispatch_candidate": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "repeated_desktop_state_mismatch", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "inspect_before_dispatch"}, "repair_action": {"id": "inspect_live_desktop_target"}, "dispatch_readiness": {"primary_blocker_class_id": "desktop_state_mismatch"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}, "recommendation_trace": {"selected_action_id": "inspect_before_dispatch"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_author_loop"]["macro_name"] == "sig"
    assert payload["primary_macro_author_loop"]["next_step"]["id"] == "inspect_live_desktop_target"
    assert payload["primary_macro_author_loop"]["execution"]["runtime_posture"]["id"] == "warm_dispatch_candidate"
    assert payload["primary_macro_author_loop"]["execution"]["dispatch_gate"]["decision"]["id"] == "inspect_before_dispatch"
    assert payload["sources"]["helpers"]["macro_author_loop_json"]["next_step_id"] == "inspect_live_desktop_target"
    assert payload["sources"]["helpers"]["macro_author_loop_json"]["runtime_posture_id"] == "warm_dispatch_candidate"
    assert payload["sources"]["helpers"]["macro_author_loop_json"]["dispatch_gate_decision_id"] == "inspect_before_dispatch"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_author_loop_macro=sig" in summary
    assert "primary_macro_author_loop_next_step=inspect_live_desktop_target" in summary
    assert "primary_macro_author_loop_runtime_posture=warm_dispatch_candidate" in summary
    assert "primary_macro_author_loop_dispatch_decision=inspect_before_dispatch" in summary


def test_generated_stack_state_json_survives_helper_failure(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"
    wrapper = tmp_path / "vhk-wrapper.sh"
    wrapper.write_text(f"#!/usr/bin/env sh\nexec {sys.executable} -m vhk.cli \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)

    repo_src = Path(__file__).resolve().parents[1] / "src"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys", "--vhk-cmd", str(wrapper), "--vhk-pythonpath", str(repo_src)])
    assert res.exit_code == 0, res.output

    broken = out_dir / "bin" / "macro_inventory_json.sh"
    broken.write_text("#!/usr/bin/env sh\necho 'broken inventory helper' >&2\nexit 9\n", encoding="utf-8")
    broken.chmod(0o755)

    env = os.environ.copy()
    env["DISPLAY"] = env.get("DISPLAY", ":0")
    env["XDG_RUNTIME_DIR"] = env.get("XDG_RUNTIME_DIR", str(tmp_path / "runtime"))
    env["PYTHONPATH"] = str(repo_src)
    Path(env["XDG_RUNTIME_DIR"]).mkdir(parents=True, exist_ok=True)

    state = subprocess.run([str(out_dir / "bin" / "stack_state_json.sh")], capture_output=True, text=True, cwd=str(out_dir / "bin"), env=env, check=False)
    assert state.returncode == 0, state.stderr
    payload = json.loads(state.stdout)
    assert payload["stack_kind"] == "vhk.i3_x11.warm_runtime.state"
    assert payload["readiness"]["helper_error_count"] >= 1
    assert any(item["helper"] == "macro_inventory_json" for item in payload["readiness"]["helper_errors"])
    assert payload["sources"]["helpers"]["macro_inventory_json"]["returncode"] == 9
    assert payload["sources"]["helpers"]["macro_inventory_json"]["error"] == "broken inventory helper"
    assert payload["next_action"]["id"] in {"inspect_helper_failures", "enable_runtime_socket", "clear_prereq_blockers", "runtime_ready"}


def test_generated_dispatch_macro_checked_wrapper_blocks_and_forces(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_checked"
    wrapper = tmp_path / "vhk-wrapper.sh"
    wrapper.write_text(f"#!/usr/bin/env sh\nexec /opt/pyvenv/bin/python3 -m vhk.cli \"$@\"\n", encoding="utf-8")
    wrapper.chmod(0o755)
    repo_src = Path(__file__).resolve().parents[1] / "src"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys", "--vhk-cmd", str(wrapper), "--vhk-pythonpath", str(repo_src)])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    (bin_dir / "list_macros.sh").write_text("#!/usr/bin/env sh\nset -eu\nprintf 'sig\\n'\n")
    (bin_dir / "list_macros.sh").chmod(0o755)
    (bin_dir / "dispatch_macro.sh").write_text("#!/usr/bin/env sh\nset -eu\nprintf 'raw:%s|%s\\n' \"$1\" \"${2:-}\"\n")
    (bin_dir / "dispatch_macro.sh").chmod(0o755)

    gate_ready = {
        "dispatch_readiness": {"can_emit_minimal_payload_now": True, "blockers": []},
        "dispatch_contract": {"bus_payload_minimal": {"macro": "sig"}},
        "decision": {"reason": "ready"},
    }
    (bin_dir / "macro_dispatch_gate_json.sh").write_text("#!/usr/bin/env sh\nset -eu\ncat <<'JSON'\n" + json.dumps(gate_ready) + "\nJSON\n")
    (bin_dir / "macro_dispatch_gate_json.sh").chmod(0o755)

    ok = subprocess.run([str(bin_dir / "dispatch_macro_checked.sh"), "sig"], capture_output=True, text=True, check=False)
    assert ok.returncode == 0, ok.stderr
    assert ok.stdout.strip() == "raw:sig|{\"macro\": \"sig\"}"

    gate_blocked = {
        "dispatch_readiness": {
            "can_emit_minimal_payload_now": False,
            "blockers": ["latest_run_proof_not_clean"],
            "live_probe_hint": {"id": "window_event_probe", "summary": "Latest matching run failed around `WaitForWindowEvent`, after `window_event` waits x2.", "step_type": "WaitForWindowEvent", "wait_kind": "window_event", "wait_count": 2, "observation": {"source_id": "wait_attempt", "kind": "window_event", "attempt": 2, "summary": "Latest matching run preserved a failed live wait observation (matched=False, workspace=2, wm=i3, event=focus).", "observed": {"matched": False, "workspace": "2", "wm": "i3", "event": "focus"}}},
        },
        "dispatch_contract": {"bus_payload_minimal": {"macro": "sig"}},
        "decision": {"reason": "inspect latest run first"},
    }
    (bin_dir / "macro_dispatch_gate_json.sh").write_text("#!/usr/bin/env sh\nset -eu\ncat <<'JSON'\n" + json.dumps(gate_blocked) + "\nJSON\n")
    (bin_dir / "macro_dispatch_gate_json.sh").chmod(0o755)

    blocked = subprocess.run([str(bin_dir / "dispatch_macro_checked.sh"), "sig"], capture_output=True, text=True, check=False)
    assert blocked.returncode == 4
    assert "latest_run_proof_not_clean" in blocked.stderr
    assert "inspect latest run first" in blocked.stderr

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_src)
    latest_dispatch = subprocess.run([str(bin_dir / "latest_dispatch_json.sh")], capture_output=True, text=True, env=env, check=False)
    assert latest_dispatch.returncode == 0, latest_dispatch.stderr
    latest_payload = json.loads(latest_dispatch.stdout)
    assert latest_payload["latest_dispatch"]["macro"] == "sig"
    assert latest_payload["latest_dispatch"]["result"] == "blocked"
    assert latest_payload["latest_dispatch"]["route"] == "checked_dispatch"
    assert "latest_run_proof_not_clean" in latest_payload["latest_dispatch"]["stderr"]
    assert "inspect latest run first" in latest_payload["latest_dispatch"]["stderr"]
    assert latest_payload["latest_dispatch"]["gate"]["live_probe_hint"]["id"] == "window_event_probe"
    assert latest_payload["latest_dispatch"]["gate"]["live_probe_hint"]["observation"]["observed"]["event"] == "focus"
    assert "inspect latest run first" in latest_payload["latest_dispatch"]["gate"]["blocked_message"]

    forced = subprocess.run([str(bin_dir / "dispatch_macro_checked.sh"), "--force", "sig", "{\"macro\":\"sig\",\"vars\":{\"x\":1}}"], capture_output=True, text=True, check=False)
    assert forced.returncode == 0, forced.stderr
    assert forced.stdout.strip() == "raw:sig|{\"macro\":\"sig\",\"vars\":{\"x\":1}}"


def test_generated_dispatch_receipt_tracks_emitted_checked_dispatch(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_receipts"
    wrapper = tmp_path / "vhk-wrapper.sh"
    wrapper.write_text(
        f"#!/usr/bin/env sh\n"
        f"if [ \"${{1:-}}\" = \"emit-bus\" ]; then\n"
        f"  shift\n"
        f"  printf 'emit:%s|%s\\n' \"$2\" \"$4\"\n"
        f"  exit 0\n"
        f"fi\n"
        f"exec {sys.executable} -m vhk.cli \"$@\"\n",
        encoding="utf-8",
    )
    wrapper.chmod(0o755)

    repo_src = Path(__file__).resolve().parents[1] / "src"
    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys", "--vhk-cmd", str(wrapper), "--vhk-pythonpath", str(repo_src)])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(
        bin_dir / "macro_dispatch_gate_json.sh",
        {
            "dispatch_readiness": {"can_emit_minimal_payload_now": True, "blockers": []},
            "dispatch_contract": {"bus_payload_minimal": {"macro": "sig"}},
            "decision": {"id": "dispatch_now", "reason": "ready"},
            "preferred_execution_mode": "warm_runtime_dispatch",
        },
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_src)
    ok = subprocess.run([str(bin_dir / "dispatch_macro_checked.sh"), "sig"], capture_output=True, text=True, env=env, check=False)
    assert ok.returncode == 0, ok.stderr
    assert "emit:hotkey|{\"macro\": \"sig\"}" in ok.stdout.strip()

    latest_dispatch = subprocess.run([str(bin_dir / "latest_dispatch_json.sh")], capture_output=True, text=True, env=env, check=False)
    assert latest_dispatch.returncode == 0, latest_dispatch.stderr
    payload = json.loads(latest_dispatch.stdout)
    assert payload["stack_kind"] == "vhk.project.latest_dispatch"
    assert payload["latest_dispatch"]["macro"] == "sig"
    assert payload["latest_dispatch"]["result"] == "emitted"
    assert payload["latest_dispatch"]["route"] == "checked_dispatch"
    assert payload["latest_dispatch"]["checked_gate"] is True
    assert payload["latest_dispatch"]["payload"]["json"] == {"macro": "sig"}
    assert payload["latest_dispatch"]["desktop_session_contract"]["status"] == "in_sync"



def _write_json_stub(path: Path, payload: dict) -> None:
    path.write_text(
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        "cat <<'JSON'\n"
        f"{json.dumps(payload)}\n"
        "JSON\n"
    )
    path.chmod(0o755)


def test_generated_next_action_helper_consumes_macro_review_queue(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(
        bin_dir / "check_runtime_json.sh",
        {
            "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
            "env": {"session_ready": True},
            "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
            "capabilities": {"warm_runtime": True},
            "health": {"blockers": [], "warnings": []},
        },
    )
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "reasons": [], "next_step": {}}})
    _write_json_stub(
        bin_dir / "macro_inventory_json.sh",
        {
            "project": {
                "macro_count": 1,
                "groups": [],
                "tags": [],
                "recording_sidecar_missing_count": 0,
                "recording_sidecar_stale_count": 1,
                "recording_sidecar_newer_than_source_count": 0,
                "macros_with_exact_recording_segments": 0,
                "macros_with_title_recording_segments": 0,
            },
            "macros": [{"name": "sig"}],
        },
    )
    _write_json_stub(
        bin_dir / "macro_review_queue_json.sh",
        {
            "counts": {
                "missing_recording_sidecars": 0,
                "stale_recording_sidecars": 1,
                "recording_newer_than_source": 0,
                "exact_segment_macros": 0,
                "title_segment_macros": 0,
                "needs_review_count": 1,
            },
            "queue": {
                "missing_recording_sidecars": [],
                "stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
                "recording_newer_than_source": [],
                "exact_segment_macros": [],
                "title_segment_macros": [],
            },
            "ordered": [{"name": "sig", "kind": "stale_recording_sidecar"}],
        },
    )
    _write_json_stub(
        bin_dir / "macro_author_queue_json.sh",
        {
            "summary": {"primary_macro_name": "sig", "primary_action_id": "refresh_recording_review"},
            "primary_macro": {
                "name": "sig",
                "preferred_execution_mode": "warm_runtime_dispatch",
                "next_step": {
                    "id": "refresh_recording_review",
                    "summary": "Review or refresh recorder evidence because the macro source is newer than the sidecar.",
                    "reason": "Recorder context may be stale relative to the editable macro source.",
                    "command": "macro_recording_json.sh sig",
                    "followup": ["record_macro.sh sig 5000"],
                },
                "dispatch_attention": {"id": "none", "needs_attention": False},
                "priority": {"effective_rank": 1},
            },
            "macros": [{"name": "sig"}],
        },
    )
    _write_json_stub(
        bin_dir / "macro_dispatch_gate_json.sh",
        {
            "repair_action": {"id": "repair_recorder_contract", "command": "macro_recording_json.sh sig"},
            "decision": {"id": "stabilize_before_dispatch", "command": "macro_author_loop_json.sh sig"},
            "dispatch_readiness": {"can_emit_minimal_payload_now": False},
        },
    )

    payload = json.loads(subprocess.check_output([str(bin_dir / "next_action_json.sh")], text=True))
    assert payload["review_counts"]["stale_recording_sidecars"] == 1
    assert payload["macro_review_queue"]["stale_recording_sidecars"][0]["name"] == "sig"
    assert payload["primary_action"]["id"] == "refresh_recording_review"
    assert payload["primary_action"]["command"] == "./bin/macro_recording_json.sh sig"
    assert payload["recommendation_trace"]["selected_action_id"] == "refresh_recording_review"
    assert payload["review_queue_source"]["mode"] == "authoritative_helper"
    assert payload["macro_author_queue"]["primary_macro"]["name"] == "sig"



def test_generated_next_action_helper_uses_dispatch_gate_for_ready_primary_macro(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_ready"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(
        bin_dir / "check_runtime_json.sh",
        {
            "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
            "env": {"session_ready": True},
            "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
            "capabilities": {"warm_runtime": True},
            "health": {"blockers": [], "warnings": []},
        },
    )
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "reasons": [], "next_step": {}}})
    _write_json_stub(
        bin_dir / "macro_author_queue_json.sh",
        {
            "summary": {"primary_macro_name": "sig", "primary_action_id": "dispatch_or_run"},
            "primary_macro": {
                "name": "sig",
                "preferred_execution_mode": "warm_runtime_dispatch",
                "next_step": {
                    "id": "dispatch_or_run",
                    "summary": "Execute the macro through the preferred lane and inspect the resulting artifacts.",
                    "reason": "Recorder evidence is present and no macro-specific review blockers were detected.",
                    "command": "dispatch_macro.sh sig",
                    "followup": ["macro_contract_json.sh sig", "macro_latest_run_json.sh sig"],
                },
                "dispatch_attention": {"id": "none", "needs_attention": False},
                "priority": {"effective_rank": 7},
            },
            "macros": [{"name": "sig"}],
        },
    )
    _write_json_stub(
        bin_dir / "macro_dispatch_gate_json.sh",
        {
            "preferred_execution_mode": "warm_runtime_dispatch",
            "decision": {"id": "dispatch_now", "command": "dispatch_macro_checked.sh sig", "reason": "ready"},
            "repair_action": {"id": "ready_to_dispatch", "command": "dispatch_macro_checked.sh sig", "followup": ["latest_run_json.sh", "macro_report_latest.sh sig"], "reason": "ready"},
            "dispatch_readiness": {"can_emit_minimal_payload_now": True, "blockers": []},
        },
    )

    payload = json.loads(subprocess.check_output([str(bin_dir / "next_action_json.sh")], text=True))
    assert payload["primary_action"]["id"] == "ready_to_dispatch"
    assert payload["primary_action"]["command"] == "./bin/dispatch_macro_checked.sh sig"
    assert payload["dispatch_gate"]["repair_action"]["id"] == "ready_to_dispatch"
    assert payload["macro_author_queue"]["primary_macro"]["name"] == "sig"
    assert payload["recommendation_trace"]["selected_action_id"] == "ready_to_dispatch"


def test_generated_stack_state_json_carries_runtime_board(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(
        bin_dir / "check_runtime_json.sh",
        {
            "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
            "env": {"session_ready": True},
            "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
            "capabilities": {"warm_runtime": True},
            "health": {"blockers": [], "warnings": []},
        },
    )
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(
        bin_dir / "macro_inventory_json.sh",
        {
            "project": {
                "macro_count": 1,
                "groups": [],
                "tags": [],
                "recording_sidecar_count": 1,
                "recording_sidecar_missing_count": 0,
                "recording_sidecar_stale_count": 0,
                "recording_sidecar_newer_than_source_count": 0,
                "macros_with_exact_recording_segments": 0,
                "macros_with_title_recording_segments": 0,
            },
            "macros": [{"name": "sig"}],
        },
    )
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy", "summary": "healthy replay"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "repeat_or_trace", "command": "./bin/macro_report_latest.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector", "selector": {"class": "Alacritty", "workspace": "2"}}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {"generated_stack": {"dispatch_checked_wrapper": "dispatch_macro_checked.sh sig"}}, "authoring": {"workflow": {"preferred_loop": ["source", "recording_review", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(
        bin_dir / "macro_runtime_board_json.sh",
        {
            "summary": {
                "primary_macro_name": "sig",
                "primary_posture_id": "warm_dispatch_ready",
                "counts_by_posture_id": {"warm_dispatch_ready": 1},
            },
            "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}},
            "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}],
        },
    )
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "clean_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(
        bin_dir / "next_action_json.sh",
        {"primary_action": {"id": "runtime_ready", "command": "./bin/dispatch_macro.sh sig"}},
    )

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["macro_replay_board"]["summary"]["primary_macro_name"] == "sig"
    assert payload["macro_replay_board"]["summary"]["primary_posture_id"] == "verified_recent"
    assert payload["sources"]["helpers"]["macro_replay_board_json"]["primary_posture_id"] == "verified_recent"
    assert payload["primary_macro_latest_run"]["macro_name"] == "sig"
    assert payload["primary_macro_latest_run"]["latest_run_health"]["verdict"] == "healthy"
    assert payload["sources"]["helpers"]["macro_latest_run_json"]["verdict"] == "healthy"
    assert payload["primary_macro_contract"]["macro_name"] == "sig"
    assert payload["primary_macro_contract"]["macro"]["desktop_target"]["selector_source_id"] == "recording_stable_selector"
    assert payload["primary_macro_contract"]["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert payload["sources"]["helpers"]["macro_contract_json"]["desktop_target_source_id"] == "recording_stable_selector"
    assert payload["macro_runtime_board"]["summary"]["primary_macro_name"] == "sig"
    assert payload["macro_runtime_board"]["summary"]["primary_posture_id"] == "warm_dispatch_ready"
    assert payload["sources"]["helpers"]["macro_runtime_board_json"]["primary_posture_id"] == "warm_dispatch_ready"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "replay_board_primary_macro=sig" in summary
    assert "replay_board_primary_posture=verified_recent" in summary
    assert "primary_macro_latest_run_macro=sig" in summary
    assert "primary_macro_latest_run_verdict=healthy" in summary
    assert "primary_macro_replay_posture=verified_recent" in summary
    assert "primary_macro_contract_macro=sig" in summary
    assert "primary_macro_contract_target_source=recording_stable_selector" in summary
    assert "primary_macro_contract_execution_mode=warm_runtime_dispatch" in summary
    assert "runtime_board_primary_macro=sig" in summary
    assert "runtime_board_primary_posture=warm_dispatch_ready" in summary


def test_generated_stack_state_json_carries_primary_dispatch_gate(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_dispatch_gate"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn", "ready_to_iterate": False}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": False}, "latest_run_health": {"verdict": "fail", "summary": "latest run failed"}, "replay_posture": {"id": "failed_recent"}, "next_step": {"id": "inspect_run_history", "command": "./bin/macro_report_latest.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {"generated_stack": {"dispatch_checked_wrapper": "dispatch_macro_checked.sh sig"}}, "authoring": {"workflow": {"preferred_loop": ["source", "recording_review", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent", "counts_by_posture_id": {"warning_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_candidate", "counts_by_posture_id": {"warm_dispatch_candidate": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "repeated_desktop_state_mismatch", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "inspect_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}, "repair_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig"}, "dispatch_readiness": {"primary_blocker_class_id": "desktop_state_mismatch", "blocked_message": "focus/title mismatch"}, "preferred_execution_mode": "warm_runtime_dispatch"})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}, "recommendation_trace": {"selected_action_id": "inspect_before_dispatch"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["macro_dispatch_gate"]["primary_macro_name"] == "sig"
    assert payload["macro_dispatch_gate"]["decision"]["id"] == "inspect_before_dispatch"
    assert payload["macro_dispatch_gate"]["repair_action"]["id"] == "inspect_live_desktop_target"
    assert payload["primary_macro_latest_run"]["latest_run_health"]["verdict"] == "fail"
    assert payload["primary_macro_latest_run"]["replay_posture"]["id"] == "failed_recent"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["decision_id"] == "inspect_before_dispatch"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["primary_blocker_class_id"] == "desktop_state_mismatch"
    assert payload["sources"]["helpers"]["macro_latest_run_json"]["verdict"] == "fail"
    assert payload["primary_macro_contract"]["macro"]["desktop_target"]["selector"]["workspace"] == "2"
    assert payload["sources"]["helpers"]["macro_contract_json"]["desktop_target_source_id"] == "macro_when"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "dispatch_gate_primary_macro=sig" in summary
    assert "dispatch_gate_decision=inspect_before_dispatch" in summary
    assert "dispatch_gate_repair_action=inspect_live_desktop_target" in summary
    assert "dispatch_gate_primary_blocker_class=desktop_state_mismatch" in summary
    assert "primary_macro_latest_run_macro=sig" in summary
    assert "primary_macro_latest_run_verdict=fail" in summary
    assert "primary_macro_replay_posture=failed_recent" in summary
    assert "primary_macro_contract_macro=sig" in summary
    assert "primary_macro_contract_target_source=macro_when" in summary


def test_generated_stack_state_json_carries_primary_macro_latest_run(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_latest"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {
        "macro": {"name": "sig"},
        "latest_run": {"macro": "sig", "ok": True, "run_id": "run-123"},
        "latest_run_health": {"verdict": "warn", "summary": "Latest matching run shows flakiness.", "next_step": {"id": "review_run_history"}},
        "replay_posture": {"id": "warning_recent"},
        "next_step": {"id": "review_run_history", "command": "./bin/macro_report_latest.sh sig"},
        "preferred_entrypoints": {"latest_report": "./bin/macro_report_latest.sh sig"},
    })
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "inspect_before_dispatch"}, "repair_action": {"id": "refresh_matching_run_proof"}, "dispatch_readiness": {"primary_blocker_class_id": "run_proof_gap"}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent", "counts_by_posture_id": {"warning_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first", "counts_by_posture_id": {"stabilize_first": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "repeated_run_proof_gap", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "repeated_run_proof_gap"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "repeated_run_proof_gap"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "review_run_history", "command": "./bin/macro_report_latest.sh sig"}, "recommendation_trace": {"selected_action_id": "review_run_history"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_latest_run"]["macro_name"] == "sig"
    assert payload["primary_macro_latest_run"]["latest_run"]["run_id"] == "run-123"
    assert payload["primary_macro_latest_run"]["latest_run_health"]["verdict"] == "warn"
    assert payload["primary_macro_latest_run"]["replay_posture"]["id"] == "warning_recent"
    assert payload["primary_macro_latest_run"]["next_step"]["id"] == "review_run_history"
    assert payload["sources"]["helpers"]["macro_latest_run_json"]["primary_macro_name"] == "sig"
    assert payload["sources"]["helpers"]["macro_latest_run_json"]["verdict"] == "warn"
    assert payload["sources"]["helpers"]["macro_latest_run_json"]["replay_posture_id"] == "warning_recent"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_latest_run_macro=sig" in summary
    assert "primary_macro_latest_run_verdict=warn" in summary
    assert "primary_macro_replay_posture=warning_recent" in summary
    assert "primary_macro_latest_run_next_step=review_run_history" in summary


def test_generated_stack_state_json_carries_primary_macro_acceptance(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_acceptance"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 2, "groups": [], "tags": []}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 2, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 2, "review_acceptance_macro_count": 2, "runtime_acceptance_macro_count": 2}, "macros": [{"name": "other", "review_acceptances": [{"issue_code": "stale_recording_sidecar", "signoff_complete": True}], "accepted_review_issue_codes": ["stale_recording_sidecar"], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "verified_recent", "signoff_complete": True}}, {"name": "sig", "review_acceptances": [{"issue_code": "exact_recording_segments", "signoff_complete": True}, {"issue_code": "title_recording_segments", "signoff_complete": False}], "accepted_review_issue_codes": ["exact_recording_segments"], "incomplete_review_issue_codes": ["title_recording_segments"], "runtime_acceptance": {"posture_id": "warm_dispatch_ready", "signoff_complete": True}}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 1}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_acceptance"]["macro_name"] == "sig"
    assert payload["primary_macro_acceptance"]["runtime_acceptance"]["posture_id"] == "warm_dispatch_ready"
    assert payload["primary_macro_acceptance"]["accepted_review_issue_codes"] == ["exact_recording_segments"]
    assert payload["primary_macro_acceptance"]["incomplete_review_issue_codes"] == ["title_recording_segments"]
    assert payload["sources"]["helpers"]["macro_acceptance_ledger_json"]["selected_macro_name"] == "sig"
    assert payload["sources"]["helpers"]["macro_acceptance_ledger_json"]["selected_macro_runtime_posture_id"] == "warm_dispatch_ready"
    assert payload["sources"]["helpers"]["macro_acceptance_ledger_json"]["selected_macro_incomplete_issue_count"] == 1

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_acceptance_macro=sig" in summary
    assert "primary_macro_acceptance_runtime_posture=warm_dispatch_ready" in summary
    assert "primary_macro_acceptance_review_count=2" in summary
    assert "primary_macro_acceptance_incomplete_issue_count=1" in summary



def test_generated_stack_state_json_carries_primary_macro_acceptance_ticket_ready_for_signoff(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_acceptance_ticket_ready"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig", "author_loop": "./bin/macro_author_loop_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "dispatch_now"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}, "preferred_execution_mode": "warm_runtime_dispatch"})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "run_id": "run-123", "ok": True}, "latest_run_health": {"verdict": "healthy", "summary": "looks good"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "repeat_or_trace", "command": "./bin/macro_report_latest.sh sig"}, "preferred_entrypoints": {"latest_run_json": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "history": "./bin/history_runs.sh --macro sig --limit 5"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"summary": "Firefox on workspace 2"}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}, "invocation": {"generated_stack": {"dispatch_checked_wrapper": "./bin/dispatch_macro_checked.sh sig", "report_latest_wrapper": "./bin/macro_report_latest.sh sig", "trace_latest_wrapper": "./bin/macro_trace_latest.sh sig", "latest_run_wrapper": "./bin/macro_latest_run_json.sh sig", "author_loop_wrapper": "./bin/macro_author_loop_json.sh sig"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"preferred_execution_mode": "warm_runtime_dispatch"}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"exists": True, "has_recorded_context": True, "freshness": {"status": "current"}, "selector_summary": {"selector_source_id": "macro_when", "exact_segment_count": 0, "title_segment_count": 0, "workspace_segment_count": 0}, "transition_reason_counts": {"title": 0, "workspace": 0}}, "review": {"commands": {"record_shell": "./bin/record_macro.sh sig", "cleanup_review_shell": "./bin/optimize_macro.sh sig", "cleanup_apply_shell": "./bin/apply_optimize_macro.sh sig"}, "generated_stack": {"record": "./bin/record_macro.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}, "latest_run": {"run_id": "run-123"}, "latest_run_health": {"verdict": "healthy"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "missing", "matches_current_posture": False, "posture_id": None}}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"result": "emitted", "route": "checked_dispatch"}}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"result": "emitted", "route": "checked_dispatch"}}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"route": "checked_dispatch"}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"route": "checked_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"ledger_source": {"path": str((proj / "acceptance" / "macro_acceptance.yaml")), "relative_path": "acceptance/macro_acceptance.yaml", "exists": True, "format": "yaml"}, "summary": {"accepted_macro_count": 1, "review_acceptance_macro_count": 1, "runtime_acceptance_macro_count": 0}, "macros": [{"name": "sig", "review_acceptances": [{"issue_code": "exact_recording_segments", "signoff_complete": True}], "accepted_review_issue_codes": ["exact_recording_segments"], "incomplete_review_issue_codes": [], "runtime_acceptance": None}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "recommendation_trace": {"selected_action_id": "dispatch_now"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_acceptance_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "ready_for_signoff"
    assert ticket["route_id"] == "verify_then_update_acceptance"
    assert ticket["recommended"]["command"] == "./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>"
    assert ticket["ledger_update_handoff"]["ledger_source"]["relative_path"] == "acceptance/macro_acceptance.yaml"
    assert ticket["ledger_update_handoff"]["suggested_entry"]["runtime_acceptance"]["posture_id"] == "warm_dispatch_ready"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_acceptance_ticket_status_id"] == "ready_for_signoff"
    assert payload["sources"]["helpers"]["macro_acceptance_ledger_json"]["selected_macro_acceptance_ticket_status_id"] == "ready_for_signoff"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_acceptance_ticket_macro=sig" in summary
    assert "primary_macro_acceptance_ticket_status=ready_for_signoff" in summary
    assert "primary_macro_acceptance_ticket_route=verify_then_update_acceptance" in summary
    assert "primary_macro_acceptance_ticket_command=./bin/record_runtime_acceptance.sh sig --accepted-by <operator> --note <why-this-posture-is-acceptable>" in summary


def test_generated_stack_state_json_carries_primary_macro_acceptance_ticket_repair_before_signoff(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_acceptance_ticket_repair"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig", "author_loop": "./bin/macro_author_loop_json.sh sig", "contract": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "dispatch_now"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig", "summary": "gate says ready now"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}, "preferred_execution_mode": "warm_runtime_dispatch"})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "run_id": "run-321", "ok": True}, "latest_run_health": {"verdict": "healthy", "summary": "looks good"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "repeat_or_trace", "command": "./bin/macro_report_latest.sh sig"}, "preferred_entrypoints": {"latest_run_json": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "history": "./bin/history_runs.sh --macro sig --limit 5"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"summary": "Firefox on workspace 2"}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}, "invocation": {"generated_stack": {"dispatch_checked_wrapper": "./bin/dispatch_macro_checked.sh sig", "dispatch_gate_wrapper": "./bin/macro_dispatch_gate_json.sh sig", "report_latest_wrapper": "./bin/macro_report_latest.sh sig", "trace_latest_wrapper": "./bin/macro_trace_latest.sh sig", "latest_run_wrapper": "./bin/macro_latest_run_json.sh sig", "author_loop_wrapper": "./bin/macro_author_loop_json.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"preferred_execution_mode": "warm_runtime_dispatch"}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"exists": True, "has_recorded_context": True, "freshness": {"status": "current"}, "selector_summary": {"selector_source_id": "macro_when", "exact_segment_count": 0, "title_segment_count": 0, "workspace_segment_count": 0}, "transition_reason_counts": {"title": 0, "workspace": 0}}, "review": {"commands": {"record_shell": "./bin/record_macro.sh sig", "cleanup_review_shell": "./bin/optimize_macro.sh sig", "cleanup_apply_shell": "./bin/apply_optimize_macro.sh sig"}, "generated_stack": {"record": "./bin/record_macro.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}, "latest_run": {"run_id": "run-321"}, "latest_run_health": {"verdict": "healthy"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "accepted", "matches_current_posture": True, "posture_id": "warm_dispatch_ready", "accepted_by": "dev", "accepted_at": "2026-03-21T19:00:00Z"}}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "acceptance": {"runtime_signoff": {"status": "accepted", "matches_current_posture": True, "posture_id": "warm_dispatch_ready", "accepted_by": "dev", "accepted_at": "2026-03-21T19:00:00Z"}}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_attention", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_attention"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_attention"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"route": "checked_dispatch"}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"route": "checked_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"ledger_source": {"path": str((proj / "acceptance" / "macro_acceptance.yaml")), "relative_path": "acceptance/macro_acceptance.yaml", "exists": True, "format": "yaml"}, "summary": {"accepted_macro_count": 1, "review_acceptance_macro_count": 1, "runtime_acceptance_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [{"issue_code": "exact_recording_segments", "signoff_complete": True}], "accepted_review_issue_codes": ["exact_recording_segments"], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "warm_dispatch_ready", "accepted_by": "dev", "accepted_at": "2026-03-21T19:00:00Z", "signoff_complete": True}}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "recommendation_trace": {"selected_action_id": "dispatch_now"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_acceptance_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "repair_before_signoff"
    assert ticket["route_id"] == "repair_then_acceptance_review"
    assert ticket["recommended"]["command"] == payload["primary_macro_repair_recipe"]["recommended"]["command"]
    assert payload["primary_macro_consistency"]["status_id"] == "contradictions_present"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_acceptance_ticket_status_id"] == "repair_before_signoff"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_acceptance_ticket_macro=sig" in summary
    assert "primary_macro_acceptance_ticket_status=repair_before_signoff" in summary
    assert "primary_macro_acceptance_ticket_route=repair_then_acceptance_review" in summary
    assert f"primary_macro_acceptance_ticket_command={ticket['recommended']['command']}" in summary


def test_generated_stack_state_json_carries_primary_macro_board_slices(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_slices"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml", "macros/other.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "other", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 2, "groups": [], "tags": []}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 2, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"warm_runtime_checked": "dispatch_macro_checked.sh sig", "direct_run": "run_macro.sh sig"}}, {"name": "other", "execution": {"preferred_mode": "direct_run"}, "preferred_entrypoints": {"direct_run": "run_macro.sh other"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "dispatch_now"}, "repair_action": {"id": "ready_to_dispatch"}, "dispatch_readiness": {"primary_blocker_class_id": None}, "preferred_execution_mode": "warm_runtime_dispatch"})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_or_run"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector"}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {}, "authoring": {}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "dispatch_history": {"id": "dispatch_clean_recently"}, "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_or_run"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}, "selector_summary": {"selector_source_id": "recording_stable_selector"}}, "review": {}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "other", "primary_posture_id": "failed_recent", "counts_by_posture_id": {"failed_recent": 1, "verified_recent": 1}}, "primary_macro": {"name": "other", "replay_posture": {"id": "failed_recent"}}, "macros": [{"name": "other", "replay_posture": {"id": "failed_recent"}}, {"name": "sig", "replay_posture": {"id": "verified_recent"}, "latest_run_health": {"verdict": "healthy"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "other", "primary_posture_id": "stabilize_first", "counts_by_posture_id": {"stabilize_first": 1, "warm_dispatch_ready": 1}}, "primary_macro": {"name": "other", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "other", "runtime_posture": {"id": "stabilize_first"}}, {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}, "dispatch_attention": {"id": "none"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "other", "primary_posture_id": "repeated_contract_debt", "attention_macro_count": 1}, "primary_macro": {"name": "other", "dispatch_history_posture": {"id": "repeated_contract_debt", "attention_id": "repeated_contract_debt"}}, "macros": [{"name": "other", "dispatch_history_posture": {"id": "repeated_contract_debt", "attention_id": "repeated_contract_debt"}}, {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently", "attention_id": "none"}, "dispatch_history": {"primary_blocked_class_id": None}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "other", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "other", "preferred_execution_mode": "direct_run", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}, "macros": [{"name": "other", "preferred_execution_mode": "direct_run", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}, {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"bus_event": "hotkey"}}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "recommendation_trace": {"selected_action_id": "ready_to_dispatch"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["macro_replay_board"]["summary"]["primary_macro_name"] == "other"
    assert payload["primary_macro_replay_board"]["macro_name"] == "sig"
    assert payload["primary_macro_replay_board"]["replay_posture"]["id"] == "verified_recent"
    assert payload["primary_macro_runtime_board"]["macro_name"] == "sig"
    assert payload["primary_macro_runtime_board"]["runtime_posture"]["id"] == "warm_dispatch_ready"
    assert payload["primary_macro_dispatch_history"]["macro_name"] == "sig"
    assert payload["primary_macro_dispatch_history"]["dispatch_history_posture"]["id"] == "dispatch_clean_recently"
    assert payload["primary_macro_dispatch_catalog"]["macro_name"] == "sig"
    assert payload["primary_macro_dispatch_catalog"]["dispatch_readiness"]["can_emit_minimal_payload_now"] is True
    assert payload["primary_macro_dispatch_catalog"]["preferred_execution_mode"] == "warm_runtime_dispatch"
    assert payload["sources"]["helpers"]["macro_replay_board_json"]["selected_macro_name"] == "sig"
    assert payload["sources"]["helpers"]["macro_replay_board_json"]["selected_macro_posture_id"] == "verified_recent"
    assert payload["sources"]["helpers"]["macro_runtime_board_json"]["selected_macro_posture_id"] == "warm_dispatch_ready"
    assert payload["sources"]["helpers"]["macro_dispatch_history_board_json"]["selected_macro_posture_id"] == "dispatch_clean_recently"
    assert payload["sources"]["helpers"]["macro_dispatch_catalog_json"]["selected_macro_dispatch_ready"] is True

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_replay_board_macro=sig" in summary
    assert "primary_macro_replay_board_posture=verified_recent" in summary
    assert "primary_macro_runtime_board_macro=sig" in summary
    assert "primary_macro_runtime_board_posture=warm_dispatch_ready" in summary
    assert "primary_macro_dispatch_history_macro=sig" in summary
    assert "primary_macro_dispatch_history_posture=dispatch_clean_recently" in summary
    assert "primary_macro_dispatch_catalog_macro=sig" in summary
    assert "primary_macro_dispatch_catalog_mode=warm_runtime_dispatch" in summary
    assert "primary_macro_dispatch_catalog_ready=True" in summary


def test_generated_stack_state_json_carries_primary_macro_execution_brief(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_execution_brief"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn", "ready_to_iterate": False}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": False}, "latest_run_health": {"verdict": "warn", "summary": "latest run still warns"}, "replay_posture": {"id": "warning_recent"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig", "reason": "inspect warnings"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "recording_stable_selector"}, "hints": {"has_interactive_inputs": False}, "prompt_steps": []}, "invocation": {"generated_stack": {"dispatch_checked_wrapper": "dispatch_macro_checked.sh sig"}}, "authoring": {"workflow": {"preferred_loop": ["source", "recording_review", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "stabilize_first"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "stabilize_before_dispatch"}}}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig", "reason": "inspect warnings"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}, "review": {}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "repeated_desktop_state_mismatch", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "stabilize_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}, "repair_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig", "reason": "live desktop state still mismatches the target"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 1}, "queue": {"stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}]}, "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [{"issue_code": "segments_ok"}], "incomplete_review_issue_codes": ["desktop_target_needs_refresh"], "runtime_acceptance": {"posture_id": "needs_refresh"}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    brief = payload["primary_macro_execution_brief"]
    assert brief["macro_name"] == "sig"
    assert brief["action_bias_id"] == "review_queue_repair"
    assert brief["recommended"]["command"] == "./bin/macro_recording_json.sh sig"
    assert brief["signals"]["review_queue_present"] is True
    assert brief["signals"]["runtime_posture_id"] == "stabilize_first"
    assert brief["signals"]["replay_posture_id"] == "warning_recent"
    assert brief["signals"]["repair_action_id"] == "inspect_live_desktop_target"
    assert brief["signals"]["latest_dispatch_result"] == "blocked"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_action_bias_id"] == "review_queue_repair"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_recommended_command"] == "./bin/macro_recording_json.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_execution_brief_macro=sig" in summary
    assert "primary_macro_execution_brief_action_bias=review_queue_repair" in summary
    assert "primary_macro_execution_brief_recommended_command=./bin/macro_recording_json.sh sig" in summary
    ticket = payload["primary_macro_execution_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "repair_before_execute"
    assert ticket["route_id"] == "review_then_execute"
    assert ticket["recommended"]["command"] == "./bin/macro_recording_json.sh sig"
    assert ticket["preflight_commands"] == ["./bin/macro_contract_json.sh sig", "./bin/macro_dispatch_gate_json.sh sig"]
    assert ticket["verify_commands"] == ["./bin/macro_latest_run_json.sh sig", "./bin/macro_report_latest.sh sig", "./bin/macro_dispatch_gate_json.sh sig", "./bin/dispatch_macro_checked.sh sig"]
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_execution_ticket_status_id"] == "repair_before_execute"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_execution_ticket_route_id"] == "review_then_execute"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_execution_ticket_command"] == "./bin/macro_recording_json.sh sig"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_execution_ticket_status_id"] == "repair_before_execute"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_execution_ticket_route_id"] == "review_then_execute"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_execution_ticket_command"] == "./bin/macro_recording_json.sh sig"
    assert "primary_macro_execution_ticket_macro=sig" in summary
    assert "primary_macro_execution_ticket_status=repair_before_execute" in summary
    assert "primary_macro_execution_ticket_route=review_then_execute" in summary
    assert "primary_macro_execution_ticket_command=./bin/macro_recording_json.sh sig" in summary



def test_generated_stack_state_json_carries_primary_macro_execution_ticket_dispatch_ready(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_execution_ticket_dispatch_ready"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok", "summary": "latest run is clean"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_again", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when", "summary": "Dispatch expects the focused X11 window to match the macro when: selector."}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"bus_event": "hotkey", "bus_payload_minimal": {"macro": "sig"}, "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "emit_bus_command": "./bin/dispatch_macro.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig", "reason": "gate and latest run both say the macro can emit now"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_execution_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "dispatch_ready"
    assert ticket["execution_mode_id"] == "warm_runtime_dispatch"
    assert ticket["route_id"] == "checked_warm_dispatch"
    assert ticket["recommended"]["command"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["preflight_commands"] == ["./bin/macro_dispatch_gate_json.sh sig", "./bin/macro_contract_json.sh sig", "./bin/macro_latest_run_json.sh sig"]
    assert ticket["verify_commands"] == ["./bin/latest_dispatch_json.sh", "./bin/macro_latest_run_json.sh sig", "./bin/macro_report_latest.sh sig", "./bin/macro_trace_latest.sh sig"]
    assert ticket["route_contract"]["bus_event"] == "hotkey"
    assert ticket["route_contract"]["generated_stack_checked_command"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["route_contract"]["selector_source_id"] == "macro_when"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_execution_ticket_status_id"] == "dispatch_ready"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_execution_ticket_route_id"] == "checked_warm_dispatch"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_execution_ticket_command"] == "./bin/dispatch_macro_checked.sh sig"
    runtime_ticket = payload["warm_runtime_ticket"]
    assert runtime_ticket["status_id"] == "runtime_ready_for_selected_macro"
    assert runtime_ticket["route_id"] == "ready_then_selected_macro"
    assert runtime_ticket["recommended"]["command"] == "./bin/dispatch_macro_checked.sh sig"
    assert runtime_ticket["selected_macro_handoff"]["macro_name"] == "sig"
    assert runtime_ticket["selected_macro_handoff"]["execution_ticket_status_id"] == "dispatch_ready"
    assert payload["sources"]["helpers"]["status_runtime_json"]["selected_warm_runtime_ticket_status_id"] == "runtime_ready_for_selected_macro"
    assert payload["sources"]["helpers"]["check_runtime_json"]["selected_warm_runtime_ticket_route_id"] == "ready_then_selected_macro"
    assert payload["sources"]["helpers"]["next_action_json"]["selected_warm_runtime_ticket_command"] == "./bin/dispatch_macro_checked.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_execution_ticket_macro=sig" in summary
    assert "primary_macro_execution_ticket_status=dispatch_ready" in summary
    assert "primary_macro_execution_ticket_route=checked_warm_dispatch" in summary
    assert "primary_macro_execution_ticket_command=./bin/dispatch_macro_checked.sh sig" in summary
    assert "warm_runtime_ticket_status=runtime_ready_for_selected_macro" in summary
    assert "warm_runtime_ticket_route=ready_then_selected_macro" in summary
    assert "warm_runtime_ticket_command=./bin/dispatch_macro_checked.sh sig" in summary



def test_generated_stack_state_json_carries_warm_runtime_ticket_activation_env_sync(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_warm_runtime_ticket_activation_env_sync"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}, "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"}, "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}}})
    _write_json_stub(bin_dir / "check_runtime_json.sh", {
        "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
        "env": {"session_ready": False, "DISPLAY": ":0", "XAUTHORITY": "/tmp/Xauthority", "XDG_RUNTIME_DIR": "/run/user/1000", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus", "I3SOCK": "/run/user/1000/i3/ipc.sock"},
        "session_attachment": {
            "status": "activation_environment_drift",
            "ready": False,
            "activation_environment": {"status": "drift", "in_sync": False},
            "commands": {"sync_activation_environment": "dbus-update-activation-environment --systemd DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS XDG_RUNTIME_DIR I3SOCK"},
            "blockers": ["activation environment drift"],
            "warnings": [],
        },
        "health": {"blockers": ["activation environment drift"], "warnings": []},
        "capabilities": {"warm_runtime": True},
        "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"},
    })
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_again", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when"}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"bus_event": "hotkey", "bus_payload_minimal": {"macro": "sig"}, "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "emit_bus_command": "./bin/dispatch_macro.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig", "reason": "gate and latest run both say the macro can emit now"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "startup_handoff_status_json.sh", {"startup_handoff": {"verdict": "primary_owner_ready", "autostart": {"state": "hidden"}, "counts": {"enabled_unit_count": 1}}})
    _write_json_stub(bin_dir / "startup_handoff_drift_json.sh", {"drift": {"verdict": "stable", "previous_verdict": "stable"}, "history": {"sample_count": 1}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["session_attachment"]["status"] == "activation_environment_drift"
    assert payload["warm_runtime_ticket"]["status_id"] == "sync_session_activation_environment"
    assert payload["warm_runtime_ticket"]["route_id"] == "activation_env_then_assert"
    assert payload["warm_runtime_ticket"]["recommended"]["command"].startswith("dbus-update-activation-environment --systemd")
    assert payload["sources"]["helpers"]["check_runtime_json"]["session_attachment_status"] == "activation_environment_drift"
    assert payload["sources"]["helpers"]["check_runtime_json"]["activation_environment_status"] == "drift"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "session_attachment_status=activation_environment_drift" in summary
    assert "activation_environment_status=drift" in summary
    assert "warm_runtime_ticket_status=sync_session_activation_environment" in summary


def test_generated_stack_state_json_carries_warm_runtime_ticket_service_session_restart(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_warm_runtime_ticket_service_session_restart"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}, "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"}, "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}}})
    _write_json_stub(bin_dir / "check_runtime_json.sh", {
        "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
        "env": {"session_ready": False, "DISPLAY": ":0", "XAUTHORITY": "/tmp/Xauthority", "XDG_RUNTIME_DIR": "/run/user/1000", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus", "I3SOCK": "/run/user/1000/i3/ipc.sock"},
        "service_environment_probe": {"available": True, "pid": 4242, "readable": True, "environment": {"DISPLAY": ":1", "XAUTHORITY": "/tmp/stale.Xauthority", "XDG_RUNTIME_DIR": "/run/user/1000", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus", "I3SOCK": "/run/user/1000/i3/ipc.sock"}},
        "session_attachment": {
            "status": "service_session_drift",
            "ready": False,
            "activation_environment": {"status": "in_sync", "in_sync": True},
            "runtime_service_environment": {"status": "drift", "in_sync": False, "mismatched": [{"variable": "DISPLAY"}]},
            "commands": {"sync_activation_environment": "dbus-update-activation-environment --systemd DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS XDG_RUNTIME_DIR I3SOCK"},
            "blockers": ["service session drift"],
            "warnings": [],
        },
        "health": {"blockers": ["service session drift"], "warnings": []},
        "capabilities": {"warm_runtime": True},
        "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"},
    })
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_again", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when"}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"bus_event": "hotkey", "bus_payload_minimal": {"macro": "sig"}, "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "emit_bus_command": "./bin/dispatch_macro.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig", "reason": "gate and latest run both say the macro can emit now"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "startup_handoff_status_json.sh", {"startup_handoff": {"verdict": "primary_owner_ready", "autostart": {"state": "hidden"}, "counts": {"enabled_unit_count": 1}}})
    _write_json_stub(bin_dir / "startup_handoff_drift_json.sh", {"drift": {"verdict": "stable", "previous_verdict": "stable"}, "history": {"sample_count": 1}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["session_attachment"]["status"] == "service_session_drift"
    assert payload["session_attachment"]["runtime_service_environment"]["status"] == "drift"
    assert payload["warm_runtime_ticket"]["status_id"] == "restart_runtime_in_live_session"
    assert payload["warm_runtime_ticket"]["route_id"] == "service_env_then_restart"
    assert payload["warm_runtime_ticket"]["recommended"]["command"].startswith("dbus-update-activation-environment --systemd DISPLAY XAUTHORITY DBUS_SESSION_BUS_ADDRESS XDG_RUNTIME_DIR I3SOCK && systemctl --user restart ")
    assert payload["warm_runtime_ticket"]["recommended"]["command"].endswith(".service")
    assert payload["sources"]["helpers"]["check_runtime_json"]["runtime_service_environment_status"] == "drift"
    assert payload["sources"]["helpers"]["check_runtime_json"]["service_environment_pid"] == 4242

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "session_attachment_status=service_session_drift" in summary
    assert "runtime_service_environment_status=drift" in summary
    assert "warm_runtime_ticket_status=restart_runtime_in_live_session" in summary
    assert "warm_runtime_ticket_route=service_env_then_restart" in summary


def test_generated_stack_state_json_carries_warm_runtime_ticket_expected_watcher_contract_restart(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_warm_runtime_ticket_expected_watcher_contract_restart"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}, "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"}, "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}}})
    _write_json_stub(bin_dir / "check_runtime_json.sh", {
        "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
        "env": {"session_ready": True, "DISPLAY": ":0", "XAUTHORITY": "/tmp/Xauthority", "XDG_RUNTIME_DIR": "/run/user/1000", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus", "I3SOCK": "/run/user/1000/i3/ipc.sock"},
        "session_attachment": {"status": "attached", "ready": True, "blockers": [], "warnings": []},
        "dispatch_path_summary": {
            "status": "ok",
            "ok": True,
            "env_in_sync": True,
            "watchers_in_sync": False,
            "expected_watchers": ["hotkeys"],
            "daemon_watchers": ["clipboard"],
            "missing_expected_watchers": ["hotkeys"],
            "roundtrip_latency_ms": 11.7,
            "ack_pid": 4242,
        },
        "health": {"blockers": ["dispatch watcher contract drift"], "warnings": []},
        "capabilities": {"warm_runtime": False},
        "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service", "expected_watchers": ["hotkeys"]},
    })
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_again", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when"}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}, "dispatch_attention": {"id": "runtime_not_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "runtime_not_ready", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}, "dispatch_contract": {"bus_event": "hotkey", "bus_payload_minimal": {"macro": "sig"}, "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "emit_bus_command": "./bin/dispatch_macro.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh"}, "repair_action": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh", "reason": "runtime watcher contract drifted"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": "runtime_not_ready"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh"}, "recommendation_trace": {"selected_action_id": "inspect_runtime"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["warm_runtime_ticket"]
    assert payload["dispatch_path_summary"]["watchers_in_sync"] is False
    assert payload["dispatch_path_summary"]["missing_expected_watchers"] == ["hotkeys"]
    assert ticket["status_id"] == "restart_runtime_for_expected_watcher_contract"
    assert ticket["route_id"] == "watcher_contract_then_restart"
    assert ticket["recommended"]["command"].startswith("systemctl --user restart ")
    assert ticket["recommended"]["command"].endswith(".service")
    assert payload["sources"]["helpers"]["check_runtime_json"]["dispatch_watchers_in_sync"] is False
    assert payload["sources"]["helpers"]["check_runtime_json"]["dispatch_missing_expected_watchers"] == ["hotkeys"]

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "warm_runtime_ticket_status=restart_runtime_for_expected_watcher_contract" in summary
    assert "warm_runtime_ticket_route=watcher_contract_then_restart" in summary
    assert "dispatch_watchers_in_sync=False" in summary
    assert "dispatch_missing_expected_watchers=hotkeys" in summary


def test_generated_stack_state_json_carries_warm_runtime_ticket_reload_runtime_for_project_contract(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_warm_runtime_ticket_reload_runtime_for_project_contract"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}, "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"}, "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}}})
    _write_json_stub(bin_dir / "check_runtime_json.sh", {
        "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
        "env": {"session_ready": True, "DISPLAY": ":0", "XAUTHORITY": "/tmp/Xauthority", "XDG_RUNTIME_DIR": "/run/user/1000", "DBUS_SESSION_BUS_ADDRESS": "unix:path=/run/user/1000/bus", "I3SOCK": "/run/user/1000/i3/ipc.sock"},
        "session_attachment": {"status": "attached", "ready": True, "blockers": [], "warnings": []},
        "dispatch_path_summary": {
            "status": "ok",
            "ok": True,
            "env_in_sync": True,
            "watchers_in_sync": True,
            "runtime_contract_in_sync": False,
            "expected_watchers": ["hotkeys"],
            "daemon_watchers": ["hotkeys"],
            "missing_expected_watchers": [],
            "expected_runtime_contract_digest": "disk-digest",
            "daemon_runtime_contract_digest": "daemon-digest",
            "roundtrip_latency_ms": 9.2,
            "ack_pid": 4242,
        },
        "health": {"blockers": ["dispatch runtime contract drift"], "warnings": []},
        "capabilities": {"warm_runtime": False},
        "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service", "expected_watchers": ["hotkeys"], "expected_runtime_contract": {"digest": "disk-digest"}},
    })
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_again", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when"}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}, "dispatch_attention": {"id": "runtime_not_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "runtime_not_ready", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}, "dispatch_contract": {"bus_event": "hotkey", "bus_payload_minimal": {"macro": "sig"}, "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "emit_bus_command": "./bin/dispatch_macro.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh"}, "repair_action": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh", "reason": "runtime project contract drifted"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": "runtime_not_ready"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh"}, "recommendation_trace": {"selected_action_id": "inspect_runtime"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["warm_runtime_ticket"]
    assert payload["dispatch_path_summary"]["runtime_contract_in_sync"] is False
    assert payload["dispatch_path_summary"]["expected_runtime_contract_digest"] == "disk-digest"
    assert payload["dispatch_path_summary"]["daemon_runtime_contract_digest"] == "daemon-digest"
    assert ticket["status_id"] == "reload_runtime_for_project_contract"
    assert ticket["route_id"] == "runtime_contract_then_reload"
    assert ticket["recommended"]["command"] == "./bin/reload_runtime_json.sh"
    assert payload["sources"]["helpers"]["check_runtime_json"]["dispatch_runtime_contract_in_sync"] is False
    assert payload["sources"]["helpers"]["check_runtime_json"]["dispatch_expected_runtime_contract_digest"] == "disk-digest"
    assert payload["sources"]["helpers"]["check_runtime_json"]["dispatch_daemon_runtime_contract_digest"] == "daemon-digest"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "warm_runtime_ticket_status=reload_runtime_for_project_contract" in summary
    assert "warm_runtime_ticket_route=runtime_contract_then_reload" in summary
    assert "dispatch_runtime_contract_in_sync=False" in summary
    assert "dispatch_expected_runtime_contract_digest=disk-digest" in summary
    assert "dispatch_daemon_runtime_contract_digest=daemon-digest" in summary





def test_generated_stack_state_json_carries_warm_runtime_ticket_activate_socket(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_warm_runtime_ticket_activate_socket"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    socket_command = "systemctl --user daemon-reload && systemctl --user enable --now vhk-i3-busd-hotkeys.socket"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "health": {"blockers": ["socket unit not active", "service unit not active or activating"], "warnings": []}, "capabilities": {"warm_runtime": False}, "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": False, "issues": ["socket unit not active", "service unit not active or activating"]}, "runtime": {"socket_unit": "vhk-i3-busd-hotkeys.socket", "service_unit": "vhk-i3-busd-hotkeys.service"}, "units": {"socket": {"ActiveState": "inactive"}, "service": {"ActiveState": "inactive"}}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok", "summary": "latest run is clean"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_again", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when", "summary": "Dispatch expects the focused X11 window to match the macro when: selector."}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "stabilize_first"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "inspect_runtime"}}}, "next_step": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}, "dispatch_attention": {"id": "runtime_not_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "runtime_not_ready", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}, "dispatch_contract": {"bus_event": "hotkey", "bus_payload_minimal": {"macro": "sig"}, "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "emit_bus_command": "./bin/dispatch_macro.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh"}, "repair_action": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh", "reason": "runtime socket is not active yet"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": "runtime_not_ready"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "enable_runtime_socket", "command": socket_command}, "recommendation_trace": {"selected_action_id": "enable_runtime_socket"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["warm_runtime_ticket"]
    assert ticket["status_id"] == "activate_runtime_socket"
    assert ticket["route_id"] == "socket_activation_then_assert"
    assert ticket["recommended"]["command"] == socket_command
    assert ticket["signals"]["overall_ready"] is False
    assert ticket["signals"]["socket_active"] is False
    assert payload["sources"]["helpers"]["status_runtime_json"]["selected_warm_runtime_ticket_status_id"] == "activate_runtime_socket"
    assert payload["sources"]["helpers"]["check_runtime_json"]["selected_warm_runtime_ticket_command"] == socket_command
    assert payload["sources"]["helpers"]["next_action_json"]["selected_warm_runtime_ticket_route_id"] == "socket_activation_then_assert"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "warm_runtime_ticket_status=activate_runtime_socket" in summary
    assert "warm_runtime_ticket_route=socket_activation_then_assert" in summary
    assert f"warm_runtime_ticket_command={socket_command}" in summary



def test_generated_stack_state_json_carries_primary_macro_recording_ticket(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_recording_ticket"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "source": "./bin/macro_source_json.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "render_review": "./bin/render_macro.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok"}, "replay_posture": {"id": "verified_recent"}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}}, "hints": {"has_interactive_inputs": False}}, "authoring": {"workflow": {"preferred_loop": ["recording_review", "run_or_dispatch"]}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "source_newer_than_recording"}}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"path": "/tmp/fake/sig.window-context.yaml", "exists": True, "has_recorded_context": True, "freshness": {"status": "source_newer_than_recording", "review_notes": ["Macro source is newer than the recorder sidecar; treat recorder evidence as stale after cleanup, retime, or manual edits."]}, "selector_summary": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "exact_segment_count": 1}, "transition_reason_counts": {"title": 1}, "exact_segment_count": 1, "relative_mouse_mode": "window"}, "review": {"generated_stack": {"record": "./bin/record_macro.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "render_review": "./bin/render_macro.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 1}, "queue": {"stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}]}, "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_recording_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "rerecord_after_source_edits"
    assert ticket["route_id"] == "record_then_review"
    assert ticket["recommended"]["command"] == "./bin/record_macro.sh sig"
    assert ticket["selector_summary"]["selector_source_id"] == "macro_when"
    assert ticket["signals"]["relative_mouse_mode"] == "window"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_recording_ticket_status_id"] == "rerecord_after_source_edits"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_recording_ticket_command"] == "./bin/record_macro.sh sig"
    assert payload["sources"]["helpers"]["macro_recording_json"]["selected_macro_recording_ticket_route_id"] == "record_then_review"
    assert payload["sources"]["helpers"]["macro_recording_json"]["selector_source_id"] == "macro_when"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_recording_ticket_macro=sig" in summary
    assert "primary_macro_recording_ticket_status=rerecord_after_source_edits" in summary
    assert "primary_macro_recording_ticket_route=record_then_review" in summary
    assert "primary_macro_recording_ticket_command=./bin/record_macro.sh sig" in summary





def test_generated_stack_state_json_carries_primary_macro_cleanup_ticket_review_diff(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_cleanup_ticket_review_diff"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn", "ready_to_iterate": False}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "source": "./bin/macro_source_json.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "render_review": "./bin/render_macro.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "warn", "summary": "latest run still warns"}, "replay_posture": {"id": "warning_recent", "summary": "latest proof still warns"}, "preferred_entrypoints": {"latest_run_json": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig", "history": "./bin/history_runs.sh --macro sig --limit 5"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when"}, "hints": {"has_interactive_inputs": False}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "stabilize_first"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "stabilize_before_dispatch"}}}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"exists": True, "has_recorded_context": True, "freshness": {"status": "aligned"}, "selector_summary": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "exact_segment_count": 2}, "transition_reason_counts": {"title": 0}, "exact_segment_count": 2, "relative_mouse_mode": "window"}, "review": {"generated_stack": {"record": "./bin/record_macro.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "render_review": "./bin/render_macro.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "repeated_desktop_state_mismatch", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "repeated_desktop_state_mismatch"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}, "dispatch_contract": {"bus_event": "hotkey", "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "stabilize_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}, "repair_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": "desktop_state_mismatch"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"active_counts": {"needs_review_count": 1}, "active_queue": {"exact_segment_macros": [{"name": "sig", "kind": "exact_segments", "review_command": "./bin/macro_recording_json.sh sig"}]}, "active_ordered": [{"name": "sig", "kind": "exact_segments", "review_command": "./bin/macro_recording_json.sh sig"}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "review_cleanup_diff", "command": "./bin/optimize_macro.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_cleanup_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "review_cleanup_diff"
    assert ticket["route_id"] == "review_cleanup_then_apply"
    assert ticket["recommended"]["command"] == "./bin/optimize_macro.sh sig"
    assert ticket["signals"]["exact_segment_count"] == 2
    assert "exact_segments" in ticket["signals"]["issue_codes"]
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_cleanup_ticket_status_id"] == "review_cleanup_diff"
    assert payload["sources"]["helpers"]["macro_recording_json"]["selected_macro_cleanup_ticket_route_id"] == "review_cleanup_then_apply"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_cleanup_ticket_command"] == "./bin/optimize_macro.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_cleanup_ticket_macro=sig" in summary
    assert "primary_macro_cleanup_ticket_status=review_cleanup_diff" in summary
    assert "primary_macro_cleanup_ticket_route=review_cleanup_then_apply" in summary
    assert "primary_macro_cleanup_ticket_command=./bin/optimize_macro.sh sig" in summary


def test_generated_stack_state_json_carries_primary_macro_cleanup_ticket_clear(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_cleanup_ticket_clear"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "source": "./bin/macro_source_json.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "render_review": "./bin/render_macro.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy", "summary": "latest run is clean"}, "replay_posture": {"id": "verified_recent", "summary": "healthy matching run"}, "preferred_entrypoints": {"latest_run_json": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig", "history": "./bin/history_runs.sh --macro sig --limit 5"}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when"}, "hints": {"has_interactive_inputs": False}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"exists": True, "has_recorded_context": True, "freshness": {"status": "aligned"}, "selector_summary": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "exact_segment_count": 0}, "transition_reason_counts": {"title": 0, "workspace": 0}, "exact_segment_count": 0, "relative_mouse_mode": "window"}, "review": {"generated_stack": {"recording_review": "./bin/macro_recording_json.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"bus_event": "hotkey", "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig", "reason": "gate and latest run both say the macro can emit now"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"active_counts": {"needs_review_count": 0}, "active_queue": {}, "active_ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_cleanup_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "cleanup_clear"
    assert ticket["route_id"] == "cleanup_clear_then_execute"
    assert ticket["recommended"]["command"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["signals"]["active_issue_count"] == 0
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_cleanup_ticket_status_id"] == "cleanup_clear"
    assert payload["sources"]["helpers"]["macro_recording_json"]["selected_macro_cleanup_ticket_command"] == "./bin/dispatch_macro_checked.sh sig"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_cleanup_ticket_route_id"] == "cleanup_clear_then_execute"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_cleanup_ticket_macro=sig" in summary
    assert "primary_macro_cleanup_ticket_status=cleanup_clear" in summary
    assert "primary_macro_cleanup_ticket_route=cleanup_clear_then_execute" in summary
    assert "primary_macro_cleanup_ticket_command=./bin/dispatch_macro_checked.sh sig" in summary


def test_generated_stack_state_json_carries_primary_macro_replay_ticket_record_first(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_replay_ticket_record_first"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "source": "./bin/macro_source_json.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "render_review": "./bin/render_macro.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok", "summary": "latest run is clean"}, "replay_posture": {"id": "verified_recent", "summary": "healthy matching run"}, "preferred_entrypoints": {"latest_run_json": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig", "history": "./bin/history_runs.sh --macro sig --limit 5"}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}}, "hints": {"has_interactive_inputs": False}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "source_newer_than_recording"}}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"path": "/tmp/fake/sig.window-context.yaml", "exists": True, "has_recorded_context": True, "freshness": {"status": "source_newer_than_recording", "review_notes": ["Macro source is newer than the recorder sidecar; treat recorder evidence as stale after cleanup, retime, or manual edits."]}, "selector_summary": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}}, "relative_mouse_mode": "window"}, "review": {"generated_stack": {"record": "./bin/record_macro.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "render_review": "./bin/render_macro.sh sig", "cleanup_review": "./bin/optimize_macro.sh sig", "cleanup_apply": "./bin/apply_optimize_macro.sh sig", "retime": "./bin/retime_macro.sh sig"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}, "latest_run_context": {"scope": "matching_macro", "latest_macro": "sig", "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "ok"}}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 1}, "queue": {"stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}]}, "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_replay_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "record_before_replay"
    assert ticket["route_id"] == "record_then_replay"
    assert ticket["recommended"]["command"] == "./bin/record_macro.sh sig"
    assert ticket["signals"]["recording_ticket_status_id"] == "rerecord_after_source_edits"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_replay_ticket_status_id"] == "record_before_replay"
    assert payload["sources"]["helpers"]["macro_latest_run_json"]["selected_macro_replay_ticket_route_id"] == "record_then_replay"
    assert payload["sources"]["helpers"]["macro_replay_board_json"]["selected_macro_replay_ticket_command"] == "./bin/record_macro.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_replay_ticket_macro=sig" in summary
    assert "primary_macro_replay_ticket_status=record_before_replay" in summary
    assert "primary_macro_replay_ticket_route=record_then_replay" in summary
    assert "primary_macro_replay_ticket_command=./bin/record_macro.sh sig" in summary



def test_generated_stack_state_json_carries_primary_macro_replay_ticket_verified_recent(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_replay_ticket_verified_recent"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "recording_review": "./bin/macro_recording_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"macro": {"name": "sig"}, "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy", "summary": "latest run is clean"}, "replay_posture": {"id": "verified_recent", "summary": "healthy matching run"}, "preferred_entrypoints": {"latest_run_json": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig", "history": "./bin/history_runs.sh --macro sig --limit 5"}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when", "summary": "Dispatch expects the focused X11 window to match the macro when: selector."}, "hints": {"preferred_execution_mode": "warm_runtime_dispatch"}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}, "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_gate": {"decision": {"id": "dispatch_now"}}}, "next_step": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"exists": True, "has_recorded_context": True, "freshness": {"status": "aligned"}}, "review": {"generated_stack": {"recording_review": "./bin/macro_recording_json.sh sig"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}, "latest_run_context": {"scope": "matching_macro", "latest_macro": "sig", "latest_run": {"macro": "sig", "ok": True}, "latest_run_health": {"verdict": "healthy"}}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "dispatch_clean_recently", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "dispatch_clean_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}, "primary_blocked_class_id": None, "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"bus_event": "hotkey", "generated_stack_checked_command": "./bin/dispatch_macro_checked.sh sig", "generated_stack_gate_command": "./bin/macro_dispatch_gate_json.sh sig", "contract_wrapper": "./bin/macro_contract_json.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig", "reason": "gate and latest run both say the macro can emit now"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [], "incomplete_review_issue_codes": [], "runtime_acceptance": {"posture_id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["primary_macro_replay_ticket"]
    assert ticket["macro_name"] == "sig"
    assert ticket["status_id"] == "replay_proof_ready"
    assert ticket["route_id"] == "verified_replay_then_execute"
    assert ticket["recommended"]["command"] == "./bin/dispatch_macro_checked.sh sig"
    assert ticket["signals"]["replay_posture_id"] == "verified_recent"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_replay_ticket_status_id"] == "replay_proof_ready"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_replay_ticket_route_id"] == "verified_replay_then_execute"
    assert payload["sources"]["helpers"]["macro_latest_run_json"]["selected_macro_replay_ticket_command"] == "./bin/dispatch_macro_checked.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_replay_ticket_macro=sig" in summary
    assert "primary_macro_replay_ticket_status=replay_proof_ready" in summary
    assert "primary_macro_replay_ticket_route=verified_replay_then_execute" in summary
    assert "primary_macro_replay_ticket_command=./bin/dispatch_macro_checked.sh sig" in summary



def test_generated_stack_state_json_carries_primary_macro_consistency(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_consistency"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}, "latest_run_health": {"verdict": "warn"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig"}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_ready"}}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch", "unresolved_force_override": True}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": True}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "dispatch_now", "command": "./bin/dispatch_macro_checked.sh sig"}, "repair_action": {"id": "ready_to_dispatch", "command": "./bin/dispatch_macro_checked.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": True, "primary_blocker_class_id": None}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 1}, "queue": {"stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}]}, "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 1}, "macros": [{"name": "sig", "review_acceptances": [{"issue_code": "segments_ok"}], "runtime_acceptance": {"posture_id": "accepted_recent"}}]})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    consistency = payload["primary_macro_consistency"]
    assert consistency["macro_name"] == "sig"
    assert consistency["status_id"] == "contradictions_present"
    assert consistency["primary_issue_id"] == "review_queue_vs_dispatch_ready"
    issue_ids = {item["id"] for item in consistency["issues"]}
    assert {"review_queue_vs_dispatch_ready", "accepted_but_latest_run_warns", "runtime_acceptance_vs_blocked_dispatch", "unresolved_force_override", "runtime_vs_replay_posture_mismatch"}.issubset(issue_ids)
    assert consistency["recommended"]["command"] == "./bin/macro_recording_json.sh sig"
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_consistency_status_id"] == "contradictions_present"
    assert "review_queue_vs_dispatch_ready" in payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_consistency_issue_ids"]

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_consistency_macro=sig" in summary
    assert "primary_macro_consistency_status=contradictions_present" in summary
    assert "primary_macro_consistency_primary_issue=review_queue_vs_dispatch_ready" in summary
    assert "primary_macro_consistency_recommended_command=./bin/macro_recording_json.sh sig" in summary


def test_generated_stack_state_json_carries_primary_macro_repair_recipe(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_repair_recipe"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}, "latest_run_health": {"verdict": "warn"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig"}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}, "execution": {"runtime_posture": {"id": "stabilize_first"}}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "contract_debt", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "stabilize_before_dispatch", "command": "./bin/macro_report_latest.sh sig"}, "repair_action": {"id": "repair_latest_run", "command": "./bin/macro_report_latest.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": "contract_debt"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 1}, "queue": {"stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}]}, "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    recipe = payload["primary_macro_repair_recipe"]
    assert recipe["macro_name"] == "sig"
    assert recipe["status_id"] == "repair_needed"
    assert recipe["recipe_id"] == "review_then_repair"
    assert recipe["focus_id"] == "recorder_contract"
    assert recipe["source_blocker_class_id"] == "contract_debt"
    assert recipe["step_budget"] == 4
    assert recipe["step_count"] == 4
    assert recipe["evidence_commands"] == [
        "./bin/macro_recording_json.sh sig",
        "./bin/macro_contract_json.sh sig",
        "./bin/macro_author_loop_json.sh sig",
    ]
    assert [step["command"] for step in recipe["steps"]] == [
        "./bin/macro_recording_json.sh sig",
        "./bin/macro_report_latest.sh sig",
        "./bin/macro_contract_json.sh sig",
        "./bin/macro_author_loop_json.sh sig",
    ]
    helper_meta = payload["sources"]["helpers"]["macro_author_queue_json"]
    assert helper_meta["selected_macro_repair_recipe_id"] == "review_then_repair"
    assert helper_meta["selected_macro_repair_recipe_status_id"] == "repair_needed"
    assert helper_meta["selected_macro_repair_recipe_focus_id"] == "recorder_contract"
    assert helper_meta["selected_macro_repair_recipe_source_blocker_class_id"] == "contract_debt"
    assert helper_meta["selected_macro_repair_recipe_command"] == "./bin/macro_recording_json.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_repair_recipe_macro=sig" in summary
    assert "primary_macro_repair_recipe_status=repair_needed" in summary
    assert "primary_macro_repair_recipe_id=review_then_repair" in summary
    assert "primary_macro_repair_recipe_focus=recorder_contract" in summary
    assert "primary_macro_repair_recipe_source_blocker_class=contract_debt" in summary
    assert "primary_macro_repair_recipe_command=./bin/macro_recording_json.sh sig" in summary


def test_generated_stack_state_json_carries_primary_macro_repair_recipe_direct_run(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_repair_recipe_direct_run"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "other"}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "direct_run"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run_health": {"verdict": "ok"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig"}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "direct_run_only"}}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "direct_run_only"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "direct_run_only"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "direct_run_only"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "no_dispatch_history", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "no_dispatch_history"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "no_dispatch_history"}, "dispatch_history": {}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "direct_run", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "direct_run", "decision": {"id": "use_direct_run", "command": "./bin/run_macro.sh sig"}, "repair_action": {"id": "use_direct_run", "command": "./bin/run_macro.sh sig"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": "direct_run_only"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "use_direct_run", "command": "./bin/run_macro.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    recipe = payload["primary_macro_repair_recipe"]
    assert recipe["macro_name"] == "sig"
    assert recipe["status_id"] == "direct_run_ready"
    assert recipe["recipe_id"] == "direct_run_now"
    assert recipe["focus_id"] == "direct_run_lane"
    assert recipe["step_count"] == 1
    assert recipe["evidence_commands"] == [
        "./bin/run_macro.sh sig",
        "./bin/macro_contract_json.sh sig",
        "./bin/macro_author_loop_json.sh sig",
    ]
    assert recipe["steps"][0]["command"] == "./bin/run_macro.sh sig"
    assert recipe["recommended"]["command"] == "./bin/run_macro.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_repair_recipe_macro=sig" in summary
    assert "primary_macro_repair_recipe_status=direct_run_ready" in summary
    assert "primary_macro_repair_recipe_id=direct_run_now" in summary
    assert "primary_macro_repair_recipe_focus=direct_run_lane" in summary
    assert "primary_macro_repair_recipe_command=./bin/run_macro.sh sig" in summary


def test_generated_stack_state_json_carries_blocker_aware_desktop_target_recipe(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_desktop_target_recipe"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}, "latest_run_health": {"verdict": "warn"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig"}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_candidate"}}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_candidate"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}, "primary_blocked_class_id": "desktop_state_mismatch", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"preferred_execution_mode": "warm_runtime_dispatch", "decision": {"id": "inspect_before_dispatch", "command": "./bin/macro_report_latest.sh sig"}, "repair_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig", "source_blocker_class_id": "desktop_state_mismatch"}, "dispatch_readiness": {"can_emit_minimal_payload_now": False, "primary_blocker_class_id": "desktop_state_mismatch"}})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    recipe = payload["primary_macro_repair_recipe"]
    assert recipe["focus_id"] == "live_desktop_target"
    assert recipe["source_blocker_class_id"] == "desktop_state_mismatch"
    assert recipe["evidence_commands"] == [
        "./bin/macro_report_latest.sh sig",
        "./bin/macro_trace_latest.sh sig",
        "./bin/macro_contract_json.sh sig",
        "./bin/macro_dispatch_gate_json.sh sig",
    ]
    assert [step["command"] for step in recipe["steps"]] == [
        "./bin/macro_report_latest.sh sig",
        "./bin/macro_trace_latest.sh sig",
        "./bin/macro_contract_json.sh sig",
        "./bin/macro_author_loop_json.sh sig",
    ]



def test_generated_stack_state_json_carries_primary_macro_probe_observation(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_probe_observation"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": False}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": [{"name": "sig", "execution": {"preferred_mode": "warm_runtime_dispatch"}, "preferred_entrypoints": {"author_loop": "./bin/macro_author_loop_json.sh sig", "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig", "warm_runtime_gate": "./bin/macro_dispatch_gate_json.sh sig", "direct_run": "./bin/run_macro.sh sig", "contract": "./bin/macro_contract_json.sh sig", "latest_run": "./bin/macro_latest_run_json.sh sig", "latest_report": "./bin/macro_report_latest.sh sig", "latest_trace": "./bin/macro_trace_latest.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {
        "latest_run": {"macro": "sig", "ok": False},
        "latest_run_health": {
            "verdict": "warn",
            "probe_hint": {
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
        "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"},
    })
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig", "desktop_target": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "summary": "Warm dispatch expects the macro's explicit when: selector to match the focused X11/i3 target."}}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "next_step": {"id": "inspect_latest_run", "command": "./bin/macro_report_latest.sh sig"}, "execution": {"runtime_posture": {"id": "warm_dispatch_candidate"}}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent"}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_candidate"}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"macro": "sig", "result": "blocked", "route": "checked_dispatch", "gate": {"live_probe_hint": {"id": "window_event_probe", "summary": "Latest matching run failed around `WaitForWindowEvent`, after `window_event` waits x2.", "step_type": "WaitForWindowEvent", "wait_kind": "window_event", "wait_count": 2, "observation": {"source_id": "wait_attempt", "summary": "Latest matching run preserved a failed live wait observation (matched=False, workspace=2, wm=i3, event=focus).", "observed": {"matched": False, "workspace": "2", "wm": "i3", "event": "focus"}}}}}, "primary_blocked_class_id": "desktop_state_mismatch", "unresolved_force_override": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {
        "preferred_execution_mode": "warm_runtime_dispatch",
        "decision": {"id": "inspect_before_dispatch", "command": "./bin/macro_report_latest.sh sig"},
        "repair_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig", "source_blocker_class_id": "desktop_state_mismatch"},
        "dispatch_readiness": {
            "can_emit_minimal_payload_now": False,
            "primary_blocker_class_id": "desktop_state_mismatch",
            "desktop_target": {"selector_source_id": "macro_when", "selector": {"class": "Alacritty", "workspace": "2"}, "summary": "Warm dispatch expects the macro's explicit when: selector to match the focused X11/i3 target."},
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
    })
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_live_desktop_target", "command": "./bin/macro_report_latest.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    observation = payload["primary_macro_probe_observation"]
    assert observation["macro_name"] == "sig"
    assert observation["status_id"] == "observation_available"
    assert observation["source_id"] == "macro_dispatch_gate.dispatch_readiness.live_probe_hint"
    assert observation["probe_id"] == "window_event_probe"
    assert observation["observation_source_id"] == "wait_attempt"
    assert observation["observed"]["workspace"] == "2"
    assert observation["observed"]["event"] == "focus"
    assert observation["desktop_target"]["selector"]["class"] == "Alacritty"
    assert observation["recommended"]["command"] == "./bin/macro_report_latest.sh sig"
    assert observation["inspect_commands"] == [
        "./bin/macro_report_latest.sh sig",
        "./bin/macro_trace_latest.sh sig",
        "./bin/macro_dispatch_gate_json.sh sig",
        "./bin/macro_contract_json.sh sig",
        "./bin/macro_latest_run_json.sh sig",
    ]
    assert payload["sources"]["helpers"]["macro_author_queue_json"]["selected_macro_probe_observation_status_id"] == "observation_available"
    assert payload["sources"]["helpers"]["macro_dispatch_gate_json"]["selected_macro_probe_observation_probe_id"] == "window_event_probe"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_probe_observation_macro=sig" in summary
    assert "primary_macro_probe_observation_status=observation_available" in summary
    assert "primary_macro_probe_observation_probe_id=window_event_probe" in summary
    assert "primary_macro_probe_observation_source=wait_attempt" in summary
    assert "primary_macro_probe_observation_command=./bin/macro_report_latest.sh sig" in summary


def test_generated_stack_state_json_carries_primary_macro_review_queue(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_review_queue"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "other"}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 2}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 2}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent", "counts_by_posture_id": {"warning_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first", "counts_by_posture_id": {"stabilize_first": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {
        "counts": {"needs_review_count": 2, "stale_recording_sidecars": 1, "title_segment_macros": 1},
        "queue": {
            "stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig", "kind": "stale_recording_sidecar"}],
            "title_segment_macros": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig", "kind": "title_recording_segments"}],
        },
        "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}],
        "accepted_counts": {"accepted_issue_count": 0},
    })
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}, "recommendation_trace": {"selected_action_id": "refresh_recording_review"}})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "stabilize_before_dispatch"}, "repair_action": {"id": "repair_recorder_contract"}, "dispatch_readiness": {"primary_blocker_class_id": "contract_debt"}})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run_health": {"verdict": "warning_recent"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig"}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "next_step": {"id": "refresh_recording_review"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "source_newer_than_recording"}}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_review_queue"]["macro_name"] == "sig"
    assert payload["primary_macro_review_queue"]["present"] is True
    assert payload["primary_macro_review_queue"]["queue_ids"] == ["stale_recording_sidecars", "title_segment_macros"]
    assert payload["primary_macro_review_queue"]["review_command"] == "./bin/macro_recording_json.sh sig"
    assert payload["primary_macro_review_queue"]["ordered_item"]["kind"] == "stale_recording_sidecar"
    assert payload["sources"]["helpers"]["macro_review_queue_json"]["selected_macro_name"] == "sig"
    assert payload["sources"]["helpers"]["macro_review_queue_json"]["selected_macro_present"] is True
    assert payload["sources"]["helpers"]["macro_review_queue_json"]["selected_macro_queue_ids"] == ["stale_recording_sidecars", "title_segment_macros"]
    assert payload["sources"]["helpers"]["macro_review_queue_json"]["selected_macro_review_command"] == "./bin/macro_recording_json.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_review_queue_macro=sig" in summary
    assert "primary_macro_review_queue_present=True" in summary
    assert "primary_macro_review_queue_categories=stale_recording_sidecars,title_segment_macros" in summary
    assert "primary_macro_review_queue_review_command=./bin/macro_recording_json.sh sig" in summary


def test_generated_stack_state_json_carries_primary_macro_latest_dispatch(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_latest_dispatch"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "other"}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 2}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 2}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "accepted_counts": {"accepted_issue_count": 0}})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {
        "summary": {"primary_macro_name": "other", "primary_posture_id": "repeated_contract_debt", "attention_macro_count": 1},
        "primary_macro": {"name": "other", "dispatch_history_posture": {"id": "repeated_contract_debt"}},
        "macros": [
            {"name": "other", "dispatch_history_posture": {"id": "repeated_contract_debt"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}}},
            {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently", "attention_id": "repeated_run_proof_gap"}, "dispatch_history": {"latest_receipt": {"receipt_id": "dispatch-1", "recorded_at": "2026-03-21T09:48:00Z", "result": "blocked", "route": "checked_dispatch", "checked_gate": True, "force_override": False, "gate": {"primary_blocker_class_id": "run_proof_gap"}}, "latest_blocked_receipt": {"receipt_id": "dispatch-1", "recorded_at": "2026-03-21T09:48:00Z", "route": "checked_dispatch", "gate": {"primary_blocker_class_id": "run_proof_gap"}}, "latest_clean_emit": {"recorded_at": "2026-03-20T09:48:00Z", "route": "checked_dispatch"}, "latest_force_override": {"recorded_at": "2026-03-21T09:40:00Z", "route": "checked_dispatch_forced"}, "unresolved_force_override": True, "primary_blocked_class_id": "run_proof_gap"}},
        ],
    })
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_dispatch_gate", "command": "./bin/macro_dispatch_gate_json.sh sig"}, "recommendation_trace": {"selected_action_id": "inspect_dispatch_gate"}})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "stabilize_before_dispatch"}, "repair_action": {"id": "refresh_matching_run_proof"}, "dispatch_readiness": {"primary_blocker_class_id": "run_proof_gap"}})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run_health": {"verdict": "warning_recent"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig"}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "execution": {"runtime_posture": {"id": "stabilize_first"}}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "aligned"}}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["latest_dispatch"]["macro"] == "other"
    assert payload["primary_macro_latest_dispatch"]["macro_name"] == "sig"
    assert payload["primary_macro_latest_dispatch"]["latest_receipt"]["result"] == "blocked"
    assert payload["primary_macro_latest_dispatch"]["latest_receipt"]["route"] == "checked_dispatch"
    assert payload["primary_macro_latest_dispatch"]["primary_blocked_class_id"] == "run_proof_gap"
    assert payload["primary_macro_latest_dispatch"]["unresolved_force_override"] is True
    assert payload["sources"]["helpers"]["macro_dispatch_history_board_json"]["selected_macro_latest_result"] == "blocked"
    assert payload["sources"]["helpers"]["macro_dispatch_history_board_json"]["selected_macro_primary_blocked_class_id"] == "run_proof_gap"
    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_latest_dispatch_macro=sig" in summary
    assert "primary_macro_latest_dispatch_result=blocked" in summary
    assert "primary_macro_latest_dispatch_route=checked_dispatch" in summary
    assert "primary_macro_latest_dispatch_primary_blocked_class=run_proof_gap" in summary
    assert "primary_macro_latest_dispatch_unresolved_force_override=True" in summary



def test_generated_stack_state_json_carries_primary_macro_command_palette(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_primary_command_palette"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"health": {"blockers": [], "warnings": []}, "capabilities": {"warm_runtime": True}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "other"}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "other", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok"}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 2}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {
        "project": {"macro_count": 2, "interactive_macro_count": 0, "preset_enabled_macro_count": 0},
        "macros": [
            {
                "name": "sig",
                "execution": {"preferred_mode": "warm_runtime_dispatch"},
                "preferred_entrypoints": {
                    "author_loop": "./bin/macro_author_loop_json.sh sig",
                    "warm_runtime_checked": "./bin/dispatch_macro_checked.sh sig",
                    "direct_run": "./bin/run_macro.sh sig",
                },
            },
            {"name": "other"},
        ],
    })
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}, {"name": "other"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warning_recent", "counts_by_posture_id": {"warning_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "warning_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "warning_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first", "counts_by_posture_id": {"stabilize_first": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}, "dispatch_history": {"latest_receipt": {"result": "blocked", "route": "checked_dispatch"}}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig", "preferred_execution_mode": "warm_runtime_dispatch", "dispatch_readiness": {"can_emit_minimal_payload_now": False}}]})
    _write_json_stub(bin_dir / "macro_acceptance_ledger_json.sh", {"summary": {"accepted_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {
        "counts": {"needs_review_count": 1, "stale_recording_sidecars": 1},
        "queue": {"stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig", "kind": "stale_recording_sidecar"}]},
        "ordered": [{"name": "sig", "kind": "stale_recording_sidecar", "review_command": "./bin/macro_recording_json.sh sig"}],
        "accepted_counts": {"accepted_issue_count": 0},
    })
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}, "recommendation_trace": {"selected_action_id": "refresh_recording_review"}})
    _write_json_stub(bin_dir / "macro_dispatch_gate_json.sh", {"decision": {"id": "stabilize_before_dispatch"}, "repair_action": {"id": "repair_recorder_contract", "command": "./bin/macro_recording_json.sh sig", "followup": ["./bin/dispatch_macro_checked.sh sig"]}, "dispatch_readiness": {"primary_blocker_class_id": "contract_debt"}})
    _write_json_stub(bin_dir / "macro_latest_run_json.sh", {"latest_run_health": {"verdict": "warning_recent"}, "next_step": {"id": "inspect_latest_failures", "command": "./bin/report_latest.sh --show-errors --show-waits --show-advice"}})
    _write_json_stub(bin_dir / "macro_contract_json.sh", {"macro": {"name": "sig"}})
    _write_json_stub(bin_dir / "macro_author_loop_json.sh", {"macro": {"name": "sig"}, "next_step": {"id": "refresh_recording_review", "command": "./bin/macro_recording_json.sh sig"}})
    _write_json_stub(bin_dir / "macro_recording_json.sh", {"macro": {"name": "sig"}, "recording": {"freshness": {"status": "source_newer_than_recording"}}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["primary_macro_command_palette"]["macro_name"] == "sig"
    assert payload["primary_macro_command_palette"]["recommended"]["id"] == "review_queue_review"
    assert payload["primary_macro_command_palette"]["recommended"]["source_id"] == "primary_macro_review_queue.review_command"
    assert payload["primary_macro_command_palette"]["recommended"]["command"] == "./bin/macro_recording_json.sh sig"
    assert payload["primary_macro_command_palette"]["repair_command"] == "./bin/macro_recording_json.sh sig"
    assert any(item["id"] == "warm_runtime_checked" for item in payload["primary_macro_command_palette"]["items"])
    assert payload["primary_macro_command_palette"]["warm_runtime_entrypoint"] == "./bin/dispatch_macro_checked.sh sig"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "primary_macro_command_palette_macro=sig" in summary
    assert "primary_macro_command_palette_recommended_id=review_queue_review" in summary
    assert "primary_macro_command_palette_recommended_command=./bin/macro_recording_json.sh sig" in summary

def test_generated_stack_state_json_carries_dispatch_catalog(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "clean_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey", "bus_event_source": "explicit"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_contract": {"generated_stack_command": "dispatch_macro.sh sig"}}, "macros": [{"name": "sig", "dispatch_contract": {"generated_stack_command": "dispatch_macro.sh sig"}}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "runtime_ready", "command": "./bin/dispatch_macro.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["macro_dispatch_catalog"]["summary"]["dispatch_ready_now_count"] == 1
    assert payload["macro_dispatch_catalog"]["runtime"]["bus_event"] == "hotkey"
    assert payload["sources"]["helpers"]["macro_dispatch_catalog_json"]["dispatch_ready_now_count"] == 1

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "dispatch_ready_now_count=1" in summary
    assert "dispatch_bus_event=hotkey" in summary


def test_generated_stack_state_json_carries_latest_dispatch(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_latest_dispatch"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch", "checked_gate": True}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_candidate", "counts_by_posture_id": {"warm_dispatch_candidate": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["latest_dispatch"]["macro"] == "sig"
    assert payload["latest_dispatch"]["result"] == "blocked"
    assert payload["sources"]["helpers"]["latest_dispatch_json"]["route"] == "checked_dispatch"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "latest_dispatch_macro=sig" in summary
    assert "latest_dispatch_result=blocked" in summary




def test_generated_stack_state_json_carries_review_queue_and_counts(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(
        bin_dir / "check_runtime_json.sh",
        {
            "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
            "env": {"session_ready": True},
            "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
            "capabilities": {"warm_runtime": True},
            "health": {"blockers": [], "warnings": []},
        },
    )
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(
        bin_dir / "macro_inventory_json.sh",
        {
            "project": {
                "macro_count": 1,
                "groups": [],
                "tags": [],
                "recording_sidecar_count": 1,
                "recording_sidecar_missing_count": 0,
                "recording_sidecar_stale_count": 1,
                "recording_sidecar_newer_than_source_count": 0,
                "macros_with_exact_recording_segments": 1,
                "macros_with_title_recording_segments": 0,
            },
            "macros": [{"name": "sig"}],
        },
    )
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "no_dispatch_history", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "no_dispatch_history"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "no_dispatch_history"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(
        bin_dir / "macro_review_queue_json.sh",
        {
            "counts": {
                "missing_recording_sidecars": 0,
                "stale_recording_sidecars": 1,
                "recording_newer_than_source": 0,
                "exact_segment_macros": 1,
                "title_segment_macros": 0,
                "needs_review_count": 2,
            },
            "queue": {
                "missing_recording_sidecars": [],
                "stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
                "recording_newer_than_source": [],
                "exact_segment_macros": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
                "title_segment_macros": [],
            },
            "ordered": [{"name": "sig", "kind": "stale_recording_sidecar"}, {"name": "sig", "kind": "exact_segments"}],
        },
    )
    _write_json_stub(
        bin_dir / "next_action_json.sh",
        {
            "primary_action": {"id": "refresh_recording_evidence", "command": "./bin/macro_recording_json.sh sig"},
        },
    )

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["review_counts"]["needs_review_count"] == 2
    assert payload["macro_review_queue"]["queue"]["stale_recording_sidecars"][0]["name"] == "sig"
    assert payload["sources"]["helpers"]["macro_review_queue_json"]["available"] is True
    assert payload["sources"]["helpers"]["macro_replay_board_json"]["available"] is True
    assert payload["sources"]["helpers"]["macro_runtime_board_json"]["available"] is True
    assert payload["control_plane"]["helper_surface_contracts"]["next_action_json"]["surface_class"] == "runtime_snapshot"
    assert payload["next_action_trace"]["selected_action_id"] == "refresh_recording_evidence"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "review_queue_needs_review_count=2" in summary
    assert "review_queue_missing_recording_sidecars=0" in summary
    assert "recommendation_trace_selected_action=refresh_recording_evidence" in summary


def test_generated_stack_state_and_next_action_respect_accepted_review_debt(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(
        bin_dir / "check_runtime_json.sh",
        {
            "project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]},
            "env": {"session_ready": True},
            "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True},
            "capabilities": {"warm_runtime": True},
            "health": {"blockers": [], "warnings": []},
        },
    )
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "reasons": [], "next_step": {}}})
    _write_json_stub(
        bin_dir / "macro_inventory_json.sh",
        {
            "project": {
                "macro_count": 1,
                "groups": [],
                "tags": [],
                "recording_sidecar_missing_count": 0,
                "recording_sidecar_stale_count": 1,
                "recording_sidecar_newer_than_source_count": 0,
                "macros_with_exact_recording_segments": 1,
                "macros_with_title_recording_segments": 0,
            },
            "macros": [{"name": "sig"}],
        },
    )
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(
        bin_dir / "macro_review_queue_json.sh",
        {
            "counts": {
                "missing_recording_sidecars": 0,
                "stale_recording_sidecars": 1,
                "recording_newer_than_source": 0,
                "exact_segment_macros": 1,
                "title_segment_macros": 0,
                "needs_review_count": 2,
            },
            "active_counts": {
                "missing_recording_sidecars": 0,
                "stale_recording_sidecars": 0,
                "recording_newer_than_source": 0,
                "exact_segment_macros": 0,
                "title_segment_macros": 0,
                "needs_review_count": 0,
            },
            "accepted_counts": {
                "stale_recording_sidecars": 1,
                "exact_segment_macros": 1,
                "accepted_issue_count": 2,
            },
            "queue": {
                "missing_recording_sidecars": [],
                "stale_recording_sidecars": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
                "recording_newer_than_source": [],
                "exact_segment_macros": [{"name": "sig", "review_command": "./bin/macro_recording_json.sh sig"}],
                "title_segment_macros": [],
            },
            "active_queue": {
                "missing_recording_sidecars": [],
                "stale_recording_sidecars": [],
                "recording_newer_than_source": [],
                "exact_segment_macros": [],
                "title_segment_macros": [],
            },
            "ordered": [{"name": "sig", "kind": "stale_recording_sidecar"}, {"name": "sig", "kind": "exact_segments"}],
            "active_ordered": [],
        },
    )
    _write_json_stub(
        bin_dir / "macro_acceptance_ledger_json.sh",
        {
            "summary": {"accepted_macro_count": 1, "review_acceptance_macro_count": 1, "runtime_acceptance_macro_count": 0},
            "macros": [{"name": "sig", "accepted_review_issue_codes": ["stale_recording_sidecar", "exact_segments"], "review_acceptances": []}],
        },
    )
    _write_json_stub(
        bin_dir / "next_action_json.sh",
        {
            "primary_action": {"id": "runtime_ready", "command": "./bin/list_macros.sh"},
            "review_queue_source": {"mode": "authoritative_helper"},
            "recommendation_trace": {"selected_action_id": "runtime_ready"},
        },
    )

    next_payload = json.loads(subprocess.check_output([str(bin_dir / "next_action_json.sh")], text=True))
    assert next_payload["primary_action"]["id"] == "runtime_ready"

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["review_counts"]["needs_review_count"] == 0
    assert payload["macro_review_queue"]["accepted_counts"]["accepted_issue_count"] == 2
    assert payload["macro_review_queue"]["queue"]["stale_recording_sidecars"] == []
    assert payload["macro_acceptance_ledger"]["summary"]["accepted_macro_count"] == 1
    assert payload["sources"]["helpers"]["macro_review_queue_json"]["accepted_issue_count"] == 2
    assert payload["sources"]["helpers"]["macro_acceptance_ledger_json"]["accepted_macro_count"] == 1

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "review_queue_needs_review_count=0" in summary
    assert "review_queue_accepted_issue_count=2" in summary
    assert "acceptance_ledger_macro_count=1" in summary


def test_generated_stack_state_json_carries_dispatch_history_board(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_dispatch_history"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"health": {"ready": True, "issues": []}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_candidate", "counts_by_posture_id": {"warm_dispatch_candidate": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_candidate"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1, "unresolved_force_override_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_before_dispatch", "command": "./bin/macro_author_loop_json.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["macro_dispatch_history_board"]["summary"]["primary_posture_id"] == "blocked_repeated_recently"
    assert payload["macro_dispatch_history_board"]["summary"]["attention_macro_count"] == 1
    assert payload["sources"]["helpers"]["macro_dispatch_history_board_json"]["primary_posture_id"] == "blocked_repeated_recently"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "dispatch_history_primary_macro=sig" in summary
    assert "dispatch_history_primary_posture=blocked_repeated_recently" in summary
    assert "dispatch_history_attention_macro_count=1" in summary


def test_generated_stack_state_json_carries_startup_handoff_witness_duplicate_risk(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_startup_handoff_duplicate"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"runtime": {"socket_unit": "vhk-busd-p.socket", "service_unit": "vhk-busd-p.service"}, "health": {"ready": True, "issues": []}, "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}}})
    _write_json_stub(bin_dir / "startup_handoff_status_json.sh", {"startup_handoff": {"verdict": "duplicate_start_risk", "summary": "Both the user unit and autostart bridge currently own startup.", "counts": {"enabled_unit_count": 2, "masked_unit_count": 0}, "autostart": {"state": "present", "effective": True}}})
    _write_json_stub(bin_dir / "startup_handoff_drift_json.sh", {"drift": {"verdict": "chronic_duplicate_risk", "summary": "Duplicate-start risk has repeated across recent snapshots.", "recent_verdicts": ["duplicate_start_risk", "duplicate_start_risk"]}, "history": {"sample_count": 2}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "clean_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "runtime_ready", "command": "./bin/dispatch_macro.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["startup_handoff_witness"]["status_id"] == "duplicate_start_risk"
    assert payload["startup_handoff_witness"]["route_id"] == "dedupe_startup_owners"
    assert payload["startup_handoff_witness"]["recommended"]["command"] == "./bin/startup_handoff_status_json.sh"
    assert payload["sources"]["helpers"]["startup_handoff_status_json"]["verdict"] == "duplicate_start_risk"
    assert payload["sources"]["helpers"]["startup_handoff_drift_json"]["verdict"] == "chronic_duplicate_risk"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "startup_handoff_witness_status=duplicate_start_risk" in summary
    assert "startup_handoff_verdict=duplicate_start_risk" in summary
    assert "startup_handoff_drift_verdict=chronic_duplicate_risk" in summary


def test_generated_stack_state_json_carries_startup_handoff_witness_primary_owner_ready(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_startup_handoff_ready"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"runtime": {"socket_unit": "vhk-busd-p.socket", "service_unit": "vhk-busd-p.service"}, "health": {"ready": True, "issues": []}, "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}}})
    _write_json_stub(bin_dir / "startup_handoff_status_json.sh", {"startup_handoff": {"verdict": "primary_user_unit_owner", "summary": "The VHK user unit is the only effective startup owner.", "counts": {"enabled_unit_count": 1, "masked_unit_count": 0}, "autostart": {"state": "absent", "effective": False}}})
    _write_json_stub(bin_dir / "startup_handoff_drift_json.sh", {"drift": {"verdict": "stable", "summary": "Startup ownership is stable.", "recent_verdicts": ["primary_user_unit_owner", "primary_user_unit_owner"]}, "history": {"sample_count": 2}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "clean_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"generated_stack_command": "dispatch_macro.sh sig"}, "preferred_execution_mode": "warm_runtime_dispatch"}, "macros": [{"name": "sig", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"generated_stack_command": "dispatch_macro.sh sig"}, "preferred_execution_mode": "warm_runtime_dispatch"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "runtime_ready", "command": "./bin/dispatch_macro.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    assert payload["startup_handoff_witness"]["status_id"] == "startup_owner_current"
    assert payload["startup_handoff_witness"]["route_id"] == "startup_ok_then_runtime"
    assert payload["startup_handoff_witness"]["recommended"]["command"] == "./bin/dispatch_macro.sh sig"
    assert payload["sources"]["helpers"]["startup_handoff_status_json"]["selected_startup_handoff_witness_status_id"] == "startup_owner_current"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "startup_handoff_witness_status=startup_owner_current" in summary
    assert "startup_handoff_verdict=primary_user_unit_owner" in summary


def test_generated_stack_state_json_carries_startup_handoff_repair_ticket_duplicate_risk(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_startup_handoff_repair_duplicate"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    autostart_path = str((tmp_path / "autostart" / "vhk-busd-p.desktop").resolve())
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"runtime": {"socket_unit": "vhk-busd-p.socket", "service_unit": "vhk-busd-p.service"}, "health": {"ready": True, "issues": []}, "units": {"socket": {"ActiveState": "active"}, "service": {"ActiveState": "active"}}})
    _write_json_stub(bin_dir / "startup_handoff_status_json.sh", {"startup_handoff": {"verdict": "duplicate_start_risk", "summary": "Both the user unit and autostart bridge currently own startup.", "counts": {"enabled_unit_count": 1, "masked_unit_count": 0}, "autostart": {"path": autostart_path, "state": "present", "effective": True}}})
    _write_json_stub(bin_dir / "startup_handoff_drift_json.sh", {"drift": {"verdict": "chronic_duplicate_risk", "summary": "Duplicate-start risk has repeated across recent snapshots.", "recent_verdicts": ["duplicate_start_risk", "duplicate_start_risk"]}, "history": {"sample_count": 2}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "emitted", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "ok", "ready_to_iterate": True}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "warm_dispatch_ready", "counts_by_posture_id": {"warm_dispatch_ready": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "warm_dispatch_ready"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "clean_recent_dispatch", "attention_macro_count": 0}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "clean_recent_dispatch"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 1, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"generated_stack_command": "./bin/dispatch_macro.sh sig"}, "preferred_execution_mode": "warm_runtime_dispatch"}, "macros": [{"name": "sig", "dispatch_readiness": {"can_emit_minimal_payload_now": True}, "dispatch_contract": {"generated_stack_command": "./bin/dispatch_macro.sh sig"}, "preferred_execution_mode": "warm_runtime_dispatch"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "runtime_ready", "command": "./bin/dispatch_macro.sh sig"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["startup_handoff_repair_ticket"]
    assert ticket["status_id"] == "prefer_user_unit_owner"
    assert ticket["route_id"] == "hide_autostart_bridge_then_verify"
    assert ticket["target_owner_id"] == "primary_user_unit_owner"
    assert "Hidden=true" in ticket["recommended"]["command"]
    assert autostart_path in ticket["recommended"]["command"]
    assert payload["sources"]["helpers"]["startup_handoff_status_json"]["selected_startup_handoff_repair_ticket_status_id"] == "prefer_user_unit_owner"
    assert payload["sources"]["helpers"]["startup_handoff_drift_json"]["selected_startup_handoff_repair_ticket_route_id"] == "hide_autostart_bridge_then_verify"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "startup_handoff_repair_ticket_status=prefer_user_unit_owner" in summary
    assert "startup_handoff_repair_ticket_route=hide_autostart_bridge_then_verify" in summary


def test_generated_stack_state_json_carries_startup_handoff_repair_ticket_promote_user_unit_owner(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_startup_handoff_repair_promote"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    bin_dir = out_dir / "bin"
    _write_json_stub(bin_dir / "check_runtime_json.sh", {"project": {"exists": True, "project_yaml_exists": True, "macro_files": ["macros/sig.yaml"]}, "env": {"session_ready": True}, "commands": {"xdotool": True, "xprop": True, "xwininfo": True, "xclip": True}, "capabilities": {"warm_runtime": True}, "health": {"blockers": [], "warnings": []}})
    _write_json_stub(bin_dir / "status_runtime_json.sh", {"runtime": {"socket_unit": "vhk-busd-p.socket", "service_unit": "vhk-busd-p.service"}, "health": {"ready": False, "issues": ["socket inactive"]}, "units": {"socket": {"ActiveState": "inactive"}, "service": {"ActiveState": "inactive"}}})
    _write_json_stub(bin_dir / "startup_handoff_status_json.sh", {"startup_handoff": {"verdict": "fallback_autostart_owner", "summary": "The XDG autostart bridge currently owns startup.", "counts": {"enabled_unit_count": 0, "masked_unit_count": 0}, "autostart": {"path": str((tmp_path / "autostart" / "vhk-busd-p.desktop").resolve()), "state": "present", "effective": True}}})
    _write_json_stub(bin_dir / "startup_handoff_drift_json.sh", {"drift": {"verdict": "stable", "summary": "Startup ownership is stable but still autostart-owned.", "recent_verdicts": ["fallback_autostart_owner", "fallback_autostart_owner"]}, "history": {"sample_count": 2}})
    _write_json_stub(bin_dir / "latest_run_json.sh", {"latest_run": {"macro": "sig", "ok": True}})
    _write_json_stub(bin_dir / "latest_dispatch_json.sh", {"latest_dispatch": {"macro": "sig", "result": "blocked", "route": "checked_dispatch"}})
    _write_json_stub(bin_dir / "latest_run_health_json.sh", {"health": {"verdict": "warn", "ready_to_iterate": False}})
    _write_json_stub(bin_dir / "macro_inventory_json.sh", {"project": {"macro_count": 1, "groups": [], "tags": []}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_entrypoints_json.sh", {"project": {"macro_count": 1, "interactive_macro_count": 0, "preset_enabled_macro_count": 0}, "macros": []})
    _write_json_stub(bin_dir / "macro_author_queue_json.sh", {"summary": {"primary_macro_name": "sig"}, "primary_macro": {"name": "sig"}, "macros": [{"name": "sig"}]})
    _write_json_stub(bin_dir / "macro_replay_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "verified_recent", "counts_by_posture_id": {"verified_recent": 1}}, "primary_macro": {"name": "sig", "replay_posture": {"id": "verified_recent"}}, "macros": [{"name": "sig", "replay_posture": {"id": "verified_recent"}}]})
    _write_json_stub(bin_dir / "macro_runtime_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "stabilize_first", "counts_by_posture_id": {"stabilize_first": 1}}, "primary_macro": {"name": "sig", "runtime_posture": {"id": "stabilize_first"}}, "macros": [{"name": "sig", "runtime_posture": {"id": "stabilize_first"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_history_board_json.sh", {"summary": {"primary_macro_name": "sig", "primary_posture_id": "blocked_repeated_recently", "attention_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}, "macros": [{"name": "sig", "dispatch_history_posture": {"id": "blocked_repeated_recently"}}]})
    _write_json_stub(bin_dir / "macro_dispatch_catalog_json.sh", {"runtime": {"bus_event": "hotkey"}, "summary": {"primary_macro_name": "sig", "dispatch_ready_now_count": 0, "thin_dispatch_macro_count": 1}, "primary_macro": {"name": "sig", "dispatch_readiness": {"can_emit_minimal_payload_now": False}, "dispatch_contract": {"generated_stack_command": "./bin/dispatch_macro.sh sig"}, "preferred_execution_mode": "warm_runtime_dispatch"}, "macros": [{"name": "sig", "dispatch_readiness": {"can_emit_minimal_payload_now": False}, "dispatch_contract": {"generated_stack_command": "./bin/dispatch_macro.sh sig"}, "preferred_execution_mode": "warm_runtime_dispatch"}]})
    _write_json_stub(bin_dir / "macro_review_queue_json.sh", {"counts": {"needs_review_count": 0}, "queue": {}, "ordered": []})
    _write_json_stub(bin_dir / "next_action_json.sh", {"primary_action": {"id": "inspect_runtime", "command": "./bin/status_runtime.sh"}})

    payload = json.loads(subprocess.check_output([str(bin_dir / "stack_state_json.sh")], text=True))
    ticket = payload["startup_handoff_repair_ticket"]
    assert ticket["status_id"] == "promote_user_unit_owner"
    assert ticket["route_id"] == "enable_user_unit_then_verify"
    assert ticket["target_owner_id"] == "primary_user_unit_owner"
    assert ticket["recommended"]["command"] == "systemctl --user daemon-reload && systemctl --user enable --now vhk-busd-p.socket"
    assert payload["sources"]["helpers"]["startup_handoff_status_json"]["selected_startup_handoff_repair_ticket_command"] == "systemctl --user daemon-reload && systemctl --user enable --now vhk-busd-p.socket"

    summary = subprocess.check_output([str(bin_dir / "stack_state.sh")], text=True)
    assert "startup_handoff_repair_ticket_status=promote_user_unit_owner" in summary
    assert "startup_handoff_repair_ticket_route=enable_user_unit_then_verify" in summary



def test_generated_stack_state_json_carries_primary_macro_replay_ticket_rerun_after_contract_change(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / 'stack_replay_ticket_stale_contract'
    runner = CliRunner()
    result = runner.invoke(app, ['gen-i3-busd-stack', str(proj), '--out-dir', str(out_dir), '--watcher', 'hotkeys'])
    assert result.exit_code == 0, result.output

    bin_dir = out_dir / 'bin'
    systemd_user_dir = out_dir / 'systemd-user'

    def _write_json_stub(path: Path, payload: dict[str, Any]):
        path.write_text('#!/usr/bin/env python3\nimport json\nprint(json.dumps(' + json.dumps(payload) + '))\n', encoding='utf-8')
        path.chmod(0o755)

    def _write_text_stub(path: Path, text: str):
        path.write_text('#!/usr/bin/env bash\nprintf %s ' + shlex.quote(text) + '\n', encoding='utf-8')
        path.chmod(0o755)

    _write_json_stub(bin_dir / 'check_runtime_json.sh', {'health': {'blockers': [], 'warnings': []}, 'capabilities': {'warm_runtime': True}, 'ready': True, 'service': {'active': True}, 'socket': {'listening': True}, 'x11': {'display_present': True}, 'dispatch_path_probe': {'ok': True}, 'dispatch_path_summary': {'ok': True}, 'session_attachment': {'status': 'attached'}, 'resident_service': {'status': 'attached'}})
    _write_json_stub(bin_dir / 'status_runtime_json.sh', {'health': {'ready': True, 'issues': []}})
    _write_json_stub(bin_dir / 'latest_run_json.sh', {'latest_run': {'macro': 'sig', 'ok': True}})
    _write_json_stub(bin_dir / 'latest_dispatch_json.sh', {'latest_dispatch': {'macro': 'sig', 'result': 'emitted', 'route': 'checked_dispatch'}})
    _write_json_stub(bin_dir / 'latest_run_health_json.sh', {'health': {'verdict': 'stale', 'ready_to_iterate': False}})
    _write_json_stub(bin_dir / 'macro_inventory_json.sh', {'project': {'macro_count': 1}, 'macros': [{'name': 'sig'}]})
    _write_json_stub(bin_dir / 'macro_entrypoints_json.sh', {'project': {'macro_count': 1, 'interactive_macro_count': 0, 'preset_enabled_macro_count': 0}, 'macros': [{'name': 'sig', 'execution': {'preferred_mode': 'warm_runtime_dispatch'}, 'preferred_entrypoints': {'author_loop': './bin/macro_author_loop_json.sh sig', 'recording_review': './bin/macro_recording_json.sh sig', 'warm_runtime_checked': './bin/dispatch_macro_checked.sh sig', 'warm_runtime_gate': './bin/macro_dispatch_gate_json.sh sig', 'direct_run': './bin/run_macro.sh sig', 'contract': './bin/macro_contract_json.sh sig', 'latest_run': './bin/macro_latest_run_json.sh sig', 'latest_report': './bin/macro_report_latest.sh sig', 'latest_trace': './bin/macro_trace_latest.sh sig'}}]})
    _write_json_stub(bin_dir / 'macro_author_queue_json.sh', {'summary': {'primary_macro_name': 'sig'}, 'primary_macro': {'name': 'sig'}, 'macros': [{'name': 'sig'}]})
    _write_json_stub(bin_dir / 'macro_latest_run_json.sh', {'macro': {'name': 'sig'}, 'latest_run': {'macro': 'sig', 'ok': True}, 'latest_run_health': {'verdict': 'stale', 'summary': 'The latest matching replay proof no longer matches the current macro or recorder contract.', 'proof_contract': {'in_sync': False, 'source_changed': True}, 'next_step': {'id': 'rerun_after_contract_change', 'command': './bin/run_macro.sh sig'}}, 'replay_posture': {'id': 'stale_contract', 'summary': 'stale replay proof'}, 'preferred_entrypoints': {'latest_run_json': './bin/macro_latest_run_json.sh sig', 'latest_report': './bin/macro_report_latest.sh sig', 'latest_trace': './bin/macro_trace_latest.sh sig', 'history': './bin/history_runs.sh --macro sig --limit 5'}, 'next_step': {'id': 'rerun_after_contract_change', 'command': './bin/run_macro.sh sig'}})
    _write_json_stub(bin_dir / 'macro_contract_json.sh', {'macro': {'name': 'sig', 'desktop_target': {'selector_source_id': 'macro_when', 'summary': 'Dispatch expects the focused X11 window to match the macro when: selector.'}, 'hints': {'preferred_execution_mode': 'warm_runtime_dispatch'}}})
    _write_json_stub(bin_dir / 'macro_author_loop_json.sh', {'macro': {'name': 'sig'}, 'execution': {'runtime_posture': {'id': 'warm_dispatch_candidate'}, 'preferred_execution_mode': 'warm_runtime_dispatch', 'dispatch_gate': {'decision': {'id': 'stabilize_before_dispatch'}}}, 'next_step': {'id': 'rerun_after_contract_change', 'command': './bin/run_macro.sh sig'}})
    _write_json_stub(bin_dir / 'macro_recording_json.sh', {'macro': {'name': 'sig'}, 'recording': {'exists': True, 'has_recorded_context': True, 'freshness': {'status': 'aligned'}}, 'review': {'generated_stack': {'recording_review': './bin/macro_recording_json.sh sig'}}})
    _write_json_stub(bin_dir / 'macro_replay_board_json.sh', {'summary': {'primary_macro_name': 'sig', 'primary_posture_id': 'stale_contract'}, 'primary_macro': {'name': 'sig', 'replay_posture': {'id': 'stale_contract'}}, 'macros': [{'name': 'sig', 'replay_posture': {'id': 'stale_contract'}, 'latest_run_context': {'scope': 'matching_macro', 'latest_macro': 'sig', 'latest_run': {'macro': 'sig', 'ok': True}, 'latest_run_health': {'verdict': 'stale'}}}]})
    _write_json_stub(bin_dir / 'macro_runtime_board_json.sh', {'summary': {'primary_macro_name': 'sig', 'primary_posture_id': 'warm_dispatch_candidate'}, 'primary_macro': {'name': 'sig', 'runtime_posture': {'id': 'warm_dispatch_candidate'}}, 'macros': [{'name': 'sig', 'runtime_posture': {'id': 'warm_dispatch_candidate'}}]})
    _write_json_stub(bin_dir / 'macro_dispatch_history_board_json.sh', {'summary': {'primary_macro_name': 'sig', 'primary_posture_id': 'dispatch_clean_recently', 'attention_macro_count': 0}, 'primary_macro': {'name': 'sig', 'dispatch_history_posture': {'id': 'dispatch_clean_recently'}}, 'macros': [{'name': 'sig', 'dispatch_history_posture': {'id': 'dispatch_clean_recently'}, 'dispatch_history': {'latest_receipt': {'macro': 'sig', 'result': 'emitted', 'route': 'checked_dispatch'}, 'primary_blocked_class_id': None, 'unresolved_force_override': False}}]})
    _write_json_stub(bin_dir / 'macro_dispatch_catalog_json.sh', {'runtime': {'bus_event': 'hotkey'}, 'summary': {'primary_macro_name': 'sig', 'dispatch_ready_now_count': 0}, 'primary_macro': {'name': 'sig', 'preferred_execution_mode': 'warm_runtime_dispatch', 'dispatch_readiness': {'can_emit_minimal_payload_now': False}}, 'macros': [{'name': 'sig', 'preferred_execution_mode': 'warm_runtime_dispatch', 'dispatch_readiness': {'can_emit_minimal_payload_now': False}, 'dispatch_contract': {'bus_event': 'hotkey', 'generated_stack_checked_command': './bin/dispatch_macro_checked.sh sig', 'generated_stack_gate_command': './bin/macro_dispatch_gate_json.sh sig', 'contract_wrapper': './bin/macro_contract_json.sh sig'}}]})
    _write_json_stub(bin_dir / 'macro_dispatch_gate_json.sh', {'preferred_execution_mode': 'warm_runtime_dispatch', 'decision': {'id': 'stabilize_before_dispatch', 'command': './bin/run_macro.sh sig'}, 'repair_action': {'id': 'refresh_replay_proof', 'command': './bin/run_macro.sh sig', 'reason': 'rerun after contract drift'}, 'dispatch_readiness': {'can_emit_minimal_payload_now': False, 'primary_blocker_class_id': 'run_proof_gap'}})
    _write_json_stub(bin_dir / 'macro_review_queue_json.sh', {'counts': {'needs_review_count': 0}, 'queue': {}, 'ordered': []})
    _write_json_stub(bin_dir / 'macro_acceptance_ledger_json.sh', {'summary': {'accepted_macro_count': 0}, 'macros': []})
    _write_json_stub(bin_dir / 'next_action_json.sh', {'primary_action': {'id': 'rerun_after_contract_change', 'command': './bin/run_macro.sh sig'}})
    _write_text_stub(bin_dir / 'stack_state.sh', 'primary_macro_replay_ticket_status=rerun_after_contract_change\n')

    payload = json.loads(subprocess.check_output([str(bin_dir / 'stack_state_json.sh')], text=True))
    ticket = payload['primary_macro_replay_ticket']
    assert ticket['status_id'] == 'rerun_after_contract_change'
    assert ticket['route_id'] == 'rerun_then_replay_refresh'
    assert ticket['recommended']['command'] == './bin/run_macro.sh sig'
    assert ticket['signals']['replay_posture_id'] == 'stale_contract'
    assert payload['sources']['helpers']['macro_author_queue_json']['selected_macro_replay_ticket_status_id'] == 'rerun_after_contract_change'

    summary = subprocess.check_output([str(bin_dir / 'stack_state.sh')], text=True)
    assert 'primary_macro_replay_ticket_status=rerun_after_contract_change' in summary



def test_generated_stack_writes_record_runtime_acceptance_wrapper(tmp_path: Path):
    proj = _make_project(tmp_path)
    out_dir = tmp_path / "stack_runtime_acceptance_wrapper"

    res = runner.invoke(app, ["gen-i3-busd-stack", str(proj), "--out-dir", str(out_dir), "--watcher", "hotkeys"])
    assert res.exit_code == 0, res.output

    script_path = out_dir / "bin" / "record_runtime_acceptance.sh"
    assert script_path.exists()
    text = script_path.read_text()
    assert 'usage: record_runtime_acceptance.sh <macro-name> --accepted-by <name> --note <text>' in text
    assert 'macro-runtime-accept "$PROJECT_ROOT" "$MACRO_NAME" "$@"' in text
