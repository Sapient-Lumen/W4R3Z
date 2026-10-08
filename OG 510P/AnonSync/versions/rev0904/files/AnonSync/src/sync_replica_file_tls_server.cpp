#include "sync_replica_file_tls_server.hpp"

#include "sync_stream_socket_deadline_poll.hpp"

#include <cerrno>
#include <chrono>
#include <memory>
#include <stdexcept>
#include <string>
#include <utility>

#include <openssl/err.h>

#ifdef __linux__
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

using SslOwner = std::unique_ptr<SSL, decltype(&SSL_free)>;

#ifdef __linux__
class AcceptedSocketOwner final {
public:
    explicit AcceptedSocketOwner(int descriptor) noexcept
        : descriptor_(descriptor) {}
    AcceptedSocketOwner(const AcceptedSocketOwner&) = delete;
    AcceptedSocketOwner& operator=(const AcceptedSocketOwner&) = delete;
    AcceptedSocketOwner(AcceptedSocketOwner&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    AcceptedSocketOwner& operator=(AcceptedSocketOwner&& other) noexcept {
        if (this != &other) {
            close_noexcept();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }
    ~AcceptedSocketOwner() noexcept { close_noexcept(); }

    [[nodiscard]] int descriptor() const noexcept { return descriptor_; }

private:
    void close_noexcept() noexcept {
        if (descriptor_ >= 0) {
            const int descriptor = std::exchange(descriptor_, -1);
            // On Linux, retrying close() after EINTR can close a descriptor
            // that another thread already reused. Ownership ends after this
            // single call regardless of its diagnostic result.
            (void)::close(descriptor);
        }
    }

    int descriptor_ = -1;
};
#endif

[[nodiscard]] std::string diagnostic_prefix(
    std::string_view label,
    int descriptor) {
    return std::string(label) + " descriptor " + std::to_string(descriptor);
}

void require_listener_accepting_or_throw(
    const SyncSocketLifetimeIdentity& socket,
    std::string_view label) {
#ifdef __linux__
    reprove_sync_stream_socket_lifetime_or_throw(socket, label);
    int accepting = 0;
    socklen_t accepting_bytes = sizeof(accepting);
    errno = 0;
    if (::getsockopt(
            socket.descriptor(), SOL_SOCKET, SO_ACCEPTCONN,
            &accepting, &accepting_bytes) != 0 ||
        accepting_bytes != sizeof(accepting)) {
        throw std::runtime_error(
            diagnostic_prefix(label, socket.descriptor()) +
            " could not prove SO_ACCEPTCONN (errno " +
            std::to_string(errno) + ")");
    }
    reprove_sync_stream_socket_lifetime_or_throw(socket, label);
    if (accepting != 1) {
        throw std::invalid_argument(
            diagnostic_prefix(label, socket.descriptor()) +
            " is not a listening socket");
    }
#else
    (void)socket;
    throw std::runtime_error(
        std::string(label) +
        " cannot prove listening-socket authority on this platform");
#endif
}

}  // namespace

struct SyncReplicaFileTlsServerContextAccess final {
    static SSL_CTX* require_or_throw(
        const SyncReplicaFileTlsServerContext& context,
        std::string_view label) {
        if (context.context_ == nullptr) {
            throw std::logic_error(
                std::string(label) + " server context reference is inactive");
        }
        return context.context_;
    }
};

struct SyncReplicaFileTlsServerListenerAccess final {
    static const SyncSocketLifetimeIdentity& require_or_throw(
        SyncReplicaFileTlsServerListener& listener,
        std::string_view label) {
        // A moved-from capability is ordinary local misuse, not evidence that a
        // live capability crossed a process boundary. Check activity before the
        // fail-stop process-incarnation guard; an inherited active capability
        // still retains socket_ and therefore reaches the fail-stop check.
        if (!listener.socket_.has_value()) {
            throw std::logic_error(
                std::string(label) + " listener capability is inactive");
        }
        require_sync_process_incarnation_or_fail_stop(
            listener.process_, label);
        require_sync_thread_incarnation_or_throw(listener.thread_, label);
        const auto& socket = *listener.socket_;
        require_sync_stream_socket_nonblocking_or_throw(socket, label);
        require_sync_stream_socket_close_on_exec_or_throw(socket, label);
        require_listener_accepting_or_throw(socket, label);
        return socket;
    }
};

namespace {

#ifdef __linux__
[[nodiscard]] bool retryable_accept_error(int error) noexcept {
    return error == EINTR || error == EAGAIN || error == EWOULDBLOCK ||
           error == ECONNABORTED || error == EPROTO || error == ENETDOWN ||
           error == ENOPROTOOPT || error == EHOSTDOWN || error == ENONET ||
           error == EHOSTUNREACH || error == EOPNOTSUPP ||
           error == ENETUNREACH;
}

struct AcceptOutcome final {
    std::optional<AcceptedSocketOwner> socket;
    std::uint64_t attempts = 0U;
};

[[nodiscard]] AcceptOutcome accept_one_until_or_throw(
    SyncReplicaFileTlsServerListener& listener,
    std::chrono::steady_clock::time_point deadline,
    const std::string& label) {
    AcceptOutcome outcome;
    for (;;) {
        const auto& listener_socket =
            SyncReplicaFileTlsServerListenerAccess::require_or_throw(
                listener, label);
        // The caller supplies an absolute cutpoint. Pre-accept authority
        // reproof can legitimately consume the remaining budget, so expiry
        // before the first accept4() is represented truthfully by zero
        // attempts rather than by a fabricated syscall.
        if (std::chrono::steady_clock::now() >= deadline) return outcome;

        ++outcome.attempts;
        errno = 0;
        const int accepted = ::accept4(
            listener_socket.descriptor(), nullptr, nullptr,
            SOCK_NONBLOCK | SOCK_CLOEXEC);
        const int accept_errno = errno;
        if (accepted >= 0) {
            AcceptedSocketOwner child(accepted);
            // The listener cannot silently change identity or accepting policy
            // across accept. Raw descriptor mutation remains externally
            // serialized, but this catches accidental ABA around the syscall.
            (void)SyncReplicaFileTlsServerListenerAccess::require_or_throw(
                listener, label + " post-accept listener reproof");
            outcome.socket.emplace(std::move(child));
            return outcome;
        }
        if (!retryable_accept_error(accept_errno)) {
            throw std::runtime_error(
                label + " accept4 failed (errno " +
                std::to_string(accept_errno) + ")");
        }
        if (accept_errno != EAGAIN && accept_errno != EWOULDBLOCK) {
            continue;
        }

        const auto poll_result = poll_sync_stream_socket_until_or_throw(
            listener_socket, SyncStreamSocketPollReadiness::Readable,
            deadline, label + " readiness");
        if (poll_result ==
            SyncStreamSocketDeadlinePollResult::DeadlineExpired) {
            return outcome;
        }
    }
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

[[nodiscard]] HandshakeOutcome drive_server_handshake_until_or_throw(
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
        if (std::chrono::steady_clock::now() >= deadline) {
            outcome.terminal = HandshakeOutcome::Terminal::DeadlineExpired;
            return outcome;
        }

        ERR_clear_error();
        ++outcome.attempts;
        const int result = SSL_accept(ssl);
        if (result == 1) {
            require_sync_stream_socket_nonblocking_or_throw(socket, label);
            outcome.terminal = HandshakeOutcome::Terminal::Complete;
            outcome.ssl_error.reset();
            return outcome;
        }
        // OpenSSL requires SSL_get_error on this same thread with no intervening
        // OpenSSL call. Socket reproof and diagnostics happen only afterward.
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
    SyncReplicaFileTlsServerShutdownDisposition disposition =
        SyncReplicaFileTlsServerShutdownDisposition::NotAttempted;
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
        if (std::chrono::steady_clock::now() >= deadline) {
            outcome.disposition =
                SyncReplicaFileTlsServerShutdownDisposition::DeadlineExpired;
            return outcome;
        }

        ERR_clear_error();
        ++outcome.attempts;
        const int result = SSL_shutdown(ssl);
        if (result == 1) {
            outcome.disposition =
                SyncReplicaFileTlsServerShutdownDisposition::Complete;
            outcome.ssl_error.reset();
            return outcome;
        }
        if (result == 0) {
            // For TLS, OpenSSL documents this as local close_notify sent while
            // the peer response remains outstanding. SSL_get_error must not be
            // called for this non-error return.
            outcome.disposition =
                SyncReplicaFileTlsServerShutdownDisposition::CloseNotifySent;
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
                SyncReplicaFileTlsServerShutdownDisposition::Failed;
            return outcome;
        }

        const auto poll_result = poll_sync_stream_socket_until_or_throw(
            socket, readiness, deadline, label + " readiness");
        if (poll_result ==
            SyncStreamSocketDeadlinePollResult::DeadlineExpired) {
            outcome.disposition =
                SyncReplicaFileTlsServerShutdownDisposition::DeadlineExpired;
            return outcome;
        }
    }
}

[[nodiscard]] SyncReplicaFileTlsServerDisposition map_receive_disposition(
    SyncReplicaFileTlsReceiveDisposition disposition) {
    switch (disposition) {
        case SyncReplicaFileTlsReceiveDisposition::PeerClosed:
            return SyncReplicaFileTlsServerDisposition::PeerClosed;
        case SyncReplicaFileTlsReceiveDisposition::RequestDeadlineExpired:
            return SyncReplicaFileTlsServerDisposition::RequestDeadlineExpired;
        case SyncReplicaFileTlsReceiveDisposition::ReceiptDeadlineExpired:
            return SyncReplicaFileTlsServerDisposition::ReceiptDeadlineExpired;
        case SyncReplicaFileTlsReceiveDisposition::ReceiptSent:
            return SyncReplicaFileTlsServerDisposition::ReceiptSent;
    }
    throw std::logic_error(
        "sync replica file TLS server observed unknown receive disposition");
}

}  // namespace

SyncReplicaFileTlsServerContext::SyncReplicaFileTlsServerContext(
    SyncReplicaFileTlsServerContext&& other) noexcept
    : context_(std::exchange(other.context_, nullptr)) {}

SyncReplicaFileTlsServerContext&
SyncReplicaFileTlsServerContext::operator=(
    SyncReplicaFileTlsServerContext&& other) noexcept {
    if (this != &other) {
        if (context_ != nullptr) SSL_CTX_free(context_);
        context_ = std::exchange(other.context_, nullptr);
    }
    return *this;
}

SyncReplicaFileTlsServerContext::~SyncReplicaFileTlsServerContext() noexcept {
    if (context_ != nullptr) SSL_CTX_free(context_);
}

SyncReplicaFileTlsServerContext
retain_sync_replica_file_tls_server_context_or_throw(
    SSL_CTX* context,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS server context label must not be empty");
    }
    if (context == nullptr) {
        throw std::invalid_argument(label + " SSL context is null");
    }
    ERR_clear_error();
    if (SSL_CTX_up_ref(context) != 1) {
        throw std::runtime_error(label + " could not retain SSL context");
    }
    return SyncReplicaFileTlsServerContext(context);
}

