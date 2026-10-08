#include "sync_replica_bootstrap_record.hpp"

#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_bounded_regular_file.hpp"

#include <array>
#include <filesystem>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::string_view kRecordPathDigestDomain =
    "anonsync:replica-bootstrap-record-path:v1\n";
constexpr std::array<std::string_view, 3> kSqliteSidecarSuffixes{
    "-journal",
    "-wal",
    "-shm",
};

void require_canonical_absolute_path(
    const fs::path& path,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "bootstrap-record path label must not be empty");
    }
    if (path.native().find(fs::path::value_type{}) !=
        fs::path::string_type::npos) {
        throw std::invalid_argument(label + " path must not contain NUL");
    }
    if (path.empty() || !path.is_absolute()) {
        throw std::invalid_argument(label + " path must be absolute");
    }
    if (path.lexically_normal() != path) {
        throw std::invalid_argument(
            label + " path must be lexically normalized");
    }
    if (path.parent_path().empty()) {
        throw std::invalid_argument(label + " path has no parent directory");
    }
}

[[nodiscard]] fs::path append_ascii_path_suffix(
    const fs::path& path,
    std::string_view suffix) {
    fs::path::string_type native = path.native();
    for (const char byte : suffix) {
        native.push_back(static_cast<fs::path::value_type>(byte));
    }
    return fs::path(std::move(native));
}

[[nodiscard]] bool path_is_same_or_descendant(
    const fs::path& candidate,
    const fs::path& root) {
    auto candidate_part = candidate.begin();
    for (auto root_part = root.begin(); root_part != root.end();
         ++root_part, ++candidate_part) {
        if (candidate_part == candidate.end() ||
            *candidate_part != *root_part) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    const std::string& bytes) noexcept {
    return {
        reinterpret_cast<const unsigned char*>(bytes.data()),
        bytes.size(),
    };
}

}  // namespace

fs::path sync_replica_bootstrap_record_path_or_throw(
    const fs::path& absolute_manifest_path,
    const std::string& label) {
    require_canonical_absolute_path(absolute_manifest_path, label);
    const std::string digest = sha256_hex(
        std::string(kRecordPathDigestDomain) +
        absolute_manifest_path.generic_string());
    return absolute_manifest_path.parent_path() /
        (".anonsync-replica-bootstrap-" + digest + ".json");
}

void validate_sync_replica_bootstrap_record_namespace_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "bootstrap-record namespace label must not be empty");
    }
    validate_sync_replica_deployment_manifest_or_throw(
        deployment, label + " deployment manifest");
    const fs::path record_path = sync_replica_bootstrap_record_path_or_throw(
        deployment.manifest_path, label + " derived path");

    std::vector<std::pair<std::string, fs::path>> authorities{
        {"manifest_path", deployment.manifest_path},
        {"replica_db", deployment.replica_db},
    };
    if (deployment.effect_db.has_value()) {
        authorities.emplace_back("effect_db", *deployment.effect_db);
    }
    if (deployment.membership_db.has_value()) {
        authorities.emplace_back("membership_db", *deployment.membership_db);
        authorities.emplace_back("anchor_db", *deployment.anchor_db);
    }
    const std::size_t database_count = authorities.size() - 1U;
    for (std::size_t index = 1U; index <= database_count; ++index) {
        const auto database = authorities[index];
        for (const std::string_view suffix : kSqliteSidecarSuffixes) {
            authorities.emplace_back(
                database.first + " SQLite sidecar " + std::string(suffix),
                append_ascii_path_suffix(database.second, suffix));
        }
    }
    for (const auto& [name, path] : authorities) {
        if (record_path == path) {
            throw std::invalid_argument(
                label + " deterministic bootstrap record collides with " +
                name);
        }
    }
    for (const auto& [name, root] :
         std::vector<std::pair<std::string, fs::path>>{
             deployment.payload_root.has_value()
                 ? std::pair<std::string, fs::path>{
                       "payload_root", *deployment.payload_root}
                 : std::pair<std::string, fs::path>{},
             deployment.files_root.has_value()
                 ? std::pair<std::string, fs::path>{
                       "files_root", *deployment.files_root}
                 : std::pair<std::string, fs::path>{},
         }) {
        if (!name.empty() && path_is_same_or_descendant(record_path, root)) {
            throw std::invalid_argument(
                label + " deterministic bootstrap record must not be inside " +
                name);
        }
    }
}

SyncReplicaBootstrapRecord create_sync_replica_bootstrap_record_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "bootstrap-record creation label must not be empty");
    }
    validate_sync_replica_bootstrap_record_namespace_or_throw(
        deployment, label + " namespace");
    const std::string exact =
        encode_sync_replica_deployment_manifest_or_throw(
            deployment, label + " exact manifest");
    const fs::path record_path = sync_replica_bootstrap_record_path_or_throw(
        deployment.manifest_path, label + " path");
    write_sync_file_atomically_create_new_no_symlink_or_throw(
        record_path, byte_span(exact), label + " publication");
    SyncReplicaBootstrapRecord record =
        read_sync_replica_bootstrap_record_or_throw(
            deployment.manifest_path, label + " readback");
    if (record.exact_manifest_bytes != exact) {
        throw std::runtime_error(
            label + " durable readback differs from publication bytes");
    }
    return record;
}

SyncReplicaBootstrapRecord read_sync_replica_bootstrap_record_or_throw(
    const fs::path& absolute_manifest_path,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "bootstrap-record read label must not be empty");
    }
    const fs::path record_path = sync_replica_bootstrap_record_path_or_throw(
        absolute_manifest_path, label + " path");
    std::string exact = read_sync_bounded_regular_file_no_symlink_or_throw(
        record_path, kSyncReplicaDeploymentManifestMaxBytes,
        label + " exact file");
    SyncReplicaDeploymentManifest deployment =
        decode_sync_replica_deployment_manifest_or_throw(
            exact, absolute_manifest_path, label + " manifest bytes");
    validate_sync_replica_bootstrap_record_namespace_or_throw(
        deployment, label + " namespace");
    const SyncImmutableFileReconciliationOutcome durability =
        reconcile_sync_immutable_file_create_new_no_symlink_or_throw(
            record_path, byte_span(exact), label + " durability reconciliation");
    if (durability !=
        SyncImmutableFileReconciliationOutcome::ExactAndDirectorySynced) {
        throw std::runtime_error(
            label + " bootstrap record could not be reconciled as exact and "
            "directory-synced: " +
            sync_immutable_file_reconciliation_outcome_name(durability));
    }
    return {
        .record_path = record_path,
        .deployment = std::move(deployment),
        .exact_manifest_bytes = std::move(exact),
    };
}

void attest_sync_replica_bootstrap_record_unchanged_or_throw(
    const SyncReplicaBootstrapRecord& expected,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "bootstrap-record attestation label must not be empty");
    }
    const SyncReplicaBootstrapRecord observed =
        read_sync_replica_bootstrap_record_or_throw(
            expected.deployment.manifest_path, label + " reread");
    if (observed.record_path != expected.record_path ||
        observed.exact_manifest_bytes != expected.exact_manifest_bytes) {
        throw std::runtime_error(
            label + " bootstrap record changed after the accepted observation");
    }
}

}  // namespace anonsync
