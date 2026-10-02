#include "test_harness.hpp"

#include "iotox/sync_digest.hpp"
#include "iotox/sync_multiwriter_reconcile.hpp"

#include <algorithm>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::TreeV2BranchStore;
using iotox::sync::TreeV2Snapshot;
using iotox::sync::TreeV2SourceDigestCache;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-sync-multiwriter-reconcile-XXXXXX";
        std::vector<char> mutable_pattern(pattern.begin(), pattern.end());
        mutable_pattern.push_back('\0');
        char *created = ::mkdtemp(mutable_pattern.data());
        if (created == nullptr) throw std::runtime_error("mkdtemp failed");
        path_ = created;
        if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0)
            throw std::runtime_error("chmod failed");
    }

    ~TempDirectory() {
        std::error_code ignored;
        std::filesystem::remove_all(path_, ignored);
    }

    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

Sodium sodium() {
    auto loaded = Sodium::load();
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

DeviceIdentity identity(const std::filesystem::path &path,
                        const Sodium &crypto) {
    auto loaded = DeviceIdentity::load_or_create(path, crypto, true);
    if (!loaded) throw std::runtime_error(loaded.status().message());
    return std::move(loaded).value();
}

void make_directory(const std::filesystem::path &path) {
    if (!std::filesystem::create_directory(path) ||
        ::chmod(path.c_str(), static_cast<mode_t>(0700)) != 0) {
        throw std::runtime_error("unable to create private directory");
    }
}

void write_file(const std::filesystem::path &path, std::string_view text) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(text.data(), static_cast<std::streamsize>(text.size()));
    output.close();
    if (!output || ::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
        throw std::runtime_error("unable to write private file");
}

NamespacePolicy policy_for(const std::filesystem::path &root,
                           const DeviceIdentity &left,
                           const DeviceIdentity &right) {
    NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = root.string();
    policy.engine = Engine::tree_v2;
    policy.writers = {left.public_key(), right.public_key()};
    std::sort(policy.writers.begin(), policy.writers.end());
    return policy;
}

} // namespace

IOTOX_TEST("tree-v2 reconcile preserves offline concurrency then explicit "
           "resolution") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    const std::filesystem::path remote = temporary.path() / "remote";
    make_directory(root);
    make_directory(worktree);
    make_directory(remote);
    write_file(worktree / "field.txt", "common base");
    write_file(remote / "field.txt", "remote offline edit");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());

    auto initialized = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());
    IOTOX_CHECK(initialized.value().workspace_initialized);
    IOTOX_CHECK(initialized.value().workspace_exchanged);
    IOTOX_CHECK(initialized.value().conflicts == 0U);

    auto remote_scan = iotox::sync::scan_tree_v2_worktree(
        policy, remote, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK_MSG(remote_scan.ok(), remote_scan.status().message());
    auto remote_objects = iotox::sync::store_tree_v2_scan_objects(
        policy, remote_scan.value(), transaction.value());
    IOTOX_CHECK_MSG(remote_objects.ok(), remote_objects.status().message());
    auto remote_head = iotox::sync::create_tree_v2_branch_head(
        policy, remote_scan.value().manifest, std::nullopt, {}, right, crypto);
    IOTOX_CHECK_MSG(remote_head.ok(), remote_head.status().message());
    TreeV2BranchStore branches(root);
    auto accepted = branches.accept(
        policy,
        TreeV2Snapshot{remote_head.value(), remote_scan.value().manifest},
        crypto, transaction.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());

    write_file(worktree / "field.txt", "local offline edit");
    auto conflicted = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(conflicted.ok(), conflicted.status().message());
    IOTOX_CHECK(conflicted.value().local_changed);
    IOTOX_CHECK(conflicted.value().local_events == 1U);
    IOTOX_CHECK(conflicted.value().branch_advances == 1U);
    IOTOX_CHECK(conflicted.value().conflicts == 1U);
    IOTOX_CHECK(conflicted.value().frontier_writers == 2U);
    const std::filesystem::path conflicts =
        worktree / std::string(iotox::sync::kTreeV2ConflictRoot);
    IOTOX_CHECK(std::filesystem::exists(conflicts));

    auto frontier = branches.load_frontier(policy, crypto, transaction.value());
    IOTOX_CHECK(frontier.ok());
    const auto local =
        std::find_if(frontier.value().begin(), frontier.value().end(),
                     [&left](const TreeV2Snapshot &snapshot) {
                         return snapshot.head.writer == left.public_key();
                     });
    IOTOX_CHECK(local != frontier.value().end());
    IOTOX_CHECK(!iotox::sync::tree_v2_head_observes(
        local->head, iotox::sync::TreeV2Version{right.public_key(), 1U}));
    IOTOX_CHECK(local->manifest.entries.size() == 1U);

    write_file(worktree / "field.txt", "explicit resolution");
    auto resolved = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(resolved.ok(), resolved.status().message());
    IOTOX_CHECK(resolved.value().local_events == 1U);
    IOTOX_CHECK(resolved.value().branch_advances == 1U);
    IOTOX_CHECK(resolved.value().conflicts == 0U);
    std::size_t derived = 0U;
    for (const auto &entry :
         std::filesystem::recursive_directory_iterator(conflicts)) {
        if (entry.is_regular_file() &&
            entry.path().filename() != ".iotox-projection") {
            ++derived;
        }
    }
    IOTOX_CHECK(derived == 0U);
}

