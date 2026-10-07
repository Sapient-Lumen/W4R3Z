#!/usr/bin/env python3
"""Fail closed if obvious credential or private-key material is shipped."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from typing import Any

TEXT_SUFFIXES = {
    ".cff",
    ".csv",
    ".json",
    ".jsonl",
    ".key",
    ".md",
    ".pem",
    ".paths",
    ".py",
    ".sha256",
    ".asc",
    ".tex",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {"LICENSE", "Makefile", "NOTICE", "VERSION"}

# Keep marker fragments split so the checker does not create its own finding.
PRIVATE_KEY_BEGIN = "-----BEGIN "
PRIVATE_KEY_END = " PRIVATE KEY-----"
PGP_PRIVATE_BEGIN = "-----BEGIN PGP " + "PRIVATE KEY BLOCK-----"

REGEX_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_access_key_id", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,}\b")),
    ("openai_style_api_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("anthropic_style_api_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("stripe_secret_or_restricted_key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("jwt_like_token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_text_surface(path: pathlib.Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES


def line_excerpt(line: str) -> str:
    cleaned = " ".join(line.strip().split())
    if len(cleaned) <= 80:
        return cleaned
    return cleaned[:77] + "..."


def line_findings(rel: str, line_no: int, line: str) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if PRIVATE_KEY_BEGIN in line and PRIVATE_KEY_END in line:
        found.append({"path": rel, "line": line_no, "category": "pem_private_key_marker", "excerpt": line_excerpt(line)})
    if PGP_PRIVATE_BEGIN in line:
        found.append({"path": rel, "line": line_no, "category": "pgp_private_key_marker", "excerpt": line_excerpt(line)})
    for name, pattern in REGEX_PATTERNS:
        if pattern.search(line):
            found.append({"path": rel, "line": line_no, "category": name, "excerpt": "redacted token-like match"})
    return found


def detector_negative_controls() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    controls = [
        {
            "name": "pem_private_key_marker_in_pem_surface",
            "path": "synthetic/private.pem",
            "line": PRIVATE_KEY_BEGIN + "OPENSSH" + PRIVATE_KEY_END,
            "expected_category": "pem_private_key_marker",
        },
        {
            "name": "pgp_private_key_marker",
            "path": "synthetic/private.asc",
            "line": PGP_PRIVATE_BEGIN,
            "expected_category": "pgp_private_key_marker",
        },
        {
            "name": "public_key_not_private",
            "path": "synthetic/public.pem",
            "line": "-----BEGIN PUBLIC KEY-----",
            "expected_category": "none",
        },
    ]
    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for control in controls:
        detected = line_findings(str(control["path"]), 1, str(control["line"]))
        categories = sorted({str(item["category"]) for item in detected})
        expected = str(control["expected_category"])
        ok = (not categories) if expected == "none" else expected in categories
        row = {
            "name": control["name"],
            "status": "pass" if ok else "fail",
            "expected_category": expected,
            "detected_categories": categories,
        }
        if not ok:
            failures.append({"category": "secret_detector_negative_control_failed", **row})
        rows.append(row)
    return rows, failures


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    findings: list[dict[str, Any]] = []
    text_count = 0
    pattern_counts = {name: 0 for name, _ in REGEX_PATTERNS}
    marker_counts = {"pem_private_key_marker": 0, "pgp_private_key_marker": 0}

    for path in sorted((p for p in root.rglob("*") if p.is_file() and is_text_surface(p)), key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            # Text validity is enforced by check_text_surface_normalization.py.
            continue
        text_count += 1
        for line_no, line in enumerate(text.splitlines(), start=1):
            for finding in line_findings(rel, line_no, line):
                category = str(finding["category"])
                if category in marker_counts:
                    marker_counts[category] += 1
                elif category in pattern_counts:
                    pattern_counts[category] += 1
                findings.append(finding)

    negative_controls, negative_control_failures = detector_negative_controls()
    findings.extend(negative_control_failures)

    category_counts: dict[str, int] = {}
    for item in findings:
        category = str(item["category"])
        category_counts[category] = category_counts.get(category, 0) + 1

    summary = {
        "checks_failed": len(findings),
        "text_surface_count": text_count,
        "finding_count": len(findings),
        "private_key_marker_count": sum(marker_counts.values()),
        "token_like_pattern_count": sum(pattern_counts.values()),
        "category_counts": category_counts,
        "secret_detector_negative_control_count": len(negative_controls),
        "secret_detector_negative_control_failed_count": len(negative_control_failures),
    }
    return {
        "status": "pass" if not findings else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_root": ".",
        "policy": {
            "scope": "UTF-8 text surfaces including .pem/.key/.asc signing surfaces; binary classification is handled by archive-entry and artifact-quarantine checks.",
            "redaction": "Token-like matches are reported by path, line, and category without echoing matched secret text.",
            "patterns": [name for name, _ in REGEX_PATTERNS] + sorted(marker_counts),
        },
        "findings": findings[:100],
        "secret_detector_negative_controls": negative_controls,
        "summary": summary,
        "fail_closed_rule": "If secret-like material is found, default to no publication and remove or quarantine the affected payload before packaging.",
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
