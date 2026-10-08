#pragma once

#include <cstdint>
#include <string>
#include <vector>


namespace anonsync {


struct SyncValidationResult {
    bool ok = false;
    std::string reason;
};

struct NormalizedSyncPath {
    std::string value;
};

enum class SyncManifestEntryKind {
    File,
    Tombstone
};

struct SyncChunkRange {
    std::uint64_t offset = 0;
    std::uint64_t length = 0;
    std::string sha256;
};

struct SyncVersionLineageEntry {
    std::string device_id;
    std::uint64_t counter = 0;
};

struct SyncManifestEntry {
    std::string folder_id;
    std::string device_id;
    NormalizedSyncPath path;
    SyncManifestEntryKind kind = SyncManifestEntryKind::File;
    std::uint64_t size_bytes = 0;
    std::string content_sha256;
    std::vector<SyncChunkRange> chunks;
    std::vector<SyncVersionLineageEntry> lineage;
    std::string conflict_set_id;
};

struct SyncFolderManifest {
    std::string folder_id;
    std::string device_id;
    std::uint64_t manifest_counter = 0;
    std::vector<SyncManifestEntry> entries;
};

struct SyncFolderScanOptions {
    std::string root_path;
    std::string folder_id;
    std::string device_id;
    std::uint64_t manifest_counter = 0;
    std::uint64_t lineage_counter = 0;
    std::uint64_t chunk_size_bytes = 256 * 1024;
};


enum class SyncPlanAction {
    Noop,
    FetchRemoteFile,
    PublishLocalFile,
    ApplyRemoteTombstone,
    PublishLocalTombstone,
    RecordConflict
};

enum class SyncLineageRelation {
    Equal,
    LocalNewer,
    RemoteNewer,
    Concurrent
};

struct SyncManifestPlanEntry {
    NormalizedSyncPath path;
    SyncPlanAction action = SyncPlanAction::Noop;
    SyncLineageRelation lineage_relation = SyncLineageRelation::Equal;
    bool local_entry_present = false;
    bool remote_entry_present = false;
    SyncManifestEntryKind local_entry_kind = SyncManifestEntryKind::File;
    SyncManifestEntryKind remote_entry_kind = SyncManifestEntryKind::File;
    std::uint64_t local_size_bytes = 0;
    std::uint64_t remote_size_bytes = 0;
    std::string local_content_sha256;
    std::string remote_content_sha256;
    std::string local_entry_digest;
    std::string remote_entry_digest;
    std::string local_version_digest;
    std::string remote_version_digest;
    std::string conflict_set_id;
    std::string reason;
    std::vector<SyncChunkRange> needed_chunks;
};

struct SyncManifestDiffPlan {
    std::string folder_id;
    std::string local_device_id;
    std::string remote_device_id;
    std::string local_manifest_digest;
    std::string remote_manifest_digest;
    std::vector<SyncManifestPlanEntry> entries;
};

enum class SyncLocalApplyAction {
    Noop,
    StageRemoteFile,
    DeleteLocalPath,
    PreserveConflictCopy,
    AdvertiseLocalFile,
    AdvertiseLocalTombstone
};

struct SyncLocalApplyOptions {
    std::string local_root_path;
    std::string staging_root_path;
};

struct SyncLocalApplyPlanEntry {
    NormalizedSyncPath path;
    SyncPlanAction source_action = SyncPlanAction::Noop;
    SyncLocalApplyAction local_action = SyncLocalApplyAction::Noop;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::string absolute_conflict_copy_path;
    bool local_entry_present = false;
    bool remote_entry_present = false;
    SyncManifestEntryKind local_entry_kind = SyncManifestEntryKind::File;
    SyncManifestEntryKind remote_entry_kind = SyncManifestEntryKind::File;
    std::uint64_t local_size_bytes = 0;
    std::uint64_t remote_size_bytes = 0;
    std::string local_content_sha256;
    std::string remote_content_sha256;
    std::string local_entry_digest;
    std::string remote_entry_digest;
    std::string local_version_digest;
    std::string remote_version_digest;
    std::string conflict_set_id;
    std::string idempotency_key;
    std::string reason;
    std::vector<SyncChunkRange> needed_chunks;
};

struct SyncLocalApplyPlan {
    std::string folder_id;
    std::string local_device_id;
    std::string remote_device_id;
    std::string local_root_path;
    std::string staging_root_path;
    std::vector<SyncLocalApplyPlanEntry> entries;
};

struct SyncStagedFileMaterializationOptions {
    std::string local_root_path;
    std::string staging_root_path;
    bool allow_overwrite = true;
    bool require_chunk_receipts = false;
};

struct SyncStagedFileMaterializationResult {
    NormalizedSyncPath path;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::uint64_t size_bytes = 0;
    std::uint64_t chunks_verified = 0;
    std::string content_sha256;
    std::string idempotency_key;
    bool preflight_checked_target = false;
    bool replaced_existing_target = false;
    bool chunk_receipts_checked = false;
    bool materialized = false;
};

struct SyncTombstoneApplicationOptions {
    std::string local_root_path;
};

struct SyncTombstoneApplicationResult {
    NormalizedSyncPath path;
    std::string absolute_target_path;
    std::string idempotency_key;
    bool preflight_checked_target = false;
    bool target_existed = false;
    bool removed = false;
};

struct SyncConflictPreservationOptions {
    std::string local_root_path;
    std::string staging_root_path;
    bool require_chunk_receipts = false;
};

struct SyncConflictPreservationResult {
    NormalizedSyncPath path;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::string absolute_conflict_copy_path;
    std::string idempotency_key;
    bool preflight_checked_target = false;
    bool conflict_copy_preserved = false;
    bool reused_existing_conflict_copy = false;
    bool remote_file_materialized = false;
    bool remote_tombstone_applied = false;
    bool chunk_receipts_checked = false;
    std::uint64_t remote_size_bytes = 0;
    std::uint64_t remote_chunks_verified = 0;
    std::string remote_content_sha256;
};

struct SyncChunkReceiptWriteOptions {
    std::string local_root_path;
    std::string staging_root_path;
};

struct SyncChunkReceiptWriteResult {
    NormalizedSyncPath path;
    std::string absolute_staging_path;
    std::string absolute_receipt_path;
    std::uint64_t offset = 0;
    std::uint64_t length = 0;
    std::string chunk_sha256;
    std::string idempotency_key;
    bool chunk_written = false;
    bool reused_existing_receipt = false;
    bool staged_file_complete = false;
    std::uint64_t chunks_verified = 0;
    std::string content_sha256;
};

struct SyncStagedTransferInspectionOptions {
    std::string local_root_path;
    std::string staging_root_path;
};

struct SyncStagedTransferInspectionResult {
    NormalizedSyncPath path;
    std::string absolute_staging_path;
    std::string idempotency_key;
    bool staged_file_exists = false;
    bool staged_file_complete = false;
    bool chunk_receipts_checked = false;
    std::uint64_t total_chunks = 0;
    std::uint64_t receipts_verified = 0;
    std::uint64_t chunks_verified = 0;
    std::uint64_t staged_size_bytes = 0;
    std::string content_sha256;
    std::vector<SyncChunkRange> missing_chunks;
};

struct SyncStagedTransferCleanupOptions {
    std::string local_root_path;
    std::string staging_root_path;
    bool remove_receipts = true;
    bool prune_empty_parent_directories = true;
};

struct SyncStagedTransferCleanupResult {
    NormalizedSyncPath path;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::string absolute_receipt_directory_path;
    std::string idempotency_key;
    bool terminal_target_verified = false;
    bool staged_file_absent = false;
    bool receipt_directory_removed = false;
    bool parent_directories_pruned = false;
    bool cleanup_performed = false;
    std::uint64_t receipts_removed = 0;
    std::uint64_t directories_removed = 0;
};

struct SyncChunkRequestPlanOptions {
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
};

struct SyncChunkRequestPlanResult {
    NormalizedSyncPath path;
    std::string idempotency_key;
    bool staged_file_complete = false;
    bool more_chunks_available = false;
    std::uint64_t total_missing_chunks = 0;
    std::uint64_t selected_chunks = 0;
    std::uint64_t selected_bytes = 0;
    std::vector<SyncChunkRange> chunks_to_request;
};

struct SyncChunkResponseEnvelope {
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string response_idempotency_key;
    std::string remote_entry_digest;
    std::string remote_version_digest;
    std::string apply_entry_idempotency_key;
    std::uint64_t offset = 0;
    std::uint64_t length = 0;
    std::string chunk_sha256;
};

struct SyncChunkResponseBatchEnvelope {
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string batch_idempotency_key;
    std::string remote_entry_digest;
    std::string remote_version_digest;
    std::string apply_entry_idempotency_key;
    std::uint64_t response_count = 0;
    std::uint64_t total_bytes = 0;
    std::vector<SyncChunkResponseEnvelope> responses;
};

struct SyncRequestedChunkAcceptanceResult {
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string response_idempotency_key;
    std::string receipt_idempotency_key;
    std::string absolute_staging_path;
    std::string absolute_receipt_path;
    std::uint64_t offset = 0;
    std::uint64_t length = 0;
    std::string chunk_sha256;
    bool request_evidence_checked = false;
    bool response_envelope_checked = false;
    bool chunk_written = false;
    bool reused_existing_receipt = false;
    bool staged_file_complete = false;
    std::uint64_t chunks_verified = 0;
    std::string content_sha256;
};

struct SyncChunkResponseBatchAcceptanceResult {
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string batch_idempotency_key;
    bool request_evidence_checked = false;
    bool batch_envelope_checked = false;
    std::uint64_t response_count = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    bool staged_file_complete = false;
    std::uint64_t chunks_verified = 0;
    std::string content_sha256;
    std::vector<SyncRequestedChunkAcceptanceResult> accepted_chunks;
};

struct SyncChunkTransferRoundResult {
    SyncChunkResponseBatchAcceptanceResult batch_acceptance;
    SyncStagedTransferInspectionResult post_batch_inspection;
    SyncChunkRequestPlanResult next_request_plan;
    bool post_batch_inspection_checked = false;
    bool next_request_plan_built = false;
    bool ready_to_materialize = false;
    bool more_chunks_needed = false;
};

struct SyncPeerChunkAvailability {
    std::string peer_id;
    std::string peer_session_id;
    std::uint64_t max_chunks = 0;
    std::uint64_t max_bytes = 0;
    std::vector<SyncChunkRange> available_chunks;
};

struct SyncPeerChunkAssignment {
    std::string peer_id;
    std::string peer_session_id;
    std::string peer_request_idempotency_key;
    std::uint64_t assigned_chunks = 0;
    std::uint64_t assigned_bytes = 0;
    std::vector<SyncChunkRange> chunks;
};

struct SyncPeerChunkScheduleResult {
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::uint64_t peer_count = 0;
    std::uint64_t total_request_chunks = 0;
    std::uint64_t total_request_bytes = 0;
    std::uint64_t assigned_chunks = 0;
    std::uint64_t assigned_bytes = 0;
    bool request_fully_covered = false;
    std::vector<SyncPeerChunkAssignment> assignments;
    std::vector<SyncChunkRange> unassigned_chunks;
};

struct SyncPeerChunkResponseBatchEnvelope {
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string peer_request_idempotency_key;
    std::string peer_response_batch_idempotency_key;
    std::string batch_idempotency_key;
    std::string remote_entry_digest;
    std::string remote_version_digest;
    std::string apply_entry_idempotency_key;
    std::uint64_t response_count = 0;
    std::uint64_t total_bytes = 0;
    std::vector<SyncChunkResponseEnvelope> responses;
};

struct SyncPeerChunkResponseBatchAcceptanceResult {
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string peer_request_idempotency_key;
    std::string peer_response_batch_idempotency_key;
    std::string batch_idempotency_key;
    bool request_evidence_checked = false;
    bool peer_schedule_checked = false;
    bool peer_assignment_checked = false;
    bool peer_response_envelope_checked = false;
    std::uint64_t response_count = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    bool staged_file_complete = false;
    std::uint64_t chunks_verified = 0;
    std::string content_sha256;
    std::vector<SyncRequestedChunkAcceptanceResult> accepted_chunks;
};

struct SyncPeerChunkTransferRoundResult {
    SyncPeerChunkResponseBatchAcceptanceResult peer_batch_acceptance;
    SyncStagedTransferInspectionResult post_batch_inspection;
    SyncChunkRequestPlanResult next_request_plan;
    SyncPeerChunkScheduleResult next_peer_schedule;
    bool post_batch_inspection_checked = false;
    bool next_request_plan_built = false;
    bool next_peer_schedule_built = false;
    bool ready_to_materialize = false;
    bool more_chunks_needed = false;
    bool peer_work_scheduled = false;
};

struct SyncFakePeerFileFetchSessionOptions {
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string folder_id = "folder-alpha";
    std::string source_device_id = "device-bravo";
    std::string destination_device_id = "device-alpha";
    std::string peer_id = "peer-bravo";
    std::string peer_session_id = "session-alpha";
    std::uint64_t source_manifest_counter = 1;
    std::uint64_t destination_manifest_counter = 1;
    std::uint64_t source_lineage_counter = 1;
    std::uint64_t destination_lineage_counter = 1;
    std::uint64_t chunk_size_bytes = 256 * 1024;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
    std::uint64_t max_transfer_rounds = 1024;
    bool require_chunk_receipts_for_materialization = true;
    bool cleanup_staged_transfer_artifacts_after_materialization = true;
};

struct SyncFakePeerFileFetchSessionFileResult {
    NormalizedSyncPath path;
    std::uint64_t transfer_rounds = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    std::uint64_t bytes_materialized = 0;
    std::uint64_t cleanup_receipts_removed = 0;
    std::uint64_t cleanup_directories_removed = 0;
    std::string source_content_sha256;
    std::string destination_content_sha256;
    bool receipt_gated_materialization = false;
    bool staging_artifacts_cleaned = false;
    bool materialized = false;
};

struct SyncFakePeerFileFetchSessionResult {
    SyncFolderManifest source_manifest;
    SyncFolderManifest destination_manifest_before;
    SyncManifestDiffPlan diff_plan;
    SyncLocalApplyPlan apply_plan;
    SyncFolderManifest destination_manifest_after;
    std::uint64_t apply_entries_considered = 0;
    std::uint64_t files_materialized = 0;
    std::uint64_t transfer_rounds = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    std::uint64_t bytes_materialized = 0;
    std::uint64_t cleanup_receipts_removed = 0;
    std::uint64_t cleanup_directories_removed = 0;
    std::string source_content_digest;
    std::string destination_content_digest;
    bool content_converged = false;
    std::vector<SyncFakePeerFileFetchSessionFileResult> files;
};

struct SyncSessionCheckpointOptions {
    std::string sqlite_path;
    std::string session_id;
    bool reset_existing_session_rows = true;
    bool require_converged_session = true;
    bool require_committed_cleanup = true;
};

struct SyncSessionCheckpointResult {
    std::string sqlite_path;
    std::string session_id;
    std::string checkpoint_idempotency_key;
    std::string source_manifest_digest;
    std::string destination_manifest_before_digest;
    std::string destination_manifest_after_digest;
    bool transaction_committed = false;
    bool checkpoint_reloaded = false;
    bool content_converged = false;
    std::uint64_t source_manifest_entries_written = 0;
    std::uint64_t destination_before_manifest_entries_written = 0;
    std::uint64_t destination_after_manifest_entries_written = 0;
    std::uint64_t source_manifest_chunks_written = 0;
    std::uint64_t destination_before_manifest_chunks_written = 0;
    std::uint64_t destination_after_manifest_chunks_written = 0;
    std::uint64_t apply_intents_written = 0;
    std::uint64_t file_results_written = 0;
    std::uint64_t materialization_checkpoints_written = 0;
    std::uint64_t cleanup_checkpoints_written = 0;
    std::uint64_t chunk_receipts_recorded = 0;
};

struct SyncSessionCheckpointResumeViewOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    bool require_content_converged = true;
    bool require_committed_cleanup = true;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool require_destination_filesystem_match = true;
    bool require_staging_artifacts_cleaned = true;
};

