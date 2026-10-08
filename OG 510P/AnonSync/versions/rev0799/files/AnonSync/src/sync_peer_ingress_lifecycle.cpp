#include "anonsync_core.hpp"
#include "anonsync_core_internal.hpp"
#include "sync_sqlite_support.hpp"
#include "sync_sqlite_runtime.hpp"
#include "sync_peer_ingress_reconciliation.hpp"
#include "sync_peer_ingress_claim.hpp"
#include "sync_peer_ingress_projection.hpp"
#include "sync_peer_ingress_wire.hpp"
#include "sync_peer_ingress_payload_store.hpp"
#include "sync_peer_ingress_retention.hpp"
#include "sync_peer_ingress_schema.hpp"
#include "sqlite_path_security.hpp"

#include <algorithm>
#include <atomic>
#include <cctype>
#include <chrono>
#include <filesystem>
#include <functional>
#include <exception>
#include <iostream>
#include <memory>
#include <optional>
#include <thread>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {
namespace {

namespace fs = std::filesystem;

SyncValidationResult ok_result() {
    return {true, ""};
}

SyncValidationResult fail_result(const std::string& reason) {
    return {false, reason};
}

bool valid_sync_id(const std::string& value) {
    return sync_internal_valid_sync_id(value);
}

fs::path absolute_lexically_normal_path_or_throw(const std::string& raw_path, const std::string& label) {
    return sync_internal_absolute_lexically_normal_path_or_throw(raw_path, label);
}

std::string u64_string(std::uint64_t value) {
    return std::to_string(value);
}

SyncValidationResult resolve_peer_transport_frame_limit(
    std::uint64_t max_frame_bytes,
    std::uint64_t max_canonical_payload_bytes,
    std::uint64_t& out,
    const std::string& label) {
    out = 0;
    if (max_frame_bytes == 0) {
        return fail_result(label + " max_frame_bytes must be positive");
    }
    if (max_canonical_payload_bytes == 0) {
        return fail_result(label + " max_canonical_payload_bytes must be positive");
    }
    out = std::min(max_frame_bytes, max_canonical_payload_bytes);
    return ok_result();
}

void publish_peer_transport_enqueue_compatibility(
    SyncPeerTransportIngressEnqueueResult& out) {
    out.canonical_payload_codec_version = out.payload_frame_codec_version;
    out.canonical_payload_bytes = out.payload_frame_bytes;
    out.canonical_payload_sha256 = out.payload_frame_sha256;
    out.canonical_payload_persisted = out.payload_frame_stored ||
                                      out.payload_frame_already_present;
    out.canonical_payload_reused = out.payload_frame_already_present;
}

void publish_peer_transport_load_compatibility(
    SyncPeerTransportIngressPayloadLoadResult& out) {
    out.durable_payload_present = out.payload_found;
    out.canonical_payload_hash_checked = out.frame_digest_checked;
    out.canonical_payload_decoded = out.canonical_frame_decoded;
    out.canonical_payload_codec_version = out.codec_version;
    out.canonical_payload_bytes = out.canonical_frame_bytes;
    out.canonical_payload_sha256 = out.canonical_frame_sha256;
    out.payload.transport_envelope = out.transport_envelope;
    out.payload.chunk_bytes = out.chunk_bytes;
}

void publish_peer_transport_process_compatibility(
    SyncPeerTransportIngressProcessResult& out) {
    out.durable_payload_loaded = out.durable_payload_checked && !out.durable_payload_missing;
    out.canonical_payload_hash_checked = out.durable_payload_checked;
    out.canonical_payload_decoded = out.durable_payload_checked;
    out.caller_payload_matches_durable = out.durable_payload_matches_submission;
    out.canonical_payload_codec_version = out.durable_payload_codec_version;
    out.canonical_payload_bytes = out.durable_payload_frame_bytes;
    out.canonical_payload_sha256 = out.durable_payload_frame_sha256;
}

struct PeerTransportEnqueueCompatibilityPublisher final {
    SyncPeerTransportIngressEnqueueResult& out;
    ~PeerTransportEnqueueCompatibilityPublisher() noexcept {
        try { publish_peer_transport_enqueue_compatibility(out); } catch (...) {}
    }
};

struct PeerTransportLoadCompatibilityPublisher final {
    SyncPeerTransportIngressPayloadLoadResult& out;
    ~PeerTransportLoadCompatibilityPublisher() noexcept {
        try { publish_peer_transport_load_compatibility(out); } catch (...) {}
    }
};

struct PeerTransportProcessCompatibilityPublisher final {
    SyncPeerTransportIngressProcessResult& out;
    ~PeerTransportProcessCompatibilityPublisher() noexcept {
        try { publish_peer_transport_process_compatibility(out); } catch (...) {}
    }
};

std::uint64_t checked_peer_transport_epoch_add_or_throw(std::uint64_t base_epoch,
                                                         std::uint64_t increment,
                                                         const std::string& label) {
    if (increment > std::numeric_limits<std::uint64_t>::max() - base_epoch) {
        throw std::runtime_error(label + " overflows uint64 epoch range");
    }
    const std::uint64_t result = base_epoch + increment;
    (void)u64_to_sqlite_i64_or_throw(result, label);
    return result;
}

std::uint64_t checked_peer_transport_counter_add_or_throw(
    std::uint64_t left,
    std::uint64_t right,
    const std::string& label) {
    if (right > std::numeric_limits<std::uint64_t>::max() - left) {
        throw std::runtime_error(label + " overflows uint64 counter range");
    }
    return left + right;
}

SyncValidationResult validate_peer_transport_envelope_bounds(const SyncPeerChunkResponseBatchEnvelope& batch,
                                                              std::uint64_t max_response_count,
                                                              std::uint64_t max_total_bytes,
                                                              std::uint64_t max_chunk_bytes,
                                                              const std::string& label) {
    return sync_internal_validate_peer_transport_envelope_bounds(batch,
                                                                 max_response_count,
                                                                 max_total_bytes,
                                                                 max_chunk_bytes,
                                                                 label);
}

}  // namespace

SyncValidationResult validate_peer_transport_ingress_queue_options(const std::string& sqlite_path,
                                                                   const std::string& session_id,
                                                                   std::uint64_t now_epoch,
                                                                   const std::string& label) {
    if (sqlite_path.empty()) return fail_result(label + " sqlite_path is required");
    if (!valid_sync_id(session_id)) return fail_result(label + " session_id must be lowercase portable sync id");
    if (now_epoch == 0) return fail_result(label + " time epoch must be positive");
    return ok_result();
}

SyncValidationResult validate_peer_transport_ingress_retry_options(std::uint64_t max_attempts,
                                                                   std::uint64_t retry_backoff_seconds,
                                                                   const std::string& label) {
    if (max_attempts == 0) return fail_result(label + " max_attempts must be positive");
    if (retry_backoff_seconds == 0) return fail_result(label + " retry_backoff_seconds must be positive");
    return ok_result();
}

SyncValidationResult validate_peer_transport_sqlite_busy_timeout(std::uint64_t timeout_ms,
                                                                  const std::string& label) {
    if (timeout_ms > kSyncPeerTransportMaxSqliteBusyTimeoutMs) {
        return fail_result(label + " sqlite_busy_timeout_ms exceeds " +
                           std::to_string(kSyncPeerTransportMaxSqliteBusyTimeoutMs));
    }
    return ok_result();
}

SyncValidationResult validate_peer_transport_ingress_process_options(const SyncPeerTransportIngressProcessOptions& options) {
    SyncValidationResult base = validate_peer_transport_ingress_queue_options(options.sqlite_path,
                                                                               options.session_id,
                                                                               options.process_now_epoch,
                                                                               "peer transport ingress process");
    if (!base.ok) return base;
    if (!valid_sync_id(options.worker_id)) return fail_result("peer transport ingress process worker_id must be lowercase portable sync id");
    if (!valid_sync_id(options.worker_lease_id)) return fail_result("peer transport ingress process worker_lease_id must be lowercase portable sync id");
    if (options.lease_duration_seconds == 0) return fail_result("peer transport ingress process lease_duration_seconds must be positive");
    SyncValidationResult retry = validate_peer_transport_ingress_retry_options(options.max_attempts,
                                                                                options.retry_backoff_seconds,
                                                                                "peer transport ingress process");
    if (!retry.ok) return retry;
    return validate_peer_transport_sqlite_busy_timeout(options.sqlite_busy_timeout_ms,
                                                       "peer transport ingress process");
}

SyncValidationResult validate_peer_transport_ingress_retention_options(const SyncPeerTransportIngressRetentionOptions& options) {
    SyncValidationResult base = validate_peer_transport_ingress_queue_options(options.sqlite_path,
                                                                               options.session_id,
                                                                               options.retention_now_epoch,
                                                                               "peer transport ingress retention");
    if (!base.ok) return base;
    if (!valid_sync_id(options.operator_id)) return fail_result("peer transport ingress retention operator_id must be lowercase portable sync id");
    if (options.reason.empty()) return fail_result("peer transport ingress retention reason is required");
    if (options.completed_older_than_epoch == 0 &&
        options.abandoned_older_than_epoch == 0 &&
        options.authority_denial_older_than_epoch == 0) {
        return fail_result("peer transport ingress retention requires at least one nonzero cutoff");
    }
    if (options.completed_older_than_epoch > options.retention_now_epoch ||
        options.abandoned_older_than_epoch > options.retention_now_epoch ||
        options.authority_denial_older_than_epoch > options.retention_now_epoch) {
        return fail_result("peer transport ingress retention cutoffs cannot be in the future");
    }
    if (options.max_frame_bytes == 0 || options.max_chunk_count == 0 ||
        options.max_metadata_field_bytes == 0) {
        return fail_result("peer transport ingress retention canonical verifier limits must be positive");
    }
    const std::uint64_t sqlite_max = static_cast<std::uint64_t>(
        std::numeric_limits<sqlite3_int64>::max());
    if (options.max_completed_rows > sqlite_max ||
        options.max_abandoned_rows > sqlite_max ||
        options.max_authority_denial_rows > sqlite_max) {
        return fail_result("peer transport ingress retention max row limits exceed SQLite INTEGER range");
    }
    return validate_peer_transport_sqlite_busy_timeout(options.sqlite_busy_timeout_ms,
                                                       "peer transport ingress retention");
}

SyncValidationResult validate_peer_transport_ingress_envelope_shape(const SyncPeerTransportBoundChunkResponseBatchEnvelope& envelope,
                                                                    const std::vector<std::string>& chunk_bytes,
                                                                    const std::string& label) {
    if (envelope.transport_envelope_idempotency_key.rfind("sync-peer-transport-envelope:v1:", 0) != 0) {
        return fail_result(label + " requires namespaced transport envelope idempotency key");
    }
    if (!is_lowercase_sha256_hex(envelope.transport_mac_sha256)) {
        return fail_result(label + " requires lowercase transport_mac_sha256 evidence");
    }
    if (!valid_sync_id(envelope.transport_instance_id) || !valid_sync_id(envelope.transport_key_id)) {
        return fail_result(label + " requires valid transport identity");
    }
    if (!valid_sync_id(envelope.peer_batch_envelope.peer_id) || !valid_sync_id(envelope.peer_batch_envelope.peer_session_id)) {
        return fail_result(label + " requires valid peer identity");
    }
    if (envelope.peer_batch_envelope.path.value.empty()) return fail_result(label + " requires peer batch path evidence");
    if (envelope.peer_batch_envelope.responses.size() != chunk_bytes.size()) {
        return fail_result(label + " chunk_bytes count must match peer response count");
    }
    return validate_peer_transport_envelope_bounds(envelope.peer_batch_envelope,
                                                   envelope.max_response_count,
                                                   envelope.max_total_bytes,
                                                   envelope.max_chunk_bytes,
                                                   label);
}

std::string peer_transport_ingress_event_key(const std::string& session_id,
                                             const std::string& transport_envelope_key,
                                             const std::string& event_kind,
                                             std::uint64_t attempt,
                                             const std::string& state_after,
                                             std::uint64_t observed_at_epoch,
                                             const std::string& reason) {
    const std::string material = length_prefixed_security_tuple("anonsync-sync-peer-transport-ingress-event-v1", {
        {"session_id", session_id},
        {"transport_envelope_key", transport_envelope_key},
        {"event_kind", event_kind},
        {"attempt", u64_string(attempt)},
        {"state_after", state_after},
        {"observed_at_epoch", u64_string(observed_at_epoch)},
        {"reason", reason}
    });
    return "sync-peer-transport-ingress-event:v1:" + sha256_hex(material);
}

void insert_peer_transport_ingress_event_or_throw(sqlite3* db,
                                                  const std::string& session_id,
                                                  const std::string& transport_envelope_key,
                                                  const std::string& event_kind,
                                                  const std::string& state_after,
                                                  std::uint64_t observed_at_epoch,
                                                  std::uint64_t attempt,
                                                  const std::string& reason,
                                                  const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db,
        "INSERT OR IGNORE INTO sync_peer_transport_ingress_events("
        "session_id, transport_envelope_idempotency_key, event_idempotency_key, event_kind, state_after, observed_at_epoch, attempt, reason) "
        "VALUES(?,?,?,?,?,?,?,?);",
        label + " event insert prepare");
    int i = 1;
    sqlite_bind_text_or_throw(stmt.stmt, i++, session_id, label + " event session");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope_key, label + " event transport key");
    sqlite_bind_text_or_throw(stmt.stmt, i++, peer_transport_ingress_event_key(session_id,
                                                                               transport_envelope_key,
                                                                               event_kind,
                                                                               attempt,
                                                                               state_after,
                                                                               observed_at_epoch,
                                                                               reason), label + " event key");
    sqlite_bind_text_or_throw(stmt.stmt, i++, event_kind, label + " event kind");
    sqlite_bind_text_or_throw(stmt.stmt, i++, state_after, label + " event state");
    sqlite_bind_u64_or_throw(stmt.stmt, i++, observed_at_epoch, label + " event observed");
    sqlite_bind_u64_or_throw(stmt.stmt, i++, attempt, label + " event attempt");
    sqlite_bind_text_or_throw(stmt.stmt, i++, reason, label + " event reason");
    sqlite_step_done_or_throw(stmt.stmt, label + " event insert");
}

const std::vector<std::string>& peer_transport_ingress_sqlite_family_suffixes() {
    static const std::vector<std::string> suffixes = {"-wal", "-shm", "-journal"};
    return suffixes;
}

SqlitePathFamilyGuard guard_peer_transport_ingress_sqlite_path_or_throw(
    const fs::path& sqlite_path,
    bool create_parent_directories,
    const std::string& label) {
    return guard_sqlite_path_family_or_throw(sqlite_path,
                                             create_parent_directories,
                                             peer_transport_ingress_sqlite_family_suffixes(),
                                             label);
}

bool peer_transport_ingress_sqlite_exists_or_throw(const fs::path& sqlite_path,
                                                    const std::string& label) {
    SqlitePathFamilyGuard guard = guard_peer_transport_ingress_sqlite_path_or_throw(
        sqlite_path, false, label);
    return guard.parent_exists() && guard.database_existed_at_preflight();
}

struct PeerTransportSqliteBusyHandlerContext {
    SyncPeerTransportSqliteWriteContentionResult* evidence = nullptr;
    std::atomic<bool>* contention_observed_signal = nullptr;
    std::chrono::steady_clock::time_point wait_started{};
    bool wait_started_valid = false;
};

struct PeerTransportIngressWriteConnection {
    // Declaration order is authority order. Reverse destruction revokes the
    // exact serialized-generation capability before strict-close destroys the
    // owner, then releases callback state and the approved parent directory.
    std::unique_ptr<SqlitePathFamilyGuard> path_guard;
    std::unique_ptr<PeerTransportSqliteBusyHandlerContext> busy_context;
    PeerTransportIngressSchemaAttestation schema_attestation;
    SyncSqliteDb owner;
    SyncSqliteSerializedDbBorrow serialized;

    PeerTransportIngressWriteConnection() = default;
    ~PeerTransportIngressWriteConnection() = default;
    PeerTransportIngressWriteConnection(
        const PeerTransportIngressWriteConnection&) = delete;
    PeerTransportIngressWriteConnection& operator=(
        const PeerTransportIngressWriteConnection&) = delete;
    PeerTransportIngressWriteConnection(
        PeerTransportIngressWriteConnection&&) noexcept = default;
    PeerTransportIngressWriteConnection& operator=(
        PeerTransportIngressWriteConnection&&) = delete;
};

struct PeerTransportIngressReadConnection {
    // The serialized-generation capability is released before the read-only
    // owner closes and before the approved parent path is released.
    std::unique_ptr<SqlitePathFamilyGuard> path_guard;
    PeerTransportIngressSchemaAttestation schema_attestation;
    SyncSqliteDb owner;
    SyncSqliteSerializedDbBorrow serialized;

    PeerTransportIngressReadConnection() = default;
    ~PeerTransportIngressReadConnection() = default;
    PeerTransportIngressReadConnection(
        const PeerTransportIngressReadConnection&) = delete;
    PeerTransportIngressReadConnection& operator=(
        const PeerTransportIngressReadConnection&) = delete;
    PeerTransportIngressReadConnection(
        PeerTransportIngressReadConnection&&) noexcept = default;
    PeerTransportIngressReadConnection& operator=(
        PeerTransportIngressReadConnection&&) = delete;
};

static_assert(std::is_nothrow_move_constructible_v<
                  PeerTransportIngressWriteConnection> &&
                  std::is_nothrow_move_constructible_v<
                      PeerTransportIngressReadConnection> &&
                  !std::is_move_assignable_v<
                      PeerTransportIngressWriteConnection> &&
                  !std::is_move_assignable_v<
                      PeerTransportIngressReadConnection>,
              "a live peer-ingress connection cannot overwrite an owner while its "
              "serialized-generation capability remains active");

[[nodiscard]] SyncSqliteConnectionAuthorityLease
verify_peer_transport_write_schema_snapshot_or_throw(
    const PeerTransportIngressWriteConnection& connection,
    const std::string& label) {
    return verify_peer_transport_ingress_schema_attestation_current_or_throw(
        connection.owner.db, connection.schema_attestation, label);
}

[[nodiscard]] SyncSqliteConnectionAuthorityLease
verify_peer_transport_read_schema_snapshot_or_throw(
    const PeerTransportIngressReadConnection& connection,
    const std::string& label) {
    return verify_peer_transport_ingress_schema_attestation_current_or_throw(
        connection.owner.db, connection.schema_attestation, label);
}

sqlite3_int64 peer_transport_sqlite_scalar_i64_or_throw(
    sqlite3* db,
    const std::string& sql,
    const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db, sql, label + " prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " query");
    return static_cast<sqlite3_int64>(sqlite_column_i64_or_throw(
        stmt.stmt, 0, label + " exact scalar"));
}

void peer_transport_sqlite_dbconfig_or_throw(sqlite3* db,
                                             int option,
                                             int requested,
                                             const std::string& label) {
    int actual = -1;
    const int rc = sqlite3_db_config(db, option, requested, &actual);
    if (rc != SQLITE_OK) throw_sqlite_exception(db, rc, label);
    if (actual != requested) {
        throw std::runtime_error(label + " did not enter the requested state");
    }
}

void configure_peer_transport_sqlite_defensive_profile_or_throw(
    sqlite3* db,
    bool read_only,
    const std::string& label) {
#ifdef SQLITE_DBCONFIG_DEFENSIVE
    peer_transport_sqlite_dbconfig_or_throw(
        db, SQLITE_DBCONFIG_DEFENSIVE, 1, label + " could not enable defensive mode");
#endif
#ifdef SQLITE_DBCONFIG_TRUSTED_SCHEMA
    peer_transport_sqlite_dbconfig_or_throw(
        db, SQLITE_DBCONFIG_TRUSTED_SCHEMA, 0, label + " could not disable trusted schema");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_TRIGGER
    peer_transport_sqlite_dbconfig_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_TRIGGER, 0, label + " could not disable schema triggers");
#endif
#ifdef SQLITE_DBCONFIG_ENABLE_VIEW
    peer_transport_sqlite_dbconfig_or_throw(
        db, SQLITE_DBCONFIG_ENABLE_VIEW, 0, label + " could not disable schema views");
#endif
#ifdef SQLITE_LIMIT_ATTACHED
    (void)sqlite3_limit(db, SQLITE_LIMIT_ATTACHED, 0);
    if (sqlite3_limit(db, SQLITE_LIMIT_ATTACHED, -1) != 0) {
        throw std::runtime_error(label + " could not disable attached databases");
    }
#endif
#ifdef SQLITE_LIMIT_TRIGGER_DEPTH
    // SQLite implements foreign-key actions with trigger-depth accounting even
    // when application-defined triggers are disabled above. A limit of zero
    // makes every ON DELETE action fail with "too many levels of trigger
    // recursion". Permit exactly one FK-action frame; recursive trigger chains
    // remain impossible and schema triggers remain disabled.
    (void)sqlite3_limit(db, SQLITE_LIMIT_TRIGGER_DEPTH, 1);
    if (sqlite3_limit(db, SQLITE_LIMIT_TRIGGER_DEPTH, -1) != 1) {
        throw std::runtime_error(label + " could not bound trigger depth to one");
    }
#endif
    sqlite_exec_or_throw(db, "PRAGMA ignore_check_constraints=OFF;",
                         label + " could not enable CHECK constraints");
    if (peer_transport_sqlite_scalar_i64_or_throw(
            db,
            "PRAGMA ignore_check_constraints;",
            label + " CHECK constraint verification") != 0) {
        throw std::runtime_error(label + " CHECK constraints remain disabled");
    }
    sqlite_exec_or_throw(db, "PRAGMA trusted_schema=OFF;",
                         label + " could not disable trusted_schema pragma");
    if (peer_transport_sqlite_scalar_i64_or_throw(
            db, "PRAGMA trusted_schema;", label + " trusted_schema verification") != 0) {
        throw std::runtime_error(label + " trusted_schema verification failed");
    }
    if (read_only) {
        sqlite_exec_or_throw(db, "PRAGMA query_only=ON;",
                             label + " could not enable query_only");
        if (peer_transport_sqlite_scalar_i64_or_throw(
                db, "PRAGMA query_only;", label + " query_only verification") != 1) {
            throw std::runtime_error(label + " query_only verification failed");
        }
    }
}

SyncSqliteConcurrentJournalProfile
configure_and_verify_peer_transport_sqlite_durability_or_throw(
    sqlite3* db,
    const std::string& label) {
    SyncSqliteConcurrentJournalProfile profile =
        configure_sync_sqlite_concurrent_durable_journal_or_throw(db, label);
    sqlite_exec_or_throw(db, "PRAGMA foreign_keys=ON;",
                         label + " could not enable foreign keys");
    if (peer_transport_sqlite_scalar_i64_or_throw(
            db, "PRAGMA foreign_keys;", label + " foreign_keys verification") != 1) {
        throw std::runtime_error(label + " foreign_keys verification failed");
    }
    return profile;
}

std::uint64_t peer_transport_elapsed_ms(std::chrono::steady_clock::time_point started) {
    const auto elapsed = std::chrono::steady_clock::now() - started;
    const auto milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
    return milliseconds > 0 ? static_cast<std::uint64_t>(milliseconds) : 0;
}

