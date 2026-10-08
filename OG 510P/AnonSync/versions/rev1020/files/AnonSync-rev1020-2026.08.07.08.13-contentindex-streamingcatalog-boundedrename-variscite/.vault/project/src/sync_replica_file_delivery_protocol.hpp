#pragma once

#include "sync_replica_delivery_protocol.hpp"

#include <cstdint>
#include <optional>
#include <string>
#include <string_view>

namespace anonsync {

inline constexpr std::uint32_t kSyncReplicaFileDeliveryProtocolVersion = 2U;
inline constexpr std::uint64_t kSyncReplicaFileDeliveryDefaultMaxPayloadBytes =
    4ULL * 1024ULL * 1024ULL;

// File-delivery v2 owns one complete payload inside one authenticated frame.
// It remains a deliberately small compatibility path even when a folder admits
// much larger files; resumable reconciliation ranges own those files.
[[nodiscard]] constexpr std::uint64_t
sync_replica_file_delivery_single_frame_payload_limit(
    std::uint64_t configured_max_payload_bytes) noexcept {
    return configured_max_payload_bytes <
                   kSyncReplicaFileDeliveryDefaultMaxPayloadBytes
        ? configured_max_payload_bytes
        : kSyncReplicaFileDeliveryDefaultMaxPayloadBytes;
}
inline constexpr std::uint64_t
    kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes =
        16ULL * 1024ULL * 1024ULL;
inline constexpr std::uint64_t
    kSyncReplicaFileDeliveryDefaultMaxReceiptFrameBytes =
        256ULL * 1024ULL;

struct SyncReplicaFileDeliveryProtocolLimits final {
    SyncReplicaDeliveryProtocolLimits evidence;
    std::uint64_t max_payload_bytes =
        kSyncReplicaFileDeliveryDefaultMaxPayloadBytes;
    std::uint64_t max_request_frame_bytes =
        kSyncReplicaFileDeliveryDefaultMaxRequestFrameBytes;
    std::uint64_t max_receipt_frame_bytes =
        kSyncReplicaFileDeliveryDefaultMaxReceiptFrameBytes;

    bool operator==(const SyncReplicaFileDeliveryProtocolLimits&) const =
        default;
};

void validate_sync_replica_file_delivery_protocol_limits_or_throw(
    const SyncReplicaFileDeliveryProtocolLimits& limits);

// Cheap classifier used only after the TLS record layer has delivered one
// complete bounded frame. A positive result selects the file-delivery decoder;
// it is not validation or authorization.
[[nodiscard]] bool sync_replica_file_delivery_request_frame_has_magic(
    std::string_view frame) noexcept;

// The inner evidence request remains the exact authenticated attempt envelope.
// The outer request adds the content bytes committed by that operation. Version
// 2 deliberately supports files only; tombstone effects need a separate policy
// for deletion, conflict preservation, and rollback-safe namespace mutation.
struct SyncReplicaFileDeliveryRequest final {
    SyncReplicaDeliveryRequest evidence_request;
    std::string payload;

    bool operator==(const SyncReplicaFileDeliveryRequest&) const = default;
};

enum class SyncReplicaFileDeliveryReceiptDisposition : std::uint8_t {
    Published = 1U,
    AlreadyPublished = 2U,
    EffectCapacityBlocked = 3U,
    EvidenceCapacityBlocked = 4U,
    EvidencePending = 5U,
    EvidenceQuarantined = 6U,
    ProjectionBlocked = 7U,
    DestinationConflict = 8U,
    EffectPathBlocked = 9U,
};

// Effect-terminal means exact payload bytes are durably published at the
// receiver's canonical destination and the receiver effect database has marked
// that fact. Every other disposition leaves the sender outbox intent live.
[[nodiscard]] bool sync_replica_file_delivery_receipt_is_effect_terminal(
    SyncReplicaFileDeliveryReceiptDisposition disposition) noexcept;

// Capacity and receiver-local path policy can deny effect acquisition before
// causal evidence admission. Those receipts deliberately carry neither an
// inner evidence receipt nor an effect ID; they attest only the exact request,
// unchanged effect cutpoint, and typed denial.
[[nodiscard]] bool
sync_replica_file_delivery_receipt_precedes_effect_authority(
    SyncReplicaFileDeliveryReceiptDisposition disposition) noexcept;

struct SyncReplicaFileDeliveryReceipt final {
    std::string folder_id;
    SyncReplicaActor sender_actor;
    SyncReplicaActor receiver_actor;
    std::string operation_id;
    std::string claim_id;
    std::uint64_t dispatch_attempts = 0U;
    std::string request_digest;
    SyncReplicaDeliveryChannelBinding channel_binding;
    SyncReplicaFileDeliveryReceiptDisposition disposition =
        SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked;

    // Pre-effect dispositions occur before evidence admission and therefore
    // have no inner receipt. Every other disposition owns the exact evidence
    // result.
    std::optional<SyncReplicaDeliveryReceipt> evidence_receipt;

    // Empty only for a pre-effect disposition. Otherwise this is the shared
    // structural identity of the staged/published immutable effect.
    std::string effect_id;
    std::uint64_t receiver_effect_generation = 0U;
    std::string receiver_effect_cutpoint_digest;

    bool operator==(const SyncReplicaFileDeliveryReceipt&) const = default;
};

void validate_sync_replica_file_delivery_request_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits = {});
void validate_sync_replica_file_delivery_receipt_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryProtocolLimits& limits = {});

[[nodiscard]] std::string encode_sync_replica_file_delivery_request_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits = {});
[[nodiscard]] SyncReplicaFileDeliveryRequest
    decode_sync_replica_file_delivery_request_or_throw(
        std::string_view frame,
        const SyncReplicaFileDeliveryProtocolLimits& limits = {});
[[nodiscard]] std::string sync_replica_file_delivery_request_digest_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits = {});

[[nodiscard]] std::string encode_sync_replica_file_delivery_receipt_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryProtocolLimits& limits = {});
[[nodiscard]] SyncReplicaFileDeliveryReceipt
    decode_sync_replica_file_delivery_receipt_or_throw(
        std::string_view frame,
        const SyncReplicaFileDeliveryProtocolLimits& limits = {});
[[nodiscard]] std::string sync_replica_file_delivery_receipt_digest_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryProtocolLimits& limits = {});

void validate_sync_replica_file_delivery_receipt_for_request_or_throw(
    const SyncReplicaFileDeliveryReceipt& receipt,
    const SyncReplicaFileDeliveryRequest& request,
    const SyncReplicaFileDeliveryProtocolLimits& limits = {});

}  // namespace anonsync
