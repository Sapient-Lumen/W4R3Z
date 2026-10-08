#include "self_exec_test_process.hpp"

#include <charconv>
#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <utility>
#include <vector>

#include <dirent.h>
#include <fcntl.h>
#include <spawn.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <unistd.h>

extern char** environ;

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;

constexpr unsigned kFixtureFailSafeSeconds = 15;
using anonsync::test::current_self_executable_or_throw;
using anonsync::test::spawn_self_exec_test_process_or_throw;
using anonsync::test::spawn_self_exec_test_process_with_output_capture_or_throw;
using anonsync::test::verify_self_exec_child_boundary_or_throw;

constexpr std::string_view kHelperFlag =
    "--anonsync-self-exec-test-helper-v1";
constexpr std::string_view kDescendantFlag =
    "--anonsync-self-exec-test-descendant-v1";
constexpr int kSuccessExit = 37;
constexpr int kHelperFailureExit = 91;
constexpr int kHelperUsageExit = 92;

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

class ScopedPidReport final {
public:
    explicit ScopedPidReport(std::string_view stem) {
        path_ = fs::temp_directory_path() /
                (std::string(stem) + "-" + std::to_string(::getpid()) + "-" +
                 std::to_string(std::chrono::steady_clock::now()
                                    .time_since_epoch()
                                    .count()));
        std::error_code error;
        (void)fs::remove(path_, error);
        native_ = path_.native();
    }

    ScopedPidReport(const ScopedPidReport&) = delete;
    ScopedPidReport& operator=(const ScopedPidReport&) = delete;

    ~ScopedPidReport() {
        std::error_code error;
        (void)fs::remove(path_, error);
    }

    [[nodiscard]] const std::string& native() const noexcept { return native_; }

    [[nodiscard]] pid_t read_exact_or_throw() const {
        const int descriptor =
            ::open(native_.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (descriptor < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "open self-exec escaped-child PID report");
        }
        pid_t value = -1;
        unsigned char* cursor = reinterpret_cast<unsigned char*>(&value);
        std::size_t remaining = sizeof(value);
        while (remaining != 0) {
            const ssize_t count = ::read(descriptor, cursor, remaining);
            if (count < 0 && errno == EINTR) continue;
            if (count <= 0) {
                const int read_error = count < 0 ? errno : EIO;
                (void)::close(descriptor);
                throw std::system_error(
                    read_error, std::generic_category(),
                    "read self-exec escaped-child PID report");
            }
            cursor += static_cast<std::size_t>(count);
            remaining -= static_cast<std::size_t>(count);
        }
        unsigned char extra = 0;
        ssize_t trailing = -1;
        do {
            trailing = ::read(descriptor, &extra, 1);
        } while (trailing < 0 && errno == EINTR);
        const int trailing_error = errno;
        (void)::close(descriptor);
        if (trailing > 0) {
            throw std::runtime_error(
                "self-exec escaped-child PID report was not exact");
        }
        if (trailing < 0) {
            throw std::system_error(
                trailing_error, std::generic_category(),
                "finish self-exec escaped-child PID report");
        }
        if (value <= 0) {
            throw std::runtime_error(
                "self-exec escaped-child PID report was not positive");
        }
        return value;
    }

private:
    fs::path path_;
    std::string native_;
};

bool write_exact(int descriptor, const void* data, std::size_t size) noexcept {
    const auto* cursor = static_cast<const unsigned char*>(data);
    while (size != 0) {
        const ssize_t count = ::write(descriptor, cursor, size);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return false;
        cursor += static_cast<std::size_t>(count);
        size -= static_cast<std::size_t>(count);
    }
    return true;
}

