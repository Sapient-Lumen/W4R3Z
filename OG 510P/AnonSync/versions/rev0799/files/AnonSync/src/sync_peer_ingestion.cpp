#include "anonsync_core.hpp"
#include "anonsync_core_internal.hpp"
#include "sync_sqlite_support.hpp"

#include <algorithm>
#include <exception>
#include <limits>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {
namespace {

SyncValidationResult peer_ingestion_ok() {
    return {true, ""};
}

SyncValidationResult peer_ingestion_fail(const std::string& reason) {
    return {false, reason};
}

using PeerIngestionSqliteDb = SyncSqliteDb;
using PeerIngestionSqliteStmt = SyncSqliteStmt;

std::string peer_ingestion_sqlite_message(sqlite3* db, const std::string& label) {
    const char* message = db ? sqlite3_errmsg(db) : nullptr;
    return label + ": " + (message ? message : "unknown sqlite error");
}

PeerIngestionSqliteStmt peer_ingestion_prepare_or_throw(
    sqlite3* db,
    const std::string& sql,
    const std::string& label) {
    return sqlite_prepare_or_throw(db, sql, label);
}

PeerIngestionSqliteStmt peer_ingestion_prepare_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& sql,
    const std::string& label) {
    return sqlite_prepare_or_throw(db, sql, label);
}

void peer_ingestion_exec_or_throw(
    SyncSqliteDbHandleSlot& db,
    const std::string& sql,
    const std::string& label) {
    sqlite_exec_or_throw(db, sql, label);
}

void peer_ingestion_bind_text_or_throw(sqlite3_stmt* stmt, int index, const std::string& value, const std::string& label) {
    sqlite_bind_text_or_throw(stmt, index, value, label);
}

void peer_ingestion_bind_u64_or_throw(sqlite3_stmt* stmt, int index, std::uint64_t value, const std::string& label) {
    sqlite_bind_u64_or_throw(stmt, index, value, label);
}

void peer_ingestion_step_done_or_throw(sqlite3_stmt* stmt, const std::string& label) {
    sqlite_step_done_or_throw(stmt, label);
}

std::uint64_t peer_ingestion_column_u64_or_throw(sqlite3_stmt* stmt, int index, const std::string& label) {
    return sqlite_column_u64_or_throw(stmt, index, label);
}

std::string peer_ingestion_column_text_or_throw(sqlite3_stmt* stmt, int index, const std::string& label) {
    return sqlite_column_text_or_throw(stmt, index, label);
}

struct PeerSidecarSweepGroupKey {
    std::string request_idempotency_key;
    std::string schedule_idempotency_key;
    std::string peer_request_idempotency_key;
    std::string execution_idempotency_key;
    std::string peer_id;
    std::string peer_session_id;

    bool operator<(const PeerSidecarSweepGroupKey& other) const {
        if (request_idempotency_key != other.request_idempotency_key) return request_idempotency_key < other.request_idempotency_key;
        if (schedule_idempotency_key != other.schedule_idempotency_key) return schedule_idempotency_key < other.schedule_idempotency_key;
        if (peer_request_idempotency_key != other.peer_request_idempotency_key) return peer_request_idempotency_key < other.peer_request_idempotency_key;
        if (execution_idempotency_key != other.execution_idempotency_key) return execution_idempotency_key < other.execution_idempotency_key;
        if (peer_id != other.peer_id) return peer_id < other.peer_id;
        return peer_session_id < other.peer_session_id;
    }
};

std::string peer_sidecar_sweep_response_key(const PeerSidecarSweepGroupKey& key,
                                            const SyncChunkRange& chunk,
                                            const NormalizedSyncPath& path) {
    const std::string material = length_prefixed_security_tuple("anonsync-sync-sidecar-recovery-sweep-response-v1", {
        {"path", path.value},
        {"request_key", key.request_idempotency_key},
        {"schedule_key", key.schedule_idempotency_key},
        {"peer_request_key", key.peer_request_idempotency_key},
        {"execution_key", key.execution_idempotency_key},
        {"peer_id", key.peer_id},
        {"peer_session_id", key.peer_session_id},
        {"offset", std::to_string(chunk.offset)},
        {"length", std::to_string(chunk.length)},
        {"chunk_sha256", chunk.sha256}
    });
    return "sync-resume-peer-response:v1:sweep-" + sha256_hex(material);
}

struct PeerSidecarSweepGroupCandidate {
    std::vector<SyncChunkRange> chunks;
    std::uint64_t rows = 0;
    std::uint64_t bytes = 0;
    std::uint64_t lease_expires_at_epoch = 0;
};


struct PeerSidecarRecoveryReviewClassification {
    bool review_required = false;
    bool missing_sidecar = false;
    bool tampered_sidecar = false;
    bool staged_bytes_mismatch = false;
    std::string review_reason;
};

bool peer_ingestion_contains(const std::string& haystack, const std::string& needle) {
    return haystack.find(needle) != std::string::npos;
}

PeerSidecarRecoveryReviewClassification classify_peer_sidecar_recovery_failure(const std::string& reason) {
    PeerSidecarRecoveryReviewClassification out;
    if (peer_ingestion_contains(reason, "missing accepted receipt sidecar") ||
        (peer_ingestion_contains(reason, "receipt sidecar") && peer_ingestion_contains(reason, "missing"))) {
        out.review_required = true;
        out.missing_sidecar = true;
        out.review_reason = "missing accepted receipt sidecar evidence";
        return out;
    }
    if (peer_ingestion_contains(reason, "staged chunk bytes do not match response evidence") ||
        peer_ingestion_contains(reason, "receipt does not match staged bytes") ||
        peer_ingestion_contains(reason, "staged transfer inspection receipt does not match staged bytes")) {
        out.review_required = true;
        out.staged_bytes_mismatch = true;
        out.review_reason = "staged chunk bytes no longer match accepted evidence";
        return out;
    }
    if (peer_ingestion_contains(reason, "receipt exists with different material") ||
        peer_ingestion_contains(reason, "staged sync chunk receipt must not be a symlink") ||
        peer_ingestion_contains(reason, "staged sync chunk receipt must be a regular file") ||
        peer_ingestion_contains(reason, "existing receipt row does not match accepted sidecar evidence")) {
        out.review_required = true;
        out.tampered_sidecar = true;
        out.review_reason = "accepted receipt sidecar evidence is present but invalid";
        return out;
    }
    return out;
}


std::string peer_sidecar_recovery_review_category(const PeerSidecarRecoveryReviewClassification& classification) {
    if (classification.missing_sidecar) return "missing-sidecar";
    if (classification.tampered_sidecar) return "tampered-sidecar";
    if (classification.staged_bytes_mismatch) return "staged-bytes-mismatch";
    return "unknown";
}

std::string peer_sidecar_recovery_chunk_set_digest(const PeerSidecarSweepGroupCandidate& candidate) {
    std::string material;
    std::uint64_t index = 0;
    for (const auto& chunk : candidate.chunks) {
        material += length_prefixed_security_tuple("anonsync-sync-sidecar-review-chunk-v1", {
            {"index", std::to_string(index++)},
            {"offset", std::to_string(chunk.offset)},
            {"length", std::to_string(chunk.length)},
            {"chunk_sha256", chunk.sha256}
        });
    }
    return sha256_hex(material);
}

std::string peer_sidecar_recovery_review_event_idempotency_key(
    const std::string& session_id,
    const NormalizedSyncPath& path,
    const PeerSidecarSweepGroupKey& key,
    const PeerSidecarSweepGroupCandidate& candidate,
    const PeerSidecarRecoveryReviewClassification& classification) {
    const std::string material = length_prefixed_security_tuple("anonsync-sync-sidecar-review-event-v1", {
        {"session_id", session_id},
        {"path", path.value},
        {"review_category", peer_sidecar_recovery_review_category(classification)},
        {"request_key", key.request_idempotency_key},
        {"schedule_key", key.schedule_idempotency_key},
        {"peer_request_key", key.peer_request_idempotency_key},
        {"execution_key", key.execution_idempotency_key},
        {"peer_id", key.peer_id},
        {"peer_session_id", key.peer_session_id},
        {"chunk_count", std::to_string(candidate.rows)},
        {"bytes", std::to_string(candidate.bytes)},
        {"chunk_set_digest", peer_sidecar_recovery_chunk_set_digest(candidate)}
    });
    return "sync-sidecar-review:v1:" + sha256_hex(material);
}

void ensure_peer_sidecar_review_events_schema_or_throw(SyncSqliteDbHandleSlot& db) {
    peer_ingestion_exec_or_throw(db,
        "CREATE TABLE IF NOT EXISTS sync_session_bound_peer_sidecar_review_events("
        "session_id TEXT NOT NULL REFERENCES sync_session_checkpoints(session_id) ON DELETE CASCADE,"
        "path TEXT NOT NULL,"
        "review_event_idempotency_key TEXT NOT NULL,"
        "review_category TEXT NOT NULL CHECK(review_category IN ('missing-sidecar','tampered-sidecar','staged-bytes-mismatch')),"
        "review_reason TEXT NOT NULL,"
        "request_idempotency_key TEXT NOT NULL,"
        "schedule_idempotency_key TEXT NOT NULL,"
        "peer_request_idempotency_key TEXT NOT NULL,"
        "execution_idempotency_key TEXT NOT NULL,"
        "peer_id TEXT NOT NULL,"
        "peer_session_id TEXT NOT NULL,"
        "worker_id TEXT NOT NULL,"
        "worker_lease_id TEXT NOT NULL,"
        "chunks_considered INTEGER NOT NULL CHECK(chunks_considered > 0),"
        "bytes_considered INTEGER NOT NULL CHECK(bytes_considered >= 0),"
        "first_observed_at_epoch INTEGER NOT NULL CHECK(first_observed_at_epoch > 0),"
        "last_observed_at_epoch INTEGER NOT NULL CHECK(last_observed_at_epoch >= first_observed_at_epoch),"
        "observations INTEGER NOT NULL CHECK(observations > 0),"
        "PRIMARY KEY(session_id, path, review_event_idempotency_key));",
        "sync session checkpoint bound peer sidecar review event schema");
}

void ensure_peer_sidecar_review_event_resolutions_schema_or_throw(
    SyncSqliteDbHandleSlot& db) {
    peer_ingestion_exec_or_throw(db,
        "CREATE TABLE IF NOT EXISTS sync_session_bound_peer_sidecar_review_event_resolutions("
        "session_id TEXT NOT NULL,"
        "path TEXT NOT NULL,"
        "review_event_idempotency_key TEXT NOT NULL,"
        "resolution_state TEXT NOT NULL CHECK(resolution_state='quarantined'),"
        "resolution_reason TEXT NOT NULL,"
        "resolved_by_operator_id TEXT NOT NULL,"
        "resolved_at_epoch INTEGER NOT NULL CHECK(resolved_at_epoch > 0),"
        "workorder_rows_quarantined INTEGER NOT NULL CHECK(workorder_rows_quarantined >= 0),"
        "workorder_rows_already_quarantined INTEGER NOT NULL CHECK(workorder_rows_already_quarantined >= 0),"
        "PRIMARY KEY(session_id, path, review_event_idempotency_key),"
        "FOREIGN KEY(session_id, path, review_event_idempotency_key) "
        "REFERENCES sync_session_bound_peer_sidecar_review_events(session_id, path, review_event_idempotency_key) ON DELETE CASCADE);",
        "sync session checkpoint bound peer sidecar review event resolution schema");
}

struct PeerSidecarReviewEventPersistResult {
    std::string review_event_idempotency_key;
    bool written = false;
    bool already_present = false;
};

