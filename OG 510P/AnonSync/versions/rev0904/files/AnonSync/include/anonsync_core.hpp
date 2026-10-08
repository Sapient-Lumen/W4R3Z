#pragma once

#include "anonsync_sync_checkpoint_owner_fence.hpp"

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

struct SyncPeerTransportEnvelopeBuildOptions {
    std::string transport_instance_id;
    std::string transport_key_id;
    std::string shared_secret;
    std::uint64_t issued_at_epoch = 1;
    std::uint64_t expires_at_epoch = 0;
    std::uint64_t max_response_count = 0;
    std::uint64_t max_total_bytes = 0;
    std::uint64_t max_chunk_bytes = 0;
};

struct SyncPeerTransportEnvelopeVerifyOptions {
    std::string expected_transport_instance_id;
    std::string expected_transport_key_id;
    std::string shared_secret;
    std::string expected_peer_id;
    std::string expected_peer_session_id;
    std::uint64_t verify_now_epoch = 1;
    std::uint64_t max_response_count = 0;
    std::uint64_t max_total_bytes = 0;
    std::uint64_t max_chunk_bytes = 0;
};

struct SyncPeerTransportBoundChunkResponseBatchEnvelope {
    SyncPeerChunkResponseBatchEnvelope peer_batch_envelope;
    std::string transport_instance_id;
    std::string transport_key_id;
    std::string transport_envelope_idempotency_key;
    std::string transport_mac_sha256;
    std::uint64_t issued_at_epoch = 0;
    std::uint64_t expires_at_epoch = 0;
    std::uint64_t max_response_count = 0;
    std::uint64_t max_total_bytes = 0;
    std::uint64_t max_chunk_bytes = 0;
};

// Stable public facade over the one self-contained canonical ingress frame.
// Transport fixtures, durable queue evidence, restart recovery, and callers of
// this API therefore share one versioned byte identity rather than competing
// migration and production encodings.
inline constexpr std::uint32_t kSyncPeerTransportCanonicalWireVersion = 1;
inline constexpr std::uint64_t kSyncPeerTransportDefaultMaxCanonicalPayloadBytes =
    64ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t kSyncPeerTransportDefaultMaxCanonicalStringBytes =
    1ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t kSyncPeerTransportDefaultMaxCanonicalResponseCount = 4096;

struct SyncPeerTransportCanonicalCodecLimits {
    std::uint64_t max_wire_bytes = kSyncPeerTransportDefaultMaxCanonicalPayloadBytes;
    std::uint64_t max_string_bytes = kSyncPeerTransportDefaultMaxCanonicalStringBytes;
    std::uint64_t max_response_count = kSyncPeerTransportDefaultMaxCanonicalResponseCount;
    std::uint64_t max_total_chunk_bytes = kSyncPeerTransportDefaultMaxCanonicalPayloadBytes;
    std::uint64_t max_chunk_bytes = kSyncPeerTransportDefaultMaxCanonicalPayloadBytes;
};

struct SyncPeerTransportCanonicalPayload {
    SyncPeerTransportBoundChunkResponseBatchEnvelope transport_envelope;
    std::vector<std::string> chunk_bytes;
};

struct SyncPeerTransportBoundChunkResponseBatchAcceptanceResult {
    SyncPeerChunkResponseBatchAcceptanceResult peer_batch_acceptance;
    std::string transport_instance_id;
    std::string transport_key_id;
    std::string transport_envelope_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    bool transport_envelope_checked = false;
    bool transport_mac_checked = false;
    bool transport_bounds_checked = false;
    bool peer_batch_acceptance_attempted = false;
    bool peer_batch_acceptance_completed = false;
    std::uint64_t response_count = 0;
    std::uint64_t total_bytes = 0;
    std::uint64_t chunks_written = 0;
    std::uint64_t bytes_authenticated = 0;
};

inline constexpr std::uint64_t kSyncPeerTransportDefaultSqliteBusyTimeoutMs = 1000;
inline constexpr std::uint64_t kSyncPeerTransportMaxSqliteBusyTimeoutMs = 60000;

// Evidence from bounded SQLite write-lock acquisition. A zero configured
// timeout means fail fast; every nonzero timeout is capped by the public max.
// SQLITE_BUSY and SQLITE_LOCKED are reported separately because SQLite assigns
// them different concurrency meanings and may bypass a busy handler to avoid a
// deadlock. Counters aggregate when an operation uses more than one write
// transaction (for example ingress claim followed by completion).
struct SyncPeerTransportSqliteWriteContentionResult {
    std::uint64_t configured_busy_timeout_ms = 0;
    std::uint64_t busy_handler_invocations = 0;
    std::uint64_t busy_sleep_ms = 0;
    std::uint64_t write_lock_attempts = 0;
    std::uint64_t write_locks_acquired = 0;
    std::uint64_t write_lock_wait_elapsed_ms = 0;
    bool busy_handler_installed = false;
    bool contention_observed = false;
    bool sqlite_busy = false;
    bool sqlite_locked = false;
    bool busy_timeout_exhausted = false;
    std::int32_t primary_result_code = 0;
    std::int32_t extended_result_code = 0;
    std::string result_code_name;
    std::string failure_operation;
    // Journal selection is durable-policy evidence, not an implementation
    // detail. Fixed runtimes use verified WAL/FULL. An explicitly permitted
    // affected system runtime is forced to verified DELETE/FULL for internal
    // stores and exposes that concurrency downgrade through the fallback flag.
    std::string sqlite_runtime_version;
    std::string sqlite_runtime_source_id;
    std::string sqlite_journal_mode;
    bool sqlite_durability_profile_checked = false;
    bool sqlite_runtime_bundled = false;
    bool sqlite_wal_reset_fix_known = false;
    bool sqlite_rollback_journal_fallback_active = false;
};

struct SyncPeerTransportAuthorityRecordOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string peer_id;
    std::string peer_session_id;
    std::string transport_instance_id;
    std::string transport_key_id;
    // trusted allows use; disabled/revoked deny use while preserving evidence.
    std::string authority_status = "trusted";
    std::uint64_t valid_from_epoch = 1;
    // Zero means no local expiry.
    std::uint64_t valid_until_epoch = 0;
    std::uint64_t updated_at_epoch = 1;
    std::string reason;
    std::uint64_t sqlite_busy_timeout_ms = kSyncPeerTransportDefaultSqliteBusyTimeoutMs;
};

struct SyncPeerTransportAuthorityRecordResult {
    std::string sqlite_path;
    std::string session_id;
    std::string peer_id;
    std::string peer_session_id;
    std::string transport_instance_id;
    std::string transport_key_id;
    std::string authority_status;
    std::uint64_t valid_from_epoch = 0;
    std::uint64_t valid_until_epoch = 0;
    std::uint64_t updated_at_epoch = 0;
    bool record_inserted = false;
    bool record_updated = false;
    SyncPeerTransportSqliteWriteContentionResult sqlite_write_contention;
};

struct SyncPeerTransportAuthoritySupersessionRecordOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string peer_id;
    std::string peer_session_id;
    std::string transport_instance_id;
    std::string old_transport_key_id;
    std::string replacement_transport_key_id;
    // Inclusive overlap in which the old key may still be accepted while the
    // replacement key is being adopted. After overlap_valid_until_epoch, the
    // old key is denied as superseded-expired.
    std::uint64_t overlap_valid_from_epoch = 1;
    std::uint64_t overlap_valid_until_epoch = 1;
    std::uint64_t updated_at_epoch = 1;
    std::string reason;
    std::uint64_t sqlite_busy_timeout_ms = kSyncPeerTransportDefaultSqliteBusyTimeoutMs;
};

struct SyncPeerTransportAuthoritySupersessionRecordResult {
    std::string sqlite_path;
    std::string session_id;
    std::string peer_id;
    std::string peer_session_id;
    std::string transport_instance_id;
    std::string old_transport_key_id;
    std::string replacement_transport_key_id;
    std::uint64_t overlap_valid_from_epoch = 0;
    std::uint64_t overlap_valid_until_epoch = 0;
    std::uint64_t updated_at_epoch = 0;
    bool record_inserted = false;
    bool record_updated = false;
    SyncPeerTransportSqliteWriteContentionResult sqlite_write_contention;
};

struct SyncPeerTransportAuthorityDecisionOptions {
    std::string sqlite_path;
    std::string session_id;
    std::uint64_t decision_now_epoch = 1;
};

struct SyncPeerTransportAuthorityDecisionResult {
    std::string sqlite_path;
    std::string session_id;
    std::string transport_envelope_idempotency_key;
    std::string payload_digest;
    std::string peer_id;
    std::string peer_session_id;
    std::string transport_instance_id;
    std::string transport_key_id;
    bool authority_checked = false;
    bool authority_record_found = false;
    bool authority_allowed = false;
    bool authority_denied = false;
    bool denial_recorded = false;
    bool denial_already_present = false;
    bool authority_supersession_found = false;
    bool authority_supersession_overlap_valid = false;
    bool authority_supersession_expired = false;
    std::string authority_status;
    std::string authority_lifecycle_state;
    std::uint64_t valid_from_epoch = 0;
    std::uint64_t valid_until_epoch = 0;
    std::string replacement_transport_key_id;
    std::uint64_t supersession_overlap_valid_from_epoch = 0;
    std::uint64_t supersession_overlap_valid_until_epoch = 0;
    std::string authority_reason;
    std::string supersession_reason;
    std::string deny_reason;
};

struct SyncPeerTransportIngressEnqueueOptions {
    std::string sqlite_path;
    std::string session_id;
    std::uint64_t enqueue_now_epoch = 1;
    std::uint64_t max_attempts = 3;
    std::uint64_t retry_backoff_seconds = 30;
    // Zero means unlimited. Nonzero caps are enforced before inserting a new row;
    // duplicate matching payloads remain idempotent queue observations.
    std::uint64_t max_open_rows = 0;
    std::uint64_t max_open_bytes = 0;
    std::uint64_t max_peer_open_rows = 0;
    std::uint64_t max_peer_open_bytes = 0;
    // Logical payload bytes and durable canonical-frame bytes are deliberately
    // distinct pressure dimensions. Metadata-rich frames can be much larger
    // than their chunk payload, so a deployment that needs a hard database
    // growth bound should set these physical evidence caps as well.
    std::uint64_t max_open_frame_bytes = 0;
    std::uint64_t max_peer_open_frame_bytes = 0;
    // Canonical payload evidence is stored in the same SQLite transaction as
    // queue admission. These bounds apply before any untrusted allocation.
    std::uint64_t max_frame_bytes = 16 * 1024 * 1024;
    std::uint64_t max_chunk_count = 1024;
    bool require_authority_gate = false;
    // Compatibility alias retained while callers converge on frame terminology.
    // The effective limit is the smaller value, so mixed callers fail closed.
    std::uint64_t max_canonical_payload_bytes =
        kSyncPeerTransportDefaultMaxCanonicalPayloadBytes;
    std::uint64_t sqlite_busy_timeout_ms = kSyncPeerTransportDefaultSqliteBusyTimeoutMs;
};

