#pragma once

#include "sync_process_incarnation_internal.hpp"

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <thread>
#include <type_traits>
#include <utility>

#include <sqlite3.h>

namespace anonsync {

// Exact run-time threading evidence captured when one database-owner
// generation adopts a SQLite handle. `Unserialized` includes SQLite's
// multi-thread mode (and any build/start-time configuration that leaves the
// per-connection mutex absent). The value is process-local and is never
// serialized as durable domain evidence.
enum class SyncSqliteConnectionMutexMode : std::uint8_t {
    Unknown = 0,
    Unserialized = 1,
    Serialized = 2
};

}  // namespace anonsync

namespace anonsync::detail {

// The lifecycle guard is consulted after fork(), where a hidden library lock
// inside a non-lock-free std::atomic could itself be inherited as locked.
// Refuse such targets at build time rather than claiming a fail-stop boundary
// that can deadlock.
static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
              "SQLite process-bound owner guards require lock-free incarnation atomics");

struct SyncSqliteDbHandlePolicy final {
    using Handle = sqlite3;
    struct Evidence final {
        SyncSqliteConnectionMutexMode mutex_mode =
            SyncSqliteConnectionMutexMode::Unknown;
        sqlite3_mutex* mutex_identity = nullptr;

        friend bool operator==(const Evidence&, const Evidence&) = default;
    };

    [[nodiscard]] static Evidence capture_evidence(Handle* handle) noexcept;
    [[nodiscard]] static bool evidence_is_empty(
        const Evidence& evidence) noexcept;
    [[nodiscard]] static bool evidence_is_valid(
        Handle* handle, const Evidence& evidence) noexcept;
    static void dispose(Handle* handle) noexcept;
    static constexpr const char* name() noexcept { return "SQLite connection"; }
};

struct SyncSqliteStmtHandlePolicy final {
    using Handle = sqlite3_stmt;
    struct Evidence final {
        friend bool operator==(const Evidence&, const Evidence&) = default;
    };

    [[nodiscard]] static Evidence capture_evidence(Handle*) noexcept {
        return {};
    }
    [[nodiscard]] static bool evidence_is_empty(const Evidence&) noexcept {
        return true;
    }
    [[nodiscard]] static bool evidence_is_valid(
        Handle* handle, const Evidence&) noexcept {
        return handle != nullptr;
    }
    static void dispose(Handle* handle) noexcept;
    static constexpr const char* name() noexcept { return "SQLite statement"; }
};

template <typename Policy>
struct ProcessBoundHandleState final {
    using Handle = typename Policy::Handle;
    using Evidence = typename Policy::Evidence;

    explicit ProcessBoundHandleState(
        SyncProcessIncarnation state_process_id_value) noexcept
        : state_process_id(state_process_id_value) {}

    // A process-aware lifecycle lock avoids inheriting an opaque locked
    // std::mutex across fork(). A child that observes a parent-held operation
    // fails stopped instead of hanging or touching copied SQLite state.
    // state_process_id is immutable provenance for the C++ ownership storage
    // itself. It remains bound after close or a null SQLite output so a fork
    // child cannot destroy, move, or reuse an inherited shared_ptr control
    // block merely because the raw handle happens to be empty.
    const SyncProcessIncarnation state_process_id;
    std::atomic<std::uint64_t> lifecycle_lock_owner_raw{};
    Handle* handle = nullptr;
    Evidence evidence{};
    SyncProcessIncarnation process_id;
    std::uint64_t generation = 0;
    std::size_t active_borrows = 0;
    // Protected by lifecycle_lock_owner_raw. Once disposal starts, no callback or
    // concurrent operation may inspect, refill, move, or reset this owner until
    // the exact close/finalize transition has returned.
    bool disposal_pending = false;
    bool output_pending = false;
    SyncProcessIncarnation output_process_id;
};

template <typename Policy>
class ProcessBoundHandleStateGuard final {
public:
    using State = ProcessBoundHandleState<Policy>;

