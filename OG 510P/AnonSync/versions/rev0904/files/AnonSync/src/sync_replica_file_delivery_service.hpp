#pragma once

#include "sync_replica_delivery_service.hpp"
#include "sync_replica_file_delivery_protocol.hpp"
#include "sync_replica_file_effect_sqlite_owner.hpp"
#include "sync_replica_file_payload_snapshot.hpp"
#include "sync_replica_file_payload_store.hpp"

#include <cstdint>
#include <exception>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

class SyncReplicaFileDeliveryService;
class SyncReplicaFileTlsDispatchContinuation;
class SyncReplicaTlsAuthenticatedChannel;

struct SyncReplicaFileDeliveryRetryPolicy final {
    // Local policy owns retry timing. Receiver receipts classify durable state
    // but never supply an absolute or relative sender deadline.
    std::uint64_t pre_dispatch_failure_delay_seconds = 1U;
    std::uint64_t effect_capacity_blocked_delay_seconds = 30U;
    std::uint64_t effect_path_blocked_delay_seconds = 60U * 60U;
    std::uint64_t evidence_capacity_blocked_delay_seconds = 30U;
    std::uint64_t evidence_pending_delay_seconds = 1U;
    std::uint64_t evidence_quarantined_delay_seconds = 60U * 60U;
    std::uint64_t projection_blocked_delay_seconds = 1U;
    std::uint64_t destination_conflict_delay_seconds = 60U * 60U;

    bool operator==(const SyncReplicaFileDeliveryRetryPolicy&) const = default;
};

struct SyncReplicaFileDeliveryServiceLimits final {
    SyncReplicaDeliveryServiceLimits evidence;
    SyncReplicaFileDeliveryRetryPolicy retry;
    std::uint64_t max_payload_bytes =
        kSyncReplicaFileDeliveryDefaultMaxPayloadBytes;
    std::uint64_t max_request_frame_bytes =
        kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes;
    std::uint64_t max_receipt_frame_bytes =
        kSyncReplicaFileDeliveryDefaultMaxReceiptFrameBytes;

    bool operator==(const SyncReplicaFileDeliveryServiceLimits&) const =
        default;
};

struct SyncReplicaOutboundFileDelivery final {
    SyncReplicaSqliteOutboxClaim claim;
    SyncReplicaFileDeliveryRequest request;
    std::string request_frame;
    std::string request_digest;

    bool operator==(const SyncReplicaOutboundFileDelivery&) const = default;
};

// Explicit composition seam implemented by sync_replica_file_tls_dispatch.
// The file service remains transport-neutral; these functions are the only
// friends allowed to combine its durable claim owner with a live TLS stream.
[[nodiscard]] SyncReplicaFileTlsDispatchContinuation
begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    const SyncReplicaOutboundFileDelivery& outbound,
    const std::string& label);

void dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    const SyncReplicaOutboundFileDelivery& outbound,
    const std::string& label);

[[nodiscard]] std::optional<SyncReplicaOutboundFileDelivery>
claim_and_dispatch_next_file_delivery_over_tls_or_throw(
    SyncReplicaFileDeliveryService& service,
    const SyncReplicaTlsAuthenticatedChannel& channel,
    std::string worker_id,
    std::uint64_t lease_seconds,
    SyncReplicaFilePayloadSnapshot payload_snapshot,
    const std::string& label);

struct SyncReplicaInboundFileDelivery final {
    SyncReplicaFileDeliveryRequest request;
    SyncReplicaFileEffectStageResult stage_result =
        SyncReplicaFileEffectStageResult::CapacityBlocked;
    // Receiver-local exact accounting for a capacity rejection. The wire
    // receipt remains a bounded generic classification and cannot select or
    // amplify local retry timing through these diagnostics.
    std::optional<SyncReplicaFileEffectCapacityBlock> capacity_block;
    std::optional<SyncReplicaInboundDelivery> evidence_delivery;
    std::optional<SyncReplicaFileEffectMaterializeResult>
        materialize_result;
    SyncReplicaFileDeliveryReceipt receipt;
    std::string receipt_frame;
    std::string receipt_digest;

    bool operator==(const SyncReplicaInboundFileDelivery&) const = default;
};

enum class SyncReplicaFileDeliveryReceiptApplyResult {
    EffectSettled,
    ReceiverEffectCapacityBlocked,
    ReceiverEffectPathBlocked,
    ReceiverEvidenceCapacityBlocked,
    ReceiverEvidencePending,
    ReceiverEvidenceQuarantined,
    ReceiverProjectionBlocked,
    ReceiverDestinationConflict,
    IntentMissing,
    StaleClaim,
    ExpiredClaim,
};