struct SyncSessionCheckpointResumeViewResult {
    std::string sqlite_path;
    std::string session_id;
    std::string checkpoint_idempotency_key;
    std::string schema_version;
    std::string folder_id;
    std::string source_device_id;
    std::string destination_device_id;
    std::string peer_id;
    std::string peer_session_id;
    std::string source_manifest_digest;
    std::string destination_manifest_before_digest;
    std::string destination_manifest_after_digest;
    std::string source_content_digest;
    std::string destination_content_digest;
    bool content_converged = false;
    bool materialization_terminal_complete = false;
    bool cleanup_terminal_complete = false;
    bool all_chunk_receipts_committed_cleaned = false;
    bool schema_version_supported = false;
    bool manifest_digest_rows_verified = false;
    bool manifest_entry_rows_verified = false;
    bool manifest_chunk_rows_verified = false;
    bool file_result_aggregates_verified = false;
    bool chunk_receipt_totals_verified = false;
    bool chunk_receipt_coverage_verified = false;
    bool source_filesystem_verified = false;
    bool destination_filesystem_verified = false;
    bool staging_artifacts_verified = false;
    bool durable_integrity_verified = false;
    bool terminal_session_complete = false;
    std::uint64_t apply_entries_considered = 0;
    std::uint64_t files_materialized = 0;
    std::uint64_t transfer_rounds = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    std::uint64_t bytes_materialized = 0;
    std::uint64_t cleanup_receipts_removed = 0;
    std::uint64_t cleanup_directories_removed = 0;
    std::uint64_t source_manifest_entries_recorded = 0;
    std::uint64_t destination_before_manifest_entries_recorded = 0;
    std::uint64_t destination_after_manifest_entries_recorded = 0;
    std::uint64_t source_manifest_entry_rows_recorded = 0;
    std::uint64_t destination_before_manifest_entry_rows_recorded = 0;
    std::uint64_t destination_after_manifest_entry_rows_recorded = 0;
    std::uint64_t source_manifest_chunks_recorded = 0;
    std::uint64_t destination_before_manifest_chunks_recorded = 0;
    std::uint64_t destination_after_manifest_chunks_recorded = 0;
    std::uint64_t source_manifest_chunk_rows_recorded = 0;
    std::uint64_t destination_before_manifest_chunk_rows_recorded = 0;
    std::uint64_t destination_after_manifest_chunk_rows_recorded = 0;
    std::uint64_t source_manifest_chunks_without_receipts = 0;
    std::uint64_t chunk_receipts_without_source_manifest_chunks = 0;
    std::uint64_t source_filesystem_entries_checked = 0;
    std::uint64_t source_filesystem_file_entries_checked = 0;
    std::uint64_t source_filesystem_tombstone_entries_checked = 0;
    std::uint64_t source_filesystem_missing_paths = 0;
    std::uint64_t source_filesystem_kind_mismatches = 0;
    std::uint64_t source_filesystem_content_mismatches = 0;
    std::uint64_t destination_filesystem_entries_checked = 0;
    std::uint64_t destination_filesystem_file_entries_checked = 0;
    std::uint64_t destination_filesystem_tombstone_entries_checked = 0;
    std::uint64_t destination_filesystem_missing_paths = 0;
    std::uint64_t destination_filesystem_kind_mismatches = 0;
    std::uint64_t destination_filesystem_content_mismatches = 0;
    std::uint64_t staging_artifact_paths_checked = 0;
    std::uint64_t staging_files_present = 0;
    std::uint64_t staging_receipt_directories_present = 0;
    std::uint64_t staging_artifact_kind_mismatches = 0;
    std::uint64_t apply_intents_recorded = 0;
    std::uint64_t file_results_recorded = 0;
    std::uint64_t materialization_checkpoints_recorded = 0;
    std::uint64_t cleanup_checkpoints_recorded = 0;
    std::uint64_t chunk_receipts_recorded = 0;
    std::uint64_t files_pending_materialization = 0;
    std::uint64_t files_pending_cleanup = 0;
    std::uint64_t chunk_receipts_pending_cleanup = 0;
    std::vector<NormalizedSyncPath> pending_materialization_paths;
    std::vector<NormalizedSyncPath> pending_cleanup_paths;
    std::vector<NormalizedSyncPath> source_filesystem_drift_paths;
    std::vector<NormalizedSyncPath> destination_filesystem_drift_paths;
    std::vector<NormalizedSyncPath> staging_artifact_paths;
};

struct SyncSessionCheckpointStagingRepairOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    bool require_terminal_checkpoint = true;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool require_destination_filesystem_match = true;
    bool remove_staged_files = true;
    bool remove_receipts = true;
    bool prune_empty_parent_directories = true;
};

struct SyncSessionCheckpointStagingRepairFileResult {
    NormalizedSyncPath path;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::string absolute_receipt_directory_path;
    bool terminal_destination_verified = false;
    bool staged_file_removed = false;
    bool receipt_directory_removed = false;
    bool parent_directories_pruned = false;
    bool cleanup_performed = false;
    std::uint64_t receipts_removed = 0;
    std::uint64_t directories_removed = 0;
};

struct SyncSessionCheckpointStagingRepairResult {
    std::string sqlite_path;
    std::string session_id;
    bool resume_view_loaded = false;
    bool terminal_session_complete = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool destination_filesystem_verified = false;
    bool pre_repair_staging_artifacts_clean = false;
    bool post_repair_staging_artifacts_clean = false;
    bool repair_performed = false;
    std::uint64_t files_considered = 0;
    std::uint64_t files_repaired = 0;
    std::uint64_t staged_files_removed = 0;
    std::uint64_t receipt_files_removed = 0;
    std::uint64_t receipt_directories_removed = 0;
    std::uint64_t parent_directories_pruned = 0;
    std::uint64_t directories_removed = 0;
    std::uint64_t unsafe_artifacts_detected = 0;
    std::uint64_t staging_file_content_mismatches = 0;
    std::uint64_t receipt_content_mismatches = 0;
    std::uint64_t unexpected_receipt_artifacts = 0;
    std::vector<NormalizedSyncPath> pre_repair_artifact_paths;
    std::vector<NormalizedSyncPath> post_repair_artifact_paths;
    std::vector<SyncSessionCheckpointStagingRepairFileResult> files;
};


enum class SyncSessionCheckpointResumeActionKind {
    AlreadyConverged,
    RepairCommittedStaging,
    CleanupCommittedStaging,
    MaterializeStagedFile,
    ResumeTransfer,
    RetryTransfer,
    QuarantineStaging,
    RejectDrift
};

struct SyncSessionCheckpointResumeActionPlanOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool require_destination_filesystem_match = false;
    bool require_staging_artifacts_cleaned = false;
};

struct SyncSessionCheckpointResumeActionFilePlan {
    NormalizedSyncPath path;
    SyncSessionCheckpointResumeActionKind action = SyncSessionCheckpointResumeActionKind::RejectDrift;
    std::string action_reason;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::string absolute_receipt_directory_path;
    bool materialized_row_present = false;
    bool cleanup_row_present = false;
    bool receipt_rows_match_manifest = false;
    bool root_paths_match_checkpoint = false;
    bool destination_target_present = false;
    bool destination_target_matches = false;
    bool staged_file_present = false;
    bool staged_file_complete = false;
    bool staged_file_content_matches = false;
    bool receipt_directory_present = false;
    bool all_receipts_verified = false;
    std::uint64_t chunks_total = 0;
    std::uint64_t receipt_rows_recorded = 0;
    std::uint64_t accepted_receipt_rows = 0;
    std::uint64_t committed_cleaned_receipt_rows = 0;
    std::uint64_t receipt_files_present = 0;
    std::uint64_t receipt_files_verified = 0;
    std::uint64_t missing_receipts = 0;
    std::uint64_t receipt_content_mismatches = 0;
    std::uint64_t receipt_kind_mismatches = 0;
    std::uint64_t staged_file_kind_mismatches = 0;
    std::uint64_t staged_file_content_mismatches = 0;
    std::uint64_t unexpected_receipt_artifacts = 0;
    std::vector<SyncChunkRange> chunks_to_request;
};

