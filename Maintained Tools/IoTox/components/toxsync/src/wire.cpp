#include "toxsync/wire.hpp"

#include <algorithm>
#include <bit>
#include <limits>
#include <stdexcept>
#include <type_traits>

namespace toxsync {
namespace {

constexpr std::uint16_t kVersion = 1U;
constexpr std::array<std::byte, 4> kHeadMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'H'}, std::byte{'D'}};
constexpr std::array<std::byte, 4> kHeadSummaryMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'H'}, std::byte{'S'}};
constexpr std::array<std::byte, 4> kHeadQueryMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'H'}, std::byte{'Q'}};
constexpr std::array<std::byte, 4> kHeadReceiptMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'H'}, std::byte{'R'}};
constexpr std::array<std::byte, 4> kRequestMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'R'}, std::byte{'Q'}};
constexpr std::array<std::byte, 4> kOfferMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'R'}, std::byte{'O'}};
constexpr std::array<std::byte, 4> kCancelMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'R'}, std::byte{'C'}};
constexpr std::array<std::byte, 4> kResultMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'R'}, std::byte{'S'}};
constexpr std::array<std::byte, 4> kCapabilitiesMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'C'}, std::byte{'P'}};
constexpr std::array<std::byte, 4> kInventoryRequestMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'I'}, std::byte{'Q'}};
constexpr std::array<std::byte, 4> kInventoryPageMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'I'}, std::byte{'P'}};

template <typename T, std::size_t N>
void write_le(std::array<std::byte, N>& output, std::size_t& offset, T value) {
    static_assert(std::is_unsigned_v<T>);
    if (offset > output.size() || sizeof(T) > output.size() - offset) {
        throw std::logic_error("toxsync wire encoder overflow");
    }
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        output[offset++] = static_cast<std::byte>(value >> (i * 8U));
    }
}

template <typename T>
[[nodiscard]] T read_le(std::span<const std::byte> input, std::size_t& offset) {
    static_assert(std::is_unsigned_v<T>);
    if (offset > input.size() || sizeof(T) > input.size() - offset) {
        throw std::runtime_error("truncated toxsync wire integer");
    }
    std::uint64_t wide{};
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        wide |= static_cast<std::uint64_t>(
                    std::to_integer<unsigned char>(input[offset++]))
                << (i * 8U);
    }
    return static_cast<T>(wide);
}

template <std::size_t N>
void copy_digest(std::array<std::byte, N>& output,
                 std::size_t& offset,
                 const Digest256& digest) {
    if (offset > output.size() || digest.bytes.size() > output.size() - offset) {
        throw std::logic_error("toxsync wire encoder digest overflow");
    }
    std::copy(digest.bytes.begin(), digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += digest.bytes.size();
}

void read_digest(std::span<const std::byte> input,
                 std::size_t& offset,
                 Digest256& digest) {
    if (offset > input.size() || digest.bytes.size() > input.size() - offset) {
        throw std::runtime_error("truncated toxsync wire digest");
    }
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                digest.bytes.size(), digest.bytes.begin());
    offset += digest.bytes.size();
}

[[nodiscard]] bool all_zero(std::span<const std::byte> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(),
                       [](std::byte value) { return value == std::byte{0}; });
}

[[nodiscard]] bool known_engine(Engine engine) noexcept {
    return engine == Engine::range_v1 || engine == Engine::content_store_v2;
}

[[nodiscard]] bool known_offer_status(RangeOfferStatus status) noexcept {
    return status >= RangeOfferStatus::accepted &&
           status <= RangeOfferStatus::internal_error;
}

[[nodiscard]] bool known_cancel_reason(RangeCancelReason reason) noexcept {
    return reason >= RangeCancelReason::requester_cancelled &&
           reason <= RangeCancelReason::shutdown;
}

[[nodiscard]] bool known_result_status(RangeResultStatus status) noexcept {
    return status >= RangeResultStatus::completed &&
           status <= RangeResultStatus::io_failed;
}

[[nodiscard]] bool known_inventory_status(InventoryStatus status) noexcept {
    return status >= InventoryStatus::available &&
           status <= InventoryStatus::internal_error;
}

[[nodiscard]] bool known_head_receipt_status(
    HeadReceiptStatus status) noexcept {
    return status >= HeadReceiptStatus::accepted &&
           status <= HeadReceiptStatus::unsupported;
}

void validate_head_hint(std::uint16_t flags,
                        std::uint16_t known_flags,
                        std::uint16_t has_head_flag,
                        std::uint64_t generation,
                        const Digest256& namespace_id,
                        const Digest256& record,
                        const char* label) {
    if ((flags & ~known_flags) != 0U) {
        throw std::runtime_error(std::string("unknown toxsync ") + label +
                                 " flags");
    }
    if (all_zero(namespace_id.bytes)) {
        throw std::runtime_error(std::string("toxsync ") + label +
                                 " namespace is empty");
    }
    const bool has_head = (flags & has_head_flag) != 0U;
    if (has_head) {
        if (generation == 0U || all_zero(record.bytes)) {
            throw std::runtime_error(std::string("toxsync ") + label +
                                     " head identity is incomplete");
        }
    } else if (generation != 0U || !all_zero(record.bytes)) {
        throw std::runtime_error(std::string("toxsync ") + label +
                                 " empty-head fields are not zero");
    }
}

