#include "sync_replica_reconciliation_service.hpp"

#if !defined(_WIN32)

#include "sha256_digest.hpp"
#include "sync_atomic_file_publication.hpp"
#include "sync_manifest_validation.hpp"

#include <algorithm>
#include <cstdint>
#include <limits>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {
namespace {

void increment_or_throw(
    std::uint64_t& value,
    const std::string& label) {
    if (value == std::numeric_limits<std::uint64_t>::max()) {
        throw std::overflow_error(label + " counter overflow");
    }
    ++value;
}

void add_or_throw(
    std::uint64_t& value,
    std::uint64_t added,
    const std::string& label) {
    if (added > std::numeric_limits<std::uint64_t>::max() - value) {
        throw std::overflow_error(label + " counter overflow");
    }
    value += added;
}

void count_admission_or_throw(
    SyncReplicaAdmission admission,
    SyncReplicaReconciliationApplyResult& result,
    const std::string& label) {
    switch (admission) {
        case SyncReplicaAdmission::InsertedActive:
            increment_or_throw(result.inserted_active, label + " active");
            return;
        case SyncReplicaAdmission::InsertedPending:
            increment_or_throw(result.inserted_pending, label + " pending");
            return;
        case SyncReplicaAdmission::InsertedQuarantined:
            increment_or_throw(
                result.inserted_quarantined, label + " quarantined");
            return;
        case SyncReplicaAdmission::Duplicate:
            increment_or_throw(
                result.duplicate_operations, label + " duplicate");
            return;
        case SyncReplicaAdmission::CapacityBlocked:
            return;
    }
    throw std::logic_error(label + " received an unknown admission result");
}

enum class ReceivedFilePayloadDisposition : std::uint8_t {
    Complete = 1U,
    Progress = 2U,
};

struct ReceivedFilePayloadResult final {
    ReceivedFilePayloadDisposition disposition =
        ReceivedFilePayloadDisposition::Complete;
    std::uint64_t next_offset_bytes = 0U;
};

template <typename Chunk>
[[nodiscard]] std::vector<std::uint64_t> chunk_offsets_or_throw(
    const std::vector<Chunk>& chunks,
    std::uint64_t total_size_bytes,
    const std::string& label) {
    if (chunks.empty()) {
        throw std::invalid_argument(label + " manifest must contain a chunk");
    }
    std::vector<std::uint64_t> offsets;
    offsets.reserve(chunks.size() + 1U);
    offsets.push_back(0U);
    std::uint64_t covered = 0U;
    for (const Chunk& chunk : chunks) {
        if (covered > total_size_bytes || chunk.size_bytes == 0U ||
            chunk.size_bytes > total_size_bytes - covered) {
            throw std::invalid_argument(
                label + " manifest chunk extent exceeds the payload");
        }
        covered += chunk.size_bytes;
        offsets.push_back(covered);
    }
    if (covered != total_size_bytes) {
        throw std::invalid_argument(
            label + " manifest chunks do not exactly cover the payload");
    }
    return offsets;
}

[[nodiscard]] std::size_t chunk_index_for_offset_or_throw(
    const std::vector<std::uint64_t>& offsets,
    std::uint64_t offset_bytes,
    std::uint64_t total_size_bytes,
    const std::string& label) {
    if (offsets.size() < 2U || offset_bytes >= total_size_bytes) {
        throw std::invalid_argument(
            label + " offset is outside the content-defined payload");
    }
    const auto upper = std::upper_bound(
        offsets.begin(), offsets.end(), offset_bytes);
    if (upper == offsets.begin() || upper == offsets.end()) {
        throw std::logic_error(
            label + " content-defined offsets lost their containing chunk");
    }
    return static_cast<std::size_t>(
        std::distance(offsets.begin(), upper) - 1);
}

// Incrementally extends the sorted digest lookup and cumulative-offset index
// shared by bounded same-path and cross-file projections. Keeping this in one
// implementation prevents the two delta paths from disagreeing about partial
// chunk authority, ordering, or source-extent accounting.
template <typename Projection>
void extend_content_defined_projection_index_or_throw(
    Projection& projected,
    const std::vector<SyncReplicaFilePayloadStoreContentDefinedChunk>& chunks,
    std::uint64_t source_size_bytes,
    const std::string& label) {
    if (projected.indexed_chunk_count > chunks.size() ||
        projected.chunk_offsets.size() !=
            projected.indexed_chunk_count + 1U ||
        projected.digest_order.size() != projected.indexed_chunk_count) {
        throw std::logic_error(
            label + " partial index lost its retained frontier");
    }
    while (projected.indexed_chunk_count < chunks.size()) {
        const std::size_t index = projected.indexed_chunk_count;
        const auto& chunk = chunks[index];
        const std::uint64_t prior = projected.chunk_offsets.back();
        if (prior > source_size_bytes || chunk.size_bytes == 0U ||
            chunk.size_bytes > source_size_bytes - prior) {
            throw std::logic_error(
                label + " partial chunk exceeds its source extent");
        }
        projected.chunk_offsets.push_back(prior + chunk.size_bytes);
        auto less_index = [&](std::size_t left, std::size_t right) {
            const auto& left_chunk = chunks[left];
            const auto& right_chunk = chunks[right];
            if (left_chunk.sha256 != right_chunk.sha256) {
                return left_chunk.sha256 < right_chunk.sha256;
            }
            if (left_chunk.size_bytes != right_chunk.size_bytes) {
                return left_chunk.size_bytes < right_chunk.size_bytes;
            }
            return left < right;
        };
        const auto position = std::lower_bound(
            projected.digest_order.begin(), projected.digest_order.end(),
            index, less_index);
        projected.digest_order.insert(position, index);
        ++projected.indexed_chunk_count;
    }
}

// Payload durability must precede operation admission. In particular, a
// verified partial range is useful resume state but is not authority to admit
// metadata that names a whole file which the receiver cannot yet materialize.
// Keeping that rule in one helper makes it difficult for future accounting or
// replay refactors to reintroduce the operation-ahead crash window.
[[nodiscard]] ReceivedFilePayloadResult receive_file_payload_or_throw(
    SyncReplicaFilePayloadStore& payload_store,
    const SyncReplicaOperation& operation,
    std::uint64_t offset_bytes,
    std::string chunk_sha256,
    std::string_view bytes,
    SyncReplicaReconciliationApplyResult& result,
    std::uint64_t& terminal_verification_steps_spent,
    std::uint64_t max_terminal_verification_steps_per_apply,
    const std::string& label) {
    const bool whole =
        offset_bytes == 0U &&
        static_cast<std::uint64_t>(bytes.size()) == operation.size_bytes;
    if (whole) {
        const SyncReplicaFilePayloadStorePutResult put =
            payload_store.put_payload_or_throw(std::string(bytes));
        if (put.content_sha256 != operation.content_sha256 ||
            put.size_bytes != operation.size_bytes) {
            throw std::logic_error(
                label + " payload store did not preserve response content identity");
        }
        switch (put.disposition) {
            case SyncReplicaFilePayloadStorePutDisposition::Inserted:
                increment_or_throw(
                    result.inserted_payloads,
                    label + " inserted payload");
                break;
            case SyncReplicaFilePayloadStorePutDisposition::AlreadyPresent:
                increment_or_throw(
                    result.existing_payloads,
                    label + " existing payload");
                break;
        }
        return {};
    }

    const bool defer_terminal_verification =
        terminal_verification_steps_spent >=
        max_terminal_verification_steps_per_apply;
    const SyncReplicaFilePayloadStoreStageResult staged =
        defer_terminal_verification
            ? payload_store.
                stage_payload_prefix_deferring_terminal_verification_or_throw(
                    operation.content_sha256, operation.size_bytes,
                    offset_bytes, std::move(chunk_sha256), bytes)
            : payload_store.stage_payload_prefix_or_throw(
                    operation.content_sha256, operation.size_bytes,
                    offset_bytes, std::move(chunk_sha256), bytes);
    increment_or_throw(
        result.staged_payload_ranges,
        label + " staged payload range");
    add_or_throw(
        result.staged_payload_bytes,
        staged.accepted_range_bytes,
        label + " staged payload bytes");
    add_or_throw(
        result.terminal_verification_steps,
        staged.terminal_verification_steps,
        label + " terminal verification steps");
    add_or_throw(
        terminal_verification_steps_spent,
        staged.terminal_verification_steps,
        label + " terminal verification step budget");
    if (terminal_verification_steps_spent >
        max_terminal_verification_steps_per_apply) {
        throw std::logic_error(
            label + " terminal verification crossed its per-apply step budget");
    }
    if (staged.content_sha256 != operation.content_sha256 ||
        staged.total_size_bytes != operation.size_bytes) {
        throw std::logic_error(
            label + " staged payload store lost content identity");
    }
    switch (staged.disposition) {
        case SyncReplicaFilePayloadStoreStageDisposition::Progress:
            return {
                ReceivedFilePayloadDisposition::Progress,
                staged.next_offset_bytes};
        case SyncReplicaFilePayloadStoreStageDisposition::CompletedInserted:
            increment_or_throw(
                result.inserted_payloads,
                label + " completed staged payload");
            return {};
        case SyncReplicaFilePayloadStoreStageDisposition::
            CompletedAlreadyPresent:
            increment_or_throw(
                result.existing_payloads,
                label + " existing staged payload");
            return {};
    }
    throw std::logic_error(
        label + " staged payload store returned an unknown disposition");
}

}  // namespace

std::string_view
sync_replica_reconciliation_source_manifest_projection_step_disposition_name(
    SyncReplicaReconciliationSourceManifestProjectionStepDisposition
        disposition) noexcept {
    switch (disposition) {
        case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                NoPendingWork:
            return "no_pending_work";
        case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                Progress:
            return "progress";
        case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                Completed:
            return "completed";
        case SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                PayloadUnavailable:
            return "payload_unavailable";
    }
    return "unknown";
}

SyncReplicaReconciliationServeSession::
    SyncReplicaReconciliationServeSession(
        std::string folder_id,
        SyncReplicaActor local_actor,
        SyncReplicaActor peer_actor,
        SyncReplicaDeliveryChannelBinding channel_binding)
    : folder_id_(std::move(folder_id)),
      local_actor_(std::move(local_actor)),
      peer_actor_(std::move(peer_actor)),
      channel_binding_(std::move(channel_binding)) {}

SyncReplicaReconciliationService::SyncReplicaReconciliationService(
    SyncReplicaSqliteOwner& owner,
    SyncReplicaFilePayloadStore& payload_store,
    SyncReplicaReconciliationProtocolLimits limits,
    std::string label,
    SyncReplicaSelectiveSyncPolicy selective_sync_policy,
    std::uint64_t max_local_reuse_bytes_per_apply,
    std::uint64_t max_predecessor_projection_bytes_per_apply,
    std::uint64_t max_terminal_verification_steps_per_apply,
    std::uint64_t max_source_manifest_projection_bytes_per_request)
    : owner_(owner),
      payload_store_(payload_store),
      protocol_limits_(std::move(limits)),
      max_local_reuse_bytes_per_apply_(max_local_reuse_bytes_per_apply),
      max_predecessor_projection_bytes_per_apply_(
          max_predecessor_projection_bytes_per_apply),
      max_terminal_verification_steps_per_apply_(
          max_terminal_verification_steps_per_apply),
      max_source_manifest_projection_bytes_per_request_(
          max_source_manifest_projection_bytes_per_request),
      label_(std::move(label)),
      selective_sync_policy_(std::move(selective_sync_policy)) {
    if (label_.empty()) {
        throw std::invalid_argument(
            "sync replica reconciliation service label must not be empty");
    }
    validate_sync_replica_reconciliation_protocol_limits_or_throw(
        protocol_limits_);
    if (max_local_reuse_bytes_per_apply_ == 0U ||
        max_local_reuse_bytes_per_apply_ >
            kSyncReplicaReconciliationMaximumLocalReuseBytesPerApply) {
        throw std::invalid_argument(
            label_ +
            " local reuse byte frontier must be in [1, shipping maximum]");
    }
    if (max_predecessor_projection_bytes_per_apply_ == 0U ||
        max_predecessor_projection_bytes_per_apply_ >
            kSyncReplicaReconciliationMaximumPredecessorProjectionBytesPerApply) {
        throw std::invalid_argument(
            label_ +
            " predecessor projection byte frontier must be in [1, shipping maximum]");
    }
    if (max_terminal_verification_steps_per_apply_ == 0U ||
        max_terminal_verification_steps_per_apply_ >
            kSyncReplicaReconciliationMaximumTerminalVerificationStepsPerApply) {
        throw std::invalid_argument(
            label_ +
            " terminal verification step frontier must be in [1, shipping maximum]");
    }
    if (max_source_manifest_projection_bytes_per_request_ == 0U ||
        max_source_manifest_projection_bytes_per_request_ >
            kSyncReplicaReconciliationMaximumSourceManifestProjectionBytesPerRequest) {
        throw std::invalid_argument(
            label_ +
            " source manifest projection byte frontier must be in [1, shipping maximum]");
    }
    const SyncReplicaSqliteIdentityCutpoint identity =
        owner_.identity_cutpoint_or_throw();
    folder_id_ = identity.folder_id;
    local_actor_ = identity.local_actor;
    if (!sync_id_is_valid(folder_id_) ||
        !sync_id_is_valid(local_actor_.device_id) ||
        local_actor_.epoch == 0U) {
        throw std::logic_error(label_ + " owner identity is invalid");
    }
    if (payload_store_.folder_id() != folder_id_) {
        throw std::invalid_argument(
            label_ + " payload store belongs to another folder");
    }
    validate_sync_replica_selective_sync_policy_or_throw(
        selective_sync_policy_, label_ + " selective-sync policy");
    const SyncReplicaModelLimits& durable_model = identity.limits.model;
    const SyncReplicaModelLimits& wire_model = protocol_limits_.model;
    if (wire_model.max_operations < durable_model.max_operations ||
        wire_model.max_context_entries < durable_model.max_context_entries ||
        wire_model.max_predecessor_ids < durable_model.max_predecessor_ids ||
        wire_model.max_canonical_operation_bytes <
            durable_model.max_canonical_operation_bytes ||
        wire_model.max_retained_canonical_bytes <
            durable_model.max_retained_canonical_bytes ||
        wire_model.max_retained_context_entries <
            durable_model.max_retained_context_entries ||
        wire_model.max_retained_predecessor_ids <
            durable_model.max_retained_predecessor_ids) {
        throw std::invalid_argument(
            label_ + " wire model limits do not cover every operation retained by the owner");
    }
    if (protocol_limits_.max_payload_extent_bytes <
        payload_store_.limits().max_payload_bytes) {
        throw std::invalid_argument(
            label_ + " wire payload extent cannot describe every payload admitted by the store");
    }
}

void SyncReplicaReconciliationService::
require_current_owner_identity_or_throw(
    const std::string& operation_label) {
    const SyncReplicaSqliteIdentityCutpoint cutpoint =
        owner_.identity_cutpoint_or_throw();
    if (cutpoint.folder_id != folder_id_ ||
        cutpoint.local_actor != local_actor_) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " owner identity changed after service construction");
    }
    if (payload_store_.folder_id() != folder_id_) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " payload store identity changed after service construction");
    }
}

void SyncReplicaReconciliationService::validate_channel_or_throw(
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

void SyncReplicaReconciliationService::validate_serve_session_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    const SyncReplicaReconciliationServeSession& session,
    const std::string& operation_label) const {
    validate_channel_or_throw(channel_authority, operation_label);
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    if (session.folder_id_ != folder_id_ ||
        session.local_actor_ != local_actor_ ||
        session.peer_actor_ != channel.peer_actor ||
        session.channel_binding_ != channel.binding) {
        throw std::invalid_argument(
            label_ + " " + operation_label +
            " serve session does not bind this folder, actors, and channel");
    }
}

