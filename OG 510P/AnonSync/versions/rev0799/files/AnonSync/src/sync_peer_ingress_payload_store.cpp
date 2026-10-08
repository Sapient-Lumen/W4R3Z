#include "sync_peer_ingress_payload_store.hpp"

#include "anonsync_core_internal.hpp"
#include "sync_peer_ingress_schema_sql.hpp"
#include "sync_peer_ingress_wire.hpp"
#include "sync_sqlite_support.hpp"
#include "sync_sqlite_schema_identity.hpp"

#include <array>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

#include <sqlite3.h>

namespace anonsync {
namespace {

void validate_store_input_or_throw(const std::string& session_id,
                                   const std::string& transport_envelope_idempotency_key,
                                   const std::string& canonical_frame,
                                   const std::string& payload_digest,
                                   std::uint64_t stored_at_epoch,
                                   const std::string& label) {
    if (session_id.empty()) throw std::runtime_error(label + " session_id is empty");
    if (transport_envelope_idempotency_key.empty()) {
        throw std::runtime_error(label + " transport envelope idempotency key is empty");
    }
    if (canonical_frame.empty()) throw std::runtime_error(label + " canonical frame is empty");
    if (canonical_frame.size() > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        throw std::runtime_error(label + " canonical frame exceeds SQLite blob length range");
    }
    if (!is_lowercase_sha256_hex(payload_digest)) {
        throw std::runtime_error(label + " payload digest is not lowercase SHA-256 evidence");
    }
    if (stored_at_epoch == 0) throw std::runtime_error(label + " stored_at_epoch must be positive");
}


struct PayloadColumnSpec {
    const char* name;
    const char* type;
    std::uint64_t not_null;
    std::uint64_t primary_key_position;
};

std::string lower_ascii_copy(std::string value) {
    for (char& c : value) {
        const unsigned char uc = static_cast<unsigned char>(c);
        if (uc >= 'A' && uc <= 'Z') c = static_cast<char>(uc - 'A' + 'a');
    }
    return value;
}

void verify_payload_table_columns_or_throw(sqlite3* db,
                                           const std::string& label) {
    static constexpr std::array<PayloadColumnSpec, 8> expected{{
        {"session_id", "text", 1, 1},
        {"transport_envelope_idempotency_key", "text", 1, 2},
        {"codec_version", "integer", 1, 0},
        {"canonical_frame_sha256", "text", 1, 0},
        {"payload_digest", "text", 1, 0},
        {"canonical_frame_bytes", "integer", 1, 0},
        {"canonical_frame", "blob", 1, 0},
        {"stored_at_epoch", "integer", 1, 0}
    }};

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "PRAGMA main.table_xinfo('sync_peer_transport_ingress_payloads');",
        label + " table_xinfo prepare");
    std::size_t index = 0;
    while (true) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, label + " table_xinfo query");
        }
        if (index >= expected.size()) {
            throw std::runtime_error(label + " payload table has unexpected extra columns");
        }
        const PayloadColumnSpec& spec = expected[index];
        const std::uint64_t cid =
            sqlite_column_u64_or_throw(stmt.stmt, 0, label + " column id");
        const std::string name =
            sqlite_column_text_or_throw(stmt.stmt, 1, label + " column name");
        const std::string type = lower_ascii_copy(
            sqlite_column_text_or_throw(stmt.stmt, 2, label + " column type"));
        const std::uint64_t not_null =
            sqlite_column_u64_or_throw(stmt.stmt, 3, label + " column not-null");
        const std::uint64_t primary_key_position =
            sqlite_column_u64_or_throw(stmt.stmt, 5, label + " column primary key");
        const std::uint64_t hidden =
            sqlite_column_u64_or_throw(stmt.stmt, 6, label + " column hidden state");
        if (cid != index || name != spec.name || type != spec.type ||
            not_null != spec.not_null || hidden != 0 ||
            primary_key_position != spec.primary_key_position) {
            throw std::runtime_error(
                label + " payload table column " + std::to_string(index) +
                " does not match the required name/type/nullability/visibility/primary-key identity");
        }
        ++index;
    }
    if (index != expected.size()) {
        throw std::runtime_error(label + " payload table is missing required columns");
    }
}

