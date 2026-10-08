#include "sqlite_authorizer_owner.hpp"

#include "sqlite_retained_callback_slots.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"

#include <sqlite3.h>

#include <stdexcept>
#include <string>

namespace anonsync::persistence {
namespace {

[[noreturn]] void fail_stop_on_authorizer_owner_violation_noexcept() noexcept {
    fail_stop_on_sync_process_capability_violation_noexcept();
}

std::runtime_error authorizer_error(sqlite3* database,
                                    int result_code,
                                    const std::string& label,
                                    const char* operation) {
    const char* detail = database == nullptr ? nullptr : sqlite3_errmsg(database);
    if (detail == nullptr || *detail == '\0') detail = sqlite3_errstr(result_code);
    return std::runtime_error(
        label + " could not " + operation + " SQLite authorizer owner: " +
        (detail == nullptr ? "SQLite error" : detail));
}

}  // namespace

SqliteAuthorizerOwner::SqliteAuthorizerOwner() noexcept
    : process_id_(current_sync_process_incarnation_noexcept()) {}

SqliteAuthorizerOwner::~SqliteAuthorizerOwner() {
    require_current_process_noexcept();
    if (database_ != nullptr || callback_ != nullptr ||
        callback_context_ != nullptr || callback_claim_.attached()) {
        // Auto-detach could dereference a database that was already closed or
        // replaced.  The enclosing connection owner must run ordered teardown.
        fail_stop_on_authorizer_owner_violation_noexcept();
    }
}

void SqliteAuthorizerOwner::attach(
    sqlite3* database,
    SqliteAuthorizerCallback callback,
    void* callback_context,
    const std::string& label) {
    require_current_process_noexcept();
    require_shape_noexcept();
    if (database_ != nullptr) {
        throw std::logic_error("SQLite authorizer owner is already attached");
    }
    if (database == nullptr || callback == nullptr ||
        callback_context == nullptr) {
        throw std::invalid_argument(
            "SQLite authorizer owner requires a database, callback, and retained context");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "SQLite authorizer owner requires a nonempty diagnostic label");
    }

    // The lifetime claim and callback setter are one singleton-slot
    // transition. Recursive composition keeps this safe when the enclosing
    // connection authority already owns the same database mutex.
    SyncSqliteDatabaseMutexGuard mutation_guard(
        database, label + " authorizer slot attachment");
    callback_claim_.attach(database,
                           mutation_guard,
                           kSqliteAuthorizerOwnerClientDataName,
                           label,
                           "authorizer owner");
    const int result =
        sqlite3_set_authorizer(database, callback, callback_context);
    if (result != SQLITE_OK) {
        callback_claim_.detach(database, mutation_guard);
        throw authorizer_error(database, result, label, "attach");
    }

    database_ = database;
    callback_ = callback;
    callback_context_ = callback_context;
}

void SqliteAuthorizerOwner::replace(
    sqlite3* database,
    SqliteAuthorizerCallback callback,
    void* callback_context,
    const std::string& label) {
    require_current_process_noexcept();
    require_shape_noexcept();
    if (database == nullptr || callback == nullptr ||
        callback_context == nullptr) {
        throw std::invalid_argument(
            "SQLite authorizer owner replacement requires a database, callback, and retained context");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "SQLite authorizer owner replacement requires a nonempty diagnostic label");
    }
    if (database_ == nullptr || database_ != database) {
        throw std::logic_error(
            "SQLite authorizer owner replacement requires its exact attached connection");
    }

    SyncSqliteDatabaseMutexGuard mutation_guard(
        database, label + " authorizer slot replacement");
    callback_claim_.require_live(database, mutation_guard);
    const int result =
        sqlite3_set_authorizer(database, callback, callback_context);
    if (result != SQLITE_OK) {
        throw authorizer_error(database, result, label, "replace");
    }
    callback_ = callback;
    callback_context_ = callback_context;
}

void SqliteAuthorizerOwner::require_live(sqlite3* database) const noexcept {
    require_current_process_noexcept();
    require_shape_noexcept();
    if (database_ == nullptr || database == nullptr || database_ != database) {
        fail_stop_on_authorizer_owner_violation_noexcept();
    }
    SyncSqliteDatabaseMutexGuard mutation_guard(
        database, kSyncSqliteDatabaseMutexFailStop);
    callback_claim_.require_live(database, mutation_guard);
}

void SqliteAuthorizerOwner::detach(sqlite3* database) noexcept {
    require_current_process_noexcept();
    require_shape_noexcept();
    if (database_ == nullptr) return;
    if (database == nullptr || database_ != database) {
        fail_stop_on_authorizer_owner_violation_noexcept();
    }

    {
        SyncSqliteDatabaseMutexGuard mutation_guard(
            database, kSyncSqliteDatabaseMutexFailStop);
        callback_claim_.require_live(database, mutation_guard);
        if (sqlite3_set_authorizer(database, nullptr, nullptr) != SQLITE_OK) {
            fail_stop_on_authorizer_owner_violation_noexcept();
        }
        callback_claim_.detach(database, mutation_guard);
        database_ = nullptr;
        callback_ = nullptr;
        callback_context_ = nullptr;
    }
}

bool SqliteAuthorizerOwner::attached() const noexcept {
    require_current_process_noexcept();
    require_shape_noexcept();
    return database_ != nullptr;
}

void SqliteAuthorizerOwner::require_current_process_noexcept() const noexcept {
    if (!process_id_.valid() ||
        !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_authorizer_owner_violation_noexcept();
    }
}

void SqliteAuthorizerOwner::require_shape_noexcept() const noexcept {
    const bool empty = database_ == nullptr && callback_ == nullptr &&
                       callback_context_ == nullptr;
    const bool live = database_ != nullptr && callback_ != nullptr &&
                      callback_context_ != nullptr;
    if ((!empty && !live) || callback_claim_.attached() != live) {
        fail_stop_on_authorizer_owner_violation_noexcept();
    }
}

}  // namespace anonsync::persistence
