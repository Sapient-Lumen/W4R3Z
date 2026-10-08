#pragma once

#include "anonsync_core.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

// Private bridge for deterministic crash/recovery fixtures that must construct
// byte-exact sync-domain artifacts.  This is deliberately not installed under
// include/: runtime consumers must not depend on diagnostic fixture authority.
namespace anonsync::sync_domain_test_access {

struct DaemonOwnerLockRecord {
    std::string daemon_id;
    std::string worker_id;
    std::string owner_lock_id;
    std::uint64_t owner_lock_epoch = 0;
    std::uint64_t acquired_at_epoch = 0;
    std::uint64_t expires_at_epoch = 0;
    bool acquired = false;
    bool reclaimed_expired = false;
};

std::string remote_staging_relative_path_for_fixture(
    const NormalizedSyncPath& path,
    const std::string& digest,
    const std::string& label);

std::string resolve_normalized_relative_under_root_for_fixture(
    const std::filesystem::path& root,
    const NormalizedSyncPath& relative,
    const std::string& label);

std::string chunk_receipt_relative_path_for_fixture(
    const NormalizedSyncPath& path,
    const std::string& digest,
    const SyncChunkRange& chunk,
    const std::string& label);

std::string chunk_receipt_material_for_fixture(
    const SyncManifestEntry& remote_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncChunkRange& chunk);

std::string hash_file_and_build_chunks_for_fixture(
    const std::filesystem::path& file_path,
    std::uint64_t chunk_size,
    std::uint64_t& size_bytes,
    std::vector<SyncChunkRange>& chunks);

std::string convergence_content_digest_for_fixture(
    const SyncFolderManifest& manifest);

bool manifests_have_same_file_content_for_fixture(
    const SyncFolderManifest& left,
    const SyncFolderManifest& right);

void write_staged_chunk_bytes_for_fixture(
    const std::filesystem::path& path,
    const SyncChunkRange& chunk,
    const std::string& chunk_bytes);

void write_receipt_file_atomically_for_fixture(
    const std::filesystem::path& receipt_path,
    const std::string& receipt_text);

DaemonOwnerLockRecord acquire_resume_transfer_daemon_owner_lock_for_fixture(
    const std::string& sqlite_path,
    const std::string& session_id,
    const std::string& daemon_id,
    const std::string& worker_id,
    std::uint64_t acquired_at_epoch,
    std::uint64_t owner_lock_seconds);

std::string resume_transfer_daemon_service_instance_id_for_fixture(
    const std::string& session_id,
    const std::string& daemon_id,
    const std::string& worker_id,
    std::uint64_t restart_epoch);

}  // namespace anonsync::sync_domain_test_access
