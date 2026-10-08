#include "sync_replica_file_tls_client.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_file_tls_dispatch.hpp"
#include "sync_replica_tls_poll.hpp"
#include "sync_replica_tls_record_exchange.hpp"
#include "sync_socket_readiness_identity.hpp"
#include "sync_stream_socket_deadline_poll.hpp"

#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <openssl/err.h>

namespace anonsync {
namespace {

using SslOwner = std::unique_ptr<SSL, decltype(&SSL_free)>;


struct HandshakeOutcome final {
    enum class Terminal {
        Complete,
        DeadlineExpired,
        Rejected,
    } terminal = Terminal::Rejected;
    std::uint64_t attempts = 0U;
    std::optional<int> ssl_error;
};

[[nodiscard]] HandshakeOutcome drive_client_handshake_until_or_throw(
    SSL* ssl,
    const SyncSocketLifetimeIdentity& socket,
    std::chrono::steady_clock::time_point deadline,
    const std::string& label) {
    if (ssl == nullptr) {
        throw std::invalid_argument(label + " SSL handle is null");
    }
    HandshakeOutcome outcome;
    for (;;) {
        require_sync_stream_socket_nonblocking_or_throw(socket, label);
        require_sync_stream_socket_close_on_exec_or_throw(socket, label);
        if (std::chrono::steady_clock::now() >= deadline) {
            outcome.terminal = HandshakeOutcome::Terminal::DeadlineExpired;
            return outcome;
        }

        ERR_clear_error();
        ++outcome.attempts;
        const int result = SSL_connect(ssl);
        if (result == 1) {
            require_sync_stream_socket_nonblocking_or_throw(socket, label);
            require_sync_stream_socket_close_on_exec_or_throw(socket, label);
            outcome.terminal = HandshakeOutcome::Terminal::Complete;
            outcome.ssl_error.reset();
            return outcome;
        }
        // SSL_get_error must immediately follow this exact SSL_connect result
        // on the same thread, before socket reproof or any other OpenSSL call.
        const int ssl_error = SSL_get_error(ssl, result);
        outcome.ssl_error = ssl_error;

        SyncStreamSocketPollReadiness readiness =
            SyncStreamSocketPollReadiness::Readable;
        if (ssl_error == SSL_ERROR_WANT_READ) {
            readiness = SyncStreamSocketPollReadiness::Readable;
        } else if (ssl_error == SSL_ERROR_WANT_WRITE) {
            readiness = SyncStreamSocketPollReadiness::Writable;
        } else {
            outcome.terminal = HandshakeOutcome::Terminal::Rejected;
            return outcome;
        }

        const auto poll_result = poll_sync_stream_socket_until_or_throw(
            socket, readiness, deadline, label + " readiness");
        if (poll_result ==
            SyncStreamSocketDeadlinePollResult::DeadlineExpired) {
            outcome.terminal = HandshakeOutcome::Terminal::DeadlineExpired;
            return outcome;
        }
    }
}

struct ShutdownOutcome final {
    SyncReplicaFileTlsClientShutdownDisposition disposition =
        SyncReplicaFileTlsClientShutdownDisposition::NotAttempted;
    std::uint64_t attempts = 0U;
    std::optional<int> ssl_error;
};

[[nodiscard]] ShutdownOutcome drive_fast_shutdown_until_or_throw(
    SSL* ssl,
    const SyncSocketLifetimeIdentity& socket,
    std::chrono::steady_clock::time_point deadline,
    const std::string& label) {
    ShutdownOutcome outcome;
    for (;;) {
        require_sync_stream_socket_nonblocking_or_throw(socket, label);
        require_sync_stream_socket_close_on_exec_or_throw(socket, label);
        if (std::chrono::steady_clock::now() >= deadline) {
            outcome.disposition =
                SyncReplicaFileTlsClientShutdownDisposition::DeadlineExpired;
            return outcome;
        }

        ERR_clear_error();
        ++outcome.attempts;
        const int result = SSL_shutdown(ssl);
        if (result == 1) {
            outcome.disposition =
                SyncReplicaFileTlsClientShutdownDisposition::Complete;
            outcome.ssl_error.reset();
            return outcome;
        }
        if (result == 0) {
            outcome.disposition =
                SyncReplicaFileTlsClientShutdownDisposition::CloseNotifySent;
            outcome.ssl_error.reset();
            return outcome;
        }

        const int ssl_error = SSL_get_error(ssl, result);
        outcome.ssl_error = ssl_error;
        SyncStreamSocketPollReadiness readiness =
            SyncStreamSocketPollReadiness::Readable;
        if (ssl_error == SSL_ERROR_WANT_READ) {
            readiness = SyncStreamSocketPollReadiness::Readable;
        } else if (ssl_error == SSL_ERROR_WANT_WRITE) {
            readiness = SyncStreamSocketPollReadiness::Writable;
        } else {
            outcome.disposition =
                SyncReplicaFileTlsClientShutdownDisposition::Failed;
            return outcome;
        }

        const auto poll_result = poll_sync_stream_socket_until_or_throw(
            socket, readiness, deadline, label + " readiness");
        if (poll_result ==
            SyncStreamSocketDeadlinePollResult::DeadlineExpired) {
            outcome.disposition =
                SyncReplicaFileTlsClientShutdownDisposition::DeadlineExpired;
            return outcome;
        }
    }
}

[[nodiscard]] bool finish_request_until_or_throw(
    SyncReplicaFileTlsDispatchContinuation& continuation,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::chrono::steady_clock::time_point deadline,
    const std::string& poll_label,
    SyncReplicaFileTlsClientResult& result) {
    const auto observe_progress = [&] {
        result.request_frame_bytes = continuation.frame_bytes();
        result.request_body_bytes_written =
            continuation.body_bytes_written();
    };

    bool retry_pending = false;
    for (;;) {
        if (!retry_pending &&
            std::chrono::steady_clock::now() >= deadline) {
            observe_progress();
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            return false;
        }

        if (retry_pending) {
            switch (continuation.poll_and_advance_or_throw(
                deadline, poll_label)) {
                case SyncReplicaTlsRecordWritePollProgress::DeadlineExpired:
                    observe_progress();
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    return false;
                case SyncReplicaTlsRecordWritePollProgress::Progress:
                    observe_progress();
                    retry_pending = false;
                    break;
                case SyncReplicaTlsRecordWritePollProgress::WantRead:
                case SyncReplicaTlsRecordWritePollProgress::WantWrite:
                    observe_progress();
                    retry_pending = true;
                    break;
                case SyncReplicaTlsRecordWritePollProgress::Complete:
                    result.request_frame_bytes = continuation.frame_bytes();
                    result.request_body_bytes_written =
                        result.request_frame_bytes;
                    return true;
            }
            continue;
        }

        switch (continuation.advance_or_throw()) {
            case SyncReplicaTlsRecordWriteProgress::Progress:
                observe_progress();
                break;
            case SyncReplicaTlsRecordWriteProgress::WantRead:
            case SyncReplicaTlsRecordWriteProgress::WantWrite:
                observe_progress();
                retry_pending = true;
                break;
            case SyncReplicaTlsRecordWriteProgress::Complete:
                result.request_frame_bytes = continuation.frame_bytes();
                result.request_body_bytes_written = result.request_frame_bytes;
                return true;
        }
    }
}

void validate_expected_peer_or_throw(
    const SyncReplicaTlsPeerPolicy& expected_peer,
    const std::string& label) {
    if (!sync_id_is_valid(expected_peer.actor.device_id) ||
        expected_peer.actor.epoch == 0U) {
        throw std::invalid_argument(
            label + " expected peer actor is invalid");
    }
    if (!is_lowercase_sha256_hex(expected_peer.spki_sha256)) {
        throw std::invalid_argument(
            label + " expected peer SPKI is not lowercase SHA-256");
    }
}

}  // namespace

struct SyncReplicaFileTlsClientContextAccess final {
    static SSL_CTX* require_or_throw(
        const SyncReplicaFileTlsClientContext& context,
        std::string_view label) {
        if (context.context_ == nullptr) {
            throw std::logic_error(
                std::string(label) + " client context reference is inactive");
        }
        return context.context_;
    }
};

SyncReplicaFileTlsClientContext::SyncReplicaFileTlsClientContext(
    SyncReplicaFileTlsClientContext&& other) noexcept
    : context_(std::exchange(other.context_, nullptr)) {}

SyncReplicaFileTlsClientContext&
SyncReplicaFileTlsClientContext::operator=(
    SyncReplicaFileTlsClientContext&& other) noexcept {
    if (this != &other) {
        if (context_ != nullptr) SSL_CTX_free(context_);
        context_ = std::exchange(other.context_, nullptr);
    }
    return *this;
}

SyncReplicaFileTlsClientContext::~SyncReplicaFileTlsClientContext() noexcept {
    if (context_ != nullptr) SSL_CTX_free(context_);
}

SyncReplicaFileTlsClientContext
SyncReplicaFileTlsClientContext::retain_another_or_throw(
    const std::string& label) const {
    if (context_ == nullptr) {
        throw std::logic_error(label + " source context is inactive");
    }
    return retain_sync_replica_file_tls_client_context_or_throw(
        context_, label);
}

SyncReplicaFileTlsClientContext
retain_sync_replica_file_tls_client_context_or_throw(
    SSL_CTX* context,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS client context label must not be empty");
    }
    if (context == nullptr) {
        throw std::invalid_argument(label + " SSL context is null");
    }
    ERR_clear_error();
    if (SSL_CTX_up_ref(context) != 1) {
        throw std::runtime_error(label + " could not retain SSL context");
    }
    return SyncReplicaFileTlsClientContext(context);
}

