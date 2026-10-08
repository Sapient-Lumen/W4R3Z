#include "sync_replica_file_payload_retention_mark.hpp"

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

namespace anonsync {
namespace {

constexpr std::string_view kMagic =
    "anonsync:sync-replica-file-payload-retention-mark:v1\n";
constexpr std::uint64_t kEncodedU64Bytes = 8U;
constexpr std::uint64_t kDigestTextBytes = 64U;
constexpr std::uint64_t kMetadataBytes =
    kSyncPosixRegularFileSnapshotMetadataEncodedBytes;
constexpr std::uint64_t kEncodedU64Count = 10U;
constexpr std::uint64_t kSourceDigestCount = 8U;
constexpr std::uint64_t kBodyBytes =
    kDigestTextBytes + kMetadataBytes +
    (kEncodedU64Count * kEncodedU64Bytes) +
    (kSourceDigestCount * kDigestTextBytes);
constexpr std::uint64_t kExactBytes =
    static_cast<std::uint64_t>(kMagic.size()) + kBodyBytes +
    kDigestTextBytes;

[[noreturn]] void invalid(
    std::string_view label,
    std::string_view reason) {
    throw std::invalid_argument(
        std::string(label) + " payload retention mark " +
        std::string(reason));
}

void append_u64(std::string& output, std::uint64_t value) {
    for (unsigned shift = 56U;; shift -= 8U) {
        output.push_back(static_cast<char>((value >> shift) & 0xffU));
        if (shift == 0U) break;
    }
}

void validate_digest(
    std::string_view digest,
    std::string_view field,
    std::string_view label) {
    if (!is_lowercase_sha256_hex(digest)) {
        invalid(label, std::string(field) + " digest is invalid");
    }
}

void validate_limits_or_throw(
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    if (max_payload_entries == 0U) {
        invalid(label, "configured payload entry ceiling is zero");
    }
    if (max_indexed_bytes == 0U) {
        invalid(label, "configured indexed-byte ceiling is zero");
    }
}

void validate_mark_or_throw(
    const SyncReplicaFilePayloadRetentionMark& mark,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    validate_digest(mark.store_identity_sha256, "store-identity", label);
    validate_sync_posix_private_single_link_regular_file_snapshot_metadata_or_throw(
        mark.store_identity_metadata, std::nullopt,
        std::string(label) + " store identity");
    if (mark.generation == 0U) {
        invalid(label, "generation is zero");
    }
    validate_sync_replica_file_payload_retention_policy_for_store_or_throw(
        mark.policy, mark.marked_at_unix_seconds, max_payload_entries,
        max_indexed_bytes, label);

    const auto& policy = mark.policy;

    if (mark.source_replica_state_generation == 0U) {
        invalid(label, "source replica generation is zero");
    }
    validate_digest(mark.source_operation_set_digest, "operation-set", label);
    validate_digest(mark.source_evidence_set_digest, "evidence-set", label);
    validate_digest(
        mark.source_historical_version_pin_set_digest,
        "historical-version-pin-set", label);
    validate_digest(mark.source_visible_state_digest, "visible-state", label);
    validate_digest(
        mark.source_payload_snapshot_digest, "payload-snapshot", label);
    validate_digest(
        mark.source_payload_transient_namespace_digest,
        "payload-transient-namespace", label);
    validate_digest(
        mark.unreferenced_candidate_set_digest, "candidate-set", label);
    validate_digest(
        mark.durable_candidate_witness_digest,
        "durable-candidate-witness", label);

    if (mark.unreferenced_candidate_payload_count == 0U) {
        invalid(label, "contains no unreferenced payload candidates");
    }
    if (mark.unreferenced_candidate_payload_count > max_payload_entries ||
        mark.unreferenced_candidate_payload_count >
            policy.maximum_candidate_payload_count) {
        invalid(label, "observed candidate count exceeds policy");
    }
    if (mark.unreferenced_candidate_payload_bytes > max_indexed_bytes ||
        mark.unreferenced_candidate_payload_bytes >
            policy.maximum_candidate_payload_bytes) {
        invalid(label, "observed candidate bytes exceed policy");
    }
    if (policy.maximum_collection_payload_count >
        mark.unreferenced_candidate_payload_count) {
        invalid(label, "policy collection count exceeds candidates");
    }
    if (policy.maximum_collection_payload_bytes >
        mark.unreferenced_candidate_payload_bytes) {
        invalid(label, "policy collection bytes exceed candidates");
    }
    if (mark.unreferenced_candidate_payload_bytes != 0U &&
        policy.maximum_collection_payload_bytes == 0U) {
        invalid(label, "non-empty candidate bytes have zero collection bytes");
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
        const std::string_view result = bytes_.substr(position_, count);
        position_ += count;
        return result;
    }

    [[nodiscard]] std::uint64_t take_u64() {
        std::uint64_t value = 0U;
        for (const unsigned char byte : take(8U)) {
            value = (value << 8U) | static_cast<std::uint64_t>(byte);
        }
        return value;
    }

    [[nodiscard]] std::string take_digest(std::string_view field) {
        const std::string value(take(64U));
        if (!is_lowercase_sha256_hex(value)) {
            invalid(label_, std::string(field) + " digest is invalid");
        }
        return value;
    }

    [[nodiscard]] SyncPosixRegularFileSnapshotMetadata take_metadata() {
        return parse_sync_posix_regular_file_snapshot_metadata_binary_or_throw(
            take(static_cast<std::size_t>(kMetadataBytes)),
            std::string(label_) + " payload retention mark");
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

void validate_sync_replica_file_payload_retention_policy_or_throw(
    const SyncReplicaFilePayloadRetentionPolicy& policy,
    std::uint64_t marked_at_unix_seconds,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload retention policy label must not be empty");
    }
    if (marked_at_unix_seconds == 0U) {
        invalid(label, "mark time is zero");
    }
    if (policy.minimum_grace_seconds == 0U ||
        policy.minimum_grace_seconds >
            kSyncReplicaFilePayloadRetentionMarkMaximumGraceSeconds) {
        invalid(label, "policy grace seconds are invalid");
    }
    if (policy.minimum_grace_seconds >
        std::numeric_limits<std::uint64_t>::max() -
            marked_at_unix_seconds) {
        invalid(label, "policy grace deadline overflows");
    }
    if (policy.maximum_candidate_payload_count == 0U) {
        invalid(label, "policy candidate count frontier is zero");
    }
    if (policy.maximum_collection_payload_count == 0U ||
        policy.maximum_collection_payload_count >
            policy.maximum_candidate_payload_count) {
        invalid(label, "policy collection count frontier is invalid");
    }
    if (policy.maximum_collection_payload_bytes >
        policy.maximum_candidate_payload_bytes) {
        invalid(label, "policy collection bytes frontier is invalid");
    }
    if (policy.maximum_candidate_payload_bytes != 0U &&
        policy.maximum_collection_payload_bytes == 0U) {
        invalid(label, "nonzero candidate bytes have zero collection bytes");
    }
}

void validate_sync_replica_file_payload_retention_policy_for_store_or_throw(
    const SyncReplicaFilePayloadRetentionPolicy& policy,
    std::uint64_t marked_at_unix_seconds,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    validate_sync_replica_file_payload_retention_policy_or_throw(
        policy, marked_at_unix_seconds, label);
    validate_limits_or_throw(max_payload_entries, max_indexed_bytes, label);
    if (policy.maximum_candidate_payload_count > max_payload_entries) {
        invalid(label, "policy candidate count exceeds store capacity");
    }
    if (policy.maximum_candidate_payload_bytes > max_indexed_bytes) {
        invalid(label, "policy candidate bytes exceed store capacity");
    }
}

std::uint64_t
sync_replica_file_payload_retention_mark_exact_bytes() noexcept {
    return kExactBytes;
}

std::string serialize_sync_replica_file_payload_retention_mark_or_throw(
    const SyncReplicaFilePayloadRetentionMark& mark,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload retention mark serialization label must not be empty");
    }
    validate_mark_or_throw(
        mark, max_payload_entries, max_indexed_bytes, label);
    if (kExactBytes > std::numeric_limits<std::size_t>::max()) {
        throw std::length_error(
            std::string(label) + " payload retention mark exceeds size_t");
    }

    std::string encoded;
    encoded.reserve(static_cast<std::size_t>(kExactBytes));
    encoded.append(kMagic);
    encoded.append(mark.store_identity_sha256);
    append_sync_posix_regular_file_snapshot_metadata_binary(
        encoded, mark.store_identity_metadata);
    append_u64(encoded, mark.generation);
    append_u64(encoded, mark.marked_at_unix_seconds);
    append_u64(encoded, mark.policy.minimum_grace_seconds);
    append_u64(encoded, mark.policy.maximum_candidate_payload_count);
    append_u64(encoded, mark.policy.maximum_candidate_payload_bytes);
    append_u64(encoded, mark.policy.maximum_collection_payload_count);
    append_u64(encoded, mark.policy.maximum_collection_payload_bytes);
    append_u64(encoded, mark.unreferenced_candidate_payload_count);
    append_u64(encoded, mark.unreferenced_candidate_payload_bytes);
    append_u64(encoded, mark.source_replica_state_generation);
    encoded.append(mark.source_operation_set_digest);
    encoded.append(mark.source_evidence_set_digest);
    encoded.append(mark.source_historical_version_pin_set_digest);
    encoded.append(mark.source_visible_state_digest);
    encoded.append(mark.source_payload_snapshot_digest);
    encoded.append(mark.source_payload_transient_namespace_digest);
    encoded.append(mark.unreferenced_candidate_set_digest);
    encoded.append(mark.durable_candidate_witness_digest);
    encoded.append(sha256_hex(encoded));
    if (encoded.size() != kExactBytes) {
        throw std::logic_error(
            std::string(label) + " payload retention mark encoded size drifted");
    }
    return encoded;
}

SyncReplicaFilePayloadRetentionMark
parse_sync_replica_file_payload_retention_mark_or_throw(
    std::string_view bytes,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "payload retention mark parsing label must not be empty");
    }
    validate_limits_or_throw(max_payload_entries, max_indexed_bytes, label);
    if (bytes.size() != kExactBytes) {
        invalid(label, "length is not the exact v1 size");
    }
    const std::size_t framed_size =
        bytes.size() - static_cast<std::size_t>(kDigestTextBytes);
    const std::string_view expected_checksum = bytes.substr(framed_size);
    if (!is_lowercase_sha256_hex(expected_checksum) ||
        sha256_hex(std::string(bytes.substr(0U, framed_size))) !=
            expected_checksum) {
        invalid(label, "checksum is invalid");
    }

