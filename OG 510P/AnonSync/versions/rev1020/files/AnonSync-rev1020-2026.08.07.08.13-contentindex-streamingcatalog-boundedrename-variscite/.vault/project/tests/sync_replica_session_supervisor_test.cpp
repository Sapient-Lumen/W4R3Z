#include "sync_replica_session_supervisor.hpp"

#include <array>
#include <chrono>
#include <cstdint>
#include <exception>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

namespace {

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;
using namespace std::chrono_literals;

static_assert(!std::is_copy_constructible_v<
              anonsync::SyncReplicaSessionSupervisor>);
static_assert(!std::is_move_constructible_v<
              anonsync::SyncReplicaSessionSupervisor>);

std::size_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_throws(Function&& function, std::string_view message) {
    ++checks;
    try {
        std::forward<Function>(function)();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(std::string(message));
}

[[nodiscard]] TimePoint at(std::chrono::seconds offset) {
    return TimePoint{} + offset;
}

void test_limit_validation() {
    anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
        {1U, 1U, std::nullopt}, "minimum limits");
    anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
        {anonsync::kSyncReplicaSessionSupervisorMaximumSessions,
         anonsync::kSyncReplicaSessionSupervisorMaximumStageTimeoutSeconds,
         anonsync::kSyncReplicaSessionSupervisorMaximumRuntimeSeconds},
        "maximum limits");

    require_throws(
        [] {
            anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
                {0U, 1U, std::nullopt}, "zero sessions");
        },
        "zero maximum session count must fail");
    require_throws(
        [] {
            anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
                {anonsync::kSyncReplicaSessionSupervisorMaximumSessions + 1U,
                 1U, std::nullopt},
                "too many sessions");
        },
        "oversized maximum session count must fail");
    require_throws(
        [] {
            anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
                {1U, 0U, std::nullopt}, "zero stage timeout");
        },
        "zero stage timeout must fail");
    require_throws(
        [] {
            anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
                {1U,
                 anonsync::
                     kSyncReplicaSessionSupervisorMaximumStageTimeoutSeconds +
                     1U,
                 std::nullopt},
                "oversized stage timeout");
        },
        "oversized stage timeout must fail");
    require_throws(
        [] {
            anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
                {1U, 1U, 0U}, "zero runtime");
        },
        "zero command runtime must fail");
    require_throws(
        [] {
            anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
                {1U, 1U,
                 anonsync::
                     kSyncReplicaSessionSupervisorMaximumRuntimeSeconds + 1U},
                "oversized runtime");
        },
        "oversized command runtime must fail");
    require_throws(
        [] {
            anonsync::validate_sync_replica_session_supervisor_limits_or_throw(
                {1U, 1U, std::nullopt}, "");
        },
        "empty validation label must fail");
    require_throws(
        [] {
            anonsync::SyncReplicaSessionSupervisor supervisor(
                {1U, 1U, std::nullopt}, at(0s), "");
            (void)supervisor;
        },
        "empty supervisor label must fail");
}

