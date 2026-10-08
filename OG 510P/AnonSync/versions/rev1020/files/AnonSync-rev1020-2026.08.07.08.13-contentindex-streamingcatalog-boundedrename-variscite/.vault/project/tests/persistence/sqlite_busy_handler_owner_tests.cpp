#include "sqlite_busy_handler_owner.hpp"
#include "sqlite_retained_callback_slots.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <thread>
#include <type_traits>

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;
using anonsync::SyncSqliteDbHandleSlot;
using anonsync::SyncSqliteSerializedDbBorrow;
using anonsync::borrow_sync_sqlite_serialized_db_or_throw;
using anonsync::persistence::SqliteBusyHandlerOwner;
using anonsync::persistence::SqliteBusyHandlerSnapshot;
using anonsync::persistence::kMaximumSqliteBusyHandlerWaitMilliseconds;

class Database final {
public:
    explicit Database(const fs::path& path) {
        const int result = sqlite3_open_v2(
            path.string().c_str(),
            database_.out(),
            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
            nullptr);
        if (result != SQLITE_OK) {
            sqlite3* const database = database_.get();
            const std::string detail =
                database == nullptr ? sqlite3_errstr(result)
                                    : sqlite3_errmsg(database);
            database_.reset();
            throw std::runtime_error("SQLite test database open failed: " +
                                     detail);
        }
    }

    ~Database() = default;

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    [[nodiscard]] sqlite3* get() const noexcept { return database_.get(); }

    [[nodiscard]] SyncSqliteSerializedDbBorrow busy_borrow(
        const std::string& label) const {
        return borrow_sync_sqlite_serialized_db_or_throw(database_, label);
    }

    [[nodiscard]] std::size_t active_borrows() const noexcept {
        return database_.active_borrows();
    }

private:
    SyncSqliteDbHandleSlot database_;
};

class TemporaryDatabasePath final {
public:
    TemporaryDatabasePath() {
        const auto stamp = std::chrono::steady_clock::now()
                               .time_since_epoch()
                               .count();
        path_ = fs::temp_directory_path() /
                ("anonsync-sqlite-busy-owner-" + std::to_string(stamp) +
                 "-" + std::to_string(sequence_.fetch_add(
                           1U, std::memory_order_relaxed)) +
                 ".sqlite");
    }

    ~TemporaryDatabasePath() {
        std::error_code error;
        fs::remove(path_, error);
        fs::remove(path_.string() + "-journal", error);
        fs::remove(path_.string() + "-wal", error);
        fs::remove(path_.string() + "-shm", error);
    }

    [[nodiscard]] const fs::path& get() const noexcept { return path_; }

private:
    inline static std::atomic<std::uint64_t> sequence_{0};
    fs::path path_;
};

void expect(bool condition, const std::string& label, int& checks) {
    ++checks;
    if (!condition) throw std::runtime_error("check failed: " + label);
}

void execute_or_throw(sqlite3* database,
                      const std::string& sql,
                      const std::string& label) {
    char* raw_error = nullptr;
    const int result = sqlite3_exec(
        database, sql.c_str(), nullptr, nullptr, &raw_error);
    const std::string detail = raw_error == nullptr ? std::string() : raw_error;
    sqlite3_free(raw_error);
    if (result != SQLITE_OK) {
        throw std::runtime_error(label + ": " +
                                 (detail.empty() ? sqlite3_errstr(result)
                                                 : detail));
    }
}

int execute_result(sqlite3* database, const std::string& sql) {
    char* raw_error = nullptr;
    const int result = sqlite3_exec(
        database, sql.c_str(), nullptr, nullptr, &raw_error);
    sqlite3_free(raw_error);
    return result;
}

template <typename Exception, typename Function>
void expect_exception(Function&& function,
                      const std::string& fragment,
                      const std::string& label,
                      int& checks) {
    bool matched = false;
    try {
        function();
    } catch (const Exception& error) {
        matched = std::string(error.what()).find(fragment) != std::string::npos;
    }
    expect(matched, label, checks);
}

void configure_lock_fixture(sqlite3* database) {
    execute_or_throw(database,
                     "PRAGMA journal_mode=DELETE;"
                     "CREATE TABLE IF NOT EXISTS evidence(value INTEGER NOT NULL);",
                     "lock fixture configuration");
}

