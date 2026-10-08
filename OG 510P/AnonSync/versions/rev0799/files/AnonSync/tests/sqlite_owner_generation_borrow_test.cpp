#include "sync_sqlite_process_incarnation.hpp"
#include "sync_sqlite_support.hpp"

#include <array>
#include <atomic>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <thread>
#include <type_traits>
#include <utility>

#if !defined(_WIN32)
#include <sys/wait.h>
#include <unistd.h>
#endif

namespace {

static_assert(!std::is_constructible_v<
                  anonsync::SyncSqliteSerializedDbBorrow, sqlite3*>,
              "a raw SQLite address must not mint serialized authority");
static_assert(!std::is_convertible_v<
                  anonsync::SyncSqliteSerializedDbBorrow, sqlite3*>,
              "serialized authority must not implicitly decay to a raw address");
static_assert(!std::is_constructible_v<
                  anonsync::SyncSqliteSerializedDbBorrow,
                  anonsync::SyncSqliteDbHandleBorrow>,
              "a generic owner borrow must not self-upgrade to serialized authority");
static_assert(!std::is_copy_constructible_v<
                  anonsync::SyncSqliteSerializedDbBorrow> &&
                  !std::is_copy_assignable_v<
                      anonsync::SyncSqliteSerializedDbBorrow>,
              "serialized authority must remain a unique lifetime pin");
static_assert(std::is_nothrow_move_constructible_v<
                  anonsync::SyncSqliteSerializedDbBorrow> &&
                  std::is_nothrow_move_assignable_v<
                      anonsync::SyncSqliteSerializedDbBorrow>,
              "serialized authority transfer must not strand a live pin");

std::size_t checks = 0;

[[noreturn]] void fail(std::string_view message) {
    std::cerr << "FAIL: " << message << '\n';
    std::exit(1);
}

void require(bool value, std::string_view message) {
    ++checks;
    if (!value) fail(message);
}

template <class F>
void require_logic_error(F&& operation, std::string_view message) {
    try {
        std::forward<F>(operation)();
    } catch (const std::logic_error&) {
        ++checks;
        return;
    } catch (const std::exception& error) {
        std::cerr << "unexpected exception: " << error.what() << '\n';
        fail(message);
    }
    fail(message);
}

template <class F>
void require_runtime_error(F&& operation,
                           std::string_view expected_fragment,
                           std::string_view message) {
    try {
        std::forward<F>(operation)();
    } catch (const std::runtime_error& error) {
        require(std::string_view(error.what()).find(expected_fragment) !=
                    std::string_view::npos,
                std::string(message) + " returned the wrong error");
        return;
    } catch (const std::exception& error) {
        std::cerr << "unexpected exception: " << error.what() << '\n';
        fail(message);
    }
    fail(message);
}


struct AuthorizerBorrowObservation final {
    anonsync::SyncSqliteDbHandleSlot* owner = nullptr;
    std::size_t callbacks = 0;
    std::size_t unpinned_callbacks = 0;
};

int observe_owner_borrow_authorizer(void* context,
                                    int,
                                    const char*,
                                    const char*,
                                    const char*,
                                    const char*) noexcept {
    auto* observation = static_cast<AuthorizerBorrowObservation*>(context);
    if (observation == nullptr || observation->owner == nullptr) {
        return SQLITE_DENY;
    }
    ++observation->callbacks;
    if (observation->owner->active_borrows() == 0) {
        ++observation->unpinned_callbacks;
    }
    return SQLITE_OK;
}

anonsync::SyncSqliteDb open_memory_database(std::string_view label) {
    anonsync::SyncSqliteDb owner;
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                      SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
    const int rc = sqlite3_open_v2(":memory:", owner.db.out(), flags, nullptr);
    if (rc != SQLITE_OK) {
        fail(std::string(label) + " open failed");
    }
    return owner;
}

anonsync::SyncSqliteDb open_unserialized_memory_database(
    std::string_view label) {
    anonsync::SyncSqliteDb owner;
    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                      SQLITE_OPEN_NOMUTEX | SQLITE_OPEN_PRIVATECACHE;
    const int rc = sqlite3_open_v2(":memory:", owner.db.out(), flags, nullptr);
    if (rc != SQLITE_OK) {
        fail(std::string(label) + " open failed");
    }
    return owner;
}

void connection_mutex_mode_is_exact_generation_evidence() {
    anonsync::SyncSqliteDb serialized =
        open_memory_database("serialized mode fixture");
    auto serialized_borrow = serialized.db.borrow();
    require(sqlite3_db_mutex(serialized.db.get()) != nullptr,
            "FULLMUTEX fixture did not materialize a connection mutex");
    require(serialized_borrow.connection_mutex_mode() ==
                anonsync::SyncSqliteConnectionMutexMode::Serialized,
            "FULLMUTEX owner generation was not classified as serialized");
    require(serialized_borrow.serialized_connection(),
            "serialized owner generation did not expose serialized authority");
    auto serialized_capability =
        anonsync::borrow_sync_sqlite_serialized_db_or_throw(
            serialized.db, "serialized generation probe");
    require(serialized_capability.get() == serialized.db.get() &&
                serialized_capability.generation() ==
                    serialized_borrow.generation(),
            "serialized capability changed the exact owner generation");
    require(serialized_capability.connection_mutex_mode() ==
                anonsync::SyncSqliteConnectionMutexMode::Serialized,
            "serialized capability lost its mutex-mode proof");
    auto moved_serialized_capability = std::move(serialized_capability);
    require(!serialized_capability &&
                moved_serialized_capability.generation() ==
                    serialized_borrow.generation(),
            "serialized capability move lost exact owner-generation evidence");
    moved_serialized_capability.reset();
    const std::uint64_t serialized_generation = serialized_borrow.generation();
    serialized_borrow.reset();
    serialized.db.reset();

    anonsync::SyncSqliteDb unserialized =
        open_unserialized_memory_database("unserialized mode fixture");
    auto first = unserialized.db.borrow();
    require(sqlite3_db_mutex(unserialized.db.get()) == nullptr,
            "NOMUTEX fixture unexpectedly materialized a connection mutex");
    const std::uint64_t unserialized_generation = first.generation();
    require(first.connection_mutex_mode() ==
                anonsync::SyncSqliteConnectionMutexMode::Unserialized,
            "NOMUTEX owner generation was not classified as unserialized");
    require(!first.serialized_connection(),
            "NOMUTEX owner generation appeared serialized");
    require_runtime_error(
        [&] {
            (void)anonsync::borrow_sync_sqlite_serialized_db_or_throw(
                unserialized.db, "unserialized generation probe");
        },
        "serialized/FULLMUTEX",
        "NOMUTEX generation was accepted as serialized");

    auto moved = std::move(first);
    require(moved.generation() == unserialized_generation &&
                moved.connection_mutex_mode() ==
                    anonsync::SyncSqliteConnectionMutexMode::Unserialized,
            "borrow move lost exact mutex-mode evidence");
    require(sqlite3_exec(moved.get(),
                         "CREATE TABLE raw_compatibility(value INTEGER);",
                         nullptr,
                         nullptr,
                         nullptr) == SQLITE_OK,
            "unserialized raw compatibility path stopped working");
    moved.reset();
    unserialized.db.reset();

    const int reopen_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                             SQLITE_OPEN_FULLMUTEX |
                             SQLITE_OPEN_PRIVATECACHE;
    require(sqlite3_open_v2(":memory:",
                            unserialized.db.out(),
                            reopen_flags,
                            nullptr) == SQLITE_OK,
            "serialized reopen after NOMUTEX generation failed");
    auto reopened = unserialized.db.borrow();
    require(reopened.generation() > unserialized_generation &&
                reopened.connection_mutex_mode() ==
                    anonsync::SyncSqliteConnectionMutexMode::Serialized,
            "reopen did not bind new mutex mode to a new owner generation");
    require(reopened.generation() >= serialized_generation,
            "owner generation regressed while changing mutex mode");
    reopened.reset();
    unserialized.db.reset();
}

void typed_owner_paths_reject_unserialized_generation_before_sql() {
    anonsync::SyncSqliteDb owner =
        open_unserialized_memory_database("typed NOMUTEX rejection fixture");
    anonsync::sqlite_exec_or_throw(
        owner.db.get(),
        "CREATE TABLE records(session_id TEXT NOT NULL, value INTEGER NOT NULL);"
        "INSERT INTO records(session_id,value) VALUES('session-a',1);",
        "raw compatibility schema");

    AuthorizerBorrowObservation observation{std::addressof(owner.db)};
    require(sqlite3_set_authorizer(owner.db.get(),
                                   observe_owner_borrow_authorizer,
                                   std::addressof(observation)) == SQLITE_OK,
            "could not install NOMUTEX rejection authorizer");

    const auto require_rejected_without_sql =
        [&](auto&& operation, std::string_view label) {
            observation.callbacks = 0;
            observation.unpinned_callbacks = 0;
            require_runtime_error(std::forward<decltype(operation)>(operation),
                                  "serialized/FULLMUTEX",
                                  label);
            require(observation.callbacks == 0,
                    std::string(label) + " touched SQLite before rejection");
            require(owner.db.active_borrows() == 0,
                    std::string(label) + " leaked an owner-generation pin");
            require(sqlite3_get_autocommit(owner.db.get()) != 0,
                    std::string(label) + " changed transaction state");
        };

    require_rejected_without_sql(
        [&] {
            anonsync::sqlite_exec_or_throw(
                owner.db, "SELECT 1;", "typed NOMUTEX exec");
        },
        "typed exec accepted NOMUTEX");
    require_rejected_without_sql(
        [&] {
            (void)anonsync::sqlite_prepare_or_throw(
                owner.db, "SELECT 1;", "typed NOMUTEX prepare");
        },
        "typed prepare accepted NOMUTEX");
    require_rejected_without_sql(
        [&] {
            (void)anonsync::sqlite_count_for_session_or_throw(
                owner.db,
                "SELECT COUNT(*) FROM records WHERE session_id=?;",
                "session-a",
                "typed NOMUTEX count");
        },
        "typed count accepted NOMUTEX");
    require_rejected_without_sql(
        [&] {
            (void)anonsync::sqlite_table_exists_or_throw(
                owner.db, "records", "typed NOMUTEX table probe");
        },
        "typed table probe accepted NOMUTEX");
    require_rejected_without_sql(
        [&] {
            (void)anonsync::sqlite_table_column_exists_or_throw(
                owner.db,
                "records",
                "value",
                "typed NOMUTEX column probe");
        },
        "typed column probe accepted NOMUTEX");
    require_rejected_without_sql(
        [&] {
            anonsync::SyncSqliteTransaction transaction(
                owner.db,
                "typed NOMUTEX transaction",
                anonsync::SyncSqliteTransactionMode::Immediate);
            (void)transaction;
        },
        "typed transaction accepted NOMUTEX");

    require(sqlite3_set_authorizer(owner.db.get(), nullptr, nullptr) ==
                SQLITE_OK,
            "could not clear NOMUTEX rejection authorizer");
    require(sqlite3_exec(owner.db.get(),
                         "INSERT INTO records(session_id,value) "
                         "VALUES('raw-still-live',2);",
                         nullptr,
                         nullptr,
                         nullptr) == SQLITE_OK,
            "typed rejection damaged raw compatibility state");
    owner.db.reset();
}

void exact_generation_survives_owner_move() {
    anonsync::SyncSqliteDb owner = open_memory_database("move fixture");
    const std::uint64_t generation = owner.db.generation();
    auto borrow = owner.db.borrow();
    sqlite3* const raw = borrow.get();

    anonsync::SyncSqliteDb moved = std::move(owner);
    require(owner.db.empty(), "moved-from owner was not empty");
    require(moved.db.get() == raw, "owner move changed the SQLite address");
    require(moved.db.generation() == generation,
            "owner move changed the exact generation");
    require(borrow.get() == raw,
            "exact-generation borrow did not follow the owner move");
    require(moved.db.active_borrows() == 1,
            "owner move lost the active borrow pin");

    borrow.reset();
    require(moved.db.active_borrows() == 0,
            "borrow reset did not revoke the pin");
    moved.db.reset();
}

void generation_advances_after_strict_close_and_reopen() {
    anonsync::SyncSqliteDb owner = open_memory_database("generation fixture");
    auto first = owner.db.borrow();
    const std::uint64_t first_generation = first.generation();
    first.reset();
    owner.db.reset();

    const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                      SQLITE_OPEN_FULLMUTEX | SQLITE_OPEN_PRIVATECACHE;
    require(sqlite3_open_v2(":memory:", owner.db.out(), flags, nullptr) == SQLITE_OK,
            "reopen failed");
    auto second = owner.db.borrow();
    require(second.generation() > first_generation,
            "owner generation did not advance across reopen");
    second.reset();
    owner.db.reset();
}


void typed_helper_overloads_hold_owner_generation() {
    anonsync::SyncSqliteDb owner = open_memory_database("typed helper fixture");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "CREATE TABLE records(session_id TEXT NOT NULL, value INTEGER NOT NULL);"
        "INSERT INTO records(session_id,value) VALUES('session-a',1);",
        "typed helper schema");

