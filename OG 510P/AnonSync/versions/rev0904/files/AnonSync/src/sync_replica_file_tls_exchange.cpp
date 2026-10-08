#include "sync_replica_file_tls_exchange.hpp"

#include <chrono>
#include <exception>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

namespace anonsync {
namespace {

static_assert(std::is_nothrow_move_constructible_v<
              SyncReplicaInboundFileDelivery>);
static_assert(std::is_nothrow_move_constructible_v<
              SyncReplicaFileTlsReceiveResult>);
static_assert(std::is_nothrow_move_constructible_v<
              SyncReplicaTlsAuthenticatedChannel>);
static_assert(std::is_nothrow_move_constructible_v<std::string>);
static_assert(std::is_nothrow_move_assignable_v<std::string>);

struct ReadOutcome final {
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

[[nodiscard]] ReadOutcome read_request_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    const std::string& read_label,
    const std::string& poll_label) {
    ReadOutcome outcome;
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
            outcome.prefix_bytes_received =
                reader.prefix_bytes_received();
            outcome.frame_bytes = reader.frame_bytes();
            outcome.body_bytes_received = reader.body_bytes_received();
            // If no OpenSSL operation began, destruction would release the
            // reservation without poisoning. This one-shot application owner
            // still discards the idle conversation on timeout.
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
                    outcome.body_bytes_received = reader.body_bytes_received();
                    return outcome;
                case SyncReplicaTlsRecordReadPollProgress::Progress:
                    retry_pending = false;
                    break;
                case SyncReplicaTlsRecordReadPollProgress::WantRead:
                case SyncReplicaTlsRecordReadPollProgress::WantWrite:
                    retry_pending = true;
                    break;
                case SyncReplicaTlsRecordReadPollProgress::Complete:
                    outcome.terminal = ReadOutcome::Terminal::Complete;
                    outcome.prefix_bytes_received =
                        kSyncReplicaTlsRecordPrefixBytes;
                    outcome.frame_bytes = reader.frame_bytes();
                    outcome.body_bytes_received = outcome.frame_bytes;
                    outcome.frame = reader.take_frame_or_throw();
                    return outcome;
                case SyncReplicaTlsRecordReadPollProgress::PeerClosed:
                    outcome.terminal = ReadOutcome::Terminal::PeerClosed;
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
                outcome.terminal = ReadOutcome::Terminal::Complete;
                outcome.prefix_bytes_received =
                    kSyncReplicaTlsRecordPrefixBytes;
                outcome.frame_bytes = reader.frame_bytes();
                outcome.body_bytes_received = outcome.frame_bytes;
                outcome.frame = reader.take_frame_or_throw();
                return outcome;
            case SyncReplicaTlsRecordReadProgress::PeerClosed:
                outcome.terminal = ReadOutcome::Terminal::PeerClosed;
                return outcome;
        }
    }
}

[[nodiscard]] bool write_receipt_until_or_throw(
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string_view receipt_frame,
    std::uint64_t max_frame_bytes,
    std::chrono::steady_clock::time_point deadline,
    const std::string& write_label,
    const std::string& poll_label,
    SyncReplicaFileTlsReceiveResult& result) {
    result.receipt_frame_bytes =
        static_cast<std::uint64_t>(receipt_frame.size());
    if (std::chrono::steady_clock::now() >= deadline) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return false;
    }

    SyncReplicaTlsRecordWriteContinuation writer = [&] {
        try {
            return prepare_sync_replica_tls_record_write_or_throw(
                channel, receipt_frame, max_frame_bytes,
                SyncReplicaTlsRecordWriteReadinessPolicy::
                    RequireNonblockingSocket,
                write_label);
        } catch (...) {
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            throw;
        }
    }();

    const auto observe_progress = [&] {
        result.receipt_write_started = writer.io_started();
        result.receipt_prefix_bytes_written =
            writer.prefix_bytes_written();
        result.receipt_prefix_accepted = writer.prefix_complete();
        result.receipt_body_bytes_written = writer.body_bytes_written();
    };
    const auto expire_and_discard = [&]() -> bool {
        observe_progress();
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return false;
    };

    bool retry_pending = false;
    for (;;) {
        if (!retry_pending &&
            std::chrono::steady_clock::now() >= deadline) {
            return expire_and_discard();
        }

        if (retry_pending) {
            switch (poll_and_advance_sync_replica_tls_record_write_or_throw(
                writer, deadline, poll_label)) {
                case SyncReplicaTlsRecordWritePollProgress::DeadlineExpired:
                    return expire_and_discard();
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
                    result.receipt_write_started = true;
                    result.receipt_prefix_bytes_written =
                        kSyncReplicaTlsRecordPrefixBytes;
                    result.receipt_prefix_accepted = true;
                    result.receipt_body_bytes_written =
                        result.receipt_frame_bytes;
                    return true;
            }
            continue;
        }

        switch (writer.advance_or_throw()) {
            case SyncReplicaTlsRecordWriteProgress::Progress:
                observe_progress();
                break;
            case SyncReplicaTlsRecordWriteProgress::WantRead:
            case SyncReplicaTlsRecordWriteProgress::WantWrite:
                observe_progress();
                retry_pending = true;
                break;
            case SyncReplicaTlsRecordWriteProgress::Complete:
                result.receipt_write_started = true;
                result.receipt_prefix_bytes_written =
                    kSyncReplicaTlsRecordPrefixBytes;
                result.receipt_prefix_accepted = true;
                result.receipt_body_bytes_written =
                    result.receipt_frame_bytes;
                return true;
        }
    }
}

}  // namespace

