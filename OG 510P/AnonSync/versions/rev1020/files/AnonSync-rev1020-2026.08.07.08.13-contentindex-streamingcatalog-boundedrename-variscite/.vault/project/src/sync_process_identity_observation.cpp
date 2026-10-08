#include "sync_process_identity_observation.hpp"

#include "sync_process_identity_observation_internal.hpp"
#include "sync_system_epoch_identity.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <utility>

#if defined(__linux__)
#include <fcntl.h>
#include <poll.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <unistd.h>
#elif defined(_WIN32)
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <unistd.h>
#endif

namespace anonsync {
namespace {

constexpr std::string_view kLinuxFormat =
    "linux-proc-starttime-v1";
constexpr std::string_view kWindowsFormat =
    "windows-creation-filetime-v1";
constexpr std::string_view kUnavailableFormat =
    "process-incarnation-unavailable-v1";
constexpr std::size_t kMaximumProcTextBytes = 4096;

class ProcessNotRunningError final : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

[[nodiscard]] std::string decimal_u64(std::uint64_t value) {
    return std::to_string(value);
}

#if defined(__linux__)

class OwnedDescriptor final {
public:
    explicit OwnedDescriptor(int value = -1) noexcept : value_(value) {}
    OwnedDescriptor(const OwnedDescriptor&) = delete;
    OwnedDescriptor& operator=(const OwnedDescriptor&) = delete;
    OwnedDescriptor(OwnedDescriptor&& other) noexcept
        : value_(std::exchange(other.value_, -1)) {}
    OwnedDescriptor& operator=(OwnedDescriptor&& other) noexcept {
        if (this != &other) {
            close_noexcept();
            value_ = std::exchange(other.value_, -1);
        }
        return *this;
    }
    ~OwnedDescriptor() { close_noexcept(); }

    [[nodiscard]] int get() const noexcept { return value_; }
    [[nodiscard]] bool valid() const noexcept { return value_ >= 0; }

private:
    void close_noexcept() noexcept {
        if (value_ < 0) return;
        const int saved = errno;
        (void)::close(value_);
        errno = saved;
        value_ = -1;
    }

