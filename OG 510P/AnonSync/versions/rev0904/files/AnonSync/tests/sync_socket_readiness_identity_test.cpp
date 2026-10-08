#include "sync_socket_readiness_identity.hpp"
#include "sync_stream_socket_deadline_poll.hpp"

#include <chrono>
#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

#ifdef __linux__
#include <fcntl.h>
#include <sys/socket.h>
#include <unistd.h>
#endif

namespace {

static_assert(
    !std::is_default_constructible_v<anonsync::SyncSocketLifetimeIdentity>);
static_assert(
    std::is_copy_constructible_v<anonsync::SyncSocketLifetimeIdentity>);
static_assert(
    std::is_nothrow_move_constructible_v<
        anonsync::SyncSocketLifetimeIdentity>);
static_assert(!std::is_aggregate_v<anonsync::SyncSocketLifetimeIdentity>);

struct TestState final {
    std::uint64_t passed = 0U;
    std::uint64_t failed = 0U;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }
};

template <typename Function>
void require_throws_containing(
    TestState& test,
    Function&& function,
    const std::string& expected,
    const std::string& label) {
    try {
        function();
        test.require(false, label + " (no exception)");
    } catch (const std::exception& error) {
        test.require(
            std::string(error.what()).find(expected) != std::string::npos,
            label + " (unexpected exception: " + error.what() + ")");
    }
}

#ifdef __linux__
class FileDescriptor final {
public:
    FileDescriptor() = default;
    explicit FileDescriptor(int value) noexcept : value_(value) {}
    ~FileDescriptor() noexcept {
        if (value_ >= 0) (void)::close(value_);
    }
    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;
    FileDescriptor(FileDescriptor&& other) noexcept
        : value_(std::exchange(other.value_, -1)) {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            if (value_ >= 0) (void)::close(value_);
            value_ = std::exchange(other.value_, -1);
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return value_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(value_, -1);
    }

private:
    int value_ = -1;
};

struct SocketPair final {
    FileDescriptor left;
    FileDescriptor right;
};

[[nodiscard]] SocketPair make_stream_socket_pair(bool nonblocking) {
    int descriptors[2]{-1, -1};
    int type = SOCK_STREAM | SOCK_CLOEXEC;
    if (nonblocking) type |= SOCK_NONBLOCK;
    if (::socketpair(AF_UNIX, type, 0, descriptors) != 0) {
        throw std::runtime_error("socket lifetime test could not create socketpair");
    }
    return {FileDescriptor(descriptors[0]), FileDescriptor(descriptors[1])};
}

void set_nonblocking(int descriptor, bool enabled) {
    const int flags = ::fcntl(descriptor, F_GETFL, 0);
    if (flags < 0 ||
        ::fcntl(
            descriptor, F_SETFL,
            enabled ? flags | O_NONBLOCK : flags & ~O_NONBLOCK) != 0) {
        throw std::runtime_error("socket lifetime test could not change O_NONBLOCK");
    }
}

void set_close_on_exec(int descriptor, bool enabled = true) {
    const int flags = ::fcntl(descriptor, F_GETFD, 0);
    if (flags < 0 ||
        ::fcntl(
            descriptor, F_SETFD,
            enabled ? flags | FD_CLOEXEC : flags & ~FD_CLOEXEC) != 0) {
        throw std::runtime_error("socket lifetime test could not change FD_CLOEXEC");
    }
}
#endif

