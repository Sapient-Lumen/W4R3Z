#include "peer_ingress_test_fixture.hpp"
#include "sync_peer_ingress_payload_store.hpp"
#include "sync_peer_ingress_wire.hpp"
#include "sync_sqlite_runtime.hpp"
#include "sync_sqlite_support.hpp"

#include <chrono>
#include <cstdint>
#include <exception>
#include <filesystem>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

#include <sqlite3.h>

#if defined(__unix__) || defined(__APPLE__)
#include <sys/wait.h>
#include <unistd.h>
#endif

namespace {

using namespace anonsync;
using anonsync::test::PeerIngressFixture;

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Function>
void require_throws(Function&& function,
                    const std::string& expected_fragment,
                    const std::string& message,
                    std::uint64_t& checks) {
    ++checks;
    try {
        function();
    } catch (const std::exception& e) {
        if (expected_fragment.empty() ||
            std::string(e.what()).find(expected_fragment) != std::string::npos) {
            return;
        }
        fail(message + ": unexpected error: " + e.what());
    }
    fail(message + ": no exception was thrown");
}

std::filesystem::path unique_database_path() {
    const auto ticks = std::chrono::high_resolution_clock::now().time_since_epoch().count();
#if defined(__unix__) || defined(__APPLE__)
    const long long pid = static_cast<long long>(::getpid());
#else
    const long long pid = 0;
#endif
    return std::filesystem::temp_directory_path() /
           ("anonsync-rev0773-payload-store-" + std::to_string(pid) + "-" +
            std::to_string(ticks) + ".sqlite");
}

struct SqliteCloser {
    void operator()(sqlite3* db) const noexcept {
        if (db != nullptr) sqlite3_close_v2(db);
    }
};

using SqlitePtr = std::unique_ptr<sqlite3, SqliteCloser>;

SqlitePtr open_database(const std::filesystem::path& path) {
    sqlite3* raw = nullptr;
    int flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int rc = sqlite3_open_v2(path.string().c_str(), &raw, flags, nullptr);
    if (rc != SQLITE_OK) {
        const std::string reason = raw != nullptr ? sqlite3_errmsg(raw) : "unknown open error";
        if (raw != nullptr) sqlite3_close_v2(raw);
        fail("test database open failed: " + reason);
    }
    return SqlitePtr(raw);
}

void create_test_parent_schema(sqlite3* db, const std::string& label) {
    sqlite_exec_or_throw(
        db,
        "CREATE TABLE sync_peer_transport_ingress_envelopes("
        "session_id TEXT NOT NULL,"
        "transport_envelope_idempotency_key TEXT NOT NULL,"
        "PRIMARY KEY(session_id, transport_envelope_idempotency_key));",
        label);
}

std::uint64_t scalar_count(sqlite3* db,
                           const std::string& sql,
                           const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db, sql, label + " prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " query");
    return sqlite_column_u64_or_throw(stmt.stmt, 0, label + " value");
}

void insert_parent(sqlite3* db,
                   const std::string& session_id,
                   const std::string& key,
                   const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "INSERT INTO sync_peer_transport_ingress_envelopes("
        "session_id, transport_envelope_idempotency_key) VALUES(?,?);",
        label + " prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, session_id, label + " session");
    sqlite_bind_text_or_throw(stmt.stmt, 2, key, label + " key");
    sqlite_step_done_or_throw(stmt.stmt, label + " insert");
}

struct EncodedFixture {
    PeerIngressFixture fixture;
    std::string frame;
    std::string payload_digest;
};

EncodedFixture encode_fixture(const std::string& key_seed,
                              const PeerTransportIngressWireLimits& limits) {
    EncodedFixture out;
    out.fixture = anonsync::test::make_peer_ingress_fixture(key_seed);
    const SyncValidationResult encoded = encode_peer_transport_ingress_wire_frame(
        limits,
        out.fixture.envelope,
        out.fixture.chunks,
        out.frame,
        out.payload_digest);
    if (!encoded.ok) fail("fixture encoding failed: " + encoded.reason);
    return out;
}

void update_frame_blob(sqlite3* db,
                       const std::string& session_id,
                       const std::string& key,
                       const std::string& frame,
                       const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "UPDATE main.sync_peer_transport_ingress_payloads SET canonical_frame=? "
        "WHERE session_id=? AND transport_envelope_idempotency_key=?;",
        label + " prepare");
    sqlite_bind_blob_or_throw(stmt.stmt, 1, frame, label + " frame");
    sqlite_bind_text_or_throw(stmt.stmt, 2, session_id, label + " session");
    sqlite_bind_text_or_throw(stmt.stmt, 3, key, label + " key");
    sqlite_step_done_or_throw(stmt.stmt, label + " update");
    if (sqlite3_changes(db) != 1) fail(label + " did not update exactly one row");
}

