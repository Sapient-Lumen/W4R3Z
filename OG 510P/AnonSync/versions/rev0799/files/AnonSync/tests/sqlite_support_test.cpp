#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

struct TestState {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }

    template <typename Fn>
    void require_throws(Fn&& fn, const std::string& label) {
        try {
            fn();
            require(false, label);
        } catch (...) {
            require(true, label);
        }
    }
};

anonsync::SyncSqliteDb open_memory_database() {
    anonsync::SyncSqliteDb owner;
    const int rc = sqlite3_open_v2(":memory:",
                                   owner.db.out(),
                                   SQLITE_OPEN_READWRITE |
                                       SQLITE_OPEN_CREATE |
                                       SQLITE_OPEN_FULLMUTEX,
                                   nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "sqlite support test could not open memory database"));
    }
    const int extended_rc = sqlite3_extended_result_codes(owner.db, 1);
    if (extended_rc != SQLITE_OK) {
        anonsync::throw_sqlite_exception(owner.db,
                                         extended_rc,
                                         "sqlite support test extended result codes");
    }
    return owner;
}

std::uint64_t scalar_count(sqlite3* db, const std::string& sql) {
    anonsync::SyncSqliteStmt stmt =
        anonsync::sqlite_prepare_or_throw(db, sql, "sqlite support scalar count");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) {
        anonsync::throw_sqlite_exception(db, rc, "sqlite support scalar count query");
    }
    return anonsync::sqlite_column_u64_or_throw(stmt.stmt, 0, "sqlite support scalar count");
}

}  // namespace

