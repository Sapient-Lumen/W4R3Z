#!/usr/bin/env python3
"""Fail-closed audit for exact SQLite scalar extraction.

SQLite's result APIs are dynamically typed and are only valid while a statement
is positioned on SQLITE_ROW. This audit keeps raw sqlite3_column_* access inside
reviewed invariant-owned decoders and prevents convenience call sites from
reintroducing numeric coercion or C-string truncation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}
DIRECT_COLUMN_API = re.compile(
    r"(?<![A-Za-z0-9_])sqlite3_column_(?:text16|text|blob|bytes16|bytes|type|int64|int|double|value)\s*\("
)
ALLOWED_DIRECT_FILES = {
    Path("src/persistence/sqlite_exact_value.cpp"),
}
REQUIRED_FILES = (
    Path("CMakeLists.txt"),
    Path("src/persistence/sqlite_exact_value.hpp"),
    Path("src/persistence/sqlite_exact_value.cpp"),
    Path("src/persistence/sqlite_projection_decoder.cpp"),
    Path("src/sync_sqlite_support.cpp"),
    Path("src/sqlite_replay_ledger.cpp"),
    Path("src/reporting_selftests.cpp"),
    Path("tests/persistence/sqlite_exact_value_tests.cpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def code_only(text: str) -> str:
    """Replace comments and literals with spaces while preserving newlines."""
    out: list[str] = []
    i = 0
    state = "code"
    quote = ""
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if state == "code":
            if ch == "/" and nxt == "/":
                out.extend("  ")
                i += 2
                state = "line_comment"
                continue
            if ch == "/" and nxt == "*":
                out.extend("  ")
                i += 2
                state = "block_comment"
                continue
            if ch in ('"', "'"):
                quote = ch
                out.append(" ")
                i += 1
                state = "literal"
                continue
            out.append(ch)
            i += 1
            continue
        if state == "line_comment":
            if ch == "\n":
                out.append("\n")
                state = "code"
            else:
                out.append(" ")
            i += 1
            continue
        if state == "block_comment":
            if ch == "*" and nxt == "/":
                out.extend("  ")
                i += 2
                state = "code"
            else:
                out.append("\n" if ch == "\n" else " ")
                i += 1
            continue
        if state == "literal":
            if ch == "\\" and nxt:
                out.append(" ")
                out.append("\n" if nxt == "\n" else " ")
                i += 2
                continue
            if ch == quote:
                out.append(" ")
                i += 1
                state = "code"
                continue
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue
    return "".join(out)


def source_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for base in (root / "src", root / "include"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES:
                files.append(path.relative_to(root))
    return files


def direct_locations(root: Path, relative: Path) -> list[dict[str, object]]:
    path = root / relative
    original = path.read_text(encoding="utf-8", errors="strict")
    stripped = code_only(original)
    original_lines = original.splitlines()
    locations: list[dict[str, object]] = []
    for match in DIRECT_COLUMN_API.finditer(stripped):
        line_number = stripped.count("\n", 0, match.start()) + 1
        locations.append(
            {
                "path": relative.as_posix(),
                "line": line_number,
                "text": original_lines[line_number - 1].strip()[:300],
            }
        )
    return locations


def require(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, bool(condition), detail))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path, help="write deterministic JSON report")
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).is_file()]
    if missing:
        report = {
            "format": "anonsync-sqlite-scalar-extraction-audit-v1",
            "passed": False,
            "violations": [f"missing required file: {path}" for path in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    texts = {
        path: (root / path).read_text(encoding="utf-8", errors="strict")
        for path in REQUIRED_FILES
    }
    locations = {
        path: direct_locations(root, path)
        for path in source_files(root)
    }
    locations = {path: rows for path, rows in locations.items() if rows}
    unauthorized = {
        path: rows for path, rows in locations.items()
        if path not in ALLOWED_DIRECT_FILES
    }

    cmake = texts[Path("CMakeLists.txt")]
    header = texts[Path("src/persistence/sqlite_exact_value.hpp")]
    exact_cpp = texts[Path("src/persistence/sqlite_exact_value.cpp")]
    projection_cpp = texts[Path("src/persistence/sqlite_projection_decoder.cpp")]
    support_cpp = texts[Path("src/sync_sqlite_support.cpp")]
    ledger_cpp = texts[Path("src/sqlite_replay_ledger.cpp")]
    reporting_selftests_cpp = texts[Path("src/reporting_selftests.cpp")]
    selftests_cpp = ledger_cpp
    focused_test = texts[Path("tests/persistence/sqlite_exact_value_tests.cpp")]

    checks: list[Check] = []
    require(
        checks,
        not unauthorized,
        "raw_column_api_confined_to_exact_boundary",
        "no production source outside the invariant-owned exact scalar reader may call sqlite3_column_* directly",
    )
    require(
        checks,
        len(locations.get(Path("src/persistence/sqlite_exact_value.cpp"), [])) == 6,
        "exact_boundary_has_expected_six_raw_calls",
        "the general exact boundary should own type, text/blob, byte-count, and integer extraction; alternate scalar APIs remain absent",
    )
    require(
        checks,
        len(locations.get(Path("src/persistence/sqlite_projection_decoder.cpp"), [])) == 0 and
        "sqlite_exact_optional_text_or_throw" in projection_cpp and
        "sqlite_exact_optional_u64_or_throw" in projection_cpp,
        "projection_decoder_delegates_all_scalar_extraction",
        "the specialized projection decoder must own mapping semantics without reacquiring raw sqlite3_column_* authority",
    )
    for needle, check_id in (
        ("statement_not_positioned", "row_state_failure_is_typed"),
        ("wrong_storage_class", "storage_class_failure_is_typed"),
        ("byte_limit_exceeded", "byte_limit_failure_is_typed"),
        ("sqlite_exact_text_or_throw", "exact_text_api_exists"),
        ("sqlite_exact_blob_or_throw", "exact_blob_api_exists"),
        ("sqlite_exact_i64_or_throw", "exact_signed_api_exists"),
        ("sqlite_exact_u64_or_throw", "exact_unsigned_api_exists"),
        ("sqlite_exact_optional_text_or_throw", "optional_exact_text_api_exists"),
        ("sqlite_exact_optional_u64_or_throw", "optional_exact_unsigned_api_exists"),
    ):
        require(checks, needle in header, check_id, f"required exact boundary marker: {needle}")
    require(
        checks,
        "sqlite3_data_count(statement) != column_count" in exact_cpp,
        "reader_requires_current_sqlite_row",
        "all exact scalar readers must reject unstepped, exhausted, or reset statements before extraction",
    )
    require(
        checks,
        exact_cpp.find("sqlite3_column_text(statement, column)") <
        exact_cpp.find("sqlite3_column_bytes(statement, column)"),
        "text_pointer_precedes_byte_count",
        "SQLite's documented safe TEXT conversion order must remain pointer first, byte count second",
    )
    require(
        checks,
        "actual != expected" in exact_cpp and "wrong_storage_class" in exact_cpp,
        "numeric_coercion_is_rejected",
        "durable scalars must match the requested SQLite storage class before conversion",
    )
    require(
        checks,
        "sqlite_exact_text_or_throw" in support_cpp and
        "sqlite_exact_blob_or_throw" in support_cpp and
        "sqlite_exact_i64_or_throw" in support_cpp and
        "sqlite_exact_u64_or_throw" in support_cpp,
        "generic_support_delegates_to_exact_boundary",
        "generic support wrappers must not reacquire raw SQLite conversion authority",
    )
    require(
        checks,
        "sqlite_exact_i64_or_throw" in ledger_cpp and
        "sqlite_exact_text_or_throw" in ledger_cpp,
        "replay_ledger_uses_exact_scalars",
        "restart and snapshot verification must preserve TEXT bytes and reject non-INTEGER durable counts",
    )
    require(
        checks,
        "hidden NUL suffix" in selftests_cpp and
        "fractional durable row count" in selftests_cpp and
        "CAST(X'0068696464656e' AS TEXT)" in selftests_cpp and
        "line_count=2.75" in selftests_cpp,
        "integration_selftest_preserves_lossy_scalar_regressions",
        "the old NUL-truncation and REAL-to-INTEGER acceptance paths must remain executable hostile cases",
    )
    for needle, check_id in (
        ("sensitive-marker\\0hidden-suffix", "focused_test_covers_embedded_nul"),
        ("wrong_storage_class", "focused_test_covers_storage_class_rejection"),
        ("statement_not_positioned", "focused_test_covers_row_state"),
        ("byte_limit_exceeded", "focused_test_covers_byte_limit"),
        ("negative_unsigned", "focused_test_covers_negative_unsigned"),
    ):
        require(checks, needle in focused_test, check_id, f"focused exact-value test marker: {needle}")
    for needle, check_id in (
        ("add_library(anonsync_sqlite_exact_value STATIC", "exact_boundary_is_independent_library"),
        ("add_executable(anonsync_sqlite_exact_value_test", "focused_test_is_independent_executable"),
        ("add_test(NAME anonsync_sqlite_exact_value_test", "focused_test_is_registered"),
        ("anonsync_sqlite_exact_value_test", "focused_target_is_named_in_build_graph_guard"),
        ("audit_sqlite_scalar_extraction.py", "source_audit_is_registered"),
    ):
        require(checks, needle in cmake, check_id, f"required CMake marker: {needle}")
    require(
        checks,
        "sqlite3_column_text" not in support_cpp and
        "sqlite3_column_int64" not in support_cpp and
        "sqlite3_column_blob" not in support_cpp,
        "generic_support_contains_no_raw_extraction",
        "support wrappers must be pure delegators to the invariant-owned exact boundary",
    )
    require(
        checks,
        "std::string(reinterpret_cast<const char*>(sqlite3_column_text" not in
        "\n".join((support_cpp, ledger_cpp, reporting_selftests_cpp)),
        "cstring_sqlite_text_construction_is_absent",
        "known embedded-NUL-truncating construction must not return in audited call sites",
    )

    report = {
        "format": "anonsync-sqlite-scalar-extraction-audit-v1",
        "passed": all(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "metrics": {
            "production_source_files_scanned": len(source_files(root)),
            "direct_column_call_count": sum(len(rows) for rows in locations.values()),
            "exact_boundary_direct_calls": len(locations.get(Path("src/persistence/sqlite_exact_value.cpp"), [])),
            "projection_decoder_direct_calls": len(locations.get(Path("src/persistence/sqlite_projection_decoder.cpp"), [])),
            "unauthorized_direct_call_count": sum(len(rows) for rows in unauthorized.values()),
        },
        "direct_call_locations": {
            path.as_posix(): rows for path, rows in sorted(locations.items(), key=lambda item: item[0].as_posix())
        },
        "unauthorized_direct_call_locations": {
            path.as_posix(): rows for path, rows in sorted(unauthorized.items(), key=lambda item: item[0].as_posix())
        },
        "evidence_sha256": {
            path.as_posix(): sha256_file(root / path) for path in REQUIRED_FILES
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
