#pragma once

#include "sync_replica_file_delivery_service.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_tls_transport.hpp"

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

#include <openssl/ssl.h>

namespace anonsync {

// Move-only retained reference to one caller-configured OpenSSL client context.
// The factory increments SSL_CTX's reference count before any socket or durable
// delivery authority is spent. Certificate, private-key, trust-store, and
// verification-depth configuration remain caller-owned and must not be mutated
// while an SSL object derived from this retained context is live.
class SyncReplicaFileTlsClientContext final {
public:
    SyncReplicaFileTlsClientContext(
        const SyncReplicaFileTlsClientContext&) = delete;
    SyncReplicaFileTlsClientContext& operator=(
        const SyncReplicaFileTlsClientContext&) = delete;
    SyncReplicaFileTlsClientContext(
        SyncReplicaFileTlsClientContext&& other) noexcept;
    SyncReplicaFileTlsClientContext& operator=(
        SyncReplicaFileTlsClientContext&& other) noexcept;
    ~SyncReplicaFileTlsClientContext() noexcept;

    [[nodiscard]] bool active() const noexcept {
        return context_ != nullptr;
    }

private:
    explicit SyncReplicaFileTlsClientContext(SSL_CTX* context) noexcept
        : context_(context) {}

    SSL_CTX* context_ = nullptr;

    friend SyncReplicaFileTlsClientContext
    retain_sync_replica_file_tls_client_context_or_throw(
        SSL_CTX*, const std::string&);
    friend struct SyncReplicaFileTlsClientContextAccess;
};

[[nodiscard]] SyncReplicaFileTlsClientContext
retain_sync_replica_file_tls_client_context_or_throw(
    SSL_CTX* context,
    const std::string& label = "sync replica file TLS client context");

// Deliberately numeric-only. This owner does not silently delegate replica
// routing authority, blocking behavior, search domains, or address churn to a
// process-global resolver. IPv4 and unscoped IPv6 literals are accepted.
struct SyncReplicaFileTlsClientEndpoint final {
    std::string numeric_address;
    std::uint16_t port = 0U;

    bool operator==(const SyncReplicaFileTlsClientEndpoint&) const = default;
};

struct SyncReplicaFileTlsClientDeadlines final {
    std::chrono::steady_clock::time_point connect;
    std::chrono::steady_clock::time_point handshake;
    std::chrono::steady_clock::time_point request;
    std::chrono::steady_clock::time_point receipt;
    std::chrono::steady_clock::time_point shutdown;
};

enum class SyncReplicaFileTlsClientDisposition {
    ConnectDeadlineExpired,
    ConnectFailed,
    HandshakeDeadlineExpired,
    HandshakeRejected,
    PeerUnauthorized,
    NoReadyDelivery,
    RequestDeadlineExpired,
    PeerClosed,
    ReceiptDeadlineExpired,
    ReceiptApplied,
};

enum class SyncReplicaFileTlsClientShutdownDisposition {
    NotAttempted,
    CloseNotifySent,
    Complete,
    DeadlineExpired,
    Failed,
};

struct SyncReplicaFileTlsClientResult final {
    SyncReplicaFileTlsClientDisposition disposition =
        SyncReplicaFileTlsClientDisposition::ConnectDeadlineExpired;
    SyncReplicaFileTlsClientShutdownDisposition shutdown_disposition =
        SyncReplicaFileTlsClientShutdownDisposition::NotAttempted;

    bool socket_created = false;
    bool socket_policy_verified = false;
    bool connected = false;
    bool handshake_complete = false;
    bool peer_authenticated = false;

    std::uint64_t connect_attempts = 0U;
    std::uint64_t handshake_attempts = 0U;
    std::uint64_t shutdown_attempts = 0U;
    std::optional<int> connect_error;
    std::optional<int> handshake_ssl_error;
    std::optional<int> shutdown_ssl_error;

    std::optional<std::string> peer_spki_sha256;
    std::optional<SyncReplicaActor> peer_actor;

    // Present after one exact claim crossed the accepted TLS-prefix frontier.
    std::optional<std::string> operation_id;
    std::optional<std::string> claim_id;
    std::optional<std::string> request_digest;
    std::uint64_t request_prefix_bytes_written = 0U;
    std::uint64_t request_frame_bytes = 0U;
    std::uint64_t request_body_bytes_written = 0U;

    std::uint64_t receipt_prefix_bytes_received = 0U;
    std::uint64_t receipt_frame_bytes = 0U;
    std::uint64_t receipt_body_bytes_received = 0U;
    std::optional<SyncReplicaFileDeliveryReceiptApplyResult>
        receipt_apply_result;

    bool operator==(const SyncReplicaFileTlsClientResult&) const = default;
};

[[nodiscard]] std::string_view sync_replica_file_tls_client_disposition_name(
    SyncReplicaFileTlsClientDisposition disposition) noexcept;
[[nodiscard]] std::string_view
sync_replica_file_tls_client_shutdown_disposition_name(
    SyncReplicaFileTlsClientShutdownDisposition disposition) noexcept;

#if !defined(_WIN32)
// Owns one outbound replica conversation end to end:
//
//   immutable durable payload-store observation
//     -> exact nonblocking+CLOEXEC numeric-address connect
//     -> bounded TLS 1.3 mutual-authentication handshake
//     -> expected actor/SPKI authorization
//     -> at most one SQLite outbox claim
//     -> guarded complete encrypted record-prefix cutpoint
//     -> bounded request body
//     -> bounded authenticated receipt
//     -> exact durable receipt application
//     -> optional one-shot close_notify
//     -> unconditional socket close
//
// No outbox claim is attempted before peer authentication and payload-store
// preflight. NoReadyDelivery therefore spends neither claim nor request bytes.
// Once the complete request prefix is accepted under the SQLite dispatch guard,
// request or receipt timeout leaves the exact claim live and ambiguous; this
// owner never converts transport uncertainty into a retry release. A complete
// authenticated receipt is applied before ReceiptApplied is returned. As on the
// receiver, TLS shutdown is subordinate to the application result and cannot
// downgrade a completed receipt application.
//
// The endpoint is numeric-only and all deadlines are absolute steady-clock
// cutpoints. The function is process/thread-affine through the SQLite, payload,
// socket, and authenticated-channel authorities it composes.
[[nodiscard]] SyncReplicaFileTlsClientResult
send_one_sync_replica_file_delivery_tls_session_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot,
    SyncReplicaFileTlsClientContext client_context,
    const SyncReplicaFileTlsClientEndpoint& endpoint,
    const SyncReplicaTlsPeerPolicy& expected_peer,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFileTlsClientDeadlines& deadlines,
    const std::string& label = "sync replica file TLS client session");
#endif

}  // namespace anonsync
