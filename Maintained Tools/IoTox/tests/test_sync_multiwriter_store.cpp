#include "test_harness.hpp"

#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_multiwriter_store.hpp"

#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <span>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>

namespace {

using iotox::security::DeviceIdentity;
using iotox::security::Sodium;
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::TreeV2BranchHead;
using iotox::sync::TreeV2BranchStore;
using iotox::sync::TreeV2BranchStoreDecision;
using iotox::sync::TreeV2Entry;
using iotox::sync::TreeV2EntryKind;
using iotox::sync::TreeV2Manifest;
using iotox::sync::TreeV2Observation;
using iotox::sync::TreeV2Snapshot;
using iotox::sync::TreeV2Version;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-sync-multiwriter-store-XXXXXX";
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

std::vector<std::uint8_t> read_bytes(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("read bytes failed");
    return std::vector<std::uint8_t>(
        std::istreambuf_iterator<char>(input),
        std::istreambuf_iterator<char>());
}

void write_bytes(const std::filesystem::path &path,
                 std::span<const std::uint8_t> bytes) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(reinterpret_cast<const char *>(bytes.data()),
                 static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output || ::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
        throw std::runtime_error("write bytes failed");
}

Digest digest(std::uint8_t value) {
    Digest result{};
    result[0U] = value;
    return result;
}

std::string numbered_path(std::size_t index) {
    std::string number = std::to_string(index);
    if (number.size() < 3U) number.insert(0U, 3U - number.size(), '0');
    return "file-" + number + ".txt";
}

std::string lower_hex(std::span<const std::uint8_t> bytes) {
    static constexpr char digits[] = "0123456789abcdef";
    std::string result;
    result.reserve(bytes.size() * 2U);
    for (const std::uint8_t byte : bytes) {
        result.push_back(digits[byte >> 4U]);
        result.push_back(digits[byte & 0x0fU]);
    }
    return result;
}

TreeV2Manifest manifest(const DeviceIdentity &writer, std::uint64_t generation,
                        std::uint8_t value) {
    return TreeV2Manifest{
        {TreeV2Entry{"field.txt", TreeV2EntryKind::file,
                     TreeV2Version{writer.public_key(), generation},
                     digest(value), 1024U, false}}};
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
                        const std::optional<TreeV2BranchHead> &previous,
                        const DeviceIdentity &writer, const Sodium &crypto) {
    auto created = iotox::sync::create_tree_v2_branch_head(
        policy, tree, previous, {}, writer, crypto);
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

TreeV2BranchHead
observed_branch(const NamespacePolicy &policy, const TreeV2Manifest &tree,
                const std::optional<TreeV2BranchHead> &previous,
                const TreeV2Observation &observed, const DeviceIdentity &writer,
                const Sodium &crypto) {
    auto created = iotox::sync::create_tree_v2_branch_head(
        policy, tree, previous,
        std::span<const TreeV2Observation>(&observed, 1U), writer, crypto);
    if (!created) throw std::runtime_error(created.status().message());
    return created.value();
}

} // namespace

IOTOX_TEST("tree-v2 branch store advances each writer independently") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    TreeV2BranchStore store(root);

    const TreeV2Manifest left_tree = manifest(left, 1U, 1U);
    auto left_one = store.publish_local(policy, left_tree, left, crypto,
                                        transaction.value());
    IOTOX_CHECK_MSG(left_one.ok(), left_one.status().message());
    IOTOX_CHECK(left_one.value().decision ==
                TreeV2BranchStoreDecision::accepted_genesis);
    auto duplicate = store.publish_local(policy, left_tree, left, crypto,
                                         transaction.value());
    IOTOX_CHECK_MSG(duplicate.ok(), duplicate.status().message());
    IOTOX_CHECK(duplicate.value().decision ==
                TreeV2BranchStoreDecision::duplicate);

    const TreeV2Manifest right_tree = manifest(right, 1U, 2U);
    const TreeV2BranchHead right_head =
        branch(policy, right_tree, std::nullopt, right, crypto);
    auto accepted_right =
        store.accept(policy, TreeV2Snapshot{right_head, right_tree}, crypto,
                     transaction.value());
    IOTOX_CHECK_MSG(accepted_right.ok(), accepted_right.status().message());
    IOTOX_CHECK(accepted_right.value().decision ==
                TreeV2BranchStoreDecision::accepted_genesis);

