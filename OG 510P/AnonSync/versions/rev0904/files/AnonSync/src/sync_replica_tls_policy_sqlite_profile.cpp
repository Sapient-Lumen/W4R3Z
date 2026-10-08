#include "sync_replica_tls_policy_sqlite_profile.hpp"

#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {
namespace {

void validate_backend_disposition_or_throw(
    SyncReplicaTlsPolicySqliteBackendDisposition disposition,
    const std::string& label) {
    switch (disposition) {
        case SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed:
        case SyncReplicaTlsPolicySqliteBackendDisposition::
            DetachedBootstrapImage:
            return;
    }
    throw std::invalid_argument(
        label + " TLS policy SQLite backend disposition is invalid");
}

[[nodiscard]] int step_row_or_done_or_throw(
    sqlite3_stmt* statement,
    const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result != SQLITE_ROW && result != SQLITE_DONE) {
        throw_sqlite_exception(sqlite3_db_handle(statement), result, label);
    }
    return result;
}

[[nodiscard]] std::string pragma_text_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string_view sql,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, std::string(sql), label + " prepare");
    if (step_row_or_done_or_throw(statement.stmt, label + " step") !=
        SQLITE_ROW) {
        throw std::runtime_error(label + " returned no row");
    }
    const std::string value = sqlite_column_text_or_throw(
        statement.stmt, 0, 32U, label + " value");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " trailing step") != SQLITE_DONE) {
        throw std::runtime_error(label + " returned multiple rows");
    }
    return value;
}

[[nodiscard]] std::uint64_t pragma_u64_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string_view sql,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db, std::string(sql), label + " prepare");
    if (step_row_or_done_or_throw(statement.stmt, label + " step") !=
        SQLITE_ROW) {
        throw std::runtime_error(label + " returned no row");
    }
    const std::uint64_t value = sqlite_column_u64_or_throw(
        statement.stmt, 0, label + " value");
    if (step_row_or_done_or_throw(
            statement.stmt, label + " trailing step") != SQLITE_DONE) {
        throw std::runtime_error(label + " returned multiple rows");
    }
    return value;
}

void configure_db_config_or_throw(
    SyncSqliteDbHandleSlot& db,
    int option,
    int requested,
    const std::string& label) {
    sqlite3* const handle = db.get();
    if (handle == nullptr) {
        throw std::logic_error(label + " SQLite handle is inactive");
    }
    int observed = -1;
    const int result = sqlite3_db_config(handle, option, requested, &observed);
    if (result != SQLITE_OK) {
        throw_sqlite_exception(handle, result, label);
    }
    if (observed != requested) {
        throw std::runtime_error(
            label + " did not enter the requested connection state");
    }
}

void require_db_config_or_throw(
    SyncSqliteDbHandleSlot& db,
    int option,
    int expected,
    const std::string& label) {
    sqlite3* const handle = db.get();
    if (handle == nullptr) {
        throw std::logic_error(label + " SQLite handle is inactive");
    }
    int observed = -1;
    const int result = sqlite3_db_config(handle, option, -1, &observed);
    if (result != SQLITE_OK) {
        throw_sqlite_exception(handle, result, label);
    }
    if (observed != expected) {
        throw std::runtime_error(
            label + " connection profile changed after owner configuration");
    }
}

[[nodiscard]] SyncSqliteSerializedDbBorrow
retain_exact_serialized_database_or_throw(
    SyncSqliteDbHandleSlot& database,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "TLS policy SQLite connection binding label must not be empty");
    }
    return borrow_sync_sqlite_serialized_db_or_throw(
        database, label + " serialized database lifetime");
}

void require_connection_profile_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
#ifdef SQLITE_DBCONFIG_DEFENSIVE
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_DEFENSIVE, 1,
        label + " defensive mode");
