#pragma once

#include "iotox/security/identity.hpp"
#include "iotox/status.hpp"
#include "iotox/sync_multiwriter.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <optional>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

class TreeV2StateWitness;

inline constexpr std::size_t kTreeV2WorkspacePathBytes = 4096U;

enum class TreeV2WorkspacePhase : std::uint8_t {
    stable = 1U,
    pending_exchange = 2U,
};

struct TreeV2WorkspaceState {
    std::string namespace_id;
    std::filesystem::path worktree;
    std::uint64_t generation{0U};
    TreeV2WorkspacePhase phase{TreeV2WorkspacePhase::stable};
    Digest active_manifest{};
    Digest pending_manifest{};
    Digest pending_worktree_manifest{};
    std::vector<TreeV2Observation> active_frontier;
    std::vector<TreeV2Observation> pending_frontier;
    security::SigningPublicKey signer{};
    security::Signature signature{};

    [[nodiscard]] bool operator==(const TreeV2WorkspaceState &) const = default;
};

enum class TreeV2WorkspaceDecision : std::uint8_t {
    initialized = 1U,
    begun = 2U,
    finished = 3U,
    duplicate = 4U,
};

struct TreeV2WorkspaceStoreResult {
    TreeV2WorkspaceDecision decision{TreeV2WorkspaceDecision::initialized};
    TreeV2WorkspaceState state;
};

[[nodiscard]] std::string_view
tree_v2_workspace_phase_name(TreeV2WorkspacePhase phase) noexcept;
[[nodiscard]] std::string_view
tree_v2_workspace_decision_name(TreeV2WorkspaceDecision decision) noexcept;
[[nodiscard]] Status
validate_tree_v2_workspace_state(const TreeV2WorkspaceState &state);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_tree_v2_workspace_state(const TreeV2WorkspaceState &state);
[[nodiscard]] Result<TreeV2WorkspaceState>
decode_tree_v2_workspace_state(std::span<const std::uint8_t> bytes);
[[nodiscard]] Status verify_tree_v2_workspace_state(
    const TreeV2WorkspaceState &state,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium);

class TreeV2WorkspaceStore final {
  public:
    explicit TreeV2WorkspaceStore(
        std::filesystem::path namespace_root,
        std::shared_ptr<TreeV2StateWitness> witness = {});

    [[nodiscard]] Result<std::optional<TreeV2WorkspaceState>>
    load(const NamespacePolicy &policy,
         const security::SigningPublicKey &expected_device,
         const security::Sodium &sodium,
         const SyncNamespaceTransaction *transaction = nullptr) const;
    [[nodiscard]] Result<TreeV2WorkspaceStoreResult>
    initialize(const NamespacePolicy &policy,
               const std::filesystem::path &worktree,
               const Digest &active_manifest,
               std::span<const TreeV2Observation> active_frontier,
               const security::DeviceIdentity &identity,
               const security::Sodium &sodium,
               const SyncNamespaceTransaction *transaction = nullptr) const;
    [[nodiscard]] Result<TreeV2WorkspaceStoreResult>
    begin_exchange(const NamespacePolicy &policy, const Digest &expected_active,
                   const Digest &pending_manifest,
                   const Digest &worktree_manifest,
                   std::span<const TreeV2Observation> pending_frontier,
                   const security::DeviceIdentity &identity,
                   const security::Sodium &sodium,
                   const SyncNamespaceTransaction *transaction = nullptr) const;
    [[nodiscard]] Result<TreeV2WorkspaceStoreResult>
    finish_exchange(const NamespacePolicy &policy,
                    const Digest &pending_manifest,
                    const security::DeviceIdentity &identity,
                    const security::Sodium &sodium,
                    const SyncNamespaceTransaction *transaction = nullptr) const;

  private:
    [[nodiscard]] Result<TreeV2WorkspaceStoreResult>
    commit(const NamespacePolicy &policy, TreeV2WorkspaceState state,
           TreeV2WorkspaceDecision decision,
           const security::DeviceIdentity &identity,
           const security::Sodium &sodium,
           const SyncNamespaceTransaction *transaction) const;

    std::filesystem::path root_;
    std::shared_ptr<TreeV2StateWitness> witness_;
};

} // namespace iotox::sync