SyncReplicaFileTlsServerListener::SyncReplicaFileTlsServerListener(
    SyncSocketLifetimeIdentity socket,
    SyncProcessIncarnation process,
    SyncThreadIncarnation thread) noexcept
    : socket_(std::move(socket)), process_(process), thread_(thread) {}

SyncReplicaFileTlsServerListener::SyncReplicaFileTlsServerListener(
    SyncReplicaFileTlsServerListener&& other) noexcept
    : socket_(std::move(other.socket_)),
      process_(other.process_),
      thread_(other.thread_) {
    other.socket_.reset();
    other.process_ = {};
    other.thread_ = {};
}

SyncReplicaFileTlsServerListener&
SyncReplicaFileTlsServerListener::operator=(
    SyncReplicaFileTlsServerListener&& other) noexcept {
    if (this != &other) {
        socket_ = std::move(other.socket_);
        process_ = other.process_;
        thread_ = other.thread_;
        other.socket_.reset();
        other.process_ = {};
        other.thread_ = {};
    }
    return *this;
}

SyncReplicaFileTlsServerListener
observe_sync_replica_file_tls_server_listener_or_throw(
    int descriptor,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS server listener label must not be empty");
    }
    SyncSocketLifetimeIdentity socket =
        observe_sync_stream_socket_lifetime_or_throw(descriptor, label);
    require_sync_stream_socket_nonblocking_or_throw(socket, label);
    require_sync_stream_socket_close_on_exec_or_throw(socket, label);
    require_listener_accepting_or_throw(socket, label);
    const SyncProcessIncarnation process =
        current_sync_process_incarnation_noexcept();
    const SyncThreadIncarnation thread =
        current_sync_thread_incarnation_noexcept();
    if (!process.valid() || !thread.valid()) {
        throw std::logic_error(
            label + " could not bind live process/thread authority");
    }
    return SyncReplicaFileTlsServerListener(
        std::move(socket), process, thread);
}

