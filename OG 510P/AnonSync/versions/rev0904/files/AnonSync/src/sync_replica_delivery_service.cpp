#include "sync_replica_delivery_service.hpp"

#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>

namespace anonsync {
namespace {

[[nodiscard]] SyncReplicaDeliveryReceiptDisposition
receipt_disposition(SyncReplicaAdmission admission) {
    switch (admission) {
        case SyncReplicaAdmission::InsertedActive:
            return SyncReplicaDeliveryReceiptDisposition::InsertedActive;
        case SyncReplicaAdmission::InsertedPending:
            return SyncReplicaDeliveryReceiptDisposition::InsertedPending;
        case SyncReplicaAdmission::InsertedQuarantined:
            return SyncReplicaDeliveryReceiptDisposition::InsertedQuarantined;
        case SyncReplicaAdmission::Duplicate:
            return SyncReplicaDeliveryReceiptDisposition::Duplicate;
        case SyncReplicaAdmission::CapacityBlocked:
            return SyncReplicaDeliveryReceiptDisposition::CapacityBlocked;
    }
    throw std::logic_error(
        "sync replica delivery service received an unknown admission result");
}

[[nodiscard]] std::optional<SyncReplicaDeliveryReceiptApplyResult>
classify_current_request_identity(
    const SyncReplicaSqliteSnapshot& snapshot,
    const SyncReplicaDeliveryRequest& request,
    const std::string& label) {
    const auto intent = std::find_if(
        snapshot.outbox.begin(), snapshot.outbox.end(),
        [&](const SyncReplicaSqliteOutboxIntent& candidate) {
            return candidate.destination_device_id ==
                       request.receiver_actor.device_id &&
                   candidate.operation_id == request.operation.operation_id;
        });
    if (intent == snapshot.outbox.end()) {
        return SyncReplicaDeliveryReceiptApplyResult::IntentMissing;
    }
    if (intent->lease.claim_id != request.claim_id ||
        intent->lease.dispatch_attempts != request.dispatch_attempts) {
        return SyncReplicaDeliveryReceiptApplyResult::StaleClaim;
    }
    const auto operation = std::lower_bound(
        snapshot.durable.operations.begin(),
        snapshot.durable.operations.end(),
        request.operation.operation_id,
        [](const SyncReplicaOperation& candidate, const std::string& operation_id) {
            return candidate.operation_id < operation_id;
        });
    if (operation == snapshot.durable.operations.end() ||
        operation->operation_id != request.operation.operation_id ||
        *operation != request.operation) {
        throw std::logic_error(
            label + " current outbox attempt lost its exact operation evidence");
    }
    return std::nullopt;
}

[[nodiscard]] SyncReplicaDeliveryReceiptApplyResult map_settlement_result(
    SyncReplicaSqliteOutboxReceiptResult result) {
    switch (result) {
        case SyncReplicaSqliteOutboxReceiptResult::Applied:
            return SyncReplicaDeliveryReceiptApplyResult::EvidenceSettled;
        case SyncReplicaSqliteOutboxReceiptResult::IntentMissing:
            return SyncReplicaDeliveryReceiptApplyResult::IntentMissing;
        case SyncReplicaSqliteOutboxReceiptResult::StaleClaim:
            return SyncReplicaDeliveryReceiptApplyResult::StaleClaim;
        case SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim:
            return SyncReplicaDeliveryReceiptApplyResult::ExpiredClaim;
        case SyncReplicaSqliteOutboxReceiptResult::LeaseAlreadyCovered:
            throw std::logic_error(
                "sync replica delivery settlement returned a renewal-only result");
    }
    throw std::logic_error(
        "sync replica delivery settlement returned an unknown result");
}

}  // namespace

SyncReplicaDeliveryRequest
make_sync_replica_delivery_request_from_claim_or_throw(
    const SyncReplicaSqliteOutboxClaim& claim,
    const SyncReplicaActor& local_actor,
    const SyncReplicaDeliveryChannelContext& channel,
    std::optional<SyncReplicaValueKind> required_kind,
    const std::string& label) {
    if (claim.intent.destination_device_id != channel.peer_actor.device_id) {
        throw std::logic_error(
            label + " claimed destination differs from authenticated peer");
    }
    if (claim.intent.operation_id != claim.operation.operation_id ||
        claim.operation.dot.actor != local_actor) {
        throw std::logic_error(
            label + " claimed operation is not local exact evidence");
    }
    if (required_kind.has_value() &&
        claim.operation.kind != *required_kind) {
        throw std::logic_error(
            label + " claimed operation has the wrong service value kind");
    }
    if (claim.intent.lease.claim_id.empty() ||
        claim.intent.lease.dispatch_attempts == 0U) {
        throw std::logic_error(
            label + " claimed intent lacks active attempt authority");
    }
    return {
        claim.operation.folder_id,
        local_actor,
        channel.peer_actor,
        claim.intent.lease.claim_id,
        claim.intent.lease.dispatch_attempts,
        channel.binding,
        claim.operation,
    };
}

SyncReplicaDeliveryService::SyncReplicaDeliveryService(
    SyncReplicaSqliteOwner& owner,
    SyncReplicaDeliveryServiceLimits limits,
    std::string label)
    : owner_(owner),
      protocol_limits_{
          limits.wire_operation_limits,
          limits.max_request_frame_bytes,
          limits.max_receipt_frame_bytes,
      },
      label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica delivery service label must not be empty");
    }
    const SyncReplicaSqliteSnapshot snapshot = owner_.snapshot_or_throw();
    folder_id_ = snapshot.durable.folder_id;
    local_actor_ = snapshot.durable.local_actor;
    if (!sync_id_is_valid(folder_id_) ||
        !sync_id_is_valid(local_actor_.device_id) ||
        local_actor_.epoch == 0U) {
        throw std::logic_error(label_ + " owner identity is invalid");
    }
    validate_sync_replica_delivery_protocol_limits_or_throw(
        protocol_limits_);
}

