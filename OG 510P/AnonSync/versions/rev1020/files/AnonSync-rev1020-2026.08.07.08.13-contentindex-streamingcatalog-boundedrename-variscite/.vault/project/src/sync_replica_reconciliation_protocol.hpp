#pragma once

#include "sync_replica_content_defined_chunker.hpp"
#include "sync_replica_delivery_protocol.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_payload_extent.hpp"
#include "sha256_digest.hpp"
#include "sync_replica_selective_sync_policy.hpp"

#include <cstdint>
#include <cstddef>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>
#include <vector>

namespace anonsync {

inline constexpr std::uint32_t kSyncReplicaReconciliationProtocolVersion = 9U;
// Content-defined manifests resynchronize after insertion or deletion instead
// of invalidating every later fixed offset. The minimum average matches the
// ordinary wire range. Average size doubles only when needed to keep a normal
// manifest near 4,096 chunks; the independent 8,192-record hard frontier still
// covers the exact 4 TiB payload ceiling even if every chunk ends at its
// minimum size. Boundary hashes are scheduling hints; SHA-256 remains chunk and
// whole-payload authority.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMinimumAverageChunkBytes =
        4ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumAverageChunkBytes =
        1024ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumContentDefinedChunks = 8192U;
static_assert(
    (kSyncReplicaReconciliationMaximumAverageChunkBytes / 2U) *
            kSyncReplicaReconciliationMaximumContentDefinedChunks ==
        kSyncReplicaMaximumPayloadExtentBytes);
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxOperationsPerPage = 128U;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxCanonicalOperationBytesPerPage =
        16ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxPayloadsPerPage = 128U;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxSinglePayloadBytes =
        4ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage =
        64ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxPayloadExtentBytes =
        kSyncReplicaDefaultMaximumPayloadExtentBytes;

// Public limit objects may reduce these frontiers but may not silently raise
// the shipping memory and descriptor boundary. This keeps an erroneous or
// hostile in-process caller from converting one bounded generation-9 page
// into an unbounded operation vector, descriptor fanout, payload owner, or
// response frame.
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumOperationsPerPage =
        kSyncReplicaReconciliationDefaultMaxOperationsPerPage;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumCanonicalOperationBytesPerPage =
        kSyncReplicaReconciliationDefaultMaxCanonicalOperationBytesPerPage;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumPayloadsPerPage =
        kSyncReplicaReconciliationDefaultMaxPayloadsPerPage;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumSinglePayloadBytes =
        kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumPayloadBytesPerPage =
        kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage;

// The deployment ceiling bounds one complete retained payload. The wire-range
// ceiling is deliberately independent: deployments may admit larger files
// without silently returning to whole-file framing. Keeping this composition
// policy beside the protocol constant prevents CLI, retained-service, and
// sync-once owners from drifting apart.
[[nodiscard]] constexpr std::uint64_t
sync_replica_reconciliation_single_payload_limit(
    std::uint64_t max_payload_bytes) noexcept {
    return max_payload_bytes <
            kSyncReplicaReconciliationDefaultMaxSinglePayloadBytes
        ? max_payload_bytes
        : kSyncReplicaReconciliationDefaultMaxSinglePayloadBytes;
}
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxRequestFrameBytes = 128ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationDefaultMaxResponseFrameBytes =
        96ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumRequestFrameBytes =
        kSyncReplicaReconciliationDefaultMaxRequestFrameBytes;
inline constexpr std::uint64_t
    kSyncReplicaReconciliationMaximumResponseFrameBytes =
        kSyncReplicaReconciliationDefaultMaxResponseFrameBytes;

// Bounded share-global anti-entropy. The operation and payload ceilings are
// independent: a page may contain many tombstones, while identical file bytes
// are transmitted once even when several operations refer to the same digest.
struct SyncReplicaReconciliationProtocolLimits final {
    SyncReplicaModelLimits model;
    std::uint64_t max_operations_per_page =
        kSyncReplicaReconciliationDefaultMaxOperationsPerPage;
    std::uint64_t max_canonical_operation_bytes_per_page =
        kSyncReplicaReconciliationDefaultMaxCanonicalOperationBytesPerPage;
    std::uint64_t max_payloads_per_page =
        kSyncReplicaReconciliationDefaultMaxPayloadsPerPage;
    std::uint64_t max_single_payload_bytes =
        kSyncReplicaReconciliationDefaultMaxSinglePayloadBytes;
    std::uint64_t max_payload_bytes_per_page =
        kSyncReplicaReconciliationDefaultMaxPayloadBytesPerPage;
    // Complete retained-file extent. This is deliberately independent from
    // the bytes in one response page; one file may require many bounded pages.
    std::uint64_t max_payload_extent_bytes =
        kSyncReplicaReconciliationDefaultMaxPayloadExtentBytes;
    std::uint64_t max_request_frame_bytes =
        kSyncReplicaReconciliationDefaultMaxRequestFrameBytes;
    std::uint64_t max_response_frame_bytes =
        kSyncReplicaReconciliationDefaultMaxResponseFrameBytes;

