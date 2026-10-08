#pragma once

#include "sync_replica_tls_transport.hpp"

#include <chrono>
#include <string_view>

namespace anonsync {

// One bounded event-loop step for an exact pending SSL_read_ex() operation.
// Deadline expiry is policy, not transport progress, and leaves the continuation
// at the same WANT frontier for a later owner.
enum class SyncReplicaTlsRecordReadPollProgress {
    DeadlineExpired,
    Progress,
    WantRead,
    WantWrite,
    Complete,
    PeerClosed,
};

// One bounded event-loop step for an exact pending SSL_write_ex() operation.
// Local completion means that OpenSSL accepted the complete application record;
// it is not proof of peer receipt or receiver effect.
enum class SyncReplicaTlsRecordWritePollProgress {
    DeadlineExpired,
    Progress,
    WantRead,
    WantWrite,
    Complete,
};

// These overloads require an active strict-nonblocking continuation already at
// WANT_READ or WANT_WRITE. The absolute steady-clock deadline bounds this
// owner's willingness to begin the next OpenSSL operation; it does not claim to
// bound time spent inside one OpenSSL call.
//
// The exact target is re-proved before every poll, including after EINTR or the
// portable EAGAIN resource failure. Deadline expiry and poll syscall failure do
// not consume the pending retry. One nonzero poll result causes at most one
// continuation advance. POLLERR, POLLHUP, and POLLNVAL are advisory wakeups,
// never TLS protocol facts; the continuation's socket reproof and OpenSSL own
// close/error classification. Unsupported platforms fail closed.
[[nodiscard]] SyncReplicaTlsRecordReadPollProgress
poll_and_advance_sync_replica_tls_record_read_or_throw(
    SyncReplicaTlsRecordReadContinuation& continuation,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label = "sync replica TLS record read poll");

[[nodiscard]] SyncReplicaTlsRecordWritePollProgress
poll_and_advance_sync_replica_tls_record_write_or_throw(
    SyncReplicaTlsRecordWriteContinuation& continuation,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label = "sync replica TLS record write poll");

}  // namespace anonsync
