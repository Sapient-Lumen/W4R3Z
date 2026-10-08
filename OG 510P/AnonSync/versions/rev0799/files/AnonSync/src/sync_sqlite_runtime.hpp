#pragma once

#include <string>

struct sqlite3;

namespace anonsync {

struct SyncSqliteRuntimeProfile {
    std::string version;
    std::string source_id;
    int version_number = 0;
    int threadsafe = 0;
    bool header_runtime_version_match = false;
    bool wal_reset_fix_present = false;
    bool bundled = false;
};

// Durable evidence for the journal policy verified for an internal store.
// Official builds require a runtime with the March 2026 WAL-reset fix and use
// WAL/FULL. rollback_journal_fallback_active is retained as evidence-schema
// compatibility but is always false: AnonSync never silently weakens policy.
struct SyncSqliteConcurrentJournalProfile {
    int runtime_version_number = 0;
    std::string runtime_version;
    std::string runtime_source_id;
    std::string journal_mode;
    bool header_runtime_version_match = false;
    bool runtime_threadsafe = false;
    bool bundled = false;
    bool wal_reset_fix_known = false;
    bool rollback_journal_fallback_active = false;
};

// SQLite's March 2026 WAL-reset corruption fix first shipped in 3.51.3,
// with maintained-branch backports in 3.50.7 and 3.44.6. This classifier is
// explicit so an affected system-library build cannot silently activate WAL.
bool sync_sqlite_version_has_wal_reset_fix(int version_number) noexcept;
SyncSqliteRuntimeProfile sync_sqlite_runtime_profile();

// Strict gate for every store that enables WAL. Official builds fail closed on
// an affected, mismatched, unthreadsafe, or provenance-divergent runtime.
void require_sync_sqlite_wal_runtime_safe_or_throw(const std::string& label);

// Configure and read back WAL plus synchronous=FULL outside a transaction.
SyncSqliteRuntimeProfile configure_sync_sqlite_wal_full_or_throw(
    sqlite3* db,
    const std::string& label);

// Configure a durable internal-store profile outside a transaction. This is
// a strict alias for verified WAL/FULL and fails closed on an affected,
// mismatched, unthreadsafe, or provenance-divergent runtime.
SyncSqliteConcurrentJournalProfile
configure_sync_sqlite_concurrent_durable_journal_or_throw(
    sqlite3* db,
    const std::string& label);

}  // namespace anonsync
