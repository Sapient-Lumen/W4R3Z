#include "sync_replica_tls_record_exchange.hpp"

#include <chrono>
#include <stdexcept>
#include <string>
#include <string_view>

namespace anonsync {

SyncReplicaTlsRecordReadUntilResult
read_sync_replica_tls_record_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS bounded record read label is empty");
    }

    // Finish all diagnostic allocations before the first OpenSSL operation.
    const std::string read_label = std::string(label) + " record";
    const std::string poll_label = std::string(label) + " poll";
    SyncReplicaTlsRecordReadUntilResult result;
    if (std::chrono::steady_clock::now() >= deadline) return result;

    auto reader = begin_sync_replica_tls_record_read_or_throw(
        channel, max_frame_bytes,
        SyncReplicaTlsRecordReadReadinessPolicy::RequireNonblockingSocket,
        read_label);
    const auto observe = [&] {
        result.prefix_bytes_received = reader.prefix_bytes_received();
        result.frame_bytes = reader.frame_bytes();
        result.body_bytes_received = reader.body_bytes_received();
    };

    bool retry_pending = false;
    for (;;) {
        if (!retry_pending && std::chrono::steady_clock::now() >= deadline) {
            observe();
            return result;
        }

        if (retry_pending) {
            switch (poll_and_advance_sync_replica_tls_record_read_or_throw(
                reader, deadline, poll_label)) {
                case SyncReplicaTlsRecordReadPollProgress::DeadlineExpired:
                    observe();
                    return result;
                case SyncReplicaTlsRecordReadPollProgress::Progress:
                    observe();
                    retry_pending = false;
                    break;
                case SyncReplicaTlsRecordReadPollProgress::WantRead:
                case SyncReplicaTlsRecordReadPollProgress::WantWrite:
                    observe();
                    retry_pending = true;
                    break;
                case SyncReplicaTlsRecordReadPollProgress::Complete:
                    result.disposition =
                        SyncReplicaTlsRecordReadUntilDisposition::Complete;
                    result.prefix_bytes_received =
                        kSyncReplicaTlsRecordPrefixBytes;
                    result.frame_bytes = reader.frame_bytes();
                    result.body_bytes_received = result.frame_bytes;
                    result.frame = reader.take_frame_or_throw();
                    return result;
                case SyncReplicaTlsRecordReadPollProgress::PeerClosed:
                    result.disposition =
                        SyncReplicaTlsRecordReadUntilDisposition::PeerClosed;
                    return result;
            }
            continue;
        }

        switch (reader.advance_or_throw()) {
            case SyncReplicaTlsRecordReadProgress::Progress:
                observe();
                break;
            case SyncReplicaTlsRecordReadProgress::WantRead:
            case SyncReplicaTlsRecordReadProgress::WantWrite:
                observe();
                retry_pending = true;
                break;
            case SyncReplicaTlsRecordReadProgress::Complete:
                result.disposition =
                    SyncReplicaTlsRecordReadUntilDisposition::Complete;
                result.prefix_bytes_received = kSyncReplicaTlsRecordPrefixBytes;
                result.frame_bytes = reader.frame_bytes();
                result.body_bytes_received = result.frame_bytes;
                result.frame = reader.take_frame_or_throw();
                return result;
            case SyncReplicaTlsRecordReadProgress::PeerClosed:
                result.disposition =
                    SyncReplicaTlsRecordReadUntilDisposition::PeerClosed;
                return result;
        }
    }
}

