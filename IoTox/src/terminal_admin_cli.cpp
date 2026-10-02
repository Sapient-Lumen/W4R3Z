#include "iotox/terminal_admin_cli.hpp"

#include "iotox/cli_registry.hpp"
#include "iotox/security/sodium.hpp"
#include "iotox/state_store.hpp"
#include "iotox/sync_digest.hpp"
#include "iotox/terminal_profile.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <optional>
#include <sstream>
#include <span>
#include <string>
#include <string_view>
#include <array>
#include <fcntl.h>
#include <linux/capability.h>
#include <linux/filter.h>
#include <linux/landlock.h>
#include <linux/securebits.h>
#include <linux/seccomp.h>
#include <grp.h>
#include <pwd.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/vfs.h>
#include <sys/wait.h>
#include <sys/xattr.h>
#include <unistd.h>
#include <vector>

namespace iotox {
namespace {

constexpr std::array<std::string_view, kTerminalCgroupInterfaceCount>
    kCgroupInterfaces{
        "cgroup.kill", "cgroup.freeze", "pids.max", "memory.high",
        "memory.max", "memory.swap.max", "cpu.max", "io.max",
        "cpu.pressure", "memory.pressure", "io.pressure", "irq.pressure"};

std::filesystem::path current_cgroup_root() {
    std::ifstream input("/proc/self/cgroup");
    std::string line;
    while (std::getline(input, line)) {
        constexpr std::string_view prefix{"0::/"};
        if (!line.starts_with(prefix)) continue;
        const std::filesystem::path relative =
            std::filesystem::path(line.substr(prefix.size())).lexically_normal();
        for (const auto &component : relative) {
            if (component == "..") return "/sys/fs/cgroup";
        }
        return std::filesystem::path{"/sys/fs/cgroup"} / relative;
    }
    return "/sys/fs/cgroup";
}

struct AdminArguments {
    std::filesystem::path store;
    std::filesystem::path cgroup_root{current_cgroup_root()};
    std::optional<std::filesystem::path> shell_override;
    std::optional<std::filesystem::path> toolbox_directory;
    std::uint32_t owner_uid{0U};
    bool allow_sudo{false};
    std::vector<std::string_view> positional;
};

bool is_admin_command(std::string_view value) noexcept {
    return is_cli_command_kind(value, CliCommandKind::terminal_admin);
}

Result<std::uint32_t> parse_uid(std::string_view text) {
    if (text.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "--ratox-profile-owner-uid requires decimal digits"};
    }
    std::uint64_t value = 0U;
    for (const char character : text) {
        if (character < '0' || character > '9') {
            return Status{ErrorCode::invalid_argument,
                          "--ratox-profile-owner-uid requires decimal digits"};
        }
        const std::uint64_t digit =
            static_cast<std::uint64_t>(character - '0');
        if (value > (std::numeric_limits<std::uint32_t>::max() - digit) / 10U) {
            return Status{ErrorCode::invalid_argument,
                          "--ratox-profile-owner-uid must fit uint32"};
        }
        value = value * 10U + digit;
    }
    return static_cast<std::uint32_t>(value);
}

Result<AdminArguments> parse_arguments(
    std::span<const std::string_view> arguments) {
    AdminArguments parsed;
    const std::uint64_t effective_uid = static_cast<std::uint64_t>(::geteuid());
    if (effective_uid > std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::unsupported,
                      "effective UID cannot be represented by the terminal profile store"};
    }
    parsed.owner_uid = static_cast<std::uint32_t>(effective_uid);
    for (std::size_t index = 0U; index < arguments.size(); ++index) {
        const std::string_view argument = arguments[index];
        if (argument == "--ratox-profile-store" ||
            argument == "--ratox-cgroup-root" ||
            argument == "--ratox-profile-owner-uid" ||
            argument == "--shell" ||
            argument == "--toolbox-dir") {
            if (index + 1U >= arguments.size()) {
                return Status{ErrorCode::invalid_argument,
                              std::string(argument) + " requires a value"};
            }
            const std::string_view value = arguments[++index];
            if (argument == "--ratox-profile-store") {
                parsed.store = value;
            } else if (argument == "--ratox-cgroup-root") {
                parsed.cgroup_root = value;
            } else if (argument == "--shell") {
                parsed.shell_override = std::filesystem::path(value);
            } else if (argument == "--toolbox-dir") {
                parsed.toolbox_directory = std::filesystem::path(value);
            } else {
                auto uid = parse_uid(value);
                if (!uid) return uid.status();
                parsed.owner_uid = uid.value();
            }
            continue;
        }
        if (argument == "--allow-sudo") {
            parsed.allow_sudo = true;
            continue;
        }
        if (argument.starts_with("--")) {
            return Status{ErrorCode::invalid_argument,
                          "unknown terminal profile option: " +
                              std::string(argument)};
        }
        parsed.positional.push_back(argument);
    }
    if (parsed.positional.empty() ||
        !is_admin_command(parsed.positional.front())) {
        return Status{ErrorCode::invalid_argument,
                      "terminal profile command is missing"};
    }
    return parsed;
}

Result<terminal::ProfileStoreData> load_valid_store(
    const AdminArguments &arguments) {
    if (arguments.store.empty()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal profile store command requires --ratox-profile-store PATH"};
    }
    auto loaded = terminal::load_profile_store(
        arguments.store, arguments.owner_uid);
    if (!loaded) return loaded.status();
    terminal::ProfileRegistry registry;
    const Status valid = registry.replace(loaded.value());
    if (!valid.ok()) return valid;
    return loaded;
}

Status reread_store(const AdminArguments &arguments) {
    auto loaded = load_valid_store(arguments);
    return loaded ? Status::success() : loaded.status();
}

Result<std::vector<std::uint8_t>> read_record(
    const std::filesystem::path &path) {
    auto bytes = StateStore::read(path);
    if (!bytes) return bytes.status();
    if (bytes.value().size() > terminal::kMaximumProfileFileBytes) {
        return Status{ErrorCode::resource_exhausted,
                      "terminal profile input exceeds the canonical byte bound"};
    }
    return bytes;
}

Result<terminal::PrincipalId> parse_principal(std::string_view text) {
    auto bytes = security::decode_hex_exact(
        text, terminal::PrincipalId{}.size(), "terminal principal public key");
    if (!bytes) return bytes.status();
    terminal::PrincipalId principal{};
    std::copy(bytes.value().begin(), bytes.value().end(), principal.begin());
    return principal;
}

int fail(const Status &status, int code = 3) {
    std::cerr << status.message() << '\n';
    return code;
}

int print_bytes(std::span<const std::uint8_t> bytes) {
    std::cout.write(
        reinterpret_cast<const char *>(bytes.data()),
        static_cast<std::streamsize>(bytes.size()));
    if (!std::cout) {
        std::cerr << "unable to write terminal profile record\n";
        return 3;
    }
    return 0;
}

struct LocalAccount {
    std::uint32_t uid{0U};
    std::uint32_t gid{0U};
    std::string name;
    std::filesystem::path home;
    std::filesystem::path shell;
    std::vector<std::uint32_t> supplementary_groups;
};

