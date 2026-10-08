#include "sync_replica_reconciliation_protocol.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kRequestMagic =
    "ANONSYNC-REPLICA-RECONCILIATION-REQUEST";
constexpr std::string_view kResponseMagic =
    "ANONSYNC-REPLICA-RECONCILIATION-RESPONSE";
constexpr std::string_view kRequestStructuralDigestDomain =
    "anonsync-sync-replica-reconciliation-request-frame-v9";
constexpr std::string_view kResponseStructuralDigestDomain =
    "anonsync-sync-replica-reconciliation-response-frame-v9";
constexpr std::string_view kRequestDigestDomain =
    "anonsync-sync-replica-reconciliation-request-v9";
constexpr std::string_view kResponseDigestDomain =
    "anonsync-sync-replica-reconciliation-response-v9";
constexpr std::string_view kDeltaManifestDigestDomain =
    "anonsync-sync-replica-reconciliation-content-defined-manifest-v1";
constexpr std::uint64_t kDigestTextBytes = 64U;
constexpr std::uint64_t kFixedFrameTrailerBytes = kDigestTextBytes;

[[nodiscard]] std::string u32_be(std::uint32_t value) {
    std::string out(4U, '\0');
    for (std::size_t index = 0; index < 4U; ++index) {
        out[3U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

[[nodiscard]] std::string u64_be(std::uint64_t value) {
    std::string out(8U, '\0');
    for (std::size_t index = 0; index < 8U; ++index) {
        out[7U - index] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    return out;
}

[[nodiscard]] std::uint64_t size_to_u64_or_throw(
    std::size_t value,
    const std::string& label) {
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (value > static_cast<std::size_t>(
                        std::numeric_limits<std::uint64_t>::max())) {
            throw std::overflow_error(label + " exceeds uint64_t");
        }
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::size_t u64_to_size_or_throw(
    std::uint64_t value,
    const std::string& label) {
    if (value > static_cast<std::uint64_t>(
                    std::numeric_limits<std::size_t>::max())) {
        throw std::overflow_error(label + " exceeds addressable size");
    }
    return static_cast<std::size_t>(value);
}

[[nodiscard]] std::uint64_t checked_add_u64_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::overflow_error(label + " exceeds uint64_t");
    }
    return left + right;
}

[[nodiscard]] std::uint64_t checked_multiply_u64_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (left != 0U &&
        right > std::numeric_limits<std::uint64_t>::max() / left) {
        throw std::overflow_error(label + " exceeds uint64_t");
    }
    return left * right;
}

void append_u32(std::string& out, std::uint32_t value) {
    out.append(u32_be(value));
}

void append_u64(std::string& out, std::uint64_t value) {
    out.append(u64_be(value));
}

void append_framed(std::string& out, std::string_view bytes) {
    append_u64(
        out,
        size_to_u64_or_throw(
            bytes.size(), "sync replica reconciliation field length"));
    out.append(bytes);
}

void append_framed(
    std::string& out,
    const Sha256DigestValue& digest) {
    append_u64(out, kDigestTextBytes);
    digest.append_lowercase_hex_to(out);
}

void append_optional_digest_field(
    std::string& out,
    const std::optional<std::string>& value) {
    append_u32(out, value.has_value() ? 1U : 0U);
    if (value.has_value()) append_framed(out, *value);
}

void append_digest_framed(
    Sha256DigestBuilder& digest,
    std::string_view bytes) {
    digest.update(u64_be(size_to_u64_or_throw(
        bytes.size(), "sync replica reconciliation digest field length")));
    digest.update(bytes);
}

void append_digest_framed(
    Sha256DigestBuilder& destination,
    const Sha256DigestValue& digest) {
    destination.update(u64_be(kDigestTextBytes));
    digest.update_lowercase_hex(destination);
}

[[nodiscard]] std::uint64_t fixed_frame_bytes(std::string_view magic) {
    std::uint64_t bytes = size_to_u64_or_throw(
        magic.size(), "sync replica reconciliation magic length");
    return checked_add_u64_or_throw(
        bytes, 4U + 8U + kFixedFrameTrailerBytes,
        "sync replica reconciliation fixed frame length");
}

[[nodiscard]] std::uint64_t framed_capacity_or_throw(
    std::uint64_t maximum_bytes,
    const std::string& label) {
    return checked_add_u64_or_throw(8U, maximum_bytes, label);
}

[[nodiscard]] std::uint64_t maximum_request_frame_bytes_or_throw() {
    std::uint64_t bytes = fixed_frame_bytes(kRequestMagic);
    auto add = [&](std::uint64_t value, std::string_view field) {
        bytes = checked_add_u64_or_throw(
            bytes, value,
            "sync replica reconciliation maximum request " +
                std::string(field));
    };
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request folder frame"),
        "folder");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request requester frame"),
        "requester");
    add(8U, "requester epoch");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request responder frame"),
        "responder");
    add(8U, "responder epoch");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "request binding type frame"),
        "binding type");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "request binding digest frame"),
        "binding digest");
    add(4U, "cursor presence");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes, "request cursor frame"),
        "cursor");
    add(4U, "source digest presence");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "request source digest frame"),
        "source digest");
    add(4U, "payload continuation presence");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "request payload operation frame"),
        "payload operation");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "request payload content frame"),
        "payload content");
    add(8U, "payload total size");
    add(8U, "payload next offset");
    add(4U + framed_capacity_or_throw(
                 kSyncManifestSha256TextBytes,
                 "request cached delta manifest digest frame"),
        "cached delta manifest digest");
    add(8U, "selective-sync generation");
    add(4U, "selective-sync default mode");
    add(8U, "selective-sync rule count");
    add(8U, "selective-sync rule-path bytes");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "request selective-sync digest frame"),
        "selective-sync digest");
    add(kSyncReplicaSelectiveSyncMaximumRulePathBytes,
        "selective-sync rule paths");
    add(checked_multiply_u64_or_throw(
            kSyncReplicaSelectiveSyncMaximumRules, 12U,
            "request selective-sync rule framing"),
        "selective-sync rule framing");
    return bytes;
}

[[nodiscard]] std::uint64_t maximum_response_frame_bytes_or_throw(
    const SyncReplicaReconciliationProtocolLimits& limits) {
    std::uint64_t bytes = fixed_frame_bytes(kResponseMagic);
    auto add = [&](std::uint64_t value, std::string_view field) {
        bytes = checked_add_u64_or_throw(
            bytes, value,
            "sync replica reconciliation maximum response " +
                std::string(field));
    };
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "response folder frame"),
        "folder");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "response requester frame"),
        "requester");
    add(8U, "requester epoch");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "response responder frame"),
        "responder");
    add(8U, "responder epoch");
    add(framed_capacity_or_throw(
            kSyncManifestIdMaxBytes, "response binding type frame"),
        "binding type");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "response binding digest frame"),
        "binding digest");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "response request digest frame"),
        "request digest");
    add(4U, "disposition");
    add(8U, "source generation");
    add(8U, "source evidence count");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "response source digest frame"),
        "source digest");
    add(8U, "operation count");
    add(limits.max_canonical_operation_bytes_per_page,
        "canonical operation bytes");
    add(checked_multiply_u64_or_throw(
            limits.max_operations_per_page, 8U,
            "response operation framing overhead"),
        "operation framing overhead");
    add(8U, "payload count");
    add(limits.max_payload_bytes_per_page, "payload bytes");
    add(checked_multiply_u64_or_throw(
            limits.max_payloads_per_page,
            (8U + kSyncManifestSha256TextBytes) + 8U + 8U +
                (8U + kSyncManifestSha256TextBytes) + 8U +
                4U + (8U + kSyncManifestSha256TextBytes) + 4U +
                8U + 8U,
            "response payload framing overhead"),
        "payload framing overhead");
    // Validation permits at most one ranged payload identity, represented by
    // several contiguous range records, and whole payloads carry no manifest.
    // Charge one complete bounded content-defined manifest rather than
    // multiplying its cost by the range-record count. Four parameter fields plus
    // count consume 40 bytes; each chunk consumes size plus one framed SHA-256
    // digest (80 bytes).
    add(40U, "content-defined manifest header");
    add(checked_multiply_u64_or_throw(
            kSyncReplicaReconciliationMaximumContentDefinedChunks,
            8U + 8U + kSyncManifestSha256TextBytes,
            "response content-defined manifest framing"),
        "content-defined manifest framing");
    add(4U, "has-more flag");
    add(4U + framed_capacity_or_throw(
                 kSyncManifestSha256TextBytes,
                 "response next cursor frame"),
        "next cursor");
    add(4U + framed_capacity_or_throw(
                 kSyncManifestSha256TextBytes,
                 "response blocked operation frame"),
        "blocked operation");
    add(4U, "payload continuation presence");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "response payload operation frame"),
        "payload operation");
    add(framed_capacity_or_throw(
            kSyncManifestSha256TextBytes,
            "response payload content frame"),
        "payload content");
    add(8U, "payload total size");
    add(8U, "payload next offset");
    add(8U, "metadata-only operation count");
    add(checked_multiply_u64_or_throw(
            limits.max_operations_per_page,
            8U + kSyncManifestSha256TextBytes,
            "response metadata-only operation framing"),
        "metadata-only operation framing");
    return bytes;
}

void validate_actor_or_throw(
    const SyncReplicaActor& actor,
    const std::string& label) {
    if (!sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument(label + " actor identity is invalid");
    }
}

void validate_payload_continuation_or_throw(
    const SyncReplicaReconciliationPayloadContinuation& continuation,
    const SyncReplicaReconciliationProtocolLimits& limits,
    const std::string& label) {
    if (!is_lowercase_sha256_hex(continuation.operation_id) ||
        !is_lowercase_sha256_hex(continuation.content_sha256)) {
        throw std::invalid_argument(label + " digest identity is invalid");
    }
    if (continuation.total_size_bytes == 0U ||
        continuation.total_size_bytes >
            limits.max_payload_extent_bytes ||
        continuation.next_offset_bytes == 0U ||
        continuation.next_offset_bytes > continuation.total_size_bytes) {
        throw std::invalid_argument(label + " byte extent is invalid");
    }
}

struct DeltaManifestView final {
    const SyncReplicaContentDefinedChunkingParameters* parameters = nullptr;
    std::uint64_t total_size_bytes = 0U;
    const SyncReplicaReconciliationDeltaManifest* owned = nullptr;
    std::span<const SyncReplicaReconciliationCumulativeDeltaChunk> cumulative;

    [[nodiscard]] static DeltaManifestView from_owned(
        std::uint64_t total_size,
        const SyncReplicaReconciliationDeltaManifest& manifest) noexcept {
        return {&manifest.parameters, total_size, &manifest, {}};
    }

    [[nodiscard]] static DeltaManifestView from_borrowed(
        const SyncReplicaReconciliationBorrowedDeltaManifest& manifest)
        noexcept {
        return {
            &manifest.parameters, manifest.total_size_bytes, nullptr,
            manifest.chunks};
    }

    [[nodiscard]] bool present() const noexcept {
        return parameters != nullptr;
    }

    [[nodiscard]] bool is_borrowed() const noexcept {
        return present() && owned == nullptr;
    }

    [[nodiscard]] std::size_t chunk_count() const noexcept {
        return owned != nullptr ? owned->chunks.size() : cumulative.size();
    }

    [[nodiscard]] std::uint64_t chunk_size_bytes(
        std::size_t index) const noexcept {
        if (owned != nullptr) return owned->chunks[index].size_bytes;
        const std::uint64_t preceding =
            index == 0U ? 0U : cumulative[index - 1U].end_offset_bytes;
        return cumulative[index].end_offset_bytes - preceding;
    }

    [[nodiscard]] const Sha256DigestValue& chunk_sha256(
        std::size_t index) const noexcept {
        return owned != nullptr ? owned->chunks[index].sha256
                                : cumulative[index].sha256;
    }
};

[[nodiscard]] const std::optional<
    SyncReplicaReconciliationBorrowedDeltaManifest>&
borrowed_delta_manifest_at_or_none_or_throw(
    const std::vector<std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest>>& manifests,
    std::size_t index,
    std::string_view label) {
    static const std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest> none;
    if (manifests.empty()) return none;
    if (index >= manifests.size()) {
        throw std::logic_error(
            std::string(label) + " borrowed manifest index is out of range");
    }
    return manifests[index];
}

[[nodiscard]] DeltaManifestView delta_manifest_view_or_none_or_throw(
    const SyncReplicaReconciliationPayload& payload,
    const std::optional<SyncReplicaReconciliationBorrowedDeltaManifest>&
        borrowed,
    std::string_view label) {
    if (payload.delta_manifest.has_value() && borrowed.has_value()) {
        throw std::invalid_argument(
            std::string(label) +
            " carries both owning and borrowed complete manifests");
    }
    if (payload.delta_manifest.has_value()) {
        return DeltaManifestView::from_owned(
            payload.total_size_bytes, *payload.delta_manifest);
    }
    if (borrowed.has_value()) {
        if (borrowed->total_size_bytes != payload.total_size_bytes) {
            throw std::invalid_argument(
                std::string(label) +
                " borrowed complete manifest changed payload extent");
        }
        return DeltaManifestView::from_borrowed(*borrowed);
    }
    return {};
}