#endif
#ifdef SQLITE_DBCONFIG_TRUSTED_SCHEMA
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_TRUSTED_SCHEMA, 0,
        label + " trusted schema");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_TRIGGER
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_TRIGGER, 0,
        label + " schema triggers");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_VIEW
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_VIEW, 0,
        label + " schema views");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION, 0,
        label + " load extension");
#endif
#ifdef SQLITE_DBCONFIG_DQS_DML
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_DQS_DML, 0,
        label + " DQS DML");
#endif
#ifdef SQLITE_DBCONFIG_DQS_DDL
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_DQS_DDL, 0,
        label + " DQS DDL");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0,
        label + " attach create");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE
    require_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0,
        label + " attach write");
#endif
#ifdef SQLITE_LIMIT_ATTACHED
    if (sqlite3_limit(db.get(), SQLITE_LIMIT_ATTACHED, -1) != 0) {
        throw std::runtime_error(
            label + " attached-database limit changed after owner configuration");
    }
#endif
#ifdef SQLITE_LIMIT_TRIGGER_DEPTH
    if (sqlite3_limit(db.get(), SQLITE_LIMIT_TRIGGER_DEPTH, -1) != 0) {
        throw std::runtime_error(
            label + " trigger-depth limit changed after owner configuration");
    }
#endif
    if (pragma_u64_or_throw(
            db, "PRAGMA trusted_schema;", label + " trusted_schema") != 0U ||
        pragma_u64_or_throw(
            db, "PRAGMA query_only;", label + " query_only") != 0U ||
        pragma_u64_or_throw(
            db, "PRAGMA read_uncommitted;", label + " read_uncommitted") != 0U ||
        pragma_u64_or_throw(
            db, "PRAGMA ignore_check_constraints;",
            label + " ignore_check_constraints") != 0U) {
        throw std::runtime_error(
            label + " mutable connection pragma escaped the owner profile");
    }

    SyncSqliteStmt databases = sqlite_prepare_or_throw(
        db, "PRAGMA database_list;", label + " database list prepare");
    for (;;) {
        const int step = step_row_or_done_or_throw(
            databases.stmt, label + " database list step");
        if (step == SQLITE_DONE) break;
        const std::string name = sqlite_column_text_or_throw(
            databases.stmt, 1, 32U, label + " database name");
        if (name != "main" && name != "temp") {
            throw std::runtime_error(
                label + " has an attached database outside owner authority");
        }
    }
}

}  // namespace

SyncReplicaTlsPolicySqliteConnectionBinding::
    SyncReplicaTlsPolicySqliteConnectionBinding(
        SyncSqliteDbHandleSlot& database,
        std::string label,
        SyncReplicaTlsPolicySqliteBackendDisposition disposition)
    : database_(database),
      retained_lifetime_(
          retain_exact_serialized_database_or_throw(database, label)),
      database_generation_(retained_lifetime_.generation()),
      label_(std::move(label)),
      disposition_(disposition) {
    validate_backend_disposition_or_throw(disposition_, label_);
    configure_sync_replica_tls_policy_sqlite_connection_or_throw(
        database_, label_ + " connection profile");
    const char* const observed_filename =
        sqlite3_db_filename(retained_lifetime_.get(), "main");
    if (disposition_ ==
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed) {
        database_filename_ =
            sync_replica_tls_policy_sqlite_main_filename_or_throw(
                database_, label_ + " main database");
        database_path_guard_ = guard_sqlite_path_family_or_throw(
            database_filename_, false, {"-journal", "-wal", "-shm"},
            label_ + " main database namespace");
        database_path_guard_.verify_open_database_or_throw(
            retained_lifetime_.get(),
            label_ + " main database open identity");
    } else if (observed_filename == nullptr || observed_filename[0] != '\0') {
        throw std::runtime_error(
            label_ + " detached bootstrap image unexpectedly names a file");
    }
    require_current_or_throw("construction");
}

SyncSqliteDbHandleSlot&
SyncReplicaTlsPolicySqliteConnectionBinding::database_or_throw(
    std::string_view operation_label) {
    require_current_or_throw(operation_label);
    return database_;
}

