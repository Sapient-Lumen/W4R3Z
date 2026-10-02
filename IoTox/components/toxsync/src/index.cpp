#include "toxsync/index.hpp"
#include "toxsync/rolling_checksum.hpp"

#include "artifact_hasher.hpp"

#include <algorithm>
#include <array>
#include <fstream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <type_traits>
#include <vector>

namespace toxsync {
namespace {

constexpr std::array<std::byte, 8> kMagic{
    std::byte{'T'}, std::byte{'O'}, std::byte{'X'}, std::byte{'S'},
    std::byte{'Y'}, std::byte{'N'}, std::byte{'1'}, std::byte{0},
};

template <typename T>
void store_le(std::byte* output, T value) noexcept {
    static_assert(std::is_unsigned_v<T>);
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        output[i] = static_cast<std::byte>(value >> (i * 8U));
    }
}

template <typename T>
T load_le(const std::byte* input) noexcept {
    static_assert(std::is_unsigned_v<T>);
    std::uint64_t wide{};
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        wide |= static_cast<std::uint64_t>(std::to_integer<unsigned char>(input[i])) << (i * 8U);
    }
    return static_cast<T>(wide);
}

[[nodiscard]] std::uint64_t file_size_checked(const std::filesystem::path& path) {
    std::error_code error;
    const auto size = std::filesystem::file_size(path, error);
    if (error) throw std::runtime_error("cannot read file size: " + path.string() + ": " + error.message());
    return size;
}

void encode_header(const Index& index, std::span<std::byte, Index::kHeaderBytes> output) noexcept {
    std::copy(kMagic.begin(), kMagic.end(), output.begin());
    std::size_t offset = kMagic.size();
    store_le<std::uint16_t>(output.data() + offset, Index::kFormatVersion); offset += sizeof(std::uint16_t);
    store_le<std::uint16_t>(output.data() + offset, static_cast<std::uint16_t>(Index::kHeaderBytes));
    offset += sizeof(std::uint16_t);
    store_le<std::uint32_t>(output.data() + offset, index.block_size); offset += sizeof(std::uint32_t);
    store_le<std::uint64_t>(output.data() + offset, index.target_size); offset += sizeof(std::uint64_t);
    store_le<std::uint64_t>(output.data() + offset, static_cast<std::uint64_t>(index.blocks.size()));
    offset += sizeof(std::uint64_t);
    std::copy(index.target_digest.bytes.begin(), index.target_digest.bytes.end(), output.begin() +
              static_cast<std::ptrdiff_t>(offset));
}

void encode_record(const BlockRecord& block, std::span<std::byte, Index::kRecordBytes> output) noexcept {
    store_le<std::uint32_t>(output.data(), block.weak);
    store_le<std::uint32_t>(output.data() + 4U, block.length);
    store_le<std::uint64_t>(output.data() + 8U, block.strong.lo);
    store_le<std::uint64_t>(output.data() + 16U, block.strong.hi);
}

[[nodiscard]] BlockRecord decode_record(std::span<const std::byte, Index::kRecordBytes> input) noexcept {
    return BlockRecord{
        .weak = load_le<std::uint32_t>(input.data()),
        .length = load_le<std::uint32_t>(input.data() + 4U),
        .strong = Hash128{
            .lo = load_le<std::uint64_t>(input.data() + 8U),
            .hi = load_le<std::uint64_t>(input.data() + 16U),
        },
    };
}

Index decode_header(std::span<const std::byte, Index::kHeaderBytes> bytes,
                    std::uint64_t& block_count) {
    if (!std::equal(kMagic.begin(), kMagic.end(), bytes.begin())) {
        throw std::runtime_error("invalid toxsync index magic");
    }
    std::size_t offset = kMagic.size();
    const auto version = load_le<std::uint16_t>(bytes.data() + offset); offset += sizeof(std::uint16_t);
    const auto header_size = load_le<std::uint16_t>(bytes.data() + offset); offset += sizeof(std::uint16_t);
    if (version != Index::kFormatVersion) throw std::runtime_error("unsupported toxsync index version");
    if (header_size != Index::kHeaderBytes) throw std::runtime_error("unsupported toxsync index header size");

    Index index;
    index.block_size = load_le<std::uint32_t>(bytes.data() + offset); offset += sizeof(std::uint32_t);
    index.target_size = load_le<std::uint64_t>(bytes.data() + offset); offset += sizeof(std::uint64_t);
    block_count = load_le<std::uint64_t>(bytes.data() + offset); offset += sizeof(std::uint64_t);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset), index.target_digest.bytes.size(),
                index.target_digest.bytes.begin());
    return index;
}

