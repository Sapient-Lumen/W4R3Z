#!/usr/bin/env python3
"""Build release evidence from one declared Micromax source snapshot.

The lane captures source bytes once, materializes independent test/build/archive
copies, runs focused trust checks, builds the wheel twice under one declared
environment, verifies Wheel/RECORD integrity, and optionally asks ``mkrevzip`` to
embed the sealed receipt in the revision archive.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import re
import shutil
import sys
import tempfile
import time
import tomllib
import zipfile
import zlib
from collections import Counter
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from email.parser import Parser
from pathlib import Path
from typing import Mapping

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import mkrevzip  # noqa: E402
import mxbuilder  # noqa: E402
import mxrelease  # noqa: E402
from mxtoolrun import run_captured, tail_text  # noqa: E402

RUN_SCHEMA = "micromax.mxrepro.run.v1"
WHEEL_VERIFICATION_SCHEMA = "micromax.mxrepro.wheel-verification.v1"
DEFAULT_TIMEOUT_SECONDS = 600.0
DEFAULT_RECEIPT_NAME = "micromax-release-receipt.json"
DEFAULT_RUN_NAME = "micromax-repro-run.json"

FOCUSED_TESTS = [
    "tests/test_mxrepro.py",
    "tests/test_mkrevzip.py",
    "tests/test_mxrelease.py",
    "tests/test_installed_runtime_resources.py::test_pyproject_declares_bundled_runtime_resource_data_files",
    "tests/test_revision_index.py",
    "tests/test_docs_index.py",
    "tests/test_mxcontext.py",
    "tests/test_mxaudit.py",
    "tests/test_effect_contracts.py",
]


class ReproducibleReleaseError(ValueError):
    """Raised when snapshot, environment, test, wheel, or archive evidence fails."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _release_table(root: Path) -> dict[str, object]:
    try:
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ReproducibleReleaseError(f"could not read pyproject release policy: {exc}") from exc
    tool = data.get("tool") if isinstance(data.get("tool"), dict) else {}
    micromax = tool.get("micromax") if isinstance(tool.get("micromax"), dict) else {}
    release = micromax.get("release") if isinstance(micromax.get("release"), dict) else {}
    return dict(release)


def _actual_builder_versions(projects: list[str]) -> dict[str, str]:
    """Return the interpreter and installed package versions under test."""

    versions = {"python": platform.python_version()}
    for project in projects:
        try:
            versions[project] = importlib.metadata.version(project)
        except importlib.metadata.PackageNotFoundError as exc:
            raise ReproducibleReleaseError(
                f"declared builder package is not installed: {project}"
            ) from exc
    return versions


