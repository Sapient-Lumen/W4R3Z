#!/usr/bin/env python3
"""mxrelease: resumable full-suite evidence for short cloudtainers.

``mxtest`` remains the node/chunk harness, but whole-suite pytest collection can
be too large for a short interactive tooltimer. This release lane avoids global
collection by discovering ``tests/test*.py``, running bounded batches of selected
files in fresh pytest children, checkpointing after every batch, and verifying
that the completed manifest still matches the current source tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from mxtoolrun import format_duration, isolated_python_env, run_captured, tail_text, utc_now  # noqa: E402

from mxtest import (  # noqa: E402
    environment_manifest_payload,
    source_manifest_differences,
    source_manifest_issues,
    source_manifest_payload,
)

SCHEMA = "micromax.mxrelease.full-suite.v1"
PACKAGE_INPUT_SCHEMA = "micromax.mxrelease.package-inputs.v1"
PACKAGE_INPUT_POLICY_HASH_LOCKED_BUILDER = "hash-locked-release-builder"
PACKAGE_VERSION_POLICY_ARCHIVE_REV_INDEPENDENT = "archive-revision-independent"
PACKAGE_BUILD_BACKEND = "setuptools.build_meta"
PACKAGE_BUILD_BACKEND_REQUIREMENT = "setuptools>=77.0.3"
PACKAGE_WHEEL_FRONTEND = "pip-wheel-no-build-isolation"
PACKAGE_RELEASE_BUILDERS = (
    "builder_python",
    "builder_pip",
    "builder_setuptools",
    "builder_pytest",
)
BUILDER_LOCK_PATH = "release/requirements-builder.txt"
BUILDER_LOCK_PROJECTS = {
    "pip",
    "setuptools",
    "pytest",
    "iniconfig",
    "packaging",
    "pluggy",
    "pygments",
}
BUILDER_DECLARATION_KEYS = {
    "pip": "builder_pip",
    "setuptools": "builder_setuptools",
    "pytest": "builder_pytest",
}
PACKAGE_INPUT_FILES = [
    "pyproject.toml",
    "requirements-dev.txt",
    ".pre-commit-config.yaml",
    "Makefile",
    BUILDER_LOCK_PATH,
    "tools/mxbuilder.py",
    ".github/workflows/reproducible-release.yml",
]
LOCK_FILE_NAMES = {
    "Pipfile.lock",
    "poetry.lock",
    "pylock.toml",
    "requirements.lock",
    "requirements-builder.txt",
    "uv.lock",
}
UNPINNED_PRECOMMIT_REVS = {"", "head", "latest", "main", "master", "trunk"}
DEFAULT_MANIFEST = ".artifacts/mxrelease-full-suite.json"
DEFAULT_MAX_RUNTIME_SECONDS = 8.0
DEFAULT_BATCH_TIMEOUT_SECONDS = 20.0
DEFAULT_BATCH_SIZE = 12
SUMMARY_RE = re.compile(r"(?P<count>\d+)\s+(?P<name>passed|failed|skipped|xfailed|xpassed|error|errors)\b")
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
STATUS_ORDER = ["passed", "failed", "timed_out", "not_run"]


def isolated_env() -> dict[str, str]:
    """Return the deterministic pytest environment used by release children."""

    return isolated_python_env(ROOT)


def _read_toml(path: Path) -> dict[str, Any]:
    """Read a TOML file as an object, returning an empty object on absence."""

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if isinstance(data, dict):
        return data
    return {}


def _sha256_file(path: Path) -> str:
    """Return a SHA-256 hex digest for one package-input file."""

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_project_name(value: str) -> str:
    """Return the PEP 503 comparison key for one package project name."""

    return re.sub(r"[-_.]+", "-", str(value).strip()).lower()


def _logical_requirement_lines(path: Path) -> list[str]:
    """Join backslash continuations without accepting pip directives."""

    lines = path.read_text(encoding="utf-8").splitlines()
    logical: list[str] = []
    pending = ""
    for number, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            if pending:
                raise ValueError(f"comment/blank interrupts lock row before line {number}")
            continue
        continued = stripped.endswith("\\")
        fragment = stripped[:-1].rstrip() if continued else stripped
        if " #" in fragment:
            fragment = fragment.split(" #", 1)[0].rstrip()
        pending = (pending + " " + fragment).strip()
        if continued:
            continue
        logical.append(pending)
        pending = ""
    if pending:
        raise ValueError("unterminated backslash continuation in builder lock")
    return logical


def parse_builder_lock(path: Path) -> list[dict[str, Any]]:
    """Parse Micromax's narrow exact-wheel builder lock.

    This intentionally is not a second package manager.  Each logical row must
    be ``project==version`` followed only by one or more local SHA-256 hashes.
    URLs, markers, extras, editable/VCS rows, and pip options are rejected.
    """

    path = Path(path)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    requirement_re = re.compile(
        r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)=="
        r"(?P<version>[A-Za-z0-9][A-Za-z0-9.!+_-]*)$"
    )
    hash_re = re.compile(r"^--hash=sha256:(?P<digest>[0-9a-f]{64})$")
    for line in _logical_requirement_lines(path):
        tokens = line.split()
        if not tokens:
            continue
        match = requirement_re.fullmatch(tokens[0])
        if match is None:
            raise ValueError(f"builder lock row is not an exact project==version: {line!r}")
        name = canonical_project_name(match.group("name"))
        if name in seen:
            raise ValueError(f"duplicate project in builder lock: {name}")
        hashes: list[str] = []
        for token in tokens[1:]:
            hash_match = hash_re.fullmatch(token)
            if hash_match is None:
                raise ValueError(f"unsupported token in builder lock row for {name}: {token!r}")
            digest = hash_match.group("digest")
            if digest in hashes:
                raise ValueError(f"duplicate hash in builder lock row for {name}")
            hashes.append(digest)
        if not hashes:
            raise ValueError(f"builder lock row has no SHA-256 hash: {name}")
        seen.add(name)
        rows.append(
            {
                "name": name,
                "version": match.group("version"),
                "hashes": hashes,
            }
        )
    if not rows:
        raise ValueError("builder lock is empty")
    return sorted(rows, key=lambda row: str(row["name"]))


def builder_lock_descriptor(path: Path) -> dict[str, Any]:
    """Return the source-bound lock identity and normalized exact rows."""

    rows = parse_builder_lock(path)
    return {
        "path": BUILDER_LOCK_PATH,
        "bytes": path.stat().st_size,
        "sha256": _sha256_file(path),
        "entries": rows,
    }


def _package_input_file_rows(root: Path) -> list[dict[str, Any]]:
    """Return digests for release/package policy input files that exist."""

    rows: list[dict[str, Any]] = []
    for rel in PACKAGE_INPUT_FILES:
        path = root / rel
        if not path.is_file():
            continue
        rows.append(
            {
                "path": rel,
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )
    return rows


def _normalize_requirement(value: object) -> str:
    """Return a simple stable key for comparing direct requirement declarations."""

    text = str(value or "").split("#", 1)[0].strip()
    if not text:
        return ""
    return re.sub(r"\s+", "", text).lower()


def _requirements_file_rows(path: Path) -> list[str]:
    """Return normalized direct requirements from a pip requirements file."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    out: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-", "--")):
            out.append(line.lower())
            continue
        norm = _normalize_requirement(line)
        if norm:
            out.append(norm)
    return out


