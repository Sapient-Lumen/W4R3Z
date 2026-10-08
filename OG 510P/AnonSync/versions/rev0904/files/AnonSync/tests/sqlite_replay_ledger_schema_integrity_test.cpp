#include "anonsync_core_internal.hpp"
#include "sqlite_snapshot_seal.hpp"

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

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void cleanup_sqlite_family(const std::string& path) {
    for (const std::string_view suffix : {"", "-wal", "-shm", "-journal",
                                          ".restore.lock", ".write.lock"}) {
        std::remove((path + std::string(suffix)).c_str());
    }
}

class Database final {
public:
    Database(const std::string& path, int flags) {
        if (sqlite3_open_v2(path.c_str(), &db_, flags, nullptr) != SQLITE_OK) {
            const std::string message = db_ ? sqlite3_errmsg(db_) : "sqlite open failed";
            if (db_ != nullptr) sqlite3_close_v2(db_);
            db_ = nullptr;
            throw std::runtime_error(message);
        }
    }

    explicit Database(sqlite3* database) : db_(database) {
        if (db_ == nullptr) throw std::runtime_error("null sqlite database");
    }

    ~Database() {
        if (db_ != nullptr) sqlite3_close_v2(db_);
    }

    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

    sqlite3* get() const noexcept { return db_; }

    void exec(const std::string& sql) const {
        char* error = nullptr;
        const int rc = sqlite3_exec(db_, sql.c_str(), nullptr, nullptr, &error);
        if (rc != SQLITE_OK) {
            const std::string message = error != nullptr ? error : sqlite3_errmsg(db_);
            sqlite3_free(error);
            throw std::runtime_error(message);
        }
    }

    std::string text(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(db_, sql.c_str(), -1, &statement, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(db_));
        }
        const int rc = sqlite3_step(statement);
        if (rc != SQLITE_ROW) {
            sqlite3_finalize(statement);
            throw std::runtime_error("text query returned no row");
        }
        const unsigned char* value = sqlite3_column_text(statement, 0);
        const int bytes = sqlite3_column_bytes(statement, 0);
        if (value == nullptr || bytes < 0) {
            sqlite3_finalize(statement);
            throw std::runtime_error("text query returned invalid text");
        }
        std::string out(reinterpret_cast<const char*>(value),
                        static_cast<std::size_t>(bytes));
        sqlite3_finalize(statement);
        return out;
    }

    std::int64_t integer(const std::string& sql) const {
        sqlite3_stmt* statement = nullptr;
        if (sqlite3_prepare_v2(db_, sql.c_str(), -1, &statement, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite3_errmsg(db_));
        }
        const int rc = sqlite3_step(statement);
        if (rc != SQLITE_ROW || sqlite3_column_type(statement, 0) != SQLITE_INTEGER) {
            sqlite3_finalize(statement);
            throw std::runtime_error("integer query returned no exact integer row");
        }
        const std::int64_t out = sqlite3_column_int64(statement, 0);
        sqlite3_finalize(statement);
        return out;
    }

private:
    sqlite3* db_ = nullptr;
};

// Snapshot inspection itself must not create WAL/SHM state beside the main
// file.  Use the same immutable byte seal as production verification so this
// regression test cannot accidentally poison a later restore fixture merely by
// reading sqlite_schema.
class SealedReadOnlyDatabase final {
public:
    SealedReadOnlyDatabase(const std::string& path, const std::string& label)
        : seal_(anonsync::persistence::SealedSqliteSnapshot::capture(path, label)),
          database_(seal_.open_database_or_throw(label + " immutable open")) {}

    std::string text(const std::string& sql) const { return database_.text(sql); }
    std::int64_t integer(const std::string& sql) const {
        return database_.integer(sql);
    }

private:
    anonsync::persistence::SealedSqliteSnapshot seal_;
    Database database_;
};

void bump_schema_cookie(const Database& database, int cookie) {
    database.exec("PRAGMA schema_version=" + std::to_string(cookie) + ";");
}

void weaken_replay_table(const std::string& path) {
    Database database(path, SQLITE_OPEN_READWRITE);
    database.exec("PRAGMA writable_schema=ON;");
    database.exec(
        "UPDATE sqlite_schema SET sql="
        "'CREATE TABLE ingress_sender_replay_cache ("
        "replay_key_sha256 TEXT PRIMARY KEY,format TEXT,service_config_sha256 TEXT,"
        "ingress_profile_sha256 TEXT,sender_replay_cache_instance_id TEXT,"
        "sender_proof_kid TEXT,principal TEXT,nonce TEXT,issued_at_epoch INTEGER,"
        "observed_at_epoch INTEGER,replay_window_seconds INTEGER,material_sha256 TEXT,"
        "prepared_sequence INTEGER,prepared_entry_hash TEXT,effect_idempotency_key TEXT)' "
        "WHERE type='table' AND name='ingress_sender_replay_cache';");
    bump_schema_cookie(database, 790201);
    database.exec("PRAGMA writable_schema=OFF;");
}

