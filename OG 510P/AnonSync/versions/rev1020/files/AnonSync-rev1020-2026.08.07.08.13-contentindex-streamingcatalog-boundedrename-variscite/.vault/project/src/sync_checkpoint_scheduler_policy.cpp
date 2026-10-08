#include "sync_checkpoint_scheduler_policy.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync::sync_checkpoint_scheduler_policy {
namespace {

SyncValidationResult ok_result() {
    return {true, ""};
}

SyncValidationResult fail_result(const std::string& reason) {
    return {false, reason};
}

enum class SchedulerPriorityClass : std::uint8_t {
    TerminalReview = 0,
    Mutating = 1,
    PassiveObservation = 2,
    CompletedObservation = 3,
};

struct ActionBlueprint final {
    SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind action_kind;
    const char* action_reason;
    bool mutating_action;
    SchedulerPriorityClass priority_class;
};

using QueueFact =
    SyncSessionCheckpointResumeTransferWorkorderQueueFact;
using QueueKind =
    SyncSessionCheckpointResumeTransferWorkorderQueueKind;

bool is_lowercase_sha256_digest(std::string_view value) noexcept {
    return value.size() == 64 &&
           std::all_of(value.begin(), value.end(), [](char c) {
               return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f');
           });
}

bool has_sha256_authority_suffix(const std::string& value,
                                 std::string_view prefix) noexcept {
    if (!value.starts_with(prefix) ||
        value.size() != prefix.size() + 64) {
        return false;
    }
    return is_lowercase_sha256_digest(
        std::string_view(value).substr(prefix.size()));
}

void require_fact_relationship(bool condition, const char* reason) {
    if (condition) return;
    throw std::runtime_error(
        std::string(
            "sync checkpoint scheduler policy refuses inconsistent queue fact: ") +
        reason);
}

bool mutating_queue_kind(QueueKind kind) noexcept {
    return kind == QueueKind::OwnedClaimReady ||
           kind == QueueKind::ExpiredReclaimReady ||
           kind == QueueKind::ExpiredAbandonReady;
}

void validate_queue_fact_or_throw(const QueueFact& fact) {
    require_fact_relationship(!fact.path.value.empty(),
                              "normalized path is empty");
    require_fact_relationship(
        fact.source_action == "resume-transfer" ||
            fact.source_action == "retry-transfer",
        "source action is not authorized for a resume workorder");
    require_fact_relationship(is_lowercase_sha256_digest(fact.chunk_sha256),
                              "chunk hash is not lowercase SHA-256 evidence");
    require_fact_relationship(fact.chunk_length != 0,
                              "chunk length is zero");
    require_fact_relationship(
        fact.chunk_offset <=
            std::numeric_limits<std::uint64_t>::max() - fact.chunk_length,
        "chunk range overflows uint64 authority");
    require_fact_relationship(fact.worker_lease_epoch != 0,
                              "worker lease epoch is zero");
    require_fact_relationship(
        fact.claimed_at_epoch != 0 &&
            fact.lease_expires_at_epoch > fact.claimed_at_epoch &&
            fact.retry_at_epoch >= fact.lease_expires_at_epoch &&
            fact.claim_attempts != 0,
        "lease timing evidence is malformed");

    const bool terminal_kind =
        fact.queue_kind == QueueKind::AbandonedReview ||
        fact.queue_kind == QueueKind::QuarantinedReview;
    require_fact_relationship(
        fact.terminal_review_required == terminal_kind,
        "terminal-review evidence disagrees with queue kind");

    switch (fact.queue_kind) {
        case QueueKind::OwnedClaimReady:
            require_fact_relationship(
                fact.work_state == "claimed" &&
                    fact.owned_by_selector_worker &&
                    !fact.lease_expired &&
                    !fact.retry_window_open,
                "owned ready claim lacks live matching ownership evidence");
            break;
        case QueueKind::LiveClaimedByOther:
            require_fact_relationship(
                fact.work_state == "claimed" &&
                    !fact.owned_by_selector_worker &&
                    !fact.lease_expired &&
                    !fact.retry_window_open,
                "live foreign claim evidence disagrees with queue kind");
            break;
        case QueueKind::ExpiredCoolingDown:
            require_fact_relationship(
                fact.work_state == "claimed" &&
                    fact.lease_expired &&
                    !fact.retry_window_open,
                "cooling claim lacks expired closed-retry evidence");
            break;
        case QueueKind::ExpiredReclaimReady:
        case QueueKind::ExpiredAbandonReady:
            require_fact_relationship(
                fact.work_state == "claimed" &&
                    fact.lease_expired &&
                    fact.retry_window_open,
                "expired mutation lacks expired open-retry evidence");
            break;
        case QueueKind::AbandonedReview:
            require_fact_relationship(
                fact.work_state == "abandoned",
                "abandoned review state disagrees with queue kind");
            break;
        case QueueKind::QuarantinedReview:
            require_fact_relationship(
                fact.work_state == "quarantined",
                "quarantined review state disagrees with queue kind");
            break;
        case QueueKind::CompletedIgnored:
            require_fact_relationship(
                fact.work_state == "completed",
                "completed observation state disagrees with queue kind");
            break;
    }

    // Terminal-review rows may intentionally contain malformed historical
    // key authority; surfacing that evidence must not launder it into mutation
    // and must not hide it by rejecting the review observation. Exact key
    // namespace and digest shape are therefore required only before a mutating
    // action is minted.
    if (!mutating_queue_kind(fact.queue_kind)) return;
    require_fact_relationship(
        has_sha256_authority_suffix(
            fact.request_idempotency_key,
            "sync-resume-transfer-request:v1:"),
        "request-key authority is malformed");
    require_fact_relationship(
        has_sha256_authority_suffix(
            fact.peer_request_idempotency_key,
            "sync-resume-peer-request:v1:"),
        "peer-request-key authority is malformed");
    require_fact_relationship(
        has_sha256_authority_suffix(
            fact.schedule_idempotency_key,
            "sync-resume-peer-schedule:v1:"),
        "schedule-key authority is malformed");
    require_fact_relationship(
        has_sha256_authority_suffix(
            fact.execution_idempotency_key,
            "sync-resume-transfer-execute:v1:"),
        "execution-key authority is malformed");
    require_fact_relationship(
        has_sha256_authority_suffix(
            fact.worker_lease_id,
            "sync-resume-transfer-lease:v1:"),
        "worker-lease authority is malformed");
}

ActionBlueprint action_blueprint_or_throw(QueueKind queue_kind) {
    using ActionKind =
        SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind;
    switch (queue_kind) {
        case QueueKind::OwnedClaimReady:
            return {ActionKind::ExecuteOwnedClaim,
                    "execute-owned-claimed-workorder",
                    true,
                    SchedulerPriorityClass::Mutating};
        case QueueKind::ExpiredReclaimReady:
            return {ActionKind::ClaimOrReclaimExpired,
                    "claim-or-reclaim-expired-retry-open-workorder",
                    true,
                    SchedulerPriorityClass::Mutating};
        case QueueKind::ExpiredAbandonReady:
            return {ActionKind::AbandonExpired,
                    "abandon-expired-workorder-at-attempt-cap",
                    true,
                    SchedulerPriorityClass::Mutating};
        case QueueKind::LiveClaimedByOther:
            return {ActionKind::ObserveLiveClaimedByOther,
                    "skip-live-claim-held-by-another-worker-or-unknown-lease",
                    false,
                    SchedulerPriorityClass::PassiveObservation};
        case QueueKind::ExpiredCoolingDown:
            return {ActionKind::WaitRetryBackoff,
                    "wait-for-retry-at-before-reclaim",
                    false,
                    SchedulerPriorityClass::PassiveObservation};
        case QueueKind::AbandonedReview:
            return {ActionKind::ReviewAbandoned,
                    "surface-abandoned-workorder-for-terminal-review",
                    false,
                    SchedulerPriorityClass::TerminalReview};
        case QueueKind::QuarantinedReview:
            return {ActionKind::ReviewQuarantined,
                    "surface-quarantined-workorder-for-safety-review",
                    false,
                    SchedulerPriorityClass::TerminalReview};
        case QueueKind::CompletedIgnored:
            return {ActionKind::IgnoreCompleted,
                    "ignore-completed-workorder-in-daemon-pass",
                    false,
                    SchedulerPriorityClass::CompletedObservation};
    }
    throw std::runtime_error(
        "sync checkpoint scheduler policy received an unknown queue kind");
}

SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction make_action(
    const QueueFact& fact,
    const ActionBlueprint& blueprint) {
    SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction action;
    action.path = fact.path;
    action.action_kind = blueprint.action_kind;
    action.source_queue_kind = fact.queue_kind;
    action.action_reason = blueprint.action_reason;
    action.queue_reason = fact.queue_reason;
    action.work_state = fact.work_state;
    action.source_action = fact.source_action;
    action.request_idempotency_key = fact.request_idempotency_key;
    action.peer_request_idempotency_key = fact.peer_request_idempotency_key;
    action.schedule_idempotency_key = fact.schedule_idempotency_key;
    action.execution_idempotency_key = fact.execution_idempotency_key;
    action.peer_id = fact.peer_id;
    action.peer_session_id = fact.peer_session_id;
    action.worker_id = fact.worker_id;
    action.worker_lease_id = fact.worker_lease_id;
    action.chunk_sha256 = fact.chunk_sha256;
    action.mutating_action = blueprint.mutating_action;
    action.terminal_review_required = fact.terminal_review_required;
    action.owned_by_scheduler_worker = fact.owned_by_selector_worker;
    action.lease_expired = fact.lease_expired;
    action.retry_window_open = fact.retry_window_open;
    action.chunk_offset = fact.chunk_offset;
    action.chunk_length = fact.chunk_length;
    action.claimed_at_epoch = fact.claimed_at_epoch;
    action.lease_expires_at_epoch = fact.lease_expires_at_epoch;
    action.retry_at_epoch = fact.retry_at_epoch;
    action.claim_attempts = fact.claim_attempts;
    return action;
}

struct SchedulerActionGroup final {
    SchedulerPriorityClass priority_class =
        SchedulerPriorityClass::PassiveObservation;
    std::string mutation_execution_key;
    SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind action_kind =
        SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::
            ObserveLiveClaimedByOther;
    std::vector<SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction>
        actions;
};

bool group_fits(std::uint64_t returned,
                std::uint64_t group_size,
                std::uint64_t maximum) noexcept {
    if (maximum == 0) return true;
    if (returned > maximum || group_size > maximum) return false;
    return group_size <= maximum - returned;
}

void count_returned_action(
    const SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction& action,
    SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult& out) {
    using ActionKind =
        SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind;
    if (action.mutating_action) ++out.mutating_actions_planned;
    switch (action.action_kind) {
        case ActionKind::ExecuteOwnedClaim:
            ++out.execute_owned_claim_actions;
            break;
        case ActionKind::ClaimOrReclaimExpired:
            ++out.claim_or_reclaim_expired_actions;
            break;
        case ActionKind::AbandonExpired:
            ++out.abandon_expired_actions;
            break;
        case ActionKind::ObserveLiveClaimedByOther:
            ++out.observe_live_claimed_by_other_actions;
            break;
        case ActionKind::WaitRetryBackoff:
            ++out.wait_retry_backoff_actions;
            break;
        case ActionKind::ReviewAbandoned:
            ++out.review_abandoned_actions;
            break;
        case ActionKind::ReviewQuarantined:
            ++out.review_quarantined_actions;
            break;
        case ActionKind::IgnoreCompleted:
            ++out.ignore_completed_actions;
            break;
    }
}

}  // namespace