std::string_view sync_replica_file_tls_client_disposition_name(
    SyncReplicaFileTlsClientDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaFileTlsClientDisposition::ConnectDeadlineExpired:
            return "connect_deadline_expired";
        case SyncReplicaFileTlsClientDisposition::ConnectFailed:
            return "connect_failed";
        case SyncReplicaFileTlsClientDisposition::RouteDeadlineExpired:
            return "route_deadline_expired";
        case SyncReplicaFileTlsClientDisposition::RouteRejected:
            return "route_rejected";
        case SyncReplicaFileTlsClientDisposition::HandshakeDeadlineExpired:
            return "handshake_deadline_expired";
        case SyncReplicaFileTlsClientDisposition::HandshakeRejected:
            return "handshake_rejected";
        case SyncReplicaFileTlsClientDisposition::PeerUnauthorized:
            return "peer_unauthorized";
        case SyncReplicaFileTlsClientDisposition::DispatchDeadlineExpired:
            return "dispatch_deadline_expired";
        case SyncReplicaFileTlsClientDisposition::NoReadyDelivery:
            return "no_ready_delivery";
        case SyncReplicaFileTlsClientDisposition::RequestDeadlineExpired:
            return "request_deadline_expired";
        case SyncReplicaFileTlsClientDisposition::PeerClosed:
            return "peer_closed";
        case SyncReplicaFileTlsClientDisposition::ReceiptDeadlineExpired:
            return "receipt_deadline_expired";
        case SyncReplicaFileTlsClientDisposition::ReceiptApplied:
            return "receipt_applied";
    }
    return "unknown";
}

