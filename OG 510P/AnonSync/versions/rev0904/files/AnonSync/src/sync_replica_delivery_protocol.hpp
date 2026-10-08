#pragma once

#include "sync_replica_model.hpp"

#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint32_t kSyncReplicaDeliveryProtocolVersion = 1U;
inline constexpr std::uint64_t kSyncReplicaDeliveryDefaultMaxRequestFrameBytes =
    8ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t kSyncReplicaDeliveryDefaultMaxReceiptFrameBytes =
    64ULL * 1024ULL;
inline constexpr std::uint64_t kSyncReplicaDeliveryMaxChannelBindingBytes =
    4096ULL;

// Framing limits are independent of replica evidence limits. The request owns
// one complete canonical operation plus exact dispatch/channel identity; the
// receipt is deliberately small. A caller may tighten either frame ceiling but
// cannot loosen the model's operation validation through this layer.
struct SyncReplicaDeliveryProtocolLimits final {
    SyncReplicaModelLimits model;
    std::uint64_t max_request_frame_bytes =
        kSyncReplicaDeliveryDefaultMaxRequestFrameBytes;
    std::uint64_t max_receipt_frame_bytes =
        kSyncReplicaDeliveryDefaultMaxReceiptFrameBytes;

    bool operator==(const SyncReplicaDeliveryProtocolLimits&) const = default;
};

void validate_sync_replica_delivery_protocol_limits_or_throw(
    const SyncReplicaDeliveryProtocolLimits& limits);

// The lower authenticated transport owns the raw binding observation. This
// protocol stores only a domain-separated SHA-256 digest and its public type.
// The digest is not a key and is not authentication by itself. For TLS 1.3 the
// raw observation can be RFC 9266 tls-exporter bytes; for Noise it can be the
// handshake hash. Synthetic test bindings use the same explicit boundary.
struct SyncReplicaDeliveryChannelBinding final {
    std::string type;
    std::string digest;

    bool operator==(const SyncReplicaDeliveryChannelBinding&) const = default;
};

[[nodiscard]] SyncReplicaDeliveryChannelBinding
make_sync_replica_delivery_channel_binding_or_throw(
    std::string type,
    std::string_view raw_binding_bytes);

void validate_sync_replica_delivery_channel_binding_or_throw(
    const SyncReplicaDeliveryChannelBinding& binding,
    const std::string& label);

// One request is exact attempt authority, not merely an operation envelope.
// The receiver actor epoch and channel binding prevent a request authorized for
// one authenticated incarnation/session from being replayed as another. Lease
// timestamps and worker identity remain local operational state and are not
// leaked because the receiver does not need them to admit immutable evidence.
struct SyncReplicaDeliveryRequest final {
    std::string folder_id;
    SyncReplicaActor sender_actor;
    SyncReplicaActor receiver_actor;
    std::string claim_id;
    std::uint64_t dispatch_attempts = 0;
    SyncReplicaDeliveryChannelBinding channel_binding;
    SyncReplicaOperation operation;

    bool operator==(const SyncReplicaDeliveryRequest&) const = default;
};

enum class SyncReplicaDeliveryReceiptDisposition : std::uint8_t {
    InsertedActive = 1U,
    InsertedPending = 2U,
    InsertedQuarantined = 3U,
    Duplicate = 4U,
    CapacityBlocked = 5U,
};

// A receipt reports the exact receiver evidence state after durable admission.
// "Terminal" in this protocol means terminal only for immutable operation-
// evidence transfer; it does not attest payload materialization or a visible
// filesystem effect. cutpoint_digest remains an unkeyed structural token;
// authenticity comes only from the lower channel that produced the binding.
// CapacityBlocked is the sole nonterminal disposition and carries no retained
// evidence state; its unchanged receiver generation and cutpoint remain explicit.
struct SyncReplicaDeliveryReceipt final {
    std::string folder_id;
    SyncReplicaActor sender_actor;
    SyncReplicaActor receiver_actor;
    std::string operation_id;
    std::string claim_id;
    std::uint64_t dispatch_attempts = 0;
    std::string request_digest;
    SyncReplicaDeliveryChannelBinding channel_binding;
    SyncReplicaDeliveryReceiptDisposition disposition =
        SyncReplicaDeliveryReceiptDisposition::CapacityBlocked;
    std::optional<SyncReplicaEvidenceState> evidence_state;
    std::uint64_t receiver_state_generation = 0;
    std::string receiver_cutpoint_digest;

    bool operator==(const SyncReplicaDeliveryReceipt&) const = default;
};

[[nodiscard]] bool sync_replica_delivery_receipt_is_evidence_terminal(
    SyncReplicaDeliveryReceiptDisposition disposition) noexcept;

void validate_sync_replica_delivery_request_or_throw(
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits = {});

void validate_sync_replica_delivery_receipt_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryProtocolLimits& limits = {});

[[nodiscard]] std::string encode_sync_replica_delivery_request_or_throw(
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaDeliveryRequest
    decode_sync_replica_delivery_request_or_throw(
        std::string_view frame,
        const SyncReplicaDeliveryProtocolLimits& limits = {});

[[nodiscard]] std::string sync_replica_delivery_request_digest_or_throw(
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits = {});

[[nodiscard]] std::string encode_sync_replica_delivery_receipt_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryProtocolLimits& limits = {});

[[nodiscard]] SyncReplicaDeliveryReceipt
    decode_sync_replica_delivery_receipt_or_throw(
        std::string_view frame,
        const SyncReplicaDeliveryProtocolLimits& limits = {});

[[nodiscard]] std::string sync_replica_delivery_receipt_digest_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryProtocolLimits& limits = {});

// Exact cross-message validation. This does not prove that the channel context
// was honestly obtained; it ensures a decoded receipt cannot be applied to a
// different request, actor epoch, operation, claim, attempt, or channel.
void validate_sync_replica_delivery_receipt_for_request_or_throw(
    const SyncReplicaDeliveryReceipt& receipt,
    const SyncReplicaDeliveryRequest& request,
    const SyncReplicaDeliveryProtocolLimits& limits = {});

}  // namespace anonsync