void SyncReplicaTlsPolicySqliteConnectionBinding::require_current_or_throw(
    std::string_view operation_label) {
    if (operation_label.empty()) {
        throw std::invalid_argument(
            "TLS policy SQLite binding operation label must not be empty");
    }
    sqlite3* const retained = retained_lifetime_.get();
    sqlite3* const current = database_.get();
    if (current != retained ||
        database_.generation() != database_generation_) {
        throw std::runtime_error(
            label_ + " exact SQLite handle-slot generation changed during " +
            std::string(operation_label));
    }
    const char* const observed_filename =
        sqlite3_db_filename(retained, "main");
    if (disposition_ ==
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed) {
        if (observed_filename == nullptr || observed_filename[0] == '\0' ||
            database_filename_ != observed_filename) {
            throw std::runtime_error(
                label_ + " exact SQLite main-database identity changed during " +
                std::string(operation_label));
        }
        database_path_guard_.verify_open_database_or_throw(
            retained, label_ + " exact SQLite path identity during " +
                          std::string(operation_label));
    } else if (observed_filename == nullptr || observed_filename[0] != '\0') {
        throw std::runtime_error(
            label_ + " detached SQLite image gained a filename during " +
            std::string(operation_label));
    }
}

void configure_sync_replica_tls_policy_sqlite_connection_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "TLS policy SQLite connection label must not be empty");
    }
    sqlite3* const handle = db.get();
    if (handle == nullptr) {
        throw std::logic_error(label + " SQLite handle is inactive");
    }
#ifdef SQLITE_DBCONFIG_DEFENSIVE
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_DEFENSIVE, 1,
        label + " enable defensive mode");
#endif
#ifdef SQLITE_DBCONFIG_TRUSTED_SCHEMA
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_TRUSTED_SCHEMA, 0,
        label + " disable trusted schema");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_TRIGGER
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_TRIGGER, 0,
        label + " disable schema triggers");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_VIEW
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_VIEW, 0,
        label + " disable schema views");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION, 0,
        label + " disable load extension");
#endif
#ifdef SQLITE_DBCONFIG_DQS_DML
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_DQS_DML, 0,
        label + " disable DQS DML");
#endif
#ifdef SQLITE_DBCONFIG_DQS_DDL
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_DQS_DDL, 0,
        label + " disable DQS DDL");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0,
        label + " disable attach create");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE
    configure_db_config_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0,
        label + " disable attach write");
#endif
#ifdef SQLITE_LIMIT_ATTACHED
    (void)sqlite3_limit(handle, SQLITE_LIMIT_ATTACHED, 0);
    if (sqlite3_limit(handle, SQLITE_LIMIT_ATTACHED, -1) != 0) {
        throw std::runtime_error(
            label + " could not disable attached databases");
    }
#endif
#ifdef SQLITE_LIMIT_TRIGGER_DEPTH
    (void)sqlite3_limit(handle, SQLITE_LIMIT_TRIGGER_DEPTH, 0);
    if (sqlite3_limit(handle, SQLITE_LIMIT_TRIGGER_DEPTH, -1) != 0) {
        throw std::runtime_error(
            label + " could not disable trigger recursion");
    }
#endif
    sqlite_exec_or_throw(
        db,
        "PRAGMA trusted_schema=OFF;"
        "PRAGMA query_only=OFF;"
        "PRAGMA read_uncommitted=OFF;"
        "PRAGMA ignore_check_constraints=OFF;",
        label + " configure connection pragmas");
}

std::string sync_replica_tls_policy_sqlite_main_filename_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "TLS policy SQLite filename label must not be empty");
    }
    sqlite3* const handle = db.get();
    if (handle == nullptr) {
        throw std::logic_error(label + " SQLite handle is inactive");
    }
    const char* const filename = sqlite3_db_filename(handle, "main");
    if (filename == nullptr || filename[0] == '\0') {
        throw std::runtime_error(
            label + " has no durable main filename");
    }
    return filename;
}

