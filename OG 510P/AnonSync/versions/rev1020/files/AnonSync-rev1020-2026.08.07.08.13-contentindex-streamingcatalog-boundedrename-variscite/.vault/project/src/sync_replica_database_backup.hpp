#pragma once

#if !defined(_WIN32)

#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_sqlite_owner.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <string>

namespace anonsync {

// The current artifact owner is deliberately memory-resident. Keep its product
// ceiling below the generic one-gigabyte untrusted-SQLite ceiling until a
// descriptor-streaming publisher is implemented and qualified at target scale.
inline constexpr std::uint64_t
    kSyncReplicaDatabaseBackupMaximumArtifactBytes =
        512ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaDatabaseBackupMaximumArtifactPages = 262144ULL;

// Compact exact source witness retained across the backup bracket. The full
// causal graph is independently restored and validated at each observation,
// then released immediately. Its canonical digests and lineage are sufficient
// to prove that before/captured/after observations name one exact replica
// cutpoint without retaining two or three complete operation graphs beside the
// resident SQLite image.
struct SyncReplicaDatabaseBackupCutpoint final {
    std::string database_incarnation_sha256;
    std::uint64_t database_recovery_epoch = 0U;
    std::uint64_t state_generation = 0U;
    std::uint64_t policy_generation = 0U;
    std::uint64_t outbox_time_high_water_epoch = 0U;
    std::string local_operation_digest;
    std::string operation_set_digest;
    std::string evidence_set_digest;
    std::string visible_state_digest;
    std::string outbox_digest;
    std::string outbox_clock_digest;
    std::uint64_t historical_version_pin_count = 0U;
    std::string historical_version_pin_set_digest;
    std::string cutpoint_digest;

    bool operator==(const SyncReplicaDatabaseBackupCutpoint&) const = default;
};

struct SyncReplicaDatabaseBackupArtifactObservation final {
    std::filesystem::path artifact_path;
    std::string artifact_sha256;
    std::uint64_t artifact_bytes = 0U;
    std::uint32_t sqlite_page_size = 0U;
    std::uint32_t sqlite_page_count = 0U;
    SyncReplicaDatabaseBackupCutpoint source_cutpoint;

    bool operator==(
        const SyncReplicaDatabaseBackupArtifactObservation&) const = default;
};

// One exact current-schema witness for any manifest-selected SQLite authority.
// `state_digest` is the role's canonical complete-state digest;
// `auxiliary_digest` retains an independent role-specific digest where one
// exists. Replica observations additionally preserve the released v1 cutpoint
// so explicit `--role replica` artifacts remain consumable by the existing
// replacement ceremony and legacy inspector.
struct SyncReplicaRoleDatabaseBackupCutpoint final {
    SyncReplicaSqliteDeploymentRole database_role =
        SyncReplicaSqliteDeploymentRole::Replica;
    std::filesystem::path source_database_path;
    std::uint64_t state_generation = 0U;
    std::uint64_t logical_record_count = 0U;
    std::string state_digest;
    std::string auxiliary_digest;
    std::optional<SyncReplicaDatabaseBackupCutpoint> replica_cutpoint;

    bool operator==(
        const SyncReplicaRoleDatabaseBackupCutpoint&) const = default;
};

struct SyncReplicaRoleDatabaseBackupArtifactObservation final {
    std::filesystem::path artifact_path;
    std::string artifact_sha256;
    std::uint64_t artifact_bytes = 0U;
    std::uint32_t sqlite_page_size = 0U;
    std::uint32_t sqlite_page_count = 0U;
    SyncReplicaRoleDatabaseBackupCutpoint source_cutpoint;

    bool operator==(
        const SyncReplicaRoleDatabaseBackupArtifactObservation&) const =
        default;
};

// Offline, share-scoped ownership for one immutable replica-database backup
// artifact. Construction claims the deployment singleton before any selected
// database family or detached artifact is opened. Creation copies one pinned
// source snapshot, brackets it with exact current-schema observations, publishes
// create-new, closes the source, then reopens and re-proves the durable artifact.
// Inspection observes only the selected detached artifact plus the manifest.
// Neither operation replaces the live database family or advances recovery.
class SyncReplicaDatabaseBackupOwner final {
public:
    explicit SyncReplicaDatabaseBackupOwner(
        SyncReplicaDeploymentManifest deployment,
        std::string label = "sync replica database backup owner");
    ~SyncReplicaDatabaseBackupOwner() noexcept;

    SyncReplicaDatabaseBackupOwner(
        const SyncReplicaDatabaseBackupOwner&) = delete;
    SyncReplicaDatabaseBackupOwner& operator=(
        const SyncReplicaDatabaseBackupOwner&) = delete;
    SyncReplicaDatabaseBackupOwner(
        SyncReplicaDatabaseBackupOwner&&) = delete;
    SyncReplicaDatabaseBackupOwner& operator=(
        SyncReplicaDatabaseBackupOwner&&) = delete;

    [[nodiscard]] const SyncReplicaDeploymentManifest& deployment()
        const noexcept;

    [[nodiscard]] SyncReplicaDatabaseBackupArtifactObservation
    create_artifact_or_throw(
        const std::filesystem::path& absolute_artifact_path);

    [[nodiscard]] SyncReplicaDatabaseBackupArtifactObservation
    inspect_artifact_or_throw(
        const std::filesystem::path& absolute_artifact_path);

    // Explicit role-bound surface. Every role uses the same bounded immutable
    // SQLite artifact publisher and singleton, but role-specific deployment
    // binding and complete logical-state proof. Only Replica is currently
    // accepted by database-recovery-replace; the remaining roles are
    // inspection-only recovery components.
    [[nodiscard]] SyncReplicaRoleDatabaseBackupArtifactObservation
    create_role_artifact_or_throw(
        SyncReplicaSqliteDeploymentRole database_role,
        const std::filesystem::path& absolute_artifact_path);

    [[nodiscard]] SyncReplicaRoleDatabaseBackupArtifactObservation
    inspect_role_artifact_or_throw(
        SyncReplicaSqliteDeploymentRole database_role,
        const std::filesystem::path& absolute_artifact_path);

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
