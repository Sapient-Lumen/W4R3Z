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

struct ContentStoreWorkspaceAccess final {
    static std::size_t growth_capacity(std::size_t current, std::size_t required) {
        if (required == 0U) return 0U;
        if (current >= required) return current;
        // These arenas are controlled by explicit session limits. Page-rounding
        // avoids the 1.5x geometric slack that is useful for general vectors but
        // wasteful for long-lived IoT workers with stable buffer policies.
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

constexpr std::array<std::byte, 8> kManifestMagic{
    std::byte{'T'}, std::byte{'X'}, std::byte{'S'}, std::byte{'C'},
    std::byte{'D'}, std::byte{'C'}, std::byte{'2'}, std::byte{0},
};
constexpr std::uint16_t kManifestFlags = 0U;
constexpr std::uint32_t kEntryFlags = 0U;
constexpr std::size_t kDefaultRecordBuffer = 64U * 1024U;

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
    for (std::size_t index = 0; index < table.size(); ++index) {
        table[index] = splitmix64(0x544f5853594e4300ULL + index);
    }
    return table;
}

constexpr auto kGearTable = make_gear_table();

template <typename T>
void store_le(std::byte* output, T value) noexcept {
    static_assert(std::is_unsigned_v<T>);
    for (std::size_t index = 0; index < sizeof(T); ++index) {
        output[index] = static_cast<std::byte>(value >> (index * 8U));
    }
}

template <typename T>
[[nodiscard]] T load_le(const std::byte* input) noexcept {
    static_assert(std::is_unsigned_v<T>);
    std::uint64_t wide{};
    for (std::size_t index = 0; index < sizeof(T); ++index) {
        wide |= static_cast<std::uint64_t>(std::to_integer<unsigned char>(input[index]))
                << (index * 8U);
    }
    return static_cast<T>(wide);
}

[[nodiscard]] bool all_zero(std::span<const std::byte> bytes) noexcept {
    return std::all_of(bytes.begin(), bytes.end(), [](std::byte value) {
        return value == std::byte{0};
    });
}

void validate_chunking(const ContentChunking& chunking,
                       const ContentStoreLimits& limits) {
    if (chunking.min_bytes < limits.min_chunk_bytes ||
        chunking.max_bytes > limits.max_chunk_bytes ||
        chunking.min_bytes > chunking.average_bytes ||
        chunking.average_bytes > chunking.max_bytes) {
        throw std::invalid_argument("content-store chunk sizes are outside configured limits");
    }
    if (!std::has_single_bit(chunking.average_bytes)) {
        throw std::invalid_argument("content-store average chunk size must be a power of two");
    }
}

[[nodiscard]] std::uint64_t ceiling_divide(std::uint64_t numerator,
                                           std::uint64_t denominator) {
    if (denominator == 0U) {
        throw std::invalid_argument("content-store divisor must be nonzero");
    }
    if (numerator == 0U) return 0U;
    return 1U + (numerator - 1U) / denominator;
}

[[nodiscard]] std::uint64_t manifest_bytes_for_chunks(std::uint64_t chunks) {
    constexpr auto header =
        static_cast<std::uint64_t>(ContentManifestMetadata::kHeaderBytes);
    constexpr auto entry =
        static_cast<std::uint64_t>(ContentManifestMetadata::kEntryBytes);
    if (chunks > (std::numeric_limits<std::uint64_t>::max() - header) / entry) {
        throw std::overflow_error("content-store manifest size overflow");
    }
    return header + chunks * entry;
}

[[nodiscard]] std::uint64_t next_power_of_two(std::uint64_t value) {
    if (value <= 1U) return 1U;
    if (value > (std::uint64_t{1} << 63U)) {
        throw std::overflow_error("content-store chunk size cannot be rounded safely");
    }
    return std::bit_ceil(value);
}

[[nodiscard]] std::size_t normalized_io_bytes(std::size_t requested) {
    if (requested == 0U) {
        throw std::invalid_argument("content-store I/O buffer size must be nonzero");
    }
    return requested;
}

[[nodiscard]] std::size_t normalized_record_bytes(std::size_t requested) {
    if (requested == 0U) {
        throw std::invalid_argument("content-store manifest buffer size must be nonzero");
    }
    auto records = requested / ContentManifestMetadata::kEntryBytes;
    if (records == 0U) records = 1U;
    if (records > std::numeric_limits<std::size_t>::max() /
                      ContentManifestMetadata::kEntryBytes) {
        throw std::length_error("content-store manifest buffer size overflows this platform");
    }
    return records * ContentManifestMetadata::kEntryBytes;
}

[[nodiscard]] std::filesystem::path part_path_for(const std::filesystem::path& path) {
    auto part = path;
    part += ".toxsync.part";
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
        throw std::runtime_error("cannot open parent directory for fsync: " +
                                 parent.string() + ": " + std::strerror(errno));
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
        throw std::runtime_error("atomic rename failed: " +
                                 std::string(std::strerror(errno)));
    }
#else
    std::error_code error;
    std::filesystem::remove(destination, error);
    error.clear();
    std::filesystem::rename(source, destination, error);
    if (error) throw std::runtime_error("rename failed: " + error.message());
#endif
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
                                         std::uint64_t expected_size,
                                         std::uint64_t* read_calls = nullptr) {
    detail::ArtifactSha256 hasher;
    std::uint64_t offset{};
    while (offset < expected_size) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(expected_size - offset, buffer.size()));
        auto output = buffer.first(count);
        file.read_exact_at(offset, output);
        if (read_calls != nullptr) ++*read_calls;
        hasher.update(output);
        offset += count;
    }
    if (file.size() != expected_size) {
        throw std::runtime_error("content-store file changed while hashing: " +
                                 file.path_text());
    }
    return hasher.finish();
}

