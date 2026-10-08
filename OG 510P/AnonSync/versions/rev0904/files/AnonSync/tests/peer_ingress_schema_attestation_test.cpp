#include "sync_peer_ingress_payload_store.hpp"
#include "sync_peer_ingress_schema.hpp"
#include "sync_peer_ingress_schema_sql.hpp"
#include "sync_sqlite_support.hpp"
#include "sync_sqlite_schema_identity.hpp"

#if defined(__linux__)
#include "self_exec_test_process.hpp"
#endif

#include <chrono>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

#include <sqlite3.h>

#if defined(__unix__) || defined(__APPLE__)
#include <unistd.h>
#endif

namespace {

using namespace anonsync;
namespace fs = std::filesystem;

static_assert(!std::is_copy_constructible_v<
                  PeerTransportIngressSchemaAttestation> &&
                  !std::is_copy_assignable_v<
                      PeerTransportIngressSchemaAttestation>,
              "schema attestations must remain unique owner-generation pins");
static_assert(std::is_nothrow_move_constructible_v<
                  PeerTransportIngressSchemaAttestation> &&
                  std::is_nothrow_move_assignable_v<
                      PeerTransportIngressSchemaAttestation>,
              "schema attestation transfer must preserve its exact owner pin");

[[noreturn]] void fail(const std::string& message) {
    throw std::runtime_error(message);
}

void require(bool condition, const std::string& message, std::uint64_t& checks) {
    ++checks;
    if (!condition) fail(message);
}

template <typename Function>
void require_throws(Function&& function,
                    std::string_view expected_fragment,
                    const std::string& message,
                    std::uint64_t& checks) {
    ++checks;
    try {
        function();
    } catch (const std::exception& e) {
        const std::string reason = e.what();
        if (expected_fragment.empty() ||
            reason.find(expected_fragment) != std::string::npos) {
            return;
        }
        fail(message + ": unexpected error: " + reason);
    }
    fail(message + ": no exception was thrown");
}

struct SqlitePtr final {
    SyncSqliteDb owner;

    [[nodiscard]] sqlite3* get() const noexcept { return owner.db.get(); }
};

SqlitePtr open_database(const fs::path& path, bool readonly = false) {
    SqlitePtr out;
    int flags = (readonly ? SQLITE_OPEN_READONLY
                          : SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE) |
                SQLITE_OPEN_FULLMUTEX;
#ifdef SQLITE_OPEN_NOFOLLOW
    flags |= SQLITE_OPEN_NOFOLLOW;
#endif
    const int rc = sqlite3_open_v2(path.string().c_str(), out.owner.db.out(),
                                   flags, nullptr);
    if (rc != SQLITE_OK) {
        const std::string reason = out.get() != nullptr
                                       ? sqlite3_errmsg(out.get())
                                       : "unknown SQLite open error";
        fail("test database open failed: " + reason);
    }
    sqlite3_extended_result_codes(out.get(), 1);
    return out;
}

std::uint64_t scalar_u64(sqlite3* db,
                         const std::string& sql,
                         const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db, sql, label + " prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " query");
    return sqlite_column_u64_or_throw(stmt.stmt, 0, label + " value");
}

std::uint64_t reserved_object_count(sqlite3* db) {
    return scalar_u64(
        db,
        "SELECT COUNT(*) FROM main.sqlite_schema WHERE sql IS NOT NULL AND ("
        "name GLOB 'sync_peer_transport_*' OR "
        "name GLOB 'idx_sync_peer_transport_*' OR "
        "tbl_name GLOB 'sync_peer_transport_*');",
        "reserved schema count");
}

void install_exact_schema(sqlite3* db,
                          const std::function<std::string(
                              const PeerTransportIngressSchemaSqlObject&)>& transform = {}) {
    sqlite_exec_or_throw(db, "BEGIN IMMEDIATE;", "manual schema begin");
    try {
        for (const PeerTransportIngressSchemaSqlObject& object :
             kPeerTransportIngressSchemaSqlObjects) {
            const std::string ddl = transform ? transform(object)
                                              : std::string(object.ddl);
            sqlite_exec_or_throw(db,
                                 ddl + ";",
                                 "manual schema object " + std::string(object.name));
        }
        sqlite_exec_or_throw(db, "COMMIT;", "manual schema commit");
    } catch (...) {
        sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, nullptr);
        throw;
    }
}

