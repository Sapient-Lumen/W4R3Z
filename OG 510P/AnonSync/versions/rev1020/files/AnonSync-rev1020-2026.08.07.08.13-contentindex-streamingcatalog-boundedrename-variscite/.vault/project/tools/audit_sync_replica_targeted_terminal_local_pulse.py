#!/usr/bin/env python3
"""Lexical hygiene audit for rev1005 targeted terminal verification.

Source spelling is not semantic proof. Compiler, sanitizer, runtime, stress,
reconstruction, and package evidence remain load-bearing.
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
    Path("TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md"),
    Path("REVISION_NOTES_rev1005.md"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("src/anonsync_sync.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_reconciliation_service_test.cpp"),
    Path("tools/test_anonsync_replica_reconciliation_process.py"),
    Path("tools/audit_sync_replica_terminal_verification_continuation.py"),
    Path("tools/audit_sync_file_payload_store.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    opening = text.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [item.check_id for item in checks if not item.passed]
    report = {
        "format": "anonsync-targeted-terminal-local-pulse-audit-v1",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling does not prove inode identity, bounded byte work, "
            "crash recovery, scheduler fairness, SHA-256 authority, route "
            "performance, sanitizer cleanliness, or package identity"
        ),
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(item) for item in checks],
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
    candidates = (root.parent.parent / "BOOTSTRAPROSE.md", root.parent / "BOOTSTRAPROSE.md")
    bootstrap_path = next((path for path in candidates if path.is_file()), None)
    require(bootstrap_path is not None, "release_root_bootstrap_exists", str(candidates))
    if missing or bootstrap_path is None:
        return emit(root, args.json, checks)

    texts = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    store_h = texts["src/sync_replica_file_payload_store.hpp"]
    store_c = texts["src/sync_replica_file_payload_store.cpp"]
    service_h = texts["src/sync_replica_reconciliation_service.hpp"]
    service_c = texts["src/sync_replica_reconciliation_service.cpp"]
    tls_h = texts["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls_c = texts["src/sync_replica_reconciliation_tls_exchange.cpp"]
    store_test = texts["tests/sync_replica_file_payload_store_test.cpp"]
    service_test = texts["tests/sync_replica_reconciliation_service_test.cpp"]
    process_test = texts["tools/test_anonsync_replica_reconciliation_process.py"]
    cmake = texts["CMakeLists.txt"]
    verifier = texts["tools/verify_release_package.py"]
    structural = texts["tools/audit_sync_file_payload_store.py"]
    prose = "\n".join((
        texts["TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md"],
        texts["REVISION_NOTES_rev1005.md"], texts["README.md"], bootstrap,
    ))

    targeted = body(store_c, "observe_staged_prefix_terminal_target_under_lease_or_throw(")
    stage = body(store_c, "SyncReplicaFilePayloadStore::stage_payload_prefix_impl_or_throw(")
    apply = body(service_c, "SyncReplicaReconciliationService::apply_response_or_throw(")

    require(bool(targeted), "targeted_observer_exists", "exact terminal observer is retained")
    require(
        "ExclusiveMutation" in targeted and "pre-observation lease proof" in targeted
        and "final observation lease proof" in targeted,
        "targeted_observer_is_store_writer_fenced",
        "intermediate computation remains inside the shared store lease protocol",
    )
    require(
        "reopen_matching_root_authority_or_throw" in targeted
        and "duplicate_shared_open_description_or_throw" in targeted,
        "targeted_observer_reopens_independent_root_authority",
        "the retained descriptor is not trusted by pathname alone",
    )
    require(
        "observe_terminal_verification_state_file_or_throw" in targeted
        and "exact completed prefix" in targeted
        and "exact durable payload name" in targeted,
        "targeted_observer_opens_only_exact_terminal_names",
        "journal, completed prefix, and digest name are explicit",
    )
    require(
        "readdir" not in targeted and "fdopendir" not in targeted
        and "scan_store_under_lease_or_throw" not in targeted,
        "intermediate_observer_does_not_enumerate_payload_namespace",
        "unrelated payload count no longer multiplies every SHA checkpoint",
    )
    require(
        "initial root fstat failed" in targeted and "final root fstat failed" in targeted
        and "payload root changed during exact terminal observation" in targeted,
        "targeted_observer_brackets_exact_names_with_root_identity",
        "namespace drift remains fail closed without enumeration",
    )
    require(
        "verify_named_regular_file_or_throw" in targeted
        and "require_private_regular_file_or_throw" in targeted
        and "same_directory_observation" in targeted,
        "targeted_observer_reproves_file_shape_path_and_root",
        "exact names remain bound to private regular inodes",
    )
    require(
        "scan_store_under_lease_or_throw" in stage
        and stage.find("scan_store_under_lease_or_throw") < stage.find("rename_noreplace_at_or_throw"),
        "final_publication_retains_complete_store_scan",
        "targeted progress never becomes namespace or publication authority",
    )
    require(
        "stage_payload_prefix_deferring_terminal_verification_or_throw" in store_h
        and "defer_terminal_verification" in stage
        and "deferred terminal verification final lease cutpoint" in stage,
        "deferred_terminal_range_api_is_explicit_and_narrow",
        "authenticated bytes can settle without silently consuming an extra hash step",
    )
    require(
        "terminal_verification_steps" in store_h
        and "terminal_verification_only && defer_terminal_verification" in stage,
        "store_result_and_entry_modes_are_mechanically_distinct",
        "source-byte-free continuation cannot be confused with deferred range staging",
    )
    require(
        "kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply = 32U" in service_h
        and "max_terminal_verification_steps_per_apply_ == 0U" in service_c,
        "service_frontier_is_nonzero_bounded_and_configurable_for_tests",
        "shipping pulse is 32 fixed steps and invalid frontiers fail construction",
    )
    require(
        "continue_terminal_verification_locally_or_throw" in apply
        and "terminal_verification_steps_spent" in apply
        and "terminal_verification_step_budget_exhaustions" in apply,
        "apply_runs_and_accounts_receiver_local_pulse",
        "local progress is visible and bounded per authenticated apply",
    )
    require(
        "stage_payload_prefix_deferring_terminal_verification_or_throw" in apply
        and "crossed its per-apply step budget" in apply,
        "all_range_paths_respect_exact_terminal_step_frontier",
        "multi-file pages cannot smuggle one automatic hash step per file",
    )
    require(
        all(token in tls_h + tls_c for token in (
            "terminal_verification_steps",
            "terminal_verification_local_continuation_steps",
            "terminal_verification_step_budget_exhaustions",
        )),
        "tls_aggregation_retains_terminal_pulse_accounting",
        "operator-visible totals survive multi-page exchange",
    )
    require(
        all(token in texts["src/anonsync_sync.cpp"] + texts["src/anonsync_replica.cpp"] for token in (
            "terminal_verification_steps",
            "terminal_verification_local_continuation_steps",
            "terminal_verification_step_budget_exhaustions",
        )),
        "shipping_cli_json_exposes_terminal_pulse_accounting",
        "the bounded-work behavior is diagnosable",
    )
    require(
        "test_targeted_terminal_continuation_defers_namespace_reproof" in store_test
        and "test_deferred_terminal_verification_preserves_exact_prefix" in store_test,
        "payload_store_runtime_covers_targeted_and_deferred_paths",
        "unexpected namespace and zero-step deferred staging have direct regressions",
    )
    require(
        "test_terminal_verification_step_budget_yields_exact_continuation" in service_test
        and "terminal_verification_step_budget_exhaustions == 1U" in service_test
        and "terminal-verification frontier above the shipping maximum" in service_test,
        "service_runtime_covers_yield_completion_and_constructor_bounds",
        "a one-step pulse proves exact continuation across applies",
    )
    require(
        "--after-operation-id" in process_test
        and "terminal_verification_steps" in process_test
        and "payload continuation" in process_test.lower()
        and "1024" in process_test,
        "process_oracle_proves_small_payload_cold_cursor_confirmation",
        "the source is not reopened after receiver publication",
    )
    require(
        "anonsync_sync_replica_targeted_terminal_local_pulse_source_audit" in cmake
        and "TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md" in verifier
        and "REVISION_NOTES_rev1005.md" in verifier
        and "rev1005" in structural,
        "release_policy_binds_complete_rev1005_slice",
        "implementation, tests, prose, focused audit, and structural integration are mandatory",
    )
    normalized = " ".join(prose.replace("**", "").split())
    require(
        all(token in normalized for token in (
            "1 GiB", "4 TiB", "4,096", "complete final scan",
            "source-side target-manifest", "background receiver-local scheduler",
        )),
        "scale_boundary_and_next_scheduler_nonclaim_are_explicit",
        "rev1005 is not overstated as complete multi-terabyte qualification",
    )
    require(
        all(token not in prose for token in (
            "VALIDATION_PENDING_REV1005", "ARCHIVE_PENDING_REV1005", "CODENAME_PENDING_REV1005",
        )),
        "final_release_placeholders_are_sealed",
        "the final focused audit cannot pass before publication facts exist",
    )
    self_text = Path(__file__).read_text(encoding="utf-8")
    require(
        "lexical-hygiene-not-semantic-proof" in self_text
        and "Source spelling is not semantic proof" in self_text
        and "Compiler, sanitizer, runtime" in self_text,
        "lexical_audit_disclaims_semantic_authority",
        "runtime and package evidence remain load-bearing",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
