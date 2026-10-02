#pragma once

#include "toxsync/hash.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace toxsync {

enum class Engine : std::uint16_t {
    range_v1 = 1U,
    content_store_v2 = 2U,
};

inline constexpr std::uint32_t kHeadFlagTreepack = 1U << 0U;
inline constexpr std::uint32_t kHeadFlagSnapshot = 1U << 1U;
inline constexpr std::uint32_t kKnownHeadFlags =
    kHeadFlagTreepack | kHeadFlagSnapshot;

// The first 172 bytes are the canonical signing body. Toxsync intentionally
// treats the 64-byte signature as opaque: identity policy and Ed25519/other
// signing backends remain above the transport-neutral library.
struct MutableHead {
    Engine engine{Engine::range_v1};
    std::uint32_t flags{};
    std::uint64_t generation{};
    Digest256 namespace_id{};
    Digest256 artifact{};
    Digest256 index{};
    Digest256 parent{};
    std::uint64_t artifact_size{};
    std::uint64_t index_size{};
    std::uint32_t block_size{};
    std::array<std::byte, 64> signature{};
    friend constexpr bool operator==(const MutableHead&, const MutableHead&) = default;
};

inline constexpr std::size_t kMutableHeadSigningBytes = 172U;
inline constexpr std::size_t kMutableHeadBytes = 236U;
[[nodiscard]] std::array<std::byte, kMutableHeadSigningBytes>
encode_mutable_head_signing(const MutableHead& head);
[[nodiscard]] std::array<std::byte, kMutableHeadBytes>
encode_mutable_head(const MutableHead& head);
[[nodiscard]] MutableHead decode_mutable_head(std::span<const std::byte> bytes);

// HEAD anti-entropy is intentionally tiny and independent of directory or
// object-transfer machinery. A summary advertises only the latest signed HEAD
// identity known for one namespace. A query asks the peer to send its complete
// signed HEAD. Receipts close the exchange without replaying the full record.
// All three messages remain useful over transports other than Tox.
inline constexpr std::uint16_t kHeadSummaryFlagHasHead = 1U << 0U;
inline constexpr std::uint16_t kKnownHeadSummaryFlags =
    kHeadSummaryFlagHasHead;

struct HeadSummary {
    std::uint16_t flags{};
    std::uint64_t generation{};
    Digest256 namespace_id{};
    Digest256 record{};
    friend constexpr bool operator==(const HeadSummary&,
                                     const HeadSummary&) = default;
};

inline constexpr std::size_t kHeadSummaryBytes = 80U;
[[nodiscard]] std::array<std::byte, kHeadSummaryBytes>
encode_head_summary(const HeadSummary& summary);
[[nodiscard]] HeadSummary decode_head_summary(
    std::span<const std::byte> bytes);

inline constexpr std::uint16_t kHeadQueryFlagHasHead = 1U << 0U;
inline constexpr std::uint16_t kKnownHeadQueryFlags = kHeadQueryFlagHasHead;

struct HeadQuery {
    std::uint16_t flags{};
    std::uint64_t generation{};
    Digest256 namespace_id{};
    Digest256 record{};
    friend constexpr bool operator==(const HeadQuery&,
                                     const HeadQuery&) = default;
};

inline constexpr std::size_t kHeadQueryBytes = 80U;
[[nodiscard]] std::array<std::byte, kHeadQueryBytes>
encode_head_query(const HeadQuery& query);
[[nodiscard]] HeadQuery decode_head_query(std::span<const std::byte> bytes);

enum class HeadReceiptStatus : std::uint16_t {
    accepted = 0U,
    duplicate = 1U,
    up_to_date = 2U,
    not_found = 3U,
    untrusted = 4U,
    rejected = 5U,
    unsupported = 6U,
};

struct HeadReceipt {
    HeadReceiptStatus status{HeadReceiptStatus::up_to_date};
    std::uint32_t flags{};
    std::uint64_t generation{};
    Digest256 namespace_id{};
    Digest256 record{};
    friend constexpr bool operator==(const HeadReceipt&,
                                     const HeadReceipt&) = default;
};

