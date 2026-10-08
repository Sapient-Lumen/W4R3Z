#include "sync_bounded_regular_file.hpp"

#include <array>
#include <cerrno>
#include <cstdarg>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>

#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace {

using anonsync::read_sync_bounded_regular_file_no_symlink_or_throw;

constexpr int kScriptedDescriptor = 73;

enum class Operation : unsigned char { open, fstat, read, close };

struct Action final {
    Operation operation = Operation::open;
    int integer_result = 0;
    int error = 0;
    struct stat status {};
    const char* bytes = nullptr;
    std::size_t byte_count = 0;
    std::size_t expected_request = 0;
};

struct Script final {
    std::array<Action, 24> actions{};
    std::size_t size = 0;
    std::size_t cursor = 0;
    bool armed = false;
    bool mismatch = false;
    int observed_open_flags = 0;
    off_t expected_pread_offset = 0;
    std::size_t pread_calls = 0;

    void reset() noexcept {
        size = 0;
        cursor = 0;
        armed = false;
        mismatch = false;
        observed_open_flags = 0;
        expected_pread_offset = 0;
        pread_calls = 0;
    }

    Action* next(Operation expected) noexcept {
        if (!armed || cursor >= size ||
            actions[cursor].operation != expected) {
            mismatch = true;
            errno = EPROTO;
            return nullptr;
        }
        return &actions[cursor++];
    }

    void push(Action action) {
        if (size >= actions.size()) {
            throw std::runtime_error("syscall script capacity exceeded");
        }
        actions[size++] = action;
    }
};

Script g_script;

[[nodiscard]] struct stat regular_status(off_t size,
                                         long modification_nanoseconds = 100,
                                         long change_nanoseconds = 200) {
    struct stat result {};
    result.st_mode = S_IFREG | 0600;
    result.st_dev = 11;
    result.st_ino = 22;
    result.st_size = size;
    result.st_nlink = 1;
#if defined(__linux__)
    result.st_mtim.tv_sec = 1000;
    result.st_mtim.tv_nsec = modification_nanoseconds;
    result.st_ctim.tv_sec = 2000;
    result.st_ctim.tv_nsec = change_nanoseconds;
#else
#error "This deterministic syscall oracle is Linux-only"
#endif
    return result;
}

[[nodiscard]] Action open_action(int result = kScriptedDescriptor,
                                 int error = 0) {
    Action action;
    action.operation = Operation::open;
    action.integer_result = result;
    action.error = error;
    return action;
}

[[nodiscard]] Action stat_action(const struct stat& status,
                                 int result = 0,
                                 int error = 0) {
    Action action;
    action.operation = Operation::fstat;
    action.integer_result = result;
    action.error = error;
    action.status = status;
    return action;
}

[[nodiscard]] Action read_action(const char* bytes,
                                 std::size_t byte_count,
                                 std::size_t expected_request,
                                 int result = -2,
                                 int error = 0) {
    Action action;
    action.operation = Operation::read;
    action.integer_result = result == -2
                                ? static_cast<int>(byte_count)
                                : result;
    action.error = error;
    action.bytes = bytes;
    action.byte_count = byte_count;
    action.expected_request = expected_request;
    return action;
}

[[nodiscard]] Action close_action(int result = 0, int error = 0) {
    Action action;
    action.operation = Operation::close;
    action.integer_result = result;
    action.error = error;
    return action;
}

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

class ArmedScript final {
public:
    ArmedScript() { g_script.armed = true; }
    ArmedScript(const ArmedScript&) = delete;
    ArmedScript& operator=(const ArmedScript&) = delete;
    ~ArmedScript() { g_script.armed = false; }
};

[[nodiscard]] bool script_consumed_exactly() noexcept {
    return !g_script.mismatch && g_script.cursor == g_script.size;
}

[[nodiscard]] std::string run_success(std::uint64_t maximum_bytes) {
    const ArmedScript armed;
    return read_sync_bounded_regular_file_no_symlink_or_throw(
        "/scripted/bounded-read", maximum_bytes, "scripted read");
}

[[nodiscard]] std::string run_rejection(std::uint64_t maximum_bytes) {
    try {
        const ArmedScript armed;
        (void)read_sync_bounded_regular_file_no_symlink_or_throw(
            "/scripted/bounded-read", maximum_bytes, "scripted read");
        return {};
    } catch (const std::exception& error) {
        return error.what();
    }
}

void begin_script() { g_script.reset(); }

