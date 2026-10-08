#pragma once

#include "sync_replica_file_tls_client.hpp"
#include "sync_replica_file_tls_server.hpp"
#include "sync_replica_outbox_clock.hpp"

#include <array>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaSessionSupervisorMaximumSessions =
    256U;
inline constexpr std::uint64_t
    kSyncReplicaSessionSupervisorMaximumStageTimeoutSeconds = 3600U;
inline constexpr std::uint64_t
    kSyncReplicaSessionSupervisorMaximumRuntimeSeconds = 86400U;
inline constexpr std::uint64_t
    kSyncReplicaSessionSupervisorStageCount = 5U;
inline constexpr std::uint64_t
    kSyncReplicaSessionSupervisorReceiptStageOrdinal = 4U;

enum class SyncReplicaSessionStage : std::size_t {
    First = 0U,
    Second = 1U,
    Third = 2U,
    Fourth = 3U,
    Fifth = 4U,
};

struct SyncReplicaSessionSupervisorLimits final {
    std::uint64_t maximum_sessions = 0U;
    std::uint64_t stage_timeout_seconds = 0U;

    // An absent value preserves one-session compatibility: only the five
    // caller-owned stage cutpoints bound that conversation. Bounded batch
    // commands supply this value explicitly so setup time is charged and no
    // later session may begin after the one absolute command cutpoint.
    std::optional<std::uint64_t> maximum_runtime_seconds;

    bool operator==(const SyncReplicaSessionSupervisorLimits&) const = default;
};

void validate_sync_replica_session_supervisor_limits_or_throw(
    const SyncReplicaSessionSupervisorLimits& limits,
    std::string_view label = "sync replica session supervisor limits");

// Reject a lease that can expire solely within the modeled sender receipt-read
// horizon and the complete wall-clock movement/uncertainty envelope admitted by
// the durable outbox clock policy. This is a necessary lower bound, not a
// real-time completion guarantee: process descheduling, SQLite writer waits,
// local decoding/application work, and Linux system suspension remain outside
// this static proof. Expiry is still fail-closed at settlement. A future exact
// renewable heartbeat may use shorter renewal periods only while it owns and
// renews the same fenced claim before expiry. Transport currently uses
// steady_clock while durable observations use CLOCK_BOOTTIME.
[[nodiscard]] std::uint64_t
sync_replica_session_receipt_horizon_seconds_or_throw(
    std::uint64_t stage_timeout_seconds,
    std::string_view label = "sync replica session receipt horizon");
[[nodiscard]] std::uint64_t
minimum_sync_replica_session_claim_lease_seconds_or_throw(
    std::uint64_t stage_timeout_seconds,
    const SyncReplicaOutboxClockPolicy& clock_policy = {},
    std::string_view label = "sync replica session claim lease");
void validate_sync_replica_session_claim_lease_seconds_or_throw(
    std::uint64_t lease_seconds,
    std::uint64_t stage_timeout_seconds,
    const SyncReplicaOutboxClockPolicy& clock_policy = {},
    std::string_view label = "sync replica session claim lease");

struct SyncReplicaSessionDeadlinePlan final {
    std::uint64_t session_index = 0U;
    std::array<std::chrono::steady_clock::time_point, 5U> stages{};
    std::optional<std::chrono::steady_clock::time_point> command_deadline;

    [[nodiscard]] std::chrono::steady_clock::time_point deadline(
        SyncReplicaSessionStage stage) const noexcept;
    [[nodiscard]] bool command_limits(
        SyncReplicaSessionStage stage) const noexcept;
    [[nodiscard]] SyncReplicaFileTlsClientDeadlines
    client_deadlines() const noexcept;
    [[nodiscard]] SyncReplicaFileTlsServerDeadlines
    server_deadlines() const noexcept;

    bool operator==(const SyncReplicaSessionDeadlinePlan&) const = default;
};

enum class SyncReplicaSessionAuthorizationDisposition {
    Authorized,
    MaximumSessionsReached,
    CommandDeadlineReached,
};

struct SyncReplicaSessionAuthorization final {
    SyncReplicaSessionAuthorizationDisposition disposition =
        SyncReplicaSessionAuthorizationDisposition::MaximumSessionsReached;
    std::optional<SyncReplicaSessionDeadlinePlan> plan;
};

// Process-local bounded composition policy. This owner does not mint durable
// work, lease, clock, transport, or retry authority. It only decides whether a
// later one-session owner may begin and clamps that owner's five absolute
// steady-clock cutpoints to one optional command deadline. The command deadline
// starts before deployment/store/TLS preflight; synchronous local work is not
// asynchronously interrupted, but its elapsed time is charged at the next
// admission/deadline boundary.
class SyncReplicaSessionSupervisor final {
public:
    SyncReplicaSessionSupervisor(
        SyncReplicaSessionSupervisorLimits limits,
        std::chrono::steady_clock::time_point started_at,
        std::string label = "sync replica session supervisor");

