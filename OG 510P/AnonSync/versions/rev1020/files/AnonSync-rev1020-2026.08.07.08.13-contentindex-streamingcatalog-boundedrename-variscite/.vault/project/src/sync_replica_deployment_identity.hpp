#pragma once

#include "sync_replica_model.hpp"

#include <filesystem>
#include <string>
#include <string_view>

namespace anonsync {

// One unguessable identity shared by every authority store selected by a
// deployment manifest. The manifest digest binds the exact configuration bytes;
// the deployment ID distinguishes two fresh deployments with otherwise
// identical paths, actors, folders, and limits.
struct SyncReplicaDeploymentIdentity final {
    std::string deployment_id;
    std::string manifest_digest;
    std::filesystem::path manifest_path;
    std::string folder_id;
    SyncReplicaActor local_actor;

    bool operator==(const SyncReplicaDeploymentIdentity&) const = default;
};

[[nodiscard]] bool sync_replica_deployment_id_is_valid(
    std::string_view value) noexcept;

[[nodiscard]] std::string generate_sync_replica_deployment_id_or_throw(
    const std::string& label);

void validate_sync_replica_deployment_identity_or_throw(
    const SyncReplicaDeploymentIdentity& identity,
    const std::string& label);

}  // namespace anonsync
