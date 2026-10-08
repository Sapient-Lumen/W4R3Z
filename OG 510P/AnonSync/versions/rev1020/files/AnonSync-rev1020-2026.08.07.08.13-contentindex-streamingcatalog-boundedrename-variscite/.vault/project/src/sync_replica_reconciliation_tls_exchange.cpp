#include "sync_replica_reconciliation_tls_exchange.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

void add_or_throw(
    std::uint64_t& target,
    std::uint64_t value,
    std::string_view label) {
    if (value > std::numeric_limits<std::uint64_t>::max() - target) {
        throw std::overflow_error(std::string(label) + " counter overflow");
    }
    target += value;
}

void increment_or_throw(std::uint64_t& target, std::string_view label) {
    add_or_throw(target, 1U, label);
}

void validate_round_trip_bound_or_throw(
    std::uint64_t value,
    std::string_view label) {
    if (value == 0U ||
        value > kSyncReplicaReconciliationTlsMaximumRoundTrips) {
        throw std::invalid_argument(
            std::string(label) + " must be in [1, " +
            std::to_string(kSyncReplicaReconciliationTlsMaximumRoundTrips) +
            "]");
    }
}

void validate_pull_options_or_throw(
    const SyncReplicaReconciliationTlsPullOptions& options) {
    validate_round_trip_bound_or_throw(
        options.max_round_trips,
        "sync replica reconciliation TLS max_round_trips");
    if (options.max_source_resets > options.max_round_trips) {
        throw std::invalid_argument(
            "sync replica reconciliation TLS max_source_resets exceeds max_round_trips");
    }
    if (options.after_operation_id.has_value() &&
        !options.expected_source_evidence_set_digest.has_value()) {
        throw std::invalid_argument(
            "sync replica reconciliation TLS cursor lacks its source digest");
    }
    if (options.payload_continuation.has_value() &&
        !options.expected_source_evidence_set_digest.has_value()) {
        throw std::invalid_argument(
            "sync replica reconciliation TLS payload continuation lacks its source digest");
    }
    if (options.expected_source_evidence_set_digest.has_value() &&
        !options.after_operation_id.has_value() &&
        !options.payload_continuation.has_value()) {
        throw std::invalid_argument(
            "sync replica reconciliation TLS source digest has no continuation");
    }
}

