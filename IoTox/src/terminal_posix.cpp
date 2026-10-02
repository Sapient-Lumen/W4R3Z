#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "iotox/terminal_posix.hpp"
#include "iotox/terminal_cgroup.hpp"
#include "iotox/terminal_seccomp_policy.hpp"
#include "toxsync/hash.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <charconv>
#include <chrono>
#include <climits>
#include <csignal>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <dirent.h>
#include <filesystem>
#include <fcntl.h>
#include <grp.h>
#include <linux/audit.h>
#include <linux/capability.h>
#include <linux/filter.h>
#include <linux/magic.h>
#include <linux/sched.h>
#if __has_include(<linux/landlock.h>)
#include <linux/landlock.h>
#define IOTOX_HAS_LINUX_LANDLOCK_HEADER 1
#endif
#include <linux/seccomp.h>
#include <linux/securebits.h>
#include <limits>
#include <memory>
#include <optional>
#include <poll.h>
#include <spawn.h>
#include <span>
#include <string>
#include <string_view>
#include <thread>
#include <sys/ioctl.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <sys/vfs.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::terminal {
namespace {

constexpr int kConfigurationDescriptor = 3;
constexpr int kStatusDescriptor = 4;
constexpr int kExecutableDescriptor = 5;
constexpr int kWorkingDirectoryDescriptor = 6;
constexpr int kFirstUnreservedDescriptor = 7;
constexpr int kFirstSpawnSourceDescriptor = 16;
constexpr unsigned int kRequiredQuiescentSessionSweeps = 3U;
// Linux UAPI assigns waitid idtype value 3 to pidfds. Keep the typed
// constant local so builds do not require libc headers new enough to name
// P_PIDFD; EINVAL/ENOSYS falls back to direct-child waiting.
constexpr idtype_t kLinuxPidfdWaitIdType = static_cast<idtype_t>(3);
constexpr std::size_t kMaximumManifestBytes = 128U * 1024U;
constexpr std::array<std::uint8_t, 8U> kManifestMagic{
    static_cast<std::uint8_t>('I'), static_cast<std::uint8_t>('O'),
    static_cast<std::uint8_t>('T'), static_cast<std::uint8_t>('X'),
    static_cast<std::uint8_t>('P'), static_cast<std::uint8_t>('T'),
    static_cast<std::uint8_t>('Y'), static_cast<std::uint8_t>('1')};
constexpr std::array<std::uint8_t, 8U> kChildReadyRecord{
    static_cast<std::uint8_t>('I'), static_cast<std::uint8_t>('P'),
    static_cast<std::uint8_t>('R'), static_cast<std::uint8_t>('1'),
    1U, 0U, 0U, 0U};
constexpr std::array<std::uint8_t, 4U> kChildErrorMagic{
    static_cast<std::uint8_t>('I'), static_cast<std::uint8_t>('P'),
    static_cast<std::uint8_t>('E'), static_cast<std::uint8_t>('1')};
constexpr std::size_t kChildErrorBytes = 12U;

enum class ChildStage : std::uint32_t {
    marker = 1U,
    status_descriptor = 2U,
    parent_death = 3U,
    manifest_read = 4U,
    manifest_decode = 5U,
    session = 6U,
    controlling_terminal = 7U,
    window = 8U,
    foreground_group = 9U,
    executable = 10U,
    working_directory = 11U,
    resource_limits = 12U,
    identity = 13U,
    no_new_privileges = 14U,
    descriptor_hygiene = 15U,
    final_exec = 16U,
    internal_exception = 17U,
    descriptor_contract = 18U,
    ambient_capabilities = 19U,
    dumpable_guard = 20U,
    securebits = 21U,
    capability_bounding_set = 22U,
    active_capabilities = 23U,
    mdwe = 24U,
    landlock = 25U,
    seccomp = 26U,
};

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

class DirectoryStream {
  public:
    DirectoryStream() = default;
    explicit DirectoryStream(DIR *directory) : directory_(directory) {}
    ~DirectoryStream() { reset(); }

    DirectoryStream(const DirectoryStream &) = delete;
    DirectoryStream &operator=(const DirectoryStream &) = delete;
    DirectoryStream(DirectoryStream &&other) noexcept
        : directory_(std::exchange(other.directory_, nullptr)) {}
    DirectoryStream &operator=(DirectoryStream &&other) noexcept {
        if (this != &other) {
            reset();
            directory_ = std::exchange(other.directory_, nullptr);
        }
        return *this;
    }

    [[nodiscard]] DIR *get() const noexcept { return directory_; }
    void reset(DIR *directory = nullptr) noexcept {
        if (directory_ != nullptr) {
            static_cast<void>(::closedir(directory_));
        }
        directory_ = directory;
    }

  private:
    DIR *directory_{nullptr};
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

class SpawnAttributes {
  public:
    SpawnAttributes() : error_(::posix_spawnattr_init(&attributes_)) {}
    ~SpawnAttributes() {
        if (error_ == 0) {
            static_cast<void>(::posix_spawnattr_destroy(&attributes_));
        }
    }
    SpawnAttributes(const SpawnAttributes &) = delete;
    SpawnAttributes &operator=(const SpawnAttributes &) = delete;

    [[nodiscard]] int error() const noexcept { return error_; }
    [[nodiscard]] posix_spawnattr_t *get() noexcept { return &attributes_; }

  private:
    posix_spawnattr_t attributes_{};
    int error_{0};
};

[[nodiscard]] Status errno_status(
    ErrorCode code, std::string_view operation, int error_number = errno) {
    return Status{
        code,
        std::string(operation) + ": " + std::strerror(error_number)};
}

[[nodiscard]] Status spawn_error(
    std::string_view operation, int error_number) {
    return errno_status(ErrorCode::io_error, operation, error_number);
}

[[nodiscard]] Status validate_startup_timeout(std::chrono::milliseconds timeout) {
    if (timeout.count() <= 0 || timeout > std::chrono::seconds{30}) {
        return Status{ErrorCode::invalid_argument,
                      "PTY startup timeout must be in (0, 30s]"};
    }
    return Status::success();
}

[[nodiscard]] Result<FileDescriptor> duplicate_spawn_source(int descriptor) {
    const int duplicate =
        ::fcntl(descriptor, F_DUPFD_CLOEXEC, kFirstSpawnSourceDescriptor);
    if (duplicate < 0) {
        return errno_status(ErrorCode::io_error, "duplicate PTY spawn descriptor");
    }
    return FileDescriptor{duplicate};
}

[[nodiscard]] Result<FileDescriptor> open_absolute_without_symlinks(
    const std::filesystem::path &path, int final_flags, mode_t final_type) {
    if (!path.is_absolute() || path.empty() ||
        path.lexically_normal() != path || path == "/") {
        return Status{ErrorCode::invalid_argument,
                      "PTY path must be a non-root normalized absolute path"};
    }
    FileDescriptor current(
        ::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (current.get() < 0) {
        return errno_status(ErrorCode::io_error, "open PTY path root");
    }
    std::vector<std::string> components;
    for (const auto &component : path.relative_path()) {
        const std::string text = component.string();
        if (text.empty() || text == "." || text == ".." ||
            text.find('/') != std::string::npos || text.find('\0') != std::string::npos) {
            return Status{ErrorCode::invalid_argument,
                          "PTY path contains an invalid component"};
        }
        components.push_back(text);
    }
    if (components.empty()) {
        return Status{ErrorCode::invalid_argument, "PTY path has no final component"};
    }
    for (std::size_t index = 0U; index + 1U < components.size(); ++index) {
        FileDescriptor next(::openat(
            current.get(), components[index].c_str(),
            O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
        if (next.get() < 0) {
            return errno_status(ErrorCode::io_error,
                                "open PTY path directory component");
        }
        current = std::move(next);
    }
    FileDescriptor result(::openat(
        current.get(), components.back().c_str(),
        final_flags | O_CLOEXEC | O_NOFOLLOW));
    if (result.get() < 0) {
        return errno_status(ErrorCode::io_error, "open PTY path final component");
    }
    struct stat metadata {};
    if (::fstat(result.get(), &metadata) != 0) {
        return errno_status(ErrorCode::io_error, "fstat PTY path final component");
    }
    if ((metadata.st_mode & S_IFMT) != final_type) {
        return Status{ErrorCode::invalid_argument,
                      "PTY path final component has the wrong file type"};
    }
    return result;
}

[[nodiscard]] Status validate_executable_descriptor(
    int descriptor, std::string_view label,
    std::optional<uid_t> profile_owner = std::nullopt) {
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        return errno_status(ErrorCode::io_error, "fstat PTY executable");
    }
    if (!S_ISREG(metadata.st_mode) ||
        (metadata.st_mode & static_cast<mode_t>(0111)) == 0 ||
        (metadata.st_mode & static_cast<mode_t>(0022)) != 0 ||
        (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID)) != 0) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) +
                          " must be executable, non-writable by group/other, and non-privileged"};
    }
    const uid_t effective_uid = ::geteuid();
    if (metadata.st_uid != static_cast<uid_t>(0) &&
        metadata.st_uid != effective_uid &&
        (!profile_owner.has_value() || metadata.st_uid != *profile_owner)) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) +
                          " must be owned by root, the daemon uid, or the frozen account uid"};
    }
    std::array<std::uint8_t, 4U> magic{};
    const ssize_t count = ::pread(descriptor, magic.data(), magic.size(), 0);
    if (count != static_cast<ssize_t>(magic.size())) {
        return count < 0
                   ? errno_status(ErrorCode::io_error, "read PTY executable header")
                   : Status{ErrorCode::invalid_argument,
                            std::string(label) + " has a truncated executable header"};
    }
    constexpr std::array<std::uint8_t, 4U> elf{
        0x7fU, static_cast<std::uint8_t>('E'), static_cast<std::uint8_t>('L'),
        static_cast<std::uint8_t>('F')};
    if (magic != elf) {
        return Status{ErrorCode::unsupported,
                      std::string(label) + " is not a regular ELF executable"};
    }
    return Status::success();
}

[[nodiscard]] Result<FileDescriptor> open_secure_executable(
    const std::filesystem::path &path, std::string_view label,
    std::optional<uid_t> profile_owner = std::nullopt) {
    auto opened = open_absolute_without_symlinks(
        path, O_RDONLY | O_NONBLOCK, S_IFREG);
    if (!opened.ok()) return opened.status();
    const Status valid = validate_executable_descriptor(
        opened.value().get(), label, profile_owner);
    if (!valid.ok()) return valid;
    return std::move(opened.value());
}

[[nodiscard]] Result<ExecutableDigest> hash_executable_descriptor(
    int descriptor, std::string_view label) {
    struct stat before {};
    if (::fstat(descriptor, &before) != 0) {
        return errno_status(
            ErrorCode::io_error,
            "inspect " + std::string(label) + " before SHA-256");
    }
    if (!S_ISREG(before.st_mode) || before.st_size < 0) {
        return Status{ErrorCode::invalid_argument,
                      std::string(label) + " is not a finite regular file"};
    }
    toxsync::Sha256 hasher;
    std::array<std::byte, 64U * 1024U> buffer{};
    off_t offset = 0;
    while (offset < before.st_size) {
        const off_t remaining = before.st_size - offset;
        const std::size_t requested = std::min<std::size_t>(
            buffer.size(), static_cast<std::size_t>(remaining));
        const ssize_t count = ::pread(
            descriptor, buffer.data(), requested, offset);
        if (count < 0) {
            if (errno == EINTR) continue;
            return errno_status(
                ErrorCode::io_error,
                "hash " + std::string(label) + " with SHA-256");
        }
        if (count == 0) {
            return Status{
                ErrorCode::protocol_error,
                std::string(label) + " changed while SHA-256 was computed"};
        }
        hasher.update(std::span<const std::byte>(
            buffer.data(), static_cast<std::size_t>(count)));
        offset += static_cast<off_t>(count);
    }
    struct stat after {};
    if (::fstat(descriptor, &after) != 0) {
        return errno_status(
            ErrorCode::io_error,
            "inspect " + std::string(label) + " after SHA-256");
    }
    if (before.st_dev != after.st_dev || before.st_ino != after.st_ino ||
        before.st_mode != after.st_mode || before.st_nlink != after.st_nlink ||
        before.st_uid != after.st_uid || before.st_gid != after.st_gid ||
        before.st_size != after.st_size ||
        before.st_mtim.tv_sec != after.st_mtim.tv_sec ||
        before.st_mtim.tv_nsec != after.st_mtim.tv_nsec ||
        before.st_ctim.tv_sec != after.st_ctim.tv_sec ||
        before.st_ctim.tv_nsec != after.st_ctim.tv_nsec) {
        return Status{
            ErrorCode::protocol_error,
            std::string(label) + " changed while SHA-256 was computed"};
    }
    const toxsync::Digest256 source = hasher.finish();
    ExecutableDigest digest{};
    for (std::size_t index = 0U; index < digest.size(); ++index) {
        digest[index] = std::to_integer<std::uint8_t>(source.bytes[index]);
    }
    return digest;
}

[[nodiscard]] Status verify_executable_digest(
    int descriptor, const ExecutableDigest &expected,
    std::string_view label) {
    auto observed = hash_executable_descriptor(descriptor, label);
    if (!observed.ok()) return observed.status();
    if (observed.value() != expected) {
        return Status{
            ErrorCode::protocol_error,
            std::string(label) + " does not match the profile SHA-256 pin"};
    }
    return Status::success();
}

[[nodiscard]] Result<FileDescriptor> open_secure_working_directory(
    const std::filesystem::path &path) {
    if (path == "/") {
        FileDescriptor root(
            ::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
        if (root.get() < 0) {
            return errno_status(ErrorCode::io_error, "open PTY working directory root");
        }
        return root;
    }
    return open_absolute_without_symlinks(
        path, O_RDONLY | O_DIRECTORY, S_IFDIR);
}

void append_u16(std::vector<std::uint8_t> &bytes, std::uint16_t value) {
    bytes.push_back(static_cast<std::uint8_t>(value & 0xffU));
    bytes.push_back(static_cast<std::uint8_t>((value >> 8U) & 0xffU));
}

void append_u32(std::vector<std::uint8_t> &bytes, std::uint32_t value) {
    for (unsigned shift = 0U; shift < 32U; shift += 8U) {
        bytes.push_back(static_cast<std::uint8_t>((value >> shift) & 0xffU));
    }
}

void append_u64(std::vector<std::uint8_t> &bytes, std::uint64_t value) {
    for (unsigned shift = 0U; shift < 64U; shift += 8U) {
        bytes.push_back(static_cast<std::uint8_t>((value >> shift) & 0xffU));
    }
}

class ManifestReader {
  public:
    explicit ManifestReader(std::span<const std::uint8_t> bytes) : bytes_(bytes) {}

    [[nodiscard]] Result<std::span<const std::uint8_t>> take(std::size_t count) {
        if (count > bytes_.size() - offset_) {
            return Status{ErrorCode::protocol_error, "PTY manifest is truncated"};
        }
        const auto result = bytes_.subspan(offset_, count);
        offset_ += count;
        return result;
    }

    [[nodiscard]] Result<std::uint16_t> u16() {
        auto bytes = take(2U);
        if (!bytes.ok()) return bytes.status();
        return static_cast<std::uint16_t>(bytes.value()[0U]) |
               static_cast<std::uint16_t>(
                   static_cast<std::uint16_t>(bytes.value()[1U]) << 8U);
    }

    [[nodiscard]] Result<std::uint32_t> u32() {
        auto bytes = take(4U);
        if (!bytes.ok()) return bytes.status();
        std::uint32_t value = 0U;
        for (unsigned index = 0U; index < 4U; ++index) {
            value |= static_cast<std::uint32_t>(bytes.value()[index]) << (index * 8U);
        }
        return value;
    }

    [[nodiscard]] Result<std::uint64_t> u64() {
        auto bytes = take(8U);
        if (!bytes.ok()) return bytes.status();
        std::uint64_t value = 0U;
        for (unsigned index = 0U; index < 8U; ++index) {
            value |= static_cast<std::uint64_t>(bytes.value()[index]) << (index * 8U);
        }
        return value;
    }

    [[nodiscard]] bool exhausted() const noexcept { return offset_ == bytes_.size(); }

  private:
    std::span<const std::uint8_t> bytes_;
    std::size_t offset_{0U};
};

[[nodiscard]] Result<std::vector<std::uint8_t>> encode_manifest(
    const ResolvedProfile &resolved) {
    const Status valid = validate_resolved_profile(resolved);
    if (!valid.ok()) return valid;
    auto profile = encode_profile_record(resolved.profile);
    if (!profile.ok()) return profile.status();
    if (profile.value().size() > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "PTY profile record cannot fit the manifest"};
    }
    std::vector<std::uint8_t> bytes;
    bytes.reserve(profile.value().size() + kMaximumResolvedEnvironmentBytes + 64U);
    bytes.insert(bytes.end(), kManifestMagic.begin(), kManifestMagic.end());
    append_u32(bytes, static_cast<std::uint32_t>(profile.value().size()));
    bytes.insert(bytes.end(), profile.value().begin(), profile.value().end());
    append_u16(bytes, resolved.accepted_dimensions.columns);
    append_u16(bytes, resolved.accepted_dimensions.rows);
    append_u64(bytes, resolved.policy_generation);
    append_u16(bytes, static_cast<std::uint16_t>(resolved.environment.size()));
    for (const EnvironmentEntry &entry : resolved.environment) {
        append_u16(bytes, static_cast<std::uint16_t>(entry.name.size()));
        append_u32(bytes, static_cast<std::uint32_t>(entry.value.size()));
        bytes.insert(bytes.end(), entry.name.begin(), entry.name.end());
        bytes.insert(bytes.end(), entry.value.begin(), entry.value.end());
    }
    if (bytes.size() > kMaximumManifestBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "PTY manifest exceeds the local handoff byte bound"};
    }
    return bytes;
}

