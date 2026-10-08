#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
target_rel = Path(sys.argv[2] if len(sys.argv) > 2 else "src/sync_domain.cpp")
target = root / target_rel
module_cpp = root / "src/persistence/peer_ingress_connection_profile.cpp"
module_hpp = root / "src/persistence/peer_ingress_connection_profile.hpp"
test_cpp = root / "tests/persistence/peer_ingress_connection_profile_test.cpp"
cmake_path = root / "CMakeLists.txt"

for required in (target, module_cpp, module_hpp, test_cpp, cmake_path):
    if not required.is_file():
        print(json.dumps({
            "passed": False,
            "error": f"missing required file: {required}",
        }, indent=2, sort_keys=True))
        raise SystemExit(1)

target_text = target.read_text(encoding="utf-8")
cpp = module_cpp.read_text(encoding="utf-8")
hpp = module_hpp.read_text(encoding="utf-8")
test = test_cpp.read_text(encoding="utf-8")
cmake = cmake_path.read_text(encoding="utf-8")

raw_open_pattern = re.compile(r"(?<![A-Za-z0-9_])(?:::)?sqlite3_open_v2\s*\(")
verified_open_pattern = re.compile(r"\bopen_verified_sqlite_database\s*\(")

raw_target_sites = len(raw_open_pattern.findall(target_text))
verified_target_sites = len(verified_open_pattern.findall(target_text))
raw_boundary_sites = len(raw_open_pattern.findall(cpp))

profile_include = '#include "persistence/peer_ingress_connection_profile.hpp"'
posix_guard = "#if !defined(_WIN32)"
include_position = target_text.find(profile_include)
posix_guard_position = target_text.find(posix_guard)

checks = {
    "target_has_no_raw_sqlite3_open_v2": raw_target_sites == 0,
    "target_routes_all_discovered_opens_through_boundary":
        verified_target_sites >= 1,
    "raw_open_is_confined_to_one_boundary_site": raw_boundary_sites == 1,
    "profile_header_is_cross_platform_visible":
        include_position >= 0 and
        (posix_guard_position < 0 or include_position < posix_guard_position),
    "module_is_compiled":
        "src/persistence/peer_ingress_connection_profile.cpp" in cmake,
    "focused_test_is_registered":
        "anonsync_peer_ingress_connection_profile_test" in cmake,
    "durable_profile_rejects_empty_and_special_names":
        "filename_is_durable_file_candidate" in cpp and
        "filename[0] == ':'" in cpp,
    "uri_scheme_is_rejected_even_without_uri_flag":
        "has_file_uri_scheme" in cpp and
        "return !has_file_uri_scheme(filename);" in cpp,
    "fullmutex_is_mandatory":
        "(flags & SQLITE_OPEN_FULLMUTEX) == 0" in cpp,
    "alternate_control_planes_are_rejected": all(
        token in cpp for token in (
            "SQLITE_OPEN_URI",
            "SQLITE_OPEN_MEMORY",
            "SQLITE_OPEN_NOMUTEX",
            "SQLITE_OPEN_SHAREDCACHE",
        )
    ),
    "unknown_application_flags_are_rejected":
        "flags & ~allowed_application_open_flags()" in cpp,
    "private_cache_is_imposed":
        "flags | SQLITE_OPEN_PRIVATECACHE" in cpp,
    "file_backing_is_observed":
        'sqlite3_db_filename(candidate, "main")' in cpp and
        "observed_main_filename[0] == '\\0'" in cpp,
    "actual_access_mode_is_observed":
        'sqlite3_db_readonly(candidate, "main")' in cpp,
    "actual_serialization_is_observed":
        "sqlite3_db_mutex(candidate) == nullptr" in cpp,
    "exact_vfs_object_is_observed":
        "SQLITE_FCNTL_VFS_POINTER" in cpp and
        "observed_vfs != selected_vfs" in cpp,
    "vfs_name_is_diagnostic_only":
        "VFSNAME is diagnostic-only" in cpp and
        "vfs_name_diagnostic_available" in cpp,
    "successful_candidate_publication_follows_all_observations":
        cpp.rfind("*published_database = candidate;") >
        cpp.find("SQLITE_FCNTL_VFS_POINTER") > 0,
    "misleading_scoped_busy_handler_api_is_absent":
        "ScopedSqliteBusyHandler" not in hpp and
        "BoundedBusyAttemptBudget" not in hpp and
        "bounded_busy_attempt_callback" not in cpp,
    "adversarial_test_covers_uri_control_plane":
        "mode=memory" in test and "nolock=1" in test,
    "adversarial_test_covers_exact_vfs_alias":
        "RegisteredAliasVfs" in test and
        "vfs_identity_verified" in test,
    "adversarial_test_covers_literal_mode_text_filename":
        "literal-mode=memory" in test,
}

result = {
    "format": "anonsync-peer-ingress-connection-profile-audit-v2",
    "passed": all(checks.values()),
    "target": target_rel.as_posix(),
    "metrics": {
        "target_raw_open_sites": raw_target_sites,
        "target_verified_open_sites": verified_target_sites,
        "boundary_raw_open_sites": raw_boundary_sites,
        "target_lines": len(target_text.splitlines()),
        "boundary_lines": len(cpp.splitlines()),
        "focused_test_lines": len(test.splitlines()),
    },
    "checks": checks,
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if result["passed"] else 1)
