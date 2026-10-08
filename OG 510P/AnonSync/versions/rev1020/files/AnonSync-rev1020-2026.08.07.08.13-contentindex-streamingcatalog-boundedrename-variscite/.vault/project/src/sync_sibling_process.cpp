#include "sync_sibling_process.hpp"

#if !defined(_WIN32)

#include <algorithm>
#include <array>
#include <cerrno>
#include <csignal>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <fcntl.h>
#include <poll.h>
#include <spawn.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

extern char** environ;

namespace anonsync {
namespace {

namespace fs = std::filesystem;

constexpr std::size_t kMaximumExecutablePathBytes = 64U * 1024U;
constexpr std::size_t kMaximumArguments = 256U;
constexpr std::size_t kMaximumArgumentBytes = 1024U * 1024U;
constexpr std::uint64_t kMaximumCapturedStderrBytes = 64U * 1024U;

class ScopedDescriptor final {
public:
    ScopedDescriptor() noexcept = default;
    explicit ScopedDescriptor(int descriptor) noexcept
        : descriptor_(descriptor) {}
    ~ScopedDescriptor() noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
    }

    ScopedDescriptor(const ScopedDescriptor&) = delete;
    ScopedDescriptor& operator=(const ScopedDescriptor&) = delete;
    ScopedDescriptor(ScopedDescriptor&& other) noexcept
        : descriptor_(other.release()) {}
    ScopedDescriptor& operator=(ScopedDescriptor&& other) noexcept {
        if (this == &other) return *this;
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = other.release();
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        const int released = descriptor_;
        descriptor_ = -1;
        return released;
    }
    void reset() noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = -1;
    }

private:
    int descriptor_ = -1;
};

[[noreturn]] void throw_errno(
    std::string_view label,
    std::string_view operation,
    int error = errno) {
    throw std::runtime_error(
        std::string(label) + " " + std::string(operation) + ": " +
        std::strerror(error));
}

void require_label(std::string_view label) {
    if (label.empty()) {
        throw std::invalid_argument(
            "sync sibling process label must not be empty");
    }
}

[[nodiscard]] bool basename_is_portable_executable(
    std::string_view value) noexcept {
    if (value.empty() || value == "." || value == "..") return false;
    for (const unsigned char byte : value) {
        if (!((byte >= 'a' && byte <= 'z') ||
              (byte >= 'A' && byte <= 'Z') ||
              (byte >= '0' && byte <= '9') || byte == '_' || byte == '-')) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] fs::path running_executable_path_or_throw(
    std::string_view label) {
    std::vector<char> bytes(4096U);
    for (;;) {
        const ssize_t count =
            ::readlink("/proc/self/exe", bytes.data(), bytes.size());
        if (count < 0) throw_errno(label, "readlink(/proc/self/exe)");
        if (static_cast<std::size_t>(count) < bytes.size()) {
            fs::path path(std::string(bytes.data(), static_cast<std::size_t>(count)));
            if (path.empty() || !path.is_absolute() ||
                path.lexically_normal() != path || path.parent_path().empty()) {
                throw std::runtime_error(
                    std::string(label) +
                    " current executable path is not canonical absolute");
            }
            return path;
        }
        if (bytes.size() >= kMaximumExecutablePathBytes) {
            throw std::runtime_error(
                std::string(label) + " current executable path is too long");
        }
        bytes.resize(std::min(
            bytes.size() * 2U, kMaximumExecutablePathBytes));
    }
}

void require_exact_executable_or_throw(
    const fs::path& path,
    std::string_view label) {
    if (path.empty() || !path.is_absolute() ||
        path.lexically_normal() != path || path.parent_path().empty()) {
        throw std::invalid_argument(
            std::string(label) +
            " executable must be a canonical absolute path");
    }
    struct stat status {};
    if (::lstat(path.c_str(), &status) != 0) {
        throw_errno(label, "sibling lstat");
    }
    if (S_ISLNK(status.st_mode) || !S_ISREG(status.st_mode)) {
        throw std::runtime_error(
            std::string(label) +
            " sibling must be a non-symlink regular file: " +
            path.generic_string());
    }
    if (::access(path.c_str(), X_OK) != 0) {
        throw_errno(label, "sibling executable access");
    }
}

void validate_arguments_or_throw(
    const std::vector<std::string>& arguments,
    std::string_view label) {
    if (arguments.size() > kMaximumArguments) {
        throw std::invalid_argument(
            std::string(label) + " has too many arguments");
    }
    std::size_t total = 0U;
    for (const std::string& argument : arguments) {
        if (argument.find('\0') != std::string::npos) {
            throw std::invalid_argument(
                std::string(label) + " argument contains NUL");
        }
        if (argument.size() > kMaximumArgumentBytes - total) {
            throw std::invalid_argument(
                std::string(label) + " argument bytes exceed the bound");
        }
        total += argument.size();
    }
}

[[noreturn]] void terminate_child_and_throw(
    pid_t child,
    std::string message) {
    if (::kill(child, SIGKILL) != 0 && errno != ESRCH) {
        message += "; kill failed: ";
        message += std::strerror(errno);
    }
    int status = 0;
    while (::waitpid(child, &status, 0) < 0 && errno == EINTR) {}
    throw std::runtime_error(std::move(message));
}

[[nodiscard]] int wait_child_or_throw(pid_t child, std::string_view label) {
    int status = 0;
    for (;;) {
        const pid_t waited = ::waitpid(child, &status, 0);
        if (waited == child) break;
        if (waited < 0 && errno == EINTR) continue;
        if (waited < 0) throw_errno(label, "waitpid");
        throw std::runtime_error(
            std::string(label) + " waitpid returned an unexpected process");
    }
    return status;
}

}  // namespace