SyncReplicaReconciliationSourceManifestProjectionStatus
SyncReplicaReconciliationService::source_manifest_projection_status() const {
    SyncReplicaReconciliationSourceManifestProjectionStatus status;
    if (!source_content_defined_projection_.has_value()) return status;
    const SourceContentDefinedProjection& source =
        *source_content_defined_projection_;
    if (!source.projection.active()) {
        throw std::logic_error(
            label_ + " retained an inactive source manifest projection");
    }
    status.pending = true;
    status.operation_id = source.source_operation.operation_id;
    status.content_sha256 = source.content_sha256;
    status.total_size_bytes = source.total_size_bytes;
    status.next_offset_bytes = source.projection.next_offset_bytes();
    status.completed_chunk_count = static_cast<std::uint64_t>(
        source.projection.completed_chunks().size());
    if (status.operation_id.empty() || status.content_sha256.empty() ||
        status.total_size_bytes == 0U ||
        status.next_offset_bytes >= status.total_size_bytes) {
        throw std::logic_error(
            label_ + " retained an invalid source manifest projection");
    }
    return status;
}

SyncReplicaReconciliationSourceManifestCacheStatus
SyncReplicaReconciliationService::source_manifest_cache_status() const {
    SyncReplicaReconciliationSourceManifestCacheStatus status;
    status.complete_checkpoint_restorations =
        source_manifest_complete_checkpoint_restorations_;
    status.terminal_releases = source_manifest_cache_terminal_releases_;
    status.terminal_released_capacity_bytes =
        source_manifest_cache_terminal_released_capacity_bytes_;
    if (!source_content_defined_manifest_.has_value()) return status;

    const CachedSourceContentDefinedManifest& source =
        *source_content_defined_manifest_;
    status.resident = true;
    status.operation_id = source.operation_id;
    status.canonical_path = source.canonical_path;
    status.content_sha256 = source.content_sha256;
    status.total_size_bytes = source.total_size_bytes;
    status.manifest_digest = source.manifest_digest;
    status.chunk_count = static_cast<std::uint64_t>(
        source.manifest.chunk_count());
    status.retained_chunk_capacity_bytes =
        source.manifest.retained_chunk_capacity_bytes();
    status.exact_complete_checkpoint_durable =
        !pending_source_manifest_checkpoint_.has_value() &&
        source_durable_checkpoint_complete_ &&
        source_durable_checkpoint_operation_id_ == source.operation_id &&
        source_durable_checkpoint_next_offset_bytes_ ==
            source.total_size_bytes &&
        source_durable_checkpoint_manifest_digest_ == source.manifest_digest;
    if (status.operation_id.empty() || status.canonical_path.empty() ||
        status.content_sha256.empty() || status.total_size_bytes == 0U ||
        status.manifest_digest.empty() || status.chunk_count == 0U ||
        status.retained_chunk_capacity_bytes == 0U) {
        throw std::logic_error(
            label_ + " retained an invalid completed source manifest cache");
    }
    return status;
}

void SyncReplicaReconciliationService::
install_source_content_defined_checkpoint_for_operation_or_throw(
    SyncReplicaSourceManifestCheckpoint checkpoint,
    const SyncReplicaOperation& operation,
    const SyncReplicaContentDefinedChunkingParameters& parameters,
    std::string_view operation_label_view) {
    const std::string operation_label(operation_label_view);
    if (operation_label.empty()) {
        throw std::invalid_argument(
            "source manifest checkpoint installation label must not be empty");
    }
    if (checkpoint.operation_id != operation.operation_id ||
        checkpoint.canonical_path != operation.canonical_path ||
        checkpoint.content_sha256 != operation.content_sha256 ||
        checkpoint.total_size_bytes != operation.size_bytes ||
        checkpoint.parameters != parameters) {
        throw std::invalid_argument(
            label_ + " " + operation_label +
            " checkpoint does not bind the exact retained file operation");
    }

    source_durable_checkpoint_operation_id_ = checkpoint.operation_id;
    source_durable_checkpoint_next_offset_bytes_ =
        checkpoint.next_offset_bytes;
    source_durable_checkpoint_complete_ =
        checkpoint.disposition ==
        SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest;
    source_durable_checkpoint_manifest_digest_ =
        source_durable_checkpoint_complete_ ? checkpoint.manifest_digest
                                            : std::string{};

    if (checkpoint.disposition ==
        SyncReplicaSourceManifestCheckpointDisposition::ActiveProjection) {
        SyncReplicaFilePayloadStoreContentDefinedProjectionCheckpoint restored;
        restored.content_sha256 = checkpoint.content_sha256;
        restored.total_size_bytes = checkpoint.total_size_bytes;
        restored.metadata = checkpoint.payload_metadata;
        restored.parameters = checkpoint.parameters;
        restored.next_offset_bytes = checkpoint.next_offset_bytes;
        restored.completed_chunk_bytes = checkpoint.completed_chunk_bytes;
        restored.whole_hash = checkpoint.whole_hash;
        restored.current_chunk_hash = checkpoint.current_chunk_hash;
        restored.chunker = checkpoint.chunker;
        restored.completed_chunks.reserve(checkpoint.chunks.size());
        for (auto& chunk : checkpoint.chunks) {
            restored.completed_chunks.emplace_back(
                chunk.size_bytes, chunk.sha256);
        }
        SyncReplicaFilePayloadStoreContentDefinedProjection projection;
        projection.restore_checkpoint_or_throw(
            std::move(restored),
            label_ + " " + operation_label + " durable byte-frontier restore");
        source_content_defined_manifest_.reset();
        source_content_defined_projection_ = SourceContentDefinedProjection{
            operation,
            checkpoint.content_sha256,
            checkpoint.total_size_bytes,
            checkpoint.payload_metadata,
            checkpoint.parameters,
            std::move(projection)};
        return;
    }

    if (checkpoint.disposition !=
        SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " parsed checkpoint has an unsupported disposition");
    }
    SyncReplicaReconciliationDeltaManifest manifest;
    manifest.parameters = checkpoint.parameters;
    manifest.chunks.reserve(checkpoint.chunks.size());
    for (auto& chunk : checkpoint.chunks) {
        manifest.chunks.emplace_back(chunk.size_bytes, chunk.sha256);
    }
    SyncReplicaReconciliationCompactManifest compact_manifest =
        SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
            operation.size_bytes, manifest,
            label_ + " " + operation_label + " restored compact manifest");
    const std::string manifest_digest =
        sync_replica_reconciliation_delta_manifest_digest_or_throw(
            operation.content_sha256, operation.size_bytes, manifest);
    if (manifest_digest != checkpoint.manifest_digest) {
        // The payload-store codec intentionally does not depend on wire
        // framing. A syntactically sound but semantically mismatched optional
        // record is ignored and replaced by an ordinary fresh projection.
        source_durable_checkpoint_operation_id_.clear();
        source_durable_checkpoint_next_offset_bytes_ = 0U;
        source_durable_checkpoint_complete_ = false;
        source_durable_checkpoint_manifest_digest_.clear();
        return;
    }
    source_content_defined_projection_.reset();
    std::uint64_t next_complete_checkpoint_restorations =
        source_manifest_complete_checkpoint_restorations_;
    increment_or_throw(
        next_complete_checkpoint_restorations,
        label_ + " complete source manifest checkpoint restorations");
    source_content_defined_manifest_ = CachedSourceContentDefinedManifest{
        operation.operation_id,
        operation.canonical_path,
        checkpoint.content_sha256,
        checkpoint.total_size_bytes,
        checkpoint.payload_metadata,
        manifest_digest,
        std::move(compact_manifest)};
    source_manifest_complete_checkpoint_restorations_ =
        next_complete_checkpoint_restorations;
}

void SyncReplicaReconciliationService::
restore_source_content_defined_checkpoint_for_operation_or_throw(
    const SyncReplicaOperation& operation,
    const SyncReplicaContentDefinedChunkingParameters& parameters,
    std::string_view operation_label_view) {
    const std::string operation_label(operation_label_view);
    if (operation_label.empty()) {
        throw std::invalid_argument(
            "source manifest checkpoint restore label must not be empty");
    }
    if ((source_content_defined_manifest_.has_value() &&
         source_content_defined_manifest_->content_sha256 ==
             operation.content_sha256 &&
         source_content_defined_manifest_->total_size_bytes ==
             operation.size_bytes &&
         source_content_defined_manifest_->manifest.parameters() == parameters) ||
        (source_content_defined_projection_.has_value() &&
         source_content_defined_projection_->content_sha256 ==
             operation.content_sha256 &&
         source_content_defined_projection_->total_size_bytes ==
             operation.size_bytes &&
         source_content_defined_projection_->parameters == parameters)) {
        return;
    }

    source_durable_checkpoint_operation_id_.clear();
    source_durable_checkpoint_next_offset_bytes_ = 0U;
    source_durable_checkpoint_complete_ = false;
    source_durable_checkpoint_manifest_digest_.clear();

    std::optional<SyncReplicaSourceManifestCheckpoint> checkpoint;
    try {
        checkpoint =
            payload_store_.load_source_manifest_checkpoint_or_none_or_throw(
                label_ + " " + operation_label + " durable checkpoint load");
    } catch (const SyncReplicaFilePayloadStoreLeaseBusyError&) {
        // Checkpoint hydration is optional acceleration. A concurrent writer
        // must not make authenticated source bytes unavailable; the ordinary
        // exact payload open below remains the authority and a later turn can
        // retry the durable observation.
        return;
    }
    if (!checkpoint.has_value() ||
        checkpoint->operation_id != operation.operation_id ||
        checkpoint->canonical_path != operation.canonical_path ||
        checkpoint->content_sha256 != operation.content_sha256 ||
        checkpoint->total_size_bytes != operation.size_bytes ||
        checkpoint->parameters != parameters) {
        return;
    }
    install_source_content_defined_checkpoint_for_operation_or_throw(
        std::move(*checkpoint), operation, parameters, operation_label);
}

void SyncReplicaReconciliationService::
restore_source_content_defined_checkpoint_without_peer_or_throw() {
    if (source_durable_checkpoint_scheduler_restore_attempted_ ||
        source_content_defined_projection_.has_value() ||
        source_content_defined_manifest_.has_value()) {
        return;
    }
    source_durable_checkpoint_scheduler_restore_attempted_ = true;

    std::optional<SyncReplicaSourceManifestCheckpoint> checkpoint;
    try {
        checkpoint =
            payload_store_.load_source_manifest_checkpoint_or_none_or_throw(
                label_ + " source-local durable checkpoint discovery");
    } catch (const SyncReplicaFilePayloadStoreLeaseBusyError&) {
        // The scheduler may retry a temporary store writer conflict. No source
        // or replica authority has been consumed.
        source_durable_checkpoint_scheduler_restore_attempted_ = false;
        return;
    }
    if (!checkpoint.has_value()) return;

    const SyncReplicaSqliteTargetedPathCutpoint cutpoint =
        owner_.targeted_path_cutpoint_or_throw(
            checkpoint->canonical_path, checkpoint->operation_id);
    const SyncReplicaOperation* operation =
        cutpoint.requested_retained_operation_or_none();
    if (operation == nullptr ||
        operation->kind != SyncReplicaValueKind::File ||
        operation->operation_id != checkpoint->operation_id ||
        operation->canonical_path != checkpoint->canonical_path ||
        operation->content_sha256 != checkpoint->content_sha256 ||
        operation->size_bytes != checkpoint->total_size_bytes ||
        operation->size_bytes == 0U) {
        return;
    }
    const SyncReplicaContentDefinedChunkingParameters parameters =
        sync_replica_reconciliation_content_defined_parameters_or_throw(
            operation->size_bytes);
    if (parameters != checkpoint->parameters) return;
    install_source_content_defined_checkpoint_for_operation_or_throw(
        std::move(*checkpoint), *operation, parameters,
        "source-local path-bound checkpoint restore");
}

SyncReplicaReconciliationSourceManifestProjectionStatus
SyncReplicaReconciliationService::
discover_source_manifest_projection_or_throw() {
    require_current_owner_identity_or_throw(
        "source-local durable checkpoint discovery");
    // Completion clears the process-local projection before the optional
    // checkpoint publication runs. A typed atomic-publication or lease-busy
    // failure can therefore leave only this bounded candidate. Retry it from
    // the peer-independent owner cutpoint before asking whether hash work is
    // pending; otherwise a completed manifest could remain restart-cold until
    // another authenticated request happened to call the continuation path.
    publish_pending_source_manifest_checkpoint_if_possible_or_throw(
        "source-local pending checkpoint discovery publication");
    restore_source_content_defined_checkpoint_without_peer_or_throw();
    return source_manifest_projection_status();
}

