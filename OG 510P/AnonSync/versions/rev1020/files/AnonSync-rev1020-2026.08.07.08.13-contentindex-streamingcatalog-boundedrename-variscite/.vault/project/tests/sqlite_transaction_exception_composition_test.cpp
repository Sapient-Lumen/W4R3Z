#include "sync_sqlite_connection_authority.hpp"
#include "sync_sqlite_connection_authority_internal.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace {

using namespace anonsync;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Function>
void require_throws(Function&& function,
                    std::string_view expected_fragment,
                    const std::string& message,
                    std::uint64_t& checks) {
    ++checks;
    try {
        function();
    } catch (const std::exception& error) {
        const std::string reason = error.what();
        if (reason.find(expected_fragment) != std::string::npos) return;
        fail(message + ": unexpected error: " + reason);
    }
    fail(message + ": no exception was thrown");
}

struct SqliteCloser final {
    void operator()(sqlite3* db) const noexcept {
        if (db == nullptr) return;
        revoke_sync_sqlite_connection_authority_before_close_noexcept(db);
        (void)sqlite3_close_v2(db);
    }
};
using SqlitePtr = std::unique_ptr<sqlite3, SqliteCloser>;

SqlitePtr open_memory_database() {
    sqlite3* raw = nullptr;
    const int rc = sqlite3_open_v2(
        ":memory:",
        &raw,
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    if (rc != SQLITE_OK) {
        const std::string reason =
            raw != nullptr ? sqlite3_errmsg(raw) : "unknown SQLite open error";
        if (raw != nullptr) (void)sqlite3_close_v2(raw);
        fail("could not open exception-composition database: " + reason);
    }
    return SqlitePtr(raw);
}

bool ascii_case_equal(const char* raw, std::string_view expected) noexcept {
    if (raw == nullptr) return false;
    std::size_t index = 0;
    for (; index < expected.size() && raw[index] != '\0'; ++index) {
        unsigned char observed = static_cast<unsigned char>(raw[index]);
        unsigned char wanted = static_cast<unsigned char>(expected[index]);
        if (observed >= 'a' && observed <= 'z') {
            observed = static_cast<unsigned char>(observed - 'a' + 'A');
        }
        if (wanted >= 'a' && wanted <= 'z') {
            wanted = static_cast<unsigned char>(wanted - 'a' + 'A');
        }
        if (observed != wanted) return false;
    }
    return index == expected.size() && raw[index] == '\0';
}

// One callback denial is a deterministic cut after the typed owner has armed
// its exact single-use permit but before SQLite applies that boundary. The
// policy itself never mutates the connection and never throws across the C ABI.
struct OneShotBoundaryCutpoint final {
    int target_action = 0;
    std::string target_operation;
    std::uint64_t matching_callbacks = 0;
    std::uint64_t denials = 0;
    bool armed = false;

    void arm(int action, std::string operation) {
        if (armed) fail("attempted to arm a second boundary cutpoint");
        target_action = action;
        target_operation = std::move(operation);
        matching_callbacks = 0;
        armed = true;
    }

    void require_consumed(std::uint64_t& checks, const std::string& label) const {
        require(!armed && matching_callbacks == 1 && denials == 1,
                label + " did not consume exactly one policy cutpoint",
                checks);
    }
};

int one_shot_cutpoint_policy(OneShotBoundaryCutpoint& cutpoint,
                             int action,
                             const char* argument1,
                             const char*,
                             const char*,
                             const char*) noexcept {
    if (!cutpoint.armed || action != cutpoint.target_action ||
        !ascii_case_equal(argument1, cutpoint.target_operation)) {
        return SQLITE_OK;
    }
    ++cutpoint.matching_callbacks;
    ++cutpoint.denials;
    cutpoint.armed = false;
    return SQLITE_DENY;
}

struct Fixture final {
    std::shared_ptr<OneShotBoundaryCutpoint> cutpoint_owner =
        std::make_shared<OneShotBoundaryCutpoint>();
    OneShotBoundaryCutpoint& cutpoint = *cutpoint_owner;
    SqlitePtr db = open_memory_database();
    SyncSqliteConnectionAuthorityProof authority;

    Fixture() {
        sqlite_exec_or_throw(
            db.get(),
            "CREATE TABLE trace_rows(value INTEGER PRIMARY KEY);",
            "exception-composition schema");
        authority = install_sync_sqlite_connection_authority_or_throw(
            db.get(),
            make_sync_sqlite_owned_authorizer_policy<
                one_shot_cutpoint_policy>(cutpoint_owner),
            "exception-composition authority");
        if (!authority.valid()) fail("exception-composition authority is invalid");
    }
};

std::vector<int> actual_rows(sqlite3* db) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        db,
        "SELECT value FROM trace_rows ORDER BY value;",
        "exception-composition row snapshot");
    std::vector<int> rows;
    for (;;) {
        const int rc = sqlite3_step(statement.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, "exception-composition row step");
        }
        rows.push_back(sqlite3_column_int(statement.stmt, 0));
    }
    return rows;
}

