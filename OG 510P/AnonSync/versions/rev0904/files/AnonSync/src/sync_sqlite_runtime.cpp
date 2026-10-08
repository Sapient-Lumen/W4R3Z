#include "sync_sqlite_runtime.hpp"

#include "sqlite_exact_value.hpp"

#include <array>
#include <stdexcept>
#include <string>

#include <sqlite3.h>

namespace anonsync {
namespace {

#if defined(ANONSYNC_BUNDLED_SQLITE)
static_assert(SQLITE_VERSION_NUMBER == 3053003,
              "the reviewed bundled SQLite profile must remain pinned to 3.53.3");
constexpr const char* kExpectedBundledSqliteSourceId =
    "2026-06-26 20:14:12 "
    "d4c0e51e4aeb96955b99185ab9cde75c339e2c29c3f3f12428d364a10d782c62";
#endif

std::string runtime_error_detail(sqlite3* db) {
    const char* message = db != nullptr ? sqlite3_errmsg(db) : nullptr;
    return message != nullptr ? message : "unknown SQLite error";
}

void runtime_exec_or_throw(sqlite3* db,
                           const std::string& sql,
                           const std::string& label) {
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, nullptr);
    if (rc == SQLITE_OK) return;
    const std::string detail = runtime_error_detail(db);
    throw std::runtime_error(label + ": " + detail + " (sqlite rc=" +
                             std::to_string(rc) + ")");
}

std::string runtime_scalar_text_or_throw(sqlite3* db,
                                         const std::string& sql,
                                         const std::string& label) {
    sqlite3_stmt* statement = nullptr;
    const int prepare_rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &statement, nullptr);
    if (prepare_rc != SQLITE_OK) {
        throw std::runtime_error(label + " prepare: " + runtime_error_detail(db));
    }
    struct Finalize final {
        sqlite3_stmt* statement = nullptr;
        ~Finalize() { if (statement != nullptr) sqlite3_finalize(statement); }
    } finalize{statement};
    const int step_rc = sqlite3_step(statement);
    if (step_rc != SQLITE_ROW) {
        throw std::runtime_error(label + " query: " + runtime_error_detail(db) +
                                 " (sqlite rc=" + std::to_string(step_rc) + ")");
    }
    return persistence::sqlite_exact_text_or_throw(statement, 0, label);
}

long long runtime_scalar_i64_or_throw(sqlite3* db,
                                      const std::string& sql,
                                      const std::string& label) {
    sqlite3_stmt* statement = nullptr;
    const int prepare_rc = sqlite3_prepare_v2(db, sql.c_str(), -1, &statement, nullptr);
    if (prepare_rc != SQLITE_OK) {
        throw std::runtime_error(label + " prepare: " + runtime_error_detail(db));
    }
    struct Finalize final {
        sqlite3_stmt* statement = nullptr;
        ~Finalize() { if (statement != nullptr) sqlite3_finalize(statement); }
    } finalize{statement};
    const int step_rc = sqlite3_step(statement);
    if (step_rc != SQLITE_ROW) {
        throw std::runtime_error(label + " query: " + runtime_error_detail(db) +
                                 " (sqlite rc=" + std::to_string(step_rc) + ")");
    }
    return persistence::sqlite_exact_i64_or_throw(statement, 0, label);
}

std::string lower_ascii(std::string value) {
    for (char& c : value) {
        if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
    }
    return value;
}

void require_header_and_mutex_profile_or_throw(
    const SyncSqliteRuntimeProfile& profile,
    const std::string& prefix) {
    if (!profile.header_runtime_version_match) {
        throw std::runtime_error(
            prefix + " refused journal configuration: SQLite header/runtime version mismatch "
            "(header=" + std::to_string(SQLITE_VERSION_NUMBER) + ", runtime=" +
            std::to_string(profile.version_number) + ", source_id=" +
            profile.source_id + ")");
    }
    if (profile.threadsafe == 0) {
        throw std::runtime_error(
            prefix + " refused journal configuration: SQLite was compiled without mutex support");
    }
}

