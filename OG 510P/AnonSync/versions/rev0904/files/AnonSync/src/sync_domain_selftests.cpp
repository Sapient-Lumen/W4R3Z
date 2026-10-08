#include "anonsync_core.hpp"
#include "anonsync_selftest_api.hpp"
#include "anonsync_core_internal.hpp"
#include "sync_sqlite_support.hpp"
#include "sync_sqlite_runtime.hpp"
#include "sync_peer_ingress_reconciliation.hpp"
#include "sync_domain_test_access.hpp"
#include "sync_process_identity_observation.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <chrono>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <system_error>
#include <type_traits>
#include <utility>

#include <sqlite3.h>

#include "persistence/peer_ingress_connection_profile.hpp"

#if !defined(_WIN32)
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace fs = std::filesystem;

namespace {

template <typename Unsigned>
long long checked_cli_integer_for_selftest(Unsigned value, const std::string& label) {
    static_assert(std::is_integral_v<Unsigned> && std::is_unsigned_v<Unsigned>);
    const auto max_value = static_cast<std::uintmax_t>(std::numeric_limits<long long>::max());
    if (static_cast<std::uintmax_t>(value) > max_value) {
        throw std::runtime_error(label + " exceeds the signed CLI integer range");
    }
    return static_cast<long long>(value);
}

std::string u64_string(std::uint64_t value) {
    return std::to_string(value);
}

SyncProcessIdentityObservation recycled_process_identity_fixture_or_throw() {
    SyncProcessIdentityObservation observation =
        current_sync_process_identity_observation_or_throw();
    if (observation.start_token.empty()) {
        return observation;
    }
    char& last = observation.start_token.back();
    last = last == '9' ? '8' : static_cast<char>(last + 1);
    validate_sync_process_identity_observation_or_throw(observation);
    return observation;
}

bool same_chunk_range(const SyncChunkRange& left, const SyncChunkRange& right) {
    return left.offset == right.offset &&
           left.length == right.length &&
           left.sha256 == right.sha256;
}

const SyncManifestEntry* find_manifest_entry_by_path(
    const SyncFolderManifest& manifest,
    const NormalizedSyncPath& path) {
    const auto it = std::lower_bound(
        manifest.entries.begin(),
        manifest.entries.end(),
        path.value,
        [](const SyncManifestEntry& entry, const std::string& value) {
            return entry.path.value < value;
        });
    if (it == manifest.entries.end() || it->path.value != path.value) return nullptr;
    return &(*it);
}

const SyncLocalApplyPlanEntry* find_apply_entry_by_path(
    const SyncLocalApplyPlan& plan,
    const NormalizedSyncPath& path) {
    const auto it = std::find_if(
        plan.entries.begin(),
        plan.entries.end(),
        [&](const SyncLocalApplyPlanEntry& entry) {
            return entry.path.value == path.value;
        });
    return it == plan.entries.end() ? nullptr : &(*it);
}

void sqlite_backup_file_or_throw(
    const fs::path& source_path,
    const fs::path& destination_path,
    const std::string& label) {
    SyncSqliteDb source;
    SyncSqliteDb destination;
    int source_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
    int destination_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    source_flags |= SQLITE_OPEN_NOFOLLOW;
    destination_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    if (::anonsync::persistence::open_verified_sqlite_database(
            source_path.string().c_str(), source.db.out(), source_flags, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            source.db, label + " could not open sqlite backup source"));
    }
    if (::anonsync::persistence::open_verified_sqlite_database(
            destination_path.string().c_str(), destination.db.out(), destination_flags, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            destination.db, label + " could not open sqlite backup destination"));
    }
    sqlite3_backup* backup = sqlite3_backup_init(destination.db, "main", source.db, "main");
    if (backup == nullptr) {
        throw std::runtime_error(sqlite_error_message(
            destination.db, label + " could not initialize sqlite backup"));
    }
    const int step_rc = sqlite3_backup_step(backup, -1);
    const int finish_rc = sqlite3_backup_finish(backup);
    if (finish_rc != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            destination.db, label + " could not finish sqlite backup"));
    }
    if (step_rc != SQLITE_DONE) {
        throw std::runtime_error(label + " sqlite backup did not copy all pages");
    }
}

struct SyncSidecarReviewEventMetrics {
    std::uint64_t rows = 0;
    std::uint64_t observations = 0;
    std::uint64_t missing_sidecar_rows = 0;
    std::uint64_t tampered_sidecar_rows = 0;
    std::uint64_t staged_bytes_mismatch_rows = 0;
};

SyncSidecarReviewEventMetrics sqlite_sidecar_review_event_metrics_for_session_or_throw(
    const fs::path& sqlite_path,
    const std::string& session_id,
    const std::string& label) {
    SyncSqliteDb handle;
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    if (::anonsync::persistence::open_verified_sqlite_database(
            sqlite_path.string().c_str(), handle.db.out(), flags, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            handle.db, label + " could not open sqlite database"));
    }
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        handle.db,
        "SELECT COUNT(*), COALESCE(SUM(observations),0), "
        "COALESCE(SUM(CASE WHEN review_category='missing-sidecar' THEN 1 ELSE 0 END),0), "
        "COALESCE(SUM(CASE WHEN review_category='tampered-sidecar' THEN 1 ELSE 0 END),0), "
        "COALESCE(SUM(CASE WHEN review_category='staged-bytes-mismatch' THEN 1 ELSE 0 END),0) "
        "FROM sync_session_bound_peer_sidecar_review_events WHERE session_id=?;",
        label + " prepare review event metrics");
    sqlite_bind_text_or_throw(stmt.stmt, 1, session_id, label + " session");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) {
        throw std::runtime_error(label + ": review event metrics returned no row");
    }
    SyncSidecarReviewEventMetrics out;
    out.rows = sqlite_column_u64_or_throw(stmt.stmt, 0, label + " rows");
    out.observations = sqlite_column_u64_or_throw(stmt.stmt, 1, label + " observations");
    out.missing_sidecar_rows = sqlite_column_u64_or_throw(
        stmt.stmt, 2, label + " missing sidecar rows");
    out.tampered_sidecar_rows = sqlite_column_u64_or_throw(
        stmt.stmt, 3, label + " tampered sidecar rows");
    out.staged_bytes_mismatch_rows = sqlite_column_u64_or_throw(
        stmt.stmt, 4, label + " staged bytes mismatch rows");
    return out;
}

}  // namespace

int run_sync_domain_model_selftest() {
    int passed = 0;
    int failed = 0;
    auto require = [&](bool condition, const std::string& message) {
        if (!condition) throw std::runtime_error(message);
        ++passed;
    };
    auto require_invalid_path = [&](const std::string& path, const std::string& label) {
        NormalizedSyncPath out;
        SyncValidationResult result = normalize_sync_relative_path(path, out);
        if (result.ok) throw std::runtime_error("path unexpectedly accepted: " + label);
        ++passed;
    };

    try {
        NormalizedSyncPath path;
        SyncValidationResult normalized = normalize_sync_relative_path("docs/report.txt", path);
        require(normalized.ok && path.value == "docs/report.txt", "portable relative path accepted and preserved");
        require_invalid_path("/etc/passwd", "absolute path");
        require_invalid_path("folder/../secret.txt", "dot segment");
        require_invalid_path("folder//secret.txt", "empty component");
        require_invalid_path("folder\\secret.txt", "backslash path");
        require_invalid_path("aux/report.txt", "reserved device component");
        require_invalid_path("folder/name:.txt", "portable-invalid colon");
        require_invalid_path(std::string("folder/") + std::string("\xc0\xaf", 2), "invalid UTF-8 path");
        require_invalid_path(std::string("folder/") + std::string("\xc1\x80", 2), "overlong two-byte UTF-8 path");

        const std::string hash_a(64, 'a');
        const std::string hash_b(64, 'b');
        const std::string hash_c(64, 'c');
        const std::string hash_d(64, 'd');
        const std::string hash_e(64, 'e');
        const std::string hash_f(64, 'f');
        const auto selftest_ticks = std::chrono::high_resolution_clock::now().time_since_epoch().count();
        run_sync_peer_ingress_lifecycle_selftests(require);
        SyncManifestEntry file;
        file.folder_id = "folder-alpha";
        file.device_id = "device-alpha";
        file.path = path;
        file.kind = SyncManifestEntryKind::File;
        file.size_bytes = 12;
        file.content_sha256 = hash_a;
        file.chunks = {{0, 5, hash_b}, {5, 7, hash_c}};
        file.lineage = {{"device-alpha", 1}};
        SyncValidationResult valid_file = validate_sync_manifest_entry(file);
        require(valid_file.ok, "valid file manifest entry accepted");

        SyncManifestEntry gap = file;
        gap.chunks[1].offset = 6;
        require(!validate_sync_manifest_entry(gap).ok, "chunk gap rejected");

        SyncManifestEntry uppercase_hash = file;
        uppercase_hash.content_sha256[0] = 'A';
        require(!validate_sync_manifest_entry(uppercase_hash).ok, "uppercase content hash rejected");

        SyncManifestEntry unsorted_lineage = file;
        unsorted_lineage.lineage = {{"device-zulu", 1}, {"device-alpha", 1}};
        require(!validate_sync_manifest_entry(unsorted_lineage).ok, "unsorted lineage rejected");

        SyncManifestEntry tombstone;
        tombstone.folder_id = "folder-alpha";
        tombstone.device_id = "device-alpha";
        tombstone.path = path;
        tombstone.kind = SyncManifestEntryKind::Tombstone;
        tombstone.lineage = {{"device-alpha", 2}};
        require(validate_sync_manifest_entry(tombstone).ok, "valid tombstone manifest entry accepted");
        tombstone.content_sha256 = hash_a;
        require(!validate_sync_manifest_entry(tombstone).ok, "tombstone content hash rejected");
        tombstone.content_sha256.clear();

        NormalizedSyncPath media_path;
        require(normalize_sync_relative_path("media/photo.jpg", media_path).ok, "second portable relative path accepted");
        SyncManifestEntry photo = file;
        photo.path = media_path;
        photo.size_bytes = 3;
        photo.content_sha256 = hash_b;
        photo.chunks = {{0, 3, hash_c}};
        photo.lineage = {{"device-alpha", 2}};

        SyncFolderManifest manifest;
        manifest.folder_id = "folder-alpha";
        manifest.device_id = "device-alpha";
        manifest.manifest_counter = 7;
        manifest.entries = {file, photo};
        require(validate_sync_folder_manifest(manifest).ok, "valid sorted folder manifest accepted");

        SyncFolderManifest duplicate_path = manifest;
        duplicate_path.entries[1].path = file.path;
        require(!validate_sync_folder_manifest(duplicate_path).ok, "duplicate manifest path rejected");

        SyncFolderManifest unsorted_manifest = manifest;
        std::swap(unsorted_manifest.entries[0], unsorted_manifest.entries[1]);
        require(!validate_sync_folder_manifest(unsorted_manifest).ok, "unsorted manifest paths rejected");

        SyncFolderManifest mismatched_folder = manifest;
        mismatched_folder.entries[0].folder_id = "folder-bravo";
        require(!validate_sync_folder_manifest(mismatched_folder).ok, "manifest entry folder mismatch rejected");

        const std::string manifest_digest = sync_folder_manifest_digest(manifest);
        const std::string manifest_digest_repeat = sync_folder_manifest_digest(manifest);
        SyncFolderManifest next_manifest = manifest;
        next_manifest.manifest_counter = 8;
        require(manifest_digest == manifest_digest_repeat && manifest_digest.size() == 64, "folder manifest digest is deterministic sha256");
        require(manifest_digest != sync_folder_manifest_digest(next_manifest), "folder manifest digest binds manifest counter");



        auto publish_entry_as = [](SyncManifestEntry entry, const std::string& publisher_device_id) {
            entry.device_id = publisher_device_id;
            return entry;
        };
        auto folder_manifest = [](const std::string& folder_id,
                                  const std::string& device_id,
                                  std::uint64_t counter,
                                  std::vector<SyncManifestEntry> entries) {
            SyncFolderManifest result;
            result.folder_id = folder_id;
            result.device_id = device_id;
            result.manifest_counter = counter;
            result.entries = std::move(entries);
            return result;
        };

        SyncManifestEntry remote_file = publish_entry_as(file, "device-bravo");
        SyncManifestEntry remote_photo = publish_entry_as(photo, "device-bravo");
        SyncFolderManifest remote_same = folder_manifest("folder-alpha", "device-bravo", 5, {remote_file, remote_photo});
        SyncManifestDiffPlan same_plan;
        SyncValidationResult same_plan_result = build_sync_manifest_diff_plan(manifest, remote_same, same_plan);
        require(same_plan_result.ok, "manifest diff accepts same folder across different devices");
        require(same_plan.folder_id == "folder-alpha" &&
                same_plan.local_device_id == "device-alpha" &&
                same_plan.remote_device_id == "device-bravo" &&
                same_plan.local_manifest_digest.size() == 64 &&
                same_plan.remote_manifest_digest.size() == 64,
                "manifest diff plan binds folder, peer devices, and manifest digests");
        require(same_plan.entries.size() == 2 &&
                same_plan.entries[0].action == SyncPlanAction::Noop &&
                same_plan.entries[1].action == SyncPlanAction::Noop,
                "manifest diff no-ops already synchronized versions");
        require(same_plan.entries[0].local_entry_digest != same_plan.entries[0].remote_entry_digest &&
                same_plan.entries[0].local_version_digest == same_plan.entries[0].remote_version_digest,
                "manifest diff compares publisher-neutral version digests, not publisher-bound entry digests");

        SyncManifestEntry remote_newer_file = remote_file;
        remote_newer_file.size_bytes = 9;
        remote_newer_file.content_sha256 = hash_d;
        remote_newer_file.chunks = {{0, 5, hash_b}, {5, 4, hash_e}};
        remote_newer_file.lineage = {{"device-alpha", 1}, {"device-bravo", 1}};
        SyncFolderManifest remote_newer_manifest = folder_manifest("folder-alpha", "device-bravo", 6, {remote_newer_file, remote_photo});
        SyncManifestDiffPlan remote_newer_plan;
        require(build_sync_manifest_diff_plan(manifest, remote_newer_manifest, remote_newer_plan).ok,
                "manifest diff accepts a remote-newer version vector");
        require(remote_newer_plan.entries[0].path.value == "docs/report.txt" &&
                remote_newer_plan.entries[0].action == SyncPlanAction::FetchRemoteFile &&
                remote_newer_plan.entries[0].lineage_relation == SyncLineageRelation::RemoteNewer,
                "manifest diff plans fetch for remote-newer file version");
        require(remote_newer_plan.entries[0].needed_chunks.size() == 1 &&
                remote_newer_plan.entries[0].needed_chunks[0].offset == 5 &&
                remote_newer_plan.entries[0].needed_chunks[0].length == 4 &&
                remote_newer_plan.entries[0].needed_chunks[0].sha256 == hash_e,
                "manifest diff requests only chunks unavailable by local hash and length");

        SyncManifestEntry local_newer_file = file;
        local_newer_file.size_bytes = 12;
        local_newer_file.content_sha256 = hash_e;
        local_newer_file.chunks = {{0, 12, hash_f}};
        local_newer_file.lineage = {{"device-alpha", 2}};
        SyncFolderManifest local_newer_manifest = folder_manifest("folder-alpha", "device-alpha", 8, {local_newer_file, photo});
        SyncManifestDiffPlan local_newer_plan;
        require(build_sync_manifest_diff_plan(local_newer_manifest, remote_same, local_newer_plan).ok &&
                local_newer_plan.entries[0].action == SyncPlanAction::PublishLocalFile &&
                local_newer_plan.entries[0].lineage_relation == SyncLineageRelation::LocalNewer,
                "manifest diff plans publish for local-newer file version");

        SyncManifestEntry remote_delete = remote_file;
        remote_delete.kind = SyncManifestEntryKind::Tombstone;
        remote_delete.size_bytes = 0;
        remote_delete.content_sha256.clear();
        remote_delete.chunks.clear();
        remote_delete.lineage = {{"device-alpha", 1}, {"device-bravo", 2}};
        SyncFolderManifest remote_delete_manifest = folder_manifest("folder-alpha", "device-bravo", 7, {remote_delete, remote_photo});
        SyncManifestDiffPlan remote_delete_plan;
        require(build_sync_manifest_diff_plan(manifest, remote_delete_manifest, remote_delete_plan).ok &&
                remote_delete_plan.entries[0].action == SyncPlanAction::ApplyRemoteTombstone &&
                remote_delete_plan.entries[0].needed_chunks.empty(),
                "manifest diff plans tombstone application without chunk transfer");

        SyncManifestEntry local_concurrent_file = file;
        local_concurrent_file.content_sha256 = hash_d;
        local_concurrent_file.chunks = {{0, 12, hash_e}};
        local_concurrent_file.lineage = {{"device-alpha", 2}};
        SyncManifestEntry remote_concurrent_file = remote_file;
        remote_concurrent_file.content_sha256 = hash_e;
        remote_concurrent_file.chunks = {{0, 12, hash_f}};
        remote_concurrent_file.lineage = {{"device-bravo", 2}};
        SyncFolderManifest local_concurrent_manifest = folder_manifest("folder-alpha", "device-alpha", 9, {local_concurrent_file});
        SyncFolderManifest remote_concurrent_manifest = folder_manifest("folder-alpha", "device-bravo", 9, {remote_concurrent_file});
        SyncManifestDiffPlan alpha_conflict_view;
        SyncManifestDiffPlan bravo_conflict_view;
        require(build_sync_manifest_diff_plan(local_concurrent_manifest,
                                              remote_concurrent_manifest,
                                              alpha_conflict_view).ok &&
                build_sync_manifest_diff_plan(remote_concurrent_manifest,
                                              local_concurrent_manifest,
                                              bravo_conflict_view).ok &&
                alpha_conflict_view.entries.size() == 1 &&
                bravo_conflict_view.entries.size() == 1,
                "manifest diff builds both orientations of a concurrent vector-clock conflict");
        const bool alpha_preserves_conflict =
            alpha_conflict_view.entries[0].action == SyncPlanAction::RecordConflict;
        const bool bravo_preserves_conflict =
            bravo_conflict_view.entries[0].action == SyncPlanAction::RecordConflict;
        require(alpha_preserves_conflict != bravo_preserves_conflict &&
                (alpha_conflict_view.entries[0].action == SyncPlanAction::PublishLocalFile) !=
                    (bravo_conflict_view.entries[0].action == SyncPlanAction::PublishLocalFile) &&
                alpha_conflict_view.entries[0].lineage_relation == SyncLineageRelation::Concurrent &&
                bravo_conflict_view.entries[0].lineage_relation == SyncLineageRelation::Concurrent,
                "concurrent vector-clock edits choose one deterministic publisher and one preserving loser");
        const SyncManifestDiffPlan& conflict_plan = alpha_preserves_conflict
            ? alpha_conflict_view
            : bravo_conflict_view;
        const SyncManifestDiffPlan& conflict_winner_plan = alpha_preserves_conflict
            ? bravo_conflict_view
            : alpha_conflict_view;
        require(conflict_plan.entries[0].conflict_set_id.rfind("conflict-", 0) == 0 &&
                conflict_winner_plan.entries[0].conflict_set_id.empty() &&
                conflict_plan.entries[0].local_version_digest ==
                    conflict_winner_plan.entries[0].remote_version_digest &&
                conflict_plan.entries[0].remote_version_digest ==
                    conflict_winner_plan.entries[0].local_version_digest,
                "both orientations agree on the exact concurrent winner and conflict-set ownership");
        require(conflict_plan.entries[0].needed_chunks.size() == 1,
                "manifest diff keeps winner chunk needs for conflict materialization");

        SyncManifestEntry remote_same_lineage_divergent = remote_file;
        remote_same_lineage_divergent.content_sha256 = hash_f;
        remote_same_lineage_divergent.chunks = {{0, 12, hash_e}};
        remote_same_lineage_divergent.lineage = {{"device-alpha", 1}};
        SyncFolderManifest remote_equal_divergent_manifest = folder_manifest("folder-alpha", "device-bravo", 10, {remote_same_lineage_divergent});
        const SyncFolderManifest equal_lineage_local_manifest =
            folder_manifest("folder-alpha", "device-alpha", 10, {file});
        SyncManifestDiffPlan equal_lineage_alpha_view;
        equal_lineage_alpha_view.folder_id = "must-be-cleared";
        equal_lineage_alpha_view.entries.push_back(SyncManifestPlanEntry{});
        SyncManifestDiffPlan equal_lineage_bravo_view = equal_lineage_alpha_view;
        const SyncValidationResult equal_alpha_result =
            build_sync_manifest_diff_plan(equal_lineage_local_manifest,
                                          remote_equal_divergent_manifest,
                                          equal_lineage_alpha_view);
        const SyncValidationResult equal_bravo_result =
            build_sync_manifest_diff_plan(remote_equal_divergent_manifest,
                                          equal_lineage_local_manifest,
                                          equal_lineage_bravo_view);
        require(!equal_alpha_result.ok && !equal_bravo_result.ok &&
                equal_alpha_result.reason.find("counter reuse or equivocation") != std::string::npos &&
                equal_bravo_result.reason.find("counter reuse or equivocation") != std::string::npos &&
                equal_lineage_alpha_view.folder_id.empty() &&
                equal_lineage_bravo_view.folder_id.empty() &&
                equal_lineage_alpha_view.entries.empty() &&
                equal_lineage_bravo_view.entries.empty(),
                "equal-lineage divergent content fails closed in both orientations without leaking a partial plan");

        SyncFolderManifest empty_local = folder_manifest("folder-alpha", "device-alpha", 1, {});
        SyncManifestDiffPlan remote_only_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 2, {remote_file}), remote_only_plan).ok &&
                remote_only_plan.entries.size() == 1 &&
                remote_only_plan.entries[0].action == SyncPlanAction::FetchRemoteFile &&
                remote_only_plan.entries[0].needed_chunks.size() == remote_file.chunks.size(),
                "manifest diff fetches every chunk for a remote-only file");

        NormalizedSyncPath deleted_path;
        require(normalize_sync_relative_path("old/deleted.txt", deleted_path).ok, "deleted tombstone path accepted");
        SyncManifestEntry local_delete;
        local_delete.folder_id = "folder-alpha";
        local_delete.device_id = "device-alpha";
        local_delete.path = deleted_path;
        local_delete.kind = SyncManifestEntryKind::Tombstone;
        local_delete.lineage = {{"device-alpha", 2}};
        SyncManifestDiffPlan local_tombstone_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 11, {local_delete}),
                                              folder_manifest("folder-alpha", "device-bravo", 11, {}),
                                              local_tombstone_plan).ok &&
                local_tombstone_plan.entries[0].action == SyncPlanAction::PublishLocalTombstone,
                "manifest diff publishes local-only tombstones to peers");

        const fs::path apply_root = fs::temp_directory_path() / ("anonsync-sync-apply-selftest-" + std::to_string(selftest_ticks));
        const fs::path apply_staging_root = fs::temp_directory_path() / ("anonsync-sync-stage-selftest-" + std::to_string(selftest_ticks));
        std::error_code apply_cleanup_ec;
        fs::remove_all(apply_root, apply_cleanup_ec);
        fs::remove_all(apply_staging_root, apply_cleanup_ec);
        fs::create_directories(apply_root, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not create local apply selftest root: " + apply_cleanup_ec.message());
        SyncLocalApplyOptions apply_options;
        apply_options.local_root_path = apply_root.string();
        apply_options.staging_root_path = apply_staging_root.string();

        SyncLocalApplyPlan remote_file_apply_plan;
        require(build_sync_local_apply_plan(remote_newer_plan, apply_options, remote_file_apply_plan).ok &&
                remote_file_apply_plan.folder_id == "folder-alpha" &&
                remote_file_apply_plan.local_device_id == "device-alpha" &&
                remote_file_apply_plan.remote_device_id == "device-bravo" &&
                remote_file_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan stages remote-newer files under a separate staging root");
        require(remote_file_apply_plan.entries[0].absolute_target_path.find("docs/report.txt") != std::string::npos &&
                remote_file_apply_plan.entries[0].absolute_staging_path.find("docs/report.txt.remote-") != std::string::npos &&
                remote_file_apply_plan.entries[0].absolute_staging_path.find(remote_newer_plan.entries[0].remote_entry_digest.substr(0, 16)) != std::string::npos &&
                remote_file_apply_plan.entries[0].needed_chunks.size() == 1,
                "local apply plan binds target path, staging path, and chunk needs for fetches");
        const std::string remote_apply_key = remote_file_apply_plan.entries[0].idempotency_key;
        SyncLocalApplyPlan remote_file_apply_plan_repeat;
        require(build_sync_local_apply_plan(remote_newer_plan, apply_options, remote_file_apply_plan_repeat).ok &&
                remote_apply_key == remote_file_apply_plan_repeat.entries[0].idempotency_key &&
                remote_apply_key.rfind("sync-local-apply:v1:", 0) == 0,
                "local apply plan emits deterministic idempotency keys");

        SyncLocalApplyPlan remote_tombstone_apply_plan;
        require(build_sync_local_apply_plan(remote_delete_plan, apply_options, remote_tombstone_apply_plan).ok &&
                remote_tombstone_apply_plan.entries[0].local_action == SyncLocalApplyAction::DeleteLocalPath &&
                remote_tombstone_apply_plan.entries[0].absolute_staging_path.empty() &&
                remote_tombstone_apply_plan.entries[0].absolute_conflict_copy_path.empty(),
                "local apply plan maps remote tombstones to local delete intents without staging");

        SyncLocalApplyPlan conflict_apply_plan;
        require(build_sync_local_apply_plan(conflict_plan, apply_options, conflict_apply_plan).ok &&
                conflict_apply_plan.entries[0].local_action == SyncLocalApplyAction::PreserveConflictCopy &&
                conflict_apply_plan.entries[0].absolute_conflict_copy_path.ends_with(
                    ".anonsync-conflict-" + conflict_plan.local_device_id + "-" +
                    conflict_plan.entries[0].conflict_set_id) &&
                conflict_apply_plan.entries[0].absolute_staging_path.find("docs/report.txt.remote-") != std::string::npos &&
                conflict_apply_plan.entries[0].needed_chunks.size() == 1,
                "local apply plan preserves local conflicts and stages the remote conflict version");

        SyncLocalApplyPlan outbound_apply_plan;
        require(build_sync_local_apply_plan(local_newer_plan, apply_options, outbound_apply_plan).ok &&
                outbound_apply_plan.entries[0].local_action == SyncLocalApplyAction::AdvertiseLocalFile &&
                outbound_apply_plan.entries[0].absolute_staging_path.empty(),
                "local apply plan marks local-newer files as outbound peer advertisements");

        auto write_binary_fixture = [](const fs::path& p, const std::string& body) {
            std::error_code create_ec;
            fs::create_directories(p.parent_path(), create_ec);
            if (create_ec) throw std::runtime_error("could not create binary fixture parent: " + create_ec.message());
            std::ofstream out(p, std::ios::binary);
            if (!out) throw std::runtime_error("could not write binary fixture: " + p.string());
            out.write(body.data(), static_cast<std::streamsize>(body.size()));
            if (!out) throw std::runtime_error("could not finish binary fixture write: " + p.string());
        };
        auto read_binary_fixture = [](const fs::path& p) {
            std::ifstream in(p, std::ios::binary);
            if (!in) throw std::runtime_error("could not read binary fixture: " + p.string());
            std::ostringstream body;
            body << in.rdbuf();
            return body.str();
        };
        auto remote_file_entry_for_body = [&](const std::string& raw_path,
                                              const std::string& body,
                                              std::uint64_t counter) {
            NormalizedSyncPath normalized_path;
            SyncValidationResult path_ok = normalize_sync_relative_path(raw_path, normalized_path);
            if (!path_ok.ok) throw std::runtime_error("selftest remote path invalid: " + path_ok.reason);
            SyncManifestEntry entry;
            entry.folder_id = "folder-alpha";
            entry.device_id = "device-bravo";
            entry.path = normalized_path;
            entry.kind = SyncManifestEntryKind::File;
            entry.size_bytes = static_cast<std::uint64_t>(body.size());
            entry.content_sha256 = sha256_hex(body);
            entry.lineage = {{"device-bravo", counter}};
            std::uint64_t offset = 0;
            constexpr std::uint64_t kSelftestChunkSize = 5;
            while (offset < entry.size_bytes) {
                const std::uint64_t length = std::min<std::uint64_t>(kSelftestChunkSize, entry.size_bytes - offset);
                entry.chunks.push_back(SyncChunkRange{offset, length, sha256_hex(body.substr(static_cast<size_t>(offset), static_cast<size_t>(length)))});
                offset += length;
            }
            return entry;
        };

        auto orient_remote_file_as_deterministic_conflict_winner_or_throw = [](
            const SyncManifestEntry& local_file,
            SyncManifestEntry& remote_file) {
            if (local_file.kind != SyncManifestEntryKind::File ||
                remote_file.kind != SyncManifestEntryKind::File ||
                remote_file.lineage.empty()) {
                throw std::runtime_error(
                    "conflict selftest winner orientation requires two files and remote lineage");
            }
            constexpr std::size_t kMaximumDigestOrientationAttempts = 4096U;
            for (std::size_t attempt = 0;
                 attempt < kMaximumDigestOrientationAttempts;
                 ++attempt) {
                if (sync_manifest_entry_version_digest(remote_file) >
                    sync_manifest_entry_version_digest(local_file)) {
                    return;
                }
                std::uint64_t& counter = remote_file.lineage.back().counter;
                if (counter == std::numeric_limits<std::uint64_t>::max()) {
                    throw std::runtime_error(
                        "conflict selftest remote lineage counter exhausted");
                }
                ++counter;
            }
            throw std::runtime_error(
                "conflict selftest could not orient remote file as deterministic winner");
        };

        auto chunk_bytes_for_body = [](const std::string& body, const SyncChunkRange& chunk) {
            return body.substr(static_cast<size_t>(chunk.offset), static_cast<size_t>(chunk.length));
        };

        const fs::path fake_source_root = fs::temp_directory_path() / ("anonsync-sync-fake-peer-source-" + std::to_string(selftest_ticks));
        const fs::path fake_destination_root = fs::temp_directory_path() / ("anonsync-sync-fake-peer-destination-" + std::to_string(selftest_ticks));
        const fs::path fake_staging_root = fs::temp_directory_path() / ("anonsync-sync-fake-peer-stage-" + std::to_string(selftest_ticks));
        fs::remove_all(fake_source_root, apply_cleanup_ec);
        fs::remove_all(fake_destination_root, apply_cleanup_ec);
        fs::remove_all(fake_staging_root, apply_cleanup_ec);
        fs::create_directories(fake_source_root, apply_cleanup_ec);
        fs::create_directories(fake_destination_root, apply_cleanup_ec);
        fs::create_directories(fake_staging_root, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not prepare fake peer session roots: " + apply_cleanup_ec.message());
        const std::string fake_session_report = "source peer report alpha bravo charlie";
        const std::string fake_session_media = "0123456789abcdef";
        write_binary_fixture(fake_source_root / "docs/session-report.txt", fake_session_report);
        write_binary_fixture(fake_source_root / "media/session-media.bin", fake_session_media);
        SyncFakePeerFileFetchSessionOptions fake_session_options;
        fake_session_options.source_root_path = fake_source_root.string();
        fake_session_options.destination_root_path = fake_destination_root.string();
        fake_session_options.staging_root_path = fake_staging_root.string();
        fake_session_options.folder_id = "folder-alpha";
        fake_session_options.source_device_id = "device-bravo";
        fake_session_options.destination_device_id = "device-alpha";
        fake_session_options.peer_id = "peer-bravo";
        fake_session_options.peer_session_id = "session-main";
        fake_session_options.source_manifest_counter = 70;
        fake_session_options.destination_manifest_counter = 71;
        fake_session_options.source_lineage_counter = 72;
        fake_session_options.destination_lineage_counter = 73;
        fake_session_options.chunk_size_bytes = 5;
        fake_session_options.max_chunks_per_request = 2;
        fake_session_options.max_chunks_per_peer_round = 1;
        fake_session_options.max_transfer_rounds = 32;
        SyncFakePeerFileFetchSessionResult fake_session_result;
        SyncValidationResult fake_session_run = run_sync_fake_peer_file_fetch_session(fake_session_options, fake_session_result);
        std::uint64_t fake_source_chunk_count = 0;
        for (const auto& entry : fake_session_result.source_manifest.entries) {
            fake_source_chunk_count += static_cast<std::uint64_t>(entry.chunks.size());
        }
        require(fake_session_run.ok &&
                fake_session_result.content_converged &&
                fake_session_result.files_materialized == 2 &&
                fake_session_result.apply_entries_considered == 2,
                "fake peer file-fetch session drives scan, diff, local apply, peer rounds, materialization, and rescan convergence");
        require(fake_session_result.transfer_rounds == fake_source_chunk_count &&
                fake_session_result.chunks_written == fake_source_chunk_count &&
                fake_session_result.receipts_reused == 0 &&
                fake_session_result.files.size() == 2,
                "fake peer file-fetch session exposes receipt-backed chunk and round evidence across files");
        const bool all_fake_session_files_cleaned = std::all_of(fake_session_result.files.begin(),
                                                               fake_session_result.files.end(),
                                                               [](const SyncFakePeerFileFetchSessionFileResult& file_result) {
                                                                   return file_result.staging_artifacts_cleaned &&
                                                                          file_result.cleanup_receipts_removed > 0 &&
                                                                          file_result.cleanup_directories_removed > 0;
                                                               });
        std::error_code fake_staging_empty_ec;
        require(fake_session_result.cleanup_receipts_removed == fake_source_chunk_count &&
                fake_session_result.cleanup_directories_removed >= fake_session_result.files.size() &&
                all_fake_session_files_cleaned &&
                fs::is_empty(fake_staging_root, fake_staging_empty_ec) && !fake_staging_empty_ec,
                "fake peer file-fetch session cleans committed staging receipts and prunes empty staging directories");
        require(read_binary_fixture(fake_destination_root / "docs/session-report.txt") == fake_session_report &&
                read_binary_fixture(fake_destination_root / "media/session-media.bin") == fake_session_media,
                "fake peer file-fetch session materializes exact source bytes into the destination root");
        require(fake_session_result.source_content_digest == fake_session_result.destination_content_digest &&
                fake_session_result.destination_manifest_after.entries.size() == fake_session_result.source_manifest.entries.size(),
                "fake peer file-fetch session proves content-digest convergence independent of scan-time publisher lineage");
        const fs::path fake_session_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(fake_session_checkpoint_db, apply_cleanup_ec);
        SyncSessionCheckpointOptions checkpoint_options;
        checkpoint_options.sqlite_path = fake_session_checkpoint_db.string();
        checkpoint_options.session_id = "session-main";
        SyncSessionCheckpointResult checkpoint_result;
        SyncValidationResult checkpoint_run = persist_sync_fake_peer_session_checkpoint(fake_session_options,
                                                                                        fake_session_result,
                                                                                        checkpoint_options,
                                                                                        checkpoint_result);
        require(checkpoint_run.ok && checkpoint_result.transaction_committed && checkpoint_result.checkpoint_reloaded &&
                checkpoint_result.content_converged &&
                checkpoint_result.file_results_written == fake_session_result.files_materialized &&
                checkpoint_result.apply_intents_written == fake_session_result.apply_entries_considered &&
                checkpoint_result.source_manifest_chunks_written == fake_source_chunk_count &&
                checkpoint_result.chunk_receipts_recorded == fake_source_chunk_count,
                "sync session checkpoint persists fake peer session evidence and reload-verifies durable SQLite rows");
        SyncSessionCheckpointResumeViewOptions resume_options;
        resume_options.sqlite_path = fake_session_checkpoint_db.string();
        resume_options.session_id = "session-main";
        resume_options.source_root_path = fake_source_root.string();
        resume_options.destination_root_path = fake_destination_root.string();
        resume_options.staging_root_path = fake_staging_root.string();
        resume_options.expected_folder_id = "folder-alpha";
        resume_options.expected_source_device_id = "device-bravo";
        resume_options.expected_destination_device_id = "device-alpha";
        resume_options.expected_peer_id = "peer-bravo";
        SyncSessionCheckpointResumeViewResult resume_view;
        SyncValidationResult resume_run = load_sync_session_checkpoint_resume_view(resume_options, resume_view);
        require(resume_run.ok &&
                resume_view.terminal_session_complete &&
                resume_view.materialization_terminal_complete &&
                resume_view.cleanup_terminal_complete &&
                resume_view.all_chunk_receipts_committed_cleaned &&
                resume_view.schema_version == "rev0720-sync-session-checkpoint-v4" &&
                resume_view.schema_version_supported &&
                resume_view.manifest_digest_rows_verified &&
                resume_view.manifest_entry_rows_verified &&
                resume_view.manifest_chunk_rows_verified &&
                resume_view.file_result_aggregates_verified &&
                resume_view.chunk_receipt_totals_verified &&
                resume_view.chunk_receipt_coverage_verified &&
                resume_view.durable_integrity_verified &&
                resume_view.file_results_recorded == fake_session_result.files_materialized &&
                resume_view.apply_intents_recorded == fake_session_result.apply_entries_considered &&
                resume_view.chunk_receipts_recorded == fake_source_chunk_count &&
                resume_view.source_manifest_entry_rows_recorded == resume_view.source_manifest_entries_recorded &&
                resume_view.source_manifest_chunks_recorded == fake_source_chunk_count &&
                resume_view.source_manifest_chunk_rows_recorded == fake_source_chunk_count &&
                resume_view.destination_after_manifest_chunk_rows_recorded == fake_source_chunk_count &&
                resume_view.source_manifest_chunks_without_receipts == 0 &&
                resume_view.chunk_receipts_without_source_manifest_chunks == 0 &&
                resume_view.source_filesystem_verified &&
                resume_view.source_filesystem_entries_checked == resume_view.source_manifest_entry_rows_recorded &&
                resume_view.source_filesystem_file_entries_checked == fake_session_result.files_materialized &&
                resume_view.source_filesystem_missing_paths == 0 &&
                resume_view.source_filesystem_kind_mismatches == 0 &&
                resume_view.source_filesystem_content_mismatches == 0 &&
                resume_view.source_filesystem_drift_paths.empty() &&
                resume_view.destination_filesystem_verified &&
                resume_view.destination_filesystem_entries_checked == resume_view.destination_after_manifest_entry_rows_recorded &&
                resume_view.destination_filesystem_file_entries_checked == fake_session_result.files_materialized &&
                resume_view.destination_filesystem_missing_paths == 0 &&
                resume_view.destination_filesystem_kind_mismatches == 0 &&
                resume_view.destination_filesystem_content_mismatches == 0 &&
                resume_view.destination_filesystem_drift_paths.empty() &&
                resume_view.staging_artifacts_verified &&
                resume_view.staging_artifact_paths_checked == fake_session_result.files_materialized &&
                resume_view.staging_files_present == 0 &&
                resume_view.staging_receipt_directories_present == 0 &&
                resume_view.staging_artifact_kind_mismatches == 0 &&
                resume_view.staging_artifact_paths.empty() &&
                resume_view.files_pending_materialization == 0 &&
                resume_view.files_pending_cleanup == 0 &&
                resume_view.chunk_receipts_pending_cleanup == 0 &&
                resume_view.pending_materialization_paths.empty() &&
                resume_view.pending_cleanup_paths.empty(),
                "sync session checkpoint resume view reloads terminal completion and durable integrity evidence as restart input");
        SyncSessionCheckpointResumeActionPlanOptions action_plan_options;
        action_plan_options.sqlite_path = fake_session_checkpoint_db.string();
        action_plan_options.session_id = "session-main";
        action_plan_options.source_root_path = fake_source_root.string();
        action_plan_options.destination_root_path = fake_destination_root.string();
        action_plan_options.staging_root_path = fake_staging_root.string();
        action_plan_options.expected_folder_id = "folder-alpha";
        action_plan_options.expected_source_device_id = "device-bravo";
        action_plan_options.expected_destination_device_id = "device-alpha";
        action_plan_options.expected_peer_id = "peer-bravo";
        SyncSessionCheckpointResumeActionPlanResult clean_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, clean_action_plan).ok &&
                clean_action_plan.resume_view_loaded &&
                clean_action_plan.durable_integrity_verified &&
                clean_action_plan.source_filesystem_verified &&
                clean_action_plan.files_considered == fake_session_result.files_materialized &&
                clean_action_plan.already_converged_files == fake_session_result.files_materialized &&
                clean_action_plan.materialize_staged_files == 0 &&
                clean_action_plan.resume_transfer_files == 0 &&
                clean_action_plan.repair_committed_staging_files == 0 &&
                clean_action_plan.quarantine_staging_files == 0,
                "sync session checkpoint resume action plan recognizes terminal clean files as already converged");

        NormalizedSyncPath pending_materialize_path;
        require(normalize_sync_relative_path("docs/session-report.txt", pending_materialize_path).ok,
                "sync session checkpoint resume action plan fixture path normalizes");
        const SyncManifestEntry* pending_materialize_entry = find_manifest_entry_by_path(fake_session_result.source_manifest, pending_materialize_path);
        const SyncLocalApplyPlanEntry* pending_materialize_apply = find_apply_entry_by_path(fake_session_result.apply_plan, pending_materialize_path);
        require(pending_materialize_entry != nullptr && pending_materialize_apply != nullptr,
                "sync session checkpoint resume action plan fixture has source and apply evidence");
        const std::string pending_materialize_digest = sync_manifest_entry_digest(*pending_materialize_entry);
        NormalizedSyncPath pending_materialize_staged_relative;
        pending_materialize_staged_relative.value = sync_domain_test_access::remote_staging_relative_path_for_fixture(
            pending_materialize_path,
            pending_materialize_digest,
            "sync session checkpoint resume action plan pending materialization staging path");
        const fs::path pending_materialize_staged_path = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
            fake_staging_root,
            pending_materialize_staged_relative,
            "sync session checkpoint resume action plan pending materialization staged file"));
        write_binary_fixture(pending_materialize_staged_path, fake_session_report);
        for (const auto& chunk : pending_materialize_entry->chunks) {
            const NormalizedSyncPath receipt_relative{sync_domain_test_access::chunk_receipt_relative_path_for_fixture(
                pending_materialize_entry->path,
                pending_materialize_digest,
                chunk,
                "sync session checkpoint resume action plan pending materialization receipt")};
            const fs::path receipt_path = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
                fake_staging_root,
                receipt_relative,
                "sync session checkpoint resume action plan pending materialization receipt path"));
            write_binary_fixture(receipt_path, sync_domain_test_access::chunk_receipt_material_for_fixture(*pending_materialize_entry, *pending_materialize_apply, chunk));
        }
        {
            SyncSqliteDb pending_handle;
            int pending_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            pending_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), pending_handle.db.out(), pending_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(pending_handle.db, "could not reopen checkpoint db for pending materialization action-plan test"));
            }
            sqlite_exec_or_throw(pending_handle.db,
                                 "UPDATE sync_session_file_results SET materialized=0, staging_artifacts_cleaned=0 "
                                 "WHERE session_id='session-main' AND path='docs/session-report.txt';"
                                 "UPDATE sync_session_chunk_receipts SET receipt_state='accepted' "
                                 "WHERE session_id='session-main' AND path='docs/session-report.txt';",
                                 "could not mark checkpoint rows pending for resume action-plan materialization test");
        }
        SyncSessionCheckpointResumeActionPlanResult pending_materialize_action_plan;
        SyncValidationResult pending_materialize_plan_run = plan_sync_session_checkpoint_resume_actions(action_plan_options,
                                                                                                       pending_materialize_action_plan);
        const auto pending_materialize_file = std::find_if(pending_materialize_action_plan.files.begin(),
                                                           pending_materialize_action_plan.files.end(),
                                                           [](const SyncSessionCheckpointResumeActionFilePlan& file_plan) {
                                                               return file_plan.path.value == "docs/session-report.txt";
                                                           });
        require(pending_materialize_plan_run.ok &&
                pending_materialize_action_plan.materialize_staged_files == 1 &&
                pending_materialize_action_plan.already_converged_files == 1 &&
                pending_materialize_file != pending_materialize_action_plan.files.end() &&
                pending_materialize_file->action == SyncSessionCheckpointResumeActionKind::MaterializeStagedFile &&
                pending_materialize_file->staged_file_complete &&
                pending_materialize_file->all_receipts_verified &&
                pending_materialize_file->chunks_to_request.empty(),
                "sync session checkpoint resume action plan classifies complete pending staged evidence as materialize-staged-file");
        const fs::path pending_materialize_target_path = fake_destination_root / "docs/session-report.txt";
        fs::remove(pending_materialize_target_path, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not remove pending materialization target fixture: " + apply_cleanup_ec.message());
        SyncSessionCheckpointResumeActionPlanResult absent_target_materialize_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, absent_target_materialize_action_plan).ok &&
                absent_target_materialize_action_plan.materialize_staged_files == 1,
                "sync session checkpoint resume action plan still materializes complete staged evidence when the destination target is absent");
        SyncSessionCheckpointMaterializeResumeOptions materialize_resume_options;
        materialize_resume_options.sqlite_path = fake_session_checkpoint_db.string();
        materialize_resume_options.session_id = "session-main";
        materialize_resume_options.source_root_path = fake_source_root.string();
        materialize_resume_options.destination_root_path = fake_destination_root.string();
        materialize_resume_options.staging_root_path = fake_staging_root.string();
        materialize_resume_options.expected_folder_id = "folder-alpha";
        materialize_resume_options.expected_source_device_id = "device-bravo";
        materialize_resume_options.expected_destination_device_id = "device-alpha";
        materialize_resume_options.expected_peer_id = "peer-bravo";
        SyncSessionCheckpointMaterializeResumeResult materialize_resume_result;
        SyncValidationResult materialize_resume_run = execute_sync_session_checkpoint_resume_materializations(materialize_resume_options,
                                                                                                            materialize_resume_result);
        require(materialize_resume_run.ok &&
                materialize_resume_result.action_plan_loaded &&
                materialize_resume_result.durable_integrity_verified &&
                materialize_resume_result.source_filesystem_verified &&
                materialize_resume_result.transaction_committed &&
                materialize_resume_result.files_considered == fake_session_result.files_materialized &&
                materialize_resume_result.files_materialized == 1 &&
                materialize_resume_result.files_skipped == 1 &&
                materialize_resume_result.file_result_rows_updated == 1 &&
                materialize_resume_result.materialization_checkpoints_written == 1 &&
                materialize_resume_result.post_cleanup_committed_staging_files == 1 &&
                materialize_resume_result.post_already_converged_files == 1 &&
                materialize_resume_result.files.size() == 1 &&
                materialize_resume_result.files[0].path.value == "docs/session-report.txt" &&
                materialize_resume_result.files[0].destination_target_absent_preflight &&
                !materialize_resume_result.files[0].destination_target_already_matching &&
                materialize_resume_result.files[0].staged_file_verified &&
                materialize_resume_result.files[0].receipt_sidecars_verified &&
                materialize_resume_result.files[0].atomic_rename_performed &&
                materialize_resume_result.files[0].database_rows_updated &&
                materialize_resume_result.files[0].content_sha256 == pending_materialize_entry->content_sha256 &&
                materialize_resume_result.files[0].chunks_verified == pending_materialize_entry->chunks.size() &&
                !fs::exists(pending_materialize_staged_path) &&
                fs::exists(pending_materialize_target_path),
                "sync session checkpoint resume materialization executor performs only the complete MaterializeStagedFile branch and leaves cleanup pending");
        SyncSessionCheckpointResumeActionPlanResult post_materialize_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, post_materialize_action_plan).ok &&
                post_materialize_action_plan.cleanup_committed_staging_files == 1 &&
                post_materialize_action_plan.materialize_staged_files == 0,
                "sync session checkpoint resume materialization executor transitions the file into cleanup-committed-staging restart state");
        NormalizedSyncPath cleanup_media_path;
        require(normalize_sync_relative_path("media/session-media.bin", cleanup_media_path).ok,
                "sync session checkpoint resume cleanup fixture path normalizes");
        const SyncManifestEntry* cleanup_media_entry = find_manifest_entry_by_path(fake_session_result.source_manifest, cleanup_media_path);
        const SyncLocalApplyPlanEntry* cleanup_media_apply = find_apply_entry_by_path(fake_session_result.apply_plan, cleanup_media_path);
        require(cleanup_media_entry != nullptr && cleanup_media_apply != nullptr,
                "sync session checkpoint resume cleanup fixture has source and apply evidence");
        const std::string cleanup_media_digest = sync_manifest_entry_digest(*cleanup_media_entry);
        NormalizedSyncPath cleanup_media_staged_relative;
        cleanup_media_staged_relative.value = sync_domain_test_access::remote_staging_relative_path_for_fixture(
            cleanup_media_path,
            cleanup_media_digest,
            "sync session checkpoint resume cleanup staged file fixture path");
        const fs::path cleanup_media_staged_path = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
            fake_staging_root,
            cleanup_media_staged_relative,
            "sync session checkpoint resume cleanup staged file fixture"));
        write_binary_fixture(cleanup_media_staged_path, fake_session_media);
        for (const auto& chunk : cleanup_media_entry->chunks) {
            const NormalizedSyncPath receipt_relative{sync_domain_test_access::chunk_receipt_relative_path_for_fixture(
                cleanup_media_entry->path,
                cleanup_media_digest,
                chunk,
                "sync session checkpoint resume cleanup receipt fixture")};
            const fs::path receipt_path = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
                fake_staging_root,
                receipt_relative,
                "sync session checkpoint resume cleanup receipt fixture path"));
            write_binary_fixture(receipt_path, sync_domain_test_access::chunk_receipt_material_for_fixture(*cleanup_media_entry, *cleanup_media_apply, chunk));
        }
        {
            SyncSqliteDb cleanup_handle;
            int cleanup_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            cleanup_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), cleanup_handle.db.out(), cleanup_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(cleanup_handle.db, "could not reopen checkpoint db for resume cleanup executor test"));
            }
            sqlite_exec_or_throw(cleanup_handle.db,
                                 "UPDATE sync_session_file_results SET staging_artifacts_cleaned=0 "
                                 "WHERE session_id='session-main' AND path='media/session-media.bin';"
                                 "UPDATE sync_session_chunk_receipts SET receipt_state='accepted' "
                                 "WHERE session_id='session-main' AND path='media/session-media.bin';",
                                 "could not mark checkpoint rows pending for resume cleanup executor test");
        }
        SyncSessionCheckpointResumeActionPlanResult pending_cleanup_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, pending_cleanup_action_plan).ok &&
                pending_cleanup_action_plan.cleanup_committed_staging_files == 2 &&
                pending_cleanup_action_plan.materialize_staged_files == 0,
                "sync session checkpoint resume action plan classifies materialized pending rows as cleanup-committed-staging");
        SyncSessionCheckpointCleanupResumeOptions cleanup_resume_options;
        cleanup_resume_options.sqlite_path = fake_session_checkpoint_db.string();
        cleanup_resume_options.session_id = "session-main";
        cleanup_resume_options.source_root_path = fake_source_root.string();
        cleanup_resume_options.destination_root_path = fake_destination_root.string();
        cleanup_resume_options.staging_root_path = fake_staging_root.string();
        cleanup_resume_options.expected_folder_id = "folder-alpha";
        cleanup_resume_options.expected_source_device_id = "device-bravo";
        cleanup_resume_options.expected_destination_device_id = "device-alpha";
        cleanup_resume_options.expected_peer_id = "peer-bravo";
        SyncSessionCheckpointCleanupResumeResult cleanup_resume_result;
        SyncValidationResult cleanup_resume_run = execute_sync_session_checkpoint_resume_cleanups(cleanup_resume_options,
                                                                                                  cleanup_resume_result);
        const auto cleanup_media_file = std::find_if(cleanup_resume_result.files.begin(),
                                                     cleanup_resume_result.files.end(),
                                                     [](const SyncSessionCheckpointCleanupResumeFileResult& file_result) {
                                                         return file_result.path.value == "media/session-media.bin";
                                                     });
        const auto cleanup_docs_file = std::find_if(cleanup_resume_result.files.begin(),
                                                    cleanup_resume_result.files.end(),
                                                    [](const SyncSessionCheckpointCleanupResumeFileResult& file_result) {
                                                        return file_result.path.value == "docs/session-report.txt";
                                                    });
        const std::uint64_t cleanup_resume_chunk_total = static_cast<std::uint64_t>(pending_materialize_entry->chunks.size() + cleanup_media_entry->chunks.size());
        require(cleanup_resume_run.ok &&
                cleanup_resume_result.action_plan_loaded &&
                cleanup_resume_result.durable_integrity_verified &&
                cleanup_resume_result.source_filesystem_verified &&
                cleanup_resume_result.transaction_committed &&
                cleanup_resume_result.files_considered == fake_session_result.files_materialized &&
                cleanup_resume_result.files_cleaned == 2 &&
                cleanup_resume_result.files_skipped == 0 &&
                cleanup_resume_result.file_result_rows_updated == 2 &&
                cleanup_resume_result.cleanup_checkpoints_written == 2 &&
                cleanup_resume_result.receipt_rows_updated == cleanup_resume_chunk_total &&
                cleanup_resume_result.receipt_files_removed == cleanup_resume_chunk_total &&
                cleanup_resume_result.staged_files_removed == 1 &&
                cleanup_resume_result.directories_removed >= 2 &&
                cleanup_resume_result.post_already_converged_files == fake_session_result.files_materialized &&
                cleanup_resume_result.post_repair_committed_staging_files == 0 &&
                cleanup_resume_result.files.size() == 2 &&
                cleanup_docs_file != cleanup_resume_result.files.end() &&
                cleanup_docs_file->staged_file_absent_preflight &&
                cleanup_docs_file->receipt_sidecars_verified &&
                cleanup_docs_file->database_rows_updated &&
                cleanup_media_file != cleanup_resume_result.files.end() &&
                cleanup_media_file->staged_file_verified &&
                cleanup_media_file->staged_file_removed &&
                cleanup_media_file->receipt_sidecars_verified &&
                cleanup_media_file->database_rows_updated &&
                !fs::exists(cleanup_media_staged_path),
                "sync session checkpoint resume cleanup executor commits the CleanupCommittedStaging branch and sweeps DB-bound receipts");
        SyncSessionCheckpointResumeActionPlanResult post_cleanup_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, post_cleanup_action_plan).ok &&
                post_cleanup_action_plan.already_converged_files == fake_session_result.files_materialized &&
                post_cleanup_action_plan.cleanup_committed_staging_files == 0 &&
                post_cleanup_action_plan.repair_committed_staging_files == 0,
                "sync session checkpoint resume cleanup executor transitions all cleaned files back to already-converged restart state");
        SyncSessionCheckpointResumeViewResult post_cleanup_resume_view;
        require(load_sync_session_checkpoint_resume_view(resume_options, post_cleanup_resume_view).ok &&
                post_cleanup_resume_view.terminal_session_complete &&
                post_cleanup_resume_view.cleanup_terminal_complete &&
                post_cleanup_resume_view.all_chunk_receipts_committed_cleaned &&
                post_cleanup_resume_view.staging_artifacts_verified &&
                post_cleanup_resume_view.files_pending_cleanup == 0 &&
                post_cleanup_resume_view.chunk_receipts_pending_cleanup == 0 &&
                post_cleanup_resume_view.staging_artifact_paths.empty(),
                "sync session checkpoint resume cleanup executor restores the strict terminal resume view");
        {
            SyncSqliteDb resume_transfer_handle;
            int resume_transfer_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            resume_transfer_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), resume_transfer_handle.db.out(), resume_transfer_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(resume_transfer_handle.db, "could not reopen checkpoint db for resume transfer plan test"));
            }
            sqlite_exec_or_throw(resume_transfer_handle.db,
                                 "UPDATE sync_session_file_results SET materialized=0, staging_artifacts_cleaned=0 "
                                 "WHERE session_id='session-main' AND path='docs/session-report.txt';",
                                 "could not mark checkpoint rows pending for resume transfer plan test");
        }
        SyncSessionCheckpointResumeActionPlanResult pending_resume_transfer_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, pending_resume_transfer_action_plan).ok &&
                pending_resume_transfer_action_plan.resume_transfer_files == 1 &&
                pending_resume_transfer_action_plan.materialize_staged_files == 0 &&
                pending_resume_transfer_action_plan.cleanup_committed_staging_files == 0,
                "sync session checkpoint resume action plan classifies missing sidecars with durable receipt rows as resume-transfer");
        SyncSessionCheckpointResumeTransferPlanOptions transfer_plan_options;
        transfer_plan_options.sqlite_path = fake_session_checkpoint_db.string();
        transfer_plan_options.session_id = "session-main";
        transfer_plan_options.source_root_path = fake_source_root.string();
        transfer_plan_options.destination_root_path = fake_destination_root.string();
        transfer_plan_options.staging_root_path = fake_staging_root.string();
        transfer_plan_options.expected_folder_id = "folder-alpha";
        transfer_plan_options.expected_source_device_id = "device-bravo";
        transfer_plan_options.expected_destination_device_id = "device-alpha";
        transfer_plan_options.expected_peer_id = "peer-bravo";
        transfer_plan_options.peer_session_id = "session-main-resume";
        transfer_plan_options.max_chunks_per_request = 1;
        transfer_plan_options.max_chunks_per_peer_round = 1;
        SyncSessionCheckpointResumeTransferPlanResult transfer_plan;
        SyncValidationResult transfer_plan_run = plan_sync_session_checkpoint_resume_transfers(transfer_plan_options, transfer_plan);
        require(transfer_plan_run.ok &&
                transfer_plan.action_plan_loaded &&
                transfer_plan.durable_integrity_verified &&
                transfer_plan.source_filesystem_verified &&
                transfer_plan.files_considered == fake_session_result.files_materialized &&
                transfer_plan.files_planned == 1 &&
                transfer_plan.files_skipped == 1 &&
                transfer_plan.resume_transfer_files_planned == 1 &&
                transfer_plan.retry_transfer_files_planned == 0 &&
                transfer_plan.total_missing_chunks == pending_materialize_entry->chunks.size() &&
                transfer_plan.selected_chunks == 1 &&
                transfer_plan.peer_assigned_chunks == 1 &&
                transfer_plan.deferred_chunks == pending_materialize_entry->chunks.size() - 1 &&
                transfer_plan.files.size() == 1 &&
                transfer_plan.files[0].path.value == "docs/session-report.txt" &&
                transfer_plan.files[0].source_action == SyncSessionCheckpointResumeActionKind::ResumeTransfer &&
                transfer_plan.files[0].request_idempotency_key.starts_with("sync-resume-transfer-request:v1:") &&
                transfer_plan.files[0].schedule_idempotency_key.starts_with("sync-resume-peer-schedule:v1:") &&
                transfer_plan.files[0].peer_request_idempotency_key.starts_with("sync-resume-peer-request:v1:") &&
                transfer_plan.files[0].peer_id == "peer-bravo" &&
                transfer_plan.files[0].peer_session_id == "session-main-resume" &&
                transfer_plan.files[0].peer_work_scheduled &&
                transfer_plan.files[0].chunks_to_request.size() == 1 &&
                transfer_plan.files[0].peer_assigned_chunk_ranges.size() == 1,
                "sync session checkpoint resume transfer planner turns ResumeTransfer evidence into peer-bound missing-chunk work");
        SyncSessionCheckpointResumeTransferClaimOptions transfer_claim_options;
        transfer_claim_options.sqlite_path = fake_session_checkpoint_db.string();
        transfer_claim_options.session_id = "session-main";
        transfer_claim_options.source_root_path = fake_source_root.string();
        transfer_claim_options.destination_root_path = fake_destination_root.string();
        transfer_claim_options.staging_root_path = fake_staging_root.string();
        transfer_claim_options.expected_folder_id = "folder-alpha";
        transfer_claim_options.expected_source_device_id = "device-bravo";
        transfer_claim_options.expected_destination_device_id = "device-alpha";
        transfer_claim_options.expected_peer_id = "peer-bravo";
        transfer_claim_options.peer_session_id = "session-main-resume";
        transfer_claim_options.worker_id = "worker-charlie";
        transfer_claim_options.worker_lease_epoch = 7;
        transfer_claim_options.workorder_claim_now_epoch = 1000;
        transfer_claim_options.worker_lease_seconds = 10;
        auto make_transfer_workorder_queue_options = [&](const fs::path& checkpoint_db,
                                                         std::uint64_t now_epoch) {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options;
            queue_options.sqlite_path = checkpoint_db.string();
            queue_options.session_id = "session-main";
            queue_options.source_root_path = fake_source_root.string();
            queue_options.destination_root_path = fake_destination_root.string();
            queue_options.staging_root_path = fake_staging_root.string();
            queue_options.expected_folder_id = "folder-alpha";
            queue_options.expected_source_device_id = "device-bravo";
            queue_options.expected_destination_device_id = "device-alpha";
            queue_options.expected_peer_id = "peer-bravo";
            queue_options.queue_now_epoch = now_epoch;
            return queue_options;
        };
        auto make_transfer_workorder_scheduler_options = [&](const fs::path& checkpoint_db,
                                                             std::uint64_t now_epoch) {
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions scheduler_options;
            scheduler_options.sqlite_path = checkpoint_db.string();
            scheduler_options.session_id = "session-main";
            scheduler_options.source_root_path = fake_source_root.string();
            scheduler_options.destination_root_path = fake_destination_root.string();
            scheduler_options.staging_root_path = fake_staging_root.string();
            scheduler_options.expected_folder_id = "folder-alpha";
            scheduler_options.expected_source_device_id = "device-bravo";
            scheduler_options.expected_destination_device_id = "device-alpha";
            scheduler_options.expected_peer_id = "peer-bravo";
            scheduler_options.scheduler_now_epoch = now_epoch;
            return scheduler_options;
        };
        auto make_transfer_workorder_scheduler_execution_options = [&](const fs::path& checkpoint_db,
                                                                       std::uint64_t now_epoch,
                                                                       const std::string& worker_id,
                                                                       std::uint64_t worker_lease_epoch,
                                                                       std::uint64_t worker_lease_seconds) {
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions scheduler_execution_options;
            scheduler_execution_options.sqlite_path = checkpoint_db.string();
            scheduler_execution_options.session_id = "session-main";
            scheduler_execution_options.source_root_path = fake_source_root.string();
            scheduler_execution_options.destination_root_path = fake_destination_root.string();
            scheduler_execution_options.staging_root_path = fake_staging_root.string();
            scheduler_execution_options.expected_folder_id = "folder-alpha";
            scheduler_execution_options.expected_source_device_id = "device-bravo";
            scheduler_execution_options.expected_destination_device_id = "device-alpha";
            scheduler_execution_options.expected_peer_id = "peer-bravo";
            scheduler_execution_options.peer_session_id = "session-main-resume";
            scheduler_execution_options.worker_id = worker_id;
            scheduler_execution_options.worker_lease_epoch = worker_lease_epoch;
            scheduler_execution_options.scheduler_now_epoch = now_epoch;
            scheduler_execution_options.worker_lease_seconds = worker_lease_seconds;
            scheduler_execution_options.workorder_retry_backoff_seconds = 5;
            return scheduler_execution_options;
        };
        auto make_transfer_workorder_daemon_loop_options = [&](const fs::path& checkpoint_db,
                                                            std::uint64_t initial_now_epoch,
                                                            const std::string& worker_id,
                                                            std::uint64_t worker_lease_epoch,
                                                            std::uint64_t worker_lease_seconds) {
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions loop_options;
            loop_options.sqlite_path = checkpoint_db.string();
            loop_options.session_id = "session-main";
            loop_options.source_root_path = fake_source_root.string();
            loop_options.destination_root_path = fake_destination_root.string();
            loop_options.staging_root_path = fake_staging_root.string();
            loop_options.expected_folder_id = "folder-alpha";
            loop_options.expected_source_device_id = "device-bravo";
            loop_options.expected_destination_device_id = "device-alpha";
            loop_options.expected_peer_id = "peer-bravo";
            loop_options.peer_session_id = "session-main-resume";
            loop_options.worker_id = worker_id;
            loop_options.initial_worker_lease_epoch = worker_lease_epoch;
            loop_options.initial_scheduler_now_epoch = initial_now_epoch;
            loop_options.worker_lease_seconds = worker_lease_seconds;
            loop_options.loop_tick_seconds = 1;
            loop_options.workorder_retry_backoff_seconds = 5;
            return loop_options;
        };
        auto count_session_rows_in_checkpoint = [&](const fs::path& checkpoint_db,
                                                     const std::string& sql,
                                                     const std::string& label) {
            SyncSqliteDb count_handle;
            int count_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            count_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(checkpoint_db.string().c_str(), count_handle.db.out(), count_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(count_handle.db, "could not reopen checkpoint db for " + label));
            }
            return sqlite_count_for_session_or_throw(count_handle.db,
                                                     sql,
                                                     "session-main",
                                                     label);
        };
        const fs::path retry_backoff_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-retry-backoff-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(retry_backoff_checkpoint_db, apply_cleanup_ec);
        fs::remove(fs::path(retry_backoff_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(retry_backoff_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                    retry_backoff_checkpoint_db,
                                    "sync session checkpoint resume transfer retry-backoff selftest");
        SyncSessionCheckpointResumeTransferClaimOptions backoff_claim_options = transfer_claim_options;
        backoff_claim_options.sqlite_path = retry_backoff_checkpoint_db.string();
        backoff_claim_options.workorder_retry_backoff_seconds = 5;
        SyncSessionCheckpointResumeTransferClaimResult backoff_claim_result;
        SyncValidationResult backoff_claim_run = claim_sync_session_checkpoint_resume_transfer_workorders(backoff_claim_options,
                                                                                                          backoff_claim_result);
        require(backoff_claim_run.ok &&
                backoff_claim_result.workorder_claim_now_epoch == 1000 &&
                backoff_claim_result.lease_expires_at_epoch == 1010 &&
                backoff_claim_result.workorder_retry_backoff_seconds == 5 &&
                backoff_claim_result.retry_at_epoch == 1015 &&
                backoff_claim_result.workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                backoff_claim_result.files.size() == 1 &&
                backoff_claim_result.files[0].claimed_at_epoch == 1000 &&
                backoff_claim_result.files[0].lease_expires_at_epoch == 1010 &&
                backoff_claim_result.files[0].retry_at_epoch == 1015,
                "sync session checkpoint resume transfer claim stores deterministic retry-at backoff evidence on claimed rows");
        const fs::path scheduler_executor_owned_seed_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-scheduler-executor-owned-seed-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(scheduler_executor_owned_seed_checkpoint_db, apply_cleanup_ec);
        fs::remove(fs::path(scheduler_executor_owned_seed_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(scheduler_executor_owned_seed_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                    scheduler_executor_owned_seed_checkpoint_db,
                                    "sync session checkpoint resume transfer scheduler executor owned seed selftest");
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(retry_backoff_checkpoint_db, 1005);
            queue_options.worker_id = backoff_claim_result.worker_id;
            queue_options.worker_lease_id = backoff_claim_result.worker_lease_id;
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.read_only_scan_completed &&
                    queue_result.resume_view_loaded &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.queue_facts_returned == pending_materialize_entry->chunks.size() &&
                    queue_result.owned_claim_ready_rows == pending_materialize_entry->chunks.size() &&
                    queue_result.live_claimed_by_other_rows == 0 &&
                    !queue_result.facts.empty() &&
                    queue_result.facts[0].queue_kind == SyncSessionCheckpointResumeTransferWorkorderQueueKind::OwnedClaimReady &&
                    queue_result.facts[0].owned_by_selector_worker &&
                    !queue_result.facts[0].lease_expired,
                    "sync session checkpoint resume transfer queue selector exposes owned live claimed rows as runnable without mutation");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions scheduler_options = make_transfer_workorder_scheduler_options(retry_backoff_checkpoint_db, 1005);
            scheduler_options.worker_id = backoff_claim_result.worker_id;
            scheduler_options.worker_lease_id = backoff_claim_result.worker_lease_id;
            scheduler_options.max_scheduler_actions = 1;
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult scheduler_result;
            SyncValidationResult scheduler_run = plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_options, scheduler_result);
            require(scheduler_run.ok &&
                    scheduler_result.queue_selected &&
                    scheduler_result.scheduler_plan_completed &&
                    scheduler_result.queue_facts_considered == pending_materialize_entry->chunks.size() &&
                    scheduler_result.scheduler_action_groups_considered == 1 &&
                    scheduler_result.scheduler_action_groups_returned == 0 &&
                    scheduler_result.scheduler_action_groups_deferred_by_limit == 1 &&
                    scheduler_result.scheduler_actions_deferred_by_limit == pending_materialize_entry->chunks.size() &&
                    scheduler_result.scheduler_actions_returned == 0 &&
                    scheduler_result.mutating_actions_planned == 0 &&
                    scheduler_result.actions.empty(),
                    "sync session checkpoint resume transfer scheduler pass refuses to split an execution-idempotency workorder batch at a too-small action limit");
            scheduler_options.max_scheduler_actions = pending_materialize_entry->chunks.size();
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult complete_scheduler_result;
            SyncValidationResult complete_scheduler_run = plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_options, complete_scheduler_result);
            require(complete_scheduler_run.ok &&
                    complete_scheduler_result.scheduler_plan_completed &&
                    complete_scheduler_result.scheduler_action_groups_considered == 1 &&
                    complete_scheduler_result.scheduler_action_groups_returned == 1 &&
                    complete_scheduler_result.scheduler_action_groups_deferred_by_limit == 0 &&
                    complete_scheduler_result.scheduler_actions_returned == pending_materialize_entry->chunks.size() &&
                    complete_scheduler_result.mutating_actions_planned == pending_materialize_entry->chunks.size() &&
                    complete_scheduler_result.execute_owned_claim_actions == pending_materialize_entry->chunks.size() &&
                    !complete_scheduler_result.actions.empty() &&
                    complete_scheduler_result.actions[0].action_kind == SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::ExecuteOwnedClaim &&
                    complete_scheduler_result.actions[0].source_queue_kind == SyncSessionCheckpointResumeTransferWorkorderQueueKind::OwnedClaimReady &&
                    complete_scheduler_result.actions[0].mutating_action &&
                    complete_scheduler_result.actions[0].scheduler_priority == 1 &&
                    complete_scheduler_result.actions[0].scheduler_group_priority == 1 &&
                    complete_scheduler_result.actions[0].scheduler_group_size == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer scheduler pass maps a complete execution batch to bounded execute-owned actions");
        }
        {
            const fs::path scheduler_executor_deferred_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-scheduler-executor-deferred-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(scheduler_executor_deferred_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_deferred_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_deferred_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        scheduler_executor_deferred_checkpoint_db,
                                        "sync session checkpoint resume transfer scheduler executor deferred selftest");
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions scheduler_execution_options =
                make_transfer_workorder_scheduler_execution_options(scheduler_executor_deferred_checkpoint_db, 1005, "worker-charlie", 7, 10);
            scheduler_execution_options.max_scheduler_actions = 1;
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult scheduler_execution_result;
            SyncValidationResult scheduler_execution_run = execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_execution_options,
                                                                                                                                     scheduler_execution_result);
            require(scheduler_execution_run.ok &&
                    scheduler_execution_result.scheduler_execution_completed &&
                    scheduler_execution_result.scheduler_actions_returned == 0 &&
                    scheduler_execution_result.mutating_actions_planned == 0 &&
                    scheduler_execution_result.mutating_action_groups_selected == 0 &&
                    scheduler_execution_result.scheduler_action_groups_deferred_by_limit == 1 &&
                    scheduler_execution_result.scheduler_actions_deferred_by_limit == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_rows_completed == 0 &&
                    scheduler_execution_result.workorder_rows_reclaimed == 0 &&
                    scheduler_execution_result.workorder_rows_abandoned == 0,
                    "sync session checkpoint resume transfer scheduler executor refuses to mutate a deferred partial execution group");
            SyncSqliteDb scheduler_deferred_probe_handle;
            int scheduler_deferred_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            scheduler_deferred_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(scheduler_executor_deferred_checkpoint_db.string().c_str(), scheduler_deferred_probe_handle.db.out(), scheduler_deferred_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(scheduler_deferred_probe_handle.db, "could not reopen checkpoint db for scheduler executor deferred probe"));
            }
            const std::uint64_t still_claimed_rows = sqlite_count_for_session_or_throw(scheduler_deferred_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-charlie' AND claim_attempts=1;",
                "session-main",
                "resume transfer scheduler executor deferred claimed row count");
            require(still_claimed_rows == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer scheduler executor leaves deferred rows untouched in SQLite");
        }
        {
            const fs::path scheduler_executor_cooldown_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-scheduler-executor-cooldown-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(scheduler_executor_cooldown_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_cooldown_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_cooldown_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        scheduler_executor_cooldown_checkpoint_db,
                                        "sync session checkpoint resume transfer scheduler executor cooldown selftest");
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions scheduler_execution_options =
                make_transfer_workorder_scheduler_execution_options(scheduler_executor_cooldown_checkpoint_db, 1010, "worker-delta", 9, 15);
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult scheduler_execution_result;
            SyncValidationResult scheduler_execution_run = execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_execution_options,
                                                                                                                                     scheduler_execution_result);
            require(scheduler_execution_run.ok &&
                    scheduler_execution_result.scheduler_execution_completed &&
                    scheduler_execution_result.mutating_actions_planned == 0 &&
                    scheduler_execution_result.nonmutating_actions_observed == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_rows_reclaimed == 0 &&
                    scheduler_execution_result.workorder_rows_completed == 0 &&
                    scheduler_execution_result.workorder_rows_abandoned == 0,
                    "sync session checkpoint resume transfer scheduler executor observes retry cooldown rows without mutation");
            SyncSqliteDb scheduler_cooldown_probe_handle;
            int scheduler_cooldown_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            scheduler_cooldown_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(scheduler_executor_cooldown_checkpoint_db.string().c_str(), scheduler_cooldown_probe_handle.db.out(), scheduler_cooldown_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(scheduler_cooldown_probe_handle.db, "could not reopen checkpoint db for scheduler executor cooldown probe"));
            }
            const std::uint64_t cooldown_rows_untouched = sqlite_count_for_session_or_throw(scheduler_cooldown_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-charlie' AND retry_at_epoch=1015 AND claim_attempts=1;",
                "session-main",
                "resume transfer scheduler executor cooldown untouched row count");
            require(cooldown_rows_untouched == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer scheduler executor leaves retry-cooling rows owned by the prior worker");
        }
        {
            const fs::path scheduler_executor_reclaim_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-scheduler-executor-reclaim-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(scheduler_executor_reclaim_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_reclaim_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_reclaim_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        scheduler_executor_reclaim_checkpoint_db,
                                        "sync session checkpoint resume transfer scheduler executor reclaim selftest");
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions scheduler_execution_options =
                make_transfer_workorder_scheduler_execution_options(scheduler_executor_reclaim_checkpoint_db, 1015, "worker-delta", 9, 15);
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult scheduler_execution_result;
            SyncValidationResult scheduler_execution_run = execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_execution_options,
                                                                                                                                     scheduler_execution_result);
            require(scheduler_execution_run.ok &&
                    scheduler_execution_result.scheduler_execution_completed &&
                    scheduler_execution_result.claim_or_reclaim_expired_groups_selected == 1 &&
                    scheduler_execution_result.claim_or_abandon_filter_keys == 1 &&
                    scheduler_execution_result.claim_or_abandon_runs == 1 &&
                    scheduler_execution_result.execute_owned_runs == 0 &&
                    scheduler_execution_result.claim_or_reclaim_expired_actions_selected == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_rows_reclaimed == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_reclaim_events_written == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_rows_completed == 0,
                    "sync session checkpoint resume transfer scheduler executor reclaims only the returned expired complete group");
        }
        {
            const fs::path scheduler_executor_abandon_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-scheduler-executor-abandon-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(scheduler_executor_abandon_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_abandon_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_abandon_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        scheduler_executor_abandon_checkpoint_db,
                                        "sync session checkpoint resume transfer scheduler executor abandon selftest");
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions scheduler_execution_options =
                make_transfer_workorder_scheduler_execution_options(scheduler_executor_abandon_checkpoint_db, 1015, "worker-delta", 9, 15);
            scheduler_execution_options.max_workorder_claim_attempts = 1;
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult scheduler_execution_result;
            SyncValidationResult scheduler_execution_run = execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_execution_options,
                                                                                                                                     scheduler_execution_result);
            require(scheduler_execution_run.ok &&
                    scheduler_execution_result.scheduler_execution_completed &&
                    scheduler_execution_result.abandon_expired_groups_selected == 1 &&
                    scheduler_execution_result.claim_or_abandon_filter_keys == 1 &&
                    scheduler_execution_result.abandon_expired_actions_selected == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_rows_abandoned == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_abandon_events_written == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_rows_reclaimed == 0 &&
                    scheduler_execution_result.workorder_rows_completed == 0,
                    "sync session checkpoint resume transfer scheduler executor abandons only the returned expired attempt-cap group");
        }
        {
            const fs::path daemon_loop_deferred_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-loop-deferred-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(daemon_loop_deferred_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(daemon_loop_deferred_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(daemon_loop_deferred_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        daemon_loop_deferred_checkpoint_db,
                                        "sync session checkpoint resume transfer workorder daemon loop deferred selftest");
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions daemon_loop_options =
                make_transfer_workorder_daemon_loop_options(daemon_loop_deferred_checkpoint_db, 1005, "worker-charlie", 7, 10);
            daemon_loop_options.max_loop_passes = 3;
            daemon_loop_options.max_scheduler_actions_per_pass = 1;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult daemon_loop_result;
            SyncValidationResult daemon_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(daemon_loop_options,
                                                                                                                    daemon_loop_result);
            require(daemon_loop_run.ok &&
                    daemon_loop_result.daemon_loop_completed &&
                    daemon_loop_result.daemon_id == "worker-charlie-daemon" &&
                    daemon_loop_result.daemon_lease_events_written == 1 &&
                    daemon_loop_result.daemon_lease_events_already_present == 0 &&
                    daemon_loop_result.final_worker_lease_epoch == 7 &&
                    daemon_loop_result.next_worker_lease_epoch == 8 &&
                    daemon_loop_result.worker_lease_id == daemon_loop_result.final_worker_lease_id &&
                    daemon_loop_result.passes_attempted == 1 &&
                    daemon_loop_result.passes_completed == 1 &&
                    daemon_loop_result.stopped_on_deferred_actions &&
                    !daemon_loop_result.stopped_after_idle_pass &&
                    daemon_loop_result.scheduler_action_groups_deferred_by_limit == 1 &&
                    daemon_loop_result.scheduler_actions_deferred_by_limit == pending_materialize_entry->chunks.size() &&
                    daemon_loop_result.workorder_rows_completed == 0 &&
                    daemon_loop_result.workorder_rows_reclaimed == 0 &&
                    daemon_loop_result.pass_results.size() == 1 &&
                    daemon_loop_result.pass_results[0].worker_lease_id == daemon_loop_result.final_worker_lease_id,
                    "sync session checkpoint resume transfer workorder daemon loop stops after a deferred complete action group without spinning");
            require(count_session_rows_in_checkpoint(daemon_loop_deferred_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_lease_events WHERE session_id=? AND daemon_id='worker-charlie-daemon' AND worker_id='worker-charlie' AND worker_lease_epoch=7 AND lease_reason='scheduler-pass' AND loop_pass_index=1;",
                                                     "daemon loop deferred lease event count") == 1,
                    "sync session checkpoint resume transfer workorder daemon loop stores a durable scheduler-pass lease event before planning");
        }
        {
            const fs::path daemon_loop_reclaim_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-loop-reclaim-idle-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(daemon_loop_reclaim_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(daemon_loop_reclaim_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(daemon_loop_reclaim_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        daemon_loop_reclaim_checkpoint_db,
                                        "sync session checkpoint resume transfer workorder daemon loop reclaim idle selftest");
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions daemon_loop_options =
                make_transfer_workorder_daemon_loop_options(daemon_loop_reclaim_checkpoint_db, 1015, "worker-delta", 9, 15);
            daemon_loop_options.max_loop_passes = 3;
            daemon_loop_options.max_scheduler_actions_per_pass = pending_materialize_entry->chunks.size();
            daemon_loop_options.execute_owned_claim_actions = false;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult daemon_loop_result;
            SyncValidationResult daemon_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(daemon_loop_options,
                                                                                                                    daemon_loop_result);
            require(daemon_loop_run.ok &&
                    daemon_loop_result.daemon_loop_completed &&
                    daemon_loop_result.daemon_id == "worker-delta-daemon" &&
                    daemon_loop_result.daemon_lease_events_written == 1 &&
                    daemon_loop_result.daemon_lease_events_already_present == 0 &&
                    daemon_loop_result.final_worker_lease_epoch == 9 &&
                    daemon_loop_result.next_worker_lease_epoch == 10 &&
                    daemon_loop_result.worker_lease_id == daemon_loop_result.final_worker_lease_id &&
                    daemon_loop_result.passes_attempted == 2 &&
                    daemon_loop_result.passes_completed == 2 &&
                    daemon_loop_result.mutating_passes == 1 &&
                    daemon_loop_result.idle_passes == 1 &&
                    daemon_loop_result.stopped_after_idle_pass &&
                    !daemon_loop_result.max_loop_passes_reached &&
                    daemon_loop_result.claim_or_reclaim_expired_groups_selected == 1 &&
                    daemon_loop_result.execute_owned_claim_groups_selected == 0 &&
                    daemon_loop_result.workorder_rows_reclaimed == pending_materialize_entry->chunks.size() &&
                    daemon_loop_result.workorder_reclaim_events_written == pending_materialize_entry->chunks.size() &&
                    daemon_loop_result.workorder_rows_completed == 0 &&
                    daemon_loop_result.pass_results.size() == 2 &&
                    daemon_loop_result.pass_results[0].claim_or_reclaim_expired_groups_selected == 1 &&
                    daemon_loop_result.pass_results[0].worker_lease_id == daemon_loop_result.final_worker_lease_id &&
                    daemon_loop_result.pass_results[1].execute_owned_claim_actions_selected == 0 &&
                    daemon_loop_result.pass_results[1].worker_lease_id == daemon_loop_result.final_worker_lease_id,
                    "sync session checkpoint resume transfer workorder daemon loop can reclaim once then stop on the next idle owned-claim pass");
            require(count_session_rows_in_checkpoint(daemon_loop_reclaim_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_lease_events WHERE session_id=? AND daemon_id='worker-delta-daemon' AND worker_id='worker-delta' AND worker_lease_epoch=9 AND lease_started_at_epoch=1015 AND lease_expires_at_epoch=1030 AND lease_reason='scheduler-pass';",
                                                     "daemon loop reclaim lease event count") == 1,
                    "sync session checkpoint resume transfer workorder daemon loop reuses one durable lease across live mutating and idle passes");
        }
        {
            const fs::path daemon_loop_renewal_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-loop-renewal-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(daemon_loop_renewal_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(daemon_loop_renewal_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(daemon_loop_renewal_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        daemon_loop_renewal_checkpoint_db,
                                        "sync session checkpoint resume transfer workorder daemon loop lease renewal selftest");
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions daemon_loop_options =
                make_transfer_workorder_daemon_loop_options(daemon_loop_renewal_checkpoint_db, 1015, "worker-echo", 21, 1);
            daemon_loop_options.max_loop_passes = 2;
            daemon_loop_options.loop_tick_seconds = 2;
            daemon_loop_options.workorder_retry_backoff_seconds = 0;
            daemon_loop_options.max_scheduler_actions_per_pass = pending_materialize_entry->chunks.size();
            daemon_loop_options.execute_owned_claim_actions = false;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult daemon_loop_result;
            SyncValidationResult daemon_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(daemon_loop_options,
                                                                                                                    daemon_loop_result);
            require(daemon_loop_run.ok &&
                    daemon_loop_result.daemon_loop_completed &&
                    daemon_loop_result.daemon_id == "worker-echo-daemon" &&
                    daemon_loop_result.daemon_lease_events_written == 2 &&
                    daemon_loop_result.daemon_lease_events_already_present == 0 &&
                    daemon_loop_result.final_worker_lease_epoch == 22 &&
                    daemon_loop_result.next_worker_lease_epoch == 23 &&
                    daemon_loop_result.passes_attempted == 2 &&
                    daemon_loop_result.passes_completed == 2 &&
                    daemon_loop_result.mutating_passes == 2 &&
                    daemon_loop_result.idle_passes == 0 &&
                    daemon_loop_result.max_loop_passes_reached &&
                    daemon_loop_result.claim_or_reclaim_expired_groups_selected == 2 &&
                    daemon_loop_result.workorder_rows_reclaimed == pending_materialize_entry->chunks.size() * 2 &&
                    daemon_loop_result.workorder_reclaim_events_written == pending_materialize_entry->chunks.size() * 2 &&
                    daemon_loop_result.pass_results.size() == 2 &&
                    daemon_loop_result.pass_results[0].worker_lease_id != daemon_loop_result.pass_results[1].worker_lease_id &&
                    daemon_loop_result.pass_results[1].worker_lease_id == daemon_loop_result.final_worker_lease_id,
                    "sync session checkpoint resume transfer workorder daemon loop renews the durable lease after expiry before reclaiming again");
            require(count_session_rows_in_checkpoint(daemon_loop_renewal_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_lease_events WHERE session_id=? AND daemon_id='worker-echo-daemon' AND worker_id='worker-echo' AND worker_lease_epoch IN (21,22) AND lease_reason='scheduler-pass';",
                                                     "daemon loop renewal lease event count") == 2,
                    "sync session checkpoint resume transfer workorder daemon loop stores one lease event per acquired daemon lease epoch");
            SyncSessionCheckpointOperatorStatusOptions daemon_status_options;
            daemon_status_options.sqlite_path = daemon_loop_renewal_checkpoint_db.string();
            daemon_status_options.session_id = "session-main";
            daemon_status_options.scheduler_now_epoch = 1018;
            SyncSessionCheckpointOperatorStatusResult daemon_status;
            SyncValidationResult daemon_status_run = load_sync_session_checkpoint_operator_status(daemon_status_options,
                                                                                                  daemon_status);
            require(daemon_status_run.ok &&
                    daemon_status.status_loaded &&
                    daemon_status.query_only_enabled &&
                    daemon_status.daemon_lease_events == 2 &&
                    daemon_status.live_daemon_lease_events == 0 &&
                    daemon_status.expired_daemon_lease_events == 2 &&
                    daemon_status.latest_daemon_id == "worker-echo-daemon" &&
                    daemon_status.latest_daemon_worker_lease_epoch == 22 &&
                    !daemon_status.latest_daemon_lease_live &&
                    daemon_status.workorder_reclaim_events == pending_materialize_entry->chunks.size() * 2 &&
                    daemon_status.retryable_expired_workorder_rows == pending_materialize_entry->chunks.size() &&
                    daemon_status.suggested_next_action == "run-daemon-reclaim-retry",
                    "sync session checkpoint operator status summarizes expired daemon leases and retryable reclaimed rows");
        }
        {
            const fs::path daemon_owner_conflict_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-owner-conflict-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(daemon_owner_conflict_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(daemon_owner_conflict_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(daemon_owner_conflict_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        daemon_owner_conflict_checkpoint_db,
                                        "sync session checkpoint resume transfer workorder daemon owner lock conflict selftest");
            sync_domain_test_access::DaemonOwnerLockRecord held_owner = sync_domain_test_access::acquire_resume_transfer_daemon_owner_lock_for_fixture(daemon_owner_conflict_checkpoint_db.string(),
                                                                                                               "session-main",
                                                                                                               "worker-foxtrot-daemon",
                                                                                                               "worker-foxtrot",
                                                                                                               1005,
                                                                                                               50);
            require(held_owner.acquired &&
                    held_owner.owner_lock_epoch == 1 &&
                    held_owner.owner_lock_id.starts_with("sync-resume-daemon-owner-lock:v1:"),
                    "sync session checkpoint resume transfer daemon owner lock mints the first durable generation rather than accepting caller authority");
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions blocked_loop_options =
                make_transfer_workorder_daemon_loop_options(daemon_owner_conflict_checkpoint_db, 1006, "worker-golf", 32, 10);
            blocked_loop_options.max_loop_passes = 1;
            const fs::path blocked_loop_heartbeat_path = fs::temp_directory_path() / ("anonsync-sync-daemon-blocked-heartbeat-" + std::to_string(selftest_ticks) + ".json");
            fs::remove(blocked_loop_heartbeat_path, apply_cleanup_ec);
            write_file(blocked_loop_heartbeat_path.string(), "sentinel-live-owner-heartbeat\n");
            blocked_loop_options.daemon_heartbeat_path = blocked_loop_heartbeat_path.string();
            blocked_loop_options.daemon_heartbeat_stale_after_seconds = 7;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult blocked_loop_result;
            SyncValidationResult blocked_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(blocked_loop_options,
                                                                                                                       blocked_loop_result);
            require(!blocked_loop_run.ok &&
                    blocked_loop_run.reason.find("already held by live daemon worker-foxtrot-daemon") != std::string::npos &&
                    count_session_rows_in_checkpoint(daemon_owner_conflict_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_lease_events WHERE session_id=? AND daemon_id='worker-golf-daemon';",
                                                     "daemon owner lock blocked competing scheduler lease count") == 0 &&
                    read_file(blocked_loop_heartbeat_path.string()) == "sentinel-live-owner-heartbeat\n",
                    "sync session checkpoint resume transfer daemon owner lock blocks a competing local daemon before scheduler lease or heartbeat evidence is written");
            SyncSessionCheckpointOperatorStatusOptions owner_status_options;
            owner_status_options.sqlite_path = daemon_owner_conflict_checkpoint_db.string();
            owner_status_options.session_id = "session-main";
            owner_status_options.scheduler_now_epoch = 1006;
            SyncSessionCheckpointOperatorStatusResult owner_status;
            SyncValidationResult owner_status_run = load_sync_session_checkpoint_operator_status(owner_status_options,
                                                                                                  owner_status);
            require(owner_status_run.ok &&
                    owner_status.status_loaded &&
                    owner_status.daemon_owner_lock_rows == 1 &&
                    owner_status.daemon_owner_lock_held &&
                    owner_status.daemon_owner_lock_live &&
                    owner_status.daemon_owner_lock_daemon_id == "worker-foxtrot-daemon" &&
                    !owner_status.safe_to_schedule &&
                    owner_status.suggested_next_action == "wait-daemon-owner-lock",
                    "sync session checkpoint operator status reports a live daemon owner lock as wait-not-schedule state");
            const fs::path owner_status_cli_report_path = fs::temp_directory_path() / ("anonsync-sync-operator-status-cli-" + std::to_string(selftest_ticks) + ".json");
            fs::remove(owner_status_cli_report_path, apply_cleanup_ec);
            int owner_status_cli_rc = run_sync_checkpoint_operator_status_report_command(daemon_owner_conflict_checkpoint_db.string(),
                                                                                         "session-main",
                                                                                         1006,
                                                                                         owner_status_cli_report_path.string());
            Json owner_status_cli_report = load_json(owner_status_cli_report_path.string());
            require(owner_status_cli_rc == 0 &&
                    owner_status_cli_report.at("format").str() == "anonsync-sync-checkpoint-operator-status-report-v1" &&
                    owner_status_cli_report.at("ok").boolean(false) &&
                    owner_status_cli_report.at("status").at("query_only_enabled").boolean(false) &&
                    owner_status_cli_report.at("status").at("daemon_owner_lock_live").boolean(false) &&
                    owner_status_cli_report.at("status").at("suggested_next_action").str() == "wait-daemon-owner-lock",
                    "sync checkpoint operator status CLI emits read-only actionable owner-lock JSON");
            {
                const fs::path symlink_report_target = fs::temp_directory_path() / ("anonsync-sync-operator-status-symlink-target-" + std::to_string(selftest_ticks) + ".json");
                const fs::path symlink_report_path = fs::temp_directory_path() / ("anonsync-sync-operator-status-symlink-report-" + std::to_string(selftest_ticks) + ".json");
                fs::remove(symlink_report_path, apply_cleanup_ec);
                fs::remove(symlink_report_target, apply_cleanup_ec);
                write_file(symlink_report_target.string(), "sentinel-report-target\n");
                std::error_code symlink_ec;
                fs::create_symlink(symlink_report_target, symlink_report_path, symlink_ec);
                if (!symlink_ec) {
                    int symlink_report_rc = run_sync_checkpoint_operator_status_report_command(daemon_owner_conflict_checkpoint_db.string(),
                                                                                               "session-main",
                                                                                               1006,
                                                                                               symlink_report_path.string());
                    require(symlink_report_rc == 1 &&
                            read_file(symlink_report_target.string()) == "sentinel-report-target\n",
                            "sync checkpoint operator status CLI refuses to write reports through symlink paths");
                    fs::remove(symlink_report_path, apply_cleanup_ec);
                }
                fs::remove(symlink_report_target, apply_cleanup_ec);
            }
            const fs::path stale_heartbeat_path = fs::temp_directory_path() / ("anonsync-sync-daemon-stale-heartbeat-" + std::to_string(selftest_ticks) + ".json");
            fs::remove(stale_heartbeat_path, apply_cleanup_ec);
            const std::string held_owner_service_instance_id =
                sync_domain_test_access::resume_transfer_daemon_service_instance_id_for_fixture(
                    "session-main",
                    "worker-foxtrot-daemon",
                    "worker-foxtrot",
                    31);
            const SyncProcessIdentityObservation held_owner_process_identity =
                recycled_process_identity_fixture_or_throw();
            {
                std::ostringstream hb;
                hb << "{\n"
                   << "  \"format\": \"anonsync-sync-daemon-service-heartbeat-v2\",\n"
                   << "  \"revision_id\": \"rev0839\",\n"
                   << "  \"operation\": \"sync-daemon-service-heartbeat\",\n"
                   << "  \"service_instance_id\": \"" << held_owner_service_instance_id << "\",\n"
                   << "  \"service_restart_epoch\": 31,\n"
                   << "  \"state\": \"scheduler-pass\",\n"
                   << "  \"final\": false,\n"
                   << "  \"reason\": \"selftest stale heartbeat\",\n"
                   << "  \"heartbeat_epoch\": 1005,\n"
                   << "  \"stale_after_seconds\": 1,\n"
                   << "  \"stale_at_epoch\": 1006,\n"
                   << "  \"process_id\": " << held_owner_process_identity.process_id << ",\n"
                   << "  \"process_incarnation\": {\n"
                   << "    \"format\": \"" << json_escape(held_owner_process_identity.format) << "\",\n"
                   << "    \"process_id\": " << held_owner_process_identity.process_id << ",\n"
                   << "    \"boot_id\": \"" << json_escape(held_owner_process_identity.boot_id) << "\",\n"
                   << "    \"start_token\": \"" << json_escape(held_owner_process_identity.start_token) << "\"\n"
                   << "  },\n"
                   << "  \"checkpoint_path\": \"" << json_escape(daemon_owner_conflict_checkpoint_db.string()) << "\",\n"
                   << "  \"session_id\": \"session-main\",\n"
                   << "  \"daemon_id\": \"worker-foxtrot-daemon\",\n"
                   << "  \"worker_id\": \"worker-foxtrot\",\n"
                   << "  \"service_lifecycle\": {},\n"
                   << "  \"owner_lock\": {\n"
                   << "    \"required\": true,\n"
                   << "    \"acquired\": true,\n"
                   << "    \"released\": false,\n"
                   << "    \"reclaimed_expired\": false,\n"
                   << "    \"owner_lock_id\": \"" << json_escape(held_owner.owner_lock_id) << "\",\n"
                   << "    \"owner_lock_epoch\": " << held_owner.owner_lock_epoch << ",\n"
                   << "    \"acquired_at_epoch\": 1005,\n"
                   << "    \"expires_at_epoch\": 1055,\n"
                   << "    \"released_at_epoch\": 0\n"
                   << "  },\n"
                   << "  \"lease\": {},\n"
                   << "  \"progress\": {}\n"
                   << "}\n";
                write_file(stale_heartbeat_path.string(), hb.str());
            }
            SyncSessionCheckpointOperatorStatusOptions stale_heartbeat_status_options = owner_status_options;
            stale_heartbeat_status_options.daemon_heartbeat_path = stale_heartbeat_path.string();
            SyncSessionCheckpointOperatorStatusResult stale_heartbeat_status;
            SyncValidationResult stale_heartbeat_status_run = load_sync_session_checkpoint_operator_status(stale_heartbeat_status_options,
                                                                                                            stale_heartbeat_status);
            require(stale_heartbeat_status_run.ok &&
                    stale_heartbeat_status.status_loaded &&
                    stale_heartbeat_status.daemon_heartbeat_requested &&
                    stale_heartbeat_status.daemon_heartbeat_loaded &&
                    stale_heartbeat_status.daemon_heartbeat_format_ok &&
                    stale_heartbeat_status.daemon_heartbeat_session_matches &&
                    stale_heartbeat_status.daemon_heartbeat_checkpoint_matches &&
                    stale_heartbeat_status.daemon_heartbeat_owner_lock_matches &&
                    stale_heartbeat_status.daemon_heartbeat_process_identity_present &&
                    stale_heartbeat_status.daemon_heartbeat_process_identity_checked &&
                    stale_heartbeat_status.daemon_heartbeat_process_live &&
                    !stale_heartbeat_status.daemon_heartbeat_process_identity_matches &&
                    stale_heartbeat_status.daemon_heartbeat_process_identity_match_kind == "mismatch" &&
                    stale_heartbeat_status.daemon_heartbeat_stale &&
                    stale_heartbeat_status.daemon_heartbeat_attention_required &&
                    stale_heartbeat_status.operator_attention_required &&
                    !stale_heartbeat_status.safe_to_schedule &&
                    stale_heartbeat_status.suggested_next_action == "inspect-stale-daemon-heartbeat",
                    "sync checkpoint operator status detects stale external heartbeat for a live owner lock before advising wait");
            const fs::path stale_heartbeat_cli_report_path = fs::temp_directory_path() / ("anonsync-sync-operator-status-stale-heartbeat-cli-" + std::to_string(selftest_ticks) + ".json");
            fs::remove(stale_heartbeat_cli_report_path, apply_cleanup_ec);
            int stale_heartbeat_cli_rc = run_sync_checkpoint_operator_status_report_command(daemon_owner_conflict_checkpoint_db.string(),
                                                                                            "session-main",
                                                                                            1006,
                                                                                            stale_heartbeat_cli_report_path.string(),
                                                                                            stale_heartbeat_path.string());
            Json stale_heartbeat_cli_report = load_json(stale_heartbeat_cli_report_path.string());
            require(stale_heartbeat_cli_rc == 0 &&
                    stale_heartbeat_cli_report.at("status").at("daemon_heartbeat_loaded").boolean(false) &&
                    stale_heartbeat_cli_report.at("status").at("daemon_heartbeat_stale").boolean(false) &&
                    stale_heartbeat_cli_report.at("status").at("daemon_heartbeat_attention_required").boolean(false) &&
                    stale_heartbeat_cli_report.at("status").at("suggested_next_action").str() == "inspect-stale-daemon-heartbeat",
                    "sync checkpoint operator status CLI includes heartbeat freshness evidence for live owner locks");
            {
                const fs::path oversized_heartbeat_path = fs::temp_directory_path() / ("anonsync-sync-daemon-oversized-heartbeat-" + std::to_string(selftest_ticks) + ".json");
                fs::remove(oversized_heartbeat_path, apply_cleanup_ec);
                write_file(oversized_heartbeat_path.string(), std::string(70000, ' '));
                SyncSessionCheckpointOperatorStatusOptions oversized_heartbeat_status_options = owner_status_options;
                oversized_heartbeat_status_options.daemon_heartbeat_path = oversized_heartbeat_path.string();
                SyncSessionCheckpointOperatorStatusResult oversized_heartbeat_status;
                SyncValidationResult oversized_heartbeat_status_run = load_sync_session_checkpoint_operator_status(oversized_heartbeat_status_options,
                                                                                                                    oversized_heartbeat_status);
                require(oversized_heartbeat_status_run.ok &&
                        oversized_heartbeat_status.status_loaded &&
                        oversized_heartbeat_status.daemon_heartbeat_requested &&
                        oversized_heartbeat_status.daemon_heartbeat_path_exists &&
                        !oversized_heartbeat_status.daemon_heartbeat_loaded &&
                        oversized_heartbeat_status.daemon_heartbeat_attention_required &&
                        oversized_heartbeat_status.daemon_heartbeat_error.find("exceeds bounded read limit") != std::string::npos &&
                        oversized_heartbeat_status.suggested_next_action == "inspect-daemon-heartbeat-mismatch",
                        "sync checkpoint operator status bounds daemon heartbeat reads before parsing external JSON");
                fs::remove(oversized_heartbeat_path, apply_cleanup_ec);
            }
            SyncSessionCheckpointOperatorStatusOptions missing_heartbeat_status_options = owner_status_options;
            missing_heartbeat_status_options.daemon_heartbeat_path = stale_heartbeat_path.string() + ".missing";
            SyncSessionCheckpointOperatorStatusResult missing_heartbeat_status;
            SyncValidationResult missing_heartbeat_status_run = load_sync_session_checkpoint_operator_status(missing_heartbeat_status_options,
                                                                                                              missing_heartbeat_status);
            require(missing_heartbeat_status_run.ok &&
                    missing_heartbeat_status.status_loaded &&
                    missing_heartbeat_status.daemon_heartbeat_requested &&
                    !missing_heartbeat_status.daemon_heartbeat_path_exists &&
                    !missing_heartbeat_status.daemon_heartbeat_loaded &&
                    missing_heartbeat_status.daemon_heartbeat_attention_required &&
                    missing_heartbeat_status.suggested_next_action == "inspect-daemon-heartbeat-mismatch",
                    "sync checkpoint operator status treats a missing requested heartbeat as attention when a live owner lock exists");
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions takeover_loop_options =
                make_transfer_workorder_daemon_loop_options(daemon_owner_conflict_checkpoint_db, 1060, "worker-golf", 32, 10);
            takeover_loop_options.max_loop_passes = 1;
            takeover_loop_options.max_scheduler_actions_per_pass = 1;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult takeover_loop_result;
            SyncValidationResult takeover_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(takeover_loop_options,
                                                                                                                       takeover_loop_result);
            require(takeover_loop_run.ok &&
                    takeover_loop_result.daemon_owner_lock_acquired &&
                    takeover_loop_result.daemon_owner_lock_reclaimed_expired &&
                    takeover_loop_result.daemon_owner_lock_released &&
                    takeover_loop_result.daemon_owner_lock_epoch == held_owner.owner_lock_epoch + 1 &&
                    takeover_loop_result.daemon_id == "worker-golf-daemon",
                    "sync session checkpoint resume transfer daemon owner lock mints the next durable generation when a new daemon takes over after expiry");
        }
        {
            const fs::path service_lifecycle_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-daemon-service-lifecycle-" + std::to_string(selftest_ticks) + ".sqlite");
            const fs::path service_lifecycle_heartbeat_path = fs::temp_directory_path() / ("anonsync-sync-daemon-service-lifecycle-heartbeat-" + std::to_string(selftest_ticks) + ".json");
            fs::remove(service_lifecycle_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(service_lifecycle_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(service_lifecycle_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            fs::remove(service_lifecycle_heartbeat_path, apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        service_lifecycle_checkpoint_db,
                                        "sync daemon service lifecycle preflight seed selftest");
            sync_domain_test_access::DaemonOwnerLockRecord stale_owner = sync_domain_test_access::acquire_resume_transfer_daemon_owner_lock_for_fixture(service_lifecycle_checkpoint_db.string(),
                                                                                                                 "session-main",
                                                                                                                 "worker-service-prior-daemon",
                                                                                                                 "worker-service-prior",
                                                                                                                   1005,
                                                                                                                 50);
            require(stale_owner.acquired && stale_owner.expires_at_epoch == 1055,
                    "sync daemon service lifecycle fixture starts with an owner lock that later expires");
            const std::string prior_service_instance_id =
                sync_domain_test_access::resume_transfer_daemon_service_instance_id_for_fixture(
                    "session-main",
                    "worker-service-prior-daemon",
                    "worker-service-prior",
                    61);
            const SyncProcessIdentityObservation live_process_identity =
                current_sync_process_identity_observation_or_throw();
            const SyncProcessIdentityObservation prior_process_identity =
                recycled_process_identity_fixture_or_throw();
            auto write_service_lifecycle_heartbeat_for_process =
                [&](std::uint64_t heartbeat_epoch,
                    std::uint64_t stale_at_epoch,
                    const SyncProcessIdentityObservation& process_identity) {
                std::ostringstream hb;
                hb << "{\n"
                   << "  \"format\": \"anonsync-sync-daemon-service-heartbeat-v2\",\n"
                   << "  \"revision_id\": \"rev0839\",\n"
                   << "  \"operation\": \"sync-daemon-service-heartbeat\",\n"
                   << "  \"service_instance_id\": \"" << prior_service_instance_id << "\",\n"
                   << "  \"service_restart_epoch\": 61,\n"
                   << "  \"state\": \"scheduler-pass-started\",\n"
                   << "  \"final\": false,\n"
                   << "  \"reason\": \"selftest prior service heartbeat\",\n"
                   << "  \"heartbeat_epoch\": " << heartbeat_epoch << ",\n"
                   << "  \"stale_after_seconds\": 20,\n"
                   << "  \"stale_at_epoch\": " << stale_at_epoch << ",\n"
                   << "  \"process_id\": " << process_identity.process_id << ",\n"
                   << "  \"process_incarnation\": {\n"
                   << "    \"format\": \"" << json_escape(process_identity.format) << "\",\n"
                   << "    \"process_id\": " << process_identity.process_id << ",\n"
                   << "    \"boot_id\": \"" << json_escape(process_identity.boot_id) << "\",\n"
                   << "    \"start_token\": \"" << json_escape(process_identity.start_token) << "\"\n"
                   << "  },\n"
                   << "  \"checkpoint_path\": \"" << json_escape(service_lifecycle_checkpoint_db.string()) << "\",\n"
                   << "  \"session_id\": \"session-main\",\n"
                   << "  \"daemon_id\": \"worker-service-prior-daemon\",\n"
                   << "  \"worker_id\": \"worker-service-prior\",\n"
                   << "  \"service_lifecycle\": {},\n"
                   << "  \"owner_lock\": {\n"
                   << "    \"required\": true,\n"
                   << "    \"acquired\": true,\n"
                   << "    \"released\": false,\n"
                   << "    \"reclaimed_expired\": false,\n"
                   << "    \"owner_lock_id\": \"" << json_escape(stale_owner.owner_lock_id) << "\",\n"
                   << "    \"owner_lock_epoch\": " << stale_owner.owner_lock_epoch << ",\n"
                   << "    \"acquired_at_epoch\": 1005,\n"
                   << "    \"expires_at_epoch\": 1055,\n"
                   << "    \"released_at_epoch\": 0\n"
                   << "  },\n"
                   << "  \"lease\": {\n"
                   << "    \"worker_lease_id\": \"sync-resume-transfer-lease:v1:test\",\n"
                   << "    \"final_worker_lease_epoch\": 61,\n"
                   << "    \"next_worker_lease_epoch\": 62,\n"
                   << "    \"next_scheduler_now_epoch\": " << heartbeat_epoch << "\n"
                   << "  },\n"
                   << "  \"progress\": {\n"
                   << "    \"passes_attempted\": 1,\n"
                   << "    \"passes_completed\": 0,\n"
                   << "    \"mutating_passes\": 0,\n"
                   << "    \"idle_passes\": 0,\n"
                   << "    \"startup_sidecar_recovery_attempted\": false,\n"
                   << "    \"startup_sidecar_recovery_completed\": false,\n"
                   << "    \"workorder_rows_claimed\": 0,\n"
                   << "    \"workorder_rows_reclaimed\": 0,\n"
                   << "    \"workorder_rows_completed\": 0,\n"
                   << "    \"chunks_written\": 0,\n"
                   << "    \"bytes_written\": 0\n"
                   << "  }\n"
                   << "}\n";
                write_file(service_lifecycle_heartbeat_path.string(), hb.str());
                return hb.str();
            };
            auto write_service_lifecycle_heartbeat =
                [&](std::uint64_t heartbeat_epoch,
                    std::uint64_t stale_at_epoch) {
                    return write_service_lifecycle_heartbeat_for_process(
                        heartbeat_epoch,
                        stale_at_epoch,
                        prior_process_identity);
                };
            const std::string fresh_heartbeat_text = write_service_lifecycle_heartbeat(1056, 1076);
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions fresh_block_options =
                make_transfer_workorder_daemon_loop_options(service_lifecycle_checkpoint_db, 1056, "worker-service-next", 62, 10);
            fresh_block_options.max_loop_passes = 1;
            fresh_block_options.max_scheduler_actions_per_pass = 1;
            fresh_block_options.daemon_heartbeat_path = service_lifecycle_heartbeat_path.string();
            fresh_block_options.daemon_heartbeat_stale_after_seconds = 20;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult fresh_block_result;
            SyncValidationResult fresh_block_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(fresh_block_options,
                                                                                                                      fresh_block_result);
            require(!fresh_block_run.ok &&
                    fresh_block_run.reason.find(
                        "heartbeat process incarnation is no longer exact before both stale horizon and owner expiry permit re-entry") !=
                        std::string::npos &&
                    fresh_block_result.service_lifecycle_preflight_checked &&
                    fresh_block_result.service_lifecycle_heartbeat_existing_loaded &&
                    fresh_block_result.service_lifecycle_heartbeat_existing_fresh &&
                    fresh_block_result.service_lifecycle_existing_heartbeat_process_identity_checked &&
                    fresh_block_result.service_lifecycle_existing_heartbeat_process_live &&
                    !fresh_block_result.service_lifecycle_existing_heartbeat_process_identity_matches &&
                    fresh_block_result.service_lifecycle_existing_heartbeat_process_identity_match_kind == "mismatch" &&
                    !fresh_block_result.daemon_owner_lock_acquired &&
                    count_session_rows_in_checkpoint(service_lifecycle_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_owner_locks WHERE session_id=? AND daemon_id='worker-service-prior-daemon';",
                                                     "fresh heartbeat service lifecycle owner lock nonmutation count") == 1 &&
                    count_session_rows_in_checkpoint(service_lifecycle_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_lease_events WHERE session_id=? AND daemon_id='worker-service-next-daemon';",
                                                     "fresh heartbeat service lifecycle daemon lease nonmutation count") == 0 &&
                    read_file(service_lifecycle_heartbeat_path.string()) == fresh_heartbeat_text,
                    "sync daemon service lifecycle preflight blocks fresh non-final heartbeat before owner-lock or scheduler mutation");
            SyncSessionCheckpointOperatorStatusOptions fresh_heartbeat_status_options;
            fresh_heartbeat_status_options.sqlite_path = service_lifecycle_checkpoint_db.string();
            fresh_heartbeat_status_options.session_id = "session-main";
            fresh_heartbeat_status_options.scheduler_now_epoch = 1056;
            fresh_heartbeat_status_options.daemon_heartbeat_path = service_lifecycle_heartbeat_path.string();
            SyncSessionCheckpointOperatorStatusResult fresh_heartbeat_status;
            SyncValidationResult fresh_heartbeat_status_run =
                load_sync_session_checkpoint_operator_status(
                    fresh_heartbeat_status_options,
                    fresh_heartbeat_status);
            require(fresh_heartbeat_status_run.ok &&
                    fresh_heartbeat_status.daemon_heartbeat_loaded &&
                    fresh_heartbeat_status.daemon_heartbeat_owner_lock_matches &&
                    !fresh_heartbeat_status.daemon_owner_lock_live &&
                    !fresh_heartbeat_status.daemon_heartbeat_stale &&
                    fresh_heartbeat_status.daemon_heartbeat_process_identity_checked &&
                    fresh_heartbeat_status.daemon_heartbeat_process_live &&
                    !fresh_heartbeat_status.daemon_heartbeat_process_identity_matches &&
                    fresh_heartbeat_status.daemon_heartbeat_process_identity_match_kind == "mismatch" &&
                    fresh_heartbeat_status.daemon_heartbeat_attention_required &&
                    fresh_heartbeat_status.daemon_heartbeat_error.find(
                        "heartbeat process incarnation is no longer exact before both stale horizon and owner expiry permit re-entry") !=
                        std::string::npos &&
                    fresh_heartbeat_status.suggested_next_action == "inspect-daemon-heartbeat-mismatch",
                    "sync checkpoint operator status mirrors fresh-heartbeat preflight even after the durable owner generation expires");

            const std::string inconsistent_horizon_text =
                write_service_lifecycle_heartbeat(1056, 1075);
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions inconsistent_horizon_options =
                make_transfer_workorder_daemon_loop_options(service_lifecycle_checkpoint_db, 1077, "worker-service-next", 62, 10);
            inconsistent_horizon_options.max_loop_passes = 1;
            inconsistent_horizon_options.max_scheduler_actions_per_pass = 1;
            inconsistent_horizon_options.daemon_heartbeat_path = service_lifecycle_heartbeat_path.string();
            inconsistent_horizon_options.daemon_heartbeat_stale_after_seconds = 20;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult inconsistent_horizon_result;
            SyncValidationResult inconsistent_horizon_run =
                run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(
                    inconsistent_horizon_options,
                    inconsistent_horizon_result);
            require(!inconsistent_horizon_run.ok &&
                    inconsistent_horizon_run.reason.find("stale_at_epoch does not equal heartbeat_epoch plus stale_after_seconds") != std::string::npos &&
                    !inconsistent_horizon_result.daemon_owner_lock_acquired &&
                    count_session_rows_in_checkpoint(service_lifecycle_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_lease_events WHERE session_id=? AND daemon_id='worker-service-next-daemon';",
                                                     "inconsistent heartbeat horizon daemon lease nonmutation count") == 0 &&
                    read_file(service_lifecycle_heartbeat_path.string()) == inconsistent_horizon_text,
                    "sync daemon service lifecycle recomputes stale-horizon arithmetic before any owner or scheduler mutation");

            std::string mismatched_owner_text =
                write_service_lifecycle_heartbeat(1056, 1076);
            const std::string mismatched_owner_id =
                "sync-resume-daemon-owner-lock:v1:" + std::string(64, '0');
            const std::size_t owner_id_position =
                mismatched_owner_text.find(stale_owner.owner_lock_id);
            if (owner_id_position == std::string::npos) {
                throw std::runtime_error("sync daemon service lifecycle owner generation fixture could not locate owner_lock_id");
            }
            mismatched_owner_text.replace(owner_id_position,
                                          stale_owner.owner_lock_id.size(),
                                          mismatched_owner_id);
            write_file(service_lifecycle_heartbeat_path.string(),
                       mismatched_owner_text);
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult mismatched_owner_result;
            SyncValidationResult mismatched_owner_run =
                run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(
                    inconsistent_horizon_options,
                    mismatched_owner_result);
            require(!mismatched_owner_run.ok &&
                    mismatched_owner_run.reason.find("not bound to the exact durable owner generation") != std::string::npos &&
                    !mismatched_owner_result.daemon_owner_lock_acquired &&
                    read_file(service_lifecycle_heartbeat_path.string()) == mismatched_owner_text,
                    "sync daemon service lifecycle refuses a canonical but different owner generation before takeover");

            std::string mismatched_service_instance_text =
                write_service_lifecycle_heartbeat(1056, 1076);
            const std::string mismatched_service_instance_id =
                "sync-daemon-service-instance:v1:" +
                std::string(64, prior_service_instance_id.ends_with(
                                    std::string(64, '0'))
                                    ? '1'
                                    : '0');
            const std::size_t service_instance_position =
                mismatched_service_instance_text.find(
                    prior_service_instance_id);
            if (service_instance_position == std::string::npos) {
                throw std::runtime_error(
                    "sync daemon service lifecycle fixture could not locate service_instance_id");
            }
            mismatched_service_instance_text.replace(
                service_instance_position,
                prior_service_instance_id.size(),
                mismatched_service_instance_id);
            write_file(service_lifecycle_heartbeat_path.string(),
                       mismatched_service_instance_text);
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult
                mismatched_service_instance_result;
            SyncValidationResult mismatched_service_instance_run =
                run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(
                    inconsistent_horizon_options,
                    mismatched_service_instance_result);
            require(!mismatched_service_instance_run.ok &&
                    mismatched_service_instance_run.reason.find(
                        "service_instance_id is not bound") !=
                        std::string::npos &&
                    !mismatched_service_instance_result.daemon_owner_lock_acquired &&
                    read_file(service_lifecycle_heartbeat_path.string()) ==
                        mismatched_service_instance_text,
                    "sync daemon service lifecycle recomputes service-instance identity before takeover");

            SyncSessionCheckpointOperatorStatusOptions
                mismatched_service_status_options =
                    fresh_heartbeat_status_options;
            mismatched_service_status_options.scheduler_now_epoch = 1077;
            SyncSessionCheckpointOperatorStatusResult
                mismatched_service_status;
            SyncValidationResult mismatched_service_status_run =
                load_sync_session_checkpoint_operator_status(
                    mismatched_service_status_options,
                    mismatched_service_status);
            require(mismatched_service_status_run.ok &&
                    mismatched_service_status.daemon_heartbeat_loaded &&
                    mismatched_service_status.daemon_heartbeat_stale &&
                    mismatched_service_status.daemon_heartbeat_owner_lock_matches &&
                    mismatched_service_status.daemon_heartbeat_attention_required &&
                    mismatched_service_status.daemon_heartbeat_error.find(
                        "service_instance_id is not bound") !=
                        std::string::npos,
                    "sync checkpoint operator status reports the same service-instance identity blocker as daemon preflight");

            const std::string live_stale_heartbeat_text =
                write_service_lifecycle_heartbeat_for_process(
                    1056,
                    1076,
                    live_process_identity);
            SyncSessionCheckpointOperatorStatusOptions
                live_stale_process_status_options =
                    fresh_heartbeat_status_options;
            live_stale_process_status_options.scheduler_now_epoch = 1077;
            SyncSessionCheckpointOperatorStatusResult
                live_stale_process_status;
            SyncValidationResult live_stale_process_status_run =
                load_sync_session_checkpoint_operator_status(
                    live_stale_process_status_options,
                    live_stale_process_status);
            require(live_stale_process_status_run.ok &&
                    live_stale_process_status.daemon_heartbeat_loaded &&
                    live_stale_process_status.daemon_heartbeat_stale &&
                    !live_stale_process_status.daemon_owner_lock_live &&
                    live_stale_process_status.daemon_heartbeat_process_identity_present &&
                    live_stale_process_status.daemon_heartbeat_process_identity_checked &&
                    live_stale_process_status.daemon_heartbeat_process_live &&
                    live_stale_process_status.daemon_heartbeat_process_identity_matches &&
                    live_stale_process_status.daemon_heartbeat_process_identity_match_kind == "match" &&
                    live_stale_process_status.daemon_heartbeat_attention_required &&
                    live_stale_process_status.daemon_heartbeat_error.find(
                        "exact process incarnation remains live") !=
                        std::string::npos,
                    "sync checkpoint operator status refuses clock-only staleness when the exact heartbeat process incarnation remains live");
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions
                live_stale_process_reentry_options =
                    make_transfer_workorder_daemon_loop_options(
                        service_lifecycle_checkpoint_db,
                        1077,
                        "worker-service-next",
                        62,
                        10);
            live_stale_process_reentry_options.max_loop_passes = 1;
            live_stale_process_reentry_options.max_scheduler_actions_per_pass = 1;
            live_stale_process_reentry_options.daemon_heartbeat_path =
                service_lifecycle_heartbeat_path.string();
            live_stale_process_reentry_options.daemon_heartbeat_stale_after_seconds =
                20;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult
                live_stale_process_reentry_result;
            SyncValidationResult live_stale_process_reentry_run =
                run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(
                    live_stale_process_reentry_options,
                    live_stale_process_reentry_result);
            require(!live_stale_process_reentry_run.ok &&
                    live_stale_process_reentry_run.reason.find(
                        "exact process incarnation remains live") !=
                        std::string::npos &&
                    live_stale_process_reentry_result.service_lifecycle_existing_heartbeat_process_identity_checked &&
                    live_stale_process_reentry_result.service_lifecycle_existing_heartbeat_process_live &&
                    live_stale_process_reentry_result.service_lifecycle_existing_heartbeat_process_identity_matches &&
                    !live_stale_process_reentry_result.daemon_owner_lock_acquired &&
                    read_file(service_lifecycle_heartbeat_path.string()) ==
                        live_stale_heartbeat_text,
                    "sync daemon preflight rejects stale-time takeover while the exact process incarnation is still observable");

            write_service_lifecycle_heartbeat(1056, 1076);
            SyncSessionCheckpointOperatorStatusOptions stale_prior_status_options =
                fresh_heartbeat_status_options;
            stale_prior_status_options.scheduler_now_epoch = 1077;
            SyncSessionCheckpointOperatorStatusResult stale_prior_status;
            SyncValidationResult stale_prior_status_run =
                load_sync_session_checkpoint_operator_status(
                    stale_prior_status_options,
                    stale_prior_status);
            require(stale_prior_status_run.ok &&
                    stale_prior_status.daemon_heartbeat_loaded &&
                    stale_prior_status.daemon_heartbeat_owner_lock_matches &&
                    stale_prior_status.daemon_heartbeat_stale &&
                    !stale_prior_status.daemon_owner_lock_live &&
                    stale_prior_status.daemon_heartbeat_process_identity_present &&
                    stale_prior_status.daemon_heartbeat_process_identity_checked &&
                    stale_prior_status.daemon_heartbeat_process_live &&
                    !stale_prior_status.daemon_heartbeat_process_identity_matches &&
                    stale_prior_status.daemon_heartbeat_process_identity_match_kind == "mismatch" &&
                    !stale_prior_status.daemon_heartbeat_attention_required,
                    "sync checkpoint operator status permits re-entry only after stale time, expired owner authority, and a different observed process incarnation agree");
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions stale_reentry_options =
                make_transfer_workorder_daemon_loop_options(service_lifecycle_checkpoint_db, 1077, "worker-service-next", 62, 10);
            stale_reentry_options.max_loop_passes = 1;
            stale_reentry_options.max_scheduler_actions_per_pass = 1;
            stale_reentry_options.daemon_heartbeat_path = service_lifecycle_heartbeat_path.string();
            stale_reentry_options.daemon_heartbeat_stale_after_seconds = 20;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult stale_reentry_result;
            SyncValidationResult stale_reentry_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(stale_reentry_options,
                                                                                                                        stale_reentry_result);
            Json stale_reentry_heartbeat = load_json(service_lifecycle_heartbeat_path.string());
            require(stale_reentry_run.ok &&
                    stale_reentry_result.service_lifecycle_preflight_checked &&
                    stale_reentry_result.service_lifecycle_preflight_passed &&
                    stale_reentry_result.service_lifecycle_heartbeat_existing_loaded &&
                    stale_reentry_result.service_lifecycle_heartbeat_existing_stale &&
                    stale_reentry_result.service_lifecycle_reentry_from_stale_heartbeat &&
                    stale_reentry_result.service_lifecycle_existing_heartbeat_process_identity_checked &&
                    stale_reentry_result.service_lifecycle_existing_heartbeat_process_live &&
                    !stale_reentry_result.service_lifecycle_existing_heartbeat_process_identity_matches &&
                    stale_reentry_result.service_lifecycle_existing_heartbeat_process_identity_match_kind == "mismatch" &&
                    stale_reentry_result.daemon_owner_lock_acquired &&
                    stale_reentry_result.daemon_owner_lock_reclaimed_expired &&
                    stale_reentry_result.daemon_owner_lock_released &&
                    stale_reentry_heartbeat.at("service_lifecycle").at("reentry_from_stale_heartbeat").boolean(false) &&
                    stale_reentry_heartbeat.at("service_instance_id").str().starts_with("sync-daemon-service-instance:v1:") &&
                    stale_reentry_heartbeat.at("service_restart_epoch").integer(-1) == 62,
                    "sync daemon service lifecycle permits stale heartbeat plus expired owner-lock re-entry with restart identity evidence");
        }
        {
            const fs::path terminal_source_root = fs::temp_directory_path() / ("anonsync-sync-terminal-tombstone-source-" + std::to_string(selftest_ticks));
            const fs::path terminal_destination_root = fs::temp_directory_path() / ("anonsync-sync-terminal-tombstone-destination-" + std::to_string(selftest_ticks));
            const fs::path terminal_staging_root = fs::temp_directory_path() / ("anonsync-sync-terminal-tombstone-stage-" + std::to_string(selftest_ticks));
            const fs::path terminal_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-terminal-tombstone-checkpoint-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove_all(terminal_source_root, apply_cleanup_ec);
            fs::remove_all(terminal_destination_root, apply_cleanup_ec);
            fs::remove_all(terminal_staging_root, apply_cleanup_ec);
            fs::remove(terminal_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            fs::create_directories(terminal_source_root);
            fs::create_directories(terminal_destination_root / "grave");
            fs::create_directories(terminal_staging_root);
            const fs::path terminal_target = terminal_destination_root / "grave/delete-me.txt";
            write_file(terminal_target.string(), "terminal tombstone drainage selftest\n");

            NormalizedSyncPath terminal_path;
            require(normalize_sync_relative_path("grave/delete-me.txt", terminal_path).ok,
                    "sync terminal tombstone drainage fixture path normalizes");
            SyncManifestEntry terminal_local_file;
            terminal_local_file.folder_id = "folder-alpha";
            terminal_local_file.device_id = "device-alpha";
            terminal_local_file.path = terminal_path;
            terminal_local_file.kind = SyncManifestEntryKind::File;
            terminal_local_file.lineage = {{"device-alpha", 1}};
            terminal_local_file.content_sha256 = sync_domain_test_access::hash_file_and_build_chunks_for_fixture(terminal_target,
                                                                            8,
                                                                            terminal_local_file.size_bytes,
                                                                            terminal_local_file.chunks);
            require(validate_sync_manifest_entry(terminal_local_file).ok,
                    "sync terminal tombstone drainage local file evidence validates");
            SyncManifestEntry terminal_remote_tombstone = publish_entry_as(terminal_local_file, "device-bravo");
            terminal_remote_tombstone.kind = SyncManifestEntryKind::Tombstone;
            terminal_remote_tombstone.size_bytes = 0;
            terminal_remote_tombstone.content_sha256.clear();
            terminal_remote_tombstone.chunks.clear();
            terminal_remote_tombstone.lineage = {{"device-alpha", 1}, {"device-bravo", 2}};
            require(validate_sync_manifest_entry(terminal_remote_tombstone).ok,
                    "sync terminal tombstone drainage remote tombstone evidence validates");
            SyncManifestEntry terminal_after_tombstone = publish_entry_as(terminal_remote_tombstone, "device-alpha");

            SyncFolderManifest terminal_destination_before = folder_manifest("folder-alpha",
                                                                             "device-alpha",
                                                                             90,
                                                                             {terminal_local_file});
            SyncFolderManifest terminal_source_manifest = folder_manifest("folder-alpha",
                                                                          "device-bravo",
                                                                          91,
                                                                          {terminal_remote_tombstone});
            SyncFolderManifest terminal_destination_after = folder_manifest("folder-alpha",
                                                                            "device-alpha",
                                                                            92,
                                                                            {terminal_after_tombstone});
            SyncManifestDiffPlan terminal_diff;
            require(build_sync_manifest_diff_plan(terminal_destination_before,
                                                  terminal_source_manifest,
                                                  terminal_diff).ok &&
                    terminal_diff.entries.size() == 1 &&
                    terminal_diff.entries[0].action == SyncPlanAction::ApplyRemoteTombstone,
                    "sync terminal tombstone drainage checkpoint fixture plans a remote tombstone");
            SyncLocalApplyOptions terminal_apply_options;
            terminal_apply_options.local_root_path = terminal_destination_root.string();
            terminal_apply_options.staging_root_path = terminal_staging_root.string();
            SyncLocalApplyPlan terminal_apply_plan;
            require(build_sync_local_apply_plan(terminal_diff,
                                                terminal_apply_options,
                                                terminal_apply_plan).ok &&
                    terminal_apply_plan.entries.size() == 1 &&
                    terminal_apply_plan.entries[0].local_action == SyncLocalApplyAction::DeleteLocalPath &&
                    terminal_apply_plan.entries[0].absolute_staging_path.empty(),
                    "sync terminal tombstone drainage local apply plan is a staging-free delete intent");

            SyncFakePeerFileFetchSessionOptions terminal_run_options;
            terminal_run_options.source_root_path = terminal_source_root.string();
            terminal_run_options.destination_root_path = terminal_destination_root.string();
            terminal_run_options.staging_root_path = terminal_staging_root.string();
            terminal_run_options.folder_id = "folder-alpha";
            terminal_run_options.source_device_id = "device-bravo";
            terminal_run_options.destination_device_id = "device-alpha";
            terminal_run_options.peer_id = "peer-bravo";
            terminal_run_options.peer_session_id = "session-main-resume";
            terminal_run_options.source_manifest_counter = 91;
            terminal_run_options.destination_manifest_counter = 90;
            terminal_run_options.source_lineage_counter = 2;
            terminal_run_options.destination_lineage_counter = 1;
            terminal_run_options.chunk_size_bytes = 8;

            SyncFakePeerFileFetchSessionResult terminal_session_result;
            terminal_session_result.source_manifest = terminal_source_manifest;
            terminal_session_result.destination_manifest_before = terminal_destination_before;
            terminal_session_result.diff_plan = terminal_diff;
            terminal_session_result.apply_plan = terminal_apply_plan;
            terminal_session_result.destination_manifest_after = terminal_destination_after;
            terminal_session_result.apply_entries_considered = static_cast<std::uint64_t>(terminal_apply_plan.entries.size());
            terminal_session_result.source_content_digest = sync_domain_test_access::convergence_content_digest_for_fixture(terminal_source_manifest);
            terminal_session_result.destination_content_digest = sync_domain_test_access::convergence_content_digest_for_fixture(terminal_destination_after);
            terminal_session_result.content_converged = sync_domain_test_access::manifests_have_same_file_content_for_fixture(terminal_source_manifest,
                                                                                         terminal_destination_after) &&
                                                        terminal_session_result.source_content_digest == terminal_session_result.destination_content_digest;
            require(terminal_session_result.content_converged,
                    "sync terminal tombstone drainage synthetic checkpoint converges after tombstone application");

            SyncSessionCheckpointOptions terminal_checkpoint_options;
            terminal_checkpoint_options.sqlite_path = terminal_checkpoint_db.string();
            terminal_checkpoint_options.session_id = "session-main";
            terminal_checkpoint_options.require_committed_cleanup = false;
            SyncSessionCheckpointResult terminal_checkpoint_result;
            SyncValidationResult terminal_checkpoint_run = persist_sync_fake_peer_session_checkpoint(terminal_run_options,
                                                                                                     terminal_session_result,
                                                                                                     terminal_checkpoint_options,
                                                                                                     terminal_checkpoint_result);
            require(terminal_checkpoint_run.ok &&
                    terminal_checkpoint_result.transaction_committed &&
                    terminal_checkpoint_result.apply_intents_written == 1 &&
                    fs::exists(terminal_target),
                    "sync terminal tombstone drainage checkpoint persists delete intent while target still exists");

            SyncSessionCheckpointOperatorStatusOptions terminal_pre_status_options;
            terminal_pre_status_options.sqlite_path = terminal_checkpoint_db.string();
            terminal_pre_status_options.session_id = "session-main";
            terminal_pre_status_options.scheduler_now_epoch = 1190;
            SyncSessionCheckpointOperatorStatusResult terminal_pre_status;
            require(load_sync_session_checkpoint_operator_status(terminal_pre_status_options,
                                                                 terminal_pre_status).ok &&
                    terminal_pre_status.terminal_apply_tombstone_intent_rows == 1 &&
                    terminal_pre_status.pending_terminal_apply_tombstone_intent_rows == 1 &&
                    terminal_pre_status.terminal_apply_workorder_rows == 0 &&
                    terminal_pre_status.safe_to_schedule &&
                    terminal_pre_status.suggested_next_action == "run-daemon-terminal-apply",
                    "sync checkpoint operator status surfaces unmaterialized tombstone intents as daemon terminal apply work");

            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions terminal_daemon_options;
            terminal_daemon_options.sqlite_path = terminal_checkpoint_db.string();
            terminal_daemon_options.session_id = "session-main";
            terminal_daemon_options.source_root_path = terminal_source_root.string();
            terminal_daemon_options.destination_root_path = terminal_destination_root.string();
            terminal_daemon_options.staging_root_path = terminal_staging_root.string();
            terminal_daemon_options.expected_folder_id = "folder-alpha";
            terminal_daemon_options.expected_source_device_id = "device-bravo";
            terminal_daemon_options.expected_destination_device_id = "device-alpha";
            terminal_daemon_options.expected_peer_id = "peer-bravo";
            terminal_daemon_options.peer_id = "peer-bravo";
            terminal_daemon_options.peer_session_id = "session-main-resume";
            terminal_daemon_options.worker_id = "worker-terminal";
            terminal_daemon_options.daemon_id = "worker-terminal-daemon";
            terminal_daemon_options.initial_worker_lease_epoch = 70;
            terminal_daemon_options.initial_scheduler_now_epoch = 1200;
            terminal_daemon_options.worker_lease_seconds = 30;
            terminal_daemon_options.loop_tick_seconds = 1;
            terminal_daemon_options.max_loop_passes = 1;
            terminal_daemon_options.max_scheduler_actions_per_pass = 1;
            terminal_daemon_options.workorder_retry_backoff_seconds = 0;
            terminal_daemon_options.recover_bound_peer_sidecars_before_scheduling = false;
            terminal_daemon_options.hydrate_startup_sidecar_evidence_from_checkpoint = false;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult terminal_daemon_result;
            SyncValidationResult terminal_daemon_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(terminal_daemon_options,
                                                                                                                          terminal_daemon_result);
            require(terminal_daemon_run.ok &&
                    terminal_daemon_result.daemon_owner_lock_acquired &&
                    terminal_daemon_result.daemon_owner_lock_released &&
                    terminal_daemon_result.terminal_apply_workorders_checked == 1 &&
                    terminal_daemon_result.terminal_apply_workorders_inserted == 1 &&
                    terminal_daemon_result.terminal_apply_workorders_completed == 1 &&
                    terminal_daemon_result.terminal_apply_tombstone_workorders_completed == 1 &&
                    terminal_daemon_result.terminal_apply_tombstone_targets_removed == 1 &&
                    !fs::exists(terminal_target),
                    "sync daemon terminal apply workorder deletes checkpoint-matched tombstone target under owner fence");

            SyncSessionCheckpointOperatorStatusResult terminal_post_status;
            require(load_sync_session_checkpoint_operator_status(terminal_pre_status_options,
                                                                 terminal_post_status).ok &&
                    terminal_post_status.terminal_apply_tombstone_intent_rows == 1 &&
                    terminal_post_status.pending_terminal_apply_tombstone_intent_rows == 0 &&
                    terminal_post_status.terminal_apply_workorder_rows == 1 &&
                    terminal_post_status.completed_terminal_apply_workorder_rows == 1 &&
                    terminal_post_status.tombstone_terminal_apply_completed_rows == 1 &&
                    terminal_post_status.tombstone_terminal_apply_targets_removed == 1 &&
                    terminal_post_status.suggested_next_action == "idle-clean",
                    "sync checkpoint operator status reports terminal tombstone drainage as completed evidence");

            terminal_daemon_options.worker_id = "worker-terminal-repeat";
            terminal_daemon_options.daemon_id = "worker-terminal-repeat-daemon";
            terminal_daemon_options.initial_worker_lease_epoch = 80;
            terminal_daemon_options.initial_scheduler_now_epoch = 1300;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult terminal_repeat_result;
            SyncValidationResult terminal_repeat_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(terminal_daemon_options,
                                                                                                                          terminal_repeat_result);
            require(terminal_repeat_run.ok &&
                    terminal_repeat_result.terminal_apply_workorders_checked == 1 &&
                    terminal_repeat_result.terminal_apply_workorders_already_completed == 1 &&
                    terminal_repeat_result.terminal_apply_workorders_completed == 0 &&
                    !fs::exists(terminal_target),
                    "sync daemon terminal tombstone replay is idempotent and refuses resurrected completed targets");

            fs::remove_all(terminal_source_root, apply_cleanup_ec);
            fs::remove_all(terminal_destination_root, apply_cleanup_ec);
            fs::remove_all(terminal_staging_root, apply_cleanup_ec);
            fs::remove(terminal_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        }
        {
            const fs::path terminal_conflict_source_root = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-source-" + std::to_string(selftest_ticks));
            const fs::path terminal_conflict_destination_root = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-destination-" + std::to_string(selftest_ticks));
            const fs::path terminal_conflict_staging_root = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-stage-" + std::to_string(selftest_ticks));
            const fs::path terminal_conflict_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-checkpoint-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove_all(terminal_conflict_source_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_destination_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_staging_root, apply_cleanup_ec);
            fs::remove(terminal_conflict_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            fs::create_directories(terminal_conflict_source_root);
            fs::create_directories(terminal_conflict_destination_root / "grave");
            fs::create_directories(terminal_conflict_staging_root);
            const fs::path terminal_conflict_target = terminal_conflict_destination_root / "grave/conflict-delete.txt";
            const std::string terminal_conflict_local_body = "terminal conflict tombstone keeps local bytes before delete\n";
            write_file(terminal_conflict_target.string(), terminal_conflict_local_body);

            NormalizedSyncPath terminal_conflict_path;
            require(normalize_sync_relative_path("grave/conflict-delete.txt", terminal_conflict_path).ok,
                    "sync terminal conflict tombstone drainage fixture path normalizes");
            SyncManifestEntry terminal_conflict_local_file;
            terminal_conflict_local_file.folder_id = "folder-alpha";
            terminal_conflict_local_file.device_id = "device-alpha";
            terminal_conflict_local_file.path = terminal_conflict_path;
            terminal_conflict_local_file.kind = SyncManifestEntryKind::File;
            terminal_conflict_local_file.lineage = {{"device-alpha", 3}};
            terminal_conflict_local_file.content_sha256 = sync_domain_test_access::hash_file_and_build_chunks_for_fixture(terminal_conflict_target,
                                                                                     8,
                                                                                     terminal_conflict_local_file.size_bytes,
                                                                                     terminal_conflict_local_file.chunks);
            require(validate_sync_manifest_entry(terminal_conflict_local_file).ok,
                    "sync terminal conflict tombstone drainage local file evidence validates");
            SyncManifestEntry terminal_conflict_remote_tombstone = publish_entry_as(terminal_conflict_local_file, "device-bravo");
            terminal_conflict_remote_tombstone.kind = SyncManifestEntryKind::Tombstone;
            terminal_conflict_remote_tombstone.size_bytes = 0;
            terminal_conflict_remote_tombstone.content_sha256.clear();
            terminal_conflict_remote_tombstone.chunks.clear();
            terminal_conflict_remote_tombstone.lineage = {{"device-bravo", 4}};
            require(validate_sync_manifest_entry(terminal_conflict_remote_tombstone).ok,
                    "sync terminal conflict tombstone drainage remote tombstone evidence validates");
            SyncManifestEntry terminal_conflict_after_tombstone = publish_entry_as(terminal_conflict_remote_tombstone, "device-alpha");

            SyncFolderManifest terminal_conflict_destination_before = folder_manifest("folder-alpha",
                                                                                      "device-alpha",
                                                                                      93,
                                                                                      {terminal_conflict_local_file});
            SyncFolderManifest terminal_conflict_source_manifest = folder_manifest("folder-alpha",
                                                                                   "device-bravo",
                                                                                   94,
                                                                                   {terminal_conflict_remote_tombstone});
            SyncFolderManifest terminal_conflict_destination_after = folder_manifest("folder-alpha",
                                                                                     "device-alpha",
                                                                                     95,
                                                                                     {terminal_conflict_after_tombstone});
            SyncManifestDiffPlan terminal_conflict_diff;
            require(build_sync_manifest_diff_plan(terminal_conflict_destination_before,
                                                  terminal_conflict_source_manifest,
                                                  terminal_conflict_diff).ok &&
                    terminal_conflict_diff.entries.size() == 1 &&
                    terminal_conflict_diff.entries[0].action == SyncPlanAction::RecordConflict,
                    "sync terminal conflict tombstone drainage checkpoint fixture plans a file/delete conflict");
            SyncLocalApplyOptions terminal_conflict_apply_options;
            terminal_conflict_apply_options.local_root_path = terminal_conflict_destination_root.string();
            terminal_conflict_apply_options.staging_root_path = terminal_conflict_staging_root.string();
            SyncLocalApplyPlan terminal_conflict_apply_plan;
            require(build_sync_local_apply_plan(terminal_conflict_diff,
                                                terminal_conflict_apply_options,
                                                terminal_conflict_apply_plan).ok &&
                    terminal_conflict_apply_plan.entries.size() == 1 &&
                    terminal_conflict_apply_plan.entries[0].local_action == SyncLocalApplyAction::PreserveConflictCopy &&
                    terminal_conflict_apply_plan.entries[0].absolute_staging_path.empty() &&
                    !terminal_conflict_apply_plan.entries[0].absolute_conflict_copy_path.empty(),
                    "sync terminal conflict tombstone drainage local apply plan is a staging-free conflict-copy delete intent");
            const fs::path terminal_conflict_copy_path = fs::path(terminal_conflict_apply_plan.entries[0].absolute_conflict_copy_path);

            SyncFakePeerFileFetchSessionOptions terminal_conflict_run_options;
            terminal_conflict_run_options.source_root_path = terminal_conflict_source_root.string();
            terminal_conflict_run_options.destination_root_path = terminal_conflict_destination_root.string();
            terminal_conflict_run_options.staging_root_path = terminal_conflict_staging_root.string();
            terminal_conflict_run_options.folder_id = "folder-alpha";
            terminal_conflict_run_options.source_device_id = "device-bravo";
            terminal_conflict_run_options.destination_device_id = "device-alpha";
            terminal_conflict_run_options.peer_id = "peer-bravo";
            terminal_conflict_run_options.peer_session_id = "session-main-resume";
            terminal_conflict_run_options.source_manifest_counter = 94;
            terminal_conflict_run_options.destination_manifest_counter = 93;
            terminal_conflict_run_options.source_lineage_counter = 4;
            terminal_conflict_run_options.destination_lineage_counter = 3;
            terminal_conflict_run_options.chunk_size_bytes = 8;

            SyncFakePeerFileFetchSessionResult terminal_conflict_session_result;
            terminal_conflict_session_result.source_manifest = terminal_conflict_source_manifest;
            terminal_conflict_session_result.destination_manifest_before = terminal_conflict_destination_before;
            terminal_conflict_session_result.diff_plan = terminal_conflict_diff;
            terminal_conflict_session_result.apply_plan = terminal_conflict_apply_plan;
            terminal_conflict_session_result.destination_manifest_after = terminal_conflict_destination_after;
            terminal_conflict_session_result.apply_entries_considered = static_cast<std::uint64_t>(terminal_conflict_apply_plan.entries.size());
            terminal_conflict_session_result.source_content_digest = sync_domain_test_access::convergence_content_digest_for_fixture(terminal_conflict_source_manifest);
            terminal_conflict_session_result.destination_content_digest = sync_domain_test_access::convergence_content_digest_for_fixture(terminal_conflict_destination_after);
            terminal_conflict_session_result.content_converged = false;

            SyncSessionCheckpointOptions terminal_conflict_checkpoint_options;
            terminal_conflict_checkpoint_options.sqlite_path = terminal_conflict_checkpoint_db.string();
            terminal_conflict_checkpoint_options.session_id = "session-main";
            terminal_conflict_checkpoint_options.require_committed_cleanup = false;
            terminal_conflict_checkpoint_options.require_converged_session = false;
            SyncSessionCheckpointResult terminal_conflict_checkpoint_result;
            SyncValidationResult terminal_conflict_checkpoint_run = persist_sync_fake_peer_session_checkpoint(terminal_conflict_run_options,
                                                                                                              terminal_conflict_session_result,
                                                                                                              terminal_conflict_checkpoint_options,
                                                                                                              terminal_conflict_checkpoint_result);
            require(terminal_conflict_checkpoint_run.ok &&
                    terminal_conflict_checkpoint_result.transaction_committed &&
                    terminal_conflict_checkpoint_result.apply_intents_written == 1 &&
                    fs::exists(terminal_conflict_target) &&
                    !fs::exists(terminal_conflict_copy_path),
                    "sync terminal conflict tombstone drainage checkpoint persists conflict-copy delete intent while target still exists");

            SyncSessionCheckpointOperatorStatusOptions terminal_conflict_pre_status_options;
            terminal_conflict_pre_status_options.sqlite_path = terminal_conflict_checkpoint_db.string();
            terminal_conflict_pre_status_options.session_id = "session-main";
            terminal_conflict_pre_status_options.scheduler_now_epoch = 1390;
            SyncSessionCheckpointOperatorStatusResult terminal_conflict_pre_status;
            require(load_sync_session_checkpoint_operator_status(terminal_conflict_pre_status_options,
                                                                 terminal_conflict_pre_status).ok &&
                    terminal_conflict_pre_status.terminal_apply_conflict_tombstone_intent_rows == 1 &&
                    terminal_conflict_pre_status.pending_terminal_apply_conflict_tombstone_intent_rows == 1 &&
                    terminal_conflict_pre_status.terminal_apply_workorder_rows == 0 &&
                    terminal_conflict_pre_status.safe_to_schedule &&
                    terminal_conflict_pre_status.suggested_next_action == "run-daemon-terminal-apply",
                    "sync checkpoint operator status surfaces unmaterialized conflict tombstone intents as daemon terminal apply work");

            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions terminal_conflict_daemon_options;
            terminal_conflict_daemon_options.sqlite_path = terminal_conflict_checkpoint_db.string();
            terminal_conflict_daemon_options.session_id = "session-main";
            terminal_conflict_daemon_options.source_root_path = terminal_conflict_source_root.string();
            terminal_conflict_daemon_options.destination_root_path = terminal_conflict_destination_root.string();
            terminal_conflict_daemon_options.staging_root_path = terminal_conflict_staging_root.string();
            terminal_conflict_daemon_options.expected_folder_id = "folder-alpha";
            terminal_conflict_daemon_options.expected_source_device_id = "device-bravo";
            terminal_conflict_daemon_options.expected_destination_device_id = "device-alpha";
            terminal_conflict_daemon_options.expected_peer_id = "peer-bravo";
            terminal_conflict_daemon_options.peer_id = "peer-bravo";
            terminal_conflict_daemon_options.peer_session_id = "session-main-resume";
            terminal_conflict_daemon_options.worker_id = "worker-conflict-terminal";
            terminal_conflict_daemon_options.daemon_id = "worker-conflict-terminal-daemon";
            terminal_conflict_daemon_options.initial_worker_lease_epoch = 90;
            terminal_conflict_daemon_options.initial_scheduler_now_epoch = 1400;
            terminal_conflict_daemon_options.worker_lease_seconds = 30;
            terminal_conflict_daemon_options.loop_tick_seconds = 1;
            terminal_conflict_daemon_options.max_loop_passes = 1;
            terminal_conflict_daemon_options.max_scheduler_actions_per_pass = 1;
            terminal_conflict_daemon_options.workorder_retry_backoff_seconds = 0;
            terminal_conflict_daemon_options.recover_bound_peer_sidecars_before_scheduling = false;
            terminal_conflict_daemon_options.hydrate_startup_sidecar_evidence_from_checkpoint = false;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult terminal_conflict_daemon_result;
            SyncValidationResult terminal_conflict_daemon_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(terminal_conflict_daemon_options,
                                                                                                                                   terminal_conflict_daemon_result);
            if (!(terminal_conflict_daemon_run.ok &&
                  terminal_conflict_daemon_result.daemon_owner_lock_acquired &&
                  terminal_conflict_daemon_result.daemon_owner_lock_released &&
                  terminal_conflict_daemon_result.terminal_apply_workorders_checked == 1 &&
                  terminal_conflict_daemon_result.terminal_apply_workorders_inserted == 1 &&
                  terminal_conflict_daemon_result.terminal_apply_workorders_completed == 1 &&
                  terminal_conflict_daemon_result.terminal_apply_conflict_tombstone_workorders_completed == 1 &&
                  terminal_conflict_daemon_result.terminal_apply_conflict_copies_preserved == 1 &&
                  terminal_conflict_daemon_result.terminal_apply_conflict_remote_tombstones_applied == 1 &&
                  !fs::exists(terminal_conflict_target) &&
                  fs::exists(terminal_conflict_copy_path) &&
                  read_file(terminal_conflict_copy_path.string()) == terminal_conflict_local_body)) {
                std::ostringstream terminal_conflict_diag;
                terminal_conflict_diag << "sync daemon terminal conflict tombstone preserves local bytes then deletes checkpoint-matched target under owner fence: "
                                       << "ok=" << terminal_conflict_daemon_run.ok
                                       << " reason=" << terminal_conflict_daemon_run.reason
                                       << " owner_acq=" << terminal_conflict_daemon_result.daemon_owner_lock_acquired
                                       << " owner_rel=" << terminal_conflict_daemon_result.daemon_owner_lock_released
                                       << " checked=" << terminal_conflict_daemon_result.terminal_apply_workorders_checked
                                       << " inserted=" << terminal_conflict_daemon_result.terminal_apply_workorders_inserted
                                       << " completed=" << terminal_conflict_daemon_result.terminal_apply_workorders_completed
                                       << " conflict_completed=" << terminal_conflict_daemon_result.terminal_apply_conflict_tombstone_workorders_completed
                                       << " conflict_preserved=" << terminal_conflict_daemon_result.terminal_apply_conflict_copies_preserved
                                       << " conflict_tombstone=" << terminal_conflict_daemon_result.terminal_apply_conflict_remote_tombstones_applied
                                       << " target_exists=" << fs::exists(terminal_conflict_target)
                                       << " copy_exists=" << fs::exists(terminal_conflict_copy_path);
                throw std::runtime_error(terminal_conflict_diag.str());
            }

            SyncSessionCheckpointOperatorStatusResult terminal_conflict_post_status;
            require(load_sync_session_checkpoint_operator_status(terminal_conflict_pre_status_options,
                                                                 terminal_conflict_post_status).ok &&
                    terminal_conflict_post_status.terminal_apply_conflict_tombstone_intent_rows == 1 &&
                    terminal_conflict_post_status.pending_terminal_apply_conflict_tombstone_intent_rows == 0 &&
                    terminal_conflict_post_status.terminal_apply_workorder_rows == 1 &&
                    terminal_conflict_post_status.completed_terminal_apply_workorder_rows == 1 &&
                    terminal_conflict_post_status.conflict_terminal_apply_completed_rows == 1 &&
                    terminal_conflict_post_status.conflict_terminal_apply_targets_removed == 1 &&
                    terminal_conflict_post_status.suggested_next_action == "idle-clean",
                    "sync checkpoint operator status reports terminal conflict tombstone drainage as completed evidence");

            terminal_conflict_daemon_options.worker_id = "worker-conflict-terminal-repeat";
            terminal_conflict_daemon_options.daemon_id = "worker-conflict-terminal-repeat-daemon";
            terminal_conflict_daemon_options.initial_worker_lease_epoch = 100;
            terminal_conflict_daemon_options.initial_scheduler_now_epoch = 1500;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult terminal_conflict_repeat_result;
            SyncValidationResult terminal_conflict_repeat_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(terminal_conflict_daemon_options,
                                                                                                                                   terminal_conflict_repeat_result);
            require(terminal_conflict_repeat_run.ok &&
                    terminal_conflict_repeat_result.terminal_apply_workorders_checked == 1 &&
                    terminal_conflict_repeat_result.terminal_apply_workorders_already_completed == 1 &&
                    terminal_conflict_repeat_result.terminal_apply_workorders_completed == 0 &&
                    !fs::exists(terminal_conflict_target) &&
                    fs::exists(terminal_conflict_copy_path) &&
                    read_file(terminal_conflict_copy_path.string()) == terminal_conflict_local_body,
                    "sync daemon terminal conflict tombstone replay is idempotent and preserves completed conflict-copy evidence");

            fs::remove_all(terminal_conflict_source_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_destination_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_staging_root, apply_cleanup_ec);
            fs::remove(terminal_conflict_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        }
        {
            const fs::path terminal_conflict_file_source_root = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-file-source-" + std::to_string(selftest_ticks));
            const fs::path terminal_conflict_file_destination_root = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-file-destination-" + std::to_string(selftest_ticks));
            const fs::path terminal_conflict_file_staging_root = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-file-stage-" + std::to_string(selftest_ticks));
            const fs::path terminal_conflict_file_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-terminal-conflict-file-checkpoint-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove_all(terminal_conflict_file_source_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_file_destination_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_file_staging_root, apply_cleanup_ec);
            fs::remove(terminal_conflict_file_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            fs::create_directories(terminal_conflict_file_source_root / "docs");
            fs::create_directories(terminal_conflict_file_destination_root / "docs");
            fs::create_directories(terminal_conflict_file_staging_root);
            const fs::path terminal_conflict_file_source_path = terminal_conflict_file_source_root / "docs/shared.txt";
            const fs::path terminal_conflict_file_target = terminal_conflict_file_destination_root / "docs/shared.txt";
            const std::string terminal_conflict_file_local_body = "local terminal conflict edit before owner fenced materialization\n";
            const std::string terminal_conflict_file_remote_body = "remote terminal conflict file bytes to materialize after preserve\n";
            write_file(terminal_conflict_file_source_path.string(), terminal_conflict_file_remote_body);
            write_file(terminal_conflict_file_target.string(), terminal_conflict_file_local_body);

            NormalizedSyncPath terminal_conflict_file_path;
            require(normalize_sync_relative_path("docs/shared.txt", terminal_conflict_file_path).ok,
                    "sync terminal conflict file path normalizes");
            SyncManifestEntry terminal_conflict_file_local_file;
            terminal_conflict_file_local_file.folder_id = "folder-alpha";
            terminal_conflict_file_local_file.device_id = "device-alpha";
            terminal_conflict_file_local_file.path = terminal_conflict_file_path;
            terminal_conflict_file_local_file.kind = SyncManifestEntryKind::File;
            terminal_conflict_file_local_file.lineage = {{"device-alpha", 5}};
            terminal_conflict_file_local_file.content_sha256 = sync_domain_test_access::hash_file_and_build_chunks_for_fixture(terminal_conflict_file_target,
                                                                                         8,
                                                                                         terminal_conflict_file_local_file.size_bytes,
                                                                                         terminal_conflict_file_local_file.chunks);
            require(validate_sync_manifest_entry(terminal_conflict_file_local_file).ok,
                    "sync terminal conflict file local manifest entry valid");
            SyncManifestEntry terminal_conflict_file_remote_file;
            terminal_conflict_file_remote_file.folder_id = "folder-alpha";
            terminal_conflict_file_remote_file.device_id = "device-bravo";
            terminal_conflict_file_remote_file.path = terminal_conflict_file_path;
            terminal_conflict_file_remote_file.kind = SyncManifestEntryKind::File;
            terminal_conflict_file_remote_file.lineage = {{"device-bravo", 6}};
            terminal_conflict_file_remote_file.content_sha256 = sync_domain_test_access::hash_file_and_build_chunks_for_fixture(terminal_conflict_file_source_path,
                                                                                          8,
                                                                                          terminal_conflict_file_remote_file.size_bytes,
                                                                                          terminal_conflict_file_remote_file.chunks);
            orient_remote_file_as_deterministic_conflict_winner_or_throw(
                terminal_conflict_file_local_file,
                terminal_conflict_file_remote_file);
            require(validate_sync_manifest_entry(terminal_conflict_file_remote_file).ok,
                    "sync terminal conflict file remote manifest entry valid");
            SyncManifestEntry terminal_conflict_file_after_file = publish_entry_as(terminal_conflict_file_remote_file, "device-alpha");

            SyncFolderManifest terminal_conflict_file_destination_before = folder_manifest("folder-alpha",
                                                                                          "device-alpha",
                                                                                          105,
                                                                                          {terminal_conflict_file_local_file});
            SyncFolderManifest terminal_conflict_file_source_manifest = folder_manifest("folder-alpha",
                                                                                       "device-bravo",
                                                                                       106,
                                                                                       {terminal_conflict_file_remote_file});
            SyncFolderManifest terminal_conflict_file_destination_after = folder_manifest("folder-alpha",
                                                                                         "device-alpha",
                                                                                         107,
                                                                                         {terminal_conflict_file_after_file});
            SyncManifestDiffPlan terminal_conflict_file_diff;
            require(build_sync_manifest_diff_plan(terminal_conflict_file_destination_before,
                                                  terminal_conflict_file_source_manifest,
                                                  terminal_conflict_file_diff).ok &&
                    terminal_conflict_file_diff.entries.size() == 1 &&
                    terminal_conflict_file_diff.entries[0].action == SyncPlanAction::RecordConflict,
                    "sync diff records remote file/local file concurrent conflict as conflict intent");
            SyncLocalApplyOptions terminal_conflict_file_apply_options;
            terminal_conflict_file_apply_options.local_root_path = terminal_conflict_file_destination_root.string();
            terminal_conflict_file_apply_options.staging_root_path = terminal_conflict_file_staging_root.string();
            SyncLocalApplyPlan terminal_conflict_file_apply_plan;
            require(build_sync_local_apply_plan(terminal_conflict_file_diff,
                                                terminal_conflict_file_apply_options,
                                                terminal_conflict_file_apply_plan).ok &&
                    terminal_conflict_file_apply_plan.entries.size() == 1 &&
                    terminal_conflict_file_apply_plan.entries[0].local_action == SyncLocalApplyAction::PreserveConflictCopy &&
                    !terminal_conflict_file_apply_plan.entries[0].absolute_staging_path.empty() &&
                    !terminal_conflict_file_apply_plan.entries[0].absolute_conflict_copy_path.empty(),
                    "sync terminal conflict file apply plan carries staging and conflict-copy evidence");
            const SyncLocalApplyPlanEntry& terminal_conflict_file_apply_entry = terminal_conflict_file_apply_plan.entries[0];
            const fs::path terminal_conflict_file_staging_path = fs::path(terminal_conflict_file_apply_entry.absolute_staging_path);
            const fs::path terminal_conflict_file_copy_path = fs::path(terminal_conflict_file_apply_entry.absolute_conflict_copy_path);
            fs::create_directories(terminal_conflict_file_staging_path.parent_path());
            {
                std::ofstream create_staging(terminal_conflict_file_staging_path, std::ios::binary | std::ios::trunc);
                if (!create_staging) throw std::runtime_error("sync terminal conflict file selftest could not create staging file");
            }
            SyncChunkReceiptWriteOptions terminal_conflict_file_chunk_options;
            terminal_conflict_file_chunk_options.local_root_path = terminal_conflict_file_destination_root.string();
            terminal_conflict_file_chunk_options.staging_root_path = terminal_conflict_file_staging_root.string();
            for (const auto& chunk : terminal_conflict_file_remote_file.chunks) {
                const std::string chunk_bytes = terminal_conflict_file_remote_body.substr(static_cast<size_t>(chunk.offset),
                                                                                         static_cast<size_t>(chunk.length));
                SyncChunkReceiptWriteResult receipt_result;
                SyncValidationResult receipt_run = write_sync_staged_chunk(terminal_conflict_file_remote_file,
                                                                      terminal_conflict_file_apply_entry,
                                                                      chunk,
                                                                      chunk_bytes,
                                                                      terminal_conflict_file_chunk_options,
                                                                      receipt_result);
                require(receipt_run.ok,
                        "sync terminal conflict file selftest writes staged remote conflict chunk receipts before daemon materialization");
            }

            SyncFakePeerFileFetchSessionOptions terminal_conflict_file_run_options;
            terminal_conflict_file_run_options.source_root_path = terminal_conflict_file_source_root.string();
            terminal_conflict_file_run_options.destination_root_path = terminal_conflict_file_destination_root.string();
            terminal_conflict_file_run_options.staging_root_path = terminal_conflict_file_staging_root.string();
            terminal_conflict_file_run_options.folder_id = "folder-alpha";
            terminal_conflict_file_run_options.source_device_id = "device-bravo";
            terminal_conflict_file_run_options.destination_device_id = "device-alpha";
            terminal_conflict_file_run_options.peer_id = "peer-bravo";
            terminal_conflict_file_run_options.peer_session_id = "session-main-resume";
            terminal_conflict_file_run_options.source_manifest_counter = 106;
            terminal_conflict_file_run_options.destination_manifest_counter = 105;
            terminal_conflict_file_run_options.source_lineage_counter =
                terminal_conflict_file_remote_file.lineage.back().counter;
            terminal_conflict_file_run_options.destination_lineage_counter = 5;
            terminal_conflict_file_run_options.chunk_size_bytes = 8;

            SyncFakePeerFileFetchSessionResult terminal_conflict_file_session_result;
            terminal_conflict_file_session_result.source_manifest = terminal_conflict_file_source_manifest;
            terminal_conflict_file_session_result.destination_manifest_before = terminal_conflict_file_destination_before;
            terminal_conflict_file_session_result.diff_plan = terminal_conflict_file_diff;
            terminal_conflict_file_session_result.apply_plan = terminal_conflict_file_apply_plan;
            terminal_conflict_file_session_result.destination_manifest_after = terminal_conflict_file_destination_after;
            terminal_conflict_file_session_result.apply_entries_considered = static_cast<std::uint64_t>(terminal_conflict_file_apply_plan.entries.size());
            terminal_conflict_file_session_result.source_content_digest = sync_domain_test_access::convergence_content_digest_for_fixture(terminal_conflict_file_source_manifest);
            terminal_conflict_file_session_result.destination_content_digest = sync_domain_test_access::convergence_content_digest_for_fixture(terminal_conflict_file_destination_after);
            terminal_conflict_file_session_result.content_converged = false;

            SyncSessionCheckpointOptions terminal_conflict_file_checkpoint_options;
            terminal_conflict_file_checkpoint_options.sqlite_path = terminal_conflict_file_checkpoint_db.string();
            terminal_conflict_file_checkpoint_options.session_id = "session-main";
            terminal_conflict_file_checkpoint_options.require_committed_cleanup = false;
            terminal_conflict_file_checkpoint_options.require_converged_session = false;
            SyncSessionCheckpointResult terminal_conflict_file_checkpoint_result;
            SyncValidationResult terminal_conflict_file_checkpoint_run = persist_sync_fake_peer_session_checkpoint(terminal_conflict_file_run_options,
                                                                                                                  terminal_conflict_file_session_result,
                                                                                                                  terminal_conflict_file_checkpoint_options,
                                                                                                                  terminal_conflict_file_checkpoint_result);
            require(terminal_conflict_file_checkpoint_run.ok &&
                    terminal_conflict_file_checkpoint_result.transaction_committed &&
                    terminal_conflict_file_checkpoint_result.apply_intents_written == 1 &&
                    fs::exists(terminal_conflict_file_target) &&
                    read_file(terminal_conflict_file_target.string()) == terminal_conflict_file_local_body &&
                    fs::exists(terminal_conflict_file_staging_path) &&
                    !fs::exists(terminal_conflict_file_copy_path),
                    "sync terminal conflict file checkpoint persists staged remote conflict intent while local target still has local bytes");

            const fs::path terminal_conflict_file_unstaged_checkpoint_db = fs::temp_directory_path() /
                ("anonsync-sync-terminal-conflict-file-unstaged-checkpoint-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(terminal_conflict_file_unstaged_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_unstaged_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_unstaged_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(terminal_conflict_file_checkpoint_db,
                                        terminal_conflict_file_unstaged_checkpoint_db,
                                        "sync terminal conflict file unstaged scheduler checkpoint seed");
            const fs::path terminal_conflict_file_sidecar_checkpoint_db = fs::temp_directory_path() /
                ("anonsync-sync-terminal-conflict-file-sidecar-recovery-checkpoint-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(terminal_conflict_file_sidecar_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_sidecar_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_sidecar_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(terminal_conflict_file_checkpoint_db,
                                        terminal_conflict_file_sidecar_checkpoint_db,
                                        "sync terminal conflict file sidecar recovery checkpoint seed");

            SyncSessionCheckpointOperatorStatusOptions terminal_conflict_file_pre_status_options;
            terminal_conflict_file_pre_status_options.sqlite_path = terminal_conflict_file_checkpoint_db.string();
            terminal_conflict_file_pre_status_options.session_id = "session-main";
            terminal_conflict_file_pre_status_options.scheduler_now_epoch = 1590;
            SyncSessionCheckpointOperatorStatusResult terminal_conflict_file_pre_status;
            require(load_sync_session_checkpoint_operator_status(terminal_conflict_file_pre_status_options,
                                                                 terminal_conflict_file_pre_status).ok &&
                    terminal_conflict_file_pre_status.terminal_apply_conflict_file_intent_rows == 1 &&
                    terminal_conflict_file_pre_status.pending_terminal_apply_conflict_file_intent_rows == 1 &&
                    terminal_conflict_file_pre_status.terminal_apply_workorder_rows == 0 &&
                    terminal_conflict_file_pre_status.safe_to_schedule &&
                    terminal_conflict_file_pre_status.suggested_next_action == "run-daemon-terminal-apply",
                    "sync checkpoint operator status surfaces staged conflict file intents as daemon terminal apply work");

            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions terminal_conflict_file_daemon_options;
            terminal_conflict_file_daemon_options.sqlite_path = terminal_conflict_file_checkpoint_db.string();
            terminal_conflict_file_daemon_options.session_id = "session-main";
            terminal_conflict_file_daemon_options.source_root_path = terminal_conflict_file_source_root.string();
            terminal_conflict_file_daemon_options.destination_root_path = terminal_conflict_file_destination_root.string();
            terminal_conflict_file_daemon_options.staging_root_path = terminal_conflict_file_staging_root.string();
            terminal_conflict_file_daemon_options.expected_folder_id = "folder-alpha";
            terminal_conflict_file_daemon_options.expected_source_device_id = "device-bravo";
            terminal_conflict_file_daemon_options.expected_destination_device_id = "device-alpha";
            terminal_conflict_file_daemon_options.expected_peer_id = "peer-bravo";
            terminal_conflict_file_daemon_options.peer_id = "peer-bravo";
            terminal_conflict_file_daemon_options.peer_session_id = "session-main-resume";
            terminal_conflict_file_daemon_options.worker_id = "worker-conflict-file-terminal";
            terminal_conflict_file_daemon_options.daemon_id = "worker-conflict-file-terminal-daemon";
            terminal_conflict_file_daemon_options.initial_worker_lease_epoch = 110;
            terminal_conflict_file_daemon_options.initial_scheduler_now_epoch = 1600;
            terminal_conflict_file_daemon_options.worker_lease_seconds = 30;
            terminal_conflict_file_daemon_options.loop_tick_seconds = 1;
            terminal_conflict_file_daemon_options.max_loop_passes = 1;
            terminal_conflict_file_daemon_options.max_scheduler_actions_per_pass = 1;
            terminal_conflict_file_daemon_options.workorder_retry_backoff_seconds = 0;
            terminal_conflict_file_daemon_options.recover_bound_peer_sidecars_before_scheduling = false;
            terminal_conflict_file_daemon_options.hydrate_startup_sidecar_evidence_from_checkpoint = false;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult terminal_conflict_file_daemon_result;
            SyncValidationResult terminal_conflict_file_daemon_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(terminal_conflict_file_daemon_options,
                                                                                                                                       terminal_conflict_file_daemon_result);
            if (!(terminal_conflict_file_daemon_run.ok &&
                  terminal_conflict_file_daemon_result.daemon_owner_lock_acquired &&
                  terminal_conflict_file_daemon_result.daemon_owner_lock_released &&
                  terminal_conflict_file_daemon_result.terminal_apply_workorders_checked == 1 &&
                  terminal_conflict_file_daemon_result.terminal_apply_workorders_inserted == 1 &&
                  terminal_conflict_file_daemon_result.terminal_apply_workorders_completed == 1 &&
                  terminal_conflict_file_daemon_result.terminal_apply_conflict_file_workorders_completed == 1 &&
                  terminal_conflict_file_daemon_result.terminal_apply_conflict_copies_preserved == 1 &&
                  terminal_conflict_file_daemon_result.terminal_apply_conflict_remote_files_materialized == 1 &&
                  fs::exists(terminal_conflict_file_target) &&
                  read_file(terminal_conflict_file_target.string()) == terminal_conflict_file_remote_body &&
                  fs::exists(terminal_conflict_file_copy_path) &&
                  read_file(terminal_conflict_file_copy_path.string()) == terminal_conflict_file_local_body &&
                  !fs::exists(terminal_conflict_file_staging_path))) {
                std::ostringstream terminal_conflict_file_diag;
                terminal_conflict_file_diag << "sync daemon terminal conflict file preserves local copy then materializes staged remote file under owner fence: "
                                            << "ok=" << terminal_conflict_file_daemon_run.ok
                                            << " reason=" << terminal_conflict_file_daemon_run.reason
                                            << " owner_acq=" << terminal_conflict_file_daemon_result.daemon_owner_lock_acquired
                                            << " owner_rel=" << terminal_conflict_file_daemon_result.daemon_owner_lock_released
                                            << " checked=" << terminal_conflict_file_daemon_result.terminal_apply_workorders_checked
                                            << " inserted=" << terminal_conflict_file_daemon_result.terminal_apply_workorders_inserted
                                            << " completed=" << terminal_conflict_file_daemon_result.terminal_apply_workorders_completed
                                            << " conflict_file_completed=" << terminal_conflict_file_daemon_result.terminal_apply_conflict_file_workorders_completed
                                            << " conflict_preserved=" << terminal_conflict_file_daemon_result.terminal_apply_conflict_copies_preserved
                                            << " conflict_remote_files=" << terminal_conflict_file_daemon_result.terminal_apply_conflict_remote_files_materialized
                                            << " target_exists=" << fs::exists(terminal_conflict_file_target)
                                            << " copy_exists=" << fs::exists(terminal_conflict_file_copy_path)
                                            << " staging_exists=" << fs::exists(terminal_conflict_file_staging_path);
                throw std::runtime_error(terminal_conflict_file_diag.str());
            }

            SyncSessionCheckpointOperatorStatusResult terminal_conflict_file_post_status;
            require(load_sync_session_checkpoint_operator_status(terminal_conflict_file_pre_status_options,
                                                                 terminal_conflict_file_post_status).ok &&
                    terminal_conflict_file_post_status.terminal_apply_conflict_file_intent_rows == 1 &&
                    terminal_conflict_file_post_status.pending_terminal_apply_conflict_file_intent_rows == 0 &&
                    terminal_conflict_file_post_status.terminal_apply_workorder_rows == 1 &&
                    terminal_conflict_file_post_status.completed_terminal_apply_workorder_rows == 1 &&
                    terminal_conflict_file_post_status.conflict_file_terminal_apply_workorder_rows == 1 &&
                    terminal_conflict_file_post_status.conflict_file_terminal_apply_completed_rows == 1 &&
                    terminal_conflict_file_post_status.conflict_file_terminal_apply_targets_materialized == 1 &&
                    terminal_conflict_file_post_status.suggested_next_action == "idle-clean",
                    "sync checkpoint operator status reports terminal conflict file drainage as completed materialization evidence");

            terminal_conflict_file_daemon_options.worker_id = "worker-conflict-file-terminal-repeat";
            terminal_conflict_file_daemon_options.daemon_id = "worker-conflict-file-terminal-repeat-daemon";
            terminal_conflict_file_daemon_options.initial_worker_lease_epoch = 120;
            terminal_conflict_file_daemon_options.initial_scheduler_now_epoch = 1700;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult terminal_conflict_file_repeat_result;
            SyncValidationResult terminal_conflict_file_repeat_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(terminal_conflict_file_daemon_options,
                                                                                                                                       terminal_conflict_file_repeat_result);
            require(terminal_conflict_file_repeat_run.ok &&
                    terminal_conflict_file_repeat_result.terminal_apply_workorders_checked == 1 &&
                    terminal_conflict_file_repeat_result.terminal_apply_workorders_already_completed == 1 &&
                    terminal_conflict_file_repeat_result.terminal_apply_workorders_completed == 0 &&
                    fs::exists(terminal_conflict_file_target) &&
                    read_file(terminal_conflict_file_target.string()) == terminal_conflict_file_remote_body &&
                    fs::exists(terminal_conflict_file_copy_path) &&
                    read_file(terminal_conflict_file_copy_path.string()) == terminal_conflict_file_local_body,
                    "sync daemon terminal conflict file replay is idempotent and preserves completed materialization evidence");

            write_file(terminal_conflict_file_target.string(), terminal_conflict_file_local_body);
            fs::remove(terminal_conflict_file_copy_path, apply_cleanup_ec);
            fs::remove(terminal_conflict_file_staging_path, apply_cleanup_ec);
            fs::remove_all(fs::path(terminal_conflict_file_staging_path.string() + ".chunks"), apply_cleanup_ec);
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions unstaged_conflict_file_daemon_options = terminal_conflict_file_daemon_options;
            unstaged_conflict_file_daemon_options.sqlite_path = terminal_conflict_file_unstaged_checkpoint_db.string();
            unstaged_conflict_file_daemon_options.worker_id = "worker-conflict-file-unstaged";
            unstaged_conflict_file_daemon_options.daemon_id = "worker-conflict-file-unstaged-daemon";
            unstaged_conflict_file_daemon_options.initial_worker_lease_epoch = 130;
            unstaged_conflict_file_daemon_options.initial_scheduler_now_epoch = 1800;
            unstaged_conflict_file_daemon_options.max_loop_passes = 2;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult unstaged_conflict_file_daemon_result;
            SyncValidationResult unstaged_conflict_file_daemon_run =
                run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(unstaged_conflict_file_daemon_options,
                                                                                 unstaged_conflict_file_daemon_result);
            if (!(unstaged_conflict_file_daemon_run.ok &&
                  unstaged_conflict_file_daemon_result.daemon_owner_lock_acquired &&
                  unstaged_conflict_file_daemon_result.daemon_owner_lock_released &&
                  unstaged_conflict_file_daemon_result.terminal_apply_workorders_checked >= 1 &&
                  unstaged_conflict_file_daemon_result.terminal_apply_workorders_inserted == 1 &&
                  unstaged_conflict_file_daemon_result.terminal_apply_workorders_completed == 1 &&
                  unstaged_conflict_file_daemon_result.terminal_apply_conflict_file_workorders_completed == 1 &&
                  unstaged_conflict_file_daemon_result.terminal_apply_conflict_copies_preserved == 1 &&
                  unstaged_conflict_file_daemon_result.terminal_apply_conflict_remote_files_materialized == 1 &&
                  unstaged_conflict_file_daemon_result.workorder_rows_completed == terminal_conflict_file_remote_file.chunks.size() &&
                  unstaged_conflict_file_daemon_result.chunks_written == terminal_conflict_file_remote_file.chunks.size() &&
                  fs::exists(terminal_conflict_file_target) &&
                  read_file(terminal_conflict_file_target.string()) == terminal_conflict_file_remote_body &&
                  fs::exists(terminal_conflict_file_copy_path) &&
                  read_file(terminal_conflict_file_copy_path.string()) == terminal_conflict_file_local_body &&
                  !fs::exists(terminal_conflict_file_staging_path))) {
                std::ostringstream unstaged_conflict_file_diag;
                unstaged_conflict_file_diag << "sync daemon unstaged conflict file scheduler stages remote bytes then terminal-materializes under owner fence: "
                                            << "ok=" << unstaged_conflict_file_daemon_run.ok
                                            << " reason=" << unstaged_conflict_file_daemon_run.reason
                                            << " owner_acq=" << unstaged_conflict_file_daemon_result.daemon_owner_lock_acquired
                                            << " owner_rel=" << unstaged_conflict_file_daemon_result.daemon_owner_lock_released
                                            << " checked=" << unstaged_conflict_file_daemon_result.terminal_apply_workorders_checked
                                            << " inserted=" << unstaged_conflict_file_daemon_result.terminal_apply_workorders_inserted
                                            << " terminal_completed=" << unstaged_conflict_file_daemon_result.terminal_apply_workorders_completed
                                            << " conflict_completed=" << unstaged_conflict_file_daemon_result.terminal_apply_conflict_file_workorders_completed
                                            << " workorder_completed=" << unstaged_conflict_file_daemon_result.workorder_rows_completed
                                            << " chunks_written=" << unstaged_conflict_file_daemon_result.chunks_written
                                            << " expected_chunks=" << terminal_conflict_file_remote_file.chunks.size()
                                            << " target_exists=" << fs::exists(terminal_conflict_file_target)
                                            << " copy_exists=" << fs::exists(terminal_conflict_file_copy_path)
                                            << " staging_exists=" << fs::exists(terminal_conflict_file_staging_path);
                throw std::runtime_error(unstaged_conflict_file_diag.str());
            }

            SyncSessionCheckpointOperatorStatusOptions unstaged_conflict_file_post_status_options = terminal_conflict_file_pre_status_options;
            unstaged_conflict_file_post_status_options.sqlite_path = terminal_conflict_file_unstaged_checkpoint_db.string();
            unstaged_conflict_file_post_status_options.scheduler_now_epoch = 1890;
            SyncSessionCheckpointOperatorStatusResult unstaged_conflict_file_post_status;
            require(load_sync_session_checkpoint_operator_status(unstaged_conflict_file_post_status_options,
                                                                 unstaged_conflict_file_post_status).ok &&
                    unstaged_conflict_file_post_status.pending_terminal_apply_conflict_file_intent_rows == 0 &&
                    unstaged_conflict_file_post_status.completed_terminal_apply_workorder_rows == 1 &&
                    unstaged_conflict_file_post_status.conflict_file_terminal_apply_targets_materialized == 1 &&
                    unstaged_conflict_file_post_status.suggested_next_action == "idle-clean",
                    "sync checkpoint operator status reports unstaged conflict file transfer plus terminal apply as completed evidence");

            write_file(terminal_conflict_file_target.string(), terminal_conflict_file_local_body);
            fs::remove(terminal_conflict_file_copy_path, apply_cleanup_ec);
            fs::remove(terminal_conflict_file_staging_path, apply_cleanup_ec);
            fs::remove_all(fs::path(terminal_conflict_file_staging_path.string() + ".chunks"), apply_cleanup_ec);

            SyncSessionCheckpointResumeTransferClaimOptions conflict_file_sidecar_claim_options;
            conflict_file_sidecar_claim_options.sqlite_path = terminal_conflict_file_sidecar_checkpoint_db.string();
            conflict_file_sidecar_claim_options.session_id = "session-main";
            conflict_file_sidecar_claim_options.source_root_path = terminal_conflict_file_source_root.string();
            conflict_file_sidecar_claim_options.destination_root_path = terminal_conflict_file_destination_root.string();
            conflict_file_sidecar_claim_options.staging_root_path = terminal_conflict_file_staging_root.string();
            conflict_file_sidecar_claim_options.expected_folder_id = "folder-alpha";
            conflict_file_sidecar_claim_options.expected_source_device_id = "device-bravo";
            conflict_file_sidecar_claim_options.expected_destination_device_id = "device-alpha";
            conflict_file_sidecar_claim_options.expected_peer_id = "peer-bravo";
            conflict_file_sidecar_claim_options.peer_id = "peer-bravo";
            conflict_file_sidecar_claim_options.peer_session_id = "session-main-resume";
            conflict_file_sidecar_claim_options.require_durable_integrity = false;
            conflict_file_sidecar_claim_options.worker_id = "worker-conflict-file-sidecar";
            conflict_file_sidecar_claim_options.worker_lease_epoch = 140;
            conflict_file_sidecar_claim_options.workorder_claim_now_epoch = 1900;
            conflict_file_sidecar_claim_options.worker_lease_seconds = 30;
            conflict_file_sidecar_claim_options.workorder_retry_backoff_seconds = 0;
            SyncSessionCheckpointResumeTransferClaimResult conflict_file_sidecar_claim_result;
            SyncValidationResult conflict_file_sidecar_claim_run =
                claim_sync_session_checkpoint_resume_transfer_workorders(conflict_file_sidecar_claim_options,
                                                                         conflict_file_sidecar_claim_result);
            if (!(conflict_file_sidecar_claim_run.ok &&
                  conflict_file_sidecar_claim_result.transfer_plan_loaded &&
                  conflict_file_sidecar_claim_result.source_filesystem_verified &&
                  conflict_file_sidecar_claim_result.transaction_committed &&
                  conflict_file_sidecar_claim_result.files_claimed == 1 &&
                  conflict_file_sidecar_claim_result.workorder_rows_claimed == terminal_conflict_file_remote_file.chunks.size() &&
                  conflict_file_sidecar_claim_result.files.size() == 1 &&
                  conflict_file_sidecar_claim_result.files[0].path.value == terminal_conflict_file_path.value &&
                  conflict_file_sidecar_claim_result.files[0].workorder_claimed)) {
                std::ostringstream conflict_file_sidecar_claim_diag;
                conflict_file_sidecar_claim_diag << "sync conflict-file sidecar recovery fixture claims conflict remote-byte workorders: "
                                                 << "ok=" << conflict_file_sidecar_claim_run.ok
                                                 << " reason=" << conflict_file_sidecar_claim_run.reason
                                                 << " plan=" << conflict_file_sidecar_claim_result.transfer_plan_loaded
                                                 << " source=" << conflict_file_sidecar_claim_result.source_filesystem_verified
                                                 << " committed=" << conflict_file_sidecar_claim_result.transaction_committed
                                                 << " files_claimed=" << conflict_file_sidecar_claim_result.files_claimed
                                                 << " rows_claimed=" << conflict_file_sidecar_claim_result.workorder_rows_claimed
                                                 << " expected_rows=" << terminal_conflict_file_remote_file.chunks.size();
                throw std::runtime_error(conflict_file_sidecar_claim_diag.str());
            }

            const auto& conflict_file_sidecar_claimed_file = conflict_file_sidecar_claim_result.files[0];
            SyncPeerChunkResponseBatchEnvelope conflict_file_sidecar_peer_response;
            conflict_file_sidecar_peer_response.path = conflict_file_sidecar_claimed_file.path;
            conflict_file_sidecar_peer_response.request_idempotency_key = conflict_file_sidecar_claimed_file.request_idempotency_key;
            conflict_file_sidecar_peer_response.schedule_idempotency_key = conflict_file_sidecar_claimed_file.schedule_idempotency_key;
            conflict_file_sidecar_peer_response.peer_id = conflict_file_sidecar_claimed_file.peer_id;
            conflict_file_sidecar_peer_response.peer_session_id = conflict_file_sidecar_claimed_file.peer_session_id;
            conflict_file_sidecar_peer_response.peer_request_idempotency_key = conflict_file_sidecar_claimed_file.peer_request_idempotency_key;
            conflict_file_sidecar_peer_response.peer_response_batch_idempotency_key = "sync-resume-peer-response-batch:v1:selftest-conflict-file-sidecar";
            conflict_file_sidecar_peer_response.batch_idempotency_key = "sync-resume-chunk-response-batch:v1:selftest-conflict-file-sidecar";
            conflict_file_sidecar_peer_response.remote_entry_digest = sync_manifest_entry_digest(terminal_conflict_file_remote_file);
            conflict_file_sidecar_peer_response.remote_version_digest = sync_manifest_entry_version_digest(terminal_conflict_file_remote_file);
            conflict_file_sidecar_peer_response.apply_entry_idempotency_key = terminal_conflict_file_apply_entry.idempotency_key;
            conflict_file_sidecar_peer_response.response_count = static_cast<std::uint64_t>(terminal_conflict_file_remote_file.chunks.size());
            std::vector<std::string> conflict_file_sidecar_chunk_bytes;
            conflict_file_sidecar_chunk_bytes.reserve(terminal_conflict_file_remote_file.chunks.size());
            for (const auto& chunk : terminal_conflict_file_remote_file.chunks) {
                SyncChunkResponseEnvelope response;
                response.path = conflict_file_sidecar_claimed_file.path;
                response.request_idempotency_key = conflict_file_sidecar_claimed_file.request_idempotency_key;
                response.response_idempotency_key = "sync-resume-peer-response:v1:selftest-conflict-file-sidecar-" + u64_string(chunk.offset);
                response.remote_entry_digest = conflict_file_sidecar_peer_response.remote_entry_digest;
                response.remote_version_digest = conflict_file_sidecar_peer_response.remote_version_digest;
                response.apply_entry_idempotency_key = terminal_conflict_file_apply_entry.idempotency_key;
                response.offset = chunk.offset;
                response.length = chunk.length;
                response.chunk_sha256 = chunk.sha256;
                conflict_file_sidecar_peer_response.total_bytes += chunk.length;
                conflict_file_sidecar_peer_response.responses.push_back(std::move(response));
                conflict_file_sidecar_chunk_bytes.push_back(chunk_bytes_for_body(terminal_conflict_file_remote_body, chunk));
            }

            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions conflict_file_sidecar_binding_options;
            conflict_file_sidecar_binding_options.sqlite_path = terminal_conflict_file_sidecar_checkpoint_db.string();
            conflict_file_sidecar_binding_options.session_id = "session-main";
            conflict_file_sidecar_binding_options.worker_id = conflict_file_sidecar_claim_result.worker_id;
            conflict_file_sidecar_binding_options.worker_lease_id = conflict_file_sidecar_claim_result.worker_lease_id;
            conflict_file_sidecar_binding_options.expected_execution_idempotency_key = conflict_file_sidecar_claimed_file.execution_idempotency_key;
            conflict_file_sidecar_binding_options.binding_now_epoch = 1905;
            SyncSessionCheckpointBoundPeerChunkResponseBatchAcceptanceResult conflict_file_sidecar_acceptance;
            SyncValidationResult conflict_file_sidecar_acceptance_run =
                accept_sync_session_checkpoint_bound_peer_chunk_response_batch_envelope(conflict_file_sidecar_binding_options,
                                                                                       terminal_conflict_file_remote_file,
                                                                                       terminal_conflict_file_apply_entry,
                                                                                       conflict_file_sidecar_peer_response,
                                                                                       conflict_file_sidecar_chunk_bytes,
                                                                                       terminal_conflict_file_chunk_options,
                                                                                       conflict_file_sidecar_acceptance);
            if (!(conflict_file_sidecar_acceptance_run.ok &&
                  conflict_file_sidecar_acceptance.workorder_claim_binding_checked &&
                  conflict_file_sidecar_acceptance.bytes_accepted_after_binding &&
                  conflict_file_sidecar_acceptance.workorder_binding.workorder_rows_bound == terminal_conflict_file_remote_file.chunks.size() &&
                  conflict_file_sidecar_acceptance.peer_batch_acceptance.chunks_written == terminal_conflict_file_remote_file.chunks.size() &&
                  conflict_file_sidecar_acceptance.peer_batch_acceptance.staged_file_complete &&
                  fs::exists(terminal_conflict_file_staging_path) &&
                  read_file(terminal_conflict_file_staging_path.string()) == terminal_conflict_file_remote_body &&
                  !fs::exists(terminal_conflict_file_copy_path))) {
                std::ostringstream conflict_file_sidecar_acceptance_diag;
                conflict_file_sidecar_acceptance_diag << "sync conflict-file sidecar recovery fixture accepts claimed conflict remote bytes without DB advancement: "
                                                      << "ok=" << conflict_file_sidecar_acceptance_run.ok
                                                      << " reason=" << conflict_file_sidecar_acceptance_run.reason
                                                      << " bound=" << conflict_file_sidecar_acceptance.workorder_claim_binding_checked
                                                      << " bytes=" << conflict_file_sidecar_acceptance.bytes_accepted_after_binding
                                                      << " rows_bound=" << conflict_file_sidecar_acceptance.workorder_binding.workorder_rows_bound
                                                      << " chunks_written=" << conflict_file_sidecar_acceptance.peer_batch_acceptance.chunks_written
                                                      << " staged_complete=" << conflict_file_sidecar_acceptance.peer_batch_acceptance.staged_file_complete;
                throw std::runtime_error(conflict_file_sidecar_acceptance_diag.str());
            }

            SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions conflict_file_sidecar_sweep_options;
            conflict_file_sidecar_sweep_options.sqlite_path = terminal_conflict_file_sidecar_checkpoint_db.string();
            conflict_file_sidecar_sweep_options.session_id = "session-main";
            conflict_file_sidecar_sweep_options.worker_id = conflict_file_sidecar_claim_result.worker_id;
            conflict_file_sidecar_sweep_options.worker_lease_id = conflict_file_sidecar_claim_result.worker_lease_id;
            conflict_file_sidecar_sweep_options.binding_now_epoch = 1905;
            SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult conflict_file_sidecar_evidence;
            SyncValidationResult conflict_file_sidecar_evidence_run =
                load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(conflict_file_sidecar_sweep_options,
                                                                                                  conflict_file_sidecar_evidence);
            require(conflict_file_sidecar_evidence_run.ok &&
                    conflict_file_sidecar_evidence.checkpoint_evidence_loaded &&
                    conflict_file_sidecar_evidence.checkpoint_schema_supported &&
                    conflict_file_sidecar_evidence.archived_checkpoint_exact_startup_hydration_supported &&
                    !conflict_file_sidecar_evidence.archived_checkpoint_migration_backfill_required &&
                    conflict_file_sidecar_evidence.claimed_workorder_paths_considered == 1 &&
                    conflict_file_sidecar_evidence.apply_entries_loaded == 1 &&
                    conflict_file_sidecar_evidence.remote_file_entries_loaded == 1 &&
                    conflict_file_sidecar_evidence.apply_entries.size() == 1 &&
                    conflict_file_sidecar_evidence.remote_file_entries.size() == 1 &&
                    conflict_file_sidecar_evidence.apply_entries[0].source_action == SyncPlanAction::RecordConflict &&
                    conflict_file_sidecar_evidence.apply_entries[0].local_action == SyncLocalApplyAction::PreserveConflictCopy &&
                    conflict_file_sidecar_evidence.remote_file_entries[0].path.value == terminal_conflict_file_path.value,
                    "sync session checkpoint conflict-file sidecar recovery hydrates conflict apply evidence from checkpoint");

            SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult conflict_file_sidecar_sweep_result;
            SyncValidationResult conflict_file_sidecar_sweep_run =
                recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_session(conflict_file_sidecar_sweep_options,
                                                                                    conflict_file_sidecar_evidence.remote_file_entries,
                                                                                    conflict_file_sidecar_evidence.apply_entries,
                                                                                    terminal_conflict_file_chunk_options,
                                                                                    conflict_file_sidecar_sweep_result);
            if (!(conflict_file_sidecar_sweep_run.ok &&
                  conflict_file_sidecar_sweep_result.session_sweep_completed &&
                  conflict_file_sidecar_sweep_result.claimed_workorder_paths_considered == 1 &&
                  conflict_file_sidecar_sweep_result.files_attempted == 1 &&
                  conflict_file_sidecar_sweep_result.files_completed == 1 &&
                  conflict_file_sidecar_sweep_result.files_skipped_non_fetch_stage == 0 &&
                  conflict_file_sidecar_sweep_result.workorder_rows_completed == terminal_conflict_file_remote_file.chunks.size() &&
                  conflict_file_sidecar_sweep_result.bytes_verified == terminal_conflict_file_remote_file.size_bytes &&
                  fs::exists(terminal_conflict_file_staging_path) &&
                  read_file(terminal_conflict_file_staging_path.string()) == terminal_conflict_file_remote_body &&
                  !fs::exists(terminal_conflict_file_copy_path) &&
                  read_file(terminal_conflict_file_target.string()) == terminal_conflict_file_local_body)) {
                std::ostringstream conflict_file_sidecar_sweep_diag;
                conflict_file_sidecar_sweep_diag << "sync sidecar recovery completes accepted conflict-file transfer rows before terminal materialization: "
                                                 << "ok=" << conflict_file_sidecar_sweep_run.ok
                                                 << " reason=" << conflict_file_sidecar_sweep_run.reason
                                                 << " completed=" << conflict_file_sidecar_sweep_result.session_sweep_completed
                                                 << " attempted=" << conflict_file_sidecar_sweep_result.files_attempted
                                                 << " files_completed=" << conflict_file_sidecar_sweep_result.files_completed
                                                 << " skipped=" << conflict_file_sidecar_sweep_result.files_skipped_non_fetch_stage
                                                 << " rows=" << conflict_file_sidecar_sweep_result.workorder_rows_completed
                                                 << " expected_rows=" << terminal_conflict_file_remote_file.chunks.size()
                                                 << " groups=" << conflict_file_sidecar_sweep_result.recovery_groups_considered
                                                 << " groups_failed=" << conflict_file_sidecar_sweep_result.recovery_groups_failed
                                                 << " review=" << conflict_file_sidecar_sweep_result.recovery_groups_review_required
                                                 << " missing_sidecar=" << conflict_file_sidecar_sweep_result.recovery_groups_review_missing_sidecar
                                                 << " tampered_sidecar=" << conflict_file_sidecar_sweep_result.recovery_groups_review_tampered_sidecar
                                                 << " staged_mismatch=" << conflict_file_sidecar_sweep_result.recovery_groups_review_staged_bytes_mismatch;
                if (!conflict_file_sidecar_sweep_result.files.empty()) {
                    conflict_file_sidecar_sweep_diag << " file_failure=" << conflict_file_sidecar_sweep_result.files[0].failure_reason
                                                     << " file_review=" << conflict_file_sidecar_sweep_result.files[0].review_required;
                    if (!conflict_file_sidecar_sweep_result.files[0].file_sweep.groups.empty()) {
                        const auto& debug_group = conflict_file_sidecar_sweep_result.files[0].file_sweep.groups[0];
                        conflict_file_sidecar_sweep_diag << " group_failure=" << debug_group.failure_reason
                                                         << " group_review=" << debug_group.review_required
                                                         << " review_reason=" << debug_group.review_reason;
                    }
                }
                throw std::runtime_error(conflict_file_sidecar_sweep_diag.str());
            }

            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions conflict_file_sidecar_materialize_options = terminal_conflict_file_daemon_options;
            conflict_file_sidecar_materialize_options.sqlite_path = terminal_conflict_file_sidecar_checkpoint_db.string();
            conflict_file_sidecar_materialize_options.worker_id = "worker-conflict-file-sidecar-materialize";
            conflict_file_sidecar_materialize_options.daemon_id = "worker-conflict-file-sidecar-materialize-daemon";
            conflict_file_sidecar_materialize_options.initial_worker_lease_epoch = 150;
            conflict_file_sidecar_materialize_options.initial_scheduler_now_epoch = 1920;
            conflict_file_sidecar_materialize_options.max_loop_passes = 1;
            conflict_file_sidecar_materialize_options.recover_bound_peer_sidecars_before_scheduling = false;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult conflict_file_sidecar_materialize_result;
            SyncValidationResult conflict_file_sidecar_materialize_run =
                run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(conflict_file_sidecar_materialize_options,
                                                                                 conflict_file_sidecar_materialize_result);
            if (!(conflict_file_sidecar_materialize_run.ok &&
                  conflict_file_sidecar_materialize_result.daemon_owner_lock_acquired &&
                  conflict_file_sidecar_materialize_result.daemon_owner_lock_released &&
                  conflict_file_sidecar_materialize_result.terminal_apply_workorders_inserted == 1 &&
                  conflict_file_sidecar_materialize_result.terminal_apply_workorders_completed == 1 &&
                  conflict_file_sidecar_materialize_result.terminal_apply_conflict_file_workorders_completed == 1 &&
                  conflict_file_sidecar_materialize_result.terminal_apply_conflict_copies_preserved == 1 &&
                  conflict_file_sidecar_materialize_result.terminal_apply_conflict_remote_files_materialized == 1 &&
                  fs::exists(terminal_conflict_file_target) &&
                  read_file(terminal_conflict_file_target.string()) == terminal_conflict_file_remote_body &&
                  fs::exists(terminal_conflict_file_copy_path) &&
                  read_file(terminal_conflict_file_copy_path.string()) == terminal_conflict_file_local_body &&
                  !fs::exists(terminal_conflict_file_staging_path))) {
                std::ostringstream conflict_file_sidecar_materialize_diag;
                conflict_file_sidecar_materialize_diag << "sync daemon materializes conflict-file bytes recovered from accepted sidecars: "
                                                       << "ok=" << conflict_file_sidecar_materialize_run.ok
                                                       << " reason=" << conflict_file_sidecar_materialize_run.reason
                                                       << " inserted=" << conflict_file_sidecar_materialize_result.terminal_apply_workorders_inserted
                                                       << " completed=" << conflict_file_sidecar_materialize_result.terminal_apply_workorders_completed
                                                       << " conflict_file=" << conflict_file_sidecar_materialize_result.terminal_apply_conflict_file_workorders_completed
                                                       << " preserved=" << conflict_file_sidecar_materialize_result.terminal_apply_conflict_copies_preserved
                                                       << " materialized=" << conflict_file_sidecar_materialize_result.terminal_apply_conflict_remote_files_materialized;
                throw std::runtime_error(conflict_file_sidecar_materialize_diag.str());
            }

            fs::remove(terminal_conflict_file_sidecar_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_sidecar_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_sidecar_checkpoint_db.string() + "-shm"), apply_cleanup_ec);

            fs::remove(terminal_conflict_file_unstaged_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_unstaged_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_unstaged_checkpoint_db.string() + "-shm"), apply_cleanup_ec);

            fs::remove_all(terminal_conflict_file_source_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_file_destination_root, apply_cleanup_ec);
            fs::remove_all(terminal_conflict_file_staging_root, apply_cleanup_ec);
            fs::remove(terminal_conflict_file_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(terminal_conflict_file_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        }
        {
            const fs::path workflow_daemon_gate_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-daemon-gate-" + std::to_string(selftest_ticks) + ".sqlite");
            const fs::path workflow_daemon_gate_config_path = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-daemon-gate-config-" + std::to_string(selftest_ticks) + ".json");
            const fs::path workflow_daemon_gate_report_path = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-daemon-gate-report-" + std::to_string(selftest_ticks) + ".json");
            fs::remove(workflow_daemon_gate_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(workflow_daemon_gate_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(workflow_daemon_gate_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            fs::remove(workflow_daemon_gate_config_path, apply_cleanup_ec);
            fs::remove(workflow_daemon_gate_report_path, apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        workflow_daemon_gate_checkpoint_db,
                                        "sync operator recovery workflow daemon-time gate seed selftest");
            sync_domain_test_access::DaemonOwnerLockRecord workflow_live_owner = sync_domain_test_access::acquire_resume_transfer_daemon_owner_lock_for_fixture(workflow_daemon_gate_checkpoint_db.string(),
                                                                                                                          "session-main",
                                                                                                                          "worker-hotel-prior-daemon",
                                                                                                                          "worker-hotel-prior",
                                                                                                                                     1005,
                                                                                                                          5);
            require(workflow_live_owner.acquired && workflow_live_owner.expires_at_epoch == 1010,
                    "sync operator recovery workflow daemon-time gate fixture starts with an owner lock live only at operator time");
            std::ostringstream workflow_daemon_gate_config;
            workflow_daemon_gate_config << "{\n"
                << "  \"format\": \"anonsync-sync-operator-recovery-workflow-v1\",\n"
                << "  \"checkpoint_path\": \"" << json_escape(workflow_daemon_gate_checkpoint_db.string()) << "\",\n"
                << "  \"session_id\": \"session-main\",\n"
                << "  \"operator_now_epoch\": 1006,\n"
                << "  \"repair\": {\n"
                << "    \"enabled\": false\n"
                << "  },\n"
                << "  \"daemon\": {\n"
                << "    \"enabled\": true,\n"
                << "    \"source_root_path\": \"" << json_escape(fake_source_root.string()) << "\",\n"
                << "    \"destination_root_path\": \"" << json_escape(fake_destination_root.string()) << "\",\n"
                << "    \"staging_root_path\": \"" << json_escape(fake_staging_root.string()) << "\",\n"
                << "    \"expected_folder_id\": \"folder-alpha\",\n"
                << "    \"expected_source_device_id\": \"device-bravo\",\n"
                << "    \"expected_destination_device_id\": \"device-alpha\",\n"
                << "    \"expected_peer_id\": \"peer-bravo\",\n"
                << "    \"peer_session_id\": \"session-main-resume\",\n"
                << "    \"worker_id\": \"worker-workflow-gate\",\n"
                << "    \"daemon_id\": \"worker-workflow-gate-daemon\",\n"
                << "    \"initial_worker_lease_epoch\": 52,\n"
                << "    \"daemon_now_epoch\": 1060,\n"
                << "    \"worker_lease_seconds\": 20,\n"
                << "    \"loop_tick_seconds\": 1,\n"
                << "    \"max_loop_passes\": 1,\n"
                << "    \"max_scheduler_actions_per_pass\": " << pending_materialize_entry->chunks.size() << ",\n"
                << "    \"workorder_retry_backoff_seconds\": 0,\n"
                << "    \"recover_bound_peer_sidecars_before_scheduling\": false,\n"
                << "    \"require_daemon_owner_lock\": true\n"
                << "  }\n"
                << "}\n";
            write_file(workflow_daemon_gate_config_path.string(), workflow_daemon_gate_config.str());
            int workflow_daemon_gate_rc = run_sync_checkpoint_operator_recovery_workflow_command(workflow_daemon_gate_config_path.string(),
                                                                                                  workflow_daemon_gate_report_path.string());
            Json workflow_daemon_gate_report = load_json(workflow_daemon_gate_report_path.string());
            require(workflow_daemon_gate_rc == 0 &&
                    workflow_daemon_gate_report.at("format").str() == "anonsync-sync-operator-recovery-workflow-report-v1" &&
                    workflow_daemon_gate_report.at("revision_id").str() == "rev0741" &&
                    workflow_daemon_gate_report.at("ok").boolean(false) &&
                    workflow_daemon_gate_report.at("workflow").at("initial_suggested_next_action").str() == "wait-daemon-owner-lock" &&
                    workflow_daemon_gate_report.at("workflow").at("pre_daemon_status_loaded").boolean(false) &&
                    workflow_daemon_gate_report.at("pre_daemon_status_report").at("status").at("daemon_owner_lock_live").boolean(true) == false &&
                    workflow_daemon_gate_report.at("pre_daemon_status_report").at("status").at("suggested_next_action").str() == "run-daemon-reclaim-retry" &&
                    workflow_daemon_gate_report.at("workflow").at("daemon_attempted").boolean(false) &&
                    workflow_daemon_gate_report.at("daemon_run_report").at("daemon_loop").at("daemon_owner_lock_reclaimed_expired").boolean(false) &&
                    workflow_daemon_gate_report.at("daemon_run_report").at("daemon_loop").at("workorder_rows_reclaimed").integer(-1) == static_cast<long long>(pending_materialize_entry->chunks.size()) &&
                    workflow_daemon_gate_report.at("final_status_report").at("status").at("suggested_next_action").str() == "wait-live-lease-or-run-owner",
                    "sync operator recovery workflow gates daemon entry at daemon time so an expired prior owner can be reclaimed without manual status reruns");
            require(count_session_rows_in_checkpoint(workflow_daemon_gate_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_daemon_owner_locks WHERE session_id=? AND daemon_id='worker-workflow-gate-daemon' AND lock_state='released';",
                                                     "workflow daemon gate released owner lock count") == 1 &&
                    count_session_rows_in_checkpoint(workflow_daemon_gate_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND worker_id='worker-workflow-gate' AND work_state='claimed' AND claimed_at_epoch=1060;",
                                                     "workflow daemon gate claimed row count") == pending_materialize_entry->chunks.size(),
                    "sync operator recovery workflow daemon branch leaves durable owner-lock release and claimed workorder evidence");
            fs::remove(workflow_daemon_gate_config_path, apply_cleanup_ec);
            if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow daemon gate config: " + apply_cleanup_ec.message());
            fs::remove(workflow_daemon_gate_report_path, apply_cleanup_ec);
            if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow daemon gate report: " + apply_cleanup_ec.message());
            fs::remove(workflow_daemon_gate_checkpoint_db, apply_cleanup_ec);
            if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow daemon gate db: " + apply_cleanup_ec.message());
            fs::remove(fs::path(workflow_daemon_gate_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(workflow_daemon_gate_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        }
        {
            const fs::path daemon_cli_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-cli-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(daemon_cli_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(daemon_cli_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(daemon_cli_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                        daemon_cli_checkpoint_db,
                                        "sync checkpoint daemon CLI selftest");
            const fs::path daemon_cli_report_path = fs::temp_directory_path() / ("anonsync-sync-daemon-cli-" + std::to_string(selftest_ticks) + ".json");
            const fs::path daemon_cli_heartbeat_path = fs::temp_directory_path() / ("anonsync-sync-daemon-cli-heartbeat-" + std::to_string(selftest_ticks) + ".json");
            fs::remove(daemon_cli_report_path, apply_cleanup_ec);
            fs::remove(daemon_cli_heartbeat_path, apply_cleanup_ec);
            int daemon_cli_rc = run_sync_checkpoint_daemon_run_command(daemon_cli_checkpoint_db.string(),
                                                                       "session-main",
                                                                       fake_source_root.string(),
                                                                       fake_destination_root.string(),
                                                                       fake_staging_root.string(),
                                                                       "folder-alpha",
                                                                       "device-bravo",
                                                                       "device-alpha",
                                                                       "peer-bravo",
                                                                       "peer-bravo",
                                                                       "session-main",
                                                                       "worker-cli",
                                                                       "",
                                                                       41,
                                                                       1005,
                                                                       10,
                                                                       1,
                                                                       1,
                                                                       checked_cli_integer_for_selftest(
                                                                           pending_materialize_entry->chunks.size(),
                                                                           "sync checkpoint daemon max actions"),
                                                                       0,
                                                                       false,
                                                                       true,
                                                                       daemon_cli_report_path.string(),
                                                                       daemon_cli_heartbeat_path.string(),
                                                                       9);
            Json daemon_cli_report = load_json(daemon_cli_report_path.string());
            Json daemon_cli_heartbeat = load_json(daemon_cli_heartbeat_path.string());
            require(daemon_cli_rc == 0 &&
                    daemon_cli_report.at("format").str() == "anonsync-sync-checkpoint-daemon-run-report-v1" &&
                    daemon_cli_report.at("ok").boolean(false) &&
                    daemon_cli_report.at("daemon_loop").at("daemon_loop_completed").boolean(false) &&
                    daemon_cli_report.at("daemon_loop").at("daemon_owner_lock_acquired").boolean(false) &&
                    daemon_cli_report.at("daemon_loop").at("daemon_owner_lock_released").boolean(false) &&
                    daemon_cli_report.at("daemon_loop").at("daemon_heartbeat_written").boolean(false) &&
                    daemon_cli_report.at("daemon_loop").at("daemon_heartbeat_final").boolean(false) &&
                    daemon_cli_report.at("daemon_loop").at("daemon_heartbeat_state").str() == "completed" &&
                    daemon_cli_report.at("daemon_loop").at("daemon_heartbeat_writes").integer(-1) >= 4 &&
                    daemon_cli_report.at("daemon_loop").at("passes_completed").integer(-1) == 1 &&
                    daemon_cli_heartbeat.at("format").str() == "anonsync-sync-daemon-service-heartbeat-v2" &&
                    daemon_cli_heartbeat.at("revision_id").str() == "rev0840" &&
                    daemon_cli_heartbeat.at("process_incarnation").at("process_id").integer(-1) ==
                        daemon_cli_heartbeat.at("process_id").integer(-2) &&
                    !daemon_cli_heartbeat.at("process_incarnation").at("format").str().empty() &&
                    daemon_cli_heartbeat.at("state").str() == "completed" &&
                    daemon_cli_heartbeat.at("final").boolean(false) &&
                    daemon_cli_heartbeat.at("stale_after_seconds").integer(-1) == 9 &&
                    daemon_cli_heartbeat.at("owner_lock").at("released").boolean(false) &&
                    daemon_cli_heartbeat.at("progress").at("passes_completed").integer(-1) == 1,
                    "sync checkpoint daemon CLI writes an external heartbeat file tied to owner-fenced scheduler progress");
        }
        SyncSessionCheckpointResumeTransferClaimOptions too_early_backoff_reclaim_options = backoff_claim_options;
        too_early_backoff_reclaim_options.worker_id = "worker-delta";
        too_early_backoff_reclaim_options.worker_lease_epoch = 9;
        too_early_backoff_reclaim_options.workorder_claim_now_epoch = 1010;
        too_early_backoff_reclaim_options.worker_lease_seconds = 15;
        SyncSessionCheckpointResumeTransferClaimResult too_early_backoff_reclaim_result;
        SyncValidationResult too_early_backoff_reclaim_run = claim_sync_session_checkpoint_resume_transfer_workorders(too_early_backoff_reclaim_options,
                                                                                                                       too_early_backoff_reclaim_result);
        require(!too_early_backoff_reclaim_run.ok,
                "sync session checkpoint resume transfer claim refuses expired rows before retry-at backoff opens");
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(retry_backoff_checkpoint_db, 1010);
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.queue_facts_returned == pending_materialize_entry->chunks.size() &&
                    queue_result.expired_cooling_down_rows == pending_materialize_entry->chunks.size() &&
                    !queue_result.facts.empty() &&
                    queue_result.facts[0].queue_kind == SyncSessionCheckpointResumeTransferWorkorderQueueKind::ExpiredCoolingDown &&
                    queue_result.facts[0].lease_expired &&
                    !queue_result.facts[0].retry_window_open,
                    "sync session checkpoint resume transfer queue selector keeps expired rows cooling down until retry-at opens");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions scheduler_options = make_transfer_workorder_scheduler_options(retry_backoff_checkpoint_db, 1010);
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult scheduler_result;
            SyncValidationResult scheduler_run = plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_options, scheduler_result);
            require(scheduler_run.ok &&
                    scheduler_result.scheduler_plan_completed &&
                    scheduler_result.scheduler_actions_returned == pending_materialize_entry->chunks.size() &&
                    scheduler_result.mutating_actions_planned == 0 &&
                    scheduler_result.wait_retry_backoff_actions == pending_materialize_entry->chunks.size() &&
                    !scheduler_result.actions.empty() &&
                    scheduler_result.actions[0].action_kind == SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::WaitRetryBackoff &&
                    !scheduler_result.actions[0].mutating_action,
                    "sync session checkpoint resume transfer scheduler pass waits instead of reclaiming during retry-at cooldown");
        }
        SyncSessionCheckpointResumeTransferClaimOptions open_backoff_reclaim_options = too_early_backoff_reclaim_options;
        open_backoff_reclaim_options.workorder_claim_now_epoch = 1015;
        SyncSessionCheckpointResumeTransferClaimResult open_backoff_reclaim_result;
        SyncValidationResult open_backoff_reclaim_run = claim_sync_session_checkpoint_resume_transfer_workorders(open_backoff_reclaim_options,
                                                                                                                  open_backoff_reclaim_result);
        require(open_backoff_reclaim_run.ok &&
                open_backoff_reclaim_result.worker_id == "worker-delta" &&
                open_backoff_reclaim_result.workorder_claim_now_epoch == 1015 &&
                open_backoff_reclaim_result.lease_expires_at_epoch == 1030 &&
                open_backoff_reclaim_result.workorder_retry_backoff_seconds == 5 &&
                open_backoff_reclaim_result.retry_at_epoch == 1040 &&
                open_backoff_reclaim_result.workorder_rows_reclaimed == pending_materialize_entry->chunks.size() &&
                open_backoff_reclaim_result.workorder_reclaim_events_written == pending_materialize_entry->chunks.size() &&
                open_backoff_reclaim_result.files.size() == 1 &&
                open_backoff_reclaim_result.files[0].claimed_at_epoch == 1015 &&
                open_backoff_reclaim_result.files[0].lease_expires_at_epoch == 1030 &&
                open_backoff_reclaim_result.files[0].retry_at_epoch == 1040,
                "sync session checkpoint resume transfer claim reclaims only after retry-at backoff opens and schedules the next attempt");
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(retry_backoff_checkpoint_db, 1040);
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.queue_facts_returned == pending_materialize_entry->chunks.size() &&
                    queue_result.expired_reclaim_ready_rows == pending_materialize_entry->chunks.size() &&
                    !queue_result.facts.empty() &&
                    queue_result.facts[0].queue_kind == SyncSessionCheckpointResumeTransferWorkorderQueueKind::ExpiredReclaimReady &&
                    queue_result.facts[0].reclaim_events_recorded == 1,
                    "sync session checkpoint resume transfer queue selector exposes retry-open expired rows as reclaim-ready facts");
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions capped_queue_options = queue_options;
            capped_queue_options.max_workorder_claim_attempts = 2;
            SyncSessionCheckpointResumeTransferWorkorderQueueResult capped_queue_result;
            SyncValidationResult capped_queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(capped_queue_options, capped_queue_result);
            require(capped_queue_run.ok &&
                    capped_queue_result.expired_abandon_ready_rows == pending_materialize_entry->chunks.size() &&
                    capped_queue_result.expired_reclaim_ready_rows == 0 &&
                    !capped_queue_result.facts.empty() &&
                    capped_queue_result.facts[0].queue_kind == SyncSessionCheckpointResumeTransferWorkorderQueueKind::ExpiredAbandonReady,
                    "sync session checkpoint resume transfer queue selector distinguishes retry-open rows at the abandon attempt cap");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions scheduler_options = make_transfer_workorder_scheduler_options(retry_backoff_checkpoint_db, 1040);
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult scheduler_result;
            SyncValidationResult scheduler_run = plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_options, scheduler_result);
            require(scheduler_run.ok &&
                    scheduler_result.scheduler_plan_completed &&
                    scheduler_result.claim_or_reclaim_expired_actions == pending_materialize_entry->chunks.size() &&
                    scheduler_result.abandon_expired_actions == 0 &&
                    scheduler_result.mutating_actions_planned == pending_materialize_entry->chunks.size() &&
                    !scheduler_result.actions.empty() &&
                    scheduler_result.actions[0].action_kind == SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::ClaimOrReclaimExpired &&
                    scheduler_result.actions[0].retry_window_open,
                    "sync session checkpoint resume transfer scheduler pass maps retry-open expired rows to claim-or-reclaim actions");
            scheduler_options.max_workorder_claim_attempts = 2;
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult capped_scheduler_result;
            SyncValidationResult capped_scheduler_run = plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_options, capped_scheduler_result);
            require(capped_scheduler_run.ok &&
                    capped_scheduler_result.scheduler_plan_completed &&
                    capped_scheduler_result.claim_or_reclaim_expired_actions == 0 &&
                    capped_scheduler_result.abandon_expired_actions == pending_materialize_entry->chunks.size() &&
                    capped_scheduler_result.mutating_actions_planned == pending_materialize_entry->chunks.size() &&
                    !capped_scheduler_result.actions.empty() &&
                    capped_scheduler_result.actions[0].action_kind == SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::AbandonExpired,
                    "sync session checkpoint resume transfer scheduler pass maps retry-open attempt-cap rows to abandon actions");
        }
        {
            SyncSqliteDb backoff_probe_handle;
            int backoff_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            backoff_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(retry_backoff_checkpoint_db.string().c_str(), backoff_probe_handle.db.out(), backoff_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(backoff_probe_handle.db, "could not reopen checkpoint db for retry-backoff resume transfer workorder probe"));
            }
            const std::uint64_t reclaimed_backoff_rows = sqlite_count_for_session_or_throw(backoff_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-delta' AND claimed_at_epoch=1015 AND lease_expires_at_epoch=1030 AND retry_at_epoch=1040 AND claim_attempts=2;",
                "session-main",
                "resume transfer retry-backoff reclaimed workorder count");
            const std::uint64_t retry_backoff_reclaim_events = sqlite_count_for_session_or_throw(backoff_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_reclaim_events WHERE session_id=? AND previous_worker_id='worker-charlie' AND previous_retry_at_epoch=1015 AND new_worker_id='worker-delta' AND new_retry_at_epoch=1040 AND reclaim_attempt=2 AND reclaim_reason='expired-lease';",
                "session-main",
                "resume transfer retry-backoff reclaim audit event count");
            require(reclaimed_backoff_rows == pending_materialize_entry->chunks.size() &&
                    retry_backoff_reclaim_events == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer retry-at backoff persists row schedule and event schedule evidence");
        }
        const fs::path quarantine_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-workorder-quarantine-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(quarantine_checkpoint_db, apply_cleanup_ec);
        fs::remove(fs::path(quarantine_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(quarantine_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                    quarantine_checkpoint_db,
                                    "sync session checkpoint resume transfer workorder quarantine selftest");
        SyncSessionCheckpointResumeTransferClaimOptions quarantine_initial_claim_options = transfer_claim_options;
        quarantine_initial_claim_options.sqlite_path = quarantine_checkpoint_db.string();
        SyncSessionCheckpointResumeTransferClaimResult quarantine_initial_claim_result;
        SyncValidationResult quarantine_initial_claim_run = claim_sync_session_checkpoint_resume_transfer_workorders(quarantine_initial_claim_options,
                                                                                                                     quarantine_initial_claim_result);
        require(quarantine_initial_claim_run.ok &&
                quarantine_initial_claim_result.workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                quarantine_initial_claim_result.workorder_rows_quarantined == 0,
                "sync session checkpoint resume transfer quarantine fixture starts from claimed rows");
        {
            SyncSqliteDb quarantine_mutation_handle;
            int quarantine_mutation_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            quarantine_mutation_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(quarantine_checkpoint_db.string().c_str(), quarantine_mutation_handle.db.out(), quarantine_mutation_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(quarantine_mutation_handle.db, "could not reopen checkpoint db for workorder quarantine mutation"));
            }
            sqlite_exec_or_throw(quarantine_mutation_handle.db,
                                 "UPDATE sync_session_resume_transfer_workorders "
                                 "SET schedule_idempotency_key='sync-resume-peer-schedule:v1:quarantine-mismatch' "
                                 "WHERE session_id='session-main' AND path='docs/session-report.txt' "
                                 "AND chunk_offset=(SELECT MIN(chunk_offset) FROM sync_session_resume_transfer_workorders WHERE session_id='session-main' AND path='docs/session-report.txt');",
                                 "could not inject resume transfer workorder evidence mismatch for quarantine selftest");
        }
        SyncSessionCheckpointResumeTransferClaimResult quarantine_mismatch_result;
        SyncValidationResult quarantine_mismatch_run = claim_sync_session_checkpoint_resume_transfer_workorders(quarantine_initial_claim_options,
                                                                                                                quarantine_mismatch_result);
        require(quarantine_mismatch_run.ok &&
                quarantine_mismatch_result.transaction_committed &&
                quarantine_mismatch_result.files_quarantined == 1 &&
                quarantine_mismatch_result.files_claimed == 0 &&
                quarantine_mismatch_result.workorder_rows_quarantined == 1 &&
                quarantine_mismatch_result.workorder_quarantine_events_written == 1 &&
                quarantine_mismatch_result.workorder_rows_already_owned == pending_materialize_entry->chunks.size() - 1 &&
                quarantine_mismatch_result.workorder_rows_claimed == pending_materialize_entry->chunks.size() - 1 &&
                quarantine_mismatch_result.files.size() == 1 &&
                quarantine_mismatch_result.files[0].workorder_rows_quarantined == 1 &&
                quarantine_mismatch_result.files[0].workorder_quarantine_events_written == 1,
                "sync session checkpoint resume transfer claim quarantines mismatched claimed workorder evidence without rolling back the audit event");
        {
            SyncSqliteDb quarantine_probe_handle;
            int quarantine_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            quarantine_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(quarantine_checkpoint_db.string().c_str(), quarantine_probe_handle.db.out(), quarantine_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(quarantine_probe_handle.db, "could not reopen checkpoint db for workorder quarantine probe"));
            }
            const std::uint64_t quarantined_workorder_rows = sqlite_count_for_session_or_throw(quarantine_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='quarantined';",
                "session-main",
                "resume transfer quarantined workorder count");
            const std::uint64_t quarantine_event_rows = sqlite_count_for_session_or_throw(quarantine_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_quarantine_events WHERE session_id=? AND previous_schedule_idempotency_key='sync-resume-peer-schedule:v1:quarantine-mismatch' AND expected_schedule_idempotency_key LIKE 'sync-resume-peer-schedule:v1:%' AND quarantine_reason='plan-evidence-mismatch';",
                "session-main",
                "resume transfer workorder quarantine audit event count");
            require(quarantined_workorder_rows == 1 && quarantine_event_rows == 1,
                    "sync session checkpoint resume transfer quarantine persists previous and expected schedule evidence");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(quarantine_checkpoint_db, 1000);
            queue_options.worker_id = quarantine_initial_claim_result.worker_id;
            queue_options.worker_lease_id = quarantine_initial_claim_result.worker_lease_id;
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.quarantined_review_rows == 1 &&
                    queue_result.owned_claim_ready_rows == pending_materialize_entry->chunks.size() - 1 &&
                    queue_result.queue_facts_returned == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer queue selector exposes quarantined rows only as terminal review facts");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions scheduler_options = make_transfer_workorder_scheduler_options(quarantine_checkpoint_db, 1000);
            scheduler_options.worker_id = quarantine_initial_claim_result.worker_id;
            scheduler_options.worker_lease_id = quarantine_initial_claim_result.worker_lease_id;
            SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult scheduler_result;
            SyncValidationResult scheduler_run = plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_options, scheduler_result);
            require(scheduler_run.ok &&
                    scheduler_result.scheduler_plan_completed &&
                    scheduler_result.review_quarantined_actions == 1 &&
                    scheduler_result.execute_owned_claim_actions == pending_materialize_entry->chunks.size() - 1 &&
                    scheduler_result.mutating_actions_planned == pending_materialize_entry->chunks.size() - 1 &&
                    scheduler_result.actions.size() == pending_materialize_entry->chunks.size() &&
                    scheduler_result.actions[0].action_kind == SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::ReviewQuarantined &&
                    scheduler_result.actions[0].terminal_review_required &&
                    !scheduler_result.actions[0].mutating_action &&
                    scheduler_result.actions[0].scheduler_priority == 1 &&
                    scheduler_result.actions[0].scheduler_group_priority == 1 &&
                    scheduler_result.actions[0].scheduler_group_size == 1,
                    "sync session checkpoint resume transfer scheduler pass surfaces quarantined rows before preserving owned runnable rows");
        }
        const fs::path quarantine_scheduler_fence_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-workorder-quarantine-scheduler-fence-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(quarantine_scheduler_fence_checkpoint_db, apply_cleanup_ec);
        fs::remove(fs::path(quarantine_scheduler_fence_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(quarantine_scheduler_fence_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(quarantine_checkpoint_db,
                                    quarantine_scheduler_fence_checkpoint_db,
                                    "sync session checkpoint resume transfer scheduler terminal-review fence selftest");
        {
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions fence_options =
                make_transfer_workorder_scheduler_execution_options(quarantine_scheduler_fence_checkpoint_db,
                                                                   1000,
                                                                   quarantine_initial_claim_result.worker_id,
                                                                   quarantine_initial_claim_options.worker_lease_epoch,
                                                                   quarantine_initial_claim_options.worker_lease_seconds);
            fence_options.max_scheduler_actions = static_cast<std::uint64_t>(pending_materialize_entry->chunks.size());
            fence_options.block_mutating_actions_on_terminal_review = true;
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult fence_result;
            SyncValidationResult fence_run = execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(fence_options,
                                                                                                                       fence_result);
            require(fence_run.ok &&
                    fence_result.scheduler_execution_completed &&
                    fence_result.scheduler_actions_returned == pending_materialize_entry->chunks.size() &&
                    fence_result.mutating_actions_planned == pending_materialize_entry->chunks.size() - 1 &&
                    fence_result.terminal_review_present &&
                    fence_result.terminal_review_actions_observed == 1 &&
                    fence_result.mutations_blocked_by_terminal_review &&
                    fence_result.mutating_action_groups_blocked_by_terminal_review == 1 &&
                    fence_result.mutating_actions_blocked_by_terminal_review == pending_materialize_entry->chunks.size() - 1 &&
                    fence_result.mutating_action_groups_selected == 0 &&
                    fence_result.execute_owned_claim_actions_selected == 0 &&
                    fence_result.execution_key_filters_built == 0 &&
                    fence_result.claim_or_abandon_runs == 0 &&
                    fence_result.execute_owned_runs == 0 &&
                    fence_result.workorder_rows_completed == 0 &&
                    fence_result.chunks_written == 0 &&
                    fence_result.receipt_rows_upserted == 0 &&
                    !fence_result.scheduler_result.actions.empty() &&
                    fence_result.scheduler_result.actions[0].action_kind == SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::ReviewQuarantined,
                    "sync session checkpoint scheduler terminal-review fence blocks every selected mutation before key filters or mutators run");
            require(count_session_rows_in_checkpoint(quarantine_scheduler_fence_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed';",
                                                     "scheduler terminal-review fence claimed workorder count") == pending_materialize_entry->chunks.size() - 1 &&
                    count_session_rows_in_checkpoint(quarantine_scheduler_fence_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='quarantined';",
                                                     "scheduler terminal-review fence quarantined workorder count") == 1 &&
                    count_session_rows_in_checkpoint(quarantine_scheduler_fence_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_quarantine_events WHERE session_id=?;",
                                                     "scheduler terminal-review fence quarantine event count") == 1,
                    "sync session checkpoint scheduler terminal-review fence preserves runnable, quarantined, and audit rows exactly");
        }
        const fs::path quarantine_daemon_fence_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-workorder-quarantine-daemon-fence-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(quarantine_daemon_fence_checkpoint_db, apply_cleanup_ec);
        fs::remove(fs::path(quarantine_daemon_fence_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(quarantine_daemon_fence_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(quarantine_checkpoint_db,
                                    quarantine_daemon_fence_checkpoint_db,
                                    "sync session checkpoint resume transfer daemon terminal-review fence selftest");
        {
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions fence_loop_options =
                make_transfer_workorder_daemon_loop_options(quarantine_daemon_fence_checkpoint_db,
                                                           1000,
                                                           quarantine_initial_claim_result.worker_id,
                                                           quarantine_initial_claim_options.worker_lease_epoch,
                                                           quarantine_initial_claim_options.worker_lease_seconds);
            fence_loop_options.daemon_id = "daemon-review-fence";
            fence_loop_options.max_scheduler_actions_per_pass = static_cast<std::uint64_t>(pending_materialize_entry->chunks.size());
            fence_loop_options.max_loop_passes = 1;
            fence_loop_options.stop_after_idle_pass = false;
            fence_loop_options.stop_on_deferred_actions = false;
            fence_loop_options.stop_on_terminal_review = true;
            fence_loop_options.require_daemon_owner_lock = false;
            SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult fence_loop_result;
            SyncValidationResult fence_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(fence_loop_options,
                                                                                                                    fence_loop_result);
            require(fence_loop_run.ok &&
                    fence_loop_result.daemon_loop_completed &&
                    fence_loop_result.stopped_on_terminal_review &&
                    fence_loop_result.passes_attempted == 1 &&
                    fence_loop_result.passes_completed == 1 &&
                    fence_loop_result.idle_passes == 1 &&
                    fence_loop_result.mutating_passes == 0 &&
                    fence_loop_result.terminal_review_actions_observed == 1 &&
                    fence_loop_result.mutations_blocked_by_terminal_review &&
                    fence_loop_result.mutating_action_groups_blocked_by_terminal_review == 1 &&
                    fence_loop_result.mutating_actions_blocked_by_terminal_review == pending_materialize_entry->chunks.size() - 1 &&
                    fence_loop_result.mutating_action_groups_selected == 0 &&
                    fence_loop_result.execution_key_filters_built == 0 &&
                    fence_loop_result.claim_or_abandon_runs == 0 &&
                    fence_loop_result.execute_owned_runs == 0 &&
                    fence_loop_result.workorder_rows_completed == 0 &&
                    fence_loop_result.chunks_written == 0 &&
                    fence_loop_result.pass_results.size() == 1 &&
                    fence_loop_result.pass_results[0].terminal_review_present &&
                    fence_loop_result.pass_results[0].mutations_blocked_by_terminal_review,
                    "sync checkpoint daemon stop-on-terminal-review is now a pre-mutation fence rather than a post-mutation stop condition");
            require(count_session_rows_in_checkpoint(quarantine_daemon_fence_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed';",
                                                     "daemon terminal-review fence claimed workorder count") == pending_materialize_entry->chunks.size() - 1 &&
                    count_session_rows_in_checkpoint(quarantine_daemon_fence_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='quarantined';",
                                                     "daemon terminal-review fence quarantined workorder count") == 1 &&
                    count_session_rows_in_checkpoint(quarantine_daemon_fence_checkpoint_db,
                                                     "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_quarantine_events WHERE session_id=?;",
                                                     "daemon terminal-review fence quarantine event count") == 1,
                    "sync checkpoint daemon terminal-review fence preserves pending work and durable review evidence");
        }
        SyncSessionCheckpointResumeTransferTerminalResetOptions quarantine_reset_without_permission_options;
        quarantine_reset_without_permission_options.sqlite_path = quarantine_checkpoint_db.string();
        quarantine_reset_without_permission_options.session_id = "session-main";
        quarantine_reset_without_permission_options.source_root_path = fake_source_root.string();
        quarantine_reset_without_permission_options.destination_root_path = fake_destination_root.string();
        quarantine_reset_without_permission_options.staging_root_path = fake_staging_root.string();
        quarantine_reset_without_permission_options.expected_folder_id = "folder-alpha";
        quarantine_reset_without_permission_options.expected_source_device_id = "device-bravo";
        quarantine_reset_without_permission_options.expected_destination_device_id = "device-alpha";
        quarantine_reset_without_permission_options.expected_peer_id = "peer-bravo";
        quarantine_reset_without_permission_options.peer_session_id = "session-main-resume";
        quarantine_reset_without_permission_options.worker_id = "worker-hotel";
        quarantine_reset_without_permission_options.worker_lease_epoch = 12;
        quarantine_reset_without_permission_options.workorder_reset_now_epoch = 1030;
        quarantine_reset_without_permission_options.worker_lease_seconds = 20;
        quarantine_reset_without_permission_options.workorder_retry_backoff_seconds = 5;
        quarantine_reset_without_permission_options.reset_abandoned_workorders = false;
        quarantine_reset_without_permission_options.reset_quarantined_workorders = false;
        SyncSessionCheckpointResumeTransferTerminalResetResult quarantine_reset_without_permission_result;
        SyncValidationResult quarantine_reset_without_permission_run = reset_sync_session_checkpoint_resume_transfer_terminal_workorders(quarantine_reset_without_permission_options,
                                                                                                                                          quarantine_reset_without_permission_result);
        require(!quarantine_reset_without_permission_run.ok,
                "sync session checkpoint resume transfer terminal reset requires explicit terminal-state permission");
        SyncSessionCheckpointResumeTransferTerminalResetOptions quarantine_reset_options = quarantine_reset_without_permission_options;
        quarantine_reset_options.reset_quarantined_workorders = true;
        SyncSessionCheckpointResumeTransferTerminalResetResult quarantine_reset_result;
        SyncValidationResult quarantine_reset_run = reset_sync_session_checkpoint_resume_transfer_terminal_workorders(quarantine_reset_options,
                                                                                                                      quarantine_reset_result);
        require(quarantine_reset_run.ok &&
                quarantine_reset_result.transaction_committed &&
                quarantine_reset_result.worker_id == "worker-hotel" &&
                quarantine_reset_result.workorder_reset_now_epoch == 1030 &&
                quarantine_reset_result.lease_expires_at_epoch == 1050 &&
                quarantine_reset_result.retry_at_epoch == 1055 &&
                quarantine_reset_result.files_reset == 1 &&
                quarantine_reset_result.terminal_rows_found == 1 &&
                quarantine_reset_result.workorder_rows_reset == 1 &&
                quarantine_reset_result.abandoned_rows_reset == 0 &&
                quarantine_reset_result.quarantined_rows_reset == 1 &&
                quarantine_reset_result.reset_events_written == 1 &&
                quarantine_reset_result.files.size() == 1 &&
                quarantine_reset_result.files[0].quarantined_rows_reset == 1 &&
                quarantine_reset_result.files[0].reset_events_written == 1,
                "sync session checkpoint resume transfer terminal reset can deliberately reopen quarantined rows with durable reset evidence");
        {
            SyncSqliteDb quarantine_reset_probe_handle;
            int quarantine_reset_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            quarantine_reset_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(quarantine_checkpoint_db.string().c_str(), quarantine_reset_probe_handle.db.out(), quarantine_reset_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(quarantine_reset_probe_handle.db, "could not reopen checkpoint db for workorder quarantine reset probe"));
            }
            const std::uint64_t reset_quarantine_claimed_rows = sqlite_count_for_session_or_throw(quarantine_reset_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-hotel' AND claimed_at_epoch=1030 AND lease_expires_at_epoch=1050 AND retry_at_epoch=1055 AND claim_attempts=1;",
                "session-main",
                "resume transfer reset quarantined workorder claimed count");
            const std::uint64_t reset_quarantine_event_rows = sqlite_count_for_session_or_throw(quarantine_reset_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_reset_events WHERE session_id=? AND previous_work_state='quarantined' AND previous_schedule_idempotency_key='sync-resume-peer-schedule:v1:quarantine-mismatch' AND new_schedule_idempotency_key LIKE 'sync-resume-peer-schedule:v1:%' AND new_worker_id='worker-hotel' AND reset_at_epoch=1030 AND reset_reason='operator-terminal-reset';",
                "session-main",
                "resume transfer quarantined workorder reset audit event count");
            require(reset_quarantine_claimed_rows == 1 && reset_quarantine_event_rows == 1,
                    "sync session checkpoint resume transfer terminal reset preserves quarantine evidence while reopening current-plan work");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(quarantine_checkpoint_db, 1030);
            queue_options.worker_id = quarantine_reset_result.worker_id;
            queue_options.worker_lease_id = quarantine_reset_result.worker_lease_id;
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.owned_claim_ready_rows == 1 &&
                    queue_result.reset_history_claimed_rows == 1 &&
                    queue_result.expired_reclaim_ready_rows == pending_materialize_entry->chunks.size() - 1,
                    "sync session checkpoint resume transfer queue selector returns reset quarantine rows as fresh owned claimed work while leaving old claims reclaimable");
        }

        SyncSessionCheckpointResumeTransferClaimResult transfer_claim_result;
        SyncValidationResult transfer_claim_run = claim_sync_session_checkpoint_resume_transfer_workorders(transfer_claim_options,
                                                                                                           transfer_claim_result);
        require(transfer_claim_run.ok &&
                transfer_claim_result.transfer_plan_loaded &&
                transfer_claim_result.worker_id == "worker-charlie" &&
                transfer_claim_result.worker_lease_id.starts_with("sync-resume-transfer-lease:v1:") &&
                transfer_claim_result.durable_integrity_verified &&
                transfer_claim_result.source_filesystem_verified &&
                transfer_claim_result.transaction_committed &&
                transfer_claim_result.workorder_claim_now_epoch == 1000 &&
                transfer_claim_result.worker_lease_seconds == 10 &&
                transfer_claim_result.lease_expires_at_epoch == 1010 &&
                transfer_claim_result.files_considered == fake_session_result.files_materialized &&
                transfer_claim_result.files_claimed == 1 &&
                transfer_claim_result.files_skipped == 0 &&
                transfer_claim_result.workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                transfer_claim_result.workorder_rows_already_owned == 0 &&
                transfer_claim_result.workorder_rows_reclaimed == 0 &&
                transfer_claim_result.workorder_reclaim_events_written == 0 &&
                transfer_claim_result.chunks_assigned == pending_materialize_entry->chunks.size() &&
                transfer_claim_result.files.size() == 1 &&
                transfer_claim_result.files[0].path.value == "docs/session-report.txt" &&
                transfer_claim_result.files[0].execution_idempotency_key.starts_with("sync-resume-transfer-execute:v1:") &&
                transfer_claim_result.files[0].workorder_claimed &&
                transfer_claim_result.files[0].claimed_at_epoch == 1000 &&
                transfer_claim_result.files[0].lease_expires_at_epoch == 1010 &&
                transfer_claim_result.files[0].workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                transfer_claim_result.files[0].workorder_rows_already_owned == 0 &&
                transfer_claim_result.files[0].workorder_rows_reclaimed == 0 &&
                transfer_claim_result.files[0].workorder_reclaim_events_written == 0,
                "sync session checkpoint resume transfer claim persists worker-owned claimed rows without executing bytes");
        {
            SyncSqliteDb claim_probe_handle;
            int claim_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            claim_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), claim_probe_handle.db.out(), claim_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(claim_probe_handle.db, "could not reopen checkpoint db for claimed-only resume transfer workorder probe"));
            }
            const std::uint64_t claimed_workorder_rows = sqlite_count_for_session_or_throw(claim_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-charlie';",
                "session-main",
                "resume transfer claimed-only workorder count");
            const std::uint64_t completed_workorder_rows = sqlite_count_for_session_or_throw(claim_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='completed';",
                "session-main",
                "resume transfer completed workorder count after claim only");
            const std::uint64_t lease_timed_workorder_rows = sqlite_count_for_session_or_throw(claim_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND worker_id='worker-charlie' AND claimed_at_epoch=1000 AND lease_expires_at_epoch=1010 AND claim_attempts=1;",
                "session-main",
                "resume transfer claimed-only lease timing count");
            const std::uint64_t claim_reclaim_event_rows = sqlite_count_for_session_or_throw(claim_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_reclaim_events WHERE session_id=?;",
                "session-main",
                "resume transfer claimed-only reclaim event count");
            NormalizedSyncPath claim_receipt_dir_relative;
            claim_receipt_dir_relative.value = pending_materialize_staged_relative.value + ".chunks";
            const fs::path claim_receipt_dir = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
                fake_staging_root,
                claim_receipt_dir_relative,
                "sync session checkpoint resume transfer claim fixture receipt directory"));
            require(claimed_workorder_rows == pending_materialize_entry->chunks.size() &&
                    completed_workorder_rows == 0 &&
                    lease_timed_workorder_rows == pending_materialize_entry->chunks.size() &&
                    claim_reclaim_event_rows == 0 &&
                    !fs::exists(pending_materialize_staged_path) &&
                    !fs::exists(claim_receipt_dir),
                    "sync session checkpoint resume transfer claim leaves claimed rows crash-visible without staged bytes or receipt sidecars");
        }
        {
            const auto& claimed_file = transfer_claim_result.files[0];
            SyncPeerChunkResponseBatchEnvelope claimed_peer_response;
            claimed_peer_response.path = claimed_file.path;
            claimed_peer_response.request_idempotency_key = claimed_file.request_idempotency_key;
            claimed_peer_response.schedule_idempotency_key = claimed_file.schedule_idempotency_key;
            claimed_peer_response.peer_id = claimed_file.peer_id;
            claimed_peer_response.peer_session_id = claimed_file.peer_session_id;
            claimed_peer_response.peer_request_idempotency_key = claimed_file.peer_request_idempotency_key;
            claimed_peer_response.peer_response_batch_idempotency_key = "sync-resume-peer-response-batch:v1:selftest-owned-claim";
            claimed_peer_response.batch_idempotency_key = "sync-resume-chunk-response-batch:v1:selftest-owned-claim";
            claimed_peer_response.remote_entry_digest = sync_manifest_entry_digest(*pending_materialize_entry);
            claimed_peer_response.remote_version_digest = sync_manifest_entry_version_digest(*pending_materialize_entry);
            claimed_peer_response.apply_entry_idempotency_key = pending_materialize_apply->idempotency_key;
            claimed_peer_response.response_count = static_cast<std::uint64_t>(pending_materialize_entry->chunks.size());
            std::vector<std::string> claimed_chunk_bytes;
            claimed_chunk_bytes.reserve(pending_materialize_entry->chunks.size());
            for (const auto& chunk : pending_materialize_entry->chunks) {
                SyncChunkResponseEnvelope response;
                response.path = claimed_file.path;
                response.request_idempotency_key = claimed_file.request_idempotency_key;
                response.response_idempotency_key = "sync-resume-peer-response:v1:selftest-" + u64_string(chunk.offset);
                response.remote_entry_digest = claimed_peer_response.remote_entry_digest;
                response.remote_version_digest = claimed_peer_response.remote_version_digest;
                response.apply_entry_idempotency_key = pending_materialize_apply->idempotency_key;
                response.offset = chunk.offset;
                response.length = chunk.length;
                response.chunk_sha256 = chunk.sha256;
                claimed_peer_response.total_bytes += chunk.length;
                claimed_peer_response.responses.push_back(std::move(response));
                claimed_chunk_bytes.push_back(chunk_bytes_for_body(fake_session_report, chunk));
            }
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions binding_options;
            binding_options.sqlite_path = fake_session_checkpoint_db.string();
            binding_options.session_id = "session-main";
            binding_options.worker_id = transfer_claim_result.worker_id;
            binding_options.worker_lease_id = transfer_claim_result.worker_lease_id;
            binding_options.expected_execution_idempotency_key = claimed_file.execution_idempotency_key;
            binding_options.binding_now_epoch = 1005;
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingResult binding_result;
            SyncValidationResult binding_run = verify_sync_session_checkpoint_resume_peer_response_workorder_claims(binding_options,
                                                                                                                    claimed_peer_response,
                                                                                                                    binding_result);
            require(binding_run.ok &&
                    binding_result.response_envelope_checked &&
                    binding_result.workorder_claims_checked &&
                    binding_result.all_rows_owned_by_worker &&
                    binding_result.all_rows_lease_live &&
                    binding_result.workorder_rows_bound == pending_materialize_entry->chunks.size() &&
                    binding_result.response_rows_considered == pending_materialize_entry->chunks.size() &&
                    binding_result.live_lease_rows == pending_materialize_entry->chunks.size() &&
                    binding_result.bytes_bound == pending_materialize_entry->size_bytes,
                    "sync session checkpoint resume peer response workorder binding accepts only live rows owned by the worker lease");

            SyncChunkReceiptWriteOptions claimed_write_options;
            claimed_write_options.local_root_path = fake_destination_root.string();
            claimed_write_options.staging_root_path = fake_staging_root.string();
            NormalizedSyncPath claim_receipt_dir_relative;
            claim_receipt_dir_relative.value = pending_materialize_staged_relative.value + ".chunks";
            const fs::path claim_receipt_dir = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
                fake_staging_root,
                claim_receipt_dir_relative,
                "sync session checkpoint resume peer response bound acceptance receipt directory"));

            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions wrong_worker_binding = binding_options;
            wrong_worker_binding.worker_id = "worker-echo";
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingResult wrong_worker_binding_result;
            require(!verify_sync_session_checkpoint_resume_peer_response_workorder_claims(wrong_worker_binding,
                                                                                         claimed_peer_response,
                                                                                         wrong_worker_binding_result).ok,
                    "sync session checkpoint resume peer response workorder binding refuses bytes for a different worker before acceptance");
            SyncSessionCheckpointBoundPeerChunkResponseBatchAcceptanceResult wrong_bound_acceptance;
            require(!accept_sync_session_checkpoint_bound_peer_chunk_response_batch_envelope(wrong_worker_binding,
                                                                                            *pending_materialize_entry,
                                                                                            *pending_materialize_apply,
                                                                                            claimed_peer_response,
                                                                                            claimed_chunk_bytes,
                                                                                            claimed_write_options,
                                                                                            wrong_bound_acceptance).ok &&
                    !fs::exists(pending_materialize_staged_path) &&
                    !fs::exists(claim_receipt_dir),
                    "sync session checkpoint bound peer response acceptance refuses wrong-worker bytes without writing staged evidence");

            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions expired_binding = binding_options;
            expired_binding.binding_now_epoch = 1010;
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingResult expired_binding_result;
            require(!verify_sync_session_checkpoint_resume_peer_response_workorder_claims(expired_binding,
                                                                                         claimed_peer_response,
                                                                                         expired_binding_result).ok,
                    "sync session checkpoint resume peer response workorder binding refuses bytes after the worker lease expires");

            SyncSessionCheckpointBoundPeerChunkResponseBatchAcceptanceResult bound_acceptance;
            SyncValidationResult bound_acceptance_run = accept_sync_session_checkpoint_bound_peer_chunk_response_batch_envelope(binding_options,
                                                                                                                                *pending_materialize_entry,
                                                                                                                                *pending_materialize_apply,
                                                                                                                                claimed_peer_response,
                                                                                                                                claimed_chunk_bytes,
                                                                                                                                claimed_write_options,
                                                                                                                                bound_acceptance);
            require(bound_acceptance_run.ok &&
                    bound_acceptance.workorder_claim_binding_checked &&
                    bound_acceptance.peer_batch_acceptance_attempted &&
                    bound_acceptance.bytes_accepted_after_binding &&
                    bound_acceptance.workorder_binding.workorder_rows_bound == pending_materialize_entry->chunks.size() &&
                    bound_acceptance.peer_batch_acceptance.chunks_written == pending_materialize_entry->chunks.size() &&
                    bound_acceptance.peer_batch_acceptance.staged_file_complete &&
                    bound_acceptance.peer_batch_acceptance.content_sha256 == pending_materialize_entry->content_sha256 &&
                    fs::exists(pending_materialize_staged_path) &&
                    fs::exists(claim_receipt_dir),
                    "sync session checkpoint bound peer response acceptance writes staged bytes only after live workorder claim binding");
            {
                SyncSqliteDb bound_acceptance_probe;
                int bound_acceptance_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                bound_acceptance_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), bound_acceptance_probe.db.out(), bound_acceptance_probe_flags, nullptr) != SQLITE_OK) {
                    throw std::runtime_error(sqlite_error_message(bound_acceptance_probe.db, "could not reopen checkpoint db for bound peer response acceptance probe"));
                }
                const std::uint64_t still_claimed_rows = sqlite_count_for_session_or_throw(bound_acceptance_probe.db,
                    "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-charlie';",
                    "session-main",
                    "bound peer response acceptance still-claimed workorder count");
                const std::uint64_t completed_rows = sqlite_count_for_session_or_throw(bound_acceptance_probe.db,
                    "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='completed';",
                    "session-main",
                    "bound peer response acceptance completed workorder count");
                require(still_claimed_rows == pending_materialize_entry->chunks.size() &&
                        completed_rows == 0,
                        "sync session checkpoint bound peer response acceptance writes sidecars without mutating workorder terminal state");
            }
            {
                const fs::path recovery_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-sidecar-recovery-" + std::to_string(selftest_ticks) + ".sqlite");
                fs::remove(recovery_checkpoint_db, apply_cleanup_ec);
                fs::remove(fs::path(recovery_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                fs::remove(fs::path(recovery_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                            recovery_checkpoint_db,
                                            "sync session checkpoint bound peer sidecar recovery selftest");
                SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions recovery_binding = binding_options;
                recovery_binding.sqlite_path = recovery_checkpoint_db.string();
                SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult recovery_result;
                SyncValidationResult recovery_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars(recovery_binding,
                                                                                                             *pending_materialize_entry,
                                                                                                             *pending_materialize_apply,
                                                                                                             claimed_peer_response,
                                                                                                             claimed_write_options,
                                                                                                             recovery_result);
                require(recovery_run.ok &&
                        recovery_result.transport_payload_not_required &&
                        recovery_result.sidecar_evidence_verified &&
                        recovery_result.database_advance_attempted &&
                        recovery_result.database_advance_completed &&
                        recovery_result.recovery_entrypoint_completed &&
                        recovery_result.bytes_verified == pending_materialize_entry->size_bytes &&
                        recovery_result.receipt_rows_reactivated_from_committed_cleaned == pending_materialize_entry->chunks.size() &&
                        recovery_result.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                        recovery_result.content_sha256 == pending_materialize_entry->content_sha256,
                        "sync session checkpoint bound peer sidecar recovery advances accepted sidecars without requiring transport bytes");
                SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult recovery_rerun_result;
                SyncValidationResult recovery_rerun = recover_sync_session_checkpoint_bound_peer_chunk_sidecars(recovery_binding,
                                                                                                               *pending_materialize_entry,
                                                                                                               *pending_materialize_apply,
                                                                                                               claimed_peer_response,
                                                                                                               claimed_write_options,
                                                                                                               recovery_rerun_result);
                require(recovery_rerun.ok &&
                        recovery_rerun_result.recovery_entrypoint_completed &&
                        recovery_rerun_result.receipt_rows_already_present == pending_materialize_entry->chunks.size() &&
                        recovery_rerun_result.workorder_rows_already_completed == pending_materialize_entry->chunks.size() &&
                        recovery_rerun_result.workorder_rows_completed == 0,
                        "sync session checkpoint bound peer sidecar recovery is idempotent after DB advancement replay");
                {
                    SyncSqliteDb recovery_probe;
                    int recovery_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    recovery_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(recovery_checkpoint_db.string().c_str(), recovery_probe.db.out(), recovery_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(recovery_probe.db, "could not reopen checkpoint db for bound peer sidecar recovery probe"));
                    }
                    const std::uint64_t recovery_completed_workorders = sqlite_count_for_session_or_throw(recovery_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='completed' AND worker_id='worker-charlie';",
                        "session-main",
                        "bound peer sidecar recovery completed workorder count");
                    const std::uint64_t recovery_accepted_receipts = sqlite_count_for_session_or_throw(recovery_probe.db,
                        "SELECT COUNT(*) FROM sync_session_chunk_receipts WHERE session_id=? AND path='docs/session-report.txt' AND receipt_state='accepted';",
                        "session-main",
                        "bound peer sidecar recovery accepted receipt count");
                    require(recovery_completed_workorders == pending_materialize_entry->chunks.size() &&
                            recovery_accepted_receipts == pending_materialize_entry->chunks.size(),
                            "sync session checkpoint bound peer sidecar recovery leaves durable DB rows completed and accepted");
                }
            }
            const fs::path advance_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-advance-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(advance_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(advance_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(advance_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                        advance_checkpoint_db,
                                        "sync session checkpoint bound peer acceptance db advance selftest");
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions advance_binding = binding_options;
            advance_binding.sqlite_path = advance_checkpoint_db.string();
            SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult advance_result;
            SyncValidationResult advance_run = advance_sync_session_checkpoint_bound_peer_chunk_acceptance(advance_binding,
                                                                                                           *pending_materialize_entry,
                                                                                                           *pending_materialize_apply,
                                                                                                           claimed_peer_response,
                                                                                                           claimed_write_options,
                                                                                                           advance_result);
            require(advance_run.ok &&
                    advance_result.database_evidence_loaded &&
                    advance_result.sidecar_evidence_verified &&
                    advance_result.transaction_committed &&
                    advance_result.response_rows_considered == pending_materialize_entry->chunks.size() &&
                    advance_result.live_claimed_rows_verified == pending_materialize_entry->chunks.size() &&
                    advance_result.sidecar_receipts_verified == pending_materialize_entry->chunks.size() &&
                    advance_result.staged_chunks_verified == pending_materialize_entry->chunks.size() &&
                    advance_result.bytes_verified == pending_materialize_entry->size_bytes &&
                    advance_result.receipt_rows_reactivated_from_committed_cleaned == pending_materialize_entry->chunks.size() &&
                    advance_result.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                    advance_result.file_result_row_updated &&
                    advance_result.checkpoint_aggregates_updated &&
                    advance_result.staged_file_complete &&
                    advance_result.content_sha256 == pending_materialize_entry->content_sha256,
                    "sync session checkpoint bound peer acceptance db advance converts accepted sidecars into durable receipt rows and completed workorders");
            SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult advance_rerun_result;
            SyncValidationResult advance_rerun = advance_sync_session_checkpoint_bound_peer_chunk_acceptance(advance_binding,
                                                                                                             *pending_materialize_entry,
                                                                                                             *pending_materialize_apply,
                                                                                                             claimed_peer_response,
                                                                                                             claimed_write_options,
                                                                                                             advance_rerun_result);
            require(advance_rerun.ok &&
                    advance_rerun_result.transaction_committed &&
                    advance_rerun_result.receipt_rows_already_present == pending_materialize_entry->chunks.size() &&
                    advance_rerun_result.workorder_rows_already_completed == pending_materialize_entry->chunks.size() &&
                    advance_rerun_result.workorder_rows_completed == 0 &&
                    !advance_rerun_result.file_result_row_updated,
                    "sync session checkpoint bound peer acceptance db advance is idempotent after completed DB progress");
            {
                SyncSqliteDb advance_probe;
                int advance_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                advance_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                if (::anonsync::persistence::open_verified_sqlite_database(advance_checkpoint_db.string().c_str(), advance_probe.db.out(), advance_probe_flags, nullptr) != SQLITE_OK) {
                    throw std::runtime_error(sqlite_error_message(advance_probe.db, "could not reopen checkpoint db for bound peer acceptance db advance probe"));
                }
                const std::uint64_t accepted_receipts = sqlite_count_for_session_or_throw(advance_probe.db,
                    "SELECT COUNT(*) FROM sync_session_chunk_receipts WHERE session_id=? AND path='docs/session-report.txt' AND receipt_state='accepted';",
                    "session-main",
                    "bound peer acceptance db advance accepted receipt count");
                const std::uint64_t completed_workorders = sqlite_count_for_session_or_throw(advance_probe.db,
                    "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='completed' AND worker_id='worker-charlie';",
                    "session-main",
                    "bound peer acceptance db advance completed workorder count");
                const std::uint64_t claimed_workorders_after_advance = sqlite_count_for_session_or_throw(advance_probe.db,
                    "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='claimed';",
                    "session-main",
                    "bound peer acceptance db advance claimed workorder count");
                require(accepted_receipts == pending_materialize_entry->chunks.size() &&
                        completed_workorders == pending_materialize_entry->chunks.size() &&
                        claimed_workorders_after_advance == 0,
                        "sync session checkpoint bound peer acceptance db advance leaves durable rows in accepted/completed state");
            }
            auto verify_db_advance_controlled_rollback = [&](const SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions& rollback_options,
                                                            const std::string& expected_abort_stage,
                                                            bool expect_workorders_completed_before_abort,
                                                            bool expect_file_update_before_abort,
                                                            bool expect_aggregate_update_before_abort) {
                const std::string safe_stage = [&]() {
                    std::string value;
                    value.reserve(expected_abort_stage.size());
                    for (char c : expected_abort_stage) value.push_back(c == '-' ? '_' : c);
                    return value;
                }();
                const fs::path rollback_checkpoint_db = fs::temp_directory_path() /
                    ("anonsync-sync-session-checkpoint-bound-peer-db-advance-rollback-" + safe_stage + "-" + std::to_string(selftest_ticks) + ".sqlite");
                fs::remove(rollback_checkpoint_db, apply_cleanup_ec);
                fs::remove(fs::path(rollback_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                fs::remove(fs::path(rollback_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                            rollback_checkpoint_db,
                                            "sync session checkpoint bound peer controlled db advance rollback selftest");
                std::uint64_t rollback_initial_checkpoint_chunks_written = 0;
                std::uint64_t rollback_initial_file_chunks_written = 0;
                {
                    SyncSqliteDb rollback_initial_probe;
                    int rollback_initial_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    rollback_initial_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(rollback_checkpoint_db.string().c_str(), rollback_initial_probe.db.out(), rollback_initial_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(rollback_initial_probe.db, "could not reopen checkpoint db for bound peer controlled db advance initial rollback probe"));
                    }
                    rollback_initial_checkpoint_chunks_written = sqlite_count_for_session_or_throw(rollback_initial_probe.db,
                        "SELECT COALESCE(SUM(chunks_written),0) FROM sync_session_checkpoints WHERE session_id=?;",
                        "session-main",
                        "bound peer controlled db advance initial rollback checkpoint chunks written sum");
                    rollback_initial_file_chunks_written = sqlite_count_for_session_or_throw(rollback_initial_probe.db,
                        "SELECT COALESCE(SUM(chunks_written),0) FROM sync_session_file_results WHERE session_id=? AND path='docs/session-report.txt';",
                        "session-main",
                        "bound peer controlled db advance initial rollback file chunks written sum");
                }
                SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions rollback_binding = binding_options;
                rollback_binding.sqlite_path = rollback_checkpoint_db.string();
                SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult rollback_result;
                SyncValidationResult rollback_run = advance_sync_session_checkpoint_bound_peer_chunk_acceptance_controlled(rollback_binding,
                                                                                                                            *pending_materialize_entry,
                                                                                                                            *pending_materialize_apply,
                                                                                                                            claimed_peer_response,
                                                                                                                            claimed_write_options,
                                                                                                                            rollback_options,
                                                                                                                            rollback_result);
                require(!rollback_run.ok &&
                        rollback_result.controlled_abort_before_commit &&
                        rollback_result.controlled_abort_stage == expected_abort_stage &&
                        rollback_result.database_evidence_loaded &&
                        rollback_result.sidecar_evidence_verified &&
                        !rollback_result.transaction_committed &&
                        rollback_result.receipt_rows_reactivated_from_committed_cleaned == pending_materialize_entry->chunks.size() &&
                        rollback_result.workorder_rows_completed == (expect_workorders_completed_before_abort ? pending_materialize_entry->chunks.size() : 0) &&
                        rollback_result.file_result_row_updated == expect_file_update_before_abort &&
                        rollback_result.checkpoint_aggregates_updated == expect_aggregate_update_before_abort,
                        "sync session checkpoint bound peer controlled db advance reports the expected pre-commit abort stage");
                SyncSqliteDb rollback_probe;
                int rollback_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                rollback_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                if (::anonsync::persistence::open_verified_sqlite_database(rollback_checkpoint_db.string().c_str(), rollback_probe.db.out(), rollback_probe_flags, nullptr) != SQLITE_OK) {
                    throw std::runtime_error(sqlite_error_message(rollback_probe.db, "could not reopen checkpoint db for bound peer controlled db advance rollback probe"));
                }
                const std::uint64_t rollback_accepted_receipts = sqlite_count_for_session_or_throw(rollback_probe.db,
                    "SELECT COUNT(*) FROM sync_session_chunk_receipts WHERE session_id=? AND path='docs/session-report.txt' AND receipt_state='accepted';",
                    "session-main",
                    "bound peer controlled db advance rollback accepted receipt count");
                const std::uint64_t rollback_committed_cleaned_receipts = sqlite_count_for_session_or_throw(rollback_probe.db,
                    "SELECT COUNT(*) FROM sync_session_chunk_receipts WHERE session_id=? AND path='docs/session-report.txt' AND receipt_state='committed-cleaned';",
                    "session-main",
                    "bound peer controlled db advance rollback committed-cleaned receipt count");
                const std::uint64_t rollback_completed_workorders = sqlite_count_for_session_or_throw(rollback_probe.db,
                    "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='completed';",
                    "session-main",
                    "bound peer controlled db advance rollback completed workorder count");
                const std::uint64_t rollback_claimed_workorders = sqlite_count_for_session_or_throw(rollback_probe.db,
                    "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='claimed' AND worker_id='worker-charlie';",
                    "session-main",
                    "bound peer controlled db advance rollback claimed workorder count");
                const std::uint64_t rollback_checkpoint_chunks_written = sqlite_count_for_session_or_throw(rollback_probe.db,
                    "SELECT COALESCE(SUM(chunks_written),0) FROM sync_session_checkpoints WHERE session_id=?;",
                    "session-main",
                    "bound peer controlled db advance rollback checkpoint chunks written sum");
                const std::uint64_t rollback_file_chunks_written = sqlite_count_for_session_or_throw(rollback_probe.db,
                    "SELECT COALESCE(SUM(chunks_written),0) FROM sync_session_file_results WHERE session_id=? AND path='docs/session-report.txt';",
                    "session-main",
                    "bound peer controlled db advance rollback file chunks written sum");
                require(rollback_accepted_receipts == 0 &&
                        rollback_committed_cleaned_receipts == pending_materialize_entry->chunks.size() &&
                        rollback_completed_workorders == 0 &&
                        rollback_claimed_workorders == pending_materialize_entry->chunks.size() &&
                        rollback_checkpoint_chunks_written == rollback_initial_checkpoint_chunks_written &&
                        rollback_file_chunks_written == rollback_initial_file_chunks_written,
                        "sync session checkpoint bound peer controlled db advance abort rolls back receipt, workorder, file-result, and checkpoint mutations");
            };
            {
                SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions rollback_options;
                rollback_options.abort_after_receipt_row_stage_before_workorder_completion = true;
                verify_db_advance_controlled_rollback(rollback_options,
                                                      "receipt-row-stage-before-workorder-completion",
                                                      false,
                                                      false,
                                                      false);
            }
            {
                SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions rollback_options;
                rollback_options.abort_after_workorder_completion_before_file_result_update = true;
                verify_db_advance_controlled_rollback(rollback_options,
                                                      "workorder-completion-before-file-result-update",
                                                      true,
                                                      false,
                                                      false);
            }
            {
                SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions rollback_options;
                rollback_options.abort_after_file_result_update_before_checkpoint_aggregate = true;
                verify_db_advance_controlled_rollback(rollback_options,
                                                      "file-result-update-before-checkpoint-aggregate",
                                                      true,
                                                      true,
                                                      false);
            }
            {
                SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions rollback_options;
                rollback_options.abort_after_checkpoint_aggregate_before_commit = true;
                verify_db_advance_controlled_rollback(rollback_options,
                                                      "checkpoint-aggregate-before-commit",
                                                      true,
                                                      true,
                                                      true);
            }
            {
                SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions invalid_rollback_options;
                invalid_rollback_options.abort_after_receipt_row_stage_before_workorder_completion = true;
                invalid_rollback_options.abort_after_checkpoint_aggregate_before_commit = true;
                SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult invalid_rollback_result;
                require(!advance_sync_session_checkpoint_bound_peer_chunk_acceptance_controlled(binding_options,
                                                                                                 *pending_materialize_entry,
                                                                                                 *pending_materialize_apply,
                                                                                                 claimed_peer_response,
                                                                                                 claimed_write_options,
                                                                                                 invalid_rollback_options,
                                                                                                 invalid_rollback_result).ok,
                        "sync session checkpoint bound peer controlled db advance refuses ambiguous multiple abort stages");
            }
            const fs::path wrong_advance_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-wrong-advance-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(wrong_advance_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(wrong_advance_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(wrong_advance_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                        wrong_advance_checkpoint_db,
                                        "sync session checkpoint wrong-worker bound peer acceptance db advance selftest");
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions wrong_advance_binding = wrong_worker_binding;
            wrong_advance_binding.sqlite_path = wrong_advance_checkpoint_db.string();
            SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult wrong_advance_result;
            require(!advance_sync_session_checkpoint_bound_peer_chunk_acceptance(wrong_advance_binding,
                                                                                 *pending_materialize_entry,
                                                                                 *pending_materialize_apply,
                                                                                 claimed_peer_response,
                                                                                 claimed_write_options,
                                                                                 wrong_advance_result).ok,
                    "sync session checkpoint bound peer acceptance db advance refuses sidecars for rows owned by a different worker");
            const fs::path expired_advance_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-expired-advance-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(expired_advance_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(expired_advance_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(expired_advance_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                        expired_advance_checkpoint_db,
                                        "sync session checkpoint expired bound peer acceptance db advance selftest");
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions expired_advance_binding = expired_binding;
            expired_advance_binding.sqlite_path = expired_advance_checkpoint_db.string();
            SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult expired_advance_result;
            require(!advance_sync_session_checkpoint_bound_peer_chunk_acceptance(expired_advance_binding,
                                                                                 *pending_materialize_entry,
                                                                                 *pending_materialize_apply,
                                                                                 claimed_peer_response,
                                                                                 claimed_write_options,
                                                                                 expired_advance_result).ok,
                    "sync session checkpoint bound peer acceptance db advance refuses to complete expired live claims");
            const fs::path tampered_advance_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-tampered-advance-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(tampered_advance_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(tampered_advance_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(tampered_advance_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                        tampered_advance_checkpoint_db,
                                        "sync session checkpoint tampered bound peer acceptance db advance selftest");
            std::string tampered_report = fake_session_report;
            if (!tampered_report.empty()) tampered_report[0] = tampered_report[0] == 'x' ? 'y' : 'x';
            write_binary_fixture(pending_materialize_staged_path, tampered_report);
            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions tampered_advance_binding = binding_options;
            tampered_advance_binding.sqlite_path = tampered_advance_checkpoint_db.string();
            SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult tampered_advance_result;
            require(!advance_sync_session_checkpoint_bound_peer_chunk_acceptance(tampered_advance_binding,
                                                                                 *pending_materialize_entry,
                                                                                 *pending_materialize_apply,
                                                                                 claimed_peer_response,
                                                                                 claimed_write_options,
                                                                                 tampered_advance_result).ok,
                    "sync session checkpoint bound peer acceptance db advance refuses tampered staged bytes before mutating DB rows");
            fs::remove(pending_materialize_staged_path, apply_cleanup_ec);
            if (apply_cleanup_ec) throw std::runtime_error("could not remove bound peer response acceptance staged fixture: " + apply_cleanup_ec.message());
            fs::remove_all(claim_receipt_dir, apply_cleanup_ec);
            if (apply_cleanup_ec) throw std::runtime_error("could not remove bound peer response acceptance receipt fixture: " + apply_cleanup_ec.message());

            {
                const fs::path wrong_ingestion_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-wrong-ingest-" + std::to_string(selftest_ticks) + ".sqlite");
                fs::remove(wrong_ingestion_checkpoint_db, apply_cleanup_ec);
                fs::remove(fs::path(wrong_ingestion_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                fs::remove(fs::path(wrong_ingestion_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                            wrong_ingestion_checkpoint_db,
                                            "sync session checkpoint wrong-worker bound peer ingestion facade selftest");
                SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions wrong_ingestion_binding = wrong_worker_binding;
                wrong_ingestion_binding.sqlite_path = wrong_ingestion_checkpoint_db.string();
                SyncSessionCheckpointBoundPeerChunkIngestionResult wrong_ingestion_result;
                require(!ingest_sync_session_checkpoint_bound_peer_chunk_response_batch(wrong_ingestion_binding,
                                                                                        *pending_materialize_entry,
                                                                                        *pending_materialize_apply,
                                                                                        claimed_peer_response,
                                                                                        claimed_chunk_bytes,
                                                                                        claimed_write_options,
                                                                                        wrong_ingestion_result).ok &&
                        wrong_ingestion_result.sidecar_acceptance_attempted &&
                        !wrong_ingestion_result.sidecar_acceptance_completed &&
                        !wrong_ingestion_result.database_advance_attempted &&
                        !fs::exists(pending_materialize_staged_path) &&
                        !fs::exists(claim_receipt_dir),
                        "sync session checkpoint bound peer ingestion facade refuses wrong-worker bytes before sidecar or DB mutation");
            }
            {
                const fs::path controlled_ingestion_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-controlled-crash-" + std::to_string(selftest_ticks) + ".sqlite");
                fs::remove(controlled_ingestion_checkpoint_db, apply_cleanup_ec);
                fs::remove(fs::path(controlled_ingestion_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                fs::remove(fs::path(controlled_ingestion_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                            controlled_ingestion_checkpoint_db,
                                            "sync session checkpoint controlled-crash bound peer ingestion facade selftest");
                SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions controlled_ingestion_binding = binding_options;
                controlled_ingestion_binding.sqlite_path = controlled_ingestion_checkpoint_db.string();
                SyncSessionCheckpointBoundPeerChunkIngestionControlOptions controlled_ingestion_options;
                controlled_ingestion_options.stop_after_sidecar_acceptance_before_db_advance = true;
                SyncSessionCheckpointBoundPeerChunkIngestionResult controlled_ingestion_result;
                require(!ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(controlled_ingestion_binding,
                                                                                                   *pending_materialize_entry,
                                                                                                   *pending_materialize_apply,
                                                                                                   claimed_peer_response,
                                                                                                   claimed_chunk_bytes,
                                                                                                   claimed_write_options,
                                                                                                   controlled_ingestion_options,
                                                                                                   controlled_ingestion_result).ok &&
                        controlled_ingestion_result.sidecar_acceptance_attempted &&
                        controlled_ingestion_result.sidecar_acceptance_completed &&
                        controlled_ingestion_result.controlled_stop_after_sidecar_acceptance &&
                        controlled_ingestion_result.recoverable_sidecar_acceptance_without_db_advance &&
                        !controlled_ingestion_result.database_advance_attempted &&
                        !controlled_ingestion_result.database_advance_completed &&
                        fs::exists(pending_materialize_staged_path) &&
                        fs::exists(claim_receipt_dir),
                        "sync session checkpoint bound peer ingestion controlled crash stop leaves accepted sidecars without DB advancement");
                {
                    SyncSqliteDb controlled_stop_probe;
                    int controlled_stop_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    controlled_stop_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(controlled_ingestion_checkpoint_db.string().c_str(), controlled_stop_probe.db.out(), controlled_stop_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(controlled_stop_probe.db, "could not reopen checkpoint db for bound peer controlled crash stop probe"));
                    }
                    const std::uint64_t controlled_stop_claimed_rows = sqlite_count_for_session_or_throw(controlled_stop_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='claimed' AND worker_id='worker-charlie';",
                        "session-main",
                        "bound peer controlled crash stop claimed workorder count");
                    const std::uint64_t controlled_stop_completed_rows = sqlite_count_for_session_or_throw(controlled_stop_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='completed';",
                        "session-main",
                        "bound peer controlled crash stop completed workorder count");
                    const std::uint64_t controlled_stop_accepted_receipts = sqlite_count_for_session_or_throw(controlled_stop_probe.db,
                        "SELECT COUNT(*) FROM sync_session_chunk_receipts WHERE session_id=? AND path='docs/session-report.txt' AND receipt_state='accepted';",
                        "session-main",
                        "bound peer controlled crash stop accepted receipt count");
                    require(controlled_stop_claimed_rows == pending_materialize_entry->chunks.size() &&
                            controlled_stop_completed_rows == 0 &&
                            controlled_stop_accepted_receipts == 0,
                            "sync session checkpoint bound peer ingestion controlled crash stop does not mutate SQLite rows before recovery");
                }
                {
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions expired_sweep_options;
                    expired_sweep_options.sqlite_path = controlled_ingestion_checkpoint_db.string();
                    expired_sweep_options.session_id = "session-main";
                    expired_sweep_options.worker_id = controlled_ingestion_binding.worker_id;
                    expired_sweep_options.worker_lease_id = controlled_ingestion_binding.worker_lease_id;
                    expired_sweep_options.binding_now_epoch = 1010;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult expired_sweep_result;
                    SyncValidationResult expired_sweep_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(expired_sweep_options,
                                                                                                                                     *pending_materialize_entry,
                                                                                                                                     *pending_materialize_apply,
                                                                                                                                     claimed_write_options,
                                                                                                                                     expired_sweep_result);
                    require(expired_sweep_run.ok &&
                            expired_sweep_result.sweep_query_loaded &&
                            !expired_sweep_result.recovery_attempted &&
                            !expired_sweep_result.sweep_completed &&
                            expired_sweep_result.sweep_incomplete_due_to_expired_lease &&
                            expired_sweep_result.recovery_groups_deferred_expired_lease == 1 &&
                            expired_sweep_result.claimed_rows_deferred_expired_lease == pending_materialize_entry->chunks.size() &&
                            expired_sweep_result.groups.size() == 1 &&
                            expired_sweep_result.groups[0].deferred_by_expired_lease,
                            "sync session checkpoint bound peer sidecar recovery sweep defers expired worker leases without falsely reporting completion");
                }
                {
                    require(pending_materialize_entry->chunks.size() > 1,
                            "sync session checkpoint bound peer bounded sidecar sweep fixture needs at least two chunks");
                    const fs::path bounded_sweep_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-bounded-sweep-" + std::to_string(selftest_ticks) + ".sqlite");
                    fs::remove(bounded_sweep_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(bounded_sweep_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(bounded_sweep_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    sqlite_backup_file_or_throw(controlled_ingestion_checkpoint_db,
                                                bounded_sweep_checkpoint_db,
                                                "sync session checkpoint bounded sidecar recovery sweep selftest");
                    {
                        SyncSqliteDb bounded_split_handle;
                        int bounded_split_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                        bounded_split_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                        if (::anonsync::persistence::open_verified_sqlite_database(bounded_sweep_checkpoint_db.string().c_str(), bounded_split_handle.db.out(), bounded_split_flags, nullptr) != SQLITE_OK) {
                            throw std::runtime_error(sqlite_error_message(bounded_split_handle.db, "could not open bounded sweep checkpoint db for group split fixture"));
                        }
                        sqlite_exec_or_throw(bounded_split_handle.db,
                                             "UPDATE sync_session_resume_transfer_workorders "
                                             "SET execution_idempotency_key=execution_idempotency_key || ':bounded-split' "
                                             "WHERE session_id='session-main' AND path='docs/session-report.txt' "
                                             "AND chunk_offset=(SELECT MAX(chunk_offset) FROM sync_session_resume_transfer_workorders "
                                             "WHERE session_id='session-main' AND path='docs/session-report.txt');",
                                             "sync session checkpoint bounded sidecar recovery sweep could not split a claimed group");
                    }
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions bounded_sweep_options;
                    bounded_sweep_options.sqlite_path = bounded_sweep_checkpoint_db.string();
                    bounded_sweep_options.session_id = "session-main";
                    bounded_sweep_options.worker_id = controlled_ingestion_binding.worker_id;
                    bounded_sweep_options.worker_lease_id = controlled_ingestion_binding.worker_lease_id;
                    bounded_sweep_options.binding_now_epoch = controlled_ingestion_binding.binding_now_epoch;
                    bounded_sweep_options.max_recovery_groups = 1;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult bounded_sweep_result;
                    SyncValidationResult bounded_sweep_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(bounded_sweep_options,
                                                                                                                                     *pending_materialize_entry,
                                                                                                                                     *pending_materialize_apply,
                                                                                                                                     claimed_write_options,
                                                                                                                                     bounded_sweep_result);
                    require(bounded_sweep_run.ok &&
                            bounded_sweep_result.sweep_query_loaded &&
                            bounded_sweep_result.recovery_attempted &&
                            !bounded_sweep_result.sweep_completed &&
                            bounded_sweep_result.sweep_incomplete_due_to_limit &&
                            bounded_sweep_result.recovery_groups_considered == 2 &&
                            bounded_sweep_result.recovery_groups_completed == 1 &&
                            bounded_sweep_result.recovery_groups_deferred_by_limit == 1 &&
                            bounded_sweep_result.recovery_groups_failed == 0 &&
                            bounded_sweep_result.groups.size() == 2 &&
                            bounded_sweep_result.workorder_rows_completed == pending_materialize_entry->chunks.size() - 1,
                            "sync session checkpoint bound peer sidecar recovery sweep reports bounded deferral instead of false completion");
                }
                {
                    const fs::path session_sweep_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-session-sweep-" + std::to_string(selftest_ticks) + ".sqlite");
                    fs::remove(session_sweep_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(session_sweep_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(session_sweep_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    sqlite_backup_file_or_throw(controlled_ingestion_checkpoint_db,
                                                session_sweep_checkpoint_db,
                                                "sync session checkpoint session-wide sidecar recovery sweep selftest");
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions session_sweep_options;
                    session_sweep_options.sqlite_path = session_sweep_checkpoint_db.string();
                    session_sweep_options.session_id = "session-main";
                    session_sweep_options.worker_id = controlled_ingestion_binding.worker_id;
                    session_sweep_options.worker_lease_id = controlled_ingestion_binding.worker_lease_id;
                    session_sweep_options.binding_now_epoch = controlled_ingestion_binding.binding_now_epoch;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult session_sweep_result;
                    SyncValidationResult session_sweep_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_session(session_sweep_options,
                                                                                                                                         std::vector<SyncManifestEntry>{*pending_materialize_entry},
                                                                                                                                         std::vector<SyncLocalApplyPlanEntry>{*pending_materialize_apply},
                                                                                                                                         claimed_write_options,
                                                                                                                                         session_sweep_result);
                    require(session_sweep_run.ok &&
                            session_sweep_result.transport_payload_not_required &&
                            session_sweep_result.session_sweep_attempted &&
                            session_sweep_result.session_sweep_completed &&
                            session_sweep_result.file_inputs_considered == 1 &&
                            session_sweep_result.files_attempted == 1 &&
                            session_sweep_result.files_completed == 1 &&
                            session_sweep_result.recovery_groups_completed == 1 &&
                            session_sweep_result.bytes_verified == pending_materialize_entry->size_bytes &&
                            session_sweep_result.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                            session_sweep_result.files.size() == 1 &&
                            session_sweep_result.files[0].file_sweep_completed,
                            "sync session checkpoint bound peer session sidecar recovery sweep recovers staged sidecars across apply-plan inputs");
                }
                const SyncChunkRange& first_recovery_chunk = pending_materialize_entry->chunks.front();
                const std::string first_recovery_receipt_text = sync_domain_test_access::chunk_receipt_material_for_fixture(*pending_materialize_entry,
                                                                                       *pending_materialize_apply,
                                                                                       first_recovery_chunk);
                const NormalizedSyncPath first_recovery_receipt_relative{
                    sync_domain_test_access::chunk_receipt_relative_path_for_fixture(pending_materialize_entry->path,
                                                                    sync_manifest_entry_digest(*pending_materialize_entry),
                                                                    first_recovery_chunk,
                                                                    "sync session checkpoint sidecar review classifier receipt path")
                };
                const fs::path first_recovery_receipt_path = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
                    fake_staging_root,
                    first_recovery_receipt_relative,
                    "sync session checkpoint sidecar review classifier receipt path"));
                auto restore_first_recovery_sidecar_fixture = [&]() {
                    sync_domain_test_access::write_staged_chunk_bytes_for_fixture(pending_materialize_staged_path,
                                                      first_recovery_chunk,
                                                      claimed_chunk_bytes.front());
                    sync_domain_test_access::write_receipt_file_atomically_for_fixture(first_recovery_receipt_path,
                                                           first_recovery_receipt_text);
                };
                {
                    const fs::path missing_review_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-missing-sidecar-review-" + std::to_string(selftest_ticks) + ".sqlite");
                    fs::remove(missing_review_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(missing_review_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(missing_review_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    sqlite_backup_file_or_throw(controlled_ingestion_checkpoint_db,
                                                missing_review_checkpoint_db,
                                                "sync session checkpoint missing sidecar review classifier selftest");
                    if (!fs::remove(first_recovery_receipt_path, apply_cleanup_ec) || apply_cleanup_ec) {
                        throw std::runtime_error("could not remove receipt sidecar for missing sidecar review classifier fixture: " + apply_cleanup_ec.message());
                    }
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions missing_review_options;
                    missing_review_options.sqlite_path = missing_review_checkpoint_db.string();
                    missing_review_options.session_id = "session-main";
                    missing_review_options.worker_id = controlled_ingestion_binding.worker_id;
                    missing_review_options.worker_lease_id = controlled_ingestion_binding.worker_lease_id;
                    missing_review_options.binding_now_epoch = controlled_ingestion_binding.binding_now_epoch;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult missing_review_result;
                    SyncValidationResult missing_review_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_session(missing_review_options,
                                                                                                                                             std::vector<SyncManifestEntry>{*pending_materialize_entry},
                                                                                                                                             std::vector<SyncLocalApplyPlanEntry>{*pending_materialize_apply},
                                                                                                                                             claimed_write_options,
                                                                                                                                             missing_review_result);
                    require(!missing_review_run.ok &&
                            missing_review_result.session_sweep_attempted &&
                            !missing_review_result.session_sweep_completed &&
                            missing_review_result.sweep_incomplete_due_to_review &&
                            missing_review_result.files_review_required == 1 &&
                            missing_review_result.recovery_groups_failed == 1 &&
                            missing_review_result.recovery_groups_review_required == 1 &&
                            missing_review_result.recovery_groups_review_missing_sidecar == 1 &&
                            missing_review_result.claimed_rows_review_required == pending_materialize_entry->chunks.size() &&
                            missing_review_result.bytes_review_required == pending_materialize_entry->size_bytes &&
                            missing_review_result.review_events_written == 1 &&
                            missing_review_result.review_events_already_present == 0 &&
                            missing_review_result.files.size() == 1 &&
                            missing_review_result.files[0].review_required &&
                            missing_review_result.files[0].review_events_written == 1 &&
                            missing_review_result.files[0].file_sweep.groups.size() == 1 &&
                            missing_review_result.files[0].file_sweep.groups[0].review_required &&
                            missing_review_result.files[0].file_sweep.groups[0].review_due_to_missing_sidecar &&
                            missing_review_result.files[0].file_sweep.groups[0].review_event_persisted &&
                            !missing_review_result.files[0].file_sweep.groups[0].review_event_idempotency_key.empty(),
                            "sync session checkpoint bound peer session sidecar recovery classifies and persists missing sidecars as structured review facts");
                    SyncSidecarReviewEventMetrics missing_review_metrics = sqlite_sidecar_review_event_metrics_for_session_or_throw(
                        missing_review_checkpoint_db,
                        "session-main",
                        "sync session checkpoint missing sidecar review event metrics");
                    require(missing_review_metrics.rows == 1 &&
                            missing_review_metrics.observations == 1 &&
                            missing_review_metrics.missing_sidecar_rows == 1,
                            "sync session checkpoint bound peer missing sidecar review event is durably recorded once");
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult missing_review_second_result;
                    SyncValidationResult missing_review_second_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_session(missing_review_options,
                                                                                                                                                    std::vector<SyncManifestEntry>{*pending_materialize_entry},
                                                                                                                                                    std::vector<SyncLocalApplyPlanEntry>{*pending_materialize_apply},
                                                                                                                                                    claimed_write_options,
                                                                                                                                                    missing_review_second_result);
                    require(!missing_review_second_run.ok &&
                            missing_review_second_result.review_events_written == 0 &&
                            missing_review_second_result.review_events_already_present == 1 &&
                            missing_review_second_result.files.size() == 1 &&
                            missing_review_second_result.files[0].file_sweep.groups.size() == 1 &&
                            missing_review_second_result.files[0].file_sweep.groups[0].review_event_already_present,
                            "sync session checkpoint bound peer missing sidecar review event replay updates the existing durable event");
                    SyncSidecarReviewEventMetrics missing_review_replay_metrics = sqlite_sidecar_review_event_metrics_for_session_or_throw(
                        missing_review_checkpoint_db,
                        "session-main",
                        "sync session checkpoint missing sidecar review event replay metrics");
                    require(missing_review_replay_metrics.rows == 1 &&
                            missing_review_replay_metrics.observations == 2 &&
                            missing_review_replay_metrics.missing_sidecar_rows == 1,
                            "sync session checkpoint bound peer missing sidecar review event replay is idempotent and observable");
                    restore_first_recovery_sidecar_fixture();
                }
                {
                    const fs::path tampered_review_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-tampered-sidecar-review-" + std::to_string(selftest_ticks) + ".sqlite");
                    fs::remove(tampered_review_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(tampered_review_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(tampered_review_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    sqlite_backup_file_or_throw(controlled_ingestion_checkpoint_db,
                                                tampered_review_checkpoint_db,
                                                "sync session checkpoint tampered sidecar review classifier selftest");
                    write_file(first_recovery_receipt_path.string(), "tampered receipt material");
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions tampered_review_options;
                    tampered_review_options.sqlite_path = tampered_review_checkpoint_db.string();
                    tampered_review_options.session_id = "session-main";
                    tampered_review_options.worker_id = controlled_ingestion_binding.worker_id;
                    tampered_review_options.worker_lease_id = controlled_ingestion_binding.worker_lease_id;
                    tampered_review_options.binding_now_epoch = controlled_ingestion_binding.binding_now_epoch;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult tampered_review_result;
                    SyncValidationResult tampered_review_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(tampered_review_options,
                                                                                                                                             *pending_materialize_entry,
                                                                                                                                             *pending_materialize_apply,
                                                                                                                                             claimed_write_options,
                                                                                                                                             tampered_review_result);
                    require(!tampered_review_run.ok &&
                            !tampered_review_result.sweep_completed &&
                            tampered_review_result.sweep_incomplete_due_to_review &&
                            tampered_review_result.recovery_groups_failed == 1 &&
                            tampered_review_result.recovery_groups_review_required == 1 &&
                            tampered_review_result.recovery_groups_review_tampered_sidecar == 1 &&
                            tampered_review_result.review_events_written == 1 &&
                            tampered_review_result.groups.size() == 1 &&
                            tampered_review_result.groups[0].review_required &&
                            tampered_review_result.groups[0].review_due_to_tampered_sidecar &&
                            tampered_review_result.groups[0].review_event_persisted,
                            "sync session checkpoint bound peer sidecar recovery classifies and persists tampered sidecar material as structured review facts");
                    SyncSidecarReviewEventMetrics tampered_review_metrics = sqlite_sidecar_review_event_metrics_for_session_or_throw(
                        tampered_review_checkpoint_db,
                        "session-main",
                        "sync session checkpoint tampered sidecar review event metrics");
                    require(tampered_review_metrics.rows == 1 &&
                            tampered_review_metrics.observations == 1 &&
                            tampered_review_metrics.tampered_sidecar_rows == 1,
                            "sync session checkpoint bound peer tampered sidecar review event is durably recorded");
                    restore_first_recovery_sidecar_fixture();
                }
                {
                    const fs::path staged_bytes_review_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-staged-bytes-review-" + std::to_string(selftest_ticks) + ".sqlite");
                    fs::remove(staged_bytes_review_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(staged_bytes_review_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(staged_bytes_review_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    sqlite_backup_file_or_throw(controlled_ingestion_checkpoint_db,
                                                staged_bytes_review_checkpoint_db,
                                                "sync session checkpoint staged bytes review classifier selftest");
                    std::string corrupt_first_chunk_bytes = claimed_chunk_bytes.front();
                    if (corrupt_first_chunk_bytes.empty()) throw std::runtime_error("sidecar review classifier fixture requires a non-empty first chunk");
                    corrupt_first_chunk_bytes[0] = corrupt_first_chunk_bytes[0] == 'x' ? 'y' : 'x';
                    sync_domain_test_access::write_staged_chunk_bytes_for_fixture(pending_materialize_staged_path,
                                                      first_recovery_chunk,
                                                      corrupt_first_chunk_bytes);
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions staged_bytes_review_options;
                    staged_bytes_review_options.sqlite_path = staged_bytes_review_checkpoint_db.string();
                    staged_bytes_review_options.session_id = "session-main";
                    staged_bytes_review_options.worker_id = controlled_ingestion_binding.worker_id;
                    staged_bytes_review_options.worker_lease_id = controlled_ingestion_binding.worker_lease_id;
                    staged_bytes_review_options.binding_now_epoch = controlled_ingestion_binding.binding_now_epoch;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult staged_bytes_review_result;
                    SyncValidationResult staged_bytes_review_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(staged_bytes_review_options,
                                                                                                                                               *pending_materialize_entry,
                                                                                                                                               *pending_materialize_apply,
                                                                                                                                               claimed_write_options,
                                                                                                                                               staged_bytes_review_result);
                    require(!staged_bytes_review_run.ok &&
                            !staged_bytes_review_result.sweep_completed &&
                            staged_bytes_review_result.sweep_incomplete_due_to_review &&
                            staged_bytes_review_result.recovery_groups_failed == 1 &&
                            staged_bytes_review_result.recovery_groups_review_required == 1 &&
                            staged_bytes_review_result.recovery_groups_review_staged_bytes_mismatch == 1 &&
                            staged_bytes_review_result.review_events_written == 1 &&
                            staged_bytes_review_result.groups.size() == 1 &&
                            staged_bytes_review_result.groups[0].review_required &&
                            staged_bytes_review_result.groups[0].review_due_to_staged_bytes_mismatch &&
                            staged_bytes_review_result.groups[0].review_event_persisted,
                            "sync session checkpoint bound peer sidecar recovery classifies and persists staged byte mismatch as structured review facts");
                    SyncSidecarReviewEventMetrics staged_bytes_review_metrics = sqlite_sidecar_review_event_metrics_for_session_or_throw(
                        staged_bytes_review_checkpoint_db,
                        "session-main",
                        "sync session checkpoint staged bytes review event metrics");
                    require(staged_bytes_review_metrics.rows == 1 &&
                            staged_bytes_review_metrics.observations == 1 &&
                            staged_bytes_review_metrics.staged_bytes_mismatch_rows == 1,
                            "sync session checkpoint bound peer staged bytes review event is durably recorded");
                    restore_first_recovery_sidecar_fixture();
                }
                SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions controlled_stop_sweep_options;
                controlled_stop_sweep_options.sqlite_path = controlled_ingestion_checkpoint_db.string();
                controlled_stop_sweep_options.session_id = "session-main";
                controlled_stop_sweep_options.worker_id = controlled_ingestion_binding.worker_id;
                controlled_stop_sweep_options.worker_lease_id = controlled_ingestion_binding.worker_lease_id;
                controlled_stop_sweep_options.binding_now_epoch = controlled_ingestion_binding.binding_now_epoch;
                SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult controlled_stop_sweep_result;
                SyncValidationResult controlled_stop_sweep_run = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(controlled_stop_sweep_options,
                                                                                                                                     *pending_materialize_entry,
                                                                                                                                     *pending_materialize_apply,
                                                                                                                                     claimed_write_options,
                                                                                                                                     controlled_stop_sweep_result);
                require(controlled_stop_sweep_run.ok &&
                        controlled_stop_sweep_result.sweep_query_loaded &&
                        controlled_stop_sweep_result.transport_payload_not_required &&
                        controlled_stop_sweep_result.recovery_attempted &&
                        controlled_stop_sweep_result.sweep_completed &&
                        controlled_stop_sweep_result.claimed_rows_considered == pending_materialize_entry->chunks.size() &&
                        controlled_stop_sweep_result.recovery_groups_considered == 1 &&
                        controlled_stop_sweep_result.recovery_groups_completed == 1 &&
                        controlled_stop_sweep_result.recovery_groups_failed == 0 &&
                        controlled_stop_sweep_result.bytes_verified == pending_materialize_entry->size_bytes &&
                        controlled_stop_sweep_result.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                        controlled_stop_sweep_result.groups.size() == 1 &&
                        controlled_stop_sweep_result.groups[0].execution_idempotency_key == controlled_ingestion_binding.expected_execution_idempotency_key &&
                        controlled_stop_sweep_result.groups[0].recovery.recovery_entrypoint_completed,
                        "sync session checkpoint bound peer ingestion controlled crash stop is recoverable by startup sidecar sweep without original transport envelope");
                SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult controlled_stop_sweep_rerun_result;
                SyncValidationResult controlled_stop_sweep_rerun = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(controlled_stop_sweep_options,
                                                                                                                                           *pending_materialize_entry,
                                                                                                                                           *pending_materialize_apply,
                                                                                                                                           claimed_write_options,
                                                                                                                                           controlled_stop_sweep_rerun_result);
                require(controlled_stop_sweep_rerun.ok &&
                        controlled_stop_sweep_rerun_result.sweep_query_loaded &&
                        controlled_stop_sweep_rerun_result.sweep_completed &&
                        controlled_stop_sweep_rerun_result.claimed_rows_considered == 0 &&
                        controlled_stop_sweep_rerun_result.recovery_groups_considered == 0 &&
                        !controlled_stop_sweep_rerun_result.recovery_attempted,
                        "sync session checkpoint bound peer sidecar recovery sweep is idle after it completes DB advancement");
                fs::remove(pending_materialize_staged_path, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove controlled crash stop staged fixture: " + apply_cleanup_ec.message());
                fs::remove_all(claim_receipt_dir, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove controlled crash stop receipt fixture: " + apply_cleanup_ec.message());
            }
            {
                const fs::path startup_recovery_daemon_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-startup-sidecar-recovery-" + std::to_string(selftest_ticks) + ".sqlite");
                fs::remove(startup_recovery_daemon_checkpoint_db, apply_cleanup_ec);
                fs::remove(fs::path(startup_recovery_daemon_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                fs::remove(fs::path(startup_recovery_daemon_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                            startup_recovery_daemon_checkpoint_db,
                                            "sync session checkpoint daemon startup sidecar recovery seed selftest");
                SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions startup_ingestion_binding = binding_options;
                startup_ingestion_binding.sqlite_path = startup_recovery_daemon_checkpoint_db.string();
                SyncSessionCheckpointBoundPeerChunkIngestionControlOptions startup_ingestion_control;
                startup_ingestion_control.stop_after_sidecar_acceptance_before_db_advance = true;
                SyncSessionCheckpointBoundPeerChunkIngestionResult startup_ingestion_result;
                require(!ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(startup_ingestion_binding,
                                                                                                   *pending_materialize_entry,
                                                                                                   *pending_materialize_apply,
                                                                                                   claimed_peer_response,
                                                                                                   claimed_chunk_bytes,
                                                                                                   claimed_write_options,
                                                                                                   startup_ingestion_control,
                                                                                                   startup_ingestion_result).ok &&
                        startup_ingestion_result.sidecar_acceptance_completed &&
                        startup_ingestion_result.recoverable_sidecar_acceptance_without_db_advance,
                        "sync session checkpoint daemon startup recovery fixture leaves sidecars before DB advancement");
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions missing_apply_startup_loop_options =
                    make_transfer_workorder_daemon_loop_options(startup_recovery_daemon_checkpoint_db, 1005, "worker-charlie", 7, 10);
                missing_apply_startup_loop_options.max_loop_passes = 1;
                missing_apply_startup_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                missing_apply_startup_loop_options.startup_sidecar_remote_file_entries = {*pending_materialize_entry};
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult missing_apply_startup_loop_result;
                SyncValidationResult missing_apply_startup_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(missing_apply_startup_loop_options,
                                                                                                                                      missing_apply_startup_loop_result);
                require(missing_apply_startup_loop_run.ok &&
                        missing_apply_startup_loop_result.daemon_loop_completed &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery_attempted &&
                        !missing_apply_startup_loop_result.startup_sidecar_recovery_completed &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        missing_apply_startup_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery_incomplete_due_to_missing_apply_input &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery_missing_apply_input_paths == 1 &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery.claimed_workorder_paths_considered == 1 &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery.claimed_workorder_paths_missing_apply_input == 1 &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery.files.size() == 1 &&
                        missing_apply_startup_loop_result.startup_sidecar_recovery.files[0].missing_apply_input &&
                        missing_apply_startup_loop_result.passes_attempted == 0,
                        "sync session checkpoint daemon startup sidecar recovery stops honestly when caller omits claimed apply evidence");
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions missing_remote_startup_loop_options =
                    make_transfer_workorder_daemon_loop_options(startup_recovery_daemon_checkpoint_db, 1005, "worker-charlie", 7, 10);
                missing_remote_startup_loop_options.max_loop_passes = 1;
                missing_remote_startup_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                missing_remote_startup_loop_options.startup_sidecar_apply_entries = {*pending_materialize_apply};
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult missing_remote_startup_loop_result;
                SyncValidationResult missing_remote_startup_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(missing_remote_startup_loop_options,
                                                                                                                                       missing_remote_startup_loop_result);
                require(missing_remote_startup_loop_run.ok &&
                        missing_remote_startup_loop_result.daemon_loop_completed &&
                        missing_remote_startup_loop_result.startup_sidecar_recovery_attempted &&
                        !missing_remote_startup_loop_result.startup_sidecar_recovery_completed &&
                        missing_remote_startup_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        missing_remote_startup_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                        missing_remote_startup_loop_result.startup_sidecar_recovery_incomplete_due_to_missing_remote_file_evidence &&
                        missing_remote_startup_loop_result.startup_sidecar_recovery_missing_remote_file_evidence_files == 1 &&
                        missing_remote_startup_loop_result.startup_sidecar_recovery.files_missing_remote_file_evidence == 1 &&
                        missing_remote_startup_loop_result.startup_sidecar_recovery.files.size() == 1 &&
                        missing_remote_startup_loop_result.startup_sidecar_recovery.files[0].missing_remote_file_evidence &&
                        missing_remote_startup_loop_result.passes_attempted == 0,
                        "sync session checkpoint daemon startup sidecar recovery stops honestly when caller omits claimed remote manifest evidence");
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions ambiguous_apply_startup_loop_options =
                    make_transfer_workorder_daemon_loop_options(startup_recovery_daemon_checkpoint_db, 1005, "worker-charlie", 7, 10);
                ambiguous_apply_startup_loop_options.max_loop_passes = 1;
                ambiguous_apply_startup_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                ambiguous_apply_startup_loop_options.startup_sidecar_remote_file_entries = {*pending_materialize_entry};
                ambiguous_apply_startup_loop_options.startup_sidecar_apply_entries = {*pending_materialize_apply, *pending_materialize_apply};
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult ambiguous_apply_startup_loop_result;
                SyncValidationResult ambiguous_apply_startup_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(ambiguous_apply_startup_loop_options,
                                                                                                                                          ambiguous_apply_startup_loop_result);
                require(ambiguous_apply_startup_loop_run.ok &&
                        ambiguous_apply_startup_loop_result.daemon_loop_completed &&
                        ambiguous_apply_startup_loop_result.startup_sidecar_recovery_attempted &&
                        !ambiguous_apply_startup_loop_result.startup_sidecar_recovery_completed &&
                        ambiguous_apply_startup_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        ambiguous_apply_startup_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                        ambiguous_apply_startup_loop_result.startup_sidecar_recovery_incomplete_due_to_ambiguous_apply_input &&
                        ambiguous_apply_startup_loop_result.startup_sidecar_recovery_ambiguous_apply_input_files == 1 &&
                        ambiguous_apply_startup_loop_result.startup_sidecar_recovery.files_ambiguous_apply_input == 1 &&
                        ambiguous_apply_startup_loop_result.startup_sidecar_recovery.files.size() == 1 &&
                        ambiguous_apply_startup_loop_result.startup_sidecar_recovery.files[0].ambiguous_apply_input &&
                        ambiguous_apply_startup_loop_result.passes_attempted == 0,
                        "sync session checkpoint daemon startup sidecar recovery stops honestly when caller supplies ambiguous claimed apply evidence");
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions ambiguous_remote_startup_loop_options =
                    make_transfer_workorder_daemon_loop_options(startup_recovery_daemon_checkpoint_db, 1005, "worker-charlie", 7, 10);
                ambiguous_remote_startup_loop_options.max_loop_passes = 1;
                ambiguous_remote_startup_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                ambiguous_remote_startup_loop_options.startup_sidecar_remote_file_entries = {*pending_materialize_entry, *pending_materialize_entry};
                ambiguous_remote_startup_loop_options.startup_sidecar_apply_entries = {*pending_materialize_apply};
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult ambiguous_remote_startup_loop_result;
                SyncValidationResult ambiguous_remote_startup_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(ambiguous_remote_startup_loop_options,
                                                                                                                                           ambiguous_remote_startup_loop_result);
                require(ambiguous_remote_startup_loop_run.ok &&
                        ambiguous_remote_startup_loop_result.daemon_loop_completed &&
                        ambiguous_remote_startup_loop_result.startup_sidecar_recovery_attempted &&
                        !ambiguous_remote_startup_loop_result.startup_sidecar_recovery_completed &&
                        ambiguous_remote_startup_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        ambiguous_remote_startup_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                        ambiguous_remote_startup_loop_result.startup_sidecar_recovery_incomplete_due_to_ambiguous_remote_file_evidence &&
                        ambiguous_remote_startup_loop_result.startup_sidecar_recovery_ambiguous_remote_file_evidence_files == 1 &&
                        ambiguous_remote_startup_loop_result.startup_sidecar_recovery.files_ambiguous_remote_file_evidence == 1 &&
                        ambiguous_remote_startup_loop_result.startup_sidecar_recovery.files.size() == 1 &&
                        ambiguous_remote_startup_loop_result.startup_sidecar_recovery.files[0].ambiguous_remote_file_evidence &&
                        ambiguous_remote_startup_loop_result.passes_attempted == 0,
                        "sync session checkpoint daemon startup sidecar recovery stops honestly when caller supplies ambiguous claimed remote manifest evidence");
                {
                    const fs::path startup_hydrated_daemon_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-startup-sidecar-hydrated-" + std::to_string(selftest_ticks) + ".sqlite");
                    fs::remove(startup_hydrated_daemon_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(startup_hydrated_daemon_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(startup_hydrated_daemon_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                                startup_hydrated_daemon_checkpoint_db,
                                                "sync session checkpoint daemon startup hydrated sidecar recovery seed selftest");
                    SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions hydrated_ingestion_binding = binding_options;
                    hydrated_ingestion_binding.sqlite_path = startup_hydrated_daemon_checkpoint_db.string();
                    SyncSessionCheckpointBoundPeerChunkIngestionControlOptions hydrated_ingestion_control;
                    hydrated_ingestion_control.stop_after_sidecar_acceptance_before_db_advance = true;
                    SyncSessionCheckpointBoundPeerChunkIngestionResult hydrated_ingestion_result;
                    require(!ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(hydrated_ingestion_binding,
                                                                                                       *pending_materialize_entry,
                                                                                                       *pending_materialize_apply,
                                                                                                       claimed_peer_response,
                                                                                                       claimed_chunk_bytes,
                                                                                                       claimed_write_options,
                                                                                                       hydrated_ingestion_control,
                                                                                                       hydrated_ingestion_result).ok &&
                            hydrated_ingestion_result.sidecar_acceptance_completed,
                            "sync session checkpoint daemon hydrated startup recovery fixture leaves accepted sidecars before DB advancement");
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions hydrated_evidence_options;
                    hydrated_evidence_options.sqlite_path = startup_hydrated_daemon_checkpoint_db.string();
                    hydrated_evidence_options.session_id = "session-main";
                    hydrated_evidence_options.worker_id = "worker-charlie";
                    hydrated_evidence_options.worker_lease_id = binding_options.worker_lease_id;
                    hydrated_evidence_options.binding_now_epoch = 1005;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult hydrated_evidence_result;
                    SyncValidationResult hydrated_evidence_run = load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(hydrated_evidence_options,
                                                                                                                                                    hydrated_evidence_result);
                    require(hydrated_evidence_run.ok &&
                            hydrated_evidence_result.checkpoint_evidence_loaded &&
                            hydrated_evidence_result.checkpoint_schema_version == "rev0720-sync-session-checkpoint-v4" &&
                            hydrated_evidence_result.checkpoint_schema_supported &&
                            hydrated_evidence_result.checkpoint_schema_has_manifest_chunks &&
                            hydrated_evidence_result.checkpoint_schema_has_manifest_lineage &&
                            hydrated_evidence_result.archived_checkpoint_migration_backfill_checked &&
                            hydrated_evidence_result.archived_checkpoint_exact_startup_hydration_supported &&
                            !hydrated_evidence_result.archived_checkpoint_migration_backfill_required &&
                            !hydrated_evidence_result.archived_checkpoint_migration_backfill_blocked_missing_lineage &&
                            hydrated_evidence_result.main_read_snapshot_established &&
                            hydrated_evidence_result.database_owner_generation != 0 &&
                            !hydrated_evidence_result.sqlite_lock_contention_observed &&
                            hydrated_evidence_result.sqlite_lock_wait_invocations == 0 &&
                            hydrated_evidence_result.sqlite_lock_wait_authorized_sleep_milliseconds == 0 &&
                            hydrated_evidence_result.sqlite_lock_wait_observed_sleep_milliseconds == 0 &&
                            hydrated_evidence_result.claimed_workorder_paths_considered == 1 &&
                            hydrated_evidence_result.claimed_workorder_path_bytes ==
                                pending_materialize_entry->path.value.size() &&
                            hydrated_evidence_result.evidence_metadata_bytes != 0 &&
                            hydrated_evidence_result.apply_entries_loaded == 1 &&
                            hydrated_evidence_result.remote_file_entries_loaded == 1 &&
                            hydrated_evidence_result.manifest_chunks_loaded == pending_materialize_entry->chunks.size() &&
                            hydrated_evidence_result.manifest_lineage_rows_loaded == pending_materialize_entry->lineage.size() &&
                            hydrated_evidence_result.remote_file_entries_missing_lineage_rows == 0 &&
                            hydrated_evidence_result.remote_file_entries.size() == 1 &&
                            hydrated_evidence_result.apply_entries.size() == 1 &&
                            hydrated_evidence_result.remote_file_entries[0].path.value == pending_materialize_entry->path.value &&
                            sync_manifest_entry_digest(hydrated_evidence_result.remote_file_entries[0]) == sync_manifest_entry_digest(*pending_materialize_entry) &&
                            hydrated_evidence_result.apply_entries[0].idempotency_key == pending_materialize_apply->idempotency_key,
                            "sync session checkpoint sidecar recovery hydrates remote/apply evidence from SQLite checkpoint lineage rows");
                    {
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions
                            fail_fast_lock_evidence_options = hydrated_evidence_options;
                        fail_fast_lock_evidence_options.checkpoint_evidence_limits
                            .max_sqlite_lock_wait_milliseconds = 0U;
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult
                            fail_fast_lock_evidence_result;
                        const SyncValidationResult fail_fast_lock_evidence_run =
                            load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
                                fail_fast_lock_evidence_options,
                                fail_fast_lock_evidence_result);
                        require(fail_fast_lock_evidence_run.ok &&
                                fail_fast_lock_evidence_result.checkpoint_evidence_loaded &&
                                !fail_fast_lock_evidence_result.sqlite_lock_contention_observed &&
                                fail_fast_lock_evidence_result.sqlite_lock_wait_invocations == 0 &&
                                fail_fast_lock_evidence_result.sqlite_lock_wait_authorized_sleep_milliseconds == 0 &&
                                fail_fast_lock_evidence_result.sqlite_lock_wait_observed_sleep_milliseconds == 0,
                                "checkpoint evidence admits a zero lock-wait policy and succeeds when uncontended");
                    }
                    {
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions
                            execution_limited_evidence_options = hydrated_evidence_options;
                        execution_limited_evidence_options.checkpoint_evidence_limits
                            .max_sqlite_progress_callbacks = 1U;
                        execution_limited_evidence_options.checkpoint_evidence_limits
                            .sqlite_progress_opcode_interval = 1U;
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult
                            execution_limited_evidence_result;
                        const SyncValidationResult execution_limited_evidence_run =
                            load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
                                execution_limited_evidence_options,
                                execution_limited_evidence_result);
                        require(!execution_limited_evidence_run.ok &&
                                !execution_limited_evidence_result.checkpoint_evidence_loaded &&
                                !execution_limited_evidence_result.main_read_snapshot_established &&
                                execution_limited_evidence_result.database_owner_generation == 0 &&
                                execution_limited_evidence_result.claimed_workorder_paths_considered == 0 &&
                                execution_limited_evidence_result.claimed_workorder_path_bytes == 0 &&
                                execution_limited_evidence_result.evidence_metadata_bytes == 0 &&
                                execution_limited_evidence_result.apply_entries_loaded == 0 &&
                                execution_limited_evidence_result.remote_file_entries_loaded == 0 &&
                                execution_limited_evidence_result.apply_entries.empty() &&
                                execution_limited_evidence_result.remote_file_entries.empty() &&
                                execution_limited_evidence_run.reason.find(
                                    "sqlite_verification_budget[progress_callback_limit]") !=
                                    std::string::npos,
                                "checkpoint evidence SQLite VM-step exhaustion keeps caller-visible evidence at its initialized baseline");
                    }
                    {
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions
                            widened_execution_evidence_options = hydrated_evidence_options;
                        widened_execution_evidence_options.checkpoint_evidence_limits
                            .max_sqlite_progress_callbacks = 1000001U;
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult
                            widened_execution_evidence_result;
                        const SyncValidationResult widened_execution_evidence_run =
                            load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
                                widened_execution_evidence_options,
                                widened_execution_evidence_result);
                        require(!widened_execution_evidence_run.ok &&
                                !widened_execution_evidence_result.checkpoint_evidence_loaded &&
                                widened_execution_evidence_run.reason.find(
                                    "cannot widen reviewed ceilings") !=
                                    std::string::npos,
                                "checkpoint evidence callers may tighten but cannot widen reviewed SQLite execution ceilings");
                    }
                    {
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions
                            widened_lock_wait_evidence_options = hydrated_evidence_options;
                        widened_lock_wait_evidence_options.checkpoint_evidence_limits
                            .max_sqlite_lock_wait_milliseconds = 60001U;
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult
                            widened_lock_wait_evidence_result;
                        const SyncValidationResult widened_lock_wait_evidence_run =
                            load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
                                widened_lock_wait_evidence_options,
                                widened_lock_wait_evidence_result);
                        require(!widened_lock_wait_evidence_run.ok &&
                                !widened_lock_wait_evidence_result.checkpoint_evidence_loaded &&
                                widened_lock_wait_evidence_run.reason.find(
                                    "lock-wait limit cannot widen the reviewed ceiling") !=
                                    std::string::npos,
                                "checkpoint evidence callers may tighten but cannot widen the reviewed SQLite lock-wait ceiling");
                    }
                    {
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions
                            path_limited_evidence_options = hydrated_evidence_options;
                        path_limited_evidence_options.checkpoint_evidence_limits
                            .max_claimed_path_bytes =
                            pending_materialize_entry->path.value.size() - 1U;
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult
                            path_limited_evidence_result;
                        const SyncValidationResult path_limited_evidence_run =
                            load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
                                path_limited_evidence_options,
                                path_limited_evidence_result);
                        require(!path_limited_evidence_run.ok &&
                                !path_limited_evidence_result.checkpoint_evidence_loaded &&
                                path_limited_evidence_run.reason.find(
                                    "claimed-path bytes exceed") != std::string::npos,
                                "checkpoint evidence hydration rejects claimed-path bytes before publication");
                    }
                    {
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions
                            chunk_limited_evidence_options = hydrated_evidence_options;
                        chunk_limited_evidence_options.checkpoint_evidence_limits
                            .max_manifest_chunks =
                            pending_materialize_entry->chunks.size() - 1U;
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult
                            chunk_limited_evidence_result;
                        const SyncValidationResult chunk_limited_evidence_run =
                            load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
                                chunk_limited_evidence_options,
                                chunk_limited_evidence_result);
                        require(!chunk_limited_evidence_run.ok &&
                                !chunk_limited_evidence_result.checkpoint_evidence_loaded &&
                                chunk_limited_evidence_run.reason.find(
                                    "manifest chunk count exceeds resource limit") !=
                                    std::string::npos,
                                "checkpoint evidence hydration rejects aggregate manifest cardinality before nested rows");
                    }
                    {
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions
                            metadata_limited_evidence_options = hydrated_evidence_options;
                        metadata_limited_evidence_options.checkpoint_evidence_limits
                            .max_metadata_bytes = 1U;
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult
                            metadata_limited_evidence_result;
                        const SyncValidationResult metadata_limited_evidence_run =
                            load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
                                metadata_limited_evidence_options,
                                metadata_limited_evidence_result);
                        require(!metadata_limited_evidence_run.ok &&
                                !metadata_limited_evidence_result.checkpoint_evidence_loaded &&
                                !metadata_limited_evidence_result.main_read_snapshot_established &&
                                metadata_limited_evidence_result.database_owner_generation == 0 &&
                                !metadata_limited_evidence_result.sqlite_lock_contention_observed &&
                                metadata_limited_evidence_result.sqlite_lock_wait_invocations == 0 &&
                                metadata_limited_evidence_result.sqlite_lock_wait_authorized_sleep_milliseconds == 0 &&
                                metadata_limited_evidence_result.sqlite_lock_wait_observed_sleep_milliseconds == 0 &&
                                metadata_limited_evidence_result.claimed_workorder_paths_considered == 0 &&
                                metadata_limited_evidence_result.claimed_workorder_path_bytes == 0 &&
                                metadata_limited_evidence_result.evidence_metadata_bytes == 0 &&
                                metadata_limited_evidence_result.apply_entries_loaded == 0 &&
                                metadata_limited_evidence_result.remote_file_entries_loaded == 0 &&
                                metadata_limited_evidence_result.apply_entries.empty() &&
                                metadata_limited_evidence_result.remote_file_entries.empty() &&
                                metadata_limited_evidence_result.checkpoint_schema_version.empty() &&
                                metadata_limited_evidence_result.sqlite_path ==
                                    metadata_limited_evidence_options.sqlite_path &&
                                metadata_limited_evidence_run.reason.find(
                                    "manifest metadata bytes exceed resource limit") !=
                                    std::string::npos,
                                "checkpoint evidence hydration aggregate scalar metadata budget failure keeps caller-visible evidence at its initialized baseline");
                    }
                    {
                        const fs::path startup_archived_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-startup-sidecar-archived-v3-" + std::to_string(selftest_ticks) + ".sqlite");
                        fs::remove(startup_archived_checkpoint_db, apply_cleanup_ec);
                        fs::remove(fs::path(startup_archived_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                        fs::remove(fs::path(startup_archived_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                        sqlite_backup_file_or_throw(startup_hydrated_daemon_checkpoint_db,
                                                    startup_archived_checkpoint_db,
                                                    "sync session checkpoint daemon archived v3 hydration seed selftest");
                        {
                            SyncSqliteDb archived_mutation_db;
                            int archived_mutation_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                            archived_mutation_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                            if (::anonsync::persistence::open_verified_sqlite_database(startup_archived_checkpoint_db.string().c_str(), archived_mutation_db.db.out(), archived_mutation_flags, nullptr) != SQLITE_OK) {
                                throw std::runtime_error(sqlite_error_message(archived_mutation_db.db, "could not open archived checkpoint db for lineage removal"));
                            }
                            sqlite_exec_or_throw(archived_mutation_db.db,
                                                 "DROP TABLE sync_session_manifest_lineage;"
                                                 "UPDATE sync_session_schema_meta SET value='rev0688-sync-session-checkpoint-v3' WHERE key='schema_version';",
                                                 "sync session checkpoint archived v3 fixture could not remove lineage rows");
                        }
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions archived_evidence_options = hydrated_evidence_options;
                        archived_evidence_options.sqlite_path = startup_archived_checkpoint_db.string();
                        SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult archived_evidence_result;
                        SyncValidationResult archived_evidence_run = load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(archived_evidence_options,
                                                                                                                                                        archived_evidence_result);
                        require(archived_evidence_run.ok &&
                                archived_evidence_result.checkpoint_evidence_loaded &&
                                archived_evidence_result.checkpoint_schema_version == "rev0688-sync-session-checkpoint-v3" &&
                                archived_evidence_result.checkpoint_schema_supported &&
                                archived_evidence_result.checkpoint_schema_has_manifest_chunks &&
                                !archived_evidence_result.checkpoint_schema_has_manifest_lineage &&
                                archived_evidence_result.archived_checkpoint_migration_backfill_checked &&
                                !archived_evidence_result.archived_checkpoint_exact_startup_hydration_supported &&
                                archived_evidence_result.archived_checkpoint_migration_backfill_required &&
                                archived_evidence_result.archived_checkpoint_migration_backfill_blocked_missing_lineage &&
                                archived_evidence_result.claimed_workorder_paths_considered == 1 &&
                                archived_evidence_result.apply_entries_loaded == 1 &&
                                archived_evidence_result.remote_file_entries_loaded == 0 &&
                                archived_evidence_result.manifest_chunks_loaded == pending_materialize_entry->chunks.size() &&
                                archived_evidence_result.manifest_lineage_rows_loaded == 0 &&
                                archived_evidence_result.remote_file_entries_missing_lineage_rows == 1 &&
                                archived_evidence_result.archived_checkpoint_claimed_paths_blocked_by_missing_lineage == 1 &&
                                archived_evidence_result.remote_file_entries.empty() &&
                                archived_evidence_result.apply_entries.size() == 1,
                                "archived v3 checkpoint hydration refuses exact sidecar backfill without manifest lineage rows");

                        SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions archived_startup_loop_options =
                            make_transfer_workorder_daemon_loop_options(startup_archived_checkpoint_db, 1005, "worker-charlie", 7, 10);
                        archived_startup_loop_options.max_loop_passes = 1;
                        archived_startup_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                        SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult archived_startup_loop_result;
                        SyncValidationResult archived_startup_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(archived_startup_loop_options,
                                                                                                                                          archived_startup_loop_result);
                        require(archived_startup_loop_run.ok &&
                                archived_startup_loop_result.daemon_loop_completed &&
                                archived_startup_loop_result.startup_sidecar_recovery_attempted &&
                                archived_startup_loop_result.startup_sidecar_recovery_checkpoint_evidence_hydrated &&
                                archived_startup_loop_result.startup_sidecar_recovery_checkpoint_schema_version == "rev0688-sync-session-checkpoint-v3" &&
                                archived_startup_loop_result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked &&
                                archived_startup_loop_result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_required &&
                                archived_startup_loop_result.startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage &&
                                archived_startup_loop_result.startup_sidecar_recovery_checkpoint_remote_file_entries_loaded == 0 &&
                                archived_startup_loop_result.startup_sidecar_recovery_checkpoint_remote_file_entries_missing_lineage_rows == 1 &&
                                archived_startup_loop_result.startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage == 1 &&
                                !archived_startup_loop_result.startup_sidecar_recovery_completed &&
                                archived_startup_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                                archived_startup_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                                archived_startup_loop_result.startup_sidecar_recovery_incomplete_due_to_missing_remote_file_evidence &&
                                archived_startup_loop_result.startup_sidecar_recovery_missing_remote_file_evidence_files == 1 &&
                                archived_startup_loop_result.passes_attempted == 0,
                                "daemon startup treats archived v3 checkpoint as safe-stop migration work instead of guessing missing lineage");
                    }
                    SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions hydrated_startup_loop_options =
                        make_transfer_workorder_daemon_loop_options(startup_hydrated_daemon_checkpoint_db, 1005, "worker-charlie", 7, 10);
                    hydrated_startup_loop_options.max_loop_passes = 1;
                    hydrated_startup_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                    SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult hydrated_startup_loop_result;
                    SyncValidationResult hydrated_startup_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(hydrated_startup_loop_options,
                                                                                                                                      hydrated_startup_loop_result);
                    require(hydrated_startup_loop_run.ok &&
                            hydrated_startup_loop_result.daemon_loop_completed &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_attempted &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_checkpoint_evidence_hydrated &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_checkpoint_apply_entries_loaded == 1 &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_checkpoint_remote_file_entries_loaded == 1 &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_checkpoint_manifest_chunks_loaded == pending_materialize_entry->chunks.size() &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_checkpoint_manifest_lineage_rows_loaded == pending_materialize_entry->lineage.size() &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_completed &&
                            !hydrated_startup_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                            hydrated_startup_loop_result.startup_sidecar_recovery_groups_completed == 1 &&
                            hydrated_startup_loop_result.startup_sidecar_recovery.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                            hydrated_startup_loop_result.passes_attempted == 1 &&
                            hydrated_startup_loop_result.passes_completed == 1,
                            "sync session checkpoint daemon loop hydrates startup sidecar recovery evidence from SQLite before scheduling");
                }
                {
                    const fs::path startup_hydrated_mismatch_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-startup-sidecar-hydrated-mismatch-" + std::to_string(selftest_ticks) + ".sqlite");
                    fs::remove(startup_hydrated_mismatch_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(startup_hydrated_mismatch_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(startup_hydrated_mismatch_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                                startup_hydrated_mismatch_checkpoint_db,
                                                "sync session checkpoint daemon startup hydrated mismatch seed selftest");
                    SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions mismatch_ingestion_binding = binding_options;
                    mismatch_ingestion_binding.sqlite_path = startup_hydrated_mismatch_checkpoint_db.string();
                    SyncSessionCheckpointBoundPeerChunkIngestionControlOptions mismatch_ingestion_control;
                    mismatch_ingestion_control.stop_after_sidecar_acceptance_before_db_advance = true;
                    SyncSessionCheckpointBoundPeerChunkIngestionResult mismatch_ingestion_result;
                    require(!ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(mismatch_ingestion_binding,
                                                                                                      *pending_materialize_entry,
                                                                                                      *pending_materialize_apply,
                                                                                                      claimed_peer_response,
                                                                                                      claimed_chunk_bytes,
                                                                                                      claimed_write_options,
                                                                                                      mismatch_ingestion_control,
                                                                                                      mismatch_ingestion_result).ok &&
                            mismatch_ingestion_result.sidecar_acceptance_completed,
                            "sync session checkpoint daemon hydrated mismatch fixture leaves accepted sidecars before DB advancement");
                    {
                        SyncSqliteDb mismatch_mutation_db;
                        int mismatch_mutation_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                        mismatch_mutation_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                        if (::anonsync::persistence::open_verified_sqlite_database(startup_hydrated_mismatch_checkpoint_db.string().c_str(), mismatch_mutation_db.db.out(), mismatch_mutation_flags, nullptr) != SQLITE_OK) {
                            throw std::runtime_error(sqlite_error_message(mismatch_mutation_db.db, "could not open hydrated mismatch checkpoint db for apply evidence mutation"));
                        }
                        sqlite_exec_or_throw(mismatch_mutation_db.db,
                                             "UPDATE sync_session_apply_intents SET remote_content_sha256='" + std::string(64, '0') + "' "
                                             "WHERE session_id='session-main' AND path='docs/session-report.txt';",
                                             "sync session checkpoint hydrated startup recovery mismatch fixture could not mutate apply evidence");
                    }
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions mismatch_evidence_options;
                    mismatch_evidence_options.sqlite_path = startup_hydrated_mismatch_checkpoint_db.string();
                    mismatch_evidence_options.session_id = "session-main";
                    mismatch_evidence_options.worker_id = "worker-charlie";
                    mismatch_evidence_options.worker_lease_id = binding_options.worker_lease_id;
                    mismatch_evidence_options.binding_now_epoch = 1005;
                    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult mismatch_evidence_result;
                    SyncValidationResult mismatch_evidence_run = load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(mismatch_evidence_options,
                                                                                                                                                    mismatch_evidence_result);
                    require(mismatch_evidence_run.ok &&
                            mismatch_evidence_result.checkpoint_evidence_loaded &&
                            mismatch_evidence_result.checkpoint_evidence_mismatch_detected &&
                            mismatch_evidence_result.remote_apply_evidence_mismatch_paths == 1 &&
                            mismatch_evidence_result.apply_entries_loaded == 1 &&
                            mismatch_evidence_result.remote_file_entries_loaded == 1,
                            "sync session checkpoint sidecar recovery checkpoint evidence hydration flags remote/apply drift before DB advancement");
                    SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions hydrated_mismatch_loop_options =
                        make_transfer_workorder_daemon_loop_options(startup_hydrated_mismatch_checkpoint_db, 1005, "worker-charlie", 7, 10);
                    hydrated_mismatch_loop_options.max_loop_passes = 1;
                    hydrated_mismatch_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                    SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult hydrated_mismatch_loop_result;
                    SyncValidationResult hydrated_mismatch_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(hydrated_mismatch_loop_options,
                                                                                                                                      hydrated_mismatch_loop_result);
                    require(hydrated_mismatch_loop_run.ok &&
                            hydrated_mismatch_loop_result.daemon_loop_completed &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery_attempted &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery_checkpoint_evidence_hydrated &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery_checkpoint_remote_apply_evidence_mismatch_paths == 1 &&
                            !hydrated_mismatch_loop_result.startup_sidecar_recovery_completed &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                            hydrated_mismatch_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery_incomplete_due_to_remote_apply_evidence_mismatch &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery_remote_apply_evidence_mismatch_files == 1 &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery.files_remote_apply_evidence_mismatch == 1 &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery.files.size() == 1 &&
                            hydrated_mismatch_loop_result.startup_sidecar_recovery.files[0].remote_apply_evidence_mismatch &&
                            hydrated_mismatch_loop_result.passes_attempted == 0,
                            "sync session checkpoint daemon startup sidecar recovery stops typed when hydrated checkpoint apply/remote evidence drift apart");
                }
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions startup_loop_options =
                    make_transfer_workorder_daemon_loop_options(startup_recovery_daemon_checkpoint_db, 1005, "worker-charlie", 7, 10);
                startup_loop_options.max_loop_passes = 1;
                startup_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                startup_loop_options.startup_sidecar_remote_file_entries = {*pending_materialize_entry};
                startup_loop_options.startup_sidecar_apply_entries = {*pending_materialize_apply};
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult startup_loop_result;
                SyncValidationResult startup_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(startup_loop_options,
                                                                                                                          startup_loop_result);
                require(startup_loop_run.ok &&
                        startup_loop_result.daemon_loop_completed &&
                        startup_loop_result.startup_sidecar_recovery_attempted &&
                        startup_loop_result.startup_sidecar_recovery_completed &&
                        !startup_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        !startup_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                        startup_loop_result.startup_sidecar_recovery_groups_completed == 1 &&
                        startup_loop_result.startup_sidecar_recovery.recovery_groups_completed == 1 &&
                        startup_loop_result.startup_sidecar_recovery.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                        startup_loop_result.passes_attempted == 1 &&
                        startup_loop_result.passes_completed == 1 &&
                        startup_loop_result.stopped_after_idle_pass,
                        "sync session checkpoint daemon loop drains clean accepted sidecars before normal scheduling");
                {
                    SyncSqliteDb startup_probe;
                    int startup_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    startup_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(startup_recovery_daemon_checkpoint_db.string().c_str(), startup_probe.db.out(), startup_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(startup_probe.db, "could not reopen checkpoint db for daemon startup sidecar recovery probe"));
                    }
                    const std::uint64_t startup_completed_workorders = sqlite_count_for_session_or_throw(startup_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='completed' AND worker_id='worker-charlie';",
                        "session-main",
                        "daemon startup sidecar recovery completed workorder count");
                    const std::uint64_t startup_accepted_receipts = sqlite_count_for_session_or_throw(startup_probe.db,
                        "SELECT COUNT(*) FROM sync_session_chunk_receipts WHERE session_id=? AND path='docs/session-report.txt' AND receipt_state='accepted';",
                        "session-main",
                        "daemon startup sidecar recovery accepted receipt count");
                    require(startup_completed_workorders == pending_materialize_entry->chunks.size() &&
                            startup_accepted_receipts == pending_materialize_entry->chunks.size(),
                            "sync session checkpoint daemon startup sidecar recovery advances accepted sidecars into durable rows");
                }
                fs::remove(pending_materialize_staged_path, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove daemon startup sidecar recovery staged fixture: " + apply_cleanup_ec.message());
                fs::remove_all(claim_receipt_dir, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove daemon startup sidecar recovery receipt fixture: " + apply_cleanup_ec.message());
            }
            {
                const fs::path startup_review_daemon_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-daemon-startup-sidecar-review-stop-" + std::to_string(selftest_ticks) + ".sqlite");
                fs::remove(startup_review_daemon_checkpoint_db, apply_cleanup_ec);
                fs::remove(fs::path(startup_review_daemon_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                fs::remove(fs::path(startup_review_daemon_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                            startup_review_daemon_checkpoint_db,
                                            "sync session checkpoint daemon startup sidecar review stop seed selftest");
                SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions review_stop_ingestion_binding = binding_options;
                review_stop_ingestion_binding.sqlite_path = startup_review_daemon_checkpoint_db.string();
                SyncSessionCheckpointBoundPeerChunkIngestionControlOptions review_stop_ingestion_control;
                review_stop_ingestion_control.stop_after_sidecar_acceptance_before_db_advance = true;
                SyncSessionCheckpointBoundPeerChunkIngestionResult review_stop_ingestion_result;
                require(!ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(review_stop_ingestion_binding,
                                                                                                   *pending_materialize_entry,
                                                                                                   *pending_materialize_apply,
                                                                                                   claimed_peer_response,
                                                                                                   claimed_chunk_bytes,
                                                                                                   claimed_write_options,
                                                                                                   review_stop_ingestion_control,
                                                                                                   review_stop_ingestion_result).ok &&
                        review_stop_ingestion_result.sidecar_acceptance_completed,
                        "sync session checkpoint daemon startup review stop fixture leaves accepted sidecars before DB advancement");
                fs::remove_all(claim_receipt_dir, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove daemon startup review stop receipt fixture: " + apply_cleanup_ec.message());
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions review_stop_loop_options =
                    make_transfer_workorder_daemon_loop_options(startup_review_daemon_checkpoint_db, 1005, "worker-charlie", 7, 10);
                review_stop_loop_options.max_loop_passes = 1;
                review_stop_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                review_stop_loop_options.startup_sidecar_remote_file_entries = {*pending_materialize_entry};
                review_stop_loop_options.startup_sidecar_apply_entries = {*pending_materialize_apply};
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult review_stop_loop_result;
                SyncValidationResult review_stop_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(review_stop_loop_options,
                                                                                                                             review_stop_loop_result);
                require(review_stop_loop_run.ok &&
                        review_stop_loop_result.daemon_loop_completed &&
                        review_stop_loop_result.startup_sidecar_recovery_attempted &&
                        !review_stop_loop_result.startup_sidecar_recovery_completed &&
                        review_stop_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        review_stop_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                        review_stop_loop_result.startup_sidecar_recovery_incomplete_due_to_review &&
                        review_stop_loop_result.startup_sidecar_recovery_groups_review_required == 1 &&
                        review_stop_loop_result.startup_sidecar_review_events_written == 1 &&
                        review_stop_loop_result.passes_attempted == 0 &&
                        review_stop_loop_result.passes_completed == 0,
                        "sync session checkpoint daemon loop stops before scheduling when startup sidecar recovery records review-required evidence");
                {
                    SyncSqliteDb review_stop_probe;
                    int review_stop_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    review_stop_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(startup_review_daemon_checkpoint_db.string().c_str(), review_stop_probe.db.out(), review_stop_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(review_stop_probe.db, "could not reopen checkpoint db for daemon startup sidecar review stop probe"));
                    }
                    const std::uint64_t review_event_rows = sqlite_count_for_session_or_throw(review_stop_probe.db,
                        "SELECT COUNT(*) FROM sync_session_bound_peer_sidecar_review_events WHERE session_id=? AND review_category='missing-sidecar';",
                        "session-main",
                        "daemon startup sidecar recovery review event count");
                    const std::uint64_t review_completed_workorders = sqlite_count_for_session_or_throw(review_stop_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='completed';",
                        "session-main",
                        "daemon startup sidecar review stop completed workorder count");
                    require(review_event_rows == 1 &&
                            review_completed_workorders == 0,
                            "sync session checkpoint daemon startup sidecar review stop records review event without completing dirty workorders");
                }
                SyncSessionCheckpointBoundPeerSidecarReviewEventReportOptions review_report_options;
                review_report_options.sqlite_path = startup_review_daemon_checkpoint_db.string();
                review_report_options.session_id = "session-main";
                review_report_options.path = pending_materialize_path;
                review_report_options.review_category = "missing-sidecar";
                SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult review_report_result;
                SyncValidationResult review_report_run = list_sync_session_checkpoint_bound_peer_sidecar_review_events(review_report_options,
                                                                                                                        review_report_result);
                require(review_report_run.ok &&
                        review_report_result.review_event_schema_loaded &&
                        review_report_result.report_completed &&
                        review_report_result.events_returned == 1 &&
                        review_report_result.total_observations == 1 &&
                        review_report_result.missing_sidecar_events == 1 &&
                        review_report_result.tampered_sidecar_events == 0 &&
                        review_report_result.staged_bytes_mismatch_events == 0 &&
                        review_report_result.events.size() == 1 &&
                        review_report_result.events[0].path.value == "docs/session-report.txt" &&
                        review_report_result.events[0].review_category == "missing-sidecar" &&
                        review_report_result.events[0].observations == 1 &&
                        review_report_result.events[0].review_event_idempotency_key.rfind("sync-sidecar-review:v1:", 0) == 0,
                        "sync session checkpoint sidecar review report exposes dirty daemon startup event");
                SyncSessionCheckpointOperatorStatusOptions review_stop_status_options;
                review_stop_status_options.sqlite_path = startup_review_daemon_checkpoint_db.string();
                review_stop_status_options.session_id = "session-main";
                review_stop_status_options.scheduler_now_epoch = 1005;
                SyncSessionCheckpointOperatorStatusResult review_stop_status;
                SyncValidationResult review_stop_status_run = load_sync_session_checkpoint_operator_status(review_stop_status_options,
                                                                                                           review_stop_status);
                require(review_stop_status_run.ok &&
                        review_stop_status.status_loaded &&
                        review_stop_status.query_only_enabled &&
                        review_stop_status.sidecar_review_events == 1 &&
                        review_stop_status.pending_sidecar_review_events == 1 &&
                        review_stop_status.missing_sidecar_review_events == 1 &&
                        review_stop_status.sidecar_review_repair_reset_events == 0 &&
                        review_stop_status.daemon_lease_events >= 1 &&
                        review_stop_status.operator_attention_required &&
                        !review_stop_status.safe_to_schedule &&
                        review_stop_status.suggested_next_action == "review-sidecar-events",
                        "sync session checkpoint operator status surfaces pending sidecar review as the next safe action");
                SyncSessionCheckpointBoundPeerSidecarReviewEventReportOptions invalid_review_report_options = review_report_options;
                invalid_review_report_options.review_category = "unknown-sidecar-review-category";
                SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult invalid_review_report_result;
                require(!list_sync_session_checkpoint_bound_peer_sidecar_review_events(invalid_review_report_options,
                                                                                       invalid_review_report_result).ok,
                        "sync session checkpoint sidecar review report rejects unknown categories");
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult review_stop_rerun_loop_result;
                SyncValidationResult review_stop_rerun_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(review_stop_loop_options,
                                                                                                                                   review_stop_rerun_loop_result);
                SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult review_report_after_rerun;
                SyncValidationResult review_report_after_rerun_run = list_sync_session_checkpoint_bound_peer_sidecar_review_events(review_report_options,
                                                                                                                                  review_report_after_rerun);
                require(review_stop_rerun_loop_run.ok &&
                        review_stop_rerun_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        review_stop_rerun_loop_result.startup_sidecar_review_events_written == 0 &&
                        review_stop_rerun_loop_result.startup_sidecar_review_events_already_present == 1 &&
                        review_report_after_rerun_run.ok &&
                        review_report_after_rerun.events_returned == 1 &&
                        review_report_after_rerun.total_observations == 2 &&
                        review_report_after_rerun.events[0].observations == 2,
                        "sync session checkpoint sidecar review report preserves idempotent review-event observations across repeated startup gates");
                {
                    const fs::path workflow_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-" + std::to_string(selftest_ticks) + ".sqlite");
                    const fs::path workflow_config_path = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-config-" + std::to_string(selftest_ticks) + ".json");
                    const fs::path workflow_report_path = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-report-" + std::to_string(selftest_ticks) + ".json");
                    const fs::path workflow_heartbeat_path = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-heartbeat-" + std::to_string(selftest_ticks) + ".json");
                    const fs::path workflow_source_root = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-source-" + std::to_string(selftest_ticks));
                    const fs::path workflow_destination_root = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-destination-" + std::to_string(selftest_ticks));
                    const fs::path workflow_staging_root = fs::temp_directory_path() / ("anonsync-sync-operator-recovery-workflow-stage-" + std::to_string(selftest_ticks));
                    fs::remove(workflow_checkpoint_db, apply_cleanup_ec);
                    fs::remove(fs::path(workflow_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(workflow_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    fs::remove(workflow_config_path, apply_cleanup_ec);
                    fs::remove(workflow_report_path, apply_cleanup_ec);
                    fs::remove(workflow_heartbeat_path, apply_cleanup_ec);
                    fs::remove_all(workflow_source_root, apply_cleanup_ec);
                    fs::remove_all(workflow_destination_root, apply_cleanup_ec);
                    fs::remove_all(workflow_staging_root, apply_cleanup_ec);
                    fs::copy(fake_source_root, workflow_source_root, fs::copy_options::recursive);
                    fs::copy(fake_destination_root, workflow_destination_root, fs::copy_options::recursive);
                    fs::copy(fake_staging_root, workflow_staging_root, fs::copy_options::recursive);
                    sqlite_backup_file_or_throw(startup_review_daemon_checkpoint_db,
                                                workflow_checkpoint_db,
                                                "sync operator recovery workflow seed selftest");
                    std::ostringstream workflow_config;
                    workflow_config << "{\n"
                        << "  \"format\": \"anonsync-sync-operator-recovery-workflow-v1\",\n"
                        << "  \"checkpoint_path\": \"" << json_escape(workflow_checkpoint_db.string()) << "\",\n"
                        << "  \"session_id\": \"session-main\",\n"
                        << "  \"operator_now_epoch\": 1016,\n"
                        << "  \"daemon_heartbeat_path\": \"" << json_escape(workflow_heartbeat_path.string()) << "\",\n"
                        << "  \"repair\": {\n"
                        << "    \"enabled\": true,\n"
                        << "    \"staging_root_path\": \"" << json_escape(fake_staging_root.string()) << "\",\n"
                        << "    \"path\": \"" << json_escape(pending_materialize_entry->path.value) << "\",\n"
                        << "    \"review_event_idempotency_key\": \"" << json_escape(review_report_after_rerun.events[0].review_event_idempotency_key) << "\",\n"
                        << "    \"operator_id\": \"operator-workflow-alpha\",\n"
                        << "    \"decision_reason\": \"operator-workflow-repaired-and-reset-review\",\n"
                        << "    \"repair_at_epoch\": 1016,\n"
                        << "    \"repair_worker_id\": \"worker-workflow-repair\",\n"
                        << "    \"repair_worker_lease_epoch\": 8,\n"
                        << "    \"repair_worker_lease_seconds\": 1,\n"
                        << "    \"workorder_retry_backoff_seconds\": 0\n"
                        << "  },\n"
                        << "  \"daemon\": {\n"
                        << "    \"enabled\": true,\n"
                        << "    \"source_root_path\": \"" << json_escape(fake_source_root.string()) << "\",\n"
                        << "    \"destination_root_path\": \"" << json_escape(fake_destination_root.string()) << "\",\n"
                        << "    \"staging_root_path\": \"" << json_escape(fake_staging_root.string()) << "\",\n"
                        << "    \"expected_folder_id\": \"folder-alpha\",\n"
                        << "    \"expected_source_device_id\": \"device-bravo\",\n"
                        << "    \"expected_destination_device_id\": \"device-alpha\",\n"
                        << "    \"expected_peer_id\": \"peer-bravo\",\n"
                        << "    \"peer_session_id\": \"session-main-resume\",\n"
                        << "    \"worker_id\": \"worker-workflow-daemon\",\n"
                        << "    \"daemon_id\": \"worker-workflow-daemon-main\",\n"
                        << "    \"initial_worker_lease_epoch\": 9,\n"
                        << "    \"daemon_now_epoch\": 1020,\n"
                        << "    \"worker_lease_seconds\": 10,\n"
                        << "    \"loop_tick_seconds\": 1,\n"
                        << "    \"max_loop_passes\": 3,\n"
                        << "    \"max_scheduler_actions_per_pass\": 0,\n"
                        << "    \"workorder_retry_backoff_seconds\": 0,\n"
                        << "    \"recover_bound_peer_sidecars_before_scheduling\": true,\n"
                        << "    \"require_daemon_owner_lock\": true,\n"
                        << "    \"heartbeat_path\": \"" << json_escape(workflow_heartbeat_path.string()) << "\",\n"
                        << "    \"heartbeat_stale_after_seconds\": 9\n"
                        << "  }\n"
                        << "}\n";
                    write_file(workflow_config_path.string(), workflow_config.str());
                    int workflow_rc = run_sync_checkpoint_operator_recovery_workflow_command(workflow_config_path.string(),
                                                                                            workflow_report_path.string());
                    Json workflow_report = load_json(workflow_report_path.string());
                    require(workflow_rc == 0 &&
                            workflow_report.at("format").str() == "anonsync-sync-operator-recovery-workflow-report-v1" &&
                            workflow_report.at("ok").boolean(false) &&
                            workflow_report.at("workflow").at("repair_attempted").boolean(false) &&
                            workflow_report.at("workflow").at("daemon_attempted").boolean(false) &&
                            workflow_report.at("repair_owner_lock").at("acquire_attempted").boolean(false) &&
                            workflow_report.at("repair_owner_lock").at("acquired").boolean(false) &&
                            workflow_report.at("repair_owner_lock").at("release_attempted").boolean(false) &&
                            workflow_report.at("repair_owner_lock").at("released").boolean(false) &&
                            workflow_report.at("repair_owner_lock").at("daemon_id").str() == "sync-operator-repair" &&
                            workflow_report.at("repair_owner_lock").at("worker_id").str() == "worker-workflow-repair" &&
                            workflow_report.at("repair_owner_lock").at("owner_lock_epoch").integer(-1) > 0 &&
                            workflow_report.at("repair_owner_lock").at("owner_lock_id").str().rfind("sync-resume-daemon-owner-lock:v1:", 0) == 0 &&
                            workflow_report.at("repair_owner_lock").at("acquire_reason").str().empty() &&
                            workflow_report.at("repair_owner_lock").at("release_reason").str().empty() &&
                            workflow_report.at("initial_status_report").at("status").at("suggested_next_action").str() == "review-sidecar-events" &&
                            workflow_report.at("repair_reset_report").at("repair_reset").at("workorder_rows_reset").integer(-1) == static_cast<long long>(pending_materialize_entry->chunks.size()) &&
                            workflow_report.at("after_repair_status_report").at("status").at("pending_sidecar_review_events").integer(-1) == 0 &&
                            workflow_report.at("pre_daemon_status_report").at("status").at("suggested_next_action").str() == "run-daemon-reclaim-retry" &&
                            workflow_report.at("daemon_run_report").at("daemon_loop").at("daemon_loop_completed").boolean(false) &&
                            workflow_report.at("daemon_run_report").at("daemon_loop").at("startup_sidecar_recovery_completed").boolean(false) &&
                            workflow_report.at("daemon_run_report").at("daemon_loop").at("workorder_rows_reclaimed").integer(-1) == static_cast<long long>(pending_materialize_entry->chunks.size()) &&
                            workflow_report.at("daemon_run_report").at("daemon_loop").at("workorder_rows_completed").integer(-1) == static_cast<long long>(pending_materialize_entry->chunks.size()) &&
                            workflow_report.at("final_status_report").at("status").at("claimed_workorder_rows").integer(-1) == 0 &&
                            workflow_report.at("final_status_report").at("status").at("completed_workorder_rows").integer(-1) == static_cast<long long>(pending_materialize_entry->chunks.size()) &&
                            workflow_report.at("final_status_report").at("status").at("suggested_next_action").str() == "idle-clean" &&
                            read_binary_fixture(fake_destination_root / "docs/session-report.txt") == fake_session_report,
                            "sync operator recovery workflow drives repair reset through owner-fenced daemon terminal convergence with root consistency");
                    {
                        std::ostringstream mismatched_workflow_config;
                        mismatched_workflow_config << workflow_config.str();
                        std::string mismatched_text = mismatched_workflow_config.str();
                        const std::string needle_root = "\"staging_root_path\": \"" + json_escape(fake_staging_root.string()) + "\"";
                        const std::string mismatch_root = "\"staging_root_path\": \"" + json_escape(workflow_staging_root.string()) + "\"";
                        const std::size_t root_pos = mismatched_text.find(needle_root);
                        if (root_pos == std::string::npos) throw std::runtime_error("workflow root consistency selftest could not find repair staging root");
                        mismatched_text.replace(root_pos, needle_root.size(), mismatch_root);
                        write_file(workflow_config_path.string(), mismatched_text);
                        int mismatched_workflow_rc = run_sync_checkpoint_operator_recovery_workflow_command(workflow_config_path.string(),
                                                                                                             workflow_report_path.string());
                        require(mismatched_workflow_rc == 1,
                                "sync operator recovery workflow refuses mismatched repair and daemon staging roots before mutating checkpoint state");
                        write_file(workflow_config_path.string(), workflow_config.str());
                    }
                    fs::remove_all(fake_destination_root, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not restore fake destination root after full operator workflow: " + apply_cleanup_ec.message());
                    fs::copy(workflow_destination_root, fake_destination_root, fs::copy_options::recursive, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not copy fake destination root backup after full operator workflow: " + apply_cleanup_ec.message());
                    fs::remove_all(fake_staging_root, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not restore fake staging root after full operator workflow: " + apply_cleanup_ec.message());
                    fs::copy(workflow_staging_root, fake_staging_root, fs::copy_options::recursive, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not copy fake staging root backup after full operator workflow: " + apply_cleanup_ec.message());
                    {
                        const fs::path symlink_config_target = fs::temp_directory_path() / ("anonsync-sync-operator-workflow-symlink-target-" + std::to_string(selftest_ticks) + ".json");
                        const fs::path symlink_config_path = fs::temp_directory_path() / ("anonsync-sync-operator-workflow-symlink-config-" + std::to_string(selftest_ticks) + ".json");
                        const fs::path symlink_config_report_path = fs::temp_directory_path() / ("anonsync-sync-operator-workflow-symlink-report-" + std::to_string(selftest_ticks) + ".json");
                        fs::remove(symlink_config_path, apply_cleanup_ec);
                        fs::remove(symlink_config_target, apply_cleanup_ec);
                        fs::remove(symlink_config_report_path, apply_cleanup_ec);
                        write_file(symlink_config_target.string(), workflow_config.str());
                        std::error_code symlink_config_ec;
                        fs::create_symlink(symlink_config_target, symlink_config_path, symlink_config_ec);
                        if (!symlink_config_ec) {
                            int symlink_config_rc = run_sync_checkpoint_operator_recovery_workflow_command(symlink_config_path.string(),
                                                                                                            symlink_config_report_path.string());
                            require(symlink_config_rc == 1 &&
                                    !fs::exists(symlink_config_report_path),
                                    "sync operator recovery workflow refuses symlink config paths before parsing operator JSON");
                            fs::remove(symlink_config_path, apply_cleanup_ec);
                            if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow symlink config: " + apply_cleanup_ec.message());
                        }
                        fs::remove(symlink_config_report_path, apply_cleanup_ec);
                        if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow symlink report: " + apply_cleanup_ec.message());
                        fs::remove(symlink_config_target, apply_cleanup_ec);
                        if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow symlink target: " + apply_cleanup_ec.message());
                    }
                    fs::remove(workflow_config_path, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow config: " + apply_cleanup_ec.message());
                    fs::remove(workflow_report_path, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow report: " + apply_cleanup_ec.message());
                    fs::remove(workflow_heartbeat_path, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow heartbeat: " + apply_cleanup_ec.message());
                    fs::remove(workflow_checkpoint_db, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow db: " + apply_cleanup_ec.message());
                    fs::remove(fs::path(workflow_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                    fs::remove(fs::path(workflow_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                    fs::remove_all(workflow_source_root, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow source root: " + apply_cleanup_ec.message());
                    fs::remove_all(workflow_destination_root, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow destination root: " + apply_cleanup_ec.message());
                    fs::remove_all(workflow_staging_root, apply_cleanup_ec);
                    if (apply_cleanup_ec) throw std::runtime_error("could not remove operator recovery workflow staging root: " + apply_cleanup_ec.message());
                }
                SyncInternalCheckpointMutationOwnerLease sidecar_operator_owner_lease;
                SyncValidationResult sidecar_operator_owner_acquire =
                    sync_internal_acquire_checkpoint_mutation_owner_lease(
                        startup_review_daemon_checkpoint_db.string(),
                        "session-main",
                        "daemon-sidecar-operator",
                        "worker-sidecar-operator",
                        1015,
                        10,
                        sidecar_operator_owner_lease);
                require(sidecar_operator_owner_acquire.ok &&
                            sidecar_operator_owner_lease.acquired &&
                            sidecar_operator_owner_lease.capability.owner_lock_epoch != 0,
                        "sync session checkpoint sidecar operator fixture acquires an exact successor owner generation before mutation");
                SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineOptions sidecar_review_quarantine_options;
                sidecar_review_quarantine_options.sqlite_path = startup_review_daemon_checkpoint_db.string();
                sidecar_review_quarantine_options.session_id = "session-main";
                sidecar_review_quarantine_options.daemon_owner_capability =
                    sidecar_operator_owner_lease.capability;
                sidecar_review_quarantine_options.path = pending_materialize_path;
                sidecar_review_quarantine_options.review_event_idempotency_key = review_report_after_rerun.events[0].review_event_idempotency_key;
                sidecar_review_quarantine_options.decision_operator_id = "operator-sidecar-review-alpha";
                sidecar_review_quarantine_options.decision_reason = "operator-quarantined-missing-sidecar-review";
                sidecar_review_quarantine_options.quarantine_at_epoch = 1015;
                SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineResult sidecar_review_quarantine_result;
                SyncValidationResult sidecar_review_quarantine_run = quarantine_sync_session_checkpoint_bound_peer_sidecar_review_event(sidecar_review_quarantine_options,
                                                                                                                                       sidecar_review_quarantine_result);
                require(sidecar_review_quarantine_run.ok &&
                        sidecar_review_quarantine_result.review_event_schema_loaded &&
                        sidecar_review_quarantine_result.resolution_schema_loaded &&
                        sidecar_review_quarantine_result.review_event_found &&
                        sidecar_review_quarantine_result.transaction_committed &&
                        sidecar_review_quarantine_result.quarantine_event_written &&
                        !sidecar_review_quarantine_result.quarantine_event_already_present &&
                        sidecar_review_quarantine_result.review_category == "missing-sidecar" &&
                        sidecar_review_quarantine_result.workorder_rows_matched == pending_materialize_entry->chunks.size() &&
                        sidecar_review_quarantine_result.workorder_rows_quarantined == pending_materialize_entry->chunks.size() &&
                        sidecar_review_quarantine_result.workorder_rows_already_quarantined == 0,
                        "sync session checkpoint sidecar review quarantine terminalizes matching dirty claimed workorders with one operator audit row");
                {
                    SyncSqliteDb sidecar_review_quarantine_probe;
                    int sidecar_review_quarantine_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    sidecar_review_quarantine_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(startup_review_daemon_checkpoint_db.string().c_str(), sidecar_review_quarantine_probe.db.out(), sidecar_review_quarantine_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(sidecar_review_quarantine_probe.db, "could not reopen checkpoint db for sidecar review quarantine probe"));
                    }
                    const std::uint64_t sidecar_review_quarantined_rows = sqlite_count_for_session_or_throw(sidecar_review_quarantine_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='quarantined';",
                        "session-main",
                        "sidecar review quarantine workorder count");
                    const std::uint64_t sidecar_review_claimed_rows_after_quarantine = sqlite_count_for_session_or_throw(sidecar_review_quarantine_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='claimed';",
                        "session-main",
                        "sidecar review quarantine claimed workorder count");
                    const std::uint64_t sidecar_review_resolution_rows = sqlite_count_for_session_or_throw(sidecar_review_quarantine_probe.db,
                        "SELECT COUNT(*) FROM sync_session_bound_peer_sidecar_review_event_resolutions WHERE session_id=? AND resolution_state='quarantined' AND resolved_by_operator_id='operator-sidecar-review-alpha';",
                        "session-main",
                        "sidecar review quarantine resolution count");
                    require(sidecar_review_quarantined_rows == pending_materialize_entry->chunks.size() &&
                            sidecar_review_claimed_rows_after_quarantine == 0 &&
                            sidecar_review_resolution_rows == 1,
                            "sync session checkpoint sidecar review quarantine persists terminal rows and an operator resolution record");
                }
                SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult review_report_after_quarantine;
                SyncValidationResult review_report_after_quarantine_run = list_sync_session_checkpoint_bound_peer_sidecar_review_events(review_report_options,
                                                                                                                                        review_report_after_quarantine);
                require(review_report_after_quarantine_run.ok &&
                        review_report_after_quarantine.review_event_resolution_schema_loaded &&
                        review_report_after_quarantine.events_returned == 1 &&
                        review_report_after_quarantine.quarantined_events == 1 &&
                        review_report_after_quarantine.unresolved_events == 0 &&
                        review_report_after_quarantine.events[0].resolution_state == "quarantined" &&
                        review_report_after_quarantine.events[0].resolution_reason == "operator-quarantined-missing-sidecar-review" &&
                        review_report_after_quarantine.events[0].resolved_by_operator_id == "operator-sidecar-review-alpha" &&
                        review_report_after_quarantine.events[0].resolved_at_epoch == 1015 &&
                        review_report_after_quarantine.events[0].resolved_workorder_rows_quarantined == pending_materialize_entry->chunks.size(),
                        "sync session checkpoint sidecar review report surfaces operator quarantine resolution state");
                SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineResult sidecar_review_quarantine_replay_result;
                SyncValidationResult sidecar_review_quarantine_replay_run = quarantine_sync_session_checkpoint_bound_peer_sidecar_review_event(sidecar_review_quarantine_options,
                                                                                                                                              sidecar_review_quarantine_replay_result);
                require(sidecar_review_quarantine_replay_run.ok &&
                        sidecar_review_quarantine_replay_result.transaction_committed &&
                        !sidecar_review_quarantine_replay_result.quarantine_event_written &&
                        sidecar_review_quarantine_replay_result.quarantine_event_already_present &&
                        sidecar_review_quarantine_replay_result.workorder_rows_quarantined == 0 &&
                        sidecar_review_quarantine_replay_result.workorder_rows_already_quarantined == pending_materialize_entry->chunks.size(),
                        "sync session checkpoint sidecar review quarantine is idempotent after operator resolution is already present");
                SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions sidecar_review_repair_options;
                sidecar_review_repair_options.sqlite_path = startup_review_daemon_checkpoint_db.string();
                sidecar_review_repair_options.session_id = "session-main";
                sidecar_review_repair_options.daemon_owner_capability =
                    sidecar_operator_owner_lease.capability;
                sidecar_review_repair_options.staging_root_path = claimed_write_options.staging_root_path;
                sidecar_review_repair_options.path = pending_materialize_path;
                sidecar_review_repair_options.review_event_idempotency_key = sidecar_review_quarantine_options.review_event_idempotency_key;
                sidecar_review_repair_options.decision_operator_id = "operator-sidecar-repair-alpha";
                sidecar_review_repair_options.decision_reason = "operator-repaired-missing-sidecar-review-and-reset-for-retry";
                sidecar_review_repair_options.repair_at_epoch = 1016;
                sidecar_review_repair_options.repair_worker_id = "worker-repair";
                sidecar_review_repair_options.repair_worker_lease_epoch = 8;
                sidecar_review_repair_options.repair_worker_lease_seconds = 1;
                sidecar_review_repair_options.workorder_retry_backoff_seconds = 0;
                SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult sidecar_review_repair_result;
                SyncValidationResult sidecar_review_repair_run = repair_reset_sync_session_checkpoint_bound_peer_sidecar_review_event(sidecar_review_repair_options,
                                                                                                                                       sidecar_review_repair_result);
                require(sidecar_review_repair_run.ok &&
                        sidecar_review_repair_result.review_event_schema_loaded &&
                        sidecar_review_repair_result.repair_reset_schema_loaded &&
                        sidecar_review_repair_result.review_event_found &&
                        sidecar_review_repair_result.transaction_committed &&
                        sidecar_review_repair_result.repair_reset_event_written &&
                        !sidecar_review_repair_result.repair_reset_event_already_present &&
                        sidecar_review_repair_result.review_category == "missing-sidecar" &&
                        sidecar_review_repair_result.workorder_rows_matched == pending_materialize_entry->chunks.size() &&
                        sidecar_review_repair_result.workorder_rows_reset == pending_materialize_entry->chunks.size() &&
                        sidecar_review_repair_result.quarantined_rows_reset == pending_materialize_entry->chunks.size() &&
                        sidecar_review_repair_result.claimed_rows_reset == 0 &&
                        sidecar_review_repair_result.receipt_paths_considered == pending_materialize_entry->chunks.size() &&
                        sidecar_review_repair_result.receipts_already_missing == pending_materialize_entry->chunks.size() &&
                        sidecar_review_repair_result.staged_file_checked &&
                        sidecar_review_repair_result.staged_file_left_in_place,
                        "sync session checkpoint sidecar review repair reset invalidates dirty sidecar evidence and reopens quarantined chunks narrowly");
                SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult sidecar_review_repair_replay_result;
                SyncValidationResult sidecar_review_repair_replay_run = repair_reset_sync_session_checkpoint_bound_peer_sidecar_review_event(sidecar_review_repair_options,
                                                                                                                                              sidecar_review_repair_replay_result);
                require(sidecar_review_repair_replay_run.ok &&
                        sidecar_review_repair_replay_result.transaction_committed &&
                        !sidecar_review_repair_replay_result.repair_reset_event_written &&
                        sidecar_review_repair_replay_result.repair_reset_event_already_present &&
                        sidecar_review_repair_replay_result.workorder_rows_reset == 0 &&
                        sidecar_review_repair_replay_result.workorder_rows_already_reset == pending_materialize_entry->chunks.size(),
                        "sync session checkpoint sidecar review repair reset is idempotent after operator repair evidence is present");
                SyncValidationResult sidecar_operator_owner_release =
                    sync_internal_release_checkpoint_mutation_owner_lease(
                        startup_review_daemon_checkpoint_db.string(),
                        "session-main",
                        sidecar_operator_owner_lease.capability,
                        1016);
                require(sidecar_operator_owner_release.ok,
                        "sync session checkpoint sidecar operator fixture retires its exact generation before the CLI acquires a successor");
                const fs::path sidecar_repair_cli_report_path = fs::temp_directory_path() / ("anonsync-sync-sidecar-repair-cli-" + std::to_string(selftest_ticks) + ".json");
                fs::remove(sidecar_repair_cli_report_path, apply_cleanup_ec);
                int sidecar_repair_cli_rc = run_sync_checkpoint_sidecar_repair_reset_command(startup_review_daemon_checkpoint_db.string(),
                                                                                             "session-main",
                                                                                             fake_staging_root.string(),
                                                                                             pending_materialize_entry->path.value,
                                                                                             sidecar_review_repair_options.review_event_idempotency_key,
                                                                                             sidecar_review_repair_options.decision_operator_id,
                                                                                             sidecar_review_repair_options.decision_reason,
                                                                                             checked_cli_integer_for_selftest(
                                                                                                 sidecar_review_repair_options.repair_at_epoch,
                                                                                                 "sidecar repair epoch"),
                                                                                             sidecar_review_repair_options.repair_worker_id,
                                                                                             checked_cli_integer_for_selftest(
                                                                                                 sidecar_review_repair_options.repair_worker_lease_epoch,
                                                                                                 "sidecar repair worker lease epoch"),
                                                                                             checked_cli_integer_for_selftest(
                                                                                                 sidecar_review_repair_options.repair_worker_lease_seconds,
                                                                                                 "sidecar repair worker lease seconds"),
                                                                                             checked_cli_integer_for_selftest(
                                                                                                 sidecar_review_repair_options.workorder_retry_backoff_seconds,
                                                                                                 "sidecar repair retry backoff seconds"),
                                                                                             sidecar_repair_cli_report_path.string());
                Json sidecar_repair_cli_report = load_json(sidecar_repair_cli_report_path.string());
                require(sidecar_repair_cli_rc == 0 &&
                        sidecar_repair_cli_report.at("format").str() == "anonsync-sync-checkpoint-sidecar-repair-reset-report-v1" &&
                        sidecar_repair_cli_report.at("ok").boolean(false) &&
                        sidecar_repair_cli_report.at("repair_reset").at("repair_reset_event_already_present").boolean(false) &&
                        sidecar_repair_cli_report.at("repair_reset").at("workorder_rows_reset").integer(-1) == 0 &&
                        sidecar_repair_cli_report.at("repair_reset").at("workorder_rows_already_reset").integer(-1) == static_cast<long long>(pending_materialize_entry->chunks.size()),
                        "sync checkpoint sidecar repair reset CLI preserves idempotency and emits retry evidence JSON");
                {
                    SyncSqliteDb sidecar_review_repair_probe;
                    int sidecar_review_repair_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    sidecar_review_repair_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(startup_review_daemon_checkpoint_db.string().c_str(), sidecar_review_repair_probe.db.out(), sidecar_review_repair_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(sidecar_review_repair_probe.db, "could not reopen checkpoint db for sidecar review repair reset probe"));
                    }
                    const std::uint64_t sidecar_review_repair_rows = sqlite_count_for_session_or_throw(sidecar_review_repair_probe.db,
                        "SELECT COUNT(*) FROM sync_session_bound_peer_sidecar_review_repair_resets WHERE session_id=? AND repair_state='repaired-reset' AND repaired_by_operator_id='operator-sidecar-repair-alpha';",
                        "session-main",
                        "sidecar review repair reset event count");
                    const std::uint64_t sidecar_review_repair_claimed_rows = sqlite_count_for_session_or_throw(sidecar_review_repair_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='claimed' AND worker_id='worker-repair';",
                        "session-main",
                        "sidecar review repair reset claimed workorder count");
                    const std::uint64_t sidecar_review_repair_quarantined_rows = sqlite_count_for_session_or_throw(sidecar_review_repair_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='quarantined';",
                        "session-main",
                        "sidecar review repair reset quarantined workorder count");
                    require(sidecar_review_repair_rows == 1 &&
                            sidecar_review_repair_claimed_rows == pending_materialize_entry->chunks.size() &&
                            sidecar_review_repair_quarantined_rows == 0,
                            "sync session checkpoint sidecar review repair reset persists a repair event and only reopens the matched quarantined rows");
                }
                SyncSessionCheckpointOperatorStatusOptions repaired_status_options = review_stop_status_options;
                repaired_status_options.scheduler_now_epoch = 1016;
                SyncSessionCheckpointOperatorStatusResult repaired_status;
                SyncValidationResult repaired_status_run = load_sync_session_checkpoint_operator_status(repaired_status_options,
                                                                                                        repaired_status);
                require(repaired_status_run.ok &&
                        repaired_status.status_loaded &&
                        repaired_status.sidecar_review_events == 1 &&
                        repaired_status.pending_sidecar_review_events == 0 &&
                        repaired_status.sidecar_review_repair_reset_events == 1 &&
                        repaired_status.repair_reset_workorder_rows_reset == pending_materialize_entry->chunks.size() &&
                        repaired_status.claimed_workorder_rows == pending_materialize_entry->chunks.size() &&
                        repaired_status.quarantined_workorder_rows == 0 &&
                        !repaired_status.operator_attention_required &&
                        repaired_status.safe_to_schedule &&
                        repaired_status.suggested_next_action == "wait-live-lease-or-run-owner",
                        "sync session checkpoint operator status clears review attention after repair reset reopens rows under a live lease");
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions repair_unblock_loop_options =
                    make_transfer_workorder_daemon_loop_options(startup_review_daemon_checkpoint_db, 1020, "worker-charlie", 9, 10);
                repair_unblock_loop_options.max_loop_passes = 1;
                repair_unblock_loop_options.recover_bound_peer_sidecars_before_scheduling = true;
                repair_unblock_loop_options.startup_sidecar_remote_file_entries = {*pending_materialize_entry};
                repair_unblock_loop_options.startup_sidecar_apply_entries = {*pending_materialize_apply};
                SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult repair_unblock_loop_result;
                SyncValidationResult repair_unblock_loop_run = run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(repair_unblock_loop_options,
                                                                                                                               repair_unblock_loop_result);
                require(repair_unblock_loop_run.ok &&
                        repair_unblock_loop_result.daemon_loop_completed &&
                        repair_unblock_loop_result.startup_sidecar_recovery_attempted &&
                        repair_unblock_loop_result.startup_sidecar_recovery_completed &&
                        !repair_unblock_loop_result.startup_sidecar_recovery_blocked_scheduling &&
                        !repair_unblock_loop_result.stopped_before_scheduling_on_sidecar_recovery &&
                        repair_unblock_loop_result.passes_attempted == 1,
                        "sync session checkpoint daemon startup sidecar gate unblocks after operator repair reset returns dirty rows to retryable scheduling");
                SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineOptions missing_sidecar_review_quarantine_options = sidecar_review_quarantine_options;
                missing_sidecar_review_quarantine_options.review_event_idempotency_key = "sync-sidecar-review:v1:missing-review-event-key";
                SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineResult missing_sidecar_review_quarantine_result;
                require(!quarantine_sync_session_checkpoint_bound_peer_sidecar_review_event(missing_sidecar_review_quarantine_options,
                                                                                           missing_sidecar_review_quarantine_result).ok,
                        "sync session checkpoint sidecar review quarantine rejects a missing review event key");
                fs::remove(pending_materialize_staged_path, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove daemon startup sidecar review stop staged fixture: " + apply_cleanup_ec.message());
                fs::remove_all(claim_receipt_dir, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove daemon startup sidecar review stop receipt fixture: " + apply_cleanup_ec.message());
            }
            {
                const fs::path ingestion_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-bound-peer-ingest-" + std::to_string(selftest_ticks) + ".sqlite");
                fs::remove(ingestion_checkpoint_db, apply_cleanup_ec);
                fs::remove(fs::path(ingestion_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
                fs::remove(fs::path(ingestion_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
                sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                            ingestion_checkpoint_db,
                                            "sync session checkpoint bound peer ingestion facade selftest");
                SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions ingestion_binding = binding_options;
                ingestion_binding.sqlite_path = ingestion_checkpoint_db.string();
                SyncSessionCheckpointBoundPeerChunkIngestionResult ingestion_result;
                SyncValidationResult ingestion_run = ingest_sync_session_checkpoint_bound_peer_chunk_response_batch(ingestion_binding,
                                                                                                                    *pending_materialize_entry,
                                                                                                                    *pending_materialize_apply,
                                                                                                                    claimed_peer_response,
                                                                                                                    claimed_chunk_bytes,
                                                                                                                    claimed_write_options,
                                                                                                                    ingestion_result);
                require(ingestion_run.ok &&
                        ingestion_result.sidecar_acceptance_attempted &&
                        ingestion_result.sidecar_acceptance_completed &&
                        ingestion_result.database_advance_attempted &&
                        ingestion_result.database_advance_completed &&
                        ingestion_result.transport_safe_single_entrypoint_completed &&
                        !ingestion_result.recoverable_sidecar_acceptance_without_db_advance &&
                        ingestion_result.chunks_written == pending_materialize_entry->chunks.size() &&
                        ingestion_result.bytes_bound == pending_materialize_entry->size_bytes &&
                        ingestion_result.bytes_verified == pending_materialize_entry->size_bytes &&
                        ingestion_result.receipt_rows_reactivated_from_committed_cleaned == pending_materialize_entry->chunks.size() &&
                        ingestion_result.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                        ingestion_result.content_sha256 == pending_materialize_entry->content_sha256 &&
                        fs::exists(pending_materialize_staged_path) &&
                        fs::exists(claim_receipt_dir),
                        "sync session checkpoint bound peer ingestion facade writes sidecars then advances durable DB progress through one transport entrypoint");
                {
                    SyncSqliteDb ingestion_probe;
                    int ingestion_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
                    ingestion_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
                    if (::anonsync::persistence::open_verified_sqlite_database(ingestion_checkpoint_db.string().c_str(), ingestion_probe.db.out(), ingestion_probe_flags, nullptr) != SQLITE_OK) {
                        throw std::runtime_error(sqlite_error_message(ingestion_probe.db, "could not reopen checkpoint db for bound peer ingestion facade probe"));
                    }
                    const std::uint64_t facade_completed_workorders = sqlite_count_for_session_or_throw(ingestion_probe.db,
                        "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND path='docs/session-report.txt' AND work_state='completed' AND worker_id='worker-charlie';",
                        "session-main",
                        "bound peer ingestion facade completed workorder count");
                    const std::uint64_t facade_accepted_receipts = sqlite_count_for_session_or_throw(ingestion_probe.db,
                        "SELECT COUNT(*) FROM sync_session_chunk_receipts WHERE session_id=? AND path='docs/session-report.txt' AND receipt_state='accepted';",
                        "session-main",
                        "bound peer ingestion facade accepted receipt count");
                    require(facade_completed_workorders == pending_materialize_entry->chunks.size() &&
                            facade_accepted_receipts == pending_materialize_entry->chunks.size(),
                            "sync session checkpoint bound peer ingestion facade leaves SQLite rows completed and accepted");
                }
                fs::remove(pending_materialize_staged_path, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove bound peer ingestion facade staged fixture: " + apply_cleanup_ec.message());
                fs::remove_all(claim_receipt_dir, apply_cleanup_ec);
                if (apply_cleanup_ec) throw std::runtime_error("could not remove bound peer ingestion facade receipt fixture: " + apply_cleanup_ec.message());
            }
        }

        SyncSessionCheckpointResumeActionPlanResult post_claim_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, post_claim_action_plan).ok &&
                post_claim_action_plan.resume_transfer_files == 1 &&
                post_claim_action_plan.materialize_staged_files == 0,
                "sync session checkpoint resume transfer claim does not pretend claimed work has materialized staged evidence");
        SyncSessionCheckpointResumeTransferExecutionOptions live_steal_transfer_execute_options;
        live_steal_transfer_execute_options.sqlite_path = fake_session_checkpoint_db.string();
        live_steal_transfer_execute_options.session_id = "session-main";
        live_steal_transfer_execute_options.source_root_path = fake_source_root.string();
        live_steal_transfer_execute_options.destination_root_path = fake_destination_root.string();
        live_steal_transfer_execute_options.staging_root_path = fake_staging_root.string();
        live_steal_transfer_execute_options.expected_folder_id = "folder-alpha";
        live_steal_transfer_execute_options.expected_source_device_id = "device-bravo";
        live_steal_transfer_execute_options.expected_destination_device_id = "device-alpha";
        live_steal_transfer_execute_options.expected_peer_id = "peer-bravo";
        live_steal_transfer_execute_options.peer_session_id = "session-main-resume";
        live_steal_transfer_execute_options.worker_id = "worker-echo";
        live_steal_transfer_execute_options.worker_lease_epoch = 8;
        live_steal_transfer_execute_options.workorder_claim_now_epoch = 1005;
        live_steal_transfer_execute_options.worker_lease_seconds = 10;
        SyncSessionCheckpointResumeTransferExecutionResult live_steal_transfer_execute_result;
        SyncValidationResult live_steal_transfer_execute_run = execute_sync_session_checkpoint_resume_transfer_workorders(live_steal_transfer_execute_options,
                                                                                                                           live_steal_transfer_execute_result);
        require(!live_steal_transfer_execute_run.ok,
                "sync session checkpoint resume transfer executor rejects another worker trying to steal a live claimed row before lease expiry");

        SyncSessionCheckpointResumeTransferClaimOptions expired_reclaim_options = transfer_claim_options;
        expired_reclaim_options.worker_id = "worker-delta";
        expired_reclaim_options.worker_lease_epoch = 9;
        expired_reclaim_options.workorder_claim_now_epoch = 1010;
        expired_reclaim_options.worker_lease_seconds = 15;
        SyncSessionCheckpointResumeTransferClaimResult expired_reclaim_result;
        SyncValidationResult expired_reclaim_run = claim_sync_session_checkpoint_resume_transfer_workorders(expired_reclaim_options,
                                                                                                            expired_reclaim_result);
        require(expired_reclaim_run.ok &&
                expired_reclaim_result.worker_id == "worker-delta" &&
                expired_reclaim_result.worker_lease_id.starts_with("sync-resume-transfer-lease:v1:") &&
                expired_reclaim_result.workorder_claim_now_epoch == 1010 &&
                expired_reclaim_result.worker_lease_seconds == 15 &&
                expired_reclaim_result.lease_expires_at_epoch == 1025 &&
                expired_reclaim_result.files_claimed == 1 &&
                expired_reclaim_result.workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                expired_reclaim_result.workorder_rows_already_owned == 0 &&
                expired_reclaim_result.workorder_rows_reclaimed == pending_materialize_entry->chunks.size() &&
                expired_reclaim_result.workorder_reclaim_events_written == pending_materialize_entry->chunks.size() &&
                expired_reclaim_result.files.size() == 1 &&
                expired_reclaim_result.files[0].worker_id == "worker-delta" &&
                expired_reclaim_result.files[0].claimed_at_epoch == 1010 &&
                expired_reclaim_result.files[0].lease_expires_at_epoch == 1025 &&
                expired_reclaim_result.files[0].workorder_rows_reclaimed == pending_materialize_entry->chunks.size() &&
                expired_reclaim_result.files[0].workorder_reclaim_events_written == pending_materialize_entry->chunks.size(),
                "sync session checkpoint resume transfer claim reclaims expired rows for a new worker lease without executing bytes");
        {
            SyncSqliteDb reclaim_probe_handle;
            int reclaim_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            reclaim_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), reclaim_probe_handle.db.out(), reclaim_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(reclaim_probe_handle.db, "could not reopen checkpoint db for expired resume transfer workorder reclaim probe"));
            }
            const std::uint64_t reclaimed_workorder_rows = sqlite_count_for_session_or_throw(reclaim_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-delta' AND claimed_at_epoch=1010 AND lease_expires_at_epoch=1025 AND claim_attempts=2;",
                "session-main",
                "resume transfer expired reclaim workorder count");
            const std::uint64_t stale_worker_rows = sqlite_count_for_session_or_throw(reclaim_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-charlie';",
                "session-main",
                "resume transfer stale worker workorder count after reclaim");
            const std::uint64_t reclaim_event_rows = sqlite_count_for_session_or_throw(reclaim_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_reclaim_events WHERE session_id=? AND previous_worker_id='worker-charlie' AND previous_claimed_at_epoch=1000 AND previous_lease_expires_at_epoch=1010 AND new_worker_id='worker-delta' AND new_claimed_at_epoch=1010 AND new_lease_expires_at_epoch=1025 AND reclaim_attempt=2 AND reclaim_reason='expired-lease';",
                "session-main",
                "resume transfer expired reclaim audit event count");
            require(reclaimed_workorder_rows == pending_materialize_entry->chunks.size() &&
                    stale_worker_rows == 0 &&
                    reclaim_event_rows == pending_materialize_entry->chunks.size() &&
                    !fs::exists(pending_materialize_staged_path),
                    "sync session checkpoint resume transfer reclaim updates claim ownership and timing while leaving previous-owner audit events and no staged bytes");
        }
        const fs::path abandon_cap_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-abandon-cap-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(abandon_cap_checkpoint_db, apply_cleanup_ec);
        fs::remove(fs::path(abandon_cap_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(abandon_cap_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(fake_session_checkpoint_db,
                                    abandon_cap_checkpoint_db,
                                    "sync session checkpoint resume transfer abandon-cap selftest");
        SyncSessionCheckpointResumeTransferClaimOptions capped_abandon_options = expired_reclaim_options;
        capped_abandon_options.sqlite_path = abandon_cap_checkpoint_db.string();
        capped_abandon_options.worker_id = "worker-foxtrot";
        capped_abandon_options.worker_lease_epoch = 10;
        capped_abandon_options.workorder_claim_now_epoch = 1025;
        capped_abandon_options.worker_lease_seconds = 20;
        capped_abandon_options.max_workorder_claim_attempts = 2;
        SyncSessionCheckpointResumeTransferClaimResult capped_abandon_result;
        SyncValidationResult capped_abandon_run = claim_sync_session_checkpoint_resume_transfer_workorders(capped_abandon_options,
                                                                                                           capped_abandon_result);
        require(capped_abandon_run.ok &&
                capped_abandon_result.worker_id == "worker-foxtrot" &&
                capped_abandon_result.workorder_claim_now_epoch == 1025 &&
                capped_abandon_result.worker_lease_seconds == 20 &&
                capped_abandon_result.lease_expires_at_epoch == 1045 &&
                capped_abandon_result.files_claimed == 0 &&
                capped_abandon_result.files_abandoned == 1 &&
                capped_abandon_result.workorder_rows_claimed == 0 &&
                capped_abandon_result.workorder_rows_reclaimed == 0 &&
                capped_abandon_result.workorder_reclaim_events_written == 0 &&
                capped_abandon_result.workorder_rows_abandoned == pending_materialize_entry->chunks.size() &&
                capped_abandon_result.workorder_abandon_events_written == pending_materialize_entry->chunks.size() &&
                capped_abandon_result.files.size() == 1 &&
                capped_abandon_result.files[0].path.value == "docs/session-report.txt" &&
                !capped_abandon_result.files[0].workorder_claimed &&
                capped_abandon_result.files[0].workorder_rows_claimed == 0 &&
                capped_abandon_result.files[0].workorder_rows_abandoned == pending_materialize_entry->chunks.size() &&
                capped_abandon_result.files[0].workorder_abandon_events_written == pending_materialize_entry->chunks.size(),
                "sync session checkpoint resume transfer claim abandons expired rows at a deterministic claim-attempt cap without executing bytes");
        {
            SyncSqliteDb abandon_probe_handle;
            int abandon_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            abandon_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(abandon_cap_checkpoint_db.string().c_str(), abandon_probe_handle.db.out(), abandon_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(abandon_probe_handle.db, "could not reopen checkpoint db for expired resume transfer workorder abandon probe"));
            }
            const std::uint64_t abandoned_workorder_rows = sqlite_count_for_session_or_throw(abandon_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='abandoned' AND worker_id='worker-delta' AND claimed_at_epoch=1010 AND lease_expires_at_epoch=1025 AND claim_attempts=2;",
                "session-main",
                "resume transfer abandoned workorder count");
            const std::uint64_t abandon_event_rows = sqlite_count_for_session_or_throw(abandon_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_abandon_events WHERE session_id=? AND previous_worker_id='worker-delta' AND decision_worker_id='worker-foxtrot' AND abandon_attempt=2 AND max_claim_attempts=2 AND abandoned_at_epoch=1025 AND abandon_reason='max-claim-attempts-exhausted';",
                "session-main",
                "resume transfer abandoned workorder event count");
            const std::uint64_t preserved_reclaim_event_rows = sqlite_count_for_session_or_throw(abandon_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_reclaim_events WHERE session_id=? AND previous_worker_id='worker-charlie' AND new_worker_id='worker-delta' AND reclaim_attempt=2 AND reclaim_reason='expired-lease';",
                "session-main",
                "resume transfer abandoned workorder preserved reclaim event count");
            require(abandoned_workorder_rows == pending_materialize_entry->chunks.size() &&
                    abandon_event_rows == pending_materialize_entry->chunks.size() &&
                    preserved_reclaim_event_rows == pending_materialize_entry->chunks.size() &&
                    !fs::exists(pending_materialize_staged_path),
                    "sync session checkpoint resume transfer abandon cap preserves both abandoned row state and previous reclaim history without staged bytes");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(abandon_cap_checkpoint_db, 1025);
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.queue_facts_returned == pending_materialize_entry->chunks.size() &&
                    queue_result.abandoned_review_rows == pending_materialize_entry->chunks.size() &&
                    !queue_result.facts.empty() &&
                    queue_result.facts[0].queue_kind == SyncSessionCheckpointResumeTransferWorkorderQueueKind::AbandonedReview &&
                    queue_result.facts[0].terminal_review_required,
                    "sync session checkpoint resume transfer queue selector exposes abandoned rows only as terminal review facts");
        }
        SyncSessionCheckpointResumeTransferClaimOptions capped_reclaim_after_abandon_options = capped_abandon_options;
        capped_reclaim_after_abandon_options.worker_id = "worker-golf";
        capped_reclaim_after_abandon_options.worker_lease_epoch = 11;
        capped_reclaim_after_abandon_options.workorder_claim_now_epoch = 1026;
        SyncSessionCheckpointResumeTransferClaimResult capped_reclaim_after_abandon_result;
        SyncValidationResult capped_reclaim_after_abandon_run = claim_sync_session_checkpoint_resume_transfer_workorders(capped_reclaim_after_abandon_options,
                                                                                                                         capped_reclaim_after_abandon_result);
        require(!capped_reclaim_after_abandon_run.ok,
                "sync session checkpoint resume transfer claim refuses to reclaim rows after abandon policy has made them terminal");
        SyncSessionCheckpointResumeTransferTerminalResetOptions abandon_reset_options;
        abandon_reset_options.sqlite_path = abandon_cap_checkpoint_db.string();
        abandon_reset_options.session_id = "session-main";
        abandon_reset_options.source_root_path = fake_source_root.string();
        abandon_reset_options.destination_root_path = fake_destination_root.string();
        abandon_reset_options.staging_root_path = fake_staging_root.string();
        abandon_reset_options.expected_folder_id = "folder-alpha";
        abandon_reset_options.expected_source_device_id = "device-bravo";
        abandon_reset_options.expected_destination_device_id = "device-alpha";
        abandon_reset_options.expected_peer_id = "peer-bravo";
        abandon_reset_options.peer_session_id = "session-main-resume";
        abandon_reset_options.worker_id = "worker-hotel";
        abandon_reset_options.worker_lease_epoch = 12;
        abandon_reset_options.workorder_reset_now_epoch = 1030;
        abandon_reset_options.worker_lease_seconds = 20;
        abandon_reset_options.workorder_retry_backoff_seconds = 5;
        abandon_reset_options.reset_abandoned_workorders = true;
        abandon_reset_options.reset_quarantined_workorders = false;
        SyncSessionCheckpointResumeTransferTerminalResetResult abandon_reset_result;
        SyncValidationResult abandon_reset_run = reset_sync_session_checkpoint_resume_transfer_terminal_workorders(abandon_reset_options,
                                                                                                                   abandon_reset_result);
        require(abandon_reset_run.ok &&
                abandon_reset_result.transaction_committed &&
                abandon_reset_result.worker_id == "worker-hotel" &&
                abandon_reset_result.workorder_reset_now_epoch == 1030 &&
                abandon_reset_result.lease_expires_at_epoch == 1050 &&
                abandon_reset_result.retry_at_epoch == 1055 &&
                abandon_reset_result.files_reset == 1 &&
                abandon_reset_result.terminal_rows_found == pending_materialize_entry->chunks.size() &&
                abandon_reset_result.workorder_rows_reset == pending_materialize_entry->chunks.size() &&
                abandon_reset_result.abandoned_rows_reset == pending_materialize_entry->chunks.size() &&
                abandon_reset_result.quarantined_rows_reset == 0 &&
                abandon_reset_result.reset_events_written == pending_materialize_entry->chunks.size() &&
                abandon_reset_result.files.size() == 1 &&
                abandon_reset_result.files[0].abandoned_rows_reset == pending_materialize_entry->chunks.size() &&
                abandon_reset_result.files[0].reset_events_written == pending_materialize_entry->chunks.size(),
                "sync session checkpoint resume transfer terminal reset reopens abandoned rows only through an explicit audited reset");
        {
            SyncSqliteDb abandon_reset_probe_handle;
            int abandon_reset_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            abandon_reset_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(abandon_cap_checkpoint_db.string().c_str(), abandon_reset_probe_handle.db.out(), abandon_reset_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(abandon_reset_probe_handle.db, "could not reopen checkpoint db for workorder abandon reset probe"));
            }
            const std::uint64_t reset_abandon_claimed_rows = sqlite_count_for_session_or_throw(abandon_reset_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='claimed' AND worker_id='worker-hotel' AND claimed_at_epoch=1030 AND lease_expires_at_epoch=1050 AND retry_at_epoch=1055 AND claim_attempts=1;",
                "session-main",
                "resume transfer reset abandoned workorder claimed count");
            const std::uint64_t reset_abandon_event_rows = sqlite_count_for_session_or_throw(abandon_reset_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_reset_events WHERE session_id=? AND previous_work_state='abandoned' AND previous_worker_id='worker-delta' AND new_worker_id='worker-hotel' AND reset_at_epoch=1030 AND reset_reason='operator-terminal-reset';",
                "session-main",
                "resume transfer abandoned workorder reset audit event count");
            require(reset_abandon_claimed_rows == pending_materialize_entry->chunks.size() &&
                    reset_abandon_event_rows == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer terminal reset preserves abandon evidence while reopening claimed rows");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(abandon_cap_checkpoint_db, 1030);
            queue_options.worker_id = abandon_reset_result.worker_id;
            queue_options.worker_lease_id = abandon_reset_result.worker_lease_id;
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.queue_facts_returned == pending_materialize_entry->chunks.size() &&
                    queue_result.owned_claim_ready_rows == pending_materialize_entry->chunks.size() &&
                    queue_result.reset_history_claimed_rows == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer queue selector returns reset abandoned rows as fresh owned claimed work");
        }
        SyncSessionCheckpointResumeTransferClaimOptions post_reset_claim_options = transfer_claim_options;
        post_reset_claim_options.sqlite_path = abandon_cap_checkpoint_db.string();
        post_reset_claim_options.worker_id = "worker-hotel";
        post_reset_claim_options.worker_lease_epoch = 12;
        post_reset_claim_options.workorder_claim_now_epoch = 1030;
        post_reset_claim_options.worker_lease_seconds = 20;
        post_reset_claim_options.workorder_retry_backoff_seconds = 5;
        SyncSessionCheckpointResumeTransferClaimResult post_reset_claim_result;
        SyncValidationResult post_reset_claim_run = claim_sync_session_checkpoint_resume_transfer_workorders(post_reset_claim_options,
                                                                                                             post_reset_claim_result);
        require(post_reset_claim_run.ok &&
                post_reset_claim_result.workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                post_reset_claim_result.workorder_rows_already_owned == pending_materialize_entry->chunks.size() &&
                post_reset_claim_result.files_claimed == 1 &&
                post_reset_claim_result.retry_at_epoch == 1055,
                "sync session checkpoint resume transfer claim treats reset terminal rows as ordinary owned claimed work");
        SyncSessionCheckpointResumeTransferExecutionOptions stale_owner_transfer_execute_options = live_steal_transfer_execute_options;
        stale_owner_transfer_execute_options.worker_id = "worker-charlie";
        stale_owner_transfer_execute_options.worker_lease_epoch = 7;
        stale_owner_transfer_execute_options.workorder_claim_now_epoch = 1011;
        stale_owner_transfer_execute_options.worker_lease_seconds = 10;
        SyncSessionCheckpointResumeTransferExecutionResult stale_owner_transfer_execute_result;
        SyncValidationResult stale_owner_transfer_execute_run = execute_sync_session_checkpoint_resume_transfer_workorders(stale_owner_transfer_execute_options,
                                                                                                                            stale_owner_transfer_execute_result);
        require(!stale_owner_transfer_execute_run.ok,
                "sync session checkpoint resume transfer executor rejects the stale worker after an expired claim is reclaimed");
        SyncSessionCheckpointResumeTransferExecutionOptions transfer_execute_options;
        transfer_execute_options.sqlite_path = fake_session_checkpoint_db.string();
        transfer_execute_options.session_id = "session-main";
        transfer_execute_options.source_root_path = fake_source_root.string();
        transfer_execute_options.destination_root_path = fake_destination_root.string();
        transfer_execute_options.staging_root_path = fake_staging_root.string();
        transfer_execute_options.expected_folder_id = "folder-alpha";
        transfer_execute_options.expected_source_device_id = "device-bravo";
        transfer_execute_options.expected_destination_device_id = "device-alpha";
        transfer_execute_options.expected_peer_id = "peer-bravo";
        transfer_execute_options.peer_session_id = "session-main-resume";
        transfer_execute_options.worker_id = "worker-delta";
        transfer_execute_options.worker_lease_epoch = 9;
        transfer_execute_options.workorder_claim_now_epoch = 1011;
        transfer_execute_options.worker_lease_seconds = 15;
        SyncSessionCheckpointResumeTransferExecutionResult transfer_execute_result;
        SyncValidationResult transfer_execute_run = execute_sync_session_checkpoint_resume_transfer_workorders(transfer_execute_options,
                                                                                                               transfer_execute_result);
        require(transfer_execute_run.ok &&
                transfer_execute_result.transfer_plan_loaded &&
                transfer_execute_result.worker_id == "worker-delta" &&
                transfer_execute_result.worker_lease_id.starts_with("sync-resume-transfer-lease:v1:") &&
                transfer_execute_result.durable_integrity_verified &&
                transfer_execute_result.source_filesystem_verified &&
                transfer_execute_result.transaction_committed &&
                transfer_execute_result.workorder_claim_now_epoch == 1011 &&
                transfer_execute_result.worker_lease_seconds == 15 &&
                transfer_execute_result.lease_expires_at_epoch == 1026 &&
                transfer_execute_result.files_considered == fake_session_result.files_materialized &&
                transfer_execute_result.files_executed == 1 &&
                transfer_execute_result.files_skipped == 0 &&
                transfer_execute_result.workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.workorder_rows_reclaimed == 0 &&
                transfer_execute_result.workorder_reclaim_events_written == 0 &&
                transfer_execute_result.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.chunks_assigned == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.chunks_written == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.receipts_reused == 0 &&
                transfer_execute_result.receipt_rows_upserted == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.bytes_written == pending_materialize_entry->size_bytes &&
                transfer_execute_result.post_materialize_staged_files == 1 &&
                transfer_execute_result.post_resume_transfer_files == 0 &&
                transfer_execute_result.files.size() == 1 &&
                transfer_execute_result.files[0].path.value == "docs/session-report.txt" &&
                transfer_execute_result.files[0].execution_idempotency_key.starts_with("sync-resume-transfer-execute:v1:") &&
                transfer_execute_result.files[0].worker_id == "worker-delta" &&
                transfer_execute_result.files[0].worker_lease_id == transfer_execute_result.worker_lease_id &&
                transfer_execute_result.files[0].workorder_claimed &&
                transfer_execute_result.files[0].workorder_completed &&
                transfer_execute_result.files[0].claimed_at_epoch == 1010 &&
                transfer_execute_result.files[0].lease_expires_at_epoch == 1025 &&
                transfer_execute_result.files[0].workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.files[0].workorder_rows_reclaimed == 0 &&
                transfer_execute_result.files[0].workorder_reclaim_events_written == 0 &&
                transfer_execute_result.files[0].workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.files[0].source_chunks_verified &&
                transfer_execute_result.files[0].database_rows_updated &&
                transfer_execute_result.files[0].staged_file_complete_after &&
                transfer_execute_result.files[0].chunks_verified_after == pending_materialize_entry->chunks.size() &&
                transfer_execute_result.files[0].content_sha256_after == pending_materialize_entry->content_sha256,
                "sync session checkpoint resume transfer executor fetches planned fake-peer chunks into staged receipt evidence and durable workorder claims");
        {
            SyncSqliteDb workorder_probe_handle;
            int workorder_probe_flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            workorder_probe_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), workorder_probe_handle.db.out(), workorder_probe_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(workorder_probe_handle.db, "could not reopen checkpoint db for durable resume transfer workorder probe"));
            }
            const std::uint64_t workorder_rows = sqlite_count_for_session_or_throw(workorder_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=?;",
                "session-main",
                "resume transfer workorder count");
            const std::uint64_t completed_workorder_rows = sqlite_count_for_session_or_throw(workorder_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders WHERE session_id=? AND work_state='completed' AND worker_id='worker-delta' AND claimed_at_epoch=1010 AND lease_expires_at_epoch=1025 AND claim_attempts=2;",
                "session-main",
                "resume transfer completed workorder count");
            const std::uint64_t completed_reclaim_event_rows = sqlite_count_for_session_or_throw(workorder_probe_handle.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorder_reclaim_events WHERE session_id=? AND previous_worker_id='worker-charlie' AND new_worker_id='worker-delta' AND reclaim_attempt=2 AND reclaim_reason='expired-lease';",
                "session-main",
                "resume transfer completed workorder reclaim audit event count");
            require(workorder_rows == pending_materialize_entry->chunks.size() &&
                    completed_workorder_rows == pending_materialize_entry->chunks.size() &&
                    completed_reclaim_event_rows == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer executor persists completed worker-owned workorder rows while preserving reclaim audit history");
        }
        {
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions queue_options = make_transfer_workorder_queue_options(fake_session_checkpoint_db, 1100);
            SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
            SyncValidationResult queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, queue_result);
            require(queue_run.ok &&
                    queue_result.workorder_rows_considered == pending_materialize_entry->chunks.size() &&
                    queue_result.queue_facts_returned == 0 &&
                    queue_result.completed_rows_ignored == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer queue selector ignores completed rows by default");
            queue_options.include_completed_workorders = true;
            SyncSessionCheckpointResumeTransferWorkorderQueueResult completed_queue_result;
            SyncValidationResult completed_queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(queue_options, completed_queue_result);
            require(completed_queue_run.ok &&
                    completed_queue_result.queue_facts_returned == pending_materialize_entry->chunks.size() &&
                    completed_queue_result.completed_rows_ignored == pending_materialize_entry->chunks.size() &&
                    !completed_queue_result.facts.empty() &&
                    completed_queue_result.facts[0].queue_kind == SyncSessionCheckpointResumeTransferWorkorderQueueKind::CompletedIgnored,
                    "sync session checkpoint resume transfer queue selector can expose completed rows only when explicitly requested for audit");
        }
        SyncSessionCheckpointResumeActionPlanResult post_transfer_execute_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, post_transfer_execute_action_plan).ok &&
                post_transfer_execute_action_plan.materialize_staged_files == 1 &&
                post_transfer_execute_action_plan.resume_transfer_files == 0,
                "sync session checkpoint resume transfer executor promotes completed staged work to materialization restart state");
        apply_cleanup_ec.clear();
        fs::remove(pending_materialize_staged_path, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not remove resume transfer executor staged fixture: " + apply_cleanup_ec.message());
        NormalizedSyncPath pending_materialize_receipt_dir_relative;
        pending_materialize_receipt_dir_relative.value = pending_materialize_staged_relative.value + ".chunks";
        const fs::path pending_materialize_receipt_dir = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
            fake_staging_root,
            pending_materialize_receipt_dir_relative,
            "sync session checkpoint resume transfer executor fixture receipt directory"));
        apply_cleanup_ec.clear();
        fs::remove_all(pending_materialize_receipt_dir, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not remove resume transfer executor receipt fixture: " + apply_cleanup_ec.message());
        SyncSessionCheckpointResult action_plan_restored_checkpoint;
        SyncValidationResult action_plan_restored_run = persist_sync_fake_peer_session_checkpoint(fake_session_options,
                                                                                                  fake_session_result,
                                                                                                  checkpoint_options,
                                                                                                  action_plan_restored_checkpoint);
        require(action_plan_restored_run.ok && action_plan_restored_checkpoint.checkpoint_reloaded,
                "sync session checkpoint reset restores terminal rows after pending action-plan fixture");
        apply_cleanup_ec.clear();
        fs::remove(fake_destination_root / "docs/session-report.txt", apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not remove destination fixture for resume cycle executor test: " + apply_cleanup_ec.message());
        {
            SyncSqliteDb resume_cycle_handle;
            int resume_cycle_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            resume_cycle_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), resume_cycle_handle.db.out(), resume_cycle_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(resume_cycle_handle.db, "could not reopen checkpoint db for resume cycle executor test"));
            }
            sqlite_exec_or_throw(resume_cycle_handle.db,
                                 "UPDATE sync_session_file_results SET materialized=0, staging_artifacts_cleaned=0 "
                                 "WHERE session_id='session-main' AND path='docs/session-report.txt';",
                                 "could not mark checkpoint rows pending for resume cycle executor test");
        }
        SyncSessionCheckpointResumeCycleOptions resume_cycle_options;
        resume_cycle_options.sqlite_path = fake_session_checkpoint_db.string();
        resume_cycle_options.session_id = "session-main";
        resume_cycle_options.source_root_path = fake_source_root.string();
        resume_cycle_options.destination_root_path = fake_destination_root.string();
        resume_cycle_options.staging_root_path = fake_staging_root.string();
        resume_cycle_options.expected_folder_id = "folder-alpha";
        resume_cycle_options.expected_source_device_id = "device-bravo";
        resume_cycle_options.expected_destination_device_id = "device-alpha";
        resume_cycle_options.expected_peer_id = "peer-bravo";
        resume_cycle_options.peer_session_id = "session-main-cycle";
        SyncSessionCheckpointResumeCycleResult resume_cycle_result;
        SyncValidationResult resume_cycle_run = execute_sync_session_checkpoint_resume_cycle(resume_cycle_options,
                                                                                             resume_cycle_result);
        if (!resume_cycle_run.ok) {
            throw std::runtime_error("sync session checkpoint resume cycle executor test failed before assertions: " + resume_cycle_run.reason);
        }
        std::error_code resume_cycle_staging_empty_ec;
        require(resume_cycle_run.ok &&
                resume_cycle_result.initial_action_plan_loaded &&
                resume_cycle_result.transfer_executor_ran &&
                resume_cycle_result.materialize_executor_ran &&
                resume_cycle_result.cleanup_executor_ran &&
                resume_cycle_result.final_action_plan_loaded &&
                resume_cycle_result.transaction_sequence_completed &&
                resume_cycle_result.final_converged &&
                resume_cycle_result.final_destination_filesystem_verified &&
                resume_cycle_result.final_staging_artifacts_verified &&
                resume_cycle_result.files_considered == fake_session_result.files_materialized &&
                resume_cycle_result.transfer_files_executed == 1 &&
                resume_cycle_result.transfer_chunks_written == pending_materialize_entry->chunks.size() &&
                resume_cycle_result.transfer_receipt_rows_upserted == pending_materialize_entry->chunks.size() &&
                resume_cycle_result.transfer_workorder_rows_claimed == pending_materialize_entry->chunks.size() &&
                resume_cycle_result.transfer_workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                resume_cycle_result.files_materialized == 1 &&
                resume_cycle_result.files_cleaned == 1 &&
                resume_cycle_result.receipt_rows_cleaned == pending_materialize_entry->chunks.size() &&
                resume_cycle_result.final_already_converged_files == fake_session_result.files_materialized &&
                resume_cycle_result.final_remaining_action_files == 0 &&
                read_binary_fixture(fake_destination_root / "docs/session-report.txt") == fake_session_report &&
                fs::is_empty(fake_staging_root, resume_cycle_staging_empty_ec) && !resume_cycle_staging_empty_ec,
                "sync session checkpoint resume cycle executor drains transfer, materialization, and cleanup branches to strict convergence");
        write_binary_fixture(fake_destination_root / "docs/session-report.txt", "drifted after checkpoint");
        SyncSessionCheckpointResumeViewResult drifted_destination_resume_view;
        require(!load_sync_session_checkpoint_resume_view(resume_options, drifted_destination_resume_view).ok,
                "sync session checkpoint resume filesystem probe rejects destination content drift after durable terminal checkpoint");
        SyncSessionCheckpointResumeViewOptions advisory_filesystem_resume = resume_options;
        advisory_filesystem_resume.require_destination_filesystem_match = false;
        SyncSessionCheckpointResumeViewResult advisory_filesystem_resume_view;
        SyncValidationResult advisory_filesystem_resume_run = load_sync_session_checkpoint_resume_view(advisory_filesystem_resume, advisory_filesystem_resume_view);
        require(advisory_filesystem_resume_run.ok &&
                !advisory_filesystem_resume_view.destination_filesystem_verified &&
                advisory_filesystem_resume_view.destination_filesystem_content_mismatches == 1 &&
                advisory_filesystem_resume_view.destination_filesystem_missing_paths == 0 &&
                !advisory_filesystem_resume_view.destination_filesystem_drift_paths.empty() &&
                advisory_filesystem_resume_view.destination_filesystem_drift_paths[0].value == "docs/session-report.txt",
                "sync session checkpoint resume filesystem probe exposes advisory drift evidence when strict filesystem matching is disabled");
        write_binary_fixture(fake_destination_root / "docs/session-report.txt", fake_session_report);
        write_binary_fixture(fake_source_root / "docs/session-report.txt", "source drifted after checkpoint");
        SyncSessionCheckpointResumeViewResult drifted_source_resume_view;
        require(!load_sync_session_checkpoint_resume_view(resume_options, drifted_source_resume_view).ok,
                "sync session checkpoint resume source filesystem probe rejects source content drift after durable terminal checkpoint");
        SyncSessionCheckpointResumeViewOptions advisory_source_filesystem_resume = resume_options;
        advisory_source_filesystem_resume.require_source_filesystem_match = false;
        SyncSessionCheckpointResumeViewResult advisory_source_filesystem_resume_view;
        SyncValidationResult advisory_source_filesystem_resume_run = load_sync_session_checkpoint_resume_view(advisory_source_filesystem_resume, advisory_source_filesystem_resume_view);
        require(advisory_source_filesystem_resume_run.ok &&
                !advisory_source_filesystem_resume_view.source_filesystem_verified &&
                advisory_source_filesystem_resume_view.source_filesystem_content_mismatches == 1 &&
                advisory_source_filesystem_resume_view.source_filesystem_missing_paths == 0 &&
                !advisory_source_filesystem_resume_view.source_filesystem_drift_paths.empty() &&
                advisory_source_filesystem_resume_view.source_filesystem_drift_paths[0].value == "docs/session-report.txt",
                "sync session checkpoint resume source filesystem probe exposes advisory drift evidence when strict source matching is disabled");
        write_binary_fixture(fake_source_root / "docs/session-report.txt", fake_session_report);
        const NormalizedSyncPath stale_staging_probe_path{"docs/session-report.txt"};
        const SyncManifestEntry* stale_staging_probe_entry = find_manifest_entry_by_path(fake_session_result.source_manifest, stale_staging_probe_path);
        require(stale_staging_probe_entry != nullptr,
                "sync session checkpoint resume staging cleanup probe fixture has source manifest entry");
        NormalizedSyncPath stale_staging_relative;
        stale_staging_relative.value = sync_domain_test_access::remote_staging_relative_path_for_fixture(
            stale_staging_probe_entry->path,
            sync_manifest_entry_digest(*stale_staging_probe_entry),
            "sync session checkpoint resume staging cleanup selftest");
        NormalizedSyncPath stale_receipt_dir_relative;
        stale_receipt_dir_relative.value = stale_staging_relative.value + ".chunks";
        const fs::path stale_receipt_dir = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
            fake_staging_root,
            stale_receipt_dir_relative,
            "sync session checkpoint resume stale receipt directory"));
        const SyncLocalApplyPlanEntry* stale_staging_probe_apply = find_apply_entry_by_path(fake_session_result.apply_plan, stale_staging_probe_path);
        require(stale_staging_probe_apply != nullptr,
                "sync session checkpoint staging repair fixture has apply intent evidence");
        const fs::path stale_staging_path = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
            fake_staging_root,
            stale_staging_relative,
            "sync session checkpoint staging repair stale staged file"));
        write_binary_fixture(stale_staging_path, fake_session_report);
        fs::create_directories(stale_receipt_dir, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not create stale receipt directory fixture: " + apply_cleanup_ec.message());
        for (const auto& chunk : stale_staging_probe_entry->chunks) {
            const NormalizedSyncPath receipt_relative{sync_domain_test_access::chunk_receipt_relative_path_for_fixture(
                stale_staging_probe_entry->path,
                sync_manifest_entry_digest(*stale_staging_probe_entry),
                chunk,
                "sync session checkpoint staging repair selftest receipt")};
            const fs::path receipt_path = fs::path(sync_domain_test_access::resolve_normalized_relative_under_root_for_fixture(
                fake_staging_root,
                receipt_relative,
                "sync session checkpoint staging repair selftest receipt path"));
            write_binary_fixture(receipt_path, sync_domain_test_access::chunk_receipt_material_for_fixture(*stale_staging_probe_entry, *stale_staging_probe_apply, chunk));
        }
        SyncSessionCheckpointResumeViewResult stale_staging_resume_view;
        require(!load_sync_session_checkpoint_resume_view(resume_options, stale_staging_resume_view).ok,
                "sync session checkpoint resume staging cleanup probe rejects stale committed receipt directories and staged files");
        SyncSessionCheckpointResumeViewOptions advisory_staging_resume = resume_options;
        advisory_staging_resume.require_staging_artifacts_cleaned = false;
        SyncSessionCheckpointResumeViewResult advisory_staging_resume_view;
        SyncValidationResult advisory_staging_resume_run = load_sync_session_checkpoint_resume_view(advisory_staging_resume, advisory_staging_resume_view);
        require(advisory_staging_resume_run.ok &&
                !advisory_staging_resume_view.staging_artifacts_verified &&
                advisory_staging_resume_view.staging_artifact_paths_checked == fake_session_result.files_materialized &&
                advisory_staging_resume_view.staging_files_present == 1 &&
                advisory_staging_resume_view.staging_receipt_directories_present == 1 &&
                advisory_staging_resume_view.staging_artifact_kind_mismatches == 0 &&
                advisory_staging_resume_view.staging_artifact_paths.size() == 2,
                "sync session checkpoint resume staging cleanup probe exposes advisory stale staged-file and receipt-directory evidence");
        SyncSessionCheckpointResumeActionPlanResult stale_staging_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, stale_staging_action_plan).ok &&
                stale_staging_action_plan.repair_committed_staging_files == 1 &&
                stale_staging_action_plan.already_converged_files == 1 &&
                stale_staging_action_plan.quarantine_staging_files == 0 &&
                stale_staging_action_plan.receipt_content_mismatches == 0 &&
                stale_staging_action_plan.unexpected_receipt_artifacts == 0,
                "sync session checkpoint resume action plan classifies DB-bound stale terminal artifacts as repair-committed-staging");
        SyncSessionCheckpointStagingRepairOptions staging_repair_options;
        staging_repair_options.sqlite_path = fake_session_checkpoint_db.string();
        staging_repair_options.session_id = "session-main";
        staging_repair_options.source_root_path = fake_source_root.string();
        staging_repair_options.destination_root_path = fake_destination_root.string();
        staging_repair_options.staging_root_path = fake_staging_root.string();
        staging_repair_options.expected_folder_id = "folder-alpha";
        staging_repair_options.expected_source_device_id = "device-bravo";
        staging_repair_options.expected_destination_device_id = "device-alpha";
        staging_repair_options.expected_peer_id = "peer-bravo";
        SyncSessionCheckpointStagingRepairResult staging_repair;
        SyncValidationResult staging_repair_run = repair_sync_session_checkpoint_staging_artifacts(staging_repair_options, staging_repair);
        require(staging_repair_run.ok &&
                staging_repair.resume_view_loaded &&
                staging_repair.terminal_session_complete &&
                staging_repair.durable_integrity_verified &&
                staging_repair.destination_filesystem_verified &&
                !staging_repair.pre_repair_staging_artifacts_clean &&
                staging_repair.post_repair_staging_artifacts_clean &&
                staging_repair.repair_performed &&
                staging_repair.files_considered == fake_session_result.files_materialized &&
                staging_repair.files_repaired == 1 &&
                staging_repair.staged_files_removed == 1 &&
                staging_repair.receipt_files_removed == stale_staging_probe_entry->chunks.size() &&
                staging_repair.receipt_directories_removed == 1 &&
                staging_repair.unsafe_artifacts_detected == 0 &&
                staging_repair.staging_file_content_mismatches == 0 &&
                staging_repair.receipt_content_mismatches == 0 &&
                staging_repair.unexpected_receipt_artifacts == 0 &&
                !fs::exists(stale_staging_path) &&
                !fs::exists(stale_receipt_dir),
                "sync session checkpoint staging repair removes only DB-bound committed stale artifacts after terminal destination proof");
        SyncSessionCheckpointResumeViewResult repaired_staging_resume_view;
        require(load_sync_session_checkpoint_resume_view(resume_options, repaired_staging_resume_view).ok &&
                repaired_staging_resume_view.staging_artifacts_verified,
                "sync session checkpoint staging repair restores strict resume staging cleanliness");
        write_binary_fixture(stale_staging_path, "tampered stale staged bytes");
        SyncSessionCheckpointStagingRepairResult tampered_staging_repair;
        SyncSessionCheckpointResumeActionPlanResult tampered_staging_action_plan;
        require(plan_sync_session_checkpoint_resume_actions(action_plan_options, tampered_staging_action_plan).ok &&
                tampered_staging_action_plan.quarantine_staging_files == 1 &&
                tampered_staging_action_plan.staged_file_content_mismatches == 1 &&
                tampered_staging_action_plan.repair_committed_staging_files == 0,
                "sync session checkpoint resume action plan quarantines tampered terminal staged artifacts instead of repairing them");
        require(!repair_sync_session_checkpoint_staging_artifacts(staging_repair_options, tampered_staging_repair).ok &&
                tampered_staging_repair.staging_file_content_mismatches == 1 &&
                fs::exists(stale_staging_path),
                "sync session checkpoint staging repair fail-closes on stale staged files that do not match checkpoint content");
        fs::remove(stale_staging_path, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not remove tampered stale staged fixture: " + apply_cleanup_ec.message());
        SyncSessionCheckpointResumeViewOptions mismatched_resume = resume_options;
        mismatched_resume.expected_destination_device_id = "device-wrong";
        SyncSessionCheckpointResumeViewResult mismatched_resume_view;
        require(!load_sync_session_checkpoint_resume_view(mismatched_resume, mismatched_resume_view).ok,
                "sync session checkpoint resume view rejects mismatched destination device identity");
        SyncSessionCheckpointResumeViewOptions inside_root_resume = resume_options;
        inside_root_resume.sqlite_path = (fake_destination_root / "bad-resume-view.sqlite").string();
        write_binary_fixture(fake_destination_root / "bad-resume-view.sqlite", "not a checkpoint db");
        SyncSessionCheckpointResumeViewResult inside_root_resume_view;
        require(!load_sync_session_checkpoint_resume_view(inside_root_resume, inside_root_resume_view).ok,
                "sync session checkpoint resume view rejects database paths inside synchronized roots before opening sqlite");
        SyncSessionCheckpointOptions checkpoint_inside_synced_root = checkpoint_options;
        checkpoint_inside_synced_root.sqlite_path = (fake_destination_root / "bad-session-checkpoint.sqlite").string();
        SyncSessionCheckpointResult rejected_checkpoint_result;
        require(!persist_sync_fake_peer_session_checkpoint(fake_session_options,
                                                           fake_session_result,
                                                           checkpoint_inside_synced_root,
                                                           rejected_checkpoint_result).ok,
                "sync session checkpoint rejects metadata database paths inside synchronized roots");
        {
            SyncSqliteDb corrupt_handle;
            int corrupt_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            corrupt_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), corrupt_handle.db.out(), corrupt_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(corrupt_handle.db, "could not reopen checkpoint db for receipt coverage corruption test"));
            }
            sqlite_exec_or_throw(corrupt_handle.db,
                                 "UPDATE sync_session_chunk_receipts SET chunk_sha256='0000000000000000000000000000000000000000000000000000000000000000' "
                                 "WHERE rowid=(SELECT rowid FROM sync_session_chunk_receipts WHERE session_id='session-main' ORDER BY path, chunk_offset LIMIT 1);",
                                 "could not corrupt checkpoint receipt hash for exact coverage test");
        }
        SyncSessionCheckpointResumeViewResult corrupt_receipt_resume_view;
        require(!load_sync_session_checkpoint_resume_view(resume_options, corrupt_receipt_resume_view).ok,
                "sync session checkpoint resume chunk coverage guard rejects receipts that no longer match persisted source manifest chunks");
        SyncSessionCheckpointResult restored_checkpoint_result;
        SyncValidationResult restored_checkpoint_run = persist_sync_fake_peer_session_checkpoint(fake_session_options,
                                                                                                 fake_session_result,
                                                                                                 checkpoint_options,
                                                                                                 restored_checkpoint_result);
        require(restored_checkpoint_run.ok && restored_checkpoint_result.checkpoint_reloaded &&
                restored_checkpoint_result.source_manifest_chunks_written == fake_source_chunk_count &&
                restored_checkpoint_result.chunk_receipts_recorded == fake_source_chunk_count,
                "sync session checkpoint reset restores exact manifest chunk coverage after receipt corruption");
        {
            SyncSqliteDb corrupt_handle;
            int corrupt_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            corrupt_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(fake_session_checkpoint_db.string().c_str(), corrupt_handle.db.out(), corrupt_flags, nullptr) != SQLITE_OK) {
                throw std::runtime_error(sqlite_error_message(corrupt_handle.db, "could not reopen checkpoint db for resume integrity corruption test"));
            }
            sqlite_exec_or_throw(corrupt_handle.db,
                                 "UPDATE sync_session_manifests SET entry_count = entry_count + 1 WHERE session_id='session-main' AND role='source';",
                                 "could not corrupt source manifest entry count for resume integrity test");
        }
        SyncSessionCheckpointResumeViewResult corrupt_resume_view;
        require(!load_sync_session_checkpoint_resume_view(resume_options, corrupt_resume_view).ok,
                "sync session checkpoint resume integrity guard rejects mismatched manifest entry-count rows");
        SyncFakePeerFileFetchSessionOptions overlapping_fake_session = fake_session_options;
        overlapping_fake_session.staging_root_path = fake_destination_root.string();
        SyncFakePeerFileFetchSessionResult overlapping_fake_session_result;
        require(!run_sync_fake_peer_file_fetch_session(overlapping_fake_session, overlapping_fake_session_result).ok,
                "fake peer file-fetch session rejects overlapping staging roots before scan or transfer mutation");

        const std::string materialized_body = "hello from device bravo\n";
        SyncManifestEntry materialized_remote = remote_file_entry_for_body("docs/materialized.txt", materialized_body, 4);
        SyncManifestDiffPlan materialize_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 12, {materialized_remote}), materialize_diff_plan).ok,
                "manifest diff plans a real remote-only file for materialization");
        SyncLocalApplyPlan materialize_apply_plan;
        require(build_sync_local_apply_plan(materialize_diff_plan, apply_options, materialize_apply_plan).ok &&
                materialize_apply_plan.entries.size() == 1 &&
                materialize_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan emits a stage action for materialization");
        fs::create_directories(apply_staging_root, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not create materialization staging root: " + apply_cleanup_ec.message());
        write_binary_fixture(materialize_apply_plan.entries[0].absolute_staging_path, materialized_body);
        SyncStagedFileMaterializationOptions materialize_options;
        materialize_options.local_root_path = apply_root.string();
        materialize_options.staging_root_path = apply_staging_root.string();
        SyncStagedFileMaterializationResult materialize_result;
        SyncValidationResult materialize_ok = materialize_staged_sync_file(materialized_remote, materialize_apply_plan.entries[0], materialize_options, materialize_result);
        require(materialize_ok.ok && materialize_result.materialized &&
                materialize_result.path.value == "docs/materialized.txt" &&
                materialize_result.content_sha256 == sha256_hex(materialized_body) &&
                materialize_result.chunks_verified == materialized_remote.chunks.size() &&
                materialize_result.idempotency_key.rfind("sync-materialize:v1:", 0) == 0,
                "staged file materialization verifies chunks/content and emits commit evidence");
        require(read_binary_fixture(materialize_result.absolute_target_path) == materialized_body &&
                !fs::exists(fs::path(materialize_result.absolute_staging_path)) &&
                materialize_result.preflight_checked_target &&
                !materialize_result.replaced_existing_target,
                "staged file materialization atomically moves verified content into the sync folder");

        SyncChunkReceiptWriteOptions chunk_write_options;
        chunk_write_options.local_root_path = apply_root.string();
        chunk_write_options.staging_root_path = apply_staging_root.string();

        const std::string chunked_body = "abcdeFGHIJklmno";
        SyncManifestEntry chunked_remote = remote_file_entry_for_body("docs/chunked.txt", chunked_body, 27);
        SyncManifestDiffPlan chunked_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 27, {chunked_remote}), chunked_diff_plan).ok,
                "manifest diff plans chunk receipt fixture");
        SyncLocalApplyPlan chunked_apply_plan;
        require(build_sync_local_apply_plan(chunked_diff_plan, apply_options, chunked_apply_plan).ok &&
                chunked_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan emits staged path for chunk receipt fixture");

        SyncStagedFileMaterializationOptions receipt_gated_materialize_options = materialize_options;
        receipt_gated_materialize_options.require_chunk_receipts = true;
        SyncManifestEntry no_receipt_remote = remote_file_entry_for_body("docs/no-receipt.txt", "complete but unreceipted", 31);
        SyncManifestDiffPlan no_receipt_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 31, {no_receipt_remote}), no_receipt_diff_plan).ok,
                "manifest diff plans receipt-gated missing-receipt fixture");
        SyncLocalApplyPlan no_receipt_apply_plan;
        require(build_sync_local_apply_plan(no_receipt_diff_plan, apply_options, no_receipt_apply_plan).ok,
                "local apply plan emits missing-receipt fixture");
        write_binary_fixture(no_receipt_apply_plan.entries[0].absolute_staging_path, "complete but unreceipted");
        SyncStagedFileMaterializationResult no_receipt_materialize_result;
        require(!materialize_staged_sync_file(no_receipt_remote,
                                             no_receipt_apply_plan.entries[0],
                                             receipt_gated_materialize_options,
                                             no_receipt_materialize_result).ok &&
                fs::exists(fs::path(no_receipt_apply_plan.entries[0].absolute_staging_path)) &&
                !fs::exists(fs::path(no_receipt_apply_plan.entries[0].absolute_target_path)),
                "receipt-gated staged file materialization rejects complete staged bytes without chunk receipts");

        SyncChunkReceiptWriteResult middle_chunk_result;
        require(write_sync_staged_chunk(chunked_remote,
                                       chunked_apply_plan.entries[0],
                                       chunked_remote.chunks[1],
                                       chunk_bytes_for_body(chunked_body, chunked_remote.chunks[1]),
                                       chunk_write_options,
                                       middle_chunk_result).ok &&
                middle_chunk_result.chunk_written &&
                !middle_chunk_result.reused_existing_receipt &&
                !middle_chunk_result.staged_file_complete &&
                middle_chunk_result.idempotency_key.rfind("sync-chunk-receipt:v1:", 0) == 0 &&
                fs::exists(fs::path(middle_chunk_result.absolute_receipt_path)) &&
                fs::exists(fs::path(middle_chunk_result.absolute_staging_path)) &&
                !fs::exists(fs::path(chunked_apply_plan.entries[0].absolute_target_path)),
                "staged chunk write records a receipt without committing an incomplete remote file");

        SyncStagedTransferInspectionOptions inspection_options;
        inspection_options.local_root_path = apply_root.string();
        inspection_options.staging_root_path = apply_staging_root.string();
        SyncStagedTransferInspectionResult partial_inspection;
        require(inspect_sync_staged_transfer(chunked_remote,
                                            chunked_apply_plan.entries[0],
                                            inspection_options,
                                            partial_inspection).ok &&
                partial_inspection.chunk_receipts_checked &&
                partial_inspection.staged_file_exists &&
                !partial_inspection.staged_file_complete &&
                partial_inspection.total_chunks == chunked_remote.chunks.size() &&
                partial_inspection.receipts_verified == 1 &&
                partial_inspection.missing_chunks.size() == 2 &&
                partial_inspection.missing_chunks[0].offset == chunked_remote.chunks[0].offset &&
                partial_inspection.missing_chunks[1].offset == chunked_remote.chunks[2].offset &&
                partial_inspection.idempotency_key.rfind("sync-transfer-inspect:v1:", 0) == 0,
                "staged transfer inspection reports reusable receipts and exact missing chunks for resume");

        SyncChunkRequestPlanOptions request_one_chunk;
        request_one_chunk.max_chunks_per_request = 1;
        SyncChunkRequestPlanResult one_chunk_request_plan;
        require(build_sync_chunk_request_plan(chunked_remote,
                                             chunked_apply_plan.entries[0],
                                             partial_inspection,
                                             request_one_chunk,
                                             one_chunk_request_plan).ok &&
                one_chunk_request_plan.idempotency_key.rfind("sync-chunk-request:v1:", 0) == 0 &&
                one_chunk_request_plan.total_missing_chunks == 2 &&
                one_chunk_request_plan.selected_chunks == 1 &&
                one_chunk_request_plan.selected_bytes == chunked_remote.chunks[0].length &&
                one_chunk_request_plan.more_chunks_available &&
                one_chunk_request_plan.chunks_to_request.size() == 1 &&
                same_chunk_range(one_chunk_request_plan.chunks_to_request[0], chunked_remote.chunks[0]),
                "chunk request plan turns verified partial inspection into a bounded missing-chunk request batch");

        SyncChunkRequestPlanResult tampered_accept_plan = one_chunk_request_plan;
        tampered_accept_plan.selected_bytes += 1;
        SyncRequestedChunkAcceptanceResult tampered_accept_result;
        require(!accept_sync_requested_chunk(chunked_remote,
                                            chunked_apply_plan.entries[0],
                                            partial_inspection,
                                            request_one_chunk,
                                            tampered_accept_plan,
                                            chunked_remote.chunks[0],
                                            chunk_bytes_for_body(chunked_body, chunked_remote.chunks[0]),
                                            chunk_write_options,
                                            tampered_accept_result).ok,
                "requested chunk acceptance rejects caller-mutated request plan evidence");

        SyncRequestedChunkAcceptanceResult unrequested_accept_result;
        require(!accept_sync_requested_chunk(chunked_remote,
                                            chunked_apply_plan.entries[0],
                                            partial_inspection,
                                            request_one_chunk,
                                            one_chunk_request_plan,
                                            chunked_remote.chunks[2],
                                            chunk_bytes_for_body(chunked_body, chunked_remote.chunks[2]),
                                            chunk_write_options,
                                            unrequested_accept_result).ok,
                "requested chunk acceptance rejects peer bytes for chunks outside the selected request batch");

        SyncChunkResponseEnvelope unrequested_response_envelope;
        require(!build_sync_chunk_response_envelope(chunked_remote,
                                                   chunked_apply_plan.entries[0],
                                                   one_chunk_request_plan,
                                                   chunked_remote.chunks[2],
                                                   unrequested_response_envelope).ok,
                "chunk response envelope builder rejects chunks outside the selected request batch");

        SyncChunkResponseEnvelope first_response_envelope;
        require(build_sync_chunk_response_envelope(chunked_remote,
                                                  chunked_apply_plan.entries[0],
                                                  one_chunk_request_plan,
                                                  chunked_remote.chunks[0],
                                                  first_response_envelope).ok &&
                first_response_envelope.request_idempotency_key == one_chunk_request_plan.idempotency_key &&
                first_response_envelope.response_idempotency_key.rfind("sync-chunk-response:v1:", 0) == 0 &&
                first_response_envelope.remote_entry_digest == sync_manifest_entry_digest(chunked_remote) &&
                first_response_envelope.remote_version_digest == sync_manifest_entry_version_digest(chunked_remote) &&
                first_response_envelope.apply_entry_idempotency_key == chunked_apply_plan.entries[0].idempotency_key &&
                first_response_envelope.offset == chunked_remote.chunks[0].offset &&
                first_response_envelope.length == chunked_remote.chunks[0].length &&
                first_response_envelope.chunk_sha256 == chunked_remote.chunks[0].sha256,
                "chunk response envelope binds peer bytes to request, remote entry, apply intent, and chunk range evidence");

        SyncChunkResponseEnvelope stale_response_envelope = first_response_envelope;
        stale_response_envelope.request_idempotency_key = "sync-chunk-request:v1:" + std::string(64, '0');
        SyncRequestedChunkAcceptanceResult stale_response_result;
        require(!accept_sync_chunk_response_envelope(chunked_remote,
                                                    chunked_apply_plan.entries[0],
                                                    partial_inspection,
                                                    request_one_chunk,
                                                    one_chunk_request_plan,
                                                    stale_response_envelope,
                                                    chunk_bytes_for_body(chunked_body, chunked_remote.chunks[0]),
                                                    chunk_write_options,
                                                    stale_response_result).ok,
                "chunk response envelope acceptance rejects stale request ids before writing peer bytes");

        SyncChunkResponseEnvelope tampered_response_envelope = first_response_envelope;
        tampered_response_envelope.response_idempotency_key = "sync-chunk-response:v1:" + std::string(64, '1');
        SyncRequestedChunkAcceptanceResult tampered_response_result;
        require(!accept_sync_chunk_response_envelope(chunked_remote,
                                                    chunked_apply_plan.entries[0],
                                                    partial_inspection,
                                                    request_one_chunk,
                                                    one_chunk_request_plan,
                                                    tampered_response_envelope,
                                                    chunk_bytes_for_body(chunked_body, chunked_remote.chunks[0]),
                                                    chunk_write_options,
                                                    tampered_response_result).ok,
                "chunk response envelope acceptance rejects forged response ids before writing peer bytes");

        SyncRequestedChunkAcceptanceResult accepted_request_chunk;
        require(accept_sync_chunk_response_envelope(chunked_remote,
                                                   chunked_apply_plan.entries[0],
                                                   partial_inspection,
                                                   request_one_chunk,
                                                   one_chunk_request_plan,
                                                   first_response_envelope,
                                                   chunk_bytes_for_body(chunked_body, chunked_remote.chunks[0]),
                                                   chunk_write_options,
                                                   accepted_request_chunk).ok &&
                accepted_request_chunk.request_evidence_checked &&
                accepted_request_chunk.response_envelope_checked &&
                accepted_request_chunk.chunk_written &&
                !accepted_request_chunk.reused_existing_receipt &&
                !accepted_request_chunk.staged_file_complete &&
                accepted_request_chunk.request_idempotency_key == one_chunk_request_plan.idempotency_key &&
                accepted_request_chunk.response_idempotency_key == first_response_envelope.response_idempotency_key &&
                accepted_request_chunk.receipt_idempotency_key.rfind("sync-chunk-receipt:v1:", 0) == 0 &&
                accepted_request_chunk.offset == chunked_remote.chunks[0].offset &&
                accepted_request_chunk.length == chunked_remote.chunks[0].length &&
                accepted_request_chunk.chunk_sha256 == chunked_remote.chunks[0].sha256,
                "chunk response envelope acceptance binds peer chunk bytes to verified request and response evidence before writing");

        const std::string batch_body = "uvwxyABCDE67890";
        SyncManifestEntry batch_remote = remote_file_entry_for_body("docs/batch.txt", batch_body, 33);
        SyncManifestDiffPlan batch_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 33, {batch_remote}), batch_diff_plan).ok,
                "manifest diff plans chunk response batch fixture");
        SyncLocalApplyPlan batch_apply_plan;
        require(build_sync_local_apply_plan(batch_diff_plan, apply_options, batch_apply_plan).ok &&
                batch_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan emits chunk response batch fixture");
        SyncChunkReceiptWriteResult batch_middle_chunk;
        require(write_sync_staged_chunk(batch_remote,
                                       batch_apply_plan.entries[0],
                                       batch_remote.chunks[1],
                                       chunk_bytes_for_body(batch_body, batch_remote.chunks[1]),
                                       chunk_write_options,
                                       batch_middle_chunk).ok &&
                batch_middle_chunk.chunk_written &&
                !batch_middle_chunk.staged_file_complete,
                "chunk response batch fixture starts with one reusable middle receipt");
        SyncStagedTransferInspectionResult batch_partial_inspection;
        require(inspect_sync_staged_transfer(batch_remote,
                                            batch_apply_plan.entries[0],
                                            inspection_options,
                                            batch_partial_inspection).ok &&
                batch_partial_inspection.receipts_verified == 1 &&
                batch_partial_inspection.missing_chunks.size() == 2,
                "chunk response batch fixture inspection exposes two missing chunks");
        SyncChunkRequestPlanResult batch_request_plan;
        require(build_sync_chunk_request_plan(batch_remote,
                                             batch_apply_plan.entries[0],
                                             batch_partial_inspection,
                                             SyncChunkRequestPlanOptions{},
                                             batch_request_plan).ok &&
                batch_request_plan.selected_chunks == 2 &&
                !batch_request_plan.more_chunks_available,
                "chunk response batch fixture requests all remaining chunks in one batch");

        SyncChunkResponseBatchEnvelope duplicate_batch_envelope;
        require(!build_sync_chunk_response_batch_envelope(batch_remote,
                                                         batch_apply_plan.entries[0],
                                                         batch_request_plan,
                                                         {batch_remote.chunks[0], batch_remote.chunks[0]},
                                                         duplicate_batch_envelope).ok,
                "chunk response batch envelope rejects duplicate response chunks before writes");

        SyncChunkResponseBatchEnvelope batch_response_envelope;
        require(build_sync_chunk_response_batch_envelope(batch_remote,
                                                        batch_apply_plan.entries[0],
                                                        batch_request_plan,
                                                        {batch_remote.chunks[0], batch_remote.chunks[2]},
                                                        batch_response_envelope).ok &&
                batch_response_envelope.request_idempotency_key == batch_request_plan.idempotency_key &&
                batch_response_envelope.batch_idempotency_key.rfind("sync-chunk-response-batch:v1:", 0) == 0 &&
                batch_response_envelope.response_count == 2 &&
                batch_response_envelope.responses.size() == 2 &&
                batch_response_envelope.total_bytes == batch_remote.chunks[0].length + batch_remote.chunks[2].length,
                "chunk response batch envelope binds an ordered partial peer response set to the request batch");

        SyncChunkResponseBatchEnvelope forged_batch_envelope = batch_response_envelope;
        forged_batch_envelope.batch_idempotency_key = "sync-chunk-response-batch:v1:" + std::string(64, '2');
        SyncChunkResponseBatchAcceptanceResult forged_batch_result;
        require(!accept_sync_chunk_response_batch_envelope(batch_remote,
                                                          batch_apply_plan.entries[0],
                                                          batch_partial_inspection,
                                                          SyncChunkRequestPlanOptions{},
                                                          batch_request_plan,
                                                          forged_batch_envelope,
                                                          {chunk_bytes_for_body(batch_body, batch_remote.chunks[0]),
                                                           chunk_bytes_for_body(batch_body, batch_remote.chunks[2])},
                                                          chunk_write_options,
                                                          forged_batch_result).ok,
                "chunk response batch acceptance rejects forged batch ids before staging peer bytes");

        SyncChunkResponseBatchAcceptanceResult accepted_batch_result;
        require(accept_sync_chunk_response_batch_envelope(batch_remote,
                                                         batch_apply_plan.entries[0],
                                                         batch_partial_inspection,
                                                         SyncChunkRequestPlanOptions{},
                                                         batch_request_plan,
                                                         batch_response_envelope,
                                                         {chunk_bytes_for_body(batch_body, batch_remote.chunks[0]),
                                                          chunk_bytes_for_body(batch_body, batch_remote.chunks[2])},
                                                         chunk_write_options,
                                                         accepted_batch_result).ok &&
                accepted_batch_result.request_evidence_checked &&
                accepted_batch_result.batch_envelope_checked &&
                accepted_batch_result.response_count == 2 &&
                accepted_batch_result.chunks_written == 2 &&
                accepted_batch_result.receipts_reused == 0 &&
                accepted_batch_result.staged_file_complete &&
                accepted_batch_result.chunks_verified == batch_remote.chunks.size() &&
                accepted_batch_result.content_sha256 == sha256_hex(batch_body) &&
                accepted_batch_result.accepted_chunks.size() == 2 &&
                accepted_batch_result.accepted_chunks[0].response_envelope_checked &&
                accepted_batch_result.accepted_chunks[1].response_envelope_checked,
                "chunk response batch acceptance preflights the batch envelope and writes all selected peer chunks through receipt-backed acceptance");

        const std::string round_body = "0123456789abcdefghij";
        SyncManifestEntry round_remote = remote_file_entry_for_body("docs/round.txt", round_body, 34);
        SyncManifestDiffPlan round_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 34, {round_remote}), round_diff_plan).ok,
                "manifest diff plans chunk transfer round fixture");
        SyncLocalApplyPlan round_apply_plan;
        require(build_sync_local_apply_plan(round_diff_plan, apply_options, round_apply_plan).ok &&
                round_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan emits chunk transfer round fixture");
        SyncStagedTransferInspectionResult round_initial_inspection;
        require(inspect_sync_staged_transfer(round_remote,
                                            round_apply_plan.entries[0],
                                            inspection_options,
                                            round_initial_inspection).ok &&
                round_initial_inspection.missing_chunks.size() == round_remote.chunks.size() &&
                !round_initial_inspection.staged_file_complete,
                "chunk transfer round fixture starts with every chunk missing");
        SyncChunkRequestPlanOptions round_request_options;
        round_request_options.max_chunks_per_request = 2;
        SyncChunkRequestPlanResult round_first_request;
        require(build_sync_chunk_request_plan(round_remote,
                                             round_apply_plan.entries[0],
                                             round_initial_inspection,
                                             round_request_options,
                                             round_first_request).ok &&
                round_first_request.selected_chunks == 2 &&
                round_first_request.more_chunks_available,
                "chunk transfer round plans a bounded first request batch");
        SyncPeerChunkAvailability peer_bravo;
        peer_bravo.peer_id = "peer-bravo";
        peer_bravo.peer_session_id = "session-two";
        peer_bravo.available_chunks = {round_remote.chunks[0], round_remote.chunks[1]};
        SyncPeerChunkAvailability peer_alpha;
        peer_alpha.peer_id = "peer-alpha";
        peer_alpha.peer_session_id = "session-one";
        peer_alpha.max_chunks = 1;
        peer_alpha.available_chunks = {round_remote.chunks[0], round_remote.chunks[1]};
        SyncPeerChunkScheduleResult peer_schedule;
        require(build_sync_peer_chunk_schedule(round_remote,
                                               round_apply_plan.entries[0],
                                               round_first_request,
                                               {peer_bravo, peer_alpha},
                                               peer_schedule).ok &&
                peer_schedule.schedule_idempotency_key.rfind("sync-peer-chunk-schedule:v1:", 0) == 0 &&
                peer_schedule.request_idempotency_key == round_first_request.idempotency_key &&
                peer_schedule.peer_count == 2 &&
                peer_schedule.total_request_chunks == 2 &&
                peer_schedule.assigned_chunks == 2 &&
                peer_schedule.request_fully_covered &&
                peer_schedule.unassigned_chunks.empty() &&
                peer_schedule.assignments.size() == 2 &&
                peer_schedule.assignments[0].peer_id == "peer-alpha" &&
                peer_schedule.assignments[0].peer_request_idempotency_key.rfind("sync-peer-chunk-request:v1:", 0) == 0 &&
                peer_schedule.assignments[0].assigned_chunks == 1 &&
                same_chunk_range(peer_schedule.assignments[0].chunks[0], round_remote.chunks[0]) &&
                peer_schedule.assignments[1].peer_id == "peer-bravo" &&
                peer_schedule.assignments[1].assigned_chunks == 1 &&
                same_chunk_range(peer_schedule.assignments[1].chunks[0], round_remote.chunks[1]),
                "peer chunk schedule deterministically assigns a request batch across sorted peer availability");

        SyncPeerChunkScheduleResult partial_peer_schedule;
        require(build_sync_peer_chunk_schedule(round_remote,
                                               round_apply_plan.entries[0],
                                               round_first_request,
                                               {peer_alpha},
                                               partial_peer_schedule).ok &&
                !partial_peer_schedule.request_fully_covered &&
                partial_peer_schedule.assigned_chunks == 1 &&
                partial_peer_schedule.unassigned_chunks.size() == 1 &&
                same_chunk_range(partial_peer_schedule.unassigned_chunks[0], round_remote.chunks[1]),
                "peer chunk schedule reports exact unassigned chunks when peer availability cannot cover the request batch");

        SyncPeerChunkAvailability duplicate_peer_alpha = peer_alpha;
        duplicate_peer_alpha.peer_session_id = "session-three";
        SyncPeerChunkScheduleResult duplicate_peer_schedule;
        require(!build_sync_peer_chunk_schedule(round_remote,
                                                round_apply_plan.entries[0],
                                                round_first_request,
                                                {peer_alpha, duplicate_peer_alpha},
                                                duplicate_peer_schedule).ok,
                "peer chunk schedule rejects duplicate peer ids before producing network work");

        SyncPeerChunkAvailability out_of_request_peer = peer_alpha;
        out_of_request_peer.available_chunks = {round_remote.chunks[2]};
        SyncPeerChunkScheduleResult out_of_request_schedule;
        require(!build_sync_peer_chunk_schedule(round_remote,
                                                round_apply_plan.entries[0],
                                                round_first_request,
                                                {out_of_request_peer},
                                                out_of_request_schedule).ok,
                "peer chunk schedule rejects peer availability outside the selected request batch");

        const std::string peer_bound_body = "ABCDE12345vwxyz";
        SyncManifestEntry peer_bound_remote = remote_file_entry_for_body("docs/peer-bound.txt", peer_bound_body, 35);
        SyncManifestDiffPlan peer_bound_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 35, {peer_bound_remote}), peer_bound_diff_plan).ok,
                "manifest diff plans peer-bound response fixture");
        SyncLocalApplyPlan peer_bound_apply_plan;
        require(build_sync_local_apply_plan(peer_bound_diff_plan, apply_options, peer_bound_apply_plan).ok &&
                peer_bound_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan emits peer-bound response fixture");
        SyncStagedTransferInspectionResult peer_bound_inspection;
        require(inspect_sync_staged_transfer(peer_bound_remote,
                                            peer_bound_apply_plan.entries[0],
                                            inspection_options,
                                            peer_bound_inspection).ok &&
                peer_bound_inspection.missing_chunks.size() == peer_bound_remote.chunks.size(),
                "peer-bound response fixture starts with every chunk missing");
        SyncChunkRequestPlanOptions peer_bound_request_options;
        peer_bound_request_options.max_chunks_per_request = 2;
        SyncChunkRequestPlanResult peer_bound_request;
        require(build_sync_chunk_request_plan(peer_bound_remote,
                                             peer_bound_apply_plan.entries[0],
                                             peer_bound_inspection,
                                             peer_bound_request_options,
                                             peer_bound_request).ok &&
                peer_bound_request.selected_chunks == 2,
                "peer-bound response fixture builds a bounded request");
        SyncPeerChunkAvailability peer_bound_bravo;
        peer_bound_bravo.peer_id = "peer-bravo";
        peer_bound_bravo.peer_session_id = "session-two";
        peer_bound_bravo.available_chunks = {peer_bound_remote.chunks[0], peer_bound_remote.chunks[1]};
        SyncPeerChunkAvailability peer_bound_alpha;
        peer_bound_alpha.peer_id = "peer-alpha";
        peer_bound_alpha.peer_session_id = "session-one";
        peer_bound_alpha.max_chunks = 1;
        peer_bound_alpha.available_chunks = {peer_bound_remote.chunks[0], peer_bound_remote.chunks[1]};
        SyncPeerChunkScheduleResult peer_bound_schedule;
        require(build_sync_peer_chunk_schedule(peer_bound_remote,
                                               peer_bound_apply_plan.entries[0],
                                               peer_bound_request,
                                               {peer_bound_bravo, peer_bound_alpha},
                                               peer_bound_schedule).ok &&
                peer_bound_schedule.assignments.size() == 2 &&
                peer_bound_schedule.assignments[0].peer_id == "peer-alpha" &&
                peer_bound_schedule.assignments[1].peer_id == "peer-bravo",
                "peer-bound response fixture schedules chunks across two deterministic peers");
        SyncPeerChunkResponseBatchEnvelope peer_bound_alpha_batch;
        require(build_sync_peer_chunk_response_batch_envelope(peer_bound_remote,
                                                             peer_bound_apply_plan.entries[0],
                                                             peer_bound_request,
                                                             peer_bound_schedule,
                                                             peer_bound_schedule.assignments[0],
                                                             peer_bound_schedule.assignments[0].chunks,
                                                             peer_bound_alpha_batch).ok &&
                peer_bound_alpha_batch.peer_response_batch_idempotency_key.rfind("sync-peer-chunk-response-batch:v1:", 0) == 0 &&
                peer_bound_alpha_batch.peer_request_idempotency_key == peer_bound_schedule.assignments[0].peer_request_idempotency_key &&
                peer_bound_alpha_batch.schedule_idempotency_key == peer_bound_schedule.schedule_idempotency_key &&
                peer_bound_alpha_batch.response_count == 1,
                "peer-bound response batch envelope binds bytes to one scheduled peer assignment");
        SyncPeerChunkResponseBatchAcceptanceResult peer_bound_alpha_acceptance;
        require(accept_sync_peer_chunk_response_batch_envelope(peer_bound_remote,
                                                              peer_bound_apply_plan.entries[0],
                                                              peer_bound_inspection,
                                                              peer_bound_request_options,
                                                              peer_bound_request,
                                                              peer_bound_schedule,
                                                              peer_bound_schedule.assignments[0],
                                                              peer_bound_alpha_batch,
                                                              {chunk_bytes_for_body(peer_bound_body, peer_bound_schedule.assignments[0].chunks[0])},
                                                              chunk_write_options,
                                                              peer_bound_alpha_acceptance).ok &&
                peer_bound_alpha_acceptance.request_evidence_checked &&
                peer_bound_alpha_acceptance.peer_schedule_checked &&
                peer_bound_alpha_acceptance.peer_assignment_checked &&
                peer_bound_alpha_acceptance.peer_response_envelope_checked &&
                peer_bound_alpha_acceptance.peer_id == "peer-alpha" &&
                peer_bound_alpha_acceptance.chunks_written == 1 &&
                peer_bound_alpha_acceptance.receipts_reused == 0 &&
                !peer_bound_alpha_acceptance.staged_file_complete,
                "peer-bound response acceptance verifies schedule and peer assignment before writing chunk bytes");
        SyncPeerChunkResponseBatchAcceptanceResult cross_peer_acceptance;
        require(!accept_sync_peer_chunk_response_batch_envelope(peer_bound_remote,
                                                               peer_bound_apply_plan.entries[0],
                                                               peer_bound_inspection,
                                                               peer_bound_request_options,
                                                               peer_bound_request,
                                                               peer_bound_schedule,
                                                               peer_bound_schedule.assignments[1],
                                                               peer_bound_alpha_batch,
                                                               {chunk_bytes_for_body(peer_bound_body, peer_bound_schedule.assignments[0].chunks[0])},
                                                               chunk_write_options,
                                                               cross_peer_acceptance).ok,
                "peer-bound response acceptance rejects a batch replayed against another scheduled peer assignment");
        SyncPeerChunkAssignment forged_peer_assignment = peer_bound_schedule.assignments[0];
        forged_peer_assignment.peer_session_id = "session-three";
        SyncPeerChunkResponseBatchEnvelope forged_peer_batch;
        require(!build_sync_peer_chunk_response_batch_envelope(peer_bound_remote,
                                                              peer_bound_apply_plan.entries[0],
                                                              peer_bound_request,
                                                              peer_bound_schedule,
                                                              forged_peer_assignment,
                                                              forged_peer_assignment.chunks,
                                                              forged_peer_batch).ok,
                "peer-bound response envelope builder rejects assignments not present in the verified peer schedule");

        const std::string transport_bound_body = "transport-bound-ABCDE";
        SyncManifestEntry transport_bound_remote = remote_file_entry_for_body("docs/transport-bound.txt", transport_bound_body, 36);
        SyncManifestDiffPlan transport_bound_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 36, {transport_bound_remote}), transport_bound_diff_plan).ok,
                "manifest diff plans peer transport envelope fixture");
        SyncLocalApplyPlan transport_bound_apply_plan;
        require(build_sync_local_apply_plan(transport_bound_diff_plan, apply_options, transport_bound_apply_plan).ok &&
                transport_bound_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan emits peer transport envelope fixture");
        SyncStagedTransferInspectionResult transport_bound_inspection;
        require(inspect_sync_staged_transfer(transport_bound_remote,
                                            transport_bound_apply_plan.entries[0],
                                            inspection_options,
                                            transport_bound_inspection).ok &&
                transport_bound_inspection.missing_chunks.size() == transport_bound_remote.chunks.size(),
                "peer transport envelope fixture starts with every chunk missing");
        SyncChunkRequestPlanOptions transport_bound_request_options;
        transport_bound_request_options.max_chunks_per_request = 1;
        SyncChunkRequestPlanResult transport_bound_request;
        require(build_sync_chunk_request_plan(transport_bound_remote,
                                             transport_bound_apply_plan.entries[0],
                                             transport_bound_inspection,
                                             transport_bound_request_options,
                                             transport_bound_request).ok &&
                transport_bound_request.selected_chunks == 1,
                "peer transport envelope fixture builds a bounded request");
        SyncPeerChunkAvailability transport_bound_peer;
        transport_bound_peer.peer_id = "peer-alpha";
        transport_bound_peer.peer_session_id = "session-one";
        transport_bound_peer.max_chunks = 1;
        transport_bound_peer.max_bytes = 5;
        transport_bound_peer.available_chunks = {transport_bound_remote.chunks[0]};
        SyncPeerChunkScheduleResult transport_bound_schedule;
        require(build_sync_peer_chunk_schedule(transport_bound_remote,
                                               transport_bound_apply_plan.entries[0],
                                               transport_bound_request,
                                               {transport_bound_peer},
                                               transport_bound_schedule).ok &&
                transport_bound_schedule.assignments.size() == 1 &&
                transport_bound_schedule.assignments[0].peer_id == "peer-alpha",
                "peer transport envelope fixture schedules a single bounded peer assignment");
        SyncPeerChunkResponseBatchEnvelope transport_bound_peer_batch;
        require(build_sync_peer_chunk_response_batch_envelope(transport_bound_remote,
                                                             transport_bound_apply_plan.entries[0],
                                                             transport_bound_request,
                                                             transport_bound_schedule,
                                                             transport_bound_schedule.assignments[0],
                                                             transport_bound_schedule.assignments[0].chunks,
                                                             transport_bound_peer_batch).ok &&
                transport_bound_peer_batch.response_count == 1 &&
                transport_bound_peer_batch.total_bytes == transport_bound_schedule.assignments[0].chunks[0].length,
                "peer transport envelope fixture builds a peer-bound response batch");
        SyncPeerTransportEnvelopeBuildOptions transport_build_options;
        transport_build_options.transport_instance_id = "transport-alpha";
        transport_build_options.transport_key_id = "transport-key-alpha";
        transport_build_options.shared_secret = "rev0743-selftest-transport-shared-secret";
        transport_build_options.issued_at_epoch = 100;
        transport_build_options.expires_at_epoch = 140;
        transport_build_options.max_response_count = 1;
        transport_build_options.max_total_bytes = transport_bound_peer_batch.total_bytes;
        transport_build_options.max_chunk_bytes = 5;
        SyncPeerTransportBoundChunkResponseBatchEnvelope transport_bound_envelope;
        require(build_sync_peer_transport_bound_chunk_response_batch_envelope(transport_build_options,
                                                                             transport_bound_peer_batch,
                                                                             transport_bound_envelope).ok &&
                transport_bound_envelope.transport_envelope_idempotency_key.rfind("sync-peer-transport-envelope:v1:", 0) == 0 &&
                transport_bound_envelope.transport_mac_sha256.size() == 64 &&
                transport_bound_envelope.peer_batch_envelope.peer_response_batch_idempotency_key == transport_bound_peer_batch.peer_response_batch_idempotency_key,
                "peer transport envelope builder HMAC-binds bounded peer response batch");
        SyncPeerTransportEnvelopeBuildOptions unbounded_transport_build_options = transport_build_options;
        unbounded_transport_build_options.max_total_bytes = 0;
        SyncPeerTransportBoundChunkResponseBatchEnvelope rejected_unbounded_transport_envelope;
        require(!build_sync_peer_transport_bound_chunk_response_batch_envelope(unbounded_transport_build_options,
                                                                              transport_bound_peer_batch,
                                                                              rejected_unbounded_transport_envelope).ok,
                "peer transport envelope builder refuses unbounded byte envelopes");
        SyncPeerTransportEnvelopeVerifyOptions transport_verify_options;
        transport_verify_options.expected_transport_instance_id = "transport-alpha";
        transport_verify_options.expected_transport_key_id = "transport-key-alpha";
        transport_verify_options.shared_secret = transport_build_options.shared_secret;
        transport_verify_options.expected_peer_id = "peer-alpha";
        transport_verify_options.expected_peer_session_id = "session-one";
        transport_verify_options.verify_now_epoch = 120;
        transport_verify_options.max_response_count = 1;
        transport_verify_options.max_total_bytes = transport_bound_peer_batch.total_bytes;
        transport_verify_options.max_chunk_bytes = 5;
        SyncPeerTransportBoundChunkResponseBatchAcceptanceResult transport_bound_acceptance;
        require(accept_sync_peer_transport_bound_chunk_response_batch_envelope(transport_verify_options,
                                                                              transport_bound_remote,
                                                                              transport_bound_apply_plan.entries[0],
                                                                              transport_bound_inspection,
                                                                              transport_bound_request_options,
                                                                              transport_bound_request,
                                                                              transport_bound_schedule,
                                                                              transport_bound_schedule.assignments[0],
                                                                              transport_bound_envelope,
                                                                              {chunk_bytes_for_body(transport_bound_body, transport_bound_schedule.assignments[0].chunks[0])},
                                                                              chunk_write_options,
                                                                              transport_bound_acceptance).ok &&
                transport_bound_acceptance.transport_envelope_checked &&
                transport_bound_acceptance.transport_mac_checked &&
                transport_bound_acceptance.transport_bounds_checked &&
                transport_bound_acceptance.peer_batch_acceptance_completed &&
                transport_bound_acceptance.peer_batch_acceptance.peer_id == "peer-alpha" &&
                transport_bound_acceptance.chunks_written == 1 &&
                transport_bound_acceptance.bytes_authenticated == transport_bound_peer_batch.total_bytes,
                "peer transport envelope acceptance authenticates bounded peer bytes before staging");
        SyncPeerTransportBoundChunkResponseBatchEnvelope tampered_transport_envelope = transport_bound_envelope;
        tampered_transport_envelope.peer_batch_envelope.total_bytes += 1;
        SyncPeerTransportBoundChunkResponseBatchAcceptanceResult tampered_transport_acceptance;
        require(!accept_sync_peer_transport_bound_chunk_response_batch_envelope(transport_verify_options,
                                                                               transport_bound_remote,
                                                                               transport_bound_apply_plan.entries[0],
                                                                               transport_bound_inspection,
                                                                               transport_bound_request_options,
                                                                               transport_bound_request,
                                                                               transport_bound_schedule,
                                                                               transport_bound_schedule.assignments[0],
                                                                               tampered_transport_envelope,
                                                                               {chunk_bytes_for_body(transport_bound_body, transport_bound_schedule.assignments[0].chunks[0])},
                                                                               chunk_write_options,
                                                                               tampered_transport_acceptance).ok,
                "peer transport envelope rejects tampered peer batch material before staging bytes");
        SyncPeerTransportEnvelopeVerifyOptions expired_transport_verify_options = transport_verify_options;
        expired_transport_verify_options.verify_now_epoch = 141;
        SyncPeerTransportBoundChunkResponseBatchAcceptanceResult expired_transport_acceptance;
        require(!accept_sync_peer_transport_bound_chunk_response_batch_envelope(expired_transport_verify_options,
                                                                               transport_bound_remote,
                                                                               transport_bound_apply_plan.entries[0],
                                                                               transport_bound_inspection,
                                                                               transport_bound_request_options,
                                                                               transport_bound_request,
                                                                               transport_bound_schedule,
                                                                               transport_bound_schedule.assignments[0],
                                                                               transport_bound_envelope,
                                                                               {chunk_bytes_for_body(transport_bound_body, transport_bound_schedule.assignments[0].chunks[0])},
                                                                               chunk_write_options,
                                                                               expired_transport_acceptance).ok,
                "peer transport envelope rejects expired peer response before staging bytes");
        SyncPeerTransportEnvelopeVerifyOptions wrong_secret_transport_verify_options = transport_verify_options;
        wrong_secret_transport_verify_options.shared_secret = "rev0743-selftest-wrong-shared-secret";
        SyncPeerTransportBoundChunkResponseBatchAcceptanceResult wrong_secret_transport_acceptance;
        require(!accept_sync_peer_transport_bound_chunk_response_batch_envelope(wrong_secret_transport_verify_options,
                                                                               transport_bound_remote,
                                                                               transport_bound_apply_plan.entries[0],
                                                                               transport_bound_inspection,
                                                                               transport_bound_request_options,
                                                                               transport_bound_request,
                                                                               transport_bound_schedule,
                                                                               transport_bound_schedule.assignments[0],
                                                                               transport_bound_envelope,
                                                                               {chunk_bytes_for_body(transport_bound_body, transport_bound_schedule.assignments[0].chunks[0])},
                                                                               chunk_write_options,
                                                                               wrong_secret_transport_acceptance).ok,
                "peer transport envelope rejects HMAC signed by another key before staging bytes");

        const std::string ingress_bridge_body = "ingress-bridge-ABCDE";
        SyncManifestEntry ingress_bridge_remote = remote_file_entry_for_body("docs/ingress-bridge.txt", ingress_bridge_body, 37);
        SyncManifestDiffPlan ingress_bridge_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 37, {ingress_bridge_remote}), ingress_bridge_diff_plan).ok,
                "manifest diff plans peer transport ingress bridge fixture");
        SyncLocalApplyPlan ingress_bridge_apply_plan;
        require(build_sync_local_apply_plan(ingress_bridge_diff_plan, apply_options, ingress_bridge_apply_plan).ok &&
                ingress_bridge_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "local apply plan emits peer transport ingress bridge fixture");
        SyncStagedTransferInspectionResult ingress_bridge_inspection;
        require(inspect_sync_staged_transfer(ingress_bridge_remote,
                                            ingress_bridge_apply_plan.entries[0],
                                            inspection_options,
                                            ingress_bridge_inspection).ok &&
                ingress_bridge_inspection.missing_chunks.size() == ingress_bridge_remote.chunks.size(),
                "peer transport ingress bridge fixture starts with missing staged chunks");
        SyncChunkRequestPlanOptions ingress_bridge_request_options;
        ingress_bridge_request_options.max_chunks_per_request = 1;
        SyncChunkRequestPlanResult ingress_bridge_request;
        require(build_sync_chunk_request_plan(ingress_bridge_remote,
                                             ingress_bridge_apply_plan.entries[0],
                                             ingress_bridge_inspection,
                                             ingress_bridge_request_options,
                                             ingress_bridge_request).ok &&
                ingress_bridge_request.selected_chunks == 1,
                "peer transport ingress bridge fixture builds a one-chunk request");
        SyncPeerChunkAvailability ingress_bridge_peer;
        ingress_bridge_peer.peer_id = "peer-alpha";
        ingress_bridge_peer.peer_session_id = "session-one";
        ingress_bridge_peer.max_chunks = 1;
        ingress_bridge_peer.max_bytes = 5;
        ingress_bridge_peer.available_chunks = {ingress_bridge_remote.chunks[0]};
        SyncPeerChunkScheduleResult ingress_bridge_schedule;
        require(build_sync_peer_chunk_schedule(ingress_bridge_remote,
                                               ingress_bridge_apply_plan.entries[0],
                                               ingress_bridge_request,
                                               {ingress_bridge_peer},
                                               ingress_bridge_schedule).ok &&
                ingress_bridge_schedule.assignments.size() == 1,
                "peer transport ingress bridge fixture schedules one peer assignment");
        SyncPeerChunkResponseBatchEnvelope ingress_bridge_peer_batch;
        require(build_sync_peer_chunk_response_batch_envelope(ingress_bridge_remote,
                                                             ingress_bridge_apply_plan.entries[0],
                                                             ingress_bridge_request,
                                                             ingress_bridge_schedule,
                                                             ingress_bridge_schedule.assignments[0],
                                                             ingress_bridge_schedule.assignments[0].chunks,
                                                             ingress_bridge_peer_batch).ok,
                "peer transport ingress bridge fixture builds peer response evidence");
        SyncPeerTransportEnvelopeBuildOptions ingress_bridge_build_options;
        ingress_bridge_build_options.transport_instance_id = "transport-alpha";
        ingress_bridge_build_options.transport_key_id = "transport-key-alpha";
        ingress_bridge_build_options.shared_secret = "rev0744-selftest-transport-shared-secret";
        ingress_bridge_build_options.issued_at_epoch = 200;
        ingress_bridge_build_options.expires_at_epoch = 400;
        ingress_bridge_build_options.max_response_count = 1;
        ingress_bridge_build_options.max_total_bytes = ingress_bridge_peer_batch.total_bytes;
        ingress_bridge_build_options.max_chunk_bytes = 5;
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_bridge_envelope;
        require(build_sync_peer_transport_bound_chunk_response_batch_envelope(ingress_bridge_build_options,
                                                                             ingress_bridge_peer_batch,
                                                                             ingress_bridge_envelope).ok,
                "peer transport ingress bridge fixture builds transport-bound envelope");
        const std::vector<std::string> ingress_bridge_chunk_bytes = {
            chunk_bytes_for_body(ingress_bridge_body, ingress_bridge_schedule.assignments[0].chunks[0])
        };
        const fs::path ingress_bridge_local_socket_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-local-socket-ingress-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportLocalSocketIngressSubmitOptions ingress_local_socket_options;
        ingress_local_socket_options.sqlite_path = ingress_bridge_local_socket_queue_db.string();
        ingress_local_socket_options.session_id = "ingress-session";
        ingress_local_socket_options.submit_now_epoch = 208;
        ingress_local_socket_options.max_attempts = 2;
        ingress_local_socket_options.retry_backoff_seconds = 15;
        ingress_local_socket_options.max_frame_bytes = 4096;
        ingress_local_socket_options.max_chunk_count = 4;
        SyncPeerTransportLocalSocketIngressSubmitResult ingress_local_socket_result;
        require(submit_sync_peer_transport_local_socket_ingress_fixture(ingress_local_socket_options,
                                                                       ingress_bridge_envelope,
                                                                       ingress_bridge_chunk_bytes,
                                                                       ingress_local_socket_result).ok &&
                ingress_local_socket_result.socket_pair_created &&
                ingress_local_socket_result.frame_sent &&
                ingress_local_socket_result.frame_received &&
                ingress_local_socket_result.frame_digest_checked &&
                is_lowercase_sha256_hex(
                    ingress_local_socket_result.encoded_frame_digest) &&
                ingress_local_socket_result.encoded_frame_digest ==
                    ingress_local_socket_result.socket_frame_digest &&
                ingress_local_socket_result.canonical_frame_checked &&
                ingress_local_socket_result.wire_envelope_decoded &&
                ingress_local_socket_result.payload_bytes_received &&
                ingress_local_socket_result.row_inserted &&
                ingress_local_socket_result.chunk_count_received == 1 &&
                ingress_local_socket_result.chunk_bytes_received == ingress_bridge_peer_batch.total_bytes,
                "peer transport local socket fixture feeds durable ingress queue from socket-delivered bytes");
        SyncPeerTransportIngressStatusOptions ingress_local_socket_status_options;
        ingress_local_socket_status_options.sqlite_path = ingress_bridge_local_socket_queue_db.string();
        ingress_local_socket_status_options.session_id = "ingress-session";
        ingress_local_socket_status_options.status_now_epoch = 209;
        SyncPeerTransportIngressStatusResult ingress_local_socket_status;
        require(load_sync_peer_transport_ingress_status(ingress_local_socket_status_options, ingress_local_socket_status).ok &&
                ingress_local_socket_status.table_present &&
                ingress_local_socket_status.payload_table_present &&
                ingress_local_socket_status.total_rows == 1 &&
                ingress_local_socket_status.open_rows == 1 &&
                ingress_local_socket_status.open_bytes == ingress_bridge_peer_batch.total_bytes &&
                ingress_local_socket_status.durable_payload_rows == 1 &&
                ingress_local_socket_status.open_durable_payload_frame_bytes ==
                    ingress_local_socket_result.enqueue.payload_frame_bytes &&
                ingress_local_socket_status.rows_missing_durable_payload == 0 &&
                ingress_local_socket_status.queued_rows == 1 &&
                ingress_local_socket_status.queued_bytes == ingress_bridge_peer_batch.total_bytes &&
                ingress_local_socket_status.completed_rows == 0,
                "peer transport local socket fixture exposes queued residue and open byte pressure before staging authority is invoked");
        const fs::path ingress_bridge_loopback_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-loopback-ingress-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportLoopbackIngressSubmitOptions ingress_loopback_options;
        ingress_loopback_options.sqlite_path = ingress_bridge_loopback_queue_db.string();
        ingress_loopback_options.session_id = "ingress-session";
        ingress_loopback_options.submit_now_epoch = 210;
        ingress_loopback_options.max_attempts = 2;
        ingress_loopback_options.retry_backoff_seconds = 15;
        ingress_loopback_options.max_frame_bytes = 4096;
        ingress_loopback_options.max_chunk_count = 4;
        ingress_loopback_options.max_write_chunk_bytes = 23;
        ingress_loopback_options.max_read_chunk_bytes = 17;
        SyncPeerTransportLoopbackIngressSubmitResult ingress_loopback_result;
        require(submit_sync_peer_transport_loopback_ingress_harness(ingress_loopback_options,
                                                                    ingress_bridge_envelope,
                                                                    ingress_bridge_chunk_bytes,
                                                                    ingress_loopback_result).ok &&
                ingress_loopback_result.listener_created &&
                ingress_loopback_result.client_socket_created &&
                ingress_loopback_result.client_connect_initiated &&
                ingress_loopback_result.client_connected &&
                ingress_loopback_result.server_accepted &&
                ingress_loopback_result.frame_sent &&
                ingress_loopback_result.frame_received &&
                ingress_loopback_result.frame_digest_checked &&
                is_lowercase_sha256_hex(
                    ingress_loopback_result.encoded_frame_digest) &&
                ingress_loopback_result.encoded_frame_digest ==
                    ingress_loopback_result.socket_frame_digest &&
                ingress_loopback_result.canonical_frame_checked &&
                ingress_loopback_result.wire_envelope_decoded &&
                ingress_loopback_result.payload_bytes_received &&
                ingress_loopback_result.partial_write_count > 0 &&
                ingress_loopback_result.partial_read_count > 0 &&
                ingress_loopback_result.row_inserted &&
                ingress_loopback_result.chunk_count_received == 1 &&
                ingress_loopback_result.chunk_bytes_received == ingress_bridge_peer_batch.total_bytes,
                "peer transport loopback harness feeds durable ingress through a listener/client with partial frame movement");
        SyncPeerTransportIngressStatusOptions ingress_loopback_status_options;
        ingress_loopback_status_options.sqlite_path = ingress_bridge_loopback_queue_db.string();
        ingress_loopback_status_options.session_id = "ingress-session";
        ingress_loopback_status_options.status_now_epoch = 211;
        SyncPeerTransportIngressStatusResult ingress_loopback_status;
        require(load_sync_peer_transport_ingress_status(ingress_loopback_status_options, ingress_loopback_status).ok &&
                ingress_loopback_status.table_present &&
                ingress_loopback_status.payload_table_present &&
                ingress_loopback_status.total_rows == 1 &&
                ingress_loopback_status.open_rows == 1 &&
                ingress_loopback_status.open_bytes == ingress_bridge_peer_batch.total_bytes &&
                ingress_loopback_status.open_durable_payload_frame_bytes ==
                    ingress_loopback_result.enqueue.payload_frame_bytes &&
                ingress_loopback_status.open_rows_missing_durable_payload == 0 &&
                ingress_loopback_status.queued_rows == 1,
                "peer transport loopback harness leaves only inspectable queued ingress residue before staging authority");
        SyncPeerTransportLoopbackIngressSubmitResult ingress_loopback_duplicate_result;
        require(submit_sync_peer_transport_loopback_ingress_harness(ingress_loopback_options,
                                                                    ingress_bridge_envelope,
                                                                    ingress_bridge_chunk_bytes,
                                                                    ingress_loopback_duplicate_result).ok &&
                ingress_loopback_duplicate_result.server_accepted &&
                ingress_loopback_duplicate_result.frame_digest_checked &&
                ingress_loopback_duplicate_result.row_already_present &&
                !ingress_loopback_duplicate_result.row_inserted,
                "peer transport loopback harness duplicate frame remains idempotent queue evidence");
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_loopback_pressure_envelope = ingress_bridge_envelope;
        ingress_loopback_pressure_envelope.transport_envelope_idempotency_key = "sync-peer-transport-envelope:v1:" + sha256_hex("rev0751-loopback-pressure-envelope");
        SyncPeerTransportLoopbackIngressSubmitOptions ingress_loopback_pressure_options = ingress_loopback_options;
        ingress_loopback_pressure_options.submit_now_epoch = 212;
        ingress_loopback_pressure_options.max_open_rows = 1;
        SyncPeerTransportLoopbackIngressSubmitResult ingress_loopback_pressure_result;
        require(!submit_sync_peer_transport_loopback_ingress_harness(ingress_loopback_pressure_options,
                                                                     ingress_loopback_pressure_envelope,
                                                                     ingress_bridge_chunk_bytes,
                                                                     ingress_loopback_pressure_result).ok &&
                ingress_loopback_pressure_result.server_accepted &&
                ingress_loopback_pressure_result.frame_received &&
                ingress_loopback_pressure_result.frame_digest_checked &&
                ingress_loopback_pressure_result.enqueue.backpressure_checked &&
                ingress_loopback_pressure_result.enqueue.backpressure_rejected &&
                !ingress_loopback_pressure_result.row_inserted,
                "peer transport loopback harness carries bytes through TCP before durable enqueue rejects open-row pressure");
        require(!fs::exists(fs::path(ingress_bridge_apply_plan.entries[0].absolute_staging_path)),
                "peer transport loopback harness still has no direct staged-file materialization authority");
        const fs::path ingress_operator_status_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-operator-status-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(ingress_operator_status_checkpoint_db, apply_cleanup_ec);
        fs::remove(fs::path(ingress_operator_status_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(ingress_operator_status_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(retry_backoff_checkpoint_db,
                                    ingress_operator_status_checkpoint_db,
                                    "sync peer transport ingress operator status selftest seed");
        SyncPeerTransportLocalSocketIngressSubmitOptions ingress_operator_socket_options = ingress_local_socket_options;
        ingress_operator_socket_options.sqlite_path = ingress_operator_status_checkpoint_db.string();
        ingress_operator_socket_options.session_id = "session-main";
        ingress_operator_socket_options.submit_now_epoch = 212;
        SyncPeerTransportLocalSocketIngressSubmitResult ingress_operator_socket_result;
        require(submit_sync_peer_transport_local_socket_ingress_fixture(ingress_operator_socket_options,
                                                                       ingress_bridge_envelope,
                                                                       ingress_bridge_chunk_bytes,
                                                                       ingress_operator_socket_result).ok &&
                ingress_operator_socket_result.row_inserted,
                "peer transport local socket fixture can seed ingress residue in a real checkpoint database");
        SyncSessionCheckpointOperatorStatusOptions ingress_operator_status_options;
        ingress_operator_status_options.sqlite_path = ingress_operator_status_checkpoint_db.string();
        ingress_operator_status_options.session_id = "session-main";
        ingress_operator_status_options.scheduler_now_epoch = 213;
        SyncSessionCheckpointOperatorStatusResult ingress_operator_status;
        require(load_sync_session_checkpoint_operator_status(ingress_operator_status_options, ingress_operator_status).ok &&
                ingress_operator_status.status_loaded &&
                ingress_operator_status.query_only_enabled &&
                ingress_operator_status.peer_transport_ingress_table_present &&
                ingress_operator_status.peer_transport_ingress_total_rows == 1 &&
                ingress_operator_status.peer_transport_ingress_open_rows == 1 &&
                ingress_operator_status.peer_transport_ingress_open_bytes == ingress_bridge_peer_batch.total_bytes &&
                ingress_operator_status.peer_transport_ingress_queued_rows == 1 &&
                ingress_operator_status.peer_transport_ingress_next_action == "run-peer-transport-ingress-worker",
                "sync checkpoint operator status surfaces socket-produced peer ingress queue pressure without mutating it");
        require(!fs::exists(fs::path(ingress_bridge_apply_plan.entries[0].absolute_staging_path)),
                "peer transport local socket fixture has no direct staged-file materialization authority");
        SyncPeerTransportLocalSocketIngressSubmitResult ingress_local_socket_duplicate_result;
        require(submit_sync_peer_transport_local_socket_ingress_fixture(ingress_local_socket_options,
                                                                       ingress_bridge_envelope,
                                                                       ingress_bridge_chunk_bytes,
                                                                       ingress_local_socket_duplicate_result).ok &&
                ingress_local_socket_duplicate_result.row_already_present,
                "peer transport local socket fixture duplicate frame replays as idempotent queue evidence");
        std::vector<std::string> ingress_local_socket_tampered_bytes = ingress_bridge_chunk_bytes;
        ingress_local_socket_tampered_bytes[0][0] = ingress_local_socket_tampered_bytes[0][0] == 'x' ? 'y' : 'x';
        SyncPeerTransportLocalSocketIngressSubmitResult ingress_local_socket_tampered_result;
        require(!submit_sync_peer_transport_local_socket_ingress_fixture(ingress_local_socket_options,
                                                                        ingress_bridge_envelope,
                                                                        ingress_local_socket_tampered_bytes,
                                                                        ingress_local_socket_tampered_result).ok,
                "peer transport local socket fixture rejects duplicate envelope keys with different socket payload bytes");

        const fs::path ingress_bridge_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-ingress-queue-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportIngressEnqueueOptions ingress_enqueue_options;
        ingress_enqueue_options.sqlite_path = ingress_bridge_queue_db.string();
        ingress_enqueue_options.session_id = "ingress-session";
        ingress_enqueue_options.enqueue_now_epoch = 210;
        ingress_enqueue_options.max_attempts = 2;
        ingress_enqueue_options.retry_backoff_seconds = 15;
        SyncPeerTransportIngressEnqueueResult ingress_enqueue_result;
        require(enqueue_sync_peer_transport_ingress_envelope(ingress_enqueue_options,
                                                             ingress_bridge_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             ingress_enqueue_result).ok &&
                ingress_enqueue_result.row_inserted &&
                !ingress_enqueue_result.row_already_present &&
                ingress_enqueue_result.payload_frame_stored &&
                !ingress_enqueue_result.payload_frame_already_present &&
                ingress_enqueue_result.payload_frame_codec_version == 1 &&
                ingress_enqueue_result.payload_frame_bytes >
                    ingress_bridge_peer_batch.total_bytes &&
                is_lowercase_sha256_hex(ingress_enqueue_result.payload_frame_sha256) &&
                !ingress_enqueue_result.payload_digest.empty(),
                "peer transport ingress queue atomically persists metadata and the complete canonical frame without staging authority");

        SyncPeerTransportIngressPayloadLoadOptions ingress_payload_load_options;
        ingress_payload_load_options.sqlite_path = ingress_bridge_queue_db.string();
        ingress_payload_load_options.session_id = "ingress-session";
        ingress_payload_load_options.transport_envelope_idempotency_key =
            ingress_bridge_envelope.transport_envelope_idempotency_key;
        SyncPeerTransportIngressPayloadLoadResult ingress_payload_load_result;
        require(load_sync_peer_transport_ingress_payload(
                    ingress_payload_load_options, ingress_payload_load_result).ok &&
                ingress_payload_load_result.row_found &&
                ingress_payload_load_result.payload_found &&
                ingress_payload_load_result.frame_digest_checked &&
                ingress_payload_load_result.payload_digest_checked &&
                ingress_payload_load_result.canonical_frame_decoded &&
                ingress_payload_load_result.codec_version ==
                    ingress_enqueue_result.payload_frame_codec_version &&
                ingress_payload_load_result.canonical_frame_bytes ==
                    ingress_enqueue_result.payload_frame_bytes &&
                ingress_payload_load_result.canonical_frame_sha256 ==
                    ingress_enqueue_result.payload_frame_sha256 &&
                ingress_payload_load_result.payload_digest ==
                    ingress_enqueue_result.payload_digest &&
                ingress_payload_load_result.stored_at_epoch == 210 &&
                ingress_payload_load_result.transport_envelope.transport_envelope_idempotency_key ==
                    ingress_bridge_envelope.transport_envelope_idempotency_key &&
                ingress_payload_load_result.transport_envelope.transport_mac_sha256 ==
                    ingress_bridge_envelope.transport_mac_sha256 &&
                ingress_payload_load_result.transport_envelope.peer_batch_envelope.peer_response_batch_idempotency_key ==
                    ingress_bridge_envelope.peer_batch_envelope.peer_response_batch_idempotency_key &&
                ingress_payload_load_result.chunk_bytes == ingress_bridge_chunk_bytes,
                "peer transport ingress restart loader reconstructs exact envelope and binary chunk authority from durable canonical bytes alone");

        SyncPeerTransportIngressEnqueueResult ingress_duplicate_enqueue_result;
        require(enqueue_sync_peer_transport_ingress_envelope(ingress_enqueue_options,
                                                             ingress_bridge_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             ingress_duplicate_enqueue_result).ok &&
                ingress_duplicate_enqueue_result.row_already_present &&
                !ingress_duplicate_enqueue_result.payload_frame_stored &&
                ingress_duplicate_enqueue_result.payload_frame_already_present &&
                ingress_duplicate_enqueue_result.payload_frame_sha256 ==
                    ingress_enqueue_result.payload_frame_sha256 &&
                ingress_duplicate_enqueue_result.payload_frame_bytes ==
                    ingress_enqueue_result.payload_frame_bytes,
                "peer transport ingress queue treats an exact canonical-frame replay as idempotent and re-verifies every stored byte");

        const fs::path ingress_payload_corruption_db = fs::temp_directory_path() /
            ("anonsync-sync-peer-transport-ingress-payload-corruption-" +
             std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(ingress_payload_corruption_db, apply_cleanup_ec);
        fs::remove(fs::path(ingress_payload_corruption_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(ingress_payload_corruption_db.string() + "-shm"), apply_cleanup_ec);
        SyncPeerTransportIngressEnqueueOptions ingress_payload_corruption_enqueue_options =
            ingress_enqueue_options;
        ingress_payload_corruption_enqueue_options.sqlite_path =
            ingress_payload_corruption_db.string();
        ingress_payload_corruption_enqueue_options.session_id = "ingress-corruption-session";
        SyncPeerTransportIngressEnqueueResult ingress_payload_corruption_enqueue_result;
        require(enqueue_sync_peer_transport_ingress_envelope(
                    ingress_payload_corruption_enqueue_options,
                    ingress_bridge_envelope,
                    ingress_bridge_chunk_bytes,
                    ingress_payload_corruption_enqueue_result).ok &&
                ingress_payload_corruption_enqueue_result.row_inserted &&
                ingress_payload_corruption_enqueue_result.payload_frame_stored,
                "peer transport ingress corruption fixture begins with complete durable payload evidence");
        {
            SyncSqliteDb corruption_handle;
            int corruption_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            corruption_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(ingress_payload_corruption_db.string().c_str(),
                                corruption_handle.db.out(),
                                corruption_flags,
                                nullptr) != SQLITE_OK) {
                throw std::runtime_error(
                    "peer transport ingress corruption fixture could not open SQLite database");
            }
            sqlite_exec_or_throw(
                corruption_handle.db,
                "UPDATE main.sync_peer_transport_ingress_payloads "
                "SET canonical_frame=zeroblob(canonical_frame_bytes);",
                "peer transport ingress same-length durable payload corruption");
        }
        SyncPeerTransportIngressPayloadLoadOptions ingress_payload_corruption_load_options;
        ingress_payload_corruption_load_options.sqlite_path =
            ingress_payload_corruption_db.string();
        ingress_payload_corruption_load_options.session_id = "ingress-corruption-session";
        ingress_payload_corruption_load_options.transport_envelope_idempotency_key =
            ingress_bridge_envelope.transport_envelope_idempotency_key;
        SyncPeerTransportIngressPayloadLoadResult ingress_payload_corruption_load_result;
        const SyncValidationResult ingress_payload_corruption_load =
            load_sync_peer_transport_ingress_payload(
                ingress_payload_corruption_load_options,
                ingress_payload_corruption_load_result);
        require(!ingress_payload_corruption_load.ok &&
                    ingress_payload_corruption_load_result.row_found &&
                    ingress_payload_corruption_load.reason.find(
                        "stored canonical frame digest differs from blob bytes") != std::string::npos,
                "peer transport ingress restart loader detects same-length durable BLOB corruption before publishing decoded bytes");
        SyncPeerTransportIngressEnqueueResult ingress_payload_corruption_replay_result;
        require(!enqueue_sync_peer_transport_ingress_envelope(
                    ingress_payload_corruption_enqueue_options,
                    ingress_bridge_envelope,
                    ingress_bridge_chunk_bytes,
                    ingress_payload_corruption_replay_result).ok &&
                ingress_payload_corruption_replay_result.row_already_present,
                "peer transport ingress duplicate replay refuses to overwrite contradictory durable payload history");
        fs::remove(ingress_payload_corruption_db, apply_cleanup_ec);
        fs::remove(fs::path(ingress_payload_corruption_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(ingress_payload_corruption_db.string() + "-shm"), apply_cleanup_ec);

        SyncPeerTransportIngressStatusResult ingress_queued_status;
        SyncPeerTransportIngressStatusOptions ingress_status_options;
        ingress_status_options.sqlite_path = ingress_bridge_queue_db.string();
        ingress_status_options.session_id = "ingress-session";
        ingress_status_options.status_now_epoch = 211;
        require(load_sync_peer_transport_ingress_status(ingress_status_options, ingress_queued_status).ok &&
                ingress_queued_status.table_present &&
                ingress_queued_status.payload_table_present &&
                ingress_queued_status.total_rows == 1 &&
                ingress_queued_status.open_rows == 1 &&
                ingress_queued_status.open_bytes == ingress_bridge_peer_batch.total_bytes &&
                ingress_queued_status.durable_payload_rows == 1 &&
                ingress_queued_status.durable_payload_frame_bytes ==
                    ingress_enqueue_result.payload_frame_bytes &&
                ingress_queued_status.open_durable_payload_frame_bytes ==
                    ingress_enqueue_result.payload_frame_bytes &&
                ingress_queued_status.queued_durable_payload_frame_bytes ==
                    ingress_enqueue_result.payload_frame_bytes &&
                ingress_queued_status.rows_missing_durable_payload == 0 &&
                ingress_queued_status.orphan_durable_payload_rows == 0 &&
                ingress_queued_status.queued_rows == 1 &&
                ingress_queued_status.completed_rows == 0,
                "peer transport ingress status exposes queued envelope residue and open byte pressure");
        const fs::path ingress_pressure_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-ingress-pressure-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportIngressEnqueueOptions ingress_pressure_options = ingress_enqueue_options;
        ingress_pressure_options.sqlite_path = ingress_pressure_queue_db.string();
        ingress_pressure_options.max_open_rows = 1;
        SyncPeerTransportIngressEnqueueResult ingress_pressure_first;
        require(enqueue_sync_peer_transport_ingress_envelope(ingress_pressure_options,
                                                             ingress_bridge_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             ingress_pressure_first).ok &&
                ingress_pressure_first.row_inserted &&
                ingress_pressure_first.backpressure_checked &&
                ingress_pressure_first.open_rows_before == 0 &&
                ingress_pressure_first.max_open_rows == 1,
                "peer transport ingress enqueue records pressure counters before accepting the first open row");
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_pressure_second_envelope = ingress_bridge_envelope;
        ingress_pressure_second_envelope.transport_envelope_idempotency_key = "sync-peer-transport-envelope:v1:" + sha256_hex("rev0747-pressure-second-envelope");
        SyncPeerTransportIngressEnqueueResult ingress_pressure_second;
        require(!enqueue_sync_peer_transport_ingress_envelope(ingress_pressure_options,
                                                              ingress_pressure_second_envelope,
                                                              ingress_bridge_chunk_bytes,
                                                              ingress_pressure_second).ok &&
                ingress_pressure_second.backpressure_checked &&
                ingress_pressure_second.backpressure_rejected &&
                ingress_pressure_second.open_rows_before == 1,
                "peer transport ingress enqueue rejects a second open row when the session row cap is reached");
        SyncPeerTransportIngressStatusResult ingress_pressure_status;
        SyncPeerTransportIngressStatusOptions ingress_pressure_status_options;
        ingress_pressure_status_options.sqlite_path = ingress_pressure_queue_db.string();
        ingress_pressure_status_options.session_id = "ingress-session";
        ingress_pressure_status_options.status_now_epoch = 212;
        require(load_sync_peer_transport_ingress_status(ingress_pressure_status_options, ingress_pressure_status).ok &&
                ingress_pressure_status.total_rows == 1 &&
                ingress_pressure_status.open_rows == 1 &&
                ingress_pressure_status.queued_rows == 1,
                "peer transport ingress backpressure leaves only the accepted open row in the durable queue");

        const fs::path ingress_frame_pressure_queue_db = fs::temp_directory_path() /
            ("anonsync-sync-peer-transport-ingress-frame-pressure-" +
             std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportIngressEnqueueOptions ingress_frame_pressure_options = ingress_enqueue_options;
        ingress_frame_pressure_options.sqlite_path = ingress_frame_pressure_queue_db.string();
        ingress_frame_pressure_options.max_open_bytes =
            ingress_bridge_peer_batch.total_bytes * 3;
        ingress_frame_pressure_options.max_open_frame_bytes =
            ingress_enqueue_result.payload_frame_bytes;
        SyncPeerTransportIngressEnqueueResult ingress_frame_pressure_first;
        require(enqueue_sync_peer_transport_ingress_envelope(
                    ingress_frame_pressure_options,
                    ingress_bridge_envelope,
                    ingress_bridge_chunk_bytes,
                    ingress_frame_pressure_first).ok &&
                ingress_frame_pressure_first.row_inserted &&
                ingress_frame_pressure_first.open_frame_bytes_before == 0 &&
                ingress_frame_pressure_first.max_open_frame_bytes ==
                    ingress_enqueue_result.payload_frame_bytes,
                "peer transport ingress physical pressure admits an exact first canonical frame at its configured bound");
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_frame_pressure_second_envelope =
            ingress_bridge_envelope;
        ingress_frame_pressure_second_envelope.transport_envelope_idempotency_key =
            "sync-peer-transport-envelope:v1:" +
            sha256_hex("rev0762-frame-pressure-second-envelope");
        SyncPeerTransportIngressEnqueueResult ingress_frame_pressure_second;
        const SyncValidationResult ingress_frame_pressure_rejection =
            enqueue_sync_peer_transport_ingress_envelope(
                ingress_frame_pressure_options,
                ingress_frame_pressure_second_envelope,
                ingress_bridge_chunk_bytes,
                ingress_frame_pressure_second);
        require(!ingress_frame_pressure_rejection.ok &&
                ingress_frame_pressure_rejection.reason.find(
                    "canonical-frame byte cap reached") != std::string::npos &&
                ingress_frame_pressure_second.backpressure_checked &&
                ingress_frame_pressure_second.backpressure_rejected &&
                ingress_frame_pressure_second.open_bytes_before ==
                    ingress_bridge_peer_batch.total_bytes &&
                ingress_frame_pressure_second.open_frame_bytes_before ==
                    ingress_frame_pressure_first.payload_frame_bytes &&
                !ingress_frame_pressure_second.row_inserted,
                "peer transport ingress rejects metadata amplification at the durable canonical-frame boundary even when logical payload capacity remains");

        const fs::path ingress_payload_backfill_db = fs::temp_directory_path() /
            ("anonsync-sync-peer-transport-ingress-payload-backfill-" +
             std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportIngressEnqueueOptions ingress_payload_backfill_options =
            ingress_enqueue_options;
        ingress_payload_backfill_options.sqlite_path = ingress_payload_backfill_db.string();
        SyncPeerTransportIngressEnqueueResult ingress_payload_backfill_seed;
        require(enqueue_sync_peer_transport_ingress_envelope(
                    ingress_payload_backfill_options,
                    ingress_bridge_envelope,
                    ingress_bridge_chunk_bytes,
                    ingress_payload_backfill_seed).ok &&
                ingress_payload_backfill_seed.payload_frame_stored,
                "peer transport ingress legacy backfill fixture starts with exact durable evidence");
        {
            SyncSqliteDb backfill_handle;
            int backfill_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            backfill_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(ingress_payload_backfill_db.string().c_str(),
                                backfill_handle.db.out(),
                                backfill_flags,
                                nullptr) != SQLITE_OK) {
                throw std::runtime_error(
                    "peer transport ingress legacy backfill fixture could not open SQLite database");
            }
            sqlite_exec_or_throw(
                backfill_handle.db,
                "DELETE FROM main.sync_peer_transport_ingress_payloads;",
                "peer transport ingress legacy backfill payload deletion");
        }
        SyncPeerTransportIngressStatusOptions ingress_payload_backfill_status_options;
        ingress_payload_backfill_status_options.sqlite_path = ingress_payload_backfill_db.string();
        ingress_payload_backfill_status_options.session_id = "ingress-session";
        ingress_payload_backfill_status_options.status_now_epoch = 213;
        SyncPeerTransportIngressStatusResult ingress_payload_backfill_missing_status;
        require(load_sync_peer_transport_ingress_status(
                    ingress_payload_backfill_status_options,
                    ingress_payload_backfill_missing_status).ok &&
                ingress_payload_backfill_missing_status.payload_table_present &&
                ingress_payload_backfill_missing_status.total_rows == 1 &&
                ingress_payload_backfill_missing_status.durable_payload_rows == 0 &&
                ingress_payload_backfill_missing_status.durable_payload_frame_bytes == 0 &&
                ingress_payload_backfill_missing_status.rows_missing_durable_payload == 1 &&
                ingress_payload_backfill_missing_status.open_rows_missing_durable_payload == 1,
                "peer transport ingress status makes a metadata-only legacy row explicit instead of treating absent authority bytes as zero pressure");
        SyncPeerTransportIngressEnqueueOptions ingress_payload_backfill_capped_options =
            ingress_payload_backfill_options;
        ingress_payload_backfill_capped_options.max_open_frame_bytes =
            ingress_payload_backfill_seed.payload_frame_bytes - 1;
        SyncPeerTransportIngressEnqueueResult ingress_payload_backfill_capped_result;
        const SyncValidationResult ingress_payload_backfill_capped_rejection =
            enqueue_sync_peer_transport_ingress_envelope(
                ingress_payload_backfill_capped_options,
                ingress_bridge_envelope,
                ingress_bridge_chunk_bytes,
                ingress_payload_backfill_capped_result);
        require(!ingress_payload_backfill_capped_rejection.ok &&
                ingress_payload_backfill_capped_rejection.reason.find(
                    "payload backfill backpressure rejected") != std::string::npos &&
                ingress_payload_backfill_capped_result.row_already_present &&
                ingress_payload_backfill_capped_result.backpressure_checked &&
                ingress_payload_backfill_capped_result.backpressure_rejected &&
                ingress_payload_backfill_capped_result.open_frame_bytes_before == 0 &&
                !ingress_payload_backfill_capped_result.payload_frame_stored,
                "peer transport ingress does not let a metadata-only duplicate bypass the physical evidence quota while backfilling its frame");
        SyncPeerTransportIngressEnqueueResult ingress_payload_backfill_result;
        require(enqueue_sync_peer_transport_ingress_envelope(
                    ingress_payload_backfill_options,
                    ingress_bridge_envelope,
                    ingress_bridge_chunk_bytes,
                    ingress_payload_backfill_result).ok &&
                ingress_payload_backfill_result.row_already_present &&
                ingress_payload_backfill_result.backpressure_checked &&
                ingress_payload_backfill_result.payload_frame_stored &&
                !ingress_payload_backfill_result.payload_frame_already_present,
                "peer transport ingress can deliberately repair a metadata-only row when durable evidence capacity is available");
        SyncPeerTransportIngressStatusResult ingress_payload_backfill_repaired_status;
        require(load_sync_peer_transport_ingress_status(
                    ingress_payload_backfill_status_options,
                    ingress_payload_backfill_repaired_status).ok &&
                ingress_payload_backfill_repaired_status.durable_payload_rows == 1 &&
                ingress_payload_backfill_repaired_status.durable_payload_frame_bytes ==
                    ingress_payload_backfill_seed.payload_frame_bytes &&
                ingress_payload_backfill_repaired_status.rows_missing_durable_payload == 0 &&
                ingress_payload_backfill_repaired_status.open_rows_missing_durable_payload == 0,
                "peer transport ingress status clears missing-evidence pressure only after exact canonical bytes are restored");

        const fs::path ingress_orphan_payload_db = fs::temp_directory_path() /
            ("anonsync-sync-peer-transport-ingress-orphan-payload-" +
             std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportIngressEnqueueOptions ingress_orphan_payload_options =
            ingress_enqueue_options;
        ingress_orphan_payload_options.sqlite_path = ingress_orphan_payload_db.string();
        SyncPeerTransportIngressEnqueueResult ingress_orphan_payload_seed;
        require(enqueue_sync_peer_transport_ingress_envelope(
                    ingress_orphan_payload_options,
                    ingress_bridge_envelope,
                    ingress_bridge_chunk_bytes,
                    ingress_orphan_payload_seed).ok,
                "peer transport ingress orphan fixture starts with a linked payload row");
        {
            SyncSqliteDb orphan_handle;
            int orphan_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
            orphan_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
            if (::anonsync::persistence::open_verified_sqlite_database(ingress_orphan_payload_db.string().c_str(),
                                orphan_handle.db.out(),
                                orphan_flags,
                                nullptr) != SQLITE_OK) {
                throw std::runtime_error(
                    "peer transport ingress orphan fixture could not open SQLite database");
            }
            sqlite_exec_or_throw(
                orphan_handle.db,
                "PRAGMA foreign_keys=OFF; DELETE FROM sync_peer_transport_ingress_envelopes;",
                "peer transport ingress orphan fixture parent deletion");
        }
        SyncPeerTransportIngressStatusOptions ingress_orphan_payload_status_options;
        ingress_orphan_payload_status_options.sqlite_path = ingress_orphan_payload_db.string();
        ingress_orphan_payload_status_options.session_id = "ingress-session";
        ingress_orphan_payload_status_options.status_now_epoch = 214;
        SyncPeerTransportIngressStatusResult ingress_orphan_payload_status;
        require(load_sync_peer_transport_ingress_status(
                    ingress_orphan_payload_status_options,
                    ingress_orphan_payload_status).ok &&
                ingress_orphan_payload_status.total_rows == 0 &&
                ingress_orphan_payload_status.durable_payload_rows == 0 &&
                ingress_orphan_payload_status.orphan_durable_payload_rows == 1 &&
                ingress_orphan_payload_status.orphan_durable_payload_frame_bytes ==
                    ingress_orphan_payload_seed.payload_frame_bytes,
                "peer transport ingress status exposes orphaned canonical evidence created outside the foreign-key contract");

        const fs::path ingress_authority_gate_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-authority-gate-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportAuthorityRecordOptions ingress_authority_record_options;
        ingress_authority_record_options.sqlite_path = ingress_authority_gate_queue_db.string();
        ingress_authority_record_options.session_id = "ingress-session";
        ingress_authority_record_options.peer_id = "peer-alpha";
        ingress_authority_record_options.peer_session_id = "session-one";
        ingress_authority_record_options.transport_instance_id = "transport-alpha";
        ingress_authority_record_options.transport_key_id = "transport-key-alpha";
        ingress_authority_record_options.authority_status = "trusted";
        ingress_authority_record_options.valid_from_epoch = 200;
        ingress_authority_record_options.valid_until_epoch = 0;
        ingress_authority_record_options.updated_at_epoch = 213;
        ingress_authority_record_options.reason = "rev0748 selftest trusted local peer key";
        SyncPeerTransportAuthorityRecordResult ingress_authority_record_result;
        require(record_sync_peer_transport_authority(ingress_authority_record_options, ingress_authority_record_result).ok &&
                ingress_authority_record_result.record_inserted &&
                ingress_authority_record_result.authority_status == "trusted",
                "peer transport authority record stores a trusted local peer/key status");
        SyncPeerTransportAuthorityDecisionOptions ingress_authority_decision_options;
        ingress_authority_decision_options.sqlite_path = ingress_authority_gate_queue_db.string();
        ingress_authority_decision_options.session_id = "ingress-session";
        ingress_authority_decision_options.decision_now_epoch = 214;
        SyncPeerTransportAuthorityDecisionResult ingress_authority_allowed_decision;
        require(evaluate_sync_peer_transport_authority(ingress_authority_decision_options,
                                                       ingress_bridge_envelope,
                                                       ingress_bridge_chunk_bytes,
                                                       ingress_authority_allowed_decision).ok &&
                ingress_authority_allowed_decision.authority_checked &&
                ingress_authority_allowed_decision.authority_record_found &&
                ingress_authority_allowed_decision.authority_allowed &&
                !ingress_authority_allowed_decision.authority_denied,
                "peer transport authority decision allows a trusted current peer/key before enqueue");
        const fs::path ingress_authority_supersession_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-authority-supersession-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportAuthorityRecordOptions ingress_authority_supersession_old_options = ingress_authority_record_options;
        ingress_authority_supersession_old_options.sqlite_path = ingress_authority_supersession_queue_db.string();
        ingress_authority_supersession_old_options.updated_at_epoch = 216;
        ingress_authority_supersession_old_options.reason = "rev0750 selftest trusted old peer transport key";
        SyncPeerTransportAuthorityRecordResult ingress_authority_supersession_old_result;
        require(record_sync_peer_transport_authority(ingress_authority_supersession_old_options, ingress_authority_supersession_old_result).ok &&
                ingress_authority_supersession_old_result.record_inserted,
                "peer transport authority supersession fixture records the old trusted peer/key");
        SyncPeerTransportEnvelopeBuildOptions ingress_authority_replacement_build_options = ingress_bridge_build_options;
        ingress_authority_replacement_build_options.transport_key_id = "transport-key-bravo";
        ingress_authority_replacement_build_options.issued_at_epoch = 216;
        ingress_authority_replacement_build_options.expires_at_epoch = 420;
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_authority_replacement_envelope;
        require(build_sync_peer_transport_bound_chunk_response_batch_envelope(ingress_authority_replacement_build_options,
                                                                             ingress_bridge_peer_batch,
                                                                             ingress_authority_replacement_envelope).ok,
                "peer transport authority supersession fixture builds a replacement-key envelope");
        SyncPeerTransportAuthorityRecordOptions ingress_authority_replacement_options = ingress_authority_supersession_old_options;
        ingress_authority_replacement_options.transport_key_id = "transport-key-bravo";
        ingress_authority_replacement_options.valid_from_epoch = 216;
        ingress_authority_replacement_options.updated_at_epoch = 217;
        ingress_authority_replacement_options.reason = "rev0750 selftest trusted replacement peer transport key";
        SyncPeerTransportAuthorityRecordResult ingress_authority_replacement_result;
        require(record_sync_peer_transport_authority(ingress_authority_replacement_options, ingress_authority_replacement_result).ok &&
                ingress_authority_replacement_result.record_inserted,
                "peer transport authority supersession fixture records the replacement trusted peer/key");
        SyncPeerTransportAuthorityDecisionOptions ingress_authority_supersession_decision_options;
        ingress_authority_supersession_decision_options.sqlite_path = ingress_authority_supersession_queue_db.string();
        ingress_authority_supersession_decision_options.session_id = "ingress-session";
        ingress_authority_supersession_decision_options.decision_now_epoch = 218;
        SyncPeerTransportAuthorityDecisionResult ingress_authority_replacement_decision;
        require(evaluate_sync_peer_transport_authority(ingress_authority_supersession_decision_options,
                                                       ingress_authority_replacement_envelope,
                                                       ingress_bridge_chunk_bytes,
                                                       ingress_authority_replacement_decision).ok &&
                ingress_authority_replacement_decision.authority_allowed &&
                ingress_authority_replacement_decision.authority_lifecycle_state == "current" &&
                ingress_authority_replacement_decision.transport_key_id == "transport-key-bravo" &&
                !ingress_authority_replacement_decision.authority_supersession_found,
                "peer transport authority decision treats the replacement key as the current trusted key");
        SyncPeerTransportAuthoritySupersessionRecordOptions ingress_authority_supersession_options;
        ingress_authority_supersession_options.sqlite_path = ingress_authority_supersession_queue_db.string();
        ingress_authority_supersession_options.session_id = "ingress-session";
        ingress_authority_supersession_options.peer_id = "peer-alpha";
        ingress_authority_supersession_options.peer_session_id = "session-one";
        ingress_authority_supersession_options.transport_instance_id = "transport-alpha";
        ingress_authority_supersession_options.old_transport_key_id = "transport-key-alpha";
        ingress_authority_supersession_options.replacement_transport_key_id = "transport-key-bravo";
        ingress_authority_supersession_options.overlap_valid_from_epoch = 218;
        ingress_authority_supersession_options.overlap_valid_until_epoch = 230;
        ingress_authority_supersession_options.updated_at_epoch = 218;
        ingress_authority_supersession_options.reason = "rev0750 selftest bounded peer transport key overlap";
        SyncPeerTransportAuthoritySupersessionRecordResult ingress_authority_supersession_result;
        require(record_sync_peer_transport_authority_supersession(ingress_authority_supersession_options,
                                                                  ingress_authority_supersession_result).ok &&
                ingress_authority_supersession_result.record_inserted &&
                ingress_authority_supersession_result.old_transport_key_id == "transport-key-alpha" &&
                ingress_authority_supersession_result.replacement_transport_key_id == "transport-key-bravo",
                "peer transport authority supersession stores explicit old-key to replacement-key overlap bounds");
        ingress_authority_supersession_decision_options.decision_now_epoch = 220;
        SyncPeerTransportAuthorityDecisionResult ingress_authority_overlap_decision;
        require(evaluate_sync_peer_transport_authority(ingress_authority_supersession_decision_options,
                                                       ingress_bridge_envelope,
                                                       ingress_bridge_chunk_bytes,
                                                       ingress_authority_overlap_decision).ok &&
                ingress_authority_overlap_decision.authority_allowed &&
                ingress_authority_overlap_decision.authority_supersession_found &&
                ingress_authority_overlap_decision.authority_supersession_overlap_valid &&
                ingress_authority_overlap_decision.authority_lifecycle_state == "superseded-overlap-valid" &&
                ingress_authority_overlap_decision.replacement_transport_key_id == "transport-key-bravo",
                "peer transport authority decision allows a superseded old key only inside the explicit overlap window");
        SyncPeerTransportIngressEnqueueOptions ingress_authority_supersession_enqueue_options = ingress_enqueue_options;
        ingress_authority_supersession_enqueue_options.sqlite_path = ingress_authority_supersession_queue_db.string();
        ingress_authority_supersession_enqueue_options.enqueue_now_epoch = 220;
        ingress_authority_supersession_enqueue_options.require_authority_gate = true;
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_authority_overlap_envelope = ingress_bridge_envelope;
        ingress_authority_overlap_envelope.transport_envelope_idempotency_key = "sync-peer-transport-envelope:v1:" + sha256_hex("rev0750-authority-overlap-envelope");
        SyncPeerTransportIngressEnqueueResult ingress_authority_overlap_enqueue;
        require(enqueue_sync_peer_transport_ingress_envelope(ingress_authority_supersession_enqueue_options,
                                                             ingress_authority_overlap_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             ingress_authority_overlap_enqueue).ok &&
                ingress_authority_overlap_enqueue.row_inserted &&
                ingress_authority_overlap_enqueue.authority_decision.authority_allowed &&
                ingress_authority_overlap_enqueue.authority_decision.authority_lifecycle_state == "superseded-overlap-valid" &&
                ingress_authority_overlap_enqueue.backpressure_checked,
                "peer transport ingress authority gate queues an old key only during its supersession overlap");
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_authority_superseded_expired_envelope = ingress_bridge_envelope;
        ingress_authority_superseded_expired_envelope.transport_envelope_idempotency_key = "sync-peer-transport-envelope:v1:" + sha256_hex("rev0750-authority-superseded-expired-envelope");
        ingress_authority_supersession_enqueue_options.enqueue_now_epoch = 231;
        SyncPeerTransportIngressEnqueueResult ingress_authority_superseded_expired_enqueue;
        require(!enqueue_sync_peer_transport_ingress_envelope(ingress_authority_supersession_enqueue_options,
                                                              ingress_authority_superseded_expired_envelope,
                                                              ingress_bridge_chunk_bytes,
                                                              ingress_authority_superseded_expired_enqueue).ok &&
                ingress_authority_superseded_expired_enqueue.authority_decision.authority_checked &&
                ingress_authority_superseded_expired_enqueue.authority_decision.authority_denied &&
                ingress_authority_superseded_expired_enqueue.authority_decision.denial_recorded &&
                ingress_authority_superseded_expired_enqueue.authority_decision.authority_lifecycle_state == "superseded-expired" &&
                ingress_authority_superseded_expired_enqueue.authority_decision.deny_reason == "peer transport authority superseded key expired" &&
                !ingress_authority_superseded_expired_enqueue.row_inserted &&
                !ingress_authority_superseded_expired_enqueue.backpressure_checked,
                "peer transport ingress authority gate denies an old key after the supersession overlap before queue pressure or insert");
        SyncPeerTransportIngressStatusOptions ingress_authority_supersession_status_options;
        ingress_authority_supersession_status_options.sqlite_path = ingress_authority_supersession_queue_db.string();
        ingress_authority_supersession_status_options.session_id = "ingress-session";
        ingress_authority_supersession_status_options.status_now_epoch = 232;
        SyncPeerTransportIngressStatusResult ingress_authority_supersession_status;
        require(load_sync_peer_transport_ingress_status(ingress_authority_supersession_status_options,
                                                        ingress_authority_supersession_status).ok &&
                ingress_authority_supersession_status.total_rows == 1 &&
                ingress_authority_supersession_status.authority_denial_table_present &&
                ingress_authority_supersession_status.authority_denied_rows == 1 &&
                ingress_authority_supersession_status.authority_superseded_expired_denied_rows == 1 &&
                ingress_authority_supersession_status.authority_supersession_table_present &&
                ingress_authority_supersession_status.authority_supersession_rows == 1,
                "peer transport ingress status exposes supersession rows and superseded-expired denial residue");
        SyncPeerTransportAuthorityRecordOptions ingress_authority_operator_old_options = ingress_authority_supersession_old_options;
        ingress_authority_operator_old_options.sqlite_path = ingress_operator_status_checkpoint_db.string();
        ingress_authority_operator_old_options.session_id = "session-main";
        ingress_authority_operator_old_options.updated_at_epoch = 233;
        SyncPeerTransportAuthorityRecordResult ingress_authority_operator_old_result;
        require(record_sync_peer_transport_authority(ingress_authority_operator_old_options, ingress_authority_operator_old_result).ok,
                "peer transport authority supersession fixture seeds old key into operator checkpoint database");
        SyncPeerTransportAuthorityRecordOptions ingress_authority_operator_replacement_options = ingress_authority_replacement_options;
        ingress_authority_operator_replacement_options.sqlite_path = ingress_operator_status_checkpoint_db.string();
        ingress_authority_operator_replacement_options.session_id = "session-main";
        ingress_authority_operator_replacement_options.updated_at_epoch = 234;
        SyncPeerTransportAuthorityRecordResult ingress_authority_operator_replacement_result;
        require(record_sync_peer_transport_authority(ingress_authority_operator_replacement_options, ingress_authority_operator_replacement_result).ok,
                "peer transport authority supersession fixture seeds replacement key into operator checkpoint database");
        SyncPeerTransportAuthoritySupersessionRecordOptions ingress_authority_operator_supersession_options = ingress_authority_supersession_options;
        ingress_authority_operator_supersession_options.sqlite_path = ingress_operator_status_checkpoint_db.string();
        ingress_authority_operator_supersession_options.session_id = "session-main";
        ingress_authority_operator_supersession_options.updated_at_epoch = 235;
        SyncPeerTransportAuthoritySupersessionRecordResult ingress_authority_operator_supersession_result;
        require(record_sync_peer_transport_authority_supersession(ingress_authority_operator_supersession_options,
                                                                  ingress_authority_operator_supersession_result).ok,
                "peer transport authority supersession fixture seeds overlap bounds into operator checkpoint database");
        SyncPeerTransportIngressEnqueueOptions ingress_authority_operator_enqueue_options = ingress_enqueue_options;
        ingress_authority_operator_enqueue_options.sqlite_path = ingress_operator_status_checkpoint_db.string();
        ingress_authority_operator_enqueue_options.session_id = "session-main";
        ingress_authority_operator_enqueue_options.enqueue_now_epoch = 236;
        ingress_authority_operator_enqueue_options.require_authority_gate = true;
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_authority_operator_expired_envelope = ingress_bridge_envelope;
        ingress_authority_operator_expired_envelope.transport_envelope_idempotency_key = "sync-peer-transport-envelope:v1:" + sha256_hex("rev0750-operator-superseded-expired-envelope");
        SyncPeerTransportIngressEnqueueResult ingress_authority_operator_expired_enqueue;
        require(!enqueue_sync_peer_transport_ingress_envelope(ingress_authority_operator_enqueue_options,
                                                              ingress_authority_operator_expired_envelope,
                                                              ingress_bridge_chunk_bytes,
                                                              ingress_authority_operator_expired_enqueue).ok &&
                ingress_authority_operator_expired_enqueue.authority_decision.authority_lifecycle_state == "superseded-expired",
                "peer transport authority supersession fixture records operator-visible superseded-expired denial evidence");
        ingress_operator_status_options.scheduler_now_epoch = 237;
        SyncSessionCheckpointOperatorStatusResult ingress_operator_supersession_status;
        require(load_sync_session_checkpoint_operator_status(ingress_operator_status_options, ingress_operator_supersession_status).ok &&
                ingress_operator_supersession_status.peer_transport_authority_supersession_table_present &&
                ingress_operator_supersession_status.peer_transport_authority_supersession_rows == 1 &&
                ingress_operator_supersession_status.peer_transport_authority_superseded_expired_denied_rows == 1 &&
                ingress_operator_supersession_status.peer_transport_ingress_next_action == "inspect-peer-transport-authority-denials",
                "sync checkpoint operator status surfaces supersession residue before more peer ingress work");
        SyncPeerTransportIngressEnqueueOptions ingress_authority_enqueue_options = ingress_enqueue_options;
        ingress_authority_enqueue_options.sqlite_path = ingress_authority_gate_queue_db.string();
        ingress_authority_enqueue_options.enqueue_now_epoch = 214;
        ingress_authority_enqueue_options.require_authority_gate = true;
        SyncPeerTransportIngressEnqueueResult ingress_authority_enqueue_allowed;
        require(enqueue_sync_peer_transport_ingress_envelope(ingress_authority_enqueue_options,
                                                             ingress_bridge_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             ingress_authority_enqueue_allowed).ok &&
                ingress_authority_enqueue_allowed.row_inserted &&
                ingress_authority_enqueue_allowed.authority_decision.authority_allowed &&
                ingress_authority_enqueue_allowed.backpressure_checked,
                "peer transport ingress authority gate allows trusted transport before queue insert");
        ingress_authority_record_options.authority_status = "revoked";
        ingress_authority_record_options.updated_at_epoch = 215;
        ingress_authority_record_options.reason = "rev0748 selftest revoked compromised fixture key";
        SyncPeerTransportAuthorityRecordResult ingress_authority_revoke_result;
        require(record_sync_peer_transport_authority(ingress_authority_record_options, ingress_authority_revoke_result).ok &&
                ingress_authority_revoke_result.record_updated &&
                ingress_authority_revoke_result.authority_status == "revoked",
                "peer transport authority record can revoke an existing local peer/key status");
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_authority_denied_envelope = ingress_bridge_envelope;
        ingress_authority_denied_envelope.transport_envelope_idempotency_key = "sync-peer-transport-envelope:v1:" + sha256_hex("rev0748-authority-denied-envelope");
        ingress_authority_enqueue_options.enqueue_now_epoch = 216;
        SyncPeerTransportIngressEnqueueResult ingress_authority_enqueue_denied;
        require(!enqueue_sync_peer_transport_ingress_envelope(ingress_authority_enqueue_options,
                                                              ingress_authority_denied_envelope,
                                                              ingress_bridge_chunk_bytes,
                                                              ingress_authority_enqueue_denied).ok &&
                ingress_authority_enqueue_denied.authority_decision.authority_checked &&
                ingress_authority_enqueue_denied.authority_decision.authority_denied &&
                ingress_authority_enqueue_denied.authority_decision.denial_recorded &&
                ingress_authority_enqueue_denied.authority_decision.deny_reason == "peer transport authority revoked" &&
                !ingress_authority_enqueue_denied.row_inserted &&
                !ingress_authority_enqueue_denied.backpressure_checked,
                "peer transport ingress authority gate records revoked peer/key denial before queue pressure or insert");
        SyncPeerTransportIngressStatusResult ingress_authority_denial_status;
        SyncPeerTransportIngressStatusOptions ingress_authority_denial_status_options;
        ingress_authority_denial_status_options.sqlite_path = ingress_authority_gate_queue_db.string();
        ingress_authority_denial_status_options.session_id = "ingress-session";
        ingress_authority_denial_status_options.status_now_epoch = 217;
        require(load_sync_peer_transport_ingress_status(ingress_authority_denial_status_options, ingress_authority_denial_status).ok &&
                ingress_authority_denial_status.total_rows == 1 &&
                ingress_authority_denial_status.open_rows == 1 &&
                ingress_authority_denial_status.authority_denial_table_present &&
                ingress_authority_denial_status.authority_denied_rows == 1 &&
                ingress_authority_denial_status.authority_denied_bytes == ingress_bridge_peer_batch.total_bytes,
                "peer transport ingress status exposes revoked authority denials without counting them as queue rows");
        const fs::path ingress_authority_socket_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-authority-socket-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportAuthorityRecordOptions ingress_socket_authority_record = ingress_authority_record_options;
        ingress_socket_authority_record.sqlite_path = ingress_authority_socket_queue_db.string();
        ingress_socket_authority_record.authority_status = "revoked";
        ingress_socket_authority_record.updated_at_epoch = 218;
        SyncPeerTransportAuthorityRecordResult ingress_socket_authority_record_result;
        require(record_sync_peer_transport_authority(ingress_socket_authority_record, ingress_socket_authority_record_result).ok &&
                ingress_socket_authority_record_result.record_inserted,
                "peer transport authority gate can seed a revoked peer/key before local socket ingress");
        SyncPeerTransportLocalSocketIngressSubmitOptions ingress_authority_socket_options = ingress_local_socket_options;
        ingress_authority_socket_options.sqlite_path = ingress_authority_socket_queue_db.string();
        ingress_authority_socket_options.require_authority_gate = true;
        ingress_authority_socket_options.submit_now_epoch = 219;
        SyncPeerTransportLocalSocketIngressSubmitResult ingress_authority_socket_result;
        require(!submit_sync_peer_transport_local_socket_ingress_fixture(ingress_authority_socket_options,
                                                                        ingress_bridge_envelope,
                                                                        ingress_bridge_chunk_bytes,
                                                                        ingress_authority_socket_result).ok &&
                ingress_authority_socket_result.socket_pair_created &&
                ingress_authority_socket_result.frame_received &&
                ingress_authority_socket_result.frame_digest_checked &&
                ingress_authority_socket_result.authority_decision.authority_denied &&
                !ingress_authority_socket_result.row_inserted,
                "peer transport local socket fixture propagates revoked authority denial after receiving socket bytes but before queue insert");
        SyncPeerTransportIngressProcessOptions ingress_process_options;
        ingress_process_options.sqlite_path = ingress_bridge_queue_db.string();
        ingress_process_options.session_id = "ingress-session";
        ingress_process_options.worker_id = "worker-alpha";
        ingress_process_options.worker_lease_id = "lease-alpha";
        ingress_process_options.process_now_epoch = 220;
        ingress_process_options.lease_duration_seconds = 5;
        ingress_process_options.retry_backoff_seconds = 15;
        ingress_process_options.max_attempts = 2;
        SyncPeerTransportEnvelopeVerifyOptions ingress_wrong_verify_options;
        ingress_wrong_verify_options.expected_transport_instance_id = "transport-alpha";
        ingress_wrong_verify_options.expected_transport_key_id = "transport-key-alpha";
        ingress_wrong_verify_options.shared_secret = "rev0744-selftest-wrong-transport-secret";
        ingress_wrong_verify_options.expected_peer_id = "peer-alpha";
        ingress_wrong_verify_options.expected_peer_session_id = "session-one";
        ingress_wrong_verify_options.verify_now_epoch = 220;
        ingress_wrong_verify_options.max_response_count = 1;
        ingress_wrong_verify_options.max_total_bytes = ingress_bridge_peer_batch.total_bytes;
        ingress_wrong_verify_options.max_chunk_bytes = 5;
        const fs::path ingress_authority_legacy_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-transport-authority-legacy-" + std::to_string(selftest_ticks) + ".sqlite");
        SyncPeerTransportIngressEnqueueOptions ingress_authority_legacy_enqueue_options = ingress_enqueue_options;
        ingress_authority_legacy_enqueue_options.sqlite_path = ingress_authority_legacy_queue_db.string();
        ingress_authority_legacy_enqueue_options.enqueue_now_epoch = 218;
        SyncPeerTransportIngressEnqueueResult ingress_authority_legacy_enqueue_result;
        require(enqueue_sync_peer_transport_ingress_envelope(ingress_authority_legacy_enqueue_options,
                                                             ingress_bridge_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             ingress_authority_legacy_enqueue_result).ok &&
                ingress_authority_legacy_enqueue_result.row_inserted,
                "peer transport authority legacy fixture can queue a row before authority enforcement is enabled");
        SyncPeerTransportAuthorityRecordOptions ingress_authority_legacy_revoke_options = ingress_authority_record_options;
        ingress_authority_legacy_revoke_options.sqlite_path = ingress_authority_legacy_queue_db.string();
        ingress_authority_legacy_revoke_options.authority_status = "revoked";
        ingress_authority_legacy_revoke_options.updated_at_epoch = 219;
        ingress_authority_legacy_revoke_options.reason = "rev0748 selftest revoke legacy queued ingress";
        SyncPeerTransportAuthorityRecordResult ingress_authority_legacy_revoke_result;
        require(record_sync_peer_transport_authority(ingress_authority_legacy_revoke_options, ingress_authority_legacy_revoke_result).ok &&
                ingress_authority_legacy_revoke_result.record_inserted,
                "peer transport authority gate can revoke a peer/key after a legacy row was queued");
        SyncPeerTransportIngressProcessOptions ingress_authority_legacy_process_options = ingress_process_options;
        ingress_authority_legacy_process_options.sqlite_path = ingress_authority_legacy_queue_db.string();
        ingress_authority_legacy_process_options.process_now_epoch = 220;
        ingress_authority_legacy_process_options.require_authority_gate = true;
        SyncPeerTransportIngressProcessResult ingress_authority_legacy_process_result;
        require(!process_sync_peer_transport_ingress_envelope(ingress_authority_legacy_process_options,
                                                              ingress_wrong_verify_options,
                                                              ingress_bridge_remote,
                                                              ingress_bridge_apply_plan.entries[0],
                                                              ingress_bridge_inspection,
                                                              ingress_bridge_request_options,
                                                              ingress_bridge_request,
                                                              ingress_bridge_schedule,
                                                              ingress_bridge_schedule.assignments[0],
                                                              ingress_bridge_envelope,
                                                              ingress_bridge_chunk_bytes,
                                                              chunk_write_options,
                                                              ingress_authority_legacy_process_result).ok &&
                ingress_authority_legacy_process_result.authority_decision.authority_denied &&
                ingress_authority_legacy_process_result.abandoned &&
                ingress_authority_legacy_process_result.state_after == "abandoned" &&
                !ingress_authority_legacy_process_result.acceptance_attempted &&
                ingress_authority_legacy_process_result.attempts_after_claim == 0,
                "peer transport ingress authority gate abandons a revoked legacy row before acceptance or retry debt");
        SyncPeerTransportIngressStatusResult ingress_authority_legacy_status;
        SyncPeerTransportIngressStatusOptions ingress_authority_legacy_status_options;
        ingress_authority_legacy_status_options.sqlite_path = ingress_authority_legacy_queue_db.string();
        ingress_authority_legacy_status_options.session_id = "ingress-session";
        ingress_authority_legacy_status_options.status_now_epoch = 221;
        require(load_sync_peer_transport_ingress_status(ingress_authority_legacy_status_options, ingress_authority_legacy_status).ok &&
                ingress_authority_legacy_status.abandoned_rows == 1 &&
                ingress_authority_legacy_status.authority_denied_rows == 1 &&
                ingress_authority_legacy_status.open_rows == 0 &&
                ingress_authority_legacy_status.total_attempts == 0,
                "peer transport ingress status exposes authority-abandoned legacy rows without retry attempts");
        SyncPeerTransportIngressProcessResult ingress_wrong_process_result;
        require(!process_sync_peer_transport_ingress_envelope(ingress_process_options,
                                                              ingress_wrong_verify_options,
                                                              ingress_bridge_remote,
                                                              ingress_bridge_apply_plan.entries[0],
                                                              ingress_bridge_inspection,
                                                              ingress_bridge_request_options,
                                                              ingress_bridge_request,
                                                              ingress_bridge_schedule,
                                                              ingress_bridge_schedule.assignments[0],
                                                              ingress_bridge_envelope,
                                                              ingress_bridge_chunk_bytes,
                                                              chunk_write_options,
                                                              ingress_wrong_process_result).ok &&
                ingress_wrong_process_result.claimed &&
                ingress_wrong_process_result.payload_digest_checked &&
                ingress_wrong_process_result.acceptance_attempted &&
                ingress_wrong_process_result.retry_scheduled &&
                ingress_wrong_process_result.claim_generation_id.starts_with(
                    "sync-peer-transport-ingress-claim:v1:") &&
                ingress_wrong_process_result.state_after == "failed" &&
                ingress_wrong_process_result.retry_at_epoch == 235,
                "peer transport ingress process records authenticated acceptance failure as retryable durable state");
        SyncPeerTransportIngressStatusResult ingress_failed_status;
        ingress_status_options.status_now_epoch = 221;
        require(load_sync_peer_transport_ingress_status(ingress_status_options, ingress_failed_status).ok &&
                ingress_failed_status.failed_rows == 1 &&
                ingress_failed_status.retry_waiting_rows == 1 &&
                ingress_failed_status.total_attempts == 1,
                "peer transport ingress status exposes retry backoff after failed acceptance");
        SyncPeerTransportIngressProcessOptions ingress_early_retry_options = ingress_process_options;
        ingress_early_retry_options.process_now_epoch = 230;
        SyncPeerTransportEnvelopeVerifyOptions ingress_early_retry_verify_options = ingress_wrong_verify_options;
        ingress_early_retry_verify_options.verify_now_epoch = 230;
        SyncPeerTransportIngressProcessResult ingress_early_retry_result;
        require(process_sync_peer_transport_ingress_envelope(ingress_early_retry_options,
                                                             ingress_early_retry_verify_options,
                                                             ingress_bridge_remote,
                                                             ingress_bridge_apply_plan.entries[0],
                                                             ingress_bridge_inspection,
                                                             ingress_bridge_request_options,
                                                             ingress_bridge_request,
                                                             ingress_bridge_schedule,
                                                             ingress_bridge_schedule.assignments[0],
                                                             ingress_bridge_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             chunk_write_options,
                                                             ingress_early_retry_result).ok &&
                ingress_early_retry_result.retry_backoff_deferred &&
                !ingress_early_retry_result.acceptance_attempted,
                "peer transport ingress process does not retry before retry_at opens");
        SyncPeerTransportEnvelopeVerifyOptions ingress_correct_verify_options = ingress_wrong_verify_options;
        ingress_correct_verify_options.shared_secret = ingress_bridge_build_options.shared_secret;
        ingress_correct_verify_options.verify_now_epoch = 240;
        SyncPeerTransportIngressProcessOptions ingress_retry_options = ingress_process_options;
        ingress_retry_options.process_now_epoch = 240;
        SyncPeerTransportIngressProcessResult ingress_retry_result;
        require(process_sync_peer_transport_ingress_durable_payload(
                    ingress_retry_options,
                    ingress_correct_verify_options,
                    ingress_bridge_remote,
                    ingress_bridge_apply_plan.entries[0],
                    ingress_bridge_inspection,
                    ingress_bridge_request_options,
                    ingress_bridge_request,
                    ingress_bridge_schedule,
                    ingress_bridge_schedule.assignments[0],
                    ingress_bridge_envelope.transport_envelope_idempotency_key,
                    chunk_write_options,
                    ingress_retry_result).ok &&
                ingress_retry_result.claimed &&
                ingress_retry_result.durable_payload_checked &&
                ingress_retry_result.durable_payload_matches_submission &&
                ingress_retry_result.durable_payload_claim_snapshot_checked &&
                ingress_retry_result.durable_payload_completion_snapshot_checked &&
                ingress_retry_result.acceptance_completed &&
                ingress_retry_result.claim_generation_id.starts_with(
                    "sync-peer-transport-ingress-claim:v1:") &&
                ingress_retry_result.claim_generation_id !=
                    ingress_wrong_process_result.claim_generation_id &&
                ingress_retry_result.state_after == "completed" &&
                ingress_retry_result.acceptance.peer_batch_acceptance_completed,
                "peer transport ingress restart worker reconstructs the exact durable frame by key and drains it into receipt-backed staging without sender-owned objects");
        SyncPeerTransportIngressStatusResult ingress_completed_status;
        ingress_status_options.status_now_epoch = 241;
        require(load_sync_peer_transport_ingress_status(ingress_status_options, ingress_completed_status).ok &&
                ingress_completed_status.completed_rows == 1 &&
                ingress_completed_status.failed_rows == 0 &&
                ingress_completed_status.total_attempts == 2,
                "peer transport ingress status exposes completed retry drainage");
        SyncPeerTransportIngressProcessResult ingress_completed_replay_result;
        require(process_sync_peer_transport_ingress_envelope(ingress_retry_options,
                                                             ingress_correct_verify_options,
                                                             ingress_bridge_remote,
                                                             ingress_bridge_apply_plan.entries[0],
                                                             ingress_bridge_inspection,
                                                             ingress_bridge_request_options,
                                                             ingress_bridge_request,
                                                             ingress_bridge_schedule,
                                                             ingress_bridge_schedule.assignments[0],
                                                             ingress_bridge_envelope,
                                                             ingress_bridge_chunk_bytes,
                                                             chunk_write_options,
                                                             ingress_completed_replay_result).ok &&
                ingress_completed_replay_result.already_completed &&
                !ingress_completed_replay_result.acceptance_attempted,
                "peer transport ingress completed rows replay as non-mutating observations");

        // Crash-window reconciliation proof: receipt-backed acceptance commits filesystem
        // evidence before queue completion. A restart after the claim lease and transport
        // envelope expire must complete from the original claim-time evidence rather than
        // abandon a final-attempt row or rewrite already accepted bytes.
        const std::string ingress_recovery_body = "proof";
        SyncManifestEntry ingress_recovery_remote =
            remote_file_entry_for_body("docs/ingress-recovery.txt", ingress_recovery_body, 38);
        SyncManifestDiffPlan ingress_recovery_diff_plan;
        require(build_sync_manifest_diff_plan(
                    empty_local,
                    folder_manifest("folder-alpha", "device-bravo", 38, {ingress_recovery_remote}),
                    ingress_recovery_diff_plan).ok,
                "peer transport ingress recovery fixture builds a remote-only manifest diff");
        SyncLocalApplyPlan ingress_recovery_apply_plan;
        require(build_sync_local_apply_plan(ingress_recovery_diff_plan,
                                            apply_options,
                                            ingress_recovery_apply_plan).ok &&
                ingress_recovery_apply_plan.entries.size() == 1 &&
                ingress_recovery_apply_plan.entries[0].local_action ==
                    SyncLocalApplyAction::StageRemoteFile,
                "peer transport ingress recovery fixture binds a receipt-backed staging path");
        SyncStagedTransferInspectionResult ingress_recovery_inspection;
        require(inspect_sync_staged_transfer(ingress_recovery_remote,
                                            ingress_recovery_apply_plan.entries[0],
                                            inspection_options,
                                            ingress_recovery_inspection).ok &&
                ingress_recovery_inspection.missing_chunks.size() == 1 &&
                !ingress_recovery_inspection.staged_file_exists,
                "peer transport ingress recovery fixture starts without staged or receipt evidence");
        SyncChunkRequestPlanOptions ingress_recovery_request_options;
        ingress_recovery_request_options.max_chunks_per_request = 1;
        SyncChunkRequestPlanResult ingress_recovery_request;
        require(build_sync_chunk_request_plan(ingress_recovery_remote,
                                             ingress_recovery_apply_plan.entries[0],
                                             ingress_recovery_inspection,
                                             ingress_recovery_request_options,
                                             ingress_recovery_request).ok &&
                ingress_recovery_request.selected_chunks == 1,
                "peer transport ingress recovery fixture selects its one missing chunk");
        SyncPeerChunkAvailability ingress_recovery_peer;
        ingress_recovery_peer.peer_id = "peer-alpha";
        ingress_recovery_peer.peer_session_id = "session-one";
        ingress_recovery_peer.max_chunks = 1;
        ingress_recovery_peer.max_bytes = ingress_recovery_remote.chunks[0].length;
        ingress_recovery_peer.available_chunks = {ingress_recovery_remote.chunks[0]};
        SyncPeerChunkScheduleResult ingress_recovery_schedule;
        require(build_sync_peer_chunk_schedule(ingress_recovery_remote,
                                               ingress_recovery_apply_plan.entries[0],
                                               ingress_recovery_request,
                                               {ingress_recovery_peer},
                                               ingress_recovery_schedule).ok &&
                ingress_recovery_schedule.assignments.size() == 1,
                "peer transport ingress recovery fixture binds one peer assignment");
        SyncPeerChunkResponseBatchEnvelope ingress_recovery_peer_batch;
        require(build_sync_peer_chunk_response_batch_envelope(
                    ingress_recovery_remote,
                    ingress_recovery_apply_plan.entries[0],
                    ingress_recovery_request,
                    ingress_recovery_schedule,
                    ingress_recovery_schedule.assignments[0],
                    ingress_recovery_schedule.assignments[0].chunks,
                    ingress_recovery_peer_batch).ok,
                "peer transport ingress recovery fixture builds peer response evidence");
        SyncPeerTransportEnvelopeBuildOptions ingress_recovery_build_options;
        ingress_recovery_build_options.transport_instance_id = "transport-alpha";
        ingress_recovery_build_options.transport_key_id = "transport-key-alpha";
        ingress_recovery_build_options.shared_secret =
            "rev0758-receipt-first-crash-reconciliation-shared-secret";
        ingress_recovery_build_options.issued_at_epoch = 300;
        ingress_recovery_build_options.expires_at_epoch = 330;
        ingress_recovery_build_options.max_response_count = 1;
        ingress_recovery_build_options.max_total_bytes =
            ingress_recovery_peer_batch.total_bytes;
        ingress_recovery_build_options.max_chunk_bytes =
            ingress_recovery_remote.chunks[0].length;
        SyncPeerTransportBoundChunkResponseBatchEnvelope ingress_recovery_envelope;
        require(build_sync_peer_transport_bound_chunk_response_batch_envelope(
                    ingress_recovery_build_options,
                    ingress_recovery_peer_batch,
                    ingress_recovery_envelope).ok,
                "peer transport ingress recovery fixture authenticates transport evidence");
        const std::vector<std::string> ingress_recovery_chunk_bytes = {
            chunk_bytes_for_body(ingress_recovery_body,
                                 ingress_recovery_schedule.assignments[0].chunks[0])};
        const fs::path ingress_recovery_queue_db =
            fs::temp_directory_path() /
            ("anonsync-sync-peer-transport-ingress-recovery-" +
             std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(ingress_recovery_queue_db, apply_cleanup_ec);
        fs::remove(fs::path(ingress_recovery_queue_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(ingress_recovery_queue_db.string() + "-shm"), apply_cleanup_ec);
        SyncPeerTransportIngressEnqueueOptions ingress_recovery_enqueue_options;
        ingress_recovery_enqueue_options.sqlite_path = ingress_recovery_queue_db.string();
        ingress_recovery_enqueue_options.session_id = "ingress-recovery-session";
        ingress_recovery_enqueue_options.enqueue_now_epoch = 301;
        ingress_recovery_enqueue_options.max_attempts = 1;
        ingress_recovery_enqueue_options.retry_backoff_seconds = 15;
        SyncPeerTransportIngressEnqueueResult ingress_recovery_enqueue_result;
        require(enqueue_sync_peer_transport_ingress_envelope(
                    ingress_recovery_enqueue_options,
                    ingress_recovery_envelope,
                    ingress_recovery_chunk_bytes,
                    ingress_recovery_enqueue_result).ok &&
                ingress_recovery_enqueue_result.row_inserted &&
                ingress_recovery_enqueue_result.max_attempts == 1,
                "peer transport ingress recovery fixture queues a final-attempt envelope");

        SyncPeerTransportIngressProcessOptions ingress_recovery_process_options;
        ingress_recovery_process_options.sqlite_path = ingress_recovery_queue_db.string();
        ingress_recovery_process_options.session_id = "ingress-recovery-session";
        ingress_recovery_process_options.worker_id = "worker-crash-window";
        ingress_recovery_process_options.worker_lease_id = "lease-crash-window";
        ingress_recovery_process_options.process_now_epoch = 305;
        ingress_recovery_process_options.lease_duration_seconds = 5;
        ingress_recovery_process_options.retry_backoff_seconds = 15;
        ingress_recovery_process_options.max_attempts = 1;
        ingress_recovery_process_options.controlled_abort_after_acceptance_before_completion = true;
        SyncPeerTransportEnvelopeVerifyOptions ingress_recovery_verify_options;
        ingress_recovery_verify_options.expected_transport_instance_id = "transport-alpha";
        ingress_recovery_verify_options.expected_transport_key_id = "transport-key-alpha";
        ingress_recovery_verify_options.shared_secret =
            ingress_recovery_build_options.shared_secret;
        ingress_recovery_verify_options.expected_peer_id = "peer-alpha";
        ingress_recovery_verify_options.expected_peer_session_id = "session-one";
        ingress_recovery_verify_options.verify_now_epoch = 304;
        ingress_recovery_verify_options.max_response_count = 1;
        ingress_recovery_verify_options.max_total_bytes =
            ingress_recovery_peer_batch.total_bytes;
        ingress_recovery_verify_options.max_chunk_bytes =
            ingress_recovery_remote.chunks[0].length;
        SyncPeerTransportIngressProcessResult ingress_recovery_clock_mismatch_result;
        require(!process_sync_peer_transport_ingress_envelope(
                    ingress_recovery_process_options,
                    ingress_recovery_verify_options,
                    ingress_recovery_remote,
                    ingress_recovery_apply_plan.entries[0],
                    ingress_recovery_inspection,
                    ingress_recovery_request_options,
                    ingress_recovery_request,
                    ingress_recovery_schedule,
                    ingress_recovery_schedule.assignments[0],
                    ingress_recovery_envelope,
                    ingress_recovery_chunk_bytes,
                    chunk_write_options,
                    ingress_recovery_clock_mismatch_result).ok &&
                !ingress_recovery_clock_mismatch_result.row_found &&
                !ingress_recovery_clock_mismatch_result.claimed &&
                !fs::exists(fs::path(
                    ingress_recovery_apply_plan.entries[0].absolute_staging_path)),
                "peer transport ingress refuses to claim when transport and durable claim timestamps differ");
        SyncPeerTransportIngressStatusOptions ingress_recovery_preclaim_status_options;
        ingress_recovery_preclaim_status_options.sqlite_path =
            ingress_recovery_queue_db.string();
        ingress_recovery_preclaim_status_options.session_id =
            "ingress-recovery-session";
        ingress_recovery_preclaim_status_options.status_now_epoch = 305;
        SyncPeerTransportIngressStatusResult ingress_recovery_preclaim_status;
        require(load_sync_peer_transport_ingress_status(
                    ingress_recovery_preclaim_status_options,
                    ingress_recovery_preclaim_status).ok &&
                ingress_recovery_preclaim_status.queued_rows == 1 &&
                ingress_recovery_preclaim_status.total_attempts == 0,
                "peer transport ingress timestamp mismatch leaves queue state and retry debt untouched");

        ingress_recovery_verify_options.verify_now_epoch = 305;
        SyncPeerTransportIngressProcessResult ingress_recovery_crash_result;
        require(!process_sync_peer_transport_ingress_envelope(
                    ingress_recovery_process_options,
                    ingress_recovery_verify_options,
                    ingress_recovery_remote,
                    ingress_recovery_apply_plan.entries[0],
                    ingress_recovery_inspection,
                    ingress_recovery_request_options,
                    ingress_recovery_request,
                    ingress_recovery_schedule,
                    ingress_recovery_schedule.assignments[0],
                    ingress_recovery_envelope,
                    ingress_recovery_chunk_bytes,
                    chunk_write_options,
                    ingress_recovery_crash_result).ok &&
                ingress_recovery_crash_result.claimed &&
                ingress_recovery_crash_result.acceptance_attempted &&
                ingress_recovery_crash_result.acceptance_completed &&
                ingress_recovery_crash_result.controlled_abort_after_acceptance_before_completion &&
                ingress_recovery_crash_result.state_after == "claimed" &&
                ingress_recovery_crash_result.claim_generation_id.starts_with(
                    "sync-peer-transport-ingress-claim:v1:") &&
                ingress_recovery_crash_result.attempts_after_claim == 1 &&
                ingress_recovery_crash_result.acceptance.peer_batch_acceptance.accepted_chunks.size() == 1 &&
                ingress_recovery_crash_result.sqlite_write_contention.write_lock_attempts == 1 &&
                ingress_recovery_crash_result.sqlite_write_contention.write_locks_acquired == 1,
                "peer transport ingress crash hook leaves a final-attempt claim after durable receipt-backed acceptance");
        const fs::path ingress_recovery_staged_path =
            ingress_recovery_apply_plan.entries[0].absolute_staging_path;
        const fs::path ingress_recovery_receipt_path =
            ingress_recovery_crash_result.acceptance.peer_batch_acceptance.accepted_chunks[0]
                .absolute_receipt_path;
        require(fs::exists(ingress_recovery_staged_path) &&
                fs::exists(ingress_recovery_receipt_path) &&
                read_binary_fixture(ingress_recovery_staged_path) == ingress_recovery_body,
                "peer transport ingress crash window retains matching staged bytes and a durable receipt");
        const std::string ingress_recovery_staged_hash_before =
            sha256_hex(read_binary_fixture(ingress_recovery_staged_path));
        const std::string ingress_recovery_receipt_hash_before =
            sha256_hex(read_binary_fixture(ingress_recovery_receipt_path));
        SyncPeerTransportIngressStatusOptions ingress_recovery_claimed_status_options =
            ingress_recovery_preclaim_status_options;
        ingress_recovery_claimed_status_options.status_now_epoch = 306;
        SyncPeerTransportIngressStatusResult ingress_recovery_claimed_status;
        require(load_sync_peer_transport_ingress_status(
                    ingress_recovery_claimed_status_options,
                    ingress_recovery_claimed_status).ok &&
                ingress_recovery_claimed_status.open_rows == 1 &&
                ingress_recovery_claimed_status.claimed_rows == 1 &&
                ingress_recovery_claimed_status.completed_rows == 0 &&
                ingress_recovery_claimed_status.total_attempts == 1,
                "peer transport ingress crash window is durably visible before lease expiry");

        SyncPeerTransportIngressProcessOptions ingress_recovery_restart_options =
            ingress_recovery_process_options;
        ingress_recovery_restart_options.worker_id = "worker-restart";
        ingress_recovery_restart_options.worker_lease_id = "lease-restart";
        ingress_recovery_restart_options.process_now_epoch = 400;
        ingress_recovery_restart_options.controlled_abort_after_acceptance_before_completion = false;
        SyncPeerTransportEnvelopeVerifyOptions ingress_recovery_restart_verify_options =
            ingress_recovery_verify_options;
        ingress_recovery_restart_verify_options.verify_now_epoch = 400;
        SyncPeerTransportIngressProcessResult ingress_recovery_restart_result;
        require(process_sync_peer_transport_ingress_envelope(
                    ingress_recovery_restart_options,
                    ingress_recovery_restart_verify_options,
                    ingress_recovery_remote,
                    ingress_recovery_apply_plan.entries[0],
                    ingress_recovery_inspection,
                    ingress_recovery_request_options,
                    ingress_recovery_request,
                    ingress_recovery_schedule,
                    ingress_recovery_schedule.assignments[0],
                    ingress_recovery_envelope,
                    ingress_recovery_chunk_bytes,
                    chunk_write_options,
                    ingress_recovery_restart_result).ok &&
                ingress_recovery_restart_result.row_found &&
                ingress_recovery_restart_result.payload_digest_checked &&
                ingress_recovery_restart_result.expired_claim_reconciliation_attempted &&
                ingress_recovery_restart_result.expired_claim_reconciliation_snapshot_matched &&
                !ingress_recovery_restart_result.expired_claim_reconciliation_snapshot_changed &&
                ingress_recovery_restart_result.expired_claim_completed_from_receipts &&
                !ingress_recovery_restart_result.expired_claim_reconciliation_blocked &&
                !ingress_recovery_restart_result.operator_review_required &&
                !ingress_recovery_restart_result.claimed &&
                !ingress_recovery_restart_result.acceptance_attempted &&
                ingress_recovery_restart_result.acceptance_completed &&
                ingress_recovery_restart_result.state_after == "completed" &&
                ingress_recovery_restart_result.claim_generation_id ==
                    ingress_recovery_crash_result.claim_generation_id &&
                ingress_recovery_restart_result.receipt_evidence_state == "matching-all" &&
                ingress_recovery_restart_result.expired_claim_recovery_action ==
                    "complete-from-receipts" &&
                ingress_recovery_restart_result.expected_receipts == 1 &&
                ingress_recovery_restart_result.matching_receipts == 1 &&
                ingress_recovery_restart_result.missing_receipts == 0 &&
                ingress_recovery_restart_result.conflicting_receipts == 0 &&
                ingress_recovery_restart_result.attempts_after_claim == 1 &&
                ingress_recovery_restart_result.acceptance.transport_mac_checked &&
                ingress_recovery_restart_result.acceptance.peer_batch_acceptance_completed &&
                ingress_recovery_restart_result.sqlite_write_contention.write_lock_attempts == 1 &&
                ingress_recovery_restart_result.sqlite_write_contention.write_locks_acquired == 1,
                "peer transport ingress restart completes an expired final-attempt claim from exact receipts after envelope expiry without reaccepting bytes");
        require(sha256_hex(read_binary_fixture(ingress_recovery_staged_path)) ==
                    ingress_recovery_staged_hash_before &&
                sha256_hex(read_binary_fixture(ingress_recovery_receipt_path)) ==
                    ingress_recovery_receipt_hash_before,
                "peer transport ingress receipt-first recovery leaves accepted staged and receipt bytes unchanged");
        SyncPeerTransportIngressStatusOptions ingress_recovery_completed_status_options =
            ingress_recovery_preclaim_status_options;
        ingress_recovery_completed_status_options.status_now_epoch = 401;
        SyncPeerTransportIngressStatusResult ingress_recovery_completed_status;
        require(load_sync_peer_transport_ingress_status(
                    ingress_recovery_completed_status_options,
                    ingress_recovery_completed_status).ok &&
                ingress_recovery_completed_status.total_rows == 1 &&
                ingress_recovery_completed_status.open_rows == 0 &&
                ingress_recovery_completed_status.completed_rows == 1 &&
                ingress_recovery_completed_status.abandoned_rows == 0 &&
                ingress_recovery_completed_status.expired_claim_rows == 0 &&
                ingress_recovery_completed_status.total_attempts == 1,
                "peer transport ingress receipt-first recovery closes queue residue without retry debt or abandonment");
        fs::remove(ingress_recovery_queue_db, apply_cleanup_ec);
        fs::remove(fs::path(ingress_recovery_queue_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(ingress_recovery_queue_db.string() + "-shm"), apply_cleanup_ec);

        SyncPeerTransportIngressRetentionOptions ingress_completed_retention_options;
        ingress_completed_retention_options.sqlite_path = ingress_bridge_queue_db.string();
        ingress_completed_retention_options.session_id = "ingress-session";
        ingress_completed_retention_options.operator_id = "operator-alpha";
        ingress_completed_retention_options.reason = "rev0749 selftest drain completed peer ingress residue";
        ingress_completed_retention_options.retention_now_epoch = 260;
        ingress_completed_retention_options.completed_older_than_epoch = 240;
        ingress_completed_retention_options.max_completed_rows = 1;
        ingress_completed_retention_options.dry_run = true;
        SyncPeerTransportIngressRetentionResult ingress_completed_retention_dry_run;
        require(drain_sync_peer_transport_ingress_retention(ingress_completed_retention_options,
                                                            ingress_completed_retention_dry_run).ok &&
                ingress_completed_retention_dry_run.dry_run &&
                ingress_completed_retention_dry_run.completed_eligible_rows == 1 &&
                ingress_completed_retention_dry_run.completed_rows_drained == 1 &&
                ingress_completed_retention_dry_run.audit_events_written == 0,
                "peer transport ingress retention dry-run selects completed rows without writing audit or deleting rows");
        SyncPeerTransportIngressStatusResult ingress_completed_retention_dry_status;
        require(load_sync_peer_transport_ingress_status(ingress_status_options, ingress_completed_retention_dry_status).ok &&
                ingress_completed_retention_dry_status.completed_rows == 1 &&
                ingress_completed_retention_dry_status.terminal_retention_candidate_rows == 1 &&
                ingress_completed_retention_dry_status.retention_event_rows == 0,
                "peer transport ingress status distinguishes completed rows as retention candidates before drain");
        const fs::path ingress_completed_cli_report_path = fs::temp_directory_path() / ("anonsync-sync-peer-ingress-retention-cli-dry-run-" + std::to_string(selftest_ticks) + ".json");
        fs::remove(ingress_completed_cli_report_path, apply_cleanup_ec);
        int ingress_completed_cli_dry_run_rc = run_sync_peer_ingress_retention_command(ingress_bridge_queue_db.string(),
                                                                                       "ingress-session",
                                                                                       "operator-alpha",
                                                                                       "rev0752 selftest inspect completed peer ingress residue",
                                                                                       260,
                                                                                       240,
                                                                                       0,
                                                                                       0,
                                                                                       1,
                                                                                       0,
                                                                                       0,
                                                                                       true,
                                                                                       ingress_completed_cli_report_path.string());
        Json ingress_completed_cli_report = load_json(ingress_completed_cli_report_path.string());
        require(ingress_completed_cli_dry_run_rc == 0 &&
                ingress_completed_cli_report.at("format").str() == "anonsync-sync-peer-ingress-retention-operator-report-v2" &&
                ingress_completed_cli_report.at("ok").boolean(false) &&
                ingress_completed_cli_report.at("input").at("dry_run").boolean(false) &&
                ingress_completed_cli_report.at("input").at("sqlite_busy_timeout_ms").integer() ==
                    static_cast<long long>(kSyncPeerTransportDefaultSqliteBusyTimeoutMs) &&
                ingress_completed_cli_report.at("result").at("completed_eligible_rows").integer() == 1 &&
                ingress_completed_cli_report.at("result").at("audit_events_written").integer(-1) == 0 &&
                !ingress_completed_cli_report.at("result").at("sqlite_write_contention").at("busy_handler_installed").boolean(false) &&
                ingress_completed_cli_report.at("result").at("sqlite_write_contention").at("write_lock_attempts").integer() == 0,
                "peer transport ingress retention CLI emits dry-run JSON without writing audit or deleting completed rows");
        SyncPeerTransportIngressStatusResult ingress_completed_cli_dry_status;
        require(load_sync_peer_transport_ingress_status(ingress_status_options, ingress_completed_cli_dry_status).ok &&
                ingress_completed_cli_dry_status.completed_rows == 1 &&
                ingress_completed_cli_dry_status.retention_event_rows == 0,
                "peer transport ingress retention CLI dry-run is read-only against completed residue");
        ingress_completed_retention_options.dry_run = false;
        SyncPeerTransportIngressRetentionResult ingress_completed_retention_result;
        require(drain_sync_peer_transport_ingress_retention(ingress_completed_retention_options,
                                                            ingress_completed_retention_result).ok &&
                ingress_completed_retention_result.retention_completed &&
                ingress_completed_retention_result.completed_rows_drained == 1 &&
                ingress_completed_retention_result.ingress_rows_drained == 1 &&
                ingress_completed_retention_result.audit_events_written == 1,
                "peer transport ingress retention drains completed terminal rows with durable audit evidence");
        SyncPeerTransportIngressStatusResult ingress_completed_retention_status;
        require(load_sync_peer_transport_ingress_status(ingress_status_options, ingress_completed_retention_status).ok &&
                ingress_completed_retention_status.total_rows == 0 &&
                ingress_completed_retention_status.retention_event_table_present &&
                ingress_completed_retention_status.retention_event_rows == 1 &&
                ingress_completed_retention_status.retention_drained_ingress_rows == 1 &&
                ingress_completed_retention_status.retention_drained_ingress_bytes == ingress_bridge_peer_batch.total_bytes,
                "peer transport ingress status preserves retention audit after completed row drainage");
        SyncPeerTransportIngressRetentionResult ingress_completed_retention_replay;
        require(drain_sync_peer_transport_ingress_retention(ingress_completed_retention_options,
                                                            ingress_completed_retention_replay).ok &&
                ingress_completed_retention_replay.retention_completed &&
                ingress_completed_retention_replay.retention_noop &&
                ingress_completed_retention_replay.audit_events_written == 0,
                "peer transport ingress retention is idempotent after completed rows are already drained");

        SyncPeerTransportIngressRetentionOptions ingress_legacy_retention_options;
        ingress_legacy_retention_options.sqlite_path = ingress_authority_legacy_queue_db.string();
        ingress_legacy_retention_options.session_id = "ingress-session";
        ingress_legacy_retention_options.operator_id = "operator-alpha";
        ingress_legacy_retention_options.reason = "rev0749 selftest drain abandoned and denied peer ingress residue";
        ingress_legacy_retention_options.retention_now_epoch = 260;
        ingress_legacy_retention_options.abandoned_older_than_epoch = 220;
        ingress_legacy_retention_options.authority_denial_older_than_epoch = 220;
        ingress_legacy_retention_options.max_abandoned_rows = 1;
        ingress_legacy_retention_options.max_authority_denial_rows = 1;
        const fs::path ingress_legacy_cli_queue_db = fs::temp_directory_path() / ("anonsync-sync-peer-ingress-retention-cli-apply-" + std::to_string(selftest_ticks) + ".sqlite");
        fs::remove(ingress_legacy_cli_queue_db, apply_cleanup_ec);
        fs::remove(fs::path(ingress_legacy_cli_queue_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(ingress_legacy_cli_queue_db.string() + "-shm"), apply_cleanup_ec);
        sqlite_backup_file_or_throw(ingress_authority_legacy_queue_db,
                                    ingress_legacy_cli_queue_db,
                                    "peer ingress retention CLI apply fixture");
        const fs::path ingress_legacy_cli_report_path = fs::temp_directory_path() / ("anonsync-sync-peer-ingress-retention-cli-apply-" + std::to_string(selftest_ticks) + ".json");
        fs::remove(ingress_legacy_cli_report_path, apply_cleanup_ec);
        int ingress_legacy_cli_apply_rc = run_sync_peer_ingress_retention_command(ingress_legacy_cli_queue_db.string(),
                                                                                  "ingress-session",
                                                                                  "operator-alpha",
                                                                                  "rev0752 selftest apply abandoned and denied peer ingress residue",
                                                                                  260,
                                                                                  0,
                                                                                  220,
                                                                                  220,
                                                                                  0,
                                                                                  1,
                                                                                  1,
                                                                                  false,
                                                                                  ingress_legacy_cli_report_path.string());
        Json ingress_legacy_cli_report = load_json(ingress_legacy_cli_report_path.string());
        require(ingress_legacy_cli_apply_rc == 0 &&
                ingress_legacy_cli_report.at("format").str() == "anonsync-sync-peer-ingress-retention-operator-report-v2" &&
                ingress_legacy_cli_report.at("ok").boolean(false) &&
                ingress_legacy_cli_report.at("input").at("sqlite_busy_timeout_ms").integer() ==
                    static_cast<long long>(kSyncPeerTransportDefaultSqliteBusyTimeoutMs) &&
                ingress_legacy_cli_report.at("result").at("abandoned_rows_drained").integer() == 1 &&
                ingress_legacy_cli_report.at("result").at("authority_denial_rows_drained").integer() == 1 &&
                ingress_legacy_cli_report.at("result").at("audit_events_written").integer() == 2 &&
                ingress_legacy_cli_report.at("result").at("sqlite_write_contention").at("busy_handler_installed").boolean(false) &&
                !ingress_legacy_cli_report.at("result").at("sqlite_write_contention").at("contention_observed").boolean(false) &&
                ingress_legacy_cli_report.at("result").at("sqlite_write_contention").at("write_lock_attempts").integer() == 1 &&
                ingress_legacy_cli_report.at("result").at("sqlite_write_contention").at("write_locks_acquired").integer() == 1,
                "peer transport ingress retention CLI applies abandoned and denied residue drains with JSON evidence");
        SyncPeerTransportIngressStatusOptions ingress_legacy_cli_status_options = ingress_authority_legacy_status_options;
        ingress_legacy_cli_status_options.sqlite_path = ingress_legacy_cli_queue_db.string();
        SyncPeerTransportIngressStatusResult ingress_legacy_cli_status;
        require(load_sync_peer_transport_ingress_status(ingress_legacy_cli_status_options, ingress_legacy_cli_status).ok &&
                ingress_legacy_cli_status.total_rows == 0 &&
                ingress_legacy_cli_status.authority_denied_rows == 0 &&
                ingress_legacy_cli_status.retention_event_rows == 2,
                "peer transport ingress retention CLI preserves audit after bounded apply drain");
        SyncPeerTransportIngressRetentionResult ingress_legacy_retention_result;
        require(drain_sync_peer_transport_ingress_retention(ingress_legacy_retention_options,
                                                            ingress_legacy_retention_result).ok &&
                ingress_legacy_retention_result.abandoned_rows_drained == 1 &&
                ingress_legacy_retention_result.authority_denial_rows_drained == 1 &&
                ingress_legacy_retention_result.audit_events_written == 2,
                "peer transport ingress retention drains abandoned legacy rows and authority denials only under explicit cutoffs");
        SyncPeerTransportIngressStatusResult ingress_legacy_retention_status;
        require(load_sync_peer_transport_ingress_status(ingress_authority_legacy_status_options, ingress_legacy_retention_status).ok &&
                ingress_legacy_retention_status.total_rows == 0 &&
                ingress_legacy_retention_status.authority_denied_rows == 0 &&
                ingress_legacy_retention_status.retention_event_rows == 2 &&
                ingress_legacy_retention_status.retention_drained_ingress_rows == 1 &&
                ingress_legacy_retention_status.retention_drained_authority_denial_rows == 1,
                "peer transport ingress retention leaves durable audit while removing old abandoned and denied residue");

        const fs::path ingress_supersession_cli_db = fs::temp_directory_path() / ("anonsync-sync-peer-authority-supersession-cli-" + std::to_string(selftest_ticks) + ".sqlite");
        const fs::path ingress_supersession_cli_report_path = fs::temp_directory_path() / ("anonsync-sync-peer-authority-supersession-cli-" + std::to_string(selftest_ticks) + ".json");
        const fs::path ingress_supersession_cli_update_report_path = fs::temp_directory_path() / ("anonsync-sync-peer-authority-supersession-cli-update-" + std::to_string(selftest_ticks) + ".json");
        fs::remove(ingress_supersession_cli_db, apply_cleanup_ec);
        fs::remove(fs::path(ingress_supersession_cli_db.string() + "-wal"), apply_cleanup_ec);
        fs::remove(fs::path(ingress_supersession_cli_db.string() + "-shm"), apply_cleanup_ec);
        fs::remove(ingress_supersession_cli_report_path, apply_cleanup_ec);
        fs::remove(ingress_supersession_cli_update_report_path, apply_cleanup_ec);
        int ingress_supersession_cli_insert_rc = run_sync_peer_authority_supersession_command(ingress_supersession_cli_db.string(),
                                                                                              "ingress-session",
                                                                                              "operator-alpha",
                                                                                              "peer-alpha",
                                                                                              "peer-session-alpha",
                                                                                              "transport-alpha",
                                                                                              "key-alpha-old",
                                                                                              "key-alpha-new",
                                                                                              200,
                                                                                              240,
                                                                                              210,
                                                                                              "rev0752 selftest record peer authority supersession overlap",
                                                                                              ingress_supersession_cli_report_path.string());
        Json ingress_supersession_cli_report = load_json(ingress_supersession_cli_report_path.string());
        require(ingress_supersession_cli_insert_rc == 0 &&
                ingress_supersession_cli_report.at("format").str() == "anonsync-sync-peer-authority-supersession-operator-report-v2" &&
                ingress_supersession_cli_report.at("ok").boolean(false) &&
                ingress_supersession_cli_report.at("input").at("operator_id").str() == "operator-alpha" &&
                ingress_supersession_cli_report.at("input").at("sqlite_busy_timeout_ms").integer() ==
                    static_cast<long long>(kSyncPeerTransportDefaultSqliteBusyTimeoutMs) &&
                ingress_supersession_cli_report.at("result").at("record_inserted").boolean(false) &&
                ingress_supersession_cli_report.at("result").at("authority_supersession_rows_after").integer() == 1 &&
                ingress_supersession_cli_report.at("result").at("sqlite_write_contention").at("busy_handler_installed").boolean(false) &&
                !ingress_supersession_cli_report.at("result").at("sqlite_write_contention").at("contention_observed").boolean(false) &&
                ingress_supersession_cli_report.at("result").at("sqlite_write_contention").at("write_lock_attempts").integer() == 1 &&
                ingress_supersession_cli_report.at("result").at("sqlite_write_contention").at("write_locks_acquired").integer() == 1,
                "peer authority supersession CLI inserts bounded overlap with operator JSON evidence");
        int ingress_supersession_cli_update_rc = run_sync_peer_authority_supersession_command(ingress_supersession_cli_db.string(),
                                                                                              "ingress-session",
                                                                                              "operator-alpha",
                                                                                              "peer-alpha",
                                                                                              "peer-session-alpha",
                                                                                              "transport-alpha",
                                                                                              "key-alpha-old",
                                                                                              "key-alpha-new",
                                                                                              200,
                                                                                              250,
                                                                                              211,
                                                                                              "rev0752 selftest update peer authority supersession overlap",
                                                                                              ingress_supersession_cli_update_report_path.string());
        Json ingress_supersession_cli_update_report = load_json(ingress_supersession_cli_update_report_path.string());
        require(ingress_supersession_cli_update_rc == 0 &&
                ingress_supersession_cli_update_report.at("ok").boolean(false) &&
                ingress_supersession_cli_update_report.at("result").at("record_updated").boolean(false) &&
                ingress_supersession_cli_update_report.at("result").at("authority_supersession_rows_after").integer() == 1 &&
                ingress_supersession_cli_update_report.at("result").at("sqlite_write_contention").at("write_lock_attempts").integer() == 1 &&
                ingress_supersession_cli_update_report.at("result").at("sqlite_write_contention").at("write_locks_acquired").integer() == 1,
                "peer authority supersession CLI updates existing overlap without duplicating supersession rows");

        const std::string peer_round_body = "abcdefghijKLMNO";
        SyncManifestEntry peer_round_remote = remote_file_entry_for_body("docs/peer-round.txt", peer_round_body, 42);
        SyncManifestDiffPlan peer_round_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 42, {peer_round_remote}), peer_round_diff_plan).ok,
                "peer transfer round fixture builds a remote-only manifest diff");
        SyncLocalApplyPlan peer_round_apply_plan;
        require(build_sync_local_apply_plan(peer_round_diff_plan, apply_options, peer_round_apply_plan).ok &&
                peer_round_apply_plan.entries[0].local_action == SyncLocalApplyAction::StageRemoteFile,
                "peer transfer round fixture builds a staged local apply entry");
        SyncStagedTransferInspectionResult peer_round_initial_inspection;
        require(inspect_sync_staged_transfer(peer_round_remote,
                                            peer_round_apply_plan.entries[0],
                                            inspection_options,
                                            peer_round_initial_inspection).ok &&
                peer_round_initial_inspection.missing_chunks.size() == peer_round_remote.chunks.size(),
                "peer transfer round fixture starts with all chunks missing");
        SyncChunkRequestPlanOptions peer_round_request_options;
        peer_round_request_options.max_chunks_per_request = 2;
        SyncChunkRequestPlanResult peer_round_first_request;
        require(build_sync_chunk_request_plan(peer_round_remote,
                                             peer_round_apply_plan.entries[0],
                                             peer_round_initial_inspection,
                                             peer_round_request_options,
                                             peer_round_first_request).ok &&
                peer_round_first_request.selected_chunks == 2,
                "peer transfer round fixture builds the first bounded request");
        SyncPeerChunkAvailability peer_round_alpha;
        peer_round_alpha.peer_id = "peer-alpha";
        peer_round_alpha.peer_session_id = "session-one";
        peer_round_alpha.max_chunks = 1;
        peer_round_alpha.available_chunks = {peer_round_remote.chunks[0], peer_round_remote.chunks[1]};
        SyncPeerChunkAvailability peer_round_bravo;
        peer_round_bravo.peer_id = "peer-bravo";
        peer_round_bravo.peer_session_id = "session-two";
        peer_round_bravo.available_chunks = {peer_round_remote.chunks[1]};
        SyncPeerChunkScheduleResult peer_round_first_schedule;
        require(build_sync_peer_chunk_schedule(peer_round_remote,
                                               peer_round_apply_plan.entries[0],
                                               peer_round_first_request,
                                               {peer_round_bravo, peer_round_alpha},
                                               peer_round_first_schedule).ok &&
                peer_round_first_schedule.assignments.size() == 2 &&
                peer_round_first_schedule.assignments[0].peer_id == "peer-alpha" &&
                peer_round_first_schedule.assignments[1].peer_id == "peer-bravo",
                "peer transfer round fixture builds a deterministic first peer schedule");
        SyncPeerChunkResponseBatchEnvelope peer_round_alpha_batch;
        require(build_sync_peer_chunk_response_batch_envelope(peer_round_remote,
                                                             peer_round_apply_plan.entries[0],
                                                             peer_round_first_request,
                                                             peer_round_first_schedule,
                                                             peer_round_first_schedule.assignments[0],
                                                             peer_round_first_schedule.assignments[0].chunks,
                                                             peer_round_alpha_batch).ok,
                "peer transfer round fixture builds a peer-bound first response batch");
        SyncStagedTransferInspectionOptions wrong_peer_round_inspection_options = inspection_options;
        wrong_peer_round_inspection_options.local_root_path = apply_staging_root.string();
        SyncPeerChunkTransferRoundResult wrong_peer_round_result;
        require(!accept_sync_peer_chunk_response_batch_and_plan_next(peer_round_remote,
                                                                    peer_round_apply_plan.entries[0],
                                                                    peer_round_initial_inspection,
                                                                    peer_round_request_options,
                                                                    peer_round_first_request,
                                                                    peer_round_first_schedule,
                                                                    peer_round_first_schedule.assignments[0],
                                                                    peer_round_alpha_batch,
                                                                    {chunk_bytes_for_body(peer_round_body, peer_round_first_schedule.assignments[0].chunks[0])},
                                                                    chunk_write_options,
                                                                    wrong_peer_round_inspection_options,
                                                                    {},
                                                                    wrong_peer_round_result).ok &&
                !fs::exists(fs::path(peer_round_apply_plan.entries[0].absolute_staging_path)),
                "peer transfer round rejects mismatched inspection roots before accepting peer bytes");
        SyncPeerChunkAvailability peer_round_next_bravo;
        peer_round_next_bravo.peer_id = "peer-bravo";
        peer_round_next_bravo.peer_session_id = "session-two";
        peer_round_next_bravo.available_chunks = {peer_round_remote.chunks[0], peer_round_remote.chunks[1], peer_round_remote.chunks[2]};
        SyncPeerChunkTransferRoundResult peer_round_first_result;
        require(accept_sync_peer_chunk_response_batch_and_plan_next(peer_round_remote,
                                                                    peer_round_apply_plan.entries[0],
                                                                    peer_round_initial_inspection,
                                                                    peer_round_request_options,
                                                                    peer_round_first_request,
                                                                    peer_round_first_schedule,
                                                                    peer_round_first_schedule.assignments[0],
                                                                    peer_round_alpha_batch,
                                                                    {chunk_bytes_for_body(peer_round_body, peer_round_first_schedule.assignments[0].chunks[0])},
                                                                    chunk_write_options,
                                                                    inspection_options,
                                                                    {peer_round_next_bravo},
                                                                    peer_round_first_result).ok &&
                peer_round_first_result.peer_batch_acceptance.peer_id == "peer-alpha" &&
                peer_round_first_result.post_batch_inspection_checked &&
                peer_round_first_result.next_request_plan_built &&
                peer_round_first_result.next_peer_schedule_built &&
                !peer_round_first_result.ready_to_materialize &&
                peer_round_first_result.more_chunks_needed &&
                peer_round_first_result.peer_work_scheduled &&
                peer_round_first_result.post_batch_inspection.receipts_verified == 1 &&
                peer_round_first_result.next_request_plan.selected_chunks == 2 &&
                peer_round_first_result.next_peer_schedule.assignments.size() == 1 &&
                peer_round_first_result.next_peer_schedule.assignments[0].peer_id == "peer-bravo" &&
                peer_round_first_result.next_peer_schedule.assignments[0].assigned_chunks == 2 &&
                same_chunk_range(peer_round_first_result.next_peer_schedule.assignments[0].chunks[0], peer_round_remote.chunks[1]),
                "peer transfer round accepts one scheduled peer batch, reinspects, and filters broad next-peer availability into a continuation schedule");
        SyncPeerChunkResponseBatchEnvelope peer_round_bravo_batch;
        require(build_sync_peer_chunk_response_batch_envelope(peer_round_remote,
                                                             peer_round_apply_plan.entries[0],
                                                             peer_round_first_result.next_request_plan,
                                                             peer_round_first_result.next_peer_schedule,
                                                             peer_round_first_result.next_peer_schedule.assignments[0],
                                                             peer_round_first_result.next_peer_schedule.assignments[0].chunks,
                                                             peer_round_bravo_batch).ok,
                "peer transfer round builds the final peer-bound response batch from the continuation schedule");
        SyncPeerChunkTransferRoundResult peer_round_second_result;
        require(accept_sync_peer_chunk_response_batch_and_plan_next(peer_round_remote,
                                                                    peer_round_apply_plan.entries[0],
                                                                    peer_round_first_result.post_batch_inspection,
                                                                    peer_round_request_options,
                                                                    peer_round_first_result.next_request_plan,
                                                                    peer_round_first_result.next_peer_schedule,
                                                                    peer_round_first_result.next_peer_schedule.assignments[0],
                                                                    peer_round_bravo_batch,
                                                                    {chunk_bytes_for_body(peer_round_body, peer_round_first_result.next_peer_schedule.assignments[0].chunks[0]),
                                                                     chunk_bytes_for_body(peer_round_body, peer_round_first_result.next_peer_schedule.assignments[0].chunks[1])},
                                                                    chunk_write_options,
                                                                    inspection_options,
                                                                    {},
                                                                    peer_round_second_result).ok &&
                peer_round_second_result.ready_to_materialize &&
                !peer_round_second_result.more_chunks_needed &&
                !peer_round_second_result.peer_work_scheduled &&
                peer_round_second_result.post_batch_inspection.staged_file_complete &&
                peer_round_second_result.post_batch_inspection.content_sha256 == sha256_hex(peer_round_body) &&
                peer_round_second_result.next_request_plan.staged_file_complete &&
                peer_round_second_result.next_peer_schedule.request_fully_covered &&
                peer_round_second_result.next_peer_schedule.assignments.empty(),
                "peer transfer round marks a fully received staged file materialization-ready and emits an empty complete schedule");
        SyncPeerChunkAvailability peer_round_bad_next;
        peer_round_bad_next.peer_id = "Peer-Bad";
        peer_round_bad_next.peer_session_id = "session-bad";
        peer_round_bad_next.available_chunks = {peer_round_remote.chunks[0]};
        SyncPeerChunkTransferRoundResult bad_next_availability_result;
        require(!accept_sync_peer_chunk_response_batch_and_plan_next(peer_round_remote,
                                                                    peer_round_apply_plan.entries[0],
                                                                    peer_round_initial_inspection,
                                                                    peer_round_request_options,
                                                                    peer_round_first_request,
                                                                    peer_round_first_schedule,
                                                                    peer_round_first_schedule.assignments[0],
                                                                    peer_round_alpha_batch,
                                                                    {chunk_bytes_for_body(peer_round_body, peer_round_first_schedule.assignments[0].chunks[0])},
                                                                    chunk_write_options,
                                                                    inspection_options,
                                                                    {peer_round_bad_next},
                                                                    bad_next_availability_result).ok,
                "peer transfer round rejects invalid next-peer availability before invoking receipt-backed acceptance");

        SyncChunkResponseBatchEnvelope round_first_batch;
        require(build_sync_chunk_response_batch_envelope(round_remote,
                                                        round_apply_plan.entries[0],
                                                        round_first_request,
                                                        {round_remote.chunks[0], round_remote.chunks[1]},
                                                        round_first_batch).ok,
                "chunk transfer round builds the first bounded batch envelope");
        SyncChunkTransferRoundResult round_first_result;
        require(accept_sync_chunk_response_batch_and_plan_next(round_remote,
                                                              round_apply_plan.entries[0],
                                                              round_initial_inspection,
                                                              round_request_options,
                                                              round_first_request,
                                                              round_first_batch,
                                                              {chunk_bytes_for_body(round_body, round_remote.chunks[0]),
                                                               chunk_bytes_for_body(round_body, round_remote.chunks[1])},
                                                              chunk_write_options,
                                                              inspection_options,
                                                              round_first_result).ok &&
                round_first_result.post_batch_inspection_checked &&
                round_first_result.next_request_plan_built &&
                !round_first_result.ready_to_materialize &&
                round_first_result.more_chunks_needed &&
                round_first_result.post_batch_inspection.receipts_verified == 2 &&
                round_first_result.post_batch_inspection.missing_chunks.size() == 2 &&
                round_first_result.next_request_plan.selected_chunks == 2 &&
                !round_first_result.next_request_plan.more_chunks_available &&
                same_chunk_range(round_first_result.next_request_plan.chunks_to_request[0], round_remote.chunks[2]) &&
                same_chunk_range(round_first_result.next_request_plan.chunks_to_request[1], round_remote.chunks[3]),
                "chunk transfer round re-inspects after a partial batch and emits the next deterministic request");
        SyncStagedTransferInspectionOptions wrong_round_inspection_options = inspection_options;
        wrong_round_inspection_options.staging_root_path = apply_root.string();
        SyncChunkTransferRoundResult wrong_round_root_result;
        require(!accept_sync_chunk_response_batch_and_plan_next(round_remote,
                                                               round_apply_plan.entries[0],
                                                               round_initial_inspection,
                                                               round_request_options,
                                                               round_first_request,
                                                               round_first_batch,
                                                               {chunk_bytes_for_body(round_body, round_remote.chunks[0]),
                                                                chunk_bytes_for_body(round_body, round_remote.chunks[1])},
                                                               chunk_write_options,
                                                               wrong_round_inspection_options,
                                                               wrong_round_root_result).ok,
                "chunk transfer round rejects mismatched write and inspection roots before accepting bytes");
        SyncChunkResponseBatchEnvelope round_second_batch;
        require(build_sync_chunk_response_batch_envelope(round_remote,
                                                        round_apply_plan.entries[0],
                                                        round_first_result.next_request_plan,
                                                        {round_remote.chunks[2], round_remote.chunks[3]},
                                                        round_second_batch).ok,
                "chunk transfer round builds the second bounded batch envelope from the continuation plan");
        SyncChunkTransferRoundResult round_second_result;
        require(accept_sync_chunk_response_batch_and_plan_next(round_remote,
                                                              round_apply_plan.entries[0],
                                                              round_first_result.post_batch_inspection,
                                                              round_request_options,
                                                              round_first_result.next_request_plan,
                                                              round_second_batch,
                                                              {chunk_bytes_for_body(round_body, round_remote.chunks[2]),
                                                               chunk_bytes_for_body(round_body, round_remote.chunks[3])},
                                                              chunk_write_options,
                                                              inspection_options,
                                                              round_second_result).ok &&
                round_second_result.post_batch_inspection_checked &&
                round_second_result.next_request_plan_built &&
                round_second_result.ready_to_materialize &&
                !round_second_result.more_chunks_needed &&
                round_second_result.post_batch_inspection.staged_file_complete &&
                round_second_result.post_batch_inspection.missing_chunks.empty() &&
                round_second_result.post_batch_inspection.content_sha256 == sha256_hex(round_body) &&
                round_second_result.next_request_plan.staged_file_complete &&
                round_second_result.next_request_plan.chunks_to_request.empty(),
                "chunk transfer round marks the staged file materialization-ready after the final batch");

        SyncChunkRequestPlanOptions request_too_small;
        request_too_small.max_bytes_per_request = chunked_remote.chunks[0].length - 1;
        SyncChunkRequestPlanResult too_small_request_plan;
        require(!build_sync_chunk_request_plan(chunked_remote,
                                              chunked_apply_plan.entries[0],
                                              partial_inspection,
                                              request_too_small,
                                              too_small_request_plan).ok,
                "chunk request plan rejects byte budgets that cannot carry the first missing chunk");

        SyncStagedTransferInspectionResult forged_inspection = partial_inspection;
        forged_inspection.missing_chunks[0].offset = 999;
        SyncChunkRequestPlanResult forged_request_plan;
        require(!build_sync_chunk_request_plan(chunked_remote,
                                              chunked_apply_plan.entries[0],
                                              forged_inspection,
                                              SyncChunkRequestPlanOptions{},
                                              forged_request_plan).ok,
                "chunk request plan rejects forged missing chunks not present in manifest order");

        SyncChunkReceiptWriteResult middle_chunk_repeat;
        require(write_sync_staged_chunk(chunked_remote,
                                       chunked_apply_plan.entries[0],
                                       chunked_remote.chunks[1],
                                       chunk_bytes_for_body(chunked_body, chunked_remote.chunks[1]),
                                       chunk_write_options,
                                       middle_chunk_repeat).ok &&
                !middle_chunk_repeat.chunk_written &&
                middle_chunk_repeat.reused_existing_receipt &&
                !middle_chunk_repeat.staged_file_complete &&
                middle_chunk_repeat.idempotency_key == middle_chunk_result.idempotency_key,
                "staged chunk write resumes by reusing an existing matching receipt");

        SyncChunkReceiptWriteResult first_chunk_result;
        require(write_sync_staged_chunk(chunked_remote,
                                       chunked_apply_plan.entries[0],
                                       chunked_remote.chunks[0],
                                       chunk_bytes_for_body(chunked_body, chunked_remote.chunks[0]),
                                       chunk_write_options,
                                       first_chunk_result).ok &&
                first_chunk_result.reused_existing_receipt &&
                !first_chunk_result.staged_file_complete,
                "staged chunk write reuses the first receipt already written through requested chunk acceptance");

        SyncChunkReceiptWriteResult final_chunk_result;
        require(write_sync_staged_chunk(chunked_remote,
                                       chunked_apply_plan.entries[0],
                                       chunked_remote.chunks[2],
                                       chunk_bytes_for_body(chunked_body, chunked_remote.chunks[2]),
                                       chunk_write_options,
                                       final_chunk_result).ok &&
                final_chunk_result.chunk_written &&
                final_chunk_result.staged_file_complete &&
                final_chunk_result.chunks_verified == chunked_remote.chunks.size() &&
                final_chunk_result.content_sha256 == sha256_hex(chunked_body),
                "staged chunk write declares completion only after all receipts and staged bytes verify");

        SyncStagedTransferInspectionResult complete_inspection;
        require(inspect_sync_staged_transfer(chunked_remote,
                                            chunked_apply_plan.entries[0],
                                            inspection_options,
                                            complete_inspection).ok &&
                complete_inspection.staged_file_complete &&
                complete_inspection.receipts_verified == chunked_remote.chunks.size() &&
                complete_inspection.chunks_verified == chunked_remote.chunks.size() &&
                complete_inspection.missing_chunks.empty() &&
                complete_inspection.content_sha256 == sha256_hex(chunked_body),
                "staged transfer inspection confirms complete receipt-gated staged file before materialization");

        SyncChunkRequestPlanResult complete_request_plan;
        require(build_sync_chunk_request_plan(chunked_remote,
                                             chunked_apply_plan.entries[0],
                                             complete_inspection,
                                             SyncChunkRequestPlanOptions{},
                                             complete_request_plan).ok &&
                complete_request_plan.staged_file_complete &&
                complete_request_plan.total_missing_chunks == 0 &&
                complete_request_plan.selected_chunks == 0 &&
                complete_request_plan.chunks_to_request.empty() &&
                !complete_request_plan.more_chunks_available,
                "chunk request plan emits no peer requests once staged transfer inspection is complete");

        SyncRequestedChunkAcceptanceResult complete_accept_result;
        require(!accept_sync_requested_chunk(chunked_remote,
                                            chunked_apply_plan.entries[0],
                                            complete_inspection,
                                            SyncChunkRequestPlanOptions{},
                                            complete_request_plan,
                                            chunked_remote.chunks[0],
                                            chunk_bytes_for_body(chunked_body, chunked_remote.chunks[0]),
                                            chunk_write_options,
                                            complete_accept_result).ok,
                "requested chunk acceptance rejects peer bytes after inspection says the staged file is complete");

        SyncStagedFileMaterializationResult chunked_materialize_result;
        require(materialize_staged_sync_file(chunked_remote,
                                            chunked_apply_plan.entries[0],
                                            receipt_gated_materialize_options,
                                            chunked_materialize_result).ok &&
                chunked_materialize_result.chunk_receipts_checked &&
                read_binary_fixture(chunked_materialize_result.absolute_target_path) == chunked_body &&
                !fs::exists(fs::path(chunked_materialize_result.absolute_staging_path)),
                "completed chunk receipt staging file can be materialized only after receipt-gated verification");

        SyncManifestEntry bad_chunk_remote = remote_file_entry_for_body("docs/chunk-bad.txt", "abcdefghij", 28);
        SyncManifestDiffPlan bad_chunk_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 28, {bad_chunk_remote}), bad_chunk_diff_plan).ok,
                "manifest diff plans bad chunk rejection fixture");
        SyncLocalApplyPlan bad_chunk_apply_plan;
        require(build_sync_local_apply_plan(bad_chunk_diff_plan, apply_options, bad_chunk_apply_plan).ok,
                "local apply plan emits bad chunk rejection fixture");
        SyncChunkReceiptWriteResult bad_chunk_result;
        require(!write_sync_staged_chunk(bad_chunk_remote,
                                        bad_chunk_apply_plan.entries[0],
                                        bad_chunk_remote.chunks[0],
                                        "zzzzz",
                                        chunk_write_options,
                                        bad_chunk_result).ok &&
                !fs::exists(fs::path(bad_chunk_apply_plan.entries[0].absolute_target_path)),
                "staged chunk write rejects bytes that do not hash to the manifest chunk");

        SyncManifestEntry tampered_chunk_remote = remote_file_entry_for_body("docs/chunk-tamper.txt", "receipt-test", 29);
        SyncManifestDiffPlan tampered_chunk_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 29, {tampered_chunk_remote}), tampered_chunk_diff_plan).ok,
                "manifest diff plans chunk receipt tamper fixture");
        SyncLocalApplyPlan tampered_chunk_apply_plan;
        require(build_sync_local_apply_plan(tampered_chunk_diff_plan, apply_options, tampered_chunk_apply_plan).ok,
                "local apply plan emits chunk receipt tamper fixture");
        SyncChunkReceiptWriteResult tampered_chunk_first;
        require(write_sync_staged_chunk(tampered_chunk_remote,
                                       tampered_chunk_apply_plan.entries[0],
                                       tampered_chunk_remote.chunks[0],
                                       chunk_bytes_for_body("receipt-test", tampered_chunk_remote.chunks[0]),
                                       chunk_write_options,
                                       tampered_chunk_first).ok,
                "staged chunk write creates a receipt used by tamper fixture");
        write_binary_fixture(tampered_chunk_first.absolute_staging_path, "xxxxx");
        SyncStagedTransferInspectionResult tampered_inspection;
        require(!inspect_sync_staged_transfer(tampered_chunk_remote,
                                             tampered_chunk_apply_plan.entries[0],
                                             inspection_options,
                                             tampered_inspection).ok,
                "staged transfer inspection rejects a receipt whose staged bytes were tampered");
        SyncChunkReceiptWriteResult tampered_chunk_second;
        require(!write_sync_staged_chunk(tampered_chunk_remote,
                                        tampered_chunk_apply_plan.entries[0],
                                        tampered_chunk_remote.chunks[0],
                                        chunk_bytes_for_body("receipt-test", tampered_chunk_remote.chunks[0]),
                                        chunk_write_options,
                                        tampered_chunk_second).ok,
                "staged chunk write rejects an existing receipt when staged bytes no longer match it");

        const std::string zero_chunk_body(5, '\0');
        SyncManifestEntry zero_chunk_remote = remote_file_entry_for_body("docs/chunk-zero.bin", zero_chunk_body, 30);
        SyncManifestDiffPlan zero_chunk_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 30, {zero_chunk_remote}), zero_chunk_diff_plan).ok,
                "manifest diff plans zero chunk receipt fixture");
        SyncLocalApplyPlan zero_chunk_apply_plan;
        require(build_sync_local_apply_plan(zero_chunk_diff_plan, apply_options, zero_chunk_apply_plan).ok,
                "local apply plan emits zero chunk receipt fixture");
        SyncChunkReceiptWriteResult zero_chunk_first;
        require(write_sync_staged_chunk(zero_chunk_remote,
                                       zero_chunk_apply_plan.entries[0],
                                       zero_chunk_remote.chunks[0],
                                       chunk_bytes_for_body(zero_chunk_body, zero_chunk_remote.chunks[0]),
                                       chunk_write_options,
                                       zero_chunk_first).ok,
                "staged chunk write records a receipt for an all-zero chunk");
        std::error_code remove_zero_staging_ec;
        fs::remove(fs::path(zero_chunk_first.absolute_staging_path), remove_zero_staging_ec);
        SyncChunkReceiptWriteResult zero_chunk_resume;
        require(!write_sync_staged_chunk(zero_chunk_remote,
                                        zero_chunk_apply_plan.entries[0],
                                        zero_chunk_remote.chunks[0],
                                        chunk_bytes_for_body(zero_chunk_body, zero_chunk_remote.chunks[0]),
                                        chunk_write_options,
                                        zero_chunk_resume).ok,
                "staged chunk write does not treat an all-zero sparse hole or missing file as complete without bytes");

        const std::string replace_local_body = "local version before remote handoff\n";
        const std::string replace_remote_body = "remote version after sync handoff\n";
        SyncManifestEntry replace_local = remote_file_entry_for_body("docs/replace.txt", replace_local_body, 7);
        replace_local.device_id = "device-alpha";
        replace_local.lineage = {{"device-alpha", 1}};
        SyncManifestEntry replace_remote = remote_file_entry_for_body("docs/replace.txt", replace_remote_body, 8);
        replace_remote.lineage = {{"device-alpha", 1}, {"device-bravo", 1}};
        SyncManifestDiffPlan replace_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 15, {replace_local}),
                                              folder_manifest("folder-alpha", "device-bravo", 15, {replace_remote}),
                                              replace_diff_plan).ok &&
                replace_diff_plan.entries[0].action == SyncPlanAction::FetchRemoteFile &&
                replace_diff_plan.entries[0].local_content_sha256 == sha256_hex(replace_local_body) &&
                replace_diff_plan.entries[0].remote_content_sha256 == sha256_hex(replace_remote_body),
                "manifest diff carries local and remote content evidence for overwrite preflight");
        SyncLocalApplyPlan replace_apply_plan;
        require(build_sync_local_apply_plan(replace_diff_plan, apply_options, replace_apply_plan).ok &&
                replace_apply_plan.entries[0].local_entry_present &&
                replace_apply_plan.entries[0].local_entry_kind == SyncManifestEntryKind::File &&
                replace_apply_plan.entries[0].local_content_sha256 == sha256_hex(replace_local_body),
                "local apply plan preserves local content evidence for stale-overwrite checks");
        write_binary_fixture(replace_apply_plan.entries[0].absolute_target_path, replace_local_body);
        write_binary_fixture(replace_apply_plan.entries[0].absolute_staging_path, replace_remote_body);
        SyncStagedFileMaterializationResult replace_result;
        require(materialize_staged_sync_file(replace_remote, replace_apply_plan.entries[0], materialize_options, replace_result).ok &&
                replace_result.preflight_checked_target &&
                replace_result.replaced_existing_target &&
                read_binary_fixture(replace_result.absolute_target_path) == replace_remote_body,
                "staged file materialization replaces only a target matching the planned local content evidence");

        const std::string stale_local_body = "local version that was scanned\n";
        const std::string stale_changed_body = "local version changed after scan\n";
        const std::string stale_remote_body = "remote version must wait\n";
        SyncManifestEntry stale_local = remote_file_entry_for_body("docs/stale.txt", stale_local_body, 9);
        stale_local.device_id = "device-alpha";
        stale_local.lineage = {{"device-alpha", 1}};
        SyncManifestEntry stale_remote = remote_file_entry_for_body("docs/stale.txt", stale_remote_body, 10);
        stale_remote.lineage = {{"device-alpha", 1}, {"device-bravo", 1}};
        SyncManifestDiffPlan stale_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 16, {stale_local}),
                                              folder_manifest("folder-alpha", "device-bravo", 16, {stale_remote}),
                                              stale_diff_plan).ok,
                "manifest diff plans stale-overwrite rejection fixture");
        SyncLocalApplyPlan stale_apply_plan;
        require(build_sync_local_apply_plan(stale_diff_plan, apply_options, stale_apply_plan).ok,
                "local apply plan emits stale-overwrite rejection fixture");
        write_binary_fixture(stale_apply_plan.entries[0].absolute_target_path, stale_changed_body);
        write_binary_fixture(stale_apply_plan.entries[0].absolute_staging_path, stale_remote_body);
        SyncStagedFileMaterializationResult stale_result;
        require(!materialize_staged_sync_file(stale_remote, stale_apply_plan.entries[0], materialize_options, stale_result).ok &&
                read_binary_fixture(stale_apply_plan.entries[0].absolute_target_path) == stale_changed_body &&
                fs::exists(fs::path(stale_apply_plan.entries[0].absolute_staging_path)),
                "staged file materialization rejects stale local targets before overwrite");

        SyncManifestEntry appeared_remote = remote_file_entry_for_body("docs/appeared.txt", "remote-only payload", 11);
        SyncManifestDiffPlan appeared_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 17, {appeared_remote}), appeared_diff_plan).ok,
                "manifest diff plans target-appeared rejection fixture");
        SyncLocalApplyPlan appeared_apply_plan;
        require(build_sync_local_apply_plan(appeared_diff_plan, apply_options, appeared_apply_plan).ok,
                "local apply plan emits target-appeared rejection fixture");
        write_binary_fixture(appeared_apply_plan.entries[0].absolute_target_path, "new local file after scan");
        write_binary_fixture(appeared_apply_plan.entries[0].absolute_staging_path, "remote-only payload");
        SyncStagedFileMaterializationResult appeared_result;
        require(!materialize_staged_sync_file(appeared_remote, appeared_apply_plan.entries[0], materialize_options, appeared_result).ok &&
                read_binary_fixture(appeared_apply_plan.entries[0].absolute_target_path) == "new local file after scan" &&
                fs::exists(fs::path(appeared_apply_plan.entries[0].absolute_staging_path)),
                "staged file materialization rejects newly appeared local targets for remote-only plans");

        SyncConflictPreservationOptions conflict_options;
        conflict_options.local_root_path = apply_root.string();
        conflict_options.staging_root_path = apply_staging_root.string();

        const std::string conflict_local_body = "local conflict version kept as a copy\n";
        const std::string conflict_remote_body = "remote conflict version promoted to target\n";
        SyncManifestEntry conflict_local_file = remote_file_entry_for_body("docs/conflict-real.txt", conflict_local_body, 22);
        conflict_local_file.device_id = "device-alpha";
        conflict_local_file.lineage = {{"device-alpha", 4}};
        SyncManifestEntry conflict_remote_file = remote_file_entry_for_body("docs/conflict-real.txt", conflict_remote_body, 23);
        conflict_remote_file.lineage = {{"device-bravo", 4}};
        orient_remote_file_as_deterministic_conflict_winner_or_throw(
            conflict_local_file, conflict_remote_file);
        SyncManifestDiffPlan real_conflict_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 22, {conflict_local_file}),
                                              folder_manifest("folder-alpha", "device-bravo", 22, {conflict_remote_file}),
                                              real_conflict_diff_plan).ok &&
                real_conflict_diff_plan.entries[0].action == SyncPlanAction::RecordConflict,
                "manifest diff plans real file/file conflict preservation fixture");
        SyncLocalApplyPlan real_conflict_apply_plan;
        require(build_sync_local_apply_plan(real_conflict_diff_plan, apply_options, real_conflict_apply_plan).ok &&
                real_conflict_apply_plan.entries[0].local_action == SyncLocalApplyAction::PreserveConflictCopy &&
                !real_conflict_apply_plan.entries[0].absolute_conflict_copy_path.empty() &&
                !real_conflict_apply_plan.entries[0].absolute_staging_path.empty(),
                "local apply plan emits conflict-copy and staging paths for file/file conflict");
        write_binary_fixture(real_conflict_apply_plan.entries[0].absolute_target_path, conflict_local_body);
        write_binary_fixture(real_conflict_apply_plan.entries[0].absolute_staging_path, conflict_remote_body);
        SyncConflictPreservationResult real_conflict_result;
        require(apply_sync_conflict_preservation(conflict_remote_file, real_conflict_apply_plan.entries[0], conflict_options, real_conflict_result).ok &&
                real_conflict_result.preflight_checked_target &&
                real_conflict_result.conflict_copy_preserved &&
                real_conflict_result.remote_file_materialized &&
                !real_conflict_result.remote_tombstone_applied &&
                real_conflict_result.idempotency_key.rfind("sync-conflict:v1:", 0) == 0 &&
                real_conflict_result.remote_content_sha256 == sha256_hex(conflict_remote_body) &&
                real_conflict_result.remote_chunks_verified == conflict_remote_file.chunks.size(),
                "conflict preservation copies local bytes and materializes verified remote conflict bytes");
        require(read_binary_fixture(real_conflict_result.absolute_conflict_copy_path) == conflict_local_body &&
                read_binary_fixture(real_conflict_result.absolute_target_path) == conflict_remote_body &&
                !fs::exists(fs::path(real_conflict_result.absolute_staging_path)),
                "conflict preservation leaves local conflict copy and promotes the remote file version");

        const std::string receipt_conflict_local_body = "local conflict copy with receipt gate\n";
        const std::string receipt_conflict_remote_body = "remote conflict bytes via receipts\n";
        SyncManifestEntry receipt_conflict_local = remote_file_entry_for_body("docs/conflict-receipt.txt", receipt_conflict_local_body, 32);
        receipt_conflict_local.device_id = "device-alpha";
        receipt_conflict_local.lineage = {{"device-alpha", 7}};
        SyncManifestEntry receipt_conflict_remote = remote_file_entry_for_body("docs/conflict-receipt.txt", receipt_conflict_remote_body, 33);
        receipt_conflict_remote.lineage = {{"device-bravo", 7}};
        orient_remote_file_as_deterministic_conflict_winner_or_throw(
            receipt_conflict_local, receipt_conflict_remote);
        SyncManifestDiffPlan receipt_conflict_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 32, {receipt_conflict_local}),
                                              folder_manifest("folder-alpha", "device-bravo", 32, {receipt_conflict_remote}),
                                              receipt_conflict_diff_plan).ok,
                "manifest diff plans receipt-gated conflict preservation fixture");
        SyncLocalApplyPlan receipt_conflict_apply_plan;
        require(build_sync_local_apply_plan(receipt_conflict_diff_plan, apply_options, receipt_conflict_apply_plan).ok,
                "local apply plan emits receipt-gated conflict preservation fixture");
        write_binary_fixture(receipt_conflict_apply_plan.entries[0].absolute_target_path, receipt_conflict_local_body);
        for (const auto& chunk : receipt_conflict_remote.chunks) {
            SyncChunkReceiptWriteResult receipt_conflict_chunk;
            require(write_sync_staged_chunk(receipt_conflict_remote,
                                           receipt_conflict_apply_plan.entries[0],
                                           chunk,
                                           chunk_bytes_for_body(receipt_conflict_remote_body, chunk),
                                           chunk_write_options,
                                           receipt_conflict_chunk).ok,
                    "staged chunk write records receipts for conflict preservation fixture");
        }
        SyncConflictPreservationOptions receipt_conflict_options = conflict_options;
        receipt_conflict_options.require_chunk_receipts = true;
        SyncConflictPreservationResult receipt_conflict_result;
        require(apply_sync_conflict_preservation(receipt_conflict_remote,
                                                 receipt_conflict_apply_plan.entries[0],
                                                 receipt_conflict_options,
                                                 receipt_conflict_result).ok &&
                receipt_conflict_result.chunk_receipts_checked &&
                receipt_conflict_result.remote_file_materialized &&
                read_binary_fixture(receipt_conflict_result.absolute_conflict_copy_path) == receipt_conflict_local_body &&
                read_binary_fixture(receipt_conflict_result.absolute_target_path) == receipt_conflict_remote_body,
                "receipt-gated conflict preservation requires chunk receipts before promoting remote conflict bytes");

        const std::string stale_conflict_local_body = "conflict source scanned before edit\n";
        const std::string stale_conflict_changed_body = "conflict source changed after planning\n";
        const std::string stale_conflict_remote_body = "remote conflict bytes must wait\n";
        SyncManifestEntry stale_conflict_local = remote_file_entry_for_body("docs/conflict-stale.txt", stale_conflict_local_body, 24);
        stale_conflict_local.device_id = "device-alpha";
        stale_conflict_local.lineage = {{"device-alpha", 5}};
        SyncManifestEntry stale_conflict_remote = remote_file_entry_for_body("docs/conflict-stale.txt", stale_conflict_remote_body, 25);
        stale_conflict_remote.lineage = {{"device-bravo", 5}};
        orient_remote_file_as_deterministic_conflict_winner_or_throw(
            stale_conflict_local, stale_conflict_remote);
        SyncManifestDiffPlan stale_conflict_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 23, {stale_conflict_local}),
                                              folder_manifest("folder-alpha", "device-bravo", 23, {stale_conflict_remote}),
                                              stale_conflict_diff_plan).ok,
                "manifest diff plans stale conflict preservation fixture");
        SyncLocalApplyPlan stale_conflict_apply_plan;
        require(build_sync_local_apply_plan(stale_conflict_diff_plan, apply_options, stale_conflict_apply_plan).ok,
                "local apply plan emits stale conflict preservation fixture");
        write_binary_fixture(stale_conflict_apply_plan.entries[0].absolute_target_path, stale_conflict_changed_body);
        write_binary_fixture(stale_conflict_apply_plan.entries[0].absolute_staging_path, stale_conflict_remote_body);
        SyncConflictPreservationResult stale_conflict_result;
        require(!apply_sync_conflict_preservation(stale_conflict_remote, stale_conflict_apply_plan.entries[0], conflict_options, stale_conflict_result).ok &&
                read_binary_fixture(stale_conflict_apply_plan.entries[0].absolute_target_path) == stale_conflict_changed_body &&
                fs::exists(fs::path(stale_conflict_apply_plan.entries[0].absolute_staging_path)) &&
                !fs::exists(fs::path(stale_conflict_apply_plan.entries[0].absolute_conflict_copy_path)),
                "conflict preservation rejects stale local targets before copying or promoting remote bytes");

        const std::string delete_conflict_local_body = "local edit kept when remote delete conflicts\n";
        SyncManifestEntry delete_conflict_local = remote_file_entry_for_body("docs/conflict-delete.txt", delete_conflict_local_body, 26);
        delete_conflict_local.device_id = "device-alpha";
        delete_conflict_local.lineage = {{"device-alpha", 6}};
        SyncManifestEntry delete_conflict_remote = delete_conflict_local;
        delete_conflict_remote.device_id = "device-bravo";
        delete_conflict_remote.kind = SyncManifestEntryKind::Tombstone;
        delete_conflict_remote.size_bytes = 0;
        delete_conflict_remote.content_sha256.clear();
        delete_conflict_remote.chunks.clear();
        delete_conflict_remote.lineage = {{"device-bravo", 6}};
        SyncManifestDiffPlan delete_conflict_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 24, {delete_conflict_local}),
                                              folder_manifest("folder-alpha", "device-bravo", 24, {delete_conflict_remote}),
                                              delete_conflict_diff_plan).ok &&
                delete_conflict_diff_plan.entries[0].action == SyncPlanAction::RecordConflict,
                "manifest diff plans file/delete conflict preservation fixture");
        SyncLocalApplyPlan delete_conflict_apply_plan;
        require(build_sync_local_apply_plan(delete_conflict_diff_plan, apply_options, delete_conflict_apply_plan).ok &&
                delete_conflict_apply_plan.entries[0].local_action == SyncLocalApplyAction::PreserveConflictCopy &&
                delete_conflict_apply_plan.entries[0].absolute_staging_path.empty(),
                "local apply plan emits conflict copy without staging for file/delete conflicts");
        write_binary_fixture(delete_conflict_apply_plan.entries[0].absolute_target_path, delete_conflict_local_body);
        SyncConflictPreservationResult delete_conflict_result;
        require(apply_sync_conflict_preservation(delete_conflict_remote, delete_conflict_apply_plan.entries[0], conflict_options, delete_conflict_result).ok &&
                delete_conflict_result.conflict_copy_preserved &&
                !delete_conflict_result.remote_file_materialized &&
                delete_conflict_result.remote_tombstone_applied &&
                delete_conflict_result.remote_chunks_verified == 0 &&
                delete_conflict_result.remote_content_sha256.empty(),
                "conflict preservation copies local bytes and applies the conflicting remote tombstone");
        require(read_binary_fixture(delete_conflict_result.absolute_conflict_copy_path) == delete_conflict_local_body &&
                !fs::exists(fs::path(delete_conflict_result.absolute_target_path)),
                "file/delete conflict leaves only the local conflict copy at the conflict path");

        SyncTombstoneApplicationOptions tombstone_options;
        tombstone_options.local_root_path = apply_root.string();

        const std::string tombstone_local_body = "local bytes deleted by remote tombstone\n";
        SyncManifestEntry tombstone_local_file = remote_file_entry_for_body("docs/delete-me.txt", tombstone_local_body, 12);
        tombstone_local_file.device_id = "device-alpha";
        tombstone_local_file.lineage = {{"device-alpha", 1}};
        SyncManifestEntry tombstone_remote_delete = tombstone_local_file;
        tombstone_remote_delete.device_id = "device-bravo";
        tombstone_remote_delete.kind = SyncManifestEntryKind::Tombstone;
        tombstone_remote_delete.size_bytes = 0;
        tombstone_remote_delete.content_sha256.clear();
        tombstone_remote_delete.chunks.clear();
        tombstone_remote_delete.lineage = {{"device-alpha", 1}, {"device-bravo", 1}};
        SyncManifestDiffPlan tombstone_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 18, {tombstone_local_file}),
                                              folder_manifest("folder-alpha", "device-bravo", 18, {tombstone_remote_delete}),
                                              tombstone_diff_plan).ok &&
                tombstone_diff_plan.entries[0].action == SyncPlanAction::ApplyRemoteTombstone,
                "manifest diff plans remote tombstone deletion over a planned local file");
        SyncLocalApplyPlan tombstone_apply_plan;
        require(build_sync_local_apply_plan(tombstone_diff_plan, apply_options, tombstone_apply_plan).ok &&
                tombstone_apply_plan.entries[0].local_action == SyncLocalApplyAction::DeleteLocalPath &&
                tombstone_apply_plan.entries[0].absolute_staging_path.empty() &&
                tombstone_apply_plan.entries[0].local_content_sha256 == sha256_hex(tombstone_local_body),
                "local apply plan carries delete intent evidence for remote tombstones");
        write_binary_fixture(tombstone_apply_plan.entries[0].absolute_target_path, tombstone_local_body);
        SyncTombstoneApplicationResult tombstone_result;
        SyncValidationResult tombstone_ok = apply_sync_remote_tombstone(tombstone_remote_delete, tombstone_apply_plan.entries[0], tombstone_options, tombstone_result);
        require(tombstone_ok.ok && tombstone_result.preflight_checked_target &&
                tombstone_result.target_existed && tombstone_result.removed &&
                tombstone_result.idempotency_key.rfind("sync-tombstone:v1:", 0) == 0 &&
                !fs::exists(fs::path(tombstone_result.absolute_target_path)),
                "remote tombstone application verifies planned local bytes before deleting the file");

        SyncManifestEntry no_op_remote_delete = tombstone_remote_delete;
        no_op_remote_delete.path.value = "docs/already-gone.txt";
        no_op_remote_delete.lineage = {{"device-bravo", 13}};
        SyncManifestDiffPlan no_op_tombstone_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 19, {no_op_remote_delete}), no_op_tombstone_diff_plan).ok,
                "manifest diff plans remote-only tombstone no-op fixture");
        SyncLocalApplyPlan no_op_tombstone_apply_plan;
        require(build_sync_local_apply_plan(no_op_tombstone_diff_plan, apply_options, no_op_tombstone_apply_plan).ok,
                "local apply plan emits remote-only tombstone no-op fixture");
        SyncTombstoneApplicationResult no_op_tombstone_result;
        require(apply_sync_remote_tombstone(no_op_remote_delete, no_op_tombstone_apply_plan.entries[0], tombstone_options, no_op_tombstone_result).ok &&
                no_op_tombstone_result.preflight_checked_target &&
                !no_op_tombstone_result.target_existed &&
                !no_op_tombstone_result.removed,
                "remote tombstone application is a verified no-op when the planned target is already absent");

        const std::string tombstone_stale_body = "local tombstone source changed after scan\n";
        SyncManifestEntry stale_tombstone_local = remote_file_entry_for_body("docs/delete-stale.txt", tombstone_local_body, 14);
        stale_tombstone_local.device_id = "device-alpha";
        stale_tombstone_local.lineage = {{"device-alpha", 1}};
        SyncManifestEntry stale_tombstone_remote = stale_tombstone_local;
        stale_tombstone_remote.device_id = "device-bravo";
        stale_tombstone_remote.kind = SyncManifestEntryKind::Tombstone;
        stale_tombstone_remote.size_bytes = 0;
        stale_tombstone_remote.content_sha256.clear();
        stale_tombstone_remote.chunks.clear();
        stale_tombstone_remote.lineage = {{"device-alpha", 1}, {"device-bravo", 2}};
        SyncManifestDiffPlan stale_tombstone_diff_plan;
        require(build_sync_manifest_diff_plan(folder_manifest("folder-alpha", "device-alpha", 20, {stale_tombstone_local}),
                                              folder_manifest("folder-alpha", "device-bravo", 20, {stale_tombstone_remote}),
                                              stale_tombstone_diff_plan).ok,
                "manifest diff plans stale tombstone rejection fixture");
        SyncLocalApplyPlan stale_tombstone_apply_plan;
        require(build_sync_local_apply_plan(stale_tombstone_diff_plan, apply_options, stale_tombstone_apply_plan).ok,
                "local apply plan emits stale tombstone rejection fixture");
        write_binary_fixture(stale_tombstone_apply_plan.entries[0].absolute_target_path, tombstone_stale_body);
        SyncTombstoneApplicationResult stale_tombstone_result;
        require(!apply_sync_remote_tombstone(stale_tombstone_remote, stale_tombstone_apply_plan.entries[0], tombstone_options, stale_tombstone_result).ok &&
                read_binary_fixture(stale_tombstone_apply_plan.entries[0].absolute_target_path) == tombstone_stale_body,
                "remote tombstone application rejects stale changed targets before deleting");

        SyncManifestEntry appeared_tombstone_remote = no_op_remote_delete;
        appeared_tombstone_remote.path.value = "docs/delete-appeared.txt";
        appeared_tombstone_remote.lineage = {{"device-bravo", 15}};
        SyncManifestDiffPlan appeared_tombstone_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 21, {appeared_tombstone_remote}), appeared_tombstone_diff_plan).ok,
                "manifest diff plans target-appeared tombstone fixture");
        SyncLocalApplyPlan appeared_tombstone_apply_plan;
        require(build_sync_local_apply_plan(appeared_tombstone_diff_plan, apply_options, appeared_tombstone_apply_plan).ok,
                "local apply plan emits target-appeared tombstone fixture");
        write_binary_fixture(appeared_tombstone_apply_plan.entries[0].absolute_target_path, "local file appeared after tombstone plan");
        SyncTombstoneApplicationResult appeared_tombstone_result;
        require(!apply_sync_remote_tombstone(appeared_tombstone_remote, appeared_tombstone_apply_plan.entries[0], tombstone_options, appeared_tombstone_result).ok &&
                read_binary_fixture(appeared_tombstone_apply_plan.entries[0].absolute_target_path) == "local file appeared after tombstone plan",
                "remote tombstone application rejects newly appeared targets for remote-only tombstone plans");

        const std::string tampered_expected_body = "expected remote bytes";
        SyncManifestEntry tampered_remote = remote_file_entry_for_body("docs/tampered.txt", tampered_expected_body, 5);
        SyncManifestDiffPlan tampered_diff_plan;
        require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 13, {tampered_remote}), tampered_diff_plan).ok,
                "manifest diff plans tamper-verification fixture");
        SyncLocalApplyPlan tampered_apply_plan;
        require(build_sync_local_apply_plan(tampered_diff_plan, apply_options, tampered_apply_plan).ok,
                "local apply plan emits tamper-verification fixture");
        write_binary_fixture(tampered_apply_plan.entries[0].absolute_staging_path, "tampered remote bytes");
        SyncStagedFileMaterializationResult tampered_result;
        require(!materialize_staged_sync_file(tampered_remote, tampered_apply_plan.entries[0], materialize_options, tampered_result).ok &&
                fs::exists(fs::path(tampered_apply_plan.entries[0].absolute_staging_path)) &&
                !fs::exists(fs::path(tampered_apply_plan.entries[0].absolute_target_path)),
                "staged file materialization rejects hash-mismatched staging files without committing target bytes");

        const fs::path outside_link_target = fs::temp_directory_path() / ("anonsync-sync-apply-link-target-" + std::to_string(selftest_ticks));
        fs::create_directories(outside_link_target, apply_cleanup_ec);
        if (apply_cleanup_ec) throw std::runtime_error("could not create symlink target fixture: " + apply_cleanup_ec.message());
        std::error_code symlink_ancestor_ec;
        fs::create_directory_symlink(outside_link_target, apply_root / "linked", symlink_ancestor_ec);
        if (!symlink_ancestor_ec) {
            SyncManifestEntry linked_remote = remote_file_entry_for_body("linked/escape.txt", "escape", 6);
            SyncManifestDiffPlan linked_diff_plan;
            require(build_sync_manifest_diff_plan(empty_local, folder_manifest("folder-alpha", "device-bravo", 14, {linked_remote}), linked_diff_plan).ok,
                    "manifest diff plans symlink-ancestor fixture");
            SyncLocalApplyPlan symlink_rejected_apply_plan;
            require(!build_sync_local_apply_plan(linked_diff_plan, apply_options, symlink_rejected_apply_plan).ok,
                    "local apply plan rejects existing symlink ancestors below the synchronized root");
        }
        fs::remove_all(outside_link_target, apply_cleanup_ec);

        SyncLocalApplyOptions bad_staging_options = apply_options;
        bad_staging_options.staging_root_path = (apply_root / ".anonsync-stage").string();
        SyncLocalApplyPlan rejected_apply_plan;
        require(!build_sync_local_apply_plan(remote_newer_plan, bad_staging_options, rejected_apply_plan).ok,
                "local apply plan rejects staging roots inside the synchronized folder tree");
        fs::remove_all(apply_root, apply_cleanup_ec);
        fs::remove_all(apply_staging_root, apply_cleanup_ec);

        SyncFolderManifest wrong_folder_remote = remote_same;
        wrong_folder_remote.folder_id = "folder-bravo";
        for (auto& entry : wrong_folder_remote.entries) entry.folder_id = "folder-bravo";
        SyncManifestDiffPlan rejected_plan;
        require(!build_sync_manifest_diff_plan(manifest, wrong_folder_remote, rejected_plan).ok,
                "manifest diff rejects different folder ids");
        require(!build_sync_manifest_diff_plan(manifest, manifest, rejected_plan).ok,
                "manifest diff rejects same-device peer comparison");

        const std::string commit_key = sync_mutation_idempotency_key("commit_file_version", file);
        const std::string repeat_key = sync_mutation_idempotency_key("commit_file_version", file);
        const std::string publish_key = sync_mutation_idempotency_key("publish_manifest", file);
        require(commit_key == repeat_key, "sync mutation key is deterministic");
        require(commit_key.rfind("sync:v1:", 0) == 0 && commit_key.size() == 72, "sync mutation key has stable namespaced shape");
        require(commit_key != publish_key, "different sync operations receive different idempotency keys");

        bool unknown_operation_rejected = false;
        try {
            (void)sync_mutation_idempotency_key("generic_effect", file);
        } catch (const std::invalid_argument&) {
            unknown_operation_rejected = true;
        }
        require(unknown_operation_rejected, "generic effect operation rejected at sync-domain boundary");

        {
            const fs::path scheduler_executor_owned_checkpoint_db = fs::temp_directory_path() / ("anonsync-sync-session-checkpoint-scheduler-executor-owned-" + std::to_string(selftest_ticks) + ".sqlite");
            fs::remove(scheduler_executor_owned_checkpoint_db, apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_owned_checkpoint_db.string() + "-wal"), apply_cleanup_ec);
            fs::remove(fs::path(scheduler_executor_owned_checkpoint_db.string() + "-shm"), apply_cleanup_ec);
            sqlite_backup_file_or_throw(scheduler_executor_owned_seed_checkpoint_db,
                                        scheduler_executor_owned_checkpoint_db,
                                        "sync session checkpoint resume transfer scheduler executor owned selftest");
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions scheduler_execution_options =
                make_transfer_workorder_scheduler_execution_options(scheduler_executor_owned_checkpoint_db, 1005, "worker-charlie", 7, 10);
            scheduler_execution_options.max_scheduler_actions = pending_materialize_entry->chunks.size();
            SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult scheduler_execution_result;
            SyncValidationResult scheduler_execution_run = execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(scheduler_execution_options,
                                                                                                                                     scheduler_execution_result);
            require(scheduler_execution_run.ok &&
                    scheduler_execution_result.scheduler_execution_completed &&
                    scheduler_execution_result.scheduler_actions_returned == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.mutating_actions_planned == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.execute_owned_claim_groups_selected == 1 &&
                    scheduler_execution_result.execute_filter_keys == 1 &&
                    scheduler_execution_result.execute_owned_runs == 1 &&
                    scheduler_execution_result.claim_or_abandon_runs == 0 &&
                    scheduler_execution_result.execute_owned_claim_actions_selected == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.workorder_rows_completed == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.receipt_rows_upserted == pending_materialize_entry->chunks.size() &&
                    scheduler_execution_result.scheduler_result.scheduler_action_groups_deferred_by_limit == 0,
                    "sync session checkpoint resume transfer scheduler executor executes only the returned owned complete group");
            SyncSessionCheckpointResumeTransferWorkorderQueueOptions completed_queue_options = make_transfer_workorder_queue_options(scheduler_executor_owned_checkpoint_db, 1006);
            completed_queue_options.include_completed_workorders = true;
            SyncSessionCheckpointResumeTransferWorkorderQueueResult completed_queue_result;
            SyncValidationResult completed_queue_run = select_sync_session_checkpoint_resume_transfer_workorder_queue(completed_queue_options, completed_queue_result);
            require(completed_queue_run.ok &&
                    completed_queue_result.completed_rows_ignored == pending_materialize_entry->chunks.size() &&
                    completed_queue_result.queue_facts_returned == pending_materialize_entry->chunks.size(),
                    "sync session checkpoint resume transfer scheduler executor completed rows reappear only as completed audit facts");
        }
        const fs::path scan_root = fs::temp_directory_path() / ("anonsync-sync-scan-selftest-" + std::to_string(selftest_ticks));
        auto write_fixture = [&](const fs::path& p, const std::string& body) {
            std::error_code create_ec;
            fs::create_directories(p.parent_path(), create_ec);
            if (create_ec) throw std::runtime_error("could not create fixture parent: " + create_ec.message());
            std::ofstream out(p, std::ios::binary);
            if (!out) throw std::runtime_error("could not write fixture: " + p.string());
            out.write(body.data(), static_cast<std::streamsize>(body.size()));
            if (!out) throw std::runtime_error("could not finish fixture write: " + p.string());
        };
        auto cleanup_scan_root = [&]() {
            std::error_code cleanup_ec;
            fs::remove_all(scan_root, cleanup_ec);
        };

        try {
            cleanup_scan_root();
            write_fixture(scan_root / "media" / "photo.bin", std::string("abcdefghi", 9));
            write_fixture(scan_root / "docs" / "report.txt", "hello world!");
            write_fixture(scan_root / "empty.bin", "");

            SyncFolderScanOptions scan_options;
            scan_options.root_path = scan_root.string();
            scan_options.folder_id = "folder-alpha";
            scan_options.device_id = "device-alpha";
            scan_options.manifest_counter = 9;
            scan_options.lineage_counter = 3;
            scan_options.chunk_size_bytes = 5;

            SyncFolderManifest scanned;
            SyncValidationResult scan_result = build_sync_folder_manifest_from_directory(scan_options, scanned);
            require(scan_result.ok, "filesystem folder scan builds a manifest");
            require(validate_sync_folder_manifest(scanned).ok, "filesystem folder scan output validates as folder manifest");
            require(scanned.entries.size() == 3, "filesystem folder scan indexes regular files only");
            require(scanned.entries[0].path.value == "docs/report.txt" &&
                    scanned.entries[1].path.value == "empty.bin" &&
                    scanned.entries[2].path.value == "media/photo.bin",
                    "filesystem folder scan sorts entries by canonical manifest path");
            require(scanned.entries[0].size_bytes == 12 && scanned.entries[0].content_sha256 == sha256_hex("hello world!"),
                    "filesystem folder scan hashes file content");
            require(scanned.entries[0].chunks.size() == 3 &&
                    scanned.entries[0].chunks[0].offset == 0 && scanned.entries[0].chunks[0].length == 5 &&
                    scanned.entries[0].chunks[1].offset == 5 && scanned.entries[0].chunks[1].length == 5 &&
                    scanned.entries[0].chunks[2].offset == 10 && scanned.entries[0].chunks[2].length == 2,
                    "filesystem folder scan emits contiguous chunk ranges");
            require(scanned.entries[1].size_bytes == 0 && scanned.entries[1].chunks.empty() &&
                    scanned.entries[1].content_sha256 == sha256_hex(""),
                    "filesystem folder scan represents zero-byte files without chunks");
            require(scanned.entries[0].lineage.size() == 1 &&
                    scanned.entries[0].lineage[0].device_id == "device-alpha" &&
                    scanned.entries[0].lineage[0].counter == 3,
                    "filesystem folder scan stamps local lineage counter");

            const std::string scanned_digest = sync_folder_manifest_digest(scanned);
            SyncFolderManifest scanned_again;
            require(build_sync_folder_manifest_from_directory(scan_options, scanned_again).ok &&
                    sync_folder_manifest_digest(scanned_again) == scanned_digest,
                    "filesystem folder scan is deterministic for stable inputs");

            write_fixture(scan_root / "docs" / "report.txt", "hello sync?");
            SyncFolderManifest changed_scan;
            require(build_sync_folder_manifest_from_directory(scan_options, changed_scan).ok &&
                    sync_folder_manifest_digest(changed_scan) != scanned_digest,
                    "filesystem folder scan digest changes when content changes");

            write_fixture(scan_root / "bad.", "x");
            SyncFolderManifest invalid_path_scan;
            require(!build_sync_folder_manifest_from_directory(scan_options, invalid_path_scan).ok,
                    "filesystem folder scan rejects paths outside manifest policy");
            std::error_code remove_ec;
            fs::remove(scan_root / "bad.", remove_ec);

            std::error_code symlink_ec;
            fs::create_symlink(scan_root / "docs" / "report.txt", scan_root / "report-link", symlink_ec);
            if (!symlink_ec) {
                SyncFolderManifest symlink_scan;
                require(!build_sync_folder_manifest_from_directory(scan_options, symlink_scan).ok,
                        "filesystem folder scan rejects symlink entries");
                fs::remove(scan_root / "report-link", remove_ec);
            }
            cleanup_scan_root();
        } catch (...) {
            cleanup_scan_root();
            throw;
        }
    } catch (const std::exception& e) {
        ++failed;
        std::cerr << "sync domain model selftest exception: " << e.what() << "\n";
    }

    std::cout << "anonsync_core sync domain model selftest passed=" << passed << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 1;
}

}  // namespace anonsync
