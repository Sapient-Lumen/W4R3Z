from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import stat
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

from . import __version__

ARTIFACT_AUDIT_SCHEMA = "lacuna.artifact-audit.v1"
ARTIFACT_AUDIT_EVENT = "lacuna.artifact.audited"
MANIFEST_FILE = "MANIFEST.sha256"
MANIFEST_LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
VERSION_ASSIGNMENT = re.compile(r'^__version__\s*=\s*["\']([^"\']+)["\']\s*$', re.MULTILINE)
IGNORED_RUNTIME_PARTS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
IGNORED_RUNTIME_SUFFIXES = {".pyc", ".pyo"}
NONCLAIMS = [
    "This is a local extracted-artifact audit, not a digital signature, trusted timestamp, remote transparency proof, or provider attestation.",
    "Manifest verification proves equality to the retained hashes under the current local code; it does not prove authorship, safety, narrative quality, or absence of a jointly substituted verifier and artifact.",
    "Python syntax, JSON/TOML parsing, and relative-link checks are structural smoke checks rather than the full unit/e2e acceptance suite.",
    "Unlisted runtime or campaign files are reported separately; use strict_members only for a pristine release tree.",
]


def _check(name: str, status: str, summary: str, **details: Any) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "summary": summary,
        "details": details,
    }


def _normalized_manifest_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in value
    ):
        raise ValueError("manifest member must be one normalized relative POSIX path")
    return path.as_posix()


def _manifest_entries(path: Path) -> tuple[list[tuple[str, str]], list[str]]:
    entries: list[tuple[str, str]] = []
    errors: list[str] = []
    seen: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [], [f"cannot read {MANIFEST_FILE}: {exc}"]
    for number, line in enumerate(lines, start=1):
        match = MANIFEST_LINE.fullmatch(line)
        if match is None:
            errors.append(f"line {number} is not '<sha256><two spaces><path>'")
            continue
        digest, raw_path = match.groups()
        try:
            member = _normalized_manifest_path(raw_path)
        except ValueError as exc:
            errors.append(f"line {number}: {exc}")
            continue
        if member == MANIFEST_FILE:
            errors.append(f"line {number}: the manifest cannot list itself")
            continue
        if member in seen:
            errors.append(f"line {number}: duplicate member {member}")
            continue
        seen.add(member)
        entries.append((member, digest))
    if not entries:
        errors.append("manifest contains no valid members")
    return entries, errors


def _safe_regular_member(root: Path, relative: str) -> tuple[Path | None, str | None]:
    current = root
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        current = current / part
        try:
            metadata = os.lstat(current)
        except OSError as exc:
            return None, f"cannot inspect {relative}: {exc}"
        last = index == len(parts) - 1
        if stat.S_ISLNK(metadata.st_mode):
            return None, f"linked member or path component refused: {relative}"
        if last:
            if not stat.S_ISREG(metadata.st_mode):
                return None, f"manifest member is not a regular file: {relative}"
        elif not stat.S_ISDIR(metadata.st_mode):
            return None, f"manifest path component is not a directory: {relative}"
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        return None, f"manifest member escapes or cannot resolve: {relative}: {exc}"
    return resolved, None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _enumerate_tree(root: Path) -> tuple[set[str], list[str]]:
    files: set[str] = set()
    errors: list[str] = []

    def onerror(error: OSError) -> None:
        errors.append(f"cannot enumerate tree: {error}")

    for current, dirnames, filenames in os.walk(root, topdown=True, onerror=onerror, followlinks=False):
        current_path = Path(current)
        safe_dirs: list[str] = []
        for name in sorted(dirnames):
            path = current_path / name
            try:
                metadata = os.lstat(path)
            except OSError as exc:
                errors.append(f"cannot inspect {path.relative_to(root)}: {exc}")
                continue
            if stat.S_ISLNK(metadata.st_mode):
                errors.append(f"linked directory refused: {path.relative_to(root).as_posix()}")
                continue
            if not stat.S_ISDIR(metadata.st_mode):
                errors.append(f"non-directory tree node refused: {path.relative_to(root).as_posix()}")
                continue
            safe_dirs.append(name)
        dirnames[:] = safe_dirs
        for name in sorted(filenames):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            try:
                metadata = os.lstat(path)
            except OSError as exc:
                errors.append(f"cannot inspect {relative}: {exc}")
                continue
            if stat.S_ISLNK(metadata.st_mode):
                errors.append(f"linked file refused: {relative}")
            elif not stat.S_ISREG(metadata.st_mode):
                errors.append(f"non-regular file refused: {relative}")
            else:
                files.add(relative)
    return files, errors