[[nodiscard]] std::uint32_t bitmap_popcount(
    std::span<const std::byte> bytes) noexcept {
    std::uint32_t result{};
    for (const auto value : bytes) {
        result += static_cast<std::uint32_t>(
            std::popcount(std::to_integer<unsigned char>(value)));
    }
    return result;
}

[[nodiscard]] bool trailing_inventory_bits_zero(
    std::span<const std::byte> bytes, std::uint32_t bit_count) noexcept {
    if (bit_count >= kInventoryMaximumBits) return true;
    const auto full_bytes = static_cast<std::size_t>(bit_count / 8U);
    const auto remainder = static_cast<unsigned>(bit_count % 8U);
    if (remainder != 0U) {
        const auto mask = static_cast<unsigned char>((1U << remainder) - 1U);
        if ((std::to_integer<unsigned char>(bytes[full_bytes]) &
             static_cast<unsigned char>(~mask)) != 0U) {
            return false;
        }
    }
    const auto start = full_bytes + (remainder == 0U ? 0U : 1U);
    return all_zero(bytes.subspan(start));
}

void require_magic(std::span<const std::byte> bytes,
                   std::span<const std::byte> magic,
                   const char* message) {
    if (bytes.size() < magic.size() ||
        !std::equal(magic.begin(), magic.end(), bytes.begin())) {
        throw std::runtime_error(message);
    }
}

void validate_head(const MutableHead& head) {
    if (!known_engine(head.engine)) {
        throw std::runtime_error("unsupported toxsync mutable-head engine");
    }
    if ((head.flags & ~kKnownHeadFlags) != 0U) {
        throw std::runtime_error("toxsync mutable head has unknown flags");
    }
    if (all_zero(head.namespace_id.bytes)) {
        throw std::runtime_error("toxsync mutable head has an empty namespace id");
    }
    if (all_zero(head.artifact.bytes)) {
        throw std::runtime_error("toxsync mutable head has an empty artifact digest");
    }
    if (all_zero(head.index.bytes)) {
        throw std::runtime_error("toxsync mutable head has an empty index/manifest digest");
    }
    if (head.index_size == 0U) {
        throw std::runtime_error("toxsync mutable head has a zero-size index/manifest");
    }
    if (head.engine == Engine::range_v1 && head.block_size == 0U) {
        throw std::runtime_error("toxsync range-v1 head has a zero block size");
    }
    if (head.engine == Engine::content_store_v2 && head.block_size != 0U) {
        throw std::runtime_error("toxsync content-store-v2 head must not carry a v1 block size");
    }
}

} // namespace

std::array<std::byte, kMutableHeadSigningBytes>
encode_mutable_head_signing(const MutableHead& head) {
    validate_head(head);
    std::array<std::byte, kMutableHeadSigningBytes> output{};
    std::copy(kHeadMagic.begin(), kHeadMagic.end(), output.begin());
    std::size_t offset = kHeadMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset, static_cast<std::uint16_t>(head.engine));
    write_le<std::uint32_t>(output, offset, head.flags);
    write_le<std::uint64_t>(output, offset, head.generation);
    copy_digest(output, offset, head.namespace_id);
    copy_digest(output, offset, head.artifact);
    copy_digest(output, offset, head.index);
    copy_digest(output, offset, head.parent);
    write_le<std::uint64_t>(output, offset, head.artifact_size);
    write_le<std::uint64_t>(output, offset, head.index_size);
    write_le<std::uint32_t>(output, offset, head.block_size);
    write_le<std::uint32_t>(output, offset, 0U);
    if (offset != output.size()) {
        throw std::logic_error("toxsync mutable-head signing encoder size mismatch");
    }
    return output;
}

std::array<std::byte, kMutableHeadBytes> encode_mutable_head(const MutableHead& head) {
    const auto signing = encode_mutable_head_signing(head);
    std::array<std::byte, kMutableHeadBytes> output{};
    std::copy(signing.begin(), signing.end(), output.begin());
    std::copy(head.signature.begin(), head.signature.end(),
              output.begin() + static_cast<std::ptrdiff_t>(signing.size()));
    return output;
}

