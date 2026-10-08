#include "sync_replica_file_delivery_service.hpp"

#include "sync_manifest_validation.hpp"
#include "sync_replica_file_effect_identity.hpp"

#include <algorithm>
#include <cstdint>
#include <exception>
#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <type_traits>
#include <utility>

namespace anonsync {
namespace {

[[nodiscard]] SyncReplicaFileDeliveryReceiptApplyResult
map_settlement_result(SyncReplicaSqliteOutboxReceiptResult result) {
    switch (result) {
        case SyncReplicaSqliteOutboxReceiptResult::Applied:
            return SyncReplicaFileDeliveryReceiptApplyResult::EffectSettled;
        case SyncReplicaSqliteOutboxReceiptResult::IntentMissing:
            return SyncReplicaFileDeliveryReceiptApplyResult::IntentMissing;
        case SyncReplicaSqliteOutboxReceiptResult::StaleClaim:
            return SyncReplicaFileDeliveryReceiptApplyResult::StaleClaim;
        case SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim:
            return SyncReplicaFileDeliveryReceiptApplyResult::ExpiredClaim;
        case SyncReplicaSqliteOutboxReceiptResult::LeaseAlreadyCovered:
            throw std::logic_error(
                "file delivery settlement returned a renewal-only result");
    }
    throw std::logic_error(
        "file delivery settlement returned an unknown result");
}

[[nodiscard]] SyncReplicaFileDeliveryReceiptApplyResult
nonterminal_apply_result(
    SyncReplicaFileDeliveryReceiptDisposition disposition) {
    switch (disposition) {
        case SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked:
            return SyncReplicaFileDeliveryReceiptApplyResult::
                ReceiverEffectCapacityBlocked;
        case SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked:
            return SyncReplicaFileDeliveryReceiptApplyResult::
                ReceiverEffectPathBlocked;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceCapacityBlocked:
            return SyncReplicaFileDeliveryReceiptApplyResult::
                ReceiverEvidenceCapacityBlocked;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidencePending:
            return SyncReplicaFileDeliveryReceiptApplyResult::
                ReceiverEvidencePending;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceQuarantined:
            return SyncReplicaFileDeliveryReceiptApplyResult::
                ReceiverEvidenceQuarantined;
        case SyncReplicaFileDeliveryReceiptDisposition::ProjectionBlocked:
            return SyncReplicaFileDeliveryReceiptApplyResult::
                ReceiverProjectionBlocked;
        case SyncReplicaFileDeliveryReceiptDisposition::DestinationConflict:
            return SyncReplicaFileDeliveryReceiptApplyResult::
                ReceiverDestinationConflict;
        case SyncReplicaFileDeliveryReceiptDisposition::Published:
        case SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished:
            throw std::logic_error(
                "terminal file receipt entered nonterminal classification");
    }
    throw std::logic_error(
        "unknown file receipt entered nonterminal classification");
}

void validate_retry_policy_or_throw(
    const SyncReplicaFileDeliveryRetryPolicy& policy,
    const std::string& label) {
    const auto validate_delay = [&](std::uint64_t delay,
                                    const char* field) {
        if (delay == 0U ||
            delay > kSyncReplicaOutboxMaxRetryDelaySeconds) {
            throw std::invalid_argument(
                label + " " + field +
                " must be positive and within the fixed outbox retry-delay budget");
        }
    };
    validate_delay(policy.pre_dispatch_failure_delay_seconds,
                   "pre-dispatch retry delay");
    validate_delay(policy.effect_capacity_blocked_delay_seconds,
                   "effect-capacity retry delay");
    validate_delay(policy.effect_path_blocked_delay_seconds,
                   "effect-path retry delay");
    validate_delay(policy.evidence_capacity_blocked_delay_seconds,
                   "evidence-capacity retry delay");
    validate_delay(policy.evidence_pending_delay_seconds,
                   "evidence-pending retry delay");
    validate_delay(policy.evidence_quarantined_delay_seconds,
                   "evidence-quarantined retry delay");
    validate_delay(policy.projection_blocked_delay_seconds,
                   "projection-blocked retry delay");
    validate_delay(policy.destination_conflict_delay_seconds,
                   "destination-conflict retry delay");
}

[[nodiscard]] std::uint64_t retry_delay_for_nonterminal_or_throw(
    SyncReplicaFileDeliveryReceiptDisposition disposition,
    const SyncReplicaFileDeliveryRetryPolicy& policy) {
    switch (disposition) {
        case SyncReplicaFileDeliveryReceiptDisposition::EffectCapacityBlocked:
            return policy.effect_capacity_blocked_delay_seconds;
        case SyncReplicaFileDeliveryReceiptDisposition::EffectPathBlocked:
            return policy.effect_path_blocked_delay_seconds;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceCapacityBlocked:
            return policy.evidence_capacity_blocked_delay_seconds;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidencePending:
            return policy.evidence_pending_delay_seconds;
        case SyncReplicaFileDeliveryReceiptDisposition::EvidenceQuarantined:
            return policy.evidence_quarantined_delay_seconds;
        case SyncReplicaFileDeliveryReceiptDisposition::ProjectionBlocked:
            return policy.projection_blocked_delay_seconds;
        case SyncReplicaFileDeliveryReceiptDisposition::DestinationConflict:
            return policy.destination_conflict_delay_seconds;
        case SyncReplicaFileDeliveryReceiptDisposition::Published:
        case SyncReplicaFileDeliveryReceiptDisposition::AlreadyPublished:
            throw std::logic_error(
                "terminal file receipt requested a retry delay");
    }
    throw std::logic_error(
        "unknown file receipt requested a retry delay");
}

[[nodiscard]] SyncReplicaFileDeliveryReceiptApplyResult map_release_result(
    SyncReplicaSqliteOutboxReceiptResult result,
    SyncReplicaFileDeliveryReceiptDisposition disposition) {
    switch (result) {
        case SyncReplicaSqliteOutboxReceiptResult::Applied:
            return nonterminal_apply_result(disposition);
        case SyncReplicaSqliteOutboxReceiptResult::IntentMissing:
            return SyncReplicaFileDeliveryReceiptApplyResult::IntentMissing;
        case SyncReplicaSqliteOutboxReceiptResult::StaleClaim:
            return SyncReplicaFileDeliveryReceiptApplyResult::StaleClaim;
        case SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim:
            return SyncReplicaFileDeliveryReceiptApplyResult::ExpiredClaim;
        case SyncReplicaSqliteOutboxReceiptResult::LeaseAlreadyCovered:
            throw std::logic_error(
                "file delivery retry release returned a renewal-only result");
    }
    throw std::logic_error(
        "file delivery retry release returned an unknown result");
}

[[nodiscard]] std::string exception_message(
    const std::exception_ptr& exception) {
    try {
        std::rethrow_exception(exception);
    } catch (const std::exception& error) {
        return error.what();
    } catch (...) {
        return "non-standard exception";
    }
}

[[nodiscard]] const SyncReplicaFileEffectRecord& find_effect_record_or_throw(
    const SyncReplicaFileEffectSqliteSnapshot& snapshot,
    const std::string& operation_id,
    const std::string& label) {
    const auto found = std::lower_bound(
        snapshot.effects.begin(), snapshot.effects.end(), operation_id,
        [](const SyncReplicaFileEffectRecord& record,
           const std::string& id) {
            return record.operation.operation_id < id;
        });
    if (found == snapshot.effects.end() ||
        found->operation.operation_id != operation_id) {
        throw std::logic_error(label + " staged effect record is missing");
    }
    return *found;
}

[[nodiscard]] SyncReplicaFileDeliveryReceipt make_receipt_or_throw(
    const SyncReplicaFileDeliveryRequest& request,
    SyncReplicaFileDeliveryReceiptDisposition disposition,
    std::optional<SyncReplicaDeliveryReceipt> evidence_receipt,
    const SyncReplicaFileEffectSqliteSnapshot& effect_snapshot,
    const SyncReplicaFileDeliveryProtocolLimits& limits,
    const std::string& label) {
    const SyncReplicaDeliveryRequest& evidence_request =
        request.evidence_request;
    SyncReplicaFileDeliveryReceipt receipt;
    receipt.folder_id = evidence_request.folder_id;
    receipt.sender_actor = evidence_request.sender_actor;
    receipt.receiver_actor = evidence_request.receiver_actor;
    receipt.operation_id = evidence_request.operation.operation_id;
    receipt.claim_id = evidence_request.claim_id;
    receipt.dispatch_attempts = evidence_request.dispatch_attempts;
    receipt.request_digest =
        sync_replica_file_delivery_request_digest_or_throw(request, limits);
    receipt.channel_binding = evidence_request.channel_binding;
    receipt.disposition = disposition;
    receipt.evidence_receipt = std::move(evidence_receipt);
    receipt.receiver_effect_generation = effect_snapshot.state_generation;
    receipt.receiver_effect_cutpoint_digest = effect_snapshot.cutpoint_digest;
    if (!sync_replica_file_delivery_receipt_precedes_effect_authority(
            disposition)) {
        receipt.effect_id = find_effect_record_or_throw(
            effect_snapshot, receipt.operation_id,
            label + " receipt").effect_id;
    }
    validate_sync_replica_file_delivery_receipt_for_request_or_throw(
        receipt, request, limits);
    return receipt;
}

[[nodiscard]] SyncReplicaFileDeliveryReceiptDisposition
classify_evidence_nonactive_or_throw(
    const SyncReplicaDeliveryReceipt& receipt) {
    if (receipt.disposition ==
        SyncReplicaDeliveryReceiptDisposition::CapacityBlocked) {
        return SyncReplicaFileDeliveryReceiptDisposition::
            EvidenceCapacityBlocked;
    }
    if (receipt.evidence_state ==
        SyncReplicaEvidenceState::PendingMissingDependency) {
        return SyncReplicaFileDeliveryReceiptDisposition::EvidencePending;
    }
    if (receipt.evidence_state.has_value() &&
        sync_replica_evidence_state_is_quarantined(
            *receipt.evidence_state)) {
        return SyncReplicaFileDeliveryReceiptDisposition::
            EvidenceQuarantined;
    }
    if (receipt.evidence_state == SyncReplicaEvidenceState::Active) {
        return SyncReplicaFileDeliveryReceiptDisposition::ProjectionBlocked;
    }
    throw std::logic_error(
        "file delivery evidence receipt has no classifiable retained state");
}

}  // namespace

SyncReplicaFileDeliveryService::SyncReplicaFileDeliveryService(
    SyncReplicaSqliteOwner& replica_owner,
    SyncReplicaFileEffectSqliteOwner* receiver_effect_owner,
    SyncReplicaFileDeliveryServiceLimits limits,
    std::string label)
    : replica_owner_(replica_owner),
      receiver_effect_owner_(receiver_effect_owner),
      evidence_service_(replica_owner, limits.evidence,
                        label + " evidence"),
      protocol_limits_{
          {limits.evidence.wire_operation_limits,
           limits.evidence.max_request_frame_bytes,
           limits.evidence.max_receipt_frame_bytes},
          limits.max_payload_bytes,
          limits.max_request_frame_bytes,
          limits.max_receipt_frame_bytes,
      },
      retry_policy_(limits.retry),
      label_(std::move(label)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica file delivery service label must not be empty");
    }
    folder_id_ = evidence_service_.folder_id();
    local_actor_ = evidence_service_.local_actor();
    validate_sync_replica_file_delivery_protocol_limits_or_throw(
        protocol_limits_);
    validate_retry_policy_or_throw(retry_policy_, label_ + " retry policy");
    if (receiver_effect_owner_ != nullptr) {
        const SyncReplicaFileEffectSqliteIdentityCutpoint effect =
            receiver_effect_owner_->identity_cutpoint_or_throw();
        if (effect.folder_id != folder_id_) {
            throw std::invalid_argument(
                label_ + " replica and file-effect folders differ");
        }
        if (protocol_limits_.max_payload_bytes >
            effect.limits.max_payload_bytes) {
            throw std::invalid_argument(
                label_ + " wire payload limit exceeds receiver effect policy");
        }
    }
}

