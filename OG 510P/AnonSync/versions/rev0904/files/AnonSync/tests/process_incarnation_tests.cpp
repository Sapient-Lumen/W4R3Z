#if !defined(_WIN32)
#include "inherited_test_process.hpp"
#endif
#include "sync_process_incarnation.hpp"
#include "sync_process_incarnation_internal.hpp"

#include <cerrno>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <type_traits>

#if defined(_WIN32)
#include <process.h>
#elif defined(__unix__) || defined(__APPLE__)
#include <sys/wait.h>
#include <unistd.h>
#endif

namespace {

using anonsync::SyncProcessIncarnation;
using anonsync::current_sync_process_incarnation_noexcept;
using anonsync::detail::advance_sync_process_incarnation_after_fork;
using anonsync::detail::compose_sync_process_incarnation;
using anonsync::detail::kSyncProcessMaximumLineageGeneration;
using anonsync::detail::kSyncPoisonedProcessIncarnation;
using anonsync::detail::refresh_sync_process_incarnation;
using anonsync::detail::sync_kernel_pid_from_process_incarnation;
using anonsync::detail::sync_lineage_generation_from_process_incarnation;
using anonsync::kSyncProcessCapabilityViolationExitCode;
using anonsync::require_sync_process_incarnation_or_fail_stop;
using namespace std::chrono_literals;
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_or_throw;
#endif
#if !defined(_WIN32)
using anonsync::test::spawn_inherited_test_process_with_output_capture_or_throw;
#endif

struct TestState final {
    std::uint64_t passed = 0;
    std::uint64_t failed = 0;

    void require(bool condition, const std::string& label) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "FAIL: " << label << "\n";
        }
    }
};

void test_pure_incarnation_algebra(TestState& test) {
    constexpr std::uint32_t parent_pid = 101U;
    constexpr std::uint32_t child_pid = 202U;
    constexpr std::uint32_t sibling_pid = 303U;
    constexpr SyncProcessIncarnation parent =
        compose_sync_process_incarnation(1U, parent_pid);
    constexpr SyncProcessIncarnation child =
        advance_sync_process_incarnation_after_fork(parent, child_pid);
    constexpr SyncProcessIncarnation sibling =
        advance_sync_process_incarnation_after_fork(parent, sibling_pid);
    constexpr SyncProcessIncarnation recycled =
        advance_sync_process_incarnation_after_fork(child, parent_pid);

    test.require(parent.valid() &&
                     sync_kernel_pid_from_process_incarnation(parent) == parent_pid &&
                     sync_lineage_generation_from_process_incarnation(parent) == 1U,
                 "composition preserves exact PID and generation");
    test.require(child != parent &&
                     sync_lineage_generation_from_process_incarnation(child) == 2U,
                 "child receives a distinct next-generation token");
    test.require(
        advance_sync_process_incarnation_after_fork(child, child_pid) ==
            child,
        "fork child hook is idempotent after an earlier handler refreshed the PID");
    test.require(sibling != child &&
                     sync_lineage_generation_from_process_incarnation(sibling) == 2U,
                 "siblings differ by PID within one generation");
    test.require(recycled != parent &&
                     sync_kernel_pid_from_process_incarnation(recycled) == parent_pid &&
                     sync_lineage_generation_from_process_incarnation(recycled) == 3U,
                 "recycled ancestor PID cannot resurrect ancestor authority");
    test.require(refresh_sync_process_incarnation(parent, parent_pid) == parent,
                 "same PID refresh is stable");
    test.require(refresh_sync_process_incarnation(parent, child_pid) == child,
                 "unexpected PID change advances as a fallback");
    test.require(refresh_sync_process_incarnation({}, parent_pid) == parent,
                 "pristine process state mints generation one");
    test.require(!refresh_sync_process_incarnation(
                      kSyncPoisonedProcessIncarnation, parent_pid)
                      .valid(),
                 "poisoned lineage cannot be reminted");
    const SyncProcessIncarnation maximum = compose_sync_process_incarnation(
        kSyncProcessMaximumLineageGeneration, parent_pid);
    test.require(!advance_sync_process_incarnation_after_fork(
                      maximum, child_pid)
                      .valid(),
                 "lineage exhaustion fails closed before wraparound");
    test.require(!compose_sync_process_incarnation(0, parent_pid).valid() &&
                     !compose_sync_process_incarnation(1, 0).valid(),
                 "zero generation or PID cannot compose authority");
}

