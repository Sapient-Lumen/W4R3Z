#include "anonsync_core_internal.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <cstdio>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void cleanup_sqlite_family(const std::string& path) {
    for (const std::string_view suffix : {
             "", "-wal", "-shm", "-journal", ".restore.lock", ".write.lock"}) {
        std::remove((path + std::string(suffix)).c_str());
    }
}

class Database final {
public:
    Database(const std::string& path, int flags) {
        if (sqlite3_open_v2(path.c_str(), &database_, flags, nullptr) != SQLITE_OK) {
            const std::string reason =
                database_ != nullptr ? sqlite3_errmsg(database_) : "SQLite open failed";
            if (database_ != nullptr) (void)sqlite3_close_v2(database_);
            database_ = nullptr;
            throw std::runtime_error(reason);
        }
    }

    ~Database() {
        if (database_ != nullptr) (void)sqlite3_close_v2(database_);
    }

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    void exec(const std::string& sql) const {
        char* error = nullptr;
        const int rc = sqlite3_exec(database_, sql.c_str(), nullptr, nullptr, &error);
        if (rc != SQLITE_OK) {
            const std::string reason =
                error != nullptr ? error : sqlite3_errmsg(database_);
            sqlite3_free(error);
            throw std::runtime_error(reason);
        }
    }

    std::string text(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(database_, sql.c_str(), -1, &statement, nullptr) !=
            SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(database_));
        }
        const int rc = sqlite3_step(statement);
        if (rc != SQLITE_ROW || sqlite3_column_type(statement, 0) != SQLITE_TEXT) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("text query returned no exact text row");
        }
        const unsigned char* bytes = sqlite3_column_text(statement, 0);
        const int count = sqlite3_column_bytes(statement, 0);
        if (bytes == nullptr || count < 0) {
            (void)sqlite3_finalize(statement);
            throw std::runtime_error("text query returned invalid bytes");
        }
        std::string value(reinterpret_cast<const char*>(bytes),
                          static_cast<std::size_t>(count));
        (void)sqlite3_finalize(statement);
        return value;
    }

private:
    sqlite3* database_ = nullptr;
};

anonsync::Json make_case() {
    using namespace anonsync;
    Json value;
    value.type = Json::Type::Object;
    value.o["case_id"] = json_string_value("snapshot-sidecar-binding-case");
    value.o["kind"] = json_string_value("openapi");
    value.o["operation_id"] = json_string_value("snapshotSidecarBinding");
    value.o["contract_digest_sha256"] =
        json_string_value("snapshot-sidecar-binding-input");
    value.o["cloud_event_source"] = json_string_value("");
    value.o["cloud_event_id"] = json_string_value("");
    return value;
}

anonsync::Json make_claims() {
    using namespace anonsync;
    Json value;
    value.type = Json::Type::Object;
    value.o["operation_id"] = json_string_value("snapshotSidecarBinding");
    value.o["contract_digest_sha256"] =
        json_string_value(sha256_hex("snapshot-sidecar-binding-input"));
    value.o["jti"] = json_string_value("snapshot-sidecar-binding-jti");
    return value;
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const std::string stem =
        "/tmp/anonsync_rev0796_snapshot_sidecar_binding_" +
        std::to_string(::getpid());
    const std::string live = stem + "_live.sqlite";
    const std::string snapshot = stem + "_snapshot.sqlite";
    const std::string destination = stem + "_destination.sqlite";

    const auto cleanup = [&] {
        cleanup_sqlite_family(live);
        cleanup_sqlite_family(snapshot);
        cleanup_sqlite_family(destination);
    };
    cleanup();

    try {
        std::string reason;
        auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
        backend->load(live, true, "batch");
        require(backend->stage(make_case(), make_claims(), "allow", reason),
                "seed stage failed: " + reason, checks);
        require(backend->commit(reason), "seed commit failed: " + reason, checks);
        require(backend->backup_snapshot(snapshot, reason),
                "seed snapshot failed: " + reason, checks);
        backend->close();

        Database attacker(snapshot, SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX);
        attacker.exec("PRAGMA journal_mode=WAL;");
        attacker.exec("PRAGMA wal_autocheckpoint=0;");
        attacker.exec("PRAGMA wal_checkpoint(TRUNCATE);");

        const std::string original_identity = attacker.text(
            "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;");
        const std::string main_digest_before =
            anonsync::sha256_hex(anonsync::read_file(snapshot));
        const std::string forged_identity(64, 'a');
        require(original_identity != forged_identity,
                "exploit fixture identity already equals forged value", checks);

        attacker.exec("BEGIN IMMEDIATE;");
        attacker.exec(
            "UPDATE ledger_identity SET ledger_instance_id='" + forged_identity +
            "' WHERE id=1;");
        attacker.exec("COMMIT;");

        const std::string main_digest_after =
            anonsync::sha256_hex(anonsync::read_file(snapshot));
        require(main_digest_before == main_digest_after,
                "WAL-only mutation changed manifest-bound main bytes", checks);
        require(fs::is_regular_file(snapshot + "-wal"),
                "WAL-only mutation did not leave a WAL sidecar", checks);

        {
            Database ordinary_reader(snapshot,
                                     SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX);
            require(ordinary_reader.text(
                        "SELECT ledger_instance_id FROM ledger_identity WHERE id=1;") ==
                        forged_identity,
                    "ordinary read-only SQLite did not merge unsigned WAL state",
                    checks);
        }

        bool rejected = false;
        std::string rejection;
        try {
            anonsync::restore_sqlite_snapshot_into_ledger(snapshot, destination);
        } catch (const std::exception& error) {
            rejected = true;
            rejection = error.what();
        }
        require(rejected, "restore accepted unsigned WAL state", checks);
        require(rejection.find("snapshot sidecar -wal") != std::string::npos,
                "restore rejection did not identify the unsigned WAL: " + rejection,
                checks);
        require(!fs::exists(destination),
                "rejected unsigned-WAL restore published a destination database",
                checks);

        cleanup();
        std::cout << "anonsync sqlite snapshot sidecar binding checks=" << checks
                  << "\n";
        return 0;
    } catch (const std::exception& error) {
        cleanup();
        std::cerr << "anonsync sqlite snapshot sidecar binding failed after "
                  << checks << " checks: " << error.what() << "\n";
        return 1;
    }
}
