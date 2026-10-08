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
    SyncProcessIncarnation process_id;
    std::uint64_t process_salt = 0;
    std::uint64_t connection_incarnation = 0;
    std::uint64_t authorizer_generation = 0;
    std::uint64_t transaction_generation = 0;
    SyncSqliteThreadIncarnation owner_thread_incarnation;
    sqlite3_mutex* retained_connection_mutex = nullptr;
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state = nullptr;
    bool fenced = false;
};

enum class SyncSqliteTransactionBoundaryEnd {
    Commit,
    Rollback
};

// Process-local proof for one exact named mark on the SQLite transaction
// stack. Fenced marks are bound to the live typed outer transaction and to one
// monotonically allocated savepoint generation. Unfenced marks exist only on
// connections without AnonSync-owned authorizer state and retain the older
// observation-based compatibility contract.
struct SyncSqliteSavepointBoundaryProof final {
    sqlite3* db = nullptr;
    SyncProcessIncarnation process_id;
    std::uint64_t process_salt = 0;
    std::uint64_t connection_incarnation = 0;
    std::uint64_t authorizer_generation = 0;
    std::uint64_t transaction_generation = 0;
    std::uint64_t savepoint_generation = 0;
    SyncSqliteThreadIncarnation owner_thread_incarnation;
    sqlite3_mutex* retained_connection_mutex = nullptr;
    SyncSqliteRetainedMutexCapabilityState* retained_capability_state = nullptr;
    std::string savepoint_name;
    bool fenced = false;
    bool outermost_unfenced = false;
};

enum class SyncSqliteSavepointBoundaryEnd {
    Release,
    Rollback
};

// A use-time authority probe has three outcomes. Invalid means exact identity
// evidence is known to have changed or ended. Indeterminate means the probe
// itself could not complete (for example SQLITE_NOMEM) and therefore must not
// permanently revoke a generation that may still be live. Callers fail closed
// for the current operation in both non-current states, but may retry only the
// indeterminate one.
enum class SyncSqliteBoundaryAuthorityStatus {
    Current,
    Invalid,
    Indeterminate
};

// Connection-owner teardown hook.  A live authorizer context may not be left
// for sqlite3_close() or same-name client-data destruction to consume.  The
// exact owner calls this after all user borrows and transaction boundaries are
// gone but before strict close.  Any malformed state fails stopped.
void revoke_sync_sqlite_connection_authority_before_close_noexcept(
    sqlite3* db) noexcept;

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

// Ends the exact transaction generation. Raw transaction SQL and unpermitted
// SAVEPOINT operations remain denied by the authorizer bridge. Commit is
// rejected while any typed nested mark remains live; rollback may erase the
// complete stack as an abort boundary.
void end_sync_sqlite_transaction_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof,
    SyncSqliteTransactionBoundaryEnd operation,
    const std::string& label);


// Creates one internal, injection-proof savepoint name. A non-null outer proof
// is required on an AnonSync-authorized connection. A null proof is accepted
// only for an unfenced compatibility connection, where the mark may be either
// nested or outermost.
[[nodiscard]] SyncSqliteSavepointBoundaryProof
begin_sync_sqlite_savepoint_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof* outer_transaction_proof,
    const std::string& label);

// RELEASE closes the exact top mark. Rollback executes ROLLBACK TO followed by
// RELEASE so a caught exception cannot leave a reusable mark behind. Both
// operations enforce LIFO ordering for fenced generations.
void end_sync_sqlite_savepoint_boundary_or_throw(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof,
    SyncSqliteSavepointBoundaryEnd operation,
    const std::string& label);

// Destructor path for the exact mark. It never rewinds across a newer fenced
// mark and never falls back to raw SQL after authorizer replacement.
void rollback_sync_sqlite_savepoint_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof) noexcept;

// Releases the recursive connection-mutex entry retained by a successful
// SAVEPOINT. The typed owner calls this exactly once when its mark is revoked.
void release_sync_sqlite_savepoint_mutex_noexcept(
    SyncSqliteSavepointBoundaryProof& proof) noexcept;

// True while the exact fenced generation remains anywhere in the current
// stack, or (for explicitly unfenced compatibility) while the connection still
// reports an explicit transaction.
[[nodiscard]] SyncSqliteBoundaryAuthorityStatus
sync_sqlite_savepoint_boundary_authority_status_noexcept(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof) noexcept;

[[nodiscard]] bool sync_sqlite_savepoint_boundary_authorizes_noexcept(
    sqlite3* db,
    const SyncSqliteSavepointBoundaryProof& proof) noexcept;

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
[[nodiscard]] SyncSqliteBoundaryAuthorityStatus
sync_sqlite_transaction_boundary_authority_status_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept;

[[nodiscard]] bool sync_sqlite_transaction_boundary_authorizes_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept;

// Revokes process-local transaction ownership after an observed automatic or
// out-of-band rollback. This does not execute SQL.
void abandon_sync_sqlite_transaction_boundary_noexcept(
    sqlite3* db,
    const SyncSqliteTransactionBoundaryProof& proof) noexcept;

}  // namespace anonsync
