#pragma once

#include "sync_replica_delivery_channel.hpp"
#include "sync_replica_delivery_protocol.hpp"
#include "sync_replica_sqlite_owner.hpp"

#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

struct SyncReplicaDeliveryServiceLimits final {
    // Wire-envelope validation is deliberately independent of the receiver's
    // mutable aggregate retention policy. A valid bounded operation must be
    // decoded before the owner can classify it as admissible, duplicate,
    // capacity-blocked, or policy-invalid.
    SyncReplicaModelLimits wire_operation_limits;
    std::uint64_t max_request_frame_bytes =
        kSyncReplicaDeliveryDefaultMaxRequestFrameBytes;
    std::uint64_t max_receipt_frame_bytes =
        kSyncReplicaDeliveryDefaultMaxReceiptFrameBytes;

    bool operator==(const SyncReplicaDeliveryServiceLimits&) const = default;
};

struct SyncReplicaOutboundDelivery final {
    SyncReplicaSqliteOutboxClaim claim;
    SyncReplicaDeliveryRequest request;
    std::string request_frame;
    std::string request_digest;

    bool operator==(const SyncReplicaOutboundDelivery&) const = default;
};

struct SyncReplicaInboundDelivery final {
    SyncReplicaDeliveryRequest request;
    SyncReplicaAdmission admission = SyncReplicaAdmission::CapacityBlocked;
    SyncReplicaDeliveryReceipt receipt;
    std::string receipt_frame;
    std::string receipt_digest;

    bool operator==(const SyncReplicaInboundDelivery&) const = default;
};

// Canonical request construction shared by the evidence-only and file-effect
// services.  A claimed row is descriptive data until this function binds it to
// the exact local actor and authenticated peer/channel context.  Callers may
// additionally require one value kind; this is a local service capability
// filter and does not alter canonical operation identity.
[[nodiscard]] SyncReplicaDeliveryRequest
make_sync_replica_delivery_request_from_claim_or_throw(
    const SyncReplicaSqliteOutboxClaim& claim,
    const SyncReplicaActor& local_actor,
    const SyncReplicaDeliveryChannelContext& channel,
    std::optional<SyncReplicaValueKind> required_kind,
    const std::string& label);

enum class SyncReplicaDeliveryReceiptApplyResult {
    EvidenceSettled,
    ReceiverCapacityBlocked,
    IntentMissing,
    StaleClaim,
    ExpiredClaim,
};

// First non-test orchestration boundary for the causal SQLite owner. It owns no
// socket and no cryptographic session: an authenticated TLS/Noise adapter mints
// one live channel authority and moves the canonical request/receipt bytes.
// Receiver evidence admission is durable before an evidence-terminal receipt is
// returned. This service does not transfer payload bytes or attest a filesystem
// effect. Sender settlement requires that exact in-memory request, so a process
// crash loses the response and deliberately falls back to lease expiry plus
// idempotent evidence retry.
class SyncReplicaDeliveryService final {
public:
    SyncReplicaDeliveryService(
        SyncReplicaSqliteOwner& owner,
        SyncReplicaDeliveryServiceLimits limits = {},
        std::string label = "sync replica delivery service");

    SyncReplicaDeliveryService(const SyncReplicaDeliveryService&) = delete;
    SyncReplicaDeliveryService& operator=(
        const SyncReplicaDeliveryService&) = delete;
    SyncReplicaDeliveryService(SyncReplicaDeliveryService&&) = delete;
    SyncReplicaDeliveryService& operator=(SyncReplicaDeliveryService&&) =
        delete;

    [[nodiscard]] const std::string& folder_id() const noexcept {
        return folder_id_;
    }

    [[nodiscard]] const SyncReplicaActor& local_actor() const noexcept {
        return local_actor_;
    }

    // A successful claim is already durable when request encoding begins. If a
    // later allocation/encoding failure occurs, the lease remains authoritative
    // and can be explicitly released or naturally expire; no second worker may
    // race the same attempt merely because transport preparation failed.
    [[nodiscard]] std::optional<SyncReplicaOutboundDelivery>
    claim_next_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string worker_id,
        std::uint64_t lease_seconds);

    // Decodes and channel-binds before touching receiver state. Evidence-
    // terminal receipts use the generation and cutpoint captured by the same
    // SQLite transaction that durably decided admission.
    [[nodiscard]] SyncReplicaInboundDelivery receive_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string_view request_frame);

    // The expected request is deliberately required. The service never treats
    // receipt fields as permission to reconstruct a different channel-bound
    // attempt after restart. CapacityBlocked is nonterminal and leaves the
    // sender intent/claim untouched for explicit retry policy.
    [[nodiscard]] SyncReplicaDeliveryReceiptApplyResult
    apply_receipt_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const SyncReplicaDeliveryRequest& expected_request,
        std::string_view receipt_frame);

private:
    [[nodiscard]] SyncReplicaSqliteSnapshot snapshot_or_throw(
        const std::string& operation_label);

    void validate_channel_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const std::string& operation_label) const;

    SyncReplicaSqliteOwner& owner_;
    SyncReplicaDeliveryProtocolLimits protocol_limits_;
    std::string label_;
    std::string folder_id_;
    SyncReplicaActor local_actor_;
};

}  // namespace anonsync