void test_claim_lease_covers_receipt_and_clock_authority() {
    require(
        anonsync::sync_replica_session_receipt_horizon_seconds_or_throw(10U) ==
            40U,
        "default receipt horizon must retain four staged timeout units");
    require(
        anonsync::minimum_sync_replica_session_claim_lease_seconds_or_throw(
            10U) == 661U,
        "default lease minimum omitted receipt, drift, uncertainty, or margin");
    require(
        anonsync::minimum_sync_replica_session_claim_lease_seconds_or_throw(
            3600U) == 15021U,
        "maximum timeout produced the wrong durable lease horizon");

    anonsync::SyncReplicaOutboxClockPolicy narrow;
    narrow.max_uncertainty_ns = 1500000000ULL;
    narrow.max_forward_step_seconds = 7U;
    narrow.max_realtime_lag_seconds = 9U;
    require(
        anonsync::minimum_sync_replica_session_claim_lease_seconds_or_throw(
            2U, narrow) == 31U,
        "custom lease minimum omitted lag catch-up or four uncertainties");

    anonsync::SyncReplicaOutboxClockPolicy components;
    components.max_uncertainty_ns = 1000000000ULL;
    components.max_forward_step_seconds = 2U;
    components.max_realtime_lag_seconds = 3U;
    require(
        anonsync::minimum_sync_replica_session_claim_lease_seconds_or_throw(
            1U, components) == 14U,
        "lease minimum did not bind every clock-policy component");
    components.max_realtime_lag_seconds = 4U;
    require(
        anonsync::minimum_sync_replica_session_claim_lease_seconds_or_throw(
            1U, components) == 15U,
        "lease minimum ignored legal realtime catch-up");
    components.max_realtime_lag_seconds = 3U;
    components.max_uncertainty_ns = 1250000000ULL;
    require(
        anonsync::minimum_sync_replica_session_claim_lease_seconds_or_throw(
            1U, components) == 15U,
        "lease minimum did not ceil four uncertainty allowances together");

    anonsync::validate_sync_replica_session_claim_lease_seconds_or_throw(
        661U, 10U);
    require_throws(
        [] {
            anonsync::
                validate_sync_replica_session_claim_lease_seconds_or_throw(
                    660U, 10U);
        },
        "one-second-short lease must fail closed");
    require_throws(
        [] {
            anonsync::
                validate_sync_replica_session_claim_lease_seconds_or_throw(
                    0U, 10U);
        },
        "zero lease must fail closed");
    require_throws(
        [] {
            anonsync::
                validate_sync_replica_session_claim_lease_seconds_or_throw(
                    86401U, 10U);
        },
        "lease beyond the durable lifetime budget must fail closed");
    require_throws(
        [] {
            (void)anonsync::
                sync_replica_session_receipt_horizon_seconds_or_throw(0U);
        },
        "zero timeout must not mint a receipt horizon");
    require_throws(
        [] {
            anonsync::SyncReplicaOutboxClockPolicy invalid;
            invalid.max_uncertainty_ns = 0U;
            (void)anonsync::
                minimum_sync_replica_session_claim_lease_seconds_or_throw(
                    10U, invalid);
        },
        "invalid durable clock policy must not mint a lease minimum");
}

void test_uncapped_staged_deadlines_and_maximum_sessions() {
    anonsync::SyncReplicaSessionSupervisor supervisor(
        {2U, 3U, std::nullopt}, at(10s), "uncapped");
    require(
        !supervisor.command_deadline().has_value() &&
            supervisor.sessions_authorized() == 0U,
        "uncapped supervisor must begin without command cutpoint or sessions");

    const auto first = supervisor.authorize_next_at_or_throw(at(11s));
    require(
        first.disposition == anonsync::
            SyncReplicaSessionAuthorizationDisposition::Authorized &&
            first.plan.has_value(),
        "first uncapped session must be authorized");
    const auto& plan = *first.plan;
    require(plan.session_index == 1U, "first session index must be one");
    require(
        plan.deadline(anonsync::SyncReplicaSessionStage::First) == at(14s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Second) ==
                at(17s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Third) == at(20s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Fourth) ==
                at(23s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Fifth) == at(26s),
        "uncapped session must receive five fresh staged deadlines");
    require(
        !plan.command_limits(anonsync::SyncReplicaSessionStage::First) &&
            !plan.command_limits(anonsync::SyncReplicaSessionStage::Fifth),
        "uncapped staged deadlines must not claim command limitation");
    const auto client = plan.client_deadlines();
    const auto server = plan.server_deadlines();
    require(
        client.connect == at(14s) && client.handshake == at(17s) &&
            client.request == at(20s) && client.receipt == at(23s) &&
            client.shutdown == at(26s),
        "client deadline projection must preserve every stage");
    require(
        server.accept == at(14s) && server.handshake == at(17s) &&
            server.request == at(20s) && server.receipt == at(23s) &&
            server.shutdown == at(26s),
        "server deadline projection must preserve every stage");

    const auto second = supervisor.authorize_next_at_or_throw(at(30s));
    require(
        second.disposition == anonsync::
            SyncReplicaSessionAuthorizationDisposition::Authorized &&
            second.plan.has_value() && second.plan->session_index == 2U &&
            second.plan->deadline(anonsync::SyncReplicaSessionStage::First) ==
                at(33s),
        "later session must receive deadlines anchored to its own admission");
    const auto exhausted = supervisor.authorize_next_at_or_throw(at(31s));
    require(
        exhausted.disposition == anonsync::
            SyncReplicaSessionAuthorizationDisposition::MaximumSessionsReached &&
            !exhausted.plan.has_value() &&
            supervisor.sessions_authorized() == 2U,
        "session count bound must terminalize without another plan");
}

