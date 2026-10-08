#pragma once

#include "sync_process_incarnation.hpp"
#include "sync_thread_incarnation.hpp"

#include <string_view>

struct sqlite3;
struct sqlite3_mutex;

namespace anonsync {

// Selects the allocation-free destructor/teardown lane. Invalid input or a
// missing serialized mutex is a lifetime-protocol violation and fails stopped
// rather than throwing across a noexcept boundary.
struct SyncSqliteDatabaseMutexFailStopTag final {};
inline constexpr SyncSqliteDatabaseMutexFailStopTag
    kSyncSqliteDatabaseMutexFailStop{};

// Process- and exact-thread-bound owner for one recursive sqlite3_db_mutex()
// entry. The guard is intentionally nonmovable: SQLite requires the same thread
// to leave a mutex that entered it. A guard object itself may not cross a fork
// or thread boundary; the typed database-generation owners remain responsible
// for rejecting an inherited raw sqlite3* before constructing a new guard.
//
// This owner is deliberately serialized/FULLMUTEX-only. The narrow raw
// busy-timeout compatibility lane has a separate type that cannot authorize a
// retained callback claim or transfer a mutex entry.
//
// The throwing constructor is used at ordinary API boundaries. The fail-stop
// constructor is reserved for noexcept teardown after a live owner has already
// proved that its database is serialized. release() transfers the exact mutex
// entry to a longer-lived typed lease; every other path leaves it on scope exit.
class SyncSqliteDatabaseMutexGuard final {
public:
    SyncSqliteDatabaseMutexGuard(sqlite3* database,
                                 std::string_view label);

    SyncSqliteDatabaseMutexGuard(
        sqlite3* database,
        SyncSqliteDatabaseMutexFailStopTag) noexcept;

    ~SyncSqliteDatabaseMutexGuard() noexcept;

    SyncSqliteDatabaseMutexGuard(
        const SyncSqliteDatabaseMutexGuard&) = delete;
    SyncSqliteDatabaseMutexGuard& operator=(
        const SyncSqliteDatabaseMutexGuard&) = delete;
    SyncSqliteDatabaseMutexGuard(SyncSqliteDatabaseMutexGuard&&) = delete;
    SyncSqliteDatabaseMutexGuard& operator=(
        SyncSqliteDatabaseMutexGuard&&) = delete;

    [[nodiscard]] bool owns_mutex() const noexcept;
    [[nodiscard]] sqlite3_mutex* mutex_identity() const noexcept;

    // True only while this object owns the serialized mutex entry for the
    // exact database handle. This is the compile-time witness consumed by
    // singleton callback-claim mutations.
    [[nodiscard]] bool authorizes(sqlite3* database) const noexcept;

    // Transfer the entered recursive mutex to a typed retained lease.
    [[nodiscard]] sqlite3_mutex* release() noexcept;

private:
    void require_current_execution_noexcept() const noexcept;

    sqlite3* database_ = nullptr;
    sqlite3_mutex* mutex_ = nullptr;
    SyncProcessIncarnation process_id_;
    SyncThreadIncarnation thread_id_;
};

}  // namespace anonsync