    SyncReplicaSessionSupervisor(const SyncReplicaSessionSupervisor&) = delete;
    SyncReplicaSessionSupervisor& operator=(
        const SyncReplicaSessionSupervisor&) = delete;
    SyncReplicaSessionSupervisor(SyncReplicaSessionSupervisor&&) = delete;
    SyncReplicaSessionSupervisor& operator=(
        SyncReplicaSessionSupervisor&&) = delete;

    [[nodiscard]] SyncReplicaSessionAuthorization
    authorize_next_or_throw();
    [[nodiscard]] SyncReplicaSessionAuthorization
    authorize_next_at_or_throw(
        std::chrono::steady_clock::time_point observed_at);

    [[nodiscard]] const SyncReplicaSessionSupervisorLimits& limits()
        const noexcept {
        return limits_;
    }
    [[nodiscard]] std::uint64_t sessions_authorized() const noexcept {
        return sessions_authorized_;
    }
    [[nodiscard]] std::chrono::steady_clock::time_point started_at()
        const noexcept {
        return started_at_;
    }
    [[nodiscard]] const std::optional<
        std::chrono::steady_clock::time_point>& command_deadline()
        const noexcept {
        return command_deadline_;
    }
    [[nodiscard]] bool command_deadline_reached_at(
        std::chrono::steady_clock::time_point observed_at) const noexcept;

private:
    SyncReplicaSessionSupervisorLimits limits_;
    std::chrono::steady_clock::time_point started_at_;
    std::optional<std::chrono::steady_clock::time_point> command_deadline_;
    std::uint64_t sessions_authorized_ = 0U;
    std::string label_;
};

enum class SyncReplicaSendSupervisorStopReason {
    MaximumSessionsReached,
    CommandDeadlineReached,
    NoReadyDelivery,
    ReceiverDeferred,
    ReceiptApplyConflict,
    SessionFailed,
};

[[nodiscard]] std::string_view sync_replica_send_supervisor_stop_reason_name(
    SyncReplicaSendSupervisorStopReason reason) noexcept;
[[nodiscard]] bool sync_replica_send_supervisor_stop_is_success(
    SyncReplicaSendSupervisorStopReason reason) noexcept;
[[nodiscard]] bool sync_replica_send_session_effect_is_settled(
    const SyncReplicaFileTlsClientResult& result) noexcept;
[[nodiscard]] bool sync_replica_send_session_receiver_deferred(
    const SyncReplicaFileTlsClientResult& result) noexcept;

// Exact no-claim terminal observation after mutual authentication. This is
// suitable for mapping a command-clamped request-admission expiry to the outer
// command deadline only when no operation identity, claim, application byte, or
// receipt state exists. It is not evidence that the sender had no ready work.
[[nodiscard]] bool
sync_replica_send_session_is_authenticated_dispatch_deadline_clean(
    const SyncReplicaFileTlsClientResult& result) noexcept;
[[nodiscard]] std::optional<SyncReplicaSendSupervisorStopReason>
sync_replica_send_supervisor_stop_after(
    const SyncReplicaFileTlsClientResult& result) noexcept;

enum class SyncReplicaServeSupervisorStopReason {
    MaximumSessionsReached,
    CommandDeadlineReached,
    AcceptDeadlineExpired,
    AuthenticatedPeerClosedIdle,
    SessionFailed,
};

[[nodiscard]] std::string_view sync_replica_serve_supervisor_stop_reason_name(
    SyncReplicaServeSupervisorStopReason reason) noexcept;
[[nodiscard]] bool sync_replica_serve_supervisor_stop_is_success(
    SyncReplicaServeSupervisorStopReason reason) noexcept;

// A close is idle only when an authorized TLS peer completed the handshake and
// no application-record prefix, frame, body, inbound decision, or receipt write
// exists. It is not evidence that the peer had no work; it is merely proof that
// this bounded receiver session spent no durable file-delivery authority.
[[nodiscard]] bool
sync_replica_serve_session_is_authenticated_peer_closed_idle(
    const SyncReplicaFileTlsServerResult& result) noexcept;
[[nodiscard]] std::optional<SyncReplicaServeSupervisorStopReason>
sync_replica_serve_supervisor_stop_after(
    const SyncReplicaFileTlsServerResult& result) noexcept;
[[nodiscard]] bool
sync_replica_serve_session_is_authenticated_peer_closed_idle(
    const SyncReplicaPeerTlsServerResult& result) noexcept;
[[nodiscard]] std::optional<SyncReplicaServeSupervisorStopReason>
sync_replica_serve_supervisor_stop_after(
    const SyncReplicaPeerTlsServerResult& result) noexcept;

}  // namespace anonsync