void observe_apply_result(
    const SyncReplicaReconciliationApplyResult& applied,
    SyncReplicaReconciliationTlsPullResult& result) {
    add_or_throw(
        result.inserted_active, applied.inserted_active,
        "reconciliation TLS inserted-active");
    add_or_throw(
        result.inserted_pending, applied.inserted_pending,
        "reconciliation TLS inserted-pending");
    add_or_throw(
        result.inserted_quarantined, applied.inserted_quarantined,
        "reconciliation TLS inserted-quarantined");
    add_or_throw(
        result.duplicate_operations, applied.duplicate_operations,
        "reconciliation TLS duplicate-operations");
    add_or_throw(
        result.metadata_only_file_operations,
        applied.metadata_only_file_operations,
        "reconciliation TLS metadata-only-file-operations");
    add_or_throw(
        result.inserted_payloads, applied.inserted_payloads,
        "reconciliation TLS inserted-payloads");
    add_or_throw(
        result.existing_payloads, applied.existing_payloads,
        "reconciliation TLS existing-payloads");
    add_or_throw(
        result.staged_payload_ranges, applied.staged_payload_ranges,
        "reconciliation TLS staged-payload-ranges");
    add_or_throw(
        result.staged_payload_bytes, applied.staged_payload_bytes,
        "reconciliation TLS staged-payload-bytes");
    add_or_throw(
        result.terminal_verification_steps,
        applied.terminal_verification_steps,
        "reconciliation TLS terminal-verification-steps");
    add_or_throw(
        result.terminal_verification_local_continuation_steps,
        applied.terminal_verification_local_continuation_steps,
        "reconciliation TLS terminal-verification-local-continuation-steps");
    add_or_throw(
        result.terminal_verification_step_budget_exhaustions,
        applied.terminal_verification_step_budget_exhaustions,
        "reconciliation TLS terminal-verification-step-budget-exhaustions");
    add_or_throw(
        result.reused_payload_chunks, applied.reused_payload_chunks,
        "reconciliation TLS reused-payload-blocks");
    add_or_throw(
        result.reused_payload_ranges, applied.reused_payload_ranges,
        "reconciliation TLS reused-payload-ranges");
    add_or_throw(
        result.reused_payload_bytes, applied.reused_payload_bytes,
        "reconciliation TLS reused-payload-bytes");
    add_or_throw(
        result.delta_local_reuse_read_ranges,
        applied.delta_local_reuse_read_ranges,
        "reconciliation TLS delta-local-reuse-read-ranges");
    add_or_throw(
        result.delta_local_reuse_read_bytes,
        applied.delta_local_reuse_read_bytes,
        "reconciliation TLS delta-local-reuse-read-bytes");
    result.delta_local_reuse_maximum_read_range_bytes =
        std::max(
            result.delta_local_reuse_maximum_read_range_bytes,
            applied.delta_local_reuse_maximum_read_range_bytes);
    add_or_throw(
        result.delta_local_reuse_budget_exhaustions,
        applied.delta_local_reuse_budget_exhaustions,
        "reconciliation TLS delta-local-reuse-budget-exhaustions");
    add_or_throw(
        result.delta_local_reuse_interior_resumptions,
        applied.delta_local_reuse_interior_resumptions,
        "reconciliation TLS delta-local-reuse-interior-resumptions");
    add_or_throw(
        result.delta_wire_already_durable_ranges,
        applied.delta_wire_already_durable_ranges,
        "reconciliation TLS delta-wire-already-durable-ranges");
    add_or_throw(
        result.delta_wire_already_durable_bytes,
        applied.delta_wire_already_durable_bytes,
        "reconciliation TLS delta-wire-already-durable-bytes");
    add_or_throw(
        result.delta_wire_overlap_trimmed_ranges,
        applied.delta_wire_overlap_trimmed_ranges,
        "reconciliation TLS delta-wire-overlap-trimmed-ranges");
    add_or_throw(
        result.delta_predecessor_manifest_scans,
        applied.delta_predecessor_manifest_scans,
        "reconciliation TLS delta-predecessor-manifest-scans");
    add_or_throw(
        result.delta_predecessor_manifest_reuses,
        applied.delta_predecessor_manifest_reuses,
        "reconciliation TLS delta-predecessor-manifest-reuses");
    add_or_throw(
        result.delta_predecessor_manifest_hashed_bytes,
        applied.delta_predecessor_manifest_hashed_bytes,
        "reconciliation TLS delta-predecessor-manifest-hashed-bytes");
    add_or_throw(
        result.target_content_defined_manifest_publications,
        applied.target_content_defined_manifest_publications,
        "reconciliation TLS target-content-defined-manifest-publications");
    add_or_throw(
        result.target_content_defined_manifest_reuses,
        applied.target_content_defined_manifest_reuses,
        "reconciliation TLS target-content-defined-manifest-reuses");
    add_or_throw(
        result.delta_predecessor_index_builds,
        applied.delta_predecessor_index_builds,
        "reconciliation TLS delta-predecessor-index-builds");
    add_or_throw(
        result.delta_predecessor_index_reuses,
        applied.delta_predecessor_index_reuses,
        "reconciliation TLS delta-predecessor-index-reuses");
    add_or_throw(
        result.delta_cross_file_candidate_pages,
        applied.delta_cross_file_candidate_pages,
        "reconciliation TLS delta-cross-file-candidate-pages");
    add_or_throw(
        result.delta_cross_file_candidate_paths_scanned,
        applied.delta_cross_file_candidate_paths_scanned,
        "reconciliation TLS delta-cross-file-candidate-paths-scanned");
    add_or_throw(
        result.delta_cross_file_unavailable_candidates,
        applied.delta_cross_file_unavailable_candidates,
        "reconciliation TLS delta-cross-file-unavailable-candidates");
    add_or_throw(
        result.delta_cross_file_availability_generation_restarts,
        applied.delta_cross_file_availability_generation_restarts,
        "reconciliation TLS delta-cross-file-availability-generation-restarts");
    add_or_throw(
        result.delta_cross_file_manifest_scan_steps,
        applied.delta_cross_file_manifest_scan_steps,
        "reconciliation TLS delta-cross-file-manifest-scan-steps");
    add_or_throw(
        result.delta_cross_file_manifest_scans,
        applied.delta_cross_file_manifest_scans,
        "reconciliation TLS delta-cross-file-manifest-scans");
    add_or_throw(
        result.delta_cross_file_manifest_reuses,
        applied.delta_cross_file_manifest_reuses,
        "reconciliation TLS delta-cross-file-manifest-reuses");
    add_or_throw(
        result.delta_cross_file_manifest_hashed_bytes,
        applied.delta_cross_file_manifest_hashed_bytes,
        "reconciliation TLS delta-cross-file-manifest-hashed-bytes");
    add_or_throw(
        result.delta_cross_file_candidate_matches,
        applied.delta_cross_file_candidate_matches,
        "reconciliation TLS delta-cross-file-candidate-matches");
    add_or_throw(
        result.delta_cross_file_index_builds,
        applied.delta_cross_file_index_builds,
        "reconciliation TLS delta-cross-file-index-builds");
    add_or_throw(
        result.delta_cross_file_index_reuses,
        applied.delta_cross_file_index_reuses,
        "reconciliation TLS delta-cross-file-index-reuses");
    result.source_state_generation = applied.source_state_generation;
    result.source_evidence_count = applied.source_evidence_count;
    result.source_evidence_set_digest = applied.source_evidence_set_digest;
    result.has_more = applied.has_more;
    result.next_after_operation_id = applied.next_after_operation_id;
    result.blocked_operation_id = applied.blocked_operation_id;
    result.payload_continuation = applied.payload_continuation;
}

