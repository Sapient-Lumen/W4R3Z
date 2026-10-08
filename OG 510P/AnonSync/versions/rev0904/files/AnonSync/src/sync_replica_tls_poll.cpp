#include "sync_replica_tls_poll.hpp"

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
    "TLS poll deadlines require a monotonic steady clock");

#ifdef __unix__
[[nodiscard]] short poll_events_or_throw(
    SyncReplicaTlsSocketReadiness readiness) {
    switch (readiness) {
        case SyncReplicaTlsSocketReadiness::Readable:
            return POLLIN;
        case SyncReplicaTlsSocketReadiness::Writable:
            return POLLOUT;
    }
    throw std::logic_error(
        "sync replica TLS poll observed an unknown readiness value");
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

template <typename PublicProgress, typename Continuation, typename Mapper>
[[nodiscard]] PublicProgress poll_and_advance_or_throw(
    Continuation& continuation,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label,
    Mapper&& map_progress) {
    for (;;) {
        // Target disclosure validates the public precondition and re-proves the
        // exact authentication-time BIO/socket capability. It intentionally
        // precedes deadline return so an inactive or non-WANT continuation is
        // never disguised as an ordinary timeout.
        const SyncReplicaTlsSocketReadinessTarget target =
            continuation.pending_readiness_or_throw();

        const auto before_poll = std::chrono::steady_clock::now();
        if (before_poll >= deadline) return PublicProgress::DeadlineExpired;

        struct pollfd descriptor_event {
            target.descriptor,
            poll_events_or_throw(target.readiness),
            0,
        };
        const int timeout = poll_timeout_milliseconds(before_poll, deadline);

        errno = 0;
        const int result = ::poll(&descriptor_event, 1U, timeout);
        const int poll_errno = errno;
        if (result < 0) {
            if (poll_errno == EINTR || poll_errno == EAGAIN) {
                // Never reuse a target across interruption or transient poll
                // resource failure. The next iteration re-proves the exact
                // continuation while retaining the original absolute deadline.
                continue;
            }
            throw std::runtime_error(
                std::string(label) + " poll failed (errno " +
                std::to_string(poll_errno) + ")");
        }
        if (result == 0) {
            // poll() rounds its millisecond timeout upward and scheduling may
            // overrun. Only the absolute steady-clock cutpoint owns expiry.
            if (std::chrono::steady_clock::now() >= deadline) {
                return PublicProgress::DeadlineExpired;
            }
            continue;
        }
        if (descriptor_event.revents == 0) {
            throw std::runtime_error(
                std::string(label) +
                " poll reported progress without readiness or error bits");
        }

        // A wakeup cannot spend authority after the caller's absolute cutpoint.
        // Timeout preserves the exact OpenSSL retry and its stable arguments.
        if (std::chrono::steady_clock::now() >= deadline) {
            return PublicProgress::DeadlineExpired;
        }

        // Error, hangup, and invalid bits are advisory wakeups. The continuation
        // re-proves the target again and lets OpenSSL classify close, truncation,
        // retry, or fatal protocol state. Exactly one SSL operation is issued.
        return map_progress(continuation.advance_or_throw());
    }
}
#endif

[[nodiscard]] SyncReplicaTlsRecordReadPollProgress map_read_progress_or_throw(
    SyncReplicaTlsRecordReadProgress progress) {
    switch (progress) {
        case SyncReplicaTlsRecordReadProgress::Progress:
            return SyncReplicaTlsRecordReadPollProgress::Progress;
        case SyncReplicaTlsRecordReadProgress::WantRead:
            return SyncReplicaTlsRecordReadPollProgress::WantRead;
        case SyncReplicaTlsRecordReadProgress::WantWrite:
            return SyncReplicaTlsRecordReadPollProgress::WantWrite;
        case SyncReplicaTlsRecordReadProgress::Complete:
            return SyncReplicaTlsRecordReadPollProgress::Complete;
        case SyncReplicaTlsRecordReadProgress::PeerClosed:
            return SyncReplicaTlsRecordReadPollProgress::PeerClosed;
    }
    throw std::logic_error(
        "sync replica TLS poll observed an unknown TLS read progress value");
}

[[nodiscard]] SyncReplicaTlsRecordWritePollProgress map_write_progress_or_throw(
    SyncReplicaTlsRecordWriteProgress progress) {
    switch (progress) {
        case SyncReplicaTlsRecordWriteProgress::Progress:
            return SyncReplicaTlsRecordWritePollProgress::Progress;
        case SyncReplicaTlsRecordWriteProgress::WantRead:
            return SyncReplicaTlsRecordWritePollProgress::WantRead;
        case SyncReplicaTlsRecordWriteProgress::WantWrite:
            return SyncReplicaTlsRecordWritePollProgress::WantWrite;
        case SyncReplicaTlsRecordWriteProgress::Complete:
            return SyncReplicaTlsRecordWritePollProgress::Complete;
    }
    throw std::logic_error(
        "sync replica TLS poll observed an unknown TLS write progress value");
}

}  // namespace

SyncReplicaTlsRecordReadPollProgress
poll_and_advance_sync_replica_tls_record_read_or_throw(
    SyncReplicaTlsRecordReadContinuation& continuation,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
#ifdef __unix__
    return poll_and_advance_or_throw<SyncReplicaTlsRecordReadPollProgress>(
        continuation, deadline, label, map_read_progress_or_throw);
#else
    (void)continuation;
    (void)deadline;
    throw std::runtime_error(
        std::string(label) +
        " cannot own a bounded TLS readiness poll on this platform");
#endif
}

SyncReplicaTlsRecordWritePollProgress
poll_and_advance_sync_replica_tls_record_write_or_throw(
    SyncReplicaTlsRecordWriteContinuation& continuation,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
#ifdef __unix__
    return poll_and_advance_or_throw<SyncReplicaTlsRecordWritePollProgress>(
        continuation, deadline, label, map_write_progress_or_throw);
#else
    (void)continuation;
    (void)deadline;
    throw std::runtime_error(
        std::string(label) +
        " cannot own a bounded TLS readiness poll on this platform");
#endif
}

}  // namespace anonsync
