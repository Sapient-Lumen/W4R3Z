#!/usr/bin/env python3
"""Executable DeriveBSD v0 golden-thread prototype.

This intentionally does one narrow thing: make the mission spine executable in
this archive without pretending the cloudtainer has activated a FreeBSD host.
It turns a minimal spec into a lock, plan, local artifact, local activation
receipt, rollback receipt, and explanation.  All privileged/FreeBSD effects are
represented as dry-run facts until a real FreeBSD backend replaces the local
state adapter.
"""
from __future__ import annotations

import argparse
import errno
import fcntl
from contextlib import contextmanager
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cube_digest_lib import (
    CanonicalJsonError,
    canonical_digest,
    load_json_strict_text,
    pretty_json_text,
)

CURRENT_CUBE_CUT_VERSION = "2026-06-18r630"
SCHEMA_VERSION = "0.1"
RUNTIME_IDENTITY_PROFILE = "derive-runtime-v0-content-identity-no-local-locators"
PROFILE_A = "profile-a-fleet-host"
DRY_RUN_MODE = "cloudtainer-local-dry-run"
NO_SYSTEM_MUTATION = "no-freebsd-system-mutation"
SEALED_ARTIFACT_FILE_MODE = 0o444
SEALED_ARTIFACT_DIR_MODE = 0o555
STATE_LOCK_NAME = ".derive-runtime-state.lock"
STATE_JOURNAL_NAME = ".derive-runtime-state-journal.json"
ARTIFACT_STORE_POLICY = "content-addressed-no-clobber-reuse-exact-existing"
MATERIAL_SOURCE_POLICY = "offline-checked-in-fixture-bytes-sha256-size-bound"
PACKAGE_CLOSURE_POLICY = "offline-fixture-transitive-dependency-closure"
PACKAGE_PAYLOAD_METADATA_POLICY = "checked-in-fixture-package-payload-metadata-matches-catalog-projection"
PACKAGE_REPOSITORY_SNAPSHOT_POLICY = "offline-fixture-repository-snapshot-admitted-before-catalog-resolution"
STATE_COMMIT_OBSERVATION = "exact-current-generation-readback-before-journal-clear"
PRIMARY_FREEBSD_RELEASE = "15.1-RELEASE"
ROOT = Path(__file__).resolve().parents[1]
PRIMARY_FREEBSD_MIN_OSRELDATE = 1501500
HOST_PROOF_TARGET_MATRIX_ID = "freebsd-host-proof-targets-20260617-r605"
DEFAULT_FREEBSD_REAL_BACKEND_COMMANDS = ("bectl", "bhyve", "zfs", "sysctl", "service")
DEFAULT_HOST_PROOF_IMPORT_ROOT = ROOT / "validation" / "freebsd-host-proof-imports"
DEFAULT_RUNTIME_PACKAGE_CATALOG_PATH = ROOT / "validation" / "runtime-package-catalog" / "current" / "catalog.json"
DEFAULT_RUNTIME_PACKAGE_REPOSITORY_SNAPSHOT_PATH = ROOT / "validation" / "runtime-package-repository" / "current" / "snapshot.json"
DEFAULT_RUNTIME_MATERIAL_ROOT = ROOT / "validation" / "runtime-materials" / "current"
HOST_TARGET_PRIMARY_TIER = "primary-production"
HOST_TARGET_UNSUPPORTED_TIER = "unsupported"
STATUS_COMPLETE_PRIMARY = "complete-primary-real-host-proof-imported"

_PACKAGE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.+@:-]{0,127}$")
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")
_PLATFORM_RE = re.compile(r"^freebsd-[0-9]+(?:\.[0-9]+)?-[A-Za-z0-9_]+$")
_SAFE_COMPONENT_RE = re.compile(r"[^A-Za-z0-9_.-]+")
_SHA256_DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
_PINNED_SHA256_REF_RE = re.compile(r"^.+@sha256:[a-f0-9]{64}$")


