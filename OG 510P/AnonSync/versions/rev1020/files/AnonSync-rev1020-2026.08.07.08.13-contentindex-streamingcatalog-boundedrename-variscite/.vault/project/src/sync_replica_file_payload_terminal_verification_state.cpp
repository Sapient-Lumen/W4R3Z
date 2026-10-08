#include "sync_replica_file_payload_terminal_verification_state.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_posix_regular_file_snapshot_codec.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

namespace anonsync {
namespace {

constexpr std::string_view kMagic =
    "anonsync:sync-replica-file-payload-terminal-verification-slot:v1\n";
constexpr std::uint64_t kEncodedU64Bytes = 8U;
constexpr std::uint64_t kEncodedU32Bytes = 4U;
constexpr std::uint64_t kDigestTextBytes = 64U;
constexpr std::uint64_t kMetadataBytes =
    kSyncPosixRegularFileSnapshotMetadataEncodedBytes;
constexpr std::uint64_t kHashWordsBytes = 8U * kEncodedU32Bytes;
constexpr std::uint64_t kHashBufferBytes = 64U;
constexpr std::uint64_t kBodyBytes =
    kDigestTextBytes + kMetadataBytes + kEncodedU64Bytes +
    kDigestTextBytes + kEncodedU64Bytes + kMetadataBytes +
    kEncodedU64Bytes + kHashWordsBytes + kHashBufferBytes +
    (2U * kEncodedU64Bytes);
constexpr std::uint64_t kSlotBytes =
    static_cast<std::uint64_t>(kMagic.size()) + kBodyBytes + kDigestTextBytes;
constexpr std::uint64_t kJournalBytes = 2U * kSlotBytes;

[[noreturn]] void invalid(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " terminal payload verification " +
        std::string(reason));
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

[[nodiscard]] ResumableSha256Checkpoint initial_checkpoint() {
    return ResumableSha256{}.checkpoint();
}

void validate_state(
    const SyncReplicaFilePayloadTerminalVerificationState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    if (max_payload_bytes == 0U ||
        max_payload_bytes > kSha256MaximumMessageBytes) {
        invalid(label, "state has an invalid configured payload ceiling");
    }
    if (!is_lowercase_sha256_hex(state.store_identity_sha256)) {
        invalid(label, "state contains an invalid store-identity digest");
    }
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        state.store_identity_metadata, std::nullopt,
        std::string(label) + " terminal verification identity");
    if (state.generation == 0U) {
        invalid(label, "state contains generation zero");
    }
    if (!is_lowercase_sha256_hex(state.content_sha256)) {
        invalid(label, "state contains an invalid content digest");
    }
    if (state.total_size_bytes == 0U ||
        state.total_size_bytes > max_payload_bytes) {
        invalid(label, "state contains an invalid total extent");
    }
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        state.staged_prefix_metadata, state.total_size_bytes,
        std::string(label) + " terminal verification staged prefix");
    if (state.staged_prefix_metadata.size_bytes != state.total_size_bytes ||
        state.verified_offset_bytes >= state.total_size_bytes) {
        invalid(label, "state metadata or progress is not a canonical nonterminal complete-prefix checkpoint");
    }
    validate_resumable_sha256_checkpoint_or_throw(
        state.hash,
        std::string(label) + " terminal verification hash");
    if (state.hash.total_bytes != state.verified_offset_bytes) {
        invalid(label, "state hash does not match verified progress");
    }
    if (state.verified_offset_bytes == 0U &&
        state.hash != initial_checkpoint()) {
        invalid(label, "state zero progress does not contain the initial hash");
    }
}

class Cursor final {
public:
    Cursor(std::string_view bytes, std::string_view label)
        : bytes_(bytes), label_(label) {}

    [[nodiscard]] std::string_view take(std::size_t count) {
        if (count > bytes_.size() - position_) {
            invalid(label_, "slot is truncated");
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

    [[nodiscard]] SyncPosixRegularFileSnapshotMetadata take_metadata() {
        return parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
            take(static_cast<std::size_t>(kMetadataBytes)),
            std::string(label_) + " terminal verification slot");
    }

    [[nodiscard]] bool exhausted() const noexcept {
        return position_ == bytes_.size();
    }

private:
    std::string_view bytes_;
    std::string_view label_;
    std::size_t position_ = 0U;
};

[[nodiscard]] bool all_zero(std::string_view bytes) noexcept {
    return std::all_of(
        bytes.begin(), bytes.end(), [](char value) { return value == '\0'; });
}

}  // namespace

std::uint64_t
sync_replica_file_payload_terminal_verification_slot_exact_bytes() noexcept {
    return kSlotBytes;
}

std::uint64_t
sync_replica_file_payload_terminal_verification_journal_exact_bytes() noexcept {
    return kJournalBytes;
}

std::string
serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
    const SyncReplicaFilePayloadTerminalVerificationState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "terminal payload verification serialization label must not be empty");
    }
    validate_state(state, max_payload_bytes, label);
    if (kSlotBytes > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error(
            std::string(label) + " terminal verification slot exceeds size_t");
    }

    std::string encoded;
    encoded.reserve(static_cast<std::size_t>(kSlotBytes));
    encoded.append(kMagic);
    encoded.append(state.store_identity_sha256);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        encoded, state.store_identity_metadata);
    append_u64(encoded, state.generation);
    encoded.append(state.content_sha256);
    append_u64(encoded, state.total_size_bytes);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        encoded, state.staged_prefix_metadata);
    append_u64(encoded, state.verified_offset_bytes);
    for (const std::uint32_t word : state.hash.hash_words) {
        append_u32(encoded, word);
    }
    encoded.append(
        reinterpret_cast<const char*>(state.hash.buffered_block.data()),
        state.hash.buffered_block.size());
    append_u64(encoded, state.hash.total_bytes);
    append_u64(encoded, state.hash.buffered_bytes);
    encoded.append(sha256_hex(encoded));
    if (encoded.size() != kSlotBytes) {
        throw std::logic_error(
            std::string(label) + " terminal verification slot size drifted");
    }
    return encoded;
}

