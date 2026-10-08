#pragma once

#include "sync_replica_tls_poll.hpp"
#include "sync_replica_tls_transport.hpp"

#include <chrono>
#include <cstdint>
#include <string>
#include <string_view>

namespace anonsync {

// Shared bounded driver for one complete framed TLS record. It owns no protocol
// semantics and never treats local write completion as peer receipt. Deadline
// expiry returns the exact observed transport frontier. If an OpenSSL operation
// has begun, destroying the retained continuation poisons the stream as required
// by sync_replica_tls_transport; if no operation began, the caller still decides
// whether an idle authenticated conversation may be reused or must be discarded.
enum class SyncReplicaTlsRecordReadUntilDisposition : std::uint8_t {
    Complete = 1U,
    PeerClosed = 2U,
    DeadlineExpired = 3U,
};

struct SyncReplicaTlsRecordReadUntilResult final {
    SyncReplicaTlsRecordReadUntilDisposition disposition =
        SyncReplicaTlsRecordReadUntilDisposition::DeadlineExpired;
    std::string frame;
    std::uint64_t prefix_bytes_received = 0U;
    std::uint64_t frame_bytes = 0U;
    std::uint64_t body_bytes_received = 0U;

    bool operator==(const SyncReplicaTlsRecordReadUntilResult&) const = default;
};

enum class SyncReplicaTlsRecordWriteUntilDisposition : std::uint8_t {
    Complete = 1U,
    DeadlineExpired = 2U,
};

struct SyncReplicaTlsRecordWriteUntilResult final {
    SyncReplicaTlsRecordWriteUntilDisposition disposition =
        SyncReplicaTlsRecordWriteUntilDisposition::DeadlineExpired;
    bool frame_ownership_transferred = false;
    bool io_started = false;
    std::uint64_t prefix_bytes_written = 0U;
    bool prefix_accepted = false;
    std::uint64_t frame_bytes = 0U;
    std::uint64_t body_bytes_written = 0U;

    bool operator==(const SyncReplicaTlsRecordWriteUntilResult&) const = default;
};

[[nodiscard]] SyncReplicaTlsRecordReadUntilResult
read_sync_replica_tls_record_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label = "sync replica TLS bounded record read");

[[nodiscard]] SyncReplicaTlsRecordWriteUntilResult
write_sync_replica_tls_record_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label = "sync replica TLS bounded record write");

// Transfers one complete already-owned frame into the TLS continuation before
// driving the same bounded write state machine. This avoids a second page-sized
// body allocation when a protocol encoder has just produced the final frame.
[[nodiscard]] SyncReplicaTlsRecordWriteUntilResult
write_sync_replica_tls_owned_record_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string frame,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label = "sync replica TLS bounded owned record write");

}  // namespace anonsync
