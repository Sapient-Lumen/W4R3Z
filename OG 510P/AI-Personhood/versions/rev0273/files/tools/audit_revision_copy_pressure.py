#!/usr/bin/env python3
"""Measure revision-copy pressure without treating history as an error.

The metric is deliberately heuristic. It normalizes revision tokens, release
timestamps, ISO timestamps, and standalone SHA-256 values, then measures bytes
in duplicate normalized-content families beyond one retained representative.
It is meant to expose copy-forward maintenance pressure, not to authorize
history deletion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REPORT = ROOT / "examples" / f"revision-copy-pressure-report-{REV}.json"
EXCLUDED_NAMES = {
    "MANIFEST.sha256",
    "RELEASE-MANIFEST.json",
    "context-pack.json",
    "ARCHIVE_INDEX.md",
}
REPORT_RE = re.compile(r"revision-copy-pressure-report-rev\d{4}\.json$")
REV_RE = re.compile(r"(?i)rev\d{4}")
ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z")
STAMP_RE = re.compile(r"\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2}")
SHA_RE = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")
PATH_REV_RE = re.compile(r"rev\d{4}")


def normalized_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw
    text = REV_RE.sub("revXXXX", text)
    text = ISO_RE.sub("TIMESTAMP", text)
    text = STAMP_RE.sub("FILESTAMP", text)
    text = SHA_RE.sub("SHA256", text)
    return text.encode("utf-8")


def scan_paths() -> list[Path]:
    paths = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or ".git" in path.parts:
            continue
        if path.name in EXCLUDED_NAMES or REPORT_RE.search(path.name):
            continue
        paths.append(path)
    return sorted(paths)


def compute() -> dict:
    paths = scan_paths()
    groups: dict[str, list[Path]] = defaultdict(list)
    total_bytes = 0
    revision_stamped = 0
    for path in paths:
        size = path.stat().st_size
        total_bytes += size
        rel = path.relative_to(ROOT).as_posix()
        if PATH_REV_RE.search(rel):
            revision_stamped += 1
        digest = hashlib.sha256(normalized_bytes(path)).hexdigest()
        groups[digest].append(path)

    duplicates = [group for group in groups.values() if len(group) > 1]
    duplicate_files = sum(len(group) for group in duplicates)
    redundant_bytes = sum(
        sum(path.stat().st_size for path in group) - max(path.stat().st_size for path in group)
        for group in duplicates
    )
    ratio = redundant_bytes / total_bytes if total_bytes else 0.0
    top_groups = []
    for group in sorted(
        duplicates,
        key=lambda g: sum(p.stat().st_size for p in g) - max(p.stat().st_size for p in g),
        reverse=True,
    )[:12]:
        top_groups.append(
            {
                "member_count": len(group),
                "redundant_bytes": sum(p.stat().st_size for p in group) - max(p.stat().st_size for p in group),
                "representative_paths": [p.relative_to(ROOT).as_posix() for p in group[:6]],
            }
        )
    return {
        "scan_scope": {
            "regular_files": len(paths),
            "total_bytes": total_bytes,
            "excluded_volatile_names": sorted(EXCLUDED_NAMES),
            "revision_copy_reports_excluded": True,
        },
        "observed": {
            "revision_stamped_files": revision_stamped,
            "revision_stamped_file_share": round(revision_stamped / len(paths), 6) if paths else 0.0,
            "normalized_duplicate_families": len(duplicates),
            "files_in_normalized_duplicate_families": duplicate_files,
            "normalized_redundant_bytes": redundant_bytes,
            "normalized_redundancy_ratio": round(ratio, 6),
        },
        "largest_duplicate_families": top_groups,
    }


def build_report(created_at: str) -> dict:
    result = compute()
    ratio = result["observed"]["normalized_redundancy_ratio"]
    hard_ceiling = 0.36
    result.update(
        {
            "report_id": f"RCPR-2026-{REV}",
            "created_at": created_at,
            "revision": REV,
            "method": "Normalize revNNNN tokens, ISO/release timestamps, and standalone SHA-256 values; group by normalized content hash; count bytes beyond the largest member of each duplicate family as copy pressure.",
            "intake_baseline_all_files": {
                "files": 3294,
                "bytes": 40076552,
                "normalized_duplicate_families": 189,
                "files_in_normalized_duplicate_families": 1532,
                "normalized_redundant_bytes": 13160833,
                "normalized_redundancy_ratio": 0.328392,
                "note": "Baseline includes volatile release files and cache artifacts from the received rev0262 bundle; current scan excludes volatile generated outputs, so trend comparisons are directional rather than accounting identity.",
            },
            "policy": {
                "hard_ceiling_ratio": hard_ceiling,
                "migration_target_ratio": 0.20,
                "new_versioned_copy_only_when_content_changes": True,
                "history_may_not_be_deleted_from_this_metric_alone": True,
                "recommended_architecture": "immutable release history plus stable current canonical paths and hash-addressed reuse of unchanged objects",
            },
            "decision": {
                "within_hard_ceiling": ratio <= hard_ceiling,
                "migration_required": ratio > 0.20,
                "reason": "Copy pressure is bounded for this release but remains high enough to require a stable-current/hash-reuse migration." if ratio <= hard_ceiling else "Normalized revision-copy pressure exceeded the release ceiling.",
            },
            "no_live_floor_effect": True,
        }
    )
    # Put stable identity fields first for readability.
    order = [
        "report_id", "created_at", "revision", "method", "scan_scope", "intake_baseline_all_files",
        "observed", "policy", "largest_duplicate_families", "decision", "no_live_floor_effect",
    ]
    return {key: result[key] for key in order}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--created-at", default="2026-06-18T08:27:00Z")
    args = parser.parse_args()
    if args.write:
        report = build_report(args.created_at)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(REPORT.relative_to(ROOT))
        return
    if not REPORT.exists():
        raise SystemExit(f"missing copy-pressure report: {REPORT.relative_to(ROOT)}")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report.get("revision") != REV or report.get("no_live_floor_effect") is not True:
        raise SystemExit("copy-pressure report revision/no-floor mismatch")
    fresh = compute()
    for key in ["scan_scope", "observed", "largest_duplicate_families"]:
        if report.get(key) != fresh.get(key):
            raise SystemExit(f"copy-pressure report stale at {key}; rerun with --write")
    ceiling = report.get("policy", {}).get("hard_ceiling_ratio")
    ratio = report.get("observed", {}).get("normalized_redundancy_ratio")
    if not isinstance(ceiling, (int, float)) or not isinstance(ratio, (int, float)) or ratio > ceiling:
        raise SystemExit(f"normalized revision-copy pressure exceeds ceiling: ratio={ratio} ceiling={ceiling}")
    if report.get("decision", {}).get("within_hard_ceiling") is not True:
        raise SystemExit("copy-pressure decision is not within hard ceiling")
    print("audit_revision_copy_pressure: OK " + json.dumps(report["observed"], sort_keys=True))


if __name__ == "__main__":
    main()
