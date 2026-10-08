#include "sync_replica_file_content_inventory.hpp"

#include "sha256_digest.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {

struct SyncReplicaFileContentInventory::State final {
    std::string folder_id;
    std::vector<std::string> content_sha256s;
};

SyncReplicaFileContentInventory::SyncReplicaFileContentInventory(
    std::string folder_id,
    std::vector<std::string> content_sha256s,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file content inventory label must not be empty");
    }
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            label + " folder_id is not a lowercase portable sync id");
    }
    if (content_sha256s.size() >
        kSyncReplicaFileContentInventoryMaxEntries) {
        throw std::length_error(
            label + " entry count exceeds its hard ceiling");
    }
    for (const std::string& digest : content_sha256s) {
        if (!is_lowercase_sha256_hex(digest)) {
            throw std::invalid_argument(
                label + " contains an invalid content digest");
        }
    }
    std::sort(content_sha256s.begin(), content_sha256s.end());
    if (std::adjacent_find(
            content_sha256s.begin(), content_sha256s.end()) !=
        content_sha256s.end()) {
        throw std::invalid_argument(
            label + " contains duplicate content authority");
    }

    auto state = std::make_shared<State>();
    state->folder_id = std::move(folder_id);
    state->content_sha256s = std::move(content_sha256s);
    state_ = std::move(state);
}

const SyncReplicaFileContentInventory::State&
SyncReplicaFileContentInventory::require_state_or_throw(
    std::string_view label) const {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica file content inventory operation label must not be empty");
    }
    if (!state_) {
        throw std::logic_error(
            std::string(label) + " file content inventory is inactive");
    }
    return *state_;
}

const std::string& SyncReplicaFileContentInventory::folder_id() const {
    return require_state_or_throw(
               "sync replica file content inventory folder")
        .folder_id;
}

std::uint64_t SyncReplicaFileContentInventory::entry_count() const {
    const State& state = require_state_or_throw(
        "sync replica file content inventory entry count");
    return static_cast<std::uint64_t>(state.content_sha256s.size());
}

std::span<const std::string>
SyncReplicaFileContentInventory::content_sha256s() const {
    const State& state = require_state_or_throw(
        "sync replica file content inventory identities");
    return state.content_sha256s;
}

void SyncReplicaFileContentInventory::require_folder_or_throw(
    std::string_view folder_id,
    std::string_view label) const {
    const State& state = require_state_or_throw(label);
    if (!sync_id_is_valid(folder_id)) {
        throw std::invalid_argument(
            std::string(label) + " owner folder_id is invalid");
    }
    if (state.folder_id != folder_id) {
        throw std::invalid_argument(
            std::string(label) +
            " file content inventory does not match owner folder identity");
    }
}

}  // namespace anonsync