void set_markers(sqlite3* db,
                 std::uint64_t application_id =
                     kPeerTransportIngressSqliteApplicationId,
                 std::uint64_t user_version =
                     kPeerTransportIngressSqliteUserVersion) {
    sqlite_exec_or_throw(
        db,
        "PRAGMA application_id=" + std::to_string(application_id) + ";",
        "set test application_id");
    sqlite_exec_or_throw(
        db,
        "PRAGMA user_version=" + std::to_string(user_version) + ";",
        "set test user_version");
}

struct DatabaseFixture final {
    fs::path path;

    explicit DatabaseFixture(std::string_view tag) {
        const auto ticks =
            std::chrono::high_resolution_clock::now().time_since_epoch().count();
#if defined(__unix__) || defined(__APPLE__)
        const long long pid = static_cast<long long>(::getpid());
#else
        const long long pid = 0;
#endif
        path = fs::temp_directory_path() /
               ("anonsync-rev0767-schema-" + std::string(tag) + "-" +
                std::to_string(pid) + "-" + std::to_string(ticks) + ".sqlite");
    }

    ~DatabaseFixture() {
        std::error_code ec;
        fs::remove(path, ec);
        fs::remove(fs::path(path.string() + "-wal"), ec);
        fs::remove(fs::path(path.string() + "-shm"), ec);
        fs::remove(fs::path(path.string() + "-journal"), ec);
    }
};

struct BootstrapDenyContext final {
    int schema_creates = 0;
    int deny_on = 0;
};

int deny_payload_index_authorizer(void*,
                                  int action,
                                  const char*,
                                  const char*,
                                  const char*,
                                  const char*) noexcept {
    return action == SQLITE_CREATE_INDEX ? SQLITE_DENY : SQLITE_OK;
}

int allow_all_authorizer(void*,
                         int,
                         const char*,
                         const char*,
                         const char*,
                         const char*) noexcept {
    return SQLITE_OK;
}

int bootstrap_deny_authorizer(void* raw,
                              int action,
                              const char*,
                              const char*,
                              const char*,
                              const char*) noexcept {
    auto* context = static_cast<BootstrapDenyContext*>(raw);
    if (action == SQLITE_CREATE_TABLE || action == SQLITE_CREATE_INDEX) {
        ++context->schema_creates;
        if (context->schema_creates == context->deny_on) return SQLITE_DENY;
    }
    return SQLITE_OK;
}

void test_schema_token_identity(std::uint64_t& checks) {
    require(canonicalize_sqlite_schema_sql_or_throw(
                "CREATE TABLE T (X INTEGER CHECK(X IN (1, 2)));" ) ==
                canonicalize_sqlite_schema_sql_or_throw(
                "create table t(x integer check(x in(1,2)))"),
            "schema token identity did not normalize formatting and unquoted case",
            checks);
    require(canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(state IN ('queued'))") !=
                canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(statein('queued'))"),
            "schema token identity merged a keyword boundary with an identifier",
            checks);
    require(canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(kind='blob value')") !=
                canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(kind='blobvalue')"),
            "schema token identity erased quoted semantic whitespace",
            checks);
    require(canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(kind='blob')") !=
                canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(kind='BLOB')"),
            "schema token identity erased quoted semantic case",
            checks);
    require(canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(x>0)") !=
                canonicalize_sqlite_schema_sql_or_throw(
                "CHECK(x>0) /* hostile drift */"),
            "schema token identity erased schema comments",
            checks);
}

