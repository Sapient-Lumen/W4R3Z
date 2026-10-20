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
#include <csignal>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fcntl.h>
#include <iostream>
#include <limits>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <system_error>
#include <sys/mount.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <thread>
#include <utility>
#include <unistd.h>
#include <vector>

namespace {

using iotox::ErrorCode;
using iotox::terminal::CgroupIoDevice;
using iotox::terminal::CgroupPressureAdmissionLimits;
using iotox::terminal::CgroupResourceLimits;
using iotox::terminal::IdentityMode;
using iotox::terminal::IdentityPolicy;
using iotox::terminal::detail::CgroupRecoveryConfig;
using iotox::terminal::detail::CgroupCpuStat;
using iotox::terminal::detail::CgroupIoMax;
using iotox::terminal::detail::CgroupIrqPressure;
using iotox::terminal::detail::CgroupLocalStat;
using iotox::terminal::detail::CgroupMemoryStat;
using iotox::terminal::detail::CgroupMemorySwapEvents;
using iotox::terminal::detail::CgroupPressure;
using iotox::terminal::detail::CgroupPressureAdmission;
using iotox::terminal::detail::SessionCgroup;
using iotox::terminal::detail::parse_cgroup_cpu_stat;
using iotox::terminal::detail::parse_cgroup_events;
using iotox::terminal::detail::parse_cgroup_io_max;
using iotox::terminal::detail::parse_cgroup_io_stat;
using iotox::terminal::detail::parse_cgroup_irq_pressure;
using iotox::terminal::detail::parse_cgroup_local_stat;
using iotox::terminal::detail::parse_cgroup_memory_stat;
using iotox::terminal::detail::parse_cgroup_memory_swap_events;
using iotox::terminal::detail::parse_cgroup_peak;
using iotox::terminal::detail::parse_cgroup_pressure;

[[noreturn]] void fail(std::string_view message) {
    throw std::runtime_error(std::string(message));
}

void require(bool condition, std::string_view message) {
    if (!condition) fail(message);
}

class SkipQualification final : public std::runtime_error {
  public:
    explicit SkipQualification(std::string message)
        : std::runtime_error(std::move(message)) {}
};

[[noreturn]] void skip(std::string message) {
    throw SkipQualification(std::move(message));
}

enum class OracleMode : std::uint8_t {
    lifecycle,
    memory_resources,
    cpu_resources,
    io_resources,
    pressure_admission,
};

void write_record(
    const std::filesystem::path &path, std::string_view record);
[[nodiscard]] std::string read_record(const std::filesystem::path &path);
void create_cgroup_directory_or_skip(
    const std::filesystem::path &path, std::string_view label);
void require_cgroup_setup_root_or_skip(
    const std::filesystem::path &path, std::string_view label);
[[nodiscard]] std::optional<std::uint64_t> read_optional_peak(
    const std::filesystem::path &leaf, std::string_view interface_name);
[[nodiscard]] std::optional<CgroupMemoryStat> read_optional_memory_stat(
    const std::filesystem::path &leaf);
[[nodiscard]] std::optional<CgroupMemorySwapEvents>
read_optional_memory_swap_events(const std::filesystem::path &leaf);
[[nodiscard]] std::optional<CgroupLocalStat> read_optional_local_stat(
    const std::filesystem::path &leaf);
[[nodiscard]] std::optional<CgroupIrqPressure> read_optional_irq_pressure(
    const std::filesystem::path &leaf);
[[nodiscard]] CgroupCpuStat read_cpu_stat(
    const std::filesystem::path &leaf);

[[nodiscard]] std::set<std::string> controller_set(
    std::string_view record) {
    std::set<std::string> result;
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        while (cursor < record.size() &&
               (record[cursor] == ' ' || record[cursor] == '\n')) {
            ++cursor;
        }
        if (cursor == record.size()) break;
        const std::size_t end = record.find_first_of(" \n", cursor);
        result.emplace(record.substr(
            cursor, end == std::string_view::npos
                        ? record.size() - cursor
                        : end - cursor));
        if (end == std::string_view::npos) break;
        cursor = end + 1U;
    }
    return result;
}

[[nodiscard]] std::vector<std::string_view> required_controllers(
    OracleMode mode) {
    switch (mode) {
        case OracleMode::memory_resources:
            return {"memory", "pids"};
        case OracleMode::cpu_resources:
            return {"cpu"};
        case OracleMode::io_resources:
            return {"io"};
        case OracleMode::pressure_admission:
            return {};
        case OracleMode::lifecycle:
            return {};
    }
    fail("unknown cgroup oracle mode");
}

[[nodiscard]] std::string controller_enable_record(OracleMode mode) {
    switch (mode) {
        case OracleMode::memory_resources:
            return "+memory +pids\n";
        case OracleMode::cpu_resources:
            return "+cpu\n";
        case OracleMode::io_resources:
            return "+io\n";
        case OracleMode::pressure_admission:
            break;
        case OracleMode::lifecycle:
            break;
    }
    fail("lifecycle mode has no controller enable record");
}

[[nodiscard]] bool has_required_resource_controllers(
    const std::filesystem::path &root,
    const std::vector<std::string_view> &required,
    std::string &reason) {
    const std::set<std::string> available = controller_set(
        read_record(root / "cgroup.controllers"));
    const std::set<std::string> enabled = controller_set(
        read_record(root / "cgroup.subtree_control"));
    for (const std::string_view controller : required) {
        const std::string name{controller};
        if (!available.contains(name)) {
            reason = "required controller '" + name +
                     "' is unavailable";
            return false;
        }
        if (!enabled.contains(name)) {
            reason = "required controller '" + name +
                     "' is not preactivated for child cgroups";
            return false;
        }
    }
    return true;
}

class MountedCgroup2 {
  public:
    explicit MountedCgroup2(OracleMode mode) {
        std::array<char, 96U> pattern{};
        const std::string prototype =
            "/tmp/iotox-cgroup-recovery-process-XXXXXX";
        require(prototype.size() + 1U <= pattern.size(),
                "temporary path pattern is too long");
        std::copy(prototype.begin(), prototype.end(), pattern.begin());
        char *created = ::mkdtemp(pattern.data());
        if (created == nullptr) {
            fail(std::string("mkdtemp failed: ") + std::strerror(errno));
        }
        parent_ = created;
        mount_root_ = parent_ / "mount";
        require(std::filesystem::create_directory(mount_root_),
                "unable to create cgroup mount point");
        require(::chmod(mount_root_.c_str(), static_cast<mode_t>(0700)) == 0,
                "unable to protect cgroup mount point");
        if (::mount(
                "none", mount_root_.c_str(), "cgroup2",
                MS_NOSUID | MS_NODEV | MS_NOEXEC, nullptr) != 0) {
            const int failure = errno;
            std::filesystem::remove_all(parent_);
            fail(std::string("mount cgroup2 failed: ") +
                 std::strerror(failure));
        }
        mounted_ = true;

        try {
            if (mode == OracleMode::lifecycle) {
                // Preserve the rev0028 lifecycle oracle on hosts whose cgroup
                // namespace root can create literal non-threaded domain
                // children. A threaded-domain root yields domain-invalid
                // children, so treating that topology as lifecycle evidence
                // would contradict the production cgroup.type invariant.
                const std::string type =
                    read_record(mount_root_ / "cgroup.type");
                if (type != "domain\n") {
                    skip("cgroup namespace root cannot provide non-threaded lifecycle leaves (observed '" +
                         type + "')");
                }
                require_cgroup_setup_root_or_skip(
                    mount_root_, "cgroup namespace root");
                root_ = mount_root_;
                return;
            }

            const std::string type = read_record(mount_root_ / "cgroup.type");
            if (type != "domain\n") {
                skip("cgroup namespace root is not a non-threaded domain (observed '" +
                     type + "')");
            }
            const std::vector<std::string_view> required =
                required_controllers(mode);
            const std::set<std::string> available = controller_set(
                read_record(mount_root_ / "cgroup.controllers"));
            const std::set<std::string> enabled = controller_set(
                read_record(mount_root_ / "cgroup.subtree_control"));
            bool needs_preactivation = false;
            for (const std::string_view controller : required) {
                const std::string name{controller};
                if (!available.contains(name)) {
                    skip("required controller '" + name +
                         "' is unavailable");
                }
                needs_preactivation =
                    needs_preactivation || !enabled.contains(name);
            }
            if (needs_preactivation) {
                // A fresh cgroup namespace can expose delegated controllers
                // without preactivating them. Move this oracle into a sibling
                // leaf so the namespace root satisfies the cgroup-v2
                // no-internal-process rule, then construct the exact private
                // delegation needed by the production SessionCgroup probe.
                anchor_root_ = mount_root_ / "_iotox_oracle_anchor";
                create_cgroup_directory_or_skip(
                    anchor_root_, "cgroup oracle anchor");
                write_record(
                    anchor_root_ / "cgroup.procs",
                    std::to_string(static_cast<std::int64_t>(::getpid())) +
                        "\n");
                write_record(
                    mount_root_ / "cgroup.subtree_control",
                    controller_enable_record(mode));
            }
            std::string controller_reason;
            if (!has_required_resource_controllers(
                    mount_root_, required, controller_reason)) {
                skip(controller_reason);
            }

            const std::string suffix = std::to_string(
                static_cast<std::int64_t>(::getpid()));
            root_ = mount_root_ / ("_iotox_oracle_delegated_" + suffix);
            create_cgroup_directory_or_skip(
                root_, "resource-enabled oracle delegation");
            require_cgroup_setup_root_or_skip(
                root_, "resource-enabled oracle delegation");
            if (mode == OracleMode::memory_resources) {
                inactive_root_ =
                    mount_root_ / ("_iotox_oracle_inactive_" + suffix);
                create_cgroup_directory_or_skip(
                    inactive_root_,
                    "inactive-controller oracle delegation");
            }
            require(read_record(root_ / "cgroup.type") == "domain\n",
                    "resource oracle child is not a non-threaded domain");
            if (mode != OracleMode::pressure_admission) {
                write_record(
                    root_ / "cgroup.subtree_control",
                    controller_enable_record(mode));
                std::string delegated_reason;
                require(has_required_resource_controllers(
                            root_, required, delegated_reason),
                        delegated_reason);
            }
        } catch (...) {
            cleanup_mount();
            throw;
        }
    }

