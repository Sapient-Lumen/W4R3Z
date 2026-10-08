#pragma once

#include "sync_process_incarnation.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"

#include <string>
#include <string_view>

struct sqlite3;

namespace anonsync::persistence {

// Connection-scoped lifetime sentinel for a retained SQLite callback context.
//
// SQLite callback setter APIs generally retain a raw context address but offer
// no destructor and, for several setters, no getter.  This owner attaches a
// separately allocated sentinel through sqlite3_set_clientdata().  SQLite then
// calls the sentinel destructor on actual database destruction or named-slot
// replacement. Any such destruction while the callback owner is live fails
// stopped before a later C++ destructor can call SQLite through a stale
// connection address.
//
// sqlite3_close_v2() may return SQLITE_OK while outstanding statements, blobs,
// or backups keep a zombie connection allocated.  In that case SQLite has not
// destroyed the client-data slot yet, so no client-data sentinel can reject the
// close_v2 call synchronously.  Exact-generation typed ownership prevents the
// reviewed close path from entering that state; source/runtime audits must keep
// unmediated close_v2 calls outside every live retained-callback scope.  If a
// raw close_v2 violation nevertheless defers destruction, this claim fails
// stopped when SQLite eventually destroys the connection.
//
// The sentinel has no authority to unregister a callback. The enclosing owner
// must first revoke its callback, then call detach() synchronously, and only
// then release any exact-generation database borrow. Every database-touching
// method requires a live SyncSqliteDatabaseMutexGuard for the exact handle; the
// singleton claim transition therefore cannot compile without the serialized
// critical-section witness. The class deliberately does not auto-detach: doing
// so after premature close would itself dereference invalid SQLite storage.
class SqliteRetainedCallbackClaim final {
public:
    SqliteRetainedCallbackClaim() noexcept;
    ~SqliteRetainedCallbackClaim();

    SqliteRetainedCallbackClaim(const SqliteRetainedCallbackClaim&) = delete;
    SqliteRetainedCallbackClaim& operator=(
        const SqliteRetainedCallbackClaim&) = delete;
    SqliteRetainedCallbackClaim(SqliteRetainedCallbackClaim&&) = delete;
    SqliteRetainedCallbackClaim& operator=(
        SqliteRetainedCallbackClaim&&) = delete;

    // client_data_name is copied before SQLite sees it.  owner_kind is used
    // only for value-free construction diagnostics (for example,
    // "busy-handler owner").
    void attach(sqlite3* database,
                const SyncSqliteDatabaseMutexGuard& mutex_guard,
                std::string_view client_data_name,
                const std::string& label,
                std::string_view owner_kind);

    // Prove that the exact live sentinel is still registered on database.
    // A mismatch is a retained-context lifetime violation, not a recoverable
    // data error.
    void require_live(
        sqlite3* database,
        const SyncSqliteDatabaseMutexGuard& mutex_guard) const noexcept;

    // Idempotent after a successful detach.  The caller must already have
    // revoked the retained callback and quiesced connection use.
    void detach(sqlite3* database,
                const SyncSqliteDatabaseMutexGuard& mutex_guard) noexcept;

    [[nodiscard]] bool attached() const noexcept;

private:
    struct ClaimState;

    static void destroy_claim_state(void* context) noexcept;
    void require_current_process_noexcept() const noexcept;

    SyncProcessIncarnation process_id_;
    std::string client_data_name_;
    ClaimState* claim_state_ = nullptr;
};

}  // namespace anonsync::persistence