[[nodiscard]] bool verify_blob(const std::filesystem::path& path,
                               const Digest256& digest,
                               std::uint64_t size,
                               std::span<std::byte> io) {
    if (!regular_file_exact_size(path, size)) return false;
    detail::NativeFile input(path, detail::NativeOpenMode::read_only);
    input.advise_sequential();
    return hash_native_file(input, io, size) == digest;
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
    void disarm() noexcept { armed_ = false; }
    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }

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
    name += ".toxsync.tmp." + std::to_string(process) + "." + std::to_string(number);
    return destination.parent_path() / name;
}

[[nodiscard]] bool publish_temp_no_replace(TemporaryPath& temporary,
                                           const std::filesystem::path& destination,
                                           bool fsync_parent_directory) {
    std::error_code error;
    std::filesystem::create_hard_link(temporary.path(), destination, error);
    if (!error) {
        std::filesystem::remove(temporary.path(), error);
        if (error) {
            throw std::runtime_error("cannot remove content-store temporary file: " +
                                     error.message());
        }
        temporary.disarm();
        if (fsync_parent_directory) sync_parent(destination);
        return true;
    }
    if (std::filesystem::exists(destination)) return false;
    throw std::runtime_error("cannot publish content-store object: " + error.message());
}

[[nodiscard]] bool store_buffer(const std::filesystem::path& store_root,
                                const Digest256& digest,
                                std::span<const std::byte> bytes,
                                bool fsync_on_commit,
                                bool verify_existing) {
    const auto destination = content_store_path(store_root, digest);
    ensure_parent(destination);
    std::array<std::byte, 16U * 1024U> verify_buffer;
    if (std::filesystem::exists(destination)) {
        if (!regular_file_exact_size(destination, bytes.size()) ||
            (verify_existing && !verify_blob(destination, digest, bytes.size(), verify_buffer))) {
            throw std::runtime_error("content-store object exists with invalid contents: " +
                                     destination.string());
        }
        return false;
    }

    const auto temporary_path = unique_temp_path(destination);
    TemporaryPath temporary(temporary_path);
    detail::NativeFile output(temporary_path,
                              detail::NativeOpenMode::read_write_create_exclusive);
    output.write_exact_at(0U, bytes);
    if (fsync_on_commit) output.sync();
    output.close();
    const bool created = publish_temp_no_replace(temporary, destination, fsync_on_commit);
    if (created) return true;

    // Another writer won the race. Validate its result before treating it as
    // a reusable object.
    if (!regular_file_exact_size(destination, bytes.size()) ||
        (verify_existing && !verify_blob(destination, digest, bytes.size(), verify_buffer))) {
        throw std::runtime_error("racing content-store object failed verification: " +
                                 destination.string());
    }
    return false;
}

[[nodiscard]] bool store_file(const std::filesystem::path& store_root,
                              const std::filesystem::path& source_path,
                              const Digest256& digest,
                              std::uint64_t size,
                              std::span<std::byte> io,
                              bool fsync_on_commit,
                              bool verify_existing) {
    const auto destination = content_store_path(store_root, digest);
    ensure_parent(destination);
    if (std::filesystem::exists(destination)) {
        if (!regular_file_exact_size(destination, size) ||
            (verify_existing && !verify_blob(destination, digest, size, io))) {
            throw std::runtime_error("content-store object exists with invalid contents: " +
                                     destination.string());
        }
        return false;
    }

    const auto temporary_path = unique_temp_path(destination);
    TemporaryPath temporary(temporary_path);
    detail::NativeFile input(source_path, detail::NativeOpenMode::read_only);
    detail::NativeFile output(temporary_path,
                              detail::NativeOpenMode::read_write_create_exclusive);
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
        throw std::runtime_error("manifest changed while publishing to content store");
    }
    if (fsync_on_commit) output.sync();
    output.close();
    const bool created = publish_temp_no_replace(temporary, destination, fsync_on_commit);
    if (created) return true;
    if (!regular_file_exact_size(destination, size) ||
        (verify_existing && !verify_blob(destination, digest, size, io))) {
        throw std::runtime_error("racing manifest failed content-store verification");
    }
    return false;
}

void encode_entry(std::span<std::byte, ContentManifestMetadata::kEntryBytes> output,
                  std::uint32_t length,
                  const Digest256& digest) noexcept {
    store_le<std::uint32_t>(output.data(), length);
    store_le<std::uint32_t>(output.data() + 4U, kEntryFlags);
    std::copy(digest.bytes.begin(), digest.bytes.end(), output.begin() + 8);
}

[[nodiscard]] ContentChunkRef decode_entry(
    std::span<const std::byte, ContentManifestMetadata::kEntryBytes> input,
    std::uint64_t index,
    std::uint64_t artifact_offset) {
    const auto length = load_le<std::uint32_t>(input.data());
    const auto flags = load_le<std::uint32_t>(input.data() + 4U);
    if (flags != kEntryFlags) {
        throw std::runtime_error("content manifest contains unsupported entry flags");
    }
    ContentChunkRef result{.index = index,
                           .artifact_offset = artifact_offset,
                           .length = length};
    std::copy_n(input.begin() + 8, result.digest.bytes.size(), result.digest.bytes.begin());
    return result;
}