SyncReplicaReconciliationService::SourceContentDefinedProjectionAdvance
SyncReplicaReconciliationService::
advance_source_content_defined_projection_or_throw(
    const SyncReplicaOperation& operation,
    SyncReplicaFilePayloadStoreOpenedPayload& opened,
    std::string_view operation_label_view) {
    const std::string operation_label(operation_label_view);
    if (opened.content_sha256() != operation.content_sha256 ||
        opened.size_bytes() != operation.size_bytes) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " targeted source payload lost exact content identity");
    }
    const SyncReplicaContentDefinedChunkingParameters parameters =
        sync_replica_reconciliation_content_defined_parameters_or_throw(
            operation.size_bytes);
    const SyncPosixRegularFileSnapshotMetadata source_metadata =
        opened.metadata();
    SourceContentDefinedProjectionAdvance result;
    const bool projection_matches =
        source_content_defined_projection_.has_value() &&
        source_content_defined_projection_->content_sha256 ==
            operation.content_sha256 &&
        source_content_defined_projection_->total_size_bytes ==
            operation.size_bytes &&
        source_content_defined_projection_->parameters == parameters &&
        source_content_defined_projection_->source_metadata == source_metadata;
    if (!projection_matches) {
        result.projection_restarted =
            source_content_defined_projection_.has_value();
        // A changed exact payload observation revokes the restored durable
        // frontier even when the digest-named bytes are still expected to be
        // identical. Otherwise a lower fresh boundary could be suppressed
        // until it surpassed stale progress from the replaced inode, turning
        // an optional checkpoint into restart amplification.
        source_durable_checkpoint_operation_id_.clear();
        source_durable_checkpoint_next_offset_bytes_ = 0U;
        source_durable_checkpoint_complete_ = false;
        source_durable_checkpoint_manifest_digest_.clear();
        source_content_defined_projection_ = SourceContentDefinedProjection{
            operation,
            operation.content_sha256,
            operation.size_bytes,
            source_metadata,
            parameters,
            SyncReplicaFilePayloadStoreContentDefinedProjection{}};
    } else {
        // The projection is content-scoped, but retain the newest exact causal
        // operation as the targeted-open witness for a later source-local
        // pulse. This does not alter already hashed bytes.
        source_content_defined_projection_->source_operation = operation;
    }

    SyncReplicaFilePayloadStoreContentDefinedProjectionStep projection_step =
        opened.advance_content_defined_projection_or_throw(
            source_content_defined_projection_->projection,
            parameters,
            max_source_manifest_projection_bytes_per_request_,
            label_ + " " + operation_label);
    result.hashed_bytes = projection_step.hashed_bytes;
    result.newly_completed_chunk_count =
        projection_step.newly_completed_chunk_count;

    if (!projection_step.completed_manifest.has_value()) {
        auto projection_checkpoint =
            source_content_defined_projection_->projection.checkpoint();
        std::uint64_t retained_checkpoint_frontier = 0U;
        bool retained_checkpoint_matches = false;
        if (source_durable_checkpoint_operation_id_ == operation.operation_id &&
            !source_durable_checkpoint_complete_) {
            retained_checkpoint_frontier =
                source_durable_checkpoint_next_offset_bytes_;
            retained_checkpoint_matches = true;
        }
        if (pending_source_manifest_checkpoint_.has_value() &&
            pending_source_manifest_checkpoint_->operation_id ==
                operation.operation_id &&
            pending_source_manifest_checkpoint_->disposition ==
                SyncReplicaSourceManifestCheckpointDisposition::
                    ActiveProjection) {
            retained_checkpoint_frontier = std::max(
                retained_checkpoint_frontier,
                pending_source_manifest_checkpoint_->next_offset_bytes);
            retained_checkpoint_matches = true;
        }
        const bool interval_due =
            projection_checkpoint.next_offset_bytes >
                retained_checkpoint_frontier &&
            projection_checkpoint.next_offset_bytes -
                    retained_checkpoint_frontier >=
                kSyncReplicaReconciliationSourceManifestCheckpointPublicationIntervalBytes;
        const bool checkpoint_needs_publication =
            !retained_checkpoint_matches ||
            source_durable_checkpoint_complete_ || interval_due;
        if (checkpoint_needs_publication) {
            SyncReplicaSourceManifestCheckpoint checkpoint;
            checkpoint.operation_id = operation.operation_id;
            checkpoint.canonical_path = operation.canonical_path;
            checkpoint.content_sha256 = operation.content_sha256;
            checkpoint.total_size_bytes = operation.size_bytes;
            checkpoint.payload_metadata = projection_checkpoint.metadata;
            checkpoint.parameters = projection_checkpoint.parameters;
            checkpoint.disposition =
                SyncReplicaSourceManifestCheckpointDisposition::
                    ActiveProjection;
            checkpoint.next_offset_bytes =
                projection_checkpoint.next_offset_bytes;
            checkpoint.completed_chunk_bytes =
                projection_checkpoint.completed_chunk_bytes;
            checkpoint.whole_hash = projection_checkpoint.whole_hash;
            checkpoint.current_chunk_hash =
                projection_checkpoint.current_chunk_hash;
            checkpoint.chunker = projection_checkpoint.chunker;
            checkpoint.chunks.reserve(
                projection_checkpoint.completed_chunks.size());
            for (auto& chunk : projection_checkpoint.completed_chunks) {
                checkpoint.chunks.emplace_back(
                    chunk.size_bytes, chunk.sha256);
            }
            // Publication is deferred until the caller has released every
            // opened payload descriptor retained for this response. This keeps
            // the global-store -> payload-inode lock order exact and avoids a
            // second targeted open on the completing request.
            pending_source_manifest_checkpoint_ = std::move(checkpoint);
        }
        return result;
    }

    if (!projection_step.completed_whole_hash.has_value()) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " completed source projection lacks its whole-hash checkpoint");
    }
    SyncReplicaFilePayloadStoreContentDefinedManifest projected =
        std::move(*projection_step.completed_manifest);
    source_content_defined_projection_.reset();
    if (projected.content_sha256 != operation.content_sha256 ||
        projected.total_size_bytes != operation.size_bytes ||
        projected.parameters != parameters) {
        throw std::logic_error(
            label_ + " " + operation_label +
            " content-defined projection lost exact payload identity");
    }

    SyncReplicaSourceManifestCheckpoint checkpoint;
    checkpoint.operation_id = operation.operation_id;
    checkpoint.canonical_path = operation.canonical_path;
    checkpoint.content_sha256 = operation.content_sha256;
    checkpoint.total_size_bytes = operation.size_bytes;
    checkpoint.payload_metadata = source_metadata;
    checkpoint.parameters = parameters;
    checkpoint.disposition =
        SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest;
    checkpoint.next_offset_bytes = operation.size_bytes;
    checkpoint.completed_chunk_bytes = operation.size_bytes;
    checkpoint.whole_hash = *projection_step.completed_whole_hash;
    checkpoint.current_chunk_hash = ResumableSha256{}.checkpoint();
    checkpoint.chunker = {
        0U, 0U,
        static_cast<std::uint64_t>(projected.chunks.size()), true};
    checkpoint.chunks.reserve(projected.chunks.size());

    SyncReplicaReconciliationDeltaManifest manifest;
    manifest.parameters = projected.parameters;
    manifest.chunks.reserve(projected.chunks.size());
    for (auto& chunk : projected.chunks) {
        checkpoint.chunks.emplace_back(chunk.size_bytes, chunk.sha256);
        manifest.chunks.emplace_back(chunk.size_bytes, chunk.sha256);
    }
    SyncReplicaReconciliationCompactManifest compact_manifest =
        SyncReplicaReconciliationCompactManifest::from_manifest_or_throw(
            operation.size_bytes, manifest,
            label_ + " " + operation_label + " compact manifest");
    const std::string manifest_digest =
        sync_replica_reconciliation_delta_manifest_digest_or_throw(
            operation.content_sha256, operation.size_bytes, manifest);
    checkpoint.manifest_digest = manifest_digest;
    source_content_defined_manifest_ = CachedSourceContentDefinedManifest{
        operation.operation_id,
        operation.canonical_path,
        operation.content_sha256,
        operation.size_bytes,
        source_metadata,
        manifest_digest,
        std::move(compact_manifest)};

    pending_source_manifest_checkpoint_ = std::move(checkpoint);
    result.completed = true;
    return result;
}

void SyncReplicaReconciliationService::
publish_pending_source_manifest_checkpoint_if_possible_or_throw(
    std::string_view operation_label_view) {
    if (!pending_source_manifest_checkpoint_.has_value()) return;
    const std::string operation_label(operation_label_view);
    if (operation_label.empty()) {
        throw std::invalid_argument(
            "source manifest checkpoint publication label must not be empty");
    }
    try {
        SyncReplicaSourceManifestCheckpoint& committed =
            *pending_source_manifest_checkpoint_;
        payload_store_.publish_source_manifest_checkpoint_or_throw(
            committed, label_ + " " + operation_label);
        source_durable_checkpoint_operation_id_ = committed.operation_id;
        source_durable_checkpoint_next_offset_bytes_ =
            committed.next_offset_bytes;
        source_durable_checkpoint_complete_ =
            committed.disposition ==
            SyncReplicaSourceManifestCheckpointDisposition::CompleteManifest;
        source_durable_checkpoint_manifest_digest_ =
            source_durable_checkpoint_complete_ ? committed.manifest_digest
                                                : std::string{};
        pending_source_manifest_checkpoint_.reset();
    } catch (const SyncReplicaFilePayloadStoreLeaseBusyError&) {
        // In-place publication leaves the same bounded caller-owned candidate
        // intact for a later owner turn. The durable frontier is deliberately
        // not advanced here.
    } catch (const SyncAtomicFilePublicationError&) {
        // This record is restart acceleration, never source-byte or transfer
        // authority. A typed not-published or durability-indeterminate atomic
        // failure therefore retains the bounded candidate for a later turn but
        // must not make an already re-proved payload unavailable. Identity,
        // rooted-reproof, codec, and logic failures remain terminal because
        // they do not cross this typed publication boundary.
    }
}

std::uint64_t SyncReplicaReconciliationService::
release_terminal_source_manifest_cache_if_possible_or_throw(
    const SyncReplicaOperation& operation) {
    if (!source_content_defined_manifest_.has_value() ||
        pending_source_manifest_checkpoint_.has_value()) {
        return 0U;
    }
    const CachedSourceContentDefinedManifest& source =
        *source_content_defined_manifest_;
    if (source.operation_id != operation.operation_id ||
        source.canonical_path != operation.canonical_path ||
        source.content_sha256 != operation.content_sha256 ||
        source.total_size_bytes != operation.size_bytes ||
        !source_durable_checkpoint_complete_ ||
        source_durable_checkpoint_operation_id_ != operation.operation_id ||
        source_durable_checkpoint_next_offset_bytes_ != operation.size_bytes ||
        source_durable_checkpoint_manifest_digest_ != source.manifest_digest) {
        return 0U;
    }

    const std::uint64_t released_capacity =
        source.manifest.retained_chunk_capacity_bytes();
    if (released_capacity == 0U) {
        throw std::logic_error(
            label_ + " terminal source manifest cache has no retained chunks");
    }
    std::uint64_t next_release_count =
        source_manifest_cache_terminal_releases_;
    std::uint64_t next_released_capacity =
        source_manifest_cache_terminal_released_capacity_bytes_;
    increment_or_throw(
        next_release_count,
        label_ + " terminal source manifest cache releases");
    add_or_throw(
        next_released_capacity, released_capacity,
        label_ + " terminal source manifest cache released capacity");
    source_content_defined_manifest_.reset();
    source_manifest_cache_terminal_releases_ = next_release_count;
    source_manifest_cache_terminal_released_capacity_bytes_ =
        next_released_capacity;
    return released_capacity;
}

SyncReplicaReconciliationSourceManifestProjectionStepResult
SyncReplicaReconciliationService::
continue_source_manifest_projection_or_throw() {
    if (pending_source_manifest_checkpoint_.has_value()) {
        require_current_owner_identity_or_throw(
            "source-local checkpoint publication");
        publish_pending_source_manifest_checkpoint_if_possible_or_throw(
            "source-local pending checkpoint publication");
    }
    restore_source_content_defined_checkpoint_without_peer_or_throw();
    SyncReplicaReconciliationSourceManifestProjectionStepResult result;
    result.before = source_manifest_projection_status();
    if (!result.before.pending) {
        result.after = result.before;
        return result;
    }

    require_current_owner_identity_or_throw(
        "source-local manifest projection");
    const SyncReplicaOperation operation =
        source_content_defined_projection_->source_operation;
    SyncReplicaFilePayloadStoreTargetedAccess payload_access =
        payload_store_.begin_targeted_access_or_throw(
            label_ + " source-local manifest projection access");
    std::optional<SyncReplicaFilePayloadStoreOpenedPayload> opened =
        payload_access.open_optional_payload_for_operation_or_throw(
            operation,
            label_ + " source-local manifest projection payload");
    if (!opened.has_value()) {
        source_content_defined_projection_.reset();
        result.disposition =
            SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
                PayloadUnavailable;
        result.after = source_manifest_projection_status();
        return result;
    }

    const SourceContentDefinedProjectionAdvance advanced =
        advance_source_content_defined_projection_or_throw(
            operation, *opened,
            "bounded source-local content-defined projection");
    result.hashed_bytes = advanced.hashed_bytes;
    result.newly_completed_chunk_count =
        advanced.newly_completed_chunk_count;
    result.projection_restarted = advanced.projection_restarted;
    opened.reset();
    publish_pending_source_manifest_checkpoint_if_possible_or_throw(
        "source-local exact-frontier publication");
    result.disposition = advanced.completed
        ? SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
              Completed
        : SyncReplicaReconciliationSourceManifestProjectionStepDisposition::
              Progress;
    result.after = source_manifest_projection_status();
    return result;
}

SyncReplicaReconciliationServeSession
SyncReplicaReconciliationService::make_serve_session_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority) {
    validate_channel_or_throw(channel_authority, "serve-session creation");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    return SyncReplicaReconciliationServeSession(
        folder_id_, local_actor_, channel.peer_actor, channel.binding);
}

SyncReplicaOutboundReconciliation
SyncReplicaReconciliationService::make_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::optional<std::string> after_operation_id,
    std::optional<std::string> expected_source_evidence_set_digest,
    std::optional<SyncReplicaReconciliationPayloadContinuation>
        payload_continuation) {
    validate_channel_or_throw(channel_authority, "outbound request");
    require_current_owner_identity_or_throw("outbound request");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();

    SyncReplicaReconciliationRequest request;
    request.folder_id = folder_id_;
    request.requester_actor = local_actor_;
    request.responder_actor = channel.peer_actor;
    request.channel_binding = channel.binding;
    request.after_operation_id = std::move(after_operation_id);
    request.expected_source_evidence_set_digest =
        std::move(expected_source_evidence_set_digest);
    request.payload_continuation = std::move(payload_continuation);
    if (request.payload_continuation.has_value() &&
        request.payload_continuation->next_offset_bytes <
            request.payload_continuation->total_size_bytes &&
        delta_target_manifest_.has_value() &&
        delta_target_manifest_->operation_id ==
            request.payload_continuation->operation_id &&
        delta_target_manifest_->content_sha256 ==
            request.payload_continuation->content_sha256 &&
        delta_target_manifest_->total_size_bytes ==
            request.payload_continuation->total_size_bytes) {
        request.cached_delta_manifest_digest =
            delta_target_manifest_->manifest_digest;
    }
    request.selective_sync_policy = selective_sync_policy_;
    std::string frame =
        encode_sync_replica_reconciliation_request_or_throw(
            request, protocol_limits_);
    const std::string digest =
        sync_replica_reconciliation_request_digest_or_throw(
            request, protocol_limits_);
    return {std::move(request), std::move(frame), digest};
}

SyncReplicaInboundReconciliation
SyncReplicaReconciliationService::serve_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string_view request_frame) {
    SyncReplicaReconciliationServeSession session =
        make_serve_session_or_throw(channel_authority);
    return serve_request_or_throw(
        channel_authority, request_frame, session);
}

SyncReplicaInboundReconciliation
SyncReplicaReconciliationService::serve_request_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string_view request_frame,
    SyncReplicaReconciliationServeSession& session) {
    SyncReplicaFramedInboundReconciliation framed =
        serve_request_frame_or_throw(
            channel_authority, request_frame, session);
    SyncReplicaReconciliationResponse response =
        decode_sync_replica_reconciliation_response_or_throw(
            framed.response_frame, protocol_limits_);
    validate_sync_replica_reconciliation_response_for_request_or_throw(
        response, framed.request, protocol_limits_);
    return {
        std::move(framed.request), std::move(response),
        std::move(framed.response_frame)};
}

SyncReplicaFramedInboundReconciliation
SyncReplicaReconciliationService::serve_request_frame_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string_view request_frame) {
    SyncReplicaReconciliationServeSession session =
        make_serve_session_or_throw(channel_authority);
    return serve_request_frame_or_throw(
        channel_authority, request_frame, session);
}