    explicit ProcessBoundHandleStateGuard(State& state) noexcept
        : state_(std::addressof(state)),
          process_id_(current_sync_process_incarnation_noexcept()) {
        if (state_->state_process_id != process_id_) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        const std::uint64_t process_id_raw =
            SyncProcessIncarnationAccess::raw(process_id_);
        for (;;) {
            std::uint64_t expected_raw = 0U;
            // Strong CAS is deliberate. A weak CAS may fail spuriously while
            // leaving `expected_raw == 0`; interpreting that as a foreign-process
            // owner would randomly fail-stop an otherwise healthy process.
            if (state_->lifecycle_lock_owner_raw.compare_exchange_strong(
                    expected_raw,
                    process_id_raw,
                    std::memory_order_acquire,
                    std::memory_order_relaxed)) {
                return;
            }
            if (expected_raw != process_id_raw) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            std::this_thread::yield();
        }
    }

    ~ProcessBoundHandleStateGuard() noexcept {
        std::uint64_t expected_raw =
            SyncProcessIncarnationAccess::raw(process_id_);
        if (!state_->lifecycle_lock_owner_raw.compare_exchange_strong(
                expected_raw,
                0U,
                std::memory_order_release,
                std::memory_order_relaxed)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
    }

    ProcessBoundHandleStateGuard(const ProcessBoundHandleStateGuard&) = delete;
    ProcessBoundHandleStateGuard& operator=(
        const ProcessBoundHandleStateGuard&) = delete;

private:
    State* state_ = nullptr;
    SyncProcessIncarnation process_id_;
};

template <typename Policy>
class ProcessBoundHandleSlot;

template <typename Policy>
class ProcessBoundHandleBorrow final {
public:
    using Handle = typename Policy::Handle;
    using State = ProcessBoundHandleState<Policy>;
    using Evidence = typename Policy::Evidence;

    ProcessBoundHandleBorrow() noexcept = default;
    ~ProcessBoundHandleBorrow() noexcept { release_noexcept(); }

    ProcessBoundHandleBorrow(const ProcessBoundHandleBorrow&) = delete;
    ProcessBoundHandleBorrow& operator=(const ProcessBoundHandleBorrow&) = delete;

    ProcessBoundHandleBorrow(ProcessBoundHandleBorrow&& other) noexcept {
        // Validate the source process before moving its shared-state pointer.
        // A fork child must fail stopped without even mutating the inherited
        // reference-count object.
        other.require_transferable_noexcept();
        transfer_from_noexcept(other);
    }

    ProcessBoundHandleBorrow& operator=(
        ProcessBoundHandleBorrow&& other) noexcept {
        if (this == std::addressof(other)) {
            require_transferable_noexcept();
            return *this;
        }
        // Check the source first. In a fork child this prevents both a shared
        // pointer transfer and destruction of an unrelated destination borrow.
        other.require_transferable_noexcept();
        release_noexcept();
        transfer_from_noexcept(other);
        return *this;
    }