int peer_transport_sqlite_busy_handler(void* raw_context, int prior_invocations) noexcept {
    auto* context = static_cast<PeerTransportSqliteBusyHandlerContext*>(raw_context);
    if (context == nullptr || context->evidence == nullptr) return 0;
    SyncPeerTransportSqliteWriteContentionResult& evidence = *context->evidence;
    evidence.contention_observed = true;
    if (context->contention_observed_signal != nullptr) {
        context->contention_observed_signal->store(true, std::memory_order_release);
    }
    ++evidence.busy_handler_invocations;
    if (prior_invocations == 0 || !context->wait_started_valid) {
        context->wait_started = std::chrono::steady_clock::now();
        context->wait_started_valid = true;
    }
    if (evidence.configured_busy_timeout_ms == 0) {
        evidence.busy_timeout_exhausted = true;
        return 0;
    }
    const std::uint64_t elapsed_ms = peer_transport_elapsed_ms(context->wait_started);
    if (elapsed_ms >= evidence.configured_busy_timeout_ms) {
        evidence.busy_timeout_exhausted = true;
        return 0;
    }
    const std::uint64_t remaining_ms = evidence.configured_busy_timeout_ms - elapsed_ms;
    const std::uint64_t progressive_sleep_ms =
        static_cast<std::uint64_t>(prior_invocations < 9 ? prior_invocations + 1 : 10);
    const std::uint64_t requested_sleep_ms = std::min(progressive_sleep_ms, remaining_ms);
    const int slept_ms = sqlite3_sleep(static_cast<int>(requested_sleep_ms));
    if (slept_ms > 0) evidence.busy_sleep_ms += static_cast<std::uint64_t>(slept_ms);
    return 1;
}

void capture_peer_transport_sqlite_failure(
    const SyncSqliteException& error,
    SyncPeerTransportSqliteWriteContentionResult& evidence) {
    evidence.primary_result_code = error.primary_result_code();
    evidence.extended_result_code = error.extended_result_code();
    evidence.result_code_name = sqlite_result_code_name(error.primary_result_code());
    evidence.failure_operation = error.operation();
    if (error.primary_result_code() == SQLITE_BUSY) {
        evidence.sqlite_busy = true;
        evidence.contention_observed = true;
    }
    if (error.primary_result_code() == SQLITE_LOCKED) {
        evidence.sqlite_locked = true;
        evidence.contention_observed = true;
    }
}

std::unique_ptr<SyncSqliteTransaction>
begin_peer_transport_write_transaction_or_throw(
    SyncSqliteDbHandleSlot& db,
    SyncPeerTransportSqliteWriteContentionResult& evidence,
    const std::string& label) {
    ++evidence.write_lock_attempts;
    const auto started = std::chrono::steady_clock::now();
    try {
        auto transaction = std::make_unique<SyncSqliteTransaction>(
            db,
            label,
            SyncSqliteTransactionMode::Immediate);
        evidence.write_lock_wait_elapsed_ms += peer_transport_elapsed_ms(started);
        ++evidence.write_locks_acquired;
        return transaction;
    } catch (const SyncSqliteException& error) {
        evidence.write_lock_wait_elapsed_ms += peer_transport_elapsed_ms(started);
        capture_peer_transport_sqlite_failure(error, evidence);
        throw;
    } catch (...) {
        evidence.write_lock_wait_elapsed_ms += peer_transport_elapsed_ms(started);
        throw;
    }
}

PeerTransportIngressWriteConnection open_peer_transport_ingress_sqlite_readwrite_or_throw(
    const fs::path& sqlite_path,
    std::uint64_t busy_timeout_ms,
    SyncPeerTransportSqliteWriteContentionResult& contention,
    const std::string& label) {
    contention.configured_busy_timeout_ms = busy_timeout_ms;
    PeerTransportIngressWriteConnection connection;
    connection.path_guard = std::make_unique<SqlitePathFamilyGuard>(
        guard_peer_transport_ingress_sqlite_path_or_throw(sqlite_path, true, label));
    connection.busy_context = std::make_unique<PeerTransportSqliteBusyHandlerContext>();
    connection.busy_context->evidence = &contention;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int open_rc = sqlite3_open_v2(connection.path_guard->database_path().string().c_str(),
                                        connection.owner.db.out(),
                                        flags,
                                        nullptr);
    if (open_rc != SQLITE_OK) {
        throw_sqlite_exception(connection.owner.db, open_rc, label + " could not open sqlite database");
    }
    connection.serialized = borrow_sync_sqlite_serialized_db_or_throw(
        connection.owner.db, label + " opened connection");
    sqlite3* const db = connection.serialized.get();
    connection.path_guard->verify_open_database_or_throw(db,
                                                          label + " path binding after open");
    const int extended_rc = sqlite3_extended_result_codes(db, 1);
    if (extended_rc != SQLITE_OK) {
        throw_sqlite_exception(db, extended_rc, label + " could not enable extended result codes");
    }
    configure_peer_transport_sqlite_defensive_profile_or_throw(db, false, label);
    const int busy_rc = sqlite3_busy_handler(db,
                                             peer_transport_sqlite_busy_handler,
                                             connection.busy_context.get());
    if (busy_rc != SQLITE_OK) {
        throw_sqlite_exception(db, busy_rc, label + " could not install bounded busy handler");
    }
    contention.busy_handler_installed = true;
    const SyncSqliteConcurrentJournalProfile durability_profile =
        configure_and_verify_peer_transport_sqlite_durability_or_throw(db, label);
    contention.sqlite_runtime_version = durability_profile.runtime_version;
    contention.sqlite_runtime_source_id = durability_profile.runtime_source_id;
    contention.sqlite_journal_mode = durability_profile.journal_mode;
    contention.sqlite_durability_profile_checked = true;
    contention.sqlite_runtime_bundled = durability_profile.bundled;
    contention.sqlite_wal_reset_fix_known = durability_profile.wal_reset_fix_known;
    contention.sqlite_rollback_journal_fallback_active =
        durability_profile.rollback_journal_fallback_active;
    connection.path_guard->verify_open_database_or_throw(db,
                                                          label + " path binding after journal configuration");
    connection.schema_attestation =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            db,
            true,
            false,
            label + " schema");
    connection.path_guard->verify_open_database_or_throw(db,
                                                          label + " path binding after schema attestation");
    return connection;
}

PeerTransportIngressReadConnection open_peer_transport_ingress_sqlite_readonly_or_throw(
    const fs::path& sqlite_path,
    const std::string& label) {
    PeerTransportIngressReadConnection connection;
    connection.path_guard = std::make_unique<SqlitePathFamilyGuard>(
        guard_peer_transport_ingress_sqlite_path_or_throw(sqlite_path, false, label));
    if (!connection.path_guard->parent_exists() ||
        !connection.path_guard->database_existed_at_preflight()) {
        throw std::runtime_error(label + " sqlite database does not exist");
    }
    int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int open_rc = sqlite3_open_v2(connection.path_guard->database_path().string().c_str(),
                                        connection.owner.db.out(),
                                        flags,
                                        nullptr);
    if (open_rc != SQLITE_OK) {
        throw_sqlite_exception(connection.owner.db, open_rc, label + " could not open sqlite database read-only");
    }
    connection.serialized = borrow_sync_sqlite_serialized_db_or_throw(
        connection.owner.db, label + " opened read-only connection");
    sqlite3* const db = connection.serialized.get();
    connection.path_guard->verify_open_database_or_throw(
        db, label + " read-only path binding after open");
    const int extended_rc = sqlite3_extended_result_codes(db, 1);
    if (extended_rc != SQLITE_OK) {
        throw_sqlite_exception(db, extended_rc, label + " could not enable extended result codes read-only");
    }
    configure_peer_transport_sqlite_defensive_profile_or_throw(db, true, label);
    connection.schema_attestation =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            db,
            false,
            true,
            label + " schema");
    connection.path_guard->verify_open_database_or_throw(db,
                                                          label + " read-only path binding after schema attestation");
    return connection;
}

bool valid_peer_transport_authority_status(const std::string& status) {
    return status == "trusted" || status == "disabled" || status == "revoked";
}

SyncValidationResult validate_peer_transport_authority_record_options(const SyncPeerTransportAuthorityRecordOptions& options) {
    SyncValidationResult base = validate_peer_transport_ingress_queue_options(options.sqlite_path,
                                                                               options.session_id,
                                                                               options.updated_at_epoch,
                                                                               "peer transport authority record");
    if (!base.ok) return base;
    if (!valid_sync_id(options.peer_id)) return fail_result("peer transport authority record peer_id must be lowercase portable sync id");
    if (!valid_sync_id(options.peer_session_id)) return fail_result("peer transport authority record peer_session_id must be lowercase portable sync id");
    if (!valid_sync_id(options.transport_instance_id)) return fail_result("peer transport authority record transport_instance_id must be lowercase portable sync id");
    if (!valid_sync_id(options.transport_key_id)) return fail_result("peer transport authority record transport_key_id must be lowercase portable sync id");
    if (!valid_peer_transport_authority_status(options.authority_status)) return fail_result("peer transport authority record status must be trusted, disabled, or revoked");
    if (options.valid_from_epoch == 0) return fail_result("peer transport authority record valid_from_epoch must be positive");
    if (options.valid_until_epoch != 0 && options.valid_until_epoch < options.valid_from_epoch) {
        return fail_result("peer transport authority record valid_until_epoch must be zero or after valid_from_epoch");
    }
    return validate_peer_transport_sqlite_busy_timeout(options.sqlite_busy_timeout_ms,
                                                       "peer transport authority record");
}

SyncValidationResult validate_peer_transport_authority_supersession_options(const SyncPeerTransportAuthoritySupersessionRecordOptions& options) {
    SyncValidationResult base = validate_peer_transport_ingress_queue_options(options.sqlite_path,
                                                                               options.session_id,
                                                                               options.updated_at_epoch,
                                                                               "peer transport authority supersession record");
    if (!base.ok) return base;
    if (!valid_sync_id(options.peer_id)) return fail_result("peer transport authority supersession peer_id must be lowercase portable sync id");
    if (!valid_sync_id(options.peer_session_id)) return fail_result("peer transport authority supersession peer_session_id must be lowercase portable sync id");
    if (!valid_sync_id(options.transport_instance_id)) return fail_result("peer transport authority supersession transport_instance_id must be lowercase portable sync id");
    if (!valid_sync_id(options.old_transport_key_id)) return fail_result("peer transport authority supersession old_transport_key_id must be lowercase portable sync id");
    if (!valid_sync_id(options.replacement_transport_key_id)) return fail_result("peer transport authority supersession replacement_transport_key_id must be lowercase portable sync id");
    if (options.old_transport_key_id == options.replacement_transport_key_id) {
        return fail_result("peer transport authority supersession replacement key must differ from old key");
    }
    if (options.overlap_valid_from_epoch == 0) return fail_result("peer transport authority supersession overlap_valid_from_epoch must be positive");
    if (options.overlap_valid_until_epoch < options.overlap_valid_from_epoch) {
        return fail_result("peer transport authority supersession overlap_valid_until_epoch must be at or after overlap_valid_from_epoch");
    }
    return validate_peer_transport_sqlite_busy_timeout(options.sqlite_busy_timeout_ms,
                                                       "peer transport authority supersession");
}

SyncValidationResult validate_peer_transport_authority_decision_options(const SyncPeerTransportAuthorityDecisionOptions& options,
                                                                        const std::string& label) {
    return validate_peer_transport_ingress_queue_options(options.sqlite_path,
                                                         options.session_id,
                                                         options.decision_now_epoch,
                                                         label);
}

struct PeerTransportAuthorityRecordSnapshot {
    bool found = false;
    std::string authority_status;
    std::uint64_t valid_from_epoch = 0;
    std::uint64_t valid_until_epoch = 0;
    std::string reason;
};

struct PeerTransportAuthoritySupersessionSnapshot {
    bool found = false;
    std::string replacement_transport_key_id;
    std::uint64_t overlap_valid_from_epoch = 0;
    std::uint64_t overlap_valid_until_epoch = 0;
    std::string reason;
};

PeerTransportAuthorityRecordSnapshot load_peer_transport_authority_record_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db,
        "SELECT authority_status, valid_from_epoch, valid_until_epoch, reason "
        "FROM sync_peer_transport_authority_records "
        "WHERE session_id=? AND peer_id=? AND peer_session_id=? AND transport_instance_id=? AND transport_key_id=?;",
        label + " authority record select prepare");
    int i = 1;
    sqlite_bind_text_or_throw(stmt.stmt, i++, session_id, label + " authority record session");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_id, label + " authority record peer");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_session_id, label + " authority record peer session");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_instance_id, label + " authority record transport instance");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_key_id, label + " authority record transport key");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return {};
    if (rc != SQLITE_ROW) throw_sqlite_exception(sqlite3_db_handle(stmt.stmt), rc, label + " authority record select");
    PeerTransportAuthorityRecordSnapshot row;
    row.found = true;
    row.authority_status = sqlite_column_text_or_throw(stmt.stmt, 0, label + " authority status");
    row.valid_from_epoch = sqlite_column_u64_or_throw(stmt.stmt, 1, label + " authority valid from");
    row.valid_until_epoch = sqlite_column_u64_or_throw(stmt.stmt, 2, label + " authority valid until");
    row.reason = sqlite_column_text_or_throw(stmt.stmt, 3, label + " authority reason");
    return row;
}

PeerTransportAuthoritySupersessionSnapshot load_peer_transport_authority_supersession_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::string& label) {
    if (!sqlite_table_exists_or_throw(db, "sync_peer_transport_authority_supersessions", label + " authority supersession table")) {
        return {};
    }
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db,
        "SELECT replacement_transport_key_id, overlap_valid_from_epoch, overlap_valid_until_epoch, reason "
        "FROM sync_peer_transport_authority_supersessions "
        "WHERE session_id=? AND peer_id=? AND peer_session_id=? AND transport_instance_id=? AND old_transport_key_id=?;",
        label + " authority supersession select prepare");
    int i = 1;
    sqlite_bind_text_or_throw(stmt.stmt, i++, session_id, label + " authority supersession session");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_id, label + " authority supersession peer");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_session_id, label + " authority supersession peer session");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_instance_id, label + " authority supersession transport instance");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_key_id, label + " authority supersession old transport key");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return {};
    if (rc != SQLITE_ROW) throw_sqlite_exception(sqlite3_db_handle(stmt.stmt), rc, label + " authority supersession select");
    PeerTransportAuthoritySupersessionSnapshot row;
    row.found = true;
    row.replacement_transport_key_id = sqlite_column_text_or_throw(stmt.stmt, 0, label + " authority supersession replacement key");
    row.overlap_valid_from_epoch = sqlite_column_u64_or_throw(stmt.stmt, 1, label + " authority supersession overlap valid from");
    row.overlap_valid_until_epoch = sqlite_column_u64_or_throw(stmt.stmt, 2, label + " authority supersession overlap valid until");
    row.reason = sqlite_column_text_or_throw(stmt.stmt, 3, label + " authority supersession reason");
    return row;
}

std::string peer_transport_authority_lifecycle_state(const PeerTransportAuthorityRecordSnapshot& record,
                                                     const PeerTransportAuthoritySupersessionSnapshot& supersession,
                                                     std::uint64_t now_epoch) {
    if (!record.found) return "unknown";
    if (record.authority_status == "revoked") return "revoked";
    if (record.authority_status == "disabled") return "disabled";
    if (record.authority_status != "trusted") return "untrusted-status";
    if (now_epoch < record.valid_from_epoch) return "not-yet-valid";
    if (record.valid_until_epoch != 0 && now_epoch > record.valid_until_epoch) return "expired";
    if (supersession.found) {
        if (now_epoch > supersession.overlap_valid_until_epoch) return "superseded-expired";
        if (now_epoch >= supersession.overlap_valid_from_epoch) return "superseded-overlap-valid";
    }
    return "current";
}

std::string peer_transport_authority_denial_reason(const PeerTransportAuthorityRecordSnapshot& record,
                                                   const PeerTransportAuthoritySupersessionSnapshot& supersession,
                                                   std::uint64_t now_epoch) {
    const std::string lifecycle = peer_transport_authority_lifecycle_state(record, supersession, now_epoch);
    if (lifecycle == "unknown") return "unknown peer transport authority";
    if (lifecycle == "revoked") return "peer transport authority revoked";
    if (lifecycle == "disabled") return "peer transport authority disabled";
    if (lifecycle == "untrusted-status") return "peer transport authority status is not trusted";
    if (lifecycle == "not-yet-valid") return "peer transport authority not yet valid";
    if (lifecycle == "expired") return "peer transport authority expired";
    if (lifecycle == "superseded-expired") return "peer transport authority superseded key expired";
    return "";
}

void populate_peer_transport_authority_decision_result(
    const fs::path& sqlite_path,
    const std::string& session_id,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::string& payload_digest,
    const PeerTransportAuthorityRecordSnapshot& record,
    const PeerTransportAuthoritySupersessionSnapshot& supersession,
    std::uint64_t now_epoch,
    SyncPeerTransportAuthorityDecisionResult& out) {
    out.sqlite_path = sqlite_path.generic_string();
    out.session_id = session_id;
    out.transport_envelope_idempotency_key = transport_envelope.transport_envelope_idempotency_key;
    out.payload_digest = payload_digest;
    out.peer_id = transport_envelope.peer_batch_envelope.peer_id;
    out.peer_session_id = transport_envelope.peer_batch_envelope.peer_session_id;
    out.transport_instance_id = transport_envelope.transport_instance_id;
    out.transport_key_id = transport_envelope.transport_key_id;
    out.authority_checked = true;
    out.authority_record_found = record.found;
    out.authority_supersession_found = supersession.found;
    out.authority_supersession_overlap_valid = supersession.found &&
                                              now_epoch >= supersession.overlap_valid_from_epoch &&
                                              now_epoch <= supersession.overlap_valid_until_epoch;
    out.authority_supersession_expired = supersession.found && now_epoch > supersession.overlap_valid_until_epoch;
    out.authority_status = record.authority_status;
    out.authority_lifecycle_state = peer_transport_authority_lifecycle_state(record, supersession, now_epoch);
    out.valid_from_epoch = record.valid_from_epoch;
    out.valid_until_epoch = record.valid_until_epoch;
    out.replacement_transport_key_id = supersession.replacement_transport_key_id;
    out.supersession_overlap_valid_from_epoch = supersession.overlap_valid_from_epoch;
    out.supersession_overlap_valid_until_epoch = supersession.overlap_valid_until_epoch;
    out.authority_reason = record.reason;
    out.supersession_reason = supersession.reason;
    out.deny_reason = peer_transport_authority_denial_reason(record, supersession, now_epoch);
    out.authority_allowed = out.deny_reason.empty();
    out.authority_denied = !out.authority_allowed;
}

void record_peer_transport_authority_denial_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::string& payload_digest,
    std::uint64_t denied_at_epoch,
    SyncPeerTransportAuthorityDecisionResult& decision,
    const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db,
        "INSERT OR IGNORE INTO sync_peer_transport_authority_denials("
        "session_id, transport_envelope_idempotency_key, peer_id, peer_session_id, transport_instance_id, transport_key_id, "
        "payload_digest, total_bytes, denied_at_epoch, deny_reason) "
        "VALUES(?,?,?,?,?,?,?,?,?,?);",
        label + " authority denial insert prepare");
    int i = 1;
    sqlite_bind_text_or_throw(stmt.stmt, i++, session_id, label + " authority denial session");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_envelope_idempotency_key, label + " authority denial envelope");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_id, label + " authority denial peer");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_session_id, label + " authority denial peer session");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_instance_id, label + " authority denial transport instance");
    sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_key_id, label + " authority denial transport key");
    sqlite_bind_text_or_throw(stmt.stmt, i++, payload_digest, label + " authority denial payload digest");
    sqlite_bind_u64_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.total_bytes, label + " authority denial total bytes");
    sqlite_bind_u64_or_throw(stmt.stmt, i++, denied_at_epoch, label + " authority denial denied at");
    sqlite_bind_text_or_throw(stmt.stmt, i++, decision.deny_reason, label + " authority denial reason");
    sqlite_step_done_or_throw(stmt.stmt, label + " authority denial insert");
    if (sqlite3_changes(db) == 1) {
        decision.denial_recorded = true;
    } else {
        decision.denial_already_present = true;
    }
}

SyncPeerTransportAuthorityDecisionResult evaluate_peer_transport_authority_on_db_or_throw(
    sqlite3* db,
    const fs::path& sqlite_path,
    const std::string& session_id,
    std::uint64_t now_epoch,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::string& payload_digest,
    bool persist_denial,
    const std::string& label) {
    PeerTransportAuthorityRecordSnapshot record = load_peer_transport_authority_record_or_throw(db,
                                                                                                 session_id,
                                                                                                 transport_envelope,
                                                                                                 label);
    PeerTransportAuthoritySupersessionSnapshot supersession = load_peer_transport_authority_supersession_or_throw(db,
                                                                                                                  session_id,
                                                                                                                  transport_envelope,
                                                                                                                  label);
    SyncPeerTransportAuthorityDecisionResult decision;
    populate_peer_transport_authority_decision_result(sqlite_path,
                                                      session_id,
                                                      transport_envelope,
                                                      payload_digest,
                                                      record,
                                                      supersession,
                                                      now_epoch,
                                                      decision);
    if (decision.authority_denied && persist_denial) {
        record_peer_transport_authority_denial_or_throw(db,
                                                        session_id,
                                                        transport_envelope,
                                                        payload_digest,
                                                        now_epoch,
                                                        decision,
                                                        label);
    }
    return decision;
}

PeerTransportIngressClaimGeneration peer_transport_ingress_claim_generation_from_row_or_throw(
    const PeerTransportIngressRowSnapshot& row,
    const std::string& session_id,
    const std::string& transport_envelope_key,
    const std::string& label) {
    if (row.state != "claimed") {
        throw std::runtime_error(label + " requires a claimed ingress row");
    }
    return make_peer_transport_ingress_claim_generation_or_throw(
        session_id,
        transport_envelope_key,
        row.payload_digest(),
        row.attempts,
        row.max_attempts,
        row.retry_backoff_seconds,
        row.retry_at_epoch,
        row.worker_id,
        row.worker_lease_id,
        row.claimed_at_epoch,
        row.lease_expires_at_epoch,
        label);
}

void populate_peer_transport_receipt_evidence_result(
    const PeerIngressReceiptEvidenceInspection& evidence,
    SyncPeerTransportIngressProcessResult& out) {
    out.receipt_evidence_state = peer_ingress_receipt_evidence_name(evidence.kind);
    out.expected_receipts = evidence.expected_receipts;
    out.matching_receipts = evidence.matching_receipts;
    out.missing_receipts = evidence.missing_receipts;
    out.conflicting_receipts = evidence.conflicting_receipts;
    out.receipt_evidence_reason = evidence.reason;
}

struct PeerTransportIngressOpenPressureSnapshot {
    std::uint64_t open_rows = 0;
    std::uint64_t open_bytes = 0;
    std::uint64_t open_frame_bytes = 0;
    std::uint64_t peer_open_rows = 0;
    std::uint64_t peer_open_bytes = 0;
    std::uint64_t peer_open_frame_bytes = 0;
};

bool peer_transport_ingress_cap_would_be_exceeded(std::uint64_t limit,
                                                  std::uint64_t current,
                                                  std::uint64_t added) {
    if (limit == 0) return false;
    if (added > limit) return true;
    return current > limit - added;
}

