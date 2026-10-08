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
// The observer runs synchronously after each validated step and exists so crash,
// concurrency, and restart models can act at an exact cutpoint. It must not use
// the source or destination handles.
SqliteLiveBackupEvidence copy_sqlite_live_snapshot_bounded_or_throw(
    sqlite3* destination_database,
    sqlite3* source_database,
    const std::string& label,
    const SqliteSnapshotGeometryPolicy& policy = {},
    SqliteLiveBackupStepObserver observer = nullptr,
    void* observer_context = nullptr);

}  // namespace anonsync::persistence
