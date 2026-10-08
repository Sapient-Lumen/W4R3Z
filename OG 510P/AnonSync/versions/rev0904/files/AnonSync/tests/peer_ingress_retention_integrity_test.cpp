#include "anonsync_core.hpp"
#include "peer_ingress_test_fixture.hpp"
#include "sync_peer_ingress_retention.hpp"

#include <sqlite3.h>

#include <cstdint>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>

namespace fs = std::filesystem;

namespace {

using anonsync::SyncPeerTransportIngressEnqueueOptions;
using anonsync::SyncPeerTransportIngressEnqueueResult;
using anonsync::SyncPeerTransportIngressRetentionOptions;
using anonsync::SyncPeerTransportIngressRetentionResult;
using anonsync::SyncValidationResult;
using anonsync::PeerTransportIngressWireLimits;
using anonsync::PeerTransportRetentionSelection;
using anonsync::drain_sync_peer_transport_ingress_retention;
using anonsync::enqueue_sync_peer_transport_ingress_envelope;
using anonsync::peer_transport_retention_event_idempotency_key;
using anonsync::select_verified_peer_transport_terminal_retention_or_throw;
using anonsync::test::PeerIngressFixture;
using anonsync::test::make_peer_ingress_fixture;

struct Db final {
    sqlite3* handle = nullptr;

    explicit Db(const fs::path& path) {
        const int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
        const int rc = sqlite3_open_v2(path.string().c_str(), &handle, flags, nullptr);
        if (rc != SQLITE_OK) {
            const std::string message = handle == nullptr
                ? "SQLite open failed"
                : sqlite3_errmsg(handle);
            if (handle != nullptr) sqlite3_close(handle);
            handle = nullptr;
            throw std::runtime_error(message);
        }
        sqlite3_extended_result_codes(handle, 1);
    }

    ~Db() {
        if (handle != nullptr) sqlite3_close(handle);
    }

    Db(const Db&) = delete;
    Db& operator=(const Db&) = delete;
};

struct Stmt final {
    sqlite3_stmt* handle = nullptr;

    Stmt(sqlite3* db, const char* sql) {
        const int rc = sqlite3_prepare_v2(db, sql, -1, &handle, nullptr);
        if (rc != SQLITE_OK) {
            throw std::runtime_error(std::string("SQLite prepare failed: ") + sqlite3_errmsg(db));
        }
    }

    ~Stmt() {
        if (handle != nullptr) sqlite3_finalize(handle);
    }

    Stmt(const Stmt&) = delete;
    Stmt& operator=(const Stmt&) = delete;
};

void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

void exec_or_throw(sqlite3* db, const std::string& sql) {
    char* error = nullptr;
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &error);
    if (rc != SQLITE_OK) {
        const std::string detail = error == nullptr ? sqlite3_errmsg(db) : error;
        sqlite3_free(error);
        throw std::runtime_error("SQLite exec failed: " + detail);
    }
}

void bind_text_or_throw(sqlite3* db,
                        sqlite3_stmt* stmt,
                        int index,
                        const std::string& value) {
    const int rc = sqlite3_bind_text(
        stmt, index, value.data(), static_cast<int>(value.size()), SQLITE_TRANSIENT);
    if (rc != SQLITE_OK) {
        throw std::runtime_error(std::string("SQLite text bind failed: ") + sqlite3_errmsg(db));
    }
}

void bind_u64_or_throw(sqlite3* db,
                       sqlite3_stmt* stmt,
                       int index,
                       std::uint64_t value) {
    require(value <= static_cast<std::uint64_t>(INT64_MAX),
            "test fixture integer exceeds SQLite range");
    const int rc = sqlite3_bind_int64(stmt, index, static_cast<sqlite3_int64>(value));
    if (rc != SQLITE_OK) {
        throw std::runtime_error(std::string("SQLite integer bind failed: ") + sqlite3_errmsg(db));
    }
}

