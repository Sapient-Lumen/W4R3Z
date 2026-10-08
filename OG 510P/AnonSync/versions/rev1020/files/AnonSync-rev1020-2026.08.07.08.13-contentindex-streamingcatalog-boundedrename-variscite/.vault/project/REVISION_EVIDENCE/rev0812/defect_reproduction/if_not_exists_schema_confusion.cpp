#include <sqlite3.h>

#include <iostream>
#include <stdexcept>
#include <string>

namespace {
void exec_or_throw(sqlite3* db, const char* sql) {
    char* error = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &error);
    if (rc != SQLITE_OK) {
        const std::string detail = error == nullptr ? "unknown" : error;
        sqlite3_free(error);
        throw std::runtime_error(detail);
    }
}
}  // namespace

int main() {
    sqlite3* db = nullptr;
    if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 2;
    try {
        exec_or_throw(db,
            "CREATE VIEW sync_session_checkpoint_owner_modes AS "
            "SELECT 'victim' AS session_id, 'owner-required' AS ownership_mode, "
            "1 AS latest_owner_lock_epoch, 1 AS mode_updated_at_epoch, "
            "'' AS administrative_disable_evidence_id;");

        // This is the rev0811 bootstrap shape. SQLite reports success but does
        // not replace or validate the existing view.
        exec_or_throw(db,
            "CREATE TABLE IF NOT EXISTS sync_session_checkpoint_owner_modes("
            "session_id TEXT NOT NULL PRIMARY KEY,"
            "ownership_mode TEXT NOT NULL,"
            "latest_owner_lock_epoch INTEGER NOT NULL,"
            "mode_updated_at_epoch INTEGER NOT NULL,"
            "administrative_disable_evidence_id TEXT NOT NULL);");

        sqlite3_stmt* stmt = nullptr;
        if (sqlite3_prepare_v2(db,
                "SELECT type,sql FROM sqlite_schema "
                "WHERE name='sync_session_checkpoint_owner_modes';",
                -1, &stmt, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(db));
        }
        if (sqlite3_step(stmt) != SQLITE_ROW) {
            sqlite3_finalize(stmt);
            throw std::runtime_error("reserved object disappeared");
        }
        const char* type = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        const char* sql = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        std::cout << "bundled_sqlite=" << sqlite3_libversion() << "\n";
        std::cout << "create_table_if_not_exists_returned=SQLITE_OK\n";
        std::cout << "surviving_object_type=" << (type == nullptr ? "NULL" : type) << "\n";
        std::cout << "surviving_object_sql=" << (sql == nullptr ? "NULL" : sql) << "\n";
        const bool reproduced = type != nullptr && std::string(type) == "view";
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        std::cout << "SCHEMA_CONFUSION_REPRODUCED=" << (reproduced ? "true" : "false") << "\n";
        return reproduced ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << error.what() << "\n";
        sqlite3_close(db);
        return 3;
    }
}
