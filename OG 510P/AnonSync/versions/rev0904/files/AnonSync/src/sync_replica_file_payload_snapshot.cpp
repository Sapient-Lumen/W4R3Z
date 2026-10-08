#include "sync_replica_file_payload_snapshot.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

constexpr std::string_view kSnapshotDigestDomain =
    "anonsync:sync-replica-file-payload-snapshot:v1";

struct PayloadEntry final {
    std::string content_sha256;
    std::string bytes;
};

void append_u64(Sha256DigestBuilder& digest, std::uint64_t value) {
    std::array<char, 8U> encoded{};
    for (std::size_t index = 0U; index < encoded.size(); ++index) {
        const unsigned int shift =
            static_cast<unsigned int>((encoded.size() - index - 1U) * 8U);
        encoded[index] = static_cast<char>((value >> shift) & 0xffU);
    }
    digest.update(std::string_view(encoded.data(), encoded.size()));
}

void append_string(Sha256DigestBuilder& digest, std::string_view value) {
    if (value.size() > std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            "sync replica file payload snapshot field size exceeds uint64 range");
    }
    append_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

[[nodiscard]] std::uint64_t size_to_u64_or_throw(
    std::size_t value,
    std::string_view label) {
    if (value > std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            std::string(label) + " size exceeds uint64 range");
    }
    return static_cast<std::uint64_t>(value);
}

[[nodiscard]] std::string snapshot_digest_or_throw(
    std::string_view folder_id,
    const SyncReplicaFilePayloadSnapshotLimits& limits,
    std::uint64_t retained_bytes,
    const std::vector<PayloadEntry>& entries) {
    Sha256DigestBuilder digest;
    append_string(digest, kSnapshotDigestDomain);
    append_string(digest, folder_id);
    append_u64(digest, limits.max_entries);
    append_u64(digest, limits.max_payload_bytes);
    append_u64(digest, limits.max_retained_bytes);
    append_u64(digest, static_cast<std::uint64_t>(entries.size()));
    append_u64(digest, retained_bytes);
    for (const PayloadEntry& entry : entries) {
        append_string(digest, entry.content_sha256);
        append_u64(digest, static_cast<std::uint64_t>(entry.bytes.size()));
    }
    return digest.finish_hex();
}

}  // namespace

struct SyncReplicaFilePayloadSnapshot::State final {
    std::string folder_id;
    SyncReplicaFilePayloadSnapshotLimits limits;
    std::vector<PayloadEntry> entries;
    SyncReplicaFileContentInventory content_inventory;
    std::uint64_t retained_bytes = 0U;
    std::string snapshot_digest;
};

void validate_sync_replica_file_payload_snapshot_limits_or_throw(
    const SyncReplicaFilePayloadSnapshotLimits& limits) {
    if (limits.max_entries == 0U ||
        limits.max_entries > kSyncReplicaFilePayloadSnapshotMaxEntries) {
        throw std::invalid_argument(
            "sync replica file payload snapshot entry limit is invalid");
    }
    if (limits.max_payload_bytes == 0U ||
        limits.max_retained_bytes == 0U ||
        limits.max_payload_bytes > limits.max_retained_bytes) {
        throw std::invalid_argument(
            "sync replica file payload snapshot byte limits are invalid");
    }
    if (limits.max_payload_bytes >
            std::numeric_limits<std::size_t>::max() ||
        limits.max_retained_bytes >
            std::numeric_limits<std::size_t>::max()) {
        throw std::invalid_argument(
            "sync replica file payload snapshot byte limits exceed addressable memory");
    }
}