void test_type_and_constructor_contract(int& checks) {
    static_assert(!std::is_copy_constructible_v<SqliteBusyHandlerOwner>);
    static_assert(!std::is_copy_assignable_v<SqliteBusyHandlerOwner>);
    static_assert(!std::is_move_constructible_v<SqliteBusyHandlerOwner>);
    static_assert(!std::is_move_assignable_v<SqliteBusyHandlerOwner>);
    expect(true, "busy owner address is stable", checks);

    TemporaryDatabasePath temporary;
    Database database(temporary.get());
    expect(database.active_borrows() == 0U,
           "new database begins without retained generations",
           checks);
    expect_exception<std::invalid_argument>(
        [] {
            SqliteBusyHandlerOwner owner(
                SyncSqliteSerializedDbBorrow{}, 1U, "empty generation");
        },
        "requires an exact serialized database-generation borrow",
        "empty database-generation borrow rejected",
        checks);
    expect(database.active_borrows() == 0U,
           "empty generation rejection cannot pin the database",
           checks);
    expect_exception<std::invalid_argument>(
        [&] {
            SqliteBusyHandlerOwner owner(
                database.busy_borrow("empty-label generation"), 1U, "");
        },
        "nonempty diagnostic label",
        "empty label rejected",
        checks);
    expect(database.active_borrows() == 0U,
           "label rejection releases the transferred generation",
           checks);
    expect_exception<std::invalid_argument>(
        [&] {
            SqliteBusyHandlerOwner owner(
                database.busy_borrow("widened-owner generation"),
                kMaximumSqliteBusyHandlerWaitMilliseconds + 1U,
                "widened owner");
        },
        "reviewed ceiling",
        "wait authority cannot exceed reviewed ceiling",
        checks);
    expect(database.active_borrows() == 0U,
           "policy rejection releases the transferred generation",
           checks);

    {
        SqliteBusyHandlerOwner owner(
            database.busy_borrow("maximum-owner generation"),
            kMaximumSqliteBusyHandlerWaitMilliseconds,
            "maximum owner");
        expect(database.active_borrows() == 1U,
               "live busy owner pins exactly one database generation",
               checks);
        const SqliteBusyHandlerSnapshot snapshot = owner.snapshot();
        expect(snapshot.invocations == 0U &&
                   snapshot.authorized_sleep_milliseconds == 0U &&
                   snapshot.sleep_milliseconds == 0U &&
                   !snapshot.contention_observed &&
                   !snapshot.timeout_exhausted,
               "maximum reviewed policy begins empty",
               checks);
    }
    expect(database.active_borrows() == 0U,
           "owner destruction releases its exact generation",
           checks);
}

void test_singleton_claim_and_explicit_reuse(int& checks) {
    TemporaryDatabasePath temporary;
    Database database(temporary.get());
    {
        SqliteBusyHandlerOwner first(
            database.busy_borrow("first-owner generation"),
            10U,
            "first owner");
        expect(database.active_borrows() == 1U,
               "singleton owner retains one generation",
               checks);
        expect_exception<std::logic_error>(
            [&] {
                SqliteBusyHandlerOwner duplicate(
                    database.busy_borrow("duplicate-owner generation"),
                    10U,
                    "duplicate owner");
            },
            "already has an AnonSync SQLite busy-handler owner",
            "second owner cannot silently replace retained context",
            checks);
        expect(database.active_borrows() == 1U,
               "failed duplicate construction releases only its own generation",
               checks);

        first.detach();
        expect(database.active_borrows() == 0U,
               "explicit detach releases the singleton generation",
               checks);
        first.detach();
        SqliteBusyHandlerOwner replacement(
            database.busy_borrow("replacement-owner generation"),
            10U,
            "replacement owner");
        expect(database.active_borrows() == 1U,
               "replacement pins a fresh generation borrow",
               checks);
        expect(!replacement.contention_observed(),
               "explicit detach releases singleton claim for reuse",
               checks);
    }
    expect(database.active_borrows() == 0U,
           "replacement destruction releases its generation",
           checks);

    SqliteBusyHandlerOwner after_destruction(
        database.busy_borrow("post-destruction generation"),
        10U,
        "post-destruction owner");
    expect(after_destruction.snapshot().invocations == 0U,
           "destruction detaches before owner storage expires",
           checks);
}

