#pragma once

#if !defined(_WIN32)

#include "sync_replica_delivery_channel.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_reconciliation_compact_manifest.hpp"
#include "sync_replica_reconciliation_protocol.hpp"
#include "sync_replica_sqlite_owner.hpp"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

// Cross-file discovery is local acceleration, not permission for one wrong
// multi-terabyte candidate to monopolize an authenticated service turn. One
// apply call may extend at most this many candidate bytes. Progress is retained
// only in process memory and every later step reopens and re-proves the exact
// payload observation. Completed chunks may be reused immediately; the source
// whole digest is still required before the projection becomes a complete
// cached manifest.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply =
        32ULL * 1024ULL * 1024ULL;

// Source-side adaptive-manifest construction is local work and must not let one
// authenticated request monopolize the owner thread while hashing a multi-
// terabyte payload. One request may consume at most this many exact source
// bytes. The process-lifetime reconciliation owner retains only bounded hashing
// and chunk-frontier state; every later request reopens and re-proves the exact
// immutable payload observation before resuming.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest =
        32ULL * 1024ULL * 1024ULL;

// Durable source-manifest acceleration is intentionally coarser than the
// owner-thread fairness pulse. Publishing an atomic checkpoint after every
// 32 MiB pulse would turn a 4 TiB cold source into 131,072 file fsync/rename/
// directory-fsync sequences. The first exact pulse is published immediately;
// later active records advance only after another 1 GiB, while completion is
// always published. A crash therefore loses at most one bounded 1 GiB interval
// instead of the whole payload, without making checkpoint I/O the dominant
// source-preparation cost.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationSourceManifestCheckpointPublicationIntervalBytes =
        1ULL * 1024ULL * 1024ULL * 1024ULL;
static_assert(
    kSyncReplicaReconciliationSourceManifestCheckpointPublicationIntervalBytes >=
    kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest);

// Same-path predecessors are the first and usually best delta source, but
// constructing their adaptive manifest must not turn one authenticated apply
// into a complete multi-terabyte local read. One apply may advance at most this
// many predecessor bytes. The process-local projection survives later applies
// by the same service owner; every step reopens and re-proves the exact source
// payload observation, and completed chunks may be reused before the source
// whole digest is known. Final target publication still requires the exact
// whole-target SHA-256.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply =
        32ULL * 1024ULL * 1024ULL;

// A matched adaptive chunk can be very large at the multi-terabyte payload
// ceiling. Local delta reuse is therefore a separate bounded operation from
// wire framing and candidate projection. One apply call may read at most this
// many bytes from same-path or cross-file candidates in aggregate. Exact
// durable-prefix continuation permits the next authenticated turn to resume
// inside the same chunk without copying or retaining a chunk-sized buffer.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply =
        32ULL * 1024ULL * 1024ULL;

// Local copy staging owns one bounded byte string at a time. Its granularity is
// product-owned rather than negotiated from the peer's wire range: an
// artificially tiny network frame must not turn one local-copy budget into
// millions of descriptor reopen, hash, fsync, and rename effects.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumLocalReuseRangeBytes =
        4ULL * 1024ULL * 1024ULL;
static_assert(
    kSyncReplicaReconciliationMaximumLocalReuseRangeBytes <=
    kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply);

// Once all source bytes are durably staged, terminal whole-target SHA-256 is
// receiver-local work. One authenticated apply may advance this many fixed
// 32 MiB store steps before yielding an exact payload-cold continuation. The
// default therefore verifies at most 1 GiB per apply with fixed memory while
// avoiding one peer turn for every individual hash checkpoint.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply = 32U;

struct SyncReplicaOutboundReconciliation final {
    SyncReplicaReconciliationRequest request;
    std::string request_frame;
    std::string request_digest;

    bool operator==(const SyncReplicaOutboundReconciliation&) const = default;
};

struct SyncReplicaInboundReconciliation final {
    SyncReplicaReconciliationRequest request;
    SyncReplicaReconciliationResponse response;
    std::string response_frame;

    bool operator==(const SyncReplicaInboundReconciliation&) const = default;
};

