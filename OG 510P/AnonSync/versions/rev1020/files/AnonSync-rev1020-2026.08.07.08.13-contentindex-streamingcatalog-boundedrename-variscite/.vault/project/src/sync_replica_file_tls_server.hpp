#pragma once

#include "sync_process_incarnation.hpp"
#include "sync_replica_file_tls_exchange.hpp"
#include "sync_replica_peer_tls_exchange.hpp"
#include "sync_replica_tls_membership_anchored_owner.hpp"
#include "sync_socket_readiness_identity.hpp"
#include "sync_thread_incarnation.hpp"

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

#include <openssl/ssl.h>

namespace anonsync {

class SyncReplicaConnectedStream;

// Move-only retained reference to one caller-configured OpenSSL server context.
// The factory increments SSL_CTX's reference count before accept authority can
// be spent. The underlying context must still be treated as immutable while any
// SSL object derived from it is in use; reference retention closes lifetime,
// not concurrent-mutation, hazards.
class SyncReplicaFileTlsServerContext final {
public:
    SyncReplicaFileTlsServerContext(
        const SyncReplicaFileTlsServerContext&) = delete;
    SyncReplicaFileTlsServerContext& operator=(
        const SyncReplicaFileTlsServerContext&) = delete;
    SyncReplicaFileTlsServerContext(
        SyncReplicaFileTlsServerContext&& other) noexcept;
    SyncReplicaFileTlsServerContext& operator=(
        SyncReplicaFileTlsServerContext&& other) noexcept;
    ~SyncReplicaFileTlsServerContext() noexcept;

    [[nodiscard]] bool active() const noexcept {
        return context_ != nullptr;
    }

    // Retains one additional immutable OpenSSL context reference for a later
    // accepted session. This mirrors the client-side retained-context seam and
    // lets a long-running listener reuse configured identity/trust material
    // without sharing an SSL object or rebuilding the SSL_CTX per connection.
    [[nodiscard]] SyncReplicaFileTlsServerContext retain_another_or_throw(
        const std::string& label =
            "sync replica retained TLS server context") const;

private:
    explicit SyncReplicaFileTlsServerContext(SSL_CTX* context) noexcept
        : context_(context) {}

    SSL_CTX* context_ = nullptr;

    friend SyncReplicaFileTlsServerContext
    retain_sync_replica_file_tls_server_context_or_throw(
        SSL_CTX*, const std::string&);
    friend struct SyncReplicaFileTlsServerContextAccess;
};

[[nodiscard]] SyncReplicaFileTlsServerContext
retain_sync_replica_file_tls_server_context_or_throw(
    SSL_CTX* context,
    const std::string& label = "sync replica file TLS server context");

// Move-only, non-owning authority for one exact nonblocking listening stream
// socket lifetime. Minting proves SO_ACCEPTCONN, O_NONBLOCK, and FD_CLOEXEC and
// binds later accept use to the creating process and thread. The caller retains
// descriptor ownership and must serialize close, dup2, fcntl, and listen-state
// mutation for the lifetime of this capability.
class SyncReplicaFileTlsServerListener final {
public:
    SyncReplicaFileTlsServerListener(
        const SyncReplicaFileTlsServerListener&) = delete;
    SyncReplicaFileTlsServerListener& operator=(
        const SyncReplicaFileTlsServerListener&) = delete;
    SyncReplicaFileTlsServerListener(
        SyncReplicaFileTlsServerListener&& other) noexcept;
    SyncReplicaFileTlsServerListener& operator=(
        SyncReplicaFileTlsServerListener&& other) noexcept;
    ~SyncReplicaFileTlsServerListener() noexcept = default;

    [[nodiscard]] bool active() const noexcept {
        return socket_.has_value();
    }
    [[nodiscard]] int descriptor() const noexcept {
        return socket_.has_value() ? socket_->descriptor() : -1;
    }

private:
    friend SyncReplicaFileTlsServerListener
    observe_sync_replica_file_tls_server_listener_or_throw(
        int, const std::string&);
    friend struct SyncReplicaFileTlsServerListenerAccess;

    SyncReplicaFileTlsServerListener(
        SyncSocketLifetimeIdentity socket,
        SyncProcessIncarnation process,
        SyncThreadIncarnation thread) noexcept;

