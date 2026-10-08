#pragma once

#include "sync_socket_readiness_identity.hpp"

#include <chrono>
#include <string_view>

namespace anonsync {

// Advisory readiness requested by one exact nonblocking byte-stream socket
// operation. Readiness is not protocol progress and never proves that a later
// syscall or OpenSSL operation will complete without another retry.
enum class SyncStreamSocketPollReadiness {
    Readable,
    Writable,
};

enum class SyncStreamSocketDeadlinePollResult {
    DeadlineExpired,
    Ready,
};

// Polls one exact Linux stream-socket lifetime until the requested readiness or
// an absolute steady-clock cutpoint. Every iteration re-proves both the socket
// lifetime and O_NONBLOCK policy; EINTR and the portable poll(2) EAGAIN resource
// failure retain the original cutpoint and never reuse stale observation.
//
// POLLERR, POLLHUP, and POLLNVAL are advisory wakeups. The caller must perform
// its own exact socket/protocol operation after Ready and classify the result.
// Unsupported platforms fail closed.
[[nodiscard]] SyncStreamSocketDeadlinePollResult
poll_sync_stream_socket_until_or_throw(
    const SyncSocketLifetimeIdentity& socket,
    SyncStreamSocketPollReadiness readiness,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label = "sync stream socket deadline poll");

}  // namespace anonsync