SyncReplicaSqliteSnapshot SyncReplicaDeliveryService::snapshot_or_throw(
    const std::string& operation_label) {
    SyncReplicaSqliteSnapshot snapshot = owner_.snapshot_or_throw();
    if (snapshot.durable.folder_id != folder_id_ ||
        snapshot.durable.local_actor != local_actor_) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " owner identity changed after service construction");
    }
    return snapshot;
}

void SyncReplicaDeliveryService::validate_channel_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    const std::string& operation_label) const {
    channel_authority.require_current_or_throw(
        label_ + " " + operation_label);
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    if (!sync_id_is_valid(channel.peer_actor.device_id) ||
        channel.peer_actor.epoch == 0U ||
        channel.peer_actor.device_id == local_actor_.device_id) {
        throw std::invalid_argument(
            label_ + " " + operation_label +
            " peer actor identity is invalid");
    }
    validate_sync_replica_delivery_channel_binding_or_throw(
        channel.binding, label_ + " " + operation_label);
}

std::optional<SyncReplicaOutboundDelivery>
SyncReplicaDeliveryService::claim_next_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string worker_id,
    std::uint64_t lease_seconds) {
    validate_channel_or_throw(channel_authority, "outbound claim");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    std::optional<SyncReplicaSqliteOutboxClaim> claim =
        owner_.claim_next_outbox_for_delivery_or_throw(
            std::move(worker_id), lease_seconds,
            protocol_limits_.model, channel.peer_actor.device_id);
    if (!claim.has_value()) return std::nullopt;

    SyncReplicaDeliveryRequest request =
        make_sync_replica_delivery_request_from_claim_or_throw(
            *claim, local_actor_, channel, std::nullopt,
            label_ + " outbound claim");
    std::string frame = encode_sync_replica_delivery_request_or_throw(
        request, protocol_limits_);
    const std::string digest =
        sync_replica_delivery_request_digest_or_throw(
            request, protocol_limits_);
    return SyncReplicaOutboundDelivery{
        std::move(*claim), std::move(request), std::move(frame), digest};
}