struct SyncSessionCheckpointResumeActionPlanResult {
    std::string sqlite_path;
    std::string session_id;
    bool resume_view_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool destination_filesystem_verified = false;
    bool staging_artifacts_verified = false;
    bool terminal_session_complete = false;
    std::uint64_t files_considered = 0;
    std::uint64_t already_converged_files = 0;
    std::uint64_t repair_committed_staging_files = 0;
    std::uint64_t cleanup_committed_staging_files = 0;
    std::uint64_t materialize_staged_files = 0;
    std::uint64_t resume_transfer_files = 0;
    std::uint64_t retry_transfer_files = 0;
    std::uint64_t quarantine_staging_files = 0;
    std::uint64_t reject_drift_files = 0;
    std::uint64_t receipt_content_mismatches = 0;
    std::uint64_t receipt_kind_mismatches = 0;
    std::uint64_t staged_file_kind_mismatches = 0;
    std::uint64_t staged_file_content_mismatches = 0;
    std::uint64_t unexpected_receipt_artifacts = 0;
    std::vector<SyncSessionCheckpointResumeActionFilePlan> files;
};

struct SyncSessionCheckpointMaterializeResumeOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
};

struct SyncSessionCheckpointMaterializeResumeFileResult {
    NormalizedSyncPath path;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::string absolute_receipt_directory_path;
    std::string materialization_idempotency_key;
    bool action_plan_matched = false;
    bool destination_target_absent_preflight = false;
    bool destination_target_already_matching = false;
    bool staged_file_verified = false;
    bool receipt_sidecars_verified = false;
    bool atomic_rename_performed = false;
    bool database_rows_updated = false;
    std::uint64_t size_bytes = 0;
    std::uint64_t chunks_verified = 0;
    std::string content_sha256;
};

struct SyncSessionCheckpointMaterializeResumeResult {
    std::string sqlite_path;
    std::string session_id;
    bool action_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool transaction_committed = false;
    std::uint64_t files_considered = 0;
    std::uint64_t files_materialized = 0;
    std::uint64_t files_skipped = 0;
    std::uint64_t bytes_materialized = 0;
    std::uint64_t materialization_checkpoints_written = 0;
    std::uint64_t file_result_rows_updated = 0;
    std::uint64_t post_cleanup_committed_staging_files = 0;
    std::uint64_t post_already_converged_files = 0;
    std::vector<SyncSessionCheckpointMaterializeResumeFileResult> files;
};

struct SyncSessionCheckpointCleanupResumeOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
    bool remove_receipts = true;
    bool remove_matching_staged_file = true;
    bool prune_empty_parent_directories = true;
};

struct SyncSessionCheckpointCleanupResumeFileResult {
    NormalizedSyncPath path;
    std::string absolute_target_path;
    std::string absolute_staging_path;
    std::string absolute_receipt_directory_path;
    std::string cleanup_idempotency_key;
    bool action_plan_matched = false;
    bool terminal_target_verified = false;
    bool staged_file_absent_preflight = false;
    bool staged_file_verified = false;
    bool staged_file_removed = false;
    bool receipt_sidecars_verified = false;
    bool receipt_directory_removed = false;
    bool parent_directories_pruned = false;
    bool database_rows_updated = false;
    std::uint64_t receipts_removed = 0;
    std::uint64_t directories_removed = 0;
    std::uint64_t receipt_rows_updated = 0;
};

struct SyncSessionCheckpointCleanupResumeResult {
    std::string sqlite_path;
    std::string session_id;
    bool action_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool transaction_committed = false;
    std::uint64_t files_considered = 0;
    std::uint64_t files_cleaned = 0;
    std::uint64_t files_skipped = 0;
    std::uint64_t staged_files_removed = 0;
    std::uint64_t receipt_files_removed = 0;
    std::uint64_t directories_removed = 0;
    std::uint64_t cleanup_checkpoints_written = 0;
    std::uint64_t file_result_rows_updated = 0;
    std::uint64_t receipt_rows_updated = 0;
    std::uint64_t post_already_converged_files = 0;
    std::uint64_t post_repair_committed_staging_files = 0;
    std::vector<SyncSessionCheckpointCleanupResumeFileResult> files;
};



struct SyncSessionCheckpointResumeTransferPlanOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    std::string peer_id;
    std::string peer_session_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
    bool include_retry_transfer = true;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
};

struct SyncSessionCheckpointResumeTransferFilePlan {
    NormalizedSyncPath path;
    SyncSessionCheckpointResumeActionKind source_action = SyncSessionCheckpointResumeActionKind::RejectDrift;
    std::string action_reason;
    std::string absolute_staging_path;
    std::string absolute_receipt_directory_path;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    bool action_plan_matched = false;
    bool request_built = false;
    bool peer_work_scheduled = false;
    bool more_chunks_available = false;
    std::uint64_t total_missing_chunks = 0;
    std::uint64_t selected_chunks = 0;
    std::uint64_t selected_bytes = 0;
    std::uint64_t peer_assigned_chunks = 0;
    std::uint64_t peer_assigned_bytes = 0;
    std::uint64_t unassigned_chunks = 0;
    std::vector<SyncChunkRange> chunks_to_request;
    std::vector<SyncChunkRange> peer_assigned_chunk_ranges;
    std::vector<SyncChunkRange> deferred_chunks;
};

struct SyncSessionCheckpointResumeTransferPlanResult {
    std::string sqlite_path;
    std::string session_id;
    bool action_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    std::uint64_t files_considered = 0;
    std::uint64_t files_planned = 0;
    std::uint64_t files_skipped = 0;
    std::uint64_t resume_transfer_files_planned = 0;
    std::uint64_t retry_transfer_files_planned = 0;
    std::uint64_t total_missing_chunks = 0;
    std::uint64_t selected_chunks = 0;
    std::uint64_t selected_bytes = 0;
    std::uint64_t peer_assigned_chunks = 0;
    std::uint64_t peer_assigned_bytes = 0;
    std::uint64_t deferred_chunks = 0;
    std::vector<SyncSessionCheckpointResumeTransferFilePlan> files;
};

struct SyncSessionCheckpointResumeTransferClaimOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    std::string peer_id;
    std::string peer_session_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
    bool include_retry_transfer = true;
    std::string worker_id;
    std::uint64_t worker_lease_epoch = 1;
    std::uint64_t workorder_claim_now_epoch = 1;
    std::uint64_t worker_lease_seconds = 60;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    bool allow_expired_workorder_reclaim = true;
    std::uint64_t max_workorder_claim_attempts = 0;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
    std::vector<std::string> allowed_execution_idempotency_keys;
};

struct SyncSessionCheckpointResumeTransferFileClaimResult {
    NormalizedSyncPath path;
    SyncSessionCheckpointResumeActionKind source_action = SyncSessionCheckpointResumeActionKind::RejectDrift;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string absolute_staging_path;
    bool transfer_plan_matched = false;
    bool workorder_claimed = false;
    std::uint64_t claimed_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t chunks_assigned = 0;
    std::uint64_t workorder_rows_claimed = 0;
    std::uint64_t workorder_rows_already_owned = 0;
    std::uint64_t workorder_rows_reclaimed = 0;
    std::uint64_t workorder_reclaim_events_written = 0;
    std::uint64_t workorder_rows_abandoned = 0;
    std::uint64_t workorder_abandon_events_written = 0;
    std::uint64_t workorder_rows_quarantined = 0;
    std::uint64_t workorder_quarantine_events_written = 0;
};

struct SyncSessionCheckpointResumeTransferClaimResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    bool transfer_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool transaction_committed = false;
    std::uint64_t workorder_claim_now_epoch = 0;
    std::uint64_t worker_lease_seconds = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t files_considered = 0;
    std::uint64_t files_claimed = 0;
    std::uint64_t files_skipped = 0;
    std::uint64_t files_abandoned = 0;
    std::uint64_t files_quarantined = 0;
    std::uint64_t workorder_rows_claimed = 0;
    std::uint64_t workorder_rows_already_owned = 0;
    std::uint64_t workorder_rows_reclaimed = 0;
    std::uint64_t workorder_reclaim_events_written = 0;
    std::uint64_t workorder_rows_abandoned = 0;
    std::uint64_t workorder_abandon_events_written = 0;
    std::uint64_t workorder_rows_quarantined = 0;
    std::uint64_t workorder_quarantine_events_written = 0;
    std::uint64_t chunks_assigned = 0;
    std::vector<SyncSessionCheckpointResumeTransferFileClaimResult> files;
};

