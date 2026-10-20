#include "test_harness.hpp"

#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"

#include <algorithm>
#include <cerrno>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <fstream>
#include <optional>
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
using iotox::sync::TreeV2BranchHead;
using iotox::sync::TreeV2EntryKind;
using iotox::sync::TreeV2Manifest;
using iotox::sync::TreeV2Observation;
using iotox::sync::TreeV2ScanResult;
using iotox::sync::TreeV2Snapshot;
using iotox::sync::TreeV2SourceDigestCache;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-sync-multiwriter-tree-XXXXXX";
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

class OpenWriter {
  public:
    explicit OpenWriter(const std::filesystem::path &path)
        : descriptor_(::open(path.c_str(), O_WRONLY | O_CLOEXEC)) {
        if (descriptor_ < 0) {
            throw std::runtime_error("open writer failed: " +
                                     std::string(std::strerror(errno)));
        }
    }

    ~OpenWriter() {
        if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
    }

    OpenWriter(const OpenWriter &) = delete;
    OpenWriter &operator=(const OpenWriter &) = delete;

    [[nodiscard]] bool
    refers_to(const std::filesystem::path &path) const noexcept {
        struct stat descriptor_metadata {};
        struct stat path_metadata {};
        return ::fstat(descriptor_, &descriptor_metadata) == 0 &&
               ::lstat(path.c_str(), &path_metadata) == 0 &&
               descriptor_metadata.st_dev == path_metadata.st_dev &&
               descriptor_metadata.st_ino == path_metadata.st_ino;
    }

    void write_at_start(std::string_view text) const {
        std::size_t offset = 0U;
        while (offset < text.size()) {
            const ssize_t written = ::pwrite(
                descriptor_, text.data() + offset, text.size() - offset,
                static_cast<off_t>(offset));
            if (written > 0) {
                offset += static_cast<std::size_t>(written);
                continue;
            }
            if (written < 0 && errno == EINTR) continue;
            throw std::runtime_error("descriptor write failed: " +
                                     std::string(std::strerror(errno)));
        }
        if (::fsync(descriptor_) != 0) {
            throw std::runtime_error("descriptor fsync failed: " +
                                     std::string(std::strerror(errno)));
        }
    }

  private:
    int descriptor_{-1};
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

void write_file(const std::filesystem::path &path, std::string_view text,
                mode_t mode = 0600) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(text.data(), static_cast<std::streamsize>(text.size()));
    output.close();
    if (!output || ::chmod(path.c_str(), mode) != 0)
        throw std::runtime_error("unable to write private test file");
}

std::string read_file(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    const auto bytes = std::filesystem::file_size(path);
    std::string result(static_cast<std::size_t>(bytes), '\0');
    input.read(result.data(), static_cast<std::streamsize>(result.size()));
    if (!input) throw std::runtime_error("unable to read test file");
    return result;
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

TreeV2BranchHead branch(const NamespacePolicy &policy,
                        const TreeV2Manifest &tree,
                        const DeviceIdentity &writer, const Sodium &crypto) {
    auto created = iotox::sync::create_tree_v2_branch_head(
        policy, tree, std::nullopt, {}, writer, crypto);
    if (!created) throw std::runtime_error(created.status().message());
    return created.value();
}

TreeV2Observation observation(const NamespacePolicy &policy,
                              const TreeV2BranchHead &head,
                              const Sodium &crypto) {
    auto record =
        iotox::sync::tree_v2_branch_record_digest(policy, head, crypto);
    if (!record) throw std::runtime_error(record.status().message());
    return TreeV2Observation{head.writer, head.generation, record.value()};
}

TreeV2BranchHead successor(const NamespacePolicy &policy,
                           const TreeV2Manifest &tree,
                           const TreeV2BranchHead &previous,
                           const TreeV2BranchHead &observed,
                           const DeviceIdentity &writer, const Sodium &crypto) {
    const TreeV2Observation remote = observation(policy, observed, crypto);
    auto created = iotox::sync::create_tree_v2_branch_head(
        policy, tree, previous, std::span<const TreeV2Observation>(&remote, 1U),
        writer, crypto);
    if (!created) throw std::runtime_error(created.status().message());
    return created.value();
}

} // namespace

IOTOX_TEST("tree-v2 worktree scan retains origins and creates tombstones") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(worktree);
    make_directory(worktree / "docs");
    write_file(worktree / "docs" / "field.txt", "generation one");
    const NamespacePolicy policy = policy_for(root, left, right);

    auto first = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 1U);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    IOTOX_CHECK(first.value().changed);
    IOTOX_CHECK(first.value().new_events == 2U);
    IOTOX_CHECK(first.value().manifest.entries.size() == 2U);
    IOTOX_CHECK(first.value().files.size() == 1U);

    auto unchanged = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, first.value().manifest, left.public_key(), 2U);
    IOTOX_CHECK_MSG(unchanged.ok(), unchanged.status().message());
    IOTOX_CHECK(!unchanged.value().changed);
    IOTOX_CHECK(unchanged.value().new_events == 0U);
    IOTOX_CHECK(unchanged.value().manifest == first.value().manifest);

    write_file(worktree / "docs" / "field.txt", "generation two", 0700);
    auto changed = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, first.value().manifest, left.public_key(), 2U);
    IOTOX_CHECK_MSG(changed.ok(), changed.status().message());
    IOTOX_CHECK(changed.value().changed);
    IOTOX_CHECK(changed.value().new_events == 1U);
    IOTOX_CHECK(changed.value().manifest.entries.front().origin.generation ==
                1U);
    IOTOX_CHECK(changed.value().manifest.entries.back().origin.generation ==
                2U);
    IOTOX_CHECK(changed.value().manifest.entries.back().executable);

    IOTOX_CHECK(std::filesystem::remove(worktree / "docs" / "field.txt"));
    auto removed = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, changed.value().manifest, left.public_key(), 3U);
    IOTOX_CHECK_MSG(removed.ok(), removed.status().message());
    IOTOX_CHECK(removed.value().new_events == 1U);
    IOTOX_CHECK(removed.value().manifest.entries.back().kind ==
                TreeV2EntryKind::tombstone);
    IOTOX_CHECK(removed.value().manifest.entries.back().origin.generation ==
                3U);

    make_directory(worktree / ".iotox-conflicts");
    write_file(worktree / ".iotox-conflicts" / "derived", "ignored");
    auto ignored = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, removed.value().manifest, left.public_key(), 4U);
    IOTOX_CHECK_MSG(ignored.ok(), ignored.status().message());
    IOTOX_CHECK(!ignored.value().changed);
}

