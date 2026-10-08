#pragma once

#if !defined(_WIN32)

#include "sync_replica_peer_service_configuration.hpp"

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

// The in-memory route/ingress owners retain exact I2P destination bytes, while
// the durable configuration intentionally stores only protected source paths.
// These two optional paths preserve that distinction for one configuration
// publication without teaching the runtime transport owner about provisioning.
struct SyncReplicaPeerServiceProvisioningSourceFiles final {
    std::optional<std::filesystem::path>
        outbound_i2p_private_destination_file;
    std::optional<std::filesystem::path>
        inbound_i2p_private_destination_file;

    bool operator==(
        const SyncReplicaPeerServiceProvisioningSourceFiles&) const = default;
};

enum class SyncReplicaPeerServiceConfigurationDisposition : std::uint8_t {
    Created = 1U,
    ResumedExact = 2U,
};

enum class SyncReplicaPeerServiceConfigurationInspection : std::uint8_t {
    Absent = 1U,
    ExistingExact = 2U,
};

[[nodiscard]] const char*
sync_replica_peer_service_configuration_disposition_name(
    SyncReplicaPeerServiceConfigurationDisposition disposition) noexcept;

struct SyncReplicaPeerServiceProvisioningResult final {
    SyncReplicaPeerServiceLaunchConfiguration launch;
    std::string exact_configuration_bytes;
    SyncReplicaPeerServiceConfigurationDisposition disposition =
        SyncReplicaPeerServiceConfigurationDisposition::Created;
};

// Encodes one complete v2 linked-peer document. All limits are explicit, so a
// later default change cannot silently alter an installed service. The result
// is checked by the same strict decoder used by `run --config` before it is
// returned.
[[nodiscard]] std::string
encode_sync_replica_linked_peer_service_configuration_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& configuration,
    const SyncReplicaPeerServiceProvisioningSourceFiles& source_files,
    std::string_view label =
        "sync replica linked-peer service configuration encoding");

// Atomically creates one owner-only immutable configuration, then reopens it
// through the shipping reader and proves the decoded launch is exactly the one
// requested. Existing entries are preserved and rejected; this command is not
// an in-place editor or a credential rotation mechanism.
// Observes one requested immutable configuration without creating or
// replacing it. ExistingExact requires exact canonical bytes, protected
// identity/mode checks, directory synchronization, strict decode, and exact
// launch equality. A conflicting or malformed existing entry throws.
[[nodiscard]] SyncReplicaPeerServiceConfigurationInspection
inspect_sync_replica_linked_peer_service_configuration_or_throw(
    const SyncReplicaPeerServiceLaunchConfiguration& configuration,
    const SyncReplicaPeerServiceProvisioningSourceFiles& source_files,
    std::string_view label =
        "sync replica linked-peer service configuration inspection");

[[nodiscard]] SyncReplicaPeerServiceProvisioningResult
provision_sync_replica_linked_peer_service_configuration_or_throw(
    SyncReplicaPeerServiceLaunchConfiguration configuration,
    SyncReplicaPeerServiceProvisioningSourceFiles source_files,
    std::string_view label =
        "sync replica linked-peer service configuration provisioning");

// Setup-only restart owner. An absent configuration is published through the
// same create-new path above. An existing entry is accepted only when the exact
// canonical bytes, owner-only file identity, referenced deployment, route,
// ingress, credentials, peer, and limits all revalidate. Conflicts are never
// replaced. This closes the crash window where publication succeeded but the
// calling CLI lost its terminal output before the operator could record it.
[[nodiscard]] SyncReplicaPeerServiceProvisioningResult
provision_or_resume_sync_replica_linked_peer_service_configuration_or_throw(
    SyncReplicaPeerServiceLaunchConfiguration configuration,
    SyncReplicaPeerServiceProvisioningSourceFiles source_files,
    std::string_view label =
        "sync replica linked-peer service configuration create or resume");

}  // namespace anonsync

#endif