void require_distinct_sync_replica_tls_policy_sqlite_databases_or_throw(
    std::string_view first_filename,
    std::string_view second_filename,
    const std::string& label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "TLS policy SQLite distinct-database label must not be empty");
    }
    if (first_filename.empty() || second_filename.empty()) {
        throw std::invalid_argument(
            label + " cannot compare an empty database filename");
    }
    if (first_filename == second_filename) {
        throw std::invalid_argument(
            label + " uses the same main database file for both authorities");
    }

    std::error_code error;
    const bool equivalent = std::filesystem::equivalent(
        std::filesystem::path(first_filename),
        std::filesystem::path(second_filename), error);
    if (error) {
        throw std::runtime_error(
            label + " could not prove distinct database files: " +
            error.message());
    }
    if (equivalent) {
        throw std::invalid_argument(
            label + " main database filenames alias the same filesystem object");
    }
}

void attest_sync_replica_tls_policy_sqlite_backend_or_throw(
    SyncSqliteDbHandleSlot& db,
    std::string_view authority_noun,
    const std::string& label,
    SyncReplicaTlsPolicySqliteBackendDisposition disposition) {
    if (authority_noun.empty()) {
        throw std::invalid_argument(
            "TLS policy SQLite authority noun must not be empty");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "TLS policy SQLite backend label must not be empty");
    }
    validate_backend_disposition_or_throw(disposition, label);
    require_connection_profile_or_throw(db, label + " connection profile");
    sqlite3* const handle = db.get();
    if (handle == nullptr) {
        throw std::logic_error(label + " SQLite handle is inactive");
    }
    const std::string noun(authority_noun);
    const char* const filename = sqlite3_db_filename(handle, "main");
    if (disposition ==
        SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed) {
        (void)sync_replica_tls_policy_sqlite_main_filename_or_throw(
            db, label + " " + noun + " database");
    } else if (filename == nullptr || filename[0] != '\0') {
        throw std::runtime_error(
            label + " " + noun +
            " detached bootstrap image unexpectedly names a file");
    }
    if (sqlite3_db_readonly(handle, "main") != 0) {
        throw std::runtime_error(
            label + " " + noun +
            (disposition ==
                    SyncReplicaTlsPolicySqliteBackendDisposition::DurableNamed
                 ? " database is not writable durable authority"
                 : " detached bootstrap image is not writable"));
    }
    const std::string journal_mode = pragma_text_or_throw(
        db, "PRAGMA main.journal_mode;", label + " journal mode");
    if (disposition ==
        SyncReplicaTlsPolicySqliteBackendDisposition::DetachedBootstrapImage) {
        if (journal_mode != "memory") {
            throw std::runtime_error(
                label + " " + noun +
                " detached bootstrap image journal mode is not memory");
        }
        return;
    }
    if (journal_mode != "wal" && journal_mode != "delete" &&
        journal_mode != "truncate" && journal_mode != "persist") {
        throw std::runtime_error(
            label + " " + noun + " journal mode is not durable");
    }
    const std::uint64_t synchronous = pragma_u64_or_throw(
        db, "PRAGMA main.synchronous;", label + " synchronous mode");
    // WAL+FULL syncs the WAL at each commit. Rollback-journal FULL may omit the
    // extra directory/journal sync that EXTRA requests. These are necessary
    // SQLite policy observations, not a proof of the storage stack.
    const std::uint64_t required_synchronous =
        journal_mode == "wal" ? 2U : 3U;
    if (synchronous < required_synchronous) {
        throw std::runtime_error(
            label + " " + noun +
            (journal_mode == "wal"
                 ? " WAL synchronous mode is below FULL"
                 : " rollback-journal synchronous mode is below EXTRA"));
    }
}

}  // namespace anonsync
