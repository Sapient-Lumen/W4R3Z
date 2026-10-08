#pragma once

#include "sqlite_replay_ledger_reset.hpp"
#include "sqlite_replay_ledger_schema_contract.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <filesystem>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync::test::sqlite_replay_ledger_reset_fixture {

namespace fs = std::filesystem;

inline constexpr std::string_view kInitialIdentity =
    "9999999999999999999999999999999999999999999999999999999999999999";
inline constexpr std::string_view kEntryHash =
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
inline constexpr std::string_view kContractHash =
    "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
inline constexpr std::string_view kEffectKey =
    "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc";
inline constexpr std::string_view kResultHash =
    "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd";
inline constexpr std::string_view kTransitionHash =
    "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee";
inline constexpr std::string_view kIntentHash =
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff";
inline constexpr std::string_view kReplayKey =
    "1111111111111111111111111111111111111111111111111111111111111111";
inline constexpr std::string_view kServiceHash =
    "2222222222222222222222222222222222222222222222222222222222222222";
inline constexpr std::string_view kProfileHash =
    "3333333333333333333333333333333333333333333333333333333333333333";
inline constexpr std::string_view kMaterialHash =
    "4444444444444444444444444444444444444444444444444444444444444444";

class Database final {
public:
    Database(const fs::path& path, int flags) {
        int open_flags = flags | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        open_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        const int result = sqlite3_open_v2(path.c_str(), &database_, open_flags,
                                           nullptr);
        if (result != SQLITE_OK) {
            const std::string reason = database_ != nullptr
                                           ? sqlite3_errmsg(database_)
                                           : "SQLite open failed";
            if (database_ != nullptr) (void)sqlite3_close_v2(database_);
            database_ = nullptr;
            throw std::runtime_error(reason);
        }
        if (sqlite3_busy_timeout(database_, 2000) != SQLITE_OK) {
            const std::string reason = sqlite3_errmsg(database_);
            (void)sqlite3_close_v2(database_);
            database_ = nullptr;
            throw std::runtime_error(
                "could not install SQLite busy timeout: " + reason);
        }
    }

    ~Database() {
        if (database_ != nullptr) (void)sqlite3_close_v2(database_);
    }

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    void exec(const std::string& sql) const {
        char* error = nullptr;
        const int result =
            sqlite3_exec(database_, sql.c_str(), nullptr, nullptr, &error);
        if (result != SQLITE_OK) {
            const std::string reason =
                error != nullptr ? error : sqlite3_errmsg(database_);
            sqlite3_free(error);
            throw std::runtime_error(reason);
        }
    }

    [[nodiscard]] std::string text(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(database_, sql.c_str(), -1, &statement, nullptr) !=
            SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database_));
        }
        const int first = sqlite3_step(statement);
        if (first != SQLITE_ROW ||
            sqlite3_column_type(statement, 0) != SQLITE_TEXT) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("text query did not return one text value");
        }
        const unsigned char* value = sqlite3_column_text(statement, 0);
        const int bytes = sqlite3_column_bytes(statement, 0);
        if (value == nullptr || bytes < 0) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("text query returned invalid bytes");
        }
        std::string result(
            reinterpret_cast<const char*>(value),
            static_cast<std::size_t>(bytes));
        if (sqlite3_step(statement) != SQLITE_DONE) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("text query returned extra rows");
        }
        if (sqlite3_finalize(statement) != SQLITE_OK) {
            throw std::runtime_error("text query finalize failed");
        }
        return result;
    }

    [[nodiscard]] std::int64_t integer(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(database_, sql.c_str(), -1, &statement, nullptr) !=
            SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database_));
        }
        const int first = sqlite3_step(statement);
        if (first != SQLITE_ROW ||
            sqlite3_column_type(statement, 0) != SQLITE_INTEGER) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error(
                "integer query did not return one integer");
        }
        const std::int64_t value = sqlite3_column_int64(statement, 0);
        if (sqlite3_step(statement) != SQLITE_DONE) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("integer query returned extra rows");
        }
        if (sqlite3_finalize(statement) != SQLITE_OK) {
            throw std::runtime_error("integer query finalize failed");
        }
        return value;
    }

private:
    sqlite3* database_ = nullptr;
};

inline void cleanup_family(const fs::path& path) {
    for (const std::string_view suffix :
         {"", "-wal", "-shm", "-journal", ".write.lock"}) {
        std::error_code ignored;
        fs::remove(fs::path(path.string() + std::string(suffix)), ignored);
    }
}

inline void create_schema(Database& database) {
    database.exec("PRAGMA journal_mode=WAL;");
    database.exec("PRAGMA synchronous=FULL;");
    database.exec("PRAGMA foreign_keys=ON;");
    for (const auto& definition :
         persistence::sqlite_replay_ledger_schema_contract()) {
        database.exec(
            persistence::sqlite_replay_ledger_schema_create_statement(definition));
    }
    database.exec(
        "INSERT INTO backend_profile(id, backend_name, schema_version, "
        "hash_algorithm, entry_material_version, commit_protocol) VALUES("
        "1, 'sqlite-wal', 10, 'sha256', "
        "'anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent', "
        "'sqlite-wal-begin-immediate-full-sync');");
}