void validate_delta_manifest_view_or_throw(
    std::uint64_t total_size_bytes,
    const DeltaManifestView& manifest,
    const std::string& label) {
    if (total_size_bytes == 0U) {
        throw std::invalid_argument(label + " payload is empty");
    }
    if (!manifest.present() || manifest.total_size_bytes != total_size_bytes) {
        throw std::invalid_argument(
            label + " does not bind the exact payload extent");
    }
    const SyncReplicaContentDefinedChunkingParameters canonical =
        sync_replica_reconciliation_content_defined_parameters_or_throw(
            total_size_bytes);
    validate_sync_replica_content_defined_chunking_parameters_or_throw(
        *manifest.parameters, label + " parameters");
    if (*manifest.parameters != canonical) {
        throw std::invalid_argument(
            label + " uses noncanonical content-defined parameters");
    }
    if (manifest.chunk_count() == 0U ||
        manifest.chunk_count() >
            kSyncReplicaReconciliationMaximumContentDefinedChunks) {
        throw std::invalid_argument(
            label + " chunk count is outside its bounded frontier");
    }
    std::uint64_t covered = 0U;
    for (std::size_t index = 0U; index < manifest.chunk_count(); ++index) {
        const std::uint64_t chunk_size = manifest.chunk_size_bytes(index);
        if (chunk_size == 0U ||
            chunk_size > manifest.parameters->maximum_chunk_bytes ||
            (index + 1U != manifest.chunk_count() &&
             chunk_size < manifest.parameters->minimum_chunk_bytes)) {
            throw std::invalid_argument(
                label + " contains an invalid chunk record");
        }
        if (chunk_size > total_size_bytes - covered) {
            throw std::invalid_argument(
                label + " chunk extents exceed the payload");
        }
        covered += chunk_size;
    }
    if (covered != total_size_bytes) {
        throw std::invalid_argument(
            label + " chunk extents do not cover the payload");
    }
}

[[nodiscard]] std::string delta_manifest_digest_for_view_or_throw(
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    const DeltaManifestView& manifest) {
    if (!is_lowercase_sha256_hex(content_sha256)) {
        throw std::invalid_argument(
            "sync replica reconciliation content-defined manifest content digest is invalid");
    }
    validate_delta_manifest_view_or_throw(
        total_size_bytes, manifest,
        "sync replica reconciliation content-defined manifest");

    Sha256DigestBuilder digest;
    digest.update(kDeltaManifestDigestDomain);
    append_digest_framed(digest, content_sha256);
    digest.update(u64_be(total_size_bytes));
    digest.update(u64_be(manifest.parameters->minimum_chunk_bytes));
    digest.update(u64_be(manifest.parameters->average_chunk_bytes));
    digest.update(u64_be(manifest.parameters->maximum_chunk_bytes));
    digest.update(u64_be(manifest.parameters->maximum_chunk_count));
    digest.update(u64_be(size_to_u64_or_throw(
        manifest.chunk_count(),
        "sync replica reconciliation content-defined manifest count")));
    for (std::size_t index = 0U; index < manifest.chunk_count(); ++index) {
        digest.update(u64_be(manifest.chunk_size_bytes(index)));
        append_digest_framed(digest, manifest.chunk_sha256(index));
    }
    return digest.finish_hex();
}

void validate_payload_range_against_delta_manifest_or_throw(
    const SyncReplicaReconciliationPayload& payload,
    std::string_view payload_bytes,
    const DeltaManifestView& manifest,
    const std::string& label) {
    const std::uint64_t bytes = size_to_u64_or_throw(
        payload_bytes.size(), label + " byte count");
    std::uint64_t chunk_offset = 0U;
    std::optional<std::size_t> containing;
    for (std::size_t index = 0U; index < manifest.chunk_count(); ++index) {
        const std::uint64_t chunk_size = manifest.chunk_size_bytes(index);
        if (payload.offset_bytes < chunk_offset + chunk_size) {
            containing = index;
            break;
        }
        chunk_offset += chunk_size;
    }
    if (!containing.has_value() ||
        payload.delta_chunk_offset_bytes != chunk_offset ||
        payload.delta_chunk_size_bytes !=
            manifest.chunk_size_bytes(*containing)) {
        throw std::invalid_argument(
            label + " does not name its manifest chunk");
    }
    if (payload.offset_bytes == chunk_offset &&
        bytes == manifest.chunk_size_bytes(*containing) &&
        !manifest.chunk_sha256(*containing).equals_lowercase_hex(
            payload.chunk_sha256)) {
        throw std::invalid_argument(
            label + " full chunk digest disagrees with its content-defined manifest");
    }
}

[[nodiscard]] bool response_disposition_is_known(
    SyncReplicaReconciliationResponseDisposition disposition) noexcept {
    switch (disposition) {
        case SyncReplicaReconciliationResponseDisposition::Page:
        case SyncReplicaReconciliationResponseDisposition::SourceChanged:
        case SyncReplicaReconciliationResponseDisposition::PayloadUnavailable:
        case SyncReplicaReconciliationResponseDisposition::
            SourcePayloadPreparing:
            return true;
    }
    return false;
}

void validate_protocol_limits_impl_or_throw(
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_model_limits_or_throw(limits.model);
    if (limits.max_operations_per_page == 0U ||
        limits.max_canonical_operation_bytes_per_page == 0U ||
        limits.max_payloads_per_page == 0U ||
        limits.max_single_payload_bytes == 0U ||
        limits.max_payload_bytes_per_page == 0U ||
        limits.max_payload_extent_bytes == 0U) {
        throw std::invalid_argument(
            "sync replica reconciliation page limits must be positive");
    }
    if (limits.max_operations_per_page >
            kSyncReplicaReconciliationMaximumOperationsPerPage ||
        limits.max_canonical_operation_bytes_per_page >
            kSyncReplicaReconciliationMaximumCanonicalOperationBytesPerPage ||
        limits.max_payloads_per_page >
            kSyncReplicaReconciliationMaximumPayloadsPerPage ||
        limits.max_single_payload_bytes >
            kSyncReplicaReconciliationMaximumSinglePayloadBytes ||
        limits.max_payload_bytes_per_page >
            kSyncReplicaReconciliationMaximumPayloadBytesPerPage ||
        limits.max_request_frame_bytes >
            kSyncReplicaReconciliationMaximumRequestFrameBytes ||
        limits.max_response_frame_bytes >
            kSyncReplicaReconciliationMaximumResponseFrameBytes) {
        throw std::invalid_argument(
            "sync replica reconciliation page limits exceed the fixed product memory and descriptor frontier");
    }
    if (limits.max_canonical_operation_bytes_per_page <
        limits.model.max_canonical_operation_bytes) {
        throw std::invalid_argument(
            "sync replica reconciliation canonical page budget cannot hold one maximum wire operation");
    }
    if (limits.max_payload_bytes_per_page <
        limits.max_single_payload_bytes) {
        throw std::invalid_argument(
            "sync replica reconciliation payload page budget cannot hold one maximum payload range");
    }
    if (limits.max_payload_extent_bytes <
        limits.max_single_payload_bytes) {
        throw std::invalid_argument(
            "sync replica reconciliation complete payload extent cannot hold one maximum range");
    }
    if (limits.max_payload_extent_bytes >
        kSyncReplicaMaximumPayloadExtentBytes) {
        throw std::invalid_argument(
            "sync replica reconciliation complete payload extent exceeds the bounded content-defined manifest frontier");
    }
    (void)u64_to_size_or_throw(
        limits.max_operations_per_page,
        "sync replica reconciliation operation count limit");
    (void)u64_to_size_or_throw(
        limits.max_payloads_per_page,
        "sync replica reconciliation payload count limit");
    (void)u64_to_size_or_throw(
        limits.max_single_payload_bytes,
        "sync replica reconciliation single payload limit");
    // Complete extent is serialized and compared as uint64_t; it is never one
    // allocation. Only the independently bounded range and frame ceilings
    // need to fit size_t.
    (void)u64_to_size_or_throw(
        limits.max_request_frame_bytes,
        "sync replica reconciliation request frame limit");
    (void)u64_to_size_or_throw(
        limits.max_response_frame_bytes,
        "sync replica reconciliation response frame limit");
    if (limits.max_request_frame_bytes <
        maximum_request_frame_bytes_or_throw()) {
        throw std::invalid_argument(
            "sync replica reconciliation request frame limit cannot hold every canonical request");
    }
    if (limits.max_response_frame_bytes <
        maximum_response_frame_bytes_or_throw(limits)) {
        throw std::invalid_argument(
            "sync replica reconciliation response frame limit cannot hold every configured page");
    }
}

class FrameReader final {
public:
    FrameReader(std::string_view bytes, std::string label)
        : remaining_(bytes), label_(std::move(label)) {}

    [[nodiscard]] std::uint32_t read_u32() {
        require_bytes(4U, "uint32");
        std::uint32_t value = 0U;
        for (std::size_t index = 0; index < 4U; ++index) {
            value = static_cast<std::uint32_t>(
                (value << 8U) |
                static_cast<unsigned char>(remaining_[index]));
        }
        remaining_.remove_prefix(4U);
        return value;
    }

    [[nodiscard]] std::uint64_t read_u64() {
        require_bytes(8U, "uint64");
        std::uint64_t value = 0U;
        for (std::size_t index = 0; index < 8U; ++index) {
            value = (value << 8U) |
                    static_cast<unsigned char>(remaining_[index]);
        }
        remaining_.remove_prefix(8U);
        return value;
    }

    [[nodiscard]] std::string_view read_view(
        std::uint64_t maximum_bytes,
        std::string_view field) {
        const std::uint64_t length = read_u64();
        if (length > maximum_bytes) {
            throw std::runtime_error(
                label_ + " " + std::string(field) +
                " exceeds its configured byte limit");
        }
        const std::size_t size = u64_to_size_or_throw(
            length, label_ + " " + std::string(field) + " length");
        require_bytes(size, field);
        const std::string_view value = remaining_.substr(0U, size);
        remaining_.remove_prefix(size);
        return value;
    }

    [[nodiscard]] std::string read_string(
        std::uint64_t maximum_bytes,
        std::string_view field) {
        return std::string(read_view(maximum_bytes, field));
    }

    [[nodiscard]] std::optional<std::string> read_optional_digest(
        std::string_view field) {
        const std::uint32_t present = read_u32();
        if (present > 1U) {
            throw std::runtime_error(
                label_ + " " + std::string(field) +
                " presence flag is invalid");
        }
        if (present == 0U) return std::nullopt;
        return read_string(kSyncManifestSha256TextBytes, field);
    }

    void require_consumed() const {
        if (!remaining_.empty()) {
            throw std::runtime_error(label_ + " contains trailing bytes");
        }
    }

private:
    void require_bytes(std::size_t count, std::string_view field) const {
        if (remaining_.size() < count) {
            throw std::runtime_error(
                label_ + " is truncated at " + std::string(field));
        }
    }

    std::string_view remaining_;
    std::string label_;
};

[[nodiscard]] std::string sha256_view_or_throw(std::string_view bytes) {
    Sha256DigestBuilder digest;
    digest.update(bytes);
    return digest.finish_hex();
}

[[nodiscard]] std::string body_digest_or_throw(
    std::string_view domain,
    std::string_view body) {
    Sha256DigestBuilder digest;
    digest.update(domain);
    append_digest_framed(digest, body);
    return digest.finish_hex();
}

[[nodiscard]] std::string make_frame_or_throw(
    std::string_view magic,
    std::string_view structural_digest_domain,
    std::string body,
    std::uint64_t maximum_frame_bytes,
    const std::string& label) {
    std::string frame;
    frame.reserve(
        magic.size() + 12U + body.size() +
        static_cast<std::size_t>(kFixedFrameTrailerBytes));
    frame.append(magic);
    append_u32(frame, kSyncReplicaReconciliationProtocolVersion);
    append_u64(
        frame,
        size_to_u64_or_throw(body.size(), label + " body length"));
    frame.append(body);
    frame.append(body_digest_or_throw(structural_digest_domain, body));
    if (size_to_u64_or_throw(frame.size(), label + " frame length") >
        maximum_frame_bytes) {
        throw std::invalid_argument(label + " exceeds its frame limit");
    }
    return frame;
}

[[nodiscard]] std::string_view extract_body_or_throw(
    std::string_view frame,
    std::string_view magic,
    std::string_view structural_digest_domain,
    std::uint64_t maximum_frame_bytes,
    const std::string& label) {
    if (size_to_u64_or_throw(frame.size(), label + " frame length") >
        maximum_frame_bytes) {
        throw std::runtime_error(label + " exceeds its frame limit");
    }
    const std::size_t fixed = u64_to_size_or_throw(
        fixed_frame_bytes(magic), label + " fixed frame length");
    if (frame.size() < fixed) {
        throw std::runtime_error(label + " is shorter than its fixed frame");
    }
    if (!frame.starts_with(magic)) {
        throw std::runtime_error(label + " magic is invalid");
    }

    FrameReader header(
        frame.substr(magic.size(), 12U), label + " header");
    const std::uint32_t version = header.read_u32();
    if (version != kSyncReplicaReconciliationProtocolVersion) {
        throw std::runtime_error(label + " protocol version is unsupported");
    }
    const std::uint64_t body_length = header.read_u64();
    header.require_consumed();
    const std::size_t body_size = u64_to_size_or_throw(
        body_length, label + " body length");
    if (body_size != frame.size() - fixed) {
        throw std::runtime_error(label + " body length is not exact");
    }

    const std::size_t body_begin = magic.size() + 12U;
    const std::string_view body = frame.substr(body_begin, body_size);
    const std::string_view observed_digest =
        frame.substr(body_begin + body_size, kDigestTextBytes);
    if (!is_lowercase_sha256_hex(observed_digest)) {
        throw std::runtime_error(label + " structural digest is invalid");
    }
    const std::string expected_digest =
        body_digest_or_throw(structural_digest_domain, body);
    if (observed_digest != expected_digest) {
        throw std::runtime_error(label + " structural digest mismatch");
    }
    return body;
}