    int value_ = -1;
};

[[nodiscard]] std::system_error errno_error(const std::string& label,
                                            int error_number) {
    return std::system_error(error_number, std::generic_category(), label);
}

[[nodiscard]] std::string read_small_file_or_throw(const std::string& path,
                                                   const std::string& label) {
    OwnedDescriptor descriptor(::open(path.c_str(), O_RDONLY | O_CLOEXEC |
                                                       O_NOFOLLOW | O_NONBLOCK));
    if (!descriptor.valid()) throw errno_error(label + " open", errno);

    std::string bytes;
    bytes.reserve(256);
    std::array<char, 512> buffer{};
    for (;;) {
        const ssize_t count = ::read(descriptor.get(), buffer.data(), buffer.size());
        if (count < 0 && errno == EINTR) continue;
        if (count < 0) throw errno_error(label + " read", errno);
        if (count == 0) break;
        const auto amount = static_cast<std::size_t>(count);
        if (bytes.size() > kMaximumProcTextBytes - amount) {
            throw std::runtime_error(label + " exceeds the bounded observation size");
        }
        bytes.append(buffer.data(), amount);
    }
    if (bytes.empty()) throw std::runtime_error(label + " is empty");
    if (bytes.find('\0') != std::string::npos) {
        throw std::runtime_error(label + " contains an embedded NUL");
    }
    return bytes;
}

[[nodiscard]] std::string current_linux_boot_id_or_throw() {
    const SyncSystemBootIdentityObservation observation =
        observe_sync_system_boot_identity_or_throw(
            "Linux process identity boot-id observation");
    if (observation.kind != SyncSystemBootIdentityKind::LinuxProcBootId) {
        throw std::runtime_error(
            std::string("Linux process identity boot-id source is unavailable: ") +
            sync_system_boot_identity_kind_name(observation.kind));
    }
    return observation.boot_id;
}

[[nodiscard]] detail::LinuxProcStatIdentity read_linux_proc_identity_or_throw(
    std::uint64_t process_id) {
    if (process_id == 0 ||
        process_id > static_cast<std::uint64_t>(
                         std::numeric_limits<pid_t>::max())) {
        throw std::runtime_error("Linux process identity PID is outside pid_t range");
    }
    const std::string path =
        "/proc/" + decimal_u64(process_id) + "/stat";
    const std::string bytes =
        read_small_file_or_throw(path, "Linux process stat observation");
    return detail::parse_linux_proc_pid_stat_identity_or_throw(bytes,
                                                                process_id);
}

[[nodiscard]] bool terminal_linux_process_state(char state) noexcept {
    return state == 'Z' || state == 'X' || state == 'x';
}

[[nodiscard]] int open_pidfd_noexcept(pid_t pid) noexcept {
#if defined(SYS_pidfd_open)
    return static_cast<int>(::syscall(SYS_pidfd_open, pid, 0U));
#else
    (void)pid;
    errno = ENOSYS;
    return -1;
#endif
}

[[nodiscard]] bool pidfd_reports_exit_noexcept(int descriptor,
                                               bool& indeterminate) noexcept {
    struct pollfd item {};
    item.fd = descriptor;
    item.events = POLLIN;
    for (;;) {
        const int rc = ::poll(&item, 1, 0);
        if (rc < 0 && errno == EINTR) continue;
        if (rc < 0) {
            indeterminate = true;
            return false;
        }
        if (rc == 0) return false;
        if ((item.revents & (POLLERR | POLLNVAL)) != 0) {
            indeterminate = true;
            return false;
        }
        return (item.revents & (POLLIN | POLLHUP)) != 0;
    }
}

#endif

#if defined(_WIN32)

[[nodiscard]] std::uint64_t filetime_u64(const FILETIME& value) noexcept {
    return (static_cast<std::uint64_t>(value.dwHighDateTime) << 32U) |
           static_cast<std::uint64_t>(value.dwLowDateTime);
}

[[nodiscard]] SyncProcessIdentityObservation observe_windows_process_or_throw(
    DWORD process_id) {
    HANDLE process = ::OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE,
                                   process_id);
    if (process == nullptr) {
        const DWORD error_number = ::GetLastError();
        if (error_number == ERROR_INVALID_PARAMETER) {
            throw ProcessNotRunningError(
                "the claimed Windows PID does not exist");
        }
        throw std::system_error(
            static_cast<int>(error_number), std::system_category(),
            "Windows process identity OpenProcess");
    }
    FILETIME creation{};
    FILETIME exit{};
    FILETIME kernel{};
    FILETIME user{};
    const BOOL times_ok =
        ::GetProcessTimes(process, &creation, &exit, &kernel, &user);
    const DWORD times_error = times_ok ? ERROR_SUCCESS : ::GetLastError();
    const DWORD wait_result = ::WaitForSingleObject(process, 0);
    const DWORD wait_error =
        wait_result == WAIT_FAILED ? ::GetLastError() : ERROR_SUCCESS;
    ::CloseHandle(process);
    if (!times_ok) {
        throw std::system_error(
            static_cast<int>(times_error), std::system_category(),
            "Windows process identity GetProcessTimes");
    }
    if (wait_result == WAIT_OBJECT_0) {
        throw ProcessNotRunningError(
            "the claimed Windows process has exited");
    }
    if (wait_result == WAIT_FAILED) {
        throw std::system_error(
            static_cast<int>(wait_error), std::system_category(),
            "Windows process identity WaitForSingleObject");
    }
    if (wait_result != WAIT_TIMEOUT) {
        throw std::runtime_error(
            "Windows process identity wait returned an unexpected result");
    }
    const std::uint64_t start = filetime_u64(creation);
    if (start == 0) {
        throw std::runtime_error("Windows process creation time is zero");
    }
    return {std::string(kWindowsFormat),
            static_cast<std::uint64_t>(process_id),
            "",
            decimal_u64(start)};
}

#endif

}  // namespace

