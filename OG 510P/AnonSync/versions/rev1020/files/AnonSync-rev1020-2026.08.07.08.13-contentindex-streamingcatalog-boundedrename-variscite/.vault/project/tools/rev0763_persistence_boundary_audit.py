#!/usr/bin/env python3
"""Active-tree inventory for persistence-boundary bypasses.

This is deliberately a conservative lexical inventory, not a C++ parser and
not a substitute for the invariant-specific audits.  Historical revision
artifacts are immutable evidence, so they are reported by package inventory
rather than reclassified as active production code.  ``--enforce`` fails only
when a raw sqlite3_column_* extraction occurs in current production source
outside the exact scalar owner.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".inl", ".sql"}
ACTIVE_ROOTS = ("src", "include", "tests", "fuzz")
PRODUCTION_ROOTS = ("src/", "include/")
RULES = {
    "sqlite_column_extract": re.compile(
        r"\bsqlite3_column_(?:blob|bytes|double|int|int64|text|type|value)\s*\("
    ),
    "schema_version": re.compile(
        r"\b(?:PRAGMA\s+user_version|user_version|schema_version|kSchemaVersion)\b",
        re.I,
    ),
    "schema_ddl": re.compile(
        r"\b(?:CREATE|ALTER|DROP)\s+(?:TABLE|INDEX|TRIGGER)\b", re.I
    ),
    "transaction_boundary": re.compile(
        r"\b(?:BEGIN|COMMIT|ROLLBACK|SAVEPOINT|RELEASE)\b", re.I
    ),
    "claim_tuple": re.compile(
        r"\b(?:claim|lease).{0,80}\b(?:worker|token|generation|epoch)\b", re.I
    ),
    "canonical_decode": re.compile(
        r"\bcanonical.{0,50}(?:decode|parse|verify)|"
        r"(?:decode|parse|verify).{0,50}\bcanonical\b",
        re.I,
    ),
    "possible_sensitive_log": re.compile(
        r"\b(?:LOG|TRACE|DEBUG|INFO|WARN|ERROR|printf|fprintf|cerr|clog)"
        r".{0,160}\b(?:peer|path|payload|envelope)\b",
        re.I,
    ),
}
ALLOW_SQLITE_EXTRACT = {"src/persistence/sqlite_exact_value.cpp"}


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    line: int
    excerpt: str


def code_only(text: str) -> str:
    """Replace C/C++ comments and literals with spaces, preserving newlines."""
    out: list[str] = []
    index = 0
    state = "code"
    quote = ""
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and following == "/":
                out.extend("  ")
                index += 2
                state = "line_comment"
                continue
            if char == "/" and following == "*":
                out.extend("  ")
                index += 2
                state = "block_comment"
                continue
            if char in ('"', "'"):
                quote = char
                out.append(" ")
                index += 1
                state = "literal"
                continue
            out.append(char)
            index += 1
            continue
        if state == "line_comment":
            if char == "\n":
                out.append("\n")
                state = "code"
            else:
                out.append(" ")
            index += 1
            continue
        if state == "block_comment":
            if char == "*" and following == "/":
                out.extend("  ")
                index += 2
                state = "code"
            else:
                out.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if char == "\\" and following:
            out.append(" ")
            out.append("\n" if following == "\n" else " ")
            index += 2
            continue
        if char == quote:
            out.append(" ")
            index += 1
            state = "code"
            continue
        out.append("\n" if char == "\n" else " ")
        index += 1
    return "".join(out)


def active_source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for root_name in ACTIVE_ROOTS:
        base = root / root_name
        if not base.is_dir():
            continue
        files.extend(
            path
            for path in sorted(base.rglob("*"))
            if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES
        )
    return files


def scan(root: Path) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    files = active_source_files(root)
    for path in files:
        relative = path.relative_to(root).as_posix()
        try:
            original = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError):
            continue
        stripped = code_only(original)
        original_lines = original.splitlines()
        for rule, expression in RULES.items():
            for match in expression.finditer(stripped):
                line_number = stripped.count("\n", 0, match.start()) + 1
                excerpt = ""
                if 0 < line_number <= len(original_lines):
                    excerpt = original_lines[line_number - 1].strip()[:240]
                findings.append(Finding(rule, relative, line_number, excerpt))
    return findings, len(files)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--json", dest="json_path")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    findings, active_file_count = scan(root)
    grouped = {name: sum(item.rule == name for item in findings) for name in RULES}
    extraction_findings = [
        item for item in findings if item.rule == "sqlite_column_extract"
    ]
    production_extractions = [
        item
        for item in extraction_findings
        if item.path.startswith(PRODUCTION_ROOTS)
    ]
    bypasses = [
        item
        for item in production_extractions
        if item.path not in ALLOW_SQLITE_EXTRACT
    ]
    report = {
        "format": "anonsync-active-persistence-boundary-inventory-v2",
        "root": str(root),
        "passed": not bypasses,
        "active_roots": list(ACTIVE_ROOTS),
        "historical_evidence_scanned": False,
        "active_file_count": active_file_count,
        "rules": grouped,
        "sqlite_extraction_allowlist": sorted(ALLOW_SQLITE_EXTRACT),
        "production_direct_sqlite_extractions": len(production_extractions),
        "test_direct_sqlite_extractions": len(extraction_findings) - len(production_extractions),
        "unreviewed_direct_sqlite_extractions": len(bypasses),
        "violations": [asdict(item) for item in bypasses],
        "findings": [asdict(item) for item in findings],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json_path:
        Path(args.json_path).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 2 if args.enforce and bypasses else 0


if __name__ == "__main__":
    raise SystemExit(main())