SyncValidationResult plan_resume_transfer_workorder_actions(
    const std::vector<QueueFact>& facts,
    std::uint64_t max_scheduler_actions,
    SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult& out) {
    out = SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult{};
    out.max_scheduler_actions = max_scheduler_actions;
    out.queue_facts_considered = static_cast<std::uint64_t>(facts.size());

    try {
        std::vector<SchedulerActionGroup> groups;
        groups.reserve(facts.size());
        std::map<std::string, std::size_t> mutation_group_index;

        for (const auto& fact : facts) {
            validate_queue_fact_or_throw(fact);
            const ActionBlueprint blueprint =
                action_blueprint_or_throw(fact.queue_kind);
            auto action = make_action(fact, blueprint);

            if (!blueprint.mutating_action) {
                // Observations carry no mutation atomicity. Singleton review
                // groups guarantee that a positive bounded pass surfaces at
                // least one terminal review before any mutation class.
                SchedulerActionGroup group;
                group.priority_class = blueprint.priority_class;
                group.action_kind = blueprint.action_kind;
                group.actions.push_back(std::move(action));
                groups.push_back(std::move(group));
                continue;
            }

            auto found = mutation_group_index.find(
                fact.execution_idempotency_key);
            if (found == mutation_group_index.end()) {
                SchedulerActionGroup group;
                group.priority_class = SchedulerPriorityClass::Mutating;
                group.mutation_execution_key = fact.execution_idempotency_key;
                group.action_kind = blueprint.action_kind;
                group.actions.push_back(std::move(action));
                const std::size_t index = groups.size();
                groups.push_back(std::move(group));
                mutation_group_index.emplace(fact.execution_idempotency_key,
                                             index);
            } else {
                auto& group = groups.at(found->second);
                if (group.priority_class != SchedulerPriorityClass::Mutating ||
                    group.action_kind != blueprint.action_kind ||
                    group.mutation_execution_key !=
                        fact.execution_idempotency_key) {
                    throw std::runtime_error(
                        "sync checkpoint scheduler policy refuses mixed mutation authority inside one execution group");
                }
                group.actions.push_back(std::move(action));
            }
        }

        std::stable_sort(
            groups.begin(), groups.end(),
            [](const SchedulerActionGroup& left,
               const SchedulerActionGroup& right) {
                return left.priority_class < right.priority_class;
            });
        out.scheduler_action_groups_considered =
            static_cast<std::uint64_t>(groups.size());

        std::optional<SchedulerPriorityClass> deferred_priority_barrier;
        for (auto& group : groups) {
            const std::uint64_t group_size =
                static_cast<std::uint64_t>(group.actions.size());
            const bool blocked_by_higher_priority =
                deferred_priority_barrier.has_value() &&
                group.priority_class > *deferred_priority_barrier;
            if (blocked_by_higher_priority ||
                !group_fits(out.scheduler_actions_returned,
                            group_size,
                            max_scheduler_actions)) {
                ++out.scheduler_action_groups_deferred_by_limit;
                out.scheduler_actions_deferred_by_limit += group_size;
                if (!deferred_priority_barrier.has_value() ||
                    group.priority_class < *deferred_priority_barrier) {
                    deferred_priority_barrier = group.priority_class;
                }
                continue;
            }

            ++out.scheduler_action_groups_returned;
            const std::uint64_t group_priority =
                out.scheduler_action_groups_returned;
            for (auto& action : group.actions) {
                action.scheduler_priority =
                    static_cast<std::uint64_t>(out.actions.size()) + 1;
                action.scheduler_group_priority = group_priority;
                action.scheduler_group_size = group_size;
                count_returned_action(action, out);
                out.actions.push_back(std::move(action));
            }
            out.scheduler_actions_returned =
                static_cast<std::uint64_t>(out.actions.size());
        }

        out.scheduler_plan_completed = true;
        return ok_result();
    } catch (const std::exception& e) {
        out = SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult{};
        return fail_result(
            std::string("sync checkpoint scheduler policy failed: ") +
            e.what());
    }
}

}  // namespace anonsync::sync_checkpoint_scheduler_policy