namespace detail {

bool canonical_linux_boot_id(std::string_view value) noexcept {
    return sync_system_boot_id_is_canonical(value);
}

bool canonical_positive_decimal_token(std::string_view value) noexcept {
    if (value.empty() || value.front() == '0') return false;
    return std::all_of(value.begin(), value.end(), [](char c) {
        return c >= '0' && c <= '9';
    });
}

LinuxProcStatIdentity parse_linux_proc_pid_stat_identity_or_throw(
    std::string_view bytes,
    std::uint64_t expected_process_id) {
    if (bytes.empty() || bytes.size() > kMaximumProcTextBytes ||
        bytes.find('\0') != std::string_view::npos) {
        throw std::runtime_error("Linux process stat bytes are not bounded text");
    }
    while (!bytes.empty() && (bytes.back() == '\n' || bytes.back() == '\r')) {
        bytes.remove_suffix(1);
    }
    const std::size_t open = bytes.find('(');
    const std::size_t close = bytes.rfind(')');
    if (open == std::string_view::npos || close == std::string_view::npos ||
        open == 0 || close <= open || close + 4 > bytes.size() ||
        bytes[open - 1] != ' ' || bytes[close + 1] != ' ' ||
        bytes[close + 3] != ' ') {
        throw std::runtime_error("Linux process stat framing is invalid");
    }

    std::uint64_t parsed_pid = 0;
    const std::string_view pid_text = bytes.substr(0, open - 1);
    const auto pid_result = std::from_chars(pid_text.data(),
                                            pid_text.data() + pid_text.size(),
                                            parsed_pid);
    if (pid_result.ec != std::errc{} ||
        pid_result.ptr != pid_text.data() + pid_text.size() ||
        parsed_pid == 0 || parsed_pid != expected_process_id) {
        throw std::runtime_error("Linux process stat PID does not match the requested process");
    }

    const char state = bytes[close + 2];
    if (!std::isalpha(static_cast<unsigned char>(state))) {
        throw std::runtime_error("Linux process stat state is invalid");
    }
    std::string_view fields = bytes.substr(close + 4);
    std::uint64_t starttime = 0;
    for (std::size_t field = 4; field <= 22; ++field) {
        while (!fields.empty() && fields.front() == ' ') fields.remove_prefix(1);
        if (fields.empty()) {
            throw std::runtime_error("Linux process stat ended before starttime");
        }
        const std::size_t separator = fields.find(' ');
        const std::string_view token =
            separator == std::string_view::npos ? fields
                                                : fields.substr(0, separator);
        if (field == 22) {
            const auto result = std::from_chars(token.data(),
                                                token.data() + token.size(),
                                                starttime);
            if (result.ec != std::errc{} ||
                result.ptr != token.data() + token.size() || starttime == 0) {
                throw std::runtime_error("Linux process stat starttime is not a positive integer");
            }
            break;
        }
        if (separator == std::string_view::npos) {
            throw std::runtime_error("Linux process stat ended before starttime");
        }
        fields.remove_prefix(separator + 1);
    }
    return {parsed_pid, state, starttime};
}

}  // namespace detail

void validate_sync_process_identity_observation_or_throw(
    const SyncProcessIdentityObservation& observation) {
    if (observation.format == kLinuxFormat) {
        if (observation.process_id == 0 ||
            observation.process_id > static_cast<std::uint64_t>(
                                         std::numeric_limits<std::int32_t>::max())) {
            throw std::runtime_error(
                "Linux process identity process_id is outside the supported range");
        }
        if (!detail::canonical_linux_boot_id(observation.boot_id)) {
            throw std::runtime_error(
                "Linux process identity boot_id is not a canonical lowercase UUID");
        }
        if (!detail::canonical_positive_decimal_token(observation.start_token)) {
            throw std::runtime_error(
                "Linux process identity start_token is not canonical positive decimal");
        }
        return;
    }
    if (observation.format == kWindowsFormat) {
        if (observation.process_id == 0 ||
            observation.process_id > std::numeric_limits<std::uint32_t>::max()) {
            throw std::runtime_error(
                "Windows process identity process_id is outside DWORD range");
        }
        if (!observation.boot_id.empty()) {
            throw std::runtime_error(
                "Windows process identity boot_id must be empty");
        }
        if (!detail::canonical_positive_decimal_token(observation.start_token)) {
            throw std::runtime_error(
                "Windows process identity start_token is not canonical positive decimal");
        }
        return;
    }
    if (observation.format == kUnavailableFormat) {
        if (observation.process_id != 0 || !observation.boot_id.empty() ||
            !observation.start_token.empty()) {
            throw std::runtime_error(
                "unavailable process identity must not contain identity residue");
        }
        return;
    }
    throw std::runtime_error("process identity observation format is unsupported");
}