struct SyncSessionCheckpointResumeTransferExecutionOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    std::string peer_id;
    std::string peer_session_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
    bool include_retry_transfer = true;
    std::string worker_id;
    std::uint64_t worker_lease_epoch = 1;
    std::uint64_t workorder_claim_now_epoch = 1;
    std::uint64_t worker_lease_seconds = 60;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    bool allow_expired_workorder_reclaim = true;
    std::uint64_t max_workorder_claim_attempts = 0;
    bool persist_workorder_claims = true;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
    std::vector<std::string> allowed_execution_idempotency_keys;
};

struct SyncSessionCheckpointResumeTransferFileExecutionResult {
    NormalizedSyncPath path;
    SyncSessionCheckpointResumeActionKind source_action = SyncSessionCheckpointResumeActionKind::RejectDrift;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string absolute_staging_path;
    bool transfer_plan_matched = false;
    bool workorder_claimed = false;
    bool source_chunks_verified = false;
    bool workorder_completed = false;
    bool staged_file_complete_after = false;
    bool database_rows_updated = false;
    std::uint64_t claimed_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t chunks_assigned = 0;
    std::uint64_t workorder_rows_claimed = 0;
    std::uint64_t workorder_rows_reclaimed = 0;
    std::uint64_t workorder_reclaim_events_written = 0;
    std::uint64_t workorder_rows_abandoned = 0;
    std::uint64_t workorder_abandon_events_written = 0;
    std::uint64_t workorder_rows_quarantined = 0;
    std::uint64_t workorder_quarantine_events_written = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    std::uint64_t receipt_rows_upserted = 0;
    std::uint64_t bytes_written = 0;
    std::uint64_t chunks_verified_after = 0;
    std::string content_sha256_after;
};

struct SyncSessionCheckpointResumeTransferExecutionResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    bool transfer_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool transaction_committed = false;
    std::uint64_t workorder_claim_now_epoch = 0;
    std::uint64_t worker_lease_seconds = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t files_considered = 0;
    std::uint64_t files_executed = 0;
    std::uint64_t files_skipped = 0;
    std::uint64_t workorder_rows_claimed = 0;
    std::uint64_t workorder_rows_reclaimed = 0;
    std::uint64_t workorder_reclaim_events_written = 0;
    std::uint64_t workorder_rows_abandoned = 0;
    std::uint64_t workorder_abandon_events_written = 0;
    std::uint64_t workorder_rows_quarantined = 0;
    std::uint64_t workorder_quarantine_events_written = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t chunks_assigned = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    std::uint64_t receipt_rows_upserted = 0;
    std::uint64_t bytes_written = 0;
    std::uint64_t post_materialize_staged_files = 0;
    std::uint64_t post_resume_transfer_files = 0;
    std::uint64_t post_retry_transfer_files = 0;
    std::vector<SyncSessionCheckpointResumeTransferFileExecutionResult> files;
};


struct SyncSessionCheckpointResumeTransferTerminalResetOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    std::string peer_id;
    std::string peer_session_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
    bool include_retry_transfer = true;
    std::string worker_id;
    std::uint64_t worker_lease_epoch = 1;
    std::uint64_t workorder_reset_now_epoch = 1;
    std::uint64_t worker_lease_seconds = 60;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    bool reset_abandoned_workorders = true;
    bool reset_quarantined_workorders = false;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
};

struct SyncSessionCheckpointResumeTransferTerminalResetFileResult {
    NormalizedSyncPath path;
    SyncSessionCheckpointResumeActionKind source_action = SyncSessionCheckpointResumeActionKind::RejectDrift;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string absolute_staging_path;
    bool transfer_plan_matched = false;
    std::uint64_t reset_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t chunks_assigned = 0;
    std::uint64_t terminal_rows_found = 0;
    std::uint64_t workorder_rows_reset = 0;
    std::uint64_t abandoned_rows_reset = 0;
    std::uint64_t quarantined_rows_reset = 0;
    std::uint64_t reset_events_written = 0;
};

struct SyncSessionCheckpointResumeTransferTerminalResetResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    bool transfer_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool transaction_committed = false;
    std::uint64_t workorder_reset_now_epoch = 0;
    std::uint64_t worker_lease_seconds = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t files_considered = 0;
    std::uint64_t files_reset = 0;
    std::uint64_t files_skipped = 0;
    std::uint64_t terminal_rows_found = 0;
    std::uint64_t workorder_rows_reset = 0;
    std::uint64_t abandoned_rows_reset = 0;
    std::uint64_t quarantined_rows_reset = 0;
    std::uint64_t reset_events_written = 0;
    std::uint64_t chunks_assigned = 0;
    std::vector<SyncSessionCheckpointResumeTransferTerminalResetFileResult> files;
};


enum class SyncSessionCheckpointResumeTransferWorkorderQueueKind {
    OwnedClaimReady,
    LiveClaimedByOther,
    ExpiredCoolingDown,
    ExpiredReclaimReady,
    ExpiredAbandonReady,
    AbandonedReview,
    QuarantinedReview,
    CompletedIgnored
};

struct SyncSessionCheckpointResumeTransferWorkorderQueueOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    std::string worker_id;
    std::string worker_lease_id;
    std::uint64_t queue_now_epoch = 1;
    std::uint64_t max_workorder_claim_attempts = 0;
    bool include_completed_workorders = false;
};

struct SyncSessionCheckpointResumeTransferWorkorderQueueFact {
    NormalizedSyncPath path;
    SyncSessionCheckpointResumeTransferWorkorderQueueKind queue_kind = SyncSessionCheckpointResumeTransferWorkorderQueueKind::LiveClaimedByOther;
    std::string queue_reason;
    std::string work_state;
    std::string source_action;
    std::string request_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string chunk_sha256;
    std::string absolute_staging_path;
    bool owned_by_selector_worker = false;
    bool lease_expired = false;
    bool retry_window_open = false;
    bool terminal_review_required = false;
    bool reset_history_present = false;
    std::uint64_t chunk_offset = 0;
    std::uint64_t chunk_length = 0;
    std::uint64_t worker_lease_epoch = 0;
    std::uint64_t claimed_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t claim_attempts = 0;
    std::uint64_t reclaim_events_recorded = 0;
    std::uint64_t abandon_events_recorded = 0;
    std::uint64_t quarantine_events_recorded = 0;
    std::uint64_t reset_events_recorded = 0;
};

struct SyncSessionCheckpointResumeTransferWorkorderQueueResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    bool resume_view_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool read_only_scan_completed = false;
    std::uint64_t queue_now_epoch = 0;
    std::uint64_t max_workorder_claim_attempts = 0;
    std::uint64_t workorder_rows_considered = 0;
    std::uint64_t queue_facts_returned = 0;
    std::uint64_t owned_claim_ready_rows = 0;
    std::uint64_t live_claimed_by_other_rows = 0;
    std::uint64_t expired_cooling_down_rows = 0;
    std::uint64_t expired_reclaim_ready_rows = 0;
    std::uint64_t expired_abandon_ready_rows = 0;
    std::uint64_t abandoned_review_rows = 0;
    std::uint64_t quarantined_review_rows = 0;
    std::uint64_t completed_rows_ignored = 0;
    std::uint64_t reset_history_claimed_rows = 0;
    std::vector<SyncSessionCheckpointResumeTransferWorkorderQueueFact> facts;
};

enum class SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind {
    ExecuteOwnedClaim,
    ClaimOrReclaimExpired,
    AbandonExpired,
    ObserveLiveClaimedByOther,
    WaitRetryBackoff,
    ReviewAbandoned,
    ReviewQuarantined,
    IgnoreCompleted
};

struct SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    std::string worker_id;
    std::string worker_lease_id;
    std::uint64_t scheduler_now_epoch = 1;
    std::uint64_t max_workorder_claim_attempts = 0;
    std::uint64_t max_scheduler_actions = 0;
    bool include_completed_workorders = false;
};