IOTOX_TEST("tree-v2 worktree scan reuses stable source digest cache") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(worktree);
    write_file(worktree / "first.txt", "alpha");
    write_file(worktree / "second.txt", "bravo");
    const NamespacePolicy policy = policy_for(root, left, right);

    TreeV2SourceDigestCache cache;
    auto first = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 1U, nullptr,
        nullptr, &cache);
    IOTOX_CHECK_MSG(first.ok(), first.status().message());
    IOTOX_CHECK(first.value().hashed_file_digests == 2U);
    IOTOX_CHECK(first.value().reused_file_digests == 0U);
    IOTOX_CHECK(cache.entries() == 2U);

    auto unchanged = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, first.value().manifest, left.public_key(), 2U,
        nullptr, &cache, &cache);
    IOTOX_CHECK_MSG(unchanged.ok(), unchanged.status().message());
    IOTOX_CHECK(!unchanged.value().changed);
    IOTOX_CHECK(unchanged.value().hashed_file_digests == 0U);
    IOTOX_CHECK(unchanged.value().reused_file_digests == 2U);
    IOTOX_CHECK(cache.entries() == 2U);

    write_file(worktree / "second.txt", "bravo with changed bytes");
    auto changed = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, first.value().manifest, left.public_key(), 2U,
        nullptr, &cache, &cache);
    IOTOX_CHECK_MSG(changed.ok(), changed.status().message());
    IOTOX_CHECK(changed.value().changed);
    IOTOX_CHECK(changed.value().hashed_file_digests == 1U);
    IOTOX_CHECK(changed.value().reused_file_digests == 1U);
    IOTOX_CHECK(changed.value().new_events == 1U);
    IOTOX_CHECK(cache.entries() == 2U);
}

IOTOX_TEST("tree-v2 sparse scan walks only selected roots") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(worktree);
    make_directory(worktree / "shared");
    make_directory(worktree / "shared" / "selected");
    make_directory(worktree / "shared" / "ignored");
    make_directory(worktree / "private");
    write_file(worktree / "shared" / "selected" / "field.txt", "kept");
    write_file(worktree / "shared" / "ignored" / "field.txt", "skipped");
    write_file(worktree / "private" / "secret.txt", "skipped");

    NamespacePolicy policy = policy_for(root, left, right);
    policy.projection.includes = {"shared/selected"};
    IOTOX_CHECK(iotox::sync::validate_namespace_policy(policy).ok());

    auto scan = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 1U);
    IOTOX_CHECK_MSG(scan.ok(), scan.status().message());
    IOTOX_CHECK(scan.value().inspected_entries == 3U);
    IOTOX_CHECK(scan.value().directories == 2U);
    IOTOX_CHECK(scan.value().files.size() == 1U);
    IOTOX_CHECK(scan.value().file_bytes == 4U);
    IOTOX_CHECK(scan.value().manifest.entries.size() == 3U);
    IOTOX_CHECK(scan.value().new_events == 3U);
}

IOTOX_TEST(
    "tree-v2 store rejects source mutation through an open descriptor") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(worktree);
    const std::filesystem::path source = worktree / "field.txt";
    write_file(source, "snapshot-A");
    OpenWriter writer(source);
    const NamespacePolicy policy = policy_for(root, left, right);

    auto scan = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 1U);
    IOTOX_CHECK_MSG(scan.ok(), scan.status().message());
    IOTOX_CHECK(scan.value().files.size() == 1U);
    const std::filesystem::path scanned_object =
        iotox::sync::tree_v2_object_path(
            policy, scan.value().files.front().content);

    writer.write_at_start("snapshot-B");
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    auto stored = iotox::sync::store_tree_v2_scan_objects(
        policy, scan.value(), transaction.value());
    IOTOX_CHECK(!stored.ok());
    IOTOX_CHECK(stored.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(!std::filesystem::exists(scanned_object));
    IOTOX_CHECK(!std::filesystem::exists(scanned_object.parent_path() /
                                        ".install.tmp"));

    auto rescan = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 2U);
    IOTOX_CHECK_MSG(rescan.ok(), rescan.status().message());
    auto restored = iotox::sync::store_tree_v2_scan_objects(
        policy, rescan.value(), transaction.value());
    IOTOX_CHECK_MSG(restored.ok(), restored.status().message());
    IOTOX_CHECK(restored.value().installed_objects == 1U);
}