[[nodiscard]] std::string request_body_or_throw(
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_request_or_throw(request, limits);
    std::string body;
    append_framed(body, request.folder_id);
    append_framed(body, request.requester_actor.device_id);
    append_u64(body, request.requester_actor.epoch);
    append_framed(body, request.responder_actor.device_id);
    append_u64(body, request.responder_actor.epoch);
    append_framed(body, request.channel_binding.type);
    append_framed(body, request.channel_binding.digest);
    append_optional_digest_field(body, request.after_operation_id);
    append_optional_digest_field(
        body, request.expected_source_evidence_set_digest);
    append_u32(body, request.payload_continuation.has_value() ? 1U : 0U);
    if (request.payload_continuation.has_value()) {
        append_framed(body, request.payload_continuation->operation_id);
        append_framed(body, request.payload_continuation->content_sha256);
        append_u64(body, request.payload_continuation->total_size_bytes);
        append_u64(body, request.payload_continuation->next_offset_bytes);
    }
    append_optional_digest_field(
        body, request.cached_delta_manifest_digest);
    append_u64(body, request.selective_sync_policy.generation);
    append_u32(
        body,
        static_cast<std::uint32_t>(
            request.selective_sync_policy.default_mode));
    append_u64(
        body,
        size_to_u64_or_throw(
            request.selective_sync_policy.rules.size(),
            "sync replica reconciliation request selective-sync rule count"));
    append_u64(body, request.selective_sync_policy.rule_path_bytes);
    append_framed(body, request.selective_sync_policy.policy_digest);
    for (const SyncReplicaSelectiveSyncRule& rule :
         request.selective_sync_policy.rules) {
        append_framed(body, rule.canonical_path);
        append_u32(body, static_cast<std::uint32_t>(rule.mode));
    }
    return body;
}

struct ResponseBodyMetrics final {
    std::uint64_t body_bytes = 0U;
    std::uint64_t payload_bytes = 0U;
};

[[nodiscard]] std::uint64_t exact_framed_bytes_or_throw(
    std::string_view value,
    const std::string& label) {
    return checked_add_u64_or_throw(
        8U, size_to_u64_or_throw(value.size(), label + " value"), label);
}

[[nodiscard]] std::uint64_t exact_optional_digest_bytes_or_throw(
    const std::optional<std::string>& value,
    const std::string& label) {
    if (!value.has_value()) return 4U;
    return checked_add_u64_or_throw(
        4U, exact_framed_bytes_or_throw(*value, label + " digest"), label);
}

template <typename PayloadByteCountAt, typename DeltaManifestAt>
[[nodiscard]] ResponseBodyMetrics response_body_metrics_impl_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits,
    PayloadByteCountAt&& payload_byte_count_at,
    DeltaManifestAt&& delta_manifest_at) {
    ResponseBodyMetrics metrics;
    auto add = [&](std::uint64_t value, std::string_view field) {
        metrics.body_bytes = checked_add_u64_or_throw(
            metrics.body_bytes, value,
            "sync replica reconciliation response body " +
                std::string(field));
    };
    auto add_framed = [&](std::string_view value, std::string_view field) {
        add(exact_framed_bytes_or_throw(
                value,
                "sync replica reconciliation response " +
                    std::string(field)),
            field);
    };
    auto add_optional = [&](const std::optional<std::string>& value,
                            std::string_view field) {
        add(exact_optional_digest_bytes_or_throw(
                value,
                "sync replica reconciliation response " +
                    std::string(field)),
            field);
    };

    add_framed(response.folder_id, "folder");
    add_framed(response.requester_actor.device_id, "requester");
    add(8U, "requester epoch");
    add_framed(response.responder_actor.device_id, "responder");
    add(8U, "responder epoch");
    add_framed(response.channel_binding.type, "channel binding type");
    add_framed(response.channel_binding.digest, "channel binding digest");
    add_framed(response.request_digest, "request digest");
    add(4U, "disposition");
    add(8U, "source state generation");
    add(8U, "source evidence count");
    add_framed(response.source_evidence_set_digest, "source evidence digest");
    add(8U, "operation count");
    for (const SyncReplicaOperation& operation : response.operations) {
        add(checked_add_u64_or_throw(
                8U,
                sync_replica_operation_canonical_size_or_throw(
                    operation, limits.model),
                "sync replica reconciliation response canonical operation frame"),
            "canonical operation");
    }
    add(8U, "payload count");
    for (std::size_t payload_index = 0U;
         payload_index < response.payloads.size(); ++payload_index) {
        const SyncReplicaReconciliationPayload& payload =
            response.payloads[payload_index];
        add_framed(payload.content_sha256, "payload content digest");
        add(8U, "payload total size");
        add(8U, "payload offset");
        add_framed(payload.chunk_sha256, "payload chunk digest");
        const std::uint64_t bytes = payload_byte_count_at(payload_index);
        metrics.payload_bytes = checked_add_u64_or_throw(
            metrics.payload_bytes, bytes,
            "sync replica reconciliation response payload byte total");
        add(checked_add_u64_or_throw(
                8U, bytes,
                "sync replica reconciliation response payload byte frame"),
            "payload bytes");
        add_optional(payload.delta_manifest_digest, "delta manifest digest");
        const DeltaManifestView complete_manifest =
            delta_manifest_at(payload_index);
        add(4U, "delta manifest presence");
        if (complete_manifest.present()) {
            add(40U, "delta manifest parameters and count");
            for (std::size_t chunk_index = 0U;
                 chunk_index < complete_manifest.chunk_count();
                 ++chunk_index) {
                add(8U, "delta manifest chunk size");
                add(8U + kDigestTextBytes,
                    "delta manifest fixed chunk digest");
            }
        }
        add(8U, "delta chunk offset");
        add(8U, "delta chunk size");
    }
    add(8U, "metadata-only operation count");
    for (const std::string& operation_id :
         response.metadata_only_file_operation_ids) {
        add_framed(operation_id, "metadata-only operation id");
    }
    add(4U, "has-more flag");
    add_optional(response.next_after_operation_id, "next cursor");
    add_optional(response.blocked_operation_id, "blocked operation");
    add(4U, "payload continuation presence");
    if (response.payload_continuation.has_value()) {
        add_framed(
            response.payload_continuation->operation_id,
            "payload continuation operation");
        add_framed(
            response.payload_continuation->content_sha256,
            "payload continuation content");
        add(8U, "payload continuation total size");
        add(8U, "payload continuation next offset");
    }
    return metrics;
}

[[nodiscard]] ResponseBodyMetrics response_body_metrics_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    return response_body_metrics_impl_or_throw(
        response, limits, [&](std::size_t payload_index) {
            return size_to_u64_or_throw(
                response.payloads[payload_index].bytes.size(),
                "sync replica reconciliation response payload bytes");
        }, [&](std::size_t payload_index) {
            const auto& payload = response.payloads[payload_index];
            return payload.delta_manifest.has_value()
                ? DeltaManifestView::from_owned(
                      payload.total_size_bytes, *payload.delta_manifest)
                : DeltaManifestView{};
        });
}

template <typename AppendPayloadFields, typename DeltaManifestAt>
void append_response_body_impl_or_throw(
    std::string& body,
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits,
    AppendPayloadFields&& append_payload_fields,
    DeltaManifestAt&& delta_manifest_at) {
    append_framed(body, response.folder_id);
    append_framed(body, response.requester_actor.device_id);
    append_u64(body, response.requester_actor.epoch);
    append_framed(body, response.responder_actor.device_id);
    append_u64(body, response.responder_actor.epoch);
    append_framed(body, response.channel_binding.type);
    append_framed(body, response.channel_binding.digest);
    append_framed(body, response.request_digest);
    append_u32(body, static_cast<std::uint32_t>(response.disposition));
    append_u64(body, response.source_state_generation);
    append_u64(body, response.source_evidence_count);
    append_framed(body, response.source_evidence_set_digest);
    append_u64(
        body,
        size_to_u64_or_throw(
            response.operations.size(),
            "sync replica reconciliation response operation count"));
    for (const SyncReplicaOperation& operation : response.operations) {
        append_framed(
            body,
            encode_sync_replica_operation_canonical_or_throw(
                operation, limits.model));
    }
    append_u64(
        body,
        size_to_u64_or_throw(
            response.payloads.size(),
            "sync replica reconciliation response payload count"));
    for (std::size_t payload_index = 0U;
         payload_index < response.payloads.size(); ++payload_index) {
        const SyncReplicaReconciliationPayload& payload =
            response.payloads[payload_index];
        append_framed(body, payload.content_sha256);
        append_u64(body, payload.total_size_bytes);
        append_u64(body, payload.offset_bytes);
        append_payload_fields(body, payload, payload_index);
        append_optional_digest_field(
            body, payload.delta_manifest_digest);
        const DeltaManifestView complete_manifest =
            delta_manifest_at(payload_index);
        append_u32(body, complete_manifest.present() ? 1U : 0U);
        if (complete_manifest.present()) {
            const auto& parameters = *complete_manifest.parameters;
            append_u64(body, parameters.minimum_chunk_bytes);
            append_u64(body, parameters.average_chunk_bytes);
            append_u64(body, parameters.maximum_chunk_bytes);
            append_u64(body, parameters.maximum_chunk_count);
            append_u64(
                body,
                size_to_u64_or_throw(
                    complete_manifest.chunk_count(),
                    "sync replica reconciliation content-defined chunk count"));
            for (std::size_t chunk_index = 0U;
                 chunk_index < complete_manifest.chunk_count();
                 ++chunk_index) {
                append_u64(
                    body,
                    complete_manifest.chunk_size_bytes(chunk_index));
                append_framed(
                    body, complete_manifest.chunk_sha256(chunk_index));
            }
        }
        append_u64(body, payload.delta_chunk_offset_bytes);
        append_u64(body, payload.delta_chunk_size_bytes);
    }
    append_u64(
        body,
        size_to_u64_or_throw(
            response.metadata_only_file_operation_ids.size(),
            "sync replica reconciliation response metadata-only operation count"));
    for (const std::string& operation_id :
         response.metadata_only_file_operation_ids) {
        append_framed(body, operation_id);
    }
    append_u32(body, response.has_more ? 1U : 0U);
    append_optional_digest_field(body, response.next_after_operation_id);
    append_optional_digest_field(body, response.blocked_operation_id);
    append_u32(body, response.payload_continuation.has_value() ? 1U : 0U);
    if (response.payload_continuation.has_value()) {
        append_framed(body, response.payload_continuation->operation_id);
        append_framed(body, response.payload_continuation->content_sha256);
        append_u64(body, response.payload_continuation->total_size_bytes);
        append_u64(body, response.payload_continuation->next_offset_bytes);
    }
}

void append_response_body_or_throw(
    std::string& body,
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    append_response_body_impl_or_throw(
        body, response, limits,
        [](std::string& destination,
           const SyncReplicaReconciliationPayload& payload,
           std::size_t) {
            append_framed(destination, payload.chunk_sha256);
            append_framed(destination, payload.bytes);
        }, [&](std::size_t payload_index) {
            const auto& payload = response.payloads[payload_index];
            return payload.delta_manifest.has_value()
                ? DeltaManifestView::from_owned(
                      payload.total_size_bytes, *payload.delta_manifest)
                : DeltaManifestView{};
        });
}

[[nodiscard]] std::string response_body_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_response_or_throw(response, limits);
    const ResponseBodyMetrics metrics =
        response_body_metrics_or_throw(response, limits);
    std::string body;
    body.reserve(u64_to_size_or_throw(
        metrics.body_bytes,
        "sync replica reconciliation response body size"));
    append_response_body_or_throw(body, response, limits);
    if (size_to_u64_or_throw(
            body.size(),
            "sync replica reconciliation response encoded body size") !=
        metrics.body_bytes) {
        throw std::logic_error(
            "sync replica reconciliation response body size projection drifted from canonical encoding");
    }
    return body;
}

template <typename PayloadBytesAt, typename DeltaManifestAt>
void validate_sync_replica_reconciliation_response_impl_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits,
    PayloadBytesAt&& payload_bytes_at,
    DeltaManifestAt&& delta_manifest_at);

[[nodiscard]] SyncReplicaReconciliationResponseDisposition
parse_response_disposition_or_throw(std::uint32_t value) {
    switch (value) {
        case 1U:
            return SyncReplicaReconciliationResponseDisposition::Page;
        case 2U:
            return SyncReplicaReconciliationResponseDisposition::SourceChanged;
        case 3U:
            return SyncReplicaReconciliationResponseDisposition::PayloadUnavailable;
        case 4U:
            return SyncReplicaReconciliationResponseDisposition::
                SourcePayloadPreparing;
        default:
            throw std::runtime_error(
                "sync replica reconciliation response disposition is unknown");
    }
}

[[nodiscard]] SyncReplicaSelectiveSyncMode
parse_selective_sync_mode_or_throw(
    std::uint32_t value,
    std::string_view label) {
    switch (value) {
        case 1U:
            return SyncReplicaSelectiveSyncMode::Materialize;
        case 2U:
            return SyncReplicaSelectiveSyncMode::MetadataOnly;
        default:
            throw std::runtime_error(
                std::string(label) + " selective-sync mode is unknown");
    }
}

