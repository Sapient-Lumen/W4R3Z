#include "test_harness.hpp"

#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_time_machine.hpp"

#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <sstream>
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
using iotox::sync::TreeV2BranchStore;
using iotox::sync::TreeV2Snapshot;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-sync-time-machine-XXXXXX";
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

void make_private_directory(const std::filesystem::path &path) {
    if (!std::filesystem::create_directory(path) ||
        ::chmod(path.c_str(), static_cast<mode_t>(0700)) != 0)
        throw std::runtime_error("private directory creation failed");
}

void write_file(const std::filesystem::path &path, std::string_view contents) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(contents.data(), static_cast<std::streamsize>(contents.size()));
    output.close();
    if (!output || ::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
        throw std::runtime_error("file write failed");
}

std::string read_file(const std::filesystem::path &path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("file read open failed");
    std::ostringstream output;
    output << input.rdbuf();
    if (!input.eof() && input.fail())
        throw std::runtime_error("file read failed");
    return output.str();
}

std::string numbered_path(std::size_t index) {
    std::string number = std::to_string(index);
    if (number.size() < 3U) number.insert(0U, 3U - number.size(), '0');
    return "file-" + number + ".txt";
}

NamespacePolicy policy_for(const std::filesystem::path &root,
                           const DeviceIdentity &device) {
    NamespacePolicy policy;
    policy.id = "field-notes";
    policy.root = root.string();
    policy.engine = Engine::tree_v2;
    policy.writers = {device.public_key()};
    return policy;
}

std::pair<TreeV2Snapshot, Digest>
current_local(const NamespacePolicy &policy, const DeviceIdentity &device,
              const Sodium &crypto,
              const iotox::sync::SyncNamespaceTransaction &transaction) {
    TreeV2BranchStore store{policy.root};
    auto frontier = store.load_frontier(policy, crypto, transaction);
    if (!frontier || frontier.value().size() != 1U)
        throw std::runtime_error("local frontier load failed");
    auto record = iotox::sync::tree_v2_branch_record_digest(
        policy, frontier.value().front().head, crypto);
    if (!record) throw std::runtime_error("record digest failed");
    IOTOX_CHECK(frontier.value().front().head.writer == device.public_key());
    return {frontier.value().front(), record.value()};
}

} // namespace

