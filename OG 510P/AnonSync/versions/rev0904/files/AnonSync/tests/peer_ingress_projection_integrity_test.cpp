#include "anonsync_core.hpp"
#include "peer_ingress_test_fixture.hpp"

#include <sqlite3.h>

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#if defined(__unix__) || defined(__APPLE__)
#include <unistd.h>
#endif

namespace {

using namespace anonsync;
namespace fs = std::filesystem;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

fs::path unique_database_path(const std::string& case_name) {
    const auto ticks = std::chrono::high_resolution_clock::now()
                           .time_since_epoch()
                           .count();
#if defined(__unix__) || defined(__APPLE__)
    const long long pid = static_cast<long long>(::getpid());
#else
    const long long pid = 0;
#endif
    return fs::temp_directory_path() /
           ("anonsync-rev0764-projection-" + case_name + '-' +
            std::to_string(pid) + '-' + std::to_string(ticks) + ".sqlite");
}

void remove_sqlite_family(const fs::path& path) noexcept {
    std::error_code ignored;
    fs::remove(path, ignored);
    fs::remove(path.string() + "-wal", ignored);
    fs::remove(path.string() + "-shm", ignored);
    fs::remove(path.string() + "-journal", ignored);
}

struct SqliteCloser final {
    void operator()(sqlite3* db) const noexcept {
        if (db != nullptr) sqlite3_close_v2(db);
    }
};
using SqlitePtr = std::unique_ptr<sqlite3, SqliteCloser>;

SqlitePtr open_database(const fs::path& path, bool create = false) {
    sqlite3* raw = nullptr;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_FULLMUTEX;
    if (create) flags |= SQLITE_OPEN_CREATE;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int rc = sqlite3_open_v2(path.string().c_str(), &raw, flags, nullptr);
    if (rc != SQLITE_OK) {
        const std::string reason = raw != nullptr ? sqlite3_errmsg(raw) : "open failed";
        if (raw != nullptr) sqlite3_close_v2(raw);
        fail("could not open test database: " + reason);
    }
    sqlite3_busy_timeout(raw, 5000);
    return SqlitePtr(raw);
}

void exec_or_fail(sqlite3* db, const std::string& sql, const std::string& label) {
    char* error = nullptr;
    const int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &error);
    if (rc != SQLITE_OK) {
        const std::string reason = error != nullptr ? error : sqlite3_errmsg(db);
        if (error != nullptr) sqlite3_free(error);
        fail(label + ": " + reason);
    }
}

std::uint64_t scalar_u64(sqlite3* db,
                         const std::string& sql,
                         const std::string& label) {
    sqlite3_stmt* raw_stmt = nullptr;
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &raw_stmt, nullptr) != SQLITE_OK ||
        raw_stmt == nullptr) {
        fail(label + " prepare: " + sqlite3_errmsg(db));
    }
    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(
        raw_stmt, &sqlite3_finalize);
    if (sqlite3_step(stmt.get()) != SQLITE_ROW ||
        sqlite3_column_type(stmt.get(), 0) != SQLITE_INTEGER) {
        fail(label + " did not return one integer row");
    }
    const sqlite3_int64 value = sqlite3_column_int64(stmt.get(), 0);
    if (value < 0) fail(label + " returned a negative count");
    return static_cast<std::uint64_t>(value);
}

