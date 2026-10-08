#include "sqlite_replay_ledger_reset.hpp"

#include "sha256_digest.hpp"
#include "sqlite_exact_value.hpp"
#include "sqlite_path_security.hpp"
#include "sqlite_replay_ledger_schema_contract.hpp"
#include "sqlite_replay_ledger_write_gate.hpp"
#include "sqlite_verification_budget.hpp"
#include "sync_sqlite_runtime.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <array>
#include <cctype>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <limits>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync::persistence {
namespace {

constexpr std::string_view kLogicalStateDigestFormat =
    "anonsync-sqlite-replay-ledger-logical-state-v1";
constexpr std::string_view kResetReceiptDigestFormat =
    "anonsync-sqlite-replay-ledger-logical-reset-receipt-v3";
constexpr std::uint64_t kMaximumSchemaSqlBytes = 16'384;
constexpr std::uint64_t kMaximumUnboundedLedgerTextBytes = 1ULL << 20U;

struct LedgerState final {
    SqliteReplayLedgerResetState public_state;
};

enum class DigestStorageClass : std::uint8_t {
    Integer,
    Text,
};

struct DigestColumn final {
    std::string_view name;
    DigestStorageClass storage_class;
    std::uint64_t maximum_text_bytes = 0;
};

constexpr std::array<DigestColumn, 6> kBackendProfileColumns{{
    {"id", DigestStorageClass::Integer},
    {"backend_name", DigestStorageClass::Text, 32},
    {"schema_version", DigestStorageClass::Integer},
    {"hash_algorithm", DigestStorageClass::Text, 32},
    {"entry_material_version", DigestStorageClass::Text, 256},
    {"commit_protocol", DigestStorageClass::Text, 128},
}};
constexpr std::array<DigestColumn, 2> kLedgerIdentityColumns{{
    {"id", DigestStorageClass::Integer},
    {"ledger_instance_id", DigestStorageClass::Text, 64},
}};
constexpr std::array<DigestColumn, 3> kMetadataColumns{{
    {"id", DigestStorageClass::Integer},
    {"line_count", DigestStorageClass::Integer},
    {"head_hash", DigestStorageClass::Text, 64},
}};
constexpr std::array<DigestColumn, 13> kLedgerEntryColumns{{
    {"sequence", DigestStorageClass::Integer},
    {"previous_hash", DigestStorageClass::Text, 64},
    {"entry_hash", DigestStorageClass::Text, 64},
    {"case_id", DigestStorageClass::Text, kMaximumUnboundedLedgerTextBytes},
    {"kind", DigestStorageClass::Text, 16},
    {"operation_id", DigestStorageClass::Text, kMaximumUnboundedLedgerTextBytes},
    {"contract_digest_sha256", DigestStorageClass::Text, 64},
    {"jti", DigestStorageClass::Text, kMaximumUnboundedLedgerTextBytes},
    {"action", DigestStorageClass::Text, 16},
    {"cloud_event_source", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"cloud_event_id", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"effect_idempotency_key", DigestStorageClass::Text, 64},
    {"effect_state", DigestStorageClass::Text, 16},
}};
constexpr std::array<DigestColumn, 13> kEffectTransitionColumns{{
    {"sequence", DigestStorageClass::Integer},
    {"previous_hash", DigestStorageClass::Text, 64},
    {"transition_hash", DigestStorageClass::Text, 64},
    {"ledger_instance_id", DigestStorageClass::Text, 64},
    {"effect_idempotency_key", DigestStorageClass::Text, 64},
    {"prepared_sequence", DigestStorageClass::Integer},
    {"prepared_entry_hash", DigestStorageClass::Text, 64},
    {"terminal_state", DigestStorageClass::Text, 16},
    {"result_digest_sha256", DigestStorageClass::Text, 64},
    {"transition_reason", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"transition_intent_id", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"transition_intent_signer_kid", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"transition_intent_sha256", DigestStorageClass::Text, 64},
}};
constexpr std::array<DigestColumn, 11> kEffectOutboxColumns{{
    {"effect_idempotency_key", DigestStorageClass::Text, 64},
    {"prepared_sequence", DigestStorageClass::Integer},
    {"prepared_entry_hash", DigestStorageClass::Text, 64},
    {"outbox_state", DigestStorageClass::Text, 16},
    {"dispatch_attempts", DigestStorageClass::Integer},
    {"worker_claim_id", DigestStorageClass::Text, 64},
    {"worker_id", DigestStorageClass::Text, 128},
    {"claimed_at_epoch", DigestStorageClass::Integer},
    {"lease_expires_at_epoch", DigestStorageClass::Integer},
    {"last_result_digest_sha256", DigestStorageClass::Text, 64},
    {"updated_at_sequence", DigestStorageClass::Integer},
}};
constexpr std::array<DigestColumn, 15> kIngressReplayColumns{{
    {"replay_key_sha256", DigestStorageClass::Text, 64},
    {"format", DigestStorageClass::Text, 128},
    {"service_config_sha256", DigestStorageClass::Text, 64},
    {"ingress_profile_sha256", DigestStorageClass::Text, 64},
    {"sender_replay_cache_instance_id", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"sender_proof_kid", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"principal", DigestStorageClass::Text,
     kMaximumUnboundedLedgerTextBytes},
    {"nonce", DigestStorageClass::Text, 128},
    {"issued_at_epoch", DigestStorageClass::Integer},
    {"observed_at_epoch", DigestStorageClass::Integer},
    {"replay_window_seconds", DigestStorageClass::Integer},
    {"material_sha256", DigestStorageClass::Text, 64},
    {"prepared_sequence", DigestStorageClass::Integer},
    {"prepared_entry_hash", DigestStorageClass::Text, 64},
    {"effect_idempotency_key", DigestStorageClass::Text, 64},
}};

[[nodiscard]] std::filesystem::path normalized_absolute_path_or_throw(
    const std::filesystem::path& input,
    bool require_already_normalized) {
    if (input.empty()) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset requires nonempty ledger path");
    }
    std::error_code error;
    const std::filesystem::path absolute = std::filesystem::absolute(input, error);
    if (error) {
        throw std::runtime_error(
            "sqlite-wal replay ledger reset could not make ledger path absolute: " +
            error.message());
    }
    const std::filesystem::path normalized = absolute.lexically_normal();
    if (normalized.empty() || normalized.filename().empty()) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset requires a database filename");
    }
    if (require_already_normalized &&
        input.generic_string() != normalized.generic_string()) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset request path must be absolute and lexically normalized");
    }
    return normalized;
}

