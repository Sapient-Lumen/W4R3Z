#!/usr/bin/env python3
"""Fail-closed structural audit for aggregate retained-evidence budgets."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sync_replica_model.hpp"),
    Path("src/sync_replica_model.cpp"),
    Path("src/sync_replica_operation_codec.cpp"),
    Path("src/sync_replica_operation_codec_internal.hpp"),
    Path("tests/sync_replica_aggregate_budget_test.cpp"),
    Path("tests/sync_replica_allocation_atomicity_test.cpp"),
    Path("tools/audit_sync_replica_aggregate_budget.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def function_body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    brace = text.find("{", start)
    if brace < 0:
        return ""
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-sync-replica-aggregate-budget-audit-v2",
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
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
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
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    header = text["src/sync_replica_model.hpp"]
    model = text["src/sync_replica_model.cpp"]
    codec = text["src/sync_replica_operation_codec.cpp"]
    internal = text["src/sync_replica_operation_codec_internal.hpp"]
    runtime_test = text["tests/sync_replica_aggregate_budget_test.cpp"]
    allocation_test = text["tests/sync_replica_allocation_atomicity_test.cpp"]
    cmake = text["CMakeLists.txt"]
    verifier = text["tools/verify_release_package.py"]

    limit_fields = (
        "max_retained_canonical_bytes",
        "max_retained_context_entries",
        "max_retained_predecessor_ids",
    )
    require(
        all(field in header for field in limit_fields),
        "three_independent_aggregate_limits_exist",
        "canonical bytes, context entries, and predecessor IDs have separate ceilings",
    )
    require(
        "256ULL * 1024ULL * 1024ULL" in header
        and header.count("1000000ULL") >= 2,
        "defaults_bound_retained_amplification",
        "default retained bytes and metadata cardinalities are finite",
    )
    require(
        all(
            f"limits.{aggregate} <\n        limits.{single}" in codec
            for aggregate, single in (
                ("max_retained_canonical_bytes", "max_canonical_operation_bytes"),
                ("max_retained_context_entries", "max_context_entries"),
                ("max_retained_predecessor_ids", "max_predecessor_ids"),
            )
        ),
        "aggregate_limits_admit_one_legal_envelope",
        "configuration cannot authorize an envelope that can never be retained",
    )
    require(
        "sync_replica_operation_canonical_size_or_throw" in header
        and "validate_operation_semantics_or_throw(operation, limits)" in codec,
        "exact_canonical_size_without_envelope_materialization",
        "budgeting reuses canonical semantic validation without constructing the encoded envelope",
    )
    require(
        "validate_sync_replica_operation_and_measure_or_throw" in internal
        and "sha256_hex(encode_after_semantic_validation_or_throw" in codec,
        "admission_validates_identity_and_measures_once",
        "remote and restore paths can obtain exact bytes from full identity validation",
    )

    restore_header = "restore_or_throw(\n        SyncReplicaDurableState durable"
    require(
        restore_header in header
        and "const SyncReplicaDurableState& durable" not in header,
        "restore_is_consumable_by_value",
        "rvalue durable snapshots avoid cloning the complete evidence graph",
    )
    restore = function_body(
        model, "SyncReplicaModel SyncReplicaModel::restore_or_throw(")
    require(
        "for (SyncReplicaOperation& operation : durable.operations)" in restore
        and "std::move(operation)" in restore
        and "std::move(durable.local_operation_ids)" in restore,
        "restore_moves_owned_graph_payloads",
        "operation vectors and local authority IDs transfer into the model",
    )
    require(
        ordered(
            restore,
            "validate_sync_replica_operation_and_measure_or_throw",
            "prospective_retained_totals_or_throw",
            "std::move(operation)",
            "project_sync_replica_evidence_or_throw",
            "restored.retained_canonical_bytes_ =",
        ),
        "restore_checks_budget_before_publication",
        "no over-budget durable prefix is published",
    )

    require(
        "checked_retained_total_or_throw" in model
        and "addition > limit - current" in model,
        "aggregate_addition_is_overflow_safe",
        "subtraction-based checks reject overflow and limit crossings",
    )
    require(
        all(
            f"{field}() const noexcept" in header
            for field in (
                "retained_canonical_bytes",
                "retained_context_entry_count",
                "retained_predecessor_id_count",
            )
        ),
        "exact_live_counters_are_observable",
        "tests and future persistence owners can attest aggregate charge",
    )

    local_admission = function_body(
        model, "SyncReplicaOperation SyncReplicaModel::create_local_operation_or_throw(")
    require(
        ordered(
            local_admission,
            "sync_replica_operation_canonical_size_or_throw",
            "prospective_retained_totals_or_throw",
            "evidence_by_id_.emplace",
            "project_sync_replica_evidence_or_throw",
            "retained_canonical_bytes_ =",
        ),
        "local_mint_preflights_then_commits_counters",
        "budget charge is computed before insertion and published after projection",
    )
    require(
        "catch (...)" in local_admission
        and "evidence_by_id_.erase(inserted.first);" in local_admission,
        "local_mint_rolls_back_inserted_evidence",
        "allocation/projection failure cannot leak a charged envelope",
    )

    remote_preflight = function_body(
        model,
        "SyncReplicaModel::preflight_remote_admission_or_throw(",
    )
    require(
        ordered(
            remote_preflight,
            "const auto duplicate",
            "SyncReplicaRemoteReadiness::Duplicate",
            "validate_sync_replica_operation_and_measure_or_throw",
            "retained_charge_or_throw",
            "resource_budget_or_throw",
            "SyncReplicaRemoteReadiness::CapacityBlocked",
        ),
        "exact_duplicate_bypasses_rehash_and_new_evidence_is_measured",
        "byte-identical replay reports zero charge while new evidence is fully validated before capacity classification",
    )
    remote_admission = function_body(
        model, "SyncReplicaAdmission SyncReplicaModel::accept_remote_or_throw(")
    require(
        ordered(
            remote_admission,
            "preflight_remote_admission_or_throw",
            "return SyncReplicaAdmission::Duplicate",
            "return SyncReplicaAdmission::CapacityBlocked",
            "accept_remote_admissible_after_preflight_or_throw",
        ),
        "remote_result_algebra_separates_capacity_from_validity",
        "duplicate and retryable local capacity return before evidence insertion",
    )
    remote_commit = function_body(
        model,
        "SyncReplicaModel::accept_remote_admissible_after_preflight_or_throw(",
    )
    require(
        ordered(
            remote_commit,
            "remote_preflight_is_capacity_blocked",
            "evidence_by_id_.emplace",
            "project_sync_replica_evidence_or_throw",
            "retained_canonical_bytes_ =",
        ),
        "admissible_remote_commit_rechecks_owner_then_publishes",
        "a stale owner plan cannot insert and exact counters publish after projection",
    )
    require(
        "catch (...)" in remote_commit
        and "evidence_by_id_.erase(inserted.first);" in remote_commit,
        "remote_admission_rolls_back_inserted_evidence",
        "all throwing projection cutpoints preserve prior aggregate counters",
    )

    require(
        all(token in runtime_test for token in (
            "InsertedActive",
            "InsertedPending",
            "InsertedQuarantined",
            "Duplicate",
            "CapacityBlocked",
            "SyncReplicaRemoteReadiness::CapacityBlocked",
            "restore_or_throw(\n            std::move(move_restore_state)",
            "aggregate canonical-byte ceiling",
            "aggregate context-entry ceiling",
            "aggregate predecessor-ID ceiling",
            "rejected local mint changed authority or aggregate counters",
        )),
        "runtime_test_covers_all_retained_states_and_boundaries",
        "active/pending/quarantine/duplicate, restore, and local rejection are executable",
    )
    require(
        all(token in allocation_test for token in (
            "baseline_counters.canonical_bytes",
            "retained_context_entry_count()",
            "retained_predecessor_id_count()",
            "exact duplicate replay allocated or changed retained evidence",
            "successful remote admission did not publish one active operation",
        )),
        "allocation_fault_sweep_attests_counters",
        "every injected bad_alloc cutpoint checks durable state and aggregate accounting",
    )

    target = "anonsync_sync_replica_aggregate_budget_test"
    require(
        cmake.count(target) >= 5
        and f"add_test(NAME {target}" in cmake,
        "runtime_test_is_built_registered_and_sanitized",
        "the focused proof participates in normal and sanitizer lanes",
    )
    require(
        "anonsync_sync_replica_aggregate_budget_source_audit" in cmake
        and "audit_sync_replica_aggregate_budget.py" in cmake
        and "${Python3_EXECUTABLE} -B -S" in cmake,
        "source_audit_is_hermetically_registered",
        "CTest executes the audit without site imports or bytecode writes",
    )
    require(
        "revision_number >= 867" in verifier
        and all(path in verifier for path in (
            "tests/sync_replica_aggregate_budget_test.cpp",
            "tools/audit_sync_replica_aggregate_budget.py",
        )),
        "release_verifier_requires_rev0867_boundary",
        "future packages cannot omit this implementation proof",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
