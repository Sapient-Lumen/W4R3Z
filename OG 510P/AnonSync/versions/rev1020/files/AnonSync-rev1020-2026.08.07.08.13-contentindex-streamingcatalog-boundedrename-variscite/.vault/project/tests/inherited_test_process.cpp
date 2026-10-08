#include "inherited_test_process.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <fcntl.h>
#include <optional>
#include <poll.h>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <utility>

#include <sys/wait.h>
#include <unistd.h>

namespace anonsync::test {
namespace {

using namespace std::chrono_literals;

constexpr std::size_t kMaximumInheritedCaptureBytes = 16U * 1024U * 1024U;
constexpr auto kWaitSlice = 5ms;
constexpr auto kCapturePollSlice = 10ms;

// A nested inheritance probe must remain in the top-level child's process
// group. Otherwise killing the top-level owner could strand a grandchild in a
// newly-created group. The marker is copied by fork and intentionally changed
// only in child copies.
thread_local bool inside_inherited_test_process_child = false;

[[noreturn]] void throw_errno(std::string_view operation) {
    throw std::system_error(errno, std::generic_category(),
                            std::string(operation));
}

class ScopedDescriptor final {
public:
    explicit ScopedDescriptor(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;
    ScopedDescriptor(ScopedDescriptor&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this != &other) {
            reset();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }
    ~ScopedDescriptor() { reset(); }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }
    void reset() noexcept {
        if (descriptor_ < 0) return;
        const int descriptor = std::exchange(descriptor_, -1);
        // A second close after EINTR can target a concurrently reused number.
        // Descriptor authority is therefore consumed exactly once.
        (void)::close(descriptor);
    }

private:
    int descriptor_ = -1;
};

struct CapturePipe final {
    ScopedDescriptor read_end;
    ScopedDescriptor write_end;
};

[[nodiscard]] ScopedDescriptor promote_descriptor_or_throw(
    ScopedDescriptor descriptor, std::string_view label) {
    if (descriptor.get() >= 3) return descriptor;
    const int replacement = ::fcntl(descriptor.get(), F_DUPFD, 3);
    if (replacement < 0) {
        throw_errno(std::string(label) + " fcntl(F_DUPFD)");
    }
    if (::fcntl(replacement, F_SETFD, FD_CLOEXEC) != 0) {
        const int saved_errno = errno;
        (void)::close(replacement);
        errno = saved_errno;
        throw_errno(std::string(label) + " fcntl(F_SETFD FD_CLOEXEC)");
    }
    return ScopedDescriptor(replacement);
}

[[nodiscard]] CapturePipe make_capture_pipe_or_throw() {
    int descriptors[2] = {-1, -1};
#if defined(__linux__)
    if (::pipe2(descriptors, O_CLOEXEC) != 0) {
        throw_errno("inherited test process pipe2");
    }
#else
    if (::pipe(descriptors) != 0) {
        throw_errno("inherited test process pipe");
    }
    for (int descriptor : descriptors) {
        if (::fcntl(descriptor, F_SETFD, FD_CLOEXEC) != 0) {
            const int saved_errno = errno;
            (void)::close(descriptors[0]);
            (void)::close(descriptors[1]);
            errno = saved_errno;
            throw_errno("inherited test process pipe FD_CLOEXEC");
        }
    }
#endif

    CapturePipe pipe{ScopedDescriptor(descriptors[0]),
                     ScopedDescriptor(descriptors[1])};
    pipe.read_end = promote_descriptor_or_throw(
        std::move(pipe.read_end), "inherited capture read end");
    pipe.write_end = promote_descriptor_or_throw(
        std::move(pipe.write_end), "inherited capture write end");

    const int flags = ::fcntl(pipe.read_end.get(), F_GETFL);
    if (flags < 0) throw_errno("inherited capture fcntl(F_GETFL)");
    if (::fcntl(pipe.read_end.get(), F_SETFL, flags | O_NONBLOCK) != 0) {
        throw_errno("inherited capture fcntl(F_SETFL O_NONBLOCK)");
    }
    return pipe;
}

void close_descriptor_noexcept(int& descriptor) noexcept {
    if (descriptor < 0) return;
    const int owned = std::exchange(descriptor, -1);
    (void)::close(owned);
}

[[nodiscard]] std::string child_status_text(int status) {
    if (WIFEXITED(status)) {
        return "exit status " + std::to_string(WEXITSTATUS(status));
    }
    if (WIFSIGNALED(status)) {
        return "signal " + std::to_string(WTERMSIG(status));
    }
    if (WIFSTOPPED(status)) {
        return "stopped by signal " + std::to_string(WSTOPSIG(status));
    }
    return "unclassified wait status " + std::to_string(status);
}

void drain_capture_or_throw(int& descriptor,
                            std::string& output,
                            std::size_t maximum_bytes,
                            std::string_view label) {
    if (descriptor < 0) return;
    std::array<char, 4096> buffer{};
    for (;;) {
        const ssize_t count = ::read(descriptor, buffer.data(), buffer.size());
        if (count > 0) {
            const std::size_t bytes = static_cast<std::size_t>(count);
            if (output.size() > maximum_bytes ||
                bytes > maximum_bytes - output.size()) {
                throw std::runtime_error(
                    std::string(label) + " inherited output exceeded its " +
                    std::to_string(maximum_bytes) + "-byte budget");
            }
            output.append(buffer.data(), bytes);
            continue;
        }
        if (count == 0) {
            close_descriptor_noexcept(descriptor);
            return;
        }
        if (errno == EINTR) continue;
        if (errno == EAGAIN || errno == EWOULDBLOCK) return;
        throw_errno(std::string(label) + " read inherited output");
    }
}

}  // namespace

InheritedTestProcess::InheritedTestProcess(
    InheritedTestProcess&& other) noexcept
    : topology_(std::move(other.topology_)),
      output_read_(std::exchange(other.output_read_, -1)) {}

InheritedTestProcess& InheritedTestProcess::operator=(
    InheritedTestProcess&& other) noexcept {
    if (this != &other) {
        terminate_and_reap_noexcept();
        topology_ = std::move(other.topology_);
        output_read_ = std::exchange(other.output_read_, -1);
    }
    return *this;
}

InheritedTestProcess::~InheritedTestProcess() {
    terminate_and_reap_noexcept();
}

void InheritedTestProcess::close_output_noexcept() noexcept {
    close_descriptor_noexcept(output_read_);
}

void InheritedTestProcess::terminate_and_reap_noexcept() noexcept {
    topology_.terminate_and_reap_noexcept();
    close_output_noexcept();
}

int InheritedTestProcess::wait_for_exit(
    std::chrono::milliseconds timeout, std::string_view label) {
    if (topology_.leader_process_id() <= 0) {
        throw std::logic_error(
            "inherited child has already been reaped or was never owned");
    }
    if (output_read_ >= 0) {
        throw std::logic_error(
            "captured inherited child requires wait_for_exit_with_output");
    }
    if (timeout <= std::chrono::milliseconds::zero()) {
        throw std::invalid_argument("inherited child timeout must be positive");
    }

    const auto deadline = std::chrono::steady_clock::now() + timeout;
    for (;;) {
        if (const std::optional<int> status =
                topology_.try_complete_exit_or_throw(label)) {
            return *status;
        }
        if (std::chrono::steady_clock::now() >= deadline) {
            topology_.terminate_and_reap_noexcept();
            throw std::runtime_error(std::string(label) +
                                     " timed out and was killed and reaped");
        }
        std::this_thread::sleep_for(kWaitSlice);
    }
}

void InheritedTestProcess::wait_for_exact_exit(
    int expected_exit,
    std::chrono::milliseconds timeout,
    std::string_view label) {
    if (expected_exit < 0 || expected_exit > 255) {
        throw std::invalid_argument("expected inherited exit must fit in one byte");
    }
    const int status = wait_for_exit(timeout, label);
    if (!WIFEXITED(status) || WEXITSTATUS(status) != expected_exit) {
        throw std::runtime_error(
            std::string(label) + " returned " + child_status_text(status) +
            ", expected exit status " + std::to_string(expected_exit));
    }
}

InheritedTestProcessOutput InheritedTestProcess::wait_for_exit_with_output(
    std::chrono::milliseconds timeout,
    std::size_t maximum_output_bytes,
    std::string_view label) {
    if (topology_.leader_process_id() <= 0) {
        throw std::logic_error(
            "inherited child has already been reaped or was never owned");
    }
    if (output_read_ < 0) {
        throw std::logic_error(
            "inherited child was not spawned with output capture");
    }
    if (timeout <= std::chrono::milliseconds::zero()) {
        throw std::invalid_argument("inherited child timeout must be positive");
    }
    if (maximum_output_bytes == 0 ||
        maximum_output_bytes > kMaximumInheritedCaptureBytes) {
        throw std::invalid_argument(
            "inherited output budget is zero or exceeds its hard limit");
    }

    const auto deadline = std::chrono::steady_clock::now() + timeout;
    InheritedTestProcessOutput result;
    result.bytes.reserve(std::min<std::size_t>(maximum_output_bytes, 4096));
    bool leader_completed = false;

    try {
        for (;;) {
            drain_capture_or_throw(output_read_, result.bytes,
                                   maximum_output_bytes, label);

            if (!leader_completed) {
                if (const std::optional<int> status =
                        topology_.try_complete_exit_or_throw(label)) {
                    result.wait_status = *status;
                    leader_completed = true;
                }
            }

            if (leader_completed && output_read_ < 0) return result;

            const auto now = std::chrono::steady_clock::now();
            if (now >= deadline) {
                throw std::runtime_error(
                    std::string(label) +
                    " timed out while collecting inherited output");
            }

            if (output_read_ >= 0) {
                struct pollfd descriptor {
                    output_read_, static_cast<short>(POLLIN | POLLHUP), 0
                };
                const auto remaining =
                    std::chrono::duration_cast<std::chrono::milliseconds>(
                        deadline - now);
                const int poll_timeout = static_cast<int>(std::max<long long>(
                    1, std::min<long long>(remaining.count(),
                                           kCapturePollSlice.count())));
                const int rc = ::poll(&descriptor, 1, poll_timeout);
                if (rc < 0 && errno != EINTR) {
                    throw_errno(std::string(label) +
                                " poll inherited output");
                }
                if (rc > 0 && (descriptor.revents & POLLNVAL) != 0) {
                    throw std::runtime_error(
                        std::string(label) +
                        " inherited output descriptor became invalid");
                }
            } else {
                std::this_thread::sleep_for(kWaitSlice);
            }
        }
    } catch (...) {
        // try_complete_exit_or_throw() atomically consumes both numeric
        // identifiers before returning. If a later pipe drain fails, this
        // cleanup is therefore descriptor-only rather than a stale group kill.
        topology_.terminate_and_reap_noexcept();
        close_output_noexcept();
        throw;
    }
}

InheritedTestProcess detail_spawn_inherited_test_process_or_throw(
    int (*entry)(void*, int),
    void* context,
    bool capture_output,
    std::string_view label) {
    if (entry == nullptr || context == nullptr) {
        throw std::invalid_argument(
            "inherited test process requires one callable context");
    }

    const bool create_process_group =
        !inside_inherited_test_process_child;
    CapturePipe pipe;
    if (capture_output) pipe = make_capture_pipe_or_throw();

    const pid_t child = ::fork();
    if (child < 0) {
        throw_errno(std::string(label) + " fork");
    }
    if (child == 0) {
        if (capture_output) pipe.read_end.reset();
        if (create_process_group && ::setpgid(0, 0) != 0) {
            ::_exit(kInheritedTestProcessSetupFailureExitCode);
        }
        inside_inherited_test_process_child = true;

        int exit_code = kInheritedTestProcessUnhandledExceptionExitCode;
        try {
            exit_code = entry(context,
                              capture_output ? pipe.write_end.get() : -1);
        } catch (...) {
            ::_exit(kInheritedTestProcessUnhandledExceptionExitCode);
        }
        if (exit_code < 0 || exit_code > 255) {
            ::_exit(kInheritedTestProcessInvalidReturnExitCode);
        }
        ::_exit(exit_code);
    }

    if (capture_output) pipe.write_end.reset();
    return InheritedTestProcess(
        child, create_process_group ? child : -1,
        capture_output ? pipe.read_end.release() : -1);
}

}  // namespace anonsync::test
