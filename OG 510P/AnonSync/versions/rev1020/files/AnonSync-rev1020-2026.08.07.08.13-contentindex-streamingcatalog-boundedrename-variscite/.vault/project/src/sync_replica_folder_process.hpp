#pragma once

#if !defined(_WIN32)

#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_folder_scan_owner.hpp"
#include "sync_replica_operational_database.hpp"

#include <filesystem>
#include <memory>
#include <string>

namespace anonsync {

// The folder process deliberately has no independently selected catalog path.
// One deployment manifest is the sole configuration source, and the catalog is
// a deterministic role store beside the already selected replica database.
[[nodiscard]] std::filesystem::path
sync_replica_folder_catalog_path_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

void validate_sync_replica_folder_process_deployment_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

[[nodiscard]] SyncReplicaSqliteDeploymentBinding
sync_replica_folder_catalog_binding_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

[[nodiscard]] SyncReplicaSqliteDeploymentBinding
sync_replica_primary_database_binding_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

// Opens the manifest-selected primary replica database in existing-only
// operational mode and attests its durable deployment binding. This is the
// single writer seam shared by the retained folder owner and offline recovery
// ceremony; neither caller may silently open an unbound or newly created
// SQLite image.
[[nodiscard]] SyncReplicaOperationalDatabase
open_attested_sync_replica_primary_database_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

// Read-only counterpart for offline inspection. It retains the same exact
// deployment-binding proof but cannot initialize, migrate, checkpoint, or
// otherwise mutate the selected database family.
[[nodiscard]] SyncReplicaOperationalDatabase
open_attested_sync_replica_primary_database_read_only_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

[[nodiscard]] SyncReplicaFilePayloadStoreLimits
sync_replica_folder_payload_store_limits_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

[[nodiscard]] SyncReplicaFolderScanLimits
sync_replica_folder_catalog_limits_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

// Operational owner for one configured local folder. This is the shared
// existing-only process seam used by both the standalone folder command and
// higher-level sync composition. It opens and attests the manifest-selected
// replica and derived catalog databases exactly once, then retains the replica,
// payload, and rooted folder owners in one lifetime. Bootstrap remains outside:
// a missing or mistyped store can never be created through this class.
class SyncReplicaFolderProcessOwner final {
public:
    explicit SyncReplicaFolderProcessOwner(
        SyncReplicaDeploymentManifest deployment,
        std::string label = "sync replica folder process owner");
    ~SyncReplicaFolderProcessOwner() noexcept;

    SyncReplicaFolderProcessOwner(
        const SyncReplicaFolderProcessOwner&) = delete;
    SyncReplicaFolderProcessOwner& operator=(
        const SyncReplicaFolderProcessOwner&) = delete;
    SyncReplicaFolderProcessOwner(
        SyncReplicaFolderProcessOwner&&) = delete;
    SyncReplicaFolderProcessOwner& operator=(
        SyncReplicaFolderProcessOwner&&) = delete;

    [[nodiscard]] const SyncReplicaDeploymentManifest& deployment()
        const noexcept;
    [[nodiscard]] const std::filesystem::path& catalog_path() const noexcept;

    [[nodiscard]] SyncReplicaFolderCatalogSnapshot
    catalog_snapshot_or_throw();
    [[nodiscard]] SyncReplicaFolderScanProgressSnapshot
    scan_progress_snapshot_or_throw();
    [[nodiscard]] SyncReplicaSqliteSnapshot replica_snapshot_or_throw();
    [[nodiscard]] SyncReplicaFolderConvergencePassReport
    run_convergence_pass_or_throw(
        const SyncReplicaFolderConvergencePassLimits& limits = {});

    // Immediate same-owner handoff used after a complete payload-store reproof.
    // The folder owner validates the snapshot's exact process/store origin
    // before reusing it; a snapshot from another handle, even for the same
    // durable root, is rejected.
    [[nodiscard]] SyncReplicaFolderConvergencePassReport
    run_convergence_pass_with_payload_snapshot_or_throw(
        SyncReplicaFilePayloadStoreSnapshot payload_snapshot,
        const SyncReplicaFolderConvergencePassLimits& limits = {});

    // Narrow accessors for composition owners. They expose no creation path and
    // remain valid only for this process owner's retained lifetime.
    [[nodiscard]] SyncReplicaSqliteOwner& replica_owner_or_throw();
    [[nodiscard]] SyncReplicaFilePayloadStore& payload_store_or_throw();
    [[nodiscard]] const SyncReplicaFilePayloadStore& payload_store_or_throw()
        const;
    [[nodiscard]] SyncReplicaFolderScanOwner& folder_owner_or_throw();

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