    AuthorizerBorrowObservation observation{std::addressof(owner.db)};
    require(sqlite3_set_authorizer(owner.db.get(),
                                   observe_owner_borrow_authorizer,
                                   std::addressof(observation)) == SQLITE_OK,
            "could not install borrow-observing authorizer");

    const auto reset_observation = [&] {
        observation.callbacks = 0;
        observation.unpinned_callbacks = 0;
    };
    const auto require_pinned = [&](std::string_view label) {
        require(observation.callbacks != 0,
                std::string(label) + " did not reach the authorizer");
        require(observation.unpinned_callbacks == 0,
                std::string(label) + " downgraded to an unpinned raw handle");
        require(owner.db.active_borrows() == 0,
                std::string(label) + " leaked an owner-generation pin");
    };

    reset_observation();
    anonsync::sqlite_exec_or_throw(owner.db, "SELECT 1;", "typed exec probe");
    require_pinned("typed exec helper");

    reset_observation();
    require(anonsync::sqlite_count_for_session_or_throw(
                owner.db,
                "SELECT COUNT(*) FROM records WHERE session_id=?;",
                "session-a",
                "typed count probe") == 1,
            "typed count helper returned the wrong value");
    require_pinned("typed count helper");

    reset_observation();
    require(anonsync::sqlite_table_exists_or_throw(
                owner.db, "records", "typed table probe"),
            "typed table helper did not find the table");
    require_pinned("typed table helper");