def _is_runtime_extra(relative: str) -> bool:
    path = PurePosixPath(relative)
    return any(part in IGNORED_RUNTIME_PARTS for part in path.parts) or path.suffix in IGNORED_RUNTIME_SUFFIXES


def _python_syntax(root: Path, members: list[str]) -> tuple[int, list[str]]:
    candidates = [member for member in members if member.endswith(".py")]
    errors: list[str] = []
    for member in candidates:
        path = root / member
        try:
            source = path.read_text(encoding="utf-8")
            ast.parse(source, filename=member)
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append(f"{member}: {exc}")
    return len(candidates), errors


def _parse_documents(root: Path, members: list[str]) -> tuple[int, int, list[str]]:
    json_count = 0
    toml_count = 0
    errors: list[str] = []
    for member in members:
        path = root / member
        try:
            if member.endswith(".json"):
                json.loads(path.read_text(encoding="utf-8"))
                json_count += 1
            elif member.endswith(".toml"):
                tomllib.loads(path.read_text(encoding="utf-8"))
                toml_count += 1
        except (OSError, UnicodeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"{member}: {exc}")
    return json_count, toml_count, errors


def _link_target(raw: str) -> str | None:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1 : value.index(">")]
    else:
        value = value.split(maxsplit=1)[0] if value else value
    if not value or value.startswith("#") or value.startswith("/"):
        return None
    split = urlsplit(value)
    if split.scheme or split.netloc:
        return None
    path = unquote(split.path)
    return path or None


def _markdown_links(root: Path, members: list[str]) -> tuple[int, int, list[str]]:
    markdown = [member for member in members if member.endswith(".md")]
    checked = 0
    errors: list[str] = []
    for member in markdown:
        path = root / member
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"{member}: {exc}")
            continue
        for raw in INLINE_LINK.findall(text):
            target = _link_target(raw)
            if target is None:
                continue
            checked += 1
            candidate = path.parent / target
            try:
                resolved = candidate.resolve(strict=True)
                resolved.relative_to(root)
            except (OSError, ValueError):
                errors.append(f"{member}: missing or escaping relative target {target}")
    return len(markdown), checked, errors



def _launcher_contract(root: Path) -> tuple[dict[str, Any], list[str]]:
    path = root / "lacuna"
    details: dict[str, Any] = {
        "path": "lacuna",
        "regular": False,
        "owner_executable": False,
        "shebang": None,
        "python_isolated": False,
        "bytecode_disabled": False,
    }
    errors: list[str] = []
    try:
        metadata = os.lstat(path)
    except OSError as exc:
        return details, [f"cannot inspect launcher: {exc}"]
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        return details, ["launcher must be one non-symlink regular file"]
    details["regular"] = True
    details["owner_executable"] = bool(metadata.st_mode & stat.S_IXUSR)
    if not details["owner_executable"]:
        errors.append("launcher owner-executable mode is missing")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return details, errors + [f"cannot read launcher: {exc}"]
    first = text.splitlines()[0] if text.splitlines() else ""
    details["shebang"] = first
    if first != "#!/bin/sh":
        errors.append("launcher shebang must be #!/bin/sh")
    details["python_isolated"] = 'exec python3 -S -m lacuna.cli "$@"' in text
    if not details["python_isolated"]:
        errors.append("launcher must execute python3 -S -m lacuna.cli")
    details["bytecode_disabled"] = "export PYTHONDONTWRITEBYTECODE=1" in text
    if not details["bytecode_disabled"]:
        errors.append("launcher must disable Python bytecode writes")
    return details, errors