MutableHead decode_mutable_head(std::span<const std::byte> bytes) {
    if (bytes.size() != kMutableHeadBytes) {
        throw std::runtime_error("invalid toxsync mutable-head length");
    }
    require_magic(bytes, kHeadMagic, "invalid toxsync mutable-head magic");
    std::size_t offset = kHeadMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync mutable-head version");
    }
    MutableHead head;
    head.engine = static_cast<Engine>(read_le<std::uint16_t>(bytes, offset));
    head.flags = read_le<std::uint32_t>(bytes, offset);
    head.generation = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, head.namespace_id);
    read_digest(bytes, offset, head.artifact);
    read_digest(bytes, offset, head.index);
    read_digest(bytes, offset, head.parent);
    head.artifact_size = read_le<std::uint64_t>(bytes, offset);
    head.index_size = read_le<std::uint64_t>(bytes, offset);
    head.block_size = read_le<std::uint32_t>(bytes, offset);
    const auto reserved = read_le<std::uint32_t>(bytes, offset);
    if (reserved != 0U) {
        throw std::runtime_error("toxsync mutable head has nonzero reserved bits");
    }
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                head.signature.size(), head.signature.begin());
    offset += head.signature.size();
    if (offset != bytes.size()) {
        throw std::runtime_error("toxsync mutable-head decoder size mismatch");
    }
    validate_head(head);
    return head;
}


std::array<std::byte, kHeadSummaryBytes>
encode_head_summary(const HeadSummary& summary) {
    validate_head_hint(summary.flags, kKnownHeadSummaryFlags,
                       kHeadSummaryFlagHasHead, summary.generation,
                       summary.namespace_id, summary.record, "HEAD summary");
    std::array<std::byte, kHeadSummaryBytes> output{};
    std::copy(kHeadSummaryMagic.begin(), kHeadSummaryMagic.end(), output.begin());
    std::size_t offset = kHeadSummaryMagic.size();
    write_le(output, offset, kVersion);
    write_le(output, offset, summary.flags);
    write_le(output, offset, summary.generation);
    copy_digest(output, offset, summary.namespace_id);
    copy_digest(output, offset, summary.record);
    if (offset != output.size()) {
        throw std::logic_error("toxsync HEAD-summary encoder size mismatch");
    }
    return output;
}

HeadSummary decode_head_summary(std::span<const std::byte> bytes) {
    if (bytes.size() != kHeadSummaryBytes) {
        throw std::runtime_error("invalid toxsync HEAD-summary length");
    }
    require_magic(bytes, kHeadSummaryMagic, "invalid toxsync HEAD-summary magic");
    std::size_t offset = kHeadSummaryMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync HEAD-summary version");
    }
    HeadSummary summary;
    summary.flags = read_le<std::uint16_t>(bytes, offset);
    summary.generation = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, summary.namespace_id);
    read_digest(bytes, offset, summary.record);
    validate_head_hint(summary.flags, kKnownHeadSummaryFlags,
                       kHeadSummaryFlagHasHead, summary.generation,
                       summary.namespace_id, summary.record, "HEAD summary");
    return summary;
}

std::array<std::byte, kHeadQueryBytes>
encode_head_query(const HeadQuery& query) {
    validate_head_hint(query.flags, kKnownHeadQueryFlags,
                       kHeadQueryFlagHasHead, query.generation,
                       query.namespace_id, query.record, "HEAD query");
    std::array<std::byte, kHeadQueryBytes> output{};
    std::copy(kHeadQueryMagic.begin(), kHeadQueryMagic.end(), output.begin());
    std::size_t offset = kHeadQueryMagic.size();
    write_le(output, offset, kVersion);
    write_le(output, offset, query.flags);
    write_le(output, offset, query.generation);
    copy_digest(output, offset, query.namespace_id);
    copy_digest(output, offset, query.record);
    if (offset != output.size()) {
        throw std::logic_error("toxsync HEAD-query encoder size mismatch");
    }
    return output;
}

HeadQuery decode_head_query(std::span<const std::byte> bytes) {
    if (bytes.size() != kHeadQueryBytes) {
        throw std::runtime_error("invalid toxsync HEAD-query length");
    }
    require_magic(bytes, kHeadQueryMagic, "invalid toxsync HEAD-query magic");
    std::size_t offset = kHeadQueryMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync HEAD-query version");
    }
    HeadQuery query;
    query.flags = read_le<std::uint16_t>(bytes, offset);
    query.generation = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, query.namespace_id);
    read_digest(bytes, offset, query.record);
    validate_head_hint(query.flags, kKnownHeadQueryFlags,
                       kHeadQueryFlagHasHead, query.generation,
                       query.namespace_id, query.record, "HEAD query");
    return query;
}

std::array<std::byte, kHeadReceiptBytes>
encode_head_receipt(const HeadReceipt& receipt) {
    if (!known_head_receipt_status(receipt.status)) {
        throw std::runtime_error("unknown toxsync HEAD-receipt status");
    }
    if (receipt.flags != 0U) {
        throw std::runtime_error("unknown toxsync HEAD-receipt flags");
    }
    if (all_zero(receipt.namespace_id.bytes)) {
        throw std::runtime_error("toxsync HEAD-receipt namespace is empty");
    }
    const bool has_identity = receipt.generation != 0U ||
                              !all_zero(receipt.record.bytes);
    if (has_identity &&
        (receipt.generation == 0U || all_zero(receipt.record.bytes))) {
        throw std::runtime_error("toxsync HEAD-receipt identity is incomplete");
    }
    std::array<std::byte, kHeadReceiptBytes> output{};
    std::copy(kHeadReceiptMagic.begin(), kHeadReceiptMagic.end(), output.begin());
    std::size_t offset = kHeadReceiptMagic.size();
    write_le(output, offset, kVersion);
    write_le(output, offset, static_cast<std::uint16_t>(receipt.status));
    write_le(output, offset, receipt.flags);
    write_le(output, offset, receipt.generation);
    copy_digest(output, offset, receipt.namespace_id);
    copy_digest(output, offset, receipt.record);
    if (offset != output.size()) {
        throw std::logic_error("toxsync HEAD-receipt encoder size mismatch");
    }
    return output;
}

