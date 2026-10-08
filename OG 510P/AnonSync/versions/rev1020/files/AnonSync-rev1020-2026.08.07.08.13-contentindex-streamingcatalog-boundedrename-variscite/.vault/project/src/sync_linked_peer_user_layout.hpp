#pragma once

#if !defined(_WIN32)

#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>

namespace anonsync {

// Exact per-user paths consumed by the installed linked-peer systemd unit.
// The instance spelling uses the portable sync-ID grammar, so it is safe as a
// single filename component and as the unescaped systemd instance selected by
// the current unit template.
struct SyncLinkedPeerUserLayout final {
    std::string instance;
    std::filesystem::path home_directory;
    std::filesystem::path runtime_base_directory;
    std::filesystem::path configuration_directory;
    std::filesystem::path configuration_path;
    std::filesystem::path runtime_directory;
    std::filesystem::path status_socket_path;
    std::string systemd_unit;

    bool operator==(const SyncLinkedPeerUserLayout&) const = default;
};

// Share/peer-scoped identity material for one installed linked-peer instance.
// Keeping the identity below a separate protected directory prevents service
// configuration files, public pairing cards, private keys, and peer trust
// anchors from becoming one ambiguous filename namespace.
struct SyncLinkedPeerIdentityLayout final {
    std::string instance;
    std::filesystem::path home_directory;
    std::filesystem::path identity_directory;
    std::filesystem::path private_key_path;
    std::filesystem::path certificate_path;
    std::filesystem::path pairing_card_path;
    std::filesystem::path peer_trust_path;

    bool operator==(const SyncLinkedPeerIdentityLayout&) const = default;
};

// One owner-only local share namespace selected by an explicit absolute state
// directory. The directory basename is the service instance, which keeps the
// deployment, identity, and installed unit names from drifting apart without
// adding another mutable configuration document. Ordinary synchronized files
// remain outside this namespace.
struct SyncLocalShareUserLayout final {
    std::string instance;
    std::filesystem::path state_directory;
    std::filesystem::path files_root;
    std::filesystem::path manifest_path;
    std::filesystem::path replica_database_path;
    std::filesystem::path payload_root;
    std::filesystem::path effect_database_path;
    std::filesystem::path membership_database_path;
    std::filesystem::path membership_anchor_database_path;

    bool operator==(const SyncLocalShareUserLayout&) const = default;
};

enum class SyncLocalShareDirectoryDisposition : std::uint8_t {
    Created = 1U,
    ReusedExact = 2U,
};

struct SyncLocalShareUserLayoutPreparation final {
    SyncLocalShareUserLayout layout;
    SyncLocalShareDirectoryDisposition state_directory_disposition =
        SyncLocalShareDirectoryDisposition::Created;
    SyncLocalShareDirectoryDisposition payload_root_disposition =
        SyncLocalShareDirectoryDisposition::Created;
};

[[nodiscard]] const char* sync_local_share_directory_disposition_name(
    SyncLocalShareDirectoryDisposition disposition) noexcept;

// Creates or reuses only the two AnonSync-owned directory chains:
//
//   HOME/.config/anonsync/linked-peers/        exact 0700 from anonsync down
//   XDG_RUNTIME_DIR/anonsync-INSTANCE/          exact 0700
//
// Every component is traversed descriptor-relatively without following
// symbolic links. HOME and its optional .config directory must be owned by the
// effective user and must not be group/other writable. XDG_RUNTIME_DIR must be
// effective-user-owned with exact mode 0700. Existing AnonSync-owned
// directories must already have exact mode 0700; this function never repairs
// permissions silently. Newly created directory entries and their parents are
// synchronized before return.
[[nodiscard]] SyncLinkedPeerUserLayout
prepare_sync_linked_peer_user_layout_or_throw(
    std::string_view instance,
    const std::filesystem::path& absolute_home_directory,
    const std::filesystem::path& absolute_runtime_base_directory,
    std::string_view label = "sync linked-peer user layout");

// Creates or reuses:
//
//   HOME/.config/anonsync/linked-identities/INSTANCE/   exact 0700
//
// with the same descriptor-relative, no-follow, ownership, mode, and durable
// parent rules as the service layout. The returned file paths are only names;
// this owner creates no key, certificate, card, or trust file.
[[nodiscard]] SyncLinkedPeerIdentityLayout
prepare_sync_linked_peer_identity_layout_or_throw(
    std::string_view instance,
    const std::filesystem::path& absolute_home_directory,
    std::string_view label = "sync linked-peer identity layout");

// Creates or reuses the selected state leaf and its payload child with exact
// mode 0700, descriptor-relative no-follow traversal, effective-user ownership,
// and parent-directory durability. The state directory basename must equal the
// portable instance ID. The existing files root must contain no symlink path
// component, and neither directory may contain the other.
[[nodiscard]] SyncLocalShareUserLayoutPreparation
prepare_sync_local_share_user_layout_or_throw(
    std::string_view instance,
    const std::filesystem::path& absolute_state_directory,
    const std::filesystem::path& absolute_files_root,
    std::string_view label = "sync local-share user layout");

}  // namespace anonsync

#endif
