#include "sync_thread_incarnation.hpp"

#include "sync_process_incarnation_internal.hpp"

#include <atomic>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>

namespace anonsync {

namespace detail {

class SyncThreadIncarnationAccess final {
public:
    [[nodiscard]] static constexpr std::uint64_t raw(
        SyncThreadIncarnation incarnation) noexcept {
        return incarnation.value_;
    }

    [[nodiscard]] static constexpr SyncThreadIncarnation from_raw(
        std::uint64_t value) noexcept {
        return SyncThreadIncarnation(value);
    }
};

}  // namespace detail

namespace {

static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
              "thread-incarnation allocation must remain lock-free after fork");

// Namespace storage is constant-initialized. A function-local static could
// leave an initialization guard permanently owned by a vanished thread when a
// multithreaded process forks during first use.
constinit std::atomic<std::uint64_t> next_thread_incarnation_raw{1U};

// Keep thread-local storage in raw, trivially destructible representation. The
// public proof deliberately has a non-trivial destructor to block std::bit_cast
// construction. Storing that public type in thread_local state would therefore
// emit a per-thread guard and __cxa_thread_atexit registration even with
// constinit. A post-fork child must not enter copied runtime registration
// machinery before it can refresh inherited authority.
struct ThreadLocalIncarnationRaw final {
    std::uint64_t process_raw = 0U;
    std::uint64_t incarnation_raw = 0U;
};
static_assert(std::is_trivially_copyable_v<ThreadLocalIncarnationRaw>);
static_assert(std::is_trivially_destructible_v<ThreadLocalIncarnationRaw>);
constinit thread_local ThreadLocalIncarnationRaw live_thread_incarnation_raw;

SyncThreadIncarnation allocate_thread_incarnation_noexcept() noexcept {
    std::uint64_t current =
        next_thread_incarnation_raw.load(std::memory_order_relaxed);
    for (;;) {
        if (current == 0U ||
            current == std::numeric_limits<std::uint64_t>::max()) {
            fail_stop_on_sync_thread_capability_violation_noexcept();
        }
        if (next_thread_incarnation_raw.compare_exchange_weak(
                current,
                current + 1U,
                std::memory_order_relaxed,
                std::memory_order_relaxed)) {
            return detail::SyncThreadIncarnationAccess::from_raw(current);
        }
    }
}

}  // namespace

SyncThreadIncarnation current_sync_thread_incarnation_noexcept() noexcept {
    const SyncProcessIncarnation current_process =
        current_sync_process_incarnation_noexcept();
    const std::uint64_t current_process_raw =
        detail::SyncProcessIncarnationAccess::raw(current_process);
    if (live_thread_incarnation_raw.process_raw != current_process_raw ||
        live_thread_incarnation_raw.incarnation_raw == 0U) {
        // fork() copies thread_local bytes. The sole surviving child thread
        // receives a new process incarnation and must not retain the parent's
        // exact thread capability generation.
        const SyncThreadIncarnation replacement =
            allocate_thread_incarnation_noexcept();
        live_thread_incarnation_raw.process_raw = current_process_raw;
        live_thread_incarnation_raw.incarnation_raw =
            detail::SyncThreadIncarnationAccess::raw(replacement);
    }
    return detail::SyncThreadIncarnationAccess::from_raw(
        live_thread_incarnation_raw.incarnation_raw);
}

bool sync_thread_incarnation_is_current(
    SyncThreadIncarnation expected) noexcept {
    return expected.valid() &&
           expected == current_sync_thread_incarnation_noexcept();
}

void require_sync_thread_incarnation_or_throw(
    SyncThreadIncarnation expected,
    std::string_view label) {
    if (!expected.valid()) {
        throw std::logic_error(std::string(label) +
                               " thread-affinity proof is empty");
    }
    if (!sync_thread_incarnation_is_current(expected)) {
        throw std::logic_error(std::string(label) +
                               " must execute on its originating thread");
    }
}

[[noreturn]] void fail_stop_on_sync_thread_capability_violation_noexcept()
    noexcept {
    fail_stop_on_sync_process_capability_violation_noexcept();
}

}  // namespace anonsync
