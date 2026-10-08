#include "sync_sqlite_sidecar_claimed_path_snapshot.hpp"

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>

#include <sqlite3.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
using anonsync::SyncSqliteDb;
using anonsync::SyncSqliteSidecarClaimedPathLimits;
using anonsync::SyncSqliteSidecarClaimedPathSnapshot;
using anonsync::SyncSqliteSidecarClaimedPathSnapshotReader;
using anonsync::SyncSqliteSidecarLockWaitBudget;
using anonsync::SyncSqliteSidecarLockWaitBudgetException;
using anonsync::SyncSqliteSidecarLockWaitLimits;
using anonsync::SyncSqliteSidecarSnapshotExecutionBudget;
using anonsync::SyncSqliteSidecarSnapshotExecutionLimits;
using anonsync::SyncSqliteTransaction;
using anonsync::SyncSqliteTransactionAuthority;
using anonsync::SyncSqliteTransactionMode;
using anonsync::persistence::SqliteVerificationBudgetException;
using anonsync::persistence::SqliteVerificationBudgetFailure;

static_assert(!std::is_copy_constructible_v<
              SyncSqliteSidecarClaimedPathSnapshotReader>);
static_assert(!std::is_copy_assignable_v<
              SyncSqliteSidecarClaimedPathSnapshotReader>);
static_assert(!std::is_move_constructible_v<
              SyncSqliteSidecarClaimedPathSnapshotReader>);
static_assert(!std::is_move_assignable_v<
              SyncSqliteSidecarClaimedPathSnapshotReader>);
static_assert(!std::is_copy_constructible_v<
              SyncSqliteSidecarSnapshotExecutionBudget>);
static_assert(!std::is_copy_assignable_v<
              SyncSqliteSidecarSnapshotExecutionBudget>);
static_assert(!std::is_move_constructible_v<
              SyncSqliteSidecarSnapshotExecutionBudget>);
static_assert(!std::is_move_assignable_v<
              SyncSqliteSidecarSnapshotExecutionBudget>);
static_assert(!std::is_copy_constructible_v<
              SyncSqliteSidecarLockWaitBudget>);
static_assert(!std::is_copy_assignable_v<
              SyncSqliteSidecarLockWaitBudget>);
static_assert(!std::is_move_constructible_v<
              SyncSqliteSidecarLockWaitBudget>);
static_assert(!std::is_move_assignable_v<
              SyncSqliteSidecarLockWaitBudget>);

std::uint64_t checks = 0;

[[noreturn]] void fail(const std::string& message) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(1);
}

void require(bool condition, const std::string& message) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Fn>
void require_error(Fn&& fn,
                   std::string_view expected_fragment,
                   const std::string& message) {
    try {
        std::forward<Fn>(fn)();
    } catch (const std::exception& error) {
        require(std::string_view(error.what()).find(expected_fragment) !=
                    std::string_view::npos,
                message + " returned unexpected error: " + error.what());
        return;
    }
    fail(message + " did not reject");
}

void cleanup_sqlite_family(const fs::path& path) {
    for (const std::string_view suffix : {"", "-wal", "-shm", "-journal"}) {
        std::error_code ignored;
        fs::remove(fs::path(path.string() + std::string(suffix)), ignored);
    }
}

SyncSqliteDb open_database(const fs::path& path, int flags) {
    SyncSqliteDb owner;
    const int rc = sqlite3_open_v2(path.c_str(), owner.db.out(), flags, nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error(anonsync::sqlite_error_message(
            owner.db, "claimed-path snapshot test could not open database"));
    }
    return owner;
}

SyncSqliteDb open_memory_database() {
    return open_database(
        ":memory:",
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX |
            SQLITE_OPEN_PRIVATECACHE);
}

void exec(SyncSqliteDb& db, const std::string& sql) {
    anonsync::sqlite_exec_or_throw(
        db.db, sql, "claimed-path snapshot test SQL");
}

SyncSqliteSidecarClaimedPathLimits generous_limits() {
    return {
        .max_paths = 16,
        .max_total_path_bytes = 1024,
    };
}

SyncSqliteSidecarSnapshotExecutionLimits generous_execution_limits() {
    return {
        .maximum_progress_callbacks =
            anonsync::persistence::kMaximumSqliteVerificationProgressCallbacks,
        .progress_opcode_interval =
            anonsync::persistence::kMaximumSqliteVerificationProgressOpcodeInterval,
        .maximum_elapsed_milliseconds =
            anonsync::persistence::kMaximumSqliteVerificationElapsedMilliseconds,
    };
}