IOTOX_TEST("tree-v2 time machine inventories diffs and restores only forward") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_private_directory(root);
    make_private_directory(worktree);
    const NamespacePolicy policy = policy_for(root, device);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());

    write_file(worktree / "note.txt", "alpha");
    auto first_reconcile = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, device, crypto, transaction.value());
    IOTOX_CHECK_MSG(first_reconcile.ok(), first_reconcile.status().message());
    const auto [first, first_record] =
        current_local(policy, device, crypto, transaction.value());
    IOTOX_CHECK(first.head.generation == 1U);

    write_file(worktree / "note.txt", "bravo");
    auto second_reconcile = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, device, crypto, transaction.value());
    IOTOX_CHECK_MSG(second_reconcile.ok(), second_reconcile.status().message());
    const auto [second, second_record] =
        current_local(policy, device, crypto, transaction.value());
    IOTOX_CHECK(second.head.generation == 2U);
    IOTOX_CHECK(second.head.previous == first_record);

    iotox::sync::TreeV2MaintenanceStore maintenance(root);
    auto pinned = maintenance.pin(policy, first_record, device, crypto,
                                  transaction.value());
    IOTOX_CHECK_MSG(pinned.ok(), pinned.status().message());
    auto history = iotox::sync::list_tree_v2_history(
        policy, device.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(history.ok(), history.status().message());
    IOTOX_CHECK(history.value().size() == 2U);
    IOTOX_CHECK(history.value()[0U].generation == 2U);
    IOTOX_CHECK(history.value()[0U].current);
    IOTOX_CHECK(history.value()[1U].generation == 1U);
    IOTOX_CHECK(history.value()[1U].pinned);

    auto diff = iotox::sync::diff_tree_v2_records(
        policy, first_record, second_record, crypto, transaction.value());
    IOTOX_CHECK_MSG(diff.ok(), diff.status().message());
    IOTOX_CHECK(diff.value().entries.size() == 1U);
    IOTOX_CHECK(diff.value().modified == 1U);
    IOTOX_CHECK(diff.value().projected_content_changes == 1U);
    IOTOX_CHECK(diff.value().entries[0U].path == "note.txt");
    IOTOX_CHECK(iotox::sync::tree_v2_diff_kind_name(
                    diff.value().entries[0U].kind) == "modified");
    auto conflicts = iotox::sync::tree_v2_conflicts(
        policy, std::nullopt, crypto, transaction.value());
    IOTOX_CHECK(conflicts.ok());
    IOTOX_CHECK(conflicts.value().empty());

    auto plan = iotox::sync::plan_tree_v2_restore_forward(
        policy, first_record, worktree, device, crypto, transaction.value());
    IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
    IOTOX_CHECK(plan.value().ready);
    IOTOX_CHECK(plan.value().target_pinned);
    IOTOX_CHECK(plan.value().workspace_current);
    IOTOX_CHECK(plan.value().worktree_clean);
    IOTOX_CHECK(plan.value().next_local_generation == 3U);
    IOTOX_CHECK(plan.value().changed_paths == 1U);
    IOTOX_CHECK(plan.value().required_objects == 1U);
    IOTOX_CHECK(plan.value().missing_objects == 0U);

    write_file(worktree / "note.txt", "unpublished");
    auto dirty = iotox::sync::plan_tree_v2_restore_forward(
        policy, first_record, worktree, device, crypto, transaction.value());
    IOTOX_CHECK(dirty.ok());
    IOTOX_CHECK(!dirty.value().ready);
    IOTOX_CHECK(!dirty.value().worktree_clean);
    auto stale = iotox::sync::restore_tree_v2_forward(
        policy, first_record, plan.value().id, worktree, device, crypto,
        transaction.value());
    IOTOX_CHECK(!stale.ok());
    IOTOX_CHECK(current_local(policy, device, crypto, transaction.value())
                    .first.head.generation == 2U);

    write_file(worktree / "note.txt", "bravo");
    plan = iotox::sync::plan_tree_v2_restore_forward(
        policy, first_record, worktree, device, crypto, transaction.value());
    IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
    IOTOX_CHECK(plan.value().ready);
    auto restored = iotox::sync::restore_tree_v2_forward(
        policy, first_record, plan.value().id, worktree, device, crypto,
        transaction.value());
    IOTOX_CHECK_MSG(restored.ok(), restored.status().message());
    IOTOX_CHECK(restored.value().publication.snapshot.head.generation == 3U);
    IOTOX_CHECK(restored.value().publication.snapshot.head.previous ==
                second_record);
    IOTOX_CHECK(restored.value().publication.record != first_record);
    IOTOX_CHECK(restored.value().publication.record != second_record);
    IOTOX_CHECK(read_file(worktree / "note.txt") == "alpha");
    const auto [third, third_record] =
        current_local(policy, device, crypto, transaction.value());
    IOTOX_CHECK(third.head.generation == 3U);
    IOTOX_CHECK(third_record == restored.value().publication.record);

    auto reused_plan = iotox::sync::restore_tree_v2_forward(
        policy, first_record, plan.value().id, worktree, device, crypto,
        transaction.value());
    IOTOX_CHECK(!reused_plan.ok());
    IOTOX_CHECK(current_local(policy, device, crypto, transaction.value())
                    .first.head.generation == 3U);
}

IOTOX_TEST("tree-v2 time machine diffs grouped paths") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_private_directory(root);
    make_private_directory(worktree);
    const NamespacePolicy policy = policy_for(root, device);
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK_MSG(transaction.ok(), transaction.status().message());

    constexpr std::size_t file_count = 128U;
    for (std::size_t index = 0U; index < file_count; ++index) {
        write_file(worktree / numbered_path(index),
                   "base-" + std::to_string(index));
    }
    auto first_reconcile = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, device, crypto, transaction.value());
    IOTOX_CHECK_MSG(first_reconcile.ok(), first_reconcile.status().message());
    const auto [first, first_record] =
        current_local(policy, device, crypto, transaction.value());

    write_file(worktree / numbered_path(42U), "changed");
    IOTOX_CHECK(std::filesystem::remove(worktree / numbered_path(43U)));
    write_file(worktree / "new-file.txt", "new");
    auto second_reconcile = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, device, crypto, transaction.value());
    IOTOX_CHECK_MSG(second_reconcile.ok(), second_reconcile.status().message());
    const auto [second, second_record] =
        current_local(policy, device, crypto, transaction.value());
    IOTOX_CHECK(second.head.generation == first.head.generation + 1U);

    auto diff = iotox::sync::diff_tree_v2_records(
        policy, first_record, second_record, crypto, transaction.value());
    IOTOX_CHECK_MSG(diff.ok(), diff.status().message());
    IOTOX_CHECK(diff.value().entries.size() == 3U);
    IOTOX_CHECK(diff.value().added == 1U);
    IOTOX_CHECK(diff.value().removed == 0U);
    IOTOX_CHECK(diff.value().modified == 2U);
    IOTOX_CHECK(diff.value().projected_content_changes == 3U);
}