[[nodiscard]] bool contains_ascii_control(std::string_view value) noexcept {
    for (const unsigned char character : value) {
        if (character < 0x20U || character == 0x7fU) return true;
    }
    return false;
}

void validate_intent_id_or_throw(const std::string& intent) {
    if (intent.empty() || intent.size() > 128U) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset intent id must contain 1..128 bytes");
    }
    for (const unsigned char character : intent) {
        const bool allowed =
            (character >= '0' && character <= '9') ||
            (character >= 'A' && character <= 'Z') ||
            (character >= 'a' && character <= 'z') || character == '.' ||
            character == '_' || character == ':' || character == '-';
        if (!allowed) {
            throw std::invalid_argument(
                "sqlite-wal replay ledger reset intent id must use only ASCII alphanumeric, '.', '_', ':', or '-' bytes");
        }
    }
}

void validate_safe_text_or_throw(std::string_view value,
                                 std::size_t maximum_bytes,
                                 std::string_view field) {
    if (value.empty() || value.size() > maximum_bytes ||
        contains_ascii_control(value)) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset " + std::string(field) +
            " must contain safe non-control bytes within its size limit");
    }
}

void validate_chain_summary_or_throw(std::int64_t count,
                                     const std::string& head,
                                     std::string_view label) {
    if (count < 0 ||
        (count == 0 && head != "GENESIS") ||
        (count > 0 && !is_lowercase_sha256_hex(head))) {
        throw std::invalid_argument(std::string(label) +
                                    " count/head relationship is invalid");
    }
}

void validate_expectation_or_throw(
    const SqliteReplayLedgerResetExpectation& expected) {
    if (!is_lowercase_sha256_hex(expected.ledger_instance_id)) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset expected instance id must be lowercase SHA-256");
    }
    if (!is_lowercase_sha256_hex(expected.state_sha256)) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset expected state digest must be lowercase SHA-256");
    }
    validate_chain_summary_or_throw(
        expected.durable_line_count, expected.durable_head_hash,
        "sqlite-wal replay ledger reset expected decision chain");
    validate_chain_summary_or_throw(
        expected.effect_transition_line_count,
        expected.effect_transition_head_hash,
        "sqlite-wal replay ledger reset expected transition chain");
    if (expected.ledger_entry_rows < 0 ||
        expected.effect_transition_rows < 0 ||
        expected.effect_outbox_rows < 0 ||
        expected.ingress_sender_replay_rows < 0) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset expected row counts must be nonnegative");
    }
    if (expected.ledger_entry_rows != expected.durable_line_count ||
        expected.effect_transition_rows !=
            expected.effect_transition_line_count) {
        throw std::invalid_argument(
            "sqlite-wal replay ledger reset expected metadata/table counts disagree");
    }
}

void validate_request_or_throw(const SqliteReplayLedgerResetRequest& request) {
    (void)normalized_absolute_path_or_throw(request.ledger_path, true);
    validate_intent_id_or_throw(request.reset_intent_id);
    validate_safe_text_or_throw(request.operator_id, 128, "operator id");
    validate_safe_text_or_throw(request.reason, 1024, "reason");
    validate_expectation_or_throw(request.expected);
}

void digest_token(Sha256DigestBuilder& digest,
                  std::string_view label,
                  std::string_view value) {
    const std::string label_size = std::to_string(label.size());
    const std::string value_size = std::to_string(value.size());
    digest.update(label_size);
    digest.update(":");
    digest.update(label);
    digest.update(value_size);
    digest.update(":");
    digest.update(value);
}

void digest_integer(Sha256DigestBuilder& digest,
                    std::string_view label,
                    std::int64_t value) {
    const std::string text = std::to_string(value);
    digest_token(digest, label, text);
}

void digest_unsigned_integer(Sha256DigestBuilder& digest,
                             std::string_view label,
                             std::uint64_t value) {
    const std::string text = std::to_string(value);
    digest_token(digest, label, text);
}

[[nodiscard]] int step_or_throw(sqlite3* db,
                                sqlite3_stmt* statement,
                                SqliteVerificationBudget* budget,
                                const std::string& label) {
    const int result = sqlite3_step(statement);
    if (result != SQLITE_ROW && result != SQLITE_DONE) {
        if (budget != nullptr) budget->throw_if_exhausted();
        throw_sqlite_exception(db, result, label);
    }
    return result;
}

void require_single_row(sqlite3* db,
                        sqlite3_stmt* statement,
                        const std::string& label) {
    if (step_or_throw(db, statement, nullptr, label + " first step") !=
        SQLITE_ROW) {
        throw std::runtime_error(label + " row is absent");
    }
}

void require_statement_done(sqlite3* db,
                            sqlite3_stmt* statement,
                            const std::string& label) {
    if (step_or_throw(db, statement, nullptr, label + " terminal step") !=
        SQLITE_DONE) {
        throw std::runtime_error(label + " returned more than one row");
    }
}

[[nodiscard]] std::string query_single_text(
    SyncSqliteDbHandleSlot& owner,
    const std::string& sql,
    const std::string& label,
    std::uint64_t maximum_bytes) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(owner, sql, label + " prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    require_single_row(db, statement.stmt, label);
    std::string value = sqlite_exact_text_or_throw(
        statement.stmt, 0, label, maximum_bytes);
    require_statement_done(db, statement.stmt, label);
    return value;
}