void step_done_or_throw(sqlite3* db, sqlite3_stmt* stmt) {
    const int rc = sqlite3_step(stmt);
    if (rc != SQLITE_DONE) {
        throw std::runtime_error(std::string("SQLite step failed: ") + sqlite3_errmsg(db));
    }
}

std::uint64_t scalar_u64(const fs::path& path, const std::string& sql) {
    Db db(path);
    Stmt stmt(db.handle, sql.c_str());
    const int rc = sqlite3_step(stmt.handle);
    if (rc != SQLITE_ROW || sqlite3_column_type(stmt.handle, 0) != SQLITE_INTEGER) {
        throw std::runtime_error("SQLite scalar query did not return an integer row");
    }
    const sqlite3_int64 value = sqlite3_column_int64(stmt.handle, 0);
    require(value >= 0, "SQLite scalar query returned a negative value");
    require(sqlite3_step(stmt.handle) == SQLITE_DONE,
            "SQLite scalar query returned multiple rows");
    return static_cast<std::uint64_t>(value);
}

void remove_sqlite_family(const fs::path& path) {
    std::error_code ec;
    fs::remove(path, ec);
    fs::remove(fs::path(path.string() + "-wal"), ec);
    fs::remove(fs::path(path.string() + "-shm"), ec);
    fs::remove(fs::path(path.string() + "-journal"), ec);
}

struct TempSqlite final {
    fs::path path;

    explicit TempSqlite(std::string suffix) {
        static std::uint64_t sequence = 0;
        path = fs::temp_directory_path() /
               ("anonsync-rev0765-retention-" + std::move(suffix) + "-" +
                std::to_string(++sequence) + ".sqlite");
        remove_sqlite_family(path);
    }

    ~TempSqlite() { remove_sqlite_family(path); }
};

struct TerminalFixture {
    PeerIngressFixture ingress;
    std::string session_id;
    std::uint64_t updated_at_epoch = 220;
};

TerminalFixture enqueue_completed_fixture(const fs::path& path,
                                           const std::string& key_seed) {
    TerminalFixture out;
    out.ingress = make_peer_ingress_fixture(key_seed);
    out.session_id = "retention-session";

    SyncPeerTransportIngressEnqueueOptions enqueue;
    enqueue.sqlite_path = path.string();
    enqueue.session_id = out.session_id;
    enqueue.enqueue_now_epoch = 150;
    enqueue.max_attempts = 3;
    enqueue.retry_backoff_seconds = 10;
    SyncPeerTransportIngressEnqueueResult result;
    const SyncValidationResult enqueued = enqueue_sync_peer_transport_ingress_envelope(
        enqueue, out.ingress.envelope, out.ingress.chunks, result);
    require(enqueued.ok && result.row_inserted && result.payload_frame_stored,
            "canonical terminal fixture enqueue failed: " + enqueued.reason);

    Db db(path);
    Stmt stmt(
        db.handle,
        "UPDATE sync_peer_transport_ingress_envelopes "
        "SET state='completed', updated_at_epoch=?, completed_at_epoch=?, retry_at_epoch=? "
        "WHERE session_id=? AND transport_envelope_idempotency_key=?;");
    bind_u64_or_throw(db.handle, stmt.handle, 1, out.updated_at_epoch);
    bind_u64_or_throw(db.handle, stmt.handle, 2, out.updated_at_epoch);
    bind_u64_or_throw(db.handle, stmt.handle, 3, out.updated_at_epoch);
    bind_text_or_throw(db.handle, stmt.handle, 4, out.session_id);
    bind_text_or_throw(
        db.handle,
        stmt.handle,
        5,
        out.ingress.envelope.transport_envelope_idempotency_key);
    step_done_or_throw(db.handle, stmt.handle);
    require(sqlite3_changes64(db.handle) == 1,
            "terminal fixture did not update exactly one parent row");
    return out;
}