void test_command_deadline_clamping_and_admission() {
    anonsync::SyncReplicaSessionSupervisor supervisor(
        {5U, 2U, 7U}, at(100s), "capped");
    require(
        supervisor.command_deadline() == at(107s) &&
            !supervisor.command_deadline_reached_at(at(106s)) &&
            supervisor.command_deadline_reached_at(at(107s)),
        "command cutpoint must be one absolute steady-clock deadline");

    const auto first = supervisor.authorize_next_at_or_throw(at(101s));
    require(first.plan.has_value(), "capped first session must have plan");
    const auto& plan = *first.plan;
    require(
        plan.deadline(anonsync::SyncReplicaSessionStage::First) == at(103s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Second) ==
                at(105s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Third) == at(107s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Fourth) ==
                at(107s) &&
            plan.deadline(anonsync::SyncReplicaSessionStage::Fifth) == at(107s),
        "command cutpoint must clamp all naturally later stage deadlines");
    require(
        !plan.command_limits(anonsync::SyncReplicaSessionStage::First) &&
            !plan.command_limits(anonsync::SyncReplicaSessionStage::Second) &&
            plan.command_limits(anonsync::SyncReplicaSessionStage::Third) &&
            plan.command_limits(anonsync::SyncReplicaSessionStage::Fifth),
        "deadline plan must identify stages bounded by the command cutpoint");

    const auto second = supervisor.authorize_next_at_or_throw(at(106s));
    require(
        second.disposition == anonsync::
            SyncReplicaSessionAuthorizationDisposition::Authorized &&
            second.plan.has_value() && second.plan->session_index == 2U,
        "a session may begin strictly before the command cutpoint");
    require(
        second.plan->deadline(anonsync::SyncReplicaSessionStage::First) ==
                at(107s) &&
            second.plan->command_limits(
                anonsync::SyncReplicaSessionStage::First),
        "late session's first operation must still be clamped");

    const auto expired = supervisor.authorize_next_at_or_throw(at(107s));
    require(
        expired.disposition == anonsync::
            SyncReplicaSessionAuthorizationDisposition::CommandDeadlineReached &&
            !expired.plan.has_value() && supervisor.sessions_authorized() == 2U,
        "command cutpoint must deny a later session without consuming count");

    require_throws(
        [] {
            anonsync::SyncReplicaSessionSupervisor invalid_observation(
                {1U, 1U, 1U}, at(50s), "backward observation");
            (void)invalid_observation.authorize_next_at_or_throw(at(49s));
        },
        "observation before supervisor start must fail");
}

[[nodiscard]] anonsync::SyncReplicaFileTlsClientResult client_result(
    anonsync::SyncReplicaFileTlsClientDisposition disposition,
    std::optional<anonsync::SyncReplicaFileDeliveryReceiptApplyResult> apply =
        std::nullopt) {
    anonsync::SyncReplicaFileTlsClientResult result;
    result.disposition = disposition;
    result.receipt_apply_result = apply;
    return result;
}

