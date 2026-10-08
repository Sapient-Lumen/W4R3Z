#include "sync_linked_peer_user_layout.hpp"

#if !defined(_WIN32)

#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sys/stat.h>
#include <unistd.h>

namespace {

namespace fs = std::filesystem;
std::size_t checks = 0U;

void require(bool condition, std::string_view message) {
    ++checks;
    if (!condition) throw std::runtime_error(std::string(message));
}

template <typename Function>
void require_throws(Function&& function, std::string_view message) {
    ++checks;
    try {
        std::forward<Function>(function)();
    } catch (const std::exception&) {
        return;
    }
    throw std::runtime_error(std::string(message));
}

class TemporaryDirectory final {
public:
    TemporaryDirectory() {
        std::string pattern = "/tmp/anonsync-user-layout-test-XXXXXX";
        std::vector<char> writable(pattern.begin(), pattern.end());
        writable.push_back('\0');
        char* selected = ::mkdtemp(writable.data());
        if (selected == nullptr) {
            throw std::runtime_error("mkdtemp failed");
        }
        path_ = selected;
        chmod_or_throw(path_, 0700U);
    }

    ~TemporaryDirectory() noexcept {
        std::error_code error;
        fs::remove_all(path_, error);
    }

    TemporaryDirectory(const TemporaryDirectory&) = delete;
    TemporaryDirectory& operator=(const TemporaryDirectory&) = delete;

    [[nodiscard]] const fs::path& path() const noexcept { return path_; }

    static void chmod_or_throw(const fs::path& path, mode_t mode) {
        if (::chmod(path.c_str(), mode) != 0) {
            throw std::runtime_error("chmod failed for " + path.string());
        }
    }

private:
    fs::path path_;
};

void make_directory(const fs::path& path, mode_t mode) {
    if (!fs::create_directory(path)) {
        throw std::runtime_error("could not create " + path.string());
    }
    TemporaryDirectory::chmod_or_throw(path, mode);
}

void require_mode(const fs::path& path, mode_t expected) {
    struct stat status {};
    require(::lstat(path.c_str(), &status) == 0, "path must exist");
    require(S_ISDIR(status.st_mode), "path must be a directory");
    require((status.st_mode & 07777U) == expected, "directory mode mismatch");
    require(status.st_uid == ::geteuid(), "directory owner mismatch");
}

}  // namespace

