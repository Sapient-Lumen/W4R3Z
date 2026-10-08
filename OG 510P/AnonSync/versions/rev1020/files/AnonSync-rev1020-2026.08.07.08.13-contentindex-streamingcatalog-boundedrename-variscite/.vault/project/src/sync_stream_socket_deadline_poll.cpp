#include "sync_stream_socket_deadline_poll.hpp"

#include <cerrno>
#include <chrono>
#include <climits>
#include <stdexcept>
#include <string>

#ifdef __unix__
#include <poll.h>
#endif

namespace anonsync {
namespace {

static_assert(
    std::chrono::steady_clock::is_steady,
    "socket poll deadlines require a monotonic steady clock");

#ifdef __unix__
[[nodiscard]] short poll_events_or_throw(
    SyncStreamSocketPollReadiness readiness) {
    switch (readiness) {
        case SyncStreamSocketPollReadiness::Readable:
            return POLLIN;
        case SyncStreamSocketPollReadiness::Writable:
            return POLLOUT;
    }
    throw std::logic_error(
        "sync stream socket poll observed unknown readiness");
}

[[nodiscard]] int poll_timeout_milliseconds(
    std::chrono::steady_clock::time_point now,
    std::chrono::steady_clock::time_point deadline) noexcept {
    if (deadline <= now) return 0;

    const auto remaining = deadline - now;
    const auto maximum =
        std::chrono::duration_cast<std::chrono::steady_clock::duration>(
            std::chrono::milliseconds(INT_MAX));
    if (remaining >= maximum) return INT_MAX;

    const auto whole_milliseconds =
        std::chrono::duration_cast<std::chrono::milliseconds>(remaining);
    int timeout = static_cast<int>(whole_milliseconds.count());
    if (std::chrono::duration_cast<std::chrono::steady_clock::duration>(
            whole_milliseconds) < remaining) {
        ++timeout;
    }
    return timeout > 0 ? timeout : 1;
}
#endif

}  // namespace

SyncStreamSocketDeadlinePollResult poll_sync_stream_socket_until_or_throw(
    const SyncSocketLifetimeIdentity& socket,
    SyncStreamSocketPollReadiness readiness,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
#ifdef __unix__
    for (;;) {
        require_sync_stream_socket_nonblocking_or_throw(socket, label);
        const auto before_poll = std::chrono::steady_clock::now();
        if (before_poll >= deadline) {
            return SyncStreamSocketDeadlinePollResult::DeadlineExpired;
        }

        struct pollfd descriptor_event {
            socket.descriptor(), poll_events_or_throw(readiness), 0
        };
        const int timeout = poll_timeout_milliseconds(before_poll, deadline);

        errno = 0;
        const int result = ::poll(&descriptor_event, 1U, timeout);
        const int poll_errno = errno;
        if (result < 0) {
            if (poll_errno == EINTR || poll_errno == EAGAIN) {
                continue;
            }
            throw std::runtime_error(
                std::string(label) + " poll failed (errno " +
                std::to_string(poll_errno) + ")");
        }
        if (result == 0) {
            if (std::chrono::steady_clock::now() >= deadline) {
                return SyncStreamSocketDeadlinePollResult::DeadlineExpired;
            }
            continue;
        }
        if (descriptor_event.revents == 0) {
            throw std::runtime_error(
                std::string(label) +
                " poll reported progress without readiness or error bits");
        }

        // A wakeup cannot spend authority after the absolute cutpoint. The
        // second exact reproof also catches descriptor ABA or blocking-policy
        // mutation before the caller can issue its next protocol operation.
        if (std::chrono::steady_clock::now() >= deadline) {
            return SyncStreamSocketDeadlinePollResult::DeadlineExpired;
        }
        require_sync_stream_socket_nonblocking_or_throw(socket, label);
        return SyncStreamSocketDeadlinePollResult::Ready;
    }
#else
    (void)socket;
    (void)readiness;
    (void)deadline;
    throw std::runtime_error(
        std::string(label) +
        " cannot own a bounded stream-socket poll on this platform");
#endif
}

}  // namespace anonsync