void remove_expiry_index(const std::string& path) {
    Database database(path, SQLITE_OPEN_READWRITE);
    database.exec("PRAGMA writable_schema=ON;");
    database.exec(
        "DELETE FROM sqlite_schema WHERE type='index' "
        "AND name='ingress_sender_replay_expiry';");
    bump_schema_cookie(database, 790202);
    database.exec("PRAGMA writable_schema=OFF;");
}

void add_sqlite_statistics_schema(const std::string& path) {
    Database database(path, SQLITE_OPEN_READWRITE);
    database.exec("ANALYZE;");
}

void reformat_metadata_schema(const std::string& path) {
    Database database(path, SQLITE_OPEN_READWRITE);
    database.exec("PRAGMA writable_schema=ON;");
    database.exec(
        "UPDATE sqlite_schema SET sql="
        "'CREATE TABLE metadata  (id INTEGER PRIMARY KEY CHECK(id=1),"
        "line_count INTEGER NOT NULL CHECK(line_count >= 0),"
        "head_hash TEXT NOT NULL CHECK(length(head_hash) > 0))' "
        "WHERE type='table' AND name='metadata';");
    bump_schema_cookie(database, 790203);
    database.exec("PRAGMA writable_schema=OFF;");
}

anonsync::Json make_case() {
    using namespace anonsync;
    Json value;
    value.type = Json::Type::Object;
    value.o["case_id"] = json_string_value("schema-contract-case");
    value.o["kind"] = json_string_value("openapi");
    value.o["operation_id"] = json_string_value("schemaContractOperation");
    value.o["contract_digest_sha256"] = json_string_value("schema-contract-input");
    value.o["cloud_event_source"] = json_string_value("");
    value.o["cloud_event_id"] = json_string_value("");
    return value;
}

anonsync::Json make_claims() {
    using namespace anonsync;
    Json value;
    value.type = Json::Type::Object;
    value.o["operation_id"] = json_string_value("schemaContractOperation");
    value.o["contract_digest_sha256"] =
        json_string_value(sha256_hex("schema-contract-input"));
    value.o["jti"] = json_string_value("schema-contract-jti");
    return value;
}

void expect_load_rejection(const std::string& path,
                           std::string_view expected_reason,
                           std::uint64_t& checks) {
    bool rejected = false;
    std::string reason;
    try {
        auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
        backend->load(path, "batch");
        backend->close();
    } catch (const std::exception& error) {
        rejected = true;
        reason = error.what();
    }
    require(rejected, "existing weakened ledger was accepted", checks);
    require(reason.find(expected_reason) != std::string::npos,
            "existing weakened ledger returned the wrong rejection: " + reason,
            checks);
}

