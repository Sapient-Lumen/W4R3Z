#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif
#include "sync_sqlite_busy_timeout_mutation_guard.hpp"
#include "sync_sqlite_connection_authority.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"
#include "sync_sqlite_support.hpp"

#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <type_traits>
#include <utility>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/wait.h>
#include <unistd.h>
#endif

#include <sqlite3.h>

namespace {

template <typename T>
concept StatementViewExposesOut = requires(T& value) { value.stmt.out(); };

template <typename T>
concept StatementViewExposesReset = requires(T& value) { value.stmt.reset(); };

static_assert(!StatementViewExposesOut<anonsync::SyncSqliteStmt>);
static_assert(!StatementViewExposesReset<anonsync::SyncSqliteStmt>);
static_assert(!std::is_move_constructible_v<anonsync::SyncSqliteStmt::HandleView>);

using namespace anonsync;
using namespace std::chrono_literals;
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_or_throw;
#endif

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
            return;
        }
        ++failed;
        std::cerr << "FAIL: " << label << "\n";
    }

    template <typename Function>
    void require_throws(Function&& function, const std::string& label) {
        try {
            function();
            require(false, label);
        } catch (const std::exception&) {
            require(true, label);
        } catch (...) {
            require(false, label + " threw a non-standard exception");
        }
    }
};

SyncSqliteDb open_memory_database_or_throw(const std::string& label) {
    SyncSqliteDb owner;
    const int rc = sqlite3_open_v2(
        ":memory:",
        owner.db.out(),
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    if (rc != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(
            owner.db, label + " could not open in-memory database"));
    }
    return owner;
}

int allow_policy(void*,
                 int,
                 const char*,
                 const char*,
                 const char*,
                 const char*) noexcept {
    return SQLITE_OK;
}

#if defined(__unix__) || defined(__APPLE__)

inline constexpr int kHostileTerminateExitCode = 87;
inline constexpr int kHostileAtExitCode = 88;
inline constexpr int kUnexpectedReturnExitCode = 89;
inline constexpr int kUnexpectedExceptionExitCode = 90;

[[noreturn]] void hostile_terminate_handler() noexcept {
    std::_Exit(kHostileTerminateExitCode);
}

void hostile_atexit_handler() noexcept {
    std::_Exit(kHostileAtExitCode);
}

template <typename Function>
void require_child_exit(TestState& test,
                        int expected_exit_code,
                        Function&& function,
                        const std::string& label) {
    auto child = spawn_inherited_test_process_or_throw(
        [&]() -> int {
            std::set_terminate(hostile_terminate_handler);
            if (std::atexit(hostile_atexit_handler) != 0) {
                return kUnexpectedExceptionExitCode;
            }
            try {
                function();
                return expected_exit_code == 0 ? 0
                                               : kUnexpectedReturnExitCode;
            } catch (...) {
                return kUnexpectedExceptionExitCode;
            }
        },
        label);

    const int status = child.wait_for_exit(5s, label);
    test.require(WIFEXITED(status) &&
                     WEXITSTATUS(status) == expected_exit_code,
                 label + " exited with the required code");
}

template <typename Function>
void require_child_fail_stop(TestState& test,
                             Function&& function,
                             const std::string& label) {
    require_child_exit(test,
                       kSyncProcessCapabilityViolationExitCode,
                       std::forward<Function>(function),
                       label);
}

template <typename Function>
void require_child_success(TestState& test,
                           Function&& function,
                           const std::string& label) {
    require_child_exit(
        test, 0, std::forward<Function>(function), label);
}