void test_atomic_payload_schema_ensure(std::uint64_t& checks) {
    SqlitePtr db = open_database(":memory:");
    sqlite_exec_or_throw(
        db.get(),
        "CREATE TABLE sync_peer_transport_ingress_envelopes("
        "session_id TEXT NOT NULL,"
        "transport_envelope_idempotency_key TEXT NOT NULL,"
        "PRIMARY KEY(session_id,transport_envelope_idempotency_key));",
        "payload ensure parent seed");
    if (sqlite3_set_authorizer(db.get(), deny_payload_index_authorizer, nullptr) !=
        SQLITE_OK) {
        fail("could not install payload ensure fault authorizer");
    }
    require_throws(
        [&] {
            ensure_peer_transport_ingress_payload_store_schema_or_throw(
                db.get(), "payload ensure injected index failure");
        },
        "not authorized",
        "payload schema ensure did not expose injected index failure",
        checks);
    sqlite3_set_authorizer(db.get(), nullptr, nullptr);
    require(scalar_u64(
                db.get(),
                "SELECT COUNT(*) FROM main.sqlite_schema WHERE name IN ("
                "'sync_peer_transport_ingress_payloads',"
                "'idx_sync_peer_transport_ingress_payload_digest');",
                "payload ensure rollback count") == 0,
            "payload schema ensure left a table after index creation failed",
            checks);
}

void test_fresh_bootstrap(std::uint64_t& checks) {
    DatabaseFixture fixture("fresh");
    SqlitePtr db = open_database(fixture.path);
    const PeerTransportIngressSchemaAttestation attestation =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            db.owner.db, true, false, "fresh bootstrap");

    require(attestation.authorizes(db.get()),
            "fresh attestation is not bound to its handle", checks);
    require(attestation.schema_present() && !attestation.legacy_unmarked(),
            "fresh bootstrap did not attest a marked schema", checks);
    require(attestation.manifest_sha256().size() == 64 &&
                attestation.manifest_sha256() ==
                    expected_peer_transport_ingress_schema_manifest_sha256(),
            "fresh manifest commitment differs from reviewed schema", checks);
    require(reserved_object_count(db.get()) ==
                kPeerTransportIngressSchemaSqlObjects.size(),
            "fresh bootstrap did not create the exact object count", checks);
    require(scalar_u64(db.get(), "PRAGMA application_id;", "fresh application_id") ==
                kPeerTransportIngressSqliteApplicationId &&
                scalar_u64(db.get(), "PRAGMA user_version;", "fresh user_version") ==
                    kPeerTransportIngressSqliteUserVersion,
            "fresh bootstrap markers were not committed", checks);

    SyncSqliteTransaction fresh_verify(
        db.get(), "fresh verify", SyncSqliteTransactionMode::Immediate);
    {
        SyncSqliteConnectionAuthorityLease authority_lease =
            verify_peer_transport_ingress_schema_attestation_current_or_throw(
                db.owner.db, attestation, "fresh snapshot verification");
        fresh_verify.rollback();
    }
    ++checks;

    sqlite_exec_or_throw(
        db.get(),
        "INSERT INTO sync_peer_transport_authority_records("
        "session_id,peer_id,peer_session_id,transport_instance_id,transport_key_id,"
        "authority_status,valid_from_epoch,valid_until_epoch,updated_at_epoch,reason) "
        "VALUES('s','p','ps','ti','tk','trusted',1,0,1,'reviewed');",
        "authorized DML");
    require(scalar_u64(db.get(),
                       "SELECT COUNT(*) FROM sync_peer_transport_authority_records;",
                       "authorized DML count") == 1,
            "schema authorizer blocked ordinary reviewed DML", checks);

    require_throws(
        [&] {
            sqlite_exec_or_throw(db.get(), "CREATE TABLE forbidden(x);",
                                 "forbidden persistent DDL");
        },
        "not authorized",
        "persistent DDL escaped the connection schema fence",
        checks);
    require_throws(
        [&] {
            sqlite_exec_or_throw(db.get(), "CREATE TEMP TABLE forbidden_temp(x);",
                                 "forbidden temporary DDL");
        },
        "not authorized",
        "temporary shadow DDL escaped the connection schema fence",
        checks);
    require_throws(
        [&] {
            sqlite_exec_or_throw(db.get(), "PRAGMA application_id=7;",
                                 "forbidden marker rewrite");
        },
        "not authorized",
        "application_id rewrite escaped the connection schema fence",
        checks);
}