[[nodiscard]] Result<ResolvedProfile> decode_manifest(
    std::span<const std::uint8_t> bytes) {
    if (bytes.empty() || bytes.size() > kMaximumManifestBytes) {
        return Status{ErrorCode::protocol_error,
                      "PTY manifest size is outside the local handoff bound"};
    }
    ManifestReader reader(bytes);
    auto magic = reader.take(kManifestMagic.size());
    if (!magic.ok() || !std::equal(
            magic.value().begin(), magic.value().end(), kManifestMagic.begin())) {
        return Status{ErrorCode::protocol_error, "PTY manifest header is invalid"};
    }
    auto profile_size = reader.u32();
    if (!profile_size.ok() || profile_size.value() > kMaximumProfileFileBytes) {
        return Status{ErrorCode::protocol_error, "PTY manifest profile size is invalid"};
    }
    auto profile_bytes = reader.take(profile_size.value());
    if (!profile_bytes.ok()) return profile_bytes.status();
    auto profile = decode_profile_record(profile_bytes.value());
    if (!profile.ok()) return profile.status();
    auto columns = reader.u16();
    if (!columns.ok()) return columns.status();
    auto rows = reader.u16();
    if (!rows.ok()) return rows.status();
    auto generation = reader.u64();
    if (!generation.ok()) return generation.status();
    auto environment_count = reader.u16();
    if (!environment_count.ok() ||
        environment_count.value() > kMaximumEnvironmentEntries) {
        return Status{ErrorCode::protocol_error,
                      "PTY manifest environment count is invalid"};
    }
    ResolvedProfile resolved;
    resolved.profile = std::move(profile.value());
    resolved.accepted_dimensions = Dimensions{columns.value(), rows.value()};
    resolved.policy_generation = generation.value();
    resolved.environment.reserve(environment_count.value());
    for (std::uint16_t index = 0U; index < environment_count.value(); ++index) {
        auto name_size = reader.u16();
        if (!name_size.ok() || name_size.value() == 0U ||
            name_size.value() > 64U) {
            return Status{ErrorCode::protocol_error,
                          "PTY manifest environment name size is invalid"};
        }
        auto value_size = reader.u32();
        if (!value_size.ok() || value_size.value() > kMaximumEnvironmentValueBytes) {
            return Status{ErrorCode::protocol_error,
                          "PTY manifest environment value size is invalid"};
        }
        auto name = reader.take(name_size.value());
        if (!name.ok()) return name.status();
        auto value = reader.take(value_size.value());
        if (!value.ok()) return value.status();
        resolved.environment.push_back(EnvironmentEntry{
            std::string(
                reinterpret_cast<const char *>(name.value().data()),
                name.value().size()),
            std::string(
                reinterpret_cast<const char *>(value.value().data()),
                value.value().size())});
    }
    if (!reader.exhausted()) {
        return Status{ErrorCode::protocol_error, "PTY manifest has trailing bytes"};
    }
    const Status valid = validate_resolved_profile(resolved);
    if (!valid.ok()) return valid;
    auto canonical = encode_manifest(resolved);
    if (!canonical.ok() || canonical.value().size() != bytes.size() ||
        !std::equal(canonical.value().begin(), canonical.value().end(), bytes.begin())) {
        return Status{ErrorCode::protocol_error, "PTY manifest is not canonical"};
    }
    return resolved;
}

[[nodiscard]] bool child_send_status(
    std::span<const std::uint8_t> record) noexcept {
    std::size_t offset = 0U;
    while (offset < record.size()) {
        const ssize_t count = ::send(
            kStatusDescriptor, record.data() + offset,
            record.size() - offset, MSG_NOSIGNAL);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        return false;
    }
    return true;
}

[[noreturn]] void child_fail(ChildStage stage, int error_number) noexcept {
    std::array<std::uint8_t, kChildErrorBytes> record{};
    std::copy(kChildErrorMagic.begin(), kChildErrorMagic.end(), record.begin());
    const auto stage_value = static_cast<std::uint32_t>(stage);
    const auto error_value = static_cast<std::uint32_t>(
        error_number > 0 ? error_number : EIO);
    for (unsigned index = 0U; index < 4U; ++index) {
        record[4U + index] = static_cast<std::uint8_t>(
            (stage_value >> (index * 8U)) & 0xffU);
        record[8U + index] = static_cast<std::uint8_t>(
            (error_value >> (index * 8U)) & 0xffU);
    }
    static_cast<void>(child_send_status(record));
    _exit(126);
}

void child_announce_ready() noexcept {
    if (!child_send_status(kChildReadyRecord)) _exit(126);
}

[[nodiscard]] const char *child_stage_name(ChildStage stage) noexcept {
    switch (stage) {
        case ChildStage::marker: return "internal marker";
        case ChildStage::status_descriptor: return "status descriptor";
        case ChildStage::parent_death: return "parent-death contract";
        case ChildStage::manifest_read: return "manifest read";
        case ChildStage::manifest_decode: return "manifest decode";
        case ChildStage::session: return "setsid";
        case ChildStage::controlling_terminal: return "controlling terminal";
        case ChildStage::window: return "initial window";
        case ChildStage::foreground_group: return "foreground process group";
        case ChildStage::executable: return "executable validation";
        case ChildStage::working_directory: return "working directory";
        case ChildStage::resource_limits: return "resource limits";
        case ChildStage::identity: return "identity policy";
        case ChildStage::no_new_privileges: return "no-new-privileges";
        case ChildStage::descriptor_hygiene: return "descriptor hygiene";
        case ChildStage::final_exec: return "final fexecve";
        case ChildStage::internal_exception: return "internal exception";
        case ChildStage::descriptor_contract: return "descriptor contract";
        case ChildStage::ambient_capabilities: return "ambient capability hygiene";
        case ChildStage::dumpable_guard: return "pre-exec dumpable guard";
        case ChildStage::securebits: return "securebits capability lock";
        case ChildStage::capability_bounding_set: return "capability bounding set";
        case ChildStage::active_capabilities: return "active capability floor";
        case ChildStage::mdwe: return "memory-deny-write-execute";
        case ChildStage::landlock: return "Landlock strict confinement";
        case ChildStage::seccomp: return "seccomp baseline confinement";
    }
    return "unknown stage";
}

[[nodiscard]] bool valid_child_stage(std::uint32_t value) noexcept {
    return value >= static_cast<std::uint32_t>(ChildStage::marker) &&
           value <= static_cast<std::uint32_t>(ChildStage::seccomp);
}

[[nodiscard]] Result<std::vector<std::uint8_t>> read_manifest_from_child_fd() {
    std::vector<std::uint8_t> bytes;
    std::array<std::uint8_t, 4096U> buffer{};
    while (true) {
        const ssize_t count = ::read(
            kConfigurationDescriptor, buffer.data(), buffer.size());
        if (count > 0) {
            const std::size_t amount = static_cast<std::size_t>(count);
            if (bytes.size() > kMaximumManifestBytes - amount) {
                return Status{ErrorCode::resource_exhausted,
                              "PTY manifest exceeds the child handoff bound"};
            }
            bytes.insert(
                bytes.end(), buffer.begin(),
                buffer.begin() + static_cast<std::ptrdiff_t>(amount));
            continue;
        }
        if (count == 0) break;
        if (errno == EINTR) continue;
        return errno_status(ErrorCode::io_error, "read PTY child manifest");
    }
    return bytes;
}

[[nodiscard]] Status set_descriptor_cloexec(int descriptor) {
    const int flags = ::fcntl(descriptor, F_GETFD);
    if (flags < 0 || ::fcntl(descriptor, F_SETFD, flags | FD_CLOEXEC) != 0) {
        return errno_status(ErrorCode::io_error, "set PTY child close-on-exec");
    }
    return Status::success();
}

struct SocketPeer {
    ucred credentials{};
    dev_t device{0};
    ino_t inode{0};
};

[[nodiscard]] Result<SocketPeer> socket_peer_credentials(int descriptor) {
    struct stat metadata {};
    if (::fstat(descriptor, &metadata) != 0) {
        return errno_status(ErrorCode::io_error, "fstat PTY child socket");
    }
    if (!S_ISSOCK(metadata.st_mode)) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child handoff descriptor is not a socket"};
    }
    int socket_type = 0;
    socklen_t type_size = sizeof(socket_type);
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_TYPE,
            &socket_type, &type_size) != 0) {
        return errno_status(ErrorCode::io_error, "inspect PTY child socket type");
    }
    if (type_size != sizeof(socket_type) || socket_type != SOCK_STREAM) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child handoff descriptor is not a stream socket"};
    }
    ucred credentials {};
    socklen_t credential_size = sizeof(credentials);
    if (::getsockopt(
            descriptor, SOL_SOCKET, SO_PEERCRED,
            &credentials, &credential_size) != 0) {
        return errno_status(ErrorCode::io_error, "inspect PTY child socket peer");
    }
    if (credential_size != sizeof(credentials) || credentials.pid <= 1) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child socket has invalid peer credentials"};
    }
    return SocketPeer{credentials, metadata.st_dev, metadata.st_ino};
}

[[nodiscard]] Result<pid_t> validate_child_descriptor_contract() {
    auto configuration_peer = socket_peer_credentials(kConfigurationDescriptor);
    if (!configuration_peer.ok()) return configuration_peer.status();
    auto status_peer = socket_peer_credentials(kStatusDescriptor);
    if (!status_peer.ok()) return status_peer.status();
    if (configuration_peer.value().device == status_peer.value().device &&
        configuration_peer.value().inode == status_peer.value().inode) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child manifest and status descriptors alias one socket"};
    }
    if (configuration_peer.value().credentials.pid !=
            status_peer.value().credentials.pid ||
        configuration_peer.value().credentials.uid !=
            status_peer.value().credentials.uid ||
        configuration_peer.value().credentials.gid !=
            status_peer.value().credentials.gid) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child sockets disagree about their parent peer"};
    }
    if (status_peer.value().credentials.uid != ::geteuid() ||
        status_peer.value().credentials.gid != ::getegid()) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child socket peer credentials do not match the helper"};
    }

    struct stat working_directory {};
    if (::fstat(kWorkingDirectoryDescriptor, &working_directory) != 0) {
        return errno_status(ErrorCode::io_error,
                            "fstat PTY child working directory");
    }
    if (!S_ISDIR(working_directory.st_mode)) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child working-directory descriptor is not a directory"};
    }

    std::array<struct stat, 3U> terminals{};
    for (int descriptor = STDIN_FILENO; descriptor <= STDERR_FILENO;
         ++descriptor) {
        auto &metadata = terminals[static_cast<std::size_t>(descriptor)];
        if (::fstat(descriptor, &metadata) != 0 || ::isatty(descriptor) != 1) {
            return Status{ErrorCode::invalid_argument,
                          "PTY child standard descriptor is not a terminal"};
        }
        if (!S_ISCHR(metadata.st_mode)) {
            return Status{ErrorCode::invalid_argument,
                          "PTY child standard descriptor is not a character device"};
        }
    }
    for (std::size_t index = 1U; index < terminals.size(); ++index) {
        if (terminals[index].st_dev != terminals[0U].st_dev ||
            terminals[index].st_ino != terminals[0U].st_ino ||
            terminals[index].st_rdev != terminals[0U].st_rdev) {
            return Status{ErrorCode::invalid_argument,
                          "PTY child standard descriptors do not share one terminal"};
        }
    }
    return status_peer.value().credentials.pid;
}

[[nodiscard]] Status arm_parent_death_contract(pid_t expected_parent) {
    if (expected_parent <= 1) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child expected parent pid is invalid"};
    }
    if (::prctl(PR_SET_PDEATHSIG, SIGKILL, 0, 0, 0) != 0) {
        return errno_status(ErrorCode::io_error,
                            "arm PTY parent-death signal");
    }
    int configured_signal = 0;
    if (::prctl(PR_GET_PDEATHSIG, &configured_signal, 0, 0, 0) != 0) {
        return errno_status(ErrorCode::io_error,
                            "verify PTY parent-death signal");
    }
    if (configured_signal != SIGKILL || ::getppid() != expected_parent) {
        return Status{ErrorCode::unavailable,
                      "PTY parent changed while the death contract was armed"};
    }
    return Status::success();
}

[[nodiscard]] Status arm_no_new_privileges() {
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        return errno_status(ErrorCode::io_error,
                            "arm PTY no-new-privileges contract");
    }
    const int configured = ::prctl(PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0);
    if (configured < 0) {
        return errno_status(ErrorCode::io_error,
                            "verify PTY no-new-privileges contract");
    }
    if (configured != 1) {
        return Status{ErrorCode::unavailable,
                      "PTY no-new-privileges contract did not remain armed"};
    }
    return Status::success();
}

[[nodiscard]] Status verify_privilege_escalation_prerequisites() {
    const int no_new_privileges = ::prctl(
        PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0);
    if (no_new_privileges < 0) {
        return errno_status(
            ErrorCode::io_error,
            "inspect PTY privilege-escalation no-new-privileges state");
    }
    if (no_new_privileges != 0) {
        return Status{
            ErrorCode::unavailable,
            "PTY privilege escalation is blocked by inherited no-new-privileges"};
    }
#if defined(PR_GET_SECUREBITS) && defined(SECBIT_NOROOT) && \
    defined(SECBIT_NO_SETUID_FIXUP)
    const int securebits = ::prctl(PR_GET_SECUREBITS, 0, 0, 0, 0);
    if (securebits < 0) {
        return errno_status(
            ErrorCode::io_error,
            "inspect PTY privilege-escalation securebits state");
    }
    if ((securebits & (SECBIT_NOROOT | SECBIT_NO_SETUID_FIXUP)) != 0) {
        return Status{
            ErrorCode::unavailable,
            "PTY privilege escalation is blocked by inherited securebits"};
    }
#else
    return Status{
        ErrorCode::unsupported,
        "PTY privilege-escalation securebits inspection is unavailable"};
#endif
#if defined(PR_CAPBSET_READ)
    for (const int capability : {CAP_SETUID, CAP_SETGID}) {
        const int present = ::prctl(
            PR_CAPBSET_READ, capability, 0, 0, 0);
        if (present < 0) {
            return errno_status(
                ErrorCode::io_error,
                "inspect PTY privilege-escalation capability bound");
        }
        if (present != 1) {
            return Status{
                ErrorCode::unavailable,
                "PTY privilege escalation lacks setuid/setgid capability bounds"};
        }
    }
#else
    return Status{
        ErrorCode::unsupported,
        "PTY privilege-escalation capability-bound inspection is unavailable"};
#endif
    return Status::success();
}

constexpr int kMaximumCapabilityProbe = 1024;

struct CapabilitySnapshot {
    std::array<__user_cap_data_struct, _LINUX_CAPABILITY_U32S_3> words{};
};

struct CapabilityBoundary {
    int last_capability{-1};
    bool securebits_sealed{false};
    bool bounding_set_sealed{false};
};

struct StagedCapabilityBoundary {
    CapabilityBoundary boundary{};
    ChildStage failed_stage{ChildStage::capability_bounding_set};
    Status status{};

    [[nodiscard]] bool ok() const noexcept { return status.ok(); }
};

struct StagedStatus {
    ChildStage failed_stage{ChildStage::internal_exception};
    Status status{};

    [[nodiscard]] bool ok() const noexcept { return status.ok(); }
};

[[nodiscard]] Result<int> runtime_last_capability() {
#if defined(PR_CAPBSET_READ)
    for (int capability = 0; capability <= kMaximumCapabilityProbe; ++capability) {
        errno = 0;
        const int present = ::prctl(PR_CAPBSET_READ, capability, 0, 0, 0);
        if (present >= 0) continue;
        if (errno == EINVAL && capability > 0) return capability - 1;
        return errno_status(ErrorCode::io_error,
                            "discover PTY runtime capability ceiling");
    }
    return Status{ErrorCode::unsupported,
                  "PTY runtime capability ceiling exceeds the reviewed bound"};
#else
    return Status{ErrorCode::unsupported,
                  "PTY capability bounding-set inspection is unavailable"};
#endif
}

[[nodiscard]] Result<CapabilitySnapshot> read_capability_snapshot() {
#if defined(SYS_capget)
    __user_cap_header_struct header{};
    header.version = _LINUX_CAPABILITY_VERSION_3;
    header.pid = 0;
    CapabilitySnapshot snapshot;
    if (::syscall(SYS_capget, &header, snapshot.words.data()) != 0) {
        return errno_status(ErrorCode::io_error,
                            "read PTY process capability sets");
    }
    return snapshot;
#else
    return Status{ErrorCode::unsupported,
                  "PTY capability-set inspection is unavailable"};
#endif
}

[[nodiscard]] bool capability_snapshot_empty(
    const CapabilitySnapshot &snapshot) noexcept {
    return std::all_of(
        snapshot.words.begin(), snapshot.words.end(),
        [](const __user_cap_data_struct &word) {
            return word.effective == 0U && word.permitted == 0U &&
                   word.inheritable == 0U;
        });
}

