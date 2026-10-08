#include "sqlite_exact_value.hpp"

#include <sqlite3.h>

#include <cstddef>
#include <string>
#include <utility>

namespace anonsync::persistence {
namespace {

[[noreturn]] void fail(std::string_view label,
                       int column,
                       SqliteExactValueFailure failure) {
    throw SqliteExactValueException(std::string(label), column, failure);
}

int current_storage_class_or_throw(sqlite3_stmt* statement,
                                   int column,
                                   std::string_view label) {
    if (statement == nullptr) {
        fail(label, column, SqliteExactValueFailure::invalid_statement);
    }

    const int column_count = sqlite3_column_count(statement);
    // SQLite defines sqlite3_column_* only while the most recent step returned
    // SQLITE_ROW. sqlite3_data_count() is zero before the first step, after
    // SQLITE_DONE, and after reset; on a current row it equals column_count.
    if (column_count <= 0 || sqlite3_data_count(statement) != column_count) {
        fail(label, column,
             SqliteExactValueFailure::statement_not_positioned);
    }
    if (column < 0 || column >= column_count) {
        fail(label, column, SqliteExactValueFailure::invalid_column_index);
    }
    return sqlite3_column_type(statement, column);
}

void require_storage_class(int actual,
                           int expected,
                           int column,
                           std::string_view label) {
    if (actual != expected) {
        fail(label, column, SqliteExactValueFailure::wrong_storage_class);
    }
}

void require_byte_limit(int byte_count,
                        std::uint64_t maximum_bytes,
                        int column,
                        std::string_view label) {
    if (byte_count < 0) {
        fail(label, column, SqliteExactValueFailure::allocation_failure);
    }
    if (maximum_bytes != 0 &&
        static_cast<std::uint64_t>(byte_count) > maximum_bytes) {
        fail(label, column, SqliteExactValueFailure::byte_limit_exceeded);
    }
}

std::string exception_message(std::string label,
                              int column,
                              SqliteExactValueFailure failure) {
    if (label.empty()) label = "SQLite exact scalar";
    return std::move(label) + ": column " + std::to_string(column) + ": " +
           std::string(sqlite_exact_value_failure_name(failure));
}

}  // namespace

SqliteExactValueException::SqliteExactValueException(
    std::string label,
    int column,
    SqliteExactValueFailure failure)
    : std::runtime_error(exception_message(std::move(label), column, failure)),
      column_(column),
      failure_(failure) {}

std::string_view sqlite_exact_value_failure_name(
    SqliteExactValueFailure failure) noexcept {
    switch (failure) {
        case SqliteExactValueFailure::invalid_statement:
            return "invalid_statement";
        case SqliteExactValueFailure::statement_not_positioned:
            return "statement_not_positioned";
        case SqliteExactValueFailure::invalid_column_index:
            return "invalid_column_index";
        case SqliteExactValueFailure::null_value:
            return "null_value";
        case SqliteExactValueFailure::wrong_storage_class:
            return "wrong_storage_class";
        case SqliteExactValueFailure::negative_unsigned:
            return "negative_unsigned";
        case SqliteExactValueFailure::allocation_failure:
            return "allocation_failure";
        case SqliteExactValueFailure::byte_limit_exceeded:
            return "byte_limit_exceeded";
    }
    return "unknown_failure";
}

std::optional<std::string> sqlite_exact_optional_text_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label,
    std::uint64_t maximum_bytes) {
    const int storage_class =
        current_storage_class_or_throw(statement, column, label);
    if (storage_class == SQLITE_NULL) return std::nullopt;
    require_storage_class(storage_class, SQLITE_TEXT, column, label);

    // SQLite documents text/blob pointer first and byte count second as the
    // safe conversion order. The explicit byte count preserves embedded NULs.
    const unsigned char* text = sqlite3_column_text(statement, column);
    if (text == nullptr) {
        // The initial storage class was TEXT, so this cannot represent SQL
        // NULL. SQLite documents allocation failure as the remaining null case.
        fail(label, column, SqliteExactValueFailure::allocation_failure);
    }
    const int byte_count = sqlite3_column_bytes(statement, column);
    require_byte_limit(byte_count, maximum_bytes, column, label);
    return std::string(reinterpret_cast<const char*>(text),
                       static_cast<std::size_t>(byte_count));
}

