#pragma once

#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_tls_poll.hpp"
#include "sync_replica_tls_transport.hpp"

#include <chrono>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

namespace detail {
class SyncReplicaFileTlsDispatchState;
}

// Move-only ownership of one exact file-delivery attempt after its complete TLS
// record prefix and SQLite dispatch cutpoint have both committed, but before the
// canonical request body has necessarily reached local TLS completion.
//
// The private state retains the exact frozen claim/request/frame/digest used at
// the guarded prefix frontier. The nested TLS continuation owns a separate
// private copy of the exact canonical frame and its same-pointer WANT retry
// state. Deadline expiry therefore preserves both durable attempt identity and
// transport progress; it never releases or settles the outbox claim.
//
// Destruction, move-assignment over an active value, or a terminal transport
// exception abandons the accepted-prefix record and poisons that TLS stream.
// The durable claim remains live and ambiguous until an authenticated terminal
// receipt, an explicit exact release, or owned-clock expiry changes it.
class SyncReplicaFileTlsDispatchContinuation final {
public:
    SyncReplicaFileTlsDispatchContinuation(
        const SyncReplicaFileTlsDispatchContinuation&) = delete;
    SyncReplicaFileTlsDispatchContinuation& operator=(
        const SyncReplicaFileTlsDispatchContinuation&) = delete;
    SyncReplicaFileTlsDispatchContinuation(
        SyncReplicaFileTlsDispatchContinuation&& other) noexcept;
    SyncReplicaFileTlsDispatchContinuation& operator=(
        SyncReplicaFileTlsDispatchContinuation&& other) noexcept;
    ~SyncReplicaFileTlsDispatchContinuation() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] bool complete() const noexcept;
    [[nodiscard]] std::uint64_t frame_bytes() const noexcept;
    [[nodiscard]] std::uint64_t body_bytes_written() const noexcept;

    // The exact frozen attempt remains inspectable after completion or failure
    // so receipt validation and diagnostics do not depend on caller-owned data.
    [[nodiscard]] const SyncReplicaOutboundFileDelivery& outbound_or_throw()
        const;

    [[nodiscard]] SyncReplicaTlsRecordWriteProgress advance_or_throw();
    [[nodiscard]] SyncReplicaTlsSocketReadinessTarget
        pending_readiness_or_throw() const;
    [[nodiscard]] SyncReplicaTlsRecordWritePollProgress
    poll_and_advance_or_throw(
        std::chrono::steady_clock::time_point deadline,
        std::string_view label = "sync replica file TLS dispatch poll");

    // Compatibility adapter for blocking/caller-managed use. On a strict
    // nonblocking WANT it fails and poisons exactly as the parent rev0886 API
    // did; event-loop owners should use advance/poll instead.
    void finish_or_throw();

private:
    friend SyncReplicaFileTlsDispatchContinuation
    begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
        SyncReplicaFileDeliveryService&,
        const SyncReplicaTlsAuthenticatedChannel&,
        const SyncReplicaOutboundFileDelivery&, const std::string&);

    SyncReplicaFileTlsDispatchContinuation(
        std::unique_ptr<detail::SyncReplicaFileTlsDispatchState> state,
        SyncReplicaTlsRecordWriteContinuation transport) noexcept;

    std::unique_ptr<detail::SyncReplicaFileTlsDispatchState> state_;
    SyncReplicaTlsRecordWriteContinuation transport_;
};

// Freezes one already-prepared file-delivery value, reacquires its exact claim
// under BEGIN IMMEDIATE, re-proves the authenticated TLS channel, and accepts
// only the complete encrypted 8-byte record prefix while the SQLite guard is
// held. The guard commits and releases before this function returns the
// continuation that exclusively owns all body progress.
//
// Every allocation needed by the outer continuation is completed before the
// prefix can be accepted. Failure before prefix acceptance exact-releases the
// claim through service policy. Failure after prefix acceptance is ambiguous:
// the stream is poisoned and the claim remains live.
[[nodiscard]] SyncReplicaFileTlsDispatchContinuation
begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    const SyncReplicaOutboundFileDelivery& outbound,
    const std::string& label = "sync replica file TLS dispatch begin");

// Claims and canonically prepares at most one File operation, then enters the
// guarded prefix frontier and returns exclusive body ownership. This is the
// bounded event-loop convenience path: unlike claim_and_dispatch... below, an
// ordinary nonblocking WANT is retained rather than collapsed into failure.
[[nodiscard]] std::optional<SyncReplicaFileTlsDispatchContinuation>
claim_and_begin_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    SyncReplicaFilePayloadSnapshot payload_snapshot,
    const std::string& label =
        "sync replica file TLS claim-and-begin dispatch");

#if !defined(_WIN32)
[[nodiscard]] std::optional<SyncReplicaFileTlsDispatchContinuation>
claim_and_begin_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot,
    const std::string& label =
        "sync replica durable file TLS claim-and-begin dispatch");
#endif

// Synchronous compatibility wrapper around begin...(). It is appropriate only
// when the caller guarantees that finish_or_throw() will not encounter an
// ordinary nonblocking WANT. New bounded event-loop code should retain the
// returned continuation instead of collapsing it here.
void dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    const SyncReplicaOutboundFileDelivery& outbound,
    const std::string& label = "sync replica file TLS dispatch");

// Claims, resolves, and canonically prepares at most one File operation through
// SyncReplicaFileDeliveryService, then executes the synchronous compatibility
// wrapper above. The returned value is retained for exact receipt validation.
// New nonblocking owners should use claim_and_begin... instead.
[[nodiscard]] std::optional<SyncReplicaOutboundFileDelivery>
claim_and_dispatch_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    SyncReplicaFilePayloadSnapshot payload_snapshot,
    const std::string& label = "sync replica file TLS claim-and-dispatch");

#if !defined(_WIN32)
[[nodiscard]] std::optional<SyncReplicaOutboundFileDelivery>
claim_and_dispatch_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot,
    const std::string& label =
        "sync replica durable file TLS claim-and-dispatch");
#endif

}  // namespace anonsync
