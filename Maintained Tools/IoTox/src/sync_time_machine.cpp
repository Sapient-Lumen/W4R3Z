#include "iotox/sync_time_machine.hpp"

#include "iotox/sync_tree_v2_witness.hpp"

#include "iotox/sync_multiwriter_maintenance.hpp"
#include "iotox/sync_multiwriter_store.hpp"
#include "iotox/sync_multiwriter_workspace.hpp"
#include "iotox/sync_multiwriter_worktree.hpp"

#include <algorithm>
#include <cerrno>
#include <functional>
#include <limits>
#include <map>
#include <set>
#include <span>
#include <string>
#include <sys/stat.h>

namespace iotox::sync {
namespace {

constexpr std::string_view kRestorePlanDomain =
    "iotox-sync-tree-v2-restore-plan-v1";

void append_u64(std::vector<std::uint8_t> &output, std::uint64_t value) {
    for (std::size_t index = 0U; index < 8U; ++index)
        output.push_back(
            static_cast<std::uint8_t>(value >> ((7U - index) * 8U)));
}

template <typename Container>
void append_bytes(std::vector<std::uint8_t> &output,
                  const Container &bytes) {
    output.insert(output.end(), bytes.begin(), bytes.end());
}

using TreeV2PathIndex =
    std::map<std::string, std::vector<TreeV2Entry>, std::less<>>;

[[nodiscard]] TreeV2PathIndex
index_tree_v2_manifest_paths(const TreeV2Manifest &manifest,
                             std::set<std::string> *paths = nullptr) {
    TreeV2PathIndex result;
    for (auto first = manifest.entries.begin();
         first != manifest.entries.end();) {
        auto last = first;
        while (last != manifest.entries.end() && last->path == first->path)
            ++last;
        auto &group = result[first->path];
        group.insert(group.end(), first, last);
        if (paths != nullptr) paths->insert(first->path);
        first = last;
    }
    return result;
}

[[nodiscard]] bool same_projected_payload(const TreeV2Entry &left,
                                          const TreeV2Entry &right) noexcept {
    if (left.kind == TreeV2EntryKind::tombstone &&
        right.kind == TreeV2EntryKind::tombstone)
        return true;
    return left.kind == right.kind && left.content == right.content &&
           left.content_bytes == right.content_bytes &&
           left.executable == right.executable &&
           left.owner_mode == right.owner_mode;
}

[[nodiscard]] Result<bool>
projected_changed(std::span<const TreeV2Entry> from,
                  std::span<const TreeV2Entry> to) {
    const bool from_absent = from.empty();
    const bool to_absent = to.empty();
    if (from_absent || to_absent) {
        if (from_absent && to_absent) return false;
        const auto &present = from_absent ? to : from;
        auto selected = select_tree_v2_projection_entry(present);
        if (!selected) return selected.status();
        return selected.value().kind != TreeV2EntryKind::tombstone;
    }
    auto from_selected = select_tree_v2_projection_entry(from);
    auto to_selected = select_tree_v2_projection_entry(to);
    if (!from_selected) return from_selected.status();
    if (!to_selected) return to_selected.status();
    return !same_projected_payload(from_selected.value(), to_selected.value());
}

[[nodiscard]] Result<TreeV2Diff>
diff_manifests(const NamespacePolicy &policy, const Digest &from_record,
               const Digest &to_record, const Digest &from_manifest,
               const Digest &to_manifest, const TreeV2Manifest &from,
               const TreeV2Manifest &to) {
    const Status from_valid = validate_tree_v2_manifest(policy, from);
    if (!from_valid.ok()) return from_valid;
    const Status to_valid = validate_tree_v2_manifest(policy, to);
    if (!to_valid.ok()) return to_valid;
    TreeV2Diff result;
    result.from_record = from_record;
    result.to_record = to_record;
    result.from_manifest = from_manifest;
    result.to_manifest = to_manifest;
    auto from_summary = summarize_tree_v2_manifest(policy, from);
    auto to_summary = summarize_tree_v2_manifest(policy, to);
    if (!from_summary) return from_summary.status();
    if (!to_summary) return to_summary.status();
    result.from_conflicts = from_summary.value().conflicts.size();
    result.to_conflicts = to_summary.value().conflicts.size();

    std::set<std::string> paths;
    const TreeV2PathIndex from_index =
        index_tree_v2_manifest_paths(from, &paths);
    const TreeV2PathIndex to_index =
        index_tree_v2_manifest_paths(to, &paths);
    const std::vector<TreeV2Entry> empty_entries;
    result.entries.reserve(paths.size());
    for (const std::string &path : paths) {
        const auto before_iterator = from_index.find(path);
        const auto after_iterator = to_index.find(path);
        const std::vector<TreeV2Entry> &before =
            before_iterator == from_index.end() ? empty_entries
                                                : before_iterator->second;
        const std::vector<TreeV2Entry> &after =
            after_iterator == to_index.end() ? empty_entries
                                             : after_iterator->second;
        if (before == after) continue;
        TreeV2DiffEntry entry;
        entry.path = path;
        entry.from_candidates = before.size();
        entry.to_candidates = after.size();
        if (before.empty()) {
            entry.kind = TreeV2DiffKind::added;
            ++result.added;
        } else if (after.empty()) {
            entry.kind = TreeV2DiffKind::removed;
            ++result.removed;
        } else {
            entry.kind = TreeV2DiffKind::modified;
            ++result.modified;
        }
        auto visible = projected_changed(before, after);
        if (!visible) return visible.status();
        entry.projected_content_changed = visible.value();
        if (entry.projected_content_changed)
            ++result.projected_content_changes;
        result.entries.push_back(std::move(entry));
    }
    return result;
}

[[nodiscard]] Result<std::vector<TreeV2Observation>>
frontier_observations(const NamespacePolicy &policy,
                      std::span<const TreeV2Snapshot> frontier,
                      const security::Sodium &sodium) {
    std::vector<TreeV2Observation> result;
    result.reserve(frontier.size());
    for (const TreeV2Snapshot &snapshot : frontier) {
        auto record =
            tree_v2_branch_record_digest(policy, snapshot.head, sodium);
        if (!record) return record.status();
        result.push_back(TreeV2Observation{snapshot.head.writer,
                                           snapshot.head.generation,
                                           record.value()});
    }
    std::sort(result.begin(), result.end(),
              [](const TreeV2Observation &left,
                 const TreeV2Observation &right) {
                  return left.writer < right.writer;
              });
    return result;
}

[[nodiscard]] Result<std::uint64_t>
next_generation(std::span<const TreeV2Snapshot> frontier,
                const PrincipalId &writer) {
    const auto current = std::find_if(
        frontier.begin(), frontier.end(), [&writer](const auto &snapshot) {
            return snapshot.head.writer == writer;
        });
    if (current == frontier.end()) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 restore requires a current local branch"};
    }
    if (current->head.generation == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 local branch generation is exhausted"};
    }
    return current->head.generation + 1U;
}

[[nodiscard]] Result<Digest>
parse_record_name(std::string_view name) {
    constexpr std::string_view suffix = ".branch";
    if (!name.ends_with(suffix)) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 history contains an unexpected entry"};
    }
    name.remove_suffix(suffix.size());
    if (std::any_of(name.begin(), name.end(), [](char value) {
            return value >= 'A' && value <= 'F';
        })) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 history record name is not canonical"};
    }
    auto decoded = security::decode_hex_exact(name, Digest{}.size(),
                                               "tree-v2 history record");
    if (!decoded)
        return Status{ErrorCode::protocol_error,
                      "tree-v2 history record name is not canonical"};
    Digest result{};
    std::copy(decoded.value().begin(), decoded.value().end(), result.begin());
    return result;
}