std::string render_rows(const std::vector<int>& rows) {
    std::string out = "[";
    for (std::size_t index = 0; index < rows.size(); ++index) {
        if (index != 0) out += ",";
        out += std::to_string(rows[index]);
    }
    out += "]";
    return out;
}

// This model is intentionally independent of SQLite and the C++ guard state.
// A mark is a copy of the visible row set immediately after SAVEPOINT. The
// split rollback transition models SQLite's documented rule precisely:
// ROLLBACK TO rewinds but leaves the named mark live; RELEASE erases it.
class TransactionStackModel final {
public:
    void begin() {
        if (working_.has_value()) fail("model began a nested outer transaction");
        working_ = committed_;
    }

    void insert(int value) {
        if (!working_.has_value()) fail("model insert lacks an outer transaction");
        working_->push_back(value);
        std::sort(working_->begin(), working_->end());
    }

    void begin_savepoint() {
        if (!working_.has_value()) fail("model savepoint lacks an outer transaction");
        marks_.push_back(*working_);
    }

    void release_savepoint() {
        if (marks_.empty()) fail("model release lacks a savepoint");
        marks_.pop_back();
    }

    void rollback_to_keep_mark() {
        if (marks_.empty() || !working_.has_value()) {
            fail("model rollback-to lacks a savepoint");
        }
        *working_ = marks_.back();
    }

    void rollback_to_and_release() {
        rollback_to_keep_mark();
        release_savepoint();
    }

    void commit() {
        if (!working_.has_value() || !marks_.empty()) {
            fail("model commit crossed a live savepoint");
        }
        committed_ = *working_;
        working_.reset();
    }

    void rollback() {
        if (!working_.has_value()) fail("model rollback lacks a transaction");
        working_.reset();
        marks_.clear();
    }

    [[nodiscard]] const std::vector<int>& visible() const {
        return working_.has_value() ? *working_ : committed_;
    }

    [[nodiscard]] std::size_t savepoint_depth() const noexcept {
        return marks_.size();
    }

private:
    std::vector<int> committed_;
    std::optional<std::vector<int>> working_;
    std::vector<std::vector<int>> marks_;
};

void insert_row(sqlite3* db, TransactionStackModel& model, int value) {
    sqlite_exec_or_throw(
        db,
        "INSERT INTO trace_rows(value) VALUES(" + std::to_string(value) + ");",
        "exception-composition insert");
    model.insert(value);
}

void require_matches_model(sqlite3* db,
                           const TransactionStackModel& model,
                           const std::string& label,
                           std::uint64_t& checks) {
    const std::vector<int> observed = actual_rows(db);
    require(observed == model.visible(),
            label + " diverged: SQLite=" + render_rows(observed) +
                " model=" + render_rows(model.visible()),
            checks);
}

void test_denied_savepoint_begin_is_retryable(std::uint64_t& checks) {
    Fixture fixture;
    TransactionStackModel model;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "cutpoint savepoint begin parent",
        SyncSqliteTransactionMode::Immediate);
    model.begin();
    insert_row(fixture.db.get(), model, 10);

    fixture.cutpoint.arm(SQLITE_SAVEPOINT, "BEGIN");
    require_throws(
        [&] {
            SyncSqliteSavepoint denied(
                fixture.db.get(), transaction.authority(),
                "cutpoint denied savepoint begin");
        },
        "not authorized",
        "denied SAVEPOINT begin did not surface SQLITE_AUTH",
        checks);
    fixture.cutpoint.require_consumed(checks, "SAVEPOINT begin");
    require(transaction.active() && model.savepoint_depth() == 0,
            "denied SAVEPOINT begin damaged the parent or model stack",
            checks);
    require_matches_model(fixture.db.get(), model,
                          "denied SAVEPOINT begin", checks);

    SyncSqliteSavepoint retry(
        fixture.db.get(), transaction.authority(),
        "cutpoint retried savepoint begin");
    model.begin_savepoint();
    insert_row(fixture.db.get(), model, 11);
    retry.release();
    model.release_savepoint();
    transaction.commit();
    model.commit();
    require_matches_model(fixture.db.get(), model,
                          "retried SAVEPOINT begin", checks);
}

