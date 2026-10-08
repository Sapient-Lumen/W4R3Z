#include "sqlite_busy_handler_owner.hpp"

#include "sqlite_retained_callback_slots.hpp"
#include "sync_sqlite_database_mutex_guard.hpp"

#include <sqlite3.h>

#include <algorithm>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync::persistence {
namespace {

static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
              "busy-handler diagnostics must remain lock-free after fork");
static_assert(std::atomic<std::uint32_t>::is_always_lock_free,
              "busy-handler callback activity must remain lock-free after fork");
static_assert(std::atomic<bool>::is_always_lock_free,
              "busy-handler callback flags must remain lock-free after fork");

void saturating_atomic_add(std::atomic<std::uint64_t>& value,
                           std::uint64_t amount) noexcept {
    std::uint64_t observed = value.load(std::memory_order_relaxed);
    for (;;) {
        const std::uint64_t replacement =
            amount > std::numeric_limits<std::uint64_t>::max() - observed
                ? std::numeric_limits<std::uint64_t>::max()
                : observed + amount;
        if (value.compare_exchange_weak(observed,
                                        replacement,
                                        std::memory_order_relaxed,
                                        std::memory_order_relaxed)) {
            return;
        }
    }
}

[[noreturn]] void fail_stop_on_busy_context_lifetime_violation_noexcept()
    noexcept {
    // The stable process-capability exit is also used when a retained callback
    // address cannot be revoked before its C++ lifetime ends. Continuing would
    // leave SQLite with authority to call freed storage.
    fail_stop_on_sync_process_capability_violation_noexcept();
}

std::runtime_error sqlite_busy_owner_error(sqlite3* database,
                                           int result_code,
                                           const std::string& label,
                                           std::string_view operation) {
    const char* detail = database == nullptr ? nullptr : sqlite3_errmsg(database);
    if (detail == nullptr || *detail == '\0') detail = sqlite3_errstr(result_code);
    return std::runtime_error(label + " " + std::string(operation) + ": " +
                              (detail == nullptr ? "SQLite error" : detail));
}

class CallbackActivityScope final {
public:
    explicit CallbackActivityScope(
        std::atomic<std::uint32_t>& active) noexcept
        : active_(active) {
        if (active_.fetch_add(1U, std::memory_order_acq_rel) != 0U) {
            fail_stop_on_busy_context_lifetime_violation_noexcept();
        }
    }

    ~CallbackActivityScope() {
        if (active_.fetch_sub(1U, std::memory_order_acq_rel) != 1U) {
            fail_stop_on_busy_context_lifetime_violation_noexcept();
        }
    }

    CallbackActivityScope(const CallbackActivityScope&) = delete;
    CallbackActivityScope& operator=(const CallbackActivityScope&) = delete;

private:
    std::atomic<std::uint32_t>& active_;
};

}  // namespace

SqliteBusyHandlerOwner::SqliteBusyHandlerOwner(
    SyncSqliteSerializedDbBorrow database_borrow,
    std::uint64_t maximum_wait_milliseconds,
    const std::string& label)
    : process_id_(current_sync_process_incarnation_noexcept()),
      database_borrow_(std::move(database_borrow)),
      maximum_wait_milliseconds_(maximum_wait_milliseconds) {
    sqlite3* const database = database_borrow_.get();
    if (database == nullptr) {
        throw std::invalid_argument(
            "SQLite busy handler owner requires an exact serialized database-generation borrow");
    }
    if (label.empty()) {
        throw std::invalid_argument(
            "SQLite busy handler owner requires a nonempty diagnostic label");
    }
    if (maximum_wait_milliseconds >
        kMaximumSqliteBusyHandlerWaitMilliseconds) {
        throw std::invalid_argument(
            label + " busy-handler wait exceeds the reviewed ceiling of " +
            std::to_string(kMaximumSqliteBusyHandlerWaitMilliseconds) +
            " milliseconds");
    }

    // One recursive connection-mutex region owns the complete singleton-slot
    // transition. Without this fence, two typed constructors could both
    // observe an empty client-data name before one setter destroyed the other
    // constructor's pending/live claim, turning ordinary contention into a
    // process-wide fail-stop.
    SyncSqliteDatabaseMutexGuard mutation_guard(
        database, label + " busy-handler slot attachment");
    callback_claim_.attach(database,
                           mutation_guard,
                           kSqliteBusyHandlerOwnerClientDataName,
                           label,
                           "busy-handler owner");

    const int handler_result =
        sqlite3_busy_handler(database,
                             &SqliteBusyHandlerOwner::busy_callback,
                             this);
    if (handler_result != SQLITE_OK) {
        callback_claim_.detach(database, mutation_guard);
        throw sqlite_busy_owner_error(database,
                                      handler_result,
                                      label,
                                      "could not install bounded callback");
    }
}

