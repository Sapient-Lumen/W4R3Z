#include "sync_replica_file_payload_verification_index.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_posix_regular_file_snapshot_codec.hpp"

#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kMagic =
    "anonsync:sync-replica-file-payload-verification-index:v1\n";
constexpr std::uint64_t kEncodedU64Bytes = 8U;
constexpr std::uint64_t kDigestTextBytes = 64U;
constexpr std::uint64_t kMetadataBytes =
    kSyncPosixRegularFileSnapshotMetadataEncodedBytes;
constexpr std::uint64_t kRecordBytes = kDigestTextBytes + kMetadataBytes;
constexpr std::uint64_t kHeaderBytes =
    static_cast<std::uint64_t>(kMagic.size()) + kDigestTextBytes +
    kMetadataBytes + (2U * kEncodedU64Bytes);
constexpr std::uint64_t kTrailerBytes = kDigestTextBytes;

[[noreturn]] void invalid(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " verification index " + std::string(reason));
}

[[nodiscard]] std::uint64_t checked_add(
    std::uint64_t left,
    std::uint64_t right,
    std::string_view label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::overflow_error(
            std::string(label) + " verification index size overflow");
    }
    return left + right;
}

[[nodiscard]] std::uint64_t checked_multiply(
    std::uint64_t left,
    std::uint64_t right,
    std::string_view label) {
    if (left != 0U &&
        right > std::numeric_limits<std::uint64_t>::max() / left) {
        throw std::overflow_error(
            std::string(label) + " verification index size overflow");
    }
    return left * right;
}

void append_u64(std::string& output, std::uint64_t value) {
    for (unsigned shift = 56U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

class Cursor final {
public:
    Cursor(std::string_view bytes, std::string_view label)
        : bytes_(bytes), label_(label) {}

    [[nodiscard]] std::string_view take(std::size_t count) {
        if (count > bytes_.size() - position_) {
            invalid(label_, "is truncated");
        }
        const std::string_view out = bytes_.substr(position_, count);
        position_ += count;
        return out;
    }

    [[nodiscard]] std::uint64_t take_u64() {
        const std::string_view encoded =
            take(static_cast<std::size_t>(kEncodedU64Bytes));
        std::uint64_t value = 0U;
        for (const unsigned char byte : encoded) {
            value = (value << 8U) | static_cast<std::uint64_t>(byte);
        }
        return value;
    }

    [[nodiscard]] SyncPosixRegularFileSnapshotMetadata take_metadata() {
        return parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
            take(static_cast<std::size_t>(kMetadataBytes)),
            std::string(label_) + " verification index");
    }

    [[nodiscard]] bool exhausted() const noexcept {
        return position_ == bytes_.size();
    }

private:
    std::string_view bytes_;
    std::string_view label_;
    std::size_t position_ = 0U;
};

void validate_index(
    const SyncReplicaFilePayloadVerificationIndex& index,
    std::uint64_t max_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    if (!is_lowercase_sha256_hex(index.store_identity_sha256)) {
        invalid(label, "contains an invalid store-identity digest");
    }
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        index.store_identity_metadata, std::nullopt,
        std::string(label) + " verification index");
    if (index.entries.size() > max_entries) {
        invalid(label, "entry count exceeds the configured ceiling");
    }
    if (index.indexed_bytes > max_indexed_bytes) {
        invalid(label, "aggregate bytes exceed the configured ceiling");
    }

    std::uint64_t observed_bytes = 0U;
    std::string_view previous;
    for (const auto& entry : index.entries) {
        if (!is_lowercase_sha256_hex(entry.content_sha256)) {
            invalid(label, "contains an invalid payload digest");
        }
        if (!previous.empty() && previous >= entry.content_sha256) {
            invalid(label, "payload entries are not strictly sorted");
        }
        validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
            entry.metadata, max_indexed_bytes,
            std::string(label) + " verification index");
        if (entry.metadata.size_bytes > max_indexed_bytes - observed_bytes) {
            invalid(label, "payload byte sum exceeds the configured ceiling");
        }
        observed_bytes += entry.metadata.size_bytes;
        previous = entry.content_sha256;
    }
    if (observed_bytes != index.indexed_bytes) {
        invalid(label, "aggregate byte total does not match its entries");
    }
}

}  // namespace