void test_denied_release_preserves_exact_mark(std::uint64_t& checks) {
    Fixture fixture;
    TransactionStackModel model;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "cutpoint release parent",
        SyncSqliteTransactionMode::Immediate);
    model.begin();
    insert_row(fixture.db.get(), model, 20);
    SyncSqliteSavepoint savepoint(
        fixture.db.get(), transaction.authority(), "cutpoint release mark");
    model.begin_savepoint();
    insert_row(fixture.db.get(), model, 21);

    fixture.cutpoint.arm(SQLITE_SAVEPOINT, "RELEASE");
    require_throws(
        [&] { savepoint.release(); },
        "not authorized",
        "denied RELEASE did not surface SQLITE_AUTH",
        checks);
    fixture.cutpoint.require_consumed(checks, "SAVEPOINT release");
    require(savepoint.active() && transaction.active() &&
                model.savepoint_depth() == 1,
            "denied RELEASE revoked a retryable exact mark",
            checks);
    require_matches_model(fixture.db.get(), model,
                          "denied RELEASE", checks);
    require_throws(
        [&] { transaction.commit(); },
        "typed savepoint remains active",
        "outer COMMIT crossed a mark whose RELEASE was denied",
        checks);

    savepoint.release();
    model.release_savepoint();
    transaction.commit();
    model.commit();
    require_matches_model(fixture.db.get(), model,
                          "retried RELEASE", checks);
}

void test_denied_rollback_to_preserves_unrewound_state(std::uint64_t& checks) {
    Fixture fixture;
    TransactionStackModel model;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "cutpoint rollback-to parent",
        SyncSqliteTransactionMode::Immediate);
    model.begin();
    insert_row(fixture.db.get(), model, 30);
    SyncSqliteSavepoint savepoint(
        fixture.db.get(), transaction.authority(), "cutpoint rollback-to mark");
    model.begin_savepoint();
    insert_row(fixture.db.get(), model, 31);

    fixture.cutpoint.arm(SQLITE_SAVEPOINT, "ROLLBACK");
    require_throws(
        [&] { savepoint.rollback(); },
        "not authorized",
        "denied ROLLBACK TO did not surface SQLITE_AUTH",
        checks);
    fixture.cutpoint.require_consumed(checks, "SAVEPOINT rollback-to");
    require(savepoint.active() && transaction.active(),
            "denied ROLLBACK TO revoked its retry authority",
            checks);
    require_matches_model(fixture.db.get(), model,
                          "denied ROLLBACK TO", checks);

    savepoint.rollback();
    model.rollback_to_and_release();
    transaction.commit();
    model.commit();
    require_matches_model(fixture.db.get(), model,
                          "retried ROLLBACK TO", checks);
}

void test_release_cut_after_rewind_models_partial_effect(std::uint64_t& checks) {
    Fixture fixture;
    TransactionStackModel model;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "cutpoint split rollback parent",
        SyncSqliteTransactionMode::Immediate);
    model.begin();
    insert_row(fixture.db.get(), model, 40);
    SyncSqliteSavepoint savepoint(
        fixture.db.get(), transaction.authority(), "cutpoint split rollback mark");
    model.begin_savepoint();
    insert_row(fixture.db.get(), model, 41);

    // Critical composition cut: ROLLBACK TO succeeds, then RELEASE is denied.
    // The data must be rewound while the exact named mark and guard remain live.
    fixture.cutpoint.arm(SQLITE_SAVEPOINT, "RELEASE");
    require_throws(
        [&] { savepoint.rollback(); },
        "not authorized",
        "post-rewind RELEASE denial did not surface SQLITE_AUTH",
        checks);
    model.rollback_to_keep_mark();
    fixture.cutpoint.require_consumed(checks, "post-rewind RELEASE");
    require(savepoint.active() && transaction.active() &&
                model.savepoint_depth() == 1,
            "post-rewind RELEASE denial erased retry authority",
            checks);
    require_matches_model(fixture.db.get(), model,
                          "post-rewind RELEASE denial", checks);
    require_throws(
        [&] { transaction.commit(); },
        "typed savepoint remains active",
        "outer COMMIT crossed a rewound but unreleased mark",
        checks);

    // Work after the rewind is still inside the surviving mark. Retrying the
    // rollback must rewind it again before erasing the mark.
    insert_row(fixture.db.get(), model, 42);
    savepoint.rollback();
    model.rollback_to_and_release();
    transaction.commit();
    model.commit();
    require_matches_model(fixture.db.get(), model,
                          "retried post-rewind rollback", checks);
}

