#!/usr/bin/env python3
"""Build a focused audit for local LICENSE/COPYING/NOTICE references.

This is deliberately narrower than a general rights scanner.  It answers one
release-critical question: do shipped payload files tell the reader to consult a
local license/notice file that the archive did not ship?
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "RIGHTS" / "license_reference_integrity_audit.json"
MD_OUT = ROOT / "RIGHTS" / "license_reference_integrity_audit.md"

TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".rst",
    ".tex",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SCAN_ROOTS = (
    "README.md",
    "START_HERE.md",
    "sources/",
    "papers/",
    "published/",
    "release_queue/",
)
EXCLUDED_ROOT_PREFIXES = (
    "AUDIT/",
    "RIGHTS/",
    "SBOM/",
    "INDEX/",
    "PROVENANCE/",
)
EXCLUDED_FILE_NAMES = {
    "MANIFEST.sha256",
    "DEDUPE_REPORT.md",
}
MARKDOWN_LINK_RE = re.compile(
    r"\[(?P<label>[^\]\n]{0,120}(?:licen[cs]e|notice|copying)[^\]\n]{0,120})\]"
    r"\((?P<target>[^)\s]+)\)",
    re.IGNORECASE,
)
BARE_LOCAL_RE = re.compile(
    r"\b(?:see|refer(?:s|red)?\s+to|consult)\s+(?:the\s+)?"
    r"(?P<target>`?(?:LICENSE(?:\.[A-Za-z0-9]+)?|COPYING(?:\.[A-Za-z0-9]+)?|NOTICE(?:\.[A-Za-z0-9]+)?)`?)"
    r"(?:\s+file)?\b",
    re.IGNORECASE,
)
LICENSE_TARGET_BASENAME_RE = re.compile(r"^(?:LICENSE(?:\.[A-Za-z0-9]+)?|COPYING(?:\.[A-Za-z0-9]+)?|NOTICE(?:\.[A-Za-z0-9]+)?)$", re.IGNORECASE)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_probably_text(path: Path) -> bool:
    if path.name in {"README", "LICENSE", "COPYING", "NOTICE"}:
        return True
    return path.suffix.lower() in TEXT_SUFFIXES


def iter_scan_files(root: Path = ROOT) -> list[Path]:
    files: set[Path] = set()
    for entry in SCAN_ROOTS:
        p = root / entry.rstrip("/")
        if not p.exists():
            continue
        if p.is_file():
            candidates = [p]
        else:
            candidates = [child for child in p.rglob("*") if child.is_file()]
        for child in candidates:
            r = child.relative_to(root).as_posix()
            if r in EXCLUDED_FILE_NAMES:
                continue
            if any(r.startswith(prefix) for prefix in EXCLUDED_ROOT_PREFIXES):
                continue
            if not is_probably_text(child):
                continue
            files.add(child)
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())


def read_text_lossy(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:4096]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("utf-8", errors="replace")
        except Exception:
            return None


def normalize_target(raw: str) -> str:
    target = raw.strip().strip("`'\"")
    if "#" in target:
        target = target.split("#", 1)[0]
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target


def is_external_target(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme and parsed.scheme not in {"", "file"}) or target.startswith("//")


def resolves_to_local_license_like(target: str) -> bool:
    if not target or target.startswith("#"):
        return False
    # Keep this audit intentionally scoped to license/notice/copying file targets.
    base = Path(target).name
    return bool(LICENSE_TARGET_BASENAME_RE.match(base))


def resolve_local_target(source: Path, target: str) -> Path:
    # Treat absolute archive paths as archive-root paths, but do not allow host paths.
    if target.startswith("/"):
        return (ROOT / target.lstrip("/")).resolve()
    return (source.parent / target).resolve()


def classify_reference(source: Path, raw_target: str, label: str, kind: str) -> dict[str, Any] | None:
    target = normalize_target(raw_target)
    if not resolves_to_local_license_like(target) and not is_external_target(target):
        return None
    row: dict[str, Any] = {
        "source_path": rel(source),
        "reference_kind": kind,
        "label": label.strip(),
        "target_text": target,
    }
    if is_external_target(target):
        row.update({"target_class": "external", "status": "not_checked_by_local_integrity_audit"})
        return row
    resolved = resolve_local_target(source, target)
    try:
        resolved_rel = resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        row.update({"target_class": "local_outside_archive", "status": "outside_archive"})
        return row
    exists = resolved.is_file()
    row.update({
        "target_class": "local_archive_relative",
        "resolved_archive_path": resolved_rel,
        "target_exists": exists,
        "status": "ok" if exists else "missing",
    })
    return row


def build(root: Path = ROOT) -> dict[str, Any]:
    global ROOT, JSON_OUT, MD_OUT
    old_root = ROOT
    ROOT = root
    JSON_OUT = ROOT / "RIGHTS" / "license_reference_integrity_audit.json"
    MD_OUT = ROOT / "RIGHTS" / "license_reference_integrity_audit.md"
    try:
        files = iter_scan_files(ROOT)
        references: list[dict[str, Any]] = []
        for path in files:
            text = read_text_lossy(path)
            if text is None:
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                for match in MARKDOWN_LINK_RE.finditer(line):
                    row = classify_reference(path, match.group("target"), match.group("label"), "markdown_link")
                    if row:
                        row["line"] = line_no
                        references.append(row)
                for match in BARE_LOCAL_RE.finditer(line):
                    row = classify_reference(path, match.group("target"), match.group("target"), "bare_local_file_reference")
                    if row:
                        row["line"] = line_no
                        references.append(row)
        # De-duplicate rows where a Markdown link also satisfies the bare phrase regex.
        seen: set[tuple[str, int, str, str]] = set()
        unique: list[dict[str, Any]] = []
        for row in references:
            key = (row["source_path"], int(row.get("line", 0)), row["target_text"], row["reference_kind"])
            if key in seen:
                continue
            seen.add(key)
            unique.append(row)
        missing = [r for r in unique if r.get("status") == "missing"]
        outside = [r for r in unique if r.get("status") == "outside_archive"]
        external = [r for r in unique if r.get("target_class") == "external"]
        ok = [r for r in unique if r.get("status") == "ok"]
        return {
            "version": 1,
            "revision_context": "rev0836-session-patch-over-rev0835-over-rev0826",
            "status": "blocking_missing_local_license_references" if missing or outside else "license_references_locally_resolved",
            "scope": {
                "scan_roots": list(SCAN_ROOTS),
                "excluded_root_prefixes": list(EXCLUDED_ROOT_PREFIXES),
                "excluded_file_names": sorted(EXCLUDED_FILE_NAMES),
                "text_suffixes": sorted(TEXT_SUFFIXES),
                "purpose": "Check whether shipped payload/docs point to local LICENSE/COPYING/NOTICE files that are absent from the archive.",
            },
            "files_examined": len(files),
            "references_total": len(unique),
            "local_references_ok": len(ok),
            "local_references_missing": len(missing),
            "local_references_outside_archive": len(outside),
            "external_references_not_checked": len(external),
            "missing_or_outside_references": missing + outside,
            "references": unique,
            "builder": "scripts/build_license_reference_integrity_audit.py",
            "validator": "scripts/validate_license_reference_integrity_audit.py",
        }
    finally:
        ROOT = old_root


def render_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# License reference integrity audit",
        "",
        "This audit is intentionally narrow: it checks whether shipped payload/documentation files point to local `LICENSE`, `COPYING`, or `NOTICE` files that are not present in the archive.",
        "",
        f"- Status: `{data['status']}`",
        f"- Files examined: **{data['files_examined']}**",
        f"- References found: **{data['references_total']}**",
        f"- Local references resolved: **{data['local_references_ok']}**",
        f"- Local references missing: **{data['local_references_missing']}**",
        f"- Local references outside archive: **{data['local_references_outside_archive']}**",
        f"- External references not checked: **{data['external_references_not_checked']}**",
        "",
        "## Missing or outside local references",
        "",
    ]
    rows = data.get("missing_or_outside_references", [])
    if rows:
        lines.extend([
            "| Source | Line | Target text | Resolved archive path | Status |",
            "| --- | ---: | --- | --- | --- |",
        ])
        for row in rows:
            lines.append(
                f"| `{row['source_path']}` | {row.get('line', '')} | `{row.get('target_text', '')}` | "
                f"`{row.get('resolved_archive_path', '')}` | `{row.get('status', '')}` |"
            )
    else:
        lines.append("No missing local license/notice references found in the configured scan scope.")
    lines.extend([
        "",
        "## Scope",
        "",
        f"- Scan roots: {', '.join(f'`{x}`' for x in data['scope']['scan_roots'])}",
        f"- Excluded prefixes: {', '.join(f'`{x}`' for x in data['scope']['excluded_root_prefixes'])}",
        "- This audit does not infer a license; it only checks reference integrity.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    data = build(ROOT)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(data), encoding="utf-8")
    print(
        "license-reference-integrity-build: OK "
        f"({data['files_examined']} files, {data['local_references_missing']} missing local references)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