bool write_pid_report_noexcept(const char* path, pid_t value) noexcept {
    const int descriptor = ::open(
        path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (descriptor < 0) return false;
    const bool written = write_exact(descriptor, &value, sizeof(value));
    const bool synchronized = written && ::fdatasync(descriptor) == 0;
    const bool closed = ::close(descriptor) == 0;
    return written && synchronized && closed;
}

class ScopedChildSubreaper final {
public:
    ScopedChildSubreaper() {
        if (::prctl(PR_GET_CHILD_SUBREAPER, &previous_) != 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "prctl(PR_GET_CHILD_SUBREAPER)");
        }
        changed_ = previous_ == 0;
        if (changed_ && ::prctl(PR_SET_CHILD_SUBREAPER, 1L) != 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "prctl(PR_SET_CHILD_SUBREAPER)");
        }
    }

    ScopedChildSubreaper(const ScopedChildSubreaper&) = delete;
    ScopedChildSubreaper& operator=(const ScopedChildSubreaper&) = delete;

    ~ScopedChildSubreaper() {
        if (changed_) (void)::prctl(PR_SET_CHILD_SUBREAPER, 0L);
    }

private:
    int previous_ = 0;
    bool changed_ = false;
};

pid_t parse_exact_descendant_report_or_throw(const std::string& output) {
    constexpr std::string_view prefix = "descendant=";
    if (output.size() <= prefix.size() + 1 || output.back() != '\n' ||
        output.find('\n') != output.size() - 1 ||
        output.find('\r') != std::string::npos ||
        output.find('\0') != std::string::npos ||
        std::string_view(output).substr(0, prefix.size()) != prefix) {
        throw std::runtime_error(
            "descendant report was not one exact LF record");
    }
    const std::string_view digits(output.data() + prefix.size(),
                                  output.size() - prefix.size() - 1);
    pid_t descendant = -1;
    const auto parsed = std::from_chars(
        digits.data(), digits.data() + digits.size(), descendant);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != digits.data() + digits.size() || descendant <= 0) {
        throw std::runtime_error(
            "descendant report was not one exact positive PID");
    }
    return descendant;
}

bool reap_exact_sigkill_bounded(pid_t descendant) noexcept {
    int status = 0;
    const auto deadline = std::chrono::steady_clock::now() + 2s;
    for (;;) {
        const pid_t observed = ::waitpid(descendant, &status, WNOHANG);
        if (observed == descendant) {
            return WIFSIGNALED(status) && WTERMSIG(status) == SIGKILL;
        }
        if (observed < 0 && errno != EINTR) return false;
        if (std::chrono::steady_clock::now() >= deadline) break;
        std::this_thread::sleep_for(5ms);
    }

    (void)::kill(descendant, SIGKILL);
    while (::waitpid(descendant, &status, 0) < 0 && errno == EINTR) {
    }
    return false;
}

int run_descendant(int argc, char** argv) noexcept {
    if (argc != 2 || std::string_view(argv[1]) != kDescendantFlag) {
        return kHelperUsageExit;
    }
    (void)::alarm(kFixtureFailSafeSeconds);
    for (;;) (void)::pause();
}

pid_t spawn_lingering_descendant_or_throw() {
    const std::string executable = current_self_executable_or_throw().native();
    const std::string descendant_flag(kDescendantFlag);
    std::vector<char*> arguments{
        const_cast<char*>(executable.c_str()),
        const_cast<char*>(descendant_flag.c_str()),
        nullptr,
    };

    pid_t descendant = -1;
    const int rc = ::posix_spawn(&descendant, executable.c_str(), nullptr,
                                 nullptr, arguments.data(), environ);
    if (rc != 0 || descendant <= 0) {
        throw std::system_error(
            rc != 0 ? rc : ECHILD, std::generic_category(),
            "self-exec helper lingering-descendant posix_spawn");
    }
    if (::getpgid(descendant) != ::getpgrp()) {
        (void)::kill(descendant, SIGKILL);
        int status = 0;
        while (::waitpid(descendant, &status, 0) < 0 && errno == EINTR) {
        }
        throw std::runtime_error(
            "lingering descendant escaped the helper process group");
    }
    return descendant;
}

