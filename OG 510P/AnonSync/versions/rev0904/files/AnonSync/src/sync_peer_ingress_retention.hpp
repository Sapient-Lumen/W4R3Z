#pragma once

#include "sync_peer_ingress_wire.hpp"
#include "sync_sqlite_support.hpp"

#include <cstdint>
#include <string>
#include <vector>

struct sqlite3;

namespace anonsync {

// A retention candidate is selected and later deleted by the same exact
// identity inside one SQLite snapshot/transaction.  We never re-run a broad
// LIMIT predicate after publishing audit evidence.
struct PeerTransportRetentionCandidate {
    std::string transport_envelope_idempotency_key;
    std::uint64_t lifecycle_epoch = 0;
    std::uint64_t logical_bytes = 0;
    // Value-free commitment to the exact canonical/denial evidence deleted by
    // this item. The retention event commits to the ordered item set.
    std::string evidence_sha256;
};

struct PeerTransportRetentionSelection {
    std::uint64_t rows = 0;
    std::uint64_t bytes = 0;
    std::string candidate_set_sha256;
    std::vector<PeerTransportRetentionCandidate> candidates;
};

[[nodiscard]] std::string peer_transport_retention_event_idempotency_key(
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
    const std::string& reason);

// Plain INSERT plus an exact change-count check is deliberate.  A preexisting
// event with live candidate rows is contradictory durable history, not an
// idempotent success that may be silently ignored.
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
    const std::string& label);

// Destructive terminal retention derives byte accounting from the canonical
// frame and verifies every redundant parent projection before it may become a
// candidate.  Only selected terminal rows are decoded; ordinary enqueue does
// not pay a full-database scan cost.
[[nodiscard]] PeerTransportRetentionSelection
select_verified_peer_transport_terminal_retention_or_throw(
    sqlite3* db,
    const SyncSqliteTransaction& transaction,
    const std::string& session_id,
    const std::string& state,
    std::uint64_t older_than_epoch,
    std::uint64_t max_rows,
    const PeerTransportIngressWireLimits& wire_limits,
    const std::string& label);

[[nodiscard]] PeerTransportRetentionSelection
select_peer_transport_authority_denial_retention_or_throw(
    sqlite3* db,
    const std::string& session_id,
    std::uint64_t older_than_epoch,
    std::uint64_t max_rows,
    const std::string& label);

void delete_exact_peer_transport_terminal_retention_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& state,
    const PeerTransportRetentionSelection& selection,
    const std::string& label);

void delete_exact_peer_transport_authority_denial_retention_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const PeerTransportRetentionSelection& selection,
    const std::string& label);

}  // namespace anonsync
