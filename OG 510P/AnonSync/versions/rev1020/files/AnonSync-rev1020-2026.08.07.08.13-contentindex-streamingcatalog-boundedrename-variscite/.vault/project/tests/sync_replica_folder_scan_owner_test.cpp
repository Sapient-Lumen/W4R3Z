#include "sha256_digest.hpp"
#include "sync_atomic_file_publication_internal.hpp"
#include "sync_directory_authority.hpp"
#include "sync_posix_descriptor_snapshot.hpp"
#include "sync_replica_folder_scan_owner.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_outbox_clock.hpp"
#include "sync_replica_sqlite_owner.hpp"
#include "sync_sqlite_support.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <array>
#include <chrono>
#include <cerrno>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <memory>
#include <optional>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>
#include <fcntl.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

std::uint64_t checks = 0U;

struct ScanJournalTrace final {
    std::uint64_t insert_count = 0U;
    std::uint64_t progress_update_count = 0U;
};

struct CatalogEntryReadTrace final {
    std::uint64_t entry_table_read_count = 0U;
    std::uint64_t complete_projection_read_count = 0U;
    std::uint64_t exact_path_read_count = 0U;
};

struct ReplicaPathReadTrace final {
    std::uint64_t exact_visible_path_read_count = 0U;
    std::uint64_t complete_visible_projection_read_count = 0U;
    std::uint64_t exact_operation_read_count = 0U;
    std::uint64_t complete_operation_projection_read_count = 0U;
};

struct TerminalCutpointFenceTrace final {
    anonsync::SyncReplicaSqliteOwner* competing_owner = nullptr;
    bool progress_update_observed = false;
    bool competing_writer_blocked = false;
    bool competing_writer_succeeded = false;
    bool competing_writer_failed_unexpectedly = false;
};

struct ReplicaCutpointMovementTrace final {
    anonsync::SyncReplicaSqliteOwner* competing_owner = nullptr;
    std::uint64_t remote_progress_select_count = 0U;
    bool competing_writer_attempted = false;
    bool competing_writer_succeeded = false;
    bool competing_writer_failed = false;
};

struct CatalogProgressMovementTrace final {
    sqlite3* competing_catalog_db = nullptr;
    std::uint64_t remote_progress_select_count = 0U;
    bool terminal_begin_armed = false;
    bool competing_writer_attempted = false;
    bool competing_writer_succeeded = false;
    bool competing_writer_failed = false;
};

int count_catalog_entry_reads(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (trace_kind != SQLITE_TRACE_STMT || context == nullptr ||
        statement_pointer == nullptr) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr) return 0;
    const std::string_view text(sql);
    if (text.find("sync_replica_folder_catalog_entries") !=
            std::string_view::npos &&
        text.find("SELECT") != std::string_view::npos) {
        auto& trace = *static_cast<CatalogEntryReadTrace*>(context);
        ++trace.entry_table_read_count;
        if (text.find("ORDER BY canonical_path") !=
            std::string_view::npos) {
            ++trace.complete_projection_read_count;
        }
        if (text.find("WHERE canonical_path=?") !=
            std::string_view::npos) {
            ++trace.exact_path_read_count;
        }
    }
    return 0;
}

int count_replica_path_reads(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (trace_kind != SQLITE_TRACE_STMT || context == nullptr ||
        statement_pointer == nullptr) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr) return 0;
    auto& trace = *static_cast<ReplicaPathReadTrace*>(context);
    const std::string_view text(sql);
    if (text.find("FROM main.sync_replica_visible") !=
        std::string_view::npos) {
        if (text.find("WHERE canonical_path=?") !=
            std::string_view::npos) {
            ++trace.exact_visible_path_read_count;
        }
        if (text.find("ORDER BY canonical_path,visible_ordinal") !=
            std::string_view::npos) {
            ++trace.complete_visible_projection_read_count;
        }
    }
    if (text.find("FROM main.sync_replica_operations") !=
        std::string_view::npos) {
        if (text.find("WHERE operation_id=?") !=
            std::string_view::npos) {
            ++trace.exact_operation_read_count;
        }
        if (text.find("ORDER BY operation_id") !=
            std::string_view::npos) {
            ++trace.complete_operation_projection_read_count;
        }
    }
    return 0;
}

int count_scan_journal_statements(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (trace_kind != SQLITE_TRACE_STMT || context == nullptr ||
        statement_pointer == nullptr) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr) return 0;
    auto& trace = *static_cast<ScanJournalTrace*>(context);
    const std::string_view text(sql);
    if (text.find(
            "INSERT INTO main.sync_replica_folder_catalog_scan_seen") !=
        std::string_view::npos) {
        ++trace.insert_count;
    }
    if (text.find(
            "UPDATE main.sync_replica_folder_catalog_scan_progress SET") !=
        std::string_view::npos) {
        ++trace.progress_update_count;
    }
    return 0;
}

int probe_terminal_cutpoint_fence(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (trace_kind != SQLITE_TRACE_STMT || context == nullptr ||
        statement_pointer == nullptr) {
        return 0;
    }
    auto& trace = *static_cast<TerminalCutpointFenceTrace*>(context);
    if (trace.progress_update_observed || trace.competing_owner == nullptr) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr ||
        std::string_view(sql).find(
            "UPDATE main.sync_replica_folder_catalog_remote_apply_progress ") ==
            std::string_view::npos) {
        return 0;
    }

    trace.progress_update_observed = true;
    try {
        (void)trace.competing_owner->create_local_tombstone_or_throw(
            "terminal-fence-probe.txt", std::span<const std::string>{});
        trace.competing_writer_succeeded = true;
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find("database is locked") !=
            std::string_view::npos) {
            trace.competing_writer_blocked = true;
        } else {
            trace.competing_writer_failed_unexpectedly = true;
        }
    } catch (...) {
        trace.competing_writer_failed_unexpectedly = true;
    }
    return 0;
}

int advance_replica_after_projection_snapshot(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (trace_kind != SQLITE_TRACE_STMT || context == nullptr ||
        statement_pointer == nullptr) {
        return 0;
    }
    auto& trace = *static_cast<ReplicaCutpointMovementTrace*>(context);
    if (trace.competing_writer_attempted || trace.competing_owner == nullptr) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr ||
        std::string_view(sql).find(
            "SELECT resume_after_path,inspection_sweep_basis_digest,") ==
            std::string_view::npos) {
        return 0;
    }
    ++trace.remote_progress_select_count;
    if (trace.remote_progress_select_count != 2U) return 0;

    trace.competing_writer_attempted = true;
    try {
        (void)trace.competing_owner->create_local_tombstone_or_throw(
            "advanced-projection.txt", std::span<const std::string>{});
        trace.competing_writer_succeeded = true;
    } catch (...) {
        trace.competing_writer_failed = true;
    }
    return 0;
}

int advance_catalog_progress_before_terminal_lock(
    unsigned trace_kind,
    void* context,
    void* statement_pointer,
    void*) noexcept {
    if (trace_kind != SQLITE_TRACE_STMT || context == nullptr ||
        statement_pointer == nullptr) {
        return 0;
    }
    auto& trace = *static_cast<CatalogProgressMovementTrace*>(context);
    if (trace.competing_writer_attempted ||
        trace.competing_catalog_db == nullptr) {
        return 0;
    }
    const char* sql = sqlite3_sql(
        static_cast<sqlite3_stmt*>(statement_pointer));
    if (sql == nullptr) return 0;
    const std::string_view text(sql);
    if (text.find(
            "SELECT resume_after_path,inspection_sweep_basis_digest,") !=
        std::string_view::npos) {
        ++trace.remote_progress_select_count;
        if (trace.remote_progress_select_count == 2U) {
            trace.terminal_begin_armed = true;
        }
        return 0;
    }
    if (!trace.terminal_begin_armed || text.find("BEGIN IMMEDIATE") == std::string_view::npos) {
        return 0;
    }

    trace.competing_writer_attempted = true;
    try {
        anonsync::sqlite_exec_or_throw(
            trace.competing_catalog_db,
            "UPDATE "
            "sync_replica_folder_catalog_remote_apply_progress SET "
            "resume_after_path='moved-progress.txt' WHERE id=1;",
            "terminal catalog-progress movement");
        trace.competing_writer_succeeded = true;
    } catch (...) {
        trace.competing_writer_failed = true;
    }
    return 0;
}

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Callable>
void require_error(
    Callable&& callable,
    std::string_view expected_fragment,
    const std::string& message) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const std::exception& error) {
        if (std::string_view(error.what()).find(expected_fragment) !=
            std::string_view::npos) {
            return;
        }
        fail(message + ": unexpected error: " + error.what());
    }
    fail(message + ": no error was thrown");
}

class TemporaryDirectory final {
public:
    explicit TemporaryDirectory(std::string_view stem) {
        const auto tick = std::chrono::steady_clock::now()
                              .time_since_epoch()
                              .count();
        path_ = fs::temp_directory_path() /
                (std::string(stem) + "-" +
                 std::to_string(static_cast<unsigned long long>(::getpid())) +
                 "-" + std::to_string(tick));
        fs::create_directory(path_);
        make_private_directory(path_);
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    ~TemporaryDirectory() {
        std::error_code ignored;
        fs::remove_all(path_, ignored);
    }

    [[nodiscard]] fs::path make_directory(std::string_view name) const {
        const fs::path path = path_ / std::string(name);
        fs::create_directory(path);
        make_private_directory(path);
        return path;
    }

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

private:
    static void make_private_directory(const fs::path& path) {
        if (::chmod(path.c_str(), 0700) != 0) {
            fail("could not make folder-scan fixture private");
        }
    }

    fs::path path_;
};

void write_file(const fs::path& path, std::string_view bytes) {
    fs::create_directories(path.parent_path());
    std::ofstream stream(path, std::ios::binary | std::ios::trunc);
    if (!stream) fail("could not create folder-scan test file");
    stream.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    if (!stream) fail("could not write folder-scan test file");
    stream.close();
    if (!stream) fail("could not close folder-scan test file");
}

struct StreamingFileObservation final {
    std::uint64_t size_bytes = 0U;
    std::string content_sha256;
};

[[nodiscard]] StreamingFileObservation create_sparse_file_and_hash(
    const fs::path& path,
    std::uint64_t size_bytes) {
    if (size_bytes < 2U ||
        size_bytes >
            static_cast<std::uint64_t>(std::numeric_limits<off_t>::max())) {
        fail("large folder-scan fixture size is invalid");
    }
    fs::create_directories(path.parent_path());
    int descriptor;
    do {
        descriptor = ::open(
            path.c_str(), O_RDWR | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW,
            0600);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) fail("could not create large folder-scan fixture");

    try {
        int truncate_result;
        do {
            truncate_result =
                ::ftruncate(descriptor, static_cast<off_t>(size_bytes));
        } while (truncate_result != 0 && errno == EINTR);
        if (truncate_result != 0) {
            fail("could not size large folder-scan fixture");
        }
        const char first = static_cast<char>(0x51);
        const char last = static_cast<char>(0xa7);
        ssize_t first_written;
        do {
            first_written = ::pwrite(descriptor, &first, 1U, 0);
        } while (first_written < 0 && errno == EINTR);
        ssize_t last_written;
        do {
            last_written = ::pwrite(
                descriptor, &last, 1U,
                static_cast<off_t>(size_bytes - 1U));
        } while (last_written < 0 && errno == EINTR);
        if (first_written != 1 || last_written != 1) {
            fail("could not mark large folder-scan fixture extents");
        }
        int sync_result;
        do {
            sync_result = ::fsync(descriptor);
        } while (sync_result != 0 && errno == EINTR);
        if (sync_result != 0) {
            fail("could not synchronize large folder-scan fixture");
        }
        const auto observed =
            anonsync::hash_sync_posix_regular_file_descriptor_or_throw(
                descriptor, size_bytes,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "large folder-scan fixture");
        if (::close(descriptor) != 0) {
            descriptor = -1;
            fail("could not close large folder-scan fixture");
        }
        descriptor = -1;
        return {observed.metadata.size_bytes, observed.content_sha256};
    } catch (...) {
        if (descriptor >= 0) (void)::close(descriptor);
        throw;
    }
}

[[nodiscard]] StreamingFileObservation hash_file_path(
    const fs::path& path,
    std::uint64_t maximum_bytes) {
    int descriptor;
    do {
        descriptor =
            ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) fail("could not open streamed folder-scan result");
    try {
        const auto observed =
            anonsync::hash_sync_posix_regular_file_descriptor_or_throw(
                descriptor, maximum_bytes,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "streamed folder-scan result");
        if (::close(descriptor) != 0) {
            descriptor = -1;
            fail("could not close streamed folder-scan result");
        }
        descriptor = -1;
        return {observed.metadata.size_bytes, observed.content_sha256};
    } catch (...) {
        if (descriptor >= 0) (void)::close(descriptor);
        throw;
    }
}

[[nodiscard]] std::string read_file(const fs::path& path) {
    std::ifstream stream(path, std::ios::binary);
    if (!stream) fail("could not open folder-scan test file for reading");
    return std::string(
        std::istreambuf_iterator<char>(stream),
        std::istreambuf_iterator<char>());
}

[[nodiscard]] std::uint64_t file_inode(const fs::path& path) {
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0) {
        fail("could not lstat folder-scan test file");
    }
    return static_cast<std::uint64_t>(status.st_ino);
}

[[nodiscard]] anonsync::SyncPosixRegularFileSnapshotMetadata
observe_regular_file_metadata(const fs::path& path) {
    int flags = O_RDONLY | O_NONBLOCK;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    int descriptor;
    do {
        descriptor = ::open(path.c_str(), flags);
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) fail("could not open apply test predecessor");
    try {
        const auto metadata =
            anonsync::observe_sync_posix_regular_file_descriptor_or_throw(
                descriptor,
                anonsync::SyncPosixDescriptorLinkPolicy::stable_named_object,
                "folder apply test predecessor");
        (void)::close(descriptor);
        return metadata;
    } catch (...) {
        (void)::close(descriptor);
        throw;
    }
}

[[nodiscard]] std::span<const unsigned char> byte_span(
    const std::string& bytes) noexcept {
    return std::span<const unsigned char>(
        reinterpret_cast<const unsigned char*>(bytes.data()), bytes.size());
}

void append_test_u64(
    anonsync::Sha256DigestBuilder& digest,
    std::uint64_t value) {
    std::array<char, 8U> encoded{};
    for (std::size_t index = encoded.size(); index != 0U; --index) {
        encoded[index - 1U] = static_cast<char>(value & 0xffU);
        value >>= 8U;
    }
    digest.update(std::string_view(encoded.data(), encoded.size()));
}

void append_test_string(
    anonsync::Sha256DigestBuilder& digest,
    std::string_view value) {
    append_test_u64(digest, static_cast<std::uint64_t>(value.size()));
    digest.update(value);
}

[[nodiscard]] std::string
retention_unreferenced_candidate_set_digest_for_test(
    std::vector<std::pair<std::string, std::uint64_t>> candidates) {
    std::sort(candidates.begin(), candidates.end());
    anonsync::Sha256DigestBuilder digest;
    append_test_string(
        digest,
        "anonsync:sync-replica-retention-plan-unreferenced-candidates:v1");
    std::uint64_t total_bytes = 0U;
    for (const auto& [content_sha256, size_bytes] : candidates) {
        append_test_string(digest, content_sha256);
        append_test_u64(digest, size_bytes);
        if (size_bytes >
            std::numeric_limits<std::uint64_t>::max() - total_bytes) {
            fail("retention candidate test bytes overflow");
        }
        total_bytes += size_bytes;
    }
    append_test_u64(
        digest, static_cast<std::uint64_t>(candidates.size()));
    append_test_u64(digest, total_bytes);
    return digest.finish_hex();
}

[[nodiscard]] std::string retention_durable_candidate_witness_for_test(
    const anonsync::SyncReplicaRetentionPlan& plan,
    std::string_view folder_id,
    std::string_view candidate_set_digest) {
    anonsync::Sha256DigestBuilder digest;
    append_test_string(
        digest,
        "anonsync:sync-replica-retention-plan-durable-candidate-witness:v2");
    append_test_string(digest, folder_id);
    append_test_string(
        digest, plan.source_replica_database_incarnation_sha256);
    append_test_u64(
        digest, plan.source_replica_database_recovery_epoch);
    append_test_u64(digest, plan.source_replica_state_generation);
    append_test_string(digest, plan.source_operation_set_digest);
    append_test_string(digest, plan.source_evidence_set_digest);
    append_test_string(
        digest, plan.source_historical_version_pin_set_digest);
    append_test_string(digest, plan.source_visible_state_digest);
    append_test_string(digest, plan.source_payload_snapshot_digest);
    append_test_string(
        digest, plan.source_payload_transient_namespace_digest);
    append_test_u64(digest, plan.payload_transient_entry_count);
    append_test_u64(digest, plan.payload_transient_bytes);
    append_test_u64(digest, plan.payload_transient_reserved_bytes);
    append_test_string(digest, candidate_set_digest);
    append_test_u64(
        digest,
        plan.unreferenced_by_retained_file_operations.payload_count);
    append_test_u64(
        digest,
        plan.unreferenced_by_retained_file_operations.payload_bytes);
    return digest.finish_hex();
}

[[nodiscard]] std::string retention_writer_fenced_candidate_page_digest_for_test(
    const anonsync::SyncReplicaRetentionPlan& plan,
    std::string_view folder_id) {
    anonsync::Sha256DigestBuilder digest;
    append_test_string(
        digest,
        "anonsync:sync-replica-retention-plan-writer-fenced-candidate-page:v2");
    append_test_string(
        digest, anonsync::kSyncReplicaFilePayloadUseLeaseProtocol);
    append_test_string(digest, folder_id);
    append_test_string(
        digest, plan.source_replica_database_incarnation_sha256);
    append_test_u64(
        digest, plan.source_replica_database_recovery_epoch);
    append_test_u64(digest, plan.source_replica_state_generation);
    append_test_string(digest, plan.source_operation_set_digest);
    append_test_string(digest, plan.source_evidence_set_digest);
    append_test_string(
        digest, plan.source_historical_version_pin_set_digest);
    append_test_string(digest, plan.source_payload_snapshot_digest);
    append_test_string(digest, plan.unreferenced_candidate_set_digest);
    append_test_u64(
        digest, plan.query.start_after_content_sha256.has_value() ? 1U : 0U);
    if (plan.query.start_after_content_sha256.has_value()) {
        append_test_string(digest, *plan.query.start_after_content_sha256);
    }
    append_test_u64(digest, plan.query.maximum_entries);
    append_test_u64(
        digest, plan.writer_fenced_candidate_page_entry_count);
    for (const auto& entry : plan.entries) {
        append_test_string(digest, entry.content_sha256);
        append_test_u64(digest, entry.size_bytes);
        append_test_u64(
            digest, static_cast<std::uint64_t>(entry.disposition));
        append_test_u64(
            digest,
            static_cast<std::uint64_t>(entry.payload_use_disposition));
    }
    append_test_u64(digest, plan.returned_unreferenced_candidate_count);
    append_test_u64(
        digest,
        plan.returned_candidate_payload_use_exclusive_available_count);
    append_test_u64(
        digest, plan.returned_candidate_payload_use_busy_count);
    return digest.finish_hex();
}

[[nodiscard]] std::string retention_deletion_free_mark_digest_for_test(
    const anonsync::SyncReplicaRetentionPlan& plan,
    std::string_view folder_id,
    std::string_view candidate_set_digest) {
    anonsync::Sha256DigestBuilder digest;
    append_test_string(
        digest,
        "anonsync:sync-replica-retention-plan-deletion-free-mark:v5");
    append_test_string(
        digest, anonsync::kSyncReplicaFilePayloadUseLeaseProtocol);
    append_test_string(digest, folder_id);
    append_test_string(
        digest, plan.source_replica_database_incarnation_sha256);
    append_test_u64(
        digest, plan.source_replica_database_recovery_epoch);
    append_test_u64(digest, plan.source_replica_state_generation);
    append_test_string(digest, plan.source_operation_set_digest);
    append_test_string(digest, plan.source_evidence_set_digest);
    append_test_string(
        digest, plan.source_historical_version_pin_set_digest);
    append_test_string(digest, plan.source_visible_state_digest);
    append_test_string(digest, plan.source_payload_snapshot_digest);
    append_test_string(
        digest, plan.source_payload_transient_namespace_digest);
    append_test_u64(digest, plan.payload_transient_entry_count);
    append_test_u64(digest, plan.payload_transient_bytes);
    append_test_u64(digest, plan.payload_transient_reserved_bytes);
    append_test_string(
        digest, plan.live_capability_process_store_scope_digest);
    append_test_string(
        digest, plan.live_capability_process_store_scope_incarnation_digest);
    append_test_string(digest, plan.live_capability_set_digest);
    append_test_u64(digest, plan.live_snapshot_count);
    append_test_u64(digest, plan.live_opened_payload_count);
    append_test_u64(digest, plan.live_targeted_access_count);
    append_test_u64(digest, plan.live_mutation_batch_count);
    append_test_u64(
        digest, plan.distinct_live_opened_payload_root_count);
    append_test_u64(
        digest, plan.distinct_live_opened_payload_root_bytes);
    append_test_u64(
        digest, plan.live_capability_rooted_physical_payload_count);
    append_test_u64(
        digest, plan.live_capability_rooted_physical_payload_bytes);
    append_test_u64(
        digest, plan.unreferenced_live_capability_rooted_payload_count);
    append_test_u64(
        digest, plan.unreferenced_live_capability_rooted_payload_bytes);
    append_test_string(digest, candidate_set_digest);
    append_test_u64(
        digest,
        plan.unreferenced_by_retained_file_operations.payload_count);
    append_test_u64(
        digest,
        plan.unreferenced_by_retained_file_operations.payload_bytes);
    return digest.finish_hex();
}

[[nodiscard]] std::string legacy_catalog_digest_for_test(
    const anonsync::SyncReplicaFolderCatalogSnapshot& snapshot) {
    anonsync::Sha256DigestBuilder digest;
    append_test_string(
        digest, "anonsync:sync-replica-folder-catalog:v1");
    append_test_u64(digest, 1U);
    append_test_string(digest, snapshot.folder_id);
    append_test_string(digest, snapshot.absolute_root_path);
    append_test_string(digest, snapshot.root_attestation_digest);
    append_test_u64(digest, snapshot.limits.max_catalog_entries);
    append_test_u64(digest, snapshot.limits.max_catalog_path_bytes);
    append_test_u64(digest, snapshot.limits.max_payload_bytes);
    append_test_u64(digest, snapshot.state_generation);
    append_test_u64(
        digest, static_cast<std::uint64_t>(snapshot.entries.size()));
    for (const auto& entry : snapshot.entries) {
        if (entry.kind != anonsync::SyncReplicaValueKind::File) {
            fail("legacy catalog fixture received a tombstone");
        }
        append_test_string(digest, entry.canonical_path);
        append_test_u64(digest, entry.size_bytes);
        append_test_string(digest, entry.content_sha256);
        append_test_string(digest, entry.operation_id);
        append_test_string(digest, entry.source_snapshot_sha256);
        append_test_u64(digest, entry.last_seen_generation);
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string modern_catalog_digest_for_test(
    const anonsync::SyncReplicaFolderCatalogSnapshot& snapshot,
    std::string_view domain,
    std::uint64_t schema_version,
    std::string_view fixture_label) {
    anonsync::Sha256DigestBuilder digest;
    append_test_string(digest, domain);
    append_test_u64(digest, schema_version);
    append_test_string(digest, snapshot.folder_id);
    append_test_string(digest, snapshot.absolute_root_path);
    append_test_string(digest, snapshot.root_attestation_digest);
    append_test_u64(digest, snapshot.limits.max_catalog_entries);
    append_test_u64(digest, snapshot.limits.max_catalog_path_bytes);
    append_test_u64(digest, snapshot.limits.max_payload_bytes);
    append_test_u64(digest, snapshot.state_generation);
    append_test_u64(
        digest, static_cast<std::uint64_t>(snapshot.entries.size()));
    for (const auto& entry : snapshot.entries) {
        append_test_string(digest, entry.canonical_path);
        switch (entry.kind) {
            case anonsync::SyncReplicaValueKind::File:
                append_test_u64(digest, 1U);
                break;
            case anonsync::SyncReplicaValueKind::Tombstone:
                append_test_u64(digest, 2U);
                break;
            default:
                fail(std::string(fixture_label) +
                     " catalog fixture received an invalid value kind");
        }
        append_test_u64(digest, entry.size_bytes);
        append_test_string(digest, entry.content_sha256);
        append_test_string(digest, entry.operation_id);
        append_test_string(digest, entry.source_snapshot_sha256);
        append_test_u64(digest, entry.last_seen_generation);
    }
    return digest.finish_hex();
}

[[nodiscard]] std::string previous_catalog_digest_for_test(
    const anonsync::SyncReplicaFolderCatalogSnapshot& snapshot) {
    return modern_catalog_digest_for_test(
        snapshot, "anonsync:sync-replica-folder-catalog:v2", 2U, "v2");
}

[[nodiscard]] std::string fair_scan_catalog_digest_for_test(
    const anonsync::SyncReplicaFolderCatalogSnapshot& snapshot) {
    return modern_catalog_digest_for_test(
        snapshot, "anonsync:sync-replica-folder-catalog:v3", 3U, "v3");
}

[[nodiscard]] std::string cyclic_catalog_digest_for_test(
    const anonsync::SyncReplicaFolderCatalogSnapshot& snapshot) {
    return modern_catalog_digest_for_test(
        snapshot, "anonsync:sync-replica-folder-catalog:v4", 4U, "v4");
}

struct ThrowAtPublicationCutpointContext final {
    anonsync::atomic_file_publication_detail::AtomicFilePublicationCutpoint
        cutpoint = anonsync::atomic_file_publication_detail::
            AtomicFilePublicationCutpoint::NamespacePublished;
    bool observed = false;
};

void throw_at_publication_cutpoint(
    const anonsync::atomic_file_publication_detail::
        AtomicFilePublicationObservation& observation,
    void* raw_context) {
    auto& context =
        *static_cast<ThrowAtPublicationCutpointContext*>(raw_context);
    if (observation.cutpoint == context.cutpoint) {
        context.observed = true;
        throw std::runtime_error("simulated folder apply process loss");
    }
}

struct SubstituteFinalAtCutpointContext final {
    fs::path replacement;
    fs::path destination;
    bool observed = false;
};

void substitute_final_after_temp_sync(
    const anonsync::atomic_file_publication_detail::
        AtomicFilePublicationObservation& observation,
    void* raw_context) {
    using Cutpoint = anonsync::atomic_file_publication_detail::
        AtomicFilePublicationCutpoint;
    if (observation.cutpoint != Cutpoint::TempFileSynced) return;
    auto& context =
        *static_cast<SubstituteFinalAtCutpointContext*>(raw_context);
    fs::rename(context.replacement, context.destination);
    context.observed = true;
}

class TestOutboxClockSource final
    : public anonsync::SyncReplicaOutboxClockSource {
public:
    [[nodiscard]] anonsync::SyncReplicaOutboxClockObservation observe_or_throw(
        const std::string&) override {
        constexpr std::uint64_t epoch = 1000U;
        return {
            "folder-scan-test-clock-v1",
            "01234567-89ab-cdef-0123-456789abcdef",
            std::string(64U, 'c'),
            epoch * anonsync::kSyncReplicaNanosecondsPerSecond,
            epoch * anonsync::kSyncReplicaNanosecondsPerSecond,
            1U,
            anonsync::SyncReplicaOutboxClockSynchronization::Synchronized};
    }
};

[[nodiscard]] anonsync::SyncSqliteDb open_database(
    const fs::path& path,
    std::string_view label) {
    anonsync::SyncSqliteDb owner;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int result = sqlite3_open_v2(
        path.string().c_str(), owner.db.out(), flags, nullptr);
    if (result != SQLITE_OK) {
        fail(anonsync::sqlite_error_message(
            owner.db, std::string(label) + " open"));
    }
    anonsync::sqlite_set_busy_timeout_or_throw(
        owner.db, 5000, std::string(label) + " busy timeout");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "PRAGMA journal_mode=WAL;PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;",
        std::string(label) + " durability profile");
    return owner;
}

[[nodiscard]] anonsync::SyncReplicaModel restore_model(
    const anonsync::SyncReplicaSqliteSnapshot& snapshot) {
    return anonsync::SyncReplicaModel::restore_or_throw(
        snapshot.durable, snapshot.limits.model);
}

[[nodiscard]] std::optional<anonsync::SyncReplicaFolderCatalogEntry>
find_entry(
    const anonsync::SyncReplicaFolderCatalogSnapshot& snapshot,
    std::string_view path) {
    for (const auto& entry : snapshot.entries) {
        if (entry.canonical_path == path) return entry;
    }
    return std::nullopt;
}

struct Fixture final {
    explicit Fixture(
        std::string_view stem,
        std::uint64_t configured_max_payload_bytes = 1024U * 1024U)
        : maximum_payload_bytes(configured_max_payload_bytes),
          temporary(stem),
          shared_root(temporary.make_directory("shared")),
          payload_root(temporary.make_directory("payload")),
          replica_db(open_database(
              temporary.path() / "replica.sqlite3", "replica database")),
          replica(
              replica_db.db, folder_id, local_actor, {},
              "folder-scan replica owner",
              std::make_unique<TestOutboxClockSource>()),
          payload_store(
              folder_id, payload_root,
              anonsync::SyncReplicaFilePayloadStoreOpenDisposition::
                  CreateIfMissing,
              payload_limits(configured_max_payload_bytes),
              "folder-scan payload store") {}

    [[nodiscard]] static anonsync::SyncReplicaFilePayloadStoreLimits
    payload_limits(
        std::uint64_t maximum_payload_bytes = 1024U * 1024U) {
        anonsync::SyncReplicaFilePayloadStoreLimits limits;
        limits.max_entries = 128U;
        limits.max_payload_bytes = maximum_payload_bytes;
        limits.max_indexed_bytes = std::max<std::uint64_t>(
            16U * 1024U * 1024U, maximum_payload_bytes * 2U);
        limits.max_transient_entries = 128U;
        limits.max_transient_bytes = std::max<std::uint64_t>(
            2U * 1024U * 1024U, maximum_payload_bytes * 2U);
        return limits;
    }

    [[nodiscard]] static anonsync::SyncReplicaFolderScanLimits scan_limits(
        std::uint64_t maximum_payload_bytes = 1024U * 1024U) {
        anonsync::SyncReplicaFolderScanLimits limits;
        limits.max_catalog_entries = 128U;
        limits.max_catalog_path_bytes = 64U * 1024U;
        limits.max_payload_bytes = maximum_payload_bytes;
        return limits;
    }

    [[nodiscard]] static
    anonsync::SyncReplicaFolderConvergencePassLimits pass_limits(
        std::uint64_t maximum_payload_bytes = 1024U * 1024U) {
        anonsync::SyncReplicaFolderConvergencePassLimits limits;
        limits.maximum_entries = 128U;
        limits.maximum_regular_files = 128U;
        limits.maximum_file_bytes = maximum_payload_bytes;
        limits.maximum_total_file_bytes = std::max<std::uint64_t>(
            8U * 1024U * 1024U, maximum_payload_bytes);
        limits.maximum_relative_path_bytes = 4096U;
        limits.maximum_directory_depth = 16U;
        limits.maximum_remote_paths = 128U;
        limits.maximum_remote_inspection_paths = 128U;
        limits.maximum_local_scan_segment_regular_files = 128U;
        return limits;
    }

    [[nodiscard]] fs::path catalog_path() const {
        return temporary.path() / "catalog.sqlite3";
    }

    [[nodiscard]] std::unique_ptr<anonsync::SyncReplicaFolderScanOwner>
    make_scan_owner(anonsync::SyncSqliteDb& catalog_db) {
        return std::make_unique<anonsync::SyncReplicaFolderScanOwner>(
            catalog_db.db, folder_id, shared_root, replica, payload_store,
            scan_limits(maximum_payload_bytes), "folder-scan owner");
    }

    static inline const std::string folder_id = "folder-scan-owner";
    static inline const anonsync::SyncReplicaActor local_actor{
        "device-scan-local", 1U};

    std::uint64_t maximum_payload_bytes;
    TemporaryDirectory temporary;
    fs::path shared_root;
    fs::path payload_root;
    anonsync::SyncSqliteDb replica_db;
    anonsync::SyncReplicaSqliteOwner replica;
    anonsync::SyncReplicaFilePayloadStore payload_store;
};

void test_deployment_payload_ceiling_composes_usable_pass_defaults() {
    constexpr std::uint64_t kDefaultAggregateBytes =
        256ULL * 1024ULL * 1024ULL;
    const auto small =
        anonsync::sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
            1U, "small deployment pass defaults");
    require(
        small.maximum_file_bytes == 1U &&
            small.maximum_total_file_bytes == kDefaultAggregateBytes,
        "small deployment ceiling changed the ordinary aggregate pass budget");

    const auto maximum =
        anonsync::sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
            anonsync::kSyncReplicaFolderScanMaxPayloadBytes,
            "maximum deployment pass defaults");
    require(
        maximum.maximum_file_bytes ==
                anonsync::kSyncReplicaFolderScanMaxPayloadBytes &&
            maximum.maximum_total_file_bytes ==
                anonsync::kSyncReplicaFolderScanMaxPayloadBytes,
        "maximum deployment ceiling composed an unusable aggregate pass budget");

    require_error(
        [] {
            (void)anonsync::
                sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
                    0U, "zero deployment pass defaults");
        },
        "outside the folder ceiling",
        "zero deployment ceiling was accepted for pass defaults");
    require_error(
        [] {
            (void)anonsync::
                sync_replica_folder_convergence_pass_limits_for_payload_ceiling_or_throw(
                    anonsync::kSyncReplicaFolderScanMaxPayloadBytes + 1U,
                    "oversized deployment pass defaults");
        },
        "outside the folder ceiling",
        "oversized deployment ceiling was accepted for pass defaults");
}

void test_selective_sync_policy_is_bounded_durable_and_content_cold() {
    Fixture fixture("anonsync-folder-selective-sync-policy");
    write_file(fixture.shared_root / "a.txt", "alpha");
    write_file(fixture.shared_root / "b.txt", "beta");
    write_file(fixture.shared_root / "c.txt", "gamma");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "selective-sync policy catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto bounded = Fixture::pass_limits();
    bounded.maximum_local_scan_segment_regular_files = 1U;
    const auto first = scan->run_convergence_pass_or_throw(bounded);
    const auto before = scan->snapshot_or_throw();
    const auto before_progress = scan->scan_progress_snapshot_or_throw();
    require(
        !first.completed_local_scan_epoch &&
            before.entries.size() == 1U &&
            before_progress.seen_path_count == 1U &&
            !before_progress.resume_after_path.empty(),
        "selective-sync fixture did not retain a non-genesis scan frontier");

    CatalogEntryReadTrace trace;
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            count_catalog_entry_reads, &trace) == SQLITE_OK,
        "selective-sync fixture could not install its SQLite trace");
    const auto initial = scan->selective_sync_policy_snapshot_or_throw();
    const std::vector<anonsync::SyncReplicaSelectiveSyncRule> requested{
        {"media/keep/private",
         anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly},
        {"documents", anonsync::SyncReplicaSelectiveSyncMode::Materialize},
        {"media/keep", anonsync::SyncReplicaSelectiveSyncMode::Materialize},
    };
    const auto changed = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly, requested);
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "selective-sync fixture could not remove its SQLite trace");

    const auto after = scan->snapshot_or_throw();
    const auto after_progress = scan->scan_progress_snapshot_or_throw();
    require(
        initial == anonsync::sync_replica_default_selective_sync_policy() &&
            changed.generation == initial.generation + 1U &&
            changed.default_mode ==
                anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly &&
            changed.rules.size() == 3U &&
            changed.rules[0].canonical_path == "documents" &&
            changed.rules[1].canonical_path == "media/keep" &&
            changed.rules[2].canonical_path == "media/keep/private" &&
            changed.rule_path_bytes ==
                std::string_view("documents").size() +
                    std::string_view("media/keep").size() +
                    std::string_view("media/keep/private").size() &&
            anonsync::is_lowercase_sha256_hex(changed.policy_digest),
        "selective-sync replacement did not publish one canonical bounded policy");
    require(
        anonsync::sync_replica_selective_sync_path_is_materialized(
            changed, "documents/report.txt") &&
            anonsync::sync_replica_selective_sync_path_is_materialized(
                changed, "media/keep/movie.mkv") &&
            !anonsync::sync_replica_selective_sync_path_is_materialized(
                changed, "media/keep/private/secret.mkv") &&
            !anonsync::sync_replica_selective_sync_path_is_materialized(
                changed, "media/skip/movie.mkv"),
        "selective-sync longest-prefix evaluation changed its intended meaning");
    require(
        trace.entry_table_read_count == 0U &&
            after.entries == before.entries &&
            after.state_generation == before.state_generation &&
            after.content_catalog_digest == before.content_catalog_digest &&
            after.selective_sync_policy == changed &&
            after.selective_sync_absence_fence_generation == 0U &&
            after.catalog_digest != before.catalog_digest,
        "bounded selective-sync policy control read content authority or opened an unnecessary absence fence");
    require(
        after_progress.scan_epoch == before_progress.scan_epoch + 1U &&
            after_progress.resume_after_path.empty() &&
            after_progress.seen_path_count == 0U &&
            after_progress.seen_path_bytes == 0U &&
            after_progress.remote_apply_resume_after_path.empty() &&
            after_progress.remote_inspection_sweep_basis_digest.empty() &&
            after_progress.remote_inspection_sweep_seen_path_count == 0U,
        "changed selective-sync policy did not reset both scheduling frontiers");

    CatalogEntryReadTrace replay_trace;
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            count_catalog_entry_reads, &replay_trace) == SQLITE_OK,
        "selective-sync replay could not install its SQLite trace");
    const auto replayed = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly, requested);
    const auto replay_progress = scan->scan_progress_snapshot_or_throw();
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "selective-sync replay could not remove its SQLite trace");
    require(
        replayed == changed && replay_progress == after_progress &&
            replay_trace.entry_table_read_count == 0U,
        "idempotent selective-sync replay advanced policy or scheduling authority");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    require(
        scan->selective_sync_policy_snapshot_or_throw() == changed,
        "selective-sync policy did not survive an owner restart");
}

void test_selective_sync_pure_exclusion_does_not_delay_other_deletion() {
    Fixture fixture("anonsync-folder-selective-sync-exclusion");
    constexpr std::string_view selected_path = "docs/delete.txt";
    write_file(fixture.shared_root / selected_path, "delete me");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "selective-sync exclusion catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto published = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        published.local_published_count == 1U &&
            find_entry(scan->snapshot_or_throw(), selected_path).has_value(),
        "selective-sync exclusion fixture did not publish its selected file");

    const auto narrowed = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize,
        {{"media", anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    require(
        narrowed.generation == 2U &&
            scan->snapshot_or_throw()
                    .selective_sync_absence_fence_generation == 0U,
        "pure selective-sync exclusion opened a global absence fence");

    require(
        fs::remove(fixture.shared_root / selected_path),
        "selective-sync exclusion fixture could not remove its selected file");
    const auto deleted = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto deleted_entry = find_entry(
        scan->snapshot_or_throw(), selected_path);
    require(
        deleted.local_published_count == 1U &&
            deleted.local_selection_change_absence_suppressed_count == 0U &&
            deleted_entry.has_value() &&
            deleted_entry->kind == anonsync::SyncReplicaValueKind::Tombstone,
        "pure exclusion delayed an unrelated selected-path deletion");
}

void test_selective_sync_metadata_only_is_payload_cold_and_rehydrates() {
    Fixture fixture("anonsync-folder-selective-sync-rehydration");
    constexpr std::string_view path = "media/library/movie.mkv";
    const std::string bytes = "remote media payload";
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-selective-remote", 901U});
    const auto operation = remote.create_local_file_or_throw(
        std::string(path), bytes.size(), anonsync::sha256_hex(bytes));
    require(
        fixture.replica.accept_remote_or_throw(operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "selective-sync fixture rejected its remote file metadata");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "selective-sync rehydration catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto excluded = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize,
        {{"media", anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    {
        // The exclusive payload lease is a mechanical oracle: if either direct
        // owner reaches payload authority, the error becomes lease contention
        // instead of the selective-sync rejection required at the boundary.
        auto payload_exclusion =
            fixture.payload_store.begin_mutation_batch_or_throw();
        require_error(
            [&] {
                (void)scan->apply_visible_regular_file_or_throw(
                    operation.operation_id);
            },
            "metadata-only under the current selective-sync policy",
            "direct remote apply opened payload authority for an excluded path");
        constexpr std::string_view excluded_local_path =
            "media/library/local-only.txt";
        write_file(fixture.shared_root / excluded_local_path, "local only");
        require_error(
            [&] {
                (void)scan->scan_regular_file_or_throw(
                    std::string(excluded_local_path));
            },
            "metadata-only under the current selective-sync policy",
            "direct local scan opened payload authority for an excluded path");
        require(
            fs::remove(fixture.shared_root / excluded_local_path),
            "selective-sync fixture could not remove its local policy oracle");
        (void)payload_exclusion;
    }
    const auto metadata_only = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        excluded.generation == 2U && metadata_only.used_idle_fast_path &&
            metadata_only.remote_metadata_only_file_count == 1U &&
            metadata_only.remote_acknowledged_path_count == 1U &&
            metadata_only.remote_applied_count == 0U &&
            metadata_only.remote_apply_operation_count == 0U &&
            metadata_only.payload_snapshot_observation_count == 0U &&
            metadata_only.remote_payload_snapshot_observation_count == 0U &&
            metadata_only.remote_targeted_payload_access_count == 0U &&
            metadata_only.remote_targeted_payload_probe_count == 0U &&
            metadata_only.remote_targeted_payload_selection_count == 0U &&
            metadata_only.payload_mutation_batch_count == 0U &&
            metadata_only.payload_mutation_full_scan_count == 0U &&
            !fs::exists(fixture.shared_root / path) &&
            !find_entry(scan->snapshot_or_throw(), path).has_value(),
        "metadata-only convergence touched payload or rooted file authority");

    require(
        fixture.payload_store.put_payload_or_throw(bytes).content_sha256 ==
            operation.content_sha256,
        "selective-sync fixture could not stage the later requested payload");
    const auto included = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize, {});
    const auto rehydrated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto materialized_entry = find_entry(
        scan->snapshot_or_throw(), path);
    require(
        included.generation == excluded.generation + 1U &&
            rehydrated.remote_metadata_only_file_count == 0U &&
            rehydrated.remote_applied_count == 1U &&
            rehydrated.remote_apply_operation_count == 1U &&
            rehydrated.remote_targeted_payload_access_count == 1U &&
            rehydrated.remote_targeted_payload_probe_count == 1U &&
            rehydrated.remote_targeted_payload_selection_count == 1U &&
            read_file(fixture.shared_root / path) == bytes &&
            materialized_entry.has_value() &&
            materialized_entry->operation_id == operation.operation_id,
        "later materialization did not rehydrate the retained causal file");

    auto stale_prepared = scan->prepare_regular_file_or_throw(
        std::string(path));
    const auto excluded_again = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize,
        {{"media", anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    {
        auto payload_exclusion =
            fixture.payload_store.begin_mutation_batch_or_throw();
        require_error(
            [&] {
                (void)scan->commit_prepared_regular_file_or_throw(
                    std::move(stale_prepared));
            },
            "selective-sync authority changed",
            "prepared local publication survived a metadata-only policy transition");
        (void)payload_exclusion;
    }
    CatalogEntryReadTrace dematerialization_catalog_trace;
    ReplicaPathReadTrace dematerialization_replica_trace;
    require(
        sqlite3_trace_v2(
            catalog_db.db, SQLITE_TRACE_STMT, count_catalog_entry_reads,
            &dematerialization_catalog_trace) == SQLITE_OK,
        "could not install selective-sync catalog-read trace");
    require(
        sqlite3_trace_v2(
            fixture.replica_db.db, SQLITE_TRACE_STMT,
            count_replica_path_reads,
            &dematerialization_replica_trace) == SQLITE_OK,
        "could not install selective-sync replica-read trace");
    const auto suppressed = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        sqlite3_trace_v2(catalog_db.db, 0U, nullptr, nullptr) == SQLITE_OK,
        "could not remove selective-sync catalog-read trace");
    require(
        sqlite3_trace_v2(
            fixture.replica_db.db, 0U, nullptr, nullptr) == SQLITE_OK,
        "could not remove selective-sync replica-read trace");
    const auto retained_entry = find_entry(scan->snapshot_or_throw(), path);
    const auto retained_model = restore_model(
        fixture.replica.snapshot_or_throw());
    require(
        excluded_again.generation == included.generation + 1U &&
            suppressed.remote_metadata_only_file_count == 1U &&
            suppressed.remote_targeted_catalog_path_cutpoint_count == 3U &&
            suppressed.remote_targeted_replica_path_cutpoint_count == 3U &&
            dematerialization_catalog_trace.exact_path_read_count == 3U &&
            dematerialization_catalog_trace.complete_projection_read_count <=
                4U &&
            dematerialization_replica_trace.exact_visible_path_read_count ==
                3U &&
            dematerialization_replica_trace.exact_operation_read_count == 3U &&
            dematerialization_replica_trace
                    .complete_visible_projection_read_count <= 4U &&
            dematerialization_replica_trace
                    .complete_operation_projection_read_count <= 4U &&
            suppressed
                    .remote_metadata_only_dematerialization_attempt_count ==
                1U &&
            suppressed.remote_metadata_only_dematerialized_file_count == 1U &&
            suppressed.remote_metadata_only_dematerialized_bytes ==
                bytes.size() &&
            suppressed.remote_apply_operation_count == 1U &&
            suppressed.local_metadata_only_absence_suppressed_count == 1U &&
            suppressed.local_published_count == 0U &&
            suppressed.remote_applied_count == 0U &&
            !fs::exists(fixture.shared_root / path) &&
            retained_entry.has_value() &&
            retained_entry->operation_id == operation.operation_id &&
            retained_model.visible_path(std::string(path)).has_value(),
        "excluded local absence manufactured deletion or discarded causal metadata");

    std::error_code payload_remove_error;
    const bool payload_removed = fs::remove(
        fixture.payload_root / operation.content_sha256,
        payload_remove_error);
    require(
        payload_removed && !payload_remove_error,
        "selective-sync fixture could not make rehydration payload unavailable");

    const auto included_again =
        scan->replace_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize, {});
    const auto waiting_for_payload = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto waiting_catalog = scan->snapshot_or_throw();
    const auto waiting_model = restore_model(
        fixture.replica.snapshot_or_throw());
    require(
        waiting_for_payload.local_selection_change_absence_suppressed_count ==
                1U &&
            waiting_for_payload.deferred_remote_payload_candidate_count == 1U &&
            waiting_for_payload.remote_applied_count == 0U &&
            waiting_for_payload.remote_inspection_sweep_had_unresolved_paths &&
            waiting_catalog.selective_sync_absence_fence_generation ==
                included_again.generation &&
            find_entry(waiting_catalog, path).has_value() &&
            waiting_model.visible_path(std::string(path)).has_value() &&
            !fs::exists(fixture.shared_root / path),
        "unavailable reselected payload cleared its absence fence or manufactured deletion");

    require(
        fixture.payload_store.put_payload_or_throw(bytes).content_sha256 ==
            operation.content_sha256,
        "selective-sync fixture could not restore its deferred payload");
    const auto rehydrated_again = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto rehydrated_again_catalog = scan->snapshot_or_throw();
    require(
        rehydrated_again.local_selection_change_absence_suppressed_count ==
                1U &&
            rehydrated_again.remote_applied_count == 1U &&
            rehydrated_again_catalog.selective_sync_absence_fence_generation ==
                0U &&
            read_file(fixture.shared_root / path) == bytes,
        "re-including an absent retained file did not materialize it again");

    std::error_code retained_payload_remove_error;
    require(
        fs::remove(
            fixture.payload_root / operation.content_sha256,
            retained_payload_remove_error) &&
            !retained_payload_remove_error,
        "selective-sync fixture could not remove the private predecessor payload");
    const auto excluded_without_private_copy =
        scan->replace_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize,
            {{"media",
              anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    const auto preserved_only_copy = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        excluded_without_private_copy.generation ==
                included_again.generation + 1U &&
            preserved_only_copy
                    .remote_metadata_only_dematerialization_attempt_count ==
                1U &&
            preserved_only_copy
                    .remote_metadata_only_dematerialization_payload_unavailable_count ==
                1U &&
            preserved_only_copy
                    .remote_metadata_only_dematerialization_blocked_file_count ==
                1U &&
            preserved_only_copy.remote_metadata_only_dematerialized_file_count ==
                0U &&
            preserved_only_copy.remote_inspection_sweep_had_unresolved_paths &&
            read_file(fixture.shared_root / path) == bytes,
        "metadata-only transition removed the only proved payload copy");
}

void test_selective_sync_rehydrates_remote_successor_after_dematerialization() {
    Fixture fixture("anonsync-folder-selective-sync-successor-rehydration");
    constexpr std::string_view path = "media/library/series.mkv";
    const std::string first_bytes = "episode one payload";
    const std::string second_bytes = "episode two payload";
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-selective-successor", 902U});
    const auto first = remote.create_local_file_or_throw(
        std::string(path), first_bytes.size(),
        anonsync::sha256_hex(first_bytes));
    require(
        fixture.replica.accept_remote_or_throw(first) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.payload_store.put_payload_or_throw(first_bytes)
                    .content_sha256 == first.content_sha256,
        "selective-sync successor fixture could not stage its first value");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "selective-sync successor catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto first_materialized = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        first_materialized.remote_applied_count == 1U &&
            read_file(fixture.shared_root / path) == first_bytes,
        "selective-sync successor fixture did not materialize its first value");

    const auto excluded = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize,
        {{"media", anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    const auto dematerialized = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        excluded.generation == 2U &&
            dematerialized.remote_metadata_only_dematerialized_file_count ==
                1U &&
            !fs::exists(fixture.shared_root / path),
        "selective-sync successor fixture did not dematerialize its predecessor");

    const auto second = remote.create_local_file_or_throw(
        std::string(path), second_bytes.size(),
        anonsync::sha256_hex(second_bytes));
    require(
        anonsync::sync_replica_operation_supersedes(second, first) &&
            fixture.replica.accept_remote_or_throw(second) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.payload_store.put_payload_or_throw(second_bytes)
                    .content_sha256 == second.content_sha256,
        "selective-sync successor fixture could not stage its newer value");

    const auto included = scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize, {});
    const auto rehydrated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto catalog = scan->snapshot_or_throw();
    const auto current = find_entry(catalog, path);
    require(
        included.generation == excluded.generation + 1U &&
            rehydrated.local_selection_change_absence_suppressed_count == 1U &&
            rehydrated.remote_applied_count == 1U &&
            rehydrated.remote_apply_operation_count == 1U &&
            current.has_value() &&
            current->operation_id == second.operation_id &&
            read_file(fixture.shared_root / path) == second_bytes &&
            catalog.selective_sync_absence_fence_generation == 0U,
        "selection expansion did not materialize the current remote successor over an intentionally absent predecessor");
}

void test_selective_sync_dematerialization_preserves_changed_and_untracked_files() {
    {
        Fixture fixture("anonsync-folder-selective-sync-changed-preservation");
        constexpr std::string_view path = "media/library/changed.mkv";
        const std::string admitted_bytes = "admitted media bytes";
        const std::string changed_bytes = "locally changed media bytes";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-selective-changed", 903U});
        const auto operation = remote.create_local_file_or_throw(
            std::string(path), admitted_bytes.size(),
            anonsync::sha256_hex(admitted_bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(admitted_bytes)
                        .content_sha256 == operation.content_sha256,
            "selective-sync changed-file fixture could not stage its admitted value");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(),
            "selective-sync changed-file catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto materialized = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            materialized.remote_applied_count == 1U &&
                read_file(fixture.shared_root / path) == admitted_bytes,
            "selective-sync changed-file fixture did not materialize its admitted value");

        write_file(fixture.shared_root / path, changed_bytes);
        const auto excluded = scan->replace_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize,
            {{"media",
              anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
        const auto preserved = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        const auto catalog = scan->snapshot_or_throw();
        const auto retained = find_entry(catalog, path);
        const auto model = restore_model(fixture.replica.snapshot_or_throw());
        require(
            excluded.generation == 2U &&
                preserved.remote_metadata_only_dematerialization_attempt_count ==
                    1U &&
                preserved.remote_metadata_only_dematerialization_blocked_file_count ==
                    1U &&
                preserved.remote_metadata_only_dematerialized_file_count == 0U &&
                preserved.remote_inspection_sweep_had_unresolved_paths &&
                preserved.local_published_count == 0U &&
                read_file(fixture.shared_root / path) == changed_bytes &&
                retained.has_value() &&
                retained->operation_id == operation.operation_id &&
                model.visible_path(std::string(path)).has_value(),
            "metadata-only transition removed changed local bytes or discarded their retained causal predecessor");
    }

    {
        Fixture fixture("anonsync-folder-selective-sync-untracked-preservation");
        constexpr std::string_view path = "media/library/untracked.mkv";
        const std::string remote_bytes = "remote untracked-collision bytes";
        const std::string local_bytes = "operator-owned untracked bytes";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-selective-untracked", 904U});
        const auto operation = remote.create_local_file_or_throw(
            std::string(path), remote_bytes.size(),
            anonsync::sha256_hex(remote_bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(remote_bytes)
                        .content_sha256 == operation.content_sha256,
            "selective-sync untracked fixture could not stage its remote evidence");
        write_file(fixture.shared_root / path, local_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(),
            "selective-sync untracked catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto excluded = scan->replace_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize,
            {{"media",
              anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
        const auto preserved = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        const auto catalog = scan->snapshot_or_throw();
        require(
            excluded.generation == 2U &&
                preserved.remote_metadata_only_dematerialization_attempt_count ==
                    1U &&
                preserved.remote_metadata_only_dematerialization_blocked_file_count ==
                    1U &&
                preserved.remote_metadata_only_dematerialized_file_count == 0U &&
                preserved.remote_inspection_sweep_had_unresolved_paths &&
                preserved.local_published_count == 0U &&
                read_file(fixture.shared_root / path) == local_bytes &&
                !find_entry(catalog, path).has_value() &&
                restore_model(fixture.replica.snapshot_or_throw())
                    .visible_path(std::string(path))
                    .has_value(),
            "metadata-only transition removed an untracked collision or manufactured catalog authority for it");
    }
}


void test_selective_sync_dematerialization_reproof_is_path_local() {
    Fixture fixture("anonsync-folder-selective-sync-path-local-catalog");
    constexpr std::size_t kPathCount = 8U;
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-selective-path-local", 906U});
    std::vector<std::string> paths;
    paths.reserve(kPathCount);
    for (std::size_t index = 0U; index < kPathCount; ++index) {
        const std::string path =
            "media/library/item-" + std::to_string(index) + ".mkv";
        const std::string bytes =
            "path-local-catalog-payload-" + std::to_string(index);
        const auto operation = remote.create_local_file_or_throw(
            path, bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes)
                        .content_sha256 == operation.content_sha256,
            "path-local catalog fixture could not stage one remote file");
        paths.push_back(path);
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "selective-sync path-local catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto materialized = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        materialized.remote_applied_count == kPathCount &&
            std::all_of(
                paths.begin(), paths.end(),
                [&](const std::string& path) {
                    return fs::is_regular_file(fixture.shared_root / path);
                }),
        "path-local catalog fixture did not materialize every file");

    (void)scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize,
        {{"media", anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    CatalogEntryReadTrace trace;
    ReplicaPathReadTrace replica_trace;
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            count_catalog_entry_reads, &trace) == SQLITE_OK,
        "path-local catalog fixture could not install its SQLite trace");
    require(
        sqlite3_trace_v2(
            fixture.replica_db.db.get(), SQLITE_TRACE_STMT,
            count_replica_path_reads, &replica_trace) == SQLITE_OK,
        "path-local replica fixture could not install its SQLite trace");
    const auto dematerialized = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "path-local catalog fixture could not remove its SQLite trace");
    require(
        sqlite3_trace_v2(
            fixture.replica_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "path-local replica fixture could not remove its SQLite trace");

    const auto retained_catalog = scan->snapshot_or_throw();
    require(
        dematerialized.remote_apply_operation_count == kPathCount &&
            dematerialized
                    .remote_metadata_only_dematerialization_attempt_count ==
                kPathCount &&
            dematerialized.remote_metadata_only_dematerialized_file_count ==
                kPathCount &&
            dematerialized.remote_targeted_catalog_path_cutpoint_count ==
                3U * kPathCount &&
            dematerialized.remote_targeted_replica_path_cutpoint_count ==
                3U * kPathCount &&
            trace.exact_path_read_count == 3U * kPathCount &&
            trace.complete_projection_read_count <= 4U &&
            replica_trace.exact_visible_path_read_count ==
                3U * kPathCount &&
            replica_trace.exact_operation_read_count == 3U * kPathCount &&
            replica_trace.complete_visible_projection_read_count <= 4U &&
            replica_trace.complete_operation_projection_read_count <= 4U &&
            retained_catalog.entries.size() == kPathCount &&
            std::none_of(
                paths.begin(), paths.end(),
                [&](const std::string& path) {
                    return fs::exists(fixture.shared_root / path);
                }),
        "metadata-only batch multiplied complete catalog or replica projections instead of using one-path cutpoints");
}

void test_selective_sync_dematerialization_obeys_remote_effect_frontier() {
    Fixture fixture("anonsync-folder-selective-sync-dematerialization-frontier");
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-selective-frontier", 905U});
    const std::array<std::string, 2U> paths{
        "media/a.mkv", "media/b.mkv"};
    const std::array<std::string, 2U> bytes{
        "first media payload", "second media payload"};
    std::array<anonsync::SyncReplicaOperation, 2U> operations;
    for (std::size_t index = 0U; index < paths.size(); ++index) {
        operations[index] = remote.create_local_file_or_throw(
            std::string(paths[index]), bytes[index].size(),
            anonsync::sha256_hex(bytes[index]));
        require(
            fixture.replica.accept_remote_or_throw(operations[index]) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes[index])
                        .content_sha256 ==
                    operations[index].content_sha256,
            "selective-sync frontier fixture could not stage one remote file");
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "selective-sync dematerialization-frontier catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto materialized = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        materialized.remote_applied_count == 2U &&
            read_file(fixture.shared_root / paths[0]) == bytes[0] &&
            read_file(fixture.shared_root / paths[1]) == bytes[1],
        "selective-sync frontier fixture did not materialize both files");

    (void)scan->replace_selective_sync_policy_or_throw(
        anonsync::SyncReplicaSelectiveSyncMode::Materialize,
        {{"media", anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    auto limits = Fixture::pass_limits();
    limits.maximum_remote_apply_operations = 1U;
    const auto first = scan->run_convergence_pass_or_throw(limits);
    const std::uint64_t remaining_after_first =
        static_cast<std::uint64_t>(
            fs::exists(fixture.shared_root / paths[0])) +
        static_cast<std::uint64_t>(
            fs::exists(fixture.shared_root / paths[1]));
    const auto first_catalog = scan->snapshot_or_throw();
    require(
        first.remote_apply_operation_count == 1U &&
            first.remote_metadata_only_dematerialization_attempt_count == 1U &&
            first.remote_metadata_only_dematerialized_file_count == 1U &&
            first.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    OperationCountFrontier &&
            first.deferred_remote_apply_candidate_count == 1U &&
            remaining_after_first == 1U &&
            find_entry(first_catalog, paths[0]).has_value() &&
            find_entry(first_catalog, paths[1]).has_value(),
        "metadata-only dematerialization escaped its bounded remote-effect frontier");

    const auto second = scan->run_convergence_pass_or_throw(limits);
    const auto final_catalog = scan->snapshot_or_throw();
    require(
        second.remote_apply_operation_count == 1U &&
            second.remote_metadata_only_dematerialization_attempt_count == 1U &&
            second.remote_metadata_only_dematerialized_file_count == 1U &&
            second.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    EndOfProjection &&
            second.deferred_remote_apply_candidate_count == 0U &&
            !fs::exists(fixture.shared_root / paths[0]) &&
            !fs::exists(fixture.shared_root / paths[1]) &&
            find_entry(final_catalog, paths[0]).has_value() &&
            find_entry(final_catalog, paths[1]).has_value() &&
            restore_model(fixture.replica.snapshot_or_throw())
                    .visible_paths()
                    .size() == 2U,
        "bounded metadata-only dematerialization did not resume through the ordinary remote-work frontier");
}

void test_streaming_file_larger_than_legacy_frame_ceiling() {
    constexpr std::uint64_t kLargeFileBytes =
        64ULL * 1024ULL * 1024ULL + 4096ULL;
    Fixture fixture(
        "anonsync-folder-streaming-large-file", kLargeFileBytes);
    const std::string source_path = "large/source.bin";
    const StreamingFileObservation source = create_sparse_file_and_hash(
        fixture.shared_root / source_path, kLargeFileBytes);
    require(
        source.size_bytes == kLargeFileBytes,
        "large streaming fixture did not retain its exact extent");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "large streaming catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto published = scan->scan_regular_file_or_throw(source_path);
    require(
        published.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::Published &&
            published.published_operation.has_value() &&
            published.entry.size_bytes == kLargeFileBytes &&
            published.entry.content_sha256 == source.content_sha256,
        "file above the legacy frame ceiling was not streamed into durable history");
    const auto payload_snapshot = fixture.payload_store.snapshot_or_throw();
    require(
        payload_snapshot.payload_size_or_none(source.content_sha256) ==
            std::optional<std::uint64_t>(kLargeFileBytes),
        "large streamed publication did not retain its complete payload");

    const std::string remote_path = "large/copied.bin";
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-large-streaming-remote", 44U});
    const auto target = remote.create_local_file_or_throw(
        remote_path, kLargeFileBytes, source.content_sha256);
    require(
        fixture.replica.accept_remote_or_throw(target) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "large streamed apply fixture did not admit remote evidence");
    const auto applied =
        scan->apply_visible_regular_file_or_throw(target.operation_id);
    const StreamingFileObservation destination = hash_file_path(
        fixture.shared_root / remote_path, kLargeFileBytes);
    require(
        applied.disposition ==
                anonsync::SyncReplicaFolderApplyDisposition::Applied &&
            destination.size_bytes == kLargeFileBytes &&
            destination.content_sha256 == source.content_sha256,
        "large durable payload was not streamed into the destination tree");
    const auto repeated =
        scan->apply_visible_regular_file_or_throw(target.operation_id);
    require(
        repeated.disposition ==
            anonsync::SyncReplicaFolderApplyDisposition::CatalogNoOp,
        "repeated large streamed apply rewrote an exact destination");
}

void test_bounded_whole_folder_pass_local_tree_and_noop() {
    Fixture fixture("anonsync-folder-pass-local-tree");
    const std::string alpha = "alpha";
    const std::string middle = "middle bytes";
    const std::string omega = "omega";
    write_file(fixture.shared_root / "z-omega.txt", omega);
    write_file(fixture.shared_root / "a-alpha.txt", alpha);
    write_file(fixture.shared_root / "nested" / "middle.txt", middle);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "folder-pass local catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto first = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        first.traversal.regular_file_count == 3U &&
            first.traversal.visited_directory_count == 1U &&
            first.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    EndOfNamespace &&
            first.local_published_count == 3U &&
            first.local_adopted_visible_count == 0U &&
            first.remote_applied_count == 0U &&
            first.exact_local_file_bytes ==
                alpha.size() + middle.size() + omega.size(),
        "bounded folder pass did not publish one exact file at a time");
    const auto catalog_after_first = scan->snapshot_or_throw();
    const auto replica_after_first = fixture.replica.snapshot_or_throw();
    const auto payload_after_first = fixture.payload_store.snapshot_or_throw();
    require(
        catalog_after_first.entries.size() == 3U &&
            replica_after_first.durable.operations.size() == 3U &&
            replica_after_first.durable.last_local_counter == 3U &&
            replica_after_first.outbox.empty() &&
            payload_after_first.entry_count() == 3U,
        "folder pass did not retain exactly three share-global files and payloads");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto repeated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        repeated.traversal.regular_file_count == 3U &&
            repeated.used_idle_fast_path &&
            repeated.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    EndOfNamespace &&
            repeated.local_catalog_no_op_count == 3U &&
            repeated.local_published_count == 0U &&
            repeated.remote_applied_count == 0U &&
            scan->snapshot_or_throw() == catalog_after_first &&
            fixture.replica.snapshot_or_throw() == replica_after_first &&
            fixture.payload_store.snapshot_or_throw().snapshot_digest() ==
                payload_after_first.snapshot_digest(),
        "repeated whole-folder pass was not a durable no-op");

    const auto alpha_entry = find_entry(
        catalog_after_first, "a-alpha.txt");
    require(
        alpha_entry.has_value(),
        "whole-folder idle repair fixture lost its alpha catalog entry");
    std::error_code remove_error;
    const bool removed = fs::remove(
        fixture.payload_root / alpha_entry->content_sha256,
        remove_error);
    require(
        removed && !remove_error,
        "whole-folder idle repair fixture could not remove one payload");
    const auto repaired = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        !repaired.used_idle_fast_path &&
            repaired.local_catalog_no_op_count == 3U &&
            repaired.local_published_count == 0U &&
            repaired.payload_mutation_batch_count == 1U &&
            repaired.payload_mutation_full_scan_count == 1U &&
            repaired.payload_mutation_put_count == 1U &&
            repaired.payload_mutation_inserted_count == 1U &&
            repaired.payload_mutation_already_present_count == 0U &&
            fixture.payload_store.snapshot_or_throw().snapshot_digest() ==
                payload_after_first.snapshot_digest(),
        "idle fallback did not repair only the one missing payload while reusing retained payload proofs");

    write_file(fixture.shared_root / "a-alpha.txt", "ALPHA");
    const auto same_size_change = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        !same_size_change.used_idle_fast_path &&
            same_size_change.local_published_count == 1U &&
            same_size_change.local_catalog_no_op_count == 2U &&
            same_size_change.payload_mutation_batch_count == 1U &&
            same_size_change.payload_mutation_full_scan_count == 1U &&
            same_size_change.payload_mutation_put_count == 1U &&
            same_size_change.payload_mutation_inserted_count == 1U &&
            same_size_change.payload_mutation_already_present_count == 0U,
        "idle fallback did not isolate one same-size content change from retained payloads");

    // Put a new pathname before every cataloged path while reusing bytes that
    // already exist under another name. This forces the idle attempt to miss
    // before its lazy payload snapshot, then proves the fallback takes one exact
    // cutpoint and publishes the new path without opening mutation authority.
    write_file(fixture.shared_root / "0-copy-of-omega.txt", omega);
    const auto duplicate_path = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        !duplicate_path.used_idle_fast_path &&
            duplicate_path.local_published_count == 1U &&
            duplicate_path.local_catalog_no_op_count == 3U &&
            duplicate_path.payload_mutation_batch_count == 0U &&
            duplicate_path.payload_mutation_full_scan_count == 0U &&
            duplicate_path.payload_mutation_put_count == 0U &&
            fixture.payload_store.snapshot_or_throw().entry_count() == 4U,
        "early idle miss did not reuse an exact retained payload for a new duplicate path");
}

void test_complete_payload_reproof_handoff_requires_exact_store_owner() {
    Fixture fixture("anonsync-folder-pass-payload-reproof-handoff");
    const std::string bytes = "one complete payload reproof";
    write_file(fixture.shared_root / "retained.txt", bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "payload-reproof handoff catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto populated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        populated.local_published_count == 1U &&
            populated.payload_snapshot_handoff_count == 0U &&
            populated.payload_snapshot_observation_count == 1U &&
            fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
        "ordinary convergence did not report its own complete payload-root observation");

    auto exact_reproof = fixture.payload_store.snapshot_or_throw();
    {
        // Hold a live exclusive lease after the complete reproof. Any attempt by
        // convergence to take a second complete payload snapshot must fail busy;
        // success therefore proves the moved snapshot is the authority consumed
        // by the unchanged idle path rather than a merely advisory hint.
        auto exclusion = fixture.payload_store.begin_mutation_batch_or_throw();
        require_error(
            [&] { (void)fixture.payload_store.snapshot_or_throw(); },
            "lease is busy",
            "exclusive payload lease did not expose a duplicate complete snapshot");
        const auto reused =
            scan->run_convergence_pass_with_payload_snapshot_or_throw(
                std::move(exact_reproof), Fixture::pass_limits());
        require(
            reused.used_idle_fast_path &&
                reused.local_catalog_no_op_count == 1U &&
                reused.payload_snapshot_handoff_count == 1U &&
                reused.payload_snapshot_handoff_entry_count == 1U &&
                reused.payload_snapshot_observation_count == 0U &&
                reused.payload_snapshot_observed_entry_count == 0U &&
                reused.payload_mutation_batch_count == 0U &&
                reused.payload_mutation_full_scan_count == 0U,
            "exact-owner payload reproof was not consumed without a duplicate namespace observation");
        (void)exclusion;
    }

    anonsync::SyncReplicaFilePayloadStore foreign_handle(
        Fixture::folder_id, fixture.payload_root,
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
        Fixture::payload_limits(), "foreign payload-reproof store handle");
    auto foreign_reproof = foreign_handle.snapshot_or_throw();
    const auto catalog_before_rejection = scan->snapshot_or_throw();
    const auto replica_before_rejection = fixture.replica.snapshot_or_throw();
    require_error(
        [&] {
            (void)scan->run_convergence_pass_with_payload_snapshot_or_throw(
                std::move(foreign_reproof), Fixture::pass_limits());
        },
        "exact retained store owner",
        "a complete snapshot from a second handle to the same payload root was accepted");
    require(
        scan->snapshot_or_throw() == catalog_before_rejection &&
            fixture.replica.snapshot_or_throw() == replica_before_rejection,
        "foreign payload snapshot rejection changed catalog or replica authority");
}

void test_payload_handoff_cutpoint_invalidates_after_already_present_put() {
    Fixture fixture("anonsync-folder-pass-payload-handoff-cutpoint-freshness");
    const std::string bytes =
        "payload appended after the handed-off complete inventory";
    const std::string local_path = "a-local-source.txt";
    const std::string remote_path = "z-remote-ready.txt";

    // Freeze an exact empty inventory, then append the digest through the same
    // owner. The snapshot remains a valid historical cutpoint, but it cannot
    // prove presence of this later append-only entry.
    auto stale_handoff = fixture.payload_store.snapshot_or_throw();
    const auto retained = fixture.payload_store.put_payload_or_throw(bytes);
    require(
        stale_handoff.entry_count() == 0U &&
            retained.content_sha256 == anonsync::sha256_hex(bytes),
        "payload handoff freshness fixture did not create a later retained digest");

    // Local admission cannot find the digest in the handed-off cutpoint, so it
    // enters mutation authority. The mutation owner performs its own complete
    // scan and returns AlreadyPresent rather than Inserted. Remote work in the
    // same pass must therefore stop consulting the older inventory and use
    // exact targeted access for the independently visible remote path.
    write_file(fixture.shared_root / local_path, bytes);
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-payload-handoff-cutpoint", 357U});
    const auto remote_operation = remote.create_local_file_or_throw(
        remote_path, bytes.size(), retained.content_sha256);
    require(
        fixture.replica.accept_remote_or_throw(remote_operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "payload handoff freshness fixture did not retain remote evidence");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "payload-handoff cutpoint freshness catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto pass =
        scan->run_convergence_pass_with_payload_snapshot_or_throw(
            std::move(stale_handoff), Fixture::pass_limits());

    require(
        pass.payload_snapshot_handoff_count == 1U &&
            pass.payload_snapshot_handoff_entry_count == 0U &&
            pass.payload_snapshot_observation_count == 0U &&
            pass.payload_mutation_batch_count == 1U &&
            pass.payload_mutation_full_scan_count == 1U &&
            pass.payload_mutation_put_count == 1U &&
            pass.payload_mutation_inserted_count == 0U &&
            pass.payload_mutation_already_present_count == 1U,
        "later AlreadyPresent reconciliation did not expose the stale handoff cutpoint");
    require(
        pass.remote_applied_count == 1U &&
            pass.remote_apply_operation_count == 1U &&
            pass.remote_payload_snapshot_observation_count == 0U &&
            pass.remote_payload_snapshot_entry_count == 0U &&
            pass.remote_targeted_payload_access_count == 1U &&
            pass.remote_targeted_payload_probe_count == 1U &&
            pass.remote_targeted_payload_selection_count == 1U &&
            pass.remote_targeted_payload_selected_bytes == bytes.size() &&
            pass.deferred_remote_payload_candidate_count == 0U &&
            read_file(fixture.shared_root / local_path) == bytes &&
            read_file(fixture.shared_root / remote_path) == bytes,
        "remote planning trusted a historical payload inventory after a later mutation put");
}

void test_many_file_pass_amortizes_payload_store_mutation_authority() {
    constexpr std::size_t kFileCount = 32U;
    Fixture fixture("anonsync-folder-pass-payload-batch");
    std::vector<std::string> paths;
    paths.reserve(kFileCount);
    std::vector<std::pair<std::string, std::uint64_t>> path_sizes;
    path_sizes.reserve(kFileCount);
    std::uint64_t exact_bytes = 0U;
    for (std::size_t index = 0U; index < kFileCount; ++index) {
        const std::string path =
            "group-" + std::to_string(index % 4U) + "/file-" +
            std::to_string(index) + ".dat";
        const std::string bytes =
            "payload-batch-" + std::to_string(index) + "-" +
            std::string(96U + index, static_cast<char>('a' + index % 26U));
        write_file(fixture.shared_root / path, bytes);
        paths.push_back(path);
        path_sizes.emplace_back(path, bytes.size());
        exact_bytes += bytes.size();
    }
    std::sort(path_sizes.begin(), path_sizes.end());
    const std::uint64_t initial_expected_batch_work =
        exact_bytes * 2U - path_sizes.front().second;

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "folder-pass payload-batch catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto first = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto payload_after_first = fixture.payload_store.snapshot_or_throw();
    require(
        first.traversal.regular_file_count == kFileCount &&
            first.local_published_count == kFileCount &&
            first.local_catalog_no_op_count == 0U &&
            first.payload_mutation_batch_count == 1U &&
            first.payload_mutation_full_scan_count == 1U &&
            first.payload_mutation_put_count == kFileCount &&
            first.payload_mutation_source_bytes == exact_bytes &&
            first.payload_mutation_work_bytes ==
                initial_expected_batch_work &&
            first.payload_mutation_peak_batch_put_count == kFileCount &&
            first.payload_mutation_peak_batch_work_bytes ==
                initial_expected_batch_work &&
            first.payload_mutation_inserted_count == kFileCount &&
            first.payload_mutation_already_present_count == 0U &&
            first.exact_local_file_bytes == exact_bytes &&
            payload_after_first.entry_count() == kFileCount &&
            payload_after_first.scan_hashed_entry_count() == 0U &&
            payload_after_first.scan_hashed_bytes() == 0U &&
            payload_after_first.scan_reused_entry_count() == kFileCount &&
            payload_after_first.scan_reused_bytes() == exact_bytes,
        "one many-file pass did not publish every payload and its immediate warm index through retained mutation authority");

    const auto repeated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        repeated.used_idle_fast_path &&
            repeated.local_published_count == 0U &&
            repeated.local_catalog_no_op_count == kFileCount &&
            repeated.payload_mutation_batch_count == 0U &&
            repeated.payload_mutation_full_scan_count == 0U &&
            repeated.payload_mutation_put_count == 0U &&
            repeated.payload_mutation_source_bytes == 0U &&
            repeated.payload_mutation_work_bytes == 0U &&
            repeated.payload_mutation_peak_batch_put_count == 0U &&
            repeated.payload_mutation_peak_batch_work_bytes == 0U,
        "unchanged many-file pass did not remain an exact idle no-op");

    const std::string replacement =
        "payload-batch-replacement-" + std::string(257U, 'R');
    const std::string replaced_path = paths.at(kFileCount / 2U);
    const auto replaced_position = std::find_if(
        path_sizes.begin(), path_sizes.end(),
        [&](const auto& entry) { return entry.first == replaced_path; });
    require(
        replaced_position != path_sizes.end() &&
            std::next(replaced_position) != path_sizes.end(),
        "many-file segment fixture did not retain a following no-op path");
    const std::uint64_t changed_expected_batch_work = replacement.size();
    write_file(fixture.shared_root / replaced_path, replacement);
    const auto changed = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto payload_after_change = fixture.payload_store.snapshot_or_throw();
    require(
        !changed.used_idle_fast_path &&
            changed.local_published_count == 1U &&
            changed.local_catalog_no_op_count == kFileCount - 1U &&
            changed.payload_mutation_batch_count == 1U &&
            changed.payload_mutation_full_scan_count == 1U &&
            changed.payload_mutation_put_count == 1U &&
            changed.payload_mutation_source_bytes == replacement.size() &&
            changed.payload_mutation_work_bytes ==
                changed_expected_batch_work &&
            changed.payload_mutation_peak_batch_put_count == 1U &&
            changed.payload_mutation_peak_batch_work_bytes ==
                changed_expected_batch_work &&
            changed.payload_mutation_inserted_count == 1U &&
            changed.payload_mutation_already_present_count == 0U &&
            payload_after_change.entry_count() == kFileCount + 1U &&
            payload_after_change.scan_hashed_entry_count() == 0U &&
            payload_after_change.scan_hashed_bytes() == 0U &&
            payload_after_change.scan_reused_entry_count() == kFileCount + 1U &&
            payload_after_change.scan_reused_bytes() ==
                exact_bytes + replacement.size(),
        "changed many-file pass did not release exclusive payload authority before hashing the following likely no-op while preserving immediate warm reuse");
}

void test_scan_journal_batches_one_progress_publication_per_segment() {
    Fixture fixture("anonsync-folder-pass-journal-batch");
    for (const std::string_view path :
         {"a.txt", "b.txt", "c.txt", "d.txt", "e.txt"}) {
        write_file(fixture.shared_root / std::string(path), "four");
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "journal-batch catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    ScanJournalTrace trace;
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            count_scan_journal_statements, &trace) == SQLITE_OK,
        "journal-batch fixture could not install its SQLite trace");

    auto three_files = Fixture::pass_limits();
    three_files.maximum_file_bytes = 4U;
    three_files.maximum_total_file_bytes = 12U;
    const auto partial = scan->run_convergence_pass_or_throw(three_files);
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "journal-batch fixture could not remove its SQLite trace");
    require(
        !partial.completed_local_scan_epoch &&
            partial.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    AggregateFileByteFrontier &&
            partial.local_scan_seen_path_count == 3U &&
            partial.local_scan_resume_after_path == "c.txt" &&
            trace.insert_count == 3U &&
            trace.progress_update_count == 1U,
        "one bounded segment did not batch its scan-progress head into one publication transaction");
}

void test_terminal_cutpoint_fence_serializes_progress_publication() {
    Fixture fixture("anonsync-folder-terminal-cutpoint-fence");
    write_file(fixture.shared_root / "a.txt", "terminal-fence");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "terminal-fence catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);

    anonsync::SyncSqliteDb competing_replica_db = open_database(
        fixture.temporary.path() / "replica.sqlite3",
        "terminal-fence competing replica database");
    anonsync::SyncReplicaSqliteOwner competing_owner(
        competing_replica_db.db, Fixture::folder_id, Fixture::local_actor, {},
        "terminal-fence competing replica owner",
        std::make_unique<TestOutboxClockSource>());
    anonsync::sqlite_set_busy_timeout_or_throw(
        competing_replica_db.db, 0,
        "terminal-fence competing zero busy timeout");

    TerminalCutpointFenceTrace trace{&competing_owner};
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            probe_terminal_cutpoint_fence, &trace) == SQLITE_OK,
        "terminal-fence fixture could not install its SQLite trace");
    const auto pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "terminal-fence fixture could not remove its SQLite trace");

    const auto catalog = scan->snapshot_or_throw();
    const auto replica = fixture.replica.snapshot_or_throw();
    require(
        trace.progress_update_observed &&
            trace.competing_writer_blocked &&
            !trace.competing_writer_succeeded &&
            !trace.competing_writer_failed_unexpectedly,
        "remote progress publication was not covered by the replica writer guard");
    require(
        pass.completed_local_scan_epoch &&
            pass.completed_remote_inspection_sweep &&
            pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    EndOfProjection &&
            pass.remote_inspection_terminal_cutpoint_reproved &&
            pass.remote_inspection_terminal_catalog_digest ==
                catalog.catalog_digest &&
            pass.remote_inspection_terminal_visible_state_digest ==
                replica.visible_state_digest,
        "terminal-fence pass did not report its exact post-publication cutpoint");

    const auto resumed = competing_owner.create_local_tombstone_or_throw(
        "terminal-fence-probe.txt", std::span<const std::string>{});
    require(
        resumed.canonical_path == "terminal-fence-probe.txt" &&
            resumed.kind == anonsync::SyncReplicaValueKind::Tombstone,
        "competing replica writer did not resume after terminal fence release");
}

void test_terminal_cutpoint_movement_withholds_stale_settlement() {
    Fixture fixture("anonsync-folder-terminal-cutpoint-movement");
    write_file(fixture.shared_root / "a.txt", "terminal-movement");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "terminal-movement catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);

    anonsync::SyncSqliteDb competing_replica_db = open_database(
        fixture.temporary.path() / "replica.sqlite3",
        "terminal-movement competing replica database");
    anonsync::SyncReplicaSqliteOwner competing_owner(
        competing_replica_db.db, Fixture::folder_id, Fixture::local_actor, {},
        "terminal-movement competing replica owner",
        std::make_unique<TestOutboxClockSource>());

    ReplicaCutpointMovementTrace trace{&competing_owner};
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            advance_replica_after_projection_snapshot, &trace) == SQLITE_OK,
        "terminal-movement fixture could not install its SQLite trace");
    const auto pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "terminal-movement fixture could not remove its SQLite trace");

    const auto progress = scan->scan_progress_snapshot_or_throw();
    const auto replica = fixture.replica.snapshot_or_throw();
    const auto advanced = restore_model(replica).visible_path(
        "advanced-projection.txt");
    require(
        trace.remote_progress_select_count >= 2U &&
            trace.competing_writer_attempted &&
            trace.competing_writer_succeeded &&
            !trace.competing_writer_failed && advanced.has_value(),
        "terminal-movement fixture did not advance the replica after projection observation");
    require(
        pass.completed_local_scan_epoch &&
            !pass.completed_remote_inspection_sweep &&
            pass.remote_inspection_sweep_seen_path_count == 0U &&
            pass.deferred_remote_inspection_path_count == 1U &&
            !pass.remote_inspection_terminal_cutpoint_reproved &&
            pass.remote_inspection_terminal_catalog_digest.empty() &&
            pass.remote_inspection_terminal_visible_state_digest.empty() &&
            pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    AuthorityCutpointChanged &&
            progress.remote_apply_resume_after_path.empty() &&
            progress.remote_inspection_sweep_basis_digest.empty() &&
            progress.remote_inspection_sweep_seen_path_count == 0U,
        "changed replica projection published stale cursor or settlement authority");
}

void test_terminal_catalog_progress_movement_withholds_stale_publication() {
    Fixture fixture("anonsync-folder-terminal-progress-movement");
    write_file(fixture.shared_root / "a.txt", "terminal-progress");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "terminal-progress catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    anonsync::SyncSqliteDb competing_catalog_db = open_database(
        fixture.catalog_path(),
        "terminal-progress competing catalog database");

    CatalogProgressMovementTrace trace{competing_catalog_db.db.get()};
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            advance_catalog_progress_before_terminal_lock, &trace) ==
            SQLITE_OK,
        "terminal-progress fixture could not install its SQLite trace");
    const auto pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "terminal-progress fixture could not remove its SQLite trace");

    const auto progress = scan->scan_progress_snapshot_or_throw();
    require(
        trace.remote_progress_select_count >= 2U &&
            trace.terminal_begin_armed &&
            trace.competing_writer_attempted &&
            trace.competing_writer_succeeded &&
            !trace.competing_writer_failed,
        "terminal-progress fixture did not move scheduling authority before the terminal catalog lock");
    require(
        pass.completed_local_scan_epoch &&
            !pass.completed_remote_inspection_sweep &&
            pass.remote_inspection_sweep_seen_path_count == 0U &&
            pass.deferred_remote_inspection_path_count == 1U &&
            !pass.remote_inspection_terminal_cutpoint_reproved &&
            pass.remote_inspection_terminal_catalog_digest.empty() &&
            pass.remote_inspection_terminal_visible_state_digest.empty() &&
            pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    AuthorityCutpointChanged &&
            pass.remote_apply_resume_after_path.empty() &&
            progress.remote_apply_resume_after_path == "moved-progress.txt",
        "changed catalog progress was overwritten or granted stale settlement authority");
}

void test_zero_byte_scan_segment_has_bounded_journal_publication() {
    Fixture fixture("anonsync-folder-pass-zero-byte-segment");
    for (const std::string_view path :
         {"a.txt", "b.txt", "c.txt", "d.txt", "e.txt"}) {
        write_file(fixture.shared_root / std::string(path), {});
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "zero-byte segment catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto two_files = Fixture::pass_limits();
    two_files.maximum_file_bytes = 1U;
    two_files.maximum_total_file_bytes = 1U;
    two_files.maximum_local_scan_segment_regular_files = 2U;

    ScanJournalTrace trace;
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), SQLITE_TRACE_STMT,
            count_scan_journal_statements, &trace) == SQLITE_OK,
        "zero-byte segment fixture could not install its SQLite trace");
    const auto first = scan->run_convergence_pass_or_throw(two_files);
    const auto first_progress = scan->scan_progress_snapshot_or_throw();
    require(
        sqlite3_trace_v2(
            catalog_db.db.get(), 0U, nullptr, nullptr) == SQLITE_OK,
        "zero-byte segment fixture could not remove its SQLite trace");
    require(
        !first.completed_local_scan_epoch &&
            first.traversal.regular_file_count == 2U &&
            first.traversal.classified_regular_file_bytes == 0U &&
            first.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    RegularFileCountFrontier &&
            first.local_scan_seen_path_count == 2U &&
            first.local_scan_resume_after_path == "b.txt" &&
            first.local_published_count == 2U &&
            first_progress.scan_epoch == first.local_scan_epoch &&
            first_progress.seen_path_count == 2U &&
            first_progress.seen_path_bytes == 10U &&
            first_progress.resume_after_path == "b.txt" &&
            anonsync::is_lowercase_sha256_hex(
                first_progress.seen_chain_digest) &&
            trace.insert_count == 2U &&
            trace.progress_update_count == 1U,
        "zero-byte first segment exceeded its delivered-file or journal publication frontier");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto second = scan->run_convergence_pass_or_throw(two_files);
    require(
        !second.completed_local_scan_epoch &&
            second.traversal.regular_file_count == 2U &&
            second.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    RegularFileCountFrontier &&
            second.local_scan_seen_path_count == 4U &&
            second.local_scan_resume_after_path == "d.txt" &&
            second.local_published_count == 2U,
        "durable count-bounded scan did not resume at the exact zero-byte suffix");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto completed = scan->run_convergence_pass_or_throw(two_files);
    const auto completed_progress = scan->scan_progress_snapshot_or_throw();
    const auto catalog = scan->snapshot_or_throw();
    const auto replica = fixture.replica.snapshot_or_throw();
    const auto payloads = fixture.payload_store.snapshot_or_throw();
    require(
        completed.completed_local_scan_epoch &&
            completed.traversal.regular_file_count == 1U &&
            completed.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    EndOfNamespace &&
            completed.local_scan_seen_path_count == 0U &&
            completed.local_scan_resume_after_path.empty() &&
            completed.local_published_count == 1U &&
            completed_progress.scan_epoch ==
                first_progress.scan_epoch + 1U &&
            completed_progress.seen_path_count == 0U &&
            completed_progress.seen_path_bytes == 0U &&
            completed_progress.resume_after_path.empty() &&
            anonsync::is_lowercase_sha256_hex(
                completed_progress.seen_chain_digest) &&
            catalog.entries.size() == 5U &&
            replica.durable.operations.size() == 5U &&
            payloads.entry_count() == 1U,
        "count-bounded zero-byte epoch did not complete every path exactly once while deduplicating payload bytes");
}

void test_idle_proof_obeys_path_effect_frontier() {
    Fixture fixture("anonsync-folder-pass-idle-path-frontier");
    for (const std::string_view path :
         {"a.txt", "b.txt", "c.txt", "d.txt", "e.txt"}) {
        write_file(fixture.shared_root / std::string(path), {});
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "idle path-frontier catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto seeded = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto seeded_catalog = scan->snapshot_or_throw();
    const auto seeded_replica = fixture.replica.snapshot_or_throw();
    const std::string seeded_payload_digest =
        fixture.payload_store.snapshot_or_throw().snapshot_digest();
    require(
        !seeded.used_idle_fast_path &&
            seeded.completed_local_scan_epoch &&
            seeded.local_published_count == 5U &&
            seeded_catalog.entries.size() == 5U,
        "idle path-frontier fixture did not establish its complete catalog");

    auto two_files = Fixture::pass_limits();
    two_files.maximum_file_bytes = 1U;
    two_files.maximum_total_file_bytes = 1U;
    two_files.maximum_local_scan_segment_regular_files = 2U;

    const auto first = scan->run_convergence_pass_or_throw(two_files);
    require(
        !first.used_idle_fast_path &&
            !first.completed_local_scan_epoch &&
            first.traversal.regular_file_count == 2U &&
            first.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    RegularFileCountFrontier &&
            first.local_catalog_no_op_count == 2U &&
            first.local_published_count == 0U &&
            first.local_scan_seen_path_count == 2U &&
            first.local_scan_resume_after_path == "b.txt",
        "known-large idle folder bypassed the bounded durable scan frontier");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto second = scan->run_convergence_pass_or_throw(two_files);
    require(
        !second.used_idle_fast_path &&
            !second.completed_local_scan_epoch &&
            second.traversal.regular_file_count == 2U &&
            second.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    RegularFileCountFrontier &&
            second.local_catalog_no_op_count == 2U &&
            second.local_scan_seen_path_count == 4U &&
            second.local_scan_resume_after_path == "d.txt",
        "bounded idle replacement did not resume at the durable suffix");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto completed = scan->run_convergence_pass_or_throw(two_files);
    require(
        !completed.used_idle_fast_path &&
            completed.completed_local_scan_epoch &&
            completed.traversal.regular_file_count == 1U &&
            completed.local_scan_stop_reason ==
                anonsync::SyncReplicaFolderTraversalStopReason::
                    EndOfNamespace &&
            completed.local_catalog_no_op_count == 1U &&
            completed.local_scan_seen_path_count == 0U &&
            completed.local_scan_resume_after_path.empty() &&
            scan->snapshot_or_throw() == seeded_catalog &&
            fixture.replica.snapshot_or_throw() == seeded_replica &&
            fixture.payload_store.snapshot_or_throw().snapshot_digest() ==
                seeded_payload_digest,
        "bounded idle replacement did not complete a no-effect epoch without mutating durable content");

    Fixture tombstones("anonsync-folder-pass-idle-tombstone-frontier");
    for (const std::string_view path :
         {"one.txt", "two.txt", "three.txt", "four.txt", "five.txt"}) {
        write_file(tombstones.shared_root / std::string(path), "value");
    }
    anonsync::SyncSqliteDb tombstone_catalog_db = open_database(
        tombstones.catalog_path(), "idle tombstone-frontier catalog database");
    auto tombstone_scan = tombstones.make_scan_owner(tombstone_catalog_db);
    const auto tombstone_seed = tombstone_scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        tombstone_seed.local_published_count == 5U,
        "idle tombstone-frontier fixture did not establish file predecessors");
    for (const std::string_view path :
         {"one.txt", "two.txt", "three.txt", "four.txt", "five.txt"}) {
        require(
            fs::remove(tombstones.shared_root / std::string(path)),
            "idle tombstone-frontier fixture could not remove a predecessor");
    }
    const auto deleted = tombstone_scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto deleted_catalog = tombstone_scan->snapshot_or_throw();
    const auto deleted_replica = tombstones.replica.snapshot_or_throw();
    require(
        deleted.local_published_count == 5U &&
            deleted_catalog.entries.size() == 5U &&
            std::all_of(
                deleted_catalog.entries.begin(), deleted_catalog.entries.end(),
                [](const anonsync::SyncReplicaFolderCatalogEntry& entry) {
                    return entry.kind ==
                        anonsync::SyncReplicaValueKind::Tombstone;
                }),
        "idle tombstone-frontier fixture did not establish five stable absences");

    auto two_catalog_paths = Fixture::pass_limits();
    two_catalog_paths.maximum_local_scan_segment_regular_files = 2U;
    const auto repeated_tombstones =
        tombstone_scan->run_convergence_pass_or_throw(two_catalog_paths);
    require(
        !repeated_tombstones.used_idle_fast_path &&
            repeated_tombstones.completed_local_scan_epoch &&
            repeated_tombstones.traversal.regular_file_count == 0U &&
            repeated_tombstones.local_published_count == 0U &&
            tombstone_scan->snapshot_or_throw() == deleted_catalog &&
            tombstones.replica.snapshot_or_throw() == deleted_replica,
        "tombstone-heavy catalog performed a whole speculative idle proof before authoritative adjudication");
}

void test_payload_batch_segments_bound_exclusive_lease_horizon() {
    {
        constexpr std::size_t kFileCount = 7U;
        Fixture fixture("anonsync-folder-pass-payload-segment-count");
        std::uint64_t exact_bytes = 0U;
        for (std::size_t index = 0U; index < kFileCount; ++index) {
            const std::string bytes(
                2U, static_cast<char>('a' + index));
            write_file(
                fixture.shared_root /
                    ("file-" + std::to_string(index) + ".dat"),
                bytes);
            exact_bytes += bytes.size();
        }

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(),
            "folder-pass payload count-segment catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto limits = Fixture::pass_limits();
        limits.maximum_payload_batch_puts = 3U;
        limits.maximum_payload_batch_work_bytes = 1024U;
        const auto segmented = scan->run_convergence_pass_or_throw(limits);
        const auto payload_snapshot =
            fixture.payload_store.snapshot_or_throw();
        require(
            segmented.local_published_count == kFileCount &&
                segmented.payload_mutation_batch_count == 3U &&
                segmented.payload_mutation_full_scan_count == 3U &&
                segmented.payload_mutation_put_count == kFileCount &&
                segmented.payload_mutation_source_bytes == exact_bytes &&
                segmented.payload_mutation_work_bytes == 22U &&
                segmented.payload_mutation_peak_batch_put_count == 3U &&
                segmented.payload_mutation_peak_batch_work_bytes == 10U &&
                payload_snapshot.entry_count() == kFileCount &&
                payload_snapshot.scan_hashed_entry_count() == 0U &&
                payload_snapshot.scan_reused_entry_count() == kFileCount,
            "payload mutation count frontier did not split one traversal into warm bounded lease segments");
    }

    {
        Fixture fixture("anonsync-folder-pass-payload-segment-work");
        const std::string first(4U, 'a');
        const std::string second(5U, 'b');
        const std::string third(6U, 'c');
        const std::string oversized(12U, 'd');
        write_file(fixture.shared_root / "a.dat", first);
        write_file(fixture.shared_root / "b.dat", second);
        write_file(fixture.shared_root / "c.dat", third);
        write_file(fixture.shared_root / "d.dat", oversized);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(),
            "folder-pass payload work-segment catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto limits = Fixture::pass_limits();
        limits.maximum_payload_batch_puts = 32U;
        limits.maximum_payload_batch_work_bytes = 9U;
        const auto segmented = scan->run_convergence_pass_or_throw(limits);
        require(
            segmented.local_published_count == 4U &&
                segmented.payload_mutation_batch_count == 4U &&
                segmented.payload_mutation_full_scan_count == 4U &&
                segmented.payload_mutation_put_count == 4U &&
                segmented.payload_mutation_source_bytes ==
                    first.size() + second.size() + third.size() +
                        oversized.size() &&
                segmented.payload_mutation_work_bytes == 32U &&
                segmented.payload_mutation_peak_batch_put_count == 1U &&
                segmented.payload_mutation_peak_batch_work_bytes ==
                    oversized.size(),
            "payload mutation work frontier did not isolate exact segments and one larger single-file batch");
    }
}

void test_local_batch_releases_for_remote_apply_and_reacquires() {
    Fixture fixture("anonsync-folder-pass-payload-batch-reacquire");
    const std::string remote_path = "b-remote-successor.txt";
    const std::string base_bytes = "shared predecessor";
    const std::string remote_bytes = "remote successor materialized mid-walk";
    write_file(fixture.shared_root / remote_path, base_bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "folder-pass payload-batch reacquire catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto initial = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        initial.local_published_count == 1U,
        "payload-batch reacquire fixture did not publish its common base");
    const auto base_entry = find_entry(
        scan->snapshot_or_throw(), remote_path);
    require(
        base_entry.has_value(),
        "payload-batch reacquire fixture lost its common base mapping");
    const auto base_operation = restore_model(
        fixture.replica.snapshot_or_throw())
                                    .operation_by_id(base_entry->operation_id);
    require(
        base_operation.has_value(),
        "payload-batch reacquire fixture lost its common base operation");

    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-payload-batch-reacquire", 45U});
    require(
        remote.accept_remote_or_throw(*base_operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "payload-batch reacquire remote did not accept the common base");
    const std::vector<std::string> base_head{
        base_operation->operation_id};
    const auto successor =
        remote.create_local_file_from_observed_heads_or_throw(
            remote_path, base_head, remote_bytes.size(),
            anonsync::sha256_hex(remote_bytes));
    require(
        fixture.replica.accept_remote_or_throw(successor) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.payload_store.put_payload_or_throw(remote_bytes)
                    .content_sha256 == successor.content_sha256,
        "payload-batch reacquire fixture did not retain the remote successor");

    const std::string first_local = "local-before-remote";
    const std::string second_local = "local-after-remote";
    write_file(fixture.shared_root / "a-local.txt", first_local);
    write_file(fixture.shared_root / "c-local.txt", second_local);

    const auto interleaved = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        interleaved.local_published_count == 2U &&
            interleaved.remote_applied_count == 1U &&
            interleaved.payload_mutation_batch_count == 2U &&
            interleaved.payload_mutation_full_scan_count == 2U &&
            interleaved.payload_mutation_put_count == 2U &&
            interleaved.payload_mutation_source_bytes ==
                first_local.size() + second_local.size() &&
            interleaved.payload_mutation_work_bytes ==
                first_local.size() + second_local.size() &&
            interleaved.payload_mutation_peak_batch_put_count == 1U &&
            interleaved.payload_mutation_peak_batch_work_bytes ==
                std::max(first_local.size(), second_local.size()) &&
            interleaved.payload_mutation_inserted_count == 2U &&
            interleaved.payload_mutation_already_present_count == 0U &&
            read_file(fixture.shared_root / remote_path) == remote_bytes &&
            read_file(fixture.shared_root / "a-local.txt") == first_local &&
            read_file(fixture.shared_root / "c-local.txt") == second_local,
        "folder walk did not release local mutation authority for remote apply and reacquire it afterward");

    const auto repeated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        repeated.used_idle_fast_path &&
            repeated.local_catalog_no_op_count == 3U &&
            repeated.payload_mutation_batch_count == 0U &&
            repeated.remote_applied_count == 0U,
        "payload-batch release/reacquire result was not an exact repeated no-op");
}

void test_bounded_whole_folder_pass_remote_catchup_and_divergence() {
    {
        Fixture fixture("anonsync-folder-pass-remote-catchup");
        const std::string path = "base.txt";
        const std::string base_bytes = "shared base";
        const std::string successor_bytes = "remote successor bytes";
        const std::string new_path = "remote-new.txt";
        const std::string new_bytes = "remote initial bytes";
        write_file(fixture.shared_root / path, base_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass catchup catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto initial = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            initial.local_published_count == 1U,
            "folder-pass catchup fixture did not publish its common base");
        const auto base_entry = find_entry(scan->snapshot_or_throw(), path);
        require(base_entry.has_value(),
                "folder-pass catchup fixture lost its base mapping");
        const auto base_operation = restore_model(
            fixture.replica.snapshot_or_throw())
                                        .operation_by_id(base_entry->operation_id);
        require(base_operation.has_value(),
                "folder-pass catchup fixture lost its base operation");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-remote", 31U});
        require(
            remote.accept_remote_or_throw(*base_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "remote pass model did not accept the common base");
        const std::vector<std::string> base_head{
            base_operation->operation_id};
        const auto successor =
            remote.create_local_file_from_observed_heads_or_throw(
                path, base_head, successor_bytes.size(),
                anonsync::sha256_hex(successor_bytes));
        const auto initial_remote = remote.create_local_file_or_throw(
            new_path, new_bytes.size(), anonsync::sha256_hex(new_bytes));
        require(
            fixture.replica.accept_remote_or_throw(successor) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.replica.accept_remote_or_throw(initial_remote) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(successor_bytes)
                        .content_sha256 == successor.content_sha256 &&
                fixture.payload_store.put_payload_or_throw(new_bytes)
                        .content_sha256 == initial_remote.content_sha256,
            "folder-pass catchup fixture did not admit remote operations and bytes");
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

        const auto catchup = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            catchup.remote_applied_count == 2U &&
                catchup.remote_apply_operation_count == 2U &&
                catchup.remote_payload_snapshot_observation_count == 1U &&
                catchup.remote_payload_snapshot_entry_count == 3U &&
                catchup.remote_targeted_payload_access_count == 0U &&
                catchup.remote_targeted_payload_probe_count == 0U &&
                catchup.remote_targeted_payload_selection_count == 0U &&
                catchup.remote_targeted_payload_selected_bytes == 0U &&
                catchup.deferred_remote_payload_candidate_count == 0U &&
                catchup.exact_remote_file_bytes ==
                    successor_bytes.size() + new_bytes.size() &&
                catchup.local_published_count == 0U &&
                read_file(fixture.shared_root / path) == successor_bytes &&
                read_file(fixture.shared_root / new_path) == new_bytes,
            "one bounded pass did not apply a causal successor and absent remote file");
        require(
            fixture.replica.snapshot_or_throw() == replica_cutpoint &&
                scan->snapshot_or_throw().entries.size() == 2U,
            "remote folder catchup echoed evidence or failed to catalog both paths");

        const auto repeated = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            repeated.used_idle_fast_path &&
                repeated.local_catalog_no_op_count == 2U &&
                repeated.remote_applied_count == 0U &&
                repeated.exact_remote_file_bytes == 0U &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "post-catchup whole-folder pass was not an exact no-op");
    }

    {
        Fixture fixture("anonsync-folder-pass-divergence");
        const std::string path = "diverged.txt";
        const std::string base_bytes = "common base";
        const std::string remote_bytes = "remote successor";
        const std::string local_bytes = "independent local edit";
        write_file(fixture.shared_root / path, base_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass divergence catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
        const auto base_entry = find_entry(scan->snapshot_or_throw(), path);
        require(base_entry.has_value(),
                "folder-pass divergence fixture lost its base mapping");
        const auto base_operation = restore_model(
            fixture.replica.snapshot_or_throw())
                                        .operation_by_id(base_entry->operation_id);
        require(base_operation.has_value(),
                "folder-pass divergence fixture lost its base evidence");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-diverge", 32U});
        require(
            remote.accept_remote_or_throw(*base_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "divergence remote did not accept the common base");
        const std::vector<std::string> base_head{
            base_operation->operation_id};
        const auto successor =
            remote.create_local_file_from_observed_heads_or_throw(
                path, base_head, remote_bytes.size(),
                anonsync::sha256_hex(remote_bytes));
        require(
            fixture.replica.accept_remote_or_throw(successor) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(remote_bytes)
                        .content_sha256 == successor.content_sha256,
            "divergence fixture did not admit the remote successor");
        write_file(fixture.shared_root / path, local_bytes);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

        const auto conflicted = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            conflicted.skipped_conflicted_remote_path_count == 1U &&
                conflicted.local_published_count == 0U &&
                conflicted.remote_applied_count == 0U,
            "whole-folder pass did not retain local/remote divergence as an explicit conflict");
        require(
            read_file(fixture.shared_root / path) == local_bytes &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "divergence preservation changed local bytes or durable authority");
    }
}

void test_bounded_whole_folder_pass_preserves_absent_conflict() {
    Fixture fixture("anonsync-folder-pass-absent-conflict");
    const std::string path = "conflicted.txt";
    const std::string left_bytes = "left concurrent value";
    const std::string right_bytes = "right concurrent value";
    anonsync::SyncReplicaModel left(
        Fixture::folder_id, {"device-folder-pass-left", 33U});
    anonsync::SyncReplicaModel right(
        Fixture::folder_id, {"device-folder-pass-right", 34U});
    const auto left_operation = left.create_local_file_or_throw(
        path, left_bytes.size(), anonsync::sha256_hex(left_bytes));
    const auto right_operation = right.create_local_file_or_throw(
        path, right_bytes.size(), anonsync::sha256_hex(right_bytes));
    require(
        fixture.replica.accept_remote_or_throw(left_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.replica.accept_remote_or_throw(right_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.payload_store.put_payload_or_throw(left_bytes)
                    .content_sha256 == left_operation.content_sha256 &&
            fixture.payload_store.put_payload_or_throw(right_bytes)
                    .content_sha256 == right_operation.content_sha256,
        "absent-conflict fixture did not retain both concurrent values");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "folder-pass conflict catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto report = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        report.traversal.regular_file_count == 0U &&
            report.skipped_conflicted_remote_path_count == 1U &&
            !fs::exists(fixture.shared_root / path) &&
            scan->snapshot_or_throw().entries.empty(),
        "whole-folder pass projected a deterministic winner for an absent conflict");
}



void test_local_exact_content_rename_identity_and_ambiguity_fence() {
    {
        Fixture fixture("anonsync-folder-local-rename-identity");
        const std::string source_path = "media/old-name.bin";
        const std::string destination_path = "archive/new-name.bin";
        const std::string bytes = "one exact rename payload";
        write_file(fixture.shared_root / source_path, bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "local-rename catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto seeded = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        const auto source_entry = find_entry(
            scan->snapshot_or_throw(), source_path);
        const auto before_replica = fixture.replica.snapshot_or_throw();
        const auto before_payload = fixture.payload_store.snapshot_or_throw();
        require(
            seeded.local_published_count == 1U &&
                seeded.local_identity_preserving_rename_count == 0U &&
                source_entry.has_value() &&
                source_entry->kind == anonsync::SyncReplicaValueKind::File &&
                before_payload.entry_count() == 1U,
            "local rename fixture did not publish one exact source base");

        fs::create_directories(
            (fixture.shared_root / destination_path).parent_path());
        fs::rename(
            fixture.shared_root / source_path,
            fixture.shared_root / destination_path);
        const auto renamed = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        const auto catalog = scan->snapshot_or_throw();
        const auto source_tombstone = find_entry(catalog, source_path);
        const auto destination_file = find_entry(catalog, destination_path);
        const auto after_replica = fixture.replica.snapshot_or_throw();
        const auto model = restore_model(after_replica);
        require(
            renamed.local_published_count == 1U &&
                renamed.local_identity_preserving_rename_count == 1U &&
                source_tombstone.has_value() &&
                destination_file.has_value() &&
                source_tombstone->kind ==
                    anonsync::SyncReplicaValueKind::Tombstone &&
                destination_file->kind ==
                    anonsync::SyncReplicaValueKind::File &&
                source_tombstone->last_seen_generation ==
                    destination_file->last_seen_generation &&
                destination_file->content_sha256 ==
                    anonsync::sha256_hex(bytes) &&
                after_replica.state_generation ==
                    before_replica.state_generation + 1U &&
                after_replica.durable.operations.size() ==
                    before_replica.durable.operations.size() + 2U &&
                fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
            "exact local rename did not commit one catalog generation, one replica generation, and no duplicate payload");
        const auto identity =
            model.identity_preserving_rename_for_source_tombstone(
                source_tombstone->operation_id);
        require(
            identity.has_value() &&
                identity->source_canonical_path == source_path &&
                identity->destination_canonical_path == destination_path &&
                identity->source_file_operation_id ==
                    source_entry->operation_id &&
                identity->destination_file_operation_id ==
                    destination_file->operation_id &&
                identity->source_tombstone_operation_id ==
                    source_tombstone->operation_id &&
                identity->size_bytes == bytes.size() &&
                identity->content_sha256 == anonsync::sha256_hex(bytes),
            "durable causal evidence did not re-prove the exact rename identity");

        const auto stable_replica = fixture.replica.snapshot_or_throw();
        const auto stable_catalog = scan->snapshot_or_throw();
        scan.reset();
        scan = fixture.make_scan_owner(catalog_db);
        const auto repeated = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            repeated.local_published_count == 0U &&
                repeated.local_identity_preserving_rename_count == 0U &&
                fixture.replica.snapshot_or_throw() == stable_replica &&
                scan->snapshot_or_throw() == stable_catalog,
            "restart replayed an already committed identity-preserving rename");
    }

    {
        Fixture fixture("anonsync-folder-local-rename-ambiguity");
        const std::string bytes = "duplicate rename payload";
        const std::string source_a = "duplicates/a.bin";
        const std::string source_b = "duplicates/b.bin";
        const std::string destination = "duplicates/moved.bin";
        write_file(fixture.shared_root / source_a, bytes);
        write_file(fixture.shared_root / source_b, bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "ambiguous-rename catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto seeded = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            seeded.local_published_count == 2U,
            "ambiguous rename fixture did not publish both equal-content sources");
        const auto before = fixture.replica.snapshot_or_throw();

        fs::rename(
            fixture.shared_root / source_a,
            fixture.shared_root / destination);
        require(
            fs::remove(fixture.shared_root / source_b),
            "ambiguous rename fixture could not remove its second source");
        const auto changed = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        const auto catalog = scan->snapshot_or_throw();
        const auto source_a_tombstone = find_entry(catalog, source_a);
        const auto source_b_tombstone = find_entry(catalog, source_b);
        const auto destination_file = find_entry(catalog, destination);
        const auto after = fixture.replica.snapshot_or_throw();
        const auto model = restore_model(after);
        require(
            changed.local_identity_preserving_rename_count == 0U &&
                changed.local_published_count == 3U &&
                source_a_tombstone.has_value() &&
                source_b_tombstone.has_value() &&
                destination_file.has_value() &&
                source_a_tombstone->kind ==
                    anonsync::SyncReplicaValueKind::Tombstone &&
                source_b_tombstone->kind ==
                    anonsync::SyncReplicaValueKind::Tombstone &&
                destination_file->kind ==
                    anonsync::SyncReplicaValueKind::File &&
                after.durable.operations.size() ==
                    before.durable.operations.size() + 3U,
            "duplicate-content ambiguity did not fall back to ordinary create/delete publication");
        require(
            !model.identity_preserving_rename_for_source_tombstone(
                 source_a_tombstone->operation_id)
                 .has_value() &&
                !model.identity_preserving_rename_for_source_tombstone(
                     source_b_tombstone->operation_id)
                     .has_value(),
            "ambiguous equal-content history invented a source identity after fallback");
    }
}

void test_complete_scan_deletion_restart_and_resurrection() {
    Fixture fixture("anonsync-folder-pass-local-delete");
    const std::string path = "nested/deleted.txt";
    const std::string original = "delete this exact file";
    const std::string resurrected = "created again after tombstone";
    write_file(fixture.shared_root / path, original);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "local-delete catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto initial = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(initial.local_published_count == 1U,
            "local-delete fixture did not publish its file base");
    const auto base = find_entry(scan->snapshot_or_throw(), path);
    require(base.has_value() &&
                base->kind == anonsync::SyncReplicaValueKind::File,
            "local-delete fixture did not retain a file catalog base");

    require(fs::remove_all(fixture.shared_root / "nested") == 2U,
            "local-delete fixture could not remove the file and its parent");
    const auto before_delete_replica = fixture.replica.snapshot_or_throw();
    const auto deleted = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto tombstone_entry = find_entry(scan->snapshot_or_throw(), path);
    const auto deleted_model = restore_model(fixture.replica.snapshot_or_throw());
    const auto deleted_view = deleted_model.visible_path(path);
    require(
        deleted.local_published_count == 1U &&
            deleted.remote_applied_count == 0U &&
            !fs::exists(fixture.shared_root / path) &&
            tombstone_entry.has_value() &&
            tombstone_entry->kind ==
                anonsync::SyncReplicaValueKind::Tombstone &&
            deleted_view.has_value() &&
            deleted_view->primary_kind ==
                anonsync::SyncReplicaValueKind::Tombstone &&
            deleted_view->visible_operation_ids.size() == 1U &&
            deleted_view->visible_operation_ids.front() ==
                tombstone_entry->operation_id,
        "a complete scan did not publish and catalog one exact local deletion");
    require(
        fixture.replica.snapshot_or_throw().durable.operations.size() ==
            before_delete_replica.durable.operations.size() + 1U,
        "local deletion did not add exactly one durable tombstone operation");

    const auto deletion_cutpoint = fixture.replica.snapshot_or_throw();
    const auto deletion_catalog = scan->snapshot_or_throw();
    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto repeated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        repeated.used_idle_fast_path &&
            repeated.local_published_count == 0U &&
            !fs::exists(fixture.shared_root / path) &&
            fixture.replica.snapshot_or_throw() == deletion_cutpoint &&
            scan->snapshot_or_throw() == deletion_catalog,
        "restart did not retain deletion as a stable, non-echoing absence");

    write_file(fixture.shared_root / path, resurrected);
    const auto recreated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto recreated_entry = find_entry(scan->snapshot_or_throw(), path);
    const auto recreated_view =
        restore_model(fixture.replica.snapshot_or_throw()).visible_path(path);
    require(
        recreated.local_published_count == 1U &&
            recreated_entry.has_value() &&
            recreated_entry->kind == anonsync::SyncReplicaValueKind::File &&
            recreated_entry->content_sha256 ==
                anonsync::sha256_hex(resurrected) &&
            recreated_view.has_value() &&
            recreated_view->primary_kind ==
                anonsync::SyncReplicaValueKind::File &&
            read_file(fixture.shared_root / path) == resurrected,
        "same-path recreation did not become a causal file successor");
}

void test_remote_tombstone_removal_and_delete_edit_conflicts() {
    {
        Fixture fixture("anonsync-folder-pass-remote-delete");
        const std::string path = "remote-delete.txt";
        const std::string bytes = "remote deletion predecessor";
        write_file(fixture.shared_root / path, bytes);
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "remote-delete catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
        const auto base_entry = find_entry(scan->snapshot_or_throw(), path);
        require(base_entry.has_value(),
                "remote-delete fixture lost its catalog base");
        const auto base_operation = restore_model(
            fixture.replica.snapshot_or_throw())
                                        .operation_by_id(base_entry->operation_id);
        require(base_operation.has_value(),
                "remote-delete fixture lost its replica base");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-delete", 35U});
        require(
            remote.accept_remote_or_throw(*base_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "remote-delete model did not accept the common base");
        const auto tombstone = remote.create_local_tombstone_or_throw(path);
        require(
            fixture.replica.accept_remote_or_throw(tombstone) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "remote-delete fixture did not admit the tombstone");
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

        const auto applied = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        const auto catalog_tombstone =
            find_entry(scan->snapshot_or_throw(), path);
        require(
            applied.remote_applied_count == 1U &&
                applied.local_published_count == 0U &&
                !fs::exists(fixture.shared_root / path) &&
                catalog_tombstone.has_value() &&
                catalog_tombstone->kind ==
                    anonsync::SyncReplicaValueKind::Tombstone &&
                catalog_tombstone->operation_id == tombstone.operation_id &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "remote tombstone did not remove only the exact cataloged predecessor");

        scan.reset();
        scan = fixture.make_scan_owner(catalog_db);
        const auto repeated = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            repeated.used_idle_fast_path &&
                !fs::exists(fixture.shared_root / path) &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "remote deletion was not stable across a fresh folder-owner lifetime");
    }

    {
        Fixture fixture("anonsync-folder-pass-delete-local-edit");
        const std::string path = "edited-before-delete.txt";
        const std::string base_bytes = "shared predecessor";
        const std::string local_bytes = "independent local edit survives";
        write_file(fixture.shared_root / path, base_bytes);
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "delete-local-edit catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
        const auto base_entry = find_entry(scan->snapshot_or_throw(), path);
        const auto base_operation = restore_model(
            fixture.replica.snapshot_or_throw())
                                        .operation_by_id(base_entry->operation_id);
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-delete-local-edit", 36U});
        (void)remote.accept_remote_or_throw(*base_operation);
        const auto tombstone = remote.create_local_tombstone_or_throw(path);
        (void)fixture.replica.accept_remote_or_throw(tombstone);
        write_file(fixture.shared_root / path, local_bytes);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

        const auto conflicted = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            conflicted.skipped_conflicted_remote_path_count == 1U &&
                conflicted.remote_applied_count == 0U &&
                conflicted.local_published_count == 0U &&
                read_file(fixture.shared_root / path) == local_bytes &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "remote deletion destroyed or rewrote an independently edited local file");
    }

    {
        Fixture fixture("anonsync-folder-pass-delete-remote-edit");
        const std::string path = "absent-with-remote-edit.txt";
        const std::string base_bytes = "common predecessor";
        const std::string remote_bytes = "new remote file value";
        write_file(fixture.shared_root / path, base_bytes);
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "delete-remote-edit catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
        const auto base_entry = find_entry(scan->snapshot_or_throw(), path);
        const auto base_operation = restore_model(
            fixture.replica.snapshot_or_throw())
                                        .operation_by_id(base_entry->operation_id);
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-delete-remote-edit", 37U});
        (void)remote.accept_remote_or_throw(*base_operation);
        const auto successor = remote.create_local_file_or_throw(
            path, remote_bytes.size(), anonsync::sha256_hex(remote_bytes));
        (void)fixture.replica.accept_remote_or_throw(successor);
        (void)fixture.payload_store.put_payload_or_throw(remote_bytes);
        require(fs::remove(fixture.shared_root / path),
                "delete-remote-edit fixture could not remove its local file");
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

        const auto conflicted = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            conflicted.skipped_conflicted_remote_path_count == 1U &&
                conflicted.local_published_count == 0U &&
                conflicted.remote_applied_count == 0U &&
                !fs::exists(fixture.shared_root / path) &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "local deletion falsely superseded or rematerialized a newer remote edit");
    }
}

void test_deletion_crash_residue_is_not_published() {
    Fixture fixture("anonsync-folder-pass-delete-residue");
    const std::string path = "residue.txt";
    const std::string bytes = "bytes retained by a simulated crash";
    write_file(fixture.shared_root / path, bytes);
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "delete-residue catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto base_entry = find_entry(scan->snapshot_or_throw(), path);
    const auto base_operation = restore_model(
        fixture.replica.snapshot_or_throw())
                                    .operation_by_id(base_entry->operation_id);
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-delete-residue", 38U});
    (void)remote.accept_remote_or_throw(*base_operation);
    const auto tombstone = remote.create_local_tombstone_or_throw(path);
    (void)fixture.replica.accept_remote_or_throw(tombstone);
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

    const std::string residue_name =
        ".anonsync-publish-v1-0000000000000001-0000000000000002-"
        "0000000000000003.tmp";
    fs::rename(fixture.shared_root / path,
               fixture.shared_root / residue_name);
    const auto recovered = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto entry = find_entry(scan->snapshot_or_throw(), path);
    require(
        recovered.traversal.regular_file_count == 0U &&
            recovered.traversal.ignored_internal_artifact_count == 1U &&
            recovered.local_adopted_visible_count == 1U &&
            recovered.local_published_count == 0U &&
            entry.has_value() &&
            entry->kind == anonsync::SyncReplicaValueKind::Tombstone &&
            fs::exists(fixture.shared_root / residue_name) &&
            !fs::exists(fixture.shared_root / path) &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "private deletion crash residue re-entered share history or blocked tombstone recovery");

    const auto repeated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        repeated.used_idle_fast_path &&
            repeated.traversal.ignored_internal_artifact_count == 1U &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "private deletion residue prevented a stable restart no-op");
}

void test_reserved_internal_namespace_cannot_be_materialized() {
    Fixture fixture("anonsync-folder-pass-reserved-namespace");
    const std::string reserved_component =
        ".anonsync-publish-v1-0000000000000001-0000000000000002-"
        "0000000000000003.tmp";
    const std::string path =
        "ordinary/" + reserved_component + "/remote.txt";
    const std::string bytes = "remote bytes must never enter private state";

    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-reserved-namespace", 39U});
    const auto operation = remote.create_local_file_or_throw(
        path, bytes.size(), anonsync::sha256_hex(bytes));
    require(
        fixture.replica.accept_remote_or_throw(operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "reserved-namespace fixture did not retain the remote evidence");
    (void)fixture.payload_store.put_payload_or_throw(bytes);
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "reserved-namespace catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    require_error(
        [&] {
            (void)scan->run_convergence_pass_or_throw(
                Fixture::pass_limits());
        },
        "reserved atomic-publication namespace",
        "remote evidence materialized through AnonSync's private namespace");
    require(
        !fs::exists(fixture.shared_root / "ordinary") &&
            scan->snapshot_or_throw().entries.empty() &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "reserved-path rejection changed the filesystem, catalog, or replica cutpoint");

    write_file(fixture.shared_root / reserved_component, "private-looking");
    require_error(
        [&] { (void)scan->scan_regular_file_or_throw(reserved_component); },
        "reserved atomic-publication namespace",
        "direct folder publication accepted a reserved private basename");
}

void test_incomplete_scan_cannot_infer_deletion() {
    Fixture fixture("anonsync-folder-pass-incomplete-delete");
    write_file(fixture.shared_root / "kept.txt", "kept");
    write_file(fixture.shared_root / "removed.txt", "removed");
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "incomplete-delete catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
    require(fs::remove(fixture.shared_root / "removed.txt"),
            "incomplete-delete fixture could not remove its cataloged file");
    write_file(fixture.shared_root / "budget-blocker.txt", "blocker");

    auto bounded = Fixture::pass_limits();
    bounded.maximum_entries = 1U;
    require_error(
        [&] { (void)scan->run_convergence_pass_or_throw(bounded); },
        "exceeds configured entry limit",
        "bounded traversal unexpectedly reached complete-scan deletion authority");
    const auto retained = find_entry(
        scan->snapshot_or_throw(), "removed.txt");
    require(
        retained.has_value() &&
            retained->kind == anonsync::SyncReplicaValueKind::File &&
            scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "failed traversal inferred deletion from an incomplete namespace prefix");
}

void test_bounded_whole_folder_pass_bound_stop_and_restart() {
    Fixture fixture("anonsync-folder-pass-bound-stop");
    const std::string first_bytes = "four";
    const std::string second_bytes = "eight888";
    write_file(fixture.shared_root / "a-first.txt", first_bytes);
    write_file(fixture.shared_root / "z-second.txt", second_bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "folder-pass bound-stop catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto tight = Fixture::pass_limits();
    tight.maximum_file_bytes = 8U;
    tight.maximum_total_file_bytes = 8U;
    const auto bounded = scan->run_convergence_pass_or_throw(tight);
    require(
        !bounded.completed_local_scan_epoch &&
            !bounded.restarted_local_scan_epoch &&
            bounded.local_scan_seen_path_count == 1U &&
            bounded.local_scan_resume_after_path == "a-first.txt" &&
            bounded.local_published_count == 1U,
        "bounded pass did not persist one deterministic prefix step");
    const auto partial_catalog = scan->snapshot_or_throw();
    const auto partial_replica = fixture.replica.snapshot_or_throw();
    require(
        partial_catalog.entries.size() == 1U &&
            partial_catalog.entries.front().canonical_path == "a-first.txt" &&
            partial_replica.durable.operations.size() == 1U &&
            read_file(fixture.shared_root / "z-second.txt") == second_bytes,
        "bounded stop did not preserve its earlier path-local progress and untouched later bytes");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    auto sufficient = Fixture::pass_limits();
    sufficient.maximum_file_bytes = 32U;
    sufficient.maximum_total_file_bytes = 32U;
    const auto resumed = scan->run_convergence_pass_or_throw(sufficient);
    require(
        resumed.completed_local_scan_epoch &&
            !resumed.restarted_local_scan_epoch &&
            resumed.local_catalog_no_op_count == 0U &&
            resumed.local_published_count == 1U &&
            resumed.local_scan_seen_path_count == 0U &&
            resumed.local_scan_resume_after_path.empty() &&
            scan->snapshot_or_throw().entries.size() == 2U &&
            fixture.replica.snapshot_or_throw().durable.operations.size() == 2U,
        "restart did not continue from the durable prefix and complete the epoch exactly once");
}

void test_durable_scan_epoch_delays_deletion_until_complete_suffix() {
    Fixture fixture("anonsync-folder-pass-durable-delete");
    write_file(fixture.shared_root / "a.txt", "aaaa");
    write_file(fixture.shared_root / "m.txt", "mmmm");
    write_file(fixture.shared_root / "y.txt", "yyyy");
    write_file(fixture.shared_root / "z.txt", "zzzz");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "durable-delete catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
    require(
        catalog_cutpoint.entries.size() == 4U &&
            fs::remove(fixture.shared_root / "z.txt"),
        "durable-delete fixture did not establish and remove its suffix file");

    auto one_file = Fixture::pass_limits();
    one_file.maximum_file_bytes = 4U;
    one_file.maximum_total_file_bytes = 4U;

    const auto first = scan->run_convergence_pass_or_throw(one_file);
    require(
        !first.completed_local_scan_epoch &&
            !first.restarted_local_scan_epoch &&
            first.local_scan_seen_path_count == 1U &&
            first.local_scan_resume_after_path == "a.txt" &&
            first.deferred_unadjudicated_local_absence_remote_file_count == 1U &&
            !fs::exists(fixture.shared_root / "z.txt") &&
            scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "first bounded epoch segment restored or deleted the unseen suffix");

    const std::uint64_t scan_epoch = first.local_scan_epoch;
    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto second = scan->run_convergence_pass_or_throw(one_file);
    require(
        second.local_scan_epoch == scan_epoch &&
            !second.completed_local_scan_epoch &&
            !second.restarted_local_scan_epoch &&
            second.local_scan_seen_path_count == 2U &&
            second.local_scan_resume_after_path == "m.txt" &&
            second.deferred_unadjudicated_local_absence_remote_file_count == 1U &&
            !fs::exists(fixture.shared_root / "z.txt") &&
            scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "restart did not retain deletion intent through the second epoch segment");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto completed = scan->run_convergence_pass_or_throw(one_file);
    const auto tombstone = find_entry(scan->snapshot_or_throw(), "z.txt");
    require(
        completed.local_scan_epoch == scan_epoch &&
            completed.completed_local_scan_epoch &&
            !completed.restarted_local_scan_epoch &&
            completed.local_scan_seen_path_count == 0U &&
            completed.local_scan_resume_after_path.empty() &&
            completed.local_published_count == 1U &&
            completed.deferred_unadjudicated_local_absence_remote_file_count == 0U &&
            tombstone.has_value() &&
            tombstone->kind ==
                anonsync::SyncReplicaValueKind::Tombstone &&
            !fs::exists(fixture.shared_root / "z.txt") &&
            fixture.replica.snapshot_or_throw().durable.operations.size() ==
                replica_cutpoint.durable.operations.size() + 1U,
        "completed durable epoch did not publish the suffix deletion exactly once");
}

void test_completed_epoch_does_not_restore_deleted_seen_prefix() {
    Fixture fixture("anonsync-folder-pass-deleted-seen-prefix");
    write_file(fixture.shared_root / "a.txt", "aaaa");
    write_file(fixture.shared_root / "z.txt", "zzzz");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "deleted-seen-prefix catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

    auto one_file = Fixture::pass_limits();
    one_file.maximum_file_bytes = 4U;
    one_file.maximum_total_file_bytes = 4U;
    const auto prefix = scan->run_convergence_pass_or_throw(one_file);
    require(
        !prefix.completed_local_scan_epoch &&
            prefix.local_scan_seen_path_count == 1U &&
            prefix.local_scan_resume_after_path == "a.txt",
        "deleted-seen-prefix fixture did not persist its first segment");
    require(
        fs::remove(fixture.shared_root / "a.txt"),
        "deleted-seen-prefix fixture could not remove its visited path");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto completed = scan->run_convergence_pass_or_throw(one_file);
    require(
        completed.completed_local_scan_epoch &&
            !completed.restarted_local_scan_epoch &&
            completed.local_scan_seen_path_count == 0U &&
            completed.local_scan_resume_after_path.empty() &&
            completed
                    .deferred_unadjudicated_local_absence_remote_file_count ==
                1U &&
            completed.remote_applied_count == 0U &&
            !fs::exists(fixture.shared_root / "a.txt") &&
            scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "epoch completion restored a deleted path that was seen only in an earlier segment");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto adjudicated = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto tombstone = find_entry(scan->snapshot_or_throw(), "a.txt");
    require(
        adjudicated.completed_local_scan_epoch &&
            adjudicated.local_published_count == 1U &&
            adjudicated
                    .deferred_unadjudicated_local_absence_remote_file_count ==
                0U &&
            adjudicated.remote_applied_count == 0U &&
            tombstone.has_value() &&
            tombstone->kind ==
                anonsync::SyncReplicaValueKind::Tombstone &&
            !fs::exists(fixture.shared_root / "a.txt") &&
            fixture.replica.snapshot_or_throw().durable.operations.size() ==
                replica_cutpoint.durable.operations.size() + 1U,
        "the next epoch did not publish the deferred local deletion exactly once");
}

void test_scan_epoch_restarts_when_absent_prefix_reappears() {
    Fixture fixture("anonsync-folder-pass-prefix-reappears");
    write_file(fixture.shared_root / "a.txt", "aaaa");
    write_file(fixture.shared_root / "m.txt", "mmmm");
    write_file(fixture.shared_root / "z.txt", "zzzz");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "prefix-reappears catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
    require(
        fs::remove(fixture.shared_root / "a.txt"),
        "prefix-reappears fixture could not remove its first path");

    auto one_file = Fixture::pass_limits();
    one_file.maximum_file_bytes = 4U;
    one_file.maximum_total_file_bytes = 4U;
    const auto first = scan->run_convergence_pass_or_throw(one_file);
    require(
        !first.completed_local_scan_epoch &&
            first.local_scan_resume_after_path == "m.txt" &&
            first.local_scan_seen_path_count == 1U &&
            first.deferred_unadjudicated_local_absence_remote_file_count == 1U &&
            !fs::exists(fixture.shared_root / "a.txt"),
        "bounded scan did not leave the absent prefix pending");

    write_file(fixture.shared_root / "a.txt", "aaaa");
    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto restarted = scan->run_convergence_pass_or_throw(one_file);
    require(
        restarted.local_scan_epoch == first.local_scan_epoch &&
            !restarted.completed_local_scan_epoch &&
            restarted.restarted_local_scan_epoch &&
            restarted.local_scan_seen_path_count == 0U &&
            restarted.local_scan_resume_after_path.empty() &&
            restarted.local_published_count == 0U &&
            restarted.deferred_unadjudicated_local_absence_remote_file_count == 0U &&
            read_file(fixture.shared_root / "a.txt") == "aaaa" &&
            scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "completed traversal classified an unseen-but-present prefix as absent");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto stable = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto stable_catalog = scan->snapshot_or_throw();
    bool retained_value_authority =
        stable_catalog.entries.size() == catalog_cutpoint.entries.size();
    if (retained_value_authority) {
        for (std::size_t index = 0U;
             index < stable_catalog.entries.size(); ++index) {
            const auto& before = catalog_cutpoint.entries[index];
            const auto& after = stable_catalog.entries[index];
            retained_value_authority =
                before.canonical_path == after.canonical_path &&
                before.kind == after.kind &&
                before.size_bytes == after.size_bytes &&
                before.content_sha256 == after.content_sha256 &&
                before.operation_id == after.operation_id;
            if (!retained_value_authority) break;
        }
    }
    require(
        stable.completed_local_scan_epoch &&
            !stable.restarted_local_scan_epoch &&
            stable.local_scan_epoch != first.local_scan_epoch &&
            stable.local_published_count == 0U &&
            stable.local_catalog_no_op_count +
                    stable.local_catalog_refreshed_count ==
                3U &&
            retained_value_authority &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "restarted epoch did not return to one stable complete observation without changing value authority");
}

void test_incomplete_epoch_defers_tombstone_behind_cursor() {
    Fixture fixture("anonsync-folder-pass-tombstone-behind-cursor");
    const std::string base_bytes = "aaaa";
    const std::string edited_bytes = "EDIT";
    write_file(fixture.shared_root / "a.txt", base_bytes);
    write_file(fixture.shared_root / "z.txt", "zzzz");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "tombstone-behind-cursor catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto base_entry = find_entry(scan->snapshot_or_throw(), "a.txt");
    require(base_entry.has_value(),
            "tombstone-behind-cursor fixture lost its catalog base");
    const auto base_operation = restore_model(
        fixture.replica.snapshot_or_throw())
                                    .operation_by_id(base_entry->operation_id);
    require(base_operation.has_value(),
            "tombstone-behind-cursor fixture lost its replica base");

    auto one_file = Fixture::pass_limits();
    one_file.maximum_file_bytes = 4U;
    one_file.maximum_total_file_bytes = 4U;
    const auto prefix = scan->run_convergence_pass_or_throw(one_file);
    require(
        !prefix.completed_local_scan_epoch &&
            prefix.local_scan_seen_path_count == 1U &&
            prefix.local_scan_resume_after_path == "a.txt",
        "tombstone-behind-cursor fixture did not persist its first path");

    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-tombstone-behind-cursor", 38U});
    (void)remote.accept_remote_or_throw(*base_operation);
    const auto tombstone = remote.create_local_tombstone_or_throw("a.txt");
    require(
        fixture.replica.accept_remote_or_throw(tombstone) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "tombstone-behind-cursor fixture did not admit its remote tombstone");
    write_file(fixture.shared_root / "a.txt", edited_bytes);
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto suffix = scan->run_convergence_pass_or_throw(one_file);
    require(
        suffix.completed_local_scan_epoch &&
            suffix.skipped_tombstone_remote_path_count == 1U &&
            suffix.remote_applied_count == 0U &&
            read_file(fixture.shared_root / "a.txt") == edited_bytes &&
            scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "generic remote planning applied or rejected a tombstone behind the durable cursor");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto revisited = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        revisited.completed_local_scan_epoch &&
            revisited.skipped_conflicted_remote_path_count == 1U &&
            revisited.skipped_tombstone_remote_path_count == 1U &&
            revisited.remote_applied_count == 0U &&
            revisited.local_published_count == 0U &&
            read_file(fixture.shared_root / "a.txt") == edited_bytes &&
            scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "the next epoch did not preserve the local-edit/remote-delete conflict");
}

void test_scan_progress_tampering_fails_closed() {
    Fixture fixture("anonsync-folder-pass-progress-tamper");
    write_file(fixture.shared_root / "a.txt", "four");
    write_file(fixture.shared_root / "z.txt", "eight888");
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "progress-tamper catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto bounded = Fixture::pass_limits();
    bounded.maximum_file_bytes = 8U;
    bounded.maximum_total_file_bytes = 8U;
    const auto partial = scan->run_convergence_pass_or_throw(bounded);
    require(
        !partial.completed_local_scan_epoch &&
            partial.local_scan_seen_path_count == 1U,
        "progress-tamper fixture did not retain an incomplete epoch");
    scan.reset();

    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "UPDATE sync_replica_folder_catalog_scan_seen "
        "SET chain_digest='0000000000000000000000000000000000000000000000000000000000000000' "
        "WHERE ordinal=1;",
        "progress-tamper fixture mutation");
    require_error(
        [&] { (void)fixture.make_scan_owner(catalog_db); },
        "scan-progress tail does not match its head",
        "folder owner accepted a tampered durable continuation journal");

    {
        Fixture cursor_fixture("anonsync-folder-pass-remote-cursor-tamper");
        anonsync::SyncSqliteDb cursor_db = open_database(
            cursor_fixture.catalog_path(), "remote-cursor-tamper catalog");
        auto cursor_owner = cursor_fixture.make_scan_owner(cursor_db);
        cursor_owner.reset();
        anonsync::sqlite_exec_or_throw(
            cursor_db.db,
            "UPDATE sync_replica_folder_catalog_remote_apply_progress "
            "SET resume_after_path='../escape' WHERE id=1;",
            "remote-cursor-tamper fixture mutation");
        require_error(
            [&] { (void)cursor_fixture.make_scan_owner(cursor_db); },
            "remote-apply cursor scan-progress path is invalid",
            "folder owner accepted a noncanonical remote scheduling cursor");
    }

    {
        Fixture sweep_fixture("anonsync-folder-pass-remote-sweep-tamper");
        anonsync::SyncSqliteDb sweep_db = open_database(
            sweep_fixture.catalog_path(), "remote-sweep-tamper catalog");
        auto sweep_owner = sweep_fixture.make_scan_owner(sweep_db);
        sweep_owner.reset();
        anonsync::sqlite_exec_or_throw(
            sweep_db.db,
            "UPDATE sync_replica_folder_catalog_remote_apply_progress "
            "SET inspection_sweep_basis_digest="
            "'1111111111111111111111111111111111111111111111111111111111111111',"
            "inspection_sweep_seen_path_count=1 WHERE id=1;",
            "remote-sweep-tamper fixture mutation");
        require_error(
            [&] { (void)sweep_fixture.make_scan_owner(sweep_db); },
            "remote inspection sweep state is invalid",
            "folder owner accepted an active remote sweep without its last acknowledged path");
    }

    {
        Fixture origin_fixture(
            "anonsync-folder-pass-remote-sweep-origin-tamper");
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id,
            {"device-folder-pass-origin-tamper", 410U});
        for (const std::string path : {"a.txt", "b.txt", "c.txt"}) {
            const std::string bytes = "unretained remote bytes for " + path;
            const auto operation = remote.create_local_file_or_throw(
                path, bytes.size(), anonsync::sha256_hex(bytes));
            require(
                origin_fixture.replica.accept_remote_or_throw(operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive,
                "remote sweep-origin tamper fixture rejected evidence");
        }

        anonsync::SyncSqliteDb origin_db = open_database(
            origin_fixture.catalog_path(),
            "remote-sweep-origin-tamper catalog");
        auto origin_owner = origin_fixture.make_scan_owner(origin_db);
        auto one_path = Fixture::pass_limits();
        one_path.maximum_remote_inspection_paths = 1U;
        const auto partial =
            origin_owner->run_convergence_pass_or_throw(one_path);
        const auto catalog_cutpoint = origin_owner->snapshot_or_throw();
        const auto progress_cutpoint =
            origin_owner->scan_progress_snapshot_or_throw();
        require(
            partial.remote_inspected_path_count == 1U &&
                partial.remote_acknowledged_path_count == 1U &&
                partial.remote_apply_resume_after_path == "a.txt" &&
                !partial.completed_remote_inspection_sweep &&
                !progress_cutpoint
                     .remote_inspection_sweep_basis_digest.empty() &&
                progress_cutpoint
                    .remote_inspection_sweep_started_after_path.empty() &&
                progress_cutpoint
                        .remote_inspection_sweep_seen_path_count ==
                    1U,
            "remote sweep-origin tamper fixture did not retain its first cyclic segment");
        origin_owner.reset();

        // Every retained field remains individually canonical and in range,
        // but the forged origin says that a one-path segment should have ended
        // at b.txt rather than the retained a.txt cursor.
        anonsync::sqlite_exec_or_throw(
            origin_db.db,
            "UPDATE sync_replica_folder_catalog_remote_apply_progress "
            "SET inspection_sweep_started_after_path='a.txt' WHERE id=1;",
            "remote-sweep-origin-tamper fixture mutation");
        origin_owner = origin_fixture.make_scan_owner(origin_db);
        require_error(
            [&] {
                (void)origin_owner->run_convergence_pass_or_throw(one_path);
            },
            "remote inspection sweep cursor/count disagrees with its projection origin",
            "folder owner trusted an internally inconsistent cyclic remote sweep");
        require(
            origin_owner->snapshot_or_throw() == catalog_cutpoint &&
                !fs::exists(origin_fixture.shared_root / "a.txt") &&
                !fs::exists(origin_fixture.shared_root / "b.txt") &&
                !fs::exists(origin_fixture.shared_root / "c.txt"),
            "rejected sweep-origin tampering changed shared or catalog state");
    }
}

void test_bounded_whole_folder_pass_missing_payload_and_remote_limit() {
    {
        Fixture fixture("anonsync-folder-pass-missing-payload");
        const std::string path = "remote-missing.txt";
        const std::string bytes = "bytes not retained locally";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-missing", 35U});
        const auto operation = remote.create_local_file_or_throw(
            path, bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "missing-payload fixture did not retain remote evidence");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(),
            "folder-pass missing-payload catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
        const auto pass = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            pass.remote_apply_operation_count == 0U &&
                pass.remote_payload_snapshot_observation_count == 0U &&
                pass.remote_payload_snapshot_entry_count == 0U &&
                pass.remote_targeted_payload_access_count == 1U &&
                pass.remote_targeted_payload_probe_count == 1U &&
                pass.remote_targeted_payload_selection_count == 0U &&
                pass.remote_targeted_payload_selected_bytes == 0U &&
                pass.deferred_remote_payload_candidate_count == 1U &&
                pass.deferred_remote_apply_candidate_count == 0U &&
                pass.remote_inspection_sweep_had_unresolved_paths &&
                pass.remote_apply_stop_reason ==
                    anonsync::SyncReplicaFolderRemoteApplyStopReason::
                        EndOfProjection &&
                !fs::exists(fixture.shared_root / path) &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "missing remote payload was not retained as bounded scheduling remainder");
    }

    {
        Fixture fixture("anonsync-folder-pass-missing-payload-ready-suffix");
        const std::string missing_bytes = "missing prefix bytes";
        const std::string ready_bytes = "ready suffix bytes";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id,
            {"device-folder-pass-missing-ready-suffix", 351U});
        const auto missing = remote.create_local_file_or_throw(
            "a-missing.txt", missing_bytes.size(),
            anonsync::sha256_hex(missing_bytes));
        const auto ready = remote.create_local_file_or_throw(
            "z-ready.txt", ready_bytes.size(),
            anonsync::sha256_hex(ready_bytes));
        require(
            fixture.replica.accept_remote_or_throw(missing) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.replica.accept_remote_or_throw(ready) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(ready_bytes)
                        .content_sha256 == ready.content_sha256,
            "missing-payload suffix fixture did not retain its ready payload");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(),
            "folder-pass missing-payload ready-suffix catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto pass = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        require(
            pass.remote_applied_count == 1U &&
                pass.remote_apply_operation_count == 1U &&
                pass.remote_payload_snapshot_observation_count == 0U &&
                pass.remote_payload_snapshot_entry_count == 0U &&
                pass.remote_targeted_payload_access_count == 1U &&
                pass.remote_targeted_payload_probe_count == 2U &&
                pass.remote_targeted_payload_selection_count == 1U &&
                pass.remote_targeted_payload_selected_bytes ==
                    ready_bytes.size() &&
                pass.deferred_remote_payload_candidate_count == 1U &&
                pass.deferred_remote_apply_candidate_count == 0U &&
                pass.remote_inspection_sweep_had_unresolved_paths &&
                pass.remote_apply_resume_after_path == "z-ready.txt" &&
                pass.remote_apply_stop_reason ==
                    anonsync::SyncReplicaFolderRemoteApplyStopReason::
                        EndOfProjection &&
                !fs::exists(fixture.shared_root / "a-missing.txt") &&
                read_file(fixture.shared_root / "z-ready.txt") == ready_bytes,
            "an unavailable remote prefix blocked a ready suffix or forced repeated inventories");
    }

    {
        Fixture fixture("anonsync-folder-pass-remote-limit");
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-limit", 36U});
        const std::string first_bytes = "remote one";
        const std::string second_bytes = "remote two";
        const auto first = remote.create_local_file_or_throw(
            "one.txt", first_bytes.size(), anonsync::sha256_hex(first_bytes));
        const auto second = remote.create_local_file_or_throw(
            "two.txt", second_bytes.size(), anonsync::sha256_hex(second_bytes));
        require(
            fixture.replica.accept_remote_or_throw(first) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.replica.accept_remote_or_throw(second) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(first_bytes)
                        .content_sha256 == first.content_sha256 &&
                fixture.payload_store.put_payload_or_throw(second_bytes)
                        .content_sha256 == second.content_sha256,
            "remote-limit fixture did not retain both remote values");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass remote-limit catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto limits = Fixture::pass_limits();
        limits.maximum_remote_paths = 1U;
        require_error(
            [&] { (void)scan->run_convergence_pass_or_throw(limits); },
            "exceeds its remote-path limit",
            "folder pass crossed its configured remote-path bound");
        require(
            !fs::exists(fixture.shared_root / "one.txt") &&
                !fs::exists(fixture.shared_root / "two.txt") &&
                scan->snapshot_or_throw().entries.empty(),
            "remote-path preflight applied a prefix before rejecting the bound");
    }
}

void
test_targeted_remote_payload_path_does_not_claim_complete_namespace_audit() {
    Fixture fixture("anonsync-folder-pass-targeted-payload-namespace-nonclaim");
    const std::string path = "remote-target.txt";
    const std::string bytes = "selected payload remains exact";
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-targeted-payload-namespace", 352U});
    const auto operation = remote.create_local_file_or_throw(
        path, bytes.size(), anonsync::sha256_hex(bytes));
    require(
        fixture.payload_store.put_payload_or_throw(bytes).content_sha256 ==
                operation.content_sha256 &&
            fixture.replica.accept_remote_or_throw(operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
        "targeted payload namespace fixture did not retain its selected value");

    // A complete payload inventory must reject this unowned namespace entry.
    // The bounded remote-only lane may nevertheless prove and consume the
    // independently named selected digest without enumerating or trusting the
    // unrelated entry. This is an explicit nonclaim, not namespace health.
    write_file(fixture.payload_root / "unexpected-operator-note", "hostile");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "targeted payload namespace-nonclaim catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        pass.remote_applied_count == 1U &&
            pass.remote_apply_operation_count == 1U &&
            pass.remote_payload_snapshot_observation_count == 0U &&
            pass.remote_payload_snapshot_entry_count == 0U &&
            pass.remote_targeted_payload_access_count == 1U &&
            pass.remote_targeted_payload_probe_count == 1U &&
            pass.remote_targeted_payload_selection_count == 1U &&
            pass.remote_targeted_payload_selected_bytes == bytes.size() &&
            pass.deferred_remote_payload_candidate_count == 0U &&
            pass.deferred_remote_apply_candidate_count == 0U &&
            pass.completed_remote_inspection_sweep &&
            !pass.remote_inspection_sweep_had_unresolved_paths &&
            read_file(fixture.shared_root / path) == bytes,
        "targeted remote payload lane enumerated unrelated namespace state "
        "or lost exact selected-byte proof");
    require_error(
        [&] { (void)fixture.payload_store.snapshot_or_throw(); },
        "unexpected payload-root entry",
        "targeted selection was incorrectly promoted to a complete payload "
        "namespace audit");
}

void test_targeted_remote_payload_rejects_legacy_v1_split_identity() {
    Fixture fixture("anonsync-folder-pass-targeted-payload-v1-split-authority");
    const std::string path = "remote-target.txt";
    const std::string bytes = "selected payload requires one lock authority";
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-targeted-payload-v1-split", 353U});
    const auto operation = remote.create_local_file_or_throw(
        path, bytes.size(), anonsync::sha256_hex(bytes));
    require(
        fixture.payload_store.put_payload_or_throw(bytes).content_sha256 ==
                operation.content_sha256 &&
            fixture.replica.accept_remote_or_throw(operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
        "targeted v1 split-authority fixture did not retain remote evidence");

    // The remote-only lane deliberately does not enumerate unrelated payload
    // entries, but that optimization cannot ignore another generation's lock
    // basename. A v1 reader and the current reader would otherwise coordinate
    // through different inodes while selecting the same digest-named payload.
    const fs::path current_identity =
        fixture.payload_root /
        ".anonsync-payload-store-identity-v2-reader-fence-v1";
    const fs::path legacy_v1_identity =
        fixture.payload_root / ".anonsync-payload-store-identity-v1";
    write_file(
        legacy_v1_identity,
        "anonsync:sync-replica-file-payload-store-identity:v1\n" +
            Fixture::folder_id + "\n");
    fs::permissions(
        legacy_v1_identity,
        fs::perms::owner_read | fs::perms::owner_write,
        fs::perm_options::replace);
    require(
        fs::is_regular_file(current_identity) &&
            fs::is_regular_file(legacy_v1_identity),
        "targeted v1 split-authority fixture lacks both lock names");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "targeted v1 split-authority catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    require_error(
        [&] {
            (void)scan->run_convergence_pass_or_throw(
                Fixture::pass_limits());
        },
        "coexisting incompatible payload-store identity marker: "
        ".anonsync-payload-store-identity-v1",
        "targeted remote payload access ignored a legacy v1 lock authority");
    require(
        !fs::exists(fixture.shared_root / path) &&
            scan->snapshot_or_throw().entries.empty() &&
            fs::is_regular_file(current_identity) &&
            fs::is_regular_file(legacy_v1_identity),
        "targeted v1 split-authority rejection published bytes, catalog state, "
        "or deleted forensic evidence");
}

void test_targeted_remote_payload_hashes_only_at_publication_boundary() {
    Fixture fixture("anonsync-folder-pass-targeted-payload-publication-hash");
    (void)fixture.payload_store.snapshot_or_throw();

    const std::string path = "corrupt-target.txt";
    const std::string expected_bytes = "selected payload must remain exact";
    const std::string corrupt_bytes(expected_bytes.size(), 'x');
    const std::string digest = anonsync::sha256_hex(expected_bytes);
    write_file(fixture.payload_root / digest, corrupt_bytes);
    fs::permissions(
        fixture.payload_root / digest,
        fs::perms::owner_read | fs::perms::owner_write,
        fs::perm_options::replace);

    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-targeted-payload-corruption", 354U});
    const auto operation = remote.create_local_file_or_throw(
        path, expected_bytes.size(), digest);
    require(
        fixture.replica.accept_remote_or_throw(operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "targeted payload corruption fixture did not retain remote evidence");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "targeted payload corruption catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    require_error(
        [&] {
            (void)scan->run_convergence_pass_or_throw(
                Fixture::pass_limits());
        },
        "source SHA-256 changed before publication",
        "targeted payload corruption crossed the atomic publication boundary");
    require(
        !fs::exists(fixture.shared_root / path) &&
            scan->snapshot_or_throw().entries.empty(),
        "failed targeted payload publication left visible bytes or catalog state");
    require_error(
        [&] { (void)fixture.payload_store.snapshot_or_throw(); },
        "payload bytes do not match digest basename",
        "complete payload inventory accepted the corrupt selected digest");
}

void test_remote_only_tombstone_catalog_defers_complete_payload_inventory() {
    Fixture fixture("anonsync-folder-pass-tombstone-only-targeted-payload");
    const std::string deleted_path = "deleted-local.txt";
    const std::string deleted_bytes = "retained historical payload";
    write_file(fixture.shared_root / deleted_path, deleted_bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "tombstone-only targeted-payload catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto published = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        published.local_published_count == 1U,
        "tombstone-only targeted-payload fixture did not publish its local base");
    require(
        fs::remove(fixture.shared_root / deleted_path),
        "tombstone-only targeted-payload fixture could not remove its base");
    const auto deleted = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto deleted_entry =
        find_entry(scan->snapshot_or_throw(), deleted_path);
    require(
        deleted.local_published_count == 1U &&
            deleted.traversal.regular_file_count == 0U &&
            deleted.payload_mutation_batch_count == 0U &&
            deleted_entry.has_value() &&
            deleted_entry->kind ==
                anonsync::SyncReplicaValueKind::Tombstone,
        "all-absent local traversal did not establish a tombstone-only "
        "catalog without payload mutation work");

    const std::string remote_path = "new-remote.txt";
    const std::string remote_bytes = "new exact remote payload";
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-tombstone-only-targeted-payload", 353U});
    const auto operation = remote.create_local_file_or_throw(
        remote_path, remote_bytes.size(), anonsync::sha256_hex(remote_bytes));
    require(
        fixture.payload_store.put_payload_or_throw(remote_bytes).content_sha256 ==
                operation.content_sha256 &&
            fixture.replica.accept_remote_or_throw(operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
        "tombstone-only targeted-payload fixture did not retain its remote value");
    write_file(fixture.payload_root / "unexpected-audit-only-entry", "hostile");

    const auto pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        !pass.used_idle_fast_path &&
            pass.traversal.regular_file_count == 0U &&
            pass.payload_mutation_batch_count == 0U &&
            pass.remote_applied_count == 1U &&
            pass.remote_apply_operation_count == 1U &&
            pass.remote_payload_snapshot_observation_count == 0U &&
            pass.remote_payload_snapshot_entry_count == 0U &&
            pass.remote_targeted_payload_access_count == 1U &&
            pass.remote_targeted_payload_probe_count == 1U &&
            pass.remote_targeted_payload_selection_count == 1U &&
            pass.remote_targeted_payload_selected_bytes == remote_bytes.size() &&
            pass.completed_remote_inspection_sweep &&
            !pass.remote_inspection_sweep_had_unresolved_paths &&
            read_file(fixture.shared_root / remote_path) == remote_bytes,
        "remote-only work behind a tombstone catalog forced a complete "
        "payload inventory or lost exact selected-byte proof");
    require_error(
        [&] { (void)fixture.payload_store.snapshot_or_throw(); },
        "unexpected payload-root entry",
        "remote-only tombstone-catalog selection concealed the complete "
        "inventory oracle's namespace rejection");
}

void test_bounded_whole_folder_pass_remote_work_bounds() {
    {
        Fixture fixture("anonsync-folder-pass-remote-byte-total");
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-byte-total", 37U});
        const std::string first_bytes = "123456";
        const std::string second_bytes = "abcdef";
        const auto first = remote.create_local_file_or_throw(
            "first.txt", first_bytes.size(), anonsync::sha256_hex(first_bytes));
        const auto second = remote.create_local_file_or_throw(
            "second.txt", second_bytes.size(), anonsync::sha256_hex(second_bytes));
        require(
            fixture.replica.accept_remote_or_throw(first) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.replica.accept_remote_or_throw(second) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(first_bytes)
                        .content_sha256 == first.content_sha256 &&
                fixture.payload_store.put_payload_or_throw(second_bytes)
                        .content_sha256 == second.content_sha256,
            "remote-byte-total fixture did not retain both remote files");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass remote-byte-total catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto limits = Fixture::pass_limits();
        limits.maximum_file_bytes = 10U;
        limits.maximum_total_file_bytes = 10U;
        const auto first_pass =
            scan->run_convergence_pass_or_throw(limits);
        require(
            first_pass.remote_applied_count == 1U &&
                first_pass.remote_apply_operation_count == 1U &&
                first_pass.exact_remote_file_bytes == first_bytes.size() &&
                first_pass.deferred_remote_apply_candidate_count == 1U &&
                first_pass.remote_apply_stop_reason ==
                    anonsync::SyncReplicaFolderRemoteApplyStopReason::
                        AggregateFileByteFrontier &&
                fs::exists(fixture.shared_root / "first.txt") &&
                read_file(fixture.shared_root / "first.txt") == first_bytes &&
                !fs::exists(fixture.shared_root / "second.txt") &&
                scan->snapshot_or_throw().entries.size() == 1U,
            "remote aggregate frontier did not commit exactly one safe prefix");

        const auto second_pass =
            scan->run_convergence_pass_or_throw(limits);
        require(
            second_pass.remote_applied_count == 1U &&
                second_pass.remote_apply_operation_count == 1U &&
                second_pass.exact_remote_file_bytes == second_bytes.size() &&
                second_pass.deferred_remote_apply_candidate_count == 0U &&
                second_pass.remote_apply_stop_reason ==
                    anonsync::SyncReplicaFolderRemoteApplyStopReason::
                        EndOfProjection &&
                read_file(fixture.shared_root / "first.txt") == first_bytes &&
                read_file(fixture.shared_root / "second.txt") == second_bytes &&
                scan->snapshot_or_throw().entries.size() == 2U,
            "remote aggregate frontier did not advance its deferred suffix on the next pass");
    }

    {
        Fixture fixture("anonsync-folder-pass-remote-byte-file");
        const std::string bytes = "12345";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-byte-file", 38U});
        const auto operation = remote.create_local_file_or_throw(
            "large.txt", bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes)
                        .content_sha256 == operation.content_sha256,
            "remote-byte-file fixture did not retain its remote file");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass remote-byte-file catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto limits = Fixture::pass_limits();
        limits.maximum_file_bytes = 4U;
        require_error(
            [&] { (void)scan->run_convergence_pass_or_throw(limits); },
            "remote file exceeds its per-file byte limit",
            "folder pass crossed its per-file remote byte bound");
        require(
            !fs::exists(fixture.shared_root / "large.txt") &&
                scan->snapshot_or_throw().entries.empty(),
            "remote per-file refusal changed the folder or catalog");
    }

    {
        Fixture fixture("anonsync-folder-pass-remote-path-depth");
        const std::string bytes = "nested bytes";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-depth", 39U});
        const auto operation = remote.create_local_file_or_throw(
            "nested/deep.txt", bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes)
                        .content_sha256 == operation.content_sha256,
            "remote-depth fixture did not retain its remote file");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass remote-depth catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto limits = Fixture::pass_limits();
        limits.maximum_directory_depth = 0U;
        require_error(
            [&] { (void)scan->run_convergence_pass_or_throw(limits); },
            "remote path exceeds its directory-depth limit",
            "folder pass crossed its remote directory-depth bound");
        require(
            !fs::exists(fixture.shared_root / "nested") &&
                scan->snapshot_or_throw().entries.empty(),
            "remote depth refusal changed the folder or catalog");
    }

    {
        Fixture fixture("anonsync-folder-pass-remote-path-bytes");
        const std::string bytes = "path bytes";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-path-bytes", 40U});
        const auto operation = remote.create_local_file_or_throw(
            "long.txt", bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes)
                        .content_sha256 == operation.content_sha256,
            "remote-path-bytes fixture did not retain its remote file");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass remote-path-bytes catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto limits = Fixture::pass_limits();
        limits.maximum_relative_path_bytes = 4U;
        require_error(
            [&] { (void)scan->run_convergence_pass_or_throw(limits); },
            "remote path exceeds its relative-path byte limit",
            "folder pass crossed its remote relative-path byte bound");
        require(
            !fs::exists(fixture.shared_root / "long.txt") &&
                scan->snapshot_or_throw().entries.empty(),
            "remote path-byte refusal changed the folder or catalog");
    }

    {
        Fixture fixture("anonsync-folder-pass-remote-prefix-preflight");
        const std::string first_bytes = "safe prefix";
        const std::string invalid_bytes = "invalid suffix";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-folder-pass-prefix-preflight", 41U});
        const auto first = remote.create_local_file_or_throw(
            "a.txt", first_bytes.size(), anonsync::sha256_hex(first_bytes));
        const auto invalid = remote.create_local_file_or_throw(
            "zz-too-long.txt", invalid_bytes.size(),
            anonsync::sha256_hex(invalid_bytes));
        require(
            fixture.replica.accept_remote_or_throw(first) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.replica.accept_remote_or_throw(invalid) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(first_bytes)
                        .content_sha256 == first.content_sha256 &&
                fixture.payload_store.put_payload_or_throw(invalid_bytes)
                        .content_sha256 == invalid.content_sha256,
            "remote-prefix-preflight fixture did not retain both remote files");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "folder-pass remote-prefix-preflight catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
        auto limits = Fixture::pass_limits();
        limits.maximum_relative_path_bytes = 5U;
        limits.maximum_local_scan_segment_regular_files = 1U;
        limits.maximum_remote_apply_operations = 1U;
        limits.maximum_remote_inspection_paths = 1U;
        require_error(
            [&] { (void)scan->run_convergence_pass_or_throw(limits); },
            "remote path exceeds its relative-path byte limit",
            "remote cyclic scheduling weakened complete-projection path preflight");
        require(
            !fs::exists(fixture.shared_root / "a.txt") &&
                !fs::exists(fixture.shared_root / "zz-too-long.txt") &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "remote suffix preflight applied a selected prefix before rejecting invalid evidence");
    }
}

void test_remote_apply_count_frontier_bounds_zero_byte_and_tombstone_work() {
    Fixture fixture("anonsync-folder-pass-remote-count-frontier");
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-folder-pass-count-frontier", 41U});
    const std::string empty_digest = anonsync::sha256_hex("");
    const auto first = remote.create_local_file_or_throw(
        "a-empty.txt", 0U, empty_digest);
    const auto second = remote.create_local_file_or_throw(
        "b-empty.txt", 0U, empty_digest);
    const auto tombstone =
        remote.create_local_tombstone_or_throw("c-deleted.txt");
    const auto fourth = remote.create_local_file_or_throw(
        "d-empty.txt", 0U, empty_digest);
    require(
        fixture.replica.accept_remote_or_throw(first) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.replica.accept_remote_or_throw(second) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.replica.accept_remote_or_throw(tombstone) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.replica.accept_remote_or_throw(fourth) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.payload_store.put_payload_or_throw("").content_sha256 ==
                empty_digest,
        "remote count-frontier fixture did not retain its zero-byte and tombstone values");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "folder-pass remote-count-frontier catalog");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto limits = Fixture::pass_limits();
    limits.maximum_local_scan_segment_regular_files = 2U;
    limits.maximum_remote_apply_operations = 2U;

    const auto first_pass = scan->run_convergence_pass_or_throw(limits);
    require(
        first_pass.remote_applied_count == 2U &&
            first_pass.remote_apply_operation_count == 2U &&
            first_pass.remote_payload_snapshot_observation_count == 0U &&
            first_pass.remote_payload_snapshot_entry_count == 0U &&
            first_pass.remote_targeted_payload_access_count == 1U &&
            first_pass.remote_targeted_payload_probe_count == 2U &&
            first_pass.remote_targeted_payload_selection_count == 2U &&
            first_pass.remote_targeted_payload_selected_bytes == 0U &&
            first_pass.deferred_remote_payload_candidate_count == 0U &&
            first_pass.exact_remote_file_bytes == 0U &&
            first_pass.deferred_remote_apply_candidate_count == 1U &&
            first_pass.remote_inspected_path_count == 3U &&
            first_pass.remote_acknowledged_path_count == 2U &&
            first_pass.deferred_remote_inspection_path_count == 2U &&
            first_pass.remote_inspection_sweep_seen_path_count == 2U &&
            !first_pass.completed_remote_inspection_sweep &&
            !first_pass.remote_inspection_sweep_had_unresolved_paths &&
            first_pass.remote_apply_started_after_path.empty() &&
            first_pass.remote_apply_resume_after_path == "b-empty.txt" &&
            !first_pass.remote_apply_wrapped_projection &&
            first_pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    OperationCountFrontier &&
            fs::exists(fixture.shared_root / "a-empty.txt") &&
            fs::exists(fixture.shared_root / "b-empty.txt") &&
            !fs::exists(fixture.shared_root / "c-deleted.txt") &&
            !fs::exists(fixture.shared_root / "d-empty.txt") &&
            scan->snapshot_or_throw().entries.size() == 2U,
        "remote operation frontier did not bound a zero-byte candidate prefix");

    const auto second_pass = scan->run_convergence_pass_or_throw(limits);
    const auto completed_catalog = scan->snapshot_or_throw();
    const auto deleted_entry = find_entry(completed_catalog, "c-deleted.txt");
    require(
        second_pass.remote_applied_count == 1U &&
            second_pass.remote_adopted_exact_count == 1U &&
            second_pass.remote_apply_operation_count == 2U &&
            second_pass.exact_remote_file_bytes == 0U &&
            second_pass.deferred_remote_apply_candidate_count == 0U &&
            second_pass.remote_inspected_path_count == 4U &&
            second_pass.remote_acknowledged_path_count == 4U &&
            second_pass.deferred_remote_inspection_path_count == 0U &&
            second_pass.remote_inspection_sweep_seen_path_count == 4U &&
            second_pass.completed_remote_inspection_sweep &&
            !second_pass.remote_inspection_sweep_had_unresolved_paths &&
            second_pass.remote_apply_started_after_path == "b-empty.txt" &&
            second_pass.remote_apply_resume_after_path == "b-empty.txt" &&
            second_pass.remote_apply_wrapped_projection &&
            second_pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    EndOfProjection &&
            !fs::exists(fixture.shared_root / "c-deleted.txt") &&
            fs::exists(fixture.shared_root / "d-empty.txt") &&
            completed_catalog.entries.size() == 4U &&
            deleted_entry.has_value() &&
            deleted_entry->kind == anonsync::SyncReplicaValueKind::Tombstone &&
            deleted_entry->operation_id == tombstone.operation_id,
        "remote operation frontier did not advance zero-byte and tombstone suffix work");
}

void test_remote_inspection_frontier_rotates_safe_deferrals_across_restart() {
    Fixture fixture("anonsync-folder-pass-remote-inspection-frontier");
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id,
        {"device-folder-pass-inspection-frontier", 411U});
    std::vector<anonsync::SyncReplicaOperation> operations;
    for (const std::string path : {
             "a-missing.txt", "b-missing.txt", "c-missing.txt",
             "d-missing.txt", "e-ready-later.txt"}) {
        const std::string bytes = "remote bytes for " + path;
        operations.push_back(remote.create_local_file_or_throw(
            path, bytes.size(), anonsync::sha256_hex(bytes)));
        require(
            fixture.replica.accept_remote_or_throw(operations.back()) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "remote inspection-frontier fixture rejected remote evidence");
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "remote inspection-frontier catalog");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto limits = Fixture::pass_limits();
    limits.maximum_remote_inspection_paths = 2U;
    limits.maximum_remote_apply_operations = 1U;

    const auto first = scan->run_convergence_pass_or_throw(limits);
    const auto first_progress = scan->scan_progress_snapshot_or_throw();
    require(
        first.remote_apply_operation_count == 0U &&
            first.remote_inspected_path_count == 2U &&
            first.remote_acknowledged_path_count == 2U &&
            first.deferred_remote_inspection_path_count == 3U &&
            first.remote_inspection_sweep_seen_path_count == 2U &&
            !first.completed_remote_inspection_sweep &&
            first.remote_inspection_sweep_had_unresolved_paths &&
            first.deferred_remote_payload_candidate_count == 2U &&
            first.remote_apply_started_after_path.empty() &&
            first.remote_apply_resume_after_path == "b-missing.txt" &&
            !first.remote_apply_wrapped_projection &&
            first.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    InspectionPathFrontier &&
            first_progress.remote_apply_resume_after_path ==
                "b-missing.txt" &&
            !first_progress.remote_inspection_sweep_basis_digest.empty() &&
            first_progress
                .remote_inspection_sweep_started_after_path.empty() &&
            first_progress.remote_inspection_sweep_seen_path_count == 2U &&
            first_progress.remote_inspection_sweep_had_unresolved_paths,
        "remote inspection frontier did not durably acknowledge its first safe deferral segment");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto second = scan->run_convergence_pass_or_throw(limits);
    require(
        second.remote_apply_operation_count == 0U &&
            second.remote_inspected_path_count == 2U &&
            second.remote_acknowledged_path_count == 2U &&
            second.deferred_remote_inspection_path_count == 1U &&
            second.remote_inspection_sweep_seen_path_count == 4U &&
            !second.completed_remote_inspection_sweep &&
            second.remote_inspection_sweep_had_unresolved_paths &&
            second.deferred_remote_payload_candidate_count == 2U &&
            second.remote_apply_started_after_path == "b-missing.txt" &&
            second.remote_apply_resume_after_path == "d-missing.txt" &&
            !second.remote_apply_wrapped_projection &&
            second.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    InspectionPathFrontier,
        "remote inspection cursor did not survive restart and leave the unavailable prefix behind");

    const std::string ready_bytes = "remote bytes for e-ready-later.txt";
    require(
        fixture.payload_store.put_payload_or_throw(ready_bytes)
                .content_sha256 == operations.back().content_sha256,
        "remote inspection-frontier fixture did not retain the delayed payload");
    const auto third = scan->run_convergence_pass_or_throw(limits);
    require(
        third.remote_applied_count == 1U &&
            third.remote_apply_operation_count == 1U &&
            third.remote_inspected_path_count == 1U &&
            third.remote_acknowledged_path_count == 1U &&
            third.deferred_remote_inspection_path_count == 0U &&
            third.remote_inspection_sweep_seen_path_count == 5U &&
            third.completed_remote_inspection_sweep &&
            third.remote_inspection_sweep_had_unresolved_paths &&
            third.deferred_remote_payload_candidate_count == 0U &&
            third.remote_apply_started_after_path == "d-missing.txt" &&
            third.remote_apply_resume_after_path == "e-ready-later.txt" &&
            !third.remote_apply_wrapped_projection &&
            third.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    EndOfProjection &&
            read_file(fixture.shared_root / "e-ready-later.txt") ==
                ready_bytes &&
            !fs::exists(fixture.shared_root / "a-missing.txt"),
        "bounded remote inspection did not apply a newly ready path before rotating into the missing prefix");
}

void test_remote_inspection_sweep_settles_stable_projection_across_restart() {
    Fixture fixture("anonsync-folder-pass-remote-inspection-sweep");
    for (const std::string path : {
             "a.txt", "b.txt", "c.txt", "d.txt", "e.txt"}) {
        write_file(fixture.shared_root / path, "stable bytes for " + path);
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "remote inspection-sweep catalog");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto bootstrap = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        bootstrap.local_published_count == 5U &&
            bootstrap.completed_remote_inspection_sweep &&
            bootstrap.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    EndOfProjection,
        "remote inspection-sweep fixture did not establish a stable projection");

    auto limits = Fixture::pass_limits();
    limits.maximum_remote_inspection_paths = 2U;
    const auto first = scan->run_convergence_pass_or_throw(limits);
    const auto first_progress = scan->scan_progress_snapshot_or_throw();
    require(
        first.remote_apply_operation_count == 0U &&
            first.remote_inspected_path_count == 2U &&
            first.remote_acknowledged_path_count == 2U &&
            first.remote_inspection_sweep_seen_path_count == 2U &&
            first.deferred_remote_inspection_path_count == 3U &&
            !first.completed_remote_inspection_sweep &&
            !first.remote_inspection_sweep_had_unresolved_paths &&
            first.remote_apply_started_after_path == "e.txt" &&
            first.remote_apply_resume_after_path == "b.txt" &&
            first.remote_apply_wrapped_projection &&
            first.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    InspectionPathFrontier &&
            !first_progress.remote_inspection_sweep_basis_digest.empty() &&
            first_progress.remote_inspection_sweep_started_after_path ==
                "e.txt" &&
            first_progress.remote_inspection_sweep_seen_path_count == 2U &&
            !first_progress
                 .remote_inspection_sweep_had_unresolved_paths,
        "stable remote inspection sweep did not publish its first bounded segment");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto second = scan->run_convergence_pass_or_throw(limits);
    const auto second_progress = scan->scan_progress_snapshot_or_throw();
    require(
        second.remote_apply_operation_count == 0U &&
            second.remote_inspected_path_count == 2U &&
            second.remote_acknowledged_path_count == 2U &&
            second.remote_inspection_sweep_seen_path_count == 4U &&
            second.deferred_remote_inspection_path_count == 1U &&
            !second.completed_remote_inspection_sweep &&
            !second.remote_inspection_sweep_had_unresolved_paths &&
            second.remote_apply_started_after_path == "b.txt" &&
            second.remote_apply_resume_after_path == "d.txt" &&
            !second.remote_apply_wrapped_projection &&
            second.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    InspectionPathFrontier &&
            second_progress.remote_inspection_sweep_basis_digest ==
                first_progress.remote_inspection_sweep_basis_digest &&
            second_progress.remote_inspection_sweep_started_after_path ==
                "e.txt" &&
            second_progress.remote_inspection_sweep_seen_path_count == 4U,
        "stable remote inspection sweep did not resume after owner reconstruction");

    const auto third = scan->run_convergence_pass_or_throw(limits);
    const auto completed_progress = scan->scan_progress_snapshot_or_throw();
    require(
        third.remote_apply_operation_count == 0U &&
            third.remote_inspected_path_count == 1U &&
            third.remote_acknowledged_path_count == 1U &&
            third.remote_inspection_sweep_seen_path_count == 5U &&
            third.deferred_remote_inspection_path_count == 0U &&
            third.completed_remote_inspection_sweep &&
            !third.remote_inspection_sweep_had_unresolved_paths &&
            third.remote_apply_started_after_path == "d.txt" &&
            third.remote_apply_resume_after_path == "e.txt" &&
            !third.remote_apply_wrapped_projection &&
            third.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    EndOfProjection &&
            completed_progress.remote_apply_resume_after_path == "e.txt" &&
            completed_progress
                .remote_inspection_sweep_basis_digest.empty() &&
            completed_progress
                .remote_inspection_sweep_started_after_path.empty() &&
            completed_progress.remote_inspection_sweep_seen_path_count == 0U &&
            !completed_progress
                 .remote_inspection_sweep_had_unresolved_paths,
        "stable bounded remote inspection sweep did not settle after 2+2+1 paths");
}

void test_remote_apply_cursor_survives_restart_and_defeats_prefix_churn() {
    Fixture fixture("anonsync-folder-pass-remote-cyclic-cursor");
    const std::string base_bytes = "a base";
    const std::string first_successor_bytes = "a successor one";
    const std::string second_successor_bytes = "a successor two";
    const std::string suffix_bytes = "z suffix";
    write_file(fixture.shared_root / "a.txt", base_bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "remote cyclic-cursor catalog");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto base = scan->scan_regular_file_or_throw("a.txt");
    require(
        base.published_operation.has_value(),
        "remote cyclic-cursor fixture did not publish its local base");

    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-folder-pass-cyclic-cursor", 42U});
    require(
        remote.accept_remote_or_throw(*base.published_operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "remote cyclic-cursor fixture did not admit its common base");
    const auto first_successor = remote.create_local_file_or_throw(
        "a.txt", first_successor_bytes.size(),
        anonsync::sha256_hex(first_successor_bytes));
    const auto suffix = remote.create_local_file_or_throw(
        "z.txt", suffix_bytes.size(), anonsync::sha256_hex(suffix_bytes));
    require(
        fixture.replica.accept_remote_or_throw(first_successor) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.replica.accept_remote_or_throw(suffix) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.payload_store.put_payload_or_throw(first_successor_bytes)
                    .content_sha256 == first_successor.content_sha256 &&
            fixture.payload_store.put_payload_or_throw(suffix_bytes)
                    .content_sha256 == suffix.content_sha256,
        "remote cyclic-cursor fixture did not retain its first remote projection");

    auto limits = Fixture::pass_limits();
    limits.maximum_local_scan_segment_regular_files = 1U;
    limits.maximum_remote_apply_operations = 1U;

    const auto first_pass = scan->run_convergence_pass_or_throw(limits);
    const auto first_progress = scan->scan_progress_snapshot_or_throw();
    require(
        first_pass.remote_applied_count == 1U &&
            first_pass.remote_apply_operation_count == 1U &&
            first_pass.deferred_remote_apply_candidate_count == 1U &&
            first_pass.remote_apply_started_after_path.empty() &&
            first_pass.remote_apply_resume_after_path == "a.txt" &&
            !first_pass.remote_apply_wrapped_projection &&
            first_pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    OperationCountFrontier &&
            first_progress.remote_apply_resume_after_path == "a.txt" &&
            read_file(fixture.shared_root / "a.txt") ==
                first_successor_bytes &&
            !fs::exists(fixture.shared_root / "z.txt"),
        "first cyclic pass did not select and persist the early-path boundary");

    const auto second_successor = remote.create_local_file_or_throw(
        "a.txt", second_successor_bytes.size(),
        anonsync::sha256_hex(second_successor_bytes));
    require(
        fixture.replica.accept_remote_or_throw(second_successor) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.payload_store.put_payload_or_throw(second_successor_bytes)
                    .content_sha256 == second_successor.content_sha256,
        "remote cyclic-cursor fixture did not retain sustained prefix churn");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    require(
        scan->scan_progress_snapshot_or_throw()
                .remote_apply_resume_after_path == "a.txt",
        "remote apply cursor did not survive owner restart");

    const auto second_pass = scan->run_convergence_pass_or_throw(limits);
    require(
        second_pass.remote_applied_count == 1U &&
            second_pass.remote_apply_operation_count == 1U &&
            second_pass.deferred_remote_apply_candidate_count == 1U &&
            second_pass.remote_apply_started_after_path == "a.txt" &&
            second_pass.remote_apply_resume_after_path == "z.txt" &&
            second_pass.remote_apply_wrapped_projection &&
            second_pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    OperationCountFrontier &&
            read_file(fixture.shared_root / "a.txt") ==
                first_successor_bytes &&
            read_file(fixture.shared_root / "z.txt") == suffix_bytes,
        "sustained early-path churn starved the later remote path after restart");

    const auto third_pass = scan->run_convergence_pass_or_throw(limits);
    require(
        third_pass.remote_applied_count == 1U &&
            third_pass.remote_apply_operation_count == 1U &&
            third_pass.deferred_remote_apply_candidate_count == 0U &&
            third_pass.remote_apply_started_after_path == "z.txt" &&
            third_pass.remote_apply_resume_after_path == "z.txt" &&
            third_pass.remote_apply_wrapped_projection &&
            third_pass.remote_apply_stop_reason ==
                anonsync::SyncReplicaFolderRemoteApplyStopReason::
                    EndOfProjection &&
            read_file(fixture.shared_root / "a.txt") ==
                second_successor_bytes &&
            read_file(fixture.shared_root / "z.txt") == suffix_bytes,
        "cyclic cursor did not wrap and settle the continuously changing prefix");
}

void test_catalog_predecessor_reproof_decouples_remote_apply_from_scan_cursor() {
    {
        Fixture fixture("anonsync-folder-pass-catalog-reproof-restart");
        const std::string base_bytes = "a base";
        const std::string successor_bytes = "a remote successor";
        write_file(fixture.shared_root / "a.txt", base_bytes);
        write_file(fixture.shared_root / "b.txt", "b base");
        write_file(fixture.shared_root / "c.txt", "c base");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog reproof restart catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto a_base = scan->scan_regular_file_or_throw("a.txt");
        const auto b_base = scan->scan_regular_file_or_throw("b.txt");
        const auto c_base = scan->scan_regular_file_or_throw("c.txt");
        require(
            a_base.published_operation.has_value() &&
                b_base.published_operation.has_value() &&
                c_base.published_operation.has_value(),
            "catalog reproof restart fixture did not publish its local bases");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id,
            {"device-folder-pass-catalog-reproof-restart", 43U});
        require(
            remote.accept_remote_or_throw(*a_base.published_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "catalog reproof restart fixture did not admit its common base");
        const auto successor = remote.create_local_file_or_throw(
            "a.txt", successor_bytes.size(),
            anonsync::sha256_hex(successor_bytes));
        require(
            fixture.replica.accept_remote_or_throw(successor) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "catalog reproof restart fixture did not retain its remote successor");

        auto limits = Fixture::pass_limits();
        limits.maximum_local_scan_segment_regular_files = 1U;
        limits.maximum_remote_apply_operations = 1U;

        const auto first_pass = scan->run_convergence_pass_or_throw(limits);
        const auto first_progress = scan->scan_progress_snapshot_or_throw();
        require(
            !first_pass.completed_local_scan_epoch &&
                first_pass.local_scan_seen_path_count == 1U &&
                first_pass.local_scan_resume_after_path == "a.txt" &&
                first_pass.remote_apply_operation_count == 0U &&
                first_pass.deferred_remote_payload_candidate_count == 1U &&
                first_pass.remote_payload_snapshot_observation_count == 1U &&
                first_progress.seen_path_count == 1U &&
                first_progress.resume_after_path == "a.txt" &&
                read_file(fixture.shared_root / "a.txt") == base_bytes,
            "missing payload did not leave the exact predecessor behind a durable scan cursor");

        scan.reset();
        require(
            fixture.payload_store.put_payload_or_throw(successor_bytes)
                    .content_sha256 == successor.content_sha256,
            "catalog reproof restart fixture did not retain the delayed payload");
        scan = fixture.make_scan_owner(catalog_db);
        require(
            scan->scan_progress_snapshot_or_throw().resume_after_path ==
                "a.txt",
            "catalog reproof scan cursor did not survive owner restart");

        const auto second_pass = scan->run_convergence_pass_or_throw(limits);
        const auto second_progress = scan->scan_progress_snapshot_or_throw();
        require(
            !second_pass.completed_local_scan_epoch &&
                second_pass.local_scan_seen_path_count == 2U &&
                second_pass.local_scan_resume_after_path == "b.txt" &&
                second_pass.remote_applied_count == 1U &&
                second_pass.remote_apply_operation_count == 1U &&
                second_pass
                        .remote_apply_revalidated_catalog_predecessor_count ==
                    1U &&
                second_pass.deferred_remote_payload_candidate_count == 0U &&
                second_pass.remote_apply_resume_after_path == "c.txt" &&
                second_progress.seen_path_count == 2U &&
                second_progress.resume_after_path == "b.txt" &&
                read_file(fixture.shared_root / "a.txt") == successor_bytes,
            "restart waited for a whole scan-epoch wrap before applying the cataloged predecessor");
    }

    {
        Fixture fixture("anonsync-folder-pass-completed-epoch-catalog-reproof");
        const std::string successor_bytes = "late remote successor";
        write_file(fixture.shared_root / "a.txt", "a base");
        write_file(fixture.shared_root / "b.txt", "b base");
        write_file(fixture.shared_root / "c.txt", "c base");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "completed-epoch catalog reproof catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto c_base = scan->scan_regular_file_or_throw("c.txt");
        (void)scan->scan_regular_file_or_throw("a.txt");
        (void)scan->scan_regular_file_or_throw("b.txt");
        require(
            c_base.published_operation.has_value(),
            "completed-epoch catalog reproof fixture lost its base operation");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id,
            {"device-folder-pass-completed-epoch-reproof", 431U});
        require(
            remote.accept_remote_or_throw(*c_base.published_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "completed-epoch catalog reproof fixture rejected its common base");
        const auto successor = remote.create_local_file_or_throw(
            "c.txt", successor_bytes.size(),
            anonsync::sha256_hex(successor_bytes));
        require(
            fixture.replica.accept_remote_or_throw(successor) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "completed-epoch catalog reproof fixture rejected its successor");

        auto completion_limits = Fixture::pass_limits();
        completion_limits.maximum_local_scan_segment_regular_files = 4U;
        completion_limits.maximum_remote_apply_operations = 1U;
        const std::uint64_t epoch_before =
            scan->scan_progress_snapshot_or_throw().scan_epoch;
        const auto completed =
            scan->run_convergence_pass_or_throw(completion_limits);
        const auto reset_progress = scan->scan_progress_snapshot_or_throw();
        require(
            completed.completed_local_scan_epoch &&
                completed.local_scan_seen_path_count == 0U &&
                completed.local_scan_resume_after_path.empty() &&
                completed.remote_apply_operation_count == 0U &&
                completed.deferred_remote_payload_candidate_count == 1U &&
                reset_progress.scan_epoch != epoch_before &&
                reset_progress.seen_path_count == 0U &&
                reset_progress.resume_after_path.empty(),
            "completed scan epoch did not reset before delayed remote payload arrival");

        scan.reset();
        require(
            fixture.payload_store.put_payload_or_throw(successor_bytes)
                    .content_sha256 == successor.content_sha256,
            "completed-epoch catalog reproof fixture lost its delayed payload");
        scan = fixture.make_scan_owner(catalog_db);
        auto restart_limits = Fixture::pass_limits();
        restart_limits.maximum_local_scan_segment_regular_files = 1U;
        restart_limits.maximum_remote_apply_operations = 1U;
        const auto restarted =
            scan->run_convergence_pass_or_throw(restart_limits);
        require(
            !restarted.completed_local_scan_epoch &&
                restarted.local_scan_seen_path_count == 1U &&
                restarted.local_scan_resume_after_path == "a.txt" &&
                restarted.remote_applied_count == 1U &&
                restarted.remote_apply_operation_count == 1U &&
                restarted.remote_apply_revalidated_catalog_predecessor_count ==
                    1U &&
                restarted.deferred_remote_payload_candidate_count == 0U &&
                restarted.remote_apply_resume_after_path == "c.txt" &&
                read_file(fixture.shared_root / "c.txt") == successor_bytes,
            "completed scan-epoch reset stranded a cataloged predecessor behind the new scan cursor");
    }

    {
        Fixture fixture("anonsync-folder-pass-catalog-metadata-is-not-authority");
        const std::string base_bytes = "a base";
        const std::string successor_bytes = "a remote successor";
        const std::string local_edit = "independent local edit";
        write_file(fixture.shared_root / "a.txt", base_bytes);
        write_file(fixture.shared_root / "b.txt", "b base");
        write_file(fixture.shared_root / "c.txt", "c base");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog metadata non-authority catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto a_base = scan->scan_regular_file_or_throw("a.txt");
        (void)scan->scan_regular_file_or_throw("b.txt");
        (void)scan->scan_regular_file_or_throw("c.txt");
        require(
            a_base.published_operation.has_value(),
            "catalog metadata non-authority fixture did not publish its local base");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id,
            {"device-folder-pass-catalog-nonauthority", 44U});
        require(
            remote.accept_remote_or_throw(*a_base.published_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "catalog metadata non-authority fixture did not admit its common base");
        const auto successor = remote.create_local_file_or_throw(
            "a.txt", successor_bytes.size(),
            anonsync::sha256_hex(successor_bytes));
        require(
            fixture.replica.accept_remote_or_throw(successor) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "catalog metadata non-authority fixture did not retain its remote successor");

        auto limits = Fixture::pass_limits();
        limits.maximum_local_scan_segment_regular_files = 1U;
        limits.maximum_remote_apply_operations = 1U;
        const auto first_pass = scan->run_convergence_pass_or_throw(limits);
        require(
            first_pass.local_scan_resume_after_path == "a.txt" &&
                first_pass.deferred_remote_payload_candidate_count == 1U,
            "catalog metadata non-authority fixture did not retain its first-pass nomination");

        scan.reset();
        write_file(fixture.shared_root / "a.txt", local_edit);
        require(
            fixture.payload_store.put_payload_or_throw(successor_bytes)
                    .content_sha256 == successor.content_sha256,
            "catalog metadata non-authority fixture did not retain the delayed payload");
        scan = fixture.make_scan_owner(catalog_db);
        const auto second_pass = scan->run_convergence_pass_or_throw(limits);
        require(
            second_pass.local_scan_resume_after_path == "b.txt" &&
                second_pass.remote_apply_operation_count == 0U &&
                second_pass
                        .remote_apply_revalidated_catalog_predecessor_count ==
                    0U &&
                second_pass.skipped_conflicted_remote_path_count == 1U &&
                read_file(fixture.shared_root / "a.txt") == local_edit,
            "catalog metadata reproof authorized stale remote publication after a local edit");
    }
}

void test_bounded_whole_folder_pass_limit_contract() {
    Fixture fixture("anonsync-folder-pass-limit-contract");
    auto owner_limits = Fixture::scan_limits();
    owner_limits.max_catalog_path_bytes = 16U;
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "folder-pass limit-contract catalog database");
    anonsync::SyncReplicaFolderScanOwner scan(
        catalog_db.db, Fixture::folder_id, fixture.shared_root, fixture.replica,
        fixture.payload_store, owner_limits, "folder-pass limit-contract owner");
    auto pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes = 17U;
    const auto catalog_cutpoint = scan.snapshot_or_throw();
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "relative-path limit exceeds the catalog byte budget",
        "composed pass accepted a path limit its catalog owner cannot represent");
    require(
        scan.snapshot_or_throw() == catalog_cutpoint,
        "invalid composed limits touched the catalog before failing");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_file_bytes = 9U;
    pass_limits.maximum_total_file_bytes = 8U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "file-byte limit exceeds its aggregate byte limit",
        "composed pass admitted a file that no empty fair segment can fit");
    require(
        scan.snapshot_or_throw() == catalog_cutpoint,
        "invalid file/aggregate byte composition touched the catalog");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_local_scan_segment_regular_files = 0U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "maximum regular files must be in",
        "composed pass accepted a zero local scan path frontier");
    require(
        scan.snapshot_or_throw() == catalog_cutpoint,
        "invalid local scan segment limit touched the catalog");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_regular_files = 2U;
    pass_limits.maximum_local_scan_segment_regular_files = 3U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "local scan segment regular-file limit exceeds the whole-folder regular-file limit",
        "composed pass accepted a segment frontier larger than its total file capacity");
    require(
        scan.snapshot_or_throw() == catalog_cutpoint,
        "invalid segment/whole-folder composition touched the catalog");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_remote_apply_operations = 0U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "remote-apply operation limit is invalid",
        "composed pass accepted a zero remote-apply operation frontier");
    require(
        scan.snapshot_or_throw() == catalog_cutpoint,
        "invalid remote-apply operation limit touched the catalog");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_remote_inspection_paths = 0U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "remote-inspection path limit is invalid",
        "composed pass accepted a zero remote-inspection frontier");
    require(
        scan.snapshot_or_throw() == catalog_cutpoint,
        "invalid remote-inspection path limit touched the catalog");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_regular_files = 3U;
    pass_limits.maximum_local_scan_segment_regular_files = 3U;
    pass_limits.maximum_remote_apply_operations = 2U;
    const auto independently_bounded =
        scan.run_convergence_pass_or_throw(pass_limits);
    require(
        independently_bounded.used_idle_fast_path &&
            independently_bounded.remote_apply_operation_count == 0U &&
            scan.snapshot_or_throw() == catalog_cutpoint,
        "independent local-scan and cyclic remote-apply frontiers were not accepted");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_payload_batch_puts = 0U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "payload-batch put limit is invalid",
        "composed pass accepted a zero payload mutation put frontier");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_payload_batch_work_bytes = 0U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "payload-batch work-byte limit is invalid",
        "composed pass accepted a zero payload mutation work frontier");
    require(
        scan.snapshot_or_throw() == catalog_cutpoint,
        "invalid payload mutation segment limits touched the catalog");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_entries = owner_limits.max_catalog_entries + 1U;
    const auto wider_namespace =
        scan.run_convergence_pass_or_throw(pass_limits);
    require(
        wider_namespace.completed_local_scan_epoch &&
            wider_namespace.traversal.visited_entry_count == 0U &&
            scan.snapshot_or_throw() == catalog_cutpoint,
        "namespace-entry work capacity remained incorrectly coupled to catalog row capacity");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_regular_files =
        owner_limits.max_catalog_entries + 1U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "regular-file limit exceeds the retained catalog capacity",
        "composed pass accepted more local regular files than its catalog can retain");

    pass_limits = Fixture::pass_limits();
    pass_limits.maximum_relative_path_bytes =
        owner_limits.max_catalog_path_bytes;
    pass_limits.maximum_remote_paths = owner_limits.max_catalog_entries + 1U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(pass_limits); },
        "remote-path limit exceeds the retained catalog capacity",
        "composed pass accepted more remote paths than its catalog can retain");

    auto narrow_payload_limits = Fixture::payload_limits();
    narrow_payload_limits.max_entries = 64U;
    anonsync::SyncReplicaFilePayloadStore narrow_payload_store(
        Fixture::folder_id,
        fixture.temporary.make_directory("narrow-payload"),
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        narrow_payload_limits,
        "folder-pass narrow payload store");
    anonsync::SyncSqliteDb narrow_catalog_db = open_database(
        fixture.temporary.path() / "narrow-catalog.sqlite3",
        "folder-pass narrow-payload catalog database");
    anonsync::SyncReplicaFolderScanOwner narrow_scan(
        narrow_catalog_db.db, Fixture::folder_id, fixture.shared_root,
        fixture.replica, narrow_payload_store, Fixture::scan_limits(),
        "folder-pass narrow-payload owner");
    require_error(
        [&] {
            (void)narrow_scan.run_convergence_pass_or_throw(
                Fixture::pass_limits());
        },
        "regular-file limit exceeds the retained payload-store capacity",
        "composed pass accepted more current regular files than its payload store can retain");
    require(
        narrow_scan.snapshot_or_throw().entries.empty(),
        "invalid payload-store composition touched the catalog before failing");
}

void test_namespace_entries_do_not_consume_file_capacity() {
    Fixture fixture("anonsync-folder-pass-independent-entry-capacity");
    fs::create_directory(fixture.shared_root / "nested");
    write_file(fixture.shared_root / "nested" / "a.txt", "alpha");
    write_file(fixture.shared_root / "b.txt", "beta");

    auto payload_limits = Fixture::payload_limits();
    payload_limits.max_entries = 2U;
    anonsync::SyncReplicaFilePayloadStore payload_store(
        Fixture::folder_id,
        fixture.temporary.make_directory("two-file-payload"),
        anonsync::SyncReplicaFilePayloadStoreOpenDisposition::CreateIfMissing,
        payload_limits, "independent entry-capacity payload store");

    auto owner_limits = Fixture::scan_limits();
    owner_limits.max_catalog_entries = 2U;
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.temporary.path() / "two-file-catalog.sqlite3",
        "independent entry-capacity catalog database");
    anonsync::SyncReplicaFolderScanOwner scan(
        catalog_db.db, Fixture::folder_id, fixture.shared_root,
        fixture.replica, payload_store, owner_limits,
        "independent entry-capacity owner");

    auto limits = Fixture::pass_limits();
    limits.maximum_entries = 3U;
    limits.maximum_regular_files = 2U;
    limits.maximum_remote_paths = 2U;
    limits.maximum_local_scan_segment_regular_files = 2U;
    const auto report = scan.run_convergence_pass_or_throw(limits);
    const auto catalog = scan.snapshot_or_throw();
    require(
        report.completed_local_scan_epoch &&
            report.traversal.visited_entry_count == 3U &&
            report.traversal.visited_directory_count == 1U &&
            report.traversal.regular_file_count == 2U &&
            report.local_published_count == 2U &&
            catalog.entries.size() == 2U &&
            payload_store.snapshot_or_throw().entry_count() == 2U,
        "one directory consumed durable file capacity or blocked two admissible files");

    limits.maximum_entries = 2U;
    require_error(
        [&] { (void)scan.run_convergence_pass_or_throw(limits); },
        "entry limit",
        "independent namespace budget stopped accounting for directories");
    require(
        scan.snapshot_or_throw() == catalog,
        "namespace-work refusal changed the already converged catalog");
}

void test_publish_noop_restart_and_modify() {
    Fixture fixture("anonsync-folder-scan-lifecycle");
    const std::string path = "docs/note.txt";
    const std::string first_bytes = "first local content";
    const std::string second_bytes = "second local content";
    write_file(fixture.shared_root / path, first_bytes);

    std::string first_operation_id;
    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog lifecycle database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto first = scan->scan_regular_file_or_throw(path);
        first_operation_id = first.entry.operation_id;
        require(
            first.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::Published &&
                first.published_operation.has_value() &&
                first.entry.content_sha256 == anonsync::sha256_hex(first_bytes) &&
                first.entry.size_bytes == first_bytes.size(),
            "first stable scan did not publish and map the exact file");

        const auto replica_after_first = fixture.replica.snapshot_or_throw();
        require(
            replica_after_first.durable.operations.size() == 1U &&
                replica_after_first.durable.last_local_counter == 1U &&
                replica_after_first.outbox.empty(),
            "first folder publication did not stay share-global and singular");
        const auto payload_after_first =
            fixture.payload_store.snapshot_or_throw();
        require(
            payload_after_first.entry_count() == 1U &&
                payload_after_first.payload_size_or_none(
                    first.entry.content_sha256) == first_bytes.size(),
            "first folder publication did not retain exact payload bytes");

        const auto catalog_after_first = scan->snapshot_or_throw();
        const auto payload_cutpoint = fixture.payload_store.snapshot_or_throw();
        const auto duplicate = scan->scan_regular_file_or_throw(path);
        require(
            duplicate.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::CatalogNoOp &&
                !duplicate.published_operation.has_value() &&
                duplicate.entry.operation_id == first_operation_id,
            "duplicate watcher hint did not reuse the catalog mapping");
        const auto replica_after_duplicate = fixture.replica.snapshot_or_throw();
        require(
            replica_after_duplicate.durable.operations.size() == 1U &&
                replica_after_duplicate.durable.last_local_counter == 1U &&
                replica_after_duplicate.outbox.empty(),
            "duplicate watcher hint republished evidence or scheduled a peer");
        require(
            scan->snapshot_or_throw() == catalog_after_first &&
                fixture.payload_store.snapshot_or_throw().snapshot_digest() ==
                    payload_cutpoint.snapshot_digest(),
            "CatalogNoOp advanced durable catalog or payload-store state");
    }

    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog restart database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto catalog_before_restart_hint = scan->snapshot_or_throw();
        const auto restarted = scan->scan_regular_file_or_throw(path);
        require(
            restarted.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::CatalogNoOp &&
                restarted.entry.operation_id == first_operation_id &&
                scan->snapshot_or_throw() == catalog_before_restart_hint,
            "restart did not restore one generation-stable publication mapping");

        struct stat before_mode {};
        if (::stat((fixture.shared_root / path).c_str(), &before_mode) != 0) {
            fail("could not stat metadata-refresh fixture");
        }
        const mode_t changed_mode =
            static_cast<mode_t>((before_mode.st_mode & 0777U) ^ S_IXUSR);
        if (::chmod((fixture.shared_root / path).c_str(), changed_mode) != 0) {
            fail("could not change metadata-refresh fixture mode");
        }
        const auto replica_before_refresh = fixture.replica.snapshot_or_throw();
        const auto refreshed = scan->scan_regular_file_or_throw(path);
        const auto catalog_after_refresh = scan->snapshot_or_throw();
        require(
            refreshed.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::CatalogRefreshed &&
                refreshed.entry.operation_id == first_operation_id &&
                !refreshed.published_operation.has_value() &&
                catalog_after_refresh.state_generation ==
                    catalog_before_restart_hint.state_generation + 1U &&
                refreshed.entry.source_snapshot_sha256 !=
                    find_entry(catalog_before_restart_hint, path)
                        ->source_snapshot_sha256,
            "metadata-only change was mislabeled as a durable no-op");
        require(
            fixture.replica.snapshot_or_throw() == replica_before_refresh,
            "metadata-only catalog refresh republished file evidence");

        write_file(fixture.shared_root / path, second_bytes);
        const auto modified = scan->scan_regular_file_or_throw(path);
        require(
            modified.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::Published &&
                modified.published_operation.has_value() &&
                modified.entry.operation_id != first_operation_id &&
                modified.entry.content_sha256 ==
                    anonsync::sha256_hex(second_bytes),
            "manual repair scan did not publish the missed file modification");
        require(
            modified.published_operation->predecessor_operation_ids ==
                std::vector<std::string>{first_operation_id},
            "modified file publication did not preserve its exact predecessor");
        const auto replica_after_modify = fixture.replica.snapshot_or_throw();
        require(
            replica_after_modify.durable.operations.size() == 2U &&
                replica_after_modify.durable.last_local_counter == 2U &&
                replica_after_modify.outbox.empty(),
            "modified file scan did not remain one destination-free publication");
    }
}


void test_identity_preserving_regular_file_rename_is_atomic_and_restart_stable() {
    Fixture fixture("anonsync-folder-scan-identity-rename");
    const std::string source_path = "incoming/source.bin";
    const std::string destination_path = "library/renamed.bin";
    const std::string bytes = "one immutable payload across a rooted rename";
    write_file(fixture.shared_root / source_path, bytes);

    std::string source_file_operation_id;
    anonsync::SyncReplicaIdentityPreservingRename identity;
    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "identity-rename catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto source = scan->scan_regular_file_or_throw(source_path);
        source_file_operation_id = source.entry.operation_id;
        require(
            source.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::Published &&
                source.published_operation.has_value() &&
                !source.published_identity_preserving_rename.has_value() &&
                !source.targeted_payload_reuse,
            "identity-rename fixture did not publish its source file through ordinary payload admission");

        fs::create_directories(
            (fixture.shared_root / destination_path).parent_path());
        fs::rename(
            fixture.shared_root / source_path,
            fixture.shared_root / destination_path);

        const auto renamed =
            scan->scan_regular_file_or_throw(destination_path);
        require(
            renamed.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::Published &&
                renamed.published_operation.has_value() &&
                renamed.published_identity_preserving_rename.has_value() &&
                renamed.targeted_payload_reuse,
            "rooted destination observation did not publish one causal rename pair through exact retained-payload reuse");
        identity = *renamed.published_identity_preserving_rename;
        require(
            identity.source_canonical_path == source_path &&
                identity.destination_canonical_path == destination_path &&
                identity.source_file_operation_id ==
                    source_file_operation_id &&
                identity.destination_file_operation_id ==
                    renamed.entry.operation_id &&
                identity.destination_file_operation_id ==
                    renamed.published_operation->operation_id &&
                identity.size_bytes == bytes.size() &&
                identity.content_sha256 == anonsync::sha256_hex(bytes),
            "causal rename result did not bind the exact source, destination, and content");

        const auto catalog = scan->snapshot_or_throw();
        const auto source_entry = find_entry(catalog, source_path);
        const auto destination_entry = find_entry(catalog, destination_path);
        require(
            source_entry.has_value() && destination_entry.has_value() &&
                source_entry->kind ==
                    anonsync::SyncReplicaValueKind::Tombstone &&
                source_entry->operation_id ==
                    identity.source_tombstone_operation_id &&
                source_entry->size_bytes == 0U &&
                source_entry->content_sha256.empty() &&
                destination_entry->kind ==
                    anonsync::SyncReplicaValueKind::File &&
                destination_entry->operation_id ==
                    identity.destination_file_operation_id &&
                destination_entry->content_sha256 == identity.content_sha256 &&
                source_entry->last_seen_generation ==
                    destination_entry->last_seen_generation &&
                catalog.state_generation ==
                    destination_entry->last_seen_generation,
            "catalog did not commit the source tombstone and destination file as one generation");

        const auto replica = fixture.replica.snapshot_or_throw();
        const auto model = restore_model(replica);
        require(
            replica.durable.operations.size() == 3U &&
                replica.durable.last_local_counter == 3U &&
                model.identity_preserving_rename_for_source_tombstone(
                    identity.source_tombstone_operation_id) ==
                    std::optional<
                        anonsync::SyncReplicaIdentityPreservingRename>{
                        identity},
            "replica did not retain the exact three-operation causal rename history");
        require(
            fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
            "identity-preserving rename duplicated immutable payload storage");
    }

    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "identity-rename restart catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto replica_before = fixture.replica.snapshot_or_throw();
        const auto catalog_before = scan->snapshot_or_throw();
        const auto restarted =
            scan->scan_regular_file_or_throw(destination_path);
        require(
            restarted.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::CatalogNoOp &&
                restarted.entry.operation_id ==
                    identity.destination_file_operation_id &&
                !restarted.published_operation.has_value() &&
                !restarted.published_identity_preserving_rename.has_value() &&
                restarted.targeted_payload_reuse &&
                fixture.replica.snapshot_or_throw() == replica_before &&
                scan->snapshot_or_throw() == catalog_before,
            "restart republished or forgot the committed causal rename pair");
    }
}


void test_identity_preserving_rename_replica_pair_survives_catalog_crash_window() {
    Fixture fixture("anonsync-folder-scan-rename-catalog-crash");
    const std::string source_path = "staging/original.bin";
    const std::string destination_path = "library/final.bin";
    const std::string bytes = "one payload retained across replica-first recovery";
    write_file(fixture.shared_root / source_path, bytes);

    std::string source_file_operation_id;
    anonsync::SyncReplicaSqliteLocalRenamePublicationResult publication;
    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "rename crash-window prepare catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto source = scan->scan_regular_file_or_throw(source_path);
        source_file_operation_id = source.entry.operation_id;
        require(
            source.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::Published &&
                fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
            "rename crash-window fixture did not publish one source payload");

        fs::create_directories(
            (fixture.shared_root / destination_path).parent_path());
        fs::rename(
            fixture.shared_root / source_path,
            fixture.shared_root / destination_path);

        const auto before_replica = fixture.replica.snapshot_or_throw();
        publication = fixture.replica.
            publish_local_identity_preserving_rename_from_observed_heads_or_throw(
                source_path,
                std::vector<std::string>{source_file_operation_id},
                destination_path, std::vector<std::string>{}, bytes.size(),
                anonsync::sha256_hex(bytes));
        const auto after_replica = fixture.replica.snapshot_or_throw();
        const auto stale_catalog = scan->snapshot_or_throw();
        require(
            after_replica.state_generation ==
                    before_replica.state_generation + 1U &&
                after_replica.durable.operations.size() ==
                    before_replica.durable.operations.size() + 2U &&
                find_entry(stale_catalog, source_path).has_value() &&
                find_entry(stale_catalog, source_path)->kind ==
                    anonsync::SyncReplicaValueKind::File &&
                !find_entry(stale_catalog, destination_path).has_value(),
            "rename crash-window fixture did not stop after the atomic replica pair");
        // Deliberately abandon the scanner before the two-path catalog commit.
    }

    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "rename crash-window recovery catalog");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto recovered = scan->run_convergence_pass_or_throw(
            Fixture::pass_limits());
        const auto catalog = scan->snapshot_or_throw();
        const auto source = find_entry(catalog, source_path);
        const auto destination = find_entry(catalog, destination_path);
        require(
            recovered.completed_local_scan_epoch &&
                recovered.local_published_count == 0U &&
                recovered.local_identity_preserving_rename_count == 0U &&
                recovered.local_adopted_visible_count >= 1U &&
                source.has_value() && destination.has_value() &&
                source->kind == anonsync::SyncReplicaValueKind::Tombstone &&
                source->operation_id ==
                    publication.source_tombstone_operation.operation_id &&
                destination->kind == anonsync::SyncReplicaValueKind::File &&
                destination->operation_id ==
                    publication.destination_file_operation.operation_id &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint &&
                fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
            "restart did not adopt the replica-first rename pair without republishing or duplicating payload bytes");
    }
}

void test_convergence_pass_reports_one_identity_preserving_rename() {
    Fixture fixture("anonsync-folder-pass-identity-rename");
    const std::string source_path = "camera/clip.dat";
    const std::string destination_path = "archive/2026/clip.dat";
    const std::string bytes = "same bytes, new rooted name";
    write_file(fixture.shared_root / source_path, bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "identity-rename pass catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto source = scan->scan_regular_file_or_throw(source_path);
    require(
        source.disposition ==
            anonsync::SyncReplicaFolderScanDisposition::Published,
        "identity-rename pass fixture did not publish its source");

    fs::create_directories(
        (fixture.shared_root / destination_path).parent_path());
    fs::rename(
        fixture.shared_root / source_path,
        fixture.shared_root / destination_path);

    const auto report =
        scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto catalog = scan->snapshot_or_throw();
    const auto source_entry = find_entry(catalog, source_path);
    const auto destination_entry = find_entry(catalog, destination_path);
    require(
        report.completed_local_scan_epoch &&
            report.local_published_count == 1U &&
            report.local_identity_preserving_rename_count == 1U &&
            report.traversal.regular_file_count == 1U &&
            source_entry.has_value() && destination_entry.has_value() &&
            source_entry->kind ==
                anonsync::SyncReplicaValueKind::Tombstone &&
            destination_entry->kind ==
                anonsync::SyncReplicaValueKind::File &&
            source_entry->last_seen_generation ==
                destination_entry->last_seen_generation &&
            fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
        "bounded convergence did not account for one atomic causal rename without duplicating payload bytes");

    const auto replica_after = fixture.replica.snapshot_or_throw();
    const auto catalog_after = scan->snapshot_or_throw();
    const auto settled =
        scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    require(
        settled.local_identity_preserving_rename_count == 0U &&
            settled.local_published_count == 0U &&
            fixture.replica.snapshot_or_throw() == replica_after &&
            scan->snapshot_or_throw() == catalog_after,
        "settled convergence republished the already committed causal rename");
}


void test_present_same_content_duplicate_falls_back_before_rename_publication() {
    Fixture fixture("anonsync-folder-scan-present-duplicate-rename");
    const std::string source_path = "source/moved.bin";
    const std::string duplicate_path = "source/still-present-copy.bin";
    const std::string destination_path = "destination/moved.bin";
    const std::string bytes = "one content identity under two visible names";
    write_file(fixture.shared_root / source_path, bytes);
    write_file(fixture.shared_root / duplicate_path, bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "present-duplicate rename catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto source = scan->scan_regular_file_or_throw(source_path);
    const auto duplicate = scan->scan_regular_file_or_throw(duplicate_path);
    require(
        source.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::Published &&
            duplicate.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::Published &&
            fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
        "present-duplicate fixture did not establish two visible names over one payload");

    fs::create_directories(
        (fixture.shared_root / destination_path).parent_path());
    fs::rename(
        fixture.shared_root / source_path,
        fixture.shared_root / destination_path);

    const auto published =
        scan->scan_regular_file_or_throw(destination_path);
    const auto replica = fixture.replica.snapshot_or_throw();
    const auto catalog = scan->snapshot_or_throw();
    require(
        published.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::Published &&
            published.published_operation.has_value() &&
            !published.published_identity_preserving_rename.has_value() &&
            replica.durable.operations.size() == 3U &&
            replica.durable.last_local_counter == 3U &&
            find_entry(catalog, source_path)->kind ==
                anonsync::SyncReplicaValueKind::File &&
            find_entry(catalog, duplicate_path)->kind ==
                anonsync::SyncReplicaValueKind::File &&
            find_entry(catalog, destination_path)->kind ==
                anonsync::SyncReplicaValueKind::File &&
            fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
        "still-present same-content duplicate reached rename publication instead of ordinary create fallback");
}

void test_ambiguous_same_content_absence_does_not_invent_rename_identity() {
    Fixture fixture("anonsync-folder-scan-ambiguous-rename");
    const std::string first_source = "duplicates/first.bin";
    const std::string second_source = "duplicates/second.bin";
    const std::string destination = "selected/result.bin";
    const std::string bytes = "same content retained under two prior names";
    write_file(fixture.shared_root / first_source, bytes);
    write_file(fixture.shared_root / second_source, bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "ambiguous-rename catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto first = scan->scan_regular_file_or_throw(first_source);
    const auto second = scan->scan_regular_file_or_throw(second_source);
    require(
        first.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::Published &&
            second.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::Published &&
            fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
        "ambiguous-rename fixture did not establish two names over one payload");

    fs::remove(fixture.shared_root / first_source);
    fs::create_directories((fixture.shared_root / destination).parent_path());
    fs::rename(
        fixture.shared_root / second_source,
        fixture.shared_root / destination);

    const auto published = scan->scan_regular_file_or_throw(destination);
    const auto replica = fixture.replica.snapshot_or_throw();
    require(
        published.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::Published &&
            published.published_operation.has_value() &&
            !published.published_identity_preserving_rename.has_value() &&
            replica.durable.operations.size() == 3U &&
            replica.durable.last_local_counter == 3U &&
            fixture.payload_store.snapshot_or_throw().entry_count() == 1U,
        "two absent exact-content predecessors were misclassified as one identity-preserving rename");

    const auto catalog = scan->snapshot_or_throw();
    require(
        find_entry(catalog, first_source)->kind ==
                anonsync::SyncReplicaValueKind::File &&
            find_entry(catalog, second_source)->kind ==
                anonsync::SyncReplicaValueKind::File &&
            find_entry(catalog, destination)->kind ==
                anonsync::SyncReplicaValueKind::File,
        "ambiguous rename fallback mutated a source identity before complete-scan absence proof");
}

void test_database_head_race_rejects_without_scanner_mutation() {
    Fixture fixture("anonsync-folder-scan-head-race");
    const std::string path = "race.txt";
    const std::string local_bytes = "locally observed bytes";
    write_file(fixture.shared_root / path, local_bytes);

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "catalog head-race database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto prepared = scan->prepare_regular_file_or_throw(path);
    require(
        prepared.observed_visible_operation_ids().empty() &&
            prepared.content_sha256() == anonsync::sha256_hex(local_bytes),
        "prepared observation did not bind the empty pre-hash path frontier");

    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-scan-remote", 1U});
    const std::string remote_bytes = "remote bytes won the race";
    const auto remote_operation = remote.create_local_file_or_throw(
        path, remote_bytes.size(), anonsync::sha256_hex(remote_bytes));
    require(
        fixture.replica.accept_remote_or_throw(remote_operation) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "head-race fixture did not admit the competing remote operation");

    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    const auto payload_cutpoint = fixture.payload_store.snapshot_or_throw();
    require_error(
        [&] {
            (void)scan->commit_prepared_regular_file_or_throw(
                std::move(prepared));
        },
        "replica path heads changed",
        "stale prepared bytes were published as a successor of a new head");
    require(
        fixture.replica.snapshot_or_throw() == replica_cutpoint &&
            scan->snapshot_or_throw() == catalog_cutpoint,
        "head-race rejection changed replica evidence or the path catalog");
    const auto payload_after = fixture.payload_store.snapshot_or_throw();
    require(
        payload_after.snapshot_digest() == payload_cutpoint.snapshot_digest() &&
            payload_after.entry_count() == payload_cutpoint.entry_count(),
        "head-race rejection retained a payload before causal authorization");
}

void test_prepared_file_and_path_reproof() {
    Fixture fixture("anonsync-folder-scan-reproof");
    const std::string path = "stable.txt";
    write_file(fixture.shared_root / path, "before mutation");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "catalog reproof database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto prepared = scan->prepare_regular_file_or_throw(path);
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    write_file(fixture.shared_root / path, "after mutation and longer");
    require_error(
        [&] {
            (void)scan->commit_prepared_regular_file_or_throw(
                std::move(prepared));
        },
        "prepared file changed",
        "in-place mutation of the retained descriptor was not rejected");
    require(
        fixture.replica.snapshot_or_throw() == replica_cutpoint &&
            scan->snapshot_or_throw() == catalog_cutpoint,
        "file-mutation rejection changed durable publication state");

    const fs::path real = fixture.shared_root / "real.txt";
    const fs::path link = fixture.shared_root / "link.txt";
    write_file(real, "symlink target");
    std::error_code symlink_error;
    fs::create_symlink(real.filename(), link, symlink_error);
    if (!symlink_error) {
        require_error(
            [&] { (void)scan->scan_regular_file_or_throw("link.txt"); },
            "must not be a symlink",
            "final-component symlink entered the configured-folder scanner");
    }
}

void test_restart_adopts_publication_after_catalog_crash_window() {
    Fixture fixture("anonsync-folder-scan-adoption");
    const std::string path = "crash-window.txt";
    const std::string bytes = "published before catalog commit";
    write_file(fixture.shared_root / path, bytes);

    std::string published_id;
    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog adoption prepare database");
        auto scan = fixture.make_scan_owner(catalog_db);
        auto prepared = scan->prepare_regular_file_or_throw(path);
        const auto payload = fixture.payload_store.put_payload_or_throw(bytes);
        require(
            payload.content_sha256 == prepared.content_sha256() &&
                payload.size_bytes == prepared.size_bytes(),
            "crash-window fixture did not retain the prepared payload");
        const auto operation =
            fixture.replica.publish_local_file_from_observed_heads_or_throw(
                path, prepared.observed_visible_operation_ids(),
                prepared.size_bytes(), prepared.content_sha256());
        published_id = operation.operation_id;
        // Deliberately abandon the prepared observation before catalog commit.
    }

    const auto before_recovery = fixture.replica.snapshot_or_throw();
    require(
        before_recovery.durable.operations.size() == 1U &&
            before_recovery.outbox.empty(),
        "crash-window fixture did not stop after share-global publication");
    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog adoption recovery database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto recovered = scan->scan_regular_file_or_throw(path);
        require(
            recovered.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::
                        AdoptedVisibleOperation &&
                !recovered.published_operation.has_value() &&
                recovered.entry.operation_id == published_id,
            "restart did not adopt a matching already-visible publication");
        const auto after_recovery = fixture.replica.snapshot_or_throw();
        require(
            after_recovery == before_recovery &&
                find_entry(scan->snapshot_or_throw(), path).has_value(),
            "catalog crash recovery republished or lost the path mapping");
    }
}

void test_replica_ahead_and_populated_collision_fail_closed() {
    {
        Fixture fixture("anonsync-folder-scan-replica-ahead");
        const std::string path = "advanced.txt";
        const std::string base_bytes = "cataloged base";
        const std::string remote_bytes = "new remote value";
        write_file(fixture.shared_root / path, base_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog replica-ahead database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto base = scan->scan_regular_file_or_throw(path);
        require(
            base.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::Published &&
                base.published_operation.has_value(),
            "replica-ahead fixture did not publish its local base");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-scan-remote-ahead", 3U});
        require(
            remote.accept_remote_or_throw(*base.published_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "replica-ahead fixture did not import the cataloged base");
        const std::vector<std::string> base_head{base.entry.operation_id};
        const auto remote_edit =
            remote.create_local_file_from_observed_heads_or_throw(
                path, base_head, remote_bytes.size(),
                anonsync::sha256_hex(remote_bytes));
        require(
            fixture.replica.accept_remote_or_throw(remote_edit) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "replica-ahead fixture did not admit the remote successor");

        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
        const auto payload_cutpoint = fixture.payload_store.snapshot_or_throw();
        require_error(
            [&] { (void)scan->scan_regular_file_or_throw(path); },
            "advanced beyond the cataloged local base",
            "unchanged materialized base silently ignored a newer replica head");
        write_file(fixture.shared_root / path, "local edit from old base");
        require_error(
            [&] { (void)scan->scan_regular_file_or_throw(path); },
            "advanced beyond the cataloged local base",
            "local edit from an old materialized base laundered the newer head");
        require(
            scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint &&
                fixture.payload_store.snapshot_or_throw().snapshot_digest() ==
                    payload_cutpoint.snapshot_digest(),
            "replica-ahead refusal changed catalog, evidence, or payload state");

        write_file(fixture.shared_root / path, remote_bytes);
        const auto adopted = scan->scan_regular_file_or_throw(path);
        require(
            adopted.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::
                        AdoptedVisibleOperation &&
                adopted.entry.operation_id == remote_edit.operation_id &&
                !adopted.published_operation.has_value() &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "materialized remote value was not adopted without republishing");
    }

    {
        Fixture fixture("anonsync-folder-scan-populated-collision");
        const std::string path = "existing.txt";
        const std::string remote_bytes = "replicated value";
        const std::string local_bytes = "pre-existing local value";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-scan-remote-collision", 7U});
        const auto remote_file = remote.create_local_file_or_throw(
            path, remote_bytes.size(), anonsync::sha256_hex(remote_bytes));
        require(
            fixture.replica.accept_remote_or_throw(remote_file) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "populated-collision fixture did not admit the remote value");
        write_file(fixture.shared_root / path, local_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "catalog populated-collision database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
        const auto payload_cutpoint = fixture.payload_store.snapshot_or_throw();
        require_error(
            [&] { (void)scan->scan_regular_file_or_throw(path); },
            "uncataloged local file collides",
            "populated target silently overwrote an existing replica value");
        require(
            scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint &&
                fixture.payload_store.snapshot_or_throw().snapshot_digest() ==
                    payload_cutpoint.snapshot_digest(),
            "populated-target collision changed durable state");

        write_file(fixture.shared_root / path, remote_bytes);
        const auto adopted = scan->scan_regular_file_or_throw(path);
        require(
            adopted.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::
                        AdoptedVisibleOperation &&
                adopted.entry.operation_id == remote_file.operation_id &&
                !adopted.published_operation.has_value(),
            "matching populated target did not adopt existing evidence");
    }
}

void test_multi_head_conflict_is_preserved() {
    Fixture fixture("anonsync-folder-scan-conflict");
    const std::string path = "conflicted.txt";
    const std::string common_bytes = "common";
    const std::string alpha_bytes = "alpha candidate";
    const std::string bravo_bytes = "bravo candidate";

    anonsync::SyncReplicaModel alpha(
        Fixture::folder_id, {"device-scan-alpha", 11U});
    anonsync::SyncReplicaModel bravo(
        Fixture::folder_id, {"device-scan-bravo", 12U});
    const auto common = alpha.create_local_file_or_throw(
        path, common_bytes.size(), anonsync::sha256_hex(common_bytes));
    require(
        bravo.accept_remote_or_throw(common) ==
            anonsync::SyncReplicaAdmission::InsertedActive,
        "conflict fixture did not share its common predecessor");
    const std::vector<std::string> common_head{common.operation_id};
    const auto alpha_edit = alpha.create_local_file_from_observed_heads_or_throw(
        path, common_head, alpha_bytes.size(), anonsync::sha256_hex(alpha_bytes));
    const auto bravo_edit = bravo.create_local_file_from_observed_heads_or_throw(
        path, common_head, bravo_bytes.size(), anonsync::sha256_hex(bravo_bytes));
    require(
        fixture.replica.accept_remote_or_throw(common) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.replica.accept_remote_or_throw(alpha_edit) ==
                anonsync::SyncReplicaAdmission::InsertedActive &&
            fixture.replica.accept_remote_or_throw(bravo_edit) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
        "folder scanner conflict fixture did not retain both candidates");

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "catalog conflict database");
    auto scan = fixture.make_scan_owner(catalog_db);
    write_file(fixture.shared_root / path, alpha_bytes);
    const auto adopted = scan->scan_regular_file_or_throw(path);
    require(
        adopted.disposition ==
                anonsync::SyncReplicaFolderScanDisposition::
                    AdoptedVisibleOperation &&
            adopted.entry.operation_id == alpha_edit.operation_id &&
            !adopted.published_operation.has_value(),
        "scanner did not map a displayed candidate without resolving conflict");
    const auto conflicted = fixture.replica.snapshot_or_throw();
    const auto view = restore_model(conflicted).visible_path(path);
    require(
        view.has_value() && view->visible_operation_ids.size() == 2U &&
            conflicted.durable.last_local_counter == 0U &&
            conflicted.outbox.empty(),
        "mapping one conflict candidate collapsed or scheduled the conflict");

    write_file(fixture.shared_root / path, "third unchosen candidate");
    const auto catalog_cutpoint = scan->snapshot_or_throw();
    const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
    require_error(
        [&] { (void)scan->scan_regular_file_or_throw(path); },
        "unresolved path conflict requires explicit resolution",
        "ordinary folder scan silently collapsed a two-head conflict");
    require(
        scan->snapshot_or_throw() == catalog_cutpoint &&
            fixture.replica.snapshot_or_throw() == replica_cutpoint,
        "conflict refusal changed the catalog or replica cutpoint");
}


void test_remote_apply_replaces_predecessor_without_echo_and_restarts() {
    Fixture fixture("anonsync-folder-apply-lifecycle");
    const std::string path = "docs/apply.txt";
    const std::string base_bytes = "local materialized predecessor";
    const std::string target_bytes = "remote successor bytes";
    write_file(fixture.shared_root / path, base_bytes);

    std::string target_operation_id;
    anonsync::SyncReplicaSqliteSnapshot replica_after_remote;
    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "apply lifecycle catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto base = scan->scan_regular_file_or_throw(path);
        require(
            base.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::Published &&
                base.published_operation.has_value(),
            "apply lifecycle did not publish its local predecessor");

        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-apply-remote", 21U});
        require(
            remote.accept_remote_or_throw(*base.published_operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "apply lifecycle remote did not retain the predecessor");
        const std::vector<std::string> base_head{base.entry.operation_id};
        const auto target =
            remote.create_local_file_from_observed_heads_or_throw(
                path, base_head, target_bytes.size(),
                anonsync::sha256_hex(target_bytes));
        target_operation_id = target.operation_id;
        require(
            fixture.replica.accept_remote_or_throw(target) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(target_bytes)
                        .content_sha256 == target.content_sha256,
            "apply lifecycle did not admit the exact remote successor");
        replica_after_remote = fixture.replica.snapshot_or_throw();

        const std::uint64_t predecessor_inode =
            file_inode(fixture.shared_root / path);
        const auto applied =
            scan->apply_visible_regular_file_or_throw(target.operation_id);
        require(
            applied.disposition ==
                    anonsync::SyncReplicaFolderApplyDisposition::Applied &&
                applied.operation == target &&
                applied.entry.operation_id == target.operation_id &&
                read_file(fixture.shared_root / path) == target_bytes,
            "remote successor was not atomically materialized and cataloged");
        require(
            file_inode(fixture.shared_root / path) != predecessor_inode,
            "remote replacement reused the predecessor inode instead of an atomic rename");
        require(
            fixture.replica.snapshot_or_throw() == replica_after_remote,
            "remote apply minted evidence or delivery work");

        const auto next_scan = scan->scan_regular_file_or_throw(path);
        require(
            next_scan.disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::CatalogNoOp &&
                next_scan.entry.operation_id == target.operation_id &&
                !next_scan.published_operation.has_value() &&
                fixture.replica.snapshot_or_throw() == replica_after_remote,
            "the scan after remote apply echoed the received value");

        const std::uint64_t applied_inode =
            file_inode(fixture.shared_root / path);
        const auto duplicate =
            scan->apply_visible_regular_file_or_throw(target.operation_id);
        require(
            duplicate.disposition ==
                    anonsync::SyncReplicaFolderApplyDisposition::CatalogNoOp &&
                duplicate.entry.operation_id == target.operation_id &&
                file_inode(fixture.shared_root / path) == applied_inode,
            "duplicate remote apply rewrote an exact cataloged target");
    }

    {
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "apply lifecycle restart database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto restarted =
            scan->apply_visible_regular_file_or_throw(target_operation_id);
        require(
            restarted.disposition ==
                    anonsync::SyncReplicaFolderApplyDisposition::CatalogNoOp &&
                read_file(fixture.shared_root / path) == target_bytes &&
                fixture.replica.snapshot_or_throw() == replica_after_remote,
            "restart did not restore the exact applied mapping as a no-op");
    }
}

void test_remote_apply_absent_exact_adoption_and_collision() {
    {
        Fixture fixture("anonsync-folder-apply-absent");
        const std::string path = "missing/parents/absent.txt";
        const std::string bytes = "remote initial value";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-apply-absent", 22U});
        const auto target = remote.create_local_file_or_throw(
            path, bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(target) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes)
                        .content_sha256 == target.content_sha256,
            "absent-target fixture did not admit remote evidence and bytes");
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "absent-target catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto applied =
            scan->apply_visible_regular_file_or_throw(target.operation_id);
        require(
            applied.disposition ==
                    anonsync::SyncReplicaFolderApplyDisposition::Applied &&
                read_file(fixture.shared_root / path) == bytes &&
                fs::is_directory(fixture.shared_root / "missing") &&
                fs::is_directory(fixture.shared_root / "missing" / "parents") &&
                applied.entry.operation_id == target.operation_id,
            "remote initial value did not create and use its safe parent chain");
        require(
            scan->scan_regular_file_or_throw(path).disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::CatalogNoOp &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "absent-target apply was echoed by the next local scan");
    }

    {
        Fixture fixture("anonsync-folder-apply-adopt-exact");
        const std::string path = "already-exact.txt";
        const std::string bytes = "already materialized remote value";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-apply-exact", 23U});
        const auto target = remote.create_local_file_or_throw(
            path, bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(target) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes)
                        .content_sha256 == target.content_sha256,
            "exact-adoption fixture did not admit remote evidence and bytes");
        write_file(fixture.shared_root / path, bytes);
        const std::uint64_t inode_before =
            file_inode(fixture.shared_root / path);
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "exact-adoption catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto adopted =
            scan->apply_visible_regular_file_or_throw(target.operation_id);
        require(
            adopted.disposition ==
                    anonsync::SyncReplicaFolderApplyDisposition::
                        AdoptedExactTarget &&
                adopted.entry.operation_id == target.operation_id &&
                file_inode(fixture.shared_root / path) == inode_before,
            "exact pre-existing target was rewritten instead of durably adopted");
        require(
            scan->scan_regular_file_or_throw(path).disposition ==
                    anonsync::SyncReplicaFolderScanDisposition::CatalogNoOp &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "exact adoption did not suppress local publication");
    }

    {
        Fixture fixture("anonsync-folder-apply-collision");
        const std::string path = "collision.txt";
        const std::string target_bytes = "remote collision target";
        const std::string local_bytes = "unrelated populated local value";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-apply-collision", 24U});
        const auto target = remote.create_local_file_or_throw(
            path, target_bytes.size(), anonsync::sha256_hex(target_bytes));
        require(
            fixture.replica.accept_remote_or_throw(target) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(target_bytes)
                        .content_sha256 == target.content_sha256,
            "collision fixture did not admit remote evidence and bytes");
        write_file(fixture.shared_root / path, local_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "collision catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
        require_error(
            [&] {
                (void)scan->apply_visible_regular_file_or_throw(
                    target.operation_id);
            },
            "uncataloged local file collides",
            "remote apply overwrote an unrelated populated pathname");
        require(
            read_file(fixture.shared_root / path) == local_bytes &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "populated-target refusal changed the local file or durable state");
    }
}

void test_remote_apply_parent_chain_refuses_unsafe_components() {
    {
        Fixture fixture("anonsync-folder-apply-parent-symlink");
        const fs::path outside = fixture.temporary.make_directory("outside");
        const fs::path link = fixture.shared_root / "escape";
        std::error_code symlink_error;
        fs::create_directory_symlink(outside, link, symlink_error);
        if (!symlink_error) {
            const std::string path = "escape/outside.txt";
            const std::string bytes = "must remain inside the configured root";
            anonsync::SyncReplicaModel remote(
                Fixture::folder_id, {"device-apply-parent-symlink", 24U});
            const auto target = remote.create_local_file_or_throw(
                path, bytes.size(), anonsync::sha256_hex(bytes));
            require(
                fixture.replica.accept_remote_or_throw(target) ==
                        anonsync::SyncReplicaAdmission::InsertedActive &&
                    fixture.payload_store.put_payload_or_throw(bytes)
                            .content_sha256 == target.content_sha256,
                "parent-symlink fixture did not admit remote evidence and bytes");

            anonsync::SyncSqliteDb catalog_db = open_database(
                fixture.catalog_path(), "parent-symlink catalog database");
            auto scan = fixture.make_scan_owner(catalog_db);
            const auto catalog_cutpoint = scan->snapshot_or_throw();
            require_error(
                [&] {
                    (void)scan->apply_visible_regular_file_or_throw(
                        target.operation_id);
                },
                "must not be a symlink",
                "remote apply traversed a symbolic-link parent");
            require(
                !fs::exists(outside / "outside.txt") &&
                    scan->snapshot_or_throw() == catalog_cutpoint,
                "symbolic-link parent refusal changed outside or catalog state");
        }
    }

    {
        Fixture fixture("anonsync-folder-apply-parent-file");
        const fs::path blocker = fixture.shared_root / "blocked";
        const std::string blocker_bytes = "ordinary local file";
        write_file(blocker, blocker_bytes);
        const std::string path = "blocked/child.txt";
        const std::string bytes = "remote child";
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-apply-parent-file", 25U});
        const auto target = remote.create_local_file_or_throw(
            path, bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(target) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(bytes)
                        .content_sha256 == target.content_sha256,
            "parent-file fixture did not admit remote evidence and bytes");

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "parent-file catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        require_error(
            [&] {
                (void)scan->apply_visible_regular_file_or_throw(
                    target.operation_id);
            },
            "is not a directory",
            "remote apply replaced or traversed a regular-file parent");
        require(
            read_file(blocker) == blocker_bytes &&
                scan->snapshot_or_throw() == catalog_cutpoint,
            "regular-file parent refusal changed the blocker or catalog state");
    }
}

void test_remote_apply_rejects_local_mutation_and_multihead() {
    {
        Fixture fixture("anonsync-folder-apply-local-mutation");
        const std::string path = "mutated.txt";
        const std::string base_bytes = "cataloged local base";
        const std::string target_bytes = "remote successor";
        const std::string changed_bytes = "local edit after remote arrival";
        write_file(fixture.shared_root / path, base_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "local-mutation catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto base = scan->scan_regular_file_or_throw(path);
        anonsync::SyncReplicaModel remote(
            Fixture::folder_id, {"device-apply-mutation", 25U});
        require(
            base.published_operation.has_value() &&
                remote.accept_remote_or_throw(*base.published_operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive,
            "local-mutation fixture did not establish its common base");
        const std::vector<std::string> base_head{base.entry.operation_id};
        const auto target =
            remote.create_local_file_from_observed_heads_or_throw(
                path, base_head, target_bytes.size(),
                anonsync::sha256_hex(target_bytes));
        require(
            fixture.replica.accept_remote_or_throw(target) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(target_bytes)
                        .content_sha256 == target.content_sha256,
            "local-mutation fixture did not admit its remote successor");
        write_file(fixture.shared_root / path, changed_bytes);
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
        require_error(
            [&] {
                (void)scan->apply_visible_regular_file_or_throw(
                    target.operation_id);
            },
            "local path changed from the cataloged predecessor",
            "remote apply overwrote a local edit after remote arrival");
        require(
            read_file(fixture.shared_root / path) == changed_bytes &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "local-mutation refusal changed the file or durable owners");
    }

    {
        Fixture fixture("anonsync-folder-apply-multihead");
        const std::string path = "multihead.txt";
        const std::string base_bytes = "common materialized base";
        const std::string alpha_bytes = "alpha remote edit";
        const std::string bravo_bytes = "bravo remote edit";
        write_file(fixture.shared_root / path, base_bytes);

        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "multihead apply catalog database");
        auto scan = fixture.make_scan_owner(catalog_db);
        const auto base = scan->scan_regular_file_or_throw(path);
        require(
            base.published_operation.has_value(),
            "multihead apply fixture did not publish its common base");

        anonsync::SyncReplicaModel alpha(
            Fixture::folder_id, {"device-apply-alpha", 26U});
        anonsync::SyncReplicaModel bravo(
            Fixture::folder_id, {"device-apply-bravo", 27U});
        require(
            alpha.accept_remote_or_throw(*base.published_operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                bravo.accept_remote_or_throw(*base.published_operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive,
            "multihead apply fixture did not share its common base");
        const std::vector<std::string> base_head{base.entry.operation_id};
        const auto alpha_edit =
            alpha.create_local_file_from_observed_heads_or_throw(
                path, base_head, alpha_bytes.size(),
                anonsync::sha256_hex(alpha_bytes));
        const auto bravo_edit =
            bravo.create_local_file_from_observed_heads_or_throw(
                path, base_head, bravo_bytes.size(),
                anonsync::sha256_hex(bravo_bytes));
        require(
            fixture.replica.accept_remote_or_throw(alpha_edit) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.replica.accept_remote_or_throw(bravo_edit) ==
                    anonsync::SyncReplicaAdmission::InsertedActive &&
                fixture.payload_store.put_payload_or_throw(alpha_bytes)
                        .content_sha256 == alpha_edit.content_sha256,
            "multihead apply fixture did not retain both candidates");
        const auto catalog_cutpoint = scan->snapshot_or_throw();
        const auto replica_cutpoint = fixture.replica.snapshot_or_throw();
        require_error(
            [&] {
                (void)scan->apply_visible_regular_file_or_throw(
                    alpha_edit.operation_id);
            },
            "not the sole visible value",
            "ordinary remote apply silently chose one concurrent head");
        require(
            read_file(fixture.shared_root / path) == base_bytes &&
                scan->snapshot_or_throw() == catalog_cutpoint &&
                fixture.replica.snapshot_or_throw() == replica_cutpoint,
            "multihead refusal changed the materialized base or durable state");
    }
}

void test_remote_apply_path_fence_and_crash_recovery() {
    {
        TemporaryDirectory temporary("anonsync-folder-apply-path-fence");
        const fs::path root = temporary.make_directory("root");
        const fs::path destination = root / "guarded.txt";
        const fs::path replacement = root / "racing-replacement";
        const std::string predecessor = "expected predecessor";
        const std::string racing_value = "local substitution wins";
        const std::string remote_value = "remote value must not overwrite race";
        write_file(destination, predecessor);
        write_file(replacement, racing_value);
        const auto expected = observe_regular_file_metadata(destination);
        const std::uint64_t expected_inode = file_inode(destination);
        auto authority = anonsync::SyncDirectoryAuthority::open_or_throw(
            root, "folder apply path-fence root");
        SubstituteFinalAtCutpointContext context{
            replacement, destination, false};
        require_error(
            [&] {
                anonsync::atomic_file_publication_detail::
                    write_sync_file_atomically_replace_expected_under_directory_with_observer_or_throw(
                        authority, fs::path("guarded.txt"),
                        byte_span(remote_value), expected,
                        "folder apply path-fence replacement",
                        substitute_final_after_temp_sync, &context);
            },
            "no longer names the expected regular file",
            "conditional replacement overwrote a pathname substituted after planning");
        require(
            context.observed &&
                file_inode(destination) != expected_inode &&
                read_file(destination) == racing_value,
            "pre-rename pathname fence did not preserve the racing local value");
    }

    {
        Fixture fixture("anonsync-folder-apply-crash-recovery");
        const std::string path = "crash-recovery.txt";
        const std::string base_bytes = "durable cataloged predecessor";
        const std::string target_bytes = "published before catalog recovery";
        write_file(fixture.shared_root / path, base_bytes);

        std::string target_operation_id;
        anonsync::SyncReplicaSqliteSnapshot replica_after_remote;
        {
            anonsync::SyncSqliteDb catalog_db = open_database(
                fixture.catalog_path(), "apply crash prepare catalog");
            auto scan = fixture.make_scan_owner(catalog_db);
            const auto base = scan->scan_regular_file_or_throw(path);
            require(
                base.published_operation.has_value(),
                "apply crash fixture did not publish its predecessor");

            anonsync::SyncReplicaModel remote(
                Fixture::folder_id, {"device-apply-crash", 28U});
            require(
                remote.accept_remote_or_throw(*base.published_operation) ==
                    anonsync::SyncReplicaAdmission::InsertedActive,
                "apply crash fixture remote did not retain its predecessor");
            const std::vector<std::string> base_head{base.entry.operation_id};
            const auto target =
                remote.create_local_file_from_observed_heads_or_throw(
                    path, base_head, target_bytes.size(),
                    anonsync::sha256_hex(target_bytes));
            target_operation_id = target.operation_id;
            require(
                fixture.replica.accept_remote_or_throw(target) ==
                        anonsync::SyncReplicaAdmission::InsertedActive &&
                    fixture.payload_store.put_payload_or_throw(target_bytes)
                            .content_sha256 == target.content_sha256,
                "apply crash fixture did not admit the remote successor");
            replica_after_remote = fixture.replica.snapshot_or_throw();

            const auto expected =
                observe_regular_file_metadata(fixture.shared_root / path);
            auto authority = anonsync::SyncDirectoryAuthority::open_or_throw(
                fixture.shared_root, "folder apply crash root");
            ThrowAtPublicationCutpointContext context;
            bool caught_typed_failure = false;
            try {
                anonsync::atomic_file_publication_detail::
                    write_sync_file_atomically_replace_expected_under_directory_with_observer_or_throw(
                        authority, fs::path(path), byte_span(target_bytes),
                        expected, "folder apply crash publication",
                        throw_at_publication_cutpoint, &context);
            } catch (const anonsync::SyncAtomicFilePublicationError& error) {
                caught_typed_failure = true;
                require(
                    error.outcome() ==
                        anonsync::SyncAtomicFilePublicationOutcome::
                            PublishedDurabilityIndeterminate,
                    "post-rename crash cutpoint reported the wrong effect outcome");
            }
            require(
                caught_typed_failure && context.observed &&
                    read_file(fixture.shared_root / path) == target_bytes,
                "crash cutpoint did not leave the exact published namespace effect");
            const auto stale_catalog = scan->snapshot_or_throw();
            const auto stale_entry = find_entry(stale_catalog, path);
            require(
                stale_entry.has_value() &&
                    stale_entry->operation_id == base.entry.operation_id,
                "simulated crash advanced the catalog after namespace publication");
        }

        {
            anonsync::SyncSqliteDb catalog_db = open_database(
                fixture.catalog_path(), "apply crash recovery catalog");
            auto scan = fixture.make_scan_owner(catalog_db);
            const auto recovered =
                scan->apply_visible_regular_file_or_throw(
                    target_operation_id);
            require(
                recovered.disposition ==
                        anonsync::SyncReplicaFolderApplyDisposition::
                            AdoptedExactTarget &&
                    recovered.entry.operation_id == target_operation_id &&
                    read_file(fixture.shared_root / path) == target_bytes,
                "restart did not durably adopt the exact post-rename target");
            const auto no_echo = scan->scan_regular_file_or_throw(path);
            require(
                no_echo.disposition ==
                        anonsync::SyncReplicaFolderScanDisposition::
                            CatalogNoOp &&
                    no_echo.entry.operation_id == target_operation_id &&
                    fixture.replica.snapshot_or_throw() == replica_after_remote,
                "crash recovery echoed the already-received remote value");
        }
    }
}



void test_historical_version_inspection_and_causal_restore() {
    Fixture fixture("anonsync-folder-historical-version-restore");
    constexpr std::string_view path = "notes/plan.txt";
    const std::string first_bytes = "version one\n";
    const std::string second_bytes = "version two\n";

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "historical-version catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);

    write_file(fixture.shared_root / path, first_bytes);
    const auto first_pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto first_entry = find_entry(
        scan->snapshot_or_throw(), path);
    require(
        first_pass.local_published_count == 1U && first_entry.has_value(),
        "historical-version fixture did not publish its first file value");
    const auto first_model = restore_model(
        fixture.replica.snapshot_or_throw());
    const auto first_operation = first_model.operation_by_id(
        first_entry->operation_id);
    require(
        first_operation.has_value() &&
            first_operation->kind == anonsync::SyncReplicaValueKind::File &&
            first_operation->content_sha256 ==
                anonsync::sha256_hex(first_bytes) &&
            first_operation->size_bytes == first_bytes.size(),
        "historical-version fixture lost its first causal file operation");

    write_file(fixture.shared_root / path, second_bytes);
    const auto second_pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto second_entry = find_entry(
        scan->snapshot_or_throw(), path);
    require(
        second_pass.local_published_count == 1U && second_entry.has_value() &&
            second_entry->operation_id != first_entry->operation_id,
        "historical-version fixture did not publish its successor value");
    const auto second_model = restore_model(
        fixture.replica.snapshot_or_throw());
    const auto second_operation = second_model.operation_by_id(
        second_entry->operation_id);
    require(
        second_operation.has_value() &&
            second_operation->content_sha256 ==
                anonsync::sha256_hex(second_bytes) &&
            anonsync::sync_replica_operation_supersedes(
                *second_operation, *first_operation),
        "historical-version fixture successor is not causally above the first value");

    require_error(
        [&] { (void)scan->inspect_historical_versions_or_throw(0U); },
        "entry limit is invalid",
        "historical-version inspection accepted a zero entry limit");
    require_error(
        [&] {
            (void)scan->inspect_historical_versions_or_throw(
                anonsync::kSyncReplicaHistoricalVersionMaximumEntries + 1U);
        },
        "entry limit is invalid",
        "historical-version inspection accepted an oversized entry limit");

    const auto before_restore =
        scan->inspect_historical_versions_or_throw();
    require(
        before_restore.source_replica_state_generation ==
                fixture.replica.snapshot_or_throw().state_generation &&
            before_restore.source_operation_set_digest ==
                fixture.replica.snapshot_or_throw().operation_set_digest &&
            before_restore.source_visible_state_digest.size() == 64U &&
            before_restore.source_evidence_set_digest.has_value() &&
            before_restore.source_evidence_set_digest->size() == 64U &&
            before_restore.source_payload_snapshot_digest.has_value() &&
            before_restore.source_payload_snapshot_digest->size() == 64U &&
            before_restore.historical_file_operation_count == 1U &&
            before_restore.payload_present_count ==
                std::optional<std::uint64_t>(1U) &&
            before_restore.restore_ready_count ==
                std::optional<std::uint64_t>(1U) &&
            before_restore.retained_payload_reachability.has_value() &&
            !before_restore.truncated &&
            before_restore.entries.size() == 1U,
        "historical-version inspection did not report one bounded retained predecessor");
    const auto& candidate = before_restore.entries.front();
    require(
        candidate.operation_id == first_operation->operation_id &&
            candidate.canonical_path == path &&
            candidate.size_bytes == first_bytes.size() &&
            candidate.content_sha256 == anonsync::sha256_hex(first_bytes) &&
            candidate.actor == first_operation->dot.actor &&
            candidate.counter == first_operation->dot.counter &&
            candidate.visible_head_count == 1U &&
            candidate.current_primary_operation_id ==
                second_operation->operation_id &&
            candidate.current_primary_kind ==
                anonsync::SyncReplicaValueKind::File &&
            candidate.payload_present == std::optional<bool>(true) &&
            candidate.restore_ready == std::optional<bool>(true),
        "historical-version inspection changed the exact causal candidate or readiness proof");

    const auto restored = scan->restore_historical_version_or_throw(
        anonsync::SyncReplicaHistoricalVersionRestoreRequest{
            .operation_id = first_operation->operation_id,
            .expected_current_operation_id = second_operation->operation_id,
        });
    require(
        restored.disposition ==
                anonsync::SyncReplicaHistoricalVersionRestoreDisposition::
                    Published &&
            restored.historical_operation == *first_operation &&
            restored.replaced_visible_operation == *second_operation &&
            restored.restored_operation.operation_id !=
                first_operation->operation_id &&
            restored.restored_operation.operation_id !=
                second_operation->operation_id &&
            restored.restored_operation.kind ==
                anonsync::SyncReplicaValueKind::File &&
            restored.restored_operation.canonical_path == path &&
            restored.restored_operation.size_bytes == first_bytes.size() &&
            restored.restored_operation.content_sha256 ==
                first_operation->content_sha256 &&
            anonsync::sync_replica_operation_supersedes(
                restored.restored_operation, *second_operation),
        "historical-version restore reactivated old evidence instead of minting one causal successor");
    require(
        read_file(fixture.shared_root / path) == first_bytes,
        "historical-version restore did not atomically publish the selected bytes");

    const auto after_catalog = scan->snapshot_or_throw();
    const auto after_entry = find_entry(after_catalog, path);
    const auto after_model = restore_model(
        fixture.replica.snapshot_or_throw());
    const auto after_view = after_model.visible_path(std::string(path));
    require(
        after_entry.has_value() &&
            after_entry->operation_id ==
                restored.restored_operation.operation_id &&
            after_entry->content_sha256 ==
                first_operation->content_sha256 &&
            after_view.has_value() &&
            after_view->visible_operation_ids.size() == 1U &&
            after_view->primary_operation_id ==
                restored.restored_operation.operation_id &&
            after_model.operation_by_id(first_operation->operation_id) ==
                first_operation &&
            after_model.operation_by_id(second_operation->operation_id) ==
                second_operation,
        "historical-version restore did not preserve immutable predecessors behind the new visible head");

    const auto bounded_after =
        scan->inspect_historical_versions_or_throw(1U);
    require(
        bounded_after.query == anonsync::SyncReplicaHistoricalVersionQuery{
            .maximum_entries = 1U,
            .canonical_path = std::nullopt,
            .start_after_operation_id = std::nullopt,
            .expected_source_cutpoint = std::nullopt} &&
            bounded_after.historical_file_operation_count == 2U &&
            bounded_after.historical_file_operation_count_after_cursor == 2U &&
            bounded_after.payload_present_count ==
                std::optional<std::uint64_t>(2U) &&
            bounded_after.restore_ready_count ==
                std::optional<std::uint64_t>(1U) &&
            bounded_after.truncated && bounded_after.entries.size() == 1U &&
            bounded_after.entries.front().operation_id ==
                second_operation->operation_id &&
            bounded_after.entries.front().restore_ready ==
                std::optional<bool>(true) &&
            bounded_after.next_start_after_operation_id ==
                std::optional<std::string>(second_operation->operation_id),
        "historical-version inspection did not bound, order, or cursor superseded causal values deterministically");

    const auto bounded_source = bounded_after.source_cutpoint();
    const std::string bounded_source_token = anonsync::
        encode_sync_replica_historical_version_source_cutpoint_or_throw(
            bounded_source, "historical-version test source cutpoint");
    require(
        anonsync::
            decode_sync_replica_historical_version_source_cutpoint_or_throw(
                bounded_source_token,
                "historical-version test source cutpoint") == bounded_source &&
            bounded_source_token.starts_with("v4:exact:") &&
            bounded_source_token.size() == 268U,
        "historical-version source cutpoint did not round-trip canonically");
    auto rev0972_exact_source = bounded_source;
    rev0972_exact_source.historical_version_pin_set_digest.reset();
    const std::string rev0972_exact_token = anonsync::
        encode_sync_replica_historical_version_source_cutpoint_or_throw(
            rev0972_exact_source,
            "historical-version rev0972 exact source cutpoint");
    require(
        rev0972_exact_token.starts_with("v3:exact:") &&
            rev0972_exact_token.size() == 203U &&
            anonsync::
                decode_sync_replica_historical_version_source_cutpoint_or_throw(
                    rev0972_exact_token,
                    "historical-version rev0972 exact source cutpoint") ==
                rev0972_exact_source,
        "rev0972 exact source cutpoint compatibility was not retained");
    auto legacy_exact_source = rev0972_exact_source;
    legacy_exact_source.evidence_set_digest.reset();
    const std::string legacy_exact_token = anonsync::
        encode_sync_replica_historical_version_source_cutpoint_or_throw(
            legacy_exact_source,
            "historical-version legacy exact source cutpoint");
    require(
        legacy_exact_token.starts_with("v1:") &&
            legacy_exact_token.size() == 132U &&
            anonsync::
                decode_sync_replica_historical_version_source_cutpoint_or_throw(
                    legacy_exact_token,
                    "historical-version legacy exact source cutpoint") ==
                legacy_exact_source,
        "rev0968 exact source cutpoint compatibility was not retained");
    require_error(
        [&] {
            (void)anonsync::
                decode_sync_replica_historical_version_source_cutpoint_or_throw(
                    "v1:not-a-source", "historical-version malformed source");
        },
        "token framing is invalid",
        "historical-version source cutpoint accepted malformed framing");

    anonsync::SyncReplicaHistoricalVersionQuery second_page_query;
    second_page_query.maximum_entries = 1U;
    second_page_query.start_after_operation_id =
        *bounded_after.next_start_after_operation_id;
    second_page_query.expected_source_cutpoint = bounded_source;
    const auto second_page =
        scan->inspect_historical_versions_or_throw(second_page_query);
    require(
        second_page.query == second_page_query &&
            second_page.historical_file_operation_count == 2U &&
            second_page.historical_file_operation_count_after_cursor == 1U &&
            second_page.payload_present_count ==
                std::optional<std::uint64_t>(2U) &&
            second_page.restore_ready_count ==
                std::optional<std::uint64_t>(1U) &&
            !second_page.truncated &&
            !second_page.next_start_after_operation_id.has_value() &&
            second_page.entries.size() == 1U &&
            second_page.entries.front().operation_id ==
                first_operation->operation_id &&
            second_page.entries.front().restore_ready ==
                std::optional<bool>(false),
        "historical-version cursor did not expose the exact deterministic second page");

    auto rev0972_second_page_query = second_page_query;
    rev0972_second_page_query.expected_source_cutpoint = rev0972_exact_source;
    const auto rev0972_second_page =
        scan->inspect_historical_versions_or_throw(rev0972_second_page_query);
    require(
        rev0972_second_page.entries == second_page.entries &&
            rev0972_second_page.source_cutpoint() == bounded_source,
        "empty-pin replica did not accept and upgrade a rev0972 exact source cutpoint");

    (void)fixture.payload_store.put_payload_or_throw(
        "unreferenced retained payload");
    bool caught_payload_source_change = false;
    try {
        (void)scan->inspect_historical_versions_or_throw(second_page_query);
    } catch (const anonsync::SyncReplicaHistoricalVersionSourceChangedError&
                 error) {
        caught_payload_source_change = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    PayloadSnapshot,
            "changed historical payload namespace reported the wrong failure stage");
    }
    require(
        caught_payload_source_change,
        "changed historical payload namespace did not fail a bound continuation");

    anonsync::SyncReplicaHistoricalVersionQuery path_query;
    path_query.maximum_entries = 2U;
    path_query.canonical_path = std::string(path);
    const auto path_page =
        scan->inspect_historical_versions_or_throw(path_query);
    require(
        path_page.query == path_query &&
            path_page.historical_file_operation_count == 2U &&
            path_page.historical_file_operation_count_after_cursor == 2U &&
            path_page.entries.size() == 2U && !path_page.truncated &&
            path_page.entries[0].operation_id ==
                second_operation->operation_id &&
            path_page.entries[1].operation_id ==
                first_operation->operation_id,
        "path-scoped historical inspection did not expose the complete selected history");

    anonsync::SyncReplicaHistoricalVersionQuery empty_path_query;
    empty_path_query.maximum_entries = 3U;
    empty_path_query.canonical_path = "missing/path.txt";
    const auto empty_path_page =
        scan->inspect_historical_versions_or_throw(empty_path_query);
    require(
        empty_path_page.query == empty_path_query &&
            empty_path_page.historical_file_operation_count == 0U &&
            empty_path_page.historical_file_operation_count_after_cursor == 0U &&
            empty_path_page.payload_present_count ==
                std::optional<std::uint64_t>(0U) &&
            empty_path_page.restore_ready_count ==
                std::optional<std::uint64_t>(0U) &&
            empty_path_page.entries.empty() && !empty_path_page.truncated &&
            !empty_path_page.next_start_after_operation_id.has_value(),
        "path-scoped historical inspection invented entries for an absent path");

    anonsync::SyncReplicaHistoricalVersionQuery outside_path_cursor;
    outside_path_cursor.canonical_path = "other/path.txt";
    outside_path_cursor.start_after_operation_id =
        second_operation->operation_id;
    require_error(
        [&] {
            (void)scan->inspect_historical_versions_or_throw(
                outside_path_cursor);
        },
        "outside the selected path",
        "historical-version inspection accepted a cursor from another path scope");

    anonsync::SyncReplicaHistoricalVersionQuery visible_cursor;
    visible_cursor.start_after_operation_id =
        restored.restored_operation.operation_id;
    require_error(
        [&] {
            (void)scan->inspect_historical_versions_or_throw(visible_cursor);
        },
        "no longer superseded",
        "historical-version inspection accepted a now-visible cursor");

    anonsync::SyncReplicaHistoricalVersionQuery malformed_path;
    malformed_path.canonical_path = "../escape";
    require_error(
        [&] {
            (void)scan->inspect_historical_versions_or_throw(malformed_path);
        },
        "path is not canonical",
        "historical-version inspection accepted a non-canonical path filter");

    anonsync::SyncReplicaHistoricalVersionQuery malformed_cursor;
    malformed_cursor.start_after_operation_id = "not-a-digest";
    require_error(
        [&] {
            (void)scan->inspect_historical_versions_or_throw(malformed_cursor);
        },
        "cursor is not one lowercase SHA-256 operation ID",
        "historical-version inspection accepted a malformed cursor");

    require_error(
        [&] {
            (void)scan->restore_historical_version_or_throw(
                anonsync::SyncReplicaHistoricalVersionRestoreRequest{
                    .operation_id = first_operation->operation_id,
                    .expected_current_operation_id = "not-a-digest",
                });
        },
        "expected current operation ID is invalid",
        "historical-version restore accepted a malformed expected current operation ID");
    require_error(
        [&] {
            (void)scan->restore_historical_version_or_throw(
                anonsync::SyncReplicaHistoricalVersionRestoreRequest{
                    .operation_id = first_operation->operation_id,
                    .expected_current_operation_id =
                        first_operation->operation_id,
                });
        },
        "historical and expected current operation IDs are equal",
        "historical-version restore accepted one operation as both history and current intent");

    require_error(
        [&] {
            (void)scan->restore_historical_version_or_throw(
                restored.restored_operation.operation_id);
        },
        "already visible",
        "historical-version restore accepted the current visible operation");
    require_error(
        [&] {
            (void)scan->restore_historical_version_or_throw(
                first_operation->operation_id);
        },
        "would not change current file bytes",
        "historical-version restore minted a duplicate value over identical current bytes");

    write_file(fixture.shared_root / path, "version three\n");
    const auto changed_source_pass = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        changed_source_pass.local_published_count == 1U,
        "historical-version source-change fixture did not publish a successor");
    const auto catalog_before_stale_restore = scan->snapshot_or_throw();
    const auto replica_before_stale_restore = fixture.replica.snapshot_or_throw();
    const std::string bytes_before_stale_restore =
        read_file(fixture.shared_root / path);
    bool caught_stale_restore = false;
    {
        // A stale exact-current request must fail from the replica snapshot
        // before opening catalog, rooted-path, or payload-store authority. The
        // live exclusive payload lease is a mechanical oracle: reaching targeted
        // access would report lease busy instead of the typed source change.
        auto payload_exclusion =
            fixture.payload_store.begin_mutation_batch_or_throw();
        try {
            (void)scan->restore_historical_version_or_throw(
                anonsync::SyncReplicaHistoricalVersionRestoreRequest{
                    .operation_id = second_operation->operation_id,
                    .expected_current_operation_id =
                        restored.restored_operation.operation_id,
                });
        } catch (const anonsync::
                     SyncReplicaHistoricalVersionSourceChangedError& error) {
            caught_stale_restore = true;
            require(
                error.stage() == anonsync::
                    SyncReplicaHistoricalVersionSourceChangeStage::
                        RestoreCurrentOperation,
                "stale exact-current restore reported the wrong source-change stage");
        }
        (void)payload_exclusion;
    }
    require(
        caught_stale_restore &&
            scan->snapshot_or_throw() == catalog_before_stale_restore &&
            fixture.replica.snapshot_or_throw() ==
                replica_before_stale_restore &&
            read_file(fixture.shared_root / path) ==
                bytes_before_stale_restore,
        "stale exact-current restore reached payload authority or changed durable/file state");
    bool caught_source_change = false;
    try {
        (void)scan->inspect_historical_versions_or_throw(second_page_query);
    } catch (const anonsync::SyncReplicaHistoricalVersionSourceChangedError&
                 error) {
        caught_source_change = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    OperationSetBeforePayloadObservation,
            "stale historical-version source pin reported the wrong failure stage");
    }
    require(
        caught_source_change,
        "stale historical-version source pin did not fail closed before payload observation");

    const auto current_before_metadata_only = find_entry(
        scan->snapshot_or_throw(), path);
    require(
        current_before_metadata_only.has_value() &&
            current_before_metadata_only->kind ==
                anonsync::SyncReplicaValueKind::File,
        "historical-version policy fixture lost its current catalog head");
    const auto metadata_only_policy =
        scan->replace_selective_sync_policy_or_throw(
            anonsync::SyncReplicaSelectiveSyncMode::Materialize,
            {{"notes",
              anonsync::SyncReplicaSelectiveSyncMode::MetadataOnly}});
    const auto catalog_before_metadata_restore = scan->snapshot_or_throw();
    const auto replica_before_metadata_restore =
        fixture.replica.snapshot_or_throw();
    const std::string bytes_before_metadata_restore =
        read_file(fixture.shared_root / path);
    {
        // A live exclusive payload lease proves the policy boundary rejects the
        // restore before targeted payload authority can be opened.
        auto payload_exclusion =
            fixture.payload_store.begin_mutation_batch_or_throw();
        require_error(
            [&] {
                (void)scan->restore_historical_version_or_throw(
                    anonsync::SyncReplicaHistoricalVersionRestoreRequest{
                        .operation_id = second_operation->operation_id,
                        .expected_current_operation_id =
                            current_before_metadata_only->operation_id,
                    });
            },
            "metadata-only under the current selective-sync policy",
            "historical restore opened payload authority for an excluded path");
        (void)payload_exclusion;
    }
    require(
        metadata_only_policy.generation > 1U &&
            scan->snapshot_or_throw() == catalog_before_metadata_restore &&
            fixture.replica.snapshot_or_throw() ==
                replica_before_metadata_restore &&
            read_file(fixture.shared_root / path) ==
                bytes_before_metadata_restore,
        "rejected metadata-only historical restore changed durable or rooted state");
}


void test_historical_version_metadata_only_is_payload_cold() {
    Fixture fixture("anonsync-folder-historical-version-metadata-only");
    constexpr std::string_view path = "history/metadata.txt";
    const std::string first_bytes = "metadata predecessor\n";
    const std::string second_bytes = "metadata current\n";

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "metadata-only history catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);

    write_file(fixture.shared_root / path, first_bytes);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto first_entry = find_entry(scan->snapshot_or_throw(), path);
    require(
        first_entry.has_value(),
        "metadata-only history fixture did not publish its predecessor");

    write_file(fixture.shared_root / path, second_bytes);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto second_entry = find_entry(scan->snapshot_or_throw(), path);
    require(
        second_entry.has_value() &&
            second_entry->operation_id != first_entry->operation_id,
        "metadata-only history fixture did not publish its current value");

    // A complete payload snapshot must reject this unrelated namespace entry.
    // Metadata-only inspection is required to remain entirely payload-cold and
    // therefore succeeds without converting the absence of a scan into false
    // payload-negative evidence.
    const fs::path unexpected =
        fixture.payload_root / "unexpected-history-inspection-entry";
    write_file(unexpected, "not payload authority");

    anonsync::SyncReplicaHistoricalVersionQuery metadata_query;
    metadata_query.inspection_mode = anonsync::
        SyncReplicaHistoricalVersionInspectionMode::CausalMetadataOnly;
    metadata_query.canonical_path = std::string(path);
    metadata_query.maximum_entries = 1U;
    const auto metadata =
        scan->inspect_historical_versions_or_throw(metadata_query);
    require(
        metadata.query == metadata_query &&
            metadata.source_operation_set_digest.size() == 64U &&
            !metadata.source_evidence_set_digest.has_value() &&
            !metadata.source_payload_snapshot_digest.has_value() &&
            !metadata.payload_scan_hashed_entry_count.has_value() &&
            !metadata.payload_scan_hashed_bytes.has_value() &&
            !metadata.payload_scan_reused_entry_count.has_value() &&
            !metadata.payload_scan_reused_bytes.has_value() &&
            !metadata.retained_payload_reachability.has_value() &&
            !metadata.payload_present_count.has_value() &&
            !metadata.restore_ready_count.has_value() &&
            metadata.historical_file_operation_count == 1U &&
            metadata.historical_file_operation_count_after_cursor == 1U &&
            !metadata.truncated && metadata.entries.size() == 1U,
        "metadata-only history inspection fabricated payload authority");
    const auto& entry = metadata.entries.front();
    require(
        entry.operation_id == first_entry->operation_id &&
            entry.canonical_path == path &&
            entry.size_bytes == first_bytes.size() &&
            entry.content_sha256 == anonsync::sha256_hex(first_bytes) &&
            entry.current_primary_operation_id == second_entry->operation_id &&
            !entry.payload_present.has_value() &&
            !entry.restore_ready.has_value(),
        "metadata-only history inspection changed causal metadata or invented availability");

    const auto metadata_cutpoint = metadata.source_cutpoint();
    const std::string metadata_token = anonsync::
        encode_sync_replica_historical_version_source_cutpoint_or_throw(
            metadata_cutpoint,
            "metadata-only historical-version source cutpoint");
    require(
        metadata_token.starts_with("v4:metadata:") &&
            metadata_token.size() == 141U &&
            anonsync::
                decode_sync_replica_historical_version_source_cutpoint_or_throw(
                    metadata_token,
                    "metadata-only historical-version source cutpoint") ==
                metadata_cutpoint,
        "metadata-only source cutpoint was not mode-bound and canonical");
    auto legacy_metadata_cutpoint = metadata_cutpoint;
    legacy_metadata_cutpoint.historical_version_pin_set_digest.reset();
    const std::string legacy_metadata_token = anonsync::
        encode_sync_replica_historical_version_source_cutpoint_or_throw(
            legacy_metadata_cutpoint,
            "legacy metadata-only historical-version source cutpoint");
    require(
        legacy_metadata_token.starts_with("v2:metadata:") &&
            legacy_metadata_token.size() == 76U &&
            anonsync::
                decode_sync_replica_historical_version_source_cutpoint_or_throw(
                    legacy_metadata_token,
                    "legacy metadata-only historical-version source cutpoint") ==
                legacy_metadata_cutpoint,
        "rev0970 metadata source cutpoint compatibility was not retained");

    metadata_query.expected_source_cutpoint = metadata_cutpoint;
    const auto pinned_metadata =
        scan->inspect_historical_versions_or_throw(metadata_query);
    require(
        pinned_metadata.source_cutpoint() == metadata_cutpoint &&
            pinned_metadata.entries == metadata.entries,
        "metadata-only source cutpoint did not reproduce the causal page");
    metadata_query.expected_source_cutpoint = legacy_metadata_cutpoint;
    const auto legacy_metadata =
        scan->inspect_historical_versions_or_throw(metadata_query);
    require(
        legacy_metadata.entries == metadata.entries &&
            legacy_metadata.source_cutpoint() == metadata_cutpoint,
        "empty-pin replica did not accept and upgrade a rev0970 metadata source cutpoint");

    require_error(
        [&] {
            anonsync::SyncReplicaHistoricalVersionQuery exact_query;
            exact_query.canonical_path = std::string(path);
            (void)scan->inspect_historical_versions_or_throw(exact_query);
        },
        "unexpected payload-root entry",
        "exact history inspection did not retain complete payload-namespace authority");

    fs::remove(unexpected);
    anonsync::SyncReplicaHistoricalVersionQuery exact_query;
    exact_query.canonical_path = std::string(path);
    const auto exact = scan->inspect_historical_versions_or_throw(exact_query);
    require(
        exact.source_evidence_set_digest.has_value() &&
            exact.source_payload_snapshot_digest.has_value() &&
            exact.retained_payload_reachability.has_value() &&
            exact.payload_present_count == std::optional<std::uint64_t>(1U) &&
            exact.restore_ready_count == std::optional<std::uint64_t>(1U) &&
            exact.entries.size() == 1U &&
            exact.entries.front().payload_present ==
                std::optional<bool>(true) &&
            exact.entries.front().restore_ready ==
                std::optional<bool>(true),
        "exact history inspection did not recover payload availability after namespace repair");

    anonsync::SyncReplicaHistoricalVersionQuery mismatched_mode = metadata_query;
    mismatched_mode.expected_source_cutpoint = exact.source_cutpoint();
    require_error(
        [&] {
            (void)scan->inspect_historical_versions_or_throw(
                mismatched_mode);
        },
        "cutpoint mode does not match",
        "metadata-only inspection accepted an exact-payload source cutpoint");
}


void test_historical_version_payload_reachability_and_evidence_cutpoint() {
    Fixture fixture("anonsync-folder-historical-version-retained-reachability");
    constexpr std::string_view path = "reachability/file.txt";
    const std::string predecessor_bytes = "retained predecessor bytes\n";
    const std::string current_bytes = "current visible bytes\n";
    const std::string orphan_bytes = "orphan diagnostic bytes\n";

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "historical reachability catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);

    write_file(fixture.shared_root / path, predecessor_bytes);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto predecessor_entry = find_entry(scan->snapshot_or_throw(), path);
    require(
        predecessor_entry.has_value(),
        "retained-reachability fixture lost its predecessor");

    write_file(fixture.shared_root / path, current_bytes);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto current_entry = find_entry(scan->snapshot_or_throw(), path);
    require(
        current_entry.has_value() &&
            current_entry->operation_id != predecessor_entry->operation_id,
        "retained-reachability fixture did not publish its successor");

    std::error_code remove_error;
    require(
        fs::remove(
            fixture.payload_root / predecessor_entry->content_sha256,
            remove_error) && !remove_error,
        "retained-reachability fixture could not remove its predecessor payload");
    const auto orphan = fixture.payload_store.put_payload_or_throw(orphan_bytes);
    require(
        orphan.content_sha256 == anonsync::sha256_hex(orphan_bytes),
        "retained-reachability fixture did not retain its unreferenced object");

    const anonsync::SyncReplicaActor parent_actor{
        "device-reachability-missing-parent", 81U};
    const anonsync::SyncReplicaActor child_actor{
        "device-reachability-pending-child", 82U};
    anonsync::SyncReplicaOperation missing_parent;
    missing_parent.folder_id = Fixture::folder_id;
    missing_parent.canonical_path = "reachability/pending.txt";
    missing_parent.kind = anonsync::SyncReplicaValueKind::File;
    missing_parent.size_bytes = 7U;
    missing_parent.content_sha256 = anonsync::sha256_hex("missing");
    missing_parent.dot = {parent_actor, 1U};
    missing_parent.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(missing_parent);

    anonsync::SyncReplicaOperation pending_child;
    pending_child.folder_id = Fixture::folder_id;
    pending_child.canonical_path = missing_parent.canonical_path;
    pending_child.kind = anonsync::SyncReplicaValueKind::File;
    pending_child.size_bytes = current_bytes.size();
    pending_child.content_sha256 = anonsync::sha256_hex(current_bytes);
    pending_child.dot = {child_actor, 1U};
    pending_child.causal_context = {
        {missing_parent.dot.actor, missing_parent.dot.counter}};
    pending_child.predecessor_operation_ids = {
        missing_parent.operation_id};
    pending_child.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(pending_child);
    require(
        fixture.replica.accept_remote_or_throw(pending_child) ==
                anonsync::SyncReplicaAdmission::InsertedPending &&
            restore_model(fixture.replica.snapshot_or_throw()).evidence_state(
                pending_child.operation_id) ==
                anonsync::SyncReplicaEvidenceState::PendingMissingDependency,
        "retained-reachability fixture did not preserve inactive file evidence");
    const auto retained_model = restore_model(fixture.replica.snapshot_or_throw());
    std::uint64_t visited_evidence = 0U;
    const auto noncopyable_visitor = [proof = std::make_unique<int>(17),
                                      &visited_evidence](
                                         const anonsync::SyncReplicaOperation&,
                                         anonsync::SyncReplicaEvidenceState) {
        if (*proof == 17) ++visited_evidence;
    };
    retained_model.for_each_evidence_operation(noncopyable_visitor);
    require(
        visited_evidence == 3U,
        "borrowed retained-evidence traversal copied, erased, or omitted its non-copyable visitor");

    const auto replica_before_pin = fixture.replica.snapshot_or_throw();
    const auto pin = scan->pin_historical_version_or_throw(
        predecessor_entry->operation_id);
    const auto replica_after_pin = fixture.replica.snapshot_or_throw();
    require(
        pin.disposition ==
                anonsync::SyncReplicaSqliteHistoricalVersionPinDisposition::
                    Pinned &&
            pin.operation_id == predecessor_entry->operation_id &&
            pin.pin_count == 1U &&
            replica_after_pin.historical_version_pins ==
                std::vector<std::string>{predecessor_entry->operation_id} &&
            replica_after_pin.historical_version_pin_set_digest ==
                pin.pin_set_digest &&
            replica_after_pin.operation_set_digest ==
                replica_before_pin.operation_set_digest &&
            replica_after_pin.evidence_set_digest ==
                replica_before_pin.evidence_set_digest &&
            replica_after_pin.visible_state_digest ==
                replica_before_pin.visible_state_digest,
        "explicit historical pin did not publish one isolated policy root");

    const fs::path transient_residue_a =
        fixture.payload_root /
        ".anonsync-publish-v1-0000000000000001-0000000000000002-0000000000000003.tmp";
    const fs::path transient_residue_b =
        fixture.payload_root /
        ".anonsync-publish-v1-0000000000000004-0000000000000005-0000000000000006.tmp";
    write_file(transient_residue_a, "temp");
    if (::chmod(transient_residue_a.c_str(), 0600) != 0) {
        fail("could not make retention transient residue private");
    }

    anonsync::SyncReplicaHistoricalVersionQuery exact_query;
    exact_query.canonical_path = std::string(path);
    const auto exact = scan->inspect_historical_versions_or_throw(exact_query);
    require(
        exact.source_evidence_set_digest.has_value() &&
            exact.source_evidence_set_digest->size() == 64U &&
            exact.source_historical_version_pin_set_digest ==
                pin.pin_set_digest &&
            exact.historical_version_pin_count == 1U &&
            exact.retained_payload_reachability.has_value() &&
            exact.entries.size() == 1U &&
            exact.entries.front().operation_id ==
                predecessor_entry->operation_id &&
            exact.entries.front().pinned &&
            exact.entries.front().payload_present ==
                std::optional<bool>(false),
        "exact reachability inspection lost its evidence cutpoint or path page");

    const auto& reachability = *exact.retained_payload_reachability;
    require(
        reachability.payload_entry_count == 2U &&
            reachability.payload_indexed_bytes ==
                current_bytes.size() + orphan_bytes.size() &&
            reachability.current_visible.file_operation_count == 1U &&
            reachability.current_visible.distinct_content_count == 1U &&
            reachability.current_visible.present_content_count == 1U &&
            reachability.current_visible.present_content_bytes ==
                current_bytes.size() &&
            reachability.current_visible.missing_content_count == 0U &&
            reachability.superseded_active.file_operation_count == 1U &&
            reachability.superseded_active.distinct_content_count == 1U &&
            reachability.superseded_active.present_content_count == 0U &&
            reachability.superseded_active.present_content_bytes == 0U &&
            reachability.superseded_active.missing_content_count == 1U &&
            reachability.inactive_evidence.file_operation_count == 1U &&
            reachability.inactive_evidence.distinct_content_count == 1U &&
            reachability.inactive_evidence.present_content_count == 1U &&
            reachability.inactive_evidence.present_content_bytes ==
                current_bytes.size() &&
            reachability.inactive_evidence.missing_content_count == 0U &&
            reachability.explicit_pins.file_operation_count == 1U &&
            reachability.explicit_pins.distinct_content_count == 1U &&
            reachability.explicit_pins.present_content_count == 0U &&
            reachability.explicit_pins.present_content_bytes == 0U &&
            reachability.explicit_pins.missing_content_count == 1U &&
            reachability.retained_union.file_operation_count == 3U &&
            reachability.retained_union.distinct_content_count == 2U &&
            reachability.retained_union.present_content_count == 1U &&
            reachability.retained_union.present_content_bytes ==
                current_bytes.size() &&
            reachability.retained_union.missing_content_count == 1U &&
            reachability.unreferenced_payload_count == 1U &&
            reachability.unreferenced_payload_bytes == orphan_bytes.size(),
        "retained reachability did not distinguish overlapping classes, missing history, and unreferenced objects");

    anonsync::SyncReplicaHistoricalVersionQuery metadata_query = exact_query;
    metadata_query.inspection_mode = anonsync::
        SyncReplicaHistoricalVersionInspectionMode::CausalMetadataOnly;
    const auto metadata =
        scan->inspect_historical_versions_or_throw(metadata_query);
    require(
        !metadata.source_evidence_set_digest.has_value() &&
            metadata.source_historical_version_pin_set_digest ==
                pin.pin_set_digest &&
            metadata.historical_version_pin_count == 1U &&
            !metadata.source_payload_snapshot_digest.has_value() &&
            !metadata.retained_payload_reachability.has_value() &&
            metadata.entries.size() == 1U &&
            metadata.entries.front().pinned,
        "metadata history browsing fabricated retained-payload authority");

    const auto exact_cutpoint = exact.source_cutpoint();
    require(
        exact_cutpoint.evidence_set_digest.has_value() &&
            anonsync::
                encode_sync_replica_historical_version_source_cutpoint_or_throw(
                    exact_cutpoint,
                    "retained reachability exact cutpoint").starts_with(
                        "v4:exact:"),
        "retained reachability did not emit an evidence-bound exact token");

    // The dry-run planner must project the same exact roots over physical
    // payloads rather than silently converting "unreferenced" into deletion
    // authority. The missing pinned predecessor remains visible only in the
    // reachability aggregate because no physical object exists to page.
    const auto retention_plan = scan->plan_payload_retention_or_throw();
    const std::string expected_candidate_set_digest =
        retention_unreferenced_candidate_set_digest_for_test(
            {{orphan.content_sha256,
              static_cast<std::uint64_t>(orphan_bytes.size())}});
    const std::string expected_durable_candidate_witness =
        retention_durable_candidate_witness_for_test(
            retention_plan, Fixture::folder_id,
            expected_candidate_set_digest);
    const std::string expected_deletion_free_mark_digest =
        retention_deletion_free_mark_digest_for_test(
            retention_plan, Fixture::folder_id,
            expected_candidate_set_digest);
    const std::string expected_writer_fenced_candidate_page_digest =
        retention_writer_fenced_candidate_page_digest_for_test(
            retention_plan, Fixture::folder_id);
    require(
        retention_plan.source_cutpoint() == exact_cutpoint &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.source_replica_database_incarnation_sha256) &&
            retention_plan.source_replica_database_recovery_epoch == 1U &&
            retention_plan.source_replica_state_generation ==
                fixture.replica.snapshot_or_throw().state_generation &&
            retention_plan.historical_version_pin_count == 1U &&
            retention_plan.payload_transient_entry_count == 1U &&
            retention_plan.payload_transient_bytes == 4U &&
            retention_plan.payload_transient_reserved_bytes == 4U &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.source_payload_transient_namespace_digest) &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.live_capability_process_store_scope_digest) &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.live_capability_process_store_scope_incarnation_digest) &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.live_capability_set_digest) &&
            retention_plan.live_snapshot_count == 0U &&
            retention_plan.live_opened_payload_count == 0U &&
            retention_plan.live_targeted_access_count == 0U &&
            retention_plan.live_mutation_batch_count == 0U &&
            retention_plan.distinct_live_opened_payload_root_count == 0U &&
            retention_plan.distinct_live_opened_payload_root_bytes == 0U &&
            !retention_plan.live_capabilities_may_reopen_all_current_payloads &&
            retention_plan.live_capability_rooted_physical_payload_count == 0U &&
            retention_plan.live_capability_rooted_physical_payload_bytes == 0U &&
            retention_plan.unreferenced_live_capability_rooted_payload_count == 0U &&
            retention_plan.unreferenced_live_capability_rooted_payload_bytes == 0U &&
            retention_plan.writer_fenced_observation &&
            retention_plan.cooperating_new_namespace_activity_excluded_during_observation &&
            retention_plan.writer_fenced_candidate_page_entry_count == 2U &&
            retention_plan.returned_unreferenced_candidate_count == 1U &&
            retention_plan.returned_candidate_payload_use_exclusive_available_count == 1U &&
            retention_plan.returned_candidate_payload_use_busy_count == 0U &&
            retention_plan.writer_fenced_candidate_page_digest ==
                expected_writer_fenced_candidate_page_digest &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.writer_fenced_candidate_page_digest) &&
            retention_plan.retained_payload_reachability == reachability &&
            retention_plan.current_or_explicit_pin.payload_count == 1U &&
            retention_plan.current_or_explicit_pin.payload_bytes ==
                current_bytes.size() &&
            retention_plan.retained_history_or_evidence.payload_count == 0U &&
            retention_plan.retained_history_or_evidence.payload_bytes == 0U &&
            retention_plan.unreferenced_by_retained_file_operations.payload_count == 1U &&
            retention_plan.unreferenced_by_retained_file_operations.payload_bytes ==
                orphan_bytes.size() &&
            retention_plan.unreferenced_candidate_set_digest ==
                expected_candidate_set_digest &&
            retention_plan.durable_candidate_witness_digest ==
                expected_durable_candidate_witness &&
            retention_plan.exact_deletion_free_mark_digest ==
                expected_deletion_free_mark_digest &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.unreferenced_candidate_set_digest) &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.durable_candidate_witness_digest) &&
            anonsync::is_lowercase_sha256_hex(
                retention_plan.exact_deletion_free_mark_digest) &&
            retention_plan.physical_payload_count_after_cursor == 2U &&
            !retention_plan.truncated &&
            !retention_plan.next_start_after_content_sha256.has_value() &&
            retention_plan.entries.size() == 2U,
        "retention planner did not reuse the exact reachability cutpoint and physical partition");
    require(
        retention_plan.entries[0].content_sha256 <
            retention_plan.entries[1].content_sha256,
        "retention planner did not order physical payloads by digest");
    const auto find_planned = [&](std::string_view digest)
        -> const anonsync::SyncReplicaRetentionPlanEntry* {
        const auto found = std::find_if(
            retention_plan.entries.begin(), retention_plan.entries.end(),
            [&](const anonsync::SyncReplicaRetentionPlanEntry& entry) {
                return entry.content_sha256 == digest;
            });
        return found == retention_plan.entries.end() ? nullptr : &*found;
    };
    const auto* current_planned =
        find_planned(anonsync::sha256_hex(current_bytes));
    const auto* orphan_planned = find_planned(orphan.content_sha256);
    require(
        current_planned != nullptr && current_planned->current_visible &&
            !current_planned->superseded_active &&
            current_planned->inactive_evidence &&
            !current_planned->explicit_pin &&
            !current_planned->same_process_store_live_capability &&
            current_planned->payload_use_disposition == anonsync::
                SyncReplicaRetentionPlanPayloadUseDisposition::NotApplicable &&
            current_planned->disposition == anonsync::
                SyncReplicaRetentionPlanDisposition::CurrentOrExplicitPin,
        "retention planner lost overlapping current and inactive-evidence roots");
    require(
        orphan_planned != nullptr && !orphan_planned->current_visible &&
            !orphan_planned->superseded_active &&
            !orphan_planned->inactive_evidence &&
            !orphan_planned->explicit_pin &&
            !orphan_planned->same_process_store_live_capability &&
            orphan_planned->payload_use_disposition == anonsync::
                SyncReplicaRetentionPlanPayloadUseDisposition::
                    ExclusiveAvailableAtCutpoint &&
            orphan_planned->disposition == anonsync::
                SyncReplicaRetentionPlanDisposition::
                    UnreferencedByRetainedFileOperations,
        "retention planner promoted an unreferenced physical object into a retained root");

    // Persist the policy under the exact writer-fenced snapshot which recomputes
    // the complete candidate witness. The metadata record must not enter either
    // physical-payload or transient accounting, and a monotonic SQLite
    // generation must reject a digest-level unpin/repin ABA.
    anonsync::SyncReplicaPayloadRetentionMarkRequest retention_mark_request;
    retention_mark_request.expected_source_cutpoint =
        retention_plan.source_cutpoint();
    retention_mark_request.
        expected_source_replica_database_incarnation_sha256 =
        retention_plan.source_replica_database_incarnation_sha256;
    retention_mark_request.expected_source_replica_database_recovery_epoch =
        retention_plan.source_replica_database_recovery_epoch;
    retention_mark_request.expected_source_replica_state_generation =
        retention_plan.source_replica_state_generation;
    retention_mark_request.expected_durable_candidate_witness_digest =
        retention_plan.durable_candidate_witness_digest;
    retention_mark_request.marked_at_unix_seconds = 1'800'000'000U;
    retention_mark_request.policy =
        anonsync::SyncReplicaFilePayloadRetentionPolicy{
            .minimum_grace_seconds = 86'400U,
            .maximum_candidate_payload_count = 1U,
            .maximum_candidate_payload_bytes = orphan_bytes.size(),
            .maximum_collection_payload_count = 1U,
            .maximum_collection_payload_bytes = orphan_bytes.size(),
        };

    // A policy outside this store's configured frontier is impossible before
    // any namespace fact matters. Independently lock the exact identity inode
    // while testing both invalid frontiers: the required capacity diagnostic
    // proves the owner rejected them before attempting a writer-fenced payload
    // scan. Unlike opening a mutation batch, this test lock performs no store
    // reconciliation and therefore cannot alter transient evidence itself.
    {
        auto impossible_count = retention_mark_request;
        impossible_count.policy.maximum_candidate_payload_count =
            fixture.payload_store.limits().max_entries + 1U;
        auto impossible_bytes = retention_mark_request;
        impossible_bytes.policy.maximum_candidate_payload_bytes =
            fixture.payload_store.limits().max_indexed_bytes + 1U;
        const fs::path identity_path =
            fixture.payload_root /
            ".anonsync-payload-store-identity-v2-reader-fence-v1";
        int identity_descriptor;
        do {
            identity_descriptor = ::open(
                identity_path.c_str(),
                O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        } while (identity_descriptor < 0 && errno == EINTR);
        if (identity_descriptor < 0) {
            fail("could not open retention capacity-preflight identity");
        }
        int lock_result;
        do {
            lock_result = ::flock(
                identity_descriptor, LOCK_EX | LOCK_NB);
        } while (lock_result != 0 && errno == EINTR);
        if (lock_result != 0) {
            (void)::close(identity_descriptor);
            fail("could not hold retention capacity-preflight identity lease");
        }
        try {
            require_error(
                [&] {
                    (void)scan->mark_payload_retention_or_throw(
                        impossible_count);
                },
                "candidate count exceeds store capacity",
                "retention policy spent payload-store work before rejecting an impossible count frontier");
            require_error(
                [&] {
                    (void)scan->mark_payload_retention_or_throw(
                        impossible_bytes);
                },
                "candidate bytes exceed store capacity",
                "retention policy spent payload-store work before rejecting an impossible byte frontier");
        } catch (...) {
            (void)::close(identity_descriptor);
            throw;
        }
        if (::close(identity_descriptor) != 0) {
            fail("could not release retention capacity-preflight identity lease");
        }
    }
    {
        const auto after_impossible_policy =
            fixture.payload_store.snapshot_or_throw();
        require(
            !after_impossible_policy.retention_mark_present(),
            "impossible retention policy published a durable mark");
        require(
            after_impossible_policy.snapshot_digest() ==
                retention_plan.source_payload_snapshot_digest,
            "impossible retention policy changed the physical payload snapshot");
        require(
            after_impossible_policy.transient_namespace_digest() ==
                retention_plan.source_payload_transient_namespace_digest,
            "impossible retention policy changed the transient payload namespace");
    }

    const auto first_retention_mark =
        scan->mark_payload_retention_or_throw(retention_mark_request);
    {
        const auto after_first_retention_mark =
            fixture.payload_store.snapshot_or_throw();
        require(
        !first_retention_mark.replaced_existing_file &&
            !first_retention_mark.replaced_usable_mark &&
            first_retention_mark.mark.generation == 1U &&
            first_retention_mark.mark.marked_at_unix_seconds ==
                retention_mark_request.marked_at_unix_seconds &&
            first_retention_mark.mark.policy ==
                retention_mark_request.policy &&
            first_retention_mark.mark.source_replica_state_generation ==
                retention_plan.source_replica_state_generation &&
            first_retention_mark.mark.source_operation_set_digest ==
                retention_plan.source_operation_set_digest &&
            first_retention_mark.mark.source_evidence_set_digest ==
                retention_plan.source_evidence_set_digest &&
            first_retention_mark.mark.
                    source_historical_version_pin_set_digest ==
                retention_plan.source_historical_version_pin_set_digest &&
            first_retention_mark.mark.source_visible_state_digest ==
                retention_plan.source_visible_state_digest &&
            first_retention_mark.mark.source_payload_snapshot_digest ==
                retention_plan.source_payload_snapshot_digest &&
            first_retention_mark.mark.
                    source_payload_transient_namespace_digest ==
                retention_plan.source_payload_transient_namespace_digest &&
            first_retention_mark.mark.unreferenced_candidate_set_digest ==
                retention_plan.unreferenced_candidate_set_digest &&
            first_retention_mark.mark.durable_candidate_witness_digest ==
                retention_plan.durable_candidate_witness_digest &&
            first_retention_mark.mark.
                    unreferenced_candidate_payload_count == 1U &&
            first_retention_mark.mark.
                    unreferenced_candidate_payload_bytes ==
                orphan_bytes.size() &&
            anonsync::is_lowercase_sha256_hex(
                first_retention_mark.mark.store_identity_sha256) &&
            anonsync::is_lowercase_sha256_hex(
                first_retention_mark.mark_digest) &&
            after_first_retention_mark.retention_mark_present() &&
            after_first_retention_mark.retention_mark_usable() &&
            after_first_retention_mark.retention_mark() ==
                std::optional(first_retention_mark.mark) &&
            after_first_retention_mark.retention_mark_digest() ==
                std::optional(first_retention_mark.mark_digest) &&
            after_first_retention_mark.snapshot_digest() ==
                retention_plan.source_payload_snapshot_digest &&
            after_first_retention_mark.transient_namespace_digest() ==
                retention_plan.source_payload_transient_namespace_digest &&
            after_first_retention_mark.entry_count() == 2U &&
            after_first_retention_mark.transient_entry_count() == 1U,
            "writer-fenced retention mark did not preserve exact source, policy, or payload accounting");
    }

    const auto aba_unpin = scan->unpin_historical_version_or_throw(
        predecessor_entry->operation_id);
    const auto aba_repin = scan->pin_historical_version_or_throw(
        predecessor_entry->operation_id);
    const auto replica_after_pin_aba = fixture.replica.snapshot_or_throw();
    require(
        aba_unpin.disposition == anonsync::
                SyncReplicaSqliteHistoricalVersionPinDisposition::Unpinned &&
            aba_repin.disposition == anonsync::
                SyncReplicaSqliteHistoricalVersionPinDisposition::Pinned &&
            replica_after_pin_aba.state_generation >
                retention_plan.source_replica_state_generation &&
            replica_after_pin_aba.operation_set_digest ==
                retention_plan.source_operation_set_digest &&
            replica_after_pin_aba.evidence_set_digest ==
                retention_plan.source_evidence_set_digest &&
            replica_after_pin_aba.historical_version_pin_set_digest ==
                retention_plan.source_historical_version_pin_set_digest &&
            replica_after_pin_aba.visible_state_digest ==
                retention_plan.source_visible_state_digest,
        "retention-mark ABA fixture did not restore identical digests at a newer generation");

    bool caught_retention_mark_generation_aba = false;
    try {
        (void)scan->mark_payload_retention_or_throw(
            retention_mark_request);
    } catch (const anonsync::SyncReplicaHistoricalVersionSourceChangedError&
                 error) {
        caught_retention_mark_generation_aba = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    RetentionMarkPublication,
            "retention-mark generation ABA reported the wrong source-change stage");
    }
    {
        const auto after_rejected_aba_mark =
            fixture.payload_store.snapshot_or_throw();
        require(
        caught_retention_mark_generation_aba &&
            after_rejected_aba_mark.retention_mark_usable() &&
            after_rejected_aba_mark.retention_mark()->generation == 1U &&
            after_rejected_aba_mark.retention_mark_digest() ==
                std::optional(first_retention_mark.mark_digest),
            "retention mark inherited grace across a digest-level replica ABA");
    }

    const auto current_retention_plan =
        scan->plan_payload_retention_or_throw();
    require(
        current_retention_plan.source_cutpoint() ==
                retention_plan.source_cutpoint() &&
            current_retention_plan.source_replica_database_incarnation_sha256 ==
                retention_plan.source_replica_database_incarnation_sha256 &&
            current_retention_plan.source_replica_database_recovery_epoch ==
                retention_plan.source_replica_database_recovery_epoch &&
            current_retention_plan.source_replica_state_generation ==
                replica_after_pin_aba.state_generation &&
            current_retention_plan.durable_candidate_witness_digest !=
                retention_plan.durable_candidate_witness_digest &&
            current_retention_plan.exact_deletion_free_mark_digest !=
                retention_plan.exact_deletion_free_mark_digest &&
            current_retention_plan.unreferenced_candidate_set_digest ==
                retention_plan.unreferenced_candidate_set_digest &&
            current_retention_plan.source_payload_snapshot_digest ==
                retention_plan.source_payload_snapshot_digest,
        "digest-level replica ABA did not advance the lineage-bound retention witnesses");

    auto replacement_mark_request = retention_mark_request;
    replacement_mark_request.expected_source_cutpoint =
        current_retention_plan.source_cutpoint();
    replacement_mark_request.
        expected_source_replica_database_incarnation_sha256 =
        current_retention_plan.source_replica_database_incarnation_sha256;
    replacement_mark_request.
        expected_source_replica_database_recovery_epoch =
        current_retention_plan.source_replica_database_recovery_epoch;
    replacement_mark_request.expected_source_replica_state_generation =
        current_retention_plan.source_replica_state_generation;
    replacement_mark_request.expected_durable_candidate_witness_digest =
        current_retention_plan.durable_candidate_witness_digest;
    ++replacement_mark_request.marked_at_unix_seconds;
    const auto replacement_retention_mark =
        scan->mark_payload_retention_or_throw(replacement_mark_request);
    require(
        replacement_retention_mark.replaced_existing_file &&
            replacement_retention_mark.replaced_usable_mark &&
            replacement_retention_mark.mark.generation == 2U &&
            replacement_retention_mark.mark.source_replica_state_generation ==
                current_retention_plan.source_replica_state_generation &&
            replacement_retention_mark.mark_digest !=
                first_retention_mark.mark_digest,
        "current retention mark did not conservatively replace the stale generation");

    auto stale_witness_mark_request = replacement_mark_request;
    stale_witness_mark_request.expected_durable_candidate_witness_digest[0] =
        stale_witness_mark_request.
                expected_durable_candidate_witness_digest[0] == '0'
            ? '1'
            : '0';
    bool caught_stale_retention_witness = false;
    try {
        (void)scan->mark_payload_retention_or_throw(
            stale_witness_mark_request);
    } catch (const anonsync::SyncReplicaHistoricalVersionSourceChangedError&
                 error) {
        caught_stale_retention_witness = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    RetentionMarkPublication,
            "stale retention candidate witness reported the wrong source-change stage");
    }
    {
        const auto after_stale_witness =
            fixture.payload_store.snapshot_or_throw();
        require(
        caught_stale_retention_witness &&
            after_stale_witness.retention_mark_usable() &&
            after_stale_witness.retention_mark()->generation == 2U &&
            after_stale_witness.retention_mark_digest() ==
                std::optional(replacement_retention_mark.mark_digest) &&
            after_stale_witness.snapshot_digest() ==
                retention_plan.source_payload_snapshot_digest,
            "stale candidate witness replaced the current durable retention mark");
    }

    // A snapshot issued for this exact process/store scope can reopen any
    // indexed payload after its construction lease is gone. The planner's own
    // snapshot is excluded, but every independent live snapshot must root the
    // complete physical namespace and change the exact mark. Replacing one
    // snapshot with another preserves aggregate count yet changes the exact
    // registration-set digest.
    std::string first_live_snapshot_set_digest;
    std::string first_live_snapshot_mark_digest;
    {
        auto external_snapshot = fixture.payload_store.snapshot_or_throw();
        const auto snapshot_rooted_plan =
            scan->plan_payload_retention_or_throw();
        first_live_snapshot_set_digest =
            snapshot_rooted_plan.live_capability_set_digest;
        first_live_snapshot_mark_digest =
            snapshot_rooted_plan.exact_deletion_free_mark_digest;
        require(
            snapshot_rooted_plan.live_capability_process_store_scope_digest ==
                    current_retention_plan.live_capability_process_store_scope_digest &&
                snapshot_rooted_plan.live_capability_process_store_scope_incarnation_digest ==
                current_retention_plan.live_capability_process_store_scope_incarnation_digest &&
                snapshot_rooted_plan.live_snapshot_count == 1U &&
                snapshot_rooted_plan.live_opened_payload_count == 0U &&
                snapshot_rooted_plan.live_targeted_access_count == 0U &&
                snapshot_rooted_plan.live_mutation_batch_count == 0U &&
                snapshot_rooted_plan.distinct_live_opened_payload_root_count == 0U &&
                snapshot_rooted_plan.distinct_live_opened_payload_root_bytes == 0U &&
                snapshot_rooted_plan.live_capabilities_may_reopen_all_current_payloads &&
                snapshot_rooted_plan.live_capability_rooted_physical_payload_count == 2U &&
                snapshot_rooted_plan.live_capability_rooted_physical_payload_bytes ==
                    current_bytes.size() + orphan_bytes.size() &&
                snapshot_rooted_plan.unreferenced_live_capability_rooted_payload_count == 1U &&
                snapshot_rooted_plan.unreferenced_live_capability_rooted_payload_bytes ==
                    orphan_bytes.size() &&
                snapshot_rooted_plan.live_capability_set_digest !=
                    current_retention_plan.live_capability_set_digest &&
                snapshot_rooted_plan.durable_candidate_witness_digest ==
                    current_retention_plan.durable_candidate_witness_digest &&
                snapshot_rooted_plan.exact_deletion_free_mark_digest !=
                    current_retention_plan.exact_deletion_free_mark_digest &&
                std::all_of(
                    snapshot_rooted_plan.entries.begin(),
                    snapshot_rooted_plan.entries.end(),
                    [](const anonsync::SyncReplicaRetentionPlanEntry& entry) {
                        return entry.same_process_store_live_capability;
                    }),
            "live same-process-store snapshot was not projected as an all-payload retention root");
    }
    {
        auto replacement_snapshot = fixture.payload_store.snapshot_or_throw();
        const auto replacement_rooted_plan =
            scan->plan_payload_retention_or_throw();
        require(
            replacement_rooted_plan.live_snapshot_count == 1U &&
                replacement_rooted_plan.live_capability_set_digest !=
                    first_live_snapshot_set_digest &&
                replacement_rooted_plan.durable_candidate_witness_digest ==
                    current_retention_plan.durable_candidate_witness_digest &&
                replacement_rooted_plan.exact_deletion_free_mark_digest !=
                    first_live_snapshot_mark_digest,
            "same-count live snapshot replacement aliased the exact capability-set cutpoint");
    }
    const auto after_snapshot_release_plan =
        scan->plan_payload_retention_or_throw();
    require(
        after_snapshot_release_plan.live_capability_set_digest ==
                current_retention_plan.live_capability_set_digest &&
            after_snapshot_release_plan.durable_candidate_witness_digest ==
                current_retention_plan.durable_candidate_witness_digest &&
            after_snapshot_release_plan.exact_deletion_free_mark_digest ==
                current_retention_plan.exact_deletion_free_mark_digest &&
            after_snapshot_release_plan.live_snapshot_count == 0U &&
            after_snapshot_release_plan.live_capability_rooted_physical_payload_count == 0U,
        "released same-process-store snapshot remained a retention root");

    // A separately opened owner over the same attested root and immutable
    // identity shares this process-store registry, while snapshot handoff
    // itself remains exact-owner-bound by the independent verification cache.
    {
        anonsync::SyncReplicaFilePayloadStore independent_owner(
            Fixture::folder_id, fixture.payload_root,
            anonsync::SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly,
            fixture.payload_store.limits(),
            "retention-plan independent payload-store owner");
        auto independent_snapshot = independent_owner.snapshot_or_throw();
        const auto independent_owner_rooted_plan =
            scan->plan_payload_retention_or_throw();
        require(
            independent_owner_rooted_plan
                    .live_capability_process_store_scope_digest ==
                    current_retention_plan.live_capability_process_store_scope_digest &&
                independent_owner_rooted_plan
                    .live_capability_process_store_scope_incarnation_digest ==
                    retention_plan
                        .live_capability_process_store_scope_incarnation_digest &&
                independent_owner_rooted_plan.live_snapshot_count == 1U &&
                independent_owner_rooted_plan
                    .live_capabilities_may_reopen_all_current_payloads &&
                independent_owner_rooted_plan
                    .live_capability_rooted_physical_payload_count == 2U &&
                std::all_of(
                    independent_owner_rooted_plan.entries.begin(),
                    independent_owner_rooted_plan.entries.end(),
                    [](const anonsync::SyncReplicaRetentionPlanEntry& entry) {
                        return entry.same_process_store_live_capability;
                    }),
            "independently opened same-process owner was absent from retention roots");
    }
    const auto after_independent_owner_release_plan =
        scan->plan_payload_retention_or_throw();
    require(
        after_independent_owner_release_plan.live_capability_set_digest ==
                current_retention_plan.live_capability_set_digest &&
            after_independent_owner_release_plan
                    .exact_deletion_free_mark_digest ==
                current_retention_plan.exact_deletion_free_mark_digest &&
            after_independent_owner_release_plan.live_snapshot_count == 0U,
        "released independent owner remained in the process-store retention cutpoint");

    // An opened payload descriptor is narrower: once its issuing snapshot is
    // destroyed, it roots only the exact digest/size object that the descriptor
    // can still consume. Use the otherwise-unreferenced object so this witness
    // cannot be confused with a causal File-operation root.
    anonsync::SyncReplicaOperation orphan_operation;
    orphan_operation.kind = anonsync::SyncReplicaValueKind::File;
    orphan_operation.content_sha256 = orphan.content_sha256;
    orphan_operation.size_bytes = orphan_bytes.size();
    {
        std::optional<anonsync::SyncReplicaFilePayloadStoreOpenedPayload>
            opened_orphan;
        {
            auto opening_snapshot = fixture.payload_store.snapshot_or_throw();
            opened_orphan.emplace(
                opening_snapshot.open_payload_for_operation_or_throw(
                    orphan_operation, "retention live opened orphan"));
        }
        const auto opened_rooted_plan =
            scan->plan_payload_retention_or_throw();
        const auto opened_entry = std::find_if(
            opened_rooted_plan.entries.begin(),
            opened_rooted_plan.entries.end(),
            [&](const anonsync::SyncReplicaRetentionPlanEntry& entry) {
                return entry.content_sha256 == orphan.content_sha256;
            });
        require(
            opened_rooted_plan.live_snapshot_count == 0U &&
                opened_rooted_plan.live_opened_payload_count == 1U &&
                opened_rooted_plan.live_targeted_access_count == 0U &&
                opened_rooted_plan.live_mutation_batch_count == 0U &&
                opened_rooted_plan.distinct_live_opened_payload_root_count == 1U &&
                opened_rooted_plan.distinct_live_opened_payload_root_bytes ==
                    orphan_bytes.size() &&
                !opened_rooted_plan.live_capabilities_may_reopen_all_current_payloads &&
                opened_rooted_plan.live_capability_rooted_physical_payload_count == 1U &&
                opened_rooted_plan.live_capability_rooted_physical_payload_bytes ==
                    orphan_bytes.size() &&
                opened_rooted_plan.unreferenced_live_capability_rooted_payload_count == 1U &&
                opened_rooted_plan.unreferenced_live_capability_rooted_payload_bytes ==
                    orphan_bytes.size() &&
                opened_entry != opened_rooted_plan.entries.end() &&
                opened_entry->same_process_store_live_capability &&
                opened_entry->payload_use_disposition == anonsync::
                    SyncReplicaRetentionPlanPayloadUseDisposition::
                        BusyAtCutpoint &&
                opened_entry->disposition == anonsync::
                    SyncReplicaRetentionPlanDisposition::
                        UnreferencedByRetainedFileOperations &&
                opened_rooted_plan.writer_fenced_candidate_page_entry_count == 2U &&
                opened_rooted_plan.returned_unreferenced_candidate_count == 1U &&
                opened_rooted_plan.returned_candidate_payload_use_exclusive_available_count == 0U &&
                opened_rooted_plan.returned_candidate_payload_use_busy_count == 1U &&
                opened_rooted_plan.writer_fenced_candidate_page_digest ==
                    retention_writer_fenced_candidate_page_digest_for_test(
                        opened_rooted_plan, Fixture::folder_id) &&
                opened_rooted_plan.writer_fenced_candidate_page_digest !=
                    current_retention_plan.writer_fenced_candidate_page_digest &&
                opened_rooted_plan.durable_candidate_witness_digest ==
                    current_retention_plan.durable_candidate_witness_digest &&
                opened_rooted_plan.exact_deletion_free_mark_digest !=
                    current_retention_plan.exact_deletion_free_mark_digest,
            "opened payload descriptor was not projected as one exact same-process-store live root");
    }
    const auto after_opened_release_plan =
        scan->plan_payload_retention_or_throw();
    require(
        after_opened_release_plan.live_capability_set_digest ==
                current_retention_plan.live_capability_set_digest &&
            after_opened_release_plan.exact_deletion_free_mark_digest ==
                current_retention_plan.exact_deletion_free_mark_digest &&
            after_opened_release_plan.live_opened_payload_count == 0U &&
            after_opened_release_plan.live_capability_rooted_physical_payload_count == 0U &&
            after_opened_release_plan.writer_fenced_candidate_page_entry_count == 2U &&
            after_opened_release_plan.returned_unreferenced_candidate_count == 1U &&
            after_opened_release_plan.returned_candidate_payload_use_exclusive_available_count == 1U &&
            after_opened_release_plan.returned_candidate_payload_use_busy_count == 0U &&
            after_opened_release_plan.writer_fenced_candidate_page_digest ==
                current_retention_plan.writer_fenced_candidate_page_digest,
        "released opened payload descriptor remained a retention root");

    anonsync::SyncReplicaRetentionPlanQuery first_plan_page;
    first_plan_page.maximum_entries = 1U;
    const auto first_page =
        scan->plan_payload_retention_or_throw(first_plan_page);
    require(
        first_page.entries.size() == 1U && first_page.truncated &&
            first_page.writer_fenced_candidate_page_entry_count == 1U &&
            first_page.entry_limit_frontier_reached &&
            first_page.next_start_after_content_sha256 ==
                std::optional<std::string>(
                    first_page.entries.front().content_sha256) &&
            first_page.physical_payload_count_after_cursor == 2U &&
            first_page.writer_fenced_candidate_page_digest ==
                retention_writer_fenced_candidate_page_digest_for_test(
                    first_page, Fixture::folder_id) &&
            first_page.returned_unreferenced_candidate_count ==
                first_page.returned_candidate_payload_use_exclusive_available_count +
                    first_page.returned_candidate_payload_use_busy_count,
        "retention planner did not expose one exact bounded digest page");
    anonsync::SyncReplicaRetentionPlanQuery second_plan_page;
    second_plan_page.maximum_entries = 1U;
    second_plan_page.start_after_content_sha256 =
        first_page.next_start_after_content_sha256;
    second_plan_page.expected_source_cutpoint = first_page.source_cutpoint();
    const auto second_page =
        scan->plan_payload_retention_or_throw(second_plan_page);
    require(
        second_page.source_cutpoint() == first_page.source_cutpoint() &&
            first_page.unreferenced_candidate_set_digest ==
                current_retention_plan.unreferenced_candidate_set_digest &&
            second_page.unreferenced_candidate_set_digest ==
                current_retention_plan.unreferenced_candidate_set_digest &&
            first_page.exact_deletion_free_mark_digest ==
                current_retention_plan.exact_deletion_free_mark_digest &&
            second_page.exact_deletion_free_mark_digest ==
                current_retention_plan.exact_deletion_free_mark_digest &&
            second_page.entries.size() == 1U && !second_page.truncated &&
            second_page.writer_fenced_candidate_page_entry_count == 1U &&
            !second_page.next_start_after_content_sha256.has_value() &&
            second_page.physical_payload_count_after_cursor == 1U &&
            second_page.writer_fenced_candidate_page_digest ==
                retention_writer_fenced_candidate_page_digest_for_test(
                    second_page, Fixture::folder_id) &&
            second_page.returned_unreferenced_candidate_count ==
                second_page.returned_candidate_payload_use_exclusive_available_count +
                    second_page.returned_candidate_payload_use_busy_count &&
            first_page.returned_unreferenced_candidate_count +
                    second_page.returned_unreferenced_candidate_count ==
                1U &&
            first_page.returned_candidate_payload_use_exclusive_available_count +
                    second_page.returned_candidate_payload_use_exclusive_available_count ==
                1U &&
            first_page.returned_candidate_payload_use_busy_count == 0U &&
            second_page.returned_candidate_payload_use_busy_count == 0U &&
            first_page.writer_fenced_candidate_page_digest !=
                second_page.writer_fenced_candidate_page_digest &&
            first_page.entries.front().content_sha256 <
                second_page.entries.front().content_sha256,
        "retention planner did not resume exactly with one page-invariant mark witness");

    fs::rename(transient_residue_a, transient_residue_b);
    anonsync::SyncReplicaRetentionPlanQuery transient_drift_query;
    transient_drift_query.expected_source_cutpoint =
        first_page.source_cutpoint();
    bool caught_transient_identity_change = false;
    try {
        (void)scan->plan_payload_retention_or_throw(transient_drift_query);
    } catch (const anonsync::SyncReplicaHistoricalVersionSourceChangedError&
                 error) {
        caught_transient_identity_change = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::PayloadSnapshot,
            "same-size transient identity drift reported the wrong source-change stage");
    }
    require(
        caught_transient_identity_change,
        "same-count same-byte transient identity drift preserved a stale retention cutpoint");
    fs::rename(transient_residue_b, transient_residue_a);

    auto stale_plan_cutpoint = first_page.source_cutpoint();
    stale_plan_cutpoint.operation_set_digest = std::string(64U, '0');
    anonsync::SyncReplicaRetentionPlanQuery stale_plan_query;
    stale_plan_query.expected_source_cutpoint = stale_plan_cutpoint;
    bool caught_stale_plan = false;
    try {
        (void)scan->plan_payload_retention_or_throw(stale_plan_query);
    } catch (const anonsync::SyncReplicaHistoricalVersionSourceChangedError&
                 error) {
        caught_stale_plan = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    OperationSetBeforePayloadObservation,
            "stale retention-plan source token reported the wrong stage");
    }
    require(
        caught_stale_plan,
        "retention planner accepted a stale operation-set cutpoint");

    auto pre_pin_exact_cutpoint = exact_cutpoint;
    pre_pin_exact_cutpoint.historical_version_pin_set_digest.reset();
    exact_query.expected_source_cutpoint = pre_pin_exact_cutpoint;
    bool caught_unbound_legacy_pin_set = false;
    try {
        (void)scan->inspect_historical_versions_or_throw(exact_query);
    } catch (const anonsync::
                 SyncReplicaHistoricalVersionSourceChangedError& error) {
        caught_unbound_legacy_pin_set = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    HistoricalVersionPinSetBeforePayloadObservation,
            "legacy source token with live pins reported the wrong stage");
    }
    require(
        caught_unbound_legacy_pin_set,
        "pre-pin source token treated a nonempty retention set as a wildcard");
    exact_query.expected_source_cutpoint.reset();

    const auto unpinned = scan->unpin_historical_version_or_throw(
        predecessor_entry->operation_id);
    require(
        unpinned.disposition ==
                anonsync::SyncReplicaSqliteHistoricalVersionPinDisposition::
                    Unpinned &&
            unpinned.pin_count == 0U,
        "explicit historical unpin did not remove the policy root");
    const fs::path pin_drift_poison =
        fixture.payload_root / "unexpected-pin-drift-entry";
    write_file(pin_drift_poison, "must remain unobserved");
    exact_query.expected_source_cutpoint = exact_cutpoint;
    bool caught_pin_change = false;
    try {
        (void)scan->inspect_historical_versions_or_throw(exact_query);
    } catch (const anonsync::
                 SyncReplicaHistoricalVersionSourceChangedError& error) {
        caught_pin_change = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    HistoricalVersionPinSetBeforePayloadObservation,
            "retention-pin drift reported the wrong source stage");
    }
    require(
        caught_pin_change,
        "retention-pin drift reached the payload namespace instead of failing at the replica cutpoint");
    require(
        fs::remove(pin_drift_poison),
        "retention-pin drift fixture could not remove its negative control");
    const auto repinned = scan->pin_historical_version_or_throw(
        predecessor_entry->operation_id);
    require(
        repinned.disposition ==
                anonsync::SyncReplicaSqliteHistoricalVersionPinDisposition::
                    Pinned &&
            repinned.pin_set_digest == pin.pin_set_digest,
        "repeating the exact pin did not restore its canonical set digest");

    anonsync::SyncReplicaOperation second_pending = pending_child;
    second_pending.canonical_path = "reachability/second-pending.txt";
    second_pending.dot = {
        anonsync::SyncReplicaActor{"device-reachability-second-child", 83U},
        1U};
    second_pending.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(second_pending);
    require(
        fixture.replica.accept_remote_or_throw(second_pending) ==
            anonsync::SyncReplicaAdmission::InsertedPending,
        "retained-reachability fixture did not advance inactive evidence only");

    const fs::path unexpected =
        fixture.payload_root / "unexpected-reachability-entry";
    write_file(unexpected, "not a payload object");
    exact_query.expected_source_cutpoint = exact_cutpoint;
    bool caught_evidence_change = false;
    try {
        (void)scan->inspect_historical_versions_or_throw(exact_query);
    } catch (const anonsync::
                 SyncReplicaHistoricalVersionSourceChangedError& error) {
        caught_evidence_change = true;
        require(
            error.stage() == anonsync::
                SyncReplicaHistoricalVersionSourceChangeStage::
                    EvidenceSetBeforePayloadObservation,
            "inactive-evidence drift reported the wrong exact source stage");
    }
    require(
        caught_evidence_change,
        "inactive-evidence drift reached the payload namespace instead of failing at the evidence cutpoint");
    require(
        fs::remove(unexpected),
        "retained-reachability fixture could not remove its negative-control entry");
}

void test_retention_witness_binds_exact_replica_database_incarnation() {
    Fixture fixture("anonsync-retention-database-incarnation");
    const std::string orphan_bytes = "database-lineage-orphan";
    const auto orphan = fixture.payload_store.put_payload_or_throw(orphan_bytes);

    anonsync::SyncSqliteDb second_replica_db = open_database(
        fixture.temporary.path() / "replica-second.sqlite3",
        "second retention replica database");
    anonsync::SyncReplicaSqliteOwner second_replica(
        second_replica_db.db, Fixture::folder_id, Fixture::local_actor, {},
        "second retention replica owner",
        std::make_unique<TestOutboxClockSource>());
    anonsync::SyncSqliteDb first_catalog_db = open_database(
        fixture.temporary.path() / "catalog-first.sqlite3",
        "first retention catalog database");
    anonsync::SyncSqliteDb second_catalog_db = open_database(
        fixture.temporary.path() / "catalog-second.sqlite3",
        "second retention catalog database");
    auto first_scan = std::make_unique<anonsync::SyncReplicaFolderScanOwner>(
        first_catalog_db.db, Fixture::folder_id, fixture.shared_root,
        fixture.replica, fixture.payload_store, Fixture::scan_limits(),
        "first retention lineage scan owner");
    auto second_scan = std::make_unique<anonsync::SyncReplicaFolderScanOwner>(
        second_catalog_db.db, Fixture::folder_id, fixture.shared_root,
        second_replica, fixture.payload_store, Fixture::scan_limits(),
        "second retention lineage scan owner");

    const auto first = first_scan->plan_payload_retention_or_throw();
    const auto second = second_scan->plan_payload_retention_or_throw();
    require(
        first.source_cutpoint() == second.source_cutpoint() &&
            first.source_replica_state_generation ==
                second.source_replica_state_generation &&
            first.source_operation_set_digest ==
                second.source_operation_set_digest &&
            first.source_evidence_set_digest == second.source_evidence_set_digest &&
            first.source_historical_version_pin_set_digest ==
                second.source_historical_version_pin_set_digest &&
            first.source_visible_state_digest ==
                second.source_visible_state_digest &&
            first.source_payload_snapshot_digest ==
                second.source_payload_snapshot_digest &&
            first.unreferenced_candidate_set_digest ==
                second.unreferenced_candidate_set_digest &&
            first.unreferenced_by_retained_file_operations ==
                second.unreferenced_by_retained_file_operations &&
            first.unreferenced_by_retained_file_operations.payload_count == 1U &&
            first.unreferenced_by_retained_file_operations.payload_bytes ==
                orphan_bytes.size(),
        "independent retention databases did not begin with identical causal and payload facts");
    require(
        anonsync::is_lowercase_sha256_hex(
            first.source_replica_database_incarnation_sha256) &&
            anonsync::is_lowercase_sha256_hex(
                second.source_replica_database_incarnation_sha256) &&
            first.source_replica_database_incarnation_sha256 !=
                second.source_replica_database_incarnation_sha256 &&
            first.source_replica_database_recovery_epoch == 1U &&
            second.source_replica_database_recovery_epoch == 1U &&
            first.durable_candidate_witness_digest !=
                second.durable_candidate_witness_digest &&
            first.exact_deletion_free_mark_digest !=
                second.exact_deletion_free_mark_digest &&
            first.writer_fenced_candidate_page_digest !=
                second.writer_fenced_candidate_page_digest,
        "independent identical replica databases aliased retention authority");

    anonsync::SyncReplicaPayloadRetentionMarkRequest stale_request;
    stale_request.expected_source_cutpoint = first.source_cutpoint();
    stale_request.expected_source_replica_database_incarnation_sha256 =
        first.source_replica_database_incarnation_sha256;
    stale_request.expected_source_replica_database_recovery_epoch =
        first.source_replica_database_recovery_epoch;
    stale_request.expected_source_replica_state_generation =
        first.source_replica_state_generation;
    stale_request.expected_durable_candidate_witness_digest =
        first.durable_candidate_witness_digest;
    stale_request.marked_at_unix_seconds = 1'800'000'001U;
    stale_request.policy = anonsync::SyncReplicaFilePayloadRetentionPolicy{
        .minimum_grace_seconds = 86'400U,
        .maximum_candidate_payload_count = 1U,
        .maximum_candidate_payload_bytes = orphan.size_bytes,
        .maximum_collection_payload_count = 1U,
        .maximum_collection_payload_bytes = orphan.size_bytes,
    };

    bool caught_foreign_database = false;
    {
        auto exclusive_payload_mutation =
            fixture.payload_store.begin_mutation_batch_or_throw();
        try {
            (void)second_scan->mark_payload_retention_or_throw(stale_request);
        } catch (const anonsync::SyncReplicaHistoricalVersionSourceChangedError&
                     error) {
            caught_foreign_database = true;
            require(
                error.stage() == anonsync::
                    SyncReplicaHistoricalVersionSourceChangeStage::
                        RetentionMarkPublication,
                "foreign database retention request reported the wrong stage");
        }
    }
    const auto before_recovery = second_replica.snapshot_or_throw();
    const auto recovery = second_replica.advance_database_recovery_epoch_or_throw(
        before_recovery.database_incarnation_sha256,
        before_recovery.database_recovery_epoch, before_recovery.cutpoint_digest);
    require(
        recovery.database_incarnation_sha256 ==
                before_recovery.database_incarnation_sha256 &&
            recovery.previous_database_recovery_epoch == 1U &&
            recovery.database_recovery_epoch == 2U &&
            recovery.state_generation == before_recovery.state_generation + 1U,
        "explicit replica recovery did not advance one exact lineage epoch");

    anonsync::SyncReplicaPayloadRetentionMarkRequest stale_epoch_request;
    stale_epoch_request.expected_source_cutpoint = second.source_cutpoint();
    stale_epoch_request.expected_source_replica_database_incarnation_sha256 =
        second.source_replica_database_incarnation_sha256;
    stale_epoch_request.expected_source_replica_database_recovery_epoch =
        second.source_replica_database_recovery_epoch;
    stale_epoch_request.expected_source_replica_state_generation =
        second.source_replica_state_generation;
    stale_epoch_request.expected_durable_candidate_witness_digest =
        second.durable_candidate_witness_digest;
    stale_epoch_request.marked_at_unix_seconds = 1'800'000'002U;
    stale_epoch_request.policy = stale_request.policy;

    bool caught_stale_recovery_epoch = false;
    {
        auto exclusive_payload_mutation =
            fixture.payload_store.begin_mutation_batch_or_throw();
        try {
            (void)second_scan->mark_payload_retention_or_throw(
                stale_epoch_request);
        } catch (const anonsync::
                     SyncReplicaHistoricalVersionSourceChangedError& error) {
            caught_stale_recovery_epoch = true;
            require(
                error.stage() == anonsync::
                    SyncReplicaHistoricalVersionSourceChangeStage::
                        RetentionMarkPublication,
                "stale recovery-epoch retention request reported the wrong stage");
        }
    }

    const auto after_recovery =
        second_scan->plan_payload_retention_or_throw();
    require(
        after_recovery.source_cutpoint() == second.source_cutpoint() &&
            after_recovery.source_replica_database_incarnation_sha256 ==
                second.source_replica_database_incarnation_sha256 &&
            after_recovery.source_replica_database_recovery_epoch == 2U &&
            after_recovery.source_replica_state_generation ==
                second.source_replica_state_generation + 1U &&
            after_recovery.source_operation_set_digest ==
                second.source_operation_set_digest &&
            after_recovery.source_evidence_set_digest ==
                second.source_evidence_set_digest &&
            after_recovery.source_historical_version_pin_set_digest ==
                second.source_historical_version_pin_set_digest &&
            after_recovery.source_visible_state_digest ==
                second.source_visible_state_digest &&
            after_recovery.source_payload_snapshot_digest ==
                second.source_payload_snapshot_digest &&
            after_recovery.unreferenced_candidate_set_digest ==
                second.unreferenced_candidate_set_digest &&
            after_recovery.durable_candidate_witness_digest !=
                second.durable_candidate_witness_digest &&
            after_recovery.writer_fenced_candidate_page_digest !=
                second.writer_fenced_candidate_page_digest &&
            after_recovery.exact_deletion_free_mark_digest !=
                second.exact_deletion_free_mark_digest,
        "explicit replica recovery epoch did not invalidate retention authority while preserving causal and payload facts");

    const auto after = fixture.payload_store.snapshot_or_throw();
    require(
        caught_foreign_database && caught_stale_recovery_epoch &&
            after.retention_mark_observation_known() &&
            !after.retention_mark_present() &&
            !after.retention_mark_usable() &&
            !after.retention_mark().has_value() &&
            !after.retention_mark_digest().has_value(),
        "foreign or stale-recovery retention evidence reached payload observation or durable mark publication");
}

void test_historical_version_restore_from_tombstone() {
    Fixture fixture("anonsync-folder-historical-version-tombstone-restore");
    constexpr std::string_view path = "deleted/report.txt";
    const std::string bytes = "recover deleted report\n";

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(),
        "historical-version tombstone catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);

    write_file(fixture.shared_root / path, bytes);
    const auto seeded = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto seeded_entry = find_entry(scan->snapshot_or_throw(), path);
    const auto seeded_model = restore_model(fixture.replica.snapshot_or_throw());
    const auto historical = seeded_entry.has_value()
        ? seeded_model.operation_by_id(seeded_entry->operation_id)
        : std::nullopt;
    require(
        seeded.local_published_count == 1U && historical.has_value() &&
            historical->kind == anonsync::SyncReplicaValueKind::File &&
            historical->content_sha256 == anonsync::sha256_hex(bytes),
        "deleted-version restore fixture did not publish its file predecessor");

    require(
        fs::remove(fixture.shared_root / path),
        "deleted-version restore fixture could not remove its visible file");
    const auto deleted = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    const auto tombstone_entry = find_entry(scan->snapshot_or_throw(), path);
    const auto tombstone_model = restore_model(
        fixture.replica.snapshot_or_throw());
    const auto tombstone = tombstone_entry.has_value()
        ? tombstone_model.operation_by_id(tombstone_entry->operation_id)
        : std::nullopt;
    require(
        deleted.local_published_count == 1U && tombstone.has_value() &&
            tombstone->kind == anonsync::SyncReplicaValueKind::Tombstone &&
            anonsync::sync_replica_operation_supersedes(
                *tombstone, *historical) &&
            !fs::exists(fixture.shared_root / path),
        "deleted-version restore fixture did not publish one causal tombstone");

    const auto inventory = scan->inspect_historical_versions_or_throw();
    const auto candidate = std::find_if(
        inventory.entries.begin(), inventory.entries.end(),
        [&](const anonsync::SyncReplicaHistoricalVersionEntry& entry) {
            return entry.operation_id == historical->operation_id;
        });
    require(
        candidate != inventory.entries.end() &&
            candidate->payload_present == std::optional<bool>(true) &&
            candidate->restore_ready == std::optional<bool>(true) &&
            candidate->current_primary_kind ==
                anonsync::SyncReplicaValueKind::Tombstone &&
            candidate->current_primary_operation_id ==
                tombstone->operation_id,
        "deleted-version inspection did not expose the exact restorable predecessor behind the tombstone");

    const auto restored = scan->restore_historical_version_or_throw(
        anonsync::SyncReplicaHistoricalVersionRestoreRequest{
            .operation_id = historical->operation_id,
            .expected_current_operation_id = tombstone->operation_id,
        });
    require(
        restored.disposition ==
                anonsync::SyncReplicaHistoricalVersionRestoreDisposition::
                    Published &&
            restored.historical_operation == *historical &&
            restored.replaced_visible_operation == *tombstone &&
            restored.restored_operation.operation_id !=
                historical->operation_id &&
            restored.restored_operation.operation_id !=
                tombstone->operation_id &&
            restored.restored_operation.content_sha256 ==
                historical->content_sha256 &&
            anonsync::sync_replica_operation_supersedes(
                restored.restored_operation, *tombstone) &&
            read_file(fixture.shared_root / path) == bytes,
        "deleted-version restore did not create exact bytes under one new causal successor");
}

void test_rev0951_cyclic_catalog_migrates_cursor_and_resets_sweep() {
    Fixture fixture("anonsync-folder-scan-v4-migration");
    anonsync::SyncReplicaModel remote(
        Fixture::folder_id, {"device-folder-scan-v4-migration", 771U});
    for (const std::string path : {"a.txt", "b.txt", "c.txt"}) {
        const std::string bytes = "unavailable v4 bytes for " + path;
        const auto operation = remote.create_local_file_or_throw(
            path, bytes.size(), anonsync::sha256_hex(bytes));
        require(
            fixture.replica.accept_remote_or_throw(operation) ==
                anonsync::SyncReplicaAdmission::InsertedActive,
            "v4 migration fixture rejected remote evidence");
    }

    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "v4 migration catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto limits = Fixture::pass_limits();
    limits.maximum_remote_inspection_paths = 2U;
    const auto partial = scan->run_convergence_pass_or_throw(limits);
    const auto v5_snapshot = scan->snapshot_or_throw();
    const auto retained_progress = scan->scan_progress_snapshot_or_throw();
    require(
        partial.remote_apply_resume_after_path == "b.txt" &&
            !partial.completed_remote_inspection_sweep &&
            partial.remote_inspection_sweep_had_unresolved_paths &&
            retained_progress.remote_apply_resume_after_path == "b.txt" &&
            !retained_progress
                 .remote_inspection_sweep_basis_digest.empty() &&
            retained_progress
                .remote_inspection_sweep_started_after_path.empty() &&
            retained_progress.remote_inspection_sweep_seen_path_count == 2U &&
            retained_progress
                .remote_inspection_sweep_had_unresolved_paths,
        "v4 migration fixture did not retain cursor plus active sweep state");
    scan.reset();

    const std::string v4_digest =
        cyclic_catalog_digest_for_test(v5_snapshot);
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "BEGIN IMMEDIATE;"
        "ALTER TABLE sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v5_fixture;"
        "DROP TABLE sync_replica_folder_catalog_remote_apply_progress;"
        "DROP TABLE sync_replica_folder_catalog_selection_rules;"
        "DROP INDEX sync_replica_folder_catalog_file_content;"
        "CREATE TABLE sync_replica_folder_catalog_meta("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "schema_version INTEGER NOT NULL CHECK(schema_version=4),"
        "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
        "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
        "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
        "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
        "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
        "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
        "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
        "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
        "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
        "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT;"
        "CREATE TABLE sync_replica_folder_catalog_remote_apply_progress("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "resume_after_path TEXT NOT NULL CHECK(length(resume_after_path)<=4096)) STRICT;",
        "v4 migration fixture schema");
    anonsync::SyncSqliteStmt insert_meta = anonsync::sqlite_prepare_or_throw(
        catalog_db.db,
        "INSERT INTO sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest) "
        "SELECT id,4,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,? "
        "FROM sync_replica_folder_catalog_meta_v5_fixture WHERE id=1;",
        "v4 migration fixture metadata prepare");
    anonsync::sqlite_bind_text_or_throw(
        insert_meta.stmt, 1, v4_digest, "v4 migration fixture");
    anonsync::sqlite_step_done_or_throw(
        insert_meta.stmt, "v4 migration fixture metadata step");
    anonsync::SyncSqliteStmt insert_progress =
        anonsync::sqlite_prepare_or_throw(
            catalog_db.db,
            "INSERT INTO sync_replica_folder_catalog_remote_apply_progress("
            "id,resume_after_path) VALUES(1,?);",
            "v4 migration fixture progress prepare");
    anonsync::sqlite_bind_text_or_throw(
        insert_progress.stmt, 1,
        retained_progress.remote_apply_resume_after_path,
        "v4 migration fixture");
    anonsync::sqlite_step_done_or_throw(
        insert_progress.stmt, "v4 migration fixture progress step");
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "DROP TABLE sync_replica_folder_catalog_meta_v5_fixture;COMMIT;",
        "v4 migration fixture commit");

    scan = fixture.make_scan_owner(catalog_db);
    const auto migrated = scan->snapshot_or_throw();
    const auto migrated_progress = scan->scan_progress_snapshot_or_throw();
    auto expected = v5_snapshot;
    expected.catalog_digest = migrated.catalog_digest;
    auto expected_progress = retained_progress;
    expected_progress.remote_inspection_sweep_basis_digest.clear();
    expected_progress.remote_inspection_sweep_started_after_path.clear();
    expected_progress.remote_inspection_sweep_seen_path_count = 0U;
    expected_progress.remote_inspection_sweep_had_unresolved_paths = false;
    require(
        migrated == expected && migrated.catalog_digest != v4_digest &&
            migrated_progress == expected_progress,
        "rev0951 migration changed catalog, scan journal, or remote cursor authority");

    anonsync::SyncSqliteStmt schema = anonsync::sqlite_prepare_or_throw(
        catalog_db.db,
        "SELECT m.schema_version,r.resume_after_path,"
        "r.inspection_sweep_basis_digest,"
        "r.inspection_sweep_started_after_path,"
        "r.inspection_sweep_seen_path_count,"
        "r.inspection_sweep_had_unresolved_paths "
        "FROM sync_replica_folder_catalog_meta AS m "
        "JOIN sync_replica_folder_catalog_remote_apply_progress AS r "
        "ON m.id=r.id WHERE m.id=1;",
        "v4 migrated schema prepare");
    require(
        sqlite3_step(schema.stmt) == SQLITE_ROW &&
            sqlite3_column_int64(schema.stmt, 0) == 7 &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(schema.stmt, 1))) == "b.txt" &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(schema.stmt, 2))).empty() &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(schema.stmt, 3))).empty() &&
            sqlite3_column_int64(schema.stmt, 4) == 0 &&
            sqlite3_column_int64(schema.stmt, 5) == 0 &&
            sqlite3_step(schema.stmt) == SQLITE_DONE,
        "rev0951 migration did not preserve the v4 cursor at v7 indexed sweep genesis");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    require(
        scan->snapshot_or_throw() == migrated &&
            scan->scan_progress_snapshot_or_throw() == migrated_progress,
        "rev0951 migration was not a stable one-time upgrade");
}

void test_rev0950_fair_scan_catalog_migrates_without_losing_journal() {
    Fixture fixture("anonsync-folder-scan-v3-migration");
    write_file(fixture.shared_root / "a.txt", "retained fair-scan prefix");
    write_file(fixture.shared_root / "z.txt", "deferred fair-scan suffix");
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "v3 migration catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    auto limits = Fixture::pass_limits();
    limits.maximum_local_scan_segment_regular_files = 1U;
    const auto partial = scan->run_convergence_pass_or_throw(limits);
    const auto v4_snapshot = scan->snapshot_or_throw();
    const auto retained_progress = scan->scan_progress_snapshot_or_throw();
    require(
        !partial.completed_local_scan_epoch &&
            retained_progress.seen_path_count == 1U &&
            retained_progress.resume_after_path == "a.txt" &&
            retained_progress.remote_apply_resume_after_path == "a.txt",
        "v3 migration fixture did not retain a non-genesis scan journal");
    scan.reset();

    const std::string v3_digest =
        fair_scan_catalog_digest_for_test(v4_snapshot);
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "BEGIN IMMEDIATE;"
        "DROP TABLE sync_replica_folder_catalog_remote_apply_progress;"
        "DROP TABLE sync_replica_folder_catalog_selection_rules;"
        "DROP INDEX sync_replica_folder_catalog_file_content;"
        "ALTER TABLE sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v4_fixture;"
        "CREATE TABLE sync_replica_folder_catalog_meta("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "schema_version INTEGER NOT NULL CHECK(schema_version=3),"
        "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
        "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
        "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
        "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
        "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
        "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
        "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
        "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
        "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
        "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT;",
        "v3 migration fixture schema");
    anonsync::SyncSqliteStmt insert = anonsync::sqlite_prepare_or_throw(
        catalog_db.db,
        "INSERT INTO sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest) "
        "SELECT id,3,folder_id,absolute_root_path,root_attestation_digest,"
        "state_generation,max_catalog_entries,max_catalog_path_bytes,"
        "max_payload_bytes,entry_count,catalog_path_bytes,? "
        "FROM sync_replica_folder_catalog_meta_v4_fixture WHERE id=1;",
        "v3 migration fixture metadata prepare");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 1, v3_digest, "v3 migration fixture");
    anonsync::sqlite_step_done_or_throw(
        insert.stmt, "v3 migration fixture metadata step");
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "DROP TABLE sync_replica_folder_catalog_meta_v4_fixture;COMMIT;",
        "v3 migration fixture commit");

    scan = fixture.make_scan_owner(catalog_db);
    const auto migrated = scan->snapshot_or_throw();
    const auto migrated_progress = scan->scan_progress_snapshot_or_throw();
    auto expected_migrated_progress = retained_progress;
    expected_migrated_progress.remote_apply_resume_after_path.clear();
    expected_migrated_progress
        .remote_inspection_sweep_basis_digest.clear();
    expected_migrated_progress
        .remote_inspection_sweep_started_after_path.clear();
    expected_migrated_progress
        .remote_inspection_sweep_seen_path_count = 0U;
    expected_migrated_progress
        .remote_inspection_sweep_had_unresolved_paths = false;
    require(
        migrated == v4_snapshot && migrated.catalog_digest != v3_digest &&
            migrated_progress == expected_migrated_progress,
        "rev0952 v3 migration changed catalog authority or authenticated scan continuation");

    anonsync::SyncSqliteStmt schema = anonsync::sqlite_prepare_or_throw(
        catalog_db.db,
        "SELECT m.schema_version,r.resume_after_path,"
        "r.inspection_sweep_basis_digest,"
        "r.inspection_sweep_started_after_path,"
        "r.inspection_sweep_seen_path_count,"
        "r.inspection_sweep_had_unresolved_paths,"
        "(SELECT count(*) FROM sqlite_schema WHERE sql IS NOT NULL AND "
        "name GLOB 'sync_replica_folder_catalog_*') "
        "FROM sync_replica_folder_catalog_meta AS m "
        "JOIN sync_replica_folder_catalog_remote_apply_progress AS r "
        "ON m.id=r.id WHERE m.id=1;",
        "v3 migrated schema prepare");
    require(
        sqlite3_step(schema.stmt) == SQLITE_ROW &&
            sqlite3_column_int64(schema.stmt, 0) == 7 &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(schema.stmt, 1))).empty() &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(schema.stmt, 2))).empty() &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(schema.stmt, 3))).empty() &&
            sqlite3_column_int64(schema.stmt, 4) == 0 &&
            sqlite3_column_int64(schema.stmt, 5) == 0 &&
            sqlite3_column_int64(schema.stmt, 6) == 7 &&
            sqlite3_step(schema.stmt) == SQLITE_DONE,
        "rev0952 migration did not create the exact v7 indexed sweep schema");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    require(
        scan->snapshot_or_throw() == migrated &&
            scan->scan_progress_snapshot_or_throw() == migrated_progress,
        "rev0952 v3 migration was not a stable one-time upgrade");
}

void test_rev0946_catalog_migrates_to_fair_scan_schema_exactly_once() {
    Fixture fixture("anonsync-folder-scan-v2-migration");
    write_file(fixture.shared_root / "a.txt", "retained v2 file");
    write_file(fixture.shared_root / "gone.txt", "deleted v2 file");
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "v2 migration catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    require(
        fs::remove(fixture.shared_root / "gone.txt"),
        "v2 migration fixture could not remove its tombstone predecessor");
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto v3_snapshot = scan->snapshot_or_throw();
    const auto retained_file = find_entry(v3_snapshot, "a.txt");
    const auto retained_tombstone = find_entry(v3_snapshot, "gone.txt");
    require(
        retained_file.has_value() &&
            retained_file->kind == anonsync::SyncReplicaValueKind::File &&
            retained_tombstone.has_value() &&
            retained_tombstone->kind ==
                anonsync::SyncReplicaValueKind::Tombstone,
        "v2 migration fixture did not retain both catalog value kinds");
    scan.reset();

    const std::string v2_digest =
        previous_catalog_digest_for_test(v3_snapshot);
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "BEGIN IMMEDIATE;"
        "DROP TABLE sync_replica_folder_catalog_scan_seen;"
        "DROP TABLE sync_replica_folder_catalog_scan_progress;"
        "DROP TABLE sync_replica_folder_catalog_remote_apply_progress;"
        "DROP TABLE sync_replica_folder_catalog_selection_rules;"
        "DROP INDEX sync_replica_folder_catalog_file_content;"
        "ALTER TABLE sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v3_fixture;"
        "ALTER TABLE sync_replica_folder_catalog_entries "
        "RENAME TO sync_replica_folder_catalog_entries_v3_fixture;"
        "CREATE TABLE sync_replica_folder_catalog_meta("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "schema_version INTEGER NOT NULL CHECK(schema_version=2),"
        "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
        "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
        "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
        "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
        "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
        "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
        "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
        "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
        "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
        "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT;"
        "CREATE TABLE sync_replica_folder_catalog_entries("
        "canonical_path TEXT PRIMARY KEY CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
        "value_kind INTEGER NOT NULL CHECK(value_kind IN (1,2)),"
        "size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),"
        "content_sha256 TEXT NOT NULL,"
        "operation_id TEXT NOT NULL CHECK(length(operation_id)=64),"
        "source_snapshot_sha256 TEXT NOT NULL,"
        "last_seen_generation INTEGER NOT NULL CHECK(last_seen_generation>0),"
        "CHECK((value_kind=1 AND length(content_sha256)=64 AND "
        "length(source_snapshot_sha256)=64) OR (value_kind=2 AND size_bytes=0 AND "
        "content_sha256='' AND source_snapshot_sha256=''))) STRICT;"
        "INSERT INTO sync_replica_folder_catalog_entries("
        "canonical_path,value_kind,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation) "
        "SELECT canonical_path,value_kind,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation "
        "FROM sync_replica_folder_catalog_entries_v3_fixture "
        "ORDER BY canonical_path;",
        "v2 migration fixture schema");
    anonsync::SyncSqliteStmt insert = anonsync::sqlite_prepare_or_throw(
        catalog_db.db,
        "INSERT INTO sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest) "
        "VALUES(1,2,?,?,?,?,?,?,?,?,?,?);",
        "v2 migration fixture metadata prepare");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 1, v3_snapshot.folder_id, "v2 migration fixture");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 2, v3_snapshot.absolute_root_path,
        "v2 migration fixture");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 3, v3_snapshot.root_attestation_digest,
        "v2 migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 4, v3_snapshot.state_generation,
        "v2 migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 5, v3_snapshot.limits.max_catalog_entries,
        "v2 migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 6, v3_snapshot.limits.max_catalog_path_bytes,
        "v2 migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 7, v3_snapshot.limits.max_payload_bytes,
        "v2 migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 8,
        static_cast<std::uint64_t>(v3_snapshot.entries.size()),
        "v2 migration fixture");
    std::uint64_t path_bytes = 0U;
    for (const auto& entry : v3_snapshot.entries) {
        path_bytes += static_cast<std::uint64_t>(entry.canonical_path.size());
    }
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 9, path_bytes, "v2 migration fixture");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 10, v2_digest, "v2 migration fixture");
    anonsync::sqlite_step_done_or_throw(
        insert.stmt, "v2 migration fixture metadata step");
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "DROP TABLE sync_replica_folder_catalog_entries_v3_fixture;"
        "DROP TABLE sync_replica_folder_catalog_meta_v3_fixture;"
        "COMMIT;",
        "v2 migration fixture commit");

    scan = fixture.make_scan_owner(catalog_db);
    const auto migrated = scan->snapshot_or_throw();
    auto expected = v3_snapshot;
    expected.catalog_digest = migrated.catalog_digest;
    require(
        migrated == expected && migrated.catalog_digest != v2_digest,
        "rev0946 catalog did not migrate without changing file/tombstone authority");

    anonsync::SyncSqliteStmt version_and_progress =
        anonsync::sqlite_prepare_or_throw(
            catalog_db.db,
            "SELECT m.schema_version,p.scan_epoch,p.resume_after_path,"
            "p.seen_path_count,p.seen_path_bytes,length(p.seen_chain_digest),"
            "r.resume_after_path,r.inspection_sweep_basis_digest,"
            "r.inspection_sweep_started_after_path,"
            "r.inspection_sweep_seen_path_count,"
            "r.inspection_sweep_had_unresolved_paths "
            "FROM sync_replica_folder_catalog_meta AS m "
            "JOIN sync_replica_folder_catalog_scan_progress AS p "
            "ON m.id=p.id "
            "JOIN sync_replica_folder_catalog_remote_apply_progress AS r "
            "ON m.id=r.id WHERE m.id=1;",
            "v2 migrated catalog progress prepare");
    require(
        sqlite3_step(version_and_progress.stmt) == SQLITE_ROW &&
            sqlite3_column_int64(version_and_progress.stmt, 0) == 7 &&
            sqlite3_column_int64(version_and_progress.stmt, 1) == 1 &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(version_and_progress.stmt, 2))).empty() &&
            sqlite3_column_int64(version_and_progress.stmt, 3) == 0 &&
            sqlite3_column_int64(version_and_progress.stmt, 4) == 0 &&
            sqlite3_column_int64(version_and_progress.stmt, 5) == 64 &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(version_and_progress.stmt, 6))).empty() &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(version_and_progress.stmt, 7))).empty() &&
            std::string_view(reinterpret_cast<const char*>(
                sqlite3_column_text(version_and_progress.stmt, 8))).empty() &&
            sqlite3_column_int64(version_and_progress.stmt, 9) == 0 &&
            sqlite3_column_int64(version_and_progress.stmt, 10) == 0 &&
            sqlite3_step(version_and_progress.stmt) == SQLITE_DONE,
        "rev0946 migration did not create exact scan and remote-work genesis cutpoints");

    scan.reset();
    scan = fixture.make_scan_owner(catalog_db);
    const auto stable = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        stable.used_idle_fast_path &&
            stable.completed_local_scan_epoch &&
            scan->snapshot_or_throw() == migrated,
        "rev0946 migration was not a stable one-time upgrade");
}

void test_rev0939_file_catalog_migrates_exactly_once() {
    Fixture fixture("anonsync-folder-scan-v1-migration");
    write_file(fixture.shared_root / "a.txt", "alpha migration");
    write_file(fixture.shared_root / "nested" / "b.txt", "beta migration");
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "legacy migration catalog database");
    auto scan = fixture.make_scan_owner(catalog_db);
    (void)scan->run_convergence_pass_or_throw(Fixture::pass_limits());
    const auto v3_snapshot = scan->snapshot_or_throw();
    scan.reset();

    const std::string legacy_digest =
        legacy_catalog_digest_for_test(v3_snapshot);
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "BEGIN IMMEDIATE;"
        "DROP TABLE sync_replica_folder_catalog_scan_seen;"
        "DROP TABLE sync_replica_folder_catalog_scan_progress;"
        "DROP TABLE sync_replica_folder_catalog_remote_apply_progress;"
        "DROP TABLE sync_replica_folder_catalog_selection_rules;"
        "DROP INDEX sync_replica_folder_catalog_file_content;"
        "ALTER TABLE sync_replica_folder_catalog_meta "
        "RENAME TO sync_replica_folder_catalog_meta_v3_fixture;"
        "ALTER TABLE sync_replica_folder_catalog_entries "
        "RENAME TO sync_replica_folder_catalog_entries_v3_fixture;"
        "CREATE TABLE sync_replica_folder_catalog_meta("
        "id INTEGER PRIMARY KEY CHECK(id=1),"
        "schema_version INTEGER NOT NULL CHECK(schema_version=1),"
        "folder_id TEXT NOT NULL CHECK(length(folder_id) BETWEEN 1 AND 128),"
        "absolute_root_path TEXT NOT NULL CHECK(length(absolute_root_path) BETWEEN 1 AND 16384),"
        "root_attestation_digest TEXT NOT NULL CHECK(length(root_attestation_digest)=64),"
        "state_generation INTEGER NOT NULL CHECK(state_generation>=0),"
        "max_catalog_entries INTEGER NOT NULL CHECK(max_catalog_entries>0),"
        "max_catalog_path_bytes INTEGER NOT NULL CHECK(max_catalog_path_bytes>0),"
        "max_payload_bytes INTEGER NOT NULL CHECK(max_payload_bytes>0),"
        "entry_count INTEGER NOT NULL CHECK(entry_count>=0),"
        "catalog_path_bytes INTEGER NOT NULL CHECK(catalog_path_bytes>=0),"
        "catalog_digest TEXT NOT NULL CHECK(length(catalog_digest)=64)) STRICT;"
        "CREATE TABLE sync_replica_folder_catalog_entries("
        "canonical_path TEXT PRIMARY KEY CHECK(length(canonical_path) BETWEEN 1 AND 4096),"
        "size_bytes INTEGER NOT NULL CHECK(size_bytes>=0),"
        "content_sha256 TEXT NOT NULL CHECK(length(content_sha256)=64),"
        "operation_id TEXT NOT NULL CHECK(length(operation_id)=64),"
        "source_snapshot_sha256 TEXT NOT NULL CHECK(length(source_snapshot_sha256)=64),"
        "last_seen_generation INTEGER NOT NULL CHECK(last_seen_generation>0)) STRICT;"
        "INSERT INTO sync_replica_folder_catalog_entries("
        "canonical_path,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation) "
        "SELECT canonical_path,size_bytes,content_sha256,operation_id,"
        "source_snapshot_sha256,last_seen_generation "
        "FROM sync_replica_folder_catalog_entries_v3_fixture "
        "ORDER BY canonical_path;",
        "legacy migration fixture schema");
    anonsync::SyncSqliteStmt insert = anonsync::sqlite_prepare_or_throw(
        catalog_db.db,
        "INSERT INTO sync_replica_folder_catalog_meta("
        "id,schema_version,folder_id,absolute_root_path,"
        "root_attestation_digest,state_generation,max_catalog_entries,"
        "max_catalog_path_bytes,max_payload_bytes,entry_count,"
        "catalog_path_bytes,catalog_digest) "
        "VALUES(1,1,?,?,?,?,?,?,?,?,?,?);",
        "legacy migration fixture metadata prepare");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 1, v3_snapshot.folder_id,
        "legacy migration fixture");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 2, v3_snapshot.absolute_root_path,
        "legacy migration fixture");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 3, v3_snapshot.root_attestation_digest,
        "legacy migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 4, v3_snapshot.state_generation,
        "legacy migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 5, v3_snapshot.limits.max_catalog_entries,
        "legacy migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 6, v3_snapshot.limits.max_catalog_path_bytes,
        "legacy migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 7, v3_snapshot.limits.max_payload_bytes,
        "legacy migration fixture");
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 8,
        static_cast<std::uint64_t>(v3_snapshot.entries.size()),
        "legacy migration fixture");
    std::uint64_t path_bytes = 0U;
    for (const auto& entry : v3_snapshot.entries) {
        path_bytes += static_cast<std::uint64_t>(entry.canonical_path.size());
    }
    anonsync::sqlite_bind_u64_or_throw(
        insert.stmt, 9, path_bytes, "legacy migration fixture");
    anonsync::sqlite_bind_text_or_throw(
        insert.stmt, 10, legacy_digest, "legacy migration fixture");
    anonsync::sqlite_step_done_or_throw(
        insert.stmt, "legacy migration fixture metadata step");
    anonsync::sqlite_exec_or_throw(
        catalog_db.db,
        "DROP TABLE sync_replica_folder_catalog_entries_v3_fixture;"
        "DROP TABLE sync_replica_folder_catalog_meta_v3_fixture;"
        "COMMIT;",
        "legacy migration fixture commit");

    scan = fixture.make_scan_owner(catalog_db);
    const auto migrated = scan->snapshot_or_throw();
    auto expected = v3_snapshot;
    expected.catalog_digest = migrated.catalog_digest;
    require(
        migrated == expected && migrated.catalog_digest != legacy_digest,
        "rev0939 file-only catalog did not migrate without changing its authority");

    anonsync::SyncSqliteStmt version = anonsync::sqlite_prepare_or_throw(
        catalog_db.db,
        "SELECT schema_version FROM sync_replica_folder_catalog_meta WHERE id=1;",
        "migrated catalog version prepare");
    require(
        sqlite3_step(version.stmt) == SQLITE_ROW &&
            sqlite3_column_int64(version.stmt, 0) == 7,
        "migrated folder catalog did not attest schema version 7");
    const auto stable = scan->run_convergence_pass_or_throw(
        Fixture::pass_limits());
    require(
        stable.used_idle_fast_path &&
            scan->snapshot_or_throw() == migrated,
        "migrated catalog was not a stable one-time upgrade");
}

void test_catalog_schema_contamination_fails_closed() {
    {
        Fixture fixture("anonsync-folder-scan-main-schema");
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "main schema contamination database");
        auto scan = fixture.make_scan_owner(catalog_db);
        anonsync::sqlite_exec_or_throw(
            catalog_db.db,
            "CREATE TRIGGER catalog_interceptor "
            "AFTER UPDATE ON sync_replica_folder_catalog_meta "
            "BEGIN SELECT 1; END;",
            "main schema contamination fixture");
        require_error(
            [&] { (void)scan->snapshot_or_throw(); },
            "catalog schema object count mismatch",
            "folder catalog accepted an unowned persistent trigger");
    }

    {
        Fixture fixture("anonsync-folder-scan-temp-schema");
        anonsync::SyncSqliteDb catalog_db = open_database(
            fixture.catalog_path(), "temp schema contamination database");
        auto scan = fixture.make_scan_owner(catalog_db);
        anonsync::sqlite_exec_or_throw(
            catalog_db.db,
            "CREATE TEMP TRIGGER temp_catalog_interceptor "
            "AFTER UPDATE ON main.sync_replica_folder_catalog_meta "
            "BEGIN SELECT 1; END;",
            "temp schema contamination fixture");
        require_error(
            [&] { (void)scan->snapshot_or_throw(); },
            "catalog has unowned temp schema objects",
            "folder catalog accepted an unowned temporary trigger");
    }
}

void test_catalog_identity_and_capacity_fail_closed() {
    Fixture fixture("anonsync-folder-scan-catalog-policy");
    anonsync::SyncSqliteDb catalog_db = open_database(
        fixture.catalog_path(), "catalog policy database");
    auto scan = fixture.make_scan_owner(catalog_db);
    const auto empty = scan->snapshot_or_throw();
    require(
        empty.folder_id == Fixture::folder_id && empty.entries.empty() &&
            empty.state_generation == 0U &&
            empty.absolute_root_path == fixture.shared_root.generic_string() &&
            empty.root_attestation_digest.size() == 64U &&
            empty.root_attestation_digest.find_first_not_of(
                "0123456789abcdef") == std::string::npos,
        "new folder catalog did not bind one exact configured root");

    const fs::path other_root = fixture.temporary.make_directory("other-root");
    require_error(
        [&] {
            anonsync::SyncReplicaFolderScanOwner wrong_root(
                catalog_db.db, Fixture::folder_id, other_root, fixture.replica,
                fixture.payload_store, Fixture::scan_limits(),
                "wrong-root folder-scan owner");
            (void)wrong_root.snapshot_or_throw();
        },
        "catalog identity does not match",
        "an existing folder catalog was rebound to another local root");

    const fs::path dedicated_path = fixture.temporary.path() / "not-empty.sqlite3";
    anonsync::SyncSqliteDb not_empty = open_database(
        dedicated_path, "non-dedicated catalog database");
    anonsync::sqlite_exec_or_throw(
        not_empty.db, "CREATE TABLE unrelated(value INTEGER) STRICT;",
        "non-dedicated catalog fixture");
    require_error(
        [&] {
            anonsync::SyncReplicaFolderScanOwner wrong_database(
                not_empty.db, Fixture::folder_id, fixture.shared_root,
                fixture.replica, fixture.payload_store, Fixture::scan_limits(),
                "non-dedicated folder-scan owner");
            (void)wrong_database.snapshot_or_throw();
        },
        "not dedicated and empty",
        "folder catalog silently adopted an unrelated SQLite database");

    Fixture rebound("anonsync-folder-scan-root-rebind");
    {
        anonsync::SyncSqliteDb first_catalog = open_database(
            rebound.catalog_path(), "root-rebind first catalog database");
        auto first_owner = rebound.make_scan_owner(first_catalog);
        (void)first_owner->snapshot_or_throw();
    }
    const fs::path displaced_root =
        rebound.temporary.path() / "displaced-shared-root";
    fs::rename(rebound.shared_root, displaced_root);
    fs::create_directory(rebound.shared_root);
    if (::chmod(rebound.shared_root.c_str(), 0700) != 0) {
        fail("could not make replacement shared root private");
    }
    anonsync::SyncSqliteDb rebound_catalog = open_database(
        rebound.catalog_path(), "root-rebind second catalog database");
    require_error(
        [&] {
            auto replacement_owner = rebound.make_scan_owner(rebound_catalog);
            (void)replacement_owner->snapshot_or_throw();
        },
        "catalog identity does not match",
        "folder catalog accepted a different directory at the same path");
}

}  // namespace

int main() {
    try {
        test_deployment_payload_ceiling_composes_usable_pass_defaults();
        test_selective_sync_policy_is_bounded_durable_and_content_cold();
        test_selective_sync_pure_exclusion_does_not_delay_other_deletion();
        test_selective_sync_metadata_only_is_payload_cold_and_rehydrates();
        test_selective_sync_rehydrates_remote_successor_after_dematerialization();
        test_selective_sync_dematerialization_preserves_changed_and_untracked_files();
        test_selective_sync_dematerialization_reproof_is_path_local();
        test_selective_sync_dematerialization_obeys_remote_effect_frontier();
        test_streaming_file_larger_than_legacy_frame_ceiling();
        test_bounded_whole_folder_pass_local_tree_and_noop();
        test_complete_payload_reproof_handoff_requires_exact_store_owner();
        test_payload_handoff_cutpoint_invalidates_after_already_present_put();
        test_many_file_pass_amortizes_payload_store_mutation_authority();
        test_scan_journal_batches_one_progress_publication_per_segment();
        test_terminal_cutpoint_fence_serializes_progress_publication();
        test_terminal_cutpoint_movement_withholds_stale_settlement();
        test_terminal_catalog_progress_movement_withholds_stale_publication();
        test_zero_byte_scan_segment_has_bounded_journal_publication();
        test_idle_proof_obeys_path_effect_frontier();
        test_payload_batch_segments_bound_exclusive_lease_horizon();
        test_local_batch_releases_for_remote_apply_and_reacquires();
        test_bounded_whole_folder_pass_remote_catchup_and_divergence();
        test_bounded_whole_folder_pass_preserves_absent_conflict();
        test_local_exact_content_rename_identity_and_ambiguity_fence();
        test_complete_scan_deletion_restart_and_resurrection();
        test_remote_tombstone_removal_and_delete_edit_conflicts();
        test_deletion_crash_residue_is_not_published();
        test_reserved_internal_namespace_cannot_be_materialized();
        test_incomplete_scan_cannot_infer_deletion();
        test_bounded_whole_folder_pass_bound_stop_and_restart();
        test_durable_scan_epoch_delays_deletion_until_complete_suffix();
        test_completed_epoch_does_not_restore_deleted_seen_prefix();
        test_scan_epoch_restarts_when_absent_prefix_reappears();
        test_incomplete_epoch_defers_tombstone_behind_cursor();
        test_scan_progress_tampering_fails_closed();
        test_bounded_whole_folder_pass_missing_payload_and_remote_limit();
        test_targeted_remote_payload_path_does_not_claim_complete_namespace_audit();
        test_targeted_remote_payload_rejects_legacy_v1_split_identity();
        test_targeted_remote_payload_hashes_only_at_publication_boundary();
        test_remote_only_tombstone_catalog_defers_complete_payload_inventory();
        test_bounded_whole_folder_pass_remote_work_bounds();
        test_remote_apply_count_frontier_bounds_zero_byte_and_tombstone_work();
        test_remote_inspection_frontier_rotates_safe_deferrals_across_restart();
        test_remote_inspection_sweep_settles_stable_projection_across_restart();
        test_remote_apply_cursor_survives_restart_and_defeats_prefix_churn();
        test_catalog_predecessor_reproof_decouples_remote_apply_from_scan_cursor();
        test_bounded_whole_folder_pass_limit_contract();
        test_namespace_entries_do_not_consume_file_capacity();
        test_publish_noop_restart_and_modify();
        test_identity_preserving_regular_file_rename_is_atomic_and_restart_stable();
        test_identity_preserving_rename_replica_pair_survives_catalog_crash_window();
        test_convergence_pass_reports_one_identity_preserving_rename();
        test_present_same_content_duplicate_falls_back_before_rename_publication();
        test_ambiguous_same_content_absence_does_not_invent_rename_identity();
        test_database_head_race_rejects_without_scanner_mutation();
        test_prepared_file_and_path_reproof();
        test_restart_adopts_publication_after_catalog_crash_window();
        test_replica_ahead_and_populated_collision_fail_closed();
        test_multi_head_conflict_is_preserved();
        test_remote_apply_replaces_predecessor_without_echo_and_restarts();
        test_remote_apply_absent_exact_adoption_and_collision();
        test_remote_apply_parent_chain_refuses_unsafe_components();
        test_remote_apply_rejects_local_mutation_and_multihead();
        test_remote_apply_path_fence_and_crash_recovery();
        test_historical_version_inspection_and_causal_restore();
        test_historical_version_metadata_only_is_payload_cold();
        test_historical_version_payload_reachability_and_evidence_cutpoint();
        test_retention_witness_binds_exact_replica_database_incarnation();
        test_historical_version_restore_from_tombstone();
        test_rev0951_cyclic_catalog_migrates_cursor_and_resets_sweep();
        test_rev0950_fair_scan_catalog_migrates_without_losing_journal();
        test_rev0946_catalog_migrates_to_fair_scan_schema_exactly_once();
        test_rev0939_file_catalog_migrates_exactly_once();
        test_catalog_schema_contamination_fails_closed();
        test_catalog_identity_and_capacity_fail_closed();
        std::cout << "sync replica folder-scan owner tests passed ("
                  << checks << " checks)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica folder-scan owner tests failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