void verify_payload_table_foreign_key_or_throw(sqlite3* db,
                                               const std::string& label) {
    static constexpr std::array<const char*, 2> expected_from{{
        "session_id", "transport_envelope_idempotency_key"}};
    static constexpr std::array<const char*, 2> expected_to{{
        "session_id", "transport_envelope_idempotency_key"}};

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "PRAGMA main.foreign_key_list('sync_peer_transport_ingress_payloads');",
        label + " foreign_key_list prepare");
    std::size_t index = 0;
    std::uint64_t expected_id = 0;
    bool have_id = false;
    while (true) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, label + " foreign_key_list query");
        }
        if (index >= expected_from.size()) {
            throw std::runtime_error(label + " payload table has unexpected foreign keys");
        }
        const std::uint64_t id =
            sqlite_column_u64_or_throw(stmt.stmt, 0, label + " foreign key id");
        const std::uint64_t sequence =
            sqlite_column_u64_or_throw(stmt.stmt, 1, label + " foreign key sequence");
        const std::string parent =
            sqlite_column_text_or_throw(stmt.stmt, 2, label + " foreign key parent");
        const std::string from =
            sqlite_column_text_or_throw(stmt.stmt, 3, label + " foreign key source");
        const std::string to =
            sqlite_column_text_or_throw(stmt.stmt, 4, label + " foreign key target");
        const std::string on_update = lower_ascii_copy(
            sqlite_column_text_or_throw(stmt.stmt, 5, label + " foreign key update action"));
        const std::string on_delete = lower_ascii_copy(
            sqlite_column_text_or_throw(stmt.stmt, 6, label + " foreign key delete action"));
        const std::string match = lower_ascii_copy(
            sqlite_column_text_or_throw(stmt.stmt, 7, label + " foreign key match"));
        if (!have_id) {
            expected_id = id;
            have_id = true;
        }
        if (id != expected_id || sequence != index ||
            parent != "sync_peer_transport_ingress_envelopes" ||
            from != expected_from[index] || to != expected_to[index] ||
            on_update != "restrict" || on_delete != "cascade" || match != "none") {
            throw std::runtime_error(
                label + " payload table composite foreign key identity is not exact");
        }
        ++index;
    }
    if (index != expected_from.size()) {
        throw std::runtime_error(
            label + " payload table is missing the exact composite cascade foreign key");
    }
}

const PeerTransportIngressSchemaSqlObject& required_payload_schema_object(
    std::string_view name);

void verify_payload_table_checks_or_throw(sqlite3* db,
                                          const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT sql FROM main.sqlite_schema WHERE type='table' AND "
        "name='sync_peer_transport_ingress_payloads';",
        label + " sqlite_schema prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) {
        if (rc != SQLITE_DONE) {
            throw_sqlite_exception(db, rc, label + " sqlite_schema query");
        }
        throw std::runtime_error(label + " payload table definition is absent");
    }
    const std::string canonical_sql = canonicalize_sqlite_schema_sql_or_throw(
        sqlite_column_text_or_throw(stmt.stmt, 0, label + " table SQL"));
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(label + " payload table definition is ambiguous");
    }
    const PeerTransportIngressSchemaSqlObject& expected =
        required_payload_schema_object("sync_peer_transport_ingress_payloads");
    if (canonical_sql != canonicalize_sqlite_schema_sql_or_throw(expected.ddl)) {
        throw std::runtime_error(
            label + " payload table is missing a required CHECK constraint "
                    "or differs from the exact reviewed definition");
    }
}

const PeerTransportIngressSchemaSqlObject& required_payload_schema_object(
    std::string_view name) {
    for (const PeerTransportIngressSchemaSqlObject& object :
         kPeerTransportIngressSchemaSqlObjects) {
        if (object.name == name) return object;
    }
    throw std::logic_error("reviewed payload schema object is absent from the manifest");
}

