#include "sync_peer_ingress_retention.hpp"

#include "anonsync_core_internal.hpp"
#include "sync_peer_ingress_payload_store.hpp"
#include "sync_peer_ingress_projection.hpp"
#include "sync_sqlite_support.hpp"

#include <sqlite3.h>

#include <limits>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

std::uint64_t retention_sql_limit(std::uint64_t max_rows) {
    const std::uint64_t sqlite_max = static_cast<std::uint64_t>(
        std::numeric_limits<sqlite3_int64>::max());
    if (max_rows == 0 || max_rows > sqlite_max) return sqlite_max;
    return max_rows;
}

void checked_add_retention_bytes_or_throw(std::uint64_t& total,
                                          std::uint64_t value,
                                          const std::string& label) {
    if (value > std::numeric_limits<std::uint64_t>::max() - total) {
        throw std::runtime_error(label + " canonical retention byte total overflow");
    }
    total += value;
}

void require_exact_change_count_or_throw(sqlite3* db,
                                         sqlite3_int64 expected,
                                         const std::string& label) {
    const sqlite3_int64 actual = sqlite3_changes64(db);
    if (actual != expected) {
        throw std::runtime_error(
            label + " expected exactly " + std::to_string(expected) +
            " durable row change(s), observed " + std::to_string(actual));
    }
}

void reset_statement_or_throw(sqlite3* db,
                              sqlite3_stmt* stmt,
                              const std::string& label) {
    int rc = sqlite3_reset(stmt);
    if (rc != SQLITE_OK) throw_sqlite_exception(db, rc, label + " reset");
    rc = sqlite3_clear_bindings(stmt);
    if (rc != SQLITE_OK) throw_sqlite_exception(db, rc, label + " clear bindings");
}

std::string terminal_candidate_evidence_sha256(
    const std::string& state,
    const PeerTransportIngressStoredPayload& stored,
    const persistence::CanonicalIngressProjection& canonical) {
    return sha256_hex(length_prefixed_security_tuple(
        "anonsync-sync-peer-transport-terminal-retention-candidate-evidence-v1",
        {
            {"state", state},
            {"canonical_frame_sha256", stored.canonical_frame_sha256},
            {"payload_digest", canonical.payload_digest_sha256},
            {"canonical_frame_bytes", std::to_string(stored.canonical_frame_bytes)},
            {"logical_bytes", std::to_string(canonical.total_bytes)},
            {"response_count", std::to_string(canonical.response_count)},
            {"issued_at_epoch", std::to_string(canonical.issued_at_epoch)},
            {"expires_at_epoch", std::to_string(canonical.expires_at_epoch)},
            {"stored_at_epoch", std::to_string(stored.stored_at_epoch)},
        }));
}

std::string candidate_set_sha256_or_throw(
    const std::string& event_kind,
    const std::string& state_drained,
    const std::vector<PeerTransportRetentionCandidate>& candidates,
    const std::string& label) {
    if (event_kind.empty() || state_drained.empty()) {
        throw std::runtime_error(label + " candidate-set domain is empty");
    }
    if (candidates.empty()) {
        throw std::runtime_error(label + " candidate set cannot be empty");
    }

    std::string material = length_prefixed_security_tuple(
        "anonsync-sync-peer-transport-retention-candidate-set-v1",
        {
            {"event_kind", event_kind},
            {"state_drained", state_drained},
            {"candidate_count", std::to_string(candidates.size())},
        });
    std::set<std::pair<std::string, std::uint64_t>> exact_identities;
    for (std::size_t index = 0; index < candidates.size(); ++index) {
        const PeerTransportRetentionCandidate& candidate = candidates[index];
        if (candidate.transport_envelope_idempotency_key.empty() ||
            candidate.lifecycle_epoch == 0 || candidate.logical_bytes == 0 ||
            !is_lowercase_sha256_hex(candidate.evidence_sha256)) {
            throw std::runtime_error(
                label + " candidate set contains an invalid exact evidence identity");
        }
        if (!exact_identities
                 .emplace(candidate.transport_envelope_idempotency_key,
                          candidate.lifecycle_epoch)
                 .second) {
            throw std::runtime_error(
                label + " candidate set contains a duplicate exact identity");
        }
        material += length_prefixed_security_tuple(
            "anonsync-sync-peer-transport-retention-candidate-set-item-v1",
            {
                {"ordinal", std::to_string(index)},
                {"transport_envelope_idempotency_key",
                 candidate.transport_envelope_idempotency_key},
                {"lifecycle_epoch", std::to_string(candidate.lifecycle_epoch)},
                {"logical_bytes", std::to_string(candidate.logical_bytes)},
                {"evidence_sha256", candidate.evidence_sha256},
            });
    }
    return sha256_hex(material);
}

