#include "sqlite_path_security.hpp"
#include "sqlite_snapshot_seal.hpp"
#include "sync_replica_deployment_binding.hpp"
#include "sync_replica_deployment_manifest.hpp"
#include "sync_replica_file_payload_store.hpp"
#include "sync_replica_folder_process.hpp"
#include "sync_replica_folder_scan_owner.hpp"
#include "sync_replica_operational_database.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#include <charconv>
#include <cstdint>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

#if !defined(_WIN32)

namespace {

namespace fs = std::filesystem;

constexpr std::uint64_t kMaximumBootstrapSqliteImageBytes =
    64ULL * 1024ULL * 1024ULL;
constexpr std::uint64_t kMaximumBootstrapSqliteImagePages = 16384ULL;

[[nodiscard]] std::string json_quote(std::string_view value) {
    std::ostringstream output;
    output << '"';
    for (const unsigned char byte : value) {
        switch (byte) {
            case '"': output << "\\\""; break;
            case '\\': output << "\\\\"; break;
            case '\b': output << "\\b"; break;
            case '\f': output << "\\f"; break;
            case '\n': output << "\\n"; break;
            case '\r': output << "\\r"; break;
            case '\t': output << "\\t"; break;
            default:
                if (byte < 0x20U) {
                    output << "\\u00" << std::hex << std::setw(2)
                           << std::setfill('0')
                           << static_cast<unsigned int>(byte)
                           << std::dec << std::setfill(' ');
                } else {
                    output << static_cast<char>(byte);
                }
        }
    }
    output << '"';
    return output.str();
}

class Options final {
public:
    Options(int argc, char** argv, int first) {
        for (int index = first; index < argc; ++index) {
            std::string token(argv[index]);
            if (!token.starts_with("--") || token.size() <= 2U) {
                throw std::invalid_argument(
                    "unexpected positional argument: " + token);
            }
            token.erase(0U, 2U);
            std::string key;
            std::string value;
            const std::size_t equals = token.find('=');
            if (equals == std::string::npos) {
                key = std::move(token);
                if (index + 1 >= argc ||
                    std::string_view(argv[index + 1]).starts_with("--")) {
                    throw std::invalid_argument(
                        "missing value for --" + key);
                }
                value = argv[++index];
            } else {
                key = token.substr(0U, equals);
                value = token.substr(equals + 1U);
            }
            if (key.empty()) {
                throw std::invalid_argument("empty option name");
            }
            values_[std::move(key)].push_back(std::move(value));
        }
    }

    void require_only(std::initializer_list<std::string_view> allowed) const {
        const std::set<std::string_view> accepted(
            allowed.begin(), allowed.end());
        for (const auto& [key, ignored] : values_) {
            (void)ignored;
            if (!accepted.contains(key)) {
                throw std::invalid_argument("unknown option --" + key);
            }
        }
    }

    [[nodiscard]] bool has(std::string_view key) const {
        return values_.contains(std::string(key));
    }

    [[nodiscard]] std::string one(std::string_view key) const {
        const auto found = values_.find(std::string(key));
        if (found == values_.end()) {
            throw std::invalid_argument(
                "required option --" + std::string(key) + " is missing");
        }
        if (found->second.size() != 1U || found->second.front().empty()) {
            throw std::invalid_argument(
                "option --" + std::string(key) +
                " must appear exactly once with a nonempty value");
        }
        return found->second.front();
    }

private:
    std::map<std::string, std::vector<std::string>> values_;
};

[[nodiscard]] std::uint64_t parse_uint64(
    std::string_view text,
    std::string_view label) {
    std::uint64_t value = 0U;
    const char* const begin = text.data();
    const char* const end = begin + text.size();
    const auto parsed = std::from_chars(begin, end, value, 10);
    if (parsed.ec != std::errc{} || parsed.ptr != end) {
        throw std::invalid_argument(
            std::string(label) + " is not an unsigned decimal integer");
    }
    return value;
}

[[nodiscard]] std::uint64_t option_uint64_or(
    const Options& options,
    std::string_view key,
    std::uint64_t fallback) {
    return options.has(key)
        ? parse_uint64(options.one(key), "--" + std::string(key))
        : fallback;
}

[[nodiscard]] fs::path require_absolute_path(
    std::string value,
    std::string_view label) {
    fs::path path(std::move(value));
    if (path.empty() || !path.is_absolute() ||
        path.lexically_normal() != path) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a lexically normalized absolute path");
    }
    return path;
}

