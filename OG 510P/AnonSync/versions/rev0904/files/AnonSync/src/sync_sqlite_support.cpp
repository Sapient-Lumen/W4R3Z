#include "sync_sqlite_support.hpp"

#include "persistence/sqlite_retained_callback_slots.hpp"
#include "sync_sqlite_busy_timeout_mutation_guard.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"
#include "sqlite_exact_value.hpp"

#include <limits>
#include <sstream>
#include <utility>

namespace anonsync {
namespace {

int sqlite_primary_result_code(int result_code) {
    return result_code & 0xff;
}

bool ascii_identifier_byte(unsigned char c) noexcept {
    return (c >= 'a' && c <= 'z') ||
           (c >= 'A' && c <= 'Z') ||
           (c >= '0' && c <= '9') || c == '_';
}

void require_statement_or_throw(sqlite3_stmt* stmt, const std::string& label) {
    if (stmt == nullptr) throw std::invalid_argument(label + ": statement handle is null");
}


std::string sqlite_failure_message(sqlite3* db,
                                   int result_code,
                                   const std::string& operation,
                                   const std::string& detail) {
    const int extended = db != nullptr ? sqlite3_extended_errcode(db) : result_code;
    const int effective_extended = extended != SQLITE_OK ? extended : result_code;
    std::ostringstream out;
    out << operation << ": ";
    if (!detail.empty()) {
        out << detail;
    } else {
        const char* message = db != nullptr ? sqlite3_errmsg(db) : sqlite3_errstr(result_code);
        out << (message != nullptr ? message : "unknown sqlite error");
    }
    out << " [" << sqlite_result_code_name(sqlite_primary_result_code(effective_extended))
        << " primary=" << sqlite_primary_result_code(effective_extended)
        << " extended=" << effective_extended << "]";
    return out.str();
}

}  // namespace

SyncSqliteException::SyncSqliteException(std::string message,
                                         std::string operation,
                                         int primary_result_code,
                                         int extended_result_code)
    : std::runtime_error(std::move(message)),
      operation_(std::move(operation)),
      primary_result_code_(primary_result_code),
      extended_result_code_(extended_result_code) {}

const std::string& SyncSqliteException::operation() const noexcept {
    return operation_;
}

int SyncSqliteException::primary_result_code() const noexcept {
    return primary_result_code_;
}

int SyncSqliteException::extended_result_code() const noexcept {
    return extended_result_code_;
}

sqlite3_stmt* SyncSqliteStmt::HandleView::get() const noexcept {
    if (owner_ == nullptr) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    return owner_->statement_owner_.get();
}

SyncSqliteStmt::SyncSqliteStmt() noexcept : stmt(*this) {}

SyncSqliteStmt::SyncSqliteStmt(
    SyncSqliteSerializedDbBorrow owner_borrow) noexcept
    : owner_borrow_(std::move(owner_borrow)), stmt(*this) {}

SyncSqliteStmt::SyncSqliteStmt(SyncSqliteStmt&& other) noexcept
    : stmt(*this) {
    other.require_transferable_noexcept();
    SyncSqliteSerializedDbBorrow incoming_owner(
        std::move(other.owner_borrow_));
    SyncSqliteStmtHandleSlot incoming_statement(
        std::move(other.statement_owner_));
    owner_borrow_ = std::move(incoming_owner);
    statement_owner_ = std::move(incoming_statement);
}

SyncSqliteStmt& SyncSqliteStmt::operator=(SyncSqliteStmt&& other) noexcept {
    if (this == std::addressof(other)) {
        require_transferable_noexcept();
        return *this;
    }

    // Validate and escrow every source capability before destination
    // finalization. sqlite3_finalize() may invoke binding destructors, so no
    // callback may observe an authoritative source that has not yet moved.
    other.require_transferable_noexcept();
    require_transferable_noexcept();
    SyncSqliteSerializedDbBorrow incoming_owner(
        std::move(other.owner_borrow_));
    SyncSqliteStmtHandleSlot incoming_statement(
        std::move(other.statement_owner_));
    reset();
    owner_borrow_ = std::move(incoming_owner);
    statement_owner_ = std::move(incoming_statement);
    return *this;
}

void SyncSqliteStmt::require_transferable_noexcept() const noexcept {
    // Raw-compatibility statements have no database-generation pin, while
    // typed statements do. Validate each present component independently.
    (void)owner_borrow_.get();
    (void)statement_owner_.get();
}

void SyncSqliteStmt::reset() noexcept {
    statement_owner_.reset();
    owner_borrow_.reset();
}

std::uint64_t SyncSqliteStmt::owner_generation() const noexcept {
    return owner_borrow_.generation();
}

SyncSqliteConnectionMutexMode
SyncSqliteStmt::owner_connection_mutex_mode() const noexcept {
    return owner_borrow_.connection_mutex_mode();
}

std::string sqlite_error_message(sqlite3* db, const std::string& prefix) {
    const char* msg = db != nullptr ? sqlite3_errmsg(db) : "sqlite database handle is null";
    return prefix + ": " + (msg != nullptr ? msg : "unknown sqlite error");
}

std::string sqlite_result_code_name(int result_code) {
    switch (sqlite_primary_result_code(result_code)) {
        case SQLITE_OK: return "SQLITE_OK";
        case SQLITE_ERROR: return "SQLITE_ERROR";
        case SQLITE_INTERNAL: return "SQLITE_INTERNAL";
        case SQLITE_PERM: return "SQLITE_PERM";
        case SQLITE_ABORT: return "SQLITE_ABORT";
        case SQLITE_BUSY: return "SQLITE_BUSY";
        case SQLITE_LOCKED: return "SQLITE_LOCKED";
        case SQLITE_NOMEM: return "SQLITE_NOMEM";
        case SQLITE_READONLY: return "SQLITE_READONLY";
        case SQLITE_INTERRUPT: return "SQLITE_INTERRUPT";
        case SQLITE_IOERR: return "SQLITE_IOERR";
        case SQLITE_CORRUPT: return "SQLITE_CORRUPT";
        case SQLITE_NOTFOUND: return "SQLITE_NOTFOUND";
        case SQLITE_FULL: return "SQLITE_FULL";
        case SQLITE_CANTOPEN: return "SQLITE_CANTOPEN";
        case SQLITE_PROTOCOL: return "SQLITE_PROTOCOL";
        case SQLITE_EMPTY: return "SQLITE_EMPTY";
        case SQLITE_SCHEMA: return "SQLITE_SCHEMA";
        case SQLITE_TOOBIG: return "SQLITE_TOOBIG";
        case SQLITE_CONSTRAINT: return "SQLITE_CONSTRAINT";
        case SQLITE_MISMATCH: return "SQLITE_MISMATCH";
        case SQLITE_MISUSE: return "SQLITE_MISUSE";
        case SQLITE_NOLFS: return "SQLITE_NOLFS";
        case SQLITE_AUTH: return "SQLITE_AUTH";
        case SQLITE_FORMAT: return "SQLITE_FORMAT";
        case SQLITE_RANGE: return "SQLITE_RANGE";
        case SQLITE_NOTADB: return "SQLITE_NOTADB";
        case SQLITE_NOTICE: return "SQLITE_NOTICE";
        case SQLITE_WARNING: return "SQLITE_WARNING";
        case SQLITE_ROW: return "SQLITE_ROW";
        case SQLITE_DONE: return "SQLITE_DONE";
        default: return "SQLITE_UNKNOWN";
    }
}

[[noreturn]] void throw_sqlite_exception(sqlite3* db,
                                         int result_code,
                                         const std::string& operation,
                                         const std::string& detail) {
    int extended = db != nullptr ? sqlite3_extended_errcode(db) : result_code;
    if (extended == SQLITE_OK) extended = result_code;
    throw SyncSqliteException(sqlite_failure_message(db, result_code, operation, detail),
                              operation,
                              sqlite_primary_result_code(extended),
                              extended);
}

void sqlite_set_busy_timeout_or_throw(sqlite3* db,
                                      int milliseconds,
                                      const std::string& label) {
    if (db == nullptr) {
        throw std::invalid_argument(label + ": database handle is null");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "SQLite busy-timeout configuration requires a nonempty diagnostic label");
    }
    if (milliseconds < 0) {
        throw std::invalid_argument(
            label + ": busy timeout must be nonnegative milliseconds");
    }

