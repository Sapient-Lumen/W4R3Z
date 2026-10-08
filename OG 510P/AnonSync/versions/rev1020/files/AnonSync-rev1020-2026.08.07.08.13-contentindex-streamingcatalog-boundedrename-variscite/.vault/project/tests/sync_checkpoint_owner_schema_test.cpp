#include "sync_checkpoint_owner_schema.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

namespace {

using anonsync::SyncSqliteDb;
using anonsync::SyncSqliteStmt;
using anonsync::sqlite_column_u64_or_throw;
using anonsync::sqlite_exec_or_throw;
using anonsync::sqlite_prepare_or_throw;
using anonsync::sync_checkpoint_owner_schema_internal::
    attest_checkpoint_owner_schema_or_throw;
using anonsync::sync_checkpoint_owner_schema_internal::
    ensure_checkpoint_owner_schema_or_throw;

constexpr std::string_view kRootDdl =
    "CREATE TABLE main.sync_session_checkpoints("
    "session_id TEXT PRIMARY KEY NOT NULL);";

constexpr std::string_view kOwnerLockDdl =
    "CREATE TABLE main.sync_session_resume_transfer_daemon_owner_locks("
    "session_id TEXT NOT NULL PRIMARY KEY REFERENCES "
    "sync_session_checkpoints(session_id) ON DELETE CASCADE,"
    "daemon_id TEXT NOT NULL,"
    "worker_id TEXT NOT NULL,"
    "owner_lock_id TEXT NOT NULL,"
    "owner_lock_epoch INTEGER NOT NULL CHECK(owner_lock_epoch > 0),"
    "acquired_at_epoch INTEGER NOT NULL CHECK(acquired_at_epoch > 0),"
    "expires_at_epoch INTEGER NOT NULL "
    "CHECK(expires_at_epoch > acquired_at_epoch),"
    "released_at_epoch INTEGER NOT NULL "
    "CHECK(released_at_epoch = 0 OR released_at_epoch >= acquired_at_epoch),"
    "lock_state TEXT NOT NULL CHECK(lock_state IN ('held','released')),"
    "updated_at_epoch INTEGER NOT NULL "
    "CHECK(updated_at_epoch >= acquired_at_epoch));";

constexpr std::string_view kOwnerModeDdl =
    "CREATE TABLE main.sync_session_checkpoint_owner_modes("
    "session_id TEXT NOT NULL PRIMARY KEY,"
    "ownership_mode TEXT NOT NULL CHECK(ownership_mode IN "
    "('owner-required','administratively-disabled')),"
    "latest_owner_lock_epoch INTEGER NOT NULL "
    "CHECK(latest_owner_lock_epoch > 0),"
    "mode_updated_at_epoch INTEGER NOT NULL "
    "CHECK(mode_updated_at_epoch > 0),"
    "administrative_disable_evidence_id TEXT NOT NULL,"
    "CHECK((ownership_mode='owner-required' AND "
    "administrative_disable_evidence_id='') OR "
    "(ownership_mode='administratively-disabled' AND "
    "administrative_disable_evidence_id LIKE "
    "'sync-checkpoint-owner-admin-disable:v1:%')));";

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void check(bool condition, std::string_view label) {
        if (condition) {
            ++passed;
            return;
        }
        ++failed;
        std::cerr << "FAIL: " << label << '\n';
    }
};

SyncSqliteDb open_memory_database() {
    SyncSqliteDb db;
    const int rc = sqlite3_open_v2(
        ":memory:",
        db.db.out(),
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error("owner schema test could not open SQLite database");
    }
    sqlite3_extended_result_codes(db.db.get(), 1);
    sqlite_exec_or_throw(
        db.db,
        "PRAGMA foreign_keys=ON;",
        "owner schema test foreign-key profile");
    return db;
}

void install_root_and_exact_lock(SyncSqliteDb& db) {
    sqlite_exec_or_throw(
        db.db,
        std::string(kRootDdl) + std::string(kOwnerLockDdl),
        "owner schema test exact root and lock");
}

std::uint64_t scalar_u64(sqlite3* db,
                         const std::string& sql,
                         const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db, sql, label + " prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) {
        anonsync::throw_sqlite_exception(db, rc, label + " query");
    }
    const std::uint64_t value =
        sqlite_column_u64_or_throw(stmt.stmt, 0, label + " value");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(label + " returned more than one row");
    }
    return value;
}

