#include "anonsync_core_internal.hpp"
#include <sqlite3.h>

#include <cstdio>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unistd.h>

namespace {
void cleanup(const std::string& path) {
    for (const std::string suffix : {"", "-wal", "-shm", "-journal", ".restore.lock", ".write.lock"}) {
        std::remove((path + suffix).c_str());
    }
}

void exec(sqlite3* db, const char* sql) {
    char* error = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &error);
    if (rc != SQLITE_OK) {
        const std::string message = error ? error : sqlite3_errmsg(db);
        sqlite3_free(error);
        throw std::runtime_error(message);
    }
}

std::string scalar(sqlite3* db, const char* sql) {
    sqlite3_stmt* stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite3_errmsg(db));
    }
    const int rc = sqlite3_step(stmt);
    if (rc != SQLITE_ROW) {
        sqlite3_finalize(stmt);
        throw std::runtime_error("scalar query returned no row");
    }
    const unsigned char* value = sqlite3_column_text(stmt, 0);
    const int bytes = sqlite3_column_bytes(stmt, 0);
    std::string out(reinterpret_cast<const char*>(value), static_cast<std::size_t>(bytes));
    sqlite3_finalize(stmt);
    return out;
}
}

int main() {
    using namespace anonsync;
    const std::string stem = "/tmp/anonsync_rev0791_schema_weaken_" + std::to_string(::getpid());
    const std::string source = stem + "_source.sqlite";
    const std::string snapshot = stem + "_snapshot.sqlite";
    const std::string restored = stem + "_restored.sqlite";
    cleanup(source);
    cleanup(snapshot);
    cleanup(restored);

    try {
        Json tc;
        tc.type = Json::Type::Object;
        tc.o["case_id"] = json_string_value("schema-weaken-case");
        tc.o["kind"] = json_string_value("openapi");
        tc.o["operation_id"] = json_string_value("schemaWeakenOperation");
        tc.o["contract_digest_sha256"] = json_string_value("schema-weaken-contract");
        tc.o["cloud_event_source"] = json_string_value("");
        tc.o["cloud_event_id"] = json_string_value("");

        Json claims;
        claims.type = Json::Type::Object;
        claims.o["operation_id"] = json_string_value("schemaWeakenOperation");
        claims.o["contract_digest_sha256"] = json_string_value(sha256_hex("schema-weaken-contract"));
        claims.o["jti"] = json_string_value("schema-weaken-jti");

        std::string reason;
        auto backend = create_replay_ledger_backend("sqlite-wal");
        backend->load(source, true, "batch");
        if (!backend->stage(tc, claims, "allow", reason) || !backend->commit(reason) ||
            !backend->backup_snapshot(snapshot, reason)) {
            throw std::runtime_error("seed failed: " + reason);
        }
        backend->close();

        sqlite3* db = nullptr;
        if (sqlite3_open_v2(snapshot.c_str(), &db, SQLITE_OPEN_READWRITE, nullptr) != SQLITE_OK) {
            throw std::runtime_error(db ? sqlite3_errmsg(db) : "open failed");
        }
        exec(db, "PRAGMA writable_schema=ON;");
        exec(db,
             "UPDATE sqlite_schema SET sql="
             "'CREATE TABLE ingress_sender_replay_cache ("
             "replay_key_sha256 TEXT PRIMARY KEY,format TEXT,service_config_sha256 TEXT,"
             "ingress_profile_sha256 TEXT,sender_replay_cache_instance_id TEXT,"
             "sender_proof_kid TEXT,principal TEXT,nonce TEXT,issued_at_epoch INTEGER,"
             "observed_at_epoch INTEGER,replay_window_seconds INTEGER,material_sha256 TEXT,"
             "prepared_sequence INTEGER,prepared_entry_hash TEXT,effect_idempotency_key TEXT)' "
             "WHERE type='table' AND name='ingress_sender_replay_cache';");
        exec(db, "PRAGMA schema_version=70092;");
        exec(db, "PRAGMA writable_schema=OFF;");
        sqlite3_close(db);

        bool accepted = false;
        std::string rejection;
        try {
            restore_sqlite_snapshot_into_ledger(snapshot, restored);
            accepted = true;
        } catch (const std::exception& e) {
            rejection = e.what();
        }
        std::cout << "weakened_schema_restore_accepted=" << (accepted ? "true" : "false") << "\n";
        if (!accepted) std::cout << "rejection=" << rejection << "\n";

        if (accepted) {
            sqlite3* check = nullptr;
            if (sqlite3_open_v2(restored.c_str(), &check, SQLITE_OPEN_READONLY, nullptr) != SQLITE_OK) {
                throw std::runtime_error("restored open failed");
            }
            const std::string sql = scalar(check,
                "SELECT sql FROM sqlite_schema WHERE type='table' AND name='ingress_sender_replay_cache'");
            sqlite3_close(check);
            std::cout << "restored_schema_has_foreign_key="
                      << (sql.find("FOREIGN KEY") != std::string::npos ? "true" : "false") << "\n";
            std::cout << "restored_schema_has_not_null="
                      << (sql.find("NOT NULL") != std::string::npos ? "true" : "false") << "\n";
            std::cout << "restored_schema_has_check="
                      << (sql.find("CHECK") != std::string::npos ? "true" : "false") << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "reproducer_exception=" << e.what() << "\n";
        cleanup(source); cleanup(snapshot); cleanup(restored);
        return 3;
    }

    cleanup(source); cleanup(snapshot); cleanup(restored);
    return 0;
}
