#include "iotox/protected_state.hpp"

#include "iotox/sync_namespace.hpp"
#include "iotox/update_bundle.hpp"

#include <algorithm>
#include <array>
#include <cerrno>
#include <cstring>
#include <dirent.h>
#include <fcntl.h>
#include <filesystem>
#include <iomanip>
#include <linux/fscrypt.h>
#include <linux/magic.h>
#include <sstream>
#include <string_view>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <utility>
#include <vector>

namespace iotox::protected_state {
namespace {

class Descriptor {
  public:
    explicit Descriptor(int value = -1) noexcept : value_(value) {}
    ~Descriptor() {
        if (value_ >= 0) static_cast<void>(::close(value_));
    }
    Descriptor(const Descriptor &) = delete;
    Descriptor &operator=(const Descriptor &) = delete;
    Descriptor(Descriptor &&other) noexcept : value_(other.value_) {
        other.value_ = -1;
    }
    Descriptor &operator=(Descriptor &&other) noexcept {
        if (this != &other) {
            if (value_ >= 0) static_cast<void>(::close(value_));
            value_ = other.value_;
            other.value_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return value_; }

  private:
    int value_;
};

using PolicyIdentifier =
    std::array<std::uint8_t, FSCRYPT_KEY_IDENTIFIER_SIZE>;

[[nodiscard]] Status io_status(std::string_view operation,
                               const std::filesystem::path &path,
                               int error_number = errno) {
    return Status{ErrorCode::io_error,
                  std::string(operation) + " '" + path.string() + "': " +
                      std::strerror(error_number)};
}

[[nodiscard]] bool normalized_absolute_nonroot(
    const std::filesystem::path &path) {
    return !path.empty() && path.is_absolute() && path != path.root_path() &&
           path.lexically_normal() == path;
}

[[nodiscard]] std::filesystem::path companion(
    const std::filesystem::path &path, std::string_view suffix) {
    std::filesystem::path result = path;
    result += suffix;
    return result;
}

[[nodiscard]] Result<std::uint64_t> mount_identifier(
    int descriptor, const std::filesystem::path &display) {
    struct statx metadata {};
    if (::syscall(SYS_statx, descriptor, "", AT_EMPTY_PATH | AT_SYMLINK_NOFOLLOW,
                  STATX_MNT_ID, &metadata) != 0) {
        return io_status("unable to inspect protected-state mount identity",
                         display);
    }
    if ((metadata.stx_mask & STATX_MNT_ID) == 0U) {
        return Status{ErrorCode::unsupported,
                      "protected state requires statx mount identifiers: " +
                          display.string()};
    }
    return metadata.stx_mnt_id;
}

[[nodiscard]] Result<PolicyIdentifier> policy_identifier(
    int descriptor, const std::filesystem::path &display) {
    struct fscrypt_get_policy_ex_arg argument {};
    argument.policy_size = sizeof(argument.policy);
    if (::ioctl(descriptor, FS_IOC_GET_ENCRYPTION_POLICY_EX, &argument) != 0) {
        const int error_number = errno;
        if (error_number == ENODATA || error_number == ENOTTY ||
            error_number == EOPNOTSUPP) {
            return Status{
                ErrorCode::unsupported,
                "protected state requires an fscrypt-v2 policy on '" +
                    display.string() + "'"};
        }
        return io_status("unable to inspect fscrypt policy", display,
                         error_number);
    }
    if (argument.policy_size < sizeof(fscrypt_policy_v2) ||
        argument.policy.version != FSCRYPT_POLICY_V2) {
        return Status{ErrorCode::unsupported,
                      "protected state requires fscrypt policy version 2 on '" +
                          display.string() + "'"};
    }
    PolicyIdentifier identifier{};
    std::copy_n(argument.policy.v2.master_key_identifier, identifier.size(),
                identifier.begin());
    return identifier;
}

[[nodiscard]] std::string hex_identifier(const PolicyIdentifier &identifier) {
    std::ostringstream output;
    output << std::hex << std::setfill('0');
    for (const std::uint8_t byte : identifier) {
        output << std::setw(2) << static_cast<unsigned int>(byte);
    }
    return output.str();
}

[[nodiscard]] Status require_key_present(
    int descriptor, const std::filesystem::path &display,
    const PolicyIdentifier &identifier) {
    struct fscrypt_get_key_status_arg argument {};
    argument.key_spec.type = FSCRYPT_KEY_SPEC_TYPE_IDENTIFIER;
    std::copy(identifier.begin(), identifier.end(),
              argument.key_spec.u.identifier);
    if (::ioctl(descriptor, FS_IOC_GET_ENCRYPTION_KEY_STATUS, &argument) != 0) {
        return io_status("unable to query fscrypt key status", display);
    }
    if (argument.status != FSCRYPT_KEY_STATUS_PRESENT) {
        return Status{ErrorCode::unavailable,
                      "protected-state fscrypt key is not present for policy " +
                          hex_identifier(identifier)};
    }
    return Status::success();
}

[[nodiscard]] Status require_private_metadata(
    const struct stat &metadata, const std::filesystem::path &display,
    bool root) {
    if (metadata.st_uid != ::geteuid()) {
        return Status{ErrorCode::invalid_argument,
                      "protected-state inode is not owned by the effective UID: " +
                          display.string()};
    }
    if ((S_ISREG(metadata.st_mode) || S_ISDIR(metadata.st_mode)) &&
        (metadata.st_mode & (S_IRWXG | S_IRWXO)) != 0) {
        return Status{ErrorCode::invalid_argument,
                      "protected-state inode grants group or other permissions: " +
                          display.string()};
    }
    if (root && !S_ISDIR(metadata.st_mode)) {
        return Status{ErrorCode::invalid_argument,
                      "protected-state root is not a directory: " +
                          display.string()};
    }
    if (S_ISREG(metadata.st_mode) && metadata.st_nlink != 1) {
        return Status{ErrorCode::invalid_argument,
                      "protected-state regular file or root has multiple links: " +
                          display.string()};
    }
    return Status::success();
}

[[nodiscard]] Result<Descriptor> open_directory_no_follow(
    const std::filesystem::path &path, std::string_view label) {
    int opened = -1;
    do {
        opened = ::open(path.c_str(), O_RDONLY | O_DIRECTORY | O_NOFOLLOW |
                                          O_CLOEXEC | O_NONBLOCK);
    } while (opened < 0 && errno == EINTR);
    if (opened < 0) return io_status(label, path);
    return Descriptor(opened);
}

struct WalkCounts {
    std::size_t inodes{0U};
    std::size_t symlinks{0U};
};

[[nodiscard]] Status walk_tree(
    int directory, const std::filesystem::path &display,
    std::uint64_t expected_mount, const PolicyIdentifier &expected_policy,
    WalkCounts &counts) {
    const int duplicate = ::fcntl(directory, F_DUPFD_CLOEXEC, 0);
    if (duplicate < 0) return io_status("unable to duplicate protected directory", display);
    DIR *stream = ::fdopendir(duplicate);
    if (stream == nullptr) {
        const int error_number = errno;
        static_cast<void>(::close(duplicate));
        return io_status("unable to enumerate protected directory", display,
                         error_number);
    }
    errno = 0;
    while (dirent *entry = ::readdir(stream)) {
        const std::string_view name{entry->d_name};
        if (name == "." || name == "..") continue;
        const std::filesystem::path child_display = display / entry->d_name;
        struct stat metadata {};
        if (::fstatat(directory, entry->d_name, &metadata,
                      AT_SYMLINK_NOFOLLOW) != 0) {
            const Status status = io_status(
                "unable to inspect protected-state inode", child_display);
            static_cast<void>(::closedir(stream));
            return status;
        }
        const Status private_status =
            require_private_metadata(metadata, child_display, false);
        if (!private_status.ok()) {
            static_cast<void>(::closedir(stream));
            return private_status;
        }
        if (S_ISLNK(metadata.st_mode)) {
            // fscrypt encrypts the symlink payload under the parent policy;
            // O_NOFOLLOW and same-policy parent verification prevent escape
            // from turning it into an authority-bearing configured root.
            ++counts.inodes;
            ++counts.symlinks;
            errno = 0;
            continue;
        }
        if (!S_ISDIR(metadata.st_mode) && !S_ISREG(metadata.st_mode)) {
            const Status status{
                ErrorCode::invalid_argument,
                "protected durable state contains a special inode: " +
                    child_display.string()};
            static_cast<void>(::closedir(stream));
            return status;
        }
        const int flags = S_ISDIR(metadata.st_mode)
            ? O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK
            : O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK;
        int opened = -1;
        do {
            opened = ::openat(directory, entry->d_name, flags);
        } while (opened < 0 && errno == EINTR);
        if (opened < 0) {
            const Status status =
                io_status("unable to open protected-state inode", child_display);
            static_cast<void>(::closedir(stream));
            return status;
        }
        Descriptor child(opened);
        struct stat opened_metadata {};
        if (::fstat(child.get(), &opened_metadata) != 0) {
            const Status status = io_status(
                "unable to reinspect opened protected-state inode",
                child_display);
            static_cast<void>(::closedir(stream));
            return status;
        }
        if (opened_metadata.st_dev != metadata.st_dev ||
            opened_metadata.st_ino != metadata.st_ino ||
            ((S_ISDIR(metadata.st_mode)) !=
             (S_ISDIR(opened_metadata.st_mode)))) {
            const Status status{
                ErrorCode::unavailable,
                "protected-state inode changed during inspection: " +
                    child_display.string()};
            static_cast<void>(::closedir(stream));
            return status;
        }
        const Status opened_private =
            require_private_metadata(opened_metadata, child_display, false);
        if (!opened_private.ok()) {
            static_cast<void>(::closedir(stream));
            return opened_private;
        }
        auto child_mount = mount_identifier(child.get(), child_display);
        if (!child_mount) {
            static_cast<void>(::closedir(stream));
            return child_mount.status();
        }
        if (child_mount.value() != expected_mount) {
            const Status status{
                ErrorCode::invalid_argument,
                "protected state crosses a bind or filesystem mount: " +
                    child_display.string()};
            static_cast<void>(::closedir(stream));
            return status;
        }
        auto child_policy = policy_identifier(child.get(), child_display);
        if (!child_policy) {
            static_cast<void>(::closedir(stream));
            return child_policy.status();
        }
        if (child_policy.value() != expected_policy) {
            const Status status{
                ErrorCode::invalid_argument,
                "protected-state inode has a different fscrypt policy: " +
                    child_display.string()};
            static_cast<void>(::closedir(stream));
            return status;
        }
        ++counts.inodes;
        if (S_ISDIR(metadata.st_mode)) {
            const Status nested = walk_tree(child.get(), child_display,
                                            expected_mount, expected_policy,
                                            counts);
            if (!nested.ok()) {
                static_cast<void>(::closedir(stream));
                return nested;
            }
        }
        errno = 0;
    }
    const int enumeration_error = errno;
    static_cast<void>(::closedir(stream));
    if (enumeration_error != 0) {
        return io_status("unable to complete protected-state enumeration",
                         display, enumeration_error);
    }
    return Status::success();
}

[[nodiscard]] bool path_within(const std::filesystem::path &root,
                               const std::filesystem::path &candidate) {
    if (!normalized_absolute_nonroot(candidate)) return false;
    auto root_it = root.begin();
    auto candidate_it = candidate.begin();
    for (; root_it != root.end(); ++root_it, ++candidate_it) {
        if (candidate_it == candidate.end() || *candidate_it != *root_it) {
            return false;
        }
    }
    return true;
}

[[nodiscard]] Status verify_configured_path(
    int root_descriptor, const std::filesystem::path &root,
    const std::filesystem::path &candidate, std::uint64_t expected_mount,
    const PolicyIdentifier &expected_policy) {
    if (!path_within(root, candidate)) {
        return Status{ErrorCode::invalid_argument,
                      "configured durable state escapes protected root: " +
                          candidate.string()};
    }
    const std::filesystem::path relative = candidate.lexically_relative(root);
    int current = ::fcntl(root_descriptor, F_DUPFD_CLOEXEC, 0);
    if (current < 0) {
        return io_status("unable to duplicate protected-state root", root);
    }
    Descriptor cursor(current);
    std::filesystem::path display = root;
    for (const auto &component : relative) {
        if (component == ".") continue;
        display /= component;
        int opened = -1;
        do {
            opened = ::openat(cursor.get(), component.c_str(),
                              O_PATH | O_NOFOLLOW | O_CLOEXEC);
        } while (opened < 0 && errno == EINTR);
        if (opened < 0 && errno == ENOENT) {
            // Agent-created descendants inherit the verified parent policy.
            return Status::success();
        }
        if (opened < 0) {
            return io_status("unable to inspect configured protected path",
                             display);
        }
        Descriptor next(opened);
        struct stat metadata {};
        if (::fstat(next.get(), &metadata) != 0) {
            return io_status("unable to inspect configured protected path",
                             display);
        }
        if (S_ISLNK(metadata.st_mode)) {
            return Status{ErrorCode::invalid_argument,
                          "configured protected path traverses a symlink: " +
                              display.string()};
        }
        const Status private_status =
            require_private_metadata(metadata, display, false);
        if (!private_status.ok()) return private_status;
        auto child_mount = mount_identifier(next.get(), display);
        if (!child_mount) return child_mount.status();
        if (child_mount.value() != expected_mount) {
            return Status{ErrorCode::invalid_argument,
                          "configured protected path crosses a mount: " +
                              display.string()};
        }
        // O_PATH cannot service fscrypt ioctls. The recursive root walk has
        // already checked every extant inode's exact policy; this component
        // walk independently binds the configured spelling to those inodes.
        cursor = std::move(next);
    }
    static_cast<void>(expected_policy);
    return Status::success();
}

[[nodiscard]] Result<bool> runtime_on_tmpfs(
    const std::filesystem::path &runtime) {
    if (!normalized_absolute_nonroot(runtime)) {
        return Status{ErrorCode::invalid_argument,
                      "runtime path must be normalized, non-root, and absolute in protected mode"};
    }
    std::filesystem::path existing = runtime;
    struct stat metadata {};
    while (::lstat(existing.c_str(), &metadata) != 0) {
        if (errno != ENOENT) {
            return io_status("unable to inspect protected runtime", existing);
        }
        if (existing == existing.root_path() || existing.parent_path() == existing) {
            return Status{ErrorCode::not_found,
                          "protected runtime has no existing ancestor"};
        }
        existing = existing.parent_path();
    }
    auto descriptor = open_directory_no_follow(
        existing, "unable to open protected runtime ancestor");
    if (!descriptor) return descriptor.status();
    struct statfs filesystem {};
    if (::fstatfs(descriptor.value().get(), &filesystem) != 0) {
        return io_status("unable to inspect protected runtime filesystem",
                         existing);
    }
    return static_cast<unsigned long>(filesystem.f_type) ==
        static_cast<unsigned long>(TMPFS_MAGIC);
}

[[nodiscard]] Result<std::vector<std::filesystem::path>> durable_paths(
    const Agent::Config &config) {
    std::vector<std::filesystem::path> paths{
        config.transport.state_path,
        config.security.device_identity_path,
        config.security.authority_ledger_path,
        companion(config.security.authority_ledger_path, ".guard"),
        config.security.command_store_path,
        config.security.diagnostics_store_path,
        config.security.peer_alias_store_path,
        config.security.protocol_incarnation_state_path,
        companion(config.security.protocol_incarnation_state_path, ".lock"),
    };
    if (config.security.authority_rollback_witness ||
        config.security.authority_rollback_witness_service) {
        if (!config.security.authority_rollback_witness_intent_path.empty()) {
            paths.push_back(
                config.security.authority_rollback_witness_intent_path);
        } else {
            paths.push_back(companion(
                config.security.authority_ledger_path, ".witness-intent"));
        }
    }
    if (config.security.witness_application_incarnation) {
        paths.push_back(
            config.security.application_incarnation_witness_intent_path);
    }
    if (config.security.witness_command_effects) {
        paths.push_back(
            config.security.command_effect_witness_checkpoint_path);
        paths.push_back(
            config.security.command_effect_witness_intent_path);
    }
    if (config.security.witness_sync_policy) {
        paths.push_back(
            config.security.sync_policy_witness_checkpoint_path);
        paths.push_back(config.security.sync_policy_witness_intent_path);
    }
    if (config.security.witness_update_lifecycle) {
        paths.push_back(
            config.security.update_lifecycle_witness_intent_path);
    }
    if (!config.protected_state.deployment_config_path.empty()) {
        paths.push_back(config.protected_state.deployment_config_path);
    }
    if (!config.security.route_set_path.empty()) {
        paths.push_back(config.security.route_set_path);
        paths.push_back(config.security.route_generation_state_path);
        paths.push_back(companion(config.security.route_generation_state_path,
                                  ".lock"));
        if (config.security.witness_route_generation) {
            paths.push_back(
                config.security.route_generation_witness_intent_path);
        }
    }
    if (config.security.route_workers_enabled) {
        paths.push_back(config.security.route_worker_state_root);
    }
    if (config.interactive.enabled) {
        paths.push_back(config.interactive.profile_store_root);
        paths.push_back(config.interactive.incarnation_state_path);
        paths.push_back(companion(config.interactive.incarnation_state_path,
                                  ".lock"));
        if (config.security.witness_ratox_incarnation) {
            paths.push_back(
                config.security.ratox_incarnation_witness_intent_path);
        }
        if (config.security.witness_terminal_policy) {
            paths.push_back(
                config.security.terminal_policy_witness_checkpoint_path);
            paths.push_back(
                config.security.terminal_policy_witness_intent_path);
        }
    }
    if (config.sync.enabled) {
        paths.push_back(config.sync.policy_store_root);
        std::error_code error;
        const auto namespace_index =
            config.sync.policy_store_root / "namespaces";
        if (std::filesystem::exists(namespace_index, error)) {
            auto policies = sync::load_namespace_store(
                config.sync.policy_store_root,
                static_cast<std::uint32_t>(::geteuid()));
            if (!policies) return policies.status();
            for (const sync::NamespacePolicy &policy : policies.value()) {
                paths.emplace_back(policy.root);
                paths.push_back(std::filesystem::path{policy.root} /
                                (policy.id + ".transaction.lock"));
            }
        } else if (error) {
            return Status{ErrorCode::io_error,
                          "unable to inspect synchronization policy index: " +
                              error.message()};
        }
    }
    if (config.update.enabled) {
        paths.push_back(config.update.policy_path);
        auto policy = update::load_update_policy(
            config.update.policy_path,
            static_cast<std::uint32_t>(::geteuid()));
        if (!policy) return policy.status();
        paths.push_back(policy.value().root);
        paths.push_back(policy.value().root / "state" / "update.state");
        paths.push_back(policy.value().root / "slots");
        paths.push_back(policy.value().root / "quarantine");
        // The optional current pointer is a deliberately managed symlink.
        // Recursive policy-root enumeration covers its encrypted inode and
        // payload; do not reinterpret it as a traversable configured root.
    }
    paths.erase(std::remove_if(paths.begin(), paths.end(),
                               [](const auto &path) { return path.empty(); }),
                paths.end());
    std::sort(paths.begin(), paths.end());
    paths.erase(std::unique(paths.begin(), paths.end()), paths.end());
    return paths;
}

}  // namespace

Result<Inspection> inspect(const Agent::Config &config) {
    Inspection inspection;
    if (!config.protected_state.require_fscrypt_v2) {
        if (!config.protected_state.root.empty() ||
            !config.protected_state.policy_identifier.empty()) {
            return Status{ErrorCode::invalid_argument,
                          "protected-state root and policy identifier require fscrypt-v2 protection"};
        }
        return inspection;
    }
    inspection.enabled = true;
    auto expected_identifier = security::decode_hex_exact(
        config.protected_state.policy_identifier,
        FSCRYPT_KEY_IDENTIFIER_SIZE,
        "protected-state fscrypt policy identifier");
    if (!expected_identifier) return expected_identifier.status();
    PolicyIdentifier expected_policy{};
    std::copy(expected_identifier.value().begin(),
              expected_identifier.value().end(), expected_policy.begin());
    const std::filesystem::path &root = config.protected_state.root;
    if (!normalized_absolute_nonroot(root)) {
        return Status{ErrorCode::invalid_argument,
                      "protected-state root must be normalized, non-root, and absolute"};
    }
    auto root_descriptor = open_directory_no_follow(
        root, "unable to open protected-state root");
    if (!root_descriptor) return root_descriptor.status();
    struct stat root_metadata {};
    if (::fstat(root_descriptor.value().get(), &root_metadata) != 0) {
        return io_status("unable to inspect protected-state root", root);
    }
    const Status private_root =
        require_private_metadata(root_metadata, root, true);
    if (!private_root.ok()) return private_root;
    auto mount = mount_identifier(root_descriptor.value().get(), root);
    if (!mount) return mount.status();
    auto policy = policy_identifier(root_descriptor.value().get(), root);
    if (!policy) return policy.status();
    if (policy.value() != expected_policy) {
        return Status{
            ErrorCode::invalid_argument,
            "protected-state root policy identifier does not match the configured pin: expected " +
                hex_identifier(expected_policy) + ", observed " +
                hex_identifier(policy.value())};
    }
    const Status key = require_key_present(root_descriptor.value().get(), root,
                                           policy.value());
    if (!key.ok()) return key;

    WalkCounts counts;
    counts.inodes = 1U;
    const Status walked = walk_tree(
        root_descriptor.value().get(), root, mount.value(), policy.value(),
        counts);
    if (!walked.ok()) return walked;

    auto paths = durable_paths(config);
    if (!paths) return paths.status();
    for (const std::filesystem::path &path : paths.value()) {
        const Status verified = verify_configured_path(
            root_descriptor.value().get(), root, path, mount.value(),
            policy.value());
        if (!verified.ok()) return verified;
    }
    auto tmpfs = runtime_on_tmpfs(config.runtime.root);
    if (!tmpfs) return tmpfs.status();
    inspection.runtime_tmpfs = tmpfs.value();
    if (!tmpfs.value()) {
        const Status runtime = verify_configured_path(
            root_descriptor.value().get(), root, config.runtime.root,
            mount.value(), policy.value());
        if (!runtime.ok()) {
            return Status{runtime.code(),
                          "protected runtime must be tmpfs or inside the protected-state root: " +
                              runtime.message()};
        }
    }
    inspection.policy_identifier = hex_identifier(policy.value());
    inspection.configured_paths = paths.value().size();
    inspection.verified_inodes = counts.inodes;
    inspection.protected_symlinks = counts.symlinks;
    return inspection;
}

}  // namespace iotox::protected_state
