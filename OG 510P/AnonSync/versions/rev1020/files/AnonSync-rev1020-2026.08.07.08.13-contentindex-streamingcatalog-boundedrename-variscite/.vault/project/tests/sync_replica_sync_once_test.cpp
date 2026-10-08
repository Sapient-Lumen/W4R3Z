#include "sync_replica_sync_once.hpp"

#if !defined(_WIN32)

#include <array>
#include <cstddef>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace {

std::size_t checks = 0U;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected_fragment,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected_fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

struct DispositionExpectation final {
    anonsync::SyncReplicaSyncOnceDisposition disposition;
    std::string_view name;
    bool complete;
    bool settled;
    bool bounded_progress;
};

constexpr std::array<DispositionExpectation, 21> kExpectations{{
    {anonsync::SyncReplicaSyncOnceDisposition::CompleteNoOp,
     "complete_no_op", true, true, true},
    {anonsync::SyncReplicaSyncOnceDisposition::CompleteChanged,
     "complete_changed", true, true, true},
    {anonsync::SyncReplicaSyncOnceDisposition::CompleteWithUnresolvedPaths,
     "complete_with_unresolved_paths", true, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         CommandDeadlineReachedBeforeLocalPass,
     "command_deadline_before_local_pass", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::
         CommandDeadlineReachedBeforePull,
     "command_deadline_before_pull", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         CommandDeadlineReachedBeforeRemoteApply,
     "command_deadline_before_remote_apply", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::ConnectDeadlineExpired,
     "connect_deadline_expired", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::ConnectFailed,
     "connect_failed", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::RouteDeadlineExpired,
     "route_deadline_expired", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::RouteRejected,
     "route_rejected", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::HandshakeDeadlineExpired,
     "handshake_deadline_expired", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::HandshakeRejected,
     "handshake_rejected", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::PeerUnauthorized,
     "peer_unauthorized", false, false, false},
    {anonsync::SyncReplicaSyncOnceDisposition::
         ReconciliationRoundTripLimitReached,
     "reconciliation_round_trip_limit_reached", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         ReconciliationSourceChangedLimitReached,
     "reconciliation_source_changed_limit_reached", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         ReconciliationSourcePayloadUnavailable,
     "reconciliation_source_payload_unavailable", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         ReconciliationSourcePayloadPreparing,
     "reconciliation_source_payload_preparing", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         ReconciliationReceiverCapacityBlocked,
     "reconciliation_receiver_capacity_blocked", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         ReconciliationRequestDeadlineExpired,
     "reconciliation_request_deadline_expired", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::
         ReconciliationResponseDeadlineExpired,
     "reconciliation_response_deadline_expired", false, false, true},
    {anonsync::SyncReplicaSyncOnceDisposition::ReconciliationPeerClosed,
     "reconciliation_peer_closed", false, false, true},
}};

void test_disposition_contract() {
    for (const auto& expectation : kExpectations) {
        const std::string prefix(expectation.name);
        require(
            anonsync::sync_replica_sync_once_disposition_name(
                expectation.disposition) == expectation.name,
            prefix + " name changed");
        require(
            anonsync::sync_replica_sync_once_is_complete(
                expectation.disposition) == expectation.complete,
            prefix + " completion class changed");
        require(
            anonsync::sync_replica_sync_once_is_settled(
                expectation.disposition) == expectation.settled,
            prefix + " settlement class changed");
        require(
            anonsync::sync_replica_sync_once_is_bounded_progress(
                expectation.disposition) == expectation.bounded_progress,
            prefix + " bounded-progress class changed");
    }

    const auto unknown = static_cast<anonsync::SyncReplicaSyncOnceDisposition>(
        255U);
    require(
        anonsync::sync_replica_sync_once_disposition_name(unknown) ==
            "unknown",
        "unknown disposition name changed");
    require(
        !anonsync::sync_replica_sync_once_is_complete(unknown),
        "unknown disposition became complete");
    require(
        !anonsync::sync_replica_sync_once_is_settled(unknown),
        "unknown disposition became settled");
    require(
        !anonsync::sync_replica_sync_once_is_bounded_progress(unknown),
        "unknown disposition became bounded progress");
}

void test_durable_progress_contract() {
    anonsync::SyncReplicaSyncOnceResult result;
    result.before.catalog_generation = 3U;
    result.before.catalog_entries = 2U;
    result.before.catalog_digest = std::string(64U, '1');
    result.before.replica_generation = 5U;
    result.before.replica_cutpoint_digest = std::string(64U, '2');
    result.before.replica_evidence_set_digest = std::string(64U, '3');
    result.before.replica_visible_state_digest = std::string(64U, '4');
    result.after = result.before;

    require(
        !anonsync::sync_replica_sync_once_made_durable_progress(result),
        "identical combined cutpoints reported durable progress");

    ++result.after.replica_generation;
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "replica generation change did not report durable progress");

    result.after = result.before;
    ++result.after.catalog_entries;
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "catalog change did not report durable progress");

    result.after = result.before;
    ++result.after.local_scan_epoch;
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "authenticated scan-continuation change did not report durable progress");

    result.after = result.before;
    result.after.remote_apply_resume_after_path = "later/path.txt";
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "remote scheduling cursor change did not report durable progress");

    result.after = result.before;
    result.after.remote_inspection_sweep_basis_digest =
        std::string(64U, '5');
    result.after.remote_inspection_sweep_started_after_path = "origin.txt";
    result.after.remote_inspection_sweep_seen_path_count = 7U;
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "remote inspection-sweep continuation did not report durable progress");

    result.before = result.after;
    ++result.after.remote_inspection_sweep_seen_path_count;
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "remote inspection-sweep count change did not report durable progress");

    result.before = result.after;
    result.after.remote_inspection_sweep_started_after_path = "other.txt";
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "remote inspection-sweep origin change did not report durable progress");

    result.before = result.after;
    result.after.remote_inspection_sweep_had_unresolved_paths = true;
    require(
        anonsync::sync_replica_sync_once_made_durable_progress(result),
        "remote inspection-sweep unresolved-state change did not report durable progress");
}

