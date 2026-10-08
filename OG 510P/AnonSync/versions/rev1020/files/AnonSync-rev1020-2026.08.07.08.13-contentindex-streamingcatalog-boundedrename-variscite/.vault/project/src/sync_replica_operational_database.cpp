#include "sync_replica_operational_database.hpp"

#if !defined(_WIN32)

#include "sync_replica_tls_policy_sqlite_profile.hpp"
#include "sync_sqlite_support.hpp"

#include <stdexcept>
#include <string>
#include <utility>

#include <sqlite3.h>

namespace anonsync {
namespace {

class UnadoptedSqliteConnection final {
public:
    ~UnadoptedSqliteConnection() noexcept {
        if (handle_ == nullptr) return;
        if (sqlite3_close(handle_) != SQLITE_OK) {
            (void)sqlite3_close_v2(handle_);
        }
    }
    UnadoptedSqliteConnection(const UnadoptedSqliteConnection&) = delete;
    UnadoptedSqliteConnection& operator=(
        const UnadoptedSqliteConnection&) = delete;
    UnadoptedSqliteConnection() = default;

    [[nodiscard]] sqlite3** out() noexcept { return &handle_; }
    [[nodiscard]] sqlite3* get() const noexcept { return handle_; }
    [[nodiscard]] sqlite3* release() noexcept {
        return std::exchange(handle_, nullptr);
    }

private:
    sqlite3* handle_ = nullptr;
};

[[nodiscard]] bool database_has_persistent_schema_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database,
        "SELECT 1 FROM main.sqlite_schema "
        "WHERE name NOT LIKE 'sqlite_%' LIMIT 1;",
        label + " persistent-schema probe");
    const int first = sqlite3_step(statement.stmt);
    if (first == SQLITE_DONE) return false;
    if (first != SQLITE_ROW) {
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), first,
            label + " persistent-schema probe");
    }
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " persistent-schema probe returned excess rows");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " persistent-schema trailing step");
    }
    return true;
}

[[nodiscard]] std::string journal_mode_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database, "PRAGMA main.journal_mode;",
        label + " journal-mode probe");
    const int first = sqlite3_step(statement.stmt);
    if (first != SQLITE_ROW) {
        if (first == SQLITE_DONE) {
            throw std::runtime_error(
                label + " journal-mode probe returned no row");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), first,
            label + " journal-mode probe");
    }
    const std::string mode = sqlite_column_text_or_throw(
        statement.stmt, 0, label + " journal-mode value");
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " journal-mode probe returned excess rows");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " journal-mode trailing step");
    }
    return mode;
}

void require_or_set_journal_mode_wal_or_throw(
    SyncSqliteDbHandleSlot& database,
    bool may_promote,
    const std::string& label) {
    std::string mode = journal_mode_or_throw(database, label);
    if (mode == "delete" && may_promote) {
        SyncSqliteStmt statement = sqlite_prepare_or_throw(
            database, "PRAGMA main.journal_mode=WAL;",
            label + " WAL promotion prepare");
        const int first = sqlite3_step(statement.stmt);
        if (first != SQLITE_ROW) {
            if (first == SQLITE_DONE) {
                throw std::runtime_error(
                    label + " WAL promotion returned no row");
            }
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), first,
                label + " WAL promotion");
        }
        mode = sqlite_column_text_or_throw(
            statement.stmt, 0, label + " WAL promotion value");
        const int trailing = sqlite3_step(statement.stmt);
        if (trailing != SQLITE_DONE) {
            if (trailing == SQLITE_ROW) {
                throw std::runtime_error(
                    label + " WAL promotion returned excess rows");
            }
            throw_sqlite_exception(
                sqlite3_db_handle(statement.stmt), trailing,
                label + " WAL promotion trailing step");
        }
    }
    if (mode != "wal") {
        throw std::runtime_error(
            label + " journal mode is " + mode + ", expected wal");
    }
}

void retain_exclusive_locking_mode_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database, "PRAGMA main.locking_mode=EXCLUSIVE;",
        label + " locking-mode prepare");
    const int first = sqlite3_step(statement.stmt);
    if (first != SQLITE_ROW) {
        if (first == SQLITE_DONE) {
            throw std::runtime_error(
                label + " locking-mode request returned no row");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), first,
            label + " locking-mode request");
    }
    const std::string mode = sqlite_column_text_or_throw(
        statement.stmt, 0, label + " locking-mode value");
    const int trailing = sqlite3_step(statement.stmt);
    if (trailing != SQLITE_DONE) {
        if (trailing == SQLITE_ROW) {
            throw std::runtime_error(
                label + " locking-mode request returned excess rows");
        }
        throw_sqlite_exception(
            sqlite3_db_handle(statement.stmt), trailing,
            label + " locking-mode trailing step");
    }
    if (mode != "exclusive") {
        throw std::runtime_error(
            label + " could not retain exclusive SQLite locking mode");
    }
}