def _version_coherence(root: Path) -> tuple[dict[str, str | None], list[str]]:
    values: dict[str, str | None] = {
        "runtime": __version__,
        "pyproject": None,
        "source": None,
        "revision": None,
        "revision_id": None,
        "artifact_root": None,
    }
    errors: list[str] = []
    try:
        project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        values["pyproject"] = str(project["project"]["version"])
    except (OSError, UnicodeError, KeyError, TypeError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"cannot read project version: {exc}")
    try:
        source = (root / "src/lacuna/__init__.py").read_text(encoding="utf-8")
        match = VERSION_ASSIGNMENT.search(source)
        if match is None:
            raise ValueError("__version__ assignment not found")
        values["source"] = match.group(1)
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"cannot read source version: {exc}")
    try:
        revision = json.loads((root / "REVISION.json").read_text(encoding="utf-8"))
        values["revision"] = str(revision["version"])
        values["revision_id"] = str(revision["revision"])
        values["artifact_root"] = str(revision["artifact_root"])
    except (OSError, UnicodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read revision version: {exc}")
    versions = [values[key] for key in ("runtime", "pyproject", "source", "revision") if values[key] is not None]
    if versions and len(set(versions)) != 1:
        errors.append(f"version declarations disagree: {values}")
    artifact_root = values.get("artifact_root")
    if artifact_root and artifact_root.rstrip("/") != root.name:
        errors.append(
            f"REVISION.json artifact_root {artifact_root!r} does not match extracted root {root.name!r}"
        )
    return values, errors


def audit_release_artifact(
    root: str | Path | None = None,
    *,
    strict_members: bool = False,
) -> dict[str, Any]:
    candidate = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    try:
        resolved = candidate.expanduser().resolve(strict=True)
    except OSError as exc:
        return {
            "event": ARTIFACT_AUDIT_EVENT,
            "schema": ARTIFACT_AUDIT_SCHEMA,
            "root": str(candidate),
            "project_version": __version__,
            "revision": "unknown",
            "strict_members": strict_members,
            "overall_status": "fail",
            "checks": [_check("root", "fail", f"cannot resolve artifact root: {exc}")],
            "counts": {},
            "warnings": [],
            "nonclaims": list(NONCLAIMS),
        }
    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    manifest_path = resolved / MANIFEST_FILE
    entries, manifest_errors = _manifest_entries(manifest_path)
    checks.append(
        _check(
            "manifest-format",
            "pass" if not manifest_errors else "fail",
            f"{len(entries)} unique manifest members parsed" if not manifest_errors else "manifest format or custody failed",
            errors=manifest_errors,
        )
    )
    member_names = [member for member, _digest in entries]
    missing: list[str] = []
    unsafe: list[str] = []
    mismatched: list[str] = []
    verified = 0
    for member, expected in entries:
        path, error = _safe_regular_member(resolved, member)
        if error is not None:
            if "cannot inspect" in error:
                missing.append(member)
            else:
                unsafe.append(error)
            continue
        assert path is not None
        try:
            actual = _sha256_file(path)
        except OSError as exc:
            unsafe.append(f"cannot hash {member}: {exc}")
            continue
        if actual != expected:
            mismatched.append(member)
        else:
            verified += 1
    manifest_member_errors = missing + unsafe + mismatched
    checks.append(
        _check(
            "manifest-members",
            "pass" if not manifest_member_errors else "fail",
            f"{verified}/{len(entries)} manifest members match" if not manifest_member_errors else "one or more manifest members are missing, unsafe, or changed",
            missing=missing,
            unsafe=unsafe,
            mismatched=mismatched,
        )
    )
    actual_files, tree_errors = _enumerate_tree(resolved)
    expected_files = set(member_names) | {MANIFEST_FILE}
    extras = sorted(actual_files - expected_files)
    ignored_runtime = [item for item in extras if _is_runtime_extra(item)]
    unlisted = [item for item in extras if item not in ignored_runtime]
    membership_failures = list(tree_errors)
    if strict_members:
        membership_failures.extend(unlisted)
        membership_failures.extend(ignored_runtime)
    elif unlisted:
        warnings.append(f"{len(unlisted)} unlisted non-runtime file(s) are present")
    if ignored_runtime:
        warnings.append(f"{len(ignored_runtime)} ignored runtime cache file(s) are present")
    checks.append(
        _check(
            "member-set",
            "pass" if not membership_failures else "fail",
            "tree has no unsafe nodes and satisfies the selected member policy" if not membership_failures else "tree membership or node safety failed",
            strict_members=strict_members,
            unlisted=unlisted,
            ignored_runtime=ignored_runtime,
            errors=tree_errors,
        )
    )
    python_count, python_errors = _python_syntax(resolved, member_names)
    checks.append(
        _check(
            "python-syntax",
            "pass" if not python_errors else "fail",
            f"{python_count} Python/launcher sources parsed" if not python_errors else "Python syntax parsing failed",
            errors=python_errors,
        )
    )
    json_count, toml_count, document_errors = _parse_documents(resolved, member_names)
    checks.append(
        _check(
            "json-toml-parse",
            "pass" if not document_errors else "fail",
            f"{json_count} JSON and {toml_count} TOML documents parsed" if not document_errors else "JSON/TOML parsing failed",
            errors=document_errors,
        )
    )
    markdown_count, link_count, link_errors = _markdown_links(resolved, member_names)
    checks.append(
        _check(
            "markdown-relative-links",
            "pass" if not link_errors else "fail",
            f"{link_count} relative targets across {markdown_count} Markdown files resolve" if not link_errors else "one or more relative Markdown targets do not resolve",
            errors=link_errors,
        )
    )
    launcher_details, launcher_errors = _launcher_contract(resolved)
    checks.append(
        _check(
            "launcher-contract",
            "pass" if not launcher_errors else "fail",
            "launcher is executable, isolated, and bytecode-clean" if not launcher_errors else "launcher contract failed",
            values=launcher_details,
            errors=launcher_errors,
        )
    )
    versions, version_errors = _version_coherence(resolved)
    checks.append(
        _check(
            "version-coherence",
            "pass" if not version_errors else "fail",
            f"version declarations agree at {versions.get('runtime')}" if not version_errors else "version declarations or artifact root disagree",
            values=versions,
            errors=version_errors,
        )
    )
    overall = "pass" if all(item["status"] == "pass" for item in checks) else "fail"
    return {
        "event": ARTIFACT_AUDIT_EVENT,
        "schema": ARTIFACT_AUDIT_SCHEMA,
        "root": str(resolved),
        "project_version": __version__,
        "revision": str(versions.get("revision_id") or "unknown"),
        "strict_members": strict_members,
        "overall_status": overall,
        "checks": checks,
        "counts": {
            "manifest_members": len(entries),
            "manifest_members_verified": verified,
            "actual_regular_files": len(actual_files),
            "unlisted_members": len(unlisted),
            "ignored_runtime_members": len(ignored_runtime),
            "python_sources": python_count,
            "json_documents": json_count,
            "toml_documents": toml_count,
            "markdown_files": markdown_count,
            "markdown_relative_targets": link_count,
        },
        "warnings": warnings,
        "nonclaims": list(NONCLAIMS),
    }


def artifact_audit_markdown(value: dict[str, Any]) -> str:
    lines = [
        "# Lacuna artifact check",
        "",
        f"- Status: **{value['overall_status']}**",
        f"- Revision: `{value['revision']}`",
        f"- Version: `{value['project_version']}`",
        f"- Root: `{value['root']}`",
        f"- Strict member set: **{'yes' if value['strict_members'] else 'no'}**",
        "",
        "| Check | Status | Summary |",
        "|---|---:|---|",
    ]
    for item in value["checks"]:
        summary = str(item["summary"]).replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{item['name']}` | {item['status']} | {summary} |")
    if value["warnings"]:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in value["warnings"])
    failed = [item for item in value["checks"] if item["status"] != "pass"]
    if failed:
        lines.extend(["", "## Failure details", ""])
        for item in failed:
            lines.append(f"### {item['name']}")
            lines.append("")
            details = item.get("details", {})
            lines.append("```json")
            lines.append(json.dumps(details, ensure_ascii=False, indent=2, sort_keys=True))
            lines.append("```")
            lines.append("")
    lines.extend(
        [
            "## Nonclaims",
            "",
            *(f"- {item}" for item in value["nonclaims"]),
            "",
        ]
    )
    return "\n".join(lines)