    ~MountedCgroup2() { cleanup_mount(); }

    MountedCgroup2(const MountedCgroup2 &) = delete;
    MountedCgroup2 &operator=(const MountedCgroup2 &) = delete;

    [[nodiscard]] const std::filesystem::path &root() const noexcept {
        return root_;
    }

    [[nodiscard]] const std::filesystem::path &inactive_root() const noexcept {
        return inactive_root_;
    }

  private:
    void cleanup_mount() noexcept {
        if (mounted_) {
            if (!root_.empty() && root_ != mount_root_) {
                static_cast<void>(::rmdir(root_.c_str()));
            }
            if (!inactive_root_.empty()) {
                static_cast<void>(::rmdir(inactive_root_.c_str()));
            }
            if (!anchor_root_.empty()) {
                const std::string process =
                    std::to_string(static_cast<std::int64_t>(::getpid())) +
                    "\n";
                const std::filesystem::path destination =
                    mount_root_ / "cgroup.procs";
                const int descriptor = ::open(
                    destination.c_str(), O_WRONLY | O_CLOEXEC | O_NOFOLLOW);
                if (descriptor >= 0) {
                    const ssize_t moved = ::write(
                        descriptor, process.data(), process.size());
                    static_cast<void>(moved);
                    static_cast<void>(::close(descriptor));
                }
                static_cast<void>(::rmdir(anchor_root_.c_str()));
            }
            static_cast<void>(::umount2(mount_root_.c_str(), MNT_DETACH));
            mounted_ = false;
        }
        std::error_code ignored;
        std::filesystem::remove_all(parent_, ignored);
    }

    std::filesystem::path parent_;
    std::filesystem::path mount_root_;
    std::filesystem::path root_;
    std::filesystem::path inactive_root_;
    std::filesystem::path anchor_root_;
    bool mounted_{false};
};

[[nodiscard]] IdentityPolicy contained_identity() {
    IdentityPolicy identity;
    identity.mode = IdentityMode::exact;
    identity.uid = 65534U;
    identity.gid = 65534U;
    identity.clear_supplementary_groups = true;
    return identity;
}

[[nodiscard]] std::vector<std::filesystem::path> reserved_directories(
    const std::filesystem::path &root) {
    std::vector<std::filesystem::path> result;
    for (const auto &entry : std::filesystem::directory_iterator(root)) {
        const std::string name = entry.path().filename().string();
        if (name.starts_with("_iotox_session_") && entry.is_directory()) {
            result.push_back(entry.path());
        }
    }
    std::sort(result.begin(), result.end());
    return result;
}

void write_record(
    const std::filesystem::path &path, std::string_view record) {
    const int descriptor = ::open(
        path.c_str(), O_WRONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        fail(std::string("open write record failed: ") + std::strerror(errno));
    }
    ssize_t written = -1;
    do {
        written = ::write(descriptor, record.data(), record.size());
    } while (written < 0 && errno == EINTR);
    const int failure = written < 0 ? errno : 0;
    const int close_result = ::close(descriptor);
    if (written != static_cast<ssize_t>(record.size())) {
        fail(std::string("write record failed: ") + std::strerror(failure));
    }
    require(close_result == 0, "close after write failed");
}

[[nodiscard]] std::string read_record(const std::filesystem::path &path) {
    const int descriptor = ::open(
        path.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        fail(std::string("open read record failed: ") + std::strerror(errno));
    }
    std::string result;
    std::array<char, 4096U> buffer{};
    while (true) {
        ssize_t count = -1;
        do {
            count = ::read(descriptor, buffer.data(), buffer.size());
        } while (count < 0 && errno == EINTR);
        if (count < 0) {
            const int failure = errno;
            static_cast<void>(::close(descriptor));
            fail(std::string("read record failed: ") +
                 std::strerror(failure));
        }
        if (count == 0) break;
        result.append(buffer.data(), static_cast<std::size_t>(count));
    }
    require(::close(descriptor) == 0, "close after read failed");
    return result;
}

[[nodiscard]] bool is_cgroup_setup_permission_error(int value) noexcept {
    return value == EACCES || value == EPERM || value == EROFS;
}

void create_cgroup_directory_or_skip(
    const std::filesystem::path &path, std::string_view label) {
    std::error_code error;
    if (std::filesystem::create_directory(path, error)) return;
    const std::string named_label{label};
    if (!error) {
        fail(named_label + " already exists");
    }
    if (is_cgroup_setup_permission_error(error.value())) {
        skip(named_label + " cannot be created in this cgroup namespace: " +
             error.message());
    }
    fail("unable to create " + named_label + ": " + error.message());
}

void require_cgroup_setup_root_or_skip(
    const std::filesystem::path &path, std::string_view label) {
    const std::string named_label{label};
    const int descriptor = ::open(
        path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        const int failure = errno;
        if (is_cgroup_setup_permission_error(failure)) {
            skip(named_label + " is not accessible as a cgroup setup root: " +
                 std::strerror(failure));
        }
        fail("open " + named_label + " failed: " + std::strerror(failure));
    }

    struct stat metadata {};
    const int stat_result = ::fstat(descriptor, &metadata);
    const int stat_failure = stat_result == 0 ? 0 : errno;
    require(::close(descriptor) == 0, "close cgroup setup root failed");
    if (stat_result != 0) {
        if (is_cgroup_setup_permission_error(stat_failure)) {
            skip(named_label + " cannot be inspected as a cgroup setup root: " +
                 std::strerror(stat_failure));
        }
        fail("inspect " + named_label + " failed: " +
             std::strerror(stat_failure));
    }
    if (metadata.st_uid != ::geteuid()) {
        skip(named_label + " is not owned by this cgroup oracle uid");
    }
    if ((metadata.st_mode & static_cast<mode_t>(0022)) != 0) {
        skip(named_label + " is not owner-private");
    }

    const std::filesystem::path probe =
        path / ("_iotox_oracle_probe_" +
                std::to_string(static_cast<std::int64_t>(::getpid())));
    create_cgroup_directory_or_skip(probe, named_label + " write probe");
    if (::rmdir(probe.c_str()) != 0) {
        const int failure = errno;
        if (is_cgroup_setup_permission_error(failure)) {
            skip(named_label + " write probe cannot be removed: " +
                 std::strerror(failure));
        }
        fail("remove " + named_label + " write probe failed: " +
             std::strerror(failure));
    }
}

[[nodiscard]] std::uint64_t read_flat_counter(
    const std::filesystem::path &path, std::string_view key) {
    const std::string record = read_record(path);
    const std::string prefix = std::string(key) + " ";
    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        require(end != std::string::npos,
                "flat counter record omitted its final newline");
        const std::string_view line{record.data() + cursor, end - cursor};
        if (line.starts_with(prefix)) {
            const std::string value{line.substr(prefix.size())};
            std::size_t consumed = 0U;
            const unsigned long long parsed = std::stoull(value, &consumed);
            require(consumed == value.size(),
                    "flat counter value was not canonical decimal");
            return static_cast<std::uint64_t>(parsed);
        }
        cursor = end + 1U;
    }
    fail("flat counter record omitted the requested key");
}

[[nodiscard]] std::uint64_t parse_canonical_counter(
    std::string_view value, std::string_view label) {
    require(!value.empty(), std::string(label) + " is empty");
    require(value == "0" || value.front() != '0',
            std::string(label) + " is not canonical decimal");
    std::uint64_t parsed = 0U;
    const auto result = std::from_chars(
        value.data(), value.data() + value.size(), parsed);
    require(result.ec == std::errc{} &&
                result.ptr == value.data() + value.size(),
            std::string(label) + " is not an unsigned decimal");
    return parsed;
}

[[nodiscard]] CgroupIoDevice parse_canonical_device(
    std::string_view value) {
    const std::size_t colon = value.find(':');
    require(colon != std::string_view::npos && colon > 0U &&
                colon + 1U < value.size() &&
                value.find(':', colon + 1U) == std::string_view::npos,
            "io.stat device key is malformed");
    const std::uint64_t major = parse_canonical_counter(
        value.substr(0U, colon), "io.stat device major");
    const std::uint64_t minor = parse_canonical_counter(
        value.substr(colon + 1U), "io.stat device minor");
    require(major <= std::numeric_limits<std::uint32_t>::max() &&
                minor <= std::numeric_limits<std::uint32_t>::max() &&
                (major != 0U || minor != 0U),
            "io.stat device key is outside the supported range");
    return CgroupIoDevice{
        static_cast<std::uint32_t>(major),
        static_cast<std::uint32_t>(minor)};
}

[[nodiscard]] std::optional<CgroupIoDevice> written_io_device(
    std::string_view record) {
    auto aggregate = parse_cgroup_io_stat(record);
    require(aggregate.ok(), aggregate.status().message());
    if (aggregate.value().write_bytes == 0U &&
        aggregate.value().write_operations == 0U) {
        return std::nullopt;
    }

    std::size_t cursor = 0U;
    while (cursor < record.size()) {
        const std::size_t end = record.find('\n', cursor);
        require(end != std::string_view::npos && end > cursor,
                "io.stat probe record contains a malformed line");
        const std::string_view line = record.substr(cursor, end - cursor);
        const std::size_t first_space = line.find(' ');
        require(first_space != std::string_view::npos && first_space > 0U,
                "io.stat probe line omitted its device key");
        bool wrote = false;
        std::size_t field_cursor = first_space + 1U;
        while (field_cursor < line.size()) {
            const std::size_t separator = line.find(' ', field_cursor);
            const std::size_t field_end =
                separator == std::string_view::npos ? line.size() : separator;
            const std::string_view field =
                line.substr(field_cursor, field_end - field_cursor);
            const std::size_t equals = field.find('=');
            require(equals != std::string_view::npos && equals > 0U &&
                        equals + 1U < field.size(),
                    "io.stat probe line contains a malformed field");
            const std::string_view key = field.substr(0U, equals);
            if ((key == "wbytes" || key == "wios") &&
                parse_canonical_counter(
                    field.substr(equals + 1U), "io.stat write counter") > 0U) {
                wrote = true;
            }
            if (separator == std::string_view::npos) break;
            field_cursor = separator + 1U;
        }
        if (wrote) {
            return parse_canonical_device(line.substr(0U, first_space));
        }
        cursor = end + 1U;
    }
    return std::nullopt;
}