    // No local bytes changed, but the local branch advances once to acknowledge
    // the newly observed remote frontier.
    auto left_two = store.publish_local(policy, left_tree, left, crypto,
                                        transaction.value());
    IOTOX_CHECK_MSG(left_two.ok(), left_two.status().message());
    IOTOX_CHECK(left_two.value().decision ==
                TreeV2BranchStoreDecision::accepted_advance);
    IOTOX_CHECK(left_two.value().snapshot.head.generation == 2U);
    IOTOX_CHECK(iotox::sync::tree_v2_head_observes(
        left_two.value().snapshot.head, TreeV2Version{right.public_key(), 1U}));

    TreeV2BranchStore restarted(root);
    auto frontier =
        restarted.load_frontier(policy, crypto, transaction.value());
    IOTOX_CHECK_MSG(frontier.ok(), frontier.status().message());
    IOTOX_CHECK(frontier.value().size() == 2U);
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, frontier.value(), crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    IOTOX_CHECK(merged.value().conflicts.size() == 1U);
}

IOTOX_TEST("tree-v2 branch store refuses same-writer forks and tamper") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    TreeV2BranchStore store(root);

    const TreeV2Manifest first_tree = manifest(right, 1U, 1U);
    const TreeV2BranchHead first =
        branch(policy, first_tree, std::nullopt, right, crypto);
    auto accepted = store.accept(policy, TreeV2Snapshot{first, first_tree},
                                 crypto, transaction.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());

    const TreeV2Manifest second_tree = manifest(right, 2U, 2U);
    const TreeV2BranchHead second =
        branch(policy, second_tree, first, right, crypto);
    accepted = store.accept(policy, TreeV2Snapshot{second, second_tree}, crypto,
                            transaction.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());

    const TreeV2Manifest fork_tree = manifest(right, 2U, 3U);
    const TreeV2BranchHead fork =
        branch(policy, fork_tree, first, right, crypto);
    IOTOX_CHECK(!store
                     .accept(policy, TreeV2Snapshot{fork, fork_tree}, crypto,
                             transaction.value())
                     .ok());

    const std::filesystem::path unexpected =
        root / "tree-v2" / "branches" / "surprise";
    {
        std::ofstream output(unexpected);
        output << "unexpected";
    }
    IOTOX_CHECK(::chmod(unexpected.c_str(), static_cast<mode_t>(0600)) == 0);
    IOTOX_CHECK(!store.load_frontier(policy, crypto, transaction.value()).ok());
}

IOTOX_TEST(
    "tree-v2 branch store detects every publication record corruption without mutation") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    TreeV2BranchStore store(root);

    const TreeV2Manifest tree = manifest(left, 1U, 1U);
    auto published =
        store.publish_local(policy, tree, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    const std::vector<std::pair<std::filesystem::path, std::string>>
        authoritative = {
            {iotox::sync::tree_v2_manifest_path(
                 policy, published.value().snapshot.head.manifest),
             "manifest"},
            {iotox::sync::tree_v2_branch_record_path(
                 policy, published.value().record),
             "immutable branch record"},
            {root / "tree-v2" / "branches" /
                 (lower_hex(left.public_key()) + ".branch"),
             "branch pointer"},
        };

    for (const auto &[path, family] : authoritative) {
        const std::vector<std::uint8_t> original = read_bytes(path);
        IOTOX_CHECK(!original.empty());
        std::vector<std::uint8_t> corrupt = original;
        corrupt.back() ^= 0x01U;
        write_bytes(path, corrupt);

        auto refused =
            store.load_frontier(policy, crypto, transaction.value());
        IOTOX_CHECK(!refused.ok());
        IOTOX_CHECK(refused.status().code() ==
                    iotox::ErrorCode::protocol_error);
        IOTOX_CHECK_MSG(
            refused.status().message().find(family) != std::string::npos,
            refused.status().message());
        IOTOX_CHECK(read_bytes(path) == corrupt);

        auto overwrite =
            store.publish_local(policy, tree, left, crypto, transaction.value());
        IOTOX_CHECK(!overwrite.ok());
        IOTOX_CHECK(read_bytes(path) == corrupt);

        write_bytes(path, original);
        auto restored =
            store.load_frontier(policy, crypto, transaction.value());
        IOTOX_CHECK_MSG(restored.ok(), restored.status().message());
        IOTOX_CHECK(restored.value().size() == 1U);
        IOTOX_CHECK(restored.value().front() ==
                    published.value().snapshot);
    }
}

