#pragma once

#include "sync_replica_deployment_identity.hpp"
#include "sync_replica_model.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint64_t kSyncReplicaDeploymentManifestMaxBytes =
    16U * 1024U;
inline constexpr std::uint64_t kSyncReplicaDeploymentManifestMaxPayloadBytes =
    64U * 1024U * 1024U;

// Immutable deployment authority selected by the explicit product bootstrap
// command. Operational commands load this document first and derive every
// store path, local identity, and payload ceiling from it; independently typed
// path arguments cannot be mixed into a committed store set.
struct SyncReplicaDeploymentManifest final {
    // Fresh, cryptographically random store-set identity. Every selected SQLite
    // database and product-bound payload lease anchor carries this same value.
    std::string deployment_id;

    std::filesystem::path manifest_path;
    std::filesystem::path replica_db;
    std::optional<std::filesystem::path> payload_root;
    std::optional<std::filesystem::path> effect_db;
    std::optional<std::filesystem::path> files_root;
    std::optional<std::filesystem::path> membership_db;
    std::optional<std::filesystem::path> anchor_db;
    std::string folder_id;
    SyncReplicaActor local_actor;
    std::uint64_t max_payload_bytes = 0U;

    // Empty before digest computation. Populated before store bootstrap so every
    // store can bind the exact manifest configuration, and re-proved when the
    // exact durable manifest is decoded.
    std::string manifest_digest;

    bool operator==(const SyncReplicaDeploymentManifest&) const = default;
};

[[nodiscard]] const char* sync_replica_deployment_profile_name(
    const SyncReplicaDeploymentManifest& manifest) noexcept;

[[nodiscard]] std::uint64_t
sync_replica_deployment_authority_resource_count(
    const SyncReplicaDeploymentManifest& manifest) noexcept;

void validate_sync_replica_deployment_manifest_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label);

// Computes the self-digest over the canonical unsigned v2 document. A
// pre-populated manifest_digest must either be exact or the call fails.
[[nodiscard]] std::string
compute_sync_replica_deployment_manifest_digest_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label);

[[nodiscard]] SyncReplicaDeploymentIdentity
sync_replica_deployment_identity_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label);

[[nodiscard]] std::string encode_sync_replica_deployment_manifest_or_throw(
    const SyncReplicaDeploymentManifest& manifest,
    const std::string& label);

// Decodes exact canonical deployment-manifest bytes while binding them to the
// caller-selected final manifest pathname. Bootstrap intent records use this
// surface because the authority bytes are durably staged at a different,
// deterministic pathname before the final commit marker exists.
[[nodiscard]] SyncReplicaDeploymentManifest
decode_sync_replica_deployment_manifest_or_throw(
    std::string_view exact_manifest_bytes,
    const std::filesystem::path& expected_absolute_manifest_path,
    const std::string& label);

[[nodiscard]] SyncReplicaDeploymentManifest
read_sync_replica_deployment_manifest_or_throw(
    const std::filesystem::path& absolute_manifest_path,
    const std::string& label);


}  // namespace anonsync
