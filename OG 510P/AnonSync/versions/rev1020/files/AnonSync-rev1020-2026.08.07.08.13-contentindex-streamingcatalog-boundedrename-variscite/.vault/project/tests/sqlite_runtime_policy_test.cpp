#include "sync_sqlite_runtime.hpp"

#include <cstdio>
#include <ctime>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>

#include <sqlite3.h>

#if defined(__unix__) || defined(__APPLE__)
#include <unistd.h>
#endif

static_assert(std::is_same_v<
              decltype(anonsync::SyncBundledSqliteProfileAttestation{}.expected_version),
              std::string_view>,
              "bundled SQLite attestation must retain an allocation-free evidence view");
static_assert(std::is_same_v<
              decltype(anonsync::SyncBundledSqliteProfileAttestation{}.retained_files),
              std::string_view>,
              "bundled SQLite inventory evidence must remain allocation-free");
static_assert(noexcept(anonsync::sync_bundled_sqlite_profile_attestation()),
              "bundled SQLite attestation must remain allocation-free and noexcept");

namespace {

struct TestState {
    int passed = 0;
    int failed = 0;

    void require(bool condition, const std::string& message) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << message << "\n";
        }
    }

    template <typename Exception, typename Function>
    void require_throws(Function&& function, const std::string& message) {
        try {
            function();
            require(false, message);
        } catch (const Exception&) {
            require(true, message);
        } catch (...) {
            require(false, message + " (wrong exception type)");
        }
    }
};

std::string scalar_text(sqlite3* db, const char* sql) {
    sqlite3_stmt* stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        throw std::runtime_error(std::string("prepare failed: ") + sqlite3_errmsg(db));
    }
    struct Finalize {
        sqlite3_stmt* stmt = nullptr;
        ~Finalize() { if (stmt != nullptr) sqlite3_finalize(stmt); }
    } finalize{stmt};
    const int rc = sqlite3_step(stmt);
    if (rc != SQLITE_ROW) {
        throw std::runtime_error(std::string("query failed: ") + sqlite3_errmsg(db));
    }
    const unsigned char* value = sqlite3_column_text(stmt, 0);
    if (value == nullptr) throw std::runtime_error("scalar query returned null");
    return reinterpret_cast<const char*>(value);
}

void exec(sqlite3* db, const char* sql) {
    char* error = nullptr;
    const int rc = sqlite3_exec(db, sql, nullptr, nullptr, &error);
    if (rc == SQLITE_OK) return;
    const std::string detail = error != nullptr ? error : sqlite3_errmsg(db);
    if (error != nullptr) sqlite3_free(error);
    throw std::runtime_error("exec failed: " + detail);
}

}  // namespace