bool throws_with(const std::function<void()>& fn,
                 std::string_view expected_fragment) {
    try {
        fn();
    } catch (const std::exception& error) {
        return std::string(error.what()).find(expected_fragment) !=
               std::string::npos;
    }
    return false;
}

void test_clean_bootstrap_and_repeat(TestState& test) {
    SyncSqliteDb db = open_memory_database();
    install_root_and_exact_lock(db);

    ensure_checkpoint_owner_schema_or_throw(
        db.db.get(), "clean owner schema bootstrap");
    attest_checkpoint_owner_schema_or_throw(
        db.db.get(), "clean owner schema attestation");
    ensure_checkpoint_owner_schema_or_throw(
        db.db.get(), "repeated owner schema bootstrap");

    test.check(
        scalar_u64(
            db.db.get(),
            "SELECT COUNT(*) FROM main.sqlite_schema "
            "WHERE type='table' AND name="
            "'sync_session_checkpoint_owner_modes';",
            "clean owner mode count") == 1,
        "clean bootstrap creates exactly one durable owner-mode table");
    test.check(
        scalar_u64(
            db.db.get(),
            "SELECT COUNT(*) FROM main.sqlite_schema "
            "WHERE sql IS NOT NULL AND ("
            "name='sync_session_checkpoint_owner_modes' OR "
            "tbl_name='sync_session_checkpoint_owner_modes');",
            "clean owner mode SQL object count") == 1,
        "clean bootstrap leaves no owner-mode trigger or explicit index program");
}

void test_semantically_equivalent_formatting(TestState& test) {
    SyncSqliteDb db = open_memory_database();
    sqlite_exec_or_throw(
        db.db,
        "CrEaTe TaBlE main.sync_session_checkpoints("
        "SESSION_ID text primary key not null);"
        "create table main.sync_session_resume_transfer_daemon_owner_locks("
        "session_id text not null primary key references "
        "sync_session_checkpoints(session_id) on delete cascade,"
        "daemon_id text not null,worker_id text not null,"
        "owner_lock_id text not null,owner_lock_epoch integer not null "
        "check(owner_lock_epoch>0),acquired_at_epoch integer not null "
        "check(acquired_at_epoch>0),expires_at_epoch integer not null "
        "check(expires_at_epoch>acquired_at_epoch),"
        "released_at_epoch integer not null check(released_at_epoch=0 or "
        "released_at_epoch>=acquired_at_epoch),lock_state text not null "
        "check(lock_state in('held','released')),updated_at_epoch integer "
        "not null check(updated_at_epoch>=acquired_at_epoch));"
        "CREATE TABLE main.sync_session_checkpoint_owner_modes("
        "session_id text not null primary key,ownership_mode text not null "
        "check(ownership_mode in('owner-required',"
        "'administratively-disabled')),latest_owner_lock_epoch integer not "
        "null check(latest_owner_lock_epoch>0),mode_updated_at_epoch integer "
        "not null check(mode_updated_at_epoch>0),"
        "administrative_disable_evidence_id text not null,check(("
        "ownership_mode='owner-required' and "
        "administrative_disable_evidence_id='') or (ownership_mode="
        "'administratively-disabled' and administrative_disable_evidence_id "
        "like 'sync-checkpoint-owner-admin-disable:v1:%')));",
        "owner schema equivalent formatting fixture");

    ensure_checkpoint_owner_schema_or_throw(
        db.db.get(), "owner schema equivalent formatting");
    attest_checkpoint_owner_schema_or_throw(
        db.db.get(), "owner schema equivalent formatting reattestation");
    test.check(true,
               "schema identity accepts only formatting and unquoted-case drift");
}

void test_mode_lookalikes_fail_closed(TestState& test) {
    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            "CREATE VIEW main.sync_session_checkpoint_owner_modes AS "
            "SELECT 'x' AS session_id;",
            "owner mode hostile view");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner mode view refusal");
                },
                "not the exact main table object"),
            "a view cannot occupy the sticky owner-mode authority name");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            "CREATE TABLE main.sync_session_checkpoint_owner_modes("
            "session_id TEXT NOT NULL PRIMARY KEY,"
            "ownership_mode TEXT NOT NULL,"
            "latest_owner_lock_epoch INTEGER NOT NULL,"
            "mode_updated_at_epoch INTEGER NOT NULL,"
            "administrative_disable_evidence_id TEXT NOT NULL);",
            "owner mode permissive table");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner mode permissive refusal");
                },
                "exact reviewed schema SQL does not match"),
            "a column-compatible but constraint-free owner-mode table is rejected");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            std::string(kOwnerModeDdl) +
                "CREATE INDEX main.hostile_owner_mode_index ON "
                "sync_session_checkpoint_owner_modes(ownership_mode);",
            "owner mode explicit index");
        test.check(
            throws_with(
                [&] {
                    attest_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner mode index refusal");
                },
                "unexpected SQL-bearing index, trigger, or alias objects"),
            "an explicit owner-mode index is treated as unreviewed schema code");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            std::string(kOwnerModeDdl) +
                "CREATE TRIGGER main.hostile_owner_mode_trigger "
                "BEFORE UPDATE ON sync_session_checkpoint_owner_modes "
                "BEGIN SELECT 1; END;",
            "owner mode trigger");
        test.check(
            throws_with(
                [&] {
                    attest_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner mode trigger refusal");
                },
                "unexpected SQL-bearing index, trigger, or alias objects"),
            "a main trigger cannot program owner-mode transitions");
    }
}

