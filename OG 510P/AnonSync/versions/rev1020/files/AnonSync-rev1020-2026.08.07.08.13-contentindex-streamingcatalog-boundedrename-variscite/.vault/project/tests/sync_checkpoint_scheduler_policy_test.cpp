#include "sync_checkpoint_scheduler_policy.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using Action =
    anonsync::SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction;
using ActionKind =
    anonsync::SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind;
using Fact =
    anonsync::SyncSessionCheckpointResumeTransferWorkorderQueueFact;
using PassResult =
    anonsync::SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult;
using QueueKind =
    anonsync::SyncSessionCheckpointResumeTransferWorkorderQueueKind;
using ValidationResult = anonsync::SyncValidationResult;

void require(bool condition,
             const std::string& message,
             std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

std::string authority_key(const std::string& prefix,
                          const std::string& suffix) {
    if (suffix.empty()) {
        throw std::runtime_error("authority-key fixture suffix is empty");
    }
    static constexpr char hex[] = "0123456789abcdef";
    std::string digest;
    digest.reserve(64);
    for (std::size_t index = 0; index < 64; ++index) {
        const unsigned char source = static_cast<unsigned char>(
            suffix[index % suffix.size()]);
        const std::size_t nibble =
            (static_cast<std::size_t>(source) + index) % 16U;
        digest.push_back(hex[nibble]);
    }
    return prefix + digest;
}

std::string execution_key(const std::string& suffix) {
    return authority_key("sync-resume-transfer-execute:v1:", suffix);
}

Fact make_fact(QueueKind kind,
               const std::string& path,
               const std::string& key = "") {
    Fact fact;
    fact.path = anonsync::NormalizedSyncPath{path};
    fact.queue_kind = kind;
    fact.queue_reason = "queue:" + path;
    switch (kind) {
        case QueueKind::OwnedClaimReady:
        case QueueKind::LiveClaimedByOther:
        case QueueKind::ExpiredCoolingDown:
        case QueueKind::ExpiredReclaimReady:
        case QueueKind::ExpiredAbandonReady:
            fact.work_state = "claimed";
            break;
        case QueueKind::AbandonedReview:
            fact.work_state = "abandoned";
            break;
        case QueueKind::QuarantinedReview:
            fact.work_state = "quarantined";
            break;
        case QueueKind::CompletedIgnored:
            fact.work_state = "completed";
            break;
    }
    fact.source_action = "resume-transfer";
    fact.request_idempotency_key = authority_key(
        "sync-resume-transfer-request:v1:", path);
    fact.peer_request_idempotency_key = authority_key(
        "sync-resume-peer-request:v1:", path);
    fact.schedule_idempotency_key = authority_key(
        "sync-resume-peer-schedule:v1:", path);
    fact.execution_idempotency_key = key.empty() ? execution_key(path) : key;
    fact.peer_id = "peer-a";
    fact.peer_session_id = "peer-session-a";
    fact.worker_id = "worker-a";
    fact.worker_lease_id = authority_key(
        "sync-resume-transfer-lease:v1:", path);
    fact.chunk_sha256 = std::string(64, 'a');
    fact.owned_by_selector_worker = kind == QueueKind::OwnedClaimReady;
    fact.lease_expired = kind == QueueKind::ExpiredCoolingDown ||
                         kind == QueueKind::ExpiredReclaimReady ||
                         kind == QueueKind::ExpiredAbandonReady;
    fact.retry_window_open = kind == QueueKind::ExpiredReclaimReady ||
                             kind == QueueKind::ExpiredAbandonReady;
    fact.terminal_review_required = kind == QueueKind::AbandonedReview ||
                                    kind == QueueKind::QuarantinedReview;
    fact.chunk_offset = 17;
    fact.chunk_length = 23;
    fact.worker_lease_epoch = 7;
    fact.claimed_at_epoch = 101;
    fact.lease_expires_at_epoch = 202;
    fact.retry_at_epoch = 303;
    fact.claim_attempts = 2;
    return fact;
}

std::uint8_t action_class(ActionKind kind) noexcept {
    switch (kind) {
        case ActionKind::ReviewAbandoned:
        case ActionKind::ReviewQuarantined:
            return 0;
        case ActionKind::ExecuteOwnedClaim:
        case ActionKind::ClaimOrReclaimExpired:
        case ActionKind::AbandonExpired:
            return 1;
        case ActionKind::ObserveLiveClaimedByOther:
        case ActionKind::WaitRetryBackoff:
            return 2;
        case ActionKind::IgnoreCompleted:
            return 3;
    }
    return 255;
}

void require_contiguous_group_evidence(const PassResult& result,
                                       std::uint64_t& checks) {
    std::uint64_t expected_action_priority = 1;
    std::uint64_t previous_group_priority = 0;
    std::uint64_t observed_in_group = 0;
    std::uint64_t expected_group_size = 0;
    std::string current_execution_key;
    bool current_mutating = false;
    ActionKind current_kind = ActionKind::IgnoreCompleted;

    for (const auto& action : result.actions) {
        require(action.scheduler_priority == expected_action_priority,
                "scheduler action priorities are not contiguous", checks);
        ++expected_action_priority;
        require(action.scheduler_group_priority != 0 &&
                    action.scheduler_group_size != 0,
                "scheduler action lacks group evidence", checks);
        if (action.scheduler_group_priority != previous_group_priority) {
            if (previous_group_priority != 0) {
                require(observed_in_group == expected_group_size,
                        "previous scheduler group was partial", checks);
            }
            require(action.scheduler_group_priority ==
                        previous_group_priority + 1,
                    "scheduler group priorities are not contiguous", checks);
            previous_group_priority = action.scheduler_group_priority;
            observed_in_group = 0;
            expected_group_size = action.scheduler_group_size;
            current_execution_key = action.execution_idempotency_key;
            current_mutating = action.mutating_action;
            current_kind = action.action_kind;
        } else {
            require(action.scheduler_group_size == expected_group_size &&
                        action.execution_idempotency_key ==
                            current_execution_key &&
                        action.mutating_action == current_mutating &&
                        action.action_kind == current_kind,
                    "scheduler group mixed authority", checks);
        }
        ++observed_in_group;
        if (!action.mutating_action) {
            require(action.scheduler_group_size == 1,
                    "observation was grouped as mutation authority", checks);
        }
    }
    if (previous_group_priority != 0) {
        require(observed_in_group == expected_group_size,
                "last scheduler group was partial", checks);
    }
}

void test_all_queue_permutations(std::uint64_t& checks) {
    const std::array<QueueKind, 8> kinds = {
        QueueKind::OwnedClaimReady,
        QueueKind::LiveClaimedByOther,
        QueueKind::ExpiredCoolingDown,
        QueueKind::ExpiredReclaimReady,
        QueueKind::ExpiredAbandonReady,
        QueueKind::AbandonedReview,
        QueueKind::QuarantinedReview,
        QueueKind::CompletedIgnored,
    };
    std::array<int, 8> permutation = {0, 1, 2, 3, 4, 5, 6, 7};
    std::uint64_t permutations = 0;
    do {
        std::vector<Fact> facts;
        facts.reserve(permutation.size());
        for (int raw_index : permutation) {
            const std::size_t index = static_cast<std::size_t>(raw_index);
            facts.push_back(make_fact(
                kinds[index], "permutation-" + std::to_string(index)));
        }

        PassResult result;
        const ValidationResult run =
            anonsync::sync_checkpoint_scheduler_policy::
                plan_resume_transfer_workorder_actions(facts, 0, result);
        require(run.ok && result.scheduler_plan_completed,
                "permutation policy run failed: " + run.reason, checks);
        require(result.actions.size() == facts.size() &&
                    result.scheduler_actions_returned == facts.size(),
                "permutation policy dropped an unlimited action", checks);
        require(result.review_abandoned_actions == 1 &&
                    result.review_quarantined_actions == 1 &&
                    result.mutating_actions_planned == 3 &&
                    result.observe_live_claimed_by_other_actions == 1 &&
                    result.wait_retry_backoff_actions == 1 &&
                    result.ignore_completed_actions == 1,
                "permutation policy count mismatch", checks);
        std::uint8_t previous_class = 0;
        bool first = true;
        for (const auto& action : result.actions) {
            const std::uint8_t current_class = action_class(action.action_kind);
            require(first || current_class >= previous_class,
                    "permutation policy violated review/mutation/observation ordering",
                    checks);
            previous_class = current_class;
            first = false;
        }
        require_contiguous_group_evidence(result, checks);

        PassResult capped;
        const ValidationResult capped_run =
            anonsync::sync_checkpoint_scheduler_policy::
                plan_resume_transfer_workorder_actions(facts, 1, capped);
        require(capped_run.ok && capped.scheduler_plan_completed &&
                    capped.actions.size() == 1 &&
                    action_class(capped.actions.front().action_kind) == 0 &&
                    capped.scheduler_actions_deferred_by_limit == 7,
                "bounded permutation failed to surface terminal review first",
                checks);
        ++permutations;
    } while (std::next_permutation(permutation.begin(), permutation.end()));

    require(permutations == 40320,
            "did not enumerate all eight-kind scheduler permutations", checks);
}

void test_atomic_groups_and_priority_barrier(std::uint64_t& checks) {
    const std::string shared_key = execution_key("shared-owned-group");
    std::vector<Fact> facts = {
        make_fact(QueueKind::LiveClaimedByOther, "passive"),
        make_fact(QueueKind::OwnedClaimReady, "owned-a", shared_key),
        make_fact(QueueKind::QuarantinedReview, "review"),
        make_fact(QueueKind::OwnedClaimReady, "owned-b", shared_key),
    };

    for (std::uint64_t cap = 1; cap <= 2; ++cap) {
        PassResult result;
        const ValidationResult run =
            anonsync::sync_checkpoint_scheduler_policy::
                plan_resume_transfer_workorder_actions(facts, cap, result);
        require(run.ok && result.actions.size() == 1 &&
                    result.actions.front().action_kind ==
                        ActionKind::ReviewQuarantined &&
                    result.scheduler_action_groups_returned == 1 &&
                    result.scheduler_action_groups_deferred_by_limit == 2 &&
                    result.scheduler_actions_deferred_by_limit == 3,
                "limit split or bypassed higher-priority atomic group", checks);
    }

    PassResult exact;
    const ValidationResult exact_run =
        anonsync::sync_checkpoint_scheduler_policy::
            plan_resume_transfer_workorder_actions(facts, 3, exact);
    require(exact_run.ok && exact.actions.size() == 3 &&
                exact.review_quarantined_actions == 1 &&
                exact.execute_owned_claim_actions == 2 &&
                exact.actions[1].scheduler_group_priority == 2 &&
                exact.actions[2].scheduler_group_priority == 2 &&
                exact.actions[1].scheduler_group_size == 2 &&
                exact.scheduler_actions_deferred_by_limit == 1,
            "exact cap did not admit complete review and mutation groups",
            checks);
    require_contiguous_group_evidence(exact, checks);

    PassResult unlimited;
    const ValidationResult unlimited_run =
        anonsync::sync_checkpoint_scheduler_policy::
            plan_resume_transfer_workorder_actions(facts, 0, unlimited);
    require(unlimited_run.ok && unlimited.actions.size() == 4 &&
                unlimited.scheduler_action_groups_returned == 3 &&
                unlimited.scheduler_actions_deferred_by_limit == 0,
            "unlimited grouping changed action inventory", checks);
    require_contiguous_group_evidence(unlimited, checks);
}

void test_terminal_review_preserves_hostile_evidence(std::uint64_t& checks) {
    Fact fact = make_fact(QueueKind::QuarantinedReview, "hostile-review");
    fact.schedule_idempotency_key =
        "sync-resume-peer-schedule:v1:quarantine-mismatch";
    fact.execution_idempotency_key = "hostile-execution-key";
    fact.worker_lease_id = "hostile-lease-key";

    PassResult result;
    const ValidationResult run =
        anonsync::sync_checkpoint_scheduler_policy::
            plan_resume_transfer_workorder_actions({fact}, 0, result);
    require(run.ok && result.scheduler_plan_completed &&
                result.actions.size() == 1 &&
                result.actions[0].action_kind ==
                    ActionKind::ReviewQuarantined &&
                !result.actions[0].mutating_action &&
                result.actions[0].terminal_review_required &&
                result.actions[0].schedule_idempotency_key ==
                    fact.schedule_idempotency_key,
            "terminal review rejected or laundered hostile historical authority",
            checks);
}

void test_inconsistent_authority_rejections(std::uint64_t& checks) {
    auto rejected = [&](Fact fact,
                        const std::string& expected_reason,
                        const std::string& message) {
        PassResult result;
        result.scheduler_actions_returned = 99;
        const ValidationResult run =
            anonsync::sync_checkpoint_scheduler_policy::
                plan_resume_transfer_workorder_actions({fact}, 0, result);
        require(!run.ok && run.reason.find(expected_reason) !=
                               std::string::npos,
                message, checks);
        require(!result.scheduler_plan_completed && result.actions.empty() &&
                    result.scheduler_actions_returned == 0,
                message + " did not reset output", checks);
    };

    {
        Fact fact = make_fact(QueueKind::OwnedClaimReady, "state-spoof");
        fact.work_state = "quarantined";
        rejected(std::move(fact), "owned ready claim",
                 "runnable enum with quarantined state was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::OwnedClaimReady, "owner-spoof");
        fact.owned_by_selector_worker = false;
        rejected(std::move(fact), "owned ready claim",
                 "owned-ready action without matching worker was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::ExpiredReclaimReady, "lease-spoof");
        fact.lease_expired = false;
        rejected(std::move(fact), "expired mutation",
                 "reclaim action with live lease was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::QuarantinedReview, "review-spoof");
        fact.terminal_review_required = false;
        rejected(std::move(fact), "terminal-review evidence",
                 "quarantine review without review evidence was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::LiveClaimedByOther, "source-spoof");
        fact.source_action = "publish-local";
        rejected(std::move(fact), "source action",
                 "invalid workorder source action was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::ExpiredCoolingDown, "timing-spoof");
        fact.retry_at_epoch = fact.lease_expires_at_epoch - 1;
        rejected(std::move(fact), "lease timing evidence",
                 "malformed retry timing was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::CompletedIgnored, "hash-spoof");
        fact.chunk_sha256[0] = 'A';
        rejected(std::move(fact), "chunk hash",
                 "noncanonical chunk hash was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::AbandonedReview, "zero-chunk");
        fact.chunk_length = 0;
        rejected(std::move(fact), "chunk length",
                 "zero-length workorder chunk was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::OwnedClaimReady, "request-spoof");
        fact.request_idempotency_key =
            "sync-resume-transfer-request:v1:short";
        rejected(std::move(fact), "request-key authority",
                 "malformed mutation request authority was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::ExpiredReclaimReady,
                              "lease-key-spoof");
        fact.worker_lease_id = "wrong-lease-namespace";
        rejected(std::move(fact), "worker-lease authority",
                 "malformed mutation lease authority was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::OwnedClaimReady, "epoch-spoof");
        fact.worker_lease_epoch = 0;
        rejected(std::move(fact), "worker lease epoch",
                 "zero lease epoch was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::ExpiredReclaimReady, "range-spoof");
        fact.chunk_offset = std::numeric_limits<std::uint64_t>::max();
        fact.chunk_length = 2;
        rejected(std::move(fact), "chunk range",
                 "overflowing chunk range was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::OwnedClaimReady, "execution-spoof");
        fact.execution_idempotency_key = "wrong-execution-namespace";
        rejected(std::move(fact), "execution-key authority",
                 "malformed mutation execution authority was not rejected");
    }
    {
        Fact fact = make_fact(QueueKind::OwnedClaimReady, "empty-path");
        fact.path.value.clear();
        rejected(std::move(fact), "normalized path is empty",
                 "empty normalized path was not rejected");
    }
}

void test_empty_input(std::uint64_t& checks) {
    PassResult result;
    const ValidationResult run =
        anonsync::sync_checkpoint_scheduler_policy::
            plan_resume_transfer_workorder_actions({}, 1, result);
    require(run.ok && result.scheduler_plan_completed &&
                result.actions.empty() &&
                result.scheduler_action_groups_considered == 0,
            "empty policy input was not a completed empty plan", checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        test_empty_input(checks);
        test_atomic_groups_and_priority_barrier(checks);
        test_terminal_review_preserves_hostile_evidence(checks);
        test_inconsistent_authority_rejections(checks);
        test_all_queue_permutations(checks);
        std::cout << "sync checkpoint scheduler policy tests passed: "
                  << checks << '/' << checks << '\n';
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sync checkpoint scheduler policy tests failed after "
                  << checks << " checks: " << e.what() << '\n';
        return 1;
    }
}
