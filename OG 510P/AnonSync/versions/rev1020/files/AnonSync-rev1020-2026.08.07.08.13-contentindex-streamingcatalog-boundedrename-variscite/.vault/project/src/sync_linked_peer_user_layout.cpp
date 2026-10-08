#include "sync_linked_peer_user_layout.hpp"

#if !defined(_WIN32)

#include "sync_manifest_validation.hpp"

#include <cerrno>
#include <cstring>
#include <filesystem>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

class ScopedFd final {
public:
    ScopedFd() noexcept = default;
    explicit ScopedFd(int descriptor) noexcept : descriptor_(descriptor) {}
    ~ScopedFd() noexcept { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : descriptor_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) reset(other.release());
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return descriptor_; }

private:
    [[nodiscard]] int release() noexcept {
        const int out = descriptor_;
        descriptor_ = -1;
        return out;
    }

    void reset(int descriptor = -1) noexcept {
        if (descriptor_ >= 0) (void)::close(descriptor_);
        descriptor_ = descriptor;
    }

    int descriptor_ = -1;
};

[[nodiscard]] std::string child_label(
    std::string_view label,
    std::string_view child) {
    return std::string(label) + " " + std::string(child);
}

[[noreturn]] void throw_errno(
    std::string_view label,
    std::string_view operation,
    const fs::path& path,
    int error = errno) {
    throw std::runtime_error(
        std::string(label) + " " + std::string(operation) +
        " failed for " + path.generic_string() + ": " +
        std::strerror(error));
}

[[nodiscard]] int directory_open_flags() noexcept {
    int flags = O_RDONLY | O_DIRECTORY;
#ifdef O_CLOEXEC
    flags |= O_CLOEXEC;
#endif
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    return flags;
}

[[nodiscard]] bool same_identity(
    const struct stat& left,
    const struct stat& right) noexcept {
    return left.st_dev == right.st_dev && left.st_ino == right.st_ino;
}

[[nodiscard]] fs::path normalized_absolute_directory_or_throw(
    const fs::path& selected,
    std::string_view label) {
    if (selected.empty() || !selected.is_absolute() ||
        selected.lexically_normal() != selected || selected.filename().empty()) {
        throw std::invalid_argument(
            std::string(label) +
            " must be a lexically normalized absolute directory path");
    }
    return selected;
}

void require_safe_component_or_throw(
    std::string_view component,
    std::string_view label) {
    if (component.empty() || component == "." || component == ".." ||
        component.find('/') != std::string_view::npos ||
        component.find('\0') != std::string_view::npos) {
        throw std::invalid_argument(
            std::string(label) + " contains an unsafe path component");
    }
}

void require_directory_policy_or_throw(
    const struct stat& status,
    bool exact_private_mode,
    std::string_view label,
    const fs::path& path) {
    if (!S_ISDIR(status.st_mode)) {
        throw std::runtime_error(
            std::string(label) + " is not a directory: " +
            path.generic_string());
    }
    if (status.st_uid != ::geteuid()) {
        throw std::runtime_error(
            std::string(label) + " is not owned by the effective user: " +
            path.generic_string());
    }
    const mode_t mode = status.st_mode & 07777U;
    if (exact_private_mode) {
        if (mode != 0700U) {
            throw std::runtime_error(
                std::string(label) + " must have exact mode 0700: " +
                path.generic_string());
        }
    } else if ((mode & 0022U) != 0U) {
        throw std::runtime_error(
            std::string(label) +
            " must not be group/other writable: " + path.generic_string());
    }
}

struct TraversedDirectory final {
    ScopedFd descriptor;
    struct stat identity {};
    bool created = false;
};

