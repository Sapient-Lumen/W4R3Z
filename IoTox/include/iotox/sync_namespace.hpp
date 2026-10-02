#pragma once

#include "iotox/security/sodium.hpp"
#include "iotox/status.hpp"

#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <shared_mutex>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace iotox::sync {

inline constexpr std::size_t kMaximumNamespaces = 64U;
inline constexpr std::size_t kMaximumNamespaceRecordBytes = 64U * 1024U;
inline constexpr std::size_t kMaximumNamespacePrincipals = 64U;
inline constexpr std::size_t kMaximumTreeV2SelectionRules = 64U;

using PrincipalId = security::SigningPublicKey;

enum class Engine : std::uint8_t {
    range_v1 = 1U,
    content_v2 = 2U,
    treepack_v1 = 3U,
    tree_v2 = 4U,
};

enum class ActivationMode : std::uint8_t {
  disabled = 1U,
  manual = 2U,
};

// Host-local tree-v2 projection policy. Selection rules use canonical path
// component prefixes, never globs. Empty INCLUDE means the complete tree;
// EXCLUDE always wins. owner_mode_v2 carries the file owner's r/w/x bits in
// manifest v2 while directories remain normalized private state.
enum class TreeV2MetadataMode : std::uint8_t {
  executable_v1 = 1U,
  owner_mode_v2 = 2U,
};

struct TreeV2ProjectionPolicy {
  TreeV2MetadataMode metadata{TreeV2MetadataMode::executable_v1};
  std::vector<std::string> includes;
  std::vector<std::string> excludes;

  [[nodiscard]] bool operator==(const TreeV2ProjectionPolicy &) const =
      default;
};

struct Quotas {
  std::uint64_t maximum_artifact_bytes{64U * 1024U * 1024U};
  std::uint64_t maximum_manifest_bytes{4U * 1024U * 1024U};
  std::uint64_t maximum_store_bytes{512U * 1024U * 1024U};
  std::uint64_t maximum_staging_bytes{128U * 1024U * 1024U};
  std::uint64_t maximum_objects{4096U};
  std::uint64_t maximum_retained_revisions{4U};
  std::uint64_t maximum_peers{8U};
  std::uint64_t maximum_lanes{4U};
  std::uint64_t maximum_outstanding_requests{64U};

  [[nodiscard]] bool operator==(const Quotas &) const = default;
};

// Host-local policy. It is never accepted from a remote peer and never grants
// authority by itself: transport operations must additionally pass the
// authority-ledger capability check allocated for synchronization.
struct NamespacePolicy {
  std::string id;
  std::string root;
  Engine engine{Engine::range_v1};
  ActivationMode activation{ActivationMode::disabled};
  Quotas quotas{};
  std::vector<PrincipalId> writers;
  std::vector<PrincipalId> subscribers;
  TreeV2ProjectionPolicy projection;

  [[nodiscard]] bool operator==(const NamespacePolicy &) const = default;
};

struct RegistrySnapshot {
  std::uint64_t generation{0U};
  std::size_t namespaces{0U};
  std::size_t enabled_namespaces{0U};

  [[nodiscard]] bool operator==(const RegistrySnapshot &) const = default;
};

enum class NamespaceInstallDisposition : std::uint8_t {
  installed = 1U,
  duplicate = 2U,
};

struct NamespaceInstallResult {
  NamespaceInstallDisposition disposition{
      NamespaceInstallDisposition::installed};
  NamespacePolicy policy;

  [[nodiscard]] bool operator==(const NamespaceInstallResult &) const =
      default;
};

enum class NamespaceUpdateDisposition : std::uint8_t {
  updated = 1U,
  duplicate = 2U,
};

struct NamespaceUpdateResult {
  NamespaceUpdateDisposition disposition{
      NamespaceUpdateDisposition::updated};
  NamespacePolicy policy;

  [[nodiscard]] bool operator==(const NamespaceUpdateResult &) const =
      default;
};

enum class NamespaceRemoveDisposition : std::uint8_t {
  removed = 1U,
  absent = 2U,
};

struct NamespaceRemoveResult {
  NamespaceRemoveDisposition disposition{
      NamespaceRemoveDisposition::removed};
  std::string namespace_id;

