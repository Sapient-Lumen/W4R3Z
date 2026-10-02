#include "iotox/terminal_posix.hpp"
#include "iotox/terminal_process.hpp"
#include "iotox/terminal_profile.hpp"
#include "iotox/terminal_seccomp_policy.hpp"
#include "iotox/sync_digest.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <chrono>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <linux/capability.h>
#include <linux/securebits.h>
#include <limits>
#include <optional>
#include <set>
#include <poll.h>
#include <pwd.h>
#include <spawn.h>
#include <sstream>
#include <span>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <thread>
#include <unistd.h>
#include <utility>
#include <vector>

extern char **environ;

namespace {

using namespace std::chrono_literals;
using iotox::ErrorCode;
using iotox::Status;
using iotox::terminal::CgroupAggregateLimits;
using iotox::terminal::CgroupPressureAdmissionLimits;
using iotox::terminal::CgroupResourceLimits;
using iotox::terminal::CloseReason;
using iotox::terminal::ConfinementMode;
using iotox::terminal::ControllerPhase;
using iotox::terminal::Dimensions;
using iotox::terminal::EnvironmentEntry;
using iotox::terminal::ExitKind;
using iotox::terminal::IoDisposition;
using iotox::terminal::IdentityMode;
using iotox::terminal::PosixPtyOptions;
using iotox::terminal::PosixPtyProcessFactory;
using iotox::terminal::PtyProcess;
using iotox::terminal::ResolvedProfile;
using iotox::terminal::TerminalController;
using iotox::terminal::kMaximumTerminalIoChunk;

constexpr int kSupervisorReportDescriptor = 3;
constexpr int kAmbientTestCapability = CAP_NET_BIND_SERVICE;

class FileDescriptor {
  public:
    FileDescriptor() = default;
    explicit FileDescriptor(int descriptor) : descriptor_(descriptor) {}
    ~FileDescriptor() {
        if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
    }
    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    FileDescriptor(FileDescriptor &&other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    FileDescriptor &operator=(FileDescriptor &&other) noexcept {
        if (this == &other) return *this;
        if (descriptor_ >= 0) static_cast<void>(::close(descriptor_));
        descriptor_ = std::exchange(other.descriptor_, -1);
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }

  private:
    int descriptor_{-1};
};

class ChildProcessGuard {
  public:
    explicit ChildProcessGuard(pid_t process) : process_(process) {}
    ~ChildProcessGuard() {
        if (process_ <= 0) return;
        static_cast<void>(::kill(process_, SIGKILL));
        int status = 0;
        while (::waitpid(process_, &status, 0) < 0 && errno == EINTR) {
        }
    }
    ChildProcessGuard(const ChildProcessGuard &) = delete;
    ChildProcessGuard &operator=(const ChildProcessGuard &) = delete;
    [[nodiscard]] pid_t get() const noexcept { return process_; }
    void release() noexcept { process_ = -1; }

  private:
    pid_t process_{-1};
};

class ProcessSignalGuard {
  public:
    explicit ProcessSignalGuard(pid_t process) : process_(process) {}
    ~ProcessSignalGuard() {
        if (process_ > 0) static_cast<void>(::kill(process_, SIGKILL));
    }
    ProcessSignalGuard(const ProcessSignalGuard &) = delete;
    ProcessSignalGuard &operator=(const ProcessSignalGuard &) = delete;
    void release() noexcept { process_ = -1; }

  private:
    pid_t process_{-1};
};

class SpawnFileActions {
  public:
    SpawnFileActions() : error_(::posix_spawn_file_actions_init(&actions_)) {}
    ~SpawnFileActions() {
        if (error_ == 0) {
            static_cast<void>(::posix_spawn_file_actions_destroy(&actions_));
        }
    }
    SpawnFileActions(const SpawnFileActions &) = delete;
    SpawnFileActions &operator=(const SpawnFileActions &) = delete;
    [[nodiscard]] int error() const noexcept { return error_; }
    [[nodiscard]] posix_spawn_file_actions_t *get() noexcept { return &actions_; }

  private:
    posix_spawn_file_actions_t actions_{};
    int error_{0};
};

void require(bool condition, std::string_view message) {
    if (!condition) throw std::runtime_error(std::string(message));
}

void require_ok(const Status &status, std::string_view context) {
    if (!status.ok()) {
        throw std::runtime_error(
            std::string(context) + ": " + status.message());
    }
}

[[nodiscard]] bool pidfd_open_is_available() {
#ifdef SYS_pidfd_open
    const int descriptor = static_cast<int>(
        ::syscall(SYS_pidfd_open, ::getpid(), 0U));
    if (descriptor < 0) return false;
    static_cast<void>(::close(descriptor));
    return true;
#else
    return false;
#endif
}

[[nodiscard]] std::size_t open_pidfd_count() {
    std::size_t count = 0U;
    std::error_code iteration_error;
    std::filesystem::directory_iterator iterator{
        "/proc/self/fd", iteration_error};
    const std::filesystem::directory_iterator end;
    while (!iteration_error && iterator != end) {
        std::error_code link_error;
        const std::filesystem::path target =
            std::filesystem::read_symlink(iterator->path(), link_error);
        if (!link_error && target == "anon_inode:[pidfd]") ++count;
        iterator.increment(iteration_error);
    }
    return count;
}

[[nodiscard]] std::string terminal_ioctl_count_report_line() {
    return "terminal-mutation-ioctl-count=" +
           std::to_string(
               iotox::terminal::detail::kDeniedTerminalIoctlRequests.size()) +
           "\n";
}

class TempDirectory {
  public:
    TempDirectory() {
        std::array<char, 64U> pattern{};
        const std::string value = "/tmp/iotox-terminal-posix-XXXXXX";
        std::copy(value.begin(), value.end(), pattern.begin());
        char *created = ::mkdtemp(pattern.data());
        if (created == nullptr) {
            throw std::runtime_error("mkdtemp failed");
        }
        path_ = created;
        if (::chmod(path_.c_str(), static_cast<mode_t>(0700)) != 0) {
            throw std::runtime_error("chmod temp directory failed");
        }
    }

    ~TempDirectory() { std::filesystem::remove_all(path_); }
    TempDirectory(const TempDirectory &) = delete;
    TempDirectory &operator=(const TempDirectory &) = delete;

    [[nodiscard]] const std::filesystem::path &path() const noexcept {
        return path_;
    }

  private:
    std::filesystem::path path_;
};

class ScopedIgnoredSignal {
  public:
    explicit ScopedIgnoredSignal(int signal_number) : signal_number_(signal_number) {
        struct sigaction ignored {};
        ignored.sa_handler = SIG_IGN;
        if (::sigemptyset(&ignored.sa_mask) != 0 ||
            ::sigaction(signal_number_, &ignored, &previous_) != 0) {
            throw std::runtime_error("failed to install ignored signal disposition");
        }
        installed_ = true;
    }

    ~ScopedIgnoredSignal() {
        if (installed_) {
            static_cast<void>(::sigaction(signal_number_, &previous_, nullptr));
        }
    }

    ScopedIgnoredSignal(const ScopedIgnoredSignal &) = delete;
    ScopedIgnoredSignal &operator=(const ScopedIgnoredSignal &) = delete;