// Shipping source result. response contains complete canonical metadata and
// per-range digests, while each payload.bytes string is empty; response_frame
// is the sole payload-sized owner. Exact source descriptors have already been
// released before this object can cross into TLS backpressure.
struct SyncReplicaFramedInboundReconciliation final {
    SyncReplicaReconciliationRequest request;
    // Metadata-only process view. When a complete source manifest was framed
    // directly from the retained compact sequence, response intentionally
    // omits that owning vector; response_frame remains the complete canonical
    // generation-9 response and the compatibility API decodes it normally.
    SyncReplicaReconciliationResponse response;
    std::string response_frame;
    std::uint64_t direct_payload_ranges = 0U;
    std::uint64_t direct_payload_bytes = 0U;
    // Shipping direct-fill framing owns no aggregate payload page and no
    // range-sized source staging buffer beside the final response frame.
    std::uint64_t direct_frame_payload_page_bytes_at_reservation = 0U;
    std::uint64_t direct_frame_maximum_source_staging_bytes = 0U;
    std::uint64_t direct_frame_borrowed_manifest_count = 0U;
    std::uint64_t direct_frame_borrowed_manifest_chunks = 0U;
    std::uint64_t direct_frame_manifest_materialization_bytes = 0U;
    // A terminal ranged response may release the one completed compact source
    // manifest after canonical framing and exact durable-checkpoint
    // publication. A lost response can rehydrate the same bounded sequence
    // from that checkpoint without source-byte hashing.
    std::uint64_t source_manifest_cache_terminal_releases = 0U;
    std::uint64_t source_manifest_cache_terminal_released_capacity_bytes = 0U;
    // Exact source descriptors are bounded by max_payloads_per_page and are
    // released before this result can enter TLS backpressure.
    std::uint64_t direct_frame_open_source_descriptors_at_reservation = 0U;
};

// Session-local channel identity and bounded telemetry for one authenticated
// reconciliation stream. Payload access remains request-scoped: every
// payload-bearing request opens the selected digest under a fresh shared store
// lease and releases every descriptor and namespace-wide capability before
// returning. The service, not the session, owns the single bounded source
// manifest projection so an intentionally yielded hash can resume across fresh
// authenticated sessions. That projection is acceleration only and is discarded
// whenever exact content identity or source metadata changes.
class SyncReplicaReconciliationServeSession final {
public:
    SyncReplicaReconciliationServeSession(
        const SyncReplicaReconciliationServeSession&) = delete;
    SyncReplicaReconciliationServeSession& operator=(
        const SyncReplicaReconciliationServeSession&) = delete;
    SyncReplicaReconciliationServeSession(
        SyncReplicaReconciliationServeSession&&) noexcept = default;
    SyncReplicaReconciliationServeSession& operator=(
        SyncReplicaReconciliationServeSession&&) noexcept = default;
    ~SyncReplicaReconciliationServeSession() noexcept = default;

    [[nodiscard]] std::uint64_t payload_targeted_access_births() const noexcept {
        return payload_targeted_access_births_;
    }

    [[nodiscard]] std::uint64_t payload_targeted_open_attempts() const noexcept {
        return payload_targeted_open_attempts_;
    }

    [[nodiscard]] std::uint64_t payload_targeted_opens() const noexcept {
        return payload_targeted_opens_;
    }

    [[nodiscard]] std::uint64_t content_defined_manifest_scans() const noexcept {
        return content_defined_manifest_scans_;
    }

    [[nodiscard]] std::uint64_t content_defined_manifest_reuses() const noexcept {
        return content_defined_manifest_reuses_;
    }

    [[nodiscard]] std::uint64_t
    content_defined_manifest_hashed_bytes() const noexcept {
        return content_defined_manifest_hashed_bytes_;
    }

    [[nodiscard]] std::uint64_t
    content_defined_manifest_projection_steps() const noexcept {
        return content_defined_manifest_projection_steps_;
    }

    [[nodiscard]] std::uint64_t
    content_defined_manifest_projection_restarts() const noexcept {
        return content_defined_manifest_projection_restarts_;
    }

    [[nodiscard]] std::uint64_t
    source_payload_preparing_responses() const noexcept {
        return source_payload_preparing_responses_;
    }

    [[nodiscard]] std::uint64_t content_defined_manifest_publications() const noexcept {
        return content_defined_manifest_publications_;
    }