void test_concurrent_duplicate_owners_reject_without_fail_stop(int& checks) {
    TemporaryDatabasePath temporary;
    Database database(temporary.get());

    constexpr int kIterations = 64;
    int successful_attachments = 0;
    int duplicate_rejections = 0;
    for (int iteration = 0; iteration < kIterations; ++iteration) {
        std::array<SyncSqliteSerializedDbBorrow, 2> borrows{
            database.busy_borrow("concurrent duplicate generation A"),
            database.busy_borrow("concurrent duplicate generation B")};
        std::array<std::exception_ptr, 2> errors;
        std::array<std::atomic<int>, 2> outcomes;
        for (auto& outcome : outcomes) {
            outcome.store(0, std::memory_order_relaxed);
        }
        std::atomic<int> ready{0};
        std::atomic<int> finished{0};
        std::atomic<bool> start{false};
        std::atomic<bool> release{false};
        std::array<std::thread, 2> threads;

        for (std::size_t index = 0; index < threads.size(); ++index) {
            threads[index] = std::thread(
                [&, index, borrow = std::move(borrows[index])]() mutable {
                    ready.fetch_add(1, std::memory_order_release);
                    while (!start.load(std::memory_order_acquire)) {
                        std::this_thread::yield();
                    }

                    std::unique_ptr<SqliteBusyHandlerOwner> owner;
                    try {
                        owner = std::make_unique<SqliteBusyHandlerOwner>(
                            std::move(borrow),
                            10U,
                            "concurrent duplicate busy owner");
                        outcomes[index].store(1, std::memory_order_release);
                    } catch (const std::logic_error& error) {
                        if (std::string(error.what()).find(
                                "already has an AnonSync SQLite busy-handler owner") !=
                            std::string::npos) {
                            outcomes[index].store(2, std::memory_order_release);
                        } else {
                            errors[index] = std::current_exception();
                            outcomes[index].store(3, std::memory_order_release);
                        }
                    } catch (...) {
                        errors[index] = std::current_exception();
                        outcomes[index].store(3, std::memory_order_release);
                    }

                    finished.fetch_add(1, std::memory_order_release);
                    while (!release.load(std::memory_order_acquire)) {
                        std::this_thread::yield();
                    }
                    if (owner) owner->detach();
                });
        }

        while (ready.load(std::memory_order_acquire) != 2) {
            std::this_thread::yield();
        }
        start.store(true, std::memory_order_release);
        while (finished.load(std::memory_order_acquire) != 2) {
            std::this_thread::yield();
        }

        int iteration_successes = 0;
        int iteration_rejections = 0;
        for (const auto& outcome : outcomes) {
            const int value = outcome.load(std::memory_order_acquire);
            iteration_successes += value == 1 ? 1 : 0;
            iteration_rejections += value == 2 ? 1 : 0;
        }
        successful_attachments += iteration_successes;
        duplicate_rejections += iteration_rejections;

        release.store(true, std::memory_order_release);
        for (auto& thread : threads) thread.join();
        for (const auto& error : errors) {
            if (error) std::rethrow_exception(error);
        }
        if (iteration_successes != 1 || iteration_rejections != 1) {
            throw std::runtime_error(
                "concurrent duplicate busy-owner outcome mismatch at iteration " +
                std::to_string(iteration));
        }
        if (database.active_borrows() != 0U) {
            throw std::runtime_error(
                "concurrent duplicate busy-owner generation leak at iteration " +
                std::to_string(iteration));
        }
    }

    expect(successful_attachments == kIterations &&
               duplicate_rejections == kIterations,
           "every concurrent duplicate race has one live owner and one recoverable rejection",
           checks);
    expect(database.active_borrows() == 0U,
           "concurrent duplicate corpus releases every exact generation",
           checks);
}

void test_zero_timeout_fail_fast(int& checks) {
    TemporaryDatabasePath temporary;
    Database writer(temporary.get());
    Database contender(temporary.get());
    configure_lock_fixture(writer.get());
    execute_or_throw(writer.get(), "BEGIN IMMEDIATE;", "writer lock");

    {
        SqliteBusyHandlerOwner owner(
            contender.busy_borrow("zero-timeout generation"),
            0U,
            "zero-timeout contender");
        const int result = execute_result(contender.get(), "BEGIN IMMEDIATE;");
        const SqliteBusyHandlerSnapshot snapshot = owner.snapshot();
        expect(result == SQLITE_BUSY,
               "zero-timeout contender returns SQLITE_BUSY",
               checks);
        expect(snapshot.contention_observed && snapshot.invocations >= 1U,
               "zero-timeout callback records contention",
               checks);
        expect(snapshot.timeout_exhausted,
               "zero-timeout callback records exhausted authority",
               checks);
        expect(snapshot.authorized_sleep_milliseconds == 0U,
               "zero-timeout callback consumes no sleep authority",
               checks);
        expect(snapshot.sleep_milliseconds == 0U,
               "zero-timeout callback does not sleep",
               checks);
    }

    execute_or_throw(writer.get(), "ROLLBACK;", "writer unlock");
}

