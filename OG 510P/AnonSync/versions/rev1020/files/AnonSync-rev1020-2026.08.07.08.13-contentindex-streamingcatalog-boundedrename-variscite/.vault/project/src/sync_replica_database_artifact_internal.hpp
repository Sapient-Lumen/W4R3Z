#pragma once

#if !defined(_WIN32)

#include "persistence/sqlite_snapshot_geometry.hpp"
#include "persistence/sqlite_snapshot_seal.hpp"
#include "sqlite_path_security.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_replica_database_backup.hpp"
#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_folder_process.hpp"
#include "sync_replica_tls_policy_sqlite_profile.hpp"
#include "sync_sqlite_support.hpp"

#include <array>
#include <exception>
#include <filesystem>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>
#include <vector>

namespace anonsync::sync_replica_database_artifact_detail {

namespace fs = std::filesystem;

inline constexpr std::array<std::string_view, 4U>
    kSqliteArtifactFamilySuffixes{"", "-journal", "-wal", "-shm"};

[[nodiscard]] inline std::array<fs::path, 4U> sqlite_artifact_family_paths(
    const fs::path& database_path) {
    std::array<fs::path, 4U> paths;
    for (std::size_t index = 0U;
         index < kSqliteArtifactFamilySuffixes.size(); ++index) {
        paths[index] = fs::path(
            database_path.string() +
            std::string(kSqliteArtifactFamilySuffixes[index]));
    }
    return paths;
}

[[nodiscard]] inline std::vector<std::string>
sqlite_artifact_sidecar_suffixes() {
    std::vector<std::string> suffixes;
    suffixes.reserve(kSqliteArtifactFamilySuffixes.size() - 1U);
    for (std::size_t index = 1U;
         index < kSqliteArtifactFamilySuffixes.size(); ++index) {
        suffixes.emplace_back(kSqliteArtifactFamilySuffixes[index]);
    }
    return suffixes;
}

[[nodiscard]] inline bool sqlite_artifact_families_overlap(
    const fs::path& left,
    const fs::path& right) {
    const auto left_family = sqlite_artifact_family_paths(left);
    const auto right_family = sqlite_artifact_family_paths(right);
    for (const fs::path& left_member : left_family) {
        for (const fs::path& right_member : right_family) {
            if (left_member == right_member) return true;
        }
    }
    return false;
}

inline void require_disjoint_artifact_families_or_throw(
    const fs::path& left,
    const fs::path& right,
    const std::string& label) {
    if (sqlite_artifact_families_overlap(left, right)) {
        throw std::invalid_argument(
            label + " SQLite artifact families overlap");
    }
}

static_assert(
    kSyncReplicaDatabaseBackupMaximumArtifactBytes <=
    persistence::kMaximumUntrustedSqliteSnapshotBytes);
static_assert(
    kSyncReplicaDatabaseBackupMaximumArtifactPages <=
    persistence::kMaximumUntrustedSqliteSnapshotPages);

[[nodiscard]] inline constexpr persistence::SqliteSnapshotSealPolicy
backup_seal_policy() noexcept {
    return {
        .maximum_bytes = kSyncReplicaDatabaseBackupMaximumArtifactBytes,
        .maximum_pages = kSyncReplicaDatabaseBackupMaximumArtifactPages,
    };
}

// Shared optional-open classifier. Exact ENOENT/not-found is absence; every
// other failed observation preserves the original open/capture diagnostic.
inline void require_exact_path_absence_or_rethrow(
    const fs::path& path,
    const std::exception_ptr& original_failure) {
    std::error_code status_error;
    const fs::file_status status = fs::symlink_status(path, status_error);
    if ((status_error &&
         status_error != std::errc::no_such_file_or_directory) ||
        (!status_error && status.type() != fs::file_type::not_found)) {
        std::rethrow_exception(original_failure);
    }
}

[[nodiscard]] inline bool path_is_same_or_descendant(
    const fs::path& candidate,
    const fs::path& root) {
    auto candidate_it = candidate.begin();
    for (auto root_it = root.begin(); root_it != root.end();
         ++root_it, ++candidate_it) {
        if (candidate_it == candidate.end() || *candidate_it != *root_it) {
            return false;
        }
    }
    return true;
}

inline void validate_artifact_path_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& artifact_path,
    const std::string& label) {
    if (artifact_path.native().find(fs::path::value_type{}) !=
            fs::path::string_type::npos ||
        artifact_path.empty() || !artifact_path.is_absolute() ||
        artifact_path.lexically_normal() != artifact_path) {
        throw std::invalid_argument(
            label + " must be a canonical absolute path without NUL");
    }
    const auto artifact_family = sqlite_artifact_family_paths(artifact_path);
    for (const fs::path& artifact_member : artifact_family) {
        if (artifact_member == deployment.manifest_path) {
            throw std::invalid_argument(
                label + " SQLite family collides with the deployment manifest");
        }
    }

    std::vector<fs::path> active_databases;
    active_databases.reserve(5U);
    active_databases.push_back(deployment.replica_db);
    const auto append_optional_database = [&](const auto& selected) {
        if (selected.has_value()) active_databases.push_back(*selected);
    };
    append_optional_database(deployment.effect_db);
    append_optional_database(deployment.membership_db);
    append_optional_database(deployment.anchor_db);
    if (deployment.files_root.has_value()) {
        active_databases.push_back(
            sync_replica_folder_catalog_path_or_throw(
                deployment, label + " folder catalog path"));
    }
    for (const fs::path& active_database : active_databases) {
        if (sqlite_artifact_families_overlap(
                artifact_path, active_database)) {
            throw std::invalid_argument(
                label + " SQLite family overlaps an active SQLite family");
        }
    }

    for (const auto& root : {deployment.payload_root, deployment.files_root}) {
        if (!root.has_value()) continue;
        for (const fs::path& artifact_member : artifact_family) {
            if (path_is_same_or_descendant(artifact_member, *root)) {
                throw std::invalid_argument(
                    label +
                    " SQLite family must remain outside payload storage and synchronized files");
            }
        }
    }
}