IOTOX_TEST("tree-v2 reconcile skips CAS refresh for unchanged stable workspace") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(worktree);
    write_file(worktree / "field.txt", "stable content");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto digest = iotox::sync::hash_sync_file_sha256(worktree / "field.txt");
    IOTOX_CHECK_MSG(digest.ok(), digest.status().message());

    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    TreeV2SourceDigestCache cache;
    auto initialized = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value(), nullptr, &cache);
    IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());
    IOTOX_CHECK(initialized.value().source_inspected_entries == 1U);
    IOTOX_CHECK(initialized.value().source_hashed_file_digests == 1U);
    IOTOX_CHECK(initialized.value().source_reused_file_digests == 0U);
    IOTOX_CHECK(initialized.value().cas_inspected_objects == 0U);
    IOTOX_CHECK(initialized.value().cas_inspected_bytes == 0U);
    IOTOX_CHECK(initialized.value().cas_installed_objects == 1U);
    IOTOX_CHECK(initialized.value().cas_installed_bytes == 14U);
    IOTOX_CHECK(initialized.value().cas_reused_objects == 0U);
    IOTOX_CHECK(initialized.value().projection_directories == 0U);
    IOTOX_CHECK(initialized.value().projection_files == 1U);
    IOTOX_CHECK(initialized.value().projection_bytes == 14U);
    IOTOX_CHECK(initialized.value().projection_conflict_files == 0U);
    IOTOX_CHECK(initialized.value().projection_conflict_tombstones == 0U);
    IOTOX_CHECK(initialized.value().projection_preserved_unselected_entries ==
                0U);
    IOTOX_CHECK(initialized.value().projection_preserved_unselected_bytes ==
                0U);
    const std::filesystem::path object =
        iotox::sync::tree_v2_object_path(policy, digest.value());
    IOTOX_CHECK(std::filesystem::exists(object));

    auto stable = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value(), nullptr, &cache);
    IOTOX_CHECK_MSG(stable.ok(), stable.status().message());
    IOTOX_CHECK(!stable.value().local_changed);
    IOTOX_CHECK(stable.value().source_inspected_entries == 2U);
    IOTOX_CHECK(stable.value().source_reused_file_digests <= 1U);
    IOTOX_CHECK(stable.value().cas_inspected_objects == 0U);
    IOTOX_CHECK(stable.value().cas_inspected_bytes == 0U);
    IOTOX_CHECK(stable.value().cas_installed_objects == 0U);
    IOTOX_CHECK(stable.value().cas_installed_bytes == 0U);
    IOTOX_CHECK(stable.value().cas_reused_objects == 0U);
    IOTOX_CHECK(stable.value().projection_directories == 0U);
    IOTOX_CHECK(stable.value().projection_files == 0U);
    IOTOX_CHECK(stable.value().projection_bytes == 0U);
    IOTOX_CHECK(stable.value().projection_conflict_files == 0U);
    IOTOX_CHECK(stable.value().projection_conflict_tombstones == 0U);
    IOTOX_CHECK(stable.value().branch_advances == 0U);
    IOTOX_CHECK(!stable.value().workspace_exchanged);
    IOTOX_CHECK(std::filesystem::remove(object));

    auto unchanged = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value(), nullptr, &cache);
    IOTOX_CHECK_MSG(unchanged.ok(), unchanged.status().message());
    IOTOX_CHECK(!unchanged.value().local_changed);
    IOTOX_CHECK(unchanged.value().source_inspected_entries == 2U);
    IOTOX_CHECK(unchanged.value().source_hashed_file_digests == 0U);
    IOTOX_CHECK(unchanged.value().source_reused_file_digests == 1U);
    IOTOX_CHECK(unchanged.value().cas_inspected_objects == 0U);
    IOTOX_CHECK(unchanged.value().cas_inspected_bytes == 0U);
    IOTOX_CHECK(unchanged.value().cas_installed_objects == 0U);
    IOTOX_CHECK(unchanged.value().cas_installed_bytes == 0U);
    IOTOX_CHECK(unchanged.value().cas_reused_objects == 0U);
    IOTOX_CHECK(unchanged.value().projection_directories == 0U);
    IOTOX_CHECK(unchanged.value().projection_files == 0U);
    IOTOX_CHECK(unchanged.value().projection_bytes == 0U);
    IOTOX_CHECK(unchanged.value().projection_conflict_files == 0U);
    IOTOX_CHECK(unchanged.value().projection_conflict_tombstones == 0U);
    IOTOX_CHECK(unchanged.value().branch_advances == 0U);
    IOTOX_CHECK(!unchanged.value().workspace_exchanged);
    IOTOX_CHECK(unchanged.value().projection_preserved_unselected_entries ==
                0U);
    IOTOX_CHECK(unchanged.value().projection_preserved_unselected_bytes == 0U);
    IOTOX_CHECK(!std::filesystem::exists(object));
}

