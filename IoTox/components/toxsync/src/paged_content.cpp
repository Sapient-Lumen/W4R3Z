#include "toxsync/content_store.hpp"

#include "artifact_hasher.hpp"
#include "native_file.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <cerrno>
#include <chrono>
#include <cstring>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <system_error>
#include <type_traits>

#if defined(__unix__) || defined(__APPLE__)
#include <fcntl.h>
#include <unistd.h>
#endif

namespace toxsync {

struct PagedContentWorkspaceAccess final {
    static std::size_t growth_capacity(std::size_t current, std::size_t required) {
        if (required == 0U) return 0U;
        if (current >= required) return current;
        constexpr std::size_t page = 4096U;
        if (required > std::numeric_limits<std::size_t>::max() - (page - 1U)) {
            return required;
        }
        return ((required + page - 1U) / page) * page;
    }

    static std::span<std::byte> prepare_io(ContentStoreWorkspace& workspace,
                                            std::size_t required,
                                            std::uint32_t& growth_events) {
        if (workspace.io_capacity_ < required) {
            const auto capacity = growth_capacity(workspace.io_capacity_, required);
            workspace.io_ = std::make_unique_for_overwrite<std::byte[]>(capacity);
            workspace.io_capacity_ = capacity;
            ++growth_events;
        }
        return {workspace.io_.get(), required};
    }

    static std::span<std::byte> prepare_chunk(ContentStoreWorkspace& workspace,
                                               std::size_t required,
                                               std::uint32_t& growth_events) {
        if (workspace.chunk_capacity_ < required) {
            const auto capacity = growth_capacity(workspace.chunk_capacity_, required);
            workspace.chunk_ = std::make_unique_for_overwrite<std::byte[]>(capacity);
            workspace.chunk_capacity_ = capacity;
            ++growth_events;
        }
        return {workspace.chunk_.get(), required};
    }

    static std::span<std::byte> prepare_records(ContentStoreWorkspace& workspace,
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

constexpr std::array<std::byte, 8> kFlatManifestMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'S'}, std::byte{'C'},
    std::byte{'D'}, std::byte{'C'}, std::byte{'2'}, std::byte{0},
};
constexpr std::array<std::byte, 8> kPagedRootMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'S'}, std::byte{'P'},
    std::byte{'G'}, std::byte{'2'}, std::byte{0}, std::byte{0},
};
constexpr std::array<std::byte, 8> kPagedPageMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'S'}, std::byte{'P'},
    std::byte{'A'}, std::byte{'G'}, std::byte{'2'}, std::byte{0},
};
constexpr std::uint16_t kPagedFlags = 0U;
constexpr std::uint32_t kPagedEntryFlags = 0U;
constexpr std::uint32_t kMaximumEntriesPerPage = 1U << 20U;
constexpr std::size_t kDefaultManifestBuffer = 64U * 1024U;

void throw_if_cancelled(const ContentReconstructOptions& options) {
    if (options.cancellation_requested()) {
        throw ContentOperationCancelled{};
    }
}

[[nodiscard]] constexpr std::uint64_t splitmix64(std::uint64_t value) noexcept {
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30U)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27U)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31U);
}

[[nodiscard]] constexpr std::array<std::uint64_t, 256> make_gear_table() noexcept {
    std::array<std::uint64_t, 256> table{};
    for (std::size_t index = 0U; index < table.size(); ++index) {
        table[index] = splitmix64(0x544f5853594e4300ULL + index);
    }
    return table;
}

constexpr auto kGearTable = make_gear_table();

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
    std::uint64_t wide{};
    for (std::size_t index = 0U; index < sizeof(T); ++index) {
        wide |= static_cast<std::uint64_t>(
                    std::to_integer<unsigned char>(input[index]))
                << (index * 8U);
    }
    return static_cast<T>(wide);
}

[[nodiscard]] bool all_zero(std::span<const std::byte> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::byte value) {
        return value == std::byte{0};
    });
}

[[nodiscard]] std::uint64_t ceiling_divide(std::uint64_t numerator,
                                           std::uint64_t denominator) {
    if (denominator == 0U) {
        throw std::invalid_argument("paged content divisor must be nonzero");
    }
    if (numerator == 0U) return 0U;
    return 1U + (numerator - 1U) / denominator;
}

[[nodiscard]] std::uint64_t checked_add(std::uint64_t left,
                                        std::uint64_t right,
                                        const char* message) {
    if (left > std::numeric_limits<std::uint64_t>::max() - right) {
        throw std::overflow_error(message);
    }
    return left + right;
}

[[nodiscard]] std::uint64_t checked_multiply(std::uint64_t left,
                                             std::uint64_t right,
                                             const char* message) {
    if (left != 0U && right > std::numeric_limits<std::uint64_t>::max() / left) {
        throw std::overflow_error(message);
    }
    return left * right;
}

[[nodiscard]] std::uint64_t next_power_of_two(std::uint64_t value) {
    if (value <= 1U) return 1U;
    if (value > (std::uint64_t{1} << 63U)) {
        throw std::overflow_error("paged content chunk size cannot be rounded safely");
    }
    return std::bit_ceil(value);
}

void validate_chunking(const ContentChunking& chunking,
                       const ContentStoreLimits& limits) {
    if (chunking.min_bytes < limits.min_chunk_bytes ||
        chunking.max_bytes > limits.max_chunk_bytes ||
        chunking.min_bytes > chunking.average_bytes ||
        chunking.average_bytes > chunking.max_bytes ||
        !std::has_single_bit(chunking.average_bytes)) {
        throw std::invalid_argument("paged content chunking violates configured limits");
    }
}

void validate_entries_per_page(std::uint32_t entries_per_page) {
    if (entries_per_page == 0U || entries_per_page > kMaximumEntriesPerPage) {
        throw std::invalid_argument("paged content entries-per-page is outside limits");
    }
    const auto entries_bytes = checked_multiply(
        entries_per_page, PagedContentManifestMetadata::kChunkEntryBytes,
        "paged content page size overflows");
    const auto page_bytes = checked_add(
        PagedContentManifestMetadata::kPageHeaderBytes, entries_bytes,
        "paged content page size overflows");
    if (page_bytes > std::numeric_limits<std::uint32_t>::max()) {
        throw std::invalid_argument("paged content page cannot be encoded in 32 bits");
    }
}

[[nodiscard]] std::size_t normalized_io_bytes(std::size_t requested) {
    if (requested == 0U) {
        throw std::invalid_argument("paged content I/O buffer must be nonzero");
    }
    return requested;
}

[[nodiscard]] std::size_t normalized_root_buffer(std::size_t requested) {
    if (requested == 0U) {
        throw std::invalid_argument("paged content root buffer must be nonzero");
    }
    auto records = requested / PagedContentManifestMetadata::kPageRecordBytes;
    if (records == 0U) records = 1U;
    if (records > std::numeric_limits<std::size_t>::max() /
                      PagedContentManifestMetadata::kPageRecordBytes) {
        throw std::length_error("paged content root buffer overflows this platform");
    }
    return records * PagedContentManifestMetadata::kPageRecordBytes;
}

[[nodiscard]] std::size_t normalized_entry_buffer(std::size_t requested) {
    if (requested == 0U) {
        throw std::invalid_argument("paged content entry buffer must be nonzero");
    }
    auto records = requested / PagedContentManifestMetadata::kChunkEntryBytes;
    if (records == 0U) records = 1U;
    if (records > std::numeric_limits<std::size_t>::max() /
                      PagedContentManifestMetadata::kChunkEntryBytes) {
        throw std::length_error("paged content entry buffer overflows this platform");
    }
    return records * PagedContentManifestMetadata::kChunkEntryBytes;
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
        throw std::runtime_error("cannot open paged-content parent directory: " +
                                 parent.string() + ": " + std::strerror(errno));
    }
    const int result = ::fsync(descriptor);
    const int saved = errno;
    (void)::close(descriptor);
    if (result != 0) {
        throw std::runtime_error("cannot fsync paged-content parent directory: " +
                                 parent.string() + ": " + std::strerror(saved));
    }
#else
    (void)path;
#endif
}

void atomic_replace(const std::filesystem::path& source,
                    const std::filesystem::path& destination) {
#if defined(__unix__) || defined(__APPLE__)
    if (::rename(source.c_str(), destination.c_str()) != 0) {
        throw std::runtime_error("cannot atomically publish paged content: " +
                                 std::string(std::strerror(errno)));
    }
#else
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(source, destination, error);
    if (error) {
        throw std::runtime_error("cannot publish paged content: " + error.message());
    }
#endif
}

[[nodiscard]] std::filesystem::path part_path_for(
    const std::filesystem::path& path) {
    auto result = path;
    result += ".toxsync.part";
    return result;
}

class TemporaryPath final {
public:
    explicit TemporaryPath(std::filesystem::path path) : path_(std::move(path)) {}
    ~TemporaryPath() {
        if (!armed_) return;
        std::error_code ignored;
        std::filesystem::remove(path_, ignored);
    }
    TemporaryPath(const TemporaryPath&) = delete;
    TemporaryPath& operator=(const TemporaryPath&) = delete;
    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }
    void disarm() noexcept { armed_ = false; }

private:
    std::filesystem::path path_{};
    bool armed_{true};
};

[[nodiscard]] std::filesystem::path unique_temp_path(
    const std::filesystem::path& destination) {
    static std::atomic<std::uint64_t> sequence{};
    const auto number = sequence.fetch_add(1U, std::memory_order_relaxed);
#if defined(__unix__) || defined(__APPLE__)
    const auto process = static_cast<std::uint64_t>(::getpid());
#else
    const auto process = static_cast<std::uint64_t>(
        std::chrono::steady_clock::now().time_since_epoch().count());
#endif
    auto name = destination.filename().string();
    name += ".toxsync.tmp." + std::to_string(process) + "." +
            std::to_string(number);
    return destination.parent_path() / name;
}

[[nodiscard]] bool regular_file_exact_size(const std::filesystem::path& path,
                                            std::uint64_t expected_size) {
    std::error_code error;
    const auto status = std::filesystem::symlink_status(path, error);
    if (error || !std::filesystem::is_regular_file(status)) return false;
    const auto size = std::filesystem::file_size(path, error);
    return !error && size == expected_size;
}

[[nodiscard]] Digest256 hash_native_file(detail::NativeFile& file,
                                         std::span<std::byte> buffer,
                                         std::uint64_t size) {
    detail::ArtifactSha256 hasher;
    std::uint64_t offset{};
    while (offset < size) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(size - offset, buffer.size()));
        auto bytes = buffer.first(count);
        file.read_exact_at(offset, bytes);
        hasher.update(bytes);
        offset += count;
    }
    if (file.size() != size) {
        throw std::runtime_error("paged content file changed while hashing");
    }
    return hasher.finish();
}

[[nodiscard]] bool verify_file(const std::filesystem::path& path,
                               const Digest256& digest,
                               std::uint64_t size,
                               std::span<std::byte> buffer) {
    if (!regular_file_exact_size(path, size)) return false;
    detail::NativeFile input(path, detail::NativeOpenMode::read_only);
    return hash_native_file(input, buffer, size) == digest;
}

[[nodiscard]] bool publish_temp_no_replace(
    TemporaryPath& temporary,
    const std::filesystem::path& destination,
    bool fsync_parent_directory) {
    std::error_code error;
    std::filesystem::create_hard_link(temporary.path(), destination, error);
    if (!error) {
        std::filesystem::remove(temporary.path(), error);
        if (error) {
            throw std::runtime_error("cannot remove paged-content temporary file: " +
                                     error.message());
        }
        temporary.disarm();
        if (fsync_parent_directory) sync_parent(destination);
        return true;
    }
    if (std::filesystem::exists(destination)) return false;
    throw std::runtime_error("cannot publish paged-content object: " + error.message());
}

