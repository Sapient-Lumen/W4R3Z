#include "sync_replica_session_supervisor.hpp"

#include "sync_replica_outbox_lease.hpp"

#include <chrono>
#include <limits>
#include <stdexcept>
#include <utility>

namespace anonsync {
namespace {

using Clock = std::chrono::steady_clock;
using TimePoint = Clock::time_point;
using Duration = Clock::duration;

[[nodiscard]] Duration seconds_duration_or_throw(
    std::uint64_t seconds,
    const std::string& label) {
    if (seconds > static_cast<std::uint64_t>(
                      std::numeric_limits<std::int64_t>::max())) {
        throw std::overflow_error(label + " seconds exceed int64_t");
    }
    const auto value = std::chrono::seconds(
        static_cast<std::int64_t>(seconds));
    const Duration converted =
        std::chrono::duration_cast<Duration>(value);
    if (converted <= Duration::zero()) {
        throw std::overflow_error(
            label + " cannot be represented by steady_clock");
    }
    return converted;
}

[[nodiscard]] TimePoint checked_add_or_throw(
    TimePoint base,
    Duration delta,
    const std::string& label) {
    if (delta < Duration::zero() ||
        base > TimePoint::max() - delta) {
        throw std::overflow_error(label + " deadline overflows steady_clock");
    }
    return base + delta;
}

[[nodiscard]] std::size_t stage_index(
    SyncReplicaSessionStage stage) noexcept {
    return static_cast<std::size_t>(stage);
}

[[nodiscard]] std::uint64_t checked_multiply_u64_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right != 0U &&
        left > std::numeric_limits<std::uint64_t>::max() / right) {
        throw std::overflow_error(label + " multiplication overflows");
    }
    return left * right;
}

[[nodiscard]] std::uint64_t checked_add_u64_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (left > std::numeric_limits<std::uint64_t>::max() - right) {
        throw std::overflow_error(label + " addition overflows");
    }
    return left + right;
}

[[nodiscard]] std::uint64_t ceiling_divide_u64_or_throw(
    std::uint64_t numerator,
    std::uint64_t denominator,
    const std::string& label) {
    if (denominator == 0U) {
        throw std::logic_error(label + " divisor is zero");
    }
    return numerator == 0U ? 0U : 1U + ((numerator - 1U) / denominator);
}

void validate_stage_timeout_or_throw(
    std::uint64_t stage_timeout_seconds,
    const std::string& label) {
    if (stage_timeout_seconds == 0U ||
        stage_timeout_seconds >
            kSyncReplicaSessionSupervisorMaximumStageTimeoutSeconds) {
        throw std::invalid_argument(
            label + " stage_timeout_seconds must be in 1..3600");
    }
}

}  // namespace

void validate_sync_replica_session_supervisor_limits_or_throw(
    const SyncReplicaSessionSupervisorLimits& limits,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica session supervisor limits label is empty");
    }
    if (limits.maximum_sessions == 0U ||
        limits.maximum_sessions >
            kSyncReplicaSessionSupervisorMaximumSessions) {
        throw std::invalid_argument(
            label + " maximum_sessions must be in 1..256");
    }
    validate_stage_timeout_or_throw(
        limits.stage_timeout_seconds, label);
    if (limits.maximum_runtime_seconds.has_value() &&
        (*limits.maximum_runtime_seconds == 0U ||
         *limits.maximum_runtime_seconds >
             kSyncReplicaSessionSupervisorMaximumRuntimeSeconds)) {
        throw std::invalid_argument(
            label + " maximum_runtime_seconds must be in 1..86400");
    }
}

std::uint64_t sync_replica_session_receipt_horizon_seconds_or_throw(
    std::uint64_t stage_timeout_seconds,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica session receipt horizon label is empty");
    }
    validate_stage_timeout_or_throw(stage_timeout_seconds, label);
    return checked_multiply_u64_or_throw(
        stage_timeout_seconds,
        kSyncReplicaSessionSupervisorReceiptStageOrdinal,
        label + " receipt horizon");
}

