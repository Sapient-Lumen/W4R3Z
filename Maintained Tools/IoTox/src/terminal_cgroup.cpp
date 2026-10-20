#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "iotox/terminal_cgroup.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cerrno>
#include <charconv>
#include <chrono>
#include <climits>
#include <cstdint>
#include <cstring>
#include <dirent.h>
#include <exception>
#include <fcntl.h>
#include <linux/magic.h>
#include <limits>
#include <new>
#include <mutex>
#include <poll.h>
#include <set>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <tuple>
#include <sys/eventfd.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/vfs.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::terminal::detail {
namespace {

constexpr std::size_t kMaximumCgroupRecordBytes = 64U * 1024U;
constexpr std::size_t kMaximumProcRecordBytes = 64U * 1024U;
constexpr unsigned int kMaximumCgroupNameAttempts = 1024U;
constexpr std::uint64_t kDefaultCpuPeriodMicroseconds = 100000U;
constexpr std::string_view kSessionCgroupPrefix{"_iotox_session_"};
constexpr std::string_view kSessionCgroupV2Prefix{"_iotox_session_v2_"};

template <typename Integer>
void saturating_increment(Integer &value) noexcept {
    if (value != std::numeric_limits<Integer>::max()) ++value;
}

template <typename Integer>
void atomic_saturating_increment(std::atomic<Integer> &value) noexcept {
    Integer current = value.load(std::memory_order_relaxed);
    while (current != std::numeric_limits<Integer>::max() &&
           !value.compare_exchange_weak(
               current, static_cast<Integer>(current + 1),
               std::memory_order_release, std::memory_order_relaxed)) {
    }
}

template <typename Integer>
void saturating_add(Integer &value, Integer increment) noexcept {
    const Integer maximum = std::numeric_limits<Integer>::max();
    if (increment > maximum - value) {
        value = maximum;
    } else {
        value += increment;
    }
}

class FileDescriptor {
  public:
    FileDescriptor() = default;
    explicit FileDescriptor(int descriptor) : descriptor_(descriptor) {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor &) = delete;
    FileDescriptor &operator=(const FileDescriptor &) = delete;
    FileDescriptor(FileDescriptor &&other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    FileDescriptor &operator=(FileDescriptor &&other) noexcept {
        if (this != &other) {
            reset();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }
    [[nodiscard]] int release() noexcept {
        return std::exchange(descriptor_, -1);
    }
    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) {
            static_cast<void>(::close(descriptor_));
        }
        descriptor_ = descriptor;
    }

  private:
    int descriptor_{-1};
};

[[nodiscard]] Status verify_control_boundary(
    int descriptor, uid_t target_uid, gid_t target_gid,
    std::string_view name);

[[nodiscard]] Status errno_status(
    ErrorCode code, std::string_view operation, int error_number = errno) {
    return Status{
        code,
        std::string(operation) + ": " + std::strerror(error_number)};
}

[[nodiscard]] bool valid_flat_key(std::string_view key) noexcept {
    if (key.empty()) return false;
    return std::all_of(key.begin(), key.end(), [](char character) {
        return (character >= 'a' && character <= 'z') ||
               (character >= '0' && character <= '9') || character == '_' ||
               character == '.' || character == '-';
    });
}

[[nodiscard]] bool valid_controller_name(std::string_view name) noexcept {
    if (name.empty()) return false;
    return std::all_of(name.begin(), name.end(), [](char character) {
        return (character >= 'a' && character <= 'z') ||
               (character >= '0' && character <= '9') || character == '_';
    });
}

[[nodiscard]] Result<std::set<std::string>> parse_controller_list(
    std::string_view record, std::string_view label) {
    std::set<std::string> controllers;
    if (record.empty()) return controllers;
    if (record.back() != '\n' || record.find('\n') != record.size() - 1U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " is not one canonical newline-terminated controller list"};
    }
    record.remove_suffix(1U);
    if (record.empty()) return controllers;

    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t separator = record.find(' ', cursor);
        const std::size_t end = separator == std::string_view::npos
                                    ? record.size()
                                    : separator;
        const std::string_view controller = record.substr(cursor, end - cursor);
        if (!valid_controller_name(controller) ||
            !controllers.emplace(controller).second) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) +
                              " contains an invalid or duplicate controller"};
        }
        if (separator == std::string_view::npos) break;
        cursor = separator + 1U;
        if (cursor == record.size() || record[cursor] == ' ') {
            return Status{ErrorCode::protocol_error,
                          std::string(label) +
                              " contains noncanonical spacing"};
        }
    }
    return controllers;
}

[[nodiscard]] Result<std::uint64_t> parse_flat_value(
    std::string_view value) {
    if (value.empty() || value.front() == '+' || value.front() == '-' ||
        (value.size() > 1U && value.front() == '0')) {
        return Status{ErrorCode::protocol_error,
                      "cgroup.events contains an invalid value"};
    }
    std::uint64_t parsed_value = 0U;
    const auto parsed = std::from_chars(
        value.data(), value.data() + value.size(), parsed_value);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != value.data() + value.size()) {
        return Status{ErrorCode::protocol_error,
                      "cgroup.events contains an invalid value"};
    }
    return parsed_value;
}

[[nodiscard]] Result<std::uint64_t> parse_canonical_unsigned(
    std::string_view value, std::string_view label) {
    if (value.empty() || value.front() == '+' || value.front() == '-' ||
        (value.size() > 1U && value.front() == '0')) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " contains a noncanonical integer"};
    }
    std::uint64_t parsed = 0U;
    const auto result = std::from_chars(
        value.data(), value.data() + value.size(), parsed, 10);
    if (result.ec != std::errc{} ||
        result.ptr != value.data() + value.size()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " contains an invalid integer"};
    }
    return parsed;
}

[[nodiscard]] Status validate_psi_decimal(
    std::string_view value, std::string_view label,
    bool percentage) {
    if (value.empty() || value.size() > 32U || value.front() == '+' ||
        value.front() == '-') {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " contains an invalid decimal"};
    }
    const std::size_t point = value.find('.');
    if (point == std::string_view::npos || point == 0U ||
        point + 1U >= value.size() ||
        value.find('.', point + 1U) != std::string_view::npos) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " contains an invalid decimal"};
    }
    const std::string_view whole = value.substr(0U, point);
    const std::string_view fraction = value.substr(point + 1U);
    if ((whole.size() > 1U && whole.front() == '0') ||
        !std::all_of(whole.begin(), whole.end(), [](char character) {
            return character >= '0' && character <= '9';
        }) ||
        !std::all_of(fraction.begin(), fraction.end(), [](char character) {
            return character >= '0' && character <= '9';
        })) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " contains a noncanonical decimal"};
    }
    if (!percentage) return Status::success();
    if (fraction.size() != 2U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) +
                          " contains a noncanonical percentage"};
    }
    auto integral = parse_canonical_unsigned(whole, label);
    if (!integral.ok()) return integral.status();
    if (integral.value() > 100U ||
        (integral.value() == 100U && fraction != "00")) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " percentage exceeds 100.00"};
    }
    return Status::success();
}

[[nodiscard]] Result<std::uint16_t> parse_psi_percentage_basis_points(
    std::string_view value, std::string_view label) {
    const Status valid = validate_psi_decimal(value, label, true);
    if (!valid.ok()) return valid;
    const std::size_t point = value.find('.');
    auto whole = parse_canonical_unsigned(value.substr(0U, point), label);
    if (!whole.ok()) return whole.status();
    const std::string_view fraction = value.substr(point + 1U);
    const std::uint16_t fractional = static_cast<std::uint16_t>(
        static_cast<unsigned int>(fraction[0U] - '0') * 10U +
        static_cast<unsigned int>(fraction[1U] - '0'));
    const std::uint64_t basis_points = whole.value() * 100U + fractional;
    if (basis_points > kCgroupMaximumPressureBasisPoints) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " percentage exceeds 100.00"};
    }
    return static_cast<std::uint16_t>(basis_points);
}

[[nodiscard]] Status validate_future_psi_value(
    std::string_view value, std::string_view label) {
    if (value.find('.') != std::string_view::npos) {
        return validate_psi_decimal(value, label, false);
    }
    auto parsed = parse_canonical_unsigned(value, label);
    return parsed.ok() ? Status::success() : parsed.status();
}

[[nodiscard]] Result<CgroupIoDevice> parse_cgroup_device_key(
    std::string_view value, std::string_view label) {
    const std::size_t separator = value.find(':');
    if (separator == std::string_view::npos || separator == 0U ||
        separator + 1U >= value.size() ||
        value.find(':', separator + 1U) != std::string_view::npos) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " contains an invalid device key"};
    }
    auto major = parse_canonical_unsigned(
        value.substr(0U, separator), label);
    if (!major.ok()) return major.status();
    auto minor = parse_canonical_unsigned(
        value.substr(separator + 1U), label);
    if (!minor.ok()) return minor.status();
    if (major.value() > std::numeric_limits<std::uint32_t>::max() ||
        minor.value() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " device key exceeds u32"};
    }
    if (major.value() == 0U && minor.value() == 0U) {
        return Status{ErrorCode::protocol_error,
                      std::string(label) + " device key 0:0 is invalid"};
    }
    return CgroupIoDevice{
        static_cast<std::uint32_t>(major.value()),
        static_cast<std::uint32_t>(minor.value())};
}

[[nodiscard]] Result<FileDescriptor> open_absolute_directory_without_symlinks(
    const std::filesystem::path &path) {
    if (path.empty() || !path.is_absolute() || path == "/" ||
        path.lexically_normal() != path) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup root must be a normalized non-root absolute path"};
    }
    FileDescriptor current(
        ::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (current.get() < 0) {
        return errno_status(ErrorCode::io_error, "open cgroup path root");
    }
    for (const auto &component : path.relative_path()) {
        const std::string name = component.string();
        if (name.empty() || name == "." || name == ".." ||
            name.find('/') != std::string::npos ||
            name.find('\0') != std::string::npos) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox cgroup root contains an invalid component"};
        }
        FileDescriptor next(::openat(
            current.get(), name.c_str(),
            O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
        if (next.get() < 0) {
            const ErrorCode code =
                errno == EACCES || errno == EPERM
                    ? ErrorCode::unavailable
                    : ErrorCode::io_error;
            return errno_status(
                code, "open Ratox cgroup root component");
        }
        current = std::move(next);
    }
    return current;
}

[[nodiscard]] Status require_cgroup2_filesystem(
    int descriptor, std::string_view label) {
    struct statfs filesystem {};
    if (::fstatfs(descriptor, &filesystem) != 0) {
        return errno_status(ErrorCode::io_error, "inspect cgroup filesystem");
    }
    if (filesystem.f_type != static_cast<decltype(filesystem.f_type)>(
                                 CGROUP2_SUPER_MAGIC)) {
        return Status{
            ErrorCode::unsupported,
            std::string(label) + " is not backed by the cgroup v2 filesystem"};
    }
    return Status::success();
}

[[nodiscard]] Result<FileDescriptor> open_control_file(
    int directory, std::string_view name, int flags) {
    const std::string stable_name{name};
    FileDescriptor descriptor(::openat(
        directory, stable_name.c_str(),
        flags | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) {
        ErrorCode code = ErrorCode::io_error;
        if (errno == ENOENT || errno == EOPNOTSUPP) {
            code = ErrorCode::unsupported;
        } else if (errno == EACCES || errno == EPERM || errno == EROFS) {
            code = ErrorCode::unavailable;
        } else if (errno == ENFILE || errno == EMFILE || errno == ENOMEM) {
            code = ErrorCode::resource_exhausted;
        }
        return errno_status(
            code, "open cgroup v2 control file '" + stable_name + "'");
    }
    struct stat metadata {};
    if (::fstat(descriptor.get(), &metadata) != 0) {
        return errno_status(
            ErrorCode::io_error,
            "inspect cgroup v2 control file '" + stable_name + "'");
    }
    if (!S_ISREG(metadata.st_mode)) {
        return Status{
            ErrorCode::unsupported,
            "cgroup v2 control file '" + stable_name +
                "' is not a regular kernel interface"};
    }
    return descriptor;
}

[[nodiscard]] Result<std::string> read_control_record(
    int descriptor, std::string_view label,
    std::size_t maximum_bytes = kMaximumCgroupRecordBytes) {
    if (::lseek(descriptor, 0, SEEK_SET) < 0) {
        return errno_status(ErrorCode::io_error, "rewind " + std::string(label));
    }
    std::string result;
    result.reserve(std::min<std::size_t>(maximum_bytes, 4096U));
    std::array<char, 4096U> buffer{};
    while (true) {
        const std::size_t remaining = maximum_bytes - result.size();
        if (remaining == 0U) {
            char extra = 0;
            ssize_t count = -1;
            do {
                count = ::read(descriptor, &extra, 1U);
            } while (count < 0 && errno == EINTR);
            if (count < 0) {
                return errno_status(
                    ErrorCode::io_error, "read " + std::string(label));
            }
            if (count > 0) {
                return Status{ErrorCode::resource_exhausted,
                              std::string(label) + " exceeds the byte bound"};
            }
            break;
        }
        ssize_t count = -1;
        do {
            count = ::read(
                descriptor, buffer.data(),
                std::min<std::size_t>(buffer.size(), remaining));
        } while (count < 0 && errno == EINTR);
        if (count < 0) {
            return errno_status(
                ErrorCode::io_error, "read " + std::string(label));
        }
        if (count == 0) break;
        result.append(buffer.data(), static_cast<std::size_t>(count));
    }
    return result;
}

[[nodiscard]] Status write_control_record(
    int descriptor, std::string_view record, std::string_view label) {
    ssize_t count = -1;
    do {
        count = ::write(descriptor, record.data(), record.size());
    } while (count < 0 && errno == EINTR);
    if (count < 0) {
        const ErrorCode code =
            errno == EACCES || errno == EPERM || errno == EROFS
                ? ErrorCode::unavailable
                : ErrorCode::io_error;
        return errno_status(code, "write " + std::string(label));
    }
    if (count != static_cast<ssize_t>(record.size())) {
        return Status{ErrorCode::io_error,
                      std::string(label) + " accepted a short write"};
    }
    return Status::success();
}

[[nodiscard]] std::set<std::string> requested_resource_controllers(
    const CgroupResourceLimits &limits) {
    std::set<std::string> requested;
    if (limits.maximum_processes.has_value()) requested.emplace("pids");
    if (limits.maximum_memory_high_bytes.has_value() ||
        limits.maximum_memory_bytes.has_value() ||
        limits.maximum_swap_bytes.has_value()) {
        requested.emplace("memory");
    }
    if (limits.cpu_quota_microseconds.has_value()) requested.emplace("cpu");
    if (limits.io_device.has_value()) requested.emplace("io");
    return requested;
}

[[nodiscard]] Status require_resource_controllers(
    int delegated_root, uid_t target_uid, gid_t target_gid,
    const CgroupResourceLimits &limits) {
    const std::set<std::string> requested =
        requested_resource_controllers(limits);
    if (requested.empty()) return Status::success();

    auto available = open_control_file(
        delegated_root, "cgroup.controllers", O_RDONLY);
    if (!available.ok()) return available.status();
    const Status available_boundary = verify_control_boundary(
        available.value().get(), target_uid, target_gid,
        "cgroup.controllers");
    if (!available_boundary.ok()) return available_boundary;
    auto available_record = read_control_record(
        available.value().get(), "cgroup.controllers");
    if (!available_record.ok()) return available_record.status();
    auto available_set = parse_controller_list(
        available_record.value(), "cgroup.controllers");
    if (!available_set.ok()) return available_set.status();

    auto enabled = open_control_file(
        delegated_root, "cgroup.subtree_control", O_RDONLY);
    if (!enabled.ok()) return enabled.status();
    const Status enabled_boundary = verify_control_boundary(
        enabled.value().get(), target_uid, target_gid,
        "cgroup.subtree_control");
    if (!enabled_boundary.ok()) return enabled_boundary;
    auto enabled_record = read_control_record(
        enabled.value().get(), "cgroup.subtree_control");
    if (!enabled_record.ok()) return enabled_record.status();
    auto enabled_set = parse_controller_list(
        enabled_record.value(), "cgroup.subtree_control");
    if (!enabled_set.ok()) return enabled_set.status();

    for (const std::string &controller : requested) {
        if (!available_set.value().contains(controller)) {
            return Status{
                ErrorCode::unsupported,
                "Ratox cgroup controller '" + controller +
                    "' is not available to the delegated root"};
        }
        if (!enabled_set.value().contains(controller)) {
            return Status{
                ErrorCode::unavailable,
                "Ratox cgroup controller '" + controller +
                    "' is not activated in the delegated root subtree"};
        }
    }
    return Status::success();
}

[[nodiscard]] Status write_and_verify_resource_control(
    int session_directory, uid_t target_uid, gid_t target_gid,
    std::string_view name, std::string record) {
    auto control = open_control_file(session_directory, name, O_RDWR);
    if (!control.ok()) return control.status();
    const Status protected_control = verify_control_boundary(
        control.value().get(), target_uid, target_gid, name);
    if (!protected_control.ok()) return protected_control;
    const Status written = write_control_record(
        control.value().get(), record, name);
    if (!written.ok()) return written;
    auto observed = read_control_record(
        control.value().get(), name, 256U);
    if (!observed.ok()) return observed.status();
    if (observed.value() != record) {
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup control '" + std::string(name) +
                "' did not retain the exact configured value"};
    }
    return Status::success();
}

[[nodiscard]] Result<std::vector<CgroupIoMax>> parse_io_max_record_internal(
    std::string_view record) {
    if (record.empty() || record.size() > kMaximumCgroupRecordBytes ||
        record.back() != '\n') {
        return Status{ErrorCode::protocol_error,
                      "io.max is empty, oversized, or unterminated"};
    }
    std::vector<CgroupIoMax> devices;
    std::set<std::pair<std::uint32_t, std::uint32_t>> device_keys;
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        if (end == std::string_view::npos || end == cursor) {
            return Status{ErrorCode::protocol_error,
                          "io.max contains a malformed line"};
        }
        const std::string_view line = record.substr(cursor, end - cursor);
        const std::size_t first_space = line.find(' ');
        if (first_space == std::string_view::npos || first_space == 0U ||
            first_space + 1U >= line.size()) {
            return Status{ErrorCode::protocol_error,
                          "io.max contains a malformed device line"};
        }
        auto device = parse_cgroup_device_key(
            line.substr(0U, first_space), "io.max");
        if (!device.ok()) return device.status();
        if (!device_keys.emplace(
                device.value().major, device.value().minor).second) {
            return Status{ErrorCode::protocol_error,
                          "io.max contains a duplicate device line"};
        }

        CgroupIoMax parsed;
        parsed.device = device.value();
        std::set<std::string> keys;
        bool rbps_seen = false;
        bool wbps_seen = false;
        bool riops_seen = false;
        bool wiops_seen = false;
        std::size_t field_cursor = first_space + 1U;
        while (field_cursor < line.size()) {
            const std::size_t separator = line.find(' ', field_cursor);
            const std::size_t field_end =
                separator == std::string_view::npos ? line.size() : separator;
            if (field_end == field_cursor) {
                return Status{ErrorCode::protocol_error,
                              "io.max contains noncanonical spacing"};
            }
            const std::string_view field =
                line.substr(field_cursor, field_end - field_cursor);
            const std::size_t equals = field.find('=');
            if (equals == std::string_view::npos || equals == 0U ||
                equals + 1U >= field.size() ||
                field.find('=', equals + 1U) != std::string_view::npos) {
                return Status{ErrorCode::protocol_error,
                              "io.max contains a malformed keyed value"};
            }
            const std::string_view key = field.substr(0U, equals);
            const std::string_view value = field.substr(equals + 1U);
            if (!valid_flat_key(key) ||
                !keys.emplace(key).second) {
                return Status{ErrorCode::protocol_error,
                              "io.max contains an invalid or duplicate key"};
            }
            std::optional<std::uint64_t> finite;
            if (value != "max") {
                auto numeric = parse_canonical_unsigned(value, "io.max");
                if (!numeric.ok()) return numeric.status();
                finite = numeric.value();
            }
            const bool standard_key =
                key == "rbps" || key == "wbps" ||
                key == "riops" || key == "wiops";
            if (standard_key && finite.has_value() && *finite == 0U) {
                return Status{ErrorCode::protocol_error,
                              "io.max contains a zero finite ceiling"};
            }
            if (key == "rbps") {
                rbps_seen = true;
                parsed.read_bytes_per_second = finite;
            } else if (key == "wbps") {
                wbps_seen = true;
                parsed.write_bytes_per_second = finite;
            } else if (key == "riops") {
                riops_seen = true;
                parsed.read_operations_per_second = finite;
            } else if (key == "wiops") {
                wiops_seen = true;
                parsed.write_operations_per_second = finite;
            }
            if (separator == std::string_view::npos) break;
            field_cursor = separator + 1U;
            if (field_cursor == line.size() || line[field_cursor] == ' ') {
                return Status{ErrorCode::protocol_error,
                              "io.max contains noncanonical spacing"};
            }
        }
        if (!rbps_seen || !wbps_seen || !riops_seen || !wiops_seen) {
            return Status{ErrorCode::protocol_error,
                          "io.max omitted a mandatory ceiling field"};
        }
        devices.push_back(parsed);
        cursor = end + 1U;
    }
    std::sort(
        devices.begin(), devices.end(),
        [](const CgroupIoMax &left, const CgroupIoMax &right) noexcept {
            if (left.device.major != right.device.major) {
                return left.device.major < right.device.major;
            }
            return left.device.minor < right.device.minor;
        });
    return devices;
}

[[nodiscard]] std::string io_max_value(
    const std::optional<std::uint64_t> &value) {
    return value.has_value() ? std::to_string(*value) : "max";
}

