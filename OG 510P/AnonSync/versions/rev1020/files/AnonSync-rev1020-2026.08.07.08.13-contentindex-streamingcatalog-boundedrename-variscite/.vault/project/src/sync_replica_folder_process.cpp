#include "sync_replica_folder_process.hpp"

#if !defined(_WIN32)

#include "sync_replica_operational_database.hpp"

#include <array>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::array<std::string_view, 4> kSqliteFamilySuffixes{
    "", "-journal", "-wal", "-shm"};

static_assert(
    SyncReplicaFolderScanLimits{}.max_catalog_entries ==
    kSyncReplicaFilePayloadStoreProductionMaxEntries);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}.maximum_regular_files ==
    kSyncReplicaFilePayloadStoreProductionMaxEntries);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}.maximum_entries >=
    SyncReplicaFolderConvergencePassLimits{}.maximum_regular_files);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}.maximum_remote_paths ==
    kSyncReplicaFilePayloadStoreProductionMaxEntries);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}
            .maximum_local_scan_segment_regular_files > 0U);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}
            .maximum_local_scan_segment_regular_files <=
    SyncReplicaFolderConvergencePassLimits{}.maximum_regular_files);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}
            .maximum_remote_apply_operations >=
    SyncReplicaFolderConvergencePassLimits{}
            .maximum_local_scan_segment_regular_files);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}
            .maximum_remote_apply_operations <=
    SyncReplicaFolderConvergencePassLimits{}.maximum_remote_paths);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}
            .maximum_remote_inspection_paths > 0U);
static_assert(
    SyncReplicaFolderConvergencePassLimits{}
            .maximum_remote_inspection_paths <=
    SyncReplicaFolderConvergencePassLimits{}.maximum_remote_paths);

[[nodiscard]] fs::path append_ascii_suffix(
    const fs::path& path,
    std::string_view suffix) {
    fs::path::string_type native = path.native();
    for (const char byte : suffix) {
        native.push_back(static_cast<fs::path::value_type>(byte));
    }
    return fs::path(std::move(native));
}

[[nodiscard]] bool same_or_descendant(
    const fs::path& candidate,
    const fs::path& ancestor) {
    auto candidate_part = candidate.begin();
    auto ancestor_part = ancestor.begin();
    for (; ancestor_part != ancestor.end();
         ++ancestor_part, ++candidate_part) {
        if (candidate_part == candidate.end() ||
            *candidate_part != *ancestor_part) {
            return false;
        }
    }
    return true;
}

void require_catalog_namespace_disjoint_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& catalog,
    const std::string& label) {
    using NamedPath = std::pair<std::string, fs::path>;
    std::vector<NamedPath> selected{
        {"manifest_path", deployment.manifest_path},
    };
    auto append_database_family = [&selected](
                                      std::string name,
                                      const fs::path& path) {
        for (const std::string_view suffix : kSqliteFamilySuffixes) {
            selected.emplace_back(
                suffix.empty() ? name :
                    name + " SQLite sidecar " + std::string(suffix),
                append_ascii_suffix(path, suffix));
        }
    };
    append_database_family("replica_db", deployment.replica_db);
    if (deployment.effect_db.has_value()) {
        append_database_family("effect_db", *deployment.effect_db);
    }
    if (deployment.membership_db.has_value()) {
        append_database_family("membership_db", *deployment.membership_db);
        append_database_family("anchor_db", *deployment.anchor_db);
    }

    std::vector<NamedPath> catalog_family;
    for (const std::string_view suffix : kSqliteFamilySuffixes) {
        catalog_family.emplace_back(
            suffix.empty() ? "folder_catalog" :
                "folder_catalog SQLite sidecar " + std::string(suffix),
            append_ascii_suffix(catalog, suffix));
    }
    for (const auto& [catalog_name, catalog_path] : catalog_family) {
        for (const auto& [selected_name, selected_path] : selected) {
            if (catalog_path == selected_path) {
                throw std::invalid_argument(
                    label + " derived " + catalog_name + " collides with " +
                    selected_name);
            }
        }
    }

    std::vector<NamedPath> roots;
    if (deployment.payload_root.has_value()) {
        roots.emplace_back("payload_root", *deployment.payload_root);
    }
    if (deployment.files_root.has_value()) {
        roots.emplace_back("files_root", *deployment.files_root);
    }
    for (const auto& [catalog_name, catalog_path] : catalog_family) {
        for (const auto& [root_name, root_path] : roots) {
            if (same_or_descendant(catalog_path, root_path) ||
                same_or_descendant(root_path, catalog_path)) {
                throw std::invalid_argument(
                    label + " derived " + catalog_name +
                    " must not overlap " + root_name);
            }
        }
    }
}

}  // namespace