def _pyproject_list(table: dict[str, Any], *keys: str) -> list[str]:
    """Return a string list from a nested pyproject table."""

    cur: object = table
    for key in keys:
        if not isinstance(cur, dict):
            return []
        cur = cur.get(key)
    if not isinstance(cur, list):
        return []
    return [str(item) for item in cur if isinstance(item, str)]


def _release_policy(pyproject: dict[str, Any]) -> dict[str, Any]:
    """Return the project-local release policy table in normalized form."""

    tool = pyproject.get("tool") if isinstance(pyproject.get("tool"), dict) else {}
    micromax = tool.get("micromax") if isinstance(tool.get("micromax"), dict) else {}
    release = micromax.get("release") if isinstance(micromax.get("release"), dict) else {}
    return {
        "dependency_policy": str(release.get("dependency_policy") or "").strip(),
        "package_version_policy": str(release.get("package_version_policy") or "").strip(),
        "build_backend_requirement": str(release.get("build_backend_requirement") or "").strip(),
        "wheel_build_frontend": str(release.get("wheel_build_frontend") or "").strip(),
        "source_date_epoch": release.get("source_date_epoch"),
        **{
            key: str(release.get(key) or "").strip()
            for key in PACKAGE_RELEASE_BUILDERS
        },
    }


def _lock_files(root: Path) -> list[str]:
    """Return lock files visible to the release/package input policy."""

    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file()
        and path.name in LOCK_FILE_NAMES
        and not {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}.intersection(
            path.relative_to(root).parts
        )
    )


def _precommit_rev_rows(path: Path) -> list[dict[str, Any]]:
    """Return a tiny parser view of pre-commit repo/rev rows.

    Avoid PyYAML as a new release-tool dependency.  The checked-in pre-commit
    file is simple enough that a line-oriented repo/rev pass gives the package
    input verifier one useful invariant: remote hooks should not float on
    ``main``/``master``/``HEAD``/``latest``.
    """

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []
    rows: list[dict[str, Any]] = []
    current_repo = ""
    for raw in lines:
        line = raw.strip()
        if line.startswith("- repo:") or line.startswith("repo:"):
            current_repo = line.split(":", 1)[1].strip().strip('"\'')
            continue
        if line.startswith("rev:"):
            rev = line.split(":", 1)[1].strip().strip('"\'')
            rev_key = rev.lower()
            rows.append(
                {
                    "repo": current_repo,
                    "rev": rev,
                    "pinned": rev_key not in UNPINNED_PRECOMMIT_REVS and "$" not in rev and "{" not in rev,
                }
            )
    return rows