void encode_header(const ContentManifestMetadata& metadata,
                   std::span<std::byte, ContentManifestMetadata::kHeaderBytes> output) noexcept {
    std::fill(output.begin(), output.end(), std::byte{0});
    std::copy(kManifestMagic.begin(), kManifestMagic.end(), output.begin());
    std::size_t offset = kManifestMagic.size();
    store_le<std::uint16_t>(output.data() + offset,
                            ContentManifestMetadata::kFormatVersion);
    offset += sizeof(std::uint16_t);
    store_le<std::uint16_t>(output.data() + offset,
                            static_cast<std::uint16_t>(ContentManifestMetadata::kHeaderBytes));
    offset += sizeof(std::uint16_t);
    store_le<std::uint16_t>(output.data() + offset,
                            static_cast<std::uint16_t>(ContentManifestMetadata::kEntryBytes));
    offset += sizeof(std::uint16_t);
    store_le<std::uint16_t>(output.data() + offset, kManifestFlags);
    offset += sizeof(std::uint16_t);
    store_le<std::uint32_t>(output.data() + offset, metadata.chunking.min_bytes);
    offset += sizeof(std::uint32_t);
    store_le<std::uint32_t>(output.data() + offset, metadata.chunking.average_bytes);
    offset += sizeof(std::uint32_t);
    store_le<std::uint32_t>(output.data() + offset, metadata.chunking.max_bytes);
    offset += sizeof(std::uint32_t);
    offset += sizeof(std::uint32_t); // reserved
    store_le<std::uint64_t>(output.data() + offset, metadata.artifact_size);
    offset += sizeof(std::uint64_t);
    store_le<std::uint64_t>(output.data() + offset, metadata.chunk_count);
    offset += sizeof(std::uint64_t);
    std::copy(metadata.artifact_digest.bytes.begin(), metadata.artifact_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
    offset += metadata.artifact_digest.bytes.size();
    std::copy(metadata.entries_digest.bytes.begin(), metadata.entries_digest.bytes.end(),
              output.begin() + static_cast<std::ptrdiff_t>(offset));
}

[[nodiscard]] ContentManifestMetadata decode_header(
    std::span<const std::byte, ContentManifestMetadata::kHeaderBytes> input,
    const ContentStoreLimits& limits) {
    if (!std::equal(kManifestMagic.begin(), kManifestMagic.end(), input.begin())) {
        throw std::runtime_error("invalid toxsync content manifest magic");
    }
    std::size_t offset = kManifestMagic.size();
    const auto version = load_le<std::uint16_t>(input.data() + offset);
    offset += sizeof(std::uint16_t);
    const auto header_bytes = load_le<std::uint16_t>(input.data() + offset);
    offset += sizeof(std::uint16_t);
    const auto entry_bytes = load_le<std::uint16_t>(input.data() + offset);
    offset += sizeof(std::uint16_t);
    const auto flags = load_le<std::uint16_t>(input.data() + offset);
    offset += sizeof(std::uint16_t);
    if (version != ContentManifestMetadata::kFormatVersion ||
        header_bytes != ContentManifestMetadata::kHeaderBytes ||
        entry_bytes != ContentManifestMetadata::kEntryBytes || flags != kManifestFlags) {
        throw std::runtime_error("unsupported toxsync content manifest format");
    }

    ContentManifestMetadata metadata;
    metadata.chunking.min_bytes = load_le<std::uint32_t>(input.data() + offset);
    offset += sizeof(std::uint32_t);
    metadata.chunking.average_bytes = load_le<std::uint32_t>(input.data() + offset);
    offset += sizeof(std::uint32_t);
    metadata.chunking.max_bytes = load_le<std::uint32_t>(input.data() + offset);
    offset += sizeof(std::uint32_t);
    if (load_le<std::uint32_t>(input.data() + offset) != 0U) {
        throw std::runtime_error("content manifest reserved header bits are nonzero");
    }
    offset += sizeof(std::uint32_t);
    metadata.artifact_size = load_le<std::uint64_t>(input.data() + offset);
    offset += sizeof(std::uint64_t);
    metadata.chunk_count = load_le<std::uint64_t>(input.data() + offset);
    offset += sizeof(std::uint64_t);
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.artifact_digest.bytes.size(), metadata.artifact_digest.bytes.begin());
    offset += metadata.artifact_digest.bytes.size();
    std::copy_n(input.begin() + static_cast<std::ptrdiff_t>(offset),
                metadata.entries_digest.bytes.size(), metadata.entries_digest.bytes.begin());
    offset += metadata.entries_digest.bytes.size();
    if (!all_zero(input.subspan(offset))) {
        throw std::runtime_error("content manifest reserved header bytes are nonzero");
    }

    validate_chunking(metadata.chunking, limits);
    if (metadata.artifact_size > limits.max_artifact_size ||
        metadata.chunk_count > limits.max_chunks) {
        throw std::runtime_error("content manifest exceeds configured resource limits");
    }
    if ((metadata.artifact_size == 0U) != (metadata.chunk_count == 0U)) {
        throw std::runtime_error("content manifest empty-artifact shape is invalid");
    }
    if (metadata.chunk_count >
        (std::numeric_limits<std::uint64_t>::max() - ContentManifestMetadata::kHeaderBytes) /
            ContentManifestMetadata::kEntryBytes) {
        throw std::runtime_error("content manifest encoded size overflows");
    }
    return metadata;
}