struct SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction {
    NormalizedSyncPath path;
    SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind action_kind = SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind::ObserveLiveClaimedByOther;
    SyncSessionCheckpointResumeTransferWorkorderQueueKind source_queue_kind = SyncSessionCheckpointResumeTransferWorkorderQueueKind::LiveClaimedByOther;
    std::string action_reason;
    std::string queue_reason;
    std::string work_state;
    std::string source_action;
    std::string request_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string chunk_sha256;
    bool mutating_action = false;
    bool terminal_review_required = false;
    bool owned_by_scheduler_worker = false;
    bool lease_expired = false;
    bool retry_window_open = false;
    std::uint64_t scheduler_priority = 0;
    std::uint64_t scheduler_group_priority = 0;
    std::uint64_t scheduler_group_size = 0;
    std::uint64_t chunk_offset = 0;
    std::uint64_t chunk_length = 0;
    std::uint64_t claimed_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t claim_attempts = 0;
};

struct SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    bool queue_selected = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool scheduler_plan_completed = false;
    std::uint64_t scheduler_now_epoch = 0;
    std::uint64_t max_workorder_claim_attempts = 0;
    std::uint64_t max_scheduler_actions = 0;
    std::uint64_t queue_facts_considered = 0;
    std::uint64_t scheduler_action_groups_considered = 0;
    std::uint64_t scheduler_action_groups_returned = 0;
    std::uint64_t scheduler_action_groups_deferred_by_limit = 0;
    std::uint64_t scheduler_actions_deferred_by_limit = 0;
    std::uint64_t scheduler_actions_returned = 0;
    std::uint64_t mutating_actions_planned = 0;
    std::uint64_t execute_owned_claim_actions = 0;
    std::uint64_t claim_or_reclaim_expired_actions = 0;
    std::uint64_t abandon_expired_actions = 0;
    std::uint64_t observe_live_claimed_by_other_actions = 0;
    std::uint64_t wait_retry_backoff_actions = 0;
    std::uint64_t review_abandoned_actions = 0;
    std::uint64_t review_quarantined_actions = 0;
    std::uint64_t ignore_completed_actions = 0;
    SyncSessionCheckpointResumeTransferWorkorderQueueResult queue_result;
    std::vector<SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction> actions;
};

struct SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    std::string peer_id;
    std::string peer_session_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
    bool include_retry_transfer = true;
    std::string worker_id;
    std::uint64_t worker_lease_epoch = 1;
    std::uint64_t scheduler_now_epoch = 1;
    std::uint64_t worker_lease_seconds = 60;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    bool allow_expired_workorder_reclaim = true;
    std::uint64_t max_workorder_claim_attempts = 0;
    std::uint64_t max_scheduler_actions = 0;
    bool execute_owned_claim_actions = true;
    bool claim_or_reclaim_expired_actions = true;
    bool abandon_expired_actions = true;
    bool include_completed_workorders = false;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
};

struct SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    bool scheduler_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool scheduler_execution_completed = false;
    std::uint64_t scheduler_now_epoch = 0;
    std::uint64_t max_scheduler_actions = 0;
    std::uint64_t scheduler_actions_returned = 0;
    std::uint64_t mutating_actions_planned = 0;
    std::uint64_t mutating_action_groups_selected = 0;
    std::uint64_t execute_owned_claim_groups_selected = 0;
    std::uint64_t claim_or_reclaim_expired_groups_selected = 0;
    std::uint64_t abandon_expired_groups_selected = 0;
    std::uint64_t execute_owned_claim_actions_selected = 0;
    std::uint64_t claim_or_reclaim_expired_actions_selected = 0;
    std::uint64_t abandon_expired_actions_selected = 0;
    std::uint64_t nonmutating_actions_observed = 0;
    std::uint64_t scheduler_action_groups_deferred_by_limit = 0;
    std::uint64_t scheduler_actions_deferred_by_limit = 0;
    std::uint64_t execution_key_filters_built = 0;
    std::uint64_t claim_or_abandon_filter_keys = 0;
    std::uint64_t execute_filter_keys = 0;
    std::uint64_t claim_or_abandon_runs = 0;
    std::uint64_t execute_owned_runs = 0;
    std::uint64_t workorder_rows_claimed = 0;
    std::uint64_t workorder_rows_reclaimed = 0;
    std::uint64_t workorder_reclaim_events_written = 0;
    std::uint64_t workorder_rows_abandoned = 0;
    std::uint64_t workorder_abandon_events_written = 0;
    std::uint64_t workorder_rows_quarantined = 0;
    std::uint64_t workorder_quarantine_events_written = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t receipts_reused = 0;
    std::uint64_t receipt_rows_upserted = 0;
    std::uint64_t bytes_written = 0;
    SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult scheduler_result;
    SyncSessionCheckpointResumeTransferClaimResult claim_result;
    SyncSessionCheckpointResumeTransferExecutionResult execution_result;
};


struct SyncSessionCheckpointResumeCycleOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string source_root_path;
    std::string destination_root_path;
    std::string staging_root_path;
    std::string expected_folder_id;
    std::string expected_source_device_id;
    std::string expected_destination_device_id;
    std::string expected_peer_id;
    std::string peer_id;
    std::string peer_session_id;
    bool require_durable_integrity = true;
    bool require_source_filesystem_match = true;
    bool fail_on_quarantine_or_reject = true;
    bool include_retry_transfer = true;
    bool execute_transfer_workorders = true;
    bool execute_materializations = true;
    bool execute_cleanups = true;
    bool require_final_content_converged = true;
    bool require_final_staging_artifacts_cleaned = true;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
};

struct SyncSessionCheckpointResumeCycleResult {
    std::string sqlite_path;
    std::string session_id;
    bool initial_action_plan_loaded = false;
    bool transfer_executor_ran = false;
    bool materialize_executor_ran = false;
    bool cleanup_executor_ran = false;
    bool final_action_plan_loaded = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool final_destination_filesystem_verified = false;
    bool final_staging_artifacts_verified = false;
    bool final_converged = false;
    bool transaction_sequence_completed = false;
    std::uint64_t files_considered = 0;
    std::uint64_t transfer_files_executed = 0;
    std::uint64_t transfer_chunks_written = 0;
    std::uint64_t transfer_receipt_rows_upserted = 0;
    std::uint64_t transfer_workorder_rows_claimed = 0;
    std::uint64_t transfer_workorder_rows_completed = 0;
    std::uint64_t transfer_bytes_written = 0;
    std::uint64_t files_materialized = 0;
    std::uint64_t materialization_checkpoints_written = 0;
    std::uint64_t materialized_bytes = 0;
    std::uint64_t files_cleaned = 0;
    std::uint64_t cleanup_checkpoints_written = 0;
    std::uint64_t receipt_rows_cleaned = 0;
    std::uint64_t final_already_converged_files = 0;
    std::uint64_t final_remaining_action_files = 0;
    SyncSessionCheckpointResumeActionPlanResult initial_action_plan;
    SyncSessionCheckpointResumeTransferExecutionResult transfer_execution;
    SyncSessionCheckpointMaterializeResumeResult materialization_execution;
    SyncSessionCheckpointCleanupResumeResult cleanup_execution;
    SyncSessionCheckpointResumeActionPlanResult final_action_plan;
};


SyncValidationResult normalize_sync_relative_path(const std::string& raw_path, NormalizedSyncPath& out);
SyncValidationResult validate_sync_manifest_entry(const SyncManifestEntry& entry);
SyncValidationResult validate_sync_folder_manifest(const SyncFolderManifest& manifest);
SyncValidationResult build_sync_folder_manifest_from_directory(const SyncFolderScanOptions& options, SyncFolderManifest& out);
SyncValidationResult build_sync_manifest_diff_plan(const SyncFolderManifest& local, const SyncFolderManifest& remote, SyncManifestDiffPlan& out);
SyncValidationResult build_sync_local_apply_plan(const SyncManifestDiffPlan& diff_plan, const SyncLocalApplyOptions& options, SyncLocalApplyPlan& out);
SyncValidationResult materialize_staged_sync_file(const SyncManifestEntry& remote_file_entry,
                                                const SyncLocalApplyPlanEntry& apply_entry,
                                                const SyncStagedFileMaterializationOptions& options,
                                                SyncStagedFileMaterializationResult& out);
SyncValidationResult apply_sync_remote_tombstone(const SyncManifestEntry& remote_tombstone_entry,
                                                const SyncLocalApplyPlanEntry& apply_entry,
                                                const SyncTombstoneApplicationOptions& options,
                                                SyncTombstoneApplicationResult& out);
