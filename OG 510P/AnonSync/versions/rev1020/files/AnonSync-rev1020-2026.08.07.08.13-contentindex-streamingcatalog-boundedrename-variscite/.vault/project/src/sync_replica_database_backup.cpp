#include "sync_replica_database_backup.hpp"

#if !defined(_WIN32)

#include "persistence/sqlite_snapshot_seal.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_replica_database_artifact_internal.hpp"
#include "sync_replica_deployment_identity.hpp"
#include "sync_replica_file_effect_sqlite_owner.hpp"
#include "sync_replica_folder_process.hpp"
#include "sync_replica_folder_scan_owner.hpp"
#include "sync_replica_operational_database.hpp"
#include "sync_replica_peer_service_singleton.hpp"
#include "sync_replica_tls_membership_anchor_sqlite_owner.hpp"
#include "sync_replica_tls_membership_sqlite_owner.hpp"
#include "sync_replica_tls_policy_sqlite_profile.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <filesystem>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {

namespace fs = std::filesystem;
namespace artifact_detail = sync_replica_database_artifact_detail;

namespace {

[[nodiscard]] fs::path database_path_for_role_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    const auto require_selected = [&](const auto& selected,
                                      std::string_view name) -> fs::path {
        if (!selected.has_value()) {
            throw std::invalid_argument(
                label + " requires " + std::string(name) +
                " in the deployment manifest");
        }
        return *selected;
    };
    switch (role) {
        case SyncReplicaSqliteDeploymentRole::Replica:
            return deployment.replica_db;
        case SyncReplicaSqliteDeploymentRole::FileEffect:
            return require_selected(deployment.effect_db, "effect_db");
        case SyncReplicaSqliteDeploymentRole::TlsMembership:
            return require_selected(
                deployment.membership_db, "membership_db");
        case SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor:
            return require_selected(deployment.anchor_db, "anchor_db");
        case SyncReplicaSqliteDeploymentRole::FolderCatalog:
            if (!deployment.files_root.has_value()) {
                throw std::invalid_argument(
                    label + " requires files_root in the deployment manifest");
            }
            return sync_replica_folder_catalog_path_or_throw(
                deployment, label + " folder-catalog path");
    }
    throw std::invalid_argument(label + " database role is invalid");
}

[[nodiscard]] SyncReplicaSqliteDeploymentBinding
binding_for_role_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    SyncReplicaSqliteDeploymentRole role,
    const std::string& label) {
    SyncReplicaSqliteDeploymentBinding binding{
        .deployment = sync_replica_deployment_identity_or_throw(
            deployment, label + " deployment identity"),
        .role = role,
        .database_path = database_path_for_role_or_throw(
            deployment, role, label),
    };
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        binding, label + " binding");
    return binding;
}

[[nodiscard]] SyncReplicaRoleDatabaseBackupCutpoint
role_cutpoint_from_replica_snapshot(
    const fs::path& source_path,
    SyncReplicaSqliteSnapshot snapshot) {
    SyncReplicaRoleDatabaseBackupCutpoint cutpoint;
    cutpoint.database_role = SyncReplicaSqliteDeploymentRole::Replica;
    cutpoint.source_database_path = source_path;
    cutpoint.state_generation = snapshot.state_generation;
    cutpoint.logical_record_count =
        static_cast<std::uint64_t>(snapshot.durable.operations.size());
    cutpoint.state_digest = snapshot.cutpoint_digest;
    cutpoint.auxiliary_digest = snapshot.operation_set_digest;
    cutpoint.replica_cutpoint =
        artifact_detail::compact_backup_cutpoint(std::move(snapshot));
    return cutpoint;
}