PeerTransportIngressOpenPressureSnapshot load_peer_transport_ingress_open_pressure_or_throw(sqlite3* db,
                                                                                            const std::string& session_id,
                                                                                            const std::string& peer_id,
                                                                                            const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db,
        "SELECT "
        "COUNT(*), "
        "COALESCE(SUM(q.total_bytes),0), "
        "COALESCE(SUM(COALESCE(p.canonical_frame_bytes,0)),0), "
        "COALESCE(SUM(CASE WHEN q.peer_id=? THEN 1 ELSE 0 END),0), "
        "COALESCE(SUM(CASE WHEN q.peer_id=? THEN q.total_bytes ELSE 0 END),0), "
        "COALESCE(SUM(CASE WHEN q.peer_id=? THEN COALESCE(p.canonical_frame_bytes,0) ELSE 0 END),0) "
        "FROM main.sync_peer_transport_ingress_envelopes q "
        "LEFT JOIN main.sync_peer_transport_ingress_payloads p "
        "ON p.session_id=q.session_id AND "
        "p.transport_envelope_idempotency_key=q.transport_envelope_idempotency_key "
        "WHERE q.session_id=? AND q.state IN ('queued','claimed','failed');",
        label + " open pressure prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, peer_id, label + " open pressure peer rows");
    sqlite_bind_text_or_throw(stmt.stmt, 2, peer_id, label + " open pressure peer bytes");
    sqlite_bind_text_or_throw(stmt.stmt, 3, peer_id, label + " open pressure peer frame bytes");
    sqlite_bind_text_or_throw(stmt.stmt, 4, session_id, label + " open pressure session");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(sqlite3_db_handle(stmt.stmt), rc, label + " open pressure select");
    PeerTransportIngressOpenPressureSnapshot out;
    out.open_rows = sqlite_column_u64_or_throw(stmt.stmt, 0, label + " open rows");
    out.open_bytes = sqlite_column_u64_or_throw(stmt.stmt, 1, label + " open bytes");
    out.open_frame_bytes = sqlite_column_u64_or_throw(stmt.stmt, 2, label + " open frame bytes");
    out.peer_open_rows = sqlite_column_u64_or_throw(stmt.stmt, 3, label + " peer open rows");
    out.peer_open_bytes = sqlite_column_u64_or_throw(stmt.stmt, 4, label + " peer open bytes");
    out.peer_open_frame_bytes = sqlite_column_u64_or_throw(stmt.stmt, 5, label + " peer open frame bytes");
    return out;
}

void populate_peer_transport_ingress_pressure_result(
    const PeerTransportIngressOpenPressureSnapshot& pressure,
    SyncPeerTransportIngressEnqueueResult& out) {
    out.backpressure_checked = true;
    out.open_rows_before = pressure.open_rows;
    out.open_bytes_before = pressure.open_bytes;
    out.open_frame_bytes_before = pressure.open_frame_bytes;
    out.peer_open_rows_before = pressure.peer_open_rows;
    out.peer_open_bytes_before = pressure.peer_open_bytes;
    out.peer_open_frame_bytes_before = pressure.peer_open_frame_bytes;
}

std::string peer_transport_ingress_backpressure_reason(const SyncPeerTransportIngressEnqueueOptions& options,
                                                       const PeerTransportIngressOpenPressureSnapshot& pressure,
                                                       std::uint64_t added_rows,
                                                       std::uint64_t added_bytes,
                                                       std::uint64_t added_frame_bytes) {
    if (peer_transport_ingress_cap_would_be_exceeded(options.max_open_rows, pressure.open_rows, added_rows)) {
        return "session open ingress row cap reached";
    }
    if (peer_transport_ingress_cap_would_be_exceeded(options.max_open_bytes, pressure.open_bytes, added_bytes)) {
        return "session open ingress byte cap reached";
    }
    if (peer_transport_ingress_cap_would_be_exceeded(options.max_open_frame_bytes,
                                                     pressure.open_frame_bytes,
                                                     added_frame_bytes)) {
        return "session open ingress canonical-frame byte cap reached";
    }
    if (peer_transport_ingress_cap_would_be_exceeded(options.max_peer_open_rows, pressure.peer_open_rows, added_rows)) {
        return "peer open ingress row cap reached";
    }
    if (peer_transport_ingress_cap_would_be_exceeded(options.max_peer_open_bytes, pressure.peer_open_bytes, added_bytes)) {
        return "peer open ingress byte cap reached";
    }
    if (peer_transport_ingress_cap_would_be_exceeded(options.max_peer_open_frame_bytes,
                                                     pressure.peer_open_frame_bytes,
                                                     added_frame_bytes)) {
        return "peer open ingress canonical-frame byte cap reached";
    }
    return "";
}

PeerTransportIngressStoredPayload require_exact_peer_transport_ingress_stored_payload_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& session_id,
    const std::string& transport_envelope_key,
    const std::string& expected_canonical_frame,
    const std::string& expected_payload_digest,
    const std::string& label) {
    if (!sqlite_table_exists_or_throw(
            db, "sync_peer_transport_ingress_payloads", label + " payload table")) {
        throw std::runtime_error(label + " durable payload table is missing");
    }
    PeerTransportIngressStoredPayload stored =
        load_peer_transport_ingress_stored_payload_or_throw(
            db,
            transaction,
            session_id,
            transport_envelope_key,
            static_cast<std::uint64_t>(expected_canonical_frame.size()),
            label + " payload load");
    if (!stored.found) {
        throw std::runtime_error(label + " queue row has no durable canonical payload evidence");
    }
    if (stored.codec_version != kPeerTransportIngressWireCodecVersion ||
        stored.payload_digest != expected_payload_digest ||
        stored.canonical_frame_bytes !=
            static_cast<std::uint64_t>(expected_canonical_frame.size()) ||
        stored.canonical_frame_sha256 != sha256_hex(expected_canonical_frame) ||
        stored.canonical_frame != expected_canonical_frame) {
        throw std::runtime_error(
            label + " durable canonical payload differs from the expected exact bytes");
    }
    return stored;
}

SyncValidationResult record_sync_peer_transport_authority(
    const SyncPeerTransportAuthorityRecordOptions& options,
    SyncPeerTransportAuthorityRecordResult& out) {
    out = SyncPeerTransportAuthorityRecordResult{};
    out.sqlite_write_contention.configured_busy_timeout_ms = options.sqlite_busy_timeout_ms;
    SyncValidationResult options_result = validate_peer_transport_authority_record_options(options);
    if (!options_result.ok) return options_result;
    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(options.sqlite_path,
                                                                         "peer transport authority record sqlite_path");
    out.sqlite_path = sqlite_path.generic_string();
    out.session_id = options.session_id;
    out.peer_id = options.peer_id;
    out.peer_session_id = options.peer_session_id;
    out.transport_instance_id = options.transport_instance_id;
    out.transport_key_id = options.transport_key_id;
    out.authority_status = options.authority_status;
    out.valid_from_epoch = options.valid_from_epoch;
    out.valid_until_epoch = options.valid_until_epoch;
    out.updated_at_epoch = options.updated_at_epoch;
    try {
        PeerTransportIngressWriteConnection db = open_peer_transport_ingress_sqlite_readwrite_or_throw(
            sqlite_path,
            options.sqlite_busy_timeout_ms,
            out.sqlite_write_contention,
            "peer transport authority record");
        SyncSqliteConnectionAuthorityLease schema_authority_lease;
        std::unique_ptr<SyncSqliteTransaction> transaction_owner =
            begin_peer_transport_write_transaction_or_throw(
                db.owner.db,
                out.sqlite_write_contention,
                "peer transport authority record");
        SyncSqliteTransaction& transaction = *transaction_owner;
        schema_authority_lease = verify_peer_transport_write_schema_snapshot_or_throw(
            db, "peer transport authority record transaction schema");
        SyncSqliteStmt existing = sqlite_prepare_or_throw(db.owner.db,
            "SELECT COUNT(*) FROM sync_peer_transport_authority_records "
            "WHERE session_id=? AND peer_id=? AND peer_session_id=? AND transport_instance_id=? AND transport_key_id=?;",
            "peer transport authority record existing prepare");
        int e = 1;
        sqlite_bind_text_or_throw(existing.stmt, e++, options.session_id, "peer transport authority record existing session");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.peer_id, "peer transport authority record existing peer");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.peer_session_id, "peer transport authority record existing peer session");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.transport_instance_id, "peer transport authority record existing transport instance");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.transport_key_id, "peer transport authority record existing transport key");
        const int erc = sqlite3_step(existing.stmt);
        if (erc != SQLITE_ROW) throw_sqlite_exception(db.owner.db, erc, "peer transport authority record existing check");
        const bool already_present = sqlite_column_u64_or_throw(existing.stmt, 0, "peer transport authority record existing count") != 0;

        SyncSqliteStmt stmt = sqlite_prepare_or_throw(db.owner.db,
            "INSERT INTO sync_peer_transport_authority_records("
            "session_id, peer_id, peer_session_id, transport_instance_id, transport_key_id, authority_status, "
            "valid_from_epoch, valid_until_epoch, updated_at_epoch, reason) "
            "VALUES(?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(session_id, peer_id, peer_session_id, transport_instance_id, transport_key_id) DO UPDATE SET "
            "authority_status=excluded.authority_status, valid_from_epoch=excluded.valid_from_epoch, "
            "valid_until_epoch=excluded.valid_until_epoch, updated_at_epoch=excluded.updated_at_epoch, reason=excluded.reason;",
            "peer transport authority record upsert prepare");
        int i = 1;
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.session_id, "peer transport authority record session");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.peer_id, "peer transport authority record peer");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.peer_session_id, "peer transport authority record peer session");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.transport_instance_id, "peer transport authority record transport instance");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.transport_key_id, "peer transport authority record transport key");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.authority_status, "peer transport authority record status");
        sqlite_bind_u64_or_throw(stmt.stmt, i++, options.valid_from_epoch, "peer transport authority record valid from");
        sqlite_bind_u64_or_throw(stmt.stmt, i++, options.valid_until_epoch, "peer transport authority record valid until");
        sqlite_bind_u64_or_throw(stmt.stmt, i++, options.updated_at_epoch, "peer transport authority record updated");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.reason, "peer transport authority record reason");
        sqlite_step_done_or_throw(stmt.stmt, "peer transport authority record upsert");
        out.record_inserted = !already_present;
        out.record_updated = already_present;
        transaction.commit();
        return ok_result();
    } catch (const SyncSqliteException& e) {
        capture_peer_transport_sqlite_failure(e, out.sqlite_write_contention);
        return fail_result(std::string("peer transport authority record failed: ") + e.what());
    } catch (const std::exception& e) {
        return fail_result(std::string("peer transport authority record failed: ") + e.what());
    }
}

SyncValidationResult record_sync_peer_transport_authority_supersession(
    const SyncPeerTransportAuthoritySupersessionRecordOptions& options,
    SyncPeerTransportAuthoritySupersessionRecordResult& out) {
    out = SyncPeerTransportAuthoritySupersessionRecordResult{};
    out.sqlite_write_contention.configured_busy_timeout_ms = options.sqlite_busy_timeout_ms;
    SyncValidationResult options_result = validate_peer_transport_authority_supersession_options(options);
    if (!options_result.ok) return options_result;
    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(options.sqlite_path,
                                                                         "peer transport authority supersession sqlite_path");
    out.sqlite_path = sqlite_path.generic_string();
    out.session_id = options.session_id;
    out.peer_id = options.peer_id;
    out.peer_session_id = options.peer_session_id;
    out.transport_instance_id = options.transport_instance_id;
    out.old_transport_key_id = options.old_transport_key_id;
    out.replacement_transport_key_id = options.replacement_transport_key_id;
    out.overlap_valid_from_epoch = options.overlap_valid_from_epoch;
    out.overlap_valid_until_epoch = options.overlap_valid_until_epoch;
    out.updated_at_epoch = options.updated_at_epoch;
    try {
        PeerTransportIngressWriteConnection db = open_peer_transport_ingress_sqlite_readwrite_or_throw(
            sqlite_path,
            options.sqlite_busy_timeout_ms,
            out.sqlite_write_contention,
            "peer transport authority supersession");
        SyncSqliteConnectionAuthorityLease schema_authority_lease;
        std::unique_ptr<SyncSqliteTransaction> transaction_owner =
            begin_peer_transport_write_transaction_or_throw(
                db.owner.db,
                out.sqlite_write_contention,
                "peer transport authority supersession");
        SyncSqliteTransaction& transaction = *transaction_owner;
        schema_authority_lease = verify_peer_transport_write_schema_snapshot_or_throw(
            db, "peer transport authority supersession transaction schema");
        SyncSqliteStmt existing = sqlite_prepare_or_throw(db.owner.db,
            "SELECT COUNT(*) FROM sync_peer_transport_authority_supersessions "
            "WHERE session_id=? AND peer_id=? AND peer_session_id=? AND transport_instance_id=? AND old_transport_key_id=?;",
            "peer transport authority supersession existing prepare");
        int e = 1;
        sqlite_bind_text_or_throw(existing.stmt, e++, options.session_id, "peer transport authority supersession existing session");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.peer_id, "peer transport authority supersession existing peer");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.peer_session_id, "peer transport authority supersession existing peer session");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.transport_instance_id, "peer transport authority supersession existing transport instance");
        sqlite_bind_text_or_throw(existing.stmt, e++, options.old_transport_key_id, "peer transport authority supersession existing old key");
        const int erc = sqlite3_step(existing.stmt);
        if (erc != SQLITE_ROW) throw_sqlite_exception(db.owner.db, erc, "peer transport authority supersession existing check");
        const bool already_present = sqlite_column_u64_or_throw(existing.stmt, 0, "peer transport authority supersession existing count") != 0;

        SyncSqliteStmt stmt = sqlite_prepare_or_throw(db.owner.db,
            "INSERT INTO sync_peer_transport_authority_supersessions("
            "session_id, peer_id, peer_session_id, transport_instance_id, old_transport_key_id, replacement_transport_key_id, "
            "overlap_valid_from_epoch, overlap_valid_until_epoch, updated_at_epoch, reason) "
            "VALUES(?,?,?,?,?,?,?,?,?,?) "
            "ON CONFLICT(session_id, peer_id, peer_session_id, transport_instance_id, old_transport_key_id) DO UPDATE SET "
            "replacement_transport_key_id=excluded.replacement_transport_key_id, "
            "overlap_valid_from_epoch=excluded.overlap_valid_from_epoch, "
            "overlap_valid_until_epoch=excluded.overlap_valid_until_epoch, "
            "updated_at_epoch=excluded.updated_at_epoch, reason=excluded.reason;",
            "peer transport authority supersession upsert prepare");
        int i = 1;
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.session_id, "peer transport authority supersession session");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.peer_id, "peer transport authority supersession peer");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.peer_session_id, "peer transport authority supersession peer session");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.transport_instance_id, "peer transport authority supersession transport instance");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.old_transport_key_id, "peer transport authority supersession old key");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.replacement_transport_key_id, "peer transport authority supersession replacement key");
        sqlite_bind_u64_or_throw(stmt.stmt, i++, options.overlap_valid_from_epoch, "peer transport authority supersession overlap valid from");
        sqlite_bind_u64_or_throw(stmt.stmt, i++, options.overlap_valid_until_epoch, "peer transport authority supersession overlap valid until");
        sqlite_bind_u64_or_throw(stmt.stmt, i++, options.updated_at_epoch, "peer transport authority supersession updated");
        sqlite_bind_text_or_throw(stmt.stmt, i++, options.reason, "peer transport authority supersession reason");
        sqlite_step_done_or_throw(stmt.stmt, "peer transport authority supersession upsert");
        out.record_inserted = !already_present;
        out.record_updated = already_present;
        transaction.commit();
        return ok_result();
    } catch (const SyncSqliteException& e) {
        capture_peer_transport_sqlite_failure(e, out.sqlite_write_contention);
        return fail_result(std::string("peer transport authority supersession failed: ") + e.what());
    } catch (const std::exception& e) {
        return fail_result(std::string("peer transport authority supersession failed: ") + e.what());
    }
}

SyncValidationResult evaluate_sync_peer_transport_authority(
    const SyncPeerTransportAuthorityDecisionOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportAuthorityDecisionResult& out) {
    out = SyncPeerTransportAuthorityDecisionResult{};
    SyncValidationResult option_result = validate_peer_transport_authority_decision_options(options,
                                                                                           "peer transport authority decision");
    if (!option_result.ok) return option_result;
    SyncValidationResult envelope_result = validate_peer_transport_ingress_envelope_shape(transport_envelope,
                                                                                         chunk_bytes,
                                                                                         "peer transport authority decision");
    if (!envelope_result.ok) return envelope_result;
    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(options.sqlite_path,
                                                                         "peer transport authority decision sqlite_path");
    const std::string payload_digest = digest_peer_transport_ingress_payload(transport_envelope, chunk_bytes);
    try {
        if (!peer_transport_ingress_sqlite_exists_or_throw(sqlite_path,
                                                               "peer transport authority decision")) {
            populate_peer_transport_authority_decision_result(sqlite_path,
                                                              options.session_id,
                                                              transport_envelope,
                                                              payload_digest,
                                                              {},
                                                              {},
                                                              options.decision_now_epoch,
                                                              out);
            return fail_result("peer transport authority denied: " + out.deny_reason);
        }
        PeerTransportIngressReadConnection db = open_peer_transport_ingress_sqlite_readonly_or_throw(
            sqlite_path,
            "peer transport authority decision");
        SyncSqliteConnectionAuthorityLease schema_authority_lease;
        SyncSqliteTransaction transaction(db.owner.db,
                                          "peer transport authority decision read snapshot",
                                          SyncSqliteTransactionMode::Deferred);
        schema_authority_lease = verify_peer_transport_read_schema_snapshot_or_throw(
            db, "peer transport authority decision snapshot schema");
        if (!sqlite_table_exists_or_throw(db.owner.db,
                                          "sync_peer_transport_authority_records",
                                          "peer transport authority decision authority table")) {
            populate_peer_transport_authority_decision_result(sqlite_path,
                                                              options.session_id,
                                                              transport_envelope,
                                                              payload_digest,
                                                              {},
                                                              {},
                                                              options.decision_now_epoch,
                                                              out);
        } else {
            out = evaluate_peer_transport_authority_on_db_or_throw(db.owner.db,
                                                                   sqlite_path,
                                                                   options.session_id,
                                                                   options.decision_now_epoch,
                                                                   transport_envelope,
                                                                   payload_digest,
                                                                   false,
                                                                   "peer transport authority decision");
        }
        transaction.commit();
        return out.authority_allowed ? ok_result() : fail_result("peer transport authority denied: " + out.deny_reason);
    } catch (const std::exception& e) {
        return fail_result(std::string("peer transport authority decision failed: ") + e.what());
    }
}