IOTOX_TEST("tree-v2 sparse reconcile reports preserved projection work") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    const std::filesystem::path remote = temporary.path() / "remote";
    make_directory(root);
    make_directory(worktree);
    make_directory(remote);
    make_directory(worktree / "shared");
    make_directory(worktree / "shared" / "cache");
    make_directory(worktree / "private");
    make_directory(remote / "shared");
    write_file(worktree / "shared" / "readme", "selected");
    write_file(worktree / "shared" / "cache" / "local", "cache survives");
    write_file(worktree / "private" / "secret", "private survives");
    write_file(remote / "shared" / "remote", "remote selected");

    NamespacePolicy policy = policy_for(root, left, right);
    policy.projection.metadata =
        iotox::sync::TreeV2MetadataMode::owner_mode_v2;
    policy.projection.includes = {"shared"};
    policy.projection.excludes = {"shared/cache"};
    IOTOX_CHECK(iotox::sync::validate_namespace_policy(policy).ok());

    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    auto initialized = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());
    IOTOX_CHECK(initialized.value().workspace_initialized);
    IOTOX_CHECK(initialized.value().workspace_exchanged);
    IOTOX_CHECK(initialized.value().projection_preserved_unselected_entries ==
                4U);
    IOTOX_CHECK(
        initialized.value().projection_preserved_unselected_directories == 2U);
    IOTOX_CHECK(initialized.value().projection_preserved_unselected_files ==
                2U);
    IOTOX_CHECK(initialized.value().projection_preserved_unselected_bytes ==
                30U);

    write_file(worktree / "shared" / "cache" / "new-local", "also ignored");
    auto remote_scan = iotox::sync::scan_tree_v2_worktree(
        policy, remote, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK_MSG(remote_scan.ok(), remote_scan.status().message());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, remote_scan.value(), transaction.value())
                    .ok());
    auto remote_head = iotox::sync::create_tree_v2_branch_head(
        policy, remote_scan.value().manifest, std::nullopt, {}, right, crypto);
    IOTOX_CHECK_MSG(remote_head.ok(), remote_head.status().message());
    TreeV2BranchStore branches(root);
    auto accepted = branches.accept(
        policy,
        TreeV2Snapshot{remote_head.value(), remote_scan.value().manifest},
        crypto, transaction.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());

    auto reconciled = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(reconciled.ok(), reconciled.status().message());
    IOTOX_CHECK(!reconciled.value().local_changed);
    IOTOX_CHECK(reconciled.value().workspace_exchanged);
    IOTOX_CHECK(reconciled.value().projection_preserved_unselected_entries ==
                5U);
    IOTOX_CHECK(reconciled.value().projection_preserved_unselected_directories ==
                2U);
    IOTOX_CHECK(reconciled.value().projection_preserved_unselected_files == 3U);
    IOTOX_CHECK(reconciled.value().projection_preserved_unselected_bytes ==
                42U);
}