IOTOX_TEST("tree-v2 restore plan reports missing retained file objects") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto device = identity(temporary.path() / "device.identity", crypto);
    auto foreign = identity(temporary.path() / "foreign.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    make_private_directory(root);
    make_private_directory(worktree);
    NamespacePolicy policy = policy_for(root, device);
    policy.writers.push_back(foreign.public_key());
    std::sort(policy.writers.begin(), policy.writers.end());
    auto transaction = iotox::sync::SyncNamespaceTransaction::acquire(policy);
    IOTOX_CHECK(transaction.ok());
    write_file(worktree / "note.txt", "retained bytes");
    auto reconciled = iotox::sync::reconcile_tree_v2_workspace(
        policy, worktree, device, crypto, transaction.value());
    IOTOX_CHECK(reconciled.ok());
    const auto [snapshot, record] =
        current_local(policy, device, crypto, transaction.value());
    IOTOX_CHECK(snapshot.manifest.entries.size() == 1U);
    const std::filesystem::path object = iotox::sync::tree_v2_object_path(
        policy, snapshot.manifest.entries.front().content);
    const std::filesystem::path held = object.parent_path() / "held-object";
    std::filesystem::rename(object, held);
    auto plan = iotox::sync::plan_tree_v2_restore_forward(
        policy, record, worktree, device, crypto, transaction.value());
    IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
    IOTOX_CHECK(plan.value().missing_objects == 1U);
    IOTOX_CHECK(plan.value().missing_bytes == 14U);
    IOTOX_CHECK(!plan.value().ready);
    std::filesystem::rename(held, object);

    TreeV2BranchStore store(root);
    iotox::sync::TreeV2Entry concurrent = snapshot.manifest.entries.front();
    concurrent.origin = {foreign.public_key(), 1U};
    iotox::sync::TreeV2Manifest foreign_manifest{{concurrent}};
    auto foreign_head = iotox::sync::create_tree_v2_branch_head(
        policy, foreign_manifest, std::nullopt, {}, foreign, crypto);
    IOTOX_CHECK_MSG(foreign_head.ok(), foreign_head.status().message());
    auto foreign_accepted = store.accept(
        policy, TreeV2Snapshot{foreign_head.value(), foreign_manifest}, crypto,
        transaction.value());
    IOTOX_CHECK_MSG(foreign_accepted.ok(),
                    foreign_accepted.status().message());
    iotox::sync::TreeV2Manifest conflicted = snapshot.manifest;
    conflicted.entries.push_back(concurrent);
    std::sort(conflicted.entries.begin(), conflicted.entries.end(),
              [](const auto &left, const auto &right) {
                  if (left.path != right.path) return left.path < right.path;
                  if (left.origin.writer != right.origin.writer)
                      return left.origin.writer < right.origin.writer;
                  return left.origin.generation < right.origin.generation;
              });
    const std::vector<iotox::sync::TreeV2Observation> observations{
        {foreign.public_key(), 1U, foreign_accepted.value().record}};
    auto conflicted_head = iotox::sync::create_tree_v2_branch_head(
        policy, conflicted, snapshot.head, observations, device, crypto);
    IOTOX_CHECK_MSG(conflicted_head.ok(),
                    conflicted_head.status().message());
    auto accepted = store.accept(
        policy, TreeV2Snapshot{conflicted_head.value(), conflicted}, crypto,
        transaction.value());
    IOTOX_CHECK_MSG(accepted.ok(), accepted.status().message());
    auto conflicted_plan = iotox::sync::plan_tree_v2_restore_forward(
        policy, accepted.value().record, worktree, device, crypto,
        transaction.value());
    IOTOX_CHECK_MSG(conflicted_plan.ok(),
                    conflicted_plan.status().message());
    IOTOX_CHECK(conflicted_plan.value().target_conflicts == 1U);
    IOTOX_CHECK(!conflicted_plan.value().ready);
}