void finalize_selection_or_throw(
    PeerTransportRetentionSelection& selection,
    const std::string& event_kind,
    const std::string& state_drained,
    const std::string& label) {
    selection.rows = static_cast<std::uint64_t>(selection.candidates.size());
    if (selection.rows == 0) {
        if (selection.bytes != 0) {
            throw std::runtime_error(label + " empty candidate set has a nonzero byte total");
        }
        selection.candidate_set_sha256.clear();
        return;
    }
    selection.candidate_set_sha256 = candidate_set_sha256_or_throw(
        event_kind, state_drained, selection.candidates, label);
}

void verify_selection_or_throw(
    const PeerTransportRetentionSelection& selection,
    const std::string& event_kind,
    const std::string& state_drained,
    const std::string& label) {
    if (selection.rows != selection.candidates.size()) {
        throw std::runtime_error(label + " retention selection cardinality is contradictory");
    }
    if (selection.rows == 0) {
        if (selection.bytes != 0 || !selection.candidate_set_sha256.empty()) {
            throw std::runtime_error(label + " empty retention selection has durable claims");
        }
        return;
    }

    std::uint64_t checked_bytes = 0;
    for (const PeerTransportRetentionCandidate& candidate : selection.candidates) {
        checked_add_retention_bytes_or_throw(
            checked_bytes, candidate.logical_bytes, label + " selection");
    }
    if (checked_bytes != selection.bytes) {
        throw std::runtime_error(label + " retention selection byte total is contradictory");
    }
    const std::string expected_candidate_set_sha256 = candidate_set_sha256_or_throw(
        event_kind, state_drained, selection.candidates, label);
    if (selection.candidate_set_sha256 != expected_candidate_set_sha256) {
        throw std::runtime_error(
            label + " retention selection candidate-set commitment is contradictory");
    }
}

}  // namespace

std::string peer_transport_retention_event_idempotency_key(
    const std::string& session_id,
    const std::string& event_kind,
    const std::string& state_drained,
    std::uint64_t older_than_epoch,
    std::uint64_t max_rows,
    std::uint64_t drained_rows,
    std::uint64_t drained_bytes,
    const std::string& candidate_set_sha256,
    std::uint64_t retained_at_epoch,
    const std::string& operator_id,
    const std::string& reason) {
    if (!is_lowercase_sha256_hex(candidate_set_sha256)) {
        throw std::invalid_argument(
            "peer transport retention event requires a lowercase candidate-set SHA-256 commitment");
    }
    if (drained_rows == 0 || drained_bytes == 0) {
        throw std::invalid_argument(
            "peer transport retention event requires positive drained evidence");
    }
    const std::string material = length_prefixed_security_tuple(
        "anonsync-sync-peer-transport-ingress-retention-event-v2",
        {
            {"session_id", session_id},
            {"event_kind", event_kind},
            {"state_drained", state_drained},
            {"older_than_epoch", std::to_string(older_than_epoch)},
            {"max_rows", std::to_string(max_rows)},
            {"drained_rows", std::to_string(drained_rows)},
            {"drained_bytes", std::to_string(drained_bytes)},
            {"candidate_set_sha256", candidate_set_sha256},
            {"retained_at_epoch", std::to_string(retained_at_epoch)},
            {"operator_id", operator_id},
            {"reason", reason},
        });
    return "sync-peer-transport-ingress-retention-event:v2:" +
           candidate_set_sha256 + ":" + sha256_hex(material);
}