void test_send_terminal_policy() {
    using Apply = anonsync::SyncReplicaFileDeliveryReceiptApplyResult;
    using Disposition = anonsync::SyncReplicaFileTlsClientDisposition;
    using Stop = anonsync::SyncReplicaSendSupervisorStopReason;

    const auto settled = client_result(Disposition::ReceiptApplied,
                                       Apply::EffectSettled);
    require(
        anonsync::sync_replica_send_session_effect_is_settled(settled) &&
            !anonsync::sync_replica_send_session_receiver_deferred(settled) &&
            !anonsync::sync_replica_send_supervisor_stop_after(settled)
                 .has_value(),
        "settled receipt must authorize only the caller's next bounded session");

    constexpr std::array receiver_deferrals{
        Apply::ReceiverEffectCapacityBlocked,
        Apply::ReceiverEffectPathBlocked,
        Apply::ReceiverEvidenceCapacityBlocked,
        Apply::ReceiverEvidencePending,
        Apply::ReceiverEvidenceQuarantined,
        Apply::ReceiverProjectionBlocked,
        Apply::ReceiverDestinationConflict,
    };
    for (const Apply apply : receiver_deferrals) {
        const auto deferred = client_result(Disposition::ReceiptApplied, apply);
        require(
            anonsync::sync_replica_send_session_receiver_deferred(deferred) &&
                anonsync::sync_replica_send_supervisor_stop_after(deferred) ==
                    Stop::ReceiverDeferred,
            "every authenticated receiver deferral must stop as bounded progress");
    }

    constexpr std::array local_conflicts{
        Apply::IntentMissing,
        Apply::StaleClaim,
        Apply::ExpiredClaim,
    };
    for (const Apply apply : local_conflicts) {
        const auto conflict = client_result(Disposition::ReceiptApplied, apply);
        require(
            !anonsync::sync_replica_send_session_receiver_deferred(conflict) &&
                anonsync::sync_replica_send_supervisor_stop_after(conflict) ==
                    Stop::ReceiptApplyConflict,
            "local receipt-apply conflicts must not be laundered into deferral");
    }

    require(
        anonsync::sync_replica_send_supervisor_stop_after(
            client_result(Disposition::NoReadyDelivery)) ==
            Stop::NoReadyDelivery,
        "authenticated no-ready session must stop without failure");
    require(
        anonsync::sync_replica_send_supervisor_stop_after(
            client_result(Disposition::PeerClosed)) == Stop::SessionFailed,
        "ambiguous peer close must remain a failed sender session");

    auto dispatch_deadline =
        client_result(Disposition::DispatchDeadlineExpired);
    dispatch_deadline.socket_created = true;
    dispatch_deadline.socket_policy_verified = true;
    dispatch_deadline.connected = true;
    dispatch_deadline.handshake_complete = true;
    dispatch_deadline.peer_authenticated = true;
    dispatch_deadline.peer_spki_sha256 = std::string(64U, 'b');
    dispatch_deadline.peer_actor =
        anonsync::SyncReplicaActor{"peer-device", 2U};
    require(
        anonsync::
            sync_replica_send_session_is_authenticated_dispatch_deadline_clean(
                dispatch_deadline) &&
            anonsync::sync_replica_send_supervisor_stop_after(
                dispatch_deadline) == Stop::SessionFailed,
        "clean post-authentication dispatch expiry must be identifiable without "
        "becoming success absent an outer command cutpoint");

    auto dispatch_with_claim = dispatch_deadline;
    dispatch_with_claim.claim_id = "claim-id";
    require(
        !anonsync::
            sync_replica_send_session_is_authenticated_dispatch_deadline_clean(
                dispatch_with_claim),
        "dispatch expiry with claim identity must remain ambiguous");
    auto dispatch_with_bytes = dispatch_deadline;
    dispatch_with_bytes.request_prefix_bytes_written = 1U;
    require(
        !anonsync::
            sync_replica_send_session_is_authenticated_dispatch_deadline_clean(
                dispatch_with_bytes),
        "dispatch expiry with application bytes must remain ambiguous");
    auto dispatch_without_auth = dispatch_deadline;
    dispatch_without_auth.peer_authenticated = false;
    require(
        !anonsync::
            sync_replica_send_session_is_authenticated_dispatch_deadline_clean(
                dispatch_without_auth),
        "dispatch expiry without authenticated peer authority must not be clean");

    constexpr std::array success_stops{
        Stop::MaximumSessionsReached,
        Stop::CommandDeadlineReached,
        Stop::NoReadyDelivery,
        Stop::ReceiverDeferred,
    };
    for (const Stop stop : success_stops) {
        require(
            anonsync::sync_replica_send_supervisor_stop_is_success(stop),
            "bounded sender progress stop must be successful");
    }
    require(
        !anonsync::sync_replica_send_supervisor_stop_is_success(
            Stop::ReceiptApplyConflict) &&
            !anonsync::sync_replica_send_supervisor_stop_is_success(
                Stop::SessionFailed),
        "sender conflicts and session failures must remain unsuccessful");
    require(
        anonsync::sync_replica_send_supervisor_stop_reason_name(
            Stop::CommandDeadlineReached) == "command_deadline_reached" &&
            anonsync::sync_replica_send_supervisor_stop_reason_name(
                Stop::ReceiverDeferred) == "receiver_deferred",
        "sender stop names must be stable presentation values");
}

[[nodiscard]] anonsync::SyncReplicaFileTlsServerResult idle_server_result() {
    anonsync::SyncReplicaFileTlsServerResult result;
    result.disposition = anonsync::SyncReplicaFileTlsServerDisposition::PeerClosed;
    result.accepted = true;
    result.accepted_socket_policy_verified = true;
    result.handshake_complete = true;
    result.peer_spki_sha256 = std::string(64U, 'a');
    result.peer_actor = anonsync::SyncReplicaActor{"peer-device", 1U};
    result.receive.emplace();
    result.receive->disposition =
        anonsync::SyncReplicaFileTlsReceiveDisposition::PeerClosed;
    return result;
}