IOTOX_TEST(
    "tree-v2 cached CAS inventory revalidates before metadata effects") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path first_tree = temporary.path() / "first";
    const std::filesystem::path second_tree = temporary.path() / "second";
    make_directory(root);
    make_directory(first_tree);
    make_directory(second_tree);
    write_file(first_tree / "first.txt", "first immutable object");
    write_file(second_tree / "second.txt", "second immutable object");
    const NamespacePolicy policy = policy_for(root, left, right);

    auto first = iotox::sync::scan_tree_v2_worktree(
        policy, first_tree, std::nullopt, left.public_key(), 1U);
    auto second = iotox::sync::scan_tree_v2_worktree(
        policy, second_tree, std::nullopt, left.public_key(), 2U);
    IOTOX_CHECK(first.ok());
    IOTOX_CHECK(second.ok());
    const std::filesystem::path recovered_fanout =
        root / "tree-v2" / "objects" / "ab";
    make_directory(root / "tree-v2");
    make_directory(root / "tree-v2" / "objects");
    make_directory(recovered_fanout);
    write_file(recovered_fanout / ".install.tmp", "interrupted install");
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    auto inventory = iotox::sync::inspect_tree_v2_object_store(
        policy, transaction.value());
    IOTOX_CHECK_MSG(inventory.ok(), inventory.status().message());
    IOTOX_CHECK(inventory.value().objects() == 0U);
    IOTOX_CHECK(
        !std::filesystem::exists(recovered_fanout / ".install.tmp"));

    auto stored_first = iotox::sync::store_tree_v2_scan_objects(
        policy, first.value(), inventory.value(), transaction.value());
    auto stored_second = iotox::sync::store_tree_v2_scan_objects(
        policy, second.value(), inventory.value(), transaction.value());
    IOTOX_CHECK_MSG(stored_first.ok(), stored_first.status().message());
    IOTOX_CHECK_MSG(stored_second.ok(), stored_second.status().message());
    IOTOX_CHECK(stored_first.value().installed_objects == 1U);
    IOTOX_CHECK(stored_second.value().installed_objects == 1U);
    IOTOX_CHECK(stored_first.value().inspected_objects == 0U);
    IOTOX_CHECK(stored_second.value().inspected_objects == 0U);
    IOTOX_CHECK(inventory.value().objects() == 2U);

    auto exact = iotox::sync::revalidate_tree_v2_object_store(
        policy, inventory.value(), transaction.value());
    IOTOX_CHECK_MSG(exact.ok(), exact.status().message());
    IOTOX_CHECK(exact.value().inspected_objects == 2U);

    const std::filesystem::path concurrent_tree =
        temporary.path() / "concurrent";
    make_directory(concurrent_tree);
    write_file(concurrent_tree / "third.txt", "concurrent valid object");
    auto concurrent = iotox::sync::scan_tree_v2_worktree(
        policy, concurrent_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(concurrent.ok());
    auto concurrent_store = iotox::sync::store_tree_v2_scan_objects(
        policy, concurrent.value(), transaction.value());
    IOTOX_CHECK_MSG(concurrent_store.ok(),
                    concurrent_store.status().message());
    auto additive = iotox::sync::revalidate_tree_v2_object_store(
        policy, inventory.value(), transaction.value());
    IOTOX_CHECK_MSG(additive.ok(), additive.status().message());
    IOTOX_CHECK(additive.value().inspected_objects == 3U);

    const std::filesystem::path corrupted =
        iotox::sync::tree_v2_object_path(
            policy, first.value().files.front().content);
    write_file(corrupted, "wrong immutable object");
    auto rejected = iotox::sync::revalidate_tree_v2_object_store(
        policy, inventory.value(), transaction.value());
    IOTOX_CHECK(!rejected.ok());
    IOTOX_CHECK(rejected.status().code() == iotox::ErrorCode::protocol_error);
}

IOTOX_TEST("tree-v2 CAS and projection preserve both concurrent files") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path left_tree = temporary.path() / "left-tree";
    const std::filesystem::path right_tree = temporary.path() / "right-tree";
    make_directory(root);
    make_directory(left_tree);
    make_directory(right_tree);
    write_file(left_tree / "field.txt", "left concurrent bytes");
    write_file(right_tree / "field.txt", "right concurrent bytes");
    const NamespacePolicy policy = policy_for(root, left, right);

    auto left_scan = iotox::sync::scan_tree_v2_worktree(
        policy, left_tree, std::nullopt, left.public_key(), 1U);
    auto right_scan = iotox::sync::scan_tree_v2_worktree(
        policy, right_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK_MSG(left_scan.ok(), left_scan.status().message());
    IOTOX_CHECK_MSG(right_scan.ok(), right_scan.status().message());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    auto stored_left = iotox::sync::store_tree_v2_scan_objects(
        policy, left_scan.value(), transaction.value());
    auto stored_right = iotox::sync::store_tree_v2_scan_objects(
        policy, right_scan.value(), transaction.value());
    IOTOX_CHECK_MSG(stored_left.ok(), stored_left.status().message());
    IOTOX_CHECK_MSG(stored_right.ok(), stored_right.status().message());
    IOTOX_CHECK(stored_left.value().installed_objects == 1U);
    IOTOX_CHECK(stored_right.value().installed_objects == 1U);

    const TreeV2Snapshot left_snapshot{
        branch(policy, left_scan.value().manifest, left, crypto),
        left_scan.value().manifest};
    const TreeV2Snapshot right_snapshot{
        branch(policy, right_scan.value().manifest, right, crypto),
        right_scan.value().manifest};
    const std::vector<TreeV2Snapshot> snapshots{left_snapshot, right_snapshot};
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, snapshots, crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    IOTOX_CHECK(merged.value().conflicts.size() == 1U);

    const std::filesystem::path projection = temporary.path() / "projection";
    auto materialized = iotox::sync::materialize_tree_v2_merge(
        policy, merged.value(), projection, crypto, transaction.value());
    IOTOX_CHECK_MSG(materialized.ok(), materialized.status().message());
    IOTOX_CHECK(materialized.value().files == 1U);
    IOTOX_CHECK(materialized.value().conflict_files == 1U);
    const std::string ordinary = read_file(projection / "field.txt");
    IOTOX_CHECK(ordinary == "left concurrent bytes" ||
                ordinary == "right concurrent bytes");

    std::vector<std::string> projected_contents{ordinary};
    const std::filesystem::path conflicts =
        projection / std::string(iotox::sync::kTreeV2ConflictRoot);
    for (const auto &entry :
         std::filesystem::recursive_directory_iterator(conflicts)) {
        if (entry.is_regular_file() &&
            entry.path().filename() != ".iotox-projection")
            projected_contents.push_back(read_file(entry.path()));
    }
    std::sort(projected_contents.begin(), projected_contents.end());
    IOTOX_CHECK(projected_contents ==
                std::vector<std::string>(
                    {"left concurrent bytes", "right concurrent bytes"}));
}