std::size_t count_parent_open_descriptors_or_throw() {
    DIR* raw_directory = ::opendir("/proc/self/fd");
    if (raw_directory == nullptr) {
        throw std::runtime_error("could not open /proc/self/fd");
    }
    const int scan_descriptor = ::dirfd(raw_directory);
    if (scan_descriptor < 0) {
        (void)::closedir(raw_directory);
        throw std::runtime_error("could not identify /proc/self/fd scanner");
    }

    std::size_t count = 0;
    errno = 0;
    while (dirent* entry = ::readdir(raw_directory)) {
        char* end = nullptr;
        errno = 0;
        const long descriptor = std::strtol(entry->d_name, &end, 10);
        if (errno == 0 && end != entry->d_name && *end == '\0' &&
            descriptor >= 0 && descriptor != scan_descriptor) {
            ++count;
        }
        errno = 0;
    }
    const int read_errno = errno;
    (void)::closedir(raw_directory);
    if (read_errno != 0) {
        throw std::runtime_error("could not enumerate /proc/self/fd");
    }
    return count;
}

int run_helper(int argc, char** argv) {
    try {
        verify_self_exec_child_boundary_or_throw();
        if (::getenv("ANONSYNC_SELF_EXEC_PARENT_LEAK") != nullptr) {
            return kHelperFailureExit;
        }
        if ((argc != 3 && argc != 4) ||
            std::string_view(argv[1]) != kHelperFlag) {
            return kHelperUsageExit;
        }
        const std::string_view action(argv[2]);
        if (action == "return-with-escaped-capture-descendant") {
            if (argc != 4) return kHelperUsageExit;
            auto* escaped_owner = new anonsync::test::SelfExecTestProcess(
                spawn_self_exec_test_process_or_throw(
                    current_self_executable_or_throw(),
                    {std::string(kHelperFlag), "hang-until-parent-kills"}));
            const pid_t escaped = escaped_owner->process_id();
            if (escaped <= 0 ||
                !write_pid_report_noexcept(argv[3], escaped)) {
                delete escaped_owner;
                return kHelperFailureExit;
            }
            return kSuccessExit;
        }
        if (argc != 3) return kHelperUsageExit;
        if (action == "return-exact") return kSuccessExit;
        if (action == "emit-captured") {
            std::cout << "stdout-evidence\n" << std::flush;
            std::cerr << "stderr-evidence\n" << std::flush;
            return kSuccessExit;
        }
        if (action == "emit-large-captured") {
            constexpr int kMaximumReviewedPipeCapacity = 4 * 1024 * 1024;
            const int stdout_capacity = ::fcntl(STDOUT_FILENO, F_GETPIPE_SZ);
            const int stderr_capacity = ::fcntl(STDERR_FILENO, F_GETPIPE_SZ);
            if (stdout_capacity <= 0 || stderr_capacity <= 0 ||
                stdout_capacity > kMaximumReviewedPipeCapacity ||
                stderr_capacity > kMaximumReviewedPipeCapacity) {
                return kHelperFailureExit;
            }
            std::cout << std::string(
                             static_cast<std::size_t>(stdout_capacity) + 4096,
                             'o')
                      << std::flush;
            std::cerr << std::string(
                             static_cast<std::size_t>(stderr_capacity) + 4096,
                             'e')
                      << std::flush;
            return kSuccessExit;
        }
        if (action == "emit-over-budget") {
            std::cout << std::string(4096, 'x') << std::flush;
            (void)::alarm(kFixtureFailSafeSeconds);
            for (;;) (void)::pause();
        }
        if (action == "emit-then-hang") {
            std::cout << "stdout-before-hang\n" << std::flush;
            std::cerr << "stderr-before-hang\n" << std::flush;
            (void)::alarm(kFixtureFailSafeSeconds);
            for (;;) (void)::pause();
        }
        if (action == "hang-until-parent-kills") {
            (void)::alarm(kFixtureFailSafeSeconds);
            for (;;) (void)::pause();
        }
        if (action == "return-with-lingering-descendant") {
            const pid_t descendant = spawn_lingering_descendant_or_throw();
            std::cout << "descendant=" << descendant << "\n" << std::flush;
            if (!std::cout) {
                (void)::kill(descendant, SIGKILL);
                int status = 0;
                while (::waitpid(descendant, &status, 0) < 0 &&
                       errno == EINTR) {
                }
                return kHelperFailureExit;
            }
            return kSuccessExit;
        }
        return kHelperUsageExit;
    } catch (...) {
        return kHelperFailureExit;
    }
}


