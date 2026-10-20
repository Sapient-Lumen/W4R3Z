#pragma once

#include "iotox/status.hpp"
#include "iotox/sync_multiwriter.hpp"
#include "iotox/sync_transaction.hpp"

#include <cstdint>
#include <filesystem>
#include <functional>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace iotox::sync {

struct TreeV2ScannedFile {
    std::string path;
    Digest content{};
    std::uint64_t content_bytes{0U};
    std::filesystem::path source;

    [[nodiscard]] bool operator==(const TreeV2ScannedFile &) const = default;
};

struct TreeV2ScanResult {
    TreeV2Manifest manifest;
    std::vector<TreeV2ScannedFile> files;
    std::uint64_t directories{0U};
    std::uint64_t file_bytes{0U};
    std::uint64_t inspected_entries{0U};
    std::uint64_t hashed_file_digests{0U};
    std::uint64_t reused_file_digests{0U};
    std::uint64_t new_events{0U};
    bool changed{false};

    [[nodiscard]] bool operator==(const TreeV2ScanResult &) const = default;
};

// In-process, non-durable file digest cache for repeated local source scans.
// Entries are created only by scan_tree_v2_worktree() after a stable file hash
// or a previously verified reuse. Callers cannot forge cache entries directly;
// a process restart, namespace/source/projection change, or any file metadata
// identity change falls back to hashing.
class TreeV2SourceDigestCache final {
  public:
    struct FileIdentity {
        std::uint64_t device{0U};
        std::uint64_t inode{0U};
        std::uint64_t mode{0U};
        std::uint64_t links{0U};
        std::uint64_t owner{0U};
        std::uint64_t bytes{0U};
        std::int64_t modified_seconds{0};
        std::int64_t modified_nanoseconds{0};
        std::int64_t changed_seconds{0};
        std::int64_t changed_nanoseconds{0};

        [[nodiscard]] bool operator==(const FileIdentity &) const = default;
    };

    [[nodiscard]] std::size_t entries() const noexcept {
        return files_.size();
    }
    [[nodiscard]] bool empty() const noexcept { return files_.empty(); }
    void clear() {
        namespace_id_.clear();
        source_.clear();
        projection_ = {};
        files_.clear();
        verified_ = false;
    }

  private:
    struct Entry {
        FileIdentity identity;
        Digest content{};
        std::uint64_t content_bytes{0U};
    };

    friend Result<TreeV2ScanResult> scan_tree_v2_worktree(
        const NamespacePolicy &, const std::filesystem::path &,
        const std::optional<TreeV2Manifest> &, const PrincipalId &,
        std::uint64_t, const TreeV2ProjectionPolicy *,
        const TreeV2SourceDigestCache *, TreeV2SourceDigestCache *);

    std::string namespace_id_;
    std::filesystem::path source_;
    TreeV2ProjectionPolicy projection_;
    std::map<std::string, Entry> files_;
    bool verified_{false};
};

struct TreeV2ObjectStoreResult {
    std::uint64_t inspected_objects{0U};
    std::uint64_t inspected_bytes{0U};
    std::uint64_t installed_objects{0U};
    std::uint64_t installed_bytes{0U};
    std::uint64_t reused_objects{0U};

    [[nodiscard]] bool
    operator==(const TreeV2ObjectStoreResult &) const = default;
};

// One strictly verified in-memory view of the immutable tree-v2 CAS. This is
// deliberately not a durable index: callers may reuse it only while building
// one effect-free object closure, and must revalidate it under the same
// namespace transaction that commits metadata or projects a worktree.
// Private state prevents an unverified caller-constructed inventory from
// becoming quota authority.
class TreeV2ObjectInventory final {
  public:
    TreeV2ObjectInventory() = default;

    [[nodiscard]] std::uint64_t objects() const noexcept {
        return objects_.size();
    }
    [[nodiscard]] std::uint64_t bytes() const noexcept { return bytes_; }

  private:
    friend Result<TreeV2ObjectInventory> inspect_tree_v2_object_store(
        const NamespacePolicy &, const SyncNamespaceTransaction &);
    friend Result<TreeV2ObjectStoreResult> store_tree_v2_scan_objects(
        const NamespacePolicy &, const TreeV2ScanResult &,
        TreeV2ObjectInventory &, const SyncNamespaceTransaction &);
    friend Result<TreeV2ObjectStoreResult> revalidate_tree_v2_object_store(
        const NamespacePolicy &, const TreeV2ObjectInventory &,
        const SyncNamespaceTransaction &);

    std::string namespace_id_;
    std::filesystem::path root_;
    std::map<Digest, std::uint64_t> objects_;
    std::uint64_t bytes_{0U};
    bool verified_{false};
};

struct TreeV2ProjectionResult {
    std::uint64_t directories{0U};
    std::uint64_t files{0U};
    std::uint64_t bytes{0U};
    std::uint64_t conflict_files{0U};
    std::uint64_t conflict_tombstones{0U};

    [[nodiscard]] bool
    operator==(const TreeV2ProjectionResult &) const = default;
};

struct TreeV2WorktreeUpdateResult {
    TreeV2ProjectionResult projection;
    bool exchanged{false};
    std::uint64_t preserved_unselected_entries{0U};
    std::uint64_t preserved_unselected_directories{0U};
    std::uint64_t preserved_unselected_files{0U};
    std::uint64_t preserved_unselected_bytes{0U};

    [[nodiscard]] bool
    operator==(const TreeV2WorktreeUpdateResult &) const = default;
};

// Test-only observation/injection points around an atomic projection exchange.
// Production callers leave both default-empty. The post-exchange point is
// before either projection is validated or obsolete staging can be removed.
struct TreeV2WorktreeSeams {
    std::function<Status()> before_exchange;
    std::function<Status()> after_exchange;
};

