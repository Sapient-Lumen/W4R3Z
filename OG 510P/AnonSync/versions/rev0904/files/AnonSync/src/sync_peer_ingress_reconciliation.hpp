#pragma once

#include "anonsync_core.hpp"

#include <cstdint>
#include <string>
#include <vector>

namespace anonsync {

enum class PeerIngressReceiptEvidenceKind {
    NotInspected,
    MatchingAll,
    AuthoritativelyAbsent,
    Partial,
    Conflicting,
    Unavailable
};

struct PeerIngressReceiptEvidenceInspection {
    PeerIngressReceiptEvidenceKind kind = PeerIngressReceiptEvidenceKind::NotInspected;
    bool transport_evidence_checked = false;
    bool peer_batch_evidence_checked = false;
    std::uint64_t expected_receipts = 0;
    std::uint64_t matching_receipts = 0;
    std::uint64_t missing_receipts = 0;
    std::uint64_t conflicting_receipts = 0;
    std::string reason;
};

enum class PeerIngressExpiredClaimAction {
    CompleteFromReceipts,
    RetryAfterAuthoritativeAbsence,
    AbandonAfterAuthoritativeAbsence,
    BlockPartialEvidence,
    BlockConflictingEvidence,
    BlockUnavailableEvidence
};

struct PeerIngressExpiredClaimDecision {
    PeerIngressExpiredClaimAction action = PeerIngressExpiredClaimAction::BlockUnavailableEvidence;
    bool attempt_cap_reached = false;
    bool operator_review_required = false;
    std::string reason;
};

const char* peer_ingress_receipt_evidence_name(PeerIngressReceiptEvidenceKind kind) noexcept;
const char* peer_ingress_expired_claim_action_name(PeerIngressExpiredClaimAction action) noexcept;
PeerIngressExpiredClaimDecision decide_peer_ingress_expired_claim_recovery(
    const PeerIngressReceiptEvidenceInspection& evidence,
    std::uint64_t attempts,
    std::uint64_t max_attempts);

// Read-only evidence probe implemented beside the receipt serialization and
// path derivation in sync_domain.cpp. It deliberately performs no SQLite work
// and no filesystem mutation.
SyncValidationResult inspect_sync_peer_transport_ingress_receipt_evidence(
    const SyncPeerTransportEnvelopeVerifyOptions& transport_options,
    std::uint64_t original_claimed_at_epoch,
    const SyncManifestEntry& remote_file_entry,
    const SyncLocalApplyPlanEntry& apply_entry,
    const SyncChunkRequestPlanResult& request_plan,
    const SyncPeerChunkScheduleResult& peer_schedule,
    const SyncPeerChunkAssignment& peer_assignment,
    const SyncPeerTransportBoundChunkResponseBatchEnvelope& transport_envelope,
    const std::vector<std::string>& chunk_bytes,
    const SyncChunkReceiptWriteOptions& write_options,
    PeerIngressReceiptEvidenceInspection& out);

}  // namespace anonsync
