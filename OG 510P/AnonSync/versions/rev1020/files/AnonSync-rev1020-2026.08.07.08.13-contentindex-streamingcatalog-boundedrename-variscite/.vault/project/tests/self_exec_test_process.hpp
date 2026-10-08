#pragma once

#include <chrono>
#include <cstddef>
#include <filesystem>
#include <string>
#include <string_view>
#include <vector>

#include "test_process_topology_owner.hpp"

#include <sys/types.h>

namespace anonsync::test {

struct SelfExecTestProcessOutput final {
    std::string standard_output;
    std::string standard_error;
};

// One test-only process owner for crash/frontier probes. The parent pins the
// exact running executable object, prepares a versioned argv instruction,
// closes every unrelated descriptor through posix_spawn file actions, supplies
// a small allowlisted environment, resets child signal state, and creates a
// child-owned process group before exec. The returned owner is move-only,
// bounded-waited, and fail-safe: an unreaped helper group is killed and its
// leader is reaped during destruction.
class SelfExecTestProcess final {
public:
    SelfExecTestProcess(const SelfExecTestProcess&) = delete;
    SelfExecTestProcess& operator=(const SelfExecTestProcess&) = delete;

    SelfExecTestProcess(SelfExecTestProcess&& other) noexcept;
    SelfExecTestProcess& operator=(SelfExecTestProcess&& other) noexcept;
    ~SelfExecTestProcess();

    // Consumes one uncaptured helper and returns its normal byte-sized exit
    // code. Signal termination and every wait failure remain exceptional. This
    // is used only where the caller has a small reviewed set of authoritative
    // outcomes rather than one exact status.
    [[nodiscard]] int wait_for_exit_code(
        std::chrono::milliseconds timeout, std::string_view label);

    void wait_for_exact_exit(int expected_exit,
                             std::chrono::milliseconds timeout,
                             std::string_view label);

    // Captured helpers must use this wait so stdout and stderr are drained
    // concurrently while the child runs. Each stream has an explicit byte
    // budget; timeout, read failure, invalid status, and overflow consume the
    // complete process/capture authority before throwing.
    [[nodiscard]] SelfExecTestProcessOutput wait_for_exact_exit_with_output(
        int expected_exit,
        std::chrono::milliseconds timeout,
        std::size_t maximum_bytes_per_stream,
        std::string_view label);

    [[nodiscard]] bool active() const noexcept {
        return topology_.active() || stdout_read_ >= 0 || stderr_read_ >= 0;
    }
    [[nodiscard]] pid_t process_id() const noexcept {
        return topology_.leader_process_id();
    }
    [[nodiscard]] bool captures_output() const noexcept {
        return stdout_read_ >= 0 && stderr_read_ >= 0;
    }

private:
    friend SelfExecTestProcess spawn_self_exec_test_process_or_throw(
        const std::filesystem::path& executable,
        const std::vector<std::string>& arguments);
    friend SelfExecTestProcess
    spawn_self_exec_test_process_with_output_capture_or_throw(
        const std::filesystem::path& executable,
        const std::vector<std::string>& arguments);

    explicit SelfExecTestProcess(pid_t child,
                                 int stdout_read = -1,
                                 int stderr_read = -1) noexcept
        : topology_(child, child),
          stdout_read_(stdout_read),
          stderr_read_(stderr_read) {}
    void terminate_and_reap_noexcept() noexcept;
    void close_output_capture_noexcept() noexcept;

    detail::TestProcessTopologyOwner topology_;
    int stdout_read_ = -1;
    int stderr_read_ = -1;
};

// Linux-focused tests use /proc/self/exe rather than trusting argv[0] or PATH.
[[nodiscard]] std::filesystem::path current_self_executable_or_throw();

// Arguments do not include argv[0]. The path must name the exact current
// executable object; it is NUL-fenced, opened with O_NOFOLLOW, and executed via
// a pinned descriptor. All strings are bounded and the spawn either returns one
// owned PID or throws without leaking a process owner.
[[nodiscard]] SelfExecTestProcess spawn_self_exec_test_process_or_throw(
    const std::filesystem::path& executable,
    const std::vector<std::string>& arguments);

// Like spawn_self_exec_test_process_or_throw(), but independently redirects
// stdout and stderr into parent-owned close-on-exec pipes. The read ends are
// nonblocking; the child write ends remain blocking. Callers must consume the
// owner with wait_for_exact_exit_with_output().
[[nodiscard]] SelfExecTestProcess
spawn_self_exec_test_process_with_output_capture_or_throw(
    const std::filesystem::path& executable,
    const std::vector<std::string>& arguments);

// Call at the start of every helper mode, before opening SQLite or filesystem
// state. It proves the running image matches the pinned descriptor and consumes
// that descriptor, then proves an isolated process group, only descriptors
// 0/1/2, the exact allowlisted environment, default sentinel disposition, and
// an empty signal mask.
void verify_self_exec_child_boundary_or_throw();

}  // namespace anonsync::test