[[nodiscard]] Result<TreeV2Manifest>
authored_restore_manifest(const NamespacePolicy &policy,
                          const TreeV2Manifest &current,
                          const TreeV2Manifest &target,
                          const PrincipalId &writer,
                          std::uint64_t generation) {
    auto target_summary = summarize_tree_v2_manifest(policy, target);
    if (!target_summary) return target_summary.status();
    if (!target_summary.value().conflicts.empty()) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 restore target has unresolved conflicts"};
    }
    std::map<std::string, TreeV2Entry> authored;
    for (const TreeV2Entry &entry : target.entries) {
        TreeV2Entry next = entry;
        next.origin = TreeV2Version{writer, generation};
        authored.emplace(next.path, std::move(next));
    }
    for (const TreeV2Entry &entry : current.entries) {
        if (authored.contains(entry.path)) continue;
        authored.emplace(entry.path,
                         TreeV2Entry{entry.path,
                                     TreeV2EntryKind::tombstone,
                                     TreeV2Version{writer, generation},
                                     {},
                                     0U,
                                     false,
                                     0U});
    }
    if (authored.size() > policy.quotas.maximum_objects) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 restore revision exceeds the object quota"};
    }
    TreeV2Manifest result;
    result.entries.reserve(authored.size());
    for (auto &[path, entry] : authored) {
        static_cast<void>(path);
        result.entries.push_back(std::move(entry));
    }
    const Status valid = validate_tree_v2_manifest(policy, result);
    if (!valid.ok()) return valid;
    return result;
}

} // namespace

