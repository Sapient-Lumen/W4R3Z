#include "sync_replica_tls_membership_snapshot.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <array>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kSnapshotDigestDomain =
    "anonsync:sync-replica-tls-membership-snapshot:v1";

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
            "sync replica TLS membership field size exceeds uint64 range");
    }
    append_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

void append_actor(
    Sha256DigestBuilder& digest,
    const SyncReplicaActor& actor) {
    append_string(digest, actor.device_id);
    append_u64(digest, actor.epoch);
}

void validate_actor_or_throw(
    const SyncReplicaActor& actor,
    std::string_view label) {
    if (!sync_id_is_valid(actor.device_id) || actor.epoch == 0U) {
        throw std::invalid_argument(
            std::string(label) + " actor identity is invalid");
    }
}

[[nodiscard]] std::string snapshot_digest_or_throw(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::uint64_t policy_epoch,
    const std::vector<SyncReplicaTlsMembershipEntry>& entries) {
    Sha256DigestBuilder digest;
    append_string(digest, kSnapshotDigestDomain);
    append_string(digest, folder_id);
    append_actor(digest, local_actor);
    append_u64(digest, policy_epoch);
    append_u64(digest, static_cast<std::uint64_t>(entries.size()));
    for (const auto& entry : entries) {
        append_string(digest, entry.spki_sha256);
        append_actor(digest, entry.actor);
    }
    return digest.finish_hex();
}

}  // namespace

struct SyncReplicaTlsMembershipSnapshot::State final {
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t policy_epoch = 0U;
    std::vector<SyncReplicaTlsMembershipEntry> entries;
    std::string snapshot_digest;
};

SyncReplicaTlsMembershipSnapshot::SyncReplicaTlsMembershipSnapshot(
    std::string folder_id,
    SyncReplicaActor local_actor,
    std::uint64_t policy_epoch,
    std::vector<SyncReplicaTlsMembershipEntry> entries,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership snapshot label must not be empty");
    }
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync id");
    }
    validate_actor_or_throw(local_actor, label + " local");
    if (policy_epoch == 0U) {
        throw std::invalid_argument(
            label + " policy_epoch must be positive");
    }
    if (entries.size() > kSyncReplicaTlsMembershipMaxEntries) {
        throw std::length_error(
            label + " entry count exceeds the configured hard ceiling");
    }

    for (const auto& entry : entries) {
        if (!is_lowercase_sha256_hex(entry.spki_sha256)) {
            throw std::invalid_argument(
                label + " member SPKI is not lowercase SHA-256");
        }
        validate_actor_or_throw(entry.actor, label + " member");
        if (entry.actor.device_id == local_actor.device_id) {
            throw std::invalid_argument(
                label + " cannot authorize the receiver's own device_id");
        }
    }

    std::sort(
        entries.begin(), entries.end(),
        [](const SyncReplicaTlsMembershipEntry& left,
           const SyncReplicaTlsMembershipEntry& right) {
            return left.spki_sha256 < right.spki_sha256;
        });
    const auto duplicate = std::adjacent_find(
        entries.begin(), entries.end(),
        [](const SyncReplicaTlsMembershipEntry& left,
           const SyncReplicaTlsMembershipEntry& right) {
            return left.spki_sha256 == right.spki_sha256;
        });
    if (duplicate != entries.end()) {
        throw std::invalid_argument(
            label + " contains duplicate SPKI membership authority");
    }

    auto state = std::make_shared<State>();
    state->folder_id = std::move(folder_id);
    state->local_actor = std::move(local_actor);
    state->policy_epoch = policy_epoch;
    state->entries = std::move(entries);
    state->snapshot_digest = snapshot_digest_or_throw(
        state->folder_id, state->local_actor, state->policy_epoch,
        state->entries);
    state_ = std::move(state);
}

const SyncReplicaTlsMembershipSnapshot::State&
SyncReplicaTlsMembershipSnapshot::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica TLS membership operation label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " membership snapshot is inactive");
    }
    return *state_;
}

const std::string& SyncReplicaTlsMembershipSnapshot::folder_id() const {
    return require_state_or_throw("sync replica TLS membership folder")
        .folder_id;
}

const SyncReplicaActor& SyncReplicaTlsMembershipSnapshot::local_actor() const {
    return require_state_or_throw("sync replica TLS membership local actor")
        .local_actor;
}

std::uint64_t SyncReplicaTlsMembershipSnapshot::policy_epoch() const {
    return require_state_or_throw("sync replica TLS membership policy epoch")
        .policy_epoch;
}

std::uint64_t SyncReplicaTlsMembershipSnapshot::entry_count() const {
    const State& state =
        require_state_or_throw("sync replica TLS membership entry count");
    return static_cast<std::uint64_t>(state.entries.size());
}

const std::string& SyncReplicaTlsMembershipSnapshot::snapshot_digest() const {
    return require_state_or_throw("sync replica TLS membership digest")
        .snapshot_digest;
}

std::span<const SyncReplicaTlsMembershipEntry>
SyncReplicaTlsMembershipSnapshot::entries() const {
    const auto& entries =
        require_state_or_throw("sync replica TLS membership entries").entries;
    return {entries.data(), entries.size()};
}

std::optional<SyncReplicaActor>
SyncReplicaTlsMembershipSnapshot::resolve_peer_or_throw(
    std::string_view spki_sha256,
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    if (!is_lowercase_sha256_hex(spki_sha256)) {
        throw std::invalid_argument(
            std::string(label) + " SPKI is not lowercase SHA-256");
    }
    const auto found = std::lower_bound(
        state.entries.begin(), state.entries.end(), spki_sha256,
        [](const SyncReplicaTlsMembershipEntry& entry,
           std::string_view pin) {
            return entry.spki_sha256 < pin;
        });
    if (found == state.entries.end() ||
        found->spki_sha256 != spki_sha256) {
        return std::nullopt;
    }
    return found->actor;
}

void SyncReplicaTlsMembershipSnapshot::require_service_identity_or_throw(
    std::string_view folder_id,
    const SyncReplicaActor& local_actor,
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            std::string(label) + " service folder_id is invalid");
    }
    validate_actor_or_throw(local_actor, std::string(label) + " service local");
    if (state.folder_id != folder_id || state.local_actor != local_actor) {
        throw std::invalid_argument(
            std::string(label) +
            " membership snapshot does not match receiver service identity");
    }
}

}  // namespace anonsync