[[nodiscard]] anonsync::SyncSqliteDb
open_detached_bootstrap_database_or_throw(const std::string& label) {
    constexpr int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
        SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE | SQLITE_OPEN_MEMORY;
    sqlite3* raw = nullptr;
    const int opened = sqlite3_open_v2(":memory:", &raw, flags, nullptr);
    if (opened != SQLITE_OK) {
        const std::string message = anonsync::sqlite_error_message(
            raw, label + " open");
        if (raw != nullptr) (void)sqlite3_close_v2(raw);
        throw std::runtime_error(message);
    }
    if (raw == nullptr) {
        throw std::runtime_error(
            label + " detached open returned no SQLite handle");
    }
    const char* const filename = sqlite3_db_filename(raw, "main");
    if (filename == nullptr || *filename != '\0') {
        (void)sqlite3_close_v2(raw);
        throw std::runtime_error(
            label + " detached bootstrap database names a file");
    }

    anonsync::SyncSqliteDb database;
    {
        auto output = database.db.out();
        sqlite3** destination = output.get();
        *destination = raw;
        raw = nullptr;
    }
    anonsync::sqlite_exec_or_throw(
        database.db,
        "PRAGMA temp_store=MEMORY;"
        "PRAGMA foreign_keys=ON;"
        "PRAGMA trusted_schema=OFF;",
        label + " profile");
    return database;
}

void require_fresh_catalog_family_or_throw(
    const fs::path& catalog_path,
    const std::string& label) {
    anonsync::SqlitePathFamilyGuard guard =
        anonsync::guard_sqlite_path_family_or_throw(
            catalog_path, false, {"-journal", "-wal", "-shm"}, label);
    if (!guard.parent_exists()) {
        throw std::runtime_error(
            label + " parent directory does not exist");
    }
    if (guard.database_existed_at_preflight()) {
        throw std::runtime_error(
            label + " main database already exists");
    }
    guard.verify_sidecars_absent_or_throw(label + " sidecar proof");
}

[[nodiscard]] anonsync::SyncReplicaFolderConvergencePassLimits
pass_limits_from_options_or_throw(
    const Options& options,
    const anonsync::SyncReplicaDeploymentManifest& deployment) {
    anonsync::SyncReplicaFolderConvergencePassLimits limits =
        anonsync::sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
            deployment.max_payload_bytes,
            "anonsync_folder deployment limits");
    limits.maximum_entries = option_uint64_or(
        options, "maximum-entries", limits.maximum_entries);
    limits.maximum_regular_files = option_uint64_or(
        options, "maximum-regular-files", limits.maximum_regular_files);
    limits.maximum_file_bytes = option_uint64_or(
        options, "maximum-file-bytes", deployment.max_payload_bytes);
    limits.maximum_total_file_bytes = option_uint64_or(
        options, "maximum-total-file-bytes",
        limits.maximum_total_file_bytes);
    limits.maximum_relative_path_bytes = option_uint64_or(
        options, "maximum-relative-path-bytes",
        limits.maximum_relative_path_bytes);
    limits.maximum_directory_depth = option_uint64_or(
        options, "maximum-directory-depth",
        limits.maximum_directory_depth);
    limits.maximum_remote_paths = option_uint64_or(
        options, "maximum-remote-paths", limits.maximum_remote_paths);
    limits.maximum_remote_inspection_paths = option_uint64_or(
        options, "maximum-remote-inspection-paths",
        limits.maximum_remote_inspection_paths);
    if (limits.maximum_file_bytes > deployment.max_payload_bytes) {
        throw std::invalid_argument(
            "--maximum-file-bytes exceeds manifest max_payload_bytes");
    }
    return limits;
}