int main() {
    TestState test;
    sqlite3* db = nullptr;
#if defined(__unix__) || defined(__APPLE__)
    const long long pid = static_cast<long long>(::getpid());
#else
    const long long pid = 0;
#endif
    const std::string path = "/tmp/anonsync-sqlite-runtime-policy-" +
                             std::to_string(static_cast<long long>(std::time(nullptr))) + "-" +
                             std::to_string(pid) + ".sqlite";
    auto cleanup = [&]() {
        if (db != nullptr) {
            sqlite3_close_v2(db);
            db = nullptr;
        }
        std::remove(path.c_str());
        std::remove((path + "-wal").c_str());
        std::remove((path + "-shm").c_str());
        std::remove((path + "-journal").c_str());
    };
    cleanup();

    try {
        using anonsync::sync_sqlite_version_has_wal_reset_fix;
        test.require(!sync_sqlite_version_has_wal_reset_fix(3044005),
                     "3.44.5 is affected");
        test.require(sync_sqlite_version_has_wal_reset_fix(3044006),
                     "3.44.6 has the maintained-branch fix");
        test.require(!sync_sqlite_version_has_wal_reset_fix(3045000),
                     "3.45.0 is not covered by the 3.44 backport");
        test.require(!sync_sqlite_version_has_wal_reset_fix(3050006),
                     "3.50.6 is affected");
        test.require(sync_sqlite_version_has_wal_reset_fix(3050007),
                     "3.50.7 has the maintained-branch fix");
        test.require(!sync_sqlite_version_has_wal_reset_fix(3051000),
                     "3.51.0 is affected");
        test.require(!sync_sqlite_version_has_wal_reset_fix(3051002),
                     "3.51.2 is affected");
        test.require(sync_sqlite_version_has_wal_reset_fix(3051003),
                     "3.51.3 has the mainline fix");
        test.require(sync_sqlite_version_has_wal_reset_fix(3053003),
                     "3.53.3 inherits the mainline fix");

        const anonsync::SyncSqliteRuntimeProfile runtime =
            anonsync::sync_sqlite_runtime_profile();
        const anonsync::SyncBundledSqliteProfileAttestation
            bundled_attestation =
                anonsync::sync_bundled_sqlite_profile_attestation();
        test.require(runtime.bundled == bundled_attestation.bundled,
                     "runtime and reviewed profile agree on bundled mode");
        test.require(runtime.bundled_provenance_match ==
                         bundled_attestation.runtime_identity_match,
                     "runtime preserves reviewed provenance result");
        test.require(runtime.header_runtime_version_match,
                     "SQLite header and runtime versions match");
        test.require(runtime.threadsafe != 0,
                     "SQLite runtime has mutex support");
        test.require(runtime.wal_reset_fix_present ==
                         sync_sqlite_version_has_wal_reset_fix(runtime.version_number),
                     "runtime fix flag agrees with classifier");
        test.require(!runtime.version.empty() && !runtime.source_id.empty(),
                     "runtime exposes version and source identity");

        test.require_throws<std::invalid_argument>(
            [&] {
                (void)anonsync::configure_sync_sqlite_concurrent_durable_journal_or_throw(
                    nullptr, "runtime policy null handle");
            },
            "negotiated journal helper rejects null handle");
        test.require_throws<std::invalid_argument>(
            [&] {
                (void)anonsync::configure_sync_sqlite_wal_full_or_throw(
                    nullptr, "runtime policy strict null handle");
            },
            "strict WAL helper rejects null handle");

        if (sqlite3_open_v2(path.c_str(),
                            &db,
                            SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE |
                                SQLITE_OPEN_FULLMUTEX,
                            nullptr) != SQLITE_OK) {
            throw std::runtime_error(std::string("database open failed: ") +
                                     (db != nullptr ? sqlite3_errmsg(db) : "unknown"));
        }

        exec(db, "BEGIN;");
        test.require_throws<std::logic_error>(
            [&] {
                (void)anonsync::configure_sync_sqlite_concurrent_durable_journal_or_throw(
                    db, "runtime policy transaction");
            },
            "negotiated journal helper rejects active transaction");
        test.require_throws<std::logic_error>(
            [&] {
                (void)anonsync::configure_sync_sqlite_wal_full_or_throw(
                    db, "runtime policy strict transaction");
            },
            "strict WAL helper rejects active transaction");
        exec(db, "ROLLBACK;");

        const anonsync::SyncSqliteConcurrentJournalProfile evidence =
            anonsync::configure_sync_sqlite_concurrent_durable_journal_or_throw(
                db, "runtime policy negotiated journal");
        test.require(runtime.wal_reset_fix_present,
                     "official runtime contains the WAL-reset corruption fix");
        test.require(evidence.runtime_version_number == runtime.version_number,
                     "journal evidence preserves runtime version number");
        test.require(evidence.runtime_version == runtime.version,
                     "journal evidence preserves runtime version string");
        test.require(evidence.runtime_source_id == runtime.source_id,
                     "journal evidence preserves runtime source identity");
        test.require(evidence.header_runtime_version_match,
                     "journal evidence records header/runtime match");
        test.require(evidence.runtime_threadsafe,
                     "journal evidence records mutex support");
        test.require(evidence.bundled == runtime.bundled,
                     "journal evidence preserves bundled flag");
        test.require(evidence.bundled_provenance_match ==
                         runtime.bundled_provenance_match,
                     "journal evidence preserves bundled provenance result");
        test.require(evidence.wal_reset_fix_known,
                     "journal evidence records the required WAL-reset fix");
        test.require(!evidence.rollback_journal_fallback_active,
                     "journal policy never advertises a silent rollback fallback");
        test.require(evidence.journal_mode == "wal",
                     "journal evidence reports strict WAL mode");
        test.require(scalar_text(db, "PRAGMA journal_mode;") == "wal",
                     "database reports strict WAL mode");
        test.require(scalar_text(db, "PRAGMA synchronous;") == "2",
                     "strict journal policy enforces synchronous=FULL");

        bool gate_ok = true;
        try {
            anonsync::require_sync_sqlite_wal_runtime_safe_or_throw(
                "runtime policy strict gate");
        } catch (...) {
            gate_ok = false;
        }
        test.require(gate_ok,
                     "strict WAL gate accepts fixed runtime");
        const anonsync::SyncSqliteRuntimeProfile strict =
            anonsync::configure_sync_sqlite_wal_full_or_throw(
                db, "runtime policy strict WAL/FULL");
        test.require(strict.source_id == runtime.source_id,
                     "strict WAL helper returns exact runtime identity");
        test.require(scalar_text(db, "PRAGMA journal_mode;") == "wal",
                     "strict WAL helper verifies WAL mode");

        if (runtime.bundled) {
            test.require(bundled_attestation.runtime_identity_match,
                         "bundled runtime exactly matches reviewed semantic identity");
            test.require(runtime.version_number ==
                             bundled_attestation.expected_version_number &&
                             runtime.version == bundled_attestation.expected_version &&
                             runtime.source_id == bundled_attestation.expected_source_id,
                         "bundled runtime remains pinned to the generated profile");
            test.require(bundled_attestation.sqlite3_c_sha256.size() == 64U &&
                             bundled_attestation.sqlite3_c_sha3_256.size() == 64U &&
                             bundled_attestation.sqlite3_h_sha256.size() == 64U &&
                             bundled_attestation.sqlite3ext_h_sha256.size() == 64U &&
                             bundled_attestation.license_sha256.size() == 64U &&
                             bundled_attestation.provenance_sha256.size() == 64U,
                         "bundled profile exposes every reviewed vendor digest");
            test.require(!bundled_attestation.amalgamation_archive.empty() &&
                             bundled_attestation.amalgamation_archive_sha3_256.size() == 64U &&
                             bundled_attestation.retained_files ==
                                 "LICENSE.md;UPSTREAM-PROVENANCE.md;sqlite3.c;"
                                 "sqlite3.h;sqlite3ext.h",
                         "bundled profile exposes upstream archive and closed inventory evidence");
            test.require(scalar_text(db, "PRAGMA foreign_keys;") == "1",
                         "bundled default enables foreign keys");
            test.require(scalar_text(db, "PRAGMA trusted_schema;") == "0",
                         "bundled default disables trusted schema");
            test.require(scalar_text(db, "PRAGMA secure_delete;") == "1",
                         "bundled default enables secure delete");
        }

        exec(db,
             "CREATE TABLE evidence(id INTEGER PRIMARY KEY, value TEXT NOT NULL);"
             "BEGIN IMMEDIATE;"
             "INSERT INTO evidence(value) VALUES('durable');"
             "COMMIT;");
        test.require(scalar_text(db, "SELECT value FROM evidence WHERE id=1;") ==
                         "durable",
                     "selected durable mode commits evidence");
        test.require(scalar_text(db, "PRAGMA integrity_check;") == "ok",
                     "selected durable mode passes integrity_check");

        std::cout << "anonsync sqlite runtime policy test runtime=" << runtime.version
                  << " source_id=" << runtime.source_id
                  << " journal=" << evidence.journal_mode
                  << " bundled=" << (runtime.bundled ? "true" : "false")
                  << " provenance_match="
                  << (runtime.bundled_provenance_match ? "true" : "false")
                  << " sqlite3_c_sha3="
                  << bundled_attestation.sqlite3_c_sha3_256
                  << " passed=" << test.passed
                  << " failed=" << test.failed << "\n";
        cleanup();
        return test.failed == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        std::cerr << "anonsync sqlite runtime policy test fatal after "
                  << test.passed << " checks: " << error.what() << "\n";
        cleanup();
        return 2;
    }
}