void insert_peer_transport_retention_event_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& event_kind,
    const std::string& state_drained,
    std::uint64_t older_than_epoch,
    std::uint64_t max_rows,
    const PeerTransportRetentionSelection& selection,
    std::uint64_t retained_at_epoch,
    const std::string& operator_id,
    const std::string& reason,
    const std::string& label) {
    verify_selection_or_throw(selection, event_kind, state_drained, label);
    if (selection.rows == 0) return;

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "INSERT INTO sync_peer_transport_ingress_retention_events("
        "session_id, retention_event_idempotency_key, event_kind, state_drained, older_than_epoch, max_rows, "
        "drained_rows, drained_bytes, retained_at_epoch, operator_id, reason) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?);",
        label + " retention event insert prepare");
    int i = 1;
    sqlite_bind_text_or_throw(
        stmt.stmt, i++, session_id, label + " retention event session");
    sqlite_bind_text_or_throw(
        stmt.stmt,
        i++,
        peer_transport_retention_event_idempotency_key(
            session_id,
            event_kind,
            state_drained,
            older_than_epoch,
            max_rows,
            selection.rows,
            selection.bytes,
            selection.candidate_set_sha256,
            retained_at_epoch,
            operator_id,
            reason),
        label + " retention event key");
    sqlite_bind_text_or_throw(
        stmt.stmt, i++, event_kind, label + " retention event kind");
    sqlite_bind_text_or_throw(
        stmt.stmt, i++, state_drained, label + " retention event state");
    sqlite_bind_u64_or_throw(
        stmt.stmt, i++, older_than_epoch, label + " retention event older than");
    sqlite_bind_u64_or_throw(
        stmt.stmt, i++, max_rows, label + " retention event max rows");
    sqlite_bind_u64_or_throw(
        stmt.stmt, i++, selection.rows, label + " retention event drained rows");
    sqlite_bind_u64_or_throw(
        stmt.stmt, i++, selection.bytes, label + " retention event drained bytes");
    sqlite_bind_u64_or_throw(
        stmt.stmt, i++, retained_at_epoch, label + " retention event retained at");
    sqlite_bind_text_or_throw(
        stmt.stmt, i++, operator_id, label + " retention event operator");
    sqlite_bind_text_or_throw(
        stmt.stmt, i++, reason, label + " retention event reason");
    sqlite_step_done_or_throw(stmt.stmt, label + " retention event insert");
    require_exact_change_count_or_throw(db, 1, label + " retention event insert");
}