SyncReplicaInboundDelivery SyncReplicaDeliveryService::receive_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string_view request_frame) {
    validate_channel_or_throw(channel_authority, "inbound request");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    SyncReplicaDeliveryRequest request =
        decode_sync_replica_delivery_request_or_throw(
            request_frame, protocol_limits_);
    if (request.folder_id != folder_id_ ||
        request.sender_actor != channel.peer_actor ||
        request.receiver_actor != local_actor_ ||
        request.channel_binding != channel.binding) {
        throw std::runtime_error(
            label_ + " inbound request does not bind this folder, peer, actor epoch, and channel");
    }

    const SyncReplicaSqliteRemoteAdmissionResult admission =
        owner_.accept_remote_with_cutpoint_or_throw(request.operation);

    SyncReplicaDeliveryReceipt receipt;
    receipt.folder_id = folder_id_;
    receipt.sender_actor = request.sender_actor;
    receipt.receiver_actor = local_actor_;
    receipt.operation_id = request.operation.operation_id;
    receipt.claim_id = request.claim_id;
    receipt.dispatch_attempts = request.dispatch_attempts;
    receipt.request_digest =
        sync_replica_delivery_request_digest_or_throw(
            request, protocol_limits_);
    receipt.channel_binding = channel.binding;
    receipt.disposition = receipt_disposition(admission.admission);
    receipt.evidence_state = admission.evidence_state;
    receipt.receiver_state_generation = admission.state_generation;
    receipt.receiver_cutpoint_digest = admission.cutpoint_digest;

    std::string receipt_frame =
        encode_sync_replica_delivery_receipt_or_throw(
            receipt, protocol_limits_);
    const std::string receipt_digest =
        sync_replica_delivery_receipt_digest_or_throw(
            receipt, protocol_limits_);
    return {
        std::move(request), admission.admission, std::move(receipt),
        std::move(receipt_frame), receipt_digest};
}

SyncReplicaDeliveryReceiptApplyResult
SyncReplicaDeliveryService::apply_receipt_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    const SyncReplicaDeliveryRequest& expected_request,
    std::string_view receipt_frame) {
    validate_channel_or_throw(channel_authority, "receipt application");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    validate_sync_replica_delivery_request_or_throw(
        expected_request, protocol_limits_);
    if (expected_request.folder_id != folder_id_ ||
        expected_request.sender_actor != local_actor_ ||
        expected_request.receiver_actor != channel.peer_actor ||
        expected_request.channel_binding != channel.binding) {
        throw std::runtime_error(
            label_ + " expected request does not bind this folder, peer, actor epoch, and channel");
    }

    const SyncReplicaDeliveryReceipt receipt =
        decode_sync_replica_delivery_receipt_or_throw(
            receipt_frame, protocol_limits_);
    validate_sync_replica_delivery_receipt_for_request_or_throw(
        receipt, expected_request, protocol_limits_);
    if (receipt.disposition ==
        SyncReplicaDeliveryReceiptDisposition::CapacityBlocked) {
        const SyncReplicaSqliteSnapshot snapshot =
            snapshot_or_throw("capacity receipt classification");
        const auto current = classify_current_request_identity(
            snapshot, expected_request, label_ + " capacity receipt");
        if (current.has_value()) return *current;
        return SyncReplicaDeliveryReceiptApplyResult::ReceiverCapacityBlocked;
    }

    return map_settlement_result(owner_.settle_outbox_or_throw(
        receipt.receiver_actor.device_id,
        receipt.operation_id,
        receipt.claim_id));
}

}  // namespace anonsync