    [[nodiscard]] Handle* get() const noexcept {
        if (state_ == nullptr) {
            if (handle_ != nullptr || process_id_.valid() || generation_ != 0 ||
                !Policy::evidence_is_empty(evidence_)) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            return nullptr;
        }
        if (handle_ == nullptr || !process_id_.valid() || generation_ == 0) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        // Reject inherited provenance before consulting copied generation
        // state. The process-aware guard then compares the exact frozen
        // handle/generation/evidence tuple. Evidence validation is deliberately
        // SQLite-free: mutex mode is immutable for one open connection.
        require_current_noexcept();
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        if (state_->process_id != process_id_ ||
            state_->generation != generation_ || state_->handle != handle_ ||
            state_->evidence != evidence_ ||
            state_->active_borrows == 0) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        if (!Policy::evidence_is_valid(handle_, evidence_)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return handle_;
    }

    operator Handle*() const noexcept { return get(); }

    [[nodiscard]] explicit operator bool() const noexcept {
        return get() != nullptr;
    }

    [[nodiscard]] std::uint64_t generation() const noexcept {
        if (state_ == nullptr) {
            (void)get();
            return 0;
        }
        (void)get();
        return generation_;
    }

    // A database borrow carries the exact mutex classification and mutex
    // identity captured when its owner generation adopted the handle. This is
    // stronger than trusting an open-call flag at a distant call site: it
    // records the connection SQLite actually materialized.
    [[nodiscard]] SyncSqliteConnectionMutexMode connection_mutex_mode()
        const noexcept {
        static_assert(std::is_same_v<Policy, SyncSqliteDbHandlePolicy>,
                      "connection mutex mode exists only on database borrows");
        if (state_ == nullptr) {
            (void)get();
            return SyncSqliteConnectionMutexMode::Unknown;
        }
        (void)get();
        return evidence_.mutex_mode;
    }

    [[nodiscard]] bool serialized_connection() const noexcept {
        static_assert(std::is_same_v<Policy, SyncSqliteDbHandlePolicy>,
                      "serialized connection evidence exists only on database borrows");
        return connection_mutex_mode() ==
               SyncSqliteConnectionMutexMode::Serialized;
    }

    void reset() noexcept { release_noexcept(); }

private:
    friend class ProcessBoundHandleSlot<Policy>;

    ProcessBoundHandleBorrow(std::shared_ptr<State> state,
                             Handle* handle,
                             Evidence evidence,
                             SyncProcessIncarnation process_id,
                             std::uint64_t generation) noexcept
        : state_(std::move(state)),
          handle_(handle),
          evidence_(evidence),
          process_id_(process_id),
          generation_(generation) {}

    void require_current_noexcept() const noexcept {
        if (!sync_process_incarnation_is_current(process_id_)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
    }

    void require_transferable_noexcept() const noexcept {
        if (state_ == nullptr) {
            if (handle_ != nullptr || process_id_.valid() || generation_ != 0 ||
                !Policy::evidence_is_empty(evidence_)) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            return;
        }
        if (handle_ == nullptr || !process_id_.valid() || generation_ == 0) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        require_current_noexcept();
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        if (state_->process_id != process_id_ ||
            state_->generation != generation_ || state_->handle != handle_ ||
            state_->evidence != evidence_ ||
            state_->active_borrows == 0) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        if (!Policy::evidence_is_valid(handle_, evidence_)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
    }

    void transfer_from_noexcept(ProcessBoundHandleBorrow& other) noexcept {
        state_ = std::move(other.state_);
        handle_ = std::exchange(other.handle_, nullptr);
        evidence_ = std::exchange(other.evidence_, Evidence{});
        process_id_ = std::exchange(other.process_id_, SyncProcessIncarnation{});
        generation_ = std::exchange(other.generation_, 0);
    }

    void release_noexcept() noexcept {
        if (state_ == nullptr) {
            if (handle_ != nullptr || process_id_.valid() || generation_ != 0 ||
                !Policy::evidence_is_empty(evidence_)) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            return;
        }
        require_current_noexcept();
        {
            ProcessBoundHandleStateGuard<Policy> guard(*state_);
            if (state_->process_id != process_id_ ||
                state_->generation != generation_ ||
                state_->handle != handle_ || state_->evidence != evidence_ ||
                state_->active_borrows == 0) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            --state_->active_borrows;
        }
        state_.reset();
        handle_ = nullptr;
        evidence_ = Evidence{};
        process_id_ = {};
        generation_ = 0;
    }

    std::shared_ptr<State> state_;
    Handle* handle_ = nullptr;
    Evidence evidence_{};
    SyncProcessIncarnation process_id_;
    std::uint64_t generation_ = 0;
};

template <typename Policy>
class ProcessBoundHandleOutGuard final {
public:
    using Handle = typename Policy::Handle;

    explicit ProcessBoundHandleOutGuard(ProcessBoundHandleSlot<Policy>& slot)
        : slot_(std::addressof(slot)),
          process_id_(current_sync_process_incarnation_noexcept()) {
        slot_->begin_output_or_throw();
    }

    ~ProcessBoundHandleOutGuard() noexcept {
        if (slot_ == nullptr) return;
        if (!sync_process_incarnation_is_current(process_id_)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        slot_->adopt_output_noexcept(candidate_, process_id_);
        candidate_ = nullptr;
        slot_ = nullptr;
    }

    ProcessBoundHandleOutGuard(const ProcessBoundHandleOutGuard&) = delete;
    ProcessBoundHandleOutGuard& operator=(
        const ProcessBoundHandleOutGuard&) = delete;
    ProcessBoundHandleOutGuard(ProcessBoundHandleOutGuard&&) = delete;
    ProcessBoundHandleOutGuard& operator=(ProcessBoundHandleOutGuard&&) = delete;

    operator Handle**() noexcept { return get(); }

    [[nodiscard]] Handle** get() noexcept {
        if (!sync_process_incarnation_is_current(process_id_)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        return std::addressof(candidate_);
    }

private:
    ProcessBoundHandleSlot<Policy>* slot_ = nullptr;
    Handle* candidate_ = nullptr;
    SyncProcessIncarnation process_id_;
};

template <typename Policy>
class ProcessBoundHandleSlot final {
public:
    using Handle = typename Policy::Handle;
    using State = ProcessBoundHandleState<Policy>;
    using Evidence = typename Policy::Evidence;
    using Borrow = ProcessBoundHandleBorrow<Policy>;
    using OutGuard = ProcessBoundHandleOutGuard<Policy>;

    // Allocate shared generation state only when SQLite actually writes an
    // output handle. Most default-constructed owners stay empty, so eager heap
    // allocation here was pure lifecycle overhead.
    ProcessBoundHandleSlot() = default;
    ~ProcessBoundHandleSlot() noexcept { dispose_owned_noexcept(); }

    ProcessBoundHandleSlot(const ProcessBoundHandleSlot&) = delete;
    ProcessBoundHandleSlot& operator=(const ProcessBoundHandleSlot&) = delete;

    ProcessBoundHandleSlot(ProcessBoundHandleSlot&& other) noexcept {
        transfer_from_noexcept(other);
    }

    ProcessBoundHandleSlot& operator=(ProcessBoundHandleSlot&& other) noexcept {
        if (this == std::addressof(other)) {
            require_current_if_owned_noexcept();
            return *this;
        }

        // Movement is one authority transition. Validate both participants,
        // then escrow the source before destroying the destination. Otherwise
        // an inherited or output-pending source can cause an unrelated valid
        // destination to close before the invalid transfer is rejected. The
        // escrow also prevents a SQLite close/finalize callback from mutating
        // the not-yet-transferred source object.
        other.require_current_if_owned_noexcept();
        require_current_if_owned_noexcept();
        std::shared_ptr<State> incoming_state = std::move(other.state_);
        dispose_owned_noexcept();
        state_ = std::move(incoming_state);
        return *this;
    }

    [[nodiscard]] Handle* get() const noexcept {
        if (state_ == nullptr) return nullptr;
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        require_consistent_state_noexcept(*state_);
        return state_->handle;
    }

    operator Handle*() const noexcept { return get(); }

    [[nodiscard]] bool empty() const noexcept { return get() == nullptr; }

    [[nodiscard]] explicit operator bool() const noexcept {
        return get() != nullptr;
    }

    [[nodiscard]] OutGuard out() {
        ensure_state();
        return OutGuard(*this);
    }

    [[nodiscard]] Borrow borrow() const {
        if (state_ == nullptr) {
            throw std::logic_error(std::string(Policy::name()) +
                                   " owner slot is empty");
        }
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        require_consistent_state_noexcept(*state_);
        if (state_->handle == nullptr) {
            throw std::logic_error(std::string(Policy::name()) +
                                   " owner slot is empty");
        }
        if (state_->active_borrows ==
            std::numeric_limits<std::size_t>::max()) {
            throw std::overflow_error(std::string(Policy::name()) +
                                      " borrow count overflow");
        }
        ++state_->active_borrows;
        return Borrow(state_, state_->handle, state_->evidence,
                      state_->process_id,
                      state_->generation);
    }

    // Explicit destruction retains the same process and generation fences as
    // the destructor. A live borrow is a fatal lifetime-order violation: the
    // slot never degrades to SQLite's deferred zombie-close semantics.
    void reset() noexcept { dispose_owned_noexcept(); }

    [[nodiscard]] std::uint64_t generation() const noexcept {
        if (state_ == nullptr) return 0;
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        require_consistent_state_noexcept(*state_);
        return state_->generation;
    }

    [[nodiscard]] std::size_t active_borrows() const noexcept {
        if (state_ == nullptr) return 0;
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        require_consistent_state_noexcept(*state_);
        return state_->active_borrows;
    }

private:
    friend class ProcessBoundHandleOutGuard<Policy>;

    static void require_transition_idle_noexcept(const State& state) noexcept {
        if (state.disposal_pending) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
    }

    static void require_consistent_state_noexcept(const State& state) noexcept {
        require_transition_idle_noexcept(state);
        if (state.output_pending) {
            // No operation except the exact OutGuard destructor may inspect,
            // move, reset, or reuse a reserved output slot.
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        const bool empty_state = state.handle == nullptr && !state.process_id.valid();
        const bool owned_state = state.handle != nullptr && state.process_id.valid() &&
                                 state.generation != 0;
        if (!empty_state && !owned_state) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        if (state.output_process_id.valid()) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        if (empty_state) {
            if (state.active_borrows != 0 ||
                !Policy::evidence_is_empty(state.evidence)) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
        }
        if (owned_state) {
            if (!Policy::evidence_is_valid(state.handle, state.evidence) ||
                !sync_process_incarnation_is_current(state.process_id)) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
        }
    }

    void ensure_state() {
        if (state_ == nullptr) {
            state_ = std::make_shared<State>(
                current_sync_process_incarnation_noexcept());
        }
    }

    void begin_output_or_throw() {
        ensure_state();
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        if (state_->output_pending) {
            if (state_->disposal_pending || state_->handle != nullptr ||
                state_->process_id.valid() ||
                state_->active_borrows != 0 ||
                !Policy::evidence_is_empty(state_->evidence) ||
                !sync_process_incarnation_is_current(
                    state_->output_process_id)) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            throw std::logic_error(std::string(Policy::name()) +
                                   " output acquisition is already pending");
        }
        require_consistent_state_noexcept(*state_);
        if (state_->handle != nullptr || state_->process_id.valid() ||
            state_->active_borrows != 0 ||
            !Policy::evidence_is_empty(state_->evidence)) {
            throw std::logic_error(std::string(Policy::name()) +
                                   " output acquisition requires an empty, unborrowed owner slot");
        }
        if (state_->generation == std::numeric_limits<std::uint64_t>::max()) {
            throw std::overflow_error(std::string(Policy::name()) +
                                      " generation is exhausted");
        }
        state_->output_pending = true;
        state_->output_process_id =
            current_sync_process_incarnation_noexcept();
    }

    void adopt_output_noexcept(Handle* handle,
                               SyncProcessIncarnation process_id) noexcept {
        if (state_ == nullptr) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        if (state_->disposal_pending || !state_->output_pending ||
            state_->handle != nullptr || state_->process_id.valid() ||
            state_->active_borrows != 0 ||
            !Policy::evidence_is_empty(state_->evidence) ||
            state_->output_process_id != process_id || !process_id.valid() ||
            !sync_process_incarnation_is_current(process_id)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        state_->output_pending = false;
        state_->output_process_id = {};
        if (handle == nullptr) return;
        if (state_->generation == std::numeric_limits<std::uint64_t>::max()) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        ++state_->generation;
        if (state_->generation == 0) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        const Evidence evidence = Policy::capture_evidence(handle);
        if (!Policy::evidence_is_valid(handle, evidence)) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        state_->handle = handle;
        state_->evidence = evidence;
        state_->process_id = process_id;
    }

    void require_current_if_owned_noexcept() const noexcept {
        if (state_ == nullptr) return;
        ProcessBoundHandleStateGuard<Policy> guard(*state_);
        require_consistent_state_noexcept(*state_);
    }

    void dispose_owned_noexcept() noexcept {
        if (state_ == nullptr) return;

        // Keep the exact state alive independently of the public owner object.
        // SQLite close/finalize may invoke application callbacks; those callbacks
        // must observe a synchronized transition fence and fail stopped before
        // they can recursively reset or replace this owner.
        const std::shared_ptr<State> disposing_state = state_;
        Handle* owned = nullptr;
        {
            ProcessBoundHandleStateGuard<Policy> guard(*disposing_state);
            require_transition_idle_noexcept(*disposing_state);
            require_consistent_state_noexcept(*disposing_state);
            if (disposing_state->active_borrows != 0) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            disposing_state->disposal_pending = true;
            owned = disposing_state->handle;
            disposing_state->handle = nullptr;
            disposing_state->evidence = Evidence{};
            disposing_state->process_id = {};
        }

        if (owned != nullptr) Policy::dispose(owned);

        {
            ProcessBoundHandleStateGuard<Policy> guard(*disposing_state);
            if (!disposing_state->disposal_pending ||
                disposing_state->handle != nullptr ||
                disposing_state->process_id.valid() ||
                disposing_state->active_borrows != 0 ||
                disposing_state->output_pending ||
                disposing_state->output_process_id.valid() ||
                !Policy::evidence_is_empty(disposing_state->evidence)) {
                fail_stop_on_sync_process_capability_violation_noexcept();
            }
            disposing_state->disposal_pending = false;
        }
    }

    void transfer_from_noexcept(ProcessBoundHandleSlot& other) noexcept {
        other.require_current_if_owned_noexcept();
        state_ = std::move(other.state_);
    }

    std::shared_ptr<State> state_;
};

}  // namespace anonsync::detail

namespace anonsync {
using SyncSqliteDbHandleSlot =
    detail::ProcessBoundHandleSlot<detail::SyncSqliteDbHandlePolicy>;
using SyncSqliteStmtHandleSlot =
    detail::ProcessBoundHandleSlot<detail::SyncSqliteStmtHandlePolicy>;
using SyncSqliteDbHandleBorrow =
    detail::ProcessBoundHandleBorrow<detail::SyncSqliteDbHandlePolicy>;
using SyncSqliteStmtHandleBorrow =
    detail::ProcessBoundHandleBorrow<detail::SyncSqliteStmtHandlePolicy>;
using SyncSqliteDbBorrow = SyncSqliteDbHandleBorrow;
using SyncSqliteStmtBorrow = SyncSqliteStmtHandleBorrow;

// Exact-generation database use authority whose SQLite connection mutex mode
// was captured when the owner adopted the handle and proved serialized before
// this capability was minted.  There is intentionally no raw-pointer
// constructor: an address alone cannot recover owner generation or open mode.
class SyncSqliteSerializedDbBorrow final {
public:
    SyncSqliteSerializedDbBorrow() noexcept = default;
    ~SyncSqliteSerializedDbBorrow() = default;
    SyncSqliteSerializedDbBorrow(const SyncSqliteSerializedDbBorrow&) = delete;
    SyncSqliteSerializedDbBorrow& operator=(
        const SyncSqliteSerializedDbBorrow&) = delete;
    SyncSqliteSerializedDbBorrow(
        SyncSqliteSerializedDbBorrow&&) noexcept = default;
    SyncSqliteSerializedDbBorrow& operator=(
        SyncSqliteSerializedDbBorrow&&) noexcept = default;

    [[nodiscard]] sqlite3* get() const noexcept { return borrow_.get(); }
    // Deliberately no implicit sqlite3* conversion. Downgrading this proof to
    // an untracked address must be visible as an explicit .get() at the call
    // site, which keeps migration debt searchable.
    [[nodiscard]] explicit operator bool() const noexcept {
        return get() != nullptr;
    }
    [[nodiscard]] std::uint64_t generation() const noexcept {
        return borrow_.generation();
    }
    [[nodiscard]] SyncSqliteConnectionMutexMode connection_mutex_mode() const
        noexcept {
        return borrow_.connection_mutex_mode();
    }
    void reset() noexcept { borrow_.reset(); }

private:
    explicit SyncSqliteSerializedDbBorrow(
        SyncSqliteDbHandleBorrow borrow) noexcept
        : borrow_(std::move(borrow)) {}

    SyncSqliteDbHandleBorrow borrow_;

    friend SyncSqliteSerializedDbBorrow
    borrow_sync_sqlite_serialized_db_or_throw(
        const SyncSqliteDbHandleSlot&, const std::string&);
};

[[nodiscard]] inline SyncSqliteSerializedDbBorrow
borrow_sync_sqlite_serialized_db_or_throw(
    const SyncSqliteDbHandleSlot& owner,
    const std::string& label) {
    SyncSqliteDbHandleBorrow borrow = owner.borrow();
    if (borrow.connection_mutex_mode() !=
        SyncSqliteConnectionMutexMode::Serialized) {
        throw std::runtime_error(
            label + " requires a serialized/FULLMUTEX SQLite connection");
    }
    return SyncSqliteSerializedDbBorrow(std::move(borrow));
}
}  // namespace anonsync