SyncReplicaFilePayloadSnapshot::SyncReplicaFilePayloadSnapshot(
    std::string folder_id,
    std::vector<std::string> payloads,
    SyncReplicaFilePayloadSnapshotLimits limits,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file payload snapshot label must not be empty");
    }
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync id");
    }
    validate_sync_replica_file_payload_snapshot_limits_or_throw(limits);
    if (payloads.size() > limits.max_entries) {
        throw std::length_error(
            label + " entry count exceeds its configured budget");
    }

    std::vector<PayloadEntry> entries;
    entries.reserve(payloads.size());
    std::uint64_t retained_bytes = 0U;
    for (std::string& payload : payloads) {
        const std::uint64_t payload_bytes =
            size_to_u64_or_throw(payload.size(), label + " payload");
        if (payload_bytes > limits.max_payload_bytes) {
            throw std::length_error(
                label + " payload exceeds its configured byte budget");
        }
        if (retained_bytes > limits.max_retained_bytes ||
            payload_bytes > limits.max_retained_bytes - retained_bytes) {
            throw std::length_error(
                label + " aggregate payload bytes exceed their configured budget");
        }
        retained_bytes += payload_bytes;
        entries.push_back({sha256_hex(payload), std::move(payload)});
    }

    std::sort(
        entries.begin(), entries.end(),
        [](const PayloadEntry& left, const PayloadEntry& right) {
            return left.content_sha256 < right.content_sha256;
        });
    const auto duplicate = std::adjacent_find(
        entries.begin(), entries.end(),
        [](const PayloadEntry& left, const PayloadEntry& right) {
            return left.content_sha256 == right.content_sha256;
        });
    if (duplicate != entries.end()) {
        throw std::invalid_argument(
            label + " contains duplicate content authority");
    }

    auto state = std::make_shared<State>();
    state->folder_id = std::move(folder_id);
    state->limits = limits;
    state->entries = std::move(entries);
    std::vector<std::string> content_sha256s;
    content_sha256s.reserve(state->entries.size());
    for (const PayloadEntry& entry : state->entries) {
        content_sha256s.push_back(entry.content_sha256);
    }
    state->content_inventory = SyncReplicaFileContentInventory(
        state->folder_id, std::move(content_sha256s),
        label + " content inventory");
    state->retained_bytes = retained_bytes;
    state->snapshot_digest = snapshot_digest_or_throw(
        state->folder_id, state->limits, state->retained_bytes,
        state->entries);
    state_ = std::move(state);
}

const SyncReplicaFilePayloadSnapshot::State&
SyncReplicaFilePayloadSnapshot::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file payload snapshot operation label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " payload snapshot is inactive");
    }
    return *state_;
}

const std::string& SyncReplicaFilePayloadSnapshot::folder_id() const {
    return require_state_or_throw("sync replica file payload snapshot folder")
        .folder_id;
}

std::uint64_t SyncReplicaFilePayloadSnapshot::entry_count() const {
    const State& state = require_state_or_throw(
        "sync replica file payload snapshot entry count");
    return static_cast<std::uint64_t>(state.entries.size());
}

std::uint64_t SyncReplicaFilePayloadSnapshot::retained_bytes() const {
    return require_state_or_throw(
               "sync replica file payload snapshot retained bytes")
        .retained_bytes;
}

const std::string& SyncReplicaFilePayloadSnapshot::snapshot_digest() const {
    return require_state_or_throw(
               "sync replica file payload snapshot digest")
        .snapshot_digest;
}

const SyncReplicaFilePayloadSnapshotLimits&
SyncReplicaFilePayloadSnapshot::limits() const {
    return require_state_or_throw(
               "sync replica file payload snapshot limits")
        .limits;
}

SyncReplicaFileContentInventory
SyncReplicaFilePayloadSnapshot::content_inventory() const {
    const State& state = require_state_or_throw(
        "sync replica file payload snapshot content inventory");
    return state.content_inventory;
}

std::string SyncReplicaFilePayloadSnapshot::copy_payload_for_operation_or_throw(
    const SyncReplicaOperation& operation,
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    if (operation.kind != SyncReplicaValueKind::File) {
        throw std::invalid_argument(
            std::string(label) + " requires a file operation");
    }
    if (!is_lowercase_sha256_hex(operation.content_sha256)) {
        throw std::invalid_argument(
            std::string(label) + " operation content digest is invalid");
    }
    if (operation.size_bytes > state.limits.max_payload_bytes) {
        throw std::length_error(
            std::string(label) + " operation exceeds the snapshot payload budget");
    }
    const auto found = std::lower_bound(
        state.entries.begin(), state.entries.end(), operation.content_sha256,
        [](const PayloadEntry& entry, std::string_view digest) {
            return entry.content_sha256 < digest;
        });
    if (found == state.entries.end() ||
        found->content_sha256 != operation.content_sha256) {
        throw std::runtime_error(
            std::string(label) + " has no payload for the claimed operation");
    }
    if (found->bytes.size() != operation.size_bytes) {
        throw std::logic_error(
            std::string(label) + " payload size disagrees with the claimed operation");
    }
    return found->bytes;
}

void SyncReplicaFilePayloadSnapshot::preflight_or_throw(
    std::string_view label) const {
    (void)require_state_or_throw(label);
}

void SyncReplicaFilePayloadSnapshot::require_folder_or_throw(
    std::string_view folder_id,
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            std::string(label) + " service folder_id is invalid");
    }
    if (state.folder_id != folder_id) {
        throw std::invalid_argument(
            std::string(label) +
            " payload snapshot does not match service folder identity");
    }
}

}  // namespace anonsync