SyncReplicaFileTlsReceiveResult
receive_one_sync_replica_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::chrono::steady_clock::time_point request_deadline,
    std::chrono::steady_clock::time_point receipt_deadline,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS receiver exchange label is empty");
    }

    // Finish every diagnostic allocation before the preflight and first read
    // operation. In particular, no label construction is first attempted after
    // the durable receiver callback or after a response prefix is accepted.
    const std::string preflight_label = label + " inbound preflight";
    const std::string request_label = label + " request";
    const std::string request_poll_label = label + " request poll";
    const std::string receipt_label = label + " receipt";
    const std::string receipt_poll_label = label + " receipt poll";

    try {
        // Reject sender-only services and stale/misbound live channels before
        // reserving the TLS read stream or consuming one application byte.
        service.preflight_inbound_channel_or_throw(
            channel.delivery_authority(), preflight_label);
    } catch (...) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }

    SyncReplicaFileTlsReceiveResult result;
    ReadOutcome request = [&] {
        try {
            return read_request_until_or_throw(
                channel, service.max_request_frame_bytes(), request_deadline,
                request_label, request_poll_label);
        } catch (...) {
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            throw;
        }
    }();
    result.request_prefix_bytes_received =
        request.prefix_bytes_received;
    result.request_frame_bytes = request.frame_bytes;
    result.request_body_bytes_received = request.body_bytes_received;

    switch (request.terminal) {
        case ReadOutcome::Terminal::PeerClosed:
            result.disposition =
                SyncReplicaFileTlsReceiveDisposition::PeerClosed;
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            return result;
        case ReadOutcome::Terminal::DeadlineExpired:
            result.disposition =
                SyncReplicaFileTlsReceiveDisposition::RequestDeadlineExpired;
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            return result;
        case ReadOutcome::Terminal::Complete:
            break;
    }

    try {
        // Re-attest the exact live channel at the durable frontier. The early
        // preflight is not authority to survive arbitrary request-read delay.
        result.inbound.emplace(service.receive_request_or_throw(
            channel.delivery_authority(), request.frame));
    } catch (...) {
        // The TLS record is complete, so the transport itself is synchronized,
        // but the application conversation has no receipt. Never interpret a
        // later peer record as the missing response/request boundary.
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }

    try {
        const bool sent = write_receipt_until_or_throw(
            channel, result.inbound->receipt_frame,
            service.max_receipt_frame_bytes(), receipt_deadline,
            receipt_label, receipt_poll_label, result);
        result.disposition = sent
            ? SyncReplicaFileTlsReceiveDisposition::ReceiptSent
            : SyncReplicaFileTlsReceiveDisposition::ReceiptDeadlineExpired;
        // A completed local write is not permission to interpret a second
        // application record under an owner documented as one conversation.
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return result;
    } catch (...) {
        // Durable idempotent state may already exist. Transport failure cannot
        // revoke it, settle a sender, or leave this application stream reusable.
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }
}

SyncReplicaFileTlsReceiverSession::SyncReplicaFileTlsReceiverSession(
    SyncReplicaFileDeliveryService& service,
    SyncReplicaTlsAuthenticatedChannel&& channel,
    std::chrono::steady_clock::time_point request_deadline,
    std::chrono::steady_clock::time_point receipt_deadline,
    std::string label)
    : service_(&service),
      request_deadline_(request_deadline),
      receipt_deadline_(receipt_deadline),
      label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS receiver session label is empty");
    }

    // Validate before moving so a construction-time configuration failure does
    // not silently consume the caller's only authenticated capability.
    const std::string preflight_label = label_ + " construction preflight";
    service.preflight_inbound_channel_or_throw(
        channel.delivery_authority(), preflight_label);
    channel_.emplace(std::move(channel));
}

SyncReplicaFileTlsReceiverSession::SyncReplicaFileTlsReceiverSession(
    SyncReplicaFileTlsReceiverSession&& other) noexcept
    : service_(std::exchange(other.service_, nullptr)),
      channel_(std::move(other.channel_)),
      request_deadline_(other.request_deadline_),
      receipt_deadline_(other.receipt_deadline_),
      label_(std::move(other.label_)) {
    // optional<T>'s move leaves the source engaged with a moved-from T. Reset
    // it explicitly so active() remains a truthful ownership predicate.
    other.channel_.reset();
}

SyncReplicaFileTlsReceiverSession&
SyncReplicaFileTlsReceiverSession::operator=(
    SyncReplicaFileTlsReceiverSession&& other) noexcept {
    if (this != &other) {
        discard_noexcept();
        service_ = std::exchange(other.service_, nullptr);
        channel_ = std::move(other.channel_);
        request_deadline_ = other.request_deadline_;
        receipt_deadline_ = other.receipt_deadline_;
        label_ = std::move(other.label_);
        other.channel_.reset();
    }
    return *this;
}

SyncReplicaFileTlsReceiverSession::~SyncReplicaFileTlsReceiverSession()
    noexcept {
    discard_noexcept();
}

bool SyncReplicaFileTlsReceiverSession::active() const noexcept {
    return service_ != nullptr && channel_.has_value();
}

SyncReplicaFileTlsReceiveResult
SyncReplicaFileTlsReceiverSession::run_or_throw() {
    if (!active()) {
        throw std::logic_error(
            "sync replica file TLS receiver session is not active");
    }

    try {
        SyncReplicaFileTlsReceiveResult result =
            receive_one_sync_replica_file_delivery_over_tls_or_throw(
                *service_, *channel_, request_deadline_, receipt_deadline_,
                label_);
        discard_noexcept();
        return result;
    } catch (...) {
        discard_noexcept();
        throw;
    }
}

void SyncReplicaFileTlsReceiverSession::discard_noexcept() noexcept {
    if (channel_.has_value()) {
        discard_sync_replica_tls_authenticated_channel_noexcept(*channel_);
        channel_.reset();
    }
    service_ = nullptr;
}

}  // namespace anonsync