    bool operator==(const SyncReplicaReconciliationProtocolLimits&) const =
        default;
};

void validate_sync_replica_reconciliation_protocol_limits_or_throw(
    const SyncReplicaReconciliationProtocolLimits& limits);

// Cheap classifier used only after the TLS record layer has delivered one
// complete bounded frame. A positive result selects the reconciliation decoder;
// it is not validation or authorization.
[[nodiscard]] bool sync_replica_reconciliation_request_frame_has_magic(
    std::string_view frame) noexcept;

struct SyncReplicaReconciliationPayloadContinuation final {
    std::string operation_id;
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t next_offset_bytes = 0U;

    bool operator==(
        const SyncReplicaReconciliationPayloadContinuation&) const = default;
};

// The first request has no cursor. Every page or payload continuation is paired
// with the exact source evidence-set digest observed on the preceding response.
// This prevents a lexical cursor or byte offset from silently continuing across
// a changing source evidence set.
struct SyncReplicaReconciliationRequest final {
    std::string folder_id;
    SyncReplicaActor requester_actor;
    SyncReplicaActor responder_actor;
    SyncReplicaDeliveryChannelBinding channel_binding;
    std::optional<std::string> after_operation_id;
    std::optional<std::string> expected_source_evidence_set_digest;
    std::optional<SyncReplicaReconciliationPayloadContinuation>
        payload_continuation;
    // A receiver may retain the complete target content-defined manifest in
    // process across bounded range-window continuations. Advertising its exact
    // digest lets the source send only constant-size references instead of
    // copying as many as 8,192 chunk records into every range record. This is
    // deliberately request-local and non-durable: a restarted receiver omits
    // the field and receives the complete manifest again before it can use
    // local predecessor bytes.
    std::optional<std::string> cached_delta_manifest_digest;
    // The requester, not the source, decides which visible file values require
    // payload bytes. The complete bounded canonical policy is bound into every
    // request digest so a cursor or range continuation cannot silently cross a
    // selection change.
    SyncReplicaSelectiveSyncPolicy selective_sync_policy =
        sync_replica_default_selective_sync_policy();

    bool operator==(const SyncReplicaReconciliationRequest&) const = default;
};

// Canonical whole-file content-defined projection. Chunk offsets are the
// cumulative preceding sizes. One bounded response may carry several
// contiguous chunk-confined ranges for one large payload. The complete bounded
// manifest appears on the first range of a cache-cold window; later ranges in
// that response and later continuation responses carry only its digest plus
// the exact containing chunk extent.
struct SyncReplicaReconciliationDeltaChunk final {
    SyncReplicaReconciliationDeltaChunk(
        std::uint64_t size,
        std::string_view digest)
        : size_bytes(size), sha256(digest) {}
    SyncReplicaReconciliationDeltaChunk(
        std::uint64_t size,
        Sha256DigestValue digest)
        : size_bytes(size), sha256(std::move(digest)) {}

    std::uint64_t size_bytes = 0U;
    Sha256DigestValue sha256;