inline constexpr std::size_t kHeadReceiptBytes = 84U;
[[nodiscard]] std::array<std::byte, kHeadReceiptBytes>
encode_head_receipt(const HeadReceipt& receipt);
[[nodiscard]] HeadReceipt decode_head_receipt(
    std::span<const std::byte> bytes);

inline constexpr std::uint16_t kRangeRequestFlagAllowFailover = 1U << 0U;
inline constexpr std::uint16_t kRangeRequestFlagPreferParallel = 1U << 1U;
inline constexpr std::uint16_t kRangeRequestFlagVerifyWholeArtifact = 1U << 2U;
inline constexpr std::uint16_t kKnownRangeRequestFlags =
    kRangeRequestFlagAllowFailover | kRangeRequestFlagPreferParallel |
    kRangeRequestFlagVerifyWholeArtifact;

struct RangeRequest {
    std::uint64_t request_id{};
    Digest256 artifact{};
    std::uint64_t offset{};
    std::uint32_t length{};
    std::uint16_t flags{};
    friend constexpr bool operator==(const RangeRequest&, const RangeRequest&) = default;
};

inline constexpr std::size_t kRangeRequestBytes = 64U;
[[nodiscard]] std::array<std::byte, kRangeRequestBytes>
encode_range_request(const RangeRequest& request);
[[nodiscard]] RangeRequest decode_range_request(
    std::span<const std::byte> bytes,
    std::uint32_t max_length = 1U << 20U);

enum class RangeOfferStatus : std::uint16_t {
    accepted = 0U,
    not_found = 1U,
    denied = 2U,
    busy = 3U,
    invalid = 4U,
    internal_error = 5U,
};

struct RangeOffer {
    RangeOfferStatus status{RangeOfferStatus::accepted};
    std::uint16_t flags{};
    std::uint64_t request_id{};
    Digest256 artifact{};
    std::uint64_t offset{};
    std::uint32_t length{};
    std::uint32_t retry_after_ms{};
    std::array<std::byte, 32> file_id{};
    friend constexpr bool operator==(const RangeOffer&, const RangeOffer&) = default;
};

inline constexpr std::size_t kRangeOfferBytes = 104U;
[[nodiscard]] std::array<std::byte, kRangeOfferBytes>
encode_range_offer(const RangeOffer& offer);
[[nodiscard]] RangeOffer decode_range_offer(
    std::span<const std::byte> bytes,
    std::uint32_t max_length = 1U << 20U);

enum class RangeCancelReason : std::uint16_t {
    requester_cancelled = 1U,
    superseded = 2U,
    timeout = 3U,
    shutdown = 4U,
};

struct RangeCancel {
    RangeCancelReason reason{RangeCancelReason::requester_cancelled};
    std::uint32_t flags{};
    std::uint64_t request_id{};
    friend constexpr bool operator==(const RangeCancel&, const RangeCancel&) = default;
};

inline constexpr std::size_t kRangeCancelBytes = 24U;
[[nodiscard]] std::array<std::byte, kRangeCancelBytes>
encode_range_cancel(const RangeCancel& cancel);
[[nodiscard]] RangeCancel decode_range_cancel(std::span<const std::byte> bytes);

enum class RangeResultStatus : std::uint16_t {
    completed = 0U,
    cancelled = 1U,
    verification_failed = 2U,
    io_failed = 3U,
};

struct RangeResult {
    RangeResultStatus status{RangeResultStatus::completed};
    std::uint32_t flags{};
    std::uint64_t request_id{};
    std::uint64_t bytes_received{};
    Digest256 range_digest{};
    friend constexpr bool operator==(const RangeResult&, const RangeResult&) = default;
};

inline constexpr std::size_t kRangeResultBytes = 64U;
[[nodiscard]] std::array<std::byte, kRangeResultBytes>
encode_range_result(const RangeResult& result);
[[nodiscard]] RangeResult decode_range_result(std::span<const std::byte> bytes);

inline constexpr std::uint16_t kCapabilityRangeV1 = 1U << 0U;
inline constexpr std::uint16_t kCapabilityContentStoreV2 = 1U << 1U;
// Compatibility name retained for rev0007 callers.
inline constexpr std::uint16_t kCapabilityContentStoreV2Preview =
    kCapabilityContentStoreV2;
