#include "test_harness.hpp"

#include "iotox/state_store.hpp"
#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"
#include "iotox/sync_multiwriter_workspace.hpp"

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
using iotox::sync::Digest;
using iotox::sync::Engine;
using iotox::sync::NamespacePolicy;
using iotox::sync::TreeV2BranchHead;
using iotox::sync::TreeV2BranchStore;
using iotox::sync::TreeV2Entry;
using iotox::sync::TreeV2EntryKind;
using iotox::sync::TreeV2MaintenanceStore;
using iotox::sync::TreeV2Manifest;
using iotox::sync::TreeV2Snapshot;
using iotox::sync::TreeV2Version;

class TempDirectory {
  public:
    TempDirectory() {
        std::string pattern = "/tmp/iotox-tree-maintenance-XXXXXX";
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

Digest digest(std::uint8_t value) {
    Digest result{};
    result[0U] = value;
    return result;
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

TreeV2Manifest directory_manifest(const DeviceIdentity &writer,
                                  std::uint64_t generation) {
    return TreeV2Manifest{{TreeV2Entry{
        "notes", TreeV2EntryKind::directory,
        TreeV2Version{writer.public_key(), generation}, {}, 0U, false}}};
}

TreeV2Manifest equivalent_directory_manifest(const DeviceIdentity &writer,
                                             std::uint64_t generation) {
    return directory_manifest(writer, generation);
}

TreeV2BranchHead branch(const NamespacePolicy &policy,
                        const TreeV2Manifest &manifest,
                        const std::optional<TreeV2BranchHead> &previous,
                        const DeviceIdentity &writer, const Sodium &crypto) {
    auto created = iotox::sync::create_tree_v2_branch_head(
        policy, manifest, previous, {}, writer, crypto);
    if (!created) throw std::runtime_error(created.status().message());
    return created.value();
}

void write_file(const std::filesystem::path &path, std::string_view text) {
    std::ofstream output(path, std::ios::binary | std::ios::trunc);
    output.write(text.data(), static_cast<std::streamsize>(text.size()));
    output.close();
    if (!output || ::chmod(path.c_str(), static_cast<mode_t>(0600)) != 0)
        throw std::runtime_error("write file failed");
}

} // namespace

IOTOX_TEST("tree-v2 checkpoint GC quarantines and restores exact ancestors") {
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
    TreeV2BranchStore branches(root);

    auto first = branches.publish_local(policy, directory_manifest(left, 1U),
                                        left, crypto, transaction.value());
    IOTOX_CHECK(first.ok());
    auto second = branches.publish_local(policy, directory_manifest(left, 2U),
                                         left, crypto, transaction.value());
    IOTOX_CHECK(second.ok());
    auto checkpoint = branches.checkpoint_local(policy, left, crypto,
                                                transaction.value());
    IOTOX_CHECK_MSG(checkpoint.ok(), checkpoint.status().message());

    auto plan = iotox::sync::plan_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
    IOTOX_CHECK(plan.value().checkpoint_floors == 1U);
    IOTOX_CHECK(plan.value().reachable.size() == 2U);
    IOTOX_CHECK(plan.value().candidates.size() == 4U);

    auto quarantined = iotox::sync::quarantine_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(quarantined.ok(), quarantined.status.message());
    IOTOX_CHECK(quarantined.moved == 4U);
    IOTOX_CHECK(!std::filesystem::exists(
        iotox::sync::tree_v2_branch_record_path(policy,
                                                first.value().record)));
    IOTOX_CHECK(std::filesystem::exists(
        iotox::sync::tree_v2_branch_record_path(policy,
                                                checkpoint.value().record)));
    auto after = iotox::sync::plan_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(after.ok());
    IOTOX_CHECK(after.value().candidates.empty());

    auto restored = iotox::sync::restore_tree_v2_quarantine(
        policy, crypto, transaction.value());
    IOTOX_CHECK_MSG(restored.ok(), restored.status.message());
    IOTOX_CHECK(restored.restored == 4U);
    IOTOX_CHECK(std::filesystem::exists(
        iotox::sync::tree_v2_branch_record_path(policy,
                                                first.value().record)));
    IOTOX_CHECK(branches.load_frontier(policy, crypto, transaction.value()).ok());
}

IOTOX_TEST("tree-v2 sparse GC roots only selected content custody") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    auto right = identity(temporary.path() / "right.identity", crypto);
    const std::filesystem::path root = temporary.path() / "namespace";
    const std::filesystem::path worktree = temporary.path() / "worktree";
    IOTOX_CHECK(std::filesystem::create_directory(root));
    IOTOX_CHECK(std::filesystem::create_directory(worktree));
    IOTOX_CHECK(::chmod(root.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod(worktree.c_str(), static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(std::filesystem::create_directory(worktree / "keep"));
    IOTOX_CHECK(std::filesystem::create_directory(worktree / "omit"));
    IOTOX_CHECK(::chmod((worktree / "keep").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    IOTOX_CHECK(::chmod((worktree / "omit").c_str(),
                        static_cast<mode_t>(0700)) == 0);
    write_file(worktree / "keep" / "a.txt", "selected");
    write_file(worktree / "omit" / "b.txt", "not selected");

    const NamespacePolicy complete = policy_for(root, left, right);
    auto transaction =
        iotox::sync::SyncNamespaceTransaction::acquire(complete);
    IOTOX_CHECK(transaction.ok());
    auto scan = iotox::sync::scan_tree_v2_worktree(
        complete, worktree, std::nullopt, left.public_key(), 1U);
    IOTOX_CHECK_MSG(scan.ok(), scan.status().message());
    auto objects = iotox::sync::store_tree_v2_scan_objects(
        complete, scan.value(), transaction.value());
    IOTOX_CHECK_MSG(objects.ok(), objects.status().message());
    TreeV2BranchStore branches(root);
    auto published = branches.publish_local(
        complete, scan.value().manifest, left, crypto, transaction.value());
    IOTOX_CHECK_MSG(published.ok(), published.status().message());

    NamespacePolicy sparse = complete;
    sparse.projection.includes = {"keep"};
    IOTOX_CHECK(iotox::sync::validate_namespace_policy(sparse).ok());
    auto plan = iotox::sync::plan_tree_v2_gc(
        sparse, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
    IOTOX_CHECK(!plan.value().custody_complete);
    IOTOX_CHECK(plan.value().manifest_file_objects == 2U);
    IOTOX_CHECK(plan.value().selected_file_objects == 1U);
    IOTOX_CHECK(plan.value().skipped_file_objects == 1U);
    IOTOX_CHECK(plan.value().candidates.size() == 1U);
    IOTOX_CHECK(plan.value().candidates.front().kind ==
                iotox::sync::TreeV2ObjectKind::file);

    auto quarantined = iotox::sync::quarantine_tree_v2_gc(
        sparse, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(quarantined.ok(), quarantined.status.message());
    IOTOX_CHECK(quarantined.moved == 1U);
    auto widened = iotox::sync::plan_tree_v2_gc(
        complete, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(!widened.ok());
    auto restored = iotox::sync::restore_tree_v2_quarantine(
        complete, crypto, transaction.value());
    IOTOX_CHECK_MSG(restored.ok(), restored.status.message());
    IOTOX_CHECK(restored.restored == 1U);
    IOTOX_CHECK(iotox::sync::plan_tree_v2_gc(
                    complete, left.public_key(), crypto, transaction.value())
                    .ok());
}

IOTOX_TEST("tree-v2 retention pin roots closure until explicit unpin") {
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
    TreeV2BranchStore branches(root);
    auto first = branches.publish_local(policy, directory_manifest(left, 1U),
                                        left, crypto, transaction.value());
    IOTOX_CHECK(first.ok());
    auto second = branches.publish_local(policy, directory_manifest(left, 2U),
                                         left, crypto, transaction.value());
    IOTOX_CHECK(second.ok());
    TreeV2MaintenanceStore maintenance(root);
    auto pinned = maintenance.pin(policy, second.value().record, left, crypto,
                                  transaction.value());
    IOTOX_CHECK_MSG(pinned.ok(), pinned.status().message());
    IOTOX_CHECK(branches.checkpoint_local(policy, left, crypto,
                                         transaction.value()).ok());
    auto retained = iotox::sync::plan_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(retained.ok());
    IOTOX_CHECK(retained.value().pinned_roots == 1U);
    IOTOX_CHECK(retained.value().candidates.empty());
    auto unpinned = maintenance.unpin(policy, second.value().record, left,
                                      crypto, transaction.value());
    IOTOX_CHECK(unpinned.ok());
    auto reclaimable = iotox::sync::plan_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(reclaimable.ok());
    IOTOX_CHECK(reclaimable.value().candidates.size() == 4U);
}

IOTOX_TEST(
    "tree-v2 maintenance store detects signed state corruption without mutation") {
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
    TreeV2BranchStore branches(root);
    auto published = branches.publish_local(
        policy, directory_manifest(left, 1U), left, crypto,
        transaction.value());
    IOTOX_CHECK_MSG(published.ok(), published.status().message());
    TreeV2MaintenanceStore maintenance(root);
    auto pinned = maintenance.pin(policy, published.value().record, left,
                                  crypto, transaction.value());
    IOTOX_CHECK_MSG(pinned.ok(), pinned.status().message());

    const std::filesystem::path record =
        root / "tree-v2" / "maintenance.state";
    auto original = iotox::StateStore::read(record);
    IOTOX_CHECK_MSG(original.ok(), original.status().message());
    IOTOX_CHECK(!original.value().empty());
    std::vector<std::uint8_t> corrupt = original.value();
    corrupt.back() ^= 0x01U;
    IOTOX_CHECK(iotox::StateStore::write_atomic(record, corrupt).ok());

    auto refused =
        maintenance.load(policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(!refused.ok());
    IOTOX_CHECK(refused.status().code() == iotox::ErrorCode::protocol_error);
    IOTOX_CHECK_MSG(
        refused.status().message().find("maintenance state") !=
            std::string::npos,
        refused.status().message());
    auto retained = iotox::StateStore::read(record);
    IOTOX_CHECK(retained.ok());
    IOTOX_CHECK(retained.value() == corrupt);
    auto overwrite = maintenance.pin(policy, published.value().record, left,
                                     crypto, transaction.value());
    IOTOX_CHECK(!overwrite.ok());
    retained = iotox::StateStore::read(record);
    IOTOX_CHECK(retained.ok());
    IOTOX_CHECK(retained.value() == corrupt);

    IOTOX_CHECK(
        iotox::StateStore::write_atomic(record, original.value()).ok());
    auto restored =
        maintenance.load(policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(restored.ok(), restored.status().message());
    IOTOX_CHECK(restored.value().mutation == pinned.value().mutation);
    IOTOX_CHECK(restored.value().pins == pinned.value().pins);
}

IOTOX_TEST("tree-v2 GC roots a derived manifest from the signed workspace") {
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
    TreeV2BranchStore branches(root);
    auto published = branches.publish_local(
        policy, directory_manifest(left, 1U), left, crypto,
        transaction.value());
    IOTOX_CHECK(published.ok());

    // This is a durable merge projection, not a branch authored just to
    // acknowledge receipt of another writer.
    const TreeV2Manifest derived = directory_manifest(right, 2U);
    auto retained = branches.retain_manifest(policy, derived, crypto,
                                             transaction.value());
    IOTOX_CHECK(retained.ok());
    const std::filesystem::path worktree = temporary.path() / "worktree";
    IOTOX_CHECK(std::filesystem::create_directory(worktree));
    IOTOX_CHECK(::chmod(worktree.c_str(), static_cast<mode_t>(0700)) == 0);
    iotox::sync::TreeV2WorkspaceStore workspace(root);
    std::vector<iotox::sync::TreeV2Observation> visible{
        {published.value().snapshot.head.writer,
         published.value().snapshot.head.generation,
         published.value().record}};
    auto initialized = workspace.initialize(
        policy, worktree, retained.value(), visible, left, crypto);
    IOTOX_CHECK_MSG(initialized.ok(), initialized.status().message());

    auto plan = iotox::sync::plan_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK_MSG(plan.ok(), plan.status().message());
    IOTOX_CHECK(std::none_of(
        plan.value().candidates.begin(), plan.value().candidates.end(),
        [&retained](const iotox::sync::TreeV2GcObject &object) {
            return object.kind == iotox::sync::TreeV2ObjectKind::manifest &&
                   object.digest == retained.value();
        }));
    IOTOX_CHECK(iotox::sync::load_tree_v2_stored_manifest(
                    policy, retained.value(), crypto, transaction.value())
                    .ok());
}

IOTOX_TEST("tree-v2 restore refuses tampered quarantine bytes") {
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
    TreeV2BranchStore branches(root);
    IOTOX_CHECK(branches.publish_local(policy, directory_manifest(left, 1U),
                                       left, crypto, transaction.value()).ok());
    IOTOX_CHECK(branches.publish_local(policy, directory_manifest(left, 2U),
                                       left, crypto, transaction.value()).ok());
    IOTOX_CHECK(branches.checkpoint_local(policy, left, crypto,
                                         transaction.value()).ok());
    auto quarantined = iotox::sync::quarantine_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(quarantined.ok());
    const std::filesystem::path records =
        root / "tree-v2" / "gc-quarantine" / "records";
    const auto entry = *std::filesystem::directory_iterator(records);
    auto bytes = iotox::StateStore::read(entry.path());
    IOTOX_CHECK(bytes.ok() && !bytes.value().empty());
    bytes.value().front() ^= 0x01U;
    IOTOX_CHECK(iotox::StateStore::write_atomic(entry.path(), bytes.value()).ok());
    const std::filesystem::path live =
        root / "tree-v2" / "records" /
        (entry.path().filename().string() + ".branch");
    IOTOX_CHECK(!std::filesystem::exists(live));
    auto restored = iotox::sync::restore_tree_v2_quarantine(
        policy, crypto, transaction.value());
    IOTOX_CHECK(!restored.ok());
    IOTOX_CHECK(!std::filesystem::exists(live));
    IOTOX_CHECK(std::filesystem::exists(entry.path()));
}

IOTOX_TEST("tree-v2 GC inventory rejects symlink-shaped objects") {
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
    TreeV2BranchStore branches(root);
    IOTOX_CHECK(branches.publish_local(policy, directory_manifest(left, 1U),
                                       left, crypto, transaction.value()).ok());
    const std::filesystem::path objects = root / "tree-v2" / "objects";
    IOTOX_CHECK(std::filesystem::create_directory(objects));
    IOTOX_CHECK(::chmod(objects.c_str(), static_cast<mode_t>(0700)) == 0);
    const std::filesystem::path injected =
        objects / "ee";
    std::filesystem::create_directory_symlink(root, injected);
    IOTOX_CHECK(std::filesystem::is_symlink(injected));
    auto planned = iotox::sync::plan_tree_v2_gc(
        policy, left.public_key(), crypto, transaction.value());
    IOTOX_CHECK(!planned.ok());
    IOTOX_CHECK(planned.status().message().find("symlink") !=
                std::string::npos);
}

IOTOX_TEST("tree-v2 terminal cutoff retires exact observed writer") {
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
    TreeV2BranchStore branches(root);
    IOTOX_CHECK(branches.publish_local(policy, directory_manifest(left, 1U),
                                       left, crypto, transaction.value()).ok());
    const TreeV2Manifest right_one_manifest =
        equivalent_directory_manifest(right, 1U);
    const TreeV2BranchHead right_one = branch(
        policy, right_one_manifest, std::nullopt, right, crypto);
    auto accepted = branches.accept(
        policy, TreeV2Snapshot{right_one, right_one_manifest}, crypto,
        transaction.value());
    IOTOX_CHECK(accepted.ok());
    auto checkpoint = branches.checkpoint_local(policy, left, crypto,
                                                transaction.value());
    IOTOX_CHECK_MSG(checkpoint.ok(), checkpoint.status().message());

    // Force the exact crash window after signed cutoff commit but before the
    // current branch pointer can be retired. An exact retry must finish it.
    const std::filesystem::path retired =
        root / "tree-v2" / "retired-branches";
    IOTOX_CHECK(std::filesystem::create_directory(retired));
    IOTOX_CHECK(::chmod(retired.c_str(), static_cast<mode_t>(0700)) == 0);
    const std::filesystem::path obstruction =
        retired / (lower_hex(right.public_key()) + ".branch");
    IOTOX_CHECK(iotox::StateStore::write_atomic(
                    obstruction, std::vector<std::uint8_t>{1U})
                    .ok());
    auto interrupted = iotox::sync::cutoff_tree_v2_writer(
        policy, right.public_key(), left, crypto, transaction.value());
    IOTOX_CHECK(!interrupted.ok());
    IOTOX_CHECK(std::filesystem::remove(obstruction));
    auto cutoff = iotox::sync::cutoff_tree_v2_writer(
        policy, right.public_key(), left, crypto, transaction.value());
    IOTOX_CHECK_MSG(cutoff.ok(), cutoff.status().message());
    IOTOX_CHECK(cutoff.value().record == accepted.value().record);
    auto duplicate = iotox::sync::cutoff_tree_v2_writer(
        policy, right.public_key(), left, crypto, transaction.value());
    IOTOX_CHECK_MSG(duplicate.ok(), duplicate.status().message());
    IOTOX_CHECK(duplicate.value() == cutoff.value());
    auto frontier = branches.load_frontier(policy, crypto, transaction.value());
    IOTOX_CHECK(frontier.ok());
    IOTOX_CHECK(frontier.value().size() == 1U);

    const TreeV2Manifest right_two_manifest =
        equivalent_directory_manifest(right, 2U);
    const TreeV2BranchHead right_two = branch(
        policy, right_two_manifest, right_one, right, crypto);
    auto right_two_record = iotox::sync::tree_v2_branch_record_digest(
        policy, right_two, crypto);
    IOTOX_CHECK(right_two_record.ok());
    const auto admission = iotox::sync::admit_tree_v2_writer_record(
        policy, right_two, right_two_record.value(), left.public_key(), crypto,
        transaction.value());
    IOTOX_CHECK(!admission.ok());
    IOTOX_CHECK(admission.message().find("terminal writer cutoff") !=
                std::string::npos);
}

IOTOX_TEST("tree-v2 maintenance codec is canonical signed and bounded") {
    TempDirectory temporary;
    auto crypto = sodium();
    auto left = identity(temporary.path() / "left.identity", crypto);
    iotox::sync::TreeV2MaintenanceState state;
    state.namespace_id = "field-notes";
    state.mutation = 1U;
    state.signer = left.public_key();
    state.pins = {digest(1U)};
    auto body = iotox::sync::encode_tree_v2_maintenance_state(state);
    IOTOX_CHECK(body.ok());
    auto decoded = iotox::sync::decode_tree_v2_maintenance_state(
        body.value(), 1U, 1U);
    IOTOX_CHECK(decoded.ok());
    std::vector<std::uint8_t> tampered = body.value();
    tampered[14U] = 1U;
    IOTOX_CHECK(!iotox::sync::decode_tree_v2_maintenance_state(
                     tampered, 1U, 1U).ok());
}
