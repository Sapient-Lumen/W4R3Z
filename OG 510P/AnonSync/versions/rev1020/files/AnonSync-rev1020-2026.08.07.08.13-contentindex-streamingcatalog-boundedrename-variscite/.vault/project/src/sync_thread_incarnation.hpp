#pragma once

#include "sync_process_incarnation.hpp"

#include <cstdint>
#include <string_view>
#include <type_traits>

namespace anonsync {

namespace detail {
class SyncThreadIncarnationAccess;
}

// One typed process-local proof for one exact C++ thread lifetime. Native
// thread identifiers may be reused after a thread exits, so retained
// capability owners bind to a monotonically allocated incarnation instead.
// The value is refreshed after fork because thread_local storage is copied into
// the child while the originating thread lifetime is not. It is not an
// interchange format. Deliberately exposing no integer constructor and making
// the value non-trivially-copyable prevents ordinary numeric, row, wire, or
// std::bit_cast evidence from being confused with live thread authority. This
// is domain separation against accidental evidence confusion, not a security
// boundary against hostile code already executing in this process.
// It is also an affinity proof, not synchronization: callers must not race an
// owner's lifetime or mutate its storage concurrently and expect this token to
// repair the underlying C++ object-lifetime violation.
class SyncThreadIncarnation final {
public:
    constexpr SyncThreadIncarnation() noexcept = default;
    constexpr SyncThreadIncarnation(
        const SyncThreadIncarnation&) noexcept = default;
    constexpr SyncThreadIncarnation& operator=(
        const SyncThreadIncarnation&) noexcept = default;
    constexpr SyncThreadIncarnation(
        SyncThreadIncarnation&&) noexcept = default;
    constexpr SyncThreadIncarnation& operator=(
        SyncThreadIncarnation&&) noexcept = default;
    constexpr ~SyncThreadIncarnation() noexcept {}

    [[nodiscard]] constexpr bool valid() const noexcept {
        return value_ != 0U;
    }

    friend constexpr bool operator==(
        const SyncThreadIncarnation&,
        const SyncThreadIncarnation&) noexcept = default;

private:
    explicit constexpr SyncThreadIncarnation(std::uint64_t value) noexcept
        : value_(value) {}

    std::uint64_t value_ = 0U;

    friend class detail::SyncThreadIncarnationAccess;
};

static_assert(sizeof(SyncThreadIncarnation) == sizeof(std::uint64_t));
static_assert(alignof(SyncThreadIncarnation) == alignof(std::uint64_t));
static_assert(!std::is_trivially_copyable_v<SyncThreadIncarnation>);
static_assert(std::is_standard_layout_v<SyncThreadIncarnation>);
static_assert(!std::is_constructible_v<SyncThreadIncarnation, std::uint64_t>);
static_assert(!std::is_convertible_v<std::uint64_t, SyncThreadIncarnation>);

[[nodiscard]] SyncThreadIncarnation
current_sync_thread_incarnation_noexcept() noexcept;

[[nodiscard]] bool sync_thread_incarnation_is_current(
    SyncThreadIncarnation expected) noexcept;

// Empty proof is a programming error. A nonempty proof from another thread is
// rejected before the caller may inspect or mutate the protected owner.
void require_sync_thread_incarnation_or_throw(
    SyncThreadIncarnation expected,
    std::string_view label);

// noexcept owner operations and destructors cannot report a foreign-thread
// ownership violation. They fail stopped without unwinding or teardown hooks.
[[noreturn]] void fail_stop_on_sync_thread_capability_violation_noexcept()
    noexcept;

}  // namespace anonsync
