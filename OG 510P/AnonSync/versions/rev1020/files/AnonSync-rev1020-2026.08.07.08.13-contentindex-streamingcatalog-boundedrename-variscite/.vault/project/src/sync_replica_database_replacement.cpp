#include "sync_replica_database_replacement.hpp"

#if !defined(_WIN32)

#include "persistence/sqlite_live_backup.hpp"
#include "persistence/sqlite_snapshot_seal.hpp"
#include "sync_replica_database_artifact_internal.hpp"
#include "sync_replica_database_replacement_receipt_internal.hpp"
#include "sync_replica_operational_database.hpp"
#include "sync_replica_peer_service_singleton.hpp"
#include "sync_replica_tls_policy_sqlite_profile.hpp"
#include "sync_sqlite_handle_slot.hpp"
#include "sync_sqlite_support.hpp"

#include <exception>
#include <filesystem>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {

namespace fs = std::filesystem;
namespace artifact_detail = sync_replica_database_artifact_detail;
namespace replacement_detail = sync_replica_database_replacement_detail;

namespace {

struct SealedArtifact final {
    persistence::SealedSqliteSnapshot seal;
    SyncReplicaDatabaseBackupArtifactObservation observation;
};

void require_expectation_or_throw(
    const SyncReplicaDatabaseReplacementExpectation& expectation,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(
            expectation.database_incarnation_sha256) ||
        expectation.database_recovery_epoch == 0U ||
        !is_lowercase_sha256_hex(expectation.cutpoint_digest)) {
        throw std::invalid_argument(
            label + " current database expectation is invalid");
    }
}

void require_expected_current_or_throw(
    const SyncReplicaDatabaseBackupCutpoint& current,
    const SyncReplicaDatabaseReplacementExpectation& expectation,
    const std::string& label) {
    if (current.database_incarnation_sha256 !=
            expectation.database_incarnation_sha256 ||
        current.database_recovery_epoch !=
            expectation.database_recovery_epoch ||
        current.cutpoint_digest != expectation.cutpoint_digest) {
        throw std::runtime_error(
            label + " current database expectation is stale");
    }
}

[[nodiscard]] SyncReplicaDatabaseBackupCutpoint inspect_active_cutpoint_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    SyncReplicaOperationalDatabase active =
        open_attested_sync_replica_primary_database_read_only_or_throw(
            deployment, label + " forensic source");
    SyncReplicaDatabaseBackupCutpoint cutpoint =
        artifact_detail::compact_backup_cutpoint(
            inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
                active.handle(), deployment.folder_id,
                deployment.local_actor, label + " snapshot"));
    active.verify_open_database_or_throw(label + " rooted reproof");
    return cutpoint;
}

[[nodiscard]] SealedArtifact capture_displaced_database_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& rollback_path,
    const SyncReplicaDatabaseReplacementExpectation& expected_current,
    const SyncReplicaDatabaseBackupArtifactObservation& candidate,
    const std::string& label) {
    SyncReplicaOperationalDatabase active_source =
        open_attested_sync_replica_primary_database_read_only_or_throw(
            deployment, label + " forensic source");
    const SyncReplicaDatabaseBackupCutpoint before =
        artifact_detail::compact_backup_cutpoint(
            inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
                active_source.handle(), deployment.folder_id,
                deployment.local_actor, label + " snapshot before capture"));
    require_expected_current_or_throw(before, expected_current, label);

    persistence::SealedSqliteSnapshot rollback_seal;
    {
        auto active_borrow = borrow_sync_sqlite_serialized_db_or_throw(
            active_source.handle(), label + " serialized source capability");
        rollback_seal = persistence::SealedSqliteSnapshot::capture_database(
            active_borrow.get(), label + " bounded database capture",
            artifact_detail::backup_seal_policy());
    }
    SyncReplicaDatabaseBackupArtifactObservation rollback =
        artifact_detail::inspect_sealed_artifact_or_throw(
            deployment, rollback_seal, rollback_path,
            label + " detached rollback inspection");
    const SyncReplicaDatabaseBackupCutpoint after =
        artifact_detail::compact_backup_cutpoint(
            inspect_sync_replica_sqlite_snapshot_read_only_or_throw(
                active_source.handle(), deployment.folder_id,
                deployment.local_actor, label + " snapshot after capture"));
    active_source.verify_open_database_or_throw(
        label + " final rooted reproof");
    if (before != rollback.source_cutpoint ||
        after != rollback.source_cutpoint) {
        throw std::runtime_error(
            label + " database changed across rollback capture");
    }
    if (candidate.sqlite_page_size != rollback.sqlite_page_size) {
        throw std::runtime_error(
            label + " candidate page size differs from the displaced database");
    }
    return {
        .seal = std::move(rollback_seal),
        .observation = std::move(rollback),
    };
}

