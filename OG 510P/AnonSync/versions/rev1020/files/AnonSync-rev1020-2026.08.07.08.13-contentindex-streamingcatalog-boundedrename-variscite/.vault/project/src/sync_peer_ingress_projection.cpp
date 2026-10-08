#include "sync_peer_ingress_projection.hpp"

#include "persistence/sqlite_projection_decoder.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <stdexcept>
#include <string>
#include <utility>

namespace anonsync {
namespace {

bool valid_ingress_state(const std::string& state) noexcept {
    return state == "queued" || state == "claimed" || state == "completed" ||
           state == "failed" || state == "abandoned";
}

void verify_operational_shape_or_throw(
    const std::string& state,
    std::uint64_t attempts,
    std::uint64_t max_attempts,
    std::uint64_t retry_backoff_seconds,
    std::uint64_t retry_at_epoch,
    const std::string& worker_id,
    const std::string& worker_lease_id,
    std::uint64_t claimed_at_epoch,
    std::uint64_t lease_expires_at_epoch,
    const std::string& label) {
    if (!valid_ingress_state(state)) {
        throw std::runtime_error(label + " rejected unknown ingress lifecycle state");
    }
    if (max_attempts == 0) {
        throw std::runtime_error(label + " rejected zero max_attempts");
    }
    if (retry_backoff_seconds == 0) {
        throw std::runtime_error(label + " rejected zero retry_backoff_seconds");
    }
    if (attempts > max_attempts) {
        throw std::runtime_error(label + " rejected attempts above max_attempts");
    }
    if (lease_expires_at_epoch < claimed_at_epoch) {
        throw std::runtime_error(label + " rejected inverted claim lease interval");
    }
    const bool any_claim_identity =
        !worker_id.empty() || !worker_lease_id.empty() || claimed_at_epoch != 0 ||
        lease_expires_at_epoch != 0;
    const bool complete_claim_identity =
        !worker_id.empty() && !worker_lease_id.empty() && claimed_at_epoch != 0 &&
        lease_expires_at_epoch != 0;
    if (any_claim_identity && !complete_claim_identity) {
        throw std::runtime_error(label + " rejected incomplete retained claim identity");
    }
    if (complete_claim_identity && attempts == 0) {
        throw std::runtime_error(label + " rejected claim identity without an attempt");
    }
    if (state == "queued" &&
        (attempts != 0 || retry_at_epoch != 0 || any_claim_identity)) {
        throw std::runtime_error(label + " rejected non-initial queued lifecycle shape");
    }
    if (state == "claimed" &&
        (!complete_claim_identity || attempts == 0 ||
         retry_at_epoch != lease_expires_at_epoch)) {
        throw std::runtime_error(label + " rejected incomplete claimed-generation identity");
    }
}

}  // namespace

persistence::CanonicalIngressProjection canonical_peer_transport_ingress_projection(
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::string& payload_digest_sha256) {
    persistence::CanonicalIngressProjection out;
    out.transport_envelope_idempotency_key =
        transport_envelope.transport_envelope_idempotency_key;
    out.transport_instance_id = transport_envelope.transport_instance_id;
    out.transport_key_id = transport_envelope.transport_key_id;
    out.peer_id = transport_envelope.peer_batch_envelope.peer_id;
    out.peer_session_id = transport_envelope.peer_batch_envelope.peer_session_id;
    out.peer_response_batch_idempotency_key =
        transport_envelope.peer_batch_envelope.peer_response_batch_idempotency_key;
    out.logical_path = transport_envelope.peer_batch_envelope.path.value;
    out.payload_digest_sha256 = payload_digest_sha256;
    out.response_count = transport_envelope.peer_batch_envelope.response_count;
    out.total_bytes = transport_envelope.peer_batch_envelope.total_bytes;
    out.issued_at_epoch = transport_envelope.issued_at_epoch;
    out.expires_at_epoch = transport_envelope.expires_at_epoch;
    return out;
}

bool peer_transport_ingress_row_exists_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT 1 FROM sync_peer_transport_ingress_envelopes "
        "WHERE session_id=? AND transport_envelope_idempotency_key=?;",
        label + " existence prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, session_id, label + " existence session");
    sqlite_bind_text_or_throw(
        stmt.stmt,
        2,
        transport_envelope_idempotency_key,
        label + " existence transport key");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return false;
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " existence query");
    const int trailing_rc = sqlite3_step(stmt.stmt);
    if (trailing_rc == SQLITE_ROW) {
        throw std::runtime_error(label + " existence query returned duplicate primary-key rows");
    }
    if (trailing_rc != SQLITE_DONE) {
        throw_sqlite_exception(db, trailing_rc, label + " existence trailing row check");
    }
    return true;
}

