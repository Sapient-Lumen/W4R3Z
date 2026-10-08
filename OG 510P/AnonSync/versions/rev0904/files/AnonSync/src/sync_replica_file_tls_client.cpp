#include "sync_replica_file_tls_client.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"
#include "sync_replica_file_tls_dispatch.hpp"
#include "sync_replica_tls_poll.hpp"
#include "sync_socket_readiness_identity.hpp"
#include "sync_stream_socket_deadline_poll.hpp"

#include <cerrno>
#include <chrono>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <openssl/err.h>

#ifdef __linux__
#include <arpa/inet.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

using SslOwner = std::unique_ptr<SSL, decltype(&SSL_free)>;

#ifdef __linux__
class ConnectedSocketOwner final {
public:
    explicit ConnectedSocketOwner(int descriptor) noexcept
        : descriptor_(descriptor) {}
    ConnectedSocketOwner(const ConnectedSocketOwner&) = delete;
    ConnectedSocketOwner& operator=(const ConnectedSocketOwner&) = delete;
    ConnectedSocketOwner(ConnectedSocketOwner&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    ConnectedSocketOwner& operator=(ConnectedSocketOwner&& other) noexcept {
        if (this != &other) {
            close_noexcept();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }
    ~ConnectedSocketOwner() noexcept { close_noexcept(); }

    [[nodiscard]] int descriptor() const noexcept { return descriptor_; }

private:
    void close_noexcept() noexcept {
        if (descriptor_ >= 0) {
            const int descriptor = std::exchange(descriptor_, -1);
            // Linux close() ownership ends after one call. Retrying after EINTR
            // can close an unrelated descriptor that another thread reused.
            (void)::close(descriptor);
        }
    }

    int descriptor_ = -1;
};

struct ParsedEndpoint final {
    int family = AF_UNSPEC;
    sockaddr_storage address{};
    socklen_t address_bytes = 0U;
};

[[nodiscard]] ParsedEndpoint parse_numeric_endpoint_or_throw(
    const SyncReplicaFileTlsClientEndpoint& endpoint,
    const std::string& label) {
    if (endpoint.numeric_address.empty()) {
        throw std::invalid_argument(label + " numeric address is empty");
    }
    if (endpoint.port == 0U) {
        throw std::invalid_argument(label + " port must be nonzero");
    }

    ParsedEndpoint parsed;
    sockaddr_in ipv4{};
    ipv4.sin_family = AF_INET;
    ipv4.sin_port = htons(endpoint.port);
    const int ipv4_result = ::inet_pton(
        AF_INET, endpoint.numeric_address.c_str(), &ipv4.sin_addr);
    if (ipv4_result == 1) {
        parsed.family = AF_INET;
        std::memcpy(&parsed.address, &ipv4, sizeof(ipv4));
        parsed.address_bytes = sizeof(ipv4);
        return parsed;
    }
    if (ipv4_result < 0) {
        throw std::runtime_error(
            label + " could not parse IPv4 endpoint (errno " +
            std::to_string(errno) + ")");
    }

    sockaddr_in6 ipv6{};
    ipv6.sin6_family = AF_INET6;
    ipv6.sin6_port = htons(endpoint.port);
    const int ipv6_result = ::inet_pton(
        AF_INET6, endpoint.numeric_address.c_str(), &ipv6.sin6_addr);
    if (ipv6_result == 1) {
        parsed.family = AF_INET6;
        std::memcpy(&parsed.address, &ipv6, sizeof(ipv6));
        parsed.address_bytes = sizeof(ipv6);
        return parsed;
    }
    if (ipv6_result < 0) {
        throw std::runtime_error(
            label + " could not parse IPv6 endpoint (errno " +
            std::to_string(errno) + ")");
    }

    throw std::invalid_argument(
        label + " endpoint is not a numeric IPv4 or unscoped IPv6 address");
}

[[nodiscard]] bool connect_in_progress_error(int error) noexcept {
    return error == EINPROGRESS || error == EALREADY ||
           error == EWOULDBLOCK || error == EINTR;
}

struct ConnectOutcome final {
    enum class Terminal {
        Connected,
        DeadlineExpired,
        Failed,
    } terminal = Terminal::Failed;
    std::uint64_t attempts = 0U;
    std::optional<int> error;
};

[[nodiscard]] ConnectOutcome connect_until_or_throw(
    const SyncSocketLifetimeIdentity& socket,
    const ParsedEndpoint& endpoint,
    std::chrono::steady_clock::time_point deadline,
    const std::string& label) {
    ConnectOutcome outcome;
    require_sync_stream_socket_nonblocking_or_throw(socket, label);
    require_sync_stream_socket_close_on_exec_or_throw(socket, label);
    if (std::chrono::steady_clock::now() >= deadline) {
        outcome.terminal = ConnectOutcome::Terminal::DeadlineExpired;
        return outcome;
    }

    ++outcome.attempts;
    errno = 0;
    const int connected = ::connect(
        socket.descriptor(),
        reinterpret_cast<const sockaddr*>(&endpoint.address),
        endpoint.address_bytes);
    const int connect_errno = errno;
    if (connected == 0 ||
        (connected < 0 && connect_errno == EISCONN)) {
        require_sync_stream_socket_nonblocking_or_throw(socket, label);
        require_sync_stream_socket_close_on_exec_or_throw(socket, label);
        outcome.terminal = ConnectOutcome::Terminal::Connected;
        outcome.error.reset();
        return outcome;
    }
    if (!connect_in_progress_error(connect_errno)) {
        outcome.terminal = ConnectOutcome::Terminal::Failed;
        outcome.error = connect_errno;
        return outcome;
    }

    const auto readiness = poll_sync_stream_socket_until_or_throw(
        socket, SyncStreamSocketPollReadiness::Writable,
        deadline, label + " readiness");
    if (readiness ==
        SyncStreamSocketDeadlinePollResult::DeadlineExpired) {
        outcome.terminal = ConnectOutcome::Terminal::DeadlineExpired;
        return outcome;
    }

    int socket_error = 0;
    socklen_t socket_error_bytes = sizeof(socket_error);
    errno = 0;
    if (::getsockopt(
            socket.descriptor(), SOL_SOCKET, SO_ERROR,
            &socket_error, &socket_error_bytes) != 0 ||
        socket_error_bytes != sizeof(socket_error)) {
        throw std::runtime_error(
            label + " could not observe SO_ERROR (errno " +
            std::to_string(errno) + ")");
    }
    require_sync_stream_socket_nonblocking_or_throw(socket, label);
    require_sync_stream_socket_close_on_exec_or_throw(socket, label);
    if (socket_error == 0 || socket_error == EISCONN) {
        outcome.terminal = ConnectOutcome::Terminal::Connected;
        outcome.error.reset();
    } else {
        outcome.terminal = ConnectOutcome::Terminal::Failed;
        outcome.error = socket_error;
    }
    return outcome;
}
#endif

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

struct ReceiptReadOutcome final {
    enum class Terminal {
        Complete,
        PeerClosed,
        DeadlineExpired,
    } terminal = Terminal::DeadlineExpired;
    std::string frame;
    std::uint64_t prefix_bytes_received = 0U;
    std::uint64_t frame_bytes = 0U;
    std::uint64_t body_bytes_received = 0U;
};

[[nodiscard]] ReceiptReadOutcome read_receipt_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    const std::string& read_label,
    const std::string& poll_label) {
    ReceiptReadOutcome outcome;
    if (std::chrono::steady_clock::now() >= deadline) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return outcome;
    }