[[nodiscard]] std::int64_t query_single_i64(
    SyncSqliteDbHandleSlot& owner,
    const std::string& sql,
    const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(owner, sql, label + " prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    require_single_row(db, statement.stmt, label);
    const std::int64_t value =
        sqlite_exact_i64_or_throw(statement.stmt, 0, label);
    require_statement_done(db, statement.stmt, label);
    return value;
}

void verify_exact_schema_or_throw(SyncSqliteDbHandleSlot& owner,
                                  SqliteVerificationBudget& budget,
                                  const std::string& label) {
    const auto contract = sqlite_replay_ledger_schema_contract();
    std::vector<ObservedSqliteSchemaObject> observed;
    observed.reserve(contract.size() + 1U);
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        owner,
        "SELECT type, name, tbl_name, sql FROM sqlite_schema "
        "WHERE sql IS NOT NULL ORDER BY name COLLATE BINARY;",
        label + " schema prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    while (true) {
        const int result = step_or_throw(
            db, statement.stmt, &budget, label + " schema step");
        if (result == SQLITE_DONE) break;
        budget.consume_row();
        ObservedSqliteSchemaObject object;
        object.type = sqlite_exact_text_or_throw(
            statement.stmt, 0, label + " schema type", 16);
        object.name = sqlite_exact_text_or_throw(
            statement.stmt, 1, label + " schema name", 255);
        object.table_name = sqlite_exact_text_or_throw(
            statement.stmt, 2, label + " schema table", 255);
        object.stored_sql = sqlite_exact_text_or_throw(
            statement.stmt, 3, label + " schema SQL", kMaximumSchemaSqlBytes);
        budget.consume_text_row(
            {object.type, object.name, object.table_name, object.stored_sql});
        budget.consume_retained_text(
            {object.type, object.name, object.table_name, object.stored_sql});
        observed.push_back(std::move(object));
        if (observed.size() > contract.size()) break;
    }
    const SqliteReplayLedgerSchemaVerification verification =
        verify_sqlite_replay_ledger_schema(observed);
    if (!verification) {
        throw std::runtime_error(label + " exact schema rejected: " +
                                 verification.safe_summary());
    }
}

void verify_backend_profile_or_throw(SyncSqliteDbHandleSlot& owner,
                                     const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        owner,
        "SELECT backend_name, schema_version, hash_algorithm, "
        "entry_material_version, commit_protocol FROM backend_profile WHERE id=1;",
        label + " backend profile prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    require_single_row(db, statement.stmt, label + " backend profile");
    const std::string backend = sqlite_exact_text_or_throw(
        statement.stmt, 0, label + " backend name", 32);
    const std::int64_t schema_version = sqlite_exact_i64_or_throw(
        statement.stmt, 1, label + " schema version");
    const std::string hash_algorithm = sqlite_exact_text_or_throw(
        statement.stmt, 2, label + " hash algorithm", 32);
    const std::string material_version = sqlite_exact_text_or_throw(
        statement.stmt, 3, label + " material version", 256);
    const std::string commit_protocol = sqlite_exact_text_or_throw(
        statement.stmt, 4, label + " commit protocol", 128);
    require_statement_done(db, statement.stmt, label + " backend profile");
    if (backend != kSqliteReplayLedgerBackendName ||
        schema_version != kSqliteReplayLedgerSchemaVersion ||
        hash_algorithm != kSqliteReplayLedgerHashAlgorithm ||
        material_version != kSqliteReplayLedgerEntryMaterialVersion ||
        commit_protocol != kSqliteReplayLedgerCommitProtocol) {
        throw std::runtime_error(label + " backend profile mismatch");
    }
}

void verify_integrity_or_throw(SyncSqliteDbHandleSlot& owner,
                               SqliteVerificationBudget& budget,
                               const std::string& label) {
    SyncSqliteStmt integrity = sqlite_prepare_or_throw(
        owner, "PRAGMA integrity_check;", label + " integrity_check prepare");
    sqlite3* db = sqlite3_db_handle(integrity.stmt);
    if (step_or_throw(db, integrity.stmt, &budget,
                      label + " integrity_check step") != SQLITE_ROW) {
        throw std::runtime_error(label + " integrity_check returned no row");
    }
    budget.consume_row();
    const std::string result = sqlite_exact_text_or_throw(
        integrity.stmt, 0, label + " integrity_check result", 4096);
    budget.consume_text_row({result});
    if (result != "ok") {
        throw std::runtime_error(label + " integrity_check rejected durable state");
    }
    if (step_or_throw(db, integrity.stmt, &budget,
                      label + " integrity_check terminal step") != SQLITE_DONE) {
        throw std::runtime_error(label + " integrity_check returned multiple rows");
    }

    SyncSqliteStmt foreign_keys = sqlite_prepare_or_throw(
        owner, "PRAGMA foreign_key_check;",
        label + " foreign_key_check prepare");
    db = sqlite3_db_handle(foreign_keys.stmt);
    const int foreign_key_result = step_or_throw(
        db, foreign_keys.stmt, &budget, label + " foreign_key_check step");
    if (foreign_key_result != SQLITE_DONE) {
        throw std::runtime_error(label + " foreign_key_check reported a violation");
    }
}

