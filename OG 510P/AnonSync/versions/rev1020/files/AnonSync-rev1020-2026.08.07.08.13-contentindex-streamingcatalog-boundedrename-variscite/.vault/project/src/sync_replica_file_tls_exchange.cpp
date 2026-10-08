#include "sync_replica_file_tls_exchange.hpp"

#include "sync_replica_tls_record_exchange.hpp"

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

}  // namespace

namespace {

SyncReplicaFileTlsReceiveResult receive_impl_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::optional<std::string> first_request_frame,
    std::chrono::steady_clock::time_point request_deadline,
    std::chrono::steady_clock::time_point receipt_deadline,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file TLS receiver exchange label is empty");
    }

    // Finish every diagnostic allocation before the preflight and first read
    // operation. No label construction is first attempted after the durable
    // receiver callback or after a response prefix is accepted.
    const std::string preflight_label = label + " inbound preflight";
    const std::string request_label = label + " request";
    const std::string receipt_label = label + " receipt";

    try {
        if (first_request_frame.has_value() &&
            (first_request_frame->empty() ||
             first_request_frame->size() >
                 service.max_request_frame_bytes())) {
            throw std::invalid_argument(
                label +
                " first request is empty or exceeds the configured frame limit");
        }
        service.preflight_inbound_channel_or_throw(
            channel.delivery_authority(), preflight_label);
    } catch (...) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }

    SyncReplicaFileTlsReceiveResult result;
    std::string request_frame;
    if (first_request_frame.has_value()) {
        request_frame = std::move(*first_request_frame);
        result.request_prefix_bytes_received =
            kSyncReplicaTlsRecordPrefixBytes;
        result.request_frame_bytes =
            static_cast<std::uint64_t>(request_frame.size());
        result.request_body_bytes_received = result.request_frame_bytes;
    } else {
        SyncReplicaTlsRecordReadUntilResult request = [&] {
            try {
                return read_sync_replica_tls_record_until_or_throw(
                    channel, service.max_request_frame_bytes(), request_deadline,
                    request_label);
            } catch (...) {
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                throw;
            }
        }();
        result.request_prefix_bytes_received = request.prefix_bytes_received;
        result.request_frame_bytes = request.frame_bytes;
        result.request_body_bytes_received = request.body_bytes_received;

        switch (request.disposition) {
            case SyncReplicaTlsRecordReadUntilDisposition::PeerClosed:
                result.disposition =
                    SyncReplicaFileTlsReceiveDisposition::PeerClosed;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            case SyncReplicaTlsRecordReadUntilDisposition::DeadlineExpired:
                result.disposition = SyncReplicaFileTlsReceiveDisposition::
                    RequestDeadlineExpired;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            case SyncReplicaTlsRecordReadUntilDisposition::Complete:
                break;
        }
        request_frame = std::move(request.frame);
    }

    try {
        // Re-attest the exact live channel at the durable frontier. The early
        // preflight is not authority to survive arbitrary request-read delay.
        result.inbound.emplace(service.receive_request_or_throw(
            channel.delivery_authority(), request_frame));
    } catch (...) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }

    try {
        const SyncReplicaTlsRecordWriteUntilResult receipt =
            write_sync_replica_tls_record_until_or_throw(
                channel, result.inbound->receipt_frame,
                service.max_receipt_frame_bytes(), receipt_deadline,
                receipt_label);
        result.receipt_write_started = receipt.io_started;
        result.receipt_prefix_bytes_written = receipt.prefix_bytes_written;
        result.receipt_prefix_accepted = receipt.prefix_accepted;
        result.receipt_frame_bytes = receipt.frame_bytes;
        result.receipt_body_bytes_written = receipt.body_bytes_written;
        result.disposition =
            receipt.disposition ==
                    SyncReplicaTlsRecordWriteUntilDisposition::Complete
                ? SyncReplicaFileTlsReceiveDisposition::ReceiptSent
                : SyncReplicaFileTlsReceiveDisposition::ReceiptDeadlineExpired;
        // This remains a one-conversation owner. A complete local write is not
        // permission to reinterpret a second application record.
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return result;
    } catch (...) {
        // Durable idempotent state may already exist. Transport failure cannot
        // revoke it, settle a sender, or leave this stream reusable.
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
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
    return receive_impl_or_throw(
        service, channel, std::nullopt, request_deadline, receipt_deadline,
        label);
}

SyncReplicaFileTlsReceiveResult
receive_one_sync_replica_file_delivery_after_first_request_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string first_request_frame,
    std::chrono::steady_clock::time_point receipt_deadline,
    const std::string& label) {
    return receive_impl_or_throw(
        service, channel, std::move(first_request_frame), receipt_deadline,
        receipt_deadline, label);
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