SyncReplicaFileTlsServerResult
serve_one_sync_replica_file_delivery_tls_session_or_throw(
    SyncReplicaFileDeliveryService& service,
    SyncReplicaFileTlsServerListener& listener,
    SyncReplicaFileTlsServerContext server_context,
    SyncReplicaTlsAnchoredMembershipAuthority membership,
    const SyncReplicaFileTlsServerDeadlines& deadlines,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS server session label must not be empty");
    }
    SSL_CTX* const server_context_handle =
        SyncReplicaFileTlsServerContextAccess::require_or_throw(
            server_context, label);
    if (!membership.active()) {
        throw std::invalid_argument(
            label + " membership authority is inactive");
    }
    const SyncReplicaTlsMembershipSnapshot& membership_snapshot =
        membership.snapshot();
    membership_snapshot.require_service_identity_or_throw(
        service.folder_id(), service.local_actor(),
        label + " membership pre-accept");

    SyncReplicaFileTlsServerResult result;
    result.membership_state_generation = membership.state_generation();
    result.membership_policy_epoch = membership_snapshot.policy_epoch();
    result.membership_entry_count = membership_snapshot.entry_count();
    result.membership_snapshot_digest = membership_snapshot.snapshot_digest();
    result.membership_previous_chain_digest =
        membership.previous_chain_digest();
    result.membership_chain_digest = membership.chain_digest();
    result.membership_durable_anchor_state_generation =
        membership.durable_anchor().state_generation;
    result.membership_durable_anchor_chain_digest =
        membership.durable_anchor().chain_digest;
    result.membership_durable_anchor_transition_sequence =
        membership.durable_transition_sequence();
    result.membership_durable_anchor_transition_digest =
        membership.durable_transition_digest();