[[nodiscard]] SyncReplicaRoleDatabaseBackupCutpoint
inspect_role_database_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaDeploymentManifest& deployment,
    SyncReplicaSqliteDeploymentRole role,
    bool detached_image,
    const std::string& label) {
    const SyncReplicaSqliteDeploymentBinding binding =
        binding_for_role_or_throw(deployment, role, label);

    switch (role) {
        case SyncReplicaSqliteDeploymentRole::Replica: {
            SyncReplicaSqliteSnapshot snapshot = detached_image
                ? inspect_sync_replica_sqlite_snapshot_in_attested_detached_read_only_image_or_throw(
                      database, binding, deployment.folder_id,
                      deployment.local_actor,
                      label + " replica current-schema inspection")
                : [&]() {
                      attest_sync_replica_sqlite_deployment_binding_or_throw(
                          database, binding,
                          label + " replica deployment binding");
                      return inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
                          database, deployment.folder_id,
                          deployment.local_actor,
                          label + " replica current-schema inspection");
                  }();
            return role_cutpoint_from_replica_snapshot(
                binding.database_path, std::move(snapshot));
        }
        case SyncReplicaSqliteDeploymentRole::FileEffect: {
            if (!deployment.files_root.has_value()) {
                throw std::invalid_argument(
                    label + " file-effect inspection requires files_root");
            }
            SyncReplicaFileEffectSqliteSnapshot snapshot;
            if (detached_image) {
                attest_sync_replica_sqlite_deployment_binding_in_read_only_detached_image_or_throw(
                    database, binding,
                    label + " file-effect detached deployment binding");
                snapshot =
                    inspect_sync_replica_file_effect_sqlite_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw(
                        database, deployment.folder_id,
                        *deployment.files_root,
                        label + " file-effect detached current-schema inspection");
            } else {
                attest_sync_replica_sqlite_deployment_binding_or_throw(
                    database, binding,
                    label + " file-effect deployment binding");
                snapshot =
                    inspect_sync_replica_file_effect_sqlite_snapshot_without_root_access_or_throw(
                        database, deployment.folder_id,
                        *deployment.files_root,
                        label + " file-effect current-schema inspection");
            }
            return {
                .database_role = role,
                .source_database_path = binding.database_path,
                .state_generation = snapshot.state_generation,
                .logical_record_count =
                    static_cast<std::uint64_t>(snapshot.effects.size()),
                .state_digest = std::move(snapshot.cutpoint_digest),
                .auxiliary_digest =
                    std::move(snapshot.device_usage_digest),
                .replica_cutpoint = std::nullopt,
            };
        }
        case SyncReplicaSqliteDeploymentRole::TlsMembership: {
            SyncReplicaTlsMembershipSqliteSnapshot snapshot;
            if (detached_image) {
                attest_sync_replica_sqlite_deployment_binding_in_read_only_detached_image_or_throw(
                    database, binding,
                    label + " membership detached deployment binding");
                snapshot =
                    inspect_sync_replica_tls_membership_sqlite_snapshot_in_detached_read_only_image_or_throw(
                        database, deployment.folder_id,
                        deployment.local_actor, std::nullopt,
                        label + " membership detached current-schema inspection");
            } else {
                attest_sync_replica_sqlite_deployment_binding_or_throw(
                    database, binding,
                    label + " membership deployment binding");
                snapshot =
                    inspect_sync_replica_tls_membership_sqlite_snapshot_read_only_or_throw(
                        database, deployment.folder_id,
                        deployment.local_actor, std::nullopt,
                        label + " membership current-schema inspection");
            }
            return {
                .database_role = role,
                .source_database_path = binding.database_path,
                .state_generation = snapshot.state_generation,
                .logical_record_count =
                    static_cast<std::uint64_t>(snapshot.history.size()),
                .state_digest = std::move(snapshot.current_chain_digest),
                .auxiliary_digest =
                    std::move(snapshot.current_snapshot_digest),
                .replica_cutpoint = std::nullopt,
            };
        }
        case SyncReplicaSqliteDeploymentRole::TlsMembershipAnchor: {
            SyncReplicaTlsMembershipAnchorSqliteSnapshot snapshot;
            if (detached_image) {
                attest_sync_replica_sqlite_deployment_binding_in_read_only_detached_image_or_throw(
                    database, binding,
                    label + " membership-anchor detached deployment binding");
                snapshot =
                    inspect_sync_replica_tls_membership_anchor_sqlite_snapshot_in_detached_read_only_image_or_throw(
                        database, deployment.folder_id,
                        deployment.local_actor,
                        label + " membership-anchor detached current-schema inspection");
            } else {
                attest_sync_replica_sqlite_deployment_binding_or_throw(
                    database, binding,
                    label + " membership-anchor deployment binding");
                snapshot =
                    inspect_sync_replica_tls_membership_anchor_sqlite_snapshot_read_only_or_throw(
                        database, deployment.folder_id,
                        deployment.local_actor,
                        label + " membership-anchor current-schema inspection");
            }
            return {
                .database_role = role,
                .source_database_path = binding.database_path,
                .state_generation = snapshot.transition_sequence,
                .logical_record_count =
                    static_cast<std::uint64_t>(snapshot.history.size()),
                .state_digest =
                    std::move(snapshot.current_transition_digest),
                .auxiliary_digest =
                    std::move(snapshot.current_anchor.chain_digest),
                .replica_cutpoint = std::nullopt,
            };
        }
        case SyncReplicaSqliteDeploymentRole::FolderCatalog: {
            if (!deployment.files_root.has_value()) {
                throw std::invalid_argument(
                    label + " folder-catalog inspection requires files_root");
            }
            SyncReplicaFolderCatalogSnapshot snapshot = detached_image
                ? inspect_sync_replica_folder_catalog_snapshot_in_attested_detached_read_only_image_without_root_access_or_throw(
                      database, binding, deployment.folder_id,
                      *deployment.files_root,
                      label + " folder-catalog detached current-schema inspection")
                : inspect_sync_replica_folder_catalog_snapshot_read_only_without_root_access_or_throw(
                      database, binding, deployment.folder_id,
                      *deployment.files_root,
                      label + " folder-catalog current-schema inspection");
            return {
                .database_role = role,
                .source_database_path = binding.database_path,
                .state_generation = snapshot.state_generation,
                .logical_record_count =
                    static_cast<std::uint64_t>(snapshot.entries.size()),
                .state_digest = std::move(snapshot.catalog_digest),
                .auxiliary_digest =
                    std::move(snapshot.root_attestation_digest),
                .replica_cutpoint = std::nullopt,
            };
        }
    }
    throw std::invalid_argument(label + " database role is invalid");
}

