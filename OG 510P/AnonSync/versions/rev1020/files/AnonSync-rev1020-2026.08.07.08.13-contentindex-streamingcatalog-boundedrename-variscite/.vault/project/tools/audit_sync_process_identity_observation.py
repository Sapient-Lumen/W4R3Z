#!/usr/bin/env python3
"""Fail-closed audit for daemon heartbeat process-incarnation observations."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("include/anonsync_core.hpp"),
    Path("src/sync_process_identity_observation.hpp"),
    Path("src/sync_process_identity_observation_internal.hpp"),
    Path("src/sync_process_identity_observation.cpp"),
    Path("src/sync_system_epoch_identity.hpp"),
    Path("src/sync_system_epoch_identity.cpp"),
    Path("tests/sync_system_epoch_identity_test.cpp"),
    Path("src/sync_daemon_heartbeat_document.hpp"),
    Path("src/sync_daemon_heartbeat_document.cpp"),
    Path("src/sync_daemon_heartbeat_publication.cpp"),
    Path("src/sync_domain.cpp"),
    Path("src/sync_domain_selftests.cpp"),
    Path("src/sync_operator_cli.cpp"),
    Path("tests/sync_process_identity_observation_test.cpp"),
    Path("tests/sync_daemon_heartbeat_document_test.cpp"),
    Path("tools/audit_sync_process_identity_observation.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def block_between(text: str, begin: str, end: str) -> str:
    start = text.find(begin)
    stop = text.find(end, start + len(begin)) if start >= 0 else -1
    return text[start:stop] if start >= 0 and stop > start else ""


def emit(root: Path, output: Path | None, checks: list[Check], metrics: dict) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-process-identity-observation-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "metrics": metrics,
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="AnonSync source root",
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    if missing:
        return emit(root, args.json, checks, {})

    texts = {
        path: (root / path).read_text(encoding="utf-8") for path in REQUIRED
    }
    cmake = texts[Path("CMakeLists.txt")]
    public = texts[Path("include/anonsync_core.hpp")]
    header = texts[Path("src/sync_process_identity_observation.hpp")]
    internal = texts[Path("src/sync_process_identity_observation_internal.hpp")]
    source = texts[Path("src/sync_process_identity_observation.cpp")]
    epoch_header = texts[Path("src/sync_system_epoch_identity.hpp")]
    epoch_source = texts[Path("src/sync_system_epoch_identity.cpp")]
    epoch_test = texts[Path("tests/sync_system_epoch_identity_test.cpp")]
    heartbeat_header = texts[Path("src/sync_daemon_heartbeat_document.hpp")]
    heartbeat_source = texts[Path("src/sync_daemon_heartbeat_document.cpp")]
    heartbeat_publication = texts[Path("src/sync_daemon_heartbeat_publication.cpp")]
    domain = texts[Path("src/sync_domain.cpp")]
    selftests = texts[Path("src/sync_domain_selftests.cpp")]
    cli = texts[Path("src/sync_operator_cli.cpp")]
    focused = texts[Path("tests/sync_process_identity_observation_test.cpp")]
    heartbeat_test = texts[Path("tests/sync_daemon_heartbeat_document_test.cpp")]

    require(
        "struct SyncProcessIdentityObservation final" in header
        and "Unlike SyncProcessIncarnation" in header
        and "not process-local capability authority" in header,
        "observation_not_authority",
        "serializable process evidence is explicitly distinct from local capability authority",
    )
    require(
        "enum class SyncProcessIdentityMatchKind" in header
        and all(name in header for name in (
            "Match", "NotRunning", "Mismatch", "Unsupported",
            "Indeterminate", "Invalid",
        )),
        "typed_match_outcomes",
        "liveness checks cannot collapse mismatch, absence, unsupported, and error into one boolean",
    )
    require(
        "linux-proc-starttime-v1" in source
        and "windows-creation-filetime-v1" in source
        and "process-incarnation-unavailable-v1" in source,
        "versioned_platform_formats",
        "platform observations and explicit unavailability have versioned canonical formats",
    )
    require(
        '#include "sync_system_epoch_identity.hpp"' in source
        and "observe_sync_system_boot_identity_or_throw" in source
        and '"/proc/" + decimal_u64(process_id) + "/stat"' in source
        and "rfind(')')" in source
        and "field <= 22" in source,
        "linux_boot_and_starttime_binding",
        "Linux identity reuses the shared strict boot observation and binds proc stat field 22 while handling parentheses in comm",
    )
    require(
        '"/proc/sys/kernel/random/boot_id"' in epoch_source
        and "O_NOFOLLOW" in epoch_source
        and "kMaximumBootIdentityBytes" in epoch_source
        and "sync_system_parse_boot_id_text_or_throw" in epoch_header
        and "repeated newline is not normalized into evidence" in epoch_test,
        "shared_boot_observer_is_bounded_and_strict",
        "the process leaf cannot silently diverge from the outbox clock's boot-ID framing policy",
    )
    require(
        "SYS_pidfd_open" in source
        and "pidfd_reports_exit_noexcept" in source
        and source.count("pidfd_reports_exit_noexcept(") >= 3,
        "linux_pidfd_reuse_fence",
        "a stable pidfd is checked around proc observation when the kernel supports it",
    )
    require(
        "O_NOFOLLOW" in source
        and "O_CLOEXEC" in source
        and "kMaximumProcTextBytes" in source
        and "embedded NUL" in source,
        "bounded_proc_reads",
        "proc evidence is read through bounded, no-follow, close-on-exec descriptors",
    )
    require(
        "OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION" in source
        and "GetProcessTimes" in source
        and "WaitForSingleObject" in source,
        "windows_creation_time_binding",
        "Windows identity binds an opened process object to creation FILETIME and live state",
    )
    require(
        "::kill(" not in source
        and "kill(expected" not in source
        and "kill(pid" not in source,
        "no_pid_only_liveness_probe",
        "the leaf does not treat kill(pid, 0) as incarnation evidence",
    )
    require(
        "canonical_linux_boot_id" in internal
        and "canonical_positive_decimal_token" in internal
        and "parse_linux_proc_pid_stat_identity_or_throw" in internal,
        "parser_contract_exposed_only_to_tests",
        "format geometry and the proc parser have a narrow internal test surface",
    )
    require(
        "process_identity_present" in heartbeat_header
        and "SyncProcessIdentityObservation process_identity" in heartbeat_header,
        "heartbeat_typed_process_field",
        "the authority-bearing heartbeat subset owns a typed process observation",
    )
    require(
        "anonsync-sync-daemon-service-heartbeat-v2" in heartbeat_publication
        and '"process_incarnation"' in heartbeat_source
        and 'document.revision_id = "rev0840"' in heartbeat_publication
        and "result.daemon_heartbeat_process_identity_format" in heartbeat_publication
        and "result.daemon_heartbeat_process_boot_id" in heartbeat_publication
        and "result.daemon_heartbeat_process_start_token" in heartbeat_publication,
        "heartbeat_v2_serialization",
        "new heartbeat bytes carry the typed process object under a new schema revision",
    )
    require(
        "v1 cannot contain process_incarnation fields" in heartbeat_source
        and "legacy v1 heartbeat remains decodable" in heartbeat_test,
        "legacy_decode_without_evidence_promotion",
        "v1 remains readable but cannot smuggle fields that bypass v2 validation",
    )
    require(
        "bind_current_process_identity_to_heartbeat_result_or_throw" in domain
        and "writer process incarnation changed after the first heartbeat" in domain,
        "writer_incarnation_sticky",
        "all writes in one daemon result remain bound to the first observed OS process life",
    )
    require(
        domain.count("check_sync_process_identity_observation_noexcept(") >= 2
        and "record_existing_heartbeat_process_match" in domain,
        "preflight_and_status_reobserve",
        "daemon preflight and operator status independently re-observe the claimed process",
    )
    require(
        "non-final legacy heartbeat has only PID process evidence" in heartbeat_source
        and "non-final heartbeat process incarnation could not be verified" in heartbeat_source
        and domain.count(
            "evaluate_sync_daemon_heartbeat_lifecycle_or_throw("
        ) >= 2,
        "nonfinal_fail_closed",
        "one shared policy makes preflight and status refuse legacy, unsupported, invalid, and indeterminate evidence",
    )
    require(
        "heartbeat is stale while its exact process incarnation remains live" in heartbeat_source
        and "clock staleness cannot impersonate exact process death" in heartbeat_test,
        "clock_staleness_not_process_death",
        "stale time cannot authorize takeover while the exact process remains observable",
    )
    require(
        "different observed process incarnation agree" in selftests
        and "exact heartbeat process incarnation remains live" in selftests
        and "recycled_process_identity_fixture_or_throw" in selftests,
        "integration_reuse_corpus",
        "domain tests distinguish a recycled live PID from the exact live incarnation",
    )
    require(
        "Linux stat parser uses the final comm delimiter and exact field 22" in focused
        and "same Linux PID with a different starttime is PID reuse evidence" in focused
        and "current Linux process re-observes as one exact live incarnation" in focused,
        "focused_parser_and_live_corpus",
        "focused tests cover hostile proc framing, exact current match, and PID reuse evidence",
    )
    require(
        "v2 heartbeat requires typed process-incarnation evidence" in heartbeat_test
        and "top-level PID cannot diverge" in heartbeat_test
        and "legacy format cannot smuggle" in heartbeat_test,
        "heartbeat_schema_corpus",
        "document tests enforce required shape, duplicate PID equality, and version separation",
    )
    require(
        "daemon_heartbeat_process_identity_present" in public
        and "daemon_heartbeat_process_identity_match_kind" in public
        and "service_lifecycle_existing_heartbeat_process_identity_matches" in public,
        "public_result_evidence",
        "daemon and operator results expose typed process verification outcomes",
    )
    require(
        "daemon_heartbeat_process_identity_verification_available" in cli
        and "service_lifecycle_existing_heartbeat_process_identity_match_kind" in cli
        and "daemon_heartbeat_process_start_token" in cli,
        "cli_evidence_parity",
        "JSON reports surface the same process-incarnation facts used by policy",
    )

    invariant_block = block_between(
        cmake,
        "foreach(ANONSYNC_INVARIANT_OWNED_SOURCE",
        "add_library(anonsync_core_lib",
    )
    core_link_block = block_between(
        cmake,
        "target_link_libraries(anonsync_core_lib",
        "if(ANONSYNC_USE_BUNDLED_SQLITE)",
    )
    focused_guard_block = block_between(
        cmake,
        "foreach(ANONSYNC_FOCUSED_BOUNDARY_TARGET",
        "if(TARGET anonsync_sync_bounded_regular_file_syscall_test)",
    )
    inherited_consumer_block = block_between(
        cmake,
        "foreach(ANONSYNC_INHERITED_PROCESS_CONSUMER",
        "target_link_libraries(${ANONSYNC_INHERITED_PROCESS_CONSUMER}",
    )
    sanitizer_compile_block = block_between(
        cmake,
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS",
        "if(TARGET anonsync_sync_bounded_regular_file_syscall_test)",
    )
    sanitizer_link_block = block_between(
        cmake,
        "foreach(tgt\n      anonsync_core",
        "target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)",
    )
    require(
        "add_library(anonsync_process_identity_observation STATIC" in cmake
        and "ANONSYNC_PROCESS_IDENTITY_OBSERVATION_SOURCE" in invariant_block
        and "target_link_libraries(anonsync_process_identity_observation PRIVATE" in cmake
        and "anonsync_system_epoch_identity" in cmake,
        "focused_leaf_target",
        "process observation has one separately compiled invariant owner outside core translation units",
    )
    require(
        "anonsync_process_identity_observation" in core_link_block
        and "anonsync_process_identity_observation" in focused_guard_block,
        "one_way_dependency",
        "core consumes the leaf and configure guards forbid a leaf-to-core backedge",
    )
    require(
        "add_executable(anonsync_process_identity_observation_test" in cmake
        and "add_test(NAME anonsync_process_identity_observation_test" in cmake,
        "focused_test_registered",
        "the independent observation corpus is a CTest obligation",
    )
    require(
        "anonsync_process_identity_observation_test" not in inherited_consumer_block,
        "focused_test_has_no_unused_process_wrapper",
        "the non-forking leaf corpus does not inherit the process-wrapper dependency graph",
    )
    require(
        "anonsync_process_identity_observation" in sanitizer_compile_block
        and "anonsync_process_identity_observation_test" in sanitizer_compile_block
        and "anonsync_process_identity_observation_test" in sanitizer_link_block,
        "focused_sanitizer_compile_link_parity",
        "the focused executable and leaf are instrumented and the executable links the sanitizer runtime",
    )

    metrics = {
        "header_lines": len(header.splitlines()),
        "source_lines": len(source.splitlines()),
        "focused_test_lines": len(focused.splitlines()),
        "domain_lines": len(domain.splitlines()),
        "process_checker_domain_calls": domain.count(
            "check_sync_process_identity_observation_noexcept("
        ),
        "shared_lifecycle_policy_domain_calls": domain.count(
            "evaluate_sync_daemon_heartbeat_lifecycle_or_throw("
        ),
        "pidfd_poll_sites": source.count("pidfd_reports_exit_noexcept("),
        "raw_pid_only_kill_sites": source.count("::kill("),
    }
    return emit(root, args.json, checks, metrics)


if __name__ == "__main__":
    raise SystemExit(main())