void corrupt_projection(const fs::path& path,
                        const std::string& session_id,
                        const std::string& transport_key,
                        const std::string& column,
                        const std::string& sql_expression) {
    static const std::vector<std::string> allowed_columns{
        "transport_instance_id",
        "transport_key_id",
        "peer_id",
        "peer_session_id",
        "peer_response_batch_idempotency_key",
        "path",
        "payload_digest",
        "response_count",
        "total_bytes",
        "issued_at_epoch",
        "expires_at_epoch",
        "attempts",
        "retry_at_epoch",
        "worker_id",
    };
    bool allowed = false;
    for (const auto& candidate : allowed_columns) {
        if (candidate == column) allowed = true;
    }
    if (!allowed) fail("test attempted to mutate an unapproved column");

    SqlitePtr db = open_database(path);
    exec_or_fail(db.get(), "PRAGMA foreign_keys=ON;", "enable foreign keys");
    exec_or_fail(db.get(),
                 "PRAGMA ignore_check_constraints=ON;",
                 "enable corruption fixture");
    const std::string sql =
        "UPDATE sync_peer_transport_ingress_envelopes SET " + column + '=' +
        sql_expression +
        " WHERE session_id=?1 AND transport_envelope_idempotency_key=?2;";
    sqlite3_stmt* raw_stmt = nullptr;
    const int prepare_rc =
        sqlite3_prepare_v2(db.get(), sql.c_str(), -1, &raw_stmt, nullptr);
    if (prepare_rc != SQLITE_OK || raw_stmt == nullptr) {
        fail("could not prepare corruption update: " +
             std::string(sqlite3_errmsg(db.get())));
    }
    std::unique_ptr<sqlite3_stmt, decltype(&sqlite3_finalize)> stmt(
        raw_stmt, &sqlite3_finalize);
    if (sqlite3_bind_text(stmt.get(),
                          1,
                          session_id.data(),
                          static_cast<int>(session_id.size()),
                          SQLITE_TRANSIENT) != SQLITE_OK ||
        sqlite3_bind_text(stmt.get(),
                          2,
                          transport_key.data(),
                          static_cast<int>(transport_key.size()),
                          SQLITE_TRANSIENT) != SQLITE_OK) {
        fail("could not bind corruption update");
    }
    if (sqlite3_step(stmt.get()) != SQLITE_DONE) {
        fail("could not apply corruption update: " +
             std::string(sqlite3_errmsg(db.get())));
    }
    if (sqlite3_changes(db.get()) != 1) {
        fail("corruption update did not affect exactly one row");
    }
    exec_or_fail(db.get(),
                 "PRAGMA ignore_check_constraints=OFF;",
                 "disable corruption fixture");
}

void require_safe_failure(const SyncValidationResult& result,
                          const std::string& expected_fragment,
                          const std::string& context,
                          std::uint64_t& checks) {
    require(!result.ok, context + " unexpectedly succeeded", checks);
    require(result.reason.find(expected_fragment) != std::string::npos,
            context + " did not identify the contradicted projection: " +
                result.reason,
            checks);
    const std::vector<std::string> forbidden{
        "forged-sensitive-marker",
        "docs/wire-fixture.bin",
        "peer-response-batch-evidence-v1",
    };
    for (const auto& value : forbidden) {
        require(result.reason.find(value) == std::string::npos,
                context + " leaked persisted/canonical content: " + result.reason,
                checks);
    }
}

struct MutationCase final {
    std::string name;
    std::string column;
    std::string expression;
    std::string expected_failure;
};