int main() {
    TestState test;
    try {
        anonsync::SyncSqliteDb db = open_memory_database();
        test.require(db.db != nullptr, "database owner holds opened handle");

        anonsync::SyncSqliteDb moved = std::move(db);
        test.require(db.db == nullptr && moved.db != nullptr,
                     "database owner move constructor transfers handle exactly once");
        db = std::move(moved);
        test.require(moved.db == nullptr && db.db != nullptr,
                     "database owner move assignment transfers handle exactly once");

        const std::uint64_t first_owner_generation = db.db.generation();
        test.require(first_owner_generation != 0,
                     "opened database minted a nonzero owner generation");
        {
            anonsync::SyncSqliteStmt bound = anonsync::sqlite_prepare_or_throw(
                db.db, "SELECT 1;", "sqlite support owner-generation statement");
            test.require(bound.owner_generation() == first_owner_generation &&
                             db.db.active_borrows() == 1,
                         "prepared statement pins the exact owner generation");
            anonsync::SyncSqliteDb moved_with_borrow = std::move(db);
            test.require(db.db.empty() &&
                             moved_with_borrow.db.active_borrows() == 1 &&
                             bound.owner_generation() == first_owner_generation,
                         "owner move preserves a live generation-bound statement");
            test.require(sqlite3_step(bound.stmt) == SQLITE_ROW,
                         "generation-bound statement remains usable after owner move");
            db = std::move(moved_with_borrow);
            bound.reset();
            test.require(db.db.active_borrows() == 0,
                         "statement reset finalizes before releasing its owner pin");
        }

        anonsync::sqlite_exec_or_throw(
            db.db,
            "CREATE TABLE records("
            "id INTEGER PRIMARY KEY,"
            "session_id TEXT NOT NULL,"
            "txt TEXT NOT NULL UNIQUE,"
            "payload BLOB NOT NULL,"
            "flag INTEGER NOT NULL,"
            "n INTEGER NOT NULL);",
            "sqlite support test schema");
        test.require(anonsync::sqlite_table_exists_or_throw(
                         db.db, "records", "sqlite support table exists"),
                     "table existence helper finds present table");
        test.require(!anonsync::sqlite_table_exists_or_throw(
                         db.db, "missing", "sqlite support missing table"),
                     "table existence helper reports absent table");
        test.require(anonsync::sqlite_table_column_exists_or_throw(
                         db.db, "records", "payload", "sqlite support column exists"),
                     "column existence helper finds present column");
        test.require(!anonsync::sqlite_table_column_exists_or_throw(
                         db.db, "records", "missing", "sqlite support missing column"),
                     "column existence helper reports absent column");
        anonsync::sqlite_exec_or_throw(
            db.db,
            "CREATE TEMP TABLE records(temp_only_column TEXT NOT NULL);",
            "sqlite support temp shadow table");
        test.require(anonsync::sqlite_table_column_exists_or_throw(
                         db.db,
                         "records",
                         "payload",
                         "sqlite support main column through temp shadow"),
                     "column existence helper ignores a TEMP same-name table");
        test.require(!anonsync::sqlite_table_column_exists_or_throw(
                         db.db,
                         "records",
                         "temp_only_column",
                         "sqlite support temp-only column shadow"),
                     "column existence helper never reports a TEMP-only column");
        anonsync::sqlite_exec_or_throw(
            db.db, "DROP TABLE temp.records;", "sqlite support drop temp shadow table");
        anonsync::sqlite_exec_or_throw(
            db.db,
            "CREATE TEMP TABLE temp_only(value INTEGER);",
            "sqlite support temp-only table");
        test.require(!anonsync::sqlite_table_exists_or_throw(
                         db.db, "temp_only", "sqlite support temp-only table existence"),
                     "table existence helper does not mistake TEMP state for durable state");
        anonsync::sqlite_exec_or_throw(
            db.db, "DROP TABLE temp.temp_only;", "sqlite support drop temp-only table");

        const std::string binary_payload("A\0B\0C", 5);
        anonsync::SyncSqliteTransactionAuthority committed_authority;
        {
            anonsync::SyncSqliteTransaction tx(db.db, "sqlite support committed transaction");
            test.require(db.db.active_borrows() == 1,
                         "active typed transaction pins the exact owner generation");
            committed_authority = tx.authority();
            test.require(tx.active(), "transaction guard reports active after begin");
            test.require(tx.authorizes(db.db) && tx.authorizes_write(db.db),
                         "immediate transaction issues exact write authority");
            test.require(committed_authority.authorizes_write(db.db),
                         "copied transaction lease observes exact live write generation");
            anonsync::SyncSqliteStmt insert = anonsync::sqlite_prepare_or_throw(
                db.db,
                "INSERT INTO records(id,session_id,txt,payload,flag,n) VALUES(?,?,?,?,?,?);",
                "sqlite support insert prepare");
            test.require(db.db.active_borrows() == 2 &&
                             insert.owner_generation() == db.db.generation(),
                         "transaction and statement hold independent exact-generation pins");
            anonsync::sqlite_bind_u64_or_throw(insert.stmt, 1, 1, "record id");
            anonsync::sqlite_bind_text_or_throw(insert.stmt, 2, "session-a", "record session");
            anonsync::sqlite_bind_text_or_throw(insert.stmt, 3, "alpha", "record text");
            anonsync::sqlite_bind_blob_or_throw(insert.stmt, 4, binary_payload, "record payload");
            anonsync::sqlite_bind_bool_or_throw(insert.stmt, 5, true, "record flag");
            anonsync::sqlite_bind_u64_or_throw(insert.stmt, 6, 42, "record integer");
            anonsync::sqlite_step_done_or_throw(insert.stmt, "record insert");

            // sqlite_step_done_or_throw resets and clears the reusable statement.
            anonsync::sqlite_bind_u64_or_throw(insert.stmt, 1, 2, "record two id");
            anonsync::sqlite_bind_text_or_throw(insert.stmt, 2, "session-a", "record two session");
            anonsync::sqlite_bind_text_or_throw(insert.stmt, 3, "beta", "record two text");
            anonsync::sqlite_bind_blob_or_throw(insert.stmt, 4, std::string(), "record two payload");
            anonsync::sqlite_bind_bool_or_throw(insert.stmt, 5, false, "record two flag");
            anonsync::sqlite_bind_u64_or_throw(insert.stmt, 6, 7, "record two integer");
            anonsync::sqlite_step_done_or_throw(insert.stmt, "record two insert");
            tx.commit();
            test.require(db.db.active_borrows() == 1,
                         "commit releases the transaction pin before guard destruction");
            test.require(!tx.active(), "transaction guard reports inactive after commit");
            test.require(!committed_authority.authorizes(db.db),
                         "commit revokes every lease for the exact transaction generation");
        }
        test.require(db.db.active_borrows() == 0,
                     "statement destruction releases the final owner-generation pin");
        test.require(!committed_authority.authorizes(db.db),
                     "destroyed committed guard cannot revive an ended lease");
        {
            anonsync::SyncSqliteTransaction read_tx(
                db.db,
                "sqlite support read snapshot authority",
                anonsync::SyncSqliteTransactionMode::Deferred);
            const anonsync::SyncSqliteTransactionAuthority read_authority =
                read_tx.authority();
            test.require(read_authority.authorizes(db.db) &&
                             !read_authority.authorizes_snapshot(db.db),
                         "deferred transaction is active before a main snapshot exists");
            test.require(scalar_count(db.db, "SELECT COUNT(*) FROM records;") == 2,
                         "read authority fixture established a snapshot");
            test.require(read_authority.authorizes_snapshot(db.db) &&
                             !read_authority.authorizes_write(db.db),
                         "read lease distinguishes snapshot authority from write authority");
            read_tx.commit();
            test.require(!read_authority.authorizes(db.db),
                         "read snapshot lease is revoked at commit");
        }
        {
            anonsync::SyncSqliteTransaction next_generation(
                db.db, "sqlite support next transaction generation");
            test.require(next_generation.authorizes_write(db.db),
                         "later transaction generation has live write authority");
            test.require(!committed_authority.authorizes(db.db),
                         "old lease cannot authorize a later transaction on the same handle");
            next_generation.rollback();
        }
        {
            anonsync::SyncSqliteDb other = open_memory_database();
            anonsync::SyncSqliteTransaction other_tx(
                other.db, "sqlite support other connection authority");
            test.require(!other_tx.authorizes(db.db) && other_tx.authorizes(other.db),
                         "transaction authority is bound to one exact SQLite handle");
            other_tx.rollback();
        }
        anonsync::SyncSqliteTransactionAuthority destructor_authority;
        {
            anonsync::SyncSqliteTransaction destructor_tx(
                db.db, "sqlite support destructor authority revocation");
            destructor_authority = destructor_tx.authority();
            test.require(destructor_authority.authorizes_write(db.db),
                         "destructor test acquired live authority");
        }
        test.require(!destructor_authority.authorizes(db.db),
                     "guard destruction revokes authority after implicit rollback");
        anonsync::SyncSqliteTransactionAuthority bypassed_boundary_authority;
        {
            anonsync::SyncSqliteTransaction bypassed_boundary(
                db.db, "sqlite support bypassed boundary detection");
            bypassed_boundary_authority = bypassed_boundary.authority();
            anonsync::sqlite_exec_or_throw(
                db.db,
                "COMMIT;",
                "sqlite support deliberate raw commit misuse");
            test.require(!bypassed_boundary.active() &&
                             !bypassed_boundary_authority.authorizes(db.db),
                         "observing a bypassed boundary permanently revokes its generation");
            test.require_throws(
                [&] { bypassed_boundary.commit(); },
                "revoked guard refuses to commit a transaction boundary it no longer owns");
            bypassed_boundary.rollback();
            test.require(!bypassed_boundary.active(),
                         "rollback disarms a guard after SQLite already ended its boundary");
            anonsync::SyncSqliteTransaction later_generation(
                db.db, "sqlite support generation after bypassed boundary");
            test.require(!bypassed_boundary_authority.authorizes(db.db) &&
                             later_generation.authorizes_write(db.db),
                         "revoked bypassed lease cannot revive in a later transaction");
            later_generation.rollback();
        }

        test.require(scalar_count(db.db, "SELECT COUNT(*) FROM records;") == 2,
                     "committed rows survive transaction guard scope");
        test.require(anonsync::sqlite_count_for_session_or_throw(
                         db.db,
                         "SELECT COUNT(*) FROM records WHERE session_id=?;",
                         "session-a",
                         "sqlite support session count") == 2,
                     "session count helper binds and reads exact integer result");

        {
            anonsync::SyncSqliteStmt row = anonsync::sqlite_prepare_or_throw(
                db.db,
                "SELECT txt,payload,flag,n FROM records WHERE id=1;",
                "sqlite support row prepare");
            test.require(sqlite3_step(row.stmt) == SQLITE_ROW,
                         "row query returns one row");
            test.require(anonsync::sqlite_column_text_or_throw(
                             row.stmt, 0, "row text") == "alpha",
                         "text column helper preserves exact bytes");
            test.require(anonsync::sqlite_column_blob_or_throw(
                             row.stmt, 1, 5, "row blob") == binary_payload,
                         "blob column helper preserves embedded NUL bytes");
            test.require(anonsync::sqlite_column_bool_or_throw(
                             row.stmt, 2, "row bool"),
                         "boolean column helper accepts exact integer one");
            test.require(anonsync::sqlite_column_u64_or_throw(
                             row.stmt, 3, "row integer") == 42,
                         "integer column helper reads nonnegative integer");
            test.require_throws(
                [&] { (void)anonsync::sqlite_column_blob_or_throw(
                          row.stmt, 1, 4, "bounded row blob"); },
                "blob helper rejects values above the caller bound");
        }

        {
            anonsync::SyncSqliteTransaction tx(db.db, "sqlite support destructor rollback");
            anonsync::sqlite_exec_or_throw(
                db.db,
                "INSERT INTO records(id,session_id,txt,payload,flag,n) "
                "VALUES(3,'session-b','gamma',x'',0,1);",
                "sqlite support rollback insert");
        }
        test.require(scalar_count(db.db, "SELECT COUNT(*) FROM records;") == 2,
                     "transaction destructor rolls back uncommitted work");

        {
            anonsync::SyncSqliteTransaction tx(db.db, "sqlite support explicit rollback");
            anonsync::sqlite_exec_or_throw(
                db.db,
                "INSERT INTO records(id,session_id,txt,payload,flag,n) "
                "VALUES(4,'session-b','delta',x'',0,1);",
                "sqlite support explicit rollback insert");
            tx.rollback();
            test.require(!tx.active(), "explicit rollback deactivates transaction guard");
        }
        test.require(scalar_count(db.db, "SELECT COUNT(*) FROM records;") == 2,
                     "explicit rollback removes uncommitted work");

        {
            anonsync::SyncSqliteTransaction exclusive(
                db.db,
                "sqlite support exclusive transaction",
                anonsync::SyncSqliteTransactionMode::Exclusive);
            test.require(exclusive.authorizes_write(db.db),
                         "exclusive typed mode establishes write authority");
            anonsync::sqlite_exec_or_throw(
                db.db,
                "INSERT INTO records(id,session_id,txt,payload,flag,n) "
                "VALUES(5,'session-c','epsilon',x'',1,9);",
                "sqlite support exclusive insert");
            exclusive.commit();
        }
        test.require(scalar_count(db.db, "SELECT COUNT(*) FROM records;") == 3,
                     "exclusive typed transaction commits through guard");

        test.require_throws(
            [&] {
                anonsync::SyncSqliteTransaction invalid_mode(
                    db.db,
                    "invalid typed transaction mode",
                    static_cast<anonsync::SyncSqliteTransactionMode>(255));
            },
            "transaction guard rejects an invalid typed begin mode");
        test.require(sqlite3_get_autocommit(db.db) != 0,
                     "failed transaction construction leaves the connection in autocommit");
        {
            anonsync::SyncSqliteTransaction outer(db.db, "outer transaction");
            test.require_throws(
                [&] { anonsync::SyncSqliteTransaction nested(db.db, "nested transaction"); },
                "transaction guard refuses nested begin");
            outer.rollback();
        }

        test.require_throws(
            [&] { (void)anonsync::sqlite_prepare_or_throw(
                      db.db, "SELECT 1; SELECT 2;", "trailing SQL test"); },
            "prepare helper rejects trailing executable SQL");
        test.require_throws(
            [&] { (void)anonsync::sqlite_prepare_or_throw(db.db, "", "empty SQL test"); },
            "prepare helper rejects empty SQL");
        test.require_throws(
            [&] { anonsync::sqlite_exec_or_throw(nullptr, "SELECT 1;", "null db test"); },
            "exec helper rejects null database handle");
        test.require_throws(
            [&] { (void)anonsync::u64_to_sqlite_i64_or_throw(
                      std::numeric_limits<std::uint64_t>::max(), "overflow test"); },
            "uint64 conversion rejects values outside SQLite int64 range");

        {
            anonsync::SyncSqliteStmt text_value = anonsync::sqlite_prepare_or_throw(
                db.db, "SELECT '42';", "type text prepare");
            test.require(sqlite3_step(text_value.stmt) == SQLITE_ROW,
                         "text type fixture returns row");
            test.require_throws(
                [&] { (void)anonsync::sqlite_column_u64_or_throw(
                          text_value.stmt, 0, "text as integer"); },
                "integer helper rejects SQLite text coercion");
        }
        {
            anonsync::SyncSqliteStmt integer_value = anonsync::sqlite_prepare_or_throw(
                db.db, "SELECT 42;", "type integer prepare");
            test.require(sqlite3_step(integer_value.stmt) == SQLITE_ROW,
                         "integer type fixture returns row");
            test.require_throws(
                [&] { (void)anonsync::sqlite_column_text_or_throw(
                          integer_value.stmt, 0, "integer as text"); },
                "text helper rejects SQLite integer coercion");
        }
        {
            anonsync::SyncSqliteStmt negative = anonsync::sqlite_prepare_or_throw(
                db.db, "SELECT -1;", "negative integer prepare");
            test.require(sqlite3_step(negative.stmt) == SQLITE_ROW,
                         "negative fixture returns row");
            test.require_throws(
                [&] { (void)anonsync::sqlite_column_u64_or_throw(
                          negative.stmt, 0, "negative unsigned value"); },
                "unsigned integer helper rejects negative values");
        }
        {
            anonsync::SyncSqliteStmt invalid_bool = anonsync::sqlite_prepare_or_throw(
                db.db, "SELECT 2;", "invalid bool prepare");
            test.require(sqlite3_step(invalid_bool.stmt) == SQLITE_ROW,
                         "invalid bool fixture returns row");
            test.require_throws(
                [&] { (void)anonsync::sqlite_column_bool_or_throw(
                          invalid_bool.stmt, 0, "invalid bool"); },
                "boolean helper rejects integers outside zero and one");
        }

        bool captured_constraint = false;
        try {
            anonsync::sqlite_exec_or_throw(
                db.db,
                "INSERT INTO records(id,session_id,txt,payload,flag,n) "
                "VALUES(6,'session-z','alpha',x'',0,1);",
                "unique constraint fixture");
        } catch (const anonsync::SyncSqliteException& error) {
            captured_constraint =
                error.primary_result_code() == SQLITE_CONSTRAINT &&
                error.extended_result_code() == SQLITE_CONSTRAINT_UNIQUE &&
                error.operation() == "unique constraint fixture" &&
                std::string(error.what()).find("SQLITE_CONSTRAINT") != std::string::npos;
        }
        test.require(captured_constraint,
                     "structured exception preserves operation and extended constraint code");

        test.require(anonsync::sqlite_simple_identifier_ok("Table_123"),
                     "identifier helper accepts portable ASCII identifier");
        test.require(!anonsync::sqlite_simple_identifier_ok("table-name") &&
                         !anonsync::sqlite_simple_identifier_ok("t\xC3\xA9") &&
                         !anonsync::sqlite_simple_identifier_ok(""),
                     "identifier helper rejects punctuation, non-ASCII, and empty input");
        test.require_throws(
            [&] { (void)anonsync::sqlite_table_exists_or_throw(
                      db.db, "records;DROP_TABLE", "unsafe table name"); },
            "table existence helper rejects non-identifier SQL material");

        std::cout << "anonsync sqlite support test runtime=" << sqlite3_libversion()
                  << " passed=" << test.passed
                  << " failed=" << test.failed << "\n";
        return test.failed == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "sqlite support test fatal: " << error.what() << "\n";
        return 2;
    }
}
