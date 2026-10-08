#!/usr/bin/env python3
"""Lexical tripwire for store-set birth attestation and fresh bootstrap.

This review pins source shape and adversarial-test vocabulary. It is not a
semantic proof of entropy, cryptographic authenticity, SQLite durability,
filesystem race freedom, crash recovery, or cross-resource atomicity.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("src/anonsync_replica.cpp"),
    Path("src/sync_replica_deployment_identity.hpp"),
    Path("src/sync_replica_deployment_identity.cpp"),
    Path("src/sync_replica_deployment_manifest.hpp"),
    Path("src/sync_replica_deployment_manifest.cpp"),
    Path("src/sync_replica_bootstrap_record.hpp"),
    Path("src/sync_replica_bootstrap_record.cpp"),
    Path("src/persistence/sqlite_snapshot_seal.hpp"),
    Path("src/persistence/sqlite_snapshot_seal.cpp"),
    Path("src/sync_replica_deployment_binding.hpp"),
    Path("src/sync_replica_deployment_binding.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("src/sync_replica_tls_policy_sqlite_profile.hpp"),
    Path("src/sync_replica_tls_policy_sqlite_profile.cpp"),
    Path("src/sync_replica_tls_membership_sqlite_owner.hpp"),
    Path("src/sync_replica_tls_membership_sqlite_owner.cpp"),
    Path("src/sync_replica_tls_membership_anchor_sqlite_owner.hpp"),
    Path("src/sync_replica_tls_membership_anchor_sqlite_owner.cpp"),
    Path("tests/persistence/sqlite_snapshot_seal_tests.cpp"),
    Path("tests/sync_replica_deployment_binding_test.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tests/sync_replica_tls_membership_sqlite_owner_test.cpp"),
    Path("tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp"),
    Path("tools/test_anonsync_replica_cli.py"),
    Path("tools/test_anonsync_replica_bootstrap_resume.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def delimited_body(text: str, signature: str, opening: str = "{", closing: str = "}") -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    boundary = text.find(opening, start + len(signature))
    if boundary < 0:
        return ""
    depth = 0
    quote = ""
    escaped = False
    line_comment = False
    block_comment = False
    index = boundary
    while index < len(text):
        byte = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if byte == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if byte == "*" and following == "/":
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif byte == "\\":
                escaped = True
            elif byte == quote:
                quote = ""
            index += 1
            continue
        if byte == "/" and following == "/":
            line_comment = True
            index += 2
            continue
        if byte == "/" and following == "*":
            block_comment = True
            index += 2
            continue
        if byte == "#":
            line_comment = True
            index += 1
            continue
        if byte in ('"', "'"):
            quote = byte
            index += 1
            continue
        if byte == opening:
            depth += 1
        elif byte == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
        index += 1
    return ""


def ordered(text: str, *tokens: str) -> bool:
    cursor = -1
    for token in tokens:
        cursor = text.find(token, cursor + 1)
        if cursor < 0:
            return False
    return True


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-replica-deployment-binding-audit-v4",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source vocabulary and order do not prove entropy, cryptographic "
            "authenticity, SQLite or filesystem durability, race freedom, "
            "crash recovery, or cross-resource atomicity"
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
    if missing:
        return emit(root, args.json, checks)

    text = {path.as_posix(): (root / path).read_text(encoding="utf-8") for path in REQUIRED}
    cmake = text["CMakeLists.txt"]
    product = text["src/anonsync_replica.cpp"]
    identity_header = text["src/sync_replica_deployment_identity.hpp"]
    identity = text["src/sync_replica_deployment_identity.cpp"]
    manifest_header = text["src/sync_replica_deployment_manifest.hpp"]
    manifest = text["src/sync_replica_deployment_manifest.cpp"]
    record_header = text["src/sync_replica_bootstrap_record.hpp"]
    record_source = text["src/sync_replica_bootstrap_record.cpp"]
    snapshot_header = text["src/persistence/sqlite_snapshot_seal.hpp"]
    snapshot_source = text["src/persistence/sqlite_snapshot_seal.cpp"]
    binding_header = text["src/sync_replica_deployment_binding.hpp"]
    binding = text["src/sync_replica_deployment_binding.cpp"]
    payload_header = text["src/sync_replica_file_payload_store.hpp"]
    payload = text["src/sync_replica_file_payload_store.cpp"]
    tls_profile_header = text["src/sync_replica_tls_policy_sqlite_profile.hpp"]
    tls_profile = text["src/sync_replica_tls_policy_sqlite_profile.cpp"]
    membership_header = text["src/sync_replica_tls_membership_sqlite_owner.hpp"]
    membership = text["src/sync_replica_tls_membership_sqlite_owner.cpp"]
    anchor_header = text[
        "src/sync_replica_tls_membership_anchor_sqlite_owner.hpp"
    ]
    anchor = text["src/sync_replica_tls_membership_anchor_sqlite_owner.cpp"]
    snapshot_test = text["tests/persistence/sqlite_snapshot_seal_tests.cpp"]
    binding_test = text["tests/sync_replica_deployment_binding_test.cpp"]
    payload_test = text["tests/sync_replica_file_payload_store_test.cpp"]
    membership_test = text[
        "tests/sync_replica_tls_membership_sqlite_owner_test.cpp"
    ]
    anchor_test = text[
        "tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp"
    ]
    process = text["tools/test_anonsync_replica_cli.py"]
    resume_process = text["tools/test_anonsync_replica_bootstrap_resume.py"]

    require(
        "std::array<unsigned char, 32U>" in identity
        and "RAND_bytes" in identity
        and "sync_replica_deployment_id_is_valid" in identity
        and "lowercase" in identity,
        "deployment_id_is_random_256_bit_and_strictly_validated",
        "bootstrap receives a reviewed lowercase 256-bit deployment identifier",
    )
    require(
        all(token in identity_header for token in (
            "deployment_id", "manifest_digest", "manifest_path", "folder_id", "local_actor"
        ))
        and "validate_sync_replica_deployment_identity_or_throw" in identity,
        "one_dependency_light_deployment_identity_is_shared",
        "manifest, SQLite, and payload owners consume the same exact identity value",
    )
    require(
        all(token in manifest for token in (
            "anonsync-replica-deployment-manifest-v2",
            "anonsync:replica-deployment-manifest:v2\\n",
            '"deployment_id"',
            '"sqlite_application_id_policy"',
            '"store_internal_deployment_binding"',
            '"bootstrap_store_adoption_policy"',
            '"role-specific-v1"',
            '"required-v1"',
            '"fresh-only-v1"',
        ))
        and "sync_replica_deployment_identity_or_throw" in manifest_header,
        "manifest_v2_commits_deployment_and_store_binding_policy",
        "the published capability commits common birth and non-adoption policy",
    )
    require(
        all(token in binding for token in (
            "0x41535201U", "0x41535202U", "0x41535203U", "0x41535204U"
        ))
        and "enum class SyncReplicaSqliteDeploymentRole" in binding_header,
        "sqlite_roles_have_distinct_early_application_id_fences",
        "replica, effect, membership, and anchor files are classified before owner adoption",
    )
    require(
        "CREATE TABLE anonsync_store_set_binding(" in binding
        and "id INTEGER PRIMARY KEY CHECK(id=1)" in binding
        and ") STRICT" in binding
        and "exact deployment-binding sqlite_schema mismatch" in binding,
        "binding_schema_is_exact_strict_and_singleton",
        "schema tolerance cannot mint store-set authority",
    )
    digest_body = delimited_body(binding, "binding_digest_or_throw(")
    require(
        ordered(
            digest_body,
            "kBindingDigestDomain", "kBindingFormat", "deployment_id",
            "manifest_digest", "manifest_path", "role", "database_path",
            "folder_id", "device_id", "epoch", "application_id",
        )
        and "append_u64" in digest_body and "append_string" in digest_body,
        "binding_digest_length_frames_every_authority_field",
        "the row checksum covers deployment, manifest, role, path, actor, and classifier",
    )
    filename_body = delimited_body(binding, "require_opened_filename_or_throw(")
    require(
        "sqlite3_db_filename" in filename_body
        and "observed.lexically_normal() != observed" in filename_body
        and "observed != expected" in filename_body,
        "binding_attests_exact_normalized_opened_filename",
        "copying a database to a new pathname cannot transfer path authority",
    )
    attest_body = delimited_body(binding, "attest_binding_state_or_throw(")
    require(
        ordered(
            attest_body,
            "require_binding_filename_authority_or_throw",
            "require_application_id_or_throw",
            "require_exact_binding_schema_or_throw", "SELECT id,format,deployment_id",
            "binding_digest_or_throw",
        )
        and "temporary deployment-binding shadow is forbidden" in binding,
        "binding_attestation_checks_filename_authority_header_schema_row_and_digest",
        "named operation and detached construction share one exact state proof while retaining different filename authority",
    )
    initialize = delimited_body(binding, "initialize_binding_or_throw(")
    initialize_named = delimited_body(
        binding, "initialize_sync_replica_sqlite_deployment_binding_or_throw("
    )
    initialize_detached = delimited_body(
        binding,
        "initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(",
    )
    detached_filename = delimited_body(
        binding, "require_detached_main_database_or_throw("
    )
    detached_empty = delimited_body(
        binding, "require_detached_bootstrap_image_empty_or_throw("
    )
    require(
        ordered(
            initialize,
            "SyncSqliteTransaction", "namespace is already occupied",
            "prior application_id", "PRAGMA main.application_id=",
            "CREATE TABLE main.", "INSERT INTO main.anonsync_store_set_binding",
            "staged proof", "transaction.commit()", "SyncSqliteTransaction proof",
            "committed proof",
        )
        and "BindingFilenameAuthority::ExactOpenedPath" in initialize_named
        and "BindingFilenameAuthority::DetachedBootstrapImage" in initialize_detached
        and "sqlite3_db_filename" in detached_filename
        and "detached bootstrap image unexpectedly names a file" in detached_filename,
        "binding_initialization_is_transactional_postcommit_reproved_and_filename_scoped",
        "the classifier and exact row cross one SQLite commit; detached construction cannot masquerade as a named database",
    )
    require(
        "sqlite3_db_readonly" in detached_filename
        and "PRAGMA main.journal_mode;" in detached_filename
        and "expected memory" in detached_filename
        and "main.sqlite_schema" in detached_empty
        and "temp.sqlite_schema" in detached_empty
        and "must be schema-empty before deployment binding" in detached_empty
        and ordered(
            initialize_detached,
            "require_detached_main_database_or_throw",
            "require_detached_bootstrap_image_empty_or_throw",
            "initialize_binding_or_throw",
        ),
        "detached_binding_initializer_requires_true_empty_memory_image",
        "an empty filename alone cannot authorize a disk-backed temporary or prepopulated database as the private genesis image",
    )
    open_bound = delimited_body(product, "open_bound_operational_database_or_throw(")
    require(
        ordered(
            open_bound,
            "DatabaseOpenDisposition::ExistingOperational",
            "attest_sync_replica_sqlite_deployment_binding_or_throw",
            "return database",
        ),
        "existing_database_open_attests_binding_before_return",
        "operational callers cannot accidentally construct an owner first",
    )
    init = delimited_body(product, "int command_init(")
    resume = delimited_body(product, "int command_init_resume(")
    create_missing = delimited_body(
        product, "void create_missing_bootstrap_resources_or_throw("
    )
    sealed_create = delimited_body(
        product, "void create_sealed_bootstrap_database_or_throw("
    )
    identity_phase = delimited_body(
        product, "attest_existing_bootstrap_resource_identities_or_throw("
    )
    snapshot_create_new = delimited_body(
        snapshot_source,
        "void SealedSqliteSnapshot::\npublish_exact_copy_atomically_create_new_with_observer_or_throw(",
    )
    require(
        ordered(
            init,
            "generate_sync_replica_deployment_id_or_throw",
            "compute_sync_replica_deployment_manifest_digest_or_throw",
            "validate_sync_replica_bootstrap_record_namespace_or_throw",
            "require_path_absent_for_fresh_bootstrap_or_throw",
            "require_fresh_database_family_or_throw",
            "require_empty_directory_for_fresh_bootstrap_or_throw",
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw",
            "create_sync_replica_bootstrap_record_or_throw",
            "require_fresh_inventory_after_bootstrap_record_or_throw",
            "create_missing_bootstrap_resources_or_throw",
        )
        and "-journal" in product and "-wal" in product and "-shm" in product,
        "whole_selected_namespace_is_preflighted_before_record_first_mutation",
        "main files, sidecars, payload roots, delivery roots, final manifest, and record must be clean before materialization",
    )
    require(
        create_missing.count("create_sealed_bootstrap_database_or_throw") == 4
        and ordered(
            sealed_create,
            "open_detached_bootstrap_database_or_throw",
            "initialize_detached_sqlite_deployment_binding_or_throw",
            "initialize_and_verify_role",
            "SealedSqliteSnapshot::capture_database",
            "require_fresh_database_family_or_throw",
            "publish_exact_copy_atomically_create_new_or_throw",
            "open_bound_bootstrap_candidate_or_throw",
            "promote_bound_bootstrap_candidate_to_operational_or_throw",
        )
        and ordered(
            create_missing,
            "replica_database_present",
            "create_sealed_bootstrap_database_or_throw",
            "SyncReplicaSqliteDeploymentRole::Replica",
            "SyncReplicaSqliteOwner owner",
            "effect_database_present",
            "create_sealed_bootstrap_database_or_throw",
            "SyncReplicaSqliteDeploymentRole::FileEffect",
            "SyncReplicaFileEffectSqliteOwner owner",
            "membership_database_present",
            "create_sealed_bootstrap_database_or_throw",
            "SyncReplicaSqliteDeploymentRole::TlsMembership",
            "SyncReplicaTlsMembershipSqliteOwner owner",
            "anchor_database_present",
            "create_sealed_bootstrap_database_or_throw",
            "SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor",
            "SyncReplicaTlsMembershipAnchorSqliteOwner owner",
        )
        and "publish_exact_copy_atomically_create_new_or_throw" in snapshot_header
        and ordered(
            snapshot_create_new,
            "verify_unchanged_or_throw",
            "write_sync_file_atomically_create_new_with_observer_or_throw",
            "verify_unchanged_or_throw",
        ),
        "every_created_database_is_complete_bound_and_role_initialized_before_publication",
        "shared fresh/recovery creation exposes one exact create-new SQLite image rather than an empty main file followed by repair",
    )
    require(
        ordered(
            resume,
            "read_sync_replica_bootstrap_record_or_throw",
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw",
            "attest_existing_bootstrap_resource_identities_or_throw",
            "promote_existing_bootstrap_sqlite_authorities_or_throw",
            "attest_existing_bootstrap_role_state_or_throw",
            "advanced beyond bootstrap genesis",
            "existing = BootstrapExistingSqliteAuthorities{}",
            "create_missing_bootstrap_resources_or_throw",
            "attest_complete_bootstrap_store_set_or_throw",
        )
        and "DatabaseOpenDisposition disposition" in identity_phase
        and "open_bound_operational_database_or_throw" in identity_phase
        and "open_bound_bootstrap_candidate_or_throw" in identity_phase
        and identity_phase.count("authorities.") >= 4
        and "create_sealed_bootstrap_database_or_throw" not in identity_phase,
        "resume_retains_all_present_bindings_before_promotion_schema_or_creation",
        "foreign exact-looking resources fail in phase one; retained handles close the ordinary reopen gap before genesis-gated recomposition",
    )
    operational_signatures = (
        "int command_status(", "int command_clock_observe(", "int command_clock_recover(",
        "int command_enqueue_file(", "int command_membership_publish(",
        "int command_send_one(", "int command_serve_one(",
    )
    operational = [delimited_body(product, signature) for signature in operational_signatures]
    require(
        all("open_database_or_throw" not in body for body in operational)
        and sum(body.count("open_bound_operational_database_or_throw") for body in operational) == 14,
        "all_operational_sqlite_paths_use_the_bound_open_frontier",
        "status, clock, enqueue, membership, send, and receive have no raw SQLite bypass",
    )
    product_constructor = payload_header[payload_header.find("SyncReplicaFilePayloadStore(") :]
    require(
        "SyncReplicaDeploymentIdentity deployment" in product_constructor
        and "kProductStoreIdentityBasenameV3" in payload
        and "product_store_identity_payload_or_throw" in payload
        and all(token in delimited_body(payload, "product_store_identity_payload_or_throw(") for token in (
            "deployment_id", "manifest_digest", "manifest_path", "folder_id", "device_id", "epoch", "kStoreLeaseProtocol"
        )),
        "product_payload_marker_v3_binds_common_deployment_birth",
        "payload bytes cannot be silently transplanted behind another manifest",
    )
    require(
        "allow_existing_payload_adoption = false" in payload
        and "product-bound bootstrap refuses adoption of pre-existing" in payload,
        "product_payload_bootstrap_refuses_preexisting_namespace_adoption",
        "fresh product setup cannot bless digest-named leftovers or transient residue",
    )
    require(
        all(token in binding_test for token in (
            "wrong deployment", "wrong manifest digest", "wrong role", "wrong path",
            "application-id tamper", "temp shadow", "row tamper", "copied database",
            "deployment-binding detached fixture",
            "a detached image crossed the ordinary named authority gate",
            "deployment-binding detached image named readback",
            "a named database was accepted as a detached bootstrap image",
            "anonymous temporary rejection",
            "expected memory",
            "prepopulated detached rejection",
            "must be schema-empty",
        )),
        "compiled_binding_test_covers_identity_role_path_header_schema_and_copy_attacks",
        "runtime tests exercise every exact SQLite binding dimension plus detached-image authority separation",
    )
    require(
        "publish_exact_copy_atomically_create_new_or_throw" in snapshot_test
        and "immutable sealed publication changed resident bytes" in snapshot_test
        and "failed immutable republish replaced the existing image" in snapshot_test,
        "compiled_snapshot_test_pins_exact_create_new_publication",
        "the sealed-image wrapper preserves exact bytes and refuses replacement of an existing main file",
    )
    require(
        "enum class SyncReplicaTlsPolicySqliteBackendDisposition" in tls_profile_header
        and "DetachedBootstrapImage" in tls_profile_header
        and "detached bootstrap image unexpectedly names a file" in tls_profile
        and "detached bootstrap image cannot publish membership authority" in membership
        and "detached bootstrap image cannot advance membership anchor" in anchor
        and "backend_disposition_" in membership_header
        and "backend_disposition_" in anchor_header
        and "detached membership bootstrap owner crossed into durable publication" in membership_test
        and "detached membership-anchor owner crossed into durable advancement" in anchor_test,
        "detached_tls_role_owners_are_genesis_only_and_nonoperational",
        "the compatibility profile permits namespace-free schema construction but refuses durable membership transitions",
    )
    require(
        all(token in payload_test for token in (
            "product-bound", "wrong deployment", "product-bound wrong manifest",
            "incompatible", "pre-existing"
        )),
        "compiled_payload_test_covers_product_binding_and_nonadoption",
        "runtime tests reject foreign marker generations and preseeded roots",
    )
    require(
        all(token in record_header + record_source for token in (
            "SyncReplicaBootstrapRecord",
            "exact_manifest_bytes",
            "validate_sync_replica_bootstrap_record_namespace_or_throw",
            "write_sync_file_atomically_create_new_no_symlink_or_throw",
            "decode_sync_replica_deployment_manifest_or_throw",
        )),
        "bootstrap_record_binds_exact_future_manifest_before_store_birth",
        "recovery authority is one immutable deployment identity and configuration, not inferred resource co-location",
    )
    require(
        all(token in resume_process for token in (
            "foreign-binding rejection",
            "advanced beyond bootstrap genesis",
            "genesis receiver resume",
            "committed missing-store refusal",
            "copied bootstrap record",
            "sealed rollback-image resume",
            "rollback-sidecar rejection",
            "unbound SQLite rejection",
        )),
        "resume_process_proof_covers_identity_first_completion_and_recomposition_refusal",
        "the shipped executable creates only sealed record-selected genesis stores and rejects contaminated, unbound, foreign, or advanced partial sets",
    )
    require(
        all(token in process for token in (
            "forge_manifest_deployment_id", "same-role database substitution",
            "cross-role database substitution", "foreign payload substitution",
            "orphan-sidecar bootstrap", "preseeded-payload bootstrap",
            "verify_database_binding", "expected_database_binding_digest",
        )),
        "process_proof_covers_canonical_forgery_store_swaps_and_freshness_cutpoints",
        "the shipped executable rejects independently valid resource recomposition",
    )
    require(
        all(token in cmake for token in (
            "anonsync_sync_replica_deployment_identity",
            "anonsync_sync_replica_deployment_binding",
            "anonsync_sync_replica_deployment_binding_test",
            "anonsync_sqlite_snapshot_seal",
            "anonsync_sync_replica_bootstrap_record",
            "anonsync_sync_replica_bootstrap_record_test",
            "anonsync_replica_bootstrap_resume_process_test",
            "anonsync_replica_deployment_binding_source_audit",
            "audit_anonsync_replica_deployment_binding.py",
        )),
        "identity_binding_runtime_test_and_audit_are_in_normal_build_graph",
        "ordinary CMake/CTest validation retains the new product boundary",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