void configure_connection_or_throw(SyncSqliteDbHandleSlot& owner,
                                   bool query_only,
                                   const std::string& label) {
    sqlite3* db = owner.get();
    if (sqlite3_extended_result_codes(db, 1) != SQLITE_OK) {
        throw std::runtime_error(label + " could not enable extended result codes");
    }
    sqlite_set_busy_timeout_or_throw(
        owner, 1000, label + " busy timeout");
#ifdef SQLITE_DBCONFIG_TRUSTED_SCHEMA
    int trusted_schema_out = 0;
    if (sqlite3_db_config(db, SQLITE_DBCONFIG_TRUSTED_SCHEMA, 0,
                          &trusted_schema_out) != SQLITE_OK ||
        trusted_schema_out != 0) {
        throw std::runtime_error(label + " could not disable trusted_schema");
    }
#endif
#ifdef SQLITE_DBCONFIG_DEFENSIVE
    int defensive_out = 0;
    if (sqlite3_db_config(db, SQLITE_DBCONFIG_DEFENSIVE, 1,
                          &defensive_out) != SQLITE_OK ||
        defensive_out != 1) {
        throw std::runtime_error(label + " could not enable defensive mode");
    }
#endif
    const std::string journal_mode = query_single_text(
        owner, "PRAGMA journal_mode;", label + " journal_mode", 32);
    if (journal_mode != "wal") {
        throw std::runtime_error(label + " requires the existing WAL journal profile");
    }
    sqlite_exec_or_throw(owner, "PRAGMA synchronous=FULL;",
                         label + " synchronous configuration");
    sqlite_exec_or_throw(owner, "PRAGMA foreign_keys=ON;",
                         label + " foreign_keys configuration");
    sqlite_exec_or_throw(owner, "PRAGMA trusted_schema=OFF;",
                         label + " trusted_schema configuration");
    sqlite_exec_or_throw(owner, "PRAGMA ignore_check_constraints=OFF;",
                         label + " check-constraint configuration");
    sqlite_exec_or_throw(owner, "PRAGMA cell_size_check=ON;",
                         label + " cell-size configuration");
    sqlite_exec_or_throw(owner, "PRAGMA mmap_size=0;",
                         label + " mmap configuration");
    sqlite_exec_or_throw(owner,
                         query_only ? "PRAGMA query_only=ON;"
                                    : "PRAGMA query_only=OFF;",
                         label + " query-only configuration");
    if (query_single_i64(owner, "PRAGMA synchronous;",
                         label + " synchronous verification") != 2 ||
        query_single_i64(owner, "PRAGMA foreign_keys;",
                         label + " foreign_keys verification") != 1 ||
        query_single_i64(owner, "PRAGMA trusted_schema;",
                         label + " trusted_schema verification") != 0 ||
        query_single_i64(owner, "PRAGMA ignore_check_constraints;",
                         label + " check-constraint verification") != 0 ||
        query_single_i64(owner, "PRAGMA cell_size_check;",
                         label + " cell-size verification") != 1 ||
        query_single_i64(owner, "PRAGMA mmap_size;",
                         label + " mmap verification") != 0 ||
        query_single_i64(owner, "PRAGMA query_only;",
                         label + " query-only verification") !=
            (query_only ? 1 : 0)) {
        throw std::runtime_error(label + " SQLite connection profile mismatch");
    }
}

[[nodiscard]] std::pair<std::int64_t, std::string> query_metadata(
    SyncSqliteDbHandleSlot& owner,
    const std::string& table,
    const std::string& label) {
    const std::string sql =
        "SELECT line_count, head_hash FROM " + table + " WHERE id=1;";
    SyncSqliteStmt statement = sqlite_prepare_or_throw(owner, sql, label + " prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    require_single_row(db, statement.stmt, label);
    const std::int64_t line_count =
        sqlite_exact_i64_or_throw(statement.stmt, 0, label + " line_count");
    const std::string head_hash = sqlite_exact_text_or_throw(
        statement.stmt, 1, label + " head_hash", 64);
    require_statement_done(db, statement.stmt, label);
    validate_chain_summary_or_throw(line_count, head_hash, label);
    return {line_count, head_hash};
}

[[nodiscard]] std::int64_t digest_table(
    SyncSqliteDbHandleSlot& owner,
    SqliteVerificationBudget& budget,
    Sha256DigestBuilder& digest,
    std::string_view table_name,
    std::string_view sql,
    std::span<const DigestColumn> columns,
    const std::string& label) {
    digest_token(digest, "table", table_name);
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        owner, std::string(sql), label + " prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    if (sqlite3_column_count(statement.stmt) !=
        static_cast<int>(columns.size())) {
        throw std::logic_error(label + " canonical query column count mismatch");
    }
    std::int64_t row_count = 0;
    while (true) {
        const int result = step_or_throw(db, statement.stmt, &budget,
                                         label + " step");
        if (result == SQLITE_DONE) break;
        budget.consume_row();
        budget.checkpoint();
        if (row_count == std::numeric_limits<std::int64_t>::max()) {
            throw std::overflow_error(label + " row count overflow");
        }
        ++row_count;
        digest_integer(digest, "row", row_count);
        for (std::size_t index = 0; index < columns.size(); ++index) {
            const DigestColumn& column = columns[index];
            const int sqlite_index = static_cast<int>(index);
            digest_token(digest, "column", column.name);
            if (column.storage_class == DigestStorageClass::Integer) {
                digest_token(digest, "storage", "integer");
                const std::int64_t value = sqlite_exact_i64_or_throw(
                    statement.stmt, sqlite_index,
                    label + " " + std::string(column.name));
                digest_integer(digest, "value", value);
            } else {
                digest_token(digest, "storage", "text");
                const std::string value = sqlite_exact_text_or_throw(
                    statement.stmt, sqlite_index,
                    label + " " + std::string(column.name),
                    column.maximum_text_bytes);
                budget.consume_decoded_text_bytes(value.size());
                digest_token(digest, "value", value);
            }
        }
    }
    digest_integer(digest, "rows", row_count);
    return row_count;
}

