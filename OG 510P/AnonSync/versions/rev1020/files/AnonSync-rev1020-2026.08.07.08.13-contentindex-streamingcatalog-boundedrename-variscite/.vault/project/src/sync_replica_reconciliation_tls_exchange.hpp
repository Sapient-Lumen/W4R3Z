#pragma once

#if !defined(_WIN32)

#include "sync_replica_reconciliation_service.hpp"
#include "sync_replica_tls_record_exchange.hpp"
#include "sync_replica_tls_transport.hpp"

#include <chrono>
#include <cstdint>
#include <optional>
#include <string>

namespace anonsync {

inline constexpr std::uint64_t
    kSyncReplicaReconciliationTlsDefaultMaxRoundTrips = 64U;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationTlsMaximumRoundTrips = 4096U;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationTlsDefaultMaxSourceResets = 4U;

struct SyncReplicaReconciliationTlsPullOptions final {
    std::uint64_t max_round_trips =
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips;
    std::uint64_t max_source_resets =
        kSyncReplicaReconciliationTlsDefaultMaxSourceResets;
    std::optional<std::string> after_operation_id;
    std::optional<std::string> expected_source_evidence_set_digest;
    std::optional<SyncReplicaReconciliationPayloadContinuation>
        payload_continuation;
    std::chrono::steady_clock::time_point deadline{};

    bool operator==(const SyncReplicaReconciliationTlsPullOptions&) const =
        default;
};

enum class SyncReplicaReconciliationTlsPullDisposition : std::uint8_t {
    Complete = 1U,
    RoundTripLimitReached = 2U,
    SourceChangedLimitReached = 3U,
    SourcePayloadUnavailable = 4U,
    ReceiverCapacityBlocked = 5U,
    RequestDeadlineExpired = 6U,
    ResponseDeadlineExpired = 7U,
    PeerClosed = 8U,
    SourcePayloadPreparing = 9U,
};

struct SyncReplicaReconciliationTlsPullResult final {
    SyncReplicaReconciliationTlsPullDisposition disposition =
        SyncReplicaReconciliationTlsPullDisposition::RequestDeadlineExpired;
    std::uint64_t round_trips = 0U;
    std::uint64_t pages_applied = 0U;
    std::uint64_t source_resets = 0U;
    // Source-side content-defined manifest preparation responses observed on
    // this authenticated stream. Preparation turns may be collapsed inside
    // max_round_trips before a payload/page response becomes terminal.
    std::uint64_t source_payload_preparing_responses = 0U;
    std::uint64_t inserted_active = 0U;
    std::uint64_t inserted_pending = 0U;
    std::uint64_t inserted_quarantined = 0U;
    std::uint64_t duplicate_operations = 0U;
    std::uint64_t metadata_only_file_operations = 0U;
    std::uint64_t inserted_payloads = 0U;
    std::uint64_t existing_payloads = 0U;
    std::uint64_t staged_payload_ranges = 0U;
    std::uint64_t staged_payload_bytes = 0U;
    std::uint64_t terminal_verification_steps = 0U;
    std::uint64_t terminal_verification_local_continuation_steps = 0U;
    std::uint64_t terminal_verification_step_budget_exhaustions = 0U;
    std::uint64_t reused_payload_chunks = 0U;
    std::uint64_t reused_payload_ranges = 0U;
    std::uint64_t reused_payload_bytes = 0U;
    std::uint64_t delta_local_reuse_read_ranges = 0U;
    std::uint64_t delta_local_reuse_read_bytes = 0U;
    std::uint64_t delta_local_reuse_maximum_read_range_bytes = 0U;
    std::uint64_t delta_local_reuse_budget_exhaustions = 0U;
    std::uint64_t delta_local_reuse_interior_resumptions = 0U;
    std::uint64_t delta_wire_already_durable_ranges = 0U;
    std::uint64_t delta_wire_already_durable_bytes = 0U;
    std::uint64_t delta_wire_overlap_trimmed_ranges = 0U;
    std::uint64_t delta_predecessor_manifest_scans = 0U;
    std::uint64_t delta_predecessor_manifest_reuses = 0U;
    std::uint64_t delta_predecessor_manifest_hashed_bytes = 0U;
    std::uint64_t target_content_defined_manifest_publications = 0U;
    std::uint64_t target_content_defined_manifest_reuses = 0U;
    std::uint64_t delta_predecessor_index_builds = 0U;
    std::uint64_t delta_predecessor_index_reuses = 0U;
    std::uint64_t delta_cross_file_candidate_pages = 0U;
    std::uint64_t delta_cross_file_candidate_paths_scanned = 0U;
    std::uint64_t delta_cross_file_unavailable_candidates = 0U;
    std::uint64_t delta_cross_file_availability_generation_restarts = 0U;
    std::uint64_t delta_cross_file_manifest_scan_steps = 0U;
    std::uint64_t delta_cross_file_manifest_scans = 0U;
    std::uint64_t delta_cross_file_manifest_reuses = 0U;
    std::uint64_t delta_cross_file_manifest_hashed_bytes = 0U;
    std::uint64_t delta_cross_file_candidate_matches = 0U;
    std::uint64_t delta_cross_file_index_builds = 0U;
    std::uint64_t delta_cross_file_index_reuses = 0U;
    std::uint64_t request_frame_bytes_written = 0U;
    std::uint64_t response_frame_bytes_received = 0U;
    std::uint64_t source_state_generation = 0U;
    std::uint64_t source_evidence_count = 0U;
    std::string source_evidence_set_digest;
    bool has_more = false;
    std::optional<std::string> next_after_operation_id;
    std::optional<std::string> blocked_operation_id;
    std::optional<SyncReplicaReconciliationPayloadContinuation>
        payload_continuation;