[[nodiscard]] bool store_bytes(const std::filesystem::path& store_root,
                               const Digest256& digest,
                               std::span<const std::byte> bytes,
                               bool fsync_on_commit,
                               bool verify_existing,
                               std::span<std::byte> verify_buffer) {
    const auto destination = content_store_path(store_root, digest);
    ensure_parent(destination);
    if (std::filesystem::exists(destination)) {
        if (!regular_file_exact_size(destination, bytes.size()) ||
            (verify_existing &&
             !verify_file(destination, digest, bytes.size(), verify_buffer))) {
            throw std::runtime_error(
                "paged-content object exists with invalid contents: " +
                destination.string());
        }
        return false;
    }

    const auto temporary_path = unique_temp_path(destination);
    TemporaryPath temporary(temporary_path);
    detail::NativeFile output(
        temporary_path, detail::NativeOpenMode::read_write_create_exclusive);
    output.write_exact_at(0U, bytes);
    if (fsync_on_commit) output.sync();
    output.close();
    const bool created = publish_temp_no_replace(
        temporary, destination, fsync_on_commit);
    if (created) return true;
    if (!regular_file_exact_size(destination, bytes.size()) ||
        (verify_existing &&
         !verify_file(destination, digest, bytes.size(), verify_buffer))) {
        throw std::runtime_error("racing paged-content object failed verification");
    }
    return false;
}

[[nodiscard]] bool store_file(const std::filesystem::path& store_root,
                              const std::filesystem::path& source,
                              const Digest256& digest,
                              std::uint64_t size,
                              std::span<std::byte> io,
                              bool fsync_on_commit,
                              bool verify_existing) {
    const auto destination = content_store_path(store_root, digest);
    ensure_parent(destination);
    if (std::filesystem::exists(destination)) {
        if (!regular_file_exact_size(destination, size) ||
            (verify_existing && !verify_file(destination, digest, size, io))) {
            throw std::runtime_error(
                "paged-content root exists with invalid contents: " +
                destination.string());
        }
        return false;
    }

    const auto temporary_path = unique_temp_path(destination);
    TemporaryPath temporary(temporary_path);
    detail::NativeFile input(source, detail::NativeOpenMode::read_only);
    detail::NativeFile output(
        temporary_path, detail::NativeOpenMode::read_write_create_exclusive);
    detail::ArtifactSha256 hasher;
    std::uint64_t offset{};
    while (offset < size) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(size - offset, io.size()));
        auto bytes = io.first(count);
        input.read_exact_at(offset, bytes);
        hasher.update(bytes);
        output.write_exact_at(offset, bytes);
        offset += count;
    }
    if (input.size() != size || hasher.finish() != digest) {
        throw std::runtime_error("paged-content root changed while publishing");
    }
    if (fsync_on_commit) output.sync();
    output.close();
    const bool created = publish_temp_no_replace(
        temporary, destination, fsync_on_commit);
    if (created) return true;
    if (!regular_file_exact_size(destination, size) ||
        (verify_existing && !verify_file(destination, digest, size, io))) {
        throw std::runtime_error("racing paged-content root failed verification");
    }
    return false;
}

class GearChunker final {
public:
    explicit GearChunker(ContentChunking options)
        : options_(options),
          mask_(static_cast<std::uint64_t>(options.average_bytes - 1U)) {}

    [[nodiscard]] bool push(std::byte value) noexcept {
        const auto index = std::to_integer<unsigned char>(value);
        hash_ = (hash_ << 1U) + kGearTable[index];
        ++length_;
        return length_ >= options_.max_bytes ||
               (length_ >= options_.min_bytes && (hash_ & mask_) == 0U);
    }

    void reset() noexcept {
        hash_ = 0U;
        length_ = 0U;
    }

private:
    ContentChunking options_{};
    std::uint64_t mask_{};
    std::uint64_t hash_{};
    std::uint32_t length_{};
};

void encode_chunk_entry(
    std::span<std::byte, PagedContentManifestMetadata::kChunkEntryBytes> output,
    std::uint32_t length,
    const Digest256& digest) noexcept {
    store_le<std::uint32_t>(output.data(), length);
    store_le<std::uint32_t>(output.data() + 4U, kPagedEntryFlags);
    std::copy(digest.bytes.begin(), digest.bytes.end(), output.begin() + 8);
}

[[nodiscard]] ContentChunkRef decode_chunk_entry(
    std::span<const std::byte,
              PagedContentManifestMetadata::kChunkEntryBytes> input,
    std::uint64_t index,
    std::uint64_t artifact_offset) {
    const auto length = load_le<std::uint32_t>(input.data());
    const auto flags = load_le<std::uint32_t>(input.data() + 4U);
    if (flags != kPagedEntryFlags) {
        throw std::runtime_error("paged content has unsupported chunk-entry flags");
    }
    ContentChunkRef result{
        .index = index,
        .artifact_offset = artifact_offset,
        .length = length,
    };
    std::copy_n(input.begin() + 8, result.digest.bytes.size(),
                result.digest.bytes.begin());
    return result;
}

void encode_page_header(
    const PagedContentPageRef& page,
    const Digest256& entries_digest,
    std::span<std::byte, PagedContentManifestMetadata::kPageHeaderBytes> output) {
    std::fill(output.begin(), output.end(), std::byte{0});
    std::copy(kPagedPageMagic.begin(), kPagedPageMagic.end(), output.begin());
    std::size_t offset = kPagedPageMagic.size();
    store_le<std::uint16_t>(output.data() + offset,
                            PagedContentManifestMetadata::kFormatVersion);
    offset += 2U;
    store_le<std::uint16_t>(
        output.data() + offset,
        static_cast<std::uint16_t>(PagedContentManifestMetadata::kPageHeaderBytes));
    offset += 2U;
    store_le<std::uint16_t>(
        output.data() + offset,
        static_cast<std::uint16_t>(PagedContentManifestMetadata::kChunkEntryBytes));
    offset += 2U;
    store_le<std::uint16_t>(output.data() + offset, kPagedFlags);
    offset += 2U;
    store_le<std::uint64_t>(output.data() + offset, page.page_index);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, page.first_chunk);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, page.artifact_offset);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, page.artifact_bytes);
    offset += 8U;
    store_le<std::uint32_t>(output.data() + offset, page.chunk_count);
    offset += 4U;
    offset += 4U; // reserved
    std::copy(entries_digest.bytes.begin(), entries_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
}

struct DecodedPageHeader {
    PagedContentPageRef page{};
    Digest256 entries_digest{};
};

[[nodiscard]] DecodedPageHeader decode_page_header(
    std::span<const std::byte, PagedContentManifestMetadata::kPageHeaderBytes> input) {
    if (!std::equal(kPagedPageMagic.begin(), kPagedPageMagic.end(), input.begin())) {
        throw std::runtime_error("invalid paged-content page magic");
    }
    std::size_t offset = kPagedPageMagic.size();
    const auto version = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    const auto header_bytes = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    const auto entry_bytes = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    const auto flags = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    if (version != PagedContentManifestMetadata::kFormatVersion ||
        header_bytes != PagedContentManifestMetadata::kPageHeaderBytes ||
        entry_bytes != PagedContentManifestMetadata::kChunkEntryBytes ||
        flags != kPagedFlags) {
        throw std::runtime_error("unsupported paged-content page format");
    }
    DecodedPageHeader result;
    result.page.page_index = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    result.page.first_chunk = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    result.page.artifact_offset = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    result.page.artifact_bytes = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    result.page.chunk_count = load_le<std::uint32_t>(input.data() + offset);
    offset += 4U;
    if (load_le<std::uint32_t>(input.data() + offset) != 0U) {
        throw std::runtime_error("paged-content page reserved bits are nonzero");
    }
    offset += 4U;
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                result.entries_digest.bytes.size(),
                result.entries_digest.bytes.begin());
    offset += result.entries_digest.bytes.size();
    if (!all_zero(input.subspan(offset))) {
        throw std::runtime_error("paged-content page reserved bytes are nonzero");
    }
    const auto body = checked_multiply(
        result.page.chunk_count,
        PagedContentManifestMetadata::kChunkEntryBytes,
        "paged-content page size overflows");
    const auto encoded = checked_add(
        PagedContentManifestMetadata::kPageHeaderBytes, body,
        "paged-content page size overflows");
    if (encoded > std::numeric_limits<std::uint32_t>::max()) {
        throw std::runtime_error("paged-content page encoded size exceeds 32 bits");
    }
    result.page.encoded_size = static_cast<std::uint32_t>(encoded);
    return result;
}

void encode_page_record(
    const PagedContentPageRef& page,
    std::span<std::byte, PagedContentManifestMetadata::kPageRecordBytes> output) {
    std::fill(output.begin(), output.end(), std::byte{0});
    std::size_t offset{};
    store_le<std::uint64_t>(output.data() + offset, page.page_index);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, page.first_chunk);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, page.artifact_offset);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, page.artifact_bytes);
    offset += 8U;
    store_le<std::uint32_t>(output.data() + offset, page.chunk_count);
    offset += 4U;
    store_le<std::uint32_t>(output.data() + offset, page.encoded_size);
    offset += 4U;
    std::copy(page.digest.bytes.begin(), page.digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
}

[[nodiscard]] PagedContentPageRef decode_page_record(
    std::span<const std::byte,
              PagedContentManifestMetadata::kPageRecordBytes> input) {
    PagedContentPageRef page;
    std::size_t offset{};
    page.page_index = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    page.first_chunk = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    page.artifact_offset = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    page.artifact_bytes = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    page.chunk_count = load_le<std::uint32_t>(input.data() + offset);
    offset += 4U;
    page.encoded_size = load_le<std::uint32_t>(input.data() + offset);
    offset += 4U;
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                page.digest.bytes.size(), page.digest.bytes.begin());
    offset += page.digest.bytes.size();
    if (!all_zero(input.subspan(offset))) {
        throw std::runtime_error("paged-content root record reserved bytes are nonzero");
    }
    return page;
}