void require_wal_profile_safe_or_throw(const SyncSqliteRuntimeProfile& profile,
                                       const std::string& prefix) {
    require_header_and_mutex_profile_or_throw(profile, prefix);
    if (!profile.wal_reset_fix_present) {
        throw std::runtime_error(
            prefix + " refused WAL: SQLite " + profile.version + " (" +
            std::to_string(profile.version_number) +
            ") is not known to contain the WAL-reset corruption fix; require "
            "3.51.3+, 3.50.7 on the 3.50 branch, or 3.44.6 on the 3.44 branch");
    }
#if defined(ANONSYNC_BUNDLED_SQLITE)
    if (profile.version_number != 3053003 ||
        profile.source_id != kExpectedBundledSqliteSourceId) {
        throw std::runtime_error(
            prefix + " refused WAL: bundled SQLite provenance mismatch (version=" +
            profile.version + ", source_id=" + profile.source_id + ")");
    }
    // SQLITE_TRUSTED_SCHEMA is intentionally verified through the live PRAGMA
    // in the runtime policy test: SQLite does not expose that default through
    // sqlite3_compileoption_used() on every supported release.
    constexpr std::array<const char*, 10> kRequiredCompileOptions = {
        "THREADSAFE=1",
        "DQS=0",
        "DEFAULT_FOREIGN_KEYS",
        "DEFAULT_MEMSTATUS=0",
        "DEFAULT_SYNCHRONOUS=2",
        "DEFAULT_WAL_SYNCHRONOUS=2",
        "ENABLE_API_ARMOR",
        "OMIT_LOAD_EXTENSION",
        "OMIT_SHARED_CACHE",
        "SECURE_DELETE",
    };
    for (const char* option : kRequiredCompileOptions) {
        if (sqlite3_compileoption_used(option) == 0) {
            throw std::runtime_error(
                prefix + " refused WAL: bundled SQLite compile option missing: " +
                option);
        }
    }
#endif
}

}  // namespace

bool sync_sqlite_version_has_wal_reset_fix(int version_number) noexcept {
    if (version_number >= 3051003) return true;
    if (version_number >= 3050007 && version_number < 3051000) return true;
    if (version_number >= 3044006 && version_number < 3045000) return true;
    return false;
}

SyncSqliteRuntimeProfile sync_sqlite_runtime_profile() {
    SyncSqliteRuntimeProfile profile;
    const char* version = sqlite3_libversion();
    const char* source_id = sqlite3_sourceid();
    profile.version = version != nullptr ? version : "";
    profile.source_id = source_id != nullptr ? source_id : "";
    profile.version_number = sqlite3_libversion_number();
    profile.threadsafe = sqlite3_threadsafe();
    profile.header_runtime_version_match =
        profile.version_number == SQLITE_VERSION_NUMBER;
    profile.wal_reset_fix_present =
        sync_sqlite_version_has_wal_reset_fix(profile.version_number);
#if defined(ANONSYNC_BUNDLED_SQLITE)
    profile.bundled = true;
#endif
    return profile;
}

void require_sync_sqlite_wal_runtime_safe_or_throw(const std::string& label) {
    const SyncSqliteRuntimeProfile profile = sync_sqlite_runtime_profile();
    const std::string prefix = label.empty() ? "SQLite WAL runtime gate" : label;
    require_wal_profile_safe_or_throw(profile, prefix);
}

SyncSqliteRuntimeProfile configure_sync_sqlite_wal_full_or_throw(
    sqlite3* db,
    const std::string& label) {
    const std::string prefix = label.empty() ? "SQLite WAL/FULL configuration" : label;
    if (db == nullptr) throw std::invalid_argument(prefix + ": database handle is null");
    if (sqlite3_get_autocommit(db) == 0) {
        throw std::logic_error(prefix + ": WAL/FULL must be configured outside a transaction");
    }

    const SyncSqliteRuntimeProfile profile = sync_sqlite_runtime_profile();
    require_wal_profile_safe_or_throw(profile, prefix + " runtime gate");

    const std::string journal_mode = lower_ascii(runtime_scalar_text_or_throw(
        db, "PRAGMA journal_mode=WAL;", prefix + " journal_mode negotiation"));
    if (journal_mode != "wal") {
        throw std::runtime_error(prefix +
                                 ": journal_mode verification expected wal but received " +
                                 journal_mode);
    }
    runtime_exec_or_throw(db, "PRAGMA synchronous=FULL;",
                          prefix + " synchronous FULL setup");
    if (runtime_scalar_i64_or_throw(db, "PRAGMA synchronous;",
                                    prefix + " synchronous verification") != 2) {
        throw std::runtime_error(prefix + ": synchronous verification expected FULL");
    }
    return profile;
}

SyncSqliteConcurrentJournalProfile
configure_sync_sqlite_concurrent_durable_journal_or_throw(
    sqlite3* db,
    const std::string& label) {
    const std::string prefix = label.empty()
        ? "SQLite concurrent journal policy"
        : label;
    const SyncSqliteRuntimeProfile runtime =
        configure_sync_sqlite_wal_full_or_throw(db, prefix);

    SyncSqliteConcurrentJournalProfile profile;
    profile.runtime_version_number = runtime.version_number;
    profile.runtime_version = runtime.version;
    profile.runtime_source_id = runtime.source_id;
    profile.journal_mode = "wal";
    profile.header_runtime_version_match = runtime.header_runtime_version_match;
    profile.runtime_threadsafe = runtime.threadsafe != 0;
    profile.bundled = runtime.bundled;
    profile.wal_reset_fix_known = runtime.wal_reset_fix_present;
    profile.rollback_journal_fallback_active = false;
    return profile;
}

}  // namespace anonsync
