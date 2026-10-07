#!/usr/bin/env python3
"""Guard that compiled publication artifacts are not silently shipped.

The archive carries source and evidence surfaces, not built PDFs or release zips
inside the repo tree.  Compile witnesses may record PDF digests; this checker
verifies that those digest-bearing PDF outputs remain quarantined outside the
shipped datacube unless a future publication receipt explicitly changes policy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

ZIP_NAME_RE = re.compile(r"^Anonymity-rev\d{4}-.+\.zip(?:\.sha256)?$")
DISALLOWED_BUILD_SUFFIXES = (
    ".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".synctex.gz",
    ".bbl", ".blg", ".bcf", ".run.xml", ".toc", ".lof", ".lot",
)
PDF_OUTPUT_NAME_RE = re.compile(r"(^|/)(paper|compiled|output|freeze|publication)(?:[-_.].*)?\.pdf$", re.IGNORECASE)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compile_pdf_digests(root: pathlib.Path) -> set[str]:
    digests: set[str] = set()
    witness_path = root / "release_queue" / "FREEZE_COMPILE_WITNESS.json"
    if witness_path.exists():
        try:
            witness = load_json(witness_path)
            report = witness.get("preflight_report", {}) if isinstance(witness, dict) else {}
            details = report.get("details", {}) if isinstance(report, dict) else {}
            compile_details = details.get("compile", {}) if isinstance(details, dict) else {}
            digest = compile_details.get("output_pdf_sha256")
            if isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest):
                digests.add(digest)
        except Exception:
            pass
    for snapshot in sorted((root / "release_queue" / "freeze_packets").glob("*/FREEZE_COMPILE_WITNESS.snapshot.json")):
        try:
            data = load_json(snapshot)
            report = data.get("preflight_report", {}) if isinstance(data, dict) else {}
            details = report.get("details", {}) if isinstance(report, dict) else {}
            compile_details = details.get("compile", {}) if isinstance(details, dict) else {}
            digest = compile_details.get("output_pdf_sha256")
            if isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest):
                digests.add(digest)
        except Exception:
            pass
    return digests


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    findings: list[dict[str, Any]] = []
    compile_digests = compile_pdf_digests(root)
    shipped_digest_hits: list[dict[str, Any]] = []

    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        name = path.name
        category = ""
        if ZIP_NAME_RE.match(name):
            category = "release_zip_inside_repo_tree"
        elif name.endswith(DISALLOWED_BUILD_SUFFIXES):
            category = "latex_build_byproduct"
        elif rel.startswith("series/") and name.endswith(".pdf"):
            category = "compiled_series_pdf"
        elif rel.startswith("release_queue/") and name.endswith(".pdf"):
            category = "freeze_or_evidence_pdf_inside_release_queue"
        elif rel.startswith("published/") and PDF_OUTPUT_NAME_RE.search(rel):
            category = "compiled_publication_pdf_without_receipt_policy"
        elif rel.startswith("build/"):
            category = "build_tree_file_inside_archive"
        if category:
            findings.append({"path": rel, "category": category})

        if compile_digests and path.stat().st_size > 0:
            digest = sha256_file(path)
            if digest in compile_digests:
                shipped_digest_hits.append({"path": rel, "sha256": digest})

    failures: list[dict[str, Any]] = []
    if findings:
        failures.append({"category": "disallowed_artifact_paths", "count": len(findings), "findings": findings[:50]})
    if shipped_digest_hits:
        failures.append({"category": "compile_output_digest_shipped", "count": len(shipped_digest_hits), "hits": shipped_digest_hits[:50]})

    categories: dict[str, int] = {}
    for finding in findings:
        categories[finding["category"]] = categories.get(finding["category"], 0) + 1

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "quarantine_policy": "source_and_evidence_only_no_silent_compiled_outputs",
        "compile_output_pdf_digests": sorted(compile_digests),
        "findings": findings,
        "shipped_compile_output_digest_hits": shipped_digest_hits,
        "summary": {
            "checks_failed": len(failures),
            "disallowed_artifact_count": len(findings),
            "category_counts": categories,
            "compile_output_pdf_digest_count": len(compile_digests),
            "shipped_compile_output_digest_hit_count": len(shipped_digest_hits),
        },
        "failures": failures[:50],
        "fail_closed_rule": "If compiled PDFs, release zips, build byproducts, or a recorded compile-output digest appear inside the shipped repo tree, default to no publication and remove or explicitly receipt the artifact.",
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
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
