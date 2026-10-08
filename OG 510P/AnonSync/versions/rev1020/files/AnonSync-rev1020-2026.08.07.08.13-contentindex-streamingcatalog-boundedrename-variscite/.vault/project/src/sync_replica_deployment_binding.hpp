#pragma once

#include "sync_replica_deployment_identity.hpp"
#include "sync_sqlite_handle_slot.hpp"

#include <cstdint>
#include <filesystem>
#include <string>

namespace anonsync {

class SyncSqliteTransactionAuthority;

// Role-specific file-format fence layered ahead of each exact owner schema.
// The application ID is intentionally only an early classifier; the full
// deployment identity, manifest digest, path, actor, and role are attested from
// the exact singleton table before any role owner is constructed.
enum class SyncReplicaSqliteDeploymentRole : std::uint8_t {
    Replica = 1U,
    FileEffect = 2U,
    TlsMembership = 3U,
    TlsMembershipAnchor = 4U,
    FolderCatalog = 5U,
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

// Transaction-neutral composition gates. These attest the current SQLite
// cutpoint without opening or committing a transaction. A durable owner that
// already holds its own read/write transaction must use these forms; standalone
// callers should use the transaction-owning wrappers below.
void attest_sync_replica_sqlite_deployment_binding_state_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label);
void attest_sync_replica_sqlite_deployment_binding_state_in_detached_image_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label);

// Read-only counterpart for one sealed, filename-free MEMORY-journal image.
// This gate is intentionally distinct from both the named operational gate and
// the writable bootstrap-image gate: a detached backup verifier must prove the
// durable logical binding without acquiring schema or mutation authority. The
// exact live outer transaction capability owns the nested write-denial probe,
// so raw SAVEPOINT SQL cannot escape the centralized transaction boundary.
void attest_sync_replica_sqlite_deployment_binding_state_in_read_only_detached_image_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const SyncSqliteTransactionAuthority& transaction_authority,
    const std::string& label);

// Detached-image re-attestation after a role owner has added its exact schema.
// The logical durable pathname remains binding.database_path while the live
// SQLite main database must still be a filename-free MEMORY-journal image.
// This exists so bootstrap can prove the completed image before sealing it;
// operational callers must use the named gate below.
void attest_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw(
    SyncSqliteDbHandleSlot& database,
    const SyncReplicaSqliteDeploymentBinding& binding,
    const std::string& label);

// Transaction-owning verifier for a sealed read-only detached image. It proves
// the exact logical deployment row and role application ID while retaining the
// namespace-free/read-only profile throughout the observation.
void attest_sync_replica_sqlite_deployment_binding_in_read_only_detached_image_or_throw(
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