SyncPeerTransportIngressRetentionOptions retention_options(
    const fs::path& path,
    const TerminalFixture& fixture,
    std::string reason) {
    SyncPeerTransportIngressRetentionOptions options;
    options.sqlite_path = path.string();
    options.session_id = fixture.session_id;
    options.operator_id = "operator-retention";
    options.reason = std::move(reason);
    options.retention_now_epoch = 300;
    options.completed_older_than_epoch = 250;
    options.max_completed_rows = 1;
    return options;
}

void require_failure_result_has_no_uncommitted_claims(
    const SyncPeerTransportIngressRetentionResult& result,
    const std::string& label) {
    require(!result.retention_completed, label + " reported retention_completed after failure");
    require(!result.retention_schema_loaded,
            label + " published staged schema state after failure");
    require(result.completed_eligible_rows == 0 &&
                result.completed_eligible_bytes == 0 &&
                result.abandoned_eligible_rows == 0 &&
                result.abandoned_eligible_bytes == 0 &&
                result.authority_denial_eligible_rows == 0 &&
                result.authority_denial_eligible_bytes == 0,
            label + " published staged eligibility after failure");
    require(result.ingress_rows_drained == 0 &&
                result.ingress_bytes_drained == 0 &&
                result.completed_rows_drained == 0 &&
                result.completed_bytes_drained == 0 &&
                result.abandoned_rows_drained == 0 &&
                result.abandoned_bytes_drained == 0 &&
                result.authority_denial_rows_drained == 0 &&
                result.authority_denial_bytes_drained == 0 &&
                result.audit_events_written == 0,
            label + " published rolled-back drain or audit mutations");
}

void test_canonical_projection_corruption_fails_closed() {
    TempSqlite temp("projection-corruption");
    const TerminalFixture fixture = enqueue_completed_fixture(temp.path, "projection-corruption");
    const std::uint64_t canonical_bytes = fixture.ingress.envelope.peer_batch_envelope.total_bytes;
    {
        Db db(temp.path);
        Stmt stmt(
            db.handle,
            "UPDATE sync_peer_transport_ingress_envelopes SET total_bytes=? "
            "WHERE session_id=? AND transport_envelope_idempotency_key=?;");
        bind_u64_or_throw(db.handle, stmt.handle, 1, canonical_bytes + 1);
        bind_text_or_throw(db.handle, stmt.handle, 2, fixture.session_id);
        bind_text_or_throw(
            db.handle,
            stmt.handle,
            3,
            fixture.ingress.envelope.transport_envelope_idempotency_key);
        step_done_or_throw(db.handle, stmt.handle);
        require(sqlite3_changes64(db.handle) == 1,
                "projection corruption fixture did not mutate one row");
    }

    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path, fixture, "projection corruption must not authorize retention");
    SyncPeerTransportIngressRetentionResult result;
    const SyncValidationResult run =
        drain_sync_peer_transport_ingress_retention(options, result);
    require(!run.ok, "retention accepted a contradictory parent projection");
    require(run.reason.find("persisted ingress projection") != std::string::npos,
            "projection mismatch did not produce a safe field-level diagnostic");
    require(run.reason.find(fixture.ingress.envelope.transport_envelope_idempotency_key) ==
                std::string::npos &&
                run.reason.find(fixture.ingress.envelope.peer_batch_envelope.path.value) ==
                    std::string::npos,
            "projection mismatch diagnostic leaked durable peer evidence values");
    require_failure_result_has_no_uncommitted_claims(result, "projection corruption");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 0,
            "projection contradiction mutated parent, payload, or retention audit state");
}