class GearChunker final {
public:
    explicit GearChunker(ContentChunking options)
        : options_(options), mask_(static_cast<std::uint64_t>(options.average_bytes - 1U)) {}

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

template <typename Visitor>
[[nodiscard]] ContentManifestMetadata stream_manifest(
    const std::filesystem::path& manifest_path,
    std::span<std::byte> record_buffer,
    const ContentStoreLimits& limits,
    Visitor&& visitor) {
    if (record_buffer.size() < ContentManifestMetadata::kEntryBytes) {
        throw std::invalid_argument("content manifest record buffer is too small");
    }
    const auto usable = (record_buffer.size() / ContentManifestMetadata::kEntryBytes) *
                        ContentManifestMetadata::kEntryBytes;
    record_buffer = record_buffer.first(usable);

    detail::NativeFile manifest(manifest_path, detail::NativeOpenMode::read_only);
    manifest.advise_sequential();
    const auto file_size = manifest.size();
    if (file_size < ContentManifestMetadata::kHeaderBytes) {
        throw std::runtime_error("truncated toxsync content manifest header");
    }
    std::array<std::byte, ContentManifestMetadata::kHeaderBytes> header{};
    manifest.read_exact_at(0U, header);
    auto metadata = decode_header(header, limits);
    if (metadata.encoded_size() != file_size) {
        throw std::runtime_error("content manifest length does not match chunk count");
    }

    detail::ArtifactSha256 entries_hasher;
    detail::ArtifactSha256 manifest_hasher;
    manifest_hasher.update(header);
    std::uint64_t entry_index{};
    std::uint64_t artifact_offset{};
    std::uint64_t manifest_offset = ContentManifestMetadata::kHeaderBytes;
    while (entry_index < metadata.chunk_count) {
        const auto remaining = metadata.chunk_count - entry_index;
        const auto capacity = record_buffer.size() / ContentManifestMetadata::kEntryBytes;
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(remaining, capacity));
        const auto bytes_count = count * ContentManifestMetadata::kEntryBytes;
        auto bytes = record_buffer.first(bytes_count);
        manifest.read_exact_at(manifest_offset, bytes);
        entries_hasher.update(bytes);
        manifest_hasher.update(bytes);

        for (std::size_t local = 0U; local < count; ++local) {
            const auto global = entry_index + local;
            const auto* pointer = bytes.data() + local * ContentManifestMetadata::kEntryBytes;
            const auto entry = decode_entry(
                std::span<const std::byte, ContentManifestMetadata::kEntryBytes>(
                    pointer, ContentManifestMetadata::kEntryBytes),
                global, artifact_offset);
            if (entry.length == 0U || entry.length > metadata.chunking.max_bytes ||
                (global + 1U < metadata.chunk_count &&
                 entry.length < metadata.chunking.min_bytes)) {
                throw std::runtime_error("content manifest contains an invalid chunk length");
            }
            if (artifact_offset > metadata.artifact_size ||
                entry.length > metadata.artifact_size - artifact_offset) {
                throw std::runtime_error("content manifest chunk lengths exceed artifact size");
            }
            visitor(entry);
            artifact_offset += entry.length;
        }
        entry_index += count;
        manifest_offset += bytes_count;
    }
    if (artifact_offset != metadata.artifact_size) {
        throw std::runtime_error("content manifest chunk lengths do not equal artifact size");
    }
    if (entries_hasher.finish() != metadata.entries_digest) {
        throw std::runtime_error("content manifest entry digest mismatch");
    }
    metadata.manifest_digest = manifest_hasher.finish();
    return metadata;
}

} // namespace

std::uint64_t ContentManifestMetadata::encoded_size() const noexcept {
    return static_cast<std::uint64_t>(kHeaderBytes) +
           chunk_count * static_cast<std::uint64_t>(kEntryBytes);
}

ContentScaleEstimate estimate_content_scale(
    std::uint64_t artifact_size,
    const ContentChunkingAutoOptions& options,
    const ContentStoreLimits& limits) {
    if (artifact_size > limits.max_artifact_size) {
        throw std::invalid_argument("content-store artifact exceeds configured size limit");
    }
    validate_chunking(options.preferred, limits);
    if (options.metadata_budget_bytes < ContentManifestMetadata::kHeaderBytes) {
        throw std::invalid_argument(
            "content-store metadata budget is smaller than the manifest header");
    }

    const auto maximum_entries_by_budget =
        (options.metadata_budget_bytes - ContentManifestMetadata::kHeaderBytes) /
        ContentManifestMetadata::kEntryBytes;
    if (artifact_size != 0U && maximum_entries_by_budget == 0U) {
        throw std::invalid_argument(
            "content-store metadata budget cannot hold one chunk entry");
    }
    const auto maximum_entries =
        std::min(maximum_entries_by_budget, limits.max_chunks);
    if (artifact_size != 0U && maximum_entries == 0U) {
        throw std::invalid_argument("content-store chunk limit is zero");
    }

    const auto preferred_worst_chunks = ceiling_divide(
        artifact_size, options.preferred.min_bytes);
    ContentChunking selected = options.preferred;
    if (preferred_worst_chunks > maximum_entries) {
        const auto required_min = ceiling_divide(artifact_size, maximum_entries);
        const auto rounded_min = next_power_of_two(std::max<std::uint64_t>(
            required_min, options.preferred.min_bytes));
        if (rounded_min > limits.max_chunk_bytes ||
            rounded_min > std::numeric_limits<std::uint32_t>::max()) {
            throw std::invalid_argument(
                "content-store metadata budget cannot be met within chunk-size limits");
        }
        selected.min_bytes = static_cast<std::uint32_t>(rounded_min);

        const auto preferred_scale = ceiling_divide(
            rounded_min, options.preferred.min_bytes);
        const auto scale = next_power_of_two(preferred_scale);
        auto average = static_cast<std::uint64_t>(options.preferred.average_bytes);
        if (average > std::numeric_limits<std::uint64_t>::max() / scale) {
            average = limits.max_chunk_bytes;
        } else {
            average *= scale;
        }
        average = std::max<std::uint64_t>(average, selected.min_bytes);
        average = std::min<std::uint64_t>(average, limits.max_chunk_bytes);
        if (!std::has_single_bit(average)) {
            average = std::bit_floor(average);
        }
        if (average < selected.min_bytes) {
            average = selected.min_bytes;
        }
        selected.average_bytes = static_cast<std::uint32_t>(average);

        auto maximum = static_cast<std::uint64_t>(options.preferred.max_bytes);
        if (maximum > std::numeric_limits<std::uint64_t>::max() / scale) {
            maximum = limits.max_chunk_bytes;
        } else {
            maximum *= scale;
        }
        maximum = std::max<std::uint64_t>(maximum, selected.average_bytes);
        maximum = std::min<std::uint64_t>(maximum, limits.max_chunk_bytes);
        selected.max_bytes = static_cast<std::uint32_t>(maximum);
    }

    validate_chunking(selected, limits);
    const auto maximum_chunks = ceiling_divide(artifact_size, selected.min_bytes);
    if (maximum_chunks > limits.max_chunks) {
        throw std::invalid_argument("content-store auto chunking exceeds chunk-count limit");
    }
    const auto maximum_manifest_bytes = manifest_bytes_for_chunks(maximum_chunks);
    if (maximum_manifest_bytes > options.metadata_budget_bytes) {
        throw std::invalid_argument(
            "content-store metadata budget cannot be met within configured limits");
    }
    return ContentScaleEstimate{
        .artifact_size = artifact_size,
        .chunking = selected,
        .maximum_chunks = maximum_chunks,
        .maximum_manifest_bytes = maximum_manifest_bytes,
    };
}