void observe_served_response(
    const SyncReplicaReconciliationResponse& response,
    SyncReplicaReconciliationTlsServeResult& result) {
    result.source_state_generation = response.source_state_generation;
    result.source_evidence_count = response.source_evidence_count;
    result.source_evidence_set_digest = response.source_evidence_set_digest;
    result.has_more = response.has_more;
    result.next_after_operation_id = response.next_after_operation_id;
    result.blocked_operation_id = response.blocked_operation_id;
    result.payload_continuation = response.payload_continuation;
    switch (response.disposition) {
        case SyncReplicaReconciliationResponseDisposition::Page:
            increment_or_throw(
                result.pages_served,
                "reconciliation TLS served-page");
            break;
        case SyncReplicaReconciliationResponseDisposition::SourceChanged:
            increment_or_throw(
                result.source_changed_responses,
                "reconciliation TLS source-changed-response");
            break;
        case SyncReplicaReconciliationResponseDisposition::PayloadUnavailable:
            increment_or_throw(
                result.payload_unavailable_responses,
                "reconciliation TLS payload-unavailable-response");
            break;
        case SyncReplicaReconciliationResponseDisposition::
            SourcePayloadPreparing:
            increment_or_throw(
                result.source_payload_preparing_responses,
                "reconciliation TLS source-payload-preparing-response");
            break;
    }
}

