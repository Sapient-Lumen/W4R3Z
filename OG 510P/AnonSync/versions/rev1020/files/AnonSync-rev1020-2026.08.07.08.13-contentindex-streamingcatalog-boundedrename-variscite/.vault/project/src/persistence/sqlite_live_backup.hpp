#pragma once

#include "sqlite_snapshot_geometry.hpp"

#include <cstdint>
#include <string>

struct sqlite3;

namespace anonsync::persistence {

// Each SQLite effect is intentionally small. A source that loses its pinned read
// transaction, changes reported geometry, restarts, or stops making progress is
// rejected before another page batch can be copied.
inline constexpr std::uint32_t kSqliteLiveBackupPagesPerStep = 64U;

struct SqliteLiveBackupStepObservation {
    std::uint64_t step_index = 0;
    std::uint32_t requested_pages = 0;
    int sqlite_result = 0;
    std::uint64_t reported_page_count = 0;
    std::uint64_t reported_remaining_pages = 0;
};

using SqliteLiveBackupStepObserver = void (*)(
    const SqliteLiveBackupStepObservation& observation,
    void* context);

struct SqliteLiveBackupEvidence {
    SqliteSnapshotGeometry source_geometry{};
    std::uint64_t step_calls = 0;
    std::uint64_t maximum_reported_page_count = 0;
    std::uint64_t maximum_reported_remaining_pages = 0;
};

// Copy one exact, transactionally pinned source image into an already-open,
// empty, private in-memory destination. Both handles must enter without an
// explicit or implicit main-database transaction, and the source must be
// FULLMUTEX protected. This boundary begins its own read transaction,
// establishes exact page geometry inside that transaction, performs fixed-size
// backup steps, checks SQLite's page-count/remaining evidence after every step,
// verifies the completed destination geometry, and releases the source
// transaction before returning.
//
// The observer runs synchronously after each validated nonterminal SQLITE_OK
// step and exists so crash, concurrency, and restart models can act between
// bounded page-copy effects. It is deliberately not invoked after SQLITE_DONE:
// SQLite has already completed the destination transaction at that cutpoint, so
// a throwable callback could otherwise report failure after committed mutation.
// The observer must not use the source or destination handles.
SqliteLiveBackupEvidence copy_sqlite_live_snapshot_bounded_or_throw(
    sqlite3* destination_database,
    sqlite3* source_database,
    const std::string& label,
    const SqliteSnapshotGeometryPolicy& policy = {},
    SqliteLiveBackupStepObserver observer = nullptr,
    void* observer_context = nullptr);

// Replace one already-open, named, writable destination database with the exact
// transactionally pinned source image. Both handles must be FULLMUTEX protected
// and transaction-free. The destination must be a named database, must have the
// same page size as the source before the first backup step, and remains under
// SQLite's own destination write transaction until the bounded copy completes.
// A failure before completion therefore rolls the destination back rather than
// exposing a partial logical image. The source may be a filename-free detached
// read-only image; the destination must be writable.
SqliteLiveBackupEvidence replace_sqlite_live_database_bounded_or_throw(
    sqlite3* destination_database,
    sqlite3* source_database,
    const std::string& label,
    const SqliteSnapshotGeometryPolicy& policy = {},
    SqliteLiveBackupStepObserver observer = nullptr,
    void* observer_context = nullptr);

}  // namespace anonsync::persistence
