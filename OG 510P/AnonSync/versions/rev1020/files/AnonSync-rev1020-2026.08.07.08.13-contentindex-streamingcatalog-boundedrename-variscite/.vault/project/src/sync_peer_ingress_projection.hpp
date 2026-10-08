#pragma once

#include "anonsync_core.hpp"
#include "persistence/canonical_projection_verifier.hpp"

#include <cstdint>
#include <optional>
#include <string>
#include <utility>

struct sqlite3;

namespace anonsync {

// A queue row can be constructed only from a VerifiedIngressProjection.  The
// mutable lifecycle fields remain ordinary local state; every field duplicated
// from canonical frame evidence is reachable only through canonical().
class PeerTransportIngressRowSnapshot final {
private:
    persistence::VerifiedIngressProjection verified_projection_;

public:
    PeerTransportIngressRowSnapshot(
        persistence::VerifiedIngressProjection verified_projection,
        std::string state_value,
        std::uint64_t attempts_value,
        std::uint64_t max_attempts_value,
        std::uint64_t retry_backoff_seconds_value,
        std::uint64_t retry_at_epoch_value,
        std::string worker_id_value,
        std::string worker_lease_id_value,
        std::uint64_t claimed_at_epoch_value,
        std::uint64_t lease_expires_at_epoch_value)
        : verified_projection_(std::move(verified_projection)),
          state(std::move(state_value)),
          attempts(attempts_value),
          max_attempts(max_attempts_value),
          retry_backoff_seconds(retry_backoff_seconds_value),
          retry_at_epoch(retry_at_epoch_value),
          worker_id(std::move(worker_id_value)),
          worker_lease_id(std::move(worker_lease_id_value)),
          claimed_at_epoch(claimed_at_epoch_value),
          lease_expires_at_epoch(lease_expires_at_epoch_value) {}

    [[nodiscard]] const persistence::CanonicalIngressProjection& canonical() const noexcept {
        return verified_projection_.canonical();
    }

    [[nodiscard]] const std::string& payload_digest() const noexcept {
        return canonical().payload_digest_sha256;
    }

    std::string state;
    std::uint64_t attempts{};
    std::uint64_t max_attempts{};
    std::uint64_t retry_backoff_seconds{};
    std::uint64_t retry_at_epoch{};
    std::string worker_id;
    std::string worker_lease_id;
    std::uint64_t claimed_at_epoch{};
    std::uint64_t lease_expires_at_epoch{};

};

[[nodiscard]] persistence::CanonicalIngressProjection
canonical_peer_transport_ingress_projection(
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::string& payload_digest_sha256);

// Existence is intentionally separate from projection use.  It is used only
// to preserve precise missing-row diagnostics before canonical payload bytes
// have been decoded; no queue metadata is returned by this probe.
[[nodiscard]] bool peer_transport_ingress_row_exists_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    const std::string& label);

// The only parent-row loader exposed to lifecycle code.  It strictly decodes
// all redundant SQLite fields, compares them as one set with canonical frame
// evidence, and returns no ambient/raw row object.
[[nodiscard]] std::optional<PeerTransportIngressRowSnapshot>
load_verified_peer_transport_ingress_row_or_throw(
    sqlite3* db,
    const std::string& session_id,
    const std::string& transport_envelope_idempotency_key,
    const persistence::CanonicalIngressProjection& canonical,
    const std::string& label);

}  // namespace anonsync