void test_temp_and_root_programs_fail_closed(TestState& test) {
    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        ensure_checkpoint_owner_schema_or_throw(
            db.db.get(), "temp shadow setup");
        sqlite_exec_or_throw(
            db.db,
            "CREATE TEMP TABLE sync_session_checkpoint_owner_modes("
            "session_id TEXT);",
            "owner mode temp shadow");
        test.check(
            throws_with(
                [&] {
                    attest_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner mode temp shadow refusal");
                },
                "temporary schema object"),
            "TEMP-first name shadowing is rejected even though production SQL is main-qualified");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        ensure_checkpoint_owner_schema_or_throw(
            db.db.get(), "temp trigger setup");
        sqlite_exec_or_throw(
            db.db,
            "CREATE TEMP TRIGGER hostile_temp_owner_trigger "
            "AFTER UPDATE ON main.sync_session_checkpoint_owner_modes "
            "BEGIN SELECT 1; END;",
            "owner mode temp trigger");
        test.check(
            throws_with(
                [&] {
                    attest_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner mode temp trigger refusal");
                },
                "temporary schema object"),
            "a TEMP trigger cannot program a main owner table");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        ensure_checkpoint_owner_schema_or_throw(
            db.db.get(), "root trigger setup");
        sqlite_exec_or_throw(
            db.db,
            "CREATE TRIGGER main.hostile_checkpoint_root_trigger "
            "BEFORE DELETE ON sync_session_checkpoints "
            "BEGIN SELECT 1; END;",
            "checkpoint root trigger");
        test.check(
            throws_with(
                [&] {
                    attest_checkpoint_owner_schema_or_throw(
                        db.db.get(), "checkpoint root trigger refusal");
                },
                "checkpoint root has an unreviewed trigger"),
            "checkpoint-root deletion cannot be redirected by a trigger program");
    }
}

void test_owner_lock_drift_precedes_migration(TestState& test) {
    {
        SyncSqliteDb db = open_memory_database();
        sqlite_exec_or_throw(
            db.db,
            std::string(kRootDdl) +
                "CREATE TABLE main.sync_session_resume_transfer_daemon_owner_locks("
                "session_id TEXT NOT NULL PRIMARY KEY REFERENCES "
                "sync_session_checkpoints(session_id) ON DELETE NO ACTION,"
                "daemon_id TEXT NOT NULL,worker_id TEXT NOT NULL,"
                "owner_lock_id TEXT NOT NULL,owner_lock_epoch INTEGER NOT NULL "
                "CHECK(owner_lock_epoch > 0),acquired_at_epoch INTEGER NOT NULL "
                "CHECK(acquired_at_epoch > 0),expires_at_epoch INTEGER NOT NULL "
                "CHECK(expires_at_epoch > acquired_at_epoch),"
                "released_at_epoch INTEGER NOT NULL CHECK(released_at_epoch = 0 "
                "OR released_at_epoch >= acquired_at_epoch),lock_state TEXT NOT "
                "NULL CHECK(lock_state IN ('held','released')),updated_at_epoch "
                "INTEGER NOT NULL CHECK(updated_at_epoch >= acquired_at_epoch));",
            "owner lock wrong cascade fixture");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner lock cascade refusal");
                },
                "exact reviewed schema SQL does not match"),
            "owner-lock foreign-key cascade drift is rejected");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
                "name='sync_session_checkpoint_owner_modes';",
                "owner lock drift migration side effect count") == 0,
            "hostile owner-lock evidence is rejected before mode-table creation");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            "CREATE TRIGGER main.hostile_owner_lock_trigger "
            "BEFORE UPDATE ON sync_session_resume_transfer_daemon_owner_locks "
            "BEGIN SELECT 1; END;",
            "owner lock trigger fixture");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "owner lock trigger refusal");
                },
                "unexpected SQL-bearing index, trigger, or alias objects"),
            "owner-lock state cannot be rewritten by a trigger program");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
                "name='sync_session_checkpoint_owner_modes';",
                "owner lock trigger migration side effect count") == 0,
            "owner-lock trigger refusal leaves the sticky migration absent");
    }
}

