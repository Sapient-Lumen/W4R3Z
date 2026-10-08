#pragma once

#include "sqlite_retained_callback_claim.hpp"
#include "sync_process_incarnation.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <atomic>
#include <cstdint>
#include <string>

namespace anonsync::persistence {

// Keep SQLite lock waiting bounded independently of any caller-owned result
// document. Callers may tighten this ceiling but may not enlarge the callback's
// authority beyond the public peer-ingress contract.
inline constexpr std::uint64_t kMaximumSqliteBusyHandlerWaitMilliseconds =
    60'000ULL;

// One monotone observation of the callback-owned diagnostics. While a SQLite
// operation is still running, independently loaded fields are a safe lower
// bound rather than a transactional snapshot. Once connection use has
// quiesced, this value is exact for the owner lifetime.
struct SqliteBusyHandlerSnapshot final {
    std::uint64_t invocations = 0;
    // Exact cumulative sleep authority consumed by this owner. Scheduler
    // latency can make the observed sqlite3_sleep() duration larger.
    std::uint64_t authorized_sleep_milliseconds = 0;
    // Diagnostic duration reported by sqlite3_sleep(), never authority.
    std::uint64_t sleep_milliseconds = 0;
    bool contention_observed = false;
    bool timeout_exhausted = false;
};

// Stable lifetime owner for one sqlite3_busy_handler context.
//
// The callback is intentionally cross-thread capable: a FULLMUTEX connection
// may be handed between threads, and SQLite may invoke this context on whichever
// thread drives the current operation. Every callback-reachable field is
// therefore immutable or lock-free atomic. The object remains process-bound,
// because an inherited raw callback address is never valid authority in a fork
// descendant.
//
// Construction consumes one exact-generation serialized database borrow. The
// retained borrow prevents typed close/replacement until both the callback and
// the named client-data claim are revoked. The class is nonmovable so SQLite's
// raw context address cannot change.
// maximum_wait_milliseconds is one cumulative budget for the complete owner
// lifetime, not a fresh allowance for each SQLite locking event.
//
// The named client-data claim prevents two AnonSync owners from silently
// replacing one another. Construction holds the connection's recursive mutex
// across the complete "claim empty slot + install busy callback" transition,
// so simultaneous legitimate constructors resolve as one live owner and one
// ordinary rejection rather than destructive claim replacement. The claim
// also turns premature connection destruction or named replacement into a
// fail-stop lifetime violation. A raw sqlite3_close_v2()
// with outstanding SQLite dependents may defer actual destruction; the claim
// detects that violation when destruction occurs, while the reviewed typed
// close path rejects it immediately through the generation pin. Destruction
// must not race connection use; it first unregisters the busy callback,
// synchronously clears the claim, and only then releases the exact-generation
// borrow.
class SqliteBusyHandlerOwner final {
public:
    SqliteBusyHandlerOwner(
        SyncSqliteSerializedDbBorrow database_borrow,
        std::uint64_t maximum_wait_milliseconds,
        const std::string& label);
    ~SqliteBusyHandlerOwner();

    SqliteBusyHandlerOwner(const SqliteBusyHandlerOwner&) = delete;
    SqliteBusyHandlerOwner& operator=(const SqliteBusyHandlerOwner&) = delete;
    SqliteBusyHandlerOwner(SqliteBusyHandlerOwner&&) = delete;
    SqliteBusyHandlerOwner& operator=(SqliteBusyHandlerOwner&&) = delete;

    [[nodiscard]] SqliteBusyHandlerSnapshot snapshot() const noexcept;
    [[nodiscard]] bool contention_observed() const noexcept;

    // Sequential calls from any thread in the owning process are permitted.
    // The caller must first quiesce all connection use and keep the typed owner
    // alive through this operation. Successful detach revokes every retained C
    // callback address before releasing this owner's generation pin.
    void detach() noexcept;

private:
    static int busy_callback(void* context, int prior_invocations) noexcept;
    int on_busy(int prior_invocations) noexcept;
    void require_current_process_noexcept() const noexcept;

    SyncProcessIncarnation process_id_;
    SyncSqliteSerializedDbBorrow database_borrow_;
    SqliteRetainedCallbackClaim callback_claim_;
    std::uint64_t maximum_wait_milliseconds_ = 0;
    std::atomic<std::uint64_t> invocations_{0};
    std::atomic<std::uint64_t> authorized_sleep_milliseconds_{0};
    std::atomic<std::uint64_t> sleep_milliseconds_{0};
    std::atomic<std::uint32_t> callbacks_active_{0};
    std::atomic<bool> contention_observed_{false};
    std::atomic<bool> timeout_exhausted_{false};
};

}  // namespace anonsync::persistence
