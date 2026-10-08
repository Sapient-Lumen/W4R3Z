#pragma once

#if !defined(_WIN32)

#include "sync_replica_peer_service.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::string_view
    kSyncReplicaLinkedPeerServiceConfigurationSchema =
        "anonsync.linked-peer-service.v2";
inline constexpr std::string_view
    kSyncReplicaLinkedPeerServiceConfigurationLegacySchema =
        "anonsync.linked-peer-service.v1";
inline constexpr std::uint64_t
    kSyncReplicaLinkedPeerServiceConfigurationMaximumBytes = 64U * 1024U;
inline constexpr std::uint64_t
    kSyncReplicaPeerServiceTlsFileMaximumBytes = 1024U * 1024U;

struct SyncReplicaPeerServiceTlsFiles final {
    std::filesystem::path certificate;
    std::filesystem::path private_key;
    std::filesystem::path ca_file;

    bool operator==(const SyncReplicaPeerServiceTlsFiles&) const = default;
};

// Applies the same referenced-file admission used by durable configuration
// readback. In particular, the private key must be an owner-only, bounded,
// non-symlink regular file before an immutable service configuration can be
// published.
void validate_sync_replica_peer_service_tls_files_or_throw(
    const SyncReplicaPeerServiceTlsFiles& tls,
    std::string_view label = "sync replica peer service TLS files");

// One fully materialized launch description for the retained one-folder,
// one-peer service. A durable linked-peer JSON document and the legacy CLI
// both compile into this exact type, so configuration does not create a second
// scheduler or transport path.
struct SyncReplicaPeerServiceLaunchConfiguration final {
    std::string configuration_schema{
        kSyncReplicaLinkedPeerServiceConfigurationSchema};
    std::optional<std::filesystem::path> configuration_path;
    SyncReplicaDeploymentManifest deployment;
    SyncReplicaTlsPeerPolicy expected_peer;
    SyncReplicaPeerServiceTlsFiles tls;
    SyncReplicaStreamRoute route;
    SyncReplicaPeerIngress ingress{SyncReplicaDirectTcpIngress{}};
    SyncReplicaNumericStreamEndpoint listen_endpoint;
    std::optional<std::filesystem::path> status_socket_path;
    SyncReplicaPeerServiceLimits limits;
    std::optional<std::uint64_t> maximum_cycles;
    std::optional<std::uint64_t> maximum_service_runtime_seconds;
};

void validate_sync_replica_peer_service_launch_configuration_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& configuration,
    bool require_durable_configuration_and_status_socket,
    std::string_view label =
        "sync replica peer service launch configuration");

// Reads one owner-only (0600), single-link, non-symlink JSON document. The
// current v2 schema binds outbound dialing and inbound publication separately;
// legacy v1 documents remain readable and compile to explicit direct ingress.
// Unknown keys are rejected. Every referenced path is absolute and normalized, route
// choices are fail-closed, and the deployment manifest is loaded before folder
// limits are materialized. The returned object is immediately usable by the
// existing retained service owner.
[[nodiscard]] SyncReplicaPeerServiceLaunchConfiguration
read_sync_replica_linked_peer_service_configuration_or_throw(
    const std::filesystem::path& absolute_configuration_path,
    std::string_view label =
        "sync replica linked-peer service configuration");

}  // namespace anonsync

#endif