    reset_observation();
    require(anonsync::sqlite_table_column_exists_or_throw(
                owner.db, "records", "value", "typed column probe"),
            "typed column helper did not find the column");
    require_pinned("typed column helper");

    require(sqlite3_set_authorizer(owner.db.get(), nullptr, nullptr) == SQLITE_OK,
            "could not clear borrow-observing authorizer");
    owner.db.reset();
}

void typed_statement_pins_exact_owner_generation() {
    anonsync::SyncSqliteDb owner = open_memory_database("statement fixture");
    const std::uint64_t generation = owner.db.generation();
    anonsync::SyncSqliteStmt statement = anonsync::sqlite_prepare_or_throw(
        owner.db, "SELECT 1;", "typed statement fixture");

    require(statement.owner_generation() == generation,
            "typed statement lost the owner generation");
    require(statement.owner_connection_mutex_mode() ==
                anonsync::SyncSqliteConnectionMutexMode::Serialized,
            "typed statement lost serialized owner-generation evidence");
    require(owner.db.active_borrows() == 1,
            "typed statement did not pin its owner");
    require(sqlite3_step(statement.stmt) == SQLITE_ROW,
            "typed statement did not execute");

    statement.reset();
    require(owner.db.active_borrows() == 0,
            "statement reset released dependencies in the wrong order");
    owner.db.reset();
}