void validate_header_limits(const Index& index, std::uint64_t block_count, const IndexLimits& limits) {
    if (index.block_size < limits.min_block_size || index.block_size > limits.max_block_size) {
        throw std::runtime_error("toxsync index block size is outside configured limits");
    }
    if (index.target_size > limits.max_target_size) {
        throw std::runtime_error("toxsync target exceeds configured size limit");
    }
    if (block_count > limits.max_blocks || block_count > std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("toxsync index exceeds configured block limit");
    }
    if (index.expected_block_count() != block_count) {
        throw std::runtime_error("toxsync index block count does not match target size");
    }
}

} // namespace

Index Index::build_file(const std::filesystem::path& target, std::uint32_t requested_block_size) {
    return build_file(target, IndexBuildOptions{.block_size = requested_block_size});
}

Index Index::build_file(const std::filesystem::path& target, const IndexBuildOptions& options) {
    if (options.block_size < options.limits.min_block_size ||
        options.block_size > options.limits.max_block_size) {
        throw std::invalid_argument("block size is outside configured limits");
    }
    if (options.io_buffer_bytes == 0U) throw std::invalid_argument("index I/O buffer size must be nonzero");

    Index index;
    index.block_size = options.block_size;
    index.target_size = file_size_checked(target);
    if (index.target_size > options.limits.max_target_size) {
        throw std::runtime_error("toxsync target exceeds configured size limit");
    }
    const auto expected = index.expected_block_count();
    if (expected > options.limits.max_blocks || expected > std::numeric_limits<std::size_t>::max()) {
        throw std::runtime_error("toxsync index exceeds configured block limit");
    }
    index.blocks.reserve(static_cast<std::size_t>(expected));

    const auto block_bytes = static_cast<std::size_t>(index.block_size);
    auto blocks_per_buffer = options.io_buffer_bytes / block_bytes;
    if (blocks_per_buffer == 0U) blocks_per_buffer = 1U;
    if (blocks_per_buffer > std::numeric_limits<std::size_t>::max() / block_bytes) {
        throw std::length_error("index I/O buffer size overflows this platform");
    }
    const auto buffer_bytes = blocks_per_buffer * block_bytes;
    if (buffer_bytes > static_cast<std::size_t>(std::numeric_limits<std::streamsize>::max())) {
        throw std::length_error("index I/O buffer exceeds stream limits");
    }

    std::ifstream input(target, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open target file: " + target.string());
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(buffer_bytes);
    detail::ArtifactSha256 digest;
    std::uint64_t remaining = index.target_size;
    while (remaining != 0U) {
        const auto count = static_cast<std::size_t>(std::min<std::uint64_t>(remaining, buffer_bytes));
        input.read(reinterpret_cast<char*>(buffer.get()), static_cast<std::streamsize>(count));
        if (static_cast<std::size_t>(input.gcount()) != count) {
            throw std::runtime_error("target file changed or ended while building index: " + target.string());
        }
        const auto bytes = std::span<const std::byte>(buffer.get(), count);
        digest.update(bytes);
        for (std::size_t offset = 0; offset < count; offset += block_bytes) {
            const auto length = std::min(block_bytes, count - offset);
            const auto block = bytes.subspan(offset, length);
            index.blocks.push_back(BlockRecord{
                .weak = RollingChecksum::compute(block).value(),
                .length = static_cast<std::uint32_t>(length),
                .strong = fast_hash128(block),
            });
        }
        remaining -= count;
    }
    index.target_digest = digest.finish();
    index.validate(options.limits);
    return index;
}

std::uint64_t Index::expected_block_count() const noexcept {
    if (target_size == 0U || block_size == 0U) return 0U;
    return 1U + (target_size - 1U) / block_size;
}

std::uint64_t Index::encoded_size() const noexcept {
    return static_cast<std::uint64_t>(kHeaderBytes) +
           static_cast<std::uint64_t>(blocks.size()) * static_cast<std::uint64_t>(kRecordBytes);
}

void Index::validate(const IndexLimits& limits) const {
    if (block_size < limits.min_block_size || block_size > limits.max_block_size) {
        throw std::runtime_error("toxsync index block size is outside configured limits");
    }
    if (target_size > limits.max_target_size) throw std::runtime_error("toxsync target exceeds configured size limit");
    const auto expected = expected_block_count();
    if (expected > limits.max_blocks) throw std::runtime_error("toxsync index exceeds configured block limit");
    if (blocks.size() != expected) throw std::runtime_error("toxsync index block count does not match target size");
    for (std::size_t i = 0; i < blocks.size(); ++i) {
        const auto expected_length = static_cast<std::uint32_t>(
            std::min<std::uint64_t>(block_size, target_size - static_cast<std::uint64_t>(i) * block_size));
        if (blocks[i].length != expected_length || blocks[i].length == 0U) {
            throw std::runtime_error("toxsync index contains an invalid block length");
        }
    }
}

std::vector<std::byte> Index::encode() const {
    validate();
    if (encoded_size() > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error("toxsync index is too large to encode");
    }
    std::vector<std::byte> output(static_cast<std::size_t>(encoded_size()));
    encode_header(*this, std::span<std::byte, kHeaderBytes>(output.data(), kHeaderBytes));
    auto* cursor = output.data() + kHeaderBytes;
    for (const auto& block : blocks) {
        encode_record(block, std::span<std::byte, kRecordBytes>(cursor, kRecordBytes));
        cursor += kRecordBytes;
    }
    return output;
}

Index Index::decode(std::span<const std::byte> bytes, const IndexLimits& limits) {
    if (bytes.size() < kHeaderBytes) throw std::runtime_error("truncated toxsync index header");
    std::uint64_t block_count{};
    auto index = decode_header(std::span<const std::byte, kHeaderBytes>(bytes.data(), kHeaderBytes), block_count);
    validate_header_limits(index, block_count, limits);
    const auto required = index.encoded_size() + block_count * kRecordBytes;
    // index.encoded_size() currently contains only the header because blocks is empty.
    if (required != bytes.size()) throw std::runtime_error("toxsync index length does not match block count");
    index.blocks.resize(static_cast<std::size_t>(block_count));
    const auto* cursor = bytes.data() + kHeaderBytes;
    for (auto& block : index.blocks) {
        block = decode_record(std::span<const std::byte, kRecordBytes>(cursor, kRecordBytes));
        cursor += kRecordBytes;
    }
    index.validate(limits);
    return index;
}

void Index::write_file(const std::filesystem::path& path) const {
    validate();
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create toxsync index: " + path.string());

    std::array<std::byte, kHeaderBytes> header{};
    encode_header(*this, header);
    output.write(reinterpret_cast<const char*>(header.data()), static_cast<std::streamsize>(header.size()));

    constexpr std::size_t kRecordsPerChunk = 2048U;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(kRecordsPerChunk * kRecordBytes);
    std::size_t first{};
    while (first < blocks.size()) {
        const auto count = std::min(kRecordsPerChunk, blocks.size() - first);
        for (std::size_t i = 0; i < count; ++i) {
            encode_record(blocks[first + i], std::span<std::byte, kRecordBytes>(
                buffer.get() + i * kRecordBytes, kRecordBytes));
        }
        const auto bytes = count * kRecordBytes;
        output.write(reinterpret_cast<const char*>(buffer.get()), static_cast<std::streamsize>(bytes));
        first += count;
    }
    if (!output) throw std::runtime_error("cannot write toxsync index: " + path.string());
}

Index Index::read_file(const std::filesystem::path& path, const IndexLimits& limits) {
    const auto file_size = file_size_checked(path);
    if (file_size < kHeaderBytes) throw std::runtime_error("truncated toxsync index header");
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("cannot open toxsync index: " + path.string());

    std::array<std::byte, kHeaderBytes> header{};
    input.read(reinterpret_cast<char*>(header.data()), static_cast<std::streamsize>(header.size()));
    if (static_cast<std::size_t>(input.gcount()) != header.size()) {
        throw std::runtime_error("cannot read toxsync index header: " + path.string());
    }
    std::uint64_t block_count{};
    auto index = decode_header(header, block_count);
    validate_header_limits(index, block_count, limits);
    const auto required = static_cast<std::uint64_t>(kHeaderBytes) + block_count * kRecordBytes;
    if (file_size != required) throw std::runtime_error("toxsync index length does not match block count");

    index.blocks.resize(static_cast<std::size_t>(block_count));
    constexpr std::size_t kRecordsPerChunk = 2048U;
    auto buffer = std::make_unique_for_overwrite<std::byte[]>(kRecordsPerChunk * kRecordBytes);
    std::size_t first{};
    while (first < index.blocks.size()) {
        const auto count = std::min(kRecordsPerChunk, index.blocks.size() - first);
        const auto bytes = count * kRecordBytes;
        input.read(reinterpret_cast<char*>(buffer.get()), static_cast<std::streamsize>(bytes));
        if (static_cast<std::size_t>(input.gcount()) != bytes) {
            throw std::runtime_error("cannot read complete toxsync index: " + path.string());
        }
        for (std::size_t i = 0; i < count; ++i) {
            index.blocks[first + i] = decode_record(std::span<const std::byte, kRecordBytes>(
                buffer.get() + i * kRecordBytes, kRecordBytes));
        }
        first += count;
    }
    index.validate(limits);
    return index;
}

} // namespace toxsync
