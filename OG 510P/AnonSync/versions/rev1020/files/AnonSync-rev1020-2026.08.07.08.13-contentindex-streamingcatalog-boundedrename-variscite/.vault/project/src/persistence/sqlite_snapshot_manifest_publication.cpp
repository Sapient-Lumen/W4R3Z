#include "sqlite_snapshot_manifest_publication.hpp"

#include "frozen_publication_primitives.hpp"
#include "sha256_digest.hpp"
#include "sqlite_replay_ledger_schema_contract.hpp"

#include <stdexcept>
#include <utility>

namespace anonsync::persistence {
namespace {

using publication_detail::BoundedMachineText;
using publication_detail::append_json_member_prefix;
using publication_detail::append_json_string;
using publication_detail::append_line;
using publication_detail::is_base64url_without_padding;
using publication_detail::is_canonical_utc;
using publication_detail::is_lower_hex_sha256;
using publication_detail::require_nonempty_bounded_control_free;

void require_revision_text(std::string_view value, std::string_view label) {
    require_nonempty_bounded_control_free(
        value, kSqliteSnapshotManifestMaximumRevisionBytes, label);
}

void validate_fields_or_throw(
    const SqliteSnapshotManifestPayloadFields& fields) {
    require_revision_text(fields.manifest_revision_id,
                          "SQLite snapshot manifest revision id");
    require_revision_text(fields.parent_revision,
                          "SQLite snapshot manifest parent revision");
    if (!is_canonical_utc(fields.manifest_issued_at)) {
        throw std::runtime_error(
            "SQLite snapshot manifest issued-at is not canonical UTC");
    }
    if (!is_lower_hex_sha256(fields.snapshot_sha256)) {
        throw std::runtime_error(
            "SQLite snapshot manifest snapshot digest is invalid");
    }
    if (fields.backend_name != kSqliteReplayLedgerBackendName) {
        throw std::runtime_error(
            "SQLite snapshot manifest backend_name must be sqlite-wal");
    }
    if (fields.backend_profile_backend_name !=
        kSqliteReplayLedgerBackendName) {
        throw std::runtime_error(
            "SQLite snapshot manifest backend profile name mismatch");
    }
    if (fields.schema_version != kSqliteReplayLedgerSchemaVersion) {
        throw std::runtime_error(
            "SQLite snapshot manifest schema version mismatch");
    }
    if (fields.entry_material_version !=
        kSqliteReplayLedgerEntryMaterialVersion) {
        throw std::runtime_error(
            "SQLite snapshot manifest entry material version mismatch");
    }
    if (fields.hash_algorithm != kSqliteReplayLedgerHashAlgorithm) {
        throw std::runtime_error(
            "SQLite snapshot manifest hash algorithm mismatch");
    }
    if (fields.commit_protocol != kSqliteReplayLedgerCommitProtocol) {
        throw std::runtime_error(
            "SQLite snapshot manifest commit protocol mismatch");
    }
    if (fields.line_count <= 0 ||
        fields.line_count > kSqliteSnapshotManifestMaximumExactJsonInteger) {
        throw std::runtime_error(
            "SQLite snapshot manifest line_count is outside exact JSON range");
    }
    if (!is_lower_hex_sha256(fields.head_hash)) {
        throw std::runtime_error(
            "SQLite snapshot manifest head hash is invalid");
    }
    require_revision_text(fields.expected_revision,
                          "SQLite snapshot manifest expected revision");
    require_revision_text(fields.source_controls_revision,
                          "SQLite snapshot manifest source controls revision");
    require_nonempty_bounded_control_free(
        fields.manifest_subject,
        kSqliteSnapshotManifestMaximumSubjectBytes,
        "SQLite snapshot manifest subject");
    require_nonempty_bounded_control_free(
        fields.durability_ceiling,
        kSqliteSnapshotManifestMaximumDurabilityCeilingBytes,
        "SQLite snapshot manifest durability ceiling");
}

}  // namespace

FrozenSqliteSnapshotManifestV2Payload
FrozenSqliteSnapshotManifestV2Payload::freeze_or_throw(
    SqliteSnapshotManifestPayloadFields fields) {
    validate_fields_or_throw(fields);
    return FrozenSqliteSnapshotManifestV2Payload(std::move(fields));
}

std::string sqlite_snapshot_manifest_v2_signing_input_or_throw(
    const FrozenSqliteSnapshotManifestV2Payload& payload) {
    const auto& fields = payload.fields();
    BoundedMachineText out(
        kSqliteSnapshotManifestMaximumSigningInputBytes,
        "SQLite snapshot manifest signing input");
    append_line(out, kSqliteSnapshotManifestV2Format);
    append_line(out, fields.manifest_revision_id);
    append_line(out, fields.parent_revision);
    append_line(out, fields.manifest_issued_at);
    append_line(out, fields.snapshot_sha256);
    append_line(out, fields.backend_name);
    append_line(out, fields.backend_profile_backend_name);
    out.append_decimal(fields.schema_version);
    out.append('\n');
    append_line(out, fields.entry_material_version);
    append_line(out, fields.hash_algorithm);
    append_line(out, fields.commit_protocol);
    out.append_decimal(fields.line_count);
    out.append('\n');
    append_line(out, fields.head_hash);
    append_line(out, fields.expected_revision);
    append_line(out, fields.source_controls_revision);
    append_line(out, fields.manifest_subject);
    append_line(out, fields.durability_ceiling);
    return std::move(out).finish();
}

SqliteSnapshotManifestV2Publication
SqliteSnapshotManifestV2Publication::bind_or_throw(
    FrozenSqliteSnapshotManifestV2Payload payload,
    std::string payload_signing_input_sha256,
    SqliteSnapshotManifestSignatureFields signature) {
    if (!is_lower_hex_sha256(payload_signing_input_sha256)) {
        throw std::runtime_error(
            "SQLite snapshot manifest signing-input digest is invalid");
    }
    const std::string exact_signing_input =
        sqlite_snapshot_manifest_v2_signing_input_or_throw(payload);
    if (payload_signing_input_sha256 !=
        anonsync::sha256_hex(exact_signing_input)) {
        throw std::runtime_error(
            "SQLite snapshot manifest signing-input digest does not bind the frozen payload");
    }
    require_nonempty_bounded_control_free(
        signature.kid, kSqliteSnapshotManifestMaximumSignerKidBytes,
        "SQLite snapshot manifest signer kid");
    if (signature.signature_b64url.size() >
        kSqliteSnapshotManifestMaximumSignatureBytes) {
        throw std::runtime_error(
            "SQLite snapshot manifest signature exceeds byte budget");
    }
    if (!is_base64url_without_padding(signature.signature_b64url)) {
        throw std::runtime_error(
            "SQLite snapshot manifest signature is not unpadded base64url");
    }
    return SqliteSnapshotManifestV2Publication(
        std::move(payload), std::move(payload_signing_input_sha256),
        std::move(signature));
}

std::string encode_sqlite_snapshot_manifest_v2_json_or_throw(
    const SqliteSnapshotManifestV2Publication& publication) {
    const auto& fields = publication.payload().fields();
    const auto& signature = publication.signature();
    BoundedMachineText out(
        kSqliteSnapshotManifestMaximumJsonBytes,
        "SQLite snapshot manifest JSON");

    out.append("{\n");
    append_json_member_prefix(out, "  ", "format");
    append_json_string(out, kSqliteSnapshotManifestV2Format);
    out.append(",\n");
    append_json_member_prefix(out, "  ", "revision_id");
    append_json_string(out, fields.manifest_revision_id);
    out.append(",\n");
    append_json_member_prefix(out, "  ", "parent_revision");
    append_json_string(out, fields.parent_revision);
    out.append(",\n  \"payload\": {\n");
    append_json_member_prefix(out, "    ", "format");
    append_json_string(out, kSqliteSnapshotManifestV2PayloadFormat);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "manifest_revision_id");
    append_json_string(out, fields.manifest_revision_id);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "parent_revision");
    append_json_string(out, fields.parent_revision);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "manifest_issued_at");
    append_json_string(out, fields.manifest_issued_at);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "backend_name");
    append_json_string(out, fields.backend_name);
    out.append(",\n    \"backend_profile\": {\n");
    append_json_member_prefix(out, "      ", "backend_name");
    append_json_string(out, fields.backend_profile_backend_name);
    out.append(",\n");
    append_json_member_prefix(out, "      ", "schema_version");
    out.append_decimal(fields.schema_version);
    out.append(",\n");
    append_json_member_prefix(out, "      ", "entry_material_version");
    append_json_string(out, fields.entry_material_version);
    out.append(",\n");
    append_json_member_prefix(out, "      ", "hash_algorithm");
    append_json_string(out, fields.hash_algorithm);
    out.append(",\n");
    append_json_member_prefix(out, "      ", "commit_protocol");
    append_json_string(out, fields.commit_protocol);
    out.append("\n    },\n");
    append_json_member_prefix(out, "    ", "snapshot_sha256");
    append_json_string(out, fields.snapshot_sha256);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "line_count");
    out.append_decimal(fields.line_count);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "head_hash");
    append_json_string(out, fields.head_hash);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "expected_revision");
    append_json_string(out, fields.expected_revision);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "source_controls_revision");
    append_json_string(out, fields.source_controls_revision);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "manifest_subject");
    append_json_string(out, fields.manifest_subject);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "durability_ceiling");
    append_json_string(out, fields.durability_ceiling);
    out.append("\n  },\n");
    append_json_member_prefix(out, "  ", "payload_signing_input_sha256");
    append_json_string(out, publication.payload_signing_input_sha256());
    out.append(",\n  \"signature\": {\n");
    append_json_member_prefix(out, "    ", "alg");
    append_json_string(out, "RS256");
    out.append(",\n");
    append_json_member_prefix(out, "    ", "kid");
    append_json_string(out, signature.kid);
    out.append(",\n");
    append_json_member_prefix(out, "    ", "signature_b64url");
    append_json_string(out, signature.signature_b64url);
    out.append("\n  },\n");
    append_json_member_prefix(out, "  ", "blocked_claim");
    append_json_string(
        out,
        "Frozen local snapshot publication; not remote durability, key custody, or distributed convergence evidence.");
    out.append("\n}\n");

    return std::move(out).finish();
}

}  // namespace anonsync::persistence
