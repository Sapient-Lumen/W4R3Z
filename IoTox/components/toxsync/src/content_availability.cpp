#include "toxsync/content_availability.hpp"

#include "toxsync/hash.hpp"

#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstring>
#include <fstream>
#include <limits>
#include <stdexcept>
#include <type_traits>

namespace toxsync {
namespace {

constexpr std::array<std::byte, 8> kAvailabilityMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'A'}, std::byte{'V'},
    std::byte{'A'}, std::byte{'I'}, std::byte{'L'}, std::byte{'1'},
};
constexpr std::size_t kMinimumFilterBytes = 64U;
constexpr std::size_t kMaximumHashFunctions = 16U;

[[nodiscard]] bool all_zero(std::span<const std::byte> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::byte value) {
        return value == std::byte{0};
    });
}

template <typename T>
void store_le(std::byte* output, T value) noexcept {
    static_assert(std::is_unsigned_v<T>);
    for (std::size_t index = 0U; index < sizeof(T); ++index) {
        output[index] = static_cast<std::byte>(value >> (index * 8U));
    }
}

template <typename T>
[[nodiscard]] T load_le(const std::byte* input) noexcept {
    static_assert(std::is_unsigned_v<T>);
    std::uint64_t value{};
    for (std::size_t index = 0U; index < sizeof(T); ++index) {
        value |= static_cast<std::uint64_t>(
                     std::to_integer<unsigned>(input[index]))
                 << (index * 8U);
    }
    return static_cast<T>(value);
}

void validate_config(const ContentAvailabilityConfig& config) {
    if (config.filter_bytes < kMinimumFilterBytes ||
        !std::has_single_bit(config.filter_bytes)) {
        throw std::invalid_argument(
            "content availability filter size must be a power of two of at least 64 bytes");
    }
    if (config.filter_bytes >
        static_cast<std::size_t>(std::numeric_limits<std::uint32_t>::max() / 8U)) {
        throw std::invalid_argument("content availability filter is too large");
    }
    if (config.hash_functions == 0U ||
        config.hash_functions > kMaximumHashFunctions) {
        throw std::invalid_argument(
            "content availability hash-function count must be between 1 and 16");
    }
}

[[nodiscard]] bool regular_file_exact_size(const std::filesystem::path& path,
                                            std::uint64_t expected) noexcept {
    std::error_code error;
    const auto status = std::filesystem::symlink_status(path, error);
    if (error || !std::filesystem::is_regular_file(status) ||
        std::filesystem::is_symlink(status)) {
        return false;
    }
    const auto size = std::filesystem::file_size(path, error);
    return !error && size == expected;
}

[[nodiscard]] bool verify_file(const std::filesystem::path& path,
                               const Digest256& expected,
                               std::span<std::byte> buffer) {
    std::ifstream input(path, std::ios::binary);
    if (!input) return false;
    Sha256 hasher;
    for (;;) {
        input.read(reinterpret_cast<char*>(buffer.data()),
                   static_cast<std::streamsize>(buffer.size()));
        const auto count = input.gcount();
        if (count < 0) return false;
        if (count != 0) {
            hasher.update(std::span<const std::byte>(
                buffer.data(), static_cast<std::size_t>(count)));
        }
        if (input.eof()) break;
        if (!input) return false;
    }
    return hasher.finish() == expected;
}

struct BuildContext {
    ContentAvailabilityBuildResult* result{};
    const std::filesystem::path* store_root{};
    const ContentAvailabilityBuildOptions* options{};
    std::span<std::byte> verification_buffer{};
};

void visit_chunk(void* opaque, const ContentChunkRef& chunk) {
    auto& context = *static_cast<BuildContext*>(opaque);
    auto& result = *context.result;
    const auto path = content_store_path(*context.store_root, chunk.digest);
    bool available = regular_file_exact_size(path, chunk.length);
    bool corrupt = false;
    if (available && context.options->verify_chunk_digests) {
        available = verify_file(path, chunk.digest,
                                context.verification_buffer);
        corrupt = !available;
    }
    if (available) {
        result.sketch.add(chunk.digest, chunk.length);
        ++result.available_chunks;
        result.available_bytes += chunk.length;
    } else {
        ++result.missing_chunks;
        result.missing_bytes += chunk.length;
        if (corrupt) ++result.corrupt_chunks;
    }
}

} // namespace

ContentAvailabilitySketch::ContentAvailabilitySketch(
    const ContentAvailabilityConfig& config)
    : hash_functions_(config.hash_functions), salt_(config.salt) {
    validate_config(config);
    bits_.resize(config.filter_bytes, std::byte{0});
}

