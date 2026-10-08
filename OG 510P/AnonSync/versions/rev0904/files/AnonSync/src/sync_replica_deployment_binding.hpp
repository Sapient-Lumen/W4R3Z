#pragma once

#include "sync_replica_deployment_identity.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <filesystem>
#include <string>

namespace anonsync {

// Role-specific file-format fence layered ahead of each exact owner schema.
// The application ID is intentionally only an early classifier; the full
// deployment identity, manifest digest, path, actor, and role are attested from
// the exact singleton table before any role owner is constructed.
enum class SyncReplicaSqliteDeploymentRole : std::uint8_t {
    Replica = 1U,
    FileEffect = 2U,
    TlsMembership = 3U,
    TlsMembershipAnchor = 4U,
};

[[nodiscard]] const char* sync_replica_sqlite_deployment_role_name(
    SyncReplicaSqliteDeploymentRole role) noexcept;

[[nodiscard]] std::uint32_t sync_replica_sqlite_application_id(
    SyncReplicaSqliteDeploymentRole role);

struct SyncReplicaSqliteDeploymentBinding final {
    SyncReplicaDeploymentIdentity deployment;
    SyncReplicaSqliteDeploymentRole role =
        SyncReplicaSqliteDeploymentRole::Replica;
    std::filesystem::path database_path;

    bool operator==(const SyncReplicaSqliteDeploymentBinding&) const = default;
};

void validate_sync_replica_sqlite_deployment_binding_or_throw(
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label);

// Named-database bootstrap-only. The exact binding namespace and application
// ID must still be absent. Product bootstrap normally constructs a detached,
// fully bound genesis image below and publishes it create-new instead.
void initialize_sync_replica_sqlite_deployment_binding_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label);

// Bootstrap-image-only initializer. The connection must be a writable,
// schema-empty, filename-free SQLite main database using MEMORY journaling,
// while the durable row is bound to binding.database_path. The stronger
// profile excludes anonymous disk-backed temporary databases, whose SQLite
// filename is also empty. This permits the complete role schema and exact
// deployment identity to be sealed before any selected filesystem pathname
// becomes visible.
void initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label);

// Named existing-database gate. Neither operational role ownership nor
// bootstrap-candidate promotion may proceed until this exact proof succeeds on
// the already-open connection.
void attest_sync_replica_sqlite_deployment_binding_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label);

}  // namespace anonsync