    bool operator==(const SyncReplicaReconciliationDeltaChunk&) const = default;
};

static_assert(
    sizeof(SyncReplicaReconciliationDeltaChunk) == 40U,
    "wire-facing content-defined chunks must remain fixed 40-byte records");
static_assert(
    std::is_trivially_copyable_v<SyncReplicaReconciliationDeltaChunk>,
    "wire-facing content-defined chunks must not own hidden heap state");

struct SyncReplicaReconciliationDeltaManifest final {
    SyncReplicaContentDefinedChunkingParameters parameters;
    std::vector<SyncReplicaReconciliationDeltaChunk> chunks;

    bool operator==(const SyncReplicaReconciliationDeltaManifest&) const =
        default;
};

// Non-owning direct-frame source record. The cumulative exclusive end offset
// is the exact process-retained compact representation; generation-9 framing
// derives each wire chunk size from the preceding end without first rebuilding
// an owning SyncReplicaReconciliationDeltaManifest. The record is fixed-width,
// trivially copyable, and carries no lifetime authority of its own.
struct SyncReplicaReconciliationCumulativeDeltaChunk final {
    std::uint64_t end_offset_bytes = 0U;
    Sha256DigestValue sha256;

    bool operator==(
        const SyncReplicaReconciliationCumulativeDeltaChunk&) const = default;
};

static_assert(
    sizeof(SyncReplicaReconciliationCumulativeDeltaChunk) == 40U,
    "cumulative content-defined chunks must remain 40-byte records");
static_assert(
    std::is_trivially_copyable_v<
        SyncReplicaReconciliationCumulativeDeltaChunk>,
    "cumulative content-defined chunks must not own hidden heap state");

// Borrowed complete manifest used only while one response frame is assembled.
// The caller must keep the exact chunk span alive and immutable until assembly
// finishes. It is neither wire authority nor durable authority: the generated
// frame carries the ordinary released generation-9 representation and is
// independently validated before publication.
struct SyncReplicaReconciliationBorrowedDeltaManifest final {
    SyncReplicaContentDefinedChunkingParameters parameters;
    std::uint64_t total_size_bytes = 0U;
    std::span<const SyncReplicaReconciliationCumulativeDeltaChunk> chunks;
};

[[nodiscard]] SyncReplicaContentDefinedChunkingParameters
sync_replica_reconciliation_content_defined_parameters_or_throw(
    std::uint64_t total_size_bytes);

[[nodiscard]] std::string
sync_replica_reconciliation_delta_manifest_digest_or_throw(
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    const SyncReplicaReconciliationDeltaManifest& manifest);

struct SyncReplicaReconciliationPayload final {
    std::string content_sha256;
    std::uint64_t total_size_bytes = 0U;
    std::uint64_t offset_bytes = 0U;
    std::string chunk_sha256;
    std::string bytes;
    // Every ranged payload carries the exact complete-manifest witness. The
    // complete manifest itself is present only when the receiver did not prove
    // an exact process-local cache in its request.
    std::optional<std::string> delta_manifest_digest;
    std::optional<SyncReplicaReconciliationDeltaManifest> delta_manifest;
    std::uint64_t delta_chunk_offset_bytes = 0U;
    std::uint64_t delta_chunk_size_bytes = 0U;

    SyncReplicaReconciliationPayload() = default;
    SyncReplicaReconciliationPayload(
        std::string content_digest,
        std::string whole_payload);
    SyncReplicaReconciliationPayload(
        std::string content_digest,
        std::uint64_t total_size,
        std::uint64_t offset,
        std::string chunk_digest,
        std::string range_bytes,
        SyncReplicaReconciliationDeltaManifest manifest,
        std::uint64_t containing_chunk_offset,
        std::uint64_t containing_chunk_size);
    SyncReplicaReconciliationPayload(
        std::string content_digest,
        std::uint64_t total_size,
        std::uint64_t offset,
        std::string chunk_digest,
        std::string range_bytes,
        std::string manifest_digest,
        std::uint64_t containing_chunk_offset,
        std::uint64_t containing_chunk_size);