ContentAvailabilitySketch::ContentAvailabilitySketch(
    ContentAvailabilityMetadata metadata, std::vector<std::byte> bits)
    : manifest_(metadata.manifest),
      sequence_(metadata.sequence),
      item_count_(metadata.item_count),
      available_bytes_(metadata.available_bytes),
      flags_(metadata.flags),
      hash_functions_(metadata.hash_functions),
      salt_(metadata.salt),
      bits_(std::move(bits)) {}

void ContentAvailabilitySketch::reset(const Digest256& manifest,
                                      std::uint64_t sequence,
                                      std::uint16_t flags) {
    if (all_zero(manifest.bytes)) {
        throw std::invalid_argument(
            "content availability requires a nonzero manifest digest");
    }
    if ((flags & ~kKnownAvailabilityFlags) != 0U) {
        throw std::invalid_argument("content availability has unknown flags");
    }
    manifest_ = manifest;
    sequence_ = sequence;
    item_count_ = 0U;
    available_bytes_ = 0U;
    flags_ = flags;
    clear_bits();
}

void ContentAvailabilitySketch::clear_bits() noexcept {
    std::fill(bits_.begin(), bits_.end(), std::byte{0});
    item_count_ = 0U;
    available_bytes_ = 0U;
}

void ContentAvailabilitySketch::set_flags(std::uint16_t flags) {
    if ((flags & ~kKnownAvailabilityFlags) != 0U) {
        throw std::invalid_argument("content availability has unknown flags");
    }
    flags_ = flags;
}

std::pair<std::uint64_t, std::uint64_t>
ContentAvailabilitySketch::hash_pair(const Digest256& chunk) const noexcept {
    std::array<std::byte, 40> input{};
    std::copy(chunk.bytes.begin(), chunk.bytes.end(), input.begin());
    store_le<std::uint64_t>(input.data() + 32U, salt_);
    const auto hash = fast_hash128(input);
    // An odd second step visits every position in a power-of-two filter.
    return {hash.lo, hash.hi | 1ULL};
}

void ContentAvailabilitySketch::add(const Digest256& chunk,
                                    std::uint64_t chunk_bytes) noexcept {
    const auto [first, step] = hash_pair(chunk);
    const auto bit_count = static_cast<std::uint64_t>(bits_.size() * 8U);
    const auto mask = bit_count - 1U;
    for (std::uint8_t index = 0U; index < hash_functions_; ++index) {
        const auto position =
            (first + static_cast<std::uint64_t>(index) * step) & mask;
        const auto byte_index = static_cast<std::size_t>(position >> 3U);
        const auto bit = static_cast<unsigned>(position & 7U);
        bits_[byte_index] |= static_cast<std::byte>(1U << bit);
    }
    ++item_count_;
    if (available_bytes_ <=
        std::numeric_limits<std::uint64_t>::max() - chunk_bytes) {
        available_bytes_ += chunk_bytes;
    } else {
        available_bytes_ = std::numeric_limits<std::uint64_t>::max();
    }
}

bool ContentAvailabilitySketch::possibly_contains(
    const Digest256& chunk) const noexcept {
    const auto [first, step] = hash_pair(chunk);
    const auto bit_count = static_cast<std::uint64_t>(bits_.size() * 8U);
    const auto mask = bit_count - 1U;
    for (std::uint8_t index = 0U; index < hash_functions_; ++index) {
        const auto position =
            (first + static_cast<std::uint64_t>(index) * step) & mask;
        const auto byte_index = static_cast<std::size_t>(position >> 3U);
        const auto bit = static_cast<unsigned>(position & 7U);
        if ((std::to_integer<unsigned>(bits_[byte_index]) & (1U << bit)) == 0U) {
            return false;
        }
    }
    return true;
}

ContentAvailabilityMetadata ContentAvailabilitySketch::metadata() const {
    ContentAvailabilityMetadata result;
    result.manifest = manifest_;
    result.sequence = sequence_;
    result.item_count = item_count_;
    result.available_bytes = available_bytes_;
    result.bit_count = static_cast<std::uint32_t>(bits_.size() * 8U);
    result.hash_functions = hash_functions_;
    result.flags = flags_;
    result.salt = salt_;
    result.filter_digest = sha256(bits_);
    return result;
}

double ContentAvailabilitySketch::estimated_false_positive_rate() const noexcept {
    if (item_count_ == 0U) return 0.0;
    const auto bits = static_cast<double>(bits_.size() * 8U);
    const auto hashes = static_cast<double>(hash_functions_);
    const auto items = static_cast<double>(item_count_);
    const auto occupied = 1.0 - std::exp(-(hashes * items) / bits);
    return std::pow(occupied, hashes);
}