    Cursor cursor(bytes.substr(0U, framed_size), label);
    if (cursor.take(kMagic.size()) != kMagic) {
        invalid(label, "magic is invalid");
    }
    SyncReplicaFilePayloadRetentionMark mark;
    mark.store_identity_sha256 = cursor.take_digest("store-identity");
    mark.store_identity_metadata = cursor.take_metadata();
    mark.generation = cursor.take_u64();
    mark.marked_at_unix_seconds = cursor.take_u64();
    mark.policy.minimum_grace_seconds = cursor.take_u64();
    mark.policy.maximum_candidate_payload_count = cursor.take_u64();
    mark.policy.maximum_candidate_payload_bytes = cursor.take_u64();
    mark.policy.maximum_collection_payload_count = cursor.take_u64();
    mark.policy.maximum_collection_payload_bytes = cursor.take_u64();
    mark.unreferenced_candidate_payload_count = cursor.take_u64();
    mark.unreferenced_candidate_payload_bytes = cursor.take_u64();
    mark.source_replica_state_generation = cursor.take_u64();
    mark.source_operation_set_digest = cursor.take_digest("operation-set");
    mark.source_evidence_set_digest = cursor.take_digest("evidence-set");
    mark.source_historical_version_pin_set_digest =
        cursor.take_digest("historical-version-pin-set");
    mark.source_visible_state_digest = cursor.take_digest("visible-state");
    mark.source_payload_snapshot_digest = cursor.take_digest("payload-snapshot");
    mark.source_payload_transient_namespace_digest =
        cursor.take_digest("payload-transient-namespace");
    mark.unreferenced_candidate_set_digest = cursor.take_digest("candidate-set");
    mark.durable_candidate_witness_digest =
        cursor.take_digest("durable-candidate-witness");
    if (!cursor.exhausted()) {
        invalid(label, "contains trailing body bytes");
    }
    validate_mark_or_throw(
        mark, max_payload_entries, max_indexed_bytes, label);
    return mark;
}

std::string sync_replica_file_payload_retention_mark_digest_or_throw(
    const SyncReplicaFilePayloadRetentionMark& mark,
    std::uint64_t max_payload_entries,
    std::uint64_t max_indexed_bytes,
    std::string_view label) {
    const std::string encoded =
        serialize_sync_replica_file_payload_retention_mark_or_throw(
            mark, max_payload_entries, max_indexed_bytes, label);
    return encoded.substr(
        encoded.size() - static_cast<std::size_t>(kDigestTextBytes));
}

}  // namespace anonsync

#endif