[[nodiscard]] SealedArtifact inspect_required_artifact_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& artifact_path,
    const std::string& label) {
    persistence::SealedSqliteSnapshot seal =
        persistence::SealedSqliteSnapshot::capture(
            artifact_path, label + " capture",
            artifact_detail::backup_seal_policy());
    SyncReplicaDatabaseBackupArtifactObservation observation =
        artifact_detail::inspect_sealed_artifact_or_throw(
            deployment, seal, artifact_path, label + " validation");
    return {
        .seal = std::move(seal),
        .observation = std::move(observation),
    };
}

[[nodiscard]] std::optional<SealedArtifact>
inspect_existing_artifact_if_present_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const fs::path& artifact_path,
    const std::string& label) {
    try {
        return inspect_required_artifact_or_throw(
            deployment, artifact_path, label);
    } catch (...) {
        const std::exception_ptr capture_failure = std::current_exception();
        artifact_detail::require_exact_path_absence_or_rethrow(
            artifact_path, capture_failure);
        artifact_detail::preflight_artifact_output_family_create_new_or_throw(
            artifact_path, label + " absent artifact preflight");
        return std::nullopt;
    }
}

void require_representable_recovery_successor_or_throw(
    const SyncReplicaDatabaseBackupCutpoint& candidate,
    const std::string& label) {
    if (candidate.database_recovery_epoch ==
            std::numeric_limits<std::uint64_t>::max() ||
        candidate.state_generation ==
            std::numeric_limits<std::uint64_t>::max()) {
        throw std::invalid_argument(
            label +
            " candidate has no representable recovery successor; this invocation "
            "will not publish a new replacement receipt, rollback artifact, "
            "or database effect");
    }
}

void require_unambiguous_restart_states_or_throw(
    const SyncReplicaDatabaseBackupCutpoint& candidate,
    const SyncReplicaDatabaseBackupCutpoint& displaced,
    const std::string& label) {
    require_representable_recovery_successor_or_throw(candidate, label);
    if (candidate == displaced) {
        throw std::invalid_argument(
            label +
            " candidate and displaced database cutpoints are identical; "
            "the receipt cannot distinguish pre-copy from post-copy state");
    }
    if (artifact_detail::recovery_successor_matches(candidate, displaced)) {
        throw std::invalid_argument(
            label +
            " displaced database is already the candidate's exact recovery "
            "successor; replacement completion would be ambiguous");
    }
}

[[nodiscard]] SyncReplicaDatabaseReplacementEntryStage
classify_entry_stage_or_throw(
    const SyncReplicaDatabaseBackupCutpoint& active,
    const SyncReplicaDatabaseBackupCutpoint& displaced,
    const SyncReplicaDatabaseBackupCutpoint& candidate,
    const std::string& label) {
    if (active == displaced) {
        return SyncReplicaDatabaseReplacementEntryStage::
            DisplacedDatabaseCurrent;
    }
    if (active == candidate) {
        return SyncReplicaDatabaseReplacementEntryStage::
            CandidateInstalledEpochPending;
    }
    if (artifact_detail::recovery_successor_matches(candidate, active)) {
        return SyncReplicaDatabaseReplacementEntryStage::RecoveryEpochAdvanced;
    }
    throw std::runtime_error(
        label +
        " active database is neither the displaced state, the exact "
        "candidate awaiting recovery-epoch advance, nor the candidate's exact "
        "recovery successor; continuity is unknown");
}

}  // namespace

const char* sync_replica_database_replacement_entry_stage_name(
    SyncReplicaDatabaseReplacementEntryStage stage) noexcept {
    switch (stage) {
        case SyncReplicaDatabaseReplacementEntryStage::
            DisplacedDatabaseCurrent:
            return "displaced_database_current";
        case SyncReplicaDatabaseReplacementEntryStage::
            CandidateInstalledEpochPending:
            return "candidate_installed_epoch_pending";
        case SyncReplicaDatabaseReplacementEntryStage::RecoveryEpochAdvanced:
            return "recovery_epoch_advanced";
    }
    return "unknown";
}