[[nodiscard]] Status write_and_verify_io_max(
    int session_directory, uid_t target_uid, gid_t target_gid,
    const CgroupResourceLimits &limits) {
    if (!limits.io_device.has_value()) return Status::success();
    const CgroupIoDevice device = *limits.io_device;
    const std::string record =
        std::to_string(device.major) + ":" + std::to_string(device.minor) +
        " rbps=" + io_max_value(limits.maximum_io_read_bytes_per_second) +
        " wbps=" + io_max_value(limits.maximum_io_write_bytes_per_second) +
        " riops=" +
        io_max_value(limits.maximum_io_read_operations_per_second) +
        " wiops=" +
        io_max_value(limits.maximum_io_write_operations_per_second) + "\n";

    auto control = open_control_file(session_directory, "io.max", O_RDWR);
    if (!control.ok()) return control.status();
    const Status protected_control = verify_control_boundary(
        control.value().get(), target_uid, target_gid, "io.max");
    if (!protected_control.ok()) return protected_control;
    const Status written = write_control_record(
        control.value().get(), record, "io.max");
    if (!written.ok()) return written;
    auto observed = read_control_record(
        control.value().get(), "io.max", 4096U);
    if (!observed.ok()) return observed.status();
    auto parsed = parse_io_max_record_internal(observed.value());
    if (!parsed.ok()) return parsed.status();
    if (parsed.value().size() != 1U) {
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup io.max retained an unexpected device policy"};
    }
    const CgroupIoMax &actual = parsed.value().front();
    if (actual.device != device ||
        actual.read_bytes_per_second !=
            limits.maximum_io_read_bytes_per_second ||
        actual.write_bytes_per_second !=
            limits.maximum_io_write_bytes_per_second ||
        actual.read_operations_per_second !=
            limits.maximum_io_read_operations_per_second ||
        actual.write_operations_per_second !=
            limits.maximum_io_write_operations_per_second) {
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup io.max did not retain the exact configured ceilings"};
    }
    return Status::success();
}

[[nodiscard]] Status apply_resource_limits(
    int session_directory, uid_t target_uid, gid_t target_gid,
    const CgroupResourceLimits &limits) {
    if (limits.empty()) return Status::success();

    if (limits.maximum_processes.has_value()) {
        const Status pids = write_and_verify_resource_control(
            session_directory, target_uid, target_gid, "pids.max",
            std::to_string(*limits.maximum_processes) + "\n");
        if (!pids.ok()) return pids;
    }
    if (limits.maximum_memory_high_bytes.has_value() ||
        limits.maximum_memory_bytes.has_value() ||
        limits.maximum_swap_bytes.has_value()) {
        // A PTY and its descendants are one lifecycle unit. If the memory
        // controller has to invoke OOM, partial survival would violate the
        // same session-wide teardown contract enforced by cgroup.kill.
        const Status oom_group = write_and_verify_resource_control(
            session_directory, target_uid, target_gid,
            "memory.oom.group", "1\n");
        if (!oom_group.ok()) return oom_group;
    }
    if (limits.maximum_memory_high_bytes.has_value()) {
        const Status memory_high = write_and_verify_resource_control(
            session_directory, target_uid, target_gid, "memory.high",
            std::to_string(*limits.maximum_memory_high_bytes) + "\n");
        if (!memory_high.ok()) return memory_high;
    }
    if (limits.maximum_memory_bytes.has_value()) {
        const Status memory = write_and_verify_resource_control(
            session_directory, target_uid, target_gid, "memory.max",
            std::to_string(*limits.maximum_memory_bytes) + "\n");
        if (!memory.ok()) return memory;
    }
    if (limits.maximum_swap_bytes.has_value()) {
        const Status swap = write_and_verify_resource_control(
            session_directory, target_uid, target_gid, "memory.swap.max",
            std::to_string(*limits.maximum_swap_bytes) + "\n");
        if (!swap.ok()) return swap;
    }
    if (limits.cpu_quota_microseconds.has_value()) {
        const std::uint64_t period =
            limits.cpu_period_microseconds.value_or(
                kDefaultCpuPeriodMicroseconds);
        const Status cpu = write_and_verify_resource_control(
            session_directory, target_uid, target_gid, "cpu.max",
            std::to_string(*limits.cpu_quota_microseconds) + " " +
                std::to_string(period) + "\n");
        if (!cpu.ok()) return cpu;
    }
    const Status io = write_and_verify_io_max(
        session_directory, target_uid, target_gid, limits);
    if (!io.ok()) return io;
    return Status::success();
}

[[nodiscard]] Result<bool> wait_for_cgroup_event_change(
    std::span<struct pollfd> observed,
    std::chrono::steady_clock::time_point deadline) {
    if (observed.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "cgroup event wait requires at least one descriptor"};
    }
    for (const struct pollfd &descriptor : observed) {
        if (descriptor.fd < 0 || descriptor.events != POLLPRI) {
            return Status{ErrorCode::invalid_argument,
                          "cgroup event wait received an invalid descriptor"};
        }
    }

    while (true) {
        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) return false;

        const auto remaining = deadline - now;
        auto timeout =
            std::chrono::duration_cast<std::chrono::milliseconds>(remaining);
        if (timeout < remaining) timeout += std::chrono::milliseconds{1};
        const auto bounded_timeout = std::min<std::int64_t>(
            timeout.count(), static_cast<std::int64_t>(INT_MAX));
        for (struct pollfd &descriptor : observed) descriptor.revents = 0;

        const int ready = ::poll(
            observed.data(), static_cast<nfds_t>(observed.size()),
            static_cast<int>(bounded_timeout));
        if (ready < 0) {
            if (errno == EINTR) continue;
            return errno_status(
                ErrorCode::io_error, "poll cgroup.events notification");
        }
        if (ready == 0) return false;

        bool changed = false;
        for (const struct pollfd &descriptor : observed) {
            if ((descriptor.revents & POLLNVAL) != 0) {
                return Status{
                    ErrorCode::unavailable,
                    "cgroup.events descriptor became invalid while waiting"};
            }
            if ((descriptor.revents & POLLHUP) != 0) {
                return Status{
                    ErrorCode::unavailable,
                    "cgroup.events descriptor hung up while waiting"};
            }
            // Linux reports cgroup.events modifications through POLLPRI and
            // also sets POLLERR. POLLERR is therefore a state-change signal
            // here, not an I/O failure; the caller re-reads and validates the
            // complete record before making a lifecycle decision.
            if ((descriptor.revents & (POLLPRI | POLLERR)) != 0) {
                changed = true;
            }
        }
        if (changed) return true;
        return Status{
            ErrorCode::io_error,
            "poll cgroup.events returned without a recognized notification"};
    }
}

[[nodiscard]] bool lower_hex_character(char character) noexcept {
    return (character >= '0' && character <= '9') ||
           (character >= 'a' && character <= 'f');
}

[[nodiscard]] std::uint8_t lower_hex_value(char character) noexcept {
    if (character >= '0' && character <= '9') {
        return static_cast<std::uint8_t>(character - '0');
    }
    return static_cast<std::uint8_t>(character - 'a' + 10);
}

[[nodiscard]] Result<std::uint64_t> parse_canonical_positive_uint64(
    std::string_view value, std::string_view label) {
    if (value.empty() || value.front() == '0' || value.front() == '+' ||
        value.front() == '-') {
        return Status{
            ErrorCode::invalid_argument,
            std::string(label) + " is not a canonical positive integer"};
    }
    std::uint64_t parsed = 0U;
    const auto converted = std::from_chars(
        value.data(), value.data() + value.size(), parsed);
    if (converted.ec != std::errc{} ||
        converted.ptr != value.data() + value.size() || parsed == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            std::string(label) + " is not a canonical positive integer"};
    }
    return parsed;
}

[[nodiscard]] Result<std::array<std::uint8_t, 16U>> parse_boot_id_record(
    std::string_view record) {
    if (!record.empty() && record.back() == '\n') {
        record.remove_suffix(1U);
    }
    if (record.size() != 36U || record[8U] != '-' || record[13U] != '-' ||
        record[18U] != '-' || record[23U] != '-') {
        return Status{ErrorCode::protocol_error,
                      "kernel boot_id is not a canonical UUID"};
    }

    std::array<std::uint8_t, 16U> result{};
    std::size_t nibble = 0U;
    for (char character : record) {
        if (character == '-') continue;
        if (!lower_hex_character(character)) {
            return Status{ErrorCode::protocol_error,
                          "kernel boot_id contains non-lowercase hexadecimal data"};
        }
        const std::uint8_t value = lower_hex_value(character);
        if ((nibble & 1U) == 0U) {
            result[nibble / 2U] = static_cast<std::uint8_t>(value << 4U);
        } else {
            result[nibble / 2U] = static_cast<std::uint8_t>(
                result[nibble / 2U] | value);
        }
        ++nibble;
    }
    if (nibble != 32U) {
        return Status{ErrorCode::protocol_error,
                      "kernel boot_id has an invalid hexadecimal width"};
    }
    return result;
}

[[nodiscard]] Result<std::array<std::uint8_t, 16U>> parse_compact_boot_id(
    std::string_view record) {
    if (record.size() != 32U ||
        !std::all_of(record.begin(), record.end(), lower_hex_character)) {
        return Status{ErrorCode::invalid_argument,
                      "session cgroup boot identity is not 32 lowercase hexadecimal characters"};
    }
    std::array<std::uint8_t, 16U> result{};
    for (std::size_t index = 0U; index < result.size(); ++index) {
        result[index] = static_cast<std::uint8_t>(
            (lower_hex_value(record[index * 2U]) << 4U) |
            lower_hex_value(record[index * 2U + 1U]));
    }
    return result;
}

[[nodiscard]] std::string format_compact_boot_id(
    const std::array<std::uint8_t, 16U> &boot_id) {
    constexpr std::array<char, 16U> digits{
        '0', '1', '2', '3', '4', '5', '6', '7',
        '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
    std::string result(32U, '0');
    for (std::size_t index = 0U; index < boot_id.size(); ++index) {
        result[index * 2U] = digits[boot_id[index] >> 4U];
        result[index * 2U + 1U] = digits[boot_id[index] & 0x0fU];
    }
    return result;
}

[[nodiscard]] Result<FileDescriptor> open_proc_root() {
    FileDescriptor proc(
        ::open("/proc", O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (proc.get() < 0) {
        return errno_status(ErrorCode::unavailable, "open procfs root");
    }
    struct statfs filesystem {};
    if (::fstatfs(proc.get(), &filesystem) != 0) {
        return errno_status(ErrorCode::io_error, "inspect procfs root");
    }
    if (filesystem.f_type !=
        static_cast<decltype(filesystem.f_type)>(PROC_SUPER_MAGIC)) {
        return Status{ErrorCode::unsupported,
                      "/proc is not backed by the proc filesystem"};
    }
    return proc;
}

[[nodiscard]] Result<FileDescriptor> open_directory_at(
    int parent, std::string_view name, std::string_view label) {
    const std::string stable_name{name};
    FileDescriptor descriptor(::openat(
        parent, stable_name.c_str(),
        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) {
        ErrorCode code = ErrorCode::io_error;
        if (errno == ENOENT || errno == ESRCH) {
            code = ErrorCode::not_found;
        } else if (errno == EACCES || errno == EPERM) {
            code = ErrorCode::unavailable;
        } else if (errno == ENFILE || errno == EMFILE || errno == ENOMEM) {
            code = ErrorCode::resource_exhausted;
        }
        return errno_status(code, "open " + std::string(label));
    }
    return descriptor;
}

[[nodiscard]] Result<std::array<std::uint8_t, 16U>> read_current_boot_id() {
    auto proc = open_proc_root();
    if (!proc.ok()) return proc.status();
    auto sys = open_directory_at(proc.value().get(), "sys", "procfs sys directory");
    if (!sys.ok()) return sys.status();
    auto kernel = open_directory_at(
        sys.value().get(), "kernel", "procfs kernel directory");
    if (!kernel.ok()) return kernel.status();
    auto random = open_directory_at(
        kernel.value().get(), "random", "procfs random directory");
    if (!random.ok()) return random.status();

    FileDescriptor boot_id(::openat(
        random.value().get(), "boot_id", O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (boot_id.get() < 0) {
        return errno_status(ErrorCode::unavailable, "open kernel boot_id");
    }
    struct stat metadata {};
    if (::fstat(boot_id.get(), &metadata) != 0) {
        return errno_status(ErrorCode::io_error, "inspect kernel boot_id");
    }
    if (!S_ISREG(metadata.st_mode)) {
        return Status{ErrorCode::unsupported,
                      "kernel boot_id is not a regular procfs interface"};
    }
    auto record = read_control_record(boot_id.get(), "kernel boot_id", 64U);
    if (!record.ok()) return record.status();
    return parse_boot_id_record(record.value());
}

struct ProcessStatRecord {
    std::uint64_t process_id{0U};
    char state{'?'};
    std::uint64_t start_time_ticks{0U};
};

[[nodiscard]] Result<ProcessStatRecord> parse_process_stat_record(
    std::string_view record, std::uint64_t expected_process_id) {
    if (record.empty() || record.size() > kMaximumProcRecordBytes ||
        record.back() != '\n') {
        return Status{ErrorCode::protocol_error,
                      "procfs process stat record is empty, oversized, or unterminated"};
    }
    const std::size_t command_open = record.find(" (");
    const std::size_t command_close = record.rfind(") ");
    if (command_open == std::string_view::npos || command_open == 0U ||
        command_close == std::string_view::npos ||
        command_close <= command_open + 1U || command_close + 4U > record.size() ||
        record[command_close + 3U] != ' ') {
        return Status{ErrorCode::protocol_error,
                      "procfs process stat record has an ambiguous command field"};
    }

    std::uint64_t observed_process_id = 0U;
    const std::string_view process_field = record.substr(0U, command_open);
    const auto parsed_process = std::from_chars(
        process_field.data(), process_field.data() + process_field.size(),
        observed_process_id);
    if (parsed_process.ec != std::errc{} ||
        parsed_process.ptr != process_field.data() + process_field.size() ||
        observed_process_id == 0U || observed_process_id != expected_process_id) {
        return Status{ErrorCode::protocol_error,
                      "procfs process stat identity does not match its pinned directory"};
    }

    const char state = record[command_close + 2U];
    if (state == ' ' || state == '\n' || state == '\0') {
        return Status{ErrorCode::protocol_error,
                      "procfs process stat state is invalid"};
    }

    std::size_t cursor = command_close + 4U;
    std::uint64_t start_time_ticks = 0U;
    for (unsigned int field = 4U; field <= 22U; ++field) {
        while (cursor < record.size() && record[cursor] == ' ') ++cursor;
        const std::size_t end = record.find_first_of(" \n", cursor);
        if (cursor >= record.size() || end == std::string_view::npos ||
            end == cursor) {
            return Status{ErrorCode::protocol_error,
                          "procfs process stat record omits field 22"};
        }
        if (field == 22U) {
            const std::string_view value = record.substr(cursor, end - cursor);
            const auto parsed_start = std::from_chars(
                value.data(), value.data() + value.size(), start_time_ticks);
            if (parsed_start.ec != std::errc{} ||
                parsed_start.ptr != value.data() + value.size() ||
                start_time_ticks == 0U) {
                return Status{ErrorCode::protocol_error,
                              "procfs process stat starttime is invalid"};
            }
        }
        cursor = end + 1U;
    }
    return ProcessStatRecord{observed_process_id, state, start_time_ticks};
}

[[nodiscard]] Result<ProcessStatRecord> read_process_stat(
    std::uint64_t process_id) {
    if (process_id == 0U ||
        process_id > static_cast<std::uint64_t>(
                         std::numeric_limits<pid_t>::max())) {
        return Status{ErrorCode::invalid_argument,
                      "process identity cannot be represented by pid_t"};
    }
    auto proc = open_proc_root();
    if (!proc.ok()) return proc.status();
    const std::string process_name = std::to_string(process_id);
    auto process = open_directory_at(
        proc.value().get(), process_name, "procfs process directory");
    if (!process.ok()) return process.status();

    FileDescriptor stat_file(::openat(
        process.value().get(), "stat", O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (stat_file.get() < 0) {
        ErrorCode code = ErrorCode::io_error;
        if (errno == ENOENT || errno == ESRCH) {
            code = ErrorCode::not_found;
        } else if (errno == EACCES || errno == EPERM) {
            code = ErrorCode::unavailable;
        }
        return errno_status(code, "open procfs process stat");
    }
    struct stat metadata {};
    if (::fstat(stat_file.get(), &metadata) != 0) {
        return errno_status(ErrorCode::io_error, "inspect procfs process stat");
    }
    if (!S_ISREG(metadata.st_mode)) {
        return Status{ErrorCode::unsupported,
                      "procfs process stat is not a regular kernel interface"};
    }
    auto record = read_control_record(
        stat_file.get(), "procfs process stat", kMaximumProcRecordBytes);
    if (!record.ok()) return record.status();
    return parse_process_stat_record(record.value(), process_id);
}

[[nodiscard]] Result<FileDescriptor> open_process_pidfd(
    std::uint64_t process_id) {
    if (process_id == 0U ||
        process_id > static_cast<std::uint64_t>(
                         std::numeric_limits<pid_t>::max())) {
        return Status{ErrorCode::invalid_argument,
                      "process identity cannot be represented by pid_t"};
    }
#ifdef SYS_pidfd_open
    int descriptor = -1;
    do {
        descriptor = static_cast<int>(::syscall(
            SYS_pidfd_open, static_cast<pid_t>(process_id), 0U));
    } while (descriptor < 0 && errno == EINTR);
    if (descriptor < 0) {
        ErrorCode code = ErrorCode::io_error;
        if (errno == ESRCH) {
            code = ErrorCode::not_found;
        } else if (errno == ENOSYS || errno == EINVAL || errno == ENODEV) {
            code = ErrorCode::unsupported;
        } else if (errno == EMFILE || errno == ENFILE || errno == ENOMEM) {
            code = ErrorCode::resource_exhausted;
        } else if (errno == EACCES || errno == EPERM) {
            code = ErrorCode::unavailable;
        }
        return errno_status(code, "open process pidfd");
    }
    return FileDescriptor{descriptor};
#else
    static_cast<void>(process_id);
    return Status{ErrorCode::unsupported,
                  "kernel headers do not expose pidfd_open"};
#endif
}

[[nodiscard]] Result<bool> pidfd_process_exited(int descriptor) {
    struct pollfd observed {
        descriptor, POLLIN, 0
    };
    int ready = -1;
    do {
        ready = ::poll(&observed, 1U, 0);
    } while (ready < 0 && errno == EINTR);
    if (ready < 0) {
        return errno_status(ErrorCode::io_error, "poll process pidfd");
    }
    if ((observed.revents & POLLNVAL) != 0) {
        return Status{ErrorCode::io_error,
                      "process pidfd became invalid during owner validation"};
    }
    if ((observed.revents & POLLERR) != 0) {
        return Status{ErrorCode::unavailable,
                      "process pidfd reported an unexpected error"};
    }
    return (observed.revents & (POLLIN | POLLHUP)) != 0;
}

[[nodiscard]] Result<FileDescriptor> duplicate_descriptor(int descriptor) {
    const int duplicated = ::fcntl(descriptor, F_DUPFD_CLOEXEC, 0);
    if (duplicated < 0) {
        const ErrorCode code = errno == EMFILE || errno == ENFILE
                                   ? ErrorCode::resource_exhausted
                                   : ErrorCode::io_error;
        return errno_status(code, "duplicate pinned cgroup descriptor");
    }
    return FileDescriptor{duplicated};
}

class DirectoryStream {
  public:
    explicit DirectoryStream(DIR *stream) : stream_(stream) {}
    ~DirectoryStream() {
        if (stream_ != nullptr) static_cast<void>(::closedir(stream_));
    }
    DirectoryStream(const DirectoryStream &) = delete;
    DirectoryStream &operator=(const DirectoryStream &) = delete;
    [[nodiscard]] DIR *get() const noexcept { return stream_; }

  private:
    DIR *stream_{nullptr};
};

[[nodiscard]] Result<std::vector<std::string>> list_reserved_cgroup_names(
    int root, std::size_t maximum_candidates) {
    auto duplicate = duplicate_descriptor(root);
    if (!duplicate.ok()) return duplicate.status();
    const int stream_fd = duplicate.value().release();
    DIR *raw = ::fdopendir(stream_fd);
    if (raw == nullptr) {
        const int failure = errno;
        static_cast<void>(::close(stream_fd));
        return errno_status(ErrorCode::io_error,
                            "enumerate delegated cgroup root", failure);
    }
    DirectoryStream stream(raw);

    std::vector<std::string> names;
    errno = 0;
    while (dirent *entry = ::readdir(stream.get())) {
        const std::string_view name{entry->d_name};
        if (name == "." || name == ".." ||
            !name.starts_with(kSessionCgroupPrefix)) {
            continue;
        }
        if (names.size() >= maximum_candidates) {
            return Status{
                ErrorCode::resource_exhausted,
                "delegated cgroup root exceeds the bounded reserved-name recovery set"};
        }
        names.emplace_back(name);
        errno = 0;
    }
    if (errno != 0) {
        return errno_status(ErrorCode::io_error,
                            "read delegated cgroup root directory");
    }
    std::sort(names.begin(), names.end());
    return names;
}

[[nodiscard]] Status validate_legacy_session_cgroup_name(
    std::string_view name) {
    if (!name.starts_with(kSessionCgroupPrefix) ||
        name.starts_with(kSessionCgroupV2Prefix)) {
        return Status{ErrorCode::invalid_argument,
                      "legacy session cgroup name has the wrong prefix"};
    }
    name.remove_prefix(kSessionCgroupPrefix.size());
    const std::size_t separator = name.find('_');
    if (separator == std::string_view::npos ||
        name.find('_', separator + 1U) != std::string_view::npos) {
        return Status{ErrorCode::invalid_argument,
                      "legacy session cgroup name is malformed"};
    }
    auto process = parse_canonical_positive_uint64(
        name.substr(0U, separator), "legacy cgroup process id");
    if (!process.ok()) return process.status();
    auto sequence = parse_canonical_positive_uint64(
        name.substr(separator + 1U), "legacy cgroup sequence");
    if (!sequence.ok()) return sequence.status();
    if (process.value() > static_cast<std::uint64_t>(
                              std::numeric_limits<pid_t>::max())) {
        return Status{ErrorCode::invalid_argument,
                      "legacy cgroup process id exceeds pid_t"};
    }
    return Status::success();
}

[[nodiscard]] Status require_no_child_cgroups(int directory) {
    auto duplicate = duplicate_descriptor(directory);
    if (!duplicate.ok()) return duplicate.status();
    const int raw_fd = duplicate.value().release();
    DIR *raw = ::fdopendir(raw_fd);
    if (raw == nullptr) {
        const int failure = errno;
        static_cast<void>(::close(raw_fd));
        return errno_status(ErrorCode::io_error,
                            "enumerate Ratox session cgroup", failure);
    }
    DirectoryStream stream(raw);
    const int stream_descriptor = ::dirfd(stream.get());
    if (stream_descriptor < 0) {
        return errno_status(
            ErrorCode::io_error,
            "identify Ratox session cgroup directory stream");
    }
    errno = 0;
    while (dirent *entry = ::readdir(stream.get())) {
        const std::string_view name{entry->d_name};
        if (name == "." || name == "..") continue;
        struct stat metadata {};
        if (::fstatat(
                stream_descriptor, entry->d_name, &metadata,
                AT_SYMLINK_NOFOLLOW) != 0) {
            return errno_status(ErrorCode::io_error,
                                "inspect Ratox session cgroup entry");
        }
        if (S_ISDIR(metadata.st_mode)) {
            return Status{
                ErrorCode::unavailable,
                "Ratox session cgroup contains an unexpected child cgroup"};
        }
        errno = 0;
    }
    if (errno != 0) {
        return errno_status(ErrorCode::io_error,
                            "read Ratox session cgroup directory");
    }
    return Status::success();
}

[[nodiscard]] bool target_can_write(
    const struct stat &metadata, uid_t target_uid, gid_t target_gid) noexcept {
    if (metadata.st_uid == target_uid) {
        return (metadata.st_mode & S_IWUSR) != 0;
    }
    if (metadata.st_gid == target_gid) {
        return (metadata.st_mode & S_IWGRP) != 0;
    }
    return (metadata.st_mode & S_IWOTH) != 0;
}

[[nodiscard]] Status verify_daemon_owned_boundary(
    int descriptor, std::string_view label, bool require_directory) {
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        return errno_status(
            ErrorCode::io_error, "inspect " + std::string(label));
    }
    if ((require_directory && !S_ISDIR(metadata.st_mode)) ||
        (!require_directory && !S_ISREG(metadata.st_mode))) {
        return Status{ErrorCode::unsupported,
                      std::string(label) + " has the wrong file type"};
    }
    const uid_t daemon_uid = ::geteuid();
    if (metadata.st_uid != daemon_uid) {
        return Status{
            ErrorCode::invalid_argument,
            std::string(label) + " must be owned by the IoTox daemon uid"};
    }
    if ((metadata.st_mode & static_cast<mode_t>(0022)) != 0) {
        return Status{
            ErrorCode::invalid_argument,
            std::string(label) + " must not be writable by group or other"};
    }
    return Status::success();
}

[[nodiscard]] Status verify_supervisor_owned_boundary(
    int descriptor, uid_t target_uid, gid_t target_gid,
    std::string_view label, bool require_directory) {
    const Status daemon_boundary = verify_daemon_owned_boundary(
        descriptor, label, require_directory);
    if (!daemon_boundary.ok()) return daemon_boundary;

    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        return errno_status(
            ErrorCode::io_error, "reinspect " + std::string(label));
    }
    if (target_can_write(metadata, target_uid, target_gid)) {
        return Status{
            ErrorCode::invalid_argument,
            std::string(label) + " is writable by the configured PTY identity"};
    }
    return Status::success();
}

[[nodiscard]] Status verify_control_boundary(
    int descriptor, uid_t target_uid, gid_t target_gid,
    std::string_view name) {
    return verify_supervisor_owned_boundary(
        descriptor, target_uid, target_gid,
        "cgroup control file '" + std::string(name) + "'", false);
}

[[nodiscard]] Status verify_daemon_control_boundary(
    int descriptor, std::string_view name) {
    return verify_daemon_owned_boundary(
        descriptor, "cgroup control file '" + std::string(name) + "'", false);
}

[[nodiscard]] Result<std::vector<pid_t>> parse_cgroup_processes(
    std::string_view record) {
    std::vector<pid_t> processes;
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        if (end == std::string_view::npos || end == cursor) {
            return Status{ErrorCode::protocol_error,
                          "cgroup.procs contains a malformed process record"};
        }
        const std::string_view line = record.substr(cursor, end - cursor);
        std::int64_t parsed_process = 0;
        const auto parsed = std::from_chars(
            line.data(), line.data() + line.size(), parsed_process);
        if (parsed.ec != std::errc{} ||
            parsed.ptr != line.data() + line.size() || parsed_process <= 0 ||
            parsed_process > static_cast<std::int64_t>(
                                 std::numeric_limits<pid_t>::max())) {
            return Status{ErrorCode::protocol_error,
                          "cgroup.procs contains an invalid process identity"};
        }
        processes.push_back(static_cast<pid_t>(parsed_process));
        cursor = end + 1U;
    }
    return processes;
}

[[nodiscard]] Result<std::pair<uid_t, gid_t>> validate_payload_identity(
    const IdentityPolicy &identity) {
    if (identity.mode != IdentityMode::exact ||
        !identity.clear_supplementary_groups) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup containment requires an exact PTY identity with cleared supplementary groups"};
    }
    const uid_t target_uid = static_cast<uid_t>(identity.uid);
    const gid_t target_gid = static_cast<gid_t>(identity.gid);
    if (static_cast<std::uint64_t>(target_uid) != identity.uid ||
        static_cast<std::uint64_t>(target_gid) != identity.gid) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox cgroup PTY identity is not representable on this host"};
    }
    if (target_uid == static_cast<uid_t>(0) || target_uid == ::geteuid()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup containment requires a non-root PTY uid distinct from the daemon uid"};
    }
    return std::pair{target_uid, target_gid};
}

[[nodiscard]] ErrorCode mkdir_error_code(int error_number) noexcept {
    if (error_number == EACCES || error_number == EPERM ||
        error_number == EROFS) {
        return ErrorCode::unavailable;
    }
    if (error_number == EDQUOT || error_number == ENOSPC ||
        error_number == ENOMEM) {
        return ErrorCode::resource_exhausted;
    }
    return ErrorCode::io_error;
}

using FlatCounterRecord =
    std::vector<std::pair<std::string, std::uint64_t>>;

[[nodiscard]] Result<FlatCounterRecord> parse_flat_counter_record(
    std::string_view record, std::string_view label) {
    if (record.empty() || record.size() > kMaximumCgroupRecordBytes ||
        record.back() != '\n') {
        return Status{
            ErrorCode::protocol_error,
            std::string(label) + " is empty, oversized, or unterminated"};
    }
    FlatCounterRecord fields;
    std::set<std::string> keys;
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        if (end == std::string_view::npos || end == cursor) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " contains a malformed line"};
        }
        const std::string_view line = record.substr(cursor, end - cursor);
        const std::size_t separator = line.find(' ');
        if (separator == std::string_view::npos || separator == 0U ||
            separator + 1U >= line.size() ||
            line.find(' ', separator + 1U) != std::string_view::npos) {
            return Status{
                ErrorCode::protocol_error,
                std::string(label) + " contains a malformed key/value pair"};
        }
        const std::string_view key = line.substr(0U, separator);
        const std::string_view value = line.substr(separator + 1U);
        if (!valid_flat_key(key) ||
            !keys.emplace(key).second) {
            return Status{
                ErrorCode::protocol_error,
                std::string(label) + " contains an invalid or duplicate key"};
        }
        if (value.empty() || value.front() == '+' || value.front() == '-' ||
            (value.size() > 1U && value.front() == '0')) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " contains an invalid value"};
        }
        std::uint64_t parsed_value = 0U;
        const auto parsed = std::from_chars(
            value.data(), value.data() + value.size(), parsed_value);
        if (parsed.ec != std::errc{} ||
            parsed.ptr != value.data() + value.size()) {
            return Status{ErrorCode::protocol_error,
                          std::string(label) + " contains an invalid value"};
        }
        fields.emplace_back(std::string(key), parsed_value);
        cursor = end + 1U;
    }
    return fields;
}