Result<LocalAccount> lookup_account(
    std::optional<std::string_view> selected) {
    long suggested = ::sysconf(_SC_GETPW_R_SIZE_MAX);
    if (suggested < 1024L) suggested = 16384L;
    if (suggested > 1024L * 1024L) suggested = 1024L * 1024L;
    std::vector<char> buffer(static_cast<std::size_t>(suggested));
    passwd record{};
    passwd *result = nullptr;
    int error = 0;
    if (!selected.has_value()) {
        error = ::getpwuid_r(
            ::geteuid(), &record, buffer.data(), buffer.size(), &result);
    } else {
        const std::string name(*selected);
        error = ::getpwnam_r(
            name.c_str(), &record, buffer.data(), buffer.size(), &result);
        if (error == 0 && result == nullptr) {
            auto uid = parse_uid(*selected);
            if (uid) {
                error = ::getpwuid_r(
                    static_cast<uid_t>(uid.value()), &record,
                    buffer.data(), buffer.size(), &result);
            }
        }
    }
    if (error != 0) {
        return Status{
            ErrorCode::io_error,
            "unable to inspect local login account: " +
                std::string(std::strerror(error))};
    }
    if (result == nullptr || record.pw_name == nullptr ||
        record.pw_dir == nullptr || record.pw_shell == nullptr) {
        return Status{ErrorCode::not_found,
                      "local login account is not present"};
    }
    if (static_cast<std::uint64_t>(record.pw_uid) >
            std::numeric_limits<std::uint32_t>::max() ||
        static_cast<std::uint64_t>(record.pw_gid) >
            std::numeric_limits<std::uint32_t>::max()) {
        return Status{ErrorCode::unsupported,
                      "local login identity does not fit the profile format"};
    }
    LocalAccount account;
    account.uid = static_cast<std::uint32_t>(record.pw_uid);
    account.gid = static_cast<std::uint32_t>(record.pw_gid);
    account.name = record.pw_name;
    account.home = record.pw_dir;
    account.shell = record.pw_shell;
    int group_count = 1;
    std::vector<gid_t> groups(1U);
    int listed = ::getgrouplist(
        account.name.c_str(), static_cast<gid_t>(record.pw_gid),
        groups.data(), &group_count);
    if (listed < 0) {
        // getgrouplist() includes the primary gid. Profile v6 stores that gid
        // separately and permits as many as 256 supplementary groups.
        if (group_count <= 0 || group_count > 257) {
            return Status{
                ErrorCode::resource_exhausted,
                "local login account has an unsupported supplementary-group count"};
        }
        groups.resize(static_cast<std::size_t>(group_count));
        listed = ::getgrouplist(
            account.name.c_str(), static_cast<gid_t>(record.pw_gid),
            groups.data(), &group_count);
    }
    if (listed < 0 || group_count < 0 || group_count > 257) {
        return Status{
            ErrorCode::io_error,
            "unable to freeze local login supplementary groups"};
    }
    groups.resize(static_cast<std::size_t>(group_count));
    account.supplementary_groups.reserve(groups.size());
    for (const gid_t group : groups) {
        const std::uint64_t value = static_cast<std::uint64_t>(group);
        if (value > std::numeric_limits<std::uint32_t>::max()) {
            return Status{
                ErrorCode::unsupported,
                "local login supplementary group does not fit the profile format"};
        }
        account.supplementary_groups.push_back(
            static_cast<std::uint32_t>(value));
    }
    std::sort(
        account.supplementary_groups.begin(),
        account.supplementary_groups.end());
    account.supplementary_groups.erase(
        std::unique(
            account.supplementary_groups.begin(),
            account.supplementary_groups.end()),
        account.supplementary_groups.end());
    account.supplementary_groups.erase(
        std::remove(
            account.supplementary_groups.begin(),
            account.supplementary_groups.end(), account.gid),
        account.supplementary_groups.end());
    if (account.supplementary_groups.size() > 256U) {
        return Status{
            ErrorCode::resource_exhausted,
            "local login account has an unsupported supplementary-group count"};
    }
    return account;
}

struct ShellCandidate {
    std::filesystem::path path;
    std::string source;
};

bool executable_by_account(
    const struct stat &metadata, const LocalAccount &account) {
    if (metadata.st_uid == static_cast<uid_t>(account.uid)) {
        return (metadata.st_mode & S_IXUSR) != 0;
    }
    const bool member_of_file_group =
        metadata.st_gid == static_cast<gid_t>(account.gid) ||
        std::binary_search(
            account.supplementary_groups.begin(),
            account.supplementary_groups.end(),
            static_cast<std::uint32_t>(metadata.st_gid));
    return member_of_file_group
               ? (metadata.st_mode & S_IXGRP) != 0
               : (metadata.st_mode & S_IXOTH) != 0;
}

bool toolbox_path_safe_for_account(
    const std::filesystem::path &directory,
    const LocalAccount &account) {
    std::filesystem::path current{"/"};
    struct stat metadata {};
    const auto component_is_safe = [&]() {
        if (::stat(current.c_str(), &metadata) != 0 ||
            !S_ISDIR(metadata.st_mode) ||
            !executable_by_account(metadata, account)) {
            return false;
        }
        const bool owner_is_trusted =
            metadata.st_uid == static_cast<uid_t>(0) ||
            metadata.st_uid == ::geteuid() ||
            metadata.st_uid == static_cast<uid_t>(account.uid);
        const bool externally_writable =
            (metadata.st_mode & static_cast<mode_t>(0022)) != 0;
        const bool sticky =
            (metadata.st_mode & static_cast<mode_t>(S_ISVTX)) != 0;
        return owner_is_trusted && (!externally_writable || sticky);
    };
    if (!component_is_safe()) return false;
    for (const auto &component : directory.relative_path()) {
        current /= component;
        if (!component_is_safe()) return false;
    }
    return true;
}

