#include "inherited_test_process.hpp"

#include <cerrno>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <type_traits>
#include <utility>

#include <fcntl.h>
#include <sys/wait.h>
#include <unistd.h>
#if defined(__linux__)
#include <sys/prctl.h>
#endif

namespace {

namespace fs = std::filesystem;
using namespace std::chrono_literals;

constexpr unsigned kFixtureFailSafeSeconds = 15;
using anonsync::test::InheritedTestProcess;
using anonsync::test::InheritedTestProcessOutput;
using anonsync::test::kInheritedTestProcessInvalidReturnExitCode;
using anonsync::test::kInheritedTestProcessUnhandledExceptionExitCode;
using anonsync::test::spawn_inherited_test_process_or_throw;
using anonsync::test::spawn_inherited_test_process_with_output_capture_or_throw;

static_assert(!std::is_copy_constructible_v<InheritedTestProcess>);
static_assert(!std::is_copy_assignable_v<InheritedTestProcess>);
static_assert(std::is_nothrow_move_constructible_v<InheritedTestProcess>);
static_assert(std::is_nothrow_move_assignable_v<InheritedTestProcess>);

void require(bool condition, std::string_view label, std::uint64_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(label));
}

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

#if defined(__linux__)
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

    [[nodiscard]] const char* child_path() const noexcept {
        return native_.c_str();
    }

    [[nodiscard]] pid_t read_exact_or_throw() const {
        const int descriptor =
            ::open(native_.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        if (descriptor < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "open inherited escaped-child PID report");
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
                    "read inherited escaped-child PID report");
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
                "inherited escaped-child PID report was not exact");
        }
        if (trailing < 0) {
            throw std::system_error(
                trailing_error, std::generic_category(),
                "finish inherited escaped-child PID report");
        }
        if (value <= 0) {
            throw std::runtime_error(
                "inherited escaped-child PID report was not positive");
        }
        return value;
    }

private:
    fs::path path_;
    std::string native_;
};