void test_serve_terminal_policy_and_exact_idle_predicate() {
    using Disposition = anonsync::SyncReplicaFileTlsServerDisposition;
    using Stop = anonsync::SyncReplicaServeSupervisorStopReason;

    const auto idle = idle_server_result();
    require(
        anonsync::sync_replica_serve_session_is_authenticated_peer_closed_idle(
            idle) &&
            anonsync::sync_replica_serve_supervisor_stop_after(idle) ==
                Stop::AuthenticatedPeerClosedIdle,
        "exact zero-application-byte authenticated close must be bounded idle");

    auto partial_prefix = idle;
    partial_prefix.receive->request_prefix_bytes_received = 1U;
    require(
        !anonsync::sync_replica_serve_session_is_authenticated_peer_closed_idle(
            partial_prefix) &&
            anonsync::sync_replica_serve_supervisor_stop_after(partial_prefix) ==
                Stop::SessionFailed,
        "partial request prefix close must remain transport ambiguity");
    auto complete_frame = idle;
    complete_frame.receive->request_frame_bytes = 1U;
    require(
        !anonsync::sync_replica_serve_session_is_authenticated_peer_closed_idle(
            complete_frame),
        "observed request frame must not be called idle");
    auto inbound = idle;
    inbound.receive->inbound.emplace();
    require(
        !anonsync::sync_replica_serve_session_is_authenticated_peer_closed_idle(
            inbound),
        "durable inbound decision must not be called idle");
    auto receipt_started = idle;
    receipt_started.receive->receipt_write_started = true;
    require(
        !anonsync::sync_replica_serve_session_is_authenticated_peer_closed_idle(
            receipt_started),
        "receipt write frontier must not be called idle");
    auto unauthenticated = idle;
    unauthenticated.peer_actor.reset();
    require(
        !anonsync::sync_replica_serve_session_is_authenticated_peer_closed_idle(
            unauthenticated),
        "peer identity evidence is required for authenticated idle");

    anonsync::SyncReplicaFileTlsServerResult receipt;
    receipt.disposition = Disposition::ReceiptSent;
    require(
        !anonsync::sync_replica_serve_supervisor_stop_after(receipt).has_value(),
        "completed receipt must permit only a later bounded receive session");
    anonsync::SyncReplicaFileTlsServerResult accept_expired;
    accept_expired.disposition = Disposition::AcceptDeadlineExpired;
    require(
        anonsync::sync_replica_serve_supervisor_stop_after(accept_expired) ==
            Stop::AcceptDeadlineExpired,
        "ordinary accept deadline must remain distinct from command cutpoint");
    anonsync::SyncReplicaFileTlsServerResult request_expired;
    request_expired.disposition = Disposition::RequestDeadlineExpired;
    require(
        anonsync::sync_replica_serve_supervisor_stop_after(request_expired) ==
            Stop::SessionFailed,
        "partial/ambiguous receiver session timeout must remain failure");

    constexpr std::array success_stops{
        Stop::MaximumSessionsReached,
        Stop::CommandDeadlineReached,
        Stop::AcceptDeadlineExpired,
        Stop::AuthenticatedPeerClosedIdle,
    };
    for (const Stop stop : success_stops) {
        require(
            anonsync::sync_replica_serve_supervisor_stop_is_success(stop),
            "bounded receiver progress stop must be successful");
    }
    require(
        !anonsync::sync_replica_serve_supervisor_stop_is_success(
            Stop::SessionFailed),
        "receiver session failure must remain unsuccessful");
    require(
        anonsync::sync_replica_serve_supervisor_stop_reason_name(
            Stop::AuthenticatedPeerClosedIdle) ==
                "authenticated_peer_closed_idle" &&
            anonsync::sync_replica_serve_supervisor_stop_reason_name(
                Stop::CommandDeadlineReached) == "command_deadline_reached",
        "receiver stop names must be stable presentation values");
}

}  // namespace

int main() {
    try {
        test_limit_validation();
        test_claim_lease_covers_receipt_and_clock_authority();
        test_uncapped_staged_deadlines_and_maximum_sessions();
        test_command_deadline_clamping_and_admission();
        test_send_terminal_policy();
        test_serve_terminal_policy_and_exact_idle_predicate();
        std::cout << "sync replica session supervisor checks passed: "
                  << checks << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica session supervisor test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}