SqliteBusyHandlerOwner::~SqliteBusyHandlerOwner() { detach(); }

SqliteBusyHandlerSnapshot SqliteBusyHandlerOwner::snapshot() const noexcept {
    require_current_process_noexcept();

    SqliteBusyHandlerSnapshot result;
    // Every field is monotone. Acquire loads make the snapshot a conservative
    // lower bound during a running operation and exact after quiescence.
    result.contention_observed =
        contention_observed_.load(std::memory_order_acquire);
    result.invocations = invocations_.load(std::memory_order_acquire);
    result.authorized_sleep_milliseconds =
        authorized_sleep_milliseconds_.load(std::memory_order_acquire);
    result.sleep_milliseconds =
        sleep_milliseconds_.load(std::memory_order_acquire);
    result.timeout_exhausted =
        timeout_exhausted_.load(std::memory_order_acquire);
    return result;
}

bool SqliteBusyHandlerOwner::contention_observed() const noexcept {
    require_current_process_noexcept();
    return contention_observed_.load(std::memory_order_acquire);
}

void SqliteBusyHandlerOwner::detach() noexcept {
    require_current_process_noexcept();
    sqlite3* const database = database_borrow_.get();
    if (database == nullptr) {
        if (callback_claim_.attached()) {
            fail_stop_on_busy_context_lifetime_violation_noexcept();
        }
        return;
    }

    {
        SyncSqliteDatabaseMutexGuard mutation_guard(
            database, kSyncSqliteDatabaseMutexFailStop);
        callback_claim_.require_live(database, mutation_guard);

        // The recursive connection mutex serializes callback revocation with
        // every other reviewed setter. The busy-handler setter cannot return
        // until an operation currently invoking the old callback has left the
        // same connection mutex.
        if (sqlite3_busy_handler(database, nullptr, nullptr) != SQLITE_OK) {
            fail_stop_on_busy_context_lifetime_violation_noexcept();
        }
        if (callbacks_active_.load(std::memory_order_acquire) != 0U) {
            fail_stop_on_busy_context_lifetime_violation_noexcept();
        }

        callback_claim_.detach(database, mutation_guard);
    }
    // Keep the exact generation pinned until after the mutation guard has left
    // the SQLite-owned mutex it references.
    database_borrow_.reset();
}

int SqliteBusyHandlerOwner::busy_callback(void* context,
                                          int prior_invocations) noexcept {
    if (context == nullptr) return 0;
    return static_cast<SqliteBusyHandlerOwner*>(context)->on_busy(
        prior_invocations);
}

int SqliteBusyHandlerOwner::on_busy(int prior_invocations) noexcept {
    require_current_process_noexcept();
    CallbackActivityScope activity(callbacks_active_);

    saturating_atomic_add(invocations_, 1U);
    contention_observed_.store(true, std::memory_order_release);

    const std::uint64_t authorized_sleep =
        authorized_sleep_milliseconds_.load(std::memory_order_acquire);
    if (authorized_sleep >= maximum_wait_milliseconds_) {
        timeout_exhausted_.store(true, std::memory_order_release);
        return 0;
    }

    const std::uint64_t remaining =
        maximum_wait_milliseconds_ - authorized_sleep;
    const int normalized_prior = std::max(prior_invocations, 0);
    const int progressive = normalized_prior >= 9 ? 10 : normalized_prior + 1;
    const std::uint64_t progressive_sleep =
        static_cast<std::uint64_t>(progressive);
    const std::uint64_t requested_sleep =
        std::min(progressive_sleep, remaining);

    // Callback overlap is fail-stop, so this is the only writer. Consume the
    // exact authority before sleeping: a later locking event cannot reuse it,
    // and scheduler latency cannot silently enlarge the budget.
    authorized_sleep_milliseconds_.store(
        authorized_sleep + requested_sleep, std::memory_order_release);
    const int slept = sqlite3_sleep(static_cast<int>(requested_sleep));
    if (slept > 0) {
        saturating_atomic_add(sleep_milliseconds_,
                              static_cast<std::uint64_t>(slept));
    }
    return 1;
}

void SqliteBusyHandlerOwner::require_current_process_noexcept() const noexcept {
    if (!process_id_.valid() ||
        !sync_process_incarnation_is_current(process_id_)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
}

}  // namespace anonsync::persistence