void test_missing_canonical_payload_fails_closed() {
    TempSqlite temp("missing-payload");
    const TerminalFixture fixture = enqueue_completed_fixture(temp.path, "missing-payload");
    {
        Db db(temp.path);
        exec_or_throw(db.handle, "PRAGMA foreign_keys=OFF;");
        Stmt stmt(
            db.handle,
            "DELETE FROM sync_peer_transport_ingress_payloads "
            "WHERE session_id=? AND transport_envelope_idempotency_key=?;");
        bind_text_or_throw(db.handle, stmt.handle, 1, fixture.session_id);
        bind_text_or_throw(
            db.handle,
            stmt.handle,
            2,
            fixture.ingress.envelope.transport_envelope_idempotency_key);
        step_done_or_throw(db.handle, stmt.handle);
        require(sqlite3_changes64(db.handle) == 1,
                "missing-payload fixture did not remove one payload row");
    }

    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path, fixture, "missing canonical payload must not authorize retention");
    SyncPeerTransportIngressRetentionResult result;
    const SyncValidationResult run =
        drain_sync_peer_transport_ingress_retention(options, result);
    require(!run.ok &&
                run.reason.find("lacks canonical durable payload evidence") !=
                    std::string::npos,
            "retention accepted a terminal row without canonical payload evidence");
    require_failure_result_has_no_uncommitted_claims(result, "missing payload");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 0,
            "missing-payload rejection mutated parent or audit state");
}

void test_cross_domain_delete_dependency_is_rejected_before_mutation() {
    TempSqlite temp("delete-rollback");
    const TerminalFixture fixture = enqueue_completed_fixture(temp.path, "delete-rollback");
    {
        Db db(temp.path);
        exec_or_throw(db.handle, "PRAGMA foreign_keys=ON;");
        exec_or_throw(
            db.handle,
            "CREATE TABLE retention_delete_blocker("
            "session_id TEXT NOT NULL,"
            "transport_envelope_idempotency_key TEXT NOT NULL,"
            "PRIMARY KEY(session_id, transport_envelope_idempotency_key),"
            "FOREIGN KEY(session_id, transport_envelope_idempotency_key) REFERENCES "
            "sync_peer_transport_ingress_envelopes(session_id, transport_envelope_idempotency_key) "
            "ON UPDATE RESTRICT ON DELETE RESTRICT"
            ");");
        Stmt stmt(
            db.handle,
            "INSERT INTO retention_delete_blocker(session_id, transport_envelope_idempotency_key) "
            "VALUES(?,?);");
        bind_text_or_throw(db.handle, stmt.handle, 1, fixture.session_id);
        bind_text_or_throw(
            db.handle,
            stmt.handle,
            2,
            fixture.ingress.envelope.transport_envelope_idempotency_key);
        step_done_or_throw(db.handle, stmt.handle);
    }

    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path, fixture, "foreign key blocker must force atomic rollback");
    SyncPeerTransportIngressRetentionResult failed_result;
    const SyncValidationResult failed =
        drain_sync_peer_transport_ingress_retention(options, failed_result);
    require(!failed.ok &&
                failed.reason.find("cohosted with an unreviewed schema") !=
                    std::string::npos,
            "cross-domain delete blocker was not rejected by schema attestation");
    require_failure_result_has_no_uncommitted_claims(
        failed_result, "cross-domain delete dependency rejection");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 0,
            "schema dependency rejection mutated peer or audit state");

    {
        Db db(temp.path);
        exec_or_throw(db.handle, "DROP TABLE retention_delete_blocker;");
    }
    SyncPeerTransportIngressRetentionResult committed_result;
    const SyncValidationResult committed =
        drain_sync_peer_transport_ingress_retention(options, committed_result);
    const std::uint64_t canonical_bytes = fixture.ingress.envelope.peer_batch_envelope.total_bytes;
    require(committed.ok && committed_result.retention_completed &&
                committed_result.completed_eligible_rows == 1 &&
                committed_result.completed_eligible_bytes == canonical_bytes &&
                committed_result.completed_rows_drained == 1 &&
                committed_result.completed_bytes_drained == canonical_bytes &&
                committed_result.ingress_rows_drained == 1 &&
                committed_result.ingress_bytes_drained == canonical_bytes &&
                committed_result.audit_events_written == 1,
            "retention did not commit exact canonical candidate/audit results after blocker removal");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 0 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;") == 0 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 1,
            "committed retention did not delete parent/payload and preserve one audit event");
}