class DeriveRuntimeError(ValueError):
    """Raised for explicit user-facing runtime errors."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def read_json(path: Path) -> Any:
    try:
        return load_json_strict_text(path.read_text(encoding="utf-8"))
    except CanonicalJsonError as exc:
        raise DeriveRuntimeError(f"{path}: invalid hash-bound JSON: {exc}") from exc
    except OSError as exc:
        raise DeriveRuntimeError(f"{path}: cannot read JSON: {exc}") from exc


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        if tmp.exists():
            tmp.unlink()


def atomic_write_bytes(path: Path, data: bytes, *, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        tmp.chmod(mode)
        os.replace(tmp, path)
        _fsync_directory(path.parent)
    finally:
        if tmp.exists():
            tmp.unlink()


def write_json(path: Path, obj: Any) -> None:
    atomic_write_text(path, pretty_json_text(obj))


def atomic_create_text(path: Path, text: str, *, mode: int = 0o444) -> None:
    """Create a new text file without replacing an existing authority artifact.

    Receipts such as dry-run generation records are immutable evidence: once a
    generation ID has been assigned, a later activation must not silently
    clobber the file for that ID.  ``os.replace`` remains appropriate for the
    current-generation pointer, but generation receipts use O_EXCL so duplicate
    IDs fail closed.
    """

    require_no_existing_symlink_component(path, "exclusive output path")
    path.parent.mkdir(parents=True, exist_ok=True)
    require_no_existing_symlink_component(path, "exclusive output path")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd: int | None = None
    try:
        fd = os.open(path, flags, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            fd = None
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            dir_fd = os.open(path.parent, os.O_RDONLY)
        except OSError:
            return
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    except FileExistsError as exc:
        raise DeriveRuntimeError(f"exclusive output path already exists: {path}") from exc
    finally:
        if fd is not None:
            os.close(fd)


def create_json(path: Path, obj: Any, *, mode: int = 0o444) -> None:
    atomic_create_text(path, pretty_json_text(obj), mode=mode)


def existing_symlink_components(path: Path) -> list[Path]:
    """Return existing symlink components without resolving through them.

    Runtime authority paths are operator-controlled.  Even the local dry-run
    backend should not follow a symlinked store, state directory, or artifact
    member and then produce receipts that look like ordinary local evidence.
    This check walks only existing prefixes; a nonexistent tail is allowed so
    callers can create fresh state/store directories.
    """

    probe = path if path.is_absolute() else Path.cwd() / path
    current = Path(probe.anchor) if probe.anchor else Path.cwd()
    found: list[Path] = []
    for part in probe.parts[1:] if probe.anchor else probe.parts:
        current = current / part
        try:
            st = current.lstat()
        except FileNotFoundError:
            break
        except OSError as exc:
            raise DeriveRuntimeError(f"cannot inspect path component {current}: {exc}") from exc
        if os.path.islink(current):
            found.append(current)
    return found


def require_no_existing_symlink_component(path: Path, label: str) -> None:
    found = existing_symlink_components(path)
    if found:
        first = found[0]
        raise DeriveRuntimeError(f"{label} must not contain existing symlink components: {first}")


def safe_name(value: str) -> str:
    safe = _SAFE_COMPONENT_RE.sub("-", value).strip(".-")
    return safe or "unnamed"


_RUNTIME_IDENTITY_IGNORED_KEYS = {
    "created_at",
    "workspace",
    "paths",
    "state_dir",
    "lock_path",
    "plan_path",
    "artifact_path",
    "activation_receipt_path",
    "package_catalog_path",
    "catalog_path",
    "package_repository_snapshot_path",
    "repository_snapshot_path",
    "state_journal_path",
    "journal_path",
    "artifact_publish_result",
}


def _runtime_identity_value(value: Any, parents: tuple[str, ...] = ()) -> Any:
    """Return the path-independent identity view for runtime evidence.

    Runtime receipts need local locators so a human can open files on disk, but
    those locators must not define the proof identity.  The first rev0589 gate
    accidentally let temporary workspace paths change plan/artifact/receipt
    digests for the same spec.  This view keeps semantic inputs, authorities,
    targets, blast radius, and upstream digests while dropping local paths and
    wall-clock metadata.
    """

    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if key in _RUNTIME_IDENTITY_IGNORED_KEYS:
                continue
            if key == "path" and parents and parents[-1] == "spec":
                # Keep file paths in artifact tree manifests, but do not let the
                # operator's spec filename or temp directory become a lock ID.
                continue
            out[key] = _runtime_identity_value(item, (*parents, key))
        return out
    if isinstance(value, list):
        return [_runtime_identity_value(item, parents) for item in value]
    return value


def runtime_identity_view(obj: Any) -> Any:
    return _runtime_identity_value(obj)


def runtime_digest(obj: Any) -> str:
    return canonical_digest(runtime_identity_view(obj))


def with_runtime_digest(obj: dict[str, Any], field: str) -> dict[str, Any]:
    clone = dict(obj)
    clone.pop(field, None)
    clone[field] = runtime_digest(clone)
    return clone


def require_stored_runtime_digest(obj: dict[str, Any], field: str, label: str) -> str:
    observed = obj.get(field)
    if not isinstance(observed, str):
        raise DeriveRuntimeError(f"{label} missing required {field}")
    clone = dict(obj)
    clone.pop(field, None)
    expected = runtime_digest(clone)
    if observed != expected:
        raise DeriveRuntimeError(f"{label} {field} mismatch: observed {observed}, expected {expected}")
    return observed


def require_object(obj: Any, label: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise DeriveRuntimeError(f"{label} must be a JSON object")
    return obj


def require_kind(obj: dict[str, Any], kind: str, label: str) -> None:
    if obj.get("kind") != kind:
        raise DeriveRuntimeError(f"{label} kind must be {kind!r}; found {obj.get('kind')!r}")


def require_text_field(obj: dict[str, Any], field: str, label: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value:
        raise DeriveRuntimeError(f"{label} missing required string {field}")
    return value


def require_digest_equal(observed: str, expected: str, label: str) -> None:
    if observed != expected:
        raise DeriveRuntimeError(f"{label} digest chain mismatch: observed {observed}, expected {expected}")


def state_generation_digest(generation: dict[str, Any] | None) -> str | None:
    # Receipt identity stays path-independent; the rollback precondition itself
    # still compares the exact local generation object before mutating state.
    return runtime_digest(generation) if generation is not None else None


def require_receipt_generation(receipt: dict[str, Any], section: str, *, required: bool) -> dict[str, Any] | None:
    state = receipt.get(section)
    if not isinstance(state, dict):
        raise DeriveRuntimeError(f"activation receipt missing required {section} object")
    generation = state.get("current_generation")
    if generation is None:
        if required:
            raise DeriveRuntimeError(f"activation receipt {section}.current_generation must be present")
        return None
    if not isinstance(generation, dict):
        raise DeriveRuntimeError(f"activation receipt {section}.current_generation must be an object or null")
    return generation


def require_artifact_tree_matches_receipt(artifact: dict[str, Any]) -> None:
    artifact_path = require_text_field(artifact, "artifact_path", "artifact")
    artifact_root = Path(artifact_path)
    if not artifact_root.is_dir():
        raise DeriveRuntimeError(f"artifact tree missing or not a directory: {artifact_path}")
    expected_rows = artifact.get("tree_manifest")
    if not isinstance(expected_rows, list):
        raise DeriveRuntimeError("artifact tree_manifest must be an array")
    expected_digest = artifact.get("tree_manifest_digest")
    if not isinstance(expected_digest, str):
        raise DeriveRuntimeError("artifact missing required tree_manifest_digest")
    if canonical_digest(expected_rows) != expected_digest:
        raise DeriveRuntimeError("artifact tree_manifest_digest does not match stored tree_manifest")
    observed_rows = tree_manifest(artifact_root)
    observed_digest = canonical_digest(observed_rows)
    if observed_rows != expected_rows or observed_digest != expected_digest:
        raise DeriveRuntimeError(
            f"artifact tree_manifest mismatch: observed {observed_digest}, expected {expected_digest}"
        )


def _sysctl_int(name: str) -> int | None:
    try:
        proc = subprocess.run(
            ["sysctl", "-n", name],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    text = proc.stdout.strip()
    if not re.match(r"^[0-9]+$", text):
        return None
    return int(text)


def _observed_system() -> str:
    return platform.system() or "unknown"


def _freebsd_target_tier(system: str, release: str | None, osreldate_value: int | None) -> str:
    if system != "FreeBSD" or not isinstance(osreldate_value, int):
        return HOST_TARGET_UNSUPPORTED_TIER
    if str(release or "").startswith(PRIMARY_FREEBSD_RELEASE) and osreldate_value >= PRIMARY_FREEBSD_MIN_OSRELDATE:
        return HOST_TARGET_PRIMARY_TIER
    return HOST_TARGET_UNSUPPORTED_TIER


def _observed_host(minimum_osreldate: int) -> dict[str, Any]:
    system = _observed_system()
    osreldate = _sysctl_int("kern.osreldate") if system == "FreeBSD" else None
    try:
        effective_uid: int | None = os.geteuid()
    except AttributeError:
        effective_uid = None
    release = platform.release() or "unknown"
    return {
        "system": system,
        "release": release,
        "machine": platform.machine() or "unknown",
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "effective_uid": effective_uid,
        "kern_osreldate": osreldate,
        "primary_freebsd_release": PRIMARY_FREEBSD_RELEASE,
        "minimum_freebsd_osreldate": minimum_osreldate,
        "host_target_tier": _freebsd_target_tier(system, release, osreldate),
        "host_target_matrix_id": HOST_PROOF_TARGET_MATRIX_ID,
    }


def build_host_preflight_receipt(stamp: str, required_commands: list[str], minimum_osreldate: int) -> dict[str, Any]:
    host = _observed_host(minimum_osreldate)
    command_rows = []
    denial_reasons: list[str] = []

    if host["system"] != "FreeBSD":
        denial_reasons.append("unsupported-host-os")
    if host.get("effective_uid") != 0:
        denial_reasons.append("root-required-for-real-backend")
    osreldate = host.get("kern_osreldate")
    if host["system"] == "FreeBSD" and (not isinstance(osreldate, int) or osreldate < minimum_osreldate):
        denial_reasons.append("freebsd-osreldate-below-primary-floor")
    if host.get("host_target_tier") != HOST_TARGET_PRIMARY_TIER:
        denial_reasons.append("host-target-not-primary-production")

    for command in sorted(set(required_commands)):
        found = shutil.which(command) is not None
        command_rows.append({"name": command, "found": found})
        if not found:
            denial_reasons.append(f"missing-required-command:{command}")

    result = "passed" if not denial_reasons else "denied"
    receipt: dict[str, Any] = {
        "kind": "derive.runtime.host_preflight.receipt",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "profile": PROFILE_A,
        "requested_backend": "freebsd-real-activation",
        "mode": "preflight-only",
        "system_effect": NO_SYSTEM_MUTATION,
        "host": host,
        "required_commands": command_rows,
        "result": result,
        "admissible_for_real_backend": result == "passed",
        "denial_reasons": sorted(set(denial_reasons)),
        "truth_claim": "preflight observed host posture only; it did not activate bectl, run rc.d, launch bhyve, or mutate FreeBSD state",
    }
    return with_runtime_digest(receipt, "host_preflight_digest")


def host_preflight_semantic_errors(preflight: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    host = preflight.get("host") if isinstance(preflight.get("host"), dict) else {}
    if preflight.get("generated_for_version") != CURRENT_CUBE_CUT_VERSION:
        errors.append("host-preflight-cube-cut-mismatch")
    if preflight.get("profile") != PROFILE_A:
        errors.append("host-preflight-profile-mismatch")
    if preflight.get("requested_backend") != "freebsd-real-activation":
        errors.append("host-preflight-backend-mismatch")
    if preflight.get("mode") != "preflight-only":
        errors.append("host-preflight-mode-mismatch")
    if preflight.get("system_effect") != NO_SYSTEM_MUTATION:
        errors.append("host-preflight-must-be-observation-only")
    if preflight.get("result") != "passed":
        errors.append("host-preflight-result-not-passed")
    if preflight.get("admissible_for_real_backend") is not True:
        errors.append("host-preflight-not-admissible")
    denial_reasons = preflight.get("denial_reasons")
    if denial_reasons != []:
        errors.append("host-preflight-denial-reasons-not-empty")
    system = host.get("system")
    release = host.get("release")
    osreldate = host.get("kern_osreldate")
    if system != "FreeBSD":
        errors.append("unsupported-host-os")
    if host.get("effective_uid") != 0:
        errors.append("root-required-for-real-backend")
    if not isinstance(osreldate, int) or osreldate < PRIMARY_FREEBSD_MIN_OSRELDATE:
        errors.append("freebsd-osreldate-below-primary-floor")
    expected_tier = _freebsd_target_tier(str(system or ""), str(release or ""), osreldate if isinstance(osreldate, int) else None)
    if host.get("host_target_tier") != expected_tier:
        errors.append("host-target-tier-inconsistent")
    if host.get("host_target_matrix_id") != HOST_PROOF_TARGET_MATRIX_ID:
        errors.append("host-target-matrix-mismatch")
    if expected_tier != HOST_TARGET_PRIMARY_TIER:
        errors.append("host-target-not-primary-production")
    rows = preflight.get("required_commands")
    if not isinstance(rows, list):
        errors.append("host-preflight-required-commands-malformed")
        return sorted(set(errors))
    command_seen: set[str] = set()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"host-preflight-command-row-malformed:{idx}")
            continue
        name = row.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"host-preflight-command-name-malformed:{idx}")
            continue
        command_seen.add(name)
        if row.get("found") is not True:
            errors.append(f"missing-required-command:{name}")
    for name in DEFAULT_FREEBSD_REAL_BACKEND_COMMANDS:
        if name not in command_seen:
            errors.append(f"missing-required-command-row:{name}")
    return sorted(set(errors))


def _freebsd_import_reporter() -> Any:
    freebsd_tools = Path(__file__).resolve().parent / "freebsd"
    if str(freebsd_tools) not in sys.path:
        sys.path.insert(0, str(freebsd_tools))
    import report_removable_media_local_fallback_host_proof_imports as import_reporter  # type: ignore

    return import_reporter


def host_proof_import_status(import_root: Path) -> dict[str, Any]:
    reporter = _freebsd_import_reporter()
    status = reporter.summarize_import_root(import_root)
    if not isinstance(status, dict):
        raise DeriveRuntimeError("host proof import reporter returned a non-object status")
    return status


def _int_from_host_probe(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.match(r"^[0-9]+$", value):
        return int(value)
    return None


def _primary_release_family(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(PRIMARY_FREEBSD_RELEASE)


def _host_proof_matches_preflight(item: dict[str, Any], preflight: dict[str, Any]) -> list[str]:
    host = preflight.get("host") if isinstance(preflight.get("host"), dict) else {}
    errors: list[str] = []
    if item.get("valid") is not True:
        errors.append("host-proof-item-not-valid")
    if item.get("proof_status") != "real-host-proof":
        errors.append("host-proof-not-real")
    if item.get("host_target_tier") != HOST_TARGET_PRIMARY_TIER:
        errors.append("host-proof-target-not-primary-production")
    if item.get("host_target_matrix_id") != HOST_PROOF_TARGET_MATRIX_ID:
        errors.append("host-proof-target-matrix-mismatch")
    if host.get("host_target_matrix_id") != HOST_PROOF_TARGET_MATRIX_ID:
        errors.append("host-preflight-target-matrix-mismatch")
    if item.get("host_probe_observed_system") != "FreeBSD":
        errors.append("host-proof-observed-system-not-freebsd")
    if str(item.get("host_probe_effective_uid")) != "0":
        errors.append("host-proof-not-root")

    proof_release = item.get("host_probe_uname_release")
    preflight_release = host.get("release")
    if proof_release != preflight_release:
        errors.append("host-proof-preflight-release-mismatch")
    if not _primary_release_family(proof_release):
        errors.append("host-proof-release-not-primary")

    proof_machine = item.get("host_probe_uname_machine")
    if proof_machine != host.get("machine"):
        errors.append("host-proof-preflight-machine-mismatch")

    proof_osreldate = _int_from_host_probe(item.get("host_probe_osreldate"))
    preflight_osreldate = host.get("kern_osreldate")
    if proof_osreldate is None or proof_osreldate < PRIMARY_FREEBSD_MIN_OSRELDATE:
        errors.append("host-proof-osreldate-below-primary-floor")
    if proof_osreldate != preflight_osreldate:
        errors.append("host-proof-preflight-osreldate-mismatch")
    return sorted(set(errors))


def require_primary_host_proof_imported(import_root: Path, preflight: dict[str, Any]) -> dict[str, Any]:
    status = host_proof_import_status(import_root)
    if status.get("generated_for_version") != CURRENT_CUBE_CUT_VERSION:
        raise DeriveRuntimeError(
            "real backend requires current host-proof import status; "
            f"observed generated_for_version={status.get('generated_for_version')!r}"
        )
    if status.get("proof_complete") is not True or status.get("status") != STATUS_COMPLETE_PRIMARY:
        counts = status.get("counts") if isinstance(status.get("counts"), dict) else {}
        raise DeriveRuntimeError(
            "real backend requires imported primary-production real FreeBSD host proof; "
            f"status={status.get('status')} "
            f"primary_production_real_host_proof={counts.get('primary_production_real_host_proof', 0)} "
            f"real_host_proof={counts.get('real_host_proof', 0)}"
        )

    candidate_errors: list[str] = []
    for item in status.get("items", []):
        if not isinstance(item, dict):
            candidate_errors.append("host-proof-status-item-malformed")
            continue
        if item.get("proof_status") != "real-host-proof" or item.get("host_target_tier") != HOST_TARGET_PRIMARY_TIER:
            continue
        errors = _host_proof_matches_preflight(item, preflight)
        if not errors:
            return status
        candidate_errors.extend(errors)
    raise DeriveRuntimeError(
        "real backend imported host proof does not match admitted host preflight: "
        + ", ".join(sorted(set(candidate_errors)) or ["no-primary-real-host-proof-item"])
    )


def require_host_preflight_admitted(path: Path) -> dict[str, Any]:
    preflight = require_object(read_json(path), "host preflight")
    require_kind(preflight, "derive.runtime.host_preflight.receipt", "host preflight")
    require_stored_runtime_digest(preflight, "host_preflight_digest", "host preflight")
    semantic_errors = host_preflight_semantic_errors(preflight)
    if semantic_errors:
        raise DeriveRuntimeError("host preflight denied real backend admission: " + ", ".join(semantic_errors))
    return preflight


def cmd_host_preflight(args: argparse.Namespace) -> dict[str, Any]:
    stamp = args.stamp or utc_now()
    required_commands = list(DEFAULT_FREEBSD_REAL_BACKEND_COMMANDS) + list(args.require_command or [])
    receipt = build_host_preflight_receipt(stamp, required_commands, args.minimum_osreldate)
    if args.out:
        write_json(Path(args.out), receipt)
    return receipt


def cmd_host_proof_status(args: argparse.Namespace) -> dict[str, Any]:
    report = host_proof_import_status(Path(args.import_root))
    if args.out:
        write_json(Path(args.out), report)
    return report


def validate_spec(spec: dict[str, Any]) -> None:
    for key in ["format_version", "name", "platform", "packages"]:
        if key not in spec:
            raise DeriveRuntimeError(f"spec missing required key {key!r}")
    if not isinstance(spec["format_version"], str) or not re.match(r"^0\.\d+$", spec["format_version"]):
        raise DeriveRuntimeError("spec.format_version must match 0.<minor>")
    if not isinstance(spec["name"], str) or not _NAME_RE.match(spec["name"]):
        raise DeriveRuntimeError("spec.name must be a simple non-empty artifact name")
    if not isinstance(spec["platform"], str) or not _PLATFORM_RE.match(spec["platform"]):
        raise DeriveRuntimeError("spec.platform must look like freebsd-15.1-amd64")
    packages = spec["packages"]
    if not isinstance(packages, list) or not packages:
        raise DeriveRuntimeError("spec.packages must be a non-empty array")
    seen: set[str] = set()
    for idx, item in enumerate(packages):
        if not isinstance(item, dict):
            raise DeriveRuntimeError(f"spec.packages[{idx}] must be an object")
        pkg_id = item.get("id")
        if not isinstance(pkg_id, str) or not _PACKAGE_ID_RE.match(pkg_id):
            raise DeriveRuntimeError(f"spec.packages[{idx}].id must be a simple package id")
        if pkg_id in seen:
            raise DeriveRuntimeError(f"spec.packages contains duplicate id {pkg_id!r}")
        seen.add(pkg_id)


def stable_repo_locator(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except Exception:  # noqa: BLE001
        return path.as_posix()


def require_sha256_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not _SHA256_DIGEST_RE.match(value):
        raise DeriveRuntimeError(f"{label} must be a sha256:<64 lowercase hex> digest")
    return value


def require_repo_relative_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise DeriveRuntimeError(f"{label} must be a non-empty repo-relative path")
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise DeriveRuntimeError(f"{label} must stay repo-relative without '..': {value!r}")
    return ROOT / candidate


def read_bound_material_file(material: dict[str, Any], *, label: str) -> tuple[Path, bytes]:
    path = require_repo_relative_path(material.get("path"), f"{label}.path")
    require_no_existing_symlink_component(path, label)
    if not path.is_file():
        raise DeriveRuntimeError(f"{label} material file missing or not a regular file: {path}")
    expected_sha = require_sha256_digest(material.get("sha256"), f"{label}.sha256")
    expected_size = material.get("size_bytes")
    if not isinstance(expected_size, int) or expected_size < 0:
        raise DeriveRuntimeError(f"{label}.size_bytes must be a non-negative integer")
    data = path.read_bytes()
    observed_sha = sha256_bytes(data)
    if observed_sha != expected_sha:
        raise DeriveRuntimeError(f"{label} material sha256 mismatch: observed {observed_sha}, expected {expected_sha}")
    if len(data) != expected_size:
        raise DeriveRuntimeError(f"{label} material size mismatch: observed {len(data)}, expected {expected_size}")
    return path, data


def package_catalog_digest(catalog: dict[str, Any]) -> str:
    clone = dict(catalog)
    clone.pop("catalog_digest", None)
    # Runtime loads attach the admitted snapshot object for later commands; that
    # cache must never alter the on-disk catalog projection identity.
    clone.pop("_repository_snapshot", None)
    return canonical_digest(clone)


def package_repository_snapshot_digest(snapshot: dict[str, Any]) -> str:
    clone = dict(snapshot)
    clone.pop("snapshot_digest", None)
    return canonical_digest(clone)


def load_package_repository_snapshot(ref: dict[str, Any]) -> dict[str, Any]:
    """Load the byte-bound offline fixture repository snapshot named by catalog metadata.

    r629 made fixture payloads the metadata source of truth, but the catalog was
    still the only indexed repository shape.  That left a completion-risk seam:
    the next real resolver will admit a signed/freezer-protected repository
    snapshot before selecting packages, so the fixture resolver should exercise
    the same ordering now.  The catalog is therefore a projection over this
    snapshot, not an authority by itself.
    """

    if not isinstance(ref, dict):
        raise DeriveRuntimeError("package catalog must bind a repository_snapshot object")
    path = require_repo_relative_path(ref.get("path"), "repository_snapshot.path")
    require_no_existing_symlink_component(path, "package repository snapshot")
    if not path.is_file():
        raise DeriveRuntimeError(f"package repository snapshot missing or not a regular file: {path}")
    data = path.read_bytes()
    expected_sha = require_sha256_digest(ref.get("sha256"), "repository_snapshot.sha256")
    observed_sha = sha256_bytes(data)
    if observed_sha != expected_sha:
        raise DeriveRuntimeError(
            f"package repository snapshot sha256 mismatch: observed {observed_sha}, expected {expected_sha}"
        )
    snapshot = require_object(read_json(path), "package repository snapshot")
    require_kind(snapshot, "derive.runtime.package_repository.snapshot.fixture", "package repository snapshot")
    if snapshot.get("generated_for_version") != CURRENT_CUBE_CUT_VERSION:
        raise DeriveRuntimeError(
            "package repository snapshot generated_for_version mismatch: "
            f"observed {snapshot.get('generated_for_version')!r}, expected {CURRENT_CUBE_CUT_VERSION!r}"
        )
    if snapshot.get("network_used") is not False:
        raise DeriveRuntimeError("package repository snapshot must be offline and declare network_used=false")
    if snapshot.get("authoritative_package_index") is not False:
        raise DeriveRuntimeError("fixture repository snapshot must not claim authoritative_package_index=true")
    if snapshot.get("snapshot_policy") != PACKAGE_REPOSITORY_SNAPSHOT_POLICY:
        raise DeriveRuntimeError("package repository snapshot policy mismatch")
    platforms = snapshot.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        raise DeriveRuntimeError("package repository snapshot must contain a non-empty platforms object")
    observed_digest = snapshot.get("snapshot_digest")
    expected_digest = package_repository_snapshot_digest(snapshot)
    if observed_digest != expected_digest:
        raise DeriveRuntimeError(
            f"package repository snapshot_digest mismatch: observed {observed_digest}, expected {expected_digest}"
        )
    ref_digest = require_sha256_digest(ref.get("snapshot_digest"), "repository_snapshot.snapshot_digest")
    if ref_digest != observed_digest:
        raise DeriveRuntimeError(
            f"package catalog repository_snapshot digest mismatch: catalog={ref_digest}, snapshot={observed_digest}"
        )
    if ref.get("policy") != PACKAGE_REPOSITORY_SNAPSHOT_POLICY:
        raise DeriveRuntimeError("package catalog repository_snapshot policy mismatch")
    return snapshot


def _snapshot_platform(snapshot: dict[str, Any], platform: str) -> dict[str, Any]:
    platforms = snapshot.get("platforms") if isinstance(snapshot.get("platforms"), dict) else {}
    row = platforms.get(platform)
    if not isinstance(row, dict):
        raise DeriveRuntimeError(f"platform {platform!r} is not present in the fixture repository snapshot")
    packages = row.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise DeriveRuntimeError(f"platform {platform!r} repository snapshot must contain package rows")
    return row


def _package_set(value: dict[str, Any], label: str) -> set[str]:
    packages = value.get("packages") if isinstance(value.get("packages"), dict) else None
    if not isinstance(packages, dict):
        raise DeriveRuntimeError(f"{label} must contain package rows")
    return set(packages)


def validate_catalog_against_repository_snapshot(catalog: dict[str, Any], snapshot: dict[str, Any]) -> None:
    """Require the catalog to be an exact projection of the admitted snapshot."""

    catalog_platforms = catalog.get("platforms") if isinstance(catalog.get("platforms"), dict) else {}
    snapshot_platforms = snapshot.get("platforms") if isinstance(snapshot.get("platforms"), dict) else {}
    if set(catalog_platforms) != set(snapshot_platforms):
        raise DeriveRuntimeError(
            f"package catalog platforms do not match repository snapshot: catalog={sorted(catalog_platforms)}, snapshot={sorted(snapshot_platforms)}"
        )
    for platform_name, catalog_platform in catalog_platforms.items():
        if not isinstance(catalog_platform, dict):
            raise DeriveRuntimeError(f"package catalog platform {platform_name!r} must be an object")
        snapshot_platform = _snapshot_platform(snapshot, platform_name)
        catalog_ids = _package_set(catalog_platform, f"package catalog platform {platform_name!r}")
        snapshot_ids = _package_set(snapshot_platform, f"repository snapshot platform {platform_name!r}")
        if catalog_ids != snapshot_ids:
            raise DeriveRuntimeError(
                "package catalog package ids do not match repository snapshot for "
                f"{platform_name!r}: catalog={sorted(catalog_ids)}, snapshot={sorted(snapshot_ids)}"
            )
        catalog_packages = catalog_platform["packages"]
        snapshot_packages = snapshot_platform["packages"]
        for pkg_id in sorted(catalog_ids):
            catalog_entry = catalog_packages[pkg_id]
            snapshot_entry = snapshot_packages[pkg_id]
            if not isinstance(catalog_entry, dict) or not isinstance(snapshot_entry, dict):
                raise DeriveRuntimeError(f"package {pkg_id!r} catalog/snapshot rows must be objects")
            payload_info = read_fixture_package_payload(platform_name, pkg_id, catalog_entry)
            payload = payload_info["payload"]
            snapshot_deps = validate_dependency_ids(
                snapshot_entry.get("runtime_dependencies", []), pkg_id, f"package {pkg_id!r} repository snapshot"
            )
            for field in ("origin", "version", "runtime_use"):
                if catalog_entry.get(field) != snapshot_entry.get(field):
                    raise DeriveRuntimeError(
                        f"package {pkg_id!r} catalog {field} does not match repository snapshot: "
                        f"catalog={catalog_entry.get(field)!r}, snapshot={snapshot_entry.get(field)!r}"
                    )
                if payload.get(field) != snapshot_entry.get(field):
                    raise DeriveRuntimeError(
                        f"package {pkg_id!r} fixture payload {field} does not match repository snapshot: "
                        f"payload={payload.get(field)!r}, snapshot={snapshot_entry.get(field)!r}"
                    )
            if payload_info["dependencies"] != snapshot_deps:
                raise DeriveRuntimeError(
                    f"package {pkg_id!r} fixture payload dependencies do not match repository snapshot: "
                    f"payload={payload_info['dependencies']!r}, snapshot={snapshot_deps!r}"
                )
            snapshot_material = snapshot_entry.get("material")
            catalog_material = catalog_entry.get("material")
            if not isinstance(snapshot_material, dict) or not isinstance(catalog_material, dict):
                raise DeriveRuntimeError(f"package {pkg_id!r} catalog/snapshot material rows must be objects")
            for field in ("path", "sha256", "size_bytes", "media_type", "source_authority", "truth_claim"):
                if catalog_material.get(field) != snapshot_material.get(field):
                    raise DeriveRuntimeError(
                        f"package {pkg_id!r} catalog material {field} does not match repository snapshot"
                    )
            snapshot_payload_digest = require_sha256_digest(
                snapshot_entry.get("fixture_payload_digest"), f"package {pkg_id!r}.fixture_payload_digest"
            )
            if snapshot_payload_digest != payload_info["fixture_payload_digest"]:
                raise DeriveRuntimeError(
                    f"package {pkg_id!r} repository snapshot fixture_payload_digest mismatch: "
                    f"snapshot={snapshot_payload_digest}, payload={payload_info['fixture_payload_digest']}"
                )


def load_package_catalog(path: Path) -> dict[str, Any]:
    require_no_existing_symlink_component(path, "package catalog")
    catalog = require_object(read_json(path), "package catalog")
    require_kind(catalog, "derive.runtime.package_catalog.fixture", "package catalog")
    if catalog.get("generated_for_version") != CURRENT_CUBE_CUT_VERSION:
        raise DeriveRuntimeError(
            "package catalog generated_for_version mismatch: "
            f"observed {catalog.get('generated_for_version')!r}, expected {CURRENT_CUBE_CUT_VERSION!r}"
        )
    if catalog.get("network_used") is not False:
        raise DeriveRuntimeError("package catalog must be offline and declare network_used=false")
    platforms = catalog.get("platforms")
    if not isinstance(platforms, dict) or not platforms:
        raise DeriveRuntimeError("package catalog must contain a non-empty platforms object")
    observed = catalog.get("catalog_digest")
    expected = package_catalog_digest(catalog)
    if observed != expected:
        raise DeriveRuntimeError(f"package catalog_digest mismatch: observed {observed}, expected {expected}")
    snapshot = load_package_repository_snapshot(catalog.get("repository_snapshot", {}))
    validate_catalog_against_repository_snapshot(catalog, snapshot)
    catalog["_repository_snapshot"] = snapshot
    return catalog


def _platform_catalog(catalog: dict[str, Any], platform: str) -> dict[str, Any]:
    platforms = catalog.get("platforms") if isinstance(catalog.get("platforms"), dict) else {}
    platform_row = platforms.get(platform)
    if not isinstance(platform_row, dict):
        raise DeriveRuntimeError(f"platform {platform!r} is not present in the offline package catalog")
    packages = platform_row.get("packages")
    if not isinstance(packages, dict) or not packages:
        raise DeriveRuntimeError(f"platform {platform!r} package catalog must contain package rows")
    return platform_row


def package_entry(platform: str, pkg_id: str, catalog: dict[str, Any]) -> dict[str, Any]:
    platform_row = _platform_catalog(catalog, platform)
    packages = platform_row["packages"]
    entry = packages.get(pkg_id)
    if not isinstance(entry, dict):
        raise DeriveRuntimeError(
            f"package {pkg_id!r} is not present in the offline package catalog for platform {platform!r}"
        )
    return entry


def validate_dependency_ids(value: Any, pkg_id: str, label: str) -> list[str]:
    deps = value if value is not None else []
    if not isinstance(deps, list):
        raise DeriveRuntimeError(f"{label} dependencies must be an array")
    out: list[str] = []
    seen: set[str] = set()
    for idx, dep_id in enumerate(deps):
        if not isinstance(dep_id, str) or not _PACKAGE_ID_RE.match(dep_id):
            raise DeriveRuntimeError(f"{label} dependencies[{idx}] must be a simple package id")
        if dep_id == pkg_id:
            raise DeriveRuntimeError(f"package {pkg_id!r} must not depend on itself")
        if dep_id in seen:
            raise DeriveRuntimeError(f"{label} dependencies contain duplicate id {dep_id!r}")
        seen.add(dep_id)
        out.append(dep_id)
    return out


def read_fixture_package_payload(platform: str, pkg_id: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Read and verify the checked-in fixture package payload for a catalog row.

    r628 closed the catalog dependency graph, but the catalog still duplicated
    metadata already present in the package fixture bytes.  That left a risky
    stale-projection gap: a refreshed catalog digest could omit or change
    dependencies while the consumed bytes still declared a different runtime
    closure.  The fixture package payload is now treated as the source of truth
    for package identity, platform, version, origin, and runtime_dependencies;
    the catalog is only an indexed projection and must match those bytes.
    """

    material_obj = entry.get("material")
    if not isinstance(material_obj, dict):
        raise DeriveRuntimeError(f"package {pkg_id!r} catalog entry must bind material bytes")
    material_path, material_bytes = read_bound_material_file(material_obj, label=f"package {pkg_id!r}")
    try:
        payload_text = material_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DeriveRuntimeError(f"package {pkg_id!r} fixture payload must be UTF-8 JSON") from exc
    try:
        payload = require_object(load_json_strict_text(payload_text), f"package {pkg_id!r} fixture payload")
    except CanonicalJsonError as exc:
        raise DeriveRuntimeError(f"package {pkg_id!r} fixture payload invalid hash-bound JSON: {exc}") from exc
    require_kind(payload, "derive.runtime.package.fixture.bytes", f"package {pkg_id!r} fixture payload")
    if payload.get("generated_for_version") != CURRENT_CUBE_CUT_VERSION:
        raise DeriveRuntimeError(
            f"package {pkg_id!r} fixture payload generated_for_version mismatch: "
            f"observed {payload.get('generated_for_version')!r}, expected {CURRENT_CUBE_CUT_VERSION!r}"
        )
    if payload.get("network_used") is not False:
        raise DeriveRuntimeError(f"package {pkg_id!r} fixture payload must declare network_used=false")
    if payload.get("not_a_real_freebsd_pkg") is not True:
        raise DeriveRuntimeError(f"package {pkg_id!r} fixture payload must declare not_a_real_freebsd_pkg=true")
    if payload.get("package_id") != pkg_id:
        raise DeriveRuntimeError(
            f"package {pkg_id!r} catalog row points at fixture payload for package_id={payload.get('package_id')!r}"
        )
    if payload.get("platform") != platform:
        raise DeriveRuntimeError(
            f"package {pkg_id!r} fixture payload platform mismatch: observed {payload.get('platform')!r}, expected {platform!r}"
        )
    for field in ("origin", "version", "runtime_use"):
        if field in entry and entry.get(field) != payload.get(field):
            raise DeriveRuntimeError(
                f"package {pkg_id!r} catalog {field} does not match fixture payload: "
                f"catalog={entry.get(field)!r}, payload={payload.get(field)!r}"
            )
    catalog_deps = validate_dependency_ids(entry.get("dependencies", []), pkg_id, f"package {pkg_id!r} catalog")
    payload_deps = validate_dependency_ids(payload.get("runtime_dependencies", []), pkg_id, f"package {pkg_id!r} fixture payload")
    if catalog_deps != payload_deps:
        raise DeriveRuntimeError(
            f"package {pkg_id!r} catalog dependencies do not match fixture payload runtime_dependencies: "
            f"catalog={catalog_deps!r}, payload={payload_deps!r}"
        )
    return {
        "material_path": material_path,
        "material_bytes": material_bytes,
        "material_object": material_obj,
        "payload": payload,
        "dependencies": payload_deps,
        "fixture_payload_digest": canonical_digest(payload),
    }