void run_mutation_case(const MutationCase& mutation, std::uint64_t& checks) {
    const fs::path database_path = unique_database_path(mutation.name);
    remove_sqlite_family(database_path);
    try {
        const auto fixture =
            anonsync::test::make_peer_ingress_fixture("projection-" + mutation.name);
        const std::string session_id = "projection-integrity";

        SyncPeerTransportIngressEnqueueOptions enqueue_options;
        enqueue_options.sqlite_path = fs::absolute(database_path)
                                          .lexically_normal()
                                          .string();
        enqueue_options.session_id = session_id;
        enqueue_options.enqueue_now_epoch = 101;
        enqueue_options.max_frame_bytes = 64 * 1024;
        enqueue_options.max_canonical_payload_bytes = 64 * 1024;
        enqueue_options.max_chunk_count = 16;

        SyncPeerTransportIngressEnqueueResult enqueue_result;
        const SyncValidationResult enqueued =
            enqueue_sync_peer_transport_ingress_envelope(
                enqueue_options,
                fixture.envelope,
                fixture.chunks,
                enqueue_result);
        require(enqueued.ok,
                mutation.name + " fixture enqueue failed: " + enqueued.reason,
                checks);
        require(enqueue_result.row_inserted &&
                    enqueue_result.payload_frame_stored,
                mutation.name + " fixture did not create both durable rows",
                checks);

        SyncPeerTransportIngressPayloadLoadOptions load_options;
        load_options.sqlite_path = enqueue_options.sqlite_path;
        load_options.session_id = session_id;
        load_options.transport_envelope_idempotency_key =
            fixture.envelope.transport_envelope_idempotency_key;
        load_options.max_frame_bytes = 64 * 1024;
        load_options.max_canonical_payload_bytes = 64 * 1024;
        load_options.max_chunk_count = 16;
        SyncPeerTransportIngressPayloadLoadResult clean_load;
        const SyncValidationResult clean_loaded =
            load_sync_peer_transport_ingress_payload(load_options, clean_load);
        require(clean_loaded.ok,
                mutation.name + " clean payload load failed: " +
                    clean_loaded.reason,
                checks);
        require(clean_load.payload_digest_checked &&
                    clean_load.canonical_frame_decoded,
                mutation.name + " clean load did not cross the verified boundary",
                checks);

        corrupt_projection(
            database_path,
            session_id,
            fixture.envelope.transport_envelope_idempotency_key,
            mutation.column,
            mutation.expression);

        SyncPeerTransportIngressPayloadLoadResult corrupted_load;
        require_safe_failure(
            load_sync_peer_transport_ingress_payload(load_options, corrupted_load),
            mutation.expected_failure,
            mutation.name + " durable load",
            checks);
        require(corrupted_load.row_found && corrupted_load.payload_found &&
                    corrupted_load.canonical_frame_decoded,
                mutation.name +
                    " failed before reconstructing the authoritative frame",
                checks);
        require(!corrupted_load.payload_digest_checked,
                mutation.name +
                    " published digest authority after projection rejection",
                checks);

        enqueue_options.enqueue_now_epoch = 102;
        SyncPeerTransportIngressEnqueueResult duplicate_result;
        require_safe_failure(
            enqueue_sync_peer_transport_ingress_envelope(
                enqueue_options,
                fixture.envelope,
                fixture.chunks,
                duplicate_result),
            mutation.expected_failure,
            mutation.name + " duplicate enqueue",
            checks);
        require(!duplicate_result.row_already_present,
                mutation.name +
                    " published duplicate success before projection verification",
                checks);

        SyncPeerTransportIngressProcessOptions process_options;
        process_options.sqlite_path = enqueue_options.sqlite_path;
        process_options.session_id = session_id;
        process_options.worker_id = "projection-worker";
        process_options.worker_lease_id = "projection-lease";
        process_options.process_now_epoch = 150;
        process_options.lease_duration_seconds = 30;
        process_options.max_frame_bytes = 64 * 1024;
        process_options.max_canonical_payload_bytes = 64 * 1024;
        process_options.max_chunk_count = 16;
        SyncPeerTransportEnvelopeVerifyOptions verify_options;
        verify_options.verify_now_epoch = process_options.process_now_epoch;
        SyncPeerTransportIngressProcessResult process_result;
        require_safe_failure(
            process_sync_peer_transport_ingress_envelope(
                process_options,
                verify_options,
                SyncManifestEntry{},
                SyncLocalApplyPlanEntry{},
                SyncStagedTransferInspectionResult{},
                SyncChunkRequestPlanOptions{},
                SyncChunkRequestPlanResult{},
                SyncPeerChunkScheduleResult{},
                SyncPeerChunkAssignment{},
                fixture.envelope,
                fixture.chunks,
                SyncChunkReceiptWriteOptions{},
                process_result),
            mutation.expected_failure,
            mutation.name + " writer preflight",
            checks);
        require(!process_result.claimed && process_result.claim_generation_id.empty(),
                mutation.name +
                    " acquired claim authority after projection rejection",
                checks);

        remove_sqlite_family(database_path);
    } catch (...) {
        remove_sqlite_family(database_path);
        throw;
    }
}