[[nodiscard]] bool effective_capability_is_set(
    const CapabilitySnapshot &snapshot, int capability) noexcept {
    if (capability < 0) return false;
    const std::size_t word = static_cast<std::size_t>(capability / 32);
    if (word >= snapshot.words.size()) return false;
    const std::uint32_t mask =
        std::uint32_t{1U} << static_cast<unsigned>(capability % 32);
    return (snapshot.words[word].effective & mask) != 0U;
}

[[nodiscard]] Status clear_ambient_capabilities(int last_capability) {
#if defined(PR_CAP_AMBIENT) && defined(PR_CAP_AMBIENT_CLEAR_ALL) && \
    defined(PR_CAP_AMBIENT_IS_SET)
    if (last_capability < 0 || last_capability > kMaximumCapabilityProbe) {
        return Status{ErrorCode::invalid_argument,
                      "PTY ambient capability ceiling is invalid"};
    }
    if (::prctl(PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL, 0, 0, 0) != 0) {
        return errno_status(ErrorCode::io_error,
                            "clear PTY ambient capabilities");
    }
    for (int capability = 0; capability <= last_capability; ++capability) {
        const int configured = ::prctl(
            PR_CAP_AMBIENT, PR_CAP_AMBIENT_IS_SET, capability, 0, 0);
        if (configured < 0) {
            return errno_status(ErrorCode::io_error,
                                "verify PTY ambient capabilities");
        }
        if (configured != 0) {
            return Status{ErrorCode::unavailable,
                          "PTY ambient capability set did not clear"};
        }
    }
    return Status::success();
#else
    static_cast<void>(last_capability);
    return Status{ErrorCode::unsupported,
                  "PTY ambient capability clearing is unavailable"};
#endif
}

[[nodiscard]] Status seal_securebits() {
#if defined(PR_GET_SECUREBITS) && defined(PR_SET_SECUREBITS) && \
    defined(SECBIT_NOROOT) && defined(SECBIT_NOROOT_LOCKED) && \
    defined(SECBIT_NO_SETUID_FIXUP) && defined(SECBIT_NO_SETUID_FIXUP_LOCKED) && \
    defined(SECBIT_KEEP_CAPS) && defined(SECBIT_KEEP_CAPS_LOCKED) && \
    defined(SECBIT_NO_CAP_AMBIENT_RAISE) && \
    defined(SECBIT_NO_CAP_AMBIENT_RAISE_LOCKED)
    const int current = ::prctl(PR_GET_SECUREBITS, 0, 0, 0, 0);
    if (current < 0) {
        return errno_status(ErrorCode::io_error,
                            "read PTY securebits policy");
    }
    constexpr int required_set =
        SECBIT_NOROOT | SECBIT_NOROOT_LOCKED |
        SECBIT_NO_SETUID_FIXUP_LOCKED |
        SECBIT_KEEP_CAPS_LOCKED |
        SECBIT_NO_CAP_AMBIENT_RAISE |
        SECBIT_NO_CAP_AMBIENT_RAISE_LOCKED;
    constexpr int required_clear =
        SECBIT_NO_SETUID_FIXUP | SECBIT_KEEP_CAPS;
    const int desired = (current | required_set) & ~required_clear;
    if (::prctl(PR_SET_SECUREBITS, desired, 0, 0, 0) != 0) {
        return errno_status(ErrorCode::io_error,
                            "seal PTY securebits policy");
    }
    const int configured = ::prctl(PR_GET_SECUREBITS, 0, 0, 0, 0);
    if (configured < 0) {
        return errno_status(ErrorCode::io_error,
                            "verify PTY securebits policy");
    }
    if ((configured & required_set) != required_set ||
        (configured & required_clear) != 0) {
        return Status{ErrorCode::unavailable,
                      "PTY securebits policy did not converge"};
    }
    return Status::success();
#else
    return Status{ErrorCode::unsupported,
                  "PTY securebits sealing is unavailable"};
#endif
}

[[nodiscard]] Status verify_securebits_sealed() {
#if defined(PR_GET_SECUREBITS) && defined(SECBIT_NOROOT) && \
    defined(SECBIT_NOROOT_LOCKED) && defined(SECBIT_NO_SETUID_FIXUP) && \
    defined(SECBIT_NO_SETUID_FIXUP_LOCKED) && defined(SECBIT_KEEP_CAPS) && \
    defined(SECBIT_KEEP_CAPS_LOCKED) && defined(SECBIT_NO_CAP_AMBIENT_RAISE) && \
    defined(SECBIT_NO_CAP_AMBIENT_RAISE_LOCKED)
    const int configured = ::prctl(PR_GET_SECUREBITS, 0, 0, 0, 0);
    if (configured < 0) {
        return errno_status(ErrorCode::io_error,
                            "verify PTY securebits policy after identity");
    }
    constexpr int required_set =
        SECBIT_NOROOT | SECBIT_NOROOT_LOCKED |
        SECBIT_NO_SETUID_FIXUP_LOCKED |
        SECBIT_KEEP_CAPS_LOCKED |
        SECBIT_NO_CAP_AMBIENT_RAISE |
        SECBIT_NO_CAP_AMBIENT_RAISE_LOCKED;
    constexpr int required_clear =
        SECBIT_NO_SETUID_FIXUP | SECBIT_KEEP_CAPS;
    if ((configured & required_set) != required_set ||
        (configured & required_clear) != 0) {
        return Status{ErrorCode::unavailable,
                      "PTY securebits seal changed across identity setup"};
    }
    return Status::success();
#else
    return Status{ErrorCode::unsupported,
                  "PTY securebits verification is unavailable"};
#endif
}

[[nodiscard]] Status drop_capability_bounding_set(int last_capability) {
#if defined(PR_CAPBSET_READ) && defined(PR_CAPBSET_DROP)
    for (int capability = 0; capability <= last_capability; ++capability) {
        const int present = ::prctl(PR_CAPBSET_READ, capability, 0, 0, 0);
        if (present < 0) {
            return errno_status(ErrorCode::io_error,
                                "read PTY capability bounding set");
        }
        if (present == 1 &&
            ::prctl(PR_CAPBSET_DROP, capability, 0, 0, 0) != 0) {
            return errno_status(ErrorCode::io_error,
                                "drop PTY capability bounding-set member");
        }
    }
    for (int capability = 0; capability <= last_capability; ++capability) {
        const int present = ::prctl(PR_CAPBSET_READ, capability, 0, 0, 0);
        if (present < 0) {
            return errno_status(ErrorCode::io_error,
                                "verify PTY capability bounding set");
        }
        if (present != 0) {
            return Status{ErrorCode::unavailable,
                          "PTY capability bounding set did not clear"};
        }
    }
    return Status::success();
#else
    static_cast<void>(last_capability);
    return Status{ErrorCode::unsupported,
                  "PTY capability bounding-set dropping is unavailable"};
#endif
}

[[nodiscard]] Status verify_capability_bounding_set_empty(
    int last_capability) {
#if defined(PR_CAPBSET_READ)
    for (int capability = 0; capability <= last_capability; ++capability) {
        const int present = ::prctl(PR_CAPBSET_READ, capability, 0, 0, 0);
        if (present < 0) {
            return errno_status(ErrorCode::io_error,
                                "verify PTY capability bounding set after identity");
        }
        if (present != 0) {
            return Status{ErrorCode::unavailable,
                          "PTY capability bounding set changed after identity"};
        }
    }
    return Status::success();
#else
    static_cast<void>(last_capability);
    return Status{ErrorCode::unsupported,
                  "PTY capability bounding-set verification is unavailable"};
#endif
}

[[nodiscard]] StagedCapabilityBoundary prepare_capability_boundary(
    bool seal_future_privilege) {
    auto last_capability = runtime_last_capability();
    if (!last_capability.ok()) {
        return StagedCapabilityBoundary{
            {}, ChildStage::capability_bounding_set,
            last_capability.status()};
    }
    constexpr int represented_capabilities =
        static_cast<int>(_LINUX_CAPABILITY_U32S_3 * 32U);
    if (last_capability.value() >= represented_capabilities) {
        return StagedCapabilityBoundary{
            {}, ChildStage::active_capabilities,
            Status{
                ErrorCode::unsupported,
                "PTY runtime capability ceiling exceeds the reviewed capget layout"}};
    }
    const Status ambient = clear_ambient_capabilities(last_capability.value());
    if (!ambient.ok()) {
        return StagedCapabilityBoundary{
            {}, ChildStage::ambient_capabilities, ambient};
    }
    auto snapshot = read_capability_snapshot();
    if (!snapshot.ok()) {
        return StagedCapabilityBoundary{
            {}, ChildStage::active_capabilities, snapshot.status()};
    }

    uid_t real_uid = 0;
    uid_t effective_uid = 0;
    uid_t saved_uid = 0;
    if (::getresuid(&real_uid, &effective_uid, &saved_uid) != 0) {
        return StagedCapabilityBoundary{
            {}, ChildStage::identity,
            errno_status(
                ErrorCode::io_error,
                "read PTY process identity before capability sealing")};
    }
    const bool privileged_context =
        real_uid == 0 || effective_uid == 0 || saved_uid == 0 ||
        !capability_snapshot_empty(snapshot.value());
    const bool can_seal = effective_capability_is_set(
        snapshot.value(), CAP_SETPCAP);

    CapabilityBoundary boundary;
    boundary.last_capability = last_capability.value();
    if (!seal_future_privilege) {
        // The active and ambient sets are still cleared after identity setup,
        // but the host capability bounding set and ordinary securebits remain
        // available to a later explicitly authorized set-ID/file-capability
        // helper. This is the kernel distinction between an owner shell that
        // may invoke sudo and every historical default-deny profile.
        return StagedCapabilityBoundary{boundary, {}, Status::success()};
    }
    if (!can_seal) {
        if (privileged_context) {
            return StagedCapabilityBoundary{
                {}, ChildStage::capability_bounding_set,
                Status{
                    ErrorCode::unavailable,
                    "PTY privileged context cannot seal its capability boundary"}};
        }
        return StagedCapabilityBoundary{boundary, {}, Status::success()};
    }

    const Status securebits = seal_securebits();
    if (!securebits.ok()) {
        return StagedCapabilityBoundary{
            {}, ChildStage::securebits, securebits};
    }
    boundary.securebits_sealed = true;
    const Status bounding = drop_capability_bounding_set(
        boundary.last_capability);
    if (!bounding.ok()) {
        return StagedCapabilityBoundary{
            {}, ChildStage::capability_bounding_set, bounding};
    }
    boundary.bounding_set_sealed = true;
    return StagedCapabilityBoundary{boundary, {}, Status::success()};
}

[[nodiscard]] Status clear_active_capabilities() {
#if defined(SYS_capset)
    __user_cap_header_struct header{};
    header.version = _LINUX_CAPABILITY_VERSION_3;
    header.pid = 0;
    std::array<__user_cap_data_struct, _LINUX_CAPABILITY_U32S_3> empty{};
    if (::syscall(SYS_capset, &header, empty.data()) != 0) {
        return errno_status(ErrorCode::io_error,
                            "clear PTY active capability sets");
    }
    auto configured = read_capability_snapshot();
    if (!configured.ok()) return configured.status();
    if (!capability_snapshot_empty(configured.value())) {
        return Status{ErrorCode::unavailable,
                      "PTY active capability sets did not clear"};
    }
    return Status::success();
#else
    return Status{ErrorCode::unsupported,
                  "PTY capability-set clearing is unavailable"};
#endif
}

[[nodiscard]] StagedStatus finalize_capability_boundary(
    const CapabilityBoundary &boundary) {
    const Status active = clear_active_capabilities();
    if (!active.ok()) {
        return StagedStatus{ChildStage::active_capabilities, active};
    }
    const Status ambient = clear_ambient_capabilities(
        boundary.last_capability);
    if (!ambient.ok()) {
        return StagedStatus{ChildStage::ambient_capabilities, ambient};
    }
    if (boundary.securebits_sealed) {
        const Status securebits = verify_securebits_sealed();
        if (!securebits.ok()) {
            return StagedStatus{ChildStage::securebits, securebits};
        }
    }
    if (boundary.bounding_set_sealed) {
        const Status bounding = verify_capability_bounding_set_empty(
            boundary.last_capability);
        if (!bounding.ok()) {
            return StagedStatus{
                ChildStage::capability_bounding_set, bounding};
        }
    }
    return StagedStatus{};
}

[[nodiscard]] Status arm_dumpable_guard() {
#if defined(PR_SET_DUMPABLE) && defined(PR_GET_DUMPABLE)
    if (::prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) != 0) {
        return errno_status(ErrorCode::io_error,
                            "arm PTY pre-exec dumpable guard");
    }
    const int configured = ::prctl(PR_GET_DUMPABLE, 0, 0, 0, 0);
    if (configured < 0) {
        return errno_status(ErrorCode::io_error,
                            "verify PTY pre-exec dumpable guard");
    }
    if (configured != 0) {
        return Status{ErrorCode::unavailable,
                      "PTY pre-exec dumpable guard did not remain armed"};
    }
    return Status::success();
#else
    return Status{ErrorCode::unsupported,
                  "PTY pre-exec dumpable guard is unavailable"};
#endif
}

#ifndef PR_SET_MDWE
#define PR_SET_MDWE 65
#endif
#ifndef PR_GET_MDWE
#define PR_GET_MDWE 66
#endif
#ifndef PR_MDWE_REFUSE_EXEC_GAIN
#define PR_MDWE_REFUSE_EXEC_GAIN (1UL << 0)
#endif

// IoTox intentionally carries the reviewed Landlock ABI 10 wire values instead
// of requiring the build host's kernel headers to have caught up.  The runtime
// ABI query below still decides whether strict confinement is available.
constexpr unsigned int kLandlockCreateRulesetVersion = 1U << 0U;
constexpr unsigned int kLandlockRulePathBeneath = 1U;
constexpr unsigned int kLandlockRestrictSelfTsync = 1U << 3U;
constexpr std::uint64_t kLandlockAccessFsWriteFile = 1ULL << 1U;
constexpr std::uint64_t kLandlockAccessFsRemoveDir = 1ULL << 4U;
constexpr std::uint64_t kLandlockAccessFsRemoveFile = 1ULL << 5U;
constexpr std::uint64_t kLandlockAccessFsMakeChar = 1ULL << 6U;
constexpr std::uint64_t kLandlockAccessFsMakeDir = 1ULL << 7U;
constexpr std::uint64_t kLandlockAccessFsMakeReg = 1ULL << 8U;
constexpr std::uint64_t kLandlockAccessFsMakeSock = 1ULL << 9U;
constexpr std::uint64_t kLandlockAccessFsMakeFifo = 1ULL << 10U;
constexpr std::uint64_t kLandlockAccessFsMakeBlock = 1ULL << 11U;
constexpr std::uint64_t kLandlockAccessFsMakeSym = 1ULL << 12U;
constexpr std::uint64_t kLandlockAccessFsRefer = 1ULL << 13U;
constexpr std::uint64_t kLandlockAccessFsTruncate = 1ULL << 14U;
constexpr std::uint64_t kLandlockAccessFsIoctlDevice = 1ULL << 15U;
constexpr std::uint64_t kLandlockAccessFsResolveUnix = 1ULL << 16U;
constexpr std::uint64_t kLandlockAccessNetBindTcp = 1ULL << 0U;
constexpr std::uint64_t kLandlockAccessNetConnectTcp = 1ULL << 1U;
constexpr std::uint64_t kLandlockAccessNetBindUdp = 1ULL << 2U;
constexpr std::uint64_t kLandlockAccessNetConnectSendUdp = 1ULL << 3U;
constexpr std::uint64_t kLandlockScopeAbstractUnixSocket = 1ULL << 0U;
constexpr std::uint64_t kLandlockScopeSignal = 1ULL << 1U;

struct LandlockRulesetAttrPrefix {
    std::uint64_t handled_access_fs{0U};
    std::uint64_t handled_access_net{0U};
    std::uint64_t scoped{0U};
};

#pragma pack(push, 1)
struct LandlockPathBeneathAttrV1 {
    std::uint64_t allowed_access{0U};
    std::int32_t parent_fd{-1};
};
#pragma pack(pop)

static_assert(sizeof(LandlockRulesetAttrPrefix) == 24U);
static_assert(sizeof(LandlockPathBeneathAttrV1) == 12U);

#ifdef IOTOX_HAS_LINUX_LANDLOCK_HEADER
#ifdef LANDLOCK_CREATE_RULESET_VERSION
static_assert(
    kLandlockCreateRulesetVersion == LANDLOCK_CREATE_RULESET_VERSION);
#endif
#ifdef LANDLOCK_RULE_PATH_BENEATH
static_assert(kLandlockRulePathBeneath == LANDLOCK_RULE_PATH_BENEATH);
#endif
#ifdef LANDLOCK_ACCESS_FS_IOCTL_DEV
static_assert(
    kLandlockAccessFsIoctlDevice == LANDLOCK_ACCESS_FS_IOCTL_DEV);
#endif
#ifdef LANDLOCK_ACCESS_FS_RESOLVE_UNIX
static_assert(
    kLandlockAccessFsResolveUnix == LANDLOCK_ACCESS_FS_RESOLVE_UNIX);
#endif
#ifdef LANDLOCK_ACCESS_NET_BIND_UDP
static_assert(kLandlockAccessNetBindUdp == LANDLOCK_ACCESS_NET_BIND_UDP);
#endif
#ifdef LANDLOCK_ACCESS_NET_CONNECT_SEND_UDP
static_assert(
    kLandlockAccessNetConnectSendUdp ==
    LANDLOCK_ACCESS_NET_CONNECT_SEND_UDP);