ContentChunking choose_content_chunking(
    std::uint64_t artifact_size,
    const ContentChunkingAutoOptions& options,
    const ContentStoreLimits& limits) {
    return estimate_content_scale(artifact_size, options, limits).chunking;
}

std::filesystem::path content_store_path(const std::filesystem::path& store_root,
                                         const Digest256& digest) {
    const auto hex = digest.hex();
    return store_root / "sha256" / hex.substr(0U, 2U) / hex.substr(2U);
}

ContentObjectInstallStats install_content_object(
    const std::filesystem::path& source_path,
    const std::filesystem::path& store_root,
    const Digest256& expected_digest,
    std::uint64_t expected_size,
    const ContentObjectInstallOptions& options) {
    ContentStoreWorkspace workspace;
    return install_content_object(source_path, store_root, expected_digest,
                                  expected_size, workspace, options);
}

ContentObjectInstallStats install_content_object(
    const std::filesystem::path& source_path,
    const std::filesystem::path& store_root,
    const Digest256& expected_digest,
    std::uint64_t expected_size,
    ContentStoreWorkspace& workspace,
    const ContentObjectInstallOptions& options) {
    if (source_path.empty() || store_root.empty() ||
        all_zero(expected_digest.bytes)) {
        throw std::invalid_argument("content-object install arguments are incomplete");
    }
    const auto io_bytes = normalized_io_bytes(options.io_buffer_bytes);
    std::uint32_t growth_events{};
    auto io = ContentStoreWorkspaceAccess::prepare_io(
        workspace, io_bytes, growth_events);
    ContentObjectInstallStats stats;

    const auto destination = content_store_path(store_root, expected_digest);
    const auto source_absolute = std::filesystem::absolute(source_path).lexically_normal();
    const auto destination_absolute =
        std::filesystem::absolute(destination).lexically_normal();
    if (source_absolute == destination_absolute) {
        throw std::invalid_argument(
            "content-object staging source already names its store destination");
    }
    if (!regular_file_exact_size(source_path, expected_size)) {
        throw std::runtime_error(
            "content-object staging source is not a regular file of the expected size");
    }
    ensure_parent(destination);

    const auto verify_source = [&]() {
        if (options.source_preverified) {
            stats.bytes_verified = expected_size;
            return;
        }
        detail::NativeFile source(source_path, detail::NativeOpenMode::read_only);
        source.advise_sequential();
        const auto digest = hash_native_file(
            source, io, expected_size, &stats.read_calls);
        if (source.size() != expected_size || digest != expected_digest) {
            throw std::runtime_error(
                "content-object staging source failed SHA-256 verification");
        }
        stats.bytes_verified = expected_size;
    };

    const auto consume_source = [&]() {
        if (!options.consume_source) return;
        std::error_code remove_error;
        const bool removed = std::filesystem::remove(source_path, remove_error);
        if (remove_error || !removed) {
            throw std::runtime_error(
                "cannot consume content-object staging source: " +
                (remove_error ? remove_error.message() : std::string("not removed")));
        }
        if (options.fsync_on_commit &&
            source_absolute.parent_path() != destination_absolute.parent_path()) {
            sync_parent(source_path);
        }
    };

    if (std::filesystem::exists(destination)) {
        if (!regular_file_exact_size(destination, expected_size) ||
            (options.verify_existing_object &&
             !verify_blob(destination, expected_digest, expected_size, io))) {
            throw std::runtime_error(
                "content-store object exists with invalid contents: " +
                destination.string());
        }
        verify_source();
        consume_source();
        stats.method = ContentObjectInstallMethod::reused_existing;
        stats.workspace_growth_events = growth_events;
        stats.workspace_reserved_bytes = workspace.resident_bytes();
        return stats;
    }

    if (options.prefer_hard_link && options.consume_source) {
        verify_source();
        std::error_code link_error;
        std::filesystem::create_hard_link(source_path, destination, link_error);
        if (!link_error) {
            // The source is a private completed staging file. Removing its
            // original name turns hard-link publication into an atomic
            // same-filesystem move without copying payload bytes.
            consume_source();
            if (options.fsync_on_commit) sync_parent(destination);
            stats.method = ContentObjectInstallMethod::moved_by_hard_link;
            stats.workspace_growth_events = growth_events;
            stats.workspace_reserved_bytes = workspace.resident_bytes();
            return stats;
        }
        if (std::filesystem::exists(destination)) {
            if (!regular_file_exact_size(destination, expected_size) ||
                (options.verify_existing_object &&
                 !verify_blob(destination, expected_digest, expected_size, io))) {
                throw std::runtime_error(
                    "racing content-store object failed verification: " +
                    destination.string());
            }
            consume_source();
            stats.method = ContentObjectInstallMethod::reused_existing;
            stats.workspace_growth_events = growth_events;
            stats.workspace_reserved_bytes = workspace.resident_bytes();
            return stats;
        }
        // EXDEV is the expected reason, but read-only bind mounts and filesystems
        // without hard links also benefit from the bounded verified copy path.
    }

    const auto temporary_path = unique_temp_path(destination);
    TemporaryPath temporary(temporary_path);
    detail::NativeFile input(source_path, detail::NativeOpenMode::read_only);
    input.advise_sequential();
    detail::NativeFile output(
        temporary_path, detail::NativeOpenMode::read_write_create_exclusive);
    detail::ArtifactSha256 hasher;
    std::uint64_t offset{};
    while (offset < expected_size) {
        const auto count = static_cast<std::size_t>(
            std::min<std::uint64_t>(expected_size - offset, io.size()));
        auto bytes = io.first(count);
        input.read_exact_at(offset, bytes);
        ++stats.read_calls;
        // The copy itself is a new publication boundary. Authenticate the
        // exact bytes copied even when the source was verified by an upstream
        // transport worker, so a concurrent source mutation cannot silently
        // cross filesystems into the content store.
        hasher.update(bytes);
        output.write_exact_at(offset, bytes);
        ++stats.write_calls;
        offset += count;
    }
    if (input.size() != expected_size || hasher.finish() != expected_digest) {
        throw std::runtime_error(
            "content-object staging source changed or failed SHA-256 verification");
    }
    stats.bytes_verified = expected_size;
    stats.bytes_copied = expected_size;
    if (options.fsync_on_commit) output.sync();
    output.close();
    const bool created = publish_temp_no_replace(
        temporary, destination, options.fsync_on_commit);
    if (!created &&
        (!regular_file_exact_size(destination, expected_size) ||
         (options.verify_existing_object &&
          !verify_blob(destination, expected_digest, expected_size, io)))) {
        throw std::runtime_error(
            "racing content-store object failed verification after copy");
    }
    consume_source();
    stats.method = created ? ContentObjectInstallMethod::copied
                           : ContentObjectInstallMethod::reused_existing;
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

bool content_object_available(
    const std::filesystem::path& store_root,
    const Digest256& digest,
    std::uint64_t expected_size,
    bool verify_digest,
    ContentStoreWorkspace* supplied_workspace,
    std::size_t io_buffer_bytes) {
    const auto object = content_store_path(store_root, digest);
    if (!regular_file_exact_size(object, expected_size)) return false;
    if (!verify_digest) return true;
    ContentStoreWorkspace local_workspace;
    auto& workspace = supplied_workspace == nullptr
        ? local_workspace
        : *supplied_workspace;
    std::uint32_t growth_events{};
    auto io = ContentStoreWorkspaceAccess::prepare_io(
        workspace, normalized_io_bytes(io_buffer_bytes), growth_events);
    (void)growth_events;
    return verify_blob(object, digest, expected_size, io);
}

ContentStoreBuildStats build_content_store(const std::filesystem::path& artifact,
                                           const std::filesystem::path& store_root,
                                           const std::filesystem::path& manifest_path,
                                           const ContentStoreOptions& options) {
    ContentStoreWorkspace workspace;
    return build_content_store(artifact, store_root, manifest_path, workspace, options);
}

ContentStoreBuildStats build_content_store(const std::filesystem::path& artifact,
                                           const std::filesystem::path& store_root,
                                           const std::filesystem::path& manifest_path,
                                           ContentStoreWorkspace& workspace,
                                           const ContentStoreOptions& options) {
    detail::NativeFile input(artifact, detail::NativeOpenMode::read_only);
    if (options.advise_sequential_io) input.advise_sequential();
    const auto input_size = input.size();
    if (input_size > options.limits.max_artifact_size) {
        throw std::runtime_error("content-store artifact exceeds configured size limit");
    }

    ContentChunking effective_chunking = options.chunking;
    if (options.auto_chunking) {
        ContentChunkingAutoOptions automatic;
        automatic.metadata_budget_bytes = options.metadata_budget_bytes;
        automatic.preferred = options.chunking;
        effective_chunking = choose_content_chunking(
            input_size, automatic, options.limits);
    } else {
        validate_chunking(effective_chunking, options.limits);
    }
    const auto io_bytes = normalized_io_bytes(options.io_buffer_bytes);
    const auto record_bytes = normalized_record_bytes(options.manifest_buffer_bytes);
    std::uint32_t growth_events{};
    auto io = ContentStoreWorkspaceAccess::prepare_io(workspace, io_bytes, growth_events);
    auto chunk = ContentStoreWorkspaceAccess::prepare_chunk(
        workspace, static_cast<std::size_t>(effective_chunking.max_bytes), growth_events);
    auto records = ContentStoreWorkspaceAccess::prepare_records(
        workspace, record_bytes, growth_events);

    ensure_parent(manifest_path);
    const auto part_path = part_path_for(manifest_path);
    TemporaryPath manifest_part(part_path);
    detail::NativeFile manifest(part_path, detail::NativeOpenMode::read_write_truncate);
    manifest.resize(ContentManifestMetadata::kHeaderBytes);

    ContentStoreBuildStats stats;
    stats.metadata.chunking = effective_chunking;
    stats.metadata.artifact_size = input_size;
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    detail::ArtifactSha256 artifact_hasher;
    detail::ArtifactSha256 entries_hasher;
    GearChunker chunker(effective_chunking);
    std::size_t chunk_used{};
    std::size_t records_used{};
    std::uint64_t input_offset{};
    std::uint64_t manifest_offset = ContentManifestMetadata::kHeaderBytes;

    const auto flush_records = [&]() {
        if (records_used == 0U) return;
        manifest.write_exact_at(manifest_offset, records.first(records_used));
        ++stats.manifest_write_calls;
        manifest_offset += records_used;
        records_used = 0U;
    };

    const auto emit_chunk = [&](std::span<const std::byte> bytes) {
        if (bytes.empty()) return;
        if (stats.metadata.chunk_count >= options.limits.max_chunks) {
            throw std::runtime_error("content-store artifact exceeds configured chunk limit");
        }
        const auto digest = sha256(bytes);
        const bool created = store_buffer(store_root, digest, bytes,
                                          options.fsync_on_commit,
                                          options.verify_existing_chunks);
        if (created) {
            ++stats.chunks_created;
            stats.bytes_created += bytes.size();
        } else {
            ++stats.chunks_reused;
            stats.bytes_reused += bytes.size();
        }
        if (records_used + ContentManifestMetadata::kEntryBytes > records.size()) {
            flush_records();
        }
        auto encoded = std::span<std::byte, ContentManifestMetadata::kEntryBytes>(
            records.data() + records_used, ContentManifestMetadata::kEntryBytes);
        encode_entry(encoded, static_cast<std::uint32_t>(bytes.size()), digest);
        entries_hasher.update(encoded);
        records_used += ContentManifestMetadata::kEntryBytes;
        ++stats.metadata.chunk_count;
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
                throw std::runtime_error("content-store chunker exceeded maximum chunk size");
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
            throw std::runtime_error("content-store chunk buffer overflow");
        }
        if (tail != 0U) {
            std::memcpy(chunk.data() + chunk_used,
                        input_bytes.data() + segment_start,
                        tail);
            chunk_used += tail;
        }
        if (options.discard_input_cache) input.advise_dont_need(input_offset, count);
        input_offset += count;
    }
    if (chunk_used != 0U) {
        emit_chunk(std::span<const std::byte>(chunk.data(), chunk_used));
    }
    flush_records();
    if (input.size() != input_size) {
        throw std::runtime_error("content-store artifact changed while being indexed");
    }

    stats.metadata.artifact_digest = artifact_hasher.finish();
    stats.metadata.entries_digest = entries_hasher.finish();
    std::array<std::byte, ContentManifestMetadata::kHeaderBytes> header{};
    encode_header(stats.metadata, header);
    manifest.write_exact_at(0U, header);
    ++stats.manifest_write_calls;
    manifest.resize(stats.metadata.encoded_size());
    if (options.fsync_on_commit) manifest.sync();
    manifest.close();
    atomic_replace(part_path, manifest_path);
    manifest_part.disarm();
    if (options.fsync_on_commit) sync_parent(manifest_path);

    // Hash through the retained I/O arena, then optionally make the manifest
    // available through the same digest-addressed range service as chunks.
    detail::NativeFile final_manifest(manifest_path, detail::NativeOpenMode::read_only);
    stats.metadata.manifest_digest = hash_native_file(
        final_manifest, io, stats.metadata.encoded_size());
    final_manifest.close();
    if (options.publish_manifest_to_store) {
        (void)store_file(store_root, manifest_path, stats.metadata.manifest_digest,
                         stats.metadata.encoded_size(), io, options.fsync_on_commit,
                         options.verify_existing_chunks);
    }
    return stats;
}