int main() {
    try {
        TemporaryDirectory temporary;
        const fs::path home = temporary.path() / "home";
        const fs::path runtime = temporary.path() / "runtime";
        make_directory(home, 0700U);
        make_directory(runtime, 0700U);

        const auto first =
            anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                "main-peer", home, runtime, "layout test");
        require(first.instance == "main-peer", "instance must be exact");
        require(first.home_directory == home, "HOME must be exact");
        require(first.runtime_base_directory == runtime,
                "runtime base must be exact");
        require(first.configuration_directory ==
                    home / ".config" / "anonsync" / "linked-peers",
                "configuration directory must match the installed unit");
        require(first.configuration_path ==
                    home / ".config" / "anonsync" / "linked-peers" /
                        "main-peer.json",
                "configuration path must match the installed unit");
        require(first.runtime_directory == runtime / "anonsync-main-peer",
                "runtime directory must match RuntimeDirectory=");
        require(first.status_socket_path ==
                    runtime / "anonsync-main-peer" / "status.sock",
                "status path must match the service configuration");
        require(first.systemd_unit ==
                    "anonsync-linked-peer@main-peer.service",
                "systemd unit spelling must be exact");
        require_mode(home / ".config", 0700U);
        require_mode(home / ".config" / "anonsync", 0700U);
        require_mode(first.configuration_directory, 0700U);
        require_mode(first.runtime_directory, 0700U);

        const auto repeated =
            anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                "main-peer", home, runtime, "layout repeat");
        require(repeated == first, "layout preparation must be idempotent");

        const auto identity =
            anonsync::prepare_sync_linked_peer_identity_layout_or_throw(
                "main-peer", home, "identity layout test");
        require(identity.instance == "main-peer",
                "identity instance must be exact");
        require(identity.home_directory == home,
                "identity HOME must be exact");
        require(identity.identity_directory ==
                    home / ".config" / "anonsync" / "linked-identities" /
                        "main-peer",
                "identity directory must be instance-scoped");
        require(identity.private_key_path ==
                    identity.identity_directory / "local.key",
                "private-key path must be exact");
        require(identity.certificate_path ==
                    identity.identity_directory / "local.pem",
                "certificate path must be exact");
        require(identity.pairing_card_path ==
                    identity.identity_directory / "pairing-card.json",
                "pairing-card path must be exact");
        require(identity.peer_trust_path ==
                    identity.identity_directory / "peer-trust.pem",
                "peer-trust path must be exact");
        require_mode(home / ".config" / "anonsync" / "linked-identities",
                     0700U);
        require_mode(identity.identity_directory, 0700U);
        const auto identity_repeated =
            anonsync::prepare_sync_linked_peer_identity_layout_or_throw(
                "main-peer", home, "identity layout repeat");
        require(identity_repeated == identity,
                "identity layout preparation must be idempotent");

        const auto second =
            anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                "backup_2", home, runtime, "second layout");
        require(second.configuration_directory == first.configuration_directory,
                "instances must share only the protected config directory");
        require(second.runtime_directory != first.runtime_directory,
                "instances must have distinct runtime directories");
        require_mode(second.runtime_directory, 0700U);

        require_throws(
            [&] {
                (void)anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                    "../escape", home, runtime, "bad instance");
            },
            "unsafe instance must be rejected");
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                    "Uppercase", home, runtime, "bad instance");
            },
            "non-portable instance must be rejected");
        require_throws(
            [&] {
                (void)anonsync::
                    prepare_sync_linked_peer_identity_layout_or_throw(
                        "../escape", home, "bad identity instance");
            },
            "unsafe identity instance must be rejected");
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                    "main-peer", fs::path("relative-home"), runtime,
                    "relative HOME");
            },
            "relative HOME must be rejected");

        const fs::path loose_runtime = temporary.path() / "loose-runtime";
        make_directory(loose_runtime, 0755U);
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                    "peer", home, loose_runtime, "loose runtime");
            },
            "runtime base without exact 0700 must be rejected");

        const fs::path loose_home = temporary.path() / "loose-home";
        make_directory(loose_home, 0770U);
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                    "peer", loose_home, runtime, "loose HOME");
            },
            "group-writable HOME must be rejected");

        const fs::path symlink_home = temporary.path() / "symlink-home";
        const fs::path symlink_target = temporary.path() / "symlink-target";
        make_directory(symlink_home, 0700U);
        make_directory(symlink_target, 0700U);
        fs::create_directory_symlink(symlink_target, symlink_home / ".config");
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                    "peer", symlink_home, runtime, "symlink config");
            },
            "symbolic-link .config must be rejected");
        require(!fs::exists(symlink_target / "anonsync"),
                "symlink target must receive no AnonSync directories");

        const fs::path public_config_home =
            temporary.path() / "public-config-home";
        make_directory(public_config_home, 0700U);
        make_directory(public_config_home / ".config", 0755U);
        const auto public_config =
            anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                "peer", public_config_home, runtime,
                "standard public config");
        require_mode(public_config_home / ".config", 0755U);
        require_mode(public_config.configuration_directory, 0700U);

        const fs::path local_state_parent =
            temporary.path() / "local-share-state";
        const fs::path local_files = temporary.path() / "local-share-files";
        make_directory(local_state_parent, 02700U);
        make_directory(local_files, 0700U);
        const fs::path local_state = local_state_parent / "share-main";
        const auto local_share =
            anonsync::prepare_sync_local_share_user_layout_or_throw(
                "share-main", local_state, local_files,
                "local share layout");
        require(local_share.layout.instance == "share-main",
                "local-share instance must be exact");
        require(local_share.layout.state_directory == local_state,
                "local-share state directory must be exact");
        require(local_share.layout.files_root == local_files,
                "local-share files root must be exact");
        require(local_share.layout.manifest_path ==
                    local_state / "deployment.json",
                "local-share manifest path must be derived");
        require(local_share.layout.replica_database_path ==
                    local_state / "replica.sqlite3",
                "local-share replica database path must be derived");
        require(local_share.layout.payload_root == local_state / "payload",
                "local-share payload root must be derived");
        require(local_share.layout.effect_database_path ==
                    local_state / "effects.sqlite3",
                "local-share effect database path must be derived");
        require(local_share.layout.membership_database_path ==
                    local_state / "membership.sqlite3",
                "local-share membership database path must be derived");
        require(local_share.layout.membership_anchor_database_path ==
                    local_state / "membership-anchor.sqlite3",
                "local-share membership anchor path must be derived");
        require(local_share.state_directory_disposition ==
                    anonsync::SyncLocalShareDirectoryDisposition::Created,
                "first local-share state preparation must report creation");
        require(local_share.payload_root_disposition ==
                    anonsync::SyncLocalShareDirectoryDisposition::Created,
                "first local-share payload preparation must report creation");
        require_mode(local_state, 0700U);
        require_mode(local_state / "payload", 0700U);
        require_mode(local_state_parent, 02700U);

        const auto local_share_repeated =
            anonsync::prepare_sync_local_share_user_layout_or_throw(
                "share-main", local_state, local_files,
                "local share layout repeat");
        require(local_share_repeated.layout == local_share.layout,
                "local-share layout must be idempotent");
        require(local_share_repeated.state_directory_disposition ==
                    anonsync::SyncLocalShareDirectoryDisposition::ReusedExact,
                "repeated state preparation must report exact reuse");
        require(local_share_repeated.payload_root_disposition ==
                    anonsync::SyncLocalShareDirectoryDisposition::ReusedExact,
                "repeated payload preparation must report exact reuse");

        require_throws(
            [&] {
                (void)anonsync::prepare_sync_local_share_user_layout_or_throw(
                    "other-name", local_state, local_files,
                    "mismatched state basename");
            },
            "state basename drift must be rejected");

        const fs::path overlapping_files =
            temporary.path() / "overlapping-files";
        make_directory(overlapping_files, 0700U);
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_local_share_user_layout_or_throw(
                    "inside-files", overlapping_files / "inside-files",
                    overlapping_files, "overlapping local share");
            },
            "state below the files root must be rejected");
        require(!fs::exists(overlapping_files / "inside-files"),
                "overlap rejection must precede state mutation");

        const fs::path wrong_state_parent =
            temporary.path() / "wrong-state-parent";
        const fs::path wrong_state_files =
            temporary.path() / "wrong-state-files";
        make_directory(wrong_state_parent, 0700U);
        make_directory(wrong_state_files, 0700U);
        make_directory(wrong_state_parent / "wrong-state", 0755U);
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_local_share_user_layout_or_throw(
                    "wrong-state", wrong_state_parent / "wrong-state",
                    wrong_state_files, "wrong existing state mode");
            },
            "an existing nonprivate state directory must be rejected");
        require_mode(wrong_state_parent / "wrong-state", 0755U);
        require(!fs::exists(wrong_state_parent / "wrong-state" / "payload"),
                "wrong existing state mode must not be repaired or extended");

        const fs::path files_symlink_target =
            temporary.path() / "files-symlink-target";
        const fs::path files_symlink = temporary.path() / "files-symlink";
        make_directory(files_symlink_target, 0700U);
        fs::create_directory_symlink(files_symlink_target, files_symlink);
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_local_share_user_layout_or_throw(
                    "symlink-files", local_state_parent / "symlink-files",
                    files_symlink, "symbolic files root");
            },
            "symbolic-link files root must be rejected");
        require(!fs::exists(local_state_parent / "symlink-files"),
                "symbolic files-root rejection must precede state mutation");

        const fs::path wrong_owned_mode_home =
            temporary.path() / "wrong-owned-mode-home";
        make_directory(wrong_owned_mode_home, 0700U);
        make_directory(wrong_owned_mode_home / ".config", 0700U);
        make_directory(
            wrong_owned_mode_home / ".config" / "anonsync", 0755U);
        require_throws(
            [&] {
                (void)anonsync::prepare_sync_linked_peer_user_layout_or_throw(
                    "peer", wrong_owned_mode_home, runtime,
                    "wrong AnonSync mode");
            },
            "existing AnonSync-owned directory must retain exact 0700");

        std::cout << "sync linked-peer user layout tests: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync linked-peer user layout test failed after "
                  << checks << " checks: " << error.what() << '\n';
        return 1;
    }
}

#else

int main() { return 0; }

#endif