#endif
#ifdef LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET
static_assert(
    kLandlockScopeAbstractUnixSocket ==
    LANDLOCK_SCOPE_ABSTRACT_UNIX_SOCKET);
#endif
#ifdef LANDLOCK_SCOPE_SIGNAL
static_assert(kLandlockScopeSignal == LANDLOCK_SCOPE_SIGNAL);
#endif
#endif

[[nodiscard]] Status arm_memory_deny_write_execute() {
    if (::prctl(PR_SET_MDWE, PR_MDWE_REFUSE_EXEC_GAIN, 0, 0, 0) != 0) {
        return errno_status(ErrorCode::unsupported,
                            "arm PTY memory-deny-write-execute contract");
    }
    const int configured = ::prctl(PR_GET_MDWE, 0, 0, 0, 0);
    if (configured < 0) {
        return errno_status(ErrorCode::io_error,
                            "verify PTY memory-deny-write-execute contract");
    }
    if ((static_cast<unsigned long>(configured) &
         PR_MDWE_REFUSE_EXEC_GAIN) == 0UL) {
        return Status{ErrorCode::unavailable,
                      "PTY memory-deny-write-execute contract did not remain armed"};
    }
    return Status::success();
}

[[nodiscard]] Status apply_strict_landlock() {
#if defined(SYS_landlock_create_ruleset) && defined(SYS_landlock_add_rule) && \
    defined(SYS_landlock_restrict_self)
    constexpr int minimum_abi = 10;
    constexpr std::uint64_t access_fs_mutation =
        kLandlockAccessFsWriteFile |
        kLandlockAccessFsRemoveDir |
        kLandlockAccessFsRemoveFile |
        kLandlockAccessFsMakeChar |
        kLandlockAccessFsMakeDir |
        kLandlockAccessFsMakeReg |
        kLandlockAccessFsMakeSock |
        kLandlockAccessFsMakeFifo |
        kLandlockAccessFsMakeBlock |
        kLandlockAccessFsMakeSym |
        kLandlockAccessFsRefer |
        kLandlockAccessFsTruncate;
    constexpr std::uint64_t access_fs_working_directory =
        access_fs_mutation &
        ~(kLandlockAccessFsMakeChar | kLandlockAccessFsMakeBlock);
    constexpr std::uint64_t access_net_all =
        kLandlockAccessNetBindTcp |
        kLandlockAccessNetConnectTcp |
        kLandlockAccessNetBindUdp |
        kLandlockAccessNetConnectSendUdp;
    constexpr std::uint64_t scope_all =
        kLandlockScopeAbstractUnixSocket | kLandlockScopeSignal;

    errno = 0;
    const long abi = ::syscall(
        SYS_landlock_create_ruleset, nullptr, 0U,
        kLandlockCreateRulesetVersion);
    if (abi < 0) {
        return errno_status(ErrorCode::unsupported,
                            "query PTY Landlock ABI");
    }
    if (abi < minimum_abi) {
        return Status{ErrorCode::unsupported,
                      "strict PTY confinement requires Landlock ABI 10"};
    }

    LandlockRulesetAttrPrefix ruleset{};
    ruleset.handled_access_fs =
        access_fs_mutation | kLandlockAccessFsIoctlDevice |
        kLandlockAccessFsResolveUnix;
    ruleset.handled_access_net = access_net_all;
    ruleset.scoped = scope_all;
    const long created = ::syscall(
        SYS_landlock_create_ruleset, &ruleset, sizeof(ruleset), 0U);
    if (created < 0) {
        return errno_status(ErrorCode::io_error,
                            "create strict PTY Landlock ruleset");
    }
    if (created > static_cast<long>(INT_MAX)) {
        return Status{ErrorCode::resource_exhausted,
                      "strict PTY Landlock descriptor exceeds the host fd range"};
    }
    FileDescriptor ruleset_descriptor(static_cast<int>(created));

    LandlockPathBeneathAttrV1 working_directory{};
    working_directory.allowed_access = access_fs_working_directory;
    working_directory.parent_fd = kWorkingDirectoryDescriptor;
    if (::syscall(
            SYS_landlock_add_rule, ruleset_descriptor.get(),
            kLandlockRulePathBeneath, &working_directory, 0U) != 0) {
        return errno_status(ErrorCode::io_error,
                            "allow strict PTY working-directory writes");
    }
    if (::syscall(
            SYS_landlock_restrict_self, ruleset_descriptor.get(),
            kLandlockRestrictSelfTsync) != 0) {
        return errno_status(ErrorCode::io_error,
                            "enforce strict PTY Landlock ruleset");
    }
    return Status::success();
#else
    return Status{ErrorCode::unsupported,
                  "strict PTY Landlock system calls are unavailable"};
#endif
}

[[nodiscard]] std::optional<std::uint32_t> native_audit_architecture() {
#if defined(__x86_64__) && defined(AUDIT_ARCH_X86_64)
    return static_cast<std::uint32_t>(AUDIT_ARCH_X86_64);
#elif defined(__aarch64__) && defined(AUDIT_ARCH_AARCH64)
    return static_cast<std::uint32_t>(AUDIT_ARCH_AARCH64);
#elif defined(__i386__) && defined(AUDIT_ARCH_I386)
    return static_cast<std::uint32_t>(AUDIT_ARCH_I386);
#elif defined(__arm__) && defined(AUDIT_ARCH_ARM)
    return static_cast<std::uint32_t>(AUDIT_ARCH_ARM);
#elif defined(__riscv) && __riscv_xlen == 64 && defined(AUDIT_ARCH_RISCV64)
    return static_cast<std::uint32_t>(AUDIT_ARCH_RISCV64);
#elif defined(__s390x__) && defined(AUDIT_ARCH_S390X)
    return static_cast<std::uint32_t>(AUDIT_ARCH_S390X);
#elif defined(__powerpc64__) && defined(__LITTLE_ENDIAN__) && \
    defined(AUDIT_ARCH_PPC64LE)
    return static_cast<std::uint32_t>(AUDIT_ARCH_PPC64LE);
#elif defined(__powerpc64__) && defined(AUDIT_ARCH_PPC64)
    return static_cast<std::uint32_t>(AUDIT_ARCH_PPC64);
#else
    return std::nullopt;
#endif
}

void append_bpf_statement(
    std::vector<sock_filter> &filter, std::uint16_t code,
    std::uint32_t value) {
    filter.push_back(sock_filter{code, 0U, 0U, value});
}

void append_bpf_jump(
    std::vector<sock_filter> &filter, std::uint16_t code,
    std::uint32_t value, std::uint8_t jump_true,
    std::uint8_t jump_false) {
    filter.push_back(sock_filter{
        code, jump_true, jump_false, value});
}

void append_seccomp_denial(
    std::vector<sock_filter> &filter, std::uint32_t syscall_number,
    int error_number = EPERM) {
    append_bpf_jump(
        filter,
        static_cast<std::uint16_t>(BPF_JMP | BPF_JEQ | BPF_K),
        syscall_number, 0U, 1U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_RET | BPF_K),
        static_cast<std::uint32_t>(SECCOMP_RET_ERRNO) |
            static_cast<std::uint32_t>(error_number));
}

[[nodiscard]] constexpr std::uint32_t seccomp_argument_low_word_offset(
    std::size_t argument_index) {
    constexpr std::size_t argument_bytes = sizeof(seccomp_data::args[0U]);
    std::size_t word_offset = 0U;
#if defined(__BYTE_ORDER__) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    word_offset = argument_bytes - sizeof(std::uint32_t);
#elif !defined(__BYTE_ORDER__) || __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "IoTox seccomp argument filtering requires a reviewed byte order"
#endif
    return static_cast<std::uint32_t>(
        offsetof(seccomp_data, args) + argument_index * argument_bytes +
        word_offset);
}

void append_seccomp_masked_argument_denial(
    std::vector<sock_filter> &filter, std::uint32_t syscall_number,
    std::size_t argument_index, std::uint32_t denied_mask,
    int error_number = EPERM) {
    // A contains seccomp_data.nr on entry and is restored on every allowed path.
    append_bpf_jump(
        filter,
        static_cast<std::uint16_t>(BPF_JMP | BPF_JEQ | BPF_K),
        syscall_number, 0U, 3U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_LD | BPF_W | BPF_ABS),
        seccomp_argument_low_word_offset(argument_index));
    append_bpf_jump(
        filter,
        static_cast<std::uint16_t>(BPF_JMP | BPF_JSET | BPF_K),
        denied_mask, 0U, 1U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_RET | BPF_K),
        static_cast<std::uint32_t>(SECCOMP_RET_ERRNO) |
            static_cast<std::uint32_t>(error_number));
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_LD | BPF_W | BPF_ABS),
        static_cast<std::uint32_t>(offsetof(seccomp_data, nr)));
}

void append_seccomp_exact_argument_denial(
    std::vector<sock_filter> &filter, std::uint32_t syscall_number,
    std::size_t argument_index, std::uint32_t denied_value,
    int error_number = EPERM) {
    // A contains seccomp_data.nr on entry and is restored on every allowed path.
    append_bpf_jump(
        filter,
        static_cast<std::uint16_t>(BPF_JMP | BPF_JEQ | BPF_K),
        syscall_number, 0U, 3U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_LD | BPF_W | BPF_ABS),
        seccomp_argument_low_word_offset(argument_index));
    append_bpf_jump(
        filter,
        static_cast<std::uint16_t>(BPF_JMP | BPF_JEQ | BPF_K),
        denied_value, 0U, 1U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_RET | BPF_K),
        static_cast<std::uint32_t>(SECCOMP_RET_ERRNO) |
            static_cast<std::uint32_t>(error_number));
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_LD | BPF_W | BPF_ABS),
        static_cast<std::uint32_t>(offsetof(seccomp_data, nr)));
}

void append_terminal_ioctl_denials(std::vector<sock_filter> &filter) {
#ifdef SYS_ioctl
    for (const std::uint32_t request :
         detail::kDeniedTerminalIoctlRequests) {
        append_seccomp_exact_argument_denial(
            filter, static_cast<std::uint32_t>(SYS_ioctl), 1U, request);
    }
#else
    static_cast<void>(filter);
#endif
}

[[nodiscard]] Status install_baseline_seccomp() {
    const auto architecture = native_audit_architecture();
    if (!architecture.has_value()) {
        return Status{ErrorCode::unsupported,
                      "PTY seccomp architecture is not reviewed"};
    }
    std::vector<sock_filter> filter;
    filter.reserve(208U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_LD | BPF_W | BPF_ABS),
        static_cast<std::uint32_t>(offsetof(seccomp_data, arch)));
    append_bpf_jump(
        filter, static_cast<std::uint16_t>(BPF_JMP | BPF_JEQ | BPF_K),
        *architecture, 1U, 0U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_RET | BPF_K),
        static_cast<std::uint32_t>(SECCOMP_RET_KILL_PROCESS));
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_LD | BPF_W | BPF_ABS),
        static_cast<std::uint32_t>(offsetof(seccomp_data, nr)));
#if defined(__x86_64__)
    constexpr std::uint32_t x32_syscall_bit = 0x40000000U;
    append_bpf_jump(
        filter, static_cast<std::uint16_t>(BPF_JMP | BPF_JGE | BPF_K),
        x32_syscall_bit, 0U, 1U);
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_RET | BPF_K),
        static_cast<std::uint32_t>(SECCOMP_RET_ERRNO) |
            static_cast<std::uint32_t>(ENOSYS));
#endif

    // Namespace creation has two syscall entrances.  clone(2) exposes its
    // flags directly, so retain ordinary fork/thread flags and reject only
    // namespace bits.  clone3(2) stores flags behind a pointer that classic
    // seccomp cannot safely dereference, so report ENOSYS and permit libc's
    // reviewed clone(2) fallback instead.
    std::uint32_t namespace_clone_mask = 0U;
#ifdef CLONE_NEWNS
    namespace_clone_mask |= static_cast<std::uint32_t>(CLONE_NEWNS);
#endif
#ifdef CLONE_NEWCGROUP
    namespace_clone_mask |= static_cast<std::uint32_t>(CLONE_NEWCGROUP);
#endif
#ifdef CLONE_NEWUTS
    namespace_clone_mask |= static_cast<std::uint32_t>(CLONE_NEWUTS);
#endif
#ifdef CLONE_NEWIPC
    namespace_clone_mask |= static_cast<std::uint32_t>(CLONE_NEWIPC);
#endif
#ifdef CLONE_NEWUSER
    namespace_clone_mask |= static_cast<std::uint32_t>(CLONE_NEWUSER);
#endif
#ifdef CLONE_NEWPID
    namespace_clone_mask |= static_cast<std::uint32_t>(CLONE_NEWPID);
#endif
#ifdef CLONE_NEWNET
    namespace_clone_mask |= static_cast<std::uint32_t>(CLONE_NEWNET);
#endif
#ifdef SYS_clone
    if (namespace_clone_mask != 0U) {
#if defined(__s390__) || defined(__s390x__)
        constexpr std::size_t clone_flags_argument = 1U;
#else
        constexpr std::size_t clone_flags_argument = 0U;
#endif
        append_seccomp_masked_argument_denial(
            filter, static_cast<std::uint32_t>(SYS_clone),
            clone_flags_argument, namespace_clone_mask);
    }
#endif
#ifdef SYS_clone3
    append_seccomp_denial(
        filter, static_cast<std::uint32_t>(SYS_clone3), ENOSYS);
#endif

    // The helper establishes the process as the terminal session leader and
    // arms a verified parent-death signal before this filter is installed.
    // Freeze those lifecycle properties while leaving shell job-control
    // process groups available inside the existing session.
#ifdef SYS_prctl
#ifdef PR_SET_PDEATHSIG
    append_seccomp_exact_argument_denial(
        filter, static_cast<std::uint32_t>(SYS_prctl), 0U,
        static_cast<std::uint32_t>(PR_SET_PDEATHSIG));
#endif
#endif
#ifdef SYS_setsid
    append_seccomp_denial(
        filter, static_cast<std::uint32_t>(SYS_setsid));
#endif
    append_terminal_ioctl_denials(filter);