ContentManifestMetadata inspect_content_manifest(
    const std::filesystem::path& manifest_path,
    const ContentStoreLimits& limits) {
    ContentStoreWorkspace workspace;
    return inspect_content_manifest(manifest_path, workspace, limits);
}

ContentManifestMetadata inspect_content_manifest(
    const std::filesystem::path& manifest_path,
    ContentStoreWorkspace& workspace,
    const ContentStoreLimits& limits) {
    std::uint32_t growth_events{};
    auto records = ContentStoreWorkspaceAccess::prepare_records(
        workspace, kDefaultRecordBuffer, growth_events);
    (void)growth_events;
    return stream_manifest(manifest_path, records, limits,
                           [](const ContentChunkRef&) {});
}

ContentManifestWalkStats walk_content_manifest(
    const std::filesystem::path& manifest_path,
    ContentChunkCallback callback,
    void* context,
    const ContentManifestWalkOptions& options) {
    ContentStoreWorkspace workspace;
    return walk_content_manifest(manifest_path, workspace, callback, context, options);
}

ContentManifestWalkStats walk_content_manifest(
    const std::filesystem::path& manifest_path,
    ContentStoreWorkspace& workspace,
    ContentChunkCallback callback,
    void* context,
    const ContentManifestWalkOptions& options) {
    std::uint32_t growth_events{};
    auto records = ContentStoreWorkspaceAccess::prepare_records(
        workspace, normalized_record_bytes(options.manifest_buffer_bytes),
        growth_events);
    ContentManifestWalkStats stats;
    stats.metadata = stream_manifest(
        manifest_path, records, options.limits,
        [&](const ContentChunkRef& chunk) {
            ++stats.chunks_visited;
            stats.bytes_visited += chunk.length;
            if (callback != nullptr) callback(context, chunk);
        });
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

ContentStoreScanStats scan_missing_content_chunks(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    MissingContentChunkCallback callback,
    void* context,
    const ContentStoreScanOptions& options) {
    ContentStoreWorkspace workspace;
    return scan_missing_content_chunks(manifest_path, store_root, workspace,
                                       callback, context, options);
}

ContentStoreScanStats scan_missing_content_chunks(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    ContentStoreWorkspace& workspace,
    MissingContentChunkCallback callback,
    void* context,
    const ContentStoreScanOptions& options) {
    std::uint32_t growth_events{};
    auto records = ContentStoreWorkspaceAccess::prepare_records(
        workspace, normalized_record_bytes(options.manifest_buffer_bytes),
        growth_events);
    auto io = ContentStoreWorkspaceAccess::prepare_io(
        workspace, normalized_io_bytes(options.io_buffer_bytes), growth_events);
    ContentStoreScanStats stats;
    stats.metadata = stream_manifest(
        manifest_path, records, options.limits,
        [&](const ContentChunkRef& chunk) {
            const auto path = content_store_path(store_root, chunk.digest);
            bool available = regular_file_exact_size(path, chunk.length);
            bool corrupt = false;
            if (available && options.verify_chunk_digests) {
                available = verify_blob(path, chunk.digest, chunk.length, io);
                corrupt = !available;
            }
            if (available) {
                ++stats.available_chunks;
                stats.available_bytes += chunk.length;
            } else {
                ++stats.missing_chunks;
                stats.missing_bytes += chunk.length;
                if (corrupt) ++stats.corrupt_chunks;
                if (callback != nullptr) callback(context, chunk);
            }
        });
    stats.workspace_growth_events = growth_events;
    stats.workspace_reserved_bytes = workspace.resident_bytes();
    return stats;
}

ContentReconstructStats reconstruct_content_manifest(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    const ContentReconstructOptions& options) {
    ContentStoreWorkspace workspace;
    return reconstruct_content_manifest(manifest_path, store_root, output_path,
                                        workspace, options);
}

ContentReconstructStats reconstruct_content_manifest(
    const std::filesystem::path& manifest_path,
    const std::filesystem::path& store_root,
    const std::filesystem::path& output_path,
    ContentStoreWorkspace& workspace,
    const ContentReconstructOptions& options) {
    const auto io_bytes = normalized_io_bytes(options.io_buffer_bytes);
    std::uint32_t growth_events{};
    auto io = ContentStoreWorkspaceAccess::prepare_io(workspace, io_bytes, growth_events);
    auto records = ContentStoreWorkspaceAccess::prepare_records(
        workspace, normalized_record_bytes(options.manifest_buffer_bytes),
        growth_events);

    ensure_parent(output_path);
    const auto part_path = part_path_for(output_path);
    TemporaryPath output_part(part_path);
    detail::NativeFile output(part_path, detail::NativeOpenMode::read_write_truncate);
    detail::ArtifactSha256 artifact_hasher;
    ContentReconstructStats stats;
    try {
        throw_if_cancelled(options);
        stats.metadata = stream_manifest(
            manifest_path, records, options.limits,
            [&](const ContentChunkRef& chunk) {
                throw_if_cancelled(options);
                const auto path = content_store_path(store_root, chunk.digest);
                if (!regular_file_exact_size(path, chunk.length)) {
                    throw std::runtime_error("content-store chunk is missing or has wrong size: " +
                                             path.string());
                }
                detail::NativeFile input(path, detail::NativeOpenMode::read_only);
                if (options.advise_sequential_io) input.advise_sequential();
                detail::ArtifactSha256 chunk_hasher;
                std::uint64_t local_offset{};
                while (local_offset < chunk.length) {
                    throw_if_cancelled(options);
                    const auto count = static_cast<std::size_t>(
                        std::min<std::uint64_t>(chunk.length - local_offset, io.size()));
                    auto bytes = io.first(count);
                    input.read_exact_at(local_offset, bytes);
                    ++stats.chunk_read_calls;
                    chunk_hasher.update(bytes);
                    artifact_hasher.update(bytes);
                    output.write_exact_at(chunk.artifact_offset + local_offset, bytes);
                    ++stats.output_write_calls;
                    stats.bytes_read += count;
                    local_offset += count;
                }
                if (input.size() != chunk.length || chunk_hasher.finish() != chunk.digest) {
                    throw std::runtime_error("content-store chunk digest mismatch: " + path.string());
                }
                if (options.discard_chunk_cache) input.advise_dont_need(0U, chunk.length);
                ++stats.chunks_read;
            });
        throw_if_cancelled(options);
        if (artifact_hasher.finish() != stats.metadata.artifact_digest) {
            throw std::runtime_error("reconstructed content artifact digest mismatch");
        }
        output.resize(stats.metadata.artifact_size);
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

} // namespace toxsync