[[nodiscard]] LedgerState query_canonical_state(
    SyncSqliteDbHandleSlot& owner,
    SqliteVerificationBudget& budget,
    const std::filesystem::path& normalized_path,
    const std::string& label) {
    sqlite3* db = owner.get();
    if (sqlite3_get_autocommit(db) != 0 ||
        sqlite3_txn_state(db, "main") == SQLITE_TXN_NONE) {
        throw std::logic_error(label + " requires an active pinned transaction");
    }

    Sha256DigestBuilder digest;
    digest_token(digest, "format", kLogicalStateDigestFormat);
    digest_integer(digest, "schema_version",
                   kSqliteReplayLedgerSchemaVersion);

    const std::int64_t backend_rows = digest_table(
        owner, budget, digest, "backend_profile",
        "SELECT id, backend_name, schema_version, hash_algorithm, "
        "entry_material_version, commit_protocol FROM backend_profile ORDER BY id;",
        kBackendProfileColumns, label + " backend_profile");
    const std::int64_t identity_rows = digest_table(
        owner, budget, digest, "ledger_identity",
        "SELECT id, ledger_instance_id FROM ledger_identity ORDER BY id;",
        kLedgerIdentityColumns, label + " ledger_identity");
    const std::int64_t metadata_rows = digest_table(
        owner, budget, digest, "metadata",
        "SELECT id, line_count, head_hash FROM metadata ORDER BY id;",
        kMetadataColumns, label + " metadata");
    const std::int64_t transition_metadata_rows = digest_table(
        owner, budget, digest, "effect_transition_metadata",
        "SELECT id, line_count, head_hash FROM effect_transition_metadata ORDER BY id;",
        kMetadataColumns, label + " effect_transition_metadata");
    const std::int64_t ledger_entry_rows = digest_table(
        owner, budget, digest, "ledger_entries",
        "SELECT sequence, previous_hash, entry_hash, case_id, kind, operation_id, "
        "contract_digest_sha256, jti, action, cloud_event_source, cloud_event_id, "
        "effect_idempotency_key, effect_state FROM ledger_entries ORDER BY sequence;",
        kLedgerEntryColumns, label + " ledger_entries");
    const std::int64_t transition_rows = digest_table(
        owner, budget, digest, "effect_transitions",
        "SELECT sequence, previous_hash, transition_hash, ledger_instance_id, "
        "effect_idempotency_key, prepared_sequence, prepared_entry_hash, "
        "terminal_state, result_digest_sha256, transition_reason, "
        "transition_intent_id, transition_intent_signer_kid, "
        "transition_intent_sha256 FROM effect_transitions ORDER BY sequence;",
        kEffectTransitionColumns, label + " effect_transitions");
    const std::int64_t outbox_rows = digest_table(
        owner, budget, digest, "effect_outbox",
        "SELECT effect_idempotency_key, prepared_sequence, prepared_entry_hash, "
        "outbox_state, dispatch_attempts, worker_claim_id, worker_id, "
        "claimed_at_epoch, lease_expires_at_epoch, last_result_digest_sha256, "
        "updated_at_sequence FROM effect_outbox "
        "ORDER BY effect_idempotency_key COLLATE BINARY;",
        kEffectOutboxColumns, label + " effect_outbox");
    const std::int64_t ingress_rows = digest_table(
        owner, budget, digest, "ingress_sender_replay_cache",
        "SELECT replay_key_sha256, format, service_config_sha256, "
        "ingress_profile_sha256, sender_replay_cache_instance_id, "
        "sender_proof_kid, principal, nonce, issued_at_epoch, observed_at_epoch, "
        "replay_window_seconds, material_sha256, prepared_sequence, "
        "prepared_entry_hash, effect_idempotency_key "
        "FROM ingress_sender_replay_cache "
        "ORDER BY replay_key_sha256 COLLATE BINARY;",
        kIngressReplayColumns, label + " ingress_sender_replay_cache");

    if (backend_rows != 1 || identity_rows != 1 || metadata_rows != 1 ||
        transition_metadata_rows != 1) {
        throw std::runtime_error(label + " singleton table cardinality mismatch");
    }

    LedgerState state;
    state.public_state.normalized_ledger_path = normalized_path.generic_string();
    state.public_state.ledger_instance_id = query_single_text(
        owner,
        "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;",
        label + " ledger identity", 64);
    if (!is_lowercase_sha256_hex(state.public_state.ledger_instance_id)) {
        throw std::runtime_error(label + " durable ledger identity is invalid");
    }
    const auto decision_metadata = query_metadata(owner, "metadata",
                                                   label + " decision metadata");
    state.public_state.durable_line_count = decision_metadata.first;
    state.public_state.durable_head_hash = decision_metadata.second;
    const auto transition_metadata = query_metadata(
        owner, "effect_transition_metadata",
        label + " transition metadata");
    state.public_state.effect_transition_line_count = transition_metadata.first;
    state.public_state.effect_transition_head_hash = transition_metadata.second;
    state.public_state.ledger_entry_rows = ledger_entry_rows;
    state.public_state.effect_transition_rows = transition_rows;
    state.public_state.effect_outbox_rows = outbox_rows;
    state.public_state.ingress_sender_replay_rows = ingress_rows;
    state.public_state.connection_owner_generation = owner.borrow().generation();
    if (state.public_state.durable_line_count != ledger_entry_rows ||
        state.public_state.effect_transition_line_count != transition_rows) {
        throw std::runtime_error(label +
                                 " durable metadata/table cardinality mismatch");
    }
    state.public_state.state_sha256 = digest.finish_hex();
    return state;
}

[[nodiscard]] bool expectation_matches_state(
    const SqliteReplayLedgerResetExpectation& expected,
    const SqliteReplayLedgerResetState& observed) noexcept {
    return expected.namespace_identity == observed.namespace_identity &&
           expected.ledger_instance_id == observed.ledger_instance_id &&
           expected.state_sha256 == observed.state_sha256 &&
           expected.durable_line_count == observed.durable_line_count &&
           expected.durable_head_hash == observed.durable_head_hash &&
           expected.effect_transition_line_count ==
               observed.effect_transition_line_count &&
           expected.effect_transition_head_hash ==
               observed.effect_transition_head_hash &&
           expected.ledger_entry_rows == observed.ledger_entry_rows &&
           expected.effect_transition_rows ==
               observed.effect_transition_rows &&
           expected.effect_outbox_rows == observed.effect_outbox_rows &&
           expected.ingress_sender_replay_rows ==
               observed.ingress_sender_replay_rows;
}

