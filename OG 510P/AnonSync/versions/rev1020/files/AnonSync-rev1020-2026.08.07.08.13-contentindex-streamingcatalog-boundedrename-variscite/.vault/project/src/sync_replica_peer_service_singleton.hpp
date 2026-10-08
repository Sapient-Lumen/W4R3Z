#pragma once

#if !defined(_WIN32)

#include "sync_replica_deployment_manifest.hpp"

#include <memory>
#include <string>

namespace anonsync {

// Process-lifetime ownership for one local deployment. The Linux abstract
// Unix-socket name is derived only from deployment_id: the random identity
// durably embedded in every member of the store set. A retained service,
// one-shot sync, or offline database-maintenance process cannot evade the
// singleton by choosing another TCP port, status socket, configuration file,
// manifest pathname/digest, peer, command, or mutable policy.
class SyncReplicaPeerServiceSingletonOwner final {
public:
    explicit SyncReplicaPeerServiceSingletonOwner(
        const SyncReplicaDeploymentManifest& deployment,
        std::string label = "sync replica peer service singleton");
    ~SyncReplicaPeerServiceSingletonOwner() noexcept;

    SyncReplicaPeerServiceSingletonOwner(
        const SyncReplicaPeerServiceSingletonOwner&) = delete;
    SyncReplicaPeerServiceSingletonOwner& operator=(
        const SyncReplicaPeerServiceSingletonOwner&) = delete;
    SyncReplicaPeerServiceSingletonOwner(
        SyncReplicaPeerServiceSingletonOwner&&) = delete;
    SyncReplicaPeerServiceSingletonOwner& operator=(
        SyncReplicaPeerServiceSingletonOwner&&) = delete;

    [[nodiscard]] const std::string& lock_id() const noexcept;

private:
    struct State;
    std::unique_ptr<State> state_;
};

}  // namespace anonsync

#endif