void configure_durable_database(sqlite3* db, const std::string& label) {
    sqlite_exec_or_throw(db, "PRAGMA foreign_keys=ON;", label + " foreign keys");
    sqlite_exec_or_throw(db, "PRAGMA journal_mode=WAL;", label + " WAL mode");
    sqlite_exec_or_throw(db, "PRAGMA synchronous=FULL;", label + " FULL synchronous");
}

PeerTransportIngressStoredPayload load_payload_in_snapshot(
    sqlite3* db,
    const std::string& session_id,
    const std::string& key,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    SyncSqliteTransaction transaction(
        db, label + " transaction", SyncSqliteTransactionMode::Deferred);
    PeerTransportIngressStoredPayload out =
        load_peer_transport_ingress_stored_payload_or_throw(
            db, transaction, session_id, key, max_frame_bytes, label);
    transaction.commit();
    return out;
}

#if defined(__unix__) || defined(__APPLE__)
[[noreturn]] void run_payload_crash_child(
    const std::filesystem::path& path,
    const std::string& session_id,
    const EncodedFixture& fixture,
    const PeerTransportIngressWireLimits& limits,
    std::uint64_t stored_at_epoch,
    bool commit_before_crash) {
    try {
        SqlitePtr child_db = open_database(path);
        configure_durable_database(child_db.get(), "crash child");
        SyncSqliteTransaction transaction(
            child_db.get(), "crash child parent and payload");
        insert_parent(
            child_db.get(),
            session_id,
            fixture.fixture.envelope.transport_envelope_idempotency_key,
            "crash child parent");
        const PeerTransportIngressPayloadStoreOutcome outcome =
            store_or_verify_peer_transport_ingress_payload_or_throw(
                child_db.get(),
                transaction,
                session_id,
                fixture.fixture.envelope.transport_envelope_idempotency_key,
                fixture.frame,
                fixture.payload_digest,
                limits,
                stored_at_epoch,
                "crash child payload");
        if (outcome != PeerTransportIngressPayloadStoreOutcome::Inserted) _exit(90);
        if (commit_before_crash) transaction.commit();
        // Deliberately skip every C++ and SQLite destructor. This models a
        // process disappearing immediately after COMMIT or with a live write.
        _exit(0);
    } catch (...) {
        _exit(91);
    }
}

void spawn_payload_crash_child_or_throw(
    const std::filesystem::path& path,
    const std::string& session_id,
    const EncodedFixture& fixture,
    const PeerTransportIngressWireLimits& limits,
    std::uint64_t stored_at_epoch,
    bool commit_before_crash) {
    const pid_t pid = ::fork();
    if (pid < 0) fail("payload crash test fork failed");
    if (pid == 0) {
        run_payload_crash_child(
            path,
            session_id,
            fixture,
            limits,
            stored_at_epoch,
            commit_before_crash);
    }
    int status = 0;
    if (::waitpid(pid, &status, 0) != pid) fail("payload crash test waitpid failed");
    if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
        fail("payload crash child failed with status " + std::to_string(status));
    }
}
#endif

}  // namespace

