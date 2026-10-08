#include "anonsync_core_internal.hpp"

#include <sqlite3.h>

#include <filesystem>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;

class SqliteDb final {
  public:
    explicit SqliteDb(const fs::path& path) {
        const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX |
                          SQLITE_OPEN_NOFOLLOW;
        if (sqlite3_open_v2(path.c_str(), &db_, flags, nullptr) != SQLITE_OK) {
            const std::string reason = db_ ? sqlite3_errmsg(db_) : "unknown open failure";
            if (db_) sqlite3_close(db_);
            db_ = nullptr;
            throw std::runtime_error("tamper database open failed: " + reason);
        }
        sqlite3_busy_timeout(db_, 1000);
    }

    ~SqliteDb() {
        if (db_) sqlite3_close(db_);
    }

    SqliteDb(const SqliteDb&) = delete;
    SqliteDb& operator=(const SqliteDb&) = delete;

    [[nodiscard]] sqlite3* get() const noexcept { return db_; }

    void exec(std::string_view sql) const {
        char* error = nullptr;
        const std::string owned(sql);
        const int rc = sqlite3_exec(db_, owned.c_str(), nullptr, nullptr, &error);
        if (rc != SQLITE_OK) {
            const std::string reason = error ? error : sqlite3_errmsg(db_);
            sqlite3_free(error);
            throw std::runtime_error("tamper SQL failed: " + reason);
        }
    }

    void checkpoint() const {
        exec("PRAGMA wal_checkpoint(TRUNCATE);");
    }

  private:
    sqlite3* db_ = nullptr;
};

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

void remove_sqlite_family(const fs::path& path) {
    std::error_code ignored;
    fs::remove(path, ignored);
    fs::remove(path.string() + "-wal", ignored);
    fs::remove(path.string() + "-shm", ignored);
    fs::remove(path.string() + ".write.lock", ignored);
}

void clone_snapshot(const fs::path& source, const fs::path& destination) {
    remove_sqlite_family(destination);
    fs::copy_file(source, destination, fs::copy_options::overwrite_existing);
}

void mutate_sql(const fs::path& path, std::string_view sql) {
    SqliteDb db(path);
    db.exec("PRAGMA foreign_keys=OFF;");
    db.exec(sql);
    db.checkpoint();
}

void mutate_principal(const fs::path& path, const std::string& principal) {
    SqliteDb db(path);
    db.exec("PRAGMA foreign_keys=OFF;");
    sqlite3_stmt* raw = nullptr;
    if (sqlite3_prepare_v2(db.get(),
                           "UPDATE ingress_sender_replay_cache SET principal=?",
                           -1, &raw, nullptr) != SQLITE_OK) {
        throw std::runtime_error("principal tamper prepare failed: " +
                                 std::string(sqlite3_errmsg(db.get())));
    }
    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(raw,
                                                                   sqlite3_finalize);
    if (sqlite3_bind_text64(stmt.get(), 1, principal.data(),
                            static_cast<sqlite3_uint64>(principal.size()),
                            SQLITE_TRANSIENT, SQLITE_UTF8) != SQLITE_OK) {
        throw std::runtime_error("principal tamper bind failed: " +
                                 std::string(sqlite3_errmsg(db.get())));
    }
    if (sqlite3_step(stmt.get()) != SQLITE_DONE) {
        throw std::runtime_error("principal tamper update failed: " +
                                 std::string(sqlite3_errmsg(db.get())));
    }
    stmt.reset();
    db.checkpoint();
}

std::string reload_rejection(const fs::path& ledger) {
    try {
        auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
        backend->load(ledger.string(), "immediate");
        backend->close();
    } catch (const std::exception& error) {
        return error.what();
    }
    return {};
}

std::string restore_rejection(const fs::path& snapshot, const fs::path& destination) {
    remove_sqlite_family(destination);
    try {
        anonsync::restore_sqlite_snapshot_into_ledger(snapshot.string(),
                                                       destination.string());
    } catch (const std::exception& error) {
        return error.what();
    }
    return {};
}

void require_rejected(const fs::path& ledger,
                      std::string_view expected_fragment,
                      const std::string& context,
                      std::uint64_t& checks) {
    const std::string rejection = reload_rejection(ledger);
    require(!rejection.empty(), context + " was accepted during normal reload", checks);
    require(rejection.find(expected_fragment) != std::string::npos,
            context + " returned an unexpected rejection: " + rejection, checks);
}