    SyncSqliteBusyTimeoutMutationGuard mutation_guard(
        db, label + " busy-timeout replacement fence");
    if (sqlite3_get_clientdata(
            db,
            persistence::kSqliteBusyHandlerOwnerClientDataName) != nullptr) {
        throw std::logic_error(
            label +
            ": cannot replace a live AnonSync SQLite busy-handler owner");
    }

    const int result = sqlite3_busy_timeout(db, milliseconds);
    if (result != SQLITE_OK) {
        throw_sqlite_exception(db, result, label);
    }
}

void sqlite_set_busy_timeout_or_throw(SyncSqliteDbHandleSlot& db,
                                      int milliseconds,
                                      const std::string& label) {
    SyncSqliteSerializedDbBorrow owner =
        borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " typed busy-timeout configuration");
    sqlite_set_busy_timeout_or_throw(owner.get(), milliseconds, label);
}

void sqlite_exec_or_throw(sqlite3* db, const std::string& sql, const std::string& label) {
    if (db == nullptr) throw std::invalid_argument(label + ": database handle is null");
    if (sql.empty()) throw std::invalid_argument(label + ": SQL is empty");
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    if (rc != SQLITE_OK) {
        // sqlite3_exec() allocates its optional errmsg through sqlite3_malloc().
        // The connection already retains the same diagnostic via sqlite3_errmsg(),
        // so requesting a second buffer only adds an OOM cut and an ownership edge.
        throw_sqlite_exception(db, rc, label);
    }
}