PeerTransportRetentionSelection
select_verified_peer_transport_terminal_retention_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& session_id,
    const std::string& state,
    std::uint64_t older_than_epoch,
    std::uint64_t max_rows,
    const PeerTransportIngressWireLimits& wire_limits,
    const std::string& label) {
    PeerTransportRetentionSelection out;
    if (older_than_epoch == 0) return out;
    if (state != "completed" && state != "abandoned") {
        throw std::invalid_argument(
            label + " terminal retention state must be completed or abandoned");
    }
    if (wire_limits.max_frame_bytes == 0 || wire_limits.max_chunk_count == 0 ||
        wire_limits.max_metadata_field_bytes == 0) {
        throw std::invalid_argument(
            label + " terminal retention wire limits must be positive");
    }

    // The exact schema is checked once for the snapshot, not once per row.
    const VerifiedPeerTransportIngressPayloadStoreSchema verified_payload_schema =
        verify_and_acquire_peer_transport_ingress_payload_store_schema_or_throw(
            db, transaction, label + " canonical payload schema");

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT transport_envelope_idempotency_key, updated_at_epoch "
        "FROM sync_peer_transport_ingress_envelopes "
        "WHERE session_id=? AND state=? AND updated_at_epoch<=? "
        "ORDER BY updated_at_epoch, transport_envelope_idempotency_key LIMIT ?;",
        label + " terminal retention candidate prepare");
    sqlite_bind_text_or_throw(
        stmt.stmt, 1, session_id, label + " terminal retention session");
    sqlite_bind_text_or_throw(
        stmt.stmt, 2, state, label + " terminal retention state");
    sqlite_bind_u64_or_throw(
        stmt.stmt, 3, older_than_epoch, label + " terminal retention cutoff");
    sqlite_bind_u64_or_throw(
        stmt.stmt,
        4,
        retention_sql_limit(max_rows),
        label + " terminal retention limit");

    while (true) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(db, rc, label + " terminal retention candidate query");
        }
        PeerTransportRetentionCandidate candidate;
        candidate.transport_envelope_idempotency_key = sqlite_column_text_or_throw(
            stmt.stmt, 0, label + " terminal retention candidate key");
        candidate.lifecycle_epoch = sqlite_column_u64_or_throw(
            stmt.stmt, 1, label + " terminal retention candidate updated at");
        if (candidate.transport_envelope_idempotency_key.empty()) {
            throw std::runtime_error(label + " terminal retention candidate key is empty");
        }
        if (candidate.lifecycle_epoch == 0 ||
            candidate.lifecycle_epoch > older_than_epoch) {
            throw std::runtime_error(
                label + " terminal retention candidate epoch escaped the selected cutoff");
        }

        const PeerTransportIngressStoredPayload stored =
            load_peer_transport_ingress_stored_payload_from_verified_schema_or_throw(
                db,
                verified_payload_schema,
                session_id,
                candidate.transport_envelope_idempotency_key,
                wire_limits.max_frame_bytes,
                label + " terminal retention canonical payload");
        if (!stored.found) {
            throw std::runtime_error(
                label + " terminal retention candidate lacks canonical durable payload evidence");
        }

        PeerTransportIngressWirePayload decoded;
        const SyncValidationResult decoded_result =
            decode_peer_transport_ingress_wire_frame(
                wire_limits, stored.canonical_frame, decoded);
        if (!decoded_result.ok) {
            throw std::runtime_error(
                label + " terminal retention canonical frame rejected: " +
                decoded_result.reason);
        }
        if (decoded.transport_envelope.transport_envelope_idempotency_key !=
            candidate.transport_envelope_idempotency_key) {
            throw std::runtime_error(
                label + " terminal retention canonical frame identity differs from candidate key");
        }
        if (decoded.payload_digest != stored.payload_digest) {
            throw std::runtime_error(
                label + " terminal retention canonical frame digest differs from stored digest");
        }

        const persistence::CanonicalIngressProjection canonical =
            canonical_peer_transport_ingress_projection(
                decoded.transport_envelope, decoded.payload_digest);
        const std::optional<PeerTransportIngressRowSnapshot> verified_row =
            load_verified_peer_transport_ingress_row_or_throw(
                db,
                session_id,
                candidate.transport_envelope_idempotency_key,
                canonical,
                label + " terminal retention parent verification");
        if (!verified_row.has_value()) {
            throw std::runtime_error(
                label + " terminal retention candidate disappeared from its read snapshot");
        }
        if (verified_row->state != state) {
            throw std::runtime_error(
                label + " terminal retention candidate state changed inside its read snapshot");
        }

        candidate.logical_bytes = verified_row->canonical().total_bytes;
        candidate.evidence_sha256 = terminal_candidate_evidence_sha256(
            state, stored, verified_row->canonical());
        checked_add_retention_bytes_or_throw(
            out.bytes, candidate.logical_bytes, label);
        out.candidates.push_back(std::move(candidate));
    }

    finalize_selection_or_throw(
        out, "ingress-terminal-drain", state, label);
    return out;
}

