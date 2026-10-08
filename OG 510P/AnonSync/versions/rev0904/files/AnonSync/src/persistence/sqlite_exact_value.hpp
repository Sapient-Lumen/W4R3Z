#pragma once

#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>

struct sqlite3_stmt;

namespace anonsync::persistence {

// SQLite is dynamically typed. These failures describe why a durable scalar
// could not be promoted into exact C++ evidence. No observed value bytes are
// retained in the exception.
enum class SqliteExactValueFailure : std::uint8_t {
    invalid_statement,
    statement_not_positioned,
    invalid_column_index,
    null_value,
    wrong_storage_class,
    negative_unsigned,
    allocation_failure,
    byte_limit_exceeded,
};

class SqliteExactValueException final : public std::runtime_error {
public:
    SqliteExactValueException(std::string label,
                              int column,
                              SqliteExactValueFailure failure);

    [[nodiscard]] int column() const noexcept { return column_; }
    [[nodiscard]] SqliteExactValueFailure failure() const noexcept {
        return failure_;
    }

private:
    int column_ = -1;
    SqliteExactValueFailure failure_{};
};

[[nodiscard]] std::string_view sqlite_exact_value_failure_name(
    SqliteExactValueFailure failure) noexcept;

// Every reader requires a statement whose most recent sqlite3_step() returned
// SQLITE_ROW, a valid column index, and the exact SQLite storage class named by
// the function. No numeric coercion or C-string truncation is permitted. The
// optional forms preserve SQL NULL as std::nullopt; the required forms reject
// it with SqliteExactValueFailure::null_value.
[[nodiscard]] std::optional<std::string> sqlite_exact_optional_text_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label,
    std::uint64_t maximum_bytes = 0);

[[nodiscard]] std::string sqlite_exact_text_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label,
    std::uint64_t maximum_bytes = 0);

[[nodiscard]] std::optional<std::string> sqlite_exact_optional_blob_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label,
    std::uint64_t maximum_bytes = 0);

[[nodiscard]] std::string sqlite_exact_blob_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label,
    std::uint64_t maximum_bytes = 0);

[[nodiscard]] std::optional<std::int64_t> sqlite_exact_optional_i64_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label);

[[nodiscard]] std::int64_t sqlite_exact_i64_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label);

[[nodiscard]] std::optional<std::uint64_t> sqlite_exact_optional_u64_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label);

[[nodiscard]] std::uint64_t sqlite_exact_u64_or_throw(
    sqlite3_stmt* statement,
    int column,
    std::string_view label);

}  // namespace anonsync::persistence