void test_busy_timeout_mutation_guard_execution_affinity(TestState& test) {
    require_child_fail_stop(
        test,
        [] {
            sqlite3* raw_database = nullptr;
            const int result = sqlite3_open_v2(
                ":memory:",
                &raw_database,
                SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                    SQLITE_OPEN_NOMUTEX,
                nullptr);
            if (result != SQLITE_OK || raw_database == nullptr) {
                if (raw_database != nullptr) sqlite3_close(raw_database);
                throw std::runtime_error(
                    "foreign-thread NOMUTEX fixture open failed");
            }
            std::unique_ptr<sqlite3, decltype(&sqlite3_close)> database(
                raw_database, sqlite3_close);
            auto* guard = new SyncSqliteBusyTimeoutMutationGuard(
                database.get(),
                "foreign-thread NOMUTEX busy-timeout mutation");
            std::thread worker([guard] { delete guard; });
            worker.join();
        },
        "foreign-thread NOMUTEX busy-timeout guard destruction fails stopped");

    sqlite3* raw_database = nullptr;
    const int result = sqlite3_open_v2(
        ":memory:",
        &raw_database,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_NOMUTEX,
        nullptr);
    if (result != SQLITE_OK || raw_database == nullptr) {
        if (raw_database != nullptr) sqlite3_close(raw_database);
        throw std::runtime_error(
            "inherited NOMUTEX fixture open failed");
    }
    std::unique_ptr<sqlite3, decltype(&sqlite3_close)> database(
        raw_database, sqlite3_close);
    auto guard = std::make_unique<SyncSqliteBusyTimeoutMutationGuard>(
        database.get(), "inherited NOMUTEX busy-timeout mutation");
    require_child_fail_stop(
        test,
        [&] { guard.reset(); },
        "inherited NOMUTEX busy-timeout guard destruction fails stopped");
    guard.reset();
    test.require(true,
                 "parent destroys its NOMUTEX busy-timeout guard normally");

    require_child_fail_stop(
        test,
        [] {
            SyncSqliteDb child_database =
                open_memory_database_or_throw("released mutex guard fixture");
            auto* released_guard = new SyncSqliteDatabaseMutexGuard(
                child_database.db, "released mutex guard affinity");
            sqlite3_mutex* const retained_mutex = released_guard->release();
            if (retained_mutex == nullptr) {
                throw std::runtime_error(
                    "released mutex guard returned a null mutex");
            }
            std::thread worker([released_guard] { delete released_guard; });
            worker.join();
            sqlite3_mutex_leave(retained_mutex);
        },
        "released database-mutex guard destruction remains thread affine");
}

void test_process_bound_handle_slots(TestState& test) {
    SyncSqliteDb database = open_memory_database_or_throw("owner fixture");
    sqlite_exec_or_throw(database.db,
                         "CREATE TABLE records(value INTEGER);"
                         "INSERT INTO records(value) VALUES(42);",
                         "owner fixture schema");
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        database.db, "SELECT value FROM records;", "owner fixture query");

    test.require_throws(
        [&] { (void)database.db.out(); },
        "nonempty connection output acquisition is rejected");

    SyncSqliteDb reserved_output_owner;
    {
        auto pending_output = reserved_output_owner.db.out();
        test.require_throws(
            [&] { (void)reserved_output_owner.db.out(); },
            "a second connection output guard is rejected while one is pending");
        require_child_fail_stop(
            test,
            [&] { reserved_output_owner.db.reset(); },
            "child cannot manipulate a parent-reserved output slot");
        (void)pending_output;
    }
    test.require(reserved_output_owner.db.empty(),
                 "a null output result restores the slot to empty state");
    require_child_fail_stop(
        test,
        [&] { (void)reserved_output_owner.db.empty(); },
        "child cannot inspect inherited materialized owner storage");
    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteDb moved(std::move(reserved_output_owner));
            (void)moved;
        },
        "child cannot move inherited materialized owner storage");

    auto* heap_materialized_empty = new SyncSqliteDb;
    {
        auto null_output = heap_materialized_empty->db.out();
        (void)null_output;
    }
    require_child_fail_stop(
        test,
        [&] { delete heap_materialized_empty; },
        "child destructor cannot release an inherited empty shared-state owner");
    delete heap_materialized_empty;

    sqlite3* const inherited_database = database.db.get();
    sqlite3_stmt* const inherited_statement = statement.stmt.get();
    test.require(inherited_database != nullptr && inherited_statement != nullptr,
                 "parent owns live SQLite handles before fork");

    require_child_fail_stop(
        test,
        [&] { (void)database.db.get(); },
        "child cannot read an inherited connection owner");
    require_child_fail_stop(
        test,
        [&] { database.db.reset(); },
        "child cannot close an inherited connection owner");
    require_child_fail_stop(
        test,
        [&] { (void)database.db.out(); },
        "child cannot overwrite an inherited connection owner");
    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteDb moved(std::move(database));
            (void)moved;
        },
        "child cannot move an inherited connection owner");

    require_child_fail_stop(
        test,
        [&] { (void)statement.stmt.get(); },
        "child cannot read an inherited statement owner");
    require_child_fail_stop(
        test,
        [&] { statement.reset(); },
        "child cannot finalize an inherited statement owner");
    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteStmt moved(std::move(statement));
            (void)moved;
        },
        "child cannot move an inherited statement owner");

    auto* heap_database =
        new SyncSqliteDb(open_memory_database_or_throw("heap connection"));
    auto* heap_statement = new SyncSqliteStmt(sqlite_prepare_or_throw(
        heap_database->db, "SELECT 1;", "heap statement"));
    require_child_fail_stop(
        test,
        [&] { delete heap_statement; },
        "child destructor cannot finalize an inherited statement");
    require_child_fail_stop(
        test,
        [&] { delete heap_database; },
        "child destructor cannot close an inherited connection");
    delete heap_statement;
    delete heap_database;

    require_child_success(
        test,
        [] {
            {
                SyncSqliteDb child_database =
                    open_memory_database_or_throw("child-local owner");
                sqlite_exec_or_throw(child_database.db,
                                     "CREATE TABLE child_local(value INTEGER);",
                                     "child-local schema");
            }
        },
        "child can create and destroy a child-local connection");

    SyncSqliteDb empty_before_fork;
    require_child_success(
        test,
        [&] {
            const int rc = sqlite3_open_v2(
                ":memory:",
                empty_before_fork.db.out(),
                SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                    SQLITE_OPEN_FULLMUTEX,
                nullptr);
            if (rc != SQLITE_OK) throw std::runtime_error("child open failed");
            sqlite_exec_or_throw(empty_before_fork.db,
                                 "SELECT 1;",
                                 "child acquisition into inherited empty slot");
            empty_before_fork.db.reset();
        },
        "an empty pre-fork slot may mint a child-local connection");
    test.require(empty_before_fork.db.empty(),
                 "child-local acquisition cannot mutate the parent slot");

    test.require(sqlite3_step(statement.stmt) == SQLITE_ROW &&
                     sqlite3_column_int(statement.stmt, 0) == 42,
                 "parent statement remains usable after hostile child probes");
    test.require(database.db.get() == inherited_database &&
                     statement.stmt.get() == inherited_statement,
                 "parent retains exact handles after hostile child probes");
}