struct SyncPeerTransportIngressEnqueueResult {
    std::string sqlite_path;
    std::string session_id;
    std::string transport_envelope_idempotency_key;
    std::string payload_digest;
    bool row_inserted = false;
    bool row_already_present = false;
    bool payload_frame_stored = false;
    bool payload_frame_already_present = false;
    std::uint64_t payload_frame_codec_version = 0;
    std::uint64_t payload_frame_bytes = 0;
    std::string payload_frame_sha256;
    // Compatibility result aliases populated from the same canonical-frame evidence.
    bool canonical_payload_encoded = false;
    bool canonical_payload_persisted = false;
    bool canonical_payload_reused = false;
    bool legacy_payload_backfilled = false;
    std::uint64_t canonical_payload_codec_version = 0;
    std::uint64_t canonical_payload_bytes = 0;
    std::string canonical_payload_sha256;
    bool backpressure_checked = false;
    bool backpressure_rejected = false;
    std::uint64_t max_attempts = 0;
    std::uint64_t retry_backoff_seconds = 0;
    std::uint64_t open_rows_before = 0;
    std::uint64_t open_bytes_before = 0;
    std::uint64_t open_frame_bytes_before = 0;
    std::uint64_t peer_open_rows_before = 0;
    std::uint64_t peer_open_bytes_before = 0;
    std::uint64_t peer_open_frame_bytes_before = 0;
    std::uint64_t max_open_rows = 0;
    std::uint64_t max_open_bytes = 0;
    std::uint64_t max_open_frame_bytes = 0;
    std::uint64_t max_peer_open_rows = 0;
    std::uint64_t max_peer_open_bytes = 0;
    std::uint64_t max_peer_open_frame_bytes = 0;
    SyncPeerTransportAuthorityDecisionResult authority_decision;
    SyncPeerTransportSqliteWriteContentionResult sqlite_write_contention;
};

struct SyncPeerTransportIngressPayloadLoadOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string transport_envelope_idempotency_key;
    std::uint64_t max_frame_bytes = 16 * 1024 * 1024;
    std::uint64_t max_chunk_count = 1024;
    // Compatibility alias; the smaller configured bound wins.
    std::uint64_t max_canonical_payload_bytes =
        kSyncPeerTransportDefaultMaxCanonicalPayloadBytes;
};

struct SyncPeerTransportIngressPayloadLoadResult {
    SyncPeerTransportBoundChunkResponseBatchEnvelope transport_envelope;
    std::vector<std::string> chunk_bytes;
    std::string sqlite_path;
    std::string session_id;
    std::string transport_envelope_idempotency_key;
    std::string payload_digest;
    std::string canonical_frame_sha256;
    std::uint64_t canonical_frame_bytes = 0;
    std::uint64_t codec_version = 0;
    std::uint64_t stored_at_epoch = 0;
    bool row_found = false;
    bool payload_found = false;
    bool frame_digest_checked = false;
    bool payload_digest_checked = false;
    bool canonical_frame_decoded = false;
    // Compatibility load-result aliases.
    bool durable_payload_present = false;
    bool canonical_payload_hash_checked = false;
    bool canonical_payload_decoded = false;
    std::uint64_t canonical_payload_codec_version = 0;
    std::uint64_t canonical_payload_bytes = 0;
    std::string canonical_payload_sha256;
    SyncPeerTransportCanonicalPayload payload;
};

struct SyncPeerTransportIngressProcessOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    // Used only by the queued-processing compatibility entry point.
    std::string transport_envelope_idempotency_key;
    std::uint64_t process_now_epoch = 1;
    std::uint64_t lease_duration_seconds = 60;
    std::uint64_t retry_backoff_seconds = 30;
    std::uint64_t max_attempts = 3;
    bool require_authority_gate = false;
    // Deterministic crash-window proof hook. When enabled, successful receipt-backed
    // acceptance returns before the queue completion transaction, leaving the claim
    // recoverable after its lease expires.
    bool controlled_abort_after_acceptance_before_completion = false;
    std::uint64_t max_frame_bytes = 16 * 1024 * 1024;
    std::uint64_t max_chunk_count = 1024;
    // Compatibility alias; the smaller configured bound wins.
    std::uint64_t max_canonical_payload_bytes =
        kSyncPeerTransportDefaultMaxCanonicalPayloadBytes;
    std::uint64_t sqlite_busy_timeout_ms = kSyncPeerTransportDefaultSqliteBusyTimeoutMs;
};

struct SyncPeerTransportIngressProcessResult {
    SyncPeerTransportBoundChunkResponseBatchAcceptanceResult acceptance;
    std::string sqlite_path;
    std::string session_id;
    std::string transport_envelope_idempotency_key;
    std::string payload_digest;
    // Deterministic identity of the exact durable claim generation observed or acquired.
    // Empty only when no claimed generation was reached.
    std::string claim_generation_id;
    std::string state_before;
    std::string state_after;
    bool row_found = false;
    bool payload_digest_checked = false;
    bool durable_payload_checked = false;
    bool durable_payload_missing = false;
    bool durable_payload_matches_submission = false;
    bool durable_payload_claim_snapshot_checked = false;
    bool durable_payload_completion_snapshot_checked = false;
    std::uint64_t durable_payload_codec_version = 0;
    std::uint64_t durable_payload_frame_bytes = 0;
    std::string durable_payload_frame_sha256;
    // Compatibility process-result aliases.
    bool durable_payload_loaded = false;
    bool canonical_payload_hash_checked = false;
    bool canonical_payload_decoded = false;
    bool caller_payload_matches_durable = false;
    std::uint64_t canonical_payload_codec_version = 0;
    std::uint64_t canonical_payload_bytes = 0;
    std::string canonical_payload_sha256;
    bool claimed = false;
    bool live_claim_deferred = false;
    bool retry_backoff_deferred = false;
    bool already_completed = false;
    bool acceptance_attempted = false;
    bool acceptance_completed = false;
    bool expired_claim_reconciliation_attempted = false;
    bool expired_claim_reconciliation_snapshot_matched = false;
    bool expired_claim_reconciliation_snapshot_changed = false;
    bool expired_claim_completed_from_receipts = false;
    bool expired_claim_reconciliation_blocked = false;
    bool operator_review_required = false;
    bool controlled_abort_after_acceptance_before_completion = false;
    bool retry_scheduled = false;
    bool abandoned = false;
    std::string receipt_evidence_state;
    std::string expired_claim_recovery_action;
    std::uint64_t expected_receipts = 0;
    std::uint64_t matching_receipts = 0;
    std::uint64_t missing_receipts = 0;
    std::uint64_t conflicting_receipts = 0;
    std::string receipt_evidence_reason;
    std::uint64_t attempts_after_claim = 0;
    std::uint64_t max_attempts = 0;
    std::uint64_t claimed_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_at_epoch = 0;
    std::string failure_reason;
    SyncPeerTransportAuthorityDecisionResult authority_decision;
    SyncPeerTransportSqliteWriteContentionResult sqlite_write_contention;
};

struct SyncPeerTransportIngressStatusOptions {
    std::string sqlite_path;
    std::string session_id;
    std::uint64_t status_now_epoch = 1;
};

struct SyncPeerTransportIngressStatusResult {
    std::string sqlite_path;
    std::string session_id;
    bool table_present = false;
    std::uint64_t total_rows = 0;
    std::uint64_t open_rows = 0;
    std::uint64_t open_bytes = 0;
    std::uint64_t queued_rows = 0;
    std::uint64_t queued_bytes = 0;
    std::uint64_t claimed_rows = 0;
    std::uint64_t claimed_bytes = 0;
    std::uint64_t completed_rows = 0;
    std::uint64_t completed_bytes = 0;
    std::uint64_t failed_rows = 0;
    std::uint64_t failed_bytes = 0;
    std::uint64_t abandoned_rows = 0;
    std::uint64_t abandoned_bytes = 0;
    // Durable evidence accounting is kept separate from logical payload
    // accounting. Missing rows are an integrity signal, not zero-byte payloads.
    bool payload_table_present = false;
    std::uint64_t durable_payload_rows = 0;
    std::uint64_t durable_payload_frame_bytes = 0;
    std::uint64_t open_durable_payload_frame_bytes = 0;
    std::uint64_t queued_durable_payload_frame_bytes = 0;
    std::uint64_t claimed_durable_payload_frame_bytes = 0;
    std::uint64_t completed_durable_payload_frame_bytes = 0;
    std::uint64_t failed_durable_payload_frame_bytes = 0;
    std::uint64_t abandoned_durable_payload_frame_bytes = 0;
    std::uint64_t rows_missing_durable_payload = 0;
    std::uint64_t open_rows_missing_durable_payload = 0;
    std::uint64_t orphan_durable_payload_rows = 0;
    std::uint64_t orphan_durable_payload_frame_bytes = 0;
    bool authority_denial_table_present = false;
    std::uint64_t authority_denied_rows = 0;
    std::uint64_t authority_denied_bytes = 0;
    std::uint64_t authority_superseded_expired_denied_rows = 0;
    std::uint64_t authority_superseded_expired_denied_bytes = 0;
    bool authority_supersession_table_present = false;
    std::uint64_t authority_supersession_rows = 0;
    bool retention_event_table_present = false;
    std::uint64_t retention_event_rows = 0;
    std::uint64_t retention_drained_ingress_rows = 0;
    std::uint64_t retention_drained_ingress_bytes = 0;
    std::uint64_t retention_drained_authority_denial_rows = 0;
    std::uint64_t retention_drained_authority_denial_bytes = 0;
    std::uint64_t terminal_retention_candidate_rows = 0;
    std::uint64_t terminal_retention_candidate_bytes = 0;
    std::uint64_t authority_denial_retention_candidate_rows = 0;
    std::uint64_t authority_denial_retention_candidate_bytes = 0;
    std::uint64_t retry_ready_rows = 0;
    std::uint64_t retry_waiting_rows = 0;
    std::uint64_t live_claim_rows = 0;
    std::uint64_t expired_claim_rows = 0;
    std::uint64_t total_attempts = 0;
};