void test_owner_lifetime_sleep_authority_does_not_reset(int& checks) {
    TemporaryDatabasePath temporary;
    Database writer(temporary.get());
    Database contender(temporary.get());
    configure_lock_fixture(writer.get());
    execute_or_throw(
        writer.get(), "BEGIN IMMEDIATE;", "lifetime-budget writer lock");

    SqliteBusyHandlerOwner owner(
        contender.busy_borrow("lifetime-budget generation"),
        3U,
        "lifetime-budget contender");
    const int first_result =
        execute_result(contender.get(), "BEGIN IMMEDIATE;");
    const SqliteBusyHandlerSnapshot first = owner.snapshot();
    expect(first_result == SQLITE_BUSY && first.timeout_exhausted,
           "first locking event exhausts its finite owner-lifetime authority",
           checks);
    expect(first.authorized_sleep_milliseconds == 3U,
           "first locking event consumes the exact cumulative sleep authority",
           checks);
    expect(first.invocations >= 2U && first.sleep_milliseconds >= 3U,
           "first locking event records progressive callback and sleep evidence",
           checks);

    const int second_result =
        execute_result(contender.get(), "BEGIN IMMEDIATE;");
    const SqliteBusyHandlerSnapshot second = owner.snapshot();
    expect(second_result == SQLITE_BUSY &&
               second.invocations == first.invocations + 1U &&
               second.timeout_exhausted,
           "later locking event receives only one fail-fast callback",
           checks);
    expect(second.authorized_sleep_milliseconds ==
                   first.authorized_sleep_milliseconds &&
               second.sleep_milliseconds == first.sleep_milliseconds,
           "later locking event cannot renew consumed sleep authority",
           checks);
    expect(second.contention_observed && second.timeout_exhausted,
           "lifetime exhaustion remains sticky across locking events",
           checks);

    execute_or_throw(
        writer.get(), "ROLLBACK;", "lifetime-budget writer unlock");
}