void encode_root_header(
    const PagedContentManifestMetadata& metadata,
    std::span<std::byte, PagedContentManifestMetadata::kHeaderBytes> output) {
    std::fill(output.begin(), output.end(), std::byte{0});
    std::copy(kPagedRootMagic.begin(), kPagedRootMagic.end(), output.begin());
    std::size_t offset = kPagedRootMagic.size();
    store_le<std::uint16_t>(output.data() + offset,
                            PagedContentManifestMetadata::kFormatVersion);
    offset += 2U;
    store_le<std::uint16_t>(
        output.data() + offset,
        static_cast<std::uint16_t>(PagedContentManifestMetadata::kHeaderBytes));
    offset += 2U;
    store_le<std::uint16_t>(
        output.data() + offset,
        static_cast<std::uint16_t>(PagedContentManifestMetadata::kPageRecordBytes));
    offset += 2U;
    store_le<std::uint16_t>(output.data() + offset, kPagedFlags);
    offset += 2U;
    store_le<std::uint32_t>(output.data() + offset, metadata.chunking.min_bytes);
    offset += 4U;
    store_le<std::uint32_t>(output.data() + offset,
                            metadata.chunking.average_bytes);
    offset += 4U;
    store_le<std::uint32_t>(output.data() + offset, metadata.chunking.max_bytes);
    offset += 4U;
    store_le<std::uint32_t>(output.data() + offset, metadata.entries_per_page);
    offset += 4U;
    store_le<std::uint64_t>(output.data() + offset, metadata.artifact_size);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, metadata.chunk_count);
    offset += 8U;
    store_le<std::uint64_t>(output.data() + offset, metadata.page_count);
    offset += 8U;
    offset += 8U; // reserved
    std::copy(metadata.artifact_digest.bytes.begin(),
              metadata.artifact_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += metadata.artifact_digest.bytes.size();
    std::copy(metadata.chunk_entries_digest.bytes.begin(),
              metadata.chunk_entries_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += metadata.chunk_entries_digest.bytes.size();
    std::copy(metadata.page_records_digest.bytes.begin(),
              metadata.page_records_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
}

[[nodiscard]] PagedContentManifestMetadata decode_root_header(
    std::span<const std::byte, PagedContentManifestMetadata::kHeaderBytes> input,
    const ContentStoreLimits& limits) {
    if (!std::equal(kPagedRootMagic.begin(), kPagedRootMagic.end(), input.begin())) {
        throw std::runtime_error("invalid paged-content root magic");
    }
    std::size_t offset = kPagedRootMagic.size();
    const auto version = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    const auto header_bytes = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    const auto record_bytes = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    const auto flags = load_le<std::uint16_t>(input.data() + offset);
    offset += 2U;
    if (version != PagedContentManifestMetadata::kFormatVersion ||
        header_bytes != PagedContentManifestMetadata::kHeaderBytes ||
        record_bytes != PagedContentManifestMetadata::kPageRecordBytes ||
        flags != kPagedFlags) {
        throw std::runtime_error("unsupported paged-content root format");
    }

    PagedContentManifestMetadata metadata;
    metadata.chunking.min_bytes = load_le<std::uint32_t>(input.data() + offset);
    offset += 4U;
    metadata.chunking.average_bytes = load_le<std::uint32_t>(input.data() + offset);
    offset += 4U;
    metadata.chunking.max_bytes = load_le<std::uint32_t>(input.data() + offset);
    offset += 4U;
    metadata.entries_per_page = load_le<std::uint32_t>(input.data() + offset);
    offset += 4U;
    metadata.artifact_size = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    metadata.chunk_count = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    metadata.page_count = load_le<std::uint64_t>(input.data() + offset);
    offset += 8U;
    if (load_le<std::uint64_t>(input.data() + offset) != 0U) {
        throw std::runtime_error("paged-content root reserved bits are nonzero");
    }
    offset += 8U;
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.artifact_digest.bytes.size(),
                metadata.artifact_digest.bytes.begin());
    offset += metadata.artifact_digest.bytes.size();
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.chunk_entries_digest.bytes.size(),
                metadata.chunk_entries_digest.bytes.begin());
    offset += metadata.chunk_entries_digest.bytes.size();
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.page_records_digest.bytes.size(),
                metadata.page_records_digest.bytes.begin());
    offset += metadata.page_records_digest.bytes.size();
    if (!all_zero(input.subspan(offset))) {
        throw std::runtime_error("paged-content root reserved bytes are nonzero");
    }

    validate_chunking(metadata.chunking, limits);
    validate_entries_per_page(metadata.entries_per_page);
    if (metadata.artifact_size > limits.max_artifact_size ||
        metadata.chunk_count > limits.max_chunks) {
        throw std::runtime_error("paged-content root exceeds configured limits");
    }
    if ((metadata.artifact_size == 0U) != (metadata.chunk_count == 0U) ||
        (metadata.chunk_count == 0U) != (metadata.page_count == 0U)) {
        throw std::runtime_error("paged-content empty-artifact shape is invalid");
    }
    const auto expected_pages = ceiling_divide(
        metadata.chunk_count, metadata.entries_per_page);
    if (metadata.page_count != expected_pages) {
        throw std::runtime_error("paged-content root page count is inconsistent");
    }
    const auto encoded = checked_add(
        PagedContentManifestMetadata::kHeaderBytes,
        checked_multiply(metadata.page_count,
                         PagedContentManifestMetadata::kPageRecordBytes,
                         "paged-content root size overflows"),
        "paged-content root size overflows");
    if (encoded != metadata.encoded_size()) {
        throw std::runtime_error("paged-content root encoded size is inconsistent");
    }
    return metadata;
}

[[nodiscard]] PagedContentManifestMetadata quick_root_metadata(
    detail::NativeFile& root,
    const ContentStoreLimits& limits) {
    if (root.size() < PagedContentManifestMetadata::kHeaderBytes) {
        throw std::runtime_error("truncated paged-content root header");
    }
    std::array<std::byte, PagedContentManifestMetadata::kHeaderBytes> header{};
    root.read_exact_at(0U, header);
    auto metadata = decode_root_header(header, limits);
    if (root.size() != metadata.encoded_size()) {
        throw std::runtime_error("paged-content root length does not match page count");
    }
    return metadata;
}

struct FlatQuickMetadata {
    ContentChunking chunking{};
    std::uint64_t artifact_size{};
    std::uint64_t chunk_count{};
    Digest256 artifact_digest{};
};

[[nodiscard]] FlatQuickMetadata quick_flat_metadata(
    detail::NativeFile& manifest,
    const ContentStoreLimits& limits) {
    if (manifest.size() < ContentManifestMetadata::kHeaderBytes) {
        throw std::runtime_error("truncated flat content manifest");
    }
    std::array<std::byte, ContentManifestMetadata::kHeaderBytes> header{};
    manifest.read_exact_at(0U, header);
    if (!std::equal(kFlatManifestMagic.begin(), kFlatManifestMagic.end(),
                    header.begin())) {
        throw std::runtime_error("invalid flat content manifest magic");
    }
    std::size_t offset = kFlatManifestMagic.size();
    const auto version = load_le<std::uint16_t>(header.data() + offset);
    offset += 2U;
    const auto header_bytes = load_le<std::uint16_t>(header.data() + offset);
    offset += 2U;
    const auto entry_bytes = load_le<std::uint16_t>(header.data() + offset);
    offset += 2U;
    const auto flags = load_le<std::uint16_t>(header.data() + offset);
    offset += 2U;
    if (version != ContentManifestMetadata::kFormatVersion ||
        header_bytes != ContentManifestMetadata::kHeaderBytes ||
        entry_bytes != ContentManifestMetadata::kEntryBytes || flags != 0U) {
        throw std::runtime_error("unsupported flat content manifest format");
    }
    FlatQuickMetadata metadata;
    metadata.chunking.min_bytes = load_le<std::uint32_t>(header.data() + offset);
    offset += 4U;
    metadata.chunking.average_bytes = load_le<std::uint32_t>(header.data() + offset);
    offset += 4U;
    metadata.chunking.max_bytes = load_le<std::uint32_t>(header.data() + offset);
    offset += 4U;
    if (load_le<std::uint32_t>(header.data() + offset) != 0U) {
        throw std::runtime_error("flat content manifest reserved bits are nonzero");
    }
    offset += 4U;
    metadata.artifact_size = load_le<std::uint64_t>(header.data() + offset);
    offset += 8U;
    metadata.chunk_count = load_le<std::uint64_t>(header.data() + offset);
    offset += 8U;
    std::copy_n(header.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.artifact_digest.bytes.size(),
                metadata.artifact_digest.bytes.begin());
    validate_chunking(metadata.chunking, limits);
    if (metadata.artifact_size > limits.max_artifact_size ||
        metadata.chunk_count > limits.max_chunks) {
        throw std::runtime_error("flat content manifest exceeds configured limits");
    }
    const auto expected = checked_add(
        ContentManifestMetadata::kHeaderBytes,
        checked_multiply(metadata.chunk_count,
                         ContentManifestMetadata::kEntryBytes,
                         "flat content manifest size overflows"),
        "flat content manifest size overflows");
    if (manifest.size() != expected) {
        throw std::runtime_error("flat content manifest length is inconsistent");
    }
    return metadata;
}

template <typename Visitor>
[[nodiscard]] PagedContentManifestMetadata stream_root(
    const std::filesystem::path& root_path,
    std::span<std::byte> record_buffer,
    const ContentStoreLimits& limits,
    Visitor&& visitor) {
    if (record_buffer.size() < PagedContentManifestMetadata::kPageRecordBytes) {
        throw std::invalid_argument("paged-content root record buffer is too small");
    }
    const auto usable =
        (record_buffer.size() / PagedContentManifestMetadata::kPageRecordBytes) *
        PagedContentManifestMetadata::kPageRecordBytes;
    record_buffer = record_buffer.first(usable);

    detail::NativeFile root(root_path, detail::NativeOpenMode::read_only);
    root.advise_sequential();
    std::array<std::byte, PagedContentManifestMetadata::kHeaderBytes> header{};
    root.read_exact_at(0U, header);
    auto metadata = decode_root_header(header, limits);
    if (root.size() != metadata.encoded_size()) {
        throw std::runtime_error("paged-content root length does not match page count");
    }

    detail::ArtifactSha256 records_hasher;
    detail::ArtifactSha256 root_hasher;
    root_hasher.update(header);
    std::uint64_t page_index{};
    std::uint64_t expected_chunk{};
    std::uint64_t expected_offset{};
    std::uint64_t file_offset = PagedContentManifestMetadata::kHeaderBytes;
    while (page_index < metadata.page_count) {
        const auto capacity =
            record_buffer.size() /
            PagedContentManifestMetadata::kPageRecordBytes;
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(metadata.page_count - page_index, capacity));
        const auto bytes_count =
            count * PagedContentManifestMetadata::kPageRecordBytes;
        auto bytes = record_buffer.first(bytes_count);
        root.read_exact_at(file_offset, bytes);
        records_hasher.update(bytes);
        root_hasher.update(bytes);
        for (std::size_t local = 0U; local < count; ++local) {
            const auto* pointer = bytes.data() +
                local * PagedContentManifestMetadata::kPageRecordBytes;
            const auto page = decode_page_record(
                std::span<const std::byte,
                          PagedContentManifestMetadata::kPageRecordBytes>(
                    pointer, PagedContentManifestMetadata::kPageRecordBytes));
            const auto global_page = page_index + local;
            const auto expected_page_size = checked_add(
                PagedContentManifestMetadata::kPageHeaderBytes,
                checked_multiply(page.chunk_count,
                    PagedContentManifestMetadata::kChunkEntryBytes,
                    "paged-content page record size overflows"),
                "paged-content page record size overflows");
            if (page.page_index != global_page ||
                page.first_chunk != expected_chunk ||
                page.artifact_offset != expected_offset ||
                page.chunk_count == 0U ||
                page.chunk_count > metadata.entries_per_page ||
                page.encoded_size != expected_page_size ||
                page.artifact_bytes == 0U || all_zero(page.digest.bytes)) {
                throw std::runtime_error("paged-content root contains an invalid page record");
            }
            if (global_page + 1U < metadata.page_count &&
                page.chunk_count != metadata.entries_per_page) {
                throw std::runtime_error("non-final paged-content page is not full");
            }
            if (expected_chunk > metadata.chunk_count - page.chunk_count ||
                expected_offset > metadata.artifact_size - page.artifact_bytes) {
                throw std::runtime_error("paged-content page coverage exceeds root totals");
            }
            visitor(page);
            expected_chunk += page.chunk_count;
            expected_offset += page.artifact_bytes;
        }
        page_index += count;
        file_offset += bytes_count;
    }
    if (expected_chunk != metadata.chunk_count ||
        expected_offset != metadata.artifact_size) {
        throw std::runtime_error("paged-content page coverage does not equal root totals");
    }
    if (records_hasher.finish() != metadata.page_records_digest) {
        throw std::runtime_error("paged-content root record digest mismatch");
    }
    metadata.root_digest = root_hasher.finish();
    return metadata;
}

