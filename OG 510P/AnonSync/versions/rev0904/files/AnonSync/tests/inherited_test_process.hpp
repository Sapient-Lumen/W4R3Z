#pragma once

#include <chrono>
#include <concepts>
#include <cstddef>
#include <functional>
#include <memory>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

#include "test_process_topology_owner.hpp"

#include <sys/types.h>

namespace anonsync::test {

inline constexpr int kInheritedTestProcessUnhandledExceptionExitCode = 124;
inline constexpr int kInheritedTestProcessInvalidReturnExitCode = 125;
inline constexpr int kInheritedTestProcessSetupFailureExitCode = 126;

struct InheritedTestProcessOutput final {
    int wait_status = 0;
    std::string bytes;
};

// Test-only owner for probes whose exact subject is state inherited through an
// ordinary fork. This is deliberately distinct from SelfExecTestProcess:
// callers may execute only the minimal inherited-state observation under test.
// The parent owns the leader, an optional byte pipe, a monotonic deadline, and
// top-level process-group cleanup as one move-only capability.
class InheritedTestProcess final {
public:
    InheritedTestProcess(const InheritedTestProcess&) = delete;
    InheritedTestProcess& operator=(const InheritedTestProcess&) = delete;

    InheritedTestProcess(InheritedTestProcess&& other) noexcept;
    InheritedTestProcess& operator=(InheritedTestProcess&& other) noexcept;
    ~InheritedTestProcess();

    // Returns the raw wait status after consuming the leader. Captured probes
    // must use wait_for_exit_with_output() so pipe progress and process progress
    // share one deadline.
    [[nodiscard]] int wait_for_exit(std::chrono::milliseconds timeout,
                                    std::string_view label);

    void wait_for_exact_exit(int expected_exit,
                             std::chrono::milliseconds timeout,
                             std::string_view label);

    [[nodiscard]] InheritedTestProcessOutput wait_for_exit_with_output(
        std::chrono::milliseconds timeout,
        std::size_t maximum_output_bytes,
        std::string_view label);

    [[nodiscard]] bool active() const noexcept {
        return topology_.active() || output_read_ >= 0;
    }
    [[nodiscard]] pid_t process_id() const noexcept {
        return topology_.leader_process_id();
    }
    [[nodiscard]] bool captures_output() const noexcept {
        return output_read_ >= 0;
    }

private:
    friend InheritedTestProcess detail_spawn_inherited_test_process_or_throw(
        int (*entry)(void*, int), void* context, bool capture_output,
        std::string_view label);

    explicit InheritedTestProcess(pid_t leader,
                                  pid_t process_group,
                                  int output_read) noexcept
        : topology_(leader, process_group), output_read_(output_read) {}

    void terminate_and_reap_noexcept() noexcept;
    void close_output_noexcept() noexcept;

    detail::TestProcessTopologyOwner topology_;
    int output_read_ = -1;
};

// Internal non-template fork boundary. Keeping the one raw fork call here lets
// the source audit prove that no individual test owns ad-hoc PID/wait/kill
// choreography.
[[nodiscard]] InheritedTestProcess detail_spawn_inherited_test_process_or_throw(
    int (*entry)(void*, int), void* context, bool capture_output,
    std::string_view label);

template <typename Function>
requires std::invocable<Function&> &&
         std::convertible_to<std::invoke_result_t<Function&>, int>
[[nodiscard]] InheritedTestProcess spawn_inherited_test_process_or_throw(
    Function&& function, std::string_view label) {
    using StoredFunction = std::remove_reference_t<Function>;
    auto trampoline = +[](void* context, int) -> int {
        return static_cast<int>(
            std::invoke(*static_cast<StoredFunction*>(context)));
    };
    return detail_spawn_inherited_test_process_or_throw(
        trampoline, std::addressof(function), false, label);
}

template <typename Function>
requires std::invocable<Function&, int> &&
         std::convertible_to<std::invoke_result_t<Function&, int>, int>
[[nodiscard]] InheritedTestProcess
spawn_inherited_test_process_with_output_capture_or_throw(
    Function&& function, std::string_view label) {
    using StoredFunction = std::remove_reference_t<Function>;
    auto trampoline = +[](void* context, int output_descriptor) -> int {
        return static_cast<int>(std::invoke(
            *static_cast<StoredFunction*>(context), output_descriptor));
    };
    return detail_spawn_inherited_test_process_or_throw(
        trampoline, std::addressof(function), true, label);
}

}  // namespace anonsync::test