[[nodiscard]] const std::uint64_t *find_counter(
    const FlatCounterRecord &record, std::string_view key) noexcept {
    const auto found = std::find_if(
        record.begin(), record.end(), [key](const auto &field) {
            return field.first == key;
        });
    return found == record.end() ? nullptr : &found->second;
}

std::atomic<std::uint64_t> cgroup_sequence{0U};

}  // namespace

Result<std::array<std::uint8_t, 16U>> parse_boot_id(
    std::string_view record) {
    return parse_boot_id_record(record);
}

Result<CgroupOwnerIdentity> current_cgroup_owner_identity() {
    auto boot_id = read_current_boot_id();
    if (!boot_id.ok()) return boot_id.status();
    const std::uint64_t process_id = static_cast<std::uint64_t>(::getpid());
    auto process = read_process_stat(process_id);
    if (!process.ok()) return process.status();
    return CgroupOwnerIdentity{
        boot_id.value(), process_id, process.value().start_time_ticks};
}

Result<SessionCgroupName> parse_session_cgroup_name(std::string_view name) {
    if (!name.starts_with(kSessionCgroupV2Prefix)) {
        return Status{ErrorCode::invalid_argument,
                      "session cgroup name has the wrong versioned prefix"};
    }
    name.remove_prefix(kSessionCgroupV2Prefix.size());
    if (name.size() < 38U || name[32U] != '_') {
        return Status{ErrorCode::invalid_argument,
                      "session cgroup name has an invalid boot identity field"};
    }
    auto boot_id = parse_compact_boot_id(name.substr(0U, 32U));
    if (!boot_id.ok()) return boot_id.status();
    name.remove_prefix(33U);

    std::array<std::string_view, 3U> decimal_fields{};
    for (std::size_t index = 0U; index < decimal_fields.size(); ++index) {
        const std::size_t separator = name.find('_');
        if (index + 1U == decimal_fields.size()) {
            if (separator != std::string_view::npos) {
                return Status{ErrorCode::invalid_argument,
                              "session cgroup name contains trailing fields"};
            }
            decimal_fields[index] = name;
            name = {};
        } else {
            if (separator == std::string_view::npos) {
                return Status{ErrorCode::invalid_argument,
                              "session cgroup name omits an ownership field"};
            }
            decimal_fields[index] = name.substr(0U, separator);
            name.remove_prefix(separator + 1U);
        }
    }

    auto process_id = parse_canonical_positive_uint64(
        decimal_fields[0U], "session cgroup process id");
    if (!process_id.ok()) return process_id.status();
    if (process_id.value() > static_cast<std::uint64_t>(
                                 std::numeric_limits<pid_t>::max())) {
        return Status{ErrorCode::invalid_argument,
                      "session cgroup process id exceeds pid_t"};
    }
    auto start_time = parse_canonical_positive_uint64(
        decimal_fields[1U], "session cgroup process starttime");
    if (!start_time.ok()) return start_time.status();
    auto sequence = parse_canonical_positive_uint64(
        decimal_fields[2U], "session cgroup sequence");
    if (!sequence.ok()) return sequence.status();

    return SessionCgroupName{
        CgroupOwnerIdentity{
            boot_id.value(), process_id.value(), start_time.value()},
        sequence.value()};
}

Result<std::string> format_session_cgroup_name(
    const SessionCgroupName &name) {
    if (name.owner.process_id == 0U ||
        name.owner.process_id > static_cast<std::uint64_t>(
                                    std::numeric_limits<pid_t>::max()) ||
        name.owner.start_time_ticks == 0U || name.sequence == 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "session cgroup owner and sequence fields must be positive and representable"};
    }
    return std::string(kSessionCgroupV2Prefix) +
           format_compact_boot_id(name.owner.boot_id) + "_" +
           std::to_string(name.owner.process_id) + "_" +
           std::to_string(name.owner.start_time_ticks) + "_" +
           std::to_string(name.sequence);
}

Result<bool> cgroup_owner_is_live(const CgroupOwnerIdentity &owner) {
    if (owner.process_id == 0U ||
        owner.process_id > static_cast<std::uint64_t>(
                               std::numeric_limits<pid_t>::max()) ||
        owner.start_time_ticks == 0U) {
        return Status{ErrorCode::invalid_argument,
                      "session cgroup owner identity is invalid"};
    }
    auto current_boot = read_current_boot_id();
    if (!current_boot.ok()) return current_boot.status();
    if (current_boot.value() != owner.boot_id) return false;

    // Pin the numeric PID to one task before consulting procfs. This closes
    // the exit/reuse window around the starttime comparison and gives us a
    // pollable, kernel-authenticated terminal-state check. A task that exits
    // after the final poll may be conservatively preserved until the next
    // recovery pass, but it can never authorize killing a live replacement.
    auto pidfd = open_process_pidfd(owner.process_id);
    if (!pidfd.ok()) {
        if (pidfd.status().code() == ErrorCode::not_found) return false;
        return pidfd.status();
    }
    auto exited = pidfd_process_exited(pidfd.value().get());
    if (!exited.ok()) return exited.status();
    if (exited.value()) return false;

    auto process = read_process_stat(owner.process_id);
    if (!process.ok()) {
        if (process.status().code() == ErrorCode::not_found) {
            auto exited_after_proc = pidfd_process_exited(pidfd.value().get());
            if (!exited_after_proc.ok()) return exited_after_proc.status();
            if (exited_after_proc.value()) return false;
        }
        return process.status();
    }
    if (process.value().start_time_ticks != owner.start_time_ticks) {
        return false;
    }
    switch (process.value().state) {
        case 'Z':
        case 'X':
        case 'x':
            return false;
        default:
            break;
    }
    auto exited_after_stat = pidfd_process_exited(pidfd.value().get());
    if (!exited_after_stat.ok()) return exited_after_stat.status();
    return !exited_after_stat.value();
}

Result<CgroupEvents> parse_cgroup_events(std::string_view record) {
    if (record.empty() || record.size() > kMaximumCgroupRecordBytes ||
        record.back() != '\n') {
        return Status{ErrorCode::protocol_error,
                      "cgroup.events is empty, oversized, or unterminated"};
    }
    CgroupEvents events;
    bool populated_seen = false;
    std::set<std::string_view> keys;
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        if (end == std::string_view::npos || end == cursor) {
            return Status{ErrorCode::protocol_error,
                          "cgroup.events contains a malformed line"};
        }
        const std::string_view line = record.substr(cursor, end - cursor);
        const std::size_t separator = line.find(' ');
        if (separator == std::string_view::npos || separator == 0U ||
            separator + 1U >= line.size() ||
            line.find(' ', separator + 1U) != std::string_view::npos) {
            return Status{ErrorCode::protocol_error,
                          "cgroup.events contains a malformed key/value pair"};
        }
        const std::string_view key = line.substr(0U, separator);
        const std::string_view value = line.substr(separator + 1U);
        if (!valid_flat_key(key) || !keys.insert(key).second) {
            return Status{ErrorCode::protocol_error,
                          "cgroup.events contains an invalid or duplicate key"};
        }
        auto parsed_value = parse_flat_value(value);
        if (!parsed_value.ok()) return parsed_value.status();
        if (key == "populated") {
            if (parsed_value.value() > 1U) {
                return Status{ErrorCode::protocol_error,
                              "cgroup.events populated value is not boolean"};
            }
            populated_seen = true;
            events.populated = parsed_value.value() == 1U;
        } else if (key == "frozen") {
            if (parsed_value.value() > 1U) {
                return Status{ErrorCode::protocol_error,
                              "cgroup.events frozen value is not boolean"};
            }
            events.frozen = parsed_value.value() == 1U;
        }
        cursor = end + 1U;
    }
    if (!populated_seen) {
        return Status{ErrorCode::protocol_error,
                      "cgroup.events omitted the populated field"};
    }
    return events;
}

Result<CgroupPidsEvents> parse_cgroup_pids_events(
    std::string_view record) {
    auto fields = parse_flat_counter_record(record, "pids.events");
    if (!fields.ok()) return fields.status();
    const std::uint64_t *maximum = find_counter(fields.value(), "max");
    if (maximum == nullptr) {
        return Status{ErrorCode::protocol_error,
                      "pids.events omitted the max field"};
    }
    return CgroupPidsEvents{*maximum};
}

Result<CgroupMemoryEvents> parse_cgroup_memory_events(
    std::string_view record) {
    auto fields = parse_flat_counter_record(record, "memory.events");
    if (!fields.ok()) return fields.status();
    const std::uint64_t *high = find_counter(fields.value(), "high");
    const std::uint64_t *maximum = find_counter(fields.value(), "max");
    const std::uint64_t *oom = find_counter(fields.value(), "oom");
    const std::uint64_t *oom_kill = find_counter(fields.value(), "oom_kill");
    if (high == nullptr || maximum == nullptr || oom == nullptr ||
        oom_kill == nullptr) {
        return Status{
            ErrorCode::protocol_error,
            "memory.events omitted a mandatory outcome field"};
    }
    const std::uint64_t *oom_group_kill =
        find_counter(fields.value(), "oom_group_kill");
    return CgroupMemoryEvents{
        *high, *maximum, *oom, *oom_kill,
        oom_group_kill == nullptr ? 0U : *oom_group_kill};
}

Result<CgroupMemoryStat> parse_cgroup_memory_stat(
    std::string_view record) {
    auto fields = parse_flat_counter_record(record, "memory.stat");
    if (!fields.ok()) return fields.status();
    const std::uint64_t *page_faults =
        find_counter(fields.value(), "pgfault");
    const std::uint64_t *major_page_faults =
        find_counter(fields.value(), "pgmajfault");
    if (page_faults == nullptr || major_page_faults == nullptr) {
        return Status{
            ErrorCode::protocol_error,
            "memory.stat omitted a mandatory fault-accounting field"};
    }

    const std::uint64_t *pages_scanned =
        find_counter(fields.value(), "pgscan");
    const std::uint64_t *pages_reclaimed =
        find_counter(fields.value(), "pgsteal");
    const bool has_any_reclaim =
        pages_scanned != nullptr || pages_reclaimed != nullptr;
    const bool has_all_reclaim =
        pages_scanned != nullptr && pages_reclaimed != nullptr;
    if (has_any_reclaim != has_all_reclaim) {
        return Status{ErrorCode::protocol_error,
                      "memory.stat contains a partial reclaim tuple"};
    }

    const std::uint64_t *pages_in = find_counter(fields.value(), "pswpin");
    const std::uint64_t *pages_out = find_counter(fields.value(), "pswpout");
    const bool has_any_swap = pages_in != nullptr || pages_out != nullptr;
    const bool has_all_swap = pages_in != nullptr && pages_out != nullptr;
    if (has_any_swap != has_all_swap) {
        return Status{ErrorCode::protocol_error,
                      "memory.stat contains a partial swap tuple"};
    }

    CgroupMemoryStat parsed{
        *page_faults, *major_page_faults, std::nullopt, std::nullopt};
    if (has_all_reclaim) {
        parsed.reclaim =
            CgroupMemoryReclaimStat{*pages_scanned, *pages_reclaimed};
    }
    if (has_all_swap) {
        parsed.swap = CgroupMemorySwapStat{*pages_in, *pages_out};
    }
    return parsed;
}

Result<CgroupMemorySwapEvents> parse_cgroup_memory_swap_events(
    std::string_view record) {
    auto fields = parse_flat_counter_record(record, "memory.swap.events");
    if (!fields.ok()) return fields.status();
    const std::uint64_t *high = find_counter(fields.value(), "high");
    const std::uint64_t *maximum = find_counter(fields.value(), "max");
    const std::uint64_t *fail = find_counter(fields.value(), "fail");
    if (high == nullptr || maximum == nullptr || fail == nullptr) {
        return Status{
            ErrorCode::protocol_error,
            "memory.swap.events omitted a mandatory outcome field"};
    }
    return CgroupMemorySwapEvents{*high, *maximum, *fail};
}

Result<CgroupLocalStat> parse_cgroup_local_stat(std::string_view record) {
    auto fields = parse_flat_counter_record(record, "cgroup.stat.local");
    if (!fields.ok()) return fields.status();
    const std::uint64_t *frozen =
        find_counter(fields.value(), "frozen_usec");
    if (frozen == nullptr) {
        return Status{ErrorCode::protocol_error,
                      "cgroup.stat.local omitted the frozen_usec field"};
    }
    return CgroupLocalStat{*frozen};
}

Result<CgroupCpuStat> parse_cgroup_cpu_stat(std::string_view record) {
    auto fields = parse_flat_counter_record(record, "cpu.stat");
    if (!fields.ok()) return fields.status();
    const std::uint64_t *usage = find_counter(fields.value(), "usage_usec");
    const std::uint64_t *user = find_counter(fields.value(), "user_usec");
    const std::uint64_t *system = find_counter(fields.value(), "system_usec");
    if (usage == nullptr || user == nullptr || system == nullptr) {
        return Status{ErrorCode::protocol_error,
                      "cpu.stat omitted a mandatory work-accounting field"};
    }

    const std::uint64_t *periods = find_counter(fields.value(), "nr_periods");
    const std::uint64_t *throttled =
        find_counter(fields.value(), "nr_throttled");
    const std::uint64_t *throttled_time =
        find_counter(fields.value(), "throttled_usec");
    const bool has_any_bandwidth =
        periods != nullptr || throttled != nullptr || throttled_time != nullptr;
    const bool has_all_bandwidth =
        periods != nullptr && throttled != nullptr && throttled_time != nullptr;
    if (has_any_bandwidth != has_all_bandwidth) {
        return Status{ErrorCode::protocol_error,
                      "cpu.stat contains a partial bandwidth tuple"};
    }

    const std::uint64_t *bursts = find_counter(fields.value(), "nr_bursts");
    const std::uint64_t *burst_time = find_counter(fields.value(), "burst_usec");
    const bool has_any_burst = bursts != nullptr || burst_time != nullptr;
    const bool has_all_burst = bursts != nullptr && burst_time != nullptr;
    if (has_any_burst != has_all_burst ||
        (has_all_burst && !has_all_bandwidth)) {
        return Status{ErrorCode::protocol_error,
                      "cpu.stat contains a partial or detached burst tuple"};
    }

    CgroupCpuStat parsed{*usage, *user, *system, std::nullopt};
    if (has_all_bandwidth) {
        parsed.bandwidth = CgroupCpuBandwidthStat{
            *periods, *throttled, *throttled_time, std::nullopt};
        if (has_all_burst) {
            parsed.bandwidth->burst = CgroupCpuBurstStat{*bursts, *burst_time};
        }
    }
    return parsed;
}

