#!/usr/bin/env python3
"""FreeBSD-only host smoke runner for removable-media local fallback.

This is the first real-host proof lane, not a cloudtainer simulation.  It refuses
unless running on FreeBSD as root with --run-host-smoke, then creates a disposable
UFS image, attaches it with mdconfig, mounts it read-only/untrusted, captures one
regular file, unmounts/detaches, and execs the C Capsicum worker with fd 3/fd 4
plus a broker-owned fd-5 canary that the worker must close.

Failure paths are receipt-shaped: host command failures, safe-capture failures,
cleanup attempts, and worker launch failures must be recorded in the output JSON
instead of escaping as Python tracebacks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from cube_digest_lib import CanonicalJsonError, canonical_json_bytes, load_json_strict_text, pretty_json_text, write_pretty_json  # noqa: E402
from freebsd import host_proof_contract as contract  # noqa: E402

import removable_media_capsicum_worker_bridge as capsicum_bridge  # noqa: E402
import removable_media_fd_slot_launcher as fd_slots  # noqa: E402
import removable_media_safe_capture as safe_capture  # noqa: E402

VERSION = "2026-06-05r554"
RUNNER_CONTRACT_VERSION = VERSION
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
SMOKE_ID = "rm-local-freebsd-host-smoke-20260605-r554"
FIXED_GENERATED_AT = "2026-06-05T17:07:00Z"
DEFAULT_OUTPUT = ROOT / "validation" / "removable-media-local-freebsd-host-smoke.refusal.json"
DEFAULT_SELECTED_MEMBER = "invoice.pdf"
DEFAULT_FIXTURE_ROOT = ROOT / "fixtures" / "removable-media" / "local-fallback" / "exfat-card"
ALLOWED_FIXTURE_BASE = ROOT / "fixtures" / "removable-media" / "local-fallback"
MAX_FIXTURE_FILES = 64
MAX_FIXTURE_BYTES = 8 * 1024 * 1024
MOUNT_OPTIONS = ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"]
PRIVATE_WORK_ROOT_TOKEN = "$PRIVATE_WORK_ROOT"
HOST_COMMAND_ENV_POLICY = "sanitized-locale-and-path-only"
HOST_COMMAND_ENV = {"LC_ALL": "C", "PATH": "/sbin:/bin:/usr/sbin:/usr/bin"}
MD_UNIT_NUMBER_RE = re.compile(r"[0-9]+")
MD_UNIT_RE = re.compile(r"(?:/dev/)?md([0-9]+)")
MD_UNIT_NORMALIZED_RE = re.compile(r"md([0-9]+)")
C_WORKER_SOURCE = ROOT / capsicum_bridge.SOURCE_REL
WORKER_BINARY_NAME = capsicum_bridge.BINARY_BASENAME
WORKER_SOURCE_COPY_DIR = "worker-source"
WORKER_SOURCE_COPY_NAME = "rm_post_detach_capsicum_worker.c"

HOST_PROBE_COMMANDS = [
    (["/bin/uname", "-s"], "host-probe-uname-system"),
    (["/bin/uname", "-r"], "host-probe-uname-release"),
    (["/bin/uname", "-m"], "host-probe-uname-machine"),
    (["/usr/bin/id", "-u"], "host-probe-effective-uid"),
    (["/sbin/sysctl", "-n", "kern.osreldate"], "host-probe-osreldate"),
    (["/sbin/sysctl", "-n", "kern.features.security_capability_mode"], "host-probe-capsicum-capability-mode"),
    (["/sbin/sysctl", "-n", "kern.features.security_capabilities"], "host-probe-capsicum-capabilities"),
]
HOST_PROBE_VALUE_KEYS = {
    "host-probe-uname-system": "host_probe_observed_system",
    "host-probe-uname-release": "host_probe_uname_release",
    "host-probe-uname-machine": "host_probe_uname_machine",
    "host-probe-effective-uid": "host_probe_effective_uid",
    "host-probe-osreldate": "host_probe_osreldate",
    "host-probe-capsicum-capability-mode": "host_probe_capsicum_capability_mode",
    "host-probe-capsicum-capabilities": "host_probe_capsicum_capabilities",
}
CommandRunner = Callable[[list[str]], tuple[dict[str, Any], str, str]]
WorkerRunner = Callable[[Path, Path, Path, Path, Path], dict[str, Any]]


class HostSmokeFailure(Exception):
    """A host-smoke failure that should be written into the receipt."""

    def __init__(self, stage: str, message: str, *, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.stage = stage
        self.message = message
        self.details = details or {}


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
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


def redact_private_paths(value: Any, work_root: Path) -> Any:
    """Replace private host-smoke scratch paths with a stable receipt token."""
    root_text = work_root.as_posix()
    if isinstance(value, str):
        return value.replace(root_text, PRIVATE_WORK_ROOT_TOKEN)
    if isinstance(value, list):
        return [redact_private_paths(item, work_root) for item in value]
    if isinstance(value, dict):
        return {key: redact_private_paths(item, work_root) for key, item in value.items()}
    return value


def command_shape_digest(cmd: list[str]) -> str:
    payload = canonical_json_bytes(cmd)
    return sha256_bytes(payload)


def annotate_host_command_result(row: dict[str, Any]) -> dict[str, Any]:
    row["host_command_env_policy"] = HOST_COMMAND_ENV_POLICY
    row["host_command_env_keys"] = sorted(HOST_COMMAND_ENV)
    row["host_command_env_lc_all"] = HOST_COMMAND_ENV["LC_ALL"]
    return row


def redact_host_smoke_receipt(receipt: dict[str, Any], work_root: Path) -> dict[str, Any]:
    """Redact volatile work-root paths and add stable command-shape digests."""
    redacted = redact_private_paths(receipt, work_root)
    for command_list in (redacted.get("host_probes", []), redacted.get("commands", []), redacted.get("cleanup", {}).get("commands", [])):
        if not isinstance(command_list, list):
            continue
        for row in command_list:
            if isinstance(row, dict):
                cmd = row.get("command")
                if isinstance(cmd, list):
                    row["command_shape_sha256"] = command_shape_digest([str(part) for part in cmd])
                    row["private_work_root_redacted"] = work_root.as_posix() not in json.dumps(cmd, sort_keys=True)
    redacted.setdefault("workspace", {})["command_path_redaction_policy"] = "replace-private-work-root-with-$PRIVATE_WORK_ROOT-in-receipts"
    return redacted


def run_command(cmd: list[str], *, timeout_seconds: int = 60) -> tuple[dict[str, Any], str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env=HOST_COMMAND_ENV,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        result = {
            "command": cmd,
            "return_code": int(proc.returncode),
            "timed_out": False,
            **command_digest(stdout, stderr),
        }
        return result, stdout, stderr
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
            **command_digest(str(stdout), str(stderr)),
        }, str(stdout), str(stderr)


def base_receipt(*, generated_at_utc: str, work_root_policy: str = "private-temp-work-root", simulated_host_commands: bool = False) -> dict[str, Any]:
    return {
        "kind": "removable.media.local.freebsd.host.smoke.receipt",
        "schema_version": "0.1",
        "smoke_id": SMOKE_ID,
        "generated_for_version": VERSION,
        "runner_contract_version": RUNNER_CONTRACT_VERSION,
        "cube_cut_version": CURRENT_CUBE_CUT_VERSION,
        "generated_at_utc": generated_at_utc,
        "host": {
            "observed_system": platform.system(),
            "required_os": "FreeBSD",
            "requires_root": True,
            "cloudtainer_refusal_is_expected": platform.system() != "FreeBSD",
        },
        "scope": {
            "lane": "removable-media-local-fallback",
            "selected_member": DEFAULT_SELECTED_MEMBER,
            "fixture_root_allowed_base": ALLOWED_FIXTURE_BASE.relative_to(ROOT).as_posix(),
            "fixture_root_admission_policy": "checked-in-finite-symlink-free-regular-files-only-before-host-commands",
            "fixture_root_max_files": MAX_FIXTURE_FILES,
            "fixture_root_max_total_bytes": MAX_FIXTURE_BYTES,
            "fixture_manifest_policy": "regular-files-plus-directories-stable-before-makefs",
            "filesystem_image": "disposable-ufs-image-created-by-makefs",
            "device_attachment": "mdconfig-vnode-readonly",
            "mount_options": MOUNT_OPTIONS,
            "worker_bridge_id": capsicum_bridge.BRIDGE_ID,
            "worker_source": capsicum_bridge.SOURCE_REL,
            "worker_source_sha256": sha256_file(C_WORKER_SOURCE),
            "worker_source_copy_policy": "copy-c-worker-source-into-private-work-root-and-verify-digest-before-compile",
            "worker_source_copy_required_before_compile": True,
            "fd5_canary_source": "broker-nonmedia-canary-not-source-media",
            "command_path_redaction_policy": "replace-private-work-root-with-$PRIVATE_WORK_ROOT-in-receipts",
            "host_command_env_policy": HOST_COMMAND_ENV_POLICY,
            "host_command_env_keys": sorted(HOST_COMMAND_ENV),
            "host_release_floor_policy": HOST_RELEASE_FLOOR_POLICY,
            "host_release_floor": SUPPORTED_FREEBSD_RELEASE_FLOOR,
            "host_osreldate_minimum": MIN_FREEBSD_OSRELDATE,
            "host_target_matrix_id": HOST_TARGET_MATRIX_ID,
            "host_target_tier_policy": HOST_TARGET_TIER_POLICY,
            "host_primary_release": PRIMARY_FREEBSD_RELEASE,
            "host_primary_release_channel": PRIMARY_FREEBSD_RELEASE_CHANNEL,
            "host_primary_osreldate_minimum": PRIMARY_FREEBSD_OSRELDATE_MINIMUM,
        },
        "workspace": {
            "runtime_work_root_policy": work_root_policy,
            "destructive_user_path_cleanup": False,
        },
        "simulation": {
            "checker_only_host_command_simulation": simulated_host_commands,
            "not_freebsd_host_proof": simulated_host_commands,
        },
    }


def refusal_receipt(reason: str, *, generated_at_utc: str = FIXED_GENERATED_AT) -> dict[str, Any]:
    receipt = base_receipt(generated_at_utc=generated_at_utc)
    receipt.update({
        "result": "refused",
        "refusal_reason": reason,
        "host_probes": [],
        "commands": [],
        "cleanup": {
            "commands": [],
            "attempted_umount_after_failure": False,
            "attempted_mdconfig_detach_after_failure": False,
        },
        "invariants": {
            "no_host_commands_after_refusal": True,
            "no_mount_attempted_after_refusal": True,
            "no_worker_launch_after_refusal": True,
            "cloudtainer_does_not_claim_freebsd_capsicum_execution": platform.system() != "FreeBSD",
        },
    })
    return receipt


def _stable_fixture_label(path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(ROOT).as_posix()
    except ValueError:
        return "$OUTSIDE_ALLOWED_FIXTURE_BASE"


def _fixture_failure(reason: str, fixture_root: Path) -> dict[str, Any]:
    return {
        "admitted": False,
        "reason": reason,
        "allowed_base_rel": ALLOWED_FIXTURE_BASE.relative_to(ROOT).as_posix(),
        "fixture_root_label": _stable_fixture_label(fixture_root),
        "selected_member": DEFAULT_SELECTED_MEMBER,
        "max_files": MAX_FIXTURE_FILES,
        "max_total_bytes": MAX_FIXTURE_BYTES,
        "checked_before_host_commands": True,
    }


def _within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _has_symlink_component(path: Path, stop_at: Path) -> bool:
    try:
        rel = path.relative_to(stop_at)
    except ValueError:
        return True
    cur = stop_at
    if cur.is_symlink():
        return True
    for part in rel.parts:
        cur = cur / part
        try:
            if cur.is_symlink():
                return True
        except OSError:
            return False
    return False


def fixture_tree_manifest(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    file_count = 0
    directory_count = 0
    total_bytes = 0
    selected_member_sha256: str | None = None
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        rel_dir = current.relative_to(root).as_posix()
        if rel_dir != ".":
            st_dir = current.lstat()
            if stat.S_ISLNK(st_dir.st_mode):
                raise HostSmokeFailure("fixture-root-admission", "fixture tree contains symlink directory", details={"fixture_manifest_error": "fixture-entry-symlink-directory"})
            if not stat.S_ISDIR(st_dir.st_mode):
                raise HostSmokeFailure("fixture-root-admission", "fixture tree contains special directory slot", details={"fixture_manifest_error": "fixture-entry-special-directory-slot"})
            directory_count += 1
            entries.append({"entry_kind": "directory", "path": rel_dir})
        for name in sorted(list(dirnames)):
            entry = current / name
            st = entry.lstat()
            if stat.S_ISLNK(st.st_mode):
                raise HostSmokeFailure("fixture-root-admission", "fixture tree contains symlink directory", details={"fixture_manifest_error": "fixture-entry-symlink-directory"})
            if not stat.S_ISDIR(st.st_mode):
                raise HostSmokeFailure("fixture-root-admission", "fixture tree contains special directory slot", details={"fixture_manifest_error": "fixture-entry-special-directory-slot"})
        dirnames[:] = sorted(dirnames)
        for name in sorted(filenames):
            entry = current / name
            st = entry.lstat()
            if stat.S_ISLNK(st.st_mode):
                raise HostSmokeFailure("fixture-root-admission", "fixture tree contains symlink file", details={"fixture_manifest_error": "fixture-entry-symlink-file"})
            if not stat.S_ISREG(st.st_mode):
                raise HostSmokeFailure("fixture-root-admission", "fixture tree contains special file", details={"fixture_manifest_error": "fixture-entry-special-file"})
            rel = entry.relative_to(root).as_posix()
            digest = sha256_file(entry)
            file_count += 1
            total_bytes += int(st.st_size)
            if file_count > MAX_FIXTURE_FILES:
                raise HostSmokeFailure("fixture-root-admission", "fixture file count limit exceeded", details={"fixture_manifest_error": "fixture-file-count-limit-exceeded"})
            if total_bytes > MAX_FIXTURE_BYTES:
                raise HostSmokeFailure("fixture-root-admission", "fixture byte limit exceeded", details={"fixture_manifest_error": "fixture-byte-limit-exceeded"})
            if rel == DEFAULT_SELECTED_MEMBER:
                selected_member_sha256 = digest
            entries.append({"entry_kind": "regular-file", "path": rel, "size_bytes": int(st.st_size), "sha256": digest})
    payload = canonical_json_bytes(entries)
    return {
        "manifest_sha256": sha256_bytes(payload),
        "file_count": file_count,
        "directory_count": directory_count,
        "total_bytes": total_bytes,
        "selected_member": DEFAULT_SELECTED_MEMBER,
        "selected_member_sha256": selected_member_sha256,
        "entry_count": len(entries),
        "manifest_includes_directories": True,
    }


def inspect_fixture_root(fixture_root: Path) -> tuple[dict[str, Any], Path | None]:
    """Admit only checked-in boring fixture trees before makefs/host commands."""
    candidate = fixture_root if fixture_root.is_absolute() else ROOT / fixture_root
    if ".." in candidate.parts:
        return _fixture_failure("fixture-root-traversal-component", candidate), None
    try:
        base = ALLOWED_FIXTURE_BASE.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError:
        return _fixture_failure("fixture-root-missing", candidate), None
    except OSError as exc:
        return _fixture_failure(f"fixture-root-resolve-failed:{type(exc).__name__}", candidate), None
    if not _within(resolved, base):
        return _fixture_failure("fixture-root-outside-allowed-base", candidate), None
    if _has_symlink_component(candidate, ALLOWED_FIXTURE_BASE):
        return _fixture_failure("fixture-root-symlink-component", candidate), None
    try:
        root_st = candidate.lstat()
    except OSError:
        return _fixture_failure("fixture-root-lstat-failed", candidate), None
    if stat.S_ISLNK(root_st.st_mode):
        return _fixture_failure("fixture-root-is-symlink", candidate), None
    if not stat.S_ISDIR(root_st.st_mode):
        return _fixture_failure("fixture-root-not-directory", candidate), None
    selected = resolved / DEFAULT_SELECTED_MEMBER
    try:
        selected_st = selected.lstat()
    except OSError:
        return _fixture_failure("selected-member-missing", candidate), None
    if stat.S_ISLNK(selected_st.st_mode):
        return _fixture_failure("selected-member-is-symlink", candidate), None
    if not stat.S_ISREG(selected_st.st_mode):
        return _fixture_failure("selected-member-not-regular", candidate), None
    try:
        manifest = fixture_tree_manifest(resolved)
    except HostSmokeFailure as exc:
        details = _fixture_failure(str(exc.details.get("fixture_manifest_error", "fixture-tree-invalid")), candidate)
        return details, None
    if manifest.get("selected_member_sha256") is None:
        return _fixture_failure("selected-member-missing", candidate), None
    evidence = {
        "admitted": True,
        "reason": None,
        "allowed_base_rel": ALLOWED_FIXTURE_BASE.relative_to(ROOT).as_posix(),
        "fixture_root_rel": resolved.relative_to(ROOT).as_posix(),
        "selected_member": DEFAULT_SELECTED_MEMBER,
        "file_count": manifest.get("file_count"),
        "directory_count": manifest.get("directory_count"),
        "total_bytes": manifest.get("total_bytes"),
        "manifest_sha256": manifest.get("manifest_sha256"),
        "manifest_includes_directories": manifest.get("manifest_includes_directories") is True,
        "selected_member_sha256": manifest.get("selected_member_sha256"),
        "max_files": MAX_FIXTURE_FILES,
        "max_total_bytes": MAX_FIXTURE_BYTES,
        "within_allowed_base": True,
        "resolved_within_allowed_base": True,
        "no_symlink_components": True,
        "no_symlink_or_special_entries": True,
        "selected_member_regular": True,
        "checked_before_host_commands": True,
    }
    return evidence, resolved


def copy_fixture_tree_verified(dst: Path, fixture_root: Path, admission: dict[str, Any]) -> dict[str, Any]:
    if dst.exists():
        raise HostSmokeFailure("fixture-root-copy", f"destination already exists: {dst}")
    try:
        before = fixture_tree_manifest(fixture_root)
        expected_manifest = admission.get("manifest_sha256")
        if expected_manifest and before.get("manifest_sha256") != expected_manifest:
            evidence = {
                "source_manifest_sha256_at_admission": expected_manifest,
                "source_manifest_sha256_before_copy": before.get("manifest_sha256"),
                "source_stable_since_admission": False,
                "source_stable_during_copy": False,
                "copy_matches_source_manifest": False,
                "checked_before_host_commands": True,
            }
            raise HostSmokeFailure("fixture-root-copy", "fixture source changed after admission before copy", details={"fixture_copy": evidence})
        shutil.copytree(fixture_root, dst, symlinks=False)
        after = fixture_tree_manifest(fixture_root)
        copied = fixture_tree_manifest(dst)
    except HostSmokeFailure:
        raise
    except Exception as exc:  # noqa: BLE001 - copy boundary must become receipt-shaped
        raise HostSmokeFailure("fixture-root-copy", f"fixture copy failed: {type(exc).__name__}: {exc}") from exc
    evidence = {
        "source_manifest_sha256_at_admission": admission.get("manifest_sha256"),
        "source_manifest_sha256_before_copy": before.get("manifest_sha256"),
        "source_manifest_sha256_after_copy": after.get("manifest_sha256"),
        "copied_manifest_sha256": copied.get("manifest_sha256"),
        "selected_member_sha256": copied.get("selected_member_sha256"),
        "file_count": copied.get("file_count"),
        "directory_count": copied.get("directory_count"),
        "total_bytes": copied.get("total_bytes"),
        "manifest_includes_directories": copied.get("manifest_includes_directories") is True,
        "source_stable_since_admission": admission.get("manifest_sha256") == before.get("manifest_sha256"),
        "source_stable_during_copy": before.get("manifest_sha256") == after.get("manifest_sha256"),
        "copy_matches_source_manifest": copied.get("manifest_sha256") == before.get("manifest_sha256"),
        "checked_before_host_commands": True,
    }
    if evidence["source_stable_since_admission"] is not True or evidence["source_stable_during_copy"] is not True or evidence["copy_matches_source_manifest"] is not True:
        raise HostSmokeFailure("fixture-root-copy", "fixture source/copy manifest mismatch", details={"fixture_copy": evidence})
    return evidence


def copy_fixture_tree(dst: Path, fixture_root: Path) -> None:
    copy_fixture_tree_verified(dst, fixture_root, {"manifest_sha256": fixture_tree_manifest(fixture_root).get("manifest_sha256")})


def _source_failure(reason: str, source: Path) -> dict[str, Any]:
    try:
        label = source.resolve(strict=False).relative_to(ROOT).as_posix()
    except ValueError:
        label = "$OUTSIDE_REPO"
    return {
        "admitted": False,
        "reason": reason,
        "source_label": label,
        "checked_before_compile": True,
    }


def inspect_worker_source(source: Path = C_WORKER_SOURCE) -> dict[str, Any]:
    """Admit the checked-in C worker source before host compilation."""
    candidate = source if source.is_absolute() else ROOT / source
    try:
        repo_root = ROOT.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError:
        return _source_failure("worker-source-missing", candidate)
    except OSError as exc:
        return _source_failure(f"worker-source-resolve-failed:{type(exc).__name__}", candidate)
    if not _within(resolved, repo_root):
        return _source_failure("worker-source-outside-repo", candidate)
    try:
        st = candidate.lstat()
    except OSError:
        return _source_failure("worker-source-lstat-failed", candidate)
    if stat.S_ISLNK(st.st_mode):
        return _source_failure("worker-source-is-symlink", candidate)
    if not stat.S_ISREG(st.st_mode):
        return _source_failure("worker-source-not-regular", candidate)
    digest = sha256_file(resolved)
    return {
        "admitted": True,
        "reason": None,
        "source_rel": resolved.relative_to(ROOT).as_posix(),
        "source_sha256": digest,
        "size_bytes": int(st.st_size),
        "regular_file": True,
        "not_symlink": True,
        "resolved_under_repo": True,
        "checked_before_compile": True,
    }


def copy_worker_source_verified(dst: Path, source: Path = C_WORKER_SOURCE, admission: dict[str, Any] | None = None) -> dict[str, Any]:
    """Copy the C worker source into the private work root and verify stability."""
    admission = admission or inspect_worker_source(source)
    if admission.get("admitted") is not True:
        raise HostSmokeFailure("worker-source-admission", f"worker source admission failed: {admission.get('reason')}", details={"worker_source_copy": admission})
    if dst.exists():
        raise HostSmokeFailure("worker-source-copy", f"worker source copy destination already exists: {dst}")
    dst.parent.mkdir(mode=0o700, parents=True, exist_ok=False)
    try:
        before = sha256_file(source)
        expected = admission.get("source_sha256")
        if expected and before != expected:
            evidence = {
                "source_sha256_at_admission": expected,
                "source_sha256_before_copy": before,
                "source_stable_since_admission": False,
                "source_stable_during_copy": False,
                "copy_matches_source_digest": False,
                "checked_before_compile": True,
            }
            raise HostSmokeFailure("worker-source-copy", "worker source changed after admission before copy", details={"worker_source_copy": evidence})
        shutil.copy2(source, dst)
        after = sha256_file(source)
        copied = sha256_file(dst)
    except HostSmokeFailure:
        raise
    except Exception as exc:  # noqa: BLE001 - source-copy boundary must become receipt-shaped
        raise HostSmokeFailure("worker-source-copy", f"worker source copy failed: {type(exc).__name__}: {exc}") from exc
    evidence = {
        "source_rel": admission.get("source_rel"),
        "copied_source_rel": dst.relative_to(dst.parents[1]).as_posix() if len(dst.parents) > 1 else dst.name,
        "source_sha256_at_admission": admission.get("source_sha256"),
        "source_sha256_before_copy": before,
        "source_sha256_after_copy": after,
        "copied_source_sha256": copied,
        "source_size_bytes": admission.get("size_bytes"),
        "source_regular_file": admission.get("regular_file") is True,
        "source_not_symlink": admission.get("not_symlink") is True,
        "source_stable_since_admission": admission.get("source_sha256") == before,
        "source_stable_during_copy": before == after,
        "copy_matches_source_digest": copied == before,
        "compile_uses_private_source_copy": True,
        "checked_before_compile": True,
    }
    if evidence["source_stable_since_admission"] is not True or evidence["source_stable_during_copy"] is not True or evidence["copy_matches_source_digest"] is not True:
        raise HostSmokeFailure("worker-source-copy", "worker source/copy digest mismatch", details={"worker_source_copy": evidence})
    return evidence


def _single_line_command_token(stdout: str, *, command_name: str) -> str:
    """Return exactly one authority token; reject multiline/suffix output."""
    text = stdout.strip()
    if not text:
        raise RuntimeError(f"{command_name} did not print an authority token")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) != 1 or lines[0] != text:
        raise RuntimeError(f"{command_name} printed non-canonical multiline output")
    return lines[0]


def parse_md_unit(stdout: str) -> str:
    unit = _single_line_command_token(stdout, command_name="mdconfig")
    if MD_UNIT_NUMBER_RE.fullmatch(unit):
        return "md" + unit
    match = MD_UNIT_RE.fullmatch(unit)
    if match is not None:
        return "md" + match.group(1)
    raise RuntimeError(f"unexpected mdconfig unit output: {unit!r}")


def parse_fstyp_ufs_stdout(stdout: str) -> str:
    fs_type = _single_line_command_token(stdout, command_name="fstyp")
    if fs_type != "ufs":
        raise RuntimeError(f"unexpected fstyp result: {fs_type!r}")
    return fs_type


def md_unit_detach_number(md_unit: str) -> str:
    match = MD_UNIT_NORMALIZED_RE.fullmatch(md_unit)
    if match is None:
        raise RuntimeError(f"unsafe mdconfig unit for detach: {md_unit!r}")
    return match.group(1)


def run_worker(binary: Path, preserved_object: Path, output_path: Path, canary_path: Path, worker_cwd: Path) -> dict[str, Any]:
    slot_guard = fd_slots.FdSlotGuard(fd_slots.TARGET_FDS).save_and_clear()
    input_fd: int | None = None
    output_fd: int | None = None
    canary_fd: int | None = None
    stdout = ""
    stderr = ""
    return_code = 124
    timed_out = False
    try:
        worker_cwd.mkdir(mode=0o700, parents=False, exist_ok=False)
        worker_cwd_initially_empty = not any(worker_cwd.iterdir())
        input_fd = os.open(preserved_object, os.O_RDONLY)
        output_fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        canary_fd = os.open(canary_path, os.O_RDONLY)
        slot_guard.install_owned_fd(input_fd, 3)
        input_fd = None
        slot_guard.install_owned_fd(output_fd, 4)
        output_fd = None
        slot_guard.install_owned_fd(canary_fd, 5)
        canary_fd = None
        try:
            proc = subprocess.run(
                [str(binary)],
                cwd=worker_cwd,
                env={},
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30,
                check=False,
                pass_fds=(3, 4, 5),
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            return_code = int(proc.returncode)
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout or ""
            err = exc.stderr or ""
            if isinstance(out, bytes):
                out = out.decode("utf-8", errors="replace")
            if isinstance(err, bytes):
                err = err.decode("utf-8", errors="replace")
            stdout = str(out)
            stderr = (str(err) + "\n" if err else "") + "TIMEOUT after 30 seconds"
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

    output_text = output_path.read_text(encoding="utf-8", errors="replace") if output_path.exists() else ""
    try:
        report = load_json_strict_text(output_text) if output_text.strip() else None
        parse_error = None
    except CanonicalJsonError as exc:
        report = None
        parse_error = str(exc)
    slot_evidence = slot_guard.evidence()
    return {
        "command": ["$PRIVATE_WORK_ROOT/" + WORKER_BINARY_NAME],
        "return_code": return_code,
        "timed_out": timed_out,
        **command_digest(stdout, stderr),
        "output_report_sha256": sha256_bytes(output_text.encode("utf-8", errors="replace")),
        "output_report_bytes": len(output_text.encode("utf-8", errors="replace")),
        "output_report": report,
        "output_parse_error": parse_error,
        "extra_fd_canary": 5,
        "extra_fd_canary_source": "broker-nonmedia-canary-not-source-media",
        "launcher_fd_slot_policy": fd_slots.POLICY,
        "launcher_fd_slot_evidence": slot_evidence,
        "launcher_restored_parent_fd_slots": slot_evidence.get("preexisting_parent_fd_slots_preserved") is True,
        "worker_env_policy": "empty-environment",
        "worker_env_keys_passed": [],
        "worker_cwd_policy": "private-empty-directory-not-media-not-repo",
        "worker_cwd_initially_empty": worker_cwd_initially_empty,
        "worker_cwd_is_private_empty_dir": worker_cwd.is_dir() and not any(worker_cwd.iterdir()),
        "worker_cwd_contains_media_tree": (worker_cwd / "media-tree").exists(),
    }


def _command_runner_call(command_runner: Any, cmd: list[str], *, timeout_seconds: int) -> tuple[dict[str, Any], str, str]:
    return command_runner(cmd, timeout_seconds=timeout_seconds)


def collect_host_probes(command_runner: Any, host_probes: list[dict[str, Any]]) -> dict[str, str]:
    """Collect host identity/capability probes before media authority is used."""
    values: dict[str, str] = {}
    for cmd, role in HOST_PROBE_COMMANDS:
        _result, stdout, _stderr = _checked_command(
            command_runner,
            host_probes,
            cmd,
            stage=role,
            timeout_seconds=30,
        )
        try:
            token = _single_line_command_token(stdout, command_name=role)
        except RuntimeError as exc:
            raise HostSmokeFailure(role, str(exc)) from exc
        _result["observed_value"] = token
        _result["observed_stdout_text"] = stdout
        _result["observed_value_key"] = HOST_PROBE_VALUE_KEYS[role]
        values[HOST_PROBE_VALUE_KEYS[role]] = token
    if values.get("host_probe_observed_system") != "FreeBSD":
        raise HostSmokeFailure("host-probe-uname-system", "host probe did not observe FreeBSD", details={"host_probe_values": values})
    if values.get("host_probe_effective_uid") != "0":
        raise HostSmokeFailure("host-probe-effective-uid", "host probe did not observe uid 0", details={"host_probe_values": values})
    for key in ["host_probe_osreldate", "host_probe_capsicum_capability_mode", "host_probe_capsicum_capabilities"]:
        if not str(values.get(key, "")).isdigit():
            raise HostSmokeFailure(key.replace("host_probe_", "host-probe-"), f"host probe {key} was not numeric", details={"host_probe_values": values})
    observed_osreldate = int(values.get("host_probe_osreldate", "0"))
    values["host_target_tier"] = contract.classify_host_target(
        values.get("host_probe_uname_release"),
        observed_osreldate,
    )
    if observed_osreldate < MIN_FREEBSD_OSRELDATE:
        raise HostSmokeFailure(
            "host-probe-osreldate",
            "host probe kern.osreldate is below the supported FreeBSD release floor",
            details={
                "host_probe_values": values,
                "host_osreldate_observed": observed_osreldate,
                "host_osreldate_minimum": MIN_FREEBSD_OSRELDATE,
                "host_release_floor": SUPPORTED_FREEBSD_RELEASE_FLOOR,
                "host_release_floor_policy": HOST_RELEASE_FLOOR_POLICY,
                "host_target_tier": values.get("host_target_tier"),
                "host_target_matrix_id": HOST_TARGET_MATRIX_ID,
            },
        )
    if values.get("host_probe_capsicum_capability_mode") != "1" or values.get("host_probe_capsicum_capabilities") != "1":
        raise HostSmokeFailure("host-probe-capsicum", "host probes did not observe Capsicum feature sysctls enabled", details={"host_probe_values": values})
    return values


def _checked_command(
    command_runner: Any,
    commands: list[dict[str, Any]],
    cmd: list[str],
    *,
    stage: str,
    timeout_seconds: int,
) -> tuple[dict[str, Any], str, str]:
    result, stdout, stderr = _command_runner_call(command_runner, cmd, timeout_seconds=timeout_seconds)
    result = annotate_host_command_result(dict(result))
    result["command_role"] = stage
    commands.append(result)
    if result.get("return_code") != 0:
        raise HostSmokeFailure(stage, f"host command failed at {stage}: {cmd[0]}")
    return result, stdout, stderr


def run_host_smoke(
    work_root: Path,
    *,
    generated_at_utc: str,
    fixture_root: Path,
    command_runner: Any = run_command,
    worker_runner: WorkerRunner = run_worker,
    simulated_host_commands: bool = False,
) -> dict[str, Any]:
    receipt = base_receipt(generated_at_utc=generated_at_utc, simulated_host_commands=simulated_host_commands)
    host_probes: list[dict[str, Any]] = []
    host_probe_values: dict[str, str] = {}
    commands: list[dict[str, Any]] = []
    cleanup_commands: list[dict[str, Any]] = []
    fixture_admission: dict[str, Any] | None = None
    fixture_copy: dict[str, Any] | None = None
    worker_source_admission: dict[str, Any] | None = None
    worker_source_copy: dict[str, Any] | None = None
    mounted = False
    md_unit: str | None = None
    observed_md_unit: str | None = None
    failure: HostSmokeFailure | None = None
    observed_fstyp: str | None = None
    capture: Any | None = None
    worker: dict[str, Any] | None = None
    worker_binary_sha256: str | None = None
    attempted_cleanup_umount = False
    attempted_cleanup_detach = False

    image = work_root / "media.ufs"
    media_tree = work_root / "media-tree"
    mountpoint = work_root / "mnt"
    cas_root = work_root / "quarantine-cas"
    derivative = work_root / "derivative" / "worker-report.json"
    canary = work_root / "broker-nonmedia-fd5-canary"
    binary = work_root / WORKER_BINARY_NAME
    worker_source_copy_path = work_root / WORKER_SOURCE_COPY_DIR / WORKER_SOURCE_COPY_NAME
    worker_cwd = work_root / "worker-empty-cwd"

    try:
        mountpoint.mkdir(parents=True, mode=0o700)
        derivative.parent.mkdir(parents=True, mode=0o700)
        canary.write_text("broker-owned non-media fd5 canary\n", encoding="utf-8")
        fixture_admission, admitted_fixture_root = inspect_fixture_root(fixture_root)
        receipt["fixture_admission"] = fixture_admission
        if fixture_admission.get("admitted") is not True or admitted_fixture_root is None:
            raise HostSmokeFailure("fixture-root-admission", f"fixture root admission failed: {fixture_admission.get('reason')}", details={"fixture_admission": fixture_admission})
        fixture_copy = copy_fixture_tree_verified(media_tree, admitted_fixture_root, fixture_admission)
        receipt["fixture_copy"] = fixture_copy
        worker_source_admission = inspect_worker_source(C_WORKER_SOURCE)
        receipt["worker_source_admission"] = worker_source_admission
        if worker_source_admission.get("admitted") is not True:
            raise HostSmokeFailure("worker-source-admission", f"worker source admission failed: {worker_source_admission.get('reason')}", details={"worker_source_copy": worker_source_admission})
        worker_source_copy = copy_worker_source_verified(worker_source_copy_path, C_WORKER_SOURCE, worker_source_admission)
        receipt["worker_source_copy"] = worker_source_copy

        host_probe_values = collect_host_probes(command_runner, host_probes)
        receipt["host_probes"] = host_probes
        receipt["host"].update(host_probe_values)

        for cmd, stage in [
            (["/usr/bin/cc", "-std=c99", "-Wall", "-Wextra", "-Werror", "-O2", "-o", str(binary), str(worker_source_copy_path)], "compile-worker"),
            (["/usr/sbin/makefs", "-t", "ffs", str(image), str(media_tree)], "makefs-image"),
        ]:
            _checked_command(command_runner, commands, cmd, stage=stage, timeout_seconds=120)
        worker_binary_sha256 = sha256_file(binary)

        _attach_result, attach_stdout, _attach_stderr = _checked_command(
            command_runner,
            commands,
            ["/sbin/mdconfig", "-a", "-t", "vnode", "-f", str(image), "-o", "readonly"],
            stage="mdconfig-attach-readonly",
            timeout_seconds=30,
        )
        try:
            md_unit = parse_md_unit(attach_stdout)
            observed_md_unit = md_unit
        except RuntimeError as exc:
            raise HostSmokeFailure("mdconfig-parse", str(exc)) from exc
        _attach_result["observed_value"] = md_unit
        _attach_result["observed_stdout_text"] = attach_stdout
        _attach_result["observed_value_key"] = "host_smoke.observed_md_unit"
        device = f"/dev/{md_unit}"

        _fstyp_result, fstyp_stdout, _fstyp_stderr = _checked_command(
            command_runner,
            commands,
            ["/usr/sbin/fstyp", device],
            stage="fstyp-verify-ufs",
            timeout_seconds=30,
        )
        try:
            observed_fstyp = parse_fstyp_ufs_stdout(fstyp_stdout)
        except RuntimeError as exc:
            raise HostSmokeFailure("fstyp-verify-ufs", str(exc)) from exc
        _fstyp_result["observed_value"] = observed_fstyp
        _fstyp_result["observed_stdout_text"] = fstyp_stdout
        _fstyp_result["observed_value_key"] = "host_smoke.observed_fstyp"

        mount_cmd = ["/sbin/mount", "-t", "ufs", "-o", ",".join(MOUNT_OPTIONS), device, str(mountpoint)]
        _checked_command(command_runner, commands, mount_cmd, stage="mount-readonly-untrusted", timeout_seconds=30)
        mounted = True

        try:
            capture = safe_capture.capture_regular_member(mountpoint, DEFAULT_SELECTED_MEMBER, cas_root)
        except Exception as exc:  # noqa: BLE001 - this is a receipt boundary
            raise HostSmokeFailure("safe-capture", f"safe capture failed: {exc}") from exc

        _checked_command(command_runner, commands, ["/sbin/umount", str(mountpoint)], stage="umount-before-worker", timeout_seconds=30)
        mounted = False
        _checked_command(command_runner, commands, ["/sbin/mdconfig", "-d", "-u", md_unit_detach_number(md_unit)], stage="mdconfig-detach-before-worker", timeout_seconds=30)
        md_unit = None

        try:
            worker = worker_runner(binary, capture.object_path, derivative, canary, worker_cwd)
        except Exception as exc:  # noqa: BLE001 - this is a receipt boundary
            raise HostSmokeFailure("worker-launch", f"worker launch failed: {exc}") from exc
        worker_report = worker.get("output_report") if isinstance(worker.get("output_report"), dict) else {}
        passed = (
            worker.get("return_code") == 0
            and worker.get("stdout_bytes") == 0
            and worker.get("stderr_bytes") == 0
            and worker_report.get("result") == "passed"
            and worker_report.get("capsicum_mode_entered") is True
            and worker_report.get("extra_fds_closed_before_cap_enter") is True
            and worker_report.get("extra_fd_scan_limit") == 64
            and worker_report.get("extra_fd_canary_observed_before_closefrom") is True
            and worker_report.get("input_bytes") == capture.size_bytes
            and worker_report.get("input_sha256") == capture.digest
            and worker.get("worker_env_policy") == "empty-environment"
            and worker.get("worker_env_keys_passed") == []
            and worker.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo"
            and worker.get("worker_cwd_is_private_empty_dir") is True
            and worker.get("worker_cwd_contains_media_tree") is False
        )
        receipt.update({
            "result": "passed" if passed else "failed",
            "refusal_reason": None,
            "failure": None if passed else {"stage": "worker-report", "message": "worker report did not satisfy host-smoke invariants"},
            "host_probes": host_probes,
            "commands": commands,
            "fixture_admission": fixture_admission,
            "fixture_copy": fixture_copy,
            "cleanup": {
                "commands": cleanup_commands,
                "attempted_umount_after_failure": False,
                "attempted_mdconfig_detach_after_failure": False,
                "cleanup_completed_before_receipt": True,
            },
            "host_smoke": {
                "worker_binary_sha256": worker_binary_sha256,
                "observed_fstyp": observed_fstyp,
                "observed_md_unit": observed_md_unit,
                "capture_digest": capture.digest,
                "capture_size_bytes": capture.size_bytes,
                "capture_store_rel": capture.store_rel,
                "umounted_before_worker": True,
                "mdconfig_detached_before_worker": True,
                "worker": worker,
                "worker_launched": worker is not None,
                "fixture_admission": fixture_admission,
                "fixture_copy": fixture_copy,
                "worker_source_copy": worker_source_copy,
                "worker_env_policy": "empty-environment",
                "worker_cwd_policy": "private-empty-directory-not-media-not-repo",
                "host_command_env_policy": HOST_COMMAND_ENV_POLICY,
                "host_command_env_keys": sorted(HOST_COMMAND_ENV),
                "host_probe_values": host_probe_values,
                "host_target_tier": host_probe_values.get("host_target_tier"),
                "host_target_matrix_id": HOST_TARGET_MATRIX_ID,
            },
            "invariants": {
                "host_probes_collected_before_media_commands": [cmd.get("command_role") for cmd in host_probes] == [role for _cmd, role in HOST_PROBE_COMMANDS],
                "host_probe_observed_freebsd": host_probe_values.get("host_probe_observed_system") == "FreeBSD",
                "host_probe_observed_root_uid": host_probe_values.get("host_probe_effective_uid") == "0",
                "host_probe_capsicum_feature_enabled": host_probe_values.get("host_probe_capsicum_capability_mode") == "1" and host_probe_values.get("host_probe_capsicum_capabilities") == "1",
                "host_osreldate_meets_supported_floor": int(host_probe_values.get("host_probe_osreldate", "0")) >= MIN_FREEBSD_OSRELDATE,
                "host_target_tier_recorded": host_probe_values.get("host_target_tier") in {HOST_TARGET_PRIMARY_TIER, HOST_TARGET_LEGACY_TIER},
                "makefs_disposable_ufs_image_used": True,
                "fixture_root_admitted_before_host_commands": fixture_admission is not None and fixture_admission.get("checked_before_host_commands") is True,
                "fixture_root_has_no_symlink_or_special_entries": fixture_admission is not None and fixture_admission.get("no_symlink_or_special_entries") is True,
                "fixture_source_stable_during_copy": fixture_copy is not None and fixture_copy.get("source_stable_during_copy") is True,
                "fixture_copy_matches_source_manifest": fixture_copy is not None and fixture_copy.get("copy_matches_source_manifest") is True,
                "fixture_manifest_includes_directories": fixture_admission is not None and fixture_admission.get("manifest_includes_directories") is True and fixture_copy is not None and fixture_copy.get("manifest_includes_directories") is True,
                "worker_source_copied_before_compile": worker_source_copy is not None and worker_source_copy.get("checked_before_compile") is True,
                "worker_source_regular_not_symlink": worker_source_copy is not None and worker_source_copy.get("source_regular_file") is True and worker_source_copy.get("source_not_symlink") is True,
                "worker_source_stable_during_copy": worker_source_copy is not None and worker_source_copy.get("source_stable_during_copy") is True,
                "worker_source_copy_matches_digest": worker_source_copy is not None and worker_source_copy.get("copy_matches_source_digest") is True,
                "compile_uses_private_worker_source_copy": worker_source_copy is not None and worker_source_copy.get("compile_uses_private_source_copy") is True,
                "mdconfig_vnode_readonly_attach_used": True,
                "mdconfig_output_bound_to_mount_and_detach": isinstance(observed_md_unit, str) and observed_md_unit.startswith("md"),
                "fstyp_observed_ufs_before_mount": observed_fstyp == "ufs",
                "authority_tokens_replayed_from_stdout": observed_md_unit is not None and observed_fstyp == "ufs",
                "readonly_untrusted_mount_options_used": MOUNT_OPTIONS == ["ro", "nosuid", "noexec", "nosymfollow", "untrusted"],
                "safe_capture_verified_before_detach": capture.verified_after_copy is True,
                "umount_completed_before_worker": True,
                "mdconfig_detach_completed_before_worker": True,
                "worker_executed_after_detach": True,
                "fd5_nonmedia_canary_passed_to_worker": True,
                "worker_reported_capsicum_mode_entered": worker_report.get("capsicum_mode_entered") is True,
                "worker_reported_extra_fds_closed_before_cap_enter": worker_report.get("extra_fds_closed_before_cap_enter") is True,
                "worker_reported_fd5_canary_observed_before_closefrom": worker_report.get("extra_fd_canary_observed_before_closefrom") is True,
                "worker_input_sha256_matches_capture_digest": worker_report.get("input_sha256") == capture.digest,
                "worker_stdout_stderr_bytes_zero": worker.get("stdout_bytes") == 0 and worker.get("stderr_bytes") == 0,
                "worker_environment_empty": worker.get("worker_env_policy") == "empty-environment" and worker.get("worker_env_keys_passed") == [],
                "worker_cwd_private_not_media": worker.get("worker_cwd_policy") == "private-empty-directory-not-media-not-repo" and worker.get("worker_cwd_contains_media_tree") is False,
                "host_command_environment_sanitized": all(cmd.get("host_command_env_policy") == HOST_COMMAND_ENV_POLICY and cmd.get("host_command_env_keys") == sorted(HOST_COMMAND_ENV) for cmd in host_probes + commands),
                "failure_paths_are_receipt_shaped": True,
                "no_worker_launch_after_host_failure": True,
                "cloudtainer_simulation_not_freebsd_host_proof": simulated_host_commands,
            },
        })
        return redact_host_smoke_receipt(receipt, work_root)
    except HostSmokeFailure as exc:
        failure = exc
    except Exception as exc:  # noqa: BLE001 - this runner must emit evidence instead of traceback
        failure = HostSmokeFailure("unexpected-exception", f"{type(exc).__name__}: {exc}")
    finally:
        if failure is not None and mounted:
            attempted_cleanup_umount = True
            result, _out, _err = _command_runner_call(command_runner, ["/sbin/umount", str(mountpoint)], timeout_seconds=30)
            result = annotate_host_command_result(dict(result))
            result["command_role"] = "cleanup-umount-after-failure"
            cleanup_commands.append(result)
            if result.get("return_code") == 0:
                mounted = False
        if failure is not None and md_unit:
            attempted_cleanup_detach = True
            result, _out, _err = _command_runner_call(command_runner, ["/sbin/mdconfig", "-d", "-u", md_unit_detach_number(md_unit)], timeout_seconds=30)
            result = annotate_host_command_result(dict(result))
            result["command_role"] = "cleanup-mdconfig-detach-after-failure"
            cleanup_commands.append(result)
            if result.get("return_code") == 0:
                md_unit = None

    assert failure is not None
    receipt.update({
        "result": "failed",
        "refusal_reason": None,
        "failure": {
            "stage": failure.stage,
            "message": failure.message,
            "receipt_shaped_instead_of_traceback": True,
            **failure.details,
        },
        "host_probes": host_probes,
        "commands": commands,
        "fixture_admission": fixture_admission or failure.details.get("fixture_admission"),
        "fixture_copy": fixture_copy or failure.details.get("fixture_copy"),
        "worker_source_admission": worker_source_admission,
        "worker_source_copy": worker_source_copy or failure.details.get("worker_source_copy"),
        "cleanup": {
            "commands": cleanup_commands,
            "attempted_umount_after_failure": attempted_cleanup_umount,
            "attempted_mdconfig_detach_after_failure": attempted_cleanup_detach,
            "mounted_after_cleanup_assumed": mounted,
            "mdconfig_unit_after_cleanup": md_unit,
        },
        "host_smoke": {
            "worker_binary_sha256": worker_binary_sha256,
            "observed_fstyp": observed_fstyp,
            "observed_md_unit": observed_md_unit,
            "capture_digest": getattr(capture, "digest", None),
            "capture_size_bytes": getattr(capture, "size_bytes", None),
            "capture_store_rel": getattr(capture, "store_rel", None),
            "umounted_before_worker": False,
            "mdconfig_detached_before_worker": False,
            "worker": worker,
            "worker_launched": worker is not None,
            "fixture_admission": fixture_admission or failure.details.get("fixture_admission"),
            "fixture_copy": fixture_copy or failure.details.get("fixture_copy"),
            "worker_source_copy": worker_source_copy or failure.details.get("worker_source_copy"),
            "worker_env_policy": "empty-environment",
            "worker_cwd_policy": "private-empty-directory-not-media-not-repo",
            "host_command_env_policy": HOST_COMMAND_ENV_POLICY,
            "host_command_env_keys": sorted(HOST_COMMAND_ENV),
            "host_probe_values": host_probe_values or failure.details.get("host_probe_values"),
            "host_target_tier": (host_probe_values or failure.details.get("host_probe_values") or {}).get("host_target_tier") or failure.details.get("host_target_tier"),
            "host_target_matrix_id": HOST_TARGET_MATRIX_ID,
        },
        "invariants": {
            "host_probe_failure_is_receipt_shaped": failure.stage.startswith("host-probe"),
            "host_probes_complete_before_media_commands": bool(host_probes) and commands == [] if failure.stage.startswith("host-probe") else True,
            "host_osreldate_floor_failure_is_receipt_shaped": (failure.stage == "host-probe-osreldate" and "host_osreldate_minimum" in failure.details) if failure.stage == "host-probe-osreldate" else True,
            "failure_paths_are_receipt_shaped": True,
            "fixture_failure_stops_before_host_commands": failure.stage == "fixture-root-admission" and commands == [],
            "fixture_copy_failure_stops_before_host_commands": failure.stage == "fixture-root-copy" and commands == [],
            "worker_source_copy_failure_stops_before_host_commands": failure.stage in {"worker-source-admission", "worker-source-copy"} and commands == [],
            "no_host_commands_after_fixture_admission_failure": (commands == [] and failure.stage == "fixture-root-admission") if failure.stage == "fixture-root-admission" else True,
            "no_host_commands_after_fixture_copy_failure": (commands == [] and failure.stage == "fixture-root-copy") if failure.stage == "fixture-root-copy" else True,
            "no_host_commands_after_worker_source_copy_failure": (commands == [] and failure.stage in {"worker-source-admission", "worker-source-copy"}) if failure.stage in {"worker-source-admission", "worker-source-copy"} else True,
            "no_worker_launch_after_host_failure": worker is None,
            "cleanup_attempted_after_mounted_failure": attempted_cleanup_umount if mounted or attempted_cleanup_umount else failure.stage not in {"safe-capture", "umount-before-worker"},
            "cleanup_attempted_after_mdconfig_attach": attempted_cleanup_detach if md_unit or attempted_cleanup_detach else failure.stage in {"compile-worker", "makefs-image", "mdconfig-attach-readonly"},
            "host_command_environment_sanitized": all(cmd.get("host_command_env_policy") == HOST_COMMAND_ENV_POLICY and cmd.get("host_command_env_keys") == sorted(HOST_COMMAND_ENV) for cmd in host_probes + commands + cleanup_commands),
            "cloudtainer_simulation_not_freebsd_host_proof": simulated_host_commands,
        },
    })
    return redact_host_smoke_receipt(receipt, work_root)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-host-smoke", action="store_true", help="required guard before any FreeBSD host commands run")
    parser.add_argument("--work-dir", type=Path, help="private empty work root; created if absent")
    parser.add_argument("--fixture-root", type=Path, default=DEFAULT_FIXTURE_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at", default=FIXED_GENERATED_AT)
    parser.add_argument("--print", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if platform.system() != "FreeBSD":
        receipt = refusal_receipt("non-freebsd-host", generated_at_utc=args.generated_at)
    elif os.geteuid() != 0:
        receipt = refusal_receipt("root-required", generated_at_utc=args.generated_at)
    elif not args.run_host_smoke:
        receipt = refusal_receipt("explicit-host-smoke-flag-required", generated_at_utc=args.generated_at)
    elif args.work_dir is not None and args.work_dir.exists():
        receipt = refusal_receipt("work-dir-must-not-already-exist", generated_at_utc=args.generated_at)
    else:
        if args.work_dir is None:
            with tempfile.TemporaryDirectory(prefix="derivebsd-rm-host-smoke-") as td:
                receipt = run_host_smoke(Path(td), generated_at_utc=args.generated_at, fixture_root=args.fixture_root)
        else:
            args.work_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
            receipt = run_host_smoke(args.work_dir, generated_at_utc=args.generated_at, fixture_root=args.fixture_root)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_pretty_json(args.output, receipt)
    if args.print:
        print(pretty_json_text(receipt), end="")
    if receipt.get("result") == "passed":
        return 0
    if receipt.get("result") == "refused":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