std::uint64_t minimum_sync_replica_session_claim_lease_seconds_or_throw(
    std::uint64_t stage_timeout_seconds,
    const SyncReplicaOutboxClockPolicy& clock_policy,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica session claim lease label is empty");
    }
    validate_sync_replica_outbox_clock_policy_or_throw(
        clock_policy, label + " clock policy");

    std::uint64_t minimum =
        sync_replica_session_receipt_horizon_seconds_or_throw(
            stage_timeout_seconds, label);
    minimum = checked_add_u64_or_throw(
        minimum, clock_policy.max_forward_step_seconds,
        label + " accepted forward step");
    // Both claim and receipt observations are accepted against one older
    // cumulative anchor. Combining the receipt-side forward bound with the
    // claim-side realtime-lag bound permits legal catch-up of lag already
    // present at claim and contributes two anchor plus two endpoint
    // uncertainty allowances.
    minimum = checked_add_u64_or_throw(
        minimum, clock_policy.max_realtime_lag_seconds,
        label + " accepted realtime catch-up");
    const std::uint64_t uncertainty_fourfold_ns =
        checked_multiply_u64_or_throw(
            clock_policy.max_uncertainty_ns, 4U,
            label + " anchor and endpoint uncertainty");
    minimum = checked_add_u64_or_throw(
        minimum,
        ceiling_divide_u64_or_throw(
            uncertainty_fourfold_ns, kSyncReplicaNanosecondsPerSecond,
            label + " anchor and endpoint uncertainty"),
        label + " anchor and endpoint uncertainty");
    // Durable epochs are floor-converted integer seconds and expiry is
    // exclusive. One final second keeps the latest permitted receipt strictly
    // before the stored expiry even at an exact continuous-time boundary.
    minimum = checked_add_u64_or_throw(
        minimum, 1U, label + " exclusive expiry margin");
    if (minimum > kSyncReplicaOutboxMaxLeaseSeconds) {
        throw std::invalid_argument(
            label + " minimum exceeds durable outbox lease maximum");
    }
    return minimum;
}

void validate_sync_replica_session_claim_lease_seconds_or_throw(
    std::uint64_t lease_seconds,
    std::uint64_t stage_timeout_seconds,
    const SyncReplicaOutboxClockPolicy& clock_policy,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica session claim lease label is empty");
    }
    if (lease_seconds == 0U ||
        lease_seconds > kSyncReplicaOutboxMaxLeaseSeconds) {
        throw std::invalid_argument(label + " must be in 1..86400");
    }
    const std::uint64_t minimum =
        minimum_sync_replica_session_claim_lease_seconds_or_throw(
            stage_timeout_seconds, clock_policy, label);
    if (lease_seconds < minimum) {
        throw std::invalid_argument(
            label + " must be at least " + std::to_string(minimum) +
            " seconds for the configured receipt and clock horizon");
    }
}

std::chrono::steady_clock::time_point
SyncReplicaSessionDeadlinePlan::deadline(
    SyncReplicaSessionStage stage) const noexcept {
    return stages[stage_index(stage)];
}

bool SyncReplicaSessionDeadlinePlan::command_limits(
    SyncReplicaSessionStage stage) const noexcept {
    return command_deadline.has_value() &&
           deadline(stage) == *command_deadline;
}

SyncReplicaFileTlsClientDeadlines
SyncReplicaSessionDeadlinePlan::client_deadlines() const noexcept {
    return {
        deadline(SyncReplicaSessionStage::First),
        deadline(SyncReplicaSessionStage::Second),
        deadline(SyncReplicaSessionStage::Third),
        deadline(SyncReplicaSessionStage::Fourth),
        deadline(SyncReplicaSessionStage::Fifth),
    };
}

SyncReplicaFileTlsServerDeadlines
SyncReplicaSessionDeadlinePlan::server_deadlines() const noexcept {
    return {
        deadline(SyncReplicaSessionStage::First),
        deadline(SyncReplicaSessionStage::Second),
        deadline(SyncReplicaSessionStage::Third),
        deadline(SyncReplicaSessionStage::Fourth),
        deadline(SyncReplicaSessionStage::Fifth),
    };
}

SyncReplicaSessionSupervisor::SyncReplicaSessionSupervisor(
    SyncReplicaSessionSupervisorLimits limits,
    std::chrono::steady_clock::time_point started_at,
    std::string label)
    : limits_(std::move(limits)),
      started_at_(started_at),
      label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica session supervisor label is empty");
    }
    validate_sync_replica_session_supervisor_limits_or_throw(
        limits_, label_ + " limits");
    if (limits_.maximum_runtime_seconds.has_value()) {
        command_deadline_ = checked_add_or_throw(
            started_at_,
            seconds_duration_or_throw(
                *limits_.maximum_runtime_seconds,
                label_ + " command runtime"),
            label_ + " command");
    }
}