[[nodiscard]] TraversedDirectory open_existing_directory_no_symlink_or_throw(
    const fs::path& absolute_directory,
    bool exact_private_mode,
    std::string_view label) {
    ScopedFd current(::open("/", directory_open_flags()));
    if (current.get() < 0) throw_errno(label, "root open", "/");

    struct stat current_status {};
    if (::fstat(current.get(), &current_status) != 0) {
        throw_errno(label, "root fstat", "/");
    }

    fs::path walked = "/";
    for (const fs::path& component_path : absolute_directory.relative_path()) {
        const std::string component = component_path.string();
        if (component.empty() || component == ".") continue;
        require_safe_component_or_throw(component, label);
        walked /= component_path;

        struct stat before {};
        if (::fstatat(
                current.get(), component.c_str(), &before,
                AT_SYMLINK_NOFOLLOW) != 0) {
            throw_errno(label, "component inspection", walked);
        }
        if (S_ISLNK(before.st_mode)) {
            throw std::runtime_error(
                std::string(label) + " refuses symbolic-link component: " +
                walked.generic_string());
        }
        if (!S_ISDIR(before.st_mode)) {
            throw std::runtime_error(
                std::string(label) + " component is not a directory: " +
                walked.generic_string());
        }

        ScopedFd next(::openat(
            current.get(), component.c_str(), directory_open_flags()));
        if (next.get() < 0) {
            throw_errno(label, "component open", walked);
        }
        struct stat after {};
        if (::fstat(next.get(), &after) != 0) {
            throw_errno(label, "component fstat", walked);
        }
        if (!same_identity(before, after) || !S_ISDIR(after.st_mode)) {
            throw std::runtime_error(
                std::string(label) +
                " component changed during descriptor traversal: " +
                walked.generic_string());
        }
        current = std::move(next);
        current_status = after;
    }

    require_directory_policy_or_throw(
        current_status, exact_private_mode, label, absolute_directory);
    return {std::move(current), current_status, false};
}

[[nodiscard]] TraversedDirectory ensure_private_child_or_throw(
    const TraversedDirectory& parent,
    const fs::path& parent_path,
    std::string_view component_view,
    std::string_view label) {
    const std::string component(component_view);
    require_safe_component_or_throw(component, label);
    const fs::path child_path = parent_path / component;

    struct stat before {};
    bool created = false;
    if (::fstatat(
            parent.descriptor.get(), component.c_str(), &before,
            AT_SYMLINK_NOFOLLOW) != 0) {
        const int error = errno;
        if (error != ENOENT) {
            throw_errno(label, "child inspection", child_path, error);
        }
        if (::mkdirat(parent.descriptor.get(), component.c_str(), 0700) != 0) {
            const int mkdir_error = errno;
            if (mkdir_error != EEXIST) {
                throw_errno(
                    label, "private child creation", child_path, mkdir_error);
            }
        } else {
            created = true;
        }
        if (::fstatat(
                parent.descriptor.get(), component.c_str(), &before,
                AT_SYMLINK_NOFOLLOW) != 0) {
            throw_errno(label, "created child inspection", child_path);
        }
    }

    if (S_ISLNK(before.st_mode)) {
        throw std::runtime_error(
            std::string(label) + " refuses symbolic-link child: " +
            child_path.generic_string());
    }
    // A newly created directory can inherit set-group-ID from its parent even
    // though mkdirat was called with 0700. Admit only that safe provisional
    // state, then normalize through the retained no-follow descriptor. Never
    // repair an entry that another actor created or that already existed.
    require_directory_policy_or_throw(
        before, !created, label, child_path);

    ScopedFd child(::openat(
        parent.descriptor.get(), component.c_str(), directory_open_flags()));
    if (child.get() < 0) throw_errno(label, "private child open", child_path);
    struct stat after {};
    if (::fstat(child.get(), &after) != 0) {
        throw_errno(label, "private child fstat", child_path);
    }
    if (!same_identity(before, after) || !S_ISDIR(after.st_mode)) {
        throw std::runtime_error(
            std::string(label) +
            " private child changed during descriptor traversal: " +
            child_path.generic_string());
    }
    if (created) {
        if (::fchmod(child.get(), 0700U) != 0) {
            throw_errno(label, "created-child mode normalization", child_path);
        }
        if (::fsync(child.get()) != 0) {
            throw_errno(label, "created-child fsync", child_path);
        }
        if (::fstat(child.get(), &after) != 0) {
            throw_errno(label, "normalized child fstat", child_path);
        }
        if (!same_identity(before, after) || !S_ISDIR(after.st_mode)) {
            throw std::runtime_error(
                std::string(label) +
                " private child changed during mode normalization: " +
                child_path.generic_string());
        }
    }
    require_directory_policy_or_throw(after, true, label, child_path);

    if (created && ::fsync(parent.descriptor.get()) != 0) {
        throw_errno(label, "created-child parent fsync", parent_path);
    }
    return {std::move(child), after, created};
}