#define IOTOX_DENY_SYSCALL(name) \
    do { \
        append_seccomp_denial( \
            filter, static_cast<std::uint32_t>(SYS_##name)); \
    } while (false)
#ifdef SYS_ptrace
    IOTOX_DENY_SYSCALL(ptrace);
#endif
#ifdef SYS_process_vm_readv
    IOTOX_DENY_SYSCALL(process_vm_readv);
#endif
#ifdef SYS_process_vm_writev
    IOTOX_DENY_SYSCALL(process_vm_writev);
#endif
#ifdef SYS_pidfd_getfd
    IOTOX_DENY_SYSCALL(pidfd_getfd);
#endif
#ifdef SYS_pidfd_open
    IOTOX_DENY_SYSCALL(pidfd_open);
#endif
#ifdef SYS_pidfd_send_signal
    IOTOX_DENY_SYSCALL(pidfd_send_signal);
#endif
#ifdef SYS_process_madvise
    IOTOX_DENY_SYSCALL(process_madvise);
#endif
#ifdef SYS_process_mrelease
    IOTOX_DENY_SYSCALL(process_mrelease);
#endif
#ifdef SYS_kcmp
    IOTOX_DENY_SYSCALL(kcmp);
#endif
#ifdef SYS_bpf
    IOTOX_DENY_SYSCALL(bpf);
#endif
#ifdef SYS_perf_event_open
    IOTOX_DENY_SYSCALL(perf_event_open);
#endif
#ifdef SYS_userfaultfd
    IOTOX_DENY_SYSCALL(userfaultfd);
#endif
#ifdef SYS_io_uring_setup
    IOTOX_DENY_SYSCALL(io_uring_setup);
#endif
#ifdef SYS_io_uring_enter
    IOTOX_DENY_SYSCALL(io_uring_enter);
#endif
#ifdef SYS_io_uring_register
    IOTOX_DENY_SYSCALL(io_uring_register);
#endif
#ifdef SYS_mount
    IOTOX_DENY_SYSCALL(mount);
#endif
#ifdef SYS_umount2
    IOTOX_DENY_SYSCALL(umount2);
#endif
#ifdef SYS_pivot_root
    IOTOX_DENY_SYSCALL(pivot_root);
#endif
#ifdef SYS_move_mount
    IOTOX_DENY_SYSCALL(move_mount);
#endif
#ifdef SYS_fsopen
    IOTOX_DENY_SYSCALL(fsopen);
#endif
#ifdef SYS_fsconfig
    IOTOX_DENY_SYSCALL(fsconfig);
#endif
#ifdef SYS_fsmount
    IOTOX_DENY_SYSCALL(fsmount);
#endif
#ifdef SYS_fspick
    IOTOX_DENY_SYSCALL(fspick);
#endif
#ifdef SYS_open_tree
    IOTOX_DENY_SYSCALL(open_tree);
#endif
#ifdef SYS_mount_setattr
    IOTOX_DENY_SYSCALL(mount_setattr);
#endif
#ifdef SYS_chroot
    IOTOX_DENY_SYSCALL(chroot);
#endif
#ifdef SYS_unshare
    IOTOX_DENY_SYSCALL(unshare);
#endif
#ifdef SYS_setns
    IOTOX_DENY_SYSCALL(setns);
#endif
#ifdef SYS_init_module
    IOTOX_DENY_SYSCALL(init_module);
#endif
#ifdef SYS_finit_module
    IOTOX_DENY_SYSCALL(finit_module);
#endif
#ifdef SYS_delete_module
    IOTOX_DENY_SYSCALL(delete_module);
#endif
#ifdef SYS_kexec_load
    IOTOX_DENY_SYSCALL(kexec_load);
#endif
#ifdef SYS_kexec_file_load
    IOTOX_DENY_SYSCALL(kexec_file_load);
#endif
#ifdef SYS_reboot
    IOTOX_DENY_SYSCALL(reboot);
#endif
#ifdef SYS_swapon
    IOTOX_DENY_SYSCALL(swapon);
#endif
#ifdef SYS_swapoff
    IOTOX_DENY_SYSCALL(swapoff);
#endif
#ifdef SYS_open_by_handle_at
    IOTOX_DENY_SYSCALL(open_by_handle_at);
#endif
#ifdef SYS_name_to_handle_at
    IOTOX_DENY_SYSCALL(name_to_handle_at);
#endif
#ifdef SYS_keyctl
    IOTOX_DENY_SYSCALL(keyctl);
#endif
#ifdef SYS_add_key
    IOTOX_DENY_SYSCALL(add_key);
#endif
#ifdef SYS_request_key
    IOTOX_DENY_SYSCALL(request_key);
#endif
#ifdef SYS_iopl
    IOTOX_DENY_SYSCALL(iopl);
#endif
#ifdef SYS_ioperm
    IOTOX_DENY_SYSCALL(ioperm);
#endif
#ifdef SYS_vhangup
    IOTOX_DENY_SYSCALL(vhangup);
#endif
#ifdef SYS_syslog
    IOTOX_DENY_SYSCALL(syslog);
#endif
#ifdef SYS_acct
    IOTOX_DENY_SYSCALL(acct);
#endif
#ifdef SYS_quotactl
    IOTOX_DENY_SYSCALL(quotactl);
#endif
#ifdef SYS_lookup_dcookie
    IOTOX_DENY_SYSCALL(lookup_dcookie);
#endif
#ifdef SYS_fanotify_init
    IOTOX_DENY_SYSCALL(fanotify_init);
#endif
#ifdef SYS_personality
    IOTOX_DENY_SYSCALL(personality);
#endif
#ifdef SYS_sethostname
    IOTOX_DENY_SYSCALL(sethostname);
#endif
#ifdef SYS_setdomainname
    IOTOX_DENY_SYSCALL(setdomainname);
#endif
#ifdef SYS_settimeofday
    IOTOX_DENY_SYSCALL(settimeofday);
#endif
#ifdef SYS_clock_settime
    IOTOX_DENY_SYSCALL(clock_settime);
#endif
#ifdef SYS_adjtimex
    IOTOX_DENY_SYSCALL(adjtimex);
#endif
#ifdef SYS_clock_adjtime
    IOTOX_DENY_SYSCALL(clock_adjtime);
#endif
#undef IOTOX_DENY_SYSCALL
    append_bpf_statement(
        filter, static_cast<std::uint16_t>(BPF_RET | BPF_K),
        static_cast<std::uint32_t>(SECCOMP_RET_ALLOW));
    if (filter.size() > std::numeric_limits<unsigned short>::max()) {
        return Status{ErrorCode::resource_exhausted,
                      "PTY seccomp program exceeds the kernel length field"};
    }
    sock_fprog program{};
    program.len = static_cast<unsigned short>(filter.size());
    program.filter = filter.data();
    if (::prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &program) != 0) {
        return errno_status(ErrorCode::io_error,
                            "install PTY baseline seccomp filter");
    }
    const int configured = ::prctl(PR_GET_SECCOMP, 0, 0, 0, 0);
    if (configured < 0) {
        return errno_status(ErrorCode::io_error,
                            "verify PTY baseline seccomp filter");
    }
    if (configured != SECCOMP_MODE_FILTER) {
        return Status{ErrorCode::unavailable,
                      "PTY baseline seccomp filter did not remain active"};
    }
    return Status::success();
}

[[nodiscard]] Status apply_one_limit(int resource, std::uint64_t requested) {
    if (requested == 0U) return Status::success();
    struct rlimit current {};
    if (::getrlimit(resource, &current) != 0) {
        return errno_status(ErrorCode::io_error, "get PTY resource limit");
    }
    if (requested > static_cast<std::uint64_t>(current.rlim_max)) {
        return Status{ErrorCode::invalid_argument,
                      "PTY resource limit exceeds the inherited hard limit"};
    }
    current.rlim_cur = static_cast<rlim_t>(requested);
    if (::setrlimit(resource, &current) != 0) {
        return errno_status(ErrorCode::io_error, "set PTY resource limit");
    }
    return Status::success();
}

[[nodiscard]] Status apply_resource_limits(const ResourceLimits &limits) {
    struct rlimit no_core {};
    no_core.rlim_cur = 0;
    no_core.rlim_max = 0;
    if (::setrlimit(RLIMIT_CORE, &no_core) != 0) {
        return errno_status(ErrorCode::io_error, "disable PTY core dumps");
    }
    const std::array configured{
        std::pair{RLIMIT_CPU, limits.cpu_seconds},
        std::pair{RLIMIT_AS, limits.address_space_bytes},
        std::pair{RLIMIT_FSIZE, limits.file_size_bytes},
        std::pair{RLIMIT_NOFILE, limits.open_files},
#ifdef RLIMIT_NPROC
        std::pair{RLIMIT_NPROC, limits.processes},
#else
        std::pair{-1, std::uint64_t{0U}},
#endif
    };
    for (const auto &[resource, value] : configured) {
        if (resource < 0) continue;
        const Status applied = apply_one_limit(resource, value);
        if (!applied.ok()) return applied;
    }
    return Status::success();
}

[[nodiscard]] Status apply_identity(const IdentityPolicy &identity) {
    if (identity.mode == IdentityMode::inherit) return Status::success();
    if (identity.mode != IdentityMode::exact &&
        identity.mode != IdentityMode::account) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child received an invalid identity mode"};
    }
    if ((identity.mode == IdentityMode::exact &&
         (!identity.clear_supplementary_groups ||
          !identity.supplementary_groups.empty())) ||
        (identity.mode == IdentityMode::account &&
         identity.clear_supplementary_groups)) {
        return Status{ErrorCode::invalid_argument,
                      "PTY child received an invalid supplementary-group policy"};
    }
    const gid_t requested_gid = static_cast<gid_t>(identity.gid);
    const uid_t requested_uid = static_cast<uid_t>(identity.uid);
    if (static_cast<std::uint64_t>(requested_gid) != identity.gid ||
        static_cast<std::uint64_t>(requested_uid) != identity.uid) {
        return Status{ErrorCode::invalid_argument,
                      "PTY exact identity is not representable on this host"};
    }
    std::vector<gid_t> requested_groups;
    requested_groups.reserve(identity.supplementary_groups.size());
    for (const std::uint32_t group : identity.supplementary_groups) {
        const gid_t native = static_cast<gid_t>(group);
        if (static_cast<std::uint64_t>(native) != group) {
            return Status{
                ErrorCode::invalid_argument,
                "PTY supplementary group is not representable on this host"};
        }
        requested_groups.push_back(native);
    }

    const auto current_groups = [requested_gid]() -> Result<std::vector<gid_t>> {
        const int count = ::getgroups(0, nullptr);
        if (count < 0) {
            return errno_status(
                ErrorCode::io_error, "read PTY supplementary-group count");
        }
        std::vector<gid_t> groups(static_cast<std::size_t>(count));
        if (count > 0 && ::getgroups(count, groups.data()) != count) {
            return errno_status(
                ErrorCode::io_error, "read PTY supplementary groups");
        }
        std::sort(groups.begin(), groups.end());
        groups.erase(
            std::remove(groups.begin(), groups.end(), requested_gid),
            groups.end());
        return groups;
    };
    const auto identity_matches = [&]() -> Result<bool> {
        uid_t real_uid = 0;
        uid_t effective_uid = 0;
        uid_t saved_uid = 0;
        gid_t real_gid = 0;
        gid_t effective_gid = 0;
        gid_t saved_gid = 0;
        if (::getresuid(&real_uid, &effective_uid, &saved_uid) != 0 ||
            ::getresgid(&real_gid, &effective_gid, &saved_gid) != 0) {
            return errno_status(ErrorCode::io_error,
                                "read PTY identity convergence state");
        }
        auto groups = current_groups();
        if (!groups.ok()) return groups.status();
        return real_uid == requested_uid && effective_uid == requested_uid &&
               saved_uid == requested_uid && real_gid == requested_gid &&
               effective_gid == requested_gid && saved_gid == requested_gid &&
               groups.value() == requested_groups;
    };

    auto already_configured = identity_matches();
    if (!already_configured.ok()) return already_configured.status();
    if (already_configured.value()) return Status::success();

    if (::setgroups(
            requested_groups.size(),
            requested_groups.empty() ? nullptr : requested_groups.data()) !=
        0) {
        return errno_status(
            ErrorCode::io_error, "set PTY supplementary groups");
    }
    if (::setresgid(requested_gid, requested_gid, requested_gid) != 0) {
        return errno_status(ErrorCode::io_error, "set PTY gid");
    }
    if (::setresuid(requested_uid, requested_uid, requested_uid) != 0) {
        return errno_status(ErrorCode::io_error, "set PTY uid");
    }
    auto configured = identity_matches();
    if (!configured.ok()) return configured.status();
    if (!configured.value()) {
        return Status{ErrorCode::unavailable,
                      "PTY child identity did not converge exactly"};
    }
    return Status::success();
}

[[nodiscard]] Status close_unreserved_descriptors() {
    static_cast<void>(::close(kConfigurationDescriptor));
    static_cast<void>(::close(kWorkingDirectoryDescriptor));
#ifdef SYS_close_range
    if (::syscall(
            SYS_close_range,
            static_cast<unsigned int>(kFirstUnreservedDescriptor),
            std::numeric_limits<unsigned int>::max(), 0U) != 0 &&
        errno != ENOSYS && errno != EINVAL) {
        return errno_status(ErrorCode::io_error, "close PTY descriptor range");
    }
#endif

    // A lowered RLIMIT_NOFILE does not close inherited descriptors above the
    // new ceiling.  Enumerate the live descriptor table rather than guessing
    // an upper bound, then make a second pass to prove the postcondition.
    for (unsigned pass = 0U; pass < 2U; ++pass) {
        FileDescriptor directory_descriptor(::open(
            "/proc/self/fd", O_RDONLY | O_DIRECTORY | O_CLOEXEC));
        if (directory_descriptor.get() < 0) {
            return errno_status(
                ErrorCode::io_error, "open PTY descriptor inventory");
        }
        DIR *raw_directory = ::fdopendir(directory_descriptor.get());
        if (raw_directory == nullptr) {
            return errno_status(
                ErrorCode::io_error, "adopt PTY descriptor inventory");
        }
        static_cast<void>(directory_descriptor.release());
        DirectoryStream directory(raw_directory);
        const int inventory_descriptor = ::dirfd(directory.get());
        if (inventory_descriptor < 0) {
            return errno_status(
                ErrorCode::io_error, "identify PTY descriptor inventory");
        }

        while (true) {
            errno = 0;
            dirent *entry = ::readdir(directory.get());
            if (entry == nullptr) {
                if (errno != 0) {
                    return errno_status(
                        ErrorCode::io_error, "read PTY descriptor inventory");
                }
                break;
            }
            const std::string_view name{entry->d_name};
            if (name.empty()) continue;
            int descriptor = -1;
            const auto parsed = std::from_chars(
                name.data(), name.data() + name.size(), descriptor);
            if (parsed.ec != std::errc{} ||
                parsed.ptr != name.data() + name.size() || descriptor < 0) {
                continue;
            }
            if (descriptor < kFirstUnreservedDescriptor ||
                descriptor == inventory_descriptor) {
                continue;
            }
            if (pass == 0U) {
                if (::close(descriptor) != 0 && errno != EBADF && errno != EINTR) {
                    return errno_status(
                        ErrorCode::io_error, "close inventoried PTY descriptor");
                }
                continue;
            }
            return Status{
                ErrorCode::unavailable,
                "PTY descriptor closure postcondition was not satisfied"};
        }
    }
    return Status::success();
}

[[nodiscard]] int signal_number(ProcessSignal signal) {
    switch (signal) {
        case ProcessSignal::hangup: return SIGHUP;
        case ProcessSignal::terminate: return SIGTERM;
        case ProcessSignal::kill: return SIGKILL;
    }
    return 0;
}

struct ProcProcessState {
    pid_t process{-1};
    pid_t session{-1};
    char state{'?'};
    std::uint64_t start_time_ticks{0U};
};

[[nodiscard]] bool proc_state_is_live(char state) noexcept {
    return state != 'Z' && state != 'X' && state != 'x';
}

[[nodiscard]] std::optional<pid_t> parse_proc_process_name(
    std::string_view name) {
    if (name.empty()) return std::nullopt;
    std::int64_t value = 0;
    const auto parsed = std::from_chars(
        name.data(), name.data() + name.size(), value);
    if (parsed.ec != std::errc{} ||
        parsed.ptr != name.data() + name.size() || value <= 0 ||
        value > static_cast<std::int64_t>(std::numeric_limits<pid_t>::max())) {
        return std::nullopt;
    }
    return static_cast<pid_t>(value);
}

[[nodiscard]] bool parse_next_proc_integer(
    std::string_view text, std::size_t &cursor, std::int64_t &value) {
    while (cursor < text.size() && text[cursor] == ' ') ++cursor;
    if (cursor == text.size()) return false;
    const char *begin = text.data() + cursor;
    const char *end = text.data() + text.size();
    const auto parsed = std::from_chars(begin, end, value);
    if (parsed.ec != std::errc{} || parsed.ptr == begin) return false;
    cursor = static_cast<std::size_t>(parsed.ptr - text.data());
    return true;
}