Result<std::uint64_t> parse_cgroup_peak(std::string_view record) {
    constexpr std::string_view kLabel{"cgroup peak"};
    if (record.empty() || record.size() > 64U || record.back() != '\n' ||
        record.find('\n') != record.size() - 1U) {
        return Status{ErrorCode::protocol_error,
                      "cgroup peak is empty, oversized, or noncanonical"};
    }
    record.remove_suffix(1U);
    return parse_canonical_unsigned(record, kLabel);
}

namespace {

struct PressureClasses {
    std::optional<CgroupPressureClassSample> some;
    std::optional<CgroupPressureClassSample> full;
};

[[nodiscard]] Result<PressureClasses> parse_pressure_classes(
    std::string_view record) {
    constexpr std::string_view kLabel{"cgroup pressure"};
    if (record.empty() || record.size() > kMaximumCgroupRecordBytes ||
        record.back() != '\n') {
        return Status{ErrorCode::protocol_error,
                      "cgroup pressure is empty, oversized, or unterminated"};
    }

    PressureClasses pressure;
    std::set<std::string> classes;
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        if (end == std::string_view::npos || end == cursor) {
            return Status{ErrorCode::protocol_error,
                          "cgroup pressure contains a malformed line"};
        }
        const std::string_view line = record.substr(cursor, end - cursor);
        const std::size_t first_space = line.find(' ');
        if (first_space == std::string_view::npos || first_space == 0U ||
            first_space + 1U >= line.size()) {
            return Status{ErrorCode::protocol_error,
                          "cgroup pressure contains a malformed class line"};
        }
        const std::string_view pressure_class = line.substr(0U, first_space);
        if (!valid_flat_key(pressure_class) ||
            !classes.emplace(pressure_class).second) {
            return Status{
                ErrorCode::protocol_error,
                "cgroup pressure contains an invalid or duplicate class"};
        }

        std::optional<std::uint16_t> average_10;
        std::optional<std::uint16_t> average_60;
        std::optional<std::uint16_t> average_300;
        std::optional<std::uint64_t> total;
        std::set<std::string> keys;
        std::size_t field_cursor = first_space + 1U;
        while (field_cursor < line.size()) {
            const std::size_t separator = line.find(' ', field_cursor);
            const std::size_t field_end =
                separator == std::string_view::npos ? line.size() : separator;
            if (field_end == field_cursor) {
                return Status{ErrorCode::protocol_error,
                              "cgroup pressure contains noncanonical spacing"};
            }
            const std::string_view field =
                line.substr(field_cursor, field_end - field_cursor);
            const std::size_t equals = field.find('=');
            if (equals == std::string_view::npos || equals == 0U ||
                equals + 1U >= field.size() ||
                field.find('=', equals + 1U) != std::string_view::npos) {
                return Status{ErrorCode::protocol_error,
                              "cgroup pressure contains a malformed keyed value"};
            }
            const std::string_view key = field.substr(0U, equals);
            const std::string_view value = field.substr(equals + 1U);
            if (!valid_flat_key(key) || !keys.emplace(key).second) {
                return Status{
                    ErrorCode::protocol_error,
                    "cgroup pressure contains an invalid or duplicate key"};
            }

            if (key == "total") {
                auto parsed = parse_canonical_unsigned(value, kLabel);
                if (!parsed.ok()) return parsed.status();
                total = parsed.value();
            } else if (key == "avg10" || key == "avg60" ||
                       key == "avg300") {
                auto parsed = parse_psi_percentage_basis_points(value, kLabel);
                if (!parsed.ok()) return parsed.status();
                if (key == "avg10") {
                    average_10 = parsed.value();
                } else if (key == "avg60") {
                    average_60 = parsed.value();
                } else {
                    average_300 = parsed.value();
                }
            } else {
                const Status valid = validate_future_psi_value(value, kLabel);
                if (!valid.ok()) return valid;
            }

            if (separator == std::string_view::npos) break;
            field_cursor = separator + 1U;
            if (field_cursor == line.size() || line[field_cursor] == ' ') {
                return Status{ErrorCode::protocol_error,
                              "cgroup pressure contains noncanonical spacing"};
            }
        }

        if (pressure_class == "some" || pressure_class == "full") {
            if (!average_10.has_value() || !average_60.has_value() ||
                !average_300.has_value() || !total.has_value()) {
                return Status{
                    ErrorCode::protocol_error,
                    "cgroup pressure omitted a mandatory PSI field"};
            }
            CgroupPressureClassSample sample{
                *average_10, *average_60, *average_300, *total};
            if (pressure_class == "some") {
                pressure.some = sample;
            } else {
                pressure.full = sample;
            }
        }
        cursor = end + 1U;
    }

    return pressure;
}

}  // namespace

Result<CgroupPressureSample> parse_cgroup_pressure_sample(
    std::string_view record) {
    auto pressure = parse_pressure_classes(record);
    if (!pressure.ok()) return pressure.status();
    if (!pressure.value().some.has_value()) {
        return Status{ErrorCode::protocol_error,
                      "cgroup pressure omitted the some class"};
    }
    return CgroupPressureSample{
        pressure.value().some, pressure.value().full};
}

Result<CgroupPressure> parse_cgroup_pressure(std::string_view record) {
    auto pressure = parse_cgroup_pressure_sample(record);
    if (!pressure.ok()) return pressure.status();
    return CgroupPressure{
        pressure.value().some->total_microseconds,
        pressure.value().full.has_value()
            ? std::optional<std::uint64_t>{
                  pressure.value().full->total_microseconds}
            : std::nullopt};
}

Result<std::string> encode_cgroup_pressure_trigger(
    CgroupPressureTriggerClass pressure_class,
    std::uint64_t stall_microseconds,
    std::uint64_t window_microseconds) {
    std::string_view class_name;
    switch (pressure_class) {
        case CgroupPressureTriggerClass::some:
            class_name = "some";
            break;
        case CgroupPressureTriggerClass::full:
            class_name = "full";
            break;
        default:
            return Status{
                ErrorCode::invalid_argument,
                "cgroup PSI trigger class is not defined"};
    }

    if (window_microseconds <
            kCgroupMinimumPressureTriggerWindowMicroseconds ||
        window_microseconds >
            kCgroupMaximumPressureTriggerWindowMicroseconds) {
        return Status{
            ErrorCode::invalid_argument,
            "cgroup PSI trigger window must be in 2000000..10000000 microseconds"};
    }
    if (window_microseconds %
            kCgroupPressureTriggerWindowQuantumMicroseconds !=
        0U) {
        return Status{
            ErrorCode::invalid_argument,
            "cgroup PSI trigger window must be a multiple of 2000000 microseconds"};
    }
    if (stall_microseconds == 0U ||
        stall_microseconds > window_microseconds) {
        return Status{
            ErrorCode::invalid_argument,
            "cgroup PSI trigger stall time must be in 1..window microseconds"};
    }

    // The kernel parser currently copies at most 32 bytes. IoTox's bounded
    // policy yields at most 27 bytes including the terminating NUL, but retain
    // explicit headroom and verify each append instead of relying on decimal
    // formatting or locale behavior.
    std::array<char, 32U> record{};
    char *cursor = record.data();
    char *const end = record.data() + record.size();
    const auto append_text = [&cursor, end](std::string_view text) -> bool {
        if (static_cast<std::size_t>(end - cursor) < text.size()) return false;
        std::memcpy(cursor, text.data(), text.size());
        cursor += static_cast<std::ptrdiff_t>(text.size());
        return true;
    };
    const auto append_unsigned = [&cursor, end](std::uint64_t value) -> bool {
        const auto encoded = std::to_chars(cursor, end, value);
        if (encoded.ec != std::errc{}) return false;
        cursor = encoded.ptr;
        return true;
    };

    if (!append_text(class_name) || !append_text(" ") ||
        !append_unsigned(stall_microseconds) || !append_text(" ") ||
        !append_unsigned(window_microseconds) || cursor == end) {
        return Status{
            ErrorCode::internal_error,
            "cgroup PSI trigger record exceeded the canonical buffer"};
    }
    *cursor++ = '\0';

    try {
        return std::string(
            record.data(), static_cast<std::size_t>(cursor - record.data()));
    } catch (const std::bad_alloc &) {
        return Status{
            ErrorCode::resource_exhausted,
            "allocate canonical cgroup PSI trigger record"};
    } catch (...) {
        return Status{
            ErrorCode::internal_error,
            "construct canonical cgroup PSI trigger record"};
    }
}

CgroupPressureMonitorPollDecision
classify_cgroup_pressure_monitor_poll_events(
    CgroupPressureMonitorDescriptorRole role,
    std::uint16_t events) noexcept {
    const auto bits = [](short value) noexcept {
        return static_cast<std::uint16_t>(
            static_cast<unsigned short>(value));
    };
    const std::uint16_t terminal_events = bits(
        static_cast<short>(POLLERR | POLLHUP | POLLNVAL));

    std::uint16_t allowed = terminal_events;
    switch (role) {
        case CgroupPressureMonitorDescriptorRole::stop:
            allowed = static_cast<std::uint16_t>(allowed | bits(POLLIN));
            break;
        case CgroupPressureMonitorDescriptorRole::trigger:
            allowed = static_cast<std::uint16_t>(allowed | bits(POLLPRI));
            break;
        default:
            return CgroupPressureMonitorPollDecision{
                false, false, ErrorCode::protocol_error};
    }

    if ((events & static_cast<std::uint16_t>(~allowed)) != 0U) {
        return CgroupPressureMonitorPollDecision{
            false, false, ErrorCode::protocol_error};
    }

    const bool terminal = (events & terminal_events) != 0U;
    if (role == CgroupPressureMonitorDescriptorRole::stop) {
        if (terminal) {
            return CgroupPressureMonitorPollDecision{
                false, false, ErrorCode::io_error};
        }
        return CgroupPressureMonitorPollDecision{
            (events & bits(POLLIN)) != 0U, false, ErrorCode::ok};
    }

    const bool triggered = (events & bits(POLLPRI)) != 0U;
    return CgroupPressureMonitorPollDecision{
        false, triggered,
        terminal ? ErrorCode::unavailable : ErrorCode::ok};
}

Result<CgroupIrqPressure> parse_cgroup_irq_pressure(
    std::string_view record) {
    auto pressure = parse_pressure_classes(record);
    if (!pressure.ok()) return pressure.status();
    if (!pressure.value().full.has_value()) {
        return Status{ErrorCode::protocol_error,
                      "irq.pressure omitted the full class"};
    }
    return CgroupIrqPressure{pressure.value().full->total_microseconds};
}

Result<CgroupPressureAdmissionDecision> evaluate_cgroup_pressure_admission(
    const CgroupPressureAdmissionLimits &limits,
    const CgroupPressureAdmissionObservation &observation,
    bool currently_closed,
    bool trigger_hold_active) {
    const Status valid = validate_cgroup_pressure_admission_limits(limits);
    if (!valid.ok()) return valid;
    if (limits.empty()) return CgroupPressureAdmissionDecision{};

    const auto require_observation = [](
        const auto &threshold, const auto &observed,
        std::string_view label) -> Status {
        if (threshold.has_value() && !observed.has_value()) {
            return Status{
                ErrorCode::protocol_error,
                "Ratox cgroup pressure admission sample omitted " +
                    std::string(label)};
        }
        return Status::success();
    };
    for (const auto &[threshold, observed, label] : std::array{
             std::tuple{
                 &limits.maximum_cpu_some_average_10_basis_points,
                 &observation.cpu_some_average_10_basis_points,
                 std::string_view{"CPU some avg10"}},
             std::tuple{
                 &limits.maximum_memory_full_average_10_basis_points,
                 &observation.memory_full_average_10_basis_points,
                 std::string_view{"memory full avg10"}},
             std::tuple{
                 &limits.maximum_io_full_average_10_basis_points,
                 &observation.io_full_average_10_basis_points,
                 std::string_view{"I/O full avg10"}},
         }) {
        const Status present = require_observation(*threshold, *observed, label);
        if (!present.ok()) return present;
    }

    if (trigger_hold_active) {
        return CgroupPressureAdmissionDecision{
            false, true, !currently_closed, false};
    }

    const auto exceeds_close_threshold = [](const auto &threshold,
                                             const auto &observed) noexcept {
        return threshold.has_value() && *observed > *threshold;
    };
    const bool close =
        exceeds_close_threshold(
            limits.maximum_cpu_some_average_10_basis_points,
            observation.cpu_some_average_10_basis_points) ||
        exceeds_close_threshold(
            limits.maximum_memory_full_average_10_basis_points,
            observation.memory_full_average_10_basis_points) ||
        exceeds_close_threshold(
            limits.maximum_io_full_average_10_basis_points,
            observation.io_full_average_10_basis_points);

    if (!currently_closed) {
        return CgroupPressureAdmissionDecision{
            !close, close, close, false};
    }

    const auto satisfies_reopen_threshold = [&limits](
                                                const auto &threshold,
                                                const auto &observed) noexcept {
        return !threshold.has_value() ||
               *observed <= static_cast<std::uint16_t>(
                   *threshold - limits.hysteresis_basis_points);
    };
    const bool reopen =
        satisfies_reopen_threshold(
            limits.maximum_cpu_some_average_10_basis_points,
            observation.cpu_some_average_10_basis_points) &&
        satisfies_reopen_threshold(
            limits.maximum_memory_full_average_10_basis_points,
            observation.memory_full_average_10_basis_points) &&
        satisfies_reopen_threshold(
            limits.maximum_io_full_average_10_basis_points,
            observation.io_full_average_10_basis_points);
    return CgroupPressureAdmissionDecision{
        reopen, !reopen, false, reopen};
}

Result<std::vector<CgroupIoMax>> parse_cgroup_io_max(
    std::string_view record) {
    return parse_io_max_record_internal(record);
}

Result<CgroupIoStat> parse_cgroup_io_stat(std::string_view record) {
    if (record.empty()) return CgroupIoStat{};
    if (record.size() > kMaximumCgroupRecordBytes || record.back() != '\n') {
        return Status{ErrorCode::protocol_error,
                      "io.stat is oversized or unterminated"};
    }

    CgroupIoStat totals;
    std::set<std::pair<std::uint32_t, std::uint32_t>> devices;
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        if (end == std::string_view::npos || end == cursor) {
            return Status{ErrorCode::protocol_error,
                          "io.stat contains a malformed line"};
        }
        const std::string_view line = record.substr(cursor, end - cursor);
        const std::size_t first_space = line.find(' ');
        if (first_space == 0U) {
            return Status{ErrorCode::protocol_error,
                          "io.stat contains a malformed device line"};
        }
        const std::size_t device_end =
            first_space == std::string_view::npos ? line.size() : first_space;
        auto device = parse_cgroup_device_key(
            line.substr(0U, device_end), "io.stat");
        if (!device.ok()) return device.status();
        if (!devices.emplace(
                device.value().major, device.value().minor).second) {
            return Status{ErrorCode::protocol_error,
                          "io.stat contains a duplicate device line"};
        }
        if (first_space == std::string_view::npos ||
            first_space + 1U == line.size()) {
            cursor = end + 1U;
            continue;
        }

        std::set<std::string> keys;
        std::optional<std::uint64_t> read_bytes;
        std::optional<std::uint64_t> write_bytes;
        std::optional<std::uint64_t> read_operations;
        std::optional<std::uint64_t> write_operations;
        std::optional<std::uint64_t> discard_bytes;
        std::optional<std::uint64_t> discard_operations;
        std::size_t field_cursor = first_space + 1U;
        while (field_cursor < line.size()) {
            const std::size_t separator = line.find(' ', field_cursor);
            const std::size_t field_end =
                separator == std::string_view::npos ? line.size() : separator;
            if (field_end == field_cursor) {
                return Status{ErrorCode::protocol_error,
                              "io.stat contains noncanonical spacing"};
            }
            const std::string_view field =
                line.substr(field_cursor, field_end - field_cursor);
            const std::size_t equals = field.find('=');
            if (equals == std::string_view::npos || equals == 0U ||
                equals + 1U >= field.size() ||
                field.find('=', equals + 1U) != std::string_view::npos) {
                return Status{ErrorCode::protocol_error,
                              "io.stat contains a malformed keyed value"};
            }
            const std::string_view key = field.substr(0U, equals);
            const std::string_view value = field.substr(equals + 1U);
            if (!valid_flat_key(key) || !keys.emplace(key).second) {
                return Status{ErrorCode::protocol_error,
                              "io.stat contains an invalid or duplicate key"};
            }
            auto numeric = parse_canonical_unsigned(value, "io.stat");
            if (!numeric.ok()) return numeric.status();
            if (key == "rbytes") {
                read_bytes = numeric.value();
            } else if (key == "wbytes") {
                write_bytes = numeric.value();
            } else if (key == "rios") {
                read_operations = numeric.value();
            } else if (key == "wios") {
                write_operations = numeric.value();
            } else if (key == "dbytes") {
                discard_bytes = numeric.value();
            } else if (key == "dios") {
                discard_operations = numeric.value();
            }
            if (separator == std::string_view::npos) break;
            field_cursor = separator + 1U;
            if (field_cursor == line.size() || line[field_cursor] == ' ') {
                return Status{ErrorCode::protocol_error,
                              "io.stat contains noncanonical spacing"};
            }
        }
        if (!read_bytes.has_value() || !write_bytes.has_value() ||
            !read_operations.has_value() || !write_operations.has_value()) {
            return Status{ErrorCode::protocol_error,
                          "io.stat omitted a mandatory read/write counter"};
        }
        if (discard_bytes.has_value() != discard_operations.has_value()) {
            return Status{ErrorCode::protocol_error,
                          "io.stat omitted one member of the discard counter pair"};
        }
        saturating_add(totals.read_bytes, *read_bytes);
        saturating_add(totals.write_bytes, *write_bytes);
        saturating_add(totals.read_operations, *read_operations);
        saturating_add(totals.write_operations, *write_operations);
        saturating_add(totals.discard_bytes, discard_bytes.value_or(0U));
        saturating_add(
            totals.discard_operations, discard_operations.value_or(0U));
        cursor = end + 1U;
    }
    return totals;
}

[[nodiscard]] Status write_pressure_trigger_record(
    int descriptor, CgroupPressureTriggerClass pressure_class,
    std::uint64_t stall_microseconds,
    std::uint64_t window_microseconds,
    std::string_view label) {
    auto encoded = encode_cgroup_pressure_trigger(
        pressure_class, stall_microseconds, window_microseconds);
    if (!encoded.ok()) return encoded.status();
    const std::string &record = encoded.value();
    ssize_t count = -1;
    do {
        count = ::write(descriptor, record.data(), record.size());
    } while (count < 0 && errno == EINTR);
    if (count < 0) {
        ErrorCode code = ErrorCode::io_error;
        if (errno == EOPNOTSUPP || errno == ENOSYS) {
            code = ErrorCode::unsupported;
        } else if (errno == EACCES || errno == EPERM || errno == EROFS ||
                   errno == EINVAL || errno == EBUSY) {
            code = ErrorCode::unavailable;
        } else if (errno == ENFILE || errno == EMFILE || errno == ENOMEM ||
                   errno == ENOSPC) {
            code = ErrorCode::resource_exhausted;
        }
        return errno_status(
            code, "register cgroup PSI trigger on " + std::string(label));
    }
    if (count != static_cast<ssize_t>(record.size())) {
        return Status{
            ErrorCode::io_error,
            "cgroup PSI trigger on " + std::string(label) +
                " accepted a short write"};
    }
    return Status::success();
}

struct CgroupPressureAdmission::State {
    enum class TriggerKind : std::uint8_t {
        cpu_some = 1U,
        memory_full = 2U,
        io_full = 3U,
    };

    struct TriggerDescriptor {
        TriggerKind kind;
        FileDescriptor descriptor;
    };

    explicit State(CgroupPressureAdmissionLimits configured_limits)
        : limits(std::move(configured_limits)),
          trigger_monitor_healthy(limits.triggers_empty()) {}

    ~State() {
        stop_requested.store(true, std::memory_order_release);
        if (stop_event.get() >= 0) {
            const std::uint64_t signal = 1U;
            ssize_t written = -1;
            do {
                written = ::write(stop_event.get(), &signal, sizeof(signal));
            } while (written < 0 && errno == EINTR);
            // EAGAIN means the event counter already carries a wakeup. All
            // teardown paths still join before closing descriptor-pinned PSI
            // trigger registrations.
        }
        if (monitor.joinable()) monitor.join();
    }

    State(const State &) = delete;
    State &operator=(const State &) = delete;

    [[nodiscard]] Result<CgroupPressureAdmissionObservation> sample() {
        const auto require_accounting_enabled = [this]() -> Status {
            auto accounting = read_control_record(
                pressure_control.get(), "cgroup.pressure", 16U);
            if (!accounting.ok()) return accounting.status();
            if (accounting.value() != "1\n") {
                return Status{
                    ErrorCode::unavailable,
                    "Ratox cgroup pressure admission requires cgroup.pressure=1"};
            }
            return Status::success();
        };
        const Status accounting_before = require_accounting_enabled();
        if (!accounting_before.ok()) return accounting_before;

        CgroupPressureAdmissionObservation observation;
        const auto read_sample = [](int descriptor, std::string_view label)
            -> Result<CgroupPressureSample> {
            auto record = read_control_record(descriptor, label);
            if (!record.ok()) return record.status();
            return parse_cgroup_pressure_sample(record.value());
        };
        if (cpu_pressure.get() >= 0) {
            auto parsed = read_sample(cpu_pressure.get(), "cpu.pressure");
            if (!parsed.ok()) return parsed.status();
            observation.cpu_some_average_10_basis_points =
                parsed.value().some->average_10_basis_points;
        }
        if (memory_pressure.get() >= 0) {
            auto parsed = read_sample(memory_pressure.get(), "memory.pressure");
            if (!parsed.ok()) return parsed.status();
            if (!parsed.value().full.has_value()) {
                return Status{
                    ErrorCode::protocol_error,
                    "memory.pressure omitted the full class required by Ratox admission"};
            }
            observation.memory_full_average_10_basis_points =
                parsed.value().full->average_10_basis_points;
        }
        if (io_pressure.get() >= 0) {
            auto parsed = read_sample(io_pressure.get(), "io.pressure");
            if (!parsed.ok()) return parsed.status();
            if (!parsed.value().full.has_value()) {
                return Status{
                    ErrorCode::protocol_error,
                    "io.pressure omitted the full class required by Ratox admission"};
            }
            observation.io_full_average_10_basis_points =
                parsed.value().full->average_10_basis_points;
        }
        // A privileged single writer is part of the delegated-root contract,
        // but recheck the non-hierarchical accounting switch so a disable that
        // persists across the sample cannot be reported as valid evidence.
        const Status accounting_after = require_accounting_enabled();
        if (!accounting_after.ok()) return accounting_after;
        return observation;
    }

