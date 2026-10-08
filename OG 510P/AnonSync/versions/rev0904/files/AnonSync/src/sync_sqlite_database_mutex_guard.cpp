#include "sync_sqlite_database_mutex_guard.hpp"

#include "sync_sqlite_execution_affinity.hpp"

#include <sqlite3.h>

#include <stdexcept>
#include <string>

namespace anonsync {
namespace {

[[noreturn]] void fail_stop_on_database_mutex_guard_violation_noexcept()
    noexcept {
    fail_stop_on_sync_process_capability_violation_noexcept();
}

}  // namespace

SyncSqliteDatabaseMutexGuard::SyncSqliteDatabaseMutexGuard(
    sqlite3* database,
    std::string_view label)
    : database_(database),
      process_id_(current_sync_process_incarnation_noexcept()),
      thread_id_(current_sync_thread_incarnation_noexcept()) {
    if (database == nullptr) {
        throw std::invalid_argument(
            std::string(label) + " database handle is null");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "SQLite database mutex guard requires a nonempty diagnostic label");
    }

    mutex_ = sqlite3_db_mutex(database);
    if (mutex_ == nullptr) {
        throw std::runtime_error(
            std::string(label) +
            " requires a serialized/FULLMUTEX SQLite connection");
    }

    // SQLite's per-connection mutex is recursive in serialized mode, so an
    // API-specific owner may compose this guard under a broader connection
    // authority lease without deadlocking the exact owning thread.
    sqlite3_mutex_enter(mutex_);
}

SyncSqliteDatabaseMutexGuard::SyncSqliteDatabaseMutexGuard(
    sqlite3* database,
    SyncSqliteDatabaseMutexFailStopTag) noexcept
    : database_(database),
      process_id_(current_sync_process_incarnation_noexcept()),
      thread_id_(current_sync_thread_incarnation_noexcept()) {
    if (database == nullptr) {
        fail_stop_on_database_mutex_guard_violation_noexcept();
    }
    mutex_ = sqlite3_db_mutex(database);
    if (mutex_ == nullptr) {
        fail_stop_on_database_mutex_guard_violation_noexcept();
    }
    sqlite3_mutex_enter(mutex_);
}

SyncSqliteDatabaseMutexGuard::~SyncSqliteDatabaseMutexGuard() noexcept {
    require_current_execution_noexcept();
    if (mutex_ != nullptr) {
        sqlite3_mutex_leave(mutex_);
        mutex_ = nullptr;
    }
    database_ = nullptr;
}

bool SyncSqliteDatabaseMutexGuard::owns_mutex() const noexcept {
    require_current_execution_noexcept();
    return mutex_ != nullptr;
}

sqlite3_mutex* SyncSqliteDatabaseMutexGuard::mutex_identity() const noexcept {
    require_current_execution_noexcept();
    return mutex_;
}

bool SyncSqliteDatabaseMutexGuard::authorizes(sqlite3* database) const noexcept {
    require_current_execution_noexcept();
    return database != nullptr && database_ == database && mutex_ != nullptr;
}

sqlite3_mutex* SyncSqliteDatabaseMutexGuard::release() noexcept {
    require_current_execution_noexcept();
    if (mutex_ == nullptr) {
        fail_stop_on_database_mutex_guard_violation_noexcept();
    }
    sqlite3_mutex* const result = mutex_;
    mutex_ = nullptr;
    database_ = nullptr;
    return result;
}

void SyncSqliteDatabaseMutexGuard::require_current_execution_noexcept() const
    noexcept {
    require_current_sync_sqlite_execution_noexcept(process_id_, thread_id_);
}

}  // namespace anonsync
