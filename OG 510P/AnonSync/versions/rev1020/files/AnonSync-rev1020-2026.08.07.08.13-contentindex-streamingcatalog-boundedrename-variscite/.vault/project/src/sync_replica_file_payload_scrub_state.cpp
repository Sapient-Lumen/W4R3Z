#include "sync_replica_file_payload_scrub_state.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_posix_regular_file_snapshot_codec.hpp"

#include <algorithm>
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
    "anonsync:sync-replica-file-payload-scrub-state:v1\n";
constexpr std::uint64_t kEncodedU64Bytes = 8U;
constexpr std::uint64_t kEncodedU32Bytes = 4U;
constexpr std::uint64_t kDigestTextBytes = 64U;
constexpr std::uint64_t kMetadataBytes =
    kSyncPosixRegularFileSnapshotMetadataEncodedBytes;
constexpr std::uint64_t kHashWordCount = 8U;
constexpr std::uint64_t kHashWordsBytes =
    kHashWordCount * kEncodedU32Bytes;
constexpr std::uint64_t kHashBufferBytes = 64U;
constexpr std::uint64_t kBodyBytes =
    kDigestTextBytes + kMetadataBytes +
    (3U * kEncodedU64Bytes) +
    kDigestTextBytes + kDigestTextBytes + kMetadataBytes +
    kEncodedU64Bytes + kHashWordsBytes + kHashBufferBytes +
    (2U * kEncodedU64Bytes) + kDigestTextBytes;
constexpr std::uint64_t kExactBytes =
    static_cast<std::uint64_t>(kMagic.size()) + kBodyBytes +
    kDigestTextBytes;

[[noreturn]] void invalid(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " payload scrub state " + std::string(reason));
}