std::string_view tree_v2_diff_kind_name(TreeV2DiffKind kind) noexcept {
    switch (kind) {
    case TreeV2DiffKind::added:
        return "added";
    case TreeV2DiffKind::removed:
        return "removed";
    case TreeV2DiffKind::modified:
        return "modified";
    }
    return "unknown";
}

Result<std::vector<TreeV2Revision>> list_tree_v2_history(
    const NamespacePolicy &policy,
    const security::SigningPublicKey &expected_device,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
    TreeV2BranchStore store{std::filesystem::path(policy.root)};
    const Status prepared = store.prepare(policy, transaction);
    if (!prepared.ok()) return prepared;
    auto frontier = store.load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    std::set<Digest> current;
    for (const TreeV2Snapshot &snapshot : frontier.value()) {
        auto record = tree_v2_branch_record_digest(policy, snapshot.head, sodium);
        if (!record) return record.status();
        current.insert(record.value());
    }
    TreeV2MaintenanceStore maintenance{std::filesystem::path(policy.root)};
    auto state = maintenance.load(policy, expected_device, sodium, transaction);
    if (!state) return state.status();
    const std::set<Digest> pinned(state.value().pins.begin(),
                                  state.value().pins.end());

    std::vector<TreeV2Revision> result;
    try {
        const std::filesystem::path records =
            std::filesystem::path(policy.root) / "tree-v2" / "records";
        for (const auto &entry : std::filesystem::directory_iterator(records)) {
            if (result.size() >= policy.quotas.maximum_objects) {
                return Status{ErrorCode::resource_exhausted,
                              "tree-v2 history exceeds the object quota"};
            }
            auto record = parse_record_name(entry.path().filename().string());
            if (!record) return record.status();
            auto snapshot = load_tree_v2_stored_record(
                policy, record.value(), sodium, transaction);
            if (!snapshot) return snapshot.status();
            auto summary =
                summarize_tree_v2_manifest(policy, snapshot.value().manifest);
            if (!summary) return summary.status();
            result.push_back(TreeV2Revision{
                record.value(), snapshot.value().head.writer,
                snapshot.value().head.generation,
                snapshot.value().head.previous,
                snapshot.value().head.manifest, summary.value().paths,
                summary.value().live_files, summary.value().conflicts.size(),
                snapshot.value().head.checkpoint, current.contains(record.value()),
                pinned.contains(record.value())});
        }
    } catch (const std::filesystem::filesystem_error &error) {
        return Status{ErrorCode::io_error,
                      "unable to inventory tree-v2 history: " +
                          std::string(error.what())};
    }
    std::sort(result.begin(), result.end(),
              [](const TreeV2Revision &left, const TreeV2Revision &right) {
                  if (left.writer != right.writer)
                      return left.writer < right.writer;
                  if (left.generation != right.generation)
                      return left.generation > right.generation;
                  return left.record < right.record;
              });
    return result;
}

