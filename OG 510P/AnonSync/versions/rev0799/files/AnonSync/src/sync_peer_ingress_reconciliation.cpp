#include "sync_peer_ingress_reconciliation.hpp"

namespace anonsync {

const char* peer_ingress_receipt_evidence_name(PeerIngressReceiptEvidenceKind kind) noexcept {
    switch (kind) {
        case PeerIngressReceiptEvidenceKind::NotInspected: return "not-inspected";
        case PeerIngressReceiptEvidenceKind::MatchingAll: return "matching-all";
        case PeerIngressReceiptEvidenceKind::AuthoritativelyAbsent: return "authoritatively-absent";
        case PeerIngressReceiptEvidenceKind::Partial: return "partial";
        case PeerIngressReceiptEvidenceKind::Conflicting: return "conflicting";
        case PeerIngressReceiptEvidenceKind::Unavailable: return "unavailable";
    }
    return "unavailable";
}

const char* peer_ingress_expired_claim_action_name(PeerIngressExpiredClaimAction action) noexcept {
    switch (action) {
        case PeerIngressExpiredClaimAction::CompleteFromReceipts: return "complete-from-receipts";
        case PeerIngressExpiredClaimAction::RetryAfterAuthoritativeAbsence: return "retry-after-authoritative-absence";
        case PeerIngressExpiredClaimAction::AbandonAfterAuthoritativeAbsence: return "abandon-after-authoritative-absence";
        case PeerIngressExpiredClaimAction::BlockPartialEvidence: return "block-partial-evidence";
        case PeerIngressExpiredClaimAction::BlockConflictingEvidence: return "block-conflicting-evidence";
        case PeerIngressExpiredClaimAction::BlockUnavailableEvidence: return "block-unavailable-evidence";
    }
    return "block-unavailable-evidence";
}

PeerIngressExpiredClaimDecision decide_peer_ingress_expired_claim_recovery(
    const PeerIngressReceiptEvidenceInspection& evidence,
    std::uint64_t attempts,
    std::uint64_t max_attempts) {
    PeerIngressExpiredClaimDecision decision;
    decision.attempt_cap_reached = max_attempts == 0 || attempts >= max_attempts;

    switch (evidence.kind) {
        case PeerIngressReceiptEvidenceKind::MatchingAll:
            decision.action = PeerIngressExpiredClaimAction::CompleteFromReceipts;
            decision.reason = "all expected durable receipts and staged chunk bytes match";
            return decision;
        case PeerIngressReceiptEvidenceKind::AuthoritativelyAbsent:
            decision.action = decision.attempt_cap_reached
                ? PeerIngressExpiredClaimAction::AbandonAfterAuthoritativeAbsence
                : PeerIngressExpiredClaimAction::RetryAfterAuthoritativeAbsence;
            decision.reason = decision.attempt_cap_reached
                ? "attempt cap reached and every expected durable receipt is absent"
                : "every expected durable receipt is absent; another claim may retry acceptance";
            return decision;
        case PeerIngressReceiptEvidenceKind::Partial:
            decision.action = PeerIngressExpiredClaimAction::BlockPartialEvidence;
            decision.operator_review_required = true;
            decision.reason = "some expected durable receipts match while others are absent";
            return decision;
        case PeerIngressReceiptEvidenceKind::Conflicting:
            decision.action = PeerIngressExpiredClaimAction::BlockConflictingEvidence;
            decision.operator_review_required = true;
            decision.reason = evidence.reason.empty()
                ? "durable receipt or staged-byte evidence conflicts with the queued envelope"
                : evidence.reason;
            return decision;
        case PeerIngressReceiptEvidenceKind::Unavailable:
        case PeerIngressReceiptEvidenceKind::NotInspected:
            decision.action = PeerIngressExpiredClaimAction::BlockUnavailableEvidence;
            decision.operator_review_required = true;
            decision.reason = evidence.reason.empty()
                ? "durable receipt evidence could not be inspected"
                : evidence.reason;
            return decision;
    }

    decision.operator_review_required = true;
    decision.reason = "durable receipt evidence produced an unknown recovery classification";
    return decision;
}

}  // namespace anonsync