template <typename Visitor>
void stream_page(const std::filesystem::path& page_path,
                 const PagedContentPageRef& expected,
                 const PagedContentManifestMetadata& root_metadata,
                 std::span<std::byte> entry_buffer,
                 bool verify_page_digest,
                 Visitor&& visitor) {
    if (entry_buffer.size() < PagedContentManifestMetadata::kChunkEntryBytes) {
        throw std::invalid_argument("paged-content entry buffer is too small");
    }
    const auto usable =
        (entry_buffer.size() / PagedContentManifestMetadata::kChunkEntryBytes) *
        PagedContentManifestMetadata::kChunkEntryBytes;
    entry_buffer = entry_buffer.first(usable);

    detail::NativeFile page_file(page_path, detail::NativeOpenMode::read_only);
    if (page_file.size() != expected.encoded_size) {
        throw std::runtime_error("paged-content page has the wrong size");
    }
    std::array<std::byte, PagedContentManifestMetadata::kPageHeaderBytes> header{};
    page_file.read_exact_at(0U, header);
    const auto decoded = decode_page_header(header);
    if (decoded.page.page_index != expected.page_index ||
        decoded.page.first_chunk != expected.first_chunk ||
        decoded.page.artifact_offset != expected.artifact_offset ||
        decoded.page.artifact_bytes != expected.artifact_bytes ||
        decoded.page.chunk_count != expected.chunk_count ||
        decoded.page.encoded_size != expected.encoded_size) {
        throw std::runtime_error("paged-content page header disagrees with root record");
    }

    detail::ArtifactSha256 entries_hasher;
    detail::ArtifactSha256 page_hasher;
    page_hasher.update(header);
    std::uint64_t local_index{};
    std::uint64_t artifact_offset = expected.artifact_offset;
    std::uint64_t page_bytes{};
    std::uint64_t file_offset = PagedContentManifestMetadata::kPageHeaderBytes;
    while (local_index < expected.chunk_count) {
        const auto capacity =
            entry_buffer.size() /
            PagedContentManifestMetadata::kChunkEntryBytes;
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(expected.chunk_count - local_index, capacity));
        const auto bytes_count =
            count * PagedContentManifestMetadata::kChunkEntryBytes;
        auto bytes = entry_buffer.first(bytes_count);
        page_file.read_exact_at(file_offset, bytes);
        entries_hasher.update(bytes);
        page_hasher.update(bytes);
        for (std::size_t local = 0U; local < count; ++local) {
            const auto index = local_index + local;
            const auto* pointer = bytes.data() +
                local * PagedContentManifestMetadata::kChunkEntryBytes;
            const auto chunk = decode_chunk_entry(
                std::span<const std::byte,
                          PagedContentManifestMetadata::kChunkEntryBytes>(
                    pointer, PagedContentManifestMetadata::kChunkEntryBytes),
                expected.first_chunk + index, artifact_offset);
            if (chunk.length == 0U ||
                chunk.length > root_metadata.chunking.max_bytes ||
                (chunk.index + 1U < root_metadata.chunk_count &&
                 chunk.length < root_metadata.chunking.min_bytes) ||
                artifact_offset > root_metadata.artifact_size - chunk.length) {
                throw std::runtime_error("paged-content page contains invalid chunk length");
            }
            visitor(chunk);
            artifact_offset += chunk.length;
            page_bytes += chunk.length;
        }
        local_index += count;
        file_offset += bytes_count;
    }
    if (page_bytes != expected.artifact_bytes ||
        entries_hasher.finish() != decoded.entries_digest) {
        throw std::runtime_error("paged-content page coverage or entry digest mismatch");
    }
    const auto digest = page_hasher.finish();
    if (verify_page_digest && digest != expected.digest) {
        throw std::runtime_error("paged-content page digest mismatch");
    }
}

[[nodiscard]] PagedContentPageRef read_page_record_at(
    detail::NativeFile& root,
    const PagedContentManifestMetadata& metadata,
    std::uint64_t page_index) {
    if (page_index >= metadata.page_count) {
        throw std::out_of_range("paged-content page index is outside root");
    }
    std::array<std::byte, PagedContentManifestMetadata::kPageRecordBytes> bytes{};
    const auto offset = checked_add(
        PagedContentManifestMetadata::kHeaderBytes,
        checked_multiply(page_index,
                         PagedContentManifestMetadata::kPageRecordBytes,
                         "paged-content page-record offset overflows"),
        "paged-content page-record offset overflows");
    root.read_exact_at(offset, bytes);
    auto page = decode_page_record(bytes);
    if (page.page_index != page_index || page.chunk_count == 0U ||
        page.chunk_count > metadata.entries_per_page ||
        all_zero(page.digest.bytes)) {
        throw std::runtime_error("paged-content direct page record is invalid");
    }
    return page;
}

void set_bit(std::span<std::byte> bits,
             std::uint32_t index,
             bool value) noexcept {
    const auto byte_index = static_cast<std::size_t>(index / 8U);
    const auto bit_index = static_cast<unsigned>(index % 8U);
    const auto mask = static_cast<unsigned char>(1U << bit_index);
    auto byte = std::to_integer<unsigned char>(bits[byte_index]);
    if (value) {
        byte = static_cast<unsigned char>(byte | mask);
    } else {
        byte = static_cast<unsigned char>(
            byte & static_cast<unsigned char>(~mask));
    }
    bits[byte_index] = static_cast<std::byte>(byte);
}

} // namespace

std::uint64_t PagedContentManifestMetadata::encoded_size() const noexcept {
    return static_cast<std::uint64_t>(kHeaderBytes) +
           page_count * static_cast<std::uint64_t>(kPageRecordBytes);
}

ContentManifestFormat detect_content_manifest_format(
    const std::filesystem::path& manifest_path) {
    detail::NativeFile input(manifest_path, detail::NativeOpenMode::read_only);
    if (input.size() < 8U) {
        throw std::runtime_error("content manifest is too small to identify");
    }
    std::array<std::byte, 8> magic{};
    input.read_exact_at(0U, magic);
    if (magic == kFlatManifestMagic) return ContentManifestFormat::flat_v1;
    if (magic == kPagedRootMagic) return ContentManifestFormat::paged_v2;
    throw std::runtime_error("unknown toxsync content manifest format");
}

PagedContentScaleEstimate estimate_paged_content_scale(
    std::uint64_t artifact_size,
    const PagedContentStoreOptions& options) {
    if (artifact_size > options.limits.max_artifact_size) {
        throw std::invalid_argument("paged-content artifact exceeds configured limit");
    }
    validate_chunking(options.chunking, options.limits);
    validate_entries_per_page(options.entries_per_page);
    if (options.root_metadata_budget_bytes <
        PagedContentManifestMetadata::kHeaderBytes) {
        throw std::invalid_argument("paged-content root budget is smaller than header");
    }
    const auto max_pages_by_budget =
        (options.root_metadata_budget_bytes -
         PagedContentManifestMetadata::kHeaderBytes) /
        PagedContentManifestMetadata::kPageRecordBytes;
    if (artifact_size != 0U && max_pages_by_budget == 0U) {
        throw std::invalid_argument("paged-content root budget cannot hold one page");
    }
    const auto max_chunks_by_budget = checked_multiply(
        max_pages_by_budget, options.entries_per_page,
        "paged-content root budget chunk count overflows");
    const auto maximum_chunks =
        std::min(max_chunks_by_budget, options.limits.max_chunks);
    if (artifact_size != 0U && maximum_chunks == 0U) {
        throw std::invalid_argument("paged-content configured chunk limit is zero");
    }

    ContentChunking selected = options.chunking;
    const auto preferred_worst = ceiling_divide(
        artifact_size, options.chunking.min_bytes);
    if (preferred_worst > maximum_chunks) {
        const auto required_min = ceiling_divide(artifact_size, maximum_chunks);
        const auto rounded = next_power_of_two(
            std::max<std::uint64_t>(required_min, options.chunking.min_bytes));
        if (rounded > options.limits.max_chunk_bytes ||
            rounded > std::numeric_limits<std::uint32_t>::max()) {
            throw std::invalid_argument(
                "paged-content root budget cannot be met within chunk limits");
        }
        selected.min_bytes = static_cast<std::uint32_t>(rounded);
        auto average = std::max<std::uint64_t>(
            rounded, options.chunking.average_bytes);
        if (!std::has_single_bit(average)) average = std::bit_ceil(average);
        average = std::min<std::uint64_t>(average,
                                          options.limits.max_chunk_bytes);
        if (!std::has_single_bit(average)) average = std::bit_floor(average);
        if (average < rounded) average = rounded;
        selected.average_bytes = static_cast<std::uint32_t>(average);
        auto maximum = std::max<std::uint64_t>(
            selected.average_bytes, options.chunking.max_bytes);
        maximum = std::min<std::uint64_t>(maximum,
                                          options.limits.max_chunk_bytes);
        selected.max_bytes = static_cast<std::uint32_t>(maximum);
    }
    validate_chunking(selected, options.limits);
    const auto chunks = ceiling_divide(artifact_size, selected.min_bytes);
    const auto pages = ceiling_divide(chunks, options.entries_per_page);
    const auto root_bytes = checked_add(
        PagedContentManifestMetadata::kHeaderBytes,
        checked_multiply(pages,
                         PagedContentManifestMetadata::kPageRecordBytes,
                         "paged-content root size overflows"),
        "paged-content root size overflows");
    if (chunks > options.limits.max_chunks ||
        root_bytes > options.root_metadata_budget_bytes) {
        throw std::invalid_argument("paged-content scale exceeds configured budget");
    }
    const auto page_headers = checked_multiply(
        pages, PagedContentManifestMetadata::kPageHeaderBytes,
        "paged-content distributed metadata overflows");
    const auto chunk_entries = checked_multiply(
        chunks, PagedContentManifestMetadata::kChunkEntryBytes,
        "paged-content distributed metadata overflows");
    const auto distributed = checked_add(
        root_bytes, checked_add(page_headers, chunk_entries,
                                "paged-content distributed metadata overflows"),
        "paged-content distributed metadata overflows");
    return PagedContentScaleEstimate{
        .artifact_size = artifact_size,
        .chunking = selected,
        .entries_per_page = options.entries_per_page,
        .maximum_chunks = chunks,
        .maximum_pages = pages,
        .maximum_root_bytes = root_bytes,
        .maximum_distributed_metadata_bytes = distributed,
    };
}

PagedContentStoreBuildStats build_paged_content_store(
    const std::filesystem::path& artifact,
    const std::filesystem::path& store_root,
    const std::filesystem::path& root_manifest_path,
    const PagedContentStoreOptions& options) {
    ContentStoreWorkspace workspace;
    return build_paged_content_store(
        artifact, store_root, root_manifest_path, workspace, options);
}