struct SyncReplicaDatabaseReplacementOwner::State final {
    static std::string require_label(std::string value) {
        if (value.empty()) {
            throw std::invalid_argument(
                "sync replica database replacement owner label is empty");
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

SyncReplicaDatabaseReplacementOwner::SyncReplicaDatabaseReplacementOwner(
    SyncReplicaDeploymentManifest deployment,
    std::string label)
    : state_(std::make_unique<State>(
          std::move(deployment), std::move(label))) {}

SyncReplicaDatabaseReplacementOwner::~SyncReplicaDatabaseReplacementOwner()
    noexcept = default;

const SyncReplicaDeploymentManifest&
SyncReplicaDatabaseReplacementOwner::deployment() const noexcept {
    return state_->deployment;
}

SyncReplicaDatabaseReplacementResult
SyncReplicaDatabaseReplacementOwner::replace_or_resume_or_throw(
    const fs::path& absolute_candidate_artifact_path,
    const fs::path& absolute_rollback_artifact_path,
    const fs::path& absolute_receipt_path,
    const SyncReplicaDatabaseReplacementExpectation& expected_current) {
    require_expectation_or_throw(expected_current, state_->label);
    artifact_detail::validate_artifact_path_or_throw(
        state_->deployment, absolute_candidate_artifact_path,
        state_->label + " candidate artifact path");
    artifact_detail::validate_artifact_path_or_throw(
        state_->deployment, absolute_rollback_artifact_path,
        state_->label + " rollback artifact path");
    artifact_detail::require_disjoint_artifact_families_or_throw(
        absolute_candidate_artifact_path,
        absolute_rollback_artifact_path,
        state_->label + " candidate and rollback");
    replacement_detail::validate_external_receipt_path_or_throw(
        state_->deployment, absolute_candidate_artifact_path,
        absolute_rollback_artifact_path, absolute_receipt_path,
        state_->label + " external action receipt path");

    std::optional<replacement_detail::ReplacementReceipt> receipt =
        replacement_detail::read_replacement_receipt_if_present_or_throw(
            absolute_receipt_path, state_->label + " action receipt");
    const bool receipt_preexisting = receipt.has_value();
    if (!receipt_preexisting) {
        // Reject deterministic rollback-family conflicts before retaining as
        // much as two complete SQLite images in memory. The immutable receipt
        // and rollback are still re-proved immediately before publication.
        artifact_detail::preflight_artifact_output_family_create_new_or_throw(
            absolute_rollback_artifact_path,
            state_->label + " rollback output preflight");
    }

    persistence::SealedSqliteSnapshot candidate_seal =
        persistence::SealedSqliteSnapshot::capture(
            absolute_candidate_artifact_path,
            state_->label + " bounded candidate capture",
            artifact_detail::backup_seal_policy());
    const SyncReplicaDatabaseBackupArtifactObservation candidate =
        artifact_detail::inspect_sealed_artifact_or_throw(
            state_->deployment, candidate_seal,
            absolute_candidate_artifact_path,
            state_->label + " candidate validation");
    // A replacement action must have one exactly representable terminal
    // recovery successor. Reject overflow before the first receipt, rollback,
    // or database effect can become durable.
    require_representable_recovery_successor_or_throw(
        candidate.source_cutpoint, state_->label);

    bool receipt_created_this_invocation = false;
    bool rollback_published_this_invocation = false;
    bool database_replacement_performed_this_invocation = false;
    bool recovery_epoch_advanced_this_invocation = false;
    persistence::SqliteLiveBackupEvidence replacement_evidence;

    std::optional<SealedArtifact> rollback =
        inspect_existing_artifact_if_present_or_throw(
            state_->deployment, absolute_rollback_artifact_path,
            state_->label + " rollback artifact");
    replacement_detail::ReplacementReceiptObservation receipt_observation;

    if (receipt_preexisting) {
        replacement_detail::require_replacement_receipt_selection_matches_or_throw(
            *receipt, state_->deployment,
            absolute_candidate_artifact_path,
            absolute_rollback_artifact_path,
            absolute_receipt_path, expected_current, candidate,
            state_->label + " action receipt");
        if (rollback.has_value()) {
            replacement_detail::require_replacement_receipt_artifact_matches_or_throw(
                receipt->rollback, rollback->observation, "rollback",
                state_->label + " action receipt");
        } else {
            // Receipt-only restart: the rollback can be reconstructed only
            // while the active database remains the exact displaced state.
            SealedArtifact displaced = capture_displaced_database_or_throw(
                state_->deployment, absolute_rollback_artifact_path,
                expected_current, candidate,
                state_->label + " resumed displaced database");
            replacement_detail::require_replacement_receipt_artifact_matches_or_throw(
                receipt->rollback, displaced.observation, "rollback",
                state_->label + " action receipt");
            (void)replacement_detail::reprove_replacement_receipt_or_throw(
                absolute_receipt_path, *receipt,
                state_->label + " pre-rollback receipt reproof");
            artifact_detail::preflight_artifact_output_family_create_new_or_throw(
                absolute_rollback_artifact_path,
                state_->label +
                    " resumed rollback final prepublication reproof");
            displaced.seal.publish_exact_copy_atomically_create_new_or_throw(
                absolute_rollback_artifact_path,
                state_->label + " resumed rollback artifact publication");
            rollback_published_this_invocation = true;
        }
    } else {
        if (rollback.has_value()) {
            throw std::runtime_error(
                state_->label +
                " rollback artifact appeared without an immutable receipt");
        }
        SealedArtifact displaced = capture_displaced_database_or_throw(
            state_->deployment, absolute_rollback_artifact_path,
            expected_current, candidate,
            state_->label + " displaced database");
        require_unambiguous_restart_states_or_throw(
            candidate.source_cutpoint, displaced.observation.source_cutpoint,
            state_->label);
        receipt = replacement_detail::make_replacement_receipt_or_throw(
            state_->deployment, absolute_candidate_artifact_path,
            absolute_rollback_artifact_path, absolute_receipt_path,
            expected_current, candidate, displaced.observation,
            state_->label + " action receipt");

        // Durable immutable intent precedes the first rollback or database
        // effect. A crash after this cutpoint is classified only from exact
        // current database and artifact state; the receipt is never updated.
        receipt_observation =
            replacement_detail::publish_replacement_receipt_create_new_or_throw(
                absolute_receipt_path, *receipt,
                state_->label + " immutable action receipt");
        receipt_created_this_invocation = true;
        artifact_detail::preflight_artifact_output_family_create_new_or_throw(
            absolute_rollback_artifact_path,
            state_->label + " rollback output final prepublication reproof");
        displaced.seal.publish_exact_copy_atomically_create_new_or_throw(
            absolute_rollback_artifact_path,
            state_->label + " immutable rollback artifact publication");
        rollback_published_this_invocation = true;
    }

    if (!receipt.has_value()) {
        throw std::logic_error(
            state_->label + " replacement receipt admission is incomplete");
    }

    // Release the resident displaced snapshot before independently reopening
    // the durable rollback. Candidate + displaced and candidate + rollback are
    // each bounded pairs; the ceremony never retains all three complete images
    // at once merely to prove create-new publication.
    if (!rollback.has_value()) {
        rollback = inspect_existing_artifact_if_present_or_throw(
            state_->deployment, absolute_rollback_artifact_path,
            state_->label + " durable rollback artifact");
        if (!rollback.has_value()) {
            throw std::logic_error(
                state_->label + " rollback publication vanished");
        }
        replacement_detail::require_replacement_receipt_artifact_matches_or_throw(
            receipt->rollback, rollback->observation, "rollback",
            state_->label + " action receipt");
    }

    receipt_observation =
        replacement_detail::reprove_replacement_receipt_or_throw(
            absolute_receipt_path, *receipt,
            state_->label + " admitted action receipt reproof");

    if (candidate.sqlite_page_size != rollback->observation.sqlite_page_size) {
        throw std::runtime_error(
            state_->label +
            " candidate page size differs from the displaced database");
    }
    require_unambiguous_restart_states_or_throw(
        candidate.source_cutpoint, rollback->observation.source_cutpoint,
        state_->label);
    (void)replacement_detail::reprove_replacement_receipt_or_throw(
        absolute_receipt_path, *receipt,
        state_->label + " pre-database-effect receipt reproof");

    const SyncReplicaDatabaseBackupCutpoint active_at_entry =
        inspect_active_cutpoint_or_throw(
            state_->deployment,
            state_->label + " active replacement classification");
    const SyncReplicaDatabaseReplacementEntryStage entry_stage =
        classify_entry_stage_or_throw(
            active_at_entry, rollback->observation.source_cutpoint,
            candidate.source_cutpoint, state_->label);

    SyncReplicaDatabaseBackupCutpoint restored_cutpoint =
        candidate.source_cutpoint;
    SyncReplicaDatabaseBackupCutpoint final_cutpoint = active_at_entry;

    if (entry_stage !=
        SyncReplicaDatabaseReplacementEntryStage::RecoveryEpochAdvanced) {
        SyncReplicaOperationalDatabase active_destination =
            open_attested_sync_replica_primary_database_or_throw(
                state_->deployment,
                state_->label + " writable replacement destination");
        SyncReplicaSqliteOwner replica_owner(
            active_destination.handle(), state_->deployment.folder_id,
            state_->deployment.local_actor, SyncReplicaSqliteOwnerLimits{},
            state_->label + " replacement replica owner");
        const SyncReplicaDatabaseBackupCutpoint writable_entry =
            artifact_detail::compact_backup_cutpoint(
                replica_owner.snapshot_or_throw());
        const SyncReplicaDatabaseBackupCutpoint& expected_writable_entry =
            entry_stage == SyncReplicaDatabaseReplacementEntryStage::
                               DisplacedDatabaseCurrent
                ? rollback->observation.source_cutpoint
                : candidate.source_cutpoint;
        if (writable_entry != expected_writable_entry) {
            throw std::runtime_error(
                state_->label +
                " active database changed between forensic classification "
                "and writable admission");
        }

        if (entry_stage == SyncReplicaDatabaseReplacementEntryStage::
                               DisplacedDatabaseCurrent) {
            SyncSqliteDbHandleSlot candidate_database =
                candidate_seal.open_database_owner_or_throw(
                    state_->label + " replacement source database");
            configure_sync_replica_tls_policy_sqlite_read_only_connection_or_throw(
                candidate_database,
                state_->label + " replacement source read-only profile");
            sqlite_exec_or_throw(
                candidate_database,
                "PRAGMA temp_store=MEMORY;PRAGMA foreign_keys=ON;",
                state_->label + " replacement source pragmas");
            {
                auto destination_borrow =
                    borrow_sync_sqlite_serialized_db_or_throw(
                        active_destination.handle(),
                        state_->label + " writable destination capability");
                auto candidate_borrow =
                    borrow_sync_sqlite_serialized_db_or_throw(
                        candidate_database,
                        state_->label + " detached candidate capability");
                replacement_evidence =
                    persistence::replace_sqlite_live_database_bounded_or_throw(
                        destination_borrow.get(), candidate_borrow.get(),
                        state_->label +
                            " bounded logical database replacement",
                        artifact_detail::backup_seal_policy());
            }
            database_replacement_performed_this_invocation = true;
        }

        active_destination.verify_open_database_or_throw(
            state_->label + " restored database rooted reproof");
        restored_cutpoint = artifact_detail::compact_backup_cutpoint(
            replica_owner.snapshot_or_throw());
        if (restored_cutpoint != candidate.source_cutpoint) {
            throw std::runtime_error(
                state_->label +
                " restored database differs from the validated candidate");
        }

        (void)replacement_detail::reprove_replacement_receipt_or_throw(
            absolute_receipt_path, *receipt,
            state_->label + " pre-recovery-epoch receipt reproof");
        const SyncReplicaSqliteDatabaseRecoveryEpochResult advanced =
            replica_owner.advance_database_recovery_epoch_or_throw(
                restored_cutpoint.database_incarnation_sha256,
                restored_cutpoint.database_recovery_epoch,
                restored_cutpoint.cutpoint_digest);
        recovery_epoch_advanced_this_invocation = true;
        final_cutpoint = artifact_detail::compact_backup_cutpoint(
            replica_owner.snapshot_or_throw());
        if (!artifact_detail::recovery_successor_matches(
                restored_cutpoint, final_cutpoint) ||
            advanced.database_incarnation_sha256 !=
                final_cutpoint.database_incarnation_sha256 ||
            advanced.previous_database_recovery_epoch !=
                restored_cutpoint.database_recovery_epoch ||
            advanced.database_recovery_epoch !=
                final_cutpoint.database_recovery_epoch ||
            advanced.state_generation != final_cutpoint.state_generation ||
            advanced.cutpoint_digest != final_cutpoint.cutpoint_digest) {
            throw std::runtime_error(
                state_->label +
                " post-replacement recovery epoch proof is inconsistent");
        }
        active_destination.verify_open_database_or_throw(
            state_->label + " final writable deployment reproof");
    }

    // Close any writable destination, then bracket final receipt and artifact
    // pathname observations with two independent current-database cutpoints.
    // Resident candidate and rollback images are released before reopening the
    // selected names, preserving the bounded two-image memory contract.
    const SyncReplicaDatabaseBackupCutpoint durable_final_before_artifacts =
        inspect_active_cutpoint_or_throw(
            state_->deployment,
            state_->label +
                " final forensic deployment reproof before artifacts");
    if (durable_final_before_artifacts != final_cutpoint) {
        throw std::runtime_error(
            state_->label +
            " final reopened database differs from the committed result");
    }

    receipt_observation =
        replacement_detail::reprove_replacement_receipt_or_throw(
            absolute_receipt_path, *receipt,
            state_->label + " pre-final-artifact receipt reproof");

    candidate_seal = {};
    rollback->seal = {};

    SyncReplicaDatabaseBackupArtifactObservation durable_candidate;
    {
        SealedArtifact reopened_candidate =
            inspect_required_artifact_or_throw(
                state_->deployment, absolute_candidate_artifact_path,
                state_->label + " final candidate pathname reproof");
        replacement_detail::require_replacement_receipt_artifact_matches_or_throw(
            receipt->candidate, reopened_candidate.observation, "candidate",
            state_->label + " final action receipt");
        if (reopened_candidate.observation != candidate) {
            throw std::runtime_error(
                state_->label +
                " final candidate artifact differs from the admitted "
                "candidate");
        }
        durable_candidate = reopened_candidate.observation;
    }

    SyncReplicaDatabaseBackupArtifactObservation durable_rollback;
    {
        SealedArtifact reopened_rollback =
            inspect_required_artifact_or_throw(
                state_->deployment, absolute_rollback_artifact_path,
                state_->label + " final rollback pathname reproof");
        replacement_detail::require_replacement_receipt_artifact_matches_or_throw(
            receipt->rollback, reopened_rollback.observation, "rollback",
            state_->label + " final action receipt");
        if (reopened_rollback.observation != rollback->observation) {
            throw std::runtime_error(
                state_->label +
                " final rollback artifact differs from the admitted "
                "rollback");
        }
        durable_rollback = reopened_rollback.observation;
    }

    receipt_observation =
        replacement_detail::reprove_replacement_receipt_or_throw(
            absolute_receipt_path, *receipt,
            state_->label + " final immutable receipt reproof");

    const SyncReplicaDatabaseBackupCutpoint durable_final_after_artifacts =
        inspect_active_cutpoint_or_throw(
            state_->deployment,
            state_->label +
                " final forensic deployment reproof after artifacts");
    if (durable_final_after_artifacts != final_cutpoint) {
        throw std::runtime_error(
            state_->label +
                " final database changed across artifact pathname reproof");
    }

    // The deployment singleton excludes cooperating AnonSync owners. These
    // sequential pathname observations are not a continuous reservation of
    // candidate, rollback, or receipt names against a noncooperating same-UID
    // process; success reports that limitation explicitly.

    return {
        .candidate_artifact = std::move(durable_candidate),
        .rollback_artifact = std::move(durable_rollback),
        .displaced_cutpoint = rollback->observation.source_cutpoint,
        .restored_cutpoint = std::move(restored_cutpoint),
        .final_cutpoint = std::move(final_cutpoint),
        .receipt_path = receipt_observation.receipt_path,
        .receipt_action_sha256 = receipt_observation.action_sha256,
        .receipt_record_sha256 = receipt_observation.record_sha256,
        .entry_stage = entry_stage,
        .backup_step_calls = replacement_evidence.step_calls,
        .maximum_reported_page_count =
            replacement_evidence.maximum_reported_page_count,
        .maximum_reported_remaining_pages =
            replacement_evidence.maximum_reported_remaining_pages,
        .receipt_preexisting = receipt_preexisting,
        .receipt_created_this_invocation =
            receipt_created_this_invocation,
        .rollback_published_this_invocation =
            rollback_published_this_invocation,
        .database_replacement_performed_this_invocation =
            database_replacement_performed_this_invocation,
        .recovery_epoch_advanced_this_invocation =
            recovery_epoch_advanced_this_invocation,
        .idempotent_reproof_only =
            entry_stage == SyncReplicaDatabaseReplacementEntryStage::
                               RecoveryEpochAdvanced,
        .final_candidate_path_reproved = true,
        .final_rollback_path_reproved = true,
    };
}

}  // namespace anonsync

#endif
