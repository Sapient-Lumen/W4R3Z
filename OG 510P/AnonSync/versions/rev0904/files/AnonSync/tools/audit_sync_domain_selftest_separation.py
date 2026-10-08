#!/usr/bin/env python3
"""Enforce the sync-domain runtime/diagnostic ownership boundary."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SELFTEST_ENTRY = "run_sync_domain_model_selftest"
FIXTURE_DECL_RE = re.compile(
    r"\b(?:std::string|bool|void|DaemonOwnerLockRecord)\s+"
    r"([a-z0-9_]+_for_fixture)\s*\(",
)
FIXTURE_DEF_RE = re.compile(
    r"\b(?:std::string|bool|void|DaemonOwnerLockRecord)\s+"
    r"([a-z0-9_]+_for_fixture)\s*\(",
)


def source_list_block(cmake: str, variable: str) -> str:
    match = re.search(rf"set\({re.escape(variable)}\s+(.*?)\)", cmake, re.DOTALL)
    return match.group(1) if match else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    cmake = (root / "CMakeLists.txt").read_text()
    runtime_path = root / "src/sync_domain.cpp"
    selftest_path = root / "src/sync_domain_selftests.cpp"
    bridge_path = root / "src/sync_domain_test_access.hpp"
    runtime = runtime_path.read_text()
    selftest = selftest_path.read_text()
    bridge = bridge_path.read_text()
    public_headers = "\n".join(
        path.read_text(errors="replace")
        for path in sorted((root / "include").glob("*.hpp"))
    )

    checks: list[dict[str, object]] = []

    def check(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(passed), "detail": detail})

    check(
        "runtime_translation_unit_has_no_sync_domain_selftest_definition",
        SELFTEST_ENTRY not in runtime,
        f"runtime occurrences={runtime.count(SELFTEST_ENTRY)}",
    )
    selftest_definition_count = len(re.findall(
        rf"\bint\s+{SELFTEST_ENTRY}\s*\([^;{{}}]*\)\s*\{{",
        selftest,
    ))
    check(
        "diagnostic_translation_unit_owns_exactly_one_definition",
        selftest_definition_count == 1,
        f"selftest definitions={selftest_definition_count}",
    )

    core_sources = source_list_block(cmake, "ANONSYNC_CORE_SOURCES")
    sync_domain_source_assignment = re.search(
        r"set\(ANONSYNC_SYNC_DOMAIN_SELFTEST_SOURCE\s+([^\s)]+)\)", cmake)
    sync_domain_source = (
        sync_domain_source_assignment.group(1)
        if sync_domain_source_assignment else ""
    )
    domain_library_block = re.search(
        r"add_library\(anonsync_sync_domain_selftests_lib\s+STATIC\s+"
        r"(.*?)\)",
        cmake,
        re.DOTALL,
    )
    check(
        "cmake_assigns_sync_domain_selftest_only_to_support_library",
        sync_domain_source == "src/sync_domain_selftests.cpp"
        and domain_library_block is not None
        and "${ANONSYNC_SYNC_DOMAIN_SELFTEST_SOURCE}" in domain_library_block.group(1)
        and "src/sync_domain_selftests.cpp" not in core_sources,
        "sync-domain diagnostic source has one named support owner and is core-excluded",
    )
    check(
        "cmake_guards_every_selftest_source_against_core_reabsorption",
        "foreach(ANONSYNC_SELFTEST_SOURCE IN LISTS ANONSYNC_SELFTEST_SOURCES)" in cmake
        and 'list(FIND ANONSYNC_CORE_SOURCES "${ANONSYNC_SELFTEST_SOURCE}"' in cmake,
        "all support sources are checked rather than one hard-coded filename",
    )
    core_link_start = cmake.find("target_link_libraries(anonsync_core_lib")
    core_link_end = cmake.find("\nif(ANONSYNC_USE_BUNDLED_SQLITE)", core_link_start)
    core_link_block = (
        cmake[core_link_start:core_link_end]
        if core_link_start >= 0 and core_link_end > core_link_start
        else ""
    )
    check(
        "dependency_direction_is_selftests_to_runtime_only",
        "target_link_libraries(anonsync_sync_domain_selftests_lib PUBLIC anonsync_core_lib)" in cmake
        and bool(core_link_block)
        and "anonsync_sync_domain_selftests_lib" not in core_link_block,
        "anonsync_sync_domain_selftests_lib -> anonsync_core_lib",
    )
    focused_wrappers = [
        "anonsync_fuzz_json_codec",
        "anonsync_fuzz_jwt_codec",
        "anonsync_fuzz_route_event_ledger",
    ]
    wrapper_links_ok = all(
        re.search(
            rf"target_link_libraries\({name}\s+PRIVATE\s+"
            r"anonsync_reporting_selftests_lib\)",
            cmake,
            re.DOTALL,
        )
        for name in focused_wrappers
    )
    check(
        "focused_corpus_wrappers_do_not_build_domain_selftests",
        wrapper_links_ok,
        "three deterministic wrappers depend on reporting diagnostics, not the domain corpus aggregate",
    )

    include_users: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part.startswith("build") for part in path.parts):
            continue
        if path.suffix not in {".cpp", ".hpp", ".h", ".cc"}:
            continue
        if '#include "sync_domain_test_access.hpp"' in path.read_text(errors="replace"):
            include_users.append(path.relative_to(root).as_posix())
    check(
        "fixture_bridge_is_private_and_has_two_explicit_users",
        not (root / "include/sync_domain_test_access.hpp").exists()
        and include_users == ["src/sync_domain.cpp", "src/sync_domain_selftests.cpp"],
        f"include users={include_users}",
    )
    check(
        "public_runtime_api_does_not_expose_fixture_authority",
        "sync_domain_test_access" not in public_headers
        and "_for_fixture" not in public_headers,
        "public headers contain no fixture bridge declarations",
    )

    declarations = sorted(set(FIXTURE_DECL_RE.findall(bridge)))
    bridge_definition_section = runtime[runtime.rfind("namespace sync_domain_test_access {") :]
    definitions = sorted(set(FIXTURE_DEF_RE.findall(bridge_definition_section)))
    check(
        "fixture_bridge_declaration_definition_sets_match",
        bool(declarations) and declarations == definitions,
        f"declared={declarations} defined={definitions}",
    )
    check(
        "fixture_bridge_names_make_authority_scope_explicit",
        declarations and all(name.endswith("_for_fixture") for name in declarations),
        f"fixture entry points={declarations}",
    )

    test_only_tokens = [
        "void sqlite_backup_file_or_throw(",
        "struct SyncSidecarReviewEventMetrics",
        "sqlite_sidecar_review_event_metrics_for_session_or_throw(",
    ]
    check(
        "test_only_sqlite_fixture_helpers_left_runtime",
        all(token not in runtime for token in test_only_tokens)
        and all(token in selftest for token in test_only_tokens),
        "backup and review-metrics fixture helpers are diagnostic-owned",
    )
    check(
        "production_unit_is_materially_smaller_than_parent_boundary",
        len(runtime.splitlines()) < 17000
        and len(selftest.splitlines()) > 8000,
        f"runtime_lines={len(runtime.splitlines())} selftest_lines={len(selftest.splitlines())}",
    )
    check(
        "diagnostic_source_uses_explicit_fixture_bridge",
        selftest.count("sync_domain_test_access::") >= 20
        and '#include "sync_domain_test_access.hpp"' in selftest,
        f"qualified fixture calls={selftest.count('sync_domain_test_access::')}",
    )

    result = {
        "format": "anonsync-sync-domain-selftest-separation-audit-v1",
        "runtime_lines": len(runtime.splitlines()),
        "selftest_lines": len(selftest.splitlines()),
        "fixture_bridge_declarations": declarations,
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