void attest_replica_database_or_throw(
    anonsync::SyncReplicaOperationalDatabase& database,
    const anonsync::SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        database.handle(),
        anonsync::sync_replica_primary_database_binding_or_throw(
            deployment, label + " binding"),
        label + " deployment binding");
}

int command_init(const Options& options) {
    options.require_only({"manifest"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path, "anonsync_folder init manifest");
    anonsync::validate_sync_replica_folder_process_deployment_or_throw(
        deployment, "anonsync_folder init");
    const fs::path catalog_path =
        anonsync::sync_replica_folder_catalog_path_or_throw(
            deployment, "anonsync_folder init");
    const auto catalog_binding =
        anonsync::sync_replica_folder_catalog_binding_or_throw(
            deployment, "anonsync_folder init");

    require_fresh_catalog_family_or_throw(
        catalog_path, "anonsync_folder init catalog preflight");

    auto replica_database =
        anonsync::SyncReplicaOperationalDatabase::open_or_throw(
            deployment.replica_db,
            anonsync::SyncReplicaOperationalDatabaseOpenDisposition::
                ExistingOperational,
            "anonsync_folder init replica database");
    attest_replica_database_or_throw(
        replica_database, deployment, "anonsync_folder init replica database");
    anonsync::SyncReplicaSqliteOwner replica_owner(
        replica_database.handle(), deployment.folder_id,
        deployment.local_actor, {}, "anonsync_folder init replica owner");

    anonsync::SyncReplicaFilePayloadStore payload_store(
        anonsync::sync_replica_deployment_identity_or_throw(
            deployment, "anonsync_folder init payload identity"),
        *deployment.payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        anonsync::sync_replica_folder_payload_store_limits_or_throw(
            deployment, "anonsync_folder init payload limits"),
        "anonsync_folder init payload store");

    anonsync::persistence::SealedSqliteSnapshot sealed = [&] {
        anonsync::SyncSqliteDb detached =
            open_detached_bootstrap_database_or_throw(
                "anonsync_folder init detached catalog");
        anonsync::initialize_sync_replica_folder_catalog_in_detached_image_or_throw(
            detached.db, catalog_binding, *deployment.files_root,
            replica_owner, payload_store,
            anonsync::sync_replica_folder_catalog_limits_or_throw(
                deployment, "anonsync_folder init catalog limits"),
            "anonsync_folder init detached catalog");
        auto source = detached.db.borrow();
        return anonsync::persistence::SealedSqliteSnapshot::capture_database(
            source.get(), "anonsync_folder init sealed catalog",
            anonsync::persistence::SqliteSnapshotSealPolicy{
                .maximum_bytes = kMaximumBootstrapSqliteImageBytes,
                .maximum_pages = kMaximumBootstrapSqliteImagePages,
            });
    }();

    require_fresh_catalog_family_or_throw(
        catalog_path, "anonsync_folder init catalog publication preflight");
    sealed.publish_exact_copy_atomically_create_new_or_throw(
        catalog_path, "anonsync_folder init catalog publication");

    auto catalog_database =
        anonsync::SyncReplicaOperationalDatabase::open_or_throw(
            catalog_path,
            anonsync::SyncReplicaOperationalDatabaseOpenDisposition::
                PublishedBootstrapCandidate,
            "anonsync_folder init published catalog");
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        catalog_database.handle(), catalog_binding,
        "anonsync_folder init published catalog binding");
    anonsync::SyncReplicaFolderScanOwner folder_owner(
        catalog_database.handle(), catalog_binding, *deployment.files_root,
        replica_owner, payload_store,
        anonsync::SyncReplicaFolderCatalogOpenDisposition::ExistingOnly,
        anonsync::sync_replica_folder_catalog_limits_or_throw(
            deployment, "anonsync_folder init open catalog limits"),
        "anonsync_folder init folder owner");
    const anonsync::SyncReplicaFolderCatalogSnapshot before_promotion =
        folder_owner.snapshot_or_throw();
    catalog_database.promote_published_bootstrap_candidate_or_throw(
        "anonsync_folder init catalog promotion");
    anonsync::attest_sync_replica_sqlite_deployment_binding_or_throw(
        catalog_database.handle(), catalog_binding,
        "anonsync_folder init post-promotion binding");
    const anonsync::SyncReplicaFolderCatalogSnapshot catalog =
        folder_owner.snapshot_or_throw();
    if (catalog != before_promotion || catalog.state_generation != 0U ||
        !catalog.entries.empty()) {
        throw std::logic_error(
            "anonsync_folder init catalog changed during promotion");
    }

    std::cout
        << "{\"command\":\"init\",\"terminal_class\":\"initialized\""
        << ",\"manifest_path\":"
        << json_quote(deployment.manifest_path.generic_string())
        << ",\"catalog_path\":"
        << json_quote(catalog_path.generic_string())
        << ",\"deployment_id\":" << json_quote(deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"local_device_id\":"
        << json_quote(deployment.local_actor.device_id)
        << ",\"local_epoch\":" << deployment.local_actor.epoch
        << ",\"catalog_generation\":" << catalog.state_generation
        << ",\"catalog_entry_count\":" << catalog.entries.size()
        << ",\"catalog_digest\":" << json_quote(catalog.catalog_digest)
        << ",\"sealed_image_sha256\":"
        << json_quote(sealed.sha256_hex())
        << ",\"sealed_image_bytes\":" << sealed.byte_count()
        << "}\n";
    return 0;
}

int command_run(const Options& options) {
    options.require_only({
        "manifest", "maximum-entries", "maximum-regular-files",
        "maximum-file-bytes",
        "maximum-total-file-bytes", "maximum-relative-path-bytes",
        "maximum-directory-depth", "maximum-remote-paths",
        "maximum-remote-inspection-paths"});
    const fs::path manifest_path = require_absolute_path(
        options.one("manifest"), "--manifest");
    const anonsync::SyncReplicaDeploymentManifest deployment =
        anonsync::read_sync_replica_deployment_manifest_or_throw(
            manifest_path, "anonsync_folder run manifest");
    anonsync::validate_sync_replica_folder_process_deployment_or_throw(
        deployment, "anonsync_folder run");
    const auto pass_limits =
        pass_limits_from_options_or_throw(options, deployment);

    anonsync::SyncReplicaFolderProcessOwner process_owner(
        deployment, "anonsync_folder run process owner");

    const auto catalog_before = process_owner.catalog_snapshot_or_throw();
    const auto replica_before = process_owner.replica_snapshot_or_throw();
    const auto report = process_owner.run_convergence_pass_or_throw(pass_limits);
    const auto catalog_after = process_owner.catalog_snapshot_or_throw();
    const auto replica_after = process_owner.replica_snapshot_or_throw();

    std::cout
        << "{\"command\":\"run\",\"terminal_class\":\"completed\""
        << ",\"manifest_path\":"
        << json_quote(deployment.manifest_path.generic_string())
        << ",\"catalog_path\":"
        << json_quote(process_owner.catalog_path().generic_string())
        << ",\"deployment_id\":" << json_quote(deployment.deployment_id)
        << ",\"folder_id\":" << json_quote(deployment.folder_id)
        << ",\"catalog_generation_before\":"
        << catalog_before.state_generation
        << ",\"catalog_generation_after\":"
        << catalog_after.state_generation
        << ",\"catalog_entry_count_before\":"
        << catalog_before.entries.size()
        << ",\"catalog_entry_count_after\":"
        << catalog_after.entries.size()
        << ",\"catalog_digest_before\":"
        << json_quote(catalog_before.catalog_digest)
        << ",\"catalog_digest_after\":"
        << json_quote(catalog_after.catalog_digest)
        << ",\"replica_generation_before\":"
        << replica_before.state_generation
        << ",\"replica_generation_after\":"
        << replica_after.state_generation
        << ",\"replica_cutpoint_before\":"
        << json_quote(replica_before.cutpoint_digest)
        << ",\"replica_cutpoint_after\":"
        << json_quote(replica_after.cutpoint_digest)
        << ",\"visited_entries\":"
        << report.traversal.visited_entry_count
        << ",\"visited_directories\":"
        << report.traversal.visited_directory_count
        << ",\"regular_files\":"
        << report.traversal.regular_file_count
        << ",\"ignored_symbolic_links\":"
        << report.traversal.ignored_symbolic_link_count
        << ",\"ignored_special_files\":"
        << report.traversal.ignored_special_file_count
        << ",\"ignored_internal_artifacts\":"
        << report.traversal.ignored_internal_artifact_count
        << ",\"metadata_only_regular_files\":"
        << report.traversal.metadata_only_regular_file_count
        << ",\"metadata_only_regular_file_logical_bytes\":"
        << report.traversal.metadata_only_regular_file_logical_bytes
        << ",\"metadata_only_pruned_directories\":"
        << report.traversal.metadata_only_pruned_directory_count
        << ",\"classified_regular_file_bytes\":"
        << report.traversal.classified_regular_file_bytes
        << ",\"local_scan_epoch\":" << report.local_scan_epoch
        << ",\"completed_local_scan_epoch\":"
        << (report.completed_local_scan_epoch ? "true" : "false")
        << ",\"restarted_local_scan_epoch\":"
        << (report.restarted_local_scan_epoch ? "true" : "false")
        << ",\"local_scan_seen_path_count\":"
        << report.local_scan_seen_path_count
        << ",\"local_scan_resume_after_path\":"
        << json_quote(report.local_scan_resume_after_path)
        << ",\"local_scan_stop_reason\":"
        << json_quote(
               anonsync::sync_replica_folder_traversal_stop_reason_name(
                   report.local_scan_stop_reason))
        << ",\"local_directory_enumeration_passes\":"
        << report.local_directory_enumeration_pass_count
        << ",\"local_peak_buffered_directory_component_batch_count\":"
        << report.local_peak_buffered_directory_component_batch_count
        << ",\"local_peak_simultaneously_buffered_directory_component_count\":"
        << report.local_peak_simultaneously_buffered_directory_component_count
        << ",\"used_idle_fast_path\":"
        << (report.used_idle_fast_path ? "true" : "false")
        << ",\"payload_snapshot_handoffs\":"
        << report.payload_snapshot_handoff_count
        << ",\"payload_snapshot_handoff_entries\":"
        << report.payload_snapshot_handoff_entry_count
        << ",\"payload_snapshot_observations\":"
        << report.payload_snapshot_observation_count
        << ",\"payload_snapshot_observed_entries\":"
        << report.payload_snapshot_observed_entry_count
        << ",\"exact_local_file_bytes\":"
        << report.exact_local_file_bytes
        << ",\"exact_remote_file_bytes\":"
        << report.exact_remote_file_bytes
        << ",\"payload_mutation_batches\":"
        << report.payload_mutation_batch_count
        << ",\"payload_mutation_full_scans\":"
        << report.payload_mutation_full_scan_count
        << ",\"payload_mutation_scan_hashed_entries\":"
        << report.payload_mutation_scan_hashed_entry_count
        << ",\"payload_mutation_scan_hashed_bytes\":"
        << report.payload_mutation_scan_hashed_bytes
        << ",\"payload_mutation_scan_reused_entries\":"
        << report.payload_mutation_scan_reused_entry_count
        << ",\"payload_mutation_scan_reused_bytes\":"
        << report.payload_mutation_scan_reused_bytes
        << ",\"payload_mutation_scan_process_reused_entries\":"
        << report.payload_mutation_scan_process_reused_entry_count
        << ",\"payload_mutation_scan_process_reused_bytes\":"
        << report.payload_mutation_scan_process_reused_bytes
        << ",\"payload_mutation_scan_durable_reused_entries\":"
        << report.payload_mutation_scan_durable_reused_entry_count
        << ",\"payload_mutation_scan_durable_reused_bytes\":"
        << report.payload_mutation_scan_durable_reused_bytes
        << ",\"payload_mutation_puts\":"
        << report.payload_mutation_put_count
        << ",\"payload_mutation_source_bytes\":"
        << report.payload_mutation_source_bytes
        << ",\"payload_mutation_work_bytes\":"
        << report.payload_mutation_work_bytes
        << ",\"payload_mutation_peak_batch_puts\":"
        << report.payload_mutation_peak_batch_put_count
        << ",\"payload_mutation_peak_batch_work_bytes\":"
        << report.payload_mutation_peak_batch_work_bytes
        << ",\"payload_mutation_inserted\":"
        << report.payload_mutation_inserted_count
        << ",\"payload_mutation_already_present\":"
        << report.payload_mutation_already_present_count
        << ",\"local_published\":" << report.local_published_count
        << ",\"local_identity_preserving_renames\":"
        << report.local_identity_preserving_rename_count
        << ",\"local_adopted_visible\":"
        << report.local_adopted_visible_count
        << ",\"local_catalog_no_op\":"
        << report.local_catalog_no_op_count
        << ",\"local_catalog_refreshed\":"
        << report.local_catalog_refreshed_count
        << ",\"remote_applied\":" << report.remote_applied_count
        << ",\"remote_adopted_exact\":"
        << report.remote_adopted_exact_count
        << ",\"remote_catalog_no_op\":"
        << report.remote_catalog_no_op_count
        << ",\"remote_apply_operations\":"
        << report.remote_apply_operation_count
        << ",\"remote_metadata_only_files\":"
        << report.remote_metadata_only_file_count
        << ",\"remote_metadata_only_already_absent_files\":"
        << report.remote_metadata_only_already_absent_file_count
        << ",\"remote_targeted_catalog_path_cutpoints\":"
        << report.remote_targeted_catalog_path_cutpoint_count
        << ",\"remote_targeted_replica_path_cutpoints\":"
        << report.remote_targeted_replica_path_cutpoint_count
        << ",\"remote_metadata_only_dematerialization_attempts\":"
        << report.remote_metadata_only_dematerialization_attempt_count
        << ",\"remote_metadata_only_dematerialized_files\":"
        << report.remote_metadata_only_dematerialized_file_count
        << ",\"remote_metadata_only_dematerialized_bytes\":"
        << report.remote_metadata_only_dematerialized_bytes
        << ",\"remote_metadata_only_dematerialization_blocked_files\":"
        << report.remote_metadata_only_dematerialization_blocked_file_count
        << ",\"remote_metadata_only_dematerialization_payload_unavailable\":"
        << report.remote_metadata_only_dematerialization_payload_unavailable_count
        << ",\"local_metadata_only_absence_suppressions\":"
        << report.local_metadata_only_absence_suppressed_count
        << ",\"local_selection_change_absence_suppressions\":"
        << report.local_selection_change_absence_suppressed_count
        << ",\"remote_inspected_paths\":"
        << report.remote_inspected_path_count
        << ",\"remote_acknowledged_paths\":"
        << report.remote_acknowledged_path_count
        << ",\"deferred_remote_inspection_paths\":"
        << report.deferred_remote_inspection_path_count
        << ",\"remote_inspection_sweep_started_after_path\":"
        << json_quote(report.remote_inspection_sweep_started_after_path)
        << ",\"remote_inspection_sweep_seen_path_count\":"
        << report.remote_inspection_sweep_seen_path_count
        << ",\"completed_remote_inspection_sweep\":"
        << (report.completed_remote_inspection_sweep ? "true" : "false")
        << ",\"remote_inspection_sweep_had_unresolved_paths\":"
        << (report.remote_inspection_sweep_had_unresolved_paths
                ? "true" : "false")
        << ",\"remote_inspection_terminal_cutpoint_reproved\":"
        << (report.remote_inspection_terminal_cutpoint_reproved
                ? "true" : "false")
        << ",\"remote_inspection_terminal_catalog_digest\":"
        << json_quote(report.remote_inspection_terminal_catalog_digest)
        << ",\"remote_inspection_terminal_visible_state_digest\":"
        << json_quote(
               report.remote_inspection_terminal_visible_state_digest)
        << ",\"deferred_remote_apply_candidates\":"
        << report.deferred_remote_apply_candidate_count
        << ",\"remote_apply_stop_reason\":"
        << json_quote(
               anonsync::sync_replica_folder_remote_apply_stop_reason_name(
                   report.remote_apply_stop_reason))
        << ",\"skipped_conflicted_remote_paths\":"
        << report.skipped_conflicted_remote_path_count
        << ",\"skipped_tombstone_remote_paths\":"
        << report.skipped_tombstone_remote_path_count
        << ",\"deferred_unadjudicated_local_absence_remote_files\":"
        << report.deferred_unadjudicated_local_absence_remote_file_count
        << ",\"limits\":{\"maximum_entries\":"
        << pass_limits.maximum_entries
        << ",\"maximum_regular_files\":"
        << pass_limits.maximum_regular_files
        << ",\"maximum_file_bytes\":"
        << pass_limits.maximum_file_bytes
        << ",\"maximum_total_file_bytes\":"
        << pass_limits.maximum_total_file_bytes
        << ",\"maximum_relative_path_bytes\":"
        << pass_limits.maximum_relative_path_bytes
        << ",\"maximum_directory_depth\":"
        << pass_limits.maximum_directory_depth
        << ",\"maximum_remote_paths\":"
        << pass_limits.maximum_remote_paths
        << ",\"maximum_remote_inspection_paths\":"
        << pass_limits.maximum_remote_inspection_paths
        << ",\"maximum_remote_apply_operations\":"
        << pass_limits.maximum_remote_apply_operations << "}}\n";
    return 0;
}

void print_usage(std::ostream& output) {
    output
        << "AnonSync configured-folder process\n\n"
        << "Usage:\n"
        << "  anonsync_folder init --manifest ABSOLUTE_JSON\n"
        << "  anonsync_folder run --manifest ABSOLUTE_JSON "
           "[--maximum-entries N] [--maximum-regular-files N] "
           "[--maximum-file-bytes N] "
           "[--maximum-total-file-bytes N] "
           "[--maximum-relative-path-bytes N] "
           "[--maximum-directory-depth N] [--maximum-remote-paths N] "
           "[--maximum-remote-inspection-paths N]\n\n"
        << "init is the sole folder-catalog bootstrap authority. The catalog "
           "path is derived from the deployment manifest and published as one "
           "complete create-new sealed SQLite image. run opens every selected "
           "store existing-only and performs one bounded synchronous pass. "
           "Neither command is a watcher, retry loop, or daemon. JSON is "
           "written to stdout and diagnostics to stderr.\n";
}

void emit_error(
    std::string_view command,
    std::string_view error_code,
    std::string_view message) {
    std::cout
        << "{\"command\":" << json_quote(command)
        << ",\"terminal_class\":\"stopped\",\"error_code\":"
        << json_quote(error_code)
        << ",\"message\":" << json_quote(message) << "}\n";
    std::cerr << "anonsync_folder: " << message << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    std::string command = argc >= 2 ? argv[1] : "";
    try {
        if (argc < 2 || command == "--help" || command == "help") {
            print_usage(std::cout);
            return argc < 2 ? 2 : 0;
        }
        const Options options(argc, argv, 2);
        if (command == "init") return command_init(options);
        if (command == "run") return command_run(options);
        throw std::invalid_argument("unknown command: " + command);
    } catch (const std::invalid_argument& error) {
        emit_error(command, "invalid_arguments", error.what());
        return 2;
    } catch (const std::exception& error) {
        emit_error(command, "operation_stopped", error.what());
        return 1;
    }
}

#else

int main() {
    std::cerr << "anonsync_folder is currently supported only on Linux\n";
    return 1;
}

#endif