  [[nodiscard]] bool operator==(const NamespaceRemoveResult &) const =
      default;
};

[[nodiscard]] bool valid_namespace_id(std::string_view value) noexcept;
[[nodiscard]] std::string_view engine_name(Engine engine) noexcept;
[[nodiscard]] std::string_view
tree_v2_metadata_mode_name(TreeV2MetadataMode mode) noexcept;
[[nodiscard]] bool valid_tree_v2_selection_path(std::string_view path) noexcept;
[[nodiscard]] bool tree_v2_path_selected(const NamespacePolicy &policy,
                                         std::string_view path,
                                         bool directory) noexcept;
[[nodiscard]] Status validate_namespace_policy(const NamespacePolicy &policy);
// Prepares the empty ROOT/namespaces administration directory while retaining
// the same no-follow and owner-only boundary used by all store operations.
// ROOT itself must already exist as a normalized private directory.
[[nodiscard]] Status prepare_namespace_store(const std::filesystem::path &root,
                                             std::uint32_t expected_owner_uid);
// Convenience namespaces created by the Agent keep generated synchronization
// state in one deterministic private data/ child of the policy store. This
// never aliases the watched source tree.
[[nodiscard]] Result<std::filesystem::path> managed_namespace_root(
    const std::filesystem::path &policy_store_root,
    std::string_view namespace_id);
[[nodiscard]] Result<std::filesystem::path> prepare_managed_namespace_root(
    const std::filesystem::path &policy_store_root,
    std::string_view namespace_id, std::uint32_t expected_owner_uid);
[[nodiscard]] Result<std::vector<std::uint8_t>>
encode_namespace_policy(const NamespacePolicy &policy);
[[nodiscard]] Result<NamespacePolicy>
decode_namespace_policy(std::span<const std::uint8_t> bytes);

// Loads ROOT/namespaces/<namespace-id>.namespace. ROOT and namespaces must be
// normalized absolute, owner-only, no-follow directories. Records must be
// single-link owner-only regular files. Any unexpected entry fails the load.
[[nodiscard]] Result<std::vector<NamespacePolicy>>
load_namespace_store(const std::filesystem::path &root,
                     std::uint32_t expected_owner_uid);

// Atomically and durably creates one canonical owner-local policy record.
// Exact retry is a duplicate; replacing an existing ID is deliberately
// refused in the first administration slice. The store must already satisfy
// the strict loader boundary.
[[nodiscard]] Result<NamespaceInstallResult>
install_namespace_policy(const std::filesystem::path &root,
                         const NamespacePolicy &policy,
                         std::uint32_t expected_owner_uid);

// Atomically replaces only the live-administration fields of one existing
// policy. ID, root, engine, and quotas are immutable in this first update
// slice. Exact retry is a duplicate.
[[nodiscard]] Result<NamespaceUpdateResult>
update_namespace_policy(const std::filesystem::path &root,
                        const NamespacePolicy &policy,
                        std::uint32_t expected_owner_uid);

// Durably removes only the policy record. Namespace content and signed local
// state remain untouched and cannot become deletion candidates from this
// operation. Exact retry reports absent.
[[nodiscard]] Result<NamespaceRemoveResult>
remove_namespace_policy(const std::filesystem::path &root,
                        std::string_view namespace_id,
                        std::uint32_t expected_owner_uid);

// Removes only strictly shaped owner-private update temporaries left before
// the atomic rename commit point. Any ambiguity fails closed.
[[nodiscard]] Status cleanup_namespace_policy_temporaries(
    const std::filesystem::path &root,
    std::uint32_t expected_owner_uid);

class NamespaceRegistry {
public:
  [[nodiscard]] Status replace(std::vector<NamespacePolicy> policies);
  // Emergency security transition: remove every live policy without requiring
  // another generation value. Used only when durable truth cannot be loaded.
  void fail_closed() noexcept;
  [[nodiscard]] Result<NamespacePolicy> resolve(std::string_view id) const;
  [[nodiscard]] std::vector<NamespacePolicy> list() const;
  [[nodiscard]] RegistrySnapshot snapshot() const;

private:
  mutable std::shared_mutex mutex_;
  std::vector<NamespacePolicy> policies_;
  std::uint64_t generation_{0U};
};

} // namespace iotox::sync