def package_dependencies(platform: str, pkg_id: str, catalog: dict[str, Any]) -> list[str]:
    entry = package_entry(platform, pkg_id, catalog)
    payload_info = read_fixture_package_payload(platform, pkg_id, entry)
    return list(payload_info["dependencies"])


def package_resolution(
    platform: str,
    pkg_id: str,
    catalog: dict[str, Any],
    *,
    requested: bool,
    dependency_depth: int,
    dependency_chain: list[str],
    requested_by: list[str],
) -> dict[str, Any]:
    entry = package_entry(platform, pkg_id, catalog)
    payload_info = read_fixture_package_payload(platform, pkg_id, entry)
    dependencies = list(payload_info["dependencies"])
    material_obj = payload_info["material_object"]
    material_path = payload_info["material_path"]
    material_bytes = payload_info["material_bytes"]
    payload = payload_info["payload"]
    fixture_payload_digest = payload_info["fixture_payload_digest"]
    entry_digest = canonical_digest(entry)
    catalog_digest_value = require_text_field(catalog, "catalog_digest", "package catalog")
    snapshot = require_object(catalog.get("_repository_snapshot"), "package repository snapshot")
    snapshot_digest_value = require_text_field(snapshot, "snapshot_digest", "package repository snapshot")
    snapshot_entry = _snapshot_platform(snapshot, platform)["packages"][pkg_id]
    snapshot_row_digest = canonical_digest(snapshot_entry)
    resolved_ref = entry.get("resolved_ref")
    if not isinstance(resolved_ref, str) or not resolved_ref:
        resolved_ref = f"pkgbase-fixture://{platform}/{pkg_id}"
    material_row = {
        "path": stable_repo_locator(material_path),
        "sha256": sha256_bytes(material_bytes),
        "size_bytes": len(material_bytes),
        "media_type": material_obj.get("media_type", "application/vnd.derivebsd.runtime-fixture-pkg"),
        "source_authority": material_obj.get("source_authority", "checked-in-runtime-fixture"),
        "truth_claim": material_obj.get("truth_claim", "checked-in fixture bytes only; not an authoritative FreeBSD pkg archive"),
        "fixture_payload_digest": fixture_payload_digest,
    }
    digest_material = {
        "platform": platform,
        "package_id": pkg_id,
        "catalog_digest": catalog_digest_value,
        "catalog_entry_digest": entry_digest,
        "package_repository_snapshot_digest": snapshot_digest_value,
        "package_repository_snapshot_row_digest": snapshot_row_digest,
        "dependencies": dependencies,
        "dependency_chain": dependency_chain,
        "dependency_depth": dependency_depth,
        "fixture_payload_digest": fixture_payload_digest,
        "material_sha256": material_row["sha256"],
        "material_size_bytes": material_row["size_bytes"],
        "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
        "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        "requested": requested,
        "requested_by": requested_by,
        "resolver": catalog.get("resolver_identity"),
    }
    return {
        "id": pkg_id,
        "resolved_ref": resolved_ref,
        "origin": payload.get("origin"),
        "version": payload.get("version"),
        "runtime_use": payload.get("runtime_use"),
        "dependencies": dependencies,
        "requested": requested,
        "requested_by": requested_by,
        "dependency_depth": dependency_depth,
        "dependency_chain": dependency_chain,
        "catalog_entry_digest": entry_digest,
        "catalog_digest": catalog_digest_value,
        "package_repository_snapshot_digest": snapshot_digest_value,
        "package_repository_snapshot_row_digest": snapshot_row_digest,
        "fixture_payload_digest": fixture_payload_digest,
        "payload_metadata_verified": True,
        "resolution_digest": canonical_digest(digest_material),
        "resolution_authority": "offline-fixture-catalog-no-network",
        "package_closure_policy": PACKAGE_CLOSURE_POLICY,
        "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
        "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        "material_source_policy": MATERIAL_SOURCE_POLICY,
        "material": material_row,
        "consumable_bytes_verified": True,
        "authoritative_package_index": False,
        "network_used": False,
    }