SyncReplicaFramedInboundReconciliation
SyncReplicaReconciliationService::serve_request_frame_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    std::string_view request_frame,
    SyncReplicaReconciliationServeSession& session) {
    validate_serve_session_or_throw(
        channel_authority, session, "inbound request");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    SyncReplicaReconciliationRequest request =
        decode_sync_replica_reconciliation_request_or_throw(
            request_frame, protocol_limits_);
    if (request.folder_id != folder_id_ ||
        request.requester_actor != channel.peer_actor ||
        request.responder_actor != local_actor_ ||
        request.channel_binding != channel.binding) {
        throw std::runtime_error(
            label_ + " inbound reconciliation request does not bind this folder, peer, actor epoch, and channel");
    }
    publish_pending_source_manifest_checkpoint_if_possible_or_throw(
        "pre-request source manifest checkpoint publication");

    const bool terminal_verification_request =
        request.payload_continuation.has_value() &&
        request.payload_continuation->next_offset_bytes ==
            request.payload_continuation->total_size_bytes;
    const SyncReplicaSqliteEvidencePage page = owner_.evidence_page_or_throw(
        request.after_operation_id,
        request.expected_source_evidence_set_digest,
        {request.payload_continuation.has_value()
             ? 1U
             : protocol_limits_.max_operations_per_page,
         protocol_limits_.max_canonical_operation_bytes_per_page});

    SyncReplicaReconciliationResponse response;
    response.folder_id = folder_id_;
    response.requester_actor = request.requester_actor;
    response.responder_actor = local_actor_;
    response.channel_binding = channel.binding;
    response.request_digest =
        sync_replica_reconciliation_request_digest_or_throw(
            request, protocol_limits_);
    response.source_state_generation = page.source_state_generation;
    response.source_evidence_count = page.source_evidence_count;
    response.source_evidence_set_digest =
        page.source_evidence_set_digest;

    struct SelectedPayloadSource final {
        SyncReplicaReconciliationPayload metadata;
        std::optional<SyncReplicaReconciliationBorrowedDeltaManifest>
            borrowed_delta_manifest;
        std::size_t opened_payload_index = 0U;
        std::uint64_t offset_bytes = 0U;
        std::uint64_t range_bytes = 0U;
    };
    std::vector<SelectedPayloadSource> selected_payloads;
    std::vector<SyncReplicaFilePayloadStoreOpenedPayload> opened_payloads;
    selected_payloads.reserve(static_cast<std::size_t>(
        protocol_limits_.max_payloads_per_page));
    opened_payloads.reserve(static_cast<std::size_t>(
        protocol_limits_.max_payloads_per_page));
    std::uint64_t payload_bytes = 0U;
    const SyncReplicaOperation* terminal_source_manifest_operation = nullptr;

    if (page.disposition ==
        SyncReplicaSqliteEvidencePageDisposition::SourceChanged) {
        response.disposition =
            SyncReplicaReconciliationResponseDisposition::SourceChanged;
    } else {
        response.disposition =
            SyncReplicaReconciliationResponseDisposition::Page;
        response.next_after_operation_id = request.after_operation_id;

        // Hydrate at most one ranged source before any payload descriptor in
        // this page is opened. A page may retain earlier whole-payload
        // descriptors until direct frame assembly, so checkpoint observation
        // inside the loop would reverse the store-global/inode lock order.
        if (!terminal_verification_request) {
            for (const SyncReplicaOperation& operation : page.operations) {
                const bool materialized_file =
                    operation.kind == SyncReplicaValueKind::File &&
                    sync_replica_selective_sync_path_is_materialized(
                        request.selective_sync_policy,
                        operation.canonical_path);
                const bool ranged = materialized_file &&
                    (request.payload_continuation.has_value() ||
                     operation.size_bytes >
                         protocol_limits_.max_single_payload_bytes);
                if (!ranged) continue;
                const SyncReplicaContentDefinedChunkingParameters parameters =
                    sync_replica_reconciliation_content_defined_parameters_or_throw(
                        operation.size_bytes);
                restore_source_content_defined_checkpoint_for_operation_or_throw(
                    operation, parameters,
                    "pre-open source content-defined checkpoint restore");
                break;
            }
        }

        const bool page_requires_payload_access = std::any_of(
            page.operations.begin(), page.operations.end(),
            [&](const SyncReplicaOperation& operation) {
                return !terminal_verification_request &&
                       operation.kind == SyncReplicaValueKind::File &&
                       sync_replica_selective_sync_path_is_materialized(
                           request.selective_sync_policy,
                           operation.canonical_path);
            });
        std::optional<SyncReplicaFilePayloadStoreTargetedAccess>
            request_payload_access;
        SyncReplicaFilePayloadStoreTargetedAccess* payload_access = nullptr;
        if (page_requires_payload_access) {
            request_payload_access.emplace(
                payload_store_.begin_targeted_access_or_throw(
                    label_ + " request-scoped source payload access"));
            increment_or_throw(
                session.payload_targeted_access_births_,
                label_ + " targeted payload access birth");
            payload_access = &*request_payload_access;
        }

        auto open_source_payload_or_none = [&]
            (const SyncReplicaOperation& operation,
             std::string_view operation_label)
            -> std::optional<SyncReplicaFilePayloadStoreOpenedPayload> {
            if (payload_access == nullptr) {
                throw std::logic_error(
                    label_ + " selected file has no targeted payload access");
            }
            increment_or_throw(
                session.payload_targeted_open_attempts_,
                label_ + " targeted payload open attempt");
            std::optional<SyncReplicaFilePayloadStoreOpenedPayload> opened =
                payload_access->open_optional_payload_for_operation_or_throw(
                    operation, operation_label);
            if (opened.has_value()) {
                increment_or_throw(
                    session.payload_targeted_opens_,
                    label_ + " targeted payload open");
            }
            return opened;
        };

        std::set<std::string> selected_whole_payload_digests;
        bool budget_trimmed = false;
        bool payload_incomplete = false;
        for (const SyncReplicaOperation& operation : page.operations) {
            const bool metadata_only_file =
                operation.kind == SyncReplicaValueKind::File &&
                !sync_replica_selective_sync_path_is_materialized(
                    request.selective_sync_policy,
                    operation.canonical_path);
            if (request.payload_continuation.has_value() &&
                (operation.operation_id !=
                     request.payload_continuation->operation_id ||
                 operation.kind != SyncReplicaValueKind::File ||
                 metadata_only_file ||
                 operation.content_sha256 !=
                     request.payload_continuation->content_sha256 ||
                 operation.size_bytes !=
                     request.payload_continuation->total_size_bytes)) {
                throw std::runtime_error(
                    label_ + " source evidence no longer binds the requested payload continuation");
            }

            if (metadata_only_file) {
                response.operations.push_back(operation);
                response.metadata_only_file_operation_ids.push_back(
                    operation.operation_id);
                response.next_after_operation_id = operation.operation_id;
                continue;
            }

            if (terminal_verification_request) {
                response.operations.push_back(operation);
                response.payload_continuation = request.payload_continuation;
                response.next_after_operation_id = request.after_operation_id;
                payload_incomplete = true;
                break;
            }

            if (operation.kind == SyncReplicaValueKind::File) {
                const std::uint64_t offset =
                    request.payload_continuation.has_value()
                        ? request.payload_continuation->next_offset_bytes
                        : 0U;
                const bool whole_inline =
                    !request.payload_continuation.has_value() &&
                    operation.size_bytes <=
                        protocol_limits_.max_single_payload_bytes;
                if (whole_inline) {
                    if (!selected_whole_payload_digests.contains(
                            operation.content_sha256)) {
                        if (selected_payloads.size() >=
                                protocol_limits_.max_payloads_per_page ||
                            operation.size_bytes >
                                protocol_limits_.max_payload_bytes_per_page -
                                    payload_bytes) {
                            budget_trimmed = true;
                            break;
                        }
                        std::optional<SyncReplicaFilePayloadStoreOpenedPayload>
                            opened = open_source_payload_or_none(
                                operation,
                                label_ +
                                    " reconciliation whole payload selection");
                        if (!opened.has_value()) {
                            response.disposition =
                                SyncReplicaReconciliationResponseDisposition::PayloadUnavailable;
                            response.blocked_operation_id =
                                operation.operation_id;
                            break;
                        }
                        if (opened->content_sha256() !=
                                operation.content_sha256 ||
                            opened->size_bytes() != operation.size_bytes) {
                            throw std::logic_error(
                                label_ + " whole targeted payload selection lost exact content identity");
                        }
                        const std::size_t opened_payload_index =
                            opened_payloads.size();
                        opened_payloads.push_back(std::move(*opened));
                        SyncReplicaReconciliationPayload metadata;
                        metadata.content_sha256 = operation.content_sha256;
                        metadata.total_size_bytes = operation.size_bytes;
                        metadata.offset_bytes = 0U;
                        selected_payloads.push_back({
                            std::move(metadata), std::nullopt,
                            opened_payload_index, 0U, operation.size_bytes});
                        add_or_throw(
                            payload_bytes, operation.size_bytes,
                            label_ + " response payload bytes");
                        selected_whole_payload_digests.insert(
                            operation.content_sha256);
                    }
                } else {
                    if (selected_payloads.size() >=
                            protocol_limits_.max_payloads_per_page ||
                        payload_bytes >=
                            protocol_limits_.max_payload_bytes_per_page) {
                        budget_trimmed = true;
                        break;
                    }
                    const SyncReplicaContentDefinedChunkingParameters
                        parameters =
                            sync_replica_reconciliation_content_defined_parameters_or_throw(
                                operation.size_bytes);
                    std::optional<SyncReplicaFilePayloadStoreOpenedPayload>
                        opened = open_source_payload_or_none(
                            operation,
                            label_ +
                                " reconciliation ranged payload selection");
                    if (!opened.has_value()) {
                        response.disposition =
                            SyncReplicaReconciliationResponseDisposition::PayloadUnavailable;
                        response.blocked_operation_id = operation.operation_id;
                        break;
                    }
                    if (opened->content_sha256() !=
                            operation.content_sha256 ||
                        opened->size_bytes() != operation.size_bytes) {
                        throw std::logic_error(
                            label_ + " ranged targeted payload selection lost exact content identity");
                    }
                    bool reused_cached_manifest = false;
                    if (source_content_defined_manifest_.has_value() &&
                        source_content_defined_manifest_->content_sha256 ==
                            operation.content_sha256 &&
                        source_content_defined_manifest_->total_size_bytes ==
                            operation.size_bytes &&
                        source_content_defined_manifest_->manifest.parameters() ==
                            parameters &&
                        source_content_defined_manifest_->source_metadata ==
                            opened->metadata()) {
                        reused_cached_manifest = true;
                    } else {
                        source_content_defined_manifest_.reset();
                        const SourceContentDefinedProjectionAdvance
                            projection_step =
                                advance_source_content_defined_projection_or_throw(
                                    operation, *opened,
                                    "bounded source content-defined projection");
                        if (projection_step.projection_restarted) {
                            increment_or_throw(
                                session.content_defined_manifest_projection_restarts_,
                                label_ +
                                    " content-defined manifest projection restart");
                        }
                        increment_or_throw(
                            session.content_defined_manifest_projection_steps_,
                            label_ +
                                " content-defined manifest projection step");
                        add_or_throw(
                            session.content_defined_manifest_hashed_bytes_,
                            projection_step.hashed_bytes,
                            label_ + " content-defined manifest hashed bytes");
                        if (!projection_step.completed) {
                            response.disposition =
                                SyncReplicaReconciliationResponseDisposition::
                                    SourcePayloadPreparing;
                            response.blocked_operation_id =
                                operation.operation_id;
                            increment_or_throw(
                                session.source_payload_preparing_responses_,
                                label_ + " source payload preparing response");
                            break;
                        }
                        increment_or_throw(
                            session.content_defined_manifest_scans_,
                            label_ + " content-defined manifest scan");
                        increment_or_throw(
                            session.content_defined_chunk_index_builds_,
                            label_ + " content-defined chunk-index build");
                    }
                    const auto& source_manifest =
                        *source_content_defined_manifest_;
                    if (request.cached_delta_manifest_digest.has_value() &&
                        *request.cached_delta_manifest_digest !=
                            source_manifest.manifest_digest) {
                        throw std::runtime_error(
                            label_ + " requested content-defined manifest cache does not match current source bytes");
                    }
                    if (reused_cached_manifest) {
                        increment_or_throw(
                            session.content_defined_manifest_reuses_,
                            label_ + " content-defined manifest reuse");
                        increment_or_throw(
                            session.content_defined_chunk_index_reuses_,
                            label_ + " content-defined chunk-index reuse");
                    }
                    increment_or_throw(
                        session.content_defined_chunk_index_lookups_,
                        label_ + " content-defined chunk-index lookup");
                    const std::size_t opened_payload_index =
                        opened_payloads.size();
                    opened_payloads.push_back(std::move(*opened));
                    std::size_t chunk_index =
                        source_manifest.manifest.chunk_index_for_offset_or_throw(
                            offset, label_);
                    std::uint64_t next_offset = offset;
                    std::uint64_t window_ranges = 0U;
                    std::uint64_t window_bytes = 0U;
                    bool first_range = true;
                    while (
                        next_offset < operation.size_bytes &&
                        selected_payloads.size() <
                            protocol_limits_.max_payloads_per_page &&
                        payload_bytes <
                            protocol_limits_.max_payload_bytes_per_page) {
                        while (
                            chunk_index + 1U <
                                source_manifest.manifest.chunk_count() &&
                            next_offset ==
                                source_manifest.manifest
                                    .chunk_end_offset_bytes_or_throw(
                                        chunk_index, label_)) {
                            ++chunk_index;
                        }
                        if (chunk_index >=
                            source_manifest.manifest.chunk_count()) {
                            throw std::logic_error(
                                label_ + " source content-defined chunk index ended before its payload");
                        }
                        const std::uint64_t chunk_offset =
                            source_manifest.manifest
                                .chunk_offset_bytes_or_throw(
                                    chunk_index, label_);
                        const std::uint64_t chunk_end =
                            source_manifest.manifest
                                .chunk_end_offset_bytes_or_throw(
                                    chunk_index, label_);
                        const std::uint64_t chunk_size = chunk_end - chunk_offset;
                        const std::uint64_t available_page_bytes =
                            protocol_limits_.max_payload_bytes_per_page -
                            payload_bytes;
                        const std::uint64_t maximum_range =
                            std::min<std::uint64_t>(
                                {protocol_limits_.max_single_payload_bytes,
                                 available_page_bytes,
                                 chunk_end - next_offset});
                        if (maximum_range == 0U) break;

                        const std::uint64_t supplied = maximum_range;
                        if (supplied == 0U) {
                            throw std::logic_error(
                                label_ + " ranged payload plan made no progress");
                        }
                        const std::uint64_t range_offset = next_offset;
                        add_or_throw(
                            payload_bytes, supplied,
                            label_ + " response payload bytes");
                        add_or_throw(
                            next_offset, supplied,
                            label_ + " ranged payload next offset");

                        SyncReplicaReconciliationPayload metadata(
                            operation.content_sha256, operation.size_bytes,
                            range_offset, std::string{}, std::string{},
                            source_manifest.manifest_digest, chunk_offset,
                            chunk_size);
                        std::optional<
                            SyncReplicaReconciliationBorrowedDeltaManifest>
                            borrowed_delta_manifest;
                        if (first_range &&
                            !request.cached_delta_manifest_digest.has_value()) {
                            borrowed_delta_manifest =
                                source_manifest.manifest.borrow_for_direct_frame();
                            increment_or_throw(
                                session.content_defined_manifest_publications_,
                                label_ +
                                    " content-defined manifest publication");
                        } else {
                            increment_or_throw(
                                session.content_defined_manifest_references_,
                                label_ +
                                    " content-defined manifest reference");
                        }
                        selected_payloads.push_back({
                            std::move(metadata),
                            std::move(borrowed_delta_manifest),
                            opened_payload_index, range_offset, supplied});
                        increment_or_throw(
                            window_ranges,
                            label_ + " ranged payload window ranges");
                        add_or_throw(
                            window_bytes, supplied,
                            label_ + " ranged payload window bytes");
                        first_range = false;
                    }
                    if (next_offset == offset) {
                        budget_trimmed = true;
                        break;
                    }
                    increment_or_throw(
                        session.ranged_payload_windows_,
                        label_ + " ranged payload windows");
                    add_or_throw(
                        session.ranged_payload_ranges_, window_ranges,
                        label_ + " ranged payload ranges");
                    add_or_throw(
                        session.ranged_payload_bytes_, window_bytes,
                        label_ + " ranged payload bytes");
                    response.operations.push_back(operation);
                    response.payload_continuation =
                        SyncReplicaReconciliationPayloadContinuation{
                            operation.operation_id,
                            operation.content_sha256,
                            operation.size_bytes,
                            next_offset};
                    if (next_offset == operation.size_bytes) {
                        terminal_source_manifest_operation = &operation;
                    }
                    payload_incomplete = true;
                    break;
                }
            }
            response.operations.push_back(operation);
            response.next_after_operation_id = operation.operation_id;
        }

        std::sort(
            selected_payloads.begin(), selected_payloads.end(),
            [](const SelectedPayloadSource& left,
               const SelectedPayloadSource& right) {
                if (left.metadata.content_sha256 !=
                    right.metadata.content_sha256) {
                    return left.metadata.content_sha256 <
                           right.metadata.content_sha256;
                }
                return left.metadata.offset_bytes <
                       right.metadata.offset_bytes;
            });
        if (request.payload_continuation.has_value() &&
            page.operations.empty()) {
            throw std::runtime_error(
                label_ + " requested payload continuation is absent from retained source evidence");
        }
        if (response.disposition ==
                SyncReplicaReconciliationResponseDisposition::PayloadUnavailable ||
            response.disposition ==
                SyncReplicaReconciliationResponseDisposition::
                    SourcePayloadPreparing) {
            response.has_more = true;
        } else if (payload_incomplete) {
            response.has_more = true;
        } else {
            response.has_more = budget_trimmed || page.has_more;
        }
    }

    std::vector<std::uint64_t> payload_byte_counts;
    std::vector<std::optional<
        SyncReplicaReconciliationBorrowedDeltaManifest>>
        borrowed_delta_manifests;
    payload_byte_counts.reserve(selected_payloads.size());
    borrowed_delta_manifests.reserve(selected_payloads.size());
    response.payloads.reserve(selected_payloads.size());
    std::uint64_t expected_borrowed_manifest_count = 0U;
    std::uint64_t expected_borrowed_manifest_chunks = 0U;
    for (SelectedPayloadSource& selected : selected_payloads) {
        payload_byte_counts.push_back(selected.range_bytes);
        if (selected.borrowed_delta_manifest.has_value()) {
            increment_or_throw(
                expected_borrowed_manifest_count,
                label_ + " direct response borrowed manifest count");
            add_or_throw(
                expected_borrowed_manifest_chunks,
                static_cast<std::uint64_t>(
                    selected.borrowed_delta_manifest->chunks.size()),
                label_ + " direct response borrowed manifest chunks");
        }
        borrowed_delta_manifests.push_back(
            std::move(selected.borrowed_delta_manifest));
        response.payloads.push_back(std::move(selected.metadata));
    }
    SyncReplicaReconciliationResponseFrameAssembly assembly =
        begin_sync_replica_reconciliation_response_frame_assembly_or_throw(
            std::move(response), request, std::move(payload_byte_counts),
            std::move(borrowed_delta_manifests),
            protocol_limits_);
    if (assembly.payload_count() != selected_payloads.size()) {
        throw std::logic_error(
            label_ + " direct response assembly lost its payload cardinality");
    }
    for (std::size_t payload_index = 0U;
         payload_index < selected_payloads.size(); ++payload_index) {
        const SelectedPayloadSource& selected =
            selected_payloads[payload_index];
        if (selected.opened_payload_index >= opened_payloads.size()) {
            throw std::logic_error(
                label_ + " direct response source descriptor index is invalid");
        }
        std::span<char> destination =
            assembly.payload_bytes_or_throw(payload_index);
        if (destination.size() != selected.range_bytes) {
            throw std::logic_error(
                label_ + " direct response payload hole changed its exact range size");
        }
        std::string chunk_sha256 =
            opened_payloads[selected.opened_payload_index]
                .copy_exact_range_into_or_throw(
                    selected.offset_bytes, destination,
                    label_ + " direct response payload " +
                        std::to_string(payload_index));
        assembly.commit_payload_or_throw(
            payload_index, std::move(chunk_sha256));
    }
    SyncReplicaReconciliationDirectFrameResponse direct =
        assembly.finish_or_throw();
    if (direct.payload_bytes != payload_bytes ||
        direct.borrowed_delta_manifest_count !=
            expected_borrowed_manifest_count ||
        direct.borrowed_delta_manifest_chunks !=
            expected_borrowed_manifest_chunks ||
        direct.response.payloads.size() != selected_payloads.size() ||
        std::any_of(
            direct.response.payloads.begin(), direct.response.payloads.end(),
            [](const SyncReplicaReconciliationPayload& payload) {
                return !payload.bytes.empty() ||
                       payload.delta_manifest.has_value();
            })) {
        throw std::logic_error(
            label_ +
            " direct response retained a second payload or manifest aggregate");
    }
    const std::uint64_t opened_payload_count =
        static_cast<std::uint64_t>(opened_payloads.size());
    opened_payloads.clear();
    publish_pending_source_manifest_checkpoint_if_possible_or_throw(
        "post-frame source manifest checkpoint publication");
    std::uint64_t terminal_cache_releases = 0U;
    std::uint64_t terminal_cache_released_capacity_bytes = 0U;
    if (terminal_source_manifest_operation != nullptr) {
        terminal_cache_released_capacity_bytes =
            release_terminal_source_manifest_cache_if_possible_or_throw(
                *terminal_source_manifest_operation);
        terminal_cache_releases =
            terminal_cache_released_capacity_bytes == 0U ? 0U : 1U;
    }
    return {
        std::move(request), std::move(direct.response),
        std::move(direct.frame),
        static_cast<std::uint64_t>(selected_payloads.size()),
        direct.payload_bytes,
        0U,
        0U,
        direct.borrowed_delta_manifest_count,
        direct.borrowed_delta_manifest_chunks,
        0U,
        terminal_cache_releases,
        terminal_cache_released_capacity_bytes,
        opened_payload_count};
}

