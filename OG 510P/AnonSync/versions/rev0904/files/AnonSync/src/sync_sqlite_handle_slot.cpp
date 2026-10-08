#include "sync_sqlite_handle_slot.hpp"
#include "sync_sqlite_connection_authority_internal.hpp"

namespace anonsync::detail {

SyncSqliteDbHandlePolicy::Evidence
SyncSqliteDbHandlePolicy::capture_evidence(Handle* handle) noexcept {
    if (handle == nullptr) return {};
    sqlite3_mutex* const mutex = sqlite3_db_mutex(handle);
    return {
        mutex != nullptr ? SyncSqliteConnectionMutexMode::Serialized
                         : SyncSqliteConnectionMutexMode::Unserialized,
        mutex,
    };
}

bool SyncSqliteDbHandlePolicy::evidence_is_empty(
    const Evidence& evidence) noexcept {
    return evidence.mutex_mode == SyncSqliteConnectionMutexMode::Unknown &&
           evidence.mutex_identity == nullptr;
}

bool SyncSqliteDbHandlePolicy::evidence_is_valid(
    Handle* handle, const Evidence& evidence) noexcept {
    if (handle == nullptr) return false;
    // A connection's threading mode is selected when it is opened and cannot
    // be changed for that connection generation. Re-reading sqlite3_db_mutex()
    // here would make every owner/borrow bookkeeping check an SQLite operation
    // and could itself violate a NOMUTEX connection's no-concurrent-use rule.
    // The exact handle, process, generation, and captured evidence are compared
    // by the owner state; this predicate therefore validates only the frozen
    // evidence shape.
    if (evidence.mutex_mode ==
        SyncSqliteConnectionMutexMode::Serialized) {
        return evidence.mutex_identity != nullptr;
    }
    if (evidence.mutex_mode ==
        SyncSqliteConnectionMutexMode::Unserialized) {
        return evidence.mutex_identity == nullptr;
    }
    return false;
}

void SyncSqliteDbHandlePolicy::dispose(Handle* handle) noexcept {
    if (handle == nullptr) return;
    // SQLite normally rolls back an open transaction during close. That is not
    // an acceptable owner-lifetime substitute: a transaction boundary must be
    // ended by its exact guard before the connection generation can disappear.
    if (sqlite3_get_autocommit(handle) == 0) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    // The connection-authority client-data state is also SQLite's retained
    // authorizer context.  Revoke that singleton callback and consume its
    // lifetime claim before strict close can invoke client-data destructors.
    revoke_sync_sqlite_connection_authority_before_close_noexcept(handle);
    // close_v2 deliberately permits a zombie connection whose storage remains
    // owned by unfinalized statements. AnonSync requires dependent-before-owner
    // destruction, so a busy strict close is a fatal lifetime-order defect.
    if (sqlite3_close(handle) != SQLITE_OK) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
}

void SyncSqliteStmtHandlePolicy::dispose(Handle* handle) noexcept {
    if (handle != nullptr) (void)sqlite3_finalize(handle);
}

}  // namespace anonsync::detail