def resolve_package_closure(platform: str, requested_packages: list[dict[str, Any]], catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Resolve the finite offline transitive dependency closure.

    The dry-run resolver still uses checked-in fixture rows, but a lock that
    carries only the direct package names can look much more complete than it
    is.  This helper makes dependency omission executable: every dependency row
    must exist in the finite catalog, cycles are refused, and the artifact later
    carries every closure member's checked-in bytes.
    """

    requested_ids = [pkg["id"] for pkg in requested_packages]
    requested_set = set(requested_ids)
    visited: set[str] = set()
    visiting: list[str] = []
    output_ids: list[str] = []
    metadata: dict[str, dict[str, Any]] = {}

    def record(pkg_id: str, chain: list[str]) -> None:
        root_id = chain[0]
        meta = metadata.setdefault(
            pkg_id,
            {
                "requested": False,
                "requested_by": set(),
                "dependency_depth": len(chain) - 1,
                "dependency_chain": list(chain),
            },
        )
        meta["requested_by"].add(root_id)
        if pkg_id in requested_set:
            meta["requested"] = True
        if len(chain) - 1 < meta["dependency_depth"]:
            meta["dependency_depth"] = len(chain) - 1
            meta["dependency_chain"] = list(chain)

    def visit(pkg_id: str, chain: list[str]) -> None:
        record(pkg_id, chain)
        if pkg_id in visiting:
            cycle_start = visiting.index(pkg_id)
            cycle = visiting[cycle_start:] + [pkg_id]
            raise DeriveRuntimeError("package dependency cycle detected: " + " -> ".join(cycle))
        if pkg_id in visited:
            return
        entry = package_entry(platform, pkg_id, catalog)
        visiting.append(pkg_id)
        for dep_id in package_dependencies(platform, pkg_id, catalog):
            try:
                package_entry(platform, dep_id, catalog)
            except DeriveRuntimeError as exc:
                raise DeriveRuntimeError(
                    f"dependency package {dep_id!r} required by {pkg_id!r} is not present in the offline package catalog for platform {platform!r}"
                ) from exc
            visit(dep_id, chain + [dep_id])
        visiting.pop()
        visited.add(pkg_id)
        output_ids.append(pkg_id)

    for requested_id in requested_ids:
        visit(requested_id, [requested_id])

    resolved: list[dict[str, Any]] = []
    for pkg_id in output_ids:
        meta = metadata[pkg_id]
        resolved.append(
            package_resolution(
                platform,
                pkg_id,
                catalog,
                requested=bool(meta["requested"]),
                dependency_depth=int(meta["dependency_depth"]),
                dependency_chain=list(meta["dependency_chain"]),
                requested_by=sorted(meta["requested_by"]),
            )
        )
    return resolved


def normalize_microvm_image(vm: dict[str, Any], idx: int) -> dict[str, Any]:
    image = vm.get("image")
    if not isinstance(image, dict):
        raise DeriveRuntimeError(f"targets.microvms[{idx}].image must be an object")
    closure = image.get("closure")
    if not isinstance(closure, str) or not closure:
        raise DeriveRuntimeError(f"targets.microvms[{idx}].image.closure must be a non-empty string")
    if ":latest" in closure:
        raise DeriveRuntimeError(f"targets.microvms[{idx}].image.closure must not use a latest tag")
    if not _PINNED_SHA256_REF_RE.match(closure):
        raise DeriveRuntimeError(f"targets.microvms[{idx}].image.closure must be digest-pinned with @sha256:<64 lowercase hex>")
    return {
        "closure": closure,
        "pin_policy": "digest-pinned-no-latest-tag",
    }


def microvm_targets(spec: dict[str, Any]) -> list[dict[str, Any]]:
    targets = spec.get("targets")
    if not isinstance(targets, dict):
        return []
    microvms = targets.get("microvms")
    if not isinstance(microvms, list):
        return []
    out: list[dict[str, Any]] = []
    for idx, vm in enumerate(microvms):
        if not isinstance(vm, dict):
            raise DeriveRuntimeError(f"targets.microvms[{idx}] must be an object")
        name = vm.get("name")
        if not isinstance(name, str) or not _NAME_RE.match(name):
            raise DeriveRuntimeError(f"targets.microvms[{idx}].name must be a simple name")
        resources = vm.get("resources") if isinstance(vm.get("resources"), dict) else {}
        cpu = resources.get("cpu", 1)
        mem_mb = resources.get("mem_mb", 256)
        if not isinstance(cpu, int) or cpu < 1 or cpu > 64:
            raise DeriveRuntimeError(f"targets.microvms[{idx}].resources.cpu must be a safe integer")
        if not isinstance(mem_mb, int) or mem_mb < 64 or mem_mb > 1048576:
            raise DeriveRuntimeError(f"targets.microvms[{idx}].resources.mem_mb must be a safe integer MB value")
        network = vm.get("network") if isinstance(vm.get("network"), dict) else {}
        mode = network.get("mode", "none")
        if mode not in {"none", "nat", "vsock-only"}:
            raise DeriveRuntimeError(f"targets.microvms[{idx}].network.mode must be none, nat, or vsock-only")
        out.append({
            "name": name,
            "resources": {"cpu": cpu, "mem_mb": mem_mb},
            "network": {"mode": mode},
            "image": normalize_microvm_image(vm, idx),
            "declared_secrets": sorted((vm.get("secrets") or {}).get("required", []))
            if isinstance(vm.get("secrets"), dict) and isinstance((vm.get("secrets") or {}).get("required"), list)
            else [],
        })
    return out


def cmd_lock(args: argparse.Namespace) -> dict[str, Any]:
    spec_path = Path(args.spec)
    spec = require_object(read_json(spec_path), "spec")
    validate_spec(spec)
    stamp = args.stamp or utc_now()
    spec_digest = canonical_digest(spec)
    catalog_path = Path(args.package_catalog or DEFAULT_RUNTIME_PACKAGE_CATALOG_PATH)
    catalog = load_package_catalog(catalog_path)
    catalog_digest_value = require_text_field(catalog, "catalog_digest", "package catalog")
    repository_snapshot = require_object(catalog.get("_repository_snapshot"), "package repository snapshot")
    repository_snapshot_digest_value = require_text_field(repository_snapshot, "snapshot_digest", "package repository snapshot")
    repository_snapshot_ref = require_object(catalog.get("repository_snapshot"), "package catalog repository_snapshot")
    platform_catalog = _platform_catalog(catalog, spec["platform"])
    resolved_packages = resolve_package_closure(spec["platform"], spec["packages"], catalog)
    requested_package_ids = [item["id"] for item in spec["packages"]]
    resolved_package_ids = [item["id"] for item in resolved_packages]
    dependency_package_ids = [item["id"] for item in resolved_packages if item.get("requested") is not True]
    closure_material = {
        "policy": PACKAGE_CLOSURE_POLICY,
        "requested_package_ids": requested_package_ids,
        "resolved_package_ids": resolved_package_ids,
        "dependency_package_ids": dependency_package_ids,
        "catalog_digest": catalog_digest_value,
        "package_repository_snapshot_digest": repository_snapshot_digest_value,
        "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
    }
    package_closure = dict(closure_material)
    package_closure["closure_digest"] = canonical_digest(closure_material)
    lock: dict[str, Any] = {
        "kind": "derive.runtime.lock",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "profile": PROFILE_A,
        "spec": {
            "path": spec_path.as_posix(),
            "digest": spec_digest,
            "name": spec["name"],
            "platform": spec["platform"],
            "format_version": spec["format_version"],
        },
        "resolver": {
            "mode": "offline-fixture-catalog-no-network",
            "resolver_identity": catalog.get("resolver_identity"),
            "package_catalog_path": stable_repo_locator(catalog_path),
            "package_catalog_digest": catalog_digest_value,
            "package_catalog_platform_digest": canonical_digest(platform_catalog),
            "package_repository_snapshot_path": repository_snapshot_ref.get("path"),
            "package_repository_snapshot_sha256": repository_snapshot_ref.get("sha256"),
            "package_repository_snapshot_digest": repository_snapshot_digest_value,
            "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
            "material_source_policy": MATERIAL_SOURCE_POLICY,
            "package_closure_policy": PACKAGE_CLOSURE_POLICY,
            "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
            "purpose": "bootstrap the executable product spine against an admitted finite fixture repository snapshot before catalog selection and payload-verified dependency closure",
            "truth_claim": "finite-offline-fixture-repository-snapshot-plus-catalog-projection-plus-payload-verified-closure-and-bytes-not-a-package-index-resolution",
            "network_used": False,
        },
        "package_closure": package_closure,
        "packages": resolved_packages,
        "targets": {"microvms": microvm_targets(spec)},
        "product_gap": [
            "replace offline fixture resolver/materials with FreeBSD pkgbase/source byte resolver",
            "import real host posture before production activation",
        ],
    }
    lock = with_runtime_digest(lock, "lock_digest")
    if args.out:
        write_json(Path(args.out), lock)
    return lock


def cmd_plan(args: argparse.Namespace) -> dict[str, Any]:
    lock_path = Path(args.lock)
    lock = require_object(read_json(lock_path), "lock")
    require_kind(lock, "derive.runtime.lock", "lock")
    stamp = args.stamp or utc_now()
    lock_digest = require_stored_runtime_digest(lock, "lock_digest", "lock")
    steps = [
        {
            "id": "materialize-runtime-manifest",
            "action": "write-local-artifact-tree",
            "authority": "user-write-output-dir",
            "inputs": [lock_digest],
            "freebsd_privilege_required": False,
        },
        {
            "id": "stage-generation-pointer",
            "action": "journaled-atomic-local-state-pointer-update",
            "authority": "user-write-state-dir",
            "inputs": ["artifact_digest", "state_journal_digest"],
            "freebsd_privilege_required": False,
        },
        {
            "id": "explain-digest-chain",
            "action": "read-receipt-and-emit-chain-explanation",
            "authority": "read-generated-evidence",
            "inputs": ["activation_receipt_digest"],
            "freebsd_privilege_required": False,
        },
    ]
    if lock.get("targets", {}).get("microvms"):
        steps.insert(1, {
            "id": "plan-bhyve-launch-receipt",
            "action": "emit-non-executed-bhyve-launch-intent",
            "authority": "no-bhyve-authority-in-cloudtainer",
            "inputs": [lock_digest],
            "freebsd_privilege_required": True,
        })
    plan: dict[str, Any] = {
        "kind": "derive.runtime.plan",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "profile": lock["profile"],
        "lock_path": lock_path.as_posix(),
        "lock_digest": lock_digest,
        "spec_digest": lock["spec"]["digest"],
        "execution_surface": {
            "mode": DRY_RUN_MODE,
            "freebsd_system_mutation": False,
            "bhyve_execution": False,
            "network_used": False,
            "package_closure_policy": PACKAGE_CLOSURE_POLICY,
            "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
            "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        },
        "package_closure": lock.get("package_closure"),
        "blast_radius": {
            "writes": ["artifact_output_dir", "local_state_dir"],
            "host_files_changed": [],
            "requires_root": False,
            "rollback_available": True,
            "state_commit_policy": "exclusive-lock-plus-precommit-journal",
        },
        "steps": steps,
        "packages": lock["packages"],
        "targets": lock.get("targets", {"microvms": []}),
        "product_gap": [
            "freebsd-bectl-activation-backend",
            "freebsd-bhyve-launch-stop-backend",
            "real-host-proof-import",
        ],
    }
    plan = with_runtime_digest(plan, "plan_digest")
    if args.out:
        write_json(Path(args.out), plan)
    return plan


def _mode_text(mode: int) -> str:
    return f"0o{stat.S_IMODE(mode):03o}"


def _has_writable_bits(mode: int) -> bool:
    return bool(stat.S_IMODE(mode) & 0o222)


def seal_artifact_tree(root: Path) -> None:
    """Make a local artifact tree visibly immutable before hashing it.

    This is not a FreeBSD integrity primitive and does not replace a future
    readonly ZFS/bectl backend, but it prevents the dry-run runtime from
    treating obviously mutable local files as sealed evidence.  Directories are
    chmodded after files so traversal remains possible during sealing.
    """

    require_no_existing_symlink_component(root, "artifact root")
    if not root.is_dir():
        raise DeriveRuntimeError(f"artifact root missing or not a directory: {root}")
    dirs: list[Path] = [root]
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode):
            raise DeriveRuntimeError(f"artifact tree must not contain symlink entries: {rel}")
        if stat.S_ISDIR(st.st_mode):
            dirs.append(path)
            continue
        if not stat.S_ISREG(st.st_mode):
            raise DeriveRuntimeError(f"artifact tree entry must be a regular file or directory: {rel}")
        if st.st_nlink != 1:
            raise DeriveRuntimeError(f"artifact file must not have hardlink aliases: {rel}")
        path.chmod(SEALED_ARTIFACT_FILE_MODE)
    for path in sorted(dirs, key=lambda item: len(item.parts), reverse=True):
        path.chmod(SEALED_ARTIFACT_DIR_MODE)


def remove_tree_for_rebuild(path: Path) -> None:
    """Remove a previously sealed local artifact tree without following links."""

    require_no_existing_symlink_component(path, "artifact tree removal target")
    if not path.exists():
        return
    if not path.is_dir():
        raise DeriveRuntimeError(f"artifact tree removal target must be a directory: {path}")
    for item in sorted(path.rglob("*"), key=lambda candidate: len(candidate.parts), reverse=True):
        if item.is_symlink():
            raise DeriveRuntimeError(f"artifact tree removal target must not contain symlinks: {item}")
        try:
            item.chmod(0o700 if item.is_dir() else 0o600)
        except OSError:
            pass
    try:
        path.chmod(0o700)
    except OSError:
        pass
    shutil.rmtree(path)


def tree_manifest(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    require_no_existing_symlink_component(root, "artifact root")
    if not root.is_dir():
        raise DeriveRuntimeError(f"artifact tree missing or not a directory: {root}")
    root_stat = root.lstat()
    if _has_writable_bits(root_stat.st_mode):
        raise DeriveRuntimeError(f"artifact root directory must be sealed read-only: {_mode_text(root_stat.st_mode)}")
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        st = path.lstat()
        mode = stat.S_IMODE(st.st_mode)
        if stat.S_ISLNK(st.st_mode):
            raise DeriveRuntimeError(f"artifact tree must not contain symlink entries: {rel}")
        if stat.S_ISDIR(st.st_mode):
            if _has_writable_bits(st.st_mode):
                raise DeriveRuntimeError(f"artifact directory must be sealed read-only: {rel} mode={_mode_text(st.st_mode)}")
            rows.append({"path": rel, "type": "directory", "mode": _mode_text(mode)})
            continue
        if not stat.S_ISREG(st.st_mode):
            raise DeriveRuntimeError(f"artifact tree entry must be a regular file or directory: {rel}")
        if st.st_nlink != 1:
            raise DeriveRuntimeError(f"artifact file must not have hardlink aliases: {rel}")
        if _has_writable_bits(st.st_mode):
            raise DeriveRuntimeError(f"artifact file must be sealed read-only: {rel} mode={_mode_text(st.st_mode)}")
        data = path.read_bytes()
        rows.append({
            "path": rel,
            "type": "file",
            "mode": _mode_text(mode),
            "size_bytes": len(data),
            "sha256": sha256_bytes(data),
        })
    return rows


def materialize_package_inputs(plan: dict[str, Any], artifact_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    input_dir = artifact_root / "inputs" / "packages"
    input_dir.mkdir(parents=True)
    for idx, pkg in enumerate(plan.get("packages", [])):
        if not isinstance(pkg, dict):
            raise DeriveRuntimeError(f"plan.packages[{idx}] must be an object")
        pkg_id = require_text_field(pkg, "id", f"plan.packages[{idx}]")
        material = pkg.get("material")
        if not isinstance(material, dict):
            raise DeriveRuntimeError(f"plan.packages[{idx}] must bind material bytes")
        source_path, data = read_bound_material_file(material, label=f"locked package {pkg_id!r}")
        sha_hex = sha256_bytes(data).split(":", 1)[1]
        member_rel = f"inputs/packages/{safe_name(pkg_id)}-{sha_hex[:12]}.pkg"
        atomic_write_bytes(artifact_root / member_rel, data, mode=0o444)
        rows.append({
            "package_id": pkg_id,
            "origin": pkg.get("origin"),
            "version": pkg.get("version"),
            "resolved_ref": pkg.get("resolved_ref"),
            "source_material_path": stable_repo_locator(source_path),
            "artifact_member_path": member_rel,
            "sha256": sha256_bytes(data),
            "size_bytes": len(data),
            "media_type": material.get("media_type", "application/vnd.derivebsd.runtime-fixture-pkg"),
            "fixture_payload_digest": material.get("fixture_payload_digest") or pkg.get("fixture_payload_digest"),
            "payload_metadata_verified": pkg.get("payload_metadata_verified") is True,
            "material_source_policy": pkg.get("material_source_policy", MATERIAL_SOURCE_POLICY),
            "package_closure_policy": pkg.get("package_closure_policy", PACKAGE_CLOSURE_POLICY),
            "package_payload_metadata_policy": pkg.get("package_payload_metadata_policy", PACKAGE_PAYLOAD_METADATA_POLICY),
            "package_repository_snapshot_policy": pkg.get("package_repository_snapshot_policy", PACKAGE_REPOSITORY_SNAPSHOT_POLICY),
            "package_repository_snapshot_digest": pkg.get("package_repository_snapshot_digest"),
            "package_repository_snapshot_row_digest": pkg.get("package_repository_snapshot_row_digest"),
            "requested": pkg.get("requested"),
            "requested_by": pkg.get("requested_by", []),
            "dependency_depth": pkg.get("dependency_depth"),
            "dependency_chain": pkg.get("dependency_chain", []),
            "dependencies": pkg.get("dependencies", []),
            "truth_claim": material.get("truth_claim", "checked-in fixture bytes only; not an authoritative FreeBSD pkg archive"),
        })
    return rows


def write_artifact_tree(plan: dict[str, Any], artifact_root: Path, stamp: str) -> None:
    require_no_existing_symlink_component(artifact_root, "artifact root")
    if artifact_root.exists():
        raise DeriveRuntimeError(f"artifact staging root already exists: {artifact_root}")
    (artifact_root / "activation" / "rc.conf.d").mkdir(parents=True)
    (artifact_root / "microvm").mkdir(parents=True)
    package_material_rows = materialize_package_inputs(plan, artifact_root)
    package_materials_digest = canonical_digest(package_material_rows)
    manifest = {
        "kind": "derive.runtime.artifact.manifest",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "profile": plan["profile"],
        "lock_digest": plan["lock_digest"],
        "plan_digest": require_stored_runtime_digest(plan, "plan_digest", "plan"),
        "packages": [
            {
                "id": row["package_id"],
                "artifact_member_path": row["artifact_member_path"],
                "sha256": row["sha256"],
                "size_bytes": row["size_bytes"],
            }
            for row in package_material_rows
        ],
        "package_materials_digest": package_materials_digest,
        "execution_surface": plan["execution_surface"],
    }
    write_json(artifact_root / "inputs" / "package-materials.json", {
        "kind": "derive.runtime.artifact.package_materials",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "material_source_policy": MATERIAL_SOURCE_POLICY,
        "package_closure_policy": PACKAGE_CLOSURE_POLICY,
        "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
        "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        "package_repository_snapshot_digest": (plan.get("package_closure", {}) or {}).get("package_repository_snapshot_digest"),
        "packages": package_material_rows,
        "package_materials_digest": package_materials_digest,
        "truth_claim": "artifact carries copied checked-in fixture package bytes; these bytes are not authoritative FreeBSD package artifacts",
    })
    write_json(artifact_root / "manifest.json", manifest)
    rc_lines = [
        "# DeriveBSD dry-run activation fragment.",
        f"# generated_for_version={CURRENT_CUBE_CUT_VERSION}",
        f"# plan_digest={require_stored_runtime_digest(plan, 'plan_digest', 'plan')}",
        "# This artifact is not installed into /etc by the cloudtainer prototype.",
        f"derivebsd_profile=\"{plan['profile']}\"",
        "derivebsd_dry_run=\"YES\"",
        "",
    ]
    atomic_write_text(artifact_root / "activation" / "rc.conf.d" / "derivebsd.conf", "\n".join(rc_lines))
    microvms = plan.get("targets", {}).get("microvms", [])
    write_json(artifact_root / "microvm" / "launch-intent.json", {
        "kind": "derive.runtime.microvm.launch.intent",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "bhyve_executed": False,
        "reason": "cloudtainer has no FreeBSD bhyve authority",
        "instances": microvms,
    })
    seal_artifact_tree(artifact_root)


def unique_artifact_staging_root(store: Path, plan_digest: str) -> Path:
    stem = safe_name(f"artifact-staging-{os.getpid()}-{plan_digest[-12:]}")
    for attempt in range(1000):
        candidate = store / f".{stem}-{attempt}"
        require_no_existing_symlink_component(candidate, "artifact staging root")
        if not candidate.exists() and not os.path.islink(candidate):
            return candidate
    raise DeriveRuntimeError(f"cannot allocate a fresh artifact staging root under {store}")


def publish_artifact_tree(provisional_root: Path, final_root: Path, expected_rows: list[dict[str, Any]]) -> str:
    """Publish a sealed artifact tree without replacing an existing CAS object.

    The final artifact path is content-addressed.  If the object already exists,
    the existing tree must match byte-for-byte at the manifest level and is
    reused in place.  A rebuild may never delete and republish that address
    beneath readers.
    """

    require_no_existing_symlink_component(provisional_root, "artifact staging root")
    require_no_existing_symlink_component(final_root, "artifact final root")
    if final_root.exists() or os.path.islink(final_root):
        if not final_root.is_dir():
            raise DeriveRuntimeError(f"artifact final root exists but is not a directory: {final_root}")
        observed_rows = tree_manifest(final_root)
        if observed_rows != expected_rows:
            raise DeriveRuntimeError(
                "content-addressed artifact collision: existing final root does not match the rebuilt tree"
            )
        remove_tree_for_rebuild(provisional_root)
        _fsync_directory(final_root.parent)
        return "reused-existing-exact-artifact"
    try:
        provisional_root.rename(final_root)
    except OSError as exc:
        if exc.errno in {errno.EEXIST, errno.ENOTEMPTY}:
            observed_rows = tree_manifest(final_root)
            if observed_rows != expected_rows:
                raise DeriveRuntimeError(
                    "content-addressed artifact collision after publish race: existing final root differs"
                ) from exc
            remove_tree_for_rebuild(provisional_root)
            _fsync_directory(final_root.parent)
            return "reused-existing-exact-artifact-after-race"
        raise DeriveRuntimeError(f"cannot publish artifact tree {provisional_root} -> {final_root}: {exc}") from exc
    _fsync_directory(final_root.parent)
    return "published-new-artifact"


def cmd_build(args: argparse.Namespace) -> dict[str, Any]:
    plan_path = Path(args.plan)
    plan = require_object(read_json(plan_path), "plan")
    require_kind(plan, "derive.runtime.plan", "plan")
    stamp = args.stamp or utc_now()
    plan_digest = require_stored_runtime_digest(plan, "plan_digest", "plan")
    store = Path(args.store)
    require_no_existing_symlink_component(store, "artifact store")
    store.mkdir(parents=True, exist_ok=True)
    require_no_existing_symlink_component(store, "artifact store")
    artifact_root = unique_artifact_staging_root(store, plan_digest)
    write_artifact_tree(plan, artifact_root, stamp)
    manifest_rows = tree_manifest(artifact_root)
    manifest_digest = canonical_digest(manifest_rows)
    artifact_id = "artifact-" + hashlib.sha256(f"{plan_digest}\n{manifest_digest}\n".encode()).hexdigest()[:32]
    final_root = store / artifact_id
    publish_result = publish_artifact_tree(artifact_root, final_root, manifest_rows)
    artifact: dict[str, Any] = {
        "kind": "derive.runtime.artifact",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "profile": plan["profile"],
        "artifact_id": artifact_id,
        "artifact_path": final_root.as_posix(),
        "plan_path": plan_path.as_posix(),
        "plan_digest": plan_digest,
        "lock_digest": plan["lock_digest"],
        "spec_digest": plan["spec_digest"],
        "tree_manifest": manifest_rows,
        "tree_manifest_digest": manifest_digest,
        "activation_surface": {
            "mode": DRY_RUN_MODE,
            "system_mutation": False,
            "freebsd_backend_executed": False,
            "artifact_tree_policy": "sealed-readonly-no-symlink-no-hardlink-aliases",
            "artifact_store_policy": ARTIFACT_STORE_POLICY,
            "material_source_policy": MATERIAL_SOURCE_POLICY,
            "package_closure_policy": PACKAGE_CLOSURE_POLICY,
            "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
            "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
            "package_repository_snapshot_digest": (plan.get("package_closure", {}) or {}).get("package_repository_snapshot_digest"),
            "artifact_publish_result": publish_result,
            "state_commit_policy": "exclusive-lock-plus-precommit-journal",
            "state_commit_observation": STATE_COMMIT_OBSERVATION,
        },
    }
    artifact = with_runtime_digest(artifact, "artifact_digest")
    if args.out:
        write_json(Path(args.out), artifact)
    return artifact


def current_generation_path(state_dir: Path) -> Path:
    return state_dir / "current-generation.json"


def generations_dir(state_dir: Path) -> Path:
    return state_dir / "generations"


def state_lock_path(state_dir: Path) -> Path:
    return state_dir / STATE_LOCK_NAME


def state_journal_path(state_dir: Path) -> Path:
    return state_dir / STATE_JOURNAL_NAME


def _fsync_directory(path: Path) -> None:
    try:
        dir_fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)



def require_no_pending_state_journal(state_dir: Path) -> None:
    journal_path = state_journal_path(state_dir)
    require_no_existing_symlink_component(journal_path, "state mutation journal")
    if journal_path.exists() or os.path.islink(journal_path):
        raise DeriveRuntimeError(
            f"state mutation journal already exists: {journal_path}; operator review/recovery required before another state change"
        )


def write_state_precommit_journal(
    state_dir: Path,
    *,
    operation: str,
    stamp: str,
    state_before: dict[str, Any] | None,
    state_after: dict[str, Any] | None,
    reason: str,
    input_digest: str,
) -> str:
    require_no_existing_symlink_component(state_dir, "state directory")
    journal_path = state_journal_path(state_dir)
    require_no_pending_state_journal(state_dir)
    material: dict[str, Any] = {
        "kind": "derive.runtime.state_mutation.journal",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "operation": operation,
        "phase": "precommit-before-current-generation-pointer-update",
        "mode": DRY_RUN_MODE,
        "system_effect": NO_SYSTEM_MUTATION,
        "input_digest": input_digest,
        "reason": reason,
        "state_before_digest": state_generation_digest(state_before),
        "state_after_digest": state_generation_digest(state_after),
        "state_before": {"current_generation": state_before},
        "state_after": {"current_generation": state_after},
        "truth_claim": "precommit journal written before local dry-run current-generation mutation; no FreeBSD state was changed",
    }
    material = with_runtime_digest(material, "state_journal_digest")
    create_json(journal_path, material, mode=0o400)
    return require_text_field(material, "state_journal_digest", "state mutation journal")


def clear_state_precommit_journal(state_dir: Path, expected_digest: str) -> None:
    journal_path = state_journal_path(state_dir)
    require_no_existing_symlink_component(journal_path, "state mutation journal")
    if not journal_path.exists():
        raise DeriveRuntimeError(f"state mutation journal missing during commit: {journal_path}")
    journal = require_object(read_json(journal_path), "state mutation journal")
    require_kind(journal, "derive.runtime.state_mutation.journal", "state mutation journal")
    observed = require_stored_runtime_digest(journal, "state_journal_digest", "state mutation journal")
    if observed != expected_digest:
        raise DeriveRuntimeError(
            f"state mutation journal digest mismatch during commit: observed {observed}, expected {expected_digest}"
        )
    journal_path.unlink()
    _fsync_directory(state_dir)


@contextmanager
def acquire_state_mutation_lock(state_dir: Path, *, operation: str, stamp: str):
    """Fail closed when another activation/rollback owns the local state pointer.

    The local backend is dry-run, but it is still the executable authority spine.
    Concurrent writers to ``current-generation.json`` would make rollback
    preconditions ambiguous and could produce receipts that each individually
    validate while jointly lying about the observed state transition.  The lock
    file descriptor stays open for the whole critical section and cleanup only
    unlinks the same inode this process created.
    """

    require_no_existing_symlink_component(state_dir, "state directory")
    state_dir.mkdir(parents=True, exist_ok=True)
    require_no_existing_symlink_component(state_dir, "state directory")
    require_no_pending_state_journal(state_dir)
    lock_path = state_lock_path(state_dir)
    require_no_existing_symlink_component(lock_path, "state mutation lock")
    owner_token = sha256_bytes(os.urandom(32))
    material = {
        "kind": "derive.runtime.state_mutation.lock",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "operation": operation,
        "pid": os.getpid(),
        "owner_token_digest": owner_token,
        "lock_cleanup_policy": "open-fd-flock-plus-dev-inode-owner-check-before-unlink",
        "system_effect": NO_SYSTEM_MUTATION,
        "truth_claim": "exclusive local dry-run state pointer mutation guard; no FreeBSD state was changed",
    }
    fd: int | None = None
    acquired = False
    lock_identity: tuple[int, int] | None = None
    try:
        try:
            fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            acquired = True
            lock_stat = os.fstat(fd)
            lock_identity = (lock_stat.st_dev, lock_stat.st_ino)
        except FileExistsError as exc:
            raise DeriveRuntimeError(f"state mutation lock already exists: {lock_path}") from exc
        except OSError as exc:
            raise DeriveRuntimeError(f"cannot acquire state mutation lock {lock_path}: {exc}") from exc
        os.write(fd, pretty_json_text(with_runtime_digest(material, "state_lock_digest")).encode("utf-8"))
        os.fsync(fd)
        _fsync_directory(state_dir)
        require_no_pending_state_journal(state_dir)
        yield lock_path
    finally:
        release_error: DeriveRuntimeError | None = None
        if acquired and fd is not None:
            try:
                try:
                    current_stat = os.stat(lock_path, follow_symlinks=False)
                except FileNotFoundError as exc:
                    release_error = DeriveRuntimeError(
                        f"state mutation lock disappeared before release: {lock_path}"
                    )
                else:
                    current_identity = (current_stat.st_dev, current_stat.st_ino)
                    if lock_identity is None or current_identity != lock_identity:
                        release_error = DeriveRuntimeError(
                            f"state mutation lock ownership changed; refusing to unlink replacement lock: {lock_path}"
                        )
                    else:
                        os.unlink(lock_path)
                        _fsync_directory(state_dir)
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
            finally:
                os.close(fd)
                fd = None
        elif fd is not None:
            os.close(fd)
            fd = None
        if release_error is not None:
            raise release_error

def read_current_generation(state_dir: Path) -> dict[str, Any] | None:
    require_no_existing_symlink_component(state_dir, "state directory")
    path = current_generation_path(state_dir)
    require_no_existing_symlink_component(path, "current generation pointer")
    if not path.exists():
        return None
    value = require_object(read_json(path), "current generation")
    return value


def write_current_generation(state_dir: Path, generation: dict[str, Any] | None) -> None:
    require_no_existing_symlink_component(state_dir, "state directory")
    path = current_generation_path(state_dir)
    require_no_existing_symlink_component(path, "current generation pointer")
    if generation is None:
        if path.exists():
            path.unlink()
            _fsync_directory(state_dir)
        return
    write_json(path, generation)


def commit_current_generation(state_dir: Path, generation: dict[str, Any] | None, *, operation: str) -> dict[str, Any] | None:
    write_current_generation(state_dir, generation)
    observed = read_current_generation(state_dir)
    if observed != generation:
        raise DeriveRuntimeError(
            f"{operation} current-generation commit readback mismatch; refusing to clear state journal"
        )
    return observed


def cmd_state_status(args: argparse.Namespace) -> dict[str, Any]:
    state_dir = Path(args.state)
    stamp = args.stamp or utc_now()
    current = read_current_generation(state_dir) if state_dir.exists() else None
    journal_path = state_journal_path(state_dir)
    report: dict[str, Any] = {
        "kind": "derive.runtime.state_status.report",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "mode": DRY_RUN_MODE,
        "system_effect": NO_SYSTEM_MUTATION,
        "state_dir": state_dir.as_posix(),
        "current_generation_digest": state_generation_digest(current),
        "pending_journal": False,
        "status": "clean",
        "recovery_action": "none",
        "truth_claim": "state-status is read-only; it inspects local dry-run pointer and precommit journal only",
    }
    if journal_path.exists() or os.path.islink(journal_path):
        report["pending_journal"] = True
        try:
            journal = require_object(read_json(journal_path), "state mutation journal")
            require_kind(journal, "derive.runtime.state_mutation.journal", "state mutation journal")
            journal_digest = require_stored_runtime_digest(journal, "state_journal_digest", "state mutation journal")
            before_digest = journal.get("state_before_digest")
            after_digest = journal.get("state_after_digest")
            current_digest = state_generation_digest(current)
            report.update({
                "state_journal_digest": journal_digest,
                "journal_operation": journal.get("operation"),
                "journal_phase": journal.get("phase"),
                "journal_state_before_digest": before_digest,
                "journal_state_after_digest": after_digest,
            })
            if current_digest == after_digest:
                report["status"] = "journal-pending-commit-applied"
                report["recovery_action"] = "complete-by-clearing-journal-after-operator-review"
            elif current_digest == before_digest:
                report["status"] = "journal-pending-commit-not-applied"
                report["recovery_action"] = "retry-or-clear-journal-after-operator-review"
            else:
                report["status"] = "journal-pending-state-diverged"
                report["recovery_action"] = "quarantine-state-dir-and-review-before-any-mutation"
        except DeriveRuntimeError as exc:
            report["status"] = "journal-pending-malformed"
            report["recovery_action"] = "quarantine-state-dir-and-review-malformed-journal"
            report["journal_error"] = str(exc)
    report = with_runtime_digest(report, "state_status_digest")
    if args.out:
        write_json(Path(args.out), report)
    return report


def cmd_activate(args: argparse.Namespace) -> dict[str, Any]:
    artifact_path = Path(args.artifact)
    artifact = require_object(read_json(artifact_path), "artifact")
    require_kind(artifact, "derive.runtime.artifact", "artifact")
    stamp = args.stamp or utc_now()
    artifact_digest = require_stored_runtime_digest(artifact, "artifact_digest", "artifact")
    require_artifact_tree_matches_receipt(artifact)
    if args.mode == "freebsd-real":
        if not args.host_preflight:
            raise DeriveRuntimeError("freebsd-real activation requires --host-preflight before any authority-changing step")
        preflight = require_host_preflight_admitted(Path(args.host_preflight))
        require_primary_host_proof_imported(Path(args.host_proof_import_root), preflight)
        raise DeriveRuntimeError("freebsd-real activation backend is not implemented; refusing to simulate host mutation")
    state_dir = Path(args.state)
    with acquire_state_mutation_lock(state_dir, operation="activate", stamp=stamp):
        before = read_current_generation(state_dir)
        generation_root = generations_dir(state_dir)
        require_no_existing_symlink_component(generation_root, "generations directory")
        generation_root.mkdir(parents=True, exist_ok=True)
        require_no_existing_symlink_component(generation_root, "generations directory")
        generation_id = "gen-" + hashlib.sha256(f"{artifact_digest}\n{stamp}\n".encode()).hexdigest()[:32]
        generation = {
            "generation_id": generation_id,
            "created_at": stamp,
            "artifact_path": artifact_path.as_posix(),
            "artifact_digest": artifact_digest,
            "plan_digest": artifact["plan_digest"],
            "lock_digest": artifact["lock_digest"],
            "spec_digest": artifact["spec_digest"],
            "mode": DRY_RUN_MODE,
        }
        generation_path = generation_root / f"{generation_id}.json"
        require_no_existing_symlink_component(generation_path, "generation receipt path")
        if generation_path.exists() or os.path.islink(generation_path):
            raise DeriveRuntimeError(f"exclusive output path already exists: {generation_path}")
        state_journal_digest = write_state_precommit_journal(
            state_dir,
            operation="activate",
            stamp=stamp,
            state_before=before,
            state_after=generation,
            reason="advance-current-generation-to-built-artifact",
            input_digest=artifact_digest,
        )
        create_json(generation_path, generation, mode=0o444)
        committed_generation = commit_current_generation(state_dir, generation, operation="activation")
        clear_state_precommit_journal(state_dir, state_journal_digest)
    receipt: dict[str, Any] = {
        "kind": "derive.runtime.activation.receipt",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "profile": artifact["profile"],
        "mode": DRY_RUN_MODE,
        "system_effect": NO_SYSTEM_MUTATION,
        "state_dir": state_dir.as_posix(),
        "artifact_path": artifact_path.as_posix(),
        "artifact_digest": artifact_digest,
        "plan_digest": artifact["plan_digest"],
        "lock_digest": artifact["lock_digest"],
        "spec_digest": artifact["spec_digest"],
        "state_before": {"current_generation": before},
        "state_after": {"current_generation": committed_generation},
        "state_journal": {
            "policy": "exclusive-lock-plus-precommit-journal",
            "precommit_journal_digest": state_journal_digest,
            "commit_observation": STATE_COMMIT_OBSERVATION,
            "commit_readback_digest": state_generation_digest(committed_generation),
            "result": "removed-after-current-generation-fsync",
        },
        "rollback": {
            "available": True,
            "restore_generation": before,
            "command": "derive-runtime rollback --receipt <activation.receipt.json> --state <state-dir>",
        },
        "truth_claim": "local pointer mutation only; no FreeBSD host activation, bectl switch, rc.d run, or bhyve launch occurred",
    }
    receipt = with_runtime_digest(receipt, "activation_receipt_digest")
    if args.out:
        write_json(Path(args.out), receipt)
    return receipt


def cmd_rollback(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt = require_object(read_json(receipt_path), "activation receipt")
    require_kind(receipt, "derive.runtime.activation.receipt", "activation receipt")
    stamp = args.stamp or utc_now()
    activation_receipt_digest = require_stored_runtime_digest(receipt, "activation_receipt_digest", "activation receipt")
    expected_current_generation = require_receipt_generation(receipt, "state_after", required=True)
    restore_generation = require_receipt_generation(receipt, "state_before", required=False)
    state_dir = Path(args.state)
    with acquire_state_mutation_lock(state_dir, operation="rollback", stamp=stamp):
        before = read_current_generation(state_dir)
        if before != expected_current_generation:
            raise DeriveRuntimeError(
                "rollback precondition failed: current generation does not match activation receipt state_after.current_generation"
            )
        state_journal_digest = write_state_precommit_journal(
            state_dir,
            operation="rollback",
            stamp=stamp,
            state_before=before,
            state_after=restore_generation,
            reason="restore-current-generation-from-activation-receipt",
            input_digest=activation_receipt_digest,
        )
        after = commit_current_generation(state_dir, restore_generation, operation="rollback")
        clear_state_precommit_journal(state_dir, state_journal_digest)
    rollback_receipt: dict[str, Any] = {
        "kind": "derive.runtime.rollback.receipt",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "mode": DRY_RUN_MODE,
        "system_effect": NO_SYSTEM_MUTATION,
        "state_dir": state_dir.as_posix(),
        "activation_receipt_path": receipt_path.as_posix(),
        "activation_receipt_digest": activation_receipt_digest,
        "precondition": {
            "current_generation_must_match_activation_state_after": True,
            "observed_current_generation_digest": state_generation_digest(before),
            "expected_current_generation_digest": state_generation_digest(expected_current_generation),
            "result": "passed-before-state-mutation",
        },
        "state_before": {"current_generation": before},
        "state_after": {"current_generation": after},
        "state_journal": {
            "policy": "exclusive-lock-plus-precommit-journal",
            "precommit_journal_digest": state_journal_digest,
            "commit_observation": STATE_COMMIT_OBSERVATION,
            "commit_readback_digest": state_generation_digest(after),
            "result": "removed-after-current-generation-fsync",
        },
        "truth_claim": "rollback restored only the local dry-run generation pointer after verifying receipt digest, current-generation precondition, and journaled state commit",
    }
    rollback_receipt = with_runtime_digest(rollback_receipt, "rollback_receipt_digest")
    if args.out:
        write_json(Path(args.out), rollback_receipt)
    return rollback_receipt


def cmd_explain(args: argparse.Namespace) -> dict[str, Any]:
    receipt_path = Path(args.receipt)
    receipt = require_object(read_json(receipt_path), "activation receipt")
    require_kind(receipt, "derive.runtime.activation.receipt", "activation receipt")
    activation_receipt_digest = require_stored_runtime_digest(receipt, "activation_receipt_digest", "activation receipt")
    artifact_path = Path(require_text_field(receipt, "artifact_path", "activation receipt"))
    artifact = require_object(read_json(artifact_path), "artifact")
    require_kind(artifact, "derive.runtime.artifact", "artifact")
    artifact_digest = require_stored_runtime_digest(artifact, "artifact_digest", "artifact")
    require_digest_equal(artifact_digest, receipt.get("artifact_digest"), "activation receipt -> artifact")
    require_artifact_tree_matches_receipt(artifact)
    plan = require_object(read_json(Path(require_text_field(artifact, "plan_path", "artifact"))), "plan")
    require_kind(plan, "derive.runtime.plan", "plan")
    plan_digest = require_stored_runtime_digest(plan, "plan_digest", "plan")
    require_digest_equal(plan_digest, artifact.get("plan_digest"), "artifact -> plan")
    lock = require_object(read_json(Path(require_text_field(plan, "lock_path", "plan"))), "lock")
    require_kind(lock, "derive.runtime.lock", "lock")
    lock_digest = require_stored_runtime_digest(lock, "lock_digest", "lock")
    require_digest_equal(lock_digest, plan.get("lock_digest"), "plan -> lock")
    stamp = args.stamp or utc_now()
    explanation: dict[str, Any] = {
        "kind": "derive.runtime.explanation",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "summary": "Spec resolved to an offline lock, compiled to a dry-run plan, materialized as a local artifact, activated by an atomic local state pointer, and remained rollbackable without mutating FreeBSD.",
        "profile": receipt["profile"],
        "truth_claim": receipt["truth_claim"],
        "digest_chain": {
            "spec_digest": lock["spec"]["digest"],
            "lock_digest": lock_digest,
            "plan_digest": plan_digest,
            "artifact_digest": artifact_digest,
            "activation_receipt_digest": activation_receipt_digest,
        },
        "paths": {
            "spec": lock["spec"].get("path"),
            "lock": plan.get("lock_path"),
            "plan": artifact.get("plan_path"),
            "artifact": receipt.get("artifact_path"),
            "activation_receipt": receipt_path.as_posix(),
        },
        "blast_radius": plan.get("blast_radius", {}),
        "packages": [row["id"] for row in lock.get("packages", [])],
        "requested_packages": [row["id"] for row in lock.get("packages", []) if row.get("requested") is True],
        "dependency_packages": [row["id"] for row in lock.get("packages", []) if row.get("requested") is not True],
        "package_closure_policy": PACKAGE_CLOSURE_POLICY,
        "package_payload_metadata_policy": PACKAGE_PAYLOAD_METADATA_POLICY,
        "package_repository_snapshot_policy": PACKAGE_REPOSITORY_SNAPSHOT_POLICY,
        "package_repository_snapshot_digest": (lock.get("package_closure", {}) or {}).get("package_repository_snapshot_digest"),
        "microvm_instances_planned_not_launched": [row["name"] for row in lock.get("targets", {}).get("microvms", [])],
        "next_real_backend": [
            "replace offline fixture catalog/material resolver with FreeBSD package/base-set byte resolver",
            "turn dry-run rc.conf fragment into bectl/rc.d staged activation on FreeBSD",
            "turn non-executed microvm intent into derive-vmmd bhyve launch/stop receipts",
        ],
    }
    explanation = with_runtime_digest(explanation, "explanation_digest")
    if args.out:
        write_json(Path(args.out), explanation)
    return explanation


def cmd_run_golden_thread(args: argparse.Namespace) -> dict[str, Any]:
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    stamp = args.stamp or utc_now()
    lock_path = workspace / "lock.json"
    plan_path = workspace / "plan.json"
    artifact_path = workspace / "artifact.json"
    activation_path = workspace / "activation.receipt.json"
    rollback_path = workspace / "rollback.receipt.json"
    explain_path = workspace / "explain.json"
    store_path = workspace / "store"
    state_path = workspace / "state"

    lock = cmd_lock(argparse.Namespace(spec=args.spec, out=str(lock_path), stamp=stamp, package_catalog=args.package_catalog))
    plan = cmd_plan(argparse.Namespace(lock=str(lock_path), out=str(plan_path), stamp=stamp))
    artifact = cmd_build(argparse.Namespace(plan=str(plan_path), store=str(store_path), out=str(artifact_path), stamp=stamp))
    activation = cmd_activate(argparse.Namespace(artifact=str(artifact_path), state=str(state_path), out=str(activation_path), stamp=stamp, mode="dry-run"))
    explanation = cmd_explain(argparse.Namespace(receipt=str(activation_path), out=str(explain_path), stamp=stamp))
    rollback = cmd_rollback(argparse.Namespace(receipt=str(activation_path), state=str(state_path), out=str(rollback_path), stamp=stamp))
    summary: dict[str, Any] = {
        "kind": "derive.runtime.golden_thread.run",
        "schema_version": SCHEMA_VERSION,
        "runtime_identity_profile": RUNTIME_IDENTITY_PROFILE,
        "generated_for_version": CURRENT_CUBE_CUT_VERSION,
        "created_at": stamp,
        "profile": PROFILE_A,
        "workspace": workspace.as_posix(),
        "mode": DRY_RUN_MODE,
        "system_effect": NO_SYSTEM_MUTATION,
        "steps_completed": ["lock", "plan", "build", "activate", "explain", "rollback"],
        "paths": {
            "lock": lock_path.as_posix(),
            "plan": plan_path.as_posix(),
            "artifact": artifact_path.as_posix(),
            "activation_receipt": activation_path.as_posix(),
            "explanation": explain_path.as_posix(),
            "rollback_receipt": rollback_path.as_posix(),
            "store": store_path.as_posix(),
            "state": state_path.as_posix(),
        },
        "digests": {
            "spec": lock["spec"]["digest"],
            "lock": require_stored_runtime_digest(lock, "lock_digest", "lock"),
            "plan": require_stored_runtime_digest(plan, "plan_digest", "plan"),
            "artifact": require_stored_runtime_digest(artifact, "artifact_digest", "artifact"),
            "activation_receipt": require_stored_runtime_digest(activation, "activation_receipt_digest", "activation receipt"),
            "explanation": require_stored_runtime_digest(explanation, "explanation_digest", "explanation"),
            "rollback_receipt": require_stored_runtime_digest(rollback, "rollback_receipt_digest", "rollback receipt"),
        },
        "rollback_restored_previous_generation": rollback["state_after"]["current_generation"] == activation["state_before"]["current_generation"],
        "state_commit_policy": "exclusive-lock-plus-precommit-journal",
        "state_commit_observation": STATE_COMMIT_OBSERVATION,
        "state_journal_removed_after_commit": (
            activation.get("state_journal", {}).get("result") == "removed-after-current-generation-fsync"
            and rollback.get("state_journal", {}).get("result") == "removed-after-current-generation-fsync"
        ),
        "product_gap": plan["product_gap"],
    }
    summary = with_runtime_digest(summary, "run_digest")
    if args.out:
        write_json(Path(args.out), summary)
    else:
        print(pretty_json_text(summary), end="")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="derive-runtime", description="DeriveBSD v0 dry-run golden-thread prototype")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("lock")
    p.add_argument("--spec", required=True)
    p.add_argument("--package-catalog", default=str(DEFAULT_RUNTIME_PACKAGE_CATALOG_PATH))
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.set_defaults(func=cmd_lock)

    p = sub.add_parser("plan")
    p.add_argument("--lock", required=True)
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("build")
    p.add_argument("--plan", required=True)
    p.add_argument("--store", required=True)
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("host-preflight")
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.add_argument("--minimum-osreldate", type=int, default=PRIMARY_FREEBSD_MIN_OSRELDATE)
    p.add_argument("--require-command", action="append", default=[])
    p.set_defaults(func=cmd_host_preflight)

    p = sub.add_parser("host-proof-status")
    p.add_argument("--import-root", default=str(DEFAULT_HOST_PROOF_IMPORT_ROOT))
    p.add_argument("--out")
    p.add_argument("--fail-if-incomplete", action="store_true")
    p.set_defaults(func=cmd_host_proof_status)

    p = sub.add_parser("state-status")
    p.add_argument("--state", required=True)
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.set_defaults(func=cmd_state_status)

    p = sub.add_parser("activate")
    p.add_argument("--artifact", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.add_argument("--mode", choices=["dry-run", "freebsd-real"], default="dry-run")
    p.add_argument("--host-preflight")
    p.add_argument("--host-proof-import-root", default=str(DEFAULT_HOST_PROOF_IMPORT_ROOT))
    p.set_defaults(func=cmd_activate)

    p = sub.add_parser("rollback")
    p.add_argument("--receipt", required=True)
    p.add_argument("--state", required=True)
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.set_defaults(func=cmd_rollback)

    p = sub.add_parser("explain")
    p.add_argument("--receipt", required=True)
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.set_defaults(func=cmd_explain)

    p = sub.add_parser("run-golden-thread")
    p.add_argument("--spec", required=True)
    p.add_argument("--package-catalog", default=str(DEFAULT_RUNTIME_PACKAGE_CATALOG_PATH))
    p.add_argument("--workspace", required=True)
    p.add_argument("--out")
    p.add_argument("--stamp")
    p.set_defaults(func=cmd_run_golden_thread)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
        if args.command != "run-golden-thread" and not getattr(args, "out", None):
            print(pretty_json_text(result), end="")
        if args.command == "host-preflight" and isinstance(result, dict) and result.get("result") != "passed":
            reasons = result.get("denial_reasons") if isinstance(result.get("denial_reasons"), list) else []
            print("derive-runtime: host preflight denied: " + ", ".join(str(r) for r in reasons), file=sys.stderr)
            return 1
        if args.command == "host-proof-status" and getattr(args, "fail_if_incomplete", False) and isinstance(result, dict) and result.get("proof_complete") is not True:
            print("derive-runtime: host proof incomplete: " + str(result.get("status")), file=sys.stderr)
            return 1
        return 0
    except DeriveRuntimeError as exc:
        parser.exit(1, f"derive-runtime: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