    std::optional<SyncSocketLifetimeIdentity> socket_;
    SyncProcessIncarnation process_;
    SyncThreadIncarnation thread_;
};

[[nodiscard]] SyncReplicaFileTlsServerListener
observe_sync_replica_file_tls_server_listener_or_throw(
    int descriptor,
    const std::string& label = "sync replica file TLS server listener");

struct SyncReplicaFileTlsServerDeadlines final {
    std::chrono::steady_clock::time_point accept;
    std::chrono::steady_clock::time_point handshake;
    std::chrono::steady_clock::time_point request;
    std::chrono::steady_clock::time_point receipt;
    std::chrono::steady_clock::time_point shutdown;
};

enum class SyncReplicaFileTlsServerDisposition {
    AcceptDeadlineExpired,
    HandshakeDeadlineExpired,
    HandshakeRejected,
    PeerUnauthorized,
    PeerClosed,
    RequestDeadlineExpired,
    ReceiptDeadlineExpired,
    ReceiptSent,
};

// Shutdown is deliberately subordinate to the application result. A completed
// receipt write is not downgraded if close_notify later times out or fails, and
// close_notify is never represented as proof that the peer applied a receipt.
enum class SyncReplicaFileTlsServerShutdownDisposition {
    NotAttempted,
    CloseNotifySent,
    Complete,
    DeadlineExpired,
    Failed,
};

struct SyncReplicaFileTlsServerResult final {
    SyncReplicaFileTlsServerDisposition disposition =
        SyncReplicaFileTlsServerDisposition::AcceptDeadlineExpired;
    SyncReplicaFileTlsServerShutdownDisposition shutdown_disposition =
        SyncReplicaFileTlsServerShutdownDisposition::NotAttempted;

    bool accepted = false;
    bool accepted_socket_policy_verified = false;
    bool handshake_complete = false;
    std::uint64_t membership_state_generation = 0U;
    std::uint64_t membership_policy_epoch = 0U;
    std::uint64_t membership_entry_count = 0U;
    std::string membership_snapshot_digest;
    std::string membership_previous_chain_digest;
    std::string membership_chain_digest;
    std::uint64_t membership_durable_anchor_state_generation = 0U;
    std::string membership_durable_anchor_chain_digest;
    std::uint64_t membership_durable_anchor_transition_sequence = 0U;
    std::string membership_durable_anchor_transition_digest;
    std::uint64_t accept_attempts = 0U;
    std::uint64_t handshake_attempts = 0U;
    std::uint64_t shutdown_attempts = 0U;
    std::optional<int> handshake_ssl_error;
    std::optional<int> shutdown_ssl_error;
    std::optional<std::string> peer_spki_sha256;
    std::optional<SyncReplicaActor> peer_actor;
    std::optional<SyncReplicaFileTlsReceiveResult> receive;

    bool operator==(const SyncReplicaFileTlsServerResult&) const = default;
};

// Owns one accepted receiver session end to end:
//
//   exact listener capability
//     -> atomic nonblocking+CLOEXEC accept
//     -> bounded TLS 1.3 mutual-authentication handshake
//     -> durable append-only membership authority resolution
//     -> authenticated channel capability
//     -> one exclusive move-only receiver session
//     -> one bounded durable file-delivery conversation
//     -> optional one-shot close_notify
//     -> unconditional accepted-descriptor close
//
// The listening descriptor is never owned or closed here. The accepted child,
// SSL object, and all session authority are scope-owned and cannot escape. An
// accept timeout, rejected handshake, or unauthorized peer invokes no durable
// file service callback. Request/receipt semantics are inherited exactly from
// SyncReplicaFileTlsReceiverSession and its one-conversation exchange. The
// retained server-context value closes raw SSL_CTX lifetime races; the caller
// must still serialize mutation of the underlying context while this call is
// live. Anchored membership authority is taken by value and can be emitted only
// after the append-only membership owner commits and an independently persisted
// anchor store covers that exact chain cutpoint. The immutable snapshot, chain,
// and retained anchor-store evidence are bound into every terminal result. Raw
// membership-owner authority is a distinct type and cannot enter this API. A
// later policy rotation does not revoke the already-issued value while accept
// or handshake is in progress. OpenSSL
// callbacks configured on the context remain part of the caller-owned TLS trust
// stack.
//
// After ReceiptSent, this owner attempts OpenSSL's one-shot fast shutdown. The
// application protocol has an unambiguous complete receipt record and admits no
// further message on the one-shot session; waiting for peer close_notify is not
// required for application settlement. Any other terminal path closes without
// SSL_shutdown because an exact pending OpenSSL operation or fatal session may
// exist. All deadlines are absolute cutpoints. In particular, accept or
// handshake expiry may report zero attempts when preceding validation, accepted-
// socket policy proof, or scheduling exhausts the supplied stage budget before
// the first stage syscall. Attempt counters are diagnostic evidence, not
// authority that a syscall must occur.
[[nodiscard]] SyncReplicaFileTlsServerResult
serve_one_sync_replica_file_delivery_tls_session_or_throw(
    SyncReplicaFileDeliveryService& service,
    SyncReplicaFileTlsServerListener& listener,
    SyncReplicaFileTlsServerContext server_context,
    SyncReplicaTlsAnchoredMembershipAuthority membership,
    const SyncReplicaFileTlsServerDeadlines& deadlines,
    const std::string& label = "sync replica file TLS server session");


enum class SyncReplicaPeerTlsServerDisposition : std::uint8_t {
    AcceptDeadlineExpired = 1U,
    HandshakeDeadlineExpired = 2U,
    HandshakeRejected = 3U,
    PeerUnauthorized = 4U,
    ApplicationServed = 5U,
};

struct SyncReplicaPeerTlsServerResult final {
    SyncReplicaPeerTlsServerDisposition disposition =
        SyncReplicaPeerTlsServerDisposition::AcceptDeadlineExpired;
    SyncReplicaFileTlsServerShutdownDisposition shutdown_disposition =
        SyncReplicaFileTlsServerShutdownDisposition::NotAttempted;

