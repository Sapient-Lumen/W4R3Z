#!/usr/bin/env python3
"""Shared publication-rights gate for artifact-emitting entry points.

Development validators may remain green while a rights ledger explicitly blocks
publication.  Any script that emits or updates public/full-release artifacts must
call this gate before it writes release records, materialized bundles, ZIP files,
or sidecars.

rev0842 hardening: do not rely only on generated rights ledgers for local
LICENSE/COPYING/NOTICE reference integrity.  The gate performs a narrow fresh
scan of likely payload/documentation text before making a publication decision,
so a stale ledger cannot accidentally unblock a tree whose shipped files point to
missing local rights files.

rev0845 hardening: the fresh scan now fails closed on symlinked scan inputs and
symlinked local rights targets, and it recognizes common HTML/reStructuredText
link forms.  Publication-critical scans should not read through host/cloudtainer
symlinks or accept license files that resolve indirectly through a mutable link.

rev0846 hardening: local rights targets are rejected if any intermediate archive
path component is a symlink, not only when the final LICENSE/COPYING/NOTICE file
itself is a symlink.

rev0848 hardening: local component-license references are also recognized when
they point into a LICENSES/licences/notices/copyright directory whose leaf file
name is not itself license-like (for example LICENSES/Apache-2.0.txt).

rev0849 hardening: HTML/XML documentation surfaces and conventional docs/ roots
are included in the fresh local rights-reference scan so web-rendered public
materials cannot carry missing local license links that Markdown-only scanning
would miss.

rev0850 hardening: the rights ledger itself and root LICENSE/COPYING/NOTICE
sentinels are now rejected when they are symlinks or pass through symlinked
components, so a future rights-unblock cannot be based on mutable host or
cloudtainer-local files.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True

RIGHTS_LEDGER_REL = "RIGHTS/component_license_ledger.json"
ROOT_RIGHTS_NAMES = ("LICENSE", "LICENSE.md", "COPYING", "NOTICE")
TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".htm",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".tex",
    ".toml",
    ".txt",
    ".xhtml",
    ".xml",
    ".yaml",
    ".yml",
}
LICENSE_REFERENCE_SCAN_ROOTS = (
    "README.md",
    "START_HERE.md",
    "docs/",
    "documentation/",
    "sources/",
    "papers/",
    "artifacts/curated/",
    "certs/curated/",
    "published/",
    "release_queue/",
)
LICENSE_REFERENCE_SCAN_EXCLUDED_PREFIXES = (
    "AUDIT/",
    "CHECKS/",
    "INDEX/",
    "PATCHES/",
    "PROVENANCE/",
    "RIGHTS/",
    "SBOM/",
    "VALIDATION/",
)
LICENSE_REFERENCE_SCAN_EXCLUDED_NAMES = {
    "DEDUPE_REPORT.md",
    "MANIFEST.sha256",
}
MAX_TEXT_BYTES_FOR_FRESH_SCAN = 2_000_000
LICENSE_WORD_RE = re.compile(r"\b(?:licen[cs]e|notice|copying)\b", re.IGNORECASE)
MARKDOWN_LINK_RE = re.compile(
    r"\[(?P<label>[^\]\n]{0,180})\]\(\s*"
    r"(?P<target><[^>\n]+>|[^)\s]+)"
    r"(?:\s+['\"][^)\n]*['\"])?\s*\)"
)
MARKDOWN_REFERENCE_DEF_RE = re.compile(
    r"^\s*\[(?P<label>[^\]\n]{1,180})\]:\s*"
    r"(?P<target><[^>\n]+>|[^\s]+)"
    r"(?:\s+.*)?$"
)
HTML_HREF_RE = re.compile(
    r"<a\s+[^>]*?href\s*=\s*(?P<quote>['\"]?)(?P<target>[^'\"\s>]+)(?P=quote)[^>]*>"
    r"(?P<label>.*?)</a>",
    re.IGNORECASE,
)
RST_INLINE_LINK_RE = re.compile(r"`(?P<label>[^`\n]{1,180})\s*<(?P<target>[^>\n]+)>`_?")
RST_REFERENCE_DEF_RE = re.compile(r"^\s*\.\.\s+_(?P<label>[^:\n]{1,180}):\s*(?P<target>\S+)")
BARE_LOCAL_RE = re.compile(
    r"\b(?:see|refer(?:s|red)?\s+to|consult)\s+(?:the\s+)?"
    r"(?P<target>`?(?:LICENSE(?:\.[A-Za-z0-9]+)?|COPYING(?:\.[A-Za-z0-9]+)?|NOTICE(?:\.[A-Za-z0-9]+)?)`?)"
    r"(?:\s+file)?\b",
    re.IGNORECASE,
)
LICENSE_TARGET_BASENAME_RE = re.compile(
    r"^(?:LICEN[CS]E(?:\.[A-Za-z0-9]+)?|COPYING(?:\.[A-Za-z0-9]+)?|NOTICE(?:\.[A-Za-z0-9]+)?|COPYRIGHT(?:\.[A-Za-z0-9]+)?|LICEN[CS]ES?)$",
    re.IGNORECASE,
)
LICENSE_TARGET_COMPONENT_RE = re.compile(
    r"^(?:LICEN[CS]ES?|COPYING|NOTICES?|COPYRIGHTS?)$",
    re.IGNORECASE,
)


def _coerce_blockers(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _archive_regular_file_error(root: Path, path: Path, label: str) -> str | None:
    """Return a blocking error when a publication-critical input is unsafe."""
    first_symlink, first_symlink_rel = _first_symlink_component(root, path)
    if first_symlink is not None:
        return f"{label} resolves through a symlink component: {first_symlink_rel}"
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except ValueError:
        return f"{label} escapes archive root"
    if not path.exists():
        return f"missing {label}"
    if not path.is_file():
        return f"{label} is not a regular file"
    return None


def _load_ledger(root: Path) -> tuple[dict[str, Any], str | None]:
    path = root / RIGHTS_LEDGER_REL
    safety_error = _archive_regular_file_error(root, path, RIGHTS_LEDGER_REL)
    if safety_error is not None:
        return {}, safety_error
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exercised through CLI scripts
        return {}, f"invalid {RIGHTS_LEDGER_REL}: {exc}"
    if not isinstance(data, dict):
        return {}, f"invalid {RIGHTS_LEDGER_REL}: expected JSON object"
    return data, None


def _root_rights_file_audit(root: Path) -> dict[str, Any]:
    regular_files: list[str] = []
    symlink_rejected: list[dict[str, str | None]] = []
    non_regular_rejected: list[str] = []
    for name in ROOT_RIGHTS_NAMES:
        path = root / name
        if not path.exists() and not path.is_symlink():
            continue
        first_symlink, first_symlink_rel = _first_symlink_component(root, path)
        if first_symlink is not None:
            symlink_rejected.append({"path": name, "symlink_archive_path": first_symlink_rel})
            continue
        try:
            path.resolve(strict=False).relative_to(root.resolve())
        except ValueError:
            symlink_rejected.append({"path": name, "symlink_archive_path": None})
            continue
        if path.is_file():
            regular_files.append(name)
        else:
            non_regular_rejected.append(name)
    return {
        "regular_files": regular_files,
        "symlink_rejected": symlink_rejected,
        "non_regular_rejected": non_regular_rejected,
    }


def _as_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _as_rel_safe(root: Path, path: Path) -> str:
    try:
        return _as_rel(root, path)
    except ValueError:
        return str(path)


def _is_probably_text(path: Path) -> bool:
    if path.name in {"README", "LICENSE", "COPYING", "NOTICE"}:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def _iter_license_reference_scan_files(root: Path) -> tuple[list[Path], int, list[str]]:
    files: set[Path] = set()
    skipped_too_large = 0
    symlink_paths: list[str] = []
    for entry in LICENSE_REFERENCE_SCAN_ROOTS:
        base = root / entry.rstrip("/")
        if base.is_symlink():
            symlink_paths.append(entry.rstrip("/") or ".")
            continue
        if not base.exists():
            continue
        candidates: list[Path] = []
        if base.is_file():
            candidates = [base]
        elif base.is_dir():
            for child in base.rglob("*"):
                if child.is_symlink():
                    symlink_paths.append(_as_rel_safe(root, child))
                    continue
                if child.is_file():
                    candidates.append(child)
        for child in candidates:
            rel = _as_rel(root, child)
            if rel in LICENSE_REFERENCE_SCAN_EXCLUDED_NAMES:
                continue
            if any(rel.startswith(prefix) for prefix in LICENSE_REFERENCE_SCAN_EXCLUDED_PREFIXES):
                continue
            if not _is_probably_text(child):
                continue
            try:
                if child.stat().st_size > MAX_TEXT_BYTES_FOR_FRESH_SCAN:
                    skipped_too_large += 1
                    continue
            except OSError:
                continue
            files.add(child)
    return sorted(files, key=lambda p: _as_rel(root, p)), skipped_too_large, sorted(set(symlink_paths))


def _read_text_lossy(path: Path) -> str | None:
    try:
        if path.is_symlink():
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def _normalize_target(raw: str) -> str:
    target = html.unescape(raw.strip()).strip("`'\"")
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if "#" in target:
        target = target.split("#", 1)[0]
    return target


def _target_basename_is_license_like(target: str) -> bool:
    if not target:
        return False
    return bool(LICENSE_TARGET_BASENAME_RE.match(PurePosixPath(target.replace("\\", "/")).name))


def _target_path_is_license_like(target: str) -> bool:
    """Return true for local paths that are lexically rights-file locations.

    Some projects put component terms under directories such as LICENSES/ or
    notices/ with filenames like Apache-2.0.txt.  Earlier fresh scans only
    looked at the link label or final basename, so a reference to
    `LICENSES/Apache-2.0.txt` with label `Apache-2.0` could be missed.
    """
    if not target:
        return False
    normalized = target.replace("\\", "/")
    parts = [part for part in PurePosixPath(normalized).parts if part not in {"", ".", "/"}]
    return _target_basename_is_license_like(normalized) or any(LICENSE_TARGET_COMPONENT_RE.match(part) for part in parts)


def _reference_is_rights_like(label: str, target: str) -> bool:
    return bool(LICENSE_WORD_RE.search(label or "")) or _target_path_is_license_like(target)


def _external_scheme(target: str) -> str | None:
    parsed = urlparse(target)
    if target.startswith("//"):
        return "network-path"
    if parsed.scheme and parsed.scheme.lower() != "file":
        return parsed.scheme.lower()
    return None


def _file_uri_parts(target: str) -> tuple[str, str] | None:
    parsed = urlparse(target)
    if parsed.scheme.lower() == "file":
        return parsed.netloc, unquote(parsed.path)
    return None


def _unresolved_local_target(root: Path, source: Path, target: str) -> tuple[Path | None, dict[str, Any]]:
    file_uri = _file_uri_parts(target)
    if file_uri is not None:
        netloc, file_path = file_uri
        if netloc and netloc.lower() != "localhost":
            return None, {"target_class": "local_outside_archive", "status": "outside_archive", "file_uri_netloc": netloc}
        target = file_path
    # Treat leading slash as an archive-root path, not as a host path.  Host/private cloud paths
    # will therefore fail closed as missing archive paths.
    if target.startswith("/"):
        return root / target.lstrip("/"), {}
    return source.parent / target, {}


def _first_symlink_component(root: Path, candidate: Path) -> tuple[Path | None, str | None]:
    """Return the first symlink component on an archive-local candidate path.

    Path.is_symlink() only detects the final component.  For publication rights
    references, `docs/link/LICENSE` must also fail closed when `docs/link` is a
    symlink, even if the resolved target eventually points back inside the
    archive.  The scan is lexical and stops at the first component that exists as
    a symlink.
    """
    root = root.resolve()
    try:
        rel = candidate.relative_to(root)
    except ValueError:
        try:
            rel = candidate.resolve(strict=False).relative_to(root)
        except ValueError:
            return None, None
    cursor = root
    for part in rel.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            try:
                return cursor, cursor.relative_to(root).as_posix()
            except ValueError:
                return cursor, str(cursor)
    return None, None


def _classify_license_reference(root: Path, source: Path, raw_target: str, label: str, kind: str) -> dict[str, Any] | None:
    if raw_target.strip().startswith("#") or raw_target.strip().startswith("<#"):
        return None
    target = _normalize_target(raw_target)
    if not target:
        return None
    if not _reference_is_rights_like(label, target):
        return None
    row: dict[str, Any] = {
        "source_path": _as_rel(root, source),
        "reference_kind": kind,
        "label": html.unescape(label.strip()),
        "target_text": target,
    }
    scheme = _external_scheme(target)
    if scheme is not None:
        row.update({"target_class": "external", "external_scheme": scheme, "status": "not_checked_by_local_integrity_scan"})
        return row
    candidate, early_status = _unresolved_local_target(root, source, target)
    if candidate is None:
        row.update(early_status)
        return row
    first_symlink, first_symlink_rel = _first_symlink_component(root, candidate)
    candidate_is_symlink = first_symlink is not None
    resolved = candidate.resolve(strict=False)
    try:
        resolved_rel = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        row.update({"target_class": "local_outside_archive", "status": "outside_archive"})
        return row
    if candidate_is_symlink:
        row.update(
            {
                "target_class": "local_archive_symlink",
                "resolved_archive_path": resolved_rel,
                "symlink_archive_path": first_symlink_rel,
                "target_exists": False,
                "status": "target_symlink_rejected",
            }
        )
        return row
    exists = candidate.is_file()
    row.update(
        {
            "target_class": "local_archive_relative",
            "resolved_archive_path": resolved_rel,
            "target_exists": exists,
            "status": "ok" if exists else "missing",
        }
    )
    return row


def fresh_local_license_reference_scan(root: Path) -> dict[str, Any]:
    """Return a fresh, narrow scan of local LICENSE/COPYING/NOTICE references.

    This intentionally duplicates the release-critical part of the broader
    generated license-reference audit so publication entry points fail closed even
    when RIGHTS/component_license_ledger.json or generated audit files are stale.
    """
    root = root.resolve()
    scan_roots_present = [entry for entry in LICENSE_REFERENCE_SCAN_ROOTS if (root / entry.rstrip("/")).exists()]
    scan_roots_missing = [entry for entry in LICENSE_REFERENCE_SCAN_ROOTS if entry not in scan_roots_present]
    canonical_payload_roots_present = (root / "sources").exists() and (root / "papers").exists()
    files, skipped_too_large, symlink_paths = _iter_license_reference_scan_files(root)
    references: list[dict[str, Any]] = []
    unreadable = 0
    for path in files:
        text = _read_text_lossy(path)
        if text is None:
            unreadable += 1
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in MARKDOWN_LINK_RE.finditer(line):
                row = _classify_license_reference(root, path, match.group("target"), match.group("label"), "markdown_link")
                if row:
                    row["line"] = line_no
                    references.append(row)
            reference_def = MARKDOWN_REFERENCE_DEF_RE.match(line)
            if reference_def:
                row = _classify_license_reference(
                    root,
                    path,
                    reference_def.group("target"),
                    reference_def.group("label"),
                    "markdown_reference_definition",
                )
                if row:
                    row["line"] = line_no
                    references.append(row)
            for match in HTML_HREF_RE.finditer(line):
                row = _classify_license_reference(root, path, match.group("target"), match.group("label"), "html_href")
                if row:
                    row["line"] = line_no
                    references.append(row)
            for match in RST_INLINE_LINK_RE.finditer(line):
                row = _classify_license_reference(root, path, match.group("target"), match.group("label"), "rst_inline_link")
                if row:
                    row["line"] = line_no
                    references.append(row)
            rst_def = RST_REFERENCE_DEF_RE.match(line)
            if rst_def:
                row = _classify_license_reference(root, path, rst_def.group("target"), rst_def.group("label"), "rst_reference_definition")
                if row:
                    row["line"] = line_no
                    references.append(row)
            for match in BARE_LOCAL_RE.finditer(line):
                row = _classify_license_reference(root, path, match.group("target"), match.group("target"), "bare_local_file_reference")
                if row:
                    row["line"] = line_no
                    references.append(row)
    seen: set[tuple[str, int, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for row in references:
        key = (row["source_path"], int(row.get("line", 0)), row["target_text"], row["reference_kind"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    missing = [row for row in unique if row.get("status") == "missing"]
    outside = [row for row in unique if row.get("status") == "outside_archive"]
    target_symlink = [row for row in unique if row.get("status") == "target_symlink_rejected"]
    ok = [row for row in unique if row.get("status") == "ok"]
    external = [row for row in unique if row.get("target_class") == "external"]
    blocking_references = missing + outside + target_symlink
    return {
        "version": 2,
        "status": "blocking_local_license_reference_integrity" if blocking_references or symlink_paths else "license_references_locally_resolved",
        "scan_roots": list(LICENSE_REFERENCE_SCAN_ROOTS),
        "scan_roots_present": scan_roots_present,
        "scan_roots_missing": scan_roots_missing,
        "canonical_payload_roots_present": canonical_payload_roots_present,
        "excluded_prefixes": list(LICENSE_REFERENCE_SCAN_EXCLUDED_PREFIXES),
        "files_examined": len(files),
        "files_skipped_too_large": skipped_too_large,
        "files_unreadable": unreadable,
        "files_symlink_rejected": len(symlink_paths),
        "symlink_paths_rejected": symlink_paths[:50],
        "references_total": len(unique),
        "local_references_ok": len(ok),
        "local_references_missing": len(missing),
        "local_references_outside_archive": len(outside),
        "local_references_target_symlink_rejected": len(target_symlink),
        "external_references_not_checked": len(external),
        "missing_or_outside_local_license_reference_count": len(missing) + len(outside),
        "missing_or_outside_local_license_references": missing + outside,
        "blocking_local_license_reference_count": len(blocking_references),
        "blocking_local_license_references": blocking_references,
    }


def _coerce_optional_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def publication_rights_gate_status(root: Path) -> dict[str, Any]:
    """Return the publication-rights decision used by release emitters."""
    root = root.resolve()
    ledger, load_error = _load_ledger(root)
    blockers = _coerce_blockers(ledger.get("blocking_findings", [])) if not load_error else []
    blocker_ids = [str(item.get("id")) for item in blockers if item.get("id")]
    decision_required = bool(ledger.get("decision_required_before_publication")) if not load_error else True
    status = str(ledger.get("status", "missing")) if not load_error else "publication_blocked_missing_rights_ledger"
    ledger_root_rights_present = bool(ledger.get("root_license_or_notice_file_present")) if not load_error else False
    root_rights_audit = _root_rights_file_audit(root)
    actual_root_rights_files = list(root_rights_audit["regular_files"])
    root_rights_symlink_rejected = list(root_rights_audit["symlink_rejected"])
    root_rights_non_regular_rejected = list(root_rights_audit["non_regular_rejected"])
    actual_root_rights_present = bool(actual_root_rights_files)
    root_rights_present = ledger_root_rights_present and actual_root_rights_present and not root_rights_symlink_rejected and not root_rights_non_regular_rejected
    fresh_scan = fresh_local_license_reference_scan(root)
    fresh_missing_or_outside = int(fresh_scan["missing_or_outside_local_license_reference_count"])
    fresh_target_symlinks = int(fresh_scan.get("local_references_target_symlink_rejected", 0))
    fresh_scan_symlinks = int(fresh_scan.get("files_symlink_rejected", 0))
    ledger_missing_or_outside = _coerce_optional_int(ledger.get("missing_or_outside_local_license_reference_count")) if not load_error else None
    blocked_reasons: list[str] = []
    if load_error:
        blocked_reasons.append("rights_ledger_load_error")
    if decision_required:
        blocked_reasons.append("decision_required_before_publication")
    if blockers:
        blocked_reasons.append("blocking_findings_present")
    if status.startswith("publication_blocked"):
        blocked_reasons.append("ledger_status_blocks_publication")
    if not ledger_root_rights_present:
        blocked_reasons.append("ledger_reports_no_root_license_or_notice")
    if not actual_root_rights_present:
        blocked_reasons.append("root_license_or_notice_file_absent")
    elif not root_rights_present:
        blocked_reasons.append("root_license_or_notice_ledger_stale")
    if root_rights_symlink_rejected:
        blocked_reasons.append("root_license_or_notice_symlink_rejected")
    if root_rights_non_regular_rejected:
        blocked_reasons.append("root_license_or_notice_non_regular_rejected")
    if fresh_missing_or_outside:
        blocked_reasons.append("fresh_local_license_reference_missing_or_outside")
    if fresh_target_symlinks:
        blocked_reasons.append("fresh_local_license_reference_target_symlink")
    if fresh_scan_symlinks:
        blocked_reasons.append("fresh_license_reference_scan_symlink_rejected")
    ledger_count_comparable = bool(fresh_scan.get("canonical_payload_roots_present"))
    if ledger_missing_or_outside is not None and not ledger_count_comparable:
        blocked_reasons.append("license_reference_scan_scope_partial")
    elif ledger_missing_or_outside is not None and ledger_missing_or_outside != fresh_missing_or_outside:
        blocked_reasons.append("license_reference_ledger_stale")

    return {
        "rights_ledger": RIGHTS_LEDGER_REL,
        "blocked": bool(blocked_reasons),
        "blocked_reasons": blocked_reasons,
        "load_error": load_error,
        "ledger_status": status,
        "decision_required_before_publication": decision_required,
        "blocking_finding_ids": blocker_ids,
        "blocking_finding_count": len(blockers),
        "ledger_root_license_or_notice_file_present": ledger_root_rights_present,
        "actual_root_license_or_notice_file_present": actual_root_rights_present,
        "actual_root_license_or_notice_files": actual_root_rights_files,
        "root_license_or_notice_symlink_rejected": root_rights_symlink_rejected,
        "root_license_or_notice_non_regular_rejected": root_rights_non_regular_rejected,
        "root_license_or_notice_file_present": root_rights_present,
        "fresh_local_license_reference_scan": fresh_scan,
        "license_reference_ledger_count_comparable": ledger_count_comparable,
        "ledger_missing_or_outside_local_license_reference_count": ledger_missing_or_outside,
        "fresh_missing_or_outside_local_license_reference_count": fresh_missing_or_outside,
        "fresh_target_symlink_license_reference_count": fresh_target_symlinks,
        "fresh_scan_symlink_path_count": fresh_scan_symlinks,
    }


def format_publication_rights_block(context: str, status: dict[str, Any]) -> str:
    blockers = status.get("blocking_finding_ids") or ["unspecified_rights_blocker"]
    reasons = status.get("blocked_reasons") or ["unspecified_rights_reason"]
    detail = status.get("load_error") or status.get("ledger_status") or "<missing>"
    fresh_count = status.get("fresh_missing_or_outside_local_license_reference_count", "unknown")
    ledger_count = status.get("ledger_missing_or_outside_local_license_reference_count", "unknown")
    symlink_count = status.get("fresh_target_symlink_license_reference_count", "unknown")
    scan_symlink_count = status.get("fresh_scan_symlink_path_count", "unknown")
    root_rights_symlink_count = len(status.get("root_license_or_notice_symlink_rejected") or [])
    return (
        f"{context}: publication rights gate blocked; "
        f"status={detail}; "
        f"decision_required_before_publication={str(bool(status.get('decision_required_before_publication'))).lower()}; "
        f"root_license_or_notice_file_present={str(bool(status.get('root_license_or_notice_file_present'))).lower()}; "
        f"fresh_missing_or_outside_local_license_references={fresh_count}; "
        f"fresh_target_symlink_license_references={symlink_count}; "
        f"fresh_scan_symlink_paths={scan_symlink_count}; "
        f"root_rights_symlink_rejected={root_rights_symlink_count}; "
        f"ledger_missing_or_outside_local_license_references={ledger_count}; "
        f"blockers={','.join(str(x) for x in blockers)}; "
        f"reasons={','.join(str(x) for x in reasons)}; "
        "repair=add owner-approved root LICENSE/NOTICE, resolve missing local license references, remove symlinked publication-critical rights paths, refresh RIGHTS/component_license_ledger.json, then retry publication"
    )


def assert_publication_rights_ready(root: Path, context: str) -> None:
    """Exit when an artifact-emitting publication path is not rights-ready."""
    status = publication_rights_gate_status(root)
    if status["blocked"]:
        raise SystemExit(format_publication_rights_block(context, status))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether publication rights allow release emission.")
    parser.add_argument("--context", default="publication-rights-gate", help="operator context for diagnostics")
    parser.add_argument("--root", default=None, help="archive root to check; defaults to the parent of scripts/")
    parser.add_argument("--json", action="store_true", help="emit the raw gate status as JSON on success")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    status = publication_rights_gate_status(root)
    if status["blocked"]:
        print(format_publication_rights_block(args.context, status), file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print(f"{args.context}: publication rights gate OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