[[nodiscard]] SyncReplicaReconciliationRequest parse_request_body_or_throw(
    std::string_view body,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    FrameReader reader(body, "sync replica reconciliation request body");
    SyncReplicaReconciliationRequest request;
    request.folder_id = reader.read_string(
        kSyncManifestIdMaxBytes, "folder_id");
    request.requester_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "requester_device_id");
    request.requester_actor.epoch = reader.read_u64();
    request.responder_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "responder_device_id");
    request.responder_actor.epoch = reader.read_u64();
    request.channel_binding.type = reader.read_string(
        kSyncManifestIdMaxBytes, "channel_binding_type");
    request.channel_binding.digest = reader.read_string(
        kSyncManifestSha256TextBytes, "channel_binding_digest");
    request.after_operation_id =
        reader.read_optional_digest("after_operation_id");
    request.expected_source_evidence_set_digest =
        reader.read_optional_digest("expected_source_evidence_set_digest");
    const std::uint32_t has_payload_continuation = reader.read_u32();
    if (has_payload_continuation > 1U) {
        throw std::runtime_error(
            "sync replica reconciliation request payload continuation presence flag is invalid");
    }
    if (has_payload_continuation == 1U) {
        SyncReplicaReconciliationPayloadContinuation continuation;
        continuation.operation_id = reader.read_string(
            kSyncManifestSha256TextBytes,
            "payload_continuation_operation_id");
        continuation.content_sha256 = reader.read_string(
            kSyncManifestSha256TextBytes,
            "payload_continuation_content_sha256");
        continuation.total_size_bytes = reader.read_u64();
        continuation.next_offset_bytes = reader.read_u64();
        request.payload_continuation = std::move(continuation);
    }
    request.cached_delta_manifest_digest =
        reader.read_optional_digest("cached_delta_manifest_digest");
    request.selective_sync_policy.generation = reader.read_u64();
    request.selective_sync_policy.default_mode =
        parse_selective_sync_mode_or_throw(
            reader.read_u32(),
            "sync replica reconciliation request");
    const std::uint64_t rule_count = reader.read_u64();
    if (rule_count > kSyncReplicaSelectiveSyncMaximumRules) {
        throw std::runtime_error(
            "sync replica reconciliation request selective-sync rule count exceeds its limit");
    }
    request.selective_sync_policy.rule_path_bytes = reader.read_u64();
    if (request.selective_sync_policy.rule_path_bytes >
        kSyncReplicaSelectiveSyncMaximumRulePathBytes) {
        throw std::runtime_error(
            "sync replica reconciliation request selective-sync rule-path bytes exceed their limit");
    }
    request.selective_sync_policy.policy_digest = reader.read_string(
        kSyncManifestSha256TextBytes, "selective_sync_policy_digest");
    request.selective_sync_policy.rules.reserve(u64_to_size_or_throw(
        rule_count,
        "sync replica reconciliation request selective-sync rule count"));
    for (std::uint64_t index = 0U; index < rule_count; ++index) {
        SyncReplicaSelectiveSyncRule rule;
        rule.canonical_path = reader.read_string(
            kSyncManifestRelativePathMaxBytes,
            "selective_sync_rule_path");
        rule.mode = parse_selective_sync_mode_or_throw(
            reader.read_u32(),
            "sync replica reconciliation request rule");
        request.selective_sync_policy.rules.push_back(std::move(rule));
    }
    reader.require_consumed();
    validate_sync_replica_reconciliation_request_or_throw(request, limits);
    return request;
}

[[nodiscard]] SyncReplicaReconciliationBorrowedResponse
parse_response_body_borrowing_payloads_without_validation_or_throw(
    std::string_view body,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    FrameReader reader(body, "sync replica reconciliation response body");
    SyncReplicaReconciliationBorrowedResponse borrowed;
    SyncReplicaReconciliationResponse& response = borrowed.response;
    response.folder_id = reader.read_string(
        kSyncManifestIdMaxBytes, "folder_id");
    response.requester_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "requester_device_id");
    response.requester_actor.epoch = reader.read_u64();
    response.responder_actor.device_id = reader.read_string(
        kSyncManifestIdMaxBytes, "responder_device_id");
    response.responder_actor.epoch = reader.read_u64();
    response.channel_binding.type = reader.read_string(
        kSyncManifestIdMaxBytes, "channel_binding_type");
    response.channel_binding.digest = reader.read_string(
        kSyncManifestSha256TextBytes, "channel_binding_digest");
    response.request_digest = reader.read_string(
        kSyncManifestSha256TextBytes, "request_digest");
    response.disposition =
        parse_response_disposition_or_throw(reader.read_u32());
    response.source_state_generation = reader.read_u64();
    response.source_evidence_count = reader.read_u64();
    response.source_evidence_set_digest = reader.read_string(
        kSyncManifestSha256TextBytes, "source_evidence_set_digest");

    const std::uint64_t operation_count = reader.read_u64();
    if (operation_count > limits.max_operations_per_page) {
        throw std::runtime_error(
            "sync replica reconciliation response operation count exceeds its limit");
    }
    response.operations.reserve(u64_to_size_or_throw(
        operation_count,
        "sync replica reconciliation response operation count"));
    for (std::uint64_t index = 0U; index < operation_count; ++index) {
        const std::string_view canonical = reader.read_view(
            limits.model.max_canonical_operation_bytes,
            "canonical_operation");
        response.operations.push_back(
            decode_sync_replica_operation_canonical_or_throw(
                canonical, limits.model));
    }

    const std::uint64_t payload_count = reader.read_u64();
    if (payload_count > limits.max_payloads_per_page) {
        throw std::runtime_error(
            "sync replica reconciliation response payload count exceeds its limit");
    }
    const std::size_t payload_capacity = u64_to_size_or_throw(
        payload_count,
        "sync replica reconciliation response payload count");
    response.payloads.reserve(payload_capacity);
    borrowed.payload_bytes.reserve(payload_capacity);
    for (std::uint64_t index = 0U; index < payload_count; ++index) {
        SyncReplicaReconciliationPayload payload;
        payload.content_sha256 = reader.read_string(
            kSyncManifestSha256TextBytes, "payload_content_sha256");
        payload.total_size_bytes = reader.read_u64();
        payload.offset_bytes = reader.read_u64();
        payload.chunk_sha256 = reader.read_string(
            kSyncManifestSha256TextBytes, "payload_chunk_sha256");
        borrowed.payload_bytes.push_back(reader.read_view(
            limits.max_single_payload_bytes, "payload_bytes"));
        payload.delta_manifest_digest =
            reader.read_optional_digest("payload_delta_manifest_digest");
        const std::uint32_t has_delta_manifest = reader.read_u32();
        if (has_delta_manifest > 1U) {
            throw std::runtime_error(
                "sync replica reconciliation response content-defined manifest presence flag is invalid");
        }
        if (has_delta_manifest == 1U) {
            SyncReplicaReconciliationDeltaManifest manifest;
            manifest.parameters.minimum_chunk_bytes = reader.read_u64();
            manifest.parameters.average_chunk_bytes = reader.read_u64();
            manifest.parameters.maximum_chunk_bytes = reader.read_u64();
            manifest.parameters.maximum_chunk_count = reader.read_u64();
            const std::uint64_t chunk_count = reader.read_u64();
            if (chunk_count >
                kSyncReplicaReconciliationMaximumContentDefinedChunks) {
                throw std::runtime_error(
                    "sync replica reconciliation response content-defined manifest exceeds its count limit");
            }
            manifest.chunks.reserve(u64_to_size_or_throw(
                chunk_count,
                "sync replica reconciliation content-defined chunk count"));
            for (std::uint64_t chunk_index = 0U;
                 chunk_index < chunk_count; ++chunk_index) {
                manifest.chunks.push_back({
                    reader.read_u64(),
                    reader.read_view(
                        kSyncManifestSha256TextBytes,
                        "payload_content_defined_chunk_sha256"),
                });
            }
            payload.delta_manifest = std::move(manifest);
        }
        payload.delta_chunk_offset_bytes = reader.read_u64();
        payload.delta_chunk_size_bytes = reader.read_u64();
        response.payloads.push_back(std::move(payload));
    }
    const std::uint64_t metadata_only_count = reader.read_u64();
    if (metadata_only_count > limits.max_operations_per_page) {
        throw std::runtime_error(
            "sync replica reconciliation response metadata-only operation count exceeds its limit");
    }
    response.metadata_only_file_operation_ids.reserve(u64_to_size_or_throw(
        metadata_only_count,
        "sync replica reconciliation response metadata-only operation count"));
    for (std::uint64_t index = 0U; index < metadata_only_count; ++index) {
        response.metadata_only_file_operation_ids.push_back(
            reader.read_string(
                kSyncManifestSha256TextBytes,
                "metadata_only_file_operation_id"));
    }
    const std::uint32_t has_more = reader.read_u32();
    if (has_more > 1U) {
        throw std::runtime_error(
            "sync replica reconciliation response has-more flag is invalid");
    }
    response.has_more = has_more == 1U;
    response.next_after_operation_id =
        reader.read_optional_digest("next_after_operation_id");
    response.blocked_operation_id =
        reader.read_optional_digest("blocked_operation_id");
    const std::uint32_t has_payload_continuation = reader.read_u32();
    if (has_payload_continuation > 1U) {
        throw std::runtime_error(
            "sync replica reconciliation response payload continuation presence flag is invalid");
    }
    if (has_payload_continuation == 1U) {
        SyncReplicaReconciliationPayloadContinuation continuation;
        continuation.operation_id = reader.read_string(
            kSyncManifestSha256TextBytes,
            "payload_continuation_operation_id");
        continuation.content_sha256 = reader.read_string(
            kSyncManifestSha256TextBytes,
            "payload_continuation_content_sha256");
        continuation.total_size_bytes = reader.read_u64();
        continuation.next_offset_bytes = reader.read_u64();
        response.payload_continuation = std::move(continuation);
    }
    reader.require_consumed();
    return borrowed;
}

[[nodiscard]] SyncReplicaReconciliationBorrowedResponse
parse_response_body_borrowing_payloads_or_throw(
    std::string_view body,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    SyncReplicaReconciliationBorrowedResponse borrowed =
        parse_response_body_borrowing_payloads_without_validation_or_throw(
            body, limits);
    validate_sync_replica_reconciliation_response_impl_or_throw(
        borrowed.response, limits, [&](std::size_t payload_index) {
            return borrowed.payload_bytes[payload_index];
        }, [&](std::size_t payload_index) {
            const auto& payload = borrowed.response.payloads[payload_index];
            return payload.delta_manifest.has_value()
                ? DeltaManifestView::from_owned(
                      payload.total_size_bytes, *payload.delta_manifest)
                : DeltaManifestView{};
        });
    return borrowed;
}

[[nodiscard]] SyncReplicaReconciliationResponse parse_response_body_or_throw(
    std::string_view body,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    SyncReplicaReconciliationBorrowedResponse borrowed =
        parse_response_body_borrowing_payloads_or_throw(body, limits);
    if (borrowed.response.payloads.size() != borrowed.payload_bytes.size()) {
        throw std::logic_error(
            "sync replica reconciliation borrowed payload cardinality changed after validation");
    }
    for (std::size_t index = 0U; index < borrowed.payload_bytes.size();
         ++index) {
        borrowed.response.payloads[index].bytes.assign(
            borrowed.payload_bytes[index]);
    }
    return std::move(borrowed.response);
}

}  // namespace

SyncReplicaContentDefinedChunkingParameters
sync_replica_reconciliation_content_defined_parameters_or_throw(
    std::uint64_t total_size_bytes) {
    if (total_size_bytes == 0U ||
        total_size_bytes > kSyncReplicaMaximumPayloadExtentBytes) {
        throw std::invalid_argument(
            "sync replica reconciliation content-defined payload extent is invalid");
    }
    std::uint64_t average =
        kSyncReplicaReconciliationMinimumAverageChunkBytes;
    while (1U + ((total_size_bytes - 1U) / average) > 4096U) {
        if (average >=
            kSyncReplicaReconciliationMaximumAverageChunkBytes) {
            break;
        }
        average *= 2U;
    }
    SyncReplicaContentDefinedChunkingParameters parameters{
        average / 2U,
        average,
        average * 2U,
        kSyncReplicaReconciliationMaximumContentDefinedChunks,
    };
    validate_sync_replica_content_defined_chunking_parameters_or_throw(
        parameters,
        "sync replica reconciliation canonical content-defined parameters");
    const std::uint64_t worst_case_count =
        1U + ((total_size_bytes - 1U) / parameters.minimum_chunk_bytes);
    if (worst_case_count > parameters.maximum_chunk_count) {
        throw std::length_error(
            "sync replica reconciliation payload exceeds the bounded content-defined manifest extent");
    }
    return parameters;
}

std::string
sync_replica_reconciliation_delta_manifest_digest_or_throw(
    std::string_view content_sha256,
    std::uint64_t total_size_bytes,
    const SyncReplicaReconciliationDeltaManifest& manifest) {
    const DeltaManifestView view = DeltaManifestView::from_owned(
        total_size_bytes, manifest);
    return delta_manifest_digest_for_view_or_throw(
        content_sha256, total_size_bytes, view);
}

SyncReplicaReconciliationPayload::SyncReplicaReconciliationPayload(
    std::string content_digest,
    std::string whole_payload)
    : content_sha256(std::move(content_digest)),
      total_size_bytes(size_to_u64_or_throw(
          whole_payload.size(),
          "sync replica reconciliation whole payload size")),
      offset_bytes(0U),
      chunk_sha256(content_sha256),
      bytes(std::move(whole_payload)) {}

