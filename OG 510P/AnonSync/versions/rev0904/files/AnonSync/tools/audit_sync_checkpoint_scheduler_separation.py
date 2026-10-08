#!/usr/bin/env python3
"""Enforce checkpoint scheduler policy, execution, and terminal-review fences."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PLANNER = "plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass"
EXECUTOR = "execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass"
POLICY = "plan_resume_transfer_workorder_actions"


def source_list_block(cmake: str, variable: str) -> str:
    match = re.search(rf"set\({re.escape(variable)}\s+(.*?)\)", cmake, re.DOTALL)
    return match.group(1) if match else ""


def definition_owners(root: Path, name: str) -> list[str]:
    pattern = re.compile(
        rf"\bSyncValidationResult\s+{re.escape(name)}\s*\([^;{{}}]*\)\s*\{{",
        re.DOTALL,
    )
    owners: list[str] = []
    for path in sorted((root / "src").rglob("*.cpp")):
        text = path.read_text(errors="replace")
        if pattern.search(text):
            owners.append(path.relative_to(root).as_posix())
    return owners


def include_users(root: Path, header: str) -> list[str]:
    users: list[str] = []
    include = f'#include "{header}"'
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".cpp", ".cc", ".h", ".hpp"}:
            continue
        if any(part.startswith("build") for part in path.relative_to(root).parts):
            continue
        if include in path.read_text(errors="replace"):
            users.append(path.relative_to(root).as_posix())
    return users


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    cmake = (root / "CMakeLists.txt").read_text()
    public_header = (root / "include/anonsync_core.hpp").read_text()
    domain = (root / "src/sync_domain.cpp").read_text()
    scheduler = (root / "src/sync_checkpoint_scheduler.cpp").read_text()
    policy = (root / "src/sync_checkpoint_scheduler_policy.cpp").read_text()
    policy_header = (root / "src/sync_checkpoint_scheduler_policy.hpp").read_text()
    internal_header = (root / "src/sync_checkpoint_resume_internal.hpp").read_text()
    selftests = (root / "src/sync_domain_selftests.cpp").read_text()
    focused_test = (root / "tests/sync_checkpoint_scheduler_policy_test.cpp").read_text()
    operator_cli = (root / "src/sync_operator_cli.cpp").read_text()

    checks: list[dict[str, object]] = []

    def check(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(passed), "detail": detail})

    planner_owners = definition_owners(root, PLANNER)
    executor_owners = definition_owners(root, EXECUTOR)
    policy_owners = definition_owners(root, POLICY)
    check(
        "scheduler_translation_unit_owns_public_planner_and_executor",
        planner_owners == ["src/sync_checkpoint_scheduler.cpp"]
        and executor_owners == ["src/sync_checkpoint_scheduler.cpp"],
        f"planner={planner_owners} executor={executor_owners}",
    )
    domain_public_definition_pattern = re.compile(
        rf"\bSyncValidationResult\s+(?:{re.escape(PLANNER)}|{re.escape(EXECUTOR)})"
        r"\s*\([^;{}]*\)\s*\{",
        re.DOTALL,
    )
    check(
        "domain_monolith_no_longer_defines_scheduler_entry_points",
        domain_public_definition_pattern.search(domain) is None,
        f"domain_lines={len(domain.splitlines())}",
    )
    check(
        "pure_policy_has_one_definition_owner",
        policy_owners == ["src/sync_checkpoint_scheduler_policy.cpp"],
        f"policy owners={policy_owners}",
    )

    core_sources = source_list_block(cmake, "ANONSYNC_CORE_SOURCES")
    check(
        "cmake_places_executor_in_core_and_policy_outside_core",
        "src/sync_checkpoint_scheduler.cpp" in core_sources
        and "src/sync_checkpoint_scheduler_policy.cpp" not in core_sources
        and "add_library(anonsync_sync_checkpoint_scheduler_policy STATIC" in cmake
        and "${ANONSYNC_SYNC_CHECKPOINT_SCHEDULER_POLICY_SOURCE}" in cmake,
        "executor is runtime-owned; policy has a dedicated static owner",
    )
    core_link_start = cmake.find("target_link_libraries(anonsync_core_lib")
    core_link_end = cmake.find("\nif(ANONSYNC_USE_BUNDLED_SQLITE)", core_link_start)
    core_links = cmake[core_link_start:core_link_end] if core_link_start >= 0 else ""
    policy_link_pattern = re.compile(
        r"target_link_libraries\(anonsync_sync_checkpoint_scheduler_policy\b(.*?)\)",
        re.DOTALL,
    )
    policy_link = policy_link_pattern.search(cmake)
    check(
        "dependency_direction_is_runtime_to_pure_policy_only",
        "anonsync_sync_checkpoint_scheduler_policy" in core_links
        and (policy_link is None or "anonsync_core_lib" not in policy_link.group(1)),
        "anonsync_core_lib -> scheduler policy; policy does not link runtime",
    )

    forbidden_policy_tokens = [
        "sqlite3", "std::filesystem", "<filesystem>", "<fstream>",
        "openssl", "sha256_hex", "sync_domain", "select_sync_session",
        "claim_sync_session", "execute_sync_session", "std::chrono",
    ]
    present_forbidden = [token for token in forbidden_policy_tokens if token in policy.lower()]
    check(
        "policy_is_free_of_io_crypto_clock_and_mutator_dependencies",
        not present_forbidden,
        f"forbidden tokens present={present_forbidden}",
    )

    validate_position = policy.find("validate_queue_fact_or_throw(fact)")
    blueprint_position = policy.find("action_blueprint_or_throw(fact.queue_kind)")
    action_position = policy.find("make_action(fact, blueprint)")
    check(
        "fact_relationships_are_validated_before_action_authority",
        0 <= validate_position < blueprint_position < action_position,
        f"positions validate={validate_position} blueprint={blueprint_position} action={action_position}",
    )
    relationship_tokens = [
        "terminal-review evidence disagrees with queue kind",
        "owned ready claim lacks live matching ownership evidence",
        "expired mutation lacks expired open-retry evidence",
        "chunk range overflows uint64 authority",
        "request-key authority is malformed",
        "execution-key authority is malformed",
        "worker-lease authority is malformed",
        "if (!mutating_queue_kind(fact.queue_kind)) return;",
    ]
    check(
        "policy_binds_state_lease_review_chunk_and_mutation_key_evidence",
        all(token in policy for token in relationship_tokens),
        "queue enum alone cannot mint mutation authority; hostile terminal evidence remains reviewable",
    )
    check(
        "policy_orders_review_before_mutation_and_enforces_priority_barrier",
        "TerminalReview = 0" in policy
        and "Mutating = 1" in policy
        and "PassiveObservation = 2" in policy
        and "CompletedObservation = 3" in policy
        and "std::stable_sort" in policy
        and "deferred_priority_barrier" in policy
        and "blocked_by_higher_priority" in policy,
        "priority classes and deferred-class barrier are explicit",
    )
    check(
        "policy_preserves_atomic_mutation_groups_and_singleton_observations",
        "mutation_group_index" in policy
        and "fact.execution_idempotency_key" in policy
        and "Observations carry no mutation atomicity" in policy
        and "group.actions.push_back" in policy,
        "mutations group by execution authority; reviews/observations stay singleton",
    )

    queue_position = scheduler.find(
        "select_sync_session_checkpoint_resume_transfer_workorder_queue")
    policy_call_position = scheduler.find(
        "sync_checkpoint_scheduler_policy::plan_resume_transfer_workorder_actions")
    check(
        "planner_loads_durable_queue_then_calls_policy_once",
        0 <= queue_position < policy_call_position
        and scheduler.count(
            "sync_checkpoint_scheduler_policy::plan_resume_transfer_workorder_actions") == 1,
        f"queue_position={queue_position} policy_position={policy_call_position}",
    )

    policy_users = include_users(root, "sync_checkpoint_scheduler_policy.hpp")
    internal_users = include_users(root, "sync_checkpoint_resume_internal.hpp")
    check(
        "private_scheduler_headers_have_exact_include_users",
        policy_users == [
            "src/sync_checkpoint_scheduler.cpp",
            "src/sync_checkpoint_scheduler_policy.cpp",
            "tests/sync_checkpoint_scheduler_policy_test.cpp",
        ]
        and internal_users == [
            "src/sync_checkpoint_scheduler.cpp",
            "src/sync_domain.cpp",
        ]
        and not (root / "include/sync_checkpoint_scheduler_policy.hpp").exists()
        and not (root / "include/sync_checkpoint_resume_internal.hpp").exists(),
        f"policy users={policy_users} internal users={internal_users}",
    )
    helper_names = [
        "checkpoint_resume_transfer_worker_lease_id_or_throw",
        "unique_resume_transfer_execution_keys_or_throw",
    ]
    helper_definition_patterns = [
        re.compile(
            rf"\b(?:std::string|std::vector<std::string>)\s+{re.escape(name)}"
            r"\s*\([^;{}]*\)\s*\{",
            re.DOTALL,
        )
        for name in helper_names
    ]
    check(
        "shared_resume_helpers_have_one_source_private_owner",
        all(name in internal_header for name in helper_names)
        and all(pattern.search(domain) is None for pattern in helper_definition_patterns)
        and "namespace anonsync::sync_checkpoint_internal" in internal_header,
        "lease/key helper definitions moved from the monolith into one private seam",
    )

    fence_position = scheduler.find("block_mutations_for_terminal_review")
    key_push_position = min(
        pos for pos in [
            scheduler.find("execute_keys.push_back"),
            scheduler.find("claim_or_abandon_keys.push_back"),
        ] if pos >= 0
    )
    key_filter_position = scheduler.find("unique_resume_transfer_execution_keys_or_throw")
    claim_mutator_position = scheduler.find(
        "claim_sync_session_checkpoint_resume_transfer_workorders")
    execute_mutator_position = scheduler.find(
        "execute_sync_session_checkpoint_resume_transfer_workorders")
    check(
        "terminal_review_fence_precedes_keys_and_mutators",
        0 <= fence_position < key_push_position < key_filter_position
        < claim_mutator_position < execute_mutator_position
        and "if (block_mutations_for_terminal_review)" in scheduler
        and "mutating_actions_blocked_by_terminal_review" in scheduler,
        "terminal review is evaluated before execution-key filters and both mutation paths",
    )
    public_fence_tokens = [
        "bool block_mutating_actions_on_terminal_review = true;",
        "bool terminal_review_present = false;",
        "bool mutations_blocked_by_terminal_review = false;",
        "mutating_action_groups_blocked_by_terminal_review",
        "mutating_actions_blocked_by_terminal_review",
    ]
    check(
        "public_options_default_safe_and_report_fence_evidence",
        all(token in public_header for token in public_fence_tokens),
        "default-on option and explicit result counters are public",
    )
    check(
        "daemon_wires_stop_policy_to_pre_mutation_fence",
        "pass_options.block_mutating_actions_on_terminal_review =" in domain
        and "options.stop_on_terminal_review" in domain
        and "const bool terminal_review_observed" in domain
        and "const bool terminal_review_fenced" in domain
        and "out.stopped_on_terminal_review = true" in domain,
        "daemon stop-on-review now controls executor authority before post-pass stop",
    )
    daemon_evidence_tokens = [
        "out.mutations_blocked_by_terminal_review ||",
        "pass_result.mutating_action_groups_blocked_by_terminal_review",
        "pass_result.mutating_actions_blocked_by_terminal_review",
        "scheduler-pass-terminal-review-fenced",
    ]
    cli_evidence_tokens = [
        "terminal_review_actions_observed",
        "mutations_blocked_by_terminal_review",
        "mutating_action_groups_blocked_by_terminal_review",
        "mutating_actions_blocked_by_terminal_review",
    ]
    check(
        "daemon_heartbeat_and_cli_preserve_fence_evidence",
        all(token in domain for token in daemon_evidence_tokens)
        and all(token in operator_cli for token in cli_evidence_tokens),
        "aggregate, heartbeat state, and JSON report expose the safety decision",
    )

    integration_tokens = [
        "quarantine_scheduler_fence_checkpoint_db",
        "quarantine_daemon_fence_checkpoint_db",
        "scheduler terminal-review fence blocks every selected mutation",
        "pre-mutation fence rather than a post-mutation stop condition",
        "work_state='claimed'",
        "work_state='quarantined'",
    ]
    check(
        "domain_corpus_reproduces_and_locks_in_terminal_review_fence",
        all(token in selftests for token in integration_tokens),
        "hostile durable row plus runnable claims are checked at executor and daemon layers",
    )
    focused_tokens = [
        "permutations == 40320",
        "test_atomic_groups_and_priority_barrier",
        "test_terminal_review_preserves_hostile_evidence",
        "test_inconsistent_authority_rejections",
        "runnable enum with quarantined state was not rejected",
    ]
    check(
        "focused_policy_test_is_exhaustive_and_hostile",
        all(token in focused_test for token in focused_tokens)
        and "anonsync_sync_checkpoint_scheduler_policy_test" in cmake,
        "8! orderings, limits, groups, and inconsistent facts are independently tested",
    )

    sanitizer_block = source_list_block(cmake, "ANONSYNC_SANITIZER_COMPILE_TARGETS")
    check(
        "sanitizer_target_graph_avoids_interface_target_and_covers_new_owner",
        "anonsync_selftests_lib" not in sanitizer_block
        and "anonsync_reporting_selftests_lib" in sanitizer_block
        and "anonsync_sync_domain_selftests_lib" in sanitizer_block
        and "anonsync_sync_checkpoint_scheduler_policy" in sanitizer_block
        and "anonsync_sync_checkpoint_scheduler_policy_test" in sanitizer_block,
        "PRIVATE sanitizer flags are applied only to concrete targets",
    )
    check(
        "source_audit_and_focused_test_are_release_gate_obligations",
        "add_test(NAME anonsync_sync_checkpoint_scheduler_policy_test" in cmake
        and "add_test(NAME anonsync_sync_checkpoint_scheduler_separation_audit" in cmake
        and "tools/audit_sync_checkpoint_scheduler_separation.py" in cmake,
        "CTest registers both executable behavior and source ownership",
    )
    check(
        "runtime_monolith_shrank_without_reabsorbing_policy",
        len(domain.splitlines()) < 15400
        and len(scheduler.splitlines()) > 400
        and len(policy.splitlines()) > 350
        and "sync_checkpoint_scheduler_policy.hpp" not in public_header
        and "sync_checkpoint_resume_internal.hpp" not in public_header,
        f"domain={len(domain.splitlines())} scheduler={len(scheduler.splitlines())} policy={len(policy.splitlines())}",
    )

    result = {
        "format": "anonsync-sync-checkpoint-scheduler-separation-audit-v1",
        "planner_definition_owners": planner_owners,
        "executor_definition_owners": executor_owners,
        "policy_definition_owners": policy_owners,
        "domain_lines": len(domain.splitlines()),
        "scheduler_lines": len(scheduler.splitlines()),
        "policy_lines": len(policy.splitlines()),
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
