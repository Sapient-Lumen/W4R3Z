#!/usr/bin/env python3
"""Lexical hygiene audit for canonical TLS membership value authority.

This audit inventories reviewed source shape, canonicalization vocabulary, and
composition order. It deliberately does not claim to prove C++ immutability,
hash collision resistance, authorization correctness, concurrency safety,
OpenSSL peer identity, SQLite durability, or rollback resistance. Compiled
adversarial tests and the durable membership-owner audit carry those semantic
obligations.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def body(text: str, marker: str) -> str:
    start = text.find(marker)
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
                return text[start : index + 1]
    return ""


def ordered(text: str, *tokens: str) -> bool:
    position = 0
    for token in tokens:
        position = text.find(token, position)
        if position < 0:
            return False
        position += len(token)
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    paths = {
        "header": root / "src/sync_replica_tls_membership_snapshot.hpp",
        "source": root / "src/sync_replica_tls_membership_snapshot.cpp",
        "owner_header": root / "src/sync_replica_tls_membership_sqlite_owner.hpp",
        "owner_source": root / "src/sync_replica_tls_membership_sqlite_owner.cpp",
        "server_header": root / "src/sync_replica_file_tls_server.hpp",
        "server_source": root / "src/sync_replica_file_tls_server.cpp",
        "runtime": root / "tests/sync_replica_tls_transport_test.cpp",
        "owner_runtime": root / "tests/sync_replica_tls_membership_sqlite_owner_test.cpp",
        "cmake": root / "CMakeLists.txt",
        "verifier": root / "tools/verify_release_package.py",
    }
    missing = sorted(
        str(path.relative_to(root)) for path in paths.values() if not path.is_file()
    )
    text = {
        name: path.read_text(encoding="utf-8") if path.is_file() else ""
        for name, path in paths.items()
    }
    checks: list[dict[str, object]] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append({"check_id": check_id, "passed": bool(condition), "detail": detail})

    require(not missing, "required_files_exist", f"missing={missing}")
    header = text["header"]
    source = text["source"]
    owner_header = text["owner_header"]
    server_header = text["server_header"]
    server_source = text["server_source"]
    runtime = text["runtime"]
    owner_runtime = text["owner_runtime"]
    cmake = text["cmake"]
    verifier = text["verifier"]

    snapshot_class = body(header, "class SyncReplicaTlsMembershipSnapshot final")
    require(
        bool(snapshot_class)
        and "std::shared_ptr<const State> state_" in snapshot_class
        and "SyncReplicaTlsMembershipSnapshot(\n        const SyncReplicaTlsMembershipSnapshot&) noexcept = default" in snapshot_class
        and "active() const noexcept" in snapshot_class,
        "snapshot_retains_copyable_const_shared_state",
        "copies retain only immutable canonical state",
    )
    require(
        "std::function" not in header + source + server_header + server_source
        and "SyncReplicaTlsPeerActorResolver" not in header + server_header
        and "resolve_peer_actor" not in server_source,
        "membership_path_contains_no_arbitrary_callback",
        "post-handshake authorization is pure immutable lookup",
    )
    require(
        "policy_epoch is caller-owned configuration versioning" in header
        and "not itself rollback protection" in header
        and "durable SQLite" in header,
        "policy_epoch_nonclaim_names_durable_owner",
        "digest versioning is not misrepresented as rollback defense",
    )

    constructor = body(source, "SyncReplicaTlsMembershipSnapshot::SyncReplicaTlsMembershipSnapshot(")
    require(
        ordered(
            constructor,
            "sync_id_is_valid(folder_id)",
            "validate_actor_or_throw(local_actor",
            "policy_epoch == 0U",
            "entries.size() > kSyncReplicaTlsMembershipMaxEntries",
        ),
        "constructor_bounds_identity_epoch_and_count",
        "invalid service identity and unbounded membership fail before retention",
    )
    require(
        ordered(
            constructor,
            "is_lowercase_sha256_hex(entry.spki_sha256)",
            "validate_actor_or_throw(entry.actor",
            "entry.actor.device_id == local_actor.device_id",
            "std::sort(",
            "std::adjacent_find(",
            "duplicate SPKI membership authority",
        ),
        "entries_are_validated_sorted_and_deduplicated",
        "one canonical SPKI maps to at most one actor",
    )
    require(
        "kSyncReplicaTlsMembershipMaxEntries = 65536U" in header
        and "std::length_error" in constructor,
        "snapshot_has_explicit_entry_ceiling",
        "configuration input cannot allocate an unbounded membership set",
    )

    digest = body(source, "std::string snapshot_digest_or_throw(")
    require(
        "anonsync:sync-replica-tls-membership-snapshot:v1" in source
        and ordered(
            digest,
            "kSnapshotDigestDomain",
            "folder_id",
            "local_actor",
            "policy_epoch",
            "entries.size()",
            "entry.spki_sha256",
            "entry.actor",
        ),
        "digest_is_domain_separated_and_complete",
        "folder, receiver, epoch, count, pins, and actors are committed",
    )
    require(
        "std::array<char, 8U> encoded" in source
        and "append_u64(digest, static_cast<std::uint64_t>(value.size()))" in source
        and "digest.update(value)" in source,
        "digest_fields_are_canonically_framed",
        "fixed-width counts and length prefixes close concatenation ambiguity",
    )

    lookup = body(source, "SyncReplicaTlsMembershipSnapshot::resolve_peer_or_throw(")
    require(
        ordered(
            lookup,
            "is_lowercase_sha256_hex(spki_sha256)",
            "std::lower_bound(",
            "found->spki_sha256 != spki_sha256",
            "return found->actor",
        ),
        "lookup_requires_exact_canonical_pin",
        "malformed or absent authenticated evidence cannot alias membership",
    )
    identity = body(source, "SyncReplicaTlsMembershipSnapshot::require_service_identity_or_throw(")
    require(
        "state.folder_id != folder_id" in identity
        and "state.local_actor != local_actor" in identity,
        "snapshot_is_scoped_to_exact_service_identity",
        "one value cannot cross folder or local actor authority",
    )
    require(
        "std::span<const SyncReplicaTlsMembershipEntry> entries() const" in header
        and "require_state_or_throw" in body(
            source, "SyncReplicaTlsMembershipSnapshot::entries() const")
        and "entries.data(), entries.size()" in body(
            source, "SyncReplicaTlsMembershipSnapshot::entries() const"),
        "canonical_entries_are_exposed_read_only",
        "durable owner persists the exact canonical sequence without a copy-only escape hatch",
    )

    authority_class = body(owner_header, "class SyncReplicaTlsMembershipAuthority final")
    require(
        bool(authority_class)
        and "const SyncReplicaTlsMembershipAuthority&) = delete" in authority_class
        and "SyncReplicaTlsMembershipAuthority&&) noexcept = default" in authority_class
        and "friend class SyncReplicaTlsMembershipSqliteOwner" in authority_class
        and "explicit SyncReplicaTlsMembershipAuthority(" in authority_class,
        "accepted_session_authority_is_owner_only_and_move_only",
        "a freely constructed snapshot cannot impersonate a committed policy capability",
    )

    serve = body(server_source, "Result serve_one_authenticated_tls_session_or_throw(")
    require(
        "SyncReplicaTlsAnchoredMembershipAuthority membership" in server_header
        and "SyncReplicaTlsMembershipSnapshot membership" not in server_header
        and "SyncReplicaTlsMembershipAuthority membership" not in server_header
        and "SyncReplicaTlsAnchoredMembershipAuthority membership" in serve,
        "server_takes_anchored_durable_authority_by_value",
        "one independently anchored capability is consumed by one accepted-session invocation",
    )
    require(
        ordered(
            serve,
            "membership.snapshot()",
            "membership_snapshot.require_service_identity_or_throw",
            "membership.state_generation()",
            "membership_snapshot.snapshot_digest()",
            "SSL_new(server_context_handle)",
            "std::forward<Acquire>(acquire)()",
        ),
        "service_identity_and_policy_evidence_precede_accept",
        "cross-service policy cannot spend listener or native-overlay stream authority",
    )
    require(
        ordered(
            serve,
            "sync_replica_tls_peer_spki_sha256_or_throw",
            "membership_snapshot.resolve_peer_or_throw",
            "result.disposition = peer_unauthorized",
            "post-membership accepted socket",
            "authenticate_sync_replica_tls13_channel_or_throw",
        ),
        "exact_spki_membership_precedes_application_channel",
        "certificate validity alone never authorizes an actor",
    )
    require(
        all(token in server_header + serve for token in (
            "membership_state_generation",
            "membership_policy_epoch",
            "membership_entry_count",
            "membership_snapshot_digest",
            "membership_previous_chain_digest",
            "membership_chain_digest",
        )),
        "server_result_exposes_full_membership_cutpoint",
        "terminal diagnostics bind snapshot and append-only chain evidence",
    )

    runtime_tokens = (
        "immutable TLS membership digest depended on caller entry order",
        "immutable TLS membership lookup lost exact SPKI-to-actor authority",
        "immutable TLS membership digest omitted policy epoch",
        "moved-from TLS membership snapshot remained usable",
        "TLS membership snapshot admitted conflicting duplicate SPKI authority",
        "TLS membership snapshot authorized the receiver as its own peer",
        "TLS membership preaccept mismatch reached durable authority",
        "TLS server authorized or misattributed a certificate-valid unmapped peer",
        "TLS server did not preserve accepted-session terminal cutpoints and membership evidence",
    )
    require(
        all(token in runtime for token in runtime_tokens),
        "compiled_runtime_matrix_covers_snapshot_and_composition",
        "canonicalization, misuse, rejection, and terminal success are executable",
    )
    require(
        all(token in owner_runtime for token in (
            "committed membership authority lost canonical policy evidence",
            "moved-from membership authority remained usable",
            "external membership anchor did not detect whole-database rollback",
        )),
        "durable_owner_runtime_consumes_canonical_value_surface",
        "snapshot integration is tested across persistence, movement, and rollback",
    )
    require(
        "add_library(anonsync_sync_replica_tls_membership STATIC" in cmake
        and "ANONSYNC_SYNC_REPLICA_TLS_MEMBERSHIP_SOURCE" in cmake
        and "anonsync_sync_replica_tls_membership" in cmake,
        "membership_is_a_separate_authority_library",
        "policy work does not remain textually fused into the accepted-session target",
    )
    require(
        cmake.count("anonsync_sync_tls_membership_snapshot_source_audit") >= 2,
        "snapshot_audit_is_registered",
        "ordinary CTest retains the lexical inventory",
    )
    require(
        all(token in verifier for token in (
            "src/sync_replica_tls_membership_snapshot.hpp",
            "src/sync_replica_tls_membership_snapshot.cpp",
            "src/sync_replica_tls_membership_sqlite_owner.hpp",
            "tools/audit_sync_tls_membership_snapshot.py",
        )),
        "release_verifier_requires_snapshot_surface",
        "a sealed revision cannot omit value, owner bridge, or audit",
    )
    require(
        "Lexical hygiene audit" in (__doc__ or "")
        and "does not claim to prove" in (__doc__ or ""),
        "audit_disclaims_semantic_authority",
        "source vocabulary is not represented as runtime proof",
    )

    passed = all(bool(check["passed"]) for check in checks)
    result = {
        "format": "anonsync-tls-membership-snapshot-source-audit-v2",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove authorization, hashing, "
            "concurrency, OpenSSL, SQLite durability, or rollback semantics"
        ),
        "root": str(root),
        "passed": passed,
        "passed_checks": sum(bool(check["passed"]) for check in checks),
        "total_checks": len(checks),
        "checks": checks,
        "violations": [check["check_id"] for check in checks if not check["passed"]],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