HeadReceipt decode_head_receipt(std::span<const std::byte> bytes) {
    if (bytes.size() != kHeadReceiptBytes) {
        throw std::runtime_error("invalid toxsync HEAD-receipt length");
    }
    require_magic(bytes, kHeadReceiptMagic, "invalid toxsync HEAD-receipt magic");
    std::size_t offset = kHeadReceiptMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync HEAD-receipt version");
    }
    HeadReceipt receipt;
    receipt.status = static_cast<HeadReceiptStatus>(
        read_le<std::uint16_t>(bytes, offset));
    receipt.flags = read_le<std::uint32_t>(bytes, offset);
    receipt.generation = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, receipt.namespace_id);
    read_digest(bytes, offset, receipt.record);
    if (!known_head_receipt_status(receipt.status)) {
        throw std::runtime_error("unknown toxsync HEAD-receipt status");
    }
    if (receipt.flags != 0U) {
        throw std::runtime_error("unknown toxsync HEAD-receipt flags");
    }
    if (all_zero(receipt.namespace_id.bytes)) {
        throw std::runtime_error("toxsync HEAD-receipt namespace is empty");
    }
    const bool has_identity = receipt.generation != 0U ||
                              !all_zero(receipt.record.bytes);
    if (has_identity &&
        (receipt.generation == 0U || all_zero(receipt.record.bytes))) {
        throw std::runtime_error("toxsync HEAD-receipt identity is incomplete");
    }
    return receipt;
}

std::array<std::byte, kRangeRequestBytes>
encode_range_request(const RangeRequest& request) {
    if ((request.flags & ~kKnownRangeRequestFlags) != 0U) {
        throw std::invalid_argument("toxsync range request has unknown flags");
    }
    if (request.request_id == 0U || request.length == 0U ||
        request.offset > std::numeric_limits<std::uint64_t>::max() - request.length) {
        throw std::invalid_argument("toxsync range request is empty or overflows");
    }
    if (all_zero(request.artifact.bytes)) {
        throw std::invalid_argument("toxsync range request has an empty artifact digest");
    }

    std::array<std::byte, kRangeRequestBytes> output{};
    std::copy(kRequestMagic.begin(), kRequestMagic.end(), output.begin());
    std::size_t offset = kRequestMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset, request.flags);
    write_le<std::uint64_t>(output, offset, request.request_id);
    copy_digest(output, offset, request.artifact);
    write_le<std::uint64_t>(output, offset, request.offset);
    write_le<std::uint32_t>(output, offset, request.length);
    write_le<std::uint32_t>(output, offset, 0U);
    return output;
}

RangeRequest decode_range_request(std::span<const std::byte> bytes,
                                  std::uint32_t max_length) {
    if (bytes.size() != kRangeRequestBytes) {
        throw std::runtime_error("invalid toxsync range-request length");
    }
    require_magic(bytes, kRequestMagic, "invalid toxsync range-request magic");
    std::size_t offset = kRequestMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync range-request version");
    }
    RangeRequest request;
    request.flags = read_le<std::uint16_t>(bytes, offset);
    request.request_id = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, request.artifact);
    request.offset = read_le<std::uint64_t>(bytes, offset);
    request.length = read_le<std::uint32_t>(bytes, offset);
    const auto reserved = read_le<std::uint32_t>(bytes, offset);
    if (reserved != 0U) {
        throw std::runtime_error("toxsync range request has nonzero reserved bits");
    }
    if ((request.flags & ~kKnownRangeRequestFlags) != 0U) {
        throw std::runtime_error("toxsync range request has unknown flags");
    }
    if (all_zero(request.artifact.bytes)) {
        throw std::runtime_error("toxsync range request has an empty artifact digest");
    }
    if (request.request_id == 0U || request.length == 0U ||
        request.length > max_length) {
        throw std::runtime_error("toxsync range request length exceeds policy");
    }
    if (request.offset > std::numeric_limits<std::uint64_t>::max() - request.length) {
        throw std::runtime_error("toxsync range request overflows artifact address space");
    }
    return request;
}

