#pragma once

#if !defined(_WIN32)

#include "sync_replica_database_backup.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <string>

namespace anonsync {

struct SyncReplicaDatabaseReplacementExpectation final {
    std::string database_incarnation_sha256;
    std::uint64_t database_recovery_epoch = 0U;
    std::string cutpoint_digest;

    bool operator==(
        const SyncReplicaDatabaseReplacementExpectation&) const = default;
};

enum class SyncReplicaDatabaseReplacementEntryStage {
    DisplacedDatabaseCurrent,
    CandidateInstalledEpochPending,
    RecoveryEpochAdvanced,
};

[[nodiscard]] const char* sync_replica_database_replacement_entry_stage_name(
    SyncReplicaDatabaseReplacementEntryStage stage) noexcept;

struct SyncReplicaDatabaseReplacementResult final {
    SyncReplicaDatabaseBackupArtifactObservation candidate_artifact;
    SyncReplicaDatabaseBackupArtifactObservation rollback_artifact;
    SyncReplicaDatabaseBackupCutpoint displaced_cutpoint;
    SyncReplicaDatabaseBackupCutpoint restored_cutpoint;
    SyncReplicaDatabaseBackupCutpoint final_cutpoint;
    std::filesystem::path receipt_path;
    std::string receipt_action_sha256;
    std::string receipt_record_sha256;
    SyncReplicaDatabaseReplacementEntryStage entry_stage =
        SyncReplicaDatabaseReplacementEntryStage::DisplacedDatabaseCurrent;
    std::uint64_t backup_step_calls = 0U;
    std::uint64_t maximum_reported_page_count = 0U;
    std::uint64_t maximum_reported_remaining_pages = 0U;
    bool receipt_preexisting = false;
    bool receipt_created_this_invocation = false;
    bool rollback_published_this_invocation = false;
    bool database_replacement_performed_this_invocation = false;
    bool recovery_epoch_advanced_this_invocation = false;
    bool idempotent_reproof_only = false;
    bool final_candidate_path_reproved = false;
    bool final_rollback_path_reproved = false;
};

// Separate offline authority for replacing the primary replica database from
// one already-created immutable backup artifact. Construction claims the same
// deployment singleton used by run, once, backup, and recovery commands before
// any database family, artifact, or action receipt is opened. One bounded,
// immutable, create-new receipt binds the exact selected action before the first
// rollback or database effect. Restart progress is classified from the active
// database's exact logical cutpoint, never from a mutable receipt stage. The
// owner admits only the exact displaced database, the exact candidate awaiting
// recovery-epoch advance, or the candidate's exact recovery successor. It does
// not restore payload bytes or any other deployment database.
class SyncReplicaDatabaseReplacementOwner final {
public:
    explicit SyncReplicaDatabaseReplacementOwner(
        SyncReplicaDeploymentManifest deployment,
        std::string label = "sync replica database replacement owner");
    ~SyncReplicaDatabaseReplacementOwner() noexcept;

    SyncReplicaDatabaseReplacementOwner(
        const SyncReplicaDatabaseReplacementOwner&) = delete;
    SyncReplicaDatabaseReplacementOwner& operator=(
        const SyncReplicaDatabaseReplacementOwner&) = delete;
    SyncReplicaDatabaseReplacementOwner(
        SyncReplicaDatabaseReplacementOwner&&) = delete;
    SyncReplicaDatabaseReplacementOwner& operator=(
        SyncReplicaDatabaseReplacementOwner&&) = delete;

    [[nodiscard]] const SyncReplicaDeploymentManifest& deployment()
        const noexcept;

    [[nodiscard]] SyncReplicaDatabaseReplacementResult
    replace_or_resume_or_throw(
        const std::filesystem::path& absolute_candidate_artifact_path,
        const std::filesystem::path& absolute_rollback_artifact_path,
        const std::filesystem::path& absolute_receipt_path,
        const SyncReplicaDatabaseReplacementExpectation& expected_current);

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