void test_empty_process_proof_rejected(TestState& test) {
    bool rejected = false;
    try {
        require_sync_process_incarnation_or_fail_stop(
            {}, "empty process proof test");
    } catch (const std::logic_error& error) {
        rejected = std::string(error.what()).find(
                       "process-incarnation proof is empty") !=
                   std::string::npos;
    }
    test.require(rejected,
                 "empty process proof is rejected as a programming error");
}

void test_live_process_token(TestState& test) {
    const SyncProcessIncarnation first = current_sync_process_incarnation_noexcept();
    const SyncProcessIncarnation second = current_sync_process_incarnation_noexcept();
    test.require(first.valid() && first == second,
                 "live token is nonzero and stable");
#if defined(_WIN32)
    const auto pid = static_cast<std::uint32_t>(::_getpid());
#else
    const auto pid = static_cast<std::uint32_t>(::getpid());
#endif
    test.require(sync_kernel_pid_from_process_incarnation(first) == pid,
                 "live token binds current kernel PID");
    test.require(sync_lineage_generation_from_process_incarnation(first) != 0,
                 "live token binds a nonzero lineage generation");
    test.require(!std::is_constructible_v<SyncProcessIncarnation, std::uint64_t> &&
                     !std::is_convertible_v<std::uint64_t, SyncProcessIncarnation> &&
                     !std::is_trivially_copyable_v<SyncProcessIncarnation>,
                 "raw integers and bit-casts cannot manufacture process authority");
    require_sync_process_incarnation_or_fail_stop(first, "live process token");
    test.require(true, "current token authorizes current process");
}

#if defined(__unix__) || defined(__APPLE__)

struct ProcessIncarnationObservation final {
    std::uint32_t kernel_pid = 0;
    std::uint32_t lineage_generation = 0;
};

static_assert(std::is_trivially_copyable_v<ProcessIncarnationObservation>);
static_assert(sizeof(ProcessIncarnationObservation) ==
              2U * sizeof(std::uint32_t));

[[nodiscard]] ProcessIncarnationObservation observe_process_incarnation(
    SyncProcessIncarnation token) noexcept {
    return {
        sync_kernel_pid_from_process_incarnation(token),
        sync_lineage_generation_from_process_incarnation(token),
    };
}

bool write_exact(int fd, const void* data, std::size_t count) noexcept {
    const auto* cursor = static_cast<const unsigned char*>(data);
    while (count != 0U) {
        const ssize_t rc = ::write(fd, cursor, count);
        if (rc < 0 && errno == EINTR) continue;
        if (rc <= 0) return false;
        const auto amount = static_cast<std::size_t>(rc);
        cursor += amount;
        count -= amount;
    }
    return true;
}

[[nodiscard]] ProcessIncarnationObservation decode_observation_or_throw(
    const std::string& bytes, const std::string& label) {
    if (bytes.size() != sizeof(ProcessIncarnationObservation)) {
        throw std::runtime_error(
            label + " returned " + std::to_string(bytes.size()) +
            " bytes instead of one typed process-incarnation observation");
    }
    ProcessIncarnationObservation observation{};
    std::memcpy(&observation, bytes.data(), sizeof(observation));
    return observation;
}

void test_direct_fork(TestState& test) {
    const SyncProcessIncarnation parent =
        current_sync_process_incarnation_noexcept();
    auto child = spawn_inherited_test_process_with_output_capture_or_throw(
        [&](int output_descriptor) {
            const SyncProcessIncarnation token =
                current_sync_process_incarnation_noexcept();
            const ProcessIncarnationObservation observation =
                observe_process_incarnation(token);
            const bool exact_next_generation =
                token != parent &&
                observation.lineage_generation ==
                    sync_lineage_generation_from_process_incarnation(parent) +
                        1U;
            return exact_next_generation &&
                           write_exact(output_descriptor, &observation,
                                       sizeof(observation))
                       ? 0
                       : 90;
        },
        "direct process-incarnation observation");
    const pid_t child_pid = child.process_id();
    const anonsync::test::InheritedTestProcessOutput output =
        child.wait_for_exit_with_output(
            5s, sizeof(ProcessIncarnationObservation),
            "direct process-incarnation observation");
    const ProcessIncarnationObservation observation =
        decode_observation_or_throw(output.bytes, "direct child");
    test.require(WIFEXITED(output.wait_status) &&
                     WEXITSTATUS(output.wait_status) == 0,
                 "direct child receives and reports a valid token");
    test.require(observation.kernel_pid ==
                     static_cast<std::uint32_t>(child_pid),
                 "direct child observation binds child PID");
    test.require(current_sync_process_incarnation_noexcept() == parent,
                 "child generation cannot mutate parent state");
}