void insert_exact_retention_event(const fs::path& path,
                                  const TerminalFixture& fixture,
                                  const SyncPeerTransportIngressRetentionOptions& options) {
    Db db(path);
    anonsync::SyncSqliteTransaction transaction(
        db.handle,
        "retention collision fixture transaction",
        anonsync::SyncSqliteTransactionMode::Deferred);
    const PeerTransportRetentionSelection selection =
        select_verified_peer_transport_terminal_retention_or_throw(
            db.handle,
            transaction,
            fixture.session_id,
            "completed",
            options.completed_older_than_epoch,
            options.max_completed_rows,
            PeerTransportIngressWireLimits{},
            "retention collision fixture");
    require(selection.rows == 1,
            "retention collision fixture did not select exactly one canonical row");
    const std::string event_key = peer_transport_retention_event_idempotency_key(
        fixture.session_id,
        "ingress-terminal-drain",
        "completed",
        options.completed_older_than_epoch,
        options.max_completed_rows,
        selection.rows,
        selection.bytes,
        selection.candidate_set_sha256,
        options.retention_now_epoch,
        options.operator_id,
        options.reason);
    Stmt stmt(
        db.handle,
        "INSERT INTO sync_peer_transport_ingress_retention_events("
        "session_id, retention_event_idempotency_key, event_kind, state_drained, older_than_epoch, "
        "max_rows, drained_rows, drained_bytes, retained_at_epoch, operator_id, reason) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?);");
    int i = 1;
    bind_text_or_throw(db.handle, stmt.handle, i++, fixture.session_id);
    bind_text_or_throw(db.handle, stmt.handle, i++, event_key);
    bind_text_or_throw(db.handle, stmt.handle, i++, "ingress-terminal-drain");
    bind_text_or_throw(db.handle, stmt.handle, i++, "completed");
    bind_u64_or_throw(db.handle, stmt.handle, i++, options.completed_older_than_epoch);
    bind_u64_or_throw(db.handle, stmt.handle, i++, options.max_completed_rows);
    bind_u64_or_throw(db.handle, stmt.handle, i++, selection.rows);
    bind_u64_or_throw(db.handle, stmt.handle, i++, selection.bytes);
    bind_u64_or_throw(db.handle, stmt.handle, i++, options.retention_now_epoch);
    bind_text_or_throw(db.handle, stmt.handle, i++, options.operator_id);
    bind_text_or_throw(db.handle, stmt.handle, i++, options.reason);
    step_done_or_throw(db.handle, stmt.handle);
    transaction.commit();
}

void test_configured_wire_limits_fail_closed_before_destruction() {
    TempSqlite temp("wire-limit");
    const TerminalFixture fixture = enqueue_completed_fixture(temp.path, "wire-limit");
    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path, fixture, "destructive verifier must honor explicit canonical frame limits");
    options.max_frame_bytes = 1;

    SyncPeerTransportIngressRetentionResult result;
    const SyncValidationResult run =
        drain_sync_peer_transport_ingress_retention(options, result);
    require(!run.ok && run.reason.find("frame") != std::string::npos,
            "retention ignored an explicit canonical frame decode limit");
    require_failure_result_has_no_uncommitted_claims(result, "canonical frame limit");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 0,
            "canonical frame limit rejection mutated durable evidence");
}