void typed_statement_move_and_failure_paths_release_exactly_once() {
    anonsync::SyncSqliteDb owner = open_memory_database("statement move fixture");
    anonsync::SyncSqliteStmt first = anonsync::sqlite_prepare_or_throw(
        owner.db, "SELECT 1;", "first typed statement");
    anonsync::SyncSqliteStmt second = anonsync::sqlite_prepare_or_throw(
        owner.db, "SELECT 2;", "second typed statement");
    require(owner.db.active_borrows() == 2,
            "two typed statements did not hold two owner pins");

    second = std::move(first);
    require(owner.db.active_borrows() == 1,
            "statement move assignment did not release the replaced pin");
    require(second.owner_generation() == owner.db.generation() &&
                sqlite3_step(second.stmt) == SQLITE_ROW,
            "statement move assignment lost the transferred generation");

    auto* const second_alias = std::addressof(second);
    second = std::move(*second_alias);
    require(owner.db.active_borrows() == 1,
            "statement self-move changed the owner pin count");
    second.reset();
    require(owner.db.active_borrows() == 0,
            "moved statement did not release its final owner pin");

    try {
        (void)anonsync::sqlite_prepare_or_throw(
            owner.db, "SELECT FROM;", "failing typed statement");
        fail("invalid typed prepare unexpectedly succeeded");
    } catch (const anonsync::SyncSqliteException&) {
        require(owner.db.active_borrows() == 0,
                "failed typed prepare leaked an owner pin");
    }
    owner.db.reset();
}

void typed_transaction_pins_only_while_active() {
    anonsync::SyncSqliteDb owner = open_memory_database("transaction fixture");
    {
        anonsync::SyncSqliteTransaction transaction(
            owner.db,
            "typed owner-generation transaction",
            anonsync::SyncSqliteTransactionMode::Deferred);
        require(owner.db.active_borrows() == 1,
                "typed transaction did not pin its owner generation");
        transaction.rollback();
        require(owner.db.active_borrows() == 0,
                "completed transaction retained an inert owner pin");
    }
    owner.db.reset();
}