SyncReplicaReconciliationPayload::SyncReplicaReconciliationPayload(
    std::string content_digest,
    std::uint64_t total_size,
    std::uint64_t offset,
    std::string chunk_digest,
    std::string range_bytes,
    SyncReplicaReconciliationDeltaManifest manifest,
    std::uint64_t containing_chunk_offset,
    std::uint64_t containing_chunk_size)
    : content_sha256(std::move(content_digest)),
      total_size_bytes(total_size),
      offset_bytes(offset),
      chunk_sha256(std::move(chunk_digest)),
      bytes(std::move(range_bytes)),
      delta_manifest_digest(
          sync_replica_reconciliation_delta_manifest_digest_or_throw(
              content_sha256, total_size_bytes, manifest)),
      delta_manifest(std::move(manifest)),
      delta_chunk_offset_bytes(containing_chunk_offset),
      delta_chunk_size_bytes(containing_chunk_size) {}

SyncReplicaReconciliationPayload::SyncReplicaReconciliationPayload(
    std::string content_digest,
    std::uint64_t total_size,
    std::uint64_t offset,
    std::string chunk_digest,
    std::string range_bytes,
    std::string manifest_digest,
    std::uint64_t containing_chunk_offset,
    std::uint64_t containing_chunk_size)
    : content_sha256(std::move(content_digest)),
      total_size_bytes(total_size),
      offset_bytes(offset),
      chunk_sha256(std::move(chunk_digest)),
      bytes(std::move(range_bytes)),
      delta_manifest_digest(std::move(manifest_digest)),
      delta_chunk_offset_bytes(containing_chunk_offset),
      delta_chunk_size_bytes(containing_chunk_size) {}

bool sync_replica_reconciliation_request_frame_has_magic(
    std::string_view frame) noexcept {
    return frame.starts_with(kRequestMagic);
}

void validate_sync_replica_reconciliation_protocol_limits_or_throw(
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
}

void validate_sync_replica_reconciliation_request_or_throw(
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    if (!sync_id_is_valid(request.folder_id)) {
        throw std::invalid_argument(
            "sync replica reconciliation request folder identity is invalid");
    }
    validate_actor_or_throw(
        request.requester_actor,
        "sync replica reconciliation requester");
    validate_actor_or_throw(
        request.responder_actor,
        "sync replica reconciliation responder");
    if (request.requester_actor.device_id ==
        request.responder_actor.device_id) {
        throw std::invalid_argument(
            "sync replica reconciliation request actors must name distinct devices");
    }
    validate_sync_replica_delivery_channel_binding_or_throw(
        request.channel_binding,
        "sync replica reconciliation request");
    if (request.after_operation_id.has_value() &&
        !request.expected_source_evidence_set_digest.has_value()) {
        throw std::invalid_argument(
            "sync replica reconciliation request cursor lacks its source digest");
    }
    if (request.payload_continuation.has_value() &&
        !request.expected_source_evidence_set_digest.has_value()) {
        throw std::invalid_argument(
            "sync replica reconciliation request payload continuation lacks its source digest");
    }
    if (request.expected_source_evidence_set_digest.has_value() &&
        !request.after_operation_id.has_value() &&
        !request.payload_continuation.has_value()) {
        throw std::invalid_argument(
            "sync replica reconciliation request source digest has no continuation authority");
    }
    if (request.after_operation_id.has_value() &&
        !is_lowercase_sha256_hex(*request.after_operation_id)) {
        throw std::invalid_argument(
            "sync replica reconciliation request cursor is not lowercase SHA-256");
    }
    if (request.expected_source_evidence_set_digest.has_value() &&
        !is_lowercase_sha256_hex(
            *request.expected_source_evidence_set_digest)) {
        throw std::invalid_argument(
            "sync replica reconciliation request source digest is not lowercase SHA-256");
    }
    if (request.payload_continuation.has_value()) {
        validate_payload_continuation_or_throw(
            *request.payload_continuation, limits,
            "sync replica reconciliation request payload continuation");
        if (request.after_operation_id.has_value() &&
            request.payload_continuation->operation_id <=
                *request.after_operation_id) {
            throw std::invalid_argument(
                "sync replica reconciliation request payload operation does not follow its cursor");
        }
    }
    if (request.cached_delta_manifest_digest.has_value()) {
        if (!request.payload_continuation.has_value()) {
            throw std::invalid_argument(
                "sync replica reconciliation request cached content-defined manifest has no payload continuation");
        }
        if (!is_lowercase_sha256_hex(
                *request.cached_delta_manifest_digest)) {
            throw std::invalid_argument(
                "sync replica reconciliation request cached delta manifest digest is invalid");
        }
        if (request.payload_continuation->next_offset_bytes ==
            request.payload_continuation->total_size_bytes) {
            throw std::invalid_argument(
                "sync replica reconciliation terminal verification continuation cannot carry a cached delta manifest");
        }
    }
    validate_sync_replica_selective_sync_policy_or_throw(
        request.selective_sync_policy,
        "sync replica reconciliation request selective-sync policy");
}