std::uint64_t
sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
    std::uint64_t max_entries,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload verification index size label must not be empty");
    }
    return checked_add(
        checked_add(
            kHeaderBytes,
            checked_multiply(max_entries, kRecordBytes, label), label),
        kTrailerBytes, label);
}

std::string serialize_sync_replica_file_payload_verification_index_or_throw(
    const SyncReplicaFilePayloadVerificationIndex& index,
    std::uint64_t max_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload verification index serialization label must not be empty");
    }
    validate_index(index, max_entries, max_indexed_bytes, label);
    const std::uint64_t exact_size = checked_add(
        checked_add(
            kHeaderBytes,
            checked_multiply(
                static_cast<std::uint64_t>(index.entries.size()),
                kRecordBytes, label),
            label),
        kTrailerBytes, label);
    if (exact_size > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error(
            std::string(label) + " verification index exceeds size_t");
    }

    std::string encoded;
    encoded.reserve(static_cast<std::size_t>(exact_size));
    encoded.append(kMagic);
    encoded.append(index.store_identity_sha256);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        encoded, index.store_identity_metadata);
    append_u64(encoded, static_cast<std::uint64_t>(index.entries.size()));
    append_u64(encoded, index.indexed_bytes);
    for (const auto& entry : index.entries) {
        encoded.append(entry.content_sha256);
        append_sync_posix_regular_file_snapshot_metadata_binary(
            encoded, entry.metadata);
    }
    encoded.append(sha256_hex(encoded));
    if (encoded.size() != exact_size) {
        throw std::logic_error(
            std::string(label) + " verification index encoded size drifted");
    }
    return encoded;
}

SyncReplicaFilePayloadVerificationIndex
parse_sync_replica_file_payload_verification_index_or_throw(
    std::string_view bytes,
    std::uint64_t max_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload verification index parse label must not be empty");
    }
    const std::uint64_t maximum =
        sync_replica_file_payload_verification_index_maximum_bytes_or_throw(
            max_entries, label);
    if (bytes.size() > maximum) {
        invalid(label, "exceeds the configured encoded-size ceiling");
    }
    const std::uint64_t minimum = kHeaderBytes + kTrailerBytes;
    if (bytes.size() < minimum) invalid(label, "is truncated");

    const std::string_view payload =
        bytes.substr(0U, bytes.size() - static_cast<std::size_t>(kTrailerBytes));
    const std::string_view checksum =
        bytes.substr(bytes.size() - static_cast<std::size_t>(kTrailerBytes));
    Sha256DigestBuilder checksum_builder;
    checksum_builder.update(payload);
    if (!is_lowercase_sha256_hex(checksum) ||
        checksum_builder.finish_hex() != checksum) {
        invalid(label, "checksum does not match its bytes");
    }

    Cursor cursor(payload, label);
    if (cursor.take(kMagic.size()) != kMagic) {
        invalid(label, "has an incompatible format generation");
    }

    SyncReplicaFilePayloadVerificationIndex out;
    out.store_identity_sha256 =
        std::string(cursor.take(static_cast<std::size_t>(kDigestTextBytes)));
    out.store_identity_metadata = cursor.take_metadata();
    const std::uint64_t entry_count = cursor.take_u64();
    out.indexed_bytes = cursor.take_u64();
    if (entry_count > max_entries) {
        invalid(label, "entry count exceeds the configured ceiling");
    }
    const std::uint64_t expected_payload_size = checked_add(
        kHeaderBytes,
        checked_multiply(entry_count, kRecordBytes, label), label);
    if (expected_payload_size != payload.size()) {
        invalid(label, "length does not match its entry count");
    }
    if (entry_count > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error(
            std::string(label) + " verification index entry count exceeds size_t");
    }
    out.entries.reserve(static_cast<std::size_t>(entry_count));
    for (std::uint64_t index = 0U; index < entry_count; ++index) {
        SyncReplicaFilePayloadVerificationIndexEntry entry;
        entry.content_sha256 =
            std::string(cursor.take(static_cast<std::size_t>(kDigestTextBytes)));
        entry.metadata = cursor.take_metadata();
        out.entries.push_back(std::move(entry));
    }
    if (!cursor.exhausted()) invalid(label, "contains trailing payload bytes");
    validate_index(out, max_entries, max_indexed_bytes, label);
    return out;
}

}  // namespace anonsync

#endif