inline void seed_nonempty_ledger(const fs::path& path) {
    cleanup_family(path);
    Database database(path, SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE);
    create_schema(database);
    database.exec("INSERT INTO ledger_identity(id, ledger_instance_id) VALUES(1, '" +
                  std::string(kInitialIdentity) + "');");
    database.exec("INSERT INTO metadata(id, line_count, head_hash) VALUES(1, 1, '" +
                  std::string(kEntryHash) + "');");
    database.exec(
        "INSERT INTO effect_transition_metadata(id, line_count, head_hash) "
        "VALUES(1, 1, '" + std::string(kTransitionHash) + "');");
    database.exec(
        "INSERT INTO ledger_entries(sequence, previous_hash, entry_hash, case_id, "
        "kind, operation_id, contract_digest_sha256, jti, action, "
        "cloud_event_source, cloud_event_id, effect_idempotency_key, effect_state) "
        "VALUES(1, 'GENESIS', '" + std::string(kEntryHash) +
        "', 'case-one', 'openapi', 'operation-one', '" +
        std::string(kContractHash) +
        "', 'jti-one', 'allow', '', '', '" + std::string(kEffectKey) +
        "', 'prepared');");
    database.exec(
        "INSERT INTO effect_transitions(sequence, previous_hash, transition_hash, "
        "ledger_instance_id, effect_idempotency_key, prepared_sequence, "
        "prepared_entry_hash, terminal_state, result_digest_sha256, "
        "transition_reason, transition_intent_id, transition_intent_signer_kid, "
        "transition_intent_sha256) VALUES(1, 'GENESIS', '" +
        std::string(kTransitionHash) + "', '" + std::string(kInitialIdentity) +
        "', '" + std::string(kEffectKey) + "', 1, '" +
        std::string(kEntryHash) + "', 'applied', '" +
        std::string(kResultHash) +
        "', 'applied by focused fixture', 'intent-one', 'kid-one', '" +
        std::string(kIntentHash) + "');");
    database.exec(
        "INSERT INTO effect_outbox(effect_idempotency_key, prepared_sequence, "
        "prepared_entry_hash, outbox_state, dispatch_attempts, worker_claim_id, "
        "worker_id, claimed_at_epoch, lease_expires_at_epoch, "
        "last_result_digest_sha256, updated_at_sequence) VALUES('" +
        std::string(kEffectKey) + "', 1, '" + std::string(kEntryHash) +
        "', 'applied', 1, '', '', 0, 0, '" + std::string(kResultHash) +
        "', 1);");
    database.exec(
        "INSERT INTO ingress_sender_replay_cache(replay_key_sha256, format, "
        "service_config_sha256, ingress_profile_sha256, "
        "sender_replay_cache_instance_id, sender_proof_kid, principal, nonce, "
        "issued_at_epoch, observed_at_epoch, replay_window_seconds, material_sha256, "
        "prepared_sequence, prepared_entry_hash, effect_idempotency_key) VALUES('" +
        std::string(kReplayKey) +
        "', 'anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction', '" +
        std::string(kServiceHash) + "', '" + std::string(kProfileHash) +
        "', 'cache-instance', 'sender-kid', 'principal-one', "
        "'0123456789abcdef', 100, 101, 300, '" +
        std::string(kMaterialHash) + "', 1, '" + std::string(kEntryHash) +
        "', '" + std::string(kEffectKey) + "');");
}

[[nodiscard]] inline persistence::SqliteReplayLedgerResetExpectation
expectation_from(const persistence::SqliteReplayLedgerResetState& state) {
    persistence::SqliteReplayLedgerResetExpectation expected;
    expected.namespace_identity = state.namespace_identity;
    expected.ledger_instance_id = state.ledger_instance_id;
    expected.state_sha256 = state.state_sha256;
    expected.durable_line_count = state.durable_line_count;
    expected.durable_head_hash = state.durable_head_hash;
    expected.effect_transition_line_count = state.effect_transition_line_count;
    expected.effect_transition_head_hash = state.effect_transition_head_hash;
    expected.ledger_entry_rows = state.ledger_entry_rows;
    expected.effect_transition_rows = state.effect_transition_rows;
    expected.effect_outbox_rows = state.effect_outbox_rows;
    expected.ingress_sender_replay_rows = state.ingress_sender_replay_rows;
    return expected;
}

[[nodiscard]] inline persistence::SqliteReplayLedgerResetRequest request_for(
    const fs::path& path,
    const persistence::SqliteReplayLedgerResetState& state,
    std::string intent = "focused-reset-intent-001") {
    persistence::SqliteReplayLedgerResetRequest request;
    request.ledger_path = path;
    request.reset_intent_id = std::move(intent);
    request.operator_id = "focused-test-operator";
    request.reason = "exercise exact-state reset and crash-recoverable receipt";
    request.expected = expectation_from(state);
    return request;
}

}  // namespace anonsync::test::sqlite_replay_ledger_reset_fixture