  private:
    int signal_number_{0};
    struct sigaction previous_ {};
    bool installed_{false};
};

ResolvedProfile make_profile(
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory,
    std::string mode) {
    ResolvedProfile resolved;
    resolved.profile.id = "native-fixture";
    resolved.profile.enabled = true;
    resolved.profile.arguments = {fixture.string(), std::move(mode)};
    resolved.profile.working_directory = working_directory.string();
    resolved.profile.terminal_type = "xterm-256color";
    resolved.profile.environment = {EnvironmentEntry{"ALPHA", "sealed"}};
    resolved.profile.dimensions.minimum = Dimensions{20U, 5U};
    resolved.profile.dimensions.initial = Dimensions{91U, 33U};
    resolved.profile.dimensions.maximum = Dimensions{160U, 80U};
    resolved.profile.dimensions.allow_resize = true;
    resolved.profile.limits.cpu_seconds = 10U;
#if defined(IOTOX_TEST_LARGE_SHADOW_HELPER)
    // The test launches the sanitizer-instrumented iotox binary as the setup
    // helper. ASan and TSan reserve large virtual shadow mappings before
    // main(), so lowering RLIMIT_AS here would make later fail-closed setup
    // allocations abort before the child can emit its stage record.
    resolved.profile.limits.address_space_bytes = 0U;
#else
    resolved.profile.limits.address_space_bytes = 512U * 1024U * 1024U;
#endif
    resolved.profile.limits.file_size_bytes = 1024U * 1024U;
    resolved.profile.limits.open_files = 32U;
    // RLIMIT_NPROC is per real UID, not per PTY. The ordinary inherited-UID
    // fixture therefore leaves it disabled and exercises per-session process
    // accounting through the delegated-cgroup routes when those are available.
    resolved.profile.limits.processes = 0U;
    resolved.profile.hangup_grace = 20ms;
    resolved.profile.terminate_grace = 20ms;
    resolved.profile.kill_reap_grace = 500ms;
    resolved.environment = {
        EnvironmentEntry{"ALPHA", "sealed"},
        EnvironmentEntry{"TERM", "xterm-256color"},
    };
    resolved.accepted_dimensions = Dimensions{91U, 33U};
    resolved.policy_generation = 7U;
    return resolved;
}

std::string normalize_terminal_text(std::span<const std::uint8_t> bytes) {
    std::string text(
        reinterpret_cast<const char *>(bytes.data()), bytes.size());
    text.erase(std::remove(text.begin(), text.end(), '\r'), text.end());
    return text;
}

[[nodiscard]] std::string controller_phase_name(ControllerPhase phase) {
    switch (phase) {
        case ControllerPhase::running: return "running";
        case ControllerPhase::hangup_grace: return "hangup-grace";
        case ControllerPhase::terminate_grace: return "terminate-grace";
        case ControllerPhase::kill_reap_grace: return "kill-reap-grace";
        case ControllerPhase::exited: return "exited";
        case ControllerPhase::failed: return "failed";
    }
    return "unknown";
}

[[nodiscard]] std::string terminal_output_tail(
    std::span<const std::uint8_t> bytes, std::size_t limit = 2048U) {
    if (bytes.empty()) return {};
    const std::size_t offset = bytes.size() > limit ? bytes.size() - limit : 0U;
    std::string text(
        reinterpret_cast<const char *>(bytes.data() + offset),
        bytes.size() - offset);
    text.erase(std::remove(text.begin(), text.end(), '\r'), text.end());
    return text;
}

[[nodiscard]] bool write_all_descriptor(int descriptor, std::string_view text) {
    std::size_t offset = 0U;
    while (offset < text.size()) {
        const ssize_t count = ::write(
            descriptor, text.data() + offset, text.size() - offset);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return false;
    }
    return true;
}

[[nodiscard]] bool raise_test_ambient_capability() {
#if defined(SYS_capget) && defined(SYS_capset) && defined(PR_CAP_AMBIENT) && \
    defined(PR_CAP_AMBIENT_RAISE) && defined(PR_CAP_AMBIENT_IS_SET)
    __user_cap_header_struct header{};
    header.version = _LINUX_CAPABILITY_VERSION_3;
    header.pid = 0;
    std::array<__user_cap_data_struct, 2U> capabilities{};
    if (::syscall(SYS_capget, &header, capabilities.data()) != 0) return false;
    const std::size_t word =
        static_cast<std::size_t>(kAmbientTestCapability / 32);
    const std::uint32_t mask =
        std::uint32_t{1U} << static_cast<unsigned>(kAmbientTestCapability % 32);
    if (word >= capabilities.size() ||
        (capabilities[word].permitted & mask) == 0U) {
        return false;
    }
    capabilities[word].inheritable |= mask;
    if (::syscall(SYS_capset, &header, capabilities.data()) != 0) return false;
    if (::prctl(
            PR_CAP_AMBIENT, PR_CAP_AMBIENT_RAISE,
            kAmbientTestCapability, 0, 0) != 0) {
        return false;
    }
    return ::prctl(
               PR_CAP_AMBIENT, PR_CAP_AMBIENT_IS_SET,
               kAmbientTestCapability, 0, 0) == 1;
#else
    return false;
#endif
}

[[nodiscard]] pid_t parse_pid_record(
    std::string_view text, std::string_view label) {
    const std::string marker = std::string(label) + "=";
    const std::size_t marker_offset = text.find(marker);
    require(
        marker_offset != std::string_view::npos,
        "PTY fixture omitted its " + std::string(label));
    const std::size_t begin = marker_offset + marker.size();
    const std::size_t end = text.find('\n', begin);
    require(
        end != std::string_view::npos && end > begin,
        "PTY fixture emitted an invalid " + std::string(label) + " record");
    std::uint64_t parsed = 0U;
    const auto conversion = std::from_chars(
        text.data() + static_cast<std::ptrdiff_t>(begin),
        text.data() + static_cast<std::ptrdiff_t>(end), parsed);
    require(
        conversion.ec == std::errc{} &&
            conversion.ptr == text.data() + static_cast<std::ptrdiff_t>(end) &&
            parsed > 1U &&
            parsed <= static_cast<std::uint64_t>(
                std::numeric_limits<pid_t>::max()),
        "PTY fixture " + std::string(label) +
            " is outside the host pid range");
    return static_cast<pid_t>(parsed);
}

[[nodiscard]] pid_t parse_reported_pid(std::string_view text) {
    return parse_pid_record(text, "pid");
}

[[nodiscard]] std::string read_line_with_timeout(
    int descriptor, std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::string text;
    text.reserve(64U);
    while (std::chrono::steady_clock::now() < deadline && text.size() < 128U) {
        pollfd event{descriptor, static_cast<short>(POLLIN | POLLHUP), 0};
        const int ready = ::poll(&event, 1U, 50);
        if (ready < 0) {
            if (errno == EINTR) continue;
            throw std::runtime_error("poll supervisor report failed");
        }
        if (ready == 0) continue;
        if ((event.revents & static_cast<short>(POLLERR | POLLNVAL)) != 0) {
            throw std::runtime_error("supervisor report pipe failed");
        }
        std::array<char, 64U> buffer{};
        const ssize_t count = ::read(descriptor, buffer.data(), buffer.size());
        if (count > 0) {
            text.append(buffer.data(), static_cast<std::size_t>(count));
            const std::size_t newline = text.find('\n');
            if (newline != std::string::npos) {
                text.resize(newline + 1U);
                return text;
            }
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        if (count == 0) break;
        throw std::runtime_error("read supervisor report failed");
    }
    throw std::runtime_error("timed out waiting for parent-death supervisor");
}

[[nodiscard]] std::filesystem::path current_executable() {
    std::array<char, 4096U> path{};
    const ssize_t count = ::readlink(
        "/proc/self/exe", path.data(), path.size() - 1U);
    require(count > 0 && static_cast<std::size_t>(count) < path.size(),
            "read /proc/self/exe failed");
    path[static_cast<std::size_t>(count)] = '\0';
    return std::filesystem::path(path.data()).lexically_normal();
}

struct ProcIdentity {
    char state{'?'};
    std::uint64_t start_time{0U};
};

[[nodiscard]] std::optional<ProcIdentity> read_proc_identity(pid_t process) {
    std::ifstream input("/proc/" + std::to_string(process) + "/stat");
    if (!input) return std::nullopt;
    std::string line;
    std::getline(input, line);
    const std::size_t closing_name = line.rfind(')');
    if (closing_name == std::string::npos || closing_name + 2U >= line.size()) {
        return std::nullopt;
    }
    std::istringstream fields(line.substr(closing_name + 2U));
    std::vector<std::string> values;
    std::string value;
    while (fields >> value && values.size() <= 19U) {
        values.push_back(std::move(value));
    }
    if (values.size() <= 19U || values[0U].size() != 1U) return std::nullopt;
    std::uint64_t start_time = 0U;
    const auto converted = std::from_chars(
        values[19U].data(), values[19U].data() + values[19U].size(), start_time);
    if (converted.ec != std::errc{} ||
        converted.ptr != values[19U].data() + values[19U].size()) {
        return std::nullopt;
    }
    return ProcIdentity{values[0U][0U], start_time};
}

[[nodiscard]] bool wait_for_target_exit(
    int pid_descriptor, pid_t target, const ProcIdentity &initial,
    std::chrono::milliseconds timeout) {
    if (pid_descriptor >= 0) {
        pollfd event{pid_descriptor, POLLIN, 0};
        const auto deadline = std::chrono::steady_clock::now() + timeout;
        while (std::chrono::steady_clock::now() < deadline) {
            const int ready = ::poll(&event, 1U, 50);
            if (ready > 0) {
                return (event.revents & static_cast<short>(POLLIN | POLLHUP)) != 0;
            }
            if (ready < 0 && errno != EINTR) return false;
        }
        return false;
    }

    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (std::chrono::steady_clock::now() < deadline) {
        const auto current = read_proc_identity(target);
        if (!current.has_value() || current->start_time != initial.start_time ||
            current->state == 'Z' || current->state == 'X') {
            return true;
        }
        std::this_thread::sleep_for(5ms);
    }
    return false;
}

[[nodiscard]] bool wait_for_process_state(
    pid_t process, char expected, std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    while (std::chrono::steady_clock::now() < deadline) {
        const auto identity = read_proc_identity(process);
        if (identity && identity->state == expected) return true;
        std::this_thread::sleep_for(1ms);
    }
    return false;
}

[[nodiscard]] std::vector<std::uint8_t> collect_process_until(
    PtyProcess &process, std::string_view marker,
    std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::vector<std::uint8_t> bytes;
    while (std::chrono::steady_clock::now() < deadline) {
        auto read = process.read(4096U);
        require(read.ok(), read.status().message());
        if (read.value().disposition == IoDisposition::progress) {
            bytes.insert(
                bytes.end(), read.value().bytes.begin(), read.value().bytes.end());
            const std::string text = normalize_terminal_text(bytes);
            if (text.find(marker) != std::string::npos) return bytes;
        } else {
            std::this_thread::sleep_for(1ms);
        }
    }
    throw std::runtime_error("timed out collecting direct PTY process output");
}

std::vector<std::uint8_t> collect_until(
    TerminalController &controller, std::string_view marker,
    std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::vector<std::uint8_t> output;
    while (std::chrono::steady_clock::now() < deadline) {
        auto read = controller.read_output(4096U);
        require(read.ok(), read.status().message());
        if (read.value().disposition == IoDisposition::progress) {
            output.insert(
                output.end(), read.value().bytes.begin(), read.value().bytes.end());
            const std::string text = normalize_terminal_text(output);
            if (text.find(marker) != std::string::npos) return output;
        }
        require_ok(controller.poll(std::chrono::steady_clock::now()), "poll PTY");
        std::this_thread::sleep_for(1ms);
    }
    throw std::runtime_error("timed out collecting PTY marker");
}

std::pair<std::vector<std::uint8_t>, iotox::terminal::ControllerSnapshot>
collect_to_exit(TerminalController &controller, std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::vector<std::uint8_t> output;
    while (std::chrono::steady_clock::now() < deadline) {
        auto read = controller.read_output(4096U);
        require(read.ok(), read.status().message());
        if (read.value().disposition == IoDisposition::progress) {
            output.insert(
                output.end(), read.value().bytes.begin(), read.value().bytes.end());
        }
        require_ok(controller.poll(std::chrono::steady_clock::now()), "poll PTY");
        const auto snapshot = controller.snapshot();
        if (snapshot.phase == ControllerPhase::exited && snapshot.output_closed) {
            return {std::move(output), snapshot};
        }
        std::this_thread::sleep_for(1ms);
    }
    const auto snapshot = controller.snapshot();
    throw std::runtime_error(
        "timed out waiting for PTY exit; phase=" +
        controller_phase_name(snapshot.phase) +
        " output-closed=" + std::string(snapshot.output_closed ? "1" : "0") +
        " output-tail=\n" + terminal_output_tail(output));
}

void write_controller_text(
    TerminalController &controller, std::string_view text,
    std::chrono::milliseconds timeout) {
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::size_t offset = 0U;
    while (offset < text.size() && std::chrono::steady_clock::now() < deadline) {
        auto written = controller.write_input(
            std::span<const std::uint8_t>{
                reinterpret_cast<const std::uint8_t *>(text.data()),
                text.size()}.subspan(offset));
        require(written.ok(), written.status().message());
        if (written.value().disposition == IoDisposition::progress) {
            offset += written.value().bytes;
        } else {
            require_ok(controller.poll(std::chrono::steady_clock::now()),
                       "poll PTY input");
            std::this_thread::sleep_for(1ms);
        }
    }
    require(offset == text.size(), "timed out writing PTY text");
}

[[nodiscard]] int run_parent_death_supervisor(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    const int report_flags = ::fcntl(kSupervisorReportDescriptor, F_GETFD);
    require(report_flags >= 0, "parent-death supervisor report fd is absent");
    require(
        ::fcntl(
            kSupervisorReportDescriptor, F_SETFD,
            report_flags | FD_CLOEXEC) == 0,
        "parent-death supervisor could not seal its report fd");

    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto profile = make_profile(
        fixture, ::geteuid() == 0 ? std::filesystem::path{"/"}
                                  : working_directory,
        "hold");
    if (::geteuid() == 0) {
        profile.profile.identity.mode = IdentityMode::exact;
        profile.profile.identity.uid = 65'534U;
        profile.profile.identity.gid = 65'534U;
        profile.profile.identity.clear_supplementary_groups = true;
        profile.profile.limits.processes = 0U;
    }
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    const auto output = collect_until(*controller.value(), "READY\n", 3000ms);
    const pid_t target = parse_reported_pid(normalize_terminal_text(output));
    const std::string report = "pid=" + std::to_string(target) + "\n";
    require(
        write_all_descriptor(kSupervisorReportDescriptor, report),
        "parent-death supervisor could not report the target pid");
    while (true) {
        errno = 0;
        if (::pause() < 0 && errno == EINTR) continue;
        return 70;
    }
}

[[nodiscard]] int run_ambient_capability_supervisor(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    if (::geteuid() != 0 || !raise_test_ambient_capability()) return 77;
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(
        factory, make_profile(fixture, working_directory, "report"));
    require(controller.ok(), controller.status().message());
    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::array required{
        std::string{"ambient-capabilities=0\n"},
        std::string{"effective-capabilities=0\n"},
        std::string{"permitted-capabilities=0\n"},
        std::string{"inheritable-capabilities=0\n"},
        std::string{"bounding-capabilities=0\n"},
        std::string{"securebits-sealed=1\n"},
        std::string{"seccomp-mode=2\n"},
        std::string{"baseline-syscall-denied=1\n"},
        std::string{"process-handle-syscalls-denied=1\n"},
        std::string{"terminal-injection-ioctl-denied=1\n"},
        std::string{"terminal-mutation-ioctl-set-denied=1\n"},
        terminal_ioctl_count_report_line(),
        std::string{"ordinary-ioctl-kernel-validation=1\n"},
        std::string{"namespace-clone-argument-denied=1\n"},
        std::string{"ordinary-clone-kernel-validation=1\n"},
        std::string{"clone3-legacy-fallback=1\n"},
        std::string{"thread-clone-fallback-operational=1\n"},
    };
    for (const std::string &needle : required) {
        require(
            text.find(needle) != std::string::npos,
            "PTY target did not preserve its sealed capability boundary: " +
                needle);
    }
    require(snapshot.exit.has_value(), "ambient-capability exit missing");
    require(
        snapshot.exit->kind == ExitKind::exited && snapshot.exit->value == 0,
        "ambient-capability fixture did not exit normally");
    return 0;
}

void test_inherited_ambient_capabilities_are_cleared(
    const std::filesystem::path &self,
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    if (::geteuid() != 0) return;
    std::array<std::string, 5U> argument_storage{
        self.string(), "--ambient-capability-supervisor", iotox.string(),
        fixture.string(), working_directory.string()};
    std::array<char *, 6U> arguments{
        argument_storage[0U].data(), argument_storage[1U].data(),
        argument_storage[2U].data(), argument_storage[3U].data(),
        argument_storage[4U].data(), nullptr};
    pid_t supervisor = -1;
    const int spawned = ::posix_spawn(
        &supervisor, self.c_str(), nullptr, nullptr, arguments.data(), environ);
    require(spawned == 0 && supervisor > 1,
            "spawn ambient-capability supervisor failed");
    ChildProcessGuard supervisor_guard(supervisor);
    int status = 0;
    pid_t waited = -1;
    do {
        waited = ::waitpid(supervisor, &status, 0);
    } while (waited < 0 && errno == EINTR);
    require(waited == supervisor, "reap ambient-capability supervisor failed");
    supervisor_guard.release();
    require(WIFEXITED(status), "ambient-capability supervisor was signaled");
    if (WEXITSTATUS(status) == 77) return;
    require(WEXITSTATUS(status) == 0,
            "ambient-capability inheritance test failed");
}

void test_parent_death_contract_is_effective(
    const std::filesystem::path &self,
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    int report_pipe[2]{-1, -1};
    require(
        ::pipe2(report_pipe, O_CLOEXEC) == 0,
        "create parent-death supervisor pipe failed");
    FileDescriptor report_read(report_pipe[0]);
    FileDescriptor report_write(report_pipe[1]);
    FileDescriptor spawn_report_source(
        ::fcntl(report_write.get(), F_DUPFD_CLOEXEC, 64));
    require(
        spawn_report_source.get() >= 0,
        "duplicate parent-death report source failed");

    SpawnFileActions actions;
    require(actions.error() == 0, "initialize parent-death spawn actions failed");
    require(
        ::posix_spawn_file_actions_adddup2(
            actions.get(), spawn_report_source.get(),
            kSupervisorReportDescriptor) == 0,
        "map parent-death report descriptor failed");
    require(
        ::posix_spawn_file_actions_addclose(
            actions.get(), spawn_report_source.get()) == 0,
        "close parent-death report source in supervisor failed");
    if (report_read.get() != kSupervisorReportDescriptor) {
        require(
            ::posix_spawn_file_actions_addclose(
                actions.get(), report_read.get()) == 0,
            "close parent-death report reader in supervisor failed");
    }
    if (report_write.get() != kSupervisorReportDescriptor) {
        require(
            ::posix_spawn_file_actions_addclose(
                actions.get(), report_write.get()) == 0,
            "close duplicate parent-death writer in supervisor failed");
    }

    std::array<std::string, 5U> argument_storage{
        self.string(), "--parent-death-supervisor", iotox.string(),
        fixture.string(), working_directory.string()};
    std::array<char *, 6U> arguments{
        argument_storage[0U].data(), argument_storage[1U].data(),
        argument_storage[2U].data(), argument_storage[3U].data(),
        argument_storage[4U].data(), nullptr};
    pid_t supervisor = -1;
    const int spawned = ::posix_spawn(
        &supervisor, self.c_str(), actions.get(), nullptr,
        arguments.data(), environ);
    require(spawned == 0 && supervisor > 1,
            "spawn parent-death supervisor failed");
    ChildProcessGuard supervisor_guard(supervisor);
    report_write = FileDescriptor{};
    spawn_report_source = FileDescriptor{};

    const std::string report = read_line_with_timeout(report_read.get(), 5000ms);
    report_read = FileDescriptor{};
    const pid_t target = parse_reported_pid(report);
    ProcessSignalGuard target_guard(target);
    require(::kill(target, 0) == 0,
            "parent-death target exited before its supervisor");
    const auto initial_identity = read_proc_identity(target);
    require(initial_identity.has_value(),
            "could not identify the parent-death target in procfs");

    FileDescriptor target_pidfd;
#ifdef SYS_pidfd_open
    const int opened_pidfd = static_cast<int>(
        ::syscall(SYS_pidfd_open, target, 0U));
    if (opened_pidfd >= 0) target_pidfd = FileDescriptor(opened_pidfd);
#endif

    require(::kill(supervisor, SIGKILL) == 0,
            "kill parent-death supervisor failed");
    int supervisor_status = 0;
    pid_t waited = -1;
    do {
        waited = ::waitpid(supervisor, &supervisor_status, 0);
    } while (waited < 0 && errno == EINTR);
    require(waited == supervisor, "reap parent-death supervisor failed");
    supervisor_guard.release();
    require(
        WIFSIGNALED(supervisor_status) &&
            WTERMSIG(supervisor_status) == SIGKILL,
        "parent-death supervisor did not terminate by SIGKILL");

    require(
        wait_for_target_exit(
            target_pidfd.get(), target, *initial_identity, 3000ms),
        "target survived death of its verified PTY parent");
    target_guard.release();
}

void test_report(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    ScopedIgnoredSignal ignored_pipe(SIGPIPE);
    ScopedIgnoredSignal ignored_file_size(SIGXFSZ);
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(
        factory, make_profile(fixture, working_directory, "report"));
    require(controller.ok(), controller.status().message());
    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::array required{
        std::string{"cwd="} + working_directory.string() + "\n",
        std::string{"TERM=xterm-256color\n"},
        std::string{"ALPHA=sealed\n"},
        std::string{"PATH=<unset>\n"},
        std::string{"LD_PRELOAD=<unset>\n"},
        std::string{"IOTOX_INTERNAL_TERMINAL_CHILD=<unset>\n"},
        std::string{"winsize=91x33\n"},
        std::string{"no-new-privs=1\n"},
        std::string{"ambient-capabilities=0\n"},
        std::string{"effective-capabilities=0\n"},
        std::string{"permitted-capabilities=0\n"},
        std::string{"inheritable-capabilities=0\n"},
        std::string{"seccomp-mode=2\n"},
        std::string{"baseline-syscall-denied=1\n"},
        std::string{"terminal-injection-ioctl-denied=1\n"},
        std::string{"terminal-mutation-ioctl-set-denied=1\n"},
        terminal_ioctl_count_report_line(),
        std::string{"ordinary-ioctl-kernel-validation=1\n"},
        std::string{"namespace-clone-argument-denied=1\n"},
        std::string{"ordinary-clone-kernel-validation=1\n"},
        std::string{"clone3-legacy-fallback=1\n"},
        std::string{"thread-clone-fallback-operational=1\n"},
        std::string{"parent-death-signal="} + std::to_string(SIGKILL) + "\n",
        std::string{"signal-pipe=default\n"},
        std::string{"signal-xfsz=default\n"},
        std::string{"uid="} +
            std::to_string(static_cast<std::uint64_t>(::getuid())) + "\n",
        std::string{"euid="} +
            std::to_string(static_cast<std::uint64_t>(::geteuid())) + "\n",
        std::string{"gid="} +
            std::to_string(static_cast<std::uint64_t>(::getgid())) + "\n",
        std::string{"egid="} +
            std::to_string(static_cast<std::uint64_t>(::getegid())) + "\n",
        std::string{"core-soft=0\n"},
        std::string{"core-hard=0\n"},
        std::string{"nofile-soft=32\n"},
        std::string{"sid-equals-pid=1\n"},
        std::string{"pgrp-equals-pid=1\n"},
        std::string{"foreground=1\n"},
    };
    for (const std::string &needle : required) {
        require(text.find(needle) != std::string::npos, needle);
    }
    if (::geteuid() == 0) {
        require(
            text.find("bounding-capabilities=0\n") != std::string::npos,
            "privileged PTY target retained a capability in its bounding set");
        require(
            text.find("securebits-sealed=1\n") != std::string::npos,
            "privileged PTY target did not lock securebits");
    }
    for (int descriptor = 3; descriptor <= 16; ++descriptor) {
        const std::string needle =
            "fd" + std::to_string(descriptor) + "=closed\n";
        require(text.find(needle) != std::string::npos, needle);
    }
    require(snapshot.exit.has_value(), "report exit missing");
    require(snapshot.exit->kind == ExitKind::exited, "report did not exit normally");
    require(snapshot.exit->value == 0, "report returned nonzero");
    require(!snapshot.exit->core_dumped, "report claimed a core dump");
}

void test_explicit_privilege_escalation_boundary(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto profile = make_profile(
        fixture, ::geteuid() == 0 ? std::filesystem::path{"/"}
                                  : working_directory,
        "report");
    profile.profile.confinement = ConfinementMode::compatibility;
    profile.profile.allow_privilege_escalation = true;
    if (::geteuid() == 0) {
        profile.profile.identity.mode = IdentityMode::exact;
        profile.profile.identity.uid = 65'534U;
        profile.profile.identity.gid = 65'534U;
        profile.profile.identity.clear_supplementary_groups = true;
    } else {
        profile.profile.identity.mode = IdentityMode::account;
        profile.profile.identity.uid = static_cast<std::uint32_t>(::geteuid());
        profile.profile.identity.gid = static_cast<std::uint32_t>(::getegid());
        profile.profile.identity.clear_supplementary_groups = false;
        const int group_count = ::getgroups(0, nullptr);
        require(group_count >= 0,
                "read account supplementary-group count failed");
        std::vector<gid_t> groups(static_cast<std::size_t>(group_count));
        require(
            group_count == 0 ||
                ::getgroups(group_count, groups.data()) == group_count,
            "read account supplementary groups failed");
        for (const gid_t group : groups) {
            if (group != ::getegid()) {
                profile.profile.identity.supplementary_groups.push_back(
                    static_cast<std::uint32_t>(group));
            }
        }
        std::sort(
            profile.profile.identity.supplementary_groups.begin(),
            profile.profile.identity.supplementary_groups.end());
    }
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::array required{
        std::string{"no-new-privs=0\n"},
        std::string{"ambient-capabilities=0\n"},
        std::string{"effective-capabilities=0\n"},
        std::string{"permitted-capabilities=0\n"},
        std::string{"inheritable-capabilities=0\n"},
        std::string{"securebits-sealed=0\n"},
        std::string{"uid="} +
            std::to_string(
                ::geteuid() == 0 ? 65'534U
                                  : static_cast<std::uint32_t>(::geteuid())) +
            "\n",
    };
    for (const std::string &needle : required) {
        require(text.find(needle) != std::string::npos, needle);
    }
    require(
        text.find("bounding-capabilities=0\n") == std::string::npos,
        "sudo-capable PTY target lost its capability bounding set");
    require(snapshot.exit.has_value(),
            "privilege-escalation report exit missing");
    require(snapshot.exit->kind == ExitKind::exited &&
                snapshot.exit->value == 0,
            "privilege-escalation report did not exit normally");
}

void qualify_real_sudo_from_non_root_account(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &sudo,
    const std::filesystem::path &id) {
    require(::geteuid() != 0,
            "sudo qualification must begin as a non-root account");
    struct stat sudo_metadata {};
    require(
        ::stat(sudo.c_str(), &sudo_metadata) == 0 &&
            S_ISREG(sudo_metadata.st_mode) &&
            sudo_metadata.st_uid == 0 &&
            (sudo_metadata.st_mode & S_ISUID) != 0,
        "sudo qualification requires one setuid-root sudo executable");

    auto profile = make_profile(fixture, "/tmp", "sudo-probe");
    profile.profile.arguments.push_back(sudo.string());
    profile.profile.arguments.push_back(id.string());
    profile.profile.confinement = ConfinementMode::compatibility;
    profile.profile.allow_privilege_escalation = true;
    profile.profile.identity.mode = IdentityMode::account;
    profile.profile.identity.uid = static_cast<std::uint32_t>(::geteuid());
    profile.profile.identity.gid = static_cast<std::uint32_t>(::getegid());
    profile.profile.identity.clear_supplementary_groups = false;
    const int group_count = ::getgroups(0, nullptr);
    require(group_count >= 0,
            "sudo qualification could not read supplementary-group count");
    std::vector<gid_t> groups(static_cast<std::size_t>(group_count));
    require(
        group_count == 0 ||
            ::getgroups(group_count, groups.data()) == group_count,
        "sudo qualification could not read supplementary groups");
    for (const gid_t group : groups) {
        if (group != ::getegid()) {
            profile.profile.identity.supplementary_groups.push_back(
                static_cast<std::uint32_t>(group));
        }
    }
    std::sort(
        profile.profile.identity.supplementary_groups.begin(),
        profile.profile.identity.supplementary_groups.end());

    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 5000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::string account =
        std::to_string(static_cast<std::uint32_t>(::geteuid()));
    require(
        text.find("pre-sudo-euid=" + account + "\n") !=
            std::string::npos,
        "sudo qualification did not start as the selected non-root account");
    require(text.find("\n0\n") != std::string::npos,
            "sudo qualification did not observe effective uid zero");
    require(
        text.find("sudo-exit=0 post-sudo-euid=" + account + "\n") !=
            std::string::npos,
        "sudo qualification did not return cleanly to the non-root shell");
    require(snapshot.exit.has_value() &&
                snapshot.exit->kind == ExitKind::exited &&
                snapshot.exit->value == 0,
            "sudo qualification fixture did not exit successfully");
}

void qualify_rescue_toolbox_through_shell(
    const std::filesystem::path &iotox,
    const std::filesystem::path &shell,
    const std::filesystem::path &toolbox) {
    require(::geteuid() != 0,
            "rescue-toolbox qualification must begin as a non-root account");
    passwd *account = ::getpwuid(::geteuid());
    require(
        account != nullptr && account->pw_name != nullptr,
        "rescue-toolbox qualification could not resolve its account");
    std::error_code canonical_error;
    const std::filesystem::path qualified_shell =
        std::filesystem::canonical(shell, canonical_error);
    require(!canonical_error && std::filesystem::is_regular_file(qualified_shell),
            "rescue-toolbox shell is not a regular file");
    require(std::filesystem::is_regular_file(toolbox / "toybox"),
            "rescue-toolbox multicall executable is missing");

    TempDirectory temporary;
    auto profile = make_profile(qualified_shell, temporary.path(), "-i");
    profile.profile.id = "rescue-toolbox";
    profile.profile.environment = {
        EnvironmentEntry{"HISTFILE", "/dev/null"},
        EnvironmentEntry{"HOME", temporary.path().string()},
        EnvironmentEntry{"IOTOX_RESCUE_TOOLBOX", toolbox.string()},
        EnvironmentEntry{"LOGNAME", account->pw_name},
        EnvironmentEntry{"PATH", toolbox.string()},
        EnvironmentEntry{"PS1", "iotox-rescue$ "},
        EnvironmentEntry{"SHELL", qualified_shell.string()},
        EnvironmentEntry{"USER", account->pw_name},
    };
    profile.environment = profile.profile.environment;
    profile.environment.push_back(
        EnvironmentEntry{"TERM", profile.profile.terminal_type});
    std::sort(
        profile.environment.begin(), profile.environment.end(),
        [](const EnvironmentEntry &left, const EnvironmentEntry &right) {
            return left.name < right.name;
        });
    profile.profile.confinement = ConfinementMode::baseline;
    profile.profile.allow_privilege_escalation = false;
    profile.profile.identity.mode = IdentityMode::account;
    profile.profile.identity.uid = static_cast<std::uint32_t>(::geteuid());
    profile.profile.identity.gid = static_cast<std::uint32_t>(::getegid());
    profile.profile.identity.clear_supplementary_groups = false;
    profile.profile.limits =
        iotox::terminal::ResourceLimits{0U, 0U, 0U, 0U, 0U};
    auto shell_digest =
        iotox::sync::hash_sync_file_sha256(qualified_shell);
    auto toolbox_digest =
        iotox::sync::hash_sync_file_sha256(toolbox / "toybox");
    require(shell_digest.ok(), shell_digest.status().message());
    require(toolbox_digest.ok(), toolbox_digest.status().message());
    profile.profile.executable_sha256 = shell_digest.value();
    profile.profile.toolbox_sha256 = toolbox_digest.value();
    const int group_count = ::getgroups(0, nullptr);
    require(group_count >= 0,
            "rescue-toolbox qualification could not read supplementary groups");
    std::vector<gid_t> groups(static_cast<std::size_t>(group_count));
    require(
        group_count == 0 ||
            ::getgroups(group_count, groups.data()) == group_count,
        "rescue-toolbox qualification could not freeze supplementary groups");
    for (const gid_t group : groups) {
        if (group != ::getegid()) {
            profile.profile.identity.supplementary_groups.push_back(
                static_cast<std::uint32_t>(group));
        }
    }
    std::sort(
        profile.profile.identity.supplementary_groups.begin(),
        profile.profile.identity.supplementary_groups.end());

    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    const std::string command =
        "printf 'RESCUE-SHELL:%s\\n' \"$KSH_VERSION\"\n"
        "printf 'TOYBOX-PATH:%s\\n' \"$(command -v toybox)\"\n"
        "printf 'ID-PATH:%s\\n' \"$(command -v id)\"\n"
        "id\n"
        "printf 'iotox-rescue\\n' > \"$HOME/payload\"\n"
        "sha256sum \"$HOME/payload\"\n"
        "ls -l \"$HOME/payload\"\n"
        "exit\n";
    write_controller_text(*controller.value(), command, 3000ms);
    auto [bytes, snapshot] =
        collect_to_exit(*controller.value(), 10000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::string toolbox_text = toolbox.string();
    const std::array required{
        std::string{"RESCUE-SHELL:"},
        std::string{"TOYBOX-PATH:"} + toolbox_text + "/toybox\n",
        std::string{"ID-PATH:"} + toolbox_text + "/id\n",
        std::string{"uid="} + std::to_string(::geteuid()),
        std::string{
            "e443f60d64346ce1302f936c996b96aebdcbe1adff9e8b25280c733f6187509d"},
        std::string{"payload\n"},
    };
    for (const std::string &needle : required) {
        require(
            text.find(needle) != std::string::npos,
            "rescue-toolbox PTY output omitted: " + needle + "\n" + text);
    }
    require(snapshot.exit.has_value() &&
                snapshot.exit->kind == ExitKind::exited &&
                snapshot.exit->value == 0,
            "rescue-toolbox shell did not exit successfully");
}

void qualify_password_sudo_through_login_shell(
    const std::filesystem::path &iotox,
    const std::filesystem::path &shell,
    const std::filesystem::path &sudo,
    const std::filesystem::path &id,
    std::string password) {
    require(::geteuid() != 0,
            "sudo shell qualification must begin as a non-root account");
    passwd *account = ::getpwuid(::geteuid());
    require(
        account != nullptr && account->pw_name != nullptr &&
            account->pw_dir != nullptr,
        "sudo shell qualification could not resolve its login account");
    const std::filesystem::path home = account->pw_dir;
    auto profile = make_profile(shell, home, "-l");
    profile.profile.id = "sudo-login-shell";
    profile.profile.environment = {
        EnvironmentEntry{"HOME", home.string()},
        EnvironmentEntry{"LOGNAME", account->pw_name},
        EnvironmentEntry{
            "PATH",
            "/run/wrappers/bin:/run/current-system/sw/bin:/usr/bin:/bin"},
        EnvironmentEntry{"SHELL", shell.string()},
        EnvironmentEntry{"USER", account->pw_name},
    };
    profile.environment = profile.profile.environment;
    profile.environment.push_back(
        EnvironmentEntry{"TERM", profile.profile.terminal_type});
    std::sort(
        profile.environment.begin(), profile.environment.end(),
        [](const EnvironmentEntry &left, const EnvironmentEntry &right) {
            return left.name < right.name;
        });
    profile.profile.confinement = ConfinementMode::compatibility;
    profile.profile.allow_privilege_escalation = true;
    profile.profile.identity.mode = IdentityMode::account;
    profile.profile.identity.uid = static_cast<std::uint32_t>(::geteuid());
    profile.profile.identity.gid = static_cast<std::uint32_t>(::getegid());
    profile.profile.identity.clear_supplementary_groups = false;
    profile.profile.limits =
        iotox::terminal::ResourceLimits{0U, 0U, 0U, 0U, 0U};
    const int group_count = ::getgroups(0, nullptr);
    require(group_count >= 0,
            "sudo shell qualification could not read supplementary groups");
    std::vector<gid_t> groups(static_cast<std::size_t>(group_count));
    require(
        group_count == 0 ||
            ::getgroups(group_count, groups.data()) == group_count,
        "sudo shell qualification could not freeze supplementary groups");
    for (const gid_t group : groups) {
        if (group != ::getegid()) {
            profile.profile.identity.supplementary_groups.push_back(
                static_cast<std::uint32_t>(group));
        }
    }
    std::sort(
        profile.profile.identity.supplementary_groups.begin(),
        profile.profile.identity.supplementary_groups.end());

    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    const std::string command =
        "PS1='IOTOX-SHELL-READY:'\n"
        "PROMPT_COMMAND=\n"
        "printf 'pre-shell-euid=%s\\n' \"$(" + id.string() +
        " -u)\"\n"
        "iotox_sudo_prompt='IOTOX-SUDO-'\n"
        "iotox_sudo_prompt=\"${iotox_sudo_prompt}PASSWORD:\"\n" +
        sudo.string() + " -k -p \"$iotox_sudo_prompt\" -- " + id.string() +
        " -u\n";
    write_controller_text(*controller.value(), command, 3000ms);
    std::vector<std::uint8_t> before_password = collect_until(
        *controller.value(), "IOTOX-SUDO-PASSWORD:", 5000ms);
    // Match a human response boundary. Sudo may emit its prompt while still
    // completing terminal-mode setup and flushing pre-prompt input; an
    // immediate same-timeslice write can race that flush.
    std::this_thread::sleep_for(100ms);
    write_controller_text(*controller.value(), password + "\n", 3000ms);
    std::vector<std::uint8_t> sudo_output = collect_until(
        *controller.value(), "\n0\n", 5000ms);
    // Match a human waiting for the shell to regain terminal control after
    // sudo restores termios and PAM closes its session. The following newline
    // also fences any unterminated prompt repaint before the status command.
    std::this_thread::sleep_for(250ms);
    const std::string continuation =
        "\nstatus=$?\nprintf 'sudo-exit=%s post-shell-euid=%s\\n' "
        "\"$status\" \"$(" + id.string() +
        " -u)\"\nexit \"$status\"\n";
    write_controller_text(*controller.value(), continuation, 3000ms);
    auto [after_password, snapshot] =
        collect_to_exit(*controller.value(), 10000ms);
    before_password.insert(
        before_password.end(), sudo_output.begin(), sudo_output.end());
    before_password.insert(
        before_password.end(), after_password.begin(), after_password.end());
    const std::string text = normalize_terminal_text(before_password);
    const std::string uid =
        std::to_string(static_cast<std::uint32_t>(::geteuid()));
    require(text.find("pre-shell-euid=" + uid + "\n") != std::string::npos,
            "login shell did not begin as the selected non-root account");
    require(text.find("\n0\n") != std::string::npos,
            "password-authorized sudo child did not become root");
    require(
        text.find("sudo-exit=0 post-shell-euid=" + uid + "\n") !=
            std::string::npos,
        "login shell did not return to its non-root account after sudo");
    require(text.find(password) == std::string::npos,
            "sudo password was echoed into terminal output");
    require(snapshot.exit.has_value() &&
                snapshot.exit->kind == ExitKind::exited &&
                snapshot.exit->value == 0,
            "sudo login shell did not exit successfully");
}

void test_baseline_lifecycle_fences(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(
        factory,
        make_profile(fixture, working_directory, "baseline-fence-probe"));
    require(controller.ok(), controller.status().message());
    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::array required{
        std::string{"ordinary-fork-allowed=1\n"},
        std::string{"ordinary-thread-allowed=1\n"},
        std::string{"namespace-clone-denied=1\n"},
        std::string{"clone3-unavailable=1\n"},
        std::string{"descendant-setsid-denied=1\n"},
        std::string{"terminal-detach-denied=1\n"},
        std::string{"parent-death-change-denied=1\n"},
        std::string{"process-handle-syscalls-denied=1\n"},
    };
    for (const std::string &needle : required) {
        require(text.find(needle) != std::string::npos, needle);
    }
    require(snapshot.exit.has_value(), "baseline fence probe exit missing");
    require(
        snapshot.exit->kind == ExitKind::exited && snapshot.exit->value == 0,
        "baseline fence probe did not exit normally");
}

void test_high_inherited_descriptor_is_closed(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    FileDescriptor source(::open("/dev/null", O_RDONLY | O_CLOEXEC));
    require(source.get() >= 0, "open descriptor source failed");
    FileDescriptor inherited(::fcntl(source.get(), F_DUPFD, 256));
    require(inherited.get() >= 256, "duplicate high inherited descriptor failed");

    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto profile = make_profile(fixture, working_directory, "fd-probe");
    profile.profile.arguments.push_back(std::to_string(inherited.get()));
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    require(
        text.find("inherited-high-fd-closed=1\n") != std::string::npos,
        "PTY target retained a high inherited descriptor");
    require(snapshot.exit.has_value(), "descriptor probe exit missing");
    require(
        snapshot.exit->kind == ExitKind::exited && snapshot.exit->value == 0,
        "descriptor probe did not exit normally");
}

void test_session_wide_shutdown_contains_separate_process_groups(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(
        factory, make_profile(fixture, working_directory, "session-tree"));
    require(controller.ok(), controller.status().message());
    const std::vector<std::uint8_t> bytes =
        collect_until(*controller.value(), "READY\n", 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    require(
        text.find("child-separate-pgrp=1\n") != std::string::npos,
        "session fixture did not create a separate descendant process group");
    const pid_t leader = parse_pid_record(text, "leader-pid");
    const pid_t child = parse_pid_record(text, "child-pid");
    require(leader != child, "session fixture reused the leader pid for its child");
    ProcessSignalGuard child_guard(child);
    const auto child_identity = read_proc_identity(child);
    require(child_identity.has_value(), "session descendant vanished before shutdown");

    FileDescriptor child_pidfd;
#ifdef SYS_pidfd_open
    const int opened_pidfd = static_cast<int>(::syscall(SYS_pidfd_open, child, 0U));
    if (opened_pidfd >= 0) child_pidfd = FileDescriptor(opened_pidfd);
#endif

    const auto start = std::chrono::steady_clock::now();
    require_ok(
        controller.value()->request_close(CloseReason::authority_revoked, start),
        "request session-wide close");
    require_ok(controller.value()->poll(start + 20ms), "send session TERM");
    require_ok(controller.value()->poll(start + 40ms), "send session KILL");

    const auto deadline = std::chrono::steady_clock::now() + 3000ms;
    while (std::chrono::steady_clock::now() < deadline) {
        require_ok(
            controller.value()->poll(start + 40ms),
            "reap session-wide shutdown");
        if (controller.value()->snapshot().phase == ControllerPhase::exited) break;
        std::this_thread::sleep_for(1ms);
    }
    const auto snapshot = controller.value()->snapshot();
    require(snapshot.phase == ControllerPhase::exited,
            "session-wide shutdown did not converge");
    require(snapshot.exit.has_value(), "session leader exit missing");
    require(
        snapshot.exit->kind == ExitKind::signaled &&
            snapshot.exit->value == SIGKILL,
        "session leader did not preserve forced SIGKILL status");
    require(
        wait_for_target_exit(
            child_pidfd.get(), child, *child_identity, 3000ms),
        "separate-process-group descendant survived session shutdown");
    child_guard.release();
}

void test_natural_leader_exit_reaps_remaining_session(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(
        factory, make_profile(fixture, working_directory, "session-orphan"));
    require(controller.ok(), controller.status().message());
    const std::vector<std::uint8_t> ready_bytes =
        collect_until(*controller.value(), "READY\n", 3000ms);
    const std::string ready_text = normalize_terminal_text(ready_bytes);
    require(
        ready_text.find("child-separate-pgrp=1\n") != std::string::npos,
        "orphan fixture did not create a separate descendant process group");
    const pid_t leader = parse_pid_record(ready_text, "leader-pid");
    const pid_t child = parse_pid_record(ready_text, "child-pid");
    require(leader != child, "orphan fixture reused the leader pid for its child");
    ProcessSignalGuard child_guard(child);
    const auto child_identity = read_proc_identity(child);
    require(child_identity.has_value(), "orphan descendant vanished before observation");

    FileDescriptor child_pidfd;
#ifdef SYS_pidfd_open
    const int opened_pidfd = static_cast<int>(::syscall(SYS_pidfd_open, child, 0U));
    if (opened_pidfd >= 0) child_pidfd = FileDescriptor(opened_pidfd);
#endif

    auto [remaining_bytes, snapshot] =
        collect_to_exit(*controller.value(), 3000ms);
    static_cast<void>(remaining_bytes);
    require(snapshot.exit.has_value(), "natural session leader exit missing");
    require(
        snapshot.exit->kind == ExitKind::exited && snapshot.exit->value == 0,
        "natural session leader status was not preserved");
    require(
        wait_for_target_exit(
            child_pidfd.get(), child, *child_identity, 3000ms),
        "orphan descendant survived natural leader exit");
    child_guard.release();
}

void test_reap_requires_repeated_quiescent_session_inventories(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto process = factory.spawn(
        make_profile(fixture, working_directory, "quiescence-probe"));
    require(process.ok(), process.status().message());
    const std::vector<std::uint8_t> ready =
        collect_process_until(*process.value(), "READY\n", 3000ms);
    const std::string text = normalize_terminal_text(ready);
    const pid_t leader = parse_pid_record(text, "leader-pid");

    const std::array<std::uint8_t, 1U> release{1U};
    auto written = process.value()->write(release);
    require(written.ok(), written.status().message());
    require(
        written.value().disposition == IoDisposition::progress &&
            written.value().bytes == release.size(),
        "quiescence probe release byte was not delivered");
    require(
        wait_for_process_state(leader, 'Z', 3000ms),
        "quiescence probe leader did not become waitable");

    auto first = process.value()->poll_exit();
    require(first.ok(), first.status().message());
    require(
        !first.value().has_value(),
        "PTY leader was reaped after only one empty session inventory");
    auto second = process.value()->poll_exit();
    require(second.ok(), second.status().message());
    require(
        !second.value().has_value(),
        "PTY leader was reaped before the third empty session inventory");
    auto third = process.value()->poll_exit();
    require(third.ok(), third.status().message());
    require(third.value().has_value(),
            "PTY leader was not reaped after repeated quiescent inventories");
    require(
        third.value()->kind == ExitKind::exited && third.value()->value == 0,
        "quiescence probe exit status changed");
    auto repeated = process.value()->poll_exit();
    require(repeated.ok() && repeated.value() == third.value(),
            "quiescence probe exit observation was not idempotent");
}

void test_session_shutdown_converges_during_bounded_fork_churn(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    const std::filesystem::path record_path =
        working_directory / "session-fork-churn.pids";
    std::error_code remove_error;
    std::filesystem::remove(record_path, remove_error);

    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto profile = make_profile(fixture, working_directory, "session-fork-churn");
    profile.profile.arguments.push_back(record_path.string());
    profile.profile.limits.processes = 0U;
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    const std::vector<std::uint8_t> ready =
        collect_until(*controller.value(), "READY\n", 3000ms);
    const std::string text = normalize_terminal_text(ready);
    const pid_t leader = parse_pid_record(text, "leader-pid");
    const pid_t churner = parse_pid_record(text, "churner-pid");
    require(leader != churner, "fork-churn fixture reused the leader pid");

    std::vector<std::pair<pid_t, ProcIdentity>> observed;
    std::set<pid_t> unique;
    const auto observation_deadline = std::chrono::steady_clock::now() + 250ms;
    while (std::chrono::steady_clock::now() < observation_deadline &&
           observed.size() < 6U) {
        std::ifstream records(record_path);
        std::uint64_t value = 0U;
        while (records >> value &&
               value <= static_cast<std::uint64_t>(
                            std::numeric_limits<pid_t>::max())) {
            const pid_t process = static_cast<pid_t>(value);
            if (process <= 1 || !unique.insert(process).second) continue;
            const auto identity = read_proc_identity(process);
            if (identity) {
                observed.emplace_back(process, *identity);
            } else {
                unique.erase(process);
            }
        }
        if (observed.size() < 6U) std::this_thread::sleep_for(1ms);
    }
    require(observed.size() >= 2U,
            "fork-churn fixture did not expose multiple live session members");

    const auto start = std::chrono::steady_clock::now();
    require_ok(
        controller.value()->request_close(CloseReason::authority_revoked, start),
        "request fork-churn close");
    std::this_thread::sleep_for(3ms);
    require_ok(controller.value()->poll(start + 20ms),
               "send fork-churn TERM");
    std::this_thread::sleep_for(3ms);
    require_ok(controller.value()->poll(start + 40ms),
               "send fork-churn KILL");

    const auto deadline = std::chrono::steady_clock::now() + 3000ms;
    while (std::chrono::steady_clock::now() < deadline) {
        require_ok(controller.value()->poll(start + 40ms),
                   "reap fork-churn session");
        if (controller.value()->snapshot().phase == ControllerPhase::exited) break;
        std::this_thread::sleep_for(1ms);
    }
    const auto snapshot = controller.value()->snapshot();
    require(snapshot.phase == ControllerPhase::exited,
            "fork-churn session shutdown did not converge");
    require(snapshot.exit.has_value(), "fork-churn leader exit missing");
    require(
        snapshot.exit->kind == ExitKind::signaled &&
            snapshot.exit->value == SIGKILL,
        "fork-churn leader did not preserve SIGKILL status");
    for (const auto &[process, identity] : observed) {
        require(
            wait_for_target_exit(-1, process, identity, 3000ms),
            "observed fork-churn descendant survived session shutdown");
    }
}

void test_exact_identity_preserves_parent_death_contract(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture) {
    if (::geteuid() != 0) return;
    constexpr std::uint32_t target_uid = 65'534U;
    constexpr std::uint32_t target_gid = 65'534U;
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto profile = make_profile(fixture, "/", "report");
    profile.profile.identity.mode = IdentityMode::exact;
    profile.profile.identity.uid = target_uid;
    profile.profile.identity.gid = target_gid;
    profile.profile.identity.clear_supplementary_groups = true;
    profile.profile.limits.processes = 0U;
    auto controller = TerminalController::start(factory, std::move(profile));
    require(controller.ok(), controller.status().message());
    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::array required{
        std::string{"cwd=/\n"},
        std::string{"parent-death-signal="} + std::to_string(SIGKILL) + "\n",
        std::string{"uid="} + std::to_string(target_uid) + "\n",
        std::string{"euid="} + std::to_string(target_uid) + "\n",
        std::string{"gid="} + std::to_string(target_gid) + "\n",
        std::string{"egid="} + std::to_string(target_gid) + "\n",
        std::string{"supplementary-groups=0\n"},
        std::string{"no-new-privs=1\n"},
        std::string{"ambient-capabilities=0\n"},
        std::string{"effective-capabilities=0\n"},
        std::string{"permitted-capabilities=0\n"},
        std::string{"inheritable-capabilities=0\n"},
        std::string{"bounding-capabilities=0\n"},
        std::string{"securebits-sealed=1\n"},
        std::string{"seccomp-mode=2\n"},
        std::string{"baseline-syscall-denied=1\n"},
        std::string{"terminal-injection-ioctl-denied=1\n"},
        std::string{"terminal-mutation-ioctl-set-denied=1\n"},
        terminal_ioctl_count_report_line(),
        std::string{"ordinary-ioctl-kernel-validation=1\n"},
        std::string{"namespace-clone-argument-denied=1\n"},
        std::string{"ordinary-clone-kernel-validation=1\n"},
        std::string{"clone3-legacy-fallback=1\n"},
        std::string{"thread-clone-fallback-operational=1\n"},
    };
    for (const std::string &needle : required) {
        require(text.find(needle) != std::string::npos, needle);
    }
    require(snapshot.exit.has_value(), "exact-identity exit missing");
    require(snapshot.exit->kind == ExitKind::exited,
            "exact-identity fixture did not exit normally");
    require(snapshot.exit->value == 0,
            "exact-identity fixture returned nonzero");
}

void test_strict_confinement_is_enforced_or_fails_closed(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    TempDirectory outside;
    const std::filesystem::path outside_file =
        outside.path() / "strict-outside.txt";
    const std::filesystem::path outside_existing_file =
        outside.path() / "strict-existing.txt";
    const std::filesystem::path socket_path = outside.path() / "strict.sock";
    {
        std::ofstream output(
            outside_existing_file,
            std::ios::binary | std::ios::out | std::ios::trunc);
        require(output.good(), "create strict existing outside file failed");
        output << "sentinel";
        require(output.good(), "write strict existing outside file failed");
    }
    const auto outside_contents = [&outside_existing_file]() {
        std::ifstream input(outside_existing_file, std::ios::binary);
        require(input.good(), "open strict existing outside file failed");
        std::string contents;
        std::array<char, 256U> buffer{};
        while (input.good()) {
            input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
            const std::streamsize count = input.gcount();
            if (count > 0) {
                contents.append(
                    buffer.data(), static_cast<std::size_t>(count));
            }
        }
        require(input.eof(), "read strict existing outside file failed");
        return contents;
    };
    const std::string socket_name = socket_path.string();
    require(
        socket_name.size() < sizeof(sockaddr_un::sun_path),
        "strict test Unix socket path is too long");

    FileDescriptor listener(::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0));
    require(listener.get() >= 0, "create strict test Unix socket failed");
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    std::copy(socket_name.begin(), socket_name.end(), address.sun_path);
    require(
        ::bind(
            listener.get(), reinterpret_cast<const sockaddr *>(&address),
            static_cast<socklen_t>(sizeof(address))) == 0,
        "bind strict test Unix socket failed");
    require(::listen(listener.get(), 1) == 0,
            "listen on strict test Unix socket failed");

    const std::string abstract_name =
        "iotox-strict-" + outside.path().filename().string();
    require(
        !abstract_name.empty() &&
            abstract_name.size() + 1U <= sizeof(sockaddr_un::sun_path),
        "strict abstract Unix socket name is too long");
    FileDescriptor abstract_listener(
        ::socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0));
    require(
        abstract_listener.get() >= 0,
        "create strict abstract Unix socket failed");
    sockaddr_un abstract_address{};
    abstract_address.sun_family = AF_UNIX;
    abstract_address.sun_path[0] = '\0';
    std::copy(
        abstract_name.begin(), abstract_name.end(),
        abstract_address.sun_path + 1);
    const socklen_t abstract_length = static_cast<socklen_t>(
        offsetof(sockaddr_un, sun_path) + 1U + abstract_name.size());
    require(
        ::bind(
            abstract_listener.get(),
            reinterpret_cast<const sockaddr *>(&abstract_address),
            abstract_length) == 0,
        "bind strict abstract Unix socket failed");
    require(
        ::listen(abstract_listener.get(), 1) == 0,
        "listen on strict abstract Unix socket failed");

    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto profile = make_profile(fixture, working_directory, "strict-probe");
    profile.profile.confinement = ConfinementMode::strict;
    profile.profile.arguments.push_back(outside_file.string());
    profile.profile.arguments.push_back(outside_existing_file.string());
    profile.profile.arguments.push_back(socket_path.string());
    profile.profile.arguments.push_back(abstract_name);
    auto controller = TerminalController::start(factory, std::move(profile));
    if (!controller.ok()) {
        const std::string &message = controller.status().message();
        const bool recognized_fail_closed_stage =
            message.find("Landlock strict confinement") != std::string::npos ||
            message.find("memory-deny-write-execute") != std::string::npos ||
            message.find("seccomp baseline confinement") != std::string::npos;
        require(
            recognized_fail_closed_stage,
            "strict confinement failed outside a declared fail-closed kernel boundary: " +
                message);
        require(
            !std::filesystem::exists(outside_file),
            "strict setup failure still created the outside file");
        require(
            outside_contents() == "sentinel",
            "strict setup failure mutated the existing outside file");
        return;
    }

    auto [bytes, snapshot] = collect_to_exit(*controller.value(), 3000ms);
    const std::string text = normalize_terminal_text(bytes);
    const std::array required{
        std::string{"inside-write=1\n"},
        std::string{"inside-rename=1\n"},
        std::string{"inside-unix-bind=1\n"},
        std::string{"outside-write-denied=1\n"},
        std::string{"outside-truncate-denied=1\n"},
        std::string{"outside-unlink-denied=1\n"},
        std::string{"tcp-connect-denied=1\n"},
        std::string{"tcp-bind-denied=1\n"},
        std::string{"udp-send-denied=1\n"},
        std::string{"udp-connect-denied=1\n"},
        std::string{"udp-bind-denied=1\n"},
        std::string{"pathname-unix-denied=1\n"},
        std::string{"abstract-unix-denied=1\n"},
        std::string{"signal-scope-denied=1\n"},
        std::string{"mdwe-denied=1\n"},
        std::string{"seccomp-denied=1\n"},
    };
    for (const std::string &needle : required) {
        require(text.find(needle) != std::string::npos, needle);
    }
    require(snapshot.exit.has_value(), "strict-probe exit missing");
    require(
        snapshot.exit->kind == ExitKind::exited && snapshot.exit->value == 0,
        "strict-probe fixture did not exit normally");
    require(
        std::filesystem::exists(working_directory / "strict-inside.txt"),
        "strict confinement denied the declared working-directory write");
    require(
        !std::filesystem::exists(outside_file),
        "strict confinement allowed a write outside the working directory");
    require(
        outside_contents() == "sentinel",
        "strict confinement changed the existing outside file");
}

void test_backend_enforces_direct_call_bounds(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto process = factory.spawn(
        make_profile(fixture, working_directory, "echo"));
    require(process.ok(), process.status().message());

    std::vector<std::uint8_t> oversized(kMaximumTerminalIoChunk + 1U, 0U);
    auto write = process.value()->write(oversized);
    require(!write.ok(), "direct oversized PTY write was accepted");
    require(write.status().code() == ErrorCode::resource_exhausted,
            "direct oversized PTY write used the wrong error code");

    auto empty_read = process.value()->read(0U);
    require(!empty_read.ok(), "direct zero-byte PTY read was accepted");
    require(empty_read.status().code() == ErrorCode::invalid_argument,
            "direct zero-byte PTY read used the wrong error code");

    auto oversized_read = process.value()->read(kMaximumTerminalIoChunk + 1U);
    require(!oversized_read.ok(), "direct oversized PTY read was accepted");
    require(oversized_read.status().code() == ErrorCode::invalid_argument,
            "direct oversized PTY read used the wrong error code");

    const Status invalid_resize = process.value()->resize(Dimensions{0U, 24U});
    require(!invalid_resize.ok(), "direct invalid PTY resize was accepted");
}

void test_binary_echo_and_resize(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    const bool pidfd_available = pidfd_open_is_available();
    const std::size_t pidfds_before = open_pidfd_count();
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(
        factory, make_profile(fixture, working_directory, "echo"));
    require(controller.ok(), controller.status().message());
    if (pidfd_available) {
        require(
            open_pidfd_count() >= pidfds_before + 1U,
            "PTY supervisor did not retain a pidfd for its live child");
    }
    const auto ready = collect_until(*controller.value(), "READY\n", 3000ms);
    require(
        normalize_terminal_text(ready).find("READY\n") != std::string::npos,
        "echo fixture did not become ready");

    auto resized = controller.value()->resize(Dimensions{200U, 2U});
    require(resized.ok(), resized.status().message());
    require(
        resized.value() == Dimensions{160U, 5U},
        "native resize did not use policy clamps");

    const std::array<std::uint8_t, 9U> payload{
        0U, 1U, 2U, 10U, 13U, 127U, 128U, 254U, 255U};
    std::size_t written = 0U;
    const auto write_deadline = std::chrono::steady_clock::now() + 3000ms;
    while (written < payload.size() &&
           std::chrono::steady_clock::now() < write_deadline) {
        auto result = controller.value()->write_input(
            std::span<const std::uint8_t>{payload}.subspan(written));
        require(result.ok(), result.status().message());
        if (result.value().disposition == IoDisposition::progress) {
            written += result.value().bytes;
        } else {
            std::this_thread::sleep_for(1ms);
        }
    }
    require(written == payload.size(), "binary PTY write timed out");

    std::vector<std::uint8_t> echoed;
    const auto read_deadline = std::chrono::steady_clock::now() + 3000ms;
    while (echoed.size() < payload.size() &&
           std::chrono::steady_clock::now() < read_deadline) {
        auto result = controller.value()->read_output(4096U);
        require(result.ok(), result.status().message());
        if (result.value().disposition == IoDisposition::progress) {
            echoed.insert(
                echoed.end(), result.value().bytes.begin(),
                result.value().bytes.end());
        } else {
            std::this_thread::sleep_for(1ms);
        }
    }
    require(echoed.size() >= payload.size(), "binary PTY echo timed out");
    require(
        std::equal(payload.begin(), payload.end(), echoed.begin()),
        "binary PTY echo changed bytes");

    const auto close_time = std::chrono::steady_clock::now();
    require_ok(
        controller.value()->request_close(
            CloseReason::controller_request, close_time),
        "request echo close");
    const auto exit_deadline = std::chrono::steady_clock::now() + 3000ms;
    while (std::chrono::steady_clock::now() < exit_deadline) {
        require_ok(controller.value()->poll(close_time), "poll echo close");
        if (controller.value()->snapshot().phase == ControllerPhase::exited) break;
        std::this_thread::sleep_for(1ms);
    }
    const auto snapshot = controller.value()->snapshot();
    require(snapshot.phase == ControllerPhase::exited, "echo did not exit on HUP");
    require(snapshot.exit.has_value(), "echo exit missing");
    require(snapshot.exit->kind == ExitKind::signaled, "echo was not signaled");
    require(snapshot.exit->value == SIGHUP, "echo received the wrong close signal");
    require(snapshot.hangup_signals == 1U, "echo HUP count is wrong");
    require(snapshot.resize_calls == 1U, "echo resize count is wrong");
    require(snapshot.input_bytes == payload.size(), "echo input count is wrong");
}

void test_forced_shutdown(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto controller = TerminalController::start(
        factory, make_profile(fixture, working_directory, "ignore"));
    require(controller.ok(), controller.status().message());
    static_cast<void>(collect_until(*controller.value(), "READY\n", 3000ms));

    const auto start = std::chrono::steady_clock::now();
    require_ok(
        controller.value()->request_close(CloseReason::authority_revoked, start),
        "request forced close");
    require_ok(controller.value()->poll(start + 20ms), "send TERM");
    require_ok(controller.value()->poll(start + 40ms), "send KILL");

    const auto deadline = std::chrono::steady_clock::now() + 3000ms;
    while (std::chrono::steady_clock::now() < deadline) {
        require_ok(controller.value()->poll(start + 40ms), "reap killed PTY");
        if (controller.value()->snapshot().phase == ControllerPhase::exited) break;
        std::this_thread::sleep_for(1ms);
    }
    const auto snapshot = controller.value()->snapshot();
    require(snapshot.phase == ControllerPhase::exited, "ignored process was not reaped");
    require(snapshot.exit.has_value(), "forced exit missing");
    require(snapshot.exit->kind == ExitKind::signaled, "forced exit was not signaled");
    require(snapshot.exit->value == SIGKILL, "forced exit was not SIGKILL");
    require(snapshot.close_reason == CloseReason::authority_revoked,
            "forced close reason changed");
    require(snapshot.hangup_signals == 1U, "forced HUP count is wrong");
    require(snapshot.terminate_signals == 1U, "forced TERM count is wrong");
    require(snapshot.kill_signals == 1U, "forced KILL count is wrong");
}


void test_cgroup_configuration_fails_closed_without_cgroup2(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &ordinary_directory) {
    auto profile_budget =
        make_profile(fixture, ordinary_directory, "report");
    profile_budget.profile.cgroup_limits.maximum_processes = 3U;
    PosixPtyProcessFactory unrooted_profile_factory(
        PosixPtyOptions{iotox, 3000ms});
    auto unrooted_profile =
        unrooted_profile_factory.spawn(profile_budget);
    require(
        !unrooted_profile.ok(),
        "profile-scoped resource policy was accepted without a cgroup root");
    require(
        unrooted_profile.status().code() == ErrorCode::invalid_argument,
        "unrooted profile resource policy failed with the wrong error code");
    require(
        unrooted_profile.status().message().find("delegated cgroup root") !=
            std::string::npos,
        "unrooted profile resource policy omitted the delegation requirement");

    CgroupResourceLimits unrooted_limits;
    unrooted_limits.maximum_processes = 4U;
    PosixPtyProcessFactory unrooted_factory(
        PosixPtyOptions{iotox, 3000ms, {}, unrooted_limits});
    auto unrooted = unrooted_factory.spawn(
        make_profile(fixture, ordinary_directory, "report"));
    require(!unrooted.ok(),
            "controller-backed resource policy was accepted without a cgroup root");
    require(
        unrooted.status().code() == ErrorCode::invalid_argument,
        "unrooted resource policy failed with the wrong error code");
    require(
        unrooted.status().message().find("delegated cgroup root") !=
            std::string::npos,
        "unrooted resource policy failure omitted the delegation requirement");

    CgroupAggregateLimits unrooted_aggregate;
    unrooted_aggregate.maximum_reserved_processes = 4U;
    PosixPtyProcessFactory unrooted_aggregate_factory(
        PosixPtyOptions{
            iotox, 3000ms, {}, {}, unrooted_aggregate});
    auto unrooted_aggregate_result = unrooted_aggregate_factory.spawn(
        make_profile(fixture, ordinary_directory, "report"));
    require(
        !unrooted_aggregate_result.ok(),
        "aggregate reservation was accepted without a cgroup root");
    require(
        unrooted_aggregate_result.status().code() ==
            ErrorCode::invalid_argument,
        "unrooted aggregate reservation failed with the wrong error code");

    CgroupPressureAdmissionLimits unrooted_pressure;
    unrooted_pressure.maximum_cpu_some_average_10_basis_points = 100U;
    unrooted_pressure.hysteresis_basis_points = 25U;
    PosixPtyProcessFactory unrooted_pressure_factory(
        PosixPtyOptions{
            iotox, 3000ms, {}, {}, {}, unrooted_pressure});
    const Status unrooted_pressure_configuration =
        unrooted_pressure_factory.configuration_status();
    require(
        !unrooted_pressure_configuration.ok(),
        "pressure admission factory deferred its missing-root failure");
    require(
        unrooted_pressure_configuration.code() == ErrorCode::invalid_argument,
        "unrooted pressure admission failed with the wrong error code");
    auto unrooted_pressure_result = unrooted_pressure_factory.spawn(
        make_profile(fixture, ordinary_directory, "report"));
    require(
        !unrooted_pressure_result.ok(),
        "pressure admission was accepted without a cgroup root");
    require(
        unrooted_pressure_result.status().message().find(
            "pressure admission requires a delegated cgroup root") !=
            std::string::npos,
        "unrooted pressure admission omitted the delegation requirement");
    const auto unrooted_pressure_snapshot =
        unrooted_pressure_factory.aggregate_snapshot().pressure_admission;
    require(
        unrooted_pressure_snapshot.limits == unrooted_pressure &&
            unrooted_pressure_snapshot.checks == 0U &&
            unrooted_pressure_snapshot.rejections == 0U,
        "configuration failure mutated pressure admission accounting");

    CgroupPressureAdmissionLimits malformed_pressure;
    malformed_pressure.maximum_memory_full_average_10_basis_points = 10U;
    malformed_pressure.hysteresis_basis_points = 11U;
    PosixPtyProcessFactory malformed_pressure_factory(
        PosixPtyOptions{
            iotox, 3000ms, ordinary_directory, {}, {}, malformed_pressure});
    const Status malformed_pressure_configuration =
        malformed_pressure_factory.configuration_status();
    require(
        !malformed_pressure_configuration.ok() &&
            malformed_pressure_configuration.code() ==
                ErrorCode::invalid_argument,
        "malformed pressure hysteresis reached cgroup filesystem access");
    require(
        malformed_pressure_configuration.message().find(
            "hysteresis must not exceed") != std::string::npos,
        "malformed pressure hysteresis omitted its semantic reason");

    PosixPtyProcessFactory ordinary_pressure_factory(
        PosixPtyOptions{
            iotox, 3000ms, ordinary_directory, {}, {}, unrooted_pressure});
    const Status ordinary_pressure_configuration =
        ordinary_pressure_factory.configuration_status();
    require(
        !ordinary_pressure_configuration.ok() &&
            ordinary_pressure_configuration.code() == ErrorCode::unsupported,
        "ordinary directory passed pressure admission startup preflight");
    require(
        ordinary_pressure_configuration.message().find("cgroup v2") !=
            std::string::npos,
        "pressure admission preflight omitted the cgroup-v2 boundary");

    CgroupResourceLimits malformed_limits;
    malformed_limits.cpu_period_microseconds = 100000U;
    PosixPtyProcessFactory malformed_factory(
        PosixPtyOptions{
            iotox, 3000ms, ordinary_directory, malformed_limits});
    auto malformed = malformed_factory.spawn(
        make_profile(fixture, ordinary_directory, "report"));
    require(!malformed.ok(),
            "malformed controller policy reached cgroup filesystem access");
    require(
        malformed.status().code() == ErrorCode::invalid_argument,
        "malformed controller policy failed with the wrong error code");
    require(
        malformed.status().message().find("period requires") !=
            std::string::npos,
        "malformed controller policy omitted its semantic reason");

    PosixPtyProcessFactory inherited_factory(
        PosixPtyOptions{iotox, 3000ms, ordinary_directory});
    auto inherited = inherited_factory.spawn(
        make_profile(fixture, ordinary_directory, "report"));
    require(!inherited.ok(),
            "cgroup containment accepted an inherited PTY identity");
    require(
        inherited.status().code() == ErrorCode::invalid_argument,
        "inherited cgroup identity failed with the wrong error code");

    auto exact = make_profile(fixture, ordinary_directory, "report");
    exact.profile.identity.mode = IdentityMode::exact;
    const std::uint64_t effective_uid =
        static_cast<std::uint64_t>(::geteuid());
    exact.profile.identity.uid =
        effective_uid == 65534U ? 65533U : 65534U;
    exact.profile.identity.gid = exact.profile.identity.uid;
    exact.profile.identity.clear_supplementary_groups = true;

    PosixPtyProcessFactory missing_reservation_factory(
        PosixPtyOptions{
            iotox, 3000ms, ordinary_directory, {}, unrooted_aggregate});
    auto missing_reservation = missing_reservation_factory.spawn(exact);
    require(
        !missing_reservation.ok(),
        "aggregate admission accepted a session without a finite reservation");
    require(
        missing_reservation.status().code() == ErrorCode::invalid_argument,
        "missing aggregate reservation used the wrong error code");
    require(
        missing_reservation_factory.aggregate_snapshot().active_reservations ==
            0U,
        "rejected aggregate admission changed active accounting");

    auto reserved = exact;
    reserved.profile.cgroup_limits.maximum_processes = 2U;
    reserved.profile.cgroup_limits.cpu_quota_microseconds = 75000U;
    reserved.profile.cgroup_limits.cpu_period_microseconds = 50000U;
    CgroupAggregateLimits two_processes;
    two_processes.maximum_reserved_processes = 2U;
    two_processes.maximum_reserved_cpu_quota_microseconds = 150000U;
    two_processes.cpu_period_microseconds = 100000U;
    PosixPtyProcessFactory rollback_factory(
        PosixPtyOptions{
            "relative-helper", 3000ms, ordinary_directory, {},
            two_processes});
    auto rolled_back = rollback_factory.spawn(reserved);
    require(!rolled_back.ok(), "relative helper unexpectedly spawned");
    require(
        rolled_back.status().code() == ErrorCode::invalid_argument,
        "relative helper failure used the wrong error code");
    const auto rolled_back_snapshot = rollback_factory.aggregate_snapshot();
    require(
        rolled_back_snapshot.active_reservations == 0U &&
            rolled_back_snapshot.reserved_processes == 0U &&
            rolled_back_snapshot.reserved_cpu_quota_microseconds == 0U,
        "failed spawn retained an aggregate cgroup reservation");
    require(
        rolled_back_snapshot.peak_active_reservations == 1U &&
            rolled_back_snapshot.peak_reserved_processes == 2U &&
            rolled_back_snapshot.peak_reserved_cpu_quota_microseconds ==
                150000U,
        "failed spawn did not prove reservation-before-mutation ordering");

    auto unrepresentable_cpu = exact;
    unrepresentable_cpu.profile.cgroup_limits.cpu_quota_microseconds = 1000U;
    unrepresentable_cpu.profile.cgroup_limits.cpu_period_microseconds = 3000U;
    CgroupAggregateLimits aggregate_cpu;
    aggregate_cpu.maximum_reserved_cpu_quota_microseconds = 100000U;
    aggregate_cpu.cpu_period_microseconds = 100000U;
    PosixPtyProcessFactory unrepresentable_cpu_factory(
        PosixPtyOptions{
            iotox, 3000ms, ordinary_directory, {}, aggregate_cpu});
    auto unrepresentable_cpu_result =
        unrepresentable_cpu_factory.spawn(unrepresentable_cpu);
    require(
        !unrepresentable_cpu_result.ok(),
        "aggregate admission rounded a nonrepresentable CPU reservation");
    require(
        unrepresentable_cpu_result.status().code() ==
            ErrorCode::invalid_argument,
        "nonrepresentable CPU reservation used the wrong error code");
    require(
        unrepresentable_cpu_result.status().message().find(
            "exactly representable") != std::string::npos,
        "nonrepresentable CPU reservation omitted its exactness reason");
    const auto unrepresentable_cpu_snapshot =
        unrepresentable_cpu_factory.aggregate_snapshot();
    require(
        unrepresentable_cpu_snapshot.active_reservations == 0U &&
            unrepresentable_cpu_snapshot.peak_active_reservations == 0U &&
            unrepresentable_cpu_snapshot.reserved_cpu_quota_microseconds ==
                0U,
        "nonrepresentable CPU policy mutated aggregate admission state");

    PosixPtyProcessFactory ordinary_factory(
        PosixPtyOptions{iotox, 3000ms, ordinary_directory});
    auto ordinary = ordinary_factory.spawn(exact);
    require(!ordinary.ok(),
            "ordinary directory was accepted as a cgroup v2 delegation");
    require(
        ordinary.status().code() == ErrorCode::unsupported,
        "ordinary cgroup root failed with the wrong error code");
    require(
        ordinary.status().message().find("cgroup v2") != std::string::npos,
        "ordinary cgroup root failure omitted the kernel boundary");

    auto compatibility = exact;
    compatibility.profile.confinement = ConfinementMode::compatibility;
    auto compatibility_result = ordinary_factory.spawn(compatibility);
    require(!compatibility_result.ok(),
            "compatibility profile accepted cgroup containment");
    require(
        compatibility_result.status().code() == ErrorCode::invalid_argument,
        "compatibility cgroup failure used the wrong error code");
}

void test_inherited_identity_rejects_per_uid_process_limit(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &ordinary_directory) {
    auto profile = make_profile(fixture, ordinary_directory, "report");
    profile.profile.limits.processes = 8U;
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto result = factory.spawn(profile);
    require(!result.ok(),
            "inherited PTY identity accepted a per-UID process limit");
    require(result.status().code() == ErrorCode::invalid_argument,
            "inherited PTY process limit failed with the wrong error code");
    require(result.status().message().find("RLIMIT_NPROC") !=
                std::string::npos &&
            result.status().message().find("pids.max") != std::string::npos,
            "inherited PTY process-limit failure omitted the safe alternative");
}

void test_executable_rejections(
    const std::filesystem::path &iotox,
    const std::filesystem::path &fixture,
    const std::filesystem::path &working_directory) {
    const std::filesystem::path symlink = working_directory / "fixture-link";
    std::filesystem::create_symlink(fixture, symlink);
    PosixPtyProcessFactory factory(PosixPtyOptions{iotox, 3000ms});
    auto symlinked = factory.spawn(
        make_profile(symlink, working_directory, "report"));
    require(!symlinked.ok(), "symlink executable was accepted");

    const std::filesystem::path writable = working_directory / "writable-fixture";
    std::filesystem::copy_file(fixture, writable);
    require(::chmod(writable.c_str(), static_cast<mode_t>(0777)) == 0,
            "chmod writable fixture failed");
    auto writable_result = factory.spawn(
        make_profile(writable, working_directory, "report"));
    require(!writable_result.ok(), "group/other-writable executable was accepted");
    require(
        writable_result.status().code() == ErrorCode::invalid_argument,
        "writable executable failed with the wrong error code");

    auto impossible_limits = make_profile(fixture, working_directory, "report");
    impossible_limits.profile.limits.open_files = (1ULL << 60U);
    auto child_rejection = factory.spawn(impossible_limits);
    require(!child_rejection.ok(), "impossible child limit was accepted");
    require(
        child_rejection.status().message().find("resource limits") !=
            std::string::npos,
        "child setup failure did not preserve its stage");

    PosixPtyProcessFactory wrong_helper(PosixPtyOptions{fixture, 1000ms});
    for (unsigned attempt = 0U; attempt < 8U; ++attempt) {
        auto unreviewed_helper = wrong_helper.spawn(
            make_profile(fixture, working_directory, "report"));
        require(!unreviewed_helper.ok(), "unreviewed PTY helper was accepted");
        require(
            unreviewed_helper.status().code() == ErrorCode::protocol_error,
            "unreviewed PTY helper failure was not classified at the protocol boundary: " +
                unreviewed_helper.status().message());
        require(
            unreviewed_helper.status().message().find("became ready") !=
                std::string::npos,
            "unreviewed PTY helper failure omitted the readiness boundary");
    }

    auto correct_digest = iotox::sync::hash_sync_file_sha256(fixture);
    require(correct_digest.ok(), correct_digest.status().message());
    auto pinned = make_profile(fixture, working_directory, "report");
    pinned.profile.executable_sha256 = correct_digest.value();
    auto pinned_result = TerminalController::start(factory, pinned);
    require(pinned_result.ok(), pinned_result.status().message());
    auto [pinned_bytes, pinned_snapshot] =
        collect_to_exit(*pinned_result.value(), 3000ms);
    static_cast<void>(pinned_bytes);
    require(
        pinned_snapshot.exit.has_value() &&
            pinned_snapshot.exit->kind == ExitKind::exited &&
            pinned_snapshot.exit->value == 0,
        "correct executable SHA-256 pin did not reach normal exit");

    pinned.profile.executable_sha256->front() ^= 0xffU;
    auto mismatched = factory.spawn(pinned);
    require(!mismatched.ok(), "incorrect executable SHA-256 pin was accepted");
    require(
        mismatched.status().code() == ErrorCode::protocol_error &&
            mismatched.status().message().find("SHA-256 pin") !=
            std::string::npos,
        "incorrect executable SHA-256 pin failed at the wrong boundary");

    const std::filesystem::path toolbox = working_directory / "pinned-toolbox";
    std::filesystem::create_directory(toolbox);
    require(::chmod(toolbox.c_str(), static_cast<mode_t>(0700)) == 0,
            "chmod pinned toolbox failed");
    const std::filesystem::path toybox = toolbox / "toybox";
    std::filesystem::copy_file(fixture, toybox);
    require(::chmod(toybox.c_str(), static_cast<mode_t>(0500)) == 0,
            "chmod pinned Toybox failed");
    auto correct_toolbox_digest = iotox::sync::hash_sync_file_sha256(toybox);
    require(correct_toolbox_digest.ok(), correct_toolbox_digest.status().message());
    auto toolbox_pinned = make_profile(fixture, working_directory, "report");
    toolbox_pinned.profile.executable_sha256 = correct_digest.value();
    toolbox_pinned.profile.toolbox_sha256 = correct_toolbox_digest.value();
    toolbox_pinned.profile.environment.push_back(
        EnvironmentEntry{"IOTOX_RESCUE_TOOLBOX", toolbox.string()});
    toolbox_pinned.environment.insert(
        toolbox_pinned.environment.begin() + 1,
        EnvironmentEntry{"IOTOX_RESCUE_TOOLBOX", toolbox.string()});
    auto toolbox_pinned_result =
        TerminalController::start(factory, toolbox_pinned);
    require(toolbox_pinned_result.ok(), toolbox_pinned_result.status().message());
    auto [toolbox_pinned_bytes, toolbox_pinned_snapshot] =
        collect_to_exit(*toolbox_pinned_result.value(), 3000ms);
    static_cast<void>(toolbox_pinned_bytes);
    require(
        toolbox_pinned_snapshot.exit.has_value() &&
            toolbox_pinned_snapshot.exit->kind == ExitKind::exited &&
            toolbox_pinned_snapshot.exit->value == 0,
        "correct toolbox SHA-256 pin did not reach normal exit");

    require(::chmod(toybox.c_str(), static_cast<mode_t>(0700)) == 0,
            "make pinned Toybox writable failed");
    {
        std::ofstream changed(toybox, std::ios::binary | std::ios::app);
        require(changed.good(), "open pinned Toybox for mutation failed");
        changed.put('\0');
        require(changed.good(), "mutate pinned Toybox failed");
    }
    require(::chmod(toybox.c_str(), static_cast<mode_t>(0500)) == 0,
            "reseal pinned Toybox failed");
    auto changed_toolbox = factory.spawn(toolbox_pinned);
    require(!changed_toolbox.ok(), "mutated toolbox SHA-256 payload was accepted");
    require(
        changed_toolbox.status().code() == ErrorCode::protocol_error &&
            changed_toolbox.status().message().find("toolbox executable does not match") !=
                std::string::npos,
        "mutated toolbox payload failed at the wrong boundary");
}

}  // namespace

int main(int argc, char **argv) {
    try {
        if (argc == 5 &&
            std::string_view(argv[1]) == "--rescue-toolbox-qualification") {
            qualify_rescue_toolbox_through_shell(
                std::filesystem::absolute(argv[2]).lexically_normal(),
                std::filesystem::absolute(argv[3]).lexically_normal(),
                std::filesystem::absolute(argv[4]).lexically_normal());
            std::cout << "terminal rescue toolbox qualification passed\n";
            return 0;
        }
        if (argc == 7 &&
            std::string_view(argv[1]) == "--sudo-shell-qualification") {
            qualify_password_sudo_through_login_shell(
                std::filesystem::absolute(argv[2]).lexically_normal(),
                std::filesystem::absolute(argv[3]).lexically_normal(),
                std::filesystem::absolute(argv[4]).lexically_normal(),
                std::filesystem::absolute(argv[5]).lexically_normal(),
                argv[6]);
            std::cout << "terminal sudo shell qualification passed\n";
            return 0;
        }
        if (argc == 6 &&
            std::string_view(argv[1]) == "--sudo-qualification") {
            qualify_real_sudo_from_non_root_account(
                std::filesystem::absolute(argv[2]).lexically_normal(),
                std::filesystem::absolute(argv[3]).lexically_normal(),
                std::filesystem::absolute(argv[4]).lexically_normal(),
                std::filesystem::absolute(argv[5]).lexically_normal());
            std::cout << "terminal sudo qualification passed\n";
            return 0;
        }
        if (argc == 5 &&
            std::string_view(argv[1]) == "--parent-death-supervisor") {
            return run_parent_death_supervisor(
                std::filesystem::absolute(argv[2]).lexically_normal(),
                std::filesystem::absolute(argv[3]).lexically_normal(),
                std::filesystem::absolute(argv[4]).lexically_normal());
        }
        if (argc == 5 &&
            std::string_view(argv[1]) == "--ambient-capability-supervisor") {
            return run_ambient_capability_supervisor(
                std::filesystem::absolute(argv[2]).lexically_normal(),
                std::filesystem::absolute(argv[3]).lexically_normal(),
                std::filesystem::absolute(argv[4]).lexically_normal());
        }
        require(argc == 3, "usage: test-terminal-posix IOTOX FIXTURE");
        const std::filesystem::path iotox =
            std::filesystem::absolute(argv[1]).lexically_normal();
        const std::filesystem::path fixture =
            std::filesystem::absolute(argv[2]).lexically_normal();
        TempDirectory temporary;
        test_report(iotox, fixture, temporary.path());
        test_explicit_privilege_escalation_boundary(
            iotox, fixture, temporary.path());
        test_baseline_lifecycle_fences(iotox, fixture, temporary.path());
        test_high_inherited_descriptor_is_closed(
            iotox, fixture, temporary.path());
        test_exact_identity_preserves_parent_death_contract(iotox, fixture);
        test_parent_death_contract_is_effective(
            current_executable(), iotox, fixture, temporary.path());
        test_inherited_ambient_capabilities_are_cleared(
            current_executable(), iotox, fixture, temporary.path());
        test_strict_confinement_is_enforced_or_fails_closed(
            iotox, fixture, temporary.path());
        test_binary_echo_and_resize(iotox, fixture, temporary.path());
        test_forced_shutdown(iotox, fixture, temporary.path());
        test_session_wide_shutdown_contains_separate_process_groups(
            iotox, fixture, temporary.path());
        test_natural_leader_exit_reaps_remaining_session(
            iotox, fixture, temporary.path());
        test_reap_requires_repeated_quiescent_session_inventories(
            iotox, fixture, temporary.path());
        test_session_shutdown_converges_during_bounded_fork_churn(
            iotox, fixture, temporary.path());
        test_backend_enforces_direct_call_bounds(
            iotox, fixture, temporary.path());
        test_cgroup_configuration_fails_closed_without_cgroup2(
            iotox, fixture, temporary.path());
        test_inherited_identity_rejects_per_uid_process_limit(
            iotox, fixture, temporary.path());
        test_executable_rejections(iotox, fixture, temporary.path());
        std::cout << "terminal POSIX process tests passed\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "terminal POSIX process test failure: " << error.what() << '\n';
        return 1;
    }
}