SyncReplicaReconciliationTlsServeResult serve_impl_or_throw(
    SyncReplicaReconciliationService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::optional<std::string> first_request_frame,
    SyncReplicaReconciliationTlsServeOptions options,
    const std::string& label) {
    SyncReplicaReconciliationTlsServeResult result;
    try {
        if (label.empty()) {
            throw std::invalid_argument(
                "sync replica reconciliation TLS serve label is empty");
        }
        validate_round_trip_bound_or_throw(
            options.max_round_trips,
            "sync replica reconciliation TLS serve max_round_trips");
        if (first_request_frame.has_value() &&
            (first_request_frame->empty() ||
             first_request_frame->size() >
                 service.max_request_frame_bytes())) {
            throw std::invalid_argument(
                label + " first request is empty or exceeds the configured frame limit");
        }
        SyncReplicaReconciliationServeSession serve_session =
            service.make_serve_session_or_throw(
                channel.delivery_authority());

        for (std::uint64_t index = 0U;
             index < options.max_round_trips; ++index) {
            std::string request_frame;
            if (first_request_frame.has_value()) {
                request_frame = std::move(*first_request_frame);
                first_request_frame.reset();
                add_or_throw(
                    result.request_frame_bytes_received,
                    static_cast<std::uint64_t>(request_frame.size()),
                    "reconciliation TLS request-frame-bytes");
            } else {
                const SyncReplicaTlsRecordReadUntilResult read =
                    read_sync_replica_tls_record_until_or_throw(
                        channel, service.max_request_frame_bytes(),
                        options.deadline,
                        label + " request " + std::to_string(index + 1U));
                add_or_throw(
                    result.request_frame_bytes_received,
                    read.body_bytes_received,
                    "reconciliation TLS request-frame-bytes");
                if (read.disposition ==
                    SyncReplicaTlsRecordReadUntilDisposition::PeerClosed) {
                    result.disposition =
                        SyncReplicaReconciliationTlsServeDisposition::PeerClosed;
                    result.has_more = true;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    return result;
                }
                if (read.disposition ==
                    SyncReplicaTlsRecordReadUntilDisposition::DeadlineExpired) {
                    result.disposition = SyncReplicaReconciliationTlsServeDisposition::
                        RequestDeadlineExpired;
                    result.has_more = true;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    return result;
                }
                request_frame = read.frame;
            }
            increment_or_throw(
                result.requests_received,
                "reconciliation TLS requests-received");

            SyncReplicaFramedInboundReconciliation inbound =
                service.serve_request_frame_or_throw(
                    channel.delivery_authority(), request_frame,
                    serve_session);
            increment_or_throw(
                result.response_direct_source_frames,
                "reconciliation TLS direct source response frame");
            add_or_throw(
                result.response_direct_source_frame_payload_bytes,
                inbound.direct_payload_bytes,
                "reconciliation TLS direct source response payload bytes");
            result.response_direct_source_frame_maximum_staging_bytes =
                std::max(
                    result.response_direct_source_frame_maximum_staging_bytes,
                    inbound.direct_frame_maximum_source_staging_bytes);
            add_or_throw(
                result.response_direct_source_frame_payload_page_bytes_at_reservation,
                inbound.direct_frame_payload_page_bytes_at_reservation,
                "reconciliation TLS source payload-page bytes at frame reservation");
            result.response_direct_source_frame_maximum_open_descriptors =
                std::max(
                    result.response_direct_source_frame_maximum_open_descriptors,
                    inbound.direct_frame_open_source_descriptors_at_reservation);
            result.payload_targeted_access_births =
                serve_session.payload_targeted_access_births();
            result.payload_targeted_open_attempts =
                serve_session.payload_targeted_open_attempts();
            result.payload_targeted_opens =
                serve_session.payload_targeted_opens();
            result.content_defined_manifest_scans =
                serve_session.content_defined_manifest_scans();
            result.content_defined_manifest_reuses =
                serve_session.content_defined_manifest_reuses();
            result.content_defined_manifest_hashed_bytes =
                serve_session.content_defined_manifest_hashed_bytes();
            result.content_defined_manifest_projection_steps =
                serve_session.content_defined_manifest_projection_steps();
            result.content_defined_manifest_projection_restarts =
                serve_session.content_defined_manifest_projection_restarts();
            result.content_defined_manifest_publications =
                serve_session.content_defined_manifest_publications();
            result.content_defined_manifest_references =
                serve_session.content_defined_manifest_references();
            result.content_defined_chunk_index_builds =
                serve_session.content_defined_chunk_index_builds();
            result.content_defined_chunk_index_reuses =
                serve_session.content_defined_chunk_index_reuses();
            result.content_defined_chunk_index_lookups =
                serve_session.content_defined_chunk_index_lookups();
            result.ranged_payload_windows =
                serve_session.ranged_payload_windows();
            result.ranged_payload_ranges =
                serve_session.ranged_payload_ranges();
            result.ranged_payload_bytes =
                serve_session.ranged_payload_bytes();
            observe_served_response(inbound.response, result);

            const SyncReplicaReconciliationResponseDisposition
                response_disposition = inbound.response.disposition;
            const bool response_has_more = inbound.response.has_more;
            // The direct source path never materialized payload strings in
            // response. Release bounded metadata before TLS backpressure; the
            // final encoded frame is the only payload-sized response owner.
            std::vector<SyncReplicaOperation>().swap(
                inbound.response.operations);
            std::vector<SyncReplicaReconciliationPayload>().swap(
                inbound.response.payloads);
            std::vector<std::string>().swap(
                inbound.response.metadata_only_file_operation_ids);
            const SyncReplicaTlsRecordWriteUntilResult write =
                write_sync_replica_tls_owned_record_until_or_throw(
                    channel, std::move(inbound.response_frame),
                    service.max_response_frame_bytes(), options.deadline,
                    label + " response " + std::to_string(index + 1U));
            if (write.frame_ownership_transferred) {
                increment_or_throw(
                    result.response_frame_owned_handoffs,
                    "reconciliation TLS owned response-frame handoff");
            }
            add_or_throw(
                result.response_frame_bytes_written,
                write.body_bytes_written,
                "reconciliation TLS response-frame-bytes");
            if (write.disposition !=
                SyncReplicaTlsRecordWriteUntilDisposition::Complete) {
                result.disposition = SyncReplicaReconciliationTlsServeDisposition::
                    ResponseDeadlineExpired;
                result.has_more = true;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            }
            increment_or_throw(
                result.responses_written,
                "reconciliation TLS responses-written");

            if (response_disposition ==
                SyncReplicaReconciliationResponseDisposition::PayloadUnavailable) {
                result.disposition = SyncReplicaReconciliationTlsServeDisposition::
                    SourcePayloadUnavailable;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            }
            if (response_disposition ==
                SyncReplicaReconciliationResponseDisposition::
                    SourcePayloadPreparing) {
                if (index + 1U < options.max_round_trips) {
                    continue;
                }
                result.disposition = SyncReplicaReconciliationTlsServeDisposition::
                    SourcePayloadPreparing;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            }
            if (response_disposition ==
                    SyncReplicaReconciliationResponseDisposition::Page &&
                !response_has_more) {
                result.disposition =
                    SyncReplicaReconciliationTlsServeDisposition::Complete;
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            }
        }

        result.disposition = SyncReplicaReconciliationTlsServeDisposition::
            RoundTripLimitReached;
        result.has_more = true;
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return result;
    } catch (...) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }
}

}  // namespace