IOTOX_TEST("tree-v2 projection materializes concurrent deletion provenance") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path left_tree = temporary.path() / "left-tree";
    const std::filesystem::path right_tree = temporary.path() / "right-tree";
    make_directory(root);
    make_directory(left_tree);
    make_directory(right_tree);
    write_file(left_tree / "field.txt", "base");
    write_file(right_tree / "field.txt", "base");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto left_base = iotox::sync::scan_tree_v2_worktree(
        policy, left_tree, std::nullopt, left.public_key(), 1U);
    auto right_base = iotox::sync::scan_tree_v2_worktree(
        policy, right_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(left_base.ok());
    IOTOX_CHECK(right_base.ok());
    IOTOX_CHECK(std::filesystem::remove(left_tree / "field.txt"));
    write_file(right_tree / "field.txt", "edited while offline");
    auto removed = iotox::sync::scan_tree_v2_worktree(
        policy, left_tree, left_base.value().manifest, left.public_key(), 2U);
    auto edited = iotox::sync::scan_tree_v2_worktree(
        policy, right_tree, right_base.value().manifest, right.public_key(),
        2U);
    IOTOX_CHECK(removed.ok());
    IOTOX_CHECK(edited.ok());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    auto stored = iotox::sync::store_tree_v2_scan_objects(
        policy, edited.value(), transaction.value());
    IOTOX_CHECK_MSG(stored.ok(), stored.status().message());
    const TreeV2BranchHead left_one =
        branch(policy, left_base.value().manifest, left, crypto);
    const TreeV2BranchHead right_one =
        branch(policy, right_base.value().manifest, right, crypto);
    const TreeV2Snapshot left_snapshot{
        successor(policy, removed.value().manifest, left_one, right_one, left,
                  crypto),
        removed.value().manifest};
    const TreeV2Snapshot right_snapshot{
        successor(policy, edited.value().manifest, right_one, left_one, right,
                  crypto),
        edited.value().manifest};
    const std::vector<TreeV2Snapshot> snapshots{left_snapshot, right_snapshot};
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, snapshots, crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    const std::filesystem::path projection = temporary.path() / "projection";
    auto materialized = iotox::sync::materialize_tree_v2_merge(
        policy, merged.value(), projection, crypto, transaction.value());
    IOTOX_CHECK_MSG(materialized.ok(), materialized.status().message());
    IOTOX_CHECK(read_file(projection / "field.txt") == "edited while offline");
    IOTOX_CHECK(materialized.value().conflict_tombstones == 1U);
}