PeerSidecarReviewEventPersistResult persist_peer_sidecar_recovery_review_event(
    const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
    const NormalizedSyncPath& path,
    const PeerSidecarSweepGroupKey& key,
    const PeerSidecarSweepGroupCandidate& candidate,
    const PeerSidecarRecoveryReviewClassification& classification) {
    if (!classification.review_required) {
        throw std::runtime_error("sync session checkpoint bound peer sidecar review event requires a review classification");
    }
    PeerSidecarReviewEventPersistResult result;
    result.review_event_idempotency_key = peer_sidecar_recovery_review_event_idempotency_key(
        options.session_id,
        path,
        key,
        candidate,
        classification);

    PeerIngestionSqliteDb db;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    if (sqlite3_open_v2(options.sqlite_path.c_str(), db.db.out(), flags, nullptr) != SQLITE_OK) {
        throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer sidecar review event could not open sqlite database"));
    }
    peer_ingestion_exec_or_throw(db.db, "PRAGMA foreign_keys=ON;", "sync session checkpoint bound peer sidecar review event enable foreign keys");
    ensure_peer_sidecar_review_events_schema_or_throw(db.db);

    SyncSqliteTransaction transaction(
        db.db,
        "sync session checkpoint bound peer sidecar review event",
        SyncSqliteTransactionMode::Immediate);

    PeerIngestionSqliteStmt insert_stmt = peer_ingestion_prepare_or_throw(
        db.db,
        "INSERT OR IGNORE INTO sync_session_bound_peer_sidecar_review_events("
        "session_id, path, review_event_idempotency_key, review_category, review_reason, "
        "request_idempotency_key, schedule_idempotency_key, peer_request_idempotency_key, "
        "execution_idempotency_key, peer_id, peer_session_id, worker_id, worker_lease_id, "
        "chunks_considered, bytes_considered, first_observed_at_epoch, last_observed_at_epoch, observations) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1);",
        "sync session checkpoint bound peer sidecar review event insert prepare");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar review event bind session");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 2, path.value, "sync session checkpoint bound peer sidecar review event bind path");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 3, result.review_event_idempotency_key, "sync session checkpoint bound peer sidecar review event bind event key");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 4, peer_sidecar_recovery_review_category(classification), "sync session checkpoint bound peer sidecar review event bind category");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 5, classification.review_reason, "sync session checkpoint bound peer sidecar review event bind reason");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 6, key.request_idempotency_key, "sync session checkpoint bound peer sidecar review event bind request key");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 7, key.schedule_idempotency_key, "sync session checkpoint bound peer sidecar review event bind schedule key");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 8, key.peer_request_idempotency_key, "sync session checkpoint bound peer sidecar review event bind peer request key");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 9, key.execution_idempotency_key, "sync session checkpoint bound peer sidecar review event bind execution key");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 10, key.peer_id, "sync session checkpoint bound peer sidecar review event bind peer id");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 11, key.peer_session_id, "sync session checkpoint bound peer sidecar review event bind peer session");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 12, options.worker_id, "sync session checkpoint bound peer sidecar review event bind worker");
    peer_ingestion_bind_text_or_throw(insert_stmt.stmt, 13, options.worker_lease_id, "sync session checkpoint bound peer sidecar review event bind lease");
    peer_ingestion_bind_u64_or_throw(insert_stmt.stmt, 14, candidate.rows, "sync session checkpoint bound peer sidecar review event bind chunks");
    peer_ingestion_bind_u64_or_throw(insert_stmt.stmt, 15, candidate.bytes, "sync session checkpoint bound peer sidecar review event bind bytes");
    peer_ingestion_bind_u64_or_throw(insert_stmt.stmt, 16, options.binding_now_epoch, "sync session checkpoint bound peer sidecar review event bind first observed");
    peer_ingestion_bind_u64_or_throw(insert_stmt.stmt, 17, options.binding_now_epoch, "sync session checkpoint bound peer sidecar review event bind last observed");
    peer_ingestion_step_done_or_throw(insert_stmt.stmt, "sync session checkpoint bound peer sidecar review event insert");
    result.written = sqlite3_changes(db.db) > 0;

    if (!result.written) {
        PeerIngestionSqliteStmt update_stmt = peer_ingestion_prepare_or_throw(
            db.db,
            "UPDATE sync_session_bound_peer_sidecar_review_events "
            "SET last_observed_at_epoch=?, observations=observations+1, review_reason=?, chunks_considered=?, bytes_considered=? "
            "WHERE session_id=? AND path=? AND review_event_idempotency_key=?;",
            "sync session checkpoint bound peer sidecar review event update prepare");
        peer_ingestion_bind_u64_or_throw(update_stmt.stmt, 1, options.binding_now_epoch, "sync session checkpoint bound peer sidecar review event update last observed");
        peer_ingestion_bind_text_or_throw(update_stmt.stmt, 2, classification.review_reason, "sync session checkpoint bound peer sidecar review event update reason");
        peer_ingestion_bind_u64_or_throw(update_stmt.stmt, 3, candidate.rows, "sync session checkpoint bound peer sidecar review event update chunks");
        peer_ingestion_bind_u64_or_throw(update_stmt.stmt, 4, candidate.bytes, "sync session checkpoint bound peer sidecar review event update bytes");
        peer_ingestion_bind_text_or_throw(update_stmt.stmt, 5, options.session_id, "sync session checkpoint bound peer sidecar review event update session");
        peer_ingestion_bind_text_or_throw(update_stmt.stmt, 6, path.value, "sync session checkpoint bound peer sidecar review event update path");
        peer_ingestion_bind_text_or_throw(update_stmt.stmt, 7, result.review_event_idempotency_key, "sync session checkpoint bound peer sidecar review event update event key");
        peer_ingestion_step_done_or_throw(update_stmt.stmt, "sync session checkpoint bound peer sidecar review event update");
        if (sqlite3_changes(db.db) == 0) {
            throw std::runtime_error("sync session checkpoint bound peer sidecar review event upsert neither inserted nor updated");
        }
        result.already_present = true;
    }

    // Finalize every statement-owned generation pin before the transaction
    // boundary is ended. The commit guard is the sole live owner capability at
    // COMMIT, so a statement can never outlive or ambiguously straddle it.
    insert_stmt.reset();
    transaction.commit();
    return result;
}

void apply_peer_sidecar_recovery_review_classification(
    const PeerSidecarRecoveryReviewClassification& classification,
    const PeerSidecarSweepGroupCandidate& candidate,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult& group_result,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult& sweep_result) {
    if (!classification.review_required) return;
    group_result.review_required = true;
    group_result.review_due_to_missing_sidecar = classification.missing_sidecar;
    group_result.review_due_to_tampered_sidecar = classification.tampered_sidecar;
    group_result.review_due_to_staged_bytes_mismatch = classification.staged_bytes_mismatch;
    group_result.review_reason = classification.review_reason;
    ++sweep_result.recovery_groups_review_required;
    sweep_result.claimed_rows_review_required += candidate.rows;
    sweep_result.bytes_review_required += candidate.bytes;
    if (classification.missing_sidecar) ++sweep_result.recovery_groups_review_missing_sidecar;
    if (classification.tampered_sidecar) ++sweep_result.recovery_groups_review_tampered_sidecar;
    if (classification.staged_bytes_mismatch) ++sweep_result.recovery_groups_review_staged_bytes_mismatch;
}

SyncValidationResult validate_peer_sidecar_recovery_sweep_options(const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
                                                                  const std::string& label) {
    if (options.sqlite_path.empty()) {
        return peer_ingestion_fail(label + " sqlite_path is required");
    }
    if (options.session_id.empty()) {
        return peer_ingestion_fail(label + " session_id is required");
    }
    if (options.worker_id.empty()) {
        return peer_ingestion_fail(label + " worker_id is required");
    }
    if (options.worker_lease_id.empty()) {
        return peer_ingestion_fail(label + " worker_lease_id is required");
    }
    if (options.binding_now_epoch == 0) {
        return peer_ingestion_fail(label + " binding_now_epoch must be positive");
    }
    return peer_ingestion_ok();
}

const SyncManifestEntry* find_peer_sidecar_remote_file_by_path(const std::vector<SyncManifestEntry>& remote_file_entries,
                                                               const NormalizedSyncPath& path) {
    const SyncManifestEntry* found = nullptr;
    for (const auto& entry : remote_file_entries) {
        if (entry.kind != SyncManifestEntryKind::File || entry.path.value != path.value) continue;
        if (found != nullptr) {
            throw std::runtime_error("sync session checkpoint bound peer chunk sidecar recovery session sweep remote file evidence is not unique for path: " + path.value);
        }
        found = &entry;
    }
    return found;
}

void add_peer_sidecar_sweep_candidate_chunk(std::map<PeerSidecarSweepGroupKey, PeerSidecarSweepGroupCandidate>& candidates,
                                            const PeerSidecarSweepGroupKey& key,
                                            const SyncChunkRange& chunk,
                                            std::uint64_t lease_expires_at_epoch) {
    PeerSidecarSweepGroupCandidate& candidate = candidates[key];
    candidate.chunks.push_back(chunk);
    ++candidate.rows;
    candidate.bytes += chunk.length;
    if (candidate.lease_expires_at_epoch == 0 || lease_expires_at_epoch < candidate.lease_expires_at_epoch) {
        candidate.lease_expires_at_epoch = lease_expires_at_epoch;
    }
}

SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult make_deferred_peer_sidecar_sweep_group_result(
    const NormalizedSyncPath& path,
    const PeerSidecarSweepGroupKey& key,
    const PeerSidecarSweepGroupCandidate& candidate,
    const std::string& reason) {
    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult group_result;
    group_result.path = path;
    group_result.request_idempotency_key = key.request_idempotency_key;
    group_result.schedule_idempotency_key = key.schedule_idempotency_key;
    group_result.peer_request_idempotency_key = key.peer_request_idempotency_key;
    group_result.execution_idempotency_key = key.execution_idempotency_key;
    group_result.peer_id = key.peer_id;
    group_result.peer_session_id = key.peer_session_id;
    group_result.chunks_considered = candidate.rows;
    group_result.bytes_considered = candidate.bytes;
    group_result.failure_reason = reason;
    return group_result;
}


std::vector<NormalizedSyncPath> peer_sidecar_claimed_workorder_paths_for_session_or_throw(
    const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options) {
    PeerIngestionSqliteDb db;
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    if (sqlite3_open_v2(options.sqlite_path.c_str(), db.db.out(), flags, nullptr) != SQLITE_OK) {
        throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer chunk sidecar recovery session sweep could not open sqlite database for claimed path coverage"));
    }
    PeerIngestionSqliteStmt stmt = peer_ingestion_prepare_or_throw(db.db,
        "SELECT DISTINCT path FROM sync_session_resume_transfer_workorders "
        "WHERE session_id=? AND worker_id=? AND worker_lease_id=? AND work_state='claimed' "
        "ORDER BY path;",
        "sync session checkpoint bound peer chunk sidecar recovery session sweep claimed path coverage query prepare");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer chunk sidecar recovery session sweep bind claimed path session");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 2, options.worker_id, "sync session checkpoint bound peer chunk sidecar recovery session sweep bind claimed path worker");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 3, options.worker_lease_id, "sync session checkpoint bound peer chunk sidecar recovery session sweep bind claimed path lease");

    std::vector<NormalizedSyncPath> paths;
    while (true) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer chunk sidecar recovery session sweep claimed path coverage query"));
        }
        NormalizedSyncPath path;
        SyncValidationResult normalized_path = normalize_sync_relative_path(
            peer_ingestion_column_text_or_throw(stmt.stmt, 0, "sync session checkpoint bound peer chunk sidecar recovery session sweep claimed path column"),
            path);
        if (!normalized_path.ok) {
            throw std::runtime_error("sync session checkpoint bound peer chunk sidecar recovery session sweep stored claimed path is invalid: " + normalized_path.reason);
        }
        paths.push_back(std::move(path));
    }
    return paths;
}

SyncManifestEntryKind peer_sidecar_manifest_kind_from_text_or_throw(const std::string& value, const std::string& label) {
    if (value == "file") return SyncManifestEntryKind::File;
    if (value == "tombstone") return SyncManifestEntryKind::Tombstone;
    throw std::runtime_error(label + " has unsupported manifest kind: " + value);
}

SyncPlanAction peer_sidecar_plan_action_from_text_or_throw(const std::string& value, const std::string& label) {
    if (value == "noop") return SyncPlanAction::Noop;
    if (value == "fetch_remote_file") return SyncPlanAction::FetchRemoteFile;
    if (value == "publish_local_file") return SyncPlanAction::PublishLocalFile;
    if (value == "apply_remote_tombstone") return SyncPlanAction::ApplyRemoteTombstone;
    if (value == "publish_local_tombstone") return SyncPlanAction::PublishLocalTombstone;
    if (value == "record_conflict") return SyncPlanAction::RecordConflict;
    throw std::runtime_error(label + " has unsupported plan action: " + value);
}

SyncLocalApplyAction peer_sidecar_local_apply_action_from_text_or_throw(const std::string& value, const std::string& label) {
    if (value == "noop") return SyncLocalApplyAction::Noop;
    if (value == "stage_remote_file") return SyncLocalApplyAction::StageRemoteFile;
    if (value == "delete_local_path") return SyncLocalApplyAction::DeleteLocalPath;
    if (value == "preserve_conflict_copy") return SyncLocalApplyAction::PreserveConflictCopy;
    if (value == "advertise_local_file") return SyncLocalApplyAction::AdvertiseLocalFile;
    if (value == "advertise_local_tombstone") return SyncLocalApplyAction::AdvertiseLocalTombstone;
    throw std::runtime_error(label + " has unsupported local apply action: " + value);
}

bool peer_ingestion_table_exists_or_throw(sqlite3* db, const std::string& table_name, const std::string& label) {
    PeerIngestionSqliteStmt stmt = peer_ingestion_prepare_or_throw(
        db,
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;",
        label + " table-exists prepare");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 1, table_name, label + " table name");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw std::runtime_error(peer_ingestion_sqlite_message(db, label + " table-exists step"));
    return peer_ingestion_column_u64_or_throw(stmt.stmt, 0, label + " table-exists count") != 0;
}

std::string peer_ingestion_schema_meta_value_or_empty_or_throw(sqlite3* db,
                                                               const std::string& key,
                                                               const std::string& label) {
    if (!peer_ingestion_table_exists_or_throw(db, "sync_session_schema_meta", label)) return std::string();
    PeerIngestionSqliteStmt stmt = peer_ingestion_prepare_or_throw(
        db,
        "SELECT value FROM sync_session_schema_meta WHERE key=?;",
        label + " schema-meta prepare");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 1, key, label + " schema-meta key");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return std::string();
    if (rc != SQLITE_ROW) throw std::runtime_error(peer_ingestion_sqlite_message(db, label + " schema-meta step"));
    const std::string value = peer_ingestion_column_text_or_throw(stmt.stmt, 0, label + " schema-meta value");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(label + " schema metadata key is not unique");
    }
    return value;
}