SyncReplicaTlsRecordWriteUntilResult
write_sync_replica_tls_record_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view frame,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS bounded record write label is empty");
    }

    const std::string write_label = std::string(label) + " record";
    const std::string poll_label = std::string(label) + " poll";
    SyncReplicaTlsRecordWriteUntilResult result;
    result.frame_bytes = static_cast<std::uint64_t>(frame.size());
    if (std::chrono::steady_clock::now() >= deadline) return result;

    auto writer = prepare_sync_replica_tls_record_write_or_throw(
        channel, frame, max_frame_bytes,
        SyncReplicaTlsRecordWriteReadinessPolicy::RequireNonblockingSocket,
        write_label);
    const auto observe = [&] {
        result.io_started = writer.io_started();
        result.prefix_bytes_written = writer.prefix_bytes_written();
        result.prefix_accepted = writer.prefix_complete();
        result.body_bytes_written = writer.body_bytes_written();
    };

    bool retry_pending = false;
    for (;;) {
        if (!retry_pending && std::chrono::steady_clock::now() >= deadline) {
            observe();
            return result;
        }

        if (retry_pending) {
            switch (poll_and_advance_sync_replica_tls_record_write_or_throw(
                writer, deadline, poll_label)) {
                case SyncReplicaTlsRecordWritePollProgress::DeadlineExpired:
                    observe();
                    return result;
                case SyncReplicaTlsRecordWritePollProgress::Progress:
                    observe();
                    retry_pending = false;
                    break;
                case SyncReplicaTlsRecordWritePollProgress::WantRead:
                case SyncReplicaTlsRecordWritePollProgress::WantWrite:
                    observe();
                    retry_pending = true;
                    break;
                case SyncReplicaTlsRecordWritePollProgress::Complete:
                    result.disposition =
                        SyncReplicaTlsRecordWriteUntilDisposition::Complete;
                    result.io_started = true;
                    result.prefix_bytes_written =
                        kSyncReplicaTlsRecordPrefixBytes;
                    result.prefix_accepted = true;
                    result.body_bytes_written = result.frame_bytes;
                    return result;
            }
            continue;
        }

        switch (writer.advance_or_throw()) {
            case SyncReplicaTlsRecordWriteProgress::Progress:
                observe();
                break;
            case SyncReplicaTlsRecordWriteProgress::WantRead:
            case SyncReplicaTlsRecordWriteProgress::WantWrite:
                observe();
                retry_pending = true;
                break;
            case SyncReplicaTlsRecordWriteProgress::Complete:
                result.disposition =
                    SyncReplicaTlsRecordWriteUntilDisposition::Complete;
                result.io_started = true;
                result.prefix_bytes_written = kSyncReplicaTlsRecordPrefixBytes;
                result.prefix_accepted = true;
                result.body_bytes_written = result.frame_bytes;
                return result;
        }
    }
}

SyncReplicaTlsRecordWriteUntilResult
write_sync_replica_tls_owned_record_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string frame,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS bounded owned record write label is empty");
    }

    const std::string write_label = std::string(label) + " record";
    const std::string poll_label = std::string(label) + " poll";
    SyncReplicaTlsRecordWriteUntilResult result;
    result.frame_bytes = static_cast<std::uint64_t>(frame.size());
    if (std::chrono::steady_clock::now() >= deadline) return result;

    auto writer = prepare_sync_replica_tls_owned_record_write_or_throw(
        channel, std::move(frame), max_frame_bytes,
        SyncReplicaTlsRecordWriteReadinessPolicy::RequireNonblockingSocket,
        write_label);
    result.frame_ownership_transferred = true;
    const auto observe = [&] {
        result.io_started = writer.io_started();
        result.prefix_bytes_written = writer.prefix_bytes_written();
        result.prefix_accepted = writer.prefix_complete();
        result.body_bytes_written = writer.body_bytes_written();
    };

    bool retry_pending = false;
    for (;;) {
        if (!retry_pending && std::chrono::steady_clock::now() >= deadline) {
            observe();
            return result;
        }

        if (retry_pending) {
            switch (poll_and_advance_sync_replica_tls_record_write_or_throw(
                writer, deadline, poll_label)) {
                case SyncReplicaTlsRecordWritePollProgress::DeadlineExpired:
                    observe();
                    return result;
                case SyncReplicaTlsRecordWritePollProgress::Progress:
                    observe();
                    retry_pending = false;
                    break;
                case SyncReplicaTlsRecordWritePollProgress::WantRead:
                case SyncReplicaTlsRecordWritePollProgress::WantWrite:
                    observe();
                    retry_pending = true;
                    break;
                case SyncReplicaTlsRecordWritePollProgress::Complete:
                    result.disposition =
                        SyncReplicaTlsRecordWriteUntilDisposition::Complete;
                    result.io_started = true;
                    result.prefix_bytes_written =
                        kSyncReplicaTlsRecordPrefixBytes;
                    result.prefix_accepted = true;
                    result.body_bytes_written = result.frame_bytes;
                    return result;
            }
            continue;
        }

        switch (writer.advance_or_throw()) {
            case SyncReplicaTlsRecordWriteProgress::Progress:
                observe();
                break;
            case SyncReplicaTlsRecordWriteProgress::WantRead:
            case SyncReplicaTlsRecordWriteProgress::WantWrite:
                observe();
                retry_pending = true;
                break;
            case SyncReplicaTlsRecordWriteProgress::Complete:
                result.disposition =
                    SyncReplicaTlsRecordWriteUntilDisposition::Complete;
                result.io_started = true;
                result.prefix_bytes_written = kSyncReplicaTlsRecordPrefixBytes;
                result.prefix_accepted = true;
                result.body_bytes_written = result.frame_bytes;
                return result;
        }
    }
}

}  // namespace anonsync