std::string main_schema_creation_sql_or_throw(
    const PeerTransportIngressSchemaSqlObject& object) {
    std::string sql(object.ddl);
    const std::string prefix = object.type == "table"
        ? "CREATE TABLE "
        : object.type == "index" ? "CREATE INDEX " : "";
    if (prefix.empty() || sql.rfind(prefix, 0) != 0) {
        throw std::logic_error(
            "reviewed payload schema object has an unsupported creation form");
    }
    // SQLite records the canonical object SQL without this qualifier, but the
    // execution-time qualifier prevents TEMP-first name resolution from
    // redirecting index creation to a same-named look-alike table.
    sql.insert(prefix.size(), "main.");
    return sql + ";";
}

bool schema_object_exists_or_throw(sqlite3* db,
                                   std::string_view type,
                                   std::string_view name,
                                   const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT COUNT(*) FROM main.sqlite_schema WHERE type=? AND name=?;",
        label + " existence prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, std::string(type), label + " type");
    sqlite_bind_text_or_throw(stmt.stmt, 2, std::string(name), label + " name");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " existence query");
    const std::uint64_t count =
        sqlite_column_u64_or_throw(stmt.stmt, 0, label + " existence count");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE || count > 1) {
        throw std::runtime_error(label + " schema identity is ambiguous");
    }
    return count == 1;
}

void verify_exact_payload_schema_object_or_throw(
    sqlite3* db,
    const PeerTransportIngressSchemaSqlObject& expected,
    const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT tbl_name, sql FROM main.sqlite_schema WHERE type=? AND name=?;",
        label + " exact object prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, std::string(expected.type),
                              label + " expected type");
    sqlite_bind_text_or_throw(stmt.stmt, 2, std::string(expected.name),
                              label + " expected name");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) {
        throw std::runtime_error(label + " reviewed schema object is absent");
    }
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " exact object query");
    const std::string table_name =
        sqlite_column_text_or_throw(stmt.stmt, 0, label + " table name");
    const std::string observed_sql = canonicalize_sqlite_schema_sql_or_throw(
        sqlite_column_text_or_throw(stmt.stmt, 1, label + " SQL"));
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(label + " reviewed schema object is ambiguous");
    }
    if (table_name != expected.table_name ||
        observed_sql != canonicalize_sqlite_schema_sql_or_throw(expected.ddl)) {
        throw std::runtime_error(label + " differs from the exact reviewed definition");
    }
}

class PayloadSchemaSavepoint final {
private:
    sqlite3* db_ = nullptr;
    SyncSqliteProcessId process_id_ = 0;
    std::string label_;
    bool active_ = false;

public:
    PayloadSchemaSavepoint(sqlite3* db, std::string label)
        : db_(db),
          process_id_(current_sync_sqlite_process_id_noexcept()),
          label_(std::move(label)),
          active_(true) {
        sqlite_exec_or_throw(db_,
                             "SAVEPOINT anonsync_peer_payload_schema;",
                             label_ + " savepoint begin");
    }
    PayloadSchemaSavepoint(const PayloadSchemaSavepoint&) = delete;
    PayloadSchemaSavepoint& operator=(const PayloadSchemaSavepoint&) = delete;
    ~PayloadSchemaSavepoint() {
        if (!active_ || db_ == nullptr) return;
        if (!sync_sqlite_process_id_is_current(process_id_)) {
            fail_stop_on_sync_sqlite_capability_violation_noexcept();
        }
        sqlite3_exec(db_,
                     "ROLLBACK TO anonsync_peer_payload_schema;"
                     "RELEASE anonsync_peer_payload_schema;",
                     nullptr,
                     nullptr,
                     nullptr);
    }
    void commit() {
        require_sync_sqlite_process_id_or_fail_stop(
            process_id_, label_ + " savepoint commit");
        sqlite_exec_or_throw(db_,
                             "RELEASE anonsync_peer_payload_schema;",
                             label_ + " savepoint release");
        active_ = false;
    }
};