    [[nodiscard]] Status reserve_trigger_descriptors() {
        const std::size_t required =
            static_cast<std::size_t>(
                limits.cpu_some_trigger_stall_microseconds.has_value()) +
            static_cast<std::size_t>(
                limits.memory_full_trigger_stall_microseconds.has_value()) +
            static_cast<std::size_t>(
                limits.io_full_trigger_stall_microseconds.has_value());
        try {
            triggers.reserve(required);
        } catch (const std::bad_alloc &) {
            return Status{
                ErrorCode::resource_exhausted,
                "allocate Ratox PSI trigger descriptor set"};
        } catch (...) {
            return Status{
                ErrorCode::internal_error,
                "construct Ratox PSI trigger descriptor set"};
        }
        return Status::success();
    }

    [[nodiscard]] Status add_trigger(
        TriggerKind kind, std::string_view file_name,
        CgroupPressureTriggerClass pressure_class,
        std::uint64_t stall_microseconds) {
        auto opened = open_control_file(
            root.get(), file_name, O_RDWR | O_NONBLOCK);
        if (!opened.ok()) return opened.status();
        const Status protected_control =
            verify_daemon_control_boundary(opened.value().get(), file_name);
        if (!protected_control.ok()) return protected_control;

        const Status registered = write_pressure_trigger_record(
            opened.value().get(), pressure_class, stall_microseconds,
            *limits.trigger_window_microseconds, file_name);
        if (!registered.ok()) return registered;

        // create() reserves the complete vector before registering any
        // kernel trigger. Keep a local guard as well: a future caller or type
        // change must fail closed instead of allowing an allocation exception
        // to cross this Result-returning boundary after registration.
        if (triggers.size() == triggers.capacity()) {
            return Status{
                ErrorCode::internal_error,
                "Ratox PSI trigger descriptor capacity invariant failed"};
        }
        try {
            triggers.push_back(
                TriggerDescriptor{kind, std::move(opened).value()});
        } catch (const std::bad_alloc &) {
            return Status{
                ErrorCode::resource_exhausted,
                "retain Ratox PSI trigger descriptor"};
        } catch (...) {
            return Status{
                ErrorCode::internal_error,
                "retain Ratox PSI trigger descriptor"};
        }
        return Status::success();
    }

    [[nodiscard]] Status start_monitor() {
        if (triggers.empty()) return Status::success();

        FileDescriptor wakeup(::eventfd(0U, EFD_CLOEXEC | EFD_NONBLOCK));
        if (wakeup.get() < 0) {
            const ErrorCode code =
                errno == EMFILE || errno == ENFILE || errno == ENOMEM
                    ? ErrorCode::resource_exhausted
                    : ErrorCode::io_error;
            return errno_status(code, "create Ratox PSI monitor wakeup");
        }
        stop_event = std::move(wakeup);

        // Build the complete poll set synchronously. Once create() succeeds,
        // the monitor loop performs no allocation and cannot silently degrade
        // because its first vector growth failed on the worker thread.
        std::vector<struct pollfd> observed;
        try {
            observed.reserve(triggers.size() + 1U);
            observed.push_back(
                pollfd{stop_event.get(), static_cast<short>(POLLIN), 0});
            for (const TriggerDescriptor &trigger : triggers) {
                observed.push_back(pollfd{
                    trigger.descriptor.get(),
                    static_cast<short>(POLLPRI), 0});
            }
        } catch (const std::bad_alloc &) {
            trigger_monitor_error_code = ErrorCode::resource_exhausted;
            return Status{
                ErrorCode::resource_exhausted,
                "allocate Ratox PSI trigger monitor poll set"};
        } catch (...) {
            trigger_monitor_error_code = ErrorCode::internal_error;
            return Status{
                ErrorCode::internal_error,
                "construct Ratox PSI trigger monitor poll set"};
        }

        trigger_monitor_healthy = true;
        trigger_monitor_error_code = ErrorCode::ok;
        try {
            monitor = std::thread(
                [this, observed = std::move(observed)]() mutable noexcept {
                    monitor_loop(std::move(observed));
                });
        } catch (const std::system_error &error) {
            trigger_monitor_healthy = false;
            const std::error_code code = error.code();
            const bool exhausted =
                code == std::errc::resource_unavailable_try_again ||
                code == std::errc::not_enough_memory;
            trigger_monitor_error_code =
                exhausted ? ErrorCode::resource_exhausted
                          : ErrorCode::internal_error;
            return Status{
                trigger_monitor_error_code,
                "start Ratox PSI trigger monitor: " +
                    std::string(error.what())};
        } catch (...) {
            trigger_monitor_healthy = false;
            trigger_monitor_error_code = ErrorCode::internal_error;
            return Status{
                ErrorCode::internal_error,
                "start Ratox PSI trigger monitor failed"};
        }
        return Status::success();
    }

    [[nodiscard]] bool trigger_hold_active_locked(
        std::chrono::steady_clock::time_point now) const noexcept {
        return !limits.triggers_empty() && now < trigger_hold_until;
    }

    [[nodiscard]] std::uint64_t trigger_hold_remaining_microseconds_locked(
        std::chrono::steady_clock::time_point now) const noexcept {
        if (!trigger_hold_active_locked(now)) return 0U;
        const auto remaining = std::chrono::ceil<std::chrono::microseconds>(
            trigger_hold_until - now);
        if (remaining.count() <= 0) return 0U;
        return static_cast<std::uint64_t>(remaining.count());
    }

    void drain_pending_locked(
        std::chrono::steady_clock::time_point now) noexcept {
        const std::uint64_t cpu_events =
            pending_cpu_some_trigger_events.exchange(
                0U, std::memory_order_acq_rel);
        const std::uint64_t memory_events =
            pending_memory_full_trigger_events.exchange(
                0U, std::memory_order_acq_rel);
        const std::uint64_t io_events =
            pending_io_full_trigger_events.exchange(
                0U, std::memory_order_acq_rel);

        std::uint64_t newly_observed = 0U;
        saturating_add(newly_observed, cpu_events);
        saturating_add(newly_observed, memory_events);
        saturating_add(newly_observed, io_events);
        if (newly_observed != 0U) {
            saturating_add(trigger_events, newly_observed);
            saturating_add(cpu_some_trigger_events, cpu_events);
            saturating_add(memory_full_trigger_events, memory_events);
            saturating_add(io_full_trigger_events, io_events);
            const auto candidate =
                now + std::chrono::microseconds{
                          *limits.trigger_window_microseconds};
            if (candidate > trigger_hold_until) {
                trigger_hold_until = candidate;
            }
            if (!closed) {
                closed = true;
                saturating_increment(closed_transitions);
                saturating_increment(trigger_closed_transitions);
            }
        }

        const ErrorCode monitor_error =
            pending_monitor_error.exchange(
                ErrorCode::ok, std::memory_order_acq_rel);
        if (monitor_error != ErrorCode::ok) {
            trigger_monitor_healthy = false;
            trigger_monitor_error_code = monitor_error;
            saturating_increment(trigger_monitor_failures);
            if (!closed) {
                closed = true;
                saturating_increment(closed_transitions);
            }
        }
    }

    void queue_trigger(TriggerKind kind) noexcept {
        switch (kind) {
            case TriggerKind::cpu_some:
                atomic_saturating_increment(
                    pending_cpu_some_trigger_events);
                break;
            case TriggerKind::memory_full:
                atomic_saturating_increment(
                    pending_memory_full_trigger_events);
                break;
            case TriggerKind::io_full:
                atomic_saturating_increment(
                    pending_io_full_trigger_events);
                break;
        }
    }

    void queue_monitor_failure(ErrorCode code) noexcept {
        ErrorCode expected = ErrorCode::ok;
        static_cast<void>(pending_monitor_error.compare_exchange_strong(
            expected, code, std::memory_order_release,
            std::memory_order_relaxed));
        std::scoped_lock lock(mutex);
        drain_pending_locked(std::chrono::steady_clock::now());
    }

    void monitor_loop(std::vector<struct pollfd> observed) noexcept {
        try {
            if (observed.size() != triggers.size() + 1U) {
                queue_monitor_failure(ErrorCode::protocol_error);
                return;
            }
            while (true) {
                for (struct pollfd &descriptor : observed) {
                    descriptor.revents = 0;
                }
                const int ready = ::poll(
                    observed.data(), static_cast<nfds_t>(observed.size()), -1);
                if (ready < 0) {
                    if (errno == EINTR) continue;
                    const ErrorCode code = errno == ENOMEM
                                               ? ErrorCode::resource_exhausted
                                               : ErrorCode::io_error;
                    queue_monitor_failure(code);
                    return;
                }
                if (ready == 0) {
                    queue_monitor_failure(ErrorCode::protocol_error);
                    return;
                }

                std::size_t descriptors_ready = 0U;
                for (const struct pollfd &descriptor : observed) {
                    if (descriptor.revents != 0) ++descriptors_ready;
                }
                if (descriptors_ready != static_cast<std::size_t>(ready)) {
                    queue_monitor_failure(ErrorCode::protocol_error);
                    return;
                }

                const auto stop_decision =
                    classify_cgroup_pressure_monitor_poll_events(
                        CgroupPressureMonitorDescriptorRole::stop,
                        static_cast<std::uint16_t>(
                            static_cast<unsigned short>(
                                observed.front().revents)));
                if (stop_decision.failure_code != ErrorCode::ok) {
                    queue_monitor_failure(stop_decision.failure_code);
                    return;
                }
                if (stop_decision.stop_requested ||
                    stop_requested.load(std::memory_order_acquire)) {
                    return;
                }

                bool trigger_observed = false;
                ErrorCode source_error = ErrorCode::ok;
                for (std::size_t index = 0U; index < triggers.size(); ++index) {
                    const auto decision =
                        classify_cgroup_pressure_monitor_poll_events(
                            CgroupPressureMonitorDescriptorRole::trigger,
                            static_cast<std::uint16_t>(
                                static_cast<unsigned short>(
                                    observed[index + 1U].revents)));
                    if (decision.trigger_observed) {
                        queue_trigger(triggers[index].kind);
                        trigger_observed = true;
                    }
                    if (decision.failure_code != ErrorCode::ok) {
                        source_error = decision.failure_code;
                        break;
                    }
                }
                if (trigger_observed) {
                    std::scoped_lock lock(mutex);
                    drain_pending_locked(std::chrono::steady_clock::now());
                }
                if (source_error != ErrorCode::ok) {
                    queue_monitor_failure(source_error);
                    return;
                }
            }
        } catch (...) {
            queue_monitor_failure(ErrorCode::internal_error);
        }
    }

    mutable std::mutex mutex;
    CgroupPressureAdmissionLimits limits;
    FileDescriptor root;
    FileDescriptor pressure_control;
    FileDescriptor cpu_pressure;
    FileDescriptor memory_pressure;
    FileDescriptor io_pressure;
    std::vector<TriggerDescriptor> triggers;
    FileDescriptor stop_event;
    std::thread monitor;
    std::atomic<bool> stop_requested{false};
    std::atomic<std::uint64_t> pending_cpu_some_trigger_events{0U};
    std::atomic<std::uint64_t> pending_memory_full_trigger_events{0U};
    std::atomic<std::uint64_t> pending_io_full_trigger_events{0U};
    std::atomic<ErrorCode> pending_monitor_error{ErrorCode::ok};
    bool closed{false};
    std::uint64_t checks{0U};
    std::uint64_t admitted{0U};
    std::uint64_t rejections{0U};
    std::uint64_t sampling_failures{0U};
    std::uint64_t closed_transitions{0U};
    std::uint64_t reopened_transitions{0U};
    bool trigger_monitor_healthy{true};
    ErrorCode trigger_monitor_error_code{ErrorCode::ok};
    std::uint64_t trigger_events{0U};
    std::uint64_t cpu_some_trigger_events{0U};
    std::uint64_t memory_full_trigger_events{0U};
    std::uint64_t io_full_trigger_events{0U};
    std::uint64_t trigger_monitor_failures{0U};
    std::uint64_t trigger_closed_transitions{0U};
    std::uint64_t trigger_hold_rejections{0U};
    std::chrono::steady_clock::time_point trigger_hold_until{
        std::chrono::steady_clock::time_point::min()};
    bool last_sample_valid{false};
    ErrorCode last_sampling_error_code{ErrorCode::ok};
    CgroupPressureAdmissionObservation last_observation;
};
CgroupPressureAdmission::CgroupPressureAdmission(
    std::shared_ptr<State> state) noexcept
    : state_(std::move(state)) {}

Result<std::shared_ptr<CgroupPressureAdmission>>
CgroupPressureAdmission::create(
    const std::filesystem::path &delegated_root,
    CgroupPressureAdmissionLimits limits) {
    const Status valid = validate_cgroup_pressure_admission_limits(limits);
    if (!valid.ok()) return valid;
    auto state = std::make_shared<State>(std::move(limits));
    if (state->limits.empty()) {
        return std::shared_ptr<CgroupPressureAdmission>(
            new CgroupPressureAdmission(std::move(state)));
    }
    if (delegated_root.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup pressure admission requires a delegated cgroup root"};
    }

    auto root = open_absolute_directory_without_symlinks(delegated_root);
    if (!root.ok()) return root.status();
    const Status cgroup2 = require_cgroup2_filesystem(
        root.value().get(), "Ratox pressure admission cgroup root");
    if (!cgroup2.ok()) return cgroup2;
    const Status boundary = verify_daemon_owned_boundary(
        root.value().get(), "Ratox pressure admission cgroup root", true);
    if (!boundary.ok()) return boundary;
    state->root = std::move(root).value();

    const auto open_required = [&state](
                                   std::string_view name,
                                   FileDescriptor &destination) -> Status {
        auto opened = open_control_file(state->root.get(), name, O_RDONLY);
        if (!opened.ok()) return opened.status();
        const Status protected_control =
            verify_daemon_control_boundary(opened.value().get(), name);
        if (!protected_control.ok()) return protected_control;
        destination = std::move(opened).value();
        return Status::success();
    };

    Status opened = open_required(
        "cgroup.pressure", state->pressure_control);
    if (!opened.ok()) return opened;
    if (state->limits.maximum_cpu_some_average_10_basis_points.has_value()) {
        opened = open_required("cpu.pressure", state->cpu_pressure);
        if (!opened.ok()) return opened;
    }
    if (state->limits.maximum_memory_full_average_10_basis_points.has_value()) {
        opened = open_required("memory.pressure", state->memory_pressure);
        if (!opened.ok()) return opened;
    }
    if (state->limits.maximum_io_full_average_10_basis_points.has_value()) {
        opened = open_required("io.pressure", state->io_pressure);
        if (!opened.ok()) return opened;
    }

    // Preflight the complete descriptor-pinned sample before registering
    // asynchronous triggers. Startup may proceed while the host is pressured;
    // the first actual admission then closes the avg10 gate. Unsupported PSI
    // syntax, accounting, ownership, or pressure classes fail startup.
    auto sample = state->sample();
    if (!sample.ok()) return sample.status();
    auto decision = evaluate_cgroup_pressure_admission(
        state->limits, sample.value(), false);
    if (!decision.ok()) return decision.status();

    // Allocate the complete descriptor set before the first registration.
    // Each registered PSI trigger is a kernel-side resource bound to its file
    // descriptor, so memory exhaustion must be discovered before any partial
    // registration side effect rather than between otherwise valid triggers.
    opened = state->reserve_trigger_descriptors();
    if (!opened.ok()) return opened;

    if (state->limits.cpu_some_trigger_stall_microseconds.has_value()) {
        opened = state->add_trigger(
            State::TriggerKind::cpu_some, "cpu.pressure",
            CgroupPressureTriggerClass::some,
            *state->limits.cpu_some_trigger_stall_microseconds);
        if (!opened.ok()) return opened;
    }
    if (state->limits.memory_full_trigger_stall_microseconds.has_value()) {
        opened = state->add_trigger(
            State::TriggerKind::memory_full, "memory.pressure",
            CgroupPressureTriggerClass::full,
            *state->limits.memory_full_trigger_stall_microseconds);
        if (!opened.ok()) return opened;
    }
    if (state->limits.io_full_trigger_stall_microseconds.has_value()) {
        opened = state->add_trigger(
            State::TriggerKind::io_full, "io.pressure",
            CgroupPressureTriggerClass::full,
            *state->limits.io_full_trigger_stall_microseconds);
        if (!opened.ok()) return opened;
    }
    const Status monitored = state->start_monitor();
    if (!monitored.ok()) return monitored;

    return std::shared_ptr<CgroupPressureAdmission>(
        new CgroupPressureAdmission(std::move(state)));
}

Status CgroupPressureAdmission::admit() {
    if (!state_) {
        return Status{
            ErrorCode::internal_error,
            "Ratox cgroup pressure admission state is unavailable"};
    }
    std::scoped_lock lock(state_->mutex);
    if (state_->limits.empty()) return Status::success();

    saturating_increment(state_->checks);
    state_->drain_pending_locked(std::chrono::steady_clock::now());
    if (!state_->trigger_monitor_healthy) {
        saturating_increment(state_->rejections);
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup PSI trigger monitor failed closed"};
    }

    auto observation = state_->sample();
    state_->drain_pending_locked(std::chrono::steady_clock::now());
    if (!observation.ok()) {
        saturating_increment(state_->sampling_failures);
        saturating_increment(state_->rejections);
        state_->last_sample_valid = false;
        state_->last_sampling_error_code = observation.status().code();
        if (!state_->closed) {
            state_->closed = true;
            saturating_increment(state_->closed_transitions);
        }
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup pressure admission sample failed: " +
                observation.status().message()};
    }

    state_->last_sample_valid = true;
    state_->last_sampling_error_code = ErrorCode::ok;
    state_->last_observation = observation.value();
    if (!state_->trigger_monitor_healthy) {
        saturating_increment(state_->rejections);
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup PSI trigger monitor failed closed"};
    }

    const auto evaluate_current_state = [&]() {
        const auto now = std::chrono::steady_clock::now();
        return evaluate_cgroup_pressure_admission(
            state_->limits, observation.value(), state_->closed,
            state_->trigger_hold_active_locked(now));
    };
    auto decision = evaluate_current_state();
    if (!decision.ok()) {
        saturating_increment(state_->sampling_failures);
        saturating_increment(state_->rejections);
        state_->last_sample_valid = false;
        state_->last_sampling_error_code = decision.status().code();
        if (!state_->closed) {
            state_->closed = true;
            saturating_increment(state_->closed_transitions);
        }
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup pressure admission evaluation failed: " +
                decision.status().message()};
    }

    // A monitor thread publishes trigger counters atomically before acquiring
    // this mutex. Drain once more after evaluation, then recompute if the gate
    // changed while the complete descriptor-pinned sample was evaluated.
    state_->drain_pending_locked(std::chrono::steady_clock::now());
    if (!state_->trigger_monitor_healthy) {
        saturating_increment(state_->rejections);
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup PSI trigger monitor failed closed"};
    }
    decision = evaluate_current_state();
    if (!decision.ok()) {
        saturating_increment(state_->sampling_failures);
        saturating_increment(state_->rejections);
        state_->last_sample_valid = false;
        state_->last_sampling_error_code = decision.status().code();
        if (!state_->closed) {
            state_->closed = true;
            saturating_increment(state_->closed_transitions);
        }
        return Status{
            ErrorCode::unavailable,
            "Ratox cgroup pressure admission evaluation failed: " +
                decision.status().message()};
    }

    state_->closed = decision.value().closed;
    if (decision.value().closed_transition) {
        saturating_increment(state_->closed_transitions);
    }
    if (decision.value().reopened_transition) {
        saturating_increment(state_->reopened_transitions);
    }
    if (decision.value().admitted) {
        saturating_increment(state_->admitted);
        return Status::success();
    }
    const bool trigger_hold_active = state_->trigger_hold_active_locked(
        std::chrono::steady_clock::now());
    saturating_increment(state_->rejections);
    if (trigger_hold_active) {
        saturating_increment(state_->trigger_hold_rejections);
    }
    return Status{
        ErrorCode::resource_exhausted,
        trigger_hold_active
            ? "Ratox cgroup pressure admission gate is closed by an active PSI trigger hold"
            : "Ratox cgroup pressure admission gate is closed"};
}

CgroupPressureAdmissionSnapshot CgroupPressureAdmission::snapshot() const {
    if (!state_) return {};
    std::scoped_lock lock(state_->mutex);
    const auto now = std::chrono::steady_clock::now();
    state_->drain_pending_locked(now);

    CgroupPressureAdmissionSnapshot snapshot;
    snapshot.limits = state_->limits;
    snapshot.closed = state_->closed;
    snapshot.checks = state_->checks;
    snapshot.admitted = state_->admitted;
    snapshot.rejections = state_->rejections;
    snapshot.sampling_failures = state_->sampling_failures;
    snapshot.closed_transitions = state_->closed_transitions;
    snapshot.reopened_transitions = state_->reopened_transitions;
    snapshot.trigger_monitor_healthy = state_->trigger_monitor_healthy;
    snapshot.trigger_hold_active =
        state_->trigger_hold_active_locked(now);
    snapshot.trigger_hold_remaining_microseconds =
        state_->trigger_hold_remaining_microseconds_locked(now);
    snapshot.trigger_monitor_error_code =
        state_->trigger_monitor_error_code;
    snapshot.trigger_events = state_->trigger_events;
    snapshot.cpu_some_trigger_events = state_->cpu_some_trigger_events;
    snapshot.memory_full_trigger_events =
        state_->memory_full_trigger_events;
    snapshot.io_full_trigger_events = state_->io_full_trigger_events;
    snapshot.trigger_monitor_failures = state_->trigger_monitor_failures;
    snapshot.trigger_closed_transitions =
        state_->trigger_closed_transitions;
    snapshot.trigger_hold_rejections = state_->trigger_hold_rejections;
    snapshot.last_sample_valid = state_->last_sample_valid;
    snapshot.last_sampling_error_code = state_->last_sampling_error_code;
    snapshot.last_observation = state_->last_observation;
    return snapshot;
}