Result<std::filesystem::path> qualify_shell(
    const std::filesystem::path &candidate,
    const LocalAccount &account) {
    if (!candidate.is_absolute()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal shell candidate is not absolute"};
    }
    std::error_code filesystem_error;
    const std::filesystem::path resolved =
        std::filesystem::canonical(candidate, filesystem_error);
    if (filesystem_error || !resolved.is_absolute() || resolved == "/" ||
        resolved.lexically_normal() != resolved) {
        return Status{ErrorCode::not_found,
                      "terminal shell candidate cannot be canonically resolved"};
    }
    const int descriptor = ::open(
        resolved.c_str(), O_RDONLY | O_NONBLOCK | O_CLOEXEC | O_NOFOLLOW);
    if (descriptor < 0) {
        return Status{ErrorCode::not_found,
                      "terminal shell candidate cannot be opened"};
    }
    struct stat metadata {};
    std::array<std::uint8_t, 4U> magic{};
    const bool inspected = ::fstat(descriptor, &metadata) == 0;
    const ssize_t count = inspected
        ? ::pread(descriptor, magic.data(), magic.size(), 0)
        : -1;
    static_cast<void>(::close(descriptor));
    constexpr std::array<std::uint8_t, 4U> elf{
        0x7fU, static_cast<std::uint8_t>('E'),
        static_cast<std::uint8_t>('L'), static_cast<std::uint8_t>('F')};
    if (!inspected || !S_ISREG(metadata.st_mode) ||
        (metadata.st_mode & static_cast<mode_t>(0111)) == 0 ||
        (metadata.st_mode & static_cast<mode_t>(0022)) != 0 ||
        (metadata.st_mode & static_cast<mode_t>(S_ISUID | S_ISGID)) != 0 ||
        (metadata.st_uid != static_cast<uid_t>(0) &&
         metadata.st_uid != ::geteuid() &&
         metadata.st_uid != static_cast<uid_t>(account.uid)) ||
        count != static_cast<ssize_t>(magic.size()) || magic != elf) {
        return Status{
            ErrorCode::unsupported,
            "terminal shell candidate fails the Ratox ELF ownership/mode contract"};
    }
    if (!executable_by_account(metadata, account)) {
        return Status{ErrorCode::unavailable,
                      "terminal shell candidate is not executable by the target identity"};
    }
    return resolved;
}

struct QualifiedToolbox {
    std::filesystem::path directory;
    std::filesystem::path multicall;
};

Result<QualifiedToolbox> qualify_toolbox(
    const std::filesystem::path &candidate,
    const LocalAccount &account) {
    if (!candidate.is_absolute()) {
        return Status{ErrorCode::invalid_argument,
                      "terminal toolbox directory is not absolute"};
    }
    std::error_code filesystem_error;
    const std::filesystem::path directory =
        std::filesystem::canonical(candidate, filesystem_error);
    if (filesystem_error || !directory.is_absolute() || directory == "/" ||
        directory.lexically_normal() != directory) {
        return Status{ErrorCode::not_found,
                      "terminal toolbox directory cannot be canonically resolved"};
    }
    struct stat metadata {};
    if (::stat(directory.c_str(), &metadata) != 0 ||
        !S_ISDIR(metadata.st_mode) ||
        !toolbox_path_safe_for_account(directory, account) ||
        (metadata.st_mode & static_cast<mode_t>(0022)) != 0 ||
        (metadata.st_uid != static_cast<uid_t>(0) &&
         metadata.st_uid != ::geteuid() &&
         metadata.st_uid != static_cast<uid_t>(account.uid))) {
        return Status{
            ErrorCode::unsupported,
            "terminal toolbox directory fails the Ratox ownership/mode contract"};
    }
    const std::filesystem::path multicall_path = directory / "toybox";
    struct stat multicall_metadata {};
    if (::lstat(multicall_path.c_str(), &multicall_metadata) != 0 ||
        !S_ISREG(multicall_metadata.st_mode)) {
        return Status{
            ErrorCode::unsupported,
            "terminal toolbox toybox must be one regular non-symlink executable"};
    }
    auto multicall = qualify_shell(multicall_path, account);
    if (!multicall) {
        return Status{
            multicall.status().code(),
            "terminal toolbox requires a qualified toybox executable: " +
                multicall.status().message()};
    }
    return QualifiedToolbox{directory, multicall.value()};
}

std::string shell_path_environment(
    const LocalAccount *account = nullptr,
    const std::optional<std::filesystem::path> &toolbox = std::nullopt) {
    std::vector<std::string> directories;
    if (toolbox) directories.push_back(toolbox->string());
    if (account != nullptr) {
        directories.push_back(
            "/etc/profiles/per-user/" + account->name + "/bin");
        directories.push_back((account->home / ".local/bin").string());
        directories.push_back((account->home / ".nix-profile/bin").string());
    }
    for (const std::string_view directory : {
             "/run/wrappers/bin", "/run/current-system/sw/bin",
             "/nix/var/nix/profiles/default/bin", "/usr/local/sbin",
             "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin",
             "/bin"}) {
        directories.emplace_back(directory);
    }
    std::string result;
    for (const std::string &directory : directories) {
        if (!result.empty()) result.push_back(':');
        result += directory;
    }
    return result;
}

Result<std::vector<ShellCandidate>> discover_shells(
    const LocalAccount &account,
    const std::optional<std::filesystem::path> &override_path) {
    std::vector<std::pair<std::filesystem::path, std::string>> proposed;
    if (override_path) proposed.emplace_back(*override_path, "explicit");
    if (!account.shell.empty()) proposed.emplace_back(account.shell, "passwd");
    if (account.uid == static_cast<std::uint32_t>(::geteuid())) {
        const char *ambient_shell = ::getenv("SHELL");
        if (ambient_shell != nullptr && *ambient_shell != '\0') {
            proposed.emplace_back(ambient_shell, "environment");
        }
    }
    const std::string search_path = shell_path_environment(&account);
    const std::string_view search_path_view{search_path};
    std::size_t begin = 0U;
    while (begin <= search_path_view.size()) {
        const std::size_t end = search_path_view.find(':', begin);
        const std::string_view component = search_path_view.substr(
            begin, end == std::string_view::npos
                       ? search_path_view.size() - begin
                       : end - begin);
        if (!component.empty() && component.front() == '/') {
            for (const std::string_view name : {
                     "bash", "zsh", "fish", "ksh", "oksh", "mksh",
                     "dash", "ash", "sh", "csh", "tcsh"}) {
                proposed.emplace_back(
                    std::filesystem::path(std::string(component)) / name,
                    "fallback");
            }
        }
        if (end == std::string_view::npos) break;
        begin = end + 1U;
    }

    std::vector<ShellCandidate> result;
    for (const auto &[candidate, source] : proposed) {
        auto qualified = qualify_shell(candidate, account);
        if (!qualified) {
            if (source == "explicit") {
                return Status{
                    qualified.status().code(),
                    "explicit terminal shell is unusable: " +
                        qualified.status().message()};
            }
            continue;
        }
        if (std::any_of(
                result.begin(), result.end(), [&](const ShellCandidate &item) {
                    return item.path == qualified.value();
                })) {
            continue;
        }
        result.push_back(ShellCandidate{qualified.value(), source});
    }
    return result;
}

std::filesystem::path working_home(const LocalAccount &account) {
    if (!account.home.is_absolute()) return "/";
    std::error_code error;
    const std::filesystem::path resolved =
        std::filesystem::canonical(account.home, error);
    if (error || !std::filesystem::is_directory(resolved, error) || error) {
        return "/";
    }
    return resolved;
}

struct SudoCandidate {
    std::filesystem::path path;
    std::string mechanism;
};

std::uint32_t load_little_endian_u32(
    const std::uint8_t *bytes) noexcept {
    return static_cast<std::uint32_t>(bytes[0U]) |
           (static_cast<std::uint32_t>(bytes[1U]) << 8U) |
           (static_cast<std::uint32_t>(bytes[2U]) << 16U) |
           (static_cast<std::uint32_t>(bytes[3U]) << 24U);
}

