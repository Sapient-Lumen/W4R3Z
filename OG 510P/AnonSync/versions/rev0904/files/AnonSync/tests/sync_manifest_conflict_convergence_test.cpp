#include "anonsync_core.hpp"
#include "sync_conflict_resolution.hpp"

#include <algorithm>
#include <array>
#include <filesystem>
#include <iostream>
#include <locale>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

namespace fs = std::filesystem;

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

anonsync::NormalizedSyncPath normalized_path(const std::string& value) {
    anonsync::NormalizedSyncPath out;
    const auto result = anonsync::normalize_sync_relative_path(value, out);
    if (!result.ok) {
        throw std::runtime_error("fixture path invalid: " + result.reason);
    }
    return out;
}

anonsync::SyncManifestEntry file_entry(
    const std::string& folder,
    const std::string& device,
    const std::string& path,
    char content_nibble,
    std::uint64_t counter) {
    anonsync::SyncManifestEntry out;
    out.folder_id = folder;
    out.device_id = device;
    out.path = normalized_path(path);
    out.kind = anonsync::SyncManifestEntryKind::File;
    out.size_bytes = 1;
    out.content_sha256 = std::string(64, content_nibble);
    out.chunks = {{0, 1, std::string(64, content_nibble)}};
    out.lineage = {{device, counter}};
    return out;
}

anonsync::SyncManifestEntry tombstone_entry(
    const std::string& folder,
    const std::string& device,
    const std::string& path,
    std::uint64_t counter) {
    anonsync::SyncManifestEntry out;
    out.folder_id = folder;
    out.device_id = device;
    out.path = normalized_path(path);
    out.kind = anonsync::SyncManifestEntryKind::Tombstone;
    out.lineage = {{device, counter}};
    return out;
}

anonsync::SyncFolderManifest manifest(
    const std::string& folder,
    const std::string& device,
    std::uint64_t counter,
    anonsync::SyncManifestEntry entry) {
    anonsync::SyncFolderManifest out;
    out.folder_id = folder;
    out.device_id = device;
    out.manifest_counter = counter;
    out.entries.push_back(std::move(entry));
    return out;
}

struct GroupedPunctuation final : std::numpunct<char> {
    char do_thousands_sep() const override { return '_'; }
    std::string do_grouping() const override { return "\3"; }
};

struct AbstractReplica final {
    std::string primary_version_digest;
    std::set<std::string> conflict_version_digests;

    bool operator==(const AbstractReplica&) const = default;
};

anonsync::SyncManifestEntry publish_as(
    const anonsync::SyncManifestEntry& entry,
    const std::string& device) {
    anonsync::SyncManifestEntry out = entry;
    out.device_id = device;
    return out;
}

struct FoldedConflictHistory final {
    anonsync::SyncManifestEntry primary;
    std::set<std::string> preserved_file_versions;
};