[[nodiscard]] SyncReplicaRoleDatabaseBackupArtifactObservation
inspect_role_sealed_artifact_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    SyncReplicaSqliteDeploymentRole role,
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
    SyncReplicaRoleDatabaseBackupCutpoint source_cutpoint =
        inspect_role_database_or_throw(
            database, deployment, role, true,
            label + " role-bound inspection");
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

[[nodiscard]] SyncReplicaDatabaseBackupArtifactObservation
legacy_replica_observation_or_throw(
    SyncReplicaRoleDatabaseBackupArtifactObservation observation,
    const std::string& label) {
    if (observation.source_cutpoint.database_role !=
            SyncReplicaSqliteDeploymentRole::Replica ||
        !observation.source_cutpoint.replica_cutpoint.has_value()) {
        throw std::logic_error(
            label + " explicit replica observation lacks its v1 cutpoint");
    }
    return {
        .artifact_path = std::move(observation.artifact_path),
        .artifact_sha256 = std::move(observation.artifact_sha256),
        .artifact_bytes = observation.artifact_bytes,
        .sqlite_page_size = observation.sqlite_page_size,
        .sqlite_page_count = observation.sqlite_page_count,
        .source_cutpoint =
            std::move(*observation.source_cutpoint.replica_cutpoint),
    };
}

}  // namespace

struct SyncReplicaDatabaseBackupOwner::State final {
    static std::string require_label(std::string value) {
        if (value.empty()) {
            throw std::invalid_argument(
                "sync replica database backup owner label is empty");
        }
        return value;
    }

    SyncReplicaDeploymentManifest deployment;
    std::string label;
    SyncReplicaPeerServiceSingletonOwner singleton;

    State(
        SyncReplicaDeploymentManifest deployment_value,
        std::string label_value)
        : deployment(std::move(deployment_value)),
          label(require_label(std::move(label_value))),
          singleton(deployment, label + " deployment singleton") {}
};

SyncReplicaDatabaseBackupOwner::SyncReplicaDatabaseBackupOwner(
    SyncReplicaDeploymentManifest deployment,
    std::string label)
    : state_(std::make_unique<State>(
          std::move(deployment), std::move(label))) {}

SyncReplicaDatabaseBackupOwner::~SyncReplicaDatabaseBackupOwner() noexcept =
    default;

const SyncReplicaDeploymentManifest&
SyncReplicaDatabaseBackupOwner::deployment() const noexcept {
    return state_->deployment;
}