std::string_view sync_replica_file_tls_client_shutdown_disposition_name(
    SyncReplicaFileTlsClientShutdownDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaFileTlsClientShutdownDisposition::NotAttempted:
            return "not_attempted";
        case SyncReplicaFileTlsClientShutdownDisposition::CloseNotifySent:
            return "close_notify_sent";
        case SyncReplicaFileTlsClientShutdownDisposition::Complete:
            return "complete";
        case SyncReplicaFileTlsClientShutdownDisposition::DeadlineExpired:
            return "deadline_expired";
        case SyncReplicaFileTlsClientShutdownDisposition::Failed:
            return "failed";
    }
    return "unknown";
}

std::string_view sync_replica_reconciliation_tls_client_disposition_name(
    SyncReplicaReconciliationTlsClientDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaReconciliationTlsClientDisposition::
            ConnectDeadlineExpired:
            return "connect_deadline_expired";
        case SyncReplicaReconciliationTlsClientDisposition::ConnectFailed:
            return "connect_failed";
        case SyncReplicaReconciliationTlsClientDisposition::
            RouteDeadlineExpired:
            return "route_deadline_expired";
        case SyncReplicaReconciliationTlsClientDisposition::RouteRejected:
            return "route_rejected";
        case SyncReplicaReconciliationTlsClientDisposition::
            HandshakeDeadlineExpired:
            return "handshake_deadline_expired";
        case SyncReplicaReconciliationTlsClientDisposition::HandshakeRejected:
            return "handshake_rejected";
        case SyncReplicaReconciliationTlsClientDisposition::PeerUnauthorized:
            return "peer_unauthorized";
        case SyncReplicaReconciliationTlsClientDisposition::PullCompleted:
            return "pull_completed";
    }
    return "unknown";
}