def package_input_report(root: Path = ROOT) -> dict[str, Any]:
    """Inspect package inputs and the exact release-builder wheel lock."""

    root = Path(root)
    pyproject = _read_toml(root / "pyproject.toml")
    project = pyproject.get("project") if isinstance(pyproject.get("project"), dict) else {}
    build_system = (
        pyproject.get("build-system")
        if isinstance(pyproject.get("build-system"), dict)
        else {}
    )
    policy = _release_policy(pyproject)
    runtime_deps = [
        _normalize_requirement(item)
        for item in _pyproject_list(pyproject, "project", "dependencies")
    ]
    runtime_deps = [item for item in runtime_deps if item]
    dev_deps = [
        _normalize_requirement(item)
        for item in _pyproject_list(
            pyproject, "project", "optional-dependencies", "dev"
        )
    ]
    dev_deps = [item for item in dev_deps if item]
    requirements_dev = _requirements_file_rows(root / "requirements-dev.txt")
    precommit_revs = _precommit_rev_rows(root / ".pre-commit-config.yaml")
    locks = _lock_files(root)
    dependency_policy = policy["dependency_policy"]
    version_policy = policy["package_version_policy"]
    backend_requirement = str(policy["build_backend_requirement"])
    wheel_frontend = str(policy["wheel_build_frontend"])
    source_date_epoch = policy["source_date_epoch"]
    builder_versions = {
        key: str(policy.get(key) or "") for key in PACKAGE_RELEASE_BUILDERS
    }
    build_requires = [
        str(item).strip()
        for item in (build_system.get("requires") or [])
        if isinstance(item, str) and str(item).strip()
    ]
    build_backend = str(build_system.get("build-backend") or "").strip()
    issues: list[str] = []
    lock_descriptor: dict[str, Any] | None = None

    if dependency_policy != PACKAGE_INPUT_POLICY_HASH_LOCKED_BUILDER:
        issues.append(
            f"dependency_policy must be {PACKAGE_INPUT_POLICY_HASH_LOCKED_BUILDER!r}; "
            f"got {dependency_policy!r}"
        )
    if version_policy != PACKAGE_VERSION_POLICY_ARCHIVE_REV_INDEPENDENT:
        issues.append(
            f"package_version_policy must be {PACKAGE_VERSION_POLICY_ARCHIVE_REV_INDEPENDENT!r}; "
            f"got {version_policy!r}"
        )
    if backend_requirement != PACKAGE_BUILD_BACKEND_REQUIREMENT:
        issues.append(
            "build_backend_requirement must be the supported compatibility floor "
            f"{PACKAGE_BUILD_BACKEND_REQUIREMENT!r}; got {backend_requirement!r}"
        )
    if build_requires != [backend_requirement]:
        issues.append(
            "[build-system].requires must contain only build_backend_requirement; "
            f"got {build_requires!r}"
        )
    if build_backend != PACKAGE_BUILD_BACKEND:
        issues.append(
            f"build-backend must be {PACKAGE_BUILD_BACKEND!r}; got {build_backend!r}"
        )
    if wheel_frontend != PACKAGE_WHEEL_FRONTEND:
        issues.append(
            f"wheel_build_frontend must be {PACKAGE_WHEEL_FRONTEND!r}; got {wheel_frontend!r}"
        )
    if (
        not isinstance(source_date_epoch, int)
        or isinstance(source_date_epoch, bool)
        or source_date_epoch < 315532800
    ):
        issues.append("source_date_epoch must be an integer at or after 1980-01-01 UTC")
    for key, value in builder_versions.items():
        if not re.fullmatch(r"[0-9]+(?:\.[0-9]+){1,3}(?:[A-Za-z0-9.+-]*)?", value):
            issues.append(f"{key} must declare one exact release-builder version")

    expected_locks = [BUILDER_LOCK_PATH]
    if locks != expected_locks:
        issues.append(
            "release lock set must contain only "
            f"{BUILDER_LOCK_PATH!r}; got {locks!r}"
        )
    lock_path = root / BUILDER_LOCK_PATH
    try:
        lock_descriptor = builder_lock_descriptor(lock_path)
    except (OSError, UnicodeError, ValueError) as exc:
        issues.append(f"builder lock is invalid: {exc}")
    if lock_descriptor is not None:
        rows = lock_descriptor.get("entries")
        by_name = {str(row["name"]): row for row in rows if isinstance(row, dict)} if isinstance(rows, list) else {}
        actual_projects = set(by_name)
        if actual_projects != BUILDER_LOCK_PROJECTS:
            missing = sorted(BUILDER_LOCK_PROJECTS - actual_projects)
            extra = sorted(actual_projects - BUILDER_LOCK_PROJECTS)
            issues.append(
                "builder lock project set drifted: "
                f"missing={missing!r} extra={extra!r}"
            )
        for project_name, declaration_key in BUILDER_DECLARATION_KEYS.items():
            row = by_name.get(project_name)
            locked_version = str(row.get("version") or "") if isinstance(row, dict) else ""
            if locked_version != builder_versions[declaration_key]:
                issues.append(
                    f"{declaration_key}={builder_versions[declaration_key]!r} "
                    f"does not match locked {project_name}=={locked_version}"
                )

    if runtime_deps:
        issues.append("runtime project dependencies require their own exact wheel lock")
    if sorted(dev_deps) != sorted(requirements_dev):
        issues.append("requirements-dev.txt does not mirror [project.optional-dependencies].dev")
    unpinned = [row for row in precommit_revs if row.get("pinned") is not True]
    if unpinned:
        sample = ", ".join(
            str(row.get("repo") or row.get("rev") or "?") for row in unpinned[:3]
        )
        issues.append("pre-commit hook revisions are not pinned: " + sample)

    return {
        "schema": PACKAGE_INPUT_SCHEMA,
        "ok": not issues,
        "dependency_policy": dependency_policy,
        "package_version_policy": version_policy,
        "build_backend_requirement": backend_requirement,
        "build_system_requires": build_requires,
        "build_backend": build_backend,
        "wheel_build_frontend": wheel_frontend,
        "source_date_epoch": source_date_epoch,
        **builder_versions,
        "package_name": str(project.get("name") or ""),
        "package_version": str(project.get("version") or ""),
        "lock_status": "verified-hash-lock" if lock_descriptor is not None else "invalid",
        "lock_files": locks,
        "builder_lock": lock_descriptor,
        "runtime_dependencies": runtime_deps,
        "dev_dependencies": sorted(dev_deps),
        "requirements_dev": sorted(requirements_dev),
        "precommit_revisions": precommit_revs,
        "input_files": _package_input_file_rows(root),
        "issues": issues,
    }


def print_package_inputs(report: dict[str, Any]) -> None:
    """Print a compact package-input report for release handoffs."""

    print("mxrelease package-inputs")
    print(f"  ok: {str(bool(report.get('ok'))).lower()}")
    print(f"  dependency-policy: {report.get('dependency_policy')}")
    print(f"  version-policy: {report.get('package_version_policy')}")
    print(
        "  build: "
        f"{report.get('build_backend')} via {report.get('wheel_build_frontend')} "
        f"({report.get('build_backend_requirement')})"
    )
    print(f"  source-date-epoch: {report.get('source_date_epoch')}")
    print(
        "  builder: "
        f"python={report.get('builder_python')} pip={report.get('builder_pip')} "
        f"setuptools={report.get('builder_setuptools')} pytest={report.get('builder_pytest')}"
    )
    print(f"  package: {report.get('package_name')} {report.get('package_version')}")
    print(f"  locks: {report.get('lock_status')} count={len(report.get('lock_files') or [])}")
    lock = report.get("builder_lock")
    if isinstance(lock, dict):
        print(
            f"  builder-lock: {lock.get('path')} sha256={lock.get('sha256')} "
            f"entries={len(lock.get('entries') or [])}"
        )
    print(
        f"  deps: runtime={len(report.get('runtime_dependencies') or [])} "
        f"dev={len(report.get('dev_dependencies') or [])}"
    )
    issues = report.get("issues")
    if isinstance(issues, list) and issues:
        print("  issues:")
        for issue in issues:
            print(f"    - {issue}")