    bool accepted = false;
    bool accepted_socket_policy_verified = false;
    bool handshake_complete = false;
    std::uint64_t membership_state_generation = 0U;
    std::uint64_t membership_policy_epoch = 0U;
    std::uint64_t membership_entry_count = 0U;
    std::string membership_snapshot_digest;
    std::string membership_previous_chain_digest;
    std::string membership_chain_digest;
    std::uint64_t membership_durable_anchor_state_generation = 0U;
    std::string membership_durable_anchor_chain_digest;
    std::uint64_t membership_durable_anchor_transition_sequence = 0U;
    std::string membership_durable_anchor_transition_digest;
    std::uint64_t accept_attempts = 0U;
    std::uint64_t handshake_attempts = 0U;
    std::uint64_t shutdown_attempts = 0U;
    std::optional<int> handshake_ssl_error;
    std::optional<int> shutdown_ssl_error;
    std::optional<std::string> peer_spki_sha256;
    std::optional<SyncReplicaActor> peer_actor;
    std::optional<SyncReplicaPeerTlsServeResult> application;

    bool operator==(const SyncReplicaPeerTlsServerResult&) const = default;
};

// Production accepted-session dispatcher for a combined peer deployment. It
// shares the exact listener, TLS handshake, anchored membership, peer
// authorization, and shutdown owner used by one-shot file delivery, then reads
// one first application record and dispatches it to file delivery or bounded
// reconciliation without constructing a second SSL/socket owner.
[[nodiscard]] SyncReplicaPeerTlsServerResult
serve_one_sync_replica_peer_tls_session_or_throw(
    SyncReplicaFileDeliveryService& file_service,
    SyncReplicaReconciliationService& reconciliation_service,
    SyncReplicaFileTlsServerListener& listener,
    SyncReplicaFileTlsServerContext server_context,
    SyncReplicaTlsAnchoredMembershipAuthority membership,
    const SyncReplicaFileTlsServerDeadlines& deadlines,
    std::uint64_t reconciliation_max_round_trips =
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips,
    const std::string& label = "sync replica peer TLS server session");

// The same authenticated application dispatcher over an already-owned exact
// nonblocking+CLOEXEC stream. This is the native-overlay ingress seam: a SAM
// STREAM ACCEPT socket can enter TLS directly without first being forwarded
// through a separately reachable local TCP listener. Ownership is consumed and
// the descriptor closes unconditionally at the end of this call.
[[nodiscard]] SyncReplicaPeerTlsServerResult
serve_one_sync_replica_peer_tls_connected_stream_or_throw(
    SyncReplicaFileDeliveryService& file_service,
    SyncReplicaReconciliationService& reconciliation_service,
    SyncReplicaConnectedStream stream,
    SyncReplicaFileTlsServerContext server_context,
    SyncReplicaTlsAnchoredMembershipAuthority membership,
    const SyncReplicaFileTlsServerDeadlines& deadlines,
    std::uint64_t reconciliation_max_round_trips =
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips,
    const std::string& label =
        "sync replica peer TLS connected-stream session");

}  // namespace anonsync