void install_parent_boundary_sentinels_or_throw() {
    if (::setenv("ANONSYNC_SELF_EXEC_PARENT_LEAK", "must-not-cross", 1) != 0) {
        throw std::runtime_error("could not install parent environment sentinel");
    }

    struct sigaction ignored {};
    ignored.sa_handler = SIG_IGN;
    if (::sigemptyset(&ignored.sa_mask) != 0 ||
        ::sigaction(SIGUSR1, &ignored, nullptr) != 0) {
        throw std::runtime_error("could not install parent signal-disposition sentinel");
    }

    sigset_t blocked {};
    if (::sigemptyset(&blocked) != 0 ||
        ::sigaddset(&blocked, SIGUSR2) != 0 ||
        ::sigprocmask(SIG_BLOCK, &blocked, nullptr) != 0) {
        throw std::runtime_error("could not install parent signal-mask sentinel");
    }
}

void test_exact_exit_and_boundary(const fs::path& executable,
                                  std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_or_throw(
        executable, {std::string(kHelperFlag), "return-exact"});
    require(child.active() && child.process_id() > 0,
            "spawn did not return one live child owner", checks);
    anonsync::test::SelfExecTestProcess transferred(std::move(child));
    require(!child.active() && transferred.active(),
            "move construction duplicated or lost child authority", checks);
    transferred.wait_for_exact_exit(kSuccessExit, 5s,
                                    "self-exec exact-exit helper");
    require(!transferred.active(),
            "exact-exit wait did not consume the process owner", checks);
}

void test_move_assignment_consumes_displaced_owner(
    const fs::path& executable,
    std::uint64_t& checks) {
    auto displaced = spawn_self_exec_test_process_or_throw(
        executable,
        {std::string(kHelperFlag), "hang-until-parent-kills"});
    const pid_t displaced_pid = displaced.process_id();
    auto replacement = spawn_self_exec_test_process_or_throw(
        executable, {std::string(kHelperFlag), "return-exact"});
    const pid_t replacement_pid = replacement.process_id();
    require(displaced_pid > 0 && replacement_pid > 0 &&
                displaced_pid != replacement_pid,
            "move-assignment fixture did not own two distinct helpers", checks);

    displaced = std::move(replacement);
    require(!replacement.active() && displaced.active() &&
                displaced.process_id() == replacement_pid,
            "move assignment duplicated or lost replacement authority", checks);

    int status = 0;
    errno = 0;
    const pid_t observed = ::waitpid(displaced_pid, &status, WNOHANG);
    require(observed == -1 && errno == ECHILD,
            "move assignment did not synchronously kill and reap the displaced helper",
            checks);

    displaced.wait_for_exact_exit(kSuccessExit, 5s,
                                  "self-exec move-assignment replacement");
    require(!displaced.active(),
            "move-assignment replacement owner was not consumed by wait", checks);
}

void test_exit_code_wait_returns_reviewed_status(
    const fs::path& executable, std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_or_throw(
        executable, {std::string(kHelperFlag), "return-exact"});
    const int exit_code = child.wait_for_exit_code(
        5s, "self-exec reviewed-outcome helper");
    require(exit_code == kSuccessExit,
            "exit-code wait did not return the helper's normal status", checks);
    require(!child.active(),
            "exit-code wait did not consume process authority", checks);
}

void test_timeout_kills_and_reaps(const fs::path& executable,
                                  std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_or_throw(
        executable,
        {std::string(kHelperFlag), "hang-until-parent-kills"});
    bool timed_out = false;
    try {
        child.wait_for_exact_exit(0, 75ms, "self-exec timeout helper");
    } catch (const std::exception& error) {
        timed_out = std::string_view(error.what()).find(
                        "timed out and was killed and reaped") !=
                    std::string_view::npos;
    }
    require(timed_out,
            "bounded wait did not report a killed-and-reaped timeout", checks);
    require(!child.active(),
            "timeout path retained a live or unreaped process owner", checks);
}

