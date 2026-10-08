#!/usr/bin/env python3
"""Lexical release fence for rev1016/rev1017 Linux resource diagnostics.

Source spelling is not semantic proof. Runtime, sanitizer, procfs behavior,
local-socket identity, reconstruction, and package evidence remain load-bearing.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("README.md"),
    Path("LINUX_PROCESS_RESOURCE_SNAPSHOT_AND_MULTISHARE_AGGREGATE_AUDIT_rev1016.md"),
    Path("REVISION_NOTES_rev1016.md"),
    Path("LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md"),
    Path("REVISION_NOTES_rev1017.md"),
    Path("src/anonsync_sync.cpp"),
    Path("src/sync_local_status_socket.hpp"),
    Path("src/sync_local_status_socket.cpp"),
    Path("src/sync_linux_process_resources.hpp"),
    Path("src/sync_linux_process_resources.cpp"),
    Path("tests/sync_local_status_socket_test.cpp"),
    Path("tests/sync_linux_process_resources_test.cpp"),
    Path("tests/sync_linux_process_resources_fixture.cpp"),
    Path("tools/test_anonsync_process_resources.py"),
    Path("tools/audit_sync_linux_process_resources.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def function_window(text: str, token: str, next_token: str) -> str:
    start = text.find(token)
    if start < 0:
        return ""
    end = text.find(next_token, start + len(token))
    return text[start:] if end < 0 else text[start:end]


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-linux-process-resources-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove procfs consistency, process identity, "
            "time-series scheduling, runtime peaks, sanitizer cleanliness, "
            "reconstruction, or package identity"
        ),
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 0 if not violations else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    bootstrap_candidates = (
        root.parent.parent / "BOOTSTRAPROSE.md",
        root.parent / "BOOTSTRAPROSE.md",
    )
    bootstrap_path = next((path for path in bootstrap_candidates if path.is_file()), None)
    require(bootstrap_path is not None, "bootstrap_exists", "release-root runbook is visible")
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    header = text["src/sync_linux_process_resources.hpp"]
    source = text["src/sync_linux_process_resources.cpp"]
    socket_c = text["src/sync_local_status_socket.cpp"]
    cli = text["src/anonsync_sync.cpp"]
    unit = text["tests/sync_linux_process_resources_test.cpp"]
    socket_test = text["tests/sync_local_status_socket_test.cpp"]
    fixture = text["tests/sync_linux_process_resources_fixture.cpp"]
    process_test = text["tools/test_anonsync_process_resources.py"]
    cmake = text["CMakeLists.txt"]
    design1016 = text["LINUX_PROCESS_RESOURCE_SNAPSHOT_AND_MULTISHARE_AGGREGATE_AUDIT_rev1016.md"]
    notes1016 = text["REVISION_NOTES_rev1016.md"]
    design1017 = text["LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md"]
    notes1017 = text["REVISION_NOTES_rev1017.md"]
    readme = text["README.md"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]

    status_handler = function_window(
        socket_c,
        'if (request.has_value() && *request == kStatusRequest)',
        'else if (request.has_value() && *request == kResourcesRequest)',
    )
    socket_selection = function_window(
        cli,
        "[[nodiscard]] std::vector<fs::path> resource_socket_paths_or_throw(",
        "struct ResourceTotals final",
    )
    round_sampler = function_window(
        cli,
        "[[nodiscard]] ResourceRound sample_resource_round_or_throw(",
        "void append_resource_totals_json",
    )
    one_shot = function_window(
        cli,
        "int command_resources(const Options& options)",
        "int command_resources_watch(const Options& options)",
    )
    series = function_window(
        cli,
        "int command_resources_watch(const Options& options)",
        "int command_stop(const Options& options)",
    )

    require(
        all(schema in header for schema in (
            "anonsync.local-process-resources.response.v1",
            "anonsync.local-process-resources.aggregate.v1",
            "anonsync.local-process-resources.series.v1",
        )),
        "schemas_are_explicit_and_versioned",
        "process, one-shot aggregate, and time-series boundaries are named",
    )
    require(
        'constexpr std::string_view kResourcesRequest = "resources\\n"' in socket_c
        and "query_sync_local_process_resources_or_throw" in text["src/sync_local_status_socket.hpp"],
        "series_reuses_one_exact_owner_resource_request",
        "no second daemon protocol or observer was introduced",
    )
    require(
        "observe_sync_linux_process_resources_or_throw" not in status_handler
        and "snapshot_copy()" in status_handler,
        "ordinary_status_remains_procfs_cold",
        "status reads already-rendered bytes rather than sampling procfs",
    )
    require(
        '"/proc/self/smaps_rollup"' in source
        and "kMaximumProcSnapshotBytes = 64U * 1024U" in source
        and "::read(descriptor, bytes.data(), bytes.size())" in source
        and all(token in source for token in (
            '"Pss_Anon"', '"Pss_File"', '"Pss_Shmem"',
            "getrusage(RUSAGE_SELF", '"/proc/self/fd"', '"/proc/self/task"',
        )),
        "linux_observer_remains_bounded_and_process_local",
        "rev1017 composes the released strict observer",
    )
    require(
        "selected.empty() || selected.size() > kResourceMaximumProcesses" in socket_selection
        and "same --socket path more than once" in socket_selection
        and "kResourceMaximumProcesses = 256U" in cli,
        "socket_selection_is_shared_and_bounded",
        "one through 256 distinct pathnames enter either command",
    )
    require(
        "expected_identities" in round_sampler
        and "same live process" in round_sampler
        and "restart or socket identity change" in round_sampler
        and "resource_deadline" in round_sampler,
        "round_sampler_binds_identity_dedup_and_deadline",
        "all rounds share one live-process and deadline boundary",
    )
    require(
        "ResourceTotals totals" in round_sampler
        and "round.totals.add" in round_sampler
        and "checked_resource_add" in cli,
        "one_shot_and_series_share_checked_aggregation",
        "resource sums cannot drift into duplicate implementations",
    )
    require(
        "kSyncLinuxProcessResourcesAggregateSchema" in one_shot
        and "timeout_is_one_aggregate_deadline" in one_shot
        and "samples_are_sequential_not_atomic" in one_shot,
        "released_one_shot_schema_and_nonclaims_are_preserved",
        "rev1017 does not silently revise aggregate v1",
    )
    require(
        "samples must be in [2, 1024]" in series
        and "interval must be in [1, 3600000]" in series
        and "timeout must be in [1, 86400000]" in series
        and "final scheduled sample must precede the total deadline" in series,
        "series_frontiers_and_schedule_preflight_are_explicit",
        "sample, interval, and one-deadline bounds are enforced before work",
    )
    require(
        "started_at + resource_milliseconds_or_throw" in series
        and "sleep_until(scheduled_at)" in series
        and "schedule_is_anchored_to_command_start" in series,
        "series_schedule_is_fixed_to_command_start",
        "round duration cannot accumulate into chained schedule drift",
    )
    require(
        "std::vector<ResourceSeriesPoint> points" in series
        and "std::vector<ResourceProcessEnvelope> envelopes" in series
        and "retained_shape_is_processes_plus_samples" in series
        and "full_process_by_sample_matrix_is_not_retained" in series,
        "series_retained_shape_is_processes_plus_samples",
        "the full process-by-sample response matrix is not retained",
    )
    require(
        all(token in series for token in (
            "first_totals", "last_totals", "observed_peak_sums",
            "aggregate_usage_delta", "maximum_schedule_lag_milliseconds",
            "maximum_round_sample_span_milliseconds", "processes", "points",
        )),
        "series_reports_compact_points_peaks_envelopes_and_deltas",
        "the operator receives bounded time-series evidence",
    )
    require(
        all(token in series for token in (
            "process_identity_must_remain_stable",
            "restarts_fail_closed",
            "rounds_and_processes_are_sampled_sequentially_not_atomically",
            "between_point_peaks_may_be_missed",
            "measurement_is_diagnostic_only",
            "ordinary_status_remains_procfs_cold",
        )),
        "series_states_identity_sampling_and_authority_nonclaims",
        "sampled peaks cannot masquerade as atomic sync authority",
    )
    require(
        "test_strict_smaps_parser" in unit
        and "test_live_observation_and_roundtrip" in unit
        and "query_sync_local_process_resources_or_throw" in socket_test,
        "existing_strict_observer_and_private_socket_runtime_remain_bound",
        "rev1017 retains parser and owner-socket proof",
    )
    require(
        "const long page_size = ::sysconf(_SC_PAGESIZE);" in fixture
        and fixture.find("::sysconf(_SC_PAGESIZE)") < fixture.find("::mmap(")
        and "trigger_anonymous_bytes" in fixture
        and "maximum_anonymous_bytes" in fixture,
        "fixture_queries_page_size_before_mapping_and_bounds_growth",
        "constructor failure cannot strand the new mapping before RAII ownership",
    )
    require(
        '"--samples", "16"' in process_test
        and '"--interval-milliseconds", "75"' in process_test
        and "growth_trigger.write_bytes" in process_test
        and "40 * 1024" in process_test,
        "real_process_runtime_triggers_and_observes_memory_growth",
        "a sampled series must expose the touched 48 MiB rise",
    )
    require(
        "scheduled_offset_milliseconds" in process_test
        and "retained a full response matrix" in process_test
        and "aggregate_usage_delta" in process_test
        and "process envelope" in process_test,
        "real_process_runtime_binds_fixed_schedule_compact_shape_and_envelopes",
        "output relationships are checked rather than only schema presence",
    )
    require(
        "same live process" in process_test
        and "changing_identity_server" in process_test
        and "restart or socket identity change" in process_test,
        "real_process_runtime_rejects_alias_and_process_replacement",
        "different process lifetimes cannot be joined into one series",
    )
    require(
        "final scheduled sample" in process_test
        and '"--delay-milliseconds", "250"' in process_test
        and "deadline_elapsed < 0.8" in process_test,
        "runtime_binds_schedule_preflight_and_one_total_deadline",
        "time budgets do not multiply by process or round count",
    )
    require(
        "ordinary status changed after sampling" in process_test
        and "not socket_a.exists()" in process_test,
        "runtime_binds_status_isolation_and_clean_drain",
        "diagnostic work leaves ordinary status and socket lifecycle intact",
    )
    require(
        "anonsync_sync_process_resources_process_test" in cmake
        and "anonsync_sync_linux_process_resources_audit" in cmake
        and "anonsync_product_lane" in cmake,
        "build_registry_binds_runtime_audit_and_product_lane",
        "the shipping graph retains the resource boundary",
    )
    require(
        "LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md" in verifier
        and "REVISION_NOTES_rev1017.md" in verifier
        and "rev1017_linux_process_resource_series" in structural,
        "release_and_structural_policy_bind_rev1017",
        "the archive cannot omit implementation, runtime, design, or notes",
    )
    prose = "\n".join((design1016, notes1016, design1017, notes1017, readme, bootstrap))
    require(
        all(token in prose for token in (
            "O(processes + samples)", "1,024", "one total deadline",
            "48 MiB", "40 MiB", "between", "diagnostic", "multi-terabyte",
            "page cache", "allocator", "cgroup", "rename/move", "directories",
            "conflict", "selective-sync", "ENOSPC", "Android", "Tor", "I2P",
        )),
        "benefit_and_product_nonclaims_are_explicit",
        "bounded sampling is not overstated as solved product memory or breadth",
    )
    require(
        all(token not in prose for token in (
            "VALIDATION_PENDING_REV1017",
            "ARCHIVE_PENDING_REV1017",
            "CODENAME_PENDING_REV1017",
        )),
        "final_validation_and_release_cutpoint_are_sealed",
        "the audit remains red until exact release evidence replaces placeholders",
    )
    self_text = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "Source spelling is not semantic proof" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "compiler, sanitizer, runtime, reconstruction, and package proof remain load-bearing",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