void test_nested_partial_rollback_preserves_lifo(std::uint64_t& checks) {
    Fixture fixture;
    TransactionStackModel model;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "cutpoint nested parent",
        SyncSqliteTransactionMode::Immediate);
    model.begin();
    insert_row(fixture.db.get(), model, 70);
    SyncSqliteSavepoint outer(
        fixture.db.get(), transaction.authority(), "cutpoint nested outer");
    model.begin_savepoint();
    insert_row(fixture.db.get(), model, 71);
    SyncSqliteSavepoint inner(
        fixture.db.get(), transaction.authority(), "cutpoint nested inner");
    model.begin_savepoint();
    insert_row(fixture.db.get(), model, 72);

    fixture.cutpoint.arm(SQLITE_SAVEPOINT, "RELEASE");
    require_throws(
        [&] { inner.rollback(); },
        "not authorized",
        "nested post-rewind RELEASE denial did not surface SQLITE_AUTH",
        checks);
    model.rollback_to_keep_mark();
    fixture.cutpoint.require_consumed(checks, "nested post-rewind RELEASE");
    require_matches_model(fixture.db.get(), model,
                          "nested post-rewind RELEASE denial", checks);
    require_throws(
        [&] { outer.release(); },
        "reverse construction order",
        "outer mark crossed a partially closed inner mark",
        checks);

    inner.rollback();
    model.rollback_to_and_release();
    outer.release();
    model.release_savepoint();
    transaction.commit();
    model.commit();
    require_matches_model(fixture.db.get(), model,
                          "nested retry completion", checks);
}

void test_denied_commit_is_retryable(std::uint64_t& checks) {
    Fixture fixture;
    TransactionStackModel model;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "cutpoint commit transaction",
        SyncSqliteTransactionMode::Immediate);
    model.begin();
    insert_row(fixture.db.get(), model, 50);

    fixture.cutpoint.arm(SQLITE_TRANSACTION, "COMMIT");
    require_throws(
        [&] { transaction.commit(); },
        "not authorized",
        "denied COMMIT did not surface SQLITE_AUTH",
        checks);
    fixture.cutpoint.require_consumed(checks, "transaction COMMIT");
    require(transaction.active() && sqlite3_get_autocommit(fixture.db.get()) == 0,
            "denied COMMIT revoked a still-live transaction generation",
            checks);
    require_matches_model(fixture.db.get(), model,
                          "denied COMMIT", checks);

    transaction.commit();
    model.commit();
    require_matches_model(fixture.db.get(), model,
                          "retried COMMIT", checks);
}

void test_denied_rollback_is_retryable(std::uint64_t& checks) {
    Fixture fixture;
    TransactionStackModel model;
    SyncSqliteTransaction transaction(
        fixture.db.get(), "cutpoint outer rollback transaction",
        SyncSqliteTransactionMode::Immediate);
    model.begin();
    insert_row(fixture.db.get(), model, 60);

    fixture.cutpoint.arm(SQLITE_TRANSACTION, "ROLLBACK");
    require_throws(
        [&] { transaction.rollback(); },
        "not authorized",
        "denied outer ROLLBACK did not surface SQLITE_AUTH",
        checks);
    fixture.cutpoint.require_consumed(checks, "transaction ROLLBACK");
    require(transaction.active() && sqlite3_get_autocommit(fixture.db.get()) == 0,
            "denied outer ROLLBACK revoked a still-live generation",
            checks);
    require_matches_model(fixture.db.get(), model,
                          "denied outer ROLLBACK", checks);

    transaction.rollback();
    model.rollback();
    require_matches_model(fixture.db.get(), model,
                          "retried outer ROLLBACK", checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        test_denied_savepoint_begin_is_retryable(checks);
        test_denied_release_preserves_exact_mark(checks);
        test_denied_rollback_to_preserves_unrewound_state(checks);
        test_release_cut_after_rewind_models_partial_effect(checks);
        test_nested_partial_rollback_preserves_lifo(checks);
        test_denied_commit_is_retryable(checks);
        test_denied_rollback_is_retryable(checks);
        std::cout << "sqlite transaction exception composition checks=" << checks
                  << " failures=0\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "sqlite transaction exception composition checks=" << checks
                  << " failures=1 reason=" << error.what() << "\n";
        return EXIT_FAILURE;
    }
}