ContentAvailabilityBuildResult build_content_availability(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t sequence,
    const ContentAvailabilityBuildOptions& options) {
    ContentStoreWorkspace workspace;
    return build_content_availability(manifest_path, store_root, workspace,
                                      sequence, options);
}

ContentAvailabilityBuildResult build_content_availability(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    std::uint64_t sequence,
    const ContentAvailabilityBuildOptions& options) {
    ContentAvailabilityBuildResult result{
        .sketch = ContentAvailabilitySketch(options.sketch),
    };
    // First validate and identify the complete manifest. The second streamed
    // pass builds availability without retaining an entry vector. This costs
    // metadata I/O but keeps the sketch's manifest identity authoritative.
    result.manifest = inspect_content_manifest(manifest_path, workspace,
                                               options.limits);
    std::uint16_t flags = options.verify_chunk_digests
        ? kAvailabilityFlagDigestVerified
        : 0U;
    result.sketch.reset(result.manifest.manifest_digest, sequence, flags);

    std::vector<std::byte> verification_buffer;
    if (options.verify_chunk_digests) {
        verification_buffer.resize(
            std::max<std::size_t>(4096U, options.io_buffer_bytes));
    }
    result.verification_buffer_bytes = verification_buffer.capacity();
    BuildContext context{.result = &result,
                         .store_root = &store_root,
                         .options = &options,
                         .verification_buffer = std::span<std::byte>(verification_buffer)};
    ContentManifestWalkOptions walk_options;
    walk_options.manifest_buffer_bytes = options.manifest_buffer_bytes;
    walk_options.limits = options.limits;
    const auto walked = walk_content_manifest(
        manifest_path, workspace, &visit_chunk, &context, walk_options);
    result.manifest = walked.metadata;
    result.workspace_reserved_bytes = walked.workspace_reserved_bytes;
    result.workspace_growth_events = walked.workspace_growth_events;
    if (result.missing_chunks == 0U) {
        flags = static_cast<std::uint16_t>(flags | kAvailabilityFlagComplete);
    }
    result.sketch.set_flags(flags);
    return result;
}