Result<TreeV2Diff> diff_tree_v2_records(
    const NamespacePolicy &policy, const Digest &from_record,
    const Digest &to_record, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
    auto from = load_tree_v2_stored_record(policy, from_record, sodium,
                                           transaction);
    auto to =
        load_tree_v2_stored_record(policy, to_record, sodium, transaction);
    if (!from) return from.status();
    if (!to) return to.status();
    return diff_manifests(policy, from_record, to_record,
                          from.value().head.manifest,
                          to.value().head.manifest, from.value().manifest,
                          to.value().manifest);
}

Result<std::vector<TreeV2Conflict>> tree_v2_conflicts(
    const NamespacePolicy &policy, const std::optional<Digest> &record,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction) {
    if (record) {
        auto snapshot =
            load_tree_v2_stored_record(policy, *record, sodium, transaction);
        if (!snapshot) return snapshot.status();
        auto summary =
            summarize_tree_v2_manifest(policy, snapshot.value().manifest);
        if (!summary) return summary.status();
        return summary.value().conflicts;
    }
    TreeV2BranchStore store{std::filesystem::path(policy.root)};
    auto frontier = store.load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    auto merged = merge_tree_v2_snapshots(policy, frontier.value(), sodium);
    if (!merged) return merged.status();
    return merged.value().conflicts;
}