[[nodiscard]] std::filesystem::path unique_io_path(
    std::string_view label) {
    return std::filesystem::path{"/tmp"} /
           ("iotox-cgroup-io-" + std::string(label) + "-" +
            std::to_string(static_cast<std::int64_t>(::getpid())) + "-" +
            std::to_string(static_cast<std::uint64_t>(
                std::chrono::steady_clock::now().time_since_epoch().count())));
}

[[nodiscard]] pid_t fork_sync_writer(
    const std::filesystem::path &path,
    const std::array<int, 2U> &command_descriptors,
    std::size_t bytes_to_write) {
    const pid_t writer = ::fork();
    require(writer >= 0, "unable to fork cgroup I/O writer");
    if (writer != 0) return writer;

    static_cast<void>(::close(command_descriptors[1U]));
    char command = 0;
    ssize_t received = -1;
    do {
        received = ::read(command_descriptors[0U], &command, 1U);
    } while (received < 0 && errno == EINTR);
    if (received != 1 || command != 'W') ::_exit(131);
    static_cast<void>(::close(command_descriptors[0U]));

    const int output = ::open(
        path.c_str(), O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_DSYNC,
        static_cast<mode_t>(0600));
    if (output < 0) ::_exit(132);
    std::array<std::uint8_t, 64U * 1024U> block{};
    for (std::size_t index = 0U; index < block.size(); ++index) {
        block[index] = static_cast<std::uint8_t>(index ^ 0x5aU);
    }
    std::size_t remaining = bytes_to_write;
    while (remaining > 0U) {
        const std::size_t requested = std::min(remaining, block.size());
        ssize_t count = -1;
        do {
            count = ::write(output, block.data(), requested);
        } while (count < 0 && errno == EINTR);
        if (count <= 0) ::_exit(133);
        remaining -= static_cast<std::size_t>(count);
    }
    if (::fdatasync(output) != 0) ::_exit(134);
    if (::close(output) != 0) ::_exit(135);
    ::_exit(0);
}

void release_writer(int descriptor) {
    ssize_t written = -1;
    do {
        written = ::write(descriptor, "W", 1U);
    } while (written < 0 && errno == EINTR);
    require(written == 1, "unable to release cgroup I/O writer");
}

void remove_empty_cgroup(const std::filesystem::path &path) {
    if (::rmdir(path.c_str()) != 0) {
        fail(std::string("rmdir cgroup failed: ") + std::strerror(errno));
    }
}

void wait_for_empty_cgroup(const std::filesystem::path &path) {
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds{5};
    while (true) {
        auto events = parse_cgroup_events(read_record(path / "cgroup.events"));
        require(events.ok(), "cgroup.events failed to parse during cleanup");
        if (!events.value().populated) return;
        require(std::chrono::steady_clock::now() < deadline,
                "cgroup remained populated during cleanup");
        std::this_thread::sleep_for(std::chrono::milliseconds{1});
    }
}

void wait_for_frozen_state(
    const std::filesystem::path &path, bool expected) {
    const auto deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds{5};
    while (true) {
        auto events = parse_cgroup_events(read_record(path / "cgroup.events"));
        require(events.ok(), "cgroup.events failed to parse during freeze");
        require(events.value().frozen.has_value(),
                "cgroup.events omitted freezer state");
        if (*events.value().frozen == expected) return;
        require(std::chrono::steady_clock::now() < deadline,
                "cgroup did not reach the requested freezer state");
        std::this_thread::sleep_for(std::chrono::milliseconds{1});
    }
}

struct CreatorMessage {
    std::int32_t status{0};
    std::int32_t payload_process{0};
};

struct ForkLimitMessage {
    std::int32_t created{0};
    std::int32_t failure{0};
};

void write_fork_limit_message(
    int descriptor, ForkLimitMessage message) noexcept {
    const auto *bytes = reinterpret_cast<const std::uint8_t *>(&message);
    std::size_t offset = 0U;
    while (offset < sizeof(message)) {
        ssize_t count = ::write(
            descriptor, bytes + offset, sizeof(message) - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) break;
        offset += static_cast<std::size_t>(count);
    }
}

[[nodiscard]] ForkLimitMessage read_fork_limit_message(int descriptor) {
    ForkLimitMessage message;
    auto *bytes = reinterpret_cast<std::uint8_t *>(&message);
    std::size_t offset = 0U;
    while (offset < sizeof(message)) {
        ssize_t count = ::read(
            descriptor, bytes + offset, sizeof(message) - offset);
        if (count < 0 && errno == EINTR) continue;
        require(count > 0,
                "fork-limit pipe closed before one complete message");
        offset += static_cast<std::size_t>(count);
    }
    return message;
}

void write_creator_message(int descriptor, CreatorMessage message) noexcept {
    const auto *bytes = reinterpret_cast<const std::uint8_t *>(&message);
    std::size_t offset = 0U;
    while (offset < sizeof(message)) {
        ssize_t count = ::write(
            descriptor, bytes + offset, sizeof(message) - offset);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) break;
        offset += static_cast<std::size_t>(count);
    }
}

[[nodiscard]] CreatorMessage read_creator_message(int descriptor) {
    CreatorMessage message;
    auto *bytes = reinterpret_cast<std::uint8_t *>(&message);
    std::size_t offset = 0U;
    while (offset < sizeof(message)) {
        ssize_t count = ::read(
            descriptor, bytes + offset, sizeof(message) - offset);
        if (count < 0 && errno == EINTR) continue;
        require(count > 0, "creator pipe closed before one complete message");
        offset += static_cast<std::size_t>(count);
    }
    return message;
}

void qualify_unlimited_cpu_accounting(const std::filesystem::path &root) {
    auto session = SessionCgroup::create(root, contained_identity());
    require(session.ok(), session.status().message());
    const auto leaves = reserved_directories(root);
    require(leaves.size() == 1U,
            "unlimited CPU accounting did not create exactly one leaf");

    std::array<int, 2U> command_pipe{};
    require(::pipe2(command_pipe.data(), O_CLOEXEC) == 0,
            "unable to create unlimited CPU accounting command pipe");
    const pid_t payload = ::fork();
    require(payload >= 0, "unable to fork unlimited CPU accounting payload");
    if (payload == 0) {
        static_cast<void>(::close(command_pipe[1U]));
        char command = 0;
        ssize_t received = -1;
        do {
            received = ::read(command_pipe[0U], &command, 1U);
        } while (received < 0 && errno == EINTR);
        if (received != 1 || command != 'B') ::_exit(126);
        const long page_size = ::sysconf(_SC_PAGESIZE);
        if (page_size <= 0) ::_exit(127);
        constexpr std::size_t kFaultBytes = 4U * 1024U * 1024U;
        void *allocation = ::mmap(
            nullptr,
            kFaultBytes,
            PROT_READ | PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS,
            -1,
            0);
        if (allocation == MAP_FAILED) ::_exit(128);
        auto *bytes = static_cast<volatile std::uint8_t *>(allocation);
        for (std::size_t offset = 0U; offset < kFaultBytes;
             offset += static_cast<std::size_t>(page_size)) {
            bytes[offset] = static_cast<std::uint8_t>(offset);
        }
        std::uint64_t accumulator = 1U;
        while (true) {
            accumulator = accumulator * 1664525U + 1013904223U;
            asm volatile("" : "+r"(accumulator));
        }
    }
    static_cast<void>(::close(command_pipe[0U]));
    const iotox::Status attached = session.value().attach(payload);
    require(attached.ok(), attached.message());
    require(::write(command_pipe[1U], "B", 1U) == 1,
            "unable to release unlimited CPU accounting payload");
    static_cast<void>(::close(command_pipe[1U]));
    std::this_thread::sleep_for(std::chrono::milliseconds{30});

    std::error_code local_stat_failure;
    const bool has_local_stat = std::filesystem::exists(
        leaves.front() / "cgroup.stat.local", local_stat_failure);
    require(!local_stat_failure,
            "unable to inspect cgroup.stat.local before freeze qualification");
    if (has_local_stat) {
        write_record(leaves.front() / "cgroup.freeze", "1\n");
        wait_for_frozen_state(leaves.front(), true);
        std::this_thread::sleep_for(std::chrono::milliseconds{20});
        write_record(leaves.front() / "cgroup.freeze", "0\n");
        wait_for_frozen_state(leaves.front(), false);
    }
    std::this_thread::sleep_for(std::chrono::milliseconds{30});

    const iotox::Status killed = session.value().kill_all();
    require(killed.ok(), killed.message());
    int payload_status = 0;
    require(::waitpid(payload, &payload_status, 0) == payload,
            "unable to reap unlimited CPU accounting payload");
    require(WIFSIGNALED(payload_status) && WTERMSIG(payload_status) == SIGKILL,
            "cgroup.kill did not terminate unlimited CPU accounting payload");
    wait_for_empty_cgroup(leaves.front());
    const CgroupCpuStat observed = read_cpu_stat(leaves.front());
    const auto observed_pids_peak = read_optional_peak(
        leaves.front(), "pids.peak");
    const auto observed_memory_peak = read_optional_peak(
        leaves.front(), "memory.peak");
    const auto observed_swap_peak = read_optional_peak(
        leaves.front(), "memory.swap.peak");
    const auto observed_memory_stat =
        read_optional_memory_stat(leaves.front());
    const auto observed_memory_swap_events =
        read_optional_memory_swap_events(leaves.front());
    const auto observed_local_stat =
        read_optional_local_stat(leaves.front());
    const auto observed_irq_pressure =
        read_optional_irq_pressure(leaves.front());

    const iotox::Status removed = session.value().remove_if_empty();
    require(removed.ok(), removed.message());
    const auto outcome = session.value().take_outcome();
    require(outcome.has_value() && outcome->telemetry_complete,
            "unlimited CPU session did not retain complete kernel outcomes");
    require(outcome->cpu_stat_observed,
            "unlimited CPU session lost quota-independent cpu.stat support");
    require(outcome->cpu_usage_microseconds == observed.usage_microseconds &&
                outcome->cpu_user_microseconds == observed.user_microseconds &&
                outcome->cpu_system_microseconds == observed.system_microseconds,
            "unlimited CPU session did not retain exact work accounting");
    require(outcome->cpu_usage_microseconds > 0U,
            "unlimited CPU session reported no payload work");
    require(outcome->cpu_bandwidth_stat_observed == observed.bandwidth.has_value(),
            "unlimited CPU session changed bandwidth capability state");
    require(outcome->pids_peak == observed_pids_peak &&
                outcome->memory_peak_bytes == observed_memory_peak &&
                outcome->memory_swap_peak_bytes == observed_swap_peak,
            "unlimited CPU session did not retain exact optional peaks");
    require(outcome->memory_stat == observed_memory_stat,
            "unlimited CPU session did not retain exact memory work evidence");
    require(!outcome->memory_stat.has_value() ||
                outcome->memory_stat->page_faults > 0U,
            "unlimited CPU session lost post-attachment page faults");
    require(outcome->memory_swap_events == observed_memory_swap_events,
            "unlimited CPU session did not retain exact swap event evidence");
    require(outcome->local_stat == observed_local_stat,
            "unlimited CPU session did not retain exact local freeze evidence");
    require(!outcome->local_stat.has_value() ||
                outcome->local_stat->frozen_microseconds > 0U,
            "unlimited CPU session lost positive freezer duration evidence");
    require(outcome->irq_pressure == observed_irq_pressure,
            "unlimited CPU session did not retain exact IRQ pressure evidence");
    require(reserved_directories(root).empty(),
            "unlimited CPU accounting leaf survived cleanup");
}

