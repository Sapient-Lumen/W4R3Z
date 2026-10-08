#include "sync_replica_peer_service_singleton.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"

#include <cerrno>
#include <cstddef>
#include <cstring>
#include <stdexcept>
#include <string>
#include <string_view>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <utility>

namespace anonsync {
namespace {

constexpr std::string_view kAbstractPrefix = "anonsync.peer-service.v1.";

[[nodiscard]] std::string deployment_lock_material_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label) {
    validate_sync_replica_deployment_manifest_or_throw(
        deployment, label + " deployment");
    std::string material;
    material.reserve(128U);
    material += "anonsync-peer-service-singleton-v1\n";
    // deployment_id is the random identity durably embedded in every member
    // of this store set. Configuration, manifest pathname, manifest digest,
    // peer, listener, status path, and mutable policy are deliberately absent:
    // none may create a second process owner for the same deployment.
    material += deployment.deployment_id;
    material.push_back('\n');
    return material;
}

class DescriptorOwner final {
public:
    explicit DescriptorOwner(int descriptor = -1) noexcept
        : descriptor_(descriptor) {}
    DescriptorOwner(const DescriptorOwner&) = delete;
    DescriptorOwner& operator=(const DescriptorOwner&) = delete;
    DescriptorOwner(DescriptorOwner&& other) noexcept
        : descriptor_(std::exchange(other.descriptor_, -1)) {}
    DescriptorOwner& operator=(DescriptorOwner&& other) noexcept {
        if (this != &other) {
            reset();
            descriptor_ = std::exchange(other.descriptor_, -1);
        }
        return *this;
    }
    ~DescriptorOwner() noexcept { reset(); }

private:
    void reset() noexcept {
        if (descriptor_ >= 0) {
            const int saved_errno = errno;
            (void)::close(std::exchange(descriptor_, -1));
            errno = saved_errno;
        }
    }
    int descriptor_ = -1;
};

}  // namespace

struct SyncReplicaPeerServiceSingletonOwner::State final {
    std::string lock_id;
    DescriptorOwner socket;

    State(
        const SyncReplicaDeploymentManifest& deployment,
        std::string label)
        : lock_id(std::string(kAbstractPrefix) + sha256_hex(
              deployment_lock_material_or_throw(deployment, label))) {
        if (label.empty()) {
            throw std::invalid_argument(
                "sync replica peer service singleton label is empty");
        }
#if defined(__linux__)
        const int descriptor = ::socket(
            AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
        if (descriptor < 0) {
            throw std::runtime_error(
                label + " socket creation failed: " + std::strerror(errno));
        }
        socket = DescriptorOwner(descriptor);

        sockaddr_un address{};
        address.sun_family = AF_UNIX;
        if (lock_id.size() + 1U > sizeof(address.sun_path)) {
            throw std::runtime_error(label + " abstract lock name is too long");
        }
        address.sun_path[0] = '\0';
        std::memcpy(address.sun_path + 1U, lock_id.data(), lock_id.size());
        const socklen_t address_bytes = static_cast<socklen_t>(
            offsetof(sockaddr_un, sun_path) + 1U + lock_id.size());
        if (::bind(
                descriptor,
                reinterpret_cast<const sockaddr*>(&address),
                address_bytes) != 0) {
            const int error = errno;
            if (error == EADDRINUSE) {
                throw std::runtime_error(
                    label +
                    " deployment is already owned by another AnonSync process");
            }
            throw std::runtime_error(
                label + " acquisition failed: " + std::strerror(error));
        }
#else
        (void)deployment;
        throw std::runtime_error(
            label + " requires Linux abstract Unix sockets");
#endif
    }
};

SyncReplicaPeerServiceSingletonOwner::
SyncReplicaPeerServiceSingletonOwner(
    const SyncReplicaDeploymentManifest& deployment,
    std::string label)
    : state_(std::make_unique<State>(deployment, std::move(label))) {}

SyncReplicaPeerServiceSingletonOwner::~SyncReplicaPeerServiceSingletonOwner()
    noexcept = default;

const std::string& SyncReplicaPeerServiceSingletonOwner::lock_id() const
    noexcept {
    return state_->lock_id;
}

}  // namespace anonsync

#endif