fs::path sync_replica_folder_catalog_path_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder catalog path label must not be empty");
    }
    validate_sync_replica_deployment_manifest_or_throw(
        deployment, label + " deployment manifest");
    fs::path catalog = append_ascii_suffix(
        deployment.replica_db, ".folder-catalog.sqlite3");
    if (!catalog.is_absolute() || catalog.lexically_normal() != catalog ||
        catalog.parent_path().empty()) {
        throw std::invalid_argument(
            label + " could not derive a canonical absolute catalog path");
    }
    require_catalog_namespace_disjoint_or_throw(
        deployment, catalog, label);
    return catalog;
}

void validate_sync_replica_folder_process_deployment_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder process label must not be empty");
    }
    validate_sync_replica_deployment_manifest_or_throw(
        deployment, label + " deployment manifest");
    if (!deployment.payload_root.has_value()) {
        throw std::invalid_argument(
            label + " requires payload_root in the deployment manifest");
    }
    if (!deployment.files_root.has_value()) {
        throw std::invalid_argument(
            label + " requires files_root in the deployment manifest");
    }
    (void)sync_replica_deployment_identity_or_throw(
        deployment, label + " deployment identity");
    (void)sync_replica_folder_catalog_path_or_throw(
        deployment, label + " catalog namespace");
}

SyncReplicaSqliteDeploymentBinding
sync_replica_folder_catalog_binding_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    validate_sync_replica_folder_process_deployment_or_throw(
        deployment, label);
    SyncReplicaSqliteDeploymentBinding binding{
        .deployment = sync_replica_deployment_identity_or_throw(
            deployment, label + " identity"),
        .role = SyncReplicaSqliteDeploymentRole::FolderCatalog,
        .database_path = sync_replica_folder_catalog_path_or_throw(
            deployment, label + " path"),
    };
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        binding, label + " binding");
    return binding;
}

SyncReplicaSqliteDeploymentBinding
sync_replica_primary_database_binding_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    validate_sync_replica_folder_process_deployment_or_throw(
        deployment, label);
    SyncReplicaSqliteDeploymentBinding binding{
        .deployment = sync_replica_deployment_identity_or_throw(
            deployment, label + " identity"),
        .role = SyncReplicaSqliteDeploymentRole::Replica,
        .database_path = deployment.replica_db,
    };
    validate_sync_replica_sqlite_deployment_binding_or_throw(
        binding, label + " binding");
    return binding;
}

namespace {

[[nodiscard]] SyncReplicaOperationalDatabase
open_attested_sync_replica_primary_database_with_disposition_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    SyncReplicaOperationalDatabaseOpenDisposition disposition,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "attested primary replica database label must not be empty");
    }
    SyncReplicaOperationalDatabase database =
        SyncReplicaOperationalDatabase::open_or_throw(
            deployment.replica_db, disposition, label + " database");
    attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.handle(),
        sync_replica_primary_database_binding_or_throw(
            deployment, label + " binding"),
        label + " deployment binding");
    return database;
}

}  // namespace

SyncReplicaOperationalDatabase
open_attested_sync_replica_primary_database_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    return open_attested_sync_replica_primary_database_with_disposition_or_throw(
        deployment,
        SyncReplicaOperationalDatabaseOpenDisposition::ExistingOperational,
        label);
}

SyncReplicaOperationalDatabase
open_attested_sync_replica_primary_database_read_only_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    return open_attested_sync_replica_primary_database_with_disposition_or_throw(
        deployment,
        SyncReplicaOperationalDatabaseOpenDisposition::
            ExistingForensicReadOnly,
        label);
}

SyncReplicaFilePayloadStoreLimits
sync_replica_folder_payload_store_limits_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    validate_sync_replica_folder_process_deployment_or_throw(
        deployment, label);
    return sync_replica_file_payload_store_limits_for_payload_ceiling_or_throw(
        deployment.max_payload_bytes, label + " payload store limits");
}

SyncReplicaFolderScanLimits sync_replica_folder_catalog_limits_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    validate_sync_replica_folder_process_deployment_or_throw(
        deployment, label);
    SyncReplicaFolderScanLimits limits;
    limits.max_payload_bytes = deployment.max_payload_bytes;
    validate_sync_replica_folder_scan_limits_or_throw(limits);
    return limits;
}

struct SyncReplicaFolderProcessOwner::State final {
    SyncReplicaDeploymentManifest deployment;
    fs::path catalog_path;
    SyncReplicaOperationalDatabase replica_database;
    SyncReplicaOperationalDatabase catalog_database;
    std::unique_ptr<SyncReplicaSqliteOwner> replica_owner;
    std::unique_ptr<SyncReplicaFilePayloadStore> payload_store;
    std::unique_ptr<SyncReplicaFolderScanOwner> folder_owner;
    std::string label;
};