class SessionCgroup::Impl {
  public:
    Impl() = default;
    ~Impl() {
        if (cleanup_on_destroy_) {
            static_cast<void>(best_effort_kill_and_remove(
                std::chrono::milliseconds{250}));
        }
    }

    Impl(const Impl &) = delete;
    Impl &operator=(const Impl &) = delete;

    [[nodiscard]] Status initialize_outcome_controls(
        uid_t target_uid, gid_t target_gid,
        const CgroupResourceLimits &limits) {
        const auto open_protected = [this, target_uid, target_gid](
                                        std::string_view name,
                                        FileDescriptor &destination) -> Status {
            auto opened = open_control_file(
                directory_.get(), name, O_RDONLY);
            if (!opened.ok()) return opened.status();
            const Status protected_control = verify_control_boundary(
                opened.value().get(), target_uid, target_gid, name);
            if (!protected_control.ok()) return protected_control;
            destination = std::move(opened).value();
            return Status::success();
        };
        const auto open_optional_protected =
            [this, target_uid, target_gid](
                std::string_view name,
                FileDescriptor &destination) -> Status {
            auto opened = open_control_file(directory_.get(), name, O_RDONLY);
            if (!opened.ok()) {
                if (opened.status().code() == ErrorCode::unsupported) {
                    return Status::success();
                }
                return opened.status();
            }
            const Status protected_control = verify_control_boundary(
                opened.value().get(), target_uid, target_gid, name);
            if (!protected_control.ok()) return protected_control;
            destination = std::move(opened).value();
            return Status::success();
        };
        const auto open_local_or_hierarchical = [&open_protected](
                                                    std::string_view local_name,
                                                    std::string_view hierarchical_name,
                                                    FileDescriptor &destination)
            -> Status {
            const Status local = open_protected(local_name, destination);
            if (local.ok() || local.code() != ErrorCode::unsupported) {
                return local;
            }
            return open_protected(hierarchical_name, destination);
        };

        if (limits.maximum_processes.has_value()) {
            const Status opened = open_local_or_hierarchical(
                "pids.events.local", "pids.events", pids_events_);
            if (!opened.ok()) return opened;
        }
        if (limits.maximum_memory_high_bytes.has_value() ||
            limits.maximum_memory_bytes.has_value() ||
            limits.maximum_swap_bytes.has_value()) {
            const Status opened = open_local_or_hierarchical(
                "memory.events.local", "memory.events", memory_events_);
            if (!opened.ok()) return opened;
            const Status stat_opened =
                open_protected("memory.stat", memory_stat_);
            if (!stat_opened.ok()) return stat_opened;
        } else {
            const Status opened =
                open_optional_protected("memory.stat", memory_stat_);
            if (!opened.ok()) return opened;
        }
        if (limits.maximum_swap_bytes.has_value()) {
            const Status opened = open_protected(
                "memory.swap.events", memory_swap_events_);
            if (!opened.ok()) return opened;
        } else {
            const Status opened = open_optional_protected(
                "memory.swap.events", memory_swap_events_);
            if (!opened.ok()) return opened;
        }
        if (limits.cpu_quota_microseconds.has_value()) {
            const Status opened = open_protected("cpu.stat", cpu_stat_);
            if (!opened.ok()) return opened;
        } else {
            const Status opened = open_optional_protected("cpu.stat", cpu_stat_);
            if (!opened.ok()) return opened;
        }
        if (limits.io_device.has_value()) {
            const Status opened = open_protected("io.stat", io_stat_);
            if (!opened.ok()) return opened;
        }
        // Lifetime peak interfaces arrived at different kernel ages and depend
        // on delegated controllers. Open each independently and retain absence
        // as an explicit capability gap rather than blocking containment.
        for (const auto &[name, destination] :
             std::array<std::pair<std::string_view, FileDescriptor *>, 3U>{
                 std::pair{"pids.peak", &pids_peak_},
                 std::pair{"memory.peak", &memory_peak_},
                 std::pair{"memory.swap.peak", &memory_swap_peak_}}) {
            const Status opened = open_optional_protected(name, *destination);
            if (!opened.ok()) return opened;
        }
        // PSI is a best-effort kernel capability rather than a resource
        // policy prerequisite. Preserve each resource independently when the
        // protected per-cgroup interface exists; absence remains explicit in
        // the final outcome instead of blocking otherwise valid containment.
        for (const auto &[name, destination] :
             std::array<std::pair<std::string_view, FileDescriptor *>, 5U>{
                 std::pair{"cgroup.pressure", &pressure_control_},
                 std::pair{"cpu.pressure", &cpu_pressure_},
                 std::pair{"memory.pressure", &memory_pressure_},
                 std::pair{"io.pressure", &io_pressure_},
                 std::pair{"irq.pressure", &irq_pressure_}}) {
            const Status opened = open_optional_protected(name, *destination);
            if (!opened.ok()) return opened;
        }
        const Status local_stat_opened = open_optional_protected(
            "cgroup.stat.local", local_stat_);
        if (!local_stat_opened.ok()) return local_stat_opened;

        auto initial = read_outcome();
        if (!initial.ok()) return initial.status();
        const CgroupSessionOutcome &outcome = initial.value();
        const auto pressure_nonzero = [](const auto &observed) noexcept {
            return observed.has_value() &&
                   (observed->some_total_microseconds != 0U ||
                    observed->full_total_microseconds.value_or(0U) != 0U);
        };
        const auto peak_nonzero = [](const auto &observed) noexcept {
            return observed.value_or(0U) != 0U;
        };
        if (outcome.pids_limit_hits != 0U ||
            outcome.memory_high_events != 0U ||
            outcome.memory_max_events != 0U ||
            outcome.memory_oom_events != 0U ||
            outcome.memory_oom_kills != 0U ||
            outcome.memory_oom_group_kills != 0U ||
            peak_nonzero(outcome.pids_peak) ||
            peak_nonzero(outcome.memory_peak_bytes) ||
            peak_nonzero(outcome.memory_swap_peak_bytes) ||
            (outcome.memory_stat.has_value() &&
             (outcome.memory_stat->page_faults != 0U ||
              outcome.memory_stat->major_page_faults != 0U ||
              (outcome.memory_stat->reclaim.has_value() &&
               (outcome.memory_stat->reclaim->pages_scanned != 0U ||
                outcome.memory_stat->reclaim->pages_reclaimed != 0U)) ||
              (outcome.memory_stat->swap.has_value() &&
               (outcome.memory_stat->swap->pages_in != 0U ||
                outcome.memory_stat->swap->pages_out != 0U)))) ||
            (outcome.memory_swap_events.has_value() &&
             (outcome.memory_swap_events->high != 0U ||
              outcome.memory_swap_events->maximum != 0U ||
              outcome.memory_swap_events->fail != 0U)) ||
            (outcome.local_stat.has_value() &&
             outcome.local_stat->frozen_microseconds != 0U) ||
            outcome.cpu_usage_microseconds != 0U ||
            outcome.cpu_user_microseconds != 0U ||
            outcome.cpu_system_microseconds != 0U ||
            outcome.cpu_periods != 0U ||
            outcome.cpu_throttled_periods != 0U ||
            outcome.cpu_throttled_microseconds != 0U ||
            outcome.cpu_burst_periods != 0U ||
            outcome.cpu_burst_microseconds != 0U ||
            outcome.io_read_bytes != 0U ||
            outcome.io_write_bytes != 0U ||
            outcome.io_read_operations != 0U ||
            outcome.io_write_operations != 0U ||
            outcome.io_discard_bytes != 0U ||
            outcome.io_discard_operations != 0U ||
            pressure_nonzero(outcome.cpu_pressure) ||
            pressure_nonzero(outcome.memory_pressure) ||
            pressure_nonzero(outcome.io_pressure) ||
            (outcome.irq_pressure.has_value() &&
             outcome.irq_pressure->full_total_microseconds != 0U)) {
            return Status{
                ErrorCode::unavailable,
                "new Ratox session cgroup contained nonzero kernel outcome counters"};
        }
        return Status::success();
    }

    [[nodiscard]] Result<CgroupSessionOutcome> read_outcome() {
        CgroupSessionOutcome outcome;
        if (pressure_control_.get() >= 0) {
            auto enabled = read_control_record(
                pressure_control_.get(), "cgroup.pressure", 16U);
            if (!enabled.ok()) return enabled.status();
            if (enabled.value() != "1\n") {
                return Status{
                    ErrorCode::unavailable,
                    "Ratox session cgroup PSI accounting is disabled"};
            }
        }
        if (pids_events_.get() >= 0) {
            auto record = read_control_record(
                pids_events_.get(), "pids.events");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_pids_events(record.value());
            if (!parsed.ok()) return parsed.status();
            outcome.pids_limit_hits = parsed.value().maximum_hits;
        }
        if (memory_events_.get() >= 0) {
            auto record = read_control_record(
                memory_events_.get(), "memory.events");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_memory_events(record.value());
            if (!parsed.ok()) return parsed.status();
            outcome.memory_high_events = parsed.value().high;
            outcome.memory_max_events = parsed.value().maximum;
            outcome.memory_oom_events = parsed.value().oom;
            outcome.memory_oom_kills = parsed.value().oom_kill;
            outcome.memory_oom_group_kills =
                parsed.value().oom_group_kill;
        }
        if (memory_stat_.get() >= 0) {
            auto record = read_control_record(
                memory_stat_.get(), "memory.stat");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_memory_stat(record.value());
            if (!parsed.ok()) return parsed.status();
            outcome.memory_stat = std::move(parsed).value();
        }
        if (memory_swap_events_.get() >= 0) {
            auto record = read_control_record(
                memory_swap_events_.get(), "memory.swap.events");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_memory_swap_events(record.value());
            if (!parsed.ok()) return parsed.status();
            outcome.memory_swap_events = std::move(parsed).value();
        }
        if (local_stat_.get() >= 0) {
            auto record = read_control_record(
                local_stat_.get(), "cgroup.stat.local");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_local_stat(record.value());
            if (!parsed.ok()) return parsed.status();
            outcome.local_stat = parsed.value();
        }
        const auto read_peak = [](int descriptor, std::string_view label)
            -> Result<std::uint64_t> {
            auto record = read_control_record(descriptor, label, 64U);
            if (!record.ok()) return record.status();
            return parse_cgroup_peak(record.value());
        };
        if (pids_peak_.get() >= 0) {
            auto parsed = read_peak(pids_peak_.get(), "pids.peak");
            if (!parsed.ok()) return parsed.status();
            outcome.pids_peak = parsed.value();
        }
        if (memory_peak_.get() >= 0) {
            auto parsed = read_peak(memory_peak_.get(), "memory.peak");
            if (!parsed.ok()) return parsed.status();
            outcome.memory_peak_bytes = parsed.value();
        }
        if (memory_swap_peak_.get() >= 0) {
            auto parsed = read_peak(
                memory_swap_peak_.get(), "memory.swap.peak");
            if (!parsed.ok()) return parsed.status();
            outcome.memory_swap_peak_bytes = parsed.value();
        }
        if (cpu_stat_.get() >= 0) {
            auto record = read_control_record(
                cpu_stat_.get(), "cpu.stat");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_cpu_stat(record.value());
            if (!parsed.ok()) return parsed.status();
            const CgroupCpuStat &stat = parsed.value();
            outcome.cpu_stat_observed = true;
            outcome.cpu_usage_microseconds = stat.usage_microseconds;
            outcome.cpu_user_microseconds = stat.user_microseconds;
            outcome.cpu_system_microseconds = stat.system_microseconds;
            if (stat.bandwidth.has_value()) {
                outcome.cpu_bandwidth_stat_observed = true;
                outcome.cpu_periods = stat.bandwidth->periods;
                outcome.cpu_throttled_periods =
                    stat.bandwidth->throttled_periods;
                outcome.cpu_throttled_microseconds =
                    stat.bandwidth->throttled_microseconds;
                if (stat.bandwidth->burst.has_value()) {
                    outcome.cpu_burst_stat_observed = true;
                    outcome.cpu_burst_periods =
                        stat.bandwidth->burst->periods;
                    outcome.cpu_burst_microseconds =
                        stat.bandwidth->burst->microseconds;
                }
            }
        }
        if (io_stat_.get() >= 0) {
            auto record = read_control_record(
                io_stat_.get(), "io.stat");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_io_stat(record.value());
            if (!parsed.ok()) return parsed.status();
            outcome.io_read_bytes = parsed.value().read_bytes;
            outcome.io_write_bytes = parsed.value().write_bytes;
            outcome.io_read_operations = parsed.value().read_operations;
            outcome.io_write_operations = parsed.value().write_operations;
            outcome.io_discard_bytes = parsed.value().discard_bytes;
            outcome.io_discard_operations = parsed.value().discard_operations;
        }
        const auto read_pressure = [](int descriptor,
                                      std::string_view label)
            -> Result<CgroupPressure> {
            auto record = read_control_record(descriptor, label);
            if (!record.ok()) return record.status();
            return parse_cgroup_pressure(record.value());
        };
        if (cpu_pressure_.get() >= 0) {
            auto parsed = read_pressure(cpu_pressure_.get(), "cpu.pressure");
            if (!parsed.ok()) return parsed.status();
            outcome.cpu_pressure = std::move(parsed).value();
        }
        if (memory_pressure_.get() >= 0) {
            auto parsed = read_pressure(
                memory_pressure_.get(), "memory.pressure");
            if (!parsed.ok()) return parsed.status();
            outcome.memory_pressure = std::move(parsed).value();
        }
        if (io_pressure_.get() >= 0) {
            auto parsed = read_pressure(io_pressure_.get(), "io.pressure");
            if (!parsed.ok()) return parsed.status();
            outcome.io_pressure = std::move(parsed).value();
        }
        if (irq_pressure_.get() >= 0) {
            auto record = read_control_record(
                irq_pressure_.get(), "irq.pressure");
            if (!record.ok()) return record.status();
            auto parsed = parse_cgroup_irq_pressure(record.value());
            if (!parsed.ok()) return parsed.status();
            outcome.irq_pressure = parsed.value();
        }
        return outcome;
    }

    void capture_outcome() {
        if (outcome_.has_value()) return;
        auto outcome = read_outcome();
        if (outcome.ok()) {
            outcome_ = std::move(outcome).value();
        } else {
            CgroupSessionOutcome incomplete;
            incomplete.telemetry_complete = false;
            outcome_ = std::move(incomplete);
        }
    }

    [[nodiscard]] std::optional<CgroupSessionOutcome> take_outcome() noexcept {
        if (!removed_ || !outcome_.has_value()) return std::nullopt;
        return std::exchange(outcome_, std::nullopt);
    }

    [[nodiscard]] Result<bool> populated() {
        if (removed_ || events_.get() < 0) {
            return Status{ErrorCode::unavailable,
                          "Ratox session cgroup is no longer observable"};
        }
        auto record = read_control_record(events_.get(), "cgroup.events");
        if (!record.ok()) return record.status();
        auto parsed = parse_cgroup_events(record.value());
        if (!parsed.ok()) return parsed.status();
        return parsed.value().populated;
    }

    [[nodiscard]] Status kill_all() {
        if (removed_ || kill_.get() < 0) {
            return Status{ErrorCode::unavailable,
                          "Ratox session cgroup is no longer killable"};
        }
        if (kill_sent_) return Status::success();
        const Status killed = write_control_record(
            kill_.get(), "1\n", "cgroup.kill");
        if (!killed.ok()) return killed;
        kill_sent_ = true;
        return Status::success();
    }

    [[nodiscard]] Status attach(pid_t process) {
        if (removed_ || procs_.get() < 0 || process <= 0 || attached_) {
            return Status{ErrorCode::invalid_argument,
                          "Ratox session cgroup attach state is invalid"};
        }
        const std::string record =
            std::to_string(static_cast<std::int64_t>(process)) + "\n";
        const Status written = write_control_record(
            procs_.get(), record, "cgroup.procs");
        if (!written.ok()) return written;

        auto observed_record = read_control_record(
            procs_.get(), "cgroup.procs");
        if (!observed_record.ok()) return observed_record.status();
        auto observed = parse_cgroup_processes(observed_record.value());
        if (!observed.ok()) return observed.status();
        if (observed.value().empty() ||
            !std::all_of(
                observed.value().begin(), observed.value().end(),
                [process](pid_t member) { return member == process; })) {
            return Status{
                ErrorCode::unavailable,
                "Ratox helper did not become the exclusive initial cgroup member"};
        }
        auto is_populated = populated();
        if (!is_populated.ok()) return is_populated.status();
        if (!is_populated.value()) {
            return Status{ErrorCode::unavailable,
                          "Ratox session cgroup did not become populated"};
        }
        attached_ = true;
        return Status::success();
    }

    [[nodiscard]] int events_descriptor() const noexcept {
        if (removed_) return -1;
        return events_.get();
    }

    [[nodiscard]] Status remove_if_empty() {
        if (removed_) return Status::success();
        if (!owns_directory_) {
            capture_outcome();
            removed_ = true;
            return Status::success();
        }
        if (events_.get() >= 0) {
            auto is_populated = populated();
            if (!is_populated.ok()) return is_populated.status();
            if (is_populated.value()) {
                return Status{ErrorCode::unavailable,
                              "Ratox session cgroup is still populated"};
            }
        }

        struct stat current {};
        if (::fstatat(
                parent_.get(), name_.c_str(), &current,
                AT_SYMLINK_NOFOLLOW) != 0) {
            if (errno == ENOENT) {
                CgroupSessionOutcome incomplete;
                incomplete.telemetry_complete = false;
                outcome_ = std::move(incomplete);
                removed_ = true;
                reset_leaf_descriptors();
                return Status::success();
            }
            return errno_status(
                ErrorCode::io_error, "revalidate Ratox session cgroup inode");
        }
        if (!S_ISDIR(current.st_mode) || current.st_dev != device_ ||
            current.st_ino != inode_) {
            return Status{
                ErrorCode::unavailable,
                "Ratox session cgroup pathname no longer names the pinned inode"};
        }

        capture_outcome();
        reset_leaf_descriptors();
        if (::unlinkat(parent_.get(), name_.c_str(), AT_REMOVEDIR) != 0) {
            if (errno == ENOENT) {
                removed_ = true;
                return Status::success();
            }
            const ErrorCode code =
                errno == EBUSY || errno == EAGAIN ? ErrorCode::unavailable
                                                   : ErrorCode::io_error;
            return errno_status(code, "remove empty Ratox session cgroup");
        }
        removed_ = true;
        return Status::success();
    }

    [[nodiscard]] bool best_effort_kill_and_remove(
        std::chrono::milliseconds maximum_wait) noexcept {
        if (removed_) return true;
        if (kill_.get() >= 0) {
            static_cast<void>(kill_all());
        }
        const auto bounded_wait = std::clamp(
            maximum_wait, std::chrono::milliseconds{0},
            std::chrono::milliseconds{5000});
        const auto deadline = std::chrono::steady_clock::now() + bounded_wait;
        while (events_.get() >= 0) {
            auto is_populated = populated();
            if (!is_populated.ok() || !is_populated.value()) break;
            if (std::chrono::steady_clock::now() >= deadline) break;
            std::array<struct pollfd, 1U> observed{
                pollfd{events_.get(), POLLPRI, 0}};
            auto changed = wait_for_cgroup_event_change(observed, deadline);
            if (!changed.ok() || !changed.value()) break;
        }
        const Status removed = remove_if_empty();
        return removed.ok() && removed_;
    }

    void reset_leaf_descriptors() noexcept {
        local_stat_.reset();
        irq_pressure_.reset();
        io_pressure_.reset();
        memory_pressure_.reset();
        cpu_pressure_.reset();
        pressure_control_.reset();
        io_stat_.reset();
        cpu_stat_.reset();
        memory_swap_events_.reset();
        memory_stat_.reset();
        memory_swap_peak_.reset();
        memory_peak_.reset();
        pids_peak_.reset();
        memory_events_.reset();
        pids_events_.reset();
        type_.reset();
        subtree_control_.reset();
        threads_.reset();
        events_.reset();
        kill_.reset();
        procs_.reset();
        directory_.reset();
    }

    FileDescriptor parent_;
    FileDescriptor directory_;
    FileDescriptor procs_;
    FileDescriptor kill_;
    FileDescriptor events_;
    FileDescriptor type_;
    FileDescriptor threads_;
    FileDescriptor subtree_control_;
    FileDescriptor pids_events_;
    FileDescriptor memory_events_;
    FileDescriptor memory_stat_;
    FileDescriptor memory_swap_events_;
    FileDescriptor pids_peak_;
    FileDescriptor memory_peak_;
    FileDescriptor memory_swap_peak_;
    FileDescriptor cpu_stat_;
    FileDescriptor io_stat_;
    FileDescriptor pressure_control_;
    FileDescriptor cpu_pressure_;
    FileDescriptor memory_pressure_;
    FileDescriptor io_pressure_;
    FileDescriptor irq_pressure_;
    FileDescriptor local_stat_;
    std::string name_;
    dev_t device_{0};
    ino_t inode_{0};
    bool owns_directory_{false};
    bool attached_{false};
    bool kill_sent_{false};
    bool removed_{false};
    bool cleanup_on_destroy_{true};
    std::optional<CgroupSessionOutcome> outcome_;
};

struct CgroupAggregateAdmission::Reservation::State {
    explicit State(CgroupAggregateLimits configured_limits)
        : limits(std::move(configured_limits)) {}

