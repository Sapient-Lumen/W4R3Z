#pragma once

#include <cstdint>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaFileContentInventoryMaxEntries =
    65536U;

// Bounded immutable proof of the exact file-content identities a local caller
// can supply. Construction owns, validates, sorts, and deduplicates every
// digest before the value can cross an outbox-claim boundary. Copies share only
// inaccessible const state, so the SQLite owner never borrows mutable caller
// memory while selecting or minting durable attempt authority.
//
// This is local availability evidence, not proof that payload bytes remain
// recoverable forever and not cryptographic authentication of a remote peer.
class SyncReplicaFileContentInventory final {
public:
    SyncReplicaFileContentInventory() noexcept = default;

    SyncReplicaFileContentInventory(
        std::string folder_id,
        std::vector<std::string> content_sha256s,
        std::string label = "sync replica file content inventory");

    SyncReplicaFileContentInventory(
        const SyncReplicaFileContentInventory&) noexcept = default;
    SyncReplicaFileContentInventory& operator=(
        const SyncReplicaFileContentInventory&) noexcept = default;
    SyncReplicaFileContentInventory(
        SyncReplicaFileContentInventory&&) noexcept = default;
    SyncReplicaFileContentInventory& operator=(
        SyncReplicaFileContentInventory&&) noexcept = default;
    ~SyncReplicaFileContentInventory() noexcept = default;

    [[nodiscard]] bool active() const noexcept {
        return static_cast<bool>(state_);
    }

    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] std::uint64_t entry_count() const;

    // The returned view is backed by shared immutable state and remains valid
    // while this value or any of its copies remains alive.
    [[nodiscard]] std::span<const std::string> content_sha256s() const;

    void require_folder_or_throw(
        std::string_view folder_id,
        std::string_view label) const;

private:
    struct State;

    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::shared_ptr<const State> state_;
};

}  // namespace anonsync