void verify_stored_payload_integrity_or_throw(
    const PeerTransportIngressStoredPayload& stored,
    const std::string& label) {
    if (!stored.found) throw std::runtime_error(label + " stored payload was not found");
    if (stored.codec_version != kPeerTransportIngressWireCodecVersion) {
        throw std::runtime_error(label + " stored payload uses an unsupported codec version");
    }
    if (!is_lowercase_sha256_hex(stored.canonical_frame_sha256)) {
        throw std::runtime_error(label + " stored canonical frame digest is malformed");
    }
    if (!is_lowercase_sha256_hex(stored.payload_digest)) {
        throw std::runtime_error(label + " stored payload digest is malformed");
    }
    if (stored.canonical_frame.empty()) {
        throw std::runtime_error(label + " stored canonical frame is empty");
    }
    if (stored.canonical_frame_bytes != static_cast<std::uint64_t>(stored.canonical_frame.size())) {
        throw std::runtime_error(label + " stored canonical frame byte count differs from blob length");
    }
    if (sha256_hex(stored.canonical_frame) != stored.canonical_frame_sha256) {
        throw std::runtime_error(label + " stored canonical frame digest differs from blob bytes");
    }
    if (stored.stored_at_epoch == 0) {
        throw std::runtime_error(label + " stored payload timestamp is invalid");
    }
}

}  // namespace

void ensure_peer_transport_ingress_payload_store_schema_or_throw(
    sqlite3* db,
    const std::string& label) {
    if (db == nullptr) throw std::invalid_argument(label + " database handle is null");
    const PeerTransportIngressSchemaSqlObject& table =
        required_payload_schema_object("sync_peer_transport_ingress_payloads");
    const PeerTransportIngressSchemaSqlObject& index =
        required_payload_schema_object("idx_sync_peer_transport_ingress_payload_digest");

    PayloadSchemaSavepoint savepoint(db, label + " atomic payload schema");
    if (schema_object_exists_or_throw(db, table.type, table.name,
                                      label + " payload table")) {
        // Validate a pre-existing object before adding anything else. A
        // look-alike table must not be decorated with an index and then
        // rejected after a partial mutation.
        verify_payload_table_columns_or_throw(db, label);
        verify_payload_table_foreign_key_or_throw(db, label);
        verify_payload_table_checks_or_throw(db, label);
        verify_exact_payload_schema_object_or_throw(
            db, table, label + " payload table identity");
    } else {
        sqlite_exec_or_throw(db,
                             main_schema_creation_sql_or_throw(table),
                             label + " create reviewed ingress payload table");
    }

    if (schema_object_exists_or_throw(db, index.type, index.name,
                                      label + " payload index")) {
        verify_exact_payload_schema_object_or_throw(
            db, index, label + " payload index identity");
    } else {
        sqlite_exec_or_throw(db,
                             main_schema_creation_sql_or_throw(index),
                             label + " create reviewed ingress payload digest index");
    }

    verify_peer_transport_ingress_payload_store_schema_or_throw(
        db, label + " exact schema verification");
    savepoint.commit();
}

void verify_peer_transport_ingress_payload_store_schema_or_throw(
    sqlite3* db,
    const std::string& label) {
    if (db == nullptr) throw std::invalid_argument(label + " database handle is null");
    verify_payload_table_columns_or_throw(db, label);
    verify_payload_table_foreign_key_or_throw(db, label);
    verify_payload_table_checks_or_throw(db, label);
    verify_exact_payload_schema_object_or_throw(
        db,
        required_payload_schema_object("sync_peer_transport_ingress_payloads"),
        label + " payload table identity");
    verify_exact_payload_schema_object_or_throw(
        db,
        required_payload_schema_object("idx_sync_peer_transport_ingress_payload_digest"),
        label + " payload index identity");
}