void test_stable_read_and_open_flags(TestState& test) {
    begin_script();
    const struct stat stable = regular_status(3);
    g_script.push(open_action());
    g_script.push(stat_action(stable));
    g_script.push(read_action("abc", 3, 11));
    g_script.push(read_action(nullptr, 0, 8));
    g_script.push(stat_action(stable));
    g_script.push(close_action());

    const std::string bytes = run_success(10);
    const int required_flags = O_NONBLOCK | O_NOFOLLOW;
    test.require(bytes == "abc", "stable descriptor bytes are returned exactly");
    test.require((g_script.observed_open_flags & required_flags) == required_flags,
                 "open carries nonblocking and final-symlink rejection flags");
#ifdef O_CLOEXEC
    test.require((g_script.observed_open_flags & O_CLOEXEC) != 0,
                 "open atomically requests close-on-exec");
#endif
#ifdef O_NOCTTY
    test.require((g_script.observed_open_flags & O_NOCTTY) != 0,
                 "open cannot acquire a controlling terminal");
#endif
    test.require(g_script.pread_calls == 2 &&
                     g_script.expected_pread_offset == 3,
                 "positional reads begin at byte zero and advance only by accepted bytes");
    test.require(script_consumed_exactly(),
                 "stable read consumes open, pre-stat, positional EOF, post-stat, and close in order");
}

void test_non_regular_and_initial_size_rejection(TestState& test) {
    begin_script();
    struct stat fifo = regular_status(0);
    fifo.st_mode = S_IFIFO | 0600;
    g_script.push(open_action());
    g_script.push(stat_action(fifo));
    g_script.push(close_action());
    const std::string fifo_error = run_rejection(10);
    test.require(fifo_error.find("not a regular file") != std::string::npos,
                 "non-regular descriptors are rejected before read");
    test.require(script_consumed_exactly(),
                 "non-regular rejection closes without issuing read");

    begin_script();
    g_script.push(open_action());
    g_script.push(stat_action(regular_status(11)));
    g_script.push(close_action());
    const std::string large_error = run_rejection(10);
    test.require(large_error.find("exceeds bounded read limit") !=
                     std::string::npos,
                 "initial descriptor size above the ceiling is rejected");
    test.require(script_consumed_exactly(),
                 "initial oversize rejection closes without issuing read");
}

void test_growth_and_snapshot_rejection(TestState& test) {
    begin_script();
    const struct stat initial = regular_status(3);
    g_script.push(open_action());
    g_script.push(stat_action(initial));
    g_script.push(read_action("abcd", 4, 4));
    g_script.push(close_action());
    const std::string growth_error = run_rejection(3);
    test.require(growth_error.find("exceeds bounded read limit") !=
                     std::string::npos,
                 "a one-byte sentinel rejects growth beyond the ceiling");
    test.require(script_consumed_exactly(),
                 "growth rejection closes at the first over-ceiling read");

    begin_script();
    g_script.push(open_action());
    g_script.push(stat_action(initial));
    g_script.push(read_action("abc", 3, 11));
    g_script.push(read_action(nullptr, 0, 8));
    g_script.push(stat_action(regular_status(4)));
    g_script.push(close_action());
    const std::string size_error = run_rejection(10);
    test.require(size_error.find("changed while") != std::string::npos,
                 "post-read size drift rejects a prefix that reached EOF");
    test.require(script_consumed_exactly(),
                 "size-drift proof performs the final descriptor inspection");

    begin_script();
    g_script.push(open_action());
    g_script.push(stat_action(initial));
    g_script.push(read_action("abc", 3, 11));
    g_script.push(read_action(nullptr, 0, 8));
    g_script.push(stat_action(regular_status(3, 101, 200)));
    g_script.push(close_action());
    const std::string time_error = run_rejection(10);
    test.require(time_error.find("changed while") != std::string::npos,
                 "same-size modification metadata drift rejects unstable bytes");
    test.require(script_consumed_exactly(),
                 "metadata-drift rejection still closes the exact descriptor");
}