SyncValidationResult enqueue_sync_peer_transport_ingress_envelope(
    const SyncPeerTransportIngressEnqueueOptions& options,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    SyncPeerTransportIngressEnqueueResult& out) {
    out = SyncPeerTransportIngressEnqueueResult{};
    PeerTransportEnqueueCompatibilityPublisher compatibility_publisher{out};
    out.sqlite_write_contention.configured_busy_timeout_ms = options.sqlite_busy_timeout_ms;
    SyncValidationResult queue_options = validate_peer_transport_ingress_queue_options(options.sqlite_path,
                                                                                       options.session_id,
                                                                                       options.enqueue_now_epoch,
                                                                                       "peer transport ingress enqueue");
    if (!queue_options.ok) return queue_options;
    SyncValidationResult retry_options = validate_peer_transport_ingress_retry_options(options.max_attempts,
                                                                                       options.retry_backoff_seconds,
                                                                                       "peer transport ingress enqueue");
    if (!retry_options.ok) return retry_options;
    SyncValidationResult busy_timeout = validate_peer_transport_sqlite_busy_timeout(options.sqlite_busy_timeout_ms,
                                                                                     "peer transport ingress enqueue");
    if (!busy_timeout.ok) return busy_timeout;
    std::uint64_t effective_frame_bytes = 0;
    SyncValidationResult frame_limit = resolve_peer_transport_frame_limit(
        options.max_frame_bytes,
        options.max_canonical_payload_bytes,
        effective_frame_bytes,
        "peer transport ingress enqueue");
    if (!frame_limit.ok) return frame_limit;
    PeerTransportIngressWireLimits wire_limits;
    wire_limits.max_frame_bytes = effective_frame_bytes;
    wire_limits.max_chunk_count = options.max_chunk_count;
    std::string canonical_frame;
    std::string payload_digest;
    SyncValidationResult envelope_result = encode_peer_transport_ingress_wire_frame(
        wire_limits,
        transport_envelope,
        chunk_bytes,
        canonical_frame,
        payload_digest);
    if (!envelope_result.ok) {
        return fail_result("peer transport ingress enqueue rejected wire evidence: " + envelope_result.reason);
    }
    const persistence::CanonicalIngressProjection canonical_projection =
        canonical_peer_transport_ingress_projection(transport_envelope, payload_digest);
    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(options.sqlite_path,
                                                                         "peer transport ingress enqueue sqlite_path");
    out.sqlite_path = sqlite_path.generic_string();
    out.session_id = options.session_id;
    out.transport_envelope_idempotency_key = transport_envelope.transport_envelope_idempotency_key;
    out.payload_digest = payload_digest;
    out.payload_frame_codec_version = kPeerTransportIngressWireCodecVersion;
    out.payload_frame_bytes = static_cast<std::uint64_t>(canonical_frame.size());
    out.payload_frame_sha256 = sha256_hex(canonical_frame);
    out.canonical_payload_encoded = true;
    out.max_attempts = options.max_attempts;
    out.retry_backoff_seconds = options.retry_backoff_seconds;
    out.max_open_rows = options.max_open_rows;
    out.max_open_bytes = options.max_open_bytes;
    out.max_open_frame_bytes = options.max_open_frame_bytes;
    out.max_peer_open_rows = options.max_peer_open_rows;
    out.max_peer_open_bytes = options.max_peer_open_bytes;
    out.max_peer_open_frame_bytes = options.max_peer_open_frame_bytes;
    // Mutation-result flags are published only after the enclosing SQLite
    // transaction commits. A failed event insert or COMMIT must not advertise
    // queue/payload evidence that was rolled back. row_already_present is
    // different: it reports a durable fact observed before this transaction's
    // mutations and may therefore be published as soon as the verified row is
    // found, including when contradictory payload history rejects the replay.
    bool committed_row_inserted = false;
    bool committed_payload_frame_stored = false;
    bool committed_payload_frame_already_present = false;
    bool committed_legacy_payload_backfilled = false;
    try {
        PeerTransportIngressWriteConnection db = open_peer_transport_ingress_sqlite_readwrite_or_throw(
            sqlite_path,
            options.sqlite_busy_timeout_ms,
            out.sqlite_write_contention,
            "peer transport ingress enqueue");
        SyncSqliteConnectionAuthorityLease schema_authority_lease;
        std::unique_ptr<SyncSqliteTransaction> transaction_owner =
            begin_peer_transport_write_transaction_or_throw(
                db.owner.db,
                out.sqlite_write_contention,
                "peer transport ingress enqueue");
        SyncSqliteTransaction& transaction = *transaction_owner;
        schema_authority_lease = verify_peer_transport_write_schema_snapshot_or_throw(
            db, "peer transport ingress enqueue transaction schema");
        if (options.require_authority_gate) {
            out.authority_decision = evaluate_peer_transport_authority_on_db_or_throw(db.owner.db,
                                                                                     sqlite_path,
                                                                                     options.session_id,
                                                                                     options.enqueue_now_epoch,
                                                                                     transport_envelope,
                                                                                     payload_digest,
                                                                                     true,
                                                                                     "peer transport ingress enqueue");
            if (out.authority_decision.authority_denied) {
                transaction.commit();
                return fail_result("peer transport ingress enqueue authority denied: " + out.authority_decision.deny_reason);
            }
        }
        std::optional<PeerTransportIngressRowSnapshot> existing =
            load_verified_peer_transport_ingress_row_or_throw(
                db.owner.db,
                options.session_id,
                transport_envelope.transport_envelope_idempotency_key,
                canonical_projection,
                "peer transport ingress enqueue");
        if (existing.has_value()) {
            out.row_already_present = true;
            const PeerTransportIngressStoredPayload existing_payload =
                load_peer_transport_ingress_stored_payload_or_throw(
                    db.owner.db,
                    transaction,
                    options.session_id,
                    transport_envelope.transport_envelope_idempotency_key,
                    effective_frame_bytes,
                    "peer transport ingress enqueue duplicate payload preflight");
            if (!existing_payload.found) {
                // A legacy metadata-only row is not an ordinary zero-growth
                // duplicate: backfilling its canonical evidence consumes real
                // durable storage and therefore obeys physical frame caps.
                const PeerTransportIngressOpenPressureSnapshot pressure =
                    load_peer_transport_ingress_open_pressure_or_throw(
                        db.owner.db,
                        options.session_id,
                        transport_envelope.peer_batch_envelope.peer_id,
                        "peer transport ingress enqueue duplicate payload backfill");
                populate_peer_transport_ingress_pressure_result(pressure, out);
                const std::string backpressure_reason =
                    peer_transport_ingress_backpressure_reason(
                        options,
                        pressure,
                        0,
                        0,
                        static_cast<std::uint64_t>(canonical_frame.size()));
                if (!backpressure_reason.empty()) {
                    out.backpressure_rejected = true;
                    transaction.rollback();
                    return fail_result(
                        "peer transport ingress enqueue payload backfill backpressure rejected: " +
                        backpressure_reason);
                }
            }
            const PeerTransportIngressPayloadStoreOutcome payload_outcome =
                store_or_verify_peer_transport_ingress_payload_or_throw(
                    db.owner.db,
                    transaction,
                    options.session_id,
                    transport_envelope.transport_envelope_idempotency_key,
                    canonical_frame,
                    payload_digest,
                    wire_limits,
                    options.enqueue_now_epoch,
                    "peer transport ingress enqueue duplicate payload");
            committed_payload_frame_stored =
                payload_outcome == PeerTransportIngressPayloadStoreOutcome::Inserted;
            committed_payload_frame_already_present =
                payload_outcome == PeerTransportIngressPayloadStoreOutcome::AlreadyPresent;
            committed_legacy_payload_backfilled =
                !existing_payload.found &&
                payload_outcome == PeerTransportIngressPayloadStoreOutcome::Inserted;
            insert_peer_transport_ingress_event_or_throw(
                db.owner.db,
                options.session_id,
                transport_envelope.transport_envelope_idempotency_key,
                "duplicate",
                existing->state,
                options.enqueue_now_epoch,
                existing->attempts,
                committed_payload_frame_stored
                    ? "duplicate enqueue matched row digest and backfilled canonical durable payload evidence"
                    : "duplicate enqueue matched and reverified canonical durable payload evidence",
                "peer transport ingress enqueue");
        } else {
            const PeerTransportIngressOpenPressureSnapshot pressure = load_peer_transport_ingress_open_pressure_or_throw(
                db.owner.db,
                options.session_id,
                transport_envelope.peer_batch_envelope.peer_id,
                "peer transport ingress enqueue");
            populate_peer_transport_ingress_pressure_result(pressure, out);
            const std::string backpressure_reason = peer_transport_ingress_backpressure_reason(options,
                                                                                                pressure,
                                                                                                1,
                                                                                                transport_envelope.peer_batch_envelope.total_bytes,
                                                                                                static_cast<std::uint64_t>(canonical_frame.size()));
            if (!backpressure_reason.empty()) {
                out.backpressure_rejected = true;
                transaction.rollback();
                return fail_result("peer transport ingress enqueue backpressure rejected: " + backpressure_reason);
            }
            SyncSqliteStmt stmt = sqlite_prepare_or_throw(db.owner.db,
                "INSERT INTO sync_peer_transport_ingress_envelopes("
                "session_id, transport_envelope_idempotency_key, transport_instance_id, transport_key_id, "
                "peer_id, peer_session_id, peer_response_batch_idempotency_key, path, payload_digest, "
                "response_count, total_bytes, issued_at_epoch, expires_at_epoch, enqueued_at_epoch, updated_at_epoch, "
                "state, attempts, max_attempts, retry_backoff_seconds, retry_at_epoch, worker_id, worker_lease_id, "
                "claimed_at_epoch, lease_expires_at_epoch, last_failure_reason, completed_at_epoch) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'queued',0,?,?,0,'','',0,0,'',0);",
                "peer transport ingress enqueue insert prepare");
            int i = 1;
            sqlite_bind_text_or_throw(stmt.stmt, i++, options.session_id, "peer transport ingress enqueue insert session");
            sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_envelope_idempotency_key, "peer transport ingress enqueue insert key");
            sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_instance_id, "peer transport ingress enqueue insert transport instance");
            sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.transport_key_id, "peer transport ingress enqueue insert transport key");
            sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_id, "peer transport ingress enqueue insert peer");
            sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_session_id, "peer transport ingress enqueue insert peer session");
            sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.peer_response_batch_idempotency_key, "peer transport ingress enqueue insert peer response key");
            sqlite_bind_text_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.path.value, "peer transport ingress enqueue insert path");
            sqlite_bind_text_or_throw(stmt.stmt, i++, payload_digest, "peer transport ingress enqueue insert payload");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.response_count, "peer transport ingress enqueue insert response count");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, transport_envelope.peer_batch_envelope.total_bytes, "peer transport ingress enqueue insert total bytes");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, transport_envelope.issued_at_epoch, "peer transport ingress enqueue insert issued");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, transport_envelope.expires_at_epoch, "peer transport ingress enqueue insert expires");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, options.enqueue_now_epoch, "peer transport ingress enqueue insert enqueued");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, options.enqueue_now_epoch, "peer transport ingress enqueue insert updated");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, options.max_attempts, "peer transport ingress enqueue insert max attempts");
            sqlite_bind_u64_or_throw(stmt.stmt, i++, options.retry_backoff_seconds, "peer transport ingress enqueue insert retry backoff");
            sqlite_step_done_or_throw(stmt.stmt, "peer transport ingress enqueue insert");
            committed_row_inserted = true;
            const PeerTransportIngressPayloadStoreOutcome payload_outcome =
                store_or_verify_peer_transport_ingress_payload_or_throw(
                    db.owner.db,
                    transaction,
                    options.session_id,
                    transport_envelope.transport_envelope_idempotency_key,
                    canonical_frame,
                    payload_digest,
                    wire_limits,
                    options.enqueue_now_epoch,
                    "peer transport ingress enqueue payload");
            if (payload_outcome != PeerTransportIngressPayloadStoreOutcome::Inserted) {
                throw std::runtime_error(
                    "peer transport ingress enqueue inserted a new row but payload evidence already existed");
            }
            committed_payload_frame_stored = true;
            insert_peer_transport_ingress_event_or_throw(
                db.owner.db,
                options.session_id,
                transport_envelope.transport_envelope_idempotency_key,
                "enqueued",
                "queued",
                options.enqueue_now_epoch,
                0,
                "canonical transport frame and queue row committed atomically without staging authority",
                "peer transport ingress enqueue");
            const std::optional<PeerTransportIngressRowSnapshot> inserted =
                load_verified_peer_transport_ingress_row_or_throw(
                    db.owner.db,
                    options.session_id,
                    transport_envelope.transport_envelope_idempotency_key,
                    canonical_projection,
                    "peer transport ingress enqueue post-insert verification");
            if (!inserted.has_value() || inserted->state != "queued" ||
                inserted->attempts != 0 ||
                inserted->max_attempts != options.max_attempts ||
                inserted->retry_backoff_seconds != options.retry_backoff_seconds) {
                throw std::runtime_error(
                    "peer transport ingress enqueue could not reconstitute the exact initial queue row before commit");
            }
        }
        transaction.commit();
        out.row_inserted = committed_row_inserted;
        out.payload_frame_stored = committed_payload_frame_stored;
        out.payload_frame_already_present = committed_payload_frame_already_present;
        out.legacy_payload_backfilled = committed_legacy_payload_backfilled;
        return ok_result();
    } catch (const SyncSqliteException& e) {
        capture_peer_transport_sqlite_failure(e, out.sqlite_write_contention);
        return fail_result(std::string("peer transport ingress enqueue failed: ") + e.what());
    } catch (const std::exception& e) {
        return fail_result(std::string("peer transport ingress enqueue failed: ") + e.what());
    }
}