void append_u64(std::string& output, std::uint64_t value) {
    for (unsigned shift = 56U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

void append_u32(std::string& output, std::uint32_t value) {
    for (unsigned shift = 24U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

void append_optional_digest(std::string& output, std::string_view digest) {
    if (digest.empty()) {
        output.append(static_cast<std::size_t>(kDigestTextBytes), '\0');
    } else {
        output.append(digest);
    }
}

[[nodiscard]] bool is_zero_metadata(
    const SyncPosixRegularFileSnapshotMetadata& metadata) noexcept {
    return metadata == SyncPosixRegularFileSnapshotMetadata{};
}

[[nodiscard]] ResumableSha256Checkpoint initial_hash_checkpoint() {
    ResumableSha256 initial;
    return initial.checkpoint();
}

void validate_state(
    const SyncReplicaFilePayloadScrubState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    if (max_payload_bytes == 0U ||
        max_payload_bytes > kSha256MaximumMessageBytes) {
        invalid(label, "has an invalid configured payload ceiling");
    }
    if (!is_lowercase_sha256_hex(state.store_identity_sha256)) {
        invalid(label, "contains an invalid store-identity digest");
    }
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        state.store_identity_metadata,
        std::nullopt,
        std::string(label) + " payload scrub state");
    if (state.generation == 0U) {
        invalid(label, "contains generation zero");
    }
    if (!state.cursor_after_content_sha256.empty() &&
        !is_lowercase_sha256_hex(state.cursor_after_content_sha256)) {
        invalid(label, "contains an invalid completed cursor digest");
    }

    switch (state.disposition) {
    case SyncReplicaFilePayloadScrubStateDisposition::Idle:
        if (!state.active_content_sha256.empty() ||
            !state.observed_content_sha256.empty() ||
            state.active_offset_bytes != 0U ||
            !is_zero_metadata(state.active_metadata) ||
            state.active_hash != initial_hash_checkpoint()) {
            invalid(label, "idle form contains active progress");
        }
        break;
    case SyncReplicaFilePayloadScrubStateDisposition::Prepared:
    case SyncReplicaFilePayloadScrubStateDisposition::Progress:
    case SyncReplicaFilePayloadScrubStateDisposition::IntegrityFailure: {
        if (!is_lowercase_sha256_hex(state.active_content_sha256)) {
            invalid(label, "contains an invalid active payload digest");
        }
        if (state.active_content_sha256 ==
            state.cursor_after_content_sha256) {
            invalid(label, "active payload equals its completed cursor");
        }
        validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
            state.active_metadata,
            max_payload_bytes,
            std::string(label) + " payload scrub state");
        validate_resumable_sha256_checkpoint_or_throw(
            state.active_hash, std::string(label) + " active hash");
        if (state.active_hash.total_bytes != state.active_offset_bytes) {
            invalid(label, "active offset does not match hash progress");
        }
        if (state.disposition ==
            SyncReplicaFilePayloadScrubStateDisposition::Prepared) {
            if (state.active_offset_bytes != 0U ||
                state.active_hash != initial_hash_checkpoint()) {
                invalid(label, "prepared form is not at the initial cutpoint");
            }
            if (!state.observed_content_sha256.empty()) {
                invalid(label, "prepared form contains a terminal digest");
            }
        } else if (state.disposition ==
                   SyncReplicaFilePayloadScrubStateDisposition::Progress) {
            if (state.active_offset_bytes == 0U ||
                state.active_offset_bytes >= state.active_metadata.size_bytes) {
                invalid(label, "contains a non-progressing active extent");
            }
            if (!state.observed_content_sha256.empty()) {
                invalid(label, "progress form contains a terminal digest");
            }
        } else {
            if (state.active_offset_bytes !=
                state.active_metadata.size_bytes) {
                invalid(label, "failure form is not at exact completion");
            }
            if (!is_lowercase_sha256_hex(state.observed_content_sha256) ||
                state.observed_content_sha256 ==
                    state.active_content_sha256) {
                invalid(label, "failure form contains an invalid observed digest");
            }
            ResumableSha256 completed(state.active_hash, "scrub failure hash");
            if (completed.finish_hex() != state.observed_content_sha256) {
                invalid(label, "failure digest does not match its hash state");
            }
        }
        break;
    }
    default:
        invalid(label, "contains an unknown disposition");
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
        std::uint64_t value = 0U;
        for (const unsigned char byte : take(8U)) {
            value = (value << 8U) | static_cast<std::uint64_t>(byte);
        }
        return value;
    }

    [[nodiscard]] std::uint32_t take_u32() {
        std::uint32_t value = 0U;
        for (const unsigned char byte : take(4U)) {
            value = (value << 8U) | static_cast<std::uint32_t>(byte);
        }
        return value;
    }

    [[nodiscard]] std::string take_optional_digest() {
        const std::string_view field =
            take(static_cast<std::size_t>(kDigestTextBytes));
        if (std::all_of(
                field.begin(), field.end(),
                [](char byte) { return byte == '\0'; })) {
            return {};
        }
        if (std::find(field.begin(), field.end(), '\0') != field.end()) {
            invalid(label_, "contains a partially empty digest field");
        }
        return std::string(field);
    }

    [[nodiscard]] SyncPosixRegularFileSnapshotMetadata take_metadata() {
        return parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
            take(static_cast<std::size_t>(kMetadataBytes)),
            std::string(label_) + " payload scrub state");
    }

    [[nodiscard]] bool exhausted() const noexcept {
        return position_ == bytes_.size();
    }

private:
    std::string_view bytes_;
    std::string_view label_;
    std::size_t position_ = 0U;
};

}  // namespace

std::uint64_t
sync_replica_file_payload_scrub_state_exact_bytes() noexcept {
    return kExactBytes;
}

SyncReplicaFilePayloadScrubState
initial_sync_replica_file_payload_scrub_state_or_throw(
    std::string store_identity_sha256,
    SyncPosixRegularFileSnapshotMetadata store_identity_metadata,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload scrub initial-state label must not be empty");
    }
    SyncReplicaFilePayloadScrubState state;
    state.store_identity_sha256 = std::move(store_identity_sha256);
    state.store_identity_metadata = store_identity_metadata;
    state.active_hash = initial_hash_checkpoint();
    validate_state(state, kSha256MaximumMessageBytes, label);
    return state;
}

