#pragma once

#include <cstdint>
#include <functional>
#include <string>

struct sqlite3_stmt;

namespace anonsync {

// Exact identity of one durable peer-ingress claim generation.  Worker and
// lease identifiers are intentionally insufficient: callers must also bind the
// payload, monotonic attempt, policy snapshot, and lease timestamps that were
// committed by the claim transaction.
struct PeerTransportIngressClaimGeneration {
    std::string generation_id;
    std::string session_id;
    std::string transport_envelope_idempotency_key;
    std::string payload_digest;
    std::uint64_t attempt = 0;
    std::uint64_t max_attempts = 0;
    std::uint64_t retry_backoff_seconds = 0;
    std::uint64_t retry_at_epoch = 0;
    std::string worker_id;
    std::string worker_lease_id;
    std::uint64_t claimed_at_epoch = 0;
    std::uint64_t lease_expires_at_epoch = 0;
};

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
    const std::string& label);

bool same_peer_transport_ingress_claim_generation(
    const PeerTransportIngressClaimGeneration& left,
    const PeerTransportIngressClaimGeneration& right) noexcept;

// Carries the exact generation into the append-only ingress event stream so
// terminal row rewrites do not erase which claim authorized the transition.
std::string peer_transport_ingress_claim_evidence_reason_or_throw(
    const std::string& reason,
    const PeerTransportIngressClaimGeneration& claim,
    const std::string& label);

// SQL fragment and binder are deliberately paired.  Any terminal/recovery
// mutation of a claimed ingress row must use both rather than spelling a
// partial ownership tuple at the call site.
const char* peer_transport_ingress_exact_claim_predicate_sql() noexcept;
void bind_peer_transport_ingress_exact_claim_predicate_or_throw(
    sqlite3_stmt* stmt,
    int& parameter_index,
    const PeerTransportIngressClaimGeneration& claim,
    const std::string& label);

void run_peer_transport_ingress_claim_generation_selftests(
    const std::function<void(bool, const std::string&)>& require);

}  // namespace anonsync