void SyncReplicaFileDeliveryService::validate_channel_or_throw(
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

void SyncReplicaFileDeliveryService::preflight_inbound_channel_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    const std::string& operation_label) const {
    if (operation_label.empty()) {
        throw std::invalid_argument(
            label_ + " inbound preflight label must not be empty");
    }
    validate_channel_or_throw(channel_authority, operation_label);
    if (receiver_effect_owner_ == nullptr) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " requires a receiver file-effect owner");
    }
}

SyncReplicaFileEffectSqliteSnapshot
SyncReplicaFileDeliveryService::effect_snapshot_or_throw(
    const std::string& operation_label) {
    if (receiver_effect_owner_ == nullptr) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " requires a receiver file-effect owner");
    }
    SyncReplicaFileEffectSqliteSnapshot snapshot =
        receiver_effect_owner_->snapshot_or_throw();
    if (snapshot.folder_id != folder_id_) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " effect owner identity changed after construction");
    }
    return snapshot;
}

[[noreturn]] void
SyncReplicaFileDeliveryService::release_claim_after_pre_dispatch_failure_or_throw(
    const SyncReplicaSqliteOutboxClaim& claim,
    const std::exception_ptr& original,
    std::string_view operation_label) const {
    std::string release_failure;
    try {
        const SyncReplicaSqliteOutboxReceiptResult release =
            replica_owner_.release_outbox_for_retry_or_throw(
                claim.intent.destination_device_id,
                claim.operation.operation_id,
                claim.intent.lease.claim_id,
                retry_policy_.pre_dispatch_failure_delay_seconds);
        switch (release) {
            case SyncReplicaSqliteOutboxReceiptResult::Applied:
                break;
            case SyncReplicaSqliteOutboxReceiptResult::IntentMissing:
                throw std::logic_error(
                    "pre-dispatch retry release lost its outbox intent");
            case SyncReplicaSqliteOutboxReceiptResult::StaleClaim:
                throw std::logic_error(
                    "pre-dispatch retry release lost exact claim identity");
            case SyncReplicaSqliteOutboxReceiptResult::ExpiredClaim:
                throw std::logic_error(
                    "pre-dispatch retry release found its exact claim expired");
            case SyncReplicaSqliteOutboxReceiptResult::LeaseAlreadyCovered:
                throw std::logic_error(
                    "pre-dispatch retry release returned a renewal-only result");
        }
    } catch (const std::exception& error) {
        release_failure = error.what();
    } catch (...) {
        release_failure = "non-standard exception";
    }
    const std::string frontier(operation_label);
    if (!release_failure.empty()) {
        throw std::runtime_error(
            label_ + " " + frontier + " failure (" +
            exception_message(original) +
            ") and exact retry release failed: " + release_failure);
    }
    std::rethrow_exception(original);
}