    auto reader = begin_sync_replica_tls_record_read_or_throw(
        channel, max_frame_bytes,
        SyncReplicaTlsRecordReadReadinessPolicy::RequireNonblockingSocket,
        read_label);
    bool retry_pending = false;
    for (;;) {
        if (!retry_pending &&
            std::chrono::steady_clock::now() >= deadline) {
            outcome.prefix_bytes_received = reader.prefix_bytes_received();
            outcome.frame_bytes = reader.frame_bytes();
            outcome.body_bytes_received = reader.body_bytes_received();
            if (outcome.prefix_bytes_received == 0U &&
                outcome.frame_bytes == 0U &&
                outcome.body_bytes_received == 0U) {
                discard_sync_replica_tls_authenticated_channel_noexcept(
                    channel);
            }
            return outcome;
        }

        if (retry_pending) {
            switch (poll_and_advance_sync_replica_tls_record_read_or_throw(
                reader, deadline, poll_label)) {
                case SyncReplicaTlsRecordReadPollProgress::DeadlineExpired:
                    outcome.prefix_bytes_received =
                        reader.prefix_bytes_received();
                    outcome.frame_bytes = reader.frame_bytes();
                    outcome.body_bytes_received =
                        reader.body_bytes_received();
                    return outcome;
                case SyncReplicaTlsRecordReadPollProgress::Progress:
                    retry_pending = false;
                    break;
                case SyncReplicaTlsRecordReadPollProgress::WantRead:
                case SyncReplicaTlsRecordReadPollProgress::WantWrite:
                    retry_pending = true;
                    break;
                case SyncReplicaTlsRecordReadPollProgress::Complete:
                    outcome.terminal = ReceiptReadOutcome::Terminal::Complete;
                    outcome.prefix_bytes_received =
                        kSyncReplicaTlsRecordPrefixBytes;
                    outcome.frame_bytes = reader.frame_bytes();
                    outcome.body_bytes_received = outcome.frame_bytes;
                    outcome.frame = reader.take_frame_or_throw();
                    return outcome;
                case SyncReplicaTlsRecordReadPollProgress::PeerClosed:
                    outcome.terminal = ReceiptReadOutcome::Terminal::PeerClosed;
                    return outcome;
            }
            continue;
        }

        switch (reader.advance_or_throw()) {
            case SyncReplicaTlsRecordReadProgress::Progress:
                break;
            case SyncReplicaTlsRecordReadProgress::WantRead:
            case SyncReplicaTlsRecordReadProgress::WantWrite:
                retry_pending = true;
                break;
            case SyncReplicaTlsRecordReadProgress::Complete:
                outcome.terminal = ReceiptReadOutcome::Terminal::Complete;
                outcome.prefix_bytes_received =
                    kSyncReplicaTlsRecordPrefixBytes;
                outcome.frame_bytes = reader.frame_bytes();
                outcome.body_bytes_received = outcome.frame_bytes;
                outcome.frame = reader.take_frame_or_throw();
                return outcome;
            case SyncReplicaTlsRecordReadProgress::PeerClosed:
                outcome.terminal = ReceiptReadOutcome::Terminal::PeerClosed;
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
        case SyncReplicaFileTlsClientDisposition::HandshakeDeadlineExpired:
            return "handshake_deadline_expired";
        case SyncReplicaFileTlsClientDisposition::HandshakeRejected:
            return "handshake_rejected";
        case SyncReplicaFileTlsClientDisposition::PeerUnauthorized:
            return "peer_unauthorized";
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

#if !defined(_WIN32)
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
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS client session label must not be empty");
    }
    SSL_CTX* const client_context_handle =
        SyncReplicaFileTlsClientContextAccess::require_or_throw(
            client_context, label);
    validate_expected_peer_or_throw(expected_peer, label);
    if (!sync_id_is_valid(worker_id)) {
        throw std::invalid_argument(label + " worker_id is invalid");
    }
    if (lease_seconds == 0U ||
        lease_seconds > kSyncReplicaOutboxMaxLeaseSeconds) {
        throw std::invalid_argument(
            label + " lease_seconds is outside the supported range");
    }

#ifdef __linux__
    const ParsedEndpoint parsed =
        parse_numeric_endpoint_or_throw(endpoint, label);

    // Local availability and folder identity are proved before a remote socket
    // can consume work. The service repeats exact selection/reproof inside its
    // claim transaction; this early pass only prevents avoidable network churn.
    payload_snapshot.require_folder_or_throw(
        service.folder_id(), label + " payload snapshot");
    payload_snapshot.preflight_or_throw(label + " payload preflight");

    SyncReplicaFileTlsClientResult result;
    if (std::chrono::steady_clock::now() >= deadlines.connect) {
        result.disposition =
            SyncReplicaFileTlsClientDisposition::ConnectDeadlineExpired;
        return result;
    }

    SslOwner ssl(SSL_new(client_context_handle), SSL_free);
    if (!ssl) {
        throw std::runtime_error(label + " could not allocate client SSL");
    }
    SSL_set_connect_state(ssl.get());

    const int raw_socket = ::socket(
        parsed.family, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (raw_socket < 0) {
        throw std::runtime_error(
            label + " could not create client socket (errno " +
            std::to_string(errno) + ")");
    }
    ConnectedSocketOwner socket(raw_socket);
    result.socket_created = true;
    SyncSocketLifetimeIdentity socket_identity =
        observe_sync_stream_socket_lifetime_or_throw(
            socket.descriptor(), label + " socket");
    require_sync_stream_socket_nonblocking_or_throw(
        socket_identity, label + " socket");
    require_sync_stream_socket_close_on_exec_or_throw(
        socket_identity, label + " socket");
    result.socket_policy_verified = true;

    const ConnectOutcome connected = connect_until_or_throw(
        socket_identity, parsed, deadlines.connect, label + " connect");
    result.connect_attempts = connected.attempts;
    result.connect_error = connected.error;
    if (connected.terminal ==
        ConnectOutcome::Terminal::DeadlineExpired) {
        result.disposition =
            SyncReplicaFileTlsClientDisposition::ConnectDeadlineExpired;
        return result;
    }
    if (connected.terminal == ConnectOutcome::Terminal::Failed) {
        result.disposition =
            SyncReplicaFileTlsClientDisposition::ConnectFailed;
        return result;
    }
    result.connected = true;

    ERR_clear_error();
    if (SSL_set_fd(ssl.get(), socket.descriptor()) != 1) {
        throw std::runtime_error(
            label + " could not bind connected socket to client SSL");
    }

    const HandshakeOutcome handshake = drive_client_handshake_until_or_throw(
        ssl.get(), socket_identity, deadlines.handshake,
        label + " handshake");
    result.handshake_attempts = handshake.attempts;
    result.handshake_ssl_error = handshake.ssl_error;
    if (handshake.terminal ==
        HandshakeOutcome::Terminal::DeadlineExpired) {
        result.disposition =
            SyncReplicaFileTlsClientDisposition::HandshakeDeadlineExpired;
        return result;
    }
    if (handshake.terminal == HandshakeOutcome::Terminal::Rejected) {
        result.disposition =
            SyncReplicaFileTlsClientDisposition::HandshakeRejected;
        return result;
    }
    result.handshake_complete = true;

    std::string peer_spki;
    try {
        peer_spki = sync_replica_tls_peer_spki_sha256_or_throw(
            ssl.get(), label + " authenticated peer profile");
    } catch (const std::runtime_error&) {
        result.disposition =
            SyncReplicaFileTlsClientDisposition::HandshakeRejected;
        return result;
    }
    result.peer_spki_sha256 = peer_spki;
    if (peer_spki != expected_peer.spki_sha256) {
        result.disposition =
            SyncReplicaFileTlsClientDisposition::PeerUnauthorized;
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

        std::optional<SyncReplicaFileTlsDispatchContinuation> dispatch;
        try {
            dispatch =
                claim_and_begin_next_file_delivery_over_tls_or_throw(
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
            application_terminal = true;
        } else {
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
            } else {
                ReceiptReadOutcome receipt = [&] {
                    try {
                        return read_receipt_until_or_throw(
                            channel, service.max_receipt_frame_bytes(),
                            deadlines.receipt, label + " receipt",
                            label + " receipt poll");
                    } catch (...) {
                        discard_sync_replica_tls_authenticated_channel_noexcept(
                            channel);
                        throw;
                    }
                }();
                result.receipt_prefix_bytes_received =
                    receipt.prefix_bytes_received;
                result.receipt_frame_bytes = receipt.frame_bytes;
                result.receipt_body_bytes_received =
                    receipt.body_bytes_received;
                if (receipt.terminal ==
                    ReceiptReadOutcome::Terminal::PeerClosed) {
                    result.disposition =
                        SyncReplicaFileTlsClientDisposition::PeerClosed;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                } else if (receipt.terminal ==
                           ReceiptReadOutcome::Terminal::DeadlineExpired) {
                    result.disposition = SyncReplicaFileTlsClientDisposition::
                        ReceiptDeadlineExpired;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                } else {
                    try {
                        result.receipt_apply_result =
                            service.apply_receipt_or_throw(
                                channel.delivery_authority(),
                                outbound.request, receipt.frame);
                    } catch (...) {
                        discard_sync_replica_tls_authenticated_channel_noexcept(
                            channel);
                        throw;
                    }
                    result.disposition =
                        SyncReplicaFileTlsClientDisposition::ReceiptApplied;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    application_terminal = true;
                }
            }
        }
    }

    if (application_terminal) {
        try {
            const ShutdownOutcome shutdown =
                drive_fast_shutdown_until_or_throw(
                    ssl.get(), socket_identity, deadlines.shutdown,
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
    (void)service;
    (void)payload_snapshot;
    (void)endpoint;
    (void)deadlines;
    throw std::runtime_error(
        label + " requires Linux exact nonblocking socket authority");
#endif
}
#endif

}  // namespace anonsync