def discover_test_files() -> list[str]:
    """Return all pytest test files covered by the release lane."""

    return [path.relative_to(ROOT).as_posix() for path in sorted((ROOT / "tests").glob("test*.py"))]


def discover_test_nodes(test_file: str, *, timeout_seconds: float = 30.0) -> list[str]:
    """Return pytest node ids for one slow file, or an empty list on failure."""

    target = str(test_file)
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--collect-only", target],
            cwd=str(ROOT),
            env=isolated_env(),
            capture_output=True,
            text=True,
            timeout=max(1.0, float(timeout_seconds)),
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if proc.returncode not in {0, 5}:
        return []
    nodes: list[str] = []
    for raw in (proc.stdout or "").splitlines():
        line = ANSI_RE.sub("", raw).strip()
        if not line.startswith(target + "::"):
            continue
        if " " in line:
            continue
        nodes.append(line)
    return nodes


def chunked(items: list[str], size: int) -> list[list[str]]:
    """Split items into stable non-empty chunks."""

    width = max(1, int(size))
    return [items[index : index + width] for index in range(0, len(items), width)]


def parse_pytest_counts(output: str) -> dict[str, int]:
    """Parse common pytest terminal-summary counters from child output."""

    counts = {"passed": 0, "failed": 0, "skipped": 0, "xfailed": 0, "xpassed": 0, "errors": 0}
    for match in SUMMARY_RE.finditer(output):
        name = match.group("name")
        key = "errors" if name in {"error", "errors"} else name
        counts[key] = counts.get(key, 0) + int(match.group("count"))
    return counts


def target_file(target: str) -> str:
    """Return the owning test file for a pytest file or node selector."""

    return str(target).split("::", 1)[0]


def files_for_targets(targets: list[str]) -> list[str]:
    """Return stable unique file coverage for pytest targets."""

    out: list[str] = []
    seen: set[str] = set()
    for target in targets:
        path = target_file(str(target))
        if path in seen:
            continue
        seen.add(path)
        out.append(path)
    return out


def _batch_for_not_run(targets: list[str], *, index: int, total: int) -> dict[str, Any]:
    target_list = [str(item) for item in targets]
    return {
        "index": index,
        "total": total,
        "files": files_for_targets(target_list),
        "targets": target_list,
        "status": "not_run",
        "returncode": None,
        "timed_out": False,
        "elapsed_seconds": 0.0,
        "counts": {"passed": 0, "failed": 0, "skipped": 0, "xfailed": 0, "xpassed": 0, "errors": 0},
        "output_tail": "",
        "started_at_utc": None,
        "finished_at_utc": None,
    }