bool peer_ingestion_supported_checkpoint_schema_version(const std::string& version) {
    return version == "rev0674-sync-session-checkpoint-v1" ||
           version == "rev0677-sync-session-checkpoint-v2" ||
           version == "rev0688-sync-session-checkpoint-v3" ||
           version == "rev0720-sync-session-checkpoint-v4";
}

bool peer_ingestion_checkpoint_schema_has_manifest_chunks(const std::string& version) {
    return version == "rev0677-sync-session-checkpoint-v2" ||
           version == "rev0688-sync-session-checkpoint-v3" ||
           version == "rev0720-sync-session-checkpoint-v4";
}

bool peer_ingestion_checkpoint_schema_has_manifest_lineage(const std::string& version) {
    return version == "rev0720-sync-session-checkpoint-v4";
}

void classify_archived_checkpoint_sidecar_hydration_backfill_or_throw(
    sqlite3* db,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult& out) {
    out.archived_checkpoint_migration_backfill_checked = true;
    out.checkpoint_schema_version = peer_ingestion_schema_meta_value_or_empty_or_throw(
        db,
        "schema_version",
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence loader");
    out.checkpoint_schema_supported = peer_ingestion_supported_checkpoint_schema_version(out.checkpoint_schema_version);
    out.checkpoint_schema_has_manifest_chunks =
        peer_ingestion_checkpoint_schema_has_manifest_chunks(out.checkpoint_schema_version) &&
        peer_ingestion_table_exists_or_throw(db,
                                             "sync_session_manifest_chunks",
                                             "sync session checkpoint bound peer sidecar recovery checkpoint evidence loader");
    out.checkpoint_schema_has_manifest_lineage =
        peer_ingestion_checkpoint_schema_has_manifest_lineage(out.checkpoint_schema_version) &&
        peer_ingestion_table_exists_or_throw(db,
                                             "sync_session_manifest_lineage",
                                             "sync session checkpoint bound peer sidecar recovery checkpoint evidence loader");
    out.archived_checkpoint_exact_startup_hydration_supported = out.checkpoint_schema_supported &&
                                                                out.checkpoint_schema_has_manifest_chunks &&
                                                                out.checkpoint_schema_has_manifest_lineage;
    out.archived_checkpoint_migration_backfill_required = out.checkpoint_schema_supported &&
                                                          !out.archived_checkpoint_exact_startup_hydration_supported;
    out.archived_checkpoint_migration_backfill_blocked_missing_lineage = out.checkpoint_schema_supported &&
                                                                        out.checkpoint_schema_has_manifest_chunks &&
                                                                        !out.checkpoint_schema_has_manifest_lineage;
    if (!out.checkpoint_schema_supported) {
        out.archived_checkpoint_migration_backfill_reason = "unsupported checkpoint schema cannot be used for startup sidecar hydration";
    } else if (out.archived_checkpoint_exact_startup_hydration_supported) {
        out.archived_checkpoint_migration_backfill_reason = "checkpoint carries exact manifest chunk and lineage rows for startup hydration";
    } else if (out.archived_checkpoint_migration_backfill_blocked_missing_lineage) {
        out.archived_checkpoint_migration_backfill_reason = "archived checkpoint lacks manifest lineage rows; exact remote manifest entry backfill is not possible";
    } else if (!out.checkpoint_schema_has_manifest_chunks) {
        out.archived_checkpoint_migration_backfill_reason = "archived checkpoint lacks manifest chunk rows; exact sidecar recovery backfill is not possible";
    } else {
        out.archived_checkpoint_migration_backfill_reason = "checkpoint schema is known but exact startup hydration evidence is incomplete";
    }
}

bool load_peer_sidecar_apply_entry_for_path_or_throw(sqlite3* db,
                                                     const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
                                                     const NormalizedSyncPath& path,
                                                     SyncLocalApplyPlanEntry& out) {
    PeerIngestionSqliteStmt stmt = peer_ingestion_prepare_or_throw(db,
        "SELECT source_action, local_action, idempotency_key, local_entry_digest, remote_entry_digest, "
        "local_version_digest, remote_version_digest, remote_size_bytes, remote_content_sha256, "
        "absolute_target_path, absolute_staging_path, conflict_set_id "
        "FROM sync_session_apply_intents WHERE session_id=? AND path=?;",
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply-intent query prepare");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply session");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 2, path.value, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply path");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return false;
    if (rc != SQLITE_ROW) throw std::runtime_error(peer_ingestion_sqlite_message(db, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply-intent query"));

    out = SyncLocalApplyPlanEntry{};
    out.path = path;
    out.source_action = peer_sidecar_plan_action_from_text_or_throw(
        peer_ingestion_column_text_or_throw(stmt.stmt, 0, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply source action"),
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply source action");
    out.local_action = peer_sidecar_local_apply_action_from_text_or_throw(
        peer_ingestion_column_text_or_throw(stmt.stmt, 1, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply local action"),
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply local action");
    out.idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 2, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply idempotency key");
    out.local_entry_digest = peer_ingestion_column_text_or_throw(stmt.stmt, 3, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply local entry digest");
    out.remote_entry_digest = peer_ingestion_column_text_or_throw(stmt.stmt, 4, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply remote entry digest");
    out.local_version_digest = peer_ingestion_column_text_or_throw(stmt.stmt, 5, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply local version digest");
    out.remote_version_digest = peer_ingestion_column_text_or_throw(stmt.stmt, 6, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply remote version digest");
    out.remote_size_bytes = peer_ingestion_column_u64_or_throw(stmt.stmt, 7, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply remote size");
    out.remote_content_sha256 = peer_ingestion_column_text_or_throw(stmt.stmt, 8, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply remote content sha");
    out.absolute_target_path = peer_ingestion_column_text_or_throw(stmt.stmt, 9, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply target path");
    out.absolute_staging_path = peer_ingestion_column_text_or_throw(stmt.stmt, 10, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply staging path");
    out.conflict_set_id = peer_ingestion_column_text_or_throw(stmt.stmt, 11, "sync session checkpoint bound peer sidecar recovery checkpoint evidence apply conflict id");
    out.remote_entry_present = !out.remote_entry_digest.empty();
    out.remote_entry_kind = SyncManifestEntryKind::File;
    out.local_entry_present = !out.local_entry_digest.empty();
    out.needed_chunks.clear();
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error("sync session checkpoint bound peer sidecar recovery checkpoint evidence apply intent is not unique for path: " + path.value);
    }
    return true;
}

bool load_peer_sidecar_remote_file_entry_for_path_or_throw(sqlite3* db,
                                                           const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
                                                           const NormalizedSyncPath& path,
                                                           SyncManifestEntry& out,
                                                           std::uint64_t& chunks_loaded,
                                                           std::uint64_t& lineage_rows_loaded,
                                                           bool& missing_lineage_rows) {
    PeerIngestionSqliteStmt stmt = peer_ingestion_prepare_or_throw(db,
        "SELECT m.folder_id, m.device_id, e.kind, e.entry_digest, e.version_digest, e.size_bytes, "
        "e.content_sha256, e.chunk_count, e.lineage_count, e.conflict_set_id "
        "FROM sync_session_manifest_entries e "
        "JOIN sync_session_manifests m ON m.session_id=e.session_id AND m.role=e.role "
        "WHERE e.session_id=? AND e.role='source' AND e.path=?;",
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote entry query prepare");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote session");
    peer_ingestion_bind_text_or_throw(stmt.stmt, 2, path.value, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote path");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return false;
    if (rc != SQLITE_ROW) throw std::runtime_error(peer_ingestion_sqlite_message(db, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote entry query"));

    out = SyncManifestEntry{};
    out.folder_id = peer_ingestion_column_text_or_throw(stmt.stmt, 0, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote folder");
    out.device_id = peer_ingestion_column_text_or_throw(stmt.stmt, 1, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote device");
    out.path = path;
    out.kind = peer_sidecar_manifest_kind_from_text_or_throw(
        peer_ingestion_column_text_or_throw(stmt.stmt, 2, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote kind"),
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote kind");
    const std::string stored_entry_digest = peer_ingestion_column_text_or_throw(stmt.stmt, 3, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote entry digest");
    const std::string stored_version_digest = peer_ingestion_column_text_or_throw(stmt.stmt, 4, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote version digest");
    out.size_bytes = peer_ingestion_column_u64_or_throw(stmt.stmt, 5, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote size");
    out.content_sha256 = peer_ingestion_column_text_or_throw(stmt.stmt, 6, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote content sha");
    const std::uint64_t expected_chunks = peer_ingestion_column_u64_or_throw(stmt.stmt, 7, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote chunk count");
    const std::uint64_t expected_lineage = peer_ingestion_column_u64_or_throw(stmt.stmt, 8, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote lineage count");
    out.conflict_set_id = peer_ingestion_column_text_or_throw(stmt.stmt, 9, "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote conflict id");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error("sync session checkpoint bound peer sidecar recovery checkpoint evidence remote entry is not unique for path: " + path.value);
    }

    PeerIngestionSqliteStmt chunk_stmt = peer_ingestion_prepare_or_throw(db,
        "SELECT chunk_offset, chunk_length, chunk_sha256 FROM sync_session_manifest_chunks "
        "WHERE session_id=? AND role='source' AND path=? ORDER BY chunk_index, chunk_offset;",
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote chunks query prepare");
    peer_ingestion_bind_text_or_throw(chunk_stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar recovery checkpoint evidence chunk session");
    peer_ingestion_bind_text_or_throw(chunk_stmt.stmt, 2, path.value, "sync session checkpoint bound peer sidecar recovery checkpoint evidence chunk path");
    while (true) {
        const int chunk_rc = sqlite3_step(chunk_stmt.stmt);
        if (chunk_rc == SQLITE_DONE) break;
        if (chunk_rc != SQLITE_ROW) throw std::runtime_error(peer_ingestion_sqlite_message(db, "sync session checkpoint bound peer sidecar recovery checkpoint evidence chunks query"));
        SyncChunkRange chunk;
        chunk.offset = peer_ingestion_column_u64_or_throw(chunk_stmt.stmt, 0, "sync session checkpoint bound peer sidecar recovery checkpoint evidence chunk offset");
        chunk.length = peer_ingestion_column_u64_or_throw(chunk_stmt.stmt, 1, "sync session checkpoint bound peer sidecar recovery checkpoint evidence chunk length");
        chunk.sha256 = peer_ingestion_column_text_or_throw(chunk_stmt.stmt, 2, "sync session checkpoint bound peer sidecar recovery checkpoint evidence chunk sha");
        out.chunks.push_back(std::move(chunk));
        ++chunks_loaded;
    }
    if (out.chunks.size() != expected_chunks) {
        throw std::runtime_error("sync session checkpoint bound peer sidecar recovery checkpoint evidence remote chunk rows do not match recorded count for path: " + path.value);
    }

    if (!peer_ingestion_table_exists_or_throw(db, "sync_session_manifest_lineage", "sync session checkpoint bound peer sidecar recovery checkpoint evidence")) {
        missing_lineage_rows = expected_lineage != 0;
        return false;
    }
    PeerIngestionSqliteStmt lineage_stmt = peer_ingestion_prepare_or_throw(db,
        "SELECT lineage_device_id, lineage_counter FROM sync_session_manifest_lineage "
        "WHERE session_id=? AND role='source' AND path=? ORDER BY lineage_index, lineage_device_id;",
        "sync session checkpoint bound peer sidecar recovery checkpoint evidence remote lineage query prepare");
    peer_ingestion_bind_text_or_throw(lineage_stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar recovery checkpoint evidence lineage session");
    peer_ingestion_bind_text_or_throw(lineage_stmt.stmt, 2, path.value, "sync session checkpoint bound peer sidecar recovery checkpoint evidence lineage path");
    while (true) {
        const int lineage_rc = sqlite3_step(lineage_stmt.stmt);
        if (lineage_rc == SQLITE_DONE) break;
        if (lineage_rc != SQLITE_ROW) throw std::runtime_error(peer_ingestion_sqlite_message(db, "sync session checkpoint bound peer sidecar recovery checkpoint evidence lineage query"));
        SyncVersionLineageEntry lineage;
        lineage.device_id = peer_ingestion_column_text_or_throw(lineage_stmt.stmt, 0, "sync session checkpoint bound peer sidecar recovery checkpoint evidence lineage device");
        lineage.counter = peer_ingestion_column_u64_or_throw(lineage_stmt.stmt, 1, "sync session checkpoint bound peer sidecar recovery checkpoint evidence lineage counter");
        out.lineage.push_back(std::move(lineage));
        ++lineage_rows_loaded;
    }
    if (out.lineage.size() != expected_lineage) {
        missing_lineage_rows = true;
        return false;
    }
    const SyncValidationResult entry_validation = validate_sync_manifest_entry(out);
    if (!entry_validation.ok) {
        throw std::runtime_error("sync session checkpoint bound peer sidecar recovery checkpoint evidence reconstructed remote entry is invalid for path " + path.value + ": " + entry_validation.reason);
    }
    if (sync_manifest_entry_digest(out) != stored_entry_digest || sync_manifest_entry_version_digest(out) != stored_version_digest) {
        throw std::runtime_error("sync session checkpoint bound peer sidecar recovery checkpoint evidence reconstructed remote entry digest does not match checkpoint row for path: " + path.value);
    }
    return true;
}

bool peer_sidecar_apply_entry_routes_remote_file_bytes_to_staging(
    const SyncLocalApplyPlanEntry& apply_entry) {
    return (apply_entry.source_action == SyncPlanAction::FetchRemoteFile &&
            apply_entry.local_action == SyncLocalApplyAction::StageRemoteFile) ||
           (apply_entry.source_action == SyncPlanAction::RecordConflict &&
            apply_entry.local_action == SyncLocalApplyAction::PreserveConflictCopy &&
            apply_entry.remote_entry_present &&
            apply_entry.remote_entry_kind == SyncManifestEntryKind::File);
}

std::map<std::string, std::uint64_t> peer_sidecar_remote_byte_apply_path_counts(
    const std::vector<SyncLocalApplyPlanEntry>& apply_entries) {
    std::map<std::string, std::uint64_t> counts;
    for (const auto& apply_entry : apply_entries) {
        if (!peer_sidecar_apply_entry_routes_remote_file_bytes_to_staging(apply_entry)) {
            continue;
        }
        ++counts[apply_entry.path.value];
    }
    return counts;
}

std::map<std::string, std::uint64_t> peer_sidecar_remote_file_path_counts(
    const std::vector<SyncManifestEntry>& remote_file_entries) {
    std::map<std::string, std::uint64_t> counts;
    for (const auto& entry : remote_file_entries) {
        if (entry.kind != SyncManifestEntryKind::File) continue;
        ++counts[entry.path.value];
    }
    return counts;
}

SyncValidationResult validate_peer_sidecar_remote_apply_recovery_evidence(const SyncManifestEntry& remote_file_entry,
                                                                          const SyncLocalApplyPlanEntry& apply_entry) {
    SyncValidationResult remote_result = validate_sync_manifest_entry(remote_file_entry);
    if (!remote_result.ok) return peer_ingestion_fail("remote manifest entry invalid: " + remote_result.reason);
    if (remote_file_entry.kind != SyncManifestEntryKind::File) return peer_ingestion_fail("remote manifest entry is not a file");
    if (!peer_sidecar_apply_entry_routes_remote_file_bytes_to_staging(apply_entry)) {
        return peer_ingestion_fail("apply entry is not a remote-file byte-staging intent");
    }
    if (apply_entry.path.value != remote_file_entry.path.value) return peer_ingestion_fail("apply path does not match remote manifest path");
    const std::string expected_remote_digest = sync_manifest_entry_digest(remote_file_entry);
    const std::string expected_remote_version_digest = sync_manifest_entry_version_digest(remote_file_entry);
    if (!apply_entry.remote_entry_present ||
        apply_entry.remote_entry_kind != SyncManifestEntryKind::File ||
        apply_entry.remote_size_bytes != remote_file_entry.size_bytes ||
        apply_entry.remote_content_sha256 != remote_file_entry.content_sha256 ||
        apply_entry.remote_entry_digest != expected_remote_digest ||
        apply_entry.remote_version_digest != expected_remote_version_digest) {
        return peer_ingestion_fail("apply remote digest/content evidence does not match remote manifest entry");
    }
    if (apply_entry.idempotency_key.empty() ||
        apply_entry.idempotency_key.rfind("sync-local-apply:v1:", 0) != 0) {
        return peer_ingestion_fail("apply entry idempotency key is missing or has the wrong namespace");
    }
    return peer_ingestion_ok();
}

void aggregate_peer_sidecar_session_sweep_counts(SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult& out,
                                                 const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult& file_sweep) {
    out.claimed_rows_considered += file_sweep.claimed_rows_considered;
    out.bytes_considered += file_sweep.bytes_considered;
    out.recovery_groups_considered += file_sweep.recovery_groups_considered;
    out.recovery_groups_attempted += file_sweep.recovery_groups_attempted;
    out.recovery_groups_completed += file_sweep.recovery_groups_completed;
    out.recovery_groups_failed += file_sweep.recovery_groups_failed;
    out.recovery_groups_deferred_by_limit += file_sweep.recovery_groups_deferred_by_limit;
    out.recovery_groups_deferred_expired_lease += file_sweep.recovery_groups_deferred_expired_lease;
    out.recovery_groups_review_required += file_sweep.recovery_groups_review_required;
    out.recovery_groups_review_missing_sidecar += file_sweep.recovery_groups_review_missing_sidecar;
    out.recovery_groups_review_tampered_sidecar += file_sweep.recovery_groups_review_tampered_sidecar;
    out.recovery_groups_review_staged_bytes_mismatch += file_sweep.recovery_groups_review_staged_bytes_mismatch;
    out.claimed_rows_deferred_expired_lease += file_sweep.claimed_rows_deferred_expired_lease;
    out.claimed_rows_review_required += file_sweep.claimed_rows_review_required;
    out.bytes_review_required += file_sweep.bytes_review_required;
    out.review_events_written += file_sweep.review_events_written;
    out.review_events_already_present += file_sweep.review_events_already_present;
    out.bytes_verified += file_sweep.bytes_verified;
    out.receipt_rows_inserted += file_sweep.receipt_rows_inserted;
    out.receipt_rows_reactivated_from_committed_cleaned += file_sweep.receipt_rows_reactivated_from_committed_cleaned;
    out.receipt_rows_already_present += file_sweep.receipt_rows_already_present;
    out.workorder_rows_completed += file_sweep.workorder_rows_completed;
    out.workorder_rows_already_completed += file_sweep.workorder_rows_already_completed;
    out.sweep_incomplete_due_to_limit = out.sweep_incomplete_due_to_limit || file_sweep.sweep_incomplete_due_to_limit;
    out.sweep_incomplete_due_to_expired_lease = out.sweep_incomplete_due_to_expired_lease || file_sweep.sweep_incomplete_due_to_expired_lease;
    out.sweep_incomplete_due_to_review = out.sweep_incomplete_due_to_review || file_sweep.sweep_incomplete_due_to_review;
    out.sweep_incomplete_due_to_ambiguous_apply_input = out.sweep_incomplete_due_to_ambiguous_apply_input ||
                                                        file_sweep.sweep_incomplete_due_to_ambiguous_apply_input;
    out.sweep_incomplete_due_to_ambiguous_remote_file_evidence =
        out.sweep_incomplete_due_to_ambiguous_remote_file_evidence ||
        file_sweep.sweep_incomplete_due_to_ambiguous_remote_file_evidence;
}

void summarize_peer_ingestion_result(SyncSessionCheckpointBoundPeerChunkIngestionResult& out) {
    out.bytes_bound = out.sidecar_acceptance.workorder_binding.bytes_bound;
    out.chunks_written = out.sidecar_acceptance.peer_batch_acceptance.chunks_written;
    out.bytes_verified = out.database_advance.bytes_verified;
    out.receipt_rows_inserted = out.database_advance.receipt_rows_inserted;
    out.receipt_rows_reactivated_from_committed_cleaned = out.database_advance.receipt_rows_reactivated_from_committed_cleaned;
    out.receipt_rows_already_present = out.database_advance.receipt_rows_already_present;
    out.workorder_rows_completed = out.database_advance.workorder_rows_completed;
    out.workorder_rows_already_completed = out.database_advance.workorder_rows_already_completed;
    if (!out.database_advance.content_sha256.empty()) {
        out.content_sha256 = out.database_advance.content_sha256;
    } else {
        out.content_sha256 = out.sidecar_acceptance.peer_batch_acceptance.content_sha256;
    }
}

void summarize_peer_sidecar_recovery_result(SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult& out) {
    out.sidecar_evidence_verified = out.database_advance.sidecar_evidence_verified;
    out.bytes_verified = out.database_advance.bytes_verified;
    out.receipt_rows_inserted = out.database_advance.receipt_rows_inserted;
    out.receipt_rows_reactivated_from_committed_cleaned = out.database_advance.receipt_rows_reactivated_from_committed_cleaned;
    out.receipt_rows_already_present = out.database_advance.receipt_rows_already_present;
    out.workorder_rows_completed = out.database_advance.workorder_rows_completed;
    out.workorder_rows_already_completed = out.database_advance.workorder_rows_already_completed;
    out.content_sha256 = out.database_advance.content_sha256;
}


bool peer_sidecar_review_events_table_exists_or_throw(sqlite3* db) {
    return peer_ingestion_table_exists_or_throw(
        db,
        "sync_session_bound_peer_sidecar_review_events",
        "sync session checkpoint bound peer sidecar review report table probe");
}

bool peer_sidecar_review_event_resolutions_table_exists_or_throw(sqlite3* db) {
    return peer_ingestion_table_exists_or_throw(
        db,
        "sync_session_bound_peer_sidecar_review_event_resolutions",
        "sync session checkpoint bound peer sidecar review resolution table probe");
}

bool peer_sidecar_review_category_is_supported(const std::string& category) {
    return category.empty() ||
           category == "missing-sidecar" ||
           category == "tampered-sidecar" ||
           category == "staged-bytes-mismatch";
}

void add_peer_sidecar_review_event_report_category_count(const std::string& category,
                                                         SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult& out) {
    if (category == "missing-sidecar") {
        ++out.missing_sidecar_events;
    } else if (category == "tampered-sidecar") {
        ++out.tampered_sidecar_events;
    } else if (category == "staged-bytes-mismatch") {
        ++out.staged_bytes_mismatch_events;
    }
}

}  // namespace

SyncValidationResult list_sync_session_checkpoint_bound_peer_sidecar_review_events(
    const SyncSessionCheckpointBoundPeerSidecarReviewEventReportOptions& options,
    SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult& out) {
    out = SyncSessionCheckpointBoundPeerSidecarReviewEventReportResult{};
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.max_events = options.max_events;
    if (options.sqlite_path.empty()) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review report sqlite_path is required");
    }
    if (options.session_id.empty()) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review report session_id is required");
    }
    if (!peer_sidecar_review_category_is_supported(options.review_category)) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review report review_category is not supported");
    }

    NormalizedSyncPath filter_path;
    const bool has_path_filter = !options.path.value.empty();
    if (has_path_filter) {
        SyncValidationResult normalized_path = normalize_sync_relative_path(options.path.value, filter_path);
        if (!normalized_path.ok) {
            return peer_ingestion_fail("sync session checkpoint bound peer sidecar review report path is invalid: " + normalized_path.reason);
        }
    }

    try {
        PeerIngestionSqliteDb db;
        int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(options.sqlite_path.c_str(), db.db.out(), flags, nullptr) != SQLITE_OK) {
            return peer_ingestion_fail(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer sidecar review report could not open sqlite database"));
        }
        peer_ingestion_exec_or_throw(db.db, "PRAGMA foreign_keys=ON;", "sync session checkpoint bound peer sidecar review report enable foreign keys");
        out.review_event_schema_loaded = peer_sidecar_review_events_table_exists_or_throw(db.db);
        if (!out.review_event_schema_loaded) {
            out.report_completed = true;
            return peer_ingestion_ok();
        }
        out.review_event_resolution_schema_loaded = peer_sidecar_review_event_resolutions_table_exists_or_throw(db.db);

        std::string sql =
            "SELECT e.path, e.review_event_idempotency_key, e.review_category, e.review_reason, "
            "e.request_idempotency_key, e.schedule_idempotency_key, e.peer_request_idempotency_key, "
            "e.execution_idempotency_key, e.peer_id, e.peer_session_id, e.worker_id, e.worker_lease_id, "
            "e.chunks_considered, e.bytes_considered, e.first_observed_at_epoch, e.last_observed_at_epoch, e.observations";
        if (out.review_event_resolution_schema_loaded) {
            sql += ", COALESCE(r.resolution_state,''), COALESCE(r.resolution_reason,''), "
                   "COALESCE(r.resolved_by_operator_id,''), COALESCE(r.resolved_at_epoch,0), "
                   "COALESCE(r.workorder_rows_quarantined,0), COALESCE(r.workorder_rows_already_quarantined,0)";
        } else {
            sql += ", '', '', '', 0, 0, 0";
        }
        sql += " FROM sync_session_bound_peer_sidecar_review_events e";
        if (out.review_event_resolution_schema_loaded) {
            sql += " LEFT JOIN sync_session_bound_peer_sidecar_review_event_resolutions r "
                   "ON r.session_id=e.session_id AND r.path=e.path AND r.review_event_idempotency_key=e.review_event_idempotency_key";
        }
        sql += " WHERE e.session_id=?";
        if (has_path_filter) {
            sql += " AND e.path=?";
        }
        if (!options.review_category.empty()) {
            sql += " AND e.review_category=?";
        }
        sql += " ORDER BY e.first_observed_at_epoch ASC, e.path ASC, e.review_category ASC, e.review_event_idempotency_key ASC";
        if (options.max_events != 0) {
            sql += " LIMIT ?";
        }
        sql += ";";

        PeerIngestionSqliteStmt stmt = peer_ingestion_prepare_or_throw(db.db, sql, "sync session checkpoint bound peer sidecar review report query prepare");
        int bind_index = 1;
        peer_ingestion_bind_text_or_throw(stmt.stmt, bind_index++, options.session_id, "sync session checkpoint bound peer sidecar review report bind session");
        if (has_path_filter) {
            peer_ingestion_bind_text_or_throw(stmt.stmt, bind_index++, filter_path.value, "sync session checkpoint bound peer sidecar review report bind path");
        }
        if (!options.review_category.empty()) {
            peer_ingestion_bind_text_or_throw(stmt.stmt, bind_index++, options.review_category, "sync session checkpoint bound peer sidecar review report bind category");
        }
        if (options.max_events != 0) {
            const std::uint64_t query_limit = options.max_events == std::numeric_limits<std::uint64_t>::max()
                                                  ? options.max_events
                                                  : options.max_events + 1;
            peer_ingestion_bind_u64_or_throw(stmt.stmt, bind_index++, query_limit, "sync session checkpoint bound peer sidecar review report bind limit");
        }

        while (true) {
            const int rc = sqlite3_step(stmt.stmt);
            if (rc == SQLITE_DONE) break;
            if (rc != SQLITE_ROW) {
                throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer sidecar review report query"));
            }
            if (options.max_events != 0 && out.events.size() >= options.max_events) {
                out.events_deferred_by_limit = true;
                continue;
            }

            SyncSessionCheckpointBoundPeerSidecarReviewEventRecord record;
            NormalizedSyncPath stored_path;
            SyncValidationResult normalized_stored_path = normalize_sync_relative_path(peer_ingestion_column_text_or_throw(stmt.stmt, 0, "sync session checkpoint bound peer sidecar review report column path"), stored_path);
            if (!normalized_stored_path.ok) {
                throw std::runtime_error("sync session checkpoint bound peer sidecar review report stored path is invalid: " + normalized_stored_path.reason);
            }
            record.path = stored_path;
            record.review_event_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 1, "sync session checkpoint bound peer sidecar review report column event key");
            record.review_category = peer_ingestion_column_text_or_throw(stmt.stmt, 2, "sync session checkpoint bound peer sidecar review report column category");
            record.review_reason = peer_ingestion_column_text_or_throw(stmt.stmt, 3, "sync session checkpoint bound peer sidecar review report column reason");
            record.request_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 4, "sync session checkpoint bound peer sidecar review report column request key");
            record.schedule_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 5, "sync session checkpoint bound peer sidecar review report column schedule key");
            record.peer_request_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 6, "sync session checkpoint bound peer sidecar review report column peer request key");
            record.execution_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 7, "sync session checkpoint bound peer sidecar review report column execution key");
            record.peer_id = peer_ingestion_column_text_or_throw(stmt.stmt, 8, "sync session checkpoint bound peer sidecar review report column peer id");
            record.peer_session_id = peer_ingestion_column_text_or_throw(stmt.stmt, 9, "sync session checkpoint bound peer sidecar review report column peer session");
            record.worker_id = peer_ingestion_column_text_or_throw(stmt.stmt, 10, "sync session checkpoint bound peer sidecar review report column worker");
            record.worker_lease_id = peer_ingestion_column_text_or_throw(stmt.stmt, 11, "sync session checkpoint bound peer sidecar review report column lease");
            record.chunks_considered = peer_ingestion_column_u64_or_throw(stmt.stmt, 12, "sync session checkpoint bound peer sidecar review report column chunks");
            record.bytes_considered = peer_ingestion_column_u64_or_throw(stmt.stmt, 13, "sync session checkpoint bound peer sidecar review report column bytes");
            record.first_observed_at_epoch = peer_ingestion_column_u64_or_throw(stmt.stmt, 14, "sync session checkpoint bound peer sidecar review report column first observed");
            record.last_observed_at_epoch = peer_ingestion_column_u64_or_throw(stmt.stmt, 15, "sync session checkpoint bound peer sidecar review report column last observed");
            record.observations = peer_ingestion_column_u64_or_throw(stmt.stmt, 16, "sync session checkpoint bound peer sidecar review report column observations");
            record.resolution_state = peer_ingestion_column_text_or_throw(stmt.stmt, 17, "sync session checkpoint bound peer sidecar review report column resolution state");
            record.resolution_reason = peer_ingestion_column_text_or_throw(stmt.stmt, 18, "sync session checkpoint bound peer sidecar review report column resolution reason");
            record.resolved_by_operator_id = peer_ingestion_column_text_or_throw(stmt.stmt, 19, "sync session checkpoint bound peer sidecar review report column resolved by");
            record.resolved_at_epoch = peer_ingestion_column_u64_or_throw(stmt.stmt, 20, "sync session checkpoint bound peer sidecar review report column resolved at");
            record.resolved_workorder_rows_quarantined = peer_ingestion_column_u64_or_throw(stmt.stmt, 21, "sync session checkpoint bound peer sidecar review report column rows quarantined");
            record.resolved_workorder_rows_already_quarantined = peer_ingestion_column_u64_or_throw(stmt.stmt, 22, "sync session checkpoint bound peer sidecar review report column rows already quarantined");
            out.total_observations += record.observations;
            add_peer_sidecar_review_event_report_category_count(record.review_category, out);
            if (record.resolution_state == "quarantined") {
                ++out.quarantined_events;
            } else {
                ++out.unresolved_events;
            }
            out.events.push_back(std::move(record));
        }
        out.events_returned = static_cast<std::uint64_t>(out.events.size());
        out.report_completed = true;
        return peer_ingestion_ok();
    } catch (const std::exception& e) {
        return peer_ingestion_fail(std::string("sync session checkpoint bound peer sidecar review report failed: ") + e.what());
    }
}


SyncValidationResult quarantine_sync_session_checkpoint_bound_peer_sidecar_review_event(
    const SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineOptions& options,
    SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineResult& out) {
    out = SyncSessionCheckpointBoundPeerSidecarReviewEventQuarantineResult{};
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.review_event_idempotency_key = options.review_event_idempotency_key;
    out.decision_operator_id = options.decision_operator_id;
    out.decision_reason = options.decision_reason;
    out.quarantine_at_epoch = options.quarantine_at_epoch;

    if (options.sqlite_path.empty()) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review quarantine sqlite_path is required");
    }
    if (options.session_id.empty()) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review quarantine session_id is required");
    }
    if (options.review_event_idempotency_key.empty()) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review quarantine review_event_idempotency_key is required");
    }
    if (options.decision_operator_id.empty()) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review quarantine decision_operator_id is required");
    }
    if (options.decision_reason.empty()) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review quarantine decision_reason is required");
    }
    if (options.quarantine_at_epoch == 0) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review quarantine quarantine_at_epoch must be positive");
    }

    NormalizedSyncPath normalized_path;
    SyncValidationResult normalized_path_result = normalize_sync_relative_path(options.path.value, normalized_path);
    if (!normalized_path_result.ok) {
        return peer_ingestion_fail("sync session checkpoint bound peer sidecar review quarantine path is invalid: " + normalized_path_result.reason);
    }
    out.path = normalized_path;

    struct ReviewEventRow {
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
    } review;

    PeerIngestionSqliteDb db;
    try {
        int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(options.sqlite_path.c_str(), db.db.out(), flags, nullptr) != SQLITE_OK) {
            return peer_ingestion_fail(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer sidecar review quarantine could not open sqlite database"));
        }
        peer_ingestion_exec_or_throw(db.db, "PRAGMA foreign_keys=ON;", "sync session checkpoint bound peer sidecar review quarantine enable foreign keys");
        ensure_peer_sidecar_review_events_schema_or_throw(db.db);
        out.review_event_schema_loaded = true;
        ensure_peer_sidecar_review_event_resolutions_schema_or_throw(db.db);
        out.resolution_schema_loaded = true;

        SyncSqliteTransaction transaction(
            db.db,
            "sync session checkpoint bound peer sidecar review quarantine",
            SyncSqliteTransactionMode::Immediate);

        PeerIngestionSqliteStmt review_stmt = peer_ingestion_prepare_or_throw(db.db,
            "SELECT review_category, review_reason, request_idempotency_key, schedule_idempotency_key, "
            "peer_request_idempotency_key, execution_idempotency_key, peer_id, peer_session_id, "
            "worker_id, worker_lease_id, chunks_considered, bytes_considered "
            "FROM sync_session_bound_peer_sidecar_review_events "
            "WHERE session_id=? AND path=? AND review_event_idempotency_key=?;",
            "sync session checkpoint bound peer sidecar review quarantine event query prepare");
        peer_ingestion_bind_text_or_throw(review_stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar review quarantine bind session");
        peer_ingestion_bind_text_or_throw(review_stmt.stmt, 2, normalized_path.value, "sync session checkpoint bound peer sidecar review quarantine bind path");
        peer_ingestion_bind_text_or_throw(review_stmt.stmt, 3, options.review_event_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine bind event key");
        int rc = sqlite3_step(review_stmt.stmt);
        if (rc == SQLITE_DONE) {
            throw std::runtime_error("sync session checkpoint bound peer sidecar review quarantine review event was not found");
        }
        if (rc != SQLITE_ROW) {
            throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer sidecar review quarantine event query"));
        }
        out.review_event_found = true;
        review.review_category = peer_ingestion_column_text_or_throw(review_stmt.stmt, 0, "sync session checkpoint bound peer sidecar review quarantine column category");
        review.review_reason = peer_ingestion_column_text_or_throw(review_stmt.stmt, 1, "sync session checkpoint bound peer sidecar review quarantine column reason");
        review.request_idempotency_key = peer_ingestion_column_text_or_throw(review_stmt.stmt, 2, "sync session checkpoint bound peer sidecar review quarantine column request key");
        review.schedule_idempotency_key = peer_ingestion_column_text_or_throw(review_stmt.stmt, 3, "sync session checkpoint bound peer sidecar review quarantine column schedule key");
        review.peer_request_idempotency_key = peer_ingestion_column_text_or_throw(review_stmt.stmt, 4, "sync session checkpoint bound peer sidecar review quarantine column peer request key");
        review.execution_idempotency_key = peer_ingestion_column_text_or_throw(review_stmt.stmt, 5, "sync session checkpoint bound peer sidecar review quarantine column execution key");
        review.peer_id = peer_ingestion_column_text_or_throw(review_stmt.stmt, 6, "sync session checkpoint bound peer sidecar review quarantine column peer");
        review.peer_session_id = peer_ingestion_column_text_or_throw(review_stmt.stmt, 7, "sync session checkpoint bound peer sidecar review quarantine column peer session");
        review.worker_id = peer_ingestion_column_text_or_throw(review_stmt.stmt, 8, "sync session checkpoint bound peer sidecar review quarantine column worker");
        review.worker_lease_id = peer_ingestion_column_text_or_throw(review_stmt.stmt, 9, "sync session checkpoint bound peer sidecar review quarantine column lease");
        review.chunks_considered = peer_ingestion_column_u64_or_throw(review_stmt.stmt, 10, "sync session checkpoint bound peer sidecar review quarantine column chunks");
        review.bytes_considered = peer_ingestion_column_u64_or_throw(review_stmt.stmt, 11, "sync session checkpoint bound peer sidecar review quarantine column bytes");
        if (sqlite3_step(review_stmt.stmt) != SQLITE_DONE) {
            throw std::runtime_error("sync session checkpoint bound peer sidecar review quarantine review event is not unique");
        }
        out.review_category = review.review_category;
        out.chunks_considered = review.chunks_considered;
        out.bytes_considered = review.bytes_considered;
        review_stmt.reset();

        auto count_matching_workorders = [&](const std::string& state) -> std::uint64_t {
            PeerIngestionSqliteStmt count_stmt = peer_ingestion_prepare_or_throw(db.db,
                "SELECT COUNT(*) FROM sync_session_resume_transfer_workorders "
                "WHERE session_id=? AND path=? AND request_idempotency_key=? AND schedule_idempotency_key=? "
                "AND peer_request_idempotency_key=? AND execution_idempotency_key=? AND peer_id=? AND peer_session_id=? "
                "AND worker_id=? AND worker_lease_id=? AND work_state=?;",
                "sync session checkpoint bound peer sidecar review quarantine workorder count prepare");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar review quarantine count session");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 2, normalized_path.value, "sync session checkpoint bound peer sidecar review quarantine count path");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 3, review.request_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine count request");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 4, review.schedule_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine count schedule");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 5, review.peer_request_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine count peer request");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 6, review.execution_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine count execution");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 7, review.peer_id, "sync session checkpoint bound peer sidecar review quarantine count peer");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 8, review.peer_session_id, "sync session checkpoint bound peer sidecar review quarantine count peer session");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 9, review.worker_id, "sync session checkpoint bound peer sidecar review quarantine count worker");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 10, review.worker_lease_id, "sync session checkpoint bound peer sidecar review quarantine count lease");
            peer_ingestion_bind_text_or_throw(count_stmt.stmt, 11, state, "sync session checkpoint bound peer sidecar review quarantine count state");
            const int count_rc = sqlite3_step(count_stmt.stmt);
            if (count_rc != SQLITE_ROW) {
                throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer sidecar review quarantine count"));
            }
            return peer_ingestion_column_u64_or_throw(count_stmt.stmt, 0, "sync session checkpoint bound peer sidecar review quarantine count result");
        };

        const std::uint64_t claimed_before = count_matching_workorders("claimed");
        const std::uint64_t quarantined_before = count_matching_workorders("quarantined");
        out.workorder_rows_matched = claimed_before + quarantined_before;
        if (out.workorder_rows_matched == 0) {
            throw std::runtime_error("sync session checkpoint bound peer sidecar review quarantine found no matching claimed or quarantined workorders");
        }

        PeerIngestionSqliteStmt quarantine_stmt = peer_ingestion_prepare_or_throw(db.db,
            "UPDATE sync_session_resume_transfer_workorders SET work_state='quarantined' "
            "WHERE session_id=? AND path=? AND request_idempotency_key=? AND schedule_idempotency_key=? "
            "AND peer_request_idempotency_key=? AND execution_idempotency_key=? AND peer_id=? AND peer_session_id=? "
            "AND worker_id=? AND worker_lease_id=? AND work_state='claimed';",
            "sync session checkpoint bound peer sidecar review quarantine update prepare");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar review quarantine update session");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 2, normalized_path.value, "sync session checkpoint bound peer sidecar review quarantine update path");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 3, review.request_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine update request");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 4, review.schedule_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine update schedule");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 5, review.peer_request_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine update peer request");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 6, review.execution_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine update execution");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 7, review.peer_id, "sync session checkpoint bound peer sidecar review quarantine update peer");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 8, review.peer_session_id, "sync session checkpoint bound peer sidecar review quarantine update peer session");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 9, review.worker_id, "sync session checkpoint bound peer sidecar review quarantine update worker");
        peer_ingestion_bind_text_or_throw(quarantine_stmt.stmt, 10, review.worker_lease_id, "sync session checkpoint bound peer sidecar review quarantine update lease");
        peer_ingestion_step_done_or_throw(quarantine_stmt.stmt, "sync session checkpoint bound peer sidecar review quarantine update");
        out.workorder_rows_quarantined = static_cast<std::uint64_t>(sqlite3_changes(db.db));
        out.workorder_rows_already_quarantined = quarantined_before;
        quarantine_stmt.reset();

        PeerIngestionSqliteStmt resolution_stmt = peer_ingestion_prepare_or_throw(db.db,
            "INSERT OR IGNORE INTO sync_session_bound_peer_sidecar_review_event_resolutions("
            "session_id, path, review_event_idempotency_key, resolution_state, resolution_reason, "
            "resolved_by_operator_id, resolved_at_epoch, workorder_rows_quarantined, workorder_rows_already_quarantined) "
            "VALUES(?,?,?,?,?,?,?,?,?);",
            "sync session checkpoint bound peer sidecar review quarantine resolution insert prepare");
        peer_ingestion_bind_text_or_throw(resolution_stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer sidecar review quarantine resolution bind session");
        peer_ingestion_bind_text_or_throw(resolution_stmt.stmt, 2, normalized_path.value, "sync session checkpoint bound peer sidecar review quarantine resolution bind path");
        peer_ingestion_bind_text_or_throw(resolution_stmt.stmt, 3, options.review_event_idempotency_key, "sync session checkpoint bound peer sidecar review quarantine resolution bind event key");
        peer_ingestion_bind_text_or_throw(resolution_stmt.stmt, 4, "quarantined", "sync session checkpoint bound peer sidecar review quarantine resolution bind state");
        peer_ingestion_bind_text_or_throw(resolution_stmt.stmt, 5, options.decision_reason, "sync session checkpoint bound peer sidecar review quarantine resolution bind reason");
        peer_ingestion_bind_text_or_throw(resolution_stmt.stmt, 6, options.decision_operator_id, "sync session checkpoint bound peer sidecar review quarantine resolution bind operator");
        peer_ingestion_bind_u64_or_throw(resolution_stmt.stmt, 7, options.quarantine_at_epoch, "sync session checkpoint bound peer sidecar review quarantine resolution bind epoch");
        peer_ingestion_bind_u64_or_throw(resolution_stmt.stmt, 8, out.workorder_rows_quarantined, "sync session checkpoint bound peer sidecar review quarantine resolution bind rows quarantined");
        peer_ingestion_bind_u64_or_throw(resolution_stmt.stmt, 9, out.workorder_rows_already_quarantined, "sync session checkpoint bound peer sidecar review quarantine resolution bind rows already quarantined");
        peer_ingestion_step_done_or_throw(resolution_stmt.stmt, "sync session checkpoint bound peer sidecar review quarantine resolution insert");
        out.quarantine_event_written = sqlite3_changes(db.db) > 0;
        out.quarantine_event_already_present = !out.quarantine_event_written;
        resolution_stmt.reset();

        transaction.commit();
        out.transaction_committed = true;
        return peer_ingestion_ok();
    } catch (const std::exception& e) {
        // The schema creation above is outside the resolution transaction, but review resolution and
        // workorder terminalization share one BEGIN IMMEDIATE/COMMIT boundary.
        // The typed guard rolls back the exact transaction generation before this catch runs.
        return peer_ingestion_fail(std::string("sync session checkpoint bound peer sidecar review quarantine failed: ") + e.what());
    }
}

SyncValidationResult ingest_sync_session_checkpoint_bound_peer_chunk_response_batch(
    const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
    const std::vector<std::string>& chunk_bytes,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncSessionCheckpointBoundPeerChunkIngestionResult& out) {
    SyncSessionCheckpointBoundPeerChunkIngestionControlOptions control_options;
    return ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(
        binding_options,
        remote_file_entry,
        apply_entry,
        peer_batch_envelope,
        chunk_bytes,
        write_options,
        control_options,
        out);
}

SyncValidationResult ingest_sync_session_checkpoint_bound_peer_chunk_response_batch_controlled(
    const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
    const std::vector<std::string>& chunk_bytes,
    const SyncChunkReceiptWriteOptions& write_options,
    const SyncSessionCheckpointBoundPeerChunkIngestionControlOptions& control_options,
    SyncSessionCheckpointBoundPeerChunkIngestionResult& out) {
    out = SyncSessionCheckpointBoundPeerChunkIngestionResult{};
    out.sqlite_path = binding_options.sqlite_path;
    out.session_id = binding_options.session_id;
    out.worker_id = binding_options.worker_id;
    out.worker_lease_id = binding_options.worker_lease_id;
    out.expected_execution_idempotency_key = binding_options.expected_execution_idempotency_key;
    out.path = peer_batch_envelope.path;

    try {
        out.sidecar_acceptance_attempted = true;
        SyncValidationResult sidecar_result = accept_sync_session_checkpoint_bound_peer_chunk_response_batch_envelope(
            binding_options,
            remote_file_entry,
            apply_entry,
            peer_batch_envelope,
            chunk_bytes,
            write_options,
            out.sidecar_acceptance);
        out.sidecar_acceptance_completed = sidecar_result.ok && out.sidecar_acceptance.bytes_accepted_after_binding;
        summarize_peer_ingestion_result(out);
        if (!sidecar_result.ok) {
            return peer_ingestion_fail("sync session checkpoint bound peer chunk ingestion sidecar acceptance failed before database advancement: " +
                                       sidecar_result.reason);
        }
        if (!out.sidecar_acceptance.bytes_accepted_after_binding) {
            return peer_ingestion_fail("sync session checkpoint bound peer chunk ingestion sidecar phase did not report bound byte acceptance");
        }

        if (control_options.stop_after_sidecar_acceptance_before_db_advance) {
            out.controlled_stop_after_sidecar_acceptance = true;
            out.recoverable_sidecar_acceptance_without_db_advance = true;
            summarize_peer_ingestion_result(out);
            return peer_ingestion_fail("sync session checkpoint bound peer chunk ingestion controlled stop after sidecar acceptance before database advancement; rerun sidecar recovery to advance accepted sidecars");
        }

        out.database_advance_attempted = true;
        SyncValidationResult advance_result = advance_sync_session_checkpoint_bound_peer_chunk_acceptance(
            binding_options,
            remote_file_entry,
            apply_entry,
            peer_batch_envelope,
            write_options,
            out.database_advance);
        out.database_advance_completed = advance_result.ok && out.database_advance.transaction_committed;
        summarize_peer_ingestion_result(out);
        if (!advance_result.ok) {
            out.recoverable_sidecar_acceptance_without_db_advance = out.sidecar_acceptance_completed;
            return peer_ingestion_fail("sync session checkpoint bound peer chunk ingestion database advancement failed after sidecar acceptance; rerun database advancement against the accepted sidecars: " +
                                       advance_result.reason);
        }
        if (!out.database_advance.transaction_committed) {
            out.recoverable_sidecar_acceptance_without_db_advance = out.sidecar_acceptance_completed;
            return peer_ingestion_fail("sync session checkpoint bound peer chunk ingestion database advancement did not commit after sidecar acceptance");
        }

        out.transport_safe_single_entrypoint_completed = true;
        return peer_ingestion_ok();
    } catch (const std::exception& e) {
        out.recoverable_sidecar_acceptance_without_db_advance = out.sidecar_acceptance_completed && !out.database_advance_completed;
        summarize_peer_ingestion_result(out);
        return peer_ingestion_fail(std::string("sync session checkpoint bound peer chunk ingestion failed: ") + e.what());
    }
}


SyncValidationResult recover_sync_session_checkpoint_bound_peer_chunk_sidecars(
    const SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions& binding_options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncPeerChunkResponseBatchEnvelope& peer_batch_envelope,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult& out) {
    out = SyncSessionCheckpointBoundPeerChunkSidecarRecoveryResult{};
    out.sqlite_path = binding_options.sqlite_path;
    out.session_id = binding_options.session_id;
    out.worker_id = binding_options.worker_id;
    out.worker_lease_id = binding_options.worker_lease_id;
    out.expected_execution_idempotency_key = binding_options.expected_execution_idempotency_key;
    out.path = peer_batch_envelope.path;
    out.transport_payload_not_required = true;

    try {
        out.database_advance_attempted = true;
        SyncValidationResult advance_result = advance_sync_session_checkpoint_bound_peer_chunk_acceptance(
            binding_options,
            remote_file_entry,
            apply_entry,
            peer_batch_envelope,
            write_options,
            out.database_advance);
        out.database_advance_completed = advance_result.ok && out.database_advance.transaction_committed;
        summarize_peer_sidecar_recovery_result(out);
        if (!advance_result.ok) {
            return peer_ingestion_fail(
                "sync session checkpoint bound peer chunk sidecar recovery failed before database advancement completed: " +
                advance_result.reason);
        }
        if (!out.database_advance.transaction_committed) {
            return peer_ingestion_fail("sync session checkpoint bound peer chunk sidecar recovery database advancement did not commit");
        }
        if (!out.database_advance.sidecar_evidence_verified) {
            return peer_ingestion_fail("sync session checkpoint bound peer chunk sidecar recovery did not verify accepted sidecar evidence");
        }

        out.recovery_entrypoint_completed = true;
        return peer_ingestion_ok();
    } catch (const std::exception& e) {
        summarize_peer_sidecar_recovery_result(out);
        return peer_ingestion_fail(std::string("sync session checkpoint bound peer chunk sidecar recovery failed: ") + e.what());
    }
}

SyncValidationResult recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(
    const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult& out) {
    out = SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepResult{};
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.worker_id = options.worker_id;
    out.worker_lease_id = options.worker_lease_id;
    out.path = remote_file_entry.path;
    out.binding_now_epoch = options.binding_now_epoch;
    out.transport_payload_not_required = true;

    SyncValidationResult option_result = validate_peer_sidecar_recovery_sweep_options(
        options,
        "sync session checkpoint bound peer chunk sidecar recovery sweep");
    if (!option_result.ok) return option_result;

    try {
        PeerIngestionSqliteDb db;
        int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(options.sqlite_path.c_str(), db.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer chunk sidecar recovery sweep could not open sqlite database"));
        }

        PeerIngestionSqliteStmt stmt = peer_ingestion_prepare_or_throw(db.db,
            "SELECT chunk_offset, chunk_length, chunk_sha256, request_idempotency_key, "
            "schedule_idempotency_key, peer_request_idempotency_key, execution_idempotency_key, "
            "peer_id, peer_session_id, lease_expires_at_epoch "
            "FROM sync_session_resume_transfer_workorders "
            "WHERE session_id=? AND path=? AND worker_id=? AND worker_lease_id=? AND work_state='claimed' "
            "ORDER BY request_idempotency_key, schedule_idempotency_key, peer_request_idempotency_key, "
            "execution_idempotency_key, peer_id, peer_session_id, chunk_offset;",
            "sync session checkpoint bound peer chunk sidecar recovery sweep prepare claimed workorder query");
        peer_ingestion_bind_text_or_throw(stmt.stmt, 1, options.session_id, "sync session checkpoint bound peer chunk sidecar recovery sweep bind session");
        peer_ingestion_bind_text_or_throw(stmt.stmt, 2, remote_file_entry.path.value, "sync session checkpoint bound peer chunk sidecar recovery sweep bind path");
        peer_ingestion_bind_text_or_throw(stmt.stmt, 3, options.worker_id, "sync session checkpoint bound peer chunk sidecar recovery sweep bind worker");
        peer_ingestion_bind_text_or_throw(stmt.stmt, 4, options.worker_lease_id, "sync session checkpoint bound peer chunk sidecar recovery sweep bind lease");

        std::map<PeerSidecarSweepGroupKey, PeerSidecarSweepGroupCandidate> recoverable_groups;
        std::map<PeerSidecarSweepGroupKey, PeerSidecarSweepGroupCandidate> expired_lease_groups;
        while (true) {
            const int rc = sqlite3_step(stmt.stmt);
            if (rc == SQLITE_DONE) break;
            if (rc != SQLITE_ROW) {
                throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer chunk sidecar recovery sweep claimed workorder query failed"));
            }

            SyncChunkRange chunk;
            chunk.offset = peer_ingestion_column_u64_or_throw(stmt.stmt, 0, "sync session checkpoint bound peer chunk sidecar recovery sweep chunk offset");
            chunk.length = peer_ingestion_column_u64_or_throw(stmt.stmt, 1, "sync session checkpoint bound peer chunk sidecar recovery sweep chunk length");
            chunk.sha256 = peer_ingestion_column_text_or_throw(stmt.stmt, 2, "sync session checkpoint bound peer chunk sidecar recovery sweep chunk sha");
            PeerSidecarSweepGroupKey key;
            key.request_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 3, "sync session checkpoint bound peer chunk sidecar recovery sweep request key");
            key.schedule_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 4, "sync session checkpoint bound peer chunk sidecar recovery sweep schedule key");
            key.peer_request_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 5, "sync session checkpoint bound peer chunk sidecar recovery sweep peer request key");
            key.execution_idempotency_key = peer_ingestion_column_text_or_throw(stmt.stmt, 6, "sync session checkpoint bound peer chunk sidecar recovery sweep execution key");
            key.peer_id = peer_ingestion_column_text_or_throw(stmt.stmt, 7, "sync session checkpoint bound peer chunk sidecar recovery sweep peer id");
            key.peer_session_id = peer_ingestion_column_text_or_throw(stmt.stmt, 8, "sync session checkpoint bound peer chunk sidecar recovery sweep peer session id");
            const std::uint64_t lease_expires_at_epoch = peer_ingestion_column_u64_or_throw(stmt.stmt, 9, "sync session checkpoint bound peer chunk sidecar recovery sweep lease expires");

            ++out.claimed_rows_considered;
            out.bytes_considered += chunk.length;
            if (options.require_live_lease && options.binding_now_epoch >= lease_expires_at_epoch) {
                add_peer_sidecar_sweep_candidate_chunk(expired_lease_groups, key, chunk, lease_expires_at_epoch);
                ++out.claimed_rows_deferred_expired_lease;
                out.bytes_deferred_expired_lease += chunk.length;
            } else {
                add_peer_sidecar_sweep_candidate_chunk(recoverable_groups, key, chunk, lease_expires_at_epoch);
            }
        }

        out.sweep_query_loaded = true;
        out.recovery_groups_considered = static_cast<std::uint64_t>(recoverable_groups.size() + expired_lease_groups.size());

        for (const auto& entry : expired_lease_groups) {
            SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult group_result = make_deferred_peer_sidecar_sweep_group_result(
                remote_file_entry.path,
                entry.first,
                entry.second,
                "deferred: worker lease expired before sidecar recovery sweep could safely advance DB rows");
            group_result.deferred_by_expired_lease = true;
            ++out.recovery_groups_deferred_expired_lease;
            out.groups.push_back(std::move(group_result));
        }

        const std::string remote_entry_digest = sync_manifest_entry_digest(remote_file_entry);
        const std::string remote_version_digest = sync_manifest_entry_version_digest(remote_file_entry);
        std::uint64_t group_index = 0;
        for (const auto& entry : recoverable_groups) {
            ++group_index;
            const PeerSidecarSweepGroupKey& key = entry.first;
            const PeerSidecarSweepGroupCandidate& candidate = entry.second;
            const std::vector<SyncChunkRange>& chunks = candidate.chunks;
            if (options.max_recovery_groups != 0 && group_index > options.max_recovery_groups) {
                SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult group_result = make_deferred_peer_sidecar_sweep_group_result(
                    remote_file_entry.path,
                    key,
                    candidate,
                    "deferred: recovery sweep max_recovery_groups limit reached before this group was attempted");
                group_result.deferred_by_limit = true;
                ++out.recovery_groups_deferred_by_limit;
                out.groups.push_back(std::move(group_result));
                continue;
            }

            SyncPeerChunkResponseBatchEnvelope envelope;
            envelope.path = remote_file_entry.path;
            envelope.request_idempotency_key = key.request_idempotency_key;
            envelope.schedule_idempotency_key = key.schedule_idempotency_key;
            envelope.peer_request_idempotency_key = key.peer_request_idempotency_key;
            envelope.peer_response_batch_idempotency_key = "sync-resume-peer-response-batch:v1:sweep-" + sha256_hex(length_prefixed_security_tuple("anonsync-sync-sidecar-recovery-sweep-peer-batch-v1", {
                {"path", remote_file_entry.path.value},
                {"request_key", key.request_idempotency_key},
                {"schedule_key", key.schedule_idempotency_key},
                {"peer_request_key", key.peer_request_idempotency_key},
                {"execution_key", key.execution_idempotency_key},
                {"peer_id", key.peer_id},
                {"peer_session_id", key.peer_session_id}
            }));
            envelope.batch_idempotency_key = "sync-resume-chunk-response-batch:v1:sweep-" + sha256_hex(length_prefixed_security_tuple("anonsync-sync-sidecar-recovery-sweep-batch-v1", {
                {"path", remote_file_entry.path.value},
                {"request_key", key.request_idempotency_key},
                {"execution_key", key.execution_idempotency_key},
                {"peer_request_key", key.peer_request_idempotency_key}
            }));
            envelope.peer_id = key.peer_id;
            envelope.peer_session_id = key.peer_session_id;
            envelope.remote_entry_digest = remote_entry_digest;
            envelope.remote_version_digest = remote_version_digest;
            envelope.apply_entry_idempotency_key = apply_entry.idempotency_key;
            envelope.response_count = static_cast<std::uint64_t>(chunks.size());

            SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepGroupResult group_result;
            group_result.path = remote_file_entry.path;
            group_result.request_idempotency_key = key.request_idempotency_key;
            group_result.schedule_idempotency_key = key.schedule_idempotency_key;
            group_result.peer_request_idempotency_key = key.peer_request_idempotency_key;
            group_result.execution_idempotency_key = key.execution_idempotency_key;
            group_result.peer_id = key.peer_id;
            group_result.peer_session_id = key.peer_session_id;

            for (const auto& chunk : chunks) {
                SyncChunkResponseEnvelope response;
                response.path = remote_file_entry.path;
                response.request_idempotency_key = key.request_idempotency_key;
                response.response_idempotency_key = peer_sidecar_sweep_response_key(key, chunk, remote_file_entry.path);
                response.remote_entry_digest = remote_entry_digest;
                response.remote_version_digest = remote_version_digest;
                response.apply_entry_idempotency_key = apply_entry.idempotency_key;
                response.offset = chunk.offset;
                response.length = chunk.length;
                response.chunk_sha256 = chunk.sha256;
                envelope.responses.push_back(std::move(response));
                envelope.total_bytes += chunk.length;
                ++group_result.chunks_considered;
                group_result.bytes_considered += chunk.length;
            }

            SyncSessionCheckpointResumePeerResponseWorkorderClaimBindingOptions binding;
            binding.sqlite_path = options.sqlite_path;
            binding.session_id = options.session_id;
            binding.worker_id = options.worker_id;
            binding.worker_lease_id = options.worker_lease_id;
            binding.expected_execution_idempotency_key = key.execution_idempotency_key;
            binding.binding_now_epoch = options.binding_now_epoch;
            binding.require_live_lease = options.require_live_lease;

            group_result.recovery_attempted = true;
            out.recovery_attempted = true;
            ++out.recovery_groups_attempted;
            SyncValidationResult recovery_result = recover_sync_session_checkpoint_bound_peer_chunk_sidecars(binding,
                                                                                                            remote_file_entry,
                                                                                                            apply_entry,
                                                                                                            envelope,
                                                                                                            write_options,
                                                                                                            group_result.recovery);
            group_result.recovery_completed = recovery_result.ok && group_result.recovery.recovery_entrypoint_completed;
            group_result.bytes_verified = group_result.recovery.bytes_verified;
            group_result.workorder_rows_completed = group_result.recovery.workorder_rows_completed;
            group_result.workorder_rows_already_completed = group_result.recovery.workorder_rows_already_completed;
            if (group_result.recovery_completed) {
                ++out.recovery_groups_completed;
                out.bytes_verified += group_result.recovery.bytes_verified;
                out.receipt_rows_inserted += group_result.recovery.receipt_rows_inserted;
                out.receipt_rows_reactivated_from_committed_cleaned += group_result.recovery.receipt_rows_reactivated_from_committed_cleaned;
                out.receipt_rows_already_present += group_result.recovery.receipt_rows_already_present;
                out.workorder_rows_completed += group_result.recovery.workorder_rows_completed;
                out.workorder_rows_already_completed += group_result.recovery.workorder_rows_already_completed;
            } else {
                ++out.recovery_groups_failed;
                group_result.failure_reason = recovery_result.reason;
                const PeerSidecarRecoveryReviewClassification classification = classify_peer_sidecar_recovery_failure(recovery_result.reason);
                apply_peer_sidecar_recovery_review_classification(
                    classification,
                    candidate,
                    group_result,
                    out);
                if (classification.review_required) {
                    const PeerSidecarReviewEventPersistResult review_event = persist_peer_sidecar_recovery_review_event(
                        options,
                        remote_file_entry.path,
                        key,
                        candidate,
                        classification);
                    group_result.review_event_idempotency_key = review_event.review_event_idempotency_key;
                    group_result.review_event_persisted = review_event.written;
                    group_result.review_event_already_present = review_event.already_present;
                    if (review_event.written) ++out.review_events_written;
                    if (review_event.already_present) ++out.review_events_already_present;
                }
            }
            out.groups.push_back(std::move(group_result));
        }

        out.sweep_incomplete_due_to_limit = out.recovery_groups_deferred_by_limit != 0;
        out.sweep_incomplete_due_to_expired_lease = out.recovery_groups_deferred_expired_lease != 0;
        out.sweep_incomplete_due_to_review = out.recovery_groups_review_required != 0;
        out.sweep_completed = out.recovery_groups_failed == 0 &&
                              out.recovery_groups_deferred_by_limit == 0 &&
                              out.recovery_groups_deferred_expired_lease == 0 &&
                              out.recovery_groups_review_required == 0;
        if (out.recovery_groups_failed != 0) {
            return peer_ingestion_fail("sync session checkpoint bound peer chunk sidecar recovery sweep left one or more claimed sidecar groups unrecovered");
        }
        return peer_ingestion_ok();
    } catch (const std::exception& e) {
        return peer_ingestion_fail(std::string("sync session checkpoint bound peer chunk sidecar recovery sweep failed: ") + e.what());
    }
}

SyncValidationResult load_sync_session_checkpoint_bound_peer_chunk_sidecar_recovery_checkpoint_evidence(
    const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult& out) {
    out = SyncSessionCheckpointBoundPeerChunkSidecarRecoveryCheckpointEvidenceResult{};
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.worker_id = options.worker_id;
    out.worker_lease_id = options.worker_lease_id;
    out.transport_payload_not_required = true;

    SyncValidationResult option_result = validate_peer_sidecar_recovery_sweep_options(
        options,
        "sync session checkpoint bound peer chunk sidecar recovery checkpoint evidence loader");
    if (!option_result.ok) return option_result;

    try {
        PeerIngestionSqliteDb db;
        int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(options.sqlite_path.c_str(), db.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(peer_ingestion_sqlite_message(db.db, "sync session checkpoint bound peer sidecar recovery checkpoint evidence loader could not open sqlite database"));
        }

        classify_archived_checkpoint_sidecar_hydration_backfill_or_throw(db.db, out);

        const std::vector<NormalizedSyncPath> claimed_paths = peer_sidecar_claimed_workorder_paths_for_session_or_throw(options);
        out.claimed_workorder_paths_considered = static_cast<std::uint64_t>(claimed_paths.size());
        for (const auto& path : claimed_paths) {
            SyncLocalApplyPlanEntry apply_entry;
            const bool apply_loaded = load_peer_sidecar_apply_entry_for_path_or_throw(db.db, options, path, apply_entry);

            SyncManifestEntry remote_entry;
            std::uint64_t chunks_loaded_for_entry = 0;
            std::uint64_t lineage_rows_loaded_for_entry = 0;
            bool missing_lineage_rows = false;
            const bool remote_loaded = load_peer_sidecar_remote_file_entry_for_path_or_throw(db.db,
                                                                                            options,
                                                                                            path,
                                                                                            remote_entry,
                                                                                            chunks_loaded_for_entry,
                                                                                            lineage_rows_loaded_for_entry,
                                                                                            missing_lineage_rows);
            if (apply_loaded && remote_loaded) {
                SyncValidationResult hydrated_evidence_result = validate_peer_sidecar_remote_apply_recovery_evidence(remote_entry, apply_entry);
                if (!hydrated_evidence_result.ok) {
                    ++out.remote_apply_evidence_mismatch_paths;
                    out.checkpoint_evidence_mismatch_detected = true;
                }
            }
            if (apply_loaded) {
                out.apply_entries.push_back(std::move(apply_entry));
                ++out.apply_entries_loaded;
            }
            if (remote_loaded) {
                if (remote_entry.kind == SyncManifestEntryKind::File) {
                    out.remote_file_entries.push_back(std::move(remote_entry));
                    ++out.remote_file_entries_loaded;
                }
            } else if (missing_lineage_rows) {
                ++out.remote_file_entries_missing_lineage_rows;
                ++out.archived_checkpoint_claimed_paths_blocked_by_missing_lineage;
                out.archived_checkpoint_migration_backfill_blocked_missing_lineage = true;
                if (out.archived_checkpoint_migration_backfill_reason.empty() ||
                    out.archived_checkpoint_exact_startup_hydration_supported) {
                    out.archived_checkpoint_migration_backfill_reason = "claimed sidecar recovery path lacks exact manifest lineage rows";
                }
            }
            out.manifest_chunks_loaded += chunks_loaded_for_entry;
            out.manifest_lineage_rows_loaded += lineage_rows_loaded_for_entry;
        }
        if (out.remote_file_entries_missing_lineage_rows != 0) {
            out.archived_checkpoint_migration_backfill_required = true;
            out.archived_checkpoint_exact_startup_hydration_supported = false;
        }
        out.checkpoint_evidence_loaded = true;
        return peer_ingestion_ok();
    } catch (const std::exception& e) {
        return peer_ingestion_fail(std::string("sync session checkpoint bound peer chunk sidecar recovery checkpoint evidence loader failed: ") + e.what());
    }
}

SyncValidationResult recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_session(
    const SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions& options,
    const std::vector<SyncManifestEntry>& remote_file_entries,
    const std::vector<SyncLocalApplyPlanEntry>& apply_entries,
    const SyncChunkReceiptWriteOptions& write_options,
    SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult& out) {
    out = SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepResult{};
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.worker_id = options.worker_id;
    out.worker_lease_id = options.worker_lease_id;
    out.binding_now_epoch = options.binding_now_epoch;
    out.transport_payload_not_required = true;

    SyncValidationResult option_result = validate_peer_sidecar_recovery_sweep_options(
        options,
        "sync session checkpoint bound peer chunk sidecar recovery session sweep");
    if (!option_result.ok) return option_result;

    try {
        out.session_sweep_attempted = true;

        const std::vector<NormalizedSyncPath> claimed_workorder_paths =
            peer_sidecar_claimed_workorder_paths_for_session_or_throw(options);
        out.claimed_workorder_paths_considered = static_cast<std::uint64_t>(claimed_workorder_paths.size());
        const std::map<std::string, std::uint64_t> apply_path_counts =
            peer_sidecar_remote_byte_apply_path_counts(apply_entries);
        const std::map<std::string, std::uint64_t> remote_file_path_counts =
            peer_sidecar_remote_file_path_counts(remote_file_entries);
        std::set<std::string> claimed_paths;
        std::set<std::string> ambiguous_apply_paths;
        std::set<std::string> ambiguous_remote_paths_reported;
        for (const auto& claimed_path : claimed_workorder_paths) {
            claimed_paths.insert(claimed_path.value);
            const auto apply_count_it = apply_path_counts.find(claimed_path.value);
            const std::uint64_t apply_count = apply_count_it == apply_path_counts.end() ? 0 : apply_count_it->second;
            if (apply_count == 0) {
                SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepFileResult missing_apply_result;
                missing_apply_result.path = claimed_path;
                missing_apply_result.missing_apply_input = true;
                missing_apply_result.failure_reason =
                    "missing caller-supplied remote-byte apply entry for claimed sidecar recovery workorder path";
                ++out.claimed_workorder_paths_missing_apply_input;
                out.sweep_incomplete_due_to_missing_apply_input = true;
                out.files.push_back(std::move(missing_apply_result));
                continue;
            }
            if (apply_count > 1) {
                ambiguous_apply_paths.insert(claimed_path.value);
                SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepFileResult ambiguous_apply_result;
                ambiguous_apply_result.path = claimed_path;
                ambiguous_apply_result.ambiguous_apply_input = true;
                ambiguous_apply_result.failure_reason =
                    "ambiguous caller-supplied remote-byte apply entries for claimed sidecar recovery workorder path";
                ++out.files_ambiguous_apply_input;
                out.sweep_incomplete_due_to_ambiguous_apply_input = true;
                out.files.push_back(std::move(ambiguous_apply_result));
            }
        }

        for (const auto& apply_entry : apply_entries) {
            SyncSessionCheckpointBoundPeerChunkSidecarRecoverySessionSweepFileResult file_result;
            file_result.path = apply_entry.path;
            file_result.file_input_considered = true;
            ++out.file_inputs_considered;

            if (!peer_sidecar_apply_entry_routes_remote_file_bytes_to_staging(apply_entry)) {
                file_result.skipped_non_fetch_stage = true;
                ++out.files_skipped_non_fetch_stage;
                out.files.push_back(std::move(file_result));
                continue;
            }

            const bool claimed_path_present = claimed_paths.count(apply_entry.path.value) != 0;
            if (claimed_path_present && ambiguous_apply_paths.count(apply_entry.path.value) != 0) {
                // A claimed path with more than one remote-byte apply input is already represented
                // above as a typed startup-recovery incompletion. Do not let an arbitrary duplicate
                // drive sidecar recovery or double-count a file sweep.
                continue;
            }

            const auto remote_count_it = remote_file_path_counts.find(apply_entry.path.value);
            const std::uint64_t remote_file_count = remote_count_it == remote_file_path_counts.end() ? 0 : remote_count_it->second;
            if (remote_file_count == 0) {
                file_result.missing_remote_file_evidence = true;
                file_result.failure_reason = "missing caller-supplied remote manifest entry for claimed sidecar recovery workorder path";
                ++out.files_missing_remote_file_evidence;
                out.sweep_incomplete_due_to_missing_remote_file_evidence = true;
                out.files.push_back(std::move(file_result));
                continue;
            }
            if (remote_file_count > 1) {
                if (ambiguous_remote_paths_reported.insert(apply_entry.path.value).second) {
                    file_result.ambiguous_remote_file_evidence = true;
                    file_result.failure_reason = "ambiguous caller-supplied remote manifest entries for claimed sidecar recovery workorder path";
                    ++out.files_ambiguous_remote_file_evidence;
                    out.sweep_incomplete_due_to_ambiguous_remote_file_evidence = true;
                    out.files.push_back(std::move(file_result));
                }
                continue;
            }

            const SyncManifestEntry* remote_file_entry = find_peer_sidecar_remote_file_by_path(remote_file_entries, apply_entry.path);
            if (remote_file_entry == nullptr) {
                file_result.missing_remote_file_evidence = true;
                file_result.failure_reason = "missing caller-supplied remote manifest entry for claimed sidecar recovery workorder path";
                ++out.files_missing_remote_file_evidence;
                out.sweep_incomplete_due_to_missing_remote_file_evidence = true;
                out.files.push_back(std::move(file_result));
                continue;
            }

            SyncValidationResult recovery_evidence_result = validate_peer_sidecar_remote_apply_recovery_evidence(*remote_file_entry, apply_entry);
            if (!recovery_evidence_result.ok) {
                file_result.remote_apply_evidence_mismatch = true;
                file_result.failure_reason = "remote/apply recovery evidence mismatch: " + recovery_evidence_result.reason;
                ++out.files_remote_apply_evidence_mismatch;
                out.sweep_incomplete_due_to_remote_apply_evidence_mismatch = true;
                out.files.push_back(std::move(file_result));
                continue;
            }

            if (options.max_recovery_groups != 0 && out.recovery_groups_attempted >= options.max_recovery_groups) {
                file_result.deferred_by_group_limit = true;
                file_result.failure_reason = "deferred: session sweep max_recovery_groups limit reached before this file was attempted";
                ++out.files_deferred_by_group_limit;
                out.sweep_incomplete_due_to_limit = true;
                out.files.push_back(std::move(file_result));
                continue;
            }

            SyncSessionCheckpointBoundPeerChunkSidecarRecoverySweepOptions file_options = options;
            if (options.max_recovery_groups != 0) {
                file_options.max_recovery_groups = options.max_recovery_groups - out.recovery_groups_attempted;
            }

            file_result.file_sweep_attempted = true;
            ++out.files_attempted;
            SyncValidationResult file_sweep_result = recover_sync_session_checkpoint_bound_peer_chunk_sidecars_for_file(file_options,
                                                                                                                        *remote_file_entry,
                                                                                                                        apply_entry,
                                                                                                                        write_options,
                                                                                                                        file_result.file_sweep);
            aggregate_peer_sidecar_session_sweep_counts(out, file_result.file_sweep);
            file_result.review_events_written = file_result.file_sweep.review_events_written;
            file_result.review_events_already_present = file_result.file_sweep.review_events_already_present;
            file_result.file_sweep_completed = file_sweep_result.ok && file_result.file_sweep.sweep_completed;
            if (file_result.file_sweep_completed) {
                ++out.files_completed;
            } else if (!file_sweep_result.ok) {
                ++out.files_failed;
                file_result.failure_reason = file_sweep_result.reason;
                if (file_result.file_sweep.sweep_incomplete_due_to_review) {
                    file_result.review_required = true;
                    ++out.files_review_required;
                }
            } else {
                if (file_result.file_sweep.sweep_incomplete_due_to_limit) {
                    file_result.deferred_by_group_limit = true;
                }
                if (file_result.file_sweep.sweep_incomplete_due_to_review) {
                    file_result.review_required = true;
                    ++out.files_review_required;
                }
                file_result.failure_reason = "incomplete: file sweep deferred or review-blocked at least one recovery group";
            }
            out.files.push_back(std::move(file_result));
        }

        out.session_sweep_completed = out.files_failed == 0 &&
                                      out.files_deferred_by_group_limit == 0 &&
                                      out.files_review_required == 0 &&
                                      out.claimed_workorder_paths_missing_apply_input == 0 &&
                                      out.files_missing_remote_file_evidence == 0 &&
                                      out.files_ambiguous_apply_input == 0 &&
                                      out.files_ambiguous_remote_file_evidence == 0 &&
                                      out.files_remote_apply_evidence_mismatch == 0 &&
                                      out.recovery_groups_failed == 0 &&
                                      out.recovery_groups_deferred_by_limit == 0 &&
                                      out.recovery_groups_deferred_expired_lease == 0 &&
                                      out.recovery_groups_review_required == 0;
        out.sweep_incomplete_due_to_limit = out.sweep_incomplete_due_to_limit ||
                                            out.files_deferred_by_group_limit != 0 ||
                                            out.recovery_groups_deferred_by_limit != 0;
        out.sweep_incomplete_due_to_expired_lease = out.sweep_incomplete_due_to_expired_lease ||
                                                    out.recovery_groups_deferred_expired_lease != 0;
        out.sweep_incomplete_due_to_review = out.sweep_incomplete_due_to_review ||
                                             out.files_review_required != 0 ||
                                             out.recovery_groups_review_required != 0;
        out.sweep_incomplete_due_to_missing_apply_input = out.sweep_incomplete_due_to_missing_apply_input ||
                                                          out.claimed_workorder_paths_missing_apply_input != 0;
        out.sweep_incomplete_due_to_missing_remote_file_evidence = out.sweep_incomplete_due_to_missing_remote_file_evidence ||
                                                                   out.files_missing_remote_file_evidence != 0;
        out.sweep_incomplete_due_to_ambiguous_apply_input = out.sweep_incomplete_due_to_ambiguous_apply_input ||
                                                            out.files_ambiguous_apply_input != 0;
        out.sweep_incomplete_due_to_ambiguous_remote_file_evidence =
            out.sweep_incomplete_due_to_ambiguous_remote_file_evidence ||
            out.files_ambiguous_remote_file_evidence != 0;
        out.sweep_incomplete_due_to_remote_apply_evidence_mismatch =
            out.sweep_incomplete_due_to_remote_apply_evidence_mismatch ||
            out.files_remote_apply_evidence_mismatch != 0;
        if (out.files_failed != 0 || out.recovery_groups_failed != 0) {
            return peer_ingestion_fail("sync session checkpoint bound peer chunk sidecar recovery session sweep left one or more files unrecovered");
        }
        return peer_ingestion_ok();
    } catch (const std::exception& e) {
        return peer_ingestion_fail(std::string("sync session checkpoint bound peer chunk sidecar recovery session sweep failed: ") + e.what());
    }
}

}  // namespace anonsync