SyncReplicaSessionAuthorization
SyncReplicaSessionSupervisor::authorize_next_or_throw() {
    return authorize_next_at_or_throw(Clock::now());
}

SyncReplicaSessionAuthorization
SyncReplicaSessionSupervisor::authorize_next_at_or_throw(
    std::chrono::steady_clock::time_point observed_at) {
    if (observed_at < started_at_) {
        throw std::invalid_argument(
            label_ + " observation precedes supervisor start");
    }
    if (sessions_authorized_ >= limits_.maximum_sessions) {
        return {
            SyncReplicaSessionAuthorizationDisposition::MaximumSessionsReached,
            std::nullopt,
        };
    }
    if (command_deadline_reached_at(observed_at)) {
        return {
            SyncReplicaSessionAuthorizationDisposition::CommandDeadlineReached,
            std::nullopt,
        };
    }

    const Duration stage = seconds_duration_or_throw(
        limits_.stage_timeout_seconds, label_ + " stage timeout");
    SyncReplicaSessionDeadlinePlan plan;
    plan.session_index = sessions_authorized_ + 1U;
    plan.command_deadline = command_deadline_;
    for (std::size_t index = 0U; index < plan.stages.size(); ++index) {
        const std::uint64_t multiplier =
            static_cast<std::uint64_t>(index + 1U);
        if (multiplier > static_cast<std::uint64_t>(
                             std::numeric_limits<Duration::rep>::max()) ||
            stage.count() >
                std::numeric_limits<Duration::rep>::max() /
                    static_cast<Duration::rep>(multiplier)) {
            throw std::overflow_error(
                label_ + " staged deadline duration overflows steady_clock");
        }
        const Duration staged = stage *
            static_cast<Duration::rep>(multiplier);
        const TimePoint natural = checked_add_or_throw(
            observed_at, staged, label_ + " staged session");
        plan.stages[index] = command_deadline_.has_value() &&
                natural >= *command_deadline_
            ? *command_deadline_
            : natural;
    }
    ++sessions_authorized_;
    return {
        SyncReplicaSessionAuthorizationDisposition::Authorized,
        std::move(plan),
    };
}

bool SyncReplicaSessionSupervisor::command_deadline_reached_at(
    std::chrono::steady_clock::time_point observed_at) const noexcept {
    return command_deadline_.has_value() &&
           observed_at >= *command_deadline_;
}

std::string_view sync_replica_send_supervisor_stop_reason_name(
    SyncReplicaSendSupervisorStopReason reason) noexcept {
    switch (reason) {
        case SyncReplicaSendSupervisorStopReason::MaximumSessionsReached:
            return "max_sessions_reached";
        case SyncReplicaSendSupervisorStopReason::CommandDeadlineReached:
            return "command_deadline_reached";
        case SyncReplicaSendSupervisorStopReason::NoReadyDelivery:
            return "no_ready_delivery";
        case SyncReplicaSendSupervisorStopReason::ReceiverDeferred:
            return "receiver_deferred";
        case SyncReplicaSendSupervisorStopReason::ReceiptApplyConflict:
            return "receipt_apply_conflict";
        case SyncReplicaSendSupervisorStopReason::SessionFailed:
            return "session_failed";
    }
    return "unknown";
}

bool sync_replica_send_supervisor_stop_is_success(
    SyncReplicaSendSupervisorStopReason reason) noexcept {
    return reason ==
               SyncReplicaSendSupervisorStopReason::MaximumSessionsReached ||
           reason ==
               SyncReplicaSendSupervisorStopReason::CommandDeadlineReached ||
           reason == SyncReplicaSendSupervisorStopReason::NoReadyDelivery ||
           reason == SyncReplicaSendSupervisorStopReason::ReceiverDeferred;
}

bool sync_replica_send_session_effect_is_settled(
    const SyncReplicaFileTlsClientResult& result) noexcept {
    return result.disposition ==
               SyncReplicaFileTlsClientDisposition::ReceiptApplied &&
           result.receipt_apply_result ==
               SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled;
}