IOTOX_TEST("tree-v2 store removes only exact private crash temporaries") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    TreeV2BranchStore store(root);
    IOTOX_CHECK(store.prepare(policy, transaction.value()).ok());

    const std::vector<std::filesystem::path> abandoned = {
        root / "tree-v2" / "branches" / ".update.tmp",
        root / "tree-v2" / "manifests" / ".install.tmp",
        root / "tree-v2" / "records" / ".install.tmp",
    };
    for (const auto &path : abandoned) {
        std::ofstream output(path);
        output << "partial";
        IOTOX_CHECK(::chmod(path.c_str(), static_cast<mode_t>(0600)) == 0);
    }
    auto frontier = store.load_frontier(policy, crypto, transaction.value());
    IOTOX_CHECK_MSG(frontier.ok(), frontier.status().message());
    IOTOX_CHECK(frontier.value().empty());
    for (const auto &path : abandoned)
        IOTOX_CHECK(!std::filesystem::exists(path));

    const std::filesystem::path unsafe =
        root / "tree-v2" / "branches" / ".update.tmp";
    IOTOX_CHECK(std::filesystem::create_directory(unsafe));
    IOTOX_CHECK(!store.load_frontier(policy, crypto, transaction.value()).ok());
}

IOTOX_TEST(
    "tree-v2 store authenticates carried values and explicit resolution") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    TreeV2BranchStore store(root);

    const TreeV2Manifest left_tree = manifest(left, 1U, 1U);
    auto left_one = store.publish_local(policy, left_tree, left, crypto,
                                        transaction.value());
    IOTOX_CHECK_MSG(left_one.ok(), left_one.status().message());
    const TreeV2Observation saw_left =
        observation(policy, left_one.value().snapshot.head, crypto);

    TreeV2Manifest forged = left_tree;
    forged.entries.front().content = digest(99U);
    const TreeV2BranchHead forged_head =
        observed_branch(policy, forged, std::nullopt, saw_left, right, crypto);
    auto refused = store.accept(policy, TreeV2Snapshot{forged_head, forged},
                                crypto, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().message().find("unauthenticated") !=
                std::string::npos);

    const TreeV2Manifest right_tree = manifest(right, 1U, 2U);
    const TreeV2BranchHead right_head =
        branch(policy, right_tree, std::nullopt, right, crypto);
    auto right_one =
        store.accept(policy, TreeV2Snapshot{right_head, right_tree}, crypto,
                     transaction.value());
    IOTOX_CHECK_MSG(right_one.ok(), right_one.status().message());

    auto left_two = store.publish_local(policy, left_tree, left, crypto,
                                        transaction.value());
    IOTOX_CHECK_MSG(left_two.ok(), left_two.status().message());
    const TreeV2Observation saw_right =
        observation(policy, right_one.value().snapshot.head, crypto);
    const TreeV2BranchHead silent_drop =
        observed_branch(policy, left_tree, left_two.value().snapshot.head,
                        saw_right, left, crypto);
    refused = store.accept(policy, TreeV2Snapshot{silent_drop, left_tree},
                           crypto, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK_MSG(refused.status().message().find(
                        "without a new local event") != std::string::npos,
                    refused.status().message());
}

IOTOX_TEST("tree-v2 store authenticates grouped carried histories") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());
    TreeV2BranchStore store(root);

    std::vector<TreeV2Entry> carried;
    constexpr std::size_t carried_paths = 128U;
    carried.reserve(carried_paths + 1U);
    for (std::size_t index = 0U; index < carried_paths; ++index) {
        carried.push_back(TreeV2Entry{
            numbered_path(index), TreeV2EntryKind::file,
            TreeV2Version{left.public_key(), 1U},
            digest(static_cast<std::uint8_t>((index % 250U) + 1U)), 1024U,
            false});
    }
    const TreeV2Manifest left_tree{carried};
    auto left_one = store.publish_local(policy, left_tree, left, crypto,
                                        transaction.value());
    IOTOX_CHECK_MSG(left_one.ok(), left_one.status().message());

    carried.push_back(TreeV2Entry{
        "right.txt", TreeV2EntryKind::file,
        TreeV2Version{right.public_key(), 1U}, digest(0xfeU), 1024U, false});
    const TreeV2Manifest right_tree{std::move(carried)};
    const TreeV2BranchHead right_head = observed_branch(
        policy, right_tree, std::nullopt,
        observation(policy, left_one.value().snapshot.head, crypto), right,
        crypto);
    auto accepted = store.accept(policy, TreeV2Snapshot{right_head, right_tree},
                                 crypto, transaction.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().decision ==
                TreeV2BranchStoreDecision::accepted_genesis);
}

