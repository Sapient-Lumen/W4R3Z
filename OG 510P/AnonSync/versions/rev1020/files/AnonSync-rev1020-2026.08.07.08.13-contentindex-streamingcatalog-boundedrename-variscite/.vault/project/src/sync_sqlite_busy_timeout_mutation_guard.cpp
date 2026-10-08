#include "sync_sqlite_busy_timeout_mutation_guard.hpp"

#include "sync_sqlite_execution_affinity.hpp"

#include <sqlite3.h>

#include <stdexcept>
#include <string>

namespace anonsync {

SyncSqliteBusyTimeoutMutationGuard::SyncSqliteBusyTimeoutMutationGuard(
    sqlite3* database,
    std::string_view label)
    : process_id_(current_sync_process_incarnation_noexcept()),
      thread_id_(current_sync_thread_incarnation_noexcept()) {
    if (database == nullptr) {
        throw std::invalid_argument(
            std::string(label) + " database handle is null");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "SQLite busy-timeout mutation guard requires a nonempty "
            "diagnostic label");
    }

    mutex_ = sqlite3_db_mutex(database);
    if (mutex_ != nullptr) {
        sqlite3_mutex_enter(mutex_);
    }
}

SyncSqliteBusyTimeoutMutationGuard::~SyncSqliteBusyTimeoutMutationGuard()
    noexcept {
    require_current_sync_sqlite_execution_noexcept(process_id_, thread_id_);
    if (mutex_ != nullptr) {
        sqlite3_mutex_leave(mutex_);
        mutex_ = nullptr;
    }
}

}  // namespace anonsync