def reindex_batches(batches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return batches with stable 1-based indexes and shared totals."""

    total = len(batches)
    out: list[dict[str, Any]] = []
    for index, batch in enumerate(batches, start=1):
        row = dict(batch)
        row["index"] = index
        row["total"] = total
        out.append(row)
    return out


def split_batch_for_retry(batch: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Split one timed-out batch into smaller not-run retry rows."""

    if batch.get("status") not in {"timed_out"}:
        return None
    targets_obj = batch.get("targets")
    if isinstance(targets_obj, list) and targets_obj:
        targets = [str(item) for item in targets_obj]
    else:
        files_obj = batch.get("files")
        if not isinstance(files_obj, list):
            return None
        targets = [str(item) for item in files_obj]
    if len(targets) > 1:
        pivot = max(1, len(targets) // 2)
        return [_batch_for_not_run(targets[:pivot], index=0, total=0), _batch_for_not_run(targets[pivot:], index=0, total=0)]
    if len(targets) != 1 or "::" in targets[0]:
        return None
    nodes = discover_test_nodes(targets[0])
    if len(nodes) <= 1:
        return None
    pivot = max(1, len(nodes) // 2)
    return [_batch_for_not_run(nodes[:pivot], index=0, total=0), _batch_for_not_run(nodes[pivot:], index=0, total=0)]


def split_retryable_batches(batches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Split any retryable slow batches and reindex the manifest rows."""

    out: list[dict[str, Any]] = []
    changed = False
    for batch in batches:
        split = split_batch_for_retry(batch)
        if split is None:
            out.append(batch)
        else:
            out.extend(split)
            changed = True
    return reindex_batches(out) if changed else reindex_batches(batches)


def run_batch(batch: dict[str, Any], *, timeout_seconds: float, quiet: bool = False) -> dict[str, Any]:
    """Run one batch of test files or node ids in a fresh pytest child."""

    targets_obj = batch.get("targets")
    if isinstance(targets_obj, list) and targets_obj:
        targets = [str(item) for item in targets_obj]
    else:
        targets = [str(item) for item in batch.get("files", [])]
    files = files_for_targets(targets)
    index = int(batch.get("index", 0) or 0)
    total = int(batch.get("total", 0) or 0)
    timeout_value = max(0.1, float(timeout_seconds))
    if not quiet:
        print(
            f"mxrelease: batch {index}/{total} targets={len(targets)} files={len(files)} "
            f"timeout={format_duration(timeout_value)}",
            flush=True,
        )
    command = run_captured(
        [sys.executable, "-m", "pytest", "-q", *targets],
        cwd=ROOT,
        env=isolated_env(),
        timeout_seconds=timeout_value,
        label=f"batch {index}/{total}",
        heartbeat_seconds=min(10.0, max(0.0, timeout_value / 2.0)),
        heartbeat_prefix="mxrelease",
    )
    counts = parse_pytest_counts(command.output)
    status = "timed_out" if command.timed_out else ("passed" if command.returncode == 0 else "failed")
    row = dict(batch)
    row.update(
        {
            "files": files,
            "targets": targets,
            "status": status,
            "returncode": command.returncode,
            "timed_out": bool(command.timed_out),
            "elapsed_seconds": round(float(command.elapsed_seconds), 3),
            "timeout_seconds": round(float(command.timeout_seconds), 3),
            "counts": counts,
            "output_tail": tail_text(command.output),
            "started_at_utc": command.started_at_utc,
            "finished_at_utc": command.finished_at_utc,
            "command": command.as_json(),
        }
    )
    if not quiet:
        passed = counts.get("passed", 0)
        suffix = f" tests_passed={passed}" if passed else ""
        print(f"  {status} rc={command.returncode} elapsed={format_duration(command.elapsed_seconds)}{suffix}", flush=True)
    return row

def status_counts_for_batches(batches: list[dict[str, Any]]) -> dict[str, int]:
    """Return status counts by batch."""

    counts = {name: 0 for name in STATUS_ORDER}
    for row in batches:
        status = str(row.get("status") or "not_run")
        counts[status if status in counts else "failed"] += 1
    return counts


def status_counts_for_files(batches: list[dict[str, Any]]) -> dict[str, int]:
    """Return one aggregate status per covered file, even after node splits."""

    severity = {"passed": 0, "not_run": 1, "timed_out": 2, "failed": 3}
    by_file: dict[str, str] = {}
    for row in batches:
        status = str(row.get("status") or "not_run")
        key = status if status in severity else "failed"
        files = row.get("files")
        if not isinstance(files, list):
            files = files_for_targets([str(item) for item in row.get("targets", [])]) if isinstance(row.get("targets"), list) else []
        for file_name in files:
            name = str(file_name)
            current = by_file.get(name)
            if current is None or severity[key] > severity[current]:
                by_file[name] = key
    counts = {name: 0 for name in STATUS_ORDER}
    for status in by_file.values():
        counts[status] += 1
    return counts


def aggregate_pytest_counts(batches: list[dict[str, Any]]) -> dict[str, int]:
    """Return aggregate parsed pytest counts across passed/failed batches."""

    totals = {"passed": 0, "failed": 0, "skipped": 0, "xfailed": 0, "xpassed": 0, "errors": 0}
    for row in batches:
        counts = row.get("counts")
        if not isinstance(counts, dict):
            continue
        for key in totals:
            try:
                totals[key] += int(counts.get(key, 0) or 0)
            except (TypeError, ValueError):
                continue
    return totals


def _row_elapsed(row: dict[str, Any]) -> float:
    try:
        return max(0.0, float(row.get("elapsed_seconds", 0.0) or 0.0))
    except (TypeError, ValueError):
        return 0.0


def batch_timing_summary(batches: list[dict[str, Any]], *, limit: int = 5) -> dict[str, Any]:
    """Return timing evidence and slowest-batch hints for handoff manifests."""

    measured = [row for row in batches if _row_elapsed(row) > 0]
    total = sum(_row_elapsed(row) for row in measured)
    slowest: list[dict[str, Any]] = []
    for row in sorted(measured, key=_row_elapsed, reverse=True)[: max(0, int(limit))]:
        targets = row.get("targets")
        files = row.get("files")
        target_count = len(targets) if isinstance(targets, list) else 0
        file_count = len(files) if isinstance(files, list) else 0
        slowest.append(
            {
                "index": int(row.get("index", 0) or 0),
                "status": str(row.get("status") or "not_run"),
                "elapsed_seconds": round(_row_elapsed(row), 3),
                "timeout_seconds": round(float(row.get("timeout_seconds", 0.0) or 0.0), 3),
                "file_count": file_count,
                "target_count": target_count,
                "sample": str((targets or files or [""])[0]) if isinstance(targets or files, list) and (targets or files) else "",
            }
        )
    return {
        "measured_batch_count": len(measured),
        "total_batch_elapsed_seconds": round(total, 3),
        "average_batch_elapsed_seconds": round(total / len(measured), 3) if measured else 0.0,
        "slowest_batches": slowest,
    }


def first_problem_batch(batches: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first failed/timed-out batch row for next-action guidance."""

    for row in batches:
        if row.get("status") in {"failed", "timed_out"}:
            return row
    return None


def next_not_run_batch(batches: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the first not-run batch row for next-action guidance."""

    for row in batches:
        if row.get("status") == "not_run":
            return row
    return None


def next_action_for_payload(payload: dict[str, Any], *, manifest_path: str | Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    """Return a compact, copy/pasteable next action for weaker handoff agents."""

    path = str(manifest_path)
    batches_obj = payload.get("batches")
    batches = [row for row in batches_obj if isinstance(row, dict)] if isinstance(batches_obj, list) else []
    batch_counts = status_counts_for_batches(batches)
    remaining = int(batch_counts.get("not_run", 0) or 0)
    base = [sys.executable, "tools/mxrelease.py", "--manifest", path]
    if payload.get("ok") is True:
        return {
            "state": "verify",
            "why": "full-suite manifest is complete/passed; verify it against the current source tree",
            "command": " ".join([*base, "--verify"]),
            "make_command": "make release-verify",
            "remaining_batches": 0,
        }
    problem = first_problem_batch(batches)
    if problem is not None:
        targets = problem.get("targets") if isinstance(problem.get("targets"), list) else problem.get("files")
        sample = str(targets[0]) if isinstance(targets, list) and targets else ""
        return {
            "state": "inspect-failure",
            "why": f"batch {problem.get('index')} is {problem.get('status')}; inspect its output_tail before rerunning",
            "command": " ".join([*base, "--summary"]),
            "make_command": "make release-summary",
            "remaining_batches": remaining,
            "problem_batch": {
                "index": int(problem.get("index", 0) or 0),
                "status": str(problem.get("status") or "failed"),
                "sample": sample,
            },
        }
    next_row = next_not_run_batch(batches)
    sample = ""
    if next_row is not None:
        targets = next_row.get("targets") if isinstance(next_row.get("targets"), list) else next_row.get("files")
        sample = str(targets[0]) if isinstance(targets, list) and targets else ""
    batch_size = int(payload.get("batch_size", DEFAULT_BATCH_SIZE) or DEFAULT_BATCH_SIZE)
    return {
        "state": "continue",
        "why": f"{remaining} release batch(es) remain; continue the resumable short-window lane",
        "command": " ".join(
            [
                *base,
                "--max-runtime-seconds",
                str(DEFAULT_MAX_RUNTIME_SECONDS),
                "--batch-timeout",
                str(DEFAULT_BATCH_TIMEOUT_SECONDS),
                "--batch-size",
                str(batch_size),
                "--allow-partial",
            ]
        ),
        "make_command": "make release-suite",
        "remaining_batches": remaining,
        "next_batch": {
            "index": int(next_row.get("index", 0) or 0) if next_row is not None else 0,
            "sample": sample,
        },
    }


def flatten_batch_files(batches: list[dict[str, Any]]) -> list[str]:
    """Return the unique file inventory represented by manifest batches."""

    out: list[str] = []
    seen: set[str] = set()
    for batch in batches:
        files = batch.get("files")
        if isinstance(files, list):
            candidates = [str(item) for item in files]
        elif isinstance(batch.get("targets"), list):
            candidates = files_for_targets([str(item) for item in batch.get("targets", [])])
        else:
            candidates = []
        for item in candidates:
            if item in seen:
                continue
            seen.add(item)
            out.append(item)
    return out


def _batch_key(files: list[str]) -> str:
    return "\n".join(files)


def initial_batches(
    files: list[str],
    *,
    previous: dict[str, Any] | None,
    source_digest: str,
    reset: bool,
    batch_size: int,
) -> list[dict[str, Any]]:
    """Return current batches, preserving same-source progress when safe."""

    if not reset and isinstance(previous, dict) and previous.get("source_digest") == source_digest:
        raw = previous.get("batches")
        if isinstance(raw, list) and all(isinstance(item, dict) for item in raw):
            previous_batches = [dict(item) for item in raw]
            if flatten_batch_files(previous_batches) == files:
                return split_retryable_batches(previous_batches)

    groups = chunked(files, batch_size)
    total = len(groups)
    previous_rows: dict[str, dict[str, Any]] = {}
    if not reset and isinstance(previous, dict) and previous.get("source_digest") == source_digest:
        raw = previous.get("batches")
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                old_files = item.get("files")
                if isinstance(old_files, list) and item.get("status") == "passed":
                    previous_rows[_batch_key([str(value) for value in old_files])] = item
    batches: list[dict[str, Any]] = []
    for index, group in enumerate(groups, start=1):
        old = previous_rows.get(_batch_key(group))
        if isinstance(old, dict):
            row = dict(old)
            row["index"] = index
            row["total"] = total
            row["files"] = group
            batches.append(row)
        else:
            batches.append(_batch_for_not_run(group, index=index, total=total))
    return batches


def next_not_run_index(batches: list[dict[str, Any]]) -> int | None:
    """Return the next not-run batch index, or None when none remain."""

    for index, row in enumerate(batches):
        if row.get("status") == "not_run":
            return index
    return None


def has_failure(batches: list[dict[str, Any]]) -> bool:
    """Return True if any batch failed or timed out."""

    return any(row.get("status") in {"failed", "timed_out"} for row in batches)


def build_payload(
    *,
    batches: list[dict[str, Any]],
    source_manifest: dict[str, Any],
    files: list[str],
    batch_size: int,
    started_at_utc: str | None = None,
    finished_at_utc: str | None = None,
    note: str = "",
    manifest_path: str | Path = DEFAULT_MANIFEST,
) -> dict[str, Any]:
    """Return the aggregate full-suite release manifest."""

    batch_counts = status_counts_for_batches(batches)
    file_counts = status_counts_for_files(batches)
    pytest_counts = aggregate_pytest_counts(batches)
    target_count = 0
    for batch in batches:
        targets_obj = batch.get("targets")
        if isinstance(targets_obj, list):
            target_count += len(targets_obj)
        else:
            files_obj = batch.get("files")
            target_count += len(files_obj) if isinstance(files_obj, list) else 0
    complete = bool(batches) and batch_counts["not_run"] == 0
    ok = complete and batch_counts["failed"] == 0 and batch_counts["timed_out"] == 0 and batch_counts["passed"] == len(batches)
    status = "passed" if ok else ("failed" if batch_counts["failed"] or batch_counts["timed_out"] else "partial")
    payload = {
        "schema": SCHEMA,
        "mode": "selected-file-batch-pytest-release-suite",
        "status": status,
        "ok": bool(ok),
        "complete": bool(complete),
        "note": note,
        "generated_at_utc": utc_now(),
        "started_at_utc": started_at_utc,
        "finished_at_utc": finished_at_utc if complete else None,
        "source_digest": source_manifest.get("digest"),
        "source_file_count": source_manifest.get("file_count"),
        "source_total_bytes": source_manifest.get("total_bytes"),
        "source_manifest": source_manifest,
        "environment_manifest": environment_manifest_payload(),
        "test_files": files,
        "test_file_count": len(files),
        "test_batch_count": len(batches),
        "test_target_count": int(target_count),
        "batch_size": int(batch_size),
        "test_status_counts": file_counts,
        "batch_status_counts": batch_counts,
        "pytest_counts": pytest_counts,
        "timing": batch_timing_summary(batches),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "batches": batches,
    }
    payload["next_action"] = next_action_for_payload(payload, manifest_path=manifest_path)
    return payload


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    """Atomically write a JSON manifest."""

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_manifest(path: Path) -> dict[str, Any] | None:
    """Load a manifest if it exists and is a JSON object."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if not isinstance(payload, dict):
        raise SystemExit(f"mxrelease: manifest is not an object: {path}")
    return payload


def print_progress(payload: dict[str, Any], *, started: float, max_runtime: float, quiet: bool) -> None:
    """Print one compact progress line before starting the next release batch."""

    if quiet:
        return
    batch_counts = payload.get("batch_status_counts") if isinstance(payload.get("batch_status_counts"), dict) else {}
    elapsed = time.monotonic() - started
    budget = format_duration(max_runtime) if max_runtime else "unbounded"
    print(
        "mxrelease: progress "
        + " ".join(f"{name}={batch_counts.get(name, 0)}" for name in STATUS_ORDER)
        + f" elapsed={format_duration(elapsed)} budget={budget}",
        flush=True,
    )


def run_suite(args: argparse.Namespace) -> int:
    """Run the resumable selected-file-batch suite."""

    manifest_path = Path(args.manifest)
    source = source_manifest_payload()
    files = discover_test_files()
    previous = None if args.reset else load_manifest(manifest_path)
    batches = initial_batches(
        files,
        previous=previous,
        source_digest=str(source.get("digest")),
        reset=bool(args.reset),
        batch_size=int(args.batch_size),
    )
    started_at = None
    if isinstance(previous, dict) and previous.get("source_digest") == source.get("digest"):
        value = previous.get("started_at_utc")
        started_at = value if isinstance(value, str) else None
    started_at = started_at or utc_now()
    if previous and previous.get("source_digest") != source.get("digest") and not args.reset:
        print("mxrelease: source digest changed; starting a fresh release-suite manifest")
    started = time.monotonic()
    max_runtime = max(0.0, float(args.max_runtime_seconds))
    max_new_batches = max(0, int(args.max_new_batches))
    ran = 0

    payload = build_payload(
        batches=batches,
        source_manifest=source,
        files=files,
        batch_size=int(args.batch_size),
        started_at_utc=started_at,
        note=str(args.note or ""),
        manifest_path=manifest_path,
    )
    write_manifest(manifest_path, payload)

    while not has_failure(batches):
        row_index = next_not_run_index(batches)
        if row_index is None:
            break
        if max_new_batches and ran >= max_new_batches:
            break
        elapsed = time.monotonic() - started
        if max_runtime and elapsed >= max_runtime:
            break
        payload = build_payload(
            batches=batches,
            source_manifest=source,
            files=files,
            batch_size=int(args.batch_size),
            started_at_utc=started_at,
            note=str(args.note or ""),
            manifest_path=manifest_path,
        )
        print_progress(payload, started=started, max_runtime=max_runtime, quiet=bool(args.quiet))
        row = run_batch(
            batches[row_index],
            timeout_seconds=float(args.batch_timeout),
            quiet=bool(args.quiet),
        )
        split = split_batch_for_retry(row)
        if split is None:
            batches[row_index] = row
        else:
            batches = reindex_batches([*batches[:row_index], *split, *batches[row_index + 1 :]])
            if not args.quiet:
                print(
                    f"mxrelease: split timed-out batch into {len(split)} smaller retry batches",
                    flush=True,
                )
        ran += 1
        payload = build_payload(
            batches=batches,
            source_manifest=source,
            files=files,
            batch_size=int(args.batch_size),
            started_at_utc=started_at,
            note=str(args.note or ""),
            manifest_path=manifest_path,
        )
        write_manifest(manifest_path, payload)

    finished_at = utc_now() if next_not_run_index(batches) is None else None
    payload = build_payload(
        batches=batches,
        source_manifest=source,
        files=files,
        batch_size=int(args.batch_size),
        started_at_utc=started_at,
        finished_at_utc=finished_at,
        note=str(args.note or ""),
        manifest_path=manifest_path,
    )
    write_manifest(manifest_path, payload)
    print_summary(payload, manifest_path=manifest_path, ran=ran)
    if payload["ok"]:
        return 0
    if payload["status"] == "partial" and bool(args.allow_partial):
        return 0
    return 1 if payload["status"] == "failed" else 2


def manifest_issues(payload: dict[str, Any], *, current_source: dict[str, Any] | None = None) -> list[str]:
    """Return release-manifest consistency/current-source issues."""

    issues: list[str] = []
    if payload.get("schema") != SCHEMA:
        issues.append(f"schema {payload.get('schema')!r} is not {SCHEMA!r}")
    batches_obj = payload.get("batches")
    if not isinstance(batches_obj, list):
        issues.append("batches must be a list")
        batches: list[dict[str, Any]] = []
    else:
        batches = [row for row in batches_obj if isinstance(row, dict)]
        if len(batches) != len(batches_obj):
            issues.append("batches contains non-object entries")
    expected_files = discover_test_files()
    if flatten_batch_files(batches) != expected_files:
        issues.append("batches do not match current tests/test*.py inventory")
    if payload.get("test_files") != expected_files:
        issues.append("test_files do not match current tests/test*.py inventory")
    batch_counts = status_counts_for_batches(batches)
    file_counts = status_counts_for_files(batches)
    if payload.get("batch_status_counts") != batch_counts:
        issues.append("batch_status_counts does not match batches")
    if payload.get("test_status_counts") != file_counts:
        issues.append("test_status_counts does not match batches")
    pytest_counts = aggregate_pytest_counts(batches)
    if payload.get("pytest_counts") != pytest_counts:
        issues.append("pytest_counts does not match batches")
    complete = bool(batches) and batch_counts["not_run"] == 0
    ok = complete and batch_counts["failed"] == 0 and batch_counts["timed_out"] == 0 and batch_counts["passed"] == len(batches)
    expected_status = "passed" if ok else ("failed" if batch_counts["failed"] or batch_counts["timed_out"] else "partial")
    if payload.get("complete") != complete:
        issues.append("complete does not match batches")
    if payload.get("ok") != ok:
        issues.append("ok does not match batches")
    if payload.get("status") != expected_status:
        issues.append("status does not match batches")
    issues.extend(source_manifest_issues(payload))
    current = current_source if current_source is not None else source_manifest_payload()
    if payload.get("source_digest") != current.get("digest"):
        diff = source_manifest_differences(payload.get("source_manifest"), current)
        samples = list((diff.get("added") or [])[:3]) + list((diff.get("removed") or [])[:3]) + list((diff.get("changed") or [])[:3])
        suffix = f": {', '.join(samples)}" if samples else ""
        issues.append("source_digest does not match current source" + suffix)
    return issues


def verify_manifest(path: Path) -> int:
    """Verify a complete release-suite manifest against the current tree."""

    payload = load_manifest(path)
    if payload is None:
        raise SystemExit(f"mxrelease: manifest not found: {path}")
    issues = manifest_issues(payload)
    print_summary(payload, manifest_path=path, ran=0)
    if issues:
        print("mxrelease verify issues:")
        for issue in issues:
            print(f"- {issue}")
        return 2
    if payload.get("ok") is True:
        print("mxrelease verify: full-suite release evidence is complete and current")
        return 0
    print("mxrelease verify: manifest is current but not complete/passed")
    return 1


def print_summary(payload: dict[str, Any], *, manifest_path: Path, ran: int = 0) -> None:
    """Print a compact handoff summary."""

    file_counts = payload.get("test_status_counts") if isinstance(payload.get("test_status_counts"), dict) else {}
    batch_counts = payload.get("batch_status_counts") if isinstance(payload.get("batch_status_counts"), dict) else {}
    pytest_counts = payload.get("pytest_counts") if isinstance(payload.get("pytest_counts"), dict) else {}
    timing = payload.get("timing") if isinstance(payload.get("timing"), dict) else {}
    next_action = payload.get("next_action") if isinstance(payload.get("next_action"), dict) else {}
    print("mxrelease summary")
    print(f"  manifest: {manifest_path}")
    print(f"  status: {payload.get('status')} complete={str(bool(payload.get('complete'))).lower()} ok={str(bool(payload.get('ok'))).lower()}")
    print(
        "  batches: "
        + " ".join(f"{name}={batch_counts.get(name, 0)}" for name in STATUS_ORDER)
        + f" total={payload.get('test_batch_count')} ran_now={ran}"
    )
    print(
        "  files: "
        + " ".join(f"{name}={file_counts.get(name, 0)}" for name in STATUS_ORDER)
        + f" total={payload.get('test_file_count')} targets={payload.get('test_target_count')}"
    )
    print(
        "  pytest: "
        + " ".join(f"{name}={pytest_counts.get(name, 0)}" for name in ["passed", "failed", "skipped", "errors"])
    )
    if timing:
        total_elapsed = float(timing.get("total_batch_elapsed_seconds", 0.0) or 0.0)
        average_elapsed = float(timing.get("average_batch_elapsed_seconds", 0.0) or 0.0)
        measured = int(timing.get("measured_batch_count", 0) or 0)
        print(
            f"  timing: measured_batches={measured} total={format_duration(total_elapsed)} "
            f"avg={format_duration(average_elapsed)}"
        )
        slowest = timing.get("slowest_batches")
        if isinstance(slowest, list) and slowest:
            top = slowest[0]
            if isinstance(top, dict):
                print(
                    f"  slowest: batch={top.get('index')} status={top.get('status')} "
                    f"elapsed={format_duration(float(top.get('elapsed_seconds', 0.0) or 0.0))} sample={top.get('sample')}"
                )
    digest = payload.get("source_digest")
    if isinstance(digest, str):
        print(f"  source: {digest[:12]} files={payload.get('source_file_count')}")
    if next_action:
        why = str(next_action.get("why") or "")
        command = str(next_action.get("command") or "")
        make_command = str(next_action.get("make_command") or "")
        print(f"  next: {next_action.get('state')} — {why}")
        if make_command:
            print(f"        {make_command}")
        if command:
            print(f"        {command}")


def print_next_action(payload: dict[str, Any], *, manifest_path: Path) -> None:
    """Print only the next-action block from a release manifest."""

    action = payload.get("next_action")
    if not isinstance(action, dict):
        action = next_action_for_payload(payload, manifest_path=manifest_path)
    print("mxrelease next")
    print(f"  state: {action.get('state')}")
    print(f"  why: {action.get('why')}")
    if action.get("make_command"):
        print(f"  make: {action.get('make_command')}")
    print(f"  command: {action.get('command')}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="run/verify resumable Micromax full-suite release evidence")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help="release-suite manifest path")
    parser.add_argument("--max-runtime-seconds", type=float, default=DEFAULT_MAX_RUNTIME_SECONDS, help="stop starting new batches after this many seconds")
    parser.add_argument("--batch-timeout", "--file-timeout", dest="batch_timeout", type=float, default=DEFAULT_BATCH_TIMEOUT_SECONDS, help="per-batch pytest timeout")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="number of test files per pytest child")
    parser.add_argument("--max-new-batches", "--max-new-files", dest="max_new_batches", type=int, default=0, help="run at most this many new batches; 0 means budget by time only")
    parser.add_argument("--allow-partial", action="store_true", help="exit 0 for a clean partial checkpoint")
    parser.add_argument("--reset", action="store_true", help="ignore any existing manifest and start fresh")
    parser.add_argument("--quiet", action="store_true", help="print only the compact summary")
    parser.add_argument("--note", default="", help="optional note stored in the manifest")
    parser.add_argument("--verify", action="store_true", help="verify an existing manifest against the current source tree")
    parser.add_argument("--summary", action="store_true", help="print an existing manifest summary without verifying current source")
    parser.add_argument("--next", action="store_true", help="print the manifest's next recommended release action")
    parser.add_argument("--package-inputs", action="store_true", help="inspect package/dependency input policy")
    parser.add_argument("--package-inputs-json", action="store_true", help="emit JSON for --package-inputs")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.manifest)
    if args.package_inputs:
        report = package_input_report(ROOT)
        if args.package_inputs_json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print_package_inputs(report)
        return 0 if report.get("ok") is True else 2
    if args.summary:
        payload = load_manifest(path)
        if payload is None:
            raise SystemExit(f"mxrelease: manifest not found: {path}")
        print_summary(payload, manifest_path=path, ran=0)
        return 0
    if args.next:
        payload = load_manifest(path)
        if payload is None:
            raise SystemExit(f"mxrelease: manifest not found: {path}")
        print_next_action(payload, manifest_path=path)
        return 0
    if args.verify:
        return verify_manifest(path)
    return run_suite(args)


if __name__ == "__main__":
    raise SystemExit(main())