// Composition owner for one file-only delivery slice. Every entry requires
// the same opaque live channel authority used by the evidence service; public
// descriptive context can never authorize staging, publication, or settlement.
// The sender claims only File operations after preflighting both canonical wire
// limits and the committed payload size, then resolves exact bytes from an
// immutable content-addressed snapshot that was fully owned, hashed, and bounded
// before the durable lease was minted. Its canonical digest inventory constrains
// selection inside the same SQLite claim transaction, so an unavailable earlier
// payload consumes no claim/retry authority and cannot hide a later available
// intent behind claim-release churn. The sender then re-attests the exact live
// claim and owned clock under a scope-bound SQLite writer capability and performs
// only bounded local validation/encoding before commit. The returned frame is not
// itself a network-send authority: a transport
// that can delay first-byte dispatch must re-attest at that later frontier.
//
// The receiver stages payload bytes in a separate SQLite owner before causal
// admission, then materializes only an unambiguous active primary. A sender
// outbox intent is retired only by Published/AlreadyPublished receipts. Every
// validated nonterminal receipt and every local pre-dispatch failure releases
// the exact live claim into a bounded, owner-clock-derived retry schedule;
// neither path waits out an otherwise idle lease or trusts receiver-selected
// timing.
class SyncReplicaFileDeliveryService final {
public:
    SyncReplicaFileDeliveryService(
        SyncReplicaSqliteOwner& replica_owner,
        SyncReplicaFileEffectSqliteOwner* receiver_effect_owner,
        SyncReplicaFileDeliveryServiceLimits limits = {},
        std::string label = "sync replica file delivery service");

    SyncReplicaFileDeliveryService(
        const SyncReplicaFileDeliveryService&) = delete;
    SyncReplicaFileDeliveryService& operator=(
        const SyncReplicaFileDeliveryService&) = delete;
    SyncReplicaFileDeliveryService(
        SyncReplicaFileDeliveryService&&) = delete;
    SyncReplicaFileDeliveryService& operator=(
        SyncReplicaFileDeliveryService&&) = delete;

    [[nodiscard]] const std::string& folder_id() const noexcept {
        return folder_id_;
    }
    [[nodiscard]] const SyncReplicaActor& local_actor() const noexcept {
        return local_actor_;
    }

    [[nodiscard]] std::uint64_t max_request_frame_bytes() const noexcept {
        return protocol_limits_.max_request_frame_bytes;
    }
    [[nodiscard]] std::uint64_t max_receipt_frame_bytes() const noexcept {
        return protocol_limits_.max_receipt_frame_bytes;
    }

    [[nodiscard]] std::optional<SyncReplicaOutboundFileDelivery>
    claim_next_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string worker_id,
        std::uint64_t lease_seconds,
        SyncReplicaFilePayloadSnapshot payload_snapshot);

#if !defined(_WIN32)
    // Reusable durable source authority. The immutable index is prepared before
    // a claim and only the selected payload is copied after exact selection.
    [[nodiscard]] std::optional<SyncReplicaOutboundFileDelivery>
    claim_next_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string worker_id,
        std::uint64_t lease_seconds,
        const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot);
#endif

    // Rejects a stale/misbound authenticated channel or a sender-only service
    // before a receiver transport consumes any application record bytes. This
    // is an early policy/configuration gate only: receive_request_or_throw()
    // re-attests the same live authority immediately before durable work.
    void preflight_inbound_channel_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const std::string& operation_label = "inbound preflight") const;

    [[nodiscard]] SyncReplicaInboundFileDelivery receive_request_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string_view request_frame);

    [[nodiscard]] SyncReplicaFileDeliveryReceiptApplyResult
    apply_receipt_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const SyncReplicaFileDeliveryRequest& expected_request,
        std::string_view receipt_frame);

private:
    friend SyncReplicaFileTlsDispatchContinuation
    begin_sync_replica_outbound_file_delivery_over_tls_or_throw(
        SyncReplicaFileDeliveryService&,
        const SyncReplicaTlsAuthenticatedChannel&,
        const SyncReplicaOutboundFileDelivery&, const std::string&);
    friend void dispatch_sync_replica_outbound_file_delivery_over_tls_or_throw(
        SyncReplicaFileDeliveryService&,
        const SyncReplicaTlsAuthenticatedChannel&,
        const SyncReplicaOutboundFileDelivery&, const std::string&);
    friend std::optional<SyncReplicaOutboundFileDelivery>
    claim_and_dispatch_next_file_delivery_over_tls_or_throw(
        SyncReplicaFileDeliveryService&,
        const SyncReplicaTlsAuthenticatedChannel&, std::string,
        std::uint64_t, SyncReplicaFilePayloadSnapshot,
        const std::string&);

    template <typename PayloadSource>
    [[nodiscard]] std::optional<SyncReplicaOutboundFileDelivery>
    claim_next_request_from_payload_source_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        std::string worker_id,
        std::uint64_t lease_seconds,
        const PayloadSource& payload_source);

    void validate_channel_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel,
        const std::string& operation_label) const;
    [[nodiscard]] SyncReplicaFileEffectSqliteSnapshot effect_snapshot_or_throw(
        const std::string& operation_label);
    [[noreturn]] void release_claim_after_pre_dispatch_failure_or_throw(
        const SyncReplicaSqliteOutboxClaim& claim,
        const std::exception_ptr& original,
        std::string_view operation_label) const;
    [[noreturn]] void throw_dispatch_attestation_failure_or_throw(
        SyncReplicaSqliteOutboxDispatchGuardDisposition disposition,
        std::string_view operation_label) const;

    SyncReplicaSqliteOwner& replica_owner_;
    SyncReplicaFileEffectSqliteOwner* receiver_effect_owner_ = nullptr;
    SyncReplicaDeliveryService evidence_service_;
    SyncReplicaFileDeliveryProtocolLimits protocol_limits_;
    SyncReplicaFileDeliveryRetryPolicy retry_policy_;
    std::string label_;
    std::string folder_id_;
    SyncReplicaActor local_actor_;
};

}  // namespace anonsync