    [[nodiscard]] std::uint64_t content_defined_manifest_references() const noexcept {
        return content_defined_manifest_references_;
    }

    [[nodiscard]] std::uint64_t content_defined_chunk_index_builds() const noexcept {
        return content_defined_chunk_index_builds_;
    }

    [[nodiscard]] std::uint64_t content_defined_chunk_index_reuses() const noexcept {
        return content_defined_chunk_index_reuses_;
    }

    [[nodiscard]] std::uint64_t content_defined_chunk_index_lookups() const noexcept {
        return content_defined_chunk_index_lookups_;
    }

    [[nodiscard]] std::uint64_t ranged_payload_windows() const noexcept {
        return ranged_payload_windows_;
    }

    [[nodiscard]] std::uint64_t ranged_payload_ranges() const noexcept {
        return ranged_payload_ranges_;
    }

    [[nodiscard]] std::uint64_t ranged_payload_bytes() const noexcept {
        return ranged_payload_bytes_;
    }

private:
    SyncReplicaReconciliationServeSession(
        std::string folder_id,
        SyncReplicaActor local_actor,
        SyncReplicaActor peer_actor,
        SyncReplicaDeliveryChannelBinding channel_binding);

    std::string folder_id_;
    SyncReplicaActor local_actor_;
    SyncReplicaActor peer_actor_;
    SyncReplicaDeliveryChannelBinding channel_binding_;
    std::uint64_t payload_targeted_access_births_ = 0U;
    std::uint64_t payload_targeted_open_attempts_ = 0U;
    std::uint64_t payload_targeted_opens_ = 0U;
    std::uint64_t content_defined_manifest_scans_ = 0U;
    std::uint64_t content_defined_manifest_reuses_ = 0U;
    std::uint64_t content_defined_manifest_hashed_bytes_ = 0U;
    std::uint64_t content_defined_manifest_projection_steps_ = 0U;
    std::uint64_t content_defined_manifest_projection_restarts_ = 0U;
    std::uint64_t source_payload_preparing_responses_ = 0U;
    std::uint64_t content_defined_manifest_publications_ = 0U;
    std::uint64_t content_defined_manifest_references_ = 0U;
    std::uint64_t content_defined_chunk_index_builds_ = 0U;
    std::uint64_t content_defined_chunk_index_reuses_ = 0U;
    std::uint64_t content_defined_chunk_index_lookups_ = 0U;
    std::uint64_t ranged_payload_windows_ = 0U;
    std::uint64_t ranged_payload_ranges_ = 0U;
    std::uint64_t ranged_payload_bytes_ = 0U;

    friend class SyncReplicaReconciliationService;
};

enum class SyncReplicaReconciliationApplyDisposition : std::uint8_t {
    PageApplied = 1U,
    SourceChanged = 2U,
    SourcePayloadUnavailable = 3U,
    ReceiverCapacityBlocked = 4U,
    PayloadProgress = 5U,
    SourcePayloadPreparing = 6U,
};

struct SyncReplicaReconciliationApplyResult final {
    SyncReplicaReconciliationApplyDisposition disposition =
        SyncReplicaReconciliationApplyDisposition::PageApplied;
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
    // Bytes actually read from immutable local candidate payloads. This may be
    // greater than accepted bytes when an already durable prefix advances the
    // staging cutpoint concurrently with the candidate read.
    std::uint64_t delta_local_reuse_read_ranges = 0U;
    std::uint64_t delta_local_reuse_read_bytes = 0U;
    std::uint64_t delta_local_reuse_maximum_read_range_bytes = 0U;
    std::uint64_t delta_local_reuse_budget_exhaustions = 0U;
    std::uint64_t delta_local_reuse_interior_resumptions = 0U;
    // Authenticated wire bytes which do not need to be staged again because
    // bounded local reuse advanced the exact durable prefix after the peer had
    // already framed them. A range is counted once when any of its bytes are
    // already durable; overlap_trimmed_ranges is the strict partial-overlap
    // subset whose advancing suffix is rehashed and staged normally.
    std::uint64_t delta_wire_already_durable_ranges = 0U;
    std::uint64_t delta_wire_already_durable_bytes = 0U;
    std::uint64_t delta_wire_overlap_trimmed_ranges = 0U;
    // scans counts only a completed exact predecessor manifest. hashed_bytes
    // counts the actual bounded source bytes consumed in this apply, including
    // nonterminal projection steps whose completed chunks may already provide
    // safe local delta acceleration.
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
    std::uint64_t source_state_generation = 0U;
    std::uint64_t source_evidence_count = 0U;
    std::string source_evidence_set_digest;
    bool has_more = false;
    std::optional<std::string> next_after_operation_id;
    std::optional<std::string> blocked_operation_id;
    std::optional<SyncReplicaReconciliationPayloadContinuation>
        payload_continuation;