def _read_builder_receipt(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReproducibleReleaseError(f"builder receipt is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise ReproducibleReleaseError("builder receipt must be a JSON object")
    try:
        mxbuilder.validate_receipt_digest(value)
    except mxbuilder.BuilderError as exc:
        raise ReproducibleReleaseError(str(exc)) from exc
    return value


def validate_builder_receipt(
    path: Path,
    *,
    package_inputs: Mapping[str, object],
    expected_python: str,
    actual_versions: Mapping[str, str],
    expected_receipt_digest: str | None = None,
) -> dict[str, object]:
    """Bind the release claim to the exact acquired wheel bytes."""

    receipt = _read_builder_receipt(path)
    if (
        expected_receipt_digest is not None
        and receipt.get("receipt_digest") != expected_receipt_digest
    ):
        raise ReproducibleReleaseError(
            "builder receipt digest does not match the launch capability"
        )
    if receipt.get("schema") != mxbuilder.SCHEMA or receipt.get("ok") is not True:
        raise ReproducibleReleaseError("builder receipt schema/status is invalid")
    expected_lock = package_inputs.get("builder_lock")
    if not isinstance(expected_lock, dict) or receipt.get("lock") != expected_lock:
        raise ReproducibleReleaseError(
            "builder receipt lock does not match the captured source lock"
        )
    python_row = receipt.get("python")
    if not isinstance(python_row, dict) or python_row.get("version") != expected_python:
        raise ReproducibleReleaseError("builder receipt Python does not match policy")
    entries = expected_lock.get("entries")
    if not isinstance(entries, list):
        raise ReproducibleReleaseError("builder lock descriptor has no entries")
    expected = {
        str(row.get("name") or ""): str(row.get("version") or "")
        for row in entries
        if isinstance(row, dict)
    }
    installed = receipt.get("installed")
    if not isinstance(installed, dict) or {
        str(key): str(value) for key, value in installed.items()
    } != expected:
        raise ReproducibleReleaseError("builder receipt installed versions differ from lock")
    for name, version in expected.items():
        if actual_versions.get(name) != version:
            raise ReproducibleReleaseError(
                f"current builder package {name}={actual_versions.get(name)!r} "
                f"does not match locked {version!r}"
            )
    wheels = receipt.get("wheels")
    if not isinstance(wheels, list):
        raise ReproducibleReleaseError("builder receipt has no wheel list")
    lock_by_name = {
        str(row.get("name") or ""): row for row in entries if isinstance(row, dict)
    }
    seen: set[str] = set()
    for wheel in wheels:
        if not isinstance(wheel, dict):
            raise ReproducibleReleaseError("builder receipt wheel row is invalid")
        project = str(wheel.get("project") or "")
        authority = lock_by_name.get(project)
        if authority is None or project in seen:
            raise ReproducibleReleaseError(
                f"builder receipt has unexpected/duplicate wheel: {project!r}"
            )
        digest = str(wheel.get("sha256") or "")
        hashes = authority.get("hashes")
        filename = str(wheel.get("filename") or "")
        if (
            wheel.get("version") != authority.get("version")
            or not isinstance(hashes, list)
            or digest not in hashes
            or not isinstance(wheel.get("bytes"), int)
            or isinstance(wheel.get("bytes"), bool)
            or int(wheel["bytes"]) <= 0
            or not filename
            or "/" in filename
            or "\\" in filename
            or "\x00" in filename
            or Path(filename).name != filename
        ):
            raise ReproducibleReleaseError(
                f"builder receipt wheel authority is invalid for {project!r}"
            )
        seen.add(project)
    if seen != set(expected):
        raise ReproducibleReleaseError("builder receipt wheel set is incomplete")
    boundary = receipt.get("network_boundary")
    if boundary != {
        "acquisition": "hash-checked-wheel-download-only",
        "installation": "verified-wheelhouse-pip-no-index",
        "pip_bootstrap": "safe-extract-verified-wheel",
    }:
        raise ReproducibleReleaseError("builder receipt network boundary is invalid")
    wheelhouse = receipt.get("wheelhouse_verification")
    expected_limits = {
        "wheel_bytes": mxbuilder.MAX_WHEEL_BYTES,
        "members": mxbuilder.MAX_WHEEL_MEMBERS,
        "member_bytes": mxbuilder.MAX_WHEEL_MEMBER_BYTES,
        "expanded_bytes": mxbuilder.MAX_WHEEL_UNCOMPRESSED_BYTES,
        "metadata_bytes": mxbuilder.MAX_METADATA_BYTES,
    }
    if (
        not isinstance(wheelhouse, dict)
        or wheelhouse.get("phase")
        != "identical-before-bootstrap-and-after-install"
        or wheelhouse.get("permission_boundary")
        not in {"private-posix-read-only", "platform-best-effort"}
        or wheelhouse.get("limits") != expected_limits
    ):
        raise ReproducibleReleaseError(
            "builder receipt wheelhouse verification is invalid"
        )
    return receipt


def declared_environment(
    root: Path,
    *,
    builder_receipt_path: Path | None = None,
    require_builder_receipt: bool = False,
) -> dict[str, object]:
    """Return and validate the byte-bound local builder declaration."""

    package_inputs = mxrelease.package_input_report(root)
    if package_inputs.get("ok") is not True:
        issues = package_inputs.get("issues")
        detail = (
            "; ".join(str(item) for item in issues)
            if isinstance(issues, list)
            else "unknown policy failure"
        )
        raise ReproducibleReleaseError("package input policy failed: " + detail)

    release = _release_table(root)
    epoch = release.get("source_date_epoch")
    expected = {
        "python": str(release.get("builder_python") or ""),
        "pip": str(release.get("builder_pip") or ""),
        "setuptools": str(release.get("builder_setuptools") or ""),
        "pytest": str(release.get("builder_pytest") or ""),
    }
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < mkrevzip.MIN_ZIP_EPOCH:
        raise ReproducibleReleaseError("source_date_epoch is missing or outside the ZIP range")
    for name, value in expected.items():
        if not value:
            raise ReproducibleReleaseError(f"builder_{name} is not declared")
    for key, expected_value in (
        ("builder_python", expected["python"]),
        ("builder_pip", expected["pip"]),
        ("builder_setuptools", expected["setuptools"]),
        ("builder_pytest", expected["pytest"]),
    ):
        if str(package_inputs.get(key) or "") != expected_value:
            raise ReproducibleReleaseError(
                f"{key} does not match the validated release policy"
            )

    lock = package_inputs.get("builder_lock")
    entries = lock.get("entries") if isinstance(lock, dict) else None
    if not isinstance(entries, list):
        raise ReproducibleReleaseError("validated package policy omitted builder lock rows")
    locked_versions = {
        str(row.get("name") or ""): str(row.get("version") or "")
        for row in entries
        if isinstance(row, dict)
    }
    projects = sorted(locked_versions)
    actual = _actual_builder_versions(projects)
    problems: list[str] = []
    if actual["python"] != expected["python"]:
        problems.append(f"python={actual['python']} expected {expected['python']}")
    for name, version in locked_versions.items():
        if actual.get(name) != version:
            problems.append(f"{name}={actual.get(name)} expected {version}")
    if problems:
        raise ReproducibleReleaseError(
            "current builder does not match the declared environment: "
            + "; ".join(problems)
        )

    receipt_path = builder_receipt_path
    launch_digest: str | None = None
    if receipt_path is None:
        raw = os.environ.get("MICROMAX_BUILDER_RECEIPT", "").strip()
        receipt_path = Path(raw) if raw else None
        if receipt_path is not None:
            launch_digest = os.environ.get(
                "MICROMAX_BUILDER_RECEIPT_DIGEST", ""
            ).strip()
            if len(launch_digest) != 64 or any(
                char not in "0123456789abcdef" for char in launch_digest
            ):
                raise ReproducibleReleaseError(
                    "builder launch omitted a valid receipt digest capability"
                )
    snapshot: dict[str, object] | None = None
    if receipt_path is not None:
        snapshot = validate_builder_receipt(
            receipt_path,
            package_inputs=package_inputs,
            expected_python=expected["python"],
            actual_versions=actual,
            expected_receipt_digest=launch_digest,
        )
    elif require_builder_receipt:
        raise ReproducibleReleaseError(
            "release must run through tools/mxbuilder.py so wheel bytes are receipted"
        )

    return {
        "python": actual["python"],
        "python_declared": expected["python"],
        "implementation": platform.python_implementation(),
        "python_cache_tag": str(getattr(sys.implementation, "cache_tag", "")),
        "pip": actual["pip"],
        "setuptools": actual["setuptools"],
        "pytest": actual["pytest"],
        "installed": {project: actual[project] for project in projects},
        "zlib_compile": str(zlib.ZLIB_VERSION),
        "zlib_runtime": str(zlib.ZLIB_RUNTIME_VERSION),
        "platform_system": platform.system(),
        "platform_machine": platform.machine(),
        "source_date_epoch": int(epoch),
        "timezone": "UTC",
        "python_hash_seed": "0",
        "wheel_frontend": str(package_inputs.get("wheel_build_frontend") or ""),
        "build_backend": str(package_inputs.get("build_backend") or ""),
        "build_backend_requirement": str(
            package_inputs.get("build_backend_requirement") or ""
        ),
        "builder_snapshot": snapshot,
    }


def deterministic_env(root: Path, *, source_date_epoch: int, home: Path) -> dict[str, str]:
    """Return the process environment shared by tests and both wheel builds."""

    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    # Do not inherit unrelated source trees from the cloud/container host.  The
    # one materialized snapshot is the only project import root.
    env["PYTHONPATH"] = str(root / "src")
    env.update(
        {
            "SOURCE_DATE_EPOCH": str(int(source_date_epoch)),
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "TZ": "UTC",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
            "HOME": str(home),
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_CACHE_DIR": "1",
            "PIP_NO_INDEX": "1",
            "PYTHONNOUSERSITE": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "BLIS_NUM_THREADS": "1",
        }
    )
    return env


def _normalize_tree_times(root: Path, *, source_date_epoch: int) -> None:
    """Remove materialization time as an undeclared backend input."""

    timestamp = float(source_date_epoch)
    paths = sorted(root.rglob("*"), key=lambda path: len(path.parts), reverse=True)
    for path in paths:
        os.utime(path, (timestamp, timestamp), follow_symlinks=False)
    os.utime(root, (timestamp, timestamp), follow_symlinks=False)


def _rows_identity(rows: list[dict[str, object]]) -> dict[str, tuple[int, str]]:
    identity: dict[str, tuple[int, str]] = {}
    for row in rows:
        path = str(row.get("path") or "")
        if not path or path in identity:
            raise ReproducibleReleaseError("source rows contain an empty or duplicate path")
        identity[path] = (int(row.get("bytes") or 0), str(row.get("sha256") or ""))
    return identity


def _verify_snapshot_modes(
    root: Path,
    *,
    rows: list[dict[str, object]],
    phase: str,
) -> None:
    """Reject materialized source whose declared members escaped mode policy."""

    if os.name != "posix":
        return
    expected_files = [str(row.get("path") or "") for row in rows]
    expected_files.append("MICROMAX-CONTEXT.json")
    directories: set[Path] = {root}
    for rel_text in expected_files:
        path = root / rel_text
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            raise ReproducibleReleaseError(
                f"declared source mode is unreadable during {phase}: {rel_text}: {exc}"
            ) from exc
        if not path.is_file() or path.is_symlink():
            raise ReproducibleReleaseError(
                f"declared source member is not a regular file during {phase}: {rel_text}"
            )
        actual_mode = mode & 0o7777
        if actual_mode != mkrevzip.SNAPSHOT_FILE_MODE:
            raise ReproducibleReleaseError(
                f"declared source file mode changed during {phase}: "
                f"{rel_text}={actual_mode:04o} expected {mkrevzip.SNAPSHOT_FILE_MODE:04o}"
            )
        current = path.parent
        while current != root.parent:
            directories.add(current)
            if current == root:
                break
            current = current.parent
    for directory in sorted(directories):
        try:
            mode = directory.lstat().st_mode
        except OSError as exc:
            raise ReproducibleReleaseError(
                f"declared source directory mode is unreadable during {phase}: {directory}: {exc}"
            ) from exc
        actual_mode = mode & 0o7777
        if actual_mode != mkrevzip.SNAPSHOT_DIR_MODE:
            try:
                rel = directory.relative_to(root).as_posix() or "."
            except ValueError:
                rel = str(directory)
            raise ReproducibleReleaseError(
                f"declared source directory mode changed during {phase}: "
                f"{rel}={actual_mode:04o} expected {mkrevzip.SNAPSHOT_DIR_MODE:04o}"
            )


def verify_snapshot(
    root: Path,
    *,
    rows: list[dict[str, object]],
    context_bytes: bytes,
    phase: str,
) -> None:
    """Fail unless a materialized copy is exactly the declared source."""

    actual = mkrevzip.archive_member_rows(
        root,
        manifest_rel=Path("MICROMAX-CONTEXT.json"),
    )
    expected_by_path = _rows_identity(rows)
    actual_by_path = _rows_identity(actual)
    if actual_by_path != expected_by_path:
        missing = sorted(set(expected_by_path) - set(actual_by_path))
        added = sorted(set(actual_by_path) - set(expected_by_path))
        changed = sorted(
            path
            for path in set(expected_by_path) & set(actual_by_path)
            if expected_by_path[path] != actual_by_path[path]
        )
        fragments: list[str] = []
        if missing:
            fragments.append("removed=" + ",".join(missing[:8]))
        if added:
            fragments.append("added=" + ",".join(added[:8]))
        if changed:
            fragments.append("changed=" + ",".join(changed[:8]))
        raise ReproducibleReleaseError(
            f"declared source changed during {phase}: " + "; ".join(fragments)
        )
    try:
        actual_context = (root / "MICROMAX-CONTEXT.json").read_bytes()
    except OSError as exc:
        raise ReproducibleReleaseError(f"snapshot context is unreadable during {phase}: {exc}") from exc
    if actual_context != context_bytes:
        raise ReproducibleReleaseError(
            f"declared context input changed during {phase}"
        )
    _verify_snapshot_modes(root, rows=rows, phase=phase)


def materialize_copy(
    source_root: Path,
    destination: Path,
    *,
    rows: list[dict[str, object]],
    context_bytes: bytes,
    source_date_epoch: int,
) -> None:
    """Create one exact working copy from the already captured snapshot."""

    mkrevzip.snapshot_archive_members(source_root, destination, rows)
    context_path = destination / "MICROMAX-CONTEXT.json"
    context_path.write_bytes(context_bytes)
    os.chmod(context_path, 0o644)
    _normalize_tree_times(destination, source_date_epoch=source_date_epoch)
    verify_snapshot(
        destination,
        rows=rows,
        context_bytes=context_bytes,
        phase="snapshot materialization",
    )


def capture_source(
    root: Path,
    destination: Path,
    *,
    source_date_epoch: int,
    env: dict[str, str],
    timeout_seconds: float,
    log_path: Path,
) -> tuple[
    list[dict[str, object]],
    bytes,
    dict[str, object],
    dict[str, object],
]:
    """Capture the source once and return rows, context bytes, and identity."""

    revision = mkrevzip.infer_rev(root)
    rows = mkrevzip.archive_member_rows(
        root,
        manifest_rel=Path("MICROMAX-CONTEXT.json"),
    )
    provenance = mkrevzip.archive_member_provenance(rows)
    mkrevzip.snapshot_archive_members(root, destination, rows)
    mkrevzip.assert_source_tree_unchanged(
        root,
        manifest_rel=Path("MICROMAX-CONTEXT.json"),
        expected_rows=rows,
        phase="release source byte capture",
    )

    # Generate the excluded context exactly once *from the captured bytes*.
    # Seeding its path preserves the ordinary repository shape while the live
    # context is deliberately not trusted as source truth.
    context_path = destination / "MICROMAX-CONTEXT.json"
    context_path.write_text("{}\n", encoding="utf-8")
    context_argv = [
        sys.executable,
        "tools/mxcontext.py",
        "--json",
        "--check",
    ]
    result = run_captured(
        context_argv,
        cwd=destination,
        env=env,
        timeout_seconds=timeout_seconds,
        label="source-context",
        heartbeat_seconds=30.0,
        heartbeat_prefix="mxrepro",
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.output, encoding="utf-8")
    if result.returncode != 0 or result.timed_out:
        status = "timed out" if result.timed_out else f"returned {result.returncode}"
        raise ReproducibleReleaseError(
            f"source-context {status}:\n{tail_text(result.output)}"
        )
    try:
        context = json.loads(result.output)
    except json.JSONDecodeError as exc:
        raise ReproducibleReleaseError("source-context did not emit valid JSON") from exc
    if not isinstance(context, dict) or context.get("project") != "micromax":
        raise ReproducibleReleaseError("source-context did not emit a Micromax context")
    checks = context.get("checks")
    if not isinstance(checks, dict) or checks.get("ok") is not True:
        raise ReproducibleReleaseError("source-context reports failed repository checks")
    context_bytes = mkrevzip.context_input_bytes(context)
    context_path.write_bytes(context_bytes)
    os.chmod(context_path, 0o644)
    _normalize_tree_times(destination, source_date_epoch=source_date_epoch)

    source = mkrevzip.release_source_descriptor(
        provenance=provenance,
        context=context,
        revision=revision,
        context_path="MICROMAX-CONTEXT.json",
        source_date_epoch=int(source_date_epoch),
        epoch_origin="pyproject:[tool.micromax.release].source_date_epoch",
    )
    verify_snapshot(
        destination,
        rows=rows,
        context_bytes=context_bytes,
        phase="release source capture",
    )
    mkrevzip.assert_source_tree_unchanged(
        root,
        manifest_rel=Path("MICROMAX-CONTEXT.json"),
        expected_rows=rows,
        phase="release source capture",
    )
    return rows, context_bytes, source, _command_record("source-context", context_argv)


def _command_record(label: str, argv: list[str]) -> dict[str, object]:
    normalized: list[str] = []
    for index, value in enumerate(argv):
        text = str(value)
        if index == 0:
            normalized.append("python")
        elif os.path.isabs(text):
            normalized.append("<absolute-path>")
        else:
            normalized.append(text)
    return {"label": label, "argv": normalized, "returncode": 0}


def run_checked(
    label: str,
    argv: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout_seconds: float,
    log_path: Path,
) -> dict[str, object]:
    """Run one bounded process, persist its log, and return deterministic evidence."""

    result = run_captured(
        argv,
        cwd=cwd,
        env=env,
        timeout_seconds=timeout_seconds,
        label=label,
        heartbeat_seconds=30.0,
        heartbeat_prefix="mxrepro",
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.output, encoding="utf-8")
    if result.returncode != 0 or result.timed_out:
        status = "timed out" if result.timed_out else f"returned {result.returncode}"
        raise ReproducibleReleaseError(
            f"{label} {status}:\n{tail_text(result.output)}"
        )
    return _command_record(label, argv)


def run_focused_tests(
    root: Path,
    *,
    env: dict[str, str],
    timeout_seconds: float,
    logs: Path,
) -> dict[str, object]:
    """Run the small release-source lane from one snapshot copy."""

    commands: list[dict[str, object]] = []
    steps = [
        ("context-check", [sys.executable, "tools/mxcontext.py", "--check"]),
        ("structural-audit", [sys.executable, "tools/mxaudit.py", "--check"]),
        ("effect-contracts", [sys.executable, "tools/mxeffects.py", "--check"]),
        (
            "focused-pytest",
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                *FOCUSED_TESTS,
            ],
        ),
    ]
    for label, argv in steps:
        commands.append(
            run_checked(
                label,
                argv,
                cwd=root,
                env=env,
                timeout_seconds=timeout_seconds,
                log_path=logs / f"{label}.log",
            )
        )
    return {
        "ok": True,
        "lane": "focused-release-source",
        "test_files": list(FOCUSED_TESTS),
        "commands": commands,
    }


def _expected_zip_datetime(source_date_epoch: int) -> tuple[int, int, int, int, int, int]:
    moment = datetime.fromtimestamp(int(source_date_epoch), tz=timezone.utc)
    second = moment.second - (moment.second % 2)
    return (moment.year, moment.month, moment.day, moment.hour, moment.minute, second)


def _record_digest(data: bytes) -> str:
    encoded = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return "sha256=" + encoded.decode("ascii")


def verify_wheel(path: Path, *, source_date_epoch: int) -> dict[str, object]:
    """Verify wheel ZIP safety, metadata, normalized time, and every RECORD row."""

    wheel_path = Path(path)
    raw = wheel_path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        if duplicates:
            raise ReproducibleReleaseError(
                "wheel contains duplicate members: " + ", ".join(duplicates[:5])
            )
        for info in infos:
            reason = mkrevzip._unsafe_member_reason(info.filename)
            if reason is not None:
                raise ReproducibleReleaseError(
                    f"unsafe wheel member {info.filename!r}: {reason}"
                )
            if info.is_dir():
                raise ReproducibleReleaseError(
                    f"wheel contains an unexpected directory member: {info.filename}"
                )
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ReproducibleReleaseError(f"wheel CRC check failed for: {bad_member}")
        if any(name.endswith((".pyc", ".pyo")) or "/__pycache__/" in name for name in names):
            raise ReproducibleReleaseError("wheel contains Python bytecode/cache members")

        dist_info_roots = {
            name.split("/", 1)[0]
            for name in names
            if ".dist-info/" in name and name.split("/", 1)[0].endswith(".dist-info")
        }
        if len(dist_info_roots) != 1:
            raise ReproducibleReleaseError(
                f"wheel must contain exactly one dist-info root, got {sorted(dist_info_roots)!r}"
            )
        dist_info = next(iter(dist_info_roots))
        record_name = f"{dist_info}/RECORD"
        metadata_name = f"{dist_info}/METADATA"
        wheel_name = f"{dist_info}/WHEEL"
        for required in (record_name, metadata_name, wheel_name):
            if required not in names:
                raise ReproducibleReleaseError(f"wheel is missing mandatory member: {required}")

        try:
            record_text = archive.read(record_name).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ReproducibleReleaseError("wheel RECORD is not UTF-8") from exc
        rows: dict[str, tuple[str, str]] = {}
        for csv_row in csv.reader(io.StringIO(record_text, newline="")):
            if len(csv_row) != 3:
                raise ReproducibleReleaseError("wheel RECORD row does not have three columns")
            member, digest, size = csv_row
            if member in rows:
                raise ReproducibleReleaseError(f"wheel RECORD duplicates path: {member}")
            rows[member] = (digest, size)
        if set(rows) != set(names):
            missing = sorted(set(names) - set(rows))
            extra = sorted(set(rows) - set(names))
            raise ReproducibleReleaseError(
                "wheel RECORD membership mismatch: "
                + ("missing=" + ",".join(missing[:5]) if missing else "")
                + ("; " if missing and extra else "")
                + ("extra=" + ",".join(extra[:5]) if extra else "")
            )
        for info in infos:
            member = info.filename
            digest, size = rows[member]
            if member == record_name:
                if digest or size:
                    raise ReproducibleReleaseError("wheel RECORD self-row must omit hash and size")
                continue
            data = archive.read(info)
            if digest != _record_digest(data):
                raise ReproducibleReleaseError(f"wheel RECORD digest mismatch: {member}")
            if size != str(len(data)):
                raise ReproducibleReleaseError(f"wheel RECORD size mismatch: {member}")

        expected_time = _expected_zip_datetime(source_date_epoch)
        actual_times = {info.date_time for info in infos}
        if actual_times != {expected_time}:
            raise ReproducibleReleaseError(
                f"wheel timestamps are not normalized to SOURCE_DATE_EPOCH: {sorted(actual_times)!r}"
            )

        metadata = Parser().parsestr(archive.read(metadata_name).decode("utf-8"))
        if metadata.get("License-Expression") != "MIT":
            raise ReproducibleReleaseError("wheel METADATA does not declare License-Expression: MIT")
        license_files = metadata.get_all("License-File") or []
        if license_files != ["LICENSE"]:
            raise ReproducibleReleaseError(
                f"wheel METADATA must declare exactly License-File: LICENSE; got {license_files!r}"
            )
        if f"{dist_info}/licenses/LICENSE" not in names:
            raise ReproducibleReleaseError(
                "wheel does not carry LICENSE in the standardized dist-info/licenses directory"
            )
        wheel_metadata = Parser().parsestr(archive.read(wheel_name).decode("utf-8"))
        if wheel_metadata.get("Wheel-Version") != "1.0":
            raise ReproducibleReleaseError("wheel metadata has an unsupported Wheel-Version")

        package_name = str(metadata.get("Name") or "")
        if package_name.lower() == "micromax":
            required_members = {
                "micromax/stdlib/core.mx",
                "micromax_editor/resource_roots.py",
                "micromax_editor/screen_budget.py",
                "micromax_editor/screen_consumer.py",
                "micromax_editor/screen_contract.py",
                "micromax_editor/schemas/micromax-screen-v1.schema.json",
                f"{dist_info}/entry_points.txt",
            }
            missing_members = sorted(required_members - set(names))
            if missing_members:
                raise ReproducibleReleaseError(
                    "Micromax wheel is missing runtime members: "
                    + ", ".join(missing_members)
                )
            required_suffixes = (
                "/share/micromax/docs/00-vision.md",
                "/share/micromax/docs/security-boundaries.md",
                "/share/micromax/docs/33-effect-resource-contract.md",
                "/share/micromax/plugins/core/init.mx",
                "/share/micromax/plugins/core/plugin.json",
                "/share/micromax/plugins/capdemo/init.mx",
                "/share/micromax/plugins/capdemo/plugin.json",
            )
            missing_suffixes = [
                suffix
                for suffix in required_suffixes
                if not any(name.endswith(suffix) for name in names)
            ]
            if missing_suffixes:
                raise ReproducibleReleaseError(
                    "Micromax wheel is missing installed resources: "
                    + ", ".join(missing_suffixes)
                )
            entry_points = archive.read(f"{dist_info}/entry_points.txt").decode("utf-8")
            required_entry_points = (
                "micromax = micromax.repl:main",
                "micromax-editor = micromax_editor.__main__:main",
                "micromax-screen = micromax_editor.screen_consumer:main",
            )
            missing_entry_points = [
                value for value in required_entry_points if value not in entry_points
            ]
            if missing_entry_points:
                raise ReproducibleReleaseError(
                    "Micromax wheel is missing console entry points: "
                    + ", ".join(missing_entry_points)
                )

    return {
        "schema": WHEEL_VERIFICATION_SCHEMA,
        "filename": wheel_path.name,
        "sha256": _sha256_bytes(raw),
        "bytes": len(raw),
        "member_count": len(names),
        "record_entries": len(rows),
        "normalized_timestamp": "%04d-%02d-%02dT%02d:%02d:%02dZ" % expected_time,
        "package": package_name,
        "version": str(metadata.get("Version") or ""),
        "license_expression": str(metadata.get("License-Expression") or ""),
    }


def verify_installed_wheel(
    wheel: Path,
    *,
    target: Path,
    run_dir: Path,
    env: dict[str, str],
    timeout_seconds: float,
    logs: Path,
) -> dict[str, object]:
    """Install and execute the exact wheel selected for publication.

    This replaces a third source build in the focused lane.  The probe starts
    Python in isolated mode outside the checkout, inserts only the fresh target
    install, and verifies the VM, editor screen contract, curated docs, and
    bundled plugins from that artifact.
    """

    target.mkdir(parents=True, exist_ok=False)
    run_dir.mkdir(parents=True, exist_ok=False)
    install_argv = [
        sys.executable,
        "-m",
        "pip",
        "--isolated",
        "install",
        "--no-index",
        "--no-deps",
        "--no-compile",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--target",
        str(target),
        str(Path(wheel).resolve()),
    ]
    install_command = run_checked(
        "published-wheel-install",
        install_argv,
        cwd=run_dir,
        env=env,
        timeout_seconds=timeout_seconds,
        log_path=logs / "published-wheel-install.log",
    )

    probe = r'''
import json
from pathlib import Path
import sys

target = Path(sys.argv[1]).resolve()
outside = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(target))

import micromax
import micromax_editor
from micromax import VM
from micromax_editor import Editor
from micromax_editor.resource_roots import default_docs_root, default_plugins_root
from micromax_editor.screen_consumer import screen_contract_summary
from micromax_editor.screen_contract import load_screen_contract_schema

vm = VM(strict_stdlib=True)
editor = Editor()
editor.new_buffer("*release-probe*", "artifact\n")
summary = screen_contract_summary(editor.screen_contract(4, 24))
schema = load_screen_contract_schema()
docs = default_docs_root(cwd=outside)
plugins = default_plugins_root(cwd=outside)

payload = {
    "imports_from_target": (
        Path(micromax.__file__).resolve().is_relative_to(target)
        and Path(micromax_editor.__file__).resolve().is_relative_to(target)
    ),
    "stdlib_state": vm.stdlib_health()["state"],
    "startup_diagnostics": vm.startup_diagnostics,
    "has_finally": vm.find_word("finally") is not None,
    "has_2drop": vm.find_word("2drop") is not None,
    "screen_schema": schema["properties"]["schema"]["const"],
    "screen_rows": summary["rows"],
    "docs_from_target": docs.resolve().is_relative_to(target),
    "vision_doc": (docs / "00-vision.md").is_file(),
    "security_doc": (docs / "security-boundaries.md").is_file(),
    "effect_contract_doc": (docs / "33-effect-resource-contract.md").is_file(),
    "effect_contract_has_fs_read": "ed.fs-read" in (
        docs / "33-effect-resource-contract.md"
    ).read_text(encoding="utf-8"),
    "plugins_from_target": plugins.resolve().is_relative_to(target),
    "core_plugin": (plugins / "core" / "init.mx").is_file(),
    "capdemo_plugin": (plugins / "capdemo" / "plugin.json").is_file(),
}
print(json.dumps(payload, sort_keys=True))
'''.strip()
    probe_argv = [
        sys.executable,
        "-I",
        "-c",
        probe,
        str(target),
        str(run_dir),
    ]
    result = run_captured(
        probe_argv,
        cwd=run_dir,
        env=env,
        timeout_seconds=timeout_seconds,
        label="published-wheel-runtime",
        heartbeat_seconds=30.0,
        heartbeat_prefix="mxrepro",
    )
    probe_log = logs / "published-wheel-runtime.log"
    probe_log.parent.mkdir(parents=True, exist_ok=True)
    probe_log.write_text(result.output, encoding="utf-8")
    if result.returncode != 0 or result.timed_out:
        status = "timed out" if result.timed_out else f"returned {result.returncode}"
        raise ReproducibleReleaseError(
            f"published-wheel-runtime {status}:\n{tail_text(result.output)}"
        )
    try:
        payload = json.loads(result.output)
    except json.JSONDecodeError as exc:
        raise ReproducibleReleaseError(
            "published wheel runtime probe did not emit valid JSON"
        ) from exc
    expected = {
        "imports_from_target": True,
        "stdlib_state": "loaded",
        "startup_diagnostics": [],
        "has_finally": True,
        "has_2drop": True,
        "screen_schema": "micromax.screen.v1",
        "screen_rows": 4,
        "docs_from_target": True,
        "vision_doc": True,
        "security_doc": True,
        "effect_contract_doc": True,
        "effect_contract_has_fs_read": True,
        "plugins_from_target": True,
        "core_plugin": True,
        "capdemo_plugin": True,
    }
    if payload != expected:
        raise ReproducibleReleaseError(
            "published wheel runtime probe disagrees with the install contract: "
            + json.dumps(payload, ensure_ascii=False, sort_keys=True)
        )
    return {
        "ok": True,
        "wheel_sha256": _sha256_file(Path(wheel)),
        "install": install_command,
        "runtime": _command_record("published-wheel-runtime", probe_argv),
        "checks": payload,
    }


def build_wheel(
    root: Path,
    *,
    wheelhouse: Path,
    env: dict[str, str],
    timeout_seconds: float,
    log_path: Path,
    source_date_epoch: int,
) -> tuple[Path, dict[str, object], dict[str, object]]:
    """Build and verify exactly one wheel from a fresh snapshot copy."""

    wheelhouse.mkdir(parents=True, exist_ok=False)
    argv = [
        sys.executable,
        "-m",
        "pip",
        "--isolated",
        "wheel",
        "--no-index",
        "--no-deps",
        "--no-build-isolation",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--wheel-dir",
        str(wheelhouse),
        str(root),
    ]
    command = run_checked(
        "wheel-build",
        argv,
        cwd=root.parent,
        env=env,
        timeout_seconds=timeout_seconds,
        log_path=log_path,
    )
    wheels = sorted(wheelhouse.glob("*.whl"))
    if len(wheels) != 1:
        raise ReproducibleReleaseError(
            f"wheel build produced {len(wheels)} wheel files instead of one"
        )
    wheel = wheels[0]
    return wheel, verify_wheel(wheel, source_date_epoch=source_date_epoch), command


def build_revision_archive(
    root: Path,
    *,
    outdir: Path,
    tag: str,
    stamp: str,
    timezone_name: str,
    receipt_path: Path,
    env: dict[str, str],
    timeout_seconds: float,
    log_path: Path,
    expected_source_digest: str,
    expected_receipt_digest: str,
) -> tuple[Path, dict[str, object], dict[str, object]]:
    """Build and verify one revision archive from a fresh snapshot copy."""

    outdir.mkdir(parents=True, exist_ok=False)
    argv = [
        sys.executable,
        "tools/mkrevzip.py",
        "--tag",
        str(tag),
        "--stamp",
        str(stamp),
        "--tz",
        str(timezone_name),
        "--outdir",
        str(outdir),
        "--release-receipt",
        str(receipt_path),
    ]
    result = run_captured(
        argv,
        cwd=root,
        env=env,
        timeout_seconds=timeout_seconds,
        label="revision-archive",
        heartbeat_seconds=30.0,
        heartbeat_prefix="mxrepro",
    )
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.output, encoding="utf-8")
    if result.returncode != 0 or result.timed_out:
        status = "timed out" if result.timed_out else f"returned {result.returncode}"
        raise ReproducibleReleaseError(
            f"revision-archive {status}:\n{tail_text(result.output)}"
        )
    candidates = [
        Path(line.strip())
        for line in result.output.splitlines()
        if line.strip().endswith(".zip")
    ]
    if len(candidates) != 1:
        raise ReproducibleReleaseError(
            f"revision archive command reported {len(candidates)} output paths instead of one"
        )
    archive_path = candidates[0]
    if not archive_path.is_file() or archive_path.parent.resolve() != outdir.resolve():
        raise ReproducibleReleaseError(
            "revision archive command reported a path outside its private output directory"
        )
    verification = mkrevzip.verify_archive(archive_path)
    if verification.get("source_digest") != expected_source_digest:
        raise ReproducibleReleaseError(
            "archive source digest does not match the tested source"
        )
    if verification.get("release_receipt_digest") != expected_receipt_digest:
        raise ReproducibleReleaseError(
            "archive receipt digest does not match the tested receipt"
        )
    return archive_path, verification, _command_record("revision-archive", argv)


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise ReproducibleReleaseError(f"refusing to overwrite release evidence: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise ReproducibleReleaseError(f"refusing stale release temporary: {temporary}")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _copy_artifact(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        raise ReproducibleReleaseError(f"refusing to overwrite release artifact: {destination}")
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    if temporary.exists() or temporary.is_symlink():
        raise ReproducibleReleaseError(f"refusing stale release temporary: {temporary}")
    shutil.copyfile(source, temporary)
    os.replace(temporary, destination)


def create_release_receipt(
    *,
    source: dict[str, object],
    environment: dict[str, object],
    tests: dict[str, object],
    first_wheel: dict[str, object],
    second_wheel: dict[str, object],
    build_commands: list[dict[str, object]],
) -> dict[str, object]:
    """Create the compact source-test-wheel statement embedded in the archive."""

    if first_wheel != second_wheel:
        # Raw wheel identity is checked separately; equal verification records
        # also ensure the format/metadata claims did not vary between builds.
        raise ReproducibleReleaseError("verified wheel records are not identical")
    payload: dict[str, object] = {
        "schema": mkrevzip.RELEASE_RECEIPT_SCHEMA,
        "ok": True,
        "source": source,
        "builder": environment,
        "tests": tests,
        "wheels": {
            "reproducible": True,
            "first": first_wheel,
            "second": second_wheel,
            "commands": build_commands,
        },
    }
    return mkrevzip.seal_release_receipt(payload)


def resolve_archive_stamp(
    stamp: str | None,
    *,
    timezone_name: str,
    now: datetime | None = None,
) -> str:
    """Return a canonical archive stamp without relying on shell ``date``."""

    if stamp:
        return str(stamp)
    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ReproducibleReleaseError(
            f"archive timezone is unavailable: {timezone_name!r}"
        ) from exc
    moment = now if now is not None else datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(zone).strftime("%Y.%m.%d.%H.%M")


def run_release(
    root: Path,
    *,
    output_dir: Path,
    timeout_seconds: float,
    archive_tag: str | None = None,
    archive_stamp: str | None = None,
    archive_outdir: Path | None = None,
    archive_timezone: str = "America/New_York",
    keep_work: bool = False,
) -> dict[str, object]:
    """Execute the complete single-source release lane.

    Source bytes and generated context are captured once.  Tests, two wheel
    builds, and two archive builds receive independent copies of that capture.
    Nothing is published until both output pairs agree byte-for-byte and the
    live source still matches the captured member rows.
    """

    root = Path(root).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    environment = declared_environment(root, require_builder_receipt=True)
    epoch = int(environment["source_date_epoch"])
    revision = mkrevzip.infer_rev(root)

    if archive_stamp is not None and archive_tag is None:
        raise ReproducibleReleaseError(
            "archive_stamp cannot be supplied without archive_tag"
        )
    if archive_tag is not None:
        archive_stamp = resolve_archive_stamp(
            archive_stamp,
            timezone_name=archive_timezone,
        )
    archive_destination: Path | None = None
    archive_output: Path | None = None
    if archive_tag is not None and archive_stamp is not None:
        archive_name = (
            f"Micromax-rev{revision:04d}-{archive_stamp}-{archive_tag}.zip"
        )
        mkrevzip.parse_archive_name(archive_name)
        archive_destination = (
            Path(archive_outdir).resolve()
            if archive_outdir is not None
            else output_dir
        )
        archive_destination.mkdir(parents=True, exist_ok=True)
        archive_output = archive_destination / archive_name
        if archive_output.exists() or archive_output.is_symlink():
            raise ReproducibleReleaseError(
                f"refusing to overwrite release archive: {archive_output}"
            )

    receipt_output = output_dir / DEFAULT_RECEIPT_NAME
    run_output = output_dir / DEFAULT_RUN_NAME
    logs_output = output_dir / "logs"
    for path in (receipt_output, run_output, logs_output):
        if path.exists() or path.is_symlink():
            raise ReproducibleReleaseError(
                f"refusing to overwrite release output: {path}"
            )

    work_parent = output_dir
    if keep_work:
        work_root = output_dir / "work"
        if work_root.exists() or work_root.is_symlink():
            raise ReproducibleReleaseError(f"work directory already exists: {work_root}")
        work_root.mkdir()
        cleanup = None
    else:
        cleanup = tempfile.TemporaryDirectory(prefix=".tmp-mxrepro-", dir=work_parent)
        work_root = Path(cleanup.name)

    started = time.monotonic()
    try:
        homes = work_root / "homes"
        homes.mkdir()

        def phase_home(name: str) -> Path:
            home = homes / name
            home.mkdir(parents=False, exist_ok=False)
            return home

        logs = work_root / "logs"
        logs.mkdir()

        source_snapshot = work_root / "source-snapshot"
        source_env = deterministic_env(
            source_snapshot,
            source_date_epoch=epoch,
            home=phase_home("source-context"),
        )
        rows, context_bytes, source, context_command = capture_source(
            root,
            source_snapshot,
            source_date_epoch=epoch,
            env=source_env,
            timeout_seconds=timeout_seconds,
            log_path=logs / "source-context.log",
        )

        test_root = work_root / "test-source"
        materialize_copy(
            source_snapshot,
            test_root,
            rows=rows,
            context_bytes=context_bytes,
            source_date_epoch=epoch,
        )
        test_env = deterministic_env(
            test_root,
            source_date_epoch=epoch,
            home=phase_home("focused-tests"),
        )
        tests = run_focused_tests(
            test_root,
            env=test_env,
            timeout_seconds=timeout_seconds,
            logs=logs,
        )
        tests["source_context"] = context_command
        verify_snapshot(
            test_root,
            rows=rows,
            context_bytes=context_bytes,
            phase="focused tests",
        )

        wheel_records: list[dict[str, object]] = []
        wheel_paths: list[Path] = []
        build_commands: list[dict[str, object]] = []
        for label in ("first", "second"):
            build_root = work_root / f"wheel-{label}-source"
            materialize_copy(
                source_snapshot,
                build_root,
                rows=rows,
                context_bytes=context_bytes,
                source_date_epoch=epoch,
            )
            build_env = deterministic_env(
                build_root,
                source_date_epoch=epoch,
                home=phase_home(f"wheel-{label}"),
            )
            wheel, record, command = build_wheel(
                build_root,
                wheelhouse=work_root / f"wheel-{label}-house",
                env=build_env,
                timeout_seconds=timeout_seconds,
                log_path=logs / f"wheel-{label}.log",
                source_date_epoch=epoch,
            )
            verify_snapshot(
                build_root,
                rows=rows,
                context_bytes=context_bytes,
                phase=f"{label} wheel build",
            )
            wheel_paths.append(wheel)
            wheel_records.append(record)
            build_commands.append(command)

        first_wheel_bytes = wheel_paths[0].read_bytes()
        second_wheel_bytes = wheel_paths[1].read_bytes()
        if first_wheel_bytes != second_wheel_bytes:
            raise ReproducibleReleaseError(
                "two wheels from the declared source and environment are not byte-identical"
            )
        if wheel_records[0] != wheel_records[1]:
            raise ReproducibleReleaseError("two wheel verification records disagree")

        installed_probe_env = deterministic_env(
            work_root / "no-source-imports",
            source_date_epoch=epoch,
            home=phase_home("published-wheel-install"),
        )
        installed_probe_env["MICROMAX_INIT"] = str(
            work_root / "no-source-imports" / "missing-init.mx"
        )
        installed_probe_env.pop("MICROMAX_DOCS", None)
        tests["published_wheel"] = verify_installed_wheel(
            wheel_paths[0],
            target=work_root / "published-wheel-target",
            run_dir=work_root / "published-wheel-outside-source",
            env=installed_probe_env,
            timeout_seconds=timeout_seconds,
            logs=logs,
        )

        receipt = create_release_receipt(
            source=source,
            environment=environment,
            tests=tests,
            first_wheel=wheel_records[0],
            second_wheel=wheel_records[1],
            build_commands=build_commands,
        )
        staged_receipt = work_root / DEFAULT_RECEIPT_NAME
        _write_json(staged_receipt, receipt)

        archive_paths: list[Path] = []
        archive_verifications: list[dict[str, object]] = []
        archive_commands: list[dict[str, object]] = []
        if archive_tag is not None and archive_stamp is not None:
            for label in ("first", "second"):
                archive_root = work_root / f"archive-{label}-source"
                materialize_copy(
                    source_snapshot,
                    archive_root,
                    rows=rows,
                    context_bytes=context_bytes,
                    source_date_epoch=epoch,
                )
                archive_env = deterministic_env(
                    archive_root,
                    source_date_epoch=epoch,
                    home=phase_home(f"archive-{label}"),
                )
                archive, verification, command = build_revision_archive(
                    archive_root,
                    outdir=work_root / f"archive-{label}-output",
                    tag=archive_tag,
                    stamp=archive_stamp,
                    timezone_name=archive_timezone,
                    receipt_path=staged_receipt,
                    env=archive_env,
                    timeout_seconds=timeout_seconds,
                    log_path=logs / f"archive-{label}.log",
                    expected_source_digest=str(source["digest"]),
                    expected_receipt_digest=str(receipt["receipt_digest"]),
                )
                verify_snapshot(
                    archive_root,
                    rows=rows,
                    context_bytes=context_bytes,
                    phase=f"{label} archive build",
                )
                archive_paths.append(archive)
                archive_verifications.append(verification)
                archive_commands.append(command)

            if archive_paths[0].read_bytes() != archive_paths[1].read_bytes():
                raise ReproducibleReleaseError(
                    "two revision archives from the declared source are not byte-identical"
                )
            if archive_verifications[0] != archive_verifications[1]:
                raise ReproducibleReleaseError(
                    "two revision archive verification records disagree"
                )

        # Publication names the captured generation, not whatever happens to be
        # on disk after a long build.  Refuse publication when the live member
        # set or any member byte changed while the lane ran.
        mkrevzip.assert_source_tree_unchanged(
            root,
            manifest_rel=Path("MICROMAX-CONTEXT.json"),
            expected_rows=rows,
            phase="reproducible release publication gate",
        )

        wheel_output = output_dir / wheel_paths[0].name
        if wheel_output.exists() or wheel_output.is_symlink():
            raise ReproducibleReleaseError(
                f"refusing to overwrite release wheel: {wheel_output}"
            )

        elapsed = round(time.monotonic() - started, 3)
        run_payload: dict[str, object] = {
            "schema": RUN_SCHEMA,
            "ok": True,
            "source": source,
            "receipt": {
                "path": receipt_output.name,
                "sha256": _sha256_file(staged_receipt),
                "receipt_digest": receipt["receipt_digest"],
            },
            "wheel": {
                "path": wheel_output.name,
                "sha256": wheel_records[0]["sha256"],
                "bytes": wheel_records[0]["bytes"],
                "reproducible_pair": True,
                "independent_materializations": 2,
            },
            "elapsed_seconds": elapsed,
        }
        if archive_paths and archive_output is not None:
            run_payload["archive"] = {
                "path": str(archive_output),
                "sha256": _sha256_file(archive_paths[0]),
                "bytes": archive_paths[0].stat().st_size,
                "reproducible_pair": True,
                "independent_materializations": 2,
                "commands": archive_commands,
                "verification": archive_verifications[0],
            }

        staged_run = work_root / DEFAULT_RUN_NAME
        _write_json(staged_run, run_payload)

        # All gates passed.  Publish immutable evidence without silently
        # replacing a previous run.
        _copy_artifact(staged_receipt, receipt_output)
        _copy_artifact(wheel_paths[0], wheel_output)
        if archive_paths and archive_output is not None:
            _copy_artifact(archive_paths[0], archive_output)
        shutil.copytree(logs, logs_output)
        _copy_artifact(staged_run, run_output)
        return run_payload
    finally:
        if cleanup is not None:
            cleanup.cleanup()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT), help="source repository")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / ".artifacts" / "mxrepro"),
        help="wheel, receipt, logs, and run report output directory",
    )
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--archive-tag", default=None)
    parser.add_argument("--archive-stamp", default=None)
    parser.add_argument("--archive-outdir", default=None)
    parser.add_argument("--archive-timezone", default="America/New_York")
    parser.add_argument("--keep-work", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_release(
            Path(str(args.root)),
            output_dir=Path(str(args.output_dir)),
            timeout_seconds=float(args.timeout),
            archive_tag=str(args.archive_tag) if args.archive_tag else None,
            archive_stamp=str(args.archive_stamp) if args.archive_stamp else None,
            archive_outdir=Path(str(args.archive_outdir)) if args.archive_outdir else None,
            archive_timezone=str(args.archive_timezone),
            keep_work=bool(args.keep_work),
        )
    except (
        OSError,
        zipfile.BadZipFile,
        mkrevzip.ArchiveVerificationError,
        mkrevzip.RevisionLineageError,
        ReproducibleReleaseError,
    ) as exc:
        parser.exit(1, f"reproducible release failed: {exc}\n")
    archive = result.get("archive")
    if isinstance(archive, dict):
        print(str(archive.get("path") or ""))
    else:
        print(str(Path(str(args.output_dir)).resolve() / DEFAULT_RECEIPT_NAME))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