bool has_effective_identity_file_capabilities(
    const std::filesystem::path &path) {
    constexpr std::uint32_t kRevisionMask = 0xff000000U;
    constexpr std::uint32_t kRevisionOne = 0x01000000U;
    constexpr std::uint32_t kRevisionTwo = 0x02000000U;
    constexpr std::uint32_t kRevisionThree = 0x03000000U;
    constexpr std::uint32_t kEffective = 0x00000001U;
    std::array<std::uint8_t, 24U> bytes{};
    const ssize_t count = ::getxattr(
        path.c_str(), "security.capability", bytes.data(), bytes.size());
    if (count < 12) return false;
    const std::uint32_t magic = load_little_endian_u32(bytes.data());
    const std::uint32_t revision = magic & kRevisionMask;
    const ssize_t expected = revision == kRevisionOne
        ? 12
        : revision == kRevisionTwo
              ? 20
              : revision == kRevisionThree ? 24 : -1;
    if (count != expected || (magic & kEffective) == 0U) return false;
    const std::uint32_t permitted_low =
        load_little_endian_u32(bytes.data() + 4U);
    const std::uint32_t identity_mask =
        (std::uint32_t{1U} << CAP_SETUID) |
        (std::uint32_t{1U} << CAP_SETGID);
    return (permitted_low & identity_mask) == identity_mask;
}

std::optional<SudoCandidate> discover_sudo(
    std::string_view path_environment,
    const LocalAccount *account = nullptr) {
    std::size_t begin = 0U;
    while (begin <= path_environment.size()) {
        const std::size_t end = path_environment.find(':', begin);
        const std::string_view component = path_environment.substr(
            begin, end == std::string_view::npos
                       ? path_environment.size() - begin
                       : end - begin);
        if (!component.empty() && component.front() == '/') {
            const std::filesystem::path candidate =
                std::filesystem::path(std::string(component)) / "sudo";
            struct stat metadata {};
            if (::stat(candidate.c_str(), &metadata) == 0 &&
                S_ISREG(metadata.st_mode) &&
                (account != nullptr
                     ? executable_by_account(metadata, *account)
                     : ::access(candidate.c_str(), X_OK) == 0)) {
                if (metadata.st_uid == static_cast<uid_t>(0) &&
                    (metadata.st_mode & S_ISUID) != 0) {
                    return SudoCandidate{candidate, "setuid-root"};
                }
                if (has_effective_identity_file_capabilities(candidate)) {
                    return SudoCandidate{candidate, "file-capabilities"};
                }
            }
        }
        if (end == std::string_view::npos) break;
        begin = end + 1U;
    }
    return std::nullopt;
}

Result<terminal::Profile> shell_template_profile(
    std::string id, const LocalAccount &account,
    const ShellCandidate &shell, bool allow_sudo,
    const std::optional<std::filesystem::path> &toolbox = std::nullopt) {
    terminal::Profile profile;
    profile.id = std::move(id);
    profile.enabled = false;
    profile.arguments = {shell.path.string()};
    const std::string basename = shell.path.filename().string();
    if (toolbox) {
        profile.arguments.push_back("-i");
    } else if (basename == "bash" || basename == "zsh" ||
               basename == "fish" || basename == "sh" ||
               basename == "dash" || basename == "ksh" ||
               basename == "mksh" || basename == "oksh" ||
               basename == "ash" || basename == "csh" ||
               basename == "tcsh") {
        profile.arguments.push_back("-l");
    }
    profile.working_directory = working_home(account).string();
    profile.inherited_environment = {"LANG", "TZ"};
    if (toolbox) {
        profile.environment = {
            {"HISTFILE", "/dev/null"},
            {"HOME", account.home.string()},
            {"IOTOX_RESCUE_TOOLBOX", toolbox->string()},
            {"LOGNAME", account.name},
            {"PATH", shell_path_environment(&account, toolbox)},
            {"PS1", "iotox-rescue$ "},
            {"SHELL", shell.path.string()},
            {"USER", account.name},
        };
    } else {
        profile.environment = {
            {"HOME", account.home.string()},
            {"LOGNAME", account.name},
            {"PATH", shell_path_environment(&account)},
            {"SHELL", shell.path.string()},
            {"USER", account.name},
        };
    }
    profile.identity.mode = terminal::IdentityMode::account;
    profile.identity.uid = account.uid;
    profile.identity.gid = account.gid;
    profile.identity.clear_supplementary_groups = false;
    profile.identity.supplementary_groups = account.supplementary_groups;
    profile.confinement = allow_sudo
        ? terminal::ConfinementMode::compatibility
        : terminal::ConfinementMode::baseline;
    profile.allow_privilege_escalation = allow_sudo;
    profile.limits = terminal::ResourceLimits{0U, 0U, 0U, 0U, 0U};
    auto shell_digest = sync::hash_sync_file_sha256(shell.path);
    if (!shell_digest) {
        return Status{
            shell_digest.status().code(),
            "unable to pin terminal shell payload: " +
                shell_digest.status().message()};
    }
    profile.executable_sha256 = shell_digest.value();
    if (toolbox) {
        auto toolbox_digest = sync::hash_sync_file_sha256(*toolbox / "toybox");
        if (!toolbox_digest) {
            return Status{
                toolbox_digest.status().code(),
                "unable to pin terminal toolbox payload: " +
                    toolbox_digest.status().message()};
        }
        profile.toolbox_sha256 = toolbox_digest.value();
    }
    return profile;
}

terminal::Profile template_profile(std::string id) {
    terminal::Profile profile;
    profile.id = std::move(id);
    profile.enabled = false;
    profile.arguments = {"/bin/false"};
    profile.working_directory = "/";
    profile.confinement = terminal::ConfinementMode::baseline;
    return profile;
}

std::string probe_pidfd() {
#if defined(SYS_pidfd_open)
    const long descriptor = ::syscall(SYS_pidfd_open, ::getpid(), 0U);
    if (descriptor >= 0) {
        static_cast<void>(::close(static_cast<int>(descriptor)));
        return "live-proved";
    }
    return errno == ENOSYS ? "unavailable" : "available-probe-denied";
#else
    return "unavailable-build-headers";
#endif
}

bool child_succeeded(pid_t child) {
    if (child < 0) return false;
    int status = 0;
    while (::waitpid(child, &status, 0) < 0) {
        if (errno != EINTR) return false;
    }
    return WIFEXITED(status) && WEXITSTATUS(status) == 0;
}

std::string probe_seccomp(bool live_confinement_probe) {
    errno = 0;
    if (::prctl(PR_GET_SECCOMP, 0, 0, 0, 0) < 0) {
        return errno == EINVAL ? "unavailable" : "available-probe-denied";
    }
    if (!live_confinement_probe) return "available";
    const pid_t child = ::fork();
    if (child == 0) {
        const sock_filter instruction{
            static_cast<unsigned short>(BPF_RET | BPF_K), 0U, 0U,
            SECCOMP_RET_ALLOW};
        const sock_fprog program{1U, const_cast<sock_filter *>(&instruction)};
        if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0 ||
            ::prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &program) != 0) {
            _exit(1);
        }
        _exit(0);
    }
    return child_succeeded(child) ? "live-proved" : "available-probe-denied";
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

