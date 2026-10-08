#include "sync_replica_network_simulator.hpp"

#include "sync_manifest_validation.hpp"
#include "sync_replica_operation_codec_internal.hpp"

#include <algorithm>
#include <limits>
#include <set>
#include <stdexcept>
#include <type_traits>
#include <utility>

namespace anonsync {

static_assert(std::is_nothrow_move_constructible_v<SyncReplicaOperation>);
static_assert(
    std::is_nothrow_move_constructible_v<SyncReplicaNetworkMessage>);
static_assert(std::is_nothrow_move_constructible_v<SyncReplicaModel>);
static_assert(std::is_nothrow_move_constructible_v<SyncReplicaDurableState>);
static_assert(std::is_nothrow_move_constructible_v<std::vector<std::uint64_t>>);

SyncReplicaNetworkSimulator::SyncReplicaNetworkSimulator(
    std::string folder_id,
    SyncReplicaModelLimits model_limits,
    SyncReplicaNetworkSimulatorLimits network_limits)
    : folder_id_(std::move(folder_id)),
      limits_(model_limits),
      network_limits_(network_limits) {
    if (!sync_id_is_valid(folder_id_)) {
        throw std::invalid_argument(
            "sync replica simulator folder_id must be a lowercase portable sync id");
    }
    detail::validate_sync_replica_model_limits_impl_or_throw(limits_);
    if (network_limits_.max_pending_messages == 0U) {
        throw std::invalid_argument(
            "sync replica simulator max_pending_messages must be positive");
    }
    if (network_limits_.max_pending_semantic_bytes == 0U) {
        throw std::invalid_argument(
            "sync replica simulator max_pending_semantic_bytes must be positive");
    }
}

void SyncReplicaNetworkSimulator::add_replica_or_throw(
    SyncReplicaActor actor) {
    if (nodes_.contains(actor.device_id)) {
        throw std::invalid_argument(
            "sync replica simulator device_id must be unique");
    }
    SyncReplicaModel model(folder_id_, actor, limits_);
    Node node;
    node.actor = std::move(actor);
    node.live.emplace(std::move(model));
    node.durable = node.live->durable_state();
    nodes_.emplace(node.actor.device_id, std::move(node));
}

bool SyncReplicaNetworkSimulator::has_replica(
    const std::string& device_id) const noexcept {
    return nodes_.contains(device_id);
}

bool SyncReplicaNetworkSimulator::replica_is_live(
    const std::string& device_id) const {
    return node_or_throw(device_id).live.has_value();
}

const SyncReplicaModel& SyncReplicaNetworkSimulator::replica_or_throw(
    const std::string& device_id) const {
    return live_model_or_throw(device_id);
}

SyncReplicaDurableState
SyncReplicaNetworkSimulator::durable_state_or_throw(
    const std::string& device_id) const {
    return node_or_throw(device_id).durable;
}

SyncReplicaOperation
SyncReplicaNetworkSimulator::create_local_file_or_throw(
    const std::string& device_id,
    std::string canonical_path,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    Node& node = node_or_throw(device_id);
    const std::size_t broadcast_count = nodes_.size() - 1U;
    preflight_enqueue_budget_or_throw(broadcast_count, 0U);
    SyncReplicaModel candidate = live_model_or_throw(device_id);
    SyncReplicaOperation operation = candidate.create_local_file_or_throw(
        std::move(canonical_path),
        size_bytes,
        std::move(content_sha256));
    std::vector<SyncReplicaNetworkMessage> broadcast =
        make_broadcast_batch_or_throw(device_id, operation);
    SyncReplicaDurableState durable = candidate.durable_state();
    (void)enqueue_messages_atomically_or_throw(std::move(broadcast));
    commit_candidate_noexcept(
        node, std::move(candidate), std::move(durable));
    return operation;
}

SyncReplicaOperation
SyncReplicaNetworkSimulator::create_local_tombstone_or_throw(
    const std::string& device_id,
    std::string canonical_path) {
    Node& node = node_or_throw(device_id);
    const std::size_t broadcast_count = nodes_.size() - 1U;
    preflight_enqueue_budget_or_throw(broadcast_count, 0U);
    SyncReplicaModel candidate = live_model_or_throw(device_id);
    SyncReplicaOperation operation = candidate.create_local_tombstone_or_throw(
        std::move(canonical_path));
    std::vector<SyncReplicaNetworkMessage> broadcast =
        make_broadcast_batch_or_throw(device_id, operation);
    SyncReplicaDurableState durable = candidate.durable_state();
    (void)enqueue_messages_atomically_or_throw(std::move(broadcast));
    commit_candidate_noexcept(
        node, std::move(candidate), std::move(durable));
    return operation;
}

SyncReplicaOperation
SyncReplicaNetworkSimulator::resolve_local_file_conflict_or_throw(
    const std::string& device_id,
    std::string canonical_path,
    std::span<const std::string> expected_visible_operation_ids,
    std::uint64_t size_bytes,
    std::string content_sha256) {
    Node& node = node_or_throw(device_id);
    const std::size_t broadcast_count = nodes_.size() - 1U;
    preflight_enqueue_budget_or_throw(broadcast_count, 0U);
    SyncReplicaModel candidate = live_model_or_throw(device_id);
    SyncReplicaOperation operation =
        candidate.resolve_local_file_conflict_or_throw(
            std::move(canonical_path), expected_visible_operation_ids,
            size_bytes, std::move(content_sha256));
    std::vector<SyncReplicaNetworkMessage> broadcast =
        make_broadcast_batch_or_throw(device_id, operation);
    SyncReplicaDurableState durable = candidate.durable_state();
    (void)enqueue_messages_atomically_or_throw(std::move(broadcast));
    commit_candidate_noexcept(
        node, std::move(candidate), std::move(durable));
    return operation;
}

void SyncReplicaNetworkSimulator::crash_or_throw(
    const std::string& device_id) {
    Node& node = node_or_throw(device_id);
    if (!node.live.has_value()) {
        throw std::invalid_argument(
            "sync replica simulator cannot crash an already stopped replica");
    }
    node.live.reset();
}

void SyncReplicaNetworkSimulator::restart_or_throw(
    const std::string& device_id) {
    Node& node = node_or_throw(device_id);
    if (node.live.has_value()) {
        throw std::invalid_argument(
            "sync replica simulator cannot restart an already live replica");
    }
    node.live.emplace(
        SyncReplicaModel::restore_or_throw(node.durable, limits_));
}

void SyncReplicaNetworkSimulator::partition_direction_or_throw(
    const std::string& source_device_id,
    const std::string& destination_device_id) {
    (void)node_or_throw(source_device_id);
    (void)node_or_throw(destination_device_id);
    if (source_device_id == destination_device_id) {
        throw std::invalid_argument(
            "sync replica simulator cannot partition a replica from itself");
    }
    partitioned_directions_.emplace(
        source_device_id, destination_device_id);
}

void SyncReplicaNetworkSimulator::partition_bidirectional_or_throw(
    const std::string& first_device_id,
    const std::string& second_device_id) {
    (void)node_or_throw(first_device_id);
    (void)node_or_throw(second_device_id);
    if (first_device_id == second_device_id) {
        throw std::invalid_argument(
            "sync replica simulator cannot partition a replica from itself");
    }

    const auto first = partitioned_directions_.emplace(
        first_device_id, second_device_id);
    try {
        partitioned_directions_.emplace(
            second_device_id, first_device_id);
    } catch (...) {
        if (first.second) partitioned_directions_.erase(first.first);
        throw;
    }
}

void SyncReplicaNetworkSimulator::heal_direction_or_throw(
    const std::string& source_device_id,
    const std::string& destination_device_id) {
    (void)node_or_throw(source_device_id);
    (void)node_or_throw(destination_device_id);
    if (source_device_id == destination_device_id) {
        throw std::invalid_argument(
            "sync replica simulator cannot heal a self-direction");
    }
    erase_partition_direction_noexcept(
        source_device_id, destination_device_id);
}

void SyncReplicaNetworkSimulator::heal_bidirectional_or_throw(
    const std::string& first_device_id,
    const std::string& second_device_id) {
    (void)node_or_throw(first_device_id);
    (void)node_or_throw(second_device_id);
    if (first_device_id == second_device_id) {
        throw std::invalid_argument(
            "sync replica simulator cannot heal a self-direction");
    }
    erase_partition_direction_noexcept(
        first_device_id, second_device_id);
    erase_partition_direction_noexcept(
        second_device_id, first_device_id);
}

void SyncReplicaNetworkSimulator::heal_all() noexcept {
    partitioned_directions_.clear();
}

bool SyncReplicaNetworkSimulator::direction_is_partitioned(
    const std::string& source_device_id,
    const std::string& destination_device_id) const {
    (void)node_or_throw(source_device_id);
    (void)node_or_throw(destination_device_id);
    return direction_is_partitioned_noexcept(
        source_device_id, destination_device_id);
}

bool SyncReplicaNetworkSimulator::direction_is_partitioned_noexcept(
    std::string_view source_device_id,
    std::string_view destination_device_id) const noexcept {
    return partitioned_directions_.contains(
        DirectionView{source_device_id, destination_device_id});
}

void SyncReplicaNetworkSimulator::erase_partition_direction_noexcept(
    std::string_view source_device_id,
    std::string_view destination_device_id) noexcept {
    const auto direction = partitioned_directions_.find(
        DirectionView{source_device_id, destination_device_id});
    if (direction != partitioned_directions_.end()) {
        partitioned_directions_.erase(direction);
    }
}

std::size_t SyncReplicaNetworkSimulator::enqueue_anti_entropy_or_throw(
    const std::string& source_device_id,
    const std::string& destination_device_id) {
    if (source_device_id == destination_device_id) {
        throw std::invalid_argument(
            "sync replica anti-entropy requires distinct replicas");
    }
    const SyncReplicaModel& source =
        live_model_or_throw(source_device_id);
    (void)node_or_throw(destination_device_id);
    const std::size_t operation_count = source.evidence_count();
    if (operation_count == 0U) return 0U;

    // Reject cardinality/identifier exhaustion before copying even the source
    // operation set. Then compute the exact byte charge before allocating the
    // multiplicative queued batch.
    preflight_enqueue_budget_or_throw(operation_count, 0U);
    std::vector<SyncReplicaOperation> operations =
        source.all_evidence_operations();
    std::size_t batch_semantic_bytes = 0;
    for (const SyncReplicaOperation& operation : operations) {
        const std::size_t weight =
            message_semantic_byte_weight_or_throw(
                source_device_id, destination_device_id, operation);
        if (weight > std::numeric_limits<std::size_t>::max() -
                         batch_semantic_bytes) {
            throw std::overflow_error(
                "sync replica anti-entropy semantic-byte total overflowed size_t");
        }
        batch_semantic_bytes += weight;
    }
    preflight_enqueue_budget_or_throw(
        operation_count, batch_semantic_bytes);

    std::vector<SyncReplicaNetworkMessage> batch;
    batch.reserve(operations.size());
    for (SyncReplicaOperation& operation : operations) {
        SyncReplicaNetworkMessage message;
        message.source_device_id = source_device_id;
        message.destination_device_id = destination_device_id;
        message.operation = std::move(operation);
        batch.push_back(std::move(message));
    }
    (void)enqueue_messages_atomically_or_throw(std::move(batch));
    return operations.size();
}

std::size_t
SyncReplicaNetworkSimulator::enqueue_full_mesh_anti_entropy_or_throw() {
    for (const auto& [source_id, source] : nodes_) {
        (void)source_id;
        if (!source.live.has_value()) {
            throw std::invalid_argument(
                "sync replica full-mesh anti-entropy requires every source replica live");
        }
    }

    std::size_t total_messages = 0;
    const std::size_t destinations_per_source =
        nodes_.empty() ? 0U : nodes_.size() - 1U;
    for (const auto& [source_id, source] : nodes_) {
        (void)source_id;
        const std::size_t operation_count =
            source.live->evidence_count();
        if (destinations_per_source != 0U &&
            operation_count >
                std::numeric_limits<std::size_t>::max() /
                    destinations_per_source) {
            throw std::overflow_error(
                "sync replica full-mesh anti-entropy message count overflowed size_t");
        }
        const std::size_t source_messages =
            operation_count * destinations_per_source;
        if (source_messages >
            std::numeric_limits<std::size_t>::max() - total_messages) {
            throw std::overflow_error(
                "sync replica full-mesh anti-entropy message count overflowed size_t");
        }
        total_messages += source_messages;
    }
    if (total_messages == 0U) return 0U;

    // Cardinality and message identifiers are checked before any operation is
    // copied into a mesh-sized batch. Semantic bytes are then accumulated over
    // one source snapshot at a time, still before reserve or payload copies.
    preflight_enqueue_budget_or_throw(total_messages, 0U);
    std::size_t batch_semantic_bytes = 0;
    for (const auto& [source_id, source] : nodes_) {
        const std::vector<SyncReplicaOperation> operations =
            source.live->all_evidence_operations();
        for (const auto& [destination_id, destination] : nodes_) {
            (void)destination;
            if (source_id == destination_id) continue;
            for (const SyncReplicaOperation& operation : operations) {
                const std::size_t weight =
                    message_semantic_byte_weight_or_throw(
                        source_id, destination_id, operation);
                if (weight > std::numeric_limits<std::size_t>::max() -
                                 batch_semantic_bytes) {
                    throw std::overflow_error(
                        "sync replica full-mesh anti-entropy semantic-byte total overflowed size_t");
                }
                batch_semantic_bytes += weight;
            }
        }
    }
    preflight_enqueue_budget_or_throw(
        total_messages, batch_semantic_bytes);

    std::vector<SyncReplicaNetworkMessage> batch;
    batch.reserve(total_messages);
    for (const auto& [source_id, source] : nodes_) {
        const std::vector<SyncReplicaOperation> operations =
            source.live->all_evidence_operations();
        for (const auto& [destination_id, destination] : nodes_) {
            (void)destination;
            if (source_id == destination_id) continue;
            for (const SyncReplicaOperation& operation : operations) {
                SyncReplicaNetworkMessage message;
                message.source_device_id = source_id;
                message.destination_device_id = destination_id;
                message.operation = operation;
                batch.push_back(std::move(message));
            }
        }
    }
    (void)enqueue_messages_atomically_or_throw(std::move(batch));
    return total_messages;
}

std::vector<std::uint64_t>
SyncReplicaNetworkSimulator::pending_message_ids() const {
    std::vector<std::uint64_t> ids;
    ids.reserve(messages_.size());
    for (const auto& [message_id, message] : messages_) {
        (void)message;
        ids.push_back(message_id);
    }
    return ids;
}

std::optional<SyncReplicaNetworkMessage>
SyncReplicaNetworkSimulator::message_by_id(
    std::uint64_t message_id) const {
    const auto found = messages_.find(message_id);
    if (found == messages_.end()) return std::nullopt;
    return found->second;
}

std::uint64_t SyncReplicaNetworkSimulator::duplicate_message_or_throw(
    std::uint64_t message_id) {
    const auto found = messages_.find(message_id);
    if (found == messages_.end()) {
        throw std::invalid_argument(
            "sync replica simulator cannot duplicate an unknown message");
    }
    preflight_enqueue_budget_or_throw(
        1U, found->second.semantic_byte_weight);
    SyncReplicaNetworkMessage duplicate = found->second;
    duplicate.message_id = 0;
    std::vector<SyncReplicaNetworkMessage> batch;
    batch.push_back(std::move(duplicate));
    const std::vector<std::uint64_t> ids =
        enqueue_messages_atomically_or_throw(std::move(batch));
    if (ids.size() != 1U) {
        throw std::logic_error(
            "sync replica simulator duplicate enqueue lost its one-message cardinality");
    }
    return ids.front();
}

bool SyncReplicaNetworkSimulator::drop_message(
    std::uint64_t message_id) noexcept {
    const auto found = messages_.find(message_id);
    if (found == messages_.end()) return false;
    erase_message_noexcept(found);
    return true;
}

std::optional<SyncReplicaAdmission>
SyncReplicaNetworkSimulator::deliver_message_or_throw(
    std::uint64_t message_id) {
    const auto found = messages_.find(message_id);
    if (found == messages_.end()) {
        throw std::invalid_argument(
            "sync replica simulator cannot deliver an unknown message");
    }
    const SyncReplicaNetworkMessage& message = found->second;
    Node& destination = node_or_throw(message.destination_device_id);
    if (!destination.live.has_value() ||
        direction_is_partitioned_noexcept(
            message.source_device_id, message.destination_device_id)) {
        return std::nullopt;
    }

    // Capacity and exact replay are properties of the immutable live owner.
    // Resolve both before cloning the retained graph. A duplicate needs only
    // queue retirement; a capacity block must preserve the queued envelope for
    // retry and must not manufacture a durable-state rewrite.
    const SyncReplicaRemoteAdmissionPreflight preflight =
        destination.live->preflight_remote_admission_or_throw(
            message.operation);
    if (preflight.readiness == SyncReplicaRemoteReadiness::Duplicate) {
        erase_message_noexcept(found);
        return SyncReplicaAdmission::Duplicate;
    }
    if (preflight.readiness ==
        SyncReplicaRemoteReadiness::CapacityBlocked) {
        return SyncReplicaAdmission::CapacityBlocked;
    }
    if (preflight.readiness != SyncReplicaRemoteReadiness::Admissible) {
        throw std::logic_error(
            "sync replica simulator received unknown remote readiness");
    }

    SyncReplicaModel candidate = destination.live.value();
    const SyncReplicaAdmission admission =
        candidate.accept_remote_admissible_after_preflight_or_throw(
            message.operation, preflight);
    if (admission == SyncReplicaAdmission::Duplicate ||
        admission == SyncReplicaAdmission::CapacityBlocked) {
        throw std::logic_error(
            "sync replica simulator admission changed after immutable preflight without concurrency");
    }
    SyncReplicaDurableState durable = candidate.durable_state();
    commit_candidate_noexcept(
        destination, std::move(candidate), std::move(durable));
    erase_message_noexcept(found);
    return admission;
}

std::size_t SyncReplicaNetworkSimulator::drain_deliverable_or_throw(
    SyncReplicaDeliveryOrder order,
    std::size_t max_deliveries) {
    std::size_t delivered = 0;
    std::set<std::uint64_t> capacity_blocked_message_ids;
    while (delivered < max_deliveries) {
        std::optional<std::uint64_t> selected;
        if (order == SyncReplicaDeliveryOrder::OldestFirst) {
            for (const auto& [message_id, message] : messages_) {
                if (capacity_blocked_message_ids.contains(message_id)) {
                    continue;
                }
                const Node& destination =
                    node_or_throw(message.destination_device_id);
                if (destination.live.has_value() &&
                    !direction_is_partitioned_noexcept(
                        message.source_device_id,
                        message.destination_device_id)) {
                    selected = message_id;
                    break;
                }
            }
        } else if (order == SyncReplicaDeliveryOrder::NewestFirst) {
            for (auto iterator = messages_.rbegin();
                 iterator != messages_.rend(); ++iterator) {
                if (capacity_blocked_message_ids.contains(iterator->first)) {
                    continue;
                }
                const SyncReplicaNetworkMessage& message = iterator->second;
                const Node& destination =
                    node_or_throw(message.destination_device_id);
                if (destination.live.has_value() &&
                    !direction_is_partitioned_noexcept(
                        message.source_device_id,
                        message.destination_device_id)) {
                    selected = iterator->first;
                    break;
                }
            }
        } else {
            throw std::invalid_argument(
                "sync replica simulator has unknown delivery order");
        }

        if (!selected.has_value()) break;
        const auto result = deliver_message_or_throw(selected.value());
        if (!result.has_value()) {
            throw std::logic_error(
                "sync replica simulator selected a message that became blocked without concurrency");
        }
        if (result.value() == SyncReplicaAdmission::CapacityBlocked) {
            capacity_blocked_message_ids.insert(selected.value());
            continue;
        }
        ++delivered;
    }
    return delivered;
}

bool SyncReplicaNetworkSimulator::all_replicas_live() const noexcept {
    return std::all_of(
        nodes_.begin(), nodes_.end(),
        [](const auto& entry) {
            return entry.second.live.has_value();
        });
}

bool SyncReplicaNetworkSimulator::all_operation_sets_equal_or_throw() const {
    if (nodes_.empty()) return true;
    std::optional<std::string> expected;
    for (const auto& [device_id, node] : nodes_) {
        (void)node;
        const std::string digest =
            live_model_or_throw(device_id).operation_set_digest();
        if (!expected.has_value()) expected = digest;
        if (digest != expected.value()) return false;
    }
    return true;
}

bool SyncReplicaNetworkSimulator::all_evidence_sets_equal_or_throw() const {
    if (nodes_.empty()) return true;
    std::optional<std::string> expected;
    for (const auto& [device_id, node] : nodes_) {
        (void)node;
        const std::string digest =
            live_model_or_throw(device_id).evidence_set_digest();
        if (!expected.has_value()) expected = digest;
        if (digest != expected.value()) return false;
    }
    return true;
}

bool SyncReplicaNetworkSimulator::all_visible_states_equal_or_throw() const {
    if (nodes_.empty()) return true;
    std::optional<std::string> expected;
    for (const auto& [device_id, node] : nodes_) {
        (void)node;
        const std::string digest =
            live_model_or_throw(device_id).visible_state_digest();
        if (!expected.has_value()) expected = digest;
        if (digest != expected.value()) return false;
    }
    return true;
}

SyncReplicaNetworkSimulator::Node&
SyncReplicaNetworkSimulator::node_or_throw(
    const std::string& device_id) {
    const auto found = nodes_.find(device_id);
    if (found == nodes_.end()) {
        throw std::invalid_argument(
            "sync replica simulator does not know device_id: " + device_id);
    }
    return found->second;
}

const SyncReplicaNetworkSimulator::Node&
SyncReplicaNetworkSimulator::node_or_throw(
    const std::string& device_id) const {
    const auto found = nodes_.find(device_id);
    if (found == nodes_.end()) {
        throw std::invalid_argument(
            "sync replica simulator does not know device_id: " + device_id);
    }
    return found->second;
}

SyncReplicaModel& SyncReplicaNetworkSimulator::live_model_or_throw(
    const std::string& device_id) {
    Node& node = node_or_throw(device_id);
    if (!node.live.has_value()) {
        throw std::invalid_argument(
            "sync replica simulator operation requires a live replica: " +
            device_id);
    }
    return node.live.value();
}

const SyncReplicaModel&
SyncReplicaNetworkSimulator::live_model_or_throw(
    const std::string& device_id) const {
    const Node& node = node_or_throw(device_id);
    if (!node.live.has_value()) {
        throw std::invalid_argument(
            "sync replica simulator operation requires a live replica: " +
            device_id);
    }
    return node.live.value();
}

std::vector<std::uint64_t>
SyncReplicaNetworkSimulator::enqueue_messages_atomically_or_throw(
    std::vector<SyncReplicaNetworkMessage> batch) {
    if (batch.empty()) return {};

    std::size_t batch_semantic_bytes = 0;
    for (SyncReplicaNetworkMessage& message : batch) {
        (void)node_or_throw(message.source_device_id);
        (void)node_or_throw(message.destination_device_id);
        if (message.source_device_id == message.destination_device_id) {
            throw std::invalid_argument(
                "sync replica simulator does not enqueue loopback messages");
        }
        if (message.operation.folder_id != folder_id_) {
            throw std::invalid_argument(
                "sync replica simulator cannot enqueue an operation from a different folder");
        }
        message.semantic_byte_weight =
            message_semantic_byte_weight_or_throw(message);
        if (message.semantic_byte_weight >
            std::numeric_limits<std::size_t>::max() -
                batch_semantic_bytes) {
            throw std::overflow_error(
                "sync replica simulator message batch semantic-byte weight overflowed size_t");
        }
        batch_semantic_bytes += message.semantic_byte_weight;
    }
    preflight_enqueue_budget_or_throw(
        batch.size(), batch_semantic_bytes);

    std::vector<std::uint64_t> ids;
    ids.reserve(batch.size());
    std::uint64_t candidate_next_message_id = next_message_id_;
    for (SyncReplicaNetworkMessage& message : batch) {
        message.message_id = candidate_next_message_id;
        ids.push_back(candidate_next_message_id);
        candidate_next_message_id =
            candidate_next_message_id ==
                    std::numeric_limits<std::uint64_t>::max()
                ? 0U
                : candidate_next_message_id + 1U;
    }

    std::size_t inserted_count = 0;
    try {
        for (std::size_t index = 0; index < batch.size(); ++index) {
            const auto inserted = messages_.emplace(
                ids[index], std::move(batch[index]));
            if (!inserted.second) {
                throw std::logic_error(
                    "sync replica simulator message identifier unexpectedly collided");
            }
            ++inserted_count;
        }
    } catch (...) {
        for (std::size_t index = 0; index < inserted_count; ++index) {
            messages_.erase(ids[index]);
        }
        throw;
    }

    pending_message_semantic_bytes_ += batch_semantic_bytes;
    next_message_id_ = candidate_next_message_id;
    return ids;
}

std::vector<SyncReplicaNetworkMessage>
SyncReplicaNetworkSimulator::make_broadcast_batch_or_throw(
    const std::string& source_device_id,
    const SyncReplicaOperation& operation) const {
    (void)node_or_throw(source_device_id);
    const std::size_t batch_count =
        nodes_.empty() ? 0U : nodes_.size() - 1U;
    if (batch_count == 0U) return {};

    preflight_enqueue_budget_or_throw(batch_count, 0U);
    std::size_t batch_semantic_bytes = 0;
    for (const auto& [destination_device_id, node] : nodes_) {
        (void)node;
        if (destination_device_id == source_device_id) continue;
        const std::size_t weight =
            message_semantic_byte_weight_or_throw(
                source_device_id, destination_device_id, operation);
        if (weight > std::numeric_limits<std::size_t>::max() -
                         batch_semantic_bytes) {
            throw std::overflow_error(
                "sync replica broadcast semantic-byte total overflowed size_t");
        }
        batch_semantic_bytes += weight;
    }
    preflight_enqueue_budget_or_throw(
        batch_count, batch_semantic_bytes);

    std::vector<SyncReplicaNetworkMessage> batch;
    batch.reserve(batch_count);
    for (const auto& [destination_device_id, node] : nodes_) {
        (void)node;
        if (destination_device_id == source_device_id) continue;
        SyncReplicaNetworkMessage message;
        message.source_device_id = source_device_id;
        message.destination_device_id = destination_device_id;
        message.operation = operation;
        batch.push_back(std::move(message));
    }
    return batch;
}

void SyncReplicaNetworkSimulator::preflight_enqueue_budget_or_throw(
    std::size_t batch_count,
    std::size_t batch_semantic_bytes) const {
    if (messages_.size() > network_limits_.max_pending_messages ||
        batch_count >
            network_limits_.max_pending_messages - messages_.size()) {
        throw std::length_error(
            "sync replica simulator pending-message count budget would be exceeded");
    }
    if (pending_message_semantic_bytes_ >
            network_limits_.max_pending_semantic_bytes ||
        batch_semantic_bytes >
            network_limits_.max_pending_semantic_bytes -
                pending_message_semantic_bytes_) {
        throw std::length_error(
            "sync replica simulator pending-message semantic-byte budget would be exceeded");
    }
    if (batch_count == 0U) return;
    if (next_message_id_ == 0U) {
        throw std::overflow_error(
            "sync replica simulator exhausted message identifiers");
    }
    if constexpr (sizeof(std::size_t) > sizeof(std::uint64_t)) {
        if (batch_count > static_cast<std::size_t>(
                              std::numeric_limits<std::uint64_t>::max())) {
            throw std::overflow_error(
                "sync replica simulator message batch exceeds uint64 identifier space");
        }
    }
    const std::uint64_t available_identifiers =
        std::numeric_limits<std::uint64_t>::max() - next_message_id_ + 1U;
    if (static_cast<std::uint64_t>(batch_count) >
        available_identifiers) {
        throw std::overflow_error(
            "sync replica simulator message batch exceeds remaining identifiers");
    }
}

std::size_t
SyncReplicaNetworkSimulator::message_semantic_byte_weight_or_throw(
    const std::string& source_device_id,
    const std::string& destination_device_id,
    const SyncReplicaOperation& operation) {
    std::size_t total = 0;
    const auto add = [&total](std::size_t amount) {
        if (amount > std::numeric_limits<std::size_t>::max() - total) {
            throw std::overflow_error(
                "sync replica simulator message semantic-byte weight overflowed size_t");
        }
        total += amount;
    };

    // Fixed-width semantic scalars: message id, value kind, file size, dot
    // epoch/counter, context cardinality, predecessor cardinality, and two
    // uint64 values per clock entry. Literal widths keep this accounting stable
    // across C++ ABIs.
    constexpr std::size_t kUint64SemanticBytes = 8U;
    constexpr std::size_t kKindSemanticBytes = 1U;
    add(kUint64SemanticBytes);
    add(kKindSemanticBytes);
    add(kUint64SemanticBytes);
    add(kUint64SemanticBytes);
    add(kUint64SemanticBytes);
    add(kUint64SemanticBytes);
    add(kUint64SemanticBytes);
    constexpr std::size_t kClockEntryScalarBytes =
        kUint64SemanticBytes * 2U;
    if (operation.causal_context.size() >
        std::numeric_limits<std::size_t>::max() /
            kClockEntryScalarBytes) {
        throw std::overflow_error(
            "sync replica simulator context scalar weight overflowed size_t");
    }
    add(operation.causal_context.size() *
        kClockEntryScalarBytes);

    add(source_device_id.size());
    add(destination_device_id.size());
    add(operation.operation_id.size());
    add(operation.folder_id.size());
    add(operation.canonical_path.size());
    add(operation.content_sha256.size());
    add(operation.dot.actor.device_id.size());
    for (const SyncReplicaClockEntry& entry :
         operation.causal_context) {
        add(entry.actor.device_id.size());
    }
    for (const std::string& predecessor_id :
         operation.predecessor_operation_ids) {
        add(predecessor_id.size());
    }
    return total;
}

std::size_t
SyncReplicaNetworkSimulator::message_semantic_byte_weight_or_throw(
    const SyncReplicaNetworkMessage& message) {
    return message_semantic_byte_weight_or_throw(
        message.source_device_id,
        message.destination_device_id,
        message.operation);
}

void SyncReplicaNetworkSimulator::erase_message_noexcept(
    std::map<std::uint64_t, SyncReplicaNetworkMessage>::iterator message)
    noexcept {
    if (message == messages_.end() ||
        message->second.semantic_byte_weight >
            pending_message_semantic_bytes_) {
        std::terminate();
    }
    pending_message_semantic_bytes_ -=
        message->second.semantic_byte_weight;
    messages_.erase(message);
}

void SyncReplicaNetworkSimulator::commit_candidate_noexcept(
    Node& node,
    SyncReplicaModel&& candidate,
    SyncReplicaDurableState&& durable) noexcept {
    static_assert(std::is_nothrow_move_assignable_v<SyncReplicaModel>);
    static_assert(std::is_nothrow_move_assignable_v<SyncReplicaDurableState>);
    if (!node.live.has_value()) std::terminate();
    node.durable = std::move(durable);
    node.live.value() = std::move(candidate);
}

}  // namespace anonsync
