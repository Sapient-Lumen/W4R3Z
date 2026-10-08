#pragma once

#include "sync_replica_model.hpp"

#include <cstdint>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync {

// One exact certificate-key authorization in an immutable receiver membership
// snapshot. Multiple SPKI pins may intentionally map to the same actor during a
// bounded key-rotation overlap, but one SPKI can map to only one actor.
struct SyncReplicaTlsMembershipEntry final {
    std::string spki_sha256;
    SyncReplicaActor actor;

    bool operator==(const SyncReplicaTlsMembershipEntry&) const = default;
};

inline constexpr std::uint64_t kSyncReplicaTlsMembershipMaxEntries = 65536U;

// Immutable, cheaply copyable membership authority for one receiver actor and
// one folder. Construction validates and canonically sorts the complete mapping,
// rejects duplicate SPKI authority, and binds the exact set to a versioned
// SHA-256 digest. The shared state is const after construction; accepted-session
// code takes this wrapper by value so no caller-supplied membership callback or
// mutable backing map remains live between TLS authentication and
// application-byte admission.
//
// policy_epoch is caller-owned configuration versioning. It is bound into the
// snapshot digest but is not itself rollback protection. The durable SQLite
// membership owner decides which epoch is current and is the only component
// permitted to emit accepted-session membership authority.
class SyncReplicaTlsMembershipSnapshot final {
public:
    SyncReplicaTlsMembershipSnapshot(
        std::string folder_id,
        SyncReplicaActor local_actor,
        std::uint64_t policy_epoch,
        std::vector<SyncReplicaTlsMembershipEntry> entries,
        std::string label = "sync replica TLS membership snapshot");

    SyncReplicaTlsMembershipSnapshot(
        const SyncReplicaTlsMembershipSnapshot&) noexcept = default;
    SyncReplicaTlsMembershipSnapshot& operator=(
        const SyncReplicaTlsMembershipSnapshot&) noexcept = default;
    SyncReplicaTlsMembershipSnapshot(
        SyncReplicaTlsMembershipSnapshot&&) noexcept = default;
    SyncReplicaTlsMembershipSnapshot& operator=(
        SyncReplicaTlsMembershipSnapshot&&) noexcept = default;
    ~SyncReplicaTlsMembershipSnapshot() noexcept = default;

    [[nodiscard]] bool active() const noexcept {
        return static_cast<bool>(state_);
    }

    [[nodiscard]] const std::string& folder_id() const;
    [[nodiscard]] const SyncReplicaActor& local_actor() const;
    [[nodiscard]] std::uint64_t policy_epoch() const;
    [[nodiscard]] std::uint64_t entry_count() const;
    [[nodiscard]] const std::string& snapshot_digest() const;
    [[nodiscard]] std::span<const SyncReplicaTlsMembershipEntry> entries() const;

    // Returns the actor mapped by one exact lowercase SHA-256 SPKI pin, or
    // nullopt when the authenticated key is not a member of this snapshot.
    // Malformed pins are rejected rather than normalized.
    [[nodiscard]] std::optional<SyncReplicaActor> resolve_peer_or_throw(
        std::string_view spki_sha256,
        std::string_view label = "sync replica TLS membership lookup") const;

    // Proves that this snapshot was authored for the exact file-delivery
    // service selected by the accepted-session owner. This check is pure and
    // runs before accept authority is spent.
    void require_service_identity_or_throw(
        std::string_view folder_id,
        const SyncReplicaActor& local_actor,
        std::string_view label) const;

private:
    struct State;

    [[nodiscard]] const State& require_state_or_throw(
        std::string_view label) const;

    std::shared_ptr<const State> state_;
};

}  // namespace anonsync