[[nodiscard]] bool is_complete_empty_postcondition(
    SyncSqliteDbHandleSlot& owner,
    const std::string& receipt,
    const std::string& label) {
    const std::string identity = query_single_text(
        owner,
        "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;",
        label + " identity", 64);
    const auto decision = query_metadata(owner, "metadata",
                                         label + " decision metadata");
    const auto transition = query_metadata(
        owner, "effect_transition_metadata",
        label + " transition metadata");
    const std::int64_t operational_rows = query_single_i64(
        owner,
        "SELECT (SELECT count(*) FROM ledger_entries) + "
        "(SELECT count(*) FROM effect_transitions) + "
        "(SELECT count(*) FROM effect_outbox) + "
        "(SELECT count(*) FROM ingress_sender_replay_cache);",
        label + " operational row count");
    return identity == receipt && decision.first == 0 &&
           decision.second == "GENESIS" && transition.first == 0 &&
           transition.second == "GENESIS" && operational_rows == 0;
}

void execute_expected_delete(SyncSqliteDbHandleSlot& owner,
                             const std::string& table,
                             std::int64_t expected_rows,
                             const std::string& label) {
    sqlite3* db = owner.get();
    sqlite_exec_or_throw(owner, "DELETE FROM " + table + ";", label);
    if (sqlite3_changes64(db) != expected_rows) {
        throw std::runtime_error(label + " changed an unexpected row count");
    }
}

void reset_metadata_row(SyncSqliteDbHandleSlot& owner,
                        const std::string& table,
                        std::int64_t expected_count,
                        const std::string& expected_head,
                        const std::string& label) {
    const std::string sql =
        "UPDATE " + table +
        " SET line_count=0, head_hash='GENESIS' "
        "WHERE id=1 AND line_count=?1 AND head_hash=?2;";
    SyncSqliteStmt statement = sqlite_prepare_or_throw(owner, sql, label + " prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    sqlite_bind_u64_or_throw(
        statement.stmt, 1, static_cast<std::uint64_t>(expected_count),
        label + " count bind");
    sqlite_bind_text_or_throw(statement.stmt, 2, expected_head,
                              label + " head bind");
    sqlite_step_done_or_throw(statement.stmt, label + " step");
    if (sqlite3_changes64(db) != 1) {
        throw std::runtime_error(label + " lost exact metadata precondition");
    }
}

void rotate_identity(SyncSqliteDbHandleSlot& owner,
                     const std::string& expected_identity,
                     const std::string& receipt,
                     const std::string& label) {
    SyncSqliteStmt statement = sqlite_prepare_or_throw(
        owner,
        "UPDATE ledger_identity SET ledger_instance_id=?1 "
        "WHERE id=1 AND ledger_instance_id=?2;",
        label + " prepare");
    sqlite3* db = sqlite3_db_handle(statement.stmt);
    sqlite_bind_text_or_throw(statement.stmt, 1, receipt,
                              label + " receipt bind");
    sqlite_bind_text_or_throw(statement.stmt, 2, expected_identity,
                              label + " prior identity bind");
    sqlite_step_done_or_throw(statement.stmt, label + " step");
    if (sqlite3_changes64(db) != 1) {
        throw std::runtime_error(label + " lost exact identity precondition");
    }
}

[[nodiscard]] std::string receipt_digest_material_sha256(
    const SqliteReplayLedgerResetRequest& request) {
    const std::string normalized_path =
        normalized_absolute_path_or_throw(request.ledger_path, true)
            .generic_string();
    const std::string reason_sha256 = sha256_hex(request.reason);
    Sha256DigestBuilder digest;
    digest_token(digest, "format", kResetReceiptDigestFormat);
    digest_integer(digest, "schema_version",
                   kSqliteReplayLedgerSchemaVersion);
    digest_token(digest, "ledger_path", normalized_path);
    digest_token(digest, "reset_intent_id", request.reset_intent_id);
    digest_token(digest, "operator_id", request.operator_id);
    digest_token(digest, "reason_sha256", reason_sha256);
    digest_unsigned_integer(
        digest, "expected_parent_device",
        request.expected.namespace_identity.parent_device);
    digest_unsigned_integer(
        digest, "expected_parent_inode",
        request.expected.namespace_identity.parent_inode);
    digest_unsigned_integer(
        digest, "expected_database_device",
        request.expected.namespace_identity.database_device);
    digest_unsigned_integer(
        digest, "expected_database_inode",
        request.expected.namespace_identity.database_inode);
    digest_token(digest, "expected_ledger_instance_id",
                 request.expected.ledger_instance_id);
    digest_token(digest, "expected_state_sha256",
                 request.expected.state_sha256);
    digest_integer(digest, "expected_durable_line_count",
                   request.expected.durable_line_count);
    digest_token(digest, "expected_durable_head_hash",
                 request.expected.durable_head_hash);
    digest_integer(digest, "expected_effect_transition_line_count",
                   request.expected.effect_transition_line_count);
    digest_token(digest, "expected_effect_transition_head_hash",
                 request.expected.effect_transition_head_hash);
    digest_integer(digest, "expected_ledger_entry_rows",
                   request.expected.ledger_entry_rows);
    digest_integer(digest, "expected_effect_transition_rows",
                   request.expected.effect_transition_rows);
    digest_integer(digest, "expected_effect_outbox_rows",
                   request.expected.effect_outbox_rows);
    digest_integer(digest, "expected_ingress_sender_replay_rows",
                   request.expected.ingress_sender_replay_rows);
    return digest.finish_hex();
}

