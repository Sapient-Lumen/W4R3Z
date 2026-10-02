#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_multiwriter.hpp"
#include "iotox/sync_transaction.hpp"

#include <filesystem>
#include <memory>
#include <optional>
#include <span>
#include <vector>

namespace iotox::sync {

class TreeV2StateWitness;

enum class TreeV2BranchStoreDecision : std::uint8_t {
    accepted_genesis = 1U,
    accepted_advance = 2U,
    duplicate = 3U,
    retired_terminal = 4U,
};

struct TreeV2BranchStoreResult {
    TreeV2BranchStoreDecision decision{
        TreeV2BranchStoreDecision::accepted_genesis};
    TreeV2Snapshot snapshot;
    Digest record{};
    bool manifest_installed{false};

    [[nodiscard]] bool
    operator==(const TreeV2BranchStoreResult &) const = default;
};

[[nodiscard]] std::string_view
tree_v2_branch_store_decision_name(TreeV2BranchStoreDecision decision) noexcept;

[[nodiscard]] Result<TreeV2Manifest>
load_tree_v2_stored_manifest(const NamespacePolicy &policy,
                             const Digest &digest,
                             const security::Sodium &sodium,
                             const SyncNamespaceTransaction &transaction);
[[nodiscard]] Result<TreeV2Snapshot>
load_tree_v2_stored_record(const NamespacePolicy &policy, const Digest &record,
                           const security::Sodium &sodium,
                           const SyncNamespaceTransaction &transaction);
[[nodiscard]] std::filesystem::path
tree_v2_manifest_path(const NamespacePolicy &policy, const Digest &digest);
[[nodiscard]] std::filesystem::path
tree_v2_branch_record_path(const NamespacePolicy &policy, const Digest &record);

// Durable tree-v2 truth is ordered as immutable manifest first and one
// writer-specific branch pointer last. Each writer owns an independent linear
// chain; accepting one writer can never replace another writer's branch.
class TreeV2BranchStore final {
  public:
    explicit TreeV2BranchStore(
        std::filesystem::path namespace_root,
        std::optional<security::SigningPublicKey> local_device = std::nullopt,
        std::shared_ptr<TreeV2StateWitness> witness = {});

    [[nodiscard]] Status
    prepare(const NamespacePolicy &policy,
            const SyncNamespaceTransaction &transaction) const;
    [[nodiscard]] Result<std::vector<TreeV2Snapshot>>
    load_frontier(const NamespacePolicy &policy, const security::Sodium &sodium,
                  const SyncNamespaceTransaction &transaction) const;
    [[nodiscard]] Result<TreeV2BranchStoreResult>
    accept(const NamespacePolicy &policy, const TreeV2Snapshot &snapshot,
           const security::Sodium &sodium,
           const SyncNamespaceTransaction &transaction) const;
    [[nodiscard]] Result<TreeV2BranchStoreResult>
    publish_local(const NamespacePolicy &policy, const TreeV2Manifest &manifest,
                  const security::DeviceIdentity &identity,
                  const security::Sodium &sodium,
                  const SyncNamespaceTransaction &transaction) const;
    // Retains a verified derived merge for the signed workspace journal
    // without claiming that the local writer authored another branch.
    [[nodiscard]] Result<Digest>
    retain_manifest(const NamespacePolicy &policy,
                    const TreeV2Manifest &manifest,
                    const security::Sodium &sodium,
                    const SyncNamespaceTransaction &transaction) const;
    // Publishes an edit against the exact branch frontier that was visible in
    // the writable workspace. Newly received but unprojected branches remain
    // concurrent even though they are already present in the local store.
    [[nodiscard]] Result<TreeV2BranchStoreResult> publish_local_from_frontier(
        const NamespacePolicy &policy, const TreeV2Manifest &manifest,
        std::span<const TreeV2Observation> visible_frontier,
        const security::DeviceIdentity &identity,
        const security::Sodium &sodium,
        const SyncNamespaceTransaction &transaction) const;

    [[nodiscard]] Result<TreeV2BranchStoreResult>
    checkpoint_local(const NamespacePolicy &policy,
                     const security::DeviceIdentity &identity,
                     const security::Sodium &sodium,
                     const SyncNamespaceTransaction &transaction) const;

    [[nodiscard]] const std::filesystem::path &root() const noexcept {
        return root_;
    }

  private:
    [[nodiscard]] std::filesystem::path
    manifest_path(const Digest &digest) const;
    [[nodiscard]] std::filesystem::path
    branch_path(const PrincipalId &writer) const;
    [[nodiscard]] std::filesystem::path record_path(const Digest &record) const;

    std::filesystem::path root_;
    std::optional<security::SigningPublicKey> local_device_;
    std::shared_ptr<TreeV2StateWitness> witness_;
};

} // namespace iotox::sync
