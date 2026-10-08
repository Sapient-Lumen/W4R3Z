#!/usr/bin/env python3
"""Report numbered-doc Track header coverage.

This complements scripts/check_tracks.py with a machine-readable release audit so
track-header failures are not rediscovered only by a long release-gate run.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
VERSION_NUM = VERSION.removeprefix("v").zfill(4)
DOCS = ROOT / "docs"
TRACK_RE = re.compile(r"^\*\*Track:\*\*\s*(.+)$", re.IGNORECASE | re.MULTILINE)
NUMBERED_RE = re.compile(r"^\d{1,3}[-_].*\.md$")
ALLOWED_MARKERS = ("A", "B", "C", "Shared")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def numbered_docs() -> list[Path]:
    return sorted(p for p in DOCS.glob("*.md") if NUMBERED_RE.match(p.name))


def classify(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = TRACK_RE.search(text[:4000])
    if not match:
        return {
            "path": rel(path),
            "track_header_present": "false",
            "track_label": "",
            "track_header_valid": "false",
            "problem": "missing_track_header",
        }
    label = match.group(1).strip()
    valid = any(marker in label for marker in ALLOWED_MARKERS)
    return {
        "path": rel(path),
        "track_header_present": "true",
        "track_label": label,
        "track_header_valid": "true" if valid else "false",
        "problem": "" if valid else "unrecognized_track_label",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=f"artifacts/reports/track-header-surface-rev{VERSION_NUM}.csv")
    ap.add_argument("--json", default=f"artifacts/reports/track-header-surface-rev{VERSION_NUM}.json")
    ap.add_argument("--md", default=f"artifacts/reports/track-header-surface-audit-rev{VERSION_NUM}.md")
    args = ap.parse_args()

    rows = [classify(p) for p in numbered_docs()]
    failures = [r for r in rows if r["track_header_valid"] != "true"]
    summary = {
        "archive_version": VERSION,
        "numbered_doc_count": len(rows),
        "missing_track_header_count": sum(1 for r in rows if r["problem"] == "missing_track_header"),
        "invalid_track_label_count": sum(1 for r in rows if r["problem"] == "unrecognized_track_label"),
        "failure_count": len(failures),
        "generated_index_has_track_header": any(r["path"] == "docs/13-artifact-index.md" and r["track_header_valid"] == "true" for r in rows),
        "release_gate_control": "scripts/check_tracks.py",
        "non_claims": [
            "track_headers_are_navigation_and_release_gate_metadata_only",
            "track_header_repair_does_not_change_verifier_cryptographic_semantics",
            "track_header_repair_is_not_live_pilot_authorization_or_certification",
        ],
    }

    csv_path = ROOT / args.csv
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["path", "track_header_present", "track_label", "track_header_valid", "problem"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        # Keep the release artifact size-bounded: the JSON summary records total counts,
        # while the CSV carries actionable failure rows instead of repeating every numbered doc.
        writer.writerows(failures)

    json_path = ROOT / args.json
    json_path.write_text(json.dumps({"summary": summary, "failures": failures}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md_path = ROOT / args.md
    md_lines = [
        "# Track-header surface audit",
        "",
        "**Track:** Shared (Release engineering and gate reliability)",
        f"**Status:** generated rev{VERSION_NUM} release-gate audit",
        "",
        f"Archive version: `{summary['archive_version']}`",
        "",
        "This audit exists because a numbered-doc navigation invariant is easy to break while adding urgent verifier/source changes. It is a release-gate surface only; it is not certification, legal advice, current voter instruction, production signer authority, or live-pilot evidence.",
        "",
        "## Result",
        "",
        f"- `numbered_doc_count`: `{summary['numbered_doc_count']}`",
        f"- `missing_track_header_count`: `{summary['missing_track_header_count']}`",
        f"- `invalid_track_label_count`: `{summary['invalid_track_label_count']}`",
        f"- `failure_count`: `{summary['failure_count']}`",
        f"- `generated_index_has_track_header`: `{str(summary['generated_index_has_track_header']).lower()}`",
        "",
        "## Gate",
        "",
        "`scripts/check_tracks.py` must pass before release packaging. `scripts/gen_artifact_index.py` must keep `docs/13-artifact-index.md` inside the same numbered-doc track invariant.",
        "",
    ]
    if failures:
        md_lines.append("## Failures")
        md_lines.append("")
        for row in failures[:50]:
            md_lines.append(f"- `{row['path']}`: `{row['problem']}`")
        md_lines.append("")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(json.dumps(summary, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