SyncSqliteSidecarLockWaitLimits lock_wait_limits(std::uint64_t milliseconds) {
    return {.maximum_lock_wait_milliseconds = milliseconds};
}

SyncSqliteSidecarClaimedPathSnapshot load(
    SyncSqliteSidecarClaimedPathSnapshotReader& reader,
    const SyncSqliteTransactionAuthority& authority,
    SyncSqliteSidecarSnapshotExecutionBudget& execution_budget,
    SyncSqliteSidecarClaimedPathLimits limits = generous_limits(),
    std::string session_id = "session-a",
    std::string worker_id = "worker-a",
    std::string lease_id = "lease-a") {
    return reader.load_or_throw(
        authority,
        execution_budget,
        session_id,
        worker_id,
        lease_id,
        limits,
        "claimed-path snapshot test");
}

void create_workorder_table(
    SyncSqliteDb& db,
    std::string_view path_declaration = "path") {
    exec(db,
         "CREATE TABLE main.sync_session_resume_transfer_workorders("
         "session_id, worker_id, worker_lease_id, work_state, " +
             std::string(path_declaration) + ");");
}

}  // namespace

int main() {
    const fs::path database_path =
        fs::temp_directory_path() /
        ("anonsync-sidecar-claimed-path-" +
         std::to_string(static_cast<unsigned long long>(::getpid())) +
         ".sqlite");
    const fs::path lock_database_path =
        fs::path(database_path.string() + "-lock-budget.sqlite");
    cleanup_sqlite_family(database_path);
    cleanup_sqlite_family(lock_database_path);

    try {
        {
            SyncSqliteDb writer = open_database(
                database_path,
                SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                    SQLITE_OPEN_FULLMUTEX);
            exec(writer,
                 "PRAGMA journal_mode=WAL;"
                 "PRAGMA wal_autocheckpoint=0;"
                 "CREATE TABLE main.sync_session_resume_transfer_workorders("
                 "session_id, worker_id, worker_lease_id, work_state, path);"
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','alpha'),"
                 "('session-a','worker-a','lease-a','claimed','beta'),"
                 "('session-a','worker-a','lease-a','claimed','alpha'),"
                 "('session-a','worker-b','lease-a','claimed','ignored-worker'),"
                 "('session-a','worker-a','lease-b','claimed','ignored-lease'),"
                 "('session-a','worker-a','lease-a','completed','ignored-state'),"
                 "('session-b','worker-a','lease-a','claimed','ignored-session');");

            SyncSqliteDb reader_db = open_database(
                database_path,
                SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX);
            exec(reader_db,
                 "CREATE TEMP TABLE sync_session_resume_transfer_workorders("
                 "session_id, worker_id, worker_lease_id, work_state, path);"
                 "INSERT INTO temp.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','temp-shadow');");

            SyncSqliteSidecarClaimedPathSnapshotReader reader(
                reader_db.db, "claimed-path snapshot test owner");
            require(reader.owner_generation() == reader_db.db.generation(),
                    "reader pins the exact database-owner generation");

            SyncSqliteTransaction first_transaction(
                reader_db.db,
                "claimed-path snapshot test first transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionBudget first_execution_budget(
                reader_db.db,
                generous_execution_limits(),
                "claimed-path snapshot test first execution budget");
            const SyncSqliteTransactionAuthority stale_authority =
                first_transaction.authority();
            const SyncSqliteSidecarClaimedPathSnapshot first =
                load(reader, stale_authority, first_execution_budget);
            require(first.path_count == 2 && first.paths.size() == 2 &&
                        first.paths[0].value == "alpha" &&
                        first.paths[1].value == "beta",
                    "main-schema query returns the exact distinct claimed frontier");
            require(first.total_path_bytes == 9,
                    "claimed-path byte accounting is exact");
            require(first.database_owner_generation == reader_db.db.generation(),
                    "snapshot publishes its exact database-owner generation");
            require(first_transaction.authorizes_snapshot(reader_db.db),
                    "first bounded SELECT establishes the typed main snapshot");
            require(first.paths[0].value != "temp-shadow",
                    "explicit main binding ignores a malicious TEMP shadow");

            exec(writer,
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','gamma');");
            const SyncSqliteSidecarClaimedPathSnapshot stable =
                load(reader, first_transaction.authority(), first_execution_budget);
            require(stable.path_count == 2 &&
                        stable.paths.back().value == "beta",
                    "reused reader retains the original WAL snapshot after writer commit");
            first_execution_budget.detach();
            first_transaction.commit();
            require(!stale_authority.authorizes(reader_db.db),
                    "committed transaction revokes its copied authority");
            require_error([&] { (void)load(reader, stale_authority, first_execution_budget); },
                          "exact live SQLite transaction authority",
                          "stale transaction authority is rejected");

            SyncSqliteTransaction second_transaction(
                reader_db.db,
                "claimed-path snapshot test second transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionBudget second_execution_budget(
                reader_db.db,
                generous_execution_limits(),
                "claimed-path snapshot test second execution budget");
            const SyncSqliteSidecarClaimedPathSnapshot refreshed =
                load(reader, second_transaction.authority(), second_execution_budget);
            require(refreshed.path_count == 3 &&
                        refreshed.paths.back().value == "gamma",
                    "new typed transaction observes the later committed generation");

            SyncSqliteSidecarClaimedPathLimits limits = generous_limits();
            limits.max_paths = 2;
            require_error(
                [&] { (void)load(reader, second_transaction.authority(), second_execution_budget, limits); },
                "row count exceeds",
                "max_paths plus one SQL sentinel detects a truncated frontier");
            require(load(reader, second_transaction.authority(), second_execution_budget).path_count == 3,
                    "prepared statement is reusable after row-limit rejection");

            limits = generous_limits();
            limits.max_total_path_bytes = 13;
            require_error(
                [&] { (void)load(reader, second_transaction.authority(), second_execution_budget, limits); },
                "path bytes exceed",
                "aggregate path bytes are rejected before vector publication");
            limits.max_total_path_bytes = 14;
            require(load(reader, second_transaction.authority(), second_execution_budget, limits)
                            .total_path_bytes == 14,
                    "exact aggregate path-byte ceiling is admitted");
            second_execution_budget.detach();
            require_error(
                [&] {
                    (void)load(reader,
                               second_transaction.authority(),
                               second_execution_budget);
                },
                "execution budget is detached",
                "detached execution authority cannot authorize callback-free work");
            second_transaction.commit();

            SyncSqliteDb wrong_db = open_memory_database();
            create_workorder_table(wrong_db);
            SyncSqliteTransaction wrong_transaction(
                wrong_db.db,
                "claimed-path snapshot test wrong transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionBudget wrong_execution_budget(
                wrong_db.db,
                generous_execution_limits(),
                "claimed-path snapshot test wrong execution budget");
            require_error(
                [&] { (void)load(reader, wrong_transaction.authority(), wrong_execution_budget); },
                "exact live SQLite transaction authority",
                "authority from a different database generation is rejected");
            require_error(
                [&] { (void)load(reader, SyncSqliteTransactionAuthority{}, wrong_execution_budget); },
                "exact live SQLite transaction authority",
                "missing transaction authority is rejected");
            SyncSqliteTransaction validation_transaction(
                reader_db.db,
                "claimed-path snapshot test validation transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionBudget validation_execution_budget(
                reader_db.db,
                generous_execution_limits(),
                "claimed-path snapshot test validation execution budget");
            require_error(
                [&] {
                    (void)load(reader,
                               validation_transaction.authority(),
                               wrong_execution_budget);
                },
                "exact sidecar snapshot execution-budget generation",
                "execution budget from a different database generation is rejected");
            wrong_execution_budget.detach();
            wrong_transaction.rollback();
            limits = generous_limits();
            limits.max_paths = 0;
            require_error(
                [&] { (void)load(reader, validation_transaction.authority(), validation_execution_budget, limits); },
                "limits must be positive",
                "zero row limit is rejected before query execution");
            limits = generous_limits();
            limits.max_total_path_bytes = 0;
            require_error(
                [&] { (void)load(reader, validation_transaction.authority(), validation_execution_budget, limits); },
                "limits must be positive",
                "zero byte limit is rejected before query execution");
            limits = generous_limits();
            limits.max_paths = static_cast<std::uint64_t>(
                std::numeric_limits<sqlite3_int64>::max());
            require_error(
                [&] { (void)load(reader, validation_transaction.authority(), validation_execution_budget, limits); },
                "cannot form a SQLite sentinel",
                "unrepresentable SQL sentinel is rejected");
            require_error(
                [&] { (void)load(reader, validation_transaction.authority(),
                                      validation_execution_budget, generous_limits(), "bad/session"); },
                "session id is invalid",
                "noncanonical session id is rejected");
            require_error(
                [&] { (void)load(reader, validation_transaction.authority(),
                                      validation_execution_budget, generous_limits(), "session-a", ""); },
                "worker id is required",
                "empty worker id is rejected");
            require_error(
                [&] { (void)load(reader, validation_transaction.authority(),
                                      validation_execution_budget, generous_limits(), "session-a",
                                      std::string(257, 'w')); },
                "worker id exceeds",
                "oversized worker id is rejected");
            require_error(
                [&] { (void)load(reader, validation_transaction.authority(),
                                      validation_execution_budget, generous_limits(), "session-a", "worker-a", ""); },
                "worker lease id is required",
                "empty lease id is rejected");
            validation_execution_budget.detach();
            validation_transaction.rollback();
        }

        {
            SyncSqliteDb collated = open_memory_database();
            exec(collated,
                 "CREATE TABLE main.sync_session_resume_transfer_workorders("
                 "session_id TEXT COLLATE NOCASE, "
                 "worker_id TEXT COLLATE NOCASE, "
                 "worker_lease_id TEXT COLLATE NOCASE, "
                 "work_state TEXT COLLATE NOCASE, "
                 "path TEXT COLLATE NOCASE);"
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','Case'),"
                 "('session-a','worker-a','lease-a','claimed','case'),"
                 "('SESSION-A','worker-a','lease-a','claimed','wrong-session-case'),"
                 "('session-a','WORKER-A','lease-a','claimed','wrong-worker-case'),"
                 "('session-a','worker-a','LEASE-A','claimed','wrong-lease-case'),"
                 "('session-a','worker-a','lease-a','CLAIMED','wrong-state-case');");
            SyncSqliteSidecarClaimedPathSnapshotReader reader(
                collated.db, "claimed-path collation owner");
            SyncSqliteTransaction transaction(
                collated.db,
                "claimed-path collation transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionBudget execution_budget(
                collated.db,
                generous_execution_limits(),
                "claimed-path collation execution budget");
            const auto snapshot =
                load(reader, transaction.authority(), execution_budget);
            require(snapshot.path_count == 2 &&
                        snapshot.paths[0].value == "Case" &&
                        snapshot.paths[1].value == "case",
                    "explicit binary collation preserves every exact lookup and path identity");
            execution_budget.detach();
            transaction.commit();
        }

        {
            SyncSqliteDb hostile = open_memory_database();
            create_workorder_table(hostile);
            exec(hostile,
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed',CAST(X'00' AS BLOB));");
            SyncSqliteSidecarClaimedPathSnapshotReader reader(
                hostile.db, "claimed-path hostile owner");
            SyncSqliteTransaction transaction(
                hostile.db,
                "claimed-path hostile transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionBudget execution_budget(
                hostile.db,
                generous_execution_limits(),
                "claimed-path hostile execution budget");
            require_error(
                [&] { (void)load(reader, transaction.authority(), execution_budget); },
                "wrong_storage_class",
                "BLOB path is rejected by exact SQLite extraction");
            exec(hostile,
                 "DELETE FROM main.sync_session_resume_transfer_workorders;"
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','../escape');");
            require_error(
                [&] { (void)load(reader, transaction.authority(), execution_budget); },
                "stored claimed path is invalid",
                "noncanonical persisted path is rejected");
            exec(hostile,
                 "DELETE FROM main.sync_session_resume_transfer_workorders;"
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','recovered');");
            require(load(reader, transaction.authority(), execution_budget).path_count == 1,
                    "reader remains reusable after hostile storage rejection");
            execution_budget.detach();
            transaction.commit();
        }

        {
            SyncSqliteDb expensive = open_memory_database();
            create_workorder_table(expensive);
            exec(expensive,
                 "WITH RECURSIVE n(value) AS ("
                 "VALUES(0) UNION ALL SELECT value+1 FROM n WHERE value<799) "
                 "INSERT INTO main.sync_session_resume_transfer_workorders "
                 "SELECT 'session-a','worker-a','lease-a','claimed',"
                 "printf('duplicate-%03d', value%40) FROM n;");
            SyncSqliteSidecarClaimedPathSnapshotReader reader(
                expensive.db, "claimed-path progress owner");
            SyncSqliteTransaction transaction(
                expensive.db,
                "claimed-path progress transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionLimits tight_limits =
                generous_execution_limits();
            tight_limits.maximum_progress_callbacks = 1;
            tight_limits.progress_opcode_interval = 1;
            SyncSqliteSidecarSnapshotExecutionBudget tight_budget(
                expensive.db, tight_limits, "claimed-path progress budget");
            try {
                (void)load(reader, transaction.authority(), tight_budget, {
                    .max_paths = 64,
                    .max_total_path_bytes = 4096,
                });
                fail("SQLite VM-step budget did not interrupt expensive frontier");
            } catch (const SqliteVerificationBudgetException& error) {
                require(
                    error.failure() ==
                        SqliteVerificationBudgetFailure::progress_callback_limit,
                    "SQLite interruption recovers the typed VM-step reason");
                require(error.observed() == 2 && error.limit() == 1,
                        "VM-step failure publishes exact callback accounting");
            }
            tight_budget.detach();

            SyncSqliteSidecarSnapshotExecutionBudget reuse_budget(
                expensive.db,
                generous_execution_limits(),
                "claimed-path progress reuse budget");
            const auto recovered = load(
                reader,
                transaction.authority(),
                reuse_budget,
                {.max_paths = 64, .max_total_path_bytes = 4096});
            require(recovered.path_count == 40,
                    "statement and transaction are reusable after typed interruption");
            reuse_budget.detach();
            transaction.commit();
        }

        {
            SyncSqliteDb elapsed = open_memory_database();
            create_workorder_table(elapsed);
            exec(elapsed,
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','elapsed');");
            SyncSqliteSidecarClaimedPathSnapshotReader reader(
                elapsed.db, "claimed-path elapsed owner");
            SyncSqliteTransaction transaction(
                elapsed.db,
                "claimed-path elapsed transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionLimits elapsed_limits =
                generous_execution_limits();
            elapsed_limits.maximum_elapsed_milliseconds = 1;
            SyncSqliteSidecarSnapshotExecutionBudget elapsed_budget(
                elapsed.db, elapsed_limits, "claimed-path elapsed budget");
            std::this_thread::sleep_for(std::chrono::milliseconds(4));
            try {
                (void)load(reader, transaction.authority(), elapsed_budget);
                fail("elapsed execution budget did not expire");
            } catch (const SqliteVerificationBudgetException& error) {
                require(
                    error.failure() ==
                        SqliteVerificationBudgetFailure::elapsed_time_limit,
                    "ordinary C++ checkpoint recovers the typed elapsed reason");
                require(error.observed() > error.limit() && error.limit() == 1,
                        "elapsed failure publishes monotonic observed and limit values");
            }
            elapsed_budget.detach();

            SyncSqliteSidecarSnapshotExecutionBudget reuse_budget(
                elapsed.db,
                generous_execution_limits(),
                "claimed-path elapsed reuse budget");
            require(load(reader, transaction.authority(), reuse_budget).path_count == 1,
                    "fresh execution authority succeeds after elapsed rejection");
            reuse_budget.detach();
            transaction.commit();
        }

        {
            SyncSqliteDb blocker = open_database(
                lock_database_path,
                SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                    SQLITE_OPEN_FULLMUTEX);
            exec(blocker,
                 "PRAGMA journal_mode=DELETE;"
                 "CREATE TABLE main.sync_session_resume_transfer_workorders("
                 "session_id, worker_id, worker_lease_id, work_state, path);"
                 "INSERT INTO main.sync_session_resume_transfer_workorders VALUES"
                 "('session-a','worker-a','lease-a','claimed','locked');");
            SyncSqliteDb contender = open_database(
                lock_database_path,
                SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX);
            SyncSqliteSidecarClaimedPathSnapshotReader reader(
                contender.db, "claimed-path lock-wait owner");

            require_error(
                [&] {
                    SyncSqliteSidecarLockWaitBudget widened(
                        contender.db,
                        lock_wait_limits(
                            anonsync::persistence::
                                kMaximumSqliteBusyHandlerWaitMilliseconds +
                            1U),
                        "claimed-path widened lock-wait budget");
                },
                "reviewed ceiling",
                "sidecar lock-wait authority cannot widen the generic ceiling");

            SyncSqliteSidecarLockWaitBudget identity_budget(
                contender.db,
                lock_wait_limits(1U),
                "claimed-path identity lock-wait budget");
            require(identity_budget.owner_generation() ==
                        contender.db.generation(),
                    "lock-wait owner freezes the exact database generation");
            require_error(
                [&] {
                    identity_budget.require_authorizes_or_throw(
                        contender.db.get(),
                        contender.db.generation() + 1U,
                        "claimed-path foreign lock-wait generation");
                },
                "exact sidecar lock-wait generation",
                "lock-wait owner rejects a foreign database generation");
            identity_budget.detach();
            require_error(
                [&] {
                    identity_budget.require_authorizes_or_throw(
                        contender.db.get(),
                        contender.db.generation(),
                        "claimed-path detached lock-wait generation");
                },
                "detached",
                "detachment is one-way lock-wait authority revocation");

            exec(blocker, "BEGIN EXCLUSIVE;");
            SyncSqliteSidecarLockWaitBudget exhausted_budget(
                contender.db,
                lock_wait_limits(0U),
                "claimed-path zero lock-wait budget");
            bool sqlite_busy_observed = false;
            try {
                SyncSqliteTransaction transaction(
                    contender.db,
                    "claimed-path locked transaction",
                    SyncSqliteTransactionMode::Deferred);
                SyncSqliteSidecarSnapshotExecutionBudget execution_budget(
                    contender.db,
                    generous_execution_limits(),
                    "claimed-path locked execution budget");
                try {
                    (void)load(
                        reader, transaction.authority(), execution_budget);
                    fail("zero lock-wait budget admitted a blocked SELECT");
                } catch (...) {
                    execution_budget.throw_if_exhausted();
                    throw;
                }
            } catch (const std::exception&) {
                sqlite_busy_observed = true;
            }
            require(sqlite_busy_observed,
                    "blocked transaction reports a native SQLite failure before typed translation");
            try {
                exhausted_budget.throw_if_exhausted();
                fail("exhausted lock-wait owner did not publish typed evidence");
            } catch (const SyncSqliteSidecarLockWaitBudgetException& error) {
                require(error.limit() == 0U && error.invocations() >= 1U &&
                            std::string_view(error.what()).find(
                                "sqlite_sidecar_lock_wait_budget[lock_wait_limit]") !=
                                std::string_view::npos,
                        "zero lock wait converts SQLITE_BUSY into stable typed evidence");
                require(error.authorized_sleep_milliseconds() == 0U &&
                            error.observed_sleep_milliseconds() == 0U,
                        "zero lock wait authorizes and observes no sleep");
            }
            const auto exhausted_snapshot = exhausted_budget.snapshot();
            require(exhausted_snapshot.timeout_exhausted &&
                        exhausted_snapshot.contention_observed &&
                        exhausted_snapshot.authorized_sleep_milliseconds == 0U,
                    "sticky lock-wait evidence survives transaction cleanup");
            require(contender.db.active_borrows() == 2U,
                    "transaction and execution cleanup leave only the reader and older lock-wait generations pinned");
            exhausted_budget.detach();
            exec(blocker, "ROLLBACK;");

            SyncSqliteSidecarLockWaitBudget reuse_lock_budget(
                contender.db,
                lock_wait_limits(10U),
                "claimed-path lock-wait reuse budget");
            SyncSqliteTransaction reuse_transaction(
                contender.db,
                "claimed-path lock-wait reuse transaction",
                SyncSqliteTransactionMode::Deferred);
            SyncSqliteSidecarSnapshotExecutionBudget reuse_execution_budget(
                contender.db,
                generous_execution_limits(),
                "claimed-path lock-wait reuse execution budget");
            const auto reused = load(
                reader,
                reuse_transaction.authority(),
                reuse_execution_budget);
            reuse_execution_budget.detach();
            reuse_transaction.commit();
            require(reused.path_count == 1 &&
                        reused.paths.front().value == "locked" &&
                        !reuse_lock_budget.snapshot().contention_observed,
                    "fresh lock, transaction, and execution owners succeed after exhaustion cleanup");
            reuse_lock_budget.detach();
        }

        cleanup_sqlite_family(lock_database_path);
        cleanup_sqlite_family(database_path);
        std::cout << "sync sqlite sidecar claimed path snapshot test passed="
                  << checks << " failed=0\n";
        return 0;
    } catch (const std::exception& error) {
        cleanup_sqlite_family(lock_database_path);
        cleanup_sqlite_family(database_path);
        fail(std::string("unexpected exception: ") + error.what());
    }
}
