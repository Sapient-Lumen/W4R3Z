#pragma once

#include <cstdint>
#include <string_view>
#include <type_traits>

namespace anonsync {

namespace detail {
class SyncProcessIncarnationAccess;
}

// One typed live-process incarnation proof. On fork-capable builds, the
// private representation combines a kernel PID with a child-side fork-lineage
// generation so PID recycling cannot resurrect authority in a later ordinary
// fork() descendant. Process creation that bypasses pthread_atfork(), including
// POSIX _Fork(), is outside that lineage proof; such a child must not re-enter
// AnonSync before exec. It is process-local evidence, not an interchange format.
// Deliberately exposing no integer constructor and making the value
// non-trivially-copyable prevents a raw PID, row value, or wire value from
// being mistaken for proof through ordinary conversion or std::bit_cast.
// This is domain separation against accidental evidence confusion, not a
// security boundary against hostile code already executing in this process.
class SyncProcessIncarnation final {
public:
    constexpr SyncProcessIncarnation() noexcept = default;
    constexpr SyncProcessIncarnation(
        const SyncProcessIncarnation&) noexcept = default;
    constexpr SyncProcessIncarnation& operator=(
        const SyncProcessIncarnation&) noexcept = default;
    constexpr SyncProcessIncarnation(
        SyncProcessIncarnation&&) noexcept = default;
    constexpr SyncProcessIncarnation& operator=(
        SyncProcessIncarnation&&) noexcept = default;
    constexpr ~SyncProcessIncarnation() noexcept {}

    [[nodiscard]] constexpr bool valid() const noexcept {
        return value_ != 0U;
    }

    friend constexpr bool operator==(
        const SyncProcessIncarnation&,
        const SyncProcessIncarnation&) noexcept = default;

private:
    explicit constexpr SyncProcessIncarnation(std::uint64_t value) noexcept
        : value_(value) {}

    std::uint64_t value_ = 0U;

    friend class detail::SyncProcessIncarnationAccess;
};

static_assert(sizeof(SyncProcessIncarnation) == sizeof(std::uint64_t));
static_assert(alignof(SyncProcessIncarnation) == alignof(std::uint64_t));
static_assert(!std::is_trivially_copyable_v<SyncProcessIncarnation>);
static_assert(std::is_standard_layout_v<SyncProcessIncarnation>);
static_assert(!std::is_constructible_v<SyncProcessIncarnation, std::uint64_t>);
static_assert(!std::is_convertible_v<std::uint64_t, SyncProcessIncarnation>);


inline constexpr int kSyncProcessCapabilityViolationExitCode = 86;

[[nodiscard]] SyncProcessIncarnation
current_sync_process_incarnation_noexcept() noexcept;

[[nodiscard]] bool sync_process_incarnation_is_current(
    SyncProcessIncarnation expected) noexcept;

// Empty proof is a programming error and throws. A nonempty proof from another
// process is an inherited-capability violation and exits immediately without
// C++ unwinding or atexit processing.
void require_sync_process_incarnation_or_fail_stop(
    SyncProcessIncarnation expected,
    std::string_view label);

[[noreturn]] void fail_stop_on_sync_process_capability_violation_noexcept()
    noexcept;

}  // namespace anonsync