void qualify_live_incarnation(const std::filesystem::path &root) {
    {
        auto live = SessionCgroup::create(root, contained_identity());
        require(live.ok(), live.status().message());
        auto report = SessionCgroup::recover_orphans(root);
        require(report.ok(), report.status().message());
        require(report.value().reserved_names == 1U,
                "live recovery did not observe exactly one reserved cgroup");
        require(report.value().live_incarnations == 1U,
                "live recovery did not preserve the exact owner incarnation");
        require(report.value().stale_incarnations == 0U &&
                    report.value().recovered_incarnations == 0U,
                "live recovery classified the owner as stale");
        require(reserved_directories(root).size() == 1U,
                "live recovery removed the active owner cgroup");
    }
    require(reserved_directories(root).empty(),
            "live cgroup destructor did not remove its empty leaf");
}

void qualify_empty_legacy(const std::filesystem::path &root) {
    const std::filesystem::path legacy = root / "_iotox_session_999999_1";
    require(std::filesystem::create_directory(legacy),
            "unable to create empty legacy cgroup");
    auto report = SessionCgroup::recover_orphans(root);
    require(report.ok(), report.status().message());
    require(report.value().reserved_names == 1U &&
                report.value().empty_legacy_removed == 1U,
            "empty legacy cgroup was not removed explicitly");
    require(!std::filesystem::exists(legacy),
            "empty legacy cgroup survived recovery");
}

void qualify_stale_incarnation(const std::filesystem::path &root) {
    std::array<int, 2U> pipe_descriptors{};
    require(::pipe2(pipe_descriptors.data(), O_CLOEXEC) == 0,
            "unable to create creator pipe");
    const pid_t creator = ::fork();
    require(creator >= 0, "unable to fork stale cgroup creator");
    if (creator == 0) {
        static_cast<void>(::close(pipe_descriptors[0U]));
        auto session = SessionCgroup::create(root, contained_identity());
        if (!session.ok()) {
            write_creator_message(pipe_descriptors[1U], CreatorMessage{1, 0});
            ::_exit(1);
        }
        const pid_t payload = ::fork();
        if (payload < 0) {
            write_creator_message(pipe_descriptors[1U], CreatorMessage{2, 0});
            ::_exit(2);
        }
        if (payload == 0) {
            static_cast<void>(::close(pipe_descriptors[1U]));
            while (true) ::pause();
        }
        const iotox::Status attached = session.value().attach(payload);
        if (!attached.ok()) {
            static_cast<void>(::kill(payload, SIGKILL));
            static_cast<void>(::waitpid(payload, nullptr, 0));
            write_creator_message(pipe_descriptors[1U], CreatorMessage{3, 0});
            ::_exit(3);
        }
        write_creator_message(
            pipe_descriptors[1U],
            CreatorMessage{0, static_cast<std::int32_t>(payload)});
        // Deliberately bypass C++ destructors to model daemon termination after
        // the payload entered the exact cgroup leaf.
        ::_exit(0);
    }

    static_cast<void>(::close(pipe_descriptors[1U]));
    const CreatorMessage message = read_creator_message(pipe_descriptors[0U]);
    require(::close(pipe_descriptors[0U]) == 0,
            "unable to close creator pipe");
    int creator_status = 0;
    require(::waitpid(creator, &creator_status, 0) == creator,
            "unable to reap stale cgroup creator");
    require(WIFEXITED(creator_status) && WEXITSTATUS(creator_status) == 0 &&
                message.status == 0 && message.payload_process > 0,
            "stale cgroup creator failed before deliberate crash");

    const auto before = reserved_directories(root);
    require(before.size() == 1U,
            "crashed creator did not leave one reserved cgroup");
    auto events = parse_cgroup_events(read_record(before.front() / "cgroup.events"));
    require(events.ok() && events.value().populated,
            "crashed creator did not leave a populated cgroup");

    auto report = SessionCgroup::recover_orphans(root);
    require(report.ok(), report.status().message());
    require(report.value().reserved_names == 1U &&
                report.value().stale_incarnations == 1U &&
                report.value().recovered_incarnations == 1U &&
                report.value().live_incarnations == 0U,
            "crash recovery did not reclaim exactly one stale incarnation");
    require(reserved_directories(root).empty(),
            "recovered stale cgroup pathname still exists");
}

void qualify_populated_legacy_refusal(const std::filesystem::path &root) {
    const std::filesystem::path legacy = root / "_iotox_session_888888_1";
    require(std::filesystem::create_directory(legacy),
            "unable to create populated legacy cgroup");
    const pid_t payload = ::fork();
    require(payload >= 0, "unable to fork legacy payload");
    if (payload == 0) {
        while (true) ::pause();
    }
    write_record(
        legacy / "cgroup.procs",
        std::to_string(static_cast<std::int64_t>(payload)) + "\n");
    auto events = parse_cgroup_events(read_record(legacy / "cgroup.events"));
    require(events.ok() && events.value().populated,
            "legacy payload did not enter its cgroup");

    auto report = SessionCgroup::recover_orphans(root);
    require(!report.ok() && report.status().code() == ErrorCode::unavailable,
            "populated legacy cgroup was not refused fail closed");
    require(report.status().message().find("PID-reuse-safe") !=
                std::string::npos,
            "legacy refusal omitted its owner-identity reason");
    require(std::filesystem::exists(legacy),
            "legacy refusal unexpectedly removed the cgroup");
    require(::waitpid(payload, nullptr, WNOHANG) == 0,
            "legacy refusal unexpectedly killed the payload");

    write_record(legacy / "cgroup.kill", "1\n");
    int payload_status = 0;
    require(::waitpid(payload, &payload_status, 0) == payload,
            "unable to reap legacy payload after explicit cleanup");
    require(WIFSIGNALED(payload_status) && WTERMSIG(payload_status) == SIGKILL,
            "legacy payload did not receive cgroup.kill");
    wait_for_empty_cgroup(legacy);
    remove_empty_cgroup(legacy);
}

[[nodiscard]] std::filesystem::path local_or_hierarchical_events(
    const std::filesystem::path &leaf, std::string_view local_name,
    std::string_view hierarchical_name) {
    const std::filesystem::path local = leaf / local_name;
    std::error_code failure;
    if (std::filesystem::exists(local, failure)) return local;
    require(!failure, "unable to inspect local cgroup event interface");
    return leaf / hierarchical_name;
}

[[nodiscard]] std::optional<CgroupPressure> read_optional_pressure(
    const std::filesystem::path &leaf, std::string_view interface_name) {
    const std::filesystem::path path = leaf / interface_name;
    std::error_code failure;
    const bool exists = std::filesystem::exists(path, failure);
    require(!failure, "unable to inspect cgroup pressure interface");
    if (!exists) return std::nullopt;
    auto parsed = parse_cgroup_pressure(read_record(path));
    require(parsed.ok(), parsed.status().message());
    return std::move(parsed).value();
}

[[nodiscard]] std::optional<std::uint64_t> read_optional_peak(
    const std::filesystem::path &leaf, std::string_view interface_name) {
    const std::filesystem::path path = leaf / interface_name;
    std::error_code failure;
    const bool exists = std::filesystem::exists(path, failure);
    require(!failure, "unable to inspect cgroup peak interface");
    if (!exists) return std::nullopt;
    auto parsed = parse_cgroup_peak(read_record(path));
    require(parsed.ok(), parsed.status().message());
    return parsed.value();
}

