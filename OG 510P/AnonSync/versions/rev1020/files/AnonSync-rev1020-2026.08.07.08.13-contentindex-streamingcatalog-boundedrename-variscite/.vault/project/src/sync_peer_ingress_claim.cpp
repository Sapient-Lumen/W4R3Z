#include "sync_peer_ingress_claim.hpp"

#include "anonsync_core_internal.hpp"
#include "sync_sqlite_support.hpp"

#include <stdexcept>
#include <string>

#include <sqlite3.h>

namespace anonsync {
namespace {

constexpr const char* kPeerTransportIngressClaimGenerationDomain =
    "anonsync-sync-peer-transport-ingress-claim-generation-v1";

void validate_claim_generation_tuple_or_throw(
    const PeerTransportIngressClaimGeneration& claim,
    const std::string& label) {
    if (claim.session_id.empty()) throw std::runtime_error(label + " session_id is required");
    if (claim.transport_envelope_idempotency_key.empty()) {
        throw std::runtime_error(label + " transport envelope key is required");
    }
    if (claim.payload_digest.empty()) throw std::runtime_error(label + " payload_digest is required");
    if (claim.attempt == 0) throw std::runtime_error(label + " attempt must be positive");
    if (claim.max_attempts == 0 || claim.attempt > claim.max_attempts) {
        throw std::runtime_error(label + " attempt must not exceed positive max_attempts");
    }
    if (claim.retry_backoff_seconds == 0) {
        throw std::runtime_error(label + " retry_backoff_seconds must be positive");
    }
    if (claim.worker_id.empty()) throw std::runtime_error(label + " worker_id is required");
    if (claim.worker_lease_id.empty()) throw std::runtime_error(label + " worker_lease_id is required");
    if (claim.claimed_at_epoch == 0) throw std::runtime_error(label + " claimed_at_epoch must be positive");
    if (claim.lease_expires_at_epoch < claim.claimed_at_epoch) {
        throw std::runtime_error(label + " lease expiry precedes claim timestamp");
    }
    if (claim.retry_at_epoch < claim.claimed_at_epoch) {
        throw std::runtime_error(label + " retry timestamp precedes claim timestamp");
    }
}

std::string compute_claim_generation_id(
    const PeerTransportIngressClaimGeneration& claim) {
    const std::string digest = sha256_hex(length_prefixed_security_tuple(
        kPeerTransportIngressClaimGenerationDomain,
        {
            {"session_id", claim.session_id},
            {"transport_envelope_idempotency_key", claim.transport_envelope_idempotency_key},
            {"payload_digest", claim.payload_digest},
            {"attempt", std::to_string(claim.attempt)},
            {"max_attempts", std::to_string(claim.max_attempts)},
            {"retry_backoff_seconds", std::to_string(claim.retry_backoff_seconds)},
            {"retry_at_epoch", std::to_string(claim.retry_at_epoch)},
            {"worker_id", claim.worker_id},
            {"worker_lease_id", claim.worker_lease_id},
            {"claimed_at_epoch", std::to_string(claim.claimed_at_epoch)},
            {"lease_expires_at_epoch", std::to_string(claim.lease_expires_at_epoch)},
        }));
    return std::string("sync-peer-transport-ingress-claim:v1:") + digest;
}

void validate_materialized_claim_generation_or_throw(
    const PeerTransportIngressClaimGeneration& claim,
    const std::string& label) {
    validate_claim_generation_tuple_or_throw(claim, label);
    if (claim.generation_id.empty()) {
        throw std::runtime_error(label + " generation_id is required");
    }
    if (claim.generation_id != compute_claim_generation_id(claim)) {
        throw std::runtime_error(label + " generation_id does not match its evidence tuple");
    }
}

std::uint64_t run_claim_transition_probe_or_throw(
    sqlite3* db,
    const PeerTransportIngressClaimGeneration& claim,
    const std::string& next_state,
    const std::string& label) {
    const std::string sql =
        "UPDATE sync_peer_transport_ingress_envelopes SET state=? WHERE " +
        std::string(peer_transport_ingress_exact_claim_predicate_sql()) + ";";
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(db, sql, label + " prepare");
    int i = 1;
    sqlite_bind_text_or_throw(stmt.stmt, i++, next_state, label + " next state");
    bind_peer_transport_ingress_exact_claim_predicate_or_throw(stmt.stmt, i, claim, label);
    sqlite_step_done_or_throw(stmt.stmt, label + " execute");
    return static_cast<std::uint64_t>(sqlite3_changes(db));
}

std::string load_claim_probe_state_or_throw(sqlite3* db) {
    SyncSqliteStmt stmt = sqlite_prepare_or_throw(
        db,
        "SELECT state FROM sync_peer_transport_ingress_envelopes WHERE session_id='session-a';",
        "peer ingress claim generation selftest state prepare");
    const int rc = sqlite3_step(stmt.stmt);
    if (rc != SQLITE_ROW) {
        throw_sqlite_exception(db, rc, "peer ingress claim generation selftest state select");
    }
    return sqlite_column_text_or_throw(stmt.stmt, 0, "peer ingress claim generation selftest state");
}

}  // namespace

PeerTransportIngressClaimGeneration make_peer_transport_ingress_claim_generation_or_throw(
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    const std::string& payload_digest,
    std::uint64_t attempt,
    std::uint64_t max_attempts,
    std::uint64_t retry_backoff_seconds,
    std::uint64_t retry_at_epoch,
    const std::string& worker_id,
    const std::string& worker_lease_id,
    std::uint64_t claimed_at_epoch,
    std::uint64_t lease_expires_at_epoch,
    const std::string& label) {
    PeerTransportIngressClaimGeneration claim;
    claim.session_id = session_id;
    claim.transport_envelope_idempotency_key = transport_envelope_idempotency_key;
    claim.payload_digest = payload_digest;
    claim.attempt = attempt;
    claim.max_attempts = max_attempts;
    claim.retry_backoff_seconds = retry_backoff_seconds;
    claim.retry_at_epoch = retry_at_epoch;
    claim.worker_id = worker_id;
    claim.worker_lease_id = worker_lease_id;
    claim.claimed_at_epoch = claimed_at_epoch;
    claim.lease_expires_at_epoch = lease_expires_at_epoch;
    validate_claim_generation_tuple_or_throw(claim, label);
    claim.generation_id = compute_claim_generation_id(claim);
    return claim;
}

bool same_peer_transport_ingress_claim_generation(
    const PeerTransportIngressClaimGeneration& left,
    const PeerTransportIngressClaimGeneration& right) noexcept {
    return !left.generation_id.empty() &&
           left.generation_id == right.generation_id &&
           left.session_id == right.session_id &&
           left.transport_envelope_idempotency_key == right.transport_envelope_idempotency_key &&
           left.payload_digest == right.payload_digest &&
           left.attempt == right.attempt &&
           left.max_attempts == right.max_attempts &&
           left.retry_backoff_seconds == right.retry_backoff_seconds &&
           left.retry_at_epoch == right.retry_at_epoch &&
           left.worker_id == right.worker_id &&
           left.worker_lease_id == right.worker_lease_id &&
           left.claimed_at_epoch == right.claimed_at_epoch &&
           left.lease_expires_at_epoch == right.lease_expires_at_epoch;
}

std::string peer_transport_ingress_claim_evidence_reason_or_throw(
    const std::string& reason,
    const PeerTransportIngressClaimGeneration& claim,
    const std::string& label) {
    if (reason.empty()) throw std::runtime_error(label + " reason is required");
    validate_materialized_claim_generation_or_throw(claim, label + " claim generation");
    return reason + " [claim_generation_id=" + claim.generation_id + "]";
}

const char* peer_transport_ingress_exact_claim_predicate_sql() noexcept {
    return
        "session_id=? AND transport_envelope_idempotency_key=? AND state='claimed' "
        "AND payload_digest=? AND attempts=? AND max_attempts=? "
        "AND retry_backoff_seconds=? AND retry_at_epoch=? "
        "AND worker_id=? AND worker_lease_id=? "
        "AND claimed_at_epoch=? AND lease_expires_at_epoch=?";
}

void bind_peer_transport_ingress_exact_claim_predicate_or_throw(
    sqlite3_stmt* stmt,
    int& parameter_index,
    const PeerTransportIngressClaimGeneration& claim,
    const std::string& label) {
    validate_materialized_claim_generation_or_throw(claim, label + " claim generation");
    sqlite_bind_text_or_throw(stmt, parameter_index++, claim.session_id, label + " session");
    sqlite_bind_text_or_throw(stmt, parameter_index++, claim.transport_envelope_idempotency_key,
                              label + " transport envelope key");
    sqlite_bind_text_or_throw(stmt, parameter_index++, claim.payload_digest, label + " payload digest");
    sqlite_bind_u64_or_throw(stmt, parameter_index++, claim.attempt, label + " attempt");
    sqlite_bind_u64_or_throw(stmt, parameter_index++, claim.max_attempts, label + " max attempts");
    sqlite_bind_u64_or_throw(stmt, parameter_index++, claim.retry_backoff_seconds,
                             label + " retry backoff");
    sqlite_bind_u64_or_throw(stmt, parameter_index++, claim.retry_at_epoch, label + " retry at");
    sqlite_bind_text_or_throw(stmt, parameter_index++, claim.worker_id, label + " worker");
    sqlite_bind_text_or_throw(stmt, parameter_index++, claim.worker_lease_id, label + " worker lease");
    sqlite_bind_u64_or_throw(stmt, parameter_index++, claim.claimed_at_epoch, label + " claimed at");
    sqlite_bind_u64_or_throw(stmt, parameter_index++, claim.lease_expires_at_epoch,
                             label + " lease expires");
}

void run_peer_transport_ingress_claim_generation_selftests(
    const std::function<void(bool, const std::string&)>& require) {
    const PeerTransportIngressClaimGeneration stale =
        make_peer_transport_ingress_claim_generation_or_throw(
            "session-a",
            "sync-peer-transport-envelope:v1:fixture",
            std::string(64, 'a'),
            1,
            3,
            30,
            160,
            "worker-a",
            "lease-reused",
            100,
            160,
            "peer ingress claim generation selftest stale");
    const PeerTransportIngressClaimGeneration current =
        make_peer_transport_ingress_claim_generation_or_throw(
            "session-a",
            "sync-peer-transport-envelope:v1:fixture",
            std::string(64, 'a'),
            2,
            3,
            30,
            260,
            "worker-a",
            "lease-reused",
            200,
            260,
            "peer ingress claim generation selftest current");
    const PeerTransportIngressClaimGeneration current_again =
        make_peer_transport_ingress_claim_generation_or_throw(
            "session-a",
            "sync-peer-transport-envelope:v1:fixture",
            std::string(64, 'a'),
            2,
            3,
            30,
            260,
            "worker-a",
            "lease-reused",
            200,
            260,
            "peer ingress claim generation selftest current repeat");

    require(stale.worker_id == current.worker_id &&
                stale.worker_lease_id == current.worker_lease_id &&
                stale.generation_id != current.generation_id &&
                !same_peer_transport_ingress_claim_generation(stale, current),
            "peer ingress claim generation distinguishes reused worker and lease tokens");
    require(current.generation_id.starts_with("sync-peer-transport-ingress-claim:v1:") &&
                current.generation_id == current_again.generation_id &&
                same_peer_transport_ingress_claim_generation(current, current_again),
            "peer ingress claim generation identifier is deterministic and domain separated");
    const std::string evidence_reason =
        peer_transport_ingress_claim_evidence_reason_or_throw(
            "completed fixture",
            current,
            "peer ingress claim generation selftest event evidence");
    require(evidence_reason ==
                "completed fixture [claim_generation_id=" + current.generation_id + "]",
            "peer ingress claim generation is preserved in durable event evidence");
    PeerTransportIngressClaimGeneration tampered = current;
    tampered.retry_at_epoch += 1;
    bool tampered_generation_rejected = false;
    try {
        (void)peer_transport_ingress_claim_evidence_reason_or_throw(
            "tampered fixture",
            tampered,
            "peer ingress claim generation selftest tamper rejection");
    } catch (const std::runtime_error&) {
        tampered_generation_rejected = true;
    }
    require(tampered_generation_rejected,
            "peer ingress claim generation rejects an identifier detached from its evidence tuple");

    SyncSqliteDb db;
    const int open_rc = sqlite3_open_v2(
        ":memory:",
        db.db.out(),
        SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE | SQLITE_OPEN_FULLMUTEX,
        nullptr);
    if (open_rc != SQLITE_OK) {
        throw_sqlite_exception(db.db, open_rc, "peer ingress claim generation selftest open");
    }
    sqlite_exec_or_throw(
        db.db,
        "CREATE TABLE sync_peer_transport_ingress_envelopes("
        "session_id TEXT NOT NULL,"
        "transport_envelope_idempotency_key TEXT NOT NULL,"
        "state TEXT NOT NULL,"
        "payload_digest TEXT NOT NULL,"
        "attempts INTEGER NOT NULL,"
        "max_attempts INTEGER NOT NULL,"
        "retry_backoff_seconds INTEGER NOT NULL,"
        "retry_at_epoch INTEGER NOT NULL,"
        "worker_id TEXT NOT NULL,"
        "worker_lease_id TEXT NOT NULL,"
        "claimed_at_epoch INTEGER NOT NULL,"
        "lease_expires_at_epoch INTEGER NOT NULL);",
        "peer ingress claim generation selftest schema");
    SyncSqliteStmt insert = sqlite_prepare_or_throw(
        db.db,
        "INSERT INTO sync_peer_transport_ingress_envelopes VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",
        "peer ingress claim generation selftest insert prepare");
    int i = 1;
    sqlite_bind_text_or_throw(insert.stmt, i++, current.session_id, "claim selftest session");
    sqlite_bind_text_or_throw(insert.stmt, i++, current.transport_envelope_idempotency_key,
                              "claim selftest envelope");
    sqlite_bind_text_or_throw(insert.stmt, i++, "claimed", "claim selftest state");
    sqlite_bind_text_or_throw(insert.stmt, i++, current.payload_digest, "claim selftest payload");
    sqlite_bind_u64_or_throw(insert.stmt, i++, current.attempt, "claim selftest attempt");
    sqlite_bind_u64_or_throw(insert.stmt, i++, current.max_attempts, "claim selftest max attempts");
    sqlite_bind_u64_or_throw(insert.stmt, i++, current.retry_backoff_seconds, "claim selftest retry backoff");
    sqlite_bind_u64_or_throw(insert.stmt, i++, current.retry_at_epoch, "claim selftest retry at");
    sqlite_bind_text_or_throw(insert.stmt, i++, current.worker_id, "claim selftest worker");
    sqlite_bind_text_or_throw(insert.stmt, i++, current.worker_lease_id, "claim selftest lease");
    sqlite_bind_u64_or_throw(insert.stmt, i++, current.claimed_at_epoch, "claim selftest claimed at");
    sqlite_bind_u64_or_throw(insert.stmt, i++, current.lease_expires_at_epoch, "claim selftest lease expires");
    sqlite_step_done_or_throw(insert.stmt, "peer ingress claim generation selftest insert");

    const std::uint64_t stale_changes = run_claim_transition_probe_or_throw(
        db.db, stale, "completed", "peer ingress claim generation selftest stale transition");
    const std::string state_after_stale = load_claim_probe_state_or_throw(db.db);
    const std::uint64_t current_changes = run_claim_transition_probe_or_throw(
        db.db, current, "completed", "peer ingress claim generation selftest current transition");
    const std::string state_after_current = load_claim_probe_state_or_throw(db.db);
    require(stale_changes == 0 && state_after_stale == "claimed" &&
                current_changes == 1 && state_after_current == "completed",
            "peer ingress exact claim CAS rejects stale generation despite reused worker and lease tokens");
}

}  // namespace anonsync
