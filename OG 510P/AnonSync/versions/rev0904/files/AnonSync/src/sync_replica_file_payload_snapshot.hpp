#pragma once

#include "sync_replica_file_content_inventory.hpp"
#include "sync_replica_model.hpp"

#include <cstdint>
#include <memory>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaFilePayloadSnapshotMaxEntries =
    kSyncReplicaFileContentInventoryMaxEntries;

struct SyncReplicaFilePayloadSnapshotLimits final {
    std::uint64_t max_entries = 4096U;
    std::uint64_t max_payload_bytes = 4ULL * 1024ULL * 1024ULL;
    std::uint64_t max_retained_bytes = 64ULL * 1024ULL * 1024ULL;

    bool operator==(const SyncReplicaFilePayloadSnapshotLimits&) const =
        default;
};

void validate_sync_replica_file_payload_snapshot_limits_or_throw(
    const SyncReplicaFilePayloadSnapshotLimits& limits);

// Immutable, content-addressed payload authority prepared before an outbox
// lease is minted. Construction owns and hashes every byte, applies exact
// per-payload and aggregate budgets, sorts entries by digest, and rejects
// duplicate content identities. Copies share const state; no application
// callback or mutable backing container executes while a durable claim exists.
//
// The snapshot digest is structural local evidence. It is not a signature and
// does not replace the operation's canonical content_sha256 commitment.
class SyncReplicaFilePayloadSnapshot final {
public:
    SyncReplicaFilePayloadSnapshot(
        std::string folder_id,
        std::vector<std::string> payloads,
        SyncReplicaFilePayloadSnapshotLimits limits = {},
        std::string label = "sync replica file payload snapshot");

    SyncReplicaFilePayloadSnapshot(
        const SyncReplicaFilePayloadSnapshot&) noexcept = default;
    SyncReplicaFilePayloadSnapshot& operator=(
        const SyncReplicaFilePayloadSnapshot&) noexcept = default;
    SyncReplicaFilePayloadSnapshot(
        SyncReplicaFilePayloadSnapshot&&) noexcept = default;
    SyncReplicaFilePayloadSnapshot& operator=(
        SyncReplicaFilePayloadSnapshot&&) noexcept = default;
    ~SyncReplicaFilePayloadSnapshot() noexcept = default;

    [[nodiscard]] bool active() const noexcept {
        return static_cast<bool>(state_);
    }

    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] std::uint64_t entry_count() const;
    [[nodiscard]] std::uint64_t retained_bytes() const;
    [[nodiscard]] const std::string& snapshot_digest() const;
    [[nodiscard]] const SyncReplicaFilePayloadSnapshotLimits& limits() const;

    // Canonical, bounded, independently immutable content authority used to
    // constrain the SQLite claim transaction to payloads this snapshot can
    // actually supply. Returning a cheap value copy retains its const backing
    // state; the owner never borrows caller-controlled digest storage.
    [[nodiscard]] SyncReplicaFileContentInventory content_inventory() const;

    // Returns one owned payload copy only when the exact file operation's
    // content digest and declared size are present. Missing content is a typed
    // local preparation failure; callers that already own a claim must release
    // that exact claim before propagating it.
    [[nodiscard]] std::string copy_payload_for_operation_or_throw(
        const SyncReplicaOperation& operation,
        std::string_view label =
            "sync replica file payload snapshot lookup") const;

    // Pure pre-claim scope check. A payload snapshot authored for another
    // folder cannot be used to spend this service's outbox authority.
    void require_folder_or_throw(
        std::string_view folder_id,
        std::string_view label) const;

    // Uniform pre-claim source seam shared with the durable payload-store
    // snapshot. All byte ownership for this in-memory value was frozen at
    // construction, so this proof only rejects an inactive value.
    void preflight_or_throw(std::string_view label) const;

private:
    struct State;

    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::shared_ptr<const State> state_;
};

}  // namespace anonsync