void configure_operational_profile_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    require_or_set_journal_mode_wal_or_throw(database, false, label);
    sqlite_exec_or_throw(
        database,
        "PRAGMA synchronous=FULL;"
        "PRAGMA wal_autocheckpoint=1;"
        "PRAGMA temp_store=MEMORY;"
        "PRAGMA foreign_keys=ON;"
        "PRAGMA trusted_schema=OFF;",
        label + " operational profile");
}

}  // namespace

SyncReplicaOperationalDatabase::SyncReplicaOperationalDatabase(
    SqlitePathFamilyGuard path_guard,
    std::unique_ptr<SqliteDescriptorRootedVfs> rooted_vfs,
    SyncReplicaOperationalDatabaseOpenDisposition disposition,
    std::string label)
    : path_guard_(std::move(path_guard)),
      rooted_vfs_(std::move(rooted_vfs)),
      disposition_(disposition),
      label_(std::move(label)) {
    if (!rooted_vfs_) {
        throw std::invalid_argument(
            label_ + " requires a descriptor-rooted SQLite VFS");
    }
}

SyncReplicaOperationalDatabase::~SyncReplicaOperationalDatabase() = default;

SyncReplicaOperationalDatabase::SyncReplicaOperationalDatabase(
    SyncReplicaOperationalDatabase&& other) noexcept
    : path_guard_(std::move(other.path_guard_)),
      rooted_vfs_(std::move(other.rooted_vfs_)),
      db_(std::move(other.db_)),
      disposition_(other.disposition_),
      label_(std::move(other.label_)),
      operational_profile_active_(other.operational_profile_active_) {
    other.operational_profile_active_ = false;
}

SyncReplicaOperationalDatabase&
SyncReplicaOperationalDatabase::operator=(
    SyncReplicaOperationalDatabase&& other) noexcept {
    if (this == &other) return *this;
    db_ = SyncSqliteDbHandleSlot{};
    rooted_vfs_.reset();
    path_guard_ = SqlitePathFamilyGuard{};
    path_guard_ = std::move(other.path_guard_);
    rooted_vfs_ = std::move(other.rooted_vfs_);
    db_ = std::move(other.db_);
    disposition_ = other.disposition_;
    label_ = std::move(other.label_);
    operational_profile_active_ = other.operational_profile_active_;
    other.operational_profile_active_ = false;
    return *this;
}