    bool operator==(const SyncReplicaReconciliationTlsPullResult&) const =
        default;
};

// Pulls a bounded share-global evidence walk over one already-authenticated TLS
// stream. SourceChanged resets are automatic only within the explicit reset and
// round-trip ceilings. Every terminal return discards this local authenticated
// channel capability; the SSL/socket owner remains responsible for shutdown and
// descriptor lifetime.
[[nodiscard]] SyncReplicaReconciliationTlsPullResult
pull_sync_replica_reconciliation_over_tls_or_throw(
    SyncReplicaReconciliationService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    SyncReplicaReconciliationTlsPullOptions options,
    const std::string& label = "sync replica reconciliation TLS pull");

struct SyncReplicaReconciliationTlsServeOptions final {
    std::uint64_t max_round_trips =
        kSyncReplicaReconciliationTlsDefaultMaxRoundTrips;
    std::chrono::steady_clock::time_point deadline{};

    bool operator==(const SyncReplicaReconciliationTlsServeOptions&) const =
        default;
};

enum class SyncReplicaReconciliationTlsServeDisposition : std::uint8_t {
    Complete = 1U,
    RoundTripLimitReached = 2U,
    SourcePayloadUnavailable = 3U,
    RequestDeadlineExpired = 4U,
    ResponseDeadlineExpired = 5U,
    PeerClosed = 6U,
    SourcePayloadPreparing = 7U,
};

struct SyncReplicaReconciliationTlsServeResult final {
    SyncReplicaReconciliationTlsServeDisposition disposition =
        SyncReplicaReconciliationTlsServeDisposition::RequestDeadlineExpired;
    std::uint64_t requests_received = 0U;
    std::uint64_t responses_written = 0U;
    std::uint64_t pages_served = 0U;
    std::uint64_t source_changed_responses = 0U;
    std::uint64_t payload_unavailable_responses = 0U;
    std::uint64_t source_payload_preparing_responses = 0U;
    std::uint64_t payload_targeted_access_births = 0U;
    std::uint64_t payload_targeted_open_attempts = 0U;
    std::uint64_t payload_targeted_opens = 0U;
    std::uint64_t content_defined_manifest_scans = 0U;
    std::uint64_t content_defined_manifest_reuses = 0U;
    std::uint64_t content_defined_manifest_hashed_bytes = 0U;
    std::uint64_t content_defined_manifest_projection_steps = 0U;
    std::uint64_t content_defined_manifest_projection_restarts = 0U;
    std::uint64_t content_defined_manifest_publications = 0U;
    std::uint64_t content_defined_manifest_references = 0U;
    std::uint64_t content_defined_chunk_index_builds = 0U;
    std::uint64_t content_defined_chunk_index_reuses = 0U;
    std::uint64_t content_defined_chunk_index_lookups = 0U;
    std::uint64_t ranged_payload_windows = 0U;
    std::uint64_t ranged_payload_ranges = 0U;
    std::uint64_t ranged_payload_bytes = 0U;
    std::uint64_t request_frame_bytes_received = 0U;
    std::uint64_t response_frame_bytes_written = 0U;
    // Generation-9 response frames whose payload holes were filled directly
    // from exact source descriptors. The shipping path retains neither a
    // complete payload page nor a range-sized staging owner beside the frame.
    std::uint64_t response_direct_source_frames = 0U;
    std::uint64_t response_direct_source_frame_payload_bytes = 0U;
    std::uint64_t response_direct_source_frame_maximum_staging_bytes = 0U;
    std::uint64_t response_direct_source_frame_payload_page_bytes_at_reservation = 0U;
    // Bounded by max_payloads_per_page; every descriptor drops before TLS I/O.
    std::uint64_t response_direct_source_frame_maximum_open_descriptors = 0U;
    // Number of complete response frames transferred into TLS continuation
    // ownership. The serve path never retains a second page-sized frame copy.
    std::uint64_t response_frame_owned_handoffs = 0U;
    std::uint64_t source_state_generation = 0U;
    std::uint64_t source_evidence_count = 0U;
    std::string source_evidence_set_digest;
    bool has_more = false;
    std::optional<std::string> next_after_operation_id;
    std::optional<std::string> blocked_operation_id;
    std::optional<SyncReplicaReconciliationPayloadContinuation>
        payload_continuation;

    bool operator==(const SyncReplicaReconciliationTlsServeResult&) const =
        default;
};

// Serves a bounded sequence of reconciliation requests on one authenticated
// stream. PeerClosed after at least one response is an explicit requester stop,
// not proof that the share settled. The local channel capability is discarded
// on every return.
[[nodiscard]] SyncReplicaReconciliationTlsServeResult
serve_sync_replica_reconciliation_over_tls_or_throw(
    SyncReplicaReconciliationService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    SyncReplicaReconciliationTlsServeOptions options,
    const std::string& label = "sync replica reconciliation TLS serve");

// First-frame dispatch adapter. The supplied request must be the exact complete
// frame already read under service.max_request_frame_bytes(). Subsequent records
// use the same bounded server loop and absolute deadline.
[[nodiscard]] SyncReplicaReconciliationTlsServeResult
serve_sync_replica_reconciliation_after_first_request_over_tls_or_throw(
    SyncReplicaReconciliationService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string first_request_frame,
    SyncReplicaReconciliationTlsServeOptions options,
    const std::string& label =
        "sync replica reconciliation TLS serve after first request");

}  // namespace anonsync

#endif