void test_retry_and_error_composition(TestState& test) {
    begin_script();
    const struct stat stable = regular_status(3);
    g_script.push(open_action());
    g_script.push(stat_action(stable));
    g_script.push(read_action(nullptr, 0, 11, -1, EINTR));
    g_script.push(read_action("abc", 3, 11));
    g_script.push(read_action(nullptr, 0, 8));
    g_script.push(stat_action(stable));
    g_script.push(close_action());
    test.require(run_success(10) == "abc",
                 "EINTR retries the same descriptor read");
    test.require(script_consumed_exactly(),
                 "EINTR retry preserves syscall ordering");

    begin_script();
    g_script.push(open_action());
    g_script.push(stat_action(stable));
    g_script.push(read_action(nullptr, 0, 11, -1, EIO));
    g_script.push(close_action(-1, EBADF));
    const std::string read_error = run_rejection(10);
    test.require(read_error.find("read failed") != std::string::npos &&
                     read_error.find("close failed") == std::string::npos,
                 "a primary read failure is not overwritten by cleanup failure");
    test.require(script_consumed_exactly(),
                 "read failure attempts exactly one descriptor cleanup");

    begin_script();
    g_script.push(open_action());
    g_script.push(stat_action(stable));
    g_script.push(read_action("abc", 3, 11));
    g_script.push(read_action(nullptr, 0, 8));
    g_script.push(stat_action({}, -1, EIO));
    g_script.push(close_action());
    const std::string final_stat_error = run_rejection(10);
    test.require(final_stat_error.find("final fstat failed") !=
                     std::string::npos,
                 "final descriptor inspection failures reject the observation");
    test.require(script_consumed_exactly(),
                 "final inspection failure closes the descriptor");

    begin_script();
    g_script.push(open_action());
    g_script.push(stat_action(stable));
    g_script.push(read_action("abc", 3, 11));
    g_script.push(read_action(nullptr, 0, 8));
    g_script.push(stat_action(stable));
    g_script.push(close_action(-1, EIO));
    const std::string close_error = run_rejection(10);
    test.require(close_error.find("close failed") != std::string::npos,
                 "close failure after an otherwise valid read is propagated");
    test.require(script_consumed_exactly(),
                 "normal close failure consumes the terminal close action");

    begin_script();
    g_script.push(open_action(-1, ENOENT));
    const std::string open_error = run_rejection(10);
    test.require(open_error.find("open failed") != std::string::npos,
                 "open failure rejects without manufacturing a descriptor");
    test.require(script_consumed_exactly(),
                 "open failure performs no close against an unowned descriptor");
}

}  // namespace

extern "C" int __real_open(const char* path, int flags, ...);
extern "C" int __real_fstat(int descriptor, struct stat* status);
extern "C" ssize_t __real_pread(int descriptor, void* buffer, size_t count, off_t offset);
extern "C" int __real_close(int descriptor);

extern "C" int __wrap_open(const char* path, int flags, ...) {
    if (!g_script.armed) {
        if ((flags & O_CREAT) != 0) {
            va_list arguments;
            va_start(arguments, flags);
            const mode_t mode = va_arg(arguments, mode_t);
            va_end(arguments);
            return __real_open(path, flags, mode);
        }
        return __real_open(path, flags);
    }
    Action* action = g_script.next(Operation::open);
    if (action == nullptr) return -1;
    g_script.observed_open_flags = flags;
    if (std::strcmp(path, "/scripted/bounded-read") != 0) {
        g_script.mismatch = true;
        errno = EPROTO;
        return -1;
    }
    errno = action->error;
    return action->integer_result;
}

extern "C" int __wrap_fstat(int descriptor, struct stat* status) {
    if (!g_script.armed) return __real_fstat(descriptor, status);
    Action* action = g_script.next(Operation::fstat);
    if (action == nullptr) return -1;
    if (descriptor != kScriptedDescriptor || status == nullptr) {
        g_script.mismatch = true;
        errno = EPROTO;
        return -1;
    }
    if (action->integer_result == 0) *status = action->status;
    errno = action->error;
    return action->integer_result;
}

extern "C" ssize_t __wrap_pread(int descriptor, void* buffer, size_t count,
                                  off_t offset) {
    if (!g_script.armed) return __real_pread(descriptor, buffer, count, offset);
    Action* action = g_script.next(Operation::read);
    if (action == nullptr) return -1;
    if (descriptor != kScriptedDescriptor || buffer == nullptr ||
        count != action->expected_request ||
        offset != g_script.expected_pread_offset) {
        g_script.mismatch = true;
        errno = EPROTO;
        return -1;
    }
    if (action->integer_result > 0) {
        const std::size_t amount =
            static_cast<std::size_t>(action->integer_result);
        if (amount != action->byte_count || amount > count ||
            action->bytes == nullptr) {
            g_script.mismatch = true;
            errno = EPROTO;
            return -1;
        }
        std::memcpy(buffer, action->bytes, amount);
        g_script.expected_pread_offset += static_cast<off_t>(amount);
    }
    ++g_script.pread_calls;
    errno = action->error;
    return static_cast<ssize_t>(action->integer_result);
}

extern "C" int __wrap_close(int descriptor) {
    if (!g_script.armed) return __real_close(descriptor);
    Action* action = g_script.next(Operation::close);
    if (action == nullptr) return -1;
    if (descriptor != kScriptedDescriptor) {
        g_script.mismatch = true;
        errno = EPROTO;
        return -1;
    }
    errno = action->error;
    return action->integer_result;
}

int main() {
    try {
        TestState test;
        test_stable_read_and_open_flags(test);
        test_non_regular_and_initial_size_rejection(test);
        test_growth_and_snapshot_rejection(test);
        test_retry_and_error_composition(test);
        std::cout << "sync bounded regular file syscall tests passed: "
                  << test.passed << "/" << (test.passed + test.failed) << "\n";
        return test.failed == 0 ? 0 : 1;
    } catch (const std::exception& error) {
        g_script.armed = false;
        std::cerr << "FATAL: " << error.what() << "\n";
        return 2;
    }
}