    bool operator==(const SyncReplicaReconciliationApplyResult&) const =
        default;
};

// Filesystem-cold owner-thread projection of the one source manifest currently
// being prepared. This is acceleration state only: it owns no descriptor,
// payload-store lease, authenticated channel, request cursor, or transfer
// authority. A bounded checksum-framed payload-root checkpoint may rehydrate
// it after restart; stale, absent, or unusable checkpoint state is discarded
// and ordinary exact source hashing begins conservatively.
struct SyncReplicaReconciliationSourceManifestProjectionStatus final {
    bool pending = false;
    std::string operation_id;
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t next_offset_bytes = 0U;
    std::uint64_t completed_chunk_count = 0U;

    bool operator==(
        const SyncReplicaReconciliationSourceManifestProjectionStatus&) const =
        default;
};

// Filesystem-cold owner-thread view of the one completed compact source
// manifest retained for ranged publication. This is process acceleration only;
// it owns no descriptor, payload-store lease, channel, or transfer authority.
// The exact durable-checkpoint flag means this same operation/manifest may be
// discarded and later rehydrated without rereading source bytes.
struct SyncReplicaReconciliationSourceManifestCacheStatus final {
    bool resident = false;
    std::string operation_id;
    std::string canonical_path;
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::string manifest_digest;
    std::uint64_t chunk_count = 0U;
    std::uint64_t retained_chunk_capacity_bytes = 0U;
    bool exact_complete_checkpoint_durable = false;
    std::uint64_t complete_checkpoint_restorations = 0U;
    std::uint64_t terminal_releases = 0U;
    std::uint64_t terminal_released_capacity_bytes = 0U;

    bool operator==(
        const SyncReplicaReconciliationSourceManifestCacheStatus&) const =
        default;
};

enum class SyncReplicaReconciliationSourceManifestProjectionStepDisposition
    : std::uint8_t {
    NoPendingWork = 1U,
    Progress = 2U,
    Completed = 3U,
    PayloadUnavailable = 4U,
};

[[nodiscard]] std::string_view
sync_replica_reconciliation_source_manifest_projection_step_disposition_name(
    SyncReplicaReconciliationSourceManifestProjectionStepDisposition
        disposition) noexcept;

// Result of one bounded source-local projection pulse. Every nonempty pulse
// reopens and re-proves the exact digest-named payload, consumes at most the
// service's configured 32 MiB frontier, and releases all payload authority
// before returning. Progress may advance one coarser durable acceleration
// checkpoint and completion publishes a bounded reusable manifest; neither
// mutates replica, catalog, or payload bytes or grants transfer authority.
struct SyncReplicaReconciliationSourceManifestProjectionStepResult final {
    SyncReplicaReconciliationSourceManifestProjectionStepDisposition
        disposition =
            SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                NoPendingWork;
    SyncReplicaReconciliationSourceManifestProjectionStatus before;
    SyncReplicaReconciliationSourceManifestProjectionStatus after;
    std::uint64_t hashed_bytes = 0U;
    std::uint64_t newly_completed_chunk_count = 0U;
    bool projection_restarted = false;

    bool operator==(
        const SyncReplicaReconciliationSourceManifestProjectionStepResult&)
        const = default;
};