namespace {

template <typename PayloadBytesAt, typename DeltaManifestAt>
void validate_sync_replica_reconciliation_response_impl_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits,
    PayloadBytesAt&& payload_bytes_at,
    DeltaManifestAt&& delta_manifest_at) {
    validate_protocol_limits_impl_or_throw(limits);
    if (!sync_id_is_valid(response.folder_id)) {
        throw std::invalid_argument(
            "sync replica reconciliation response folder identity is invalid");
    }
    validate_actor_or_throw(
        response.requester_actor,
        "sync replica reconciliation response requester");
    validate_actor_or_throw(
        response.responder_actor,
        "sync replica reconciliation response responder");
    if (response.requester_actor.device_id ==
        response.responder_actor.device_id) {
        throw std::invalid_argument(
            "sync replica reconciliation response actors must name distinct devices");
    }
    validate_sync_replica_delivery_channel_binding_or_throw(
        response.channel_binding,
        "sync replica reconciliation response");
    if (!is_lowercase_sha256_hex(response.request_digest)) {
        throw std::invalid_argument(
            "sync replica reconciliation response request digest is invalid");
    }
    if (!response_disposition_is_known(response.disposition)) {
        throw std::invalid_argument(
            "sync replica reconciliation response disposition is unknown");
    }
    if (!is_lowercase_sha256_hex(response.source_evidence_set_digest)) {
        throw std::invalid_argument(
            "sync replica reconciliation response source evidence digest is invalid");
    }
    if (response.operations.size() >
        u64_to_size_or_throw(
            limits.max_operations_per_page,
            "sync replica reconciliation operation count limit")) {
        throw std::invalid_argument(
            "sync replica reconciliation response has too many operations");
    }
    if (response.payloads.size() >
        u64_to_size_or_throw(
            limits.max_payloads_per_page,
            "sync replica reconciliation payload count limit")) {
        throw std::invalid_argument(
            "sync replica reconciliation response has too many payloads");
    }

    std::uint64_t canonical_bytes = 0U;
    std::string previous_operation_id;
    std::set<std::string> referenced_payloads;
    std::map<std::string, const SyncReplicaOperation*> operations_by_id;
    for (const SyncReplicaOperation& operation : response.operations) {
        validate_sync_replica_operation_or_throw(operation, limits.model);
        if (operation.folder_id != response.folder_id) {
            throw std::invalid_argument(
                "sync replica reconciliation response operation belongs to another folder");
        }
        if (!previous_operation_id.empty() &&
            operation.operation_id <= previous_operation_id) {
            throw std::invalid_argument(
                "sync replica reconciliation response operations are not strictly sorted and unique");
        }
        previous_operation_id = operation.operation_id;
        const std::uint64_t bytes =
            sync_replica_operation_canonical_size_or_throw(
                operation, limits.model);
        if (bytes >
            limits.max_canonical_operation_bytes_per_page -
                canonical_bytes) {
            throw std::invalid_argument(
                "sync replica reconciliation response canonical operation bytes exceed the page budget");
        }
        canonical_bytes += bytes;
        if (operation.kind == SyncReplicaValueKind::File) {
            referenced_payloads.insert(operation.content_sha256);
        }
        operations_by_id.emplace(operation.operation_id, &operation);
    }
    if (response.source_evidence_count < response.operations.size()) {
        throw std::invalid_argument(
            "sync replica reconciliation response source evidence count is smaller than its page");
    }

    if (response.metadata_only_file_operation_ids.size() >
        response.operations.size()) {
        throw std::invalid_argument(
            "sync replica reconciliation response has too many metadata-only operation IDs");
    }
    std::set<std::string> metadata_only_operation_ids;
    std::string previous_metadata_only_operation_id;
    for (const std::string& operation_id :
         response.metadata_only_file_operation_ids) {
        if (!is_lowercase_sha256_hex(operation_id) ||
            (!previous_metadata_only_operation_id.empty() &&
             operation_id <= previous_metadata_only_operation_id)) {
            throw std::invalid_argument(
                "sync replica reconciliation response metadata-only operation IDs are not canonical, strictly sorted, and unique");
        }
        const auto found = operations_by_id.find(operation_id);
        if (found == operations_by_id.end() ||
            found->second->kind != SyncReplicaValueKind::File) {
            throw std::invalid_argument(
                "sync replica reconciliation response metadata-only ID does not name a returned file operation");
        }
        metadata_only_operation_ids.insert(operation_id);
        previous_metadata_only_operation_id = operation_id;
    }
    std::set<std::string> materialized_payloads;
    for (const SyncReplicaOperation& operation : response.operations) {
        if (operation.kind == SyncReplicaValueKind::File &&
            !metadata_only_operation_ids.contains(operation.operation_id)) {
            materialized_payloads.insert(operation.content_sha256);
        }
    }

    struct PayloadGroup final {
        std::uint64_t total_size_bytes = 0U;
        std::uint64_t next_offset_bytes = 0U;
        bool whole = false;
        std::optional<std::string> manifest_digest;
        std::optional<DeltaManifestView> complete_manifest;
        std::uint64_t range_count = 0U;
    };

    std::uint64_t payload_bytes = 0U;
    std::string previous_payload_digest;
    std::uint64_t previous_payload_offset = 0U;
    std::map<std::string, PayloadGroup> payload_groups_by_digest;
    for (std::size_t payload_index = 0U;
         payload_index < response.payloads.size(); ++payload_index) {
        const SyncReplicaReconciliationPayload& payload =
            response.payloads[payload_index];
        const std::string_view payload_bytes_view =
            payload_bytes_at(payload_index);
        const DeltaManifestView complete_manifest =
            delta_manifest_at(payload_index);
        if (!is_lowercase_sha256_hex(payload.content_sha256) ||
            !is_lowercase_sha256_hex(payload.chunk_sha256)) {
            throw std::invalid_argument(
                "sync replica reconciliation response payload digest is invalid");
        }
        if (!previous_payload_digest.empty() &&
            (payload.content_sha256 < previous_payload_digest ||
             (payload.content_sha256 == previous_payload_digest &&
              payload.offset_bytes <= previous_payload_offset))) {
            throw std::invalid_argument(
                "sync replica reconciliation response payload ranges are not strictly sorted and unique by digest and offset");
        }
        if (payload.content_sha256 != previous_payload_digest) {
            previous_payload_digest = payload.content_sha256;
            previous_payload_offset = payload.offset_bytes;
        } else {
            previous_payload_offset = payload.offset_bytes;
        }

        const std::uint64_t bytes = size_to_u64_or_throw(
            payload_bytes_view.size(),
            "sync replica reconciliation response payload size");
        if (bytes > limits.max_single_payload_bytes) {
            throw std::invalid_argument(
                "sync replica reconciliation response payload exceeds the single-payload limit");
        }
        if (bytes > limits.max_payload_bytes_per_page - payload_bytes) {
            throw std::invalid_argument(
                "sync replica reconciliation response payload bytes exceed the page budget");
        }
        payload_bytes += bytes;
        if (payload.total_size_bytes > limits.max_payload_extent_bytes ||
            payload.offset_bytes > payload.total_size_bytes ||
            bytes > payload.total_size_bytes - payload.offset_bytes ||
            (payload.total_size_bytes != 0U && bytes == 0U)) {
            throw std::invalid_argument(
                "sync replica reconciliation response payload range extent is invalid");
        }
        if (sha256_view_or_throw(payload_bytes_view) != payload.chunk_sha256) {
            throw std::invalid_argument(
                "sync replica reconciliation response chunk digest does not match its bytes");
        }
        const bool whole = payload.offset_bytes == 0U &&
                           bytes == payload.total_size_bytes;
        if (whole && payload.chunk_sha256 != payload.content_sha256) {
            throw std::invalid_argument(
                "sync replica reconciliation response whole payload digest does not match its bytes");
        }

        auto [group_it, inserted] = payload_groups_by_digest.try_emplace(
            payload.content_sha256);
        PayloadGroup& group = group_it->second;
        if (inserted) {
            group.total_size_bytes = payload.total_size_bytes;
            group.next_offset_bytes = payload.offset_bytes;
            group.whole = whole;
        } else {
            if (group.total_size_bytes != payload.total_size_bytes) {
                throw std::invalid_argument(
                    "sync replica reconciliation response payload ranges disagree about total size");
            }
            if (group.whole || whole) {
                throw std::invalid_argument(
                    "sync replica reconciliation response whole payload is not its digest's unique range");
            }
            if (payload.offset_bytes != group.next_offset_bytes) {
                throw std::invalid_argument(
                    "sync replica reconciliation response payload ranges are not exactly contiguous");
            }
        }

        if (whole) {
            if (payload.delta_manifest_digest.has_value() ||
                complete_manifest.present() ||
                payload.delta_chunk_offset_bytes != 0U ||
                payload.delta_chunk_size_bytes != 0U) {
                throw std::invalid_argument(
                    "sync replica reconciliation whole payload carries unnecessary content-defined manifest authority");
            }
        } else {
            if (!payload.delta_manifest_digest.has_value() ||
                !is_lowercase_sha256_hex(*payload.delta_manifest_digest)) {
                throw std::invalid_argument(
                    "sync replica reconciliation ranged payload lacks a valid content-defined manifest digest");
            }
            if (!group.manifest_digest.has_value()) {
                group.manifest_digest = payload.delta_manifest_digest;
            } else if (group.manifest_digest != payload.delta_manifest_digest) {
                throw std::invalid_argument(
                    "sync replica reconciliation ranged payloads disagree about their content-defined manifest");
            }
            if (payload.delta_chunk_size_bytes == 0U ||
                payload.delta_chunk_offset_bytes > payload.offset_bytes ||
                payload.delta_chunk_offset_bytes > payload.total_size_bytes ||
                payload.delta_chunk_size_bytes >
                    payload.total_size_bytes -
                        payload.delta_chunk_offset_bytes) {
                throw std::invalid_argument(
                    "sync replica reconciliation ranged payload declares an invalid content-defined chunk extent");
            }
            const std::uint64_t within_chunk =
                payload.offset_bytes - payload.delta_chunk_offset_bytes;
            if (within_chunk > payload.delta_chunk_size_bytes ||
                bytes > payload.delta_chunk_size_bytes - within_chunk) {
                throw std::invalid_argument(
                    "sync replica reconciliation ranged payload crosses its content-defined chunk boundary");
            }
            if (complete_manifest.present()) {
                if (group.range_count != 0U) {
                    throw std::invalid_argument(
                        "sync replica reconciliation complete content-defined manifest is not confined to the first range of its payload group");
                }
                validate_delta_manifest_view_or_throw(
                    payload.total_size_bytes, complete_manifest,
                    "sync replica reconciliation content-defined manifest");
                if (*payload.delta_manifest_digest !=
                    delta_manifest_digest_for_view_or_throw(
                        payload.content_sha256, payload.total_size_bytes,
                        complete_manifest)) {
                    throw std::invalid_argument(
                        "sync replica reconciliation content-defined manifest digest does not match its complete manifest");
                }
                group.complete_manifest = complete_manifest;
            }
            if (group.complete_manifest.has_value()) {
                validate_payload_range_against_delta_manifest_or_throw(
                    payload, payload_bytes_view, *group.complete_manifest,
                    "sync replica reconciliation ranged payload");
            }
        }
        if (!referenced_payloads.contains(payload.content_sha256) ||
            !materialized_payloads.contains(payload.content_sha256)) {
            throw std::invalid_argument(
                "sync replica reconciliation response contains an unreferenced payload not required by a materialized file operation");
        }
        ++group.range_count;
        group.next_offset_bytes = payload.offset_bytes + bytes;
    }

    const bool terminal_continuation =
        response.payload_continuation.has_value() &&
        response.payload_continuation->next_offset_bytes ==
            response.payload_continuation->total_size_bytes;
    const SyncReplicaOperation* ranged_operation = nullptr;
    const PayloadGroup* ranged_group = nullptr;
    for (const SyncReplicaOperation& operation : response.operations) {
        if (operation.kind != SyncReplicaValueKind::File) continue;
        if (metadata_only_operation_ids.contains(operation.operation_id)) {
            continue;
        }
        const auto found = payload_groups_by_digest.find(
            operation.content_sha256);
        const bool terminal_payload_cold_operation =
            terminal_continuation &&
            response.payload_continuation->operation_id ==
                operation.operation_id &&
            response.payload_continuation->content_sha256 ==
                operation.content_sha256 &&
            response.payload_continuation->total_size_bytes ==
                operation.size_bytes &&
            found == payload_groups_by_digest.end();
        if (terminal_payload_cold_operation) continue;
        if (found == payload_groups_by_digest.end() ||
            found->second.total_size_bytes != operation.size_bytes) {
            throw std::invalid_argument(
                "sync replica reconciliation response does not contain a size-bound range group for every file operation");
        }
        const PayloadGroup& group = found->second;
        if (!group.whole) {
            if (ranged_operation != nullptr ||
                &operation != &response.operations.back()) {
                throw std::invalid_argument(
                    "sync replica reconciliation response ranged payload group is not its unique final operation");
            }
            ranged_operation = &operation;
            ranged_group = &group;
        }
    }

    if (response.next_after_operation_id.has_value() &&
        !is_lowercase_sha256_hex(*response.next_after_operation_id)) {
        throw std::invalid_argument(
            "sync replica reconciliation response next cursor is invalid");
    }
    if (response.blocked_operation_id.has_value() &&
        !is_lowercase_sha256_hex(*response.blocked_operation_id)) {
        throw std::invalid_argument(
            "sync replica reconciliation response blocked operation ID is invalid");
    }
    if (response.payload_continuation.has_value()) {
        validate_payload_continuation_or_throw(
            *response.payload_continuation, limits,
            "sync replica reconciliation response payload continuation");
        const bool payload_cold_terminal =
            terminal_continuation && ranged_operation == nullptr &&
            ranged_group == nullptr;
        if (payload_cold_terminal) {
            if (response.operations.size() != 1U ||
                !response.payloads.empty() ||
                !response.metadata_only_file_operation_ids.empty()) {
                throw std::invalid_argument(
                    "sync replica reconciliation terminal verification continuation did not return one exact payload-cold operation");
            }
            const SyncReplicaOperation& operation = response.operations.front();
            if (operation.kind != SyncReplicaValueKind::File ||
                response.payload_continuation->operation_id !=
                    operation.operation_id ||
                response.payload_continuation->content_sha256 !=
                    operation.content_sha256 ||
                response.payload_continuation->total_size_bytes !=
                    operation.size_bytes ||
                response.next_after_operation_id ==
                    std::optional<std::string>(operation.operation_id)) {
                throw std::invalid_argument(
                    "sync replica reconciliation terminal verification continuation does not bind its exact file operation and prior cursor");
            }
        } else {
            if (response.operations.empty() || ranged_operation == nullptr ||
                ranged_group == nullptr ||
                response.payload_continuation->operation_id !=
                    response.operations.back().operation_id ||
                response.payload_continuation->content_sha256 !=
                    ranged_operation->content_sha256 ||
                response.payload_continuation->total_size_bytes !=
                    ranged_operation->size_bytes) {
                throw std::invalid_argument(
                    "sync replica reconciliation response payload continuation does not bind its final operation");
            }
            const std::uint64_t range_end = ranged_group->next_offset_bytes;
            if (range_end != response.payload_continuation->next_offset_bytes ||
                range_end > ranged_group->total_size_bytes) {
                throw std::invalid_argument(
                    "sync replica reconciliation response payload continuation does not follow its exact contiguous range group");
            }
            if (response.next_after_operation_id ==
                std::optional<std::string>(ranged_operation->operation_id)) {
                throw std::invalid_argument(
                    "sync replica reconciliation response advanced its operation cursor before payload completion");
            }
            if (response.operations.size() >= 2U &&
                response.next_after_operation_id !=
                    std::optional<std::string>(
                        response.operations[response.operations.size() - 2U]
                            .operation_id)) {
                throw std::invalid_argument(
                    "sync replica reconciliation response payload continuation skipped its completed prefix");
            }
        }
    } else {
        if (ranged_group != nullptr) {
            if (ranged_group->next_offset_bytes !=
                ranged_group->total_size_bytes) {
                throw std::invalid_argument(
                    "sync replica reconciliation response incomplete range group lacks continuation authority");
            }
        }
        if (!response.operations.empty() &&
            response.next_after_operation_id !=
                std::optional<std::string>(
                    response.operations.back().operation_id)) {
            throw std::invalid_argument(
                "sync replica reconciliation response next cursor is not its last completed operation");
        }
    }

    switch (response.disposition) {
        case SyncReplicaReconciliationResponseDisposition::Page:
            if (response.blocked_operation_id.has_value()) {
                throw std::invalid_argument(
                    "sync replica reconciliation page cannot name a blocked operation");
            }
            if (response.has_more && response.operations.empty()) {
                throw std::invalid_argument(
                    "sync replica reconciliation nonterminal page made no cursor progress");
            }
            if (response.payload_continuation.has_value() &&
                !response.has_more) {
                throw std::invalid_argument(
                    "sync replica reconciliation payload continuation is not marked nonterminal");
            }
            break;
        case SyncReplicaReconciliationResponseDisposition::SourceChanged:
            if (!response.operations.empty() || !response.payloads.empty() ||
                !response.metadata_only_file_operation_ids.empty() ||
                response.has_more ||
                response.next_after_operation_id.has_value() ||
                response.blocked_operation_id.has_value() ||
                response.payload_continuation.has_value()) {
                throw std::invalid_argument(
                    "sync replica reconciliation source-changed response carries page authority");
            }
            break;
        case SyncReplicaReconciliationResponseDisposition::PayloadUnavailable:
            if (!response.has_more ||
                !response.blocked_operation_id.has_value() ||
                response.payload_continuation.has_value() ||
                !response.metadata_only_file_operation_ids.empty()) {
                throw std::invalid_argument(
                    "sync replica reconciliation payload-unavailable response lacks an exact blocked continuation");
            }
            if (std::any_of(
                    response.operations.begin(), response.operations.end(),
                    [&](const SyncReplicaOperation& operation) {
                        return operation.operation_id ==
                               *response.blocked_operation_id;
                    })) {
                throw std::invalid_argument(
                    "sync replica reconciliation blocked operation is already included in the response");
            }
            if (!response.operations.empty() &&
                *response.blocked_operation_id <=
                    response.operations.back().operation_id) {
                throw std::invalid_argument(
                    "sync replica reconciliation blocked operation does not follow the transferable prefix");
            }
            break;
        case SyncReplicaReconciliationResponseDisposition::
            SourcePayloadPreparing:
            if (!response.has_more ||
                !response.blocked_operation_id.has_value() ||
                response.payload_continuation.has_value()) {
                throw std::invalid_argument(
                    "sync replica reconciliation source-preparing response lacks an exact blocked continuation");
            }
            if (std::any_of(
                    response.operations.begin(), response.operations.end(),
                    [&](const SyncReplicaOperation& operation) {
                        return operation.operation_id ==
                               *response.blocked_operation_id;
                    })) {
                throw std::invalid_argument(
                    "sync replica reconciliation preparing operation is already included in the response");
            }
            if (!response.operations.empty() &&
                *response.blocked_operation_id <=
                    response.operations.back().operation_id) {
                throw std::invalid_argument(
                    "sync replica reconciliation preparing operation does not follow the transferable prefix");
            }
            break;
    }
}


[[nodiscard]] SyncReplicaReconciliationEncodedResponse
encode_sync_replica_reconciliation_response_after_validation_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits,
    bool derive_semantic_digest) {
    const ResponseBodyMetrics metrics =
        response_body_metrics_or_throw(response, limits);
    const std::uint64_t frame_bytes = checked_add_u64_or_throw(
        fixed_frame_bytes(kResponseMagic), metrics.body_bytes,
        "sync replica reconciliation response frame size");
    if (frame_bytes > limits.max_response_frame_bytes) {
        throw std::invalid_argument(
            "sync replica reconciliation response exceeds its frame limit");
    }

    std::string frame;
    frame.reserve(u64_to_size_or_throw(
        frame_bytes,
        "sync replica reconciliation response exact frame size"));
    frame.append(kResponseMagic);
    append_u32(frame, kSyncReplicaReconciliationProtocolVersion);
    append_u64(frame, metrics.body_bytes);
    const std::size_t body_begin = frame.size();
    append_response_body_or_throw(frame, response, limits);
    if (frame.size() < body_begin ||
        size_to_u64_or_throw(
            frame.size() - body_begin,
            "sync replica reconciliation response direct body size") !=
            metrics.body_bytes) {
        throw std::logic_error(
            "sync replica reconciliation response direct encoder drifted from its exact body size");
    }
    const std::string_view body(
        frame.data() + body_begin,
        u64_to_size_or_throw(
            metrics.body_bytes,
            "sync replica reconciliation response direct body view"));
    std::string response_digest;
    if (derive_semantic_digest) {
        response_digest = body_digest_or_throw(kResponseDigestDomain, body);
    }
    frame.append(body_digest_or_throw(
        kResponseStructuralDigestDomain, body));
    if (size_to_u64_or_throw(
            frame.size(),
            "sync replica reconciliation response direct frame size") !=
        frame_bytes) {
        throw std::logic_error(
            "sync replica reconciliation response direct encoder drifted from its exact frame size");
    }
    return {
        std::move(frame), response_digest, metrics.body_bytes,
        metrics.payload_bytes};
}

}  // namespace

void validate_sync_replica_reconciliation_response_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_response_impl_or_throw(
        response, limits, [&](std::size_t payload_index) {
            return std::string_view(response.payloads[payload_index].bytes);
        }, [&](std::size_t payload_index) {
            const auto& payload = response.payloads[payload_index];
            return payload.delta_manifest.has_value()
                ? DeltaManifestView::from_owned(
                      payload.total_size_bytes, *payload.delta_manifest)
                : DeltaManifestView{};
        });
}

std::string encode_sync_replica_reconciliation_request_or_throw(
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    return make_frame_or_throw(
        kRequestMagic, kRequestStructuralDigestDomain,
        request_body_or_throw(request, limits),
        limits.max_request_frame_bytes,
        "sync replica reconciliation request");
}

SyncReplicaReconciliationRequest
    decode_sync_replica_reconciliation_request_or_throw(
        std::string_view frame,
        const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    return parse_request_body_or_throw(
        extract_body_or_throw(
            frame, kRequestMagic, kRequestStructuralDigestDomain,
            limits.max_request_frame_bytes,
            "sync replica reconciliation request"),
        limits);
}