[[nodiscard]] Result<FileDescriptor> open_proc_inventory(
    ErrorCode error_code, std::string_view operation) {
    FileDescriptor descriptor(::open(
        "/proc", O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) {
        return errno_status(error_code, operation);
    }
    struct statfs filesystem {};
    if (::fstatfs(descriptor.get(), &filesystem) != 0) {
        return errno_status(error_code, "inspect PTY procfs inventory");
    }
    if (static_cast<unsigned long>(filesystem.f_type) !=
        static_cast<unsigned long>(PROC_SUPER_MAGIC)) {
        return Status{
            error_code,
            "PTY session inventory is not backed by the proc filesystem"};
    }
    return descriptor;
}

[[nodiscard]] Result<std::optional<FileDescriptor>> open_proc_process_directory(
    int proc_descriptor, pid_t process) {
    const std::string name =
        std::to_string(static_cast<std::int64_t>(process));
    FileDescriptor descriptor(::openat(
        proc_descriptor, name.c_str(),
        O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) {
        if (errno == ENOENT || errno == ESRCH || errno == EACCES ||
            errno == EPERM) {
            return std::optional<FileDescriptor>{};
        }
        return errno_status(
            ErrorCode::io_error, "open PTY session member proc directory");
    }
    return std::optional<FileDescriptor>{std::move(descriptor)};
}

[[nodiscard]] Result<std::optional<ProcProcessState>> read_proc_process_state(
    int process_directory, pid_t process) {
    FileDescriptor descriptor(::openat(
        process_directory, "stat", O_RDONLY | O_CLOEXEC | O_NOFOLLOW));
    if (descriptor.get() < 0) {
        if (errno == ENOENT || errno == ESRCH || errno == EACCES ||
            errno == EPERM) {
            return std::optional<ProcProcessState>{};
        }
        return errno_status(ErrorCode::io_error, "open PTY session member state");
    }
    std::array<char, 4096U> buffer{};
    ssize_t count = -1;
    do {
        count = ::read(descriptor.get(), buffer.data(), buffer.size() - 1U);
    } while (count < 0 && errno == EINTR);
    if (count < 0) {
        if (errno == ENOENT || errno == ESRCH) {
            return std::optional<ProcProcessState>{};
        }
        return errno_status(ErrorCode::io_error, "read PTY session member state");
    }
    if (count == 0) return std::optional<ProcProcessState>{};
    const std::string_view text{
        buffer.data(), static_cast<std::size_t>(count)};
    const std::size_t command_begin = text.find(" (");
    const std::size_t command_end = text.rfind(')');
    std::int64_t reported_process = 0;
    if (command_begin == std::string_view::npos || command_begin == 0U ||
        command_end == std::string_view::npos ||
        command_end <= command_begin + 1U ||
        command_end + 3U >= text.size() || text[command_end + 1U] != ' ') {
        return Status{ErrorCode::protocol_error,
                      "PTY session member state was malformed"};
    }
    const auto parsed_process = std::from_chars(
        text.data(), text.data() + command_begin, reported_process);
    if (parsed_process.ec != std::errc{} ||
        parsed_process.ptr != text.data() + command_begin ||
        reported_process != static_cast<std::int64_t>(process)) {
        return Status{ErrorCode::protocol_error,
                      "PTY session member process identity was malformed"};
    }
    const char state = text[command_end + 2U];
    std::size_t cursor = command_end + 3U;
    std::int64_t parent = 0;
    std::int64_t group = 0;
    std::int64_t session = 0;
    if (!parse_next_proc_integer(text, cursor, parent) ||
        !parse_next_proc_integer(text, cursor, group) ||
        !parse_next_proc_integer(text, cursor, session) || session < 0 ||
        session > static_cast<std::int64_t>(
                      std::numeric_limits<pid_t>::max())) {
        return Status{ErrorCode::protocol_error,
                      "PTY session member identity was malformed"};
    }
    // Fields 7 through 21 precede starttime (field 22). Retaining starttime
    // gives an independent process-incarnation check in addition to the open
    // proc directory and pidfd identities.
    std::int64_t ignored = 0;
    for (unsigned int field = 7U; field <= 21U; ++field) {
        if (!parse_next_proc_integer(text, cursor, ignored)) {
            return Status{ErrorCode::protocol_error,
                          "PTY session member start identity was malformed"};
        }
    }
    std::int64_t start_time_ticks = 0;
    if (!parse_next_proc_integer(text, cursor, start_time_ticks) ||
        start_time_ticks < 0) {
        return Status{ErrorCode::protocol_error,
                      "PTY session member start identity was malformed"};
    }
    static_cast<void>(parent);
    static_cast<void>(group);
    return std::optional<ProcProcessState>{ProcProcessState{
        process, static_cast<pid_t>(session), state,
        static_cast<std::uint64_t>(start_time_ticks)}};
}

enum class ProcessSignalDisposition : std::uint8_t {
    delivered = 1U,
    vanished = 2U,
};

[[nodiscard]] Status verify_session_signal_support() {
#if defined(SYS_pidfd_open) && defined(SYS_pidfd_send_signal)
    const long opened = ::syscall(SYS_pidfd_open, ::getpid(), 0U);
    if (opened < 0) {
        return errno_status(
            ErrorCode::unsupported,
            "baseline PTY session containment requires pidfd_open");
    }
    if (opened > static_cast<long>(INT_MAX)) {
        static_cast<void>(::close(static_cast<int>(opened)));
        return Status{
            ErrorCode::resource_exhausted,
            "baseline PTY session-containment pidfd exceeds the host fd range"};
    }
    FileDescriptor pidfd(static_cast<int>(opened));
    if (::syscall(
            SYS_pidfd_send_signal, pidfd.get(), 0, nullptr, 0U) != 0) {
        return errno_status(
            ErrorCode::unsupported,
            "baseline PTY session containment requires pidfd_send_signal");
    }
    auto proc = open_proc_inventory(
        ErrorCode::unsupported,
        "baseline PTY session containment requires readable procfs inventory");
    if (!proc.ok()) return proc.status();
    auto self_directory =
        open_proc_process_directory(proc.value().get(), ::getpid());
    if (!self_directory.ok()) return self_directory.status();
    if (!self_directory.value()) {
        return Status{
            ErrorCode::unsupported,
            "baseline PTY session containment requires readable procfs identity"};
    }
    auto self = read_proc_process_state(
        self_directory.value()->get(), ::getpid());
    if (!self.ok()) return self.status();
    if (!self.value()) {
        return Status{
            ErrorCode::unsupported,
            "baseline PTY session containment requires readable procfs identity"};
    }
    return Status::success();
#else
    return Status{
        ErrorCode::unsupported,
        "baseline PTY session containment requires pidfd system calls"};
#endif
}

[[nodiscard]] Result<ProcessSignalDisposition> signal_verified_process(
    pid_t process, pid_t expected_session, int signal,
    int process_directory, const ProcProcessState &observed) {
#if defined(SYS_pidfd_open) && defined(SYS_pidfd_send_signal)
    const long opened = ::syscall(SYS_pidfd_open, process, 0U);
    if (opened < 0) {
        if (errno == ESRCH) return ProcessSignalDisposition::vanished;
        return errno_status(
            ErrorCode::io_error, "open verified PTY session member pidfd");
    }
    if (opened > static_cast<long>(INT_MAX)) {
        static_cast<void>(::close(static_cast<int>(opened)));
        return Status{
            ErrorCode::resource_exhausted,
            "PTY session member pidfd exceeds the host fd range"};
    }
    FileDescriptor pidfd(static_cast<int>(opened));

    // The open proc directory continues to refer to the original process
    // incarnation even after the numeric PID is reused. Re-read through that
    // descriptor after pidfd acquisition and require the independent starttime
    // witness to match before signaling through the pidfd.
    auto current = read_proc_process_state(process_directory, process);
    if (!current.ok()) return current.status();
    if (!current.value() || current.value()->session != expected_session ||
        current.value()->start_time_ticks != observed.start_time_ticks ||
        !proc_state_is_live(current.value()->state)) {
        return ProcessSignalDisposition::vanished;
    }
    if (::syscall(
            SYS_pidfd_send_signal, pidfd.get(), signal, nullptr, 0U) == 0) {
        return ProcessSignalDisposition::delivered;
    }
    if (errno == ESRCH) return ProcessSignalDisposition::vanished;
    return errno_status(
        ErrorCode::io_error, "signal verified PTY session member");
#else
    static_cast<void>(process);
    static_cast<void>(expected_session);
    static_cast<void>(signal);
    static_cast<void>(process_directory);
    static_cast<void>(observed);
    return Status{
        ErrorCode::unsupported,
        "verified PTY session signaling requires pidfd system calls"};
#endif
}

struct SessionSweep {
    std::size_t live_members{0U};
    std::size_t signaled_members{0U};
};

[[nodiscard]] Result<SessionSweep> sweep_terminal_session(
    pid_t session, int signal) {
    auto proc = open_proc_inventory(
        ErrorCode::io_error, "open PTY session inventory");
    if (!proc.ok()) return proc.status();
    FileDescriptor proc_descriptor = std::move(proc).value();
    DIR *raw_directory = ::fdopendir(proc_descriptor.get());
    if (raw_directory == nullptr) {
        return errno_status(ErrorCode::io_error, "adopt PTY session inventory");
    }
    static_cast<void>(proc_descriptor.release());
    DirectoryStream directory(raw_directory);
    const int inventory_descriptor = ::dirfd(directory.get());
    if (inventory_descriptor < 0) {
        return errno_status(
            ErrorCode::io_error, "identify PTY session inventory");
    }

    SessionSweep sweep;
    while (true) {
        errno = 0;
        dirent *entry = ::readdir(directory.get());
        if (entry == nullptr) {
            if (errno != 0) {
                return errno_status(
                    ErrorCode::io_error, "read PTY session inventory");
            }
            break;
        }
        const auto process = parse_proc_process_name(entry->d_name);
        if (!process) continue;
        auto process_directory = open_proc_process_directory(
            inventory_descriptor, *process);
        if (!process_directory.ok()) return process_directory.status();
        if (!process_directory.value()) continue;
        auto observed = read_proc_process_state(
            process_directory.value()->get(), *process);
        if (!observed.ok()) return observed.status();
        if (!observed.value() || observed.value()->session != session ||
            !proc_state_is_live(observed.value()->state)) {
            continue;
        }
        ++sweep.live_members;
        auto sent = signal_verified_process(
            *process, session, signal, process_directory.value()->get(),
            *observed.value());
        if (!sent.ok()) return sent.status();
        if (sent.value() == ProcessSignalDisposition::delivered) {
            ++sweep.signaled_members;
        }
    }
    return sweep;
}

void best_effort_kill_terminal_session(pid_t child) noexcept {
    if (child <= 0) return;
    // The waitable leader pins the session ID while repeated pidfd-backed
    // sweeps converge. The final group/leader signals remain a last-resort
    // fence if procfs becomes unavailable during teardown.
    unsigned int quiescent_sweeps = 0U;
    for (unsigned attempt = 0U; attempt < 250U; ++attempt) {
        auto swept = sweep_terminal_session(child, SIGKILL);
        if (!swept.ok()) break;
        if (swept.value().live_members == 0U) {
            quiescent_sweeps = std::min(
                quiescent_sweeps + 1U, kRequiredQuiescentSessionSweeps);
        } else {
            quiescent_sweeps = 0U;
        }
        siginfo_t information {};
        if (::waitid(
                P_PID, static_cast<id_t>(child), &information,
                WEXITED | WNOHANG | WNOWAIT) == 0 &&
            information.si_pid != 0 &&
            quiescent_sweeps >= kRequiredQuiescentSessionSweeps) {
            break;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds{1});
    }
    static_cast<void>(::kill(-child, SIGKILL));
    static_cast<void>(::kill(child, SIGKILL));
}

[[nodiscard]] bool kill_and_reap_startup_child(
    pid_t child, bool session_containment,
    detail::SessionCgroup *session_cgroup = nullptr,
    detail::CgroupAggregateAdmission::Reservation *aggregate_reservation =
        nullptr) noexcept {
    if (child <= 0) return true;
    bool cgroup_removed = session_cgroup == nullptr;
    if (session_cgroup != nullptr) {
        cgroup_removed = session_cgroup->best_effort_kill_and_remove(
            std::chrono::milliseconds{250});
        // Retain direct leader/group signals as a final startup fence if the
        // configured cgroup control files became unavailable unexpectedly.
        static_cast<void>(::kill(-child, SIGKILL));
        static_cast<void>(::kill(child, SIGKILL));
    } else if (session_containment) {
        best_effort_kill_terminal_session(child);
    } else {
        static_cast<void>(::kill(-child, SIGKILL));
        static_cast<void>(::kill(child, SIGKILL));
    }
    int status = 0;
    pid_t waited = -1;
    do {
        waited = ::waitpid(child, &status, 0);
    } while (waited < 0 && errno == EINTR);
    if (session_cgroup != nullptr) {
        cgroup_removed = session_cgroup->best_effort_kill_and_remove(
                             std::chrono::milliseconds{0}) ||
                         cgroup_removed;
        if (aggregate_reservation != nullptr) {
            if (auto outcome = session_cgroup->take_outcome()) {
                aggregate_reservation->record_outcome(*outcome);
            }
        }
    }
    return waited == child && cgroup_removed;
}

[[nodiscard]] Result<FileDescriptor> open_child_pidfd(
    pid_t child, bool required) {
#if defined(SYS_pidfd_open)
    errno = 0;
    const long opened = ::syscall(SYS_pidfd_open, child, 0U);
    if (opened >= 0) {
        if (opened > static_cast<long>(INT_MAX)) {
            static_cast<void>(::close(static_cast<int>(opened)));
            return Status{ErrorCode::resource_exhausted,
                          "PTY child pidfd exceeds the host fd range"};
        }
        FileDescriptor pidfd(static_cast<int>(opened));
        const Status cloexec = set_descriptor_cloexec(pidfd.get());
        if (!cloexec.ok()) return cloexec;
        return pidfd;
    }
    const int failure = errno;
    if (!required &&
        (failure == ENOSYS || failure == EINVAL || failure == EPERM ||
         failure == EACCES || failure == ESRCH)) {
        return FileDescriptor{};
    }
    return errno_status(
        required ? ErrorCode::unsupported : ErrorCode::io_error,
        required ? "baseline PTY session containment requires child pidfd"
                 : "open PTY child pidfd",
        failure);
#else
    static_cast<void>(child);
    if (required) {
        return Status{
            ErrorCode::unsupported,
            "baseline PTY session containment requires pidfd_open"};
    }
    return FileDescriptor{};
#endif
}

[[nodiscard]] Status set_nonblocking(int descriptor) {
    const int flags = ::fcntl(descriptor, F_GETFL);
    if (flags < 0 || ::fcntl(descriptor, F_SETFL, flags | O_NONBLOCK) != 0) {
        return errno_status(ErrorCode::io_error, "set PTY socket nonblocking");
    }
    return Status::success();
}

[[nodiscard]] int remaining_poll_milliseconds(
    std::chrono::steady_clock::time_point deadline) {
    const auto now = std::chrono::steady_clock::now();
    if (now >= deadline) return 0;
    const auto remaining = std::chrono::duration_cast<std::chrono::milliseconds>(
        deadline - now + std::chrono::milliseconds{1});
    return static_cast<int>(std::min<std::int64_t>(
        remaining.count(), std::numeric_limits<int>::max()));
}

[[nodiscard]] Status send_manifest_with_deadline(
    int descriptor, std::span<const std::uint8_t> bytes,
    std::chrono::steady_clock::time_point deadline) {
    std::size_t offset = 0U;
    while (offset < bytes.size()) {
        const ssize_t count = ::send(
            descriptor, bytes.data() + offset, bytes.size() - offset,
            MSG_NOSIGNAL);
        if (count > 0) {
            offset += static_cast<std::size_t>(count);
            continue;
        }
        if (count < 0 && errno == EINTR) continue;
        if (count < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            pollfd candidate{descriptor, POLLOUT, 0};
            const int timeout = remaining_poll_milliseconds(deadline);
            if (timeout == 0) {
                return Status{ErrorCode::timeout,
                              "PTY child manifest handoff timed out"};
            }
            const int ready = ::poll(&candidate, 1, timeout);
            if (ready > 0) continue;
            if (ready == 0) {
                return Status{ErrorCode::timeout,
                              "PTY child manifest handoff timed out"};
            }
            if (errno == EINTR) continue;
            return errno_status(ErrorCode::io_error, "poll PTY manifest socket");
        }
        return errno_status(ErrorCode::io_error, "send PTY child manifest");
    }
    if (::shutdown(descriptor, SHUT_WR) != 0) {
        return errno_status(ErrorCode::io_error, "finish PTY child manifest");
    }
    return Status::success();
}

[[nodiscard]] Result<bool> receive_status_bytes(
    int descriptor, std::span<std::uint8_t> destination,
    std::chrono::steady_clock::time_point deadline,
    std::string_view label) {
    std::size_t received = 0U;
    while (received < destination.size()) {
        const ssize_t count = ::recv(
            descriptor, destination.data() + received,
            destination.size() - received, 0);
        if (count > 0) {
            received += static_cast<std::size_t>(count);
            continue;
        }
        if (count == 0) {
            if (received == 0U) return false;
            return Status{ErrorCode::protocol_error,
                          std::string("PTY child closed a partial ") +
                              std::string(label)};
        }
        if (errno == EINTR) continue;
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            pollfd candidate{descriptor, static_cast<short>(POLLIN | POLLHUP), 0};
            const int timeout = remaining_poll_milliseconds(deadline);
            if (timeout == 0) {
                return Status{ErrorCode::timeout, "PTY child startup timed out"};
            }
            const int ready = ::poll(&candidate, 1, timeout);
            if (ready > 0) continue;
            if (ready == 0) {
                return Status{ErrorCode::timeout, "PTY child startup timed out"};
            }
            if (errno == EINTR) continue;
            return errno_status(ErrorCode::io_error, "poll PTY startup socket");
        }
        return errno_status(ErrorCode::io_error, "read PTY startup status");
    }
    return true;
}

[[nodiscard]] Result<std::optional<Status>> decode_child_error_record(
    int descriptor, std::span<const std::uint8_t, 4U> prefix,
    std::chrono::steady_clock::time_point deadline) {
    if (!std::equal(prefix.begin(), prefix.end(), kChildErrorMagic.begin())) {
        return Status{ErrorCode::protocol_error,
                      "PTY child returned an invalid startup record"};
    }
    std::array<std::uint8_t, 8U> tail{};
    auto complete = receive_status_bytes(
        descriptor, tail, deadline, "startup error record");
    if (!complete.ok()) return complete.status();
    if (!complete.value()) {
        return Status{ErrorCode::protocol_error,
                      "PTY child closed a partial startup error record"};
    }
    std::uint32_t stage_value = 0U;
    std::uint32_t error_value = 0U;
    for (unsigned index = 0U; index < 4U; ++index) {
        stage_value |= static_cast<std::uint32_t>(tail[index]) << (index * 8U);
        error_value |= static_cast<std::uint32_t>(tail[4U + index])
                       << (index * 8U);
    }
    if (!valid_child_stage(stage_value) || error_value == 0U ||
        error_value > static_cast<std::uint32_t>(INT_MAX)) {
        return Status{ErrorCode::protocol_error,
                      "PTY child returned an invalid startup error record"};
    }
    const auto stage = static_cast<ChildStage>(stage_value);
    return std::optional<Status>{errno_status(
        ErrorCode::io_error,
        std::string("PTY child setup failed at ") + child_stage_name(stage),
        static_cast<int>(error_value))};
}

[[nodiscard]] Result<std::optional<Status>> receive_child_startup(
    int descriptor, std::chrono::steady_clock::time_point deadline) {
    std::array<std::uint8_t, 4U> prefix{};
    auto first = receive_status_bytes(
        descriptor, prefix, deadline, "startup record");
    if (!first.ok()) return first.status();
    if (!first.value()) {
        return Status{ErrorCode::protocol_error,
                      "PTY helper closed before the internal child became ready"};
    }
    if (std::equal(prefix.begin(), prefix.end(), kChildErrorMagic.begin())) {
        return decode_child_error_record(descriptor, prefix, deadline);
    }
    if (!std::equal(
            prefix.begin(), prefix.end(), kChildReadyRecord.begin())) {
        return Status{ErrorCode::protocol_error,
                      "PTY child returned an invalid readiness record"};
    }
    std::array<std::uint8_t, 4U> ready_tail{};
    auto ready_complete = receive_status_bytes(
        descriptor, ready_tail, deadline, "readiness record");
    if (!ready_complete.ok()) return ready_complete.status();
    if (!ready_complete.value() ||
        !std::equal(
            ready_tail.begin(), ready_tail.end(),
            kChildReadyRecord.begin() + 4)) {
        return Status{ErrorCode::protocol_error,
                      "PTY child returned an invalid readiness record"};
    }

    auto final = receive_status_bytes(
        descriptor, prefix, deadline, "post-readiness record");
    if (!final.ok()) return final.status();
    if (!final.value()) return std::optional<Status>{};
    return decode_child_error_record(descriptor, prefix, deadline);
}

[[nodiscard]] Result<FileDescriptor> open_slave_peer(int master) {
#ifdef TIOCGPTPEER
    const int peer = ::ioctl(
        master, TIOCGPTPEER, O_RDWR | O_NOCTTY | O_CLOEXEC);
    if (peer >= 0) return FileDescriptor{peer};
    if (errno != EINVAL && errno != ENOTTY && errno != ENOSYS) {
        return errno_status(ErrorCode::io_error, "open PTY slave peer");
    }
#endif
    std::array<char, PATH_MAX> name{};
    const int named = ::ptsname_r(master, name.data(), name.size());
    if (named != 0) {
        return errno_status(ErrorCode::io_error, "name PTY slave", named);
    }
    FileDescriptor slave(::open(
        name.data(), O_RDWR | O_NOCTTY | O_CLOEXEC | O_NOFOLLOW));
    if (slave.get() < 0) {
        return errno_status(ErrorCode::io_error, "open PTY slave");
    }
    return slave;
}

[[nodiscard]] Status add_dup_and_close(
    posix_spawn_file_actions_t *actions, int source, int destination) {
    int error = ::posix_spawn_file_actions_adddup2(actions, source, destination);
    if (error != 0) return spawn_error("add PTY spawn dup2 action", error);
    return Status::success();
}

[[nodiscard]] Status configure_spawn_actions(
    posix_spawn_file_actions_t *actions, int slave, int configuration,
    int status, int executable, int working_directory) {
    const std::array mappings{
        std::pair{slave, STDIN_FILENO},
        std::pair{slave, STDOUT_FILENO},
        std::pair{slave, STDERR_FILENO},
        std::pair{configuration, kConfigurationDescriptor},
        std::pair{status, kStatusDescriptor},
        std::pair{executable, kExecutableDescriptor},
        std::pair{working_directory, kWorkingDirectoryDescriptor},
    };
    for (const auto &[source, destination] : mappings) {
        const Status added = add_dup_and_close(actions, source, destination);
        if (!added.ok()) return added;
    }
    const std::array sources{slave, configuration, status, executable, working_directory};
    for (const int source : sources) {
        const int error = ::posix_spawn_file_actions_addclose(actions, source);
        if (error != 0) return spawn_error("add PTY spawn close action", error);
    }
    return Status::success();
}

[[nodiscard]] Status configure_spawn_attributes(posix_spawnattr_t *attributes) {
    sigset_t empty_mask {};
    sigset_t defaults {};
    if (::sigemptyset(&empty_mask) != 0 || ::sigfillset(&defaults) != 0 ||
        ::sigdelset(&defaults, SIGKILL) != 0 ||
        ::sigdelset(&defaults, SIGSTOP) != 0) {
        return errno_status(ErrorCode::io_error, "initialize PTY spawn signal sets");
    }
    int error = ::posix_spawnattr_setsigmask(attributes, &empty_mask);
    if (error != 0) return spawn_error("set PTY spawn signal mask", error);
    error = ::posix_spawnattr_setsigdefault(attributes, &defaults);
    if (error != 0) return spawn_error("set PTY spawn signal defaults", error);
    const short flags = static_cast<short>(
        POSIX_SPAWN_SETSIGMASK | POSIX_SPAWN_SETSIGDEF);
    error = ::posix_spawnattr_setflags(attributes, flags);
    if (error != 0) return spawn_error("set PTY spawn flags", error);
    return Status::success();
}

[[nodiscard]] ProcessExit decode_wait_status(int status) {
    if (WIFEXITED(status)) {
        return ProcessExit{ExitKind::exited, WEXITSTATUS(status), false};
    }
    bool core_dumped = false;
#ifdef WCOREDUMP
    core_dumped = WCOREDUMP(status) != 0;
#endif
    return ProcessExit{ExitKind::signaled, WTERMSIG(status), core_dumped};
}

class PosixPtyProcess final : public PtyProcess {
  public:
    PosixPtyProcess(
        FileDescriptor master, FileDescriptor pidfd, pid_t child,
        bool session_containment,
        std::optional<detail::SessionCgroup> session_cgroup,
        detail::CgroupAggregateAdmission::Reservation aggregate_reservation)
        : master_(std::move(master)), pidfd_(std::move(pidfd)),
          child_(child), session_(child),
          session_containment_(session_containment),
          session_cgroup_(std::move(session_cgroup)),
          aggregate_reservation_(std::move(aggregate_reservation)) {}

    ~PosixPtyProcess() override {
        if (!exit_) {
            bool cgroup_removed = !session_cgroup_.has_value();
            if (session_cgroup_) {
                cgroup_removed = session_cgroup_->best_effort_kill_and_remove(
                    std::chrono::milliseconds{250});
                static_cast<void>(::kill(-child_, SIGKILL));
                static_cast<void>(::kill(child_, SIGKILL));
            } else if (session_containment_) {
                best_effort_kill_terminal_session(child_);
            } else {
                static_cast<void>(::kill(-child_, SIGKILL));
                static_cast<void>(::kill(child_, SIGKILL));
            }
            int status = 0;
            pid_t waited = -1;
            do {
                waited = ::waitpid(child_, &status, 0);
            } while (waited < 0 && errno == EINTR);
            if (session_cgroup_) {
                cgroup_removed =
                    session_cgroup_->best_effort_kill_and_remove(
                        std::chrono::milliseconds{0}) ||
                    cgroup_removed;
                if (auto outcome = session_cgroup_->take_outcome()) {
                    aggregate_reservation_.record_outcome(*outcome);
                }
            }
            if (waited == child_ && cgroup_removed) {
                aggregate_reservation_.release();
            } else {
                aggregate_reservation_.strand();
            }
        }
    }

    Result<WriteResult> write(std::span<const std::uint8_t> bytes) override {
        if (bytes.size() > kMaximumTerminalIoChunk) {
            return Status{ErrorCode::resource_exhausted,
                          "PTY write exceeds the per-call byte bound"};
        }
        if (input_closed_) return WriteResult{IoDisposition::closed, 0U};
        if (bytes.empty()) return WriteResult{IoDisposition::progress, 0U};
        const ssize_t count = ::write(master_.get(), bytes.data(), bytes.size());
        if (count > 0) {
            return WriteResult{
                IoDisposition::progress, static_cast<std::size_t>(count)};
        }
        if (count < 0 && errno == EINTR) {
            return WriteResult{IoDisposition::would_block, 0U};
        }
        if (count < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
            return WriteResult{IoDisposition::would_block, 0U};
        }
        if (count < 0 && (errno == EIO || errno == EPIPE)) {
            input_closed_ = true;
            return WriteResult{IoDisposition::closed, 0U};
        }
        return errno_status(ErrorCode::io_error, "write PTY master");
    }

    Result<ReadResult> read(std::size_t maximum_bytes) override {
        if (maximum_bytes == 0U || maximum_bytes > kMaximumTerminalIoChunk) {
            return Status{ErrorCode::invalid_argument,
                          "PTY read bound is outside the per-call limit"};
        }
        if (output_closed_) return ReadResult{IoDisposition::closed, {}};
        std::vector<std::uint8_t> bytes(maximum_bytes);
        const ssize_t count = ::read(master_.get(), bytes.data(), bytes.size());
        if (count > 0) {
            bytes.resize(static_cast<std::size_t>(count));
            return ReadResult{IoDisposition::progress, std::move(bytes)};
        }
        if (count == 0 || (count < 0 && errno == EIO)) {
            output_closed_ = true;
            return ReadResult{IoDisposition::closed, {}};
        }
        if (count < 0 && (errno == EINTR || errno == EAGAIN || errno == EWOULDBLOCK)) {
            return ReadResult{IoDisposition::would_block, {}};
        }
        return errno_status(ErrorCode::io_error, "read PTY master");
    }

    Status resize(const Dimensions &dimensions) override {
        const Status valid = validate_dimensions(dimensions);
        if (!valid.ok()) return valid;
        winsize window{};
        window.ws_col = dimensions.columns;
        window.ws_row = dimensions.rows;
        if (::ioctl(master_.get(), TIOCSWINSZ, &window) != 0) {
            return errno_status(ErrorCode::io_error, "resize PTY window");
        }
        return Status::success();
    }

    Status send_signal(ProcessSignal signal) override {
        const int number = signal_number(signal);
        if (number == 0) {
            return Status{ErrorCode::invalid_argument,
                          "PTY signal request is unassigned"};
        }
        if (exit_) return Status::success();
        if (!session_containment_) {
            if (::kill(-child_, number) != 0 && errno != ESRCH) {
                return errno_status(
                    ErrorCode::io_error, "signal PTY process group");
            }
            return Status::success();
        }
        if (signal == ProcessSignal::kill && session_cgroup_) {
            const Status killed = session_cgroup_->kill_all();
            if (!killed.ok()) {
                static_cast<void>(::kill(-child_, number));
                static_cast<void>(::kill(child_, number));
                return killed;
            }
            session_kill_active_ = true;
            return Status::success();
        }
        auto swept = sweep_terminal_session(session_, number);
        if (!swept.ok()) {
            // The pinned leader group remains a safe last-resort target, but a
            // failed pidfd/procfs sweep is surfaced rather than pretending the
            // complete baseline session was signaled.
            static_cast<void>(::kill(-child_, number));
            static_cast<void>(::kill(child_, number));
            return swept.status();
        }
        if (signal == ProcessSignal::kill) {
            session_kill_active_ = true;
            account_kill_sweep(swept.value());
        } else {
            quiescent_kill_sweeps_ = 0U;
        }
        return Status::success();
    }

    Result<std::optional<ProcessExit>> poll_exit() override {
        if (exit_) return exit_;
        if (session_kill_active_ && !session_cgroup_) {
            auto swept = sweep_terminal_session(session_, SIGKILL);
            if (!swept.ok()) return swept.status();
            account_kill_sweep(swept.value());
        }
        siginfo_t information {};
        int observed = -1;
        if (pidfd_.get() >= 0) {
            observed = ::waitid(
                kLinuxPidfdWaitIdType,
                static_cast<id_t>(pidfd_.get()), &information,
                WEXITED | WNOHANG | WNOWAIT);
            if (observed != 0 && (errno == EINVAL || errno == ENOSYS)) {
                // pidfd_open predates P_PIDFD wait support on a narrow kernel
                // range. The still-waitable direct child pins the same identity.
                information = {};
                observed = ::waitid(
                    P_PID, static_cast<id_t>(child_), &information,
                    WEXITED | WNOHANG | WNOWAIT);
            }
        } else {
            observed = ::waitid(
                P_PID, static_cast<id_t>(child_), &information,
                WEXITED | WNOHANG | WNOWAIT);
        }
        if (observed != 0) {
            if (errno == EINTR) return std::optional<ProcessExit>{};
            return errno_status(ErrorCode::io_error, "observe PTY child exit");
        }
        if (information.si_pid == 0) return std::optional<ProcessExit>{};
        if (session_cgroup_) {
            if (!session_kill_active_) {
                const Status killed = session_cgroup_->kill_all();
                if (!killed.ok()) return killed;
                session_kill_active_ = true;
            }
            auto is_populated = session_cgroup_->populated();
            if (!is_populated.ok()) return is_populated.status();
            if (is_populated.value()) {
                return std::optional<ProcessExit>{};
            }
            const Status removed = session_cgroup_->remove_if_empty();
            if (!removed.ok()) return removed;
            if (auto outcome = session_cgroup_->take_outcome()) {
                aggregate_reservation_.record_outcome(*outcome);
            }
            // cgroup.events is recursive and excludes zombies. Keeping the
            // leader waitable until populated=0 therefore pins its identity
            // while the kernel proves that no live descendant remains.
        } else if (session_containment_) {
            if (!session_kill_active_) {
                session_kill_active_ = true;
                auto swept = sweep_terminal_session(session_, SIGKILL);
                if (!swept.ok()) return swept.status();
                account_kill_sweep(swept.value());
            }
            if (quiescent_kill_sweeps_ < kRequiredQuiescentSessionSweeps) {
                return std::optional<ProcessExit>{};
            }
            // The leader remains waitable until repeated complete procfs
            // inventories agree that every executable member disappeared. This
            // closes the one-empty-scan fork race while keeping the numeric
            // session ID pinned across inventory, signaling, and reap.
        } else {
            // Canonical v1 compatibility retains the historical process-group
            // lifecycle rather than silently acquiring baseline semantics.
            static_cast<void>(::kill(-child_, SIGKILL));
        }
        int status = 0;
        pid_t waited = -1;
        do {
            waited = ::waitpid(child_, &status, 0);
        } while (waited < 0 && errno == EINTR);
        if (waited != child_) {
            return errno_status(ErrorCode::io_error, "reap PTY child");
        }
        exit_ = decode_wait_status(status);
        aggregate_reservation_.release();
        return exit_;
    }

  private:
    void account_kill_sweep(const SessionSweep &sweep) noexcept {
        if (sweep.live_members == 0U) {
            quiescent_kill_sweeps_ = std::min(
                quiescent_kill_sweeps_ + 1U,
                kRequiredQuiescentSessionSweeps);
        } else {
            quiescent_kill_sweeps_ = 0U;
        }
    }

    FileDescriptor master_;
    FileDescriptor pidfd_;
    pid_t child_{-1};
    pid_t session_{-1};
    bool input_closed_{false};
    bool output_closed_{false};
    bool session_containment_{false};
    bool session_kill_active_{false};
    unsigned int quiescent_kill_sweeps_{0U};
    std::optional<detail::SessionCgroup> session_cgroup_;
    detail::CgroupAggregateAdmission::Reservation aggregate_reservation_;
    std::optional<ProcessExit> exit_;
};

}  // namespace

