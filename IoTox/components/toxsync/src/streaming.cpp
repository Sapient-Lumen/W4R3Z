#include "toxsync/streaming.hpp"

#include "artifact_hasher.hpp"
#include "native_file.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <limits>
#include <memory>
#include <span>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <unistd.h>
#endif

namespace toxsync {

struct StreamingWorkspaceAccess {
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

    static std::span<std::byte> prepare_data(StreamingWorkspace& workspace,
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

    static std::span<std::byte> prepare_records(StreamingWorkspace& workspace,
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

    static std::span<std::uint8_t> prepare_state(StreamingWorkspace& workspace,
                                                 std::size_t required,
                                                 std::uint32_t& growth_events) {
        if (workspace.state_capacity_ < required) {
            const auto capacity = growth_capacity(workspace.state_capacity_, required);
            workspace.state_ = std::make_unique_for_overwrite<std::uint8_t[]>(capacity);
            workspace.state_capacity_ = capacity;
            ++growth_events;
        }
        return {workspace.state_.get(), required};
    }

    static std::vector<RangeRead>& prepare_ranges(StreamingWorkspace& workspace,
                                                   std::size_t required,
                                                   std::uint32_t& growth_events) {
        if (workspace.ranges_.capacity() < required) {
            workspace.ranges_.reserve(required);
            ++growth_events;
        }
        workspace.ranges_.clear();
        return workspace.ranges_;
    }
};

namespace {

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

struct EncodedBlock {
    std::uint32_t weak{};
    std::uint32_t length{};
    Hash128 strong{};
};

[[nodiscard]] EncodedBlock decode_record(const std::byte* input) noexcept {
    return EncodedBlock{
        .weak = load_le<std::uint32_t>(input),
        .length = load_le<std::uint32_t>(input + 4U),
        .strong = Hash128{
            .lo = load_le<std::uint64_t>(input + 8U),
            .hi = load_le<std::uint64_t>(input + 16U),
        },
    };
}

[[nodiscard]] std::filesystem::path part_path_for(const std::filesystem::path& output) {
    auto path = output;
    path += ".toxsync.part";
    return path;
}

void ensure_parent(const std::filesystem::path& output) {
    const auto parent = output.parent_path();
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
        throw std::runtime_error("atomic rename failed: " + std::string(std::strerror(errno)));
    }
#else
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(source, destination, error);
    if (error) throw std::runtime_error("rename failed: " + error.message());
#endif
}

[[nodiscard]] std::size_t normalized_buffer_bytes(std::size_t requested,
                                                  std::uint32_t block_size) {
    if (requested == 0U) {
        throw std::invalid_argument("streaming I/O buffer size must be nonzero");
    }
    const auto block = static_cast<std::size_t>(block_size);
    auto blocks = requested / block;
    if (blocks == 0U) blocks = 1U;
    if (blocks > std::numeric_limits<std::size_t>::max() / block) {
        throw std::length_error("streaming I/O buffer size overflows this platform");
    }
    const auto bytes = blocks * block;
    if (bytes > static_cast<std::size_t>(std::numeric_limits<std::streamsize>::max())) {
        throw std::length_error("streaming I/O buffer exceeds stream limits");
    }
    return bytes;
}

void read_index_exact(detail::NativeFile& input,
                      std::uint64_t offset,
                      std::span<std::byte> output,
                      std::uint64_t& calls) {
    if (output.empty()) return;
    input.read_exact_at(offset, output);
    ++calls;
}

void read_range_exact(RangeSource& source,
                      std::uint64_t offset,
                      std::span<std::byte> output,
                      std::uint64_t& calls) {
    std::size_t done{};
    while (done < output.size()) {
        const auto count = source.read_at(offset + done, output.subspan(done));
        ++calls;
        if (count == 0U) {
            throw std::runtime_error("basis ended before requested aligned block");
        }
        if (count > output.size() - done) {
            throw std::runtime_error("basis returned an oversized read");
        }
        done += count;
    }
}

[[nodiscard]] std::uint32_t expected_block_length(const IndexFileMetadata& metadata,
                                                  std::uint64_t block_index) {
    const auto offset = block_index * static_cast<std::uint64_t>(metadata.block_size);
    return static_cast<std::uint32_t>(
        std::min<std::uint64_t>(metadata.block_size, metadata.target_size - offset));
}

void validate_record(const IndexFileMetadata& metadata,
                     std::uint64_t block_index,
                     const EncodedBlock& record) {
    const auto expected = expected_block_length(metadata, block_index);
    if (record.length == 0U || record.length != expected) {
        throw std::runtime_error("toxsync index contains an invalid block length");
    }
}

[[nodiscard]] std::uint64_t normalized_resume_size(const IndexFileMetadata& metadata,
                                                   const detail::NativeFile& partial,
                                                   bool resume) {
    if (!resume) return 0U;
    auto size = std::min(partial.size(), metadata.target_size);
    if (size == metadata.target_size) return size;
    return (size / metadata.block_size) * metadata.block_size;
}

bool validate_resume(detail::NativeFile& index,
                     const IndexFileMetadata& metadata,
                     detail::NativeFile& partial,
                     std::uint64_t resume_bytes,
                     std::span<std::byte> data,
                     std::span<std::byte> encoded_records,
                     detail::ArtifactSha256& digest,
                     StreamingSyncStats& stats) {
    if (resume_bytes == 0U) return true;

    const auto block = static_cast<std::size_t>(metadata.block_size);
    const auto capacity_blocks = data.size() / block;
    std::uint64_t target_offset{};
    std::uint64_t block_index{};
    std::uint64_t index_offset = Index::kHeaderBytes;
    while (target_offset < resume_bytes) {
        const auto remaining = resume_bytes - target_offset;
        const auto batch_bytes =
            static_cast<std::size_t>(std::min<std::uint64_t>(remaining, data.size()));
        const auto batch_blocks = (batch_bytes + block - 1U) / block;
        if (batch_blocks > capacity_blocks ||
            batch_blocks * Index::kRecordBytes > encoded_records.size()) {
            throw std::runtime_error("internal resume buffer sizing error");
        }

        auto bytes = data.first(batch_bytes);
        partial.read_exact_at(target_offset, bytes);
        ++stats.partial_read_calls;
        auto record_bytes = encoded_records.first(batch_blocks * Index::kRecordBytes);
        read_index_exact(index, index_offset, record_bytes, stats.index_read_calls);
        index_offset += record_bytes.size();

        std::size_t data_offset{};
        for (std::size_t i = 0; i < batch_blocks; ++i) {
            const auto record = decode_record(record_bytes.data() + i * Index::kRecordBytes);
            validate_record(metadata, block_index + i, record);
            const auto chunk = bytes.subspan(data_offset, record.length);
            if (fast_hash128(chunk) != record.strong) return false;
            data_offset += record.length;
        }
        digest.update(bytes);
        target_offset += batch_bytes;
        block_index += batch_blocks;
    }
    return true;
}

void append_range(std::vector<RangeRead>& ranges,
                  std::size_t max_ranges,
                  std::uint64_t source_offset,
                  std::span<std::byte> output,
                  RangeSource& source,
                  StreamingSyncStats& stats) {
    if (!ranges.empty()) {
        auto& previous = ranges.back();
        const auto previous_end = previous.offset + previous.output.size();
        if (previous_end == source_offset &&
            previous.output.data() + previous.output.size() == output.data()) {
            previous.output = std::span<std::byte>(previous.output.data(),
                                                   previous.output.size() + output.size());
            return;
        }
    }
    if (ranges.size() == max_ranges) {
        source.read_many(ranges);
        ++stats.source_batch_calls;
        stats.source_ranges += ranges.size();
        ranges.clear();
    }
    ranges.push_back(RangeRead{.offset = source_offset, .output = output});
}

void flush_ranges(std::vector<RangeRead>& ranges,
                  RangeSource& source,
                  StreamingSyncStats& stats) {
    if (ranges.empty()) return;
    source.read_many(ranges);
    ++stats.source_batch_calls;
    stats.source_ranges += ranges.size();
    ranges.clear();
}

void set_block_reused(std::span<std::uint8_t> state,
                      std::size_t block_index,
                      bool reused) noexcept {
    const auto byte_index = block_index / 8U;
    const auto mask = static_cast<std::uint8_t>(1U << (block_index % 8U));
    if (reused) {
        state[byte_index] = static_cast<std::uint8_t>(state[byte_index] | mask);
    } else {
        state[byte_index] = static_cast<std::uint8_t>(state[byte_index] & ~mask);
    }
}

[[nodiscard]] bool is_block_reused(std::span<const std::uint8_t> state,
                                   std::size_t block_index) noexcept {
    const auto byte_index = block_index / 8U;
    const auto mask = static_cast<std::uint8_t>(1U << (block_index % 8U));
    return (state[byte_index] & mask) != 0U;
}

} // namespace

StreamingSyncStats sync_file_streaming(const std::filesystem::path& index_path,
                                       const std::filesystem::path& basis_path,
                                       RangeSource& source,
                                       const std::filesystem::path& output,
                                       const StreamingSyncOptions& options) {
    StreamingWorkspace workspace;
    return sync_file_streaming(index_path, basis_path, source, output, workspace, options);
}

StreamingSyncStats sync_file_streaming(const std::filesystem::path& index_path,
                                       const std::filesystem::path& basis_path,
                                       RangeSource& source,
                                       const std::filesystem::path& output,
                                       StreamingWorkspace& workspace,
                                       const StreamingSyncOptions& options) {
    if (options.max_source_ranges_per_batch == 0U) {
        throw std::invalid_argument("source range batch limit must be nonzero");
    }
    if (options.max_source_ranges_per_batch > 1U * 1024U * 1024U) {
        throw std::invalid_argument("source range batch limit is unreasonably large");
    }

    StreamingSyncStats stats;
    stats.metadata = inspect_index_file(index_path, options.limits);
    stats.data_buffer_bytes =
        normalized_buffer_bytes(options.io_buffer_bytes, stats.metadata.block_size);
    const auto block = static_cast<std::size_t>(stats.metadata.block_size);
    const auto capacity_blocks = stats.data_buffer_bytes / block;
    if (capacity_blocks == 0U ||
        capacity_blocks > std::numeric_limits<std::size_t>::max() / Index::kRecordBytes) {
        throw std::length_error("streaming block capacity overflow");
    }
    stats.index_buffer_bytes = capacity_blocks * Index::kRecordBytes;
    stats.block_state_bytes = (capacity_blocks + 7U) / 8U;
    const auto max_ranges =
        std::min(options.max_source_ranges_per_batch, capacity_blocks);

    auto data = StreamingWorkspaceAccess::prepare_data(
        workspace, stats.data_buffer_bytes, stats.workspace_growth_events);
    auto records = StreamingWorkspaceAccess::prepare_records(
        workspace, stats.index_buffer_bytes, stats.workspace_growth_events);
    auto reused_state = StreamingWorkspaceAccess::prepare_state(
        workspace, stats.block_state_bytes, stats.workspace_growth_events);
    auto& ranges = StreamingWorkspaceAccess::prepare_ranges(
        workspace, max_ranges, stats.workspace_growth_events);
    stats.range_descriptor_bytes = max_ranges * sizeof(RangeRead);
    stats.workspace_reserved_bytes = workspace.resident_bytes();

    detail::NativeFile index(index_path, detail::NativeOpenMode::read_only);
    if (options.advise_sequential_io) index.advise_sequential();

    ensure_parent(output);
    const auto part = part_path_for(output);
    const bool preserve = options.resume && std::filesystem::exists(part);
    detail::NativeFile partial(
        part, preserve ? detail::NativeOpenMode::read_write_create
                       : detail::NativeOpenMode::read_write_truncate);
    if (options.advise_sequential_io) partial.advise_sequential();
    auto resume_bytes = normalized_resume_size(stats.metadata, partial, options.resume);
    partial.resize(resume_bytes);

    detail::ArtifactSha256 digest;
    if (!validate_resume(index, stats.metadata, partial, resume_bytes, data, records,
                         digest, stats)) {
        stats.discarded_resume_bytes = resume_bytes;
        resume_bytes = 0U;
        partial.resize(0U);
        digest = detail::ArtifactSha256{};
    }
    stats.resumed_bytes = resume_bytes;

    std::uint64_t basis_size{};
    std::unique_ptr<FileRangeSource> basis;
    std::error_code basis_error;
    if (std::filesystem::exists(basis_path, basis_error) && !basis_error) {
        basis_size = std::filesystem::file_size(basis_path, basis_error);
        if (basis_error) {
            throw std::runtime_error("cannot inspect basis file: " + basis_path.string() +
                                     ": " + basis_error.message());
        }
        if (basis_size != 0U) basis = std::make_unique<FileRangeSource>(basis_path);
    } else if (basis_error) {
        throw std::runtime_error("cannot inspect basis file: " + basis_path.string() +
                                 ": " + basis_error.message());
    }

    const auto first_block = resume_bytes == stats.metadata.target_size
        ? stats.metadata.block_count
        : resume_bytes / stats.metadata.block_size;
    std::uint64_t index_offset = static_cast<std::uint64_t>(Index::kHeaderBytes) +
        first_block * static_cast<std::uint64_t>(Index::kRecordBytes);

    std::uint64_t block_index = first_block;
    std::uint64_t target_offset = resume_bytes;
    while (block_index < stats.metadata.block_count) {
        const auto remaining_blocks = stats.metadata.block_count - block_index;
        const auto batch_blocks = static_cast<std::size_t>(
            std::min<std::uint64_t>(remaining_blocks, capacity_blocks));
        const auto batch_target_remaining = stats.metadata.target_size - target_offset;
        const auto batch_bytes = static_cast<std::size_t>(std::min<std::uint64_t>(
            batch_target_remaining,
            static_cast<std::uint64_t>(batch_blocks) * stats.metadata.block_size));
        auto batch = data.first(batch_bytes);
        auto encoded = records.first(batch_blocks * Index::kRecordBytes);
        read_index_exact(index, index_offset, encoded, stats.index_read_calls);
        index_offset += encoded.size();

        std::size_t basis_available{};
        if (basis && target_offset < basis_size) {
            basis_available = static_cast<std::size_t>(
                std::min<std::uint64_t>(batch_bytes, basis_size - target_offset));
            read_range_exact(*basis, target_offset, batch.first(basis_available),
                             stats.basis_read_calls);
        }

        std::fill(reused_state.begin(), reused_state.end(), std::uint8_t{0U});
        ranges.clear();
        std::size_t data_offset{};
        for (std::size_t i = 0; i < batch_blocks; ++i) {
            const auto record = decode_record(encoded.data() + i * Index::kRecordBytes);
            validate_record(stats.metadata, block_index + i, record);
            const auto length = static_cast<std::size_t>(record.length);
            auto chunk = batch.subspan(data_offset, length);
            const bool complete_basis = data_offset + length <= basis_available;
            const bool is_reused = complete_basis && fast_hash128(chunk) == record.strong;
            set_block_reused(reused_state, i, is_reused);
            if (is_reused) {
                ++stats.matched_blocks;
                stats.reused_bytes += length;
            } else {
                ++stats.missing_blocks;
                stats.fetched_bytes += length;
                append_range(ranges, max_ranges, target_offset + data_offset, chunk,
                             source, stats);
            }
            data_offset += length;
        }
        if (data_offset != batch_bytes) {
            throw std::runtime_error(
                "toxsync index records do not cover expected batch size");
        }
        flush_ranges(ranges, source, stats);

        data_offset = 0U;
        for (std::size_t i = 0; i < batch_blocks; ++i) {
            const auto record = decode_record(encoded.data() + i * Index::kRecordBytes);
            const auto length = static_cast<std::size_t>(record.length);
            const auto chunk =
                std::span<const std::byte>(batch.data() + data_offset, length);
            if (!is_block_reused(reused_state, i) && fast_hash128(chunk) != record.strong) {
                throw std::runtime_error(
                    "range source returned a block that failed toxsync strong verification");
            }
            data_offset += length;
        }

        partial.write_exact_at(target_offset, batch);
        ++stats.output_write_calls;
        digest.update(batch);
        target_offset += batch_bytes;
        block_index += batch_blocks;
    }

    stats.output_digest = digest.finish();
    if (stats.output_digest != stats.metadata.target_digest) {
        partial.close();
        std::error_code ignored;
        std::filesystem::remove(part, ignored);
        throw std::runtime_error("streamed artifact failed SHA-256 verification");
    }
    if (options.fsync_on_commit) {
        partial.sync();
        ++stats.sync_calls;
    }
    partial.close();
    atomic_replace(part, output);
    if (options.fsync_on_commit) {
        sync_parent(output);
        ++stats.sync_calls;
    }
    return stats;
}

} // namespace toxsync