std::string sync_replica_reconciliation_request_digest_or_throw(
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    return body_digest_or_throw(
        kRequestDigestDomain, request_body_or_throw(request, limits));
}

SyncReplicaReconciliationEncodedResponse
encode_sync_replica_reconciliation_response_with_digest_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_response_or_throw(response, limits);
    return encode_sync_replica_reconciliation_response_after_validation_or_throw(
        response, limits, true);
}


std::string encode_sync_replica_reconciliation_response_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_response_or_throw(response, limits);
    return encode_sync_replica_reconciliation_response_after_validation_or_throw(
               response, limits, false)
        .frame;
}

SyncReplicaReconciliationBorrowedResponse
decode_sync_replica_reconciliation_response_borrowing_payloads_or_throw(
    std::string_view frame,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    return parse_response_body_borrowing_payloads_or_throw(
        extract_body_or_throw(
            frame, kResponseMagic, kResponseStructuralDigestDomain,
            limits.max_response_frame_bytes,
            "sync replica reconciliation response"),
        limits);
}

SyncReplicaReconciliationResponse
    decode_sync_replica_reconciliation_response_or_throw(
        std::string_view frame,
        const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    return parse_response_body_or_throw(
        extract_body_or_throw(
            frame, kResponseMagic, kResponseStructuralDigestDomain,
            limits.max_response_frame_bytes,
            "sync replica reconciliation response"),
        limits);
}

std::string sync_replica_reconciliation_response_digest_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    return body_digest_or_throw(
        kResponseDigestDomain, response_body_or_throw(response, limits));
}

namespace {

template <typename PayloadBytesAt, typename DeltaManifestAt>
void validate_sync_replica_reconciliation_response_for_request_impl_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits,
    PayloadBytesAt&& payload_bytes_at,
    DeltaManifestAt&& delta_manifest_at) {
    validate_sync_replica_reconciliation_request_or_throw(request, limits);
    validate_sync_replica_reconciliation_response_impl_or_throw(
        response, limits, payload_bytes_at, delta_manifest_at);
    if (response.folder_id != request.folder_id ||
        response.requester_actor != request.requester_actor ||
        response.responder_actor != request.responder_actor ||
        response.channel_binding != request.channel_binding ||
        response.request_digest !=
            sync_replica_reconciliation_request_digest_or_throw(
                request, limits)) {
        throw std::runtime_error(
            "sync replica reconciliation response does not bind the exact request, actors, folder, and channel");
    }

    if (response.disposition ==
        SyncReplicaReconciliationResponseDisposition::SourceChanged) {
        if (!request.expected_source_evidence_set_digest.has_value() ||
            response.source_evidence_set_digest ==
                *request.expected_source_evidence_set_digest) {
            throw std::runtime_error(
                "sync replica reconciliation source-changed response does not prove a changed continued source");
        }
        return;
    }

    if (request.expected_source_evidence_set_digest.has_value() &&
        response.source_evidence_set_digest !=
            *request.expected_source_evidence_set_digest) {
        throw std::runtime_error(
            "sync replica reconciliation response changed source without an explicit reset disposition");
    }
    std::vector<std::string> expected_metadata_only_operation_ids;
    expected_metadata_only_operation_ids.reserve(response.operations.size());
    for (const SyncReplicaOperation& operation : response.operations) {
        if (operation.kind == SyncReplicaValueKind::File &&
            !sync_replica_selective_sync_path_is_materialized(
                request.selective_sync_policy,
                operation.canonical_path)) {
            expected_metadata_only_operation_ids.push_back(
                operation.operation_id);
        }
    }
    if (response.metadata_only_file_operation_ids !=
        expected_metadata_only_operation_ids) {
        throw std::runtime_error(
            "sync replica reconciliation response metadata-only operation set does not match the exact requester policy");
    }
    std::set<std::string> observed_payload_groups;
    for (std::size_t payload_index = 0U;
         payload_index < response.payloads.size(); ++payload_index) {
        const SyncReplicaReconciliationPayload& payload =
            response.payloads[payload_index];
        const DeltaManifestView complete_manifest =
            delta_manifest_at(payload_index);
        const std::uint64_t bytes = static_cast<std::uint64_t>(
            payload_bytes_at(payload_index).size());
        const bool whole = payload.offset_bytes == 0U &&
                           bytes == payload.total_size_bytes;
        if (whole) {
            observed_payload_groups.insert(payload.content_sha256);
            continue;
        }
        const bool first_range = observed_payload_groups.insert(
            payload.content_sha256).second;
        if (request.cached_delta_manifest_digest.has_value()) {
            if (payload.delta_manifest_digest !=
                    request.cached_delta_manifest_digest ||
                complete_manifest.present()) {
                throw std::runtime_error(
                    "sync replica reconciliation response did not honor the exact cached content-defined manifest reference");
            }
        } else if (first_range) {
            if (!complete_manifest.present()) {
                throw std::runtime_error(
                    "sync replica reconciliation response omitted the complete content-defined manifest from the first range without receiver cache authority");
            }
        } else if (complete_manifest.present()) {
            throw std::runtime_error(
                "sync replica reconciliation response repeated the complete content-defined manifest after the first range");
        }
    }
    if (request.payload_continuation.has_value()) {
        const auto& continuation = *request.payload_continuation;
        const bool terminal_request =
            continuation.next_offset_bytes == continuation.total_size_bytes;
        if (terminal_request) {
            if (response.disposition !=
                    SyncReplicaReconciliationResponseDisposition::Page ||
                response.operations.size() != 1U ||
                !response.payloads.empty() ||
                !response.payload_continuation.has_value() ||
                *response.payload_continuation != continuation ||
                response.next_after_operation_id !=
                    request.after_operation_id ||
                !response.has_more) {
                throw std::runtime_error(
                    "sync replica reconciliation terminal verification continuation did not return one exact payload-cold operation");
            }
            const SyncReplicaOperation& operation = response.operations.front();
            if (operation.operation_id != continuation.operation_id ||
                operation.kind != SyncReplicaValueKind::File ||
                operation.content_sha256 != continuation.content_sha256 ||
                operation.size_bytes != continuation.total_size_bytes) {
                throw std::runtime_error(
                    "sync replica reconciliation terminal verification response does not bind the requested operation");
            }
        } else if (
            response.disposition ==
                SyncReplicaReconciliationResponseDisposition::PayloadUnavailable ||
            response.disposition ==
                SyncReplicaReconciliationResponseDisposition::
                    SourcePayloadPreparing) {
            if (!response.operations.empty() || !response.payloads.empty() ||
                response.blocked_operation_id !=
                    std::optional<std::string>(continuation.operation_id) ||
                response.next_after_operation_id != request.after_operation_id) {
                throw std::runtime_error(
                    "sync replica reconciliation blocked payload continuation does not bind the requested operation");
            }
        } else {
            if (response.disposition !=
                    SyncReplicaReconciliationResponseDisposition::Page ||
                response.operations.size() != 1U ||
                response.payloads.empty()) {
                throw std::runtime_error(
                    "sync replica reconciliation payload continuation did not return one exact operation with a nonempty contiguous range group");
            }
            const SyncReplicaOperation& operation = response.operations.front();
            const SyncReplicaReconciliationPayload& first_payload =
                response.payloads.front();
            const SyncReplicaReconciliationPayload& last_payload =
                response.payloads.back();
            if (operation.operation_id != continuation.operation_id ||
                operation.kind != SyncReplicaValueKind::File ||
                operation.content_sha256 != continuation.content_sha256 ||
                operation.size_bytes != continuation.total_size_bytes ||
                first_payload.content_sha256 != continuation.content_sha256 ||
                first_payload.total_size_bytes != continuation.total_size_bytes ||
                first_payload.offset_bytes != continuation.next_offset_bytes ||
                last_payload.content_sha256 != continuation.content_sha256 ||
                last_payload.total_size_bytes != continuation.total_size_bytes) {
                throw std::runtime_error(
                    "sync replica reconciliation response range group does not continue the exact requested payload");
            }
            const std::uint64_t range_end =
                last_payload.offset_bytes +
                static_cast<std::uint64_t>(
                    payload_bytes_at(response.payloads.size() - 1U).size());
            if (response.payload_continuation.has_value()) {
                if (*response.payload_continuation !=
                        SyncReplicaReconciliationPayloadContinuation{
                            continuation.operation_id,
                            continuation.content_sha256,
                            continuation.total_size_bytes,
                            range_end} ||
                    response.next_after_operation_id !=
                        request.after_operation_id) {
                    throw std::runtime_error(
                        "sync replica reconciliation response payload continuation skipped bytes or operation authority after its range group");
                }
            } else if (range_end != continuation.total_size_bytes ||
                       response.next_after_operation_id !=
                           std::optional<std::string>(
                               continuation.operation_id)) {
                throw std::runtime_error(
                    "sync replica reconciliation final payload range group did not complete its operation cursor");
            }
        }
    } else {
        std::set<std::string> initial_payload_groups;
        for (const SyncReplicaReconciliationPayload& payload :
             response.payloads) {
            if (initial_payload_groups.insert(payload.content_sha256).second &&
                payload.offset_bytes != 0U) {
                throw std::runtime_error(
                    "sync replica reconciliation initial page began a payload group at a nonzero offset");
            }
        }
        std::optional<std::string> expected_next = request.after_operation_id;
        if (response.payload_continuation.has_value()) {
            if (response.operations.size() >= 2U) {
                expected_next =
                    response.operations[response.operations.size() - 2U]
                        .operation_id;
            }
        } else if (!response.operations.empty()) {
            expected_next = response.operations.back().operation_id;
        }
        if (response.next_after_operation_id != expected_next) {
            throw std::runtime_error(
                "sync replica reconciliation response cursor does not continue the request exactly");
        }
    }

    if (request.after_operation_id.has_value()) {
        for (const SyncReplicaOperation& operation : response.operations) {
            if (operation.operation_id <= *request.after_operation_id) {
                throw std::runtime_error(
                    "sync replica reconciliation response did not advance beyond the request cursor");
            }
        }
        if (response.blocked_operation_id.has_value() &&
            *response.blocked_operation_id <= *request.after_operation_id) {
            throw std::runtime_error(
                "sync replica reconciliation blocked operation did not advance beyond the request cursor");
        }
    }
}


}  // namespace

struct SyncReplicaReconciliationResponseFrameAssembly::State final {
    struct PayloadSlot final {
        std::size_t chunk_digest_offset = 0U;
        std::size_t bytes_offset = 0U;
        std::size_t bytes_size = 0U;
        bool committed = false;
    };

    SyncReplicaReconciliationResponse response;
    SyncReplicaReconciliationRequest request;
    SyncReplicaReconciliationProtocolLimits limits;
    std::string frame;
    std::vector<PayloadSlot> payload_slots;
    std::vector<std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest>>
        borrowed_delta_manifests;
    std::size_t body_offset = 0U;
    std::size_t structural_digest_offset = 0U;
    std::uint64_t canonical_body_bytes = 0U;
    std::uint64_t payload_bytes = 0U;
    std::uint64_t borrowed_delta_manifest_count = 0U;
    std::uint64_t borrowed_delta_manifest_chunks = 0U;
};

SyncReplicaReconciliationResponseFrameAssembly::
SyncReplicaReconciliationResponseFrameAssembly(
    std::unique_ptr<State> state) noexcept
    : state_(std::move(state)) {}

SyncReplicaReconciliationResponseFrameAssembly::
SyncReplicaReconciliationResponseFrameAssembly(
    SyncReplicaReconciliationResponseFrameAssembly&&) noexcept = default;

SyncReplicaReconciliationResponseFrameAssembly&
SyncReplicaReconciliationResponseFrameAssembly::operator=(
    SyncReplicaReconciliationResponseFrameAssembly&&) noexcept = default;

SyncReplicaReconciliationResponseFrameAssembly::~
SyncReplicaReconciliationResponseFrameAssembly() noexcept = default;

bool SyncReplicaReconciliationResponseFrameAssembly::active() const noexcept {
    return static_cast<bool>(state_);
}

std::size_t
SyncReplicaReconciliationResponseFrameAssembly::payload_count() const noexcept {
    return state_ ? state_->payload_slots.size() : 0U;
}

SyncReplicaReconciliationResponseFrameAssembly::State&
SyncReplicaReconciliationResponseFrameAssembly::require_state_or_throw(
    std::string_view operation) {
    if (!state_) {
        throw std::logic_error(
            "sync replica reconciliation response frame assembly is inactive during " +
            std::string(operation));
    }
    return *state_;
}

std::span<char>
SyncReplicaReconciliationResponseFrameAssembly::payload_bytes_or_throw(
    std::size_t payload_index) {
    State& state = require_state_or_throw("payload access");
    if (payload_index >= state.payload_slots.size()) {
        throw std::out_of_range(
            "sync replica reconciliation response frame payload index is out of range");
    }
    const State::PayloadSlot& slot = state.payload_slots[payload_index];
    if (slot.committed) {
        throw std::logic_error(
            "sync replica reconciliation response frame payload is already committed");
    }
    if (slot.bytes_offset > state.frame.size() ||
        slot.bytes_size > state.frame.size() - slot.bytes_offset) {
        throw std::logic_error(
            "sync replica reconciliation response frame payload slot escaped its frame");
    }
    return std::span<char>(
        state.frame.data() + slot.bytes_offset, slot.bytes_size);
}