void test_alternate_timeout_setter_is_fenced(int& checks) {
    TemporaryDatabasePath temporary;
    Database writer(temporary.get());
    Database contender(temporary.get());
    configure_lock_fixture(writer.get());
    execute_or_throw(
        writer.get(), "BEGIN IMMEDIATE;", "alternate-setter writer lock");

    SqliteBusyHandlerOwner owner(
        contender.busy_borrow("alternate-setter generation"),
        0U,
        "alternate-setter owner");
    expect_exception<std::logic_error>(
        [&] {
            anonsync::sqlite_set_busy_timeout_or_throw(
                contender.get(), 5'000, "hostile alternate busy setter");
        },
        "cannot replace a live AnonSync SQLite busy-handler owner",
        "busy-timeout gateway rejects replacement of retained callback",
        checks);

    const int result = execute_result(contender.get(), "BEGIN IMMEDIATE;");
    const SqliteBusyHandlerSnapshot snapshot = owner.snapshot();
    expect(result == SQLITE_BUSY && snapshot.contention_observed &&
               snapshot.timeout_exhausted && snapshot.invocations >= 1U,
           "rejected alternate setter leaves the bounded owner callable",
           checks);

    owner.detach();
    expect(contender.active_borrows() == 0U,
           "alternate-setter fixture releases the exact owner generation",
           checks);
    anonsync::sqlite_set_busy_timeout_or_throw(
        contender.get(), 1, "post-detach busy timeout");
    expect(sqlite3_get_clientdata(
               contender.get(),
               anonsync::persistence::kSqliteBusyHandlerOwnerClientDataName) ==
               nullptr,
           "ordinary timeout configuration does not mint an owner claim",
           checks);

    execute_or_throw(writer.get(), "ROLLBACK;", "alternate-setter writer unlock");
}

void test_concurrent_alternate_setter_cannot_supersede_claim(int& checks) {
    TemporaryDatabasePath temporary;
    Database writer(temporary.get());
    Database contender(temporary.get());
    configure_lock_fixture(writer.get());
    execute_or_throw(
        writer.get(), "BEGIN IMMEDIATE;", "concurrent-setter writer lock");

    constexpr int kIterations = 64;
    int gateway_succeeded = 0;
    int gateway_rejected = 0;
    for (int iteration = 0; iteration < kIterations; ++iteration) {
        SyncSqliteSerializedDbBorrow owner_borrow = contender.busy_borrow(
            "concurrent alternate-setter owner generation");
        std::unique_ptr<SqliteBusyHandlerOwner> owner;
        std::exception_ptr owner_error;
        std::exception_ptr gateway_error;
        std::atomic<int> ready{0};
        std::atomic<bool> start{false};

        auto await_start = [&] {
            ready.fetch_add(1, std::memory_order_release);
            while (!start.load(std::memory_order_acquire)) {
                std::this_thread::yield();
            }
        };
        std::thread owner_thread(
            [&, borrow = std::move(owner_borrow)]() mutable {
                await_start();
                try {
                    owner = std::make_unique<SqliteBusyHandlerOwner>(
                        std::move(borrow),
                        0U,
                        "concurrent alternate-setter owner");
                } catch (...) {
                    owner_error = std::current_exception();
                }
            });
        std::thread gateway_thread([&] {
            await_start();
            try {
                anonsync::sqlite_set_busy_timeout_or_throw(
                    contender.get(), 1, "concurrent alternate busy setter");
                ++gateway_succeeded;
            } catch (const std::logic_error& error) {
                if (std::string(error.what()).find(
                        "cannot replace a live AnonSync SQLite busy-handler owner") ==
                    std::string::npos) {
                    gateway_error = std::current_exception();
                } else {
                    ++gateway_rejected;
                }
            } catch (...) {
                gateway_error = std::current_exception();
            }
        });

        while (ready.load(std::memory_order_acquire) != 2) {
            std::this_thread::yield();
        }
        start.store(true, std::memory_order_release);
        owner_thread.join();
        gateway_thread.join();
        if (owner_error) std::rethrow_exception(owner_error);
        if (gateway_error) std::rethrow_exception(gateway_error);
        if (!owner) {
            throw std::runtime_error(
                "concurrent alternate-setter race did not retain an owner");
        }

        const int result = execute_result(contender.get(), "BEGIN IMMEDIATE;");
        const SqliteBusyHandlerSnapshot snapshot = owner->snapshot();
        if (result != SQLITE_BUSY || !snapshot.contention_observed ||
            !snapshot.timeout_exhausted || snapshot.invocations == 0U) {
            throw std::runtime_error(
                "concurrent alternate setter superseded the owner at iteration " +
                std::to_string(iteration));
        }
        owner->detach();
        owner.reset();
    }

    expect(gateway_succeeded + gateway_rejected == kIterations,
           "every alternate-setter race has one classified gateway outcome",
           checks);
    expect(contender.active_borrows() == 0U,
           "concurrent alternate-setter corpus releases every generation",
           checks);
    execute_or_throw(writer.get(), "ROLLBACK;", "concurrent-setter writer unlock");
}

void test_cross_thread_handoff_and_atomic_snapshot(int& checks) {
    TemporaryDatabasePath temporary;
    Database writer(temporary.get());
    Database contender(temporary.get());
    configure_lock_fixture(writer.get());
    execute_or_throw(writer.get(), "BEGIN IMMEDIATE;", "handoff writer lock");

    SqliteBusyHandlerOwner owner(
        contender.busy_borrow("cross-thread generation"),
        5'000U,
        "cross-thread contender");
    std::atomic<int> worker_result{SQLITE_ERROR};
    std::thread worker([&] {
        worker_result.store(
            execute_result(contender.get(), "BEGIN IMMEDIATE;"),
            std::memory_order_release);
    });

    const auto deadline = std::chrono::steady_clock::now() + 5s;
    while (!owner.contention_observed() &&
           std::chrono::steady_clock::now() < deadline) {
        std::this_thread::sleep_for(1ms);
    }
    expect(owner.contention_observed(),
           "main thread observes callback running on handed-off connection",
           checks);

    const SqliteBusyHandlerSnapshot concurrent_snapshot = owner.snapshot();
    expect(concurrent_snapshot.contention_observed &&
               concurrent_snapshot.invocations >= 1U,
           "atomic snapshot is readable while foreign-thread callback waits",
           checks);

    std::optional<SqliteBusyHandlerSnapshot> observer_snapshot;
    std::thread observer([&] { observer_snapshot = owner.snapshot(); });
    observer.join();
    expect(observer_snapshot.has_value() &&
               observer_snapshot->contention_observed &&
               observer_snapshot->invocations >= 1U,
           "third thread may observe intentionally shared callback state",
           checks);

    execute_or_throw(writer.get(), "ROLLBACK;", "handoff writer release");
    worker.join();
    expect(worker_result.load(std::memory_order_acquire) == SQLITE_OK,
           "writer handoff succeeds before bounded timeout",
           checks);
    execute_or_throw(contender.get(), "ROLLBACK;", "handoff contender rollback");

    const SqliteBusyHandlerSnapshot final_snapshot = owner.snapshot();
    expect(final_snapshot.invocations >= concurrent_snapshot.invocations &&
               final_snapshot.authorized_sleep_milliseconds >=
                   concurrent_snapshot.authorized_sleep_milliseconds &&
               final_snapshot.sleep_milliseconds >=
                   concurrent_snapshot.sleep_milliseconds &&
               final_snapshot.contention_observed &&
               !final_snapshot.timeout_exhausted,
           "quiescent snapshot monotonically contains concurrent evidence",
           checks);

    std::thread detacher([&] { owner.detach(); });
    detacher.join();
    SqliteBusyHandlerOwner replacement(
        contender.busy_borrow("cross-thread replacement generation"),
        10U,
        "cross-thread detach replacement");
    expect(replacement.snapshot().invocations == 0U,
           "quiescent foreign-thread detach clears handler and client-data claim",
           checks);
}

void test_commit_phase_contention_is_observable(int& checks) {
    TemporaryDatabasePath temporary;
    Database writer(temporary.get());
    Database reader(temporary.get());
    configure_lock_fixture(writer.get());
    execute_or_throw(
        reader.get(),
        "BEGIN; SELECT COUNT(*) FROM evidence;",
        "commit-contention reader snapshot");

    SqliteBusyHandlerOwner owner(
        writer.busy_borrow("commit-contention generation"),
        2'000U,
        "commit-contention writer");
    execute_or_throw(writer.get(),
                     "BEGIN IMMEDIATE; INSERT INTO evidence(value) VALUES(1);",
                     "commit-contention writer mutation");

    std::atomic<bool> releaser_saw_contention{false};
    std::exception_ptr releaser_error;
    std::thread releaser([&] {
        try {
            const auto deadline = std::chrono::steady_clock::now() + 1s;
            while (!owner.contention_observed() &&
                   std::chrono::steady_clock::now() < deadline) {
                std::this_thread::sleep_for(1ms);
            }
            releaser_saw_contention.store(
                owner.contention_observed(), std::memory_order_release);
            execute_or_throw(reader.get(),
                             "ROLLBACK;",
                             "commit-contention reader release");
        } catch (...) {
            releaser_error = std::current_exception();
        }
    });

    const int commit_result = execute_result(writer.get(), "COMMIT;");
    releaser.join();
    if (releaser_error) std::rethrow_exception(releaser_error);
    if (commit_result != SQLITE_OK) {
        (void)execute_result(writer.get(), "ROLLBACK;");
    }

    const SqliteBusyHandlerSnapshot snapshot = owner.snapshot();
    expect(commit_result == SQLITE_OK,
           "reader release lets the blocked COMMIT finish",
           checks);
    expect(releaser_saw_contention.load(std::memory_order_acquire) &&
               snapshot.contention_observed && snapshot.invocations >= 1U,
           "COMMIT-phase lock upgrade publishes callback evidence",
           checks);
    expect(snapshot.sleep_milliseconds >= 1U &&
               !snapshot.timeout_exhausted,
           "successful COMMIT wait records bounded sleep without exhaustion",
           checks);
}

}  // namespace

int main() {
    int checks = 0;
    try {
        test_type_and_constructor_contract(checks);
        test_singleton_claim_and_explicit_reuse(checks);
        test_concurrent_duplicate_owners_reject_without_fail_stop(checks);
        test_zero_timeout_fail_fast(checks);
        test_owner_lifetime_sleep_authority_does_not_reset(checks);
        test_alternate_timeout_setter_is_fenced(checks);
        test_concurrent_alternate_setter_cannot_supersede_claim(checks);
        test_cross_thread_handoff_and_atomic_snapshot(checks);
        test_commit_phase_contention_is_observable(checks);
        std::cout << "sqlite busy-handler owner tests passed: " << checks
                  << " checks\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sqlite busy-handler owner tests failed after " << checks
                  << " checks: " << error.what() << "\n";
        return 1;
    }
}