[[nodiscard]] std::optional<CgroupMemoryStat> read_optional_memory_stat(
    const std::filesystem::path &leaf) {
    const std::filesystem::path path = leaf / "memory.stat";
    std::error_code failure;
    const bool exists = std::filesystem::exists(path, failure);
    require(!failure, "unable to inspect memory.stat interface");
    if (!exists) return std::nullopt;
    auto parsed = parse_cgroup_memory_stat(read_record(path));
    require(parsed.ok(), parsed.status().message());
    return std::move(parsed).value();
}

[[nodiscard]] std::optional<CgroupMemorySwapEvents>
read_optional_memory_swap_events(const std::filesystem::path &leaf) {
    const std::filesystem::path path = leaf / "memory.swap.events";
    std::error_code failure;
    const bool exists = std::filesystem::exists(path, failure);
    require(!failure, "unable to inspect memory.swap.events interface");
    if (!exists) return std::nullopt;
    auto parsed = parse_cgroup_memory_swap_events(read_record(path));
    require(parsed.ok(), parsed.status().message());
    return std::move(parsed).value();
}

[[nodiscard]] std::optional<CgroupLocalStat> read_optional_local_stat(
    const std::filesystem::path &leaf) {
    const std::filesystem::path path = leaf / "cgroup.stat.local";
    std::error_code failure;
    const bool exists = std::filesystem::exists(path, failure);
    require(!failure, "unable to inspect cgroup.stat.local interface");
    if (!exists) return std::nullopt;
    auto parsed = parse_cgroup_local_stat(read_record(path));
    require(parsed.ok(), parsed.status().message());
    return parsed.value();
}

[[nodiscard]] std::optional<CgroupIrqPressure> read_optional_irq_pressure(
    const std::filesystem::path &leaf) {
    const std::filesystem::path path = leaf / "irq.pressure";
    std::error_code failure;
    const bool exists = std::filesystem::exists(path, failure);
    require(!failure, "unable to inspect irq.pressure interface");
    if (!exists) return std::nullopt;
    auto parsed = parse_cgroup_irq_pressure(read_record(path));
    require(parsed.ok(), parsed.status().message());
    return parsed.value();
}

[[nodiscard]] CgroupCpuStat read_cpu_stat(
    const std::filesystem::path &leaf) {
    auto parsed = parse_cgroup_cpu_stat(read_record(leaf / "cpu.stat"));
    require(parsed.ok(), parsed.status().message());
    return std::move(parsed).value();
}