IOTOX_TEST(
    "tree-v2 writable projection exchanges atomically and preserves edits") {
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
    write_file(worktree / "field.txt", "left bytes");
    write_file(remote / "field.txt", "right bytes");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto left_scan = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 1U);
    auto right_scan = iotox::sync::scan_tree_v2_worktree(
        policy, remote, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(left_scan.ok());
    IOTOX_CHECK(right_scan.ok());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, left_scan.value(), transaction.value())
                    .ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, right_scan.value(), transaction.value())
                    .ok());
    const std::vector<TreeV2Snapshot> snapshots{
        {branch(policy, left_scan.value().manifest, left, crypto),
         left_scan.value().manifest},
        {branch(policy, right_scan.value().manifest, right, crypto),
         right_scan.value().manifest}};
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, snapshots, crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    bool seam_called = false;
    const iotox::sync::TreeV2WorktreeSeams seams{
        [&seam_called]() {
            seam_called = true;
            return iotox::Status{iotox::ErrorCode::unavailable,
                                 "injected before exchange"};
        },
        {}};
    auto interrupted = iotox::sync::update_tree_v2_worktree(
        policy, left_scan.value().manifest, merged.value(), worktree,
        left.public_key(), crypto, transaction.value(), nullptr, seams);
    IOTOX_CHECK(!interrupted.ok());
    IOTOX_CHECK(interrupted.status().code() == iotox::ErrorCode::unavailable);
    IOTOX_CHECK(seam_called);
    IOTOX_CHECK(read_file(worktree / "field.txt") == "left bytes");
    const std::filesystem::path staging =
        temporary.path() / ".worktree.iotox-field-notes.stage";
    IOTOX_CHECK(!std::filesystem::exists(staging));

    auto updated = iotox::sync::update_tree_v2_worktree(
        policy, left_scan.value().manifest, merged.value(), worktree,
        left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(updated.ok(), updated.status().message());
    IOTOX_CHECK(updated.value().exchanged);
    IOTOX_CHECK(updated.value().preserved_unselected_entries == 0U);
    IOTOX_CHECK(updated.value().preserved_unselected_directories == 0U);
    IOTOX_CHECK(updated.value().preserved_unselected_files == 0U);
    IOTOX_CHECK(updated.value().preserved_unselected_bytes == 0U);
    IOTOX_CHECK(std::filesystem::exists(worktree / "field.txt"));
    IOTOX_CHECK(std::filesystem::exists(
        worktree / std::string(iotox::sync::kTreeV2ConflictRoot)));
    IOTOX_CHECK(!std::filesystem::exists(staging));

    write_file(worktree / "field.txt", "unpublished local edit");
    auto refused = iotox::sync::update_tree_v2_worktree(
        policy, merged.value().manifest, merged.value(), worktree,
        left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(read_file(worktree / "field.txt") == "unpublished local edit");
}

IOTOX_TEST(
    "tree-v2 projection preserves an open-descriptor mutation immediately "
    "before exchange") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path active_tree = temporary.path() / "active";
    const std::filesystem::path pending_tree = temporary.path() / "pending";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(active_tree);
    make_directory(pending_tree);
    write_file(active_tree / "field.txt", "active bytes");
    write_file(pending_tree / "field.txt", "pending bytes");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto active_scan = iotox::sync::scan_tree_v2_worktree(
        policy, active_tree, std::nullopt, left.public_key(), 1U);
    auto pending_scan = iotox::sync::scan_tree_v2_worktree(
        policy, pending_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(active_scan.ok());
    IOTOX_CHECK(pending_scan.ok());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, active_scan.value(), transaction.value())
                    .ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, pending_scan.value(), transaction.value())
                    .ok());
    auto active = iotox::sync::summarize_tree_v2_manifest(
        policy, active_scan.value().manifest);
    auto pending = iotox::sync::summarize_tree_v2_manifest(
        policy, pending_scan.value().manifest);
    IOTOX_CHECK(active.ok());
    IOTOX_CHECK(pending.ok());
    auto projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), worktree, crypto, transaction.value());
    IOTOX_CHECK_MSG(projected.ok(), projected.status().message());

    OpenWriter held_writer(worktree / "field.txt");
    const iotox::sync::TreeV2WorktreeSeams seams{
        [&held_writer]() {
            held_writer.write_at_start("held fd edit");
            return iotox::Status::success();
        },
        {}};
    auto updated = iotox::sync::update_tree_v2_worktree(
        policy, active_scan.value().manifest, pending.value(), worktree,
        left.public_key(), crypto, transaction.value(),
        &active_scan.value().manifest, seams);
    IOTOX_CHECK(!updated.ok());
    IOTOX_CHECK(updated.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(updated.status().message().find("preserved for operator recovery") !=
                std::string::npos);
    IOTOX_CHECK(read_file(worktree / "field.txt") == "pending bytes");
    const std::filesystem::path staging =
        iotox::sync::tree_v2_worktree_staging_path(policy, worktree);
    IOTOX_CHECK(read_file(staging / "field.txt") == "held fd edit");
    IOTOX_CHECK(held_writer.refers_to(staging / "field.txt"));
    IOTOX_CHECK(iotox::sync::tree_v2_projection_marker_matches(
        policy, pending_scan.value().manifest, worktree, crypto));
    IOTOX_CHECK(iotox::sync::tree_v2_projection_marker_matches(
        policy, active_scan.value().manifest, staging, crypto));

    auto refused = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(read_file(staging / "field.txt") == "held fd edit");

    write_file(worktree / "field.txt", "held fd edit");
    write_file(staging / "field.txt", "active bytes");
    auto recovered = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value().exchanged);
    IOTOX_CHECK(!std::filesystem::exists(staging));
    IOTOX_CHECK(read_file(worktree / "field.txt") == "held fd edit");
}

IOTOX_TEST(
    "tree-v2 projection preserves an open-descriptor mutation after exchange") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path active_tree = temporary.path() / "active";
    const std::filesystem::path pending_tree = temporary.path() / "pending";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(active_tree);
    make_directory(pending_tree);
    write_file(active_tree / "field.txt", "active bytes");
    write_file(pending_tree / "field.txt", "pending bytes");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto active_scan = iotox::sync::scan_tree_v2_worktree(
        policy, active_tree, std::nullopt, left.public_key(), 1U);
    auto pending_scan = iotox::sync::scan_tree_v2_worktree(
        policy, pending_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(active_scan.ok());
    IOTOX_CHECK(pending_scan.ok());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, active_scan.value(), transaction.value())
                    .ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, pending_scan.value(), transaction.value())
                    .ok());
    auto active = iotox::sync::summarize_tree_v2_manifest(
        policy, active_scan.value().manifest);
    auto pending = iotox::sync::summarize_tree_v2_manifest(
        policy, pending_scan.value().manifest);
    IOTOX_CHECK(active.ok());
    IOTOX_CHECK(pending.ok());
    auto projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), worktree, crypto, transaction.value());
    IOTOX_CHECK_MSG(projected.ok(), projected.status().message());

    OpenWriter held_writer(worktree / "field.txt");
    iotox::sync::TreeV2WorktreeSeams seams;
    seams.after_exchange = [&held_writer]() {
        held_writer.write_at_start("post exchange");
        return iotox::Status::success();
    };
    auto updated = iotox::sync::update_tree_v2_worktree(
        policy, active_scan.value().manifest, pending.value(), worktree,
        left.public_key(), crypto, transaction.value(),
        &active_scan.value().manifest, seams);
    IOTOX_CHECK(!updated.ok());
    IOTOX_CHECK(updated.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(updated.status().message().find("preserved for operator recovery") !=
                std::string::npos);
    IOTOX_CHECK(read_file(worktree / "field.txt") == "pending bytes");
    const std::filesystem::path staging =
        iotox::sync::tree_v2_worktree_staging_path(policy, worktree);
    IOTOX_CHECK(read_file(staging / "field.txt") == "post exchange");
    IOTOX_CHECK(held_writer.refers_to(staging / "field.txt"));
    IOTOX_CHECK(iotox::sync::tree_v2_projection_marker_matches(
        policy, pending_scan.value().manifest, worktree, crypto));
    IOTOX_CHECK(iotox::sync::tree_v2_projection_marker_matches(
        policy, active_scan.value().manifest, staging, crypto));

    auto refused = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(read_file(staging / "field.txt") == "post exchange");

    write_file(worktree / "field.txt", "post exchange");
    write_file(staging / "field.txt", "active bytes");
    auto recovered = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(recovered.value().exchanged);
    IOTOX_CHECK(!std::filesystem::exists(staging));
    IOTOX_CHECK(read_file(worktree / "field.txt") == "post exchange");
}