[[nodiscard]] TraversedDirectory ensure_optional_config_directory_or_throw(
    const TraversedDirectory& home,
    const fs::path& home_path,
    std::string_view label) {
    const std::string component = ".config";
    const fs::path child_path = home_path / component;
    struct stat before {};
    bool created = false;
    if (::fstatat(
            home.descriptor.get(), component.c_str(), &before,
            AT_SYMLINK_NOFOLLOW) != 0) {
        const int error = errno;
        if (error != ENOENT) {
            throw_errno(label, "config-directory inspection", child_path, error);
        }
        if (::mkdirat(home.descriptor.get(), component.c_str(), 0700) != 0) {
            const int mkdir_error = errno;
            if (mkdir_error != EEXIST) {
                throw_errno(
                    label, "config-directory creation", child_path,
                    mkdir_error);
            }
        } else {
            created = true;
        }
        if (::fstatat(
                home.descriptor.get(), component.c_str(), &before,
                AT_SYMLINK_NOFOLLOW) != 0) {
            throw_errno(label, "created config-directory inspection", child_path);
        }
    }

    if (S_ISLNK(before.st_mode)) {
        throw std::runtime_error(
            std::string(label) +
            " refuses symbolic-link .config directory: " +
            child_path.generic_string());
    }
    require_directory_policy_or_throw(
        before, false, label, child_path);

    ScopedFd child(::openat(
        home.descriptor.get(), component.c_str(), directory_open_flags()));
    if (child.get() < 0) {
        throw_errno(label, "config-directory open", child_path);
    }
    struct stat after {};
    if (::fstat(child.get(), &after) != 0) {
        throw_errno(label, "config-directory fstat", child_path);
    }
    if (!same_identity(before, after) || !S_ISDIR(after.st_mode)) {
        throw std::runtime_error(
            std::string(label) +
            " .config directory changed during descriptor traversal: " +
            child_path.generic_string());
    }
    if (created) {
        if (::fchmod(child.get(), 0700U) != 0) {
            throw_errno(
                label, "created config-directory mode normalization",
                child_path);
        }
        if (::fsync(child.get()) != 0) {
            throw_errno(label, "created config-directory fsync", child_path);
        }
        if (::fstat(child.get(), &after) != 0) {
            throw_errno(label, "normalized config-directory fstat", child_path);
        }
        if (!same_identity(before, after) || !S_ISDIR(after.st_mode)) {
            throw std::runtime_error(
                std::string(label) +
                " .config directory changed during mode normalization: " +
                child_path.generic_string());
        }
    }
    require_directory_policy_or_throw(
        after, created, label, child_path);
    if (created && ::fsync(home.descriptor.get()) != 0) {
        throw_errno(label, "config-directory parent fsync", home_path);
    }
    return {std::move(child), after, created};
}

void verify_exact_directory_identity_or_throw(
    const fs::path& path,
    const struct stat& expected,
    bool exact_private_mode,
    std::string_view label) {
    TraversedDirectory repeated =
        open_existing_directory_no_symlink_or_throw(
            path, exact_private_mode, label);
    if (!same_identity(repeated.identity, expected)) {
        throw std::runtime_error(
            std::string(label) +
            " directory identity changed before layout completion: " +
            path.generic_string());
    }
}

struct PreparedConfigurationRoot final {
    fs::path home;
    fs::path anonsync_path;
    TraversedDirectory anonsync_owner;
};

[[nodiscard]] fs::path
canonical_existing_directory_without_symlink_or_throw(
    const fs::path& selected,
    std::string_view label) {
    const fs::path normalized =
        normalized_absolute_directory_or_throw(selected, label);
    std::error_code error;
    const fs::file_status status = fs::symlink_status(normalized, error);
    if (error || fs::is_symlink(status) || !fs::is_directory(status)) {
        throw std::runtime_error(
            std::string(label) +
            " must be an existing non-symlink directory: " +
            normalized.generic_string());
    }
    const fs::path canonical = fs::canonical(normalized, error);
    if (error || canonical != normalized) {
        throw std::runtime_error(
            std::string(label) +
            " contains a symbolic-link or noncanonical component: " +
            normalized.generic_string());
    }
    return canonical;
}