void run_tests(TestState& test) {
#ifdef __linux__
    // Lifetime identity is independent from mutable readiness policy. A blocking
    // stream socket can be authenticated, while a strict event-loop frontier
    // rejects it until the same lifetime is made nonblocking.
    SocketPair primary = make_stream_socket_pair(false);
    const auto primary_identity =
        anonsync::observe_sync_stream_socket_lifetime_or_throw(
            primary.left.get(), "primary stream socket");
    test.require(
        primary_identity.descriptor() == primary.left.get(),
        "observation exposes only the advisory descriptor");

    anonsync::reprove_sync_stream_socket_lifetime_or_throw(
        primary_identity, "unchanged stream socket");
    test.require(true, "unchanged blocking socket lifetime reproves");
    require_throws_containing(
        test,
        [&] {
            anonsync::require_sync_stream_socket_nonblocking_or_throw(
                primary_identity, "blocking readiness policy");
        },
        "is not nonblocking",
        "readiness policy rejects a blocking authenticated lifetime");
    require_throws_containing(
        test,
        [&] {
            (void)anonsync::poll_sync_stream_socket_until_or_throw(
                primary_identity,
                anonsync::SyncStreamSocketPollReadiness::Readable,
                std::chrono::steady_clock::now() +
                    std::chrono::seconds(1),
                "blocking exact socket poll");
        },
        "is not nonblocking",
        "deadline poll rejects a blocking authenticated lifetime");

    set_nonblocking(primary.left.get(), true);
    anonsync::require_sync_stream_socket_nonblocking_or_throw(
        primary_identity, "enabled readiness policy");
    test.require(true, "same lifetime gains nonblocking readiness authority");

    anonsync::require_sync_stream_socket_close_on_exec_or_throw(
        primary_identity, "enabled close-on-exec policy");
    test.require(true, "same lifetime carries close-on-exec process hygiene");
    set_close_on_exec(primary.left.get(), false);
    anonsync::reprove_sync_stream_socket_lifetime_or_throw(
        primary_identity, "close-on-exec-independent lifetime");
    test.require(true, "clearing FD_CLOEXEC does not rewrite socket lifetime");
    require_throws_containing(
        test,
        [&] {
            anonsync::require_sync_stream_socket_close_on_exec_or_throw(
                primary_identity, "cleared close-on-exec policy");
        },
        "inheritable across exec",
        "close-on-exec policy rejects an inheritable authenticated lifetime");
    set_close_on_exec(primary.left.get(), true);

    test.require(
        anonsync::poll_sync_stream_socket_until_or_throw(
            primary_identity,
            anonsync::SyncStreamSocketPollReadiness::Readable,
            std::chrono::steady_clock::now(),
            "already-expired exact socket poll") ==
            anonsync::SyncStreamSocketDeadlinePollResult::DeadlineExpired,
        "already-expired exact socket poll does not issue hidden progress");
    const unsigned char readiness_byte = 0x5aU;
    if (::send(primary.right.get(), &readiness_byte, 1U, 0) != 1) {
        throw std::runtime_error("socket lifetime test could not seed readability");
    }
    test.require(
        anonsync::poll_sync_stream_socket_until_or_throw(
            primary_identity,
            anonsync::SyncStreamSocketPollReadiness::Readable,
            std::chrono::steady_clock::now() +
                std::chrono::seconds(1),
            "exact readable socket poll") ==
            anonsync::SyncStreamSocketDeadlinePollResult::Ready,
        "exact socket poll exposes advisory readability");
    unsigned char observed_byte = 0U;
    if (::recv(primary.left.get(), &observed_byte, 1U, 0) != 1 ||
        observed_byte != readiness_byte) {
        throw std::runtime_error("socket lifetime test lost readable byte");
    }
    test.require(
        anonsync::poll_sync_stream_socket_until_or_throw(
            primary_identity,
            anonsync::SyncStreamSocketPollReadiness::Writable,
            std::chrono::steady_clock::now() + std::chrono::seconds(1),
            "exact writable socket poll") ==
            anonsync::SyncStreamSocketDeadlinePollResult::Ready,
        "exact socket poll exposes advisory writability");

    SocketPair peer_closed = make_stream_socket_pair(true);
    const auto peer_closed_identity =
        anonsync::observe_sync_stream_socket_lifetime_or_throw(
            peer_closed.left.get(), "peer-closed stream socket");
    const int peer_descriptor = peer_closed.right.release();
    if (::close(peer_descriptor) != 0) {
        throw std::runtime_error(
            "socket lifetime test could not close peer fixture");
    }
    test.require(
        anonsync::poll_sync_stream_socket_until_or_throw(
            peer_closed_identity,
            anonsync::SyncStreamSocketPollReadiness::Readable,
            std::chrono::steady_clock::now() + std::chrono::seconds(1),
            "peer-closed exact socket poll") ==
            anonsync::SyncStreamSocketDeadlinePollResult::Ready,
        "peer close is an advisory readiness wakeup");
    unsigned char peer_closed_byte = 0U;
    test.require(
        ::recv(
            peer_closed.left.get(), &peer_closed_byte, 1U, MSG_DONTWAIT) ==
            0,
        "caller operation, not poll, classifies peer close");

    set_nonblocking(primary.left.get(), false);
    anonsync::reprove_sync_stream_socket_lifetime_or_throw(
        primary_identity, "readiness-independent lifetime");
    test.require(true, "clearing O_NONBLOCK does not rewrite socket lifetime");
    set_nonblocking(primary.left.get(), true);

    SocketPair independent = make_stream_socket_pair(true);
    const auto independent_identity =
        anonsync::observe_sync_stream_socket_lifetime_or_throw(
            independent.left.get(), "independent stream socket");
    test.require(
        independent_identity != primary_identity,
        "independent stream sockets cannot share lifetime identity");

    SocketPair replacement = make_stream_socket_pair(true);
    if (::dup2(replacement.left.get(), primary.left.get()) < 0) {
        throw std::runtime_error("socket lifetime test could not perform descriptor ABA");
    }
    require_throws_containing(
        test,
        [&] {
            anonsync::reprove_sync_stream_socket_lifetime_or_throw(
                primary_identity, "descriptor ABA");
        },
        "no longer names the exact observed socket lifetime",
        "lifetime reproof rejects close/dup2 descriptor ABA");

    int datagram_descriptors[2]{-1, -1};
    if (::socketpair(
            AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0,
            datagram_descriptors) != 0) {
        throw std::runtime_error("socket lifetime test could not create datagram pair");
    }
    FileDescriptor datagram_left(datagram_descriptors[0]);
    FileDescriptor datagram_right(datagram_descriptors[1]);
    require_throws_containing(
        test,
        [&] {
            (void)anonsync::observe_sync_stream_socket_lifetime_or_throw(
                datagram_left.get(), "datagram socket");
        },
        "is not a SOCK_STREAM socket",
        "datagram socket cannot mint byte-stream transport authority");

    int pipe_descriptors[2]{-1, -1};
    if (::pipe(pipe_descriptors) != 0) {
        throw std::runtime_error("socket lifetime test could not create pipe");
    }
    FileDescriptor pipe_read(pipe_descriptors[0]);
    FileDescriptor pipe_write(pipe_descriptors[1]);
    set_nonblocking(pipe_read.get(), true);
    set_nonblocking(pipe_write.get(), true);
    set_close_on_exec(pipe_read.get());
    set_close_on_exec(pipe_write.get());
    require_throws_containing(
        test,
        [&] {
            (void)anonsync::observe_sync_stream_socket_lifetime_or_throw(
                pipe_read.get(), "pipe descriptor");
        },
        "is not a socket-backed descriptor",
        "nonblocking pipe cannot mint stream socket lifetime identity");

    SocketPair closing = make_stream_socket_pair(true);
    const auto closing_identity =
        anonsync::observe_sync_stream_socket_lifetime_or_throw(
            closing.left.get(), "closing stream socket");
    const int closed_descriptor = closing.left.release();
    if (::close(closed_descriptor) != 0) {
        throw std::runtime_error("socket lifetime test could not close fixture");
    }
    require_throws_containing(
        test,
        [&] {
            anonsync::reprove_sync_stream_socket_lifetime_or_throw(
                closing_identity, "closed stream socket");
        },
        "could not be statted",
        "closed descriptor cannot reprove socket lifetime");
#else
    require_throws_containing(
        test,
        [] {
            (void)anonsync::observe_sync_stream_socket_lifetime_or_throw(
                -1, "unsupported socket lifetime");
        },
        "cannot prove",
        "unsupported platform fails closed");
#endif
}

}  // namespace

int main() {
    TestState test;
    try {
        run_tests(test);
    } catch (const std::exception& error) {
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
    std::cout << "sync socket lifetime/readiness checks: " << test.passed
              << "\n";
    return test.failed == 0U ? 0 : 1;
}
