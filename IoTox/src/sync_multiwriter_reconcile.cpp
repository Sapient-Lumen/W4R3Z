#include "iotox/sync_multiwriter_reconcile.hpp"

#include "iotox/sync_tree_v2_witness.hpp"

#include <algorithm>
#include <limits>
#include <optional>
#include <string_view>

namespace iotox::sync {
namespace {

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
        result.push_back(TreeV2Observation{
            snapshot.head.writer, snapshot.head.generation, record.value()});
    }
    std::sort(
        result.begin(), result.end(),
        [](const TreeV2Observation &left, const TreeV2Observation &right) {
            return left.writer < right.writer;
        });
    return result;
}

[[nodiscard]] Result<std::uint64_t>
next_local_generation(std::span<const TreeV2Snapshot> frontier,
                      const PrincipalId &local_writer) {
    const auto local =
        std::find_if(frontier.begin(), frontier.end(),
                     [&local_writer](const TreeV2Snapshot &snapshot) {
                         return snapshot.head.writer == local_writer;
                     });
    if (local == frontier.end()) return 1U;
    if (local->head.generation == std::numeric_limits<std::uint64_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 local branch generation is exhausted"};
    }
    return local->head.generation + 1U;
}

[[nodiscard]] Status
validate_workspace_frontier(const NamespacePolicy &policy,
                            std::span<const TreeV2Observation> observations,
                            const security::Sodium &sodium,
                            const SyncNamespaceTransaction &transaction) {
    for (const TreeV2Observation &observation : observations) {
        auto snapshot = load_tree_v2_stored_record(policy, observation.record,
                                                   sodium, transaction);
        if (!snapshot || snapshot.value().head.writer != observation.writer ||
            snapshot.value().head.generation != observation.generation) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 workspace frontier proof is unavailable"};
        }
    }
    return Status::success();
}

[[nodiscard]] Status add_counter(std::uint64_t &total, std::uint64_t delta,
                                 std::string_view name) {
    if (total > std::numeric_limits<std::uint64_t>::max() - delta) {
        return Status{ErrorCode::resource_exhausted,
                      "tree-v2 " + std::string(name) + " count overflows"};
    }
    total += delta;
    return Status::success();
}

[[nodiscard]] Status accumulate_projection_update(
    TreeV2ReconcileResult &result, const TreeV2WorktreeUpdateResult &update) {
    Status added = add_counter(result.projection_directories,
                               update.projection.directories,
                               "projection directory");
    if (!added.ok()) return added;
    added = add_counter(result.projection_files, update.projection.files,
                        "projection file");
    if (!added.ok()) return added;
    added = add_counter(result.projection_bytes, update.projection.bytes,
                        "projection byte");
    if (!added.ok()) return added;
    added = add_counter(result.projection_conflict_files,
                        update.projection.conflict_files,
                        "projection conflict file");
    if (!added.ok()) return added;
    added = add_counter(result.projection_conflict_tombstones,
                        update.projection.conflict_tombstones,
                        "projection conflict tombstone");
    if (!added.ok()) return added;
    added = add_counter(result.projection_preserved_unselected_entries,
                        update.preserved_unselected_entries,
                        "projection preserved entry");
    if (!added.ok()) return added;
    added = add_counter(result.projection_preserved_unselected_directories,
                        update.preserved_unselected_directories,
                        "projection preserved directory");
    if (!added.ok()) return added;
    added = add_counter(result.projection_preserved_unselected_files,
                        update.preserved_unselected_files,
                        "projection preserved file");
    if (!added.ok()) return added;
    return add_counter(result.projection_preserved_unselected_bytes,
                       update.preserved_unselected_bytes,
                       "projection preserved byte");
}

} // namespace