IOTOX_TEST(
    "tree-v2 projection preserves an excluded open-descriptor mutation") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path active_tree = temporary.path() / "active";
    const std::filesystem::path pending_tree = temporary.path() / "pending";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(active_tree);
    make_directory(pending_tree);
    make_directory(active_tree / "shared");
    make_directory(pending_tree / "shared");
    write_file(active_tree / "shared" / "readme", "active bytes");
    write_file(pending_tree / "shared" / "readme", "pending bytes");
    write_file(pending_tree / "shared" / "remote", "remote bytes");
    NamespacePolicy policy = policy_for(root, left, right);
    policy.projection.includes = {"shared"};
    policy.projection.excludes = {"shared/cache"};
    IOTOX_CHECK(iotox::sync::validate_namespace_policy(policy).ok());
    auto active_scan = iotox::sync::scan_tree_v2_worktree(
        policy, active_tree, std::nullopt, left.public_key(), 1U);
    auto pending_scan = iotox::sync::scan_tree_v2_worktree(
        policy, pending_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(active_scan.ok());
    IOTOX_CHECK(pending_scan.ok());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, active_scan.value(), transaction.value())
                    .ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, pending_scan.value(), transaction.value())
                    .ok());
    auto active = iotox::sync::summarize_tree_v2_manifest(
        policy, active_scan.value().manifest);
    auto pending = iotox::sync::summarize_tree_v2_manifest(
        policy, pending_scan.value().manifest);
    IOTOX_CHECK(active.ok());
    IOTOX_CHECK(pending.ok());
    auto projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), worktree, crypto, transaction.value());
    IOTOX_CHECK_MSG(projected.ok(), projected.status().message());
    make_directory(worktree / "shared" / "cache");
    write_file(worktree / "shared" / "cache" / "local", "local bytes");

    OpenWriter held_writer(worktree / "shared" / "cache" / "local");
    const iotox::sync::TreeV2WorktreeSeams seams{
        [&held_writer]() {
            held_writer.write_at_start("excluded fd edit");
            return iotox::Status::success();
        },
        {}};
    auto updated = iotox::sync::update_tree_v2_worktree(
        policy, active_scan.value().manifest, pending.value(), worktree,
        left.public_key(), crypto, transaction.value(),
        &active_scan.value().manifest, seams);
    IOTOX_CHECK(!updated.ok());
    IOTOX_CHECK(updated.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(updated.status().message().find(
                    "preserved unselected projection changed") !=
                std::string::npos);
    const std::filesystem::path staging =
        iotox::sync::tree_v2_worktree_staging_path(policy, worktree);
    IOTOX_CHECK(read_file(worktree / "shared" / "readme") ==
                "pending bytes");
    IOTOX_CHECK(read_file(worktree / "shared" / "cache" / "local") ==
                "local bytes");
    IOTOX_CHECK(read_file(staging / "shared" / "cache" / "local") ==
                "excluded fd edit");
    IOTOX_CHECK(
        held_writer.refers_to(staging / "shared" / "cache" / "local"));

    auto refused = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(std::filesystem::exists(staging));
    write_file(worktree / "shared" / "cache" / "local",
               "excluded fd edit");
    auto recovered = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK_MSG(recovered.ok(), recovered.status().message());
    IOTOX_CHECK(!std::filesystem::exists(staging));
    IOTOX_CHECK(read_file(worktree / "shared" / "cache" / "local") ==
                "excluded fd edit");
}

