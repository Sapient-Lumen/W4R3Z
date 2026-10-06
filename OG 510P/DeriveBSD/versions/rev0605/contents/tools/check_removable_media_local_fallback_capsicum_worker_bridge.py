#!/usr/bin/env python3
"""Validate the FreeBSD Capsicum worker bridge contract.

This guard closes the gap between "we have a C scaffold" and "the backend runner
knows real apply must use that scaffold, not the Python fixture worker."  It
validates the bridge receipt, checks the source digest, runs the cloudtainer
syntax probe, and rejects dead/unreachable host-runner code that looks like real
apply but is gated before the worker bridge exists.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

import removable_media_capsicum_worker_bridge as bridge
import run_removable_media_local_freebsd_backend as backend
from cube_digest_lib import load_json

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REL = "spec/removable.media.capsicum.worker.bridge.schema.json"
EXAMPLE_REL = bridge.EXAMPLE_REL
VALIDATION_REL = bridge.VALIDATION_REL
DOC_TOKENS = {
    "README.md": [bridge.VERSION, "Capsicum worker bridge", "check_removable_media_local_fallback_capsicum_worker_bridge.py"],
    "docs/00-index.md": [bridge.VERSION, "removable.media.capsicum.worker.bridge"],
    "docs/99-llm-runbook.md": ["check_removable_media_local_fallback_capsicum_worker_bridge.py", "capsicum-worker-required-for-real-apply"],
    "docs/current/removable-media-capsicum-worker-bridge.md": [
        "removable.media.capsicum.worker.bridge",
        "rm_post_detach_capsicum_worker.c",
        "python-fd-worker-cloudtainer-only",
        "freebsd-capsicum-c-worker",
        "close-fd-0-1-2-before-cap-enter",
        "delegated-output-fd-after-stdio-close",
        "extra_fds_closed_before_cap_enter",
        "fd-5",
        "input_sha256",
        "duplicate-target-fds-above-delegated-range-before-clearing-slots",
    ],
    "docs/current/removable-media-local-fallback-freebsd-backend-run.md": [
        "worker_bridge",
        "removable.media.capsicum.worker.bridge",
        "capsicum-worker-required-for-real-apply",
    ],
}


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def get(obj: dict[str, Any], *path: str) -> Any:
    cur: Any = obj
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def validate_schema(obj: dict[str, Any]) -> list[str]:
    schema = load_json(ROOT, SCHEMA_REL)
    validator = Draft202012Validator(schema)
    return [e.message for e in sorted(validator.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def semantic_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.capsicum.worker.bridge", "wrong kind")
    require(errors, obj.get("schema_version") == "0.1", "schema_version must be 0.1")
    require(errors, obj.get("bridge_id") == bridge.BRIDGE_ID, "bridge_id must bind current bridge cut")
    require(errors, obj.get("generated_for_version") == bridge.VERSION, "generated_for_version must bind current bridge cut")
    require(errors, obj.get("result") == "passed", "bridge receipt must pass")

    source = obj.get("source", {}) if isinstance(obj.get("source"), dict) else {}
    build = obj.get("build", {}) if isinstance(obj.get("build"), dict) else {}
    launch = obj.get("launch_contract", {}) if isinstance(obj.get("launch_contract"), dict) else {}
    integration = obj.get("backend_integration", {}) if isinstance(obj.get("backend_integration"), dict) else {}
    invariants = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}

    require(errors, source.get("sha256") == bridge.sha256_file(bridge.SOURCE), "source digest must match checked-in C worker")
    require(errors, source.get("delegated_input_fd") == 3 and source.get("delegated_output_fd") == 4, "bridge must bind fds 3 and 4")
    require(errors, source.get("closefrom_fd") == 5, "bridge must close fds above delegated set")
    require(errors, source.get("extra_fd_canary") == 5, "bridge must bind the fd-5 inherited-fd canary")
    require(errors, source.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "fd-5 canary must be broker-owned non-media authority")
    require(errors, source.get("extra_fd_canary_must_be_observed_before_closefrom") is True, "bridge must require observing fd-5 before closefrom")
    require(errors, source.get("extra_fd_scan_limit") == 64, "bridge must bind the worker extra-fd scan limit")
    require(errors, source.get("reported_input_digest_field") == "input_sha256", "bridge must bind the worker input digest report field")
    require(errors, source.get("stdio_policy") == "close-fd-0-1-2-before-cap-enter", "bridge must bind production stdio closure policy")
    require(errors, source.get("failure_report_channel") == "delegated-output-fd-after-stdio-close", "bridge must bind delegated-output failure report channel")
    require(errors, source.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "bridge must bind startup failure report channel")
    require(errors, source.get("startup_pre_stdio_failure_report_channel") == "delegated-output-fd-before-stdio-close", "bridge must bind pre-stdio startup failure report channel")
    require(errors, source.get("path_arguments_accepted") is False, "worker source must accept no path arguments")

    probe = build.get("cloudtainer_probe_result", {}) if isinstance(build.get("cloudtainer_probe_result"), dict) else {}
    require(errors, build.get("production_os") == "FreeBSD", "production bridge must target FreeBSD")
    require(errors, build.get("binary_residence") == "private-work-root-only-not-reused-from-user-path", "binary must live under a private work root")
    require(errors, build.get("binary_digest_required_in_host_receipt") is True, "host receipt must bind binary digest")
    require(errors, "-DDERIVEBSD_CAPSICUM_COMPILE_PROBE=1" in build.get("cloudtainer_probe_result", {}).get("command", []), "cloudtainer probe must use explicit shim define")
    require(errors, probe.get("return_code") == 0 and probe.get("timed_out") is False, "cloudtainer syntax probe must pass")
    exec_probe = build.get("cloudtainer_execution_probe_result", {}) if isinstance(build.get("cloudtainer_execution_probe_result"), dict) else {}
    success_run = exec_probe.get("success_run", {}) if isinstance(exec_probe.get("success_run"), dict) else {}
    failure_run = exec_probe.get("failure_run", {}) if isinstance(exec_probe.get("failure_run"), dict) else {}
    argument_run = exec_probe.get("argument_rejection_run", {}) if isinstance(exec_probe.get("argument_rejection_run"), dict) else {}
    success_report = success_run.get("output_report", {}) if isinstance(success_run.get("output_report"), dict) else {}
    failure_report = failure_run.get("output_report", {}) if isinstance(failure_run.get("output_report"), dict) else {}
    argument_report = argument_run.get("output_report", {}) if isinstance(argument_run.get("output_report"), dict) else {}
    require(errors, exec_probe.get("result") == "passed", "cloudtainer shim execution probe must pass")
    require(errors, exec_probe.get("claim") == "cloudtainer-shim-execution-probe-not-capsicum-execution", "execution probe must not overclaim Capsicum")
    require(errors, success_run.get("return_code") == 0 and success_report.get("result") == "passed", "execution probe success case must run and report passed")
    require(errors, success_report.get("failure_report_channel") == "delegated-output-fd-after-stdio-close", "success probe must carry failure report channel binding")
    require(errors, success_report.get("stdio_fds_closed_before_report") is True, "success probe must prove stdio was closed before the output report")
    require(errors, success_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "success probe must carry startup failure channel policy")
    require(errors, success_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "success probe must carry startup failure channel binding")
    require(errors, success_report.get("stdio_fds_closed_before_cap_enter") is True, "success probe must prove stdio was closed before cap_enter")
    require(errors, success_run.get("pass_fds") == [3, 4, 5], "success probe subprocess must pass fd 5, not merely create it in the parent")
    require(errors, success_run.get("worker_env_policy") == "empty-environment" and success_run.get("worker_env_keys_passed") == [], "success probe must launch with an empty worker environment")
    require(errors, success_run.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo" and success_run.get("worker_cwd_contains_media_tree") is False, "success probe must use a private non-media worker cwd")
    require(errors, success_run.get("extra_fd_canary") == 5 and success_run.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "success probe must pass a broker non-media fd-5 canary")
    require(errors, success_run.get("extra_fd_canary_passed_to_child") is True, "success probe must mark fd-5 as child-inherited")
    require(errors, success_run.get("launcher_fd_slot_policy") == "duplicate-target-fds-above-delegated-range-before-clearing-slots", "success probe must save target fd slots before opening delegated files")
    require(errors, success_run.get("launcher_restored_parent_fd_slots") is True, "success probe launcher must restore parent fd slots after worker")
    success_slot = success_run.get("launcher_fd_slot_evidence", {}) if isinstance(success_run.get("launcher_fd_slot_evidence"), dict) else {}
    require(errors, success_slot.get("preexisting_parent_fd_slots_preserved") is True, "success probe fd-slot evidence must preserve parent slots")
    require(errors, success_slot.get("preexisting_parent_fd_inheritable_flags_preserved") is True, "success probe fd-slot evidence must preserve parent inheritable flags")
    require(errors, success_report.get("extra_fd_canary_observed_before_closefrom") is True, "success worker report must prove fd-5 was observed before closefrom")
    require(errors, success_report.get("extra_fds_closed_before_cap_enter") is True, "success probe must prove extra inherited fds were closed before cap_enter")
    require(errors, success_report.get("extra_fd_scan_limit") == 64, "success probe must bind the extra-fd scan limit")
    require(errors, failure_run.get("return_code") == 1 and failure_report.get("result") == "failed", "execution probe failure case must run and report failed")
    require(errors, failure_report.get("error_code") == "input_fd_not_regular", "execution probe must prove non-regular fd failure is output-visible")
    require(errors, failure_report.get("failure_report_channel") == "delegated-output-fd-after-stdio-close", "failure probe must report through delegated output fd after stdio closure")
    require(errors, failure_report.get("stdio_fds_closed_before_report") is True, "post-stdio failure probe must prove stdio was closed before the report")
    require(errors, failure_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "failure probe must carry startup failure channel policy")
    require(errors, failure_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "failure probe must carry startup failure channel binding")
    require(errors, failure_report.get("stdio_fds_closed_before_cap_enter") is True, "post-stdio failure probe must prove stdio closure truthfully")
    require(errors, failure_run.get("pass_fds") == [3, 4, 5], "failure probe subprocess must pass fd 5, not merely create it in the parent")
    require(errors, failure_run.get("worker_env_policy") == "empty-environment" and failure_run.get("worker_env_keys_passed") == [], "failure probe must launch with an empty worker environment")
    require(errors, failure_run.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo" and failure_run.get("worker_cwd_contains_media_tree") is False, "failure probe must use a private non-media worker cwd")
    require(errors, failure_run.get("extra_fd_canary") == 5 and failure_run.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "failure probe must pass a broker non-media fd-5 canary")
    require(errors, failure_run.get("extra_fd_canary_passed_to_child") is True, "failure probe must mark fd-5 as child-inherited")
    require(errors, failure_run.get("launcher_fd_slot_policy") == "duplicate-target-fds-above-delegated-range-before-clearing-slots", "failure probe must save target fd slots before opening delegated files")
    require(errors, failure_run.get("launcher_restored_parent_fd_slots") is True, "failure probe launcher must restore parent fd slots after worker")
    failure_slot = failure_run.get("launcher_fd_slot_evidence", {}) if isinstance(failure_run.get("launcher_fd_slot_evidence"), dict) else {}
    require(errors, failure_slot.get("preexisting_parent_fd_slots_preserved") is True, "failure probe fd-slot evidence must preserve parent slots")
    require(errors, failure_slot.get("preexisting_parent_fd_inheritable_flags_preserved") is True, "failure probe fd-slot evidence must preserve parent inheritable flags")
    require(errors, failure_report.get("extra_fd_canary_observed_before_closefrom") is True, "failure worker report must prove fd-5 was observed before closefrom")
    require(errors, failure_report.get("extra_fds_closed_before_cap_enter") is True, "post-stdio failure probe must prove extra inherited fds were closed before cap_enter")
    require(errors, failure_report.get("extra_fd_scan_limit") == 64, "failure probe must bind the extra-fd scan limit")
    require(errors, argument_run.get("return_code") == 1 and argument_report.get("result") == "failed", "execution probe argument rejection must run and report failed")
    require(errors, argument_report.get("error_code") == "path_arguments_rejected", "execution probe must prove argv path rejection is output-visible")
    require(errors, argument_report.get("failure_report_channel") == "delegated-output-fd-before-stdio-close", "startup argument rejection must truthfully report pre-stdio-close delivery")
    require(errors, argument_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "argument rejection must carry startup failure channel binding")
    require(errors, argument_report.get("stdio_fds_closed_before_cap_enter") is False, "startup argument rejection must not claim stdio was closed")
    require(errors, argument_run.get("pass_fds") == [3, 4, 5], "argument-rejection probe subprocess must pass fd 5, not merely create it in the parent")
    require(errors, argument_run.get("worker_env_policy") == "empty-environment" and argument_run.get("worker_env_keys_passed") == [], "argument-rejection probe must launch with an empty worker environment")
    require(errors, argument_run.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo" and argument_run.get("worker_cwd_contains_media_tree") is False, "argument-rejection probe must use a private non-media worker cwd")
    require(errors, argument_run.get("extra_fd_canary") == 5 and argument_run.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "argument-rejection probe must pass the same broker non-media fd-5 canary")
    require(errors, argument_run.get("extra_fd_canary_passed_to_child") is True, "argument-rejection probe must mark fd-5 as child-inherited")
    require(errors, argument_run.get("launcher_fd_slot_policy") == "duplicate-target-fds-above-delegated-range-before-clearing-slots", "argument-rejection probe must save target fd slots before opening delegated files")
    require(errors, argument_run.get("launcher_restored_parent_fd_slots") is True, "argument-rejection probe launcher must restore parent fd slots after worker")
    argument_slot = argument_run.get("launcher_fd_slot_evidence", {}) if isinstance(argument_run.get("launcher_fd_slot_evidence"), dict) else {}
    require(errors, argument_slot.get("preexisting_parent_fd_slots_preserved") is True, "argument probe fd-slot evidence must preserve parent slots")
    require(errors, argument_slot.get("preexisting_parent_fd_inheritable_flags_preserved") is True, "argument probe fd-slot evidence must preserve parent inheritable flags")
    require(errors, argument_report.get("extra_fd_canary_observed_before_closefrom") is True, "argument-rejection worker report must prove fd-5 was observed before closefrom")
    require(errors, argument_report.get("extra_fds_closed_before_cap_enter") is False, "startup argument rejection must not claim extra-fd closure before closefrom")
    require(errors, argument_report.get("extra_fd_scan_limit") == 64, "argument probe must bind the extra-fd scan limit")
    require(errors, success_run.get("stderr_bytes") == 0 and failure_run.get("stderr_bytes") == 0 and argument_run.get("stderr_bytes") == 0, "shim execution probes must not rely on stderr")

    for key in [
        "broker_must_unmount_before_exec",
        "broker_must_close_source_media_fds_before_exec",
        "worker_must_enter_capability_mode",
        "worker_must_limit_fd_rights",
        "worker_must_verify_delegated_fds_are_regular",
        "worker_must_report_input_sha256",
        "worker_must_close_extra_fds",
        "worker_must_verify_extra_fds_closed_before_cap_enter",
        "broker_must_pass_nonmedia_fd5_canary_in_host_smoke",
        "worker_must_report_fd5_canary_observed_before_closefrom",
        "worker_must_close_stdio_fds_before_cap_enter",
        "worker_must_report_failures_to_delegated_output_after_stdio_close",
        "worker_must_report_startup_failures_to_delegated_output",
    ]:
        require(errors, launch.get(key) is True, f"launch_contract.{key} must be true")
    for key in ["argv_must_contain_paths", "env_must_contain_paths", "device_or_mount_path_visible_to_worker"]:
        require(errors, launch.get(key) is False, f"launch_contract.{key} must be false")
    require(errors, launch.get("worker_environment_policy") == "empty-environment", "launch_contract.worker_environment_policy must be empty-environment")
    require(errors, launch.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "launch_contract.worker_cwd_policy must be a private non-media directory")

    expected_binding = bridge.backend_binding_summary()
    require(errors, integration == expected_binding, "backend integration summary must be deterministic")
    require(errors, integration.get("real_apply_python_fixture_worker_allowed") is False, "real apply must disallow the Python fixture worker")
    require(errors, integration.get("real_apply_cli_gate") == bridge.REAL_APPLY_GATE_REASON, "bridge must bind current real-apply gate reason")
    require(errors, integration.get("production_worker_env_policy") == "empty-environment", "backend integration must bind empty production worker environment")
    require(errors, integration.get("production_worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "backend integration must bind private non-media worker cwd")
    require(errors, integration.get("production_stdio_policy") == "close-fd-0-1-2-before-cap-enter", "backend integration must bind production stdio closure policy")
    require(errors, integration.get("worker_failure_report_channel") == "delegated-output-fd-after-stdio-close", "backend integration must bind delegated-output failure reports")
    require(errors, integration.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "backend integration must bind startup delegated-output failure reports")
    require(errors, integration.get("startup_pre_stdio_failure_report_channel") == "delegated-output-fd-before-stdio-close", "backend integration must bind pre-stdio startup delegated-output failure reports")
    require(errors, integration.get("extra_fd_canary") == 5, "backend integration must bind fd-5 inherited-fd canary")
    require(errors, integration.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "backend integration fd-5 canary must be non-media")
    require(errors, integration.get("extra_fd_canary_must_be_observed_before_closefrom") is True, "backend integration must bind fd-5 observation-before-closefrom proof")
    require(errors, integration.get("extra_fds_closed_before_cap_enter") is True, "backend integration must bind extra-fd closure proof")
    require(errors, integration.get("extra_fd_scan_limit") == 64, "backend integration must bind extra-fd scan limit")
    require(errors, integration.get("worker_reports_input_sha256") is True, "backend integration must bind worker input digest proof")
    require(errors, integration.get("launcher_fd_slot_policy") == "duplicate-target-fds-above-delegated-range-before-clearing-slots", "backend integration must bind fd slot save-before-open policy")
    require(errors, integration.get("launcher_restores_parent_fd_slots_after_worker") is True, "backend integration must bind parent fd slot restoration")

    for key in [
        "source_requires_freebsd_capsicum_header",
        "source_has_non_freebsd_error_gate",
        "source_accepts_no_path_arguments",
        "source_closes_fds_above_delegated_set",
        "source_verifies_extra_fds_closed_before_cap_enter",
        "source_observes_fd5_canary_before_closefrom",
        "source_closes_stdio_before_cap_enter",
        "source_limits_input_fd_rights",
        "source_limits_output_fd_rights",
        "source_verifies_delegated_fds_regular",
        "source_enters_capability_mode",
        "source_verifies_delegated_fd_types",
        "cloudtainer_probe_uses_named_shim_not_production_header",
        "cloudtainer_probe_closefrom_actually_closes_canary_fd",
        "cloudtainer_compile_probe_passed",
        "cloudtainer_execution_probe_passed",
        "source_reports_failures_to_delegated_output_after_stdio_close",
        "source_reports_startup_failures_to_delegated_output",
        "source_reports_pre_stdio_failures_without_false_stdio_closed_claim",
        "source_reports_pre_stdio_startup_failures_truthfully",
        "source_has_no_stderr_error_path",
        "cloudtainer_execution_probe_uses_empty_worker_environment",
        "cloudtainer_execution_probe_uses_private_worker_cwd",
        "real_apply_python_fixture_worker_disallowed",
        "real_apply_refuses_until_bridge_ready",
    ]:
        require(errors, invariants.get(key) is True, f"invariant {key} must be true")
    return errors


def check_backend_runner_binding() -> list[str]:
    errors: list[str] = []
    receipt = load_json(ROOT, "spec/examples/removable.media.local.freebsd.backend.run.receipt.json")
    binding = receipt.get("worker_bridge", {}) if isinstance(receipt, dict) else {}
    worker = receipt.get("worker", {}) if isinstance(receipt, dict) else {}
    require(errors, binding == bridge.backend_binding_summary(), "backend runner receipt must carry exact bridge binding summary")
    require(errors, binding.get("production_worker_env_policy") == "empty-environment", "backend runner receipt must bind empty production worker environment")
    require(errors, binding.get("production_worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "backend runner receipt must bind private non-media production worker cwd")
    require(errors, binding.get("worker_failure_report_channel") == "delegated-output-fd-after-stdio-close", "backend runner receipt must bind delegated-output failure reports")
    require(errors, binding.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close", "backend runner receipt must bind startup delegated-output failure reports")
    require(errors, binding.get("startup_pre_stdio_failure_report_channel") == "delegated-output-fd-before-stdio-close", "backend runner receipt must bind pre-stdio startup delegated-output failure reports")
    require(errors, binding.get("extra_fd_canary") == 5, "backend runner receipt must bind fd-5 inherited-fd canary")
    require(errors, binding.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media", "backend runner receipt canary must be non-media")
    require(errors, binding.get("extra_fd_canary_must_be_observed_before_closefrom") is True, "backend runner receipt must bind fd-5 observation-before-closefrom proof")
    require(errors, binding.get("extra_fds_closed_before_cap_enter") is True, "backend runner receipt must bind extra-fd closure proof")
    require(errors, worker.get("launcher_kind") == "python-fd-worker-cloudtainer-fixture-only", "fixture receipt must mark Python worker as fixture-only")
    require(errors, worker.get("real_apply_python_fixture_worker_allowed") is False, "fixture receipt must forbid Python worker for real apply")
    require(errors, worker.get("real_apply_requires_capsicum_worker_bridge") is True, "fixture receipt must require Capsicum bridge for real apply")
    require(errors, worker.get("capsicum_worker_bridge_id") == bridge.BRIDGE_ID, "worker receipt must bind bridge id")

    source = (ROOT / "tools" / "run_removable_media_local_freebsd_backend.py").read_text(encoding="utf-8")
    require(errors, "import removable_media_capsicum_worker_bridge as capsicum_bridge" in source, "backend runner must import bridge module")
    apply_source = inspect.getsource(backend.build_apply_receipt)
    require(errors, "capsicum_bridge.REAL_APPLY_GATE_REASON" in apply_source, "real apply must still refuse on the bridge gate")
    require(errors, '"/usr/sbin/fstyp"' not in apply_source, "build_apply_receipt must not carry unreachable fstyp code behind the bridge refusal")
    require(errors, "fd_worker.run_fd_worker" not in apply_source, "build_apply_receipt must not launch the Python fixture worker on the real apply path")
    bridge_source_text = (ROOT / "tools" / "removable_media_capsicum_worker_bridge.py").read_text(encoding="utf-8")
    require(errors, "pass_fds=(3, 4, 5)" in bridge_source_text, "bridge execution probe must pass fd 5 into the child")
    require(errors, "env={}" in bridge_source_text, "bridge execution probe must clear the child worker environment")
    require(errors, "worker-empty-cwd" in bridge_source_text, "bridge execution probe must use a private worker cwd")
    require(errors, "unreachable" not in apply_source.lower(), "build_apply_receipt should not carry unreachable host-code comments")
    return errors


def check_docs() -> list[str]:
    errors: list[str] = []
    for rel, tokens in DOC_TOKENS.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            require(errors, token in text, f"{rel} missing token {token!r}")
    return errors


def main() -> int:
    observed = load_json(ROOT, EXAMPLE_REL)
    expected = bridge.build_bridge_receipt()
    errors = validate_schema(observed) + semantic_errors(observed)
    if observed != expected:
        errors.append("bridge example is stale; regenerate with tools/removable_media_capsicum_worker_bridge.py --write-example")
    errors.extend(check_backend_runner_binding())
    errors.extend(check_docs())
    if errors:
        print("Capsicum worker bridge check FAILED.")
        for error in errors:
            print("-", error)
        return 1
    (ROOT / VALIDATION_REL).write_text(json.dumps(observed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Capsicum worker bridge check OK")
    print("Bridge: FreeBSD C worker source digest + syntax/execution probes + backend real-apply gate binding + production stdio/error-channel/extra-fd closure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