[[noreturn]] void
SyncReplicaFileDeliveryService::throw_dispatch_attestation_failure_or_throw(
    SyncReplicaSqliteOutboxDispatchGuardDisposition disposition,
    std::string_view operation_label) const {
    const std::string frontier(operation_label);
    switch (disposition) {
        case SyncReplicaSqliteOutboxDispatchGuardDisposition::IntentMissing:
            throw std::runtime_error(
                label_ + " " + frontier +
                " dispatch attestation lost its outbox intent");
        case SyncReplicaSqliteOutboxDispatchGuardDisposition::StaleClaim:
            throw std::runtime_error(
                label_ + " " + frontier +
                " dispatch attestation lost exact claim identity");
        case SyncReplicaSqliteOutboxDispatchGuardDisposition::ExpiredClaim:
            throw std::runtime_error(
                label_ + " " + frontier +
                " dispatch attestation found its exact claim expired");
        case SyncReplicaSqliteOutboxDispatchGuardDisposition::Acquired:
            throw std::logic_error(
                label_ + " " + frontier +
                " acquired dispatch attestation has no live guard");
    }
    throw std::logic_error(
        label_ + " " + frontier + " dispatch attestation is unknown");
}

std::optional<SyncReplicaOutboundFileDelivery>
SyncReplicaFileDeliveryService::claim_next_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string worker_id,
    std::uint64_t lease_seconds,
    SyncReplicaFilePayloadSnapshot payload_snapshot) {
    return claim_next_request_from_payload_source_or_throw(
        channel_authority, std::move(worker_id), lease_seconds,
        payload_snapshot);
}