std::vector<std::byte> encode_content_availability(
    const ContentAvailabilitySketch& sketch) {
    const auto metadata = sketch.metadata();
    if (all_zero(metadata.manifest.bytes)) {
        throw std::invalid_argument(
            "cannot encode availability without a manifest digest");
    }
    if ((metadata.flags & ~kKnownAvailabilityFlags) != 0U) {
        throw std::invalid_argument("cannot encode availability with unknown flags");
    }
    std::vector<std::byte> output(metadata.encoded_size(), std::byte{0});
    std::copy(kAvailabilityMagic.begin(), kAvailabilityMagic.end(), output.begin());
    std::size_t offset = kAvailabilityMagic.size();
    store_le<std::uint16_t>(output.data() + offset,
                            ContentAvailabilityMetadata::kFormatVersion);
    offset += sizeof(std::uint16_t);
    store_le<std::uint16_t>(output.data() + offset,
                            static_cast<std::uint16_t>(
                                ContentAvailabilityMetadata::kHeaderBytes));
    offset += sizeof(std::uint16_t);
    store_le<std::uint16_t>(output.data() + offset, metadata.flags);
    offset += sizeof(std::uint16_t);
    output[offset++] = static_cast<std::byte>(metadata.hash_functions);
    ++offset; // reserved
    store_le<std::uint32_t>(output.data() + offset, metadata.bit_count);
    offset += sizeof(std::uint32_t);
    store_le<std::uint32_t>(output.data() + offset,
                            static_cast<std::uint32_t>(sketch.bits().size()));
    offset += sizeof(std::uint32_t);
    store_le<std::uint64_t>(output.data() + offset, metadata.sequence);
    offset += sizeof(std::uint64_t);
    store_le<std::uint64_t>(output.data() + offset, metadata.item_count);
    offset += sizeof(std::uint64_t);
    store_le<std::uint64_t>(output.data() + offset, metadata.available_bytes);
    offset += sizeof(std::uint64_t);
    std::copy(metadata.manifest.bytes.begin(), metadata.manifest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += metadata.manifest.bytes.size();
    store_le<std::uint64_t>(output.data() + offset, metadata.salt);
    offset += sizeof(std::uint64_t);
    std::copy(metadata.filter_digest.bytes.begin(),
              metadata.filter_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += metadata.filter_digest.bytes.size();
    // Eight trailing header bytes remain reserved and zero.
    if (offset + 8U != ContentAvailabilityMetadata::kHeaderBytes) {
        throw std::logic_error("content availability header layout mismatch");
    }
    std::copy(sketch.bits().begin(), sketch.bits().end(),
              output.begin() + static_cast<std::ptrdiff_t>(
                  ContentAvailabilityMetadata::kHeaderBytes));
    return output;
}

ContentAvailabilitySketch decode_content_availability(
    std::span<const std::byte> bytes, std::size_t max_filter_bytes) {
    if (bytes.size() < ContentAvailabilityMetadata::kHeaderBytes) {
        throw std::runtime_error("truncated content availability header");
    }
    if (!std::equal(kAvailabilityMagic.begin(), kAvailabilityMagic.end(),
                    bytes.begin())) {
        throw std::runtime_error("invalid content availability magic");
    }
    std::size_t offset = kAvailabilityMagic.size();
    const auto version = load_le<std::uint16_t>(bytes.data() + offset);
    offset += sizeof(std::uint16_t);
    const auto header_bytes = load_le<std::uint16_t>(bytes.data() + offset);
    offset += sizeof(std::uint16_t);
    if (version != ContentAvailabilityMetadata::kFormatVersion ||
        header_bytes != ContentAvailabilityMetadata::kHeaderBytes) {
        throw std::runtime_error("unsupported content availability format");
    }

    ContentAvailabilityMetadata metadata;
    metadata.flags = load_le<std::uint16_t>(bytes.data() + offset);
    offset += sizeof(std::uint16_t);
    metadata.hash_functions = std::to_integer<std::uint8_t>(bytes[offset++]);
    if (bytes[offset++] != std::byte{0}) {
        throw std::runtime_error("content availability reserved byte is nonzero");
    }
    metadata.bit_count = load_le<std::uint32_t>(bytes.data() + offset);
    offset += sizeof(std::uint32_t);
    const auto filter_bytes = load_le<std::uint32_t>(bytes.data() + offset);
    offset += sizeof(std::uint32_t);
    metadata.sequence = load_le<std::uint64_t>(bytes.data() + offset);
    offset += sizeof(std::uint64_t);
    metadata.item_count = load_le<std::uint64_t>(bytes.data() + offset);
    offset += sizeof(std::uint64_t);
    metadata.available_bytes = load_le<std::uint64_t>(bytes.data() + offset);
    offset += sizeof(std::uint64_t);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.manifest.bytes.size(), metadata.manifest.bytes.begin());
    offset += metadata.manifest.bytes.size();
    metadata.salt = load_le<std::uint64_t>(bytes.data() + offset);
    offset += sizeof(std::uint64_t);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.filter_digest.bytes.size(),
                metadata.filter_digest.bytes.begin());
    offset += metadata.filter_digest.bytes.size();
    if (!all_zero(bytes.subspan(offset,
                                ContentAvailabilityMetadata::kHeaderBytes - offset))) {
        throw std::runtime_error(
            "content availability reserved header bytes are nonzero");
    }
    if ((metadata.flags & ~kKnownAvailabilityFlags) != 0U) {
        throw std::runtime_error("content availability has unknown flags");
    }
    if (all_zero(metadata.manifest.bytes)) {
        throw std::runtime_error("content availability has an empty manifest digest");
    }
    if (filter_bytes < kMinimumFilterBytes ||
        !std::has_single_bit(filter_bytes) ||
        filter_bytes > max_filter_bytes ||
        filter_bytes > std::numeric_limits<std::uint32_t>::max() / 8U ||
        metadata.bit_count != filter_bytes * 8U ||
        metadata.hash_functions == 0U ||
        metadata.hash_functions > kMaximumHashFunctions) {
        throw std::runtime_error("content availability filter parameters are invalid");
    }
    if (bytes.size() != ContentAvailabilityMetadata::kHeaderBytes + filter_bytes) {
        throw std::runtime_error("content availability encoded length mismatch");
    }
    std::vector<std::byte> bits(filter_bytes);
    std::copy(bytes.begin() + static_cast<std::ptrdiff_t>(
                  ContentAvailabilityMetadata::kHeaderBytes),
              bytes.end(), bits.begin());
    if (sha256(bits) != metadata.filter_digest) {
        throw std::runtime_error("content availability filter digest mismatch");
    }
    return ContentAvailabilitySketch(metadata, std::move(bits));
}

} // namespace toxsync