std::string probe_mdwe(bool live_confinement_probe) {
    errno = 0;
    const int current = ::prctl(PR_GET_MDWE, 0, 0, 0, 0);
    if (current < 0 && errno == EINVAL) return "unavailable";
    if (current < 0) return "available-probe-denied";
    if (!live_confinement_probe) return "available";
    const pid_t child = ::fork();
    if (child == 0) {
        if (::prctl(PR_SET_MDWE, PR_MDWE_REFUSE_EXEC_GAIN, 0, 0, 0) != 0) {
            _exit(1);
        }
        const int proved = ::prctl(PR_GET_MDWE, 0, 0, 0, 0);
        _exit(proved >= 0 &&
                      (static_cast<unsigned long>(proved) &
                       PR_MDWE_REFUSE_EXEC_GAIN) != 0UL
                  ? 0
                  : 1);
    }
    return child_succeeded(child) ? "live-proved" : "available-probe-denied";
}

std::string probe_privilege_escalation() {
    const int no_new_privileges = ::prctl(
        PR_GET_NO_NEW_PRIVS, 0, 0, 0, 0);
    if (no_new_privileges < 0) return "probe-denied";
    if (no_new_privileges != 0) return "blocked-no-new-privileges";
#if defined(PR_GET_SECUREBITS) && defined(SECBIT_NOROOT) && \
    defined(SECBIT_NO_SETUID_FIXUP)
    const int securebits = ::prctl(PR_GET_SECUREBITS, 0, 0, 0, 0);
    if (securebits < 0) return "probe-denied";
    if ((securebits & (SECBIT_NOROOT | SECBIT_NO_SETUID_FIXUP)) != 0) {
        return "blocked-securebits";
    }
#else
    return "unavailable-build-headers";
#endif
#if defined(PR_CAPBSET_READ)
    for (const int capability : {CAP_SETUID, CAP_SETGID}) {
        const int present = ::prctl(
            PR_CAPBSET_READ, capability, 0, 0, 0);
        if (present < 0) return "probe-denied";
        if (present != 1) return "blocked-capability-bound";
    }
#else
    return "unavailable-build-headers";
#endif
    return "available-host-policy-pending";
}

std::pair<std::string, int> probe_landlock(bool live_confinement_probe) {
#if defined(SYS_landlock_create_ruleset) && defined(SYS_landlock_restrict_self)
    errno = 0;
    const long abi = ::syscall(
        SYS_landlock_create_ruleset, nullptr, 0U,
        LANDLOCK_CREATE_RULESET_VERSION);
    if (abi < 0) {
        return {errno == ENOSYS || errno == EOPNOTSUPP
                    ? "unavailable"
                    : "available-probe-denied",
                0};
    }
    if (!live_confinement_probe)
        return {"available", static_cast<int>(abi)};
    const pid_t child = ::fork();
    if (child == 0) {
        landlock_ruleset_attr ruleset{};
        ruleset.handled_access_fs = LANDLOCK_ACCESS_FS_EXECUTE;
        const long descriptor = ::syscall(
            SYS_landlock_create_ruleset, &ruleset, sizeof(ruleset), 0U);
        if (descriptor < 0 ||
            ::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0 ||
            ::syscall(SYS_landlock_restrict_self,
                      static_cast<int>(descriptor), 0U) != 0) {
            if (descriptor >= 0) static_cast<void>(::close(static_cast<int>(descriptor)));
            _exit(1);
        }
        static_cast<void>(::close(static_cast<int>(descriptor)));
        _exit(0);
    }
    return {child_succeeded(child) ? "live-proved" : "available-probe-denied",
            static_cast<int>(abi)};
#else
    return {"unavailable-build-headers", 0};
#endif
}

std::string read_small_text(const std::filesystem::path &path) {
    std::ifstream input(path);
    std::string text;
    std::getline(input, text);
    return input || input.eof() ? text : std::string{};
}

std::string file_capability(const std::filesystem::path &path) {
    struct stat metadata {};
    if (::lstat(path.c_str(), &metadata) != 0 || !S_ISREG(metadata.st_mode)) {
        return "unavailable";
    }
    const bool readable = ::access(path.c_str(), R_OK) == 0;
    const bool writable = ::access(path.c_str(), W_OK) == 0;
    if (readable && writable) return "delegated";
    if (readable) return "available-readonly";
    if (writable) return "available-writeonly";
    return "probe-denied";
}

int print_host_capabilities(const std::filesystem::path &cgroup_root) {
    std::cout << render_terminal_host_capabilities(
        probe_terminal_host_capabilities(cgroup_root, true));
    return 0;
}

Status validate_prospective_store(terminal::ProfileStoreData data) {
    terminal::ProfileRegistry registry;
    return registry.replace(std::move(data));
}

}  // namespace

TerminalHostCapabilities probe_terminal_host_capabilities(
    const std::filesystem::path &cgroup_root,
    bool live_confinement_probes) {
    TerminalHostCapabilities result;
    const std::filesystem::path effective_cgroup_root =
        cgroup_root.empty() ? current_cgroup_root() : cgroup_root;
    result.pidfd = probe_pidfd();
    result.seccomp = probe_seccomp(live_confinement_probes);
    result.mdwe = probe_mdwe(live_confinement_probes);
    const auto landlock = probe_landlock(live_confinement_probes);
    result.landlock = landlock.first;
    result.landlock_abi = landlock.second < 0
        ? 0U
        : static_cast<std::uint32_t>(landlock.second);
    result.privilege_escalation = probe_privilege_escalation();
    const auto sudo = discover_sudo(shell_path_environment());
    result.sudo_path = sudo ? sudo->path.string() : "unavailable";
    result.sudo_mechanism = sudo ? sudo->mechanism : "unavailable";
    result.cgroup_root = effective_cgroup_root;

    struct statfs filesystem {};
    constexpr long kCgroup2Magic = 0x63677270L;
    const bool cgroup_v2 =
        ::statfs(effective_cgroup_root.c_str(), &filesystem) == 0 &&
        static_cast<long>(filesystem.f_type) == kCgroup2Magic;
    result.cgroup_v2 = cgroup_v2 ? "available" : "unavailable";
    if (!cgroup_v2) return result;
    const bool delegated =
        ::access((effective_cgroup_root / "cgroup.procs").c_str(), W_OK) == 0 &&
        ::access((effective_cgroup_root / "cgroup.subtree_control").c_str(), W_OK) == 0;
    result.cgroup_delegation =
        delegated ? "delegated" : "available-not-delegated";
    result.cgroup_controllers =
        read_small_text(effective_cgroup_root / "cgroup.controllers");
    for (std::size_t index = 0U; index < kCgroupInterfaces.size(); ++index) {
        result.cgroup_interfaces[index] =
            file_capability(effective_cgroup_root / kCgroupInterfaces[index]);
    }
    return result;
}