SyncValidationResult load_sync_peer_transport_ingress_payload(
    const SyncPeerTransportIngressPayloadLoadOptions& options,
    SyncPeerTransportIngressPayloadLoadResult& out) {
    out = SyncPeerTransportIngressPayloadLoadResult{};
    PeerTransportLoadCompatibilityPublisher compatibility_publisher{out};
    if (options.sqlite_path.empty()) {
        return fail_result("peer transport ingress payload load sqlite_path is required");
    }
    if (!valid_sync_id(options.session_id)) {
        return fail_result(
            "peer transport ingress payload load session_id must be lowercase portable sync id");
    }
    if (options.transport_envelope_idempotency_key.rfind(
            "sync-peer-transport-envelope:v1:", 0) != 0) {
        return fail_result(
            "peer transport ingress payload load requires a namespaced transport envelope idempotency key");
    }
    std::uint64_t effective_frame_bytes = 0;
    SyncValidationResult frame_limit = resolve_peer_transport_frame_limit(
        options.max_frame_bytes,
        options.max_canonical_payload_bytes,
        effective_frame_bytes,
        "peer transport ingress payload load");
    if (!frame_limit.ok) return frame_limit;
    if (options.max_chunk_count == 0) {
        return fail_result("peer transport ingress payload load max_chunk_count must be positive");
    }

    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(
        options.sqlite_path, "peer transport ingress payload load sqlite_path");
    out.sqlite_path = sqlite_path.generic_string();
    out.session_id = options.session_id;
    out.transport_envelope_idempotency_key = options.transport_envelope_idempotency_key;

    try {
        if (!peer_transport_ingress_sqlite_exists_or_throw(
                sqlite_path, "peer transport ingress payload load")) {
            return fail_result("peer transport ingress payload load sqlite database does not exist");
        }
        PeerTransportIngressReadConnection db = open_peer_transport_ingress_sqlite_readonly_or_throw(
            sqlite_path, "peer transport ingress payload load");
        SyncSqliteConnectionAuthorityLease schema_authority_lease;
        SyncSqliteTransaction transaction(
            db.owner.db,
            "peer transport ingress payload load read snapshot",
            SyncSqliteTransactionMode::Deferred);
        schema_authority_lease = verify_peer_transport_read_schema_snapshot_or_throw(
            db, "peer transport ingress payload load snapshot schema");
        if (!sqlite_table_exists_or_throw(
                db.owner.db,
                "sync_peer_transport_ingress_envelopes",
                "peer transport ingress payload load ingress table")) {
            return fail_result("peer transport ingress payload load ingress table does not exist");
        }
        out.row_found = peer_transport_ingress_row_exists_or_throw(
            db.owner.db,
            options.session_id,
            options.transport_envelope_idempotency_key,
            "peer transport ingress payload load");
        if (!out.row_found) {
            return fail_result("peer transport ingress payload load found no ingress envelope row");
        }
        if (!sqlite_table_exists_or_throw(
                db.owner.db,
                "sync_peer_transport_ingress_payloads",
                "peer transport ingress payload load payload table")) {
            return fail_result(
                "peer transport ingress payload load found an ingress row without a durable payload table");
        }
        const PeerTransportIngressStoredPayload stored =
            load_peer_transport_ingress_stored_payload_or_throw(
                db.owner.db,
                transaction,
                options.session_id,
                options.transport_envelope_idempotency_key,
                effective_frame_bytes,
                "peer transport ingress payload load");
        out.payload_found = stored.found;
        if (!stored.found) {
            return fail_result(
                "peer transport ingress payload load found an ingress row without canonical payload evidence");
        }
        out.codec_version = stored.codec_version;
        out.canonical_frame_sha256 = stored.canonical_frame_sha256;
        out.canonical_frame_bytes = stored.canonical_frame_bytes;
        out.stored_at_epoch = stored.stored_at_epoch;
        out.payload_digest = stored.payload_digest;
        out.frame_digest_checked = true;

        PeerTransportIngressWireLimits limits;
        limits.max_frame_bytes = effective_frame_bytes;
        limits.max_chunk_count = options.max_chunk_count;
        PeerTransportIngressWirePayload decoded;
        const SyncValidationResult decoded_result = decode_peer_transport_ingress_wire_frame(
            limits, stored.canonical_frame, decoded);
        if (!decoded_result.ok) {
            return fail_result(
                "peer transport ingress payload load rejected durable canonical frame: " +
                decoded_result.reason);
        }
        out.canonical_frame_decoded = true;
        if (decoded.payload_digest != stored.payload_digest) {
            return fail_result(
                "peer transport ingress payload load decoded payload digest contradicts stored evidence");
        }
        if (decoded.transport_envelope.transport_envelope_idempotency_key !=
            options.transport_envelope_idempotency_key) {
            return fail_result(
                "peer transport ingress payload load decoded envelope key contradicts the requested key");
        }
        const persistence::CanonicalIngressProjection canonical_projection =
            canonical_peer_transport_ingress_projection(
                decoded.transport_envelope, decoded.payload_digest);
        const std::optional<PeerTransportIngressRowSnapshot> verified_row =
            load_verified_peer_transport_ingress_row_or_throw(
                db.owner.db,
                options.session_id,
                options.transport_envelope_idempotency_key,
                canonical_projection,
                "peer transport ingress payload load");
        if (!verified_row.has_value()) {
            return fail_result(
                "peer transport ingress payload load row disappeared inside its read snapshot");
        }
        out.payload_digest_checked = true;
        out.transport_envelope = std::move(decoded.transport_envelope);
        out.chunk_bytes = std::move(decoded.chunk_bytes);
        transaction.commit();
        return ok_result();
    } catch (const std::exception& e) {
        return fail_result(std::string("peer transport ingress payload load failed: ") + e.what());
    }
}

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
    SyncPeerTransportIngressProcessResult& out) {
    out = SyncPeerTransportIngressProcessResult{};
    PeerTransportProcessCompatibilityPublisher compatibility_publisher{out};
    out.sqlite_write_contention.configured_busy_timeout_ms = options.sqlite_busy_timeout_ms;
    SyncValidationResult option_result = validate_peer_transport_ingress_process_options(options);
    if (!option_result.ok) return option_result;
    std::uint64_t effective_frame_bytes = 0;
    SyncValidationResult frame_limit = resolve_peer_transport_frame_limit(
        options.max_frame_bytes,
        options.max_canonical_payload_bytes,
        effective_frame_bytes,
        "peer transport ingress process");
    if (!frame_limit.ok) return frame_limit;
    PeerTransportIngressWireLimits wire_limits;
    wire_limits.max_frame_bytes = effective_frame_bytes;
    wire_limits.max_chunk_count = options.max_chunk_count;
    std::string canonical_frame;
    std::string payload_digest;
    SyncValidationResult envelope_result = encode_peer_transport_ingress_wire_frame(
        wire_limits,
        transport_envelope,
        chunk_bytes,
        canonical_frame,
        payload_digest);
    if (!envelope_result.ok) {
        return fail_result(
            "peer transport ingress process rejected wire evidence: " + envelope_result.reason);
    }
    const persistence::CanonicalIngressProjection canonical_projection =
        canonical_peer_transport_ingress_projection(transport_envelope, payload_digest);
    if (transport_options.verify_now_epoch != options.process_now_epoch) {
        return fail_result(
            "peer transport ingress process requires transport verify_now_epoch to equal process_now_epoch so the durable claim timestamp is the exact authentication timestamp");
    }
    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(options.sqlite_path,
                                                                         "peer transport ingress process sqlite_path");
    out.sqlite_path = sqlite_path.generic_string();
    out.session_id = options.session_id;
    out.transport_envelope_idempotency_key = transport_envelope.transport_envelope_idempotency_key;
    out.payload_digest = payload_digest;

    try {
        std::optional<PeerTransportIngressRowSnapshot> receipt_probe_row;
        PeerTransportIngressClaimGeneration receipt_probe_claim_generation;
        PeerIngressReceiptEvidenceInspection receipt_evidence;
        bool receipt_probe_performed = false;
        bool receipt_probe_claim_generation_loaded = false;
        if (peer_transport_ingress_sqlite_exists_or_throw(
                sqlite_path, "peer transport ingress process receipt-first preflight")) {
            PeerTransportIngressReadConnection preflight_db = open_peer_transport_ingress_sqlite_readonly_or_throw(
                sqlite_path, "peer transport ingress process receipt-first preflight");
            SyncSqliteConnectionAuthorityLease preflight_schema_authority_lease;
            SyncSqliteTransaction preflight_snapshot(
                preflight_db.owner.db,
                "peer transport ingress process receipt-first preflight snapshot",
                SyncSqliteTransactionMode::Deferred);
            preflight_schema_authority_lease =
                verify_peer_transport_read_schema_snapshot_or_throw(
                    preflight_db,
                    "peer transport ingress process receipt-first snapshot schema");
            if (sqlite_table_exists_or_throw(preflight_db.owner.db,
                                             "sync_peer_transport_ingress_envelopes",
                                             "peer transport ingress process receipt-first preflight")) {
                receipt_probe_row = load_verified_peer_transport_ingress_row_or_throw(
                    preflight_db.owner.db,
                    options.session_id,
                    transport_envelope.transport_envelope_idempotency_key,
                    canonical_projection,
                    "peer transport ingress process receipt-first preflight");
            }
            if (receipt_probe_row.has_value() &&
                receipt_probe_row->state == "claimed" &&
                receipt_probe_row->lease_expires_at_epoch <= options.process_now_epoch) {
                if (!sqlite_table_exists_or_throw(
                        preflight_db.owner.db,
                        "sync_peer_transport_ingress_payloads",
                        "peer transport ingress process receipt-first payload table")) {
                    out.durable_payload_missing = true;
                    return fail_result(
                        "peer transport ingress process expired claim has no durable payload table");
                }
                const PeerTransportIngressStoredPayload stored =
                    load_peer_transport_ingress_stored_payload_or_throw(
                        preflight_db.owner.db,
                        preflight_snapshot,
                        options.session_id,
                        transport_envelope.transport_envelope_idempotency_key,
                        effective_frame_bytes,
                        "peer transport ingress process receipt-first payload");
                if (!stored.found) {
                    out.durable_payload_missing = true;
                    return fail_result(
                        "peer transport ingress process expired claim has no durable canonical payload");
                }
                out.durable_payload_codec_version = stored.codec_version;
                out.durable_payload_frame_bytes = stored.canonical_frame_bytes;
                out.durable_payload_frame_sha256 = stored.canonical_frame_sha256;
                if (receipt_probe_row->payload_digest() != payload_digest ||
                    stored.payload_digest != payload_digest ||
                    stored.canonical_frame != canonical_frame) {
                    return fail_result(
                        "peer transport ingress process expired-claim payload contradicts durable canonical evidence");
                }
                out.durable_payload_checked = true;
                out.durable_payload_matches_submission = true;
                out.payload_digest_checked = true;
            }
            preflight_snapshot.commit();
        }
        if (receipt_probe_row.has_value() &&
            receipt_probe_row->state == "claimed" &&
            receipt_probe_row->lease_expires_at_epoch <= options.process_now_epoch &&
            receipt_probe_row->payload_digest() == payload_digest) {
            out.expired_claim_reconciliation_attempted = true;
            receipt_probe_performed = true;
            receipt_probe_claim_generation = peer_transport_ingress_claim_generation_from_row_or_throw(
                *receipt_probe_row,
                options.session_id,
                transport_envelope.transport_envelope_idempotency_key,
                "peer transport ingress process receipt-first preflight claim generation");
            receipt_probe_claim_generation_loaded = true;
            out.claim_generation_id = receipt_probe_claim_generation.generation_id;
            SyncValidationResult receipt_probe_result = inspect_sync_peer_transport_ingress_receipt_evidence(
                transport_options,
                receipt_probe_row->claimed_at_epoch,
                remote_file_entry,
                apply_entry,
                request_plan,
                peer_schedule,
                peer_assignment,
                transport_envelope,
                chunk_bytes,
                write_options,
                receipt_evidence);
            if (!receipt_probe_result.ok) {
                receipt_evidence = PeerIngressReceiptEvidenceInspection{};
                receipt_evidence.kind = PeerIngressReceiptEvidenceKind::Unavailable;
                receipt_evidence.reason = receipt_probe_result.reason;
            }
            populate_peer_transport_receipt_evidence_result(receipt_evidence, out);
        }

        std::uint64_t attempt_after_claim = 0;
        std::uint64_t max_attempts_from_row = 0;
        std::uint64_t retry_backoff_from_row = 0;
        std::uint64_t claim_lease_expires = 0;
        PeerTransportIngressClaimGeneration claimed_generation;
        bool claimed_generation_loaded = false;
        {
            PeerTransportIngressWriteConnection db = open_peer_transport_ingress_sqlite_readwrite_or_throw(
                sqlite_path,
                options.sqlite_busy_timeout_ms,
                out.sqlite_write_contention,
                "peer transport ingress process claim");
            SyncSqliteConnectionAuthorityLease claim_schema_authority_lease;
            std::unique_ptr<SyncSqliteTransaction> claim_transaction_owner =
                begin_peer_transport_write_transaction_or_throw(
                    db.owner.db,
                    out.sqlite_write_contention,
                    "peer transport ingress process claim");
            SyncSqliteTransaction& claim_transaction = *claim_transaction_owner;
            claim_schema_authority_lease =
                verify_peer_transport_write_schema_snapshot_or_throw(
                    db, "peer transport ingress process claim transaction schema");
            std::optional<PeerTransportIngressRowSnapshot> row =
                load_verified_peer_transport_ingress_row_or_throw(
                    db.owner.db,
                    options.session_id,
                    transport_envelope.transport_envelope_idempotency_key,
                    canonical_projection,
                    "peer transport ingress process");
            out.row_found = row.has_value();
            if (!row.has_value()) {
                claim_transaction.commit();
                return fail_result("peer transport ingress process found no queued envelope row");
            }
            PeerTransportIngressRowSnapshot& verified_row = *row;
            out.state_before = verified_row.state;
            out.max_attempts = verified_row.max_attempts;
            const PeerTransportIngressStoredPayload stored =
                load_peer_transport_ingress_stored_payload_or_throw(
                    db.owner.db,
                    claim_transaction,
                    options.session_id,
                    transport_envelope.transport_envelope_idempotency_key,
                    effective_frame_bytes,
                    "peer transport ingress process durable payload");
            if (!stored.found) {
                out.durable_payload_missing = true;
                claim_transaction.commit();
                return fail_result(
                    "peer transport ingress process found a queued row without durable canonical payload evidence");
            }
            out.durable_payload_codec_version = stored.codec_version;
            out.durable_payload_frame_bytes = stored.canonical_frame_bytes;
            out.durable_payload_frame_sha256 = stored.canonical_frame_sha256;
            if (verified_row.payload_digest() != payload_digest ||
                stored.payload_digest != payload_digest) {
                claim_transaction.commit();
                return fail_result(
                    "peer transport ingress process supplied payload digest does not match queued durable evidence");
            }
            if (stored.canonical_frame != canonical_frame) {
                claim_transaction.commit();
                return fail_result(
                    "peer transport ingress process supplied payload bytes do not match the exact durable canonical frame");
            }
            out.payload_digest_checked = true;
            out.durable_payload_checked = true;
            out.durable_payload_matches_submission = true;
            out.durable_payload_claim_snapshot_checked = true;
            if (verified_row.state == "completed") {
                out.already_completed = true;
                out.state_after = "completed";
                out.attempts_after_claim = verified_row.attempts;
                claim_transaction.commit();
                return ok_result();
            }
            if (verified_row.state == "abandoned") {
                out.abandoned = true;
                out.state_after = "abandoned";
                out.attempts_after_claim = verified_row.attempts;
                claim_transaction.commit();
                return fail_result("peer transport ingress process envelope is abandoned");
            }
            if (verified_row.state == "claimed" && verified_row.lease_expires_at_epoch > options.process_now_epoch) {
                const PeerTransportIngressClaimGeneration live_claim_generation =
                    peer_transport_ingress_claim_generation_from_row_or_throw(
                        verified_row,
                        options.session_id,
                        transport_envelope.transport_envelope_idempotency_key,
                        "peer transport ingress process live claim generation");
                out.claim_generation_id = live_claim_generation.generation_id;
                out.live_claim_deferred = true;
                out.state_after = "claimed";
                out.lease_expires_at_epoch = verified_row.lease_expires_at_epoch;
                out.attempts_after_claim = verified_row.attempts;
                claim_transaction.commit();
                return ok_result();
            }
            if (verified_row.state == "failed" && verified_row.retry_at_epoch > options.process_now_epoch) {
                out.retry_backoff_deferred = true;
                out.state_after = "failed";
                out.retry_at_epoch = verified_row.retry_at_epoch;
                out.attempts_after_claim = verified_row.attempts;
                claim_transaction.commit();
                return ok_result();
            }
            const bool expired_claim = verified_row.state == "claimed" &&
                                       verified_row.lease_expires_at_epoch <= options.process_now_epoch;
            if (expired_claim) {
                const PeerTransportIngressClaimGeneration expired_claim_generation =
                    peer_transport_ingress_claim_generation_from_row_or_throw(
                        verified_row,
                        options.session_id,
                        transport_envelope.transport_envelope_idempotency_key,
                        "peer transport ingress process expired claim generation");
                out.claim_generation_id = expired_claim_generation.generation_id;
                out.expired_claim_reconciliation_attempted = true;
                out.state_after = "claimed";
                out.attempts_after_claim = verified_row.attempts;
                out.claimed_at_epoch = verified_row.claimed_at_epoch;
                out.lease_expires_at_epoch = verified_row.lease_expires_at_epoch;
                out.retry_at_epoch = verified_row.retry_at_epoch;

                if (!receipt_probe_performed ||
                    !receipt_probe_claim_generation_loaded ||
                    !same_peer_transport_ingress_claim_generation(
                        expired_claim_generation, receipt_probe_claim_generation)) {
                    out.expired_claim_reconciliation_snapshot_changed = true;
                    out.receipt_evidence_state = "not-inspected";
                    out.receipt_evidence_reason =
                        "expired claim identity changed before receipt-first reconciliation could acquire the writer lock";
                    claim_transaction.commit();
                    return ok_result();
                }

                out.expired_claim_reconciliation_snapshot_matched = true;
                const PeerIngressExpiredClaimDecision recovery_decision =
                    decide_peer_ingress_expired_claim_recovery(receipt_evidence,
                                                               verified_row.attempts,
                                                               verified_row.max_attempts);
                out.expired_claim_recovery_action =
                    peer_ingress_expired_claim_action_name(recovery_decision.action);
                out.operator_review_required = recovery_decision.operator_review_required;

                if (recovery_decision.action ==
                    PeerIngressExpiredClaimAction::CompleteFromReceipts) {
                    const std::string complete_from_receipts_sql =
                        "UPDATE sync_peer_transport_ingress_envelopes "
                        "SET state='completed', updated_at_epoch=?, completed_at_epoch=?, retry_at_epoch=?, "
                        "last_failure_reason='' WHERE " +
                        std::string(peer_transport_ingress_exact_claim_predicate_sql()) + ";";
                    SyncSqliteStmt complete_from_receipts_stmt = sqlite_prepare_or_throw(
                        db.owner.db,
                        complete_from_receipts_sql,
                        "peer transport ingress process receipt recovery complete prepare");
                    int r = 1;
                    sqlite_bind_u64_or_throw(complete_from_receipts_stmt.stmt, r++, options.process_now_epoch,
                                             "peer transport ingress process receipt recovery updated");
                    sqlite_bind_u64_or_throw(complete_from_receipts_stmt.stmt, r++, options.process_now_epoch,
                                             "peer transport ingress process receipt recovery completed at");
                    sqlite_bind_u64_or_throw(complete_from_receipts_stmt.stmt, r++, options.process_now_epoch,
                                             "peer transport ingress process receipt recovery retry at");
                    bind_peer_transport_ingress_exact_claim_predicate_or_throw(
                        complete_from_receipts_stmt.stmt,
                        r,
                        expired_claim_generation,
                        "peer transport ingress process receipt recovery complete");
                    sqlite_step_done_or_throw(complete_from_receipts_stmt.stmt,
                                              "peer transport ingress process receipt recovery complete");
                    if (sqlite3_changes(db.owner.db) != 1) {
                        throw std::runtime_error(
                            "peer transport ingress receipt recovery lost exact expired claim identity");
                    }
                    insert_peer_transport_ingress_event_or_throw(
                        db.owner.db,
                        options.session_id,
                        transport_envelope.transport_envelope_idempotency_key,
                        "completed",
                        "completed",
                        options.process_now_epoch,
                        verified_row.attempts,
                        peer_transport_ingress_claim_evidence_reason_or_throw(
                            "expired claim completed from exact durable receipt and staged-byte evidence",
                            expired_claim_generation,
                            "peer transport ingress process receipt recovery complete event evidence"),
                        "peer transport ingress process receipt recovery");

                    out.expired_claim_completed_from_receipts = true;
                    out.acceptance_completed = true;
                    out.state_after = "completed";
                    out.retry_at_epoch = options.process_now_epoch;
                    out.acceptance.transport_instance_id = transport_envelope.transport_instance_id;
                    out.acceptance.transport_key_id = transport_envelope.transport_key_id;
                    out.acceptance.transport_envelope_idempotency_key =
                        transport_envelope.transport_envelope_idempotency_key;
                    out.acceptance.peer_id = transport_envelope.peer_batch_envelope.peer_id;
                    out.acceptance.peer_session_id =
                        transport_envelope.peer_batch_envelope.peer_session_id;
                    out.acceptance.transport_envelope_checked = receipt_evidence.transport_evidence_checked;
                    out.acceptance.transport_mac_checked = receipt_evidence.transport_evidence_checked;
                    out.acceptance.transport_bounds_checked = receipt_evidence.transport_evidence_checked;
                    out.acceptance.peer_batch_acceptance_attempted = false;
                    out.acceptance.peer_batch_acceptance_completed = true;
                    out.acceptance.response_count =
                        transport_envelope.peer_batch_envelope.response_count;
                    out.acceptance.total_bytes = transport_envelope.peer_batch_envelope.total_bytes;
                    out.acceptance.chunks_written = 0;
                    out.acceptance.bytes_authenticated =
                        transport_envelope.peer_batch_envelope.total_bytes;
                    claim_transaction.commit();
                    return ok_result();
                }

                if (recovery_decision.action ==
                    PeerIngressExpiredClaimAction::AbandonAfterAuthoritativeAbsence) {
                    const std::string reason =
                        "attempt cap reached after receipt-first reconciliation proved every expected durable receipt absent";
                    const std::string abandon_after_absence_sql =
                        "UPDATE sync_peer_transport_ingress_envelopes "
                        "SET state='abandoned', updated_at_epoch=?, retry_at_epoch=?, last_failure_reason=? WHERE " +
                        std::string(peer_transport_ingress_exact_claim_predicate_sql()) + ";";
                    SyncSqliteStmt abandon_after_absence_stmt = sqlite_prepare_or_throw(
                        db.owner.db,
                        abandon_after_absence_sql,
                        "peer transport ingress process receipt recovery abandon prepare");
                    int r = 1;
                    sqlite_bind_u64_or_throw(abandon_after_absence_stmt.stmt, r++, options.process_now_epoch,
                                             "peer transport ingress process receipt recovery abandon updated");
                    sqlite_bind_u64_or_throw(abandon_after_absence_stmt.stmt, r++, options.process_now_epoch,
                                             "peer transport ingress process receipt recovery abandon retry at");
                    sqlite_bind_text_or_throw(abandon_after_absence_stmt.stmt, r++, reason,
                                              "peer transport ingress process receipt recovery abandon reason");
                    bind_peer_transport_ingress_exact_claim_predicate_or_throw(
                        abandon_after_absence_stmt.stmt,
                        r,
                        expired_claim_generation,
                        "peer transport ingress process receipt recovery abandon");
                    sqlite_step_done_or_throw(abandon_after_absence_stmt.stmt,
                                              "peer transport ingress process receipt recovery abandon");
                    if (sqlite3_changes(db.owner.db) != 1) {
                        throw std::runtime_error(
                            "peer transport ingress receipt recovery lost exact expired claim identity before abandonment");
                    }
                    insert_peer_transport_ingress_event_or_throw(
                        db.owner.db,
                        options.session_id,
                        transport_envelope.transport_envelope_idempotency_key,
                        "abandoned",
                        "abandoned",
                        options.process_now_epoch,
                        verified_row.attempts,
                        peer_transport_ingress_claim_evidence_reason_or_throw(
                            reason,
                            expired_claim_generation,
                            "peer transport ingress process receipt recovery abandon event evidence"),
                        "peer transport ingress process receipt recovery");
                    out.abandoned = true;
                    out.state_after = "abandoned";
                    out.failure_reason = reason;
                    out.retry_at_epoch = options.process_now_epoch;
                    claim_transaction.commit();
                    return fail_result("peer transport ingress process envelope reached attempt cap after durable receipt absence was proven");
                }

                if (recovery_decision.action !=
                    PeerIngressExpiredClaimAction::RetryAfterAuthoritativeAbsence) {
                    out.expired_claim_reconciliation_blocked = true;
                    out.failure_reason = recovery_decision.reason;
                    claim_transaction.commit();
                    return fail_result(
                        "peer transport ingress process expired claim reconciliation blocked: " +
                        recovery_decision.reason);
                }
                // Authoritative absence permits the ordinary next-attempt claim path below.
            }
            if (verified_row.attempts >= verified_row.max_attempts) {
                SyncSqliteStmt abandon_stmt = sqlite_prepare_or_throw(db.owner.db,
                    "UPDATE sync_peer_transport_ingress_envelopes "
                    "SET state='abandoned', updated_at_epoch=?, last_failure_reason=? "
                    "WHERE session_id=? AND transport_envelope_idempotency_key=?;",
                    "peer transport ingress process preclaim abandon prepare");
                sqlite_bind_u64_or_throw(abandon_stmt.stmt, 1, options.process_now_epoch, "peer transport ingress process preclaim abandon updated");
                sqlite_bind_text_or_throw(abandon_stmt.stmt, 2, "attempt cap reached before claim", "peer transport ingress process preclaim abandon reason");
                sqlite_bind_text_or_throw(abandon_stmt.stmt, 3, options.session_id, "peer transport ingress process preclaim abandon session");
                sqlite_bind_text_or_throw(abandon_stmt.stmt, 4, transport_envelope.transport_envelope_idempotency_key, "peer transport ingress process preclaim abandon key");
                sqlite_step_done_or_throw(abandon_stmt.stmt, "peer transport ingress process preclaim abandon");
                insert_peer_transport_ingress_event_or_throw(db.owner.db,
                                                             options.session_id,
                                                             transport_envelope.transport_envelope_idempotency_key,
                                                             "abandoned",
                                                             "abandoned",
                                                             options.process_now_epoch,
                                                             verified_row.attempts,
                                                             "attempt cap reached before claim",
                                                             "peer transport ingress process");
                out.abandoned = true;
                out.state_after = "abandoned";
                out.attempts_after_claim = verified_row.attempts;
                claim_transaction.commit();
                return fail_result("peer transport ingress process envelope reached attempt cap before claim");
            }

            if (options.require_authority_gate) {
                out.authority_decision = evaluate_peer_transport_authority_on_db_or_throw(db.owner.db,
                                                                                         sqlite_path,
                                                                                         options.session_id,
                                                                                         options.process_now_epoch,
                                                                                         transport_envelope,
                                                                                         payload_digest,
                                                                                         true,
                                                                                         "peer transport ingress process");
                if (out.authority_decision.authority_denied) {
                    SyncSqliteStmt authority_abandon_stmt = sqlite_prepare_or_throw(db.owner.db,
                        "UPDATE sync_peer_transport_ingress_envelopes "
                        "SET state='abandoned', updated_at_epoch=?, retry_at_epoch=?, last_failure_reason=? "
                        "WHERE session_id=? AND transport_envelope_idempotency_key=?;",
                        "peer transport ingress process authority abandon prepare");
                    int a = 1;
                    sqlite_bind_u64_or_throw(authority_abandon_stmt.stmt, a++, options.process_now_epoch, "peer transport ingress process authority abandon updated");
                    sqlite_bind_u64_or_throw(authority_abandon_stmt.stmt, a++, options.process_now_epoch, "peer transport ingress process authority abandon retry at");
                    sqlite_bind_text_or_throw(authority_abandon_stmt.stmt, a++, out.authority_decision.deny_reason, "peer transport ingress process authority abandon reason");
                    sqlite_bind_text_or_throw(authority_abandon_stmt.stmt, a++, options.session_id, "peer transport ingress process authority abandon session");
                    sqlite_bind_text_or_throw(authority_abandon_stmt.stmt, a++, transport_envelope.transport_envelope_idempotency_key, "peer transport ingress process authority abandon key");
                    sqlite_step_done_or_throw(authority_abandon_stmt.stmt, "peer transport ingress process authority abandon");
                    insert_peer_transport_ingress_event_or_throw(db.owner.db,
                                                                 options.session_id,
                                                                 transport_envelope.transport_envelope_idempotency_key,
                                                                 "abandoned",
                                                                 "abandoned",
                                                                 options.process_now_epoch,
                                                                 verified_row.attempts,
                                                                 out.authority_decision.deny_reason,
                                                                 "peer transport ingress process");
                    out.abandoned = true;
                    out.state_after = "abandoned";
                    out.failure_reason = out.authority_decision.deny_reason;
                    out.attempts_after_claim = verified_row.attempts;
                    claim_transaction.commit();
                    return fail_result("peer transport ingress process authority denied: " + out.authority_decision.deny_reason);
                }
            }

            attempt_after_claim = verified_row.attempts + 1;
            max_attempts_from_row = verified_row.max_attempts;
            retry_backoff_from_row = verified_row.retry_backoff_seconds;
            claim_lease_expires = checked_peer_transport_epoch_add_or_throw(
                options.process_now_epoch,
                options.lease_duration_seconds,
                "peer transport ingress process claim lease expiry");
            claimed_generation = make_peer_transport_ingress_claim_generation_or_throw(
                options.session_id,
                transport_envelope.transport_envelope_idempotency_key,
                payload_digest,
                attempt_after_claim,
                max_attempts_from_row,
                retry_backoff_from_row,
                claim_lease_expires,
                options.worker_id,
                options.worker_lease_id,
                options.process_now_epoch,
                claim_lease_expires,
                "peer transport ingress process new claim generation");
            claimed_generation_loaded = true;
            SyncSqliteStmt claim_stmt = sqlite_prepare_or_throw(db.owner.db,
                "UPDATE sync_peer_transport_ingress_envelopes "
                "SET state='claimed', attempts=?, updated_at_epoch=?, worker_id=?, worker_lease_id=?, "
                "claimed_at_epoch=?, lease_expires_at_epoch=?, retry_at_epoch=?, last_failure_reason='' "
                "WHERE session_id=? AND transport_envelope_idempotency_key=?;",
                "peer transport ingress process claim prepare");
            int i = 1;
            sqlite_bind_u64_or_throw(claim_stmt.stmt, i++, attempt_after_claim, "peer transport ingress process claim attempts");
            sqlite_bind_u64_or_throw(claim_stmt.stmt, i++, options.process_now_epoch, "peer transport ingress process claim updated");
            sqlite_bind_text_or_throw(claim_stmt.stmt, i++, options.worker_id, "peer transport ingress process claim worker");
            sqlite_bind_text_or_throw(claim_stmt.stmt, i++, options.worker_lease_id, "peer transport ingress process claim lease");
            sqlite_bind_u64_or_throw(claim_stmt.stmt, i++, options.process_now_epoch, "peer transport ingress process claim claimed at");
            sqlite_bind_u64_or_throw(claim_stmt.stmt, i++, claim_lease_expires, "peer transport ingress process claim expires");
            sqlite_bind_u64_or_throw(claim_stmt.stmt, i++, claim_lease_expires, "peer transport ingress process claim retry at");
            sqlite_bind_text_or_throw(claim_stmt.stmt, i++, options.session_id, "peer transport ingress process claim session");
            sqlite_bind_text_or_throw(claim_stmt.stmt, i++, transport_envelope.transport_envelope_idempotency_key, "peer transport ingress process claim key");
            sqlite_step_done_or_throw(claim_stmt.stmt, "peer transport ingress process claim");
            if (sqlite3_changes(db.owner.db) != 1) {
                throw std::runtime_error(
                    "peer transport ingress process could not install exact claim generation " +
                    claimed_generation.generation_id);
            }
            insert_peer_transport_ingress_event_or_throw(db.owner.db,
                                                         options.session_id,
                                                         transport_envelope.transport_envelope_idempotency_key,
                                                         "claim",
                                                         "claimed",
                                                         options.process_now_epoch,
                                                         attempt_after_claim,
                                                         peer_transport_ingress_claim_evidence_reason_or_throw(
                                                             "claimed transport envelope before authenticated acceptance",
                                                             claimed_generation,
                                                             "peer transport ingress process claim event evidence"),
                                                         "peer transport ingress process");
            claim_transaction.commit();
        }

        if (!claimed_generation_loaded) {
            throw std::runtime_error(
                "peer transport ingress process left claim transaction without an exact claim generation");
        }
        out.claim_generation_id = claimed_generation.generation_id;
        out.claimed = true;
        out.state_after = "claimed";
        out.attempts_after_claim = attempt_after_claim;
        out.max_attempts = max_attempts_from_row;
        out.claimed_at_epoch = options.process_now_epoch;
        out.lease_expires_at_epoch = claim_lease_expires;
        out.retry_at_epoch = claim_lease_expires;

        out.acceptance_attempted = true;
        SyncPeerTransportBoundChunkResponseBatchAcceptanceResult acceptance;
        SyncValidationResult acceptance_result = accept_sync_peer_transport_bound_chunk_response_batch_envelope(transport_options,
                                                                                                                remote_file_entry,
                                                                                                                apply_entry,
                                                                                                                inspection,
                                                                                                                request_options,
                                                                                                                request_plan,
                                                                                                                peer_schedule,
                                                                                                                peer_assignment,
                                                                                                                transport_envelope,
                                                                                                                chunk_bytes,
                                                                                                                write_options,
                                                                                                                acceptance);
        out.acceptance = acceptance;
        out.acceptance_completed = acceptance_result.ok && acceptance.peer_batch_acceptance_completed;

        if (options.controlled_abort_after_acceptance_before_completion && acceptance_result.ok) {
            out.controlled_abort_after_acceptance_before_completion = true;
            out.failure_reason =
                "controlled abort after durable acceptance before peer ingress completion transaction";
            return fail_result(
                "peer transport ingress process controlled abort after acceptance before completion");
        }

        PeerTransportIngressWriteConnection completion_db = open_peer_transport_ingress_sqlite_readwrite_or_throw(
            sqlite_path,
            options.sqlite_busy_timeout_ms,
            out.sqlite_write_contention,
            "peer transport ingress process completion");
        SyncSqliteConnectionAuthorityLease completion_schema_authority_lease;
        std::unique_ptr<SyncSqliteTransaction> completion_transaction_owner =
            begin_peer_transport_write_transaction_or_throw(
                completion_db.owner.db,
                out.sqlite_write_contention,
                "peer transport ingress process completion");
        SyncSqliteTransaction& completion_transaction =
            *completion_transaction_owner;
        completion_schema_authority_lease =
            verify_peer_transport_write_schema_snapshot_or_throw(
                completion_db,
                "peer transport ingress process completion transaction schema");
        const PeerTransportIngressStoredPayload completion_payload =
            require_exact_peer_transport_ingress_stored_payload_or_throw(
                completion_db.owner.db,
                completion_transaction,
                options.session_id,
                transport_envelope.transport_envelope_idempotency_key,
                canonical_frame,
                payload_digest,
                "peer transport ingress process completion");
        out.durable_payload_codec_version = completion_payload.codec_version;
        out.durable_payload_frame_bytes = completion_payload.canonical_frame_bytes;
        out.durable_payload_frame_sha256 = completion_payload.canonical_frame_sha256;
        out.durable_payload_checked = true;
        out.durable_payload_matches_submission = true;
        out.durable_payload_completion_snapshot_checked = true;
        if (acceptance_result.ok) {
            const std::string complete_sql =
                "UPDATE sync_peer_transport_ingress_envelopes "
                "SET state='completed', updated_at_epoch=?, completed_at_epoch=?, retry_at_epoch=?, "
                "last_failure_reason='' WHERE " +
                std::string(peer_transport_ingress_exact_claim_predicate_sql()) + ";";
            SyncSqliteStmt complete_stmt = sqlite_prepare_or_throw(
                completion_db.owner.db,
                complete_sql,
                "peer transport ingress process complete prepare");
            int i = 1;
            sqlite_bind_u64_or_throw(complete_stmt.stmt, i++, options.process_now_epoch, "peer transport ingress process complete updated");
            sqlite_bind_u64_or_throw(complete_stmt.stmt, i++, options.process_now_epoch, "peer transport ingress process complete completed at");
            sqlite_bind_u64_or_throw(complete_stmt.stmt, i++, options.process_now_epoch, "peer transport ingress process complete retry at");
            bind_peer_transport_ingress_exact_claim_predicate_or_throw(
                complete_stmt.stmt,
                i,
                claimed_generation,
                "peer transport ingress process complete");
            sqlite_step_done_or_throw(complete_stmt.stmt, "peer transport ingress process complete");
            if (sqlite3_changes(completion_db.owner.db) != 1) {
                throw std::runtime_error(
                    "peer transport ingress process completion rejected stale claim generation " +
                    claimed_generation.generation_id);
            }
            insert_peer_transport_ingress_event_or_throw(completion_db.owner.db,
                                                         options.session_id,
                                                         transport_envelope.transport_envelope_idempotency_key,
                                                         "completed",
                                                         "completed",
                                                         options.process_now_epoch,
                                                         attempt_after_claim,
                                                         peer_transport_ingress_claim_evidence_reason_or_throw(
                                                             "transport-bound envelope accepted and delegated to receipt-backed staging",
                                                             claimed_generation,
                                                             "peer transport ingress process completion event evidence"),
                                                         "peer transport ingress process completion");
            out.state_after = "completed";
            out.retry_at_epoch = options.process_now_epoch;
            completion_transaction.commit();
            return ok_result();
        }

        const bool now_abandoned = attempt_after_claim >= max_attempts_from_row;
        const std::string next_state = now_abandoned ? "abandoned" : "failed";
        const std::uint64_t next_retry_at = now_abandoned
            ? options.process_now_epoch
            : checked_peer_transport_epoch_add_or_throw(
                  options.process_now_epoch,
                  retry_backoff_from_row,
                  "peer transport ingress process retry epoch");
        const std::string fail_sql =
            "UPDATE sync_peer_transport_ingress_envelopes "
            "SET state=?, updated_at_epoch=?, retry_at_epoch=?, last_failure_reason=? WHERE " +
            std::string(peer_transport_ingress_exact_claim_predicate_sql()) + ";";
        SyncSqliteStmt fail_stmt = sqlite_prepare_or_throw(
            completion_db.owner.db,
            fail_sql,
            "peer transport ingress process failure prepare");
        int i = 1;
        sqlite_bind_text_or_throw(fail_stmt.stmt, i++, next_state, "peer transport ingress process failure state");
        sqlite_bind_u64_or_throw(fail_stmt.stmt, i++, options.process_now_epoch, "peer transport ingress process failure updated");
        sqlite_bind_u64_or_throw(fail_stmt.stmt, i++, next_retry_at, "peer transport ingress process failure retry");
        sqlite_bind_text_or_throw(fail_stmt.stmt, i++, acceptance_result.reason, "peer transport ingress process failure reason");
        bind_peer_transport_ingress_exact_claim_predicate_or_throw(
            fail_stmt.stmt,
            i,
            claimed_generation,
            "peer transport ingress process failure");
        sqlite_step_done_or_throw(fail_stmt.stmt, "peer transport ingress process failure");
        if (sqlite3_changes(completion_db.owner.db) != 1) {
            throw std::runtime_error(
                "peer transport ingress process failure rejected stale claim generation " +
                claimed_generation.generation_id);
        }
        insert_peer_transport_ingress_event_or_throw(completion_db.owner.db,
                                                     options.session_id,
                                                     transport_envelope.transport_envelope_idempotency_key,
                                                     now_abandoned ? "abandoned" : "failed",
                                                     next_state,
                                                     options.process_now_epoch,
                                                     attempt_after_claim,
                                                     peer_transport_ingress_claim_evidence_reason_or_throw(
                                                         acceptance_result.reason,
                                                         claimed_generation,
                                                         "peer transport ingress process failure event evidence"),
                                                     "peer transport ingress process completion");
        completion_transaction.commit();
        out.state_after = next_state;
        out.failure_reason = acceptance_result.reason;
        out.retry_at_epoch = next_retry_at;
        out.retry_scheduled = !now_abandoned;
        out.abandoned = now_abandoned;
        return fail_result("peer transport ingress process acceptance failed: " + acceptance_result.reason);

    } catch (const SyncSqliteException& e) {
        capture_peer_transport_sqlite_failure(e, out.sqlite_write_contention);
        if (out.sqlite_path.empty()) out.sqlite_path = sqlite_path.generic_string();
        return fail_result(std::string("peer transport ingress process failed: ") + e.what());
    } catch (const std::exception& e) {
        if (out.sqlite_path.empty()) out.sqlite_path = sqlite_path.generic_string();
        return fail_result(std::string("peer transport ingress process failed: ") + e.what());
    }
}

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
    SyncPeerTransportIngressProcessResult& out) {
    out = SyncPeerTransportIngressProcessResult{};
    PeerTransportProcessCompatibilityPublisher compatibility_publisher{out};
    out.sqlite_write_contention.configured_busy_timeout_ms = options.sqlite_busy_timeout_ms;
    out.sqlite_path = options.sqlite_path;
    out.session_id = options.session_id;
    out.transport_envelope_idempotency_key = transport_envelope_idempotency_key;

    SyncPeerTransportIngressPayloadLoadOptions load_options;
    load_options.sqlite_path = options.sqlite_path;
    load_options.session_id = options.session_id;
    load_options.transport_envelope_idempotency_key = transport_envelope_idempotency_key;
    load_options.max_frame_bytes = options.max_frame_bytes;
    load_options.max_chunk_count = options.max_chunk_count;
    load_options.max_canonical_payload_bytes = options.max_canonical_payload_bytes;
    SyncPeerTransportIngressPayloadLoadResult loaded;
    const SyncValidationResult load_result =
        load_sync_peer_transport_ingress_payload(load_options, loaded);
    if (!load_result.ok) {
        if (!loaded.sqlite_path.empty()) out.sqlite_path = loaded.sqlite_path;
        if (!loaded.session_id.empty()) out.session_id = loaded.session_id;
        if (!loaded.transport_envelope_idempotency_key.empty()) {
            out.transport_envelope_idempotency_key =
                loaded.transport_envelope_idempotency_key;
        }
        out.row_found = loaded.row_found;
        out.durable_payload_checked = loaded.row_found;
        out.durable_payload_missing = loaded.row_found && !loaded.payload_found;
        out.payload_digest = loaded.payload_digest;
        out.durable_payload_codec_version = loaded.codec_version;
        out.durable_payload_frame_bytes = loaded.canonical_frame_bytes;
        out.durable_payload_frame_sha256 = loaded.canonical_frame_sha256;
        return fail_result(
            "peer transport ingress durable process could not reconstruct canonical payload: " +
            load_result.reason);
    }

    return process_sync_peer_transport_ingress_envelope(
        options,
        transport_options,
        remote_file_entry,
        apply_entry,
        inspection,
        request_options,
        request_plan,
        peer_schedule,
        peer_assignment,
        loaded.transport_envelope,
        loaded.chunk_bytes,
        write_options,
        out);
}

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
    SyncPeerTransportIngressProcessResult& out) {
    if (options.transport_envelope_idempotency_key.rfind(
            "sync-peer-transport-envelope:v1:", 0) != 0) {
        out = SyncPeerTransportIngressProcessResult{};
        out.sqlite_path = options.sqlite_path;
        out.session_id = options.session_id;
        out.transport_envelope_idempotency_key =
            options.transport_envelope_idempotency_key;
        return fail_result(
            "queued peer transport ingress process requires a namespaced "
            "transport_envelope_idempotency_key in process options");
    }
    return process_sync_peer_transport_ingress_durable_payload(
        options,
        transport_options,
        remote_file_entry,
        apply_entry,
        inspection,
        request_options,
        request_plan,
        peer_schedule,
        peer_assignment,
        options.transport_envelope_idempotency_key,
        write_options,
        out);
}

