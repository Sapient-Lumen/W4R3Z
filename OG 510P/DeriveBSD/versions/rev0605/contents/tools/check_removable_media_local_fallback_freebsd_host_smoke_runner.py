#!/usr/bin/env python3
"""Validate the FreeBSD-only removable-media host smoke runner.

This guard keeps the next real host proof concrete while preventing the Linux
cloudtainer from overclaiming it: the runner must refuse outside FreeBSD, and
checker-only success/failure simulations must exercise the host-smoke command
order, cleanup, worker digest, and inherited-fd proofs without claiming real
FreeBSD execution.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from cube_digest_lib import load_json as load_json_strict, write_pretty_json
from freebsd import host_proof_contract as contract

ROOT = Path(__file__).resolve().parents[1]
RUNNER_REL = "tools/freebsd/run_removable_media_local_fallback_host_smoke.py"
VALIDATOR_REL = "tools/freebsd/validate_removable_media_local_fallback_host_smoke_receipt.py"
COLLECTOR_REL = "tools/freebsd/collect_removable_media_local_fallback_host_proof.sh"
RUNNER = ROOT / RUNNER_REL
VALIDATION_REL = "validation/removable-media-local-freebsd-host-smoke.refusal.json"
FAILURE_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.failure-simulation.json"
FSTYP_OUTPUT_FAILURE_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.fstyp-output-failure-simulation.json"
SUCCESS_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.success-simulation.json"
FIXTURE_ADMISSION_FAILURE_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.fixture-admission-failure-simulation.json"
FIXTURE_COPY_CHANGE_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.fixture-copy-change-simulation.json"
WORKER_SOURCE_COPY_CHANGE_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.worker-source-copy-change-simulation.json"
FIXTURE_COPY_DIRECTORY_CHANGE_SIM_REL = "validation/removable-media-local-freebsd-host-smoke.fixture-copy-directory-change-simulation.json"
DOC_REL = "docs/current/removable-media-freebsd-host-smoke.md"
HOST_SMOKE_SCHEMA_REL = "spec/removable.media.local.freebsd.host.smoke.receipt.schema.json"
HOST_SMOKE_EXAMPLE_REL = "spec/examples/removable.media.local.freebsd.host.smoke.receipt.json"
VERSION = "2026-06-05r554"
RUNNER_CONTRACT_VERSION = VERSION
CURRENT_CUBE_CUT_VERSION = contract.CURRENT_CUBE_CUT_VERSION
VALID_VISIBLE_FIXTURE_REL = "fixtures/removable-media/local-fallback/exfat-card/invoice.pdf"
VALID_VISIBLE_FIXTURE_SHA256 = "sha256:01a0cd0826db2a58f930defd65189517c567703c224d715abefeb66897a5e2cc"
VALID_VISIBLE_FIXTURE_SIZE = 685
MIN_FREEBSD_OSRELDATE = contract.MIN_FREEBSD_OSRELDATE
SUPPORTED_FREEBSD_RELEASE_FLOOR = contract.SUPPORTED_FREEBSD_RELEASE_FLOOR
HOST_RELEASE_FLOOR_POLICY = contract.HOST_RELEASE_FLOOR_POLICY
PRIMARY_FREEBSD_RELEASE = contract.PRIMARY_FREEBSD_RELEASE
PRIMARY_FREEBSD_OSRELDATE_MINIMUM = contract.PRIMARY_FREEBSD_OSRELDATE_MINIMUM
PRIMARY_FREEBSD_RELEASE_CHANNEL = contract.PRIMARY_FREEBSD_RELEASE_CHANNEL
HOST_TARGET_MATRIX_ID = contract.HOST_TARGET_MATRIX_ID
HOST_TARGET_TIER_POLICY = contract.HOST_TARGET_TIER_POLICY
HOST_TARGET_PRIMARY_TIER = contract.HOST_TARGET_PRIMARY_TIER
HOST_TARGET_LEGACY_TIER = contract.HOST_TARGET_LEGACY_TIER
SMOKE_ID = "rm-local-freebsd-host-smoke-20260605-r554"
BRIDGE_ID = "rm-capsicum-worker-bridge-20260605-r554"
EXPECTED_HOST_PROBE_ROLES = [
    "host-probe-uname-system",
    "host-probe-uname-release",
    "host-probe-uname-machine",
    "host-probe-effective-uid",
    "host-probe-osreldate",
    "host-probe-capsicum-capability-mode",
    "host-probe-capsicum-capabilities",
]
EXPECTED_HOST_PROBE_VALUES = {
    ("/bin/uname", "-s"): "FreeBSD\n",
    ("/bin/uname", "-r"): "15.1-RELEASE-p0\n",
    ("/bin/uname", "-m"): "amd64\n",
    ("/usr/bin/id", "-u"): "0\n",
    ("/sbin/sysctl", "-n", "kern.osreldate"): "1501500\n",
    ("/sbin/sysctl", "-n", "kern.features.security_capability_mode"): "1\n",
    ("/sbin/sysctl", "-n", "kern.features.security_capabilities"): "1\n",
}

EXPECTED_HOST_PROBE_VALUE_KEYS = {
    "host-probe-uname-system": "host_probe_observed_system",
    "host-probe-uname-release": "host_probe_uname_release",
    "host-probe-uname-machine": "host_probe_uname_machine",
    "host-probe-effective-uid": "host_probe_effective_uid",
    "host-probe-osreldate": "host_probe_osreldate",
    "host-probe-capsicum-capability-mode": "host_probe_capsicum_capability_mode",
    "host-probe-capsicum-capabilities": "host_probe_capsicum_capabilities",
}


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def load_json(rel: str) -> dict[str, Any]:
    obj = load_json_strict(ROOT, rel)
    return obj if isinstance(obj, dict) else {}


def run_refusal() -> tuple[int, dict[str, Any]]:
    proc = subprocess.run(
        [sys.executable, "-B", RUNNER_REL, "--output", VALIDATION_REL],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return int(proc.returncode), load_json(VALIDATION_REL)


def load_runner_module() -> Any:
    spec = importlib.util.spec_from_file_location("derivebsd_host_smoke_runner_under_test", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load host smoke runner module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fake_command_result(runner: Any, cmd: list[str], rc: int = 0, stdout: str = "", stderr: str = "") -> dict[str, Any]:
    return {
        "command": cmd,
        "return_code": rc,
        "timed_out": False,
        **runner.command_digest(stdout, stderr),
    }


def require_sanitized_host_command_rows(errors: list[str], obj: dict[str, Any], label: str) -> None:
    runner = load_runner_module()
    expected_keys = sorted(runner.HOST_COMMAND_ENV)
    rows: list[dict[str, Any]] = []
    host_probes = obj.get("host_probes", [])
    if isinstance(host_probes, list):
        rows.extend(row for row in host_probes if isinstance(row, dict))
    commands = obj.get("commands", [])
    if isinstance(commands, list):
        rows.extend(row for row in commands if isinstance(row, dict))
    cleanup = obj.get("cleanup", {}) if isinstance(obj.get("cleanup"), dict) else {}
    cleanup_commands = cleanup.get("commands", [])
    if isinstance(cleanup_commands, list):
        rows.extend(row for row in cleanup_commands if isinstance(row, dict))
    for idx, row in enumerate(rows):
        require(errors, row.get("host_command_env_policy") == runner.HOST_COMMAND_ENV_POLICY, f"{label} command row {idx} must bind sanitized host-command environment policy")
        require(errors, row.get("host_command_env_keys") == expected_keys, f"{label} command row {idx} must bind sanitized host-command environment keys")
        require(errors, row.get("host_command_env_lc_all") == "C", f"{label} command row {idx} must bind LC_ALL=C")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def copy_tree_contents(src: Path, dst: Path) -> None:
    for child in src.iterdir():
        target = dst / child.name
        if child.is_dir() and not child.is_symlink():
            shutil.copytree(child, target, symlinks=True, dirs_exist_ok=True)
        elif child.is_symlink():
            if target.exists() or target.is_symlink():
                target.unlink()
            target.symlink_to(os.readlink(child))
        else:
            shutil.copy2(child, target)


def fake_host_probe_stdout(cmd: list[str]) -> str | None:
    """Return deterministic checker-only FreeBSD host-probe output."""
    return EXPECTED_HOST_PROBE_VALUES.get(tuple(cmd))


def require_complete_host_probes(errors: list[str], obj: dict[str, Any], label: str) -> None:
    host_probes = obj.get("host_probes", []) if isinstance(obj.get("host_probes"), list) else []
    probe_roles = [row.get("command_role") for row in host_probes if isinstance(row, dict)]
    require(errors, probe_roles == EXPECTED_HOST_PROBE_ROLES, f"{label} must collect host probes before media commands")
    for idx, row in enumerate(host_probes):
        if not isinstance(row, dict):
            continue
        role = row.get("command_role")
        expected_key = EXPECTED_HOST_PROBE_VALUE_KEYS.get(role) if isinstance(role, str) else None
        expected_stdout = fake_host_probe_stdout(row.get("command", [])) if isinstance(row.get("command"), list) else None
        require(errors, row.get("return_code") == 0, f"{label} host probe {idx} must return zero")
        require(errors, isinstance(row.get("command_shape_sha256"), str) and row.get("command_shape_sha256", "").startswith("sha256:"), f"{label} host probe {idx} must carry command_shape_sha256")
        require(errors, row.get("private_work_root_redacted") is True, f"{label} host probe {idx} must report private work-root redaction")
        require(errors, row.get("observed_value_key") == expected_key, f"{label} host probe {idx} must bind observed_value_key")
        require(errors, isinstance(row.get("observed_stdout_text"), str), f"{label} host probe {idx} must carry observed_stdout_text")
        require(errors, row.get("observed_stdout_text") == expected_stdout, f"{label} host probe {idx} must carry replayable stdout text")
        if isinstance(row.get("observed_stdout_text"), str):
            require(errors, row.get("observed_value") == row.get("observed_stdout_text", "").strip(), f"{label} host probe {idx} observed_value must equal stripped stdout")
        if expected_key is not None:
            host = obj.get("host", {}) if isinstance(obj.get("host"), dict) else {}
            require(errors, host.get(expected_key) == row.get("observed_value"), f"{label} host probe {idx} must match host.{expected_key}")
    commands = obj.get("commands", []) if isinstance(obj.get("commands"), list) else []
    if commands:
        observed_roles = [row.get("command_role") for row in host_probes + commands if isinstance(row, dict)]
        require(errors, observed_roles[:len(EXPECTED_HOST_PROBE_ROLES)] == EXPECTED_HOST_PROBE_ROLES, f"{label} must record host probes before media/compile commands")
    host = obj.get("host", {}) if isinstance(obj.get("host"), dict) else {}
    expected_host = {
        "host_probe_observed_system": "FreeBSD",
        "host_probe_uname_release": "15.1-RELEASE-p0",
        "host_probe_uname_machine": "amd64",
        "host_probe_effective_uid": "0",
        "host_probe_osreldate": "1501500",
        "host_probe_capsicum_capability_mode": "1",
        "host_probe_capsicum_capabilities": "1",
    }
    for key, value in expected_host.items():
        require(errors, host.get(key) == value, f"{label} host.{key} must carry checker FreeBSD probe value")
    require(errors, host.get("host_target_tier") == HOST_TARGET_PRIMARY_TIER, f"{label} must label the checker host as the primary production target tier")


def run_success_simulation() -> dict[str, Any]:
    """Exercise the whole host-smoke success path without claiming FreeBSD host proof."""
    runner = load_runner_module()
    calls: list[list[str]] = []

    def fake_worker_runner(binary: Path, preserved_object: Path, output_path: Path, canary_path: Path, worker_cwd: Path) -> dict[str, Any]:
        del binary
        if not canary_path.exists():
            raise RuntimeError("missing fd5 canary path")
        worker_cwd.mkdir(mode=0o700, exist_ok=False)
        digest = sha256_file(preserved_object)
        size = preserved_object.stat().st_size
        report = {
            "kind": "removable.media.local.freebsd.capsicum.worker.report",
            "result": "passed",
            "capsicum_mode": "entered",
            "capsicum_mode_entered": True,
            "input_fd": 3,
            "output_fd": 4,
            "input_bytes": size,
            "input_sha256": digest,
            "input_fd_regular": True,
            "output_fd_regular": True,
            "delegated_fds_regular": True,
            "stdio_fds_closed_before_cap_enter": True,
            "stdio_fds_closed_before_report": True,
            "extra_fds_closed_before_cap_enter": True,
            "extra_fd_scan_limit": 64,
            "extra_fd_canary": 5,
            "extra_fd_canary_source": "broker-nonmedia-canary-not-source-media",
            "extra_fd_canary_observed_before_closefrom": True,
            "failure_report_channel": "delegated-output-fd-after-stdio-close",
            "startup_failure_report_channel": "delegated-output-fd-before-or-after-stdio-close",
            "path_arguments_accepted": False,
            "checker_only_worker_simulation": True,
        }
        output_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        text = output_path.read_text(encoding="utf-8")
        return {
            "command": ["$PRIVATE_WORK_ROOT/" + runner.WORKER_BINARY_NAME],
            "return_code": 0,
            "timed_out": False,
            **runner.command_digest("", ""),
            "output_report_sha256": runner.sha256_bytes(text.encode("utf-8")),
            "output_report_bytes": len(text.encode("utf-8")),
            "output_report": report,
            "output_parse_error": None,
            "extra_fd_canary": 5,
            "extra_fd_canary_source": "broker-nonmedia-canary-not-source-media",
            "worker_env_policy": "empty-environment",
            "worker_env_keys_passed": [],
            "worker_cwd_policy": "private-empty-directory-not-media-not-repo",
            "worker_cwd_is_private_empty_dir": True,
            "worker_cwd_contains_media_tree": False,
            "launcher_fd_slot_policy": "duplicate-target-fds-above-delegated-range-before-clearing-slots",
            "launcher_fd_slot_evidence": {
                "policy": "duplicate-target-fds-above-delegated-range-before-clearing-slots",
                "target_fds": [3, 4, 5],
                "saved_duplicates_outside_target_fds": True,
                "saved_and_cleared_before_opening_delegated_files": True,
                "restored_after_worker": True,
                "preexisting_parent_fd_slots_preserved": True,
                "preexisting_parent_fd_inheritable_flags_preserved": True,
                "checker_only_worker_simulation": True,
            },
            "launcher_restored_parent_fd_slots": True,
            "launcher_preserved_parent_fd_inheritable_flags": True,
            "checker_only_worker_simulation": True,
        }

    with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-success-sim-") as td:
        work_root = Path(td)

        def fake_run_command(cmd: list[str], *, timeout_seconds: int = 60) -> tuple[dict[str, Any], str, str]:
            del timeout_seconds
            calls.append(cmd)
            stdout = ""
            stderr = ""
            rc = 0
            probe_stdout = fake_host_probe_stdout(cmd)
            if probe_stdout is not None:
                stdout = probe_stdout
            elif cmd and cmd[0] == "/usr/bin/cc":
                Path(cmd[cmd.index("-o") + 1]).write_bytes(b"fake-host-smoke-worker-binary-success\n")
            elif cmd and cmd[0] == "/usr/sbin/makefs":
                Path(cmd[-2]).write_bytes(b"fake-ufs-image-success\n")
            elif cmd and cmd[0] == "/sbin/mdconfig" and "-a" in cmd:
                stdout = "md42\n"
            elif cmd and cmd[0] == "/usr/sbin/fstyp":
                stdout = "ufs\n"
            elif cmd and cmd[0] == "/sbin/mount":
                copy_tree_contents(work_root / "media-tree", Path(cmd[-1]))
            elif cmd and cmd[0] == "/sbin/umount":
                mountpoint = Path(cmd[-1])
                for child in list(mountpoint.iterdir()):
                    if child.is_dir() and not child.is_symlink():
                        shutil.rmtree(child)
                    else:
                        child.unlink()
            elif cmd and cmd[0] == "/sbin/mdconfig" and "-d" in cmd:
                stdout = ""
            else:
                rc = 127
                stderr = "unexpected simulated command\n"
            result = fake_command_result(runner, cmd, rc, stdout, stderr)
            return result, stdout, stderr

        receipt = runner.run_host_smoke(
            work_root,
            generated_at_utc="2026-06-05T16:48:00Z",
            fixture_root=runner.DEFAULT_FIXTURE_ROOT,
            command_runner=fake_run_command,
            worker_runner=fake_worker_runner,
            simulated_host_commands=True,
        )
    receipt["simulation"] = {
        **(receipt.get("simulation", {}) if isinstance(receipt.get("simulation"), dict) else {}),
        "name": "full-success-orchestration-with-safe-capture-and-worker-digest",
        "fake_commands_observed": runner.redact_private_paths(calls, work_root),
        "claims_real_freebsd_execution": False,
        "safe_capture_executed_against_simulated_mount_tree": True,
        "worker_runner_is_checker_only": True,
    }
    out = ROOT / SUCCESS_SIM_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pretty_json(out, receipt)
    return receipt


def run_failure_simulation() -> dict[str, Any]:
    runner = load_runner_module()
    calls: list[list[str]] = []

    def fake_run_command(cmd: list[str], *, timeout_seconds: int = 60) -> tuple[dict[str, Any], str, str]:
        del timeout_seconds
        calls.append(cmd)
        stdout = ""
        stderr = ""
        rc = 0
        probe_stdout = fake_host_probe_stdout(cmd)
        if probe_stdout is not None:
            stdout = probe_stdout
        elif cmd and cmd[0] == "/usr/bin/cc":
            Path(cmd[cmd.index("-o") + 1]).write_bytes(b"fake-host-smoke-worker-binary\n")
        elif cmd and cmd[0] == "/usr/sbin/makefs":
            Path(cmd[-2]).write_bytes(b"fake-ufs-image\n")
        elif cmd and cmd[0] == "/sbin/mdconfig" and "-a" in cmd:
            stdout = "md42\n"
        elif cmd and cmd[0] == "/usr/sbin/fstyp":
            stdout = "ufs\n"
        elif cmd and cmd[0] == "/sbin/mount":
            rc = 1
            stderr = "simulated mount failure\n"
        elif cmd and cmd[0] == "/sbin/mdconfig" and "-d" in cmd:
            stdout = ""
        else:
            rc = 127
            stderr = "unexpected simulated command\n"
        result = fake_command_result(runner, cmd, rc, stdout, stderr)
        return result, stdout, stderr

    with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-failure-sim-") as td:
        receipt = runner.run_host_smoke(
            Path(td),
            generated_at_utc="2026-06-05T16:49:00Z",
            fixture_root=runner.DEFAULT_FIXTURE_ROOT,
            command_runner=fake_run_command,
            simulated_host_commands=True,
        )
    receipt["simulation"] = {
        **(receipt.get("simulation", {}) if isinstance(receipt.get("simulation"), dict) else {}),
        "name": "mount-failure-receipt-shaped-cleanup",
        "fake_commands_observed": runner.redact_private_paths(calls, Path(td)),
        "claims_real_freebsd_execution": False,
    }
    out = ROOT / FAILURE_SIM_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pretty_json(out, receipt)
    return receipt


def run_fstyp_output_failure_simulation() -> dict[str, Any]:
    """Prove multiline fstyp output fails before mount/worker authority."""
    runner = load_runner_module()
    calls: list[list[str]] = []

    def fake_run_command(cmd: list[str], *, timeout_seconds: int = 60) -> tuple[dict[str, Any], str, str]:
        del timeout_seconds
        calls.append(cmd)
        stdout = ""
        stderr = ""
        rc = 0
        probe_stdout = fake_host_probe_stdout(cmd)
        if probe_stdout is not None:
            stdout = probe_stdout
        elif cmd and cmd[0] == "/usr/bin/cc":
            Path(cmd[cmd.index("-o") + 1]).write_bytes(b"fake-host-smoke-worker-binary-fstyp-failure\n")
        elif cmd and cmd[0] == "/usr/sbin/makefs":
            Path(cmd[-2]).write_bytes(b"fake-ufs-image-fstyp-failure\n")
        elif cmd and cmd[0] == "/sbin/mdconfig" and "-a" in cmd:
            stdout = "md42\n"
        elif cmd and cmd[0] == "/usr/sbin/fstyp":
            stdout = "noise ignored by a last-line parser\nufs\n"
        elif cmd and cmd[0] == "/sbin/mdconfig" and "-d" in cmd:
            stdout = ""
        else:
            rc = 127
            stderr = "unexpected simulated command after fstyp failure\n"
        result = fake_command_result(runner, cmd, rc, stdout, stderr)
        return result, stdout, stderr

    with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-fstyp-output-sim-") as td_name:
        work_root = Path(td_name)
        receipt = runner.run_host_smoke(
            work_root,
            generated_at_utc="2026-06-05T17:07:00Z",
            fixture_root=runner.DEFAULT_FIXTURE_ROOT,
            command_runner=fake_run_command,
            simulated_host_commands=True,
        )
    receipt["simulation"] = {
        **(receipt.get("simulation", {}) if isinstance(receipt.get("simulation"), dict) else {}),
        "name": "fstyp-multiline-output-fails-before-mount",
        "fake_commands_observed": runner.redact_private_paths(calls, work_root),
        "claims_real_freebsd_execution": False,
        "fstyp_stdout_was_multiline": True,
    }
    out = ROOT / FSTYP_OUTPUT_FAILURE_SIM_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pretty_json(out, receipt)
    return receipt


def run_fixture_admission_failure_simulation() -> dict[str, Any]:
    """Prove caller-controlled fixture roots fail before any host command."""
    runner = load_runner_module()
    calls: list[list[str]] = []

    def fake_run_command(cmd: list[str], *, timeout_seconds: int = 60) -> tuple[dict[str, Any], str, str]:
        del timeout_seconds
        calls.append(cmd)
        return fake_command_result(runner, cmd, 127, "", "fixture admission should have stopped host commands\n"), "", "fixture admission should have stopped host commands\n"

    with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-fixture-admission-") as td_name:
        td = Path(td_name)
        outside_fixture = td / "caller-controlled-tree"
        outside_fixture.mkdir(mode=0o700)
        (outside_fixture / "invoice.pdf").write_bytes(b"caller-controlled bytes must not become makefs input\n")
        receipt = runner.run_host_smoke(
            td / "work",
            generated_at_utc="2026-06-05T16:50:00Z",
            fixture_root=outside_fixture,
            command_runner=fake_run_command,
            simulated_host_commands=True,
        )
    receipt["simulation"] = {
        **(receipt.get("simulation", {}) if isinstance(receipt.get("simulation"), dict) else {}),
        "name": "fixture-root-admission-fails-before-host-commands",
        "fake_commands_observed": calls,
        "claims_real_freebsd_execution": False,
    }
    out = ROOT / FIXTURE_ADMISSION_FAILURE_SIM_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pretty_json(out, receipt)
    return receipt


def run_fixture_copy_change_regression() -> dict[str, Any]:
    """Prove a source fixture mutation during copy fails closed before host commands."""
    runner = load_runner_module()
    real_copytree = runner.shutil.copytree
    with tempfile.TemporaryDirectory(prefix="derivebsd-fixture-copy-regression-", dir=runner.ALLOWED_FIXTURE_BASE) as fixture_name:
        fixture_root = Path(fixture_name)
        (fixture_root / "invoice.pdf").write_bytes(b"fixture bytes before copy\n")
        admission, admitted = runner.inspect_fixture_root(fixture_root)
        if admission.get("admitted") is not True:
            raise RuntimeError(f"test fixture was not admitted: {admission}")
        with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-copy-regression-") as td_name:
            dst = Path(td_name) / "media-tree"

            def mutating_copytree(src: Path, dest: Path, *, symlinks: bool = False):
                copied = real_copytree(src, dest, symlinks=symlinks)
                (Path(src) / "invoice.pdf").write_bytes(b"fixture bytes changed during copy\n")
                return copied

            runner.shutil.copytree = mutating_copytree
            try:
                try:
                    runner.copy_fixture_tree_verified(dst, admitted, admission)
                except runner.HostSmokeFailure as exc:
                    failure = {"stage": exc.stage, "message": exc.message, **exc.details}
                else:
                    failure = {"stage": None, "message": "copy unexpectedly succeeded"}
            finally:
                runner.shutil.copytree = real_copytree
    receipt = {
        "kind": "removable.media.local.freebsd.host.smoke.fixture.copy.regression",
        "schema_version": "0.1",
        "generated_for_version": VERSION,
        "smoke_id": SMOKE_ID,
        "result": "passed" if failure.get("stage") == "fixture-root-copy" else "failed",
        "failure": failure,
        "commands": [],
        "simulation": {
            "name": "fixture-source-changed-during-copy-fails-before-host-commands",
            "claims_real_freebsd_execution": False,
            "mutated_admitted_fixture_after_copytree": True,
        },
        "invariants": {
            "fixture_copy_change_detected": failure.get("stage") == "fixture-root-copy",
            "no_host_commands_after_fixture_copy_change": True,
        },
    }
    out = ROOT / FIXTURE_COPY_CHANGE_SIM_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pretty_json(out, receipt)
    return receipt



def check_host_smoke_receipt_schema_surface(*receipts: dict[str, Any]) -> list[str]:
    """Keep the real-host proof seam schema-shaped without importing jsonschema under -S.

    validate_spec_examples.py performs the full JSON-Schema validation in the
    release-critical profile.  This checker runs under -S, so it verifies the
    schema acceptance surface and the current generated receipts' semantic shape
    directly, then proves the checked-in schema example matches the cloudtainer
    refusal receipt generated by the runner.
    """
    errors: list[str] = []
    schema_path = ROOT / HOST_SMOKE_SCHEMA_REL
    example_path = ROOT / HOST_SMOKE_EXAMPLE_REL
    require(errors, schema_path.exists(), f"missing {HOST_SMOKE_SCHEMA_REL}")
    require(errors, example_path.exists(), f"missing {HOST_SMOKE_EXAMPLE_REL}")
    if not schema_path.exists() or not example_path.exists():
        return errors

    schema = load_json(HOST_SMOKE_SCHEMA_REL)
    props = schema.get("properties", {}) if isinstance(schema.get("properties"), dict) else {}
    required = schema.get("required", []) if isinstance(schema.get("required"), list) else []
    require(errors, schema.get("title") == "Removable media local FreeBSD host smoke receipt", "host-smoke schema title must be stable")
    require(errors, (props.get("kind") or {}).get("const") == "removable.media.local.freebsd.host.smoke.receipt", "host-smoke schema kind const missing")
    require(errors, (props.get("schema_version") or {}).get("const") == "0.1", "host-smoke schema version const missing")
    require(errors, (props.get("result") or {}).get("enum") == ["refused", "failed", "passed"], "host-smoke schema result enum must cover refused/failed/passed")
    for key in ["kind", "schema_version", "smoke_id", "generated_for_version", "runner_contract_version", "cube_cut_version", "generated_at_utc", "result", "refusal_reason", "host", "scope", "workspace", "simulation", "host_probes", "commands", "cleanup", "invariants"]:
        require(errors, key in required, f"host-smoke schema must require {key}")
    schema_text = schema_path.read_text(encoding="utf-8", errors="replace")
    for token in [
        "worker_source_copy_required_before_compile",
        "copy-c-worker-source-into-private-work-root-and-verify-digest-before-compile",
        "regular-files-plus-directories-stable-before-makefs",
        "mdconfig-vnode-readonly",
        "checker_only_host_command_simulation",
        "not_freebsd_host_proof",
        "claims_real_freebsd_execution",
        "replace-private-work-root-with-$PRIVATE_WORK_ROOT-in-receipts",
        "host_probe_capsicum_feature_enabled",
        "kern.features.security_capability_mode",
        "runner_contract_version",
        "cube_cut_version",
        "host_osreldate_minimum",
        "host_release_floor",
        "host_release_floor_policy",
        "host_osreldate_meets_supported_floor",
        "host_target_matrix_id",
        "host_target_tier_policy",
        "host_target_tier",
        "host_primary_release",
        "host_primary_osreldate_minimum",
    ]:
        require(errors, token in schema_text, f"host-smoke schema missing acceptance token {token!r}")

    generated_refusal = next((r for r in receipts if r.get("result") == "refused"), None)
    if generated_refusal is not None:
        example = load_json(HOST_SMOKE_EXAMPLE_REL)
        require(errors, example == generated_refusal, "host-smoke schema example must equal the current generated cloudtainer refusal receipt")

    for obj in receipts:
        label = str(obj.get("result")) + ":" + str(obj.get("smoke_id"))
        require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.receipt", f"{label} wrong host-smoke receipt kind")
        require(errors, obj.get("schema_version") == "0.1", f"{label} wrong schema_version")
        require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, f"{label} generated_for_version must bind current host-smoke runner contract")
        require(errors, obj.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, f"{label} runner_contract_version must bind current host-smoke runner contract")
        require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, f"{label} cube_cut_version must bind current cube cut")
        require(errors, obj.get("generated_for_version") == obj.get("runner_contract_version"), f"{label} legacy generated_for_version must remain a runner-contract alias")
        require(errors, obj.get("cube_cut_version") != obj.get("runner_contract_version"), f"{label} cube_cut_version must not be confused with runner contract")
        require(errors, obj.get("smoke_id") == SMOKE_ID, f"{label} smoke_id must bind current host-smoke runner")
        for key in ["host", "scope", "workspace", "simulation", "host_probes", "commands", "cleanup", "invariants"]:
            require(errors, isinstance(obj.get(key), list if key in {"host_probes", "commands"} else dict), f"{label} {key} has wrong top-level shape")
        scope = obj.get("scope", {}) if isinstance(obj.get("scope"), dict) else {}
        require(errors, scope.get("worker_source_copy_required_before_compile") is True, f"{label} must require private worker-source copy before compile")
        require(errors, scope.get("fixture_manifest_policy") == "regular-files-plus-directories-stable-before-makefs", f"{label} must use directory-aware fixture manifests")
        require(errors, scope.get("command_path_redaction_policy") == "replace-private-work-root-with-$PRIVATE_WORK_ROOT-in-receipts", f"{label} must bind command path redaction")
        require(errors, scope.get("host_release_floor_policy") == HOST_RELEASE_FLOOR_POLICY, f"{label} must bind the host release-floor policy")
        require(errors, scope.get("host_release_floor") == SUPPORTED_FREEBSD_RELEASE_FLOOR, f"{label} must bind the host release floor")
        require(errors, scope.get("host_osreldate_minimum") == MIN_FREEBSD_OSRELDATE, f"{label} must bind the minimum kern.osreldate")
        require(errors, scope.get("host_target_matrix_id") == HOST_TARGET_MATRIX_ID, f"{label} must bind the host target matrix id")
        require(errors, scope.get("host_target_tier_policy") == HOST_TARGET_TIER_POLICY, f"{label} must bind the host target tier policy")
        require(errors, scope.get("host_primary_release") == PRIMARY_FREEBSD_RELEASE, f"{label} must bind the primary FreeBSD release")
        require(errors, scope.get("host_primary_release_channel") == PRIMARY_FREEBSD_RELEASE_CHANNEL, f"{label} must bind the primary FreeBSD release channel")
        require(errors, scope.get("host_primary_osreldate_minimum") == PRIMARY_FREEBSD_OSRELDATE_MINIMUM, f"{label} must bind the primary kern.osreldate minimum")
        sim = obj.get("simulation", {}) if isinstance(obj.get("simulation"), dict) else {}
        result = obj.get("result")
        if result == "refused":
            require(errors, obj.get("refusal_reason") in {"non-freebsd-host", "root-required", "explicit-host-smoke-flag-required", "work-dir-must-not-already-exist"}, f"{label} refusal reason must be typed")
            require(errors, obj.get("host_probes") == [], f"{label} refusal must carry no host probes")
            require(errors, obj.get("commands") == [], f"{label} refusal must carry no commands")
        elif result == "failed":
            require(errors, obj.get("refusal_reason") is None, f"{label} failed receipt must not also be refusal")
            failure = obj.get("failure", {}) if isinstance(obj.get("failure"), dict) else {}
            require(errors, failure.get("receipt_shaped_instead_of_traceback") is True, f"{label} failure must be receipt-shaped")
            require(errors, isinstance(obj.get("host_smoke"), dict), f"{label} failed receipt must include host_smoke evidence")
        elif result == "passed":
            require(errors, obj.get("refusal_reason") is None, f"{label} passed receipt must not be refusal")
            host_smoke = obj.get("host_smoke", {}) if isinstance(obj.get("host_smoke"), dict) else {}
            require_complete_host_probes(errors, obj, label)
            require(errors, host_smoke.get("observed_fstyp") == "ufs", f"{label} passed receipt must observe UFS before mount")
            require(errors, host_smoke.get("worker_env_policy") == "empty-environment", f"{label} passed receipt must clear worker environment")
            require(errors, host_smoke.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo", f"{label} passed receipt must use private non-media cwd")
            if sim.get("checker_only_host_command_simulation") is False:
                host = obj.get("host", {}) if isinstance(obj.get("host"), dict) else {}
                require(errors, host.get("observed_system") == "FreeBSD", f"{label} non-simulated passed receipt must be from FreeBSD")
                require(errors, sim.get("not_freebsd_host_proof") is False, f"{label} non-simulated passed receipt must not mark itself as non-host proof")
        else:
            errors.append(f"{label} result must be refused, failed, or passed")
    return errors

def check_refusal_receipt(obj: dict[str, Any], rc: int) -> list[str]:
    errors: list[str] = []
    require(errors, rc == 2, "cloudtainer host smoke invocation must exit 2 for structured refusal")
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.receipt", "wrong receipt kind")
    require(errors, obj.get("schema_version") == "0.1", "schema version must be 0.1")
    require(errors, obj.get("smoke_id") == SMOKE_ID, "smoke_id must bind current release")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "generated_for_version must bind current runner contract")
    require(errors, obj.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "runner_contract_version must bind current runner contract")
    require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "cube_cut_version must bind current cube cut")
    require(errors, obj.get("result") == "refused", "Linux cloudtainer receipt must be refused")
    require(errors, obj.get("refusal_reason") == "non-freebsd-host", "Linux cloudtainer must refuse as non-freebsd-host")
    require(errors, obj.get("host_probes") == [], "refusal must not run host probes")
    require(errors, obj.get("commands") == [], "refusal must not run host commands")
    host = obj.get("host", {}) if isinstance(obj.get("host"), dict) else {}
    scope = obj.get("scope", {}) if isinstance(obj.get("scope"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    require(errors, host.get("required_os") == "FreeBSD", "host smoke must require FreeBSD")
    require(errors, host.get("requires_root") is True, "host smoke must require root")
    require(errors, host.get("cloudtainer_refusal_is_expected") is True, "Linux refusal must be expected evidence")
    require(errors, scope.get("filesystem_image") == "disposable-ufs-image-created-by-makefs", "host smoke must use a disposable UFS image")
    require(errors, scope.get("device_attachment") == "mdconfig-vnode-readonly", "host smoke must attach via mdconfig vnode readonly")
    require(errors, scope.get("mount_options") == ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"], "host smoke must bind hardened FreeBSD mount options")
    require(errors, scope.get("fd5_canary_source") == "broker-nonmedia-canary-not-source-media", "fd5 canary must be non-media")
    require(errors, scope.get("worker_bridge_id") == BRIDGE_ID, "host smoke must bind current Capsicum worker bridge")
    require(errors, scope.get("host_release_floor_policy") == HOST_RELEASE_FLOOR_POLICY, "host smoke must bind host release-floor policy")
    require(errors, scope.get("host_release_floor") == SUPPORTED_FREEBSD_RELEASE_FLOOR, "host smoke must bind host release floor")
    require(errors, scope.get("host_osreldate_minimum") == MIN_FREEBSD_OSRELDATE, "host smoke must bind minimum kern.osreldate")
    require(errors, scope.get("host_target_matrix_id") == HOST_TARGET_MATRIX_ID, "host smoke must bind host target matrix id")
    require(errors, scope.get("host_target_tier_policy") == HOST_TARGET_TIER_POLICY, "host smoke must bind host target tier policy")
    require(errors, scope.get("host_primary_release") == PRIMARY_FREEBSD_RELEASE, "host smoke must bind primary FreeBSD release")
    require(errors, scope.get("host_primary_release_channel") == PRIMARY_FREEBSD_RELEASE_CHANNEL, "host smoke must bind primary FreeBSD release channel")
    require(errors, scope.get("host_primary_osreldate_minimum") == PRIMARY_FREEBSD_OSRELDATE_MINIMUM, "host smoke must bind primary kern.osreldate minimum")
    for key in ["no_host_commands_after_refusal", "no_mount_attempted_after_refusal", "no_worker_launch_after_refusal", "cloudtainer_does_not_claim_freebsd_capsicum_execution"]:
        require(errors, inv.get(key) is True, f"refusal invariant {key} must be true")
    return errors


def check_success_simulation(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.receipt", "success simulation wrong kind")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "success simulation version must bind current runner contract")
    require(errors, obj.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "success simulation runner_contract_version must bind current runner contract")
    require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "success simulation cube_cut_version must bind current cube cut")
    require(errors, obj.get("smoke_id") == SMOKE_ID, "success simulation smoke_id must bind current release")
    require(errors, obj.get("result") == "passed", "simulated success must produce passed receipt")
    require(errors, obj.get("refusal_reason") is None, "success simulation must not be a refusal")
    commands = obj.get("commands", []) if isinstance(obj.get("commands"), list) else []
    command_roles = [cmd.get("command_role") for cmd in commands if isinstance(cmd, dict)]
    require(errors, command_roles == [
        "compile-worker",
        "makefs-image",
        "mdconfig-attach-readonly",
        "fstyp-verify-ufs",
        "mount-readonly-untrusted",
        "umount-before-worker",
        "mdconfig-detach-before-worker",
    ], "success simulation must exercise host commands in production order")
    by_role = {cmd.get("command_role"): cmd for cmd in commands if isinstance(cmd, dict)}
    attach_row = by_role.get("mdconfig-attach-readonly", {})
    fstyp_row = by_role.get("fstyp-verify-ufs", {})
    mount_row = by_role.get("mount-readonly-untrusted", {})
    detach_row = by_role.get("mdconfig-detach-before-worker", {})
    require(errors, attach_row.get("observed_value") == "md42", "mdconfig attach command must record normalized md unit")
    require(errors, attach_row.get("observed_stdout_text") == "md42\n", "mdconfig attach command must carry replayable stdout text")
    require(errors, attach_row.get("observed_value_key") == "host_smoke.observed_md_unit", "mdconfig attach command must bind host_smoke.observed_md_unit")
    require(errors, fstyp_row.get("observed_value") == "ufs", "fstyp command must record observed filesystem token")
    require(errors, fstyp_row.get("observed_stdout_text") == "ufs\n", "fstyp command must carry replayable stdout text")
    require(errors, fstyp_row.get("observed_value_key") == "host_smoke.observed_fstyp", "fstyp command must bind host_smoke.observed_fstyp")
    require(errors, fstyp_row.get("command") == ["/usr/sbin/fstyp", "/dev/md42"], "fstyp command must use the mdconfig-emitted device")
    require(errors, isinstance(mount_row.get("command"), list) and "/dev/md42" in mount_row.get("command", []), "mount command must use the mdconfig-emitted device")
    require(errors, detach_row.get("command") == ["/sbin/mdconfig", "-d", "-u", "42"], "detach command must use the mdconfig-emitted unit number")
    require_complete_host_probes(errors, obj, "success simulation")
    cleanup = obj.get("cleanup", {}) if isinstance(obj.get("cleanup"), dict) else {}
    host_smoke = obj.get("host_smoke", {}) if isinstance(obj.get("host_smoke"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    simulation = obj.get("simulation", {}) if isinstance(obj.get("simulation"), dict) else {}
    worker = host_smoke.get("worker", {}) if isinstance(host_smoke.get("worker"), dict) else {}
    report = worker.get("output_report", {}) if isinstance(worker.get("output_report"), dict) else {}
    require(errors, cleanup.get("commands") == [], "success simulation must not need failure cleanup commands")
    require(errors, cleanup.get("cleanup_completed_before_receipt") is True, "success simulation must finish cleanup before receipt")
    require(errors, host_smoke.get("umounted_before_worker") is True, "success simulation must unmount before worker")
    require(errors, host_smoke.get("mdconfig_detached_before_worker") is True, "success simulation must detach md before worker")
    admission = obj.get("fixture_admission", {}) if isinstance(obj.get("fixture_admission"), dict) else {}
    fixture_copy = obj.get("fixture_copy", {}) if isinstance(obj.get("fixture_copy"), dict) else {}
    require(errors, admission.get("admitted") is True, "success simulation must admit checked-in fixture root before host commands")
    require(errors, admission.get("checked_before_host_commands") is True, "fixture admission must happen before host commands")
    require(errors, admission.get("no_symlink_or_special_entries") is True, "fixture admission must reject symlink/special entries")
    require(errors, admission.get("manifest_includes_directories") is True, "fixture admission manifest must include directory entries that makefs would image")
    require(errors, isinstance(admission.get("directory_count"), int), "fixture admission must report directory_count")
    require(errors, fixture_copy.get("manifest_includes_directories") is True, "fixture copy manifest must include directory entries")
    require(errors, fixture_copy.get("source_stable_since_admission") is True, "fixture copy must prove source stable since admission")
    require(errors, fixture_copy.get("source_stable_during_copy") is True, "fixture copy must prove source stable during copy")
    require(errors, fixture_copy.get("copy_matches_source_manifest") is True, "fixture copy must match source manifest before host commands")
    require(errors, fixture_copy.get("checked_before_host_commands") is True, "fixture copy verification must precede host commands")
    worker_source = obj.get("worker_source_copy", {}) if isinstance(obj.get("worker_source_copy"), dict) else {}
    host_worker_source = host_smoke.get("worker_source_copy", {}) if isinstance(host_smoke.get("worker_source_copy"), dict) else {}
    require(errors, worker_source.get("source_regular_file") is True and worker_source.get("source_not_symlink") is True, "worker source copy must admit a regular non-symlink C source")
    require(errors, worker_source.get("source_stable_during_copy") is True, "worker source copy must prove source stability during copy")
    require(errors, worker_source.get("copy_matches_source_digest") is True, "worker source copy must match the admitted source digest")
    require(errors, worker_source.get("compile_uses_private_source_copy") is True, "compile must use the private worker source copy")
    require(errors, host_worker_source.get("copied_source_sha256") == worker_source.get("copied_source_sha256"), "host_smoke must carry the same worker source copy evidence")
    compile_commands = [cmd for cmd in commands if isinstance(cmd, dict) and cmd.get("command_role") == "compile-worker"]
    if compile_commands:
        compile_cmd = compile_commands[0].get("command", [])
        require(errors, "$PRIVATE_WORK_ROOT/worker-source/rm_post_detach_capsicum_worker.c" in compile_cmd, "compile command must use redacted private worker source copy")
        require(errors, "tools/freebsd/rm_post_detach_capsicum_worker.c" not in compile_cmd, "compile command must not use live repository worker source")
    require(errors, inv.get("fixture_root_admitted_before_host_commands") is True, "success invariant must bind fixture admission before host commands")
    require(errors, inv.get("fixture_root_has_no_symlink_or_special_entries") is True, "success invariant must bind boring fixture tree")
    require(errors, inv.get("fixture_source_stable_during_copy") is True, "success invariant must bind source-stable fixture copy")
    require(errors, inv.get("fixture_copy_matches_source_manifest") is True, "success invariant must bind fixture copy manifest equality")
    require(errors, inv.get("worker_source_copied_before_compile") is True, "success invariant must copy worker source before compile")
    require(errors, inv.get("worker_source_regular_not_symlink") is True, "success invariant must admit regular non-symlink worker source")
    require(errors, inv.get("worker_source_stable_during_copy") is True, "success invariant must bind source-stable worker source copy")
    require(errors, inv.get("worker_source_copy_matches_digest") is True, "success invariant must bind worker source copy digest equality")
    require(errors, inv.get("compile_uses_private_worker_source_copy") is True, "success invariant must bind private worker source compile input")
    require(errors, worker.get("return_code") == 0, "success simulation worker must return zero")
    require(errors, worker.get("launcher_fd_slot_policy") == "duplicate-target-fds-above-delegated-range-before-clearing-slots", "success worker launcher must save target fd slots before opening delegated files")
    require(errors, worker.get("launcher_restored_parent_fd_slots") is True, "success worker launcher must restore parent fd slots")
    slot_evidence = worker.get("launcher_fd_slot_evidence", {}) if isinstance(worker.get("launcher_fd_slot_evidence"), dict) else {}
    require(errors, slot_evidence.get("preexisting_parent_fd_inheritable_flags_preserved") is True, "success worker launcher must preserve parent fd inheritability flags")
    require(errors, worker.get("stdout_bytes") == 0 and worker.get("stderr_bytes") == 0, "success worker must not use stdio")
    require(errors, worker.get("worker_env_policy") == "empty-environment" and worker.get("worker_env_keys_passed") == [], "success worker launch must clear the environment")
    require(errors, worker.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo" and worker.get("worker_cwd_contains_media_tree") is False, "success worker launch must use a private non-media cwd")
    require(errors, host_smoke.get("worker_env_policy") == "empty-environment", "host-smoke evidence must bind empty worker environment policy")
    require(errors, host_smoke.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "host-smoke evidence must bind private worker cwd policy")
    require(errors, report.get("capsicum_mode_entered") is True, "success worker report must bind capability-mode entry")
    require(errors, report.get("extra_fds_closed_before_cap_enter") is True, "success worker report must close extra fds")
    require(errors, report.get("extra_fd_canary_observed_before_closefrom") is True, "success worker report must prove fd-5 was child-inherited before closefrom")
    require(errors, report.get("input_sha256") == host_smoke.get("capture_digest"), "success worker digest must match safe-capture CAS digest")
    require(errors, report.get("input_bytes") == host_smoke.get("capture_size_bytes"), "success worker byte count must match capture size")
    require(errors, inv.get("worker_reported_capsicum_mode_entered") is True, "success invariant must require capability-mode entry")
    require(errors, inv.get("worker_reported_fd5_canary_observed_before_closefrom") is True, "success invariant must require fd-5 observation before closefrom")
    require(errors, inv.get("worker_stdout_stderr_bytes_zero") is True, "success invariant must require no worker stdio")
    require(errors, inv.get("worker_environment_empty") is True, "success invariant must require empty worker environment")
    require(errors, inv.get("worker_cwd_private_not_media") is True, "success invariant must require a private non-media worker cwd")
    require(errors, inv.get("worker_input_sha256_matches_capture_digest") is True, "success invariant must bind worker digest to capture digest")
    require(errors, inv.get("host_probes_collected_before_media_commands") is True, "success invariant must bind host probes before media commands")
    require(errors, inv.get("host_probe_observed_freebsd") is True, "success invariant must bind FreeBSD host probe")
    require(errors, inv.get("host_probe_observed_root_uid") is True, "success invariant must bind root host probe")
    require(errors, inv.get("host_probe_capsicum_feature_enabled") is True, "success invariant must bind Capsicum feature probes")
    probe_values = host_smoke.get("host_probe_values", {}) if isinstance(host_smoke.get("host_probe_values"), dict) else {}
    require(errors, probe_values.get("host_probe_observed_system") == "FreeBSD", "host_smoke must carry host_probe_values")
    require(errors, probe_values.get("host_probe_osreldate") == str(PRIMARY_FREEBSD_OSRELDATE_MINIMUM), "host_smoke must carry the primary target kern.osreldate proof")
    require(errors, host_smoke.get("host_target_tier") == HOST_TARGET_PRIMARY_TIER, "host_smoke must record the primary production target tier")
    require(errors, host_smoke.get("host_target_matrix_id") == HOST_TARGET_MATRIX_ID, "host_smoke must bind the host target matrix id")
    require(errors, inv.get("host_osreldate_meets_supported_floor") is True, "success invariant must prove kern.osreldate meets supported floor")
    require(errors, inv.get("host_target_tier_recorded") is True, "success invariant must prove host target tier recording")
    require(errors, inv.get("host_command_environment_sanitized") is True, "success invariant must bind sanitized host command environment")
    require(errors, host_smoke.get("host_command_env_policy") == load_runner_module().HOST_COMMAND_ENV_POLICY, "host-smoke evidence must bind sanitized host command environment policy")
    require_sanitized_host_command_rows(errors, obj, "success simulation")
    require(errors, inv.get("cloudtainer_simulation_not_freebsd_host_proof") is True, "success simulation must be marked as not host proof")
    require(errors, simulation.get("claims_real_freebsd_execution") is False, "success simulation must explicitly deny real FreeBSD execution")
    require(errors, simulation.get("safe_capture_executed_against_simulated_mount_tree") is True, "success simulation must exercise safe capture against a simulated mount tree")
    require(errors, simulation.get("worker_runner_is_checker_only") is True, "success simulation worker must be checker-only")
    return errors


def check_failure_simulation(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.receipt", "failure simulation wrong kind")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "failure simulation version must bind current runner contract")
    require(errors, obj.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "failure simulation runner_contract_version must bind current runner contract")
    require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "failure simulation cube_cut_version must bind current cube cut")
    require(errors, obj.get("result") == "failed", "simulated mount failure must produce failed receipt, not an exception")
    require(errors, obj.get("refusal_reason") is None, "failure simulation must not be a refusal")
    failure = obj.get("failure", {}) if isinstance(obj.get("failure"), dict) else {}
    cleanup = obj.get("cleanup", {}) if isinstance(obj.get("cleanup"), dict) else {}
    host_smoke = obj.get("host_smoke", {}) if isinstance(obj.get("host_smoke"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    simulation = obj.get("simulation", {}) if isinstance(obj.get("simulation"), dict) else {}
    require_complete_host_probes(errors, obj, "failure simulation")
    require(errors, failure.get("stage") == "mount-readonly-untrusted", "simulated failure stage must be mount-readonly-untrusted")
    require(errors, failure.get("receipt_shaped_instead_of_traceback") is True, "failure must be explicitly receipt-shaped")
    require(errors, cleanup.get("attempted_mdconfig_detach_after_failure") is True, "mount failure after attach must attempt mdconfig detach cleanup")
    require(errors, cleanup.get("mounted_after_cleanup_assumed") is False, "failure receipt must record not mounted after cleanup")
    require(errors, cleanup.get("mdconfig_unit_after_cleanup") is None, "failure receipt must record no md unit after cleanup")
    require(errors, host_smoke.get("worker_launched") is False, "pre-worker failure must not launch worker")
    require(errors, inv.get("failure_paths_are_receipt_shaped") is True, "failure invariant must bind receipt-shaped failure")
    require(errors, inv.get("no_worker_launch_after_host_failure") is True, "failure invariant must bind no worker launch")
    require(errors, inv.get("cleanup_attempted_after_mdconfig_attach") is True, "failure invariant must bind md cleanup evidence")
    require(errors, inv.get("host_command_environment_sanitized") is True, "failure invariant must bind sanitized host command environment")
    require_sanitized_host_command_rows(errors, obj, "failure simulation")
    require(errors, inv.get("cloudtainer_simulation_not_freebsd_host_proof") is True, "simulation must not claim FreeBSD host proof")
    require(errors, simulation.get("claims_real_freebsd_execution") is False, "failure simulation must explicitly deny real FreeBSD execution")
    calls = simulation.get("fake_commands_observed", []) if isinstance(simulation.get("fake_commands_observed"), list) else []
    require(errors, any(isinstance(cmd, list) and cmd[:2] == ["/sbin/mdconfig", "-d"] for cmd in calls), "failure simulation must observe mdconfig detach cleanup")
    return errors


def check_fstyp_output_failure_simulation(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.receipt", "fstyp-output failure simulation wrong kind")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "fstyp-output failure simulation version must bind current runner contract")
    require(errors, obj.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "fstyp-output failure simulation runner_contract_version must bind current runner contract")
    require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "fstyp-output failure simulation cube_cut_version must bind current cube cut")
    require(errors, obj.get("result") == "failed", "multiline fstyp output must produce failed receipt")
    failure = obj.get("failure", {}) if isinstance(obj.get("failure"), dict) else {}
    cleanup = obj.get("cleanup", {}) if isinstance(obj.get("cleanup"), dict) else {}
    host_smoke = obj.get("host_smoke", {}) if isinstance(obj.get("host_smoke"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    simulation = obj.get("simulation", {}) if isinstance(obj.get("simulation"), dict) else {}
    require_complete_host_probes(errors, obj, "fstyp-output failure simulation")
    require(errors, failure.get("stage") == "fstyp-verify-ufs", "multiline fstyp output must fail at fstyp-verify-ufs")
    require(errors, "non-canonical multiline" in str(failure.get("message", "")), "fstyp failure message must identify non-canonical multiline output")
    require(errors, cleanup.get("attempted_mdconfig_detach_after_failure") is True, "fstyp output failure after attach must detach mdconfig unit")
    require(errors, host_smoke.get("worker_launched") is False, "fstyp output failure must not launch worker")
    require(errors, inv.get("no_worker_launch_after_host_failure") is True, "fstyp output failure invariant must bind no worker launch")
    require(errors, inv.get("host_command_environment_sanitized") is True, "fstyp output failure invariant must bind sanitized host command environment")
    require(errors, simulation.get("fstyp_stdout_was_multiline") is True, "fstyp output simulation must disclose multiline stdout")
    require(errors, simulation.get("claims_real_freebsd_execution") is False, "fstyp output simulation must deny FreeBSD execution")
    calls = simulation.get("fake_commands_observed", []) if isinstance(simulation.get("fake_commands_observed"), list) else []
    require(errors, not any(isinstance(cmd, list) and cmd and cmd[0] == "/sbin/mount" for cmd in calls), "fstyp output failure must not reach mount")
    require_sanitized_host_command_rows(errors, obj, "fstyp-output failure simulation")
    return errors


def check_fixture_admission_failure_simulation(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.receipt", "fixture admission failure wrong kind")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "fixture admission failure version must bind current runner contract")
    require(errors, obj.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "fixture admission failure runner_contract_version must bind current runner contract")
    require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "fixture admission failure cube_cut_version must bind current cube cut")
    require(errors, obj.get("result") == "failed", "fixture admission failure must be a failed receipt")
    failure = obj.get("failure", {}) if isinstance(obj.get("failure"), dict) else {}
    admission = obj.get("fixture_admission", {}) if isinstance(obj.get("fixture_admission"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    host_smoke = obj.get("host_smoke", {}) if isinstance(obj.get("host_smoke"), dict) else {}
    simulation = obj.get("simulation", {}) if isinstance(obj.get("simulation"), dict) else {}
    require(errors, failure.get("stage") == "fixture-root-admission", "outside fixture root must fail at fixture-root-admission")
    require(errors, admission.get("admitted") is False, "outside fixture root must not be admitted")
    require(errors, admission.get("reason") == "fixture-root-outside-allowed-base", "outside fixture root must fail with outside-base reason")
    require(errors, obj.get("commands") == [], "fixture admission failure must not run host commands")
    require(errors, host_smoke.get("worker_launched") is False, "fixture admission failure must not launch worker")
    require(errors, inv.get("no_host_commands_after_fixture_admission_failure") is True, "fixture admission failure invariant must bind no host commands")
    require(errors, inv.get("fixture_failure_stops_before_host_commands") is True, "fixture admission failure invariant must bind stop-before-host-commands")
    require(errors, simulation.get("fake_commands_observed") == [], "fixture admission simulation must observe no fake host commands")
    require(errors, simulation.get("claims_real_freebsd_execution") is False, "fixture admission simulation must not claim FreeBSD execution")
    return errors



def run_fixture_copy_directory_change_regression() -> dict[str, Any]:
    """Prove empty-directory mutations are included in the makefs source manifest."""
    runner = load_runner_module()
    real_copytree = runner.shutil.copytree
    with tempfile.TemporaryDirectory(prefix="derivebsd-fixture-copy-dir-regression-", dir=runner.ALLOWED_FIXTURE_BASE) as fixture_name:
        fixture_root = Path(fixture_name)
        (fixture_root / "invoice.pdf").write_bytes(b"fixture bytes before empty dir mutation\n")
        admission, admitted = runner.inspect_fixture_root(fixture_root)
        if admission.get("admitted") is not True:
            raise RuntimeError(f"test fixture was not admitted: {admission}")
        with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-copy-dir-regression-") as td_name:
            dst = Path(td_name) / "media-tree"

            def mutating_copytree(src: Path, dest: Path, *, symlinks: bool = False):
                copied = real_copytree(src, dest, symlinks=symlinks)
                (Path(src) / "empty-dir-added-during-copy").mkdir()
                return copied

            runner.shutil.copytree = mutating_copytree
            try:
                try:
                    runner.copy_fixture_tree_verified(dst, admitted, admission)
                except runner.HostSmokeFailure as exc:
                    failure = {"stage": exc.stage, "message": exc.message, **exc.details}
                else:
                    failure = {"stage": None, "message": "directory mutation unexpectedly succeeded"}
            finally:
                runner.shutil.copytree = real_copytree
    receipt = {
        "kind": "removable.media.local.freebsd.host.smoke.fixture.copy.directory.regression",
        "schema_version": "0.1",
        "generated_for_version": VERSION,
        "smoke_id": SMOKE_ID,
        "result": "passed" if failure.get("stage") == "fixture-root-copy" else "failed",
        "failure": failure,
        "commands": [],
        "simulation": {
            "name": "fixture-empty-directory-added-during-copy-fails-before-host-commands",
            "claims_real_freebsd_execution": False,
            "mutated_admitted_fixture_with_empty_directory_after_copytree": True,
        },
        "invariants": {
            "fixture_directory_mutation_detected": failure.get("stage") == "fixture-root-copy",
            "fixture_manifest_includes_directories": True,
            "no_host_commands_after_fixture_copy_directory_change": True,
        },
    }
    out = ROOT / FIXTURE_COPY_DIRECTORY_CHANGE_SIM_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pretty_json(out, receipt)
    return receipt

def run_worker_source_copy_change_regression() -> dict[str, Any]:
    """Prove C worker source mutation during copy fails closed before host commands."""
    runner = load_runner_module()
    real_copy2 = runner.shutil.copy2
    with tempfile.TemporaryDirectory(prefix="derivebsd-worker-source-copy-regression-", dir=ROOT) as td_name:
        td = Path(td_name)
        source = td / "rm_post_detach_capsicum_worker.c"
        source.write_text("int main(void) { return 0; }\n", encoding="utf-8")
        admission = runner.inspect_worker_source(source)
        if admission.get("admitted") is not True:
            raise RuntimeError(f"test worker source was not admitted: {admission}")
        dst = td / "work" / "worker-source" / "rm_post_detach_capsicum_worker.c"

        def mutating_copy2(src: Path, dest: Path):
            copied = real_copy2(src, dest)
            Path(src).write_text("int main(void) { return 23; }\n", encoding="utf-8")
            return copied

        runner.shutil.copy2 = mutating_copy2
        try:
            try:
                runner.copy_worker_source_verified(dst, source, admission)
            except runner.HostSmokeFailure as exc:
                failure = {"stage": exc.stage, "message": exc.message, **exc.details}
            else:
                failure = {"stage": None, "message": "copy unexpectedly succeeded"}
        finally:
            runner.shutil.copy2 = real_copy2
    receipt = {
        "kind": "removable.media.local.freebsd.host.smoke.worker.source.copy.regression",
        "schema_version": "0.1",
        "generated_for_version": VERSION,
        "smoke_id": SMOKE_ID,
        "result": "passed" if failure.get("stage") == "worker-source-copy" else "failed",
        "failure": failure,
        "commands": [],
        "simulation": {
            "name": "worker-source-changed-during-copy-fails-before-host-commands",
            "claims_real_freebsd_execution": False,
            "mutated_admitted_worker_source_after_copy2": True,
        },
        "invariants": {
            "worker_source_copy_change_detected": failure.get("stage") == "worker-source-copy",
            "no_host_commands_after_worker_source_copy_change": True,
        },
    }
    out = ROOT / WORKER_SOURCE_COPY_CHANGE_SIM_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    write_pretty_json(out, receipt)
    return receipt


def check_fixture_copy_change_regression(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.fixture.copy.regression", "fixture copy regression wrong kind")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "fixture copy regression version must bind current runner contract")
    require(errors, obj.get("result") == "passed", "fixture copy source-change regression must pass")
    failure = obj.get("failure", {}) if isinstance(obj.get("failure"), dict) else {}
    fixture_copy = failure.get("fixture_copy", {}) if isinstance(failure.get("fixture_copy"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    require(errors, failure.get("stage") == "fixture-root-copy", "fixture source mutation must fail at fixture-root-copy")
    require(errors, fixture_copy.get("source_stable_during_copy") is False, "fixture copy regression must observe unstable source during copy")
    require(errors, fixture_copy.get("source_manifest_sha256_after_copy") != fixture_copy.get("source_manifest_sha256_before_copy"), "fixture copy regression must record changed source manifest after copy")
    require(errors, obj.get("commands") == [], "fixture copy regression must not run host commands")
    require(errors, inv.get("fixture_copy_change_detected") is True, "fixture copy regression invariant must bind change detection")
    require(errors, inv.get("no_host_commands_after_fixture_copy_change") is True, "fixture copy regression invariant must bind no host commands")
    return errors



def check_fixture_copy_directory_change_regression(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.fixture.copy.directory.regression", "fixture copy directory regression wrong kind")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "fixture copy directory regression version must bind current runner contract")
    require(errors, obj.get("result") == "passed", "fixture empty-directory source-change regression must pass")
    failure = obj.get("failure", {}) if isinstance(obj.get("failure"), dict) else {}
    fixture_copy = failure.get("fixture_copy", {}) if isinstance(failure.get("fixture_copy"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    require(errors, failure.get("stage") == "fixture-root-copy", "fixture empty-directory mutation must fail at fixture-root-copy")
    require(errors, fixture_copy.get("source_stable_during_copy") is False, "fixture directory regression must observe unstable source during copy")
    require(errors, fixture_copy.get("source_manifest_sha256_after_copy") != fixture_copy.get("source_manifest_sha256_before_copy"), "fixture directory regression must record changed source manifest after empty directory addition")
    require(errors, obj.get("commands") == [], "fixture directory regression must not run host commands")
    require(errors, inv.get("fixture_directory_mutation_detected") is True, "fixture directory regression invariant must bind directory mutation detection")
    require(errors, inv.get("fixture_manifest_includes_directories") is True, "fixture directory regression invariant must bind directory-aware manifest")
    require(errors, inv.get("no_host_commands_after_fixture_copy_directory_change") is True, "fixture directory regression invariant must bind no host commands")
    return errors

def check_worker_source_copy_change_regression(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    require(errors, obj.get("kind") == "removable.media.local.freebsd.host.smoke.worker.source.copy.regression", "worker source copy regression wrong kind")
    require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "worker source copy regression version must bind current runner contract")
    require(errors, obj.get("result") == "passed", "worker source source-change regression must pass")
    failure = obj.get("failure", {}) if isinstance(obj.get("failure"), dict) else {}
    worker_source = failure.get("worker_source_copy", {}) if isinstance(failure.get("worker_source_copy"), dict) else {}
    inv = obj.get("invariants", {}) if isinstance(obj.get("invariants"), dict) else {}
    require(errors, failure.get("stage") == "worker-source-copy", "worker source mutation must fail at worker-source-copy")
    require(errors, worker_source.get("source_stable_during_copy") is False, "worker source copy regression must observe unstable source during copy")
    require(errors, worker_source.get("source_sha256_after_copy") != worker_source.get("source_sha256_before_copy"), "worker source copy regression must record changed source digest after copy")
    require(errors, obj.get("commands") == [], "worker source copy regression must not run host commands")
    require(errors, inv.get("worker_source_copy_change_detected") is True, "worker source copy regression invariant must bind change detection")
    require(errors, inv.get("no_host_commands_after_worker_source_copy_change") is True, "worker source copy regression invariant must bind no host commands")
    return errors


def _validator_result(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-B", "-S", VALIDATOR_REL, *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def check_receipt_validator() -> list[str]:
    """Guard the operator-facing validator for real host-smoke evidence.

    The validator must accept checker-only receipts only when explicitly asked
    and must reject them in default real-host-proof mode.
    """
    errors: list[str] = []
    validator = ROOT / VALIDATOR_REL
    require(errors, validator.exists(), f"missing {VALIDATOR_REL}")
    if not validator.exists():
        return errors

    success_default = _validator_result(SUCCESS_SIM_REL)
    require(errors, success_default.returncode != 0, "host-smoke validator must reject checker-only success simulation in default real-proof mode")
    require(errors, "not real host proof" in success_default.stdout or "checker-only" in success_default.stdout or "real host proof" in success_default.stdout, "default validator rejection must explain simulation is not real host proof")

    success_allowed = _validator_result("--allow-checker-simulation", SUCCESS_SIM_REL)
    require(errors, success_allowed.returncode == 0, f"host-smoke validator must accept success simulation only with --allow-checker-simulation: {success_allowed.stdout} {success_allowed.stderr}")

    refusal_default = _validator_result(VALIDATION_REL)
    require(errors, refusal_default.returncode != 0, "host-smoke validator must reject cloudtainer refusal in default real-proof mode")
    refusal_allowed = _validator_result("--allow-refusal", VALIDATION_REL)
    require(errors, refusal_allowed.returncode == 0, f"host-smoke validator must accept refusal only with --allow-refusal: {refusal_allowed.stdout} {refusal_allowed.stderr}")

    failure_allowed = _validator_result("--allow-failed", "--allow-checker-simulation", FAILURE_SIM_REL)
    require(errors, failure_allowed.returncode == 0, f"host-smoke validator must accept failure simulation only with explicit non-proof flags: {failure_allowed.stdout} {failure_allowed.stderr}")

    with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-validator-tamper-") as td_name:
        tampered = load_json(SUCCESS_SIM_REL)
        tampered["cube_cut_version"] = tampered.get("runner_contract_version")
        tampered_path = Path(td_name) / "tampered-cube-cut-version.json"
        write_pretty_json(tampered_path, tampered)
        tampered_result = subprocess.run(
            [sys.executable, "-B", "-S", VALIDATOR_REL, "--allow-checker-simulation", str(tampered_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, tampered_result.returncode != 0, "host-smoke validator must reject cube cut / runner contract version confusion")

        tampered = load_json(SUCCESS_SIM_REL)
        host_probes = tampered.get("host_probes", []) if isinstance(tampered.get("host_probes"), list) else []
        if host_probes and isinstance(host_probes[0], dict):
            host_probes[0]["command_shape_sha256"] = "sha256:" + "0" * 64
        tampered_path = Path(td_name) / "tampered-command-shape.json"
        write_pretty_json(tampered_path, tampered)
        tampered_result = subprocess.run(
            [sys.executable, "-B", "-S", VALIDATOR_REL, "--allow-checker-simulation", str(tampered_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, tampered_result.returncode != 0, "host-smoke validator must reject stale command_shape_sha256 digests")

        tampered = load_json(SUCCESS_SIM_REL)
        host_probes = tampered.get("host_probes", []) if isinstance(tampered.get("host_probes"), list) else []
        if host_probes and isinstance(host_probes[0], dict):
            host_probes[0]["observed_value"] = "Linux"
        tampered_path = Path(td_name) / "tampered-probe-value.json"
        write_pretty_json(tampered_path, tampered)
        tampered_result = subprocess.run(
            [sys.executable, "-B", "-S", VALIDATOR_REL, "--allow-checker-simulation", str(tampered_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, tampered_result.returncode != 0, "host-smoke validator must reject host probe observed_value drift")

        tampered = load_json(SUCCESS_SIM_REL)
        host_probes = tampered.get("host_probes", []) if isinstance(tampered.get("host_probes"), list) else []
        if host_probes and isinstance(host_probes[0], dict):
            host_probes[0]["observed_stdout_text"] = "FreeBSD\nextra\n"
        tampered_path = Path(td_name) / "tampered-probe-stdout.json"
        write_pretty_json(tampered_path, tampered)
        tampered_result = subprocess.run(
            [sys.executable, "-B", "-S", VALIDATOR_REL, "--allow-checker-simulation", str(tampered_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, tampered_result.returncode != 0, "host-smoke validator must reject host probe stdout replay drift")

        tampered = load_json(SUCCESS_SIM_REL)
        commands = tampered.get("commands", []) if isinstance(tampered.get("commands"), list) else []
        for row in commands:
            if isinstance(row, dict) and row.get("command_role") == "mdconfig-attach-readonly":
                row["observed_stdout_text"] = "md99\n"
        tampered_path = Path(td_name) / "tampered-mdconfig-stdout.json"
        write_pretty_json(tampered_path, tampered)
        tampered_result = subprocess.run(
            [sys.executable, "-B", "-S", VALIDATOR_REL, "--allow-checker-simulation", str(tampered_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, tampered_result.returncode != 0, "host-smoke validator must reject mdconfig authority-token stdout replay drift")

        tampered = load_json(SUCCESS_SIM_REL)
        commands = tampered.get("commands", []) if isinstance(tampered.get("commands"), list) else []
        for row in commands:
            if isinstance(row, dict) and row.get("command_role") == "mdconfig-detach-before-worker":
                row["command"] = ["/sbin/mdconfig", "-d", "-u", "99"]
        tampered_path = Path(td_name) / "tampered-mdconfig-detach-target.json"
        write_pretty_json(tampered_path, tampered)
        tampered_result = subprocess.run(
            [sys.executable, "-B", "-S", VALIDATOR_REL, "--allow-checker-simulation", str(tampered_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, tampered_result.returncode != 0, "host-smoke validator must reject detach commands not bound to the mdconfig authority token")

    text = validator.read_text(encoding="utf-8", errors="replace")
    for token in [
        "Default mode is intentionally strict",
        "EXPECTED_COMMAND_ROLES",
        "EXPECTED_HOST_PROBE_ROLES",
        "checker_only",
        "real host proof must observe FreeBSD",
        "real host proof must carry uname -s FreeBSD probe",
        "kern.features.security_capability_mode=1",
        "host_probe_capsicum_feature_enabled",
        "--allow-checker-simulation",
        "--allow-refusal",
        "--allow-failed",
        "worker input digest must match safe-capture digest",
        "fixture_copy.{key}",
        "worker_source_copy.{key}",
        "host_smoke must prove mdconfig detach before worker",
        "canonical_digest(command)",
        "command_shape_sha256 must match canonical argv digest",
        "observed_stdout_text",
        "stdout_sha256 must replay observed_stdout_text",
        "observed_value must match host",
        "AUTHORITY_TOKEN_VALUE_KEYS",
        "host_smoke.observed_md_unit",
        "mdconfig authority token must match",
        "detach command must target the mdconfig-emitted unit number",
        "runner_contract_version must explicitly identify",
        "cube_cut_version must identify",
        "generated_for_version must remain a runner-contract alias",
    ]:
        require(errors, token in text, f"{VALIDATOR_REL} missing token {token!r}")
    return errors


def check_runner_source() -> list[str]:
    errors: list[str] = []
    text = RUNNER.read_text(encoding="utf-8", errors="replace")
    required = [
        "--run-host-smoke",
        "platform.system() != \"FreeBSD\"",
        "os.geteuid() != 0",
        "explicit-host-smoke-flag-required",
        "/usr/sbin/makefs",
        "/sbin/mdconfig",
        "-o", "readonly",
        "/usr/sbin/fstyp",
        "/sbin/mount",
        "MOUNT_OPTIONS",
        "/sbin/umount",
        "safe_capture.capture_regular_member",
        "subprocess.run",
        "pass_fds=(3, 4, 5)",
        "env={}",
        "env=HOST_COMMAND_ENV",
        "HOST_COMMAND_ENV_POLICY",
        "host_command_env_policy",
        "parse_fstyp_ufs_stdout",
        "_single_line_command_token",
        "worker-empty-cwd",
        "private-empty-directory-not-media-not-repo",
        "extra_fds_closed_before_cap_enter",
        "extra_fd_canary_observed_before_closefrom",
        "fd5_canary_source",
        "broker-nonmedia-canary-not-source-media",
        "worker_source_sha256",
        "worker_source_copy_policy",
        "inspect_worker_source",
        "copy_worker_source_verified",
        "worker-source-copy",
        "compile_uses_private_worker_source_copy",
        "sha256_file(C_WORKER_SOURCE)",
        "HostSmokeFailure",
        "failure_paths_are_receipt_shaped",
        "cleanup_attempted_after_mdconfig_attach",
        "simulated_host_commands",
        "worker_reported_fd5_canary_observed_before_closefrom",
        "worker_stdout_stderr_bytes_zero",
        "work-dir-must-not-already-exist",
        "launcher_restored_parent_fd_slots",
        "fd_slots.FdSlotGuard",
        "slot_guard.restore()",
        "MD_UNIT_RE",
        "MD_UNIT_NORMALIZED_RE",
        "md_unit_detach_number",
        "_single_line_command_token",
        "parse_fstyp_ufs_stdout",
        "observed_md_unit",
        "host_smoke.observed_md_unit",
        "authority_tokens_replayed_from_stdout",
        "redact_host_smoke_receipt",
        "command_shape_sha256",
        "PRIVATE_WORK_ROOT_TOKEN",
        "inspect_fixture_root",
        "fixture-root-outside-allowed-base",
        "copy_fixture_tree_verified",
        "fixture_tree_manifest",
        "collect_host_probes",
        "HOST_PROBE_COMMANDS",
        "kern.features.security_capability_mode",
        "kern.features.security_capabilities",
        "load_json_strict_text",
        "canonical_json_bytes(entries)",
        "fixture_source_stable_during_copy",
        "fixture_copy_matches_source_manifest",
        "manifest_includes_directories",
        "directory_count",
        "no_host_commands_after_fixture_copy_failure",
        "RUNNER_CONTRACT_VERSION",
        "CURRENT_CUBE_CUT_VERSION",
    ]
    for token in required:
        require(errors, token in text, f"{RUNNER_REL} missing token {token!r}")
    require(errors, "shutil.rmtree(" not in text, "host smoke runner must not recursively delete caller paths")

    launcher_text = (ROOT / "tools" / "removable_media_fd_slot_launcher.py").read_text(encoding="utf-8", errors="replace")
    for token in ["preexisting_parent_fd_inheritable_flags_preserved", "os.set_inheritable(fd, original_inheritable)", "F_DUPFD_CLOEXEC"]:
        require(errors, token in launcher_text, f"tools/removable_media_fd_slot_launcher.py missing token {token!r}")
    return errors


def check_launcher_fd_slot_regression() -> list[str]:
    """Prove run_worker does not leave delegated fd 3/4/5 open in the parent.

    The bug this guards against is subtle: if the launcher opens the preserved
    object and receives fd 3, then saves fd 3, it has saved the newly delegated
    authority rather than a pre-existing parent slot.  The post-worker parent can
    then retain fd 3/4/5 even while the receipt says slots were restored.
    """
    errors: list[str] = []
    runner = load_runner_module()
    with tempfile.TemporaryDirectory(prefix="derivebsd-host-smoke-fdslot-regression-") as td_name:
        td = Path(td_name)
        worker = td / "dummy-worker.py"
        worker.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os\n"
            "payload = {\"result\": \"passed\", \"checker_only_fdslot_regression_worker\": True}\n"
            "os.write(4, (json.dumps(payload, sort_keys=True) + \"\\n\").encode(\"utf-8\"))\n",
            encoding="utf-8",
        )
        worker.chmod(0o700)
        preserved = td / "preserved.bin"
        preserved.write_bytes(b"preserved object for fd slot regression\n")
        output = td / "worker-output.json"
        canary = td / "canary.txt"
        canary.write_text("non-media canary\n", encoding="utf-8")
        outer = runner.fd_slots.FdSlotGuard(runner.fd_slots.TARGET_FDS).save_and_clear()
        try:
            result = runner.run_worker(worker, preserved, output, canary, td / "worker-cwd")
            require(errors, result.get("launcher_fd_slot_policy") == "duplicate-target-fds-above-delegated-range-before-clearing-slots", "run_worker must report save-before-open fd-slot policy")
            require(errors, result.get("launcher_restored_parent_fd_slots") is True, "run_worker must report parent fd slot restoration")
            leaked = [fd for fd in runner.fd_slots.TARGET_FDS if runner.fd_slots.fd_identity(fd).get("open") is True]
            require(errors, leaked == [], f"run_worker leaked delegated fd slots into parent after child exit: {leaked}")
        finally:
            outer.restore()
    return errors




def check_fd_slot_guard_preserves_preexisting_target_slots_without_cross_dup() -> list[str]:
    """Prove saving fd 3/4/5 cannot allocate backups inside another target slot.

    A naive os.dup(3) while fd 4 is closed can return fd 4, so a later save of
    fd 4 actually saves the backup of fd 3.  The fixed helper duplicates all
    target fds above the delegated range before closing any target slot.
    """
    errors: list[str] = []
    runner = load_runner_module()
    fd_slots = runner.fd_slots
    outer = fd_slots.FdSlotGuard(fd_slots.TARGET_FDS).save_and_clear()
    opened: list[int] = []
    try:
        with tempfile.TemporaryDirectory(prefix="derivebsd-fdslot-crossdup-") as td_name:
            td = Path(td_name)
            originals: dict[int, dict[str, Any]] = {}
            for fd, inheritable in zip(fd_slots.TARGET_FDS, [False, True, False]):
                path = td / f"parent-slot-{fd}.txt"
                path.write_text(f"parent slot {fd}\n", encoding="utf-8")
                src = os.open(path, os.O_RDONLY)
                opened.append(src)
                os.dup2(src, fd)
                os.set_inheritable(fd, inheritable)
                originals[fd] = fd_slots.fd_identity(fd)
            guard = fd_slots.FdSlotGuard(fd_slots.TARGET_FDS).save_and_clear()
            try:
                require(errors, guard.saved_and_cleared is True, "fd slot guard must save and clear")
                require(errors, all(fd_slots.fd_identity(fd).get("open") is False for fd in fd_slots.TARGET_FDS), "target fds must be closed after save_and_clear")
                require(errors, all((saved is None or saved >= fd_slots.SAVE_DUP_MIN_FD) for saved in guard.saved_fd_numbers.values()), "backup duplicates must be allocated outside target fd range")
            finally:
                guard.restore()
            evidence = guard.evidence()
            require(errors, evidence.get("saved_duplicates_outside_target_fds") is True, "evidence must report out-of-band saved duplicates")
            require(errors, evidence.get("preexisting_parent_fd_slots_preserved") is True, "pre-existing target slots must be restored exactly")
            require(errors, evidence.get("preexisting_parent_fd_inheritable_flags_preserved") is True, "pre-existing target slot inheritability must be restored")
            for fd in fd_slots.TARGET_FDS:
                require(errors, fd_slots.identities_match(originals[fd], fd_slots.fd_identity(fd)), f"fd {fd} identity/inheritability changed across save/restore")
    finally:
        for fd in opened:
            try:
                os.close(fd)
            except OSError:
                pass
        outer.restore()
    return errors


def check_host_smoke_receipts_are_path_redacted(*objs: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for obj in objs:
        label = str(obj.get("result")) + ":" + str(obj.get("smoke_id"))
        text = json.dumps(obj, sort_keys=True)
        require(errors, "/tmp/derivebsd-host-smoke-" not in text, f"{label} must not leak transient host-smoke /tmp work roots")
        require(errors, "$PRIVATE_WORK_ROOT" in text or obj.get("result") == "refused", f"{label} must use stable $PRIVATE_WORK_ROOT command redaction")
        for cmd in obj.get("host_probes", []) if isinstance(obj.get("host_probes"), list) else []:
            if isinstance(cmd, dict):
                require(errors, cmd.get("private_work_root_redacted") is True, f"{label} host probe must report private work-root redaction")
                require(errors, isinstance(cmd.get("command_shape_sha256"), str) and cmd.get("command_shape_sha256", "").startswith("sha256:"), f"{label} host probe must carry command_shape_sha256")
        for cmd in obj.get("commands", []) if isinstance(obj.get("commands"), list) else []:
            if isinstance(cmd, dict):
                require(errors, cmd.get("private_work_root_redacted") is True, f"{label} command must report private work-root redaction")
                require(errors, isinstance(cmd.get("command_shape_sha256"), str) and cmd.get("command_shape_sha256", "").startswith("sha256:"), f"{label} command must carry command_shape_sha256")
        cleanup = obj.get("cleanup", {}) if isinstance(obj.get("cleanup"), dict) else {}
        for cmd in cleanup.get("commands", []) if isinstance(cleanup.get("commands"), list) else []:
            if isinstance(cmd, dict):
                require(errors, cmd.get("private_work_root_redacted") is True, f"{label} cleanup command must report private work-root redaction")
                require(errors, isinstance(cmd.get("command_shape_sha256"), str) and cmd.get("command_shape_sha256", "").startswith("sha256:"), f"{label} cleanup command must carry command_shape_sha256")
    return errors


def check_mdconfig_unit_parser_strictness() -> list[str]:
    """Guard the real host device path and detach target parser."""
    errors: list[str] = []
    runner = load_runner_module()
    accepted = {
        "0\n": "md0",
        "42\n": "md42",
        "md42\n": "md42",
        "/dev/md42\n": "md42",
    }
    for stdout, expected in accepted.items():
        try:
            parsed = runner.parse_md_unit(stdout)
        except Exception as exc:  # noqa: BLE001 - checker should report all cases
            errors.append(f"parse_md_unit unexpectedly rejected {stdout!r}: {exc}")
            continue
        require(errors, parsed == expected, f"parse_md_unit({stdout!r}) returned {parsed!r}, expected {expected!r}")
        require(errors, runner.md_unit_detach_number(parsed) == expected.removeprefix("md"), f"detach number for {parsed!r} must be numeric")
    rejected = [
        "",
        "md",
        "mdx",
        "md42 extra",
        "/dev/md42 extra",
        "/dev/../md42",
        "../md42",
        "md42/../zero",
        "md42;rm -rf /",
        "md 42",
        "/dev/md",
        "noise ignored by taking last line\nmd7\n",
    ]
    for stdout in rejected:
        try:
            runner.parse_md_unit(stdout)
        except Exception:
            pass
        else:
            errors.append(f"parse_md_unit must reject unsafe mdconfig output {stdout!r}")
    for unit in ["md", "mdx", "md42/../zero", "/dev/md42", "42", "md42 extra"]:
        try:
            runner.md_unit_detach_number(unit)
        except Exception:
            pass
        else:
            errors.append(f"md_unit_detach_number must reject unsafe normalized unit {unit!r}")
    try:
        require(errors, runner.parse_fstyp_ufs_stdout("ufs\n") == "ufs", "fstyp parser must accept canonical single-line ufs")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"fstyp parser unexpectedly rejected canonical ufs: {exc}")
    for stdout in ["", "ufs\nextra", "zfs\n", "noise\nufs\n", "ufs extra\n"]:
        try:
            runner.parse_fstyp_ufs_stdout(stdout)
        except Exception:
            pass
        else:
            errors.append(f"parse_fstyp_ufs_stdout must reject unsafe fstyp output {stdout!r}")
    return errors


def check_fstyp_stdout_parser_strictness() -> list[str]:
    """Guard the real host filesystem-type authority parser."""
    errors: list[str] = []
    runner = load_runner_module()
    for stdout in ["ufs\n", "ufs"]:
        try:
            parsed = runner.parse_fstyp_ufs_stdout(stdout)
        except Exception as exc:  # noqa: BLE001 - checker should report all cases
            errors.append(f"parse_fstyp_ufs_stdout unexpectedly rejected {stdout!r}: {exc}")
            continue
        require(errors, parsed == "ufs", f"parse_fstyp_ufs_stdout({stdout!r}) returned {parsed!r}, expected 'ufs'")
    rejected = [
        "",
        "ufs extra",
        "ufs\nufs",
        "zfs\n",
        "../ufs",
        "ufs;mount",
        "/dev/ufs",
    ]
    for stdout in rejected:
        try:
            runner.parse_fstyp_ufs_stdout(stdout)
        except Exception:
            pass
        else:
            errors.append(f"parse_fstyp_ufs_stdout must reject unsafe fstyp output {stdout!r}")
    return errors


def check_host_proof_collector_wrapper() -> list[str]:
    errors: list[str] = []
    path = ROOT / COLLECTOR_REL
    require(errors, path.exists(), f"missing {COLLECTOR_REL}")
    if not path.exists():
        return errors
    mode = path.stat().st_mode
    require(errors, bool(mode & 0o111), f"{COLLECTOR_REL} must be executable")
    text = path.read_text(encoding="utf-8", errors="replace")
    for token in [
        "set -eu",
        "--run-host-smoke",
        "validate_removable_media_local_fallback_host_smoke_receipt.py",
        "removable-media-local-freebsd-host-smoke.real-host.json",
        "python3",
        "-B",
        "-S",
        "sha256",
        "receipt=",
        "DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE",
        "guard_handoff_collision",
        "refusing to overwrite existing handoff file",
    ]:
        require(errors, token in text, f"{COLLECTOR_REL} missing token {token!r}")
    for banned in ["--allow-checker-simulation", "--allow-refusal", "--allow-failed", "rm -rf"]:
        require(errors, banned not in text, f"{COLLECTOR_REL} must not contain {banned!r}")

    with tempfile.TemporaryDirectory(prefix="derivebsd-host-proof-handoff-collision-") as td_name:
        tmp = Path(td_name)
        handoff = tmp / "handoff"
        handoff.mkdir()
        (handoff / "receipt.json").write_text("existing scarce receipt\n", encoding="utf-8")
        proc = subprocess.run(
            [str(path), str(tmp / "out.json"), str(tmp / "bundle.json"), str(handoff)],
            cwd=ROOT,
            env={**os.environ, "PYTHON": sys.executable},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        require(errors, proc.returncode == 2, "collector must reject a reused handoff directory before host preflight")
        combined = proc.stdout + proc.stderr
        require(errors, "refusing to overwrite existing handoff file" in combined, "handoff collision refusal must name the overwrite hazard")
        require(errors, "requires FreeBSD host" not in combined, "handoff collision guard must run before FreeBSD/root preflight")
        require(errors, (handoff / "receipt.json").read_text(encoding="utf-8") == "existing scarce receipt\n", "handoff collision guard must not overwrite existing receipt.json")
    return errors


def check_visible_fixture_pdf() -> list[str]:
    """Guard the boring positive PDF fixture from regressing into blank or hostile bytes."""
    errors: list[str] = []
    path = ROOT / VALID_VISIBLE_FIXTURE_REL
    require(errors, path.exists(), f"missing {VALID_VISIBLE_FIXTURE_REL}")
    if not path.exists():
        return errors
    st = path.lstat()
    require(errors, not stat.S_ISLNK(st.st_mode), f"{VALID_VISIBLE_FIXTURE_REL} must not be a symlink")
    require(errors, stat.S_ISREG(st.st_mode), f"{VALID_VISIBLE_FIXTURE_REL} must be a regular file")
    data = path.read_bytes()
    require(errors, len(data) == VALID_VISIBLE_FIXTURE_SIZE, f"{VALID_VISIBLE_FIXTURE_REL} size must stay digest-bound and boring")
    require(errors, sha256_bytes(data) == VALID_VISIBLE_FIXTURE_SHA256, f"{VALID_VISIBLE_FIXTURE_REL} digest must match refreshed visible fixture")
    require(errors, data.startswith(b"%PDF-"), f"{VALID_VISIBLE_FIXTURE_REL} must be a PDF header fixture")
    for token in [b"/Resources", b"/Font", b"/F1", b"DeriveBSD removable-media harness fixture", b"Valid tiny PDF: visible, deterministic, boring."]:
        require(errors, token in data, f"{VALID_VISIBLE_FIXTURE_REL} missing visible PDF token {token!r}")
    return errors

def check_docs() -> list[str]:
    errors: list[str] = []
    docs = {
        "README.md": [VERSION, CURRENT_CUBE_CUT_VERSION, "runner_contract_version", "cube_cut_version", "FreeBSD host-smoke", "host probes", "collect_removable_media_local_fallback_host_proof.sh", "check_removable_media_local_fallback_freebsd_host_smoke_runner.py", "validate_removable_media_local_fallback_host_smoke_receipt.py", "removable.media.local.freebsd.host.smoke.receipt"],
        "docs/00-index.md": [VERSION, CURRENT_CUBE_CUT_VERSION, "runner_contract_version", "cube_cut_version", "FreeBSD host-smoke receipts", "host probes", "collect_removable_media_local_fallback_host_proof.sh", "validate_removable_media_local_fallback_host_smoke_receipt.py"],
        "docs/99-llm-runbook.md": ["check_removable_media_local_fallback_freebsd_host_smoke_runner.py", "run_removable_media_local_fallback_host_smoke.py"],
        DOC_REL: ["makefs", "mdconfig", "runner_contract_version", "cube_cut_version", "host_osreldate_minimum", "host_release_floor", "host_target_matrix_id", "host_target_tier", "15.1-RELEASE", "real-host proof theatre gate", "valid visible deterministic PDF", "fstyp", "umount", "fd-5", "non-freebsd-host", "receipt-shaped failure", "success simulation", "fixture admission", "source-stable fixture copy", "directory-aware manifest", "private worker-source copy", "strict fstyp output", "mdconfig authority token", "sanitized host-command environment", "host probes", "kern.features.security_capability_mode", "collect_removable_media_local_fallback_host_proof.sh", "empty environment", "private non-media cwd", "validate_removable_media_local_fallback_host_smoke_receipt.py", "--allow-checker-simulation", "host_smoke.worker_launched", "write_pretty_json()", "removable.media.local.freebsd.host.smoke.receipt", "Last updated:"],
    }
    for rel, tokens in docs.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            require(errors, token in text, f"{rel} missing token {token!r}")
    return errors


def main() -> int:
    if not RUNNER.exists():
        print("FreeBSD host smoke runner check FAILED.")
        print(f"- missing {RUNNER_REL}")
        return 1
    rc, refusal = run_refusal()
    failure_sim = run_failure_simulation()
    fstyp_output_failure_sim = run_fstyp_output_failure_simulation()
    fixture_failure_sim = run_fixture_admission_failure_simulation()
    fixture_copy_change_sim = run_fixture_copy_change_regression()
    fixture_copy_directory_change_sim = run_fixture_copy_directory_change_regression()
    worker_source_copy_change_sim = run_worker_source_copy_change_regression()
    success_sim = run_success_simulation()
    errors = (
        check_refusal_receipt(refusal, rc)
        + check_host_smoke_receipt_schema_surface(refusal, success_sim, failure_sim, fstyp_output_failure_sim, fixture_failure_sim)
        + check_receipt_validator()
        + check_failure_simulation(failure_sim)
        + check_fstyp_output_failure_simulation(fstyp_output_failure_sim)
        + check_fixture_admission_failure_simulation(fixture_failure_sim)
        + check_fixture_copy_change_regression(fixture_copy_change_sim)
        + check_fixture_copy_directory_change_regression(fixture_copy_directory_change_sim)
        + check_worker_source_copy_change_regression(worker_source_copy_change_sim)
        + check_success_simulation(success_sim)
        + check_runner_source()
        + check_launcher_fd_slot_regression()
        + check_fd_slot_guard_preserves_preexisting_target_slots_without_cross_dup()
        + check_mdconfig_unit_parser_strictness()
        + check_fstyp_stdout_parser_strictness()
        + check_host_smoke_receipts_are_path_redacted(success_sim, failure_sim, fstyp_output_failure_sim, fixture_failure_sim)
        + check_host_proof_collector_wrapper()
        + check_visible_fixture_pdf()
        + check_docs()
    )
    if errors:
        print("FreeBSD host smoke runner check FAILED.")
        for err in errors:
            print("-", err)
        return 1
    print("FreeBSD host smoke runner check OK")
    print("Host smoke: refuses in Linux cloudtainer; success/failure/fstyp-output/fixture-admission/copy-change simulations exercise receipt-shaped command order, cleanup, fd5 observation, strict command-output parsing, host probes, sanitized host-command environment, fixture admission, directory-aware source-stable fixture copy, private worker-source copy, and input digest binding without claiming real FreeBSD execution")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