void open_existing_ledger_or_throw(const std::filesystem::path& normalized_path,
                                   SyncSqliteDbHandleSlot& owner,
                                   SqlitePathFamilyGuard& path_guard,
                                   bool query_only,
                                   const std::string& label) {
    path_guard.verify_family_or_throw(label + " pre-open namespace gate");
    require_sync_sqlite_wal_runtime_safe_or_throw(label + " runtime gate");
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int open_result = sqlite3_open_v2(
        normalized_path.c_str(), owner.out(), flags, nullptr);
    if (open_result != SQLITE_OK) {
        throw_sqlite_exception(owner, open_result, label + " open");
    }
    sqlite3* db = owner.get();
    path_guard.verify_open_database_or_throw(db, label + " open identity gate");
    if (sqlite3_db_readonly(db, "main") != 0) {
        throw std::runtime_error(label + " requires a writable main database");
    }
    configure_connection_or_throw(owner, query_only, label);
}

}  // namespace

SqliteReplayLedgerResetDurableOutcomeError::
    SqliteReplayLedgerResetDurableOutcomeError(
        SqliteReplayLedgerResetOutcome outcome,
        std::string reset_receipt_sha256)
    : std::runtime_error(
          "sqlite-wal replay ledger reset produced a durable outcome but post-commit verification did not complete"),
      outcome_(outcome),
      reset_receipt_sha256_(std::move(reset_receipt_sha256)) {}

SqliteReplayLedgerResetOutcome
SqliteReplayLedgerResetDurableOutcomeError::outcome() const noexcept {
    return outcome_;
}

const std::string&
SqliteReplayLedgerResetDurableOutcomeError::reset_receipt_sha256() const noexcept {
    return reset_receipt_sha256_;
}

SqliteReplayLedgerResetState inspect_sqlite_replay_ledger_reset_state(
    const std::filesystem::path& ledger_path) {
    const std::filesystem::path normalized_path =
        normalized_absolute_path_or_throw(ledger_path, false);
    const std::string label =
        "sqlite-wal replay ledger reset-state inspection";
    SqliteReplayLedgerWriteGate write_gate(
        normalized_path,
        SqliteReplayLedgerWriteGateNesting::RejectSameThread,
        SqliteReplayLedgerWriteGateParentPolicy::RequireExistingParent);
    if (!write_gate.owns_exclusive_gate()) {
        throw std::logic_error(label + " did not acquire its exclusive write gate");
    }
    SqlitePathFamilyGuard path_guard = guard_sqlite_path_family_or_throw(
        normalized_path, false,
        {"-wal", "-shm", "-journal", ".write.lock"}, label);
    if (!path_guard.parent_exists() ||
        !path_guard.database_existed_at_preflight()) {
        throw std::runtime_error(label + " requires an existing ledger database");
    }
    SyncSqliteDbHandleSlot owner;
    open_existing_ledger_or_throw(normalized_path, owner, path_guard, true,
                                  label);
    sqlite3* db = owner.get();
    SqliteVerificationBudget budget(
        borrow_sync_sqlite_serialized_db_or_throw(
            owner, label + " verification generation"),
        label);
    SqliteReplayLedgerResetState state;
    {
        SyncSqliteTransaction transaction(
            owner, label, SyncSqliteTransactionMode::Deferred);
        verify_exact_schema_or_throw(owner, budget, label);
        if (!transaction.authorizes_snapshot(db)) {
            throw std::logic_error(label + " did not pin a read snapshot");
        }
        verify_backend_profile_or_throw(owner, label);
        verify_integrity_or_throw(owner, budget, label);
        path_guard.verify_family_or_throw(label + " transaction namespace gate");
        path_guard.verify_open_database_or_throw(
            db, label + " transaction open identity gate");
        state = query_canonical_state(owner, budget, normalized_path, label)
                    .public_state;
        state.namespace_identity =
            path_guard.bound_path_identity_or_throw(
                label + " canonical namespace identity");
        if (state.connection_owner_generation != owner.borrow().generation()) {
            throw std::logic_error(label + " connection owner generation changed");
        }
        transaction.commit();
    }
    if (sqlite3_get_autocommit(db) == 0 ||
        sqlite3_txn_state(db, "main") != SQLITE_TXN_NONE) {
        throw std::logic_error(label + " left a transaction active");
    }
    path_guard.verify_open_database_or_throw(db, label + " final identity gate");
    return state;
}

std::string sqlite_replay_ledger_reset_receipt_sha256(
    const SqliteReplayLedgerResetRequest& request) {
    validate_request_or_throw(request);
    return receipt_digest_material_sha256(request);
}