SyncValidationResult apply_sync_conflict_preservation(const SyncManifestEntry& remote_conflict_entry,
                                                     const SyncLocalApplyPlanEntry& apply_entry,
                                                     const SyncConflictPreservationOptions& options,
                                                     SyncConflictPreservationResult& out);
SyncValidationResult write_sync_staged_chunk(const SyncManifestEntry& remote_file_entry,
                                             const SyncLocalApplyPlanEntry& apply_entry,
                                             const SyncChunkRange& chunk,
                                             const std::string& chunk_bytes,
                                             const SyncChunkReceiptWriteOptions& options,
                                             SyncChunkReceiptWriteResult& out);
SyncValidationResult inspect_sync_staged_transfer(const SyncManifestEntry& remote_file_entry,
                                                  const SyncLocalApplyPlanEntry& apply_entry,
                                                  const SyncStagedTransferInspectionOptions& options,
                                                  SyncStagedTransferInspectionResult& out);
SyncValidationResult cleanup_sync_staged_transfer_artifacts(const SyncManifestEntry& remote_file_entry,
                                                           const SyncLocalApplyPlanEntry& apply_entry,
                                                           const SyncStagedTransferCleanupOptions& options,
                                                           SyncStagedTransferCleanupResult& out);
SyncValidationResult build_sync_chunk_request_plan(const SyncManifestEntry& remote_file_entry,
                                                   const SyncLocalApplyPlanEntry& apply_entry,
                                                   const SyncStagedTransferInspectionResult& inspection,
                                                   const SyncChunkRequestPlanOptions& options,
                                                   SyncChunkRequestPlanResult& out);
SyncValidationResult build_sync_chunk_response_envelope(const SyncManifestEntry& remote_file_entry,
                                                       const SyncLocalApplyPlanEntry& apply_entry,
                                                       const SyncChunkRequestPlanResult& request_plan,
                                                       const SyncChunkRange& response_chunk,
                                                       SyncChunkResponseEnvelope& out);
SyncValidationResult build_sync_chunk_response_batch_envelope(const SyncManifestEntry& remote_file_entry,
                                                             const SyncLocalApplyPlanEntry& apply_entry,
                                                             const SyncChunkRequestPlanResult& request_plan,
                                                             const std::vector<SyncChunkRange>& response_chunks,
                                                             SyncChunkResponseBatchEnvelope& out);
SyncValidationResult accept_sync_requested_chunk(const SyncManifestEntry& remote_file_entry,
                                                const SyncLocalApplyPlanEntry& apply_entry,
                                                const SyncStagedTransferInspectionResult& inspection,
                                                const SyncChunkRequestPlanOptions& request_options,
                                                const SyncChunkRequestPlanResult& request_plan,
                                                const SyncChunkRange& response_chunk,
                                                const std::string& chunk_bytes,
                                                const SyncChunkReceiptWriteOptions& write_options,
                                                SyncRequestedChunkAcceptanceResult& out);
SyncValidationResult accept_sync_chunk_response_envelope(const SyncManifestEntry& remote_file_entry,
                                                        const SyncLocalApplyPlanEntry& apply_entry,
                                                        const SyncStagedTransferInspectionResult& inspection,
                                                        const SyncChunkRequestPlanOptions& request_options,
                                                        const SyncChunkRequestPlanResult& request_plan,
                                                        const SyncChunkResponseEnvelope& response_envelope,
                                                        const std::string& chunk_bytes,
                                                        const SyncChunkReceiptWriteOptions& write_options,
                                                        SyncRequestedChunkAcceptanceResult& out);
SyncValidationResult accept_sync_chunk_response_batch_envelope(const SyncManifestEntry& remote_file_entry,
                                                              const SyncLocalApplyPlanEntry& apply_entry,
                                                              const SyncStagedTransferInspectionResult& inspection,
                                                              const SyncChunkRequestPlanOptions& request_options,
                                                              const SyncChunkRequestPlanResult& request_plan,
                                                              const SyncChunkResponseBatchEnvelope& batch_envelope,
                                                              const std::vector<std::string>& chunk_bytes,
                                                              const SyncChunkReceiptWriteOptions& write_options,
                                                              SyncChunkResponseBatchAcceptanceResult& out);
SyncValidationResult accept_sync_chunk_response_batch_and_plan_next(const SyncManifestEntry& remote_file_entry,
                                                                   const SyncLocalApplyPlanEntry& apply_entry,
                                                                   const SyncStagedTransferInspectionResult& inspection,
                                                                   const SyncChunkRequestPlanOptions& request_options,
                                                                   const SyncChunkRequestPlanResult& request_plan,
                                                                   const SyncChunkResponseBatchEnvelope& batch_envelope,
                                                                   const std::vector<std::string>& chunk_bytes,
                                                                   const SyncChunkReceiptWriteOptions& write_options,
                                                                   const SyncStagedTransferInspectionOptions& inspection_options,
                                                                   SyncChunkTransferRoundResult& out);
SyncValidationResult build_sync_peer_chunk_schedule(const SyncManifestEntry& remote_file_entry,
                                                 const SyncLocalApplyPlanEntry& apply_entry,
                                                 const SyncChunkRequestPlanResult& request_plan,
                                                 const std::vector<SyncPeerChunkAvailability>& peer_availabilities,
                                                 SyncPeerChunkScheduleResult& out);
SyncValidationResult build_sync_peer_chunk_response_batch_envelope(const SyncManifestEntry& remote_file_entry,
                                                                   const SyncLocalApplyPlanEntry& apply_entry,
                                                                   const SyncChunkRequestPlanResult& request_plan,
                                                                   const SyncPeerChunkScheduleResult& peer_schedule,
                                                                   const SyncPeerChunkAssignment& peer_assignment,
                                                                   const std::vector<SyncChunkRange>& response_chunks,
                                                                   SyncPeerChunkResponseBatchEnvelope& out);
SyncValidationResult accept_sync_peer_chunk_response_batch_envelope(const SyncManifestEntry& remote_file_entry,
                                                                    const SyncLocalApplyPlanEntry& apply_entry,
                                                                    const SyncStagedTransferInspectionResult& inspection,
                                                                    const SyncChunkRequestPlanOptions& request_options,
                                                                    const SyncChunkRequestPlanResult& request_plan,
                                                                    const SyncPeerChunkScheduleResult& peer_schedule,
                                                                    const SyncPeerChunkAssignment& peer_assignment,
                                                                    const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                    const std::vector<std::string>& chunk_bytes,
                                                                    const SyncChunkReceiptWriteOptions& write_options,
                                                                    SyncPeerChunkResponseBatchAcceptanceResult& out);
SyncValidationResult accept_sync_peer_chunk_response_batch_and_plan_next(const SyncManifestEntry& remote_file_entry,
                                                                        const SyncLocalApplyPlanEntry& apply_entry,
                                                                        const SyncStagedTransferInspectionResult& inspection,
                                                                        const SyncChunkRequestPlanOptions& request_options,
                                                                        const SyncChunkRequestPlanResult& request_plan,
                                                                        const SyncPeerChunkScheduleResult& peer_schedule,
                                                                        const SyncPeerChunkAssignment& peer_assignment,
                                                                        const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                        const std::vector<std::string>& chunk_bytes,
                                                                        const SyncChunkReceiptWriteOptions& write_options,
                                                                        const SyncStagedTransferInspectionOptions& inspection_options,
                                                                        const std::vector<SyncPeerChunkAvailability>& next_peer_availabilities,
                                                                        SyncPeerChunkTransferRoundResult& out);
SyncValidationResult run_sync_fake_peer_file_fetch_session(const SyncFakePeerFileFetchSessionOptions& options,
                                                                       SyncFakePeerFileFetchSessionResult& out);
SyncValidationResult persist_sync_fake_peer_session_checkpoint(const SyncFakePeerFileFetchSessionOptions& run_options,
                                                            const SyncFakePeerFileFetchSessionResult& session_result,
                                                            const SyncSessionCheckpointOptions& options,
                                                            SyncSessionCheckpointResult& out);
SyncValidationResult load_sync_session_checkpoint_resume_view(const SyncSessionCheckpointResumeViewOptions& options,
                                                              SyncSessionCheckpointResumeViewResult& out);