#if !defined(_WIN32)
namespace {

template <typename Result, typename Disposition, typename Application>
Result run_authenticated_client_session_or_throw(
    SyncReplicaFileTlsClientContext client_context,
    SyncReplicaStreamConnector& connector,
    const SyncReplicaTlsPeerPolicy& expected_peer,
    std::chrono::steady_clock::time_point connect_deadline,
    std::chrono::steady_clock::time_point handshake_deadline,
    std::chrono::steady_clock::time_point shutdown_deadline,
    Disposition connect_deadline_expired,
    Disposition connect_failed,
    Disposition route_deadline_expired,
    Disposition route_rejected,
    Disposition handshake_deadline_expired,
    Disposition handshake_rejected,
    Disposition peer_unauthorized,
    Application&& application,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS client session label must not be empty");
    }
    SSL_CTX* const client_context_handle =
        SyncReplicaFileTlsClientContextAccess::require_or_throw(
            client_context, label);
    validate_expected_peer_or_throw(expected_peer, label);

#ifdef __linux__
    Result result;
    result.stream_connect.route_kind = connector.route_kind();
    if (std::chrono::steady_clock::now() >= connect_deadline) {
        result.disposition = connect_deadline_expired;
        return result;
    }

    SslOwner ssl(SSL_new(client_context_handle), SSL_free);
    if (!ssl) {
        throw std::runtime_error(label + " could not allocate client SSL");
    }
    SSL_set_connect_state(ssl.get());

    SyncReplicaStreamConnectOutcome connected =
        connector.connect_until_or_throw(connect_deadline);
    result.stream_connect = connected.report;
    result.socket_created = connected.report.data_socket_created;
    result.socket_policy_verified =
        connected.report.data_socket_policy_verified;
    result.connect_attempts = connected.report.numeric_connect_attempts;
    result.connect_error = connected.report.numeric_connect_error;

    if (connected.report.disposition ==
        SyncReplicaStreamConnectDisposition::DeadlineExpired) {
        result.disposition =
            connected.report.terminal_stage ==
                    SyncReplicaStreamRouteStage::NumericConnect
                ? connect_deadline_expired
                : route_deadline_expired;
        return result;
    }
    if (connected.report.disposition ==
        SyncReplicaStreamConnectDisposition::NumericConnectFailed) {
        result.disposition = connect_failed;
        return result;
    }
    if (connected.report.disposition ==
        SyncReplicaStreamConnectDisposition::RouteRejected) {
        result.disposition = route_rejected;
        return result;
    }
    if (!connected.stream.has_value()) {
        throw std::logic_error(
            label + " connected route omitted data-stream ownership");
    }
    SyncReplicaConnectedStream socket = std::move(*connected.stream);
    const SyncSocketLifetimeIdentity& socket_identity =
        socket.socket_identity_or_throw(label + " routed socket");
    require_sync_stream_socket_nonblocking_or_throw(
        socket_identity, label + " routed socket");
    require_sync_stream_socket_close_on_exec_or_throw(
        socket_identity, label + " routed socket");
    result.connected = true;

