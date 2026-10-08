#pragma once

#include <cstdint>
#include <string>

#include "sync_sqlite_process_incarnation.hpp"

struct sqlite3;

namespace anonsync {

// Process-local, non-serializable identity for one exact C++ thread lifetime.
// SQLite requires a recursive mutex to be left by the same thread that entered
// it. std::thread::id values may be reused after a thread exits, so retained
// SQLite mutex capabilities bind to this monotonic incarnation instead.
using SyncSqliteThreadIncarnation = std::uint64_t;

// Opaque SQLite-owned sentinel for one exact connection lifetime. Each
// AnonSync capability that retains sqlite3_db_mutex() holds one counter entry.
// Destruction with a nonzero count is a fatal close-order violation. The count
// is only a lifetime pin, not an authorization generation: exact authority is
// still carried by the owning lease/transaction and its thread incarnation.
struct SyncSqliteRetainedMutexCapabilityState;

[[nodiscard]] SyncSqliteThreadIncarnation
current_sync_sqlite_thread_incarnation_noexcept() noexcept;

[[nodiscard]] bool sync_sqlite_thread_incarnation_is_current(
    SyncSqliteThreadIncarnation expected) noexcept;

void require_sync_sqlite_thread_incarnation_or_throw(
    SyncSqliteThreadIncarnation expected,
    const std::string& label);

// These functions must be called while the connection's serialized mutex is
// held. The returned pointer is non-owning; SQLite owns the sentinel through
// client data. A live counter entry makes close/replacement fail stopped before
// control can return to an owner whose retained mutex pointer became invalid;
// it does not independently extend SQLite's object lifetime.
[[nodiscard]] SyncSqliteRetainedMutexCapabilityState*
retain_sync_sqlite_mutex_capability_or_throw(
    sqlite3* db,
    const std::string& label);

void release_sync_sqlite_mutex_capability_noexcept(
    SyncSqliteRetainedMutexCapabilityState*& state) noexcept;

[[nodiscard]] bool sync_sqlite_mutex_capability_is_live_noexcept(
    const SyncSqliteRetainedMutexCapabilityState* state) noexcept;

// A retained SQLite mutex cannot be safely released by another thread or
// after SQLite has begun destroying its connection. Those violations cannot
// be repaired inside a noexcept destructor, so they exit directly without
// invoking a replaceable C++ terminate handler or process teardown hooks.
[[noreturn]] void fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept()
    noexcept;

}  // namespace anonsync