#if !defined(_WIN32)
std::optional<SyncReplicaOutboundFileDelivery>
SyncReplicaFileDeliveryService::claim_next_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string worker_id,
    std::uint64_t lease_seconds,
    const SyncReplicaFilePayloadStoreSnapshot& payload_snapshot) {
    return claim_next_request_from_payload_source_or_throw(
        channel_authority, std::move(worker_id), lease_seconds,
        payload_snapshot);
}
#endif

template <typename PayloadSource>
std::optional<SyncReplicaOutboundFileDelivery>
SyncReplicaFileDeliveryService::
    claim_next_request_from_payload_source_or_throw(
        const SyncReplicaDeliveryChannelAuthority& channel_authority,
        std::string worker_id,
        std::uint64_t lease_seconds,
        const PayloadSource& payload_source) {
    validate_channel_or_throw(channel_authority, "outbound claim");
    payload_source.require_folder_or_throw(
        folder_id_, label_ + " outbound claim");
    payload_source.preflight_or_throw(
        label_ + " outbound payload source preflight");
    // Freeze public channel context and immutable digest availability before a
    // durable claim exists. The concrete source performs no arbitrary caller
    // callback while the claim is live; only one exact selected payload is
    // copied afterward.
    const SyncReplicaDeliveryChannelContext channel =
        channel_authority.context();
    std::optional<SyncReplicaSqliteOutboxClaim> claim =
        replica_owner_.claim_next_outbox_for_delivery_or_throw(
            std::move(worker_id), lease_seconds,
            protocol_limits_.evidence.model,
            channel.peer_actor.device_id,
            SyncReplicaValueKind::File,
            protocol_limits_.max_payload_bytes,
            payload_source.content_inventory());
    if (!claim.has_value()) return std::nullopt;

    std::string payload;
    try {
        // The same immutable digest inventory selected this operation inside
        // the owner transaction. This lookup can still reject a declared-size
        // disagreement (or fail to allocate the bounded owned copy), but an
        // ordinary absent digest cannot consume attempt authority.
        payload = payload_source.copy_payload_for_operation_or_throw(
            claim->operation, label_ + " outbound payload lookup");
    } catch (...) {
        release_claim_after_pre_dispatch_failure_or_throw(
            *claim, std::current_exception(),
            "outbound payload lookup");
    }

    SyncReplicaSqliteOutboxDispatchGuardResult dispatch_result;
    try {
        dispatch_result =
            replica_owner_.guard_outbox_claim_for_dispatch_or_throw(*claim);
    } catch (...) {
        release_claim_after_pre_dispatch_failure_or_throw(
            *claim, std::current_exception(),
            "outbound guard acquisition");
    }
    if (dispatch_result.disposition !=
            SyncReplicaSqliteOutboxDispatchGuardDisposition::Acquired ||
        dispatch_result.guard == nullptr) {
        throw_dispatch_attestation_failure_or_throw(
            dispatch_result.disposition, "post-payload-lookup");
    }

    std::unique_ptr<SyncReplicaSqliteOutboxDispatchGuard> dispatch_guard =
        std::move(dispatch_result.guard);
    try {
        // Re-prove channel liveness inside the same bounded construction
        // frontier that freezes the exact outbox row. No caller code or network
        // I/O is permitted while the SQLite writer capability is held.
        validate_channel_or_throw(
            channel_authority, "outbound dispatch construction");
        SyncReplicaSqliteOutboxClaim attested_claim =
            dispatch_guard->claim();
        SyncReplicaFileDeliveryRequest request;
        request.evidence_request =
            make_sync_replica_delivery_request_from_claim_or_throw(
                attested_claim, local_actor_, channel,
                SyncReplicaValueKind::File,
                label_ + " outbound dispatch construction");
        request.payload = std::move(payload);
        validate_sync_replica_file_delivery_request_or_throw(
            request, protocol_limits_);
        std::string frame =
            encode_sync_replica_file_delivery_request_or_throw(
                request, protocol_limits_);
        std::string digest =
            sync_replica_file_delivery_request_digest_or_throw(
                request, protocol_limits_);
        SyncReplicaOutboundFileDelivery outbound{
            std::move(attested_claim), std::move(request), std::move(frame),
            std::move(digest)};
        static_assert(std::is_nothrow_move_constructible_v<
                      SyncReplicaOutboundFileDelivery>);
        static_assert(std::is_nothrow_constructible_v<
                      std::optional<SyncReplicaOutboundFileDelivery>,
                      SyncReplicaOutboundFileDelivery&&>);
        dispatch_guard->commit_or_throw();
        return outbound;
    } catch (...) {
        const std::exception_ptr original = std::current_exception();
        // Roll back any staged clock observation and release the SQLite writer
        // slot before attempting the exact durable retry transition.
        dispatch_guard.reset();
        release_claim_after_pre_dispatch_failure_or_throw(
            *claim, original, "outbound dispatch construction");
    }
}