SyncValidationResult load_sync_peer_transport_ingress_status(
    const SyncPeerTransportIngressStatusOptions& options,
    SyncPeerTransportIngressStatusResult& out) {
    out = SyncPeerTransportIngressStatusResult{};
    SyncValidationResult queue_options = validate_peer_transport_ingress_queue_options(options.sqlite_path,
                                                                                       options.session_id,
                                                                                       options.status_now_epoch,
                                                                                       "peer transport ingress status");
    if (!queue_options.ok) return queue_options;
    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(options.sqlite_path,
                                                                         "peer transport ingress status sqlite_path");
    out.sqlite_path = sqlite_path.generic_string();
    out.session_id = options.session_id;
    try {
        if (!peer_transport_ingress_sqlite_exists_or_throw(sqlite_path,
                                                               "peer transport ingress status")) return ok_result();
        PeerTransportIngressReadConnection db = open_peer_transport_ingress_sqlite_readonly_or_throw(
            sqlite_path,
            "peer transport ingress status");
        SyncSqliteConnectionAuthorityLease status_schema_authority_lease;
        SyncSqliteTransaction status_snapshot(
            db.owner.db,
            "peer transport ingress status read snapshot",
            SyncSqliteTransactionMode::Deferred);
        status_schema_authority_lease =
            verify_peer_transport_read_schema_snapshot_or_throw(
                db,
                "peer transport ingress status schema snapshot");
        if (!sqlite_table_exists_or_throw(db.owner.db, "sync_peer_transport_ingress_envelopes", "peer transport ingress status")) {
            status_snapshot.commit();
            return ok_result();
        }
        out.table_present = true;
        SyncSqliteStmt stmt = sqlite_prepare_or_throw(db.owner.db,
            "SELECT "
            "COUNT(*), "
            "COALESCE(SUM(CASE WHEN state IN ('queued','claimed','failed') THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state IN ('queued','claimed','failed') THEN total_bytes ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='queued' THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='queued' THEN total_bytes ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='claimed' THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='claimed' THEN total_bytes ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='completed' THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='completed' THEN total_bytes ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='failed' THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='failed' THEN total_bytes ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='abandoned' THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='abandoned' THEN total_bytes ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='failed' AND retry_at_epoch<=? THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='failed' AND retry_at_epoch>? THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='claimed' AND lease_expires_at_epoch>? THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(CASE WHEN state='claimed' AND lease_expires_at_epoch<=? THEN 1 ELSE 0 END),0), "
            "COALESCE(SUM(attempts),0) "
            "FROM sync_peer_transport_ingress_envelopes WHERE session_id=?;",
            "peer transport ingress status aggregate prepare");
        sqlite_bind_u64_or_throw(stmt.stmt, 1, options.status_now_epoch, "peer transport ingress status retry ready now");
        sqlite_bind_u64_or_throw(stmt.stmt, 2, options.status_now_epoch, "peer transport ingress status retry waiting now");
        sqlite_bind_u64_or_throw(stmt.stmt, 3, options.status_now_epoch, "peer transport ingress status live claim now");
        sqlite_bind_u64_or_throw(stmt.stmt, 4, options.status_now_epoch, "peer transport ingress status expired claim now");
        sqlite_bind_text_or_throw(stmt.stmt, 5, options.session_id, "peer transport ingress status session");
        const int rc = sqlite3_step(stmt.stmt);
        if (rc != SQLITE_ROW) throw_sqlite_exception(db.owner.db, rc, "peer transport ingress status aggregate");
        out.total_rows = sqlite_column_u64_or_throw(stmt.stmt, 0, "peer transport ingress status total");
        out.open_rows = sqlite_column_u64_or_throw(stmt.stmt, 1, "peer transport ingress status open rows");
        out.open_bytes = sqlite_column_u64_or_throw(stmt.stmt, 2, "peer transport ingress status open bytes");
        out.queued_rows = sqlite_column_u64_or_throw(stmt.stmt, 3, "peer transport ingress status queued");
        out.queued_bytes = sqlite_column_u64_or_throw(stmt.stmt, 4, "peer transport ingress status queued bytes");
        out.claimed_rows = sqlite_column_u64_or_throw(stmt.stmt, 5, "peer transport ingress status claimed");
        out.claimed_bytes = sqlite_column_u64_or_throw(stmt.stmt, 6, "peer transport ingress status claimed bytes");
        out.completed_rows = sqlite_column_u64_or_throw(stmt.stmt, 7, "peer transport ingress status completed");
        out.completed_bytes = sqlite_column_u64_or_throw(stmt.stmt, 8, "peer transport ingress status completed bytes");
        out.failed_rows = sqlite_column_u64_or_throw(stmt.stmt, 9, "peer transport ingress status failed");
        out.failed_bytes = sqlite_column_u64_or_throw(stmt.stmt, 10, "peer transport ingress status failed bytes");
        out.abandoned_rows = sqlite_column_u64_or_throw(stmt.stmt, 11, "peer transport ingress status abandoned");
        out.abandoned_bytes = sqlite_column_u64_or_throw(stmt.stmt, 12, "peer transport ingress status abandoned bytes");
        out.retry_ready_rows = sqlite_column_u64_or_throw(stmt.stmt, 13, "peer transport ingress status retry ready");
        out.retry_waiting_rows = sqlite_column_u64_or_throw(stmt.stmt, 14, "peer transport ingress status retry waiting");
        out.live_claim_rows = sqlite_column_u64_or_throw(stmt.stmt, 15, "peer transport ingress status live claims");
        out.expired_claim_rows = sqlite_column_u64_or_throw(stmt.stmt, 16, "peer transport ingress status expired claims");
        out.total_attempts = sqlite_column_u64_or_throw(stmt.stmt, 17, "peer transport ingress status attempts");
        out.terminal_retention_candidate_rows = out.completed_rows + out.abandoned_rows;
        out.terminal_retention_candidate_bytes = out.completed_bytes + out.abandoned_bytes;

        out.payload_table_present = sqlite_table_exists_or_throw(
            db.owner.db,
            "sync_peer_transport_ingress_payloads",
            "peer transport ingress status payload table");
        if (out.payload_table_present) {
            SyncSqliteStmt payload_stmt = sqlite_prepare_or_throw(
                db.owner.db,
                "SELECT "
                "COALESCE(SUM(CASE WHEN p.session_id IS NOT NULL THEN 1 ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN p.session_id IS NOT NULL THEN p.canonical_frame_bytes ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN q.state IN ('queued','claimed','failed') THEN COALESCE(p.canonical_frame_bytes,0) ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN q.state='queued' THEN COALESCE(p.canonical_frame_bytes,0) ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN q.state='claimed' THEN COALESCE(p.canonical_frame_bytes,0) ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN q.state='completed' THEN COALESCE(p.canonical_frame_bytes,0) ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN q.state='failed' THEN COALESCE(p.canonical_frame_bytes,0) ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN q.state='abandoned' THEN COALESCE(p.canonical_frame_bytes,0) ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN p.session_id IS NULL THEN 1 ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN q.state IN ('queued','claimed','failed') AND p.session_id IS NULL THEN 1 ELSE 0 END),0) "
                "FROM main.sync_peer_transport_ingress_envelopes q "
                "LEFT JOIN main.sync_peer_transport_ingress_payloads p "
                "ON p.session_id=q.session_id AND "
                "p.transport_envelope_idempotency_key=q.transport_envelope_idempotency_key "
                "WHERE q.session_id=?;",
                "peer transport ingress status payload aggregate prepare");
            sqlite_bind_text_or_throw(
                payload_stmt.stmt,
                1,
                options.session_id,
                "peer transport ingress status payload session");
            const int prc = sqlite3_step(payload_stmt.stmt);
            if (prc != SQLITE_ROW) {
                throw_sqlite_exception(db.owner.db, prc, "peer transport ingress status payload aggregate");
            }
            out.durable_payload_rows = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 0, "peer transport ingress status payload rows");
            out.durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 1, "peer transport ingress status payload frame bytes");
            out.open_durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 2, "peer transport ingress status open payload frame bytes");
            out.queued_durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 3, "peer transport ingress status queued payload frame bytes");
            out.claimed_durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 4, "peer transport ingress status claimed payload frame bytes");
            out.completed_durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 5, "peer transport ingress status completed payload frame bytes");
            out.failed_durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 6, "peer transport ingress status failed payload frame bytes");
            out.abandoned_durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 7, "peer transport ingress status abandoned payload frame bytes");
            out.rows_missing_durable_payload = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 8, "peer transport ingress status rows missing payload");
            out.open_rows_missing_durable_payload = sqlite_column_u64_or_throw(
                payload_stmt.stmt, 9, "peer transport ingress status open rows missing payload");

            SyncSqliteStmt orphan_stmt = sqlite_prepare_or_throw(
                db.owner.db,
                "SELECT COUNT(*), COALESCE(SUM(p.canonical_frame_bytes),0) "
                "FROM main.sync_peer_transport_ingress_payloads p "
                "LEFT JOIN main.sync_peer_transport_ingress_envelopes q "
                "ON q.session_id=p.session_id AND "
                "q.transport_envelope_idempotency_key=p.transport_envelope_idempotency_key "
                "WHERE p.session_id=? AND q.session_id IS NULL;",
                "peer transport ingress status orphan payload aggregate prepare");
            sqlite_bind_text_or_throw(
                orphan_stmt.stmt,
                1,
                options.session_id,
                "peer transport ingress status orphan payload session");
            const int orc = sqlite3_step(orphan_stmt.stmt);
            if (orc != SQLITE_ROW) {
                throw_sqlite_exception(db.owner.db, orc, "peer transport ingress status orphan payload aggregate");
            }
            out.orphan_durable_payload_rows = sqlite_column_u64_or_throw(
                orphan_stmt.stmt, 0, "peer transport ingress status orphan payload rows");
            out.orphan_durable_payload_frame_bytes = sqlite_column_u64_or_throw(
                orphan_stmt.stmt, 1, "peer transport ingress status orphan payload frame bytes");
        } else {
            // Metadata-only legacy queues cannot be processed safely until
            // exact canonical payload evidence is backfilled.
            out.rows_missing_durable_payload = out.total_rows;
            out.open_rows_missing_durable_payload = out.open_rows;
        }

        if (sqlite_table_exists_or_throw(db.owner.db, "sync_peer_transport_authority_denials", "peer transport ingress status authority denial table")) {
            out.authority_denial_table_present = true;
            SyncSqliteStmt denial_stmt = sqlite_prepare_or_throw(db.owner.db,
                "SELECT COUNT(*), COALESCE(SUM(total_bytes),0), "
                "COALESCE(SUM(CASE WHEN deny_reason='peer transport authority superseded key expired' THEN 1 ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN deny_reason='peer transport authority superseded key expired' THEN total_bytes ELSE 0 END),0) "
                "FROM sync_peer_transport_authority_denials WHERE session_id=?;",
                "peer transport ingress status authority denial aggregate prepare");
            sqlite_bind_text_or_throw(denial_stmt.stmt, 1, options.session_id, "peer transport ingress status authority denial session");
            const int drc = sqlite3_step(denial_stmt.stmt);
            if (drc != SQLITE_ROW) throw_sqlite_exception(db.owner.db, drc, "peer transport ingress status authority denial aggregate");
            out.authority_denied_rows = sqlite_column_u64_or_throw(denial_stmt.stmt, 0, "peer transport ingress status authority denied rows");
            out.authority_denied_bytes = sqlite_column_u64_or_throw(denial_stmt.stmt, 1, "peer transport ingress status authority denied bytes");
            out.authority_superseded_expired_denied_rows = sqlite_column_u64_or_throw(denial_stmt.stmt, 2, "peer transport ingress status authority superseded expired denied rows");
            out.authority_superseded_expired_denied_bytes = sqlite_column_u64_or_throw(denial_stmt.stmt, 3, "peer transport ingress status authority superseded expired denied bytes");
            out.authority_denial_retention_candidate_rows = out.authority_denied_rows;
            out.authority_denial_retention_candidate_bytes = out.authority_denied_bytes;
        }
        if (sqlite_table_exists_or_throw(db.owner.db, "sync_peer_transport_authority_supersessions", "peer transport ingress status authority supersession table")) {
            out.authority_supersession_table_present = true;
            SyncSqliteStmt supersession_stmt = sqlite_prepare_or_throw(db.owner.db,
                "SELECT COUNT(*) FROM sync_peer_transport_authority_supersessions WHERE session_id=?;",
                "peer transport ingress status authority supersession aggregate prepare");
            sqlite_bind_text_or_throw(supersession_stmt.stmt, 1, options.session_id, "peer transport ingress status authority supersession session");
            const int src = sqlite3_step(supersession_stmt.stmt);
            if (src != SQLITE_ROW) throw_sqlite_exception(db.owner.db, src, "peer transport ingress status authority supersession aggregate");
            out.authority_supersession_rows = sqlite_column_u64_or_throw(supersession_stmt.stmt, 0, "peer transport ingress status authority supersession rows");
        }
        if (sqlite_table_exists_or_throw(db.owner.db, "sync_peer_transport_ingress_retention_events", "peer transport ingress status retention event table")) {
            out.retention_event_table_present = true;
            SyncSqliteStmt retention_stmt = sqlite_prepare_or_throw(db.owner.db,
                "SELECT COUNT(*), "
                "COALESCE(SUM(CASE WHEN event_kind='ingress-terminal-drain' THEN drained_rows ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN event_kind='ingress-terminal-drain' THEN drained_bytes ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN event_kind='authority-denial-drain' THEN drained_rows ELSE 0 END),0), "
                "COALESCE(SUM(CASE WHEN event_kind='authority-denial-drain' THEN drained_bytes ELSE 0 END),0) "
                "FROM sync_peer_transport_ingress_retention_events WHERE session_id=?;",
                "peer transport ingress status retention event aggregate prepare");
            sqlite_bind_text_or_throw(retention_stmt.stmt, 1, options.session_id, "peer transport ingress status retention event session");
            const int rrc = sqlite3_step(retention_stmt.stmt);
            if (rrc != SQLITE_ROW) throw_sqlite_exception(db.owner.db, rrc, "peer transport ingress status retention event aggregate");
            out.retention_event_rows = sqlite_column_u64_or_throw(retention_stmt.stmt, 0, "peer transport ingress status retention events");
            out.retention_drained_ingress_rows = sqlite_column_u64_or_throw(retention_stmt.stmt, 1, "peer transport ingress status retention drained ingress rows");
            out.retention_drained_ingress_bytes = sqlite_column_u64_or_throw(retention_stmt.stmt, 2, "peer transport ingress status retention drained ingress bytes");
            out.retention_drained_authority_denial_rows = sqlite_column_u64_or_throw(retention_stmt.stmt, 3, "peer transport ingress status retention drained authority denial rows");
            out.retention_drained_authority_denial_bytes = sqlite_column_u64_or_throw(retention_stmt.stmt, 4, "peer transport ingress status retention drained authority denial bytes");
        }
        status_snapshot.commit();
        return ok_result();
    } catch (const std::exception& e) {
        return fail_result(std::string("peer transport ingress status failed: ") + e.what());
    }
}