void test_atomic_bootstrap_rollback(std::uint64_t& checks) {
    DatabaseFixture fixture("rollback");
    SqlitePtr db = open_database(fixture.path);
    BootstrapDenyContext deny;
    deny.deny_on = 4;
    if (sqlite3_set_authorizer(db.get(), bootstrap_deny_authorizer, &deny) !=
        SQLITE_OK) {
        fail("could not install bootstrap rollback fixture authorizer");
    }
    require_throws(
        [&] {
            (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                db.owner.db, true, false, "injected bootstrap failure");
        },
        "not authorized",
        "injected mid-bootstrap denial did not abort initialization",
        checks);
    sqlite3_set_authorizer(db.get(), nullptr, nullptr);
    require(deny.schema_creates == deny.deny_on,
            "bootstrap fault was not injected at the intended DDL boundary", checks);
    require(sqlite3_get_autocommit(db.get()) != 0 && reserved_object_count(db.get()) == 0,
            "failed bootstrap left a transaction or partial reserved schema", checks);
    require(scalar_u64(db.get(), "PRAGMA application_id;", "rollback application_id") == 0 &&
                scalar_u64(db.get(), "PRAGMA user_version;", "rollback user_version") == 0,
            "failed bootstrap leaked database markers", checks);
}

void test_partial_and_lookalike_rejection(std::uint64_t& checks) {
    {
        DatabaseFixture fixture("partial");
        SqlitePtr db = open_database(fixture.path);
        sqlite_exec_or_throw(
            db.get(),
            std::string(kPeerTransportIngressSchemaSqlObjects.front().ddl) + ";",
            "partial schema seed");
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, true, false, "partial schema");
            },
            "object count mismatch",
            "partial schema was silently healed",
            checks);
        require(reserved_object_count(db.get()) == 1 &&
                    scalar_u64(db.get(), "PRAGMA application_id;", "partial marker") == 0,
                "partial-schema rejection mutated the database", checks);
    }

    {
        DatabaseFixture fixture("quoted-literal-drift");
        SqlitePtr db = open_database(fixture.path);
        install_exact_schema(
            db.get(),
            [](const PeerTransportIngressSchemaSqlObject& object) {
                std::string ddl(object.ddl);
                if (object.name == "sync_peer_transport_ingress_envelopes") {
                    const std::string wanted = "'queued','claimed'";
                    const std::string altered = "'q u e u e d','claimed'";
                    const std::size_t at = ddl.find(wanted);
                    if (at == std::string::npos) fail("literal drift fixture not found");
                    ddl.replace(at, wanted.size(), altered);
                }
                return ddl;
            });
        set_markers(db.get());
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, false, false, "quoted literal drift");
            },
            "schema definition mismatch",
            "quoted semantic whitespace was erased by schema normalization",
            checks);
    }
}

void test_legacy_marker_migration(std::uint64_t& checks) {
    DatabaseFixture fixture("legacy");
    {
        SqlitePtr db = open_database(fixture.path);
        install_exact_schema(db.get());
        const PeerTransportIngressSchemaAttestation read_attestation =
            initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                db.owner.db, false, false, "legacy read inspection");
        require(read_attestation.schema_present() &&
                    read_attestation.legacy_unmarked(),
                "exact unmarked legacy schema was not identified", checks);
        require(scalar_u64(db.get(), "PRAGMA application_id;", "legacy read marker") == 0,
                "read inspection mutated legacy markers", checks);
    }
    {
        SqlitePtr db = open_database(fixture.path);
        const PeerTransportIngressSchemaAttestation migrated =
            initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                db.owner.db, true, false, "legacy write migration");
        require(migrated.schema_present() && !migrated.legacy_unmarked(),
                "legacy write migration did not return marked authority", checks);
        require(scalar_u64(db.get(), "PRAGMA application_id;", "legacy migrated app") ==
                    kPeerTransportIngressSqliteApplicationId &&
                    scalar_u64(db.get(), "PRAGMA user_version;", "legacy migrated user") ==
                        kPeerTransportIngressSqliteUserVersion,
                "legacy marker migration did not commit both markers", checks);
    }
}