#ifdef __linux__
    // Allocate connection-local OpenSSL state before accept authority is spent.
    // A provider or allocator failure therefore cannot consume one queued peer
    // without first establishing an SSL owner for the child.
    SslOwner ssl(SSL_new(server_context_handle), SSL_free);
    if (!ssl) {
        throw std::runtime_error(label + " could not allocate server SSL");
    }
    SSL_set_accept_state(ssl.get());

    AcceptOutcome accepted = accept_one_until_or_throw(
        listener, deadlines.accept, label + " accept");
    result.accept_attempts = accepted.attempts;
    if (!accepted.socket.has_value()) {
        result.disposition =
            SyncReplicaFileTlsServerDisposition::AcceptDeadlineExpired;
        return result;
    }
    result.accepted = true;

    const int accepted_descriptor = accepted.socket->descriptor();
    SyncSocketLifetimeIdentity accepted_identity =
        observe_sync_stream_socket_lifetime_or_throw(
            accepted_descriptor, label + " accepted socket");
    require_sync_stream_socket_nonblocking_or_throw(
        accepted_identity, label + " accepted socket");
    require_sync_stream_socket_close_on_exec_or_throw(
        accepted_identity, label + " accepted socket");
    result.accepted_socket_policy_verified = true;

    ERR_clear_error();
    if (SSL_set_fd(ssl.get(), accepted_descriptor) != 1) {
        throw std::runtime_error(
            label + " could not bind accepted socket to server SSL");
    }

    const HandshakeOutcome handshake =
        drive_server_handshake_until_or_throw(
            ssl.get(), accepted_identity, deadlines.handshake,
            label + " handshake");
    result.handshake_attempts = handshake.attempts;
    result.handshake_ssl_error = handshake.ssl_error;
    if (handshake.terminal ==
        HandshakeOutcome::Terminal::DeadlineExpired) {
        result.disposition =
            SyncReplicaFileTlsServerDisposition::HandshakeDeadlineExpired;
        return result;
    }
    if (handshake.terminal == HandshakeOutcome::Terminal::Rejected) {
        result.disposition =
            SyncReplicaFileTlsServerDisposition::HandshakeRejected;
        return result;
    }
    result.handshake_complete = true;
    require_sync_stream_socket_nonblocking_or_throw(
        accepted_identity, label + " post-handshake accepted socket");
    require_sync_stream_socket_close_on_exec_or_throw(
        accepted_identity, label + " post-handshake accepted socket");

    std::string peer_spki;
    try {
        peer_spki = sync_replica_tls_peer_spki_sha256_or_throw(
            ssl.get(), label + " authenticated peer profile");
    } catch (const std::runtime_error&) {
        // Profile/peer-evidence failures are remote authentication rejection.
        // Resource failures such as std::bad_alloc must still propagate as
        // local failures rather than being laundered into peer behavior.
        result.disposition =
            SyncReplicaFileTlsServerDisposition::HandshakeRejected;
        return result;
    }
    result.peer_spki_sha256 = peer_spki;
    std::optional<SyncReplicaActor> peer_actor =
        membership_snapshot.resolve_peer_or_throw(
            peer_spki, label + " immutable membership lookup");
    if (!peer_actor.has_value()) {
        result.disposition =
            SyncReplicaFileTlsServerDisposition::PeerUnauthorized;
        return result;
    }
    // Membership lookup is now a pure search over immutable shared state. Reprove
    // the original accepted lifetime and mutable descriptor policy before
    // retaining that authorization in an authenticated channel.
    require_sync_stream_socket_nonblocking_or_throw(
        accepted_identity, label + " post-membership accepted socket");
    require_sync_stream_socket_close_on_exec_or_throw(
        accepted_identity, label + " post-membership accepted socket");
    result.peer_actor = *peer_actor;

    {
        SyncReplicaTlsAuthenticatedChannel channel =
            authenticate_sync_replica_tls13_channel_or_throw(
                ssl.get(), {*peer_actor, peer_spki},
                label + " authenticated channel");
        SyncReplicaFileTlsReceiverSession receiver_session(
            service, std::move(channel), deadlines.request, deadlines.receipt,
            label + " receiver session");
        result.receive = receiver_session.run_or_throw();
        result.disposition =
            map_receive_disposition(result.receive->disposition);
    }

    if (result.disposition ==
        SyncReplicaFileTlsServerDisposition::ReceiptSent) {
        try {
            const ShutdownOutcome shutdown =
                drive_fast_shutdown_until_or_throw(
                    ssl.get(), accepted_identity, deadlines.shutdown,
                    label + " fast shutdown");
            result.shutdown_disposition = shutdown.disposition;
            result.shutdown_attempts = shutdown.attempts;
            result.shutdown_ssl_error = shutdown.ssl_error;
        } catch (...) {
            // Receipt completion is the application terminal cutpoint. A later
            // local reproof, poll, or shutdown failure cannot erase it or turn
            // cleanup into an exception-only ambiguity. Scope teardown still
            // closes the accepted descriptor unconditionally.
            result.shutdown_disposition =
                SyncReplicaFileTlsServerShutdownDisposition::Failed;
        }
    }
    return result;
#else
    (void)service;
    (void)listener;
    (void)deadlines;
    throw std::runtime_error(
        label + " requires Linux accept4 and exact socket lifetime authority");
#endif
}

}  // namespace anonsync