bool sync_replica_send_session_receiver_deferred(
    const SyncReplicaFileTlsClientResult& result) noexcept {
    using Result = SyncReplicaFileDeliveryReceiptApplyResult;
    if (result.disposition !=
        SyncReplicaFileTlsClientDisposition::ReceiptApplied) {
        return false;
    }
    return result.receipt_apply_result ==
               Result::ReceiverEffectCapacityBlocked ||
           result.receipt_apply_result == Result::ReceiverEffectPathBlocked ||
           result.receipt_apply_result ==
               Result::ReceiverEvidenceCapacityBlocked ||
           result.receipt_apply_result == Result::ReceiverEvidencePending ||
           result.receipt_apply_result ==
               Result::ReceiverEvidenceQuarantined ||
           result.receipt_apply_result == Result::ReceiverProjectionBlocked ||
           result.receipt_apply_result ==
               Result::ReceiverDestinationConflict;
}

bool sync_replica_send_session_is_authenticated_dispatch_deadline_clean(
    const SyncReplicaFileTlsClientResult& result) noexcept {
    return result.disposition ==
               SyncReplicaFileTlsClientDisposition::DispatchDeadlineExpired &&
           result.socket_created && result.socket_policy_verified &&
           result.connected && result.handshake_complete &&
           result.peer_authenticated && result.peer_spki_sha256.has_value() &&
           result.peer_actor.has_value() && !result.operation_id.has_value() &&
           !result.claim_id.has_value() && !result.request_digest.has_value() &&
           result.request_prefix_bytes_written == 0U &&
           result.request_frame_bytes == 0U &&
           result.request_body_bytes_written == 0U &&
           result.receipt_prefix_bytes_received == 0U &&
           result.receipt_frame_bytes == 0U &&
           result.receipt_body_bytes_received == 0U &&
           !result.receipt_apply_result.has_value();
}

std::optional<SyncReplicaSendSupervisorStopReason>
sync_replica_send_supervisor_stop_after(
    const SyncReplicaFileTlsClientResult& result) noexcept {
    if (result.disposition ==
        SyncReplicaFileTlsClientDisposition::NoReadyDelivery) {
        return SyncReplicaSendSupervisorStopReason::NoReadyDelivery;
    }
    if (result.disposition !=
        SyncReplicaFileTlsClientDisposition::ReceiptApplied) {
        return SyncReplicaSendSupervisorStopReason::SessionFailed;
    }
    if (sync_replica_send_session_effect_is_settled(result)) {
        return std::nullopt;
    }
    if (sync_replica_send_session_receiver_deferred(result)) {
        return SyncReplicaSendSupervisorStopReason::ReceiverDeferred;
    }
    return SyncReplicaSendSupervisorStopReason::ReceiptApplyConflict;
}

std::string_view sync_replica_serve_supervisor_stop_reason_name(
    SyncReplicaServeSupervisorStopReason reason) noexcept {
    switch (reason) {
        case SyncReplicaServeSupervisorStopReason::MaximumSessionsReached:
            return "max_sessions_reached";
        case SyncReplicaServeSupervisorStopReason::CommandDeadlineReached:
            return "command_deadline_reached";
        case SyncReplicaServeSupervisorStopReason::AcceptDeadlineExpired:
            return "accept_deadline_expired";
        case SyncReplicaServeSupervisorStopReason::AuthenticatedPeerClosedIdle:
            return "authenticated_peer_closed_idle";
        case SyncReplicaServeSupervisorStopReason::SessionFailed:
            return "session_failed";
    }
    return "unknown";
}

bool sync_replica_serve_supervisor_stop_is_success(
    SyncReplicaServeSupervisorStopReason reason) noexcept {
    return reason ==
               SyncReplicaServeSupervisorStopReason::MaximumSessionsReached ||
           reason ==
               SyncReplicaServeSupervisorStopReason::CommandDeadlineReached ||
           reason ==
               SyncReplicaServeSupervisorStopReason::AcceptDeadlineExpired ||
           reason == SyncReplicaServeSupervisorStopReason::
                         AuthenticatedPeerClosedIdle;
}

bool sync_replica_serve_session_is_authenticated_peer_closed_idle(
    const SyncReplicaFileTlsServerResult& result) noexcept {
    if (result.disposition != SyncReplicaFileTlsServerDisposition::PeerClosed ||
        !result.accepted || !result.accepted_socket_policy_verified ||
        !result.handshake_complete || !result.peer_actor.has_value() ||
        !result.peer_spki_sha256.has_value() || !result.receive.has_value()) {
        return false;
    }
    const SyncReplicaFileTlsReceiveResult& receive = *result.receive;
    return receive.disposition ==
               SyncReplicaFileTlsReceiveDisposition::PeerClosed &&
           !receive.inbound.has_value() &&
           receive.request_prefix_bytes_received == 0U &&
           receive.request_frame_bytes == 0U &&
           receive.request_body_bytes_received == 0U &&
           !receive.receipt_write_started &&
           receive.receipt_prefix_bytes_written == 0U &&
           !receive.receipt_prefix_accepted &&
           receive.receipt_frame_bytes == 0U &&
           receive.receipt_body_bytes_written == 0U;
}

