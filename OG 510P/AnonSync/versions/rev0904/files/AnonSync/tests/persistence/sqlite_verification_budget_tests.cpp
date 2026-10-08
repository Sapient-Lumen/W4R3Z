#include "inherited_test_process.hpp"
#include "sqlite_retained_callback_claim.hpp"
#include "sqlite_verification_budget.hpp"
#include "sync_sqlite_handle_slot.hpp"
#include "sync_process_incarnation.hpp"

#include <sqlite3.h>

#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <exception>
#include <functional>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <type_traits>

namespace {

using anonsync::persistence::SqliteRetainedCallbackClaim;
using anonsync::persistence::SqliteVerificationBudget;
using anonsync::persistence::SqliteVerificationBudgetException;
using anonsync::persistence::SqliteVerificationBudgetFailure;
using anonsync::persistence::SqliteVerificationBudgetPolicy;
using anonsync::persistence::kMaximumSqliteVerificationDecodedTextBytes;
using anonsync::persistence::kMaximumSqliteVerificationElapsedMilliseconds;
using anonsync::persistence::kMaximumSqliteVerificationProgressCallbacks;
using anonsync::persistence::kMaximumSqliteVerificationProgressOpcodeInterval;
using anonsync::persistence::kMaximumSqliteVerificationRetainedTextBytes;
using anonsync::persistence::kMaximumSqliteVerificationRows;
using anonsync::persistence::sqlite_verification_budget_for_snapshot;
using anonsync::persistence::sqlite_verification_budget_failure_name;
using anonsync::SyncSqliteDatabaseMutexGuard;
using anonsync::SyncSqliteDbHandleSlot;
using anonsync::SyncSqliteSerializedDbBorrow;
using anonsync::borrow_sync_sqlite_serialized_db_or_throw;
using anonsync::kSyncProcessCapabilityViolationExitCode;
using anonsync::test::spawn_inherited_test_process_or_throw;

class Database final {
public:
    explicit Database(
        int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                    SQLITE_OPEN_FULLMUTEX) {
        int result = SQLITE_ERROR;
        std::string message;
        {
            auto output = owner_.out();
            result = sqlite3_open_v2(":memory:", output.get(), flags, nullptr);
            if (result != SQLITE_OK) {
                sqlite3* const database = *output.get();
                message = database == nullptr ? "SQLite memory open failed"
                                              : sqlite3_errmsg(database);
            }
        }
        if (result != SQLITE_OK) {
            owner_.reset();
            throw std::runtime_error(message);
        }
    }

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    [[nodiscard]] sqlite3* get() const noexcept { return owner_.get(); }
    [[nodiscard]] SyncSqliteSerializedDbBorrow serialized_borrow(
        const std::string& label = "verification budget test database") const {
        return borrow_sync_sqlite_serialized_db_or_throw(owner_, label);
    }
    [[nodiscard]] std::size_t active_borrows() const noexcept {
        return owner_.active_borrows();
    }
    [[nodiscard]] std::uint64_t generation() const noexcept {
        return owner_.generation();
    }
    void reset() noexcept { owner_.reset(); }

private:
    SyncSqliteDbHandleSlot owner_;
};

void expect(bool condition, const std::string& label, int& checks) {
    ++checks;
    if (!condition) throw std::runtime_error("check failed: " + label);
}

template <typename Fn>
void expect_runtime_error(Fn&& fn,
                          const std::string& fragment,
                          const std::string& label,
                          int& checks) {
    bool caught = false;
    try {
        fn();
    } catch (const std::runtime_error& error) {
        caught = std::string(error.what()).find(fragment) != std::string::npos;
    }
    expect(caught, label, checks);
}

template <typename Fn>
void expect_exception(Fn&& fn,
                      const std::string& fragment,
                      const std::string& label,
                      int& checks) {
    bool caught = false;
    try {
        fn();
    } catch (const std::exception& error) {
        caught = std::string(error.what()).find(fragment) != std::string::npos;
    }
    expect(caught, label, checks);
}

template <typename Fn>
void expect_budget_failure(Fn&& fn,
                           SqliteVerificationBudgetFailure expected_failure,
                           std::uint64_t expected_observed,
                           std::uint64_t expected_limit,
                           const std::string& label,
                           int& checks) {
    bool caught = false;
    try {
        fn();
    } catch (const SqliteVerificationBudgetException& error) {
        caught = error.failure() == expected_failure &&
                 error.observed() == expected_observed &&
                 error.limit() == expected_limit;
    }
    expect(caught, label, checks);
}

void test_type_and_failure_contract(int& checks) {
    static_assert(!std::is_copy_constructible_v<SqliteVerificationBudget>);
    static_assert(!std::is_copy_assignable_v<SqliteVerificationBudget>);
    static_assert(!std::is_move_constructible_v<SqliteVerificationBudget>);
    static_assert(!std::is_move_assignable_v<SqliteVerificationBudget>);
    expect(true, "budget owner is noncopyable and nonmovable", checks);

    expect(sqlite_verification_budget_failure_name(
               SqliteVerificationBudgetFailure::none) == "none",
           "none name", checks);
    expect(sqlite_verification_budget_failure_name(
               SqliteVerificationBudgetFailure::progress_callback_limit) ==
               "progress_callback_limit",
           "progress name", checks);
    expect(sqlite_verification_budget_failure_name(
               SqliteVerificationBudgetFailure::elapsed_time_limit) ==
               "elapsed_time_limit",
           "elapsed name", checks);
    expect(sqlite_verification_budget_failure_name(
               SqliteVerificationBudgetFailure::row_limit) == "row_limit",
           "row name", checks);
    expect(sqlite_verification_budget_failure_name(
               SqliteVerificationBudgetFailure::decoded_text_byte_limit) ==
               "decoded_text_byte_limit",
           "decoded name", checks);
    expect(sqlite_verification_budget_failure_name(
               SqliteVerificationBudgetFailure::retained_text_byte_limit) ==
               "retained_text_byte_limit",
           "retained name", checks);
}

void test_constructor_and_monotone_policy(int& checks) {
    Database database;
    expect_runtime_error(
        [&] { SqliteVerificationBudget budget(SyncSqliteSerializedDbBorrow{}, "null"); },
        "requires an exact serialized database-generation borrow",
        "null database rejected", checks);
    expect_runtime_error(
        [&] { SqliteVerificationBudget budget(database.serialized_borrow(), ""); },
        "requires a nonempty diagnostic label", "empty label rejected", checks);

    const auto zero_cases = {
        std::function<void(SqliteVerificationBudgetPolicy&)>(
            [](auto& p) { p.maximum_progress_callbacks = 0U; }),
        std::function<void(SqliteVerificationBudgetPolicy&)>(
            [](auto& p) { p.progress_opcode_interval = 0U; }),
        std::function<void(SqliteVerificationBudgetPolicy&)>(
            [](auto& p) { p.maximum_rows = 0U; }),
        std::function<void(SqliteVerificationBudgetPolicy&)>(
            [](auto& p) { p.maximum_decoded_text_bytes = 0U; }),
        std::function<void(SqliteVerificationBudgetPolicy&)>(
            [](auto& p) { p.maximum_retained_text_bytes = 0U; }),
        std::function<void(SqliteVerificationBudgetPolicy&)>(
            [](auto& p) { p.maximum_elapsed_milliseconds = 0U; }),
    };
    for (const auto& mutate : zero_cases) {
        SqliteVerificationBudgetPolicy policy;
        mutate(policy);
        expect_runtime_error(
            [&] { SqliteVerificationBudget budget(database.serialized_borrow(), "zero", policy); },
            "zero ceiling", "zero policy dimension rejected", checks);
    }

    const auto widen_cases = {
        std::function<void(SqliteVerificationBudgetPolicy&)>([](auto& p) {
            p.maximum_progress_callbacks =
                kMaximumSqliteVerificationProgressCallbacks + 1U;
        }),
        std::function<void(SqliteVerificationBudgetPolicy&)>([](auto& p) {
            p.progress_opcode_interval =
                kMaximumSqliteVerificationProgressOpcodeInterval + 1U;
        }),
        std::function<void(SqliteVerificationBudgetPolicy&)>([](auto& p) {
            p.maximum_rows = kMaximumSqliteVerificationRows + 1U;
        }),
        std::function<void(SqliteVerificationBudgetPolicy&)>([](auto& p) {
            p.maximum_decoded_text_bytes =
                kMaximumSqliteVerificationDecodedTextBytes + 1U;
        }),
        std::function<void(SqliteVerificationBudgetPolicy&)>([](auto& p) {
            p.maximum_retained_text_bytes =
                kMaximumSqliteVerificationRetainedTextBytes + 1U;
        }),
        std::function<void(SqliteVerificationBudgetPolicy&)>([](auto& p) {
            p.maximum_elapsed_milliseconds =
                kMaximumSqliteVerificationElapsedMilliseconds + 1U;
        }),
    };
    for (const auto& mutate : widen_cases) {
        SqliteVerificationBudgetPolicy policy;
        mutate(policy);
        expect_runtime_error(
            [&] { SqliteVerificationBudget budget(database.serialized_borrow(), "widen", policy); },
            "may tighten but not widen", "widened policy rejected", checks);
    }

    SqliteVerificationBudgetPolicy tight;
    tight.maximum_progress_callbacks = 10U;
    tight.progress_opcode_interval = 1U;
    tight.maximum_rows = 10U;
    tight.maximum_decoded_text_bytes = 10U;
    tight.maximum_retained_text_bytes = 10U;
    tight.maximum_elapsed_milliseconds = 10U;
    {
        SqliteVerificationBudget budget(database.serialized_borrow(), "tight policy", tight);
        expect(!budget.exhausted(), "tight policy accepted", checks);
    }
}

void test_shared_claim_input_and_reuse_contract(int& checks) {
    static_assert(!std::is_copy_constructible_v<SqliteRetainedCallbackClaim>);
    static_assert(!std::is_move_constructible_v<SqliteRetainedCallbackClaim>);
    expect(true, "shared claim is one nontransferable lifetime authority", checks);

    Database database;
    SyncSqliteDatabaseMutexGuard claim_guard(
        database.get(), "shared claim exact database guard");
    SqliteRetainedCallbackClaim claim;
    expect(!claim.attached(), "new shared claim is detached", checks);
    expect_exception(
        [&] { claim.attach(nullptr, claim_guard, "claim.null", "claim", "test owner"); },
        "requires an open database handle", "shared claim rejects null database",
        checks);
    expect_exception(
        [&] { claim.attach(database.get(), claim_guard, "", "claim", "test owner"); },
        "nonempty NUL-free name", "shared claim rejects empty name", checks);
    const std::string nul_name("claim\0alias", 11U);
    expect_exception(
        [&] { claim.attach(database.get(), claim_guard, nul_name, "claim", "test owner"); },
        "nonempty NUL-free name", "shared claim rejects NUL alias", checks);
    expect_exception(
        [&] { claim.attach(database.get(), claim_guard, "claim.owner", "claim", ""); },
        "nonempty NUL-free name", "shared claim rejects empty owner identity",
        checks);
    {
        Database other_database;
        SyncSqliteDatabaseMutexGuard other_guard(
            other_database.get(), "shared claim mismatched database guard");
        expect_exception(
            [&] {
                claim.attach(database.get(),
                             other_guard,
                             "claim.mismatched-guard",
                             "claim",
                             "test owner");
            },
            "exact serialized database-mutex guard",
            "shared claim rejects a guard for another database",
            checks);
    }
    expect(!claim.attached(), "invalid input leaves no partial claim", checks);

    std::string mutable_name = "anonsync.test.shared-claim.v1";
    const std::string frozen_name = mutable_name;
    claim.attach(database.get(), claim_guard, mutable_name, "shared claim", "test owner");
    expect(claim.attached(), "shared claim publishes attached state", checks);
    void* const published = sqlite3_get_clientdata(
        database.get(), frozen_name.c_str());
    expect(published != nullptr, "shared claim publishes exact named sentinel",
           checks);
    mutable_name.assign("redirected.after.attach");
    expect(sqlite3_get_clientdata(database.get(), frozen_name.c_str()) ==
               published,
           "shared claim freezes caller-owned name", checks);
    expect_exception(
        [&] {
            claim.attach(database.get(), claim_guard, "claim.duplicate", "shared claim",
                         "test owner");
        },
        "already attached", "shared claim rejects duplicate attachment", checks);
    claim.require_live(database.get(), claim_guard);
    expect(claim.attached(), "shared claim revalidates exact live sentinel", checks);
    claim.detach(database.get(), claim_guard);
    expect(sqlite3_get_clientdata(database.get(), frozen_name.c_str()) == nullptr,
           "shared claim synchronously clears named sentinel", checks);
    expect(!claim.attached(), "shared claim clears local attachment", checks);
    claim.detach(database.get(), claim_guard);
    expect(!claim.attached(), "shared claim detach is idempotent", checks);

    claim.attach(database.get(), claim_guard, frozen_name, "shared claim reuse", "test owner");
    expect(claim.attached(), "detached shared claim can be reused", checks);
    claim.detach(database.get(), claim_guard);
    expect(!claim.attached(), "reused shared claim detaches cleanly", checks);

    static int occupied_slot = 0;
    expect(sqlite3_set_clientdata(database.get(), "anonsync.test.occupied.v1",
                                  &occupied_slot, nullptr) == SQLITE_OK,
           "test publishes independently occupied named slot", checks);
    expect_exception(
        [&] {
            claim.attach(database.get(), claim_guard, "anonsync.test.occupied.v1",
                         "occupied claim", "test owner");
        },
        "already has", "shared claim rejects occupied named slot", checks);
    expect(sqlite3_get_clientdata(database.get(),
                                  "anonsync.test.occupied.v1") == &occupied_slot,
           "occupied rejection preserves prior slot owner", checks);
    expect(sqlite3_set_clientdata(database.get(), "anonsync.test.occupied.v1",
                                  nullptr, nullptr) == SQLITE_OK,
           "test clears independently occupied named slot", checks);
}

void test_exact_generation_and_singleton_claim(int& checks) {
    static constexpr const char* kClaimName =
        "anonsync.sqlite-verification-budget.v1";
    Database database;
    const std::uint64_t generation = database.generation();
    expect(generation != 0U, "typed database owner mints a generation", checks);
    expect(database.active_borrows() == 0U,
           "typed database starts without active borrows", checks);

    SqliteVerificationBudget budget(
        database.serialized_borrow("verification singleton generation"),
        "verification singleton");
    expect(database.active_borrows() == 1U,
           "verification owner pins one exact generation", checks);
    expect(sqlite3_get_clientdata(database.get(), kClaimName) != nullptr,
           "verification owner publishes shared named claim", checks);
    expect_exception(
        [&] {
            SqliteVerificationBudget duplicate(
                database.serialized_borrow("duplicate verification generation"),
                "duplicate verification");
        },
        "already has", "singleton progress owner rejects duplicate claim", checks);
    expect(database.active_borrows() == 1U,
           "rejected duplicate releases its temporary generation borrow", checks);
    expect(!budget.safe_summary().empty(),
           "live singleton retains value-free diagnostics", checks);
    budget.detach();
    expect(database.active_borrows() == 0U,
           "ordered detach releases exact generation", checks);
    expect(sqlite3_get_clientdata(database.get(), kClaimName) == nullptr,
           "ordered detach clears shared named claim", checks);
    expect(database.generation() == generation,
           "detach does not mutate owner generation", checks);
    budget.detach();
    expect(database.active_borrows() == 0U,
           "verification detach is idempotent", checks);

    Database unserialized(SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                          SQLITE_OPEN_NOMUTEX);
    expect_exception(
        [&] {
            SqliteVerificationBudget rejected(
                unserialized.serialized_borrow("NOMUTEX verification"),
                "NOMUTEX verification");
        },
        "serialized/FULLMUTEX", "verification owner rejects NOMUTEX generation",
        checks);
}

void test_concurrent_duplicate_budgets_reject_without_fail_stop(
    int& checks) {
    static constexpr const char* kClaimName =
        "anonsync.sqlite-verification-budget.v1";
    Database database;

    constexpr int kIterations = 64;
    int successful_attachments = 0;
    int duplicate_rejections = 0;
    for (int iteration = 0; iteration < kIterations; ++iteration) {
        std::array<SyncSqliteSerializedDbBorrow, 2> borrows{
            database.serialized_borrow("concurrent verification generation A"),
            database.serialized_borrow("concurrent verification generation B")};
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

                    std::unique_ptr<SqliteVerificationBudget> budget;
                    try {
                        budget = std::make_unique<SqliteVerificationBudget>(
                            std::move(borrow),
                            "concurrent duplicate verification budget");
                        outcomes[index].store(1, std::memory_order_release);
                    } catch (const std::logic_error& error) {
                        if (std::string(error.what()).find(
                                "already has an AnonSync SQLite verification-budget owner") !=
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
                    if (budget) budget->detach();
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
        const bool claim_is_live =
            sqlite3_get_clientdata(database.get(), kClaimName) != nullptr;

        release.store(true, std::memory_order_release);
        for (auto& thread : threads) thread.join();
        for (const auto& error : errors) {
            if (error) std::rethrow_exception(error);
        }
        if (iteration_successes != 1 || iteration_rejections != 1 ||
            !claim_is_live) {
            throw std::runtime_error(
                "concurrent duplicate verification outcome mismatch at iteration " +
                std::to_string(iteration));
        }
        if (database.active_borrows() != 0U ||
            sqlite3_get_clientdata(database.get(), kClaimName) != nullptr) {
            throw std::runtime_error(
                "concurrent duplicate verification teardown mismatch at iteration " +
                std::to_string(iteration));
        }
    }

    expect(successful_attachments == kIterations &&
               duplicate_rejections == kIterations,
           "every concurrent verification race has one live owner and one recoverable rejection",
           checks);
    expect(database.active_borrows() == 0U,
           "concurrent verification corpus releases every exact generation",
           checks);
}

enum class CallbackLifetimeViolationProbe : std::uint8_t {
    immediate_close_v2_destruction,
    deferred_close_v2_destruction,
    named_claim_replacement,
    typed_owner_reset,
};

void require_callback_lifetime_fail_stop(
    CallbackLifetimeViolationProbe probe,
    const std::string& label,
    int& checks) {
    auto process = spawn_inherited_test_process_or_throw(
        [probe]() -> int {
            auto* database = new Database();
            auto* budget = new SqliteVerificationBudget(
                database->serialized_borrow("lifetime probe generation"),
                "lifetime probe");
            (void)budget;
            sqlite3* const raw = database->get();
            switch (probe) {
                case CallbackLifetimeViolationProbe::immediate_close_v2_destruction:
                    (void)sqlite3_close_v2(raw);
                    std::_Exit(131);
                case CallbackLifetimeViolationProbe::deferred_close_v2_destruction: {
                    sqlite3_stmt* statement = nullptr;
                    if (sqlite3_prepare_v2(raw, "SELECT 1;", -1, &statement,
                                           nullptr) != SQLITE_OK) {
                        std::_Exit(132);
                    }
                    if (sqlite3_close_v2(raw) != SQLITE_OK) std::_Exit(133);
                    // close_v2 has returned and the typed owner now names a
                    // zombie connection. Finalizing its last dependent causes
                    // actual SQLite destruction and must trip the live claim.
                    (void)sqlite3_finalize(statement);
                    std::_Exit(134);
                }
                case CallbackLifetimeViolationProbe::named_claim_replacement:
                    (void)sqlite3_set_clientdata(
                        raw, "anonsync.sqlite-verification-budget.v1",
                        nullptr, nullptr);
                    std::_Exit(135);
                case CallbackLifetimeViolationProbe::typed_owner_reset:
                    database->reset();
                    std::_Exit(136);
            }
            std::_Exit(137);
        },
        label);
    process.wait_for_exact_exit(kSyncProcessCapabilityViolationExitCode,
                                std::chrono::seconds(10), label);
    expect(true, label, checks);
}

void test_close_and_replacement_fail_stop(int& checks) {
    require_callback_lifetime_fail_stop(
        CallbackLifetimeViolationProbe::immediate_close_v2_destruction,
        "live verification claim rejects immediate raw close_v2 destruction",
        checks);
    require_callback_lifetime_fail_stop(
        CallbackLifetimeViolationProbe::deferred_close_v2_destruction,
        "live verification claim rejects deferred close_v2 zombie destruction",
        checks);
    require_callback_lifetime_fail_stop(
        CallbackLifetimeViolationProbe::named_claim_replacement,
        "live verification claim rejects named-slot replacement", checks);
    require_callback_lifetime_fail_stop(
        CallbackLifetimeViolationProbe::typed_owner_reset,
        "typed database owner rejects close while verification borrow is live",
        checks);
}

void test_geometry_derivation(int& checks) {
    expect_runtime_error(
        [] { (void)sqlite_verification_budget_for_snapshot(0U, 1U); },
        "nonzero verified geometry", "zero bytes rejected", checks);
    expect_runtime_error(
        [] { (void)sqlite_verification_budget_for_snapshot(4096U, 0U); },
        "nonzero verified geometry", "zero pages rejected", checks);

    const auto small = sqlite_verification_budget_for_snapshot(4096U, 1U);
    expect(small.maximum_progress_callbacks == 10'000U,
           "small geometry callback floor", checks);
    expect(small.maximum_rows == 1'024U,
           "small geometry row floor", checks);
    expect(small.maximum_decoded_text_bytes == 4ULL * 1024ULL * 1024ULL,
           "small geometry decoded floor", checks);
    expect(small.maximum_retained_text_bytes == 1ULL * 1024ULL * 1024ULL,
           "small geometry retained floor", checks);

    const auto medium = sqlite_verification_budget_for_snapshot(
        8ULL * 1024ULL * 1024ULL, 2048U);
    expect(medium.maximum_progress_callbacks == 131'072U,
           "geometry reduced callback authority", checks);
    expect(medium.maximum_rows == 65'536U,
           "geometry reduced row authority", checks);
    expect(medium.maximum_decoded_text_bytes == 32ULL * 1024ULL * 1024ULL,
           "geometry reduced decoded authority", checks);
    expect(medium.maximum_retained_text_bytes == 8ULL * 1024ULL * 1024ULL,
           "geometry reduced retained authority", checks);

    const auto huge = sqlite_verification_budget_for_snapshot(
        UINT64_MAX, UINT64_MAX);
    expect(huge.maximum_progress_callbacks ==
               kMaximumSqliteVerificationProgressCallbacks,
           "saturating callback ceiling", checks);
    expect(huge.maximum_rows == kMaximumSqliteVerificationRows,
           "saturating row ceiling", checks);
    expect(huge.maximum_decoded_text_bytes ==
               kMaximumSqliteVerificationDecodedTextBytes,
           "saturating decoded ceiling", checks);
    expect(huge.maximum_retained_text_bytes ==
               kMaximumSqliteVerificationRetainedTextBytes,
           "saturating retained ceiling", checks);
}

void test_manual_accounting(int& checks) {
    Database database;
    SqliteVerificationBudgetPolicy policy;
    policy.maximum_rows = 2U;
    policy.maximum_decoded_text_bytes = 5U;
    policy.maximum_retained_text_bytes = 4U;
    SqliteVerificationBudget budget(database.serialized_borrow(), "manual accounting", policy);

    budget.consume_row();
    budget.consume_row();
    expect(budget.rows() == 2U, "exact row edge accepted", checks);
    expect_budget_failure(
        [&] { budget.consume_row(); }, SqliteVerificationBudgetFailure::row_limit,
        3U, 2U, "third row rejected exactly", checks);
    expect(budget.exhausted(), "failure is sticky", checks);
    expect(budget.failure() == SqliteVerificationBudgetFailure::row_limit,
           "sticky failure kind", checks);
    expect(budget.safe_summary() ==
               "sqlite_verification_budget[row_limit]:observed=3:limit=2",
           "safe summary is value-free", checks);
    expect_budget_failure(
        [&] { budget.checkpoint(); }, SqliteVerificationBudgetFailure::row_limit,
        3U, 2U, "sticky failure rethrows", checks);
    budget.detach();

    SqliteVerificationBudgetPolicy decoded_policy;
    decoded_policy.maximum_decoded_text_bytes = 5U;
    SqliteVerificationBudget decoded(database.serialized_borrow(), "decoded", decoded_policy);
    decoded.consume_decoded_text_bytes(2U);
    decoded.consume_decoded_text_bytes(3U);
    expect(decoded.decoded_text_bytes() == 5U,
           "exact decoded-byte edge accepted", checks);
    expect_budget_failure(
        [&] { decoded.consume_decoded_text_bytes(1U); },
        SqliteVerificationBudgetFailure::decoded_text_byte_limit, 6U, 5U,
        "decoded-byte excess rejected", checks);
    decoded.detach();

    SqliteVerificationBudgetPolicy text_row_policy;
    text_row_policy.maximum_rows = 2U;
    text_row_policy.maximum_decoded_text_bytes = 5U;
    SqliteVerificationBudget text_row(database.serialized_borrow(), "text row", text_row_policy);
    text_row.consume_text_row({"ab", "c"});
    text_row.consume_text_row({"de"});
    expect(text_row.rows() == 2U, "combined row accounting", checks);
    expect(text_row.decoded_text_bytes() == 5U,
           "combined decoded accounting", checks);
    text_row.detach();

    SqliteVerificationBudgetPolicy retained_policy;
    retained_policy.maximum_retained_text_bytes = 4U;
    SqliteVerificationBudget retained(database.serialized_borrow(), "retained", retained_policy);
    retained.consume_retained_text({"a", "bcd"});
    expect(retained.retained_text_bytes() == 4U,
           "exact retained-byte edge accepted", checks);
    expect_budget_failure(
        [&] { retained.consume_retained_text({"x"}); },
        SqliteVerificationBudgetFailure::retained_text_byte_limit, 5U, 4U,
        "retained-byte excess rejected", checks);
    retained.detach();
}

void test_progress_interrupt_and_detach(int& checks) {
    Database database;
    sqlite3_stmt* statement = nullptr;
    const char* sql =
        "WITH RECURSIVE x(v) AS (VALUES(1) UNION ALL SELECT v+1 FROM x WHERE v<100000) "
        "SELECT sum(v) FROM x;";
    expect(sqlite3_prepare_v2(database.get(), sql, -1, &statement, nullptr) ==
               SQLITE_OK,
           "recursive statement prepared", checks);

    SqliteVerificationBudgetPolicy policy;
    policy.maximum_progress_callbacks = 1U;
    policy.progress_opcode_interval = 1U;
    SqliteVerificationBudget budget(database.serialized_borrow(), "progress", policy);
    const int rc = sqlite3_step(statement);
    expect(rc == SQLITE_INTERRUPT, "SQLite VM interrupted", checks);
    expect(budget.progress_callbacks() == 2U,
           "interrupt occurs immediately past exact edge", checks);
    expect(budget.failure() ==
               SqliteVerificationBudgetFailure::progress_callback_limit,
           "interrupt preserves typed callback reason", checks);
    expect_budget_failure(
        [&] { budget.throw_if_exhausted(); },
        SqliteVerificationBudgetFailure::progress_callback_limit, 2U, 1U,
        "typed callback failure surfaced", checks);
    budget.detach();
    expect(sqlite3_finalize(statement) == SQLITE_INTERRUPT || statement == nullptr,
           "interrupted statement finalized", checks);

    sqlite3_stmt* trivial = nullptr;
    expect(sqlite3_prepare_v2(database.get(), "SELECT 1;", -1, &trivial, nullptr) ==
               SQLITE_OK,
           "post-detach statement prepared", checks);
    expect(sqlite3_step(trivial) == SQLITE_ROW,
           "explicit detach removes progress handler", checks);
    expect(sqlite3_finalize(trivial) == SQLITE_OK,
           "post-detach statement finalized", checks);

    {
        SqliteVerificationBudget scoped(database.serialized_borrow(), "destructor detach");
        expect(!scoped.exhausted(), "scoped owner attached", checks);
    }
    trivial = nullptr;
    expect(sqlite3_prepare_v2(database.get(), "SELECT 2;", -1, &trivial, nullptr) ==
               SQLITE_OK,
           "post-destructor statement prepared", checks);
    expect(sqlite3_step(trivial) == SQLITE_ROW,
           "destructor removes progress handler", checks);
    expect(sqlite3_finalize(trivial) == SQLITE_OK,
           "post-destructor statement finalized", checks);

    SqliteVerificationBudget detached(database.serialized_borrow(), "manual after detach");
    detached.detach();
    detached.consume_row();
    expect(detached.rows() == 1U,
           "manual accounting survives detach", checks);
}


enum class ForeignThreadFailStopProbe : std::uint8_t {
    sqlite_callback,
    detach,
    destructor,
};

void require_foreign_thread_fail_stop(ForeignThreadFailStopProbe probe,
                                      const std::string& label,
                                      int& checks) {
    auto process = spawn_inherited_test_process_or_throw(
        [probe]() -> int {
            Database database;
            SqliteVerificationBudgetPolicy policy;
            policy.progress_opcode_interval = 1U;

            if (probe == ForeignThreadFailStopProbe::destructor) {
                auto* budget = new SqliteVerificationBudget(
                    database.serialized_borrow(),
                    "foreign-thread destructor", policy);
                std::thread foreign([budget] { delete budget; });
                foreign.join();
                return 121;
            }

            SqliteVerificationBudget budget(
                database.serialized_borrow(),
                "foreign-thread callback owner", policy);
            if (probe == ForeignThreadFailStopProbe::detach) {
                std::thread foreign([&budget] { budget.detach(); });
                foreign.join();
                return 122;
            }

            std::thread foreign([&database] {
                static constexpr const char* kSql =
                    "WITH RECURSIVE x(v) AS (VALUES(1) UNION ALL "
                    "SELECT v+1 FROM x WHERE v<100000) SELECT sum(v) FROM x;";
                (void)sqlite3_exec(database.get(), kSql, nullptr, nullptr, nullptr);
            });
            foreign.join();
            budget.detach();
            return 123;
        },
        label);
    process.wait_for_exact_exit(kSyncProcessCapabilityViolationExitCode,
                                std::chrono::seconds(10), label);
    expect(true, label, checks);
}

void test_exact_thread_authority(int& checks) {
    Database database;
    static constexpr std::string_view kPrivateDiagnosticLabel =
        "exact-thread-owner-private-diagnostic";
    SqliteVerificationBudget budget(
        database.serialized_borrow(), std::string(kPrivateDiagnosticLabel));

    bool caught = false;
    std::string message;
    std::thread foreign([&] {
        try {
            budget.consume_row();
        } catch (const std::logic_error& error) {
            caught = true;
            message = error.what();
        }
    });
    foreign.join();

    expect(caught &&
               message.find("must execute on its originating thread") !=
                   std::string::npos,
           "foreign throwing entry point rejects exact-thread mismatch", checks);
    expect(message.find(kPrivateDiagnosticLabel) == std::string::npos,
           "foreign rejection does not disclose owner diagnostics", checks);
    expect(budget.rows() == 0U,
           "foreign throwing rejection preserves mutable counters", checks);
    budget.consume_row();
    expect(budget.rows() == 1U,
           "originating thread retains authority after rejection", checks);
    budget.detach();

    require_foreign_thread_fail_stop(
        ForeignThreadFailStopProbe::sqlite_callback,
        "foreign SQLite callback fails stopped before budget state", checks);
    require_foreign_thread_fail_stop(
        ForeignThreadFailStopProbe::detach,
        "foreign detach fails stopped before callback replacement", checks);
    require_foreign_thread_fail_stop(
        ForeignThreadFailStopProbe::destructor,
        "foreign destructor fails stopped before callback replacement", checks);
}

void test_elapsed_checkpoint(int& checks) {
    Database database;
    SqliteVerificationBudgetPolicy policy;
    policy.maximum_elapsed_milliseconds = 1U;
    SqliteVerificationBudget budget(database.serialized_borrow(), "elapsed", policy);
    std::this_thread::sleep_for(std::chrono::milliseconds(4));
    bool caught = false;
    try {
        budget.checkpoint();
    } catch (const SqliteVerificationBudgetException& error) {
        caught = error.failure() ==
                     SqliteVerificationBudgetFailure::elapsed_time_limit &&
                 error.observed() > 1U && error.limit() == 1U;
    }
    expect(caught, "elapsed checkpoint rejects expired authority", checks);
    budget.detach();
}

}  // namespace

int main() {
    int checks = 0;
    try {
        test_type_and_failure_contract(checks);
        test_constructor_and_monotone_policy(checks);
        test_shared_claim_input_and_reuse_contract(checks);
        test_exact_generation_and_singleton_claim(checks);
        test_concurrent_duplicate_budgets_reject_without_fail_stop(checks);
        test_close_and_replacement_fail_stop(checks);
        test_geometry_derivation(checks);
        test_manual_accounting(checks);
        test_progress_interrupt_and_detach(checks);
        test_exact_thread_authority(checks);
        test_elapsed_checkpoint(checks);
        std::cout << "anonsync sqlite verification budget tests checks=" << checks
                  << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "anonsync sqlite verification budget tests failed after "
                  << checks << " checks: " << error.what() << "\n";
        return 1;
    }
}