IOTOX_TEST(
    "tree-v2 marker mismatch never hides a selected deletion") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path active_tree = temporary.path() / "active";
    const std::filesystem::path pending_tree = temporary.path() / "pending";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(active_tree);
    make_directory(pending_tree);
    write_file(active_tree / "field.txt", "active bytes");
    write_file(pending_tree / "field.txt", "pending bytes");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto active_scan = iotox::sync::scan_tree_v2_worktree(
        policy, active_tree, std::nullopt, left.public_key(), 1U);
    auto pending_scan = iotox::sync::scan_tree_v2_worktree(
        policy, pending_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(active_scan.ok());
    IOTOX_CHECK(pending_scan.ok());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, active_scan.value(), transaction.value())
                    .ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, pending_scan.value(), transaction.value())
                    .ok());
    auto active = iotox::sync::summarize_tree_v2_manifest(
        policy, active_scan.value().manifest);
    auto pending = iotox::sync::summarize_tree_v2_manifest(
        policy, pending_scan.value().manifest);
    IOTOX_CHECK(active.ok());
    IOTOX_CHECK(pending.ok());
    auto projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), worktree, crypto, transaction.value());
    IOTOX_CHECK_MSG(projected.ok(), projected.status().message());

    NamespacePolicy metadata_transition = policy;
    metadata_transition.projection.metadata =
        iotox::sync::TreeV2MetadataMode::owner_mode_v2;
    auto transition = iotox::sync::tree_v2_projection_transition(
        metadata_transition, active_scan.value().manifest, worktree, crypto);
    IOTOX_CHECK_MSG(transition.ok(), transition.status().message());
    IOTOX_CHECK(transition.value().has_value());

    NamespacePolicy selection_transition = policy;
    selection_transition.projection.includes = {"field.txt"};
    transition = iotox::sync::tree_v2_projection_transition(
        selection_transition, active_scan.value().manifest, worktree, crypto);
    IOTOX_CHECK_MSG(transition.ok(), transition.status().message());
    IOTOX_CHECK(transition.value().has_value());

    IOTOX_CHECK(std::filesystem::remove(worktree / "field.txt"));
    auto deleted = iotox::sync::scan_tree_v2_worktree(
        selection_transition, worktree, active_scan.value().manifest,
        left.public_key(), 2U, &*transition.value());
    IOTOX_CHECK_MSG(deleted.ok(), deleted.status().message());
    IOTOX_CHECK(deleted.value().changed);
    IOTOX_CHECK(deleted.value().manifest.entries.back().kind ==
                TreeV2EntryKind::tombstone);

    IOTOX_CHECK(std::filesystem::remove(
        worktree / std::string(iotox::sync::kTreeV2ConflictRoot) /
        ".iotox-projection"));
    transition = iotox::sync::tree_v2_projection_transition(
        policy, active_scan.value().manifest, worktree, crypto);
    IOTOX_CHECK(!transition.ok());
    auto refused = iotox::sync::update_tree_v2_worktree(
        policy, active_scan.value().manifest, pending.value(), worktree,
        left.public_key(), crypto, transaction.value(),
        &active_scan.value().manifest);
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(!std::filesystem::exists(
        iotox::sync::tree_v2_worktree_staging_path(policy, worktree)));
    IOTOX_CHECK(!std::filesystem::exists(worktree / "field.txt"));
}

IOTOX_TEST(
    "tree-v2 selective projection preserves local exclusions and owner modes") {
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
    write_file(worktree / "shared" / "readme", "selected", 0400);
    write_file(worktree / "shared" / "cache" / "local", "cache survives");
    write_file(worktree / "private" / "secret", "private survives", 0500);
    write_file(remote / "shared" / "remote", "remote selected", 0500);

    NamespacePolicy policy = policy_for(root, left, right);
    policy.projection.metadata =
        iotox::sync::TreeV2MetadataMode::owner_mode_v2;
    policy.projection.includes = {"shared"};
    policy.projection.excludes = {"shared/cache"};
    IOTOX_CHECK(iotox::sync::validate_namespace_policy(policy).ok());

    auto local_scan = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 1U);
    auto remote_scan = iotox::sync::scan_tree_v2_worktree(
        policy, remote, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK_MSG(local_scan.ok(), local_scan.status().message());
    IOTOX_CHECK_MSG(remote_scan.ok(), remote_scan.status().message());
    IOTOX_CHECK(local_scan.value().manifest.entries.size() == 2U);
    IOTOX_CHECK(local_scan.value().manifest.entries.back().owner_mode == 4U);

    write_file(worktree / "shared" / "cache" / "new-local", "also ignored");
    auto unchanged = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, local_scan.value().manifest, left.public_key(), 2U);
    IOTOX_CHECK_MSG(unchanged.ok(), unchanged.status().message());
    IOTOX_CHECK(!unchanged.value().changed);
    IOTOX_CHECK(unchanged.value().new_events == 0U);

    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, local_scan.value(), transaction.value())
                    .ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, remote_scan.value(), transaction.value())
                    .ok());
    const std::vector<TreeV2Snapshot> snapshots{
        {branch(policy, local_scan.value().manifest, left, crypto),
         local_scan.value().manifest},
        {branch(policy, remote_scan.value().manifest, right, crypto),
         remote_scan.value().manifest}};
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, snapshots, crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    auto updated = iotox::sync::update_tree_v2_worktree(
        policy, local_scan.value().manifest, merged.value(), worktree,
        left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(updated.ok(), updated.status().message());
    IOTOX_CHECK(updated.value().exchanged);
    IOTOX_CHECK(updated.value().preserved_unselected_entries == 5U);
    IOTOX_CHECK(updated.value().preserved_unselected_directories == 2U);
    IOTOX_CHECK(updated.value().preserved_unselected_files == 3U);
    IOTOX_CHECK(updated.value().preserved_unselected_bytes == 42U);
    IOTOX_CHECK(read_file(worktree / "shared" / "remote") ==
                "remote selected");
    IOTOX_CHECK(read_file(worktree / "shared" / "cache" / "local") ==
                "cache survives");
    IOTOX_CHECK(read_file(worktree / "shared" / "cache" / "new-local") ==
                "also ignored");
    IOTOX_CHECK(read_file(worktree / "private" / "secret") ==
                "private survives");
    struct stat metadata {};
    IOTOX_CHECK(::lstat((worktree / "shared" / "readme").c_str(),
                        &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0700)) ==
                static_cast<mode_t>(0400));
    IOTOX_CHECK(::lstat((worktree / "shared" / "remote").c_str(),
                        &metadata) == 0);
    IOTOX_CHECK((metadata.st_mode & static_cast<mode_t>(0700)) ==
                static_cast<mode_t>(0500));
}