std::string render_terminal_host_capabilities(
    const TerminalHostCapabilities &capabilities) {
    std::ostringstream output;
    output << "pidfd=" << capabilities.pidfd << '\n'
           << "seccomp=" << capabilities.seccomp << '\n'
           << "mdwe=" << capabilities.mdwe << '\n'
           << "landlock=" << capabilities.landlock << '\n'
           << "landlock-abi=" << capabilities.landlock_abi << '\n'
           << "privilege-escalation-prerequisite="
           << capabilities.privilege_escalation << '\n'
           << "sudo-path=" << capabilities.sudo_path << '\n'
           << "sudo-mechanism=" << capabilities.sudo_mechanism << '\n'
           << "sudo-policy=" << capabilities.sudo_policy << '\n'
           << "cgroup-v2=" << capabilities.cgroup_v2 << '\n';
    if (capabilities.cgroup_v2 != "available") return output.str();
    output << "cgroup-root=" << capabilities.cgroup_root.string() << '\n'
           << "cgroup-delegation=" << capabilities.cgroup_delegation << '\n'
           << "cgroup-controllers=" << capabilities.cgroup_controllers << '\n';
    for (std::size_t index = 0U; index < kCgroupInterfaces.size(); ++index) {
        output << "cgroup-interface-" << kCgroupInterfaces[index] << '='
               << capabilities.cgroup_interfaces[index] << '\n';
    }
    return output.str();
}

bool is_terminal_admin_cli_invocation(
    std::span<const std::string_view> arguments) noexcept {
    for (std::size_t index = 0U; index < arguments.size(); ++index) {
        if (arguments[index] == "--ratox-profile-store" ||
            arguments[index] == "--ratox-cgroup-root" ||
            arguments[index] == "--ratox-profile-owner-uid" ||
            arguments[index] == "--shell" ||
            arguments[index] == "--toolbox-dir") {
            ++index;
            continue;
        }
        if (arguments[index] == "--allow-sudo") continue;
        if (arguments[index].starts_with("--")) return false;
        return is_admin_command(arguments[index]);
    }
    return false;
}

