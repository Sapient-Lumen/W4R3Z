#pragma once

#if !defined(_WIN32)

#include "sqlite_path_security.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <filesystem>
#include <memory>
#include <string>

namespace anonsync {

// Every process-facing owner opens selected SQLite stores existing-only. A
// freshly sealed bootstrap image is the sole exception: it may be opened as a
// candidate, attested by its exact role owner, and then explicitly promoted
// from rollback mode to the reviewed WAL operational profile.
enum class SyncReplicaOperationalDatabaseOpenDisposition : std::uint8_t {
    ExistingOperational = 1U,
    PublishedBootstrapCandidate = 2U,
    // Exact current-schema observation only. The descriptor-rooted VFS and
    // SQLite connection are read-only, query_only remains enabled, and no
    // schema initialization, migration, journal transition, or checkpoint is
    // permitted.
    ExistingForensicReadOnly = 3U,
};

// Move-only authority over one descriptor-rooted SQLite database family. The
// declaration order is intentional: destruction closes the SQLite connection,
// unregisters the private VFS, then releases the retained path guard.
class SyncReplicaOperationalDatabase final {
public:
    SyncReplicaOperationalDatabase() = default;
    ~SyncReplicaOperationalDatabase();
    SyncReplicaOperationalDatabase(
        const SyncReplicaOperationalDatabase&) = delete;
    SyncReplicaOperationalDatabase& operator=(
        const SyncReplicaOperationalDatabase&) = delete;
    SyncReplicaOperationalDatabase(
        SyncReplicaOperationalDatabase&& other) noexcept;
    SyncReplicaOperationalDatabase& operator=(
        SyncReplicaOperationalDatabase&& other) noexcept;

    [[nodiscard]] static SyncReplicaOperationalDatabase open_or_throw(
        const std::filesystem::path& absolute_database_path,
        SyncReplicaOperationalDatabaseOpenDisposition disposition,
        std::string label = "sync replica operational database");

    [[nodiscard]] SyncSqliteDbHandleSlot& handle() noexcept { return db_; }
    [[nodiscard]] const std::filesystem::path& database_path() const noexcept;
    [[nodiscard]] bool operational_profile_active() const noexcept {
        return operational_profile_active_;
    }

    void verify_open_database_or_throw(const std::string& label);

    // Candidate-only transition. Callers must attest the exact deployment
    // binding and role schema before this method. It never creates the main
    // database path; it only converts a complete create-new sealed image to WAL
    // and applies the reviewed connection profile.
    void promote_published_bootstrap_candidate_or_throw(
        const std::string& label);

private:
    SyncReplicaOperationalDatabase(
        SqlitePathFamilyGuard path_guard,
        std::unique_ptr<SqliteDescriptorRootedVfs> rooted_vfs,
        SyncReplicaOperationalDatabaseOpenDisposition disposition,
        std::string label);

    SqlitePathFamilyGuard path_guard_;
    std::unique_ptr<SqliteDescriptorRootedVfs> rooted_vfs_;
    SyncSqliteDbHandleSlot db_;
    SyncReplicaOperationalDatabaseOpenDisposition disposition_ =
        SyncReplicaOperationalDatabaseOpenDisposition::ExistingOperational;
    std::string label_;
    bool operational_profile_active_ = false;
};

}  // namespace anonsync

#endif