inline void preflight_artifact_output_family_create_new_or_throw(
    const fs::path& artifact_path,
    const std::string& label) {
    // Reject deterministic sidecar conflicts before paying for a complete
    // database capture or publishing the main artifact name. The create-new
    // publisher remains the final main-name race authority, and the subsequent
    // sealed reopen rejects any sidecar that races this bounded preflight.
    SqlitePathFamilyGuard family = guard_sqlite_path_family_or_throw(
        artifact_path, false, sqlite_artifact_sidecar_suffixes(),
        label + " SQLite family preflight");
    if (!family.parent_exists()) {
        throw std::runtime_error(
            label + " parent directory does not exist");
    }
    family.verify_sidecars_absent_or_throw(
        label + " sidecar preflight");
    preflight_sync_file_create_new_no_symlink_or_throw(
        artifact_path, label + " main-name preflight");
    family.verify_sidecars_absent_or_throw(
        label + " final sidecar preflight");
}

[[nodiscard]] inline SyncReplicaDatabaseBackupCutpoint compact_backup_cutpoint(
    SyncReplicaSqliteSnapshot snapshot) {
    return {
        .database_incarnation_sha256 =
            std::move(snapshot.database_incarnation_sha256),
        .database_recovery_epoch = snapshot.database_recovery_epoch,
        .state_generation = snapshot.state_generation,
        .policy_generation = snapshot.policy_generation,
        .outbox_time_high_water_epoch = snapshot.outbox_time_high_water_epoch,
        .local_operation_digest = std::move(snapshot.local_operation_digest),
        .operation_set_digest = std::move(snapshot.operation_set_digest),
        .evidence_set_digest = std::move(snapshot.evidence_set_digest),
        .visible_state_digest = std::move(snapshot.visible_state_digest),
        .outbox_digest = std::move(snapshot.outbox_digest),
        .outbox_clock_digest = std::move(snapshot.outbox_clock_digest),
        .historical_version_pin_count =
            snapshot.historical_version_pin_count,
        .historical_version_pin_set_digest =
            std::move(snapshot.historical_version_pin_set_digest),
        .cutpoint_digest = std::move(snapshot.cutpoint_digest),
    };
}

[[nodiscard]] inline SyncReplicaDatabaseBackupArtifactObservation
inspect_sealed_artifact_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    persistence::SealedSqliteSnapshot& sealed,
    const fs::path& artifact_path,
    const std::string& label) {
    SyncSqliteDbHandleSlot database = sealed.open_database_owner_or_throw(
        label + " read-only detached database");
    configure_sync_replica_tls_policy_sqlite_read_only_connection_or_throw(
        database, label + " detached connection profile");
    sqlite_exec_or_throw(
        database, "PRAGMA temp_store=MEMORY;PRAGMA foreign_keys=ON;",
        label + " detached observer pragmas");
    const SyncReplicaSqliteDeploymentBinding binding =
        sync_replica_primary_database_binding_or_throw(
            deployment, label + " deployment binding");
    SyncReplicaDatabaseBackupCutpoint source_cutpoint = compact_backup_cutpoint(
        inspect_sync_replica_sqlite_snapshot_in_attested_detached_read_only_image_or_throw(
            database, binding, deployment.folder_id, deployment.local_actor,
            label + " current-schema inspection"));
    sealed.verify_unchanged_or_throw(label + " final resident-byte reproof");
    return {
        .artifact_path = artifact_path,
        .artifact_sha256 = sealed.sha256_hex(),
        .artifact_bytes = sealed.byte_count(),
        .sqlite_page_size = sealed.page_size(),
        .sqlite_page_count = sealed.page_count(),
        .source_cutpoint = std::move(source_cutpoint),
    };
}

[[nodiscard]] inline bool recovery_successor_matches(
    const SyncReplicaDatabaseBackupCutpoint& before,
    const SyncReplicaDatabaseBackupCutpoint& after) noexcept {
    if (before.database_recovery_epoch ==
            std::numeric_limits<std::uint64_t>::max() ||
        before.state_generation == std::numeric_limits<std::uint64_t>::max()) {
        return false;
    }
    return after.database_incarnation_sha256 ==
               before.database_incarnation_sha256 &&
           after.database_recovery_epoch ==
               before.database_recovery_epoch + 1U &&
           after.state_generation == before.state_generation + 1U &&
           after.policy_generation == before.policy_generation &&
           after.outbox_time_high_water_epoch ==
               before.outbox_time_high_water_epoch &&
           after.local_operation_digest == before.local_operation_digest &&
           after.operation_set_digest == before.operation_set_digest &&
           after.evidence_set_digest == before.evidence_set_digest &&
           after.visible_state_digest == before.visible_state_digest &&
           after.outbox_digest == before.outbox_digest &&
           after.outbox_clock_digest == before.outbox_clock_digest &&
           after.historical_version_pin_count ==
               before.historical_version_pin_count &&
           after.historical_version_pin_set_digest ==
               before.historical_version_pin_set_digest;
}

}  // namespace anonsync::sync_replica_database_artifact_detail

#endif
