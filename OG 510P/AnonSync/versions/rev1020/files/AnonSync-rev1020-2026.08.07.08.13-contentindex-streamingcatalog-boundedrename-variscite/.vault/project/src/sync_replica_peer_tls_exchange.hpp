#pragma once

#if !defined(_WIN32)

#include "sync_replica_file_tls_exchange.hpp"
#include "sync_replica_reconciliation_tls_exchange.hpp"

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

struct SyncReplicaPeerTlsServeOptions final {
    std::chrono::steady_clock::time_point first_request_deadline{};
    std::chrono::steady_clock::time_point file_receipt_deadline{};
    SyncReplicaReconciliationTlsServeOptions reconciliation;

    bool operator==(const SyncReplicaPeerTlsServeOptions&) const = default;
};

enum class SyncReplicaPeerTlsServeDisposition : std::uint8_t {
    PeerClosed = 1U,
    FirstRequestDeadlineExpired = 2U,
    UnsupportedApplication = 3U,
    FileDelivery = 4U,
    Reconciliation = 5U,
};

struct SyncReplicaPeerTlsServeResult final {
    SyncReplicaPeerTlsServeDisposition disposition =
        SyncReplicaPeerTlsServeDisposition::PeerClosed;
    std::uint64_t first_request_prefix_bytes_received = 0U;
    std::uint64_t first_request_frame_bytes = 0U;
    std::uint64_t first_request_body_bytes_received = 0U;
    std::optional<SyncReplicaFileTlsReceiveResult> file_delivery;
    std::optional<SyncReplicaReconciliationTlsServeResult> reconciliation;

    bool operator==(const SyncReplicaPeerTlsServeResult&) const = default;
};

[[nodiscard]] std::string_view sync_replica_peer_tls_serve_disposition_name(
    SyncReplicaPeerTlsServeDisposition disposition) noexcept;

// Reads exactly one bounded first application record after mutual TLS and peer
// authorization, then transfers the already-consumed frame to one protocol
// owner. Classification is magic-only; the selected protocol still performs
// complete canonical decoding, channel binding, service preflight, and durable
// validation. Unknown frames are never reinterpreted and close the local
// application capability. Every terminal result or exception discards it.
[[nodiscard]] SyncReplicaPeerTlsServeResult
serve_one_sync_replica_peer_application_over_tls_or_throw(
    SyncReplicaFileDeliveryService& file_service,
    SyncReplicaReconciliationService& reconciliation_service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    SyncReplicaPeerTlsServeOptions options,
    const std::string& label = "sync replica peer TLS application serve");

}  // namespace anonsync

#endif