IOTOX_TEST("tree-v2 exchange recovery covers both durable layouts and ambiguity") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path left_tree = temporary.path() / "left-tree";
    const std::filesystem::path right_tree = temporary.path() / "right-tree";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_directory(root);
    make_directory(left_tree);
    make_directory(right_tree);
    write_file(left_tree / "field.txt", "active bytes");
    write_file(right_tree / "field.txt", "pending bytes");
    const NamespacePolicy policy = policy_for(root, left, right);
    auto active_scan = iotox::sync::scan_tree_v2_worktree(
        policy, left_tree, std::nullopt, left.public_key(), 1U);
    auto pending_scan = iotox::sync::scan_tree_v2_worktree(
        policy, right_tree, std::nullopt, right.public_key(), 1U);
    IOTOX_CHECK(active_scan.ok());
    IOTOX_CHECK(pending_scan.ok());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, active_scan.value(), transaction.value())
                    .ok());
    IOTOX_CHECK(iotox::sync::store_tree_v2_scan_objects(
                    policy, pending_scan.value(), transaction.value())
                    .ok());
    auto active = iotox::sync::summarize_tree_v2_manifest(
        policy, active_scan.value().manifest);
    auto pending = iotox::sync::summarize_tree_v2_manifest(
        policy, pending_scan.value().manifest);
    IOTOX_CHECK(active.ok());
    IOTOX_CHECK(pending.ok());

    auto projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), worktree, crypto, transaction.value());
    IOTOX_CHECK_MSG(projected.ok(), projected.status().message());
    auto before_exchange = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK_MSG(before_exchange.ok(), before_exchange.status().message());
    IOTOX_CHECK(before_exchange.value().exchanged);
    IOTOX_CHECK(read_file(worktree / "field.txt") == "pending bytes");

    const std::filesystem::path staging =
        iotox::sync::tree_v2_worktree_staging_path(policy, worktree);
    projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), staging, crypto, transaction.value());
    IOTOX_CHECK(projected.ok());
    auto after_exchange = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), worktree, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK_MSG(after_exchange.ok(), after_exchange.status().message());
    IOTOX_CHECK(after_exchange.value().exchanged);
    IOTOX_CHECK(!std::filesystem::exists(staging));
    IOTOX_CHECK(read_file(worktree / "field.txt") == "pending bytes");

    // An ordinary local writer can change the new directory after the atomic
    // exchange but before the signed workspace finish. The retained old
    // projection makes that side unambiguous; recovery must preserve the new
    // local bytes for the next forward reconciliation instead of fencing the
    // namespace forever or deleting the edit.
    projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), staging, crypto, transaction.value());
    IOTOX_CHECK(projected.ok());
    write_file(worktree / "field.txt", "local bytes after exchange");
    auto modified_after_exchange =
        iotox::sync::recover_tree_v2_worktree_exchange(
            policy, active_scan.value().manifest,
            active_scan.value().manifest, pending.value(), worktree,
            left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(modified_after_exchange.ok(),
                    modified_after_exchange.status().message());
    IOTOX_CHECK(modified_after_exchange.value().exchanged);
    IOTOX_CHECK(!std::filesystem::exists(staging));
    IOTOX_CHECK(read_file(worktree / "field.txt") ==
                "local bytes after exchange");

    const std::filesystem::path ambiguous = temporary.path() / "ambiguous";
    projected = iotox::sync::materialize_tree_v2_merge(
        policy, active.value(), ambiguous, crypto, transaction.value());
    IOTOX_CHECK(projected.ok());
    write_file(ambiguous / "field.txt", "uncommitted local bytes");
    auto refused = iotox::sync::recover_tree_v2_worktree_exchange(
        policy, active_scan.value().manifest, active_scan.value().manifest,
        pending.value(), ambiguous, left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK(read_file(ambiguous / "field.txt") ==
                "uncommitted local bytes");
}

IOTOX_TEST("tree-v2 scans stores and projects the maximum ordinary tree") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    const std::filesystem::path projection = temporary.path() / "projection";
    make_directory(root);
    make_directory(worktree);
    NamespacePolicy policy = policy_for(root, left, right);
    const std::size_t file_count =
        static_cast<std::size_t>(policy.quotas.maximum_objects);
    for (std::size_t index = 0U; index < file_count; ++index) {
        write_file(worktree / ("entry-" + std::to_string(index)),
                   "bounded-large-tree-value-" + std::to_string(index) +
                       "\n");
    }

    auto scan = iotox::sync::scan_tree_v2_worktree(
        policy, worktree, std::nullopt, left.public_key(), 1U);
    IOTOX_CHECK_MSG(scan.ok(), scan.status().message());
    IOTOX_CHECK(scan.value().changed);
    IOTOX_CHECK(scan.value().new_events == file_count);
    IOTOX_CHECK(scan.value().manifest.entries.size() == file_count);
    IOTOX_CHECK(scan.value().files.size() == file_count);

    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    auto stored = iotox::sync::store_tree_v2_scan_objects(
        policy, scan.value(), transaction.value());
    IOTOX_CHECK_MSG(stored.ok(), stored.status().message());
    IOTOX_CHECK(stored.value().installed_objects == file_count);
    const TreeV2Snapshot snapshot{
        branch(policy, scan.value().manifest, left, crypto),
        scan.value().manifest};
    auto merged = iotox::sync::merge_tree_v2_snapshots(
        policy, std::span<const TreeV2Snapshot>(&snapshot, 1U), crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    IOTOX_CHECK(merged.value().paths == file_count);
    IOTOX_CHECK(merged.value().live_files == file_count);
    IOTOX_CHECK(merged.value().conflicts.empty());
    auto materialized = iotox::sync::materialize_tree_v2_merge(
        policy, merged.value(), projection, crypto, transaction.value());
    IOTOX_CHECK_MSG(materialized.ok(), materialized.status().message());
    IOTOX_CHECK(materialized.value().files == file_count);
    IOTOX_CHECK(read_file(projection / "entry-0") ==
                "bounded-large-tree-value-0\n");
    IOTOX_CHECK(read_file(projection / "entry-4095") ==
                "bounded-large-tree-value-4095\n");
}