SyncReplicaReconciliationTlsPullResult
pull_sync_replica_reconciliation_over_tls_or_throw(
    SyncReplicaReconciliationService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    SyncReplicaReconciliationTlsPullOptions options,
    const std::string& label) {
    SyncReplicaReconciliationTlsPullResult result;
    try {
        if (label.empty()) {
            throw std::invalid_argument(
                "sync replica reconciliation TLS pull label is empty");
        }
        validate_pull_options_or_throw(options);
        std::optional<std::string> cursor =
            std::move(options.after_operation_id);
        std::optional<std::string> source_digest =
            std::move(options.expected_source_evidence_set_digest);
        std::optional<SyncReplicaReconciliationPayloadContinuation>
            payload_continuation =
                std::move(options.payload_continuation);

        for (std::uint64_t index = 0U;
             index < options.max_round_trips; ++index) {
            SyncReplicaOutboundReconciliation outbound =
                service.make_request_or_throw(
                    channel.delivery_authority(), cursor, source_digest,
                    payload_continuation);
            const SyncReplicaTlsRecordWriteUntilResult write =
                write_sync_replica_tls_owned_record_until_or_throw(
                    channel, std::move(outbound.request_frame),
                    service.max_request_frame_bytes(), options.deadline,
                    label + " request " + std::to_string(index + 1U));
            add_or_throw(
                result.request_frame_bytes_written,
                write.body_bytes_written,
                "reconciliation TLS request-frame-bytes");
            if (write.disposition !=
                SyncReplicaTlsRecordWriteUntilDisposition::Complete) {
                result.disposition = SyncReplicaReconciliationTlsPullDisposition::
                    RequestDeadlineExpired;
                result.has_more = true;
                result.next_after_operation_id = cursor;
                result.payload_continuation = payload_continuation;
                if (source_digest.has_value()) {
                    result.source_evidence_set_digest = *source_digest;
                }
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            }

            const SyncReplicaTlsRecordReadUntilResult read =
                read_sync_replica_tls_record_until_or_throw(
                    channel, service.max_response_frame_bytes(),
                    options.deadline,
                    label + " response " + std::to_string(index + 1U));
            add_or_throw(
                result.response_frame_bytes_received,
                read.body_bytes_received,
                "reconciliation TLS response-frame-bytes");
            if (read.disposition ==
                SyncReplicaTlsRecordReadUntilDisposition::PeerClosed) {
                result.disposition =
                    SyncReplicaReconciliationTlsPullDisposition::PeerClosed;
                result.has_more = true;
                result.next_after_operation_id = cursor;
                result.payload_continuation = payload_continuation;
                if (source_digest.has_value()) {
                    result.source_evidence_set_digest = *source_digest;
                }
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            }
            if (read.disposition ==
                SyncReplicaTlsRecordReadUntilDisposition::DeadlineExpired) {
                result.disposition = SyncReplicaReconciliationTlsPullDisposition::
                    ResponseDeadlineExpired;
                result.has_more = true;
                result.next_after_operation_id = cursor;
                result.payload_continuation = payload_continuation;
                if (source_digest.has_value()) {
                    result.source_evidence_set_digest = *source_digest;
                }
                discard_sync_replica_tls_authenticated_channel_noexcept(channel);
                return result;
            }

            const SyncReplicaReconciliationApplyResult applied =
                service.apply_response_or_throw(
                    channel.delivery_authority(), outbound.request,
                    read.frame);
            increment_or_throw(
                result.round_trips,
                "reconciliation TLS round-trips");
            observe_apply_result(applied, result);

            switch (applied.disposition) {
                case SyncReplicaReconciliationApplyDisposition::SourceChanged:
                    increment_or_throw(
                        result.source_resets,
                        "reconciliation TLS source-resets");
                    cursor.reset();
                    source_digest.reset();
                    payload_continuation.reset();
                    result.next_after_operation_id.reset();
                    result.has_more = true;
                    if (result.source_resets > options.max_source_resets) {
                        result.disposition =
                            SyncReplicaReconciliationTlsPullDisposition::
                                SourceChangedLimitReached;
                        discard_sync_replica_tls_authenticated_channel_noexcept(
                            channel);
                        return result;
                    }
                    continue;
                case SyncReplicaReconciliationApplyDisposition::
                    SourcePayloadUnavailable:
                    result.disposition =
                        SyncReplicaReconciliationTlsPullDisposition::
                            SourcePayloadUnavailable;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    return result;
                case SyncReplicaReconciliationApplyDisposition::
                    SourcePayloadPreparing:
                    increment_or_throw(
                        result.source_payload_preparing_responses,
                        "reconciliation TLS source-payload-preparing responses");
                    cursor = applied.next_after_operation_id;
                    // A preparing response deliberately carries no payload
                    // continuation. Preserve the requester's exact durable
                    // offset while the source completes its bounded manifest
                    // projection.
                    result.payload_continuation = payload_continuation;
                    // The protocol permits a pinned source digest only when a
                    // cursor or payload continuation grants continuation
                    // authority. A first-operation preparation pulse has
                    // neither, so its retry remains an unpinned initial page
                    // request while the source independently re-proves the
                    // exact operation and payload identity on every pulse.
                    if (cursor.has_value() ||
                        payload_continuation.has_value()) {
                        source_digest = applied.source_evidence_set_digest;
                    } else {
                        source_digest.reset();
                    }
                    if (index + 1U < options.max_round_trips) {
                        continue;
                    }
                    result.disposition =
                        SyncReplicaReconciliationTlsPullDisposition::
                            SourcePayloadPreparing;
                    result.has_more = true;
                    result.next_after_operation_id = cursor;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    return result;
                case SyncReplicaReconciliationApplyDisposition::
                    ReceiverCapacityBlocked:
                    result.disposition =
                        SyncReplicaReconciliationTlsPullDisposition::
                            ReceiverCapacityBlocked;
                    discard_sync_replica_tls_authenticated_channel_noexcept(
                        channel);
                    return result;
                case SyncReplicaReconciliationApplyDisposition::PayloadProgress:
                    if (!applied.payload_continuation.has_value()) {
                        throw std::logic_error(
                            label + " payload progress omitted its continuation");
                    }
                    cursor = applied.next_after_operation_id;
                    source_digest = applied.source_evidence_set_digest;
                    payload_continuation = applied.payload_continuation;
                    continue;
                case SyncReplicaReconciliationApplyDisposition::PageApplied:
                    increment_or_throw(
                        result.pages_applied,
                        "reconciliation TLS pages-applied");
                    if (!applied.has_more) {
                        result.disposition =
                            SyncReplicaReconciliationTlsPullDisposition::Complete;
                        discard_sync_replica_tls_authenticated_channel_noexcept(
                            channel);
                        return result;
                    }
                    payload_continuation.reset();
                    if (!applied.next_after_operation_id.has_value()) {
                        throw std::logic_error(
                            label + " nonterminal page omitted its continuation cursor");
                    }
                    cursor = applied.next_after_operation_id;
                    source_digest = applied.source_evidence_set_digest;
                    break;
            }
        }

        result.disposition = SyncReplicaReconciliationTlsPullDisposition::
            RoundTripLimitReached;
        result.has_more = true;
        result.next_after_operation_id = cursor;
        result.payload_continuation = payload_continuation;
        if (source_digest.has_value()) {
            result.source_evidence_set_digest = *source_digest;
        }
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        return result;
    } catch (...) {
        discard_sync_replica_tls_authenticated_channel_noexcept(channel);
        throw;
    }
}

SyncReplicaReconciliationTlsServeResult
serve_sync_replica_reconciliation_over_tls_or_throw(
    SyncReplicaReconciliationService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    SyncReplicaReconciliationTlsServeOptions options,
    const std::string& label) {
    return serve_impl_or_throw(
        service, channel, std::nullopt, std::move(options), label);
}

SyncReplicaReconciliationTlsServeResult
serve_sync_replica_reconciliation_after_first_request_over_tls_or_throw(
    SyncReplicaReconciliationService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string first_request_frame,
    SyncReplicaReconciliationTlsServeOptions options,
    const std::string& label) {
    return serve_impl_or_throw(
        service, channel, std::move(first_request_frame),
        std::move(options), label);
}

}  // namespace anonsync

#endif