std::array<std::byte, kRangeOfferBytes> encode_range_offer(const RangeOffer& offer) {
    if (!known_offer_status(offer.status)) {
        throw std::invalid_argument("unknown toxsync range-offer status");
    }
    if (offer.request_id == 0U) {
        throw std::invalid_argument("toxsync range offer has a zero request id");
    }
    if (offer.status == RangeOfferStatus::accepted) {
        if (offer.length == 0U ||
            offer.offset > std::numeric_limits<std::uint64_t>::max() - offer.length ||
            all_zero(offer.artifact.bytes) || all_zero(offer.file_id)) {
            throw std::invalid_argument("accepted toxsync range offer is incomplete");
        }
    } else if (offer.length != 0U || !all_zero(offer.file_id)) {
        throw std::invalid_argument("rejected toxsync range offer carries transfer data");
    }

    std::array<std::byte, kRangeOfferBytes> output{};
    std::copy(kOfferMagic.begin(), kOfferMagic.end(), output.begin());
    std::size_t offset = kOfferMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset, static_cast<std::uint16_t>(offer.status));
    write_le<std::uint16_t>(output, offset, offer.flags);
    write_le<std::uint16_t>(output, offset, 0U);
    write_le<std::uint64_t>(output, offset, offer.request_id);
    copy_digest(output, offset, offer.artifact);
    write_le<std::uint64_t>(output, offset, offer.offset);
    write_le<std::uint32_t>(output, offset, offer.length);
    write_le<std::uint32_t>(output, offset, offer.retry_after_ms);
    std::copy(offer.file_id.begin(), offer.file_id.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += offer.file_id.size();
    write_le<std::uint32_t>(output, offset, 0U);
    return output;
}

RangeOffer decode_range_offer(std::span<const std::byte> bytes,
                              std::uint32_t max_length) {
    if (bytes.size() != kRangeOfferBytes) {
        throw std::runtime_error("invalid toxsync range-offer length");
    }
    require_magic(bytes, kOfferMagic, "invalid toxsync range-offer magic");
    std::size_t offset = kOfferMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync range-offer version");
    }
    RangeOffer offer;
    offer.status = static_cast<RangeOfferStatus>(read_le<std::uint16_t>(bytes, offset));
    offer.flags = read_le<std::uint16_t>(bytes, offset);
    const auto reserved = read_le<std::uint16_t>(bytes, offset);
    if (reserved != 0U) {
        throw std::runtime_error("toxsync range offer has nonzero reserved bits");
    }
    offer.request_id = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, offer.artifact);
    offer.offset = read_le<std::uint64_t>(bytes, offset);
    offer.length = read_le<std::uint32_t>(bytes, offset);
    offer.retry_after_ms = read_le<std::uint32_t>(bytes, offset);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                offer.file_id.size(), offer.file_id.begin());
    offset += offer.file_id.size();
    const auto reserved2 = read_le<std::uint32_t>(bytes, offset);
    if (reserved2 != 0U || !known_offer_status(offer.status)) {
        throw std::runtime_error("invalid toxsync range-offer status or reserved bits");
    }
    if (offer.request_id == 0U) {
        throw std::runtime_error("toxsync range offer has a zero request id");
    }
    if (offer.status == RangeOfferStatus::accepted) {
        if (offer.length == 0U || offer.length > max_length ||
            offer.offset > std::numeric_limits<std::uint64_t>::max() - offer.length ||
            all_zero(offer.artifact.bytes) || all_zero(offer.file_id)) {
            throw std::runtime_error("accepted toxsync range offer violates policy");
        }
    } else if (offer.length != 0U || !all_zero(offer.file_id)) {
        throw std::runtime_error("rejected toxsync range offer carries transfer data");
    }
    return offer;
}

std::array<std::byte, kRangeCancelBytes>
encode_range_cancel(const RangeCancel& cancel) {
    if (!known_cancel_reason(cancel.reason) || cancel.request_id == 0U) {
        throw std::invalid_argument("invalid toxsync range-cancel reason or request id");
    }
    std::array<std::byte, kRangeCancelBytes> output{};
    std::copy(kCancelMagic.begin(), kCancelMagic.end(), output.begin());
    std::size_t offset = kCancelMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset, static_cast<std::uint16_t>(cancel.reason));
    write_le<std::uint64_t>(output, offset, cancel.request_id);
    write_le<std::uint32_t>(output, offset, cancel.flags);
    write_le<std::uint32_t>(output, offset, 0U);
    return output;
}

RangeCancel decode_range_cancel(std::span<const std::byte> bytes) {
    if (bytes.size() != kRangeCancelBytes) {
        throw std::runtime_error("invalid toxsync range-cancel length");
    }
    require_magic(bytes, kCancelMagic, "invalid toxsync range-cancel magic");
    std::size_t offset = kCancelMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync range-cancel version");
    }
    RangeCancel cancel;
    cancel.reason = static_cast<RangeCancelReason>(read_le<std::uint16_t>(bytes, offset));
    cancel.request_id = read_le<std::uint64_t>(bytes, offset);
    cancel.flags = read_le<std::uint32_t>(bytes, offset);
    const auto reserved = read_le<std::uint32_t>(bytes, offset);
    if (reserved != 0U || !known_cancel_reason(cancel.reason) ||
        cancel.request_id == 0U) {
        throw std::runtime_error("invalid toxsync range-cancel reason or reserved bits");
    }
    return cancel;
}

