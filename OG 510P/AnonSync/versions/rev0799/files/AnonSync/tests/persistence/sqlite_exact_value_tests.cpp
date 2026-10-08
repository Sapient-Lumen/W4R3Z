#include "sqlite_exact_value.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

using anonsync::persistence::SqliteExactValueException;
using anonsync::persistence::SqliteExactValueFailure;
using anonsync::persistence::sqlite_exact_blob_or_throw;
using anonsync::persistence::sqlite_exact_i64_or_throw;
using anonsync::persistence::sqlite_exact_optional_blob_or_throw;
using anonsync::persistence::sqlite_exact_optional_i64_or_throw;
using anonsync::persistence::sqlite_exact_optional_text_or_throw;
using anonsync::persistence::sqlite_exact_optional_u64_or_throw;
using anonsync::persistence::sqlite_exact_text_or_throw;
using anonsync::persistence::sqlite_exact_u64_or_throw;

class Database final {
public:
    Database() {
        if (sqlite3_open(":memory:", &db_) != SQLITE_OK) {
            const std::string message =
                db_ != nullptr ? sqlite3_errmsg(db_) : "SQLite open failed";
            if (db_ != nullptr) sqlite3_close(db_);
            throw std::runtime_error(message);
        }
    }

    ~Database() { if (db_ != nullptr) sqlite3_close(db_); }
    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    [[nodiscard]] sqlite3* get() const noexcept { return db_; }

private:
    sqlite3* db_ = nullptr;
};

class Statement final {
public:
    Statement(sqlite3* db, const std::string& sql) {
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &statement_, nullptr) !=
            SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(db));
        }
    }

    ~Statement() { if (statement_ != nullptr) sqlite3_finalize(statement_); }
    Statement(const Statement&) = delete;
    Statement& operator=(const Statement&) = delete;

    [[nodiscard]] sqlite3_stmt* get() const noexcept { return statement_; }

private:
    sqlite3_stmt* statement_ = nullptr;
};

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

template <typename Callable>
void require_failure(Callable&& callable,
                     SqliteExactValueFailure expected,
                     int expected_column,
                     const std::string& context,
                     std::uint64_t& checks) {
    ++checks;
    try {
        std::forward<Callable>(callable)();
    } catch (const SqliteExactValueException& error) {
        if (error.failure() != expected || error.column() != expected_column) {
            throw std::runtime_error(context + " returned the wrong exact-value failure");
        }
        const std::string summary = error.what();
        if (summary.find("sensitive-marker") != std::string::npos ||
            summary.find("hidden-suffix") != std::string::npos) {
            throw std::runtime_error(context + " leaked observed value bytes");
        }
        return;
    }
    throw std::runtime_error(context + " did not fail closed");
}

