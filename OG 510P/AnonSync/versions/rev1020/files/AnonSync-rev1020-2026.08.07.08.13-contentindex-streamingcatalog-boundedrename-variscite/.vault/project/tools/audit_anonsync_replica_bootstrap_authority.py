#!/usr/bin/env python3
"""Lexical tripwire for record-first bootstrap and manifest-bound operations.

This audit pins reviewed source ownership, call ordering, and adversarial-test
vocabulary. It is intentionally a source-shape check, not semantic proof of
filesystem identity, SQLite durability, concurrency safety, crash behavior, or
cross-resource atomicity. Compiled and process tests remain load-bearing.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED = (
    Path("CMakeLists.txt"),
    Path("include/anonsync_json_parser.hpp"),
    Path("src/anonsync_json_parser.cpp"),
    Path("src/anonsync_replica.cpp"),
    Path("src/sync_atomic_file_publication.hpp"),
    Path("src/sync_replica_deployment_manifest.hpp"),
    Path("src/sync_replica_deployment_manifest.cpp"),
    Path("src/sync_replica_bootstrap_record.hpp"),
    Path("src/sync_replica_bootstrap_record.cpp"),
    Path("src/sync_replica_file_payload_store.hpp"),
    Path("src/sync_replica_file_payload_store.cpp"),
    Path("tests/sync_replica_deployment_manifest_test.cpp"),
    Path("tests/sync_replica_bootstrap_record_test.cpp"),
    Path("tests/sync_replica_file_payload_store_test.cpp"),
    Path("tools/test_anonsync_replica_cli.py"),
    Path("tools/test_anonsync_replica_bootstrap_resume.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def delimited_body(
    text: str, signature: str, opening: str = "{", closing: str = "}"
) -> str:
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
        "format": "anonsync-replica-bootstrap-authority-audit-v6",
        "scope": "lexical-hygiene-not-semantic-proof",
        "scope_nonclaim": (
            "source spelling and order do not prove path identity, SQLite or "
            "filesystem durability, concurrency, crash recovery, race freedom, "
            "or cross-resource atomicity"
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
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
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
    cmake = text["CMakeLists.txt"]
    parser_header = text["include/anonsync_json_parser.hpp"]
    parser_source = text["src/anonsync_json_parser.cpp"]
    product = text["src/anonsync_replica.cpp"]
    atomic_header = text["src/sync_atomic_file_publication.hpp"]
    manifest_header = text["src/sync_replica_deployment_manifest.hpp"]
    manifest_source = text["src/sync_replica_deployment_manifest.cpp"]
    record_header = text["src/sync_replica_bootstrap_record.hpp"]
    record_source = text["src/sync_replica_bootstrap_record.cpp"]
    payload_header = text["src/sync_replica_file_payload_store.hpp"]
    payload_source = text["src/sync_replica_file_payload_store.cpp"]
    manifest_test = text["tests/sync_replica_deployment_manifest_test.cpp"]
    record_test = text["tests/sync_replica_bootstrap_record_test.cpp"]
    payload_test = text["tests/sync_replica_file_payload_store_test.cpp"]
    cli_process = text["tools/test_anonsync_replica_cli.py"]
    resume_process = text["tools/test_anonsync_replica_bootstrap_resume.py"]
    verifier = text["tools/verify_release_package.py"]

    init = delimited_body(product, "int command_init(")
    resume = delimited_body(product, "int command_init_resume(")
    create_missing = delimited_body(
        product, "void create_missing_bootstrap_resources_or_throw("
    )
    identity_phase = delimited_body(
        product, "attest_existing_bootstrap_resource_identities_or_throw("
    )
    role_phase = delimited_body(
        product, "attest_existing_bootstrap_role_state_or_throw("
    )
    complete_identity_attestation = delimited_body(
        product, "attest_complete_bootstrap_store_identities_or_throw("
    )
    complete_attestation = delimited_body(
        product, "void attest_complete_bootstrap_store_set_or_throw("
    )
    sealed_creation = delimited_body(
        product, "void create_sealed_bootstrap_database_or_throw("
    )
    promotion = delimited_body(
        product, "void promote_bound_bootstrap_candidate_to_operational_or_throw("
    )
    operational_signatures = (
        "int command_status(",
        "int command_clock_observe(",
        "int command_clock_recover(",
        "int command_enqueue_file(",
        "int command_membership_publish(",
        "SendSessionsExecution execute_send_sessions_or_throw(",
        "int command_reconcile_pull(",
        "ServeSessionsExecution execute_serve_sessions_or_throw(",
    )
    operational = [delimited_body(product, signature) for signature in operational_signatures]

    constructor_declaration = payload_header[
        payload_header.find("SyncReplicaFilePayloadStore(") :
        payload_header.find(
            "~SyncReplicaFilePayloadStore",
            payload_header.find("SyncReplicaFilePayloadStore("),
        )
    ]
    require(
        all(
            token in payload_header
            for token in (
                "enum class SyncReplicaFilePayloadStoreOpenDisposition",
                "ExistingOnly = 1",
                "CreateIfMissing = 2",
            )
        )
        and "SyncReplicaFilePayloadStoreOpenDisposition disposition"
        in constructor_declaration
        and "disposition =" not in constructor_declaration,
        "payload_open_disposition_is_explicit_and_nondefaulted",
        "every payload store construction names whether it owns creation authority",
    )

    payload_identity = delimited_body(
        payload_source, "void ensure_store_identity_or_throw("
    )
    require(
        ordered(
            payload_identity,
            "reconcile_sync_immutable_file_create_new_under_directory_or_throw",
            "ExactAndDirectorySynced",
            "ConflictingEntry",
            "SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly",
            "requires explicit ",
            '"bootstrap"',
            "scan_store_namespace_or_throw",
            "write_sync_file_atomically_create_new_under_directory_or_throw",
        ),
        "existing_only_payload_open_cannot_mint_or_adopt_identity",
        "normal payload observation fails before marker creation or namespace adoption",
    )

    decoder = delimited_body(
        manifest_source, "decode_sync_replica_deployment_manifest_or_throw("
    )
    reader = delimited_body(
        manifest_source, "read_sync_replica_deployment_manifest_or_throw("
    )
    require(
        all(
            token in manifest_header
            for token in (
                "kSyncReplicaDeploymentManifestMaxBytes",
                "decode_sync_replica_deployment_manifest_or_throw",
                "read_sync_replica_deployment_manifest_or_throw",
                "manifest_digest",
            )
        )
        and ordered(
            decoder,
            "exact.size() > kSyncReplicaDeploymentManifestMaxBytes",
            "parse_json_text",
            "require_exact_fields",
            "validate_sync_replica_deployment_manifest_or_throw",
            "manifest.manifest_path != expected_absolute_manifest_path",
            "unsupported authority policy",
            "encode_sync_replica_deployment_manifest_or_throw",
            "std::string_view(canonical) != exact",
        )
        and ordered(
            reader,
            "read_sync_bounded_regular_file_no_symlink_or_throw",
            "decode_sync_replica_deployment_manifest_or_throw",
        ),
        "manifest_decoder_is_bounded_canonical_self_digested_and_path_bound",
        "final manifests and staged records share one strict exact-byte authority grammar",
    )

    encoder = delimited_body(
        manifest_source, "encode_sync_replica_deployment_manifest_or_throw("
    )
    require(
        ordered(
            encoder,
            "canonical_unsigned_document",
            "compute_sync_replica_deployment_manifest_digest_or_throw",
            "encoded.size() > kSyncReplicaDeploymentManifestMaxBytes",
            "parse_json_text(encoded)",
            "return encoded",
        )
        and "cannot be encoded as strict UTF-8 JSON" in encoder,
        "bootstrap_writer_proves_operational_reader_admission_before_mutation",
        "the exact future manifest is bounded strict UTF-8 JSON before a store is created",
    )

    record_path = delimited_body(
        record_source, "sync_replica_bootstrap_record_path_or_throw("
    )
    require(
        "anonsync:replica-bootstrap-record-path:v1\\n" in record_source
        and ".anonsync-replica-bootstrap-" in record_source
        and "sha256_hex" in record_path
        and "absolute_manifest_path.generic_string()" in record_path,
        "bootstrap_record_path_is_deterministic_fixed_length_and_manifest_path_derived",
        "inspection finds one hidden sibling without inheriting an operator-sized basename",
    )

    namespace = delimited_body(
        record_source, "validate_sync_replica_bootstrap_record_namespace_or_throw("
    )
    require(
        all(
            token in namespace
            for token in (
                "manifest_path",
                "replica_db",
                "effect_db",
                "membership_db",
                "anchor_db",
                "kSqliteSidecarSuffixes",
                "payload_root",
                "files_root",
                "collides with",
                "must not be inside",
            )
        ),
        "bootstrap_record_namespace_cannot_alias_selected_authority",
        "the hidden witness cannot be a manifest, SQLite main/sidecar, or mutable-root descendant",
    )

    record_create = delimited_body(
        record_source, "create_sync_replica_bootstrap_record_or_throw("
    )
    record_read = delimited_body(
        record_source,
        "SyncReplicaBootstrapRecord read_sync_replica_bootstrap_record_or_throw(",
    )
    require(
        ordered(
            record_create,
            "validate_sync_replica_bootstrap_record_namespace_or_throw",
            "encode_sync_replica_deployment_manifest_or_throw",
            "write_sync_file_atomically_create_new_no_symlink_or_throw",
            "read_sync_replica_bootstrap_record_or_throw",
            "durable readback differs",
        )
        and ordered(
            record_read,
            "read_sync_bounded_regular_file_no_symlink_or_throw",
            "decode_sync_replica_deployment_manifest_or_throw",
            "validate_sync_replica_bootstrap_record_namespace_or_throw",
            "reconcile_sync_immutable_file_create_new_no_symlink_or_throw",
            "ExactAndDirectorySynced",
        )
        and "second configuration grammar" in record_header,
        "bootstrap_record_is_create_new_exact_durable_read_back_and_single_grammar",
        "visible intent is upgraded to exact file-and-parent durability before it can authorize recovery",
    )

    record_attest = delimited_body(
        record_source, "attest_sync_replica_bootstrap_record_unchanged_or_throw("
    )
    require(
        ordered(
            record_attest,
            "read_sync_replica_bootstrap_record_or_throw",
            "observed.record_path != expected.record_path",
            "observed.exact_manifest_bytes != expected.exact_manifest_bytes",
            "bootstrap record changed",
        ),
        "bootstrap_record_is_reopened_and_byte_attested_before_commit",
        "a cooperative recovery cannot switch configuration between materialization and final publication",
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
            "encode_sync_replica_deployment_manifest_or_throw",
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw",
            "create_sync_replica_bootstrap_record_or_throw",
        )
        and "-journal" in product
        and "-wal" in product
        and "-shm" in product,
        "fresh_init_proves_whole_namespace_before_first_durable_mutation",
        "manifest, record, DB families, payload root, and files root are clean before record publication",
    )

    require(
        ordered(
            init,
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw",
            "create_sync_replica_bootstrap_record_or_throw",
            "inspect_bootstrap_resource_inventory_or_throw",
            "require_fresh_inventory_after_bootstrap_record_or_throw",
            "create_missing_bootstrap_resources_or_throw",
            "attest_complete_bootstrap_store_set_or_throw",
            "attest_sync_replica_bootstrap_record_unchanged_or_throw",
            "manifest_publication.publish_or_throw()",
            "std::cout << exact_manifest",
        )
        and "No temp file or final entry is created until" in atomic_header,
        "record_is_first_durable_mutation_and_manifest_is_final_commit_cutpoint",
        "an interrupted bootstrap has explicit intent but cannot fabricate committed operational authority",
    )

    require(
        create_missing.count("create_sealed_bootstrap_database_or_throw") == 4
        and create_missing.count(
            "SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing"
        ) == 1
        and "DatabaseOpenDisposition::" not in create_missing
        and ordered(
            sealed_creation,
            "open_detached_bootstrap_database_or_throw",
            "initialize_detached_sqlite_deployment_binding_or_throw",
            "initialize_and_verify_role",
            "SealedSqliteSnapshot::capture_database",
            "require_fresh_database_family_or_throw",
            "publish_exact_copy_atomically_create_new_or_throw",
            "open_bound_bootstrap_candidate_or_throw",
            "promote_bound_bootstrap_candidate_to_operational_or_throw",
        ),
        "shared_creation_frontier_seals_binding_and_role_before_path_publication",
        "fresh init and recovery construct each role only after detached exact binding, then publish one complete image create-new",
    )

    require(
        ordered(
            complete_identity_attestation,
            "inspect_bootstrap_resource_inventory_or_throw",
            "missing_store_count",
            "selected store set remains incomplete",
            "attest_existing_bootstrap_resource_identities_or_throw",
            "CompleteBootstrapStoreAuthorities",
            ".sqlite = std::move(authorities)",
        )
        and all(
            token not in complete_identity_attestation
            for token in (
                "attest_existing_bootstrap_role_state_or_throw",
                "reconcile_complete_bootstrap_membership_pair_or_throw",
                "create_missing_bootstrap_resources_or_throw",
                "SyncReplicaSqliteOwner",
                "SyncReplicaFileEffectSqliteOwner",
                "SyncReplicaTlsMembershipSqliteOwner",
                "SyncReplicaTlsMembershipAnchorSqliteOwner",
            )
        )
        and ordered(
            complete_attestation,
            "attest_complete_bootstrap_store_identities_or_throw",
            "attest_existing_bootstrap_role_state_or_throw",
            "reconcile_complete_bootstrap_membership_pair_or_throw",
        ),
        "committed_identity_attestation_retains_handles_and_is_separate_from_role_repair",
        "a committed replay proves completeness and binding without entering schema initialization or membership reconciliation",
    )

    committed_manifest_attestation = delimited_body(
        product, "attest_committed_manifest_matches_bootstrap_record_or_throw("
    )
    require(
        ordered(
            committed_manifest_attestation,
            "read_sync_bounded_regular_file_no_symlink_or_throw",
            "decode_sync_replica_deployment_manifest_or_throw",
            "exact != record.exact_manifest_bytes",
            "reconcile_sync_immutable_file_create_new_no_symlink_or_throw",
            "ExactAndDirectorySynced",
        ),
        "visible_final_manifest_is_reconciled_to_a_durable_commit_cutpoint",
        "committed resume syncs and re-proves the exact final file and parent before accepting success",
    )

    require(
        ordered(
            resume,
            "read_sync_replica_bootstrap_record_or_throw",
            "path_is_absent_or_throw",
            "attest_committed_manifest_matches_bootstrap_record_or_throw",
            "attest_complete_bootstrap_store_identities_or_throw",
            "attest_sync_replica_bootstrap_record_unchanged_or_throw",
            "std::cout << record.exact_manifest_bytes",
        ),
        "committed_resume_requires_exact_record_and_identity_bound_complete_store_set",
        "an existing final manifest must equal the record while schema initialization, membership reconciliation, and missing-store creation remain out of scope",
    )

    require(
        ordered(
            resume,
            "prepare_sync_json_file_atomically_create_new_no_symlink_or_throw",
            "inspect_bootstrap_resource_inventory_or_throw",
            "attest_existing_bootstrap_resource_identities_or_throw",
            "DatabaseOpenDisposition::ExistingBootstrapCandidate",
            "promote_existing_bootstrap_sqlite_authorities_or_throw",
            "attest_existing_bootstrap_role_state_or_throw",
            "missing_store_count",
            "advanced beyond bootstrap genesis",
            "existing = BootstrapExistingSqliteAuthorities{}",
            "create_missing_bootstrap_resources_or_throw",
            "attest_complete_bootstrap_store_set_or_throw",
            "attest_sync_replica_bootstrap_record_unchanged_or_throw",
            "manifest_publication.publish_or_throw()",
        )
        and "DatabaseOpenDisposition disposition" in identity_phase
        and identity_phase.count("open_bound_bootstrap_candidate_or_throw") == 1
        and identity_phase.count("open_bound_operational_database_or_throw") == 1
        and "BootstrapExistingSqliteAuthorities authorities" in identity_phase
        and "ProductSqliteDatabaseAuthority& database" in promotion
        and all(
            token in promotion
            for token in (
                "require_sealed_rollback_sidecars_absent_or_throw",
                "durability pin",
                "database.read_bounded_main_file_or_throw",
                "database.sync_main_file_and_parent_directory_or_throw",
                "exact_before != exact_after",
                "PRAGMA main.journal_mode=WAL;",
                "post-promotion binding",
                "post-promotion path attestation",
            )
        )
        and all(
            token in role_phase
            for token in (
                "replica_snapshot_is_bootstrap_genesis",
                "payload_snapshot_is_bootstrap_genesis",
                "effect_snapshot_is_bootstrap_genesis",
                "membership_snapshot_is_bootstrap_genesis",
                "membership_anchor_snapshot_is_bootstrap_genesis",
                "files_root_empty",
            )
        ),
        "uncommitted_resume_is_identity_first_promoted_then_genesis_gated",
        "every present identity is proven on retained handles, rollback images are promoted only after set-wide proof, and missing resources require genesis",
    )

    require(
        ordered(
            complete_identity_attestation,
            "inspect_bootstrap_resource_inventory_or_throw",
            "missing_store_count",
            "attest_existing_bootstrap_resource_identities_or_throw",
            "return CompleteBootstrapStoreAuthorities",
        )
        and ordered(
            complete_attestation,
            "attest_complete_bootstrap_store_identities_or_throw",
            "attest_existing_bootstrap_role_state_or_throw",
            "reconcile_complete_bootstrap_membership_pair_or_throw",
        ),
        "complete_store_set_is_reinspected_with_retained_handles_and_reconciled_before_commit",
        "postcreation success depends on a newly inspected exact store set and role proof over the same opened authorities",
    )

    raw_config_reads = (
        'options.one("replica-db")',
        'options.one("payload-root")',
        'options.one("effect-db")',
        'options.one("files-root")',
        'options.one("membership-db")',
        'options.one("anchor-db")',
        'options.one("folder")',
        'options.one("local-device")',
        'options.one("local-epoch")',
        "max_payload_from_options(options)",
    )
    require(
        all(
            body.count("load_operational_deployment_manifest_or_throw") == 1
            and not any(token in body for token in raw_config_reads)
            for body in operational
        )
        and product.count("load_operational_deployment_manifest_or_throw(") == 9,
        "operational_commands_derive_configuration_only_from_committed_manifest",
        "store paths, local actor, folder, and payload ceiling cannot be mixed from raw options",
    )

    status = operational[0]
    mutable_operational = operational[1:]
    require(
        all("open_database_or_throw" not in body for body in operational)
        and status.count("open_bound_forensic_database_or_throw") == 4
        and "open_bound_operational_database_or_throw" not in status
        and "SyncReplicaFilePayloadStoreOpenDisposition::ReadOnlyInspect" in status
        and "SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing"
        not in status
        and sum(
            body.count("open_bound_operational_database_or_throw")
            for body in mutable_operational
        ) == 11
        and all(
            "open_bound_forensic_database_or_throw" not in body
            for body in mutable_operational
        )
        and "SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing"
        not in "".join(operational),
        "operational_store_opens_are_existing_only_and_bound",
        "status observes four bound forensic databases and a read-only payload store; mutable commands retain the exact existing-only operational frontier",
    )

    require(
        all(
            token in product
            for token in (
                'sync_replica_session_supervisor.hpp',
                'options, "send-one", 1U, std::nullopt',
                'options, "serve-one", 1U, std::nullopt',
                'max_sessions_from_options(options)',
                'max_runtime_from_options(options)',
                'kSyncReplicaSessionSupervisorMaximumSessions',
                'kSyncReplicaSessionSupervisorMaximumRuntimeSeconds',
            )
        ),
        "bounded_session_wrappers_delegate_to_manifest_owned_executors",
        "batching adds no raw deployment configuration or alternate SQLite bootstrap frontier",
    )

    require(
        "class JsonParser" in parser_source
        and "parse_json_text" in parser_header
        and "add_library(anonsync_json_parser STATIC" in cmake
        and "anonsync_json_parser" in cmake,
        "strict_json_parser_is_one_dependency_light_owner",
        "manifest and record decoding do not duplicate a tolerant configuration parser",
    )

    require(
        all(
            token in manifest_test
            for token in (
                "exact decoding preserves the complete sender authority",
                "copying exact bytes to another pathname cannot duplicate authority",
                "unknown fields cannot acquire future authority by parser tolerance",
                "bootstrap cannot publish a manifest operational code cannot read",
            )
        )
        and all(
            token in record_test
            for token in (
                "pathname derivation is deterministic",
                "private mode 0600",
                "bootstrap-record duplicate fixture",
                "bootstrap-record copied fixture",
                "bootstrap-record tampered fixture",
                "deterministic record namespace cannot alias",
            )
        )
        and all(
            token in payload_test
            for token in (
                "existing-only observation left an artifact",
                "existing-only mutation left an artifact",
                "existing-only observation adopted preseeded bytes",
            )
        ),
        "compiled_tests_pin_manifest_record_and_payload_authority_edges",
        "exact decoding, copied/tampered records, private publication, and noncreating payload opens are executable invariants",
    )

    require(
        all(
            token in cli_process
            for token in (
                "missing-manifest operation minted deployment or payload authority",
                "copied manifest reached the sender database",
                "tampered manifest reached its payload store",
                "operational payload open minted identity into an empty replacement",
            )
        )
        and all(
            token in resume_process
            for token in (
                "committed init-resume",
                "complete advanced resume",
                "partial sender resume",
                "foreign-binding rejection",
                "advanced beyond bootstrap genesis",
                "committed missing-store refusal",
                "orphan-sidecar refusal",
                "sealed rollback-image resume",
                "rollback-sidecar rejection",
                "unbound SQLite rejection",
                "copied bootstrap record",
            )
        ),
        "process_tests_pin_manifest_gate_and_adversarial_recovery_cutpoints",
        "the shipped executable proves exact idempotence, bounded completion, two-phase rejection, and noncreation",
    )

    require(
        all(
            token in cmake
            for token in (
                "anonsync_sync_replica_bootstrap_record",
                "anonsync_sync_replica_bootstrap_record_test",
                "anonsync_replica_bootstrap_resume_process_test",
                "anonsync_replica_bootstrap_authority_source_audit",
            )
        ),
        "record_library_compiled_test_process_test_and_audit_are_registered",
        "ordinary CMake and CTest validation retain the recovery authority surface",
    )

    require(
        "revision_number is not None and revision_number >= 900" in verifier
        and all(
            token in verifier
            for token in (
                '"src/sync_replica_bootstrap_record.hpp"',
                '"src/sync_replica_bootstrap_record.cpp"',
                '"tests/sync_replica_bootstrap_record_test.cpp"',
                '"tools/test_anonsync_replica_bootstrap_resume.py"',
                '"CRASH_RECOVERABLE_BOOTSTRAP_RECORD_AND_IDEMPOTENT_RESUME_AUDIT_rev0900.md"',
                '"REVISION_NOTES_rev0900.md"',
            )
        ),
        "release_verifier_pins_rev0900_recovery_surface",
        "a rev0900 package cannot omit the record owner, proof, audit, or handoff documents",
    )

    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