SyncValidationResult repair_sync_session_checkpoint_staging_artifacts(const SyncSessionCheckpointStagingRepairOptions& options,
                                                                      SyncSessionCheckpointStagingRepairResult& out);
SyncValidationResult plan_sync_session_checkpoint_resume_actions(const SyncSessionCheckpointResumeActionPlanOptions& options,
                                                                 SyncSessionCheckpointResumeActionPlanResult& out);
SyncValidationResult execute_sync_session_checkpoint_resume_materializations(const SyncSessionCheckpointMaterializeResumeOptions& options,
                                                                                           SyncSessionCheckpointMaterializeResumeResult& out);
SyncValidationResult execute_sync_session_checkpoint_resume_cleanups(const SyncSessionCheckpointCleanupResumeOptions& options,
                                                                    SyncSessionCheckpointCleanupResumeResult& out);
SyncValidationResult plan_sync_session_checkpoint_resume_transfers(const SyncSessionCheckpointResumeTransferPlanOptions& options,
                                                                    SyncSessionCheckpointResumeTransferPlanResult& out);
SyncValidationResult claim_sync_session_checkpoint_resume_transfer_workorders(const SyncSessionCheckpointResumeTransferClaimOptions& options,
                                                                              SyncSessionCheckpointResumeTransferClaimResult& out);
SyncValidationResult execute_sync_session_checkpoint_resume_transfer_workorders(const SyncSessionCheckpointResumeTransferExecutionOptions& options,
                                                                                SyncSessionCheckpointResumeTransferExecutionResult& out);
SyncValidationResult reset_sync_session_checkpoint_resume_transfer_terminal_workorders(const SyncSessionCheckpointResumeTransferTerminalResetOptions& options,
                                                                                                  SyncSessionCheckpointResumeTransferTerminalResetResult& out);
SyncValidationResult select_sync_session_checkpoint_resume_transfer_workorder_queue(const SyncSessionCheckpointResumeTransferWorkorderQueueOptions& options,
                                                                                                      SyncSessionCheckpointResumeTransferWorkorderQueueResult& out);
SyncValidationResult plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(const SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions& options,
                                                                                                      SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult& out);
SyncValidationResult execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(const SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions& options,
                                                                                              SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult& out);
SyncValidationResult execute_sync_session_checkpoint_resume_cycle(const SyncSessionCheckpointResumeCycleOptions& options,
                                                                  SyncSessionCheckpointResumeCycleResult& out);
std::string sync_manifest_entry_digest(const SyncManifestEntry& entry);
std::string sync_manifest_entry_version_digest(const SyncManifestEntry& entry);
std::string sync_folder_manifest_digest(const SyncFolderManifest& manifest);
std::string sync_mutation_idempotency_key(const std::string& operation, const SyncManifestEntry& entry);

struct IngressReservationServiceHandle {
    std::string service_config_path;
    std::string service_config_sha256;
};

struct IngressTransportContext {
    bool transport_authenticated = false;
    std::string authenticator;
    std::string principal;
};

struct IngressReservationResult {
    int status_code = 1;
    bool accepted = false;
    std::string report_json;
    std::string failure_reason;
};

IngressReservationResult reserve_ingress_request_json(const IngressReservationServiceHandle& operator_service_handle,
                                                        const IngressTransportContext& trusted_transport_context,
                                                        const std::string& request_json_text);
int run(const std::string& controls_path,
        const std::string& report_path,
        const std::string& contracts_path,
        const std::string& cases_jsonl_path,
        const std::string& ledger_path,
        bool ledger_reset,
        const std::string& ledger_commit_mode = "immediate",
        const std::string& ledger_backend = "local-jsonl",
        const std::string& ledger_backend_capabilities_path = "",
        const std::string& ledger_snapshot_path = "",
        const std::string& ledger_restore_from_snapshot_path = "",
        const std::string& ledger_snapshot_manifest_path = "",
        const std::string& ledger_snapshot_trust_profile_path = "",
        const std::string& ledger_snapshot_trust_profile_sha256 = "");
int run_sync_domain_model_selftest();
int run_parser_boundary_selftest();
int run_boundary_fuzz_selftest();
int run_json_codec_fuzz_selftest();
int run_jwt_codec_fuzz_selftest();
int run_route_event_ledger_fuzz_selftest();
int run_ledger_durable_io_selftest();
int run_ledger_backend_adapter_selftest();
int run_ledger_crash_injection_selftest();
int run_ledger_batch_transaction_selftest();
int run_ledger_journal_hardening_selftest();
int run_ledger_backend_interface_selftest();
int run_ledger_sqlite_wal_selftest();
int run_ledger_event_identity_replay_selftest();
int run_ledger_effect_idempotency_selftest();
int run_ledger_sqlite_effect_transition_selftest();
int run_ledger_sqlite_effect_pending_recovery_selftest();
int run_ledger_sqlite_effect_signed_transition_selftest();
int run_sqlite_effect_transition_command(const std::string& ledger_path, const std::string& effect_idempotency_key, long long prepared_sequence, const std::string& prepared_entry_hash, const std::string& terminal_state, const std::string& result_digest_sha256, const std::string& transition_reason);
int run_sqlite_effect_signed_transition_command(const std::string& ledger_path, const std::string& intent_path, const std::string& trust_profile_path, const std::string& trust_profile_sha256);
int run_sqlite_effect_pending_report_command(const std::string& ledger_path, const std::string& report_path);
int run_sqlite_effect_outbox_claim_command(const std::string& ledger_path, const std::string& worker_id, long long now_epoch, long long lease_seconds, const std::string& claim_report_path);
int run_sqlite_effect_relay_once_command(const std::string& ledger_path, const std::string& downstream_path, const std::string& worker_id, long long now_epoch, long long lease_seconds, const std::string& terminal_state, const std::string& signer_private_key_pem_path, const std::string& signer_kid, const std::string& trust_profile_path, const std::string& trust_profile_sha256, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_sqlite_effect_relay_configured_once_command(const std::string& ledger_path, const std::string& relay_config_path, const std::string& relay_config_sha256, long long now_epoch, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_sqlite_effect_relay_handle_once_command(const std::string& ledger_path, const std::string& relay_registry_path, const std::string& relay_registry_sha256, const std::string& relay_config_handle, long long now_epoch, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_ingress_reservation_command(const std::string& ingress_profile_path, const std::string& ingress_profile_sha256, const std::string& ingress_request_path, const std::string& ingress_report_path);
int run_ingress_reservation_service_command(const std::string& ingress_service_config_path,
                                            const std::string& ingress_service_config_sha256,
                                            const std::string& ingress_transport_context_path,
                                            const std::string& ingress_request_path,
                                            const std::string& ingress_report_path);
int run_ingress_reservation_service_selftest();
int run_ledger_sqlite_effect_outbox_claim_selftest();
int run_ledger_sqlite_effect_relay_selftest();
int run_ledger_sqlite_effect_relay_configured_selftest();
int run_ledger_sqlite_effect_relay_handle_selftest();
int run_ledger_sqlite_hardening_selftest();
int run_ledger_backend_capabilities_selftest();
int run_ledger_sqlite_crash_corpus_selftest();
int run_ledger_sqlite_backup_restore_selftest();
int run_ledger_host_capability_probe_selftest();
int run_ledger_sqlite_snapshot_corpus_selftest();
int run_ledger_sqlite_restore_corpus_selftest();
int run_ledger_snapshot_manifest_verifier_selftest();
int run_ledger_sqlite_restore_rollback_guard_selftest();
int run_ledger_sqlite_restore_atomicity_selftest();
int run_ledger_sqlite_restore_locking_selftest();
int run_ledger_sqlite_restore_manifest_binding_selftest();
int run_ledger_sqlite_restore_write_gate_selftest();
int run_ledger_sqlite_restore_prefix_continuity_selftest();
int run_ledger_sqlite_readonly_snapshot_verifier_selftest();
int run_ledger_host_capability_report(const std::string& report_path);
int run_sqlite_writer_lock_holder(const std::string& ledger_path, long long seconds);
int run_sqlite_restore_lock_holder(const std::string& ledger_path, long long seconds);
int run_sqlite_write_gate_holder(const std::string& ledger_path, long long seconds);
int run_ledger_lock_holder(const std::string& ledger_path, long long seconds);
}  // namespace anonsync