void qualify_memory_and_pids_resource_policy(
    const std::filesystem::path &root) {
    constexpr std::uint64_t kMemoryHighBytes = 32U * 1024U * 1024U;
    constexpr std::uint64_t kMemoryLimitBytes = 64U * 1024U * 1024U;
    CgroupResourceLimits limits;
    limits.maximum_processes = 4U;
    limits.maximum_memory_high_bytes = kMemoryHighBytes;
    limits.maximum_memory_bytes = kMemoryLimitBytes;
    limits.maximum_swap_bytes = 0U;

    const iotox::Status preflight = SessionCgroup::preflight(
        root, contained_identity(), limits);
    require(preflight.ok(), preflight.message());
    require(reserved_directories(root).empty(),
            "resource-policy preflight leaked its probe cgroup");

    auto session = SessionCgroup::create(
        root, contained_identity(), limits);
    require(session.ok(), session.status().message());
    const auto leaves = reserved_directories(root);
    require(leaves.size() == 1U,
            "resource-policy session did not create exactly one leaf");
    require(read_record(leaves.front() / "pids.max") == "4\n",
            "pids.max did not retain the configured ceiling");
    require(read_record(leaves.front() / "memory.high") ==
                std::to_string(kMemoryHighBytes) + "\n",
            "memory.high did not retain the configured throttle");
    require(read_record(leaves.front() / "memory.max") ==
                std::to_string(kMemoryLimitBytes) + "\n",
            "memory.max did not retain the configured ceiling");
    require(read_record(leaves.front() / "memory.swap.max") == "0\n",
            "memory.swap.max did not retain the no-swap policy");
    require(read_record(leaves.front() / "memory.oom.group") == "1\n",
            "memory.oom.group did not retain whole-session OOM policy");

    std::array<int, 2U> command_pipe{};
    std::array<int, 2U> result_pipe{};
    require(::pipe2(command_pipe.data(), O_CLOEXEC) == 0,
            "unable to create pids-limit command pipe");
    require(::pipe2(result_pipe.data(), O_CLOEXEC) == 0,
            "unable to create pids-limit result pipe");
    const pid_t payload = ::fork();
    require(payload >= 0, "unable to fork pids-limit payload");
    if (payload == 0) {
        static_cast<void>(::close(command_pipe[1U]));
        static_cast<void>(::close(result_pipe[0U]));
        char command = 0;
        ssize_t received = -1;
        do {
            received = ::read(command_pipe[0U], &command, 1U);
        } while (received < 0 && errno == EINTR);
        if (received != 1 || command != 'F') ::_exit(121);

        ForkLimitMessage report;
        while (report.created < 16) {
            const pid_t descendant = ::fork();
            if (descendant < 0) {
                report.failure = errno;
                break;
            }
            if (descendant == 0) {
                static_cast<void>(::close(command_pipe[0U]));
                static_cast<void>(::close(result_pipe[1U]));
                while (true) ::pause();
            }
            ++report.created;
        }
        write_fork_limit_message(result_pipe[1U], report);
        while (true) ::pause();
    }

    static_cast<void>(::close(command_pipe[0U]));
    static_cast<void>(::close(result_pipe[1U]));
    const iotox::Status attached = session.value().attach(payload);
    require(attached.ok(), attached.message());
    require(::write(command_pipe[1U], "F", 1U) == 1,
            "unable to release pids-limit payload");
    static_cast<void>(::close(command_pipe[1U]));
    const ForkLimitMessage report =
        read_fork_limit_message(result_pipe[0U]);
    require(::close(result_pipe[0U]) == 0,
            "unable to close pids-limit result pipe");
    require(report.created == 3,
            "pids.max did not cap the payload plus descendants at four tasks");
    require(report.failure == EAGAIN,
            "pids.max exhaustion did not surface as EAGAIN");
    require(read_flat_counter(
                local_or_hierarchical_events(
                    leaves.front(), "pids.events.local", "pids.events"),
                "max") > 0U,
            "pids.events did not record the rejected process creation");

    const iotox::Status killed = session.value().kill_all();
    require(killed.ok(), killed.message());
    int payload_status = 0;
    require(::waitpid(payload, &payload_status, 0) == payload,
            "unable to reap pids-limit payload");
    require(WIFSIGNALED(payload_status) && WTERMSIG(payload_status) == SIGKILL,
            "cgroup.kill did not terminate the pids-limit payload");
    wait_for_empty_cgroup(leaves.front());
    const auto observed_pids_peak = read_optional_peak(
        leaves.front(), "pids.peak");
    const auto observed_memory_peak = read_optional_peak(
        leaves.front(), "memory.peak");
    const auto observed_swap_peak = read_optional_peak(
        leaves.front(), "memory.swap.peak");
    const iotox::Status removed = session.value().remove_if_empty();
    require(removed.ok(), removed.message());
    const auto outcome = session.value().take_outcome();
    require(outcome.has_value() && outcome->telemetry_complete,
            "pids-limit session did not retain complete kernel outcomes");
    require(outcome->pids_limit_hits > 0U,
            "teardown outcome lost the observed pids.max rejection");
    require(outcome->pids_peak == observed_pids_peak &&
                outcome->memory_peak_bytes == observed_memory_peak &&
                outcome->memory_swap_peak_bytes == observed_swap_peak,
            "teardown outcome did not retain exact pids/memory peaks");
    require(!outcome->pids_peak.has_value() || *outcome->pids_peak >= 4U,
            "pids.peak did not retain the four-task high-water mark");
    require(!session.value().take_outcome().has_value(),
            "session outcome was returned more than once");
    require(reserved_directories(root).empty(),
            "pids-limit session leaf survived cleanup");

    constexpr std::uint64_t kPressureHighBytes = 8U * 1024U * 1024U;
    constexpr std::uint64_t kPressureMaximumBytes = 64U * 1024U * 1024U;
    constexpr std::size_t kPressureAllocationBytes =
        32U * 1024U * 1024U;
    CgroupResourceLimits pressure_limits;
    pressure_limits.maximum_memory_high_bytes = kPressureHighBytes;
    pressure_limits.maximum_memory_bytes = kPressureMaximumBytes;
    pressure_limits.maximum_swap_bytes = 0U;
    const iotox::Status pressure_preflight = SessionCgroup::preflight(
        root, contained_identity(), pressure_limits);
    require(pressure_preflight.ok(), pressure_preflight.message());
    require(reserved_directories(root).empty(),
            "memory-pressure preflight leaked its probe cgroup");

    auto pressure_session = SessionCgroup::create(
        root, contained_identity(), pressure_limits);
    require(
        pressure_session.ok(), pressure_session.status().message());
    const auto pressure_leaves = reserved_directories(root);
    require(pressure_leaves.size() == 1U,
            "memory-pressure session did not create exactly one leaf");
    require(read_record(pressure_leaves.front() / "memory.high") ==
                std::to_string(kPressureHighBytes) + "\n",
            "memory-pressure session lost its configured high threshold");
    require(read_record(pressure_leaves.front() / "memory.max") ==
                std::to_string(kPressureMaximumBytes) + "\n",
            "memory-pressure session lost its configured hard ceiling");

    std::array<int, 2U> pressure_command{};
    require(::pipe2(pressure_command.data(), O_CLOEXEC) == 0,
            "unable to create memory-pressure command pipe");
    const pid_t pressure_payload = ::fork();
    require(pressure_payload >= 0, "unable to fork memory-pressure payload");
    if (pressure_payload == 0) {
        static_cast<void>(::close(pressure_command[1U]));
        char command = 0;
        ssize_t received = -1;
        do {
            received = ::read(pressure_command[0U], &command, 1U);
        } while (received < 0 && errno == EINTR);
        if (received != 1 || command != 'M') ::_exit(123);

        void *const allocation = ::mmap(
            nullptr, kPressureAllocationBytes, PROT_READ | PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        if (allocation == MAP_FAILED) ::_exit(124);
        auto *const bytes = static_cast<volatile std::uint8_t *>(allocation);
        const long page_size = ::sysconf(_SC_PAGESIZE);
        if (page_size <= 0) ::_exit(125);
        for (std::size_t offset = 0U;
             offset < kPressureAllocationBytes;
             offset += static_cast<std::size_t>(page_size)) {
            bytes[offset] = static_cast<std::uint8_t>(offset);
        }
        while (true) ::pause();
    }
    static_cast<void>(::close(pressure_command[0U]));
    const iotox::Status pressure_attached =
        pressure_session.value().attach(pressure_payload);
    require(pressure_attached.ok(), pressure_attached.message());
    require(::write(pressure_command[1U], "M", 1U) == 1,
            "unable to release memory-pressure payload");
    static_cast<void>(::close(pressure_command[1U]));

    const std::filesystem::path memory_events =
        local_or_hierarchical_events(
            pressure_leaves.front(), "memory.events.local",
            "memory.events");
    const auto pressure_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds{10};
    std::uint64_t high_events = 0U;
    while (std::chrono::steady_clock::now() < pressure_deadline) {
        high_events = read_flat_counter(memory_events, "high");
        if (high_events > 0U) break;
        int observed_status = 0;
        const pid_t observed =
            ::waitpid(pressure_payload, &observed_status, WNOHANG);
        require(observed == 0,
                "memory-pressure payload exited before memory.high fired");
        std::this_thread::sleep_for(std::chrono::milliseconds{20});
    }
    require(high_events > 0U,
            "memory.high did not report pressure above its threshold");

    const iotox::Status pressure_killed =
        pressure_session.value().kill_all();
    require(pressure_killed.ok(), pressure_killed.message());
    int pressure_status = 0;
    require(::waitpid(pressure_payload, &pressure_status, 0) ==
                pressure_payload,
            "unable to reap memory-pressure payload");
    require(WIFSIGNALED(pressure_status) &&
                WTERMSIG(pressure_status) == SIGKILL,
            "cgroup.kill did not terminate the memory-pressure payload");
    wait_for_empty_cgroup(pressure_leaves.front());
    const auto observed_memory_pressure = read_optional_pressure(
        pressure_leaves.front(), "memory.pressure");
    const auto observed_pressure_memory_peak = read_optional_peak(
        pressure_leaves.front(), "memory.peak");
    const auto observed_pressure_swap_peak = read_optional_peak(
        pressure_leaves.front(), "memory.swap.peak");
    const iotox::Status pressure_removed =
        pressure_session.value().remove_if_empty();
    require(pressure_removed.ok(), pressure_removed.message());
    const auto pressure_outcome = pressure_session.value().take_outcome();
    require(pressure_outcome.has_value() &&
                pressure_outcome->telemetry_complete,
            "memory-pressure session did not retain complete kernel outcomes");
    require(pressure_outcome->memory_high_events > 0U,
            "teardown outcome lost the observed memory.high pressure");
    require(pressure_outcome->memory_pressure == observed_memory_pressure,
            "teardown outcome did not retain exact memory PSI totals");
    require(pressure_outcome->memory_peak_bytes ==
                observed_pressure_memory_peak &&
                pressure_outcome->memory_swap_peak_bytes ==
                    observed_pressure_swap_peak,
            "teardown outcome did not retain exact memory peak totals");
    require(!pressure_outcome->memory_peak_bytes.has_value() ||
                *pressure_outcome->memory_peak_bytes > kPressureHighBytes,
            "memory.peak did not retain pressure above memory.high");
    require(!pressure_session.value().take_outcome().has_value(),
            "memory-pressure outcome was returned more than once");
    require(reserved_directories(root).empty(),
            "memory-pressure session leaf survived cleanup");
}

void qualify_cpu_resource_policy(const std::filesystem::path &root) {
    CgroupResourceLimits cpu_limits;
    cpu_limits.cpu_quota_microseconds = 5000U;
    cpu_limits.cpu_period_microseconds = 100000U;
    const iotox::Status preflight = SessionCgroup::preflight(
        root, contained_identity(), cpu_limits);
    require(preflight.ok(), preflight.message());
    require(reserved_directories(root).empty(),
            "CPU-policy preflight leaked its probe cgroup");

    auto cpu_session = SessionCgroup::create(
        root, contained_identity(), cpu_limits);
    require(cpu_session.ok(), cpu_session.status().message());
    const auto cpu_leaves = reserved_directories(root);
    require(cpu_leaves.size() == 1U,
            "CPU-policy session did not create exactly one leaf");
    require(read_record(cpu_leaves.front() / "cpu.max") ==
                "5000 100000\n",
            "cpu.max did not retain the configured quota and period");

    std::array<int, 2U> cpu_command{};
    require(::pipe2(cpu_command.data(), O_CLOEXEC) == 0,
            "unable to create CPU-policy command pipe");
    const pid_t busy = ::fork();
    require(busy >= 0, "unable to fork CPU-policy payload");
    if (busy == 0) {
        static_cast<void>(::close(cpu_command[1U]));
        char command = 0;
        ssize_t received = -1;
        do {
            received = ::read(cpu_command[0U], &command, 1U);
        } while (received < 0 && errno == EINTR);
        if (received != 1 || command != 'B') ::_exit(122);
        std::uint64_t accumulator = 1U;
        while (true) {
            accumulator = accumulator * 1664525U + 1013904223U;
            asm volatile("" : "+r"(accumulator));
        }
    }
    static_cast<void>(::close(cpu_command[0U]));
    const iotox::Status cpu_attached = cpu_session.value().attach(busy);
    require(cpu_attached.ok(), cpu_attached.message());
    require(::write(cpu_command[1U], "B", 1U) == 1,
            "unable to release CPU-policy payload");
    static_cast<void>(::close(cpu_command[1U]));

    const auto throttle_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds{3};
    std::uint64_t throttled = 0U;
    while (std::chrono::steady_clock::now() < throttle_deadline) {
        throttled = read_flat_counter(
            cpu_leaves.front() / "cpu.stat", "nr_throttled");
        if (throttled > 0U) break;
        std::this_thread::sleep_for(std::chrono::milliseconds{20});
    }
    require(throttled > 0U,
            "cpu.max did not throttle a continuously runnable payload");
    const iotox::Status cpu_killed = cpu_session.value().kill_all();
    require(cpu_killed.ok(), cpu_killed.message());
    int busy_status = 0;
    require(::waitpid(busy, &busy_status, 0) == busy,
            "unable to reap CPU-policy payload");
    require(WIFSIGNALED(busy_status) && WTERMSIG(busy_status) == SIGKILL,
            "cgroup.kill did not terminate the CPU-policy payload");
    wait_for_empty_cgroup(cpu_leaves.front());
    const auto observed_cpu_pressure = read_optional_pressure(
        cpu_leaves.front(), "cpu.pressure");
    const CgroupCpuStat observed_cpu_stat = read_cpu_stat(cpu_leaves.front());
    const iotox::Status cpu_removed = cpu_session.value().remove_if_empty();
    require(cpu_removed.ok(), cpu_removed.message());
    const auto cpu_outcome = cpu_session.value().take_outcome();
    require(cpu_outcome.has_value() && cpu_outcome->telemetry_complete,
            "CPU-policy session did not retain complete kernel outcomes");
    require(cpu_outcome->cpu_stat_observed,
            "teardown outcome lost cpu.stat capability evidence");
    require(cpu_outcome->cpu_usage_microseconds ==
                observed_cpu_stat.usage_microseconds &&
                cpu_outcome->cpu_user_microseconds ==
                    observed_cpu_stat.user_microseconds &&
                cpu_outcome->cpu_system_microseconds ==
                    observed_cpu_stat.system_microseconds,
            "teardown outcome did not retain exact CPU work accounting");
    require(cpu_outcome->cpu_usage_microseconds > 0U,
            "teardown outcome lost observed CPU usage");
    require(cpu_outcome->cpu_bandwidth_stat_observed &&
                observed_cpu_stat.bandwidth.has_value(),
            "teardown outcome lost CPU bandwidth capability evidence");
    require(cpu_outcome->cpu_periods > 0U,
            "teardown outcome lost observed CPU periods");
    require(cpu_outcome->cpu_throttled_periods > 0U,
            "teardown outcome lost the observed cpu.max throttling");
    require(cpu_outcome->cpu_throttled_microseconds > 0U,
            "teardown outcome lost throttled CPU duration");
    require(cpu_outcome->cpu_pressure == observed_cpu_pressure,
            "teardown outcome did not retain exact CPU PSI totals");
    require(reserved_directories(root).empty(),
            "CPU-policy session leaf survived cleanup");
}

void qualify_io_resource_policy(const std::filesystem::path &root) {
    constexpr std::size_t kProbeBytes = 2U * 1024U * 1024U;
    const std::filesystem::path probe_path = unique_io_path("probe");
    auto probe_session = SessionCgroup::create(
        root, contained_identity(), CgroupResourceLimits{});
    require(probe_session.ok(), probe_session.status().message());
    const auto probe_leaves = reserved_directories(root);
    require(probe_leaves.size() == 1U,
            "I/O discovery session did not create exactly one leaf");

    std::array<int, 2U> probe_command{};
    require(::pipe2(probe_command.data(), O_CLOEXEC) == 0,
            "unable to create I/O discovery command pipe");
    const pid_t probe_writer = fork_sync_writer(
        probe_path, probe_command, kProbeBytes);
    static_cast<void>(::close(probe_command[0U]));
    const iotox::Status probe_attached =
        probe_session.value().attach(probe_writer);
    require(probe_attached.ok(), probe_attached.message());
    release_writer(probe_command[1U]);
    require(::close(probe_command[1U]) == 0,
            "unable to close I/O discovery command pipe");
    int probe_status = 0;
    require(::waitpid(probe_writer, &probe_status, 0) == probe_writer,
            "unable to reap I/O discovery writer");
    require(WIFEXITED(probe_status) && WEXITSTATUS(probe_status) == 0,
            "I/O discovery writer failed");
    wait_for_empty_cgroup(probe_leaves.front());
    const std::string probe_record =
        read_record(probe_leaves.front() / "io.stat");
    const std::optional<CgroupIoDevice> device =
        written_io_device(probe_record);
    const iotox::Status probe_removed =
        probe_session.value().remove_if_empty();
    require(probe_removed.ok(), probe_removed.message());
    require(reserved_directories(root).empty(),
            "I/O discovery session leaf survived cleanup");
    require(::unlink(probe_path.c_str()) == 0,
            "unable to remove I/O discovery payload");
    if (!device.has_value()) {
        skip("the qualification filesystem did not expose cgroup-attributed block I/O");
    }

    CgroupResourceLimits limits;
    limits.io_device = *device;
    limits.maximum_io_read_bytes_per_second = 8U * 1024U * 1024U;
    limits.maximum_io_write_bytes_per_second = 8U * 1024U * 1024U;
    limits.maximum_io_read_operations_per_second = 2048U;
    limits.maximum_io_write_operations_per_second = 2048U;
    const iotox::Status preflight = SessionCgroup::preflight(
        root, contained_identity(), limits);
    require(preflight.ok(), preflight.message());
    require(reserved_directories(root).empty(),
            "I/O-policy preflight leaked its probe cgroup");

    auto session = SessionCgroup::create(
        root, contained_identity(), limits);
    require(session.ok(), session.status().message());
    const auto leaves = reserved_directories(root);
    require(leaves.size() == 1U,
            "I/O-policy session did not create exactly one leaf");
    auto observed_policy = parse_cgroup_io_max(
        read_record(leaves.front() / "io.max"));
    require(observed_policy.ok(), observed_policy.status().message());
    const std::vector<CgroupIoMax> expected_policy{
        CgroupIoMax{
            *device,
            limits.maximum_io_read_bytes_per_second,
            limits.maximum_io_write_bytes_per_second,
            limits.maximum_io_read_operations_per_second,
            limits.maximum_io_write_operations_per_second}};
    require(observed_policy.value() == expected_policy,
            "io.max did not retain the exact configured device ceilings");
    auto initial_stat = parse_cgroup_io_stat(
        read_record(leaves.front() / "io.stat"));
    require(initial_stat.ok(), initial_stat.status().message());
    require(initial_stat.value() == iotox::terminal::detail::CgroupIoStat{},
            "new I/O-policy leaf began with nonzero accounting");

    const std::filesystem::path payload_path = unique_io_path("policy");
    std::array<int, 2U> command{};
    require(::pipe2(command.data(), O_CLOEXEC) == 0,
            "unable to create I/O-policy command pipe");
    const pid_t writer = fork_sync_writer(
        payload_path, command, 1024U * 1024U);
    static_cast<void>(::close(command[0U]));
    const iotox::Status attached = session.value().attach(writer);
    require(attached.ok(), attached.message());
    release_writer(command[1U]);
    require(::close(command[1U]) == 0,
            "unable to close I/O-policy command pipe");
    int writer_status = 0;
    require(::waitpid(writer, &writer_status, 0) == writer,
            "unable to reap I/O-policy writer");
    require(WIFEXITED(writer_status) && WEXITSTATUS(writer_status) == 0,
            "I/O-policy writer failed");
    wait_for_empty_cgroup(leaves.front());
    const auto observed_io_pressure = read_optional_pressure(
        leaves.front(), "io.pressure");
    const iotox::Status removed = session.value().remove_if_empty();
    require(removed.ok(), removed.message());
    const auto outcome = session.value().take_outcome();
    require(outcome.has_value() && outcome->telemetry_complete,
            "I/O-policy session did not retain complete kernel outcomes");
    require(outcome->io_write_bytes > 0U,
            "teardown outcome lost observed write bytes");
    require(outcome->io_write_operations > 0U,
            "teardown outcome lost observed write operations");
    require(outcome->io_pressure == observed_io_pressure,
            "teardown outcome did not retain exact I/O PSI totals");
    require(!session.value().take_outcome().has_value(),
            "I/O-policy outcome was returned more than once");
    require(reserved_directories(root).empty(),
            "I/O-policy session leaf survived cleanup");
    require(::unlink(payload_path.c_str()) == 0,
            "unable to remove I/O-policy payload");
}

void qualify_inactive_controller_refusal(
    const std::filesystem::path &inactive_root) {
    CgroupResourceLimits limits;
    limits.maximum_processes = 2U;
    auto refused = SessionCgroup::create(
        inactive_root, contained_identity(), limits);
    require(!refused.ok(),
            "resource policy silently degraded under an inactive controller root");
    require(refused.status().code() == ErrorCode::unavailable,
            "inactive controller root returned the wrong error class");
    require(refused.status().message().find("not activated") !=
                std::string::npos,
            "inactive controller refusal omitted its activation reason");
    require(reserved_directories(inactive_root).empty(),
            "inactive controller refusal created a session leaf");
}

void qualify_pressure_admission_policy(const std::filesystem::path &root) {
    for (const std::string_view interface_name : {
             "cgroup.pressure", "cpu.pressure",
             "memory.pressure", "io.pressure"}) {
        if (!std::filesystem::exists(root / interface_name)) {
            skip("required per-cgroup PSI interface '" +
                 std::string(interface_name) + "' is unavailable");
        }
    }
    require(read_record(root / "cgroup.pressure") == "1\n",
            "pressure-admission oracle did not start with cgroup.pressure=1");

    {
        CgroupPressureAdmissionLimits trigger_limits;
        trigger_limits.maximum_memory_full_average_10_basis_points = 10000U;
        trigger_limits.hysteresis_basis_points = 0U;
        // A two-second window is accepted for both privileged and
        // unprivileged PSI monitors. Requiring a complete two seconds of full
        // memory stall makes a spontaneous trip during this registration and
        // lifecycle qualification extremely unlikely without weakening the
        // kernel ABI exercised by the test.
        trigger_limits.trigger_window_microseconds = 2000000U;
        trigger_limits.memory_full_trigger_stall_microseconds = 2000000U;

        auto trigger_admission =
            CgroupPressureAdmission::create(root, trigger_limits);
        if (!trigger_admission.ok() &&
            (trigger_admission.status().code() == ErrorCode::unsupported ||
             trigger_admission.status().code() == ErrorCode::unavailable)) {
            skip("per-cgroup PSI trigger registration is unavailable: " +
                 trigger_admission.status().message());
        }
        require(trigger_admission.ok(), trigger_admission.status().message());

        auto trigger_snapshot = trigger_admission.value()->snapshot();
        require(trigger_snapshot.limits == trigger_limits &&
                    trigger_snapshot.trigger_monitor_healthy &&
                    !trigger_snapshot.trigger_hold_active &&
                    trigger_snapshot.trigger_hold_remaining_microseconds == 0U &&
                    trigger_snapshot.trigger_monitor_error_code == ErrorCode::ok &&
                    trigger_snapshot.trigger_events == 0U &&
                    trigger_snapshot.trigger_monitor_failures == 0U,
                "PSI trigger registration did not expose a healthy quiet monitor");

        const iotox::Status trigger_check =
            trigger_admission.value()->admit();
        require(trigger_check.ok(), trigger_check.message());
        trigger_snapshot = trigger_admission.value()->snapshot();
        require(trigger_snapshot.checks == 1U &&
                    trigger_snapshot.admitted == 1U &&
                    trigger_snapshot.rejections == 0U &&
                    !trigger_snapshot.closed &&
                    trigger_snapshot.trigger_monitor_healthy &&
                    trigger_snapshot.trigger_events == 0U,
                "quiet PSI trigger monitor changed an accepted admission");
        // Scope exit must wake and join the indefinite poll before closing the
        // descriptor that owns the kernel trigger registration.
    }

    CgroupPressureAdmissionLimits limits;
    limits.maximum_cpu_some_average_10_basis_points = 10000U;
    limits.maximum_memory_full_average_10_basis_points = 10000U;
    limits.maximum_io_full_average_10_basis_points = 10000U;
    limits.hysteresis_basis_points = 0U;

    auto admission = CgroupPressureAdmission::create(root, limits);
    require(admission.ok(), admission.status().message());
    const iotox::Status first = admission.value()->admit();
    require(first.ok(), first.message());
    auto snapshot = admission.value()->snapshot();
    require(snapshot.checks == 1U && snapshot.admitted == 1U &&
                snapshot.rejections == 0U && !snapshot.closed &&
                snapshot.last_sample_valid &&
                snapshot.last_sampling_error_code == ErrorCode::ok,
            "pressure admission did not account its initial accepted sample");
    require(snapshot.last_observation.cpu_some_average_10_basis_points.has_value() &&
                snapshot.last_observation.memory_full_average_10_basis_points.has_value() &&
                snapshot.last_observation.io_full_average_10_basis_points.has_value(),
            "pressure admission omitted a configured kernel observation");

    write_record(root / "cgroup.pressure", "0\n");
    const iotox::Status disabled = admission.value()->admit();
    require(!disabled.ok() && disabled.code() == ErrorCode::unavailable,
            "disabled PSI accounting did not fail pressure admission closed");
    snapshot = admission.value()->snapshot();
    require(snapshot.closed && snapshot.checks == 2U &&
                snapshot.admitted == 1U && snapshot.rejections == 1U &&
                snapshot.sampling_failures == 1U &&
                snapshot.closed_transitions == 1U &&
                snapshot.reopened_transitions == 0U &&
                !snapshot.last_sample_valid &&
                snapshot.last_sampling_error_code == ErrorCode::unavailable,
            "pressure admission did not latch and account the disabled sample");

    const iotox::Status disabled_again = admission.value()->admit();
    require(!disabled_again.ok() &&
                disabled_again.code() == ErrorCode::unavailable,
            "latched pressure admission accepted while PSI remained disabled");
    snapshot = admission.value()->snapshot();
    require(snapshot.closed && snapshot.checks == 3U &&
                snapshot.rejections == 2U &&
                snapshot.sampling_failures == 2U &&
                snapshot.closed_transitions == 1U &&
                !snapshot.last_sample_valid &&
                snapshot.last_sampling_error_code == ErrorCode::unavailable,
            "repeated sampling failure changed the close transition count");

    write_record(root / "cgroup.pressure", "1\n");
    const iotox::Status recovered = admission.value()->admit();
    require(recovered.ok(), recovered.message());
    snapshot = admission.value()->snapshot();
    require(!snapshot.closed && snapshot.checks == 4U &&
                snapshot.admitted == 2U && snapshot.rejections == 2U &&
                snapshot.sampling_failures == 2U &&
                snapshot.closed_transitions == 1U &&
                snapshot.reopened_transitions == 1U &&
                snapshot.last_sample_valid &&
                snapshot.last_sampling_error_code == ErrorCode::ok,
            "valid low-pressure sample did not reopen the latched gate exactly once");

    constexpr unsigned int kThreadCount = 8U;
    constexpr unsigned int kChecksPerThread = 32U;
    std::atomic_uint concurrent_failures{0U};
    std::vector<std::thread> threads;
    threads.reserve(kThreadCount);
    for (unsigned int thread = 0U; thread < kThreadCount; ++thread) {
        threads.emplace_back([&] {
            for (unsigned int check = 0U; check < kChecksPerThread; ++check) {
                if (!admission.value()->admit().ok()) {
                    concurrent_failures.fetch_add(1U, std::memory_order_relaxed);
                }
            }
        });
    }
    for (std::thread &thread : threads) thread.join();
    require(concurrent_failures.load(std::memory_order_relaxed) == 0U,
            "concurrent valid PSI admissions unexpectedly failed");
    snapshot = admission.value()->snapshot();
    constexpr std::uint64_t kConcurrentChecks =
        static_cast<std::uint64_t>(kThreadCount) * kChecksPerThread;
    require(snapshot.checks == 4U + kConcurrentChecks &&
                snapshot.admitted == 2U + kConcurrentChecks &&
                snapshot.rejections == 2U && !snapshot.closed &&
                snapshot.last_sample_valid &&
                snapshot.last_sampling_error_code == ErrorCode::ok,
            "concurrent PSI admissions did not retain exact serialized accounting");

    write_record(root / "cgroup.pressure", "0\n");
    require(read_record(root / "cgroup.pressure") == "0\n",
            "pressure-admission oracle could not disable cgroup.pressure");
    auto refused_start = CgroupPressureAdmission::create(root, limits);
    require(!refused_start.ok(),
            "startup preflight accepted disabled PSI accounting");
    require(refused_start.status().code() == ErrorCode::unavailable ||
                refused_start.status().code() == ErrorCode::unsupported,
            "startup preflight returned the wrong disabled-PSI error class");
    write_record(root / "cgroup.pressure", "1\n");
}

void qualify_malformed_and_bounded_scans(const std::filesystem::path &root) {
    const std::filesystem::path malformed = root / "_iotox_session_broken";
    require(std::filesystem::create_directory(malformed),
            "unable to create malformed reserved cgroup");
    auto malformed_report = SessionCgroup::recover_orphans(root);
    require(!malformed_report.ok() &&
                malformed_report.status().code() == ErrorCode::invalid_argument,
            "malformed reserved name did not fail closed");
    require(std::filesystem::exists(malformed),
            "malformed reserved name was modified before validation");
    remove_empty_cgroup(malformed);

    const std::array<std::filesystem::path, 3U> bounded{
        root / "_iotox_session_700001_1",
        root / "_iotox_session_700002_1",
        root / "_iotox_session_700003_1"};
    for (const auto &path : bounded) {
        require(std::filesystem::create_directory(path),
                "unable to create bounded-scan cgroup");
    }
    CgroupRecoveryConfig config;
    config.maximum_candidates = 2U;
    auto bounded_report = SessionCgroup::recover_orphans(root, config);
    require(!bounded_report.ok() &&
                bounded_report.status().code() == ErrorCode::resource_exhausted,
            "reserved-name scan did not enforce its candidate bound");
    for (const auto &path : bounded) {
        require(std::filesystem::exists(path),
                "bounded preflight modified a candidate before refusal");
        remove_empty_cgroup(path);
    }
}

int worker(OracleMode mode) {
    try {
        MountedCgroup2 cgroup(mode);
        if (mode == OracleMode::lifecycle) {
            qualify_unlimited_cpu_accounting(cgroup.root());
            qualify_live_incarnation(cgroup.root());
            qualify_empty_legacy(cgroup.root());
            qualify_stale_incarnation(cgroup.root());
            qualify_populated_legacy_refusal(cgroup.root());
            qualify_malformed_and_bounded_scans(cgroup.root());
            std::cout << "PASS boot-bound cgroup orphan recovery process oracle\n";
        } else if (mode == OracleMode::memory_resources) {
            qualify_memory_and_pids_resource_policy(cgroup.root());
            qualify_inactive_controller_refusal(cgroup.inactive_root());
            std::cout << "PASS memory/pids cgroup resource process oracle\n";
        } else if (mode == OracleMode::cpu_resources) {
            qualify_cpu_resource_policy(cgroup.root());
            std::cout << "PASS CPU cgroup resource process oracle\n";
        } else if (mode == OracleMode::io_resources) {
            qualify_io_resource_policy(cgroup.root());
            std::cout << "PASS I/O cgroup resource process oracle\n";
        } else {
            qualify_pressure_admission_policy(cgroup.root());
            std::cout << "PASS cgroup PSI pressure-admission process oracle\n";
        }
        return 0;
    } catch (const SkipQualification &exception) {
        std::string_view label = "CPU cgroup resource oracle";
        if (mode == OracleMode::lifecycle) {
            label = "cgroup lifecycle/recovery oracle";
        } else if (mode == OracleMode::memory_resources) {
            label = "memory/pids cgroup resource oracle";
        } else if (mode == OracleMode::io_resources) {
            label = "I/O cgroup resource oracle";
        } else if (mode == OracleMode::pressure_admission) {
            label = "cgroup PSI pressure-admission oracle";
        }
        std::cout << "SKIP " << label << ": "
                  << exception.what() << '\n';
        return 77;
    } catch (const std::exception &exception) {
        std::cerr << "FAIL cgroup recovery process oracle: "
                  << exception.what() << '\n';
        return 1;
    }
}

[[nodiscard]] int run_unshare(
    const std::filesystem::path &executable, OracleMode mode,
    bool worker_mode) {
    if (worker_mode) {
        const char *worker_argument = "--cpu-resource-worker";
        if (mode == OracleMode::lifecycle) {
            worker_argument = "--lifecycle-worker";
        } else if (mode == OracleMode::memory_resources) {
            worker_argument = "--memory-resource-worker";
        } else if (mode == OracleMode::io_resources) {
            worker_argument = "--io-resource-worker";
        } else if (mode == OracleMode::pressure_admission) {
            worker_argument = "--pressure-admission-worker";
        }
        ::execlp(
            "unshare", "unshare", "-UrCm", "--", executable.c_str(),
            worker_argument, nullptr);
        return 127;
    }

    const pid_t child = ::fork();
    if (child < 0) return 126;
    if (child == 0) {
        ::execlp(
            "unshare", "unshare", "-UrCm", "--", "true", nullptr);
        ::_exit(127);
    }
    int status = 0;
    if (::waitpid(child, &status, 0) != child) return 126;
    if (WIFEXITED(status)) return WEXITSTATUS(status);
    if (WIFSIGNALED(status)) return 128 + WTERMSIG(status);
    return 126;
}

}  // namespace