[[nodiscard]] bool path_is_same_or_descendant(
    const fs::path& candidate,
    const fs::path& ancestor) noexcept {
    auto candidate_it = candidate.begin();
    const auto candidate_end = candidate.end();
    for (auto ancestor_it = ancestor.begin();
         ancestor_it != ancestor.end(); ++ancestor_it) {
        if (candidate_it == candidate_end || *candidate_it != *ancestor_it) {
            return false;
        }
        ++candidate_it;
    }
    return true;
}

[[nodiscard]] PreparedConfigurationRoot
prepare_configuration_root_or_throw(
    const fs::path& absolute_home_directory,
    std::string_view label) {
    const fs::path home = normalized_absolute_directory_or_throw(
        absolute_home_directory, child_label(label, "HOME"));
    TraversedDirectory home_owner =
        open_existing_directory_no_symlink_or_throw(
            home, false, child_label(label, "HOME"));
    TraversedDirectory config_owner =
        ensure_optional_config_directory_or_throw(
            home_owner, home, child_label(label, ".config"));
    const fs::path config_base = home / ".config";
    TraversedDirectory anonsync_owner = ensure_private_child_or_throw(
        config_owner, config_base, "anonsync",
        child_label(label, "configuration root"));
    return {
        .home = home,
        .anonsync_path = config_base / "anonsync",
        .anonsync_owner = std::move(anonsync_owner),
    };
}

}  // namespace

SyncLinkedPeerUserLayout prepare_sync_linked_peer_user_layout_or_throw(
    std::string_view instance_view,
    const fs::path& absolute_home_directory,
    const fs::path& absolute_runtime_base_directory,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync linked-peer user layout label must not be empty");
    }
    const std::string instance(instance_view);
    if (!sync_id_is_valid(instance)) {
        throw std::invalid_argument(
            label + " instance is not a lowercase portable sync ID");
    }

    const fs::path runtime_base = normalized_absolute_directory_or_throw(
        absolute_runtime_base_directory,
        child_label(label, "XDG_RUNTIME_DIR"));

    PreparedConfigurationRoot configuration =
        prepare_configuration_root_or_throw(
            absolute_home_directory, label);
    TraversedDirectory linked_peers_owner = ensure_private_child_or_throw(
        configuration.anonsync_owner, configuration.anonsync_path,
        "linked-peers",
        child_label(label, "linked-peer directory"));
    const fs::path configuration_directory =
        configuration.anonsync_path / "linked-peers";

    TraversedDirectory runtime_base_owner =
        open_existing_directory_no_symlink_or_throw(
            runtime_base, true, child_label(label, "XDG_RUNTIME_DIR"));
    const std::string runtime_basename = "anonsync-" + instance;
    TraversedDirectory runtime_owner = ensure_private_child_or_throw(
        runtime_base_owner, runtime_base, runtime_basename,
        child_label(label, "runtime directory"));
    const fs::path runtime_directory = runtime_base / runtime_basename;

    verify_exact_directory_identity_or_throw(
        configuration_directory, linked_peers_owner.identity, true,
        child_label(label, "linked-peer directory reproof"));
    verify_exact_directory_identity_or_throw(
        runtime_directory, runtime_owner.identity, true,
        child_label(label, "runtime directory reproof"));

    return {
        .instance = instance,
        .home_directory = configuration.home,
        .runtime_base_directory = runtime_base,
        .configuration_directory = configuration_directory,
        .configuration_path = configuration_directory / (instance + ".json"),
        .runtime_directory = runtime_directory,
        .status_socket_path = runtime_directory / "status.sock",
        .systemd_unit =
            "anonsync-linked-peer@" + instance + ".service",
    };
}

SyncLinkedPeerIdentityLayout
prepare_sync_linked_peer_identity_layout_or_throw(
    std::string_view instance_view,
    const fs::path& absolute_home_directory,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync linked-peer identity layout label must not be empty");
    }
    const std::string instance(instance_view);
    if (!sync_id_is_valid(instance)) {
        throw std::invalid_argument(
            label + " instance is not a lowercase portable sync ID");
    }

    PreparedConfigurationRoot configuration =
        prepare_configuration_root_or_throw(
            absolute_home_directory, label);
    TraversedDirectory identities_owner = ensure_private_child_or_throw(
        configuration.anonsync_owner, configuration.anonsync_path,
        "linked-identities",
        child_label(label, "linked-identity directory"));
    const fs::path identities_path =
        configuration.anonsync_path / "linked-identities";
    TraversedDirectory identity_owner = ensure_private_child_or_throw(
        identities_owner, identities_path, instance,
        child_label(label, "instance identity directory"));
    const fs::path identity_path = identities_path / instance;

    verify_exact_directory_identity_or_throw(
        identities_path, identities_owner.identity, true,
        child_label(label, "linked-identity directory reproof"));
    verify_exact_directory_identity_or_throw(
        identity_path, identity_owner.identity, true,
        child_label(label, "instance identity directory reproof"));

    return {
        .instance = instance,
        .home_directory = configuration.home,
        .identity_directory = identity_path,
        .private_key_path = identity_path / "local.key",
        .certificate_path = identity_path / "local.pem",
        .pairing_card_path = identity_path / "pairing-card.json",
        .peer_trust_path = identity_path / "peer-trust.pem",
    };
}