void test_destructor_kills_and_reaps(const fs::path& executable,
                                     std::uint64_t& checks) {
    pid_t abandoned_child = -1;
    {
        auto child = spawn_self_exec_test_process_or_throw(
            executable,
            {std::string(kHelperFlag), "hang-until-parent-kills"});
        abandoned_child = child.process_id();
    }

    int status = 0;
    errno = 0;
    const pid_t observed = ::waitpid(abandoned_child, &status, WNOHANG);
    require(observed == -1 && errno == ECHILD,
            "destructor did not synchronously kill and reap its helper", checks);
}

void test_captured_output_is_separate_and_exact(const fs::path& executable,
                                                std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_with_output_capture_or_throw(
        executable, {std::string(kHelperFlag), "emit-captured"});
    require(child.active() && child.captures_output(),
            "captured spawn did not return combined process/pipe authority",
            checks);
    anonsync::test::SelfExecTestProcess transferred(std::move(child));
    require(!child.active() && !child.captures_output() &&
                transferred.active() && transferred.captures_output(),
            "capture move construction duplicated or lost joint authority",
            checks);
    const anonsync::test::SelfExecTestProcessOutput output =
        transferred.wait_for_exact_exit_with_output(
            kSuccessExit, 5s, 4096, "self-exec captured-output helper");
    require(output.standard_output == "stdout-evidence\n",
            "captured stdout was not byte-exact", checks);
    require(output.standard_error == "stderr-evidence\n",
            "captured stderr was not byte-exact", checks);
    require(!transferred.active() && !transferred.captures_output(),
            "captured wait did not consume PID and both pipe owners", checks);
}

void test_successful_exit_kills_remaining_group(const fs::path& executable,
                                                std::uint64_t& checks) {
    ScopedChildSubreaper subreaper;
    auto child = spawn_self_exec_test_process_with_output_capture_or_throw(
        executable,
        {std::string(kHelperFlag), "return-with-lingering-descendant"});
    const anonsync::test::SelfExecTestProcessOutput output =
        child.wait_for_exact_exit_with_output(
            kSuccessExit, 5s, 4096,
            "self-exec successful-exit descendant-group helper");
    require(output.standard_error.empty(),
            "descendant-group helper emitted unexpected stderr", checks);
    const pid_t descendant =
        parse_exact_descendant_report_or_throw(output.standard_output);
    require(reap_exact_sigkill_bounded(descendant),
            "successful leader wait did not SIGKILL and expose the exact group descendant for reap",
            checks);
}

void test_post_reap_capture_timeout_consumes_group_authority(
    const fs::path& executable, std::uint64_t& checks) {
    ScopedChildSubreaper subreaper;
    ScopedPidReport report("anonsync-selfexec-post-reap-group");
    auto child = spawn_self_exec_test_process_with_output_capture_or_throw(
        executable,
        {std::string(kHelperFlag),
         "return-with-escaped-capture-descendant", report.native()});

    bool timed_out_after_reap = false;
    try {
        (void)child.wait_for_exact_exit_with_output(
            kSuccessExit, 1s, 4096,
            "self-exec post-reap capture authority");
    } catch (const std::exception& error) {
        timed_out_after_reap =
            std::string_view(error.what()).find(
                "timed out while draining captured output") !=
            std::string_view::npos;
    }

    const pid_t escaped = report.read_exact_or_throw();
    require(timed_out_after_reap && !child.active() &&
                !child.captures_output(),
            "post-reap self-exec timeout retained numeric or descriptor authority",
            checks);
    require(::getpgid(escaped) == escaped,
            "self-exec post-reap fixture did not retain one escaped output holder",
            checks);
    require(::kill(escaped, SIGKILL) == 0 &&
                reap_exact_sigkill_bounded(escaped),
            "escaped self-exec output holder could not be killed and exactly reaped",
            checks);
}