void verify_observed_duplicate_is_distinct_from_committed_mutation(
    std::uint64_t& checks) {
    const fs::path database_path = unique_database_path("duplicate-observation");
    remove_sqlite_family(database_path);
    try {
        const auto fixture =
            anonsync::test::make_peer_ingress_fixture("duplicate-observation");
        SyncPeerTransportIngressEnqueueOptions options;
        options.sqlite_path =
            fs::absolute(database_path).lexically_normal().string();
        options.session_id = "projection-integrity";
        options.enqueue_now_epoch = 101;
        options.max_frame_bytes = 64 * 1024;
        options.max_canonical_payload_bytes = 64 * 1024;
        options.max_chunk_count = 16;

        SyncPeerTransportIngressEnqueueResult initial;
        const SyncValidationResult first =
            enqueue_sync_peer_transport_ingress_envelope(
                options, fixture.envelope, fixture.chunks, initial);
        require(first.ok && initial.row_inserted && initial.payload_frame_stored,
                "duplicate-observation fixture enqueue failed: " + first.reason,
                checks);

        {
            SqlitePtr db = open_database(database_path);
            exec_or_fail(
                db.get(),
                "UPDATE sync_peer_transport_ingress_payloads "
                "SET canonical_frame=zeroblob(length(canonical_frame));",
                "corrupt duplicate payload bytes");
        }

        options.enqueue_now_epoch = 102;
        SyncPeerTransportIngressEnqueueResult replay;
        const SyncValidationResult replayed =
            enqueue_sync_peer_transport_ingress_envelope(
                options, fixture.envelope, fixture.chunks, replay);
        require(!replayed.ok,
                "contradictory duplicate payload unexpectedly succeeded",
                checks);
        require(replayed.reason.find(
                    "stored canonical frame digest differs from blob bytes") !=
                    std::string::npos,
                "contradictory duplicate failure did not identify payload corruption",
                checks);
        require(replay.row_already_present,
                "verified pre-existing row observation was suppressed by later failure",
                checks);
        require(!replay.row_inserted && !replay.payload_frame_stored &&
                    !replay.payload_frame_already_present &&
                    !replay.legacy_payload_backfilled,
                "failed replay advertised a mutation that did not commit",
                checks);

        SqlitePtr db = open_database(database_path);
        require(scalar_u64(
                    db.get(),
                    "SELECT COUNT(*) FROM sync_peer_transport_ingress_envelopes;",
                    "duplicate parent count") == 1,
                "failed duplicate replay changed parent-row cardinality",
                checks);
        require(scalar_u64(
                    db.get(),
                    "SELECT COUNT(*) FROM sync_peer_transport_ingress_payloads;",
                    "duplicate payload count") == 1,
                "failed duplicate replay changed payload-row cardinality",
                checks);
        remove_sqlite_family(database_path);
    } catch (...) {
        remove_sqlite_family(database_path);
        throw;
    }
}