PagedContentStoreBuildStats build_paged_content_store(
    const std::filesystem::path& artifact,
    const std::filesystem::path& store_root,
    const std::filesystem::path& root_manifest_path,
    ContentStoreWorkspace& workspace,
    const PagedContentStoreOptions& options) {
    detail::NativeFile input(artifact, detail::NativeOpenMode::read_only);
    if (options.advise_sequential_io) input.advise_sequential();
    const auto input_size = input.size();
    if (input_size > options.limits.max_artifact_size) {
        throw std::runtime_error("paged-content artifact exceeds configured limit");
    }
    validate_entries_per_page(options.entries_per_page);
    ContentChunking chunking = options.chunking;
    if (options.auto_chunking) {
        chunking = estimate_paged_content_scale(input_size, options).chunking;
    } else {
        validate_chunking(chunking, options.limits);
        auto scale_options = options;
        scale_options.chunking = chunking;
        (void)estimate_paged_content_scale(input_size, scale_options);
    }

    const auto io_bytes = normalized_io_bytes(options.io_buffer_bytes);
    const auto root_buffer_bytes = normalized_root_buffer(options.root_buffer_bytes);
    const auto page_capacity_u64 = checked_add(
        PagedContentManifestMetadata::kPageHeaderBytes,
        checked_multiply(options.entries_per_page,
                         PagedContentManifestMetadata::kChunkEntryBytes,
                         "paged-content page buffer overflows"),
        "paged-content page buffer overflows");
    if (page_capacity_u64 > std::numeric_limits<std::size_t>::max() ||
        page_capacity_u64 > std::numeric_limits<std::uint32_t>::max()) {
        throw std::length_error("paged-content page buffer exceeds this platform");
    }
    const auto page_capacity = static_cast<std::size_t>(page_capacity_u64);
    if (page_capacity >
        std::numeric_limits<std::size_t>::max() - root_buffer_bytes) {
        throw std::length_error("paged-content combined record workspace overflows");
    }

    std::uint32_t growth_events{};
    auto io = PagedContentWorkspaceAccess::prepare_io(
        workspace, io_bytes, growth_events);
    auto chunk = PagedContentWorkspaceAccess::prepare_chunk(
        workspace, static_cast<std::size_t>(chunking.max_bytes), growth_events);
    auto record_arena = PagedContentWorkspaceAccess::prepare_records(
        workspace, page_capacity + root_buffer_bytes, growth_events);
    auto page_bytes = record_arena.first(page_capacity);
    auto root_records = record_arena.subspan(page_capacity, root_buffer_bytes);

    ensure_parent(root_manifest_path);
    const auto part_path = part_path_for(root_manifest_path);
    TemporaryPath root_part(part_path);
    detail::NativeFile root(part_path, detail::NativeOpenMode::read_write_truncate);
    root.resize(PagedContentManifestMetadata::kHeaderBytes);

    PagedContentStoreBuildStats stats;
    stats.metadata.chunking = chunking;
    stats.metadata.entries_per_page = options.entries_per_page;
    stats.metadata.artifact_size = input_size;
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();

    detail::ArtifactSha256 artifact_hasher;
    detail::ArtifactSha256 chunk_entries_hasher;
    detail::ArtifactSha256 page_records_hasher;
    detail::ArtifactSha256 page_entries_hasher;
    GearChunker chunker(chunking);
    std::size_t chunk_used{};
    std::uint32_t page_chunk_count{};
    std::uint64_t page_first_chunk{};
    std::uint64_t page_artifact_offset{};
    std::uint64_t page_artifact_bytes{};
    std::size_t root_records_used{};
    std::uint64_t root_file_offset = PagedContentManifestMetadata::kHeaderBytes;
    std::uint64_t input_offset{};
    std::uint64_t artifact_emitted{};

    const auto flush_root_records = [&]() {
        if (root_records_used == 0U) return;
        root.write_exact_at(root_file_offset,
                            root_records.first(root_records_used));
        root_file_offset += root_records_used;
        root_records_used = 0U;
        ++stats.root_write_calls;
    };

    const auto flush_page = [&]() {
        if (page_chunk_count == 0U) return;
        const auto encoded_size_u64 = checked_add(
            PagedContentManifestMetadata::kPageHeaderBytes,
            checked_multiply(page_chunk_count,
                             PagedContentManifestMetadata::kChunkEntryBytes,
                             "paged-content page encoded size overflows"),
            "paged-content page encoded size overflows");
        const auto encoded_size = static_cast<std::uint32_t>(encoded_size_u64);
        PagedContentPageRef page{
            .page_index = stats.metadata.page_count,
            .first_chunk = page_first_chunk,
            .artifact_offset = page_artifact_offset,
            .artifact_bytes = page_artifact_bytes,
            .chunk_count = page_chunk_count,
            .encoded_size = encoded_size,
        };
        const auto entries_digest = page_entries_hasher.finish();
        encode_page_header(
            page, entries_digest,
            std::span<std::byte,
                      PagedContentManifestMetadata::kPageHeaderBytes>(
                page_bytes.data(),
                PagedContentManifestMetadata::kPageHeaderBytes));
        const auto encoded = page_bytes.first(encoded_size);
        page.digest = sha256(encoded);
        const bool created = store_bytes(
            store_root, page.digest, encoded, options.fsync_on_commit,
            options.verify_existing_objects, io);
        if (created) {
            ++stats.pages_created;
            stats.page_bytes_created += encoded.size();
        } else {
            ++stats.pages_reused;
            stats.page_bytes_reused += encoded.size();
        }

        if (root_records_used + PagedContentManifestMetadata::kPageRecordBytes >
            root_records.size()) {
            flush_root_records();
        }
        auto record = std::span<std::byte,
            PagedContentManifestMetadata::kPageRecordBytes>(
                root_records.data() + root_records_used,
                PagedContentManifestMetadata::kPageRecordBytes);
        encode_page_record(page, record);
        page_records_hasher.update(record);
        root_records_used += PagedContentManifestMetadata::kPageRecordBytes;
        ++stats.metadata.page_count;
        page_chunk_count = 0U;
        page_artifact_bytes = 0U;
        page_entries_hasher = detail::ArtifactSha256{};
    };

    const auto emit_chunk = [&](std::span<const std::byte> bytes) {
        if (bytes.empty()) return;
        if (stats.metadata.chunk_count >= options.limits.max_chunks) {
            throw std::runtime_error("paged-content artifact exceeds chunk-count limit");
        }
        if (page_chunk_count == 0U) {
            page_first_chunk = stats.metadata.chunk_count;
            page_artifact_offset = artifact_emitted;
        }
        const auto digest = sha256(bytes);
        const bool created = store_bytes(
            store_root, digest, bytes, options.fsync_on_commit,
            options.verify_existing_objects, io);
        if (created) {
            ++stats.chunks_created;
            stats.chunk_bytes_created += bytes.size();
        } else {
            ++stats.chunks_reused;
            stats.chunk_bytes_reused += bytes.size();
        }
        const auto entry_offset =
            PagedContentManifestMetadata::kPageHeaderBytes +
            static_cast<std::size_t>(page_chunk_count) *
                PagedContentManifestMetadata::kChunkEntryBytes;
        auto entry = std::span<std::byte,
            PagedContentManifestMetadata::kChunkEntryBytes>(
                page_bytes.data() + entry_offset,
                PagedContentManifestMetadata::kChunkEntryBytes);
        encode_chunk_entry(entry, static_cast<std::uint32_t>(bytes.size()), digest);
        chunk_entries_hasher.update(entry);
        page_entries_hasher.update(entry);
        ++page_chunk_count;
        ++stats.metadata.chunk_count;
        page_artifact_bytes += bytes.size();
        artifact_emitted += bytes.size();
        if (page_chunk_count == options.entries_per_page) flush_page();
    };

    while (input_offset < input_size) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(input_size - input_offset, io.size()));
        auto input_bytes = io.first(count);
        input.read_exact_at(input_offset, input_bytes);
        ++stats.input_read_calls;
        artifact_hasher.update(input_bytes);
        std::size_t segment_start{};
        for (std::size_t index = 0U; index < input_bytes.size(); ++index) {
            if (!chunker.push(input_bytes[index])) continue;
            const auto segment_length = index + 1U - segment_start;
            if (segment_length > chunk.size() - chunk_used) {
                throw std::runtime_error("paged-content chunker exceeded maximum size");
            }
            std::memcpy(chunk.data() + chunk_used,
                        input_bytes.data() + segment_start,
                        segment_length);
            chunk_used += segment_length;
            emit_chunk(std::span<const std::byte>(chunk.data(), chunk_used));
            chunk_used = 0U;
            chunker.reset();
            segment_start = index + 1U;
        }
        const auto tail = input_bytes.size() - segment_start;
        if (tail > chunk.size() - chunk_used) {
            throw std::runtime_error("paged-content chunk buffer overflow");
        }
        if (tail != 0U) {
            std::memcpy(chunk.data() + chunk_used,
                        input_bytes.data() + segment_start, tail);
            chunk_used += tail;
        }
        if (options.discard_input_cache) {
            input.advise_dont_need(input_offset, count);
        }
        input_offset += count;
    }
    if (chunk_used != 0U) {
        emit_chunk(std::span<const std::byte>(chunk.data(), chunk_used));
    }
    flush_page();
    flush_root_records();
    if (input.size() != input_size || artifact_emitted != input_size) {
        throw std::runtime_error("paged-content artifact changed during build");
    }

    stats.metadata.artifact_digest = artifact_hasher.finish();
    stats.metadata.chunk_entries_digest = chunk_entries_hasher.finish();
    stats.metadata.page_records_digest = page_records_hasher.finish();
    const auto scale = estimate_paged_content_scale(input_size, [&] {
        auto effective = options;
        effective.chunking = chunking;
        effective.auto_chunking = false;
        return effective;
    }());
    if (stats.metadata.page_count > scale.maximum_pages ||
        stats.metadata.encoded_size() > options.root_metadata_budget_bytes) {
        throw std::runtime_error("paged-content build exceeded root metadata budget");
    }

    std::array<std::byte, PagedContentManifestMetadata::kHeaderBytes> header{};
    encode_root_header(stats.metadata, header);
    root.write_exact_at(0U, header);
    ++stats.root_write_calls;
    root.resize(stats.metadata.encoded_size());
    if (options.fsync_on_commit) root.sync();
    root.close();
    atomic_replace(part_path, root_manifest_path);
    root_part.disarm();
    if (options.fsync_on_commit) sync_parent(root_manifest_path);

    detail::NativeFile final_root(
        root_manifest_path, detail::NativeOpenMode::read_only);
    stats.metadata.root_digest = hash_native_file(
        final_root, io, stats.metadata.encoded_size());
    final_root.close();
    if (options.publish_root_to_store) {
        (void)store_file(
            store_root, root_manifest_path, stats.metadata.root_digest,
            stats.metadata.encoded_size(), io, options.fsync_on_commit,
            options.verify_existing_objects);
    }
    return stats;
}

PagedContentManifestMetadata inspect_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const ContentStoreLimits& limits) {
    ContentStoreWorkspace workspace;
    return inspect_paged_content_manifest(root_manifest_path, workspace, limits);
}

PagedContentManifestMetadata inspect_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    ContentStoreWorkspace& workspace,
    const ContentStoreLimits& limits) {
    std::uint32_t growth_events{};
    auto records = PagedContentWorkspaceAccess::prepare_records(
        workspace, kDefaultManifestBuffer, growth_events);
    (void)growth_events;
    return stream_root(root_manifest_path, records, limits,
                       [](const PagedContentPageRef&) {});
}

PagedContentManifestWalkStats walk_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    PagedContentPageCallback page_callback,
    void* page_context,
    ContentChunkCallback chunk_callback,
    void* chunk_context,
    const PagedContentManifestWalkOptions& options) {
    ContentStoreWorkspace workspace;
    return walk_paged_content_manifest(
        root_manifest_path, store_root, workspace, page_callback, page_context,
        chunk_callback, chunk_context, options);
}

