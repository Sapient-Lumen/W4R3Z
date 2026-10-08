#include "sync_process_incarnation.hpp"

#include "sync_process_incarnation_internal.hpp"

#include <atomic>
#include <cstdlib>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>

#if defined(_WIN32)
#include <process.h>
#else
#include <pthread.h>
#include <unistd.h>
#endif

namespace anonsync {
namespace {

static_assert(std::atomic<std::uint64_t>::is_always_lock_free,
              "process-incarnation refresh must remain lock-free after fork");

// Keep the fork-handler storage as raw internal representation so the public
// proof can remain non-trivially-copyable and therefore cannot be manufactured
// with std::bit_cast. This always-lock-free atomic is copied by fork(). The
// child hook advances the child copy before fork() returns; ordinary lookup
// retains a PID-change fallback for process-creation paths that bypass the
// registered hook.
std::atomic<std::uint64_t> live_process_incarnation_raw{};

std::uint32_t current_kernel_pid_or_fail_stop() noexcept {
#if defined(_WIN32)
    const int raw = ::_getpid();
#else
    const pid_t raw = ::getpid();
#endif
    if (raw <= 0) fail_stop_on_sync_process_capability_violation_noexcept();
    using Raw = std::remove_cv_t<decltype(raw)>;
    using UnsignedRaw = std::make_unsigned_t<Raw>;
    const auto unsigned_raw = static_cast<UnsignedRaw>(raw);
    if (unsigned_raw > std::numeric_limits<std::uint32_t>::max()) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
    return static_cast<std::uint32_t>(unsigned_raw);
}

#if !defined(_WIN32)

void advance_process_incarnation_in_child_after_fork() noexcept {
    const std::uint64_t observed_raw =
        live_process_incarnation_raw.load(std::memory_order_relaxed);
    if (observed_raw == 0U) return;

    const SyncProcessIncarnation observed =
        detail::SyncProcessIncarnationAccess::from_raw(observed_raw);
    const SyncProcessIncarnation advanced =
        detail::advance_sync_process_incarnation_after_fork(
            observed, current_kernel_pid_or_fail_stop());
    const SyncProcessIncarnation stored =
        !advanced.valid() ? detail::kSyncPoisonedProcessIncarnation : advanced;
    live_process_incarnation_raw.store(
        detail::SyncProcessIncarnationAccess::raw(stored),
        !advanced.valid() ? std::memory_order_relaxed : std::memory_order_release);
}

// Before dynamic initialization this object is zero-initialized to false, so an
// unusually early cross-translation-unit call fails closed rather than minting
// authority before the fork hook exists.
const bool fork_child_handler_registered =
    ::pthread_atfork(nullptr, nullptr,
                     &advance_process_incarnation_in_child_after_fork) == 0;

#endif

}  // namespace

SyncProcessIncarnation current_sync_process_incarnation_noexcept() noexcept {
#if !defined(_WIN32)
    if (!fork_child_handler_registered) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
#endif
    const std::uint32_t kernel_pid = current_kernel_pid_or_fail_stop();
    std::uint64_t observed_raw =
        live_process_incarnation_raw.load(std::memory_order_acquire);
    for (;;) {
        const SyncProcessIncarnation observed =
            detail::SyncProcessIncarnationAccess::from_raw(observed_raw);
        const SyncProcessIncarnation refreshed =
            detail::refresh_sync_process_incarnation(observed, kernel_pid);
        if (!refreshed.valid()) {
            fail_stop_on_sync_process_capability_violation_noexcept();
        }
        const std::uint64_t refreshed_raw =
            detail::SyncProcessIncarnationAccess::raw(refreshed);
        if (refreshed_raw == observed_raw) return observed;
        if (live_process_incarnation_raw.compare_exchange_weak(
                observed_raw,
                refreshed_raw,
                std::memory_order_acq_rel,
                std::memory_order_acquire)) {
            return refreshed;
        }
    }
}

bool sync_process_incarnation_is_current(SyncProcessIncarnation expected) noexcept {
    return expected.valid() &&
           expected == current_sync_process_incarnation_noexcept();
}

void require_sync_process_incarnation_or_fail_stop(
    SyncProcessIncarnation expected,
    std::string_view label) {
    if (!expected.valid()) {
        throw std::logic_error(std::string(label) +
                               " process-incarnation proof is empty");
    }
    if (!sync_process_incarnation_is_current(expected)) {
        fail_stop_on_sync_process_capability_violation_noexcept();
    }
}

[[noreturn]] void fail_stop_on_sync_process_capability_violation_noexcept()
    noexcept {
    std::_Exit(kSyncProcessCapabilityViolationExitCode);
}

}  // namespace anonsync
