#pragma once

#include "sync_replica_deployment_manifest.hpp"

#include <filesystem>
#include <string>

namespace anonsync {

// Durable pre-commit intent for one exact deployment bootstrap. The record's
// bytes are the canonical final deployment manifest itself; only its pathname
// differs. Consequently the existing manifest self-digest and final-path
// binding protect the complete bootstrap configuration without introducing a
// second configuration grammar.
struct SyncReplicaBootstrapRecord final {
    std::filesystem::path record_path;
    SyncReplicaDeploymentManifest deployment;
    std::string exact_manifest_bytes;
};

// Derives one fixed-length hidden sibling from the canonical final manifest
// path. The digest avoids filename-length inheritance from an operator-selected
// manifest basename and makes inspection possible before record bytes are read.
[[nodiscard]] std::filesystem::path
sync_replica_bootstrap_record_path_or_throw(
    const std::filesystem::path& absolute_manifest_path,
    const std::string& label);

// Proves that the deterministic record name cannot alias a selected SQLite
// main/sidecar authority or fall inside either mutable content root.
void validate_sync_replica_bootstrap_record_namespace_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

// Creates and directory-syncs the immutable record with create-new semantics,
// then reads it back through the bounded exact decoder. Existing entries are
// never adopted or replaced.
[[nodiscard]] SyncReplicaBootstrapRecord
create_sync_replica_bootstrap_record_or_throw(
    const SyncReplicaDeploymentManifest& deployment,
    const std::string& label);

// Reads the deterministic record as bounded, no-symlink bytes, decodes those
// bytes against the expected final manifest path, and reconciles the exact file
// plus parent-directory durability before returning authority.
[[nodiscard]] SyncReplicaBootstrapRecord
read_sync_replica_bootstrap_record_or_throw(
    const std::filesystem::path& absolute_manifest_path,
    const std::string& label);

// Reopens the immutable record and requires byte identity with an earlier
// observation. Bootstrap calls this immediately before publishing the final
// manifest commit marker so a cooperative recovery cannot silently switch
// configuration between materialization and commit.
void attest_sync_replica_bootstrap_record_unchanged_or_throw(
    const SyncReplicaBootstrapRecord& expected,
    const std::string& label);

}  // namespace anonsync
