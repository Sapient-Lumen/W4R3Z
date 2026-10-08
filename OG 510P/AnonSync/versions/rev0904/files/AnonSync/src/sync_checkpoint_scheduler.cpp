#include "anonsync_core.hpp"
#include "sync_checkpoint_resume_internal.hpp"
#include "sync_checkpoint_scheduler_policy.hpp"

#include <cstdint>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

SyncValidationResult ok_result() {
    return {true, ""};
}

SyncValidationResult fail_result(const std::string& reason) {
    return {false, reason};
}

bool valid_sync_id(const std::string& value) noexcept {
    return sync_checkpoint_internal::valid_portable_sync_id(value);
}

}  // namespace

SyncValidationResult plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(
    const SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions& options,
    SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult& out) {
    out = SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult{};
    if (options.sqlite_path.empty()) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass sqlite_path is required");
    }
    if (!valid_sync_id(options.session_id)) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass session_id must be lowercase portable sync id");
    }
    if (options.source_root_path.empty()) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass source_root_path is required");
    }
    if (options.destination_root_path.empty()) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass destination_root_path is required");
    }
    if (options.staging_root_path.empty()) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass staging_root_path is required");
    }
    if (options.scheduler_now_epoch == 0) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass scheduler_now_epoch must be positive");
    }
    if (options.worker_id.empty() != options.worker_lease_id.empty()) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass requires worker_id and worker_lease_id together");
    }

    SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options;
    queue_options.sqlite_path = options.sqlite_path;
    queue_options.session_id = options.session_id;
    queue_options.source_root_path = options.source_root_path;
    queue_options.destination_root_path = options.destination_root_path;
    queue_options.staging_root_path = options.staging_root_path;
    queue_options.expected_folder_id = options.expected_folder_id;
    queue_options.expected_source_device_id = options.expected_source_device_id;
    queue_options.expected_destination_device_id =
        options.expected_destination_device_id;
    queue_options.expected_peer_id = options.expected_peer_id;
    queue_options.require_durable_integrity = options.require_durable_integrity;
    queue_options.require_source_filesystem_match =
        options.require_source_filesystem_match;
    queue_options.worker_id = options.worker_id;
    queue_options.worker_lease_id = options.worker_lease_id;
    queue_options.queue_now_epoch = options.scheduler_now_epoch;
    queue_options.max_workorder_claim_attempts =
        options.max_workorder_claim_attempts;
    queue_options.include_completed_workorders =
        options.include_completed_workorders;

    SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
    const SyncValidationResult queue_run =
        select_sync_session_checkpoint_resume_transfer_workorder_queue(
            queue_options, queue_result);
    if (!queue_run.ok) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass rejected queue selection: " +
            queue_run.reason);
    }

    SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult policy_result;
    const SyncValidationResult policy_run =
        sync_checkpoint_scheduler_policy::plan_resume_transfer_workorder_actions(
            queue_result.facts, options.max_scheduler_actions, policy_result);
    if (!policy_run.ok) {
        return fail_result(
            "sync session checkpoint resume transfer workorder scheduler pass rejected scheduler policy: " +
            policy_run.reason);
    }

    out = std::move(policy_result);
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.worker_id = options.worker_id;
    out.worker_lease_id = options.worker_lease_id;
    out.queue_selected = true;
    out.durable_integrity_verified = queue_result.durable_integrity_verified;
    out.source_filesystem_verified = queue_result.source_filesystem_verified;
    out.scheduler_now_epoch = options.scheduler_now_epoch;
    out.max_workorder_claim_attempts = options.max_workorder_claim_attempts;
    out.max_scheduler_actions = options.max_scheduler_actions;
    out.queue_facts_considered = queue_result.queue_facts_returned;
    out.queue_result = std::move(queue_result);
    return ok_result();
}
SyncValidationResult execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(const SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions& options,
                                                                                              SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult& out) {
    out = SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult{};
    if (options.sqlite_path.empty()) return fail_result("sync session checkpoint resume transfer workorder scheduler executor sqlite_path is required");
    if (!valid_sync_id(options.session_id)) return fail_result("sync session checkpoint resume transfer workorder scheduler executor session_id must be lowercase portable sync id");
    if (options.source_root_path.empty()) return fail_result("sync session checkpoint resume transfer workorder scheduler executor source_root_path is required");
    if (options.destination_root_path.empty()) return fail_result("sync session checkpoint resume transfer workorder scheduler executor destination_root_path is required");
    if (options.staging_root_path.empty()) return fail_result("sync session checkpoint resume transfer workorder scheduler executor staging_root_path is required");
    const std::string peer_id = options.peer_id.empty() ? options.expected_peer_id : options.peer_id;
    const std::string peer_session_id = options.peer_session_id.empty() ? (options.session_id + "-resume") : options.peer_session_id;
    const std::string worker_id = options.worker_id.empty() ? (options.session_id + "-scheduler-worker") : options.worker_id;
    if (!valid_sync_id(peer_id) || !valid_sync_id(peer_session_id)) {
        return fail_result("sync session checkpoint resume transfer workorder scheduler executor peer_id and peer_session_id must be lowercase portable sync ids");
    }
    if (!valid_sync_id(worker_id)) return fail_result("sync session checkpoint resume transfer workorder scheduler executor worker_id must be lowercase portable sync id");
    if (options.worker_lease_epoch == 0) return fail_result("sync session checkpoint resume transfer workorder scheduler executor worker_lease_epoch must be positive");
    if (options.scheduler_now_epoch == 0) return fail_result("sync session checkpoint resume transfer workorder scheduler executor scheduler_now_epoch must be positive");
    if (options.worker_lease_seconds == 0) return fail_result("sync session checkpoint resume transfer workorder scheduler executor worker_lease_seconds must be positive");
    if (options.scheduler_now_epoch > std::numeric_limits<std::uint64_t>::max() - options.worker_lease_seconds) {
        return fail_result("sync session checkpoint resume transfer workorder scheduler executor worker lease expiration would overflow");
    }

    try {
        const std::string worker_lease_id = sync_checkpoint_internal::checkpoint_resume_transfer_worker_lease_id_or_throw(options.session_id,
                                                                                                worker_id,
                                                                                                peer_id,
                                                                                                peer_session_id,
                                                                                                options.worker_lease_epoch);
        SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions scheduler_options;
        scheduler_options.sqlite_path = options.sqlite_path;
        scheduler_options.session_id = options.session_id;
        scheduler_options.source_root_path = options.source_root_path;
        scheduler_options.destination_root_path = options.destination_root_path;
        scheduler_options.staging_root_path = options.staging_root_path;
        scheduler_options.expected_folder_id = options.expected_folder_id;
        scheduler_options.expected_source_device_id = options.expected_source_device_id;
        scheduler_options.expected_destination_device_id = options.expected_destination_device_id;
        scheduler_options.expected_peer_id = options.expected_peer_id;
        scheduler_options.require_durable_integrity = options.require_durable_integrity;
        scheduler_options.require_source_filesystem_match = options.require_source_filesystem_match;
        scheduler_options.worker_id = worker_id;
        scheduler_options.worker_lease_id = worker_lease_id;
        scheduler_options.scheduler_now_epoch = options.scheduler_now_epoch;
        scheduler_options.max_workorder_claim_attempts = options.max_workorder_claim_attempts;
        scheduler_options.max_scheduler_actions = options.max_scheduler_actions;
        scheduler_options.include_completed_workorders = options.include_completed_workorders;

        SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult scheduler_result;
        SyncValidationResult scheduler_run = plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_options,
                                                                                                                    scheduler_result);
        if (!scheduler_run.ok) {
            return fail_result("sync session checkpoint resume transfer workorder scheduler executor rejected scheduler plan: " + scheduler_run.reason);
        }

        out.sqlite_path = options.sqlite_path;
        out.session_id = options.session_id;
        out.worker_id = worker_id;
        out.worker_lease_id = worker_lease_id;
        out.scheduler_plan_loaded = true;
        out.durable_integrity_verified = scheduler_result.durable_integrity_verified;
        out.source_filesystem_verified = scheduler_result.source_filesystem_verified;
        out.scheduler_now_epoch = options.scheduler_now_epoch;
        out.max_scheduler_actions = options.max_scheduler_actions;
        out.scheduler_actions_returned = scheduler_result.scheduler_actions_returned;
        out.mutating_actions_planned = scheduler_result.mutating_actions_planned;
        out.scheduler_action_groups_deferred_by_limit = scheduler_result.scheduler_action_groups_deferred_by_limit;
        out.scheduler_actions_deferred_by_limit = scheduler_result.scheduler_actions_deferred_by_limit;
        out.scheduler_result = scheduler_result;
        if (scheduler_result.scheduler_actions_returned !=
            static_cast<std::uint64_t>(scheduler_result.actions.size())) {
            throw std::runtime_error(
                "sync session checkpoint resume transfer workorder scheduler executor refuses mismatched returned-action evidence");
        }

        out.terminal_review_actions_observed =
            scheduler_result.review_abandoned_actions +
            scheduler_result.review_quarantined_actions;
        out.terminal_review_present =
            out.terminal_review_actions_observed != 0;
        const bool block_mutations_for_terminal_review =
            options.block_mutating_actions_on_terminal_review &&
            out.terminal_review_present;

        std::vector<std::string> execute_keys;
        std::vector<std::string> claim_or_abandon_keys;
        std::map<std::uint64_t,
                 SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind>
            group_kind;
        std::map<std::uint64_t, bool> group_mutating;
        std::map<std::uint64_t, std::string> group_execution_key;
        std::map<std::uint64_t, std::uint64_t> group_expected_size;
        std::map<std::uint64_t, std::uint64_t> group_observed_size;

        auto mutating_action_requested = [&](
            SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind kind) {
            using ActionKind =
                SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind;
            switch (kind) {
                case ActionKind::ExecuteOwnedClaim:
                    return options.execute_owned_claim_actions;
                case ActionKind::ClaimOrReclaimExpired:
                    return options.claim_or_reclaim_expired_actions;
                case ActionKind::AbandonExpired:
                    return options.abandon_expired_actions;
                case ActionKind::ObserveLiveClaimedByOther:
                case ActionKind::WaitRetryBackoff:
                case ActionKind::ReviewAbandoned:
                case ActionKind::ReviewQuarantined:
                case ActionKind::IgnoreCompleted:
                    return false;
            }
            return false;
        };

        std::uint64_t expected_scheduler_priority = 1;
        std::uint64_t active_group_priority = 0;
        auto mark_group_or_throw = [&](
            const SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction&
                action) {
            if (action.scheduler_priority != expected_scheduler_priority) {
                throw std::runtime_error(
                    "sync session checkpoint resume transfer workorder scheduler executor refuses non-contiguous action priority evidence");
            }
            ++expected_scheduler_priority;
            if (action.scheduler_group_priority == 0 ||
                action.scheduler_group_size == 0) {
                throw std::runtime_error(
                    "sync session checkpoint resume transfer workorder scheduler executor action lacks complete group metadata");
            }
            if (!action.mutating_action && action.scheduler_group_size != 1) {
                throw std::runtime_error(
                    "sync session checkpoint resume transfer workorder scheduler executor refuses grouped nonmutating observations");
            }
            const auto priority = action.scheduler_group_priority;
            if (priority != active_group_priority) {
                if (active_group_priority != 0 &&
                    group_observed_size.at(active_group_priority) !=
                        group_expected_size.at(active_group_priority)) {
                    throw std::runtime_error(
                        "sync session checkpoint resume transfer workorder scheduler executor refuses a split execution group");
                }
                if (priority != active_group_priority + 1 ||
                    group_kind.contains(priority)) {
                    throw std::runtime_error(
                        "sync session checkpoint resume transfer workorder scheduler executor refuses non-contiguous group priority evidence");
                }
                active_group_priority = priority;
            }
            auto kind_found = group_kind.find(priority);
            if (kind_found == group_kind.end()) {
                group_kind[priority] = action.action_kind;
                group_mutating[priority] = action.mutating_action;
                group_execution_key[priority] =
                    action.execution_idempotency_key;
                group_expected_size[priority] = action.scheduler_group_size;
                group_observed_size[priority] = 1;
            } else {
                if (kind_found->second != action.action_kind ||
                    group_mutating[priority] != action.mutating_action ||
                    group_execution_key[priority] !=
                        action.execution_idempotency_key ||
                    group_expected_size[priority] !=
                        action.scheduler_group_size) {
                    throw std::runtime_error(
                        "sync session checkpoint resume transfer workorder scheduler executor refuses mixed authority inside one execution group");
                }
                ++group_observed_size[priority];
            }
        };

        for (const auto& action : scheduler_result.actions) {
            mark_group_or_throw(action);
            if (!action.mutating_action) {
                ++out.nonmutating_actions_observed;
                continue;
            }
            if (!action.execution_idempotency_key.starts_with(
                    "sync-resume-transfer-execute:v1:")) {
                throw std::runtime_error(
                    "sync session checkpoint resume transfer workorder scheduler executor mutating action lacks execution key evidence");
            }
            if (!mutating_action_requested(action.action_kind)) continue;
            if (block_mutations_for_terminal_review) {
                ++out.mutating_actions_blocked_by_terminal_review;
                continue;
            }

            using ActionKind =
                SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind;
            switch (action.action_kind) {
                case ActionKind::ExecuteOwnedClaim:
                    execute_keys.push_back(action.execution_idempotency_key);
                    ++out.execute_owned_claim_actions_selected;
                    break;
                case ActionKind::ClaimOrReclaimExpired:
                    claim_or_abandon_keys.push_back(
                        action.execution_idempotency_key);
                    ++out.claim_or_reclaim_expired_actions_selected;
                    break;
                case ActionKind::AbandonExpired:
                    claim_or_abandon_keys.push_back(
                        action.execution_idempotency_key);
                    ++out.abandon_expired_actions_selected;
                    break;
                case ActionKind::ObserveLiveClaimedByOther:
                case ActionKind::WaitRetryBackoff:
                case ActionKind::ReviewAbandoned:
                case ActionKind::ReviewQuarantined:
                case ActionKind::IgnoreCompleted:
                    throw std::runtime_error(
                        "sync session checkpoint resume transfer workorder scheduler executor received nonmutating action marked as mutating");
            }
        }

        if (scheduler_result.scheduler_action_groups_returned !=
            static_cast<std::uint64_t>(group_kind.size())) {
            throw std::runtime_error(
                "sync session checkpoint resume transfer workorder scheduler executor refuses mismatched returned-group evidence");
        }
        for (const auto& [priority, observed_size] : group_observed_size) {
            if (observed_size != group_expected_size.at(priority)) {
                throw std::runtime_error(
                    "sync session checkpoint resume transfer workorder scheduler executor refuses a partial execution group");
            }
            if (!group_mutating.at(priority)) continue;
            const auto kind = group_kind.at(priority);
            if (!mutating_action_requested(kind)) continue;
            if (block_mutations_for_terminal_review) {
                ++out.mutating_action_groups_blocked_by_terminal_review;
                continue;
            }

            using ActionKind =
                SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind;
            switch (kind) {
                case ActionKind::ExecuteOwnedClaim:
                    ++out.execute_owned_claim_groups_selected;
                    ++out.mutating_action_groups_selected;
                    break;
                case ActionKind::ClaimOrReclaimExpired:
                    ++out.claim_or_reclaim_expired_groups_selected;
                    ++out.mutating_action_groups_selected;
                    break;
                case ActionKind::AbandonExpired:
                    ++out.abandon_expired_groups_selected;
                    ++out.mutating_action_groups_selected;
                    break;
                case ActionKind::ObserveLiveClaimedByOther:
                case ActionKind::WaitRetryBackoff:
                case ActionKind::ReviewAbandoned:
                case ActionKind::ReviewQuarantined:
                case ActionKind::IgnoreCompleted:
                    throw std::runtime_error(
                        "sync session checkpoint resume transfer workorder scheduler executor received a nonmutating execution group");
            }
        }
        out.mutations_blocked_by_terminal_review =
            out.mutating_actions_blocked_by_terminal_review != 0;

        claim_or_abandon_keys =
            sync_checkpoint_internal::unique_resume_transfer_execution_keys_or_throw(
                claim_or_abandon_keys,
                "sync session checkpoint resume transfer workorder scheduler executor claim/abandon");
        execute_keys =
            sync_checkpoint_internal::unique_resume_transfer_execution_keys_or_throw(
                execute_keys,
                "sync session checkpoint resume transfer workorder scheduler executor execute");
        out.execution_key_filters_built =
            static_cast<std::uint64_t>(claim_or_abandon_keys.size() +
                                       execute_keys.size());
        out.claim_or_abandon_filter_keys =
            static_cast<std::uint64_t>(claim_or_abandon_keys.size());
        out.execute_filter_keys =
            static_cast<std::uint64_t>(execute_keys.size());

        if (!claim_or_abandon_keys.empty()) {
            SyncSessionCheckpointResumeTransferClaimOptions claim_options;
            claim_options.sqlite_path = options.sqlite_path;
            claim_options.session_id = options.session_id;
            claim_options.daemon_owner_capability = options.daemon_owner_capability;
            claim_options.source_root_path = options.source_root_path;
            claim_options.destination_root_path = options.destination_root_path;
            claim_options.staging_root_path = options.staging_root_path;
            claim_options.expected_folder_id = options.expected_folder_id;
            claim_options.expected_source_device_id = options.expected_source_device_id;
            claim_options.expected_destination_device_id = options.expected_destination_device_id;
            claim_options.expected_peer_id = options.expected_peer_id;
            claim_options.peer_id = peer_id;
            claim_options.peer_session_id = peer_session_id;
            claim_options.require_durable_integrity = options.require_durable_integrity;
            claim_options.require_source_filesystem_match = options.require_source_filesystem_match;
            claim_options.fail_on_quarantine_or_reject = options.fail_on_quarantine_or_reject;
            claim_options.include_retry_transfer = options.include_retry_transfer;
            claim_options.worker_id = worker_id;
            claim_options.worker_lease_epoch = options.worker_lease_epoch;
            claim_options.workorder_claim_now_epoch = options.scheduler_now_epoch;
            claim_options.worker_lease_seconds = options.worker_lease_seconds;
            claim_options.workorder_retry_backoff_seconds = options.workorder_retry_backoff_seconds;
            claim_options.allow_expired_workorder_reclaim = options.allow_expired_workorder_reclaim;
            claim_options.max_workorder_claim_attempts = options.max_workorder_claim_attempts;
            claim_options.max_chunks_per_request = options.max_chunks_per_request;
            claim_options.max_bytes_per_request = options.max_bytes_per_request;
            claim_options.max_chunks_per_peer_round = options.max_chunks_per_peer_round;
            claim_options.max_bytes_per_peer_round = options.max_bytes_per_peer_round;
            claim_options.allowed_execution_idempotency_keys = claim_or_abandon_keys;
            SyncSessionCheckpointResumeTransferClaimResult claim_result;
            SyncValidationResult claim_run = claim_sync_session_checkpoint_resume_transfer_workorders(claim_options,
                                                                                                      claim_result);
            if (!claim_run.ok) {
                return fail_result("sync session checkpoint resume transfer workorder scheduler executor claim/abandon mutator failed: " + claim_run.reason);
            }
            out.claim_result = claim_result;
            out.claim_or_abandon_runs = 1;
            out.workorder_rows_claimed += claim_result.workorder_rows_claimed;
            out.workorder_rows_reclaimed += claim_result.workorder_rows_reclaimed;
            out.workorder_reclaim_events_written += claim_result.workorder_reclaim_events_written;
            out.workorder_rows_abandoned += claim_result.workorder_rows_abandoned;
            out.workorder_abandon_events_written += claim_result.workorder_abandon_events_written;
            out.workorder_rows_quarantined += claim_result.workorder_rows_quarantined;
            out.workorder_quarantine_events_written += claim_result.workorder_quarantine_events_written;
            if (claim_result.workorder_rows_reclaimed != out.claim_or_reclaim_expired_actions_selected ||
                claim_result.workorder_rows_abandoned != out.abandon_expired_actions_selected) {
                return fail_result("sync session checkpoint resume transfer workorder scheduler executor claim/abandon mutator did not consume exactly the selected scheduler actions");
            }
        }

        if (!execute_keys.empty()) {
            SyncSessionCheckpointResumeTransferExecutionOptions execution_options;
            execution_options.sqlite_path = options.sqlite_path;
            execution_options.session_id = options.session_id;
            execution_options.daemon_owner_capability = options.daemon_owner_capability;
            execution_options.source_root_path = options.source_root_path;
            execution_options.destination_root_path = options.destination_root_path;
            execution_options.staging_root_path = options.staging_root_path;
            execution_options.expected_folder_id = options.expected_folder_id;
            execution_options.expected_source_device_id = options.expected_source_device_id;
            execution_options.expected_destination_device_id = options.expected_destination_device_id;
            execution_options.expected_peer_id = options.expected_peer_id;
            execution_options.peer_id = peer_id;
            execution_options.peer_session_id = peer_session_id;
            execution_options.require_durable_integrity = options.require_durable_integrity;
            execution_options.require_source_filesystem_match = options.require_source_filesystem_match;
            execution_options.fail_on_quarantine_or_reject = options.fail_on_quarantine_or_reject;
            execution_options.include_retry_transfer = options.include_retry_transfer;
            execution_options.worker_id = worker_id;
            execution_options.worker_lease_epoch = options.worker_lease_epoch;
            execution_options.workorder_claim_now_epoch = options.scheduler_now_epoch;
            execution_options.worker_lease_seconds = options.worker_lease_seconds;
            execution_options.workorder_retry_backoff_seconds = options.workorder_retry_backoff_seconds;
            execution_options.allow_expired_workorder_reclaim = false;
            execution_options.max_workorder_claim_attempts = options.max_workorder_claim_attempts;
            execution_options.persist_workorder_claims = true;
            execution_options.max_chunks_per_request = options.max_chunks_per_request;
            execution_options.max_bytes_per_request = options.max_bytes_per_request;
            execution_options.max_chunks_per_peer_round = options.max_chunks_per_peer_round;
            execution_options.max_bytes_per_peer_round = options.max_bytes_per_peer_round;
            execution_options.allowed_execution_idempotency_keys = execute_keys;
            SyncSessionCheckpointResumeTransferExecutionResult execution_result;
            SyncValidationResult execution_run = execute_sync_session_checkpoint_resume_transfer_workorders(execution_options,
                                                                                                            execution_result);
            if (!execution_run.ok) {
                return fail_result("sync session checkpoint resume transfer workorder scheduler executor owned-claim mutator failed: " + execution_run.reason);
            }
            out.execution_result = execution_result;
            out.execute_owned_runs = 1;
            out.workorder_rows_claimed += execution_result.workorder_rows_claimed;
            out.workorder_rows_reclaimed += execution_result.workorder_rows_reclaimed;
            out.workorder_reclaim_events_written += execution_result.workorder_reclaim_events_written;
            out.workorder_rows_abandoned += execution_result.workorder_rows_abandoned;
            out.workorder_abandon_events_written += execution_result.workorder_abandon_events_written;
            out.workorder_rows_quarantined += execution_result.workorder_rows_quarantined;
            out.workorder_quarantine_events_written += execution_result.workorder_quarantine_events_written;
            out.workorder_rows_completed += execution_result.workorder_rows_completed;
            out.chunks_written += execution_result.chunks_written;
            out.receipts_reused += execution_result.receipts_reused;
            out.receipt_rows_upserted += execution_result.receipt_rows_upserted;
            out.bytes_written += execution_result.bytes_written;
            if (execution_result.workorder_rows_completed != out.execute_owned_claim_actions_selected) {
                return fail_result("sync session checkpoint resume transfer workorder scheduler executor owned-claim mutator did not consume exactly the selected scheduler actions");
            }
        }

        out.scheduler_execution_completed = true;
        return ok_result();
    } catch (const std::exception& e) {
        out = SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult{};
        return fail_result(std::string("sync session checkpoint resume transfer workorder scheduler executor failed: ") + e.what());
    }
}

}  // namespace anonsync
