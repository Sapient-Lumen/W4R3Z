#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_multiwriter.hpp"
#include "iotox/sync_multiwriter_wire.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <span>
#include <string>
#include <vector>

namespace iotox::sync {

class TreeV2StateWitness;

struct TreeV2WriterCutoff {
    PrincipalId writer{};
    std::uint64_t generation{0U};
    Digest record{};

    [[nodiscard]] bool operator==(const TreeV2WriterCutoff &) const = default;
};

// Device-signed owner-local policy. Pins retain complete signed metadata and
// the locally selected content closure; a sparse pin is not a full backup.
// Cutoffs permanently bind one retired writer to its last admitted record.
struct TreeV2MaintenanceState {
    std::string namespace_id;
    std::uint64_t mutation{0U};
    Digest previous{};
    security::SigningPublicKey signer{};
    std::vector<Digest> pins;
    std::vector<TreeV2WriterCutoff> cutoffs;
    security::Signature signature{};

    [[nodiscard]] bool operator==(const TreeV2MaintenanceState &) const =
        default;
};

[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_maintenance_state(const TreeV2MaintenanceState &state);
[[nodiscard]] Result<TreeV2MaintenanceState>
decode_tree_v2_maintenance_state(std::span<const std::uint8_t> bytes,
                                 std::uint64_t maximum_pins,
                                 std::uint64_t maximum_cutoffs);
[[nodiscard]] Status verify_tree_v2_maintenance_state(
    const TreeV2MaintenanceState &state,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium);

class TreeV2MaintenanceStore final {
  public:
    explicit TreeV2MaintenanceStore(
        std::filesystem::path namespace_root,
        std::shared_ptr<TreeV2StateWitness> witness = {});

    [[nodiscard]] Result<TreeV2MaintenanceState>
    load(const NamespacePolicy &policy,
         const security::SigningPublicKey &expected_device,
         const security::Sodium &sodium,
         const SyncNamespaceTransaction &transaction) const;
    [[nodiscard]] Result<TreeV2MaintenanceState>
    pin(const NamespacePolicy &policy, const Digest &record,
        const security::DeviceIdentity &identity,
        const security::Sodium &sodium,
        const SyncNamespaceTransaction &transaction) const;
    [[nodiscard]] Result<TreeV2MaintenanceState>
    unpin(const NamespacePolicy &policy, const Digest &record,
          const security::DeviceIdentity &identity,
          const security::Sodium &sodium,
          const SyncNamespaceTransaction &transaction) const;
    [[nodiscard]] Result<TreeV2MaintenanceState>
    set_cutoff(const NamespacePolicy &policy,
               const TreeV2WriterCutoff &cutoff,
               const security::DeviceIdentity &identity,
               const security::Sodium &sodium,
               const SyncNamespaceTransaction &transaction) const;

  private:
    [[nodiscard]] Result<TreeV2MaintenanceState>
    commit(const NamespacePolicy &policy, TreeV2MaintenanceState state,
           const security::DeviceIdentity &identity,
           const security::Sodium &sodium,
           const SyncNamespaceTransaction &transaction) const;

    std::filesystem::path root_;
    std::shared_ptr<TreeV2StateWitness> witness_;
};

// Enforces a previously committed exact writer cutoff. A cutoff record itself
// remains admissible for idempotent recovery; every alternative or successor
// from that writer is refused.
[[nodiscard]] Status admit_tree_v2_writer_record(
    const NamespacePolicy &policy, const TreeV2BranchHead &head,
    const Digest &record, const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

struct TreeV2GcObject {
    TreeV2ObjectKind kind{TreeV2ObjectKind::branch_record};
    Digest digest{};
    std::uint64_t bytes{0U};

    [[nodiscard]] bool operator==(const TreeV2GcObject &) const = default;
};

struct TreeV2GcPlan {
    std::vector<TreeV2GcObject> reachable;
    std::vector<TreeV2GcObject> candidates;
    std::uint64_t reachable_bytes{0U};
    std::uint64_t candidate_bytes{0U};
    std::uint64_t checkpoint_floors{0U};
    std::uint64_t pinned_roots{0U};
    std::uint64_t manifest_file_objects{0U};
    std::uint64_t selected_file_objects{0U};
    std::uint64_t skipped_file_objects{0U};
    std::uint64_t selected_file_bytes{0U};
    std::uint64_t skipped_file_bytes{0U};
    bool custody_complete{true};
    bool workspace_authenticated{false};
    bool maintenance_authenticated{false};
};

struct TreeV2GcOutcome {
    Status status;
    TreeV2GcPlan plan;
    std::uint64_t moved{0U};
    std::uint64_t moved_bytes{0U};

    [[nodiscard]] bool ok() const noexcept { return status.ok(); }
};

struct TreeV2RestoreOutcome {
    Status status;
    std::uint64_t restored{0U};
    std::uint64_t restored_bytes{0U};
    std::uint64_t already_present{0U};

    [[nodiscard]] bool ok() const noexcept { return status.ok(); }
};

[[nodiscard]] Result<TreeV2GcPlan> plan_tree_v2_gc(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {});
[[nodiscard]] TreeV2GcOutcome quarantine_tree_v2_gc(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {});
[[nodiscard]] TreeV2RestoreOutcome restore_tree_v2_quarantine(
    const NamespacePolicy &policy, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {});

// Requires a current local checkpoint that exactly observes TARGET's current
// branch. The cutoff policy commits before the branch pointer is retired.
[[nodiscard]] Result<TreeV2WriterCutoff> cutoff_tree_v2_writer(
    const NamespacePolicy &policy, const PrincipalId &target,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness = {});

} // namespace iotox::sync