// Scans one owner-controlled writable tree. BASELINE is the last complete
// merged manifest projected there. Unchanged paths retain their original
// causal versions and unresolved candidates; changed paths replace the set
// with one new local event. Missing live paths become signed tombstones.
[[nodiscard]] Result<TreeV2ScanResult> scan_tree_v2_worktree(
    const NamespacePolicy &policy, const std::filesystem::path &source,
    const std::optional<TreeV2Manifest> &baseline,
    const PrincipalId &local_writer, std::uint64_t next_generation,
    const TreeV2ProjectionPolicy *previous_projection = nullptr,
    const TreeV2SourceDigestCache *digest_cache = nullptr,
    TreeV2SourceDigestCache *updated_digest_cache = nullptr);

[[nodiscard]] bool tree_v2_projection_marker_matches(
    const NamespacePolicy &policy, const TreeV2Manifest &manifest,
    const std::filesystem::path &destination,
    const security::Sodium &sodium);
// Returns an empty value for the current projection identity, or the canonical
// prior projection policy bound to the authenticated ACTIVE manifest. Missing,
// malformed, or unrelated markers fail closed.
[[nodiscard]] Result<std::optional<TreeV2ProjectionPolicy>>
tree_v2_projection_transition(
    const NamespacePolicy &policy, const TreeV2Manifest &active,
    const std::filesystem::path &destination,
    const security::Sodium &sodium);

[[nodiscard]] std::filesystem::path
tree_v2_object_path(const NamespacePolicy &policy, const Digest &digest);
[[nodiscard]] Status
verify_tree_v2_object_file(const std::filesystem::path &path,
                           const Digest &digest, std::uint64_t expected_bytes);
[[nodiscard]] Result<TreeV2ObjectStoreResult>
store_tree_v2_object_file(const NamespacePolicy &policy, const Digest &digest,
                          std::uint64_t expected_bytes,
                          const std::filesystem::path &source,
                          const SyncNamespaceTransaction &transaction);
[[nodiscard]] std::filesystem::path
tree_v2_worktree_staging_path(const NamespacePolicy &policy,
                              const std::filesystem::path &destination);

// Prospectively accounts the complete strict object store, then imports every
// unique scanned file through verified copy and no-replace digest identity.
[[nodiscard]] Result<TreeV2ObjectStoreResult>
store_tree_v2_scan_objects(const NamespacePolicy &policy,
                           const TreeV2ScanResult &scan,
                           const SyncNamespaceTransaction &transaction);

// Builds one strict, digest-verified CAS view for a bounded receive job. The
// cached overload updates that view after every exact no-replace install,
// avoiding repeated whole-store hashing. Revalidation must succeed immediately
// before any signed branch or projection effect is accepted. Other serialized
// jobs may add independently verified immutable objects; cached members may
// never disappear or change, and the complete observed store must remain in
// quota.
[[nodiscard]] Result<TreeV2ObjectInventory> inspect_tree_v2_object_store(
    const NamespacePolicy &policy,
    const SyncNamespaceTransaction &transaction);
[[nodiscard]] Result<TreeV2ObjectStoreResult> store_tree_v2_scan_objects(
    const NamespacePolicy &policy, const TreeV2ScanResult &scan,
    TreeV2ObjectInventory &inventory,
    const SyncNamespaceTransaction &transaction);
[[nodiscard]] Result<TreeV2ObjectStoreResult> revalidate_tree_v2_object_store(
    const NamespacePolicy &policy, const TreeV2ObjectInventory &inventory,
    const SyncNamespaceTransaction &transaction);

// Materializes one verified merge into a new, absent owner-private directory.
// Ordinary selected values appear at their paths. Every other concurrent live
// value and delete marker appears below the reserved .iotox-conflicts tree.
// This is the safe construction/export primitive.
[[nodiscard]] Result<TreeV2ProjectionResult> materialize_tree_v2_merge(
    const NamespacePolicy &policy, const TreeV2MergeResult &merge,
    const std::filesystem::path &destination, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction);

// Replaces one complete writable projection through a same-parent Linux
// directory exchange. The source is scanned against EXPECTED_WORKTREE both
// before and after target construction, so an observed local edit is never
// overwritten. The new and obsolete projections both revalidate exactly after
// exchange before the old tree is removed. Durable crash recovery around the
// exchange is a separate workspace journal. This bounds mutations visible to
// those scans; it cannot revoke an old descriptor that writes after the final
// validation begins.
// AUTHENTICATED_ACTIVE_PROJECTION is supplied from that signed journal when an
// established marker must authenticate either current or prior host-local
// projection rules. Null is reserved for first projection.
[[nodiscard]] Result<TreeV2WorktreeUpdateResult> update_tree_v2_worktree(
    const NamespacePolicy &policy, const TreeV2Manifest &expected_worktree,
    const TreeV2MergeResult &target, const std::filesystem::path &destination,
    const PrincipalId &local_writer, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    const TreeV2Manifest *authenticated_active_projection = nullptr,
    const TreeV2WorktreeSeams &seams = {});

// Completes a journal-authorized interrupted exchange. The visible and staged
// trees are identified by their exact manifest markers; ambiguous state is
// preserved and refused.
[[nodiscard]] Result<TreeV2WorktreeUpdateResult>
recover_tree_v2_worktree_exchange(const NamespacePolicy &policy,
                                  const TreeV2Manifest &active,
                                  const TreeV2Manifest &expected_worktree,
                                  const TreeV2MergeResult &pending,
                                  const std::filesystem::path &destination,
                                  const PrincipalId &local_writer,
                                  const security::Sodium &sodium,
                                  const SyncNamespaceTransaction &transaction);

} // namespace iotox::sync