Result<TreeV2ReconcileResult> reconcile_tree_v2_workspace(
    const NamespacePolicy &policy, const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness,
    TreeV2SourceDigestCache *source_digest_cache) {
    const Status valid = validate_namespace_policy(policy);
    if (!valid.ok()) return valid;
    if (policy.engine != Engine::tree_v2 ||
        !std::binary_search(policy.writers.begin(), policy.writers.end(),
                            identity.public_key())) {
        return Status{ErrorCode::invalid_argument,
                      "tree-v2 reconciliation requires the local writer"};
    }
    const Status held = require_sync_transaction(policy, transaction);
    if (!held.ok()) return held;

    TreeV2BranchStore branches{std::filesystem::path(policy.root),
                               identity.public_key(), witness};
    const Status prepared = branches.prepare(policy, transaction);
    if (!prepared.ok()) return prepared;
    TreeV2WorkspaceStore workspaces{std::filesystem::path(policy.root),
                                    witness};
    auto workspace = workspaces.load(policy, identity.public_key(), sodium,
                                     &transaction);
    if (!workspace) return workspace.status();
    TreeV2ReconcileResult result;

    if (workspace.value() &&
        workspace.value()->phase == TreeV2WorkspacePhase::pending_exchange) {
        TreeV2WorkspaceState pending = *workspace.value();
        if (pending.worktree != worktree) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 workspace path changed during recovery"};
        }
        const Status active_proofs = validate_workspace_frontier(
            policy, pending.active_frontier, sodium, transaction);
        if (!active_proofs.ok()) return active_proofs;
        const Status pending_proofs = validate_workspace_frontier(
            policy, pending.pending_frontier, sodium, transaction);
        if (!pending_proofs.ok()) return pending_proofs;
        auto active_manifest = load_tree_v2_stored_manifest(
            policy, pending.active_manifest, sodium, transaction);
        auto pending_manifest = load_tree_v2_stored_manifest(
            policy, pending.pending_manifest, sodium, transaction);
        auto pending_worktree = load_tree_v2_stored_manifest(
            policy, pending.pending_worktree_manifest, sodium, transaction);
        if (!active_manifest) return active_manifest.status();
        if (!pending_manifest) return pending_manifest.status();
        if (!pending_worktree) return pending_worktree.status();
        if (pending.active_manifest != pending.pending_manifest) {
            auto pending_projection =
                summarize_tree_v2_manifest(policy, pending_manifest.value());
            if (!pending_projection) return pending_projection.status();
            auto recovered = recover_tree_v2_worktree_exchange(
                policy, active_manifest.value(), pending_worktree.value(),
                pending_projection.value(), worktree, identity.public_key(),
                sodium, transaction);
            if (!recovered) return recovered.status();
            const Status counted =
                accumulate_projection_update(result, recovered.value());
            if (!counted.ok()) return counted;
            result.workspace_exchanged = recovered.value().exchanged;
        }
        auto finished = workspaces.finish_exchange(
            policy, pending.pending_manifest, identity, sodium, &transaction);
        if (!finished) return finished.status();
        workspace = std::optional<TreeV2WorkspaceState>{finished.value().state};
        result.recovered_pending_exchange = true;
    }

    std::optional<TreeV2Manifest> baseline;
    std::vector<TreeV2Observation> visible_frontier;
    if (workspace.value()) {
        if (workspace.value()->worktree != worktree ||
            workspace.value()->phase != TreeV2WorkspacePhase::stable) {
            return Status{
                ErrorCode::protocol_error,
                "tree-v2 workspace state is not stable for this path"};
        }
        const Status proofs = validate_workspace_frontier(
            policy, workspace.value()->active_frontier, sodium, transaction);
        if (!proofs.ok()) return proofs;
        auto loaded = load_tree_v2_stored_manifest(
            policy, workspace.value()->active_manifest, sodium, transaction);
        if (!loaded) return loaded.status();
        baseline = std::move(loaded).value();
        visible_frontier = workspace.value()->active_frontier;
    }

    auto frontier = branches.load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();

    // A checkpoint branch commits before its workspace marker. If power is
    // lost in that narrow interval, the checkpoint itself carries every exact
    // previously visible observation. Advance only across that authenticated
    // superset; an ordinary unseen local successor remains a hard failure.
    if (workspace.value()) {
        const auto local = std::find_if(
            frontier.value().begin(), frontier.value().end(),
            [&identity](const TreeV2Snapshot &snapshot) {
                return snapshot.head.writer == identity.public_key();
            });
        const auto visible_self = std::find_if(
            visible_frontier.begin(), visible_frontier.end(),
            [&identity](const TreeV2Observation &observation) {
                return observation.writer == identity.public_key();
            });
        auto local_record =
            local == frontier.value().end()
                ? Result<Digest>{Status{ErrorCode::not_found,
                                        "tree-v2 local branch is absent"}}
                : tree_v2_branch_record_digest(policy, local->head, sodium);
        const bool marker_matches =
            local != frontier.value().end() && local_record &&
            visible_self != visible_frontier.end() &&
            visible_self->generation == local->head.generation &&
            visible_self->record == local_record.value();
        if (!marker_matches && local != frontier.value().end() &&
            local->head.checkpoint) {
            const bool covers_visible = std::all_of(
                visible_frontier.begin(), visible_frontier.end(),
                [&local](const TreeV2Observation &observation) {
                    return std::find(local->head.observations.begin(),
                                     local->head.observations.end(),
                                     observation) !=
                           local->head.observations.end();
                });
            if (!covers_visible || !local_record) {
                return Status{ErrorCode::protocol_error,
                              "tree-v2 checkpoint does not cover the signed "
                              "workspace frontier"};
            }
            auto checkpoint_digest = tree_v2_manifest_digest(
                policy, local->manifest, sodium);
            if (!checkpoint_digest) return checkpoint_digest.status();
            auto checkpoint_frontier =
                frontier_observations(policy, frontier.value(), sodium);
            if (!checkpoint_frontier) return checkpoint_frontier.status();
            auto begun = workspaces.begin_exchange(
                policy, workspace.value()->active_manifest,
                checkpoint_digest.value(), workspace.value()->active_manifest,
                checkpoint_frontier.value(), identity, sodium, &transaction);
            if (!begun) return begun.status();
            auto target = summarize_tree_v2_manifest(policy, local->manifest);
            if (!target) return target.status();
            auto updated = update_tree_v2_worktree(
                policy, *baseline, target.value(), worktree,
                identity.public_key(), sodium, transaction, &*baseline);
            if (!updated) return updated.status();
            const Status counted =
                accumulate_projection_update(result, updated.value());
            if (!counted.ok()) return counted;
            auto finished = workspaces.finish_exchange(
                policy, checkpoint_digest.value(), identity, sodium,
                &transaction);
            if (!finished) return finished.status();
            workspace =
                std::optional<TreeV2WorkspaceState>{finished.value().state};
            baseline = local->manifest;
            visible_frontier = std::move(checkpoint_frontier).value();
            result.workspace_exchanged =
                result.workspace_exchanged || updated.value().exchanged;
            result.recovered_pending_exchange = true;
        }
    }
    auto next_generation =
        next_local_generation(frontier.value(), identity.public_key());
    if (!next_generation) return next_generation.status();
    std::optional<TreeV2ProjectionPolicy> previous_projection;
    if (baseline) {
        auto transition = tree_v2_projection_transition(
            policy, *baseline, worktree, sodium);
        if (!transition) return transition.status();
        previous_projection = std::move(transition).value();
    }
    TreeV2SourceDigestCache next_source_digest_cache;
    auto scan = scan_tree_v2_worktree(
        policy, worktree, baseline, identity.public_key(),
        next_generation.value(),
        previous_projection ? &*previous_projection : nullptr,
        source_digest_cache, source_digest_cache == nullptr
                                 ? nullptr
                                 : &next_source_digest_cache);
    if (!scan) return scan.status();
    // An unchanged scan against a stable signed workspace cannot introduce new
    // local file objects. Avoid repeating the complete CAS import/revalidation
    // pass on no-op wakeups; later projection or repair work still verifies
    // every object it actually consumes.
    if (!workspace.value() || scan.value().changed) {
        auto objects =
            store_tree_v2_scan_objects(policy, scan.value(), transaction);
        if (!objects) return objects.status();
        result.cas_inspected_objects = objects.value().inspected_objects;
        result.cas_inspected_bytes = objects.value().inspected_bytes;
        result.cas_installed_objects = objects.value().installed_objects;
        result.cas_installed_bytes = objects.value().installed_bytes;
        result.cas_reused_objects = objects.value().reused_objects;
    }

    Result<TreeV2BranchStoreResult> published = [&]()
        -> Result<TreeV2BranchStoreResult> {
        if (!workspace.value() || scan.value().changed) {
            return branches.publish_local_from_frontier(
                policy, scan.value().manifest, visible_frontier, identity,
                sodium, transaction);
        }
        const auto local = std::find_if(
            frontier.value().begin(), frontier.value().end(),
            [&identity](const TreeV2Snapshot &snapshot) {
                return snapshot.head.writer == identity.public_key();
            });
        if (local == frontier.value().end()) {
            return Status{ErrorCode::protocol_error,
                          "tree-v2 signed workspace has no local branch"};
        }
        auto record = tree_v2_branch_record_digest(policy, local->head, sodium);
        if (!record) return record.status();
        return TreeV2BranchStoreResult{
            TreeV2BranchStoreDecision::duplicate, *local, record.value(),
            false};
    }();
    if (!published) return published.status();
    result.publication = published.value().decision;
    if (published.value().decision != TreeV2BranchStoreDecision::duplicate)
        ++result.branch_advances;
    result.local_changed = scan.value().changed;
    result.local_events = scan.value().new_events;
    result.source_inspected_entries = scan.value().inspected_entries;
    result.source_hashed_file_digests = scan.value().hashed_file_digests;
    result.source_reused_file_digests = scan.value().reused_file_digests;

    frontier = branches.load_frontier(policy, sodium, transaction);
    if (!frontier) return frontier.status();
    auto merged = merge_tree_v2_snapshots(policy, frontier.value(), sodium);
    if (!merged) return merged.status();
    auto merged_digest =
        tree_v2_manifest_digest(policy, merged.value().manifest, sodium);
    if (!merged_digest) return merged_digest.status();
    auto retained = branches.retain_manifest(
        policy, merged.value().manifest, sodium, transaction);
    if (!retained) return retained.status();
    if (retained.value() != merged_digest.value()) {
        return Status{ErrorCode::internal_error,
                      "tree-v2 retained merge identity changed"};
    }
    auto target_frontier =
        frontier_observations(policy, frontier.value(), sodium);
    if (!target_frontier) return target_frontier.status();

    if (!workspace.value()) {
        auto scan_digest =
            tree_v2_manifest_digest(policy, scan.value().manifest, sodium);
        if (!scan_digest) return scan_digest.status();
        std::vector<TreeV2Observation> local_frontier{
            TreeV2Observation{published.value().snapshot.head.writer,
                              published.value().snapshot.head.generation,
                              published.value().record}};
        auto initialized =
            workspaces.initialize(policy, worktree, scan_digest.value(),
                                  local_frontier, identity, sodium,
                                  &transaction);
        if (!initialized) return initialized.status();
        workspace =
            std::optional<TreeV2WorkspaceState>{initialized.value().state};
        baseline = scan.value().manifest;
        result.workspace_initialized = true;
    }

    const bool state_changed =
        workspace.value()->active_manifest != merged_digest.value() ||
        workspace.value()->active_frontier != target_frontier.value();
    const TreeV2Manifest *active_projection =
        result.workspace_initialized ? nullptr : &*baseline;
    if (state_changed) {
        auto worktree_digest =
            tree_v2_manifest_digest(policy, scan.value().manifest, sodium);
        if (!worktree_digest) return worktree_digest.status();
        auto begun = workspaces.begin_exchange(
            policy, workspace.value()->active_manifest, merged_digest.value(),
            worktree_digest.value(), target_frontier.value(), identity, sodium,
            &transaction);
        if (!begun) return begun.status();
        if (workspace.value()->active_manifest != merged_digest.value()) {
            auto updated = update_tree_v2_worktree(
                policy, scan.value().manifest, merged.value(), worktree,
                identity.public_key(), sodium, transaction,
                active_projection);
            if (!updated) return updated.status();
            const Status counted =
                accumulate_projection_update(result, updated.value());
            if (!counted.ok()) return counted;
            result.workspace_exchanged =
                result.workspace_exchanged || updated.value().exchanged;
        } else {
            auto summarized = summarize_tree_v2_manifest(policy, *baseline);
            if (!summarized) return summarized.status();
            auto marker = update_tree_v2_worktree(
                policy, scan.value().manifest, summarized.value(), worktree,
                identity.public_key(), sodium, transaction,
                active_projection);
            if (!marker) return marker.status();
            const Status counted =
                accumulate_projection_update(result, marker.value());
            if (!counted.ok()) return counted;
            result.workspace_exchanged =
                result.workspace_exchanged || marker.value().exchanged;
        }
        auto finished = workspaces.finish_exchange(
            policy, merged_digest.value(), identity, sodium, &transaction);
        if (!finished) return finished.status();
    } else if (!result.workspace_initialized && !scan.value().changed &&
               !previous_projection) {
        // The existing stable workspace was scanned unchanged, the signed
        // frontier still matches it, and tree_v2_projection_transition already
        // authenticated the current projection marker. Avoid a second complete
        // marker-only worktree scan on pure no-op wakeups.
    } else {
        auto summarized = summarize_tree_v2_manifest(policy, *baseline);
        if (!summarized) return summarized.status();
        auto marker = update_tree_v2_worktree(
            policy, scan.value().manifest, summarized.value(), worktree,
            identity.public_key(), sodium, transaction, active_projection);
        if (!marker) return marker.status();
        const Status counted =
            accumulate_projection_update(result, marker.value());
        if (!counted.ok()) return counted;
        result.workspace_exchanged =
            result.workspace_exchanged || marker.value().exchanged;
    }

    result.frontier_writers = target_frontier.value().size();
    result.conflicts = merged.value().conflicts.size();
    result.files = merged.value().live_files;
    result.tombstoned_paths = merged.value().tombstoned_paths;
    if (source_digest_cache != nullptr) {
        if (result.workspace_exchanged) {
            source_digest_cache->clear();
        } else {
            *source_digest_cache = std::move(next_source_digest_cache);
        }
    }
    return result;
}

Result<TreeV2CheckpointResult> checkpoint_tree_v2_workspace(
    const NamespacePolicy &policy, const std::filesystem::path &worktree,
    const security::DeviceIdentity &identity, const security::Sodium &sodium,
    const SyncNamespaceTransaction &transaction,
    std::shared_ptr<TreeV2StateWitness> witness) {
    auto before = reconcile_tree_v2_workspace(policy, worktree, identity,
                                              sodium, transaction, witness);
    if (!before) return before.status();
    if (before.value().conflicts != 0U) {
        return Status{ErrorCode::unavailable,
                      "tree-v2 checkpoint refuses unresolved conflicts"};
    }
    TreeV2BranchStore store{std::filesystem::path(policy.root),
                            identity.public_key(), witness};
    auto checkpoint = store.checkpoint_local(policy, identity, sodium,
                                             transaction);
    if (!checkpoint) return checkpoint.status();
    auto after = reconcile_tree_v2_workspace(policy, worktree, identity,
                                             sodium, transaction, witness);
    if (!after) return after.status();
    return TreeV2CheckpointResult{before.value(), after.value(),
                                  checkpoint.value()};
}

} // namespace iotox::sync
