#include "sync_sqlite_mutex_capability.hpp"

#include "sync_sqlite_support.hpp"

#include <atomic>
#include <limits>
#include <stdexcept>

#include <sqlite3.h>

namespace anonsync {

struct SyncSqliteRetainedMutexCapabilityState final {
    static constexpr std::uint64_t kMagic =
        UINT64_C(0x41534d5554455843);  // "ASMUTEXC"

    std::uint64_t magic = kMagic;
    SyncSqliteRetainedMutexCapabilityState* self = this;
    SyncSqliteProcessId process_id = current_sync_sqlite_process_id_noexcept();
    // Shared close-order evidence only. A nonzero count does not identify or
    // authorize any particular lease; each owner carries its own exact thread
    // incarnation and consumes its own pointer on release.
    std::uint64_t active_capabilities = 0;
};

namespace {

static_assert(SQLITE_VERSION_NUMBER >= 3044000,
              "SQLite connection client data requires SQLite 3.44.0+");

constexpr char kRetainedMutexCapabilityClientDataName[] =
    "anonsync.sqlite.retained-mutex-capabilities.v1";

SyncSqliteThreadIncarnation allocate_thread_incarnation_noexcept() noexcept {
    static std::atomic<SyncSqliteThreadIncarnation> next{1};
    SyncSqliteThreadIncarnation current = next.load(std::memory_order_relaxed);
    for (;;) {
        if (current == 0 ||
            current == std::numeric_limits<SyncSqliteThreadIncarnation>::max()) {
            fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
        }
        if (next.compare_exchange_weak(current,
                                       current + 1,
                                       std::memory_order_relaxed,
                                       std::memory_order_relaxed)) {
            return current;
        }
    }
}

void destroy_retained_mutex_capability_state(void* raw) noexcept {
    auto* state =
        static_cast<SyncSqliteRetainedMutexCapabilityState*>(raw);
    if (state == nullptr) return;
    if (!sync_sqlite_process_id_is_current(state->process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
    }
    if (state->magic != SyncSqliteRetainedMutexCapabilityState::kMagic ||
        state->self != state || state->active_capabilities != 0) {
        // SQLite invokes client-data destructors during close or replacement.
        // Returning from that operation with a live retained entry could leave
        // its later sqlite3_mutex_leave() targeting unallocated storage.
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    state->magic = 0;
    state->self = nullptr;
    delete state;
}

SyncSqliteRetainedMutexCapabilityState*
load_retained_mutex_capability_state_or_throw(
    sqlite3* db,
    bool allow_absent,
    const std::string& label) {
    void* raw =
        sqlite3_get_clientdata(db, kRetainedMutexCapabilityClientDataName);
    if (raw == nullptr) {
        if (allow_absent) return nullptr;
        throw std::runtime_error(
            label + " retained SQLite mutex capability state is absent");
    }
    auto* state =
        static_cast<SyncSqliteRetainedMutexCapabilityState*>(raw);
    if (!sync_sqlite_process_id_is_current(state->process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
    }
    if (state->magic != SyncSqliteRetainedMutexCapabilityState::kMagic ||
        state->self != state) {
        throw std::runtime_error(
            label + " retained SQLite mutex capability state is corrupt");
    }
    return state;
}

}  // namespace

SyncSqliteThreadIncarnation
current_sync_sqlite_thread_incarnation_noexcept() noexcept {
    struct ThreadLocalIncarnation final {
        SyncSqliteProcessId process_id = 0;
        SyncSqliteThreadIncarnation incarnation = 0;
    };
    thread_local ThreadLocalIncarnation local;
    const SyncSqliteProcessId current_process =
        current_sync_sqlite_process_id_noexcept();
    if (local.process_id != current_process || local.incarnation == 0) {
        // fork() copies thread_local bytes. The sole surviving child thread
        // must not retain the parent's exact thread generation.
        local.process_id = current_process;
        local.incarnation = allocate_thread_incarnation_noexcept();
    }
    return local.incarnation;
}

bool sync_sqlite_thread_incarnation_is_current(
    SyncSqliteThreadIncarnation expected) noexcept {
    return expected != 0 &&
           expected == current_sync_sqlite_thread_incarnation_noexcept();
}

void require_sync_sqlite_thread_incarnation_or_throw(
    SyncSqliteThreadIncarnation expected,
    const std::string& label) {
    if (expected == 0) {
        throw std::logic_error(label + " thread-affinity proof is empty");
    }
    if (!sync_sqlite_thread_incarnation_is_current(expected)) {
        throw std::logic_error(
            label + " must execute on the originating SQLite mutex thread");
    }
}

SyncSqliteRetainedMutexCapabilityState*
retain_sync_sqlite_mutex_capability_or_throw(
    sqlite3* db,
    const std::string& label) {
    if (db == nullptr) {
        throw std::invalid_argument(label + " database handle is null");
    }
    SyncSqliteRetainedMutexCapabilityState* state =
        load_retained_mutex_capability_state_or_throw(db, true, label);
    if (state == nullptr) {
        state = new SyncSqliteRetainedMutexCapabilityState();
        // With a non-null destructor SQLite assumes ownership even when this
        // call reports SQLITE_NOMEM; do not retain a second C++ owner.
        const int rc = sqlite3_set_clientdata(
            db,
            kRetainedMutexCapabilityClientDataName,
            state,
            destroy_retained_mutex_capability_state);
        if (rc != SQLITE_OK) {
            throw_sqlite_exception(
                db, rc, label + " install retained mutex capability sentinel");
        }
    }
    if (state->active_capabilities ==
        std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(
            label + " exhausted retained SQLite mutex capabilities");
    }
    ++state->active_capabilities;
    return state;
}

void release_sync_sqlite_mutex_capability_noexcept(
    SyncSqliteRetainedMutexCapabilityState*& state) noexcept {
    if (state == nullptr) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    if (!sync_sqlite_process_id_is_current(state->process_id)) {
        fail_stop_on_sync_sqlite_capability_violation_noexcept();
    }
    if (state->magic != SyncSqliteRetainedMutexCapabilityState::kMagic ||
        state->self != state || state->active_capabilities == 0) {
        fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept();
    }
    --state->active_capabilities;
    state = nullptr;
}

bool sync_sqlite_mutex_capability_is_live_noexcept(
    const SyncSqliteRetainedMutexCapabilityState* state) noexcept {
    return state != nullptr &&
           sync_sqlite_process_id_is_current(state->process_id) &&
           state->magic == SyncSqliteRetainedMutexCapabilityState::kMagic &&
           state->self == state && state->active_capabilities != 0;
}

[[noreturn]] void fail_stop_on_sync_sqlite_mutex_capability_violation_noexcept()
    noexcept {
    fail_stop_on_sync_sqlite_capability_violation_noexcept();
}

}  // namespace anonsync