// A bounded pull-side anti-entropy seam. It deliberately enumerates the
// share-global retained evidence set rather than destination outbox rows. The
// lower transport supplies one live authenticated channel capability; this
// service constructs/serves one exact page and idempotently imports it. It owns
// no socket, retry loop, discovery, or daemon lifetime.
class SyncReplicaReconciliationService final {
public:
    SyncReplicaReconciliationService(
        SyncReplicaSqliteOwner& owner,
        SyncReplicaFilePayloadStore& payload_store,
        SyncReplicaReconciliationProtocolLimits limits = {},
        std::string label = "sync replica reconciliation service",
        SyncReplicaSelectiveSyncPolicy selective_sync_policy =
            sync_replica_default_selective_sync_policy(),
        std::uint64_t max_local_reuse_bytes_per_apply =
            kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply,
        std::uint64_t max_predecessor_projection_bytes_per_apply =
            kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply,
        std::uint64_t max_terminal_verification_steps_per_apply =
            kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply,
        std::uint64_t max_source_manifest_projection_bytes_per_request =
            kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest);

    SyncReplicaReconciliationService(
        const SyncReplicaReconciliationService&) = delete;
    SyncReplicaReconciliationService& operator=(
        const SyncReplicaReconciliationService&) = delete;
    SyncReplicaReconciliationService(
        SyncReplicaReconciliationService&&) = delete;
    SyncReplicaReconciliationService& operator=(
        SyncReplicaReconciliationService&&) = delete;

    [[nodiscard]] const std::string& folder_id() const noexcept {
        return folder_id_;
    }

    [[nodiscard]] const SyncReplicaActor& local_actor() const noexcept {
        return local_actor_;
    }

    [[nodiscard]] std::uint64_t max_request_frame_bytes() const noexcept {
        return protocol_limits_.max_request_frame_bytes;
    }

    [[nodiscard]] std::uint64_t max_response_frame_bytes() const noexcept {
        return protocol_limits_.max_response_frame_bytes;
    }

    [[nodiscard]] SyncReplicaOutboundReconciliation make_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::optional<std::string> after_operation_id = std::nullopt,
        std::optional<std::string> expected_source_evidence_set_digest =
            std::nullopt,
        std::optional<SyncReplicaReconciliationPayloadContinuation>
            payload_continuation = std::nullopt);

    [[nodiscard]] SyncReplicaReconciliationServeSession
    make_serve_session_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel);

    [[nodiscard]] SyncReplicaInboundReconciliation serve_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string_view request_frame);

    [[nodiscard]] SyncReplicaInboundReconciliation serve_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string_view request_frame,
        SyncReplicaReconciliationServeSession& session);

    [[nodiscard]] SyncReplicaFramedInboundReconciliation
    serve_request_frame_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string_view request_frame);

    [[nodiscard]] SyncReplicaFramedInboundReconciliation
    serve_request_frame_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string_view request_frame,
        SyncReplicaReconciliationServeSession& session);

    [[nodiscard]]
    SyncReplicaReconciliationSourceManifestProjectionStatus
    source_manifest_projection_status() const;

    [[nodiscard]] SyncReplicaReconciliationSourceManifestCacheStatus
    source_manifest_cache_status() const;

    // Performs the one bounded durable-record and targeted causal-path
    // discovery needed after process restart. The ordinary status accessor
    // remains filesystem-cold; the retained peer-service owner invokes this
    // explicit effect before selecting local source work.
    [[nodiscard]]
    SyncReplicaReconciliationSourceManifestProjectionStatus
    discover_source_manifest_projection_or_throw();

    // Advances one already-discovered source projection without requiring an
    // authenticated peer request. First discovery still occurs only while
    // serving exact retained causal evidence. This method is intended for the
    // retained single-threaded peer-service scheduler, which must interleave an
    // ordinary owner turn between calls.
    [[nodiscard]]
    SyncReplicaReconciliationSourceManifestProjectionStepResult
    continue_source_manifest_projection_or_throw();

    [[nodiscard]] SyncReplicaReconciliationApplyResult
    apply_response_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const SyncReplicaReconciliationRequest& expected_request,
        std::string_view response_frame);