int main(int argc, char **argv) {
    if (argc == 2 && std::string_view{argv[1]} == "--lifecycle-worker") {
        return worker(OracleMode::lifecycle);
    }
    if (argc == 2 &&
        std::string_view{argv[1]} == "--memory-resource-worker") {
        return worker(OracleMode::memory_resources);
    }
    if (argc == 2 &&
        std::string_view{argv[1]} == "--cpu-resource-worker") {
        return worker(OracleMode::cpu_resources);
    }
    if (argc == 2 &&
        std::string_view{argv[1]} == "--io-resource-worker") {
        return worker(OracleMode::io_resources);
    }
    if (argc == 2 &&
        std::string_view{argv[1]} == "--pressure-admission-worker") {
        return worker(OracleMode::pressure_admission);
    }
    if (argc != 2) {
        std::cerr << "usage: " << argv[0]
                  << " <--lifecycle|--memory-resource|--cpu-resource|--io-resource|--pressure-admission>\n";
        return 2;
    }

    OracleMode mode = OracleMode::lifecycle;
    if (std::string_view{argv[1]} == "--lifecycle") {
        mode = OracleMode::lifecycle;
    } else if (std::string_view{argv[1]} == "--memory-resource") {
        mode = OracleMode::memory_resources;
    } else if (std::string_view{argv[1]} == "--cpu-resource") {
        mode = OracleMode::cpu_resources;
    } else if (std::string_view{argv[1]} == "--io-resource") {
        mode = OracleMode::io_resources;
    } else if (std::string_view{argv[1]} == "--pressure-admission") {
        mode = OracleMode::pressure_admission;
    } else {
        std::cerr << "usage: " << argv[0]
                  << " <--lifecycle|--memory-resource|--cpu-resource|--io-resource|--pressure-admission>\n";
        return 2;
    }

    const std::filesystem::path executable =
        std::filesystem::absolute(argv[0]);
    const int preflight = run_unshare(executable, mode, false);
    if (preflight != 0) {
        std::cout << "SKIP user/mount/cgroup namespaces unavailable\n";
        return 77;
    }
    return run_unshare(executable, mode, true);
}