PosixPtyProcessFactory::PosixPtyProcessFactory(PosixPtyOptions options)
    : options_(std::move(options)) {
    auto admission = detail::CgroupAggregateAdmission::create(
        options_.cgroup_aggregate_limits);
    if (!admission.ok()) {
        cgroup_configuration_status_ = admission.status();
        return;
    }
    aggregate_admission_ = std::move(admission).value();
    auto pressure_admission = detail::CgroupPressureAdmission::create(
        options_.delegated_cgroup_root,
        options_.cgroup_pressure_admission_limits);
    if (!pressure_admission.ok()) {
        cgroup_configuration_status_ = pressure_admission.status();
        return;
    }
    pressure_admission_ = std::move(pressure_admission).value();
}

Status PosixPtyProcessFactory::configuration_status() const {
    return cgroup_configuration_status_;
}

detail::CgroupAggregateSnapshot
PosixPtyProcessFactory::aggregate_snapshot() const {
    detail::CgroupAggregateSnapshot snapshot;
    if (!aggregate_admission_) {
        snapshot.limits = options_.cgroup_aggregate_limits;
    } else {
        snapshot = aggregate_admission_->snapshot();
    }
    if (!pressure_admission_) {
        snapshot.pressure_admission.limits =
            options_.cgroup_pressure_admission_limits;
    } else {
        snapshot.pressure_admission = pressure_admission_->snapshot();
    }
    return snapshot;
}