void insert_authority_denial_fixture(const fs::path& path,
                                     const TerminalFixture& fixture,
                                     const std::string& payload_digest) {
    Db db(path);
    Stmt stmt(
        db.handle,
        "INSERT INTO sync_peer_transport_authority_denials("
        "session_id, transport_envelope_idempotency_key, peer_id, peer_session_id, "
        "transport_instance_id, transport_key_id, payload_digest, total_bytes, "
        "denied_at_epoch, deny_reason) VALUES(?,?,?,?,?,?,?,?,?,?);");
    int i = 1;
    bind_text_or_throw(db.handle, stmt.handle, i++, fixture.session_id);
    bind_text_or_throw(db.handle, stmt.handle, i++,
                       "sync-peer-transport-envelope:v1:authority-denial-fixture");
    bind_text_or_throw(db.handle, stmt.handle, i++, "peer-a");
    bind_text_or_throw(db.handle, stmt.handle, i++, "peer-session-a");
    bind_text_or_throw(db.handle, stmt.handle, i++, "transport-a");
    bind_text_or_throw(db.handle, stmt.handle, i++, "transport-key-a");
    bind_text_or_throw(db.handle, stmt.handle, i++, payload_digest);
    bind_u64_or_throw(db.handle, stmt.handle, i++,
                      fixture.ingress.envelope.peer_batch_envelope.total_bytes);
    bind_u64_or_throw(db.handle, stmt.handle, i++, 220);
    bind_text_or_throw(db.handle, stmt.handle, i++, "authority evidence fixture");
    step_done_or_throw(db.handle, stmt.handle);
}

void test_authority_denial_evidence_is_strictly_decoded_and_committed() {
    TempSqlite temp("authority-denial");
    const TerminalFixture fixture = enqueue_completed_fixture(temp.path, "authority-denial");
    insert_authority_denial_fixture(temp.path, fixture, std::string(64, 'A'));

    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path, fixture, "authority denial retention requires exact durable evidence");
    options.completed_older_than_epoch = 0;
    options.max_completed_rows = 0;
    options.authority_denial_older_than_epoch = 250;
    options.max_authority_denial_rows = 1;

    SyncPeerTransportIngressRetentionResult malformed_result;
    const SyncValidationResult malformed_run =
        drain_sync_peer_transport_ingress_retention(options, malformed_result);
    require(!malformed_run.ok &&
                malformed_run.reason.find("invalid durable shape") != std::string::npos,
            "authority denial retention accepted a malformed payload digest projection");
    require_failure_result_has_no_uncommitted_claims(
        malformed_result, "malformed authority denial");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_authority_denials;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 0,
            "malformed authority denial rejection mutated durable history");

    {
        Db db(temp.path);
        exec_or_throw(
            db.handle,
            "UPDATE sync_peer_transport_authority_denials "
            "SET payload_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';");
    }
    SyncPeerTransportIngressRetentionResult committed_result;
    const SyncValidationResult committed_run =
        drain_sync_peer_transport_ingress_retention(options, committed_result);
    require(committed_run.ok && committed_result.retention_completed &&
                committed_result.authority_denial_eligible_rows == 1 &&
                committed_result.authority_denial_rows_drained == 1 &&
                committed_result.audit_events_written == 1,
            "valid authority denial evidence did not commit exact retention");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_authority_denials;") == 0 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events "
                           "WHERE retention_event_idempotency_key LIKE "
                           "'sync-peer-transport-ingress-retention-event:v2:%';") == 1,
            "authority denial retention did not preserve a v2 candidate commitment");
}

void test_preexisting_event_is_contradiction_not_silent_success() {
    TempSqlite temp("event-collision");
    const TerminalFixture fixture = enqueue_completed_fixture(temp.path, "event-collision");
    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path, fixture, "preexisting audit plus live row is contradictory history");
    insert_exact_retention_event(temp.path, fixture, options);

    SyncPeerTransportIngressRetentionResult result;
    const SyncValidationResult run =
        drain_sync_peer_transport_ingress_retention(options, result);
    require(!run.ok &&
                (run.reason.find("UNIQUE") != std::string::npos ||
                 run.reason.find("constraint") != std::string::npos),
            "preexisting exact retention event was silently ignored");
    require_failure_result_has_no_uncommitted_claims(result, "retention event collision");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 1,
            "event collision deleted live evidence or changed historical audit cardinality");
}

