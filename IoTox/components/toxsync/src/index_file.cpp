#include "toxsync/index_file.hpp"

#include "artifact_hasher.hpp"
#include "native_file.hpp"
#include "toxsync/rolling_checksum.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <limits>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <type_traits>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <unistd.h>
#endif

namespace toxsync {

struct IndexWorkspaceAccess {
    [[nodiscard]] static std::size_t growth_capacity(std::size_t current,
                                                     std::size_t required) {
        if (current >= required) return current;
        if (current == 0U) return required;
        const auto extra = current / 2U;
        const auto grown = extra > std::numeric_limits<std::size_t>::max() - current
            ? std::numeric_limits<std::size_t>::max()
            : current + extra;
        return std::max(required, grown);
    }

    static std::span<std::byte> prepare_data(IndexBuildWorkspace& workspace,
                                             std::size_t required,
                                             std::uint32_t& growth_events) {
        if (workspace.data_capacity_ < required) {
            const auto capacity = growth_capacity(workspace.data_capacity_, required);
            workspace.data_ = std::make_unique_for_overwrite<std::byte[]>(capacity);
            workspace.data_capacity_ = capacity;
            ++growth_events;
        }
        return {workspace.data_.get(), required};
    }

    static std::span<std::byte> prepare_records(IndexBuildWorkspace& workspace,
                                                std::size_t required,
                                                std::uint32_t& growth_events) {
        if (workspace.record_capacity_ < required) {
            const auto capacity = growth_capacity(workspace.record_capacity_, required);
            workspace.records_ = std::make_unique_for_overwrite<std::byte[]>(capacity);
            workspace.record_capacity_ = capacity;
            ++growth_events;
        }
        return {workspace.records_.get(), required};
    }
};

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
[[nodiscard]] T load_le(const std::byte* input) noexcept {
    static_assert(std::is_unsigned_v<T>);
    std::uint64_t wide{};
    for (std::size_t i = 0; i < sizeof(T); ++i) {
        wide |= static_cast<std::uint64_t>(std::to_integer<unsigned char>(input[i]))
                << (i * 8U);
    }
    return static_cast<T>(wide);
}

[[nodiscard]] std::uint64_t block_count_for(std::uint64_t target_size,
                                            std::uint32_t block_size) noexcept {
    if (target_size == 0U || block_size == 0U) return 0U;
    return 1U + (target_size - 1U) / block_size;
}

[[nodiscard]] std::filesystem::path part_path_for(const std::filesystem::path& output) {
    auto part = output;
    part += ".toxsync.index.part";
    return part;
}

void ensure_parent(const std::filesystem::path& path) {
    const auto parent = path.parent_path();
    if (!parent.empty()) std::filesystem::create_directories(parent);
}

void sync_parent(const std::filesystem::path& path) {
#if defined(__unix__) || defined(__APPLE__)
    auto parent = path.parent_path();
    if (parent.empty()) parent = ".";
    const int descriptor = ::open(parent.c_str(), O_RDONLY | O_CLOEXEC);
    if (descriptor < 0) {
        throw std::runtime_error("cannot open parent directory for fsync: " + parent.string() +
                                 ": " + std::strerror(errno));
    }
    const int result = ::fsync(descriptor);
    const int saved = errno;
    (void)::close(descriptor);
    if (result != 0) {
        throw std::runtime_error("parent directory fsync failed: " + parent.string() +
                                 ": " + std::strerror(saved));
    }
#else
    (void)path;
#endif
}

void atomic_replace(const std::filesystem::path& source,
                    const std::filesystem::path& destination) {
#if defined(__unix__) || defined(__APPLE__)
    if (::rename(source.c_str(), destination.c_str()) != 0) {
        throw std::runtime_error("atomic index rename failed: " +
                                 std::string(std::strerror(errno)));
    }
#else
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(source, destination, error);
    if (error) throw std::runtime_error("index rename failed: " + error.message());
#endif
}

[[nodiscard]] std::array<std::byte, Index::kHeaderBytes> encode_header(
    const IndexFileMetadata& metadata) noexcept {
    std::array<std::byte, Index::kHeaderBytes> output{};
    std::copy(kMagic.begin(), kMagic.end(), output.begin());
    std::size_t offset = kMagic.size();
    store_le<std::uint16_t>(output.data() + offset, Index::kFormatVersion);
    offset += sizeof(std::uint16_t);
    store_le<std::uint16_t>(output.data() + offset,
                            static_cast<std::uint16_t>(Index::kHeaderBytes));
    offset += sizeof(std::uint16_t);
    store_le<std::uint32_t>(output.data() + offset, metadata.block_size);
    offset += sizeof(std::uint32_t);
    store_le<std::uint64_t>(output.data() + offset, metadata.target_size);
    offset += sizeof(std::uint64_t);
    store_le<std::uint64_t>(output.data() + offset, metadata.block_count);
    offset += sizeof(std::uint64_t);
    std::copy(metadata.target_digest.bytes.begin(), metadata.target_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    return output;
}

void encode_record(std::byte* output,
                   std::uint32_t weak,
                   std::uint32_t length,
                   const Hash128& strong) noexcept {
    store_le<std::uint32_t>(output, weak);
    store_le<std::uint32_t>(output + 4U, length);
    store_le<std::uint64_t>(output + 8U, strong.lo);
    store_le<std::uint64_t>(output + 16U, strong.hi);
}

[[nodiscard]] IndexFileMetadata decode_header(
    std::span<const std::byte, Index::kHeaderBytes> bytes) {
    if (!std::equal(kMagic.begin(), kMagic.end(), bytes.begin())) {
        throw std::runtime_error("invalid toxsync index magic");
    }
    std::size_t offset = kMagic.size();
    const auto version = load_le<std::uint16_t>(bytes.data() + offset);
    offset += sizeof(std::uint16_t);
    const auto header_size = load_le<std::uint16_t>(bytes.data() + offset);
    offset += sizeof(std::uint16_t);
    if (version != Index::kFormatVersion) {
        throw std::runtime_error("unsupported toxsync index version");
    }
    if (header_size != Index::kHeaderBytes) {
        throw std::runtime_error("unsupported toxsync index header size");
    }

    IndexFileMetadata metadata;
    metadata.block_size = load_le<std::uint32_t>(bytes.data() + offset);
    offset += sizeof(std::uint32_t);
    metadata.target_size = load_le<std::uint64_t>(bytes.data() + offset);
    offset += sizeof(std::uint64_t);
    metadata.block_count = load_le<std::uint64_t>(bytes.data() + offset);
    offset += sizeof(std::uint64_t);
    std::copy_n(bytes.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.target_digest.bytes.size(), metadata.target_digest.bytes.begin());
    return metadata;
}

void validate_metadata(const IndexFileMetadata& metadata,
                       const IndexLimits& limits,
                       std::uint64_t file_size) {
    if (metadata.block_size < limits.min_block_size ||
        metadata.block_size > limits.max_block_size) {
        throw std::runtime_error("toxsync index block size is outside configured limits");
    }
    if (metadata.target_size > limits.max_target_size) {
        throw std::runtime_error("toxsync target exceeds configured size limit");
    }
    if (metadata.block_count > limits.max_blocks) {
        throw std::runtime_error("toxsync index exceeds configured block limit");
    }
    if (block_count_for(metadata.target_size, metadata.block_size) != metadata.block_count) {
        throw std::runtime_error("toxsync index block count does not match target size");
    }
    const auto expected_size = metadata.encoded_size();
    if (expected_size < Index::kHeaderBytes || file_size != expected_size) {
        throw std::runtime_error("toxsync index length does not match block count");
    }
}

[[nodiscard]] std::size_t normalized_data_buffer(std::size_t requested,
                                                 std::uint32_t block_size) {
    if (requested == 0U) throw std::invalid_argument("index I/O buffer size must be nonzero");
    const auto block = static_cast<std::size_t>(block_size);
    auto blocks = requested / block;
    if (blocks == 0U) blocks = 1U;
    if (blocks > std::numeric_limits<std::size_t>::max() / block) {
        throw std::length_error("index I/O buffer size overflows this platform");
    }
    const auto result = blocks * block;
    if (result > static_cast<std::size_t>(std::numeric_limits<std::streamsize>::max())) {
        throw std::length_error("index I/O buffer exceeds stream limits");
    }
    return result;
}

[[nodiscard]] std::size_t normalized_record_buffer(std::size_t requested) {
    if (requested == 0U) {
        throw std::invalid_argument("index record buffer size must be nonzero");
    }
    auto records = requested / Index::kRecordBytes;
    if (records == 0U) records = 1U;
    return records * Index::kRecordBytes;
}

} // namespace

std::uint64_t IndexFileMetadata::encoded_size() const noexcept {
    if (block_count > (std::numeric_limits<std::uint64_t>::max() - Index::kHeaderBytes) /
                          Index::kRecordBytes) {
        return std::numeric_limits<std::uint64_t>::max();
    }
    return static_cast<std::uint64_t>(Index::kHeaderBytes) +
           block_count * static_cast<std::uint64_t>(Index::kRecordBytes);
}

std::uint64_t index_metadata_bytes(std::uint64_t target_size,
                                   std::uint32_t block_size) {
    if (block_size == 0U) throw std::invalid_argument("block size must be nonzero");
    const auto blocks = block_count_for(target_size, block_size);
    if (blocks > (std::numeric_limits<std::uint64_t>::max() - Index::kHeaderBytes) /
                     Index::kRecordBytes) {
        throw std::overflow_error("index metadata size overflow");
    }
    return static_cast<std::uint64_t>(Index::kHeaderBytes) +
           blocks * static_cast<std::uint64_t>(Index::kRecordBytes);
}

std::uint32_t choose_block_size(std::uint64_t target_size,
                                const AutoBlockSizeOptions& options) {
    if (options.min_block_size == 0U || options.max_block_size == 0U ||
        options.min_block_size > options.max_block_size) {
        throw std::invalid_argument("invalid automatic block-size bounds");
    }
    if (options.metadata_budget_bytes < Index::kHeaderBytes) {
        throw std::invalid_argument("metadata budget is smaller than the toxsync index header");
    }
    if (target_size == 0U) return options.min_block_size;
    const auto record_budget =
        (options.metadata_budget_bytes - Index::kHeaderBytes) / Index::kRecordBytes;
    if (record_budget == 0U) {
        throw std::invalid_argument("metadata budget cannot hold one toxsync block record");
    }
    const auto required_wide = 1U + (target_size - 1U) / record_budget;
    std::uint64_t candidate = std::max<std::uint64_t>(options.min_block_size, required_wide);
    if (options.power_of_two) {
        std::uint64_t rounded = 1U;
        while (rounded < candidate) {
            if (rounded > std::numeric_limits<std::uint32_t>::max() / 2U) {
                throw std::overflow_error("automatic block size overflow");
            }
            rounded <<= 1U;
        }
        candidate = rounded;
    }
    if (candidate > options.max_block_size) {
        throw std::runtime_error(
            "metadata budget requires a block size above the configured maximum");
    }
    const auto result = static_cast<std::uint32_t>(candidate);
    if (index_metadata_bytes(target_size, result) > options.metadata_budget_bytes) {
        throw std::runtime_error(
            "automatic block-size selection could not satisfy metadata budget");
    }
    return result;
}

IndexFileMetadata inspect_index_file(const std::filesystem::path& index_path,
                                     const IndexLimits& limits) {
    detail::NativeFile input(index_path, detail::NativeOpenMode::read_only);
    const auto size = input.size();
    if (size < Index::kHeaderBytes) {
        throw std::runtime_error("truncated toxsync index header");
    }
    std::array<std::byte, Index::kHeaderBytes> header{};
    input.read_exact_at(0U, header);
    auto metadata = decode_header(header);
    validate_metadata(metadata, limits, size);
    return metadata;
}

IndexFileBuildStats build_index_file(const std::filesystem::path& target,
                                     const std::filesystem::path& index_path,
                                     const IndexFileBuildOptions& options) {
    IndexBuildWorkspace workspace;
    return build_index_file(target, index_path, workspace, options);
}

IndexFileBuildStats build_index_file(const std::filesystem::path& target,
                                     const std::filesystem::path& index_path,
                                     IndexBuildWorkspace& workspace,
                                     const IndexFileBuildOptions& options) {
    IndexFileBuildStats stats;
    detail::NativeFile input(target, detail::NativeOpenMode::read_only);
    stats.metadata.target_size = input.size();
    if (stats.metadata.target_size > options.limits.max_target_size) {
        throw std::runtime_error("toxsync target exceeds configured size limit");
    }

    if (options.block_size == 0U) {
        AutoBlockSizeOptions auto_options = options.auto_block;
        auto_options.min_block_size =
            std::max(auto_options.min_block_size, options.limits.min_block_size);
        auto_options.max_block_size =
            std::min(auto_options.max_block_size, options.limits.max_block_size);
        stats.metadata.block_size = choose_block_size(stats.metadata.target_size, auto_options);
    } else {
        stats.metadata.block_size = options.block_size;
    }
    if (stats.metadata.block_size < options.limits.min_block_size ||
        stats.metadata.block_size > options.limits.max_block_size) {
        throw std::invalid_argument("block size is outside configured limits");
    }
    stats.metadata.block_count =
        block_count_for(stats.metadata.target_size, stats.metadata.block_size);
    if (stats.metadata.block_count > options.limits.max_blocks) {
        throw std::runtime_error("toxsync index exceeds configured block limit");
    }

    stats.data_buffer_bytes =
        normalized_data_buffer(options.io_buffer_bytes, stats.metadata.block_size);
    stats.record_buffer_bytes = normalized_record_buffer(options.record_buffer_bytes);
    auto data = IndexWorkspaceAccess::prepare_data(
        workspace, stats.data_buffer_bytes, stats.workspace_growth_events);
    auto records = IndexWorkspaceAccess::prepare_records(
        workspace, stats.record_buffer_bytes, stats.workspace_growth_events);
    stats.workspace_reserved_bytes = workspace.resident_bytes();

    if (options.advise_sequential_io) input.advise_sequential();

    ensure_parent(index_path);
    const auto part = part_path_for(index_path);
    std::error_code ignored;
    std::filesystem::remove(part, ignored);

    try {
        detail::NativeFile output(part, detail::NativeOpenMode::read_write_truncate);
        detail::ArtifactSha256 digest;
        std::uint64_t input_offset{};
        std::uint64_t output_offset = Index::kHeaderBytes;
        std::uint64_t remaining = stats.metadata.target_size;
        std::size_t record_used{};
        std::uint64_t emitted_blocks{};
        const auto block = static_cast<std::size_t>(stats.metadata.block_size);

        auto flush_records = [&] {
            if (record_used == 0U) return;
            output.write_exact_at(output_offset, records.first(record_used));
            output_offset += record_used;
            ++stats.index_write_calls;
            record_used = 0U;
        };

        while (remaining != 0U) {
            const auto count = static_cast<std::size_t>(
                std::min<std::uint64_t>(remaining, data.size()));
            auto bytes = data.first(count);
            input.read_exact_at(input_offset, bytes);
            ++stats.target_read_calls;
            digest.update(bytes);

            for (std::size_t offset = 0U; offset < count; offset += block) {
                const auto length = std::min(block, count - offset);
                if (record_used + Index::kRecordBytes > records.size()) flush_records();
                const auto chunk = std::span<const std::byte>(bytes).subspan(offset, length);
                encode_record(records.data() + record_used,
                              RollingChecksum::compute(chunk).value(),
                              static_cast<std::uint32_t>(length), fast_hash128(chunk));
                record_used += Index::kRecordBytes;
                ++emitted_blocks;
            }

            input_offset += count;
            remaining -= count;
            if (options.discard_input_cache) {
                input.advise_dont_need(input_offset - count, count);
            }
        }
        flush_records();

        if (emitted_blocks != stats.metadata.block_count) {
            throw std::runtime_error(
                "internal toxsync block-count mismatch while building index");
        }
        if (input.size() != stats.metadata.target_size) {
            throw std::runtime_error("target size changed while building index: " +
                                     target.string());
        }

        stats.metadata.target_digest = digest.finish();
        const auto header = encode_header(stats.metadata);
        output.write_exact_at(0U, header);
        ++stats.index_write_calls;
        if (output.size() != stats.metadata.encoded_size()) {
            throw std::runtime_error("written toxsync index length is inconsistent");
        }
        if (options.fsync_on_commit) output.sync();
        output.close();

        atomic_replace(part, index_path);
        if (options.fsync_on_commit) sync_parent(index_path);
    } catch (...) {
        std::filesystem::remove(part, ignored);
        throw;
    }
    return stats;
}

bool verify_indexed_file(const std::filesystem::path& index_path,
                         const std::filesystem::path& artifact,
                         const IndexLimits& limits) {
    const auto metadata = inspect_index_file(index_path, limits);
    std::error_code error;
    if (std::filesystem::file_size(artifact, error) != metadata.target_size || error) {
        return false;
    }
    return sha256_file(artifact.string()) == metadata.target_digest;
}

} // namespace toxsync