private:
    struct CachedSourceContentDefinedManifest final {
        std::string operation_id;
        std::string canonical_path;
        std::string content_sha256;
        std::uint64_t total_size_bytes = 0U;
        SyncPosixRegularFileSnapshotMetadata source_metadata;
        std::string manifest_digest;
        SyncReplicaReconciliationCompactManifest manifest;
    };

    struct SourceContentDefinedProjection final {
        SyncReplicaOperation source_operation;
        std::string content_sha256;
        std::uint64_t total_size_bytes = 0U;
        SyncPosixRegularFileSnapshotMetadata source_metadata;
        SyncReplicaContentDefinedChunkingParameters parameters;
        SyncReplicaFilePayloadStoreContentDefinedProjection projection;
    };

    struct SourceContentDefinedProjectionAdvance final {
        std::uint64_t hashed_bytes = 0U;
        std::uint64_t newly_completed_chunk_count = 0U;
        bool projection_restarted = false;
        bool completed = false;
    };

    struct CachedTargetContentDefinedManifest final {
        std::string operation_id;
        std::string content_sha256;
        std::uint64_t total_size_bytes = 0U;
        std::string manifest_digest;
        SyncReplicaReconciliationDeltaManifest manifest;
        std::vector<std::uint64_t> chunk_offsets;
    };

    struct CachedPredecessorContentDefinedManifest final {
        std::string target_operation_id;
        std::string target_manifest_digest;
        std::string predecessor_operation_id;
        SyncPosixRegularFileSnapshotMetadata source_metadata;
        SyncReplicaFilePayloadStoreContentDefinedManifest manifest;
        // Stable digest order for lower_bound. Building this vector once per
        // predecessor avoids allocating and sorting 8,192 indices for every
        // bounded wire range of one large target payload.
        std::vector<std::size_t> digest_order;
        std::vector<std::uint64_t> chunk_offsets;
    };

    struct PredecessorContentDefinedProjection final {
        std::string target_operation_id;
        std::string target_manifest_digest;
        SyncReplicaOperation source_operation;
        SyncPosixRegularFileSnapshotMetadata source_metadata;
        SyncReplicaFilePayloadStoreContentDefinedProjection projection;
        std::vector<std::size_t> digest_order;
        std::vector<std::uint64_t> chunk_offsets{0U};
        std::size_t indexed_chunk_count = 0U;
    };


    struct CrossFileContentDefinedSearch final {
        std::string target_operation_id;
        std::string target_manifest_digest;
        std::optional<std::string> source_visible_state_digest;
        std::optional<std::string> next_page_after_canonical_path;
        std::vector<SyncReplicaOperation> pending_file_operations;
        std::size_t next_pending_file_operation = 0U;
        std::string pending_page_tail_canonical_path;
        bool pending_page_has_more = false;
        bool pending_page_loaded = false;
        std::optional<std::uint64_t>
            payload_availability_generation_at_sweep_start;
        bool exhausted = false;
    };

    struct CachedCrossFileContentDefinedManifest final {
        std::string target_operation_id;
        std::string target_manifest_digest;
        SyncReplicaOperation source_operation;
        SyncPosixRegularFileSnapshotMetadata source_metadata;
        SyncReplicaFilePayloadStoreContentDefinedManifest manifest;
        std::vector<std::size_t> digest_order;
        std::vector<std::uint64_t> chunk_offsets;
    };

    struct CrossFileContentDefinedProjection final {
        std::string target_operation_id;
        std::string target_manifest_digest;
        SyncReplicaOperation source_operation;
        SyncPosixRegularFileSnapshotMetadata source_metadata;
        SyncReplicaFilePayloadStoreContentDefinedProjection projection;
        std::vector<std::size_t> digest_order;
        std::vector<std::uint64_t> chunk_offsets{0U};
        std::size_t indexed_chunk_count = 0U;
        bool candidate_match_observed = false;
    };

    void require_current_owner_identity_or_throw(
        const std::string& operation_label);

    void validate_channel_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const std::string& operation_label) const;

    void validate_serve_session_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const SyncReplicaReconciliationServeSession& session,
        const std::string& operation_label) const;

    // Hydrates one exact active byte frontier or complete manifest before a payload
    // descriptor is opened. This preserves the payload-store lock order:
    // store-global checkpoint observation always precedes the exact payload
    // inode lease retained by OpenedPayload.
    void restore_source_content_defined_checkpoint_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        const SyncReplicaContentDefinedChunkingParameters& parameters,
        std::string_view operation_label);

    void install_source_content_defined_checkpoint_for_operation_or_throw(
        SyncReplicaSourceManifestCheckpoint checkpoint,
        const SyncReplicaOperation& operation,
        const SyncReplicaContentDefinedChunkingParameters& parameters,
        std::string_view operation_label);

    // On the first eligible source-local scheduler turn, discovers the one
    // durable obligation without a peer request. The checkpoint is observed
    // before any payload descriptor, then bound through one path-local SQLite
    // cutpoint. Failure or staleness only discards optional acceleration.
    void restore_source_content_defined_checkpoint_without_peer_or_throw();

    [[nodiscard]] SourceContentDefinedProjectionAdvance
    advance_source_content_defined_projection_or_throw(
        const SyncReplicaOperation& operation,
        SyncReplicaFilePayloadStoreOpenedPayload& opened,
        std::string_view operation_label);

    void publish_pending_source_manifest_checkpoint_if_possible_or_throw(
        std::string_view operation_label);

    [[nodiscard]] std::uint64_t
    release_terminal_source_manifest_cache_if_possible_or_throw(
        const SyncReplicaOperation& operation);

    SyncReplicaSqliteOwner& owner_;
    SyncReplicaFilePayloadStore& payload_store_;
    SyncReplicaReconciliationProtocolLimits protocol_limits_;
    std::uint64_t max_local_reuse_bytes_per_apply_ =
        kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply;
    std::uint64_t max_predecessor_projection_bytes_per_apply_ =
        kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply;
    std::uint64_t max_terminal_verification_steps_per_apply_ =
        kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply;
    std::uint64_t max_source_manifest_projection_bytes_per_request_ =
        kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest;
    std::string label_;
    std::string folder_id_;
    SyncReplicaActor local_actor_;
    SyncReplicaSelectiveSyncPolicy selective_sync_policy_;
    // Source-side content-defined projection is acceleration, not payload or
    // protocol authority. At most one bounded incomplete source projection and
    // one bounded completed manifest are retained in memory. One additional
    // checksum-framed payload-root record survives restart at an exact byte
    // frontier or as the complete <=8,192-chunk manifest. Every use still
    // reopens the digest-named payload and requires exact private inode
    // metadata. No global chunk index or unbounded tree-sized state is created.
    std::optional<CachedSourceContentDefinedManifest>
        source_content_defined_manifest_;
    std::optional<SourceContentDefinedProjection>
        source_content_defined_projection_;
    // Process witness for the newest exact durable byte frontier already
    // observed or published for one operation. Active records are intentionally
    // coarser than fairness pulses; a lease-busy or typed atomic-publication
    // failure retains only bounded pending acceleration for a later turn.
    std::string source_durable_checkpoint_operation_id_;
    std::uint64_t source_durable_checkpoint_next_offset_bytes_ = 0U;
    bool source_durable_checkpoint_complete_ = false;
    std::string source_durable_checkpoint_manifest_digest_;
    bool source_durable_checkpoint_scheduler_restore_attempted_ = false;
    std::optional<SyncReplicaSourceManifestCheckpoint>
        pending_source_manifest_checkpoint_;
    std::uint64_t source_manifest_complete_checkpoint_restorations_ = 0U;
    std::uint64_t source_manifest_cache_terminal_releases_ = 0U;
    std::uint64_t source_manifest_cache_terminal_released_capacity_bytes_ =
        0U;
    // Receiver-side target, predecessor, and cross-file acceleration survives
    // bounded range requests for one exact target operation. Payload objects
    // are immutable and every reused range is reopened and re-proved. The
    // incomplete predecessor/cross-file projections are process-local only;
    // they avoid one complete multi-terabyte source read per apply without
    // becoming durable or admission authority. Every retained digest/offset
    // index remains bounded by the 8,192-chunk protocol frontier.
    std::optional<CachedTargetContentDefinedManifest>
        delta_target_manifest_;
    std::optional<CachedPredecessorContentDefinedManifest>
        delta_predecessor_manifest_;
    std::optional<PredecessorContentDefinedProjection>
        delta_predecessor_projection_;
    std::optional<CrossFileContentDefinedSearch>
        delta_cross_file_search_;
    std::optional<CrossFileContentDefinedProjection>
        delta_cross_file_projection_;
    std::optional<CachedCrossFileContentDefinedManifest>
        delta_cross_file_manifest_;
};

}  // namespace anonsync

#endif