void sqlite_exec_or_throw(SyncSqliteDbHandleSlot& db,
                          const std::string& sql,
                          const std::string& label) {
    SyncSqliteSerializedDbBorrow owner =
        borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " typed SQLite execution");
    sqlite_exec_or_throw(owner.get(), sql, label);
}

void SyncSqliteStmt::prepare_or_throw(
    sqlite3* db,
    const std::string& sql,
    const std::string& label) {
    if (db == nullptr) throw std::invalid_argument(label + ": database handle is null");
    if (sql.empty()) throw std::invalid_argument(label + ": SQL is empty");
    if (sql.size() > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        throw std::runtime_error(label + ": SQL exceeds SQLite prepare length range");
    }
    const char* tail = nullptr;
    const int rc = sqlite3_prepare_v3(db,
                                      sql.data(),
                                      static_cast<int>(sql.size()),
                                      SQLITE_PREPARE_PERSISTENT,
                                      statement_owner_.out(),
                                      &tail);
    if (rc != SQLITE_OK) throw_sqlite_exception(db, rc, label);
    if (statement_owner_ == nullptr) throw std::runtime_error(label + ": SQL produced no statement");
    while (tail != nullptr && *tail != '\0') {
        const unsigned char c = static_cast<unsigned char>(*tail);
        if (c != ' ' && c != '\t' && c != '\r' && c != '\n' && c != ';') {
            throw std::runtime_error(label + ": trailing SQL is not permitted");
        }
        ++tail;
    }
}

SyncSqliteStmt sqlite_prepare_or_throw(sqlite3* db,
                                      const std::string& sql,
                                      const std::string& label) {
    SyncSqliteStmt out;
    out.prepare_or_throw(db, sql, label);
    return out;
}

SyncSqliteStmt sqlite_prepare_or_throw(SyncSqliteDbHandleSlot& db,
                                      const std::string& sql,
                                      const std::string& label) {
    SyncSqliteSerializedDbBorrow owner =
        borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " typed SQLite prepare");
    sqlite3* const raw = owner.get();
    SyncSqliteStmt out(std::move(owner));
    out.prepare_or_throw(raw, sql, label);
    return out;
}