struct SyncPeerTransportIngressRetentionOptions {
    std::string sqlite_path;
    std::string session_id;
    std::string operator_id;
    std::string reason;
    std::uint64_t retention_now_epoch = 1;
    // Zero disables that terminal class. Nonzero means rows at or before the
    // cutoff are eligible. Zero max rows means unlimited for that class.
    std::uint64_t completed_older_than_epoch = 0;
    std::uint64_t abandoned_older_than_epoch = 0;
    std::uint64_t authority_denial_older_than_epoch = 0;
    std::uint64_t max_completed_rows = 0;
    std::uint64_t max_abandoned_rows = 0;
    std::uint64_t max_authority_denial_rows = 0;
    // Retention must decode the same canonical frame shape admitted earlier.
    // These fail-closed limits are explicit so a deployment that raised its
    // ingress limits can raise the destructive verifier limits deliberately.
    std::uint64_t max_frame_bytes = 16 * 1024 * 1024;
    std::uint64_t max_chunk_count = 1024;
    std::uint64_t max_metadata_field_bytes = 64 * 1024;
    bool dry_run = false;
    std::uint64_t sqlite_busy_timeout_ms = kSyncPeerTransportDefaultSqliteBusyTimeoutMs;
};

struct SyncPeerTransportIngressRetentionResult {
    std::string sqlite_path;
    std::string session_id;
    std::string operator_id;
    std::string reason;
    bool dry_run = false;
    bool retention_schema_loaded = false;
    bool retention_completed = false;
    bool retention_noop = false;
    std::uint64_t completed_eligible_rows = 0;
    std::uint64_t completed_eligible_bytes = 0;
    std::uint64_t abandoned_eligible_rows = 0;
    std::uint64_t abandoned_eligible_bytes = 0;
    std::uint64_t authority_denial_eligible_rows = 0;
    std::uint64_t authority_denial_eligible_bytes = 0;
    std::uint64_t ingress_rows_drained = 0;
    std::uint64_t ingress_bytes_drained = 0;
    std::uint64_t completed_rows_drained = 0;
    std::uint64_t completed_bytes_drained = 0;
    std::uint64_t abandoned_rows_drained = 0;
    std::uint64_t abandoned_bytes_drained = 0;
    std::uint64_t authority_denial_rows_drained = 0;
    std::uint64_t authority_denial_bytes_drained = 0;
    std::uint64_t audit_events_written = 0;
    SyncPeerTransportSqliteWriteContentionResult sqlite_write_contention;
};

struct SyncPeerTransportLocalSocketIngressSubmitOptions {
    std::string sqlite_path;
    std::string session_id;
    std::uint64_t submit_now_epoch = 1;
    std::uint64_t max_attempts = 3;
    std::uint64_t retry_backoff_seconds = 30;
    std::uint64_t max_frame_bytes = 16 * 1024 * 1024;
    std::uint64_t max_chunk_count = 1024;
    std::uint64_t max_open_rows = 0;
    std::uint64_t max_open_bytes = 0;
    std::uint64_t max_peer_open_rows = 0;
    std::uint64_t max_peer_open_bytes = 0;
    std::uint64_t max_open_frame_bytes = 0;
    std::uint64_t max_peer_open_frame_bytes = 0;
    bool require_authority_gate = false;
    std::uint64_t sqlite_busy_timeout_ms = kSyncPeerTransportDefaultSqliteBusyTimeoutMs;
};

struct SyncPeerTransportLocalSocketIngressSubmitResult {
    SyncPeerTransportIngressEnqueueResult enqueue;
    std::string sqlite_path;
    std::string session_id;
    std::string transport_envelope_idempotency_key;
    std::string payload_digest;
    // Digest frozen from canonical encoded bytes before socket transmission.
    std::string encoded_frame_digest;
    // Digest derived independently from exact bytes received by the socket.
    std::string socket_frame_digest;
    bool socket_pair_created = false;
    bool frame_sent = false;
    bool frame_received = false;
    bool frame_digest_checked = false;
    bool canonical_frame_checked = false;
    bool wire_envelope_decoded = false;
    bool payload_bytes_received = false;
    bool row_inserted = false;
    bool row_already_present = false;
    SyncPeerTransportAuthorityDecisionResult authority_decision;
    std::uint64_t frame_bytes_written = 0;
    std::uint64_t frame_bytes_read = 0;
    std::uint64_t chunk_count_received = 0;
    std::uint64_t chunk_bytes_received = 0;
};

struct SyncPeerTransportLoopbackIngressSubmitOptions {
    std::string sqlite_path;
    std::string session_id;
    std::uint64_t submit_now_epoch = 1;
    std::uint64_t max_attempts = 3;
    std::uint64_t retry_backoff_seconds = 30;
    std::uint64_t max_frame_bytes = 16 * 1024 * 1024;
    std::uint64_t max_chunk_count = 1024;
    // Small nonzero caps force partial write/read coverage in the harness.
    std::uint64_t max_write_chunk_bytes = 512;
    std::uint64_t max_read_chunk_bytes = 257;
    std::uint64_t max_open_rows = 0;
    std::uint64_t max_open_bytes = 0;
    std::uint64_t max_peer_open_rows = 0;
    std::uint64_t max_peer_open_bytes = 0;
    std::uint64_t max_open_frame_bytes = 0;
    std::uint64_t max_peer_open_frame_bytes = 0;
    bool require_authority_gate = false;
    std::uint64_t sqlite_busy_timeout_ms = kSyncPeerTransportDefaultSqliteBusyTimeoutMs;
};

struct SyncPeerTransportLoopbackIngressSubmitResult {
    SyncPeerTransportIngressEnqueueResult enqueue;
    std::string sqlite_path;
    std::string session_id;
    std::string loopback_address;
    std::string transport_envelope_idempotency_key;
    std::string payload_digest;
    // Digest frozen from canonical encoded bytes before socket transmission.
    std::string encoded_frame_digest;
    // Digest derived independently from exact bytes received by the socket.
    std::string socket_frame_digest;
    bool listener_created = false;
    bool client_socket_created = false;
    bool client_connect_initiated = false;
    bool client_connected = false;
    bool server_accepted = false;
    bool frame_sent = false;
    bool frame_received = false;
    bool frame_digest_checked = false;
    bool canonical_frame_checked = false;
    bool wire_envelope_decoded = false;
    bool payload_bytes_received = false;
    bool row_inserted = false;
    bool row_already_present = false;
    SyncPeerTransportAuthorityDecisionResult authority_decision;
    std::uint64_t loopback_port = 0;
    std::uint64_t frame_bytes_written = 0;
    std::uint64_t frame_bytes_read = 0;
    std::uint64_t write_call_count = 0;
    std::uint64_t read_call_count = 0;
    std::uint64_t partial_write_count = 0;
    std::uint64_t partial_read_count = 0;
    std::uint64_t chunk_count_received = 0;
    std::uint64_t chunk_bytes_received = 0;
};

struct SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions {
    std::string sqlite_path;
    std::string session_id;
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::string worker_id;
    std::string worker_lease_id;
    std::string expected_execution_idempotency_key;
    std::uint64_t binding_now_epoch = 1;
    bool require_live_lease = true;
};

struct SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string expected_execution_idempotency_key;
    NormalizedSyncPath path;
    bool response_envelope_checked = false;
    bool workorder_claims_checked = false;
    bool all_rows_owned_by_worker = false;
    bool all_rows_lease_live = false;
    std::uint64_t binding_now_epoch = 0;
    std::uint64_t response_rows_considered = 0;
    std::uint64_t workorder_rows_bound = 0;
    std::uint64_t live_lease_rows = 0;
    std::uint64_t bytes_bound = 0;
};

struct SyncSessionCheckpointBoundPeerChunkResponseBatchAcceptanceResult {
    SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingResult workorder_binding;
    SyncPeerChunkResponseBatchAcceptanceResult peer_batch_acceptance;
    bool workorder_claim_binding_checked = false;
    bool peer_batch_acceptance_attempted = false;
    bool bytes_accepted_after_binding = false;
};

struct SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string expected_execution_idempotency_key;
    NormalizedSyncPath path;
    bool database_evidence_loaded = false;
    bool sidecar_evidence_verified = false;
    bool transaction_committed = false;
    bool file_result_row_updated = false;
    bool checkpoint_aggregates_updated = false;
    bool staged_file_complete = false;
    bool controlled_abort_before_commit = false;
    std::string controlled_abort_stage;
    std::uint64_t response_rows_considered = 0;
    std::uint64_t live_claimed_rows_verified = 0;
    std::uint64_t completed_rows_verified = 0;
    std::uint64_t sidecar_receipts_verified = 0;
    std::uint64_t staged_chunks_verified = 0;
    std::uint64_t bytes_verified = 0;
    std::uint64_t receipt_rows_inserted = 0;
    std::uint64_t receipt_rows_reactivated_from_committed_cleaned = 0;
    std::uint64_t receipt_rows_already_present = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t workorder_rows_already_completed = 0;
    std::string content_sha256;
};

struct SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions {
    bool abort_after_receipt_row_stage_before_workorder_completion = false;
    bool abort_after_workorder_completion_before_file_result_update = false;
    bool abort_after_file_result_update_before_checkpoint_aggregate = false;
    bool abort_after_checkpoint_aggregate_before_commit = false;
};

struct SyncSessionCheckpointBoundPeerChunkIngestionResult {
    SyncSessionCheckpointBoundPeerChunkResponseBatchAcceptanceResult sidecar_acceptance;
    SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult database_advance;
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string expected_execution_idempotency_key;
    NormalizedSyncPath path;
    bool sidecar_acceptance_attempted = false;
    bool sidecar_acceptance_completed = false;
    bool database_advance_attempted = false;
    bool database_advance_completed = false;
    bool recoverable_sidecar_acceptance_without_db_advance = false;
    bool controlled_stop_after_sidecar_acceptance = false;
    bool transport_safe_single_entrypoint_completed = false;
    std::uint64_t chunks_written = 0;
    std::uint64_t bytes_bound = 0;
    std::uint64_t bytes_verified = 0;
    std::uint64_t receipt_rows_inserted = 0;
    std::uint64_t receipt_rows_reactivated_from_committed_cleaned = 0;
    std::uint64_t receipt_rows_already_present = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t workorder_rows_already_completed = 0;
    std::string content_sha256;
};