inline constexpr std::uint16_t kCapabilitySparseInventoryV2 = 1U << 2U;
inline constexpr std::uint16_t kCapabilityPagedManifestV2 = 1U << 3U;
inline constexpr std::uint16_t kCapabilityMultiSourceV2 = 1U << 4U;
inline constexpr std::uint16_t kKnownCapabilityFlags =
    kCapabilityRangeV1 | kCapabilityContentStoreV2 |
    kCapabilitySparseInventoryV2 | kCapabilityPagedManifestV2 |
    kCapabilityMultiSourceV2;


inline constexpr std::uint16_t kInventoryRequestFlagVerifyObjects = 1U << 0U;
// Interpret first_chunk/chunk_count as root-manifest page indices rather than
// artifact chunk indices. The fixed wire layout remains unchanged.
inline constexpr std::uint16_t kInventoryRequestFlagManifestPages = 1U << 1U;
inline constexpr std::uint16_t kKnownInventoryRequestFlags =
    kInventoryRequestFlagVerifyObjects | kInventoryRequestFlagManifestPages;
// Responses echo the request's known semantic flags. Older responses with zero
// flags remain valid chunk-inventory pages.
inline constexpr std::uint16_t kKnownInventoryPageFlags =
    kKnownInventoryRequestFlags;
inline constexpr std::uint32_t kInventoryMaximumBits = 4096U;
inline constexpr std::size_t kInventoryBitmapBytes =
    static_cast<std::size_t>(kInventoryMaximumBits / 8U);

struct InventoryRequest {
    std::uint64_t request_id{};
    Digest256 manifest{};
    std::uint64_t first_chunk{};
    std::uint32_t chunk_count{kInventoryMaximumBits};
    std::uint16_t flags{};
    friend constexpr bool operator==(const InventoryRequest&,
                                     const InventoryRequest&) = default;
};

inline constexpr std::size_t kInventoryRequestBytes = 64U;
[[nodiscard]] std::array<std::byte, kInventoryRequestBytes>
encode_inventory_request(const InventoryRequest& request);
[[nodiscard]] InventoryRequest decode_inventory_request(
    std::span<const std::byte> bytes);

enum class InventoryStatus : std::uint16_t {
    available = 0U,
    not_found = 1U,
    busy = 2U,
    invalid = 3U,
    internal_error = 4U,
};

struct InventoryPage {
    InventoryStatus status{InventoryStatus::available};
    std::uint16_t flags{};
    std::uint64_t request_id{};
    Digest256 manifest{};
    std::uint64_t first_chunk{};
    std::uint32_t bit_count{};
    std::uint32_t available_count{};
    std::uint32_t retry_after_ms{};
    std::array<std::byte, kInventoryBitmapBytes> bits{};
    friend constexpr bool operator==(const InventoryPage&,
                                     const InventoryPage&) = default;
};

inline constexpr std::size_t kInventoryPageBytes = 588U;
[[nodiscard]] std::array<std::byte, kInventoryPageBytes>
encode_inventory_page(const InventoryPage& page);
[[nodiscard]] InventoryPage decode_inventory_page(
    std::span<const std::byte> bytes);
[[nodiscard]] bool inventory_bit(const InventoryPage& page,
                                 std::uint32_t local_index) noexcept;
void set_inventory_bit(InventoryPage& page,
                       std::uint32_t local_index,
                       bool available);

struct RangeCapabilities {
    std::uint16_t flags{kCapabilityRangeV1};
    std::uint32_t max_range_length{1U << 20U};
    std::uint16_t max_lanes{1U};
    std::uint16_t max_inflight{4U};
    Engine max_engine{Engine::range_v1};
    std::uint16_t max_index_format{1U};
    std::uint64_t workspace_budget_bytes{8U * 1024U * 1024U};
    friend constexpr bool operator==(const RangeCapabilities&, const RangeCapabilities&) = default;
};

inline constexpr std::size_t kRangeCapabilitiesBytes = 32U;
[[nodiscard]] std::array<std::byte, kRangeCapabilitiesBytes>
encode_range_capabilities(const RangeCapabilities& capabilities);
[[nodiscard]] RangeCapabilities decode_range_capabilities(
    std::span<const std::byte> bytes);

} // namespace toxsync