    bool operator==(const SyncReplicaReconciliationPayload&) const = default;
};

enum class SyncReplicaReconciliationResponseDisposition : std::uint8_t {
    Page = 1U,
    SourceChanged = 2U,
    PayloadUnavailable = 3U,
    SourcePayloadPreparing = 4U,
};

// A response is a complete transferable prefix of one source evidence page.
// PayloadUnavailable and SourcePayloadPreparing never advance past the exact
// blocked operation. Preparing means the exact payload exists, but the source
// has intentionally yielded while building its bounded content-defined
// manifest; a later request may resume that process-local projection. The
// lexical operation order is solely a stable paging representation; causal
// applicability remains owned by SyncReplicaModel admission.
struct SyncReplicaReconciliationResponse final {
    std::string folder_id;
    SyncReplicaActor requester_actor;
    SyncReplicaActor responder_actor;
    SyncReplicaDeliveryChannelBinding channel_binding;
    std::string request_digest;
    SyncReplicaReconciliationResponseDisposition disposition =
        SyncReplicaReconciliationResponseDisposition::Page;
    std::uint64_t source_state_generation = 0U;
    std::uint64_t source_evidence_count = 0U;
    std::string source_evidence_set_digest;
    std::vector<SyncReplicaOperation> operations;
    std::vector<SyncReplicaReconciliationPayload> payloads;
    // Strictly sorted operation IDs naming File operations intentionally
    // transferred as causal metadata without payload bytes under the exact
    // requester policy. This is explicit wire authority, not an inference from
    // an absent payload.
    std::vector<std::string> metadata_only_file_operation_ids;
    bool has_more = false;
    std::optional<std::string> next_after_operation_id;
    std::optional<std::string> blocked_operation_id;
    std::optional<SyncReplicaReconciliationPayloadContinuation>
        payload_continuation;

