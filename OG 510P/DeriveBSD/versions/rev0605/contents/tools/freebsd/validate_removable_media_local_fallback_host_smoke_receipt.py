#!/usr/bin/env python3
"""Validate a removable-media FreeBSD host-smoke receipt.

Default mode is intentionally strict: exit 0 only for a non-simulated real
FreeBSD passed receipt.  Checker simulations and Linux refusal receipts are
useful archive evidence, but they are not host proof unless the caller opts into
those modes explicitly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from cube_digest_lib import CanonicalJsonError, canonical_digest, load_json_strict_text  # noqa: E402
from freebsd import host_proof_contract as contract  # noqa: E402

KIND = "removable.media.local.freebsd.host.smoke.receipt"
SCHEMA_VERSION = "0.1"
RUNNER_CONTRACT_VERSION = contract.RUNNER_CONTRACT_VERSION
CURRENT_CUBE_CUT_VERSION = contract.CURRENT_CUBE_CUT_VERSION
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
HOST_TARGET_UNSUPPORTED_TIER = contract.HOST_TARGET_UNSUPPORTED_TIER
SUPPORTED_HOST_TARGET_TIERS = {HOST_TARGET_PRIMARY_TIER, HOST_TARGET_LEGACY_TIER}
EXPECTED_COMMAND_ROLES = [
    "compile-worker",
    "makefs-image",
    "mdconfig-attach-readonly",
    "fstyp-verify-ufs",
    "mount-readonly-untrusted",
    "umount-before-worker",
    "mdconfig-detach-before-worker",
]
EXPECTED_HOST_PROBE_ROLES = [
    "host-probe-uname-system",
    "host-probe-uname-release",
    "host-probe-uname-machine",
    "host-probe-effective-uid",
    "host-probe-osreldate",
    "host-probe-capsicum-capability-mode",
    "host-probe-capsicum-capabilities",
]
EXPECTED_MOUNT_OPTIONS = ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"]
HOST_COMMAND_ENV_KEYS = ["LC_ALL", "PATH"]

HOST_PROBE_VALUE_KEYS = {
    "host-probe-uname-system": "host_probe_observed_system",
    "host-probe-uname-release": "host_probe_uname_release",
    "host-probe-uname-machine": "host_probe_uname_machine",
    "host-probe-effective-uid": "host_probe_effective_uid",
    "host-probe-osreldate": "host_probe_osreldate",
    "host-probe-capsicum-capability-mode": "host_probe_capsicum_capability_mode",
    "host-probe-capsicum-capabilities": "host_probe_capsicum_capabilities",
}

AUTHORITY_TOKEN_VALUE_KEYS = {
    "mdconfig-attach-readonly": "host_smoke.observed_md_unit",
    "fstyp-verify-ufs": "host_smoke.observed_fstyp",
}
MD_UNIT_RE = re.compile(r"md[0-9]+")


def _require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def _dict(obj: Any) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _list(obj: Any) -> list[Any]:
    return obj if isinstance(obj, list) else []


def _has_checker_only_true(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if "checker_only" in str(key) and child is True:
                return True
            if _has_checker_only_true(child):
                return True
    elif isinstance(value, list):
        return any(_has_checker_only_true(child) for child in value)
    return False


def _command_row_common_errors(row: dict[str, Any], idx: int, label: str) -> list[str]:
    errors: list[str] = []
    command = row.get("command")
    _require(errors, isinstance(command, list) and bool(command), f"{label} {idx} must carry argv")
    _require(errors, isinstance(command, list) and all(isinstance(part, str) for part in command), f"{label} {idx} argv entries must be strings")
    _require(errors, row.get("return_code") == 0, f"{label} {idx} must return 0")
    _require(errors, row.get("timed_out") is False, f"{label} {idx} must not time out")
    _require(errors, row.get("host_command_env_policy") == "sanitized-locale-and-path-only", f"{label} {idx} must bind sanitized host-command env policy")
    _require(errors, row.get("host_command_env_keys") == HOST_COMMAND_ENV_KEYS, f"{label} {idx} must bind host env keys {HOST_COMMAND_ENV_KEYS!r}")
    _require(errors, row.get("host_command_env_lc_all") == "C", f"{label} {idx} must bind LC_ALL=C")
    _require(errors, row.get("private_work_root_redacted") is True, f"{label} {idx} must report private work-root redaction")
    shape = row.get("command_shape_sha256")
    _require(errors, isinstance(shape, str) and shape.startswith("sha256:"), f"{label} {idx} must carry command_shape_sha256")
    if isinstance(command, list) and all(isinstance(part, str) for part in command):
        _require(errors, shape == canonical_digest(command), f"{label} {idx} command_shape_sha256 must match canonical argv digest")
    return errors


def _sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _probe_errors(probes: list[Any], host: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    roles = []
    for idx, row_obj in enumerate(probes):
        row = _dict(row_obj)
        role = row.get("command_role")
        roles.append(role)
        errors.extend(_command_row_common_errors(row, idx, "host probe"))
        expected_key = HOST_PROBE_VALUE_KEYS.get(role) if isinstance(role, str) else None
        observed_value = row.get("observed_value")
        stdout_text = row.get("observed_stdout_text")
        _require(errors, expected_key is not None, f"host probe {idx} must use a known host-probe role")
        _require(errors, row.get("observed_value_key") == expected_key, f"host probe {idx} must bind the host value key for {role!r}")
        _require(errors, isinstance(observed_value, str) and bool(observed_value), f"host probe {idx} must carry observed_value")
        _require(errors, isinstance(stdout_text, str), f"host probe {idx} must carry observed_stdout_text for digest replay")
        if isinstance(stdout_text, str):
            _require(errors, row.get("stdout_sha256") == _sha256_text(stdout_text), f"host probe {idx} stdout_sha256 must replay observed_stdout_text")
            _require(errors, stdout_text.strip() == observed_value, f"host probe {idx} observed_value must equal stripped stdout")
            _require(errors, "\n" not in stdout_text.strip() and "\r" not in stdout_text.strip(), f"host probe {idx} stdout must be a single token line")
        if expected_key is not None:
            _require(errors, host.get(expected_key) == observed_value, f"host probe {idx} observed_value must match host.{expected_key}")
    _require(errors, roles == EXPECTED_HOST_PROBE_ROLES, f"host probe role order must be {EXPECTED_HOST_PROBE_ROLES!r}; saw {roles!r}")
    return errors

def _authority_token_errors(row: dict[str, Any], idx: int, host_smoke: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    role = row.get("command_role")
    expected_key = AUTHORITY_TOKEN_VALUE_KEYS.get(role) if isinstance(role, str) else None
    if expected_key is None:
        return errors
    observed_value = row.get("observed_value")
    stdout_text = row.get("observed_stdout_text")
    _require(errors, row.get("observed_value_key") == expected_key, f"command {idx} must bind observed_value_key {expected_key!r}")
    _require(errors, isinstance(observed_value, str) and bool(observed_value), f"command {idx} must carry observed authority token")
    _require(errors, isinstance(stdout_text, str), f"command {idx} must carry observed_stdout_text for authority-token replay")
    if isinstance(stdout_text, str):
        _require(errors, row.get("stdout_sha256") == _sha256_text(stdout_text), f"command {idx} stdout_sha256 must replay observed_stdout_text")
        _require(errors, stdout_text.strip() == observed_value, f"command {idx} observed_value must equal stripped stdout")
        _require(errors, "\n" not in stdout_text.strip() and "\r" not in stdout_text.strip(), f"command {idx} authority stdout must be a single token line")
    if role == "mdconfig-attach-readonly":
        _require(errors, isinstance(observed_value, str) and MD_UNIT_RE.fullmatch(observed_value) is not None, "mdconfig authority token must be a normalized mdN unit")
        _require(errors, host_smoke.get("observed_md_unit") == observed_value, "mdconfig authority token must match host_smoke.observed_md_unit")
    elif role == "fstyp-verify-ufs":
        _require(errors, observed_value == "ufs", "fstyp authority token must be ufs")
        _require(errors, host_smoke.get("observed_fstyp") == observed_value, "fstyp authority token must match host_smoke.observed_fstyp")
    return errors


def _command_errors(commands: list[Any], host_smoke: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    roles = []
    rows_by_role: dict[str, dict[str, Any]] = {}
    for idx, row_obj in enumerate(commands):
        row = _dict(row_obj)
        role = row.get("command_role")
        roles.append(role)
        if isinstance(role, str):
            rows_by_role[role] = row
        errors.extend(_command_row_common_errors(row, idx, "command"))
        errors.extend(_authority_token_errors(row, idx, host_smoke))
    _require(errors, roles == EXPECTED_COMMAND_ROLES, f"command role order must be {EXPECTED_COMMAND_ROLES!r}; saw {roles!r}")
    attach = rows_by_role.get("mdconfig-attach-readonly", {})
    fstyp = rows_by_role.get("fstyp-verify-ufs", {})
    mount = rows_by_role.get("mount-readonly-untrusted", {})
    detach = rows_by_role.get("mdconfig-detach-before-worker", {})
    md_unit = attach.get("observed_value")
    if isinstance(md_unit, str) and MD_UNIT_RE.fullmatch(md_unit):
        expected_device = f"/dev/{md_unit}"
        _require(errors, fstyp.get("command") == ["/usr/sbin/fstyp", expected_device], "fstyp command must verify the mdconfig-emitted device")
        _require(errors, isinstance(mount.get("command"), list) and expected_device in mount.get("command", []), "mount command must use the mdconfig-emitted device")
        _require(errors, detach.get("command") == ["/sbin/mdconfig", "-d", "-u", md_unit.removeprefix("md")], "detach command must target the mdconfig-emitted unit number")
    return errors


def _common_errors(obj: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _require(errors, obj.get("kind") == KIND, "wrong host-smoke receipt kind")
    _require(errors, obj.get("schema_version") == SCHEMA_VERSION, "wrong host-smoke schema_version")
    _require(errors, isinstance(obj.get("smoke_id"), str) and bool(obj.get("smoke_id")), "smoke_id must be present")
    _require(errors, obj.get("generated_for_version") == RUNNER_CONTRACT_VERSION, "generated_for_version must identify the host-smoke runner contract")
    _require(errors, obj.get("runner_contract_version") == RUNNER_CONTRACT_VERSION, "runner_contract_version must explicitly identify the host-smoke runner contract")
    _require(errors, obj.get("cube_cut_version") == CURRENT_CUBE_CUT_VERSION, "cube_cut_version must identify the cube cut that emitted the receipt")
    _require(errors, obj.get("generated_for_version") == obj.get("runner_contract_version"), "generated_for_version must remain a runner-contract alias until the legacy field is retired")
    _require(errors, obj.get("cube_cut_version") != obj.get("runner_contract_version"), "cube_cut_version must not be confused with the runner contract version")
    _require(errors, isinstance(obj.get("generated_at_utc"), str) and obj.get("generated_at_utc", "").endswith("Z"), "generated_at_utc must be a UTC string")
    host = _dict(obj.get("host"))
    _require(errors, host.get("required_os") == "FreeBSD", "host.required_os must be FreeBSD")
    _require(errors, host.get("requires_root") is True, "host.requires_root must be true")
    scope = _dict(obj.get("scope"))
    _require(errors, scope.get("lane") == "removable-media-local-fallback", "scope.lane must bind removable-media local fallback")
    _require(errors, scope.get("fixture_root_allowed_base") == "fixtures/removable-media/local-fallback", "fixture root must be constrained to checked-in local-fallback fixtures")
    _require(errors, scope.get("fixture_root_admission_policy") == "checked-in-finite-symlink-free-regular-files-only-before-host-commands", "fixture admission policy must be explicit")
    _require(errors, scope.get("worker_source_copy_required_before_compile") is True, "worker source copy must be required before compile")
    _require(errors, scope.get("worker_source_copy_policy") == "copy-c-worker-source-into-private-work-root-and-verify-digest-before-compile", "worker source copy policy must bind private source compile")
    _require(errors, scope.get("host_command_env_policy") == "sanitized-locale-and-path-only", "scope must bind sanitized host-command environment")
    _require(errors, scope.get("host_command_env_keys") == HOST_COMMAND_ENV_KEYS, "scope must bind host env key list")
    _require(errors, scope.get("host_release_floor_policy") == HOST_RELEASE_FLOOR_POLICY, "scope must bind the host release floor policy")
    _require(errors, scope.get("host_release_floor") == SUPPORTED_FREEBSD_RELEASE_FLOOR, "scope must bind the supported FreeBSD release floor")
    _require(errors, scope.get("host_osreldate_minimum") == MIN_FREEBSD_OSRELDATE, "scope must bind the minimum supported kern.osreldate")
    _require(errors, scope.get("host_target_matrix_id") == HOST_TARGET_MATRIX_ID, "scope must bind the host target matrix id")
    _require(errors, scope.get("host_target_tier_policy") == HOST_TARGET_TIER_POLICY, "scope must bind the host target tier policy")
    _require(errors, scope.get("host_primary_release") == PRIMARY_FREEBSD_RELEASE, "scope must bind the primary FreeBSD release")
    _require(errors, scope.get("host_primary_release_channel") == PRIMARY_FREEBSD_RELEASE_CHANNEL, "scope must bind the primary FreeBSD release channel")
    _require(errors, scope.get("host_primary_osreldate_minimum") == PRIMARY_FREEBSD_OSRELDATE_MINIMUM, "scope must bind the primary FreeBSD kern.osreldate minimum")
    _require(errors, scope.get("mount_options") == EXPECTED_MOUNT_OPTIONS, "mount options must remain readonly/hardened/untrusted")
    _require(errors, scope.get("command_path_redaction_policy") == "replace-private-work-root-with-$PRIVATE_WORK_ROOT-in-receipts", "command path redaction policy must be present")
    workspace = _dict(obj.get("workspace"))
    _require(errors, workspace.get("runtime_work_root_policy") == "private-temp-work-root", "runtime work root must be private temp root")
    _require(errors, workspace.get("destructive_user_path_cleanup") is False, "receipt must not permit destructive user path cleanup")
    return errors


def _refusal_errors(obj: dict[str, Any]) -> list[str]:
    errors = _common_errors(obj)
    _require(errors, obj.get("result") == "refused", "refusal mode requires result=refused")
    _require(errors, obj.get("refusal_reason") in {"non-freebsd-host", "root-required", "explicit-host-smoke-flag-required", "work-dir-must-not-already-exist"}, "refusal reason must be one of the guarded pre-host-command reasons")
    _require(errors, _list(obj.get("host_probes")) == [], "refusal must not run host probes")
    _require(errors, _list(obj.get("commands")) == [], "refusal must not run host commands")
    cleanup = _dict(obj.get("cleanup"))
    _require(errors, _list(cleanup.get("commands")) == [], "refusal cleanup commands must be empty")
    inv = _dict(obj.get("invariants"))
    _require(errors, inv.get("no_host_commands_after_refusal") is True, "refusal invariant must prove no host commands")
    _require(errors, inv.get("no_mount_attempted_after_refusal") is True, "refusal invariant must prove no mount attempted")
    _require(errors, inv.get("no_worker_launch_after_refusal") is True, "refusal invariant must prove no worker launch")
    return errors


def _failed_errors(obj: dict[str, Any], *, allow_checker_simulation: bool) -> list[str]:
    errors = _common_errors(obj)
    _require(errors, obj.get("result") == "failed", "failed mode requires result=failed")
    _require(errors, obj.get("refusal_reason") is None, "failed receipt must not also be refusal")
    failure = _dict(obj.get("failure"))
    _require(errors, failure.get("receipt_shaped_instead_of_traceback") is True, "failure must be receipt-shaped")
    _require(errors, isinstance(failure.get("stage"), str) and bool(failure.get("stage")), "failure stage must be present")
    host_probes = _list(obj.get("host_probes"))
    if host_probes:
        errors.extend(_probe_errors(host_probes, _dict(obj.get("host"))))
    cleanup = _dict(obj.get("cleanup"))
    for idx, row_obj in enumerate(_list(cleanup.get("commands"))):
        row = _dict(row_obj)
        _require(errors, row.get("host_command_env_policy") == "sanitized-locale-and-path-only", f"cleanup command {idx} must bind sanitized host-command env policy")
        _require(errors, row.get("host_command_env_keys") == HOST_COMMAND_ENV_KEYS, f"cleanup command {idx} must bind host env keys")
    sim = _dict(obj.get("simulation"))
    if not allow_checker_simulation:
        _require(errors, sim.get("checker_only_host_command_simulation") is not True, "checker-only failure simulation is not real host proof")
        _require(errors, _has_checker_only_true(obj) is False, "checker-only nested evidence is not real host proof")
    return errors


def _passed_errors(obj: dict[str, Any], *, allow_checker_simulation: bool) -> list[str]:
    errors = _common_errors(obj)
    _require(errors, obj.get("result") == "passed", "real proof mode requires result=passed")
    _require(errors, obj.get("refusal_reason") is None, "passed receipt must not have a refusal reason")
    _require(errors, obj.get("failure") is None, "passed receipt must not carry failure details")
    host = _dict(obj.get("host"))
    sim = _dict(obj.get("simulation"))
    if not allow_checker_simulation:
        _require(errors, host.get("observed_system") == "FreeBSD", "real host proof must observe FreeBSD")
        _require(errors, host.get("cloudtainer_refusal_is_expected") is False, "real host proof must not be cloudtainer refusal evidence")
        _require(errors, sim.get("checker_only_host_command_simulation") is False, "real host proof must not be checker-only host-command simulation")
        _require(errors, sim.get("not_freebsd_host_proof") is False, "real host proof must not mark itself as non-FreeBSD proof")
        _require(errors, _has_checker_only_true(obj) is False, "real host proof must contain no checker_only=true nested evidence")
    host_probes = _list(obj.get("host_probes"))
    errors.extend(_probe_errors(host_probes, _dict(obj.get("host"))))
    if not allow_checker_simulation:
        _require(errors, host.get("host_probe_observed_system") == "FreeBSD", "real host proof must carry uname -s FreeBSD probe")
        _require(errors, isinstance(host.get("host_probe_uname_release"), str) and bool(host.get("host_probe_uname_release")), "real host proof must carry uname -r probe")
        _require(errors, isinstance(host.get("host_probe_uname_machine"), str) and bool(host.get("host_probe_uname_machine")), "real host proof must carry uname -m probe")
        _require(errors, host.get("host_probe_effective_uid") == "0", "real host proof must carry id -u == 0 probe")
        _require(errors, str(host.get("host_probe_osreldate", "")).isdigit(), "real host proof must carry numeric kern.osreldate probe")
        if str(host.get("host_probe_osreldate", "")).isdigit():
            _require(errors, int(str(host.get("host_probe_osreldate"))) >= MIN_FREEBSD_OSRELDATE, "real host proof kern.osreldate must meet the supported FreeBSD release floor")
        _require(errors, host.get("host_probe_capsicum_capability_mode") == "1", "real host proof must observe kern.features.security_capability_mode=1")
        _require(errors, host.get("host_probe_capsicum_capabilities") == "1", "real host proof must observe kern.features.security_capabilities=1")
    inv = _dict(obj.get("invariants"))
    if str(host.get("host_probe_osreldate", "")).isdigit():
        _require(errors, int(str(host.get("host_probe_osreldate"))) >= MIN_FREEBSD_OSRELDATE, "passed receipt kern.osreldate must meet the supported FreeBSD release floor")
    expected_tier = contract.classify_host_target(host.get("host_probe_uname_release"), host.get("host_probe_osreldate"))
    _require(errors, host.get("host_target_tier") == expected_tier, "passed receipt host_target_tier must match the shared target classifier")
    _require(errors, host.get("host_target_tier") in SUPPORTED_HOST_TARGET_TIERS, "passed receipt host_target_tier must be primary-production or supported-legacy-floor")
    _require(errors, inv.get("host_osreldate_meets_supported_floor") is True, "passed receipt must prove host_osreldate_meets_supported_floor")
    _require(errors, inv.get("host_target_tier_recorded") is True, "passed receipt must prove host_target_tier_recorded")
    host_smoke = _dict(obj.get("host_smoke"))
    _require(errors, host_smoke.get("host_target_tier") == host.get("host_target_tier"), "host_smoke.host_target_tier must mirror host.host_target_tier")
    _require(errors, host_smoke.get("host_target_matrix_id") == HOST_TARGET_MATRIX_ID, "host_smoke must bind the host target matrix id")
    errors.extend(_command_errors(_list(obj.get("commands")), host_smoke))
    cleanup = _dict(obj.get("cleanup"))
    _require(errors, _list(cleanup.get("commands")) == [], "successful smoke must not need cleanup commands")
    _require(errors, cleanup.get("attempted_umount_after_failure") is False, "successful smoke must not attempt failure umount cleanup")
    _require(errors, cleanup.get("attempted_mdconfig_detach_after_failure") is False, "successful smoke must not attempt failure mdconfig cleanup")

    fixture_copy = _dict(obj.get("fixture_copy"))
    for key in ["source_stable_since_admission", "source_stable_during_copy", "copy_matches_source_manifest", "checked_before_host_commands"]:
        _require(errors, fixture_copy.get(key) is True, f"fixture_copy.{key} must be true")
    _require(errors, fixture_copy.get("manifest_includes_directories") is True, "fixture manifest must include directories")

    worker_source_copy = _dict(obj.get("worker_source_copy"))
    for key in ["source_regular_file", "source_not_symlink", "source_stable_since_admission", "source_stable_during_copy", "copy_matches_source_digest", "compile_uses_private_source_copy", "checked_before_compile"]:
        _require(errors, worker_source_copy.get(key) is True, f"worker_source_copy.{key} must be true")

    _require(errors, isinstance(host_smoke.get("worker_binary_sha256"), str) and host_smoke.get("worker_binary_sha256", "").startswith("sha256:"), "host_smoke.worker_binary_sha256 must be sha256")
    _require(errors, host_smoke.get("observed_fstyp") == "ufs", "host_smoke must observe ufs before mount")
    _require(errors, isinstance(host_smoke.get("observed_md_unit"), str) and MD_UNIT_RE.fullmatch(host_smoke.get("observed_md_unit", "")) is not None, "host_smoke.observed_md_unit must bind the mdconfig authority token")
    _require(errors, isinstance(host_smoke.get("capture_digest"), str) and host_smoke.get("capture_digest", "").startswith("sha256:"), "host_smoke.capture_digest must be sha256")
    _require(errors, host_smoke.get("umounted_before_worker") is True, "host_smoke must prove umount before worker")
    _require(errors, host_smoke.get("mdconfig_detached_before_worker") is True, "host_smoke must prove mdconfig detach before worker")
    _require(errors, host_smoke.get("worker_launched") is True, "host_smoke must launch worker after detach")
    _require(errors, host_smoke.get("worker_env_policy") == "empty-environment", "worker environment must be empty")
    _require(errors, host_smoke.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo", "worker cwd must be private and non-media")
    worker = _dict(host_smoke.get("worker"))
    _require(errors, worker.get("return_code") == 0, "worker command must return 0")
    _require(errors, worker.get("timed_out") is False, "worker command must not time out")
    _require(errors, worker.get("stdout_bytes") == 0 and worker.get("stderr_bytes") == 0, "worker stdio must be empty")
    _require(errors, worker.get("worker_env_policy") == "empty-environment" and worker.get("worker_env_keys_passed") == [], "worker launch must pass empty environment")
    _require(errors, worker.get("worker_cwd_contains_media_tree") is False, "worker cwd must not contain mounted media tree")
    _require(errors, worker.get("launcher_restored_parent_fd_slots") is True, "launcher must restore parent fd slots")
    report = _dict(worker.get("output_report"))
    _require(errors, report.get("result") == "passed", "worker report must pass")
    _require(errors, report.get("capsicum_mode_entered") is True, "worker must report Capsicum mode entered")
    _require(errors, report.get("extra_fds_closed_before_cap_enter") is True, "worker must close extra fds before cap_enter")
    _require(errors, report.get("extra_fd_canary_observed_before_closefrom") is True, "worker must observe fd5 canary before closefrom")
    _require(errors, report.get("input_sha256") == host_smoke.get("capture_digest"), "worker input digest must match safe-capture digest")
    inv = _dict(obj.get("invariants"))
    for key in [
        "host_probes_collected_before_media_commands",
        "host_probe_observed_freebsd",
        "host_probe_observed_root_uid",
        "host_probe_capsicum_feature_enabled",
        "host_target_tier_recorded",
        "fixture_source_stable_during_copy",
        "fixture_copy_matches_source_manifest",
        "worker_source_copy_matches_digest",
        "compile_uses_private_worker_source_copy",
        "mdconfig_vnode_readonly_attach_used",
        "mdconfig_output_bound_to_mount_and_detach",
        "fstyp_observed_ufs_before_mount",
        "authority_tokens_replayed_from_stdout",
        "readonly_untrusted_mount_options_used",
        "safe_capture_verified_before_detach",
        "umount_completed_before_worker",
        "mdconfig_detach_completed_before_worker",
        "worker_executed_after_detach",
        "fd5_nonmedia_canary_passed_to_worker",
        "worker_reported_capsicum_mode_entered",
        "worker_reported_extra_fds_closed_before_cap_enter",
        "worker_reported_fd5_canary_observed_before_closefrom",
        "worker_input_sha256_matches_capture_digest",
        "worker_stdout_stderr_bytes_zero",
        "worker_environment_empty",
        "worker_cwd_private_not_media",
        "host_command_environment_sanitized",
        "failure_paths_are_receipt_shaped",
        "no_worker_launch_after_host_failure",
    ]:
        _require(errors, inv.get(key) is True, f"invariant {key} must be true")
    return errors


def validate_receipt(obj: dict[str, Any], *, allow_refusal: bool = False, allow_failed: bool = False, allow_checker_simulation: bool = False) -> list[str]:
    result = obj.get("result")
    if result == "passed":
        return _passed_errors(obj, allow_checker_simulation=allow_checker_simulation)
    if result == "refused":
        errors = _refusal_errors(obj)
        if not allow_refusal:
            errors.append("refused receipt is not accepted as host proof; pass --allow-refusal only for cloudtainer refusal evidence")
        return errors
    if result == "failed":
        errors = _failed_errors(obj, allow_checker_simulation=allow_checker_simulation)
        if not allow_failed:
            errors.append("failed receipt is not accepted as host proof; pass --allow-failed only for failure-path evidence")
        return errors
    return _common_errors(obj) + [f"unsupported result {result!r}"]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path, help="host-smoke receipt JSON to validate")
    parser.add_argument("--allow-refusal", action="store_true", help="accept guarded refusal receipts as non-proof evidence")
    parser.add_argument("--allow-failed", action="store_true", help="accept receipt-shaped failed receipts as non-proof evidence")
    parser.add_argument("--allow-checker-simulation", action="store_true", help="accept checker-only simulated success/failure receipts as non-proof evidence")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        obj = load_json_strict_text(args.receipt.read_text(encoding="utf-8"))
    except (OSError, CanonicalJsonError, json.JSONDecodeError) as exc:
        print("FreeBSD host-smoke receipt validation FAILED")
        print(f"- could not load receipt: {exc}")
        return 1
    if not isinstance(obj, dict):
        print("FreeBSD host-smoke receipt validation FAILED")
        print("- receipt root must be a JSON object")
        return 1
    errors = validate_receipt(
        obj,
        allow_refusal=args.allow_refusal,
        allow_failed=args.allow_failed,
        allow_checker_simulation=args.allow_checker_simulation,
    )
    if errors:
        print("FreeBSD host-smoke receipt validation FAILED")
        for error in errors:
            print("-", error)
        return 1
    mode = "real-host-proof" if obj.get("result") == "passed" and not args.allow_checker_simulation else "non-proof-evidence"
    print(f"FreeBSD host-smoke receipt validation OK ({mode}; result={obj.get('result')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