std::string sqlite_exact_text_or_throw(sqlite3_stmt* statement,
                                       int column,
                                       std::string_view label,
                                       std::uint64_t maximum_bytes) {
    std::optional<std::string> value = sqlite_exact_optional_text_or_throw(
        statement, column, label, maximum_bytes);
    if (!value) {
        fail(label, column, SqliteExactValueFailure::null_value);
    }
    return std::move(*value);
}

std::optional<std::string> sqlite_exact_optional_blob_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label,
    std::uint64_t maximum_bytes) {
    const int storage_class =
        current_storage_class_or_throw(statement, column, label);
    if (storage_class == SQLITE_NULL) return std::nullopt;
    require_storage_class(storage_class, SQLITE_BLOB, column, label);

    const void* blob = sqlite3_column_blob(statement, column);
    if (blob == nullptr) {
        // A zero-length BLOB legitimately has a null pointer. Check the
        // connection error immediately so SQLITE_NOMEM cannot masquerade as
        // that valid empty value.
        sqlite3* database = sqlite3_db_handle(statement);
        if (database != nullptr && sqlite3_errcode(database) == SQLITE_NOMEM) {
            fail(label, column, SqliteExactValueFailure::allocation_failure);
        }
    }
    const int byte_count = sqlite3_column_bytes(statement, column);
    require_byte_limit(byte_count, maximum_bytes, column, label);
    if (blob == nullptr && byte_count != 0) {
        fail(label, column, SqliteExactValueFailure::allocation_failure);
    }
    if (byte_count == 0) return std::string{};
    return std::string(static_cast<const char*>(blob),
                       static_cast<std::size_t>(byte_count));
}

std::string sqlite_exact_blob_or_throw(sqlite3_stmt* statement,
                                       int column,
                                       std::string_view label,
                                       std::uint64_t maximum_bytes) {
    std::optional<std::string> value = sqlite_exact_optional_blob_or_throw(
        statement, column, label, maximum_bytes);
    if (!value) {
        fail(label, column, SqliteExactValueFailure::null_value);
    }
    return std::move(*value);
}

std::optional<std::int64_t> sqlite_exact_optional_i64_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label) {
    const int storage_class =
        current_storage_class_or_throw(statement, column, label);
    if (storage_class == SQLITE_NULL) return std::nullopt;
    require_storage_class(storage_class, SQLITE_INTEGER, column, label);
    return static_cast<std::int64_t>(
        sqlite3_column_int64(statement, column));
}

std::int64_t sqlite_exact_i64_or_throw(sqlite3_stmt* statement,
                                       int column,
                                       std::string_view label) {
    const std::optional<std::int64_t> value =
        sqlite_exact_optional_i64_or_throw(statement, column, label);
    if (!value) {
        fail(label, column, SqliteExactValueFailure::null_value);
    }
    return *value;
}

std::optional<std::uint64_t> sqlite_exact_optional_u64_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label) {
    const std::optional<std::int64_t> signed_value =
        sqlite_exact_optional_i64_or_throw(statement, column, label);
    if (!signed_value) return std::nullopt;
    if (*signed_value < 0) {
        fail(label, column, SqliteExactValueFailure::negative_unsigned);
    }
    return static_cast<std::uint64_t>(*signed_value);
}

std::uint64_t sqlite_exact_u64_or_throw(sqlite3_stmt* statement,
                                        int column,
                                        std::string_view label) {
    const std::optional<std::uint64_t> value =
        sqlite_exact_optional_u64_or_throw(statement, column, label);
    if (!value) {
        fail(label, column, SqliteExactValueFailure::null_value);
    }
    return *value;
}

}  // namespace anonsync::persistence
