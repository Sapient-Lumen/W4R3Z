#!/usr/bin/env python3
"""Fail closed on quarantined state/local source use in public-answer docs.

The state/local quarantine and adopter capture validator make the source records
safe, but public-answer surface prose can still leak examples into something
that looks like current voter instruction.  This checker scans voter-facing
markdown surfaces for quarantined state/local xrefs and requires a local
non-instruction boundary wherever those examples are gathered or described.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
LOCK = ROOT / "evidence" / "lock" / "external-sources.toml"
REPORT = ROOT / "artifacts" / "reports" / "quarantined-source-public-surface-firewall-report.json"

XREF_RE = re.compile(r"xref:\s*`([^`]+)`")
BOUNDARY_RE = re.compile(r"not\s+current\s+voter\s+instruction", re.I)
MARKER = "STATE_LOCAL_QUARANTINE_BOUNDARY:"
RISKY_HEADING_RE = re.compile(r"^##\s+Sources\s*\((?:authoritative|current)", re.I | re.M)
OFFICIAL_ROUTE_HEADING_RE = re.compile(r"^##\s+Sources\s*\(official route examples; not current voter instruction\)\s*$", re.I | re.M)
RISKY_CLAIM_RE = re.compile(
    r"\b(current|says?|states?|explains?|allow(?:s|ing)?|requires?|eligible|ineligible|may|must|should|authoritative|controlling)\b",
    re.I,
)
ARCHIVAL_SKIP_PREFIXES = (
    "docs/230-external-sources-by-primary-tag.md",
    "artifacts/reports/",
)
SCAN_ROOTS = ("docs", "artifacts/checklists", "artifacts/templates")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_sources() -> dict[str, dict[str, Any]]:
    with LOCK.open("rb") as f:
        rows = tomllib.load(f).get("source", [])
    return {str(r.get("id") or ""): r for r in rows if isinstance(r, dict) and str(r.get("id") or "")}


def tags_of(row: dict[str, Any]) -> set[str]:
    return {str(t).strip() for t in (row.get("tags") or []) if str(t).strip()}


def quarantined_source_ids(sources: dict[str, dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for sid, row in sources.items():
        tags = tags_of(row)
        if {"jurisdiction_quarantine", "not_current_voter_instruction"} <= tags and not str(row.get("sha256") or "").strip():
            ids.add(sid)
    return ids


def scan_paths() -> list[Path]:
    paths: list[Path] = []
    for root_s in SCAN_ROOTS:
        root = ROOT / root_s
        if root.exists():
            paths.extend(p for p in root.rglob("*.md") if p.is_file())
    return sorted(paths)


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return any(rel == prefix or rel.startswith(prefix) for prefix in ARCHIVAL_SKIP_PREFIXES)


def paragraph_spans(lines: list[str]) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    start = 0
    buf: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if line.strip() == "":
            if buf:
                spans.append((start, idx - 1, "\n".join(buf)))
                buf = []
            start = idx + 1
            continue
        if not buf:
            start = idx
        buf.append(line)
    if buf:
        spans.append((start, len(lines), "\n".join(buf)))
    return spans


def build_report() -> dict[str, Any]:
    sources = load_sources()
    quarantined = quarantined_source_ids(sources)
    errors: list[str] = []
    files: list[dict[str, Any]] = []
    occurrence_count = 0
    risky_paragraph_count = 0

    for path in scan_paths():
        if should_skip(path):
            continue
        rel = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        cited_file = sorted({sid for sid in XREF_RE.findall(text) if sid in quarantined})
        if not cited_file:
            continue
        lines = text.splitlines()
        occurrences: list[dict[str, Any]] = []
        for lineno, line in enumerate(lines, start=1):
            cited = sorted({sid for sid in XREF_RE.findall(line) if sid in quarantined})
            if not cited:
                continue
            occurrence_count += len(cited)
            occurrences.append({"line": lineno, "source_ids": cited, "text_sha256": sha256_text(line)})

        has_marker = MARKER in text
        has_boundary = bool(BOUNDARY_RE.search(text))
        has_official_route_heading = bool(OFFICIAL_ROUTE_HEADING_RE.search(text))
        risky_heading = bool(RISKY_HEADING_RE.search(text))
        if not has_marker:
            errors.append(f"{rel}: missing {MARKER} block for quarantined state/local xrefs")
        if not has_boundary:
            errors.append(f"{rel}: missing 'not current voter instruction' boundary")
        if risky_heading:
            errors.append(f"{rel}: source heading still frames quarantined rows as authoritative/current examples")
        if rel.startswith("docs/") and not has_official_route_heading:
            errors.append(f"{rel}: missing official-route/non-instruction Sources heading")

        for start, end, para in paragraph_spans(lines):
            cited_para = sorted({sid for sid in XREF_RE.findall(para) if sid in quarantined})
            if not cited_para:
                continue
            # Paragraphs that make an active claim about a quarantined route must
            # carry the boundary locally unless they are in the explicitly marked
            # source list.  This catches example prose that starts to sound like
            # live voter guidance.
            if RISKY_CLAIM_RE.search(para) and not BOUNDARY_RE.search(para):
                # Allow compact bullet rows only when the file has the standard
                # source heading + marker; the marker is then the local section
                # boundary for the source list.
                is_bullet = para.lstrip().startswith("- ")
                if not (is_bullet and has_marker and has_official_route_heading):
                    risky_paragraph_count += 1
                    errors.append(
                        f"{rel}:{start}-{end}: quarantined xref active-claim paragraph lacks local non-instruction boundary"
                    )

        files.append({
            "path": rel,
            "source_id_count": len(cited_file),
            "source_ids": cited_file,
            "occurrence_count": sum(len(o["source_ids"]) for o in occurrences),
            "has_marker": has_marker,
            "has_official_route_heading": has_official_route_heading,
            "occurrences": occurrences,
        })

    return {
        "archive_version": VERSION,
        "synthetic_only": True,
        "quarantined_source_count": len(quarantined),
        "scanned_roots": list(SCAN_ROOTS),
        "file_count": len(files),
        "occurrence_count": occurrence_count,
        "risky_paragraph_error_count": risky_paragraph_count,
        "error_count": len(errors),
        "boundary": "Quarantined state/local source xrefs are example official routes only; they are not current voter instruction, legal authority, current-law advice, or adopter-approved public guidance without a valid adopter capture record.",
        "files": files,
        "errors": errors,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write deterministic firewall report")
    ap.add_argument("--json", action="store_true", help="print generated report JSON")
    args = ap.parse_args()

    generated = build_report()
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(generated, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(generated, sort_keys=True, separators=(",", ":")))
        return 0 if generated["error_count"] == 0 else 2

    errors = list(generated.get("errors") or [])
    if not REPORT.exists():
        errors.append(f"missing generated report: {REPORT.relative_to(ROOT)}")
    else:
        shipped = json.loads(REPORT.read_text(encoding="utf-8"))
        if shipped != generated:
            errors.append("quarantined-source public-surface firewall report is stale; run scripts/check_quarantined_source_public_surface_firewall.py --write")
    if int(generated.get("quarantined_source_count") or 0) < 70:
        errors.append("expected at least 70 quarantined state/local rows")
    if int(generated.get("file_count") or 0) < 20:
        errors.append("expected at least 20 public-surface docs containing quarantined route examples")

    if errors:
        print(f"FAIL: quarantined source public-surface firewall found {len(errors)} issue(s)", file=sys.stderr)
        for e in errors[:120]:
            print("ERROR:", e, file=sys.stderr)
        return 2
    print(
        "PASS: quarantined source public-surface firewall "
        f"({VERSION}, files={generated['file_count']}, refs={generated['occurrence_count']}, quarantined={generated['quarantined_source_count']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
