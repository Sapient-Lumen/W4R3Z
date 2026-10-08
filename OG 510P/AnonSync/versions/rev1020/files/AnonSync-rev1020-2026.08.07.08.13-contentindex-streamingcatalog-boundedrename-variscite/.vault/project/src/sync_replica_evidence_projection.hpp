#pragma once

#include "sync_replica_model.hpp"

#include <map>
#include <set>
#include <string>

namespace anonsync::detail {

// A pure, arrival-order-independent projection of retained immutable evidence.
// Every map member must already have passed exact-envelope validation at its
// admission or restore boundary. Callers may temporarily insert one validated
// envelope, compute this value, and roll the insertion back on any exception;
// derived indexes are published only after projection succeeds.
struct SyncReplicaEvidenceProjection final {
    // Immutable operation payloads remain owned exactly once by the evidence
    // store. Projection indexes active IDs rather than cloning every envelope.
    std::set<std::string> active_operation_ids;
    std::map<std::string, SyncReplicaEvidenceState> state_by_id;
    std::set<std::string> causal_head_operation_ids;
};

[[nodiscard]] SyncReplicaEvidenceProjection
project_sync_replica_evidence_or_throw(
    const std::map<std::string, SyncReplicaOperation>& evidence_by_id,
    const std::string& folder_id,
    const SyncReplicaModelLimits& limits);

}  // namespace anonsync::detail