void SyncReplicaReconciliationResponseFrameAssembly::commit_payload_or_throw(
    std::size_t payload_index,
    std::string chunk_sha256) {
    State& state = require_state_or_throw("payload commit");
    if (payload_index >= state.payload_slots.size()) {
        throw std::out_of_range(
            "sync replica reconciliation response frame payload commit index is out of range");
    }
    State::PayloadSlot& slot = state.payload_slots[payload_index];
    if (slot.committed) {
        throw std::logic_error(
            "sync replica reconciliation response frame payload was committed twice");
    }
    if (!is_lowercase_sha256_hex(chunk_sha256)) {
        throw std::invalid_argument(
            "sync replica reconciliation response frame payload digest is not lowercase SHA-256");
    }
    if (slot.chunk_digest_offset > state.frame.size() ||
        kDigestTextBytes > state.frame.size() - slot.chunk_digest_offset) {
        throw std::logic_error(
            "sync replica reconciliation response frame digest slot escaped its frame");
    }
    std::copy(
        chunk_sha256.begin(), chunk_sha256.end(),
        state.frame.begin() +
            static_cast<std::ptrdiff_t>(slot.chunk_digest_offset));
    state.response.payloads[payload_index].chunk_sha256 =
        std::move(chunk_sha256);
    slot.committed = true;
}

SyncReplicaReconciliationDirectFrameResponse
SyncReplicaReconciliationResponseFrameAssembly::finish_or_throw() {
    State& state = require_state_or_throw("finish");
    if (std::any_of(
            state.payload_slots.begin(), state.payload_slots.end(),
            [](const State::PayloadSlot& slot) { return !slot.committed; })) {
        throw std::logic_error(
            "sync replica reconciliation response frame has uncommitted payload slots");
    }
    validate_sync_replica_reconciliation_response_for_request_impl_or_throw(
        state.response, state.request, state.limits,
        [&](std::size_t payload_index) {
            const State::PayloadSlot& slot =
                state.payload_slots[payload_index];
            return std::string_view(
                state.frame.data() + slot.bytes_offset,
                slot.bytes_size);
        }, [&](std::size_t payload_index) {
            return delta_manifest_view_or_none_or_throw(
                state.response.payloads[payload_index],
                borrowed_delta_manifest_at_or_none_or_throw(
                    state.borrowed_delta_manifests, payload_index,
                    "sync replica reconciliation direct frame validation"),
                "sync replica reconciliation direct frame validation");
        });
    if (state.body_offset > state.frame.size() ||
        state.canonical_body_bytes >
            static_cast<std::uint64_t>(state.frame.size() - state.body_offset)) {
        throw std::logic_error(
            "sync replica reconciliation response frame body escaped its allocation");
    }
    const std::string_view body(
        state.frame.data() + state.body_offset,
        u64_to_size_or_throw(
            state.canonical_body_bytes,
            "sync replica reconciliation direct frame body view"));
    const std::string structural_digest = body_digest_or_throw(
        kResponseStructuralDigestDomain, body);
    if (state.structural_digest_offset > state.frame.size() ||
        structural_digest.size() >
            state.frame.size() - state.structural_digest_offset) {
        throw std::logic_error(
            "sync replica reconciliation response frame trailer escaped its allocation");
    }
    std::copy(
        structural_digest.begin(), structural_digest.end(),
        state.frame.begin() +
            static_cast<std::ptrdiff_t>(state.structural_digest_offset));

    SyncReplicaReconciliationDirectFrameResponse out{
        std::move(state.response), std::move(state.frame),
        state.canonical_body_bytes, state.payload_bytes,
        state.borrowed_delta_manifest_count,
        state.borrowed_delta_manifest_chunks};
    state_.reset();
    return out;
}

SyncReplicaReconciliationResponseFrameAssembly
begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
    SyncReplicaReconciliationResponse response_metadata,
    const SyncReplicaReconciliationRequest& request,
    std::vector<std::uint64_t> payload_byte_counts,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    return begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
        std::move(response_metadata), request,
        std::move(payload_byte_counts), {}, limits);
}

SyncReplicaReconciliationResponseFrameAssembly
begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
    SyncReplicaReconciliationResponse response_metadata,
    const SyncReplicaReconciliationRequest& request,
    std::vector<std::uint64_t> payload_byte_counts,
    std::vector<std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest>>
        borrowed_delta_manifests,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_request_or_throw(request, limits);
    if (response_metadata.payloads.size() != payload_byte_counts.size() ||
        (!borrowed_delta_manifests.empty() &&
         response_metadata.payloads.size() !=
             borrowed_delta_manifests.size())) {
        throw std::invalid_argument(
            "sync replica reconciliation response frame payload count does not match its source ranges and borrowed manifests");
    }
    if (payload_byte_counts.size() > limits.max_payloads_per_page) {
        throw std::invalid_argument(
            "sync replica reconciliation response frame exceeds its payload-count limit");
    }
    std::uint64_t payload_bytes = 0U;
    for (std::size_t payload_index = 0U;
         payload_index < response_metadata.payloads.size(); ++payload_index) {
        SyncReplicaReconciliationPayload& payload =
            response_metadata.payloads[payload_index];
        const DeltaManifestView manifest =
            delta_manifest_view_or_none_or_throw(
                payload,
                borrowed_delta_manifest_at_or_none_or_throw(
                    borrowed_delta_manifests, payload_index,
                    "sync replica reconciliation direct frame payload"),
                "sync replica reconciliation direct frame payload");
        if (manifest.present()) {
            validate_delta_manifest_view_or_throw(
                payload.total_size_bytes, manifest,
                "sync replica reconciliation direct frame complete manifest");
        }
        const std::uint64_t byte_count = payload_byte_counts[payload_index];
        if (!payload.bytes.empty() || !payload.chunk_sha256.empty()) {
            throw std::invalid_argument(
                "sync replica reconciliation response frame metadata already owns payload bytes or a committed digest");
        }
        if (byte_count > limits.max_single_payload_bytes ||
            payload.offset_bytes > payload.total_size_bytes ||
            byte_count > payload.total_size_bytes - payload.offset_bytes ||
            (byte_count == 0U &&
             (payload.offset_bytes != 0U || payload.total_size_bytes != 0U))) {
            throw std::invalid_argument(
                "sync replica reconciliation response frame source range is not exact and bounded");
        }
        payload_bytes = checked_add_u64_or_throw(
            payload_bytes, byte_count,
            "sync replica reconciliation direct frame payload bytes");
        if (payload_bytes > limits.max_payload_bytes_per_page) {
            throw std::invalid_argument(
                "sync replica reconciliation response frame exceeds its payload-byte limit");
        }
        payload.chunk_sha256.assign(
            u64_to_size_or_throw(
                kDigestTextBytes,
                "sync replica reconciliation direct frame digest placeholder"),
            '0');
    }

    const ResponseBodyMetrics metrics =
        response_body_metrics_impl_or_throw(
            response_metadata, limits,
            [&](std::size_t payload_index) {
                return payload_byte_counts[payload_index];
            }, [&](std::size_t payload_index) {
                return delta_manifest_view_or_none_or_throw(
                    response_metadata.payloads[payload_index],
                    borrowed_delta_manifest_at_or_none_or_throw(
                        borrowed_delta_manifests, payload_index,
                        "sync replica reconciliation direct frame metrics"),
                    "sync replica reconciliation direct frame metrics");
            });
    if (metrics.payload_bytes != payload_bytes) {
        throw std::logic_error(
            "sync replica reconciliation response frame payload projection drifted");
    }
    const std::uint64_t frame_bytes = checked_add_u64_or_throw(
        fixed_frame_bytes(kResponseMagic), metrics.body_bytes,
        "sync replica reconciliation direct response frame size");
    if (frame_bytes > limits.max_response_frame_bytes) {
        throw std::invalid_argument(
            "sync replica reconciliation direct response exceeds its frame limit");
    }

    auto state = std::make_unique<
        SyncReplicaReconciliationResponseFrameAssembly::State>();
    state->response = std::move(response_metadata);
    state->request = request;
    state->limits = limits;
    state->canonical_body_bytes = metrics.body_bytes;
    state->payload_bytes = metrics.payload_bytes;
    state->payload_slots.resize(payload_byte_counts.size());
    for (const auto& manifest : borrowed_delta_manifests) {
        if (!manifest.has_value()) continue;
        state->borrowed_delta_manifest_count = checked_add_u64_or_throw(
            state->borrowed_delta_manifest_count, 1U,
            "sync replica reconciliation borrowed manifest count");
        state->borrowed_delta_manifest_chunks = checked_add_u64_or_throw(
            state->borrowed_delta_manifest_chunks,
            size_to_u64_or_throw(
                manifest->chunks.size(),
                "sync replica reconciliation borrowed manifest chunks"),
            "sync replica reconciliation borrowed manifest chunk count");
    }
    state->borrowed_delta_manifests =
        std::move(borrowed_delta_manifests);
    state->frame.reserve(u64_to_size_or_throw(
        frame_bytes,
        "sync replica reconciliation direct response exact frame size"));
    state->frame.append(kResponseMagic);
    append_u32(state->frame, kSyncReplicaReconciliationProtocolVersion);
    append_u64(state->frame, metrics.body_bytes);
    state->body_offset = state->frame.size();
    append_response_body_impl_or_throw(
        state->frame, state->response, state->limits,
        [&](std::string& destination,
            const SyncReplicaReconciliationPayload&,
            std::size_t payload_index) {
            auto& slot = state->payload_slots[payload_index];
            append_u64(destination, kDigestTextBytes);
            slot.chunk_digest_offset = destination.size();
            destination.append(
                u64_to_size_or_throw(
                    kDigestTextBytes,
                    "sync replica reconciliation direct frame digest slot"),
                '0');
            append_u64(destination, payload_byte_counts[payload_index]);
            slot.bytes_offset = destination.size();
            slot.bytes_size = u64_to_size_or_throw(
                payload_byte_counts[payload_index],
                "sync replica reconciliation direct frame payload slot");
            destination.resize(destination.size() + slot.bytes_size);
        }, [&](std::size_t payload_index) {
            return delta_manifest_view_or_none_or_throw(
                state->response.payloads[payload_index],
                borrowed_delta_manifest_at_or_none_or_throw(
                    state->borrowed_delta_manifests, payload_index,
                    "sync replica reconciliation direct frame serialization"),
                "sync replica reconciliation direct frame serialization");
        });
    if (state->frame.size() < state->body_offset ||
        size_to_u64_or_throw(
            state->frame.size() - state->body_offset,
            "sync replica reconciliation direct response body size") !=
            metrics.body_bytes) {
        throw std::logic_error(
            "sync replica reconciliation direct response body size projection drifted");
    }
    state->structural_digest_offset = state->frame.size();
    state->frame.append(
        u64_to_size_or_throw(
            kDigestTextBytes,
            "sync replica reconciliation direct frame trailer"),
        '0');
    if (size_to_u64_or_throw(
            state->frame.size(),
            "sync replica reconciliation direct response frame size") !=
        frame_bytes) {
        throw std::logic_error(
            "sync replica reconciliation direct response frame size projection drifted");
    }
    return SyncReplicaReconciliationResponseFrameAssembly(std::move(state));
}

void validate_sync_replica_reconciliation_response_for_request_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_response_for_request_impl_or_throw(
        response, request, limits, [&](std::size_t payload_index) {
            return std::string_view(response.payloads[payload_index].bytes);
        }, [&](std::size_t payload_index) {
            const auto& payload = response.payloads[payload_index];
            return payload.delta_manifest.has_value()
                ? DeltaManifestView::from_owned(
                      payload.total_size_bytes, *payload.delta_manifest)
                : DeltaManifestView{};
        });
}

void validate_sync_replica_reconciliation_borrowed_response_for_request_or_throw(
    const SyncReplicaReconciliationBorrowedResponse& borrowed,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    if (borrowed.response.payloads.size() != borrowed.payload_bytes.size()) {
        throw std::invalid_argument(
            "sync replica reconciliation borrowed response payload cardinality is inconsistent");
    }
    validate_sync_replica_reconciliation_response_for_request_impl_or_throw(
        borrowed.response, request, limits, [&](std::size_t payload_index) {
            return borrowed.payload_bytes[payload_index];
        }, [&](std::size_t payload_index) {
            const auto& payload = borrowed.response.payloads[payload_index];
            return payload.delta_manifest.has_value()
                ? DeltaManifestView::from_owned(
                      payload.total_size_bytes, *payload.delta_manifest)
                : DeltaManifestView{};
        });
}


std::string
encode_sync_replica_reconciliation_response_for_request_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_response_for_request_or_throw(
        response, request, limits);
    return encode_sync_replica_reconciliation_response_after_validation_or_throw(
               response, limits, false)
        .frame;
}

SyncReplicaReconciliationEncodedResponse
encode_sync_replica_reconciliation_response_for_request_with_digest_or_throw(
    const SyncReplicaReconciliationResponse& response,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_sync_replica_reconciliation_response_for_request_or_throw(
        response, request, limits);
    return encode_sync_replica_reconciliation_response_after_validation_or_throw(
        response, limits, true);
}

SyncReplicaReconciliationBorrowedResponse
decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw(
    std::string_view frame,
    const SyncReplicaReconciliationRequest& request,
    const SyncReplicaReconciliationProtocolLimits& limits) {
    validate_protocol_limits_impl_or_throw(limits);
    SyncReplicaReconciliationBorrowedResponse borrowed =
        parse_response_body_borrowing_payloads_without_validation_or_throw(
            extract_body_or_throw(
                frame, kResponseMagic, kResponseStructuralDigestDomain,
                limits.max_response_frame_bytes,
                "sync replica reconciliation response"),
            limits);
    validate_sync_replica_reconciliation_borrowed_response_for_request_or_throw(
        borrowed, request, limits);
    return borrowed;
}

}  // namespace anonsync
