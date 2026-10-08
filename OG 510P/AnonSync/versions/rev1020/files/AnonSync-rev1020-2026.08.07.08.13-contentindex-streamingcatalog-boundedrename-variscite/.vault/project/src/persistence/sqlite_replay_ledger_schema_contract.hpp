#pragma once

#include <cstddef>
#include <cstdint>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace anonsync::persistence {

inline constexpr std::int64_t kSqliteReplayLedgerSchemaVersion = 10;
inline constexpr std::string_view kSqliteReplayLedgerBackendName = "sqlite-wal";
inline constexpr std::string_view kSqliteReplayLedgerHashAlgorithm = "sha256";
inline constexpr std::string_view kSqliteReplayLedgerEntryMaterialVersion =
    "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent";
inline constexpr std::string_view kSqliteReplayLedgerCommitProtocol =
    "sqlite-wal-begin-immediate-full-sync";

// sqlite_schema.sql is durable protocol evidence for this schema version. Each
// definition is the exact normalized SQL SQLite stores after executing the
// canonical CREATE statement. The same definitions create new databases and
// attest existing or restored databases; there is no second, weaker schema
// description that can drift from the write path.
struct SqliteReplayLedgerSchemaDefinition {
    std::string_view type;
    std::string_view name;
    std::string_view table_name;
    std::string_view stored_sql;
};

struct ObservedSqliteSchemaObject {
    std::string type;
    std::string name;
    std::string table_name;
    std::string stored_sql;
};

enum class SqliteReplayLedgerSchemaFailure : std::uint8_t {
    none,
    unexpected_object,
    duplicate_object_name,
    object_type_mismatch,
    table_name_mismatch,
    schema_sql_mismatch,
    missing_object,
};

struct SqliteReplayLedgerSchemaVerification {
    SqliteReplayLedgerSchemaFailure failure{
        SqliteReplayLedgerSchemaFailure::none};
    std::size_t observed_index = 0;
    std::string expected_object_name;

    [[nodiscard]] explicit operator bool() const noexcept {
        return failure == SqliteReplayLedgerSchemaFailure::none;
    }

    // The summary never includes observed names or SQL bytes. A hostile schema
    // cannot inject controls, secrets, or terminal escapes into diagnostics.
    [[nodiscard]] std::string safe_summary() const;
};

[[nodiscard]] std::string_view sqlite_replay_ledger_schema_failure_name(
    SqliteReplayLedgerSchemaFailure failure) noexcept;

[[nodiscard]] std::span<const SqliteReplayLedgerSchemaDefinition>
sqlite_replay_ledger_schema_contract() noexcept;

// New databases execute these exact definitions with only a trailing semicolon
// added. SQLite persists the corresponding stored_sql text in sqlite_schema.
[[nodiscard]] std::string sqlite_replay_ledger_schema_create_statement(
    const SqliteReplayLedgerSchemaDefinition& definition);

[[nodiscard]] SqliteReplayLedgerSchemaVerification
verify_sqlite_replay_ledger_schema(
    std::span<const ObservedSqliteSchemaObject> observed);

}  // namespace anonsync::persistence
