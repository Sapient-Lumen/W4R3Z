#pragma once

#if !defined(_WIN32)

#include "sync_linked_peer_pairing.hpp"
#include "sync_linked_peer_user_layout.hpp"
#include "sync_replica_folder_process.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

// Fresh share bootstrap policy. RequireEmpty is the conservative joining-peer
// default: an already populated destination is not silently merged into a
// remote share. AdoptExisting is the explicit first-share/migration behavior.
// Once the deployment manifest is committed, resume permits the ordinary live
// tree regardless of this original bootstrap choice.
enum class SyncLocalShareInitialFilesPolicy : std::uint8_t {
    RequireEmpty = 1U,
    AdoptExisting = 2U,
};

[[nodiscard]] const char* sync_local_share_initial_files_policy_name(
    SyncLocalShareInitialFilesPolicy policy) noexcept;

enum class SyncLocalShareDeploymentDisposition : std::uint8_t {
    Initialized = 1U,
    ResumedExact = 2U,
};

[[nodiscard]] const char* sync_local_share_deployment_disposition_name(
    SyncLocalShareDeploymentDisposition disposition) noexcept;

enum class SyncLocalShareCatalogDisposition : std::uint8_t {
    Initialized = 1U,
    ReusedExisting = 2U,
};

[[nodiscard]] const char* sync_local_share_catalog_disposition_name(
    SyncLocalShareCatalogDisposition disposition) noexcept;

// CLI-independent optional overrides. Defaults are resolved only after the
// committed deployment is known, so maximum_file_bytes can correctly inherit
// a nondefault manifest payload ceiling on resume.
struct SyncLocalShareFolderLimitOverrides final {
    std::optional<std::uint64_t> maximum_entries;
    std::optional<std::uint64_t> maximum_regular_files;
    std::optional<std::uint64_t> maximum_file_bytes;
    std::optional<std::uint64_t> maximum_total_file_bytes;
    std::optional<std::uint64_t> maximum_relative_path_bytes;
    std::optional<std::uint64_t> maximum_directory_depth;
    std::optional<std::uint64_t> maximum_remote_paths;
    std::optional<std::uint64_t> maximum_remote_inspection_paths;

    bool operator==(const SyncLocalShareFolderLimitOverrides&) const = default;
};

struct SyncLocalShareSetupRequest final {
    std::string instance;
    std::filesystem::path state_directory;
    std::filesystem::path files_root;
    std::filesystem::path home_directory;

    // Omitted identities are generated only for a fresh deployment. On resume,
    // supplied values are exact assertions and omitted values accept the
    // committed manifest.
    std::optional<std::string> folder_id;
    std::optional<std::string> local_device_id;
    std::optional<std::uint64_t> local_epoch;
    std::optional<std::uint64_t> max_payload_bytes;

    SyncLocalShareInitialFilesPolicy initial_files_policy =
        SyncLocalShareInitialFilesPolicy::RequireEmpty;
    SyncLocalShareFolderLimitOverrides folder_limit_overrides;
};

struct SyncLocalShareSetupResult final {
    SyncLocalShareUserLayoutPreparation layout_preparation;
    SyncLocalShareInitialFilesPolicy initial_files_policy =
        SyncLocalShareInitialFilesPolicy::RequireEmpty;
    SyncLocalShareDeploymentDisposition deployment_disposition =
        SyncLocalShareDeploymentDisposition::Initialized;
    SyncReplicaDeploymentManifest deployment;
    std::filesystem::path catalog_path;
    SyncLocalShareCatalogDisposition catalog_disposition =
        SyncLocalShareCatalogDisposition::Initialized;
    SyncReplicaFolderConvergencePassLimits folder_limits;
    SyncReplicaFolderCatalogSnapshot catalog_before;
    SyncReplicaFolderCatalogSnapshot catalog_after;
    SyncReplicaSqliteSnapshot replica_before;
    SyncReplicaSqliteSnapshot replica_after;
    SyncReplicaFolderConvergencePassReport initial_pass;
    SyncLinkedPeerIdentityCreationResult identity;
    std::string pairing_card_sha256;
    std::string pairing_verification_code;
};

// Creates or resumes one complete local share using the shipping replica and
// folder owners, then creates/resumes its signed public identity. The only
// subprocesses are exact co-installed anonsync_replica/anonsync_folder siblings
// resolved without PATH or a shell. Every committed path and optional identity
// assertion is re-proved before the result is returned.
[[nodiscard]] SyncLocalShareSetupResult
create_or_resume_sync_local_share_or_throw(
    SyncLocalShareSetupRequest request,
    std::string_view label = "sync local-share setup");

}  // namespace anonsync

#endif