std::optional<SyncReplicaServeSupervisorStopReason>
sync_replica_serve_supervisor_stop_after(
    const SyncReplicaFileTlsServerResult& result) noexcept {
    if (result.disposition ==
        SyncReplicaFileTlsServerDisposition::ReceiptSent) {
        return std::nullopt;
    }
    if (result.disposition ==
        SyncReplicaFileTlsServerDisposition::AcceptDeadlineExpired) {
        return SyncReplicaServeSupervisorStopReason::AcceptDeadlineExpired;
    }
    if (sync_replica_serve_session_is_authenticated_peer_closed_idle(result)) {
        return SyncReplicaServeSupervisorStopReason::AuthenticatedPeerClosedIdle;
    }
    return SyncReplicaServeSupervisorStopReason::SessionFailed;
}


bool sync_replica_serve_session_is_authenticated_peer_closed_idle(
    const SyncReplicaPeerTlsServerResult& result) noexcept {
    if (result.disposition !=
            SyncReplicaPeerTlsServerDisposition::ApplicationServed ||
        !result.accepted || !result.accepted_socket_policy_verified ||
        !result.handshake_complete || !result.peer_actor.has_value() ||
        !result.peer_spki_sha256.has_value() ||
        !result.application.has_value()) {
        return false;
    }
    const SyncReplicaPeerTlsServeResult& application = *result.application;
    return application.disposition ==
               SyncReplicaPeerTlsServeDisposition::PeerClosed &&
           application.first_request_prefix_bytes_received == 0U &&
           application.first_request_frame_bytes == 0U &&
           application.first_request_body_bytes_received == 0U &&
           !application.file_delivery.has_value() &&
           !application.reconciliation.has_value();
}

std::optional<SyncReplicaServeSupervisorStopReason>
sync_replica_serve_supervisor_stop_after(
    const SyncReplicaPeerTlsServerResult& result) noexcept {
    if (result.disposition ==
        SyncReplicaPeerTlsServerDisposition::AcceptDeadlineExpired) {
        return SyncReplicaServeSupervisorStopReason::AcceptDeadlineExpired;
    }
    if (sync_replica_serve_session_is_authenticated_peer_closed_idle(result)) {
        return SyncReplicaServeSupervisorStopReason::AuthenticatedPeerClosedIdle;
    }
    if (result.disposition !=
            SyncReplicaPeerTlsServerDisposition::ApplicationServed ||
        !result.application.has_value()) {
        return SyncReplicaServeSupervisorStopReason::SessionFailed;
    }

    const SyncReplicaPeerTlsServeResult& application = *result.application;
    if (application.disposition ==
            SyncReplicaPeerTlsServeDisposition::FileDelivery &&
        application.file_delivery.has_value() &&
        application.file_delivery->disposition ==
            SyncReplicaFileTlsReceiveDisposition::ReceiptSent) {
        return std::nullopt;
    }
    if (application.disposition ==
            SyncReplicaPeerTlsServeDisposition::Reconciliation &&
        application.reconciliation.has_value()) {
        switch (application.reconciliation->disposition) {
            case SyncReplicaReconciliationTlsServeDisposition::Complete:
            case SyncReplicaReconciliationTlsServeDisposition::
                RoundTripLimitReached:
            case SyncReplicaReconciliationTlsServeDisposition::
                SourcePayloadUnavailable:
            case SyncReplicaReconciliationTlsServeDisposition::
                SourcePayloadPreparing:
                return std::nullopt;
            case SyncReplicaReconciliationTlsServeDisposition::
                RequestDeadlineExpired:
            case SyncReplicaReconciliationTlsServeDisposition::
                ResponseDeadlineExpired:
            case SyncReplicaReconciliationTlsServeDisposition::PeerClosed:
                break;
        }
    }
    return SyncReplicaServeSupervisorStopReason::SessionFailed;
}

}  // namespace anonsync
