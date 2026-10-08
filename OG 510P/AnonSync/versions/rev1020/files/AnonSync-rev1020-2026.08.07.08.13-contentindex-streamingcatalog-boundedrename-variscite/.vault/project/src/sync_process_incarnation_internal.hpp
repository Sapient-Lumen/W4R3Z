#pragma once

#include "sync_process_incarnation.hpp"

#include <cstdint>
#include <limits>

namespace anonsync::detail {

// The representation bridge is defined only on the internal surface. Public
// consumers can carry and compare a proof but cannot construct one from an
// arbitrary integer through the supported API.
class SyncProcessIncarnationAccess final {
public:
    [[nodiscard]] static constexpr std::uint64_t raw(
        SyncProcessIncarnation incarnation) noexcept {
        return incarnation.value_;
    }

    [[nodiscard]] static constexpr SyncProcessIncarnation from_raw(
        std::uint64_t value) noexcept {
        return SyncProcessIncarnation(value);
    }
};

// The low half records the currently observed kernel PID. The high half is a
// fork-lineage generation. A registered child-after-fork hook advances the
// generation before child code can run. The ordinary refresh path also detects
// an unexpected PID change as a fail-closed fallback.
inline constexpr unsigned kSyncProcessKernelPidBits = 32U;
inline constexpr std::uint64_t kSyncProcessKernelPidMask =
    (std::uint64_t{1} << kSyncProcessKernelPidBits) - 1U;
inline constexpr std::uint64_t kSyncProcessMaximumLineageGeneration =
    std::numeric_limits<std::uint64_t>::max() >> kSyncProcessKernelPidBits;
// Generation zero is never valid. A nonzero generation-zero marker preserves
// exhaustion as poisoned state instead of making it look uninitialized.
inline constexpr SyncProcessIncarnation kSyncPoisonedProcessIncarnation =
    SyncProcessIncarnationAccess::from_raw(1U);

[[nodiscard]] constexpr std::uint32_t
sync_kernel_pid_from_process_incarnation(
    SyncProcessIncarnation incarnation) noexcept {
    return static_cast<std::uint32_t>(
        SyncProcessIncarnationAccess::raw(incarnation) &
        kSyncProcessKernelPidMask);
}

[[nodiscard]] constexpr std::uint32_t
sync_lineage_generation_from_process_incarnation(
    SyncProcessIncarnation incarnation) noexcept {
    return static_cast<std::uint32_t>(
        SyncProcessIncarnationAccess::raw(incarnation) >>
        kSyncProcessKernelPidBits);
}

[[nodiscard]] constexpr std::uint32_t
next_sync_fork_lineage_generation(
    std::uint64_t current_generation) noexcept {
    if (current_generation == 0U ||
        current_generation >= kSyncProcessMaximumLineageGeneration) {
        return 0U;
    }
    return static_cast<std::uint32_t>(current_generation + 1U);
}

[[nodiscard]] constexpr SyncProcessIncarnation
compose_sync_process_incarnation(
    std::uint64_t generation,
    std::uint32_t kernel_pid) noexcept {
    if (kernel_pid == 0U || generation == 0U ||
        generation > kSyncProcessMaximumLineageGeneration) {
        return {};
    }
    return SyncProcessIncarnationAccess::from_raw(
        (generation << kSyncProcessKernelPidBits) |
        static_cast<std::uint64_t>(kernel_pid));
}

[[nodiscard]] constexpr SyncProcessIncarnation
refresh_sync_process_incarnation(
    SyncProcessIncarnation observed,
    std::uint32_t current_kernel_pid) noexcept {
    if (current_kernel_pid == 0U) return {};

    const std::uint64_t observed_raw =
        SyncProcessIncarnationAccess::raw(observed);
    const std::uint64_t observed_generation =
        observed_raw >> kSyncProcessKernelPidBits;
    const std::uint32_t observed_pid =
        sync_kernel_pid_from_process_incarnation(observed);
    if (observed.valid() && observed_generation == 0U) return {};
    if (observed.valid() && observed_pid == current_kernel_pid) return observed;

    const std::uint64_t next_generation =
        observed.valid()
            ? next_sync_fork_lineage_generation(observed_generation)
            : 1U;
    return compose_sync_process_incarnation(
        next_generation, current_kernel_pid);
}

[[nodiscard]] constexpr SyncProcessIncarnation
advance_sync_process_incarnation_after_fork(
    SyncProcessIncarnation observed,
    std::uint32_t child_kernel_pid) noexcept {
    // A child handler registered earlier may already have asked for the
    // current token. The PID-mismatch fallback then records this fork edge
    // before our handler runs. Reusing the same refresh rule makes the child
    // hook idempotent instead of invalidating authority minted by that earlier
    // handler with a second generation increment.
    return refresh_sync_process_incarnation(observed, child_kernel_pid);
}

}  // namespace anonsync::detail