SyncValidationResult drain_sync_peer_transport_ingress_retention(
    const SyncPeerTransportIngressRetentionOptions& options,
    SyncPeerTransportIngressRetentionResult& out) {
    out = SyncPeerTransportIngressRetentionResult{};
    out.sqlite_write_contention.configured_busy_timeout_ms = options.sqlite_busy_timeout_ms;
    SyncValidationResult option_result =
        validate_peer_transport_ingress_retention_options(options);
    if (!option_result.ok) return option_result;

    const fs::path sqlite_path = absolute_lexically_normal_path_or_throw(
        options.sqlite_path,
        "peer transport ingress retention sqlite_path");

    SyncPeerTransportIngressRetentionResult base_result;
    base_result.sqlite_path = sqlite_path.generic_string();
    base_result.session_id = options.session_id;
    base_result.operator_id = options.operator_id;
    base_result.reason = options.reason;
    base_result.dry_run = options.dry_run;
    base_result.sqlite_write_contention.configured_busy_timeout_ms =
        options.sqlite_busy_timeout_ms;
    out = base_result;

    SyncPeerTransportSqliteWriteContentionResult contention;
    contention.configured_busy_timeout_ms = options.sqlite_busy_timeout_ms;
    try {
        if (!peer_transport_ingress_sqlite_exists_or_throw(
                sqlite_path, "peer transport ingress retention")) {
            base_result.retention_noop = true;
            base_result.retention_completed = true;
            out = std::move(base_result);
            return ok_result();
        }

        std::optional<PeerTransportIngressReadConnection> readonly_db;
        std::optional<PeerTransportIngressWriteConnection> write_db;
        const SyncSqliteSerializedDbBorrow* sqlite_authority = nullptr;
        SyncSqliteConnectionAuthorityLease schema_authority_lease;
        std::unique_ptr<SyncSqliteTransaction> transaction;
        if (options.dry_run) {
            readonly_db.emplace(
                open_peer_transport_ingress_sqlite_readonly_or_throw(
                    sqlite_path,
                    "peer transport ingress retention dry-run"));
            sqlite_authority = std::addressof(readonly_db->serialized);
            transaction = std::make_unique<SyncSqliteTransaction>(
                readonly_db->owner.db,
                "peer transport ingress retention read snapshot",
                SyncSqliteTransactionMode::Deferred);
        } else {
            write_db.emplace(
                open_peer_transport_ingress_sqlite_readwrite_or_throw(
                    sqlite_path,
                    options.sqlite_busy_timeout_ms,
                    contention,
                    "peer transport ingress retention apply"));
            sqlite_authority = std::addressof(write_db->serialized);
            transaction = begin_peer_transport_write_transaction_or_throw(
                write_db->owner.db,
                contention,
                "peer transport ingress retention apply");
        }
        if (sqlite_authority == nullptr) {
            throw std::logic_error(
                "peer transport ingress retention did not select a serialized "
                "database capability");
        }
        if (options.dry_run) {
            schema_authority_lease =
                verify_peer_transport_read_schema_snapshot_or_throw(
                    *readonly_db,
                    "peer transport ingress retention dry-run schema snapshot");
        } else {
            schema_authority_lease =
                verify_peer_transport_write_schema_snapshot_or_throw(
                    *write_db,
                    "peer transport ingress retention apply schema snapshot");
        }

        SyncPeerTransportIngressRetentionResult staged = base_result;
        const bool ingress_table_present = sqlite_table_exists_or_throw(
            sqlite_authority->get(),
            "sync_peer_transport_ingress_envelopes",
            "peer transport ingress retention ingress table");
        const bool authority_denial_table_present = sqlite_table_exists_or_throw(
            sqlite_authority->get(),
            "sync_peer_transport_authority_denials",
            "peer transport ingress retention authority denial table");
        staged.retention_schema_loaded =
            ingress_table_present || authority_denial_table_present;

        // Canonical terminal verification is intentionally bounded to the
        // exact rows selected for destructive action.  Ordinary admission does
        // not pay an O(total durable payload bytes) scan on every enqueue.
        PeerTransportIngressWireLimits retention_wire_limits;
        retention_wire_limits.max_frame_bytes = options.max_frame_bytes;
        retention_wire_limits.max_chunk_count = options.max_chunk_count;
        retention_wire_limits.max_metadata_field_bytes =
            options.max_metadata_field_bytes;
        const PeerTransportRetentionSelection completed = ingress_table_present
            ? select_verified_peer_transport_terminal_retention_or_throw(
                  sqlite_authority->get(),
                  *transaction,
                  options.session_id,
                  "completed",
                  options.completed_older_than_epoch,
                  options.max_completed_rows,
                  retention_wire_limits,
                  "peer transport ingress retention completed")
            : PeerTransportRetentionSelection{};
        const PeerTransportRetentionSelection abandoned = ingress_table_present
            ? select_verified_peer_transport_terminal_retention_or_throw(
                  sqlite_authority->get(),
                  *transaction,
                  options.session_id,
                  "abandoned",
                  options.abandoned_older_than_epoch,
                  options.max_abandoned_rows,
                  retention_wire_limits,
                  "peer transport ingress retention abandoned")
            : PeerTransportRetentionSelection{};
        const PeerTransportRetentionSelection authority_denials =
            authority_denial_table_present
                ? select_peer_transport_authority_denial_retention_or_throw(
                      sqlite_authority->get(),
                      options.session_id,
                      options.authority_denial_older_than_epoch,
                      options.max_authority_denial_rows,
                      "peer transport ingress retention authority denial")
                : PeerTransportRetentionSelection{};

        staged.completed_eligible_rows = completed.rows;
        staged.completed_eligible_bytes = completed.bytes;
        staged.abandoned_eligible_rows = abandoned.rows;
        staged.abandoned_eligible_bytes = abandoned.bytes;
        staged.authority_denial_eligible_rows = authority_denials.rows;
        staged.authority_denial_eligible_bytes = authority_denials.bytes;
        staged.ingress_rows_drained = checked_peer_transport_counter_add_or_throw(
            completed.rows,
            abandoned.rows,
            "peer transport ingress retention row total");
        staged.ingress_bytes_drained = checked_peer_transport_counter_add_or_throw(
            completed.bytes,
            abandoned.bytes,
            "peer transport ingress retention byte total");
        staged.completed_rows_drained = completed.rows;
        staged.completed_bytes_drained = completed.bytes;
        staged.abandoned_rows_drained = abandoned.rows;
        staged.abandoned_bytes_drained = abandoned.bytes;
        staged.authority_denial_rows_drained = authority_denials.rows;
        staged.authority_denial_bytes_drained = authority_denials.bytes;
        staged.retention_noop = staged.ingress_rows_drained == 0 &&
                                staged.authority_denial_rows_drained == 0;

        std::uint64_t committed_audit_events = 0;
        if (!options.dry_run) {
            if (completed.rows != 0) {
                insert_peer_transport_retention_event_or_throw(
                    sqlite_authority->get(),
                    options.session_id,
                    "ingress-terminal-drain",
                    "completed",
                    options.completed_older_than_epoch,
                    options.max_completed_rows,
                    completed,
                    options.retention_now_epoch,
                    options.operator_id,
                    options.reason,
                    "peer transport ingress retention completed");
                delete_exact_peer_transport_terminal_retention_or_throw(
                    sqlite_authority->get(),
                    options.session_id,
                    "completed",
                    completed,
                    "peer transport ingress retention completed");
                ++committed_audit_events;
            }
            if (abandoned.rows != 0) {
                insert_peer_transport_retention_event_or_throw(
                    sqlite_authority->get(),
                    options.session_id,
                    "ingress-terminal-drain",
                    "abandoned",
                    options.abandoned_older_than_epoch,
                    options.max_abandoned_rows,
                    abandoned,
                    options.retention_now_epoch,
                    options.operator_id,
                    options.reason,
                    "peer transport ingress retention abandoned");
                delete_exact_peer_transport_terminal_retention_or_throw(
                    sqlite_authority->get(),
                    options.session_id,
                    "abandoned",
                    abandoned,
                    "peer transport ingress retention abandoned");
                ++committed_audit_events;
            }
            if (authority_denials.rows != 0) {
                insert_peer_transport_retention_event_or_throw(
                    sqlite_authority->get(),
                    options.session_id,
                    "authority-denial-drain",
                    "authority-denied",
                    options.authority_denial_older_than_epoch,
                    options.max_authority_denial_rows,
                    authority_denials,
                    options.retention_now_epoch,
                    options.operator_id,
                    options.reason,
                    "peer transport ingress retention authority denial");
                delete_exact_peer_transport_authority_denial_retention_or_throw(
                    sqlite_authority->get(),
                    options.session_id,
                    authority_denials,
                    "peer transport ingress retention authority denial");
                ++committed_audit_events;
            }
        }

        // No eligibility, drain, or audit-write claim escapes until the same
        // transaction that owns the exact candidates has committed.
        transaction->commit();
        staged.audit_events_written = committed_audit_events;
        staged.retention_completed = true;
        staged.sqlite_write_contention = contention;
        out = std::move(staged);
        return ok_result();
    } catch (const SyncSqliteException& e) {
        capture_peer_transport_sqlite_failure(e, contention);
        out = base_result;
        out.sqlite_write_contention = contention;
        return fail_result(
            std::string("peer transport ingress retention failed: ") + e.what());
    } catch (const std::exception& e) {
        out = base_result;
        out.sqlite_write_contention = contention;
        return fail_result(
            std::string("peer transport ingress retention failed: ") + e.what());
    }
}