    mutable std::mutex mutex;
    CgroupAggregateLimits limits;
    std::size_t active_reservations{0U};
    std::size_t peak_active_reservations{0U};
    std::uint64_t reserved_processes{0U};
    std::uint64_t reserved_memory_bytes{0U};
    std::uint64_t reserved_swap_bytes{0U};
    std::uint64_t reserved_cpu_quota_microseconds{0U};
    std::uint64_t peak_reserved_processes{0U};
    std::uint64_t peak_reserved_memory_bytes{0U};
    std::uint64_t peak_reserved_swap_bytes{0U};
    std::uint64_t peak_reserved_cpu_quota_microseconds{0U};
    std::uint64_t rejected_reservations{0U};
    std::uint64_t stranded_reservations{0U};
    std::uint64_t completed_session_outcomes{0U};
    std::uint64_t incomplete_session_outcomes{0U};
    std::uint64_t pids_limit_hits{0U};
    std::uint64_t memory_high_events{0U};
    std::uint64_t memory_max_events{0U};
    std::uint64_t memory_oom_events{0U};
    std::uint64_t memory_oom_kills{0U};
    std::uint64_t memory_oom_group_kills{0U};
    std::uint64_t pids_peak_session_outcomes{0U};
    std::uint64_t pids_peak_sum{0U};
    std::uint64_t pids_peak_maximum{0U};
    std::uint64_t memory_peak_session_outcomes{0U};
    std::uint64_t memory_peak_sum_bytes{0U};
    std::uint64_t memory_peak_maximum_bytes{0U};
    std::uint64_t memory_swap_peak_session_outcomes{0U};
    std::uint64_t memory_swap_peak_sum_bytes{0U};
    std::uint64_t memory_swap_peak_maximum_bytes{0U};
    std::uint64_t memory_stat_session_outcomes{0U};
    std::uint64_t memory_reclaim_stat_session_outcomes{0U};
    std::uint64_t memory_swap_stat_session_outcomes{0U};
    std::uint64_t memory_page_faults{0U};
    std::uint64_t memory_major_page_faults{0U};
    std::uint64_t memory_pages_scanned{0U};
    std::uint64_t memory_pages_reclaimed{0U};
    std::uint64_t memory_pages_swapped_in{0U};
    std::uint64_t memory_pages_swapped_out{0U};
    std::uint64_t memory_swap_events_session_outcomes{0U};
    std::uint64_t memory_swap_high_events{0U};
    std::uint64_t memory_swap_max_events{0U};
    std::uint64_t memory_swap_fail_events{0U};
    std::uint64_t local_stat_session_outcomes{0U};
    std::uint64_t frozen_microseconds{0U};
    std::uint64_t cpu_stat_session_outcomes{0U};
    std::uint64_t cpu_bandwidth_stat_session_outcomes{0U};
    std::uint64_t cpu_burst_stat_session_outcomes{0U};
    std::uint64_t cpu_usage_microseconds{0U};
    std::uint64_t cpu_user_microseconds{0U};
    std::uint64_t cpu_system_microseconds{0U};
    std::uint64_t cpu_periods{0U};
    std::uint64_t cpu_throttled_periods{0U};
    std::uint64_t cpu_throttled_microseconds{0U};
    std::uint64_t cpu_burst_periods{0U};
    std::uint64_t cpu_burst_microseconds{0U};
    std::uint64_t io_read_bytes{0U};
    std::uint64_t io_write_bytes{0U};
    std::uint64_t io_read_operations{0U};
    std::uint64_t io_write_operations{0U};
    std::uint64_t io_discard_bytes{0U};
    std::uint64_t io_discard_operations{0U};
    std::uint64_t cpu_pressure_session_outcomes{0U};
    std::uint64_t cpu_pressure_full_session_outcomes{0U};
    std::uint64_t cpu_pressure_some_microseconds{0U};
    std::uint64_t cpu_pressure_full_microseconds{0U};
    std::uint64_t memory_pressure_session_outcomes{0U};
    std::uint64_t memory_pressure_full_session_outcomes{0U};
    std::uint64_t memory_pressure_some_microseconds{0U};
    std::uint64_t memory_pressure_full_microseconds{0U};
    std::uint64_t io_pressure_session_outcomes{0U};
    std::uint64_t io_pressure_full_session_outcomes{0U};
    std::uint64_t io_pressure_some_microseconds{0U};
    std::uint64_t io_pressure_full_microseconds{0U};
    std::uint64_t irq_pressure_session_outcomes{0U};
    std::uint64_t irq_pressure_full_microseconds{0U};
};

CgroupAggregateAdmission::Reservation::Reservation() noexcept = default;

CgroupAggregateAdmission::Reservation::Reservation(
    std::shared_ptr<State> state,
    std::uint64_t processes,
    std::uint64_t memory_bytes,
    std::uint64_t swap_bytes,
    std::uint64_t cpu_quota_microseconds,
    bool charged) noexcept
    : state_(std::move(state)), processes_(processes),
      memory_bytes_(memory_bytes), swap_bytes_(swap_bytes),
      cpu_quota_microseconds_(cpu_quota_microseconds), charged_(charged) {}

CgroupAggregateAdmission::Reservation::~Reservation() { release(); }

CgroupAggregateAdmission::Reservation::Reservation(
    Reservation &&other) noexcept
    : state_(std::move(other.state_)),
      processes_(std::exchange(other.processes_, 0U)),
      memory_bytes_(std::exchange(other.memory_bytes_, 0U)),
      swap_bytes_(std::exchange(other.swap_bytes_, 0U)),
      cpu_quota_microseconds_(
          std::exchange(other.cpu_quota_microseconds_, 0U)),
      charged_(std::exchange(other.charged_, false)),
      outcome_recorded_(std::exchange(other.outcome_recorded_, false)) {}

CgroupAggregateAdmission::Reservation &
CgroupAggregateAdmission::Reservation::operator=(Reservation &&other) noexcept {
    if (this == &other) return *this;
    release();
    state_ = std::move(other.state_);
    processes_ = std::exchange(other.processes_, 0U);
    memory_bytes_ = std::exchange(other.memory_bytes_, 0U);
    swap_bytes_ = std::exchange(other.swap_bytes_, 0U);
    cpu_quota_microseconds_ =
        std::exchange(other.cpu_quota_microseconds_, 0U);
    charged_ = std::exchange(other.charged_, false);
    outcome_recorded_ = std::exchange(other.outcome_recorded_, false);
    return *this;
}

bool CgroupAggregateAdmission::Reservation::active() const noexcept {
    return charged_;
}

void CgroupAggregateAdmission::Reservation::record_outcome(
    const CgroupSessionOutcome &outcome) noexcept {
    if (!state_ || outcome_recorded_) return;
    outcome_recorded_ = true;
    std::scoped_lock lock(state_->mutex);
    if (!outcome.telemetry_complete) {
        saturating_increment(state_->incomplete_session_outcomes);
        return;
    }
    saturating_increment(state_->completed_session_outcomes);
    saturating_add(state_->pids_limit_hits, outcome.pids_limit_hits);
    saturating_add(state_->memory_high_events, outcome.memory_high_events);
    saturating_add(state_->memory_max_events, outcome.memory_max_events);
    saturating_add(state_->memory_oom_events, outcome.memory_oom_events);
    saturating_add(state_->memory_oom_kills, outcome.memory_oom_kills);
    saturating_add(
        state_->memory_oom_group_kills,
        outcome.memory_oom_group_kills);
    const auto retain_peak = [](
        const std::optional<std::uint64_t> &peak,
        std::uint64_t &session_outcomes,
        std::uint64_t &sum,
        std::uint64_t &maximum) noexcept {
        if (!peak.has_value()) return;
        saturating_increment(session_outcomes);
        saturating_add(sum, *peak);
        maximum = std::max(maximum, *peak);
    };
    retain_peak(
        outcome.pids_peak,
        state_->pids_peak_session_outcomes,
        state_->pids_peak_sum,
        state_->pids_peak_maximum);
    retain_peak(
        outcome.memory_peak_bytes,
        state_->memory_peak_session_outcomes,
        state_->memory_peak_sum_bytes,
        state_->memory_peak_maximum_bytes);
    retain_peak(
        outcome.memory_swap_peak_bytes,
        state_->memory_swap_peak_session_outcomes,
        state_->memory_swap_peak_sum_bytes,
        state_->memory_swap_peak_maximum_bytes);
    if (outcome.memory_stat.has_value()) {
        saturating_increment(state_->memory_stat_session_outcomes);
        saturating_add(
            state_->memory_page_faults,
            outcome.memory_stat->page_faults);
        saturating_add(
            state_->memory_major_page_faults,
            outcome.memory_stat->major_page_faults);
        if (outcome.memory_stat->reclaim.has_value()) {
            saturating_increment(
                state_->memory_reclaim_stat_session_outcomes);
            saturating_add(
                state_->memory_pages_scanned,
                outcome.memory_stat->reclaim->pages_scanned);
            saturating_add(
                state_->memory_pages_reclaimed,
                outcome.memory_stat->reclaim->pages_reclaimed);
        }
        if (outcome.memory_stat->swap.has_value()) {
            saturating_increment(
                state_->memory_swap_stat_session_outcomes);
            saturating_add(
                state_->memory_pages_swapped_in,
                outcome.memory_stat->swap->pages_in);
            saturating_add(
                state_->memory_pages_swapped_out,
                outcome.memory_stat->swap->pages_out);
        }
    }
    if (outcome.memory_swap_events.has_value()) {
        saturating_increment(
            state_->memory_swap_events_session_outcomes);
        saturating_add(
            state_->memory_swap_high_events,
            outcome.memory_swap_events->high);
        saturating_add(
            state_->memory_swap_max_events,
            outcome.memory_swap_events->maximum);
        saturating_add(
            state_->memory_swap_fail_events,
            outcome.memory_swap_events->fail);
    }
    if (outcome.local_stat.has_value()) {
        saturating_increment(state_->local_stat_session_outcomes);
        saturating_add(
            state_->frozen_microseconds,
            outcome.local_stat->frozen_microseconds);
    }
    if (outcome.cpu_stat_observed) {
        saturating_increment(state_->cpu_stat_session_outcomes);
        saturating_add(
            state_->cpu_usage_microseconds,
            outcome.cpu_usage_microseconds);
        saturating_add(
            state_->cpu_user_microseconds,
            outcome.cpu_user_microseconds);
        saturating_add(
            state_->cpu_system_microseconds,
            outcome.cpu_system_microseconds);
        if (outcome.cpu_bandwidth_stat_observed) {
            saturating_increment(
                state_->cpu_bandwidth_stat_session_outcomes);
            saturating_add(state_->cpu_periods, outcome.cpu_periods);
            saturating_add(
                state_->cpu_throttled_periods,
                outcome.cpu_throttled_periods);
            saturating_add(
                state_->cpu_throttled_microseconds,
                outcome.cpu_throttled_microseconds);
            if (outcome.cpu_burst_stat_observed) {
                saturating_increment(
                    state_->cpu_burst_stat_session_outcomes);
                saturating_add(
                    state_->cpu_burst_periods,
                    outcome.cpu_burst_periods);
                saturating_add(
                    state_->cpu_burst_microseconds,
                    outcome.cpu_burst_microseconds);
            }
        }
    }
    saturating_add(state_->io_read_bytes, outcome.io_read_bytes);
    saturating_add(state_->io_write_bytes, outcome.io_write_bytes);
    saturating_add(
        state_->io_read_operations, outcome.io_read_operations);
    saturating_add(
        state_->io_write_operations, outcome.io_write_operations);
    saturating_add(state_->io_discard_bytes, outcome.io_discard_bytes);
    saturating_add(
        state_->io_discard_operations, outcome.io_discard_operations);
    const auto retain_pressure = [](
        const std::optional<CgroupPressure> &pressure,
        std::uint64_t &session_outcomes,
        std::uint64_t &full_session_outcomes,
        std::uint64_t &some_microseconds,
        std::uint64_t &full_microseconds) noexcept {
        if (!pressure.has_value()) return;
        saturating_increment(session_outcomes);
        saturating_add(
            some_microseconds, pressure->some_total_microseconds);
        if (!pressure->full_total_microseconds.has_value()) return;
        saturating_increment(full_session_outcomes);
        saturating_add(
            full_microseconds, *pressure->full_total_microseconds);
    };
    retain_pressure(
        outcome.cpu_pressure,
        state_->cpu_pressure_session_outcomes,
        state_->cpu_pressure_full_session_outcomes,
        state_->cpu_pressure_some_microseconds,
        state_->cpu_pressure_full_microseconds);
    retain_pressure(
        outcome.memory_pressure,
        state_->memory_pressure_session_outcomes,
        state_->memory_pressure_full_session_outcomes,
        state_->memory_pressure_some_microseconds,
        state_->memory_pressure_full_microseconds);
    retain_pressure(
        outcome.io_pressure,
        state_->io_pressure_session_outcomes,
        state_->io_pressure_full_session_outcomes,
        state_->io_pressure_some_microseconds,
        state_->io_pressure_full_microseconds);
    if (outcome.irq_pressure.has_value()) {
        saturating_increment(state_->irq_pressure_session_outcomes);
        saturating_add(
            state_->irq_pressure_full_microseconds,
            outcome.irq_pressure->full_total_microseconds);
    }
}

void CgroupAggregateAdmission::Reservation::release() noexcept {
    if (!state_) return;
    std::shared_ptr<State> state = std::move(state_);
    if (!charged_) {
        outcome_recorded_ = false;
        return;
    }
    std::scoped_lock lock(state->mutex);
    // A token is the sole authority to release its exact charge. Continuing
    // after an impossible internal mismatch would under-account live work and
    // violate the admission invariant, so fail stop rather than clamp.
    if (state->active_reservations == 0U ||
        state->reserved_processes < processes_ ||
        state->reserved_memory_bytes < memory_bytes_ ||
        state->reserved_swap_bytes < swap_bytes_ ||
        state->reserved_cpu_quota_microseconds < cpu_quota_microseconds_) {
        std::terminate();
    }
    --state->active_reservations;
    state->reserved_processes -= processes_;
    state->reserved_memory_bytes -= memory_bytes_;
    state->reserved_swap_bytes -= swap_bytes_;
    state->reserved_cpu_quota_microseconds -= cpu_quota_microseconds_;
    processes_ = 0U;
    memory_bytes_ = 0U;
    swap_bytes_ = 0U;
    cpu_quota_microseconds_ = 0U;
    charged_ = false;
    outcome_recorded_ = false;
}

void CgroupAggregateAdmission::Reservation::strand() noexcept {
    if (!state_) return;
    std::shared_ptr<State> state = std::move(state_);
    if (!charged_) {
        outcome_recorded_ = false;
        return;
    }
    std::scoped_lock lock(state->mutex);
    // Stranding deliberately retains the exact charge. It is safer to reject
    // future work until restart recovery than to under-account a cgroup whose
    // complete teardown was not proved.
    if (state->active_reservations == 0U ||
        state->reserved_processes < processes_ ||
        state->reserved_memory_bytes < memory_bytes_ ||
        state->reserved_swap_bytes < swap_bytes_ ||
        state->reserved_cpu_quota_microseconds < cpu_quota_microseconds_) {
        std::terminate();
    }
    saturating_increment(state->stranded_reservations);
    processes_ = 0U;
    memory_bytes_ = 0U;
    swap_bytes_ = 0U;
    cpu_quota_microseconds_ = 0U;
    charged_ = false;
    outcome_recorded_ = false;
}

CgroupAggregateAdmission::CgroupAggregateAdmission(
    std::shared_ptr<Reservation::State> state) noexcept
    : state_(std::move(state)) {}

Result<std::shared_ptr<CgroupAggregateAdmission>>
CgroupAggregateAdmission::create(CgroupAggregateLimits limits) {
    const Status valid = validate_cgroup_aggregate_limits(limits);
    if (!valid.ok()) return valid;
    auto state = std::make_shared<Reservation::State>(std::move(limits));
    return std::shared_ptr<CgroupAggregateAdmission>(
        new CgroupAggregateAdmission(std::move(state)));
}

Result<CgroupAggregateAdmission::Reservation>
CgroupAggregateAdmission::reserve(
    const CgroupResourceLimits &session_limits) {
    if (!state_) {
        return Status{
            ErrorCode::internal_error,
            "Ratox aggregate cgroup admission state is unavailable"};
    }
    auto charge = resolve_cgroup_aggregate_charge(
        state_->limits, session_limits);
    if (!charge.ok()) return charge.status();
    if (state_->limits.empty()) {
        return Reservation{state_, 0U, 0U, 0U, 0U, false};
    }
    const CgroupAggregateCharge resolved_charge =
        std::move(charge).value();

    const std::uint64_t processes = resolved_charge.reserved_processes;
    const std::uint64_t memory_bytes = resolved_charge.reserved_memory_bytes;
    const std::uint64_t swap_bytes = resolved_charge.reserved_swap_bytes;
    const std::uint64_t cpu_quota_microseconds =
        resolved_charge.reserved_cpu_quota_microseconds;

    std::scoped_lock lock(state_->mutex);
    const auto exceeds = [](
        std::uint64_t current, std::uint64_t requested,
        const std::optional<std::uint64_t> &maximum) noexcept {
        return maximum.has_value() &&
               (current > *maximum || requested > *maximum - current);
    };
    if (state_->active_reservations ==
            std::numeric_limits<std::size_t>::max() ||
        exceeds(
            state_->reserved_processes, processes,
            state_->limits.maximum_reserved_processes) ||
        exceeds(
            state_->reserved_memory_bytes, memory_bytes,
            state_->limits.maximum_reserved_memory_bytes) ||
        exceeds(
            state_->reserved_swap_bytes, swap_bytes,
            state_->limits.maximum_reserved_swap_bytes) ||
        exceeds(
            state_->reserved_cpu_quota_microseconds,
            cpu_quota_microseconds,
            state_->limits.maximum_reserved_cpu_quota_microseconds)) {
        saturating_increment(state_->rejected_reservations);
        return Status{
            ErrorCode::resource_exhausted,
            "Ratox aggregate cgroup reservation ceiling is exhausted"};
    }

    ++state_->active_reservations;
    state_->reserved_processes += processes;
    state_->reserved_memory_bytes += memory_bytes;
    state_->reserved_swap_bytes += swap_bytes;
    state_->reserved_cpu_quota_microseconds += cpu_quota_microseconds;
    state_->peak_active_reservations = std::max(
        state_->peak_active_reservations, state_->active_reservations);
    state_->peak_reserved_processes = std::max(
        state_->peak_reserved_processes, state_->reserved_processes);
    state_->peak_reserved_memory_bytes = std::max(
        state_->peak_reserved_memory_bytes, state_->reserved_memory_bytes);
    state_->peak_reserved_swap_bytes = std::max(
        state_->peak_reserved_swap_bytes, state_->reserved_swap_bytes);
    state_->peak_reserved_cpu_quota_microseconds = std::max(
        state_->peak_reserved_cpu_quota_microseconds,
        state_->reserved_cpu_quota_microseconds);
    return Reservation{
        state_, processes, memory_bytes, swap_bytes, cpu_quota_microseconds,
        true};
}

CgroupAggregateSnapshot CgroupAggregateAdmission::snapshot() const {
    if (!state_) return {};
    std::scoped_lock lock(state_->mutex);
    return CgroupAggregateSnapshot{
        state_->limits,
        state_->active_reservations,
        state_->peak_active_reservations,
        state_->reserved_processes,
        state_->reserved_memory_bytes,
        state_->reserved_swap_bytes,
        state_->reserved_cpu_quota_microseconds,
        state_->peak_reserved_processes,
        state_->peak_reserved_memory_bytes,
        state_->peak_reserved_swap_bytes,
        state_->peak_reserved_cpu_quota_microseconds,
        state_->rejected_reservations,
        state_->stranded_reservations,
        state_->completed_session_outcomes,
        state_->incomplete_session_outcomes,
        state_->pids_limit_hits,
        state_->memory_high_events,
        state_->memory_max_events,
        state_->memory_oom_events,
        state_->memory_oom_kills,
        state_->memory_oom_group_kills,
        state_->pids_peak_session_outcomes,
        state_->pids_peak_sum,
        state_->pids_peak_maximum,
        state_->memory_peak_session_outcomes,
        state_->memory_peak_sum_bytes,
        state_->memory_peak_maximum_bytes,
        state_->memory_swap_peak_session_outcomes,
        state_->memory_swap_peak_sum_bytes,
        state_->memory_swap_peak_maximum_bytes,
        state_->memory_stat_session_outcomes,
        state_->memory_reclaim_stat_session_outcomes,
        state_->memory_swap_stat_session_outcomes,
        state_->memory_page_faults,
        state_->memory_major_page_faults,
        state_->memory_pages_scanned,
        state_->memory_pages_reclaimed,
        state_->memory_pages_swapped_in,
        state_->memory_pages_swapped_out,
        state_->memory_swap_events_session_outcomes,
        state_->memory_swap_high_events,
        state_->memory_swap_max_events,
        state_->memory_swap_fail_events,
        state_->local_stat_session_outcomes,
        state_->frozen_microseconds,
        state_->cpu_stat_session_outcomes,
        state_->cpu_bandwidth_stat_session_outcomes,
        state_->cpu_burst_stat_session_outcomes,
        state_->cpu_usage_microseconds,
        state_->cpu_user_microseconds,
        state_->cpu_system_microseconds,
        state_->cpu_periods,
        state_->cpu_throttled_periods,
        state_->cpu_throttled_microseconds,
        state_->cpu_burst_periods,
        state_->cpu_burst_microseconds,
        state_->io_read_bytes,
        state_->io_write_bytes,
        state_->io_read_operations,
        state_->io_write_operations,
        state_->io_discard_bytes,
        state_->io_discard_operations,
        state_->cpu_pressure_session_outcomes,
        state_->cpu_pressure_full_session_outcomes,
        state_->cpu_pressure_some_microseconds,
        state_->cpu_pressure_full_microseconds,
        state_->memory_pressure_session_outcomes,
        state_->memory_pressure_full_session_outcomes,
        state_->memory_pressure_some_microseconds,
        state_->memory_pressure_full_microseconds,
        state_->io_pressure_session_outcomes,
        state_->io_pressure_full_session_outcomes,
        state_->io_pressure_some_microseconds,
        state_->io_pressure_full_microseconds,
        state_->irq_pressure_session_outcomes,
        state_->irq_pressure_full_microseconds};
}

SessionCgroup::SessionCgroup() noexcept = default;
SessionCgroup::~SessionCgroup() = default;
SessionCgroup::SessionCgroup(SessionCgroup &&) noexcept = default;
SessionCgroup &SessionCgroup::operator=(SessionCgroup &&) noexcept = default;

SessionCgroup::SessionCgroup(std::unique_ptr<Impl> implementation) noexcept
    : implementation_(std::move(implementation)) {}