IOTOX_TEST("tree-v2 reconcile repairs checkpoint branch before workspace marker") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    const std::filesystem::path remote = temporary.path() / "remote";
    make_directory(root);
    make_directory(worktree);
    make_directory(remote);
    write_file(worktree / "field.txt", "stable checkpoint content");
    write_file(remote / "field.txt", "stable checkpoint content");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    auto initialized = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK(initialized.ok());

    auto remote_scan = iotox::sync::scan_tree_v2_worktree(
        policy, remote, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(remote_scan.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, remote_scan.value(), transaction.value())
                    .ok());
    auto remote_head = iotox::sync::create_tree_v2_branch_head(
        policy, remote_scan.value().manifest, std::nullopt, {}, right, crypto);
    IOTOX_CHECK(remote_head.ok());
    TreeV2BranchStore branches(root);
    IOTOX_CHECK(branches.accept(
                    policy,
                    TreeV2Snapshot{remote_head.value(),
                                   remote_scan.value().manifest},
                    crypto, transaction.value())
                    .ok());
    auto observed = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(observed.ok(), observed.status().message());
    IOTOX_CHECK(observed.value().frontier_writers == 2U);
    IOTOX_CHECK(observed.value().branch_advances == 0U);
    auto quiet = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(quiet.ok(), quiet.status().message());
    IOTOX_CHECK(quiet.value().branch_advances == 0U);
    auto floor = branches.checkpoint_local(policy, left, crypto,
                                           transaction.value());
    IOTOX_CHECK_MSG(floor.ok(), floor.status().message());
    auto recovered = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value().recovered_pending_exchange);
    IOTOX_CHECK(recovered.value().conflicts == 0U);
    auto recovered_frontier =
        branches.load_frontier(policy, crypto, transaction.value());
    IOTOX_CHECK(recovered_frontier.ok());
    const auto recovered_local = std::find_if(
        recovered_frontier.value().begin(), recovered_frontier.value().end(),
        [&left](const TreeV2Snapshot &snapshot) {
            return snapshot.head.writer == left.public_key();
        });
    IOTOX_CHECK(recovered_local != recovered_frontier.value().end());
    IOTOX_CHECK(recovered_local->head.checkpoint);
    IOTOX_CHECK(recovered_local->head.generation ==
                floor.value().snapshot.head.generation);

    auto next = iotox::sync::checkpoint_tree_v2_workspace(
        policy, worktree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(next.ok(), next.status().message());
    IOTOX_CHECK(next.value().checkpoint.snapshot.head.checkpoint);
    IOTOX_CHECK(next.value().checkpoint.snapshot.head.generation ==
                floor.value().snapshot.head.generation + 1U);
}