IOTOX_TEST("tree-v2 workspace frontier keeps unseen remote edits concurrent") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    TreeV2BranchStore store(root);

    const TreeV2Manifest left_tree = manifest(left, 1U, 1U);
    auto left_one = store.publish_local(policy, left_tree, left, crypto,
                                        transaction.value());
    IOTOX_CHECK(left_one.ok());
    std::vector<TreeV2Observation> visible{
        observation(policy, left_one.value().snapshot.head, crypto)};

    const TreeV2Manifest right_tree = manifest(right, 1U, 2U);
    const TreeV2BranchHead right_head =
        branch(policy, right_tree, std::nullopt, right, crypto);
    auto right_one =
        store.accept(policy, TreeV2Snapshot{right_head, right_tree}, crypto,
                     transaction.value());
    IOTOX_CHECK(right_one.ok());

    const TreeV2Manifest edited = manifest(left, 2U, 3U);
    auto left_two = store.publish_local_from_frontier(
        policy, edited, visible, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(left_two.ok(), left_two.status().message());
    IOTOX_CHECK(!iotox::sync::tree_v2_head_observes(
        left_two.value().snapshot.head, TreeV2Version{right.public_key(), 1U}));
    auto frontier = store.load_frontier(policy, crypto, transaction.value());
    IOTOX_CHECK(frontier.ok());
    auto merged =
        iotox::sync::merge_tree_v2_snapshots(policy, frontier.value(), crypto);
    IOTOX_CHECK_MSG(merged.ok(), merged.status().message());
    IOTOX_CHECK(merged.value().conflicts.size() == 1U);
    IOTOX_CHECK(merged.value().manifest.entries.size() == 2U);
}