VerifiedPeerTransportIngressPayloadStoreSchema
verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& label) {
    if (!transaction.authorizes(db)) {
        throw std::invalid_argument(
            label + " requires authority from the exact active SQLite transaction");
    }
    verify_peer_transport_ingress_payload_store_schema_or_throw(db, label);
    VerifiedPeerTransportIngressPayloadStoreSchema verified(db, transaction);
    if (!verified.authorizes(db)) {
        throw std::runtime_error(
            label + " schema verification did not establish a live main-database snapshot");
    }
    return verified;
}

PeerTransportIngressStoredPayload
load_peer_transport_ingress_stored_payload_from_verified_schema_or_throw(
    sqlite3* db,
    const VerifiedPeerTransportIngressPayloadStoreSchema& verified_schema,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    if (!verified_schema.authorizes(db)) {
        throw std::invalid_argument(
            label + " payload-store schema capability no longer authorizes this exact SQLite snapshot");
    }
    if (max_frame_bytes == 0) {
        throw std::runtime_error(label + " max_frame_bytes must be positive");
    }
    PeerTransportIngressStoredPayload out;
    // Keep the BLOB as the final projected column. SQLite lets us validate the
    // independently constrained byte counts before sqlite3_column_blob()
    // materializes untrusted persistent bytes into a std::string.
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT codec_version, canonical_frame_sha256, payload_digest, canonical_frame_bytes, "
        "length(canonical_frame), stored_at_epoch, canonical_frame "
        "FROM main.sync_peer_transport_ingress_payloads "
        "WHERE session_id=? AND transport_envelope_idempotency_key=?;",
        label + " load prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, session_id, label + " load session");
    sqlite_bind_text_or_throw(
        stmt.stmt, 2, transport_envelope_idempotency_key, label + " load transport key");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return out;
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " load query");
    out.found = true;
    out.codec_version = sqlite_column_u64_or_throw(stmt.stmt, 0, label + " codec version");
    out.canonical_frame_sha256 = sqlite_column_text_or_throw(stmt.stmt, 1, label + " frame digest");
    out.payload_digest = sqlite_column_text_or_throw(stmt.stmt, 2, label + " payload digest");
    out.canonical_frame_bytes = sqlite_column_u64_or_throw(stmt.stmt, 3, label + " frame bytes");
    const std::uint64_t sqlite_blob_bytes =
        sqlite_column_u64_or_throw(stmt.stmt, 4, label + " sqlite blob length");
    out.stored_at_epoch = sqlite_column_u64_or_throw(stmt.stmt, 5, label + " stored at");
    if (out.canonical_frame_bytes == 0 ||
        out.canonical_frame_bytes != sqlite_blob_bytes) {
        throw std::runtime_error(label + " stored frame byte counts are contradictory");
    }
    if (out.canonical_frame_bytes > max_frame_bytes) {
        throw std::runtime_error(label + " stored frame exceeds configured max_frame_bytes before blob load");
    }
    if (out.canonical_frame_bytes >
        static_cast<std::uint64_t>(std::numeric_limits<int>::max())) {
        throw std::runtime_error(label + " stored frame exceeds SQLite blob length range");
    }
    out.canonical_frame = sqlite_column_blob_or_throw(
        stmt.stmt, 6, max_frame_bytes, label + " canonical frame");
    if (sqlite3_step(stmt.stmt) != SQLITE_DONE) {
        throw std::runtime_error(label + " load returned more than one payload row");
    }
    verify_stored_payload_integrity_or_throw(out, label);
    return out;
}

PeerTransportIngressStoredPayload load_peer_transport_ingress_stored_payload_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    std::uint64_t max_frame_bytes,
    const std::string& label) {
    const VerifiedPeerTransportIngressPayloadStoreSchema verified_schema =
        verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw(
            db, transaction, label + " schema");
    return load_peer_transport_ingress_stored_payload_from_verified_schema_or_throw(
        db,
        verified_schema,
        session_id,
        transport_envelope_idempotency_key,
        max_frame_bytes,
        label);
}

