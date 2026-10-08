#!/usr/bin/env python3
"""Lexical release audit for rev1018 sparse selective-service memory proof.

Source spelling is not semantic proof. Compiler, sanitizer, runtime,
reconstruction, and package evidence remain load-bearing.
lexical-hygiene-not-semantic-proof
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import NoReturn


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("README.md"),
    Path("SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md"),
    Path("REVISION_NOTES_rev1018.md"),
    Path("src/sync_replica_folder_observer.hpp"),
    Path("src/sync_replica_folder_observer.cpp"),
    Path("src/sync_replica_folder_scan_owner.hpp"),
    Path("src/sync_replica_folder_scan_owner.cpp"),
    Path("src/anonsync_folder.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("tests/sync_replica_folder_observer_test.cpp"),
    Path("tools/test_anonsync_sparse_multiterabyte_selective_resources.py"),
    Path("tools/audit_sync_sparse_multiterabyte_selective_resources.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def emit(root: Path, json_output: bool, checks: list[Check]) -> int:
    passed = sum(check.passed for check in checks)
    if json_output:
        print(json.dumps({
            "format": "anonsync-sparse-multiterabyte-selective-audit-v1",
            "root": str(root),
            "checks": [asdict(check) for check in checks],
            "passed": passed,
            "total": len(checks),
        }, sort_keys=True))
    else:
        for check in checks:
            print(f"[{'PASS' if check.passed else 'FAIL'}] {check.name}: {check.detail}")
        print(f"sparse multi-terabyte selective audit: {passed}/{len(checks)} checks passed")
    return 0 if passed == len(checks) else 1


def normalized(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    checks: list[Check] = []

    def require(condition: bool, name: str, detail: str) -> None:
        checks.append(Check(name, bool(condition), detail))

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

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    observer_h = text["src/sync_replica_folder_observer.hpp"]
    observer_c = text["src/sync_replica_folder_observer.cpp"]
    scan_h = text["src/sync_replica_folder_scan_owner.hpp"]
    scan_c = text["src/sync_replica_folder_scan_owner.cpp"]
    folder_cli = text["src/anonsync_folder.cpp"]
    sync_cli = text["src/anonsync_sync.cpp"]
    observer_test = text["tests/sync_replica_folder_observer_test.cpp"]
    process_test = text["tools/test_anonsync_sparse_multiterabyte_selective_resources.py"]
    cmake = text["CMakeLists.txt"]
    design = text["SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md"]
    notes = text["REVISION_NOTES_rev1018.md"]
    readme = text["README.md"]
    structural = text["tools/audit_sync_file_payload_store.py"]
    verifier = text["tools/verify_release_package.py"]
    self_text = text["tools/audit_sync_sparse_multiterabyte_selective_resources.py"]

    require(
        "metadata_only_regular_file_logical_bytes" in observer_h
        and "sparse logical size" in observer_h
        and "not allocated blocks" in observer_h
        and "pruned metadata-only directory" in observer_h,
        "logical_byte_field_is_narrowly_documented",
        "the report distinguishes observed sparse st_size from allocated or hashed bytes",
    )
    require(
        "regular_file_logical_size_or_throw" in observer_c
        and "metadata-only regular-file logical bytes exceed " in observer_c
        and "uint64 range" in observer_c
        and "metadata_only_regular_file_logical_bytes +=" in observer_c,
        "metadata_only_logical_bytes_use_checked_observation",
        "each individually classified excluded file contributes one checked st_size",
    )
    require(
        "local_directory_enumeration_pass_count" in scan_h
        and "local_peak_buffered_directory_component_batch_count" in scan_h
        and "local_peak_simultaneously_buffered_directory_component_count" in scan_h
        and scan_c.count("peak_simultaneously_buffered_directory_component_count") >= 2,
        "folder_pass_copies_exact_bounded_traversal_diagnostics",
        "idle and ordinary pass results expose existing traversal evidence without a second walk",
    )
    require(
        all(token in folder_cli for token in (
            "metadata_only_regular_file_logical_bytes",
            "local_directory_enumeration_passes",
            "local_peak_buffered_directory_component_batch_count",
            "local_peak_simultaneously_buffered_directory_component_count",
        ))
        and all(token in sync_cli for token in (
            "metadata_only_regular_file_logical_bytes",
            "local_directory_enumeration_passes",
            "local_peak_buffered_directory_component_batch_count",
            "local_peak_simultaneously_buffered_directory_component_count",
        )),
        "shipping_json_exposes_exact_diagnostics",
        "folder, once, and share-create paths render the same counters",
    )
    require(
        "test_selective_sparse_logical_bytes_and_bounded_batch" in observer_test
        and "metadata-only sparse logical bytes cross four tebibytes exactly" in observer_test
        and "metadata-only logical size does not spend selected byte frontiers" in observer_test
        and "peak_simultaneously_buffered_directory_component_count <=" in observer_test,
        "focused_cpp_runtime_covers_sparse_selection_and_batching",
        "the observer proof crosses four TiB while one selected file remains within an eight-byte budget",
    )
    require(
        "FILE_COUNT_PER_SHARE = 4_097" in process_test
        and "FILE_LOGICAL_BYTES = 512 * 1024 * 1024" in process_test
        and "AGGREGATE_LOGICAL_BYTES = 2 * SHARE_LOGICAL_BYTES" in process_test
        and "4_399_120_252_928" in process_test
        and process_test.count("start_service(sync=sync") == 2,
        "real_process_fixture_binds_two_services_and_exact_extent",
        "two independent configured services own 8,194 sparse files totaling more than four TiB",
    )
    require(
        '"resources-watch"' in process_test
        and "RESOURCE_SAMPLES = 24" in process_test
        and "RESOURCE_INTERVAL_MILLISECONDS = 75" in process_test
        and "MAXIMUM_AGGREGATE_PSS_KIB = 1024 * 1024" in process_test
        and "MAXIMUM_AGGREGATE_PEAK_RSS_KIB = 1536 * 1024" in process_test,
        "real_process_fixture_has_bounded_resource_envelope",
        "the existing diagnostic series binds sampled PSS and Linux lifetime peak RSS tripwires",
    )
    require(
        '"metadata_only_regular_files"' in process_test
        and '"metadata_only_regular_file_logical_bytes"' in process_test
        and '"payload_mutation_work_bytes"' in process_test
        and '"local_peak_buffered_directory_component_batch_count"' in process_test
        and "== 4_096" in process_test,
        "real_process_fixture_requires_zero_payload_work_and_bounded_names",
        "excluded bytes remain metadata-only and the 4,097-entry directory crosses one 4,096-name batch",
    )
    require(
        "anonsync_sync_sparse_multiterabyte_selective_resources_process_test" in cmake
        and "test_anonsync_sparse_multiterabyte_selective_resources.py" in cmake
        and "LABELS \"product\"" in cmake
        and "anonsync_sync_sparse_multiterabyte_selective_resources_audit" in cmake,
        "cmake_registers_product_runtime_and_source_audit",
        "ordinary product and complete registry paths cannot omit the sparse gate",
    )
    require(
        "SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md" in verifier
        and "test_anonsync_sparse_multiterabyte_selective_resources.py" in verifier
        and "audit_sync_sparse_multiterabyte_selective_resources.py" in verifier
        and "rev1018_sparse_multiterabyte_selective_memory" in structural,
        "release_and_structural_policy_bind_sparse_surfaces",
        "the package cannot omit implementation, runtime, design, or focused audit",
    )
    prose = normalized("\n".join((design, notes, readme, bootstrap)))
    require(
        all(token in prose for token in (
            "4,399,120,252,928", "4,097", "4,096", "logical", "sparse",
            "metadata-only", "PSS", "peak RSS", "sampled", "million-file",
            "dense", "delta", "rename/move", "directories", "conflict",
            "Android", "ENOSPC", "Tor", "I2P",
        )),
        "benefit_and_nonclaims_are_explicit",
        "the sparse namespace result is not overstated as dense scale, complete memory, or product breadth",
    )
    require(
        "not allocated blocks" in design
        and "not a dense-media throughput claim" in design
        and "between-point transients" in design
        and "cgroup pressure" in design,
        "measurement_limits_are_named",
        "logical extent, sampled PSS, and kernel RSS high-water retain honest scopes",
    )
    require(
        all(token not in (design + notes + readme + bootstrap) for token in (
            "VALIDATION_PENDING_REV1018",
            "ARCHIVE_PENDING_REV1018",
            "CODENAME_PENDING_REV1018",
        )),
        "final_validation_and_release_cutpoint_are_sealed",
        "the source audit remains one deliberate preseal failure until publication facts are final",
    )
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "Source spelling is not semantic proof" in self_text
        and "Compiler, sanitizer, runtime" in self_text,
        "focused_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )
    require(
        "HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md" in readme
        and "SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md" in readme,
        "combined_revision_keeps_both_reviewed_moves_visible",
        "history-cold startup and real sparse measurement are one coherent revision",
    )
    require(
        "identity-preserving rename/move" in prose
        and "complete directory" in prose
        and "controlled ENOSPC" in prose,
        "next_product_edge_returns_to_file_semantics",
        "the memory gate does not become an excuse for another diagnostics-only cycle",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
