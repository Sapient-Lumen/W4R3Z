#!/usr/bin/env python3
"""Report artifact-index coverage and release-gate first-failure risk."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = DOCS / "13-artifact-index.md"
NUMBERED_RE = re.compile(r"^\d{1,3}[-_].*\.md$")


def is_tombstone(path: Path) -> bool:
    return "tombstone" in path.read_text(encoding="utf-8", errors="ignore")[:200].lower()


def canonical_docs() -> list[Path]:
    return sorted(p for p in DOCS.glob("*.md") if NUMBERED_RE.match(p.name) and not is_tombstone(p))


def build_report() -> dict[str, object]:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    text = INDEX.read_text(encoding="utf-8", errors="ignore") if INDEX.exists() else ""
    docs = canonical_docs()
    missing = [p.name for p in docs if p.name not in text]
    duplicate_headers = text.count("# Artifact index")
    generated_marker = "scripts/gen_artifact_index.py" in text
    return {
        "archive_version": version,
        "index_path": "docs/13-artifact-index.md",
        "canonical_numbered_doc_count": len(docs),
        "missing_count": len(missing),
        "missing": missing[:100],
        "generated_marker_present": generated_marker,
        "artifact_index_header_count": duplicate_headers,
        "release_gate_first_step_risk": "cleared" if len(missing) == 0 and generated_marker and duplicate_headers == 1 else "at_risk",
        "boundary": "Artifact-index coverage audit only; not legal advice, current voter instruction, certification, live-pilot authorization, or production signer authority.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--rev", default=None)
    args = ap.parse_args()
    report = build_report()
    if args.write:
        rev = args.rev or str(report["archive_version"]).removeprefix("v")
        out_json = ROOT / "artifacts" / "reports" / f"artifact-index-surface-rev{rev}.json"
        out_csv = ROOT / "artifacts" / "reports" / f"artifact-index-surface-rev{rev}.csv"
        out_md = ROOT / "artifacts" / "reports" / f"artifact-index-release-gate-audit-rev{rev}.md"
        out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["metric", "value"])
            w.writeheader()
            for k, v in report.items():
                if isinstance(v, list):
                    v = ";".join(str(x) for x in v)
                w.writerow({"metric": k, "value": v})
        out_md.write_text(
            "# Artifact-index release-gate audit\n\n"
            f"Archive version: `{report['archive_version']}`\n\n"
            f"Canonical numbered docs: `{report['canonical_numbered_doc_count']}`\n\n"
            f"Missing from `docs/13-artifact-index.md`: `{report['missing_count']}`\n\n"
            f"Generated marker present: `{str(report['generated_marker_present']).lower()}`\n\n"
            f"Header count: `{report['artifact_index_header_count']}`\n\n"
            f"Release-gate first-step risk: `{report['release_gate_first_step_risk']}`\n\n"
            "This audit exists because rev0854's one-command release gate failed before reaching verifier or packaging checks: the artifact index had been collapsed to a small current-head note. The fix is to make the index generated and to run the generator before `scripts/check_index.py`.\n\n"
            f"Boundary: {report['boundary']}\n",
            encoding="utf-8",
        )
        print(out_json.relative_to(ROOT).as_posix())
        print(out_csv.relative_to(ROOT).as_posix())
        print(out_md.relative_to(ROOT).as_posix())
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if int(report["missing_count"]) == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