SyncReplicaFolderProcessOwner::SyncReplicaFolderProcessOwner(
    SyncReplicaDeploymentManifest deployment,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica folder process owner label must not be empty");
    }
    validate_sync_replica_folder_process_deployment_or_throw(
        deployment, label + " deployment");

    auto state = std::make_unique<State>();
    state->deployment = std::move(deployment);
    state->label = std::move(label);
    state->catalog_path = sync_replica_folder_catalog_path_or_throw(
        state->deployment, state->label + " catalog path");

    state->replica_database =
        open_attested_sync_replica_primary_database_or_throw(
            state->deployment, state->label + " replica");

    state->catalog_database =
        SyncReplicaOperationalDatabase::open_or_throw(
            state->catalog_path,
            SyncReplicaOperationalDatabaseOpenDisposition::
                ExistingOperational,
            state->label + " catalog database");
    const SyncReplicaSqliteDeploymentBinding catalog_binding =
        sync_replica_folder_catalog_binding_or_throw(
            state->deployment, state->label + " catalog binding");
    attest_sync_replica_sqlite_deployment_binding_or_throw(
        state->catalog_database.handle(), catalog_binding,
        state->label + " catalog deployment binding");

    state->replica_owner = std::make_unique<SyncReplicaSqliteOwner>(
        state->replica_database.handle(), state->deployment.folder_id,
        state->deployment.local_actor, SyncReplicaSqliteOwnerLimits{},
        state->label + " replica owner");
    state->payload_store = std::make_unique<SyncReplicaFilePayloadStore>(
        sync_replica_deployment_identity_or_throw(
            state->deployment, state->label + " payload identity"),
        *state->deployment.payload_root,
        SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        sync_replica_folder_payload_store_limits_or_throw(
            state->deployment, state->label + " payload limits"),
        state->label + " payload store");
    state->folder_owner = std::make_unique<SyncReplicaFolderScanOwner>(
        state->catalog_database.handle(), catalog_binding,
        *state->deployment.files_root, *state->replica_owner,
        *state->payload_store,
        SyncReplicaFolderCatalogOpenDisposition::ExistingOnly,
        sync_replica_folder_catalog_limits_or_throw(
            state->deployment, state->label + " catalog limits"),
        state->label + " folder owner");

    state_ = std::move(state);
}

SyncReplicaFolderProcessOwner::~SyncReplicaFolderProcessOwner() noexcept =
    default;

const SyncReplicaDeploymentManifest&
SyncReplicaFolderProcessOwner::deployment() const noexcept {
    return state_->deployment;
}

const fs::path& SyncReplicaFolderProcessOwner::catalog_path() const noexcept {
    return state_->catalog_path;
}

SyncReplicaFolderCatalogSnapshot
SyncReplicaFolderProcessOwner::catalog_snapshot_or_throw() {
    return folder_owner_or_throw().snapshot_or_throw();
}

SyncReplicaFolderScanProgressSnapshot
SyncReplicaFolderProcessOwner::scan_progress_snapshot_or_throw() {
    return folder_owner_or_throw().scan_progress_snapshot_or_throw();
}

SyncReplicaSqliteSnapshot
SyncReplicaFolderProcessOwner::replica_snapshot_or_throw() {
    return replica_owner_or_throw().snapshot_or_throw();
}

SyncReplicaFolderConvergencePassReport
SyncReplicaFolderProcessOwner::run_convergence_pass_or_throw(
    const SyncReplicaFolderConvergencePassLimits& limits) {
    return folder_owner_or_throw().run_convergence_pass_or_throw(limits);
}

SyncReplicaFolderConvergencePassReport
SyncReplicaFolderProcessOwner::
run_convergence_pass_with_payload_snapshot_or_throw(
    SyncReplicaFilePayloadStoreSnapshot payload_snapshot,
    const SyncReplicaFolderConvergencePassLimits& limits) {
    return folder_owner_or_throw()
        .run_convergence_pass_with_payload_snapshot_or_throw(
            std::move(payload_snapshot), limits);
}

SyncReplicaSqliteOwner&
SyncReplicaFolderProcessOwner::replica_owner_or_throw() {
    if (!state_ || !state_->replica_owner) {
        throw std::logic_error(
            "sync replica folder process owner is inactive");
    }
    return *state_->replica_owner;
}

SyncReplicaFilePayloadStore&
SyncReplicaFolderProcessOwner::payload_store_or_throw() {
    if (!state_ || !state_->payload_store) {
        throw std::logic_error(
            "sync replica folder process owner is inactive");
    }
    return *state_->payload_store;
}

const SyncReplicaFilePayloadStore&
SyncReplicaFolderProcessOwner::payload_store_or_throw() const {
    if (!state_ || !state_->payload_store) {
        throw std::logic_error(
            "sync replica folder process owner is inactive");
    }
    return *state_->payload_store;
}

SyncReplicaFolderScanOwner&
SyncReplicaFolderProcessOwner::folder_owner_or_throw() {
    if (!state_ || !state_->folder_owner) {
        throw std::logic_error(
            "sync replica folder process owner is inactive");
    }
    return *state_->folder_owner;
}

}  // namespace anonsync

#endif