fs::path resolve_sync_sibling_executable_or_throw(
    std::string_view executable_basename,
    std::string_view label) {
    require_label(label);
    if (!basename_is_portable_executable(executable_basename)) {
        throw std::invalid_argument(
            std::string(label) + " basename is not portable");
    }
    const fs::path running = running_executable_path_or_throw(label);
    const fs::path sibling =
        running.parent_path() / std::string(executable_basename);
    require_exact_executable_or_throw(sibling, label);
    return sibling;
}

std::string run_sync_sibling_process_or_throw(
    const fs::path& absolute_executable,
    const std::vector<std::string>& arguments,
    std::uint64_t maximum_stdout_bytes,
    std::string_view label) {
    require_label(label);
    require_exact_executable_or_throw(absolute_executable, label);
    validate_arguments_or_throw(arguments, label);
    if (maximum_stdout_bytes == 0U ||
        maximum_stdout_bytes >
            static_cast<std::uint64_t>(std::numeric_limits<std::size_t>::max())) {
        throw std::invalid_argument(
            std::string(label) + " stdout bound is invalid");
    }

    int raw_stdout_pipe[2]{-1, -1};
    if (::pipe2(raw_stdout_pipe, O_CLOEXEC) != 0) {
        throw_errno(label, "stdout pipe creation");
    }
    ScopedDescriptor stdout_read_end(raw_stdout_pipe[0]);
    ScopedDescriptor stdout_write_end(raw_stdout_pipe[1]);

    int raw_stderr_pipe[2]{-1, -1};
    if (::pipe2(raw_stderr_pipe, O_CLOEXEC) != 0) {
        throw_errno(label, "stderr pipe creation");
    }
    ScopedDescriptor stderr_read_end(raw_stderr_pipe[0]);
    ScopedDescriptor stderr_write_end(raw_stderr_pipe[1]);

    posix_spawn_file_actions_t actions;
    const int actions_init = ::posix_spawn_file_actions_init(&actions);
    if (actions_init != 0) {
        throw_errno(label, "spawn file-actions initialization", actions_init);
    }
    bool actions_live = true;
    auto destroy_actions = [&]() noexcept {
        if (!actions_live) return;
        (void)::posix_spawn_file_actions_destroy(&actions);
        actions_live = false;
    };
    auto add_action_or_throw = [&](int result, std::string_view operation) {
        if (result == 0) return;
        destroy_actions();
        throw_errno(label, operation, result);
    };
    add_action_or_throw(
        ::posix_spawn_file_actions_adddup2(
            &actions, stdout_write_end.get(), STDOUT_FILENO),
        "spawn stdout dup2");
    add_action_or_throw(
        ::posix_spawn_file_actions_adddup2(
            &actions, stderr_write_end.get(), STDERR_FILENO),
        "spawn stderr dup2");
    add_action_or_throw(
        ::posix_spawn_file_actions_addclose(&actions, stdout_read_end.get()),
        "spawn stdout read-end close action");
    add_action_or_throw(
        ::posix_spawn_file_actions_addclose(&actions, stdout_write_end.get()),
        "spawn stdout write-end close action");
    add_action_or_throw(
        ::posix_spawn_file_actions_addclose(&actions, stderr_read_end.get()),
        "spawn stderr read-end close action");
    add_action_or_throw(
        ::posix_spawn_file_actions_addclose(&actions, stderr_write_end.get()),
        "spawn stderr write-end close action");

    const std::string executable = absolute_executable.native();
    std::vector<std::string> owned_arguments;
    owned_arguments.reserve(arguments.size() + 1U);
    owned_arguments.push_back(executable);
    owned_arguments.insert(
        owned_arguments.end(), arguments.begin(), arguments.end());
    std::vector<char*> argv;
    argv.reserve(owned_arguments.size() + 1U);
    for (std::string& argument : owned_arguments) {
        argv.push_back(argument.data());
    }
    argv.push_back(nullptr);

    pid_t child = -1;
    const int spawn_result = ::posix_spawn(
        &child, executable.c_str(), &actions, nullptr, argv.data(), environ);
    destroy_actions();
    if (spawn_result != 0) {
        throw_errno(label, "posix_spawn", spawn_result);
    }
    stdout_write_end.reset();
    stderr_write_end.reset();

    auto set_nonblocking_or_throw = [&](int descriptor,
                                         std::string_view stream) {
        const int flags = ::fcntl(descriptor, F_GETFL);
        if (flags < 0 || ::fcntl(descriptor, F_SETFL, flags | O_NONBLOCK) != 0) {
            const int error = errno;
            terminate_child_and_throw(
                child, std::string(label) + " " + std::string(stream) +
                    " nonblocking setup failed: " + std::strerror(error));
        }
    };
    set_nonblocking_or_throw(stdout_read_end.get(), "stdout");
    set_nonblocking_or_throw(stderr_read_end.get(), "stderr");

    std::string output;
    output.reserve(static_cast<std::size_t>(std::min<std::uint64_t>(
        maximum_stdout_bytes, 64U * 1024U)));
    std::string diagnostics;
    diagnostics.reserve(static_cast<std::size_t>(
        kMaximumCapturedStderrBytes));
    std::array<char, 16U * 1024U> buffer{};

    auto drain_or_throw = [&](ScopedDescriptor& read_end,
                              std::string& destination,
                              std::uint64_t maximum_bytes,
                              std::string_view stream) {
        for (;;) {
            const ssize_t count =
                ::read(read_end.get(), buffer.data(), buffer.size());
            if (count == 0) {
                read_end.reset();
                return;
            }
            if (count < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK) return;
                const int error = errno;
                terminate_child_and_throw(
                    child, std::string(label) + " " + std::string(stream) +
                        " read failed: " + std::strerror(error));
            }
            const std::size_t bytes = static_cast<std::size_t>(count);
            if (bytes > static_cast<std::size_t>(maximum_bytes) -
                            destination.size()) {
                terminate_child_and_throw(
                    child, std::string(label) + " " + std::string(stream) +
                        " exceeded the configured byte bound");
            }
            destination.append(buffer.data(), bytes);
        }
    };

    while (stdout_read_end.get() >= 0 || stderr_read_end.get() >= 0) {
        std::array<pollfd, 2U> streams{{
            {stdout_read_end.get(), POLLIN | POLLHUP, 0},
            {stderr_read_end.get(), POLLIN | POLLHUP, 0},
        }};
        int poll_result = 0;
        do {
            poll_result = ::poll(streams.data(), streams.size(), -1);
        } while (poll_result < 0 && errno == EINTR);
        if (poll_result < 0) {
            const int error = errno;
            terminate_child_and_throw(
                child, std::string(label) + " output poll failed: " +
                    std::strerror(error));
        }
        if ((streams[0].revents & POLLNVAL) != 0 ||
            (streams[1].revents & POLLNVAL) != 0) {
            terminate_child_and_throw(
                child, std::string(label) +
                    " output poll observed an invalid descriptor");
        }
        if (stdout_read_end.get() >= 0 &&
            (streams[0].revents & (POLLIN | POLLHUP | POLLERR)) != 0) {
            drain_or_throw(
                stdout_read_end, output, maximum_stdout_bytes, "stdout");
        }
        if (stderr_read_end.get() >= 0 &&
            (streams[1].revents & (POLLIN | POLLHUP | POLLERR)) != 0) {
            drain_or_throw(
                stderr_read_end, diagnostics,
                kMaximumCapturedStderrBytes, "stderr");
        }
    }

    const int status = wait_child_or_throw(child, label);
    if (WIFSIGNALED(status)) {
        throw std::runtime_error(
            std::string(label) + " terminated by signal " +
            std::to_string(WTERMSIG(status)));
    }
    if (!WIFEXITED(status)) {
        throw std::runtime_error(
            std::string(label) + " did not report a normal exit status");
    }
    const int exit_code = WEXITSTATUS(status);
    if (exit_code != 0) {
        std::string message = std::string(label) + " exited with status " +
            std::to_string(exit_code);
        if (!diagnostics.empty()) {
            message += "; bounded stderr: ";
            message += diagnostics;
        }
        if (!output.empty()) {
            message += "; bounded stdout: ";
            message += output;
        }
        throw std::runtime_error(std::move(message));
    }
    if (!diagnostics.empty()) {
        std::size_t offset = 0U;
        while (offset < diagnostics.size()) {
            const ssize_t written = ::write(
                STDERR_FILENO, diagnostics.data() + offset,
                diagnostics.size() - offset);
            if (written > 0) {
                offset += static_cast<std::size_t>(written);
                continue;
            }
            if (written < 0 && errno == EINTR) continue;
            break;
        }
    }
    return output;
}

}  // namespace anonsync

#endif