void test_option_contract() {
    const anonsync::SyncReplicaSyncOnceOptions valid;
    anonsync::validate_sync_replica_sync_once_options_or_throw(
        valid, "sync-once test options");

    require_error(
        [&] {
            anonsync::validate_sync_replica_sync_once_options_or_throw(
                valid, "");
        },
        "label must not be empty",
        "empty options label was accepted");

    auto invalid = valid;
    invalid.stage_timeout_seconds = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_sync_once_options_or_throw(
                invalid, "zero stage timeout");
        },
        "stage_timeout_seconds",
        "zero stage timeout was accepted");

    invalid = valid;
    invalid.maximum_runtime_seconds = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_sync_once_options_or_throw(
                invalid, "zero command runtime");
        },
        "maximum_runtime_seconds",
        "zero command runtime was accepted");

    invalid = valid;
    invalid.max_round_trips = 0U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_sync_once_options_or_throw(
                invalid, "zero round trips");
        },
        "max_round_trips",
        "zero round trips were accepted");

    invalid = valid;
    invalid.max_round_trips =
        anonsync::kSyncReplicaReconciliationTlsMaximumRoundTrips + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_sync_once_options_or_throw(
                invalid, "excess round trips");
        },
        "max_round_trips",
        "excess round trips were accepted");

    invalid = valid;
    invalid.max_source_resets =
        anonsync::kSyncReplicaReconciliationTlsMaximumRoundTrips + 1U;
    require_error(
        [&] {
            anonsync::validate_sync_replica_sync_once_options_or_throw(
                invalid, "excess source resets");
        },
        "max_source_resets",
        "excess source resets were accepted");
}

void test_terminal_settlement_cutpoint_contract() {
    anonsync::SyncReplicaFolderConvergencePassReport pass;
    pass.completed_local_scan_epoch = true;
    pass.completed_remote_inspection_sweep = true;
    pass.remote_apply_stop_reason =
        anonsync::SyncReplicaFolderRemoteApplyStopReason::EndOfProjection;
    pass.remote_inspection_terminal_cutpoint_reproved = true;
    pass.remote_inspection_terminal_catalog_digest = std::string(64U, 'a');
    pass.remote_inspection_terminal_visible_state_digest =
        std::string(64U, 'b');

    anonsync::SyncReplicaSyncOnceCutpoint cutpoint;
    cutpoint.catalog_digest = pass.remote_inspection_terminal_catalog_digest;
    cutpoint.replica_visible_state_digest =
        pass.remote_inspection_terminal_visible_state_digest;

    require(
        anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            pass, cutpoint),
        "matching terminal cutpoint did not settle");

    auto changed_pass = pass;
    auto changed_cutpoint = cutpoint;
    changed_pass.remote_inspection_terminal_cutpoint_reproved = false;
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, cutpoint),
        "missing terminal reproof settled");

    changed_pass = pass;
    changed_pass.remote_inspection_terminal_catalog_digest =
        std::string(64U, 'c');
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, cutpoint),
        "stale terminal catalog digest settled");

    changed_pass = pass;
    changed_pass.remote_inspection_terminal_visible_state_digest =
        std::string(64U, 'd');
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, cutpoint),
        "stale terminal visible-state digest settled");

    changed_pass = pass;
    changed_pass.remote_apply_resume_after_path = "older-cursor.txt";
    changed_cutpoint = cutpoint;
    changed_cutpoint.remote_apply_resume_after_path = "newer-cursor.txt";
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, changed_cutpoint),
        "scheduling-only remote cursor movement settled");

    changed_pass = pass;
    changed_pass.completed_local_scan_epoch = false;
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, cutpoint),
        "incomplete local scan settled");

    changed_pass = pass;
    changed_pass.completed_remote_inspection_sweep = false;
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, cutpoint),
        "incomplete remote inspection settled");

    changed_pass = pass;
    changed_pass.deferred_remote_inspection_path_count = 1U;
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, cutpoint),
        "deferred remote inspection settled");

    changed_pass = pass;
    changed_pass.remote_apply_stop_reason =
        anonsync::SyncReplicaFolderRemoteApplyStopReason::
            AuthorityCutpointChanged;
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            changed_pass, cutpoint),
        "changed authority cutpoint settled");

    changed_cutpoint = cutpoint;
    changed_cutpoint.local_scan_seen_path_count = 1U;
    changed_cutpoint.local_scan_seen_path_bytes = 5U;
    changed_cutpoint.local_scan_resume_after_path = "a.txt";
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            pass, changed_cutpoint),
        "active local scan continuation settled");

    changed_cutpoint = cutpoint;
    changed_cutpoint.remote_inspection_sweep_basis_digest =
        std::string(64U, 'e');
    changed_cutpoint.remote_inspection_sweep_started_after_path = "a.txt";
    changed_cutpoint.remote_inspection_sweep_seen_path_count = 1U;
    require(
        !anonsync::sync_replica_sync_once_final_pass_settles_cutpoint(
            pass, changed_cutpoint),
        "active remote inspection continuation settled");
}

}  // namespace

int main() {
    try {
        test_disposition_contract();
        test_durable_progress_contract();
        test_option_contract();
        test_terminal_settlement_cutpoint_contract();
        std::cout << "sync replica sync-once checks passed: " << checks
                  << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica sync-once checks failed after " << checks
                  << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() {
    return 0;
}

#endif