void test_large_capture_drains_while_child_runs(const fs::path& executable,
                                               std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_with_output_capture_or_throw(
        executable, {std::string(kHelperFlag), "emit-large-captured"});
    const anonsync::test::SelfExecTestProcessOutput output =
        child.wait_for_exact_exit_with_output(
            kSuccessExit, 5s, 5U * 1024U * 1024U,
            "self-exec large captured-output helper");
    require(output.standard_output.size() > 4096 &&
                output.standard_output.find_first_not_of('o') ==
                    std::string::npos,
            "over-capacity stdout capture was truncated or corrupted", checks);
    require(output.standard_error.size() > 4096 &&
                output.standard_error.find_first_not_of('e') ==
                    std::string::npos,
            "over-capacity stderr capture was truncated or corrupted", checks);
    require(!child.active() && !child.captures_output(),
            "large capture did not consume process and descriptor authority",
            checks);
}

void test_capture_overflow_kills_and_reaps(const fs::path& executable,
                                           std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_with_output_capture_or_throw(
        executable, {std::string(kHelperFlag), "emit-over-budget"});
    const pid_t child_pid = child.process_id();
    bool overflowed = false;
    try {
        (void)child.wait_for_exact_exit_with_output(
            kSuccessExit, 5s, 128, "self-exec capture-overflow helper");
    } catch (const std::exception& error) {
        overflowed = std::string_view(error.what()).find(
                         "captured stdout exceeded its 128-byte budget") !=
                     std::string_view::npos;
    }
    require(overflowed,
            "capture byte budget did not reject an overproducing helper",
            checks);
    require(!child.active() && !child.captures_output(),
            "capture overflow retained process or descriptor authority", checks);

    int status = 0;
    errno = 0;
    const pid_t observed = ::waitpid(child_pid, &status, WNOHANG);
    require(observed == -1 && errno == ECHILD,
            "capture overflow did not synchronously kill and reap the helper",
            checks);
}

void test_capture_timeout_drains_then_kills(const fs::path& executable,
                                            std::uint64_t& checks) {
    auto child = spawn_self_exec_test_process_with_output_capture_or_throw(
        executable, {std::string(kHelperFlag), "emit-then-hang"});
    bool timed_out = false;
    try {
        (void)child.wait_for_exact_exit_with_output(
            kSuccessExit, 75ms, 4096, "self-exec captured-timeout helper");
    } catch (const std::exception& error) {
        timed_out = std::string_view(error.what()).find(
                        "timed out while draining captured output") !=
                    std::string_view::npos;
    }
    require(timed_out,
            "capture-aware wait did not enforce its monotonic deadline", checks);
    require(!child.active() && !child.captures_output(),
            "capture timeout retained process or descriptor authority", checks);
}

void test_wait_api_mode_mismatch_is_fail_closed(const fs::path& executable,
                                                std::uint64_t& checks) {
    auto captured = spawn_self_exec_test_process_with_output_capture_or_throw(
        executable, {std::string(kHelperFlag), "emit-captured"});
    bool plain_wait_rejected = false;
    try {
        captured.wait_for_exact_exit(kSuccessExit, 5s,
                                     "captured child plain-wait misuse");
    } catch (const std::logic_error&) {
        plain_wait_rejected = true;
    }
    require(plain_wait_rejected && captured.active() &&
                captured.captures_output(),
            "plain wait consumed or accepted a captured child", checks);
    (void)captured.wait_for_exact_exit_with_output(
        kSuccessExit, 5s, 4096, "captured child corrected wait");

    auto plain = spawn_self_exec_test_process_or_throw(
        executable, {std::string(kHelperFlag), "return-exact"});
    bool capture_wait_rejected = false;
    try {
        (void)plain.wait_for_exact_exit_with_output(
            kSuccessExit, 5s, 4096, "plain child capture-wait misuse");
    } catch (const std::logic_error&) {
        capture_wait_rejected = true;
    }
    require(capture_wait_rejected && plain.active() &&
                !plain.captures_output(),
            "capture wait consumed or accepted an uncaptured child", checks);
    plain.wait_for_exact_exit(kSuccessExit, 5s, "plain child corrected wait");
}

