#pragma once

#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_tls_poll.hpp"
#include "sync_replica_tls_transport.hpp"

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>

namespace anonsync {

// Terminal outcomes for one receiver-owned application conversation. A
// receipt timeout after inbound is populated means the durable receiver effect
// decision exists but no authenticated terminal receipt completed locally; the
// sender must reconcile through an exact retry on a fresh channel.
enum class SyncReplicaFileTlsReceiveDisposition {
    PeerClosed,
    RequestDeadlineExpired,
    ReceiptDeadlineExpired,
    ReceiptSent,
};

struct SyncReplicaFileTlsReceiveResult final {
    SyncReplicaFileTlsReceiveDisposition disposition =
        SyncReplicaFileTlsReceiveDisposition::PeerClosed;

    // Present only after one complete canonical request has crossed the
    // receiver service's durable idempotent decision boundary.
    std::optional<SyncReplicaInboundFileDelivery> inbound;

    std::uint64_t request_prefix_bytes_received = 0U;
    std::uint64_t request_frame_bytes = 0U;
    std::uint64_t request_body_bytes_received = 0U;
    bool receipt_write_started = false;
    std::uint64_t receipt_prefix_bytes_written = 0U;
    bool receipt_prefix_accepted = false;
    std::uint64_t receipt_frame_bytes = 0U;
    std::uint64_t receipt_body_bytes_written = 0U;

    bool operator==(const SyncReplicaFileTlsReceiveResult&) const = default;
};

// Borrowed low-level primitive for exactly one strict-nonblocking receiver
// conversation:
//
//   receiver-authority preflight before application bytes
//     -> complete bounded authenticated request
//     -> durable idempotent file/evidence decision
//     -> live channel re-attestation at the response frontier
//     -> exact authenticated receipt record
//     -> unconditional local capability discard
//
// The request and receipt deadlines are independent absolute steady-clock
// cutpoints. Request expiry invokes no durable callback. Receipt expiry never
// rolls back a durable effect and never fabricates peer receipt; it returns the
// exact durable inbound decision for diagnostics. Every terminal return and
// every post-preflight exception discards the local TLS capability, including a
// successful receipt write, so no second record can be interpreted as part of
// this application conversation.
//
// The receipt owner retains exact nonblocking WANT state from its first prefix
// operation through its final body operation. Each OpenSSL operation remains
// bounded by the transport's 64 KiB step and every WANT retry is preceded by the
// shared poll owner. Total work is bounded by the service's canonical frame
// ceilings and the two caller-owned deadlines.
[[nodiscard]] SyncReplicaFileTlsReceiveResult
receive_one_sync_replica_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::chrono::steady_clock::time_point request_deadline,
    std::chrono::steady_clock::time_point receipt_deadline,
    const std::string& label = "sync replica file TLS receiver exchange");

// First-frame dispatch adapter. The supplied request is the exact complete
// record already read under service.max_request_frame_bytes(). Metrics describe
// the full request record, including its record prefix, even though the caller
// performed the read. The same preflight, durable decision, receipt write, and
// unconditional channel-discard rules remain in force.
[[nodiscard]] SyncReplicaFileTlsReceiveResult
receive_one_sync_replica_file_delivery_after_first_request_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string first_request_frame,
    std::chrono::steady_clock::time_point receipt_deadline,
    const std::string& label =
        "sync replica file TLS receiver after first request");

// Move-only owner for one accepted receiver-side application session. The
// constructor preflights receiver service/channel compatibility before taking
// the channel, then freezes two absolute deadlines and exclusive ownership.
// run_or_throw() may be called exactly once. Success, timeout, peer close,
// exception, explicit discard, destruction, or move-assignment over an active
// owner all permanently discard the local authenticated capability.
//
// This is intentionally smaller than a listener: it does not own SSL*, the
// underlying socket descriptor, TLS close_notify, peer enrollment, accept-loop
// quotas, or persistent dead-letter policy. The accept owner must close its
// transport after this local application capability becomes terminal.
class SyncReplicaFileTlsReceiverSession final {
public:
    SyncReplicaFileTlsReceiverSession(
        SyncReplicaFileDeliveryService& service,
        SyncReplicaTlsAuthenticatedChannel&& channel,
        std::chrono::steady_clock::time_point request_deadline,
        std::chrono::steady_clock::time_point receipt_deadline,
        std::string label = "sync replica file TLS receiver session");

    SyncReplicaFileTlsReceiverSession(
        const SyncReplicaFileTlsReceiverSession&) = delete;
    SyncReplicaFileTlsReceiverSession& operator=(
        const SyncReplicaFileTlsReceiverSession&) = delete;
    SyncReplicaFileTlsReceiverSession(
        SyncReplicaFileTlsReceiverSession&& other) noexcept;
    SyncReplicaFileTlsReceiverSession& operator=(
        SyncReplicaFileTlsReceiverSession&& other) noexcept;
    ~SyncReplicaFileTlsReceiverSession() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] SyncReplicaFileTlsReceiveResult run_or_throw();
    void discard_noexcept() noexcept;

private:
    SyncReplicaFileDeliveryService* service_ = nullptr;
    std::optional<SyncReplicaTlsAuthenticatedChannel> channel_;
    std::chrono::steady_clock::time_point request_deadline_{};
    std::chrono::steady_clock::time_point receipt_deadline_{};
    std::string label_;
};

}  // namespace anonsync