PagedContentManifestWalkStats walk_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    PagedContentPageCallback page_callback,
    void* page_context,
    ContentChunkCallback chunk_callback,
    void* chunk_context,
    const PagedContentManifestWalkOptions& options) {
    const auto nested_buffer_bytes =
        normalized_entry_buffer(options.manifest_buffer_bytes);
    if (nested_buffer_bytes >
        std::numeric_limits<std::size_t>::max() - nested_buffer_bytes) {
        throw std::length_error(
            "paged-content nested walk buffers overflow this platform");
    }
    std::uint32_t growth_events{};
    auto record_arena = PagedContentWorkspaceAccess::prepare_records(
        workspace, nested_buffer_bytes * 2U, growth_events);
    auto root_records = record_arena.first(nested_buffer_bytes);
    auto page_entries = record_arena.subspan(
        nested_buffer_bytes, nested_buffer_bytes);

    PagedContentManifestWalkStats stats;
    stats.metadata = stream_root(
        root_manifest_path, root_records, options.limits,
        [](const PagedContentPageRef&) {});
    stats.distributed_metadata_bytes = stats.metadata.encoded_size();
    (void)stream_root(
        root_manifest_path, root_records, options.limits,
        [&](const PagedContentPageRef& page) {
            if (page_callback != nullptr) page_callback(page_context, page);
            const auto page_path = content_store_path(store_root, page.digest);
            stream_page(
                page_path, page, stats.metadata, page_entries,
                options.verify_page_digests,
                [&](const ContentChunkRef& chunk) {
                    if (chunk_callback != nullptr) {
                        chunk_callback(chunk_context, chunk);
                    }
                    ++stats.chunks_visited;
                    stats.artifact_bytes_visited += chunk.length;
                });
            ++stats.pages_visited;
            stats.distributed_metadata_bytes += page.encoded_size;
        });
    if (stats.pages_visited != stats.metadata.page_count ||
        stats.chunks_visited != stats.metadata.chunk_count ||
        stats.artifact_bytes_visited != stats.metadata.artifact_size) {
        throw std::runtime_error(
            "paged-content walk coverage does not match root metadata");
    }
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

PagedContentPageWindowStats read_paged_content_page_window(
    const std::filesystem::path& root_manifest_path,
    std::uint64_t first_page,
    std::span<PagedContentPageRef> output,
    const PagedContentPageWindowOptions& options) {
    ContentStoreWorkspace workspace;
    return read_paged_content_page_window(
        root_manifest_path, first_page, output, workspace, options);
}

PagedContentPageWindowStats read_paged_content_page_window(
    const std::filesystem::path& root_manifest_path,
    std::uint64_t first_page,
    std::span<PagedContentPageRef> output,
    ContentStoreWorkspace& workspace,
    const PagedContentPageWindowOptions& options) {
    if (output.empty()) {
        throw std::invalid_argument("paged-content page window output is empty");
    }
    if (output.size() > std::numeric_limits<std::uint32_t>::max()) {
        throw std::length_error("paged-content page window exceeds 32-bit count");
    }
    std::uint32_t growth_events{};
    detail::NativeFile root(root_manifest_path, detail::NativeOpenMode::read_only);
    auto metadata = quick_root_metadata(root, options.limits);
    if (options.verify_root_manifest) {
        metadata = inspect_paged_content_manifest(
            root_manifest_path, workspace, options.limits);
    }
    // Verification uses the same reusable record arena and may grow it. Acquire
    // the page-window span only after verification so it cannot dangle.
    auto records = PagedContentWorkspaceAccess::prepare_records(
        workspace, normalized_root_buffer(options.root_buffer_bytes),
        growth_events);
    if (first_page > metadata.page_count) {
        throw std::out_of_range("paged-content page window begins after root");
    }

    PagedContentPageWindowStats stats;
    stats.metadata = metadata;
    stats.first_page = first_page;
    stats.next_page = first_page;
    if (first_page == metadata.page_count) {
        stats.workspace_growth_events = growth_events;
        stats.workspace_reserved_bytes = workspace.resident_bytes();
        return stats;
    }

    const auto target_count = static_cast<std::uint32_t>(
        std::min<std::uint64_t>(output.size(), metadata.page_count - first_page));
    std::uint64_t loaded{};
    std::uint64_t file_offset = checked_add(
        PagedContentManifestMetadata::kHeaderBytes,
        checked_multiply(first_page,
                         PagedContentManifestMetadata::kPageRecordBytes,
                         "paged-content page-window offset overflows"),
        "paged-content page-window offset overflows");
    std::uint64_t previous_end{};
    bool have_previous{};
    while (loaded < target_count) {
        const auto capacity = records.size() /
            PagedContentManifestMetadata::kPageRecordBytes;
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(target_count - loaded, capacity));
        const auto byte_count = count *
            PagedContentManifestMetadata::kPageRecordBytes;
        auto bytes = records.first(byte_count);
        root.read_exact_at(file_offset, bytes);
        for (std::size_t local = 0U; local < count; ++local) {
            const auto page_index = first_page + loaded + local;
            const auto* pointer = bytes.data() +
                local * PagedContentManifestMetadata::kPageRecordBytes;
            const auto page = decode_page_record(
                std::span<const std::byte,
                          PagedContentManifestMetadata::kPageRecordBytes>(
                    pointer, PagedContentManifestMetadata::kPageRecordBytes));
            const auto expected_first = checked_multiply(
                page_index, metadata.entries_per_page,
                "paged-content page-window chunk index overflows");
            const auto expected_count = static_cast<std::uint32_t>(
                std::min<std::uint64_t>(metadata.entries_per_page,
                                        metadata.chunk_count - expected_first));
            const auto expected_encoded = checked_add(
                PagedContentManifestMetadata::kPageHeaderBytes,
                checked_multiply(expected_count,
                                 PagedContentManifestMetadata::kChunkEntryBytes,
                                 "paged-content page-window page size overflows"),
                "paged-content page-window page size overflows");
            if (page.page_index != page_index ||
                page.first_chunk != expected_first ||
                page.chunk_count != expected_count ||
                page.encoded_size != expected_encoded ||
                page.artifact_bytes == 0U ||
                page.artifact_offset > metadata.artifact_size ||
                page.artifact_bytes >
                    metadata.artifact_size - page.artifact_offset ||
                all_zero(page.digest.bytes)) {
                throw std::runtime_error(
                    "paged-content page-window record violates root geometry");
            }
            if ((page_index == 0U && page.artifact_offset != 0U) ||
                (have_previous && page.artifact_offset != previous_end)) {
                throw std::runtime_error(
                    "paged-content page-window artifact coverage is discontinuous");
            }
            previous_end = page.artifact_offset + page.artifact_bytes;
            have_previous = true;
            if (page_index + 1U == metadata.page_count &&
                previous_end != metadata.artifact_size) {
                throw std::runtime_error(
                    "paged-content final page does not end at artifact size");
            }
            output[static_cast<std::size_t>(loaded) + local] = page;
            stats.distributed_metadata_bytes += page.encoded_size;
        }
        loaded += count;
        file_offset += byte_count;
    }
    stats.pages_loaded = target_count;
    stats.next_page = first_page + target_count;
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

PagedContentScanStats scan_missing_paged_content_chunks(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    MissingContentPageCallback page_callback,
    void* page_context,
    MissingContentChunkCallback chunk_callback,
    void* chunk_context,
    const PagedContentScanOptions& options) {
    ContentStoreWorkspace workspace;
    return scan_missing_paged_content_chunks(
        root_manifest_path, store_root, workspace,
        page_callback, page_context, chunk_callback, chunk_context, options);
}

PagedContentScanStats scan_missing_paged_content_chunks(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    MissingContentPageCallback page_callback,
    void* page_context,
    MissingContentChunkCallback chunk_callback,
    void* chunk_context,
    const PagedContentScanOptions& options) {
    std::uint32_t growth_events{};
    auto io = PagedContentWorkspaceAccess::prepare_io(
        workspace, normalized_io_bytes(options.io_buffer_bytes), growth_events);
    const auto nested_buffer_bytes =
        normalized_entry_buffer(options.manifest_buffer_bytes);
    if (nested_buffer_bytes >
        std::numeric_limits<std::size_t>::max() - nested_buffer_bytes) {
        throw std::length_error("paged-content nested manifest buffers overflow");
    }
    auto record_arena = PagedContentWorkspaceAccess::prepare_records(
        workspace, nested_buffer_bytes * 2U, growth_events);
    auto root_records = record_arena.first(nested_buffer_bytes);
    auto page_entries = record_arena.subspan(
        nested_buffer_bytes, nested_buffer_bytes);
    PagedContentScanStats stats;
    stats.metadata = stream_root(
        root_manifest_path, root_records, options.limits,
        [](const PagedContentPageRef&) {});
    (void)stream_root(
        root_manifest_path, root_records, options.limits,
        [&](const PagedContentPageRef& page) {
            const auto page_path = content_store_path(store_root, page.digest);
            bool available = regular_file_exact_size(page_path, page.encoded_size);
            bool corrupt = false;
            if (available && options.verify_page_digests) {
                available = verify_file(
                    page_path, page.digest, page.encoded_size, io);
                corrupt = !available;
            }
            if (!available) {
                ++stats.missing_pages;
                if (corrupt) ++stats.corrupt_pages;
                stats.unknown_chunks += page.chunk_count;
                stats.unknown_bytes += page.artifact_bytes;
                if (page_callback != nullptr) page_callback(page_context, page);
                return;
            }
            ++stats.available_pages;
            try {
                stream_page(
                    page_path, page, stats.metadata, page_entries,
                    options.verify_page_digests,
                    [&](const ContentChunkRef& chunk) {
                        const auto path = content_store_path(store_root, chunk.digest);
                        bool chunk_available = regular_file_exact_size(path, chunk.length);
                        bool chunk_corrupt = false;
                        if (chunk_available && options.verify_chunk_digests) {
                            chunk_available = verify_file(
                                path, chunk.digest, chunk.length, io);
                            chunk_corrupt = !chunk_available;
                        }
                        if (chunk_available) {
                            ++stats.available_chunks;
                            stats.available_bytes += chunk.length;
                        } else {
                            ++stats.missing_chunks;
                            stats.missing_bytes += chunk.length;
                            if (chunk_corrupt) ++stats.corrupt_chunks;
                            if (chunk_callback != nullptr) {
                                chunk_callback(chunk_context, chunk);
                            }
                        }
                    });
            } catch (...) {
                ++stats.corrupt_pages;
                --stats.available_pages;
                ++stats.missing_pages;
                stats.unknown_chunks += page.chunk_count;
                stats.unknown_bytes += page.artifact_bytes;
                if (page_callback != nullptr) page_callback(page_context, page);
            }
        });
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

ContentReconstructStats reconstruct_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    const ContentReconstructOptions& options) {
    ContentStoreWorkspace workspace;
    return reconstruct_paged_content_manifest(
        root_manifest_path, store_root, output_path, workspace, options);
}

ContentReconstructStats reconstruct_paged_content_manifest(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    ContentStoreWorkspace& workspace,
    const ContentReconstructOptions& options) {
    std::uint32_t growth_events{};
    auto io = PagedContentWorkspaceAccess::prepare_io(
        workspace, normalized_io_bytes(options.io_buffer_bytes), growth_events);
    const auto nested_buffer_bytes =
        normalized_entry_buffer(options.manifest_buffer_bytes);
    if (nested_buffer_bytes >
        std::numeric_limits<std::size_t>::max() - nested_buffer_bytes) {
        throw std::length_error("paged-content nested manifest buffers overflow");
    }
    auto record_arena = PagedContentWorkspaceAccess::prepare_records(
        workspace, nested_buffer_bytes * 2U, growth_events);
    auto root_records = record_arena.first(nested_buffer_bytes);
    auto page_entries = record_arena.subspan(
        nested_buffer_bytes, nested_buffer_bytes);

    ensure_parent(output_path);
    const auto part_path = part_path_for(output_path);
    TemporaryPath output_part(part_path);
    detail::NativeFile output(
        part_path, detail::NativeOpenMode::read_write_truncate);
    detail::ArtifactSha256 artifact_hasher;
    detail::ArtifactSha256 chunk_entries_hasher;
    ContentReconstructStats stats;
    try {
        throw_if_cancelled(options);
        const auto metadata = stream_root(
            root_manifest_path, root_records, options.limits,
            [](const PagedContentPageRef&) {});
        // Re-scan the small root records while streaming each page. The root is
        // bounded by policy and no page- or chunk-count-sized container lives
        // in memory.
        stats.metadata.chunking = metadata.chunking;
        stats.metadata.artifact_size = metadata.artifact_size;
        stats.metadata.chunk_count = metadata.chunk_count;
        stats.metadata.artifact_digest = metadata.artifact_digest;
        stats.metadata.entries_digest = metadata.chunk_entries_digest;
        stats.metadata.manifest_digest = metadata.root_digest;

        (void)stream_root(
            root_manifest_path, root_records, options.limits,
            [&](const PagedContentPageRef& page) {
                throw_if_cancelled(options);
                const auto page_path = content_store_path(store_root, page.digest);
                stream_page(
                    page_path, page, metadata, page_entries, true,
                    [&](const ContentChunkRef& chunk) {
                        throw_if_cancelled(options);
                        const auto chunk_path =
                            content_store_path(store_root, chunk.digest);
                        if (!regular_file_exact_size(chunk_path, chunk.length)) {
                            throw std::runtime_error(
                                "paged-content chunk is missing or wrong-sized: " +
                                chunk_path.string());
                        }
                        detail::NativeFile input(
                            chunk_path, detail::NativeOpenMode::read_only);
                        if (options.advise_sequential_io) input.advise_sequential();
                        detail::ArtifactSha256 chunk_hasher;
                        std::uint64_t local_offset{};
                        std::array<std::byte,
                            PagedContentManifestMetadata::kChunkEntryBytes> encoded{};
                        encode_chunk_entry(
                            encoded, chunk.length, chunk.digest);
                        chunk_entries_hasher.update(encoded);
                        while (local_offset < chunk.length) {
                            throw_if_cancelled(options);
                            const auto count = static_cast<std::size_t>(
                                std::min<std::uint64_t>(
                                    chunk.length - local_offset, io.size()));
                            auto bytes = io.first(count);
                            input.read_exact_at(local_offset, bytes);
                            ++stats.chunk_read_calls;
                            chunk_hasher.update(bytes);
                            artifact_hasher.update(bytes);
                            output.write_exact_at(
                                chunk.artifact_offset + local_offset, bytes);
                            ++stats.output_write_calls;
                            stats.bytes_read += count;
                            local_offset += count;
                        }
                        if (input.size() != chunk.length ||
                            chunk_hasher.finish() != chunk.digest) {
                            throw std::runtime_error(
                                "paged-content chunk digest mismatch: " +
                                chunk_path.string());
                        }
                        if (options.discard_chunk_cache) {
                            input.advise_dont_need(0U, chunk.length);
                        }
                        ++stats.chunks_read;
                    });
            });
        throw_if_cancelled(options);
        if (artifact_hasher.finish() != metadata.artifact_digest ||
            chunk_entries_hasher.finish() != metadata.chunk_entries_digest) {
            throw std::runtime_error(
                "reconstructed paged-content artifact or entry digest mismatch");
        }
        output.resize(metadata.artifact_size);
        throw_if_cancelled(options);
        if (options.fsync_on_commit) output.sync();
        throw_if_cancelled(options);
        output.close();
        atomic_replace(part_path, output_path);
        output_part.disarm();
        if (options.fsync_on_commit) sync_parent(output_path);
    } catch (...) {
        try {
            output.close();
        } catch (...) {
        }
        throw;
    }
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

ContentChunkWindowStats read_content_chunk_window(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_chunk,
    std::span<ContentChunkRef> output,
    const ContentChunkWindowOptions& options) {
    ContentStoreWorkspace workspace;
    return read_content_chunk_window(
        manifest_path, store_root, first_chunk, output, workspace, options);
}

ContentChunkWindowStats read_content_chunk_window(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_chunk,
    std::span<ContentChunkRef> output,
    ContentStoreWorkspace& workspace,
    const ContentChunkWindowOptions& options) {
    if (output.empty()) {
        throw std::invalid_argument("content chunk window output is empty");
    }
    if (output.size() > std::numeric_limits<std::uint32_t>::max()) {
        throw std::length_error("content chunk window exceeds 32-bit count");
    }
    const auto buffer_bytes = normalized_entry_buffer(
        options.manifest_buffer_bytes);
    std::uint32_t growth_events{};

    ContentChunkWindowStats stats;
    stats.format = detect_content_manifest_format(manifest_path);
    stats.first_chunk = first_chunk;

    if (stats.format == ContentManifestFormat::flat_v1) {
        detail::NativeFile manifest(manifest_path, detail::NativeOpenMode::read_only);
        const auto quick = quick_flat_metadata(manifest, options.limits);
        stats.manifest_chunks = quick.chunk_count;
        stats.artifact_size = quick.artifact_size;
        stats.artifact_digest = quick.artifact_digest;
        if (options.verify_manifest) {
            const auto verified = inspect_content_manifest(
                manifest_path, workspace, options.limits);
            stats.artifact_digest = verified.artifact_digest;
            stats.manifest_digest = verified.manifest_digest;
        }
        if (first_chunk > stats.manifest_chunks) {
            throw std::out_of_range("content chunk window begins after manifest");
        }
        if (first_chunk == stats.manifest_chunks) {
            stats.first_artifact_offset = stats.artifact_size;
            stats.next_chunk = stats.manifest_chunks;
            stats.next_artifact_offset = stats.artifact_size;
            stats.workspace_growth_events = growth_events;
            stats.workspace_reserved_bytes = workspace.resident_bytes();
            return stats;
        }
        // Full-manifest verification may grow the shared record arena. Acquire
        // the operational span afterwards so later reads never target freed
        // storage.
        auto records = PagedContentWorkspaceAccess::prepare_records(
            workspace, buffer_bytes, growth_events);

        std::uint64_t artifact_offset{};
        if (first_chunk != 0U && options.artifact_offset_hint_valid) {
            artifact_offset = options.artifact_offset_hint;
            if (artifact_offset >= stats.artifact_size) {
                throw std::invalid_argument(
                    "flat content window artifact-offset hint is outside artifact");
            }
        } else if (first_chunk != 0U) {
            std::uint64_t index{};
            std::uint64_t file_offset = ContentManifestMetadata::kHeaderBytes;
            while (index < first_chunk) {
                const auto capacity = records.size() /
                    ContentManifestMetadata::kEntryBytes;
                const auto count = static_cast<std::size_t>(
                    std::min<std::uint64_t>(first_chunk - index, capacity));
                const auto byte_count = count * ContentManifestMetadata::kEntryBytes;
                auto bytes = records.first(byte_count);
                manifest.read_exact_at(file_offset, bytes);
                for (std::size_t local = 0U; local < count; ++local) {
                    const auto* pointer = bytes.data() +
                        local * ContentManifestMetadata::kEntryBytes;
                    const auto chunk = decode_chunk_entry(
                        std::span<const std::byte,
                                  PagedContentManifestMetadata::kChunkEntryBytes>(
                            pointer,
                            PagedContentManifestMetadata::kChunkEntryBytes),
                        index + local, artifact_offset);
                    if (chunk.length == 0U ||
                        chunk.length > quick.chunking.max_bytes ||
                        (chunk.index + 1U < quick.chunk_count &&
                         chunk.length < quick.chunking.min_bytes) ||
                        artifact_offset > quick.artifact_size - chunk.length ||
                        all_zero(chunk.digest.bytes)) {
                        throw std::runtime_error(
                            "flat content manifest contains invalid prefix entry");
                    }
                    artifact_offset += chunk.length;
                }
                index += count;
                file_offset += byte_count;
                stats.prefix_entries_scanned += count;
            }
        }

        stats.first_artifact_offset = artifact_offset;
        const auto target_count = static_cast<std::uint32_t>(
            std::min<std::uint64_t>(output.size(),
                                    stats.manifest_chunks - first_chunk));
        std::uint64_t loaded{};
        std::uint64_t file_offset = checked_add(
            ContentManifestMetadata::kHeaderBytes,
            checked_multiply(first_chunk, ContentManifestMetadata::kEntryBytes,
                             "flat content window offset overflows"),
            "flat content window offset overflows");
        while (loaded < target_count) {
            const auto capacity = records.size() /
                ContentManifestMetadata::kEntryBytes;
            const auto count = static_cast<std::size_t>(
                std::min<std::uint64_t>(target_count - loaded, capacity));
            const auto byte_count = count * ContentManifestMetadata::kEntryBytes;
            auto bytes = records.first(byte_count);
            manifest.read_exact_at(file_offset, bytes);
            for (std::size_t local = 0U; local < count; ++local) {
                const auto global = first_chunk + loaded + local;
                const auto* pointer = bytes.data() +
                    local * ContentManifestMetadata::kEntryBytes;
                const auto chunk = decode_chunk_entry(
                    std::span<const std::byte,
                              PagedContentManifestMetadata::kChunkEntryBytes>(
                        pointer, PagedContentManifestMetadata::kChunkEntryBytes),
                    global, artifact_offset);
                if (chunk.length == 0U ||
                    chunk.length > quick.chunking.max_bytes ||
                    (chunk.index + 1U < quick.chunk_count &&
                     chunk.length < quick.chunking.min_bytes) ||
                    artifact_offset > quick.artifact_size - chunk.length ||
                    all_zero(chunk.digest.bytes)) {
                    throw std::runtime_error(
                        "flat content manifest contains invalid window entry");
                }
                output[static_cast<std::size_t>(loaded) + local] = chunk;
                artifact_offset += chunk.length;
            }
            loaded += count;
            file_offset += byte_count;
        }
        stats.chunks_loaded = target_count;
        stats.bytes_described = artifact_offset - stats.first_artifact_offset;
        stats.next_chunk = first_chunk + target_count;
        stats.next_artifact_offset = artifact_offset;
        if (stats.next_chunk == stats.manifest_chunks &&
            stats.next_artifact_offset != stats.artifact_size) {
            throw std::runtime_error(
                "flat content window does not terminate at artifact size");
        }
        stats.workspace_growth_events = growth_events;
        stats.workspace_reserved_bytes = workspace.resident_bytes();
        return stats;
    }

    detail::NativeFile root(manifest_path, detail::NativeOpenMode::read_only);
    auto metadata = quick_root_metadata(root, options.limits);
    if (options.verify_manifest) {
        metadata = inspect_paged_content_manifest(
            manifest_path, workspace, options.limits);
    }
    stats.manifest_chunks = metadata.chunk_count;
    stats.artifact_size = metadata.artifact_size;
    stats.artifact_digest = metadata.artifact_digest;
    stats.manifest_digest = metadata.root_digest;
    if (first_chunk > stats.manifest_chunks) {
        throw std::out_of_range("content chunk window begins after paged manifest");
    }
    if (first_chunk == stats.manifest_chunks) {
        stats.first_artifact_offset = stats.artifact_size;
        stats.next_chunk = stats.manifest_chunks;
        stats.next_artifact_offset = stats.artifact_size;
        stats.workspace_growth_events = growth_events;
        stats.workspace_reserved_bytes = workspace.resident_bytes();
        return stats;
    }
    // Root verification may grow the shared record arena. Acquire the page
    // decoding span only after verification.
    auto records = PagedContentWorkspaceAccess::prepare_records(
        workspace, buffer_bytes, growth_events);

    const auto target_count = static_cast<std::uint32_t>(
        std::min<std::uint64_t>(output.size(),
                                stats.manifest_chunks - first_chunk));
    const auto last_chunk = first_chunk + target_count;
    auto page_index = first_chunk / metadata.entries_per_page;
    std::size_t loaded{};
    while (page_index < metadata.page_count && loaded < target_count) {
        const auto page = read_page_record_at(root, metadata, page_index);
        const auto expected_first = checked_multiply(
            page_index, metadata.entries_per_page,
            "paged content page first-chunk overflows");
        const auto expected_count = static_cast<std::uint32_t>(
            std::min<std::uint64_t>(metadata.entries_per_page,
                                    metadata.chunk_count - expected_first));
        const auto expected_encoded = checked_add(
            PagedContentManifestMetadata::kPageHeaderBytes,
            checked_multiply(expected_count,
                             PagedContentManifestMetadata::kChunkEntryBytes,
                             "paged content page size overflows"),
            "paged content page size overflows");
        if (page.first_chunk != expected_first ||
            page.chunk_count != expected_count ||
            page.encoded_size != expected_encoded ||
            page.artifact_offset > metadata.artifact_size ||
            page.artifact_bytes > metadata.artifact_size - page.artifact_offset) {
            throw std::runtime_error(
                "paged content direct page record violates root geometry");
        }
        const auto page_end = page.first_chunk + page.chunk_count;
        if (page_end <= first_chunk) {
            ++page_index;
            continue;
        }
        if (page.first_chunk >= last_chunk) break;
        const auto page_path = content_store_path(store_root, page.digest);
        stream_page(
            page_path, page, metadata, records, options.verify_page_digests,
            [&](const ContentChunkRef& chunk) {
                if (chunk.index < first_chunk || chunk.index >= last_chunk) return;
                if (loaded >= output.size() ||
                    chunk.index != first_chunk + loaded ||
                    all_zero(chunk.digest.bytes)) {
                    throw std::runtime_error(
                        "paged content window is not contiguous");
                }
                output[loaded] = chunk;
                ++loaded;
            });
        ++stats.page_objects_read;
        ++page_index;
    }
    if (loaded != target_count) {
        throw std::runtime_error(
            "paged content window could not load all requested chunks");
    }
    stats.chunks_loaded = target_count;
    stats.first_artifact_offset = output.front().artifact_offset;
    const auto& last = output[loaded - 1U];
    stats.next_chunk = first_chunk + target_count;
    stats.next_artifact_offset = last.artifact_offset + last.length;
    stats.bytes_described =
        stats.next_artifact_offset - stats.first_artifact_offset;
    if (stats.next_chunk == stats.manifest_chunks &&
        stats.next_artifact_offset != stats.artifact_size) {
        throw std::runtime_error(
            "paged content window does not terminate at artifact size");
    }
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

ContentAvailabilityStats fill_content_availability(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_chunk,
    std::uint32_t requested_chunks,
    std::span<std::byte> output_bits,
    bool verify_objects,
    ContentStoreWorkspace* supplied_workspace,
    const ContentStoreLimits& limits) {
    if (requested_chunks == 0U) {
        throw std::invalid_argument("content availability request is empty");
    }
    const auto required_bytes =
        (static_cast<std::size_t>(requested_chunks) + 7U) / 8U;
    if (output_bits.size() < required_bytes) {
        throw std::invalid_argument("content availability output bitmap is too small");
    }
    std::fill(output_bits.begin(), output_bits.end(), std::byte{0});
    ContentStoreWorkspace local_workspace;
    auto& workspace = supplied_workspace == nullptr ? local_workspace : *supplied_workspace;
    std::uint32_t growth_events{};
    auto io = PagedContentWorkspaceAccess::prepare_io(
        workspace, 64U * 1024U, growth_events);
    (void)growth_events;

    ContentAvailabilityStats stats;
    stats.format = detect_content_manifest_format(manifest_path);
    stats.first_chunk = first_chunk;

    if (stats.format == ContentManifestFormat::flat_v1) {
        detail::NativeFile manifest(
            manifest_path, detail::NativeOpenMode::read_only);
        const auto metadata = quick_flat_metadata(manifest, limits);
        stats.manifest_chunks = metadata.chunk_count;
        if (first_chunk >= metadata.chunk_count) return stats;
        stats.bit_count = static_cast<std::uint32_t>(
            std::min<std::uint64_t>(requested_chunks,
                                    metadata.chunk_count - first_chunk));
        if (verify_objects) {
            (void)inspect_content_manifest(manifest_path, workspace, limits);
        }
        const auto bytes_count =
            static_cast<std::size_t>(stats.bit_count) *
            ContentManifestMetadata::kEntryBytes;
        auto entries = PagedContentWorkspaceAccess::prepare_records(
            workspace, bytes_count, growth_events);
        const auto offset = checked_add(
            ContentManifestMetadata::kHeaderBytes,
            checked_multiply(first_chunk, ContentManifestMetadata::kEntryBytes,
                             "flat availability offset overflows"),
            "flat availability offset overflows");
        manifest.read_exact_at(offset, entries.first(bytes_count));
        for (std::uint32_t local = 0U; local < stats.bit_count; ++local) {
            const auto* pointer = entries.data() +
                static_cast<std::size_t>(local) *
                    ContentManifestMetadata::kEntryBytes;
            const auto chunk = decode_chunk_entry(
                std::span<const std::byte,
                          PagedContentManifestMetadata::kChunkEntryBytes>(
                    pointer, PagedContentManifestMetadata::kChunkEntryBytes),
                first_chunk + local, 0U);
            bool available = regular_file_exact_size(
                content_store_path(store_root, chunk.digest), chunk.length);
            if (available && verify_objects) {
                available = verify_file(
                    content_store_path(store_root, chunk.digest),
                    chunk.digest, chunk.length, io);
            }
            set_bit(output_bits, local, available);
            if (available) ++stats.available_count;
        }
        return stats;
    }

    detail::NativeFile root(manifest_path, detail::NativeOpenMode::read_only);
    const auto metadata = quick_root_metadata(root, limits);
    stats.manifest_chunks = metadata.chunk_count;
    if (first_chunk >= metadata.chunk_count) return stats;
    stats.bit_count = static_cast<std::uint32_t>(
        std::min<std::uint64_t>(requested_chunks,
                                metadata.chunk_count - first_chunk));
    if (verify_objects) {
        (void)inspect_paged_content_manifest(manifest_path, workspace, limits);
    }

    const auto last_chunk = first_chunk + stats.bit_count;
    auto page_index = first_chunk / metadata.entries_per_page;
    while (page_index < metadata.page_count) {
        const auto page = read_page_record_at(root, metadata, page_index);
        const auto page_end = page.first_chunk + page.chunk_count;
        if (page.first_chunk >= last_chunk) break;
        if (page_end <= first_chunk) {
            ++page_index;
            continue;
        }
        const auto page_path = content_store_path(store_root, page.digest);
        if (!regular_file_exact_size(page_path, page.encoded_size) ||
            (verify_objects &&
             !verify_file(page_path, page.digest, page.encoded_size, io))) {
            const auto unknown_begin = std::max(first_chunk, page.first_chunk);
            const auto unknown_end = std::min<std::uint64_t>(last_chunk, page_end);
            stats.unknown_count += static_cast<std::uint32_t>(
                unknown_end - unknown_begin);
            ++page_index;
            continue;
        }
        detail::NativeFile page_file(page_path, detail::NativeOpenMode::read_only);
        std::array<std::byte,
                   PagedContentManifestMetadata::kPageHeaderBytes> page_header{};
        page_file.read_exact_at(0U, page_header);
        const auto decoded = decode_page_header(page_header);
        if (decoded.page.page_index != page.page_index ||
            decoded.page.first_chunk != page.first_chunk ||
            decoded.page.chunk_count != page.chunk_count ||
            decoded.page.encoded_size != page.encoded_size) {
            const auto unknown_begin = std::max(first_chunk, page.first_chunk);
            const auto unknown_end = std::min<std::uint64_t>(last_chunk, page_end);
            stats.unknown_count += static_cast<std::uint32_t>(
                unknown_end - unknown_begin);
            ++page_index;
            continue;
        }
        const auto begin = std::max(first_chunk, page.first_chunk);
        const auto end = std::min<std::uint64_t>(last_chunk, page_end);
        const auto local_begin = begin - page.first_chunk;
        const auto count = end - begin;
        const auto entry_bytes_count = checked_multiply(
            count, PagedContentManifestMetadata::kChunkEntryBytes,
            "paged availability entry count overflows");
        if (entry_bytes_count > std::numeric_limits<std::size_t>::max()) {
            throw std::length_error("paged availability entry buffer exceeds platform");
        }
        auto entries = PagedContentWorkspaceAccess::prepare_records(
            workspace, static_cast<std::size_t>(entry_bytes_count), growth_events);
        const auto entry_offset = checked_add(
            PagedContentManifestMetadata::kPageHeaderBytes,
            checked_multiply(local_begin,
                             PagedContentManifestMetadata::kChunkEntryBytes,
                             "paged availability page offset overflows"),
            "paged availability page offset overflows");
        page_file.read_exact_at(
            entry_offset,
            entries.first(static_cast<std::size_t>(entry_bytes_count)));
        for (std::uint64_t local = 0U; local < count; ++local) {
            const auto* pointer = entries.data() +
                static_cast<std::size_t>(local) *
                    PagedContentManifestMetadata::kChunkEntryBytes;
            const auto chunk = decode_chunk_entry(
                std::span<const std::byte,
                          PagedContentManifestMetadata::kChunkEntryBytes>(
                    pointer, PagedContentManifestMetadata::kChunkEntryBytes),
                begin + local, 0U);
            const auto object = content_store_path(store_root, chunk.digest);
            bool available = regular_file_exact_size(object, chunk.length);
            if (available && verify_objects) {
                available = verify_file(
                    object, chunk.digest, chunk.length, io);
            }
            const auto output_index = static_cast<std::uint32_t>(
                begin + local - first_chunk);
            set_bit(output_bits, output_index, available);
            if (available) ++stats.available_count;
        }
        ++page_index;
    }
    return stats;
}


PagedContentPageAvailabilityStats fill_paged_content_page_availability(
    const std::filesystem::path& root_manifest_path,
    const std::filesystem::path& store_root,
    std::uint64_t first_page,
    std::uint32_t requested_pages,
    std::span<std::byte> output_bits,
    bool verify_objects,
    ContentStoreWorkspace* supplied_workspace,
    const ContentStoreLimits& limits) {
    if (requested_pages == 0U) {
        throw std::invalid_argument("paged content page-availability request is empty");
    }
    const auto required_bytes =
        (static_cast<std::size_t>(requested_pages) + 7U) / 8U;
    if (output_bits.size() < required_bytes) {
        throw std::invalid_argument(
            "paged content page-availability bitmap is too small");
    }
    std::fill(output_bits.begin(), output_bits.end(), std::byte{0});
    if (detect_content_manifest_format(root_manifest_path) !=
        ContentManifestFormat::paged_v2) {
        throw std::invalid_argument(
            "manifest-page inventory requires a paged content root");
    }

    ContentStoreWorkspace local_workspace;
    auto& workspace = supplied_workspace == nullptr
        ? local_workspace
        : *supplied_workspace;
    constexpr std::size_t kBatchPages = 128U;
    std::array<PagedContentPageRef, kBatchPages> pages{};

    PagedContentPageAvailabilityStats stats;
    stats.first_page = first_page;
    std::uint32_t loaded_total{};
    bool root_verified{};
    while (loaded_total < requested_pages) {
        const auto remaining = static_cast<std::size_t>(
            requested_pages - loaded_total);
        const auto capacity = std::min<std::size_t>(remaining, pages.size());
        PagedContentPageWindowOptions options;
        options.verify_root_manifest = verify_objects && !root_verified;
        options.root_buffer_bytes = 64U * 1024U;
        options.limits = limits;
        const auto loaded = read_paged_content_page_window(
            root_manifest_path, first_page + loaded_total,
            std::span<PagedContentPageRef>(pages.data(), capacity),
            workspace, options);
        root_verified = root_verified || options.verify_root_manifest;
        if (stats.manifest_pages == 0U) {
            stats.manifest_pages = loaded.metadata.page_count;
        } else if (stats.manifest_pages != loaded.metadata.page_count) {
            throw std::runtime_error(
                "paged content root changed during page-availability scan");
        }
        if (loaded.pages_loaded == 0U) break;
        for (std::uint32_t local = 0U; local < loaded.pages_loaded; ++local) {
            const auto& page = pages[local];
            const bool available = content_object_available(
                store_root, page.digest, page.encoded_size,
                verify_objects, &workspace, 64U * 1024U);
            set_bit(output_bits, loaded_total + local, available);
            if (available) ++stats.available_count;
        }
        loaded_total += loaded.pages_loaded;
        if (loaded.complete()) break;
    }
    stats.bit_count = loaded_total;
    return stats;
}

} // namespace toxsync
