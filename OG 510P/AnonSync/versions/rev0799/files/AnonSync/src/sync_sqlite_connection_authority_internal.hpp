#pragma once

#include <cstdint>
#include <string>

#include "sync_sqlite_mutex_capability.hpp"

struct sqlite3;
struct sqlite3_mutex;

namespace anonsync {

struct SyncSqliteRetainedMutexCapabilityState;

// Process-local proof that one exact typed transaction owns the transaction
// stack of an AnonSync-authorized SQLite connection. An unfenced proof is used
// only for connections on which no AnonSync authorizer has been installed.
// This type is private to the SQLite support implementation and is never
// serialized or exposed as domain evidence. Retained mutex ownership is also
// bound to one monotonic C++ thread incarnation because SQLite requires the
// same thread to leave a recursive mutex that entered it.
struct SyncSqliteTransactionBoundaryProof final {
    sqlite3* db = nullptr;
    SyncSqliteProcessId process_id = 0;
    std::uint64_t process_salt = 0;
    std::uint64_t connection_incarnation = 0;
    std::uint64_t authorizer_generation = 0;
    std::uint64_t transaction_generation = 0;
    SyncSqliteThreadIncarnation owner_thread_incarnation = 0;
    sqlite3_mutex* retained_connection_mutex = nullptr;
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state = nullptr;
    bool fenced = false;
};

enum class SyncSqliteTransactionBoundaryEnd {
    Commit,
    Rollback
};

// Reports whether this handle already carries AnonSync-owned client data. This
// does not claim that the callback is still installed; callers use it only to
// decide whether a restrictive policy must be reinstalled before typed SQL can
// recover from alien callback replacement.
[[nodiscard]] bool sync_sqlite_connection_authority_state_present_or_throw(
    sqlite3* db,
    const std::string& label);

// BEGIN is prepared and executed while a single-use SQLITE_TRANSACTION permit
// is armed. When an AnonSync connection authority is present, the returned
// proof binds later COMMIT/ROLLBACK to the same connection incarnation,
// authorizer generation, and typed transaction generation.
[[nodiscard]] SyncSqliteTransactionBoundaryProof
begin_sync_sqlite_transaction_boundary_or_throw(
    sqlite3* db,
    const std::string& begin_sql,
    const std::string& label);

// Ends the exact transaction generation. Raw transaction SQL and every
// SQLITE_SAVEPOINT operation remain denied by the authorizer bridge.
void end_sync_sqlite_transaction_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof,
    SyncSqliteTransactionBoundaryEnd operation,
    const std::string& label);

// Best-effort destructor path. It attempts only the exact guarded ROLLBACK.
// After alien callback replacement it deliberately does not issue raw SQL:
// SQLite exposes no transaction-generation identifier, so a raw fallback
// could roll back a later transaction that this guard never owned.
void rollback_sync_sqlite_transaction_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept;

// Releases the recursive connection-mutex entry retained by successful BEGIN.
// The typed owner calls this exactly once when its generation is revoked.
void release_sync_sqlite_transaction_mutex_noexcept(
    SyncSqliteTransactionBoundaryProof& proof) noexcept;

// Returns true only while the exact connection incarnation, authorizer
// generation, transaction generation, and owned authorizer callback remain
// current and SQLite still reports an explicit transaction.
[[nodiscard]] bool sync_sqlite_transaction_boundary_authorizes_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept;

// Revokes process-local transaction ownership after an observed automatic or
// out-of-band rollback. This does not execute SQL.
void abandon_sync_sqlite_transaction_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept;

}  // namespace anonsync