SyncReplicaInboundFileDelivery
SyncReplicaFileDeliveryService::receive_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string_view request_frame) {
    preflight_inbound_channel_or_throw(
        channel_authority, "inbound request");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    SyncReplicaFileDeliveryRequest request =
        decode_sync_replica_file_delivery_request_or_throw(
            request_frame, protocol_limits_);
    const SyncReplicaDeliveryRequest& decoded_evidence_request =
        request.evidence_request;
    if (decoded_evidence_request.folder_id != folder_id_ ||
        decoded_evidence_request.sender_actor != channel.peer_actor ||
        decoded_evidence_request.receiver_actor != local_actor_ ||
        decoded_evidence_request.channel_binding != channel.binding) {
        throw std::runtime_error(
            label_ + " inbound request does not bind this folder, peer, actor epoch, and channel");
    }

    SyncReplicaFileEffectStageOutcome stage =
        receiver_effect_owner_->stage_with_diagnostics_or_throw(
            decoded_evidence_request.operation,
            {reinterpret_cast<const unsigned char*>(request.payload.data()),
             request.payload.size()});
    SyncReplicaInboundFileDelivery inbound;
    static_assert(std::is_nothrow_move_assignable_v<
                  SyncReplicaFileDeliveryRequest>);
    static_assert(std::is_nothrow_move_assignable_v<
                  std::optional<SyncReplicaFileEffectCapacityBlock>>);
    inbound.request = std::move(request);
    inbound.stage_result = stage.result;
    inbound.capacity_block = std::move(stage.capacity_block);
    const SyncReplicaDeliveryRequest& evidence_request =
        inbound.request.evidence_request;

    std::optional<SyncReplicaFileDeliveryReceiptDisposition> disposition;
    std::optional<SyncReplicaDeliveryReceipt> evidence_receipt;
    std::unique_ptr<SyncReplicaSqliteProjectionGuard> projection_guard;
    switch (inbound.stage_result) {
        case SyncReplicaFileEffectStageResult::CapacityBlocked:
            disposition = SyncReplicaFileDeliveryReceiptDisposition::
                EffectCapacityBlocked;
            break;
        case SyncReplicaFileEffectStageResult::DestinationPathBlocked:
            disposition = SyncReplicaFileDeliveryReceiptDisposition::
                EffectPathBlocked;
            break;
        case SyncReplicaFileEffectStageResult::Inserted:
        case SyncReplicaFileEffectStageResult::Duplicate:
            break;
    }
    if (!disposition.has_value()) {
        inbound.evidence_delivery = evidence_service_.receive_request_or_throw(
            channel_authority,
            encode_sync_replica_delivery_request_or_throw(
                evidence_request, protocol_limits_.evidence));
        evidence_receipt = inbound.evidence_delivery->receipt;
        if (evidence_receipt->evidence_state !=
            SyncReplicaEvidenceState::Active) {
            disposition = classify_evidence_nonactive_or_throw(
                *evidence_receipt);
        } else {
            // The inner evidence receipt names the exact admission cutpoint.
            // Hold a BEGIN IMMEDIATE guard on that same cutpoint across the
            // independent filesystem/effect transaction. Without this bridge,
            // another causal writer could supersede the primary after a loose
            // snapshot check but before publication, minting stale visible
            // authority. A changed cutpoint is conservatively retried through
            // duplicate admission so a fresh receipt owns the next decision.
            projection_guard = replica_owner_.
                guard_unambiguous_file_primary_at_cutpoint_or_throw(
                    evidence_request.operation,
                    evidence_receipt->receiver_state_generation,
                    evidence_receipt->receiver_cutpoint_digest);
            if (!projection_guard) {
                disposition = SyncReplicaFileDeliveryReceiptDisposition::
                    ProjectionBlocked;
            } else {
                const SyncReplicaSqliteSnapshot& guarded =
                    projection_guard->snapshot();
                if (guarded.state_generation !=
                        evidence_receipt->receiver_state_generation ||
                    guarded.cutpoint_digest !=
                        evidence_receipt->receiver_cutpoint_digest) {
                    throw std::logic_error(
                        label_ +
                        " projection guard did not retain the evidence receipt cutpoint");
                }
                inbound.materialize_result =
                    receiver_effect_owner_->materialize_or_throw(
                        evidence_request.operation.operation_id);
                switch (*inbound.materialize_result) {
                    case SyncReplicaFileEffectMaterializeResult::Published:
                        disposition = SyncReplicaFileDeliveryReceiptDisposition::
                            Published;
                        break;
                    case SyncReplicaFileEffectMaterializeResult::AlreadyPublished:
                        disposition = SyncReplicaFileDeliveryReceiptDisposition::
                            AlreadyPublished;
                        break;
                    case SyncReplicaFileEffectMaterializeResult::DestinationConflict:
                        disposition = SyncReplicaFileDeliveryReceiptDisposition::
                            DestinationConflict;
                        break;
                }
            }
        }
    }

    if (!disposition.has_value()) {
        throw std::logic_error(
            label_ + " inbound request produced no classified disposition");
    }
    const SyncReplicaFileEffectSqliteSnapshot effect_snapshot =
        effect_snapshot_or_throw("receipt construction");
    inbound.receipt = make_receipt_or_throw(
        inbound.request, *disposition, std::move(evidence_receipt),
        effect_snapshot, protocol_limits_, label_);
    inbound.receipt_frame =
        encode_sync_replica_file_delivery_receipt_or_throw(
            inbound.receipt, protocol_limits_);
    inbound.receipt_digest =
        sync_replica_file_delivery_receipt_digest_or_throw(
            inbound.receipt, protocol_limits_);
    if (projection_guard) {
        // Commit only after exact effect evidence and canonical receipt bytes
        // have been constructed. A failure before this point withholds the
        // receipt; immutable publication is reconciled by the next retry.
        projection_guard->commit_or_throw();
    }
    return inbound;
}