void test_unobserved_intermediate_fork(TestState& test) {
    const SyncProcessIncarnation parent =
        current_sync_process_incarnation_noexcept();
    auto intermediate =
        spawn_inherited_test_process_with_output_capture_or_throw(
            [&](int output_descriptor) {
                // Do not inspect the intermediate token. The atfork hook must
                // preserve that edge before the nested helper creates the
                // grandchild whose observation is exported.
                auto grandchild = spawn_inherited_test_process_or_throw(
                    [&] {
                        const ProcessIncarnationObservation observation =
                            observe_process_incarnation(
                                current_sync_process_incarnation_noexcept());
                        return write_exact(output_descriptor, &observation,
                                           sizeof(observation))
                                   ? 0
                                   : 92;
                    },
                    "grandchild process-incarnation observation");
                const int status = grandchild.wait_for_exit(
                    5s, "grandchild process-incarnation observation");
                return WIFEXITED(status) && WEXITSTATUS(status) == 0 ? 0
                                                                     : 93;
            },
            "unobserved intermediate process-incarnation observation");
    const anonsync::test::InheritedTestProcessOutput output =
        intermediate.wait_for_exit_with_output(
            5s, sizeof(ProcessIncarnationObservation),
            "unobserved intermediate process-incarnation observation");
    const ProcessIncarnationObservation observation =
        decode_observation_or_throw(output.bytes, "grandchild");
    test.require(WIFEXITED(output.wait_status) &&
                     WEXITSTATUS(output.wait_status) == 0,
                 "grandchild reports through an unobserved intermediate fork");
    test.require(observation.lineage_generation ==
                     sync_lineage_generation_from_process_incarnation(parent) +
                         2U,
                 "every ordinary fork edge advances lineage before child code");
    test.require(observation.kernel_pid != 0U &&
                     observation.kernel_pid !=
                         sync_kernel_pid_from_process_incarnation(parent),
                 "grandchild observation names a distinct live lineage node");
}

void test_inherited_token_fail_stop(TestState& test) {
    const SyncProcessIncarnation parent =
        current_sync_process_incarnation_noexcept();
    auto child = spawn_inherited_test_process_or_throw(
        [&] {
            require_sync_process_incarnation_or_fail_stop(parent,
                                                          "inherited token");
            return 94;
        },
        "inherited process-incarnation token");
    const int status = child.wait_for_exit(
        5s, "inherited process-incarnation token");
    test.require(WIFEXITED(status) &&
                     WEXITSTATUS(status) ==
                         kSyncProcessCapabilityViolationExitCode,
                 "inherited parent token takes direct fail-stop path");
}

#else

void test_direct_fork(TestState& test) {
    test.require(true, "fork proof unavailable on this platform");
}
void test_unobserved_intermediate_fork(TestState& test) {
    test.require(true, "deep-fork proof unavailable on this platform");
}
void test_inherited_token_fail_stop(TestState& test) {
    test.require(true, "inherited-token proof unavailable on this platform");
}

#endif

}  // namespace

int main() {
    TestState test;
    try {
        test_pure_incarnation_algebra(test);
        test_empty_process_proof_rejected(test);
        test_live_process_token(test);
        test_direct_fork(test);
        test_unobserved_intermediate_fork(test);
        test_inherited_token_fail_stop(test);
    } catch (const std::exception& error) {
        ++test.failed;
        std::cerr << "FAIL: unexpected exception: " << error.what() << "\n";
    }
    std::cout << "anonsync process incarnation tests checks="
              << test.passed << " failed=" << test.failed << "\n";
    return test.failed == 0U ? EXIT_SUCCESS : EXIT_FAILURE;
}