PeerTransportIngressPayloadStoreOutcome store_or_verify_peer_transport_ingress_payload_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    const std::string& canonical_frame,
    const std::string& payload_digest,
    const PeerTransportIngressWireLimits& wire_limits,
    std::uint64_t stored_at_epoch,
    const std::string& label) {
    if (!transaction.authorizes_write(db)) {
        throw std::invalid_argument(
            label + " requires authority from the exact active SQLite write transaction");
    }
    const VerifiedPeerTransportIngressPayloadStoreSchema verified_schema =
        verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw(
            db, transaction, label + " schema");
    validate_store_input_or_throw(
        session_id,
        transport_envelope_idempotency_key,
        canonical_frame,
        payload_digest,
        stored_at_epoch,
        label);

    // Do not let the persistence helper become a second, weaker authority
    // boundary. The exact bytes stored under a queue identity must themselves
    // decode as canonical evidence for that identity and digest. This remains
    // true even when a future caller bypasses the normal encoder path.
    PeerTransportIngressWirePayload decoded;
    const SyncValidationResult decoded_result = decode_peer_transport_ingress_wire_frame(
        wire_limits, canonical_frame, decoded);
    if (!decoded_result.ok) {
        throw std::runtime_error(
            label + " canonical frame failed wire verification: " + decoded_result.reason);
    }
    if (decoded.transport_envelope.transport_envelope_idempotency_key !=
        transport_envelope_idempotency_key) {
        throw std::runtime_error(
            label + " canonical frame identity differs from the payload-store key");
    }
    if (decoded.payload_digest != payload_digest) {
        throw std::runtime_error(
            label + " canonical frame digest differs from the payload-store digest");
    }

    const std::string frame_digest = sha256_hex(canonical_frame);
    PeerTransportIngressStoredPayload existing =
        load_peer_transport_ingress_stored_payload_from_verified_schema_or_throw(
        db,
        verified_schema,
        session_id,
        transport_envelope_idempotency_key,
        static_cast<std::uint64_t>(canonical_frame.size()),
        label + " existing");
    if (existing.found) {
        if (existing.codec_version != kPeerTransportIngressWireCodecVersion ||
            existing.canonical_frame_sha256 != frame_digest ||
            existing.payload_digest != payload_digest ||
            existing.canonical_frame_bytes != static_cast<std::uint64_t>(canonical_frame.size()) ||
            existing.canonical_frame != canonical_frame) {
            throw std::runtime_error(
                label + " existing durable payload contradicts the submitted canonical frame");
        }
        return PeerTransportIngressPayloadStoreOutcome::AlreadyPresent;
    }

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "INSERT INTO main.sync_peer_transport_ingress_payloads("
        "session_id, transport_envelope_idempotency_key, codec_version, canonical_frame_sha256, "
        "payload_digest, canonical_frame_bytes, canonical_frame, stored_at_epoch) "
        "VALUES(?,?,?,?,?,?,?,?);",
        label + " insert prepare");
    int i = 1;
    sqlite_bind_text_or_throw(stmt.stmt, i++, session_id, label + " insert session");
    sqlite_bind_text_or_throw(
        stmt.stmt, i++, transport_envelope_idempotency_key, label + " insert transport key");
    sqlite_bind_u64_or_throw(
        stmt.stmt, i++, kPeerTransportIngressWireCodecVersion, label + " insert codec version");
    sqlite_bind_text_or_throw(stmt.stmt, i++, frame_digest, label + " insert frame digest");
    sqlite_bind_text_or_throw(stmt.stmt, i++, payload_digest, label + " insert payload digest");
    sqlite_bind_u64_or_throw(
        stmt.stmt, i++, static_cast<std::uint64_t>(canonical_frame.size()), label + " insert frame bytes");
    sqlite_bind_blob_or_throw(stmt.stmt, i++, canonical_frame, label + " insert frame blob");
    sqlite_bind_u64_or_throw(stmt.stmt, i++, stored_at_epoch, label + " insert stored at");
    sqlite_step_done_or_throw(stmt.stmt, label + " insert");
    return PeerTransportIngressPayloadStoreOutcome::Inserted;
}

}  // namespace anonsync