void sqlite_bind_text_or_throw(sqlite3_stmt* stmt, int index, const std::string& value, const std::string& label) {
    require_statement_or_throw(stmt, label);
    const int rc = sqlite3_bind_text64(stmt,
                                       index,
                                       value.data(),
                                       static_cast<sqlite3_uint64>(value.size()),
                                       SQLITE_TRANSIENT,
                                       SQLITE_UTF8);
    if (rc != SQLITE_OK) throw_sqlite_exception(sqlite3_db_handle(stmt), rc, label + " bind text");
}

void sqlite_bind_blob_or_throw(sqlite3_stmt* stmt,
                               int index,
                               const std::string& value,
                               const std::string& label) {
    require_statement_or_throw(stmt, label);
    const void* bytes = value.empty()
        ? static_cast<const void*>("")
        : static_cast<const void*>(value.data());
    const int rc = sqlite3_bind_blob64(stmt,
                                       index,
                                       bytes,
                                       static_cast<sqlite3_uint64>(value.size()),
                                       SQLITE_TRANSIENT);
    if (rc != SQLITE_OK) {
        throw_sqlite_exception(sqlite3_db_handle(stmt), rc, label + " bind blob");
    }
}

void sqlite_bind_bool_or_throw(sqlite3_stmt* stmt, int index, bool value, const std::string& label) {
    require_statement_or_throw(stmt, label);
    const int rc = sqlite3_bind_int64(stmt, index, value ? 1 : 0);
    if (rc != SQLITE_OK) throw_sqlite_exception(sqlite3_db_handle(stmt), rc, label + " bind bool");
}

sqlite3_int64 u64_to_sqlite_i64_or_throw(std::uint64_t value, const std::string& label) {
    if (value > static_cast<std::uint64_t>(std::numeric_limits<sqlite3_int64>::max())) {
        throw std::runtime_error(label + " exceeds sqlite int64 range");
    }
    return static_cast<sqlite3_int64>(value);
}

void sqlite_bind_u64_or_throw(sqlite3_stmt* stmt, int index, std::uint64_t value, const std::string& label) {
    require_statement_or_throw(stmt, label);
    const int rc = sqlite3_bind_int64(stmt, index, u64_to_sqlite_i64_or_throw(value, label));
    if (rc != SQLITE_OK) throw_sqlite_exception(sqlite3_db_handle(stmt), rc, label + " bind uint64");
}

void sqlite_step_done_or_throw(sqlite3_stmt* stmt, const std::string& label) {
    require_statement_or_throw(stmt, label);
    const int rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) throw_sqlite_exception(sqlite3_db_handle(stmt), rc, label);
    const int reset_rc = sqlite3_reset(stmt);
    if (reset_rc != SQLITE_OK) {
        throw_sqlite_exception(sqlite3_db_handle(stmt), reset_rc, label + " reset");
    }
    const int clear_rc = sqlite3_clear_bindings(stmt);
    if (clear_rc != SQLITE_OK) {
        throw_sqlite_exception(sqlite3_db_handle(stmt), clear_rc, label + " clear bindings");
    }
}

std::string sqlite_column_text_or_throw(sqlite3_stmt* stmt,
                                        int column,
                                        const std::string& label) {
    return persistence::sqlite_exact_text_or_throw(stmt, column, label);
}

std::string sqlite_column_text_or_throw(sqlite3_stmt* stmt,
                                        int column,
                                        std::uint64_t max_bytes,
                                        const std::string& label) {
    return persistence::sqlite_exact_text_or_throw(
        stmt, column, label, max_bytes);
}

std::string sqlite_column_blob_or_throw(sqlite3_stmt* stmt,
                                        int column,
                                        std::uint64_t max_bytes,
                                        const std::string& label) {
    return persistence::sqlite_exact_blob_or_throw(
        stmt, column, label, max_bytes);
}

std::int64_t sqlite_column_i64_or_throw(sqlite3_stmt* stmt,
                                        int column,
                                        const std::string& label) {
    return persistence::sqlite_exact_i64_or_throw(stmt, column, label);
}

std::uint64_t sqlite_column_u64_or_throw(sqlite3_stmt* stmt,
                                         int column,
                                         const std::string& label) {
    return persistence::sqlite_exact_u64_or_throw(stmt, column, label);
}

