#include "sync_replica_peer_tls_exchange.hpp"

#if !defined(_WIN32)

#include "sync_replica_file_delivery_protocol.hpp"
#include "sync_replica_reconciliation_protocol.hpp"
#include "sync_replica_tls_record_exchange.hpp"

#include <algorithm>
#include <stdexcept>
#include <utility>

namespace anonsync {

std::string_view sync_replica_peer_tls_serve_disposition_name(
    SyncReplicaPeerTlsServeDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaPeerTlsServeDisposition::PeerClosed:
            return "peer_closed";
        case SyncReplicaPeerTlsServeDisposition::
            FirstRequestDeadlineExpired:
            return "first_request_deadline_expired";
        case SyncReplicaPeerTlsServeDisposition::UnsupportedApplication:
            return "unsupported_application";
        case SyncReplicaPeerTlsServeDisposition::FileDelivery:
            return "file_delivery";
        case SyncReplicaPeerTlsServeDisposition::Reconciliation:
            return "reconciliation";
    }
    return "unknown";
}

SyncReplicaPeerTlsServeResult
serve_one_sync_replica_peer_application_over_tls_or_throw(
    SyncReplicaFileDeliveryService& file_service,
    SyncReplicaReconciliationService& reconciliation_service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    SyncReplicaPeerTlsServeOptions options,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica peer TLS application label is empty");
    }
    if (file_service.folder_id() != reconciliation_service.folder_id() ||
        file_service.local_actor() != reconciliation_service.local_actor()) {
        throw std::invalid_argument(
            label + " application services do not share one local identity");
    }

    SyncReplicaPeerTlsServeResult result;
    try {
        const std::uint64_t maximum_first_frame = std::max(
            file_service.max_request_frame_bytes(),
            reconciliation_service.max_request_frame_bytes());
        const SyncReplicaTlsRecordReadUntilResult first =
            read_sync_replica_tls_record_until_or_throw(
                channel, maximum_first_frame,
                options.first_request_deadline, label + " first request");
        result.first_request_prefix_bytes_received =
            first.prefix_bytes_received;
        result.first_request_frame_bytes = first.frame_bytes;
        result.first_request_body_bytes_received = first.body_bytes_received;

        if (first.disposition ==
            SyncReplicaTlsRecordReadUntilDisposition::PeerClosed) {
            result.disposition = SyncReplicaPeerTlsServeDisposition::PeerClosed;
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            return result;
        }
        if (first.disposition ==
            SyncReplicaTlsRecordReadUntilDisposition::DeadlineExpired) {
            result.disposition = SyncReplicaPeerTlsServeDisposition::
                FirstRequestDeadlineExpired;
            discard_sync_replica_tls_authenticated_channel_noexcept(channel);
            return result;
        }

        if (sync_replica_file_delivery_request_frame_has_magic(first.frame)) {
            result.file_delivery.emplace(
                receive_one_sync_replica_file_delivery_after_first_request_over_tls_or_throw(
                    file_service, channel, first.frame,
                    options.file_receipt_deadline,
                    label + " file delivery"));
            result.disposition =
                SyncReplicaPeerTlsServeDisposition::FileDelivery;
            return result;
        }
        if (sync_replica_reconciliation_request_frame_has_magic(first.frame)) {
            result.reconciliation.emplace(
                serve_sync_replica_reconciliation_after_first_request_over_tls_or_throw(
                    reconciliation_service, channel, first.frame,
                    std::move(options.reconciliation),
                    label + " reconciliation"));
            result.disposition =
                SyncReplicaPeerTlsServeDisposition::Reconciliation;
            return result;
        }

        result.disposition =
            SyncReplicaPeerTlsServeDisposition::UnsupportedApplication;
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return result;
    } catch (...) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }
}

}  // namespace anonsync

#endif