std::array<std::byte, kRangeResultBytes>
encode_range_result(const RangeResult& result) {
    if (!known_result_status(result.status) || result.request_id == 0U) {
        throw std::invalid_argument("invalid toxsync range-result status or request id");
    }
    if (result.status == RangeResultStatus::completed &&
        all_zero(result.range_digest.bytes)) {
        throw std::invalid_argument("completed toxsync range result lacks a digest");
    }
    std::array<std::byte, kRangeResultBytes> output{};
    std::copy(kResultMagic.begin(), kResultMagic.end(), output.begin());
    std::size_t offset = kResultMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset, static_cast<std::uint16_t>(result.status));
    write_le<std::uint64_t>(output, offset, result.request_id);
    write_le<std::uint64_t>(output, offset, result.bytes_received);
    copy_digest(output, offset, result.range_digest);
    write_le<std::uint32_t>(output, offset, result.flags);
    write_le<std::uint32_t>(output, offset, 0U);
    return output;
}

RangeResult decode_range_result(std::span<const std::byte> bytes) {
    if (bytes.size() != kRangeResultBytes) {
        throw std::runtime_error("invalid toxsync range-result length");
    }
    require_magic(bytes, kResultMagic, "invalid toxsync range-result magic");
    std::size_t offset = kResultMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync range-result version");
    }
    RangeResult result;
    result.status = static_cast<RangeResultStatus>(read_le<std::uint16_t>(bytes, offset));
    result.request_id = read_le<std::uint64_t>(bytes, offset);
    result.bytes_received = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, result.range_digest);
    result.flags = read_le<std::uint32_t>(bytes, offset);
    const auto reserved = read_le<std::uint32_t>(bytes, offset);
    if (reserved != 0U || !known_result_status(result.status) ||
        result.request_id == 0U) {
        throw std::runtime_error("invalid toxsync range-result status or reserved bits");
    }
    if (result.status == RangeResultStatus::completed &&
        all_zero(result.range_digest.bytes)) {
        throw std::runtime_error("completed toxsync range result lacks a digest");
    }
    return result;
}

std::array<std::byte, kInventoryRequestBytes>
encode_inventory_request(const InventoryRequest& request) {
    if (request.request_id == 0U || all_zero(request.manifest.bytes) ||
        request.chunk_count == 0U ||
        request.chunk_count > kInventoryMaximumBits ||
        (request.flags & ~kKnownInventoryRequestFlags) != 0U ||
        request.first_chunk > std::numeric_limits<std::uint64_t>::max() -
                                  request.chunk_count) {
        throw std::invalid_argument("invalid toxsync inventory request");
    }
    std::array<std::byte, kInventoryRequestBytes> output{};
    std::copy(kInventoryRequestMagic.begin(), kInventoryRequestMagic.end(),
              output.begin());
    std::size_t offset = kInventoryRequestMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset, request.flags);
    write_le<std::uint64_t>(output, offset, request.request_id);
    copy_digest(output, offset, request.manifest);
    write_le<std::uint64_t>(output, offset, request.first_chunk);
    write_le<std::uint32_t>(output, offset, request.chunk_count);
    write_le<std::uint32_t>(output, offset, 0U);
    return output;
}

InventoryRequest decode_inventory_request(std::span<const std::byte> bytes) {
    if (bytes.size() != kInventoryRequestBytes) {
        throw std::runtime_error("invalid toxsync inventory-request length");
    }
    require_magic(bytes, kInventoryRequestMagic,
                  "invalid toxsync inventory-request magic");
    std::size_t offset = kInventoryRequestMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync inventory-request version");
    }
    InventoryRequest request;
    request.flags = read_le<std::uint16_t>(bytes, offset);
    request.request_id = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, request.manifest);
    request.first_chunk = read_le<std::uint64_t>(bytes, offset);
    request.chunk_count = read_le<std::uint32_t>(bytes, offset);
    const auto reserved = read_le<std::uint32_t>(bytes, offset);
    if (reserved != 0U || request.request_id == 0U ||
        all_zero(request.manifest.bytes) || request.chunk_count == 0U ||
        request.chunk_count > kInventoryMaximumBits ||
        (request.flags & ~kKnownInventoryRequestFlags) != 0U ||
        request.first_chunk > std::numeric_limits<std::uint64_t>::max() -
                                  request.chunk_count) {
        throw std::runtime_error("invalid toxsync inventory request");
    }
    return request;
}