void run_sync_peer_ingress_lifecycle_selftests(
    const std::function<void(bool, const std::string&)>& require) {
    run_peer_transport_ingress_claim_generation_selftests(require);
    run_peer_transport_ingress_wire_codec_selftests(require);

    PeerIngressReceiptEvidenceInspection recovery_policy_fixture;
    recovery_policy_fixture.kind = PeerIngressReceiptEvidenceKind::MatchingAll;
    PeerIngressExpiredClaimDecision recovery_policy_decision =
        decide_peer_ingress_expired_claim_recovery(recovery_policy_fixture, 1, 1);
    require(recovery_policy_decision.action ==
                PeerIngressExpiredClaimAction::CompleteFromReceipts &&
            !recovery_policy_decision.operator_review_required,
            "peer ingress recovery policy completes max-attempt expired claims from matching durable receipts");
    recovery_policy_fixture.kind = PeerIngressReceiptEvidenceKind::AuthoritativelyAbsent;
    recovery_policy_decision = decide_peer_ingress_expired_claim_recovery(recovery_policy_fixture, 1, 1);
    require(recovery_policy_decision.action ==
                PeerIngressExpiredClaimAction::AbandonAfterAuthoritativeAbsence &&
            recovery_policy_decision.attempt_cap_reached,
            "peer ingress recovery policy abandons only after receipt absence and attempt cap are both proven");
    recovery_policy_fixture.kind = PeerIngressReceiptEvidenceKind::AuthoritativelyAbsent;
    recovery_policy_decision = decide_peer_ingress_expired_claim_recovery(recovery_policy_fixture, 1, 3);
    require(recovery_policy_decision.action ==
                PeerIngressExpiredClaimAction::RetryAfterAuthoritativeAbsence &&
            !recovery_policy_decision.attempt_cap_reached &&
            !recovery_policy_decision.operator_review_required,
            "peer ingress recovery policy retries below the attempt cap only after every receipt is authoritatively absent");
    recovery_policy_fixture.kind = PeerIngressReceiptEvidenceKind::Unavailable;
    recovery_policy_fixture.reason = "fixture unavailable";
    recovery_policy_decision = decide_peer_ingress_expired_claim_recovery(recovery_policy_fixture, 1, 3);
    require(recovery_policy_decision.action ==
                PeerIngressExpiredClaimAction::BlockUnavailableEvidence &&
            recovery_policy_decision.operator_review_required &&
            recovery_policy_decision.reason == "fixture unavailable",
            "peer ingress recovery policy fails closed when receipt evidence cannot be inspected");
    recovery_policy_fixture.kind = PeerIngressReceiptEvidenceKind::Partial;
    recovery_policy_fixture.reason.clear();
    recovery_policy_decision = decide_peer_ingress_expired_claim_recovery(recovery_policy_fixture, 1, 1);
    require(recovery_policy_decision.action ==
                PeerIngressExpiredClaimAction::BlockPartialEvidence &&
            recovery_policy_decision.operator_review_required,
            "peer ingress recovery policy fails closed on partial durable receipt evidence");
    recovery_policy_fixture.kind = PeerIngressReceiptEvidenceKind::Conflicting;
    recovery_policy_fixture.reason = "fixture conflict";
    recovery_policy_decision = decide_peer_ingress_expired_claim_recovery(recovery_policy_fixture, 1, 3);
    require(recovery_policy_decision.action ==
                PeerIngressExpiredClaimAction::BlockConflictingEvidence &&
            recovery_policy_decision.operator_review_required &&
            recovery_policy_decision.reason == "fixture conflict",
            "peer ingress recovery policy preserves typed conflicting-evidence diagnostics");

    const auto ticks = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    const fs::path sentinel_db = fs::temp_directory_path() /
        ("anonsync-peer-ingress-readonly-sentinel-" + std::to_string(ticks) + ".sqlite");
    const fs::path lock_db = fs::temp_directory_path() /
        ("anonsync-peer-ingress-readonly-lock-" + std::to_string(ticks) + ".sqlite");
    const fs::path missing_authority_db = fs::temp_directory_path() /
        ("anonsync-peer-ingress-readonly-missing-authority-" + std::to_string(ticks) + ".sqlite");
    const fs::path retention_contention_report = fs::temp_directory_path() /
        ("anonsync-peer-ingress-retention-contention-" + std::to_string(ticks) + ".json");
    const fs::path supersession_contention_report = fs::temp_directory_path() /
        ("anonsync-peer-authority-supersession-contention-" + std::to_string(ticks) + ".json");
    const fs::path path_security_root = fs::temp_directory_path() /
        ("anonsync-peer-ingress-path-security-" + std::to_string(ticks));
    auto remove_sqlite_family = [](const fs::path& path) {
        std::error_code ec;
        fs::remove(path, ec);
        fs::remove(fs::path(path.string() + "-wal"), ec);
        fs::remove(fs::path(path.string() + "-shm"), ec);
        fs::remove(fs::path(path.string() + "-journal"), ec);
    };
    remove_sqlite_family(sentinel_db);
    remove_sqlite_family(lock_db);
    remove_sqlite_family(missing_authority_db);
    {
        std::error_code ec;
        fs::remove(retention_contention_report, ec);
        fs::remove(supersession_contention_report, ec);
        fs::remove_all(path_security_root, ec);
        ec.clear();
        if (!fs::create_directories(path_security_root, ec) || ec) {
            throw std::runtime_error("peer ingress path security fixture directory could not be created: " + ec.message());
        }
    }

    {
        SyncSqliteDb seed;
        int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(sentinel_db.string().c_str(), seed.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite_error_message(seed.db, "peer ingress read-only sentinel seed open"));
        }
        sqlite_exec_or_throw(seed.db,
                             "CREATE TABLE unrelated_checkpoint_guard(id INTEGER PRIMARY KEY);",
                             "peer ingress read-only sentinel seed table");
    }

    const std::string sentinel_sha_before = sha256_hex(read_file(sentinel_db.string()));
    const bool sentinel_wal_before = fs::exists(fs::path(sentinel_db.string() + "-wal"));
    const bool sentinel_shm_before = fs::exists(fs::path(sentinel_db.string() + "-shm"));

    SyncPeerTransportIngressRetentionOptions sentinel_options;
    sentinel_options.sqlite_path = sentinel_db.string();
    sentinel_options.session_id = "readonly-session";
    sentinel_options.operator_id = "readonly-operator";
    sentinel_options.reason = "prove dry-run does not bootstrap peer ingress schema";
    sentinel_options.retention_now_epoch = 20;
    sentinel_options.completed_older_than_epoch = 10;
    sentinel_options.abandoned_older_than_epoch = 10;
    sentinel_options.authority_denial_older_than_epoch = 10;
    sentinel_options.dry_run = true;
    SyncPeerTransportIngressRetentionResult sentinel_result;
    const SyncValidationResult sentinel_run = drain_sync_peer_transport_ingress_retention(sentinel_options,
                                                                                          sentinel_result);
    bool sentinel_table_present = false;
    bool ingress_table_present = true;
    bool denial_table_present = true;
    {
        PeerTransportIngressReadConnection verify = open_peer_transport_ingress_sqlite_readonly_or_throw(
            sentinel_db,
            "peer ingress read-only sentinel verify");
        sentinel_table_present = sqlite_table_exists_or_throw(verify.owner.db,
                                                               "unrelated_checkpoint_guard",
                                                               "peer ingress read-only sentinel verify guard");
        ingress_table_present = sqlite_table_exists_or_throw(verify.owner.db,
                                                              "sync_peer_transport_ingress_envelopes",
                                                              "peer ingress read-only sentinel verify ingress");
        denial_table_present = sqlite_table_exists_or_throw(verify.owner.db,
                                                             "sync_peer_transport_authority_denials",
                                                             "peer ingress read-only sentinel verify denial");
    }
    const std::string sentinel_sha_after = sha256_hex(read_file(sentinel_db.string()));
    const bool sentinel_wal_after = fs::exists(fs::path(sentinel_db.string() + "-wal"));
    const bool sentinel_shm_after = fs::exists(fs::path(sentinel_db.string() + "-shm"));
    require(sentinel_run.ok && sentinel_result.retention_completed && sentinel_result.retention_noop &&
                !sentinel_result.retention_schema_loaded && sentinel_table_present &&
                !ingress_table_present && !denial_table_present &&
                sentinel_sha_before == sentinel_sha_after &&
                sentinel_wal_before == sentinel_wal_after &&
                sentinel_shm_before == sentinel_shm_after,
            "peer ingress retention dry-run leaves an unrelated checkpoint byte-for-byte unchanged without sidecars");

    SyncPeerTransportBoundChunkResponseBatchEnvelope readonly_authority_envelope;
    readonly_authority_envelope.transport_instance_id = "transport-alpha";
    readonly_authority_envelope.transport_key_id = "transport-key-alpha";
    readonly_authority_envelope.transport_envelope_idempotency_key =
        "sync-peer-transport-envelope:v1:" + sha256_hex("rev0753-readonly-authority-envelope");
    readonly_authority_envelope.transport_mac_sha256 = sha256_hex("rev0753-readonly-authority-mac");
    readonly_authority_envelope.issued_at_epoch = 1;
    readonly_authority_envelope.expires_at_epoch = 40;
    readonly_authority_envelope.max_response_count = 1;
    readonly_authority_envelope.max_total_bytes = 4;
    readonly_authority_envelope.max_chunk_bytes = 4;
    readonly_authority_envelope.peer_batch_envelope.path.value = "folder/file.bin";
    readonly_authority_envelope.peer_batch_envelope.peer_id = "peer-alpha";
    readonly_authority_envelope.peer_batch_envelope.peer_session_id = "peer-session-alpha";
    readonly_authority_envelope.peer_batch_envelope.peer_response_batch_idempotency_key =
        "sync-peer-response-batch:v1:" + sha256_hex("rev0753-readonly-authority-batch");
    readonly_authority_envelope.peer_batch_envelope.response_count = 1;
    readonly_authority_envelope.peer_batch_envelope.total_bytes = 4;
    SyncChunkResponseEnvelope readonly_authority_response;
    readonly_authority_response.path.value = "folder/file.bin";
    readonly_authority_response.length = 4;
    readonly_authority_response.chunk_sha256 = sha256_hex("data");
    readonly_authority_envelope.peer_batch_envelope.responses.push_back(readonly_authority_response);
    const std::vector<std::string> readonly_authority_chunks = {"data"};

    SyncPeerTransportAuthorityDecisionOptions readonly_authority_options;
    readonly_authority_options.sqlite_path = sentinel_db.string();
    readonly_authority_options.session_id = "readonly-session";
    readonly_authority_options.decision_now_epoch = 20;
    const std::string authority_sha_before = sha256_hex(read_file(sentinel_db.string()));
    SyncPeerTransportAuthorityDecisionResult readonly_authority_result;
    const SyncValidationResult readonly_authority_run = evaluate_sync_peer_transport_authority(
        readonly_authority_options,
        readonly_authority_envelope,
        readonly_authority_chunks,
        readonly_authority_result);
    const std::string authority_sha_after = sha256_hex(read_file(sentinel_db.string()));
    require(!readonly_authority_run.ok && readonly_authority_result.authority_checked &&
                readonly_authority_result.authority_denied &&
                !readonly_authority_result.authority_record_found &&
                !readonly_authority_result.denial_recorded &&
                readonly_authority_result.authority_lifecycle_state == "unknown" &&
                readonly_authority_result.deny_reason == "unknown peer transport authority" &&
                authority_sha_before == authority_sha_after &&
                !fs::exists(fs::path(sentinel_db.string() + "-wal")) &&
                !fs::exists(fs::path(sentinel_db.string() + "-shm")),
            "peer transport authority inspection denies unknown authority without mutating an unrelated checkpoint");

    readonly_authority_options.sqlite_path = missing_authority_db.string();
    SyncPeerTransportAuthorityDecisionResult missing_authority_result;
    const SyncValidationResult missing_authority_run = evaluate_sync_peer_transport_authority(
        readonly_authority_options,
        readonly_authority_envelope,
        readonly_authority_chunks,
        missing_authority_result);
    require(!missing_authority_run.ok && missing_authority_result.authority_checked &&
                missing_authority_result.authority_denied &&
                missing_authority_result.deny_reason == "unknown peer transport authority" &&
                !fs::exists(missing_authority_db) &&
                !fs::exists(fs::path(missing_authority_db.string() + "-wal")) &&
                !fs::exists(fs::path(missing_authority_db.string() + "-shm")),
            "peer transport authority inspection denies unknown authority without creating a missing checkpoint");

    SyncPeerTransportAuthorityRecordOptions authority_options;
    authority_options.sqlite_path = lock_db.string();
    authority_options.session_id = "readonly-session";
    authority_options.peer_id = "peer-alpha";
    authority_options.peer_session_id = "peer-session-alpha";
    authority_options.transport_instance_id = "transport-alpha";
    authority_options.transport_key_id = "key-alpha";
    authority_options.authority_status = "trusted";
    authority_options.valid_from_epoch = 1;
    authority_options.updated_at_epoch = 2;
    authority_options.reason = "seed peer ingress lifecycle schema for read-lock test";

    const fs::path hostile_target = path_security_root / "hostile-sidecar-target.bin";
    write_file(hostile_target.string(), "peer-ingress-path-family-target-sentinel");
    const std::string hostile_target_sha = sha256_hex(read_file(hostile_target.string()));
    const std::vector<std::pair<std::string, std::string>> hostile_family_members = {
        {"main", ""},
        {"wal", "-wal"},
        {"shm", "-shm"},
        {"journal", "-journal"},
    };
    std::uint64_t hostile_epoch = 30;
    for (const auto& [member_label, suffix] : hostile_family_members) {
        const fs::path hostile_db = path_security_root /
            ("hostile-" + member_label + ".sqlite");
        const fs::path hostile_member = fs::path(hostile_db.string() + suffix);
        remove_sqlite_family(hostile_db);
        std::error_code symlink_ec;
        fs::create_symlink(hostile_target, hostile_member, symlink_ec);
        if (symlink_ec) {
            throw std::runtime_error("peer ingress hostile SQLite family symlink could not be created: " +
                                     symlink_ec.message());
        }
        SyncPeerTransportAuthorityRecordOptions hostile_options = authority_options;
        hostile_options.sqlite_path = hostile_db.string();
        hostile_options.transport_key_id = "path-family-" + member_label;
        hostile_options.updated_at_epoch = hostile_epoch++;
        hostile_options.reason = "reject hostile " + member_label + " SQLite family member";
        SyncPeerTransportAuthorityRecordResult hostile_result;
        const SyncValidationResult hostile_run = record_sync_peer_transport_authority(
            hostile_options, hostile_result);
        std::error_code status_ec;
        const bool member_is_symlink = fs::is_symlink(fs::symlink_status(hostile_member, status_ec));
        const bool main_was_not_created = suffix.empty() || !fs::exists(hostile_db);
        require(!hostile_run.ok &&
                    hostile_run.reason.find("symbolic-link SQLite family member") != std::string::npos &&
                    hostile_result.sqlite_write_contention.configured_busy_timeout_ms ==
                        hostile_options.sqlite_busy_timeout_ms &&
                    !hostile_result.sqlite_write_contention.busy_handler_installed &&
                    hostile_result.sqlite_write_contention.write_lock_attempts == 0 &&
                    member_is_symlink && main_was_not_created &&
                    sha256_hex(read_file(hostile_target.string())) == hostile_target_sha,
                "peer ingress rejects hostile " + member_label +
                    " SQLite family symlink before database or target mutation");
        std::error_code remove_ec;
        fs::remove(hostile_member, remove_ec);
    }

    const fs::path nonregular_db = path_security_root / "hostile-nonregular.sqlite";
    const fs::path nonregular_wal = fs::path(nonregular_db.string() + "-wal");
    {
        std::error_code ec;
        fs::create_directory(nonregular_wal, ec);
        if (ec) throw std::runtime_error("peer ingress non-regular sidecar fixture failed: " + ec.message());
    }
    SyncPeerTransportAuthorityRecordOptions nonregular_options = authority_options;
    nonregular_options.sqlite_path = nonregular_db.string();
    nonregular_options.transport_key_id = "path-family-nonregular";
    nonregular_options.updated_at_epoch = hostile_epoch++;
    nonregular_options.reason = "reject non-regular SQLite family member";
    SyncPeerTransportAuthorityRecordResult nonregular_result;
    const SyncValidationResult nonregular_run = record_sync_peer_transport_authority(
        nonregular_options, nonregular_result);
    require(!nonregular_run.ok &&
                nonregular_run.reason.find("non-regular SQLite family member") != std::string::npos &&
                !fs::exists(nonregular_db) && fs::is_directory(nonregular_wal) &&
                !nonregular_result.sqlite_write_contention.busy_handler_installed &&
                nonregular_result.sqlite_write_contention.write_lock_attempts == 0,
            "peer ingress rejects non-regular SQLite sidecars before opening the main database");
    {
        std::error_code ec;
        fs::remove_all(nonregular_wal, ec);
    }

    const fs::path hardlinked_db = path_security_root / "hostile-hardlinked.sqlite";
    const fs::path hardlinked_wal = fs::path(hardlinked_db.string() + "-wal");
    {
        std::error_code ec;
        fs::create_hard_link(hostile_target, hardlinked_wal, ec);
        if (ec) throw std::runtime_error("peer ingress multiply-linked sidecar fixture failed: " + ec.message());
    }
    SyncPeerTransportAuthorityRecordOptions hardlinked_options = authority_options;
    hardlinked_options.sqlite_path = hardlinked_db.string();
    hardlinked_options.transport_key_id = "path-family-hardlink";
    hardlinked_options.updated_at_epoch = hostile_epoch++;
    hardlinked_options.reason = "reject multiply-linked SQLite family member";
    SyncPeerTransportAuthorityRecordResult hardlinked_result;
    const SyncValidationResult hardlinked_run = record_sync_peer_transport_authority(
        hardlinked_options, hardlinked_result);
    std::error_code hardlink_count_ec;
    const bool hardlink_still_bound =
        fs::hard_link_count(hardlinked_wal, hardlink_count_ec) == 2 && !hardlink_count_ec;
    require(!hardlinked_run.ok &&
                hardlinked_run.reason.find("multiply-linked SQLite family member") != std::string::npos &&
                !fs::exists(hardlinked_db) && hardlink_still_bound &&
                sha256_hex(read_file(hostile_target.string())) == hostile_target_sha &&
                !hardlinked_result.sqlite_write_contention.busy_handler_installed &&
                hardlinked_result.sqlite_write_contention.write_lock_attempts == 0,
            "peer ingress rejects multiply-linked SQLite sidecars before database or target mutation");
    {
        std::error_code ec;
        fs::remove(hardlinked_wal, ec);
    }

    const fs::path redirected_parent = path_security_root / "redirect-target";
    const fs::path linked_parent = path_security_root / "linked-parent";
    {
        std::error_code ec;
        fs::create_directories(redirected_parent, ec);
        if (ec) throw std::runtime_error("peer ingress redirected parent fixture failed: " + ec.message());
        fs::create_directory_symlink(redirected_parent, linked_parent, ec);
        if (ec) throw std::runtime_error("peer ingress parent symlink fixture failed: " + ec.message());
    }
    const fs::path redirected_db = linked_parent / "must-not-be-created" / "peer.sqlite";
    SyncPeerTransportAuthorityRecordOptions redirected_options = authority_options;
    redirected_options.sqlite_path = redirected_db.string();
    redirected_options.transport_key_id = "path-family-parent";
    redirected_options.updated_at_epoch = hostile_epoch++;
    redirected_options.reason = "reject symlinked parent traversal";
    SyncPeerTransportAuthorityRecordResult redirected_result;
    const SyncValidationResult redirected_run = record_sync_peer_transport_authority(
        redirected_options, redirected_result);
    require(!redirected_run.ok &&
                redirected_run.reason.find("symbolic-link parent component") != std::string::npos &&
                !fs::exists(redirected_parent / "must-not-be-created") &&
                !redirected_result.sqlite_write_contention.busy_handler_installed &&
                redirected_result.sqlite_write_contention.write_lock_attempts == 0,
            "peer ingress rejects symlinked parent traversal before create-directories can mutate its target");
    {
        std::error_code ec;
        fs::remove(linked_parent, ec);
    }

    const fs::path secure_created_db =
        path_security_root / "secure-created-parent" / "nested" / "peer.sqlite";
    SyncPeerTransportAuthorityRecordOptions secure_created_options = authority_options;
    secure_created_options.sqlite_path = secure_created_db.string();
    secure_created_options.transport_key_id = "path-family-secure-create";
    secure_created_options.updated_at_epoch = hostile_epoch++;
    secure_created_options.reason = "prove secure parent creation and database binding";
    SyncPeerTransportAuthorityRecordResult secure_created_result;
    const SyncValidationResult secure_created_run = record_sync_peer_transport_authority(
        secure_created_options, secure_created_result);
    std::error_code secure_status_ec;
    const fs::file_status secure_parent_status = fs::symlink_status(
        path_security_root / "secure-created-parent", secure_status_ec);
    const fs::file_status secure_nested_status = fs::symlink_status(
        secure_created_db.parent_path(), secure_status_ec);
    require(secure_created_run.ok && secure_created_result.record_inserted &&
                fs::is_regular_file(secure_created_db) &&
                fs::is_directory(secure_parent_status) && !fs::is_symlink(secure_parent_status) &&
                fs::is_directory(secure_nested_status) && !fs::is_symlink(secure_nested_status) &&
                secure_created_result.sqlite_write_contention.busy_handler_installed &&
                secure_created_result.sqlite_write_contention.write_lock_attempts == 1 &&
                secure_created_result.sqlite_write_contention.write_locks_acquired == 1,
            "peer ingress securely creates missing parent directories and binds the opened database identity");

    {
        SyncSqliteDb trigger_seed;
        int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(secure_created_db.string().c_str(), trigger_seed.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite_error_message(trigger_seed.db,
                                                          "peer ingress hostile trigger seed open"));
        }
        sqlite_exec_or_throw(trigger_seed.db,
            "CREATE TABLE peer_ingress_trigger_probe(value TEXT NOT NULL);"
            "CREATE TRIGGER peer_ingress_hostile_authority_trigger "
            "AFTER INSERT ON sync_peer_transport_authority_records "
            "BEGIN INSERT INTO peer_ingress_trigger_probe(value) VALUES('fired'); END;",
            "peer ingress hostile trigger seed");
    }
    SyncPeerTransportAuthorityRecordOptions trigger_options = secure_created_options;
    trigger_options.transport_key_id = "path-family-trigger-rejected";
    trigger_options.updated_at_epoch = hostile_epoch++;
    trigger_options.reason = "prove hostile schema trigger rejection";
    SyncPeerTransportAuthorityRecordResult trigger_result;
    const SyncValidationResult trigger_run = record_sync_peer_transport_authority(
        trigger_options, trigger_result);
    sqlite3_int64 trigger_probe_rows = -1;
    sqlite3_int64 trigger_definition_rows = -1;
    {
        SyncSqliteDb trigger_verify;
        int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(secure_created_db.string().c_str(), trigger_verify.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite_error_message(trigger_verify.db,
                                                          "peer ingress hostile trigger verify open"));
        }
        trigger_probe_rows = peer_transport_sqlite_scalar_i64_or_throw(
            trigger_verify.db,
            "SELECT COUNT(*) FROM peer_ingress_trigger_probe;",
            "peer ingress hostile trigger probe count");
        trigger_definition_rows = peer_transport_sqlite_scalar_i64_or_throw(
            trigger_verify.db,
            "SELECT COUNT(*) FROM sqlite_schema WHERE type='trigger' "
            "AND name='peer_ingress_hostile_authority_trigger';",
            "peer ingress hostile trigger definition count");
    }
    require(!trigger_run.ok &&
                trigger_run.reason.find("trigger or view schema programs") != std::string::npos &&
                !trigger_result.record_inserted && trigger_probe_rows == 0 &&
                trigger_definition_rows == 1,
            "peer ingress rejects preexisting schema triggers before authority mutation");
    {
        SyncSqliteDb trigger_cleanup;
        int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(secure_created_db.string().c_str(), trigger_cleanup.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite_error_message(trigger_cleanup.db,
                                                          "peer ingress hostile trigger cleanup open"));
        }
        sqlite_exec_or_throw(
            trigger_cleanup.db,
            "DROP TRIGGER peer_ingress_hostile_authority_trigger;"
            "DROP TABLE peer_ingress_trigger_probe;",
            "peer ingress hostile trigger cleanup");
    }

    const fs::path readonly_hostile_wal = fs::path(sentinel_db.string() + "-wal");
    {
        std::error_code ec;
        fs::create_symlink(hostile_target, readonly_hostile_wal, ec);
        if (ec) throw std::runtime_error("peer ingress read-only WAL symlink fixture failed: " + ec.message());
    }
    const std::string readonly_hostile_main_sha = sha256_hex(read_file(sentinel_db.string()));
    SyncPeerTransportIngressStatusOptions hostile_status_options;
    hostile_status_options.sqlite_path = sentinel_db.string();
    hostile_status_options.session_id = "readonly-session";
    hostile_status_options.status_now_epoch = 20;
    SyncPeerTransportIngressStatusResult hostile_status_result;
    const SyncValidationResult hostile_status_run = load_sync_peer_transport_ingress_status(
        hostile_status_options, hostile_status_result);
    require(!hostile_status_run.ok &&
                hostile_status_run.reason.find("symbolic-link SQLite family member") != std::string::npos &&
                sha256_hex(read_file(sentinel_db.string())) == readonly_hostile_main_sha &&
                sha256_hex(read_file(hostile_target.string())) == hostile_target_sha &&
                fs::is_symlink(fs::symlink_status(readonly_hostile_wal)),
            "peer ingress read-only status rejects a hostile WAL sidecar without mutating either file");
    {
        std::error_code ec;
        fs::remove(readonly_hostile_wal, ec);
    }

    bool parent_rebind_rejected = false;
    const fs::path identity_parent = path_security_root / "identity-parent";
    const fs::path identity_parent_old = path_security_root / "identity-parent-old";
    {
        std::error_code ec;
        fs::create_directories(identity_parent, ec);
        if (ec) throw std::runtime_error("peer ingress parent identity fixture failed: " + ec.message());
        SqlitePathFamilyGuard identity_guard = guard_peer_transport_ingress_sqlite_path_or_throw(
            identity_parent / "peer.sqlite", false, "peer ingress parent identity fixture");
        fs::rename(identity_parent, identity_parent_old, ec);
        if (ec) throw std::runtime_error("peer ingress parent identity rename failed: " + ec.message());
        fs::create_directories(identity_parent, ec);
        if (ec) throw std::runtime_error("peer ingress replacement parent creation failed: " + ec.message());
        try {
            identity_guard.verify_family_or_throw("peer ingress parent identity recheck");
        } catch (const std::exception&) {
            parent_rebind_rejected = true;
        }
    }
    require(parent_rebind_rejected,
            "peer ingress path guard detects parent pathname rebinding while its approved directory is open");

    bool main_replacement_rejected = false;
    const fs::path identity_db = path_security_root / "identity-main.sqlite";
    const fs::path identity_db_old = path_security_root / "identity-main-old.sqlite";
    {
        SyncSqliteDb seed;
        int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(identity_db.string().c_str(), seed.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite_error_message(seed.db, "peer ingress main identity seed open"));
        }
        sqlite_exec_or_throw(seed.db, "CREATE TABLE identity_guard(id INTEGER PRIMARY KEY);",
                             "peer ingress main identity seed table");
    }
    {
        SqlitePathFamilyGuard identity_guard = guard_peer_transport_ingress_sqlite_path_or_throw(
            identity_db, false, "peer ingress main identity fixture");
        SyncSqliteDb opened;
        int flags = SQLITE_OPEN_READONLY | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
        flags |= SQLITE_OPEN_NOFOLLOW;
#endif
        if (sqlite3_open_v2(identity_db.string().c_str(), opened.db.out(), flags, nullptr) != SQLITE_OK) {
            throw std::runtime_error(sqlite_error_message(opened.db, "peer ingress main identity open"));
        }
        identity_guard.verify_open_database_or_throw(opened.db,
                                                      "peer ingress main identity initial binding");
        std::error_code ec;
        fs::rename(identity_db, identity_db_old, ec);
        if (ec) throw std::runtime_error("peer ingress main identity rename failed: " + ec.message());
        write_file(identity_db.string(), "replacement-main-file");
        try {
            identity_guard.verify_open_database_or_throw(opened.db,
                                                          "peer ingress main identity recheck");
        } catch (const std::exception&) {
            main_replacement_rejected = true;
        }
    }
    require(main_replacement_rejected,
            "peer ingress path guard detects replacement of the main database after SQLite opens it");

    SyncPeerTransportAuthorityRecordResult authority_result;
    const SyncValidationResult authority_run = record_sync_peer_transport_authority(authority_options,
                                                                                    authority_result);
    if (!authority_run.ok) throw std::runtime_error(authority_run.reason);

    SyncSqliteDb writer;
    int writer_flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    writer_flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    if (sqlite3_open_v2(lock_db.string().c_str(), writer.db.out(), writer_flags, nullptr) != SQLITE_OK) {
        throw std::runtime_error(sqlite_error_message(writer.db, "peer ingress read-only lock writer open"));
    }
    sqlite_exec_or_throw(writer.db, "BEGIN IMMEDIATE;", "peer ingress read-only lock writer begin");

    SyncPeerTransportIngressRetentionOptions lock_options = sentinel_options;
    lock_options.sqlite_path = lock_db.string();
    lock_options.reason = "prove retention dry-run coexists with active writer";
    SyncPeerTransportIngressRetentionResult lock_result;
    const SyncValidationResult lock_run = drain_sync_peer_transport_ingress_retention(lock_options, lock_result);
    require(lock_run.ok && lock_result.retention_completed && lock_result.retention_noop &&
                lock_result.retention_schema_loaded &&
                !lock_result.sqlite_write_contention.busy_handler_installed &&
                lock_result.sqlite_write_contention.write_lock_attempts == 0,
            "peer ingress retention dry-run uses a read snapshot and coexists with an active WAL writer");

    SyncPeerTransportAuthorityRecordOptions invalid_timeout_options = authority_options;
    invalid_timeout_options.transport_key_id = "key-invalid-timeout";
    invalid_timeout_options.updated_at_epoch = 3;
    invalid_timeout_options.sqlite_busy_timeout_ms = kSyncPeerTransportMaxSqliteBusyTimeoutMs + 1;
    SyncPeerTransportAuthorityRecordResult invalid_timeout_result;
    const SyncValidationResult invalid_timeout_run = record_sync_peer_transport_authority(
        invalid_timeout_options,
        invalid_timeout_result);
    require(!invalid_timeout_run.ok &&
                invalid_timeout_run.reason.find("sqlite_busy_timeout_ms exceeds") != std::string::npos &&
                invalid_timeout_result.sqlite_write_contention.configured_busy_timeout_ms ==
                    kSyncPeerTransportMaxSqliteBusyTimeoutMs + 1 &&
                !invalid_timeout_result.sqlite_write_contention.busy_handler_installed &&
                invalid_timeout_result.sqlite_write_contention.write_lock_attempts == 0,
            "peer ingress SQLite busy timeout is bounded and rejected before opening the checkpoint");

    SyncPeerTransportAuthorityRecordOptions fail_fast_options = authority_options;
    fail_fast_options.transport_key_id = "key-fail-fast";
    fail_fast_options.updated_at_epoch = 4;
    fail_fast_options.sqlite_busy_timeout_ms = 0;
    SyncPeerTransportAuthorityRecordResult fail_fast_result;
    const SyncValidationResult fail_fast_run = record_sync_peer_transport_authority(
        fail_fast_options,
        fail_fast_result);
    require(!fail_fast_run.ok &&
                fail_fast_result.sqlite_path == lock_db.generic_string() &&
                fail_fast_result.session_id == fail_fast_options.session_id &&
                fail_fast_result.transport_key_id == fail_fast_options.transport_key_id &&
                fail_fast_result.sqlite_write_contention.busy_handler_installed &&
                fail_fast_result.sqlite_write_contention.contention_observed &&
                fail_fast_result.sqlite_write_contention.sqlite_busy &&
                !fail_fast_result.sqlite_write_contention.sqlite_locked &&
                fail_fast_result.sqlite_write_contention.busy_timeout_exhausted &&
                fail_fast_result.sqlite_write_contention.busy_handler_invocations >= 1 &&
                fail_fast_result.sqlite_write_contention.write_lock_attempts == 1 &&
                fail_fast_result.sqlite_write_contention.write_locks_acquired == 0 &&
                fail_fast_result.sqlite_write_contention.primary_result_code == SQLITE_BUSY &&
                fail_fast_result.sqlite_write_contention.result_code_name == "SQLITE_BUSY" &&
                fail_fast_result.sqlite_write_contention.failure_operation ==
                    "peer transport authority record begin",
            "peer ingress SQLite fail-fast contention preserves typed lock and operation evidence");

    SyncPeerTransportAuthorityRecordOptions bounded_timeout_options = authority_options;
    bounded_timeout_options.transport_key_id = "key-bounded-timeout";
    bounded_timeout_options.updated_at_epoch = 5;
    bounded_timeout_options.sqlite_busy_timeout_ms = 80;
    const auto bounded_timeout_started = std::chrono::steady_clock::now();
    SyncPeerTransportAuthorityRecordResult bounded_timeout_result;
    const SyncValidationResult bounded_timeout_run = record_sync_peer_transport_authority(
        bounded_timeout_options,
        bounded_timeout_result);
    const std::uint64_t bounded_timeout_wall_ms = peer_transport_elapsed_ms(bounded_timeout_started);
    require(!bounded_timeout_run.ok &&
                bounded_timeout_result.sqlite_write_contention.sqlite_busy &&
                bounded_timeout_result.sqlite_write_contention.busy_timeout_exhausted &&
                bounded_timeout_result.sqlite_write_contention.busy_handler_invocations > 1 &&
                bounded_timeout_result.sqlite_write_contention.write_lock_attempts == 1 &&
                bounded_timeout_result.sqlite_write_contention.write_locks_acquired == 0 &&
                bounded_timeout_result.sqlite_write_contention.write_lock_wait_elapsed_ms >= 50 &&
                bounded_timeout_wall_ms >= 50 && bounded_timeout_wall_ms < 5000,
            "peer ingress SQLite contention uses the monotonic timeout budget without assuming scheduler time was spent inside sqlite3_sleep");

    const int retention_report_rc = run_sync_peer_ingress_retention_command(
        lock_db.string(),
        "readonly-session",
        "readonly-operator",
        "capture retention contention evidence",
        20,
        10,
        10,
        10,
        0,
        0,
        0,
        false,
        retention_contention_report.string(),
        0);
    const std::string retention_report = read_file(retention_contention_report.string());
    require(retention_report_rc == 1 &&
                retention_report.find("anonsync-sync-peer-ingress-retention-operator-report-v2") != std::string::npos &&
                retention_report.find("\"ok\": false") != std::string::npos &&
                retention_report.find("\"configured_busy_timeout_ms\": 0") != std::string::npos &&
                retention_report.find("\"sqlite_busy\": true") != std::string::npos &&
                retention_report.find("\"busy_timeout_exhausted\": true") != std::string::npos &&
                retention_report.find("\"write_lock_attempts\": 1") != std::string::npos &&
                retention_report.find("\"write_locks_acquired\": 0") != std::string::npos &&
                retention_report.find("peer transport ingress retention apply begin") != std::string::npos,
            "peer ingress retention operator report propagates typed SQLite contention evidence");

    const int supersession_report_rc = run_sync_peer_authority_supersession_command(
        lock_db.string(),
        "readonly-session",
        "readonly-operator",
        "peer-alpha",
        "peer-session-alpha",
        "transport-alpha",
        "key-alpha",
        "key-beta",
        1,
        10,
        6,
        "capture supersession contention evidence",
        supersession_contention_report.string(),
        0);
    const std::string supersession_report = read_file(supersession_contention_report.string());
    require(supersession_report_rc == 1 &&
                supersession_report.find("anonsync-sync-peer-authority-supersession-operator-report-v2") != std::string::npos &&
                supersession_report.find("\"ok\": false") != std::string::npos &&
                supersession_report.find("\"configured_busy_timeout_ms\": 0") != std::string::npos &&
                supersession_report.find("\"sqlite_busy\": true") != std::string::npos &&
                supersession_report.find("\"busy_timeout_exhausted\": true") != std::string::npos &&
                supersession_report.find("\"write_lock_attempts\": 1") != std::string::npos &&
                supersession_report.find("\"write_locks_acquired\": 0") != std::string::npos &&
                supersession_report.find("peer transport authority supersession begin") != std::string::npos,
            "peer authority supersession operator report propagates typed SQLite contention evidence");

    sqlite_exec_or_throw(writer.db, "ROLLBACK;", "peer ingress contention writer rollback");
    SyncPeerTransportSqliteWriteContentionResult handoff_contention;
    PeerTransportIngressWriteConnection handoff_db = open_peer_transport_ingress_sqlite_readwrite_or_throw(
        lock_db,
        500,
        handoff_contention,
        "peer ingress handoff contender");
    std::atomic<bool> handoff_contention_observed{false};
    handoff_db.busy_context->contention_observed_signal = &handoff_contention_observed;
    sqlite_exec_or_throw(writer.db, "BEGIN IMMEDIATE;", "peer ingress handoff writer begin");
    std::exception_ptr handoff_contender_error;
    std::thread handoff_contender([&]() {
        try {
            SyncSqliteConnectionAuthorityLease handoff_schema_authority_lease;
            std::unique_ptr<SyncSqliteTransaction> handoff_transaction_owner =
                begin_peer_transport_write_transaction_or_throw(
                    handoff_db.owner.db,
                    handoff_contention,
                    "peer ingress handoff contender");
            SyncSqliteTransaction& handoff_transaction =
                *handoff_transaction_owner;
            handoff_schema_authority_lease =
                verify_peer_transport_write_schema_snapshot_or_throw(
                    handoff_db,
                    "peer ingress handoff contender schema snapshot");
            handoff_transaction.rollback();
        } catch (...) {
            handoff_contender_error = std::current_exception();
        }
    });
    const auto handoff_signal_deadline =
        std::chrono::steady_clock::now() + std::chrono::seconds(5);
    while (!handoff_contention_observed.load(std::memory_order_acquire) &&
           std::chrono::steady_clock::now() < handoff_signal_deadline) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    sqlite_exec_or_throw(writer.db, "ROLLBACK;", "peer ingress handoff writer release");
    handoff_contender.join();
    if (handoff_contender_error) std::rethrow_exception(handoff_contender_error);
    require(handoff_contention_observed.load(std::memory_order_acquire) &&
                handoff_contention.busy_handler_installed &&
                handoff_contention.contention_observed &&
                !handoff_contention.sqlite_busy &&
                !handoff_contention.sqlite_locked &&
                !handoff_contention.busy_timeout_exhausted &&
                handoff_contention.busy_handler_invocations > 0 &&
                handoff_contention.write_lock_attempts == 1 &&
                handoff_contention.write_locks_acquired == 1,
            "peer ingress SQLite contention records a signal-coordinated successful writer handoff within the bound");

    bool epoch_overflow_rejected = false;
    try {
        (void)checked_peer_transport_epoch_add_or_throw(
            std::numeric_limits<std::uint64_t>::max(),
            1,
            "peer ingress selftest epoch");
    } catch (const std::exception&) {
        epoch_overflow_rejected = true;
    }
    require(epoch_overflow_rejected &&
                checked_peer_transport_epoch_add_or_throw(20, 5, "peer ingress selftest epoch") == 25,
            "peer ingress claim lease and retry epoch arithmetic rejects unsigned wraparound");

    remove_sqlite_family(sentinel_db);
    remove_sqlite_family(lock_db);
    remove_sqlite_family(missing_authority_db);
    {
        std::error_code ec;
        fs::remove(retention_contention_report, ec);
        fs::remove(supersession_contention_report, ec);
        fs::remove_all(path_security_root, ec);
    }
}

int run_sync_peer_ingress_lifecycle_selftest() {
    int passed = 0;
    int failed = 0;
    auto require = [&](bool condition, const std::string& message) {
        if (condition) {
            ++passed;
        } else {
            ++failed;
            std::cerr << "sync peer ingress lifecycle selftest failure: " << message << "\n";
        }
    };
    try {
        run_sync_peer_ingress_lifecycle_selftests(require);
    } catch (const std::exception& e) {
        ++failed;
        std::cerr << "sync peer ingress lifecycle selftest exception: " << e.what() << "\n";
    }
    std::cout << "anonsync_core sync peer ingress lifecycle selftest passed=" << passed
              << " failed=" << failed << "\n";
    return failed == 0 ? 0 : 2;
}

}  // namespace anonsync