Status SessionCgroup::validate_resource_limits(
    const CgroupResourceLimits &resource_limits) {
    return iotox::terminal::validate_cgroup_resource_limits(resource_limits);
}

Result<SessionCgroup> SessionCgroup::create(
    const std::filesystem::path &delegated_root,
    const IdentityPolicy &payload_identity,
    CgroupResourceLimits resource_limits) {
    const Status valid_limits = validate_resource_limits(resource_limits);
    if (!valid_limits.ok()) return valid_limits;
    auto identity = validate_payload_identity(payload_identity);
    if (!identity.ok()) return identity.status();
    const auto [target_uid, target_gid] = identity.value();
    auto owner_identity = current_cgroup_owner_identity();
    if (!owner_identity.ok()) return owner_identity.status();

    auto parent = open_absolute_directory_without_symlinks(delegated_root);
    if (!parent.ok()) return parent.status();
    const Status cgroup2 = require_cgroup2_filesystem(
        parent.value().get(), "Ratox cgroup root");
    if (!cgroup2.ok()) return cgroup2;
    const Status root_boundary = verify_supervisor_owned_boundary(
        parent.value().get(), target_uid, target_gid,
        "Ratox delegated cgroup root", true);
    if (!root_boundary.ok()) return root_boundary;
    const Status controllers = require_resource_controllers(
        parent.value().get(), target_uid, target_gid, resource_limits);
    if (!controllers.ok()) return controllers;

    for (const auto &control : {
             std::pair{std::string_view{"cgroup.procs"}, O_WRONLY},
             std::pair{std::string_view{"cgroup.threads"}, O_RDONLY},
             std::pair{std::string_view{"cgroup.subtree_control"}, O_RDONLY}}) {
        auto opened = open_control_file(
            parent.value().get(), control.first, control.second);
        if (!opened.ok()) return opened.status();
        const Status protected_control = verify_control_boundary(
            opened.value().get(), target_uid, target_gid, control.first);
        if (!protected_control.ok()) return protected_control;
    }

    auto implementation = std::make_unique<Impl>();
    implementation->parent_ = std::move(parent).value();
    bool created = false;
    for (unsigned int attempt = 0U;
         attempt < kMaximumCgroupNameAttempts; ++attempt) {
        const std::uint64_t sequence =
            cgroup_sequence.fetch_add(1U, std::memory_order_relaxed) + 1U;
        auto name = format_session_cgroup_name(
            SessionCgroupName{owner_identity.value(), sequence});
        if (!name.ok()) return name.status();
        implementation->name_ = std::move(name).value();
        if (::mkdirat(
                implementation->parent_.get(),
                implementation->name_.c_str(), static_cast<mode_t>(0700)) == 0) {
            implementation->owns_directory_ = true;
            created = true;
            break;
        }
        if (errno != EEXIST) {
            const int failure = errno;
            return errno_status(
                mkdir_error_code(failure),
                "create dedicated Ratox session cgroup", failure);
        }
    }
    if (!created) {
        return Status{ErrorCode::resource_exhausted,
                      "Ratox session cgroup name space is exhausted"};
    }

    // Pin the newly created pathname before opening any kernel interface.
    // This gives every later failure path an exact inode to remove and also
    // detects a same-name replacement between mkdirat() and openat().
    struct stat created_leaf {};
    if (::fstatat(
            implementation->parent_.get(), implementation->name_.c_str(),
            &created_leaf, AT_SYMLINK_NOFOLLOW) != 0) {
        const int failure = errno;
        if (::unlinkat(
                implementation->parent_.get(), implementation->name_.c_str(),
                AT_REMOVEDIR) == 0 || errno == ENOENT) {
            implementation->owns_directory_ = false;
        }
        return errno_status(
            ErrorCode::io_error, "pin new Ratox session cgroup pathname",
            failure);
    }
    if (!S_ISDIR(created_leaf.st_mode)) {
        return Status{
            ErrorCode::unavailable,
            "new Ratox session cgroup pathname is not a directory"};
    }
    implementation->device_ = created_leaf.st_dev;
    implementation->inode_ = created_leaf.st_ino;

    implementation->directory_.reset(::openat(
        implementation->parent_.get(), implementation->name_.c_str(),
        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (implementation->directory_.get() < 0) {
        return errno_status(
            ErrorCode::io_error, "open dedicated Ratox session cgroup");
    }
    struct stat opened_leaf {};
    if (::fstat(implementation->directory_.get(), &opened_leaf) != 0) {
        return errno_status(
            ErrorCode::io_error, "inspect opened Ratox session cgroup inode");
    }
    if (!S_ISDIR(opened_leaf.st_mode) ||
        opened_leaf.st_dev != implementation->device_ ||
        opened_leaf.st_ino != implementation->inode_) {
        return Status{
            ErrorCode::unavailable,
            "Ratox session cgroup changed while its inode was being pinned"};
    }
    const Status leaf_cgroup2 = require_cgroup2_filesystem(
        implementation->directory_.get(), "Ratox session cgroup");
    if (!leaf_cgroup2.ok()) return leaf_cgroup2;
    const Status leaf_boundary = verify_supervisor_owned_boundary(
        implementation->directory_.get(), target_uid, target_gid,
        "Ratox session cgroup directory", true);
    if (!leaf_boundary.ok()) return leaf_boundary;

    auto procs = open_control_file(
        implementation->directory_.get(), "cgroup.procs", O_RDWR);
    if (!procs.ok()) return procs.status();
    implementation->procs_ = std::move(procs).value();
    auto kill = open_control_file(
        implementation->directory_.get(), "cgroup.kill", O_WRONLY);
    if (!kill.ok()) return kill.status();
    implementation->kill_ = std::move(kill).value();
    auto events = open_control_file(
        implementation->directory_.get(), "cgroup.events", O_RDONLY);
    if (!events.ok()) return events.status();
    implementation->events_ = std::move(events).value();
    auto type = open_control_file(
        implementation->directory_.get(), "cgroup.type", O_RDONLY);
    if (!type.ok()) return type.status();
    implementation->type_ = std::move(type).value();
    auto threads = open_control_file(
        implementation->directory_.get(), "cgroup.threads", O_RDONLY);
    if (!threads.ok()) return threads.status();
    implementation->threads_ = std::move(threads).value();
    auto subtree_control = open_control_file(
        implementation->directory_.get(), "cgroup.subtree_control", O_RDONLY);
    if (!subtree_control.ok()) return subtree_control.status();
    implementation->subtree_control_ = std::move(subtree_control).value();

    const std::array protected_controls{
        std::pair{implementation->procs_.get(), std::string_view{"cgroup.procs"}},
        std::pair{implementation->kill_.get(), std::string_view{"cgroup.kill"}},
        std::pair{implementation->type_.get(), std::string_view{"cgroup.type"}},
        std::pair{implementation->threads_.get(), std::string_view{"cgroup.threads"}},
        std::pair{implementation->subtree_control_.get(),
                  std::string_view{"cgroup.subtree_control"}},
    };
    for (const auto &[descriptor, name] : protected_controls) {
        const Status protected_control = verify_control_boundary(
            descriptor, target_uid, target_gid, name);
        if (!protected_control.ok()) return protected_control;
    }

    auto type_record = read_control_record(
        implementation->type_.get(), "cgroup.type", 64U);
    if (!type_record.ok()) return type_record.status();
    if (type_record.value() != "domain\n") {
        return Status{
            ErrorCode::unsupported,
            "Ratox session cgroup is not a valid non-threaded domain"};
    }
    auto process_record = read_control_record(
        implementation->procs_.get(), "cgroup.procs");
    if (!process_record.ok()) return process_record.status();
    auto processes = parse_cgroup_processes(process_record.value());
    if (!processes.ok()) return processes.status();
    if (!processes.value().empty()) {
        return Status{ErrorCode::unavailable,
                      "new Ratox session cgroup was unexpectedly populated"};
    }
    auto thread_record = read_control_record(
        implementation->threads_.get(), "cgroup.threads");
    if (!thread_record.ok()) return thread_record.status();
    auto thread_ids = parse_cgroup_processes(thread_record.value());
    if (!thread_ids.ok()) return thread_ids.status();
    if (!thread_ids.value().empty()) {
        return Status{ErrorCode::unavailable,
                      "new Ratox session cgroup unexpectedly contained threads"};
    }
    auto subtree_record = read_control_record(
        implementation->subtree_control_.get(), "cgroup.subtree_control");
    if (!subtree_record.ok()) return subtree_record.status();
    if (!subtree_record.value().empty()) {
        return Status{
            ErrorCode::unavailable,
            "new Ratox session cgroup unexpectedly enabled child controllers"};
    }
    auto is_populated = implementation->populated();
    if (!is_populated.ok()) return is_populated.status();
    if (is_populated.value()) {
        return Status{ErrorCode::unavailable,
                      "new Ratox session cgroup was unexpectedly populated"};
    }
    const Status resources = apply_resource_limits(
        implementation->directory_.get(), target_uid, target_gid,
        resource_limits);
    if (!resources.ok()) return resources;
    const Status outcome_controls = implementation->initialize_outcome_controls(
        target_uid, target_gid, resource_limits);
    if (!outcome_controls.ok()) return outcome_controls;

    return SessionCgroup(std::move(implementation));
}

Status SessionCgroup::preflight(
    const std::filesystem::path &delegated_root,
    const IdentityPolicy &payload_identity,
    CgroupResourceLimits resource_limits) {
    auto probe = create(
        delegated_root, payload_identity, std::move(resource_limits));
    if (!probe.ok()) return probe.status();
    const Status removed = probe.value().remove_if_empty();
    if (!removed.ok()) {
        return Status{
            removed.code(),
            "Ratox cgroup delegation preflight could not remove its empty probe leaf: " +
                removed.message()};
    }
    return Status::success();
}

Result<CgroupRecoveryReport> SessionCgroup::recover_orphans(
    const std::filesystem::path &delegated_root,
    CgroupRecoveryConfig config) {
    if (config.maximum_candidates == 0U ||
        config.maximum_candidates > 1024U) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup recovery candidate bound must be in [1, 1024]"};
    }
    if (config.maximum_wait.count() <= 0 ||
        config.maximum_wait > std::chrono::seconds{30}) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup recovery wait must be in (0, 30s]"};
    }

    auto parent = open_absolute_directory_without_symlinks(delegated_root);
    if (!parent.ok()) return parent.status();
    const Status cgroup2 = require_cgroup2_filesystem(
        parent.value().get(), "Ratox cgroup recovery root");
    if (!cgroup2.ok()) return cgroup2;
    const Status root_boundary = verify_daemon_owned_boundary(
        parent.value().get(), "Ratox delegated cgroup recovery root", true);
    if (!root_boundary.ok()) return root_boundary;

    for (const auto &control : {
             std::pair{std::string_view{"cgroup.procs"}, O_WRONLY},
             std::pair{std::string_view{"cgroup.threads"}, O_RDONLY},
             std::pair{std::string_view{"cgroup.subtree_control"}, O_RDONLY}}) {
        auto opened = open_control_file(
            parent.value().get(), control.first, control.second);
        if (!opened.ok()) return opened.status();
        const Status protected_control = verify_daemon_control_boundary(
            opened.value().get(), control.first);
        if (!protected_control.ok()) return protected_control;
    }

    auto names = list_reserved_cgroup_names(
        parent.value().get(), config.maximum_candidates);
    if (!names.ok()) return names.status();

    auto open_existing = [&parent](
                             const std::string &name)
        -> Result<SessionCgroup> {
        auto parent_copy = duplicate_descriptor(parent.value().get());
        if (!parent_copy.ok()) return parent_copy.status();

        auto implementation = std::make_unique<Impl>();
        implementation->cleanup_on_destroy_ = false;
        implementation->parent_ = std::move(parent_copy).value();
        implementation->name_ = name;
        implementation->owns_directory_ = true;

        struct stat named_leaf {};
        if (::fstatat(
                implementation->parent_.get(), implementation->name_.c_str(),
                &named_leaf, AT_SYMLINK_NOFOLLOW) != 0) {
            const ErrorCode code = errno == ENOENT ? ErrorCode::unavailable
                                                    : ErrorCode::io_error;
            return errno_status(
                code, "pin existing Ratox session cgroup pathname");
        }
        if (!S_ISDIR(named_leaf.st_mode)) {
            return Status{
                ErrorCode::unavailable,
                "reserved Ratox session cgroup name is not a directory"};
        }
        implementation->device_ = named_leaf.st_dev;
        implementation->inode_ = named_leaf.st_ino;

        implementation->directory_.reset(::openat(
            implementation->parent_.get(), implementation->name_.c_str(),
            O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
        if (implementation->directory_.get() < 0) {
            return errno_status(
                ErrorCode::unavailable,
                "open existing Ratox session cgroup");
        }
        struct stat opened_leaf {};
        if (::fstat(implementation->directory_.get(), &opened_leaf) != 0) {
            return errno_status(
                ErrorCode::io_error,
                "inspect existing Ratox session cgroup inode");
        }
        if (!S_ISDIR(opened_leaf.st_mode) ||
            opened_leaf.st_dev != implementation->device_ ||
            opened_leaf.st_ino != implementation->inode_) {
            return Status{
                ErrorCode::unavailable,
                "Ratox session cgroup changed while recovery pinned its inode"};
        }
        const Status leaf_cgroup2 = require_cgroup2_filesystem(
            implementation->directory_.get(), "Ratox recovery session cgroup");
        if (!leaf_cgroup2.ok()) return leaf_cgroup2;
        const Status leaf_boundary = verify_daemon_owned_boundary(
            implementation->directory_.get(),
            "Ratox recovery session cgroup directory", true);
        if (!leaf_boundary.ok()) return leaf_boundary;

        auto procs = open_control_file(
            implementation->directory_.get(), "cgroup.procs", O_RDWR);
        if (!procs.ok()) return procs.status();
        implementation->procs_ = std::move(procs).value();
        auto kill = open_control_file(
            implementation->directory_.get(), "cgroup.kill", O_WRONLY);
        if (!kill.ok()) return kill.status();
        implementation->kill_ = std::move(kill).value();
        auto events = open_control_file(
            implementation->directory_.get(), "cgroup.events", O_RDONLY);
        if (!events.ok()) return events.status();
        implementation->events_ = std::move(events).value();
        auto type = open_control_file(
            implementation->directory_.get(), "cgroup.type", O_RDONLY);
        if (!type.ok()) return type.status();
        implementation->type_ = std::move(type).value();
        auto threads = open_control_file(
            implementation->directory_.get(), "cgroup.threads", O_RDONLY);
        if (!threads.ok()) return threads.status();
        implementation->threads_ = std::move(threads).value();
        auto subtree_control = open_control_file(
            implementation->directory_.get(), "cgroup.subtree_control",
            O_RDONLY);
        if (!subtree_control.ok()) return subtree_control.status();
        implementation->subtree_control_ =
            std::move(subtree_control).value();

        const std::array protected_controls{
            std::pair{implementation->procs_.get(),
                      std::string_view{"cgroup.procs"}},
            std::pair{implementation->kill_.get(),
                      std::string_view{"cgroup.kill"}},
            std::pair{implementation->type_.get(),
                      std::string_view{"cgroup.type"}},
            std::pair{implementation->threads_.get(),
                      std::string_view{"cgroup.threads"}},
            std::pair{implementation->subtree_control_.get(),
                      std::string_view{"cgroup.subtree_control"}},
        };
        for (const auto &[descriptor, control_name] : protected_controls) {
            const Status protected_control = verify_daemon_control_boundary(
                descriptor, control_name);
            if (!protected_control.ok()) return protected_control;
        }

        auto type_record = read_control_record(
            implementation->type_.get(), "cgroup.type", 64U);
        if (!type_record.ok()) return type_record.status();
        if (type_record.value() != "domain\n") {
            return Status{
                ErrorCode::unsupported,
                "Ratox recovery session cgroup is not a non-threaded domain"};
        }
        auto subtree_record = read_control_record(
            implementation->subtree_control_.get(),
            "cgroup.subtree_control");
        if (!subtree_record.ok()) return subtree_record.status();
        if (!subtree_record.value().empty()) {
            return Status{
                ErrorCode::unavailable,
                "Ratox recovery session cgroup enabled child controllers"};
        }
        const Status childless = require_no_child_cgroups(
            implementation->directory_.get());
        if (!childless.ok()) return childless;

        return SessionCgroup(std::move(implementation));
    };

    CgroupRecoveryReport report;
    report.reserved_names = names.value().size();
    std::vector<SessionCgroup> stale_incarnations;
    std::vector<SessionCgroup> empty_legacy;
    stale_incarnations.reserve(names.value().size());
    empty_legacy.reserve(names.value().size());

    for (const std::string &name : names.value()) {
        const bool versioned =
            std::string_view{name}.starts_with(kSessionCgroupV2Prefix);
        std::optional<SessionCgroupName> parsed_name;
        if (versioned) {
            auto parsed = parse_session_cgroup_name(name);
            if (!parsed.ok()) {
                return Status{
                    parsed.status().code(),
                    "malformed reserved Ratox cgroup '" + name + "': " +
                        parsed.status().message()};
            }
            parsed_name = parsed.value();
        } else {
            const Status legacy = validate_legacy_session_cgroup_name(name);
            if (!legacy.ok()) {
                return Status{
                    legacy.code(),
                    "malformed reserved Ratox cgroup '" + name + "': " +
                        legacy.message()};
            }
        }

        auto opened = open_existing(name);
        if (!opened.ok()) {
            return Status{
                opened.status().code(),
                "unable to validate reserved Ratox cgroup '" + name + "': " +
                    opened.status().message()};
        }

        if (versioned) {
            auto live = cgroup_owner_is_live(parsed_name->owner);
            if (!live.ok()) {
                return Status{
                    live.status().code(),
                    "unable to prove owner lifetime for Ratox cgroup '" +
                        name + "': " + live.status().message()};
            }
            if (live.value()) {
                ++report.live_incarnations;
            } else {
                ++report.stale_incarnations;
                stale_incarnations.push_back(std::move(opened).value());
            }
            continue;
        }

        auto populated = opened.value().populated();
        if (!populated.ok()) {
            return Status{
                populated.status().code(),
                "unable to inspect legacy Ratox cgroup '" + name + "': " +
                    populated.status().message()};
        }
        if (populated.value()) {
            return Status{
                ErrorCode::unavailable,
                "populated legacy Ratox cgroup '" + name +
                    "' cannot be reclaimed without a PID-reuse-safe owner identity"};
        }
        empty_legacy.push_back(std::move(opened).value());
    }

    for (SessionCgroup &legacy : empty_legacy) {
        const Status removed = legacy.remove_if_empty();
        if (!removed.ok()) {
            return Status{
                removed.code(),
                "unable to remove an empty legacy Ratox cgroup: " +
                    removed.message()};
        }
        ++report.empty_legacy_removed;
    }

    std::vector<bool> removed(stale_incarnations.size(), false);
    std::size_t remaining = stale_incarnations.size();
    for (std::size_t index = 0U; index < stale_incarnations.size(); ++index) {
        auto populated = stale_incarnations[index].populated();
        if (!populated.ok()) return populated.status();
        if (populated.value()) {
            const Status killed = stale_incarnations[index].kill_all();
            if (!killed.ok()) return killed;
        } else {
            const Status removed_now =
                stale_incarnations[index].remove_if_empty();
            if (!removed_now.ok()) return removed_now;
            removed[index] = true;
            --remaining;
            ++report.recovered_incarnations;
        }
    }

    const auto deadline =
        std::chrono::steady_clock::now() + config.maximum_wait;
    std::vector<struct pollfd> observed_events;
    observed_events.reserve(stale_incarnations.size());
    while (remaining > 0U) {
        for (std::size_t index = 0U; index < stale_incarnations.size();
             ++index) {
            if (removed[index]) continue;
            auto populated = stale_incarnations[index].populated();
            if (!populated.ok()) return populated.status();
            if (populated.value()) continue;
            const Status removed_now =
                stale_incarnations[index].remove_if_empty();
            if (!removed_now.ok()) return removed_now;
            removed[index] = true;
            --remaining;
            ++report.recovered_incarnations;
        }
        if (remaining == 0U) break;
        if (std::chrono::steady_clock::now() >= deadline) {
            return Status{
                ErrorCode::timeout,
                "Ratox startup cgroup recovery timed out with " +
                    std::to_string(remaining) +
                    " stale incarnation(s) still populated"};
        }

        observed_events.clear();
        for (std::size_t index = 0U; index < stale_incarnations.size();
             ++index) {
            if (removed[index]) continue;
            const int descriptor =
                stale_incarnations[index].implementation_->events_descriptor();
            if (descriptor < 0) {
                return Status{
                    ErrorCode::unavailable,
                    "stale Ratox cgroup lost its event descriptor while waiting"};
            }
            observed_events.push_back(pollfd{descriptor, POLLPRI, 0});
        }
        auto changed = wait_for_cgroup_event_change(
            observed_events, deadline);
        if (!changed.ok()) return changed.status();
        if (!changed.value()) {
            return Status{
                ErrorCode::timeout,
                "Ratox startup cgroup recovery timed out with " +
                    std::to_string(remaining) +
                    " stale incarnation(s) still populated"};
        }
    }

    return report;
}

Status SessionCgroup::attach(pid_t process) {
    if (!implementation_) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox session cgroup is not initialized"};
    }
    return implementation_->attach(process);
}

Status SessionCgroup::kill_all() {
    if (!implementation_) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox session cgroup is not initialized"};
    }
    return implementation_->kill_all();
}

Result<bool> SessionCgroup::populated() {
    if (!implementation_) {
        return Status{ErrorCode::invalid_argument,
                      "Ratox session cgroup is not initialized"};
    }
    return implementation_->populated();
}

Status SessionCgroup::remove_if_empty() {
    if (!implementation_) return Status::success();
    return implementation_->remove_if_empty();
}

std::optional<CgroupSessionOutcome> SessionCgroup::take_outcome() noexcept {
    if (!implementation_) return std::nullopt;
    return implementation_->take_outcome();
}

bool SessionCgroup::best_effort_kill_and_remove(
    std::chrono::milliseconds maximum_wait) noexcept {
    return implementation_ == nullptr ||
           implementation_->best_effort_kill_and_remove(maximum_wait);
}

}  // namespace iotox::terminal::detail
