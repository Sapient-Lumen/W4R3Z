#include "self_exec_test_process.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <filesystem>
#include <limits>
#include <memory>
#include <optional>
#include <poll.h>
#include <spawn.h>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <utility>
#include <vector>

#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

extern char** environ;

namespace anonsync::test {
namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;

constexpr std::size_t kMaximumArgumentCount = 32;
constexpr std::size_t kMaximumArgumentBytes = 64U * 1024U;
constexpr std::size_t kMaximumSingleArgumentBytes = 4096;
constexpr std::size_t kMaximumEnvironmentBytes = 64U * 1024U;
constexpr std::size_t kMaximumCaptureBytesPerStream = 16U * 1024U * 1024U;
constexpr int kPinnedExecutableDescriptor = 3;
constexpr int kFirstSanitizedDescriptor = kPinnedExecutableDescriptor + 1;
constexpr std::string_view kPinnedExecutablePath = "/proc/self/fd/3";
constexpr auto kCapturePollSlice = 10ms;
constexpr std::array<std::string_view, 7> kPropagatedEnvironmentNames{{
    "ASAN_OPTIONS",
    "ASAN_SYMBOLIZER_PATH",
    "LSAN_OPTIONS",
    "MSAN_OPTIONS",
    "TSAN_OPTIONS",
    "UBSAN_OPTIONS",
    "LLVM_SYMBOLIZER_PATH",
}};

[[noreturn]] void throw_errno(std::string_view operation) {
    throw std::system_error(errno, std::generic_category(),
                            std::string(operation));
}

[[noreturn]] void throw_error_code(int code, std::string_view operation) {
    throw std::system_error(code, std::generic_category(),
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

private:
    void reset() noexcept {
        if (descriptor_ < 0) return;
        const int descriptor = std::exchange(descriptor_, -1);
        // On Linux, retrying close() after EINTR can close an unrelated file
        // descriptor that another thread reused. Ownership is consumed once.
        (void)::close(descriptor);
    }

    int descriptor_ = -1;
};

struct CapturePipe final {
    ScopedDescriptor read_end;
    ScopedDescriptor write_end;
};

class SpawnFileActions final {
public:
    SpawnFileActions() {
        const int rc = ::posix_spawn_file_actions_init(&actions_);
        if (rc != 0) throw_error_code(rc, "posix_spawn_file_actions_init");
        initialized_ = true;
    }
    SpawnFileActions(const SpawnFileActions&) = delete;
    SpawnFileActions& operator=(const SpawnFileActions&) = delete;
    ~SpawnFileActions() {
        if (initialized_) (void)::posix_spawn_file_actions_destroy(&actions_);
    }

    void add_dup2(int source, int destination) {
        const int rc =
            ::posix_spawn_file_actions_adddup2(&actions_, source, destination);
        if (rc != 0) {
            throw_error_code(rc, "posix_spawn_file_actions_adddup2");
        }
    }

    void add_close_from(int first_descriptor) {
        const int rc =
            ::posix_spawn_file_actions_addclosefrom_np(&actions_, first_descriptor);
        if (rc != 0) {
            throw_error_code(rc,
                             "posix_spawn_file_actions_addclosefrom_np");
        }
    }

    [[nodiscard]] const posix_spawn_file_actions_t* get() const noexcept {
        return &actions_;
    }

private:
    posix_spawn_file_actions_t actions_{};
    bool initialized_ = false;
};

class SpawnAttributes final {
public:
    SpawnAttributes() {
        int rc = ::posix_spawnattr_init(&attributes_);
        if (rc != 0) throw_error_code(rc, "posix_spawnattr_init");
        initialized_ = true;

        sigset_t empty_mask{};
        if (::sigemptyset(&empty_mask) != 0) throw_errno("sigemptyset");
        rc = ::posix_spawnattr_setsigmask(&attributes_, &empty_mask);
        if (rc != 0) throw_error_code(rc, "posix_spawnattr_setsigmask");

        sigset_t defaults{};
        if (::sigfillset(&defaults) != 0) throw_errno("sigfillset");
        if (::sigdelset(&defaults, SIGKILL) != 0 ||
            ::sigdelset(&defaults, SIGSTOP) != 0) {
            throw_errno("sigdelset");
        }
        rc = ::posix_spawnattr_setsigdefault(&attributes_, &defaults);
        if (rc != 0) throw_error_code(rc, "posix_spawnattr_setsigdefault");

        rc = ::posix_spawnattr_setpgroup(&attributes_, 0);
        if (rc != 0) throw_error_code(rc, "posix_spawnattr_setpgroup");

        constexpr short flags = POSIX_SPAWN_SETSIGMASK |
                                POSIX_SPAWN_SETSIGDEF |
                                POSIX_SPAWN_SETPGROUP;
        rc = ::posix_spawnattr_setflags(&attributes_, flags);
        if (rc != 0) throw_error_code(rc, "posix_spawnattr_setflags");
    }
    SpawnAttributes(const SpawnAttributes&) = delete;
    SpawnAttributes& operator=(const SpawnAttributes&) = delete;
    ~SpawnAttributes() {
        if (initialized_) (void)::posix_spawnattr_destroy(&attributes_);
    }

    [[nodiscard]] const posix_spawnattr_t* get() const noexcept {
        return &attributes_;
    }

private:
    posix_spawnattr_t attributes_{};
    bool initialized_ = false;
};

[[nodiscard]] std::optional<int> parse_descriptor_name(
    std::string_view name) noexcept {
    if (name.empty()) return std::nullopt;
    int value = -1;
    const auto result =
        std::from_chars(name.data(), name.data() + name.size(), value);
    if (result.ec != std::errc{} ||
        result.ptr != name.data() + name.size() || value < 0) {
        return std::nullopt;
    }
    return value;
}

[[nodiscard]] std::vector<int> open_nonstandard_descriptors_or_throw() {
    DIR* raw_directory = ::opendir("/proc/self/fd");
    if (raw_directory == nullptr) throw_errno("opendir(/proc/self/fd)");

    struct DirectoryCloser final {
        void operator()(DIR* directory) const noexcept {
            if (directory != nullptr) (void)::closedir(directory);
        }
    };
    std::unique_ptr<DIR, DirectoryCloser> directory(raw_directory);
    const int scan_descriptor = ::dirfd(directory.get());
    if (scan_descriptor < 0) throw_errno("dirfd(/proc/self/fd)");

    std::vector<int> descriptors;
    errno = 0;
    while (dirent* entry = ::readdir(directory.get())) {
        const auto parsed = parse_descriptor_name(entry->d_name);
        if (parsed.has_value() && *parsed >= 3 &&
            *parsed != scan_descriptor) {
            descriptors.push_back(*parsed);
        }
        errno = 0;
    }
    if (errno != 0) throw_errno("readdir(/proc/self/fd)");

    std::sort(descriptors.begin(), descriptors.end());
    descriptors.erase(
        std::unique(descriptors.begin(), descriptors.end()),
        descriptors.end());
    return descriptors;
}

[[nodiscard]] ScopedDescriptor make_non_cloexec_sentinel_or_throw() {
    int descriptor = ::open("/dev/null", O_RDONLY);
    if (descriptor < 0) throw_errno("open(/dev/null)");
    if (descriptor < 3) {
        const int replacement = ::fcntl(descriptor, F_DUPFD, 3);
        const int saved_errno = errno;
        (void)::close(descriptor);
        errno = saved_errno;
        if (replacement < 0) throw_errno("fcntl(F_DUPFD)");
        descriptor = replacement;
    }
    if (::fcntl(descriptor, F_SETFD, 0) != 0) {
        const int saved_errno = errno;
        (void)::close(descriptor);
        errno = saved_errno;
        throw_errno("fcntl(F_SETFD)");
    }
    return ScopedDescriptor(descriptor);
}

[[nodiscard]] ScopedDescriptor promote_for_spawn_action_or_throw(
    ScopedDescriptor descriptor,
    std::string_view label) {
    if (descriptor.get() >= kFirstSanitizedDescriptor) {
        return descriptor;
    }
    const int replacement = ::fcntl(descriptor.get(), F_DUPFD_CLOEXEC,
                                    kFirstSanitizedDescriptor);
    if (replacement < 0) {
        throw_errno(std::string(label) + " fcntl(F_DUPFD_CLOEXEC)");
    }
    return ScopedDescriptor(replacement);
}

[[nodiscard]] CapturePipe make_capture_pipe_or_throw(
    std::string_view label) {
    int raw_descriptors[2] = {-1, -1};
    if (::pipe2(raw_descriptors, O_CLOEXEC) != 0) {
        throw_errno(std::string(label) + " pipe2");
    }

    CapturePipe pipe{ScopedDescriptor(raw_descriptors[0]),
                     ScopedDescriptor(raw_descriptors[1])};
    pipe.read_end = promote_for_spawn_action_or_throw(
        std::move(pipe.read_end), std::string(label) + " read end");
    pipe.write_end = promote_for_spawn_action_or_throw(
        std::move(pipe.write_end), std::string(label) + " write end");

    const int flags = ::fcntl(pipe.read_end.get(), F_GETFL);
    if (flags < 0) {
        throw_errno(std::string(label) + " read fcntl(F_GETFL)");
    }
    if (::fcntl(pipe.read_end.get(), F_SETFL, flags | O_NONBLOCK) != 0) {
        throw_errno(std::string(label) + " read fcntl(F_SETFL O_NONBLOCK)");
    }
    return pipe;
}

[[nodiscard]] bool same_file_identity(const struct stat& left,
                                      const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

[[nodiscard]] ScopedDescriptor pin_current_executable_or_throw(
    const fs::path& canonical) {
    const std::string path = canonical.native();
    if (path.empty() || path.find('\0') != std::string::npos) {
        throw std::runtime_error(
            "self-exec helper executable path is empty or contains an embedded NUL");
    }

    int descriptor = ::open(path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) throw_errno("open pinned self-executable");
    ScopedDescriptor pinned(descriptor);
    if (descriptor < kFirstSanitizedDescriptor) {
        const int replacement =
            ::fcntl(descriptor, F_DUPFD_CLOEXEC, kFirstSanitizedDescriptor);
        if (replacement < 0) throw_errno("fcntl(F_DUPFD_CLOEXEC) executable");
        pinned = ScopedDescriptor(replacement);
        descriptor = replacement;
    }

    struct stat pinned_status {};
    struct stat running_status {};
    if (::fstat(descriptor, &pinned_status) != 0) {
        throw_errno("fstat pinned self-executable");
    }
    if (::stat("/proc/self/exe", &running_status) != 0) {
        throw_errno("stat(/proc/self/exe)");
    }
    if (!S_ISREG(pinned_status.st_mode) ||
        (pinned_status.st_mode & 0111) == 0 ||
        !same_file_identity(pinned_status, running_status)) {
        throw std::runtime_error(
            "self-exec helper executable is not the exact running image object");
    }
    return pinned;
}

[[nodiscard]] bool is_allowed_environment_name(
    std::string_view name) noexcept {
    if (name == "LC_ALL" || name == "TZ") return true;
    return std::find(kPropagatedEnvironmentNames.begin(),
                     kPropagatedEnvironmentNames.end(), name) !=
           kPropagatedEnvironmentNames.end();
}

[[nodiscard]] std::vector<std::string> minimal_environment_or_throw() {
    std::vector<std::string> environment;
    environment.emplace_back("LC_ALL=C");
    environment.emplace_back("TZ=UTC");
    std::size_t total_bytes = environment[0].size() + environment[1].size() + 2;
    for (const std::string_view name : kPropagatedEnvironmentNames) {
        const std::string owned_name(name);
        const char* value = ::getenv(owned_name.c_str());
        if (value == nullptr) continue;
        std::string entry = owned_name + "=" + value;
        total_bytes += entry.size() + 1;
        if (total_bytes > kMaximumEnvironmentBytes) {
            throw std::runtime_error(
                "self-exec helper environment exceeds its byte budget");
        }
        environment.push_back(std::move(entry));
    }
    return environment;
}

void validate_arguments_or_throw(const std::vector<std::string>& arguments) {
    if (arguments.size() > kMaximumArgumentCount) {
        throw std::runtime_error(
            "self-exec helper argument count exceeds its budget");
    }
    std::size_t bytes = 0;
    for (const std::string& argument : arguments) {
        if (argument.size() > kMaximumSingleArgumentBytes) {
            throw std::runtime_error(
                "self-exec helper argument exceeds its byte budget");
        }
        if (argument.find('\0') != std::string::npos) {
            throw std::runtime_error(
                "self-exec helper argument contains an embedded NUL");
        }
        bytes += argument.size() + 1;
        if (bytes > kMaximumArgumentBytes) {
            throw std::runtime_error(
                "self-exec helper argv exceeds its byte budget");
        }
    }
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

void close_descriptor_noexcept(int& descriptor) noexcept {
    if (descriptor < 0) return;
    const int owned_descriptor = std::exchange(descriptor, -1);
    // As with ScopedDescriptor, close authority is consumed once. Retrying an
    // EINTR result can race descriptor reuse in another thread.
    (void)::close(owned_descriptor);
}

void drain_capture_descriptor_or_throw(int& descriptor,
                                       std::string& output,
                                       std::size_t maximum_bytes,
                                       std::string_view label,
                                       std::string_view stream_name) {
    if (descriptor < 0) return;
    std::array<char, 4096> buffer{};
    for (;;) {
        const ssize_t count = ::read(descriptor, buffer.data(), buffer.size());
        if (count > 0) {
            const std::size_t bytes = static_cast<std::size_t>(count);
            if (bytes > maximum_bytes - output.size()) {
                const std::size_t remaining = maximum_bytes - output.size();
                output.append(buffer.data(), remaining);
                throw std::runtime_error(
                    std::string(label) + " captured " +
                    std::string(stream_name) + " exceeded its " +
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
        throw_errno(std::string(label) + " read captured " +
                    std::string(stream_name));
    }
}

[[nodiscard]] std::string escaped_output_excerpt(std::string_view output) {
    constexpr std::size_t kMaximumExcerptBytes = 2048;
    constexpr char kHex[] = "0123456789abcdef";
    const std::size_t bytes = std::min(output.size(), kMaximumExcerptBytes);
    std::string rendered;
    rendered.reserve(bytes + 32);
    for (std::size_t index = 0; index < bytes; ++index) {
        const unsigned char byte =
            static_cast<unsigned char>(output[index]);
        switch (byte) {
            case '\n':
                rendered += "\\n";
                break;
            case '\r':
                rendered += "\\r";
                break;
            case '\t':
                rendered += "\\t";
                break;
            case '\\':
                rendered += "\\\\";
                break;
            default:
                if (byte >= 0x20U && byte <= 0x7eU) {
                    rendered.push_back(static_cast<char>(byte));
                } else {
                    rendered += "\\x";
                    rendered.push_back(kHex[(byte >> 4U) & 0x0fU]);
                    rendered.push_back(kHex[byte & 0x0fU]);
                }
                break;
        }
    }
    if (output.size() > bytes) rendered += "...";
    return rendered;
}

[[nodiscard]] std::string captured_output_context(
    const SelfExecTestProcessOutput& output) {
    return "; captured stdout bytes=" +
           std::to_string(output.standard_output.size()) + " [" +
           escaped_output_excerpt(output.standard_output) +
           "]; captured stderr bytes=" +
           std::to_string(output.standard_error.size()) + " [" +
           escaped_output_excerpt(output.standard_error) + "]";
}

}  // namespace

SelfExecTestProcess::SelfExecTestProcess(
    SelfExecTestProcess&& other) noexcept
    : topology_(std::move(other.topology_)),
      stdout_read_(std::exchange(other.stdout_read_, -1)),
      stderr_read_(std::exchange(other.stderr_read_, -1)) {}

SelfExecTestProcess& SelfExecTestProcess::operator=(
    SelfExecTestProcess&& other) noexcept {
    if (this != &other) {
        terminate_and_reap_noexcept();
        topology_ = std::move(other.topology_);
        stdout_read_ = std::exchange(other.stdout_read_, -1);
        stderr_read_ = std::exchange(other.stderr_read_, -1);
    }
    return *this;
}

SelfExecTestProcess::~SelfExecTestProcess() {
    terminate_and_reap_noexcept();
}

void SelfExecTestProcess::terminate_and_reap_noexcept() noexcept {
    topology_.terminate_and_reap_noexcept();
    close_output_capture_noexcept();
}

void SelfExecTestProcess::close_output_capture_noexcept() noexcept {
    close_descriptor_noexcept(stdout_read_);
    close_descriptor_noexcept(stderr_read_);
}

int SelfExecTestProcess::wait_for_exit_code(
    std::chrono::milliseconds timeout, std::string_view label) {
    if (topology_.leader_process_id() <= 0) {
        throw std::logic_error(
            "self-exec child has already been reaped or was never owned");
    }
    if (stdout_read_ >= 0 || stderr_read_ >= 0) {
        throw std::logic_error(
            "captured self-exec child requires wait_for_exact_exit_with_output");
    }
    if (timeout <= std::chrono::milliseconds::zero()) {
        throw std::invalid_argument("self-exec child timeout must be positive");
    }

    const auto deadline = std::chrono::steady_clock::now() + timeout;
    for (;;) {
        if (const std::optional<int> status =
                topology_.try_complete_exit_or_throw(label)) {
            if (!WIFEXITED(*status)) {
                throw std::runtime_error(
                    std::string(label) + " returned " +
                    child_status_text(*status) +
                    ", expected normal exit status");
            }
            return WEXITSTATUS(*status);
        }
        if (std::chrono::steady_clock::now() >= deadline) {
            topology_.terminate_and_reap_or_throw(
                std::string(label) + " timeout");
            throw std::runtime_error(std::string(label) +
                                     " timed out and was killed and reaped");
        }
        std::this_thread::sleep_for(5ms);
    }
}

void SelfExecTestProcess::wait_for_exact_exit(
    int expected_exit,
    std::chrono::milliseconds timeout,
    std::string_view label) {
    if (expected_exit < 0 || expected_exit > 255) {
        throw std::invalid_argument("expected child exit must fit in one byte");
    }
    const int observed_exit = wait_for_exit_code(timeout, label);
    if (observed_exit != expected_exit) {
        throw std::runtime_error(
            std::string(label) + " returned exit status " +
            std::to_string(observed_exit) + ", expected exit status " +
            std::to_string(expected_exit));
    }
}

SelfExecTestProcessOutput SelfExecTestProcess::wait_for_exact_exit_with_output(
    int expected_exit,
    std::chrono::milliseconds timeout,
    std::size_t maximum_bytes_per_stream,
    std::string_view label) {
    if (topology_.leader_process_id() <= 0) {
        throw std::logic_error(
            "self-exec child has already been reaped or was never owned");
    }
    if (stdout_read_ < 0 || stderr_read_ < 0) {
        throw std::logic_error(
            "self-exec child was not spawned with output capture");
    }
    if (expected_exit < 0 || expected_exit > 255) {
        throw std::invalid_argument("expected child exit must fit in one byte");
    }
    if (timeout <= std::chrono::milliseconds::zero()) {
        throw std::invalid_argument("self-exec child timeout must be positive");
    }
    if (maximum_bytes_per_stream == 0 ||
        maximum_bytes_per_stream > kMaximumCaptureBytesPerStream) {
        throw std::invalid_argument(
            "self-exec capture byte budget is zero or exceeds its hard limit");
    }

    const auto deadline = std::chrono::steady_clock::now() + timeout;
    SelfExecTestProcessOutput output;
    bool leader_completed = false;
    int status = 0;

    try {
        output.standard_output.reserve(
            std::min<std::size_t>(maximum_bytes_per_stream, 4096));
        output.standard_error.reserve(
            std::min<std::size_t>(maximum_bytes_per_stream, 4096));
        for (;;) {
            drain_capture_descriptor_or_throw(
                stdout_read_, output.standard_output,
                maximum_bytes_per_stream, label, "stdout");
            drain_capture_descriptor_or_throw(
                stderr_read_, output.standard_error,
                maximum_bytes_per_stream, label, "stderr");

            if (!leader_completed) {
                if (const std::optional<int> completed =
                        topology_.try_complete_exit_or_throw(label)) {
                    status = *completed;
                    leader_completed = true;
                }
            }

            if (leader_completed && stdout_read_ < 0 && stderr_read_ < 0) {
                break;
            }

            const auto now = std::chrono::steady_clock::now();
            if (now >= deadline) {
                throw std::runtime_error(
                    std::string(label) +
                    " timed out while draining captured output");
            }

            const auto remaining = std::chrono::duration_cast<
                std::chrono::milliseconds>(deadline - now);
            const auto bounded_wait =
                std::max(1ms, std::min(kCapturePollSlice, remaining));
            std::array<struct pollfd, 2> descriptors{{
                {stdout_read_, POLLIN, 0},
                {stderr_read_, POLLIN, 0},
            }};
            const int poll_result = ::poll(
                descriptors.data(), descriptors.size(),
                static_cast<int>(bounded_wait.count()));
            if (poll_result < 0 && errno != EINTR) {
                throw_errno(std::string(label) + " poll captured output");
            }
            if ((descriptors[0].revents & POLLNVAL) != 0 ||
                (descriptors[1].revents & POLLNVAL) != 0) {
                throw std::runtime_error(
                    std::string(label) +
                    " capture poll observed an invalid descriptor");
            }
        }
    } catch (...) {
        // The shared topology owner clears leader and process-group authority
        // together after the exact reap. A drain error after that transition
        // can close descriptors, but cannot signal a cached numeric group.
        topology_.terminate_and_reap_noexcept();
        close_output_capture_noexcept();
        throw;
    }

    if (!WIFEXITED(status) || WEXITSTATUS(status) != expected_exit) {
        throw std::runtime_error(
            std::string(label) + " returned " + child_status_text(status) +
            ", expected exit status " + std::to_string(expected_exit) +
            captured_output_context(output));
    }
    return output;
}

fs::path current_self_executable_or_throw() {
    std::array<char, 4096> buffer{};
    const ssize_t size =
        ::readlink("/proc/self/exe", buffer.data(), buffer.size());
    if (size < 0) throw_errno("readlink(/proc/self/exe)");
    if (static_cast<std::size_t>(size) == buffer.size()) {
        throw std::runtime_error("/proc/self/exe exceeded the path buffer");
    }
    const fs::path executable(
        std::string(buffer.data(), static_cast<std::size_t>(size)));
    std::error_code error;
    const fs::path canonical = fs::canonical(executable, error);
    if (error || !fs::is_regular_file(canonical, error) || error) {
        throw std::runtime_error(
            "current self-executable is not one canonical regular file");
    }
    return canonical;
}

namespace {

struct SpawnedSelfExecProcess final {
    pid_t child = -1;
    int stdout_read = -1;
    int stderr_read = -1;
};

[[nodiscard]] SpawnedSelfExecProcess
spawn_self_exec_test_process_components_or_throw(
    const fs::path& executable,
    const std::vector<std::string>& arguments,
    bool capture_output) {
    validate_arguments_or_throw(arguments);

    const std::string requested_path = executable.native();
    if (requested_path.empty() ||
        requested_path.find('\0') != std::string::npos) {
        throw std::runtime_error(
            "self-exec helper executable path is empty or contains an embedded NUL");
    }
    std::error_code error;
    const fs::path canonical = fs::canonical(executable, error);
    if (error || !fs::is_regular_file(canonical, error) || error ||
        !canonical.is_absolute()) {
        throw std::runtime_error(
            "self-exec helper executable is not one canonical regular file");
    }
    const std::string executable_string = canonical.native();
    ScopedDescriptor pinned_executable =
        pin_current_executable_or_throw(canonical);

    // This deliberately non-CLOEXEC descriptor makes sanitation executable
    // proof rather than an assertion about the parent's incidental descriptor
    // set. Every successful helper must close it through a spawn file action.
    ScopedDescriptor sentinel = make_non_cloexec_sentinel_or_throw();
    std::vector<int> descriptors = open_nonstandard_descriptors_or_throw();
    if (std::find(descriptors.begin(), descriptors.end(), sentinel.get()) ==
        descriptors.end()) {
        throw std::runtime_error(
            "self-exec sanitation sentinel was not observable before spawn");
    }

    std::optional<CapturePipe> stdout_pipe;
    std::optional<CapturePipe> stderr_pipe;
    if (capture_output) {
        stdout_pipe.emplace(make_capture_pipe_or_throw("self-exec stdout"));
        stderr_pipe.emplace(make_capture_pipe_or_throw("self-exec stderr"));
    }

    SpawnFileActions actions;
    // Descriptor 3 pins the exact running executable object. The child execs
    // through /proc/self/fd/3, proves that identity against /proc/self/exe, and
    // consumes the descriptor before any test state is opened. closefrom then
    // covers every unrelated descriptor, including concurrent parent opens.
    actions.add_dup2(pinned_executable.get(), kPinnedExecutableDescriptor);
    if (capture_output) {
        actions.add_dup2(stdout_pipe->write_end.get(), STDOUT_FILENO);
        actions.add_dup2(stderr_pipe->write_end.get(), STDERR_FILENO);
    }
    actions.add_close_from(kFirstSanitizedDescriptor);
    SpawnAttributes attributes;

    std::vector<std::string> owned_arguments;
    owned_arguments.reserve(arguments.size() + 1);
    owned_arguments.push_back(executable_string);
    owned_arguments.insert(owned_arguments.end(), arguments.begin(),
                           arguments.end());
    std::vector<char*> argv;
    argv.reserve(owned_arguments.size() + 1);
    for (std::string& argument : owned_arguments) {
        argv.push_back(argument.data());
    }
    argv.push_back(nullptr);

    std::vector<std::string> environment = minimal_environment_or_throw();
    std::vector<char*> envp;
    envp.reserve(environment.size() + 1);
    for (std::string& entry : environment) envp.push_back(entry.data());
    envp.push_back(nullptr);

    pid_t child = -1;
    const int rc = ::posix_spawn(
        &child, std::string(kPinnedExecutablePath).c_str(), actions.get(),
        attributes.get(), argv.data(), envp.data());
    if (rc != 0) throw_error_code(rc, "posix_spawn self-exec helper");
    if (child <= 0) {
        throw std::runtime_error("posix_spawn returned no owned child PID");
    }
    SpawnedSelfExecProcess result;
    result.child = child;
    if (capture_output) {
        result.stdout_read = stdout_pipe->read_end.release();
        result.stderr_read = stderr_pipe->read_end.release();
    }
    return result;
}

}  // namespace

SelfExecTestProcess spawn_self_exec_test_process_or_throw(
    const fs::path& executable,
    const std::vector<std::string>& arguments) {
    const SpawnedSelfExecProcess spawned =
        spawn_self_exec_test_process_components_or_throw(executable, arguments,
                                                         false);
    return SelfExecTestProcess(spawned.child);
}

SelfExecTestProcess spawn_self_exec_test_process_with_output_capture_or_throw(
    const fs::path& executable,
    const std::vector<std::string>& arguments) {
    const SpawnedSelfExecProcess spawned =
        spawn_self_exec_test_process_components_or_throw(executable, arguments,
                                                         true);
    return SelfExecTestProcess(spawned.child, spawned.stdout_read,
                               spawned.stderr_read);
}

void verify_self_exec_child_boundary_or_throw() {
    for (int descriptor = 0; descriptor <= 2; ++descriptor) {
        errno = 0;
        if (::fcntl(descriptor, F_GETFD) < 0) {
            throw std::runtime_error(
                "self-exec helper standard descriptor is not open: " +
                std::to_string(descriptor));
        }
    }

    struct stat pinned_status {};
    struct stat running_status {};
    if (::fstat(kPinnedExecutableDescriptor, &pinned_status) != 0 ||
        ::stat("/proc/self/exe", &running_status) != 0 ||
        !S_ISREG(pinned_status.st_mode) ||
        !same_file_identity(pinned_status, running_status)) {
        throw std::runtime_error(
            "self-exec helper running image does not match its pinned executable descriptor");
    }
    if (::close(kPinnedExecutableDescriptor) != 0) {
        throw_errno("close pinned self-executable descriptor");
    }

    if (::getpgrp() != ::getpid()) {
        throw std::runtime_error(
            "self-exec helper is not the leader of its isolated process group");
    }

    const std::vector<int> descriptors = open_nonstandard_descriptors_or_throw();
    if (!descriptors.empty()) {
        std::string rendered;
        for (const int descriptor : descriptors) {
            if (!rendered.empty()) rendered += ',';
            rendered += std::to_string(descriptor);
        }
        throw std::runtime_error(
            "self-exec helper inherited non-standard descriptors: " + rendered);
    }

    bool saw_locale = false;
    bool saw_timezone = false;
    for (char** cursor = environ; cursor != nullptr && *cursor != nullptr;
         ++cursor) {
        const std::string_view entry(*cursor);
        const std::size_t separator = entry.find('=');
        if (separator == std::string_view::npos) {
            throw std::runtime_error(
                "self-exec helper environment entry has no name/value boundary");
        }
        const std::string_view name = entry.substr(0, separator);
        const std::string_view value = entry.substr(separator + 1);
        if (!is_allowed_environment_name(name)) {
            throw std::runtime_error(
                "self-exec helper inherited a non-allowlisted environment name: " +
                std::string(name));
        }
        if (name == "LC_ALL") {
            if (saw_locale || value != "C") {
                throw std::runtime_error(
                    "self-exec helper locale evidence is duplicated or noncanonical");
            }
            saw_locale = true;
        } else if (name == "TZ") {
            if (saw_timezone || value != "UTC") {
                throw std::runtime_error(
                    "self-exec helper timezone evidence is duplicated or noncanonical");
            }
            saw_timezone = true;
        }
    }
    if (!saw_locale || !saw_timezone) {
        throw std::runtime_error(
            "self-exec helper did not receive its canonical locale/timezone environment");
    }

    struct sigaction user_signal_action {};
    if (::sigaction(SIGUSR1, nullptr, &user_signal_action) != 0) {
        throw_errno("sigaction inspect SIGUSR1");
    }
    if (user_signal_action.sa_handler != SIG_DFL) {
        throw std::runtime_error(
            "self-exec helper inherited a nondefault SIGUSR1 disposition");
    }

    sigset_t current_mask{};
    if (::sigprocmask(SIG_SETMASK, nullptr, &current_mask) != 0) {
        throw_errno("sigprocmask inspect");
    }
    for (int signal_number = 1; signal_number < NSIG; ++signal_number) {
        const int member = ::sigismember(&current_mask, signal_number);
        if (member < 0) throw_errno("sigismember");
        if (member == 1) {
            throw std::runtime_error(
                "self-exec helper inherited a blocked signal: " +
                std::to_string(signal_number));
        }
    }
}

}  // namespace anonsync::test