IOTOX_TEST("tree-v2 checkpoint is a fresh-peer graph floor and successor") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path replica_root = temporary.path() / "replica";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(std::filesystem::create_directory(replica_root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(replica_root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    TreeV2BranchStore store(root);

    auto first = store.publish_local(policy, manifest(left, 1U, 1U), left,
                                     crypto, transaction.value());
    IOTOX_CHECK(first.ok());
    auto second = store.publish_local(policy, manifest(left, 2U, 2U), left,
                                      crypto, transaction.value());
    IOTOX_CHECK(second.ok());
    auto checkpoint = store.checkpoint_local(policy, left, crypto,
                                             transaction.value());
    IOTOX_CHECK_MSG(checkpoint.ok(), checkpoint.status().message());
    IOTOX_CHECK(checkpoint.value().snapshot.head.checkpoint);
    IOTOX_CHECK(checkpoint.value().snapshot.head.generation == 3U);
    IOTOX_CHECK(std::all_of(
        checkpoint.value().snapshot.manifest.entries.begin(),
        checkpoint.value().snapshot.manifest.entries.end(),
        [&checkpoint](const TreeV2Entry &entry) {
            return entry.origin.writer == checkpoint.value().snapshot.head.writer &&
                   entry.origin.generation == 3U;
        }));

    NamespacePolicy replica_policy = policy;
    replica_policy.root = replica_root.string();
    auto replica_transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(replica_policy);
    IOTOX_CHECK(replica_transaction.ok());
    TreeV2BranchStore replica(replica_root);
    auto accepted = replica.accept(replica_policy,
                                   checkpoint.value().snapshot, crypto,
                                   replica_transaction.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    IOTOX_CHECK(accepted.value().decision ==
                TreeV2BranchStoreDecision::accepted_genesis);

    auto successor = store.publish_local(policy, manifest(left, 4U, 4U), left,
                                         crypto, transaction.value());
    IOTOX_CHECK_MSG(successor.ok(), successor.status().message());
    IOTOX_CHECK(!successor.value().snapshot.head.checkpoint);
    IOTOX_CHECK(successor.value().snapshot.head.previous ==
                checkpoint.value().record);
}

IOTOX_TEST("tree-v2 branch store keeps terminal cutoff replay retired") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    TreeV2BranchStore store(root, left.public_key());

    auto left_one = store.publish_local(policy, manifest(left, 1U, 1U), left,
                                        crypto, transaction.value());
    IOTOX_CHECK_MSG(left_one.ok(), left_one.status().message());
    TreeV2Manifest right_tree{{TreeV2Entry{
        "right.txt", TreeV2EntryKind::file,
        TreeV2Version{right.public_key(), 1U}, digest(2U), 1024U, false}}};
    const TreeV2BranchHead right_head =
        branch(policy, right_tree, std::nullopt, right, crypto);
    auto right_one =
        store.accept(policy, TreeV2Snapshot{right_head, right_tree}, crypto,
                     transaction.value());
    IOTOX_CHECK_MSG(right_one.ok(), right_one.status().message());
    IOTOX_CHECK(right_one.value().decision ==
                TreeV2BranchStoreDecision::accepted_genesis);
    auto checkpoint = store.checkpoint_local(policy, left, crypto,
                                             transaction.value());
    IOTOX_CHECK_MSG(checkpoint.ok(), checkpoint.status().message());
    auto cutoff = iotox::sync::cutoff_tree_v2_writer(
        policy, right.public_key(), left, crypto, transaction.value());
    IOTOX_CHECK_MSG(cutoff.ok(), cutoff.status().message());

    auto replay =
        store.accept(policy, TreeV2Snapshot{right_head, right_tree}, crypto,
                     transaction.value());
    IOTOX_CHECK_MSG(replay.ok(), replay.status().message());
    IOTOX_CHECK(replay.value().decision ==
                TreeV2BranchStoreDecision::retired_terminal);
    IOTOX_CHECK(replay.value().record == cutoff.value().record);
    auto frontier = store.load_frontier(policy, crypto, transaction.value());
    IOTOX_CHECK_MSG(frontier.ok(), frontier.status().message());
    IOTOX_CHECK(frontier.value().size() == 1U);
    IOTOX_CHECK(frontier.value().front().head.writer == left.public_key());
    const std::filesystem::path live =
        root / "tree-v2" / "branches" /
        (lower_hex(right.public_key()) + ".branch");
    const std::filesystem::path retired =
        root / "tree-v2" / "retired-branches" /
        (lower_hex(right.public_key()) + ".branch");
    IOTOX_CHECK(!std::filesystem::exists(live));
    IOTOX_CHECK(std::filesystem::exists(retired));
    write_bytes(live, read_bytes(retired));
    IOTOX_CHECK(std::filesystem::exists(live));
    auto repair =
        store.accept(policy, TreeV2Snapshot{right_head, right_tree}, crypto,
                     transaction.value());
    IOTOX_CHECK_MSG(repair.ok(), repair.status().message());
    IOTOX_CHECK(repair.value().decision ==
                TreeV2BranchStoreDecision::retired_terminal);
    IOTOX_CHECK(!std::filesystem::exists(live));
    auto stored = iotox::sync::load_tree_v2_stored_record(
        policy, replay.value().record, crypto, transaction.value());
    IOTOX_CHECK_MSG(stored.ok(), stored.status().message());
    IOTOX_CHECK(stored.value().head == right_head);
}

IOTOX_TEST("tree-v2 checkpoint refuses unresolved conflict") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    TreeV2BranchStore store(root);
    IOTOX_CHECK(store.publish_local(policy, manifest(left, 1U, 1U), left,
                                    crypto, transaction.value()).ok());
    const TreeV2Manifest right_tree = manifest(right, 1U, 2U);
    const TreeV2BranchHead right_head =
        branch(policy, right_tree, std::nullopt, right, crypto);
    IOTOX_CHECK(store.accept(policy, TreeV2Snapshot{right_head, right_tree},
                             crypto, transaction.value()).ok());
    auto refused = store.checkpoint_local(policy, left, crypto,
                                          transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().message().find("unresolved conflicts") !=
                std::string::npos);
}

IOTOX_TEST("tree-v2 manifest bounds one candidate per writer and path") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    const NamespacePolicy policy = policy_for(root, left, right);
    TreeV2Manifest amplified{{
        TreeV2Entry{"field.txt", TreeV2EntryKind::file,
                    TreeV2Version{left.public_key(), 1U}, digest(1U), 1U,
                    false},
        TreeV2Entry{"field.txt", TreeV2EntryKind::file,
                    TreeV2Version{left.public_key(), 2U}, digest(2U), 1U,
                    false},
    }};
    const auto valid = iotox::sync::validate_tree_v2_manifest(policy, amplified);
    IOTOX_CHECK(!valid.ok());
    IOTOX_CHECK(valid.code() == iotox::ErrorCode::resource_exhausted);
}