void expect_restore_rejection(const std::string& source,
                              const std::string& destination,
                              std::string_view expected_reason,
                              std::uint64_t& checks) {
    bool rejected = false;
    std::string reason;
    try {
        anonsync::restore_sqlite_snapshot_into_ledger(source, destination);
    } catch (const std::exception& error) {
        rejected = true;
        reason = error.what();
    }
    require(rejected, "weakened snapshot was restored", checks);
    require(reason.find(expected_reason) != std::string::npos,
            "weakened snapshot returned the wrong rejection: " + reason, checks);
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const std::string stem =
        "/tmp/anonsync_rev0792_schema_contract_" + std::to_string(::getpid());
    const std::string live = stem + "_live.sqlite";
    const std::string snapshot = stem + "_snapshot.sqlite";
    const std::string valid_destination = stem + "_valid_destination.sqlite";
    const std::string weakened = stem + "_weakened.sqlite";
    const std::string weakened_destination = stem + "_weakened_destination.sqlite";
    const std::string missing_index = stem + "_missing_index.sqlite";
    const std::string statistics = stem + "_statistics.sqlite";
    const std::string statistics_destination = stem + "_statistics_destination.sqlite";
    const std::string reformatted = stem + "_reformatted.sqlite";
    const std::string reformatted_destination = stem + "_reformatted_destination.sqlite";

    const auto cleanup_all = [&] {
        for (const auto& path : {live, snapshot, valid_destination, weakened,
                                weakened_destination, missing_index, statistics,
                                statistics_destination, reformatted,
                                reformatted_destination}) {
            cleanup_sqlite_family(path);
        }
    };

    cleanup_all();
    try {
        std::string reason;
        auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
        backend->load(live, "batch");
        require(backend->stage(make_case(), make_claims(), "allow", reason),
                "seed stage failed: " + reason, checks);
        require(backend->commit(reason), "seed commit failed: " + reason, checks);
        require(backend->backup_snapshot(snapshot, reason),
                "seed snapshot failed: " + reason, checks);
        backend->close();

        {
            SealedReadOnlyDatabase database(
                snapshot, "schema integrity canonical snapshot inspection");
            require(database.integer(
                        "SELECT count(*) FROM sqlite_schema "
                        "WHERE sql IS NOT NULL") == 14,
                    "canonical snapshot has the wrong schema object count", checks);
            const std::string replay_sql = database.text(
                "SELECT sql FROM sqlite_schema WHERE type='table' "
                "AND name='ingress_sender_replay_cache'");
            require(replay_sql.find("FOREIGN KEY") != std::string::npos,
                    "canonical replay table lacks its foreign key", checks);
            require(replay_sql.find("NOT NULL") != std::string::npos,
                    "canonical replay table lacks NOT NULL enforcement", checks);
            require(replay_sql.find("CHECK") != std::string::npos,
                    "canonical replay table lacks CHECK enforcement", checks);
        }

        anonsync::restore_sqlite_snapshot_into_ledger(snapshot, valid_destination);
        {
            auto restored = anonsync::create_replay_ledger_backend("sqlite-wal");
            restored->load(valid_destination, "batch");
            require(restored->stats().durable_line_count == 1,
                    "valid exact-schema restore lost the prepared row", checks);
            restored->close();
        }

        std::filesystem::copy_file(
            snapshot, weakened, std::filesystem::copy_options::overwrite_existing);
        weaken_replay_table(weakened);
        {
            SealedReadOnlyDatabase database(
                weakened, "schema integrity weakened snapshot inspection");
            const std::string sql = database.text(
                "SELECT sql FROM sqlite_schema WHERE type='table' "
                "AND name='ingress_sender_replay_cache'");
            require(sql.find("FOREIGN KEY") == std::string::npos,
                    "weakened fixture unexpectedly retained foreign keys", checks);
            require(sql.find("NOT NULL") == std::string::npos,
                    "weakened fixture unexpectedly retained NOT NULL", checks);
            require(sql.find("CHECK") == std::string::npos,
                    "weakened fixture unexpectedly retained CHECK", checks);
        }
        expect_restore_rejection(
            weakened, weakened_destination,
            "sqlite_replay_ledger_schema[schema_sql_mismatch]:ingress_sender_replay_cache", checks);
        expect_load_rejection(
            weakened, "sqlite_replay_ledger_schema[schema_sql_mismatch]:ingress_sender_replay_cache", checks);
        {
            SealedReadOnlyDatabase database(
                weakened, "schema integrity post-load weakened inspection");
            const std::string sql = database.text(
                "SELECT sql FROM sqlite_schema WHERE type='table' "
                "AND name='ingress_sender_replay_cache'");
            require(sql.find("FOREIGN KEY") == std::string::npos,
                    "failed live load silently repaired the weakened foreign key", checks);
            require(sql.find("NOT NULL") == std::string::npos,
                    "failed live load silently repaired NOT NULL", checks);
            require(sql.find("CHECK") == std::string::npos,
                    "failed live load silently repaired CHECK", checks);
        }

        std::filesystem::copy_file(
            snapshot, missing_index,
            std::filesystem::copy_options::overwrite_existing);
        remove_expiry_index(missing_index);
        expect_load_rejection(
            missing_index, "sqlite_replay_ledger_schema[missing_object]:ingress_sender_replay_expiry", checks);
        {
            SealedReadOnlyDatabase database(
                missing_index, "schema integrity missing-index inspection");
            require(database.integer(
                        "SELECT count(*) FROM sqlite_schema WHERE type='index' "
                        "AND name='ingress_sender_replay_expiry'") == 0,
                    "failed live load silently recreated a missing index", checks);
        }

        std::filesystem::copy_file(
            snapshot, statistics,
            std::filesystem::copy_options::overwrite_existing);
        add_sqlite_statistics_schema(statistics);
        {
            SealedReadOnlyDatabase database(
                statistics, "schema integrity statistics inspection");
            require(database.integer(
                        "SELECT count(*) FROM sqlite_schema "
                        "WHERE type='table' AND name='sqlite_stat1'") == 1,
                    "statistics fixture did not create sqlite_stat1", checks);
        }
        expect_restore_rejection(
            statistics, statistics_destination,
            "sqlite_replay_ledger_schema[unexpected_object]", checks);
        expect_load_rejection(
            statistics, "sqlite_replay_ledger_schema[unexpected_object]", checks);

        std::filesystem::copy_file(
            snapshot, reformatted,
            std::filesystem::copy_options::overwrite_existing);
        reformat_metadata_schema(reformatted);
        expect_restore_rejection(
            reformatted, reformatted_destination,
            "sqlite_replay_ledger_schema[schema_sql_mismatch]:metadata", checks);

        require(!std::filesystem::exists(weakened_destination),
                "rejected restore published a destination database", checks);
        require(!std::filesystem::exists(statistics_destination),
                "rejected statistics restore published a destination database", checks);
        require(!std::filesystem::exists(reformatted_destination),
                "rejected reformatted restore published a destination database", checks);

        std::cout << "anonsync_sqlite_replay_ledger_schema_integrity_test checks="
                  << checks << "\n";
        cleanup_all();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "anonsync_sqlite_replay_ledger_schema_integrity_test failure after "
                  << checks << " checks: " << error.what() << "\n";
        cleanup_all();
        return 2;
    }
}