void verify_commit_gated_enqueue_publication(std::uint64_t& checks) {
    const fs::path database_path = unique_database_path("commit-publication");
    remove_sqlite_family(database_path);
    try {
        {
            SqlitePtr db = open_database(database_path, true);
            exec_or_fail(
                db.get(),
                "CREATE TABLE sync_peer_transport_ingress_events(dummy TEXT);",
                "create malformed event sink");
        }

        const auto fixture =
            anonsync::test::make_peer_ingress_fixture("commit-publication");
        SyncPeerTransportIngressEnqueueOptions options;
        options.sqlite_path =
            fs::absolute(database_path).lexically_normal().string();
        options.session_id = "projection-integrity";
        options.enqueue_now_epoch = 101;
        options.max_frame_bytes = 64 * 1024;
        options.max_canonical_payload_bytes = 64 * 1024;
        options.max_chunk_count = 16;
        SyncPeerTransportIngressEnqueueResult out;
        const SyncValidationResult result =
            enqueue_sync_peer_transport_ingress_envelope(
                options, fixture.envelope, fixture.chunks, out);
        require(!result.ok,
                "enqueue succeeded despite an unusable durable event sink",
                checks);
        require(result.reason.find("reserved schema object count mismatch") !=
                    std::string::npos,
                "partial-schema failure was not attributable",
                checks);
        require(!out.row_inserted && !out.payload_frame_stored &&
                    !out.canonical_payload_persisted,
                "rolled-back enqueue advertised committed durable evidence",
                checks);

        SqlitePtr db = open_database(database_path);
        require(scalar_u64(
                    db.get(),
                    "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='table' "
                    "AND name='sync_peer_transport_ingress_envelopes';",
                    "rolled-back parent schema count") == 0,
                "partial-schema refusal silently healed the parent table",
                checks);
        require(scalar_u64(
                    db.get(),
                    "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='table' "
                    "AND name='sync_peer_transport_ingress_payloads';",
                    "rolled-back payload schema count") == 0,
                "partial-schema refusal silently healed the payload table",
                checks);
        require(scalar_u64(
                    db.get(),
                    "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='table' "
                    "AND name='sync_peer_transport_ingress_events';",
                    "malformed event schema count") == 1,
                "partial-schema refusal altered the preexisting malformed object",
                checks);
        remove_sqlite_family(database_path);
    } catch (...) {
        remove_sqlite_family(database_path);
        throw;
    }
}

}  // namespace

int main() {
    std::uint64_t checks = 0;
    try {
        const std::vector<MutationCase> mutations{
            {"transport-instance",
             "transport_instance_id",
             "'forged-sensitive-marker'",
             "transport_instance_id:different"},
            {"transport-key",
             "transport_key_id",
             "'forged-sensitive-marker'",
             "transport_key_id:different"},
            {"peer-id",
             "peer_id",
             "'forged-sensitive-marker'",
             "peer_id:different"},
            {"peer-session",
             "peer_session_id",
             "'forged-sensitive-marker'",
             "peer_session_id:different"},
            {"peer-response-key",
             "peer_response_batch_idempotency_key",
             "'forged-sensitive-marker'",
             "peer_response_batch_idempotency_key:different"},
            {"path",
             "path",
             "'forged-sensitive-marker'",
             "logical_path:different"},
            {"payload-digest",
             "payload_digest",
             "'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'",
             "payload_digest_sha256:different"},
            {"response-count",
             "response_count",
             "response_count + 1",
             "response_count:different"},
            {"total-bytes",
             "total_bytes",
             "total_bytes + 1",
             "total_bytes:different"},
            {"issued-at",
             "issued_at_epoch",
             "issued_at_epoch + 1",
             "issued_at_epoch:different"},
            {"expires-at",
             "expires_at_epoch",
             "expires_at_epoch + 1",
             "expires_at_epoch:different"},
            {"total-bytes-storage-class",
             "total_bytes",
             "CAST(x'3136' AS BLOB)",
             "sqlite_projection_decode[total_bytes:wrong_storage_class]"},
            {"attempt-above-cap",
             "attempts",
             "max_attempts + 1",
             "attempts above max_attempts"},
            {"queued-retry-state",
             "retry_at_epoch",
             "150",
             "non-initial queued lifecycle shape"},
            {"partial-claim-identity",
             "worker_id",
             "'forged-sensitive-marker'",
             "incomplete retained claim identity"},
        };
        for (const auto& mutation : mutations) {
            run_mutation_case(mutation, checks);
        }
        verify_observed_duplicate_is_distinct_from_committed_mutation(checks);
        verify_commit_gated_enqueue_publication(checks);
        std::cout << "peer ingress projection integrity: " << checks
                  << " checks passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "peer ingress projection integrity: " << error.what()
                  << '\n';
        return 1;
    }
}