Result<TreeV2RestorePlan> plan_tree_v2_restore_forward(
    const NamespacePolicy &policy, const Digest &target_record,
    const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness) {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok()) return valid;
    if (policy.engine != Engine::tree_v2 ||
        !std::binary_search(policy.writers.begin(), policy.writers.end(),
                            identity.public_key())) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 restore planning requires the local writer"};
    }
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;
    if (witness) {
        const Status fresh = witness->verify_read(policy, transaction);
        if (!fresh.ok()) return fresh;
    }
    TreeV2BranchStore store{std::filesystem::path(policy.root),
                            identity.public_key(), witness};
    const Status prepared = store.prepare(policy, transaction);
    if (!prepared.ok()) return prepared;
    auto target =
        load_tree_v2_stored_record(policy, target_record, sodium, transaction);
    if (!target) return target.status();
    auto target_summary =
        summarize_tree_v2_manifest(policy, target.value().manifest);
    if (!target_summary) return target_summary.status();
    auto frontier = store.load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    auto observations =
        frontier_observations(policy, frontier.value(), sodium);
    if (!observations) return observations.status();
    auto current = merge_tree_v2_snapshots(policy, frontier.value(), sodium);
    if (!current) return current.status();
    auto current_manifest =
        tree_v2_manifest_digest(policy, current.value().manifest, sodium);
    if (!current_manifest) return current_manifest.status();
    auto generated = next_generation(frontier.value(), identity.public_key());
    if (!generated) return generated.status();
    auto diff = diff_manifests(policy, {}, target_record, current_manifest.value(),
                               target.value().head.manifest,
                               current.value().manifest,
                               target.value().manifest);
    if (!diff) return diff.status();

    TreeV2MaintenanceStore maintenance{std::filesystem::path(policy.root),
                                       witness};
    auto maintenance_state = maintenance.load(
        policy, identity.public_key(), sodium, transaction);
    if (!maintenance_state) return maintenance_state.status();
    TreeV2WorkspaceStore workspace_store{std::filesystem::path(policy.root),
                                         witness};
    auto workspace = workspace_store.load(policy, identity.public_key(), sodium,
                                          &transaction);
    if (!workspace) return workspace.status();

    TreeV2RestorePlan plan;
    plan.target_record = target_record;
    plan.target_manifest = target.value().head.manifest;
    plan.current_manifest = current_manifest.value();
    plan.next_local_generation = generated.value();
    plan.frontier_writers = frontier.value().size();
    plan.namespace_writers = policy.writers.size();
    plan.pins = maintenance_state.value().pins.size();
    plan.cutoffs = maintenance_state.value().cutoffs.size();
    plan.target_paths = target_summary.value().paths;
    plan.target_files = target_summary.value().live_files;
    plan.target_conflicts = target_summary.value().conflicts.size();
    plan.current_conflicts = current.value().conflicts.size();
    plan.changed_paths = diff.value().entries.size();
    plan.target_pinned = std::binary_search(maintenance_state.value().pins.begin(),
                                            maintenance_state.value().pins.end(),
                                            target_record);
    plan.already_current = std::any_of(
        observations.value().begin(), observations.value().end(),
        [&target_record](const TreeV2Observation &observation) {
            return observation.record == target_record;
        }) && target.value().manifest == current.value().manifest;

    std::vector<std::uint8_t> plan_material;
    auto policy_bytes = encode_namespace_policy(policy);
    if (!policy_bytes) return policy_bytes.status();
    append_u64(plan_material, policy_bytes.value().size());
    append_bytes(plan_material, policy_bytes.value());
    if (maintenance_state.value().mutation == 0U) {
        // Absence is the authenticated empty policy established by the
        // owner-local store boundary; it intentionally has no signed record.
        append_u64(plan_material, 0U);
    } else {
        auto maintenance_bytes =
            encode_tree_v2_maintenance_state(maintenance_state.value());
        if (!maintenance_bytes) return maintenance_bytes.status();
        append_u64(plan_material, maintenance_bytes.value().size());
        append_bytes(plan_material, maintenance_bytes.value());
    }
    append_bytes(plan_material, target_record);
    append_bytes(plan_material, target.value().head.manifest);
    append_bytes(plan_material, current_manifest.value());
    append_u64(plan_material, observations.value().size());
    for (const TreeV2Observation &observation : observations.value()) {
        append_bytes(plan_material, observation.writer);
        append_u64(plan_material, observation.generation);
        append_bytes(plan_material, observation.record);
    }

    std::optional<Digest> scanned_manifest;
    if (workspace.value()) {
        plan.workspace_generation = workspace.value()->generation;
        auto encoded = encode_tree_v2_workspace_state(*workspace.value());
        if (!encoded) return encoded.status();
        append_u64(plan_material, encoded.value().size());
        append_bytes(plan_material, encoded.value());
        plan.workspace_current =
            workspace.value()->phase == TreeV2WorkspacePhase::stable &&
            workspace.value()->worktree == worktree &&
            workspace.value()->active_manifest == current_manifest.value() &&
            workspace.value()->active_frontier == observations.value();
        if (plan.workspace_current) {
            auto scan = scan_tree_v2_worktree(
                policy, worktree, current.value().manifest,
                identity.public_key(), generated.value());
            if (!scan) return scan.status();
            plan.worktree_clean = !scan.value().changed;
            auto digest = tree_v2_manifest_digest(policy, scan.value().manifest,
                                                  sodium);
            if (!digest) return digest.status();
            scanned_manifest = digest.value();
        }
    } else {
        append_u64(plan_material, 0U);
    }
    append_bytes(plan_material, scanned_manifest.value_or(Digest{}));

    std::map<Digest, std::uint64_t> objects;
    for (const TreeV2Entry &entry : target.value().manifest.entries) {
        if (entry.kind != TreeV2EntryKind::file) continue;
        const auto [found, inserted] =
            objects.emplace(entry.content, entry.content_bytes);
        if (!inserted && found->second != entry.content_bytes) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 target gives one object conflicting sizes"};
        }
    }
    plan.required_objects = objects.size();
    for (const auto &[digest, bytes] : objects) {
        if (plan.required_bytes > std::numeric_limits<std::uint64_t>::max() -
                                      bytes) {
            return Status{ErrorCode::resource_exhausted,
                          "tree-v2 restore byte requirement overflows"};
        }
        plan.required_bytes += bytes;
        struct stat metadata {};
        const std::filesystem::path object = tree_v2_object_path(policy, digest);
        if (::lstat(object.c_str(), &metadata) != 0) {
            if (errno != ENOENT) {
                return Status{ErrorCode::io_error,
                              "unable to inspect a tree-v2 restore object"};
            }
            ++plan.missing_objects;
            plan.missing_bytes += bytes;
        } else {
            const Status verified =
                verify_tree_v2_object_file(object, digest, bytes);
            if (!verified.ok()) return verified;
        }
        append_bytes(plan_material, digest);
        append_u64(plan_material, bytes);
    }
    append_u64(plan_material, plan.missing_objects);
    append_u64(plan_material, plan.missing_bytes);

    bool authored_valid = false;
    if (plan.target_conflicts == 0U) {
        auto authored = authored_restore_manifest(
            policy, current.value().manifest, target.value().manifest,
            identity.public_key(), generated.value());
        authored_valid = authored.ok();
        if (!authored_valid &&
            authored.status().code() != ErrorCode::resource_exhausted) {
            return authored.status();
        }
    }
    plan.ready = plan.workspace_current && plan.worktree_clean &&
                 !plan.already_current && plan.target_conflicts == 0U &&
                 plan.missing_objects == 0U && authored_valid;
    append_u64(plan_material, plan.ready ? 1U : 0U);
    auto plan_id = sodium.hash(kRestorePlanDomain, plan_material);
    if (!plan_id) return plan_id.status();
    plan.id = plan_id.value();
    return plan;
}

