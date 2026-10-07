#!/usr/bin/env python3
"""Verify that the manual publication-decision template names all hard gates."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
from typing import Any

REQUIRED_FRAGMENTS = [
    "Publication action: publish",
    "Publication date: YYYY.MM.DD",
    "Source: series/.../paper.tex",
    "Source SHA-256: <64 lowercase hex>",
    "Published name: YYYY-MM-DD_slug_title",
    "Published path: published/YYYY-MM-DD_slug_title",
    "Evidence pack manifest: release_queue/evidence_packs/<id>/EVIDENCE_PACK_MANIFEST.json",
    "Compile witness: release_queue/FREEZE_COMPILE_WITNESS.json",
    "Freeze packet manifest: release_queue/freeze_packets/<id>/FREEZE_PACKET_MANIFEST.json",
    "Unicode/control hygiene: reports/unicode_control_hygiene.json must pass for the current revision",
    "Queue note: release_queue/published_ready/<id>.md",
    "Public citation-head update: required",
    "Publication receipt: required after guarded helper execution",
    "Publication authorized by this completed note: true",
    "python3 -B publishing/create_published_entry.py",
]

PLACEHOLDER_RE = re.compile(r"<[^>]+>|YYYY\.MM\.DD|YYYY-MM-DD_slug_title|series/\.\.\./paper\.tex")


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    path = root / "release_queue" / "PUBLICATION_DECISION_TEMPLATE.md"
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    text = ""
    if not path.exists():
        failures.append({"category": "template_missing", "path": "release_queue/PUBLICATION_DECISION_TEMPLATE.md"})
    else:
        text = path.read_text(encoding="utf-8", errors="replace")
        for fragment in REQUIRED_FRAGMENTS:
            if fragment not in text:
                failures.append({"category": "required_fragment_missing", "fragment": fragment})
        if "non-authorizing" not in text.lower() and "does not publish" not in text.lower():
            failures.append({"category": "template_missing_non_authorization_notice"})
        placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
        if not placeholders:
            warnings.append({"category": "template_has_no_placeholders", "detail": "A reusable template is expected to contain placeholders; completed decisions belong in release_queue/decisions/."})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "template_path": "release_queue/PUBLICATION_DECISION_TEMPLATE.md",
        "required_fragment_count": len(REQUIRED_FRAGMENTS),
        "warnings": warnings,
        "failures": failures,
        "summary": {
            "checks_failed": len(failures),
            "required_fragments_present": len(REQUIRED_FRAGMENTS) - sum(1 for f in failures if f.get("category") == "required_fragment_missing"),
            "placeholder_count": len(sorted(set(PLACEHOLDER_RE.findall(text)))) if text else 0,
        },
        "fail_closed_rule": "If the decision template is incomplete, do not treat a manual publish note as sufficient until it names the source, hash, evidence, compile, freeze packet, citation-head update, and receipt obligations.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
