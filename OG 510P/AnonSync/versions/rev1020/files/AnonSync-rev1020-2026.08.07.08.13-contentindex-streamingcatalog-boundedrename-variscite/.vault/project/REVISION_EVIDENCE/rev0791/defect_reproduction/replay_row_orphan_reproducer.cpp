#include "anonsync_core_internal.hpp"
#include <sqlite3.h>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unistd.h>

int main() {
    namespace fs = std::filesystem;
    const fs::path dir = fs::temp_directory_path() / ("anonsync-rev0790-replay-row-repro-" + std::to_string(::getpid()));
    fs::create_directories(dir);
    const std::string ledger = (dir / "ledger.sqlite").string();
    try {
        const auto tc = anonsync::parse_json_text(R"JSON({
          "case_id":"case-replay-row",
          "kind":"openapi",
          "cloud_event_source":"",
          "cloud_event_id":"",
          "effect_idempotency_key":"eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
          "effect_state":"prepared",
          "ingress_sender_replay":{
            "format":"anonsync-ingress-sender-replay-cache-v5-sqlite-ledger-integrated-transaction",
            "replay_key_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "service_config_sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "ingress_profile_sha256":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
            "sender_replay_cache_instance_id":"cache-instance-1",
            "sender_proof_kid":"proof-kid-1",
            "principal":"principal-1",
            "nonce":"abcdefghijklmnop",
            "issued_at_epoch":1000,
            "observed_at_epoch":1000,
            "replay_window_seconds":300,
            "material_sha256":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
          }
        })JSON");
        const auto claims = anonsync::parse_json_text(R"JSON({
          "operation_id":"replayRowOperation",
          "contract_digest_sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
          "jti":"replay-row-jti-1"
        })JSON");
        std::string reason;
        auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
        backend->load(ledger, true, "immediate");
        if (!backend->stage(tc, claims, "allow", reason)) {
            throw std::runtime_error("seed stage failed: " + reason);
        }
        backend->close();

        sqlite3* db = nullptr;
        if (sqlite3_open_v2(ledger.c_str(), &db, SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX, nullptr) != SQLITE_OK) {
            throw std::runtime_error("tamper open failed");
        }
        char* error = nullptr;
        const int rc = sqlite3_exec(db,
            "PRAGMA foreign_keys=OFF;"
            "UPDATE ingress_sender_replay_cache SET prepared_sequence=999 WHERE replay_key_sha256='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';",
            nullptr, nullptr, &error);
        if (rc != SQLITE_OK) {
            std::string message = error ? error : "tamper failed";
            sqlite3_free(error);
            sqlite3_close(db);
            throw std::runtime_error(message);
        }
        sqlite3_close(db);

        bool accepted = false;
        std::string rejection;
        try {
            auto reload = anonsync::create_replay_ledger_backend("sqlite-wal");
            reload->load(ledger, false, "immediate");
            accepted = true;
            reload->close();
        } catch (const std::exception& e) {
            rejection = e.what();
        }
        std::cout << "orphaned_replay_row_reload_accepted=" << (accepted ? "true" : "false") << "\n";
        if (!rejection.empty()) std::cout << "rejection=" << rejection << "\n";
        fs::remove_all(dir);
        return accepted ? 0 : 2;
    } catch (const std::exception& e) {
        std::cerr << "repro_error=" << e.what() << "\n";
        fs::remove_all(dir);
        return 1;
    }
}
