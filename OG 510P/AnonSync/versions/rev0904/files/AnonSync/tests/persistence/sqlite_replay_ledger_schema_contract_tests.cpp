#include "sqlite_replay_ledger_schema_contract.hpp"

#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace {

using namespace anonsync::persistence;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

std::vector<ObservedSqliteSchemaObject> canonical_observation() {
    std::vector<ObservedSqliteSchemaObject> out;
    for (const auto& definition : sqlite_replay_ledger_schema_contract()) {
        out.push_back({std::string(definition.type), std::string(definition.name),
                       std::string(definition.table_name),
                       std::string(definition.stored_sql)});
    }
    return out;
}

void require_failure(const SqliteReplayLedgerSchemaVerification& result,
                     SqliteReplayLedgerSchemaFailure expected,
                     std::string_view expected_name,
                     std::string_view context,
                     std::uint64_t& checks) {
    require(!result, std::string(context) + " was accepted", checks);
    require(result.failure == expected,
            std::string(context) + " returned the wrong failure", checks);
    require(result.expected_object_name == expected_name,
            std::string(context) + " returned the wrong trusted object name", checks);
    const std::string summary = result.safe_summary();
    require(summary.find(std::string(sqlite_replay_ledger_schema_failure_name(expected))) !=
                std::string::npos,
            std::string(context) + " summary omitted its failure", checks);
    require(summary.find("attacker-sensitive-marker") == std::string::npos,
            std::string(context) + " summary leaked hostile schema bytes", checks);
    require(summary.find('\n') == std::string::npos &&
                summary.find('\r') == std::string::npos &&
                summary.find('\x1b') == std::string::npos,
            std::string(context) + " summary admitted control bytes", checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        const auto contract = sqlite_replay_ledger_schema_contract();
        require(contract.size() == 14, "schema object count changed without a versioned test update", checks);
        require(kSqliteReplayLedgerSchemaVersion == 10,
                "schema version constant changed unexpectedly", checks);
        require(kSqliteReplayLedgerBackendName == "sqlite-wal",
                "backend name constant changed unexpectedly", checks);
        require(kSqliteReplayLedgerHashAlgorithm == "sha256",
                "hash algorithm constant changed unexpectedly", checks);
        require(kSqliteReplayLedgerEntryMaterialVersion ==
                    "anonsync-replay-ledger-entry-v7-ledger-instance-bound-transition-intent",
                "entry material version constant changed unexpectedly", checks);
        require(kSqliteReplayLedgerCommitProtocol ==
                    "sqlite-wal-begin-immediate-full-sync",
                "commit protocol constant changed unexpectedly", checks);

        const auto canonical = canonical_observation();
        require(static_cast<bool>(verify_sqlite_replay_ledger_schema(canonical)),
                "canonical schema was rejected", checks);
        require(verify_sqlite_replay_ledger_schema({}).failure ==
                    SqliteReplayLedgerSchemaFailure::missing_object,
                "empty schema did not fail as missing", checks);

        auto reversed = canonical;
        std::reverse(reversed.begin(), reversed.end());
        require(static_cast<bool>(verify_sqlite_replay_ledger_schema(reversed)),
                "verification incorrectly depended on sqlite_schema row order", checks);

        for (std::size_t index = 0; index < contract.size(); ++index) {
            const auto& definition = contract[index];
            const std::string context = "object " + std::string(definition.name);
            const std::string create_statement =
                sqlite_replay_ledger_schema_create_statement(definition);
            require(create_statement == std::string(definition.stored_sql) + ";",
                    context + " create statement diverged from stored SQL", checks);
            require(create_statement.find("IF NOT EXISTS") == std::string::npos,
                    context + " retained repair-capable IF NOT EXISTS DDL", checks);
            require(create_statement.back() == ';',
                    context + " create statement lacks one terminator", checks);

            auto missing = canonical;
            missing.erase(missing.begin() + static_cast<std::ptrdiff_t>(index));
            require_failure(verify_sqlite_replay_ledger_schema(missing),
                            SqliteReplayLedgerSchemaFailure::missing_object,
                            definition.name, context + " missing", checks);

            auto duplicate = canonical;
            duplicate.push_back(canonical[index]);
            require_failure(verify_sqlite_replay_ledger_schema(duplicate),
                            SqliteReplayLedgerSchemaFailure::duplicate_object_name,
                            definition.name, context + " duplicate", checks);

            auto wrong_type = canonical;
            wrong_type[index].type = definition.type == "table" ? "index" : "table";
            require_failure(verify_sqlite_replay_ledger_schema(wrong_type),
                            SqliteReplayLedgerSchemaFailure::object_type_mismatch,
                            definition.name, context + " type alias", checks);

            auto wrong_table = canonical;
            wrong_table[index].table_name = "attacker-sensitive-marker\n\x1b[31m";
            require_failure(verify_sqlite_replay_ledger_schema(wrong_table),
                            SqliteReplayLedgerSchemaFailure::table_name_mismatch,
                            definition.name, context + " table alias", checks);

            auto wrong_sql = canonical;
            wrong_sql[index].stored_sql += " /* attacker-sensitive-marker\n\x1b[31m */";
            require_failure(verify_sqlite_replay_ledger_schema(wrong_sql),
                            SqliteReplayLedgerSchemaFailure::schema_sql_mismatch,
                            definition.name, context + " SQL suffix", checks);
        }

        {
            auto extra = canonical;
            extra.push_back({"view", "attacker-sensitive-marker\n\x1b[31m", "x",
                             "CREATE VIEW attacker-sensitive-marker AS SELECT 1"});
            require_failure(verify_sqlite_replay_ledger_schema(extra),
                            SqliteReplayLedgerSchemaFailure::unexpected_object,
                            {}, "unexpected hostile object", checks);
        }
        {
            auto weakened = canonical;
            const auto it = std::find_if(
                weakened.begin(), weakened.end(), [](const auto& object) {
                    return object.name == "ingress_sender_replay_cache";
                });
            require(it != weakened.end(), "ingress replay table is absent from contract", checks);
            it->stored_sql =
                "CREATE TABLE ingress_sender_replay_cache ("
                "replay_key_sha256 TEXT PRIMARY KEY,format TEXT,"
                "service_config_sha256 TEXT,ingress_profile_sha256 TEXT,"
                "sender_replay_cache_instance_id TEXT,sender_proof_kid TEXT,"
                "principal TEXT,nonce TEXT,issued_at_epoch INTEGER,"
                "observed_at_epoch INTEGER,replay_window_seconds INTEGER,"
                "material_sha256 TEXT,prepared_sequence INTEGER,"
                "prepared_entry_hash TEXT,effect_idempotency_key TEXT)";
            require_failure(verify_sqlite_replay_ledger_schema(weakened),
                            SqliteReplayLedgerSchemaFailure::schema_sql_mismatch,
                            "ingress_sender_replay_cache",
                            "constraint-free ingress replay table", checks);
        }
        {
            auto generated = canonical;
            const auto it = std::find_if(
                generated.begin(), generated.end(), [](const auto& object) {
                    return object.name == "metadata";
                });
            require(it != generated.end(), "metadata table is absent from contract", checks);
            it->stored_sql.pop_back();
            it->stored_sql += ",hidden_authority TEXT GENERATED ALWAYS AS (head_hash) VIRTUAL)";
            require_failure(verify_sqlite_replay_ledger_schema(generated),
                            SqliteReplayLedgerSchemaFailure::schema_sql_mismatch,
                            "metadata", "generated hidden column", checks);
        }
        {
            auto widened_index = canonical;
            const auto it = std::find_if(
                widened_index.begin(), widened_index.end(), [](const auto& object) {
                    return object.name == "ingress_sender_replay_nonce_unique";
                });
            require(it != widened_index.end(), "replay nonce index is absent from contract", checks);
            it->stored_sql =
                "CREATE UNIQUE INDEX ingress_sender_replay_nonce_unique ON "
                "ingress_sender_replay_cache(service_config_sha256, "
                "ingress_profile_sha256, sender_replay_cache_instance_id, "
                "sender_proof_kid, nonce, replay_key_sha256)";
            require_failure(verify_sqlite_replay_ledger_schema(widened_index),
                            SqliteReplayLedgerSchemaFailure::schema_sql_mismatch,
                            "ingress_sender_replay_nonce_unique",
                            "widened nonce uniqueness identity", checks);
        }
        {
            SqliteReplayLedgerSchemaDefinition invalid{};
            bool rejected = false;
            try {
                (void)sqlite_replay_ledger_schema_create_statement(invalid);
            } catch (const std::invalid_argument&) {
                rejected = true;
            }
            require(rejected, "invalid schema definition was promoted to DDL", checks);
        }

        std::cout << "anonsync_sqlite_replay_ledger_schema_contract_test checks="
                  << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "anonsync_sqlite_replay_ledger_schema_contract_test failure after "
                  << checks << " checks: " << error.what() << "\n";
        return 2;
    }
}
