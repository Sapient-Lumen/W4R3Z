#!/usr/bin/env python3
"""Fail when diagnostic selftests leak back into the runtime API/build surface."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DECL_RE = re.compile(r"\bint\s+(run_[A-Za-z0-9_]*selftest)\s*\(")
DEF_RE = re.compile(r"\bint\s+(run_[A-Za-z0-9_]*selftest)\s*\([^;{}]*\)\s*\{")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    runtime_header = (root / "include/anonsync_core.hpp").read_text()
    selftest_header_path = root / "include/anonsync_selftest_api.hpp"
    selftest_header = selftest_header_path.read_text()
    cmake = (root / "CMakeLists.txt").read_text()
    cli = (root / "src/anonsync_core.cpp").read_text()

    runtime_declarations = sorted(set(DECL_RE.findall(runtime_header)))
    declared = sorted(set(DECL_RE.findall(selftest_header)))
    defined: dict[str, list[str]] = {}
    definition_sources = sorted((root / "src").rglob("*.cpp"))
    definition_sources.append(root / "tests/sqlite_replay_ledger_selftests.cpp")
    for source in definition_sources:
        for name in DEF_RE.findall(source.read_text(errors="replace")):
            defined.setdefault(name, []).append(source.relative_to(root).as_posix())

    checks: list[dict[str, object]] = []

    def check(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(passed), "detail": detail})

    check("runtime_header_has_no_selftest_declarations",
          not runtime_declarations,
          f"runtime declarations={runtime_declarations}")
    check("selftest_header_declares_exactly_38_entry_points",
          len(declared) == 38,
          f"declared={len(declared)}")
    missing_definitions = sorted(set(declared) - set(defined))
    duplicate_definitions = {name: paths for name, paths in defined.items()
                             if name in declared and len(paths) != 1}
    undeclared_definitions = sorted(set(defined) - set(declared))
    check("every_declared_selftest_has_one_definition",
          not missing_definitions and not duplicate_definitions,
          f"missing={missing_definitions} duplicate={duplicate_definitions}")
    check("every_selftest_definition_is_declared_in_test_api",
          not undeclared_definitions,
          f"undeclared={undeclared_definitions}")
    check("dead_ingress_reservation_selftest_declaration_removed",
          "run_ingress_reservation_service_selftest" not in runtime_header + selftest_header,
          "stale declaration absent")
    check("cli_includes_selftest_api",
          '#include "anonsync_selftest_api.hpp"' in cli,
          "diagnostic CLI includes the explicit test API")
    check("runtime_core_excludes_all_selftest_sources",
          "src/reporting_selftests.cpp" in cmake
          and "src/sync_domain_selftests.cpp" in cmake
          and "tests/sqlite_replay_ledger_selftests.cpp" in cmake
          and "foreach(ANONSYNC_SELFTEST_SOURCE IN LISTS ANONSYNC_SELFTEST_SOURCES)" in cmake
          and 'list(FIND ANONSYNC_CORE_SOURCES "${ANONSYNC_SELFTEST_SOURCE}"' in cmake,
          "CMake owns all three diagnostic sources in one-way support libraries and guards every source")

    focused_wrapper_targets = [
        "anonsync_fuzz_json_codec",
        "anonsync_fuzz_jwt_codec",
        "anonsync_fuzz_route_event_ledger",
    ]
    focused_wrapper_links_ok = all(
        re.search(
            rf"target_link_libraries\({target}\s+PRIVATE\s+"
            r"anonsync_reporting_selftests_lib\)",
            cmake,
            re.DOTALL,
        )
        for target in focused_wrapper_targets
    )
    check("focused_wrappers_exclude_domain_corpus_dependency",
          focused_wrapper_links_ok,
          "deterministic reporting wrappers do not compile the extracted domain corpus")

    wrapper_details: list[str] = []
    wrappers_ok = True
    for wrapper in sorted((root / "fuzz").glob("fuzz_*codec.cpp")) + [root / "fuzz/fuzz_route_event_ledger.cpp"]:
        if not wrapper.is_file():
            wrappers_ok = False
            wrapper_details.append(f"missing:{wrapper.name}")
            continue
        text = wrapper.read_text()
        ok = ('#include "anonsync_selftest_api.hpp"' in text
              and '#include "anonsync_core.hpp"' not in text)
        wrappers_ok &= ok
        wrapper_details.append(f"{wrapper.name}:{'test-api' if ok else 'runtime-api'}")
    check("deterministic_wrappers_use_only_selftest_api",
          wrappers_ok,
          ", ".join(wrapper_details))

    result = {
        "format": "anonsync-runtime-selftest-separation-audit-v1",
        "declared_selftests": len(declared),
        "defined_selftests": len(defined),
        "checks_passed": sum(1 for item in checks if item["passed"]),
        "checks_total": len(checks),
        "passed": all(bool(item["passed"]) for item in checks),
        "checks": checks,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