SyncReplicaFileDeliveryReceiptApplyResult
SyncReplicaFileDeliveryService::apply_receipt_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    const SyncReplicaFileDeliveryRequest& expected_request,
    std::string_view receipt_frame) {
    validate_channel_or_throw(channel_authority, "receipt application");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    validate_sync_replica_file_delivery_request_or_throw(
        expected_request, protocol_limits_);
    const SyncReplicaDeliveryRequest& evidence =
        expected_request.evidence_request;
    if (evidence.folder_id != folder_id_ ||
        evidence.sender_actor != local_actor_ ||
        evidence.receiver_actor != channel.peer_actor ||
        evidence.channel_binding != channel.binding) {
        throw std::runtime_error(
            label_ + " expected request does not bind this folder, peer, actor epoch, and channel");
    }

    const SyncReplicaFileDeliveryReceipt receipt =
        decode_sync_replica_file_delivery_receipt_or_throw(
            receipt_frame, protocol_limits_);
    validate_sync_replica_file_delivery_receipt_for_request_or_throw(
        receipt, expected_request, protocol_limits_);
    if (!sync_replica_file_delivery_receipt_is_effect_terminal(
            receipt.disposition)) {
        const std::uint64_t retry_delay =
            retry_delay_for_nonterminal_or_throw(
                receipt.disposition, retry_policy_);
        return map_release_result(
            replica_owner_.release_outbox_for_retry_or_throw(
                receipt.receiver_actor.device_id,
                receipt.operation_id,
                receipt.claim_id,
                retry_delay),
            receipt.disposition);
    }

    return map_settlement_result(replica_owner_.settle_outbox_or_throw(
        receipt.receiver_actor.device_id,
        receipt.operation_id,
        receipt.claim_id));
}

}  // namespace anonsync