bool write_pid_report_noexcept(const char* path, pid_t value) noexcept {
    const int descriptor = ::open(
        path, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (descriptor < 0) return false;
    const bool written = write_exact(descriptor, &value, sizeof(value));
    const bool synchronized = written && ::fdatasync(descriptor) == 0;
    const bool closed = ::close(descriptor) == 0;
    return written && synchronized && closed;
}
#endif

void test_exact_exit_and_move(std::uint64_t& checks) {
    auto child = spawn_inherited_test_process_or_throw(
        [] { return 37; }, "inherited exact-exit child");
    require(child.active() && child.process_id() > 0 &&
                !child.captures_output(),
            "plain spawn did not return one live owner", checks);
    InheritedTestProcess moved(std::move(child));
    require(!child.active() && moved.active(),
            "move construction duplicated or lost inherited authority", checks);
    moved.wait_for_exact_exit(37, 5s, "inherited exact-exit child");
    require(!moved.active(),
            "exact wait did not consume inherited authority", checks);
}

void test_child_exception_and_invalid_return(std::uint64_t& checks) {
    auto throwing = spawn_inherited_test_process_or_throw(
        []() -> int { throw std::runtime_error("child exception"); },
        "inherited throwing child");
    throwing.wait_for_exact_exit(
        kInheritedTestProcessUnhandledExceptionExitCode, 5s,
        "inherited throwing child");
    require(!throwing.active(),
            "exception status did not consume the owner", checks);

    auto invalid = spawn_inherited_test_process_or_throw(
        [] { return 300; }, "inherited invalid-return child");
    invalid.wait_for_exact_exit(kInheritedTestProcessInvalidReturnExitCode, 5s,
                                "inherited invalid-return child");
    require(!invalid.active(),
            "invalid-return status did not consume the owner", checks);
}

void test_capture_is_exact_and_bounded(std::uint64_t& checks) {
    constexpr char evidence[] = {'A', '\0', 'B', '\n'};
    auto child = spawn_inherited_test_process_with_output_capture_or_throw(
        [&](int descriptor) {
            return write_exact(descriptor, evidence, sizeof(evidence)) ? 0 : 91;
        },
        "inherited exact capture");
    require(child.active() && child.captures_output(),
            "captured spawn did not combine process and pipe authority", checks);
    const InheritedTestProcessOutput output =
        child.wait_for_exit_with_output(5s, sizeof(evidence),
                                        "inherited exact capture");
    require(WIFEXITED(output.wait_status) &&
                WEXITSTATUS(output.wait_status) == 0,
            "captured child returned the wrong status", checks);
    require(output.bytes.size() == sizeof(evidence) &&
                std::memcmp(output.bytes.data(), evidence,
                            sizeof(evidence)) == 0,
            "captured inherited bytes were not exact", checks);
    require(!child.active(),
            "captured wait retained process or descriptor authority", checks);

    auto overflow = spawn_inherited_test_process_with_output_capture_or_throw(
        [](int descriptor) {
            const std::string bytes(4096, 'x');
            return write_exact(descriptor, bytes.data(), bytes.size()) ? 0 : 92;
        },
        "inherited overflow capture");
    const pid_t overflow_pid = overflow.process_id();
    bool rejected = false;
    try {
        (void)overflow.wait_for_exit_with_output(
            5s, 16, "inherited overflow capture");
    } catch (const std::exception& error) {
        rejected = std::string_view(error.what()).find("exceeded") !=
                   std::string_view::npos;
    }
    require(rejected && !overflow.active(),
            "capture overflow did not fail closed", checks);
    int status = 0;
    errno = 0;
    require(::waitpid(overflow_pid, &status, WNOHANG) == -1 && errno == ECHILD,
            "capture overflow did not reap the child", checks);
}

void test_wait_mode_mismatch_is_recoverable(std::uint64_t& checks) {
    auto captured = spawn_inherited_test_process_with_output_capture_or_throw(
        [](int) { return 0; }, "captured mismatch child");
    bool plain_rejected = false;
    try {
        (void)captured.wait_for_exit(5s, "captured mismatch child");
    } catch (const std::logic_error&) {
        plain_rejected = true;
    }
    require(plain_rejected && captured.active(),
            "plain wait consumed a captured child", checks);
    (void)captured.wait_for_exit_with_output(
        5s, 1, "captured mismatch child corrected wait");

    auto plain = spawn_inherited_test_process_or_throw(
        [] { return 0; }, "plain mismatch child");
    bool capture_rejected = false;
    try {
        (void)plain.wait_for_exit_with_output(5s, 1,
                                              "plain mismatch child");
    } catch (const std::logic_error&) {
        capture_rejected = true;
    }
    require(capture_rejected && plain.active(),
            "capture wait consumed a plain child", checks);
    plain.wait_for_exact_exit(0, 5s, "plain mismatch child corrected wait");
}

void test_timeout_and_destructor_reap(std::uint64_t& checks) {
    auto child = spawn_inherited_test_process_or_throw(
        [] {
            (void)::alarm(kFixtureFailSafeSeconds);
            for (;;) (void)::pause();
            return 0;
        },
        "inherited timeout child");
    const pid_t timed_pid = child.process_id();
    bool timed_out = false;
    try {
        (void)child.wait_for_exit(75ms, "inherited timeout child");
    } catch (const std::exception& error) {
        timed_out = std::string_view(error.what()).find(
                        "timed out and was killed and reaped") !=
                    std::string_view::npos;
    }
    require(timed_out && !child.active(),
            "timeout did not synchronously consume the owner", checks);
    int status = 0;
    errno = 0;
    require(::waitpid(timed_pid, &status, WNOHANG) == -1 && errno == ECHILD,
            "timeout did not reap the inherited child", checks);

    pid_t abandoned = -1;
    {
        auto owned = spawn_inherited_test_process_or_throw(
            [] {
                (void)::alarm(kFixtureFailSafeSeconds);
                for (;;) (void)::pause();
                return 0;
            },
            "inherited destructor child");
        abandoned = owned.process_id();
    }
    errno = 0;
    require(::waitpid(abandoned, &status, WNOHANG) == -1 && errno == ECHILD,
            "destructor did not synchronously kill and reap", checks);
}

void test_external_reap_relinquishes_numeric_authority(
    std::uint64_t& checks) {
    auto child = spawn_inherited_test_process_or_throw(
        [] { return 0; }, "externally reaped inherited child");
    const pid_t child_pid = child.process_id();
    int status = 0;
    while (::waitpid(child_pid, &status, 0) < 0 && errno == EINTR) {
    }
    bool rejected = false;
    try {
        (void)child.wait_for_exit(5s, "externally reaped inherited child");
    } catch (const std::system_error& error) {
        rejected = error.code().value() == ECHILD;
    }
    require(rejected && !child.active(),
            "ECHILD did not relinquish potentially reusable PID authority",
            checks);
}

void test_nested_child_stays_in_top_level_group(std::uint64_t& checks) {
    auto outer = spawn_inherited_test_process_or_throw(
        [] {
            const pid_t outer_pid = ::getpid();
            if (::getpgrp() != outer_pid) return 91;
            auto inner = spawn_inherited_test_process_or_throw(
                [outer_pid] {
                    return ::getpgrp() == outer_pid &&
                                   ::getpid() != outer_pid
                               ? 0
                               : 92;
                },
                "nested inherited child");
            const int status = inner.wait_for_exit(5s, "nested inherited child");
            return WIFEXITED(status) && WEXITSTATUS(status) == 0 ? 0 : 93;
        },
        "top-level inherited child");
    outer.wait_for_exact_exit(0, 5s, "top-level inherited child");
    require(!outer.active(),
            "nested process-group proof retained authority", checks);
}

#if defined(__linux__)
void test_successful_exit_kills_remaining_group(std::uint64_t& checks) {
    ScopedChildSubreaper subreaper;
    auto outer = spawn_inherited_test_process_with_output_capture_or_throw(
        [](int descriptor) {
            // Deliberately leak the nested owner in this raw-fork child. The
            // wrapper exits with _exit(), so no destructor runs; the parent
            // owner must terminate the still-live group member after observing
            // the outer leader's successful status.
            auto* descendant_owner = new InheritedTestProcess(
                spawn_inherited_test_process_or_throw(
                    [] {
                        (void)::alarm(kFixtureFailSafeSeconds);
                        for (;;) (void)::pause();
                        return 0;
                    },
                    "inherited lingering descendant"));
            const pid_t descendant = descendant_owner->process_id();
            return descendant > 0 &&
                           write_exact(descriptor, &descendant,
                                       sizeof(descendant))
                       ? 0
                       : 94;
        },
        "inherited successful-exit descendant group");
    const InheritedTestProcessOutput output = outer.wait_for_exit_with_output(
        5s, sizeof(pid_t), "inherited successful-exit descendant group");
    require(WIFEXITED(output.wait_status) &&
                WEXITSTATUS(output.wait_status) == 0 &&
                output.bytes.size() == sizeof(pid_t),
            "inherited descendant-group leader did not return exact evidence",
            checks);
    pid_t descendant = -1;
    std::memcpy(&descendant, output.bytes.data(), sizeof(descendant));
    require(descendant > 0 && reap_exact_sigkill_bounded(descendant),
            "successful inherited leader wait did not SIGKILL and expose the exact group descendant for reap",
            checks);
}


void test_post_reap_capture_timeout_consumes_group_authority(
    std::uint64_t& checks) {
    ScopedChildSubreaper subreaper;
    ScopedPidReport report("anonsync-inherited-post-reap-group");
    const char* const report_path = report.child_path();

    auto outer = spawn_inherited_test_process_with_output_capture_or_throw(
        [report_path](int) {
            // This descendant deliberately leaves the top-level group while
            // retaining the inherited output descriptor. The outer leader can
            // therefore be observed, its original group can be killed, and the
            // exact leader can be reaped while EOF is still impossible.
            auto* escaped_owner = new InheritedTestProcess(
                spawn_inherited_test_process_or_throw(
                    [] {
                        if (::setpgid(0, 0) != 0) return 95;
                        (void)::alarm(kFixtureFailSafeSeconds);
                        for (;;) (void)::pause();
                        return 0;
                    },
                    "inherited escaped capture descendant"));
            const pid_t escaped = escaped_owner->process_id();
            bool escaped_group_observed = false;
            for (int attempt = 0; attempt != 250; ++attempt) {
                if (::getpgid(escaped) == escaped) {
                    escaped_group_observed = true;
                    break;
                }
                (void)::usleep(1000);
            }
            return escaped_group_observed &&
                           write_pid_report_noexcept(report_path, escaped)
                       ? 0
                       : 96;
        },
        "inherited post-reap capture authority");

    bool timed_out_after_reap = false;
    try {
        (void)outer.wait_for_exit_with_output(
            1s, 1, "inherited post-reap capture authority");
    } catch (const std::exception& error) {
        timed_out_after_reap =
            std::string_view(error.what()).find(
                "timed out while collecting inherited output") !=
            std::string_view::npos;
    }
    const pid_t escaped = report.read_exact_or_throw();
    require(timed_out_after_reap && !outer.active(),
            "post-reap capture timeout retained numeric or descriptor authority",
            checks);
    require(::getpgid(escaped) == escaped,
            "post-reap fixture did not retain one escaped output holder",
            checks);
    require(::kill(escaped, SIGKILL) == 0 &&
                reap_exact_sigkill_bounded(escaped),
            "escaped inherited output holder could not be killed and exactly reaped",
            checks);
}
#endif

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        test_exact_exit_and_move(checks);
        test_child_exception_and_invalid_return(checks);
        test_capture_is_exact_and_bounded(checks);
        test_wait_mode_mismatch_is_recoverable(checks);
        test_timeout_and_destructor_reap(checks);
        test_external_reap_relinquishes_numeric_authority(checks);
        test_nested_child_stays_in_top_level_group(checks);
#if defined(__linux__)
        test_successful_exit_kills_remaining_group(checks);
        test_post_reap_capture_timeout_consumes_group_authority(checks);
#endif
        std::cout << "anonsync_inherited_test_process_test checks=" << checks
                  << " failures=0\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "anonsync_inherited_test_process_test checks=" << checks
                  << " failures=1 reason=" << error.what() << "\n";
        return 1;
    }
}