SyncReplicaReconciliationApplyResult
SyncReplicaReconciliationService::apply_response_or_throw(
    const SyncReplicaDeliveryChannelAuthority& channel_authority,
    const SyncReplicaReconciliationRequest& expected_request,
    std::string_view response_frame) {
    validate_channel_or_throw(channel_authority, "inbound response");
    require_current_owner_identity_or_throw("inbound response");
    const SyncReplicaDeliveryChannelContext& channel =
        channel_authority.context();
    if (expected_request.folder_id != folder_id_ ||
        expected_request.requester_actor != local_actor_ ||
        expected_request.responder_actor != channel.peer_actor ||
        expected_request.channel_binding != channel.binding) {
        throw std::invalid_argument(
            label_ + " expected reconciliation request does not bind this local service and channel");
    }

    const SyncReplicaReconciliationBorrowedResponse decoded =
        decode_sync_replica_reconciliation_response_for_request_borrowing_payloads_or_throw(
            response_frame, expected_request, protocol_limits_);
    const SyncReplicaReconciliationResponse& response = decoded.response;
    const bool terminal_verification_request =
        expected_request.payload_continuation.has_value() &&
        expected_request.payload_continuation->next_offset_bytes ==
            expected_request.payload_continuation->total_size_bytes;

    SyncReplicaReconciliationApplyResult result;
    result.source_state_generation = response.source_state_generation;
    result.source_evidence_count = response.source_evidence_count;
    result.source_evidence_set_digest =
        response.source_evidence_set_digest;
    result.has_more = response.has_more;
    result.next_after_operation_id = response.next_after_operation_id;
    result.blocked_operation_id = response.blocked_operation_id;
    result.payload_continuation = response.payload_continuation;
    std::uint64_t terminal_verification_steps_spent = 0U;
    bool terminal_verification_budget_exhaustion_reported = false;

    if (response.disposition ==
        SyncReplicaReconciliationResponseDisposition::SourceChanged) {
        delta_target_manifest_.reset();
        delta_predecessor_manifest_.reset();
        delta_predecessor_projection_.reset();
        delta_cross_file_search_.reset();
        delta_cross_file_projection_.reset();
        delta_cross_file_manifest_.reset();
        result.disposition =
            SyncReplicaReconciliationApplyDisposition::SourceChanged;
        return result;
    }

    struct PayloadRangeSpan final {
        std::size_t begin = 0U;
        std::size_t count = 0U;
    };
    std::map<std::string, PayloadRangeSpan> payload_ranges_by_digest;
    for (std::size_t index = 0U; index < response.payloads.size(); ++index) {
        const SyncReplicaReconciliationPayload& payload =
            response.payloads[index];
        auto [found, inserted] = payload_ranges_by_digest.try_emplace(
            payload.content_sha256, PayloadRangeSpan{index, 0U});
        if (!inserted && found->second.begin + found->second.count != index) {
            throw std::logic_error(
                label_ + " validated payload range group lost contiguity");
        }
        ++found->second.count;
    }

    std::optional<SyncReplicaFilePayloadStoreTargetedAccess>
        delta_targeted_access;

    auto reset_delta_caches = [&]() noexcept {
        delta_target_manifest_.reset();
        delta_predecessor_manifest_.reset();
        delta_predecessor_projection_.reset();
        delta_cross_file_search_.reset();
        delta_cross_file_projection_.reset();
        delta_cross_file_manifest_.reset();
    };

    auto continue_terminal_verification_locally_or_throw = [&]
        (const SyncReplicaOperation& operation,
         ReceivedFilePayloadResult& received) {
        while (received.disposition ==
                   ReceivedFilePayloadDisposition::Progress &&
               received.next_offset_bytes == operation.size_bytes &&
               terminal_verification_steps_spent <
                   max_terminal_verification_steps_per_apply_) {
            const SyncReplicaFilePayloadStoreStageResult staged =
                payload_store_.
                    continue_staged_payload_prefix_verification_or_throw(
                        operation.content_sha256,
                        operation.size_bytes);
            if (staged.content_sha256 != operation.content_sha256 ||
                staged.total_size_bytes != operation.size_bytes ||
                staged.accepted_range_bytes != 0U ||
                staged.next_offset_bytes != operation.size_bytes ||
                staged.terminal_verification_steps > 1U) {
                throw std::logic_error(
                    label_ +
                    " local terminal payload verification lost exact identity or admitted source authority");
            }
            add_or_throw(
                result.terminal_verification_steps,
                staged.terminal_verification_steps,
                label_ + " terminal verification steps");
            add_or_throw(
                result.terminal_verification_local_continuation_steps,
                staged.terminal_verification_steps,
                label_ + " local terminal continuation steps");
            add_or_throw(
                terminal_verification_steps_spent,
                staged.terminal_verification_steps,
                label_ + " terminal verification step budget");

            switch (staged.disposition) {
                case SyncReplicaFilePayloadStoreStageDisposition::Progress:
                    if (staged.terminal_verification_steps != 1U) {
                        throw std::logic_error(
                            label_ +
                            " nonterminal local verification made no bounded hash progress");
                    }
                    received.next_offset_bytes = staged.next_offset_bytes;
                    break;
                case SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedInserted:
                    increment_or_throw(
                        result.inserted_payloads,
                        label_ +
                            " completed local terminal-verification payload");
                    received = ReceivedFilePayloadResult{};
                    break;
                case SyncReplicaFilePayloadStoreStageDisposition::
                    CompletedAlreadyPresent:
                    increment_or_throw(
                        result.existing_payloads,
                        label_ +
                            " existing local terminal-verification payload");
                    received = ReceivedFilePayloadResult{};
                    break;
            }
        }
        if (received.disposition ==
                ReceivedFilePayloadDisposition::Progress &&
            received.next_offset_bytes == operation.size_bytes &&
            terminal_verification_steps_spent >=
                max_terminal_verification_steps_per_apply_ &&
            !terminal_verification_budget_exhaustion_reported) {
            terminal_verification_budget_exhaustion_reported = true;
            increment_or_throw(
                result.terminal_verification_step_budget_exhaustions,
                label_ + " terminal verification step budget exhaustion");
        }
    };

    auto target_manifest_for_wire_or_throw = [&]
        (const SyncReplicaOperation& operation,
         const SyncReplicaReconciliationPayload& wire,
         std::string_view wire_bytes)
        -> const CachedTargetContentDefinedManifest* {
        const bool whole =
            wire.offset_bytes == 0U &&
            static_cast<std::uint64_t>(wire_bytes.size()) ==
                wire.total_size_bytes;
        if (whole) return nullptr;
        if (!wire.delta_manifest_digest.has_value()) {
            throw std::logic_error(
                label_ + " validated ranged payload lost its manifest digest");
        }

        if (wire.delta_manifest.has_value()) {
            if (delta_target_manifest_.has_value() &&
                (delta_target_manifest_->operation_id !=
                     operation.operation_id ||
                 delta_target_manifest_->manifest_digest !=
                     *wire.delta_manifest_digest)) {
                delta_predecessor_manifest_.reset();
                delta_predecessor_projection_.reset();
                delta_cross_file_search_.reset();
                delta_cross_file_projection_.reset();
                delta_cross_file_manifest_.reset();
            }
            std::vector<std::uint64_t> offsets =
                chunk_offsets_or_throw(
                    wire.delta_manifest->chunks,
                    operation.size_bytes,
                    label_ + " target content-defined manifest");
            delta_target_manifest_ = CachedTargetContentDefinedManifest{
                operation.operation_id,
                operation.content_sha256,
                operation.size_bytes,
                *wire.delta_manifest_digest,
                *wire.delta_manifest,
                std::move(offsets)};
            increment_or_throw(
                result.target_content_defined_manifest_publications,
                label_ + " target content-defined manifest publication");
        } else {
            if (!delta_target_manifest_.has_value() ||
                delta_target_manifest_->operation_id != operation.operation_id ||
                delta_target_manifest_->content_sha256 !=
                    operation.content_sha256 ||
                delta_target_manifest_->total_size_bytes !=
                    operation.size_bytes ||
                delta_target_manifest_->manifest_digest !=
                    *wire.delta_manifest_digest) {
                throw std::runtime_error(
                    label_ + " ranged payload references a content-defined manifest absent from this receiver process");
            }
            increment_or_throw(
                result.target_content_defined_manifest_reuses,
                label_ + " target content-defined manifest reuse");
        }
        CachedTargetContentDefinedManifest& retained =
            *delta_target_manifest_;
        const std::size_t chunk_index =
            chunk_index_for_offset_or_throw(
                retained.chunk_offsets, wire.offset_bytes,
                wire.total_size_bytes,
                label_ + " retained delta target");
        const std::uint64_t chunk_offset =
            retained.chunk_offsets[chunk_index];
        const std::uint64_t chunk_size =
            retained.chunk_offsets[chunk_index + 1U] - chunk_offset;
        if (wire.delta_chunk_offset_bytes != chunk_offset ||
            wire.delta_chunk_size_bytes != chunk_size) {
            throw std::runtime_error(
                label_ + " ranged payload does not bind the retained content-defined chunk extent");
        }
        if (wire.offset_bytes == chunk_offset &&
            static_cast<std::uint64_t>(wire_bytes.size()) == chunk_size &&
            !retained.manifest.chunks[chunk_index].sha256
                 .equals_lowercase_hex(wire.chunk_sha256)) {
            throw std::runtime_error(
                label_ + " ranged payload bytes do not match the retained content-defined manifest reference");
        }
        return &retained;
    };

    auto matching_candidate_chunk = [&]
        (const CachedTargetContentDefinedManifest& target,
         std::size_t target_chunk_index,
         const std::vector<
             SyncReplicaFilePayloadStoreContentDefinedChunk>& candidate_chunks,
         const std::vector<std::size_t>& candidate_indices)
        -> std::optional<std::size_t> {
        if (target_chunk_index >= target.manifest.chunks.size()) {
            throw std::logic_error(
                label_ + " delta target manifest lost its current chunk");
        }
        const SyncReplicaReconciliationDeltaChunk& target_chunk =
            target.manifest.chunks[target_chunk_index];
        auto found = std::lower_bound(
            candidate_indices.begin(), candidate_indices.end(),
            target_chunk.sha256,
            [&](std::size_t candidate_index,
                const Sha256DigestValue& digest) {
                return candidate_chunks[candidate_index].sha256 < digest;
            });
        while (found != candidate_indices.end() &&
               candidate_chunks[*found].sha256 == target_chunk.sha256) {
            if (candidate_chunks[*found].size_bytes ==
                target_chunk.size_bytes) {
                return *found;
            }
            ++found;
        }
        return std::nullopt;
    };

    enum class LocalCandidateReuseDisposition : std::uint8_t {
        SourceAvailable = 1U,
        SourceUnavailable = 2U,
        BudgetExhausted = 3U,
    };

    std::uint64_t remaining_local_reuse_bytes =
        max_local_reuse_bytes_per_apply_;
    bool local_reuse_budget_exhausted = false;
    auto mark_local_reuse_budget_exhausted_or_throw = [&]() {
        if (local_reuse_budget_exhausted) return;
        local_reuse_budget_exhausted = true;
        increment_or_throw(
            result.delta_local_reuse_budget_exhaustions,
            label_ + " delta local-reuse budget exhaustion");
    };

    // Both same-path predecessor reuse and current-visible cross-file reuse
    // pass through this one copy/staging boundary. The source operation is
    // reopened for every bounded range, each range is SHA-256 attested by the
    // payload-store owner, and only the final whole target digest can publish
    // the immutable payload. The shared per-apply byte budget is charged for
    // actual source bytes read, not merely newly accepted bytes. Exact durable
    // prefix continuation allows a later turn to resume inside one very large
    // adaptive chunk without retaining a chunk-sized buffer.
    auto reuse_local_candidate_chunks_or_throw = [&]
        (const SyncReplicaOperation& operation,
         const CachedTargetContentDefinedManifest& target,
         const SyncReplicaOperation& candidate,
         const SyncPosixRegularFileSnapshotMetadata& candidate_metadata,
         const std::vector<
             SyncReplicaFilePayloadStoreContentDefinedChunk>& candidate_chunks,
         const std::vector<std::size_t>& candidate_indices,
         const std::vector<std::uint64_t>& candidate_offsets,
         const std::string& source_label,
         ReceivedFilePayloadResult& received)
        -> LocalCandidateReuseDisposition {
        if (received.disposition !=
            ReceivedFilePayloadDisposition::Progress) {
            return LocalCandidateReuseDisposition::SourceAvailable;
        }
        std::uint64_t target_offset = received.next_offset_bytes;
        if (target_offset >= operation.size_bytes) {
            return LocalCandidateReuseDisposition::SourceAvailable;
        }
        if (candidate_offsets.size() != candidate_chunks.size() + 1U ||
            candidate_offsets.empty() || candidate_offsets.front() != 0U) {
            throw std::logic_error(
                label_ + " " + source_label +
                " chunk offsets lost their exact candidate extent");
        }
        bool first_candidate_read = true;
        while (target_offset < operation.size_bytes) {
            const std::size_t target_chunk_index =
                chunk_index_for_offset_or_throw(
                    target.chunk_offsets, target_offset,
                    operation.size_bytes,
                    label_ + " delta local-reuse target");
            const std::optional<std::size_t> candidate_chunk =
                matching_candidate_chunk(
                    target, target_chunk_index, candidate_chunks,
                    candidate_indices);
            if (!candidate_chunk.has_value()) break;
            if (*candidate_chunk + 1U >= candidate_offsets.size()) {
                throw std::logic_error(
                    label_ + " " + source_label +
                    " chunk match lost its candidate offset");
            }

            const std::uint64_t target_chunk_begin =
                target.chunk_offsets[target_chunk_index];
            const std::uint64_t target_chunk_end =
                target.chunk_offsets[target_chunk_index + 1U];
            if (target_offset < target_chunk_begin ||
                target_offset >= target_chunk_end) {
                throw std::logic_error(
                    label_ + " delta local-reuse target offset escaped its chunk");
            }
            const std::uint64_t candidate_chunk_begin =
                candidate_offsets[*candidate_chunk];
            const std::uint64_t candidate_chunk_end =
                candidate_offsets[*candidate_chunk + 1U];
            if (candidate_chunk_end < candidate_chunk_begin ||
                candidate_chunk_end - candidate_chunk_begin !=
                    target_chunk_end - target_chunk_begin) {
                throw std::logic_error(
                    label_ + " " + source_label +
                    " matched chunk lost its exact extent");
            }

            if (remaining_local_reuse_bytes == 0U) {
                received.next_offset_bytes = target_offset;
                mark_local_reuse_budget_exhausted_or_throw();
                return LocalCandidateReuseDisposition::BudgetExhausted;
            }
            const bool first_read_resumes_inside_chunk =
                first_candidate_read && target_offset != target_chunk_begin;
            const std::uint64_t invocation_chunk_start = target_offset;
            const bool invocation_started_at_chunk_boundary =
                invocation_chunk_start == target_chunk_begin;
            std::uint64_t accepted_in_chunk = 0U;
            bool jumped_to_existing_prefix = false;
            while (target_offset < target_chunk_end) {
                if (remaining_local_reuse_bytes == 0U) {
                    received.next_offset_bytes = target_offset;
                    mark_local_reuse_budget_exhausted_or_throw();
                    return LocalCandidateReuseDisposition::BudgetExhausted;
                }
                const std::uint64_t range_limit =
                    std::min<std::uint64_t>(
                        kSyncReplicaReconciliationMaximumLocalReuseRangeBytes,
                        std::min<std::uint64_t>(
                            target_chunk_end - target_offset,
                            remaining_local_reuse_bytes));
                if (range_limit == 0U) {
                    throw std::logic_error(
                        label_ + " delta local-reuse range made no progress");
                }
                const std::uint64_t intra_chunk_offset =
                    target_offset - target_chunk_begin;
                if (intra_chunk_offset >
                    candidate_chunk_end - candidate_chunk_begin) {
                    throw std::logic_error(
                        label_ + " " + source_label +
                        " local-reuse offset escaped its candidate chunk");
                }

                if (!delta_targeted_access.has_value()) {
                    delta_targeted_access.emplace(
                        payload_store_.begin_targeted_access_or_throw(
                            label_ + " delta local-candidate access"));
                }
                SyncReplicaFilePayloadStoreRange local_range;
                {
                    std::optional<SyncReplicaFilePayloadStoreOpenedPayload>
                        reopened = delta_targeted_access
                            ->open_optional_payload_for_operation_or_throw(
                                candidate,
                                label_ + " " + source_label +
                                    " chunk reopen");
                    if (!reopened.has_value()) {
                        received.next_offset_bytes = target_offset;
                        return LocalCandidateReuseDisposition::SourceUnavailable;
                    }
                    if (reopened->metadata() != candidate_metadata) {
                        received.next_offset_bytes = target_offset;
                        return LocalCandidateReuseDisposition::SourceUnavailable;
                    }
                    local_range = reopened->copy_range_or_throw(
                        candidate_chunk_begin + intra_chunk_offset,
                        range_limit,
                        label_ + " " + source_label + " chunk read");
                }
                const std::uint64_t supplied =
                    static_cast<std::uint64_t>(local_range.bytes.size());
                if (supplied == 0U || supplied > range_limit ||
                    supplied > remaining_local_reuse_bytes) {
                    throw std::logic_error(
                        label_ + " " + source_label +
                        " chunk read violated its bounded range");
                }
                remaining_local_reuse_bytes -= supplied;
                increment_or_throw(
                    result.delta_local_reuse_read_ranges,
                    label_ + " delta local-reuse source range");
                add_or_throw(
                    result.delta_local_reuse_read_bytes, supplied,
                    label_ + " delta local-reuse source bytes");
                result.delta_local_reuse_maximum_read_range_bytes =
                    std::max(
                        result.delta_local_reuse_maximum_read_range_bytes,
                        supplied);
                if (first_candidate_read) {
                    first_candidate_read = false;
                    if (first_read_resumes_inside_chunk) {
                        increment_or_throw(
                            result.delta_local_reuse_interior_resumptions,
                            label_ +
                                " delta local-reuse interior resumption");
                    }
                }

                const std::uint64_t requested_target_offset = target_offset;
                const bool defer_terminal_verification =
                    terminal_verification_steps_spent >=
                    max_terminal_verification_steps_per_apply_;
                const SyncReplicaFilePayloadStoreStageResult staged =
                    defer_terminal_verification
                        ? payload_store_.
                            stage_payload_prefix_deferring_terminal_verification_or_throw(
                                operation.content_sha256,
                                operation.size_bytes,
                                requested_target_offset,
                                std::move(local_range.chunk_sha256),
                                std::move(local_range.bytes))
                        : payload_store_.stage_payload_prefix_or_throw(
                                operation.content_sha256,
                                operation.size_bytes,
                                requested_target_offset,
                                std::move(local_range.chunk_sha256),
                                std::move(local_range.bytes));
                add_or_throw(
                    result.terminal_verification_steps,
                    staged.terminal_verification_steps,
                    label_ + " delta terminal verification steps");
                add_or_throw(
                    terminal_verification_steps_spent,
                    staged.terminal_verification_steps,
                    label_ + " delta terminal verification step budget");
                if (terminal_verification_steps_spent >
                    max_terminal_verification_steps_per_apply_) {
                    throw std::logic_error(
                        label_ +
                        " delta terminal verification crossed its per-apply step budget");
                }
                if (staged.content_sha256 != operation.content_sha256 ||
                    staged.total_size_bytes != operation.size_bytes) {
                    throw std::logic_error(
                        label_ + " delta prefix staging lost content identity");
                }
                if (staged.accepted_range_bytes != 0U) {
                    increment_or_throw(
                        result.reused_payload_ranges,
                        label_ + " reused payload range");
                    add_or_throw(
                        result.reused_payload_bytes,
                        staged.accepted_range_bytes,
                        label_ + " reused payload bytes");
                    add_or_throw(
                        accepted_in_chunk, staged.accepted_range_bytes,
                        label_ + " reused chunk bytes");
                }
                target_offset = staged.next_offset_bytes;
                const std::uint64_t expected_end =
                    requested_target_offset + supplied;
                if (target_offset < expected_end) {
                    throw std::logic_error(
                        label_ + " delta prefix staging moved backward");
                }
                const bool exact_range_advance = target_offset == expected_end;
                const bool completed_whole_chunk_from_this_invocation =
                    invocation_started_at_chunk_boundary &&
                    exact_range_advance &&
                    target_offset == target_chunk_end &&
                    accepted_in_chunk ==
                        target_chunk_end - target_chunk_begin;

                switch (staged.disposition) {
                    case SyncReplicaFilePayloadStoreStageDisposition::Progress:
                        break;
                    case SyncReplicaFilePayloadStoreStageDisposition::
                        CompletedInserted:
                        increment_or_throw(
                            result.inserted_payloads,
                            label_ + " delta completed payload");
                        if (completed_whole_chunk_from_this_invocation) {
                            increment_or_throw(
                                result.reused_payload_chunks,
                                label_ + " reused payload chunk");
                        }
                        received.disposition =
                            ReceivedFilePayloadDisposition::Complete;
                        received.next_offset_bytes = operation.size_bytes;
                        return LocalCandidateReuseDisposition::SourceAvailable;
                    case SyncReplicaFilePayloadStoreStageDisposition::
                        CompletedAlreadyPresent:
                        increment_or_throw(
                            result.existing_payloads,
                            label_ + " existing delta payload");
                        received.disposition =
                            ReceivedFilePayloadDisposition::Complete;
                        received.next_offset_bytes = operation.size_bytes;
                        return LocalCandidateReuseDisposition::SourceAvailable;
                }
                if (!exact_range_advance) {
                    jumped_to_existing_prefix = true;
                    break;
                }
            }
            if (!jumped_to_existing_prefix &&
                invocation_started_at_chunk_boundary &&
                target_offset == target_chunk_end &&
                accepted_in_chunk ==
                    target_chunk_end - target_chunk_begin) {
                increment_or_throw(
                    result.reused_payload_chunks,
                    label_ + " reused payload chunk");
            }
        }
        received.next_offset_bytes = target_offset;
        return LocalCandidateReuseDisposition::SourceAvailable;
    };

    bool predecessor_manifest_step_attempted = false;
    auto reuse_predecessor_chunks_or_throw = [&]
        (const SyncReplicaOperation& operation,
         const CachedTargetContentDefinedManifest& target,
         ReceivedFilePayloadResult& received) {
        if (received.disposition !=
                ReceivedFilePayloadDisposition::Progress ||
            operation.predecessor_operation_ids.empty()) {
            return;
        }
        if (received.next_offset_bytes >= operation.size_bytes) {
            return;
        }

        auto target_matches = [&]
            (const auto& value) {
            return value.target_operation_id == operation.operation_id &&
                   value.target_manifest_digest == target.manifest_digest;
        };
        if (delta_predecessor_manifest_.has_value() &&
            !target_matches(*delta_predecessor_manifest_)) {
            delta_predecessor_manifest_.reset();
        }
        if (delta_predecessor_projection_.has_value() &&
            !target_matches(*delta_predecessor_projection_)) {
            delta_predecessor_projection_.reset();
        }
        if (!delta_targeted_access.has_value()) {
            delta_targeted_access.emplace(
                payload_store_.begin_targeted_access_or_throw(
                    label_ + " delta predecessor access"));
        }

        for (const std::string& predecessor_id :
             operation.predecessor_operation_ids) {
            const SyncReplicaSqliteTargetedPathCutpoint predecessor_cutpoint =
                owner_.targeted_path_cutpoint_or_throw(
                    operation.canonical_path, predecessor_id);
            const SyncReplicaOperation* observed =
                predecessor_cutpoint.requested_retained_operation_or_none();
            if (observed == nullptr ||
                observed->kind != SyncReplicaValueKind::File ||
                observed->canonical_path != operation.canonical_path ||
                observed->content_sha256 == operation.content_sha256 ||
                observed->size_bytes == 0U) {
                if (delta_predecessor_manifest_.has_value() &&
                    delta_predecessor_manifest_
                            ->predecessor_operation_id == predecessor_id) {
                    delta_predecessor_manifest_.reset();
                }
                if (delta_predecessor_projection_.has_value() &&
                    delta_predecessor_projection_
                            ->source_operation.operation_id ==
                        predecessor_id) {
                    delta_predecessor_projection_.reset();
                }
                continue;
            }

            if (delta_predecessor_manifest_.has_value() &&
                delta_predecessor_manifest_->predecessor_operation_id ==
                    observed->operation_id &&
                delta_predecessor_manifest_->manifest.parameters ==
                    target.manifest.parameters &&
                delta_predecessor_manifest_->manifest.content_sha256 ==
                    observed->content_sha256 &&
                delta_predecessor_manifest_->manifest.total_size_bytes ==
                    observed->size_bytes) {
                increment_or_throw(
                    result.delta_predecessor_manifest_reuses,
                    label_ + " delta predecessor manifest reuse");
                increment_or_throw(
                    result.delta_predecessor_index_reuses,
                    label_ + " delta predecessor index reuse");
                const LocalCandidateReuseDisposition reuse_disposition =
                    reuse_local_candidate_chunks_or_throw(
                        operation, target, *observed,
                        delta_predecessor_manifest_->source_metadata,
                        delta_predecessor_manifest_->manifest.chunks,
                        delta_predecessor_manifest_->digest_order,
                        delta_predecessor_manifest_->chunk_offsets,
                        "delta predecessor", received);
                if (reuse_disposition ==
                    LocalCandidateReuseDisposition::SourceUnavailable) {
                    delta_predecessor_manifest_.reset();
                }
                return;
            }
            delta_predecessor_manifest_.reset();

            if (delta_predecessor_projection_.has_value() &&
                delta_predecessor_projection_
                        ->source_operation.operation_id !=
                    observed->operation_id) {
                delta_predecessor_projection_.reset();
            }

            std::optional<SyncReplicaFilePayloadStoreOpenedPayload> opened =
                delta_targeted_access
                    ->open_optional_payload_for_operation_or_throw(
                        *observed,
                        label_ + " delta predecessor selection");
            if (!opened.has_value()) {
                delta_predecessor_projection_.reset();
                continue;
            }

            if (!delta_predecessor_projection_.has_value() ||
                delta_predecessor_projection_->source_metadata !=
                    opened->metadata()) {
                PredecessorContentDefinedProjection projected;
                projected.target_operation_id = operation.operation_id;
                projected.target_manifest_digest = target.manifest_digest;
                projected.source_operation = *observed;
                projected.source_metadata = opened->metadata();
                projected.digest_order.reserve(static_cast<std::size_t>(
                    target.manifest.parameters.maximum_chunk_count));
                projected.chunk_offsets.reserve(static_cast<std::size_t>(
                    target.manifest.parameters.maximum_chunk_count + 1U));
                delta_predecessor_projection_ = std::move(projected);
            }

            PredecessorContentDefinedProjection& projected =
                *delta_predecessor_projection_;
            if (projected.indexed_chunk_count != 0U) {
                const LocalCandidateReuseDisposition reuse_disposition =
                    reuse_local_candidate_chunks_or_throw(
                        operation, target, projected.source_operation,
                        projected.source_metadata,
                        projected.projection.completed_chunks(),
                        projected.digest_order, projected.chunk_offsets,
                        "delta predecessor partial", received);
                if (reuse_disposition ==
                    LocalCandidateReuseDisposition::SourceUnavailable) {
                    delta_predecessor_projection_.reset();
                    return;
                }
                if (received.disposition ==
                        ReceivedFilePayloadDisposition::Complete ||
                    reuse_disposition ==
                        LocalCandidateReuseDisposition::BudgetExhausted) {
                    return;
                }
            }

            if (predecessor_manifest_step_attempted) return;
            predecessor_manifest_step_attempted = true;
            SyncReplicaFilePayloadStoreContentDefinedProjectionStep step;
            try {
                step = opened->advance_content_defined_projection_or_throw(
                    projected.projection,
                    target.manifest.parameters,
                    max_predecessor_projection_bytes_per_apply_,
                    label_ +
                        " delta predecessor bounded content-defined projection");
            } catch (...) {
                // The lower owner deliberately clears its private progress on
                // every projection failure. Drop the enclosing index at the
                // same cutpoint so a later apply cannot mistake already
                // indexed chunks for a still-active projection.
                delta_predecessor_projection_.reset();
                throw;
            }
            opened.reset();
            add_or_throw(
                result.delta_predecessor_manifest_hashed_bytes,
                step.hashed_bytes,
                label_ + " delta predecessor manifest hashed bytes");
            if (step.hashed_bytes == 0U ||
                step.hashed_bytes >
                    max_predecessor_projection_bytes_per_apply_) {
                throw std::logic_error(
                    label_ +
                    " delta predecessor projection violated its per-apply byte frontier");
            }

            const bool completed = step.completed_manifest.has_value();
            const auto& available_chunks = completed
                ? step.completed_manifest->chunks
                : projected.projection.completed_chunks();
            extend_content_defined_projection_index_or_throw(
                projected, available_chunks,
                projected.source_operation.size_bytes,
                label_ + " delta predecessor");

            if (!available_chunks.empty()) {
                const LocalCandidateReuseDisposition reuse_disposition =
                    reuse_local_candidate_chunks_or_throw(
                        operation, target, projected.source_operation,
                        projected.source_metadata, available_chunks,
                        projected.digest_order, projected.chunk_offsets,
                        completed ? "delta predecessor"
                                  : "delta predecessor partial",
                        received);
                if (reuse_disposition ==
                    LocalCandidateReuseDisposition::SourceUnavailable) {
                    delta_predecessor_projection_.reset();
                    return;
                }
            }

            if (!completed) return;
            if (projected.indexed_chunk_count !=
                    step.completed_manifest->chunks.size() ||
                projected.chunk_offsets.size() !=
                    step.completed_manifest->chunks.size() + 1U ||
                projected.chunk_offsets.back() != observed->size_bytes) {
                throw std::logic_error(
                    label_ +
                    " completed delta predecessor projection lost its exact index extent");
            }

            CachedPredecessorContentDefinedManifest retained;
            retained.target_operation_id = operation.operation_id;
            retained.target_manifest_digest = target.manifest_digest;
            retained.predecessor_operation_id = observed->operation_id;
            retained.source_metadata = projected.source_metadata;
            retained.manifest = std::move(*step.completed_manifest);
            retained.digest_order = std::move(projected.digest_order);
            retained.chunk_offsets = std::move(projected.chunk_offsets);
            delta_predecessor_projection_.reset();
            delta_predecessor_manifest_ = std::move(retained);
            increment_or_throw(
                result.delta_predecessor_manifest_scans,
                label_ + " delta predecessor manifest scan");
            increment_or_throw(
                result.delta_predecessor_index_builds,
                label_ + " delta predecessor index build");
            return;
        }
    };

    bool cross_file_candidate_page_attempted = false;
    bool cross_file_manifest_step_attempted = false;
    auto reuse_cross_file_chunks_or_throw = [&]
        (const SyncReplicaOperation& operation,
         const CachedTargetContentDefinedManifest& target,
         ReceivedFilePayloadResult& received) {
        if (received.disposition !=
                ReceivedFilePayloadDisposition::Progress ||
            received.next_offset_bytes >= operation.size_bytes) {
            return;
        }

        auto target_matches = [&]
            (const auto& value) {
            return value.target_operation_id == operation.operation_id &&
                   value.target_manifest_digest == target.manifest_digest;
        };
        if (delta_cross_file_manifest_.has_value() &&
            !target_matches(*delta_cross_file_manifest_)) {
            delta_cross_file_manifest_.reset();
        }
        if (delta_cross_file_projection_.has_value() &&
            !target_matches(*delta_cross_file_projection_)) {
            delta_cross_file_projection_.reset();
        }
        if (delta_cross_file_search_.has_value() &&
            !target_matches(*delta_cross_file_search_)) {
            delta_cross_file_search_.reset();
            delta_cross_file_projection_.reset();
        }
        if (!delta_cross_file_search_.has_value()) {
            CrossFileContentDefinedSearch search;
            search.target_operation_id = operation.operation_id;
            search.target_manifest_digest = target.manifest_digest;
            search.payload_availability_generation_at_sweep_start =
                payload_store_.payload_availability_generation_or_throw(
                    label_ +
                    " delta cross-file initial payload availability");
            delta_cross_file_search_ = std::move(search);
        }

        if (delta_cross_file_manifest_.has_value()) {
            increment_or_throw(
                result.delta_cross_file_manifest_reuses,
                label_ + " delta cross-file manifest reuse");
            increment_or_throw(
                result.delta_cross_file_index_reuses,
                label_ + " delta cross-file index reuse");
            const LocalCandidateReuseDisposition reuse_disposition =
                reuse_local_candidate_chunks_or_throw(
                    operation, target,
                    delta_cross_file_manifest_->source_operation,
                    delta_cross_file_manifest_->source_metadata,
                    delta_cross_file_manifest_->manifest.chunks,
                    delta_cross_file_manifest_->digest_order,
                    delta_cross_file_manifest_->chunk_offsets,
                    "delta cross-file candidate", received);
            if (reuse_disposition ==
                LocalCandidateReuseDisposition::SourceUnavailable) {
                delta_cross_file_manifest_.reset();
            }
            return;
        }

        CrossFileContentDefinedSearch& search = *delta_cross_file_search_;
        auto clear_pending_page = [&]() noexcept {
            search.pending_file_operations.clear();
            search.next_pending_file_operation = 0U;
            search.pending_page_tail_canonical_path.clear();
            search.pending_page_has_more = false;
            search.pending_page_loaded = false;
        };
        auto reset_sweep = [&]
            (std::optional<std::uint64_t> availability_generation) noexcept {
            delta_cross_file_projection_.reset();
            search.next_page_after_canonical_path.reset();
            clear_pending_page();
            search.payload_availability_generation_at_sweep_start =
                availability_generation;
            search.exhausted = false;
        };
        auto availability_generation_is_unchanged = []
            (const std::optional<std::uint64_t>& left,
             const std::optional<std::uint64_t>& right) noexcept {
            return left.has_value() && right.has_value() && *left == *right;
        };
        if (search.exhausted) {
            const std::optional<std::uint64_t> current_generation =
                payload_store_.payload_availability_generation_or_throw(
                    label_ +
                    " delta cross-file exhausted payload availability");
            if (availability_generation_is_unchanged(
                    search.payload_availability_generation_at_sweep_start,
                    current_generation)) {
                return;
            }
            reset_sweep(current_generation);
            increment_or_throw(
                result.delta_cross_file_availability_generation_restarts,
                label_ +
                    " delta cross-file availability generation restart");
        }
        if (cross_file_manifest_step_attempted) return;

        auto consume_pending_page_or_throw = [&]
            (bool negative_completion) {
            if (!search.pending_page_loaded ||
                search.next_pending_file_operation <
                    search.pending_file_operations.size()) {
                return;
            }
            if (!search.pending_page_has_more) {
                clear_pending_page();
                if (!negative_completion) {
                    search.exhausted = true;
                    return;
                }
                const std::optional<std::uint64_t> current_generation =
                    payload_store_.payload_availability_generation_or_throw(
                        label_ +
                        " delta cross-file completed payload availability");
                if (availability_generation_is_unchanged(
                        search.payload_availability_generation_at_sweep_start,
                        current_generation)) {
                    search.exhausted = true;
                    return;
                }
                reset_sweep(current_generation);
                increment_or_throw(
                    result.delta_cross_file_availability_generation_restarts,
                    label_ +
                        " delta cross-file availability generation restart");
                return;
            }
            if (search.pending_page_tail_canonical_path.empty()) {
                throw std::logic_error(
                    label_ + " delta cross-file page lost its continuation tail");
            }
            search.next_page_after_canonical_path =
                search.pending_page_tail_canonical_path;
            clear_pending_page();
        };

        consume_pending_page_or_throw(true);
        if (search.exhausted) return;
        if (!search.pending_page_loaded) {
            if (cross_file_candidate_page_attempted) return;
            cross_file_candidate_page_attempted = true;
            SyncReplicaSqliteVisibleFileCandidatePage page =
                owner_.visible_file_candidate_page_or_throw(
                    search.next_page_after_canonical_path,
                    search.source_visible_state_digest);
            increment_or_throw(
                result.delta_cross_file_candidate_pages,
                label_ + " delta cross-file candidate page");
            add_or_throw(
                result.delta_cross_file_candidate_paths_scanned,
                page.scanned_visible_paths,
                label_ + " delta cross-file candidate paths scanned");
            if (page.disposition ==
                SyncReplicaSqliteVisibleFileCandidatePageDisposition::
                    SourceChanged) {
                search.source_visible_state_digest =
                    page.source_visible_state_digest;
                reset_sweep(
                    payload_store_.payload_availability_generation_or_throw(
                        label_ +
                        " delta cross-file source-change payload availability"));
                return;
            }
            if (!search.source_visible_state_digest.has_value()) {
                search.source_visible_state_digest =
                    page.source_visible_state_digest;
            } else if (*search.source_visible_state_digest !=
                       page.source_visible_state_digest) {
                throw std::logic_error(
                    label_ + " delta cross-file page lost its source digest");
            }
            search.pending_file_operations =
                std::move(page.file_operations);
            search.next_pending_file_operation = 0U;
            search.pending_page_tail_canonical_path =
                std::move(page.next_after_canonical_path);
            search.pending_page_has_more = page.has_more;
            search.pending_page_loaded = true;
            if (search.pending_file_operations.empty()) {
                consume_pending_page_or_throw(true);
                return;
            }
        }

        if (!delta_targeted_access.has_value()) {
            delta_targeted_access.emplace(
                payload_store_.begin_targeted_access_or_throw(
                    label_ + " delta cross-file access"));
        }

        while (search.next_pending_file_operation <
               search.pending_file_operations.size()) {
            const SyncReplicaOperation& candidate =
                search.pending_file_operations[
                    search.next_pending_file_operation];
            const bool projection_active =
                delta_cross_file_projection_.has_value();
            if (projection_active &&
                delta_cross_file_projection_->source_operation.operation_id !=
                    candidate.operation_id) {
                throw std::logic_error(
                    label_ +
                    " delta cross-file projection lost its pending candidate");
            }
            if (!projection_active) {
                if (candidate.canonical_path == operation.canonical_path ||
                    candidate.content_sha256 == operation.content_sha256) {
                    ++search.next_pending_file_operation;
                    continue;
                }
                const std::uint64_t size_difference =
                    candidate.size_bytes > operation.size_bytes
                        ? candidate.size_bytes - operation.size_bytes
                        : operation.size_bytes - candidate.size_bytes;
                if (size_difference >
                    target.manifest.parameters.maximum_chunk_bytes) {
                    ++search.next_pending_file_operation;
                    continue;
                }
            }

            std::optional<SyncReplicaFilePayloadStoreOpenedPayload> opened =
                delta_targeted_access
                    ->open_optional_payload_for_operation_or_throw(
                        candidate,
                        label_ + " delta cross-file candidate selection");
            if (!opened.has_value()) {
                delta_cross_file_projection_.reset();
                ++search.next_pending_file_operation;
                increment_or_throw(
                    result.delta_cross_file_unavailable_candidates,
                    label_ + " delta cross-file unavailable candidate");
                continue;
            }

            if (!delta_cross_file_projection_.has_value()) {
                CrossFileContentDefinedProjection projected;
                projected.target_operation_id = operation.operation_id;
                projected.target_manifest_digest = target.manifest_digest;
                projected.source_operation = candidate;
                projected.source_metadata = opened->metadata();
                projected.digest_order.reserve(static_cast<std::size_t>(
                    target.manifest.parameters.maximum_chunk_count));
                projected.chunk_offsets.reserve(static_cast<std::size_t>(
                    target.manifest.parameters.maximum_chunk_count + 1U));
                delta_cross_file_projection_ = std::move(projected);
            } else if (
                delta_cross_file_projection_->source_metadata !=
                    opened->metadata()) {
                CrossFileContentDefinedProjection restarted;
                restarted.target_operation_id = operation.operation_id;
                restarted.target_manifest_digest = target.manifest_digest;
                restarted.source_operation = candidate;
                restarted.source_metadata = opened->metadata();
                restarted.digest_order.reserve(static_cast<std::size_t>(
                    target.manifest.parameters.maximum_chunk_count));
                restarted.chunk_offsets.reserve(static_cast<std::size_t>(
                    target.manifest.parameters.maximum_chunk_count + 1U));
                delta_cross_file_projection_ = std::move(restarted);
            }

            CrossFileContentDefinedProjection& projected =
                *delta_cross_file_projection_;
            if (projected.indexed_chunk_count != 0U) {
                const std::uint64_t before_reuse =
                    received.next_offset_bytes;
                const LocalCandidateReuseDisposition reuse_disposition =
                    reuse_local_candidate_chunks_or_throw(
                        operation, target, projected.source_operation,
                        projected.source_metadata,
                        projected.projection.completed_chunks(),
                        projected.digest_order, projected.chunk_offsets,
                        "delta cross-file partial candidate", received);
                if (reuse_disposition ==
                    LocalCandidateReuseDisposition::SourceUnavailable) {
                    delta_cross_file_projection_.reset();
                    ++search.next_pending_file_operation;
                    increment_or_throw(
                        result.delta_cross_file_unavailable_candidates,
                        label_ +
                            " delta cross-file unavailable partial candidate");
                    continue;
                }
                if (received.next_offset_bytes != before_reuse &&
                    !projected.candidate_match_observed) {
                    projected.candidate_match_observed = true;
                    increment_or_throw(
                        result.delta_cross_file_candidate_matches,
                        label_ + " delta cross-file partial candidate match");
                }
                if (received.disposition ==
                        ReceivedFilePayloadDisposition::Complete ||
                    reuse_disposition ==
                        LocalCandidateReuseDisposition::BudgetExhausted) {
                    return;
                }
            }

            cross_file_manifest_step_attempted = true;
            SyncReplicaFilePayloadStoreContentDefinedProjectionStep step;
            try {
                step = opened->advance_content_defined_projection_or_throw(
                    projected.projection,
                    target.manifest.parameters,
                    kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply,
                    label_ +
                        " delta cross-file bounded content-defined projection");
            } catch (...) {
                delta_cross_file_projection_.reset();
                throw;
            }
            opened.reset();
            increment_or_throw(
                result.delta_cross_file_manifest_scan_steps,
                label_ + " delta cross-file manifest scan step");
            add_or_throw(
                result.delta_cross_file_manifest_hashed_bytes,
                step.hashed_bytes,
                label_ + " delta cross-file manifest hashed bytes");
            if (step.hashed_bytes == 0U ||
                step.hashed_bytes >
                    kSyncReplicaReconciliationMaximumCrossFileProjectionBytesPerApply) {
                throw std::logic_error(
                    label_ +
                    " delta cross-file projection violated its per-apply byte frontier");
            }

            const bool completed = step.completed_manifest.has_value();
            const auto& available_chunks = completed
                ? step.completed_manifest->chunks
                : projected.projection.completed_chunks();
            extend_content_defined_projection_index_or_throw(
                projected, available_chunks,
                projected.source_operation.size_bytes,
                label_ + " delta cross-file");

            bool projected_reuse_budget_exhausted = false;
            if (!available_chunks.empty()) {
                const std::uint64_t before_reuse =
                    received.next_offset_bytes;
                const LocalCandidateReuseDisposition reuse_disposition =
                    reuse_local_candidate_chunks_or_throw(
                        operation, target, projected.source_operation,
                        projected.source_metadata, available_chunks,
                        projected.digest_order, projected.chunk_offsets,
                        completed ? "delta cross-file candidate"
                                  : "delta cross-file partial candidate",
                        received);
                if (reuse_disposition ==
                    LocalCandidateReuseDisposition::SourceUnavailable) {
                    delta_cross_file_projection_.reset();
                    ++search.next_pending_file_operation;
                    increment_or_throw(
                        result.delta_cross_file_unavailable_candidates,
                        label_ +
                            " delta cross-file unavailable projected candidate");
                    consume_pending_page_or_throw(true);
                    return;
                }
                projected_reuse_budget_exhausted =
                    reuse_disposition ==
                    LocalCandidateReuseDisposition::BudgetExhausted;
                if (received.next_offset_bytes != before_reuse &&
                    !projected.candidate_match_observed) {
                    projected.candidate_match_observed = true;
                    increment_or_throw(
                        result.delta_cross_file_candidate_matches,
                        label_ + " delta cross-file candidate match");
                }
            }

            if (!completed) {
                return;
            }

            if (projected.indexed_chunk_count !=
                    step.completed_manifest->chunks.size() ||
                projected.chunk_offsets.size() !=
                    step.completed_manifest->chunks.size() + 1U ||
                projected.chunk_offsets.back() != candidate.size_bytes) {
                throw std::logic_error(
                    label_ +
                    " completed delta cross-file projection lost its exact index extent");
            }
            increment_or_throw(
                result.delta_cross_file_manifest_scans,
                label_ + " delta cross-file manifest scan");
            increment_or_throw(
                result.delta_cross_file_index_builds,
                label_ + " delta cross-file index build");
            ++search.next_pending_file_operation;

            bool has_remaining_match = false;
            if (received.disposition ==
                    ReceivedFilePayloadDisposition::Progress &&
                received.next_offset_bytes < operation.size_bytes) {
                const std::size_t target_chunk_index =
                    chunk_index_for_offset_or_throw(
                        target.chunk_offsets, received.next_offset_bytes,
                        operation.size_bytes,
                        label_ + " delta cross-file remaining match");
                for (std::size_t remaining = target_chunk_index;
                     remaining < target.manifest.chunks.size();
                     ++remaining) {
                    if (matching_candidate_chunk(
                            target, remaining,
                            step.completed_manifest->chunks,
                            projected.digest_order).has_value()) {
                        has_remaining_match = true;
                        break;
                    }
                }
            }
            if (!has_remaining_match) {
                delta_cross_file_projection_.reset();
                consume_pending_page_or_throw(true);
                return;
            }

            CachedCrossFileContentDefinedManifest retained;
            retained.target_operation_id = operation.operation_id;
            retained.target_manifest_digest = target.manifest_digest;
            retained.source_operation = projected.source_operation;
            retained.source_metadata = projected.source_metadata;
            retained.manifest = std::move(*step.completed_manifest);
            retained.digest_order = std::move(projected.digest_order);
            retained.chunk_offsets = std::move(projected.chunk_offsets);
            if (!projected.candidate_match_observed) {
                increment_or_throw(
                    result.delta_cross_file_candidate_matches,
                    label_ + " delta cross-file candidate match");
            }
            delta_cross_file_projection_.reset();
            delta_cross_file_manifest_ = std::move(retained);
            if (!projected_reuse_budget_exhausted) {
                const LocalCandidateReuseDisposition reuse_disposition =
                    reuse_local_candidate_chunks_or_throw(
                        operation, target,
                        delta_cross_file_manifest_->source_operation,
                        delta_cross_file_manifest_->source_metadata,
                        delta_cross_file_manifest_->manifest.chunks,
                        delta_cross_file_manifest_->digest_order,
                        delta_cross_file_manifest_->chunk_offsets,
                        "delta cross-file candidate", received);
                if (reuse_disposition ==
                    LocalCandidateReuseDisposition::SourceUnavailable) {
                    delta_cross_file_manifest_.reset();
                }
            }
            consume_pending_page_or_throw(false);
            return;
        }
        consume_pending_page_or_throw(true);

    };

    for (const SyncReplicaOperation& operation : response.operations) {
        const bool metadata_only_file =
            operation.kind == SyncReplicaValueKind::File &&
            std::binary_search(
                response.metadata_only_file_operation_ids.begin(),
                response.metadata_only_file_operation_ids.end(),
                operation.operation_id);
        std::optional<ReceivedFilePayloadResult> received_file_payload;
        if (operation.kind == SyncReplicaValueKind::File &&
            !metadata_only_file) {
            if (terminal_verification_request) {
                received_file_payload = ReceivedFilePayloadResult{
                    ReceivedFilePayloadDisposition::Progress,
                    operation.size_bytes};
                continue_terminal_verification_locally_or_throw(
                    operation, *received_file_payload);
            } else {
                const auto payload_group =
                    payload_ranges_by_digest.find(operation.content_sha256);
                if (payload_group == payload_ranges_by_digest.end() ||
                    payload_group->second.count == 0U) {
                    throw std::logic_error(
                        label_ + " validated response lost a required payload range group");
                }
                const std::size_t payload_group_end =
                    payload_group->second.begin + payload_group->second.count;
                for (std::size_t payload_index = payload_group->second.begin;
                     payload_index < payload_group_end; ++payload_index) {
                const SyncReplicaReconciliationPayload& wire =
                    response.payloads[payload_index];
                const std::string_view wire_bytes =
                    decoded.payload_bytes[payload_index];
                const CachedTargetContentDefinedManifest* target_manifest =
                    target_manifest_for_wire_or_throw(
                        operation, wire, wire_bytes);

                std::uint64_t effective_offset = wire.offset_bytes;
                std::string_view effective_bytes = wire_bytes;
                std::string effective_chunk_sha256;
                if (received_file_payload.has_value()) {
                    if (static_cast<std::uint64_t>(wire_bytes.size()) >
                        std::numeric_limits<std::uint64_t>::max() -
                            wire.offset_bytes) {
                        throw std::logic_error(
                            label_ + " payload range extent overflow");
                    }
                    if (received_file_payload->disposition ==
                        ReceivedFilePayloadDisposition::Complete) {
                        increment_or_throw(
                            result.delta_wire_already_durable_ranges,
                            label_ + " postcompletion wire range");
                        add_or_throw(
                            result.delta_wire_already_durable_bytes,
                            static_cast<std::uint64_t>(wire_bytes.size()),
                            label_ + " postcompletion wire bytes");
                        continue;
                    }
                    const std::uint64_t wire_end =
                        wire.offset_bytes +
                        static_cast<std::uint64_t>(wire_bytes.size());
                    const std::uint64_t durable_prefix =
                        received_file_payload->next_offset_bytes;
                    if (wire_end <= durable_prefix) {
                        // A durable prefix or local predecessor reuse already
                        // covered this source range. The frame, range digest,
                        // and retained manifest were still validated above;
                        // account for the authenticated bytes and avoid
                        // restaging a range that cannot advance the exact
                        // prefix.
                        increment_or_throw(
                            result.delta_wire_already_durable_ranges,
                            label_ + " already-durable wire range");
                        add_or_throw(
                            result.delta_wire_already_durable_bytes,
                            static_cast<std::uint64_t>(wire_bytes.size()),
                            label_ + " already-durable wire bytes");
                        continue;
                    }
                    if (wire.offset_bytes > durable_prefix) {
                        throw std::runtime_error(
                            label_ + " payload range group skipped the receiver's exact durable prefix");
                    }
                    if (wire.offset_bytes < durable_prefix) {
                        const std::uint64_t overlap =
                            durable_prefix - wire.offset_bytes;
                        if (overlap >=
                            static_cast<std::uint64_t>(wire_bytes.size())) {
                            throw std::logic_error(
                                label_ + " payload overlap trim lost its advancing suffix");
                        }
                        effective_bytes.remove_prefix(
                            static_cast<std::size_t>(overlap));
                        effective_offset = durable_prefix;
                        Sha256DigestBuilder suffix_digest;
                        suffix_digest.update(effective_bytes);
                        effective_chunk_sha256 =
                            suffix_digest.finish_hex();
                        increment_or_throw(
                            result.delta_wire_already_durable_ranges,
                            label_ + " partially durable wire range");
                        add_or_throw(
                            result.delta_wire_already_durable_bytes, overlap,
                            label_ + " partially durable wire bytes");
                        increment_or_throw(
                            result.delta_wire_overlap_trimmed_ranges,
                            label_ + " overlap-trimmed wire range");
                    }
                }
                if (effective_chunk_sha256.empty()) {
                    effective_chunk_sha256 = wire.chunk_sha256;
                }

                received_file_payload = receive_file_payload_or_throw(
                    payload_store_, operation, effective_offset,
                    std::move(effective_chunk_sha256), effective_bytes,
                    result, terminal_verification_steps_spent,
                    max_terminal_verification_steps_per_apply_, label_);
                if (target_manifest != nullptr &&
                    !local_reuse_budget_exhausted) {
                    reuse_predecessor_chunks_or_throw(
                        operation, *target_manifest,
                        *received_file_payload);
                    if (!local_reuse_budget_exhausted) {
                        reuse_cross_file_chunks_or_throw(
                            operation, *target_manifest,
                            *received_file_payload);
                    }
                }
            }
            }
            if (!received_file_payload.has_value()) {
                throw std::logic_error(
                    label_ + " payload range group made no receiver observation");
            }
            continue_terminal_verification_locally_or_throw(
                operation, *received_file_payload);
            if (received_file_payload->disposition ==
                    ReceivedFilePayloadDisposition::Complete &&
                delta_target_manifest_.has_value() &&
                delta_target_manifest_->operation_id ==
                    operation.operation_id) {
                reset_delta_caches();
            }
            if (received_file_payload->disposition ==
                ReceivedFilePayloadDisposition::Progress) {
                // The private range is durable, but the whole content identity
                // is not. Stop before admitting operation metadata. A crash at
                // this frontier leaves only resumable bytes, never an active
                // file operation whose payload is absent.
                result.disposition =
                    SyncReplicaReconciliationApplyDisposition::PayloadProgress;
                result.has_more = true;
                // The response cursor names the completed operation prefix
                // immediately before this partial file. Preserve it so the
                // continuation request cannot replay that prefix and then
                // fail to bind the requested ranged operation.
                result.next_after_operation_id =
                    response.next_after_operation_id;
                result.blocked_operation_id.reset();
                result.payload_continuation =
                    SyncReplicaReconciliationPayloadContinuation{
                        operation.operation_id,
                        operation.content_sha256,
                        operation.size_bytes,
                        received_file_payload->next_offset_bytes};
                return result;
            }
        }

        if (metadata_only_file) {
            increment_or_throw(
                result.metadata_only_file_operations,
                label_ + " metadata-only file operation");
        }

        // Materialized file evidence is admitted only after the complete
        // digest-named payload is durable. Explicit metadata-only file evidence
        // is the sole exception: the exact requester policy is part of the
        // request digest and the response names every omitted operation ID.
        // A receiver-capacity refusal may leave harmless content-addressed
        // bytes, but never selected operation metadata ahead of them.
        const SyncReplicaAdmission admission =
            owner_.accept_remote_or_throw(operation);
        if (admission == SyncReplicaAdmission::CapacityBlocked) {
            result.disposition =
                SyncReplicaReconciliationApplyDisposition::ReceiverCapacityBlocked;
            result.has_more = true;
            result.next_after_operation_id =
                expected_request.after_operation_id;
            result.blocked_operation_id = operation.operation_id;
            return result;
        }
        count_admission_or_throw(
            admission, result, label_ + " reconciliation apply");

        if (received_file_payload.has_value()) {
            if (response.payload_continuation.has_value()) {
                // A restarted receiver may already own a longer exact prefix,
                // or the completed final payload. Skip the duplicate source
                // range and continue after this operation under the same
                // pinned source digest.
                result.next_after_operation_id = operation.operation_id;
                result.payload_continuation.reset();
                result.has_more = true;
            }
        }
    }

    switch (response.disposition) {
        case SyncReplicaReconciliationResponseDisposition::PayloadUnavailable:
            result.disposition =
                SyncReplicaReconciliationApplyDisposition::
                    SourcePayloadUnavailable;
            break;
        case SyncReplicaReconciliationResponseDisposition::
            SourcePayloadPreparing:
            result.disposition =
                SyncReplicaReconciliationApplyDisposition::
                    SourcePayloadPreparing;
            break;
        case SyncReplicaReconciliationResponseDisposition::Page:
            result.disposition =
                SyncReplicaReconciliationApplyDisposition::PageApplied;
            break;
        case SyncReplicaReconciliationResponseDisposition::SourceChanged:
            throw std::logic_error(
                label_ + " source-changed response crossed its early return");
    }
    return result;
}

}  // namespace anonsync

#endif