    bool operator==(const SyncReplicaReconciliationResponse&) const = default;
};

void validate_sync_replica_reconciliation_request_or_throw(
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

void validate_sync_replica_reconciliation_response_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

// Non-owning decode used by the shipping receiver. The response metadata and
// operations are owned, but payload byte strings remain empty and the exact
// byte fields are represented by payload_bytes views into the caller-owned
// frame. The frame must outlive this object. This keeps one bounded TLS frame
// from becoming a second page-sized aggregate allocation before sequential
// durable staging.
struct SyncReplicaReconciliationBorrowedResponse final {
    SyncReplicaReconciliationResponse response;
    std::vector<std::string_view> payload_bytes;
};

// One-pass product encoder result. The final frame is reserved to its exact
// canonical size and populated directly; no complete temporary response body
// is retained. The semantic response digest is derived from the canonical body
// already resident inside frame rather than serializing the page a second time.
struct SyncReplicaReconciliationEncodedResponse final {
    std::string frame;
    std::string response_digest;
    std::uint64_t canonical_body_bytes = 0U;
    std::uint64_t payload_bytes = 0U;

    bool operator==(
        const SyncReplicaReconciliationEncodedResponse&) const = default;
};

// Shipping source-side assembly result. response carries complete canonical
// metadata and per-range digests, but each payload.bytes string remains empty;
// the exact payload bytes live only in frame. This distinguishes the bounded
// direct-source path from the compatibility response object that owns another
// complete page of payload strings.
struct SyncReplicaReconciliationDirectFrameResponse final {
    SyncReplicaReconciliationResponse response;
    std::string frame;
    std::uint64_t canonical_body_bytes = 0U;
    std::uint64_t payload_bytes = 0U;
    // Complete manifests may be published directly from one exact borrowed
    // compact sequence. In that case response intentionally omits the owning
    // manifest vector; frame is the complete canonical authority.
    std::uint64_t borrowed_delta_manifest_count = 0U;
    std::uint64_t borrowed_delta_manifest_chunks = 0U;
};

// Move-only one-frame source assembly. Construction reserves and fixes one
// exact canonical generation-9 frame, including one writable hole for every
// declared payload range. Callers fill those holes directly from exact source
// descriptors, commit each range digest, and finish with ordinary complete
// response/request validation plus the structural frame digest. No executable
// callback, scatter/gather lifetime, or payload-sized auxiliary owner crosses
// this protocol boundary.
class SyncReplicaReconciliationResponseFrameAssembly final {
public:
    SyncReplicaReconciliationResponseFrameAssembly() noexcept = default;
    SyncReplicaReconciliationResponseFrameAssembly(
        const SyncReplicaReconciliationResponseFrameAssembly&) = delete;
    SyncReplicaReconciliationResponseFrameAssembly& operator=(
        const SyncReplicaReconciliationResponseFrameAssembly&) = delete;
    SyncReplicaReconciliationResponseFrameAssembly(
        SyncReplicaReconciliationResponseFrameAssembly&&) noexcept;
    SyncReplicaReconciliationResponseFrameAssembly& operator=(
        SyncReplicaReconciliationResponseFrameAssembly&&) noexcept;
    ~SyncReplicaReconciliationResponseFrameAssembly() noexcept;

    [[nodiscard]] bool active() const noexcept;
    [[nodiscard]] std::size_t payload_count() const noexcept;
    [[nodiscard]] std::span<char> payload_bytes_or_throw(
        std::size_t payload_index);
    void commit_payload_or_throw(
        std::size_t payload_index,
        std::string chunk_sha256);
    [[nodiscard]] SyncReplicaReconciliationDirectFrameResponse
    finish_or_throw();

private:
    struct State;
    explicit SyncReplicaReconciliationResponseFrameAssembly(
        std::unique_ptr<State> state) noexcept;
    [[nodiscard]] State& require_state_or_throw(std::string_view operation);

    std::unique_ptr<State> state_;

    friend SyncReplicaReconciliationResponseFrameAssembly
    begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
        SyncReplicaReconciliationResponse,
        const SyncReplicaReconciliationRequest&,
        std::vector<std::uint64_t>,
        std::vector<std::optional<
            SyncReplicaReconciliationBorrowedDeltaManifest>>,
        const SyncReplicaReconciliationProtocolLimits&);
};

[[nodiscard]] SyncReplicaReconciliationResponseFrameAssembly
begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
    SyncReplicaReconciliationResponse response_metadata,
    const SyncReplicaReconciliationRequest& request,
    std::vector<std::uint64_t> payload_byte_counts,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

// Direct borrowed-manifest assembly. borrowed_delta_manifests may be empty
// (allocation-cold compatibility path) or must have the same cardinality as
// response_metadata.payloads; each present entry replaces an absent owning
// payload.delta_manifest for canonical validation and framing. The spans remain
// caller-owned and must outlive finish_or_throw().
[[nodiscard]] SyncReplicaReconciliationResponseFrameAssembly
begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
    SyncReplicaReconciliationResponse response_metadata,
    const SyncReplicaReconciliationRequest& request,
    std::vector<std::uint64_t> payload_byte_counts,
    std::vector<std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest>>
        borrowed_delta_manifests,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] std::string
encode_sync_replica_reconciliation_request_or_throw(
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaReconciliationRequest
    decode_sync_replica_reconciliation_request_or_throw(
        std::string_view frame,
        const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] std::string
sync_replica_reconciliation_request_digest_or_throw(
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaReconciliationEncodedResponse
encode_sync_replica_reconciliation_response_with_digest_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] std::string
encode_sync_replica_reconciliation_response_for_request_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaReconciliationEncodedResponse
encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] std::string
encode_sync_replica_reconciliation_response_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaReconciliationBorrowedResponse
decode_sync_replica_reconciliation_response_borrowing_payloads_or_throw(
    std::string_view frame,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaReconciliationBorrowedResponse
decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw(
    std::string_view frame,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaReconciliationResponse
    decode_sync_replica_reconciliation_response_or_throw(
        std::string_view frame,
        const SyncReplicaReconciliationProtocolLimits& limits = {});

[[nodiscard]] std::string
sync_replica_reconciliation_response_digest_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

// Exact cross-message validation. The authenticated channel authority remains
// outside this pure protocol; this function only proves the response belongs to
// the precise request, actors, folder, cursor, and channel bytes supplied.
void validate_sync_replica_reconciliation_response_for_request_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

void validate_sync_replica_reconciliation_borrowed_response_for_request_or_throw(
    const SyncReplicaReconciliationBorrowedResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits = {});

}  // namespace anonsync