std::string serialize_sync_replica_file_payload_scrub_state_or_throw(
    const SyncReplicaFilePayloadScrubState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload scrub serialization label must not be empty");
    }
    validate_state(state, max_payload_bytes, label);
    if (kExactBytes > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error(
            std::string(label) + " payload scrub state exceeds size_t");
    }

    std::string encoded;
    encoded.reserve(static_cast<std::size_t>(kExactBytes));
    encoded.append(kMagic);
    encoded.append(state.store_identity_sha256);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        encoded, state.store_identity_metadata);
    append_u64(encoded, state.generation);
    append_u64(encoded, state.completed_cycles);
    append_u64(encoded, static_cast<std::uint64_t>(state.disposition));
    append_optional_digest(encoded, state.cursor_after_content_sha256);
    append_optional_digest(encoded, state.active_content_sha256);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        encoded, state.active_metadata);
    append_u64(encoded, state.active_offset_bytes);
    for (const std::uint32_t word : state.active_hash.hash_words) {
        append_u32(encoded, word);
    }
    encoded.append(
        reinterpret_cast<const char*>(state.active_hash.buffered_block.data()),
        state.active_hash.buffered_block.size());
    append_u64(encoded, state.active_hash.total_bytes);
    append_u64(encoded, state.active_hash.buffered_bytes);
    append_optional_digest(encoded, state.observed_content_sha256);
    encoded.append(sha256_hex(encoded));
    if (encoded.size() != kExactBytes) {
        throw std::logic_error(
            std::string(label) + " payload scrub encoded size drifted");
    }
    return encoded;
}

SyncReplicaFilePayloadScrubState
parse_sync_replica_file_payload_scrub_state_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload scrub parsing label must not be empty");
    }
    if (bytes.size() != kExactBytes) {
        invalid(label, "length is not the exact v1 size");
    }
    const std::size_t payload_bytes =
        bytes.size() - static_cast<std::size_t>(kDigestTextBytes);
    const std::string_view expected_checksum = bytes.substr(payload_bytes);
    if (!is_lowercase_sha256_hex(expected_checksum) ||
        sha256_hex(std::string(bytes.substr(0U, payload_bytes))) !=
            expected_checksum) {
        invalid(label, "checksum is invalid");
    }

    Cursor cursor(bytes.substr(0U, payload_bytes), label);
    if (cursor.take(kMagic.size()) != kMagic) {
        invalid(label, "has an incompatible format generation");
    }

    SyncReplicaFilePayloadScrubState state;
    state.store_identity_sha256 = std::string(
        cursor.take(static_cast<std::size_t>(kDigestTextBytes)));
    state.store_identity_metadata = cursor.take_metadata();
    state.generation = cursor.take_u64();
    state.completed_cycles = cursor.take_u64();
    const std::uint64_t disposition = cursor.take_u64();
    if (disposition > std::numeric_limits<std::uint8_t>::max()) {
        invalid(label, "contains an out-of-range disposition");
    }
    state.disposition = static_cast<
        SyncReplicaFilePayloadScrubStateDisposition>(disposition);
    state.cursor_after_content_sha256 = cursor.take_optional_digest();
    state.active_content_sha256 = cursor.take_optional_digest();
    state.active_metadata = cursor.take_metadata();
    state.active_offset_bytes = cursor.take_u64();
    for (std::uint32_t& word : state.active_hash.hash_words) {
        word = cursor.take_u32();
    }
    const std::string_view buffered = cursor.take(64U);
    std::copy(
        buffered.begin(), buffered.end(),
        reinterpret_cast<char*>(state.active_hash.buffered_block.data()));
    state.active_hash.total_bytes = cursor.take_u64();
    const std::uint64_t buffered_bytes = cursor.take_u64();
    if (buffered_bytes > std::numeric_limits<std::uint32_t>::max()) {
        invalid(label, "contains an out-of-range hash tail count");
    }
    state.active_hash.buffered_bytes =
        static_cast<std::uint32_t>(buffered_bytes);
    state.observed_content_sha256 = cursor.take_optional_digest();
    if (!cursor.exhausted()) invalid(label, "contains trailing bytes");
    validate_state(state, max_payload_bytes, label);
    return state;
}

}  // namespace anonsync

#endif