FoldedConflictHistory fold_conflict_history_or_throw(
    const std::vector<anonsync::SyncManifestEntry>& delivery_order) {
    using namespace anonsync;
    if (delivery_order.empty()) {
        throw std::invalid_argument("conflict history must not be empty");
    }

    const std::string host_device = "device-accumulator";
    FoldedConflictHistory out;
    out.primary = publish_as(delivery_order.front(), host_device);

    for (std::size_t index = 1; index < delivery_order.size(); ++index) {
        const SyncManifestEntry& incoming = delivery_order[index];
        const std::string local_digest =
            sync_manifest_entry_version_digest(out.primary);
        const std::string remote_digest =
            sync_manifest_entry_version_digest(incoming);

        SyncManifestDiffPlan plan;
        const SyncValidationResult built = build_sync_manifest_diff_plan(
            manifest(out.primary.folder_id, host_device, index, out.primary),
            manifest(incoming.folder_id, incoming.device_id, index, incoming),
            plan);
        if (!built.ok || plan.entries.size() != 1U) {
            throw std::runtime_error(
                "generated conflict history did not build one transition: " +
                built.reason);
        }

        const SyncManifestPlanEntry& transition = plan.entries.front();
        if (transition.lineage_relation != SyncLineageRelation::Concurrent) {
            throw std::runtime_error(
                "generated conflict values unexpectedly lost concurrent lineage");
        }
        switch (transition.action) {
            case SyncPlanAction::PublishLocalFile:
            case SyncPlanAction::PublishLocalTombstone:
                if (incoming.kind == SyncManifestEntryKind::File) {
                    // The remote peer owns and preserves this losing file.
                    out.preserved_file_versions.insert(remote_digest);
                }
                break;
            case SyncPlanAction::RecordConflict:
                if (out.primary.kind != SyncManifestEntryKind::File) {
                    throw std::runtime_error(
                        "record-conflict transition invented non-file bytes");
                }
                out.preserved_file_versions.insert(local_digest);
                out.primary = publish_as(incoming, host_device);
                break;
            case SyncPlanAction::ApplyRemoteTombstone:
                if (out.primary.kind != SyncManifestEntryKind::Tombstone ||
                    incoming.kind != SyncManifestEntryKind::Tombstone) {
                    throw std::runtime_error(
                        "unpreserved remote application escaped tombstone/tombstone policy");
                }
                out.primary = publish_as(incoming, host_device);
                break;
            case SyncPlanAction::Noop:
            case SyncPlanAction::FetchRemoteFile:
                throw std::runtime_error(
                    "generated distinct concurrent values produced an unexpected transition");
        }

        const SyncManifestEntry duplicate =
            publish_as(out.primary, "device-duplicate");
        SyncManifestDiffPlan duplicate_plan;
        const SyncValidationResult duplicate_built =
            build_sync_manifest_diff_plan(
                manifest(out.primary.folder_id, host_device, index + 100U,
                         out.primary),
                manifest(duplicate.folder_id, duplicate.device_id,
                         index + 100U, duplicate),
                duplicate_plan);
        if (!duplicate_built.ok || duplicate_plan.entries.size() != 1U ||
            duplicate_plan.entries.front().action != SyncPlanAction::Noop) {
            throw std::runtime_error(
                "duplicate winner delivery was not idempotent");
        }
    }
    return out;
}

}  // namespace