std::optional<PeerTransportIngressRowSnapshot>
load_verified_peer_transport_ingress_row_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    const persistence::CanonicalIngressProjection& canonical,
    const std::string& label) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT transport_envelope_idempotency_key, transport_instance_id, transport_key_id, "
        "peer_id, peer_session_id, peer_response_batch_idempotency_key, path, payload_digest, "
        "response_count, total_bytes, issued_at_epoch, expires_at_epoch, "
        "state, attempts, max_attempts, retry_backoff_seconds, retry_at_epoch, "
        "worker_id, worker_lease_id, claimed_at_epoch, lease_expires_at_epoch "
        "FROM sync_peer_transport_ingress_envelopes "
        "WHERE session_id=? AND transport_envelope_idempotency_key=?;",
        label + " verified select prepare");
    sqlite_bind_text_or_throw(stmt.stmt, 1, session_id, label + " verified select session");
    sqlite_bind_text_or_throw(
        stmt.stmt,
        2,
        transport_envelope_idempotency_key,
        label + " verified select transport key");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc == SQLITE_DONE) return std::nullopt;
    if (rc != SQLITE_ROW) throw_sqlite_exception(db, rc, label + " verified select row");

    const persistence::ProjectionColumnMap columns{
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11};
    persistence::ProjectionDecodeResult decoded =
        persistence::SqliteProjectionDecoder::decode(stmt.stmt, columns);
    if (!decoded) {
        throw std::runtime_error(
            label + " rejected persisted ingress projection: " +
            decoded.error().safe_summary());
    }
    persistence::ProjectionVerificationResult verified =
        persistence::CanonicalProjectionVerifier::verify(canonical, decoded.value());
    if (!verified) {
        throw std::runtime_error(
            label + " rejected persisted ingress projection: " +
            verified.error().safe_summary());
    }

    std::string state = sqlite_column_text_or_throw(stmt.stmt, 12, label + " state");
    const std::uint64_t attempts =
        sqlite_column_u64_or_throw(stmt.stmt, 13, label + " attempts");
    const std::uint64_t max_attempts =
        sqlite_column_u64_or_throw(stmt.stmt, 14, label + " max attempts");
    const std::uint64_t retry_backoff_seconds =
        sqlite_column_u64_or_throw(stmt.stmt, 15, label + " retry backoff");
    const std::uint64_t retry_at_epoch =
        sqlite_column_u64_or_throw(stmt.stmt, 16, label + " retry at");
    std::string worker_id =
        sqlite_column_text_or_throw(stmt.stmt, 17, label + " worker id");
    std::string worker_lease_id =
        sqlite_column_text_or_throw(stmt.stmt, 18, label + " worker lease id");
    const std::uint64_t claimed_at_epoch =
        sqlite_column_u64_or_throw(stmt.stmt, 19, label + " claimed at");
    const std::uint64_t lease_expires_at_epoch =
        sqlite_column_u64_or_throw(stmt.stmt, 20, label + " lease expires");

    verify_operational_shape_or_throw(
        state,
        attempts,
        max_attempts,
        retry_backoff_seconds,
        retry_at_epoch,
        worker_id,
        worker_lease_id,
        claimed_at_epoch,
        lease_expires_at_epoch,
        label);

    const int trailing_rc = sqlite3_step(stmt.stmt);
    if (trailing_rc == SQLITE_ROW) {
        throw std::runtime_error(label + " verified select returned duplicate primary-key rows");
    }
    if (trailing_rc != SQLITE_DONE) {
        throw_sqlite_exception(db, trailing_rc, label + " verified select trailing row check");
    }

    return PeerTransportIngressRowSnapshot(
        verified.take_value(),
        std::move(state),
        attempts,
        max_attempts,
        retry_backoff_seconds,
        retry_at_epoch,
        std::move(worker_id),
        std::move(worker_lease_id),
        claimed_at_epoch,
        lease_expires_at_epoch);
}

}  // namespace anonsync