void test_spawn_input_fences(const fs::path& executable,
                             std::uint64_t& checks) {
    bool missing_executable_rejected = false;
    try {
        (void)spawn_self_exec_test_process_or_throw(
            executable.parent_path() / "does-not-exist", {"probe"});
    } catch (const std::exception&) {
        missing_executable_rejected = true;
    }
    require(missing_executable_rejected,
            "spawn accepted a missing executable object", checks);

    bool aliased_executable_rejected = false;
    try {
        std::string aliased = executable.native();
        aliased.push_back('\0');
        aliased += "-ignored-suffix";
        (void)spawn_self_exec_test_process_or_throw(fs::path(aliased), {"probe"});
    } catch (const std::exception&) {
        aliased_executable_rejected = true;
    }
    require(aliased_executable_rejected,
            "spawn accepted an embedded-NUL executable alias", checks);

    bool foreign_executable_rejected = false;
    try {
        (void)spawn_self_exec_test_process_or_throw(fs::path("/bin/sh"), {"probe"});
    } catch (const std::exception&) {
        foreign_executable_rejected = true;
    }
    require(foreign_executable_rejected,
            "spawn accepted an executable object other than the running image", checks);

    bool oversized_argument_rejected = false;
    try {
        (void)spawn_self_exec_test_process_or_throw(
            executable, {std::string(4097, 'x')});
    } catch (const std::exception&) {
        oversized_argument_rejected = true;
    }
    require(oversized_argument_rejected,
            "spawn accepted an argument beyond its byte budget", checks);

    bool nul_argument_rejected = false;
    try {
        (void)spawn_self_exec_test_process_or_throw(
            executable, {std::string("ok\0hidden", 9)});
    } catch (const std::exception&) {
        nul_argument_rejected = true;
    }
    require(nul_argument_rejected,
            "spawn accepted an embedded-NUL helper argument", checks);
}

}  // namespace

int main(int argc, char** argv) {
    if (argc >= 2 && std::string_view(argv[1]) == kDescendantFlag) {
        return run_descendant(argc, argv);
    }
    if (argc >= 2 && std::string_view(argv[1]) == kHelperFlag) {
        return run_helper(argc, argv);
    }

    std::uint64_t checks = 0;
    try {
        if (argc != 1) {
            throw std::runtime_error(
                "usage: anonsync_self_exec_test_process_test");
        }
        install_parent_boundary_sentinels_or_throw();
        const fs::path executable = current_self_executable_or_throw();
        test_exact_exit_and_boundary(executable, checks);
        test_move_assignment_consumes_displaced_owner(executable, checks);
        test_exit_code_wait_returns_reviewed_status(executable, checks);
        test_timeout_kills_and_reaps(executable, checks);
        test_destructor_kills_and_reaps(executable, checks);
        const std::size_t descriptors_before_capture =
            count_parent_open_descriptors_or_throw();
        test_captured_output_is_separate_and_exact(executable, checks);
        test_successful_exit_kills_remaining_group(executable, checks);
        test_post_reap_capture_timeout_consumes_group_authority(executable,
                                                                checks);
        test_large_capture_drains_while_child_runs(executable, checks);
        test_capture_overflow_kills_and_reaps(executable, checks);
        test_capture_timeout_drains_then_kills(executable, checks);
        test_wait_api_mode_mismatch_is_fail_closed(executable, checks);
        require(count_parent_open_descriptors_or_throw() ==
                    descriptors_before_capture,
                "capture paths leaked a parent descriptor", checks);
        test_spawn_input_fences(executable, checks);
        std::cout << "anonsync_self_exec_test_process_test checks=" << checks
                  << "\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "anonsync_self_exec_test_process_test failure after "
                  << checks << " checks: " << error.what() << "\n";
        return 2;
    }
}
