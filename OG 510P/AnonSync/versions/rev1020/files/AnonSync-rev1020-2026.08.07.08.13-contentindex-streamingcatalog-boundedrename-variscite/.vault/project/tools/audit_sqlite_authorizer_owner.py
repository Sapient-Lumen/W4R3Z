#!/usr/bin/env python3
"""Audit SQLite authorizer callback, policy-context, and close ordering."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}


@dataclass(frozen=True)
class Check:
    check_id: str
    detail: str
    passed: bool


def add(checks: list[Check], condition: bool, check_id: str, detail: str) -> None:
    checks.append(Check(check_id, detail, bool(condition)))


def ordered(text: str, *tokens: str) -> bool:
    position = -1
    for token in tokens:
        position = text.find(token, position + 1)
        if position < 0:
            return False
    return True


def cpp_code_only(text: str) -> str:
    """Replace comments and literals before lexical authority inventory."""
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
                state = "line"
                continue
            if ch == "/" and nxt == "*":
                out.extend("  ")
                i += 2
                state = "block"
                continue
            if ch in {'"', "'"}:
                quote = ch
                out.append(" ")
                i += 1
                state = "literal"
                continue
            out.append(ch)
            i += 1
            continue
        if state == "line":
            out.append("\n" if ch == "\n" else " ")
            if ch == "\n":
                state = "code"
            i += 1
            continue
        if state == "block":
            if ch == "*" and nxt == "/":
                out.extend("  ")
                i += 2
                state = "code"
                continue
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue
        if ch == "\\":
            out.append(" ")
            i += 1
            if i < len(text):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1
            continue
        if ch == quote:
            out.append(" ")
            i += 1
            state = "code"
            continue
        out.append("\n" if ch == "\n" else " ")
        i += 1
    return "".join(out)


def call_inventory(root: Path, symbol: str) -> dict[str, int]:
    pattern = re.compile(rf"\b{re.escape(symbol)}\s*\(")
    result: dict[str, int] = {}
    for path in sorted((root / "src").rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        count = len(pattern.findall(cpp_code_only(path.read_text(encoding="utf-8"))))
        if count:
            result[path.relative_to(root).as_posix()] = count
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    paths = {
        "cmake": Path("CMakeLists.txt"),
        "claim_header": Path("src/persistence/sqlite_retained_callback_claim.hpp"),
        "claim_owner": Path("src/persistence/sqlite_retained_callback_claim.cpp"),
        "callback_slots": Path("src/persistence/sqlite_retained_callback_slots.hpp"),
        "raw_header": Path("src/persistence/sqlite_authorizer_owner.hpp"),
        "raw_owner": Path("src/persistence/sqlite_authorizer_owner.cpp"),
        "policy_header": Path("src/sync_sqlite_owned_authorizer_policy.hpp"),
        "policy_owner": Path("src/sync_sqlite_owned_authorizer_policy.cpp"),
        "authority_header": Path("src/sync_sqlite_connection_authority.hpp"),
        "authority": Path("src/sync_sqlite_connection_authority.cpp"),
        "authority_internal": Path("src/sync_sqlite_connection_authority_internal.hpp"),
        "handle_slot": Path("src/sync_sqlite_handle_slot.cpp"),
        "schema": Path("src/sync_peer_ingress_schema.cpp"),
        "raw_test": Path("tests/persistence/sqlite_authorizer_owner_tests.cpp"),
        "policy_test": Path("tests/sqlite_owned_authorizer_policy_test.cpp"),
        "authority_test": Path("tests/sqlite_connection_authority_test.cpp"),
        "transaction_test": Path("tests/sqlite_transaction_exception_composition_test.cpp"),
        "verifier": Path("tools/verify_release_package.py"),
    }
    missing = [path.as_posix() for path in paths.values() if not (root / path).is_file()]
    if missing:
        payload = {
            "format": "anonsync-sqlite-authorizer-owner-audit-v4",
            "passed": False,
            "missing": sorted(missing),
        }
        rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    text = {
        name: (root / path).read_text(encoding="utf-8")
        for name, path in paths.items()
    }
    cmake = text["cmake"]
    claim_header = text["claim_header"]
    claim_owner = text["claim_owner"]
    callback_slots = text["callback_slots"]
    raw_header = text["raw_header"]
    raw_owner = text["raw_owner"]
    policy_header = text["policy_header"]
    policy_owner = text["policy_owner"]
    authority_header = text["authority_header"]
    authority = text["authority"]
    authority_internal = text["authority_internal"]
    handle_slot = text["handle_slot"]
    schema = text["schema"]
    raw_test = text["raw_test"]
    policy_test = text["policy_test"]
    authority_test = text["authority_test"]
    transaction_test = text["transaction_test"]
    verifier = text["verifier"]

    sanitizer_block = cmake.split(
        'if(ANONSYNC_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")',
        1,
    )[1].split("include(CTest)", 1)[0]
    sanitizer_compile_targets = sanitizer_block.split(
        "set(ANONSYNC_SANITIZER_COMPILE_TARGETS", 1
    )[1].split("\n  if(TARGET", 1)[0]
    sanitizer_link_targets = sanitizer_block.split(
        "  foreach(tgt\n      anonsync_core", 1
    )[1].split("\n    target_link_options(${tgt}", 1)[0]
    authorizer_calls = call_inventory(root, "sqlite3_set_authorizer")
    checks: list[Check] = []

    support_links = cmake.split(
        "target_link_libraries(anonsync_sqlite_support", 1
    )[1].split("target_compile_options(anonsync_sqlite_support", 1)[0]

    add(
        checks,
        "add_library(anonsync_sqlite_authorizer_owner STATIC" in cmake
        and "add_library(anonsync_sqlite_owned_authorizer_policy STATIC" in cmake
        and "anonsync_sqlite_database_mutex_guard" in cmake.split(
            "target_link_libraries(anonsync_sqlite_authorizer_owner PUBLIC", 1
        )[1].split("target_compile_options", 1)[0]
        and "anonsync_sqlite_authorizer_owner" in support_links
        and "anonsync_sqlite_owned_authorizer_policy" in support_links,
        "owners_are_independent_support_dependencies",
        "raw SQLite callback ownership and application policy ownership are separately linkable",
    )
    add(
        checks,
        all(
            token in cmake
            for token in (
                "anonsync_sqlite_authorizer_owner_test",
                "anonsync_sqlite_owned_authorizer_policy_test",
                "anonsync_sqlite_authorizer_owner_source_audit",
            )
        ),
        "focused_tests_and_composed_audit_are_registered",
        "one existing structural audit covers both retained callback and policy-context ownership",
    )
    add(
        checks,
        all(
            target in sanitizer_compile_targets
            for target in (
                "anonsync_sqlite_authorizer_owner",
                "anonsync_sqlite_authorizer_owner_test",
                "anonsync_sqlite_owned_authorizer_policy",
                "anonsync_sqlite_owned_authorizer_policy_test",
                "anonsync_sqlite_connection_authority_test",
            )
        )
        and all(
            target in sanitizer_link_targets
            for target in (
                "anonsync_sqlite_authorizer_owner_test",
                "anonsync_sqlite_owned_authorizer_policy_test",
                "anonsync_sqlite_connection_authority_test",
            )
        ),
        "owners_and_consumers_are_in_sanitizer_graph",
        "ASan+UBSan instruments both focused owners and the integrated authority corpus",
    )
    add(
        checks,
        all(
            token in verifier
            for token in (
                '"src/persistence/sqlite_authorizer_owner.hpp"',
                '"src/persistence/sqlite_authorizer_owner.cpp"',
                '"tests/persistence/sqlite_authorizer_owner_tests.cpp"',
                '"src/sync_sqlite_owned_authorizer_policy.hpp"',
                '"src/sync_sqlite_owned_authorizer_policy.cpp"',
                '"tests/sqlite_owned_authorizer_policy_test.cpp"',
                '"tests/sqlite_connection_authority_test.cpp"',
                '"tests/sqlite_transaction_exception_composition_test.cpp"',
                '"tools/audit_sqlite_authorizer_owner.py"',
                "revision_number >= 850",
                "revision_number >= 851",
                "revision_number >= 852",
            )
        ),
        "release_verifier_requires_all_authorizer_revision_boundaries",
        "rev0850 owns the raw callback, rev0851 owns policy lifetime, and rev0852 binds typed consumers",
    )
    add(
        checks,
        authorizer_calls == {"src/persistence/sqlite_authorizer_owner.cpp": 3},
        "all_production_authorizer_setters_are_owner_confined",
        f"inventory={authorizer_calls}",
    )
    add(
        checks,
        "sqlite3_set_authorizer(" not in cpp_code_only(authority),
        "connection_authority_has_no_raw_setter",
        "the integrated state machine consumes the focused callback owner",
    )

    add(
        checks,
        all(
            token in raw_header
            for token in (
                "class SqliteAuthorizerOwner final",
                "SqliteAuthorizerOwner(const SqliteAuthorizerOwner&) = delete",
                "SqliteAuthorizerOwner(SqliteAuthorizerOwner&&) = delete",
                "SqliteRetainedCallbackClaim callback_claim_",
                "sqlite3* database_ = nullptr",
                "void* callback_context_ = nullptr",
            )
        ),
        "raw_owner_address_and_context_shape_are_stable",
        "SQLite's retained bridge context cannot move while the callback is installed",
    )
    add(
        checks,
        "current_sync_process_incarnation_noexcept()" in raw_owner
        and "sync_process_incarnation_is_current(process_id_)" in raw_owner
        and "fail_stop_on_sync_process_capability_violation_noexcept()" in raw_owner,
        "raw_owner_is_process_incarnation_bound",
        "inherited access, detach, or destruction cannot touch copied SQLite state",
    )
    add(
        checks,
        re.search(
            r"database\s*==\s*nullptr\s*\|\|\s*"
            r"callback\s*==\s*nullptr\s*\|\|\s*"
            r"callback_context\s*==\s*nullptr",
            raw_owner,
        )
        is not None
        and "label.empty()" in raw_owner,
        "raw_owner_rejects_ambient_inputs",
        "a callback, stable bridge context, connection, and diagnostic identity are mandatory",
    )
    add(
        checks,
        ordered(
            raw_owner,
            "void SqliteAuthorizerOwner::attach(",
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.attach(database",
            "mutation_guard",
            "sqlite3_set_authorizer(database, callback, callback_context)",
            "callback_claim_.detach(database, mutation_guard)",
            "database_ = database",
        ),
        "raw_attach_claims_lifetime_before_callback_publication",
        "registration failure consumes the named claim before the owner can appear live",
    )
    add(
        checks,
        ordered(
            raw_owner,
            "void SqliteAuthorizerOwner::replace(",
            "database_ != database",
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.require_live(database, mutation_guard)",
            "sqlite3_set_authorizer(database, callback, callback_context)",
            "callback_ = callback",
        ),
        "raw_replacement_requires_exact_live_connection",
        "deliberate supersession cannot cross a connection or abandon the claim",
    )
    add(
        checks,
        ordered(
            raw_owner,
            "void SqliteAuthorizerOwner::detach(",
            "SyncSqliteDatabaseMutexGuard mutation_guard(",
            "callback_claim_.require_live(database, mutation_guard)",
            "sqlite3_set_authorizer(database, nullptr, nullptr)",
            "callback_claim_.detach(database, mutation_guard)",
            "database_ = nullptr",
        ),
        "raw_detach_revokes_callback_before_claim",
        "SQLite loses the callback address before its independent sentinel is consumed",
    )
    add(
        checks,
        '"anonsync.sqlite.authorizer-owner.v1"' in callback_slots
        and "kSqliteAuthorizerOwnerClientDataName" in raw_owner
        and "registration_pending = 0" in claim_owner
        and "live = 1" in claim_owner
        and "detaching = 2" in claim_owner
        and "thread_local void* g_authorized_retained_claim_destruction" in claim_owner
        and "class SqliteRetainedCallbackClaim final" in claim_header
        and claim_header.count(
            "const SyncSqliteDatabaseMutexGuard& mutex_guard") == 3
        and claim_owner.count("mutex_guard.authorizes(database)") == 2,
        "shared_claim_has_state_and_exact_thread_witness",
        "close/replacement destruction is authorized only by reviewed synchronous calls",
    )
    add(
        checks,
        "test_concurrent_duplicate_owners_reject_without_fail_stop" in raw_test
        and "kIterations = 64" in raw_test
        and "one live owner and one recoverable rejection" in raw_test
        and "claim_is_live" in raw_test
        and "callback_calls == 0U" in raw_test,
        "concurrent_authorizer_attachment_has_runtime_oracle",
        "simultaneous legitimate attach attempts leave one callable owner and one ordinary rejection without claim loss",
    )

    policy_code = cpp_code_only(policy_header + "\n" + policy_owner)
    add(
        checks,
        all(
            token in policy_header
            for token in (
                "class SyncSqliteOwnedAuthorizerPolicy final",
                "std::unique_ptr<TypedPolicyCapsule> typed_policy_capsule_",
                "SyncSqliteOwnedAuthorizerPolicy&& other) noexcept",
                "SyncSqliteOwnedAuthorizerPolicy&&) = delete",
                "void swap(SyncSqliteOwnedAuthorizerPolicy& other) noexcept",
                "SyncProcessIncarnation process_id_",
            )
        )
        and "std::shared_ptr<void>" not in policy_code,
        "policy_owner_is_move_only_process_bound_capsule",
        "the exact typed callback/context capsule moves only through one explicit capability",
    )
    add(
        checks,
        all(
            token in policy_header
            for token in (
                "concept SyncSqliteTypedAuthorizerPolicyFor",
                "sync_sqlite_policy_value_is_supported<Policy>",
                "std::is_empty_v<PolicyType>",
                "Policy != nullptr",
                "std::same_as<int>",
                "make_sync_sqlite_owned_authorizer_policy(",
                "std::shared_ptr<Context> context_owner",
            )
        ),
        "typed_factory_proves_callback_context_contract",
        "context type, invocation shape, exact result, and supported callback form are compile-time obligations",
    )
    add(
        checks,
        all(
            token in policy_header
            for token in (
                "class TypedPolicyCapsule",
                "class TypedPolicyCapsuleModel final",
                "std::shared_ptr<Context> context_owner_",
                "std::make_unique<TypedPolicyCapsuleModel<Context, Policy>>",
            )
        )
        and "std::shared_ptr<void>" not in policy_code
        and "static_cast" not in policy_code
        and "reinterpret_cast" not in policy_code,
        "typed_capsule_has_one_erased_runtime_object",
        "invocation behavior and exact shared ownership cross the non-templated boundary together without casts",
    )
    add(
        checks,
        ordered(
            policy_owner,
            "SyncSqliteOwnedAuthorizerPolicy&& other) noexcept",
            "other.require_current_process_noexcept()",
            "other.require_shape_noexcept()",
            "context_free_policy_ = other.context_free_policy_",
            "typed_policy_capsule_ = std::move(other.typed_policy_capsule_)",
            "other.context_free_policy_ = nullptr",
        ),
        "policy_move_validates_source_before_capsule_transfer",
        "an inherited owner fails stopped before unique or shared ownership can move",
    )
    add(
        checks,
        ordered(
            policy_owner,
            "SyncSqliteOwnedAuthorizerPolicy::~SyncSqliteOwnedAuthorizerPolicy()",
            "require_current_process_noexcept()",
            "require_shape_noexcept()",
        )
        and "before typed_policy_capsule_ reaches its implicit destructor" in policy_owner,
        "policy_destructor_validates_before_capsule_release",
        "foreign-process destruction cannot enter a virtual destructor or decrement inherited shared ownership",
    )
    add(
        checks,
        ordered(
            policy_owner,
            "int SyncSqliteOwnedAuthorizerPolicy::invoke(",
            "require_current_process_noexcept()",
            "if (typed_policy_capsule_ != nullptr)",
            "typed_policy_capsule_->invoke(",
            "if (context_free_policy_ == nullptr)",
            "context_free_policy_(nullptr",
        ),
        "policy_invocation_has_exact_typed_and_context_free_lanes",
        "context-bearing invocation remains inside the capsule while compatibility invocation receives null",
    )
    add(
        checks,
        all(
            token in policy_owner
            for token in (
                "const bool empty = context_free_policy_ == nullptr",
                "const bool context_free = context_free_policy_ != nullptr",
                "const bool typed = context_free_policy_ == nullptr",
                "if (!empty && !context_free && !typed)",
                "fail_stop_on_authorizer_policy_lifetime_violation_noexcept()",
            )
        ),
        "policy_shape_is_exact_and_fail_stopped",
        "empty, context-free, and typed are the only admitted runtime representations",
    )

    state_block = authority.split("struct ConnectionAuthorityState final", 1)[1].split(
        "class RetainedMutexCapabilityReservation", 1
    )[0]
    add(
        checks,
        "SyncSqliteOwnedAuthorizerPolicy policy_owner;" in state_block
        and "persistence::SqliteAuthorizerOwner authorizer_owner;" in state_block
        and "void* policy_context" not in state_block
        and "SyncSqliteAuthorizerPolicy policy =" not in state_block,
        "connection_state_composes_both_owners_without_raw_policy_state",
        "SQLite bridge lifetime and application policy lifetime are explicit independent members",
    )
    add(
        checks,
        ordered(
            authority,
            "void destroy_connection_authority_state(void* raw) noexcept",
            "state->authorizer_owner.attached() || !state->policy_owner.empty()",
            "fail_stop_on_sync_process_capability_violation_noexcept()",
            "delete state",
        ),
        "state_destruction_rejects_live_callback_or_policy",
        "raw close or same-name replacement cannot run a policy deleter from SQLite",
    )
    add(
        checks,
        ordered(
            authority,
            "ConnectionAuthorityState* load_connection_authority_state_or_throw(",
            "!state->policy_owner.valid()",
            "state->authorizer_owner.require_live(db)",
            "return state",
        ),
        "every_state_load_proves_both_lifetimes",
        "client-data presence alone is neither callback nor policy-context authority",
    )
    add(
        checks,
        ordered(
            authority,
            "if (state == nullptr) {",
            "sqlite3_set_clientdata(",
            "state->authorizer_owner.attach(",
            "state->policy_owner.swap(policy)",
            "run_authorizer_ownership_probe_or_throw",
        ),
        "first_install_publishes_empty_state_then_callback_then_policy",
        "SQLite allocation failure cannot synchronously dispose application policy state",
    )
    add(
        checks,
        ordered(
            authority,
            "state->authorizer_owner.attach(",
            "} catch (...) {",
            "kConnectionAuthorityClientDataName, nullptr, nullptr",
            "throw;",
            "state->policy_owner.swap(policy)",
        ),
        "failed_attach_consumes_policy_empty_state_slot",
        "an attach failure cannot leave policy state or callback state resident",
    )
    add(
        checks,
        ordered(
            authority,
            "state->authorizer_owner.replace(",
            "state->policy_owner.swap(policy)",
            "retired_policy.swap(policy)",
            "++state->authorizer_generation",
            "run_authorizer_ownership_probe_or_throw",
        ),
        "replacement_escrows_old_policy_before_generation_advance",
        "failed callback supersession cannot mutate policy or mint a generation",
    )
    add(
        checks,
        ordered(
            authority,
            "SyncSqliteAuthorizerPolicy policy,",
            "if (policy == nullptr)",
            "if (policy_context != nullptr)",
            "raw authorizer policy context is not owned",
            "SyncSqliteOwnedAuthorizerPolicy(policy)",
        )
        and "use the owned-policy overload instead" in authority_header,
        "raw_api_accepts_only_context_free_compatibility",
        "arbitrary external void* lifetime can no longer enter retained connection state",
    )
    add(
        checks,
        "state.policy_owner.invoke(" in authority
        and "state.policy(" not in authority
        and "state.policy_context" not in authority,
        "bridge_invokes_only_owned_policy",
        "all policy callbacks resolve context through the process-bound owner",
    )
    add(
        checks,
        "probe_nonce" in authority
        and "observed_probe_nonce" in authority
        and "run_authorizer_ownership_probe_or_throw" in authority
        and "authorizer ownership probe failed: callback was disabled, replaced" in authority,
        "use_time_probe_detects_unobservable_raw_replacement",
        "client-data claims remain paired with executable callback-identity evidence",
    )
    add(
        checks,
        ordered(
            authority,
            "void revoke_connection_authority_state_locked_noexcept(",
            "state->authorizer_owner.detach(db)",
            "state->policy_owner.swap(retired_policy)",
            "kConnectionAuthorityClientDataName, nullptr, nullptr",
        ),
        "locked_revoke_detaches_then_escrows_then_destroys_state",
        "SQLite forgets callback and state before application policy can be released",
    )
    add(
        checks,
        "revoke_sync_sqlite_connection_authority_before_close_noexcept" in authority_internal
        and ordered(
            authority,
            "void revoke_sync_sqlite_connection_authority_before_close_noexcept(",
            "SyncSqliteOwnedAuthorizerPolicy retired_policy",
            "sqlite3_mutex_enter(mutex)",
            "revoke_connection_authority_state_locked_noexcept(",
            "sqlite3_mutex_leave(mutex)",
        ),
        "public_close_hook_releases_retired_policy_after_mutex_leave",
        "the retirement escrow outlives the manually held SQLite critical section",
    )
    add(
        checks,
        ordered(
            handle_slot,
            "void SyncSqliteDbHandlePolicy::dispose(Handle* handle) noexcept",
            "sqlite3_get_autocommit(handle)",
            "revoke_sync_sqlite_connection_authority_before_close_noexcept(handle)",
            "sqlite3_close(handle)",
        )
        and "sqlite3_close_v2(handle)" not in handle_slot,
        "typed_owner_revokes_before_strict_close",
        "production cannot defer callback or context destruction behind zombie close",
    )
    add(
        checks,
        schema.count("install_sync_sqlite_connection_authority_or_throw(") == 1
        and ordered(
            schema,
            "install_sync_sqlite_connection_authority_or_throw(",
            "peer_transport_ingress_schema_authorizer",
            "nullptr",
        ),
        "production_uses_context_free_compatibility_lane",
        "the current production policy supplies no external application context",
    )

    add(
        checks,
        all(
            token in raw_test
            for token in (
                "test_type_and_input_contract",
                "test_attach_replace_detach_and_reuse",
                "duplicate owner cannot replace the singleton claim",
                "adversarial raw replacement fixture installed",
                "detach disables the retained callback before context release",
            )
        ),
        "focused_raw_runtime_covers_attach_replace_detach",
        "the callback owner corpus executes ordinary, duplicate, alien, and reuse transitions",
    )
    add(
        checks,
        all(
            token in policy_test
            for token in (
                "static_assert(!CanMakeCountingPolicy<WrongPolicyState>)",
                "static_assert(!CanMakeCountingPolicy<const PolicyState>)",
                "static_assert(!CanMakePolicy<wrong_result_policy, PolicyState>)",
                "static_assert(!CanMakePolicy<null_typed_policy, PolicyState>)",
                "static_assert(!CanMakePolicy<member_policy, PolicyState>)",
                "static_assert(!CanMakePolicy<stateful_policy, PolicyState>)",
                "static_assert(!CanMakeCountingPolicy<volatile PolicyState>)",
                "static_assert(!CanMakeCountingPolicy<PolicyState[2]>)",
                "std::shared_ptr<void>>)",
            )
        ),
        "focused_policy_compile_time_rejects_mismatches",
        "wrong context, cv-shape, result, null/member/stateful callback, array, and legacy erasure are non-viable",
    )
    add(
        checks,
        all(
            token in policy_test
            for token in (
                "test_const_shared_context",
                "test_aliasing_shared_owner_and_custom_deleter",
                "factory preserves a genuinely const shared context",
                "typed capsule preserves the aliasing shared control block",
                "capsule preserves the exact alias pointer and state",
                "custom deleter runs exactly once after capsule retirement",
            )
        ),
        "focused_policy_runtime_preserves_const_alias_and_deleter",
        "typed erasure retains the exact stored pointer and original control block",
    )
    add(
        checks,
        all(
            token in policy_test
            for token in (
                '#include "inherited_test_process.hpp"',
                "spawn_inherited_test_process_or_throw(",
                "test_child_local_context_and_owner_work",
                "test_inherited_owner_fails_before_shared_state_access",
                "inherited move validates source before capsule transfer",
                "child fail-stop paths do not alter parent context lifetime",
            )
        )
        and "::fork(" not in policy_test
        and "::waitpid(" not in policy_test,
        "focused_policy_runtime_proves_process_provenance",
        "child-local ownership works while inherited inspection, move, and destruction fail stopped centrally",
    )
    add(
        checks,
        "make_sync_sqlite_owned_authorizer_policy<owned_allow_policy>" in authority_test
        and "make_sync_sqlite_owned_authorizer_policy<" in transaction_test
        and "one_shot_cutpoint_policy>(cutpoint_owner)" in transaction_test
        and "int owned_allow_policy(OwnedPolicyState& state" in authority_test
        and "int one_shot_cutpoint_policy(OneShotBoundaryCutpoint& cutpoint" in transaction_test
        and "SyncSqliteOwnedAuthorizerPolicy(\n                owned_allow_policy" not in authority_test
        and "SyncSqliteOwnedAuthorizerPolicy(\n                one_shot_cutpoint_policy" not in transaction_test,
        "all_context_bearing_consumers_use_typed_factory",
        "integrated lifetime and transaction-cutpoint policies cannot pair callbacks with erased context manually",
    )

    add(
        checks,
        all(
            token in authority_test
            for token in (
                "test_owned_policy_context_lifetime_and_retirement",
                "connection authority did not retain its owned policy context",
                "replaced policy context was released while SQLite mutex remained held",
                "revoked policy context was released while SQLite mutex remained held",
                "raw policy context remained an accepted retained lifetime",
            )
        ),
        "integrated_runtime_proves_retirement_outside_mutex",
        "replacement and revoke execute custom-deleter mutex probes and raw-context rejection",
    )
    add(
        checks,
        all(
            token in authority_test
            for token in (
                '"close-live-authorizer-only"',
                '"replace-live-authority-state"',
                "raw close with a live authorizer context did not fail-stop",
                "replacement of the live authorizer context state did not fail-stop",
            )
        ),
        "raw_close_and_context_replacement_fail_stopped",
        "fresh-image probes keep unsafe SQLite-owned destruction paths executable",
    )
    add(
        checks,
        "revoke_sync_sqlite_connection_authority_before_close_noexcept" in authority_test
        and "foreign close crossed a retained mutex capability" in authority_test,
        "cross_thread_close_waits_for_live_lease",
        "close serialization is tested against an exact retained mutex generation",
    )

    passed = all(check.passed for check in checks)
    payload = {
        "format": "anonsync-sqlite-authorizer-owner-audit-v4",
        "passed": passed,
        "check_count": len(checks),
        "passed_check_count": sum(check.passed for check in checks),
        "checks": [asdict(check) for check in checks],
        "inventories": {"production_sqlite3_set_authorizer_calls": authorizer_calls},
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