    ERR_clear_error();
    if (SSL_set_fd(ssl.get(), socket.descriptor()) != 1) {
        throw std::runtime_error(
            label + " could not bind connected socket to client SSL");
    }

    const HandshakeOutcome handshake = drive_client_handshake_until_or_throw(
        ssl.get(), socket_identity, handshake_deadline,
        label + " handshake");
    result.handshake_attempts = handshake.attempts;
    result.handshake_ssl_error = handshake.ssl_error;
    if (handshake.terminal == HandshakeOutcome::Terminal::DeadlineExpired) {
        result.disposition = handshake_deadline_expired;
        return result;
    }
    if (handshake.terminal == HandshakeOutcome::Terminal::Rejected) {
        result.disposition = handshake_rejected;
        return result;
    }
    result.handshake_complete = true;

    std::string peer_spki;
    try {
        peer_spki = sync_replica_tls_peer_spki_sha256_or_throw(
            ssl.get(), label + " authenticated peer profile");
    } catch (const std::runtime_error&) {
        result.disposition = handshake_rejected;
        return result;
    }
    result.peer_spki_sha256 = peer_spki;
    if (peer_spki != expected_peer.spki_sha256) {
        result.disposition = peer_unauthorized;
        return result;
    }

    bool application_terminal = false;
    {
        SyncReplicaTlsAuthenticatedChannel channel =
            authenticate_sync_replica_tls13_channel_or_throw(
                ssl.get(), expected_peer,
                label + " authenticated channel");
        result.peer_authenticated = true;
        result.peer_actor = expected_peer.actor;
        application_terminal = std::forward<Application>(application)(
            channel, result);
    }

    if (application_terminal) {
        try {
            const ShutdownOutcome shutdown = drive_fast_shutdown_until_or_throw(
                ssl.get(), socket_identity, shutdown_deadline,
                label + " fast shutdown");
            result.shutdown_disposition = shutdown.disposition;
            result.shutdown_attempts = shutdown.attempts;
            result.shutdown_ssl_error = shutdown.ssl_error;
        } catch (...) {
            result.shutdown_disposition =
                SyncReplicaFileTlsClientShutdownDisposition::Failed;
        }
    }
    return result;
#else
    (void)connector;
    (void)connect_deadline;
    (void)handshake_deadline;
    (void)shutdown_deadline;
    (void)connect_deadline_expired;
    (void)connect_failed;
    (void)route_deadline_expired;
    (void)route_rejected;
    (void)handshake_deadline_expired;
    (void)handshake_rejected;
    (void)peer_unauthorized;
    (void)application;
    throw std::runtime_error(
        label + " requires Linux exact nonblocking socket authority");
#endif
}

[[nodiscard]] bool reconciliation_pull_allows_fast_shutdown(
    SyncReplicaReconciliationTlsPullDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaReconciliationTlsPullDisposition::Complete:
        case SyncReplicaReconciliationTlsPullDisposition::
            RoundTripLimitReached:
        case SyncReplicaReconciliationTlsPullDisposition::
            SourceChangedLimitReached:
        case SyncReplicaReconciliationTlsPullDisposition::
            SourcePayloadUnavailable:
        case SyncReplicaReconciliationTlsPullDisposition::
            SourcePayloadPreparing:
        case SyncReplicaReconciliationTlsPullDisposition::
            ReceiverCapacityBlocked:
            return true;
        case SyncReplicaReconciliationTlsPullDisposition::
            RequestDeadlineExpired:
        case SyncReplicaReconciliationTlsPullDisposition::
            ResponseDeadlineExpired:
        case SyncReplicaReconciliationTlsPullDisposition::PeerClosed:
            return false;
    }
    return false;
}

}  // namespace