void test_parent_anchor_and_optional_legacy_table(TestState& test) {
    {
        SyncSqliteDb db = open_memory_database();
        sqlite_exec_or_throw(
            db.db,
            "CREATE TABLE main.sync_session_checkpoints("
            "session_id TEXT NOT NULL);" + std::string(kOwnerLockDdl),
            "malformed checkpoint root anchor fixture");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "malformed root anchor refusal");
                },
                "session_id anchor geometry does not match"),
            "an exact-looking owner lock cannot bind a non-key checkpoint root");
    }

    {
        SyncSqliteDb db = open_memory_database();
        sqlite_exec_or_throw(
            db.db, std::string(kRootDdl), "legacy database without owner lock");
        ensure_checkpoint_owner_schema_or_throw(
            db.db.get(), "legacy owner-lock absence bootstrap");
        attest_checkpoint_owner_schema_or_throw(
            db.db.get(), "legacy owner-lock absence attestation");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='table' "
                "AND name='sync_session_checkpoint_owner_modes';",
                "legacy optional lock mode count") == 1,
            "a genuinely pre-owner database can gain independent sticky-mode schema without forged owner evidence");
    }
}

void test_connection_constraint_profile(TestState& test) {
    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            "PRAGMA foreign_keys=OFF;",
            "owner schema disabled foreign-key fixture");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "disabled foreign-key refusal");
                },
                "requires foreign-key enforcement"),
            "owner schema refuses a connection that cannot enforce the reviewed cascade");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
                "name='sync_session_checkpoint_owner_modes';",
                "disabled foreign-key mode-table count") == 0,
            "foreign-key profile refusal leaves no migration side effect");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            "PRAGMA ignore_check_constraints=ON;",
            "owner schema ignored CHECK fixture");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "ignored CHECK refusal");
                },
                "requires CHECK-constraint enforcement"),
            "owner schema refuses a connection that has disabled reviewed CHECK constraints");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
                "name='sync_session_checkpoint_owner_modes';",
                "ignored CHECK mode-table count") == 0,
            "CHECK-profile refusal leaves no migration side effect");
    }
}

void test_nested_migration_savepoint(TestState& test) {
    SyncSqliteDb db = open_memory_database();
    install_root_and_exact_lock(db);
    sqlite_exec_or_throw(
        db.db, "BEGIN IMMEDIATE;", "outer migration transaction begin");
    ensure_checkpoint_owner_schema_or_throw(
        db.db.get(), "nested owner-schema migration");
    test.check(
        sqlite3_get_autocommit(db.db.get()) == 0,
        "owner-schema savepoint publication never commits the caller transaction");
    sqlite_exec_or_throw(
        db.db, "ROLLBACK;", "outer migration transaction rollback");
    test.check(
        scalar_u64(
            db.db.get(),
            "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
            "name='sync_session_checkpoint_owner_modes';",
            "outer rollback mode-table count") == 0,
        "caller rollback removes schema created through the nested migration savepoint");
}