const char* sync_local_share_directory_disposition_name(
    SyncLocalShareDirectoryDisposition disposition) noexcept {
    switch (disposition) {
        case SyncLocalShareDirectoryDisposition::Created:
            return "created";
        case SyncLocalShareDirectoryDisposition::ReusedExact:
            return "reused_exact";
    }
    return "unknown";
}

SyncLocalShareUserLayoutPreparation
prepare_sync_local_share_user_layout_or_throw(
    std::string_view instance_view,
    const fs::path& absolute_state_directory,
    const fs::path& absolute_files_root,
    std::string_view label_view) {
    const std::string label(label_view);
    if (label.empty()) {
        throw std::invalid_argument(
            "sync local-share user layout label must not be empty");
    }
    const std::string instance(instance_view);
    if (!sync_id_is_valid(instance)) {
        throw std::invalid_argument(
            label + " instance is not a lowercase portable sync ID");
    }

    const fs::path state = normalized_absolute_directory_or_throw(
        absolute_state_directory, child_label(label, "state directory"));
    if (state.filename() != fs::path(instance)) {
        throw std::invalid_argument(
            label + " state directory basename must equal the instance ID");
    }
    const fs::path files =
        canonical_existing_directory_without_symlink_or_throw(
            absolute_files_root, child_label(label, "files root"));
    const fs::path state_parent = state.parent_path();
    if (state_parent.empty()) {
        throw std::invalid_argument(
            label + " state directory must have an absolute parent");
    }
    TraversedDirectory state_parent_owner =
        open_existing_directory_no_symlink_or_throw(
            state_parent, false, child_label(label, "state parent"));

    // The selected parent traversal proves that the not-yet-created state path
    // has no symbolic-link ancestor. Reject namespace overlap before mutation.
    if (path_is_same_or_descendant(state, files) ||
        path_is_same_or_descendant(files, state)) {
        throw std::invalid_argument(
            label +
            " state directory and synchronized files root must be disjoint");
    }

    TraversedDirectory state_owner = ensure_private_child_or_throw(
        state_parent_owner, state_parent, instance,
        child_label(label, "state directory"));
    TraversedDirectory payload_owner = ensure_private_child_or_throw(
        state_owner, state, "payload",
        child_label(label, "payload root"));
    const fs::path payload = state / "payload";

    verify_exact_directory_identity_or_throw(
        state, state_owner.identity, true,
        child_label(label, "state directory reproof"));
    verify_exact_directory_identity_or_throw(
        payload, payload_owner.identity, true,
        child_label(label, "payload root reproof"));
    (void)canonical_existing_directory_without_symlink_or_throw(
        files, child_label(label, "files root reproof"));

    return {
        .layout = {
            .instance = instance,
            .state_directory = state,
            .files_root = files,
            .manifest_path = state / "deployment.json",
            .replica_database_path = state / "replica.sqlite3",
            .payload_root = payload,
            .effect_database_path = state / "effects.sqlite3",
            .membership_database_path = state / "membership.sqlite3",
            .membership_anchor_database_path =
                state / "membership-anchor.sqlite3",
        },
        .state_directory_disposition =
            state_owner.created
                ? SyncLocalShareDirectoryDisposition::Created
                : SyncLocalShareDirectoryDisposition::ReusedExact,
        .payload_root_disposition =
            payload_owner.created
                ? SyncLocalShareDirectoryDisposition::Created
                : SyncLocalShareDirectoryDisposition::ReusedExact,
    };
}

}  // namespace anonsync

#endif