PeerTransportRetentionSelection
select_peer_transport_authority_denial_retention_or_throw(
    sqlite3* db,
    const std::string& session_id,
    std::uint64_t older_than_epoch,
    std::uint64_t max_rows,
    const std::string& label) {
    PeerTransportRetentionSelection out;
    if (older_than_epoch == 0) return out;
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT transport_envelope_idempotency_key, peer_id, peer_session_id, "
        "transport_instance_id, transport_key_id, payload_digest, total_bytes, "
        "denied_at_epoch, deny_reason "
        "FROM sync_peer_transport_authority_denials "
        "WHERE session_id=? AND denied_at_epoch<=? "
        "ORDER BY denied_at_epoch, transport_envelope_idempotency_key LIMIT ?;",
        label + " authority denial retention candidate prepare");
    sqlite_bind_text_or_throw(
        stmt.stmt, 1, session_id, label + " authority denial retention session");
    sqlite_bind_u64_or_throw(
        stmt.stmt, 2, older_than_epoch, label + " authority denial retention cutoff");
    sqlite_bind_u64_or_throw(
        stmt.stmt,
        3,
        retention_sql_limit(max_rows),
        label + " authority denial retention limit");
    while (true) {
        const int rc = sqlite3_step(stmt.stmt);
        if (rc == SQLITE_DONE) break;
        if (rc != SQLITE_ROW) {
            throw_sqlite_exception(
                db, rc, label + " authority denial retention candidate query");
        }
        PeerTransportRetentionCandidate candidate;
        candidate.transport_envelope_idempotency_key = sqlite_column_text_or_throw(
            stmt.stmt, 0, label + " authority denial retention candidate key");
        const std::string peer_id = sqlite_column_text_or_throw(
            stmt.stmt, 1, label + " authority denial retention peer id");
        const std::string peer_session_id = sqlite_column_text_or_throw(
            stmt.stmt, 2, label + " authority denial retention peer session id");
        const std::string transport_instance_id = sqlite_column_text_or_throw(
            stmt.stmt, 3, label + " authority denial retention transport instance id");
        const std::string transport_key_id = sqlite_column_text_or_throw(
            stmt.stmt, 4, label + " authority denial retention transport key id");
        const std::string payload_digest = sqlite_column_text_or_throw(
            stmt.stmt, 5, label + " authority denial retention payload digest");
        candidate.logical_bytes = sqlite_column_u64_or_throw(
            stmt.stmt, 6, label + " authority denial retention candidate bytes");
        candidate.lifecycle_epoch = sqlite_column_u64_or_throw(
            stmt.stmt, 7, label + " authority denial retention candidate denied at");
        const std::string deny_reason = sqlite_column_text_or_throw(
            stmt.stmt, 8, label + " authority denial retention deny reason");
        if (candidate.transport_envelope_idempotency_key.empty() || peer_id.empty() ||
            peer_session_id.empty() || transport_instance_id.empty() ||
            transport_key_id.empty() || !is_lowercase_sha256_hex(payload_digest) ||
            candidate.logical_bytes == 0 || candidate.lifecycle_epoch == 0 ||
            candidate.lifecycle_epoch > older_than_epoch || deny_reason.empty()) {
            throw std::runtime_error(
                label + " authority denial retention candidate has invalid durable shape");
        }
        candidate.evidence_sha256 = sha256_hex(length_prefixed_security_tuple(
            "anonsync-sync-peer-transport-authority-denial-retention-candidate-evidence-v1",
            {
                {"session_id", session_id},
                {"transport_envelope_idempotency_key",
                 candidate.transport_envelope_idempotency_key},
                {"peer_id", peer_id},
                {"peer_session_id", peer_session_id},
                {"transport_instance_id", transport_instance_id},
                {"transport_key_id", transport_key_id},
                {"payload_digest", payload_digest},
                {"total_bytes", std::to_string(candidate.logical_bytes)},
                {"denied_at_epoch", std::to_string(candidate.lifecycle_epoch)},
                {"deny_reason", deny_reason},
            }));
        checked_add_retention_bytes_or_throw(
            out.bytes, candidate.logical_bytes, label);
        out.candidates.push_back(std::move(candidate));
    }
    finalize_selection_or_throw(
        out, "authority-denial-drain", "authority-denied", label);
    return out;
}