int run_terminal_admin_cli(
    std::span<const std::string_view> arguments) {
    auto parsed = parse_arguments(arguments);
    if (!parsed) return fail(parsed.status(), 2);
    const std::string_view command = parsed.value().positional.front();
    const auto arity = parsed.value().positional.size();

    if (command == "host-capabilities") {
        if (arity != 1U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "host-capabilities takes no arguments"}, 2);
        }
        if (parsed.value().allow_sudo || parsed.value().shell_override ||
            parsed.value().toolbox_directory) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "host-capabilities does not accept shell-template options"}, 2);
        }
        return print_host_capabilities(parsed.value().cgroup_root);
    }

    if (command == "terminal-shell-discover") {
        if (arity < 1U || arity > 2U) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "terminal-shell-discover accepts an optional USER"}, 2);
        }
        if (parsed.value().allow_sudo) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "terminal-shell-discover does not accept --allow-sudo"}, 2);
        }
        auto account = lookup_account(
            arity == 2U
                ? std::optional<std::string_view>{
                      parsed.value().positional[1U]}
                : std::nullopt);
        if (!account) return fail(account.status(), 4);
        const auto shells = discover_shells(
            account.value(), parsed.value().shell_override);
        if (!shells) return fail(shells.status(), 4);
        std::optional<QualifiedToolbox> toolbox;
        if (parsed.value().toolbox_directory) {
            auto qualified = qualify_toolbox(
                *parsed.value().toolbox_directory, account.value());
            if (!qualified) return fail(qualified.status(), 4);
            toolbox = std::move(qualified.value());
        }
        std::cout << "user=" << account.value().name
                  << " uid=" << account.value().uid
                  << " gid=" << account.value().gid
                  << " home=" << account.value().home.string() << '\n';
        for (std::size_t index = 0U; index < shells.value().size(); ++index) {
            std::cout << (index == 0U ? "selected=" : "candidate=")
                      << shells.value()[index].path.string()
                      << " source=" << shells.value()[index].source << '\n';
        }
        if (toolbox) {
            std::cout << "toolbox-dir=" << toolbox->directory.string()
                      << " multicall=" << toolbox->multicall.string() << '\n';
        }
        const std::string path = shell_path_environment(
            &account.value(),
            toolbox ? std::optional<std::filesystem::path>{toolbox->directory}
                    : std::nullopt);
        const auto sudo = discover_sudo(path, &account.value());
        if (sudo) {
            std::cout << "sudo=" << sudo->path.string()
                      << " mechanism=" << sudo->mechanism
                      << " policy=not-probed\n";
        } else {
            std::cout << "sudo=unavailable policy=not-probed\n";
        }
        if (shells.value().empty()) {
            return fail(Status{
                ErrorCode::not_found,
                "no Ratox-compatible ELF login shell was discovered"}, 4);
        }
        return 0;
    }

    if (command == "terminal-profile-shell-template") {
        if (arity < 2U || arity > 3U) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "terminal-profile-shell-template requires PROFILE_ID and optional USER"}, 2);
        }
        auto account = lookup_account(
            arity == 3U
                ? std::optional<std::string_view>{
                      parsed.value().positional[2U]}
                : std::nullopt);
        if (!account) return fail(account.status(), 4);
        if (account.value().uid == 0U) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "owner-shell templates must start as a non-root account; use explicit sudo policy for elevation"}, 4);
        }
        if (parsed.value().toolbox_directory) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "--toolbox-dir requires terminal-profile-toolbox-template"}, 2);
        }
        const auto shells = discover_shells(
            account.value(), parsed.value().shell_override);
        if (!shells) return fail(shells.status(), 4);
        if (shells.value().empty()) {
            return fail(Status{
                ErrorCode::not_found,
                "no Ratox-compatible ELF login shell was discovered"}, 4);
        }
        if (parsed.value().allow_sudo &&
            !discover_sudo(
                 shell_path_environment(&account.value()),
                 &account.value()).has_value()) {
            return fail(Status{
                ErrorCode::unavailable,
                "--allow-sudo requires a discoverable setuid/file-capability sudo executable"}, 4);
        }
        auto profile = shell_template_profile(
            std::string(parsed.value().positional[1U]),
            account.value(), shells.value().front(),
            parsed.value().allow_sudo);
        if (!profile) return fail(profile.status(), 4);
        auto encoded = terminal::encode_profile_record(profile.value());
        if (!encoded) return fail(encoded.status(), 2);
        return print_bytes(encoded.value());
    }

    if (command == "terminal-profile-toolbox-template") {
        if (arity < 2U || arity > 3U) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "terminal-profile-toolbox-template requires PROFILE_ID and optional USER"}, 2);
        }
        if (!parsed.value().shell_override ||
            !parsed.value().toolbox_directory) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "terminal-profile-toolbox-template requires --shell PATH and --toolbox-dir PATH"}, 2);
        }
        auto account = lookup_account(
            arity == 3U
                ? std::optional<std::string_view>{
                      parsed.value().positional[2U]}
                : std::nullopt);
        if (!account) return fail(account.status(), 4);
        if (account.value().uid == 0U) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "rescue-toolbox templates must start as a non-root account; use explicit sudo policy for elevation"}, 4);
        }
        auto toolbox = qualify_toolbox(
            *parsed.value().toolbox_directory, account.value());
        if (!toolbox) return fail(toolbox.status(), 4);
        const auto shells = discover_shells(
            account.value(), parsed.value().shell_override);
        if (!shells) return fail(shells.status(), 4);
        if (shells.value().empty() ||
            shells.value().front().source != "explicit") {
            return fail(Status{
                ErrorCode::not_found,
                "the explicit rescue shell was not selected"}, 4);
        }
        const auto path = shell_path_environment(
            &account.value(), toolbox.value().directory);
        if (parsed.value().allow_sudo &&
            !discover_sudo(path, &account.value()).has_value()) {
            return fail(Status{
                ErrorCode::unavailable,
                "--allow-sudo requires a discoverable setuid/file-capability sudo executable"}, 4);
        }
        auto profile = shell_template_profile(
            std::string(parsed.value().positional[1U]),
            account.value(), shells.value().front(),
            parsed.value().allow_sudo, toolbox.value().directory);
        if (!profile) return fail(profile.status(), 4);
        auto encoded = terminal::encode_profile_record(profile.value());
        if (!encoded) return fail(encoded.status(), 2);
        return print_bytes(encoded.value());
    }

    if (command == "terminal-profile-template") {
        if (arity != 2U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-template requires PROFILE_ID"}, 2);
        }
        if (parsed.value().allow_sudo || parsed.value().shell_override ||
            parsed.value().toolbox_directory) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "shell-template options require a shell profile template command"}, 2);
        }
        auto encoded = terminal::encode_profile_record(
            template_profile(std::string(parsed.value().positional[1U])));
        if (!encoded) return fail(encoded.status(), 2);
        return print_bytes(encoded.value());
    }

    if (command == "terminal-profile-lint") {
        if (arity != 2U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-lint requires PATH"}, 2);
        }
        if (parsed.value().allow_sudo || parsed.value().shell_override ||
            parsed.value().toolbox_directory) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "terminal-profile-lint does not accept shell-template options"}, 2);
        }
        auto bytes = read_record(parsed.value().positional[1U]);
        if (!bytes) return fail(bytes.status());
        auto profile = terminal::decode_profile_record(bytes.value());
        if (!profile) return fail(profile.status(), 2);
        std::cout << "valid=1 id=" << profile.value().id
                  << " enabled=" << (profile.value().enabled ? 1 : 0)
                  << " confinement="
                  << (profile.value().confinement == terminal::ConfinementMode::strict
                          ? "strict"
                          : profile.value().confinement ==
                                    terminal::ConfinementMode::baseline
                                ? "baseline"
                                : "compatibility")
                  << '\n';
        return 0;
    }

    if (command == "terminal-profile-check") {
        if (arity != 2U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-check requires PATH"}, 2);
        }
        if (parsed.value().allow_sudo || parsed.value().shell_override ||
            parsed.value().toolbox_directory) {
            return fail(Status{
                ErrorCode::invalid_argument,
                "terminal-profile-check does not accept shell-template options"}, 2);
        }
        auto bytes = read_record(parsed.value().positional[1U]);
        if (!bytes) return fail(bytes.status());
        auto profile = terminal::decode_profile_record(bytes.value());
        if (!profile) return fail(profile.status(), 2);

        bool payload_ready = true;
        const std::filesystem::path executable{
            profile.value().arguments.front()};
        auto executable_digest = sync::hash_sync_file_sha256(executable);
        std::cout << "iotox-terminal-profile-check-v1\n"
                  << "valid=1 id=" << profile.value().id
                  << " enabled=" << (profile.value().enabled ? 1 : 0)
                  << " confinement="
                  << (profile.value().confinement == terminal::ConfinementMode::strict
                          ? "strict"
                          : profile.value().confinement ==
                                    terminal::ConfinementMode::baseline
                                ? "baseline"
                                : "compatibility")
                  << '\n'
                  << "executable=" << executable.string() << '\n';
        if (executable_digest) {
            std::cout << "executable-state=present\n"
                      << "executable-sha256="
                      << security::hex(executable_digest.value()) << '\n';
            if (profile.value().executable_sha256) {
                const bool match =
                    executable_digest.value() ==
                    profile.value().executable_sha256.value();
                std::cout << "executable-pin="
                          << (match ? "match" : "mismatch") << '\n';
                payload_ready = payload_ready && match;
            } else {
                std::cout << "executable-pin=absent\n";
            }
        } else {
            std::cout << "executable-state=stale\n"
                      << "executable-error="
                      << executable_digest.status().message() << '\n'
                      << "executable-pin=unavailable\n";
            payload_ready = false;
        }

        const auto toolbox = std::find_if(
            profile.value().environment.begin(),
            profile.value().environment.end(),
            [](const terminal::EnvironmentEntry &entry) {
                return entry.name == "IOTOX_RESCUE_TOOLBOX";
            });
        if (profile.value().toolbox_sha256) {
            if (toolbox == profile.value().environment.end()) {
                std::cout << "toolbox-state=stale\n"
                          << "toolbox-pin=unavailable\n";
                payload_ready = false;
            } else {
                const std::filesystem::path toybox =
                    std::filesystem::path(toolbox->value) / "toybox";
                auto toolbox_digest = sync::hash_sync_file_sha256(toybox);
                std::cout << "toolbox=" << toybox.string() << '\n';
                if (toolbox_digest) {
                    const bool match =
                        toolbox_digest.value() ==
                        profile.value().toolbox_sha256.value();
                    std::cout << "toolbox-state=present\n"
                              << "toolbox-sha256="
                              << security::hex(toolbox_digest.value()) << '\n'
                              << "toolbox-pin="
                              << (match ? "match" : "mismatch") << '\n';
                    payload_ready = payload_ready && match;
                } else {
                    std::cout << "toolbox-state=stale\n"
                              << "toolbox-error="
                              << toolbox_digest.status().message() << '\n'
                              << "toolbox-pin=unavailable\n";
                    payload_ready = false;
                }
            }
        } else {
            std::cout << "toolbox-pin=absent\n";
        }
        std::cout << "payload-ready=" << (payload_ready ? 1 : 0) << '\n'
                  << "daily-driver="
                  << (payload_ready && profile.value().enabled
                          ? "ready"
                          : payload_ready ? "review-required" : "blocked")
                  << '\n'
                  << "boundary=checks-local-profile-bytes-only; binding-and-agent-readiness-are-separate\n";
        return std::cout.good() ? 0 : 3;
    }

    if (parsed.value().allow_sudo || parsed.value().shell_override ||
        parsed.value().toolbox_directory) {
        return fail(Status{
            ErrorCode::invalid_argument,
            "shell-template options are valid only for shell discovery/templates"}, 2);
    }

    auto store = load_valid_store(parsed.value());
    if (!store) return fail(store.status());

    if (command == "terminal-profile-list") {
        if (arity != 1U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-list takes no arguments"}, 2);
        }
        for (const auto &profile : store.value().profiles) {
            const std::size_t bindings = static_cast<std::size_t>(std::count_if(
                store.value().bindings.begin(), store.value().bindings.end(),
                [&](const terminal::Binding &binding) {
                    return binding.profile_id == profile.id;
                }));
            std::cout << "id=" << profile.id
                      << " enabled=" << (profile.enabled ? 1 : 0)
                      << " bindings=" << bindings << '\n';
        }
        return 0;
    }

    if (command == "terminal-profile-show") {
        if (arity != 2U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-show requires PROFILE_ID"}, 2);
        }
        const auto found = std::find_if(
            store.value().profiles.begin(), store.value().profiles.end(),
            [&](const terminal::Profile &profile) {
                return profile.id == parsed.value().positional[1U];
            });
        if (found == store.value().profiles.end()) {
            return fail(Status{ErrorCode::not_found,
                               "terminal profile is not installed"}, 4);
        }
        auto encoded = terminal::encode_profile_record(*found);
        if (!encoded) return fail(encoded.status());
        return print_bytes(encoded.value());
    }

    if (command == "terminal-profile-install") {
        if (arity != 2U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-install requires PATH"}, 2);
        }
        auto bytes = read_record(parsed.value().positional[1U]);
        if (!bytes) return fail(bytes.status());
        auto profile = terminal::decode_profile_record(bytes.value());
        if (!profile) return fail(profile.status(), 2);
        terminal::ProfileStoreData prospective = store.value();
        const auto installed = std::find_if(
            prospective.profiles.begin(), prospective.profiles.end(),
            [&](const terminal::Profile &candidate) {
                return candidate.id == profile.value().id;
            });
        if (installed == prospective.profiles.end()) {
            prospective.profiles.push_back(profile.value());
        } else {
            *installed = profile.value();
        }
        const Status valid = validate_prospective_store(std::move(prospective));
        if (!valid.ok()) return fail(valid, 4);
        const Status written = terminal::install_profile_record(
            parsed.value().store, parsed.value().owner_uid, profile.value());
        if (!written.ok()) return fail(written);
        const Status verified = reread_store(parsed.value());
        if (!verified.ok()) return fail(Status{
            verified.code(), "installed profile failed strict store reread: " +
                                 verified.message()});
        std::cout << "installed=" << profile.value().id << '\n';
        return 0;
    }

    if (command == "terminal-profile-remove") {
        if (arity != 2U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-remove requires PROFILE_ID"}, 2);
        }
        const std::string id(parsed.value().positional[1U]);
        const auto installed = std::find_if(
            store.value().profiles.begin(), store.value().profiles.end(),
            [&](const terminal::Profile &profile) { return profile.id == id; });
        if (installed == store.value().profiles.end()) {
            return fail(Status{ErrorCode::not_found,
                               "terminal profile is not installed"}, 4);
        }
        if (std::any_of(
                store.value().bindings.begin(), store.value().bindings.end(),
                [&](const terminal::Binding &binding) {
                    return binding.profile_id == id;
                })) {
            return fail(Status{ErrorCode::unavailable,
                               "terminal profile remains referenced by a binding"}, 4);
        }
        terminal::ProfileStoreData prospective = store.value();
        prospective.profiles.erase(
            std::remove_if(
                prospective.profiles.begin(), prospective.profiles.end(),
                [&](const terminal::Profile &profile) {
                    return profile.id == id;
                }),
            prospective.profiles.end());
        const Status valid = validate_prospective_store(std::move(prospective));
        if (!valid.ok()) return fail(valid, 4);
        const Status removed = terminal::remove_profile_record(
            parsed.value().store, parsed.value().owner_uid, id);
        if (!removed.ok()) return fail(removed, 4);
        const Status verified = reread_store(parsed.value());
        if (!verified.ok()) return fail(verified);
        std::cout << "removed=" << id << '\n';
        return 0;
    }

    if (command == "terminal-profile-bind") {
        if (arity != 3U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-bind requires PRINCIPAL_PUBLIC_KEY_HEX PROFILE_ID"}, 2);
        }
        auto principal = parse_principal(parsed.value().positional[1U]);
        if (!principal) return fail(principal.status(), 2);
        const std::string profile_id(parsed.value().positional[2U]);
        if (std::none_of(
                store.value().profiles.begin(), store.value().profiles.end(),
                [&](const terminal::Profile &profile) {
                    return profile.id == profile_id;
                })) {
            return fail(Status{ErrorCode::not_found,
                               "terminal binding names an uninstalled profile"}, 4);
        }
        terminal::Binding binding{principal.value(), profile_id, true};
        terminal::ProfileStoreData prospective = store.value();
        const auto installed = std::find_if(
            prospective.bindings.begin(), prospective.bindings.end(),
            [&](const terminal::Binding &candidate) {
                return candidate.principal_id == binding.principal_id;
            });
        if (installed == prospective.bindings.end()) {
            prospective.bindings.push_back(binding);
        } else {
            *installed = binding;
        }
        const Status valid = validate_prospective_store(std::move(prospective));
        if (!valid.ok()) return fail(valid, 4);
        const std::string key = security::hex(principal.value());
        const Status written = terminal::install_binding_record(
            parsed.value().store, parsed.value().owner_uid, binding);
        if (!written.ok()) return fail(written);
        const Status verified = reread_store(parsed.value());
        if (!verified.ok()) return fail(verified);
        std::cout << "principal=" << key << " profile=" << profile_id << '\n';
        return 0;
    }

    if (command == "terminal-profile-unbind") {
        if (arity != 2U) {
            return fail(Status{ErrorCode::invalid_argument,
                               "terminal-profile-unbind requires PRINCIPAL_PUBLIC_KEY_HEX"}, 2);
        }
        auto principal = parse_principal(parsed.value().positional[1U]);
        if (!principal) return fail(principal.status(), 2);
        const std::string key = security::hex(principal.value());
        terminal::ProfileStoreData prospective = store.value();
        const auto previous_size = prospective.bindings.size();
        prospective.bindings.erase(
            std::remove_if(
                prospective.bindings.begin(), prospective.bindings.end(),
                [&](const terminal::Binding &binding) {
                    return binding.principal_id == principal.value();
                }),
            prospective.bindings.end());
        if (prospective.bindings.size() == previous_size) {
            return fail(Status{ErrorCode::not_found,
                               "terminal principal is not bound"}, 4);
        }
        const Status valid = validate_prospective_store(std::move(prospective));
        if (!valid.ok()) return fail(valid, 4);
        const Status removed = terminal::remove_binding_record(
            parsed.value().store, parsed.value().owner_uid,
            principal.value());
        if (!removed.ok()) return fail(removed, 4);
        const Status verified = reread_store(parsed.value());
        if (!verified.ok()) return fail(verified);
        std::cout << "unbound=" << key << '\n';
        return 0;
    }

    return fail(Status{ErrorCode::invalid_argument,
                       "unknown terminal profile command"}, 2);
}

}  // namespace iotox
