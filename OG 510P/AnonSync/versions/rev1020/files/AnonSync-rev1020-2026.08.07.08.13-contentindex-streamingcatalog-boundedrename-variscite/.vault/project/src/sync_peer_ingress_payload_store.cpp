#include "sync_peer_ingress_payload_store.hpp"

#include "sha256_digest.hpp"
#include "sync_peer_ingress_wire.hpp"
#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>

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