std::array<std::byte, kInventoryPageBytes>
encode_inventory_page(const InventoryPage& page) {
    if (!known_inventory_status(page.status) || page.request_id == 0U ||
        all_zero(page.manifest.bytes) ||
        (page.flags & ~kKnownInventoryPageFlags) != 0U) {
        throw std::invalid_argument("invalid toxsync inventory page identity");
    }
    if (page.status == InventoryStatus::available) {
        if (page.bit_count == 0U || page.bit_count > kInventoryMaximumBits ||
            page.first_chunk > std::numeric_limits<std::uint64_t>::max() -
                                   page.bit_count ||
            !trailing_inventory_bits_zero(page.bits, page.bit_count) ||
            bitmap_popcount(page.bits) != page.available_count) {
            throw std::invalid_argument("invalid toxsync inventory page bitmap");
        }
    } else if (page.bit_count != 0U || page.available_count != 0U ||
               !all_zero(page.bits)) {
        throw std::invalid_argument(
            "rejected toxsync inventory page carries availability bits");
    }

    std::array<std::byte, kInventoryPageBytes> output{};
    std::copy(kInventoryPageMagic.begin(), kInventoryPageMagic.end(),
              output.begin());
    std::size_t offset = kInventoryPageMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset,
                            static_cast<std::uint16_t>(page.status));
    write_le<std::uint16_t>(output, offset, page.flags);
    write_le<std::uint16_t>(output, offset, 0U);
    write_le<std::uint64_t>(output, offset, page.request_id);
    copy_digest(output, offset, page.manifest);
    write_le<std::uint64_t>(output, offset, page.first_chunk);
    write_le<std::uint32_t>(output, offset, page.bit_count);
    write_le<std::uint32_t>(output, offset, page.available_count);
    write_le<std::uint32_t>(output, offset, page.retry_after_ms);
    write_le<std::uint32_t>(output, offset, 0U);
    std::copy(page.bits.begin(), page.bits.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += page.bits.size();
    if (offset != output.size()) {
        throw std::logic_error("toxsync inventory-page encoder size mismatch");
    }
    return output;
}

InventoryPage decode_inventory_page(std::span<const std::byte> bytes) {
    if (bytes.size() != kInventoryPageBytes) {
        throw std::runtime_error("invalid toxsync inventory-page length");
    }
    require_magic(bytes, kInventoryPageMagic,
                  "invalid toxsync inventory-page magic");
    std::size_t offset = kInventoryPageMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync inventory-page version");
    }
    InventoryPage page;
    page.status = static_cast<InventoryStatus>(
        read_le<std::uint16_t>(bytes, offset));
    page.flags = read_le<std::uint16_t>(bytes, offset);
    const auto reserved = read_le<std::uint16_t>(bytes, offset);
    page.request_id = read_le<std::uint64_t>(bytes, offset);
    read_digest(bytes, offset, page.manifest);
    page.first_chunk = read_le<std::uint64_t>(bytes, offset);
    page.bit_count = read_le<std::uint32_t>(bytes, offset);
    page.available_count = read_le<std::uint32_t>(bytes, offset);
    page.retry_after_ms = read_le<std::uint32_t>(bytes, offset);
    const auto reserved2 = read_le<std::uint32_t>(bytes, offset);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                page.bits.size(), page.bits.begin());
    offset += page.bits.size();
    if (offset != bytes.size() || reserved != 0U || reserved2 != 0U ||
        !known_inventory_status(page.status) || page.request_id == 0U ||
        all_zero(page.manifest.bytes) ||
        (page.flags & ~kKnownInventoryPageFlags) != 0U) {
        throw std::runtime_error("invalid toxsync inventory page header");
    }
    if (page.status == InventoryStatus::available) {
        if (page.bit_count == 0U || page.bit_count > kInventoryMaximumBits ||
            page.first_chunk > std::numeric_limits<std::uint64_t>::max() -
                                   page.bit_count ||
            !trailing_inventory_bits_zero(page.bits, page.bit_count) ||
            bitmap_popcount(page.bits) != page.available_count) {
            throw std::runtime_error("invalid toxsync inventory page bitmap");
        }
    } else if (page.bit_count != 0U || page.available_count != 0U ||
               !all_zero(page.bits)) {
        throw std::runtime_error(
            "rejected toxsync inventory page carries availability bits");
    }
    return page;
}

bool inventory_bit(const InventoryPage& page,
                   std::uint32_t local_index) noexcept {
    if (local_index >= page.bit_count) return false;
    const auto byte_index = static_cast<std::size_t>(local_index / 8U);
    const auto bit_index = static_cast<unsigned>(local_index % 8U);
    return (std::to_integer<unsigned char>(page.bits[byte_index]) &
            static_cast<unsigned char>(1U << bit_index)) != 0U;
}

void set_inventory_bit(InventoryPage& page,
                       std::uint32_t local_index,
                       bool available) {
    if (local_index >= kInventoryMaximumBits) {
        throw std::out_of_range("toxsync inventory bit index exceeds page capacity");
    }
    const auto byte_index = static_cast<std::size_t>(local_index / 8U);
    const auto bit_index = static_cast<unsigned>(local_index % 8U);
    const auto mask = static_cast<unsigned char>(1U << bit_index);
    auto value = std::to_integer<unsigned char>(page.bits[byte_index]);
    const bool previous = (value & mask) != 0U;
    if (available) {
        value = static_cast<unsigned char>(value | mask);
    } else {
        value = static_cast<unsigned char>(value & static_cast<unsigned char>(~mask));
    }
    page.bits[byte_index] = static_cast<std::byte>(value);
    if (available && !previous) ++page.available_count;
    if (!available && previous && page.available_count != 0U) --page.available_count;
    page.bit_count = std::max(page.bit_count, local_index + 1U);
}