void test_checkpoint_database_cohosting(std::uint64_t& checks) {
    {
        DatabaseFixture fixture("checkpoint-cohost");
        SqlitePtr db = open_database(fixture.path);
        sqlite_exec_or_throw(
            db.get(),
            "CREATE TABLE sync_session_schema_meta("
            "key TEXT PRIMARY KEY NOT NULL,value TEXT NOT NULL);"
            "INSERT INTO sync_session_schema_meta(key,value) "
            "VALUES('schema_version','rev0720-sync-session-checkpoint-v4');"
            "CREATE TABLE sync_session_checkpoint_probe(value INTEGER);",
            "checkpoint cohost seed");
        const PeerTransportIngressSchemaAttestation attestation =
            initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                db.owner.db, true, false, "checkpoint cohost bootstrap");
        require(attestation.schema_present() && !attestation.legacy_unmarked(),
                "reviewed checkpoint host did not admit peer-ingress bootstrap",
                checks);
        require(reserved_object_count(db.get()) ==
                    kPeerTransportIngressSchemaSqlObjects.size(),
                "checkpoint cohost did not receive the exact peer schema", checks);
        require(scalar_u64(db.get(),
                           "SELECT COUNT(*) FROM main.sqlite_schema WHERE "
                           "name='sync_session_checkpoint_probe';",
                           "checkpoint cohost probe") == 1,
                "peer bootstrap damaged the checkpoint namespace", checks);
        SyncSqliteTransaction cohost_verify(
            db.get(),
            "checkpoint cohost verify",
            SyncSqliteTransactionMode::Deferred);
        {
            SyncSqliteConnectionAuthorityLease authority_lease =
                verify_peer_transport_ingress_schema_attestation_current_or_throw(
                    db.owner.db, attestation, "checkpoint cohost current verification");
            cohost_verify.rollback();
        }
        ++checks;
    }

    {
        DatabaseFixture fixture("checkpoint-cross-domain-fk");
        SqlitePtr db = open_database(fixture.path);
        sqlite_exec_or_throw(
            db.get(),
            "CREATE TABLE sync_session_schema_meta("
            "key TEXT PRIMARY KEY NOT NULL,value TEXT NOT NULL);"
            "INSERT INTO sync_session_schema_meta(key,value) "
            "VALUES('schema_version','rev0720-sync-session-checkpoint-v4');"
            "CREATE TABLE sync_session_peer_delete_blocker("
            "session_id TEXT NOT NULL,"
            "transport_envelope_idempotency_key TEXT NOT NULL,"
            "FOREIGN KEY(session_id, transport_envelope_idempotency_key) REFERENCES "
            "sync_peer_transport_ingress_envelopes("
            "session_id, transport_envelope_idempotency_key) ON DELETE RESTRICT);",
            "checkpoint cross-domain foreign-key seed");
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, true, false, "checkpoint cross-domain bootstrap");
            },
            "cross-domain foreign key",
            "checkpoint cohost was allowed to alter peer-ingress deletion semantics",
            checks);
        require(reserved_object_count(db.get()) == 0,
                "cross-domain dependency rejection left partial peer schema",
                checks);
    }

    {
        DatabaseFixture fixture("checkpoint-unknown");
        SqlitePtr db = open_database(fixture.path);
        sqlite_exec_or_throw(
            db.get(),
            "CREATE TABLE sync_session_schema_meta("
            "key TEXT PRIMARY KEY NOT NULL,value TEXT NOT NULL);"
            "INSERT INTO sync_session_schema_meta(key,value) "
            "VALUES('schema_version','unreviewed-checkpoint-v99');",
            "unknown checkpoint seed");
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, true, false, "unknown checkpoint cohost");
            },
            "schema_version is not recognized",
            "unreviewed checkpoint host was claimed",
            checks);
        require(reserved_object_count(db.get()) == 0,
                "rejected checkpoint host was partially mutated", checks);
    }
}