Result<std::unique_ptr<PtyProcess>> PosixPtyProcessFactory::spawn(
    const ResolvedProfile &profile) {
    if (!cgroup_configuration_status_.ok()) {
        return cgroup_configuration_status_;
    }
    const Status timeout_valid = validate_startup_timeout(options_.startup_timeout);
    if (!timeout_valid.ok()) return timeout_valid;
    const Status profile_valid = validate_resolved_profile(profile);
    if (!profile_valid.ok()) return profile_valid;
    if (profile.profile.allow_privilege_escalation) {
        const bool starts_as_root =
            profile.profile.identity.mode == IdentityMode::inherit
                ? ::geteuid() == 0
                : profile.profile.identity.uid == 0U;
        if (starts_as_root) {
            return Status{
                ErrorCode::invalid_argument,
                "sudo-capable Ratox profile must start from a non-root identity"};
        }
    }
    if ((profile.profile.identity.mode == IdentityMode::inherit ||
         (profile.profile.identity.mode == IdentityMode::account &&
          profile.profile.identity.uid ==
              static_cast<std::uint64_t>(::geteuid()))) &&
        profile.profile.limits.processes != 0U) {
        return Status{
            ErrorCode::invalid_argument,
            "daemon-account PTY identity cannot safely use per-UID RLIMIT_NPROC; set limit-processes=0 or use delegated cgroup pids.max"};
    }
    auto effective_limits = compose_cgroup_resource_limits(
        options_.cgroup_resource_limits,
        profile.profile.cgroup_limits);
    if (!effective_limits.ok()) return effective_limits.status();
    const bool session_containment =
        profile.profile.confinement != ConfinementMode::compatibility;
    if (options_.delegated_cgroup_root.empty() &&
        !effective_limits.value().empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox host or profile cgroup resource limits require a delegated cgroup root"};
    }
    if (options_.delegated_cgroup_root.empty() &&
        !options_.cgroup_aggregate_limits.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox aggregate cgroup reservations require a delegated cgroup root"};
    }
    if (options_.delegated_cgroup_root.empty() &&
        !options_.cgroup_pressure_admission_limits.empty()) {
        return Status{
            ErrorCode::invalid_argument,
            "Ratox cgroup pressure admission requires a delegated cgroup root"};
    }
    if (!options_.delegated_cgroup_root.empty()) {
        if (!session_containment) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup containment is unavailable for compatibility profiles"};
        }
        if (profile.profile.identity.mode != IdentityMode::exact ||
            !profile.profile.identity.clear_supplementary_groups ||
            profile.profile.identity.uid == 0U ||
            profile.profile.identity.uid ==
                static_cast<std::uint64_t>(::geteuid())) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup containment requires a non-root exact PTY uid distinct from the daemon with supplementary groups cleared"};
        }
        const std::filesystem::path &root = options_.delegated_cgroup_root;
        if (!root.is_absolute() || root == "/" ||
            root.lexically_normal() != root) {
            return Status{
                ErrorCode::invalid_argument,
                "Ratox cgroup root must be a normalized non-root absolute path"};
        }
    }
    if (session_containment) {
        const Status supported = verify_session_signal_support();
        if (!supported.ok()) return supported;
    }
    if (!aggregate_admission_) {
        return Status{
            ErrorCode::internal_error,
            "Ratox aggregate cgroup admission controller is unavailable"};
    }
    if (!pressure_admission_) {
        return Status{
            ErrorCode::internal_error,
            "Ratox cgroup pressure admission controller is unavailable"};
    }
    const Status pressure_admitted = pressure_admission_->admit();
    if (!pressure_admitted.ok()) return pressure_admitted;
    auto reserved = aggregate_admission_->reserve(effective_limits.value());
    if (!reserved.ok()) return reserved.status();
    auto aggregate_reservation = std::move(reserved).value();
    if (!options_.helper_executable.is_absolute()) {
        return Status{ErrorCode::invalid_argument,
                      "PTY helper executable must be an absolute path"};
    }
    auto manifest = encode_manifest(profile);
    if (!manifest.ok()) return manifest.status();
    auto helper = open_secure_executable(
        options_.helper_executable, "PTY helper executable");
    if (!helper.ok()) return helper.status();
    std::optional<uid_t> profile_executable_owner;
    if (profile.profile.identity.mode == IdentityMode::account) {
        const uid_t owner =
            static_cast<uid_t>(profile.profile.identity.uid);
        if (static_cast<std::uint64_t>(owner) !=
            profile.profile.identity.uid) {
            return Status{
                ErrorCode::invalid_argument,
                "PTY account executable owner is not representable on this host"};
        }
        profile_executable_owner = owner;
    }
    auto executable = open_secure_executable(
        profile.profile.arguments.front(), "PTY profile executable",
        profile_executable_owner);
    if (!executable.ok()) return executable.status();
    if (profile.profile.executable_sha256.has_value()) {
        const Status pinned = verify_executable_digest(
            executable.value().get(), *profile.profile.executable_sha256,
            "PTY profile executable");
        if (!pinned.ok()) return pinned;
    }
    std::optional<FileDescriptor> toolbox_executable;
    if (profile.profile.toolbox_sha256.has_value()) {
        const auto toolbox = std::find_if(
            profile.profile.environment.begin(),
            profile.profile.environment.end(),
            [](const EnvironmentEntry &entry) {
                return entry.name == "IOTOX_RESCUE_TOOLBOX";
            });
        if (toolbox == profile.profile.environment.end()) {
            return Status{
                ErrorCode::internal_error,
                "validated PTY toolbox digest lost its directory"};
        }
        auto opened_toolbox = open_secure_executable(
            std::filesystem::path(toolbox->value) / "toybox",
            "PTY toolbox executable", profile_executable_owner);
        if (!opened_toolbox.ok()) return opened_toolbox.status();
        const Status pinned = verify_executable_digest(
            opened_toolbox.value().get(), *profile.profile.toolbox_sha256,
            "PTY toolbox executable");
        if (!pinned.ok()) return pinned;
        toolbox_executable.emplace(std::move(opened_toolbox.value()));
    }
    auto working_directory = open_secure_working_directory(
        profile.profile.working_directory);
    if (!working_directory.ok()) return working_directory.status();

    FileDescriptor master(::posix_openpt(
        O_RDWR | O_NOCTTY | O_CLOEXEC | O_NONBLOCK));
    if (master.get() < 0) {
        return errno_status(ErrorCode::io_error, "open PTY master");
    }
    if (::grantpt(master.get()) != 0) {
        return errno_status(ErrorCode::io_error, "grant PTY slave");
    }
    if (::unlockpt(master.get()) != 0) {
        return errno_status(ErrorCode::io_error, "unlock PTY slave");
    }
    auto slave = open_slave_peer(master.get());
    if (!slave.ok()) return slave.status();

    int configuration_pair[2]{-1, -1};
    int status_pair[2]{-1, -1};
    if (::socketpair(
            AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC,
            0, configuration_pair) != 0) {
        return errno_status(ErrorCode::io_error, "create PTY manifest socket");
    }
    FileDescriptor configuration_parent(configuration_pair[0]);
    FileDescriptor configuration_child(configuration_pair[1]);
    if (::socketpair(
            AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC,
            0, status_pair) != 0) {
        return errno_status(ErrorCode::io_error, "create PTY status socket");
    }
    FileDescriptor status_parent(status_pair[0]);
    FileDescriptor status_child(status_pair[1]);
    Status nonblocking = set_nonblocking(configuration_parent.get());
    if (!nonblocking.ok()) return nonblocking;
    nonblocking = set_nonblocking(status_parent.get());
    if (!nonblocking.ok()) return nonblocking;

    // Keep the helper executable on a high descriptor that none of the
    // posix_spawn dup2 actions can overwrite before /proc/self/fd is resolved.
    auto spawn_helper = duplicate_spawn_source(helper.value().get());
    if (!spawn_helper.ok()) return spawn_helper.status();
    auto spawn_slave = duplicate_spawn_source(slave.value().get());
    if (!spawn_slave.ok()) return spawn_slave.status();
    auto spawn_configuration = duplicate_spawn_source(configuration_child.get());
    if (!spawn_configuration.ok()) return spawn_configuration.status();
    auto spawn_status = duplicate_spawn_source(status_child.get());
    if (!spawn_status.ok()) return spawn_status.status();
    auto spawn_executable = duplicate_spawn_source(executable.value().get());
    if (!spawn_executable.ok()) return spawn_executable.status();
    auto spawn_working_directory = duplicate_spawn_source(
        working_directory.value().get());
    if (!spawn_working_directory.ok()) return spawn_working_directory.status();

    SpawnFileActions actions;
    if (actions.error() != 0) {
        return spawn_error("initialize PTY spawn actions", actions.error());
    }
    const Status actions_valid = configure_spawn_actions(
        actions.get(), spawn_slave.value().get(), spawn_configuration.value().get(),
        spawn_status.value().get(), spawn_executable.value().get(),
        spawn_working_directory.value().get());
    if (!actions_valid.ok()) return actions_valid;

    SpawnAttributes attributes;
    if (attributes.error() != 0) {
        return spawn_error("initialize PTY spawn attributes", attributes.error());
    }
    const Status attributes_valid = configure_spawn_attributes(attributes.get());
    if (!attributes_valid.ok()) return attributes_valid;

    std::optional<detail::SessionCgroup> session_cgroup;
    if (!options_.delegated_cgroup_root.empty()) {
        auto created = detail::SessionCgroup::create(
            options_.delegated_cgroup_root, profile.profile.identity,
            effective_limits.value());
        if (!created.ok()) return created.status();
        session_cgroup.emplace(std::move(created).value());
    }

    const std::string helper_path =
        "/proc/self/fd/" + std::to_string(spawn_helper.value().get());
    std::array<std::string, 2U> argument_storage{
        std::string{"iotox-terminal-child"},
        std::string{kInternalTerminalChildArgument}};
    std::array<char *, 3U> arguments{
        argument_storage[0U].data(), argument_storage[1U].data(), nullptr};
    std::array<std::string, 1U> environment_storage{
        std::string{"IOTOX_INTERNAL_TERMINAL_CHILD=1"}};
    std::array<char *, 2U> environment{
        environment_storage[0U].data(), nullptr};

    pid_t child = -1;
    const int spawned = ::posix_spawn(
        &child, helper_path.c_str(), actions.get(), attributes.get(),
        arguments.data(), environment.data());
    if (spawned != 0) {
        return spawn_error("spawn PTY helper", spawned);
    }
    if (session_cgroup) {
        const Status attached = session_cgroup->attach(child);
        if (!attached.ok()) {
            if (!kill_and_reap_startup_child(
                    child, session_containment, &*session_cgroup,
                    &aggregate_reservation)) {
                aggregate_reservation.strand();
            }
            return attached;
        }
    }
    auto child_pidfd = open_child_pidfd(child, session_containment);
    if (!child_pidfd.ok()) {
        if (!kill_and_reap_startup_child(
                child, session_containment,
                session_cgroup ? &*session_cgroup : nullptr,
                &aggregate_reservation)) {
            aggregate_reservation.strand();
        }
        return child_pidfd.status();
    }

    // The duplicated source descriptors exist only to make the file actions
    // collision-proof. Keeping the child-side status duplicate open in the
    // parent would suppress the EOF that proves the final exec succeeded.
    spawn_helper.value().reset();
    spawn_slave.value().reset();
    spawn_configuration.value().reset();
    spawn_status.value().reset();
    spawn_executable.value().reset();
    spawn_working_directory.value().reset();
    configuration_child.reset();
    status_child.reset();
    slave.value().reset();
    const auto deadline = std::chrono::steady_clock::now() + options_.startup_timeout;
    const Status sent = send_manifest_with_deadline(
        configuration_parent.get(), manifest.value(), deadline);
    if (!sent.ok()) {
        // A helper that exits without implementing the child protocol can race
        // the manifest write: the parent may observe EPIPE/ECONNRESET before it
        // observes EOF on the independent status channel. Always consult that
        // channel before classifying the failure so a closed or malformed helper
        // is deterministically reported as a protocol error and a genuine child
        // setup record is not lost behind the configuration-socket race.
        configuration_parent.reset();
        auto startup_after_send_failure = receive_child_startup(
            status_parent.get(), deadline);
        if (!kill_and_reap_startup_child(
                child, session_containment,
                session_cgroup ? &*session_cgroup : nullptr,
                &aggregate_reservation)) {
            aggregate_reservation.strand();
        }
        if (startup_after_send_failure.ok()) {
            if (startup_after_send_failure.value()) {
                return *startup_after_send_failure.value();
            }
            return sent;
        }
        if (startup_after_send_failure.status().code() ==
            ErrorCode::protocol_error) {
            return startup_after_send_failure.status();
        }
        return sent;
    }
    configuration_parent.reset();
    auto startup = receive_child_startup(status_parent.get(), deadline);
    if (!startup.ok()) {
        if (!kill_and_reap_startup_child(
                child, session_containment,
                session_cgroup ? &*session_cgroup : nullptr,
                &aggregate_reservation)) {
            aggregate_reservation.strand();
        }
        return startup.status();
    }
    if (startup.value()) {
        if (!kill_and_reap_startup_child(
                child, session_containment,
                session_cgroup ? &*session_cgroup : nullptr,
                &aggregate_reservation)) {
            aggregate_reservation.strand();
        }
        return *startup.value();
    }
    status_parent.reset();
    return std::unique_ptr<PtyProcess>(new PosixPtyProcess(
        std::move(master), std::move(child_pidfd.value()), child,
        session_containment, std::move(session_cgroup),
        std::move(aggregate_reservation)));
}

int run_internal_terminal_child() noexcept {
    try {
        const char *marker = ::getenv("IOTOX_INTERNAL_TERMINAL_CHILD");
        if (marker == nullptr || std::string_view(marker) != "1") {
            child_fail(ChildStage::marker, EPERM);
        }
        for (int descriptor = kConfigurationDescriptor;
             descriptor <= kWorkingDirectoryDescriptor; ++descriptor) {
            const Status cloexec = set_descriptor_cloexec(descriptor);
            if (!cloexec.ok()) {
                child_fail(ChildStage::status_descriptor, errno);
            }
        }
        auto expected_parent = validate_child_descriptor_contract();
        if (!expected_parent.ok()) {
            child_fail(ChildStage::descriptor_contract, EPROTO);
        }
        const Status initial_dumpable_guard = arm_dumpable_guard();
        if (!initial_dumpable_guard.ok()) {
            child_fail(ChildStage::dumpable_guard, EPERM);
        }
        const Status parent_death = arm_parent_death_contract(
            expected_parent.value());
        if (!parent_death.ok()) {
            child_fail(ChildStage::parent_death, EPIPE);
        }
        auto bytes = read_manifest_from_child_fd();
        if (!bytes.ok()) child_fail(ChildStage::manifest_read, EPROTO);
        auto resolved = decode_manifest(bytes.value());
        if (!resolved.ok()) child_fail(ChildStage::manifest_decode, EPROTO);

        std::vector<char *> arguments;
        arguments.reserve(resolved.value().profile.arguments.size() + 1U);
        for (std::string &argument : resolved.value().profile.arguments) {
            arguments.push_back(argument.data());
        }
        arguments.push_back(nullptr);
        std::vector<std::string> environment_storage;
        environment_storage.reserve(resolved.value().environment.size());
        for (const EnvironmentEntry &entry : resolved.value().environment) {
            environment_storage.push_back(entry.name + "=" + entry.value);
        }
        std::vector<char *> environment;
        environment.reserve(environment_storage.size() + 1U);
        for (std::string &entry : environment_storage) {
            environment.push_back(entry.data());
        }
        environment.push_back(nullptr);

        if (::setsid() < 0) child_fail(ChildStage::session, errno);
        if (::ioctl(STDIN_FILENO, TIOCSCTTY, 0) != 0) {
            child_fail(ChildStage::controlling_terminal, errno);
        }
        winsize window{};
        window.ws_col = resolved.value().accepted_dimensions.columns;
        window.ws_row = resolved.value().accepted_dimensions.rows;
        if (::ioctl(STDIN_FILENO, TIOCSWINSZ, &window) != 0) {
            child_fail(ChildStage::window, errno);
        }
        if (::tcsetpgrp(STDIN_FILENO, ::getpgrp()) != 0) {
            child_fail(ChildStage::foreground_group, errno);
        }
        std::optional<uid_t> profile_executable_owner;
        if (resolved.value().profile.identity.mode == IdentityMode::account) {
            profile_executable_owner = static_cast<uid_t>(
                resolved.value().profile.identity.uid);
        }
        const Status executable = validate_executable_descriptor(
            kExecutableDescriptor, "PTY child executable",
            profile_executable_owner);
        if (!executable.ok()) child_fail(ChildStage::executable, EACCES);
        if (::fchdir(kWorkingDirectoryDescriptor) != 0) {
            child_fail(ChildStage::working_directory, errno);
        }
        const Status limits = apply_resource_limits(resolved.value().profile.limits);
        if (!limits.ok()) child_fail(ChildStage::resource_limits, EINVAL);
        const bool allow_privilege_escalation =
            resolved.value().profile.allow_privilege_escalation;
        if (allow_privilege_escalation) {
            const Status prerequisites =
                verify_privilege_escalation_prerequisites();
            if (!prerequisites.ok()) {
                child_fail(ChildStage::no_new_privileges, EPERM);
            }
        } else {
            const Status no_new_privileges = arm_no_new_privileges();
            if (!no_new_privileges.ok()) {
                child_fail(ChildStage::no_new_privileges, EPERM);
            }
        }
        const StagedCapabilityBoundary capability_boundary =
            prepare_capability_boundary(!allow_privilege_escalation);
        if (!capability_boundary.ok()) {
            child_fail(capability_boundary.failed_stage, EPERM);
        }
        const Status identity = apply_identity(resolved.value().profile.identity);
        if (!identity.ok()) child_fail(ChildStage::identity, EPERM);
        const StagedStatus final_capabilities = finalize_capability_boundary(
            capability_boundary.boundary);
        if (!final_capabilities.ok()) {
            child_fail(final_capabilities.failed_stage, EPERM);
        }
        const Status final_dumpable_guard = arm_dumpable_guard();
        if (!final_dumpable_guard.ok()) {
            child_fail(ChildStage::dumpable_guard, EPERM);
        }
        const Status rearmed_parent_death = arm_parent_death_contract(
            expected_parent.value());
        if (!rearmed_parent_death.ok()) {
            child_fail(ChildStage::parent_death, EPIPE);
        }
        const ConfinementMode confinement =
            resolved.value().profile.confinement;
        if (confinement == ConfinementMode::strict) {
            const Status mdwe = arm_memory_deny_write_execute();
            if (!mdwe.ok()) child_fail(ChildStage::mdwe, EOPNOTSUPP);
            const Status landlock = apply_strict_landlock();
            if (!landlock.ok()) {
                child_fail(ChildStage::landlock, EOPNOTSUPP);
            }
        }
        if (confinement == ConfinementMode::baseline ||
            confinement == ConfinementMode::strict) {
            const Status seccomp = install_baseline_seccomp();
            if (!seccomp.ok()) child_fail(ChildStage::seccomp, EPERM);
        }
        ::umask(static_cast<mode_t>(0077));
        const Status closed = close_unreserved_descriptors();
        if (!closed.ok()) child_fail(ChildStage::descriptor_hygiene, EIO);
        child_announce_ready();
        ::fexecve(
            kExecutableDescriptor, arguments.data(), environment.data());
        child_fail(ChildStage::final_exec, errno);
    } catch (...) {
        child_fail(ChildStage::internal_exception, ENOMEM);
    }
}

}  // namespace iotox::terminal