void test_strict_owner_generation_close(TestState& test) {
    require_child_fail_stop(
        test,
        [] {
            SyncSqliteDb database =
                open_memory_database_or_throw("live borrow close fixture");
            SyncSqliteStmt statement = sqlite_prepare_or_throw(
                database.db, "SELECT 1;", "live borrow close statement");
            if (database.db.active_borrows() != 1 ||
                statement.owner_generation() != database.db.generation()) {
                throw std::runtime_error("owner-generation pin was not established");
            }
            database.db.reset();
        },
        "same-process close cannot cross a generation-bound statement");

    require_child_fail_stop(
        test,
        [] {
            SyncSqliteDb database =
                open_memory_database_or_throw("untracked transaction close fixture");
            sqlite_exec_or_throw(database.db.get(),
                                 "BEGIN IMMEDIATE;",
                                 "untracked transaction begin");
            if (sqlite3_get_autocommit(database.db.get()) != 0) {
                throw std::runtime_error("raw transaction did not begin");
            }
            database.db.reset();
        },
        "strict close fails stopped before SQLite can auto-rollback a raw transaction");

    require_child_fail_stop(
        test,
        [] {
            SyncSqliteDb database =
                open_memory_database_or_throw("untracked statement close fixture");
            sqlite3_stmt* raw_statement = nullptr;
            if (sqlite3_prepare_v2(database.db,
                                   "SELECT 1;",
                                   -1,
                                   &raw_statement,
                                   nullptr) != SQLITE_OK ||
                raw_statement == nullptr) {
                throw std::runtime_error("raw statement prepare failed");
            }
            // No AnonSync borrow exists, so strict sqlite3_close() itself must
            // reject the hidden dependent instead of creating a zombie owner.
            database.db.reset();
        },
        "strict close fails stopped on an untracked SQLite dependent");
}