void test_case_folded_aliases_and_atomic_backfill(TestState& test) {
    {
        SyncSqliteDb db = open_memory_database();
        sqlite_exec_or_throw(
            db.db,
            std::string(kRootDdl) +
                "CREATE TABLE main.Sync_Session_Resume_Transfer_Daemon_Owner_Locks("
                "session_id TEXT NOT NULL PRIMARY KEY REFERENCES "
                "sync_session_checkpoints(session_id) ON DELETE CASCADE,"
                "daemon_id TEXT NOT NULL,worker_id TEXT NOT NULL,"
                "owner_lock_id TEXT NOT NULL,owner_lock_epoch INTEGER NOT NULL "
                "CHECK(owner_lock_epoch > 0),acquired_at_epoch INTEGER NOT NULL "
                "CHECK(acquired_at_epoch > 0),expires_at_epoch INTEGER NOT NULL "
                "CHECK(expires_at_epoch > acquired_at_epoch),"
                "released_at_epoch INTEGER NOT NULL CHECK(released_at_epoch = 0 "
                "OR released_at_epoch >= acquired_at_epoch),lock_state TEXT NOT "
                "NULL CHECK(lock_state IN ('held','released')),updated_at_epoch "
                "INTEGER NOT NULL CHECK(updated_at_epoch >= acquired_at_epoch));",
            "mixed-case owner lock alias fixture");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "mixed-case owner lock alias refusal");
                },
                "not the exact main table object"),
            "SQLite case-insensitive owner-lock aliases cannot bypass exact catalog attestation");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
                "name='sync_session_checkpoint_owner_modes';",
                "mixed-case owner lock migration side effect count") == 0,
            "mixed-case owner-lock refusal leaves no sticky-mode migration side effect");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        ensure_checkpoint_owner_schema_or_throw(
            db.db.get(), "mixed-case TEMP shadow setup");
        sqlite_exec_or_throw(
            db.db,
            "CREATE TEMP TABLE Sync_Session_Checkpoint_Owner_Modes("
            "session_id TEXT);",
            "mixed-case owner mode TEMP shadow");
        test.check(
            throws_with(
                [&] {
                    attest_checkpoint_owner_schema_or_throw(
                        db.db.get(), "mixed-case TEMP shadow refusal");
                },
                "temporary schema object"),
            "SQLite case-insensitive TEMP aliases are rejected without SQL lower or overridable collations");
    }

    {
        SyncSqliteDb db = open_memory_database();
        install_root_and_exact_lock(db);
        sqlite_exec_or_throw(
            db.db,
            "INSERT INTO main.sync_session_checkpoints(session_id) "
            "VALUES('session-atomic');"
            "PRAGMA ignore_check_constraints=ON;"
            "INSERT INTO main.sync_session_resume_transfer_daemon_owner_locks("
            "session_id,daemon_id,worker_id,owner_lock_id,owner_lock_epoch,"
            "acquired_at_epoch,expires_at_epoch,released_at_epoch,lock_state,"
            "updated_at_epoch) VALUES('session-atomic','daemon-a','worker-a',"
            "'forged-owner-id',0,10,20,0,'held',10);"
            "PRAGMA ignore_check_constraints=OFF;",
            "malformed legacy owner row fixture");
        test.check(
            throws_with(
                [&] {
                    ensure_checkpoint_owner_schema_or_throw(
                        db.db.get(), "atomic legacy backfill refusal");
                },
                "backfill legacy sticky owner modes"),
            "malformed legacy rows fail the constrained sticky-mode backfill");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
                "name='sync_session_checkpoint_owner_modes';",
                "atomic backfill mode-table count") == 0,
            "failed legacy backfill rolls mode-table creation back to the migration savepoint");
        test.check(
            scalar_u64(
                db.db.get(),
                "SELECT COUNT(*) FROM "
                "main.sync_session_resume_transfer_daemon_owner_locks "
                "WHERE session_id='session-atomic';",
                "atomic backfill legacy row count") == 1,
            "migration rollback preserves the preexisting hostile row for explicit repair");
        test.check(
            sqlite3_get_autocommit(db.db.get()) == 1,
            "failed owner-schema migration releases its nested savepoint cleanly");
    }
}

}  // namespace

int main() {
    TestState test;
    try {
        test.check(
            throws_with(
                [] {
                    ensure_checkpoint_owner_schema_or_throw(
                        nullptr, "null owner schema ensure");
                },
                "database handle is null"),
            "schema ensure rejects a null SQLite handle");
        test.check(
            throws_with(
                [] {
                    attest_checkpoint_owner_schema_or_throw(
                        nullptr, "null owner schema attestation");
                },
                "database handle is null"),
            "schema attestation rejects a null SQLite handle");

        test_clean_bootstrap_and_repeat(test);
        test_semantically_equivalent_formatting(test);
        test_mode_lookalikes_fail_closed(test);
        test_temp_and_root_programs_fail_closed(test);
        test_owner_lock_drift_precedes_migration(test);
        test_parent_anchor_and_optional_legacy_table(test);
        test_connection_constraint_profile(test);
        test_nested_migration_savepoint(test);
        test_case_folded_aliases_and_atomic_backfill(test);
    } catch (const std::exception& error) {
        ++test.failed;
        std::cerr << "UNCAUGHT: " << error.what() << '\n';
    }

    std::cout << "sync checkpoint owner schema checks: " << test.passed << '/'
              << (test.passed + test.failed) << " passed\n";
    return test.failed == 0 ? 0 : 1;
}
