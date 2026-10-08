#pragma once

#include <array>
#include <string_view>

namespace anonsync {

struct PeerTransportIngressSchemaSqlObject final {
    std::string_view type;
    std::string_view name;
    std::string_view table_name;
    std::string_view ddl;
};

// The order is creation order, not comparison order.  Every statement is
// deliberately free of IF NOT EXISTS: atomic bootstrap must fail rather than
// silently accepting a pre-existing look-alike object.
inline constexpr std::array<PeerTransportIngressSchemaSqlObject, 11>
    kPeerTransportIngressSchemaSqlObjects{{
        {
            "table",
            "sync_peer_transport_ingress_envelopes",
            "sync_peer_transport_ingress_envelopes",
            "CREATE TABLE sync_peer_transport_ingress_envelopes ("
            "session_id TEXT NOT NULL,"
            "transport_envelope_idempotency_key TEXT NOT NULL,"
            "transport_instance_id TEXT NOT NULL,"
            "transport_key_id TEXT NOT NULL,"
            "peer_id TEXT NOT NULL,"
            "peer_session_id TEXT NOT NULL,"
            "peer_response_batch_idempotency_key TEXT NOT NULL,"
            "path TEXT NOT NULL,"
            "payload_digest TEXT NOT NULL,"
            "response_count INTEGER NOT NULL CHECK(response_count > 0),"
            "total_bytes INTEGER NOT NULL CHECK(total_bytes > 0),"
            "issued_at_epoch INTEGER NOT NULL CHECK(issued_at_epoch > 0),"
            "expires_at_epoch INTEGER NOT NULL CHECK(expires_at_epoch > issued_at_epoch),"
            "enqueued_at_epoch INTEGER NOT NULL CHECK(enqueued_at_epoch > 0),"
            "updated_at_epoch INTEGER NOT NULL CHECK(updated_at_epoch > 0),"
            "state TEXT NOT NULL CHECK(state IN ('queued','claimed','completed','failed','abandoned')),"
            "attempts INTEGER NOT NULL CHECK(attempts >= 0),"
            "max_attempts INTEGER NOT NULL CHECK(max_attempts > 0),"
            "retry_backoff_seconds INTEGER NOT NULL CHECK(retry_backoff_seconds > 0),"
            "retry_at_epoch INTEGER NOT NULL CHECK(retry_at_epoch >= 0),"
            "worker_id TEXT NOT NULL,"
            "worker_lease_id TEXT NOT NULL,"
            "claimed_at_epoch INTEGER NOT NULL CHECK(claimed_at_epoch >= 0),"
            "lease_expires_at_epoch INTEGER NOT NULL CHECK(lease_expires_at_epoch >= claimed_at_epoch),"
            "last_failure_reason TEXT NOT NULL,"
            "completed_at_epoch INTEGER NOT NULL CHECK(completed_at_epoch >= 0),"
            "PRIMARY KEY(session_id, transport_envelope_idempotency_key)"
            ")"
        },
        {
            "index",
            "idx_sync_peer_transport_ingress_state",
            "sync_peer_transport_ingress_envelopes",
            "CREATE INDEX idx_sync_peer_transport_ingress_state "
            "ON sync_peer_transport_ingress_envelopes(session_id, state, retry_at_epoch, lease_expires_at_epoch)"
        },
        {
            "table",
            "sync_peer_transport_ingress_events",
            "sync_peer_transport_ingress_events",
            "CREATE TABLE sync_peer_transport_ingress_events ("
            "session_id TEXT NOT NULL,"
            "transport_envelope_idempotency_key TEXT NOT NULL,"
            "event_idempotency_key TEXT NOT NULL,"
            "event_kind TEXT NOT NULL CHECK(event_kind IN ('enqueued','claim','completed','failed','abandoned','duplicate')),"
            "state_after TEXT NOT NULL,"
            "observed_at_epoch INTEGER NOT NULL CHECK(observed_at_epoch > 0),"
            "attempt INTEGER NOT NULL CHECK(attempt >= 0),"
            "reason TEXT NOT NULL,"
            "PRIMARY KEY(session_id, event_idempotency_key)"
            ")"
        },
        {
            "table",
            "sync_peer_transport_authority_records",
            "sync_peer_transport_authority_records",
            "CREATE TABLE sync_peer_transport_authority_records ("
            "session_id TEXT NOT NULL,"
            "peer_id TEXT NOT NULL,"
            "peer_session_id TEXT NOT NULL,"
            "transport_instance_id TEXT NOT NULL,"
            "transport_key_id TEXT NOT NULL,"
            "authority_status TEXT NOT NULL CHECK(authority_status IN ('trusted','disabled','revoked')),"
            "valid_from_epoch INTEGER NOT NULL CHECK(valid_from_epoch > 0),"
            "valid_until_epoch INTEGER NOT NULL CHECK(valid_until_epoch >= 0),"
            "updated_at_epoch INTEGER NOT NULL CHECK(updated_at_epoch > 0),"
            "reason TEXT NOT NULL,"
            "PRIMARY KEY(session_id, peer_id, peer_session_id, transport_instance_id, transport_key_id)"
            ")"
        },
        {
            "index",
            "idx_sync_peer_transport_authority_records_status",
            "sync_peer_transport_authority_records",
            "CREATE INDEX idx_sync_peer_transport_authority_records_status "
            "ON sync_peer_transport_authority_records(session_id, authority_status, updated_at_epoch)"
        },
        {
            "table",
            "sync_peer_transport_authority_supersessions",
            "sync_peer_transport_authority_supersessions",
            "CREATE TABLE sync_peer_transport_authority_supersessions ("
            "session_id TEXT NOT NULL,"
            "peer_id TEXT NOT NULL,"
            "peer_session_id TEXT NOT NULL,"
            "transport_instance_id TEXT NOT NULL,"
            "old_transport_key_id TEXT NOT NULL,"
            "replacement_transport_key_id TEXT NOT NULL,"
            "overlap_valid_from_epoch INTEGER NOT NULL CHECK(overlap_valid_from_epoch > 0),"
            "overlap_valid_until_epoch INTEGER NOT NULL CHECK(overlap_valid_until_epoch >= overlap_valid_from_epoch),"
            "updated_at_epoch INTEGER NOT NULL CHECK(updated_at_epoch > 0),"
            "reason TEXT NOT NULL,"
            "PRIMARY KEY(session_id, peer_id, peer_session_id, transport_instance_id, old_transport_key_id)"
            ")"
        },
        {
            "index",
            "idx_sync_peer_transport_authority_supersessions_replacement",
            "sync_peer_transport_authority_supersessions",
            "CREATE INDEX idx_sync_peer_transport_authority_supersessions_replacement "
            "ON sync_peer_transport_authority_supersessions(session_id, peer_id, peer_session_id, transport_instance_id, replacement_transport_key_id)"
        },
        {
            "table",
            "sync_peer_transport_authority_denials",
            "sync_peer_transport_authority_denials",
            "CREATE TABLE sync_peer_transport_authority_denials ("
            "session_id TEXT NOT NULL,"
            "transport_envelope_idempotency_key TEXT NOT NULL,"
            "peer_id TEXT NOT NULL,"
            "peer_session_id TEXT NOT NULL,"
            "transport_instance_id TEXT NOT NULL,"
            "transport_key_id TEXT NOT NULL,"
            "payload_digest TEXT NOT NULL,"
            "total_bytes INTEGER NOT NULL CHECK(total_bytes > 0),"
            "denied_at_epoch INTEGER NOT NULL CHECK(denied_at_epoch > 0),"
            "deny_reason TEXT NOT NULL,"
            "PRIMARY KEY(session_id, transport_envelope_idempotency_key)"
            ")"
        },
        {
            "table",
            "sync_peer_transport_ingress_retention_events",
            "sync_peer_transport_ingress_retention_events",
            "CREATE TABLE sync_peer_transport_ingress_retention_events ("
            "session_id TEXT NOT NULL,"
            "retention_event_idempotency_key TEXT NOT NULL,"
            "event_kind TEXT NOT NULL CHECK(event_kind IN ('ingress-terminal-drain','authority-denial-drain')),"
            "state_drained TEXT NOT NULL,"
            "older_than_epoch INTEGER NOT NULL CHECK(older_than_epoch > 0),"
            "max_rows INTEGER NOT NULL CHECK(max_rows >= 0),"
            "drained_rows INTEGER NOT NULL CHECK(drained_rows >= 0),"
            "drained_bytes INTEGER NOT NULL CHECK(drained_bytes >= 0),"
            "retained_at_epoch INTEGER NOT NULL CHECK(retained_at_epoch > 0),"
            "operator_id TEXT NOT NULL,"
            "reason TEXT NOT NULL,"
            "PRIMARY KEY(session_id, retention_event_idempotency_key)"
            ")"
        },
        {
            "table",
            "sync_peer_transport_ingress_payloads",
            "sync_peer_transport_ingress_payloads",
            "CREATE TABLE sync_peer_transport_ingress_payloads ("
            "session_id TEXT NOT NULL,"
            "transport_envelope_idempotency_key TEXT NOT NULL,"
            "codec_version INTEGER NOT NULL CHECK(codec_version > 0),"
            "canonical_frame_sha256 TEXT NOT NULL CHECK(length(canonical_frame_sha256) = 64),"
            "payload_digest TEXT NOT NULL CHECK(length(payload_digest) = 64),"
            "canonical_frame_bytes INTEGER NOT NULL CHECK(canonical_frame_bytes > 0),"
            "canonical_frame BLOB NOT NULL CHECK(typeof(canonical_frame) = 'blob'),"
            "stored_at_epoch INTEGER NOT NULL CHECK(stored_at_epoch > 0),"
            "PRIMARY KEY(session_id, transport_envelope_idempotency_key),"
            "FOREIGN KEY(session_id, transport_envelope_idempotency_key) REFERENCES "
            "sync_peer_transport_ingress_envelopes(session_id, transport_envelope_idempotency_key) "
            "ON UPDATE RESTRICT ON DELETE CASCADE,"
            "CHECK(canonical_frame_bytes = length(canonical_frame))"
            ")"
        },
        {
            "index",
            "idx_sync_peer_transport_ingress_payload_digest",
            "sync_peer_transport_ingress_payloads",
            "CREATE INDEX idx_sync_peer_transport_ingress_payload_digest "
            "ON sync_peer_transport_ingress_payloads(session_id, payload_digest)"
        }
    }};

}  // namespace anonsync