void test_process_bound_authority_and_transaction(TestState& test) {
    SyncSqliteDb database = open_memory_database_or_throw("authority fixture");
    sqlite3* const raw_database = database.db.get();
    const SyncSqliteConnectionAuthorityProof proof =
        install_sync_sqlite_connection_authority_or_throw(
            raw_database, allow_policy, nullptr, "fork authority fixture");
    test.require(proof.valid() && proof.authorizer_generation() == 1,
                 "parent authority proof is live before fork");

    require_child_success(
        test,
        [&] {
            if (proof.valid()) {
                throw std::runtime_error("inherited proof remained valid");
            }
        },
        "child observes inherited authority proof as invalid");
    require_child_fail_stop(
        test,
        [&] {
            auto lease = acquire_sync_sqlite_connection_authority_or_throw(
                raw_database, proof, "inherited proof acquisition");
            (void)lease;
        },
        "child cannot acquire authority from an inherited proof");

    auto lease = std::make_unique<SyncSqliteConnectionAuthorityLease>(
        acquire_sync_sqlite_connection_authority_or_throw(
            raw_database, proof, "parent lease fixture"));
    test.require(lease->active(), "parent lease is active before fork");
    require_child_success(
        test,
        [&] {
            if (lease->active()) {
                throw std::runtime_error("inherited lease remained active");
            }
        },
        "child observes inherited authority lease as inactive");
    require_child_fail_stop(
        test,
        [&] {
            SyncSqliteConnectionAuthorityLease moved(std::move(*lease));
            (void)moved;
        },
        "child cannot move an inherited authority lease");
    require_child_fail_stop(
        test,
        [&] { lease.reset(); },
        "child cannot destroy an inherited authority lease");
    test.require(lease->active(),
                 "parent lease remains active after hostile child probes");
    lease.reset();

    auto transaction = std::make_unique<SyncSqliteTransaction>(
        raw_database,
        "fork transaction fixture",
        SyncSqliteTransactionMode::Immediate);
    const SyncSqliteTransactionAuthority transaction_authority =
        transaction->authority();
    test.require(transaction->active() &&
                     transaction_authority.authorizes(raw_database),
                 "parent transaction generation is authoritative before fork");
    require_child_success(
        test,
        [&] {
            if (transaction->active() ||
                transaction->authorizes(raw_database) ||
                transaction_authority.authorizes(raw_database)) {
                throw std::runtime_error(
                    "inherited transaction authority remained active");
            }
        },
        "child observes inherited transaction capabilities as inactive");
    require_child_fail_stop(
        test,
        [&] { transaction.reset(); },
        "child cannot destruct an inherited live transaction");
    test.require(transaction->active() &&
                     transaction_authority.authorizes(raw_database),
                 "parent transaction remains authoritative after child probes");

    auto savepoint = std::make_unique<SyncSqliteSavepoint>(
        raw_database,
        transaction_authority,
        "fork savepoint fixture");
    test.require(savepoint->active(),
                 "parent savepoint generation is authoritative before fork");
    require_child_success(
        test,
        [&] {
            if (savepoint->active()) {
                throw std::runtime_error(
                    "inherited savepoint authority remained active");
            }
        },
        "child observes inherited savepoint capability as inactive");
    require_child_fail_stop(
        test,
        [&] { savepoint.reset(); },
        "child cannot destruct an inherited live savepoint");
    test.require(savepoint->active() && transaction->active(),
                 "parent savepoint remains authoritative after child probes");
    savepoint->rollback();
    test.require(!savepoint->active() && transaction->active(),
                 "savepoint rollback revokes only its exact parent-process generation");
    savepoint.reset();

    transaction->rollback();
    test.require(!transaction->active() &&
                     !transaction_authority.authorizes(raw_database),
                 "rollback revokes the exact parent transaction generation");
    transaction.reset();

    SyncSqliteConnectionAuthorityLease final_lease =
        acquire_sync_sqlite_connection_authority_or_throw(
            raw_database, proof, "parent continuity lease");
    test.require(final_lease.active(),
                 "parent authority remains usable after all fork probes");
}

#else

void test_busy_timeout_mutation_guard_execution_affinity(TestState& test) {
    test.require(
        true,
        "SQLite mutation-guard affinity tests are not supported on this platform");
}

void test_process_bound_handle_slots(TestState& test) {
    test.require(true, "fork handle-slot tests are not supported on this platform");
}

void test_strict_owner_generation_close(TestState& test) {
    test.require(true, "strict fork close tests are not supported on this platform");
}

void test_process_bound_authority_and_transaction(TestState& test) {
    test.require(true, "fork authority tests are not supported on this platform");
}

#endif

}  // namespace

int main() {
    TestState test;
    try {
        test_busy_timeout_mutation_guard_execution_affinity(test);
        test_process_bound_handle_slots(test);
        test_strict_owner_generation_close(test);
        test_process_bound_authority_and_transaction(test);
    } catch (const std::exception& error) {
        ++test.failed;
        std::cerr << "FAIL: unexpected exception: " << error.what() << "\n";
    } catch (...) {
        ++test.failed;
        std::cerr << "FAIL: unexpected non-standard exception\n";
    }

    std::cout << "sqlite process authority fork checks=" << test.passed
              << " failures=" << test.failed << "\n";
    return test.failed == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