void typed_transaction_constructor_failure_releases_its_pin() {
    anonsync::SyncSqliteDb owner = open_memory_database("transaction failure fixture");
    anonsync::SyncSqliteTransaction outer(
        owner.db,
        "outer typed owner-generation transaction",
        anonsync::SyncSqliteTransactionMode::Deferred);
    require(owner.db.active_borrows() == 1,
            "outer transaction did not establish its owner pin");
    try {
        anonsync::SyncSqliteTransaction nested(
            owner.db,
            "nested typed owner-generation transaction",
            anonsync::SyncSqliteTransactionMode::Deferred);
        (void)nested;
        fail("nested transaction unexpectedly succeeded");
    } catch (const std::exception&) {
        require(owner.db.active_borrows() == 1,
                "failed transaction construction leaked its owner pin");
    }
    outer.rollback();
    require(owner.db.active_borrows() == 0,
            "outer rollback did not release the remaining owner pin");
    owner.db.reset();
}

void empty_borrow_is_not_authority() {
    anonsync::SyncSqliteDbHandleBorrow empty;
    require(!empty, "default borrow appeared live");
    require(empty.get() == nullptr,
            "empty borrow returned a SQLite handle");
    require(empty.generation() == 0,
            "empty borrow returned a generation");
    auto* const empty_alias = std::addressof(empty);
    empty = std::move(*empty_alias);
    require(!empty, "self-moved empty borrow appeared live");

    anonsync::SyncSqliteDbHandleSlot empty_owner;
    require_logic_error([&] { (void)empty_owner.borrow(); },
                        "empty owner issued an exact-generation borrow");
    anonsync::SyncSqliteDbHandleSlot moved_owner = std::move(empty_owner);
    require_logic_error([&] { (void)empty_owner.borrow(); },
                        "moved-from owner issued an exact-generation borrow");
    require(moved_owner.empty(), "moved empty owner became nonempty");
}

void serialized_borrow_can_cross_threads_without_losing_generation() {
    anonsync::SyncSqliteDb owner = open_memory_database("thread fixture");
    auto borrow = anonsync::borrow_sync_sqlite_serialized_db_or_throw(
        owner.db, "cross-thread serialized fixture");
    const std::uint64_t generation = borrow.generation();
    sqlite3* const raw = borrow.get();
    std::atomic<bool> used{false};

    std::thread worker(
        [capability = std::move(borrow), raw, generation, &used]() mutable {
            if (capability.get() == raw &&
                capability.generation() == generation &&
                sqlite3_exec(capability.get(),
                             "CREATE TABLE thread_probe(value INTEGER);",
                             nullptr,
                             nullptr,
                             nullptr) == SQLITE_OK) {
                used.store(true, std::memory_order_release);
            }
            capability.reset();
        });
    worker.join();

    require(used.load(std::memory_order_acquire),
            "cross-thread exact-generation borrow was not usable");
    require(owner.db.active_borrows() == 0,
            "cross-thread borrow release leaked an owner pin");
    owner.db.reset();
}