void test_foreign_and_wrong_marker_rejection(std::uint64_t& checks) {
    {
        DatabaseFixture fixture("foreign");
        SqlitePtr db = open_database(fixture.path);
        sqlite_exec_or_throw(db.get(), "CREATE TABLE foreign_guard(x INTEGER);",
                             "foreign seed");
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, true, false, "foreign claim");
            },
            "refused to claim a nonempty foreign SQLite database",
            "writable bootstrap claimed a foreign database",
            checks);
        require(reserved_object_count(db.get()) == 0 &&
                    scalar_u64(db.get(),
                               "SELECT COUNT(*) FROM main.sqlite_schema "
                               "WHERE name='foreign_guard';",
                               "foreign guard count") == 1,
                "foreign-database rejection damaged the existing schema", checks);

        const PeerTransportIngressSchemaAttestation absent =
            initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                db.owner.db, false, true, "foreign read-only probe");
        require(!absent.schema_present() && absent.authorizes(db.get()),
                "read-only probe did not represent an intentionally absent schema",
                checks);
        SyncSqliteTransaction absent_verify(
            db.get(), "absent verification", SyncSqliteTransactionMode::Deferred);
        {
            SyncSqliteConnectionAuthorityLease authority_lease =
                verify_peer_transport_ingress_schema_attestation_current_or_throw(
                    db.owner.db, absent, "absent snapshot verification");
            absent_verify.rollback();
        }
        ++checks;
    }

    {
        DatabaseFixture fixture("foreign-after-peer");
        {
            SqlitePtr db = open_database(fixture.path);
            install_exact_schema(db.get());
            set_markers(db.get());
            sqlite_exec_or_throw(db.get(), "CREATE TABLE foreign_guard(x INTEGER);",
                                 "post-peer foreign seed");
        }
        SqlitePtr db = open_database(fixture.path);
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, false, false, "post-peer foreign inspection");
            },
            "cohosted with an unreviewed schema",
            "exact peer schema accepted an unreviewed cohost after bootstrap",
            checks);
    }

    {
        DatabaseFixture fixture("wrong-marker");
        SqlitePtr db = open_database(fixture.path);
        install_exact_schema(db.get());
        set_markers(db.get(), 7, kPeerTransportIngressSqliteUserVersion);
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, true, false, "wrong marker pair");
            },
            "does not identify the reviewed schema",
            "wrong application marker was accepted",
            checks);
    }
}

void test_schema_program_and_shadow_rejection(std::uint64_t& checks) {
    {
        DatabaseFixture fixture("trigger");
        {
            SqlitePtr db = open_database(fixture.path);
            install_exact_schema(db.get());
            set_markers(db.get());
            sqlite_exec_or_throw(
                db.get(),
                "CREATE TABLE trigger_probe(value TEXT);"
                "CREATE TRIGGER hostile_trigger AFTER INSERT ON "
                "sync_peer_transport_authority_records BEGIN "
                "INSERT INTO trigger_probe(value) VALUES('fired'); END;",
                "hostile trigger seed");
        }
        SqlitePtr db = open_database(fixture.path);
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, false, false, "trigger rejection");
            },
            "trigger or view schema programs",
            "preexisting trigger program was accepted",
            checks);
        require(scalar_u64(db.get(), "SELECT COUNT(*) FROM trigger_probe;",
                           "trigger probe rows") == 0,
                "rejected trigger executed during inspection", checks);
    }

    {
        SqlitePtr db = open_database(":memory:");
        sqlite_exec_or_throw(db.get(), "CREATE TEMP TABLE shadow(x);",
                             "temporary shadow seed");
        require_throws(
            [&] {
                (void)initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                    db.owner.db, true, false, "temporary shadow rejection");
            },
            "temporary schema objects",
            "temporary schema shadow was accepted",
            checks);
    }
}