SyncReplicaFileTlsClientResult
send_one_sync_replica_file_delivery_tls_session_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot,
    SyncReplicaFileTlsClientContext client_context,
    SyncReplicaStreamConnector& connector,
    const SyncReplicaTlsPeerPolicy& expected_peer,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFileTlsClientDeadlines& deadlines,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS client session label must not be empty");
    }
    if (!sync_id_is_valid(worker_id)) {
        throw std::invalid_argument(label + " worker_id is invalid");
    }
    if (lease_seconds == 0U ||
        lease_seconds > kSyncReplicaOutboxMaxLeaseSeconds) {
        throw std::invalid_argument(
            label + " lease_seconds is outside the supported range");
    }

#ifdef __linux__
    // Local availability and folder identity are proved before a remote socket
    // can consume work. The service repeats exact selection/reproof inside its
    // claim transaction; this early pass only prevents avoidable network churn.
    payload_snapshot.require_folder_or_throw(
        service.folder_id(), label + " payload snapshot");
    payload_snapshot.preflight_or_throw(label + " payload preflight");

    return run_authenticated_client_session_or_throw<
        SyncReplicaFileTlsClientResult>(
        std::move(client_context), connector, expected_peer,
        deadlines.connect, deadlines.handshake, deadlines.shutdown,
        SyncReplicaFileTlsClientDisposition::ConnectDeadlineExpired,
        SyncReplicaFileTlsClientDisposition::ConnectFailed,
        SyncReplicaFileTlsClientDisposition::RouteDeadlineExpired,
        SyncReplicaFileTlsClientDisposition::RouteRejected,
        SyncReplicaFileTlsClientDisposition::HandshakeDeadlineExpired,
        SyncReplicaFileTlsClientDisposition::HandshakeRejected,
        SyncReplicaFileTlsClientDisposition::PeerUnauthorized,
        [&](const SyncReplicaTlsAuthenticatedChannel& channel,
            SyncReplicaFileTlsClientResult& result) {
            // Handshake and peer-profile work can consume the request budget.
            // Re-observe the absolute request-admission deadline immediately
            // before the first durable claim.
            if (std::chrono::steady_clock::now() >= deadlines.request) {
                result.disposition = SyncReplicaFileTlsClientDisposition::
                    DispatchDeadlineExpired;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return true;
            }

            std::optional<SyncReplicaFileTlsDispatchContinuation> dispatch;
            try {
                dispatch = claim_and_begin_next_file_delivery_over_tls_or_throw(
                    service, channel, std::move(worker_id), lease_seconds,
                    payload_snapshot, label + " request dispatch");
            } catch (...) {
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                throw;
            }

            if (!dispatch.has_value()) {
                result.disposition =
                    SyncReplicaFileTlsClientDisposition::NoReadyDelivery;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return true;
            }

            const SyncReplicaOutboundFileDelivery& outbound =
                dispatch->outbound_or_throw();
            result.operation_id =
                outbound.request.evidence_request.operation.operation_id;
            result.claim_id = outbound.claim.intent.lease.claim_id;
            result.request_digest = outbound.request_digest;
            result.request_prefix_bytes_written =
                kSyncReplicaTlsRecordPrefixBytes;
            result.request_frame_bytes = dispatch->frame_bytes();
            result.request_body_bytes_written =
                dispatch->body_bytes_written();

            const bool request_complete = [&] {
                try {
                    return finish_request_until_or_throw(
                        *dispatch, channel, deadlines.request,
                        label + " request poll", result);
                } catch (...) {
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    throw;
                }
            }();
            if (!request_complete) {
                result.disposition = SyncReplicaFileTlsClientDisposition::
                    RequestDeadlineExpired;
                return false;
            }

            SyncReplicaTlsRecordReadUntilResult receipt = [&] {
                try {
                    return read_sync_replica_tls_record_until_or_throw(
                        channel, service.max_receipt_frame_bytes(),
                        deadlines.receipt, label + " receipt");
                } catch (...) {
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    throw;
                }
            }();
            result.receipt_prefix_bytes_received =
                receipt.prefix_bytes_received;
            result.receipt_frame_bytes = receipt.frame_bytes;
            result.receipt_body_bytes_received = receipt.body_bytes_received;
            if (receipt.disposition ==
                SyncReplicaTlsRecordReadUntilDisposition::PeerClosed) {
                result.disposition =
                    SyncReplicaFileTlsClientDisposition::PeerClosed;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return false;
            }
            if (receipt.disposition ==
                SyncReplicaTlsRecordReadUntilDisposition::DeadlineExpired) {
                result.disposition = SyncReplicaFileTlsClientDisposition::
                    ReceiptDeadlineExpired;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return false;
            }

            try {
                result.receipt_apply_result = service.apply_receipt_or_throw(
                    channel.delivery_authority(), outbound.request,
                    receipt.frame);
            } catch (...) {
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                throw;
            }
            result.disposition =
                SyncReplicaFileTlsClientDisposition::ReceiptApplied;
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            return true;
        },
        label);