Result<TreeV2RestoreForwardResult> restore_tree_v2_forward(
    const NamespacePolicy &policy, const Digest &target_record,
    const Digest &expected_plan, const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity,
    const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness) {
    if (witness) {
        const Status fresh = witness->verify_read(policy, transaction);
        if (!fresh.ok()) return fresh;
    }
    auto plan = plan_tree_v2_restore_forward(policy, target_record, worktree,
                                             identity, sodium, transaction,
                                             witness);
    if (!plan) return plan.status();
    if (!security::constant_time_equal(plan.value().id, expected_plan)) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 restore plan is stale or does not match"};
    }
    if (!plan.value().ready) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 restore plan is not ready to apply"};
    }
    TreeV2BranchStore store{std::filesystem::path(policy.root),
                            identity.public_key(), witness};
    auto target =
        load_tree_v2_stored_record(policy, target_record, sodium, transaction);
    auto frontier = store.load_frontier(policy, sodium, transaction);
    if (!target) return target.status();
    if (!frontier) return frontier.status();
    auto current = merge_tree_v2_snapshots(policy, frontier.value(), sodium);
    if (!current) return current.status();
    TreeV2WorkspaceStore workspace_store{std::filesystem::path(policy.root),
                                         witness};
    auto workspace = workspace_store.load(policy, identity.public_key(), sodium,
                                          &transaction);
    if (!workspace || !workspace.value()) {
        return workspace ? Status{ErrorCode::unavailable,
                                  "tree-v2 restore workspace disappeared"}
                         : workspace.status();
    }
    auto authored = authored_restore_manifest(
        policy, current.value().manifest, target.value().manifest,
        identity.public_key(), plan.value().next_local_generation);
    if (!authored) return authored.status();
    auto published = store.publish_local_from_frontier(
        policy, authored.value(), workspace.value()->active_frontier, identity,
        sodium, transaction);
    if (!published) return published.status();
    if (published.value().decision == TreeV2BranchStoreDecision::duplicate) {
        return Status{ErrorCode::protocol_error,
                      "tree-v2 restore did not create a forward revision"};
    }
    auto reconciled = reconcile_tree_v2_workspace(
        policy, worktree, identity, sodium, transaction, witness);
    if (!reconciled) {
        return Status{
            reconciled.status().code(),
            "tree-v2 forward revision is durable as record " +
                security::hex(published.value().record) +
                "; worktree reconciliation failed: " +
                reconciled.status().message()};
    }
    return TreeV2RestoreForwardResult{plan.value(), published.value(),
                                      reconciled.value()};
}

} // namespace iotox::sync