struct SyncSessionCheckpointBoundPeerChunkIngestionControlOptions {
    bool stop_after_sidecar_acceptance_before_db_advance = false;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult {
    SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult database_advance;
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string expected_execution_idempotency_key;
    NormalizedSyncPath path;
    bool transport_payload_not_required = false;
    bool sidecar_evidence_verified = false;
    bool database_advance_attempted = false;
    bool database_advance_completed = false;
    bool recovery_entrypoint_completed = false;
    std::uint64_t bytes_verified = 0;
    std::uint64_t receipt_rows_inserted = 0;
    std::uint64_t receipt_rows_reactivated_from_committed_cleaned = 0;
    std::uint64_t receipt_rows_already_present = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t workorder_rows_already_completed = 0;
    std::string content_sha256;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceLimits {
    std::uint64_t max_claimed_paths = 100000;
    std::uint64_t max_claimed_path_bytes = 64ULL * 1024ULL * 1024ULL;
    std::uint64_t max_manifest_chunks = 1000000;
    std::uint64_t max_manifest_lineage_rows = 500000;
    std::uint64_t max_metadata_bytes = 256ULL * 1024ULL * 1024ULL;
    // Cooperative VM execution and lock waiting are independent dimensions.
    // Callers may tighten either, but cannot widen the reviewed generic
    // hostile-SQLite ceilings enforced by the implementation. The lock value
    // is cumulative sqlite3_sleep() request authority, not a hard wall-clock
    // deadline: scheduler delay may make observed sleep larger. Zero is valid
    // and means fail fast on the first lock conflict.
    std::uint64_t max_sqlite_progress_callbacks = 1000000;
    std::uint32_t sqlite_progress_opcode_interval = 1000;
    std::uint64_t max_sqlite_elapsed_milliseconds = 60000;
    std::uint64_t max_sqlite_lock_wait_milliseconds = 60000;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions {
    std::string sqlite_path;
    std::string session_id;
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::string worker_id;
    std::string worker_lease_id;
    std::uint64_t binding_now_epoch = 1;
    bool require_live_lease = true;
    std::uint64_t max_recovery_groups = 0;
    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceLimits
        checkpoint_evidence_limits;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult {
    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult recovery;
    NormalizedSyncPath path;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    bool recovery_attempted = false;
    bool recovery_completed = false;
    bool deferred_by_limit = false;
    bool deferred_by_expired_lease = false;
    bool review_required = false;
    bool review_due_to_missing_sidecar = false;
    bool review_due_to_tampered_sidecar = false;
    bool review_due_to_staged_bytes_mismatch = false;
    std::string failure_reason;
    std::string review_reason;
    std::string review_event_idempotency_key;
    bool review_event_persisted = false;
    bool review_event_already_present = false;
    std::uint64_t chunks_considered = 0;
    std::uint64_t bytes_considered = 0;
    std::uint64_t bytes_verified = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t workorder_rows_already_completed = 0;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    NormalizedSyncPath path;
    bool sweep_query_loaded = false;
    bool transport_payload_not_required = false;
    bool recovery_attempted = false;
    bool sweep_completed = false;
    std::uint64_t binding_now_epoch = 0;
    std::uint64_t claimed_rows_considered = 0;
    std::uint64_t bytes_considered = 0;
    std::uint64_t recovery_groups_considered = 0;
    std::uint64_t recovery_groups_attempted = 0;
    std::uint64_t recovery_groups_completed = 0;
    std::uint64_t recovery_groups_failed = 0;
    std::uint64_t recovery_groups_deferred_by_limit = 0;
    std::uint64_t recovery_groups_deferred_expired_lease = 0;
    std::uint64_t recovery_groups_review_required = 0;
    std::uint64_t recovery_groups_review_missing_sidecar = 0;
    std::uint64_t recovery_groups_review_tampered_sidecar = 0;
    std::uint64_t recovery_groups_review_staged_bytes_mismatch = 0;
    std::uint64_t claimed_rows_deferred_expired_lease = 0;
    std::uint64_t claimed_rows_review_required = 0;
    std::uint64_t bytes_deferred_expired_lease = 0;
    std::uint64_t bytes_review_required = 0;
    std::uint64_t review_events_written = 0;
    std::uint64_t review_events_already_present = 0;
    bool sweep_incomplete_due_to_limit = false;
    bool sweep_incomplete_due_to_expired_lease = false;
    bool sweep_incomplete_due_to_review = false;
    bool sweep_incomplete_due_to_missing_apply_input = false;
    bool sweep_incomplete_due_to_missing_remote_file_evidence = false;
    bool sweep_incomplete_due_to_ambiguous_apply_input = false;
    bool sweep_incomplete_due_to_ambiguous_remote_file_evidence = false;
    bool sweep_incomplete_due_to_remote_apply_evidence_mismatch = false;
    std::uint64_t bytes_verified = 0;
    std::uint64_t receipt_rows_inserted = 0;
    std::uint64_t receipt_rows_reactivated_from_committed_cleaned = 0;
    std::uint64_t receipt_rows_already_present = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t workorder_rows_already_completed = 0;
    std::vector<SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult> groups;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepFileResult {
    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult file_sweep;
    NormalizedSyncPath path;
    bool file_input_considered = false;
    bool file_sweep_attempted = false;
    bool file_sweep_completed = false;
    bool skipped_non_fetch_stage = false;
    bool missing_remote_file_evidence = false;
    bool missing_apply_input = false;
    bool ambiguous_apply_input = false;
    bool ambiguous_remote_file_evidence = false;
    bool remote_apply_evidence_mismatch = false;
    bool deferred_by_group_limit = false;
    bool review_required = false;
    std::uint64_t review_events_written = 0;
    std::uint64_t review_events_already_present = 0;
    std::string failure_reason;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    bool transport_payload_not_required = false;
    bool session_sweep_attempted = false;
    bool session_sweep_completed = false;
    std::uint64_t binding_now_epoch = 0;
    std::uint64_t file_inputs_considered = 0;
    std::uint64_t files_skipped_non_fetch_stage = 0;
    std::uint64_t files_missing_remote_file_evidence = 0;
    std::uint64_t files_ambiguous_apply_input = 0;
    std::uint64_t files_ambiguous_remote_file_evidence = 0;
    std::uint64_t files_remote_apply_evidence_mismatch = 0;
    std::uint64_t claimed_workorder_paths_considered = 0;
    bool sqlite_lock_contention_observed = false;
    std::uint64_t sqlite_lock_wait_invocations = 0;
    std::uint64_t sqlite_lock_wait_authorized_sleep_milliseconds = 0;
    std::uint64_t sqlite_lock_wait_observed_sleep_milliseconds = 0;
    std::uint64_t claimed_workorder_paths_missing_apply_input = 0;
    std::uint64_t files_attempted = 0;
    std::uint64_t files_completed = 0;
    std::uint64_t files_failed = 0;
    std::uint64_t files_deferred_by_group_limit = 0;
    std::uint64_t files_review_required = 0;
    std::uint64_t claimed_rows_considered = 0;
    std::uint64_t bytes_considered = 0;
    std::uint64_t recovery_groups_considered = 0;
    std::uint64_t recovery_groups_attempted = 0;
    std::uint64_t recovery_groups_completed = 0;
    std::uint64_t recovery_groups_failed = 0;
    std::uint64_t recovery_groups_deferred_by_limit = 0;
    std::uint64_t recovery_groups_deferred_expired_lease = 0;
    std::uint64_t recovery_groups_review_required = 0;
    std::uint64_t recovery_groups_review_missing_sidecar = 0;
    std::uint64_t recovery_groups_review_tampered_sidecar = 0;
    std::uint64_t recovery_groups_review_staged_bytes_mismatch = 0;
    std::uint64_t claimed_rows_deferred_expired_lease = 0;
    std::uint64_t claimed_rows_review_required = 0;
    std::uint64_t bytes_review_required = 0;
    std::uint64_t review_events_written = 0;
    std::uint64_t review_events_already_present = 0;
    std::uint64_t bytes_verified = 0;
    std::uint64_t receipt_rows_inserted = 0;
    std::uint64_t receipt_rows_reactivated_from_committed_cleaned = 0;
    std::uint64_t receipt_rows_already_present = 0;
    std::uint64_t workorder_rows_completed = 0;
    std::uint64_t workorder_rows_already_completed = 0;
    bool sweep_incomplete_due_to_limit = false;
    bool sweep_incomplete_due_to_expired_lease = false;
    bool sweep_incomplete_due_to_review = false;
    bool sweep_incomplete_due_to_missing_apply_input = false;
    bool sweep_incomplete_due_to_missing_remote_file_evidence = false;
    bool sweep_incomplete_due_to_ambiguous_apply_input = false;
    bool sweep_incomplete_due_to_ambiguous_remote_file_evidence = false;
    bool sweep_incomplete_due_to_remote_apply_evidence_mismatch = false;
    std::vector<SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepFileResult> files;
};

struct SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::string checkpoint_schema_version;
    bool checkpoint_evidence_loaded = false;
    bool transport_payload_not_required = false;
    bool checkpoint_schema_supported = false;
    bool checkpoint_schema_has_manifest_chunks = false;
    bool checkpoint_schema_has_manifest_lineage = false;
    bool archived_checkpoint_migration_backfill_checked = false;
    bool archived_checkpoint_exact_startup_hydration_supported = false;
    bool archived_checkpoint_migration_backfill_required = false;
    bool archived_checkpoint_migration_backfill_blocked_missing_lineage = false;
    std::string archived_checkpoint_migration_backfill_reason;
    bool main_read_snapshot_established = false;
    std::uint64_t database_owner_generation = 0;
    bool sqlite_lock_contention_observed = false;
    std::uint64_t sqlite_lock_wait_invocations = 0;
    std::uint64_t sqlite_lock_wait_authorized_sleep_milliseconds = 0;
    std::uint64_t sqlite_lock_wait_observed_sleep_milliseconds = 0;
    std::uint64_t claimed_workorder_paths_considered = 0;
    std::uint64_t claimed_workorder_path_bytes = 0;
    std::uint64_t evidence_metadata_bytes = 0;
    std::uint64_t apply_entries_loaded = 0;
    std::uint64_t remote_file_entries_loaded = 0;
    std::uint64_t manifest_chunks_loaded = 0;
    std::uint64_t manifest_lineage_rows_loaded = 0;
    std::uint64_t remote_file_entries_missing_lineage_rows = 0;
    std::uint64_t archived_checkpoint_claimed_paths_blocked_by_missing_lineage = 0;
    std::uint64_t remote_apply_evidence_mismatch_paths = 0;
    bool checkpoint_evidence_mismatch_detected = false;
    std::vector<SyncManifestEntry> remote_file_entries;
    std::vector<SyncLocalApplyPlanEntry> apply_entries;
};

struct SyncSessionCheckpointBoundPeerSidecarReviewEventRecord {
    NormalizedSyncPath path;
    std::string review_event_idempotency_key;
    std::string review_category;
    std::string review_reason;
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;
    std::string worker_id;
    std::string worker_lease_id;
    std::uint64_t chunks_considered = 0;
    std::uint64_t bytes_considered = 0;
    std::uint64_t first_observed_at_epoch = 0;
    std::uint64_t last_observed_at_epoch = 0;
    std::uint64_t observations = 0;
    std::string resolution_state;
    std::string resolution_reason;
    std::string resolved_by_operator_id;
    std::uint64_t resolved_at_epoch = 0;
    std::uint64_t resolved_workorder_rows_quarantined = 0;
    std::uint64_t resolved_workorder_rows_already_quarantined = 0;
};

struct SyncSessionCheckpointBoundPeerSidecarReviewEventReportOptions {
    std::string sqlite_path;
    std::string session_id;
    NormalizedSyncPath path;
    std::string review_category;
    std::uint64_t max_events = 0;
};

struct SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult {
    std::string sqlite_path;
    std::string session_id;
    bool review_event_schema_loaded = false;
    bool review_event_resolution_schema_loaded = false;
    bool report_completed = false;
    std::uint64_t max_events = 0;
    bool events_deferred_by_limit = false;
    std::uint64_t events_returned = 0;
    std::uint64_t total_observations = 0;
    std::uint64_t missing_sidecar_events = 0;
    std::uint64_t tampered_sidecar_events = 0;
    std::uint64_t staged_bytes_mismatch_events = 0;
    std::uint64_t unresolved_events = 0;
    std::uint64_t quarantined_events = 0;
    std::vector<SyncSessionCheckpointBoundPeerSidecarReviewEventRecord> events;
};

struct SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineOptions {
    std::string sqlite_path;
    std::string session_id;
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    NormalizedSyncPath path;
    std::string review_event_idempotency_key;
    std::string decision_operator_id;
    std::string decision_reason = "sidecar-review-quarantined-by-operator";
    std::uint64_t quarantine_at_epoch = 0;
};

struct SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineResult {
    std::string sqlite_path;
    std::string session_id;
    NormalizedSyncPath path;
    std::string review_event_idempotency_key;
    std::string review_category;
    std::string decision_operator_id;
    std::string decision_reason;
    bool review_event_schema_loaded = false;
    bool resolution_schema_loaded = false;
    bool review_event_found = false;
    bool transaction_committed = false;
    bool quarantine_event_written = false;
    bool quarantine_event_already_present = false;
    std::uint64_t quarantine_at_epoch = 0;
    std::uint64_t chunks_considered = 0;
    std::uint64_t bytes_considered = 0;
    std::uint64_t workorder_rows_matched = 0;
    std::uint64_t workorder_rows_quarantined = 0;
    std::uint64_t workorder_rows_already_quarantined = 0;
};

struct SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions {
    std::string sqlite_path;
    std::string session_id;
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::string staging_root_path;
    NormalizedSyncPath path;
    std::string review_event_idempotency_key;
    std::string decision_operator_id;
    std::string decision_reason = "sidecar-review-repaired-reset-by-operator";
    std::uint64_t repair_at_epoch = 0;
    std::string repair_worker_id;
    std::uint64_t repair_worker_lease_epoch = 1;
    std::uint64_t repair_worker_lease_seconds = 1;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    bool reset_claimed_workorders = true;
    bool reset_quarantined_workorders = true;
};

struct SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult {
    std::string sqlite_path;
    std::string session_id;
    std::string staging_root_path;
    NormalizedSyncPath path;
    std::string review_event_idempotency_key;
    std::string review_category;
    std::string decision_operator_id;
    std::string decision_reason;
    std::string repair_worker_id;
    std::string repair_worker_lease_id;
    std::string sidecar_disposition;
    std::string staged_bytes_disposition;
    bool review_event_schema_loaded = false;
    bool repair_reset_schema_loaded = false;
    bool review_event_found = false;
    bool transaction_committed = false;
    bool repair_reset_event_written = false;
    bool repair_reset_event_already_present = false;
    bool staged_file_checked = false;
    bool staged_file_left_in_place = false;
    std::uint64_t repair_at_epoch = 0;
    std::uint64_t repair_worker_lease_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
    std::uint64_t retry_at_epoch = 0;
    std::uint64_t chunks_considered = 0;
    std::uint64_t bytes_considered = 0;
    std::uint64_t workorder_rows_matched = 0;
    std::uint64_t workorder_rows_reset = 0;
    std::uint64_t workorder_rows_already_reset = 0;
    std::uint64_t claimed_rows_reset = 0;
    std::uint64_t quarantined_rows_reset = 0;
    std::uint64_t receipt_paths_considered = 0;
    std::uint64_t receipts_removed = 0;
    std::uint64_t receipts_already_missing = 0;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::uint64_t owner_fence_now_epoch = 1;
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
    std::string sqlite_runtime_version;
    std::string sqlite_runtime_source_id;
    std::string sqlite_journal_mode;
    bool sqlite_runtime_bundled = false;
    bool sqlite_wal_reset_fix_known = false;
    bool sqlite_rollback_journal_fallback_active = false;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::uint64_t owner_fence_now_epoch = 1;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::uint64_t owner_fence_now_epoch = 1;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::uint64_t owner_fence_now_epoch = 1;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
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
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
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
    bool block_mutating_actions_on_terminal_review = true;
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
    bool terminal_review_present = false;
    bool mutations_blocked_by_terminal_review = false;
    std::uint64_t terminal_review_actions_observed = 0;
    std::uint64_t mutating_action_groups_blocked_by_terminal_review = 0;
    std::uint64_t mutating_actions_blocked_by_terminal_review = 0;
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

struct SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions {
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
    std::string daemon_id;
    std::uint64_t initial_worker_lease_epoch = 1;
    std::uint64_t initial_scheduler_now_epoch = 1;
    std::uint64_t worker_lease_seconds = 60;
    std::uint64_t loop_tick_seconds = 1;
    std::uint64_t workorder_retry_backoff_seconds = 0;
    bool allow_expired_workorder_reclaim = true;
    std::uint64_t max_workorder_claim_attempts = 0;
    std::uint64_t max_scheduler_actions_per_pass = 0;
    std::uint64_t max_loop_passes = 1;
    bool execute_owned_claim_actions = true;
    bool claim_or_reclaim_expired_actions = true;
    bool abandon_expired_actions = true;
    bool include_completed_workorders = false;
    bool stop_after_idle_pass = true;
    bool stop_on_deferred_actions = true;
    bool stop_on_terminal_review = true;
    bool recover_bound_peer_sidecars_before_scheduling = false;
    bool stop_before_scheduling_on_sidecar_recovery_incomplete = true;
    bool hydrate_startup_sidecar_evidence_from_checkpoint = true;
    bool require_daemon_owner_lock = true;
    std::string daemon_heartbeat_path;
    std::uint64_t daemon_heartbeat_stale_after_seconds = 0;
    std::uint64_t startup_sidecar_recovery_max_groups = 0;
    std::vector<SyncManifestEntry> startup_sidecar_remote_file_entries;
    std::vector<SyncLocalApplyPlanEntry> startup_sidecar_apply_entries;
    std::uint64_t max_chunks_per_request = 0;
    std::uint64_t max_bytes_per_request = 0;
    std::uint64_t max_chunks_per_peer_round = 0;
    std::uint64_t max_bytes_per_peer_round = 0;
};

struct SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult {
    std::string sqlite_path;
    std::string session_id;
    std::string worker_id;
    std::string daemon_id;
    std::string worker_lease_id;
    std::string service_instance_id;
    std::uint64_t service_restart_epoch = 0;
    bool service_lifecycle_preflight_checked = false;
    bool service_lifecycle_preflight_passed = false;
    bool service_lifecycle_live_owner_blocked = false;
    bool service_lifecycle_heartbeat_checked = false;
    bool service_lifecycle_heartbeat_existing_loaded = false;
    bool service_lifecycle_heartbeat_existing_final = false;
    bool service_lifecycle_heartbeat_existing_fresh = false;
    bool service_lifecycle_heartbeat_existing_stale = false;
    bool service_lifecycle_reentry_from_stale_heartbeat = false;
    bool service_lifecycle_existing_heartbeat_process_identity_checked = false;
    bool service_lifecycle_existing_heartbeat_process_live = false;
    bool service_lifecycle_existing_heartbeat_process_identity_matches = false;
    std::string service_lifecycle_existing_heartbeat_process_identity_match_kind;
    std::string service_lifecycle_preflight_reason;
    std::string service_lifecycle_existing_heartbeat_state;
    std::string service_lifecycle_existing_heartbeat_daemon_id;
    std::string service_lifecycle_existing_heartbeat_owner_lock_id;
    std::uint64_t service_lifecycle_existing_heartbeat_epoch = 0;
    std::uint64_t service_lifecycle_existing_heartbeat_stale_at_epoch = 0;
    bool daemon_loop_completed = false;
    bool stopped_after_idle_pass = false;
    bool stopped_on_deferred_actions = false;
    bool stopped_on_terminal_review = false;
    bool stopped_before_scheduling_on_sidecar_recovery = false;
    bool max_loop_passes_reached = false;
    bool durable_integrity_verified = false;
    bool source_filesystem_verified = false;
    bool startup_sidecar_recovery_attempted = false;
    bool startup_sidecar_recovery_completed = false;
    bool startup_sidecar_recovery_blocked_scheduling = false;
    bool startup_sidecar_recovery_incomplete_due_to_limit = false;
    bool startup_sidecar_recovery_incomplete_due_to_expired_lease = false;
    bool startup_sidecar_recovery_incomplete_due_to_review = false;
    bool startup_sidecar_recovery_incomplete_due_to_missing_apply_input = false;
    bool startup_sidecar_recovery_incomplete_due_to_missing_remote_file_evidence = false;
    bool startup_sidecar_recovery_incomplete_due_to_ambiguous_apply_input = false;
    bool startup_sidecar_recovery_incomplete_due_to_ambiguous_remote_file_evidence = false;
    bool startup_sidecar_recovery_incomplete_due_to_remote_apply_evidence_mismatch = false;
    bool startup_sidecar_recovery_checkpoint_evidence_hydrated = false;
    std::string startup_sidecar_recovery_checkpoint_schema_version;
    bool startup_sidecar_recovery_checkpoint_schema_supported = false;
    bool startup_sidecar_recovery_checkpoint_schema_has_manifest_chunks = false;
    bool startup_sidecar_recovery_checkpoint_schema_has_manifest_lineage = false;
    bool startup_sidecar_recovery_archived_checkpoint_migration_backfill_checked = false;
    bool startup_sidecar_recovery_archived_checkpoint_exact_startup_hydration_supported = false;
    bool startup_sidecar_recovery_archived_checkpoint_migration_backfill_required = false;
    bool startup_sidecar_recovery_archived_checkpoint_migration_backfill_blocked_missing_lineage = false;
    std::string startup_sidecar_recovery_archived_checkpoint_migration_backfill_reason;
    std::uint64_t startup_sidecar_recovery_checkpoint_apply_entries_loaded = 0;
    std::uint64_t startup_sidecar_recovery_checkpoint_remote_file_entries_loaded = 0;
    std::uint64_t startup_sidecar_recovery_checkpoint_manifest_chunks_loaded = 0;
    std::uint64_t startup_sidecar_recovery_checkpoint_manifest_lineage_rows_loaded = 0;
    std::uint64_t startup_sidecar_recovery_checkpoint_remote_file_entries_missing_lineage_rows = 0;
    std::uint64_t startup_sidecar_recovery_archived_checkpoint_claimed_paths_blocked_by_missing_lineage = 0;
    std::uint64_t startup_sidecar_recovery_checkpoint_remote_apply_evidence_mismatch_paths = 0;
    std::uint64_t startup_sidecar_recovery_missing_apply_input_paths = 0;
    std::uint64_t startup_sidecar_recovery_missing_remote_file_evidence_files = 0;
    std::uint64_t startup_sidecar_recovery_ambiguous_apply_input_files = 0;
    std::uint64_t startup_sidecar_recovery_ambiguous_remote_file_evidence_files = 0;
    std::uint64_t startup_sidecar_recovery_remote_apply_evidence_mismatch_files = 0;
    std::uint64_t startup_sidecar_recovery_groups_completed = 0;
    std::uint64_t startup_sidecar_recovery_groups_review_required = 0;
    std::uint64_t startup_sidecar_review_events_written = 0;
    std::uint64_t startup_sidecar_review_events_already_present = 0;
    std::uint64_t daemon_lease_events_written = 0;
    std::uint64_t daemon_lease_events_already_present = 0;
    std::uint64_t startup_sidecar_recovery_worker_lease_epoch = 0;
    std::string startup_sidecar_recovery_worker_lease_id;
    std::uint64_t final_worker_lease_epoch = 0;
    std::string final_worker_lease_id;
    std::uint64_t initial_worker_lease_epoch = 0;
    std::uint64_t initial_scheduler_now_epoch = 0;
    std::uint64_t next_worker_lease_epoch = 0;
    std::uint64_t next_scheduler_now_epoch = 0;
    std::uint64_t worker_lease_seconds = 0;
    std::uint64_t loop_tick_seconds = 0;
    bool daemon_owner_lock_required = false;
    bool daemon_owner_lock_acquired = false;
    bool daemon_owner_lock_released = false;
    bool daemon_owner_lock_reclaimed_expired = false;
    std::string daemon_owner_lock_id;
    std::uint64_t daemon_owner_lock_epoch = 0;
    std::uint64_t daemon_owner_lock_acquired_at_epoch = 0;
    std::uint64_t daemon_owner_lock_expires_at_epoch = 0;
    std::uint64_t daemon_owner_lock_released_at_epoch = 0;
    bool daemon_heartbeat_requested = false;
    bool daemon_heartbeat_written = false;
    bool daemon_heartbeat_final = false;
    std::uint64_t daemon_heartbeat_writes = 0;
    std::string daemon_heartbeat_path;
    std::string daemon_heartbeat_state;
    std::uint64_t daemon_heartbeat_epoch = 0;
    std::uint64_t daemon_heartbeat_stale_after_seconds = 0;
    std::uint64_t daemon_heartbeat_stale_at_epoch = 0;
    std::uint64_t daemon_heartbeat_process_id = 0;
    std::string daemon_heartbeat_process_identity_format;
    std::string daemon_heartbeat_process_boot_id;
    std::string daemon_heartbeat_process_start_token;
    std::uint64_t terminal_apply_workorders_checked = 0;
    std::uint64_t terminal_apply_workorders_inserted = 0;
    std::uint64_t terminal_apply_workorders_completed = 0;
    std::uint64_t terminal_apply_workorders_already_completed = 0;
    std::uint64_t terminal_apply_tombstone_workorders_completed = 0;
    std::uint64_t terminal_apply_tombstone_targets_removed = 0;
    std::uint64_t terminal_apply_tombstone_targets_already_absent = 0;
    std::uint64_t terminal_apply_conflict_tombstone_workorders_completed = 0;
    std::uint64_t terminal_apply_conflict_file_workorders_completed = 0;
    std::uint64_t terminal_apply_conflict_copies_preserved = 0;
    std::uint64_t terminal_apply_conflict_copies_reused = 0;
    std::uint64_t terminal_apply_conflict_remote_tombstones_applied = 0;
    std::uint64_t terminal_apply_conflict_remote_files_materialized = 0;
    std::uint64_t max_scheduler_actions_per_pass = 0;
    std::uint64_t max_loop_passes = 0;
    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult startup_sidecar_recovery;
    std::uint64_t passes_attempted = 0;
    std::uint64_t passes_completed = 0;
    std::uint64_t mutating_passes = 0;
    std::uint64_t idle_passes = 0;
    std::uint64_t terminal_review_actions_observed = 0;
    bool mutations_blocked_by_terminal_review = false;
    std::uint64_t mutating_action_groups_blocked_by_terminal_review = 0;
    std::uint64_t mutating_actions_blocked_by_terminal_review = 0;
    std::uint64_t scheduler_actions_returned = 0;
    std::uint64_t mutating_actions_planned = 0;
    std::uint64_t scheduler_action_groups_deferred_by_limit = 0;
    std::uint64_t scheduler_actions_deferred_by_limit = 0;
    std::uint64_t mutating_action_groups_selected = 0;
    std::uint64_t execute_owned_claim_groups_selected = 0;
    std::uint64_t claim_or_reclaim_expired_groups_selected = 0;
    std::uint64_t abandon_expired_groups_selected = 0;
    std::uint64_t execute_owned_claim_actions_selected = 0;
    std::uint64_t claim_or_reclaim_expired_actions_selected = 0;
    std::uint64_t abandon_expired_actions_selected = 0;
    std::uint64_t nonmutating_actions_observed = 0;
    std::uint64_t execution_key_filters_built = 0;
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
    std::vector<SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult> pass_results;
};


struct SyncSessionCheckpointOperatorStatusOptions {
    std::string sqlite_path;
    std::string session_id;
    std::uint64_t scheduler_now_epoch = 0;
    std::string daemon_heartbeat_path;
};

struct SyncSessionCheckpointOperatorStatusResult {
    std::string sqlite_path;
    std::string session_id;
    bool status_loaded = false;
    bool query_only_enabled = false;
    bool scheduler_clock_provided = false;
    std::uint64_t scheduler_now_epoch = 0;
    std::string schema_version;
    bool schema_version_supported = false;

    std::uint64_t sidecar_review_events = 0;
    std::uint64_t sidecar_review_observations = 0;
    std::uint64_t missing_sidecar_review_events = 0;
    std::uint64_t tampered_sidecar_review_events = 0;
    std::uint64_t staged_bytes_mismatch_review_events = 0;
    std::uint64_t sidecar_review_repair_reset_events = 0;
    std::uint64_t pending_sidecar_review_events = 0;
    std::uint64_t repair_reset_workorder_rows_matched = 0;
    std::uint64_t repair_reset_workorder_rows_reset = 0;
    std::uint64_t repair_reset_receipts_removed = 0;
    std::uint64_t repair_reset_receipts_already_missing = 0;

    std::uint64_t workorder_rows = 0;
    std::uint64_t claimed_workorder_rows = 0;
    std::uint64_t completed_workorder_rows = 0;
    std::uint64_t abandoned_workorder_rows = 0;
    std::uint64_t quarantined_workorder_rows = 0;
    std::uint64_t resume_transfer_workorder_rows = 0;
    std::uint64_t retry_transfer_workorder_rows = 0;
    std::uint64_t live_claimed_workorder_rows = 0;
    std::uint64_t expired_claimed_workorder_rows = 0;
    std::uint64_t retryable_expired_workorder_rows = 0;
    std::uint64_t cooling_down_expired_workorder_rows = 0;
    std::uint64_t workorder_reclaim_events = 0;
    std::uint64_t workorder_abandon_events = 0;
    std::uint64_t workorder_quarantine_events = 0;
    std::uint64_t workorder_reset_events = 0;

    std::uint64_t terminal_apply_tombstone_intent_rows = 0;
    std::uint64_t pending_terminal_apply_tombstone_intent_rows = 0;
    std::uint64_t terminal_apply_conflict_tombstone_intent_rows = 0;
    std::uint64_t pending_terminal_apply_conflict_tombstone_intent_rows = 0;
    std::uint64_t terminal_apply_conflict_file_intent_rows = 0;
    std::uint64_t pending_terminal_apply_conflict_file_intent_rows = 0;
    std::uint64_t terminal_apply_workorder_rows = 0;
    std::uint64_t pending_terminal_apply_workorder_rows = 0;
    std::uint64_t completed_terminal_apply_workorder_rows = 0;
    std::uint64_t tombstone_terminal_apply_workorder_rows = 0;
    std::uint64_t tombstone_terminal_apply_completed_rows = 0;
    std::uint64_t tombstone_terminal_apply_targets_removed = 0;
    std::uint64_t tombstone_terminal_apply_targets_already_absent = 0;
    std::uint64_t conflict_terminal_apply_workorder_rows = 0;
    std::uint64_t conflict_terminal_apply_completed_rows = 0;
    std::uint64_t conflict_terminal_apply_targets_removed = 0;
    std::uint64_t conflict_file_terminal_apply_workorder_rows = 0;
    std::uint64_t conflict_file_terminal_apply_completed_rows = 0;
    std::uint64_t conflict_file_terminal_apply_targets_materialized = 0;

    bool peer_transport_ingress_table_present = false;
    std::uint64_t peer_transport_ingress_total_rows = 0;
    std::uint64_t peer_transport_ingress_open_rows = 0;
    std::uint64_t peer_transport_ingress_open_bytes = 0;
    std::uint64_t peer_transport_ingress_queued_rows = 0;
    std::uint64_t peer_transport_ingress_queued_bytes = 0;
    std::uint64_t peer_transport_ingress_claimed_rows = 0;
    std::uint64_t peer_transport_ingress_claimed_bytes = 0;
    std::uint64_t peer_transport_ingress_completed_rows = 0;
    std::uint64_t peer_transport_ingress_completed_bytes = 0;
    std::uint64_t peer_transport_ingress_failed_rows = 0;
    std::uint64_t peer_transport_ingress_failed_bytes = 0;
    std::uint64_t peer_transport_ingress_abandoned_rows = 0;
    std::uint64_t peer_transport_ingress_abandoned_bytes = 0;
    bool peer_transport_ingress_retention_event_table_present = false;
    std::uint64_t peer_transport_ingress_retention_event_rows = 0;
    std::uint64_t peer_transport_ingress_retention_drained_rows = 0;
    std::uint64_t peer_transport_ingress_retention_drained_bytes = 0;
    std::uint64_t peer_transport_ingress_terminal_retention_candidate_rows = 0;
    std::uint64_t peer_transport_ingress_terminal_retention_candidate_bytes = 0;
    bool peer_transport_authority_denial_table_present = false;
    std::uint64_t peer_transport_authority_denied_rows = 0;
    std::uint64_t peer_transport_authority_denied_bytes = 0;
    std::uint64_t peer_transport_authority_superseded_expired_denied_rows = 0;
    std::uint64_t peer_transport_authority_superseded_expired_denied_bytes = 0;
    bool peer_transport_authority_supersession_table_present = false;
    std::uint64_t peer_transport_authority_supersession_rows = 0;
    std::uint64_t peer_transport_authority_denial_retention_candidate_rows = 0;
    std::uint64_t peer_transport_authority_denial_retention_candidate_bytes = 0;
    std::uint64_t peer_transport_ingress_retry_ready_rows = 0;
    std::uint64_t peer_transport_ingress_retry_waiting_rows = 0;
    std::uint64_t peer_transport_ingress_live_claim_rows = 0;
    std::uint64_t peer_transport_ingress_expired_claim_rows = 0;
    std::uint64_t peer_transport_ingress_total_attempts = 0;
    std::string peer_transport_ingress_next_action;

    std::uint64_t daemon_lease_events = 0;
    std::uint64_t live_daemon_lease_events = 0;
    std::uint64_t expired_daemon_lease_events = 0;
    std::uint64_t daemon_owner_lock_rows = 0;
    bool daemon_owner_lock_held = false;
    bool daemon_owner_lock_live = false;
    std::string daemon_owner_lock_daemon_id;
    std::string daemon_owner_lock_worker_id;
    std::string daemon_owner_lock_id;
    std::uint64_t daemon_owner_lock_epoch = 0;
    std::uint64_t daemon_owner_lock_acquired_at_epoch = 0;
    std::uint64_t daemon_owner_lock_expires_at_epoch = 0;
    std::uint64_t daemon_owner_lock_released_at_epoch = 0;
    std::string latest_daemon_id;
    std::string latest_daemon_worker_id;
    std::string latest_daemon_worker_lease_id;
    std::uint64_t latest_daemon_worker_lease_epoch = 0;
    std::uint64_t latest_daemon_lease_started_at_epoch = 0;
    std::uint64_t latest_daemon_lease_expires_at_epoch = 0;
    std::string latest_daemon_lease_reason;
    bool latest_daemon_lease_live = false;

    bool daemon_heartbeat_requested = false;
    bool daemon_heartbeat_path_exists = false;
    bool daemon_heartbeat_path_is_regular_file = false;
    bool daemon_heartbeat_loaded = false;
    bool daemon_heartbeat_format_ok = false;
    bool daemon_heartbeat_session_matches = false;
    bool daemon_heartbeat_checkpoint_matches = false;
    bool daemon_heartbeat_owner_lock_matches = false;
    bool daemon_heartbeat_process_identity_present = false;
    bool daemon_heartbeat_process_identity_checked = false;
    bool daemon_heartbeat_process_identity_verification_available = false;
    bool daemon_heartbeat_process_live = false;
    bool daemon_heartbeat_process_identity_matches = false;
    bool daemon_heartbeat_stale = false;
    bool daemon_heartbeat_attention_required = false;
    bool daemon_heartbeat_final = false;
    std::string daemon_heartbeat_path;
    std::string daemon_heartbeat_error;
    std::string daemon_heartbeat_format;
    std::string daemon_heartbeat_state;
    std::string daemon_heartbeat_reason;
    std::string daemon_heartbeat_checkpoint_path;
    std::string daemon_heartbeat_session_id;
    std::string daemon_heartbeat_daemon_id;
    std::string daemon_heartbeat_worker_id;
    std::string daemon_heartbeat_owner_lock_id;
    std::string daemon_heartbeat_process_identity_format;
    std::string daemon_heartbeat_process_boot_id;
    std::string daemon_heartbeat_process_start_token;
    std::string daemon_heartbeat_process_identity_match_kind;
    std::uint64_t daemon_heartbeat_epoch = 0;
    std::uint64_t daemon_heartbeat_stale_after_seconds = 0;
    std::uint64_t daemon_heartbeat_stale_at_epoch = 0;
    std::uint64_t daemon_heartbeat_process_id = 0;
    std::uint64_t daemon_heartbeat_owner_lock_epoch = 0;

    bool operator_attention_required = false;
    bool safe_to_schedule = false;
    std::string suggested_next_action;
};

struct SyncSessionCheckpointResumeCycleOptions {
    std::string sqlite_path;
    std::string session_id;
    SyncSessionCheckpointDaemonOwnerCapability daemon_owner_capability;
    std::uint64_t owner_fence_now_epoch = 1;
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
SyncValidationResult build_sync_peer_transport_bound_chunk_response_batch_envelope(
    const SyncPeerTransportEnvelopeBuildOptions& transport_options,
    const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
    SyncPeerTransportBoundChunkResponseBatchEnvelope& out);
SyncValidationResult encode_sync_peer_transport_canonical_payload(
    const SyncPeerTransportCanonicalCodecLimits& limits,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    std::string& out_wire_bytes);
SyncValidationResult decode_sync_peer_transport_canonical_payload(
    const SyncPeerTransportCanonicalCodecLimits& limits,
    const std::string& wire_bytes,
    SyncPeerTransportCanonicalPayload& out);
SyncValidationResult accept_sync_peer_transport_bound_chunk_response_batch_envelope(
    const SyncPeerTransportEnvelopeVerifyOptions& transport_options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncStagedTransferInspectionResult& inspection,
    const SyncChunkRequestPlanOptions& request_options,
    const SyncChunkRequestPlanResult& request_plan,
    const SyncPeerChunkScheduleResult& peer_schedule,
    const SyncPeerChunkAssignment& peer_assignment,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncPeerTransportBoundChunkResponseBatchAcceptanceResult& out);
SyncValidationResult record_sync_peer_transport_authority(
    const SyncPeerTransportAuthorityRecordOptions& options,
    SyncPeerTransportAuthorityRecordResult& out);

SyncValidationResult record_sync_peer_transport_authority_supersession(
    const SyncPeerTransportAuthoritySupersessionRecordOptions& options,
    SyncPeerTransportAuthoritySupersessionRecordResult& out);

SyncValidationResult evaluate_sync_peer_transport_authority(
    const SyncPeerTransportAuthorityDecisionOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportAuthorityDecisionResult& out);

SyncValidationResult enqueue_sync_peer_transport_ingress_envelope(
    const SyncPeerTransportIngressEnqueueOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportIngressEnqueueResult& out);
SyncValidationResult load_sync_peer_transport_ingress_payload(
    const SyncPeerTransportIngressPayloadLoadOptions& options,
    SyncPeerTransportIngressPayloadLoadResult& out);
SyncValidationResult process_sync_peer_transport_ingress_envelope(
    const SyncPeerTransportIngressProcessOptions& options,
    const SyncPeerTransportEnvelopeVerifyOptions& transport_options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncStagedTransferInspectionResult& inspection,
    const SyncChunkRequestPlanOptions& request_options,
    const SyncChunkRequestPlanResult& request_plan,
    const SyncPeerChunkScheduleResult& peer_schedule,
    const SyncPeerChunkAssignment& peer_assignment,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncPeerTransportIngressProcessResult& out);
// Worker-facing restart boundary. The transport envelope and chunk bytes are
// reconstructed from the durable canonical frame by key; callers do not need
// to retain or resupply sender-owned ingress objects after enqueue.
SyncValidationResult process_sync_peer_transport_ingress_durable_payload(
    const SyncPeerTransportIngressProcessOptions& options,
    const SyncPeerTransportEnvelopeVerifyOptions& transport_options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncStagedTransferInspectionResult& inspection,
    const SyncChunkRequestPlanOptions& request_options,
    const SyncChunkRequestPlanResult& request_plan,
    const SyncPeerChunkScheduleResult& peer_schedule,
    const SyncPeerChunkAssignment& peer_assignment,
    const std::string& transport_envelope_idempotency_key,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncPeerTransportIngressProcessResult& out);
// Compatibility entry point. It loads the exact durable frame using
// options.transport_envelope_idempotency_key, then delegates to the current
// restart-safe processing boundary.
SyncValidationResult process_sync_peer_transport_queued_ingress_envelope(
    const SyncPeerTransportIngressProcessOptions& options,
    const SyncPeerTransportEnvelopeVerifyOptions& transport_options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncStagedTransferInspectionResult& inspection,
    const SyncChunkRequestPlanOptions& request_options,
    const SyncChunkRequestPlanResult& request_plan,
    const SyncPeerChunkScheduleResult& peer_schedule,
    const SyncPeerChunkAssignment& peer_assignment,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncPeerTransportIngressProcessResult& out);
SyncValidationResult load_sync_peer_transport_ingress_status(
    const SyncPeerTransportIngressStatusOptions& options,
    SyncPeerTransportIngressStatusResult& out);
SyncValidationResult drain_sync_peer_transport_ingress_retention(
    const SyncPeerTransportIngressRetentionOptions& options,
    SyncPeerTransportIngressRetentionResult& out);
SyncValidationResult submit_sync_peer_transport_local_socket_ingress_fixture(
    const SyncPeerTransportLocalSocketIngressSubmitOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportLocalSocketIngressSubmitResult& out);
SyncValidationResult submit_sync_peer_transport_loopback_ingress_harness(
    const SyncPeerTransportLoopbackIngressSubmitOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportLoopbackIngressSubmitResult& out);
SyncValidationResult verify_sync_session_checkpoint_resume_peer_response_workorder_claims(const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& options,
                                                                                          const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                                          SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingResult& out);
SyncValidationResult accept_sync_session_checkpoint_bound_peer_chunk_response_batch_envelope(const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
                                                                                             const SyncManifestEntry& remote_file_entry,
                                                                                             const SyncLocalApplyPlanEntry& apply_entry,
                                                                                             const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                                             const std::vector<std::string>& chunk_bytes,
                                                                                             const SyncChunkReceiptWriteOptions& write_options,
                                                                                             SyncSessionCheckpointBoundPeerChunkResponseBatchAcceptanceResult& out);
SyncValidationResult advance_sync_session_checkpoint_bound_peer_chunk_acceptance(const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
                                                                                 const SyncManifestEntry& remote_file_entry,
                                                                                 const SyncLocalApplyPlanEntry& apply_entry,
                                                                                 const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                                 const SyncChunkReceiptWriteOptions& write_options,
                                                                                 SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult& out);
SyncValidationResult advance_sync_session_checkpoint_bound_peer_chunk_acceptance_controlled(const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
                                                                                            const SyncManifestEntry& remote_file_entry,
                                                                                            const SyncLocalApplyPlanEntry& apply_entry,
                                                                                            const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                                            const SyncChunkReceiptWriteOptions& write_options,
                                                                                            const SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceControlOptions& control_options,
                                                                                            SyncSessionCheckpointBoundPeerChunkAcceptanceDbAdvanceResult& out);
SyncValidationResult ingest_sync_session_checkpoint_bound_peer_chunk_response_batch(const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
                                                                                   const SyncManifestEntry& remote_file_entry,
                                                                                   const SyncLocalApplyPlanEntry& apply_entry,
                                                                                   const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                                   const std::vector<std::string>& chunk_bytes,
                                                                                   const SyncChunkReceiptWriteOptions& write_options,
                                                                                   SyncSessionCheckpointBoundPeerChunkIngestionResult& out);
SyncValidationResult ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
                                                                                              const SyncManifestEntry& remote_file_entry,
                                                                                              const SyncLocalApplyPlanEntry& apply_entry,
                                                                                              const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                                              const std::vector<std::string>& chunk_bytes,
                                                                                              const SyncChunkReceiptWriteOptions& write_options,
                                                                                              const SyncSessionCheckpointBoundPeerChunkIngestionControlOptions& control_options,
                                                                                              SyncSessionCheckpointBoundPeerChunkIngestionResult& out);
SyncValidationResult recover_sync_session_checkpoint_bound_peer_chunk_sidecars(const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
                                                                                      const SyncManifestEntry& remote_file_entry,
                                                                                      const SyncLocalApplyPlanEntry& apply_entry,
                                                                                      const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
                                                                                      const SyncChunkReceiptWriteOptions& write_options,
                                                                                      SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult& out);
SyncValidationResult recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
                                                                                       const SyncManifestEntry& remote_file_entry,
                                                                                       const SyncLocalApplyPlanEntry& apply_entry,
                                                                                       const SyncChunkReceiptWriteOptions& write_options,
                                                                                       SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult& out);
SyncValidationResult load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
    const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult& out);
SyncValidationResult recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_session(const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
                                                                                          const std::vector<SyncManifestEntry>& remote_file_entries,
                                                                                          const std::vector<SyncLocalApplyPlanEntry>& apply_entries,
                                                                                          const SyncChunkReceiptWriteOptions& write_options,
                                                                                          SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult& out);
SyncValidationResult list_sync_session_checkpoint_bound_peer_sidecar_review_events(const SyncSessionCheckpointBoundPeerSidecarReviewEventReportOptions& options,
                                                                                         SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult& out);
SyncValidationResult quarantine_sync_session_checkpoint_bound_peer_sidecar_review_event(const SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineOptions& options,
                                                                                       SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineResult& out);
SyncValidationResult repair_reset_sync_session_checkpoint_bound_peer_sidecar_review_event(const SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetOptions& options,
                                                                                                      SyncSessionCheckpointBoundPeerSidecarReviewEventRepairResetResult& out);
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
SyncValidationResult run_sync_session_checkpoint_resume_transfer_workorder_daemon_loop(const SyncSessionCheckpointResumeTransferWorkorderDaemonLoopOptions& options,
                                                                                      SyncSessionCheckpointResumeTransferWorkorderDaemonLoopResult& out);
SyncValidationResult load_sync_session_checkpoint_operator_status(const SyncSessionCheckpointOperatorStatusOptions& options,
                                                                  SyncSessionCheckpointOperatorStatusResult& out);
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
        const std::string& ledger_commit_mode = "immediate",
        const std::string& ledger_backend = "local-jsonl",
        const std::string& ledger_backend_capabilities_path = "",
        const std::string& ledger_snapshot_path = "",
        const std::string& ledger_restore_from_snapshot_path = "",
        const std::string& ledger_snapshot_manifest_path = "",
        const std::string& ledger_snapshot_trust_profile_path = "",
        const std::string& ledger_snapshot_trust_profile_sha256 = "");
int run_sqlite_replay_ledger_reset_state_command(
    const std::string& ledger_path,
    const std::string& report_path);
int run_sqlite_replay_ledger_reset_command(
    const std::string& request_path,
    const std::string& request_sha256,
    const std::string& receipt_path);
int run_sqlite_effect_transition_command(const std::string& ledger_path, const std::string& effect_idempotency_key, long long prepared_sequence, const std::string& prepared_entry_hash, const std::string& terminal_state, const std::string& result_digest_sha256, const std::string& transition_reason);
int run_sqlite_effect_signed_transition_command(const std::string& ledger_path, const std::string& intent_path, const std::string& trust_profile_path, const std::string& trust_profile_sha256);
int run_sqlite_effect_pending_report_command(const std::string& ledger_path, const std::string& report_path);
int run_sqlite_effect_outbox_claim_command(const std::string& ledger_path, const std::string& worker_id, long long now_epoch, long long lease_seconds, const std::string& claim_report_path);
int run_sqlite_effect_relay_once_command(const std::string& ledger_path, const std::string& downstream_path, const std::string& worker_id, long long now_epoch, long long lease_seconds, const std::string& terminal_state, const std::string& signer_private_key_pem_path, const std::string& signer_kid, const std::string& trust_profile_path, const std::string& trust_profile_sha256, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_sqlite_effect_relay_configured_once_command(const std::string& ledger_path, const std::string& relay_config_path, const std::string& relay_config_sha256, long long now_epoch, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_sqlite_effect_relay_handle_once_command(const std::string& ledger_path, const std::string& relay_registry_path, const std::string& relay_registry_sha256, const std::string& relay_config_handle, long long now_epoch, const std::string& relay_report_path, bool inject_crash_after_downstream);
int run_ingress_reservation_command(const std::string& ingress_profile_path, const std::string& ingress_profile_sha256, const std::string& ingress_request_path, const std::string& ingress_report_path);
int run_sync_checkpoint_operator_status_report_command(const std::string& checkpoint_path,
                                                        const std::string& session_id,
                                                        long long scheduler_now_epoch,
                                                        const std::string& report_path,
                                                        const std::string& daemon_heartbeat_path = "");
int run_sync_peer_ingress_retention_command(const std::string& checkpoint_path,
                                            const std::string& session_id,
                                            const std::string& operator_id,
                                            const std::string& reason,
                                            long long retention_now_epoch,
                                            long long completed_older_than_epoch,
                                            long long abandoned_older_than_epoch,
                                            long long authority_denial_older_than_epoch,
                                            long long max_completed_rows,
                                            long long max_abandoned_rows,
                                            long long max_authority_denial_rows,
                                            bool dry_run,
                                            const std::string& report_path,
                                            long long sqlite_busy_timeout_ms = static_cast<long long>(kSyncPeerTransportDefaultSqliteBusyTimeoutMs),
                                            long long max_frame_bytes = 16 * 1024 * 1024,
                                            long long max_chunk_count = 1024,
                                            long long max_metadata_field_bytes = 64 * 1024);
int run_sync_peer_authority_supersession_command(const std::string& checkpoint_path,
                                                 const std::string& session_id,
                                                 const std::string& operator_id,
                                                 const std::string& peer_id,
                                                 const std::string& peer_session_id,
                                                 const std::string& transport_instance_id,
                                                 const std::string& old_transport_key_id,
                                                 const std::string& replacement_transport_key_id,
                                                 long long overlap_valid_from_epoch,
                                                 long long overlap_valid_until_epoch,
                                                 long long updated_at_epoch,
                                                 const std::string& reason,
                                                 const std::string& report_path,
                                                 long long sqlite_busy_timeout_ms = static_cast<long long>(kSyncPeerTransportDefaultSqliteBusyTimeoutMs));
int run_sync_checkpoint_sidecar_repair_reset_command(const std::string& checkpoint_path,
                                                     const std::string& session_id,
                                                     const std::string& staging_root_path,
                                                     const std::string& sync_path,
                                                     const std::string& review_event_idempotency_key,
                                                     const std::string& decision_operator_id,
                                                     const std::string& decision_reason,
                                                     long long repair_at_epoch,
                                                     const std::string& repair_worker_id,
                                                     long long repair_worker_lease_epoch,
                                                     long long repair_worker_lease_seconds,
                                                     long long workorder_retry_backoff_seconds,
                                                     const std::string& report_path);
int run_sync_checkpoint_daemon_run_command(const std::string& checkpoint_path,
                                           const std::string& session_id,
                                           const std::string& source_root_path,
                                           const std::string& destination_root_path,
                                           const std::string& staging_root_path,
                                           const std::string& expected_folder_id,
                                           const std::string& expected_source_device_id,
                                           const std::string& expected_destination_device_id,
                                           const std::string& expected_peer_id,
                                           const std::string& peer_id,
                                           const std::string& peer_session_id,
                                           const std::string& worker_id,
                                           const std::string& daemon_id,
                                           long long initial_worker_lease_epoch,
                                           long long initial_scheduler_now_epoch,
                                           long long worker_lease_seconds,
                                           long long loop_tick_seconds,
                                           long long max_loop_passes,
                                           long long max_scheduler_actions_per_pass,
                                           long long workorder_retry_backoff_seconds,
                                           bool recover_bound_peer_sidecars_before_scheduling,
                                           bool require_daemon_owner_lock,
                                           const std::string& report_path,
                                           const std::string& daemon_heartbeat_path = "",
                                           long long daemon_heartbeat_stale_after_seconds = 0);
int run_sync_checkpoint_operator_recovery_workflow_command(const std::string& workflow_config_path,
                                                         const std::string& workflow_report_path);
int run_ingress_reservation_service_command(const std::string& ingress_service_config_path,
                                            const std::string& ingress_service_config_sha256,
                                            const std::string& ingress_transport_context_path,
                                            const std::string& ingress_request_path,
                                            const std::string& ingress_report_path);
}  // namespace anonsync