void serialized_capabilities_coordinate_concurrent_sqlite_use() {
    anonsync::SyncSqliteDb owner =
        open_memory_database("concurrent serialized fixture");
    anonsync::sqlite_exec_or_throw(
        owner.db,
        "CREATE TABLE concurrent_probe(worker INTEGER NOT NULL, "
        "sequence INTEGER NOT NULL, PRIMARY KEY(worker,sequence));",
        "concurrent serialized schema");

    constexpr int kThreadCount = 4;
    constexpr int kWritesPerThread = 80;
    std::atomic<int> ready{0};
    std::atomic<bool> go{false};
    std::atomic<int> failures{0};
    std::array<std::thread, kThreadCount> workers;

    for (int worker_index = 0; worker_index < kThreadCount; ++worker_index) {
        workers[worker_index] = std::thread([&, worker_index] {
            auto capability =
                anonsync::borrow_sync_sqlite_serialized_db_or_throw(
                    owner.db, "concurrent serialized worker");
            ready.fetch_add(1, std::memory_order_release);
            while (!go.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            for (int sequence = 0; sequence < kWritesPerThread; ++sequence) {
                const std::string sql =
                    "INSERT INTO concurrent_probe(worker,sequence) VALUES(" +
                    std::to_string(worker_index) + "," +
                    std::to_string(sequence) + ");";
                if (sqlite3_exec(capability.get(),
                                 sql.c_str(),
                                 nullptr,
                                 nullptr,
                                 nullptr) != SQLITE_OK) {
                    failures.fetch_add(1, std::memory_order_release);
                    break;
                }
            }
            capability.reset();
        });
    }

    while (ready.load(std::memory_order_acquire) != kThreadCount) {
        std::this_thread::yield();
    }
    require(owner.db.active_borrows() == kThreadCount,
            "concurrent serialized workers did not retain exact-generation pins");
    go.store(true, std::memory_order_release);
    for (auto& worker : workers) worker.join();

    require(failures.load(std::memory_order_acquire) == 0,
            "serialized capabilities did not coordinate concurrent SQLite use");
    require(owner.db.active_borrows() == 0,
            "concurrent serialized workers leaked generation pins");
    anonsync::SyncSqliteStmt count = anonsync::sqlite_prepare_or_throw(
        owner.db,
        "SELECT COUNT(*) FROM concurrent_probe;",
        "concurrent serialized count");
    require(sqlite3_step(count.stmt) == SQLITE_ROW &&
                sqlite3_column_int(count.stmt, 0) ==
                    kThreadCount * kWritesPerThread,
            "concurrent serialized use lost committed rows");
    count.reset();
    owner.db.reset();
}

void lifecycle_lock_contention_preserves_exact_accounting() {
    anonsync::SyncSqliteDb owner = open_memory_database("contention fixture");
    constexpr int kThreadCount = 6;
    constexpr int kBorrowsPerThread = 4000;
    const std::uint64_t generation = owner.db.generation();
    std::atomic<int> ready{0};
    std::atomic<bool> go{false};
    std::atomic<int> completed{0};
    std::array<std::thread, kThreadCount> workers;

    for (auto& worker : workers) {
        worker = std::thread([&] {
            ready.fetch_add(1, std::memory_order_release);
            while (!go.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            for (int index = 0; index < kBorrowsPerThread; ++index) {
                auto capability = owner.db.borrow();
                if (capability.get() != owner.db.get() ||
                    capability.generation() != generation) {
                    fail("contended borrow lost exact owner generation");
                }
            }
            completed.fetch_add(1, std::memory_order_release);
        });
    }

    while (ready.load(std::memory_order_acquire) != kThreadCount) {
        std::this_thread::yield();
    }
    go.store(true, std::memory_order_release);
    for (auto& worker : workers) worker.join();

    require(completed.load(std::memory_order_acquire) == kThreadCount,
            "lifecycle contention lost a worker");
    require(owner.db.active_borrows() == 0,
            "lifecycle contention leaked an owner-generation pin");
    require(owner.db.generation() == generation,
            "lifecycle contention changed the owner generation");
    owner.db.reset();
}

void unserialized_borrow_evidence_is_serialized_under_contention() {
    anonsync::SyncSqliteDb owner =
        open_unserialized_memory_database("NOMUTEX accounting fixture");
    constexpr int kThreadCount = 4;
    constexpr int kBorrowsPerThread = 3000;
    const std::uint64_t generation = owner.db.generation();
    std::atomic<int> ready{0};
    std::atomic<bool> go{false};
    std::atomic<int> completed{0};
    std::array<std::thread, kThreadCount> workers;

    for (auto& worker : workers) {
        worker = std::thread([&] {
            ready.fetch_add(1, std::memory_order_release);
            while (!go.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
            for (int index = 0; index < kBorrowsPerThread; ++index) {
                auto capability = owner.db.borrow();
                if (capability.generation() != generation ||
                    capability.connection_mutex_mode() !=
                        anonsync::SyncSqliteConnectionMutexMode::Unserialized) {
                    fail("NOMUTEX lifecycle accounting lost frozen generation evidence");
                }
            }
            completed.fetch_add(1, std::memory_order_release);
        });
    }

    while (ready.load(std::memory_order_acquire) != kThreadCount) {
        std::this_thread::yield();
    }
    go.store(true, std::memory_order_release);
    for (auto& worker : workers) worker.join();

    require(completed.load(std::memory_order_acquire) == kThreadCount,
            "NOMUTEX lifecycle accounting lost a worker");
    require(owner.db.active_borrows() == 0,
            "NOMUTEX lifecycle accounting leaked a generation pin");
    require(owner.db.generation() == generation,
            "NOMUTEX lifecycle accounting changed the generation");
    owner.db.reset();
}

#if !defined(_WIN32)
template <class ChildOperation>
void require_child_exit(ChildOperation&& operation,
                        int expected_exit,
                        std::string_view label) {
    const pid_t child = ::fork();
    require(child >= 0, "fork failed");
    if (child == 0) {
        std::forward<ChildOperation>(operation)();
        ::_exit(0);
    }
    int status = 0;
    require(::waitpid(child, &status, 0) == child, "waitpid failed");
    require(WIFEXITED(status), std::string(label) + " did not exit normally");
    require(WEXITSTATUS(status) == expected_exit,
            std::string(label) + " returned the wrong fail-stop status");
}

void inherited_borrow_fails_before_touching_sqlite() {
    anonsync::SyncSqliteDb owner = open_memory_database("fork fixture");
    auto borrow = owner.db.borrow();
    require_child_exit(
        [&] { (void)borrow.get(); },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "inherited borrow use");
    require(borrow.get() == owner.db.get(),
            "child fail-stop disturbed the parent borrow");
    borrow.reset();
    owner.db.reset();
}

void inherited_serialized_borrow_fails_before_touching_sqlite() {
    anonsync::SyncSqliteDb owner =
        open_memory_database("fork serialized fixture");
    auto borrow = anonsync::borrow_sync_sqlite_serialized_db_or_throw(
        owner.db, "fork serialized fixture");
    require_child_exit(
        [&] { (void)borrow.get(); },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "inherited serialized borrow use");
    require(borrow.get() == owner.db.get(),
            "child fail-stop disturbed the parent serialized borrow");
    borrow.reset();
    owner.db.reset();
}

void inherited_serialized_borrow_cannot_move_or_destruct() {
    anonsync::SyncSqliteDb owner =
        open_memory_database("fork serialized lifetime fixture");
    auto* borrow = new anonsync::SyncSqliteSerializedDbBorrow(
        anonsync::borrow_sync_sqlite_serialized_db_or_throw(
            owner.db, "fork serialized lifetime fixture"));
    require_child_exit(
        [&] {
            anonsync::SyncSqliteSerializedDbBorrow moved(std::move(*borrow));
            (void)moved;
        },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "inherited serialized borrow move");
    require_child_exit(
        [&] { delete borrow; },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "inherited serialized borrow destructor");
    require(borrow->get() == owner.db.get(),
            "child lifetime fail-stop disturbed the parent serialized borrow");
    delete borrow;
    owner.db.reset();
}

void inherited_borrow_move_fails_before_shared_state_transfer() {
    anonsync::SyncSqliteDb owner = open_memory_database("fork move fixture");
    auto borrow = owner.db.borrow();
    require_child_exit(
        [&] {
            anonsync::SyncSqliteDbHandleBorrow moved(std::move(borrow));
            (void)moved;
        },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "inherited borrow move construction");
    require_child_exit(
        [&] {
            anonsync::SyncSqliteDbHandleBorrow destination;
            destination = std::move(borrow);
        },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "inherited borrow move assignment");
    require(borrow.get() == owner.db.get(),
            "child move fail-stop disturbed the parent borrow");
    borrow.reset();
    owner.db.reset();
}

void live_borrow_blocks_owner_close() {
    require_child_exit(
        [] {
            anonsync::SyncSqliteDb owner =
                open_memory_database("live-borrow close fixture");
            auto borrow = owner.db.borrow();
            (void)borrow.get();
            owner.db.reset();
        },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "close with live exact-generation borrow");
}

void strict_close_rejects_untracked_raw_transaction() {
    require_child_exit(
        [] {
            anonsync::SyncSqliteDb owner =
                open_memory_database("strict raw transaction fixture");
            anonsync::sqlite_exec_or_throw(
                owner.db.get(), "BEGIN IMMEDIATE;", "raw transaction begin");
            if (sqlite3_get_autocommit(owner.db.get()) != 0) {
                ::_exit(13);
            }
            // sqlite3_close() would otherwise roll this transaction back and
            // report success, erasing the missing typed-boundary defect.
            owner.db.reset();
        },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "strict close with untracked raw transaction");
}

void strict_close_rejects_unfinalized_raw_statement() {
    require_child_exit(
        [] {
            anonsync::SyncSqliteDb owner =
                open_memory_database("strict-close fixture");
            sqlite3_stmt* raw_statement = nullptr;
            if (sqlite3_prepare_v2(owner.db.get(),
                                   "SELECT 1;",
                                   -1,
                                   &raw_statement,
                                   nullptr) != SQLITE_OK ||
                raw_statement == nullptr) {
                ::_exit(12);
            }
            // sqlite3_close_v2() would silently create a zombie connection.
            // The owner policy uses sqlite3_close() and fail-stops on BUSY.
            owner.db.reset();
        },
        anonsync::kSyncSqliteCapabilityViolationExitCode,
        "strict close with unfinalized raw statement");
}

void borrow_close_race_has_only_fail_closed_outcomes() {
    constexpr int kRaceIterations = 32;
    int clean_close_wins = 0;
    int fail_stop_borrow_wins = 0;

    for (int iteration = 0; iteration < kRaceIterations; ++iteration) {
        const pid_t child = ::fork();
        require(child >= 0, "race fork failed");
        if (child == 0) {
            anonsync::SyncSqliteDb owner =
                open_memory_database("borrow-close race fixture");
            std::atomic<int> ready{0};
            std::atomic<bool> go{false};
            std::atomic<bool> close_returned{false};
            std::atomic<int> borrow_result{0};

            std::thread borrower([&] {
                ready.fetch_add(1, std::memory_order_release);
                while (!go.load(std::memory_order_acquire)) {
                    std::this_thread::yield();
                }
                try {
                    auto capability = owner.db.borrow();
                    borrow_result.store(1, std::memory_order_release);
                    while (!close_returned.load(std::memory_order_acquire)) {
                        std::this_thread::yield();
                    }
                    capability.reset();
                } catch (const std::logic_error&) {
                    borrow_result.store(2, std::memory_order_release);
                } catch (...) {
                    ::_exit(12);
                }
            });

            std::thread closer([&] {
                ready.fetch_add(1, std::memory_order_release);
                while (!go.load(std::memory_order_acquire)) {
                    std::this_thread::yield();
                }
                owner.db.reset();
                close_returned.store(true, std::memory_order_release);
            });

            while (ready.load(std::memory_order_acquire) != 2) {
                std::this_thread::yield();
            }
            go.store(true, std::memory_order_release);
            closer.join();
            borrower.join();
            const bool close_won =
                owner.db.empty() &&
                borrow_result.load(std::memory_order_acquire) == 2;
            ::_exit(close_won ? 0 : 13);
        }

        int status = 0;
        require(::waitpid(child, &status, 0) == child,
                "race waitpid failed");
        require(WIFEXITED(status),
                "borrow-close race did not exit normally");
        const int exit_code = WEXITSTATUS(status);
        require(exit_code == 0 ||
                    exit_code ==
                        anonsync::kSyncSqliteCapabilityViolationExitCode,
                "borrow-close race produced a non-authoritative outcome");
        clean_close_wins += exit_code == 0 ? 1 : 0;
        fail_stop_borrow_wins +=
            exit_code == anonsync::kSyncSqliteCapabilityViolationExitCode ? 1
                                                                          : 0;
    }

    require(clean_close_wins + fail_stop_borrow_wins == kRaceIterations,
            "borrow-close race lost an iteration");
}
#endif

}  // namespace

int main() {
    connection_mutex_mode_is_exact_generation_evidence();
    typed_owner_paths_reject_unserialized_generation_before_sql();
    exact_generation_survives_owner_move();
    generation_advances_after_strict_close_and_reopen();
    typed_helper_overloads_hold_owner_generation();
    typed_statement_pins_exact_owner_generation();
    typed_statement_move_and_failure_paths_release_exactly_once();
    typed_transaction_pins_only_while_active();
    typed_transaction_constructor_failure_releases_its_pin();
    empty_borrow_is_not_authority();
    serialized_borrow_can_cross_threads_without_losing_generation();
    serialized_capabilities_coordinate_concurrent_sqlite_use();
    lifecycle_lock_contention_preserves_exact_accounting();
    unserialized_borrow_evidence_is_serialized_under_contention();
#if !defined(_WIN32)
    inherited_borrow_fails_before_touching_sqlite();
    inherited_serialized_borrow_fails_before_touching_sqlite();
    inherited_serialized_borrow_cannot_move_or_destruct();
    inherited_borrow_move_fails_before_shared_state_transfer();
    live_borrow_blocks_owner_close();
    strict_close_rejects_untracked_raw_transaction();
    strict_close_rejects_unfinalized_raw_statement();
    borrow_close_race_has_only_fail_closed_outcomes();
#endif
    std::cout << "sqlite owner-generation borrow checks passed: "
              << checks << "\n";
    return 0;
}
