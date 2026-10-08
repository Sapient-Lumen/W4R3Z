#!/usr/bin/env python3
"""Audit exact owner-generation pinning and focused schema build ownership."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/sha256_digest.hpp"),
    Path("src/sha256_digest.cpp"),
    Path("src/json_codec_crypto.cpp"),
    Path("src/contracts_policy_profiles.cpp"),
    Path("src/sync_peer_ingress_schema.hpp"),
    Path("src/sync_peer_ingress_schema.cpp"),
    Path("src/sync_peer_ingress_payload_store.cpp"),
    Path("src/sync_peer_ingress_payload_store_schema.cpp"),
    Path("src/sync_sqlite_schema_identity.cpp"),
    Path("src/sync_peer_ingress_lifecycle.cpp"),
    Path("tests/peer_ingress_schema_attestation_test.cpp"),
    Path("tests/self_exec_test_process.hpp"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    finish = text.find(end, begin + len(start)) if begin >= 0 else -1
    return text[begin:finish] if begin >= 0 and finish > begin else ""


def ordered(text: str, *markers: str) -> bool:
    cursor = 0
    for marker in markers:
        cursor = text.find(marker, cursor)
        if cursor < 0:
            return False
        cursor += len(marker)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    missing = [p.as_posix() for p in REQUIRED if not (root / p).is_file()]
    if missing:
        report = {
            "format": "anonsync-peer-ingress-schema-owner-generation-audit-v3",
            "passed": False,
            "violations": [f"missing required file: {p}" for p in missing],
        }
        rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.json:
            args.json.parent.mkdir(parents=True, exist_ok=True)
            args.json.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 2

    def read(path: str) -> str:
        return (root / path).read_text(encoding="utf-8")

    cmake = read("CMakeLists.txt")
    digest_header = read("src/sha256_digest.hpp")
    digest_source = read("src/sha256_digest.cpp")
    json_crypto = read("src/json_codec_crypto.cpp")
    contracts = read("src/contracts_policy_profiles.cpp")
    header = read("src/sync_peer_ingress_schema.hpp")
    impl = read("src/sync_peer_ingress_schema.cpp")
    payload_data = read("src/sync_peer_ingress_payload_store.cpp")
    payload_schema = read("src/sync_peer_ingress_payload_store_schema.cpp")
    schema_identity = read("src/sync_sqlite_schema_identity.cpp")
    lifecycle = read("src/sync_peer_ingress_lifecycle.cpp")
    test = read("tests/peer_ingress_schema_attestation_test.cpp")

    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    attestation = section(header,
                          "class PeerTransportIngressSchemaAttestation final",
                          "// Write-capable callers")
    require("SyncSqliteSerializedDbBorrow owner_borrow_;" in attestation
            and "sqlite3* db_" not in attestation,
            "attestation_owns_exact_generation_pin",
            "a raw address cannot preserve connection lifetime or owner generation")
    compact_attestation = " ".join(attestation.split())
    require("PeerTransportIngressSchemaAttestation( const PeerTransportIngressSchemaAttestation&) = delete;" in compact_attestation
            and "PeerTransportIngressSchemaAttestation( PeerTransportIngressSchemaAttestation&&) noexcept = default;" in compact_attestation,
            "attestation_is_unique_move_only_capability",
            "copying would duplicate one owner-generation lifetime claim")
    require("std::uint64_t owner_generation() const noexcept" in header,
            "owner_generation_is_observable_for_proof",
            "tests need a value-free way to prove exact-generation binding")
    require(header.count("SyncSqliteDbHandleSlot& db_owner") >= 2
            and "initialize_or_inspect_peer_transport_ingress_schema_or_throw(\n    sqlite3* db" not in header,
            "public_boundary_requires_typed_owner",
            "schema authority may be minted only from the owner that issues a generation pin")

    initialize = section(impl,
                         "initialize_or_inspect_peer_transport_ingress_schema_or_throw(",
                         "SyncSqliteConnectionAuthorityLease\nverify_peer_transport")
    require(ordered(initialize,
                    "SyncSqliteSerializedDbBorrow owner_borrow",
                    "borrow_sync_sqlite_serialized_db_or_throw(",
                    "sqlite3* const db = owner_borrow.get();",
                    "std::move(owner_borrow)"),
            "initialization_mints_and_transfers_generation_pin",
            "attestation must retain the generation used for schema inspection")

    verify = section(impl,
                     "verify_peer_transport_ingress_schema_attestation_current_or_throw(",
                     "std::string expected_peer_transport_ingress_schema_manifest_sha256")
    require("SyncSqliteDbHandleBorrow candidate = db_owner.borrow();" in verify
            and "attestation.owner_borrow_.generation() != candidate.generation()" in verify
            and "attested_db != db" in verify,
            "use_time_verification_matches_handle_and_generation",
            "pointer equality alone cannot authorize a reopened connection")

    for struct_name in ("PeerTransportIngressWriteConnection",
                        "PeerTransportIngressReadConnection"):
        body = section(lifecycle, f"struct {struct_name}", "};")
        require(ordered(body,
                        "SyncSqliteDb owner;",
                        "PeerTransportIngressSchemaAttestation schema_attestation;",
                        "SyncSqliteSerializedDbBorrow serialized;"),
                f"{struct_name.lower()}_destruction_order_is_authority_safe",
                "reverse destruction must release use borrow, attestation pin, then owner")

    require("SyncSqliteDb owner;" in test
            and "attestation.owner_generation() == generation" in test
            and "active_borrows() == 1" in test,
            "focused_test_proves_exact_pin_accounting",
            "the test must observe one retained pin and its exact generation")
    require("test_live_attestation_blocks_owner_close" in test
            and "kSyncProcessCapabilityViolationExitCode" in test
            and '#include "self_exec_test_process.hpp"' in test
            and "--anonsync-peer-schema-owner-close-helper-v1" in test
            and "verify_self_exec_child_boundary_or_throw();" in test
            and "spawn_self_exec_test_process_or_throw(" in test
            and "wait_for_exact_exit(" in test
            and "::fork(" not in test
            and "::waitpid(" not in test,
            "focused_test_proves_close_is_blocked",
            "a fresh exec image must fail-stop owner destruction before sqlite3_close, with no raw post-fork application path")
    require("test_owner_generation_pin_and_move" in test
            and "PeerTransportIngressSchemaAttestation moved(std::move(attestation))" in test,
            "focused_test_proves_unique_pin_transfer",
            "move must transfer rather than duplicate or release the pin")

    raw_call_pattern = re.compile(
        r"(?:initialize_or_inspect_peer_transport_ingress_schema_or_throw|"
        r"verify_peer_transport_ingress_schema_attestation_current_or_throw)"
        r"\(\s*[A-Za-z_][A-Za-z0-9_]*\.get\(\),")
    require(not raw_call_pattern.search(lifecycle + test),
            "production_and_tests_do_not_mint_from_raw_get",
            "typed call sites must not downgrade their owner before attestation")

    core_match = re.search(
        r"set\(ANONSYNC_CORE_SOURCES(?P<body>.*?)\)\nforeach\(ANONSYNC_INVARIANT_OWNED_SOURCE",
        cmake,
        re.DOTALL,
    )
    require(core_match is not None,
            "core_source_list_is_discoverable",
            "the architecture guard must be able to inspect the core source projection")
    core_body = core_match.group("body") if core_match else ""
    require(all(source not in core_body for source in (
                "src/sync_peer_ingress_schema.cpp",
                "src/sync_peer_ingress_payload_store_schema.cpp",
                "src/sync_sqlite_schema_identity.cpp")),
            "schema_sources_are_outside_core",
            "focused schema sources must not be reabsorbed into the monolith")
    require(core_body.count("src/sync_sqlite_schema_identity.cpp") == 0,
            "schema_identity_is_not_duplicated_in_core",
            "the same translation unit must not be listed twice or compiled under two owners")
    schema_source_list = section(
        cmake, "set(ANONSYNC_PEER_INGRESS_SCHEMA_SOURCES", "add_library(anonsync_peer_ingress_schema")
    require(all(source in schema_source_list for source in (
                "src/sync_peer_ingress_schema.cpp",
                "src/sync_peer_ingress_payload_store_schema.cpp"))
            and "src/sync_sqlite_schema_identity.cpp" not in schema_source_list,
            "focused_library_owns_complete_peer_schema_source_set",
            "the peer schema target must own attestation and payload shape without recompiling the shared identity owner")
    identity_source_list = section(
        cmake,
        "set(ANONSYNC_SQLITE_SCHEMA_IDENTITY_SOURCE",
        "add_library(anonsync_sqlite_schema_identity")
    require(identity_source_list.count("src/sync_sqlite_schema_identity.cpp") == 1
            and "add_library(anonsync_sqlite_schema_identity STATIC" in cmake,
            "schema_identity_has_one_independent_build_owner",
            "one reusable focused target must compile the exact schema canonicalizer exactly once")
    schema_links = section(
        cmake,
        "target_link_libraries(anonsync_peer_ingress_schema PUBLIC",
        "target_compile_options(anonsync_peer_ingress_schema")
    require("anonsync_sha256_digest" in schema_links
            and "anonsync_sqlite_schema_identity" in schema_links
            and "anonsync_sqlite_support" in schema_links
            and "anonsync_core_lib" not in schema_links,
            "focused_library_has_no_core_dependency",
            "the schema library may depend on digest and focused SQLite owners, never the core")
    require("target_link_libraries(anonsync_peer_ingress_schema_attestation_test PRIVATE\n  anonsync_peer_ingress_schema)" in cmake
            and "target_link_libraries(anonsync_peer_ingress_schema_attestation_test PRIVATE\n  anonsync_core_lib)" not in cmake,
            "focused_test_links_focused_library",
            "the focused proof must not compile or link the core monolith")
    require("anonsync_peer_ingress_schema\n    anonsync_peer_ingress_schema_attestation_test" in cmake,
            "cmake_no_core_guard_covers_schema_targets",
            "configuration must reject a future core dependency")

    require("void ensure_peer_transport_ingress_payload_store_schema_or_throw" in payload_schema
            and "void verify_peer_transport_ingress_payload_store_schema_or_throw" in payload_schema
            and "verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw" in payload_schema,
            "payload_schema_implementation_is_focused",
            "payload schema authority belongs in the focused schema translation unit")
    require("void ensure_peer_transport_ingress_payload_store_schema_or_throw" not in payload_data
            and "sync_peer_ingress_schema_sql.hpp" not in payload_data
            and "sync_sqlite_schema_identity.hpp" not in payload_data,
            "payload_data_path_no_longer_owns_schema_proof",
            "operational payload storage must consume, not implement, schema authority")
    require("canonicalize_sqlite_schema_sql_or_throw" in payload_schema
            and "canonicalize_sqlite_schema_sql_or_throw" in schema_identity,
            "payload_schema_uses_exact_identity_owner",
            "schema comparisons must route through one exact canonicalization owner")

    require("std::string sha256_hex" in digest_source
            and "bool is_lowercase_sha256_hex" in digest_source
            and "sha256_hex" in digest_header,
            "digest_boundary_owns_hash_and_text_validation",
            "focused schema code needs one small digest evidence owner")
    require("std::string sha256_hex" not in json_crypto
            and "bool is_lowercase_sha256_hex" not in contracts,
            "legacy_monoliths_do_not_duplicate_digest_owner",
            "JSON and policy units must consume the digest owner instead of redefining it")
    require("anonsync_peer_ingress_schema_owner_generation_source_audit" in cmake,
            "architecture_audit_is_registered",
            "the owner-generation and build-boundary contract must remain a CTest gate")

    passed = all(c.passed for c in checks)
    report = {
        "format": "anonsync-peer-ingress-schema-owner-generation-audit-v3",
        "passed": passed,
        "check_count": len(checks),
        "passed_check_count": sum(c.passed for c in checks),
        "checks": [asdict(c) for c in checks],
        "violations": [c.detail for c in checks if not c.passed],
        "metrics": {
            "attestation_header_lines": len(header.splitlines()),
            "schema_implementation_lines": len(impl.splitlines()),
            "payload_schema_lines": len(payload_schema.splitlines()),
            "focused_test_lines": len(test.splitlines()),
        },
        "residual_risks": [
            "The attestation pins one live process-local owner generation; restart authority must still be reconstructed from durable schema evidence.",
            "Raw SQLite compatibility overloads elsewhere remain migration debt and are not upgraded by this boundary.",
        ],
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
