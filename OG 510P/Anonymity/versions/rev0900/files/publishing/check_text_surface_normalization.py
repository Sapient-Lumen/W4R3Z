#!/usr/bin/env python3
"""Check text-surface encoding and line-ending portability.

The path guard proves names are portable.  This companion guard proves shipped
text surfaces are UTF-8, LF-normalized, contain no NUL bytes, and end with a
final line feed.  Passing reports are warning-free so text drift cannot hide in
operator-only diagnostics.
"""

from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any

TEXT_SUFFIXES = {
    ".cff",
    ".csv",
    ".json",
    ".jsonl",
    ".md",
    ".paths",
    ".py",
    ".sha256",
    ".tex",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {"LICENSE", "Makefile", "NOTICE", "VERSION"}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def is_text_surface(path: pathlib.Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    text_count = 0
    total_bytes = 0
    largest_text_surface = {"path": "", "bytes": 0}

    for path in sorted((p for p in root.rglob("*") if p.is_file() and is_text_surface(p)), key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        text_count += 1
        data = path.read_bytes()
        total_bytes += len(data)
        if len(data) > largest_text_surface["bytes"]:
            largest_text_surface = {"path": rel, "bytes": len(data)}
        if b"\x00" in data:
            failures.append({"path": rel, "category": "nul_byte_present"})
        if b"\r" in data:
            failures.append({"path": rel, "category": "carriage_return_present"})
        try:
            data.decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append({"path": rel, "category": "utf8_decode_failed", "detail": str(exc)})
        if data and not data.endswith(b"\n"):
            failures.append({"path": rel, "category": "missing_final_lf"})

    summary = {
        "checks_failed": len(failures),
        "text_surface_count": text_count,
        "text_surface_total_bytes": total_bytes,
        "nul_byte_failure_count": sum(1 for row in failures if row["category"] == "nul_byte_present"),
        "carriage_return_failure_count": sum(1 for row in failures if row["category"] == "carriage_return_present"),
        "utf8_failure_count": sum(1 for row in failures if row["category"] == "utf8_decode_failed"),
        "missing_final_lf_failure_count": sum(1 for row in failures if row["category"] == "missing_final_lf"),
        "warning_count": len(warnings),
        "missing_final_lf_warning_count": 0,
        "largest_text_surface": largest_text_surface,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "text_policy": {
            "required_encoding": "UTF-8",
            "forbidden_bytes": ["NUL", "CR"],
            "line_ending": "LF",
            "final_line_feed_required": True,
            "missing_final_lf_is_warning": False,
        },
        "text_suffixes": sorted(TEXT_SUFFIXES),
        "text_names": sorted(TEXT_NAMES),
        "failures": failures[:100],
        "warnings": warnings[:100],
        "summary": summary,
        "fail_closed_rule": "If text surfaces are not UTF-8, contain CR/NUL bytes, or lack a final LF, default to no publication and normalize the affected files before packaging.",
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