bool sqlite_column_bool_or_throw(sqlite3_stmt* stmt, int column, const std::string& label) {
    const std::uint64_t value = sqlite_column_u64_or_throw(stmt, column, label);
    if (value > 1) throw std::runtime_error(label + ": boolean column is not 0 or 1");
    return value == 1;
}

std::uint64_t sqlite_count_for_session_or_throw(sqlite3* db,
                                                const std::string& sql,
                                                const std::string& session_id,
                                                const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db, sql, label);
    sqlite_bind_text_or_throw(stmt.stmt, 1, session_id, label + " session");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " count query");
    const std::uint64_t value = sqlite_column_u64_or_throw(stmt.stmt, 0, label);
    const int trailing_rc = sqlite3_step(stmt.stmt);
    if (trailing_rc != SQLITE_DONE) {
        if (trailing_rc == SQLITE_ROW) {
            throw std::runtime_error(label + ": count query returned more than one row");
        }
        throw_sqlite_exception(db, trailing_rc, label + " trailing row check");
    }
    return value;
}

std::uint64_t sqlite_count_for_session_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& sql,
    const std::string& session_id,
    const std::string& label) {
    SyncSqliteSerializedDbBorrow owner =
        borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " typed SQLite count");
    return sqlite_count_for_session_or_throw(
        owner.get(), sql, session_id, label);
}

bool sqlite_table_exists_or_throw(sqlite3* db,
                                  const std::string& table_name,
                                  const std::string& label) {
    if (table_name.empty()) throw std::runtime_error(label + ": table name is empty");
    for (const char raw : table_name) {
        const auto c = static_cast<unsigned char>(raw);
        if (ascii_identifier_byte(c)) continue;
        throw std::runtime_error(label + ": table name is not a simple SQLite identifier");
    }
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db,
        "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='table' AND name=?;",
        label + " table existence prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, table_name, label + " table name");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " table existence query");
    const bool exists =
        sqlite_column_u64_or_throw(stmt.stmt, 0, label + " table existence") != 0;
    const int trailing_rc = sqlite3_step(stmt.stmt);
    if (trailing_rc != SQLITE_DONE) {
        if (trailing_rc == SQLITE_ROW) {
            throw std::runtime_error(label + ": table existence query returned more than one row");
        }
        throw_sqlite_exception(db, trailing_rc, label + " table existence trailing row check");
    }
    return exists;
}

bool sqlite_table_exists_or_throw(SyncSqliteDbHandleSlot& db,
                                  const std::string& table_name,
                                  const std::string& label) {
    SyncSqliteSerializedDbBorrow owner =
        borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " typed SQLite table probe");
    return sqlite_table_exists_or_throw(owner.get(), table_name, label);
}

bool sqlite_simple_identifier_ok(const std::string& identifier) {
    if (identifier.empty()) return false;
    for (const char raw : identifier) {
        const auto c = static_cast<unsigned char>(raw);
        if (ascii_identifier_byte(c)) continue;
        return false;
    }
    return true;
}

bool sqlite_table_column_exists_or_throw(sqlite3* db,
                                         const std::string& table_name,
                                         const std::string& column_name,
                                         const std::string& label) {
    if (!sqlite_simple_identifier_ok(table_name) || !sqlite_simple_identifier_ok(column_name)) {
        throw std::runtime_error(label + ": table or column name is not a simple SQLite identifier");
    }
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db,
        "PRAGMA main.table_xinfo(" + table_name + ");",
        label + " column existence prepare");
    while (true) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) return false;
        if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " column existence query");
        if (sqlite_column_text_or_throw(stmt.stmt, 1, label + " column name") == column_name) return true;
    }
}

bool sqlite_table_column_exists_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& table_name,
    const std::string& column_name,
    const std::string& label) {
    SyncSqliteSerializedDbBorrow owner =
        borrow_sync_sqlite_serialized_db_or_throw(
            db, label + " typed SQLite column probe");
    return sqlite_table_column_exists_or_throw(
        owner.get(), table_name, column_name, label);
}

}  // namespace anonsync