void step_row(Statement& statement) {
    if (sqlite3_step(statement.get()) != SQLITE_ROW) {
        throw std::runtime_error("test statement did not return SQLITE_ROW");
    }
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        Database database;
        {
            Statement statement(
                database.get(),
                "SELECT CAST(X'73656e7369746976652D6D61726B65720068696464656E2D737566666978' AS TEXT), X'780079', 42, -7, '', X'';");
            step_row(statement);
            const std::string text = sqlite_exact_text_or_throw(
                statement.get(), 0, "embedded-NUL text");
            require(text == std::string("sensitive-marker\0hidden-suffix", 30),
                    "embedded-NUL text was not preserved byte-for-byte", checks);
            const std::string blob = sqlite_exact_blob_or_throw(
                statement.get(), 1, "embedded-NUL blob");
            require(blob.size() == 3 && blob[1] == '\0',
                    "embedded-NUL blob was not preserved byte-for-byte", checks);
            require(sqlite_exact_i64_or_throw(statement.get(), 2, "signed integer") == 42,
                    "exact signed integer changed value", checks);
            require(sqlite_exact_u64_or_throw(statement.get(), 2, "unsigned integer") == 42,
                    "exact unsigned integer changed value", checks);
            require(sqlite_exact_i64_or_throw(statement.get(), 3, "negative signed integer") == -7,
                    "negative exact signed integer changed value", checks);
            require(sqlite_exact_text_or_throw(statement.get(), 4, "empty text").empty(),
                    "empty TEXT was not preserved", checks);
            require(sqlite_exact_blob_or_throw(statement.get(), 5, "empty blob").empty(),
                    "empty BLOB was not preserved", checks);
            require(sqlite_exact_optional_text_or_throw(
                        statement.get(), 0, "optional embedded-NUL text") == text,
                    "optional TEXT changed exact bytes", checks);
            require(sqlite_exact_optional_blob_or_throw(
                        statement.get(), 1, "optional embedded-NUL blob") == blob,
                    "optional BLOB changed exact bytes", checks);
            require(sqlite_exact_optional_i64_or_throw(
                        statement.get(), 2, "optional signed integer") == 42,
                    "optional signed integer changed value", checks);
            require(sqlite_exact_optional_u64_or_throw(
                        statement.get(), 2, "optional unsigned integer") == 42,
                    "optional unsigned integer changed value", checks);
            require(sqlite_exact_text_or_throw(
                        statement.get(), 0, "inclusive text byte limit", 30) == text,
                    "TEXT equal to its byte limit was rejected", checks);
            require(sqlite_exact_blob_or_throw(
                        statement.get(), 1, "inclusive blob byte limit", 3) == blob,
                    "BLOB equal to its byte limit was rejected", checks);
            require_failure(
                [&] { (void)sqlite_exact_u64_or_throw(statement.get(), 3, "negative unsigned"); },
                SqliteExactValueFailure::negative_unsigned,
                3,
                "negative unsigned",
                checks);
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), 0, "text byte limit", 29); },
                SqliteExactValueFailure::byte_limit_exceeded,
                0,
                "text byte limit",
                checks);
            require_failure(
                [&] { (void)sqlite_exact_blob_or_throw(statement.get(), 1, "blob byte limit", 2); },
                SqliteExactValueFailure::byte_limit_exceeded,
                1,
                "blob byte limit",
                checks);
        }
        {
            Statement statement(database.get(), "SELECT 2.75, '2', NULL, X'32';");
            step_row(statement);
            require_failure(
                [&] { (void)sqlite_exact_i64_or_throw(statement.get(), 0, "fractional integer"); },
                SqliteExactValueFailure::wrong_storage_class,
                0,
                "REAL-to-integer coercion",
                checks);
            require_failure(
                [&] { (void)sqlite_exact_i64_or_throw(statement.get(), 1, "text integer"); },
                SqliteExactValueFailure::wrong_storage_class,
                1,
                "TEXT-to-integer coercion",
                checks);
            require(!sqlite_exact_optional_text_or_throw(
                        statement.get(), 2, "optional null text").has_value(),
                    "optional TEXT did not preserve SQL NULL", checks);
            require(!sqlite_exact_optional_blob_or_throw(
                        statement.get(), 2, "optional null blob").has_value(),
                    "optional BLOB did not preserve SQL NULL", checks);
            require(!sqlite_exact_optional_i64_or_throw(
                        statement.get(), 2, "optional null integer").has_value(),
                    "optional INTEGER did not preserve SQL NULL", checks);
            require(!sqlite_exact_optional_u64_or_throw(
                        statement.get(), 2, "optional null unsigned").has_value(),
                    "optional unsigned INTEGER did not preserve SQL NULL", checks);
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), 2, "null text"); },
                SqliteExactValueFailure::null_value,
                2,
                "NULL text",
                checks);
            require_failure(
                [&] { (void)sqlite_exact_blob_or_throw(statement.get(), 2, "null blob"); },
                SqliteExactValueFailure::null_value,
                2,
                "NULL blob",
                checks);
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), 3, "blob as text"); },
                SqliteExactValueFailure::wrong_storage_class,
                3,
                "BLOB-to-text coercion",
                checks);
            require_failure(
                [&] { (void)sqlite_exact_blob_or_throw(statement.get(), 1, "text as blob"); },
                SqliteExactValueFailure::wrong_storage_class,
                1,
                "TEXT-to-BLOB coercion",
                checks);
        }
        {
            Statement statement(
                database.get(),
                "SELECT 9223372036854775807, -9223372036854775807 - 1;");
            step_row(statement);
            require(sqlite_exact_i64_or_throw(statement.get(), 0, "maximum i64") ==
                        INT64_C(9223372036854775807),
                    "maximum signed INTEGER changed value", checks);
            require(sqlite_exact_i64_or_throw(statement.get(), 1, "minimum i64") ==
                        INT64_MIN,
                    "minimum signed INTEGER changed value", checks);
            require(sqlite_exact_u64_or_throw(statement.get(), 0, "maximum SQLite u64") ==
                        UINT64_C(9223372036854775807),
                    "maximum nonnegative SQLite INTEGER changed value", checks);
        }
        {
            Statement statement(database.get(), "SELECT 'current row';");
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), 0, "unstepped"); },
                SqliteExactValueFailure::statement_not_positioned,
                0,
                "unstepped statement",
                checks);
            step_row(statement);
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), 1, "out of range"); },
                SqliteExactValueFailure::invalid_column_index,
                1,
                "out-of-range column",
                checks);
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), -1, "negative index"); },
                SqliteExactValueFailure::invalid_column_index,
                -1,
                "negative column index",
                checks);
            require(sqlite3_step(statement.get()) == SQLITE_DONE,
                    "statement did not reach SQLITE_DONE", checks);
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), 0, "exhausted"); },
                SqliteExactValueFailure::statement_not_positioned,
                0,
                "exhausted statement",
                checks);
            require(sqlite3_reset(statement.get()) == SQLITE_OK,
                    "statement reset failed", checks);
            require_failure(
                [&] { (void)sqlite_exact_text_or_throw(statement.get(), 0, "reset"); },
                SqliteExactValueFailure::statement_not_positioned,
                0,
                "reset statement",
                checks);
        }
        {
            Statement statement(database.get(), "SELECT X'';");
            step_row(statement);
            char* error = nullptr;
            const int rc = sqlite3_exec(
                database.get(), "SELECT * FROM deliberately_missing_table;",
                nullptr, nullptr, &error);
            sqlite3_free(error);
            require(rc == SQLITE_ERROR,
                    "unrelated SQLite error was not induced", checks);
            require(sqlite_exact_blob_or_throw(
                        statement.get(), 0, "empty BLOB after unrelated error").empty(),
                    "stale non-allocation connection error invalidated empty BLOB", checks);
        }
        require_failure(
            [&] { (void)sqlite_exact_text_or_throw(nullptr, 0, "null statement"); },
            SqliteExactValueFailure::invalid_statement,
            0,
            "null statement",
            checks);

        std::cout << "sqlite exact value: " << checks << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sqlite exact value: " << error.what() << '\n';
        return 1;
    }
}
