#include "sqlite_verification_budget.hpp"

#include <sqlite3.h>

#include <chrono>
#include <cstdint>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <type_traits>

namespace {

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

class Database final {
public:
    Database() {
        if (sqlite3_open_v2(":memory:", &db_,
                            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                                SQLITE_OPEN_FULLMUTEX,
                            nullptr) != SQLITE_OK) {
            const std::string message =
                db_ == nullptr ? "SQLite memory open failed" : sqlite3_errmsg(db_);
            if (db_ != nullptr) sqlite3_close_v2(db_);
            db_ = nullptr;
            throw std::runtime_error(message);
        }
    }

    ~Database() {
        if (db_ != nullptr) sqlite3_close_v2(db_);
    }

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    [[nodiscard]] sqlite3* get() const noexcept { return db_; }

private:
    sqlite3* db_ = nullptr;
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
        [&] { SqliteVerificationBudget budget(nullptr, "null"); },
        "requires an open database handle", "null database rejected", checks);
    expect_runtime_error(
        [&] { SqliteVerificationBudget budget(database.get(), ""); },
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
            [&] { SqliteVerificationBudget budget(database.get(), "zero", policy); },
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
            [&] { SqliteVerificationBudget budget(database.get(), "widen", policy); },
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
        SqliteVerificationBudget budget(database.get(), "tight policy", tight);
        expect(!budget.exhausted(), "tight policy accepted", checks);
    }
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
    SqliteVerificationBudget budget(database.get(), "manual accounting", policy);

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
    SqliteVerificationBudget decoded(database.get(), "decoded", decoded_policy);
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
    SqliteVerificationBudget text_row(database.get(), "text row", text_row_policy);
    text_row.consume_text_row({"ab", "c"});
    text_row.consume_text_row({"de"});
    expect(text_row.rows() == 2U, "combined row accounting", checks);
    expect(text_row.decoded_text_bytes() == 5U,
           "combined decoded accounting", checks);
    text_row.detach();

    SqliteVerificationBudgetPolicy retained_policy;
    retained_policy.maximum_retained_text_bytes = 4U;
    SqliteVerificationBudget retained(database.get(), "retained", retained_policy);
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
    SqliteVerificationBudget budget(database.get(), "progress", policy);
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
        SqliteVerificationBudget scoped(database.get(), "destructor detach");
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

    SqliteVerificationBudget detached(database.get(), "manual after detach");
    detached.detach();
    detached.consume_row();
    expect(detached.rows() == 1U,
           "manual accounting survives detach", checks);
}

void test_elapsed_checkpoint(int& checks) {
    Database database;
    SqliteVerificationBudgetPolicy policy;
    policy.maximum_elapsed_milliseconds = 1U;
    SqliteVerificationBudget budget(database.get(), "elapsed", policy);
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
        test_geometry_derivation(checks);
        test_manual_accounting(checks);
        test_progress_interrupt_and_detach(checks);
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