SyncReplicaOperationalDatabase
SyncReplicaOperationalDatabase::open_or_throw(
    const std::filesystem::path& absolute_database_path,
    SyncReplicaOperationalDatabaseOpenDisposition disposition,
    std::string label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync replica operational database label must not be empty");
    }
    switch (disposition) {
        case SyncReplicaOperationalDatabaseOpenDisposition::
            ExistingOperational:
        case SyncReplicaOperationalDatabaseOpenDisposition::
            PublishedBootstrapCandidate:
        case SyncReplicaOperationalDatabaseOpenDisposition::
            ExistingForensicReadOnly:
            break;
        default:
            throw std::invalid_argument(
                label + " open disposition is invalid");
    }

    SqlitePathFamilyGuard path_guard =
        guard_sqlite_path_family_or_throw(
            absolute_database_path, false, {"-journal", "-wal", "-shm"},
            label + " path authority");
    if (!path_guard.parent_exists() ||
        !path_guard.database_existed_at_preflight()) {
        throw std::runtime_error(
            label + " requires an existing guarded main database");
    }
    const std::filesystem::path logical_path = path_guard.database_path();
    const bool forensic_read_only =
        disposition == SyncReplicaOperationalDatabaseOpenDisposition::
            ExistingForensicReadOnly;
    auto rooted_vfs = register_sqlite_descriptor_rooted_vfs_or_throw(
        path_guard,
        forensic_read_only
            ? SqliteDescriptorRootedVfsAccess::ReadOnlyExisting
            : SqliteDescriptorRootedVfsAccess::ReadWriteExisting,
        label + " descriptor-rooted VFS");
    SyncReplicaOperationalDatabase database(
        std::move(path_guard), std::move(rooted_vfs), disposition, label);

    int flags = (forensic_read_only ? SQLITE_OPEN_READONLY
                                    : SQLITE_OPEN_READWRITE) |
                SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    UnadoptedSqliteConnection candidate;
    const int opened = sqlite3_open_v2(
        logical_path.string().c_str(), candidate.out(), flags,
        database.rooted_vfs_->name());
    if (opened != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            candidate.get(), label + " open"));
    }
    if (candidate.get() == nullptr) {
        throw std::runtime_error(label + " open returned no SQLite handle");
    }
    const int read_only = sqlite3_db_readonly(candidate.get(), "main");
    if ((!forensic_read_only && read_only != 0) ||
        (forensic_read_only && read_only != 1)) {
        throw std::runtime_error(
            label + (forensic_read_only
                ? " could not prove read-only main-database authority"
                : " could not prove writable main-database authority"));
    }
    {
        auto output = database.db_.out();
        *output.get() = candidate.release();
    }
    database.verify_open_database_or_throw(label + " post-open proof");
    sqlite_set_busy_timeout_or_throw(
        database.db_, 5000, label + " busy timeout");
    if (disposition ==
        SyncReplicaOperationalDatabaseOpenDisposition::
            PublishedBootstrapCandidate) {
        // Retain the connection-local lock before the first page read. This is
        // the same bootstrap ordering used by the product CLI and prevents a
        // later WAL promotion from opening a writer gap.
        retain_exclusive_locking_mode_or_throw(
            database.db_, label + " bootstrap candidate");
    } else if (forensic_read_only) {
        // WAL readers normally join or create a persistent -shm domain on the
        // first page read. Select the private heap WAL index and hardened
        // query-only profile before any schema or journal-mode probe instead.
        retain_exclusive_locking_mode_or_throw(
            database.db_, label + " forensic connection-local WAL index");
        configure_sync_replica_tls_policy_sqlite_read_only_connection_or_throw(
            database.db_, label + " forensic read-only profile");
    }
    if (!database_has_persistent_schema_or_throw(database.db_, label)) {
        throw std::runtime_error(
            label + " has no persistent schema and requires explicit bootstrap");
    }

    const std::string mode = journal_mode_or_throw(database.db_, label);
    if (disposition ==
        SyncReplicaOperationalDatabaseOpenDisposition::ExistingOperational) {
        if (mode != "wal") {
            throw std::runtime_error(
                label + " journal mode is " + mode + ", expected wal");
        }
        configure_operational_profile_or_throw(database.db_, label);
        database.operational_profile_active_ = true;
    } else if (disposition ==
               SyncReplicaOperationalDatabaseOpenDisposition::
                   PublishedBootstrapCandidate) {
        if (mode != "delete" && mode != "wal") {
            throw std::runtime_error(
                label + " bootstrap candidate journal mode is " + mode +
                ", expected delete or wal");
        }
        if (mode == "wal") {
            configure_operational_profile_or_throw(database.db_, label);
            database.operational_profile_active_ = true;
        }
    } else {
        if (mode != "wal") {
            throw std::runtime_error(
                label + " forensic journal mode is " + mode +
                ", expected wal");
        }
        // The private WAL index and hardened read-only profile were selected
        // before the first page read. The rooted VFS independently denies
        // mutation of the main database and every configured sidecar.
    }
    database.verify_open_database_or_throw(label + " post-profile proof");
    return database;
}

const std::filesystem::path&
SyncReplicaOperationalDatabase::database_path() const noexcept {
    return path_guard_.database_path();
}

void SyncReplicaOperationalDatabase::verify_open_database_or_throw(
    const std::string& label) {
    if (!rooted_vfs_ || !db_) {
        throw std::logic_error(
            label + " has no live operational SQLite authority");
    }
    auto borrow = db_.borrow();
    rooted_vfs_->verify_open_database_or_throw(
        borrow.get(), label + " descriptor-rooted proof");
    path_guard_.verify_open_database_or_throw(
        borrow.get(), label + " logical-path proof");
}

void SyncReplicaOperationalDatabase::
promote_published_bootstrap_candidate_or_throw(
    const std::string& label) {
    if (disposition_ !=
        SyncReplicaOperationalDatabaseOpenDisposition::
            PublishedBootstrapCandidate) {
        throw std::logic_error(
            label + " is not a published bootstrap candidate");
    }
    if (operational_profile_active_) {
        verify_open_database_or_throw(label + " already-operational proof");
        return;
    }
    rooted_vfs_->verify_sidecars_absent_or_throw(
        label + " rollback candidate sidecars");
    require_or_set_journal_mode_wal_or_throw(db_, true, label);
    configure_operational_profile_or_throw(db_, label);
    operational_profile_active_ = true;
    verify_open_database_or_throw(label + " post-promotion proof");
}

}  // namespace anonsync

#endif