int main() {
    std::uint64_t checks = 0;
    const std::filesystem::path db_path = unique_database_path();
    try {
        require(!sync_sqlite_version_has_wal_reset_fix(3044005),
                "3.44.5 was incorrectly classified fixed", checks);
        require(sync_sqlite_version_has_wal_reset_fix(3044006),
                "3.44.6 backport was not classified fixed", checks);
        require(!sync_sqlite_version_has_wal_reset_fix(3045000),
                "3.45.0 was incorrectly classified fixed", checks);
        require(!sync_sqlite_version_has_wal_reset_fix(3050006),
                "3.50.6 was incorrectly classified fixed", checks);
        require(sync_sqlite_version_has_wal_reset_fix(3050007),
                "3.50.7 backport was not classified fixed", checks);
        require(!sync_sqlite_version_has_wal_reset_fix(3051002),
                "3.51.2 was incorrectly classified fixed", checks);
        require(sync_sqlite_version_has_wal_reset_fix(3051003),
                "3.51.3 was not classified fixed", checks);
        require(sync_sqlite_version_has_wal_reset_fix(3053003),
                "3.53.3 was not classified fixed", checks);

        const SyncSqliteRuntimeProfile runtime = sync_sqlite_runtime_profile();
        require(runtime.version_number == 3053003 && runtime.version == "3.53.3",
                "runtime is not the reviewed SQLite 3.53.3", checks);
        require(runtime.header_runtime_version_match,
                "SQLite header/runtime versions differ", checks);
        require(runtime.wal_reset_fix_present,
                "runtime does not report the WAL-reset fix", checks);
        require(runtime.threadsafe != 0,
                "runtime was compiled without mutex support", checks);
#if defined(ANONSYNC_BUNDLED_SQLITE)
        require(runtime.bundled, "bundled build did not report bundled SQLite", checks);
#endif
        require_sync_sqlite_wal_runtime_safe_or_throw(
            "rev0773 payload-store test runtime gate");
        ++checks;

        {
            SqlitePtr missing_foreign_key = open_database(":memory:");
            sqlite_exec_or_throw(missing_foreign_key.get(), "PRAGMA foreign_keys=ON;",
                                 "impostor foreign keys");
            create_test_parent_schema(missing_foreign_key.get(),
                                      "impostor parent schema");
            sqlite_exec_or_throw(
                missing_foreign_key.get(),
                "CREATE TABLE sync_peer_transport_ingress_payloads("
                "session_id TEXT NOT NULL,"
                "transport_envelope_idempotency_key TEXT NOT NULL,"
                "codec_version INTEGER NOT NULL CHECK(codec_version > 0),"
                "canonical_frame_sha256 TEXT NOT NULL CHECK(length(canonical_frame_sha256) = 64),"
                "payload_digest TEXT NOT NULL CHECK(length(payload_digest) = 64),"
                "canonical_frame_bytes INTEGER NOT NULL CHECK(canonical_frame_bytes > 0),"
                "canonical_frame BLOB NOT NULL CHECK(typeof(canonical_frame) = 'blob'),"
                "stored_at_epoch INTEGER NOT NULL CHECK(stored_at_epoch > 0),"
                "PRIMARY KEY(session_id, transport_envelope_idempotency_key),"
                "CHECK(canonical_frame_bytes = length(canonical_frame)));",
                "impostor payload schema without foreign key");
            require_throws(
                [&] {
                    ensure_peer_transport_ingress_payload_store_schema_or_throw(
                        missing_foreign_key.get(), "impostor payload verification");
                },
                "foreign key",
                "look-alike payload table without cascade foreign key was accepted",
                checks);
        }

        {
            SqlitePtr missing_checks = open_database(":memory:");
            sqlite_exec_or_throw(missing_checks.get(), "PRAGMA foreign_keys=ON;",
                                 "weak schema foreign keys");
            create_test_parent_schema(missing_checks.get(),
                                      "weak schema parent");
            sqlite_exec_or_throw(
                missing_checks.get(),
                "CREATE TABLE sync_peer_transport_ingress_payloads("
                "session_id TEXT NOT NULL,"
                "transport_envelope_idempotency_key TEXT NOT NULL,"
                "codec_version INTEGER NOT NULL,"
                "canonical_frame_sha256 TEXT NOT NULL,"
                "payload_digest TEXT NOT NULL,"
                "canonical_frame_bytes INTEGER NOT NULL,"
                "canonical_frame BLOB NOT NULL,"
                "stored_at_epoch INTEGER NOT NULL,"
                "PRIMARY KEY(session_id, transport_envelope_idempotency_key),"
                "FOREIGN KEY(session_id, transport_envelope_idempotency_key) REFERENCES "
                "sync_peer_transport_ingress_envelopes(session_id, transport_envelope_idempotency_key) "
                "ON UPDATE RESTRICT ON DELETE CASCADE);",
                "weak payload schema without checks");
            require_throws(
                [&] {
                    ensure_peer_transport_ingress_payload_store_schema_or_throw(
                        missing_checks.get(), "weak payload verification");
                },
                "CHECK constraint",
                "look-alike payload table without value constraints was accepted",
                checks);
        }

        {
            SqlitePtr shadowed_schema = open_database(":memory:");
            sqlite_exec_or_throw(
                shadowed_schema.get(), "PRAGMA foreign_keys=ON;",
                "shadowed schema foreign keys");
            create_test_parent_schema(
                shadowed_schema.get(), "shadowed schema parent");
            sqlite_exec_or_throw(
                shadowed_schema.get(),
                "CREATE TEMP TABLE sync_peer_transport_ingress_payloads(poison TEXT);",
                "shadowed schema temp table");
            ensure_peer_transport_ingress_payload_store_schema_or_throw(
                shadowed_schema.get(), "shadowed main payload schema");
            require(
                scalar_count(
                    shadowed_schema.get(),
                    "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='table' "
                    "AND name='sync_peer_transport_ingress_payloads';",
                    "shadowed main table count") == 1 &&
                    scalar_count(
                        shadowed_schema.get(),
                        "SELECT COUNT(*) FROM main.sqlite_schema WHERE type='index' "
                        "AND name='idx_sync_peer_transport_ingress_payload_digest';",
                        "shadowed main index count") == 1 &&
                    scalar_count(
                        shadowed_schema.get(),
                        "SELECT COUNT(*) FROM temp.sqlite_schema WHERE type='table' "
                        "AND name='sync_peer_transport_ingress_payloads';",
                        "shadowed temp table count") == 1,
                "TEMP look-alike redirected exact main-schema creation",
                checks);
        }

        SqlitePtr db = open_database(db_path);
        configure_durable_database(db.get(), "test database");
        create_test_parent_schema(db.get(), "test parent schema");
        ensure_peer_transport_ingress_payload_store_schema_or_throw(
            db.get(), "test payload schema");

        PeerTransportIngressWireLimits limits;
        limits.max_frame_bytes = 64 * 1024;
        limits.max_chunk_count = 16;
        const std::string session_id = "session-a";
        EncodedFixture first = encode_fixture("payload-store-first", limits);

        // The old API only documented this atomicity requirement. The new API
        // cannot store evidence without an exact live write-transaction guard.
        SyncSqliteTransaction revoked(db.get(), "revoked payload transaction");
        revoked.commit();
        require_throws(
            [&] {
                (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                    db.get(),
                    revoked,
                    session_id,
                    first.fixture.envelope.transport_envelope_idempotency_key,
                    first.frame,
                    first.payload_digest,
                    limits,
                    999,
                    "revoked transaction payload");
            },
            "exact active SQLite write transaction",
            "payload store accepted an ended transaction generation",
            checks);

        {
            SyncSqliteTransaction transaction(db.get(), "first parent and payload");
            insert_parent(
                db.get(),
                session_id,
                first.fixture.envelope.transport_envelope_idempotency_key,
                "first parent");
            const PeerTransportIngressPayloadStoreOutcome inserted =
                store_or_verify_peer_transport_ingress_payload_or_throw(
                    db.get(),
                    transaction,
                    session_id,
                    first.fixture.envelope.transport_envelope_idempotency_key,
                    first.frame,
                    first.payload_digest,
                    limits,
                    1000,
                    "first payload");
            require(inserted == PeerTransportIngressPayloadStoreOutcome::Inserted,
                    "first payload was not inserted", checks);
            transaction.commit();
        }

        PeerTransportIngressStoredPayload loaded = load_payload_in_snapshot(
            db.get(),
            session_id,
            first.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "first payload load");
        require(loaded.found, "inserted payload was not found", checks);
        require(loaded.codec_version == kPeerTransportIngressWireCodecVersion,
                "stored payload codec version differs", checks);
        require(loaded.canonical_frame == first.frame &&
                    loaded.canonical_frame_bytes == first.frame.size(),
                "stored canonical frame differs from exact bytes", checks);
        require(loaded.canonical_frame_sha256 == sha256_hex(first.frame),
                "stored frame digest differs from exact bytes", checks);
        require(loaded.payload_digest == first.payload_digest,
                "stored payload digest differs", checks);
        require(loaded.stored_at_epoch == 1000,
                "stored payload timestamp differs", checks);

        {
            SyncSqliteTransaction transaction(db.get(), "duplicate payload transaction");
            const PeerTransportIngressPayloadStoreOutcome duplicate =
                store_or_verify_peer_transport_ingress_payload_or_throw(
                    db.get(),
                    transaction,
                    session_id,
                    first.fixture.envelope.transport_envelope_idempotency_key,
                    first.frame,
                    first.payload_digest,
                    limits,
                    2000,
                    "duplicate payload");
            require(duplicate == PeerTransportIngressPayloadStoreOutcome::AlreadyPresent,
                    "exact duplicate was not idempotent", checks);
            transaction.commit();
        }
        loaded = load_payload_in_snapshot(
            db.get(),
            session_id,
            first.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "duplicate payload load");
        require(loaded.stored_at_epoch == 1000,
                "idempotent duplicate rewrote original receipt time", checks);

        require_throws(
            [&] {
                (void)load_payload_in_snapshot(
                    db.get(),
                    session_id,
                    first.fixture.envelope.transport_envelope_idempotency_key,
                    static_cast<std::uint64_t>(first.frame.size() - 1),
                    "bounded payload load");
            },
            "exceeds configured max_frame_bytes",
            "oversized durable frame was not rejected before BLOB publication",
            checks);

        // A verified schema capability is a snapshot lease, not a permanent
        // assertion attached to one connection pointer.
        {
            SyncSqliteTransaction snapshot(
                db.get(),
                "stale capability snapshot",
                SyncSqliteTransactionMode::Deferred);
            const VerifiedPeerTransportIngressPayloadStoreSchema verified =
                verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw(
                    db.get(), snapshot, "stale capability schema");
            snapshot.commit();
            require_throws(
                [&] {
                    (void)load_peer_transport_ingress_stored_payload_from_verified_schema_or_throw(
                        db.get(),
                        verified,
                        session_id,
                        first.fixture.envelope.transport_envelope_idempotency_key,
                        limits.max_frame_bytes,
                        "stale capability load");
                },
                "no longer authorizes this exact SQLite snapshot",
                "schema capability survived its verifying snapshot",
                checks);
        }

        // TEMP objects must not redirect schema introspection or payload reads.
        sqlite_exec_or_throw(
            db.get(),
            "CREATE TEMP TABLE sync_peer_transport_ingress_payloads(poison TEXT);",
            "temporary payload shadow");
        loaded = load_payload_in_snapshot(
            db.get(),
            session_id,
            first.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "main-qualified payload load under temp shadow");
        require(loaded.found && loaded.canonical_frame == first.frame,
                "TEMP payload shadow redirected main durable evidence", checks);
        sqlite_exec_or_throw(
            db.get(),
            "DROP TABLE temp.sync_peer_transport_ingress_payloads;",
            "drop temporary payload shadow");

        // A deferred read snapshot is insufficient authority for a durable store.
        {
            SyncSqliteTransaction read_transaction(
                db.get(),
                "read-only payload transaction",
                SyncSqliteTransactionMode::Deferred);
            (void)scalar_count(
                db.get(),
                "SELECT COUNT(*) FROM main.sync_peer_transport_ingress_payloads;",
                "read-only payload snapshot");
            require(read_transaction.authorizes_snapshot(db.get()) &&
                        !read_transaction.authorizes_write(db.get()),
                    "deferred transaction did not remain a read snapshot", checks);
            require_throws(
                [&] {
                    (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                        db.get(),
                        read_transaction,
                        session_id,
                        first.fixture.envelope.transport_envelope_idempotency_key,
                        first.frame,
                        first.payload_digest,
                        limits,
                        1001,
                        "read-only transaction payload");
                },
                "exact active SQLite write transaction",
                "payload store accepted read-snapshot authority",
                checks);
            read_transaction.rollback();
        }

        EncodedFixture second = encode_fixture("payload-store-second", limits);
        {
            SyncSqliteTransaction transaction(db.get(), "mismatched identity transaction");
            require_throws(
                [&] {
                    (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                        db.get(),
                        transaction,
                        session_id,
                        second.fixture.envelope.transport_envelope_idempotency_key,
                        first.frame,
                        first.payload_digest,
                        limits,
                        1001,
                        "mismatched identity payload");
                },
                "identity differs",
                "payload store accepted a frame under a different durable identity",
                checks);
            transaction.rollback();
        }
        {
            SyncSqliteTransaction transaction(db.get(), "mismatched digest transaction");
            require_throws(
                [&] {
                    (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                        db.get(),
                        transaction,
                        session_id,
                        first.fixture.envelope.transport_envelope_idempotency_key,
                        first.frame,
                        sha256_hex("wrong-payload-digest"),
                        limits,
                        1001,
                        "mismatched digest payload");
                },
                "digest differs",
                "payload store accepted a digest not embedded in the frame",
                checks);
            transaction.rollback();
        }

        // Parent identity and payload evidence roll back as one unit.
        {
            SyncSqliteTransaction transaction(db.get(), "rollback parent and payload");
            insert_parent(
                db.get(),
                session_id,
                second.fixture.envelope.transport_envelope_idempotency_key,
                "rollback parent");
            (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                db.get(),
                transaction,
                session_id,
                second.fixture.envelope.transport_envelope_idempotency_key,
                second.frame,
                second.payload_digest,
                limits,
                1002,
                "rollback payload");
            transaction.rollback();
        }
        PeerTransportIngressStoredPayload rolled_back = load_payload_in_snapshot(
            db.get(),
            session_id,
            second.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "rollback payload load");
        require(!rolled_back.found &&
                    scalar_count(
                        db.get(),
                        "SELECT COUNT(*) FROM main.sync_peer_transport_ingress_envelopes "
                        "WHERE transport_envelope_idempotency_key='" +
                            second.fixture.envelope.transport_envelope_idempotency_key + "';",
                        "rollback parent count") == 0,
                "rolled-back parent/payload pair became partly durable", checks);

        {
            SyncSqliteTransaction transaction(db.get(), "commit parent and payload");
            insert_parent(
                db.get(),
                session_id,
                second.fixture.envelope.transport_envelope_idempotency_key,
                "committed parent");
            (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                db.get(),
                transaction,
                session_id,
                second.fixture.envelope.transport_envelope_idempotency_key,
                second.frame,
                second.payload_digest,
                limits,
                1003,
                "committed payload");
            transaction.commit();
        }
        PeerTransportIngressStoredPayload committed = load_payload_in_snapshot(
            db.get(),
            session_id,
            second.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "committed payload load");
        require(committed.found && committed.canonical_frame == second.frame,
                "committed parent/payload pair was not reconstructed", checks);

        EncodedFixture contradictory = first;
        contradictory.fixture.chunks[0][0] = 'A';
        anonsync::test::refresh_fixture_chunk_evidence(contradictory.fixture);
        contradictory.frame.clear();
        contradictory.payload_digest.clear();
        const SyncValidationResult contradictory_encoded =
            encode_peer_transport_ingress_wire_frame(
                limits,
                contradictory.fixture.envelope,
                contradictory.fixture.chunks,
                contradictory.frame,
                contradictory.payload_digest);
        require(contradictory_encoded.ok,
                "contradictory valid fixture did not encode", checks);
        {
            SyncSqliteTransaction transaction(db.get(), "contradictory duplicate transaction");
            require_throws(
                [&] {
                    (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                        db.get(),
                        transaction,
                        session_id,
                        first.fixture.envelope.transport_envelope_idempotency_key,
                        contradictory.frame,
                        contradictory.payload_digest,
                        limits,
                        1004,
                        "contradictory duplicate");
                },
                "contradicts",
                "same identity accepted different canonical evidence",
                checks);
            transaction.rollback();
        }

        std::string tampered = first.frame;
        tampered.back() ^= static_cast<char>(0x01);
        {
            SyncSqliteTransaction transaction(db.get(), "tamper payload transaction");
            update_frame_blob(
                db.get(),
                session_id,
                first.fixture.envelope.transport_envelope_idempotency_key,
                tampered,
                "tamper frame");
            transaction.commit();
        }
        require_throws(
            [&] {
                (void)load_payload_in_snapshot(
                    db.get(),
                    session_id,
                    first.fixture.envelope.transport_envelope_idempotency_key,
                    limits.max_frame_bytes,
                    "tampered payload load");
            },
            "digest differs from blob bytes",
            "same-length persistent BLOB corruption was not detected",
            checks);
        {
            SyncSqliteTransaction transaction(db.get(), "restore payload transaction");
            update_frame_blob(
                db.get(),
                session_id,
                first.fixture.envelope.transport_envelope_idempotency_key,
                first.frame,
                "restore frame");
            transaction.commit();
        }
        loaded = load_payload_in_snapshot(
            db.get(),
            session_id,
            first.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "restored payload load");
        require(loaded.found && loaded.canonical_frame == first.frame,
                "restored exact frame did not recover", checks);

        {
            SyncSqliteTransaction transaction(db.get(), "cascade parent delete transaction");
            SyncSqliteStmt delete_parent = sqlite_prepare_or_throw(
                db.get(),
                "DELETE FROM main.sync_peer_transport_ingress_envelopes WHERE "
                "session_id=? AND transport_envelope_idempotency_key=?;",
                "cascade parent delete prepare");
            sqlite_bind_text_or_throw(delete_parent.stmt, 1, session_id,
                                      "cascade parent delete session");
            sqlite_bind_text_or_throw(
                delete_parent.stmt, 2,
                second.fixture.envelope.transport_envelope_idempotency_key,
                "cascade parent delete key");
            sqlite_step_done_or_throw(delete_parent.stmt, "cascade parent delete");
            require(sqlite3_changes(db.get()) == 1,
                    "cascade proof did not delete one parent", checks);
            require(scalar_count(
                        db.get(),
                        "SELECT COUNT(*) FROM main.sync_peer_transport_ingress_payloads "
                        "WHERE transport_envelope_idempotency_key='" +
                            second.fixture.envelope.transport_envelope_idempotency_key +
                            "';",
                        "cascade payload count") == 0,
                    "terminal parent deletion did not cascade durable payload bytes",
                    checks);
            transaction.commit();
        }

        EncodedFixture orphan = encode_fixture("payload-store-orphan", limits);
        {
            SyncSqliteTransaction transaction(db.get(), "orphan payload transaction");
            require_throws(
                [&] {
                    (void)store_or_verify_peer_transport_ingress_payload_or_throw(
                        db.get(),
                        transaction,
                        session_id,
                        orphan.fixture.envelope.transport_envelope_idempotency_key,
                        orphan.frame,
                        orphan.payload_digest,
                        limits,
                        1005,
                        "orphan payload");
                },
                "FOREIGN KEY",
                "payload store accepted an orphan without a queue identity",
                checks);
            transaction.rollback();
        }

#if defined(__unix__) || defined(__APPLE__)
        EncodedFixture crash_committed = encode_fixture("payload-crash-committed", limits);
        EncodedFixture crash_uncommitted = encode_fixture("payload-crash-uncommitted", limits);
        db.reset();

        spawn_payload_crash_child_or_throw(
            db_path,
            session_id,
            crash_committed,
            limits,
            1100,
            true);
        db = open_database(db_path);
        configure_durable_database(db.get(), "post-commit-crash database");
        const PeerTransportIngressStoredPayload crash_recovered = load_payload_in_snapshot(
            db.get(),
            session_id,
            crash_committed.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "post-commit-crash payload load");
        require(crash_recovered.found &&
                    crash_recovered.canonical_frame == crash_committed.frame &&
                    scalar_count(
                        db.get(),
                        "SELECT COUNT(*) FROM main.sync_peer_transport_ingress_envelopes "
                        "WHERE transport_envelope_idempotency_key='" +
                            crash_committed.fixture.envelope.transport_envelope_idempotency_key +
                            "';",
                        "post-commit-crash parent count") == 1,
                "FULL/WAL commit did not preserve the exact parent/payload pair across process death",
                checks);
        db.reset();

        spawn_payload_crash_child_or_throw(
            db_path,
            session_id,
            crash_uncommitted,
            limits,
            1101,
            false);
        db = open_database(db_path);
        configure_durable_database(db.get(), "post-uncommitted-crash database");
        const PeerTransportIngressStoredPayload crash_rolled_back = load_payload_in_snapshot(
            db.get(),
            session_id,
            crash_uncommitted.fixture.envelope.transport_envelope_idempotency_key,
            limits.max_frame_bytes,
            "post-uncommitted-crash payload load");
        require(!crash_rolled_back.found &&
                    scalar_count(
                        db.get(),
                        "SELECT COUNT(*) FROM main.sync_peer_transport_ingress_envelopes "
                        "WHERE transport_envelope_idempotency_key='" +
                            crash_uncommitted.fixture.envelope.transport_envelope_idempotency_key +
                            "';",
                        "post-uncommitted-crash parent count") == 0,
                "process death published only part of an uncommitted parent/payload pair",
                checks);
#endif

        SyncSqliteStmt integrity = sqlite_prepare_or_throw(
            db.get(), "PRAGMA integrity_check;", "integrity check prepare");
        const int integrity_rc = sqlite3_step(integrity.stmt);
        require(integrity_rc == SQLITE_ROW &&
                    sqlite_column_text_or_throw(
                        integrity.stmt, 0, "integrity result") == "ok",
                "SQLite integrity_check did not return ok", checks);

        // The test-owned raw connection uses a compatibility deleter, but its
        // dependents must still be finalized before owner destruction. Keeping
        // this explicit prevents a close_v2 zombie from hiding a lifetime bug.
        integrity.reset();
        db.reset();
        std::error_code cleanup_ec;
        std::filesystem::remove(db_path, cleanup_ec);
        std::filesystem::remove(db_path.string() + "-wal", cleanup_ec);
        std::filesystem::remove(db_path.string() + "-shm", cleanup_ec);

        std::cout << "anonsync sqlite runtime and payload-store checks=" << checks
                  << " runtime=" << runtime.version
                  << " source_id=" << runtime.source_id << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::error_code cleanup_ec;
        std::filesystem::remove(db_path, cleanup_ec);
        std::filesystem::remove(db_path.string() + "-wal", cleanup_ec);
        std::filesystem::remove(db_path.string() + "-shm", cleanup_ec);
        std::cerr << "anonsync sqlite runtime and payload-store test failed after "
                  << checks << " checks: " << e.what() << "\n";
        return 1;
    }
}