SyncProcessIdentityObservation
current_sync_process_identity_observation_or_throw() {
#if defined(__linux__)
    const pid_t raw_pid = ::getpid();
    if (raw_pid <= 0) {
        throw std::runtime_error("current Linux process ID is invalid");
    }
    const auto process_id = static_cast<std::uint64_t>(raw_pid);
    const detail::LinuxProcStatIdentity identity =
        read_linux_proc_identity_or_throw(process_id);
    if (terminal_linux_process_state(identity.state)) {
        throw std::runtime_error("current Linux process is in a terminal state");
    }
    SyncProcessIdentityObservation result{
        std::string(kLinuxFormat),
        process_id,
        current_linux_boot_id_or_throw(),
        decimal_u64(identity.starttime_ticks),
    };
    validate_sync_process_identity_observation_or_throw(result);
    return result;
#elif defined(_WIN32)
    SyncProcessIdentityObservation result =
        observe_windows_process_or_throw(::GetCurrentProcessId());
    validate_sync_process_identity_observation_or_throw(result);
    return result;
#else
    return {std::string(kUnavailableFormat), 0, "", ""};
#endif
}

SyncProcessIdentityMatch check_sync_process_identity_observation_noexcept(
    const SyncProcessIdentityObservation& expected) noexcept {
    try {
        validate_sync_process_identity_observation_or_throw(expected);
    } catch (const std::exception& error) {
        return {SyncProcessIdentityMatchKind::Invalid,
                false,
                false,
                false,
                error.what()};
    } catch (...) {
        return {SyncProcessIdentityMatchKind::Invalid,
                false,
                false,
                false,
                "process identity validation failed with a nonstandard exception"};
    }

    try {
#if defined(__linux__)
        if (expected.format != kLinuxFormat) {
            return {SyncProcessIdentityMatchKind::Unsupported,
                    false,
                    false,
                    false,
                    "the heartbeat process identity format is not verifiable on Linux"};
        }
        const pid_t pid = static_cast<pid_t>(expected.process_id);
        errno = 0;
        OwnedDescriptor pidfd(open_pidfd_noexcept(pid));
        const int pidfd_error = errno;
        const bool pidfd_available = pidfd.valid();
        if (!pidfd_available && pidfd_error == ESRCH) {
            return {SyncProcessIdentityMatchKind::NotRunning,
                    true,
                    false,
                    false,
                    "the claimed Linux PID does not exist"};
        }
        if (!pidfd_available && pidfd_error != ENOSYS &&
            pidfd_error != EINVAL && pidfd_error != EPERM) {
            return {SyncProcessIdentityMatchKind::Indeterminate,
                    true,
                    false,
                    false,
                    "pidfd_open could not observe the claimed Linux PID"};
        }
        bool pidfd_indeterminate = false;
        if (pidfd_available &&
            pidfd_reports_exit_noexcept(pidfd.get(), pidfd_indeterminate)) {
            return {SyncProcessIdentityMatchKind::NotRunning,
                    true,
                    false,
                    false,
                    "the claimed Linux process has exited"};
        }
        if (pidfd_indeterminate) {
            return {SyncProcessIdentityMatchKind::Indeterminate,
                    true,
                    false,
                    false,
                    "the Linux pidfd could not be polled"};
        }

        detail::LinuxProcStatIdentity identity{};
        try {
            identity = read_linux_proc_identity_or_throw(expected.process_id);
        } catch (const std::system_error& error) {
            if (error.code().value() == ENOENT ||
                error.code().value() == ESRCH) {
                return {SyncProcessIdentityMatchKind::NotRunning,
                        true,
                        false,
                        false,
                        "the claimed Linux process disappeared during observation"};
            }
            return {SyncProcessIdentityMatchKind::Indeterminate,
                    true,
                    false,
                    false,
                    error.what()};
        } catch (const std::exception& error) {
            return {SyncProcessIdentityMatchKind::Indeterminate,
                    true,
                    false,
                    false,
                    error.what()};
        }
        std::string boot_id;
        try {
            boot_id = current_linux_boot_id_or_throw();
        } catch (const std::exception& error) {
            return {SyncProcessIdentityMatchKind::Indeterminate,
                    true,
                    true,
                    false,
                    error.what()};
        }
        if (terminal_linux_process_state(identity.state)) {
            return {SyncProcessIdentityMatchKind::NotRunning,
                    true,
                    false,
                    false,
                    "the claimed Linux process is terminal"};
        }
        if (pidfd_available &&
            pidfd_reports_exit_noexcept(pidfd.get(), pidfd_indeterminate)) {
            return {SyncProcessIdentityMatchKind::NotRunning,
                    true,
                    false,
                    false,
                    "the claimed Linux process exited during observation"};
        }
        if (pidfd_indeterminate) {
            return {SyncProcessIdentityMatchKind::Indeterminate,
                    true,
                    false,
                    false,
                    "the Linux pidfd could not be re-polled"};
        }
        const bool match =
            boot_id == expected.boot_id &&
            decimal_u64(identity.starttime_ticks) == expected.start_token;
        return {match ? SyncProcessIdentityMatchKind::Match
                      : SyncProcessIdentityMatchKind::Mismatch,
                true,
                true,
                match,
                match ? "the claimed Linux PID, boot, and starttime match"
                      : "the claimed Linux PID belongs to a different boot or process start"};
#elif defined(_WIN32)
        if (expected.format != kWindowsFormat) {
            return {SyncProcessIdentityMatchKind::Unsupported,
                    false,
                    false,
                    false,
                    "the heartbeat process identity format is not verifiable on Windows"};
        }
        SyncProcessIdentityObservation actual =
            observe_windows_process_or_throw(
                static_cast<DWORD>(expected.process_id));
        const bool match = actual == expected;
        return {match ? SyncProcessIdentityMatchKind::Match
                      : SyncProcessIdentityMatchKind::Mismatch,
                true,
                true,
                match,
                match ? "the claimed Windows PID and creation time match"
                      : "the claimed Windows PID belongs to a different process creation"};
#else
        (void)expected;
        return {SyncProcessIdentityMatchKind::Unsupported,
                false,
                false,
                false,
                "process-incarnation verification is unavailable on this platform"};
#endif
    } catch (const ProcessNotRunningError& error) {
        return {SyncProcessIdentityMatchKind::NotRunning,
                true,
                false,
                false,
                error.what()};
    } catch (const std::exception& error) {
        return {SyncProcessIdentityMatchKind::Indeterminate,
                true,
                false,
                false,
                error.what()};
    } catch (...) {
        return {SyncProcessIdentityMatchKind::Indeterminate,
                false,
                false,
                false,
                "process identity verification failed with a nonstandard exception"};
    }
}

const char* sync_process_identity_match_kind_name(
    SyncProcessIdentityMatchKind kind) noexcept {
    switch (kind) {
        case SyncProcessIdentityMatchKind::Match: return "match";
        case SyncProcessIdentityMatchKind::NotRunning: return "not-running";
        case SyncProcessIdentityMatchKind::Mismatch: return "mismatch";
        case SyncProcessIdentityMatchKind::Unsupported: return "unsupported";
        case SyncProcessIdentityMatchKind::Indeterminate: return "indeterminate";
        case SyncProcessIdentityMatchKind::Invalid: return "invalid";
    }
    return "invalid";
}

}  // namespace anonsync