void test_equal_aggregate_batches_receive_distinct_candidate_commitments() {
    TempSqlite temp("candidate-set-identity");
    const TerminalFixture first = enqueue_completed_fixture(temp.path, "same-batch-a");
    const TerminalFixture second = enqueue_completed_fixture(temp.path, "same-batch-b");
    require(first.ingress.envelope.peer_batch_envelope.total_bytes ==
                second.ingress.envelope.peer_batch_envelope.total_bytes,
            "candidate-set collision fixture requires equal aggregate byte totals");

    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path,
        first,
        "equal aggregate batches must retain distinct exact candidate commitments");
    options.max_completed_rows = 1;

    SyncPeerTransportIngressRetentionResult first_result;
    const SyncValidationResult first_run =
        drain_sync_peer_transport_ingress_retention(options, first_result);
    require(first_run.ok && first_result.completed_rows_drained == 1 &&
                first_result.audit_events_written == 1,
            "first equal-aggregate retention batch did not commit");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 1,
            "first equal-aggregate retention batch changed unexpected cardinalities");

    SyncPeerTransportIngressRetentionResult second_result;
    const SyncValidationResult second_run =
        drain_sync_peer_transport_ingress_retention(options, second_result);
    require(second_run.ok && second_result.completed_rows_drained == 1 &&
                second_result.audit_events_written == 1,
            "second equal-aggregate retention batch collided with aggregate-only history");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 0 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;") == 0 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 2 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(DISTINCT retention_event_idempotency_key) "
                           "FROM sync_peer_transport_ingress_retention_events;") == 2 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events "
                           "WHERE retention_event_idempotency_key LIKE "
                           "'sync-peer-transport-ingress-retention-event:v2:%';") == 2,
            "candidate-set commitments did not distinguish equal aggregate batches");

    SyncPeerTransportIngressRetentionResult noop_result;
    const SyncValidationResult noop_run =
        drain_sync_peer_transport_ingress_retention(options, noop_result);
    require(noop_run.ok && noop_result.retention_completed &&
                noop_result.retention_noop && noop_result.audit_events_written == 0 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 2,
            "empty replay created another retention event or failed to report a no-op");
}

void test_dry_run_preserves_compatibility_without_mutation() {
    TempSqlite temp("dry-run");
    const TerminalFixture fixture = enqueue_completed_fixture(temp.path, "dry-run");
    SyncPeerTransportIngressRetentionOptions options = retention_options(
        temp.path, fixture, "dry-run reports canonical would-drain evidence");
    options.dry_run = true;
    SyncPeerTransportIngressRetentionResult result;
    const SyncValidationResult run =
        drain_sync_peer_transport_ingress_retention(options, result);
    const std::uint64_t canonical_bytes = fixture.ingress.envelope.peer_batch_envelope.total_bytes;
    require(run.ok && result.retention_completed && result.dry_run &&
                result.completed_eligible_rows == 1 &&
                result.completed_eligible_bytes == canonical_bytes &&
                result.completed_rows_drained == 1 &&
                result.completed_bytes_drained == canonical_bytes &&
                result.audit_events_written == 0,
            "dry-run did not preserve would-drain compatibility with canonical accounting");
    require(scalar_u64(temp.path,
                       "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;") == 1 &&
                scalar_u64(temp.path,
                           "SELECT COUNT(*) FROM sync_peer_transport_ingress_retention_events;") == 0,
            "dry-run mutated parent, payload, or retention audit state");
}

}  // namespace

int main() {
    try {
        test_canonical_projection_corruption_fails_closed();
        test_missing_canonical_payload_fails_closed();
        test_cross_domain_delete_dependency_is_rejected_before_mutation();
        test_configured_wire_limits_fail_closed_before_destruction();
        test_authority_denial_evidence_is_strictly_decoded_and_committed();
        test_preexisting_event_is_contradiction_not_silent_success();
        test_equal_aggregate_batches_receive_distinct_candidate_commitments();
        test_dry_run_preserves_compatibility_without_mutation();
        std::cout << "peer ingress retention integrity tests passed\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "peer ingress retention integrity test failed: " << e.what() << '\n';
        return 1;
    }
}