void test_authorizer_ownership_and_generation(std::uint64_t& checks) {
    SqlitePtr db = open_database(":memory:");
    const PeerTransportIngressSchemaAttestation first =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            db.owner.db, true, false, "authorizer ownership baseline");
    require(first.authorizer_generation() == 1 && first.authorizes(db.get()),
            "initial schema attestation did not own authorizer generation one",
            checks);

    require(sqlite3_set_authorizer(db.get(), allow_all_authorizer, nullptr) ==
                SQLITE_OK,
            "could not install alien schema authorizer fixture",
            checks);
    require(!first.authorizes(db.get()),
            "schema attestation survived alien authorizer replacement",
            checks);
    require_throws(
        [&] {
            (void)verify_peer_transport_ingress_schema_attestation_current_or_throw(
                db.owner.db, first, "alien authorizer verification");
        },
        "authorizer ownership probe failed",
        "alien authorizer replacement retained schema authority",
        checks);

    const PeerTransportIngressSchemaAttestation second =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            db.owner.db, true, false, "authorizer ownership recovery");
    require(second.authorizer_generation() ==
                first.authorizer_generation() + 1,
            "schema authority recovery did not advance its generation",
            checks);
    require(!first.authorizes(db.get()) && second.authorizes(db.get()),
            "schema authority generation did not invalidate the stale proof",
            checks);
    require_throws(
        [&] {
            (void)verify_peer_transport_ingress_schema_attestation_current_or_throw(
                db.owner.db, first, "stale schema authority generation");
        },
        "authorizer generation changed",
        "superseded schema authority proof remained current",
        checks);

    SyncSqliteTransaction recovered_verify(
        db.get(), "recovered authority verify", SyncSqliteTransactionMode::Deferred);
    {
        SyncSqliteConnectionAuthorityLease authority_lease =
            verify_peer_transport_ingress_schema_attestation_current_or_throw(
                db.owner.db, second, "recovered schema authority verification");
        recovered_verify.rollback();
    }
    ++checks;

    require(sqlite3_set_authorizer(db.get(), nullptr, nullptr) == SQLITE_OK,
            "could not disable schema authorizer fixture",
            checks);
    require(!second.authorizes(db.get()),
            "schema attestation survived authorizer disablement",
            checks);
}

void test_owner_generation_pin_and_move(std::uint64_t& checks) {
    SqlitePtr db = open_database(":memory:");
    PeerTransportIngressSchemaAttestation attestation =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            db.owner.db, true, false, "owner-generation pin baseline");
    const std::uint64_t generation = db.owner.db.generation();
    require(generation != 0 && attestation.owner_generation() == generation,
            "schema attestation did not retain its exact owner generation",
            checks);
    require(db.owner.db.active_borrows() == 1,
            "schema attestation did not retain exactly one owner-generation pin",
            checks);

    PeerTransportIngressSchemaAttestation moved(std::move(attestation));
    require(attestation.owner_generation() == 0 &&
                moved.owner_generation() == generation &&
                moved.authorizes(db.get()),
            "schema attestation move did not transfer its owner-generation pin",
            checks);
    require(db.owner.db.active_borrows() == 1,
            "schema attestation move duplicated or lost its owner-generation pin",
            checks);

    SyncSqliteTransaction snapshot(
        db.get(), "moved attestation snapshot", SyncSqliteTransactionMode::Deferred);
    {
        SyncSqliteConnectionAuthorityLease authority_lease =
            verify_peer_transport_ingress_schema_attestation_current_or_throw(
                db.owner.db, moved, "moved attestation verification");
        snapshot.rollback();
    }
    ++checks;
}

#if defined(__linux__)
constexpr std::string_view kOwnerCloseHelper =
    "--anonsync-peer-schema-owner-close-helper-v1";

int run_owner_close_helper(int argc, char** argv) {
    try {
        anonsync::test::verify_self_exec_child_boundary_or_throw();
        if (argc != 2 || argv == nullptr || argv[1] == nullptr ||
            std::string_view(argv[1]) != kOwnerCloseHelper) {
            throw std::runtime_error("invalid schema owner-close helper instruction");
        }
        SqlitePtr db = open_database(":memory:");
        PeerTransportIngressSchemaAttestation attestation =
            initialize_or_inspect_peer_transport_ingress_schema_or_throw(
                db.owner.db, true, false, "self-exec owner-pin helper");
        if (attestation.owner_generation() != db.owner.db.generation() ||
            db.owner.db.active_borrows() != 1) {
            return 12;
        }
        // Strict owner destruction must fail before sqlite3_close() while the
        // exact schema-generation capability remains live. This is executed in
        // a fresh image rather than a child carrying parent SQLite state.
        db.owner.db.reset();
        return 13;
    } catch (const std::exception& error) {
        std::cerr << "schema owner-close helper failed: " << error.what() << '\n';
        return 14;
    }
}