SyncReplicaRoleDatabaseBackupArtifactObservation
SyncReplicaDatabaseBackupOwner::inspect_role_artifact_or_throw(
    SyncReplicaSqliteDeploymentRole database_role,
    const fs::path& absolute_artifact_path) {
    (void)database_path_for_role_or_throw(
        state_->deployment, database_role,
        state_->label + " selected database role");
    artifact_detail::validate_artifact_path_or_throw(
        state_->deployment, absolute_artifact_path,
        state_->label + " artifact inspection path");
    persistence::SealedSqliteSnapshot sealed =
        persistence::SealedSqliteSnapshot::capture(
            absolute_artifact_path,
            state_->label + " bounded artifact capture",
            artifact_detail::backup_seal_policy());
    return inspect_role_sealed_artifact_or_throw(
        state_->deployment, database_role, sealed,
        absolute_artifact_path,
        state_->label + " artifact inspection");
}

SyncReplicaRoleDatabaseBackupArtifactObservation
SyncReplicaDatabaseBackupOwner::create_role_artifact_or_throw(
    SyncReplicaSqliteDeploymentRole database_role,
    const fs::path& absolute_artifact_path) {
    const fs::path source_path = database_path_for_role_or_throw(
        state_->deployment, database_role,
        state_->label + " selected database role");
    artifact_detail::validate_artifact_path_or_throw(
        state_->deployment, absolute_artifact_path,
        state_->label + " artifact output path");
    artifact_detail::preflight_artifact_output_family_create_new_or_throw(
        absolute_artifact_path,
        state_->label + " artifact output preflight");

    SyncReplicaRoleDatabaseBackupArtifactObservation captured;
    {
        SyncReplicaOperationalDatabase source =
            SyncReplicaOperationalDatabase::open_or_throw(
                source_path,
                SyncReplicaOperationalDatabaseOpenDisposition::
                    ExistingForensicReadOnly,
                state_->label + " forensic role-bound backup source");
        const SyncReplicaRoleDatabaseBackupCutpoint before =
            inspect_role_database_or_throw(
                source.handle(), state_->deployment, database_role, false,
                state_->label + " source snapshot before capture");

        persistence::SealedSqliteSnapshot sealed;
        {
            auto source_borrow = borrow_sync_sqlite_serialized_db_or_throw(
                source.handle(),
                state_->label + " serialized source capability");
            sealed = persistence::SealedSqliteSnapshot::capture_database(
                source_borrow.get(),
                state_->label + " bounded canonical live backup",
                artifact_detail::backup_seal_policy());
        }

        captured = inspect_role_sealed_artifact_or_throw(
            state_->deployment, database_role, sealed,
            absolute_artifact_path,
            state_->label + " captured artifact");
        const SyncReplicaRoleDatabaseBackupCutpoint after =
            inspect_role_database_or_throw(
                source.handle(), state_->deployment, database_role, false,
                state_->label + " source snapshot after capture");
        source.verify_open_database_or_throw(
            state_->label + " source final rooted reproof");
        if (before != captured.source_cutpoint ||
            after != captured.source_cutpoint) {
            throw std::runtime_error(
                state_->label +
                " source changed across the exact role-bound backup capture bracket");
        }

        artifact_detail::preflight_artifact_output_family_create_new_or_throw(
            absolute_artifact_path,
            state_->label +
                " artifact output final prepublication reproof");
        sealed.publish_exact_copy_atomically_create_new_or_throw(
            absolute_artifact_path,
            state_->label + " immutable artifact publication");
    }

    SyncReplicaRoleDatabaseBackupArtifactObservation published =
        inspect_role_artifact_or_throw(
            database_role, absolute_artifact_path);
    if (published != captured) {
        throw std::runtime_error(
            state_->label +
            " published artifact differs from the captured role-bound source snapshot");
    }
    return published;
}

SyncReplicaDatabaseBackupArtifactObservation
SyncReplicaDatabaseBackupOwner::inspect_artifact_or_throw(
    const fs::path& absolute_artifact_path) {
    return legacy_replica_observation_or_throw(
        inspect_role_artifact_or_throw(
            SyncReplicaSqliteDeploymentRole::Replica,
            absolute_artifact_path),
        state_->label + " legacy replica artifact inspection");
}

SyncReplicaDatabaseBackupArtifactObservation
SyncReplicaDatabaseBackupOwner::create_artifact_or_throw(
    const fs::path& absolute_artifact_path) {
    return legacy_replica_observation_or_throw(
        create_role_artifact_or_throw(
            SyncReplicaSqliteDeploymentRole::Replica,
            absolute_artifact_path),
        state_->label + " legacy replica artifact creation");
}

}  // namespace anonsync

#endif
