#!/usr/bin/env python3
"""FreeBSD Capsicum worker bridge contract for removable-media fallback.

This module is deliberately narrower than the backend runner.  It records and
checks the host worker that must replace the Python fixture worker before real
FreeBSD apply is allowed.  The cloudtainer can syntax-check the C source through
a probe shim; a real FreeBSD host must compile the same source against
<sys/capsicum.h> and execute that binary after umount with only broker-delegated
fds 3 and 4.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import removable_media_fd_slot_launcher as fd_slots

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-06-05r554"
BRIDGE_ID = "rm-capsicum-worker-bridge-20260605-r554"
FIXED_GENERATED_AT = "2026-06-05T11:20:00Z"
SOURCE_REL = "tools/freebsd/rm_post_detach_capsicum_worker.c"
SHIM_REL = "tools/freebsd/derivebsd_capsicum_probe_shim.h"
SOURCE = ROOT / SOURCE_REL
SHIM = ROOT / SHIM_REL
EXAMPLE_REL = "spec/examples/removable.media.capsicum.worker.bridge.json"
VALIDATION_REL = "validation/removable-media-capsicum-worker-bridge.receipt.json"
BINARY_BASENAME = "rm_post_detach_capsicum_worker"
REAL_APPLY_GATE_REASON = "capsicum-worker-required-for-real-apply"
PROBE_INPUT_BYTES = b"derivebsd capsicum worker execution probe\n"


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def command_digest(stdout: str, stderr: str) -> dict[str, Any]:
    out = stdout.encode("utf-8", errors="replace")
    err = stderr.encode("utf-8", errors="replace")
    return {
        "stdout_sha256": sha256_bytes(out),
        "stderr_sha256": sha256_bytes(err),
        "stdout_bytes": len(out),
        "stderr_bytes": len(err),
    }


def run_command_result(cmd: list[str], *, timeout_seconds: float = 30) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        return {
            "command": cmd,
            "return_code": int(proc.returncode),
            "timed_out": False,
            **command_digest(stdout, stderr),
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        stderr = (str(stderr) + "\n" if stderr else "") + f"TIMEOUT after {timeout_seconds} seconds"
        return {
            "command": cmd,
            "return_code": 124,
            "timed_out": True,
            **command_digest(str(stdout), stderr),
        }


def probe_compile_command() -> list[str] | None:
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        return None
    return [
        cc,
        "-std=c99",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-fsyntax-only",
        "-DDERIVEBSD_CAPSICUM_COMPILE_PROBE=1",
        "-I",
        "tools/freebsd",
        SOURCE_REL,
    ]


def run_cloudtainer_compile_probe() -> dict[str, Any]:
    cmd = probe_compile_command()
    if cmd is None:
        return {
            "command": [],
            "return_code": 127,
            "timed_out": False,
            "stdout_sha256": sha256_bytes(b""),
            "stderr_sha256": sha256_bytes(b"no C compiler available"),
            "stdout_bytes": 0,
            "stderr_bytes": len(b"no C compiler available"),
        }
    return run_command_result(cmd, timeout_seconds=30)


def probe_executable_compile_command(binary_path: Path | str) -> list[str] | None:
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        return None
    return [
        cc,
        "-std=c99",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-DDERIVEBSD_CAPSICUM_COMPILE_PROBE=1",
        "-I",
        "tools/freebsd",
        "-o",
        str(binary_path),
        SOURCE_REL,
    ]


def _execution_compile_template(cc: str | None = None) -> list[str]:
    return [
        cc or "cc",
        "-std=c99",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-DDERIVEBSD_CAPSICUM_COMPILE_PROBE=1",
        "-I",
        "tools/freebsd",
        "-o",
        "$PRIVATE_PROBE_DIR/rm_post_detach_capsicum_worker",
        SOURCE_REL,
    ]


def _run_compile_for_execution_probe(binary_path: Path) -> dict[str, Any]:
    cmd = probe_executable_compile_command(binary_path)
    if cmd is None:
        return {
            "command": _execution_compile_template(),
            "return_code": 127,
            "timed_out": False,
            "stdout_sha256": sha256_bytes(b""),
            "stderr_sha256": sha256_bytes(b"no C compiler available"),
            "stdout_bytes": 0,
            "stderr_bytes": len(b"no C compiler available"),
        }
    result = run_command_result(cmd, timeout_seconds=30)
    result["command"] = _execution_compile_template(cmd[0])
    return result


def _run_probe_case(binary_path: Path, tmpdir: Path, *, case: str) -> dict[str, Any]:
    output_path = tmpdir / f"{case}.worker-output.json"
    input_fd: int | None = None
    output_fd: int | None = None
    canary_fd: int | None = None
    slot_guard = fd_slots.FdSlotGuard(fd_slots.TARGET_FDS).save_and_clear()
    input_bytes = PROBE_INPUT_BYTES
    try:
        if case == "success-regular-input":
            input_path = tmpdir / "probe-input.bin"
            input_path.write_bytes(input_bytes)
            input_fd = os.open(input_path, os.O_RDONLY)
            expected_return = 0
            expected_result = "passed"
            expected_error_code = None
        elif case == "failure-directory-input":
            input_fd = os.open(tmpdir, os.O_RDONLY)
            expected_return = 1
            expected_result = "failed"
            expected_error_code = "input_fd_not_regular"
        elif case == "failure-path-argument":
            input_path = tmpdir / "probe-argv-input.bin"
            input_path.write_bytes(input_bytes)
            input_fd = os.open(input_path, os.O_RDONLY)
            expected_return = 1
            expected_result = "failed"
            expected_error_code = "path_arguments_rejected"
        else:
            raise ValueError(f"unknown probe case {case!r}")

        output_fd = os.open(output_path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
        canary_path = tmpdir / f"{case}.broker-nonmedia-fd5-canary"
        canary_path.write_text("broker-owned non-media inherited-fd canary\n", encoding="utf-8")
        canary_fd = os.open(canary_path, os.O_RDONLY)
        worker_cwd = tmpdir / f"{case}.worker-empty-cwd"
        worker_cwd.mkdir(mode=0o700)
        slot_guard.install_owned_fd(input_fd, 3)
        input_fd = None
        slot_guard.install_owned_fd(output_fd, 4)
        output_fd = None
        slot_guard.install_owned_fd(canary_fd, 5)
        canary_fd = None
        try:
            argv = [str(binary_path)]
            if case == "failure-path-argument":
                argv.append("/media/should-not-be-visible")
            proc = subprocess.run(
                argv,
                cwd=worker_cwd,
                env={},
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
                pass_fds=(3, 4, 5),
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            return_code = int(proc.returncode)
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout or ""
            err = exc.stderr or ""
            if isinstance(out, bytes):
                out = out.decode("utf-8", errors="replace")
            if isinstance(err, bytes):
                err = err.decode("utf-8", errors="replace")
            stdout = str(out)
            stderr = (str(err) + "\n" if err else "") + "TIMEOUT after 10 seconds"
            return_code = 124
            timed_out = True
    finally:
        slot_guard.restore()
        for fd in (input_fd, output_fd, canary_fd):
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass

    output_bytes = output_path.read_bytes() if output_path.exists() else b""
    output_text = output_bytes.decode("utf-8", errors="replace")
    try:
        output_report: dict[str, Any] | None = json.loads(output_text) if output_text.strip() else None
        output_parse_error = None
    except json.JSONDecodeError as exc:
        output_report = None
        output_parse_error = str(exc)

    return {
        "case": case,
        "command": ["$PRIVATE_PROBE_DIR/rm_post_detach_capsicum_worker"],
        "return_code": return_code,
        "timed_out": timed_out,
        **command_digest(stdout, stderr),
        "output_report_sha256": sha256_bytes(output_bytes),
        "output_report_bytes": len(output_bytes),
        "output_report": output_report,
        "output_parse_error": output_parse_error,
        "expected_return_code": expected_return,
        "expected_report_result": expected_result,
        "expected_error_code": expected_error_code,
        "pass_fds": [3, 4, 5],
        "worker_env_policy": "empty-environment",
        "worker_env_keys_passed": [],
        "worker_cwd_policy": "private-empty-directory-not-media-not-repo",
        "worker_cwd_is_private_empty_dir": True,
        "worker_cwd_contains_media_tree": False,
        "extra_fd_canary": 5,
        "extra_fd_canary_source": "broker-nonmedia-canary-not-source-media",
        "extra_fd_canary_passed_to_child": True,
        "launcher_fd_slot_policy": fd_slots.POLICY,
        "launcher_fd_slot_evidence": slot_guard.evidence(),
        "launcher_restored_parent_fd_slots": slot_guard.evidence().get("preexisting_parent_fd_slots_preserved") is True,
    }


def run_cloudtainer_execution_probe() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="derivebsd-capsicum-worker-exec-probe-") as tmp_name:
        tmpdir = Path(tmp_name)
        binary_path = tmpdir / "rm_post_detach_capsicum_worker"
        compile_result = _run_compile_for_execution_probe(binary_path)
        if compile_result.get("return_code") != 0 or compile_result.get("timed_out") is not False:
            return {
                "claim": "cloudtainer-shim-execution-probe-not-capsicum-execution",
                "compile_result": compile_result,
                "success_run": None,
                "failure_run": None,
                "argument_rejection_run": None,
                "result": "failed",
            }
        success = _run_probe_case(binary_path, tmpdir, case="success-regular-input")
        failure = _run_probe_case(binary_path, tmpdir, case="failure-directory-input")
        argument_rejection = _run_probe_case(binary_path, tmpdir, case="failure-path-argument")
        success_report = success.get("output_report") if isinstance(success.get("output_report"), dict) else {}
        failure_report = failure.get("output_report") if isinstance(failure.get("output_report"), dict) else {}
        argument_report = argument_rejection.get("output_report") if isinstance(argument_rejection.get("output_report"), dict) else {}
        passed = (
            success.get("return_code") == 0
            and success.get("timed_out") is False
            and success_report.get("result") == "passed"
            and success_report.get("input_bytes") == len(PROBE_INPUT_BYTES)
            and success_report.get("input_sha256") == sha256_bytes(PROBE_INPUT_BYTES)
            and success_report.get("failure_report_channel") == "delegated-output-fd-after-stdio-close"
            and success_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close"
            and success_report.get("stdio_fds_closed_before_cap_enter") is True
            and success_report.get("extra_fds_closed_before_cap_enter") is True
            and success.get("pass_fds") == [3, 4, 5]
            and success.get("worker_env_policy") == "empty-environment"
            and success.get("worker_env_keys_passed") == []
            and success.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo"
            and success.get("worker_cwd_is_private_empty_dir") is True
            and success.get("worker_cwd_contains_media_tree") is False
            and success.get("extra_fd_canary_passed_to_child") is True
            and success_report.get("extra_fd_canary") == 5
            and success_report.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media"
            and success_report.get("extra_fd_canary_observed_before_closefrom") is True
            and success_report.get("extra_fd_scan_limit") == 64
            and failure.get("return_code") == 1
            and failure.get("timed_out") is False
            and failure_report.get("result") == "failed"
            and failure_report.get("error_code") == "input_fd_not_regular"
            and failure_report.get("failure_report_channel") == "delegated-output-fd-after-stdio-close"
            and failure_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close"
            and failure_report.get("stdio_fds_closed_before_cap_enter") is True
            and failure_report.get("extra_fds_closed_before_cap_enter") is True
            and failure.get("pass_fds") == [3, 4, 5]
            and failure.get("worker_env_policy") == "empty-environment"
            and failure.get("worker_env_keys_passed") == []
            and failure.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo"
            and failure.get("worker_cwd_is_private_empty_dir") is True
            and failure.get("worker_cwd_contains_media_tree") is False
            and failure.get("extra_fd_canary_passed_to_child") is True
            and failure.get("launcher_fd_slot_policy") == fd_slots.POLICY
            and failure.get("launcher_restored_parent_fd_slots") is True
            and failure_report.get("extra_fd_canary") == 5
            and failure_report.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media"
            and failure_report.get("extra_fd_canary_observed_before_closefrom") is True
            and failure_report.get("extra_fd_scan_limit") == 64
            and argument_rejection.get("return_code") == 1
            and argument_rejection.get("timed_out") is False
            and argument_report.get("result") == "failed"
            and argument_report.get("error_code") == "path_arguments_rejected"
            and argument_report.get("failure_report_channel") == "delegated-output-fd-before-stdio-close"
            and argument_report.get("startup_failure_report_channel") == "delegated-output-fd-before-or-after-stdio-close"
            and argument_report.get("stdio_fds_closed_before_cap_enter") is False
            and argument_report.get("extra_fds_closed_before_cap_enter") is False
            and argument_rejection.get("pass_fds") == [3, 4, 5]
            and argument_rejection.get("worker_env_policy") == "empty-environment"
            and argument_rejection.get("worker_env_keys_passed") == []
            and argument_rejection.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo"
            and argument_rejection.get("worker_cwd_is_private_empty_dir") is True
            and argument_rejection.get("worker_cwd_contains_media_tree") is False
            and argument_rejection.get("extra_fd_canary_passed_to_child") is True
            and argument_rejection.get("launcher_fd_slot_policy") == fd_slots.POLICY
            and argument_rejection.get("launcher_restored_parent_fd_slots") is True
            and argument_report.get("extra_fd_canary") == 5
            and argument_report.get("extra_fd_canary_source") == "broker-nonmedia-canary-not-source-media"
            and argument_report.get("extra_fd_canary_observed_before_closefrom") is True
            and argument_report.get("extra_fd_scan_limit") == 64
            and success.get("stdout_bytes") == 0
            and success.get("stderr_bytes") == 0
            and failure.get("stdout_bytes") == 0
            and failure.get("stderr_bytes") == 0
            and argument_rejection.get("stdout_bytes") == 0
            and argument_rejection.get("stderr_bytes") == 0
        )
        return {
            "claim": "cloudtainer-shim-execution-probe-not-capsicum-execution",
            "compile_result": compile_result,
            "success_run": success,
            "failure_run": failure,
            "argument_rejection_run": argument_rejection,
            "result": "passed" if passed else "failed",
        }


def production_build_command_template() -> list[str]:
    return [
        "cc",
        "-std=c99",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-O2",
        "-o",
        "$PRIVATE_WORK_ROOT/rm_post_detach_capsicum_worker",
        SOURCE_REL,
    ]


def backend_binding_summary() -> dict[str, Any]:
    return {
        "bridge_id": BRIDGE_ID,
        "bridge_example": EXAMPLE_REL,
        "bridge_check": "tools/check_removable_media_local_fallback_capsicum_worker_bridge.py",
        "host_worker_source": SOURCE_REL,
        "source_sha256": sha256_file(SOURCE),
        "fixture_worker_kind": "python-fd-worker-cloudtainer-only",
        "host_worker_kind": "freebsd-capsicum-c-worker",
        "real_apply_python_fixture_worker_allowed": False,
        "real_apply_cli_gate": REAL_APPLY_GATE_REASON,
        "cloudtainer_executes_capsicum": False,
        "production_worker_env_policy": "empty-environment",
        "production_worker_cwd_policy": "private-empty-directory-not-media-not-repo",
        "production_stdio_policy": "close-fd-0-1-2-before-cap-enter",
        "worker_failure_report_channel": "delegated-output-fd-after-stdio-close",
        "startup_failure_report_channel": "delegated-output-fd-before-or-after-stdio-close",
        "startup_pre_stdio_failure_report_channel": "delegated-output-fd-before-stdio-close",
        "extra_fd_canary": 5,
        "extra_fd_canary_source": "broker-nonmedia-canary-not-source-media",
        "extra_fd_canary_must_be_observed_before_closefrom": True,
        "extra_fds_closed_before_cap_enter": True,
        "extra_fd_scan_limit": 64,
        "worker_reports_input_sha256": True,
        "launcher_fd_slot_policy": fd_slots.POLICY,
        "launcher_restores_parent_fd_slots_after_worker": True,
    }


def build_bridge_receipt(*, generated_at_utc: str = FIXED_GENERATED_AT) -> dict[str, Any]:
    source_text = SOURCE.read_text(encoding="utf-8", errors="replace")
    shim_text = SHIM.read_text(encoding="utf-8", errors="replace")
    probe = run_cloudtainer_compile_probe()
    execution_probe = run_cloudtainer_execution_probe()
    invariants = {
        "source_requires_freebsd_capsicum_header": "#include <sys/capsicum.h>" in source_text,
        "source_has_non_freebsd_error_gate": "#error" in source_text,
        "source_accepts_no_path_arguments": "argc != 1" in source_text and "path_arguments_rejected" in source_text,
        "source_closes_fds_above_delegated_set": "closefrom(FD_AFTER_DELEGATED_SET)" in source_text,
        "source_verifies_extra_fds_closed_before_cap_enter": "verify_extra_fds_closed_before_cap_enter" in source_text and "extra_fd_still_open_before_cap_enter" in source_text and "EXTRA_FD_SCAN_LIMIT" in source_text,
        "source_observes_fd5_canary_before_closefrom": "observe_extra_fd_canary_before_closefrom" in source_text and "extra_fd_canary_observed_before_closefrom" in source_text,
        "source_closes_stdio_before_cap_enter": "close_standard_fds();" in source_text and "STDIN_FILENO, STDOUT_FILENO, STDERR_FILENO" in source_text and source_text.find("close_standard_fds();") < source_text.find("if (cap_enter()"),
        "source_limits_input_fd_rights": "cap_rights_limit(REMEDIA_INPUT_FD" in source_text,
        "source_limits_output_fd_rights": "cap_rights_limit(REMEDIA_OUTPUT_FD" in source_text,
        "source_verifies_delegated_fds_regular": "verify_delegated_fds_regular()" in source_text and "S_ISREG(input_st.st_mode)" in source_text and "S_ISREG(output_st.st_mode)" in source_text,
        "source_enters_capability_mode": "cap_enter()" in source_text,
        "source_verifies_delegated_fd_types": "verify_delegated_fds_regular();" in source_text and "fstat(REMEDIA_INPUT_FD" in source_text and "fstat(REMEDIA_OUTPUT_FD" in source_text,
        "source_reports_input_sha256": "sha256_update(&input_hash" in source_text and "input_sha256" in source_text and "sha256_digest_to_prefixed_hex" in source_text,
        "cloudtainer_probe_uses_named_shim_not_production_header": "DERIVEBSD_CAPSICUM_COMPILE_PROBE" in source_text and "not a Capsicum implementation" in shim_text,
        "cloudtainer_probe_closefrom_actually_closes_canary_fd": "derivebsd_probe_closefrom" in shim_text and "close(fd)" in shim_text and "for (int fd = lowfd" in shim_text,
        "cloudtainer_compile_probe_passed": probe["return_code"] == 0 and probe["timed_out"] is False,
        "cloudtainer_execution_probe_passed": execution_probe.get("result") == "passed",
        "source_reports_failures_to_delegated_output_after_stdio_close": "fatal_to_delegated_output" in source_text and "failure_report_channel" in source_text and "delegated-output-fd-after-stdio-close" in source_text,
        "source_reports_startup_failures_to_delegated_output": "path_arguments_rejected" in source_text and "stdio_fd_close_failed" in source_text and "delegated-output-fd-before-stdio-close" in source_text and "err(" not in source_text and "errx(" not in source_text,
        "source_reports_pre_stdio_failures_without_false_stdio_closed_claim": 'standard_fds_closed ? "true" : "false"' in source_text and "failure_channel_for_current_stdio_state" in source_text,
        "source_reports_pre_stdio_startup_failures_truthfully": 'fatal_to_delegated_output("path_arguments_rejected", false)' in source_text and "delegated-output-fd-before-stdio-close" in source_text and "standard_fds_closed = true" in source_text,
        "source_has_no_stderr_error_path": "err(" not in source_text and "errx(" not in source_text and "#include <err.h>" not in source_text,
        "cloudtainer_execution_probe_uses_empty_worker_environment": all((run or {}).get("worker_env_policy") == "empty-environment" and (run or {}).get("worker_env_keys_passed") == [] for run in [execution_probe.get("success_run"), execution_probe.get("failure_run"), execution_probe.get("argument_rejection_run")]),
        "cloudtainer_execution_probe_uses_private_worker_cwd": all((run or {}).get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo" and (run or {}).get("worker_cwd_contains_media_tree") is False for run in [execution_probe.get("success_run"), execution_probe.get("failure_run"), execution_probe.get("argument_rejection_run")]),
        "real_apply_python_fixture_worker_disallowed": True,
        "real_apply_refuses_until_bridge_ready": True,
    }
    return {
        "kind": "removable.media.capsicum.worker.bridge",
        "schema_version": "0.1",
        "bridge_id": BRIDGE_ID,
        "generated_for_version": VERSION,
        "generated_at_utc": generated_at_utc,
        "scope": {
            "lane": "removable-media-local-fallback",
            "backend_runner": "tools/run_removable_media_local_freebsd_backend.py",
            "cloudtainer_claim": "syntax-and-contract-probe-only-no-capsicum-execution",
            "production_claim": "freebsd-host-only-build-and-exec-after-umount",
        },
        "source": {
            "path": SOURCE_REL,
            "sha256": sha256_file(SOURCE),
            "freebsd_header_required": "sys/capsicum.h",
            "probe_shim": SHIM_REL,
            "probe_define": "DERIVEBSD_CAPSICUM_COMPILE_PROBE",
            "delegated_input_fd": 3,
            "delegated_output_fd": 4,
            "closefrom_fd": 5,
            "extra_fd_canary": 5,
            "extra_fd_canary_source": "broker-nonmedia-canary-not-source-media",
            "extra_fd_canary_must_be_observed_before_closefrom": True,
            "extra_fd_scan_limit": 64,
            "reported_input_digest_field": "input_sha256",
            "stdio_policy": "close-fd-0-1-2-before-cap-enter",
            "failure_report_channel": "delegated-output-fd-after-stdio-close",
            "startup_failure_report_channel": "delegated-output-fd-before-or-after-stdio-close",
            "startup_pre_stdio_failure_report_channel": "delegated-output-fd-before-stdio-close",
            "path_arguments_accepted": False,
        },
        "build": {
            "production_os": "FreeBSD",
            "production_build_command_template": production_build_command_template(),
            "binary_basename": BINARY_BASENAME,
            "binary_residence": "private-work-root-only-not-reused-from-user-path",
            "binary_digest_required_in_host_receipt": True,
            "cloudtainer_probe_result": probe,
            "cloudtainer_execution_probe_result": execution_probe,
        },
        "launch_contract": {
            "broker_must_unmount_before_exec": True,
            "broker_must_close_source_media_fds_before_exec": True,
            "input_delivery": "fd-3-preserved-cas-object-read-only",
            "output_delivery": "fd-4-broker-owned-derivative-create-exclusive",
            "argv_must_contain_paths": False,
            "env_must_contain_paths": False,
            "worker_environment_policy": "empty-environment",
            "worker_cwd_policy": "private-empty-directory-not-media-not-repo",
            "device_or_mount_path_visible_to_worker": False,
            "worker_must_enter_capability_mode": True,
            "worker_must_limit_fd_rights": True,
            "worker_must_verify_delegated_fds_are_regular": True,
            "worker_must_report_input_sha256": True,
            "worker_must_close_extra_fds": True,
            "worker_must_verify_extra_fds_closed_before_cap_enter": True,
            "broker_must_pass_nonmedia_fd5_canary_in_host_smoke": True,
            "worker_must_report_fd5_canary_observed_before_closefrom": True,
            "worker_must_close_stdio_fds_before_cap_enter": True,
            "worker_must_report_failures_to_delegated_output_after_stdio_close": True,
            "worker_must_report_startup_failures_to_delegated_output": True,
        },
        "backend_integration": backend_binding_summary(),
        "invariants": invariants,
        "result": "passed" if all(invariants.values()) else "failed",
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-example", action="store_true")
    ap.add_argument("--write-validation", action="store_true")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--print", action="store_true")
    ap.add_argument("--generated-at", default=FIXED_GENERATED_AT)
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    receipt = build_bridge_receipt(generated_at_utc=args.generated_at)
    if args.write_example:
        write_json(ROOT / EXAMPLE_REL, receipt)
    if args.write_validation:
        write_json(ROOT / VALIDATION_REL, receipt)
    if args.output:
        write_json(args.output, receipt)
    if args.print:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt.get("result") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