std::array<std::byte, kRangeCapabilitiesBytes>
encode_range_capabilities(const RangeCapabilities& capabilities) {
    const bool engine_flags_match =
        capabilities.max_engine == Engine::range_v1
            ? (capabilities.flags & kCapabilityRangeV1) != 0U
            : (capabilities.flags & (kCapabilityRangeV1 |
                                      kCapabilityContentStoreV2)) ==
                  (kCapabilityRangeV1 | kCapabilityContentStoreV2);
    const bool v2_dependencies_match =
        (capabilities.flags & (kCapabilitySparseInventoryV2 |
                               kCapabilityPagedManifestV2 |
                               kCapabilityMultiSourceV2)) == 0U ||
        (capabilities.flags & kCapabilityContentStoreV2) != 0U;
    if ((capabilities.flags & ~kKnownCapabilityFlags) != 0U ||
        capabilities.flags == 0U || capabilities.max_range_length == 0U ||
        capabilities.max_lanes == 0U ||
        capabilities.max_inflight == 0U || !known_engine(capabilities.max_engine) ||
        !engine_flags_match || !v2_dependencies_match ||
        capabilities.max_index_format == 0U ||
        capabilities.workspace_budget_bytes == 0U) {
        throw std::invalid_argument("invalid toxsync range capabilities");
    }
    std::array<std::byte, kRangeCapabilitiesBytes> output{};
    std::copy(kCapabilitiesMagic.begin(), kCapabilitiesMagic.end(), output.begin());
    std::size_t offset = kCapabilitiesMagic.size();
    write_le<std::uint16_t>(output, offset, kVersion);
    write_le<std::uint16_t>(output, offset, capabilities.flags);
    write_le<std::uint32_t>(output, offset, capabilities.max_range_length);
    write_le<std::uint16_t>(output, offset, capabilities.max_lanes);
    write_le<std::uint16_t>(output, offset, capabilities.max_inflight);
    write_le<std::uint16_t>(output, offset,
                            static_cast<std::uint16_t>(capabilities.max_engine));
    write_le<std::uint16_t>(output, offset, capabilities.max_index_format);
    write_le<std::uint64_t>(output, offset, capabilities.workspace_budget_bytes);
    write_le<std::uint32_t>(output, offset, 0U);
    return output;
}

RangeCapabilities decode_range_capabilities(std::span<const std::byte> bytes) {
    if (bytes.size() != kRangeCapabilitiesBytes) {
        throw std::runtime_error("invalid toxsync capabilities length");
    }
    require_magic(bytes, kCapabilitiesMagic, "invalid toxsync capabilities magic");
    std::size_t offset = kCapabilitiesMagic.size();
    if (read_le<std::uint16_t>(bytes, offset) != kVersion) {
        throw std::runtime_error("unsupported toxsync capabilities version");
    }
    RangeCapabilities capabilities;
    capabilities.flags = read_le<std::uint16_t>(bytes, offset);
    capabilities.max_range_length = read_le<std::uint32_t>(bytes, offset);
    capabilities.max_lanes = read_le<std::uint16_t>(bytes, offset);
    capabilities.max_inflight = read_le<std::uint16_t>(bytes, offset);
    capabilities.max_engine = static_cast<Engine>(read_le<std::uint16_t>(bytes, offset));
    capabilities.max_index_format = read_le<std::uint16_t>(bytes, offset);
    capabilities.workspace_budget_bytes = read_le<std::uint64_t>(bytes, offset);
    const auto reserved = read_le<std::uint32_t>(bytes, offset);
    const bool engine_flags_match =
        capabilities.max_engine == Engine::range_v1
            ? (capabilities.flags & kCapabilityRangeV1) != 0U
            : (capabilities.flags & (kCapabilityRangeV1 |
                                      kCapabilityContentStoreV2)) ==
                  (kCapabilityRangeV1 | kCapabilityContentStoreV2);
    const bool v2_dependencies_match =
        (capabilities.flags & (kCapabilitySparseInventoryV2 |
                               kCapabilityPagedManifestV2 |
                               kCapabilityMultiSourceV2)) == 0U ||
        (capabilities.flags & kCapabilityContentStoreV2) != 0U;
    if (reserved != 0U || (capabilities.flags & ~kKnownCapabilityFlags) != 0U ||
        capabilities.flags == 0U || capabilities.max_range_length == 0U ||
        capabilities.max_lanes == 0U ||
        capabilities.max_inflight == 0U || !known_engine(capabilities.max_engine) ||
        !engine_flags_match || !v2_dependencies_match ||
        capabilities.max_index_format == 0U ||
        capabilities.workspace_budget_bytes == 0U) {
        throw std::runtime_error("invalid toxsync range capabilities");
    }
    return capabilities;
}

} // namespace toxsync