void delete_exact_peer_transport_terminal_retention_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& state,
    const PeerTransportRetentionSelection& selection,
    const std::string& label) {
    if (state != "completed" && state != "abandoned") {
        throw std::invalid_argument(
            label + " exact terminal retention state must be completed or abandoned");
    }
    verify_selection_or_throw(selection, "ingress-terminal-drain", state, label);
    if (selection.rows == 0) return;

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "DELETE FROM sync_peer_transport_ingress_envelopes "
        "WHERE session_id=? AND transport_envelope_idempotency_key=? "
        "AND state=? AND updated_at_epoch=? AND total_bytes=?;",
        label + " exact terminal retention delete prepare");
    for (std::size_t index = 0; index < selection.candidates.size(); ++index) {
        const PeerTransportRetentionCandidate& candidate = selection.candidates[index];
        sqlite_bind_text_or_throw(
            stmt.stmt, 1, session_id, label + " exact terminal retention session");
        sqlite_bind_text_or_throw(
            stmt.stmt,
            2,
            candidate.transport_envelope_idempotency_key,
            label + " exact terminal retention key");
        sqlite_bind_text_or_throw(
            stmt.stmt, 3, state, label + " exact terminal retention state");
        sqlite_bind_u64_or_throw(
            stmt.stmt,
            4,
            candidate.lifecycle_epoch,
            label + " exact terminal retention updated at");
        sqlite_bind_u64_or_throw(
            stmt.stmt,
            5,
            candidate.logical_bytes,
            label + " exact terminal retention bytes");
        sqlite_step_done_or_throw(stmt.stmt, label + " exact terminal retention delete");
        require_exact_change_count_or_throw(
            db, 1, label + " exact terminal retention delete");
        if (index + 1 < selection.candidates.size()) {
            reset_statement_or_throw(
                db, stmt.stmt, label + " exact terminal retention delete");
        }
    }
}

void delete_exact_peer_transport_authority_denial_retention_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const PeerTransportRetentionSelection& selection,
    const std::string& label) {
    verify_selection_or_throw(
        selection, "authority-denial-drain", "authority-denied", label);
    if (selection.rows == 0) return;

    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "DELETE FROM sync_peer_transport_authority_denials "
        "WHERE session_id=? AND transport_envelope_idempotency_key=? "
        "AND denied_at_epoch=? AND total_bytes=?;",
        label + " exact authority denial retention delete prepare");
    for (std::size_t index = 0; index < selection.candidates.size(); ++index) {
        const PeerTransportRetentionCandidate& candidate = selection.candidates[index];
        sqlite_bind_text_or_throw(
            stmt.stmt, 1, session_id, label + " exact authority denial retention session");
        sqlite_bind_text_or_throw(
            stmt.stmt,
            2,
            candidate.transport_envelope_idempotency_key,
            label + " exact authority denial retention key");
        sqlite_bind_u64_or_throw(
            stmt.stmt,
            3,
            candidate.lifecycle_epoch,
            label + " exact authority denial retention denied at");
        sqlite_bind_u64_or_throw(
            stmt.stmt,
            4,
            candidate.logical_bytes,
            label + " exact authority denial retention bytes");
        sqlite_step_done_or_throw(
            stmt.stmt, label + " exact authority denial retention delete");
        require_exact_change_count_or_throw(
            db, 1, label + " exact authority denial retention delete");
        if (index + 1 < selection.candidates.size()) {
            reset_statement_or_throw(
                db, stmt.stmt, label + " exact authority denial retention delete");
        }
    }
}

}  // namespace anonsync
