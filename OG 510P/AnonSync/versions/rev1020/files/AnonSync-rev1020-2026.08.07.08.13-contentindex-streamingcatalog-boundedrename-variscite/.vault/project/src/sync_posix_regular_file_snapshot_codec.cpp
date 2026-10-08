#include "sync_posix_regular_file_snapshot_codec.hpp"

#if !defined(_WIN32)

#include <bit>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>

#include <sys/stat.h>

namespace anonsync {
namespace {

constexpr std::size_t kEncodedU64Bytes = 8U;

[[noreturn]] void invalid(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " " + std::string(reason));
}

void append_u64(std::string& output, std::uint64_t value) {
    for (unsigned shift = 56U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

[[nodiscard]] std::uint64_t read_u64(
    std::string_view bytes,
    std::size_t& position,
    std::string_view label) {
    if (bytes.size() - position < kEncodedU64Bytes) {
        invalid(label, "metadata is truncated");
    }
    std::uint64_t value = 0U;
    for (std::size_t index = 0U; index < kEncodedU64Bytes; ++index) {
        value = (value << 8U) |
                static_cast<std::uint64_t>(
                    static_cast<unsigned char>(bytes[position + index]));
    }
    position += kEncodedU64Bytes;
    return value;
}

}  // namespace

void append_sync_posix_regular_file_snapshot_metadata_binary(
    std::string& output,
    const SyncPosixRegularFileSnapshotMetadata& metadata) {
    append_u64(output, metadata.device);
    append_u64(output, metadata.inode);
    append_u64(output, metadata.size_bytes);
    append_u64(output, metadata.link_count);
    append_u64(output, metadata.owner_user_id);
    append_u64(output, metadata.owner_group_id);
    append_u64(output, metadata.mode);
    append_u64(
        output, std::bit_cast<std::uint64_t>(metadata.modification_seconds));
    append_u64(output, metadata.modification_nanoseconds);
    append_u64(
        output, std::bit_cast<std::uint64_t>(metadata.status_change_seconds));
    append_u64(output, metadata.status_change_nanoseconds);
}

SyncPosixRegularFileSnapshotMetadata
parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
    std::string_view exact_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "POSIX regular-file metadata parse label must not be empty");
    }
    if (exact_bytes.size() !=
        kSyncPosixRegularFileSnapshotMetadataEncodedBytes) {
        invalid(label, "metadata length is not the canonical eleven-field width");
    }

    std::size_t position = 0U;
    SyncPosixRegularFileSnapshotMetadata metadata;
    metadata.device = read_u64(exact_bytes, position, label);
    metadata.inode = read_u64(exact_bytes, position, label);
    metadata.size_bytes = read_u64(exact_bytes, position, label);
    metadata.link_count = read_u64(exact_bytes, position, label);
    metadata.owner_user_id = read_u64(exact_bytes, position, label);
    metadata.owner_group_id = read_u64(exact_bytes, position, label);

    const std::uint64_t encoded_mode =
        read_u64(exact_bytes, position, label);
    if (encoded_mode > std::numeric_limits<std::uint32_t>::max()) {
        invalid(label, "contains an out-of-range mode");
    }
    metadata.mode = static_cast<std::uint32_t>(encoded_mode);
    metadata.modification_seconds = std::bit_cast<std::int64_t>(
        read_u64(exact_bytes, position, label));

    const std::uint64_t modification_nanoseconds =
        read_u64(exact_bytes, position, label);
    if (modification_nanoseconds >
        std::numeric_limits<std::uint32_t>::max()) {
        invalid(label, "contains an out-of-range modification fraction");
    }
    metadata.modification_nanoseconds =
        static_cast<std::uint32_t>(modification_nanoseconds);
    metadata.status_change_seconds = std::bit_cast<std::int64_t>(
        read_u64(exact_bytes, position, label));

    const std::uint64_t status_change_nanoseconds =
        read_u64(exact_bytes, position, label);
    if (status_change_nanoseconds >
        std::numeric_limits<std::uint32_t>::max()) {
        invalid(label, "contains an out-of-range status-change fraction");
    }
    metadata.status_change_nanoseconds =
        static_cast<std::uint32_t>(status_change_nanoseconds);
    if (position != exact_bytes.size()) {
        throw std::logic_error(
            std::string(label) + " metadata decoder width drifted");
    }
    return metadata;
}

void validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
    const SyncPosixRegularFileSnapshotMetadata& metadata,
    std::optional<std::uint64_t> maximum_size_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "POSIX regular-file metadata validation label must not be empty");
    }
    if (!S_ISREG(static_cast<mode_t>(metadata.mode))) {
        invalid(label, "contains non-regular metadata");
    }
    if ((metadata.mode & 07777U) != (S_IRUSR | S_IWUSR)) {
        invalid(label, "contains metadata without exact mode 0600");
    }
    if (metadata.link_count != 1U) {
        invalid(label, "contains metadata without an exact single link");
    }
    if (maximum_size_bytes.has_value() &&
        metadata.size_bytes > *maximum_size_bytes) {
        invalid(label, "contains a payload beyond the configured byte ceiling");
    }
    if (metadata.modification_nanoseconds >= 1000000000U ||
        metadata.status_change_nanoseconds >= 1000000000U) {
        invalid(label, "contains an invalid timestamp fraction");
    }
}

}  // namespace anonsync

#endif