SqliteReplayLedgerResetResult reset_sqlite_replay_ledger(
    const SqliteReplayLedgerResetRequest& request,
    SqliteReplayLedgerResetObserver observer,
    void* observer_context) {
    validate_request_or_throw(request);
    const std::filesystem::path normalized_path =
        normalized_absolute_path_or_throw(request.ledger_path, true);
    const std::string receipt =
        sqlite_replay_ledger_reset_receipt_sha256(request);
    if (receipt == request.expected.ledger_instance_id) {
        throw std::runtime_error(
            "sqlite-wal replay ledger reset receipt collides with prior identity");
    }
    const std::string label =
        "sqlite-wal replay ledger administrative reset";

    SqliteReplayLedgerWriteGate write_gate(
        normalized_path,
        SqliteReplayLedgerWriteGateNesting::RejectSameThread,
        SqliteReplayLedgerWriteGateParentPolicy::RequireExistingParent);
    if (!write_gate.owns_exclusive_gate()) {
        throw std::logic_error(label + " did not acquire its exclusive write gate");
    }
    SqlitePathFamilyGuard path_guard = guard_sqlite_path_family_or_throw(
        normalized_path, false,
        {"-wal", "-shm", "-journal", ".write.lock"}, label);
    if (!path_guard.parent_exists() ||
        !path_guard.database_existed_at_preflight()) {
        throw std::runtime_error(label + " requires an existing ledger database");
    }
    const SqlitePathIdentity namespace_identity =
        path_guard.bound_path_identity_or_throw(
            label + " request namespace precondition");
    if (!(namespace_identity == request.expected.namespace_identity)) {
        throw std::runtime_error(
            label + " exact SQLite namespace precondition mismatch");
    }
    SyncSqliteDbHandleSlot owner;
    open_existing_ledger_or_throw(normalized_path, owner, path_guard, false,
                                  label);
    sqlite3* db = owner.get();
    const std::uint64_t owner_generation = owner.borrow().generation();
    SqliteVerificationBudget budget(
        borrow_sync_sqlite_serialized_db_or_throw(
            owner, label + " verification generation"),
        label);

    SqliteReplayLedgerResetResult result;
    result.prior = request.expected;
    result.normalized_ledger_path = normalized_path.generic_string();
    result.new_ledger_instance_id = receipt;
    result.reset_receipt_sha256 = receipt;
    result.reason_sha256 = sha256_hex(request.reason);
    result.connection_owner_generation = owner_generation;

    bool committed_mutation = false;
    {
        SyncSqliteTransaction transaction(
            owner, label, SyncSqliteTransactionMode::Immediate);
        if (!transaction.authorizes_write(db)) {
            throw std::logic_error(label +
                                   " typed transaction did not mint write authority");
        }
        path_guard.verify_family_or_throw(label + " transaction namespace gate");
        path_guard.verify_open_database_or_throw(
            db, label + " transaction open identity gate");
        if (owner.borrow().generation() != owner_generation) {
            throw std::logic_error(label + " connection owner generation changed");
        }
        verify_exact_schema_or_throw(owner, budget, label);
        verify_backend_profile_or_throw(owner, label);
        verify_integrity_or_throw(owner, budget, label);

        SqliteReplayLedgerResetState observed =
            query_canonical_state(owner, budget, normalized_path, label)
                .public_state;
        observed.namespace_identity =
            path_guard.bound_path_identity_or_throw(
                label + " transaction namespace identity");
        if (observed.ledger_instance_id == receipt) {
            result.state_advanced_after_commit =
                !is_complete_empty_postcondition(
                    owner, receipt, label + " idempotent replay");
            transaction.commit();
            result.outcome = SqliteReplayLedgerResetOutcome::AlreadyCommitted;
        } else {
            if (!expectation_matches_state(request.expected, observed)) {
                throw std::runtime_error(
                    label + " exact prior logical-state precondition mismatch");
            }

            execute_expected_delete(
                owner, "effect_transitions", observed.effect_transition_rows,
                label + " delete effect_transitions");
            execute_expected_delete(
                owner, "effect_outbox", observed.effect_outbox_rows,
                label + " delete effect_outbox");
            execute_expected_delete(
                owner, "ingress_sender_replay_cache",
                observed.ingress_sender_replay_rows,
                label + " delete ingress_sender_replay_cache");
            execute_expected_delete(
                owner, "ledger_entries", observed.ledger_entry_rows,
                label + " delete ledger_entries");
            reset_metadata_row(
                owner, "effect_transition_metadata",
                observed.effect_transition_line_count,
                observed.effect_transition_head_hash,
                label + " reset transition metadata");
            reset_metadata_row(
                owner, "metadata", observed.durable_line_count,
                observed.durable_head_hash,
                label + " reset ledger metadata");
            rotate_identity(
                owner, observed.ledger_instance_id, receipt,
                label + " rotate identity receipt");

            if (!is_complete_empty_postcondition(
                    owner, receipt, label + " transaction postcondition")) {
                throw std::logic_error(
                    label + " failed its in-transaction postcondition");
            }
            if (!transaction.authorizes_write(db)) {
                throw std::logic_error(
                    label + " write authority expired before commit");
            }
            transaction.commit();
            committed_mutation = true;
            result.outcome = SqliteReplayLedgerResetOutcome::Committed;
        }
    }

    budget.detach();
    try {
        if (observer != nullptr) {
            observer(
                SqliteReplayLedgerResetCutpoint::
                    DurableOutcomeObservedBeforePostcommitVerification,
                observer_context);
        }
        if (sqlite3_get_autocommit(db) == 0 ||
            sqlite3_txn_state(db, "main") != SQLITE_TXN_NONE) {
            throw std::logic_error(
                label + " left a transaction active after commit");
        }
        path_guard.verify_family_or_throw(
            label + " post-commit namespace gate");
        path_guard.verify_open_database_or_throw(
            db, label + " post-commit identity gate");
        if (committed_mutation) {
            SqliteVerificationBudget postcommit_budget(
                borrow_sync_sqlite_serialized_db_or_throw(
                    owner, label + " post-commit verification generation"),
                label + " post-commit");
            verify_integrity_or_throw(
                owner, postcommit_budget, label + " post-commit");
            if (!is_complete_empty_postcondition(
                    owner, receipt, label + " committed postcondition")) {
                throw std::runtime_error(
                    label + " committed postcondition is incomplete");
            }
        } else {
            const std::string current_identity = query_single_text(
                owner,
                "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;",
                label + " recovered receipt identity", 64);
            if (current_identity != receipt) {
                throw std::runtime_error(
                    label + " durable receipt identity changed during recovery");
            }
        }
        if (owner.borrow().generation() != owner_generation) {
            throw std::logic_error(
                label +
                " connection owner generation changed after commit");
        }
    } catch (...) {
        std::throw_with_nested(SqliteReplayLedgerResetDurableOutcomeError(
            result.outcome, receipt));
    }
    return result;
}

}  // namespace anonsync::persistence