SyncReplicaFilePayloadTerminalVerificationState
parse_sync_replica_file_payload_terminal_verification_state_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "terminal payload verification parsing label must not be empty");
    }
    if (bytes.size() != kSlotBytes) {
        invalid(label, "slot length is not the exact v1 size");
    }
    const std::size_t payload_bytes =
        bytes.size() - static_cast<std::size_t>(kDigestTextBytes);
    const std::string_view expected_checksum = bytes.substr(payload_bytes);
    if (!is_lowercase_sha256_hex(expected_checksum) ||
        sha256_hex(std::string(bytes.substr(0U, payload_bytes))) !=
            expected_checksum) {
        invalid(label, "slot checksum is invalid");
    }

    Cursor cursor(bytes.substr(0U, payload_bytes), label);
    if (cursor.take(kMagic.size()) != kMagic) {
        invalid(label, "slot has an incompatible format generation");
    }

    SyncReplicaFilePayloadTerminalVerificationState state;
    state.store_identity_sha256 = std::string(cursor.take(64U));
    state.store_identity_metadata = cursor.take_metadata();
    state.generation = cursor.take_u64();
    state.content_sha256 = std::string(cursor.take(64U));
    state.total_size_bytes = cursor.take_u64();
    state.staged_prefix_metadata = cursor.take_metadata();
    state.verified_offset_bytes = cursor.take_u64();
    for (std::uint32_t& word : state.hash.hash_words) {
        word = cursor.take_u32();
    }
    const std::string_view buffered = cursor.take(64U);
    std::copy(
        buffered.begin(), buffered.end(),
        reinterpret_cast<char*>(state.hash.buffered_block.data()));
    state.hash.total_bytes = cursor.take_u64();
    const std::uint64_t buffered_bytes = cursor.take_u64();
    if (buffered_bytes > std::numeric_limits<std::uint32_t>::max()) {
        invalid(label, "slot contains an out-of-range hash tail count");
    }
    state.hash.buffered_bytes =
        static_cast<std::uint32_t>(buffered_bytes);
    if (!cursor.exhausted()) invalid(label, "slot contains trailing bytes");
    validate_state(state, max_payload_bytes, label);
    return state;
}

std::string
initial_sync_replica_file_payload_terminal_verification_journal_or_throw(
    const SyncReplicaFilePayloadTerminalVerificationState& state,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    const std::string slot =
        serialize_sync_replica_file_payload_terminal_verification_state_or_throw(
            state, max_payload_bytes, label);
    if (kJournalBytes > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error(
            std::string(label) + " terminal verification journal exceeds size_t");
    }
    std::string journal;
    journal.reserve(static_cast<std::size_t>(kJournalBytes));
    journal.append(slot);
    journal.append(static_cast<std::size_t>(kSlotBytes), '\0');
    return journal;
}

SyncReplicaFilePayloadTerminalVerificationJournal
parse_sync_replica_file_payload_terminal_verification_journal_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "terminal payload verification journal label must not be empty");
    }
    if (bytes.size() != kJournalBytes) {
        invalid(label, "journal length is not the exact v1 size");
    }

    std::array<std::optional<SyncReplicaFilePayloadTerminalVerificationState>,
               2U>
        states;
    std::uint32_t invalid_nonzero = 0U;
    for (std::uint32_t slot = 0U; slot < 2U; ++slot) {
        const std::size_t offset =
            static_cast<std::size_t>(slot * kSlotBytes);
        const std::string_view encoded = bytes.substr(
            offset, static_cast<std::size_t>(kSlotBytes));
        if (all_zero(encoded)) continue;
        try {
            states[slot] =
                parse_sync_replica_file_payload_terminal_verification_state_or_throw(
                    encoded, max_payload_bytes,
                    std::string(label) + " slot " + std::to_string(slot));
        } catch (const std::invalid_argument&) {
            ++invalid_nonzero;
        }
    }

    if (!states[0U].has_value() && !states[1U].has_value()) {
        invalid(label, "journal has no valid committed slot");
    }
    std::uint32_t latest = states[1U].has_value() ? 1U : 0U;
    if (states[0U].has_value() && states[1U].has_value()) {
        if (states[0U]->generation == states[1U]->generation) {
            if (*states[0U] != *states[1U]) {
                invalid(label, "journal has conflicting equal generations");
            }
            latest = 1U;
        } else if (states[0U]->generation > states[1U]->generation) {
            latest = 0U;
        }
    }

    SyncReplicaFilePayloadTerminalVerificationJournal out;
    out.slots = states;
    out.latest_state = *states[latest];
    out.latest_slot_index = latest;
    out.valid_slot_count = static_cast<std::uint32_t>(
        (states[0U].has_value() ? 1U : 0U) +
        (states[1U].has_value() ? 1U : 0U));
    out.invalid_nonzero_slot_count = invalid_nonzero;
    return out;
}

}  // namespace anonsync

#endif