void test_live_attestation_blocks_owner_close(std::uint64_t& checks) {
    anonsync::test::SelfExecTestProcess child =
        anonsync::test::spawn_self_exec_test_process_or_throw(
            anonsync::test::current_self_executable_or_throw(),
            {std::string(kOwnerCloseHelper)});
    child.wait_for_exact_exit(
        kSyncProcessCapabilityViolationExitCode, std::chrono::seconds(10),
        "live schema attestation owner-close fail-stop");
    require(true, "owner-pin self-exec helper was launched", checks);
    require(!child.active(), "owner-pin helper authority was consumed", checks);
    require(true,
            "live schema attestation did not fail-stop owner close", checks);
}
#endif

void test_generation_and_handle_binding(std::uint64_t& checks) {
    DatabaseFixture fixture("generation");
    SqlitePtr first = open_database(fixture.path);
    const PeerTransportIngressSchemaAttestation attestation =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            first.owner.db, true, false, "generation baseline");
    {
        SqlitePtr external = open_database(fixture.path);
        sqlite_exec_or_throw(external.get(), "CREATE TABLE external_generation(x);",
                             "external generation mutation");
    }
    SyncSqliteTransaction generation_verify(
        first.get(), "generation verify", SyncSqliteTransactionMode::Immediate);
    require_throws(
        [&] {
            (void)verify_peer_transport_ingress_schema_attestation_current_or_throw(
                first.owner.db, attestation, "generation verify");
        },
        "schema generation changed",
        "external schema generation change did not invalidate attestation",
        checks);
    generation_verify.rollback();

    SqlitePtr second = open_database(":memory:");
    const PeerTransportIngressSchemaAttestation second_attestation =
        initialize_or_inspect_peer_transport_ingress_schema_or_throw(
            second.owner.db, true, false, "second handle");
    SyncSqliteTransaction handle_mismatch(
        second.get(), "handle mismatch", SyncSqliteTransactionMode::Deferred);
    require_throws(
        [&] {
            (void)verify_peer_transport_ingress_schema_attestation_current_or_throw(
                second.owner.db, attestation, "handle mismatch");
        },
        "does not authorize this SQLite owner generation",
        "attestation capability crossed SQLite handles",
        checks);
    {
        SyncSqliteConnectionAuthorityLease authority_lease =
            verify_peer_transport_ingress_schema_attestation_current_or_throw(
                second.owner.db, second_attestation, "second handle control");
        handle_mismatch.rollback();
    }
    ++checks;
}

}  // namespace

int main(int argc, char** argv) {
#if defined(__linux__)
    if (argc >= 2 && argv != nullptr && argv[1] != nullptr &&
        std::string_view(argv[1]) == kOwnerCloseHelper) {
        return run_owner_close_helper(argc, argv);
    }
#endif
    std::uint64_t checks = 0;
    try {
        if (argc != 1) {
            throw std::runtime_error("unexpected schema attestation test arguments");
        }
        test_schema_token_identity(checks);
        test_atomic_payload_schema_ensure(checks);
        test_fresh_bootstrap(checks);
        test_atomic_bootstrap_rollback(checks);
        test_partial_and_lookalike_rejection(checks);
        test_legacy_marker_migration(checks);
        test_checkpoint_database_cohosting(checks);
        test_foreign_and_wrong_marker_rejection(checks);
        test_schema_program_and_shadow_rejection(checks);
        test_authorizer_ownership_and_generation(checks);
        test_owner_generation_pin_and_move(checks);
#if defined(__linux__)
        test_live_attestation_blocks_owner_close(checks);
#endif
        test_generation_and_handle_binding(checks);
        std::cout << "peer ingress schema attestation checks=" << checks
                  << " failures=0\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "peer ingress schema attestation checks=" << checks
                  << " failures=1 reason=" << e.what() << "\n";
        return 1;
    }
}
