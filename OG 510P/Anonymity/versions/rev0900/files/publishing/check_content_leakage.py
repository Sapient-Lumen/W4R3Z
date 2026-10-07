#!/usr/bin/env python3
"""Scan shipped text surfaces for local environment path leakage.

Path portability checks filenames. This guard checks file *contents* for build
workspace paths, user home paths, sandbox URLs, and platform-specific absolute
paths that should not become part of a portable research-object bundle.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys
from typing import Any

TEXT_SUFFIXES = {
    ".json",
    ".jsonl", ".md", ".tex", ".py", ".txt", ".cff", ".sha256", ".paths", ".bib",
    ".sty", ".cls", ".yml", ".yaml", ".csv", ".tsv", ".log"
}
TEXT_BASENAMES = {"VERSION", "LICENSE", "NOTICE", "Makefile"}
PATTERNS = [
    ("container_mnt_data_path", re.compile(r"/mnt/data(?:/|\b)")),
    ("container_home_path", re.compile(r"(?<![A-Za-z0-9_~.-])/home/(?:oai|sandbox|runner|ubuntu|[^\s`'\"]+)(?:/|\b)")),
    ("tmp_absolute_path", re.compile(r"(?<![A-Za-z0-9_])/(?:tmp|var/tmp)(?:/|\b)")),
    ("mac_private_tmp_path", re.compile(r"/private/var/")),
    ("windows_user_path", re.compile(r"[A-Za-z]:\\\\Users\\\\")),
    ("windows_temp_path", re.compile(r"[A-Za-z]:\\\\(?:Temp|Windows\\\\Temp)\\\\", re.IGNORECASE)),
    ("sandbox_uri", re.compile(r"sandbox:/")),
    ("file_uri_absolute", re.compile(r"file:///(?:Users|home|mnt|tmp|var)/")),
]
EXCLUDED_PATHS = {"reports/content_leakage.json"}

ALLOWLIST: set[tuple[str, str]] = {
    # The checker necessarily names the patterns it is responsible for detecting.
    ("publishing/check_content_leakage.py", "container_mnt_data_path"),
    ("publishing/check_content_leakage.py", "container_home_path"),
    ("publishing/check_content_leakage.py", "tmp_absolute_path"),
    ("publishing/check_content_leakage.py", "mac_private_tmp_path"),
    ("publishing/check_content_leakage.py", "windows_user_path"),
    ("publishing/check_content_leakage.py", "windows_temp_path"),
    ("publishing/check_content_leakage.py", "sandbox_uri"),
    ("publishing/check_content_leakage.py", "file_uri_absolute"),
}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_text_candidate(path: pathlib.Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_BASENAMES


def scan_file(root: pathlib.Path, path: pathlib.Path) -> list[dict[str, Any]]:
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return []
    findings: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for name, pattern in PATTERNS:
            if (rel, name) in ALLOWLIST:
                continue
            match = pattern.search(line)
            if match:
                findings.append({
                    "path": rel,
                    "line": line_no,
                    "pattern": name,
                    "match": match.group(0),
                    "context": line.strip()[:220],
                })
    return findings


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    scanned = []
    findings: list[dict[str, Any]] = []
    skipped_binary = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel in EXCLUDED_PATHS:
            continue
        if not is_text_candidate(path):
            skipped_binary += 1
            continue
        scanned.append(rel)
        findings.extend(scan_file(root, path))
    counts = collections.Counter(f["pattern"] for f in findings)
    return {
        "status": "pass" if not findings else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "policy": {
            "purpose": "prevent local build/workspace paths and sandbox links from leaking into portable shipped content",
            "pattern_names": [name for name, _ in PATTERNS],
            "text_suffixes": sorted(TEXT_SUFFIXES),
            "text_basenames": sorted(TEXT_BASENAMES),
        },
        "summary": {
            "text_file_count": len(scanned),
            "non_text_file_count": skipped_binary,
            "finding_count": len(findings),
            "finding_pattern_counts": dict(sorted(counts.items())),
            "checks_failed": len(findings),
        },
        "findings": findings[:200],
        "fail_closed_rule": "If local environment paths appear in shipped text, default to no publication and scrub or explicitly justify the surface.",
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