#else
    (void)service;
    (void)payload_snapshot;
    (void)client_context;
    (void)connector;
    (void)expected_peer;
    (void)deadlines;
    throw std::runtime_error(
        label + " requires Linux exact nonblocking socket authority");
#endif
}

SyncReplicaFileTlsClientResult
send_one_sync_replica_file_delivery_tls_session_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot,
    SyncReplicaFileTlsClientContext client_context,
    const SyncReplicaFileTlsClientEndpoint& endpoint,
    const SyncReplicaTlsPeerPolicy& expected_peer,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFileTlsClientDeadlines& deadlines,
    const std::string& label) {
    SyncReplicaStreamConnector connector(
        SyncReplicaDirectTcpRoute{SyncReplicaNumericStreamEndpoint{
            endpoint.numeric_address, endpoint.port}},
        label + " direct connector");
    return send_one_sync_replica_file_delivery_tls_session_or_throw(
        service, payload_snapshot, std::move(client_context), connector,
        expected_peer, std::move(worker_id), lease_seconds, deadlines, label);
}

SyncReplicaReconciliationTlsClientResult
pull_sync_replica_reconciliation_tls_session_or_throw(
    SyncReplicaReconciliationService& service,
    SyncReplicaFileTlsClientContext client_context,
    SyncReplicaStreamConnector& connector,
    const SyncReplicaTlsPeerPolicy& expected_peer,
    SyncReplicaReconciliationTlsPullOptions options,
    const SyncReplicaReconciliationTlsClientDeadlines& deadlines,
    const std::string& label) {
    options.deadline = deadlines.application;
    return run_authenticated_client_session_or_throw<
        SyncReplicaReconciliationTlsClientResult>(
        std::move(client_context), connector, expected_peer,
        deadlines.connect, deadlines.handshake, deadlines.shutdown,
        SyncReplicaReconciliationTlsClientDisposition::
            ConnectDeadlineExpired,
        SyncReplicaReconciliationTlsClientDisposition::ConnectFailed,
        SyncReplicaReconciliationTlsClientDisposition::RouteDeadlineExpired,
        SyncReplicaReconciliationTlsClientDisposition::RouteRejected,
        SyncReplicaReconciliationTlsClientDisposition::
            HandshakeDeadlineExpired,
        SyncReplicaReconciliationTlsClientDisposition::HandshakeRejected,
        SyncReplicaReconciliationTlsClientDisposition::PeerUnauthorized,
        [&](const SyncReplicaTlsAuthenticatedChannel& channel,
            SyncReplicaReconciliationTlsClientResult& result) {
            result.pull.emplace(
                pull_sync_replica_reconciliation_over_tls_or_throw(
                    service, channel, std::move(options),
                    label + " bounded pull"));
            result.disposition =
                SyncReplicaReconciliationTlsClientDisposition::PullCompleted;
            return reconciliation_pull_allows_fast_shutdown(
                result.pull->disposition);
        },
        label);
}
#endif

}  // namespace anonsync