int main() {
    using namespace anonsync;
    try {
        int checks = 0;
        const std::string folder = "folder-alpha";
        const std::string path = "docs/concurrent.txt";
        const SyncManifestEntry alpha =
            file_entry(folder, "device-alpha", path, 'a', 1);
        const SyncManifestEntry bravo =
            file_entry(folder, "device-bravo", path, 'b', 1);
        const SyncFolderManifest alpha_manifest =
            manifest(folder, "device-alpha", 1, alpha);
        const SyncFolderManifest bravo_manifest =
            manifest(folder, "device-bravo", 1, bravo);

        SyncManifestDiffPlan alpha_view;
        SyncManifestDiffPlan bravo_view;
        require(build_sync_manifest_diff_plan(
                    alpha_manifest, bravo_manifest, alpha_view).ok &&
                    build_sync_manifest_diff_plan(
                    bravo_manifest, alpha_manifest, bravo_view).ok,
                "both peer orientations must build valid conflict plans", checks);
        require(alpha_view.entries.size() == 1U &&
                    bravo_view.entries.size() == 1U,
                "both peer orientations must describe one shared path", checks);

        SyncManifestEntry equal_lineage_divergent = bravo;
        equal_lineage_divergent.lineage = {{"device-alpha", 1}};
        SyncManifestDiffPlan equal_forward;
        equal_forward.folder_id = "must-be-cleared";
        equal_forward.entries.push_back(SyncManifestPlanEntry{});
        SyncManifestDiffPlan equal_reverse = equal_forward;
        const SyncValidationResult equal_forward_result =
            build_sync_manifest_diff_plan(
                alpha_manifest,
                manifest(folder, "device-bravo", 1,
                         equal_lineage_divergent),
                equal_forward);
        const SyncValidationResult equal_reverse_result =
            build_sync_manifest_diff_plan(
                manifest(folder, "device-bravo", 1,
                         equal_lineage_divergent),
                alpha_manifest,
                equal_reverse);
        require(!equal_forward_result.ok && !equal_reverse_result.ok &&
                    equal_forward_result.reason.find(
                        "counter reuse or equivocation") != std::string::npos &&
                    equal_reverse_result.reason.find(
                        "counter reuse or equivocation") != std::string::npos,
                "equal lineage with different bytes must fail as identity corruption in both orientations",
                checks);
        require(equal_forward.folder_id.empty() &&
                    equal_reverse.folder_id.empty() &&
                    equal_forward.entries.empty() &&
                    equal_reverse.entries.empty(),
                "failed manifest planning must not leak a caller-visible partial authority prefix",
                checks);

        SyncFolderManifest prefix_local;
        prefix_local.folder_id = folder;
        prefix_local.device_id = "device-alpha";
        prefix_local.manifest_counter = 2;
        prefix_local.entries = {
            file_entry(folder, "device-alpha", "a/local-only.txt", 'c', 1),
            alpha,
        };
        SyncFolderManifest prefix_remote;
        prefix_remote.folder_id = folder;
        prefix_remote.device_id = "device-bravo";
        prefix_remote.manifest_counter = 2;
        prefix_remote.entries = {equal_lineage_divergent};
        SyncManifestDiffPlan unpublished_prefix;
        unpublished_prefix.folder_id = "sentinel-folder";
        unpublished_prefix.entries.push_back(SyncManifestPlanEntry{});
        const SyncValidationResult prefix_result =
            build_sync_manifest_diff_plan(
                prefix_local, prefix_remote, unpublished_prefix);
        require(!prefix_result.ok &&
                    prefix_result.reason.find(
                        "counter reuse or equivocation") != std::string::npos,
                "a late equal-lineage identity failure must reject the whole multi-entry plan",
                checks);
        require(unpublished_prefix.folder_id.empty() &&
                    unpublished_prefix.local_device_id.empty() &&
                    unpublished_prefix.remote_device_id.empty() &&
                    unpublished_prefix.entries.empty(),
                "a late planner failure must discard an already-built candidate prefix",
                checks);

        const SyncManifestPlanEntry& alpha_plan = alpha_view.entries.front();
        const SyncManifestPlanEntry& bravo_plan = bravo_view.entries.front();
        const bool alpha_publishes =
            alpha_plan.action == SyncPlanAction::PublishLocalFile;
        const bool bravo_publishes =
            bravo_plan.action == SyncPlanAction::PublishLocalFile;
        const bool alpha_preserves =
            alpha_plan.action == SyncPlanAction::RecordConflict;
        const bool bravo_preserves =
            bravo_plan.action == SyncPlanAction::RecordConflict;
        require(alpha_publishes != bravo_publishes &&
                    alpha_preserves != bravo_preserves,
                "exactly one peer must publish the deterministic winner and one must preserve the loser",
                checks);
        require(alpha_plan.lineage_relation == SyncLineageRelation::Concurrent &&
                    bravo_plan.lineage_relation == SyncLineageRelation::Concurrent,
                "orientation reversal must preserve concurrent lineage classification",
                checks);

        const SyncManifestDiffPlan& winner_view =
            alpha_publishes ? alpha_view : bravo_view;
        const SyncManifestDiffPlan& loser_view =
            alpha_preserves ? alpha_view : bravo_view;
        const SyncManifestPlanEntry& winner_plan = winner_view.entries.front();
        const SyncManifestPlanEntry& loser_plan = loser_view.entries.front();
        require(winner_plan.local_version_digest ==
                    loser_plan.remote_version_digest &&
                    winner_plan.remote_version_digest ==
                    loser_plan.local_version_digest,
                "complementary plans must agree on exact winner and loser versions",
                checks);
        require(loser_plan.conflict_set_id.starts_with("conflict-") &&
                    loser_plan.conflict_set_id.size() == 41U &&
                    winner_plan.conflict_set_id.empty(),
                "only the losing peer must mint bounded conflict-copy authority",
                checks);

        const auto file_kind = SyncConflictValueKind::File;
        const std::string forward_id = make_sync_conflict_set_id_or_throw(
            folder, path, file_kind, alpha_plan.local_version_digest,
            file_kind, alpha_plan.remote_version_digest);
        const std::string reverse_id = make_sync_conflict_set_id_or_throw(
            folder, path, file_kind, bravo_plan.local_version_digest,
            file_kind, bravo_plan.remote_version_digest);
        require(forward_id == reverse_id &&
                    forward_id == loser_plan.conflict_set_id,
                "the integrated plan must use one orientation-independent conflict-set identity",
                checks);

        const std::locale previous_locale = std::locale();
        std::locale::global(std::locale(
            previous_locale, new GroupedPunctuation));
        std::string hostile_locale_id;
        try {
            hostile_locale_id = make_sync_conflict_set_id_or_throw(
                folder, path, file_kind, alpha_plan.local_version_digest,
                file_kind, alpha_plan.remote_version_digest);
        } catch (...) {
            std::locale::global(previous_locale);
            throw;
        }
        std::locale::global(previous_locale);
        require(hostile_locale_id == forward_id,
                "conflict identity must not depend on ambient numeric locale",
                checks);

        const fs::path root = fs::temp_directory_path() /
            ("anonsync-conflict-convergence-" + forward_id.substr(9, 12));
        const fs::path staging = fs::temp_directory_path() /
            ("anonsync-conflict-convergence-stage-" +
             forward_id.substr(9, 12));
        std::error_code ec;
        fs::remove_all(root, ec);
        fs::remove_all(staging, ec);
        fs::create_directories(root);
        fs::create_directories(staging);
        SyncLocalApplyOptions apply_options;
        apply_options.local_root_path = root.string();
        apply_options.staging_root_path = staging.string();
        SyncLocalApplyPlan loser_apply;
        require(build_sync_local_apply_plan(
                    loser_view, apply_options, loser_apply).ok &&
                    loser_apply.entries.size() == 1U &&
                    loser_apply.entries.front().local_action ==
                        SyncLocalApplyAction::PreserveConflictCopy,
                "losing peer must compile to one conflict-preservation transition",
                checks);
        const std::string loser_device = loser_view.local_device_id;
        const std::string expected_conflict_suffix =
            ".anonsync-conflict-" + loser_device + "-" +
            loser_plan.conflict_set_id;
        require(loser_apply.entries.front().absolute_conflict_copy_path.ends_with(
                    expected_conflict_suffix),
                "conflict artifact path must identify the local losing publisher and retain the full conflict identity",
                checks);

        // After the complementary first round, both primaries are the same
        // winner; the loser has one normal conflict artifact. Disseminating
        // that ordinary artifact by set union is duplicate- and order-
        // insensitive and yields equal states.
        AbstractReplica winner_state{
            winner_plan.local_version_digest, {}};
        AbstractReplica loser_state{
            winner_plan.local_version_digest,
            {loser_plan.local_version_digest}};
        require(winner_state.primary_version_digest ==
                    loser_state.primary_version_digest,
                "complementary first-round plans must converge the primary version",
                checks);
        winner_state.conflict_version_digests.insert(
            loser_plan.local_version_digest);
        winner_state.conflict_version_digests.insert(
            loser_plan.local_version_digest);
        loser_state.primary_version_digest =
            winner_plan.local_version_digest;
        require(winner_state == loser_state,
                "duplicate ordinary conflict-artifact delivery must converge both abstract replicas",
                checks);

        const SyncManifestEntry charlie =
            file_entry(folder, "device-charlie", path, 'c', 1);
        const std::array<SyncManifestEntry, 3> generated_files{
            alpha, bravo, charlie};
        std::set<std::string> all_file_digests;
        for (const SyncManifestEntry& entry : generated_files) {
            all_file_digests.insert(sync_manifest_entry_version_digest(entry));
        }
        require(all_file_digests.size() == generated_files.size(),
                "generated file histories require three distinct versions",
                checks);
        const std::string expected_file_winner = *all_file_digests.rbegin();
        std::set<std::string> expected_file_losers = all_file_digests;
        expected_file_losers.erase(expected_file_winner);

        std::array<std::size_t, 3> permutation{0U, 1U, 2U};
        std::size_t file_histories_checked = 0U;
        do {
            const FoldedConflictHistory folded =
                fold_conflict_history_or_throw({
                    generated_files[permutation[0]],
                    generated_files[permutation[1]],
                    generated_files[permutation[2]],
                });
            require(sync_manifest_entry_version_digest(folded.primary) ==
                        expected_file_winner &&
                    folded.preserved_file_versions == expected_file_losers,
                    "every three-file delivery order must choose one primary and preserve both losers",
                    checks);
            ++file_histories_checked;
        } while (std::next_permutation(permutation.begin(), permutation.end()));
        require(file_histories_checked == 6U,
                "three-file convergence oracle must cover every delivery permutation",
                checks);

        const SyncManifestEntry generated_delete = tombstone_entry(
            folder, "device-charlie", path, 4);
        const std::array<SyncManifestEntry, 3> mixed_values{
            alpha, bravo, generated_delete};
        const std::string expected_delete_winner =
            sync_manifest_entry_version_digest(generated_delete);
        const std::set<std::string> expected_preserved_files{
            sync_manifest_entry_version_digest(alpha),
            sync_manifest_entry_version_digest(bravo),
        };
        permutation = {0U, 1U, 2U};
        std::size_t mixed_histories_checked = 0U;
        do {
            const FoldedConflictHistory folded =
                fold_conflict_history_or_throw({
                    mixed_values[permutation[0]],
                    mixed_values[permutation[1]],
                    mixed_values[permutation[2]],
                });
            require(sync_manifest_entry_version_digest(folded.primary) ==
                        expected_delete_winner &&
                    folded.primary.kind == SyncManifestEntryKind::Tombstone &&
                    folded.preserved_file_versions == expected_preserved_files,
                    "every file/file/delete order must retain both files and converge on deletion",
                    checks);
            ++mixed_histories_checked;
        } while (std::next_permutation(permutation.begin(), permutation.end()));
        require(mixed_histories_checked == 6U,
                "mixed convergence oracle must cover every delivery permutation",
                checks);

        const std::array<SyncManifestEntry, 3> generated_tombstones{
            tombstone_entry(folder, "device-alpha", path, 5),
            tombstone_entry(folder, "device-bravo", path, 6),
            tombstone_entry(folder, "device-charlie", path, 7),
        };
        std::string expected_tombstone_winner;
        for (const SyncManifestEntry& entry : generated_tombstones) {
            expected_tombstone_winner = std::max(
                expected_tombstone_winner,
                sync_manifest_entry_version_digest(entry));
        }
        permutation = {0U, 1U, 2U};
        std::size_t tombstone_histories_checked = 0U;
        do {
            const FoldedConflictHistory folded =
                fold_conflict_history_or_throw({
                    generated_tombstones[permutation[0]],
                    generated_tombstones[permutation[1]],
                    generated_tombstones[permutation[2]],
                });
            require(sync_manifest_entry_version_digest(folded.primary) ==
                        expected_tombstone_winner &&
                    folded.primary.kind == SyncManifestEntryKind::Tombstone &&
                    folded.preserved_file_versions.empty(),
                    "every tombstone delivery order must converge without fabricating file artifacts",
                    checks);
            ++tombstone_histories_checked;
        } while (std::next_permutation(permutation.begin(), permutation.end()));
        require(tombstone_histories_checked == 6U,
                "tombstone convergence oracle must cover every delivery permutation",
                checks);

        const SyncManifestEntry delete_bravo = tombstone_entry(
            folder, "device-bravo", path, 2);
        SyncManifestDiffPlan file_delete;
        SyncManifestDiffPlan delete_file;
        require(build_sync_manifest_diff_plan(
                    alpha_manifest,
                    manifest(folder, "device-bravo", 2, delete_bravo),
                    file_delete).ok &&
                    build_sync_manifest_diff_plan(
                    manifest(folder, "device-bravo", 2, delete_bravo),
                    alpha_manifest,
                    delete_file).ok,
                "both file/delete orientations must build", checks);
        require(file_delete.entries.front().action ==
                    SyncPlanAction::RecordConflict &&
                    delete_file.entries.front().action ==
                    SyncPlanAction::PublishLocalTombstone,
                "tombstone must win while the file-owning peer preserves bytes",
                checks);

        const SyncManifestEntry delete_alpha = tombstone_entry(
            folder, "device-alpha", path, 3);
        SyncManifestDiffPlan tombstone_forward;
        SyncManifestDiffPlan tombstone_reverse;
        require(build_sync_manifest_diff_plan(
                    manifest(folder, "device-alpha", 3, delete_alpha),
                    manifest(folder, "device-bravo", 2, delete_bravo),
                    tombstone_forward).ok &&
                    build_sync_manifest_diff_plan(
                    manifest(folder, "device-bravo", 2, delete_bravo),
                    manifest(folder, "device-alpha", 3, delete_alpha),
                    tombstone_reverse).ok,
                "both tombstone/tombstone orientations must build", checks);
        const bool forward_publish =
            tombstone_forward.entries.front().action ==
            SyncPlanAction::PublishLocalTombstone;
        const bool reverse_publish =
            tombstone_reverse.entries.front().action ==
            SyncPlanAction::PublishLocalTombstone;
        const bool forward_applies =
            tombstone_forward.entries.front().action ==
            SyncPlanAction::ApplyRemoteTombstone;
        const bool reverse_applies =
            tombstone_reverse.entries.front().action ==
            SyncPlanAction::ApplyRemoteTombstone;
        require(forward_publish != reverse_publish &&
                    forward_applies != reverse_applies &&
                    forward_publish != forward_applies,
                "tombstone/tombstone conflicts must choose one winner without inventing file-copy work",
                checks);

        fs::remove_all(root, ec);
        fs::remove_all(staging, ec);
        std::cout << "sync manifest conflict convergence tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "sync manifest conflict convergence tests failed: "
                  << e.what() << '\n';
        return 1;
    }
}