anonsync::Json seed_case() {
    return anonsync::parse_json_text(R"JSON({
      "case_id":"case-replay-row-integrity",
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
}

anonsync::Json seed_claims() {
    return anonsync::parse_json_text(R"JSON({
      "operation_id":"replayRowIntegrityOperation",
      "contract_digest_sha256":"ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
      "jti":"replay-row-integrity-jti-1"
    })JSON");
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const fs::path root = fs::temp_directory_path() /
        ("anonsync-sqlite-replay-row-integrity-" + std::to_string(::getpid()));
    try {
        fs::create_directories(root);
        const fs::path seed_ledger = root / "seed.sqlite";
        const fs::path clean_snapshot = root / "clean-snapshot.sqlite";
        {
            auto backend = anonsync::create_replay_ledger_backend("sqlite-wal");
            backend->load(seed_ledger.string(), "immediate");
            std::string reason;
            require(backend->stage(seed_case(), seed_claims(), "allow", reason),
                    "seed replay reservation failed: " + reason, checks);
            const bool snapshot_created =
                backend->backup_snapshot(clean_snapshot.string(), reason);
            require(snapshot_created, "seed snapshot backup failed: " + reason,
                    checks);
            backend->close();
        }
        require(fs::is_regular_file(clean_snapshot),
                "clean replay snapshot was not published", checks);
        // Ordinary backend load is a mutating WAL-mode observation. Exercise it
        // on a disposable clone so the canonical snapshot remains immutable
        // evidence for every hostile read-only verifier corpus below.
        const fs::path ordinary_reload_copy = root / "ordinary-reload.sqlite";
        clone_snapshot(clean_snapshot, ordinary_reload_copy);
        require(reload_rejection(ordinary_reload_copy).empty(),
                "clean replay snapshot failed ordinary reload", checks);

        const fs::path orphan = root / "orphan.sqlite";
        clone_snapshot(clean_snapshot, orphan);
        mutate_sql(orphan,
            "UPDATE ingress_sender_replay_cache SET prepared_sequence=999;");
        // The write backend enables WAL before it verifies hostile rows, so it
        // is itself a mutating observer. Exercise the namespace-free restore
        // verifier first; otherwise the test contaminates its own fixture by
        // changing the main header from rollback format 1/1 to WAL format 2/2.
        const std::string restore_orphan = restore_rejection(
            orphan, root / "orphan-restore-destination.sqlite");
        require(!restore_orphan.empty(),
                "orphaned replay row was accepted during snapshot restore", checks);
        require(restore_orphan.find("foreign_key_check") != std::string::npos,
                "snapshot restore did not report the foreign-key violation: " +
                    restore_orphan,
                checks);
        require_rejected(orphan, "foreign_key_check", "orphaned prepared binding", checks);

        const fs::path malformed_digest = root / "malformed-digest.sqlite";
        clone_snapshot(clean_snapshot, malformed_digest);
        mutate_sql(malformed_digest,
            "UPDATE ingress_sender_replay_cache "
            "SET replay_key_sha256='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';");
        require_rejected(malformed_digest, "malformed_replay_key_digest",
                         "uppercase replay digest", checks);

        const fs::path real_integer = root / "real-integer.sqlite";
        clone_snapshot(clean_snapshot, real_integer);
        mutate_sql(real_integer,
            "UPDATE ingress_sender_replay_cache SET observed_at_epoch=1000.5;");
        require_rejected(real_integer, "wrong_storage_class",
                         "REAL value in INTEGER evidence", checks);

        const fs::path embedded_nul = root / "embedded-nul.sqlite";
        clone_snapshot(clean_snapshot, embedded_nul);
        mutate_sql(embedded_nul,
            "UPDATE ingress_sender_replay_cache "
            "SET principal='principal' || char(0) || 'hidden';");
        require_rejected(embedded_nul, "principal_contains_control",
                         "embedded-NUL principal", checks);

        const fs::path oversized_principal = root / "oversized-principal.sqlite";
        clone_snapshot(clean_snapshot, oversized_principal);
        mutate_principal(oversized_principal, std::string(4097, 'p'));
        require_rejected(oversized_principal, "byte_limit_exceeded",
                         "oversized principal", checks);

        const fs::path duplicate_effect = root / "duplicate-effect.sqlite";
        clone_snapshot(clean_snapshot, duplicate_effect);
        mutate_sql(duplicate_effect,
            "INSERT INTO ingress_sender_replay_cache "
            "SELECT "
            "'9999999999999999999999999999999999999999999999999999999999999999',"
            "format,service_config_sha256,ingress_profile_sha256,"
            "sender_replay_cache_instance_id,sender_proof_kid,principal,"
            "'abcdefghijklmnop2',issued_at_epoch,observed_at_epoch,"
            "replay_window_seconds,material_sha256,prepared_sequence,"
            "prepared_entry_hash,effect_idempotency_key "
            "FROM ingress_sender_replay_cache;");
        require_rejected(duplicate_effect,
                         "multiple ingress sender replay rows",
                         "duplicate reservation for one prepared effect", checks);

        const fs::path impossible_future = root / "impossible-future.sqlite";
        clone_snapshot(clean_snapshot, impossible_future);
        mutate_sql(impossible_future,
            "UPDATE ingress_sender_replay_cache "
            "SET observed_at_epoch=9223372036854774807,"
            "issued_at_epoch=9223372036854775807;");
        require_rejected(impossible_future, "issued_after_future_skew",
                         "overflow-edge future timestamp", checks);

        fs::remove_all(root);
        std::cout << "sqlite_ingress_sender_replay_integrity_checks=" << checks << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sqlite_ingress_sender_replay_integrity_failure="
                  << error.what() << "\n";
        std::error_code ignored;
        fs::remove_all(root, ignored);
        return 1;
    }
}
