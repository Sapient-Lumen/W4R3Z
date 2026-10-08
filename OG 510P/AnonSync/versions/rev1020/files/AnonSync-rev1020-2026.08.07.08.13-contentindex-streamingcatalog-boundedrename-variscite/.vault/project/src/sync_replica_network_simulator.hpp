#pragma once

#include "sync_replica_model.hpp"

#include <cstddef>
#include <cstdint>
#include <map>
#include <optional>
#include <set>
#include <span>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace anonsync {

// Deterministic in-memory fault harness for the pure replica model. It models
// duplicate/lost/reordered delivery, directional partitions, crash/restart,
// and explicit anti-entropy. Accepted operations are persisted atomically in
// this reference harness; binding that cutpoint to SQLite is a separate
// production obligation rather than an implied property of this simulator.
struct SyncReplicaNetworkMessage final {
    std::uint64_t message_id = 0;
    std::string source_device_id;
    std::string destination_device_id;
    SyncReplicaOperation operation;
    // Stable typed-value weight assigned by the simulator at queue admission.
    // This is not allocator overhead or a wire encoding length; it is an
    // implementation-independent resource-accounting unit that counts every
    // owned string byte and fixed-width scalar byte in the queued value.
    std::size_t semantic_byte_weight = 0;

    bool operator==(const SyncReplicaNetworkMessage&) const = default;
};

enum class SyncReplicaDeliveryOrder {
    OldestFirst,
    NewestFirst,
};

struct SyncReplicaNetworkSimulatorLimits final {
    // Queued frames own complete immutable operations. Bound both cardinality
    // and semantic bytes rather than assuming the operation-history cap also
    // bounds partitions, duplicates, repeated anti-entropy, or large clocks.
    std::size_t max_pending_messages = 1000000;
    std::size_t max_pending_semantic_bytes = 256U * 1024U * 1024U;
};

class SyncReplicaNetworkSimulator final {
public:
    explicit SyncReplicaNetworkSimulator(
        std::string folder_id,
        SyncReplicaModelLimits model_limits = {},
        SyncReplicaNetworkSimulatorLimits network_limits = {});

    void add_replica_or_throw(SyncReplicaActor actor);

    [[nodiscard]] bool has_replica(
        const std::string& device_id) const noexcept;

    [[nodiscard]] bool replica_is_live(
        const std::string& device_id) const;

    [[nodiscard]] const SyncReplicaModel& replica_or_throw(
        const std::string& device_id) const;

    [[nodiscard]] SyncReplicaDurableState durable_state_or_throw(
        const std::string& device_id) const;

    [[nodiscard]] SyncReplicaOperation create_local_file_or_throw(
        const std::string& device_id,
        std::string canonical_path,
        std::uint64_t size_bytes,
        std::string content_sha256);

    [[nodiscard]] SyncReplicaOperation create_local_tombstone_or_throw(
        const std::string& device_id,
        std::string canonical_path);

    [[nodiscard]] SyncReplicaOperation resolve_local_file_conflict_or_throw(
        const std::string& device_id,
        std::string canonical_path,
        std::span<const std::string> expected_visible_operation_ids,
        std::uint64_t size_bytes,
        std::string content_sha256);

    void crash_or_throw(const std::string& device_id);
    void restart_or_throw(const std::string& device_id);

    void partition_direction_or_throw(
        const std::string& source_device_id,
        const std::string& destination_device_id);

    void partition_bidirectional_or_throw(
        const std::string& first_device_id,
        const std::string& second_device_id);

    void heal_direction_or_throw(
        const std::string& source_device_id,
        const std::string& destination_device_id);

    void heal_bidirectional_or_throw(
        const std::string& first_device_id,
        const std::string& second_device_id);

    void heal_all() noexcept;

    [[nodiscard]] bool direction_is_partitioned(
        const std::string& source_device_id,
        const std::string& destination_device_id) const;

    // Enqueues a point-in-time copy of every retained source envelope,
    // including pending and quarantined evidence. Duplicate anti-entropy is
    // intentional and exercises idempotent admission.
    [[nodiscard]] std::size_t enqueue_anti_entropy_or_throw(
        const std::string& source_device_id,
        const std::string& destination_device_id);

    [[nodiscard]] std::size_t enqueue_full_mesh_anti_entropy_or_throw();

    [[nodiscard]] std::vector<std::uint64_t> pending_message_ids() const;

    [[nodiscard]] std::optional<SyncReplicaNetworkMessage> message_by_id(
        std::uint64_t message_id) const;

    [[nodiscard]] std::uint64_t duplicate_message_or_throw(
        std::uint64_t message_id);

    [[nodiscard]] bool drop_message(std::uint64_t message_id) noexcept;

    // A transport block returns nullopt. A valid capacity block returns an
    // explicit CapacityBlocked admission and leaves the message queued. Exact
    // duplicates are retired without cloning the destination graph or rewriting
    // its durable snapshot; insertions atomically update live and durable state.
    [[nodiscard]] std::optional<SyncReplicaAdmission>
    deliver_message_or_throw(std::uint64_t message_id);

    [[nodiscard]] std::size_t drain_deliverable_or_throw(
        SyncReplicaDeliveryOrder order,
        std::size_t max_deliveries = 1000000);

    [[nodiscard]] std::size_t pending_message_count() const noexcept {
        return messages_.size();
    }

    [[nodiscard]] std::size_t pending_message_semantic_bytes() const noexcept {
        return pending_message_semantic_bytes_;
    }

    [[nodiscard]] bool all_replicas_live() const noexcept;
    [[nodiscard]] bool all_operation_sets_equal_or_throw() const;
    [[nodiscard]] bool all_evidence_sets_equal_or_throw() const;
    [[nodiscard]] bool all_visible_states_equal_or_throw() const;

private:
    struct Node final {
        SyncReplicaActor actor;
        std::optional<SyncReplicaModel> live;
        SyncReplicaDurableState durable;
    };

    struct DirectionKey final {
        std::string source_device_id;
        std::string destination_device_id;

        DirectionKey(std::string source, std::string destination)
            : source_device_id(std::move(source)),
              destination_device_id(std::move(destination)) {}
    };

    struct DirectionView final {
        std::string_view source_device_id;
        std::string_view destination_device_id;
    };

    struct DirectionLess final {
        using is_transparent = void;

        [[nodiscard]] static bool compare(
            std::string_view left_source,
            std::string_view left_destination,
            std::string_view right_source,
            std::string_view right_destination) noexcept {
            if (left_source < right_source) return true;
            if (right_source < left_source) return false;
            return left_destination < right_destination;
        }

        [[nodiscard]] bool operator()(
            const DirectionKey& left,
            const DirectionKey& right) const noexcept {
            return compare(
                left.source_device_id,
                left.destination_device_id,
                right.source_device_id,
                right.destination_device_id);
        }

        [[nodiscard]] bool operator()(
            const DirectionKey& left,
            const DirectionView& right) const noexcept {
            return compare(
                left.source_device_id,
                left.destination_device_id,
                right.source_device_id,
                right.destination_device_id);
        }

        [[nodiscard]] bool operator()(
            const DirectionView& left,
            const DirectionKey& right) const noexcept {
            return compare(
                left.source_device_id,
                left.destination_device_id,
                right.source_device_id,
                right.destination_device_id);
        }
    };

    [[nodiscard]] Node& node_or_throw(const std::string& device_id);
    [[nodiscard]] const Node& node_or_throw(
        const std::string& device_id) const;

    [[nodiscard]] SyncReplicaModel& live_model_or_throw(
        const std::string& device_id);

    [[nodiscard]] const SyncReplicaModel& live_model_or_throw(
        const std::string& device_id) const;

    // The entire batch is validated and staged before queue publication. If
    // allocation, identifier exhaustion, or the independent queue budget
    // fails, no prefix is visible and next_message_id_ is unchanged.
    [[nodiscard]] std::vector<std::uint64_t>
    enqueue_messages_atomically_or_throw(
        std::vector<SyncReplicaNetworkMessage> batch);

    [[nodiscard]] std::vector<SyncReplicaNetworkMessage>
    make_broadcast_batch_or_throw(
        const std::string& source_device_id,
        const SyncReplicaOperation& operation) const;

    // Callers preflight before allocating/copying a batch; the publication
    // owner repeats the same checks after staging as defense in depth.
    void preflight_enqueue_budget_or_throw(
        std::size_t batch_count,
        std::size_t batch_semantic_bytes) const;

    [[nodiscard]] static std::size_t
    message_semantic_byte_weight_or_throw(
        const std::string& source_device_id,
        const std::string& destination_device_id,
        const SyncReplicaOperation& operation);

    [[nodiscard]] static std::size_t
    message_semantic_byte_weight_or_throw(
        const SyncReplicaNetworkMessage& message);

    void erase_message_noexcept(
        std::map<std::uint64_t, SyncReplicaNetworkMessage>::iterator message)
        noexcept;

    void commit_candidate_noexcept(
        Node& node,
        SyncReplicaModel&& candidate,
        SyncReplicaDurableState&& durable) noexcept;

    [[nodiscard]] bool direction_is_partitioned_noexcept(
        std::string_view source_device_id,
        std::string_view destination_device_id) const noexcept;

    void erase_partition_direction_noexcept(
        std::string_view source_device_id,
        std::string_view destination_device_id) noexcept;

    std::string folder_id_;
    SyncReplicaModelLimits limits_;
    SyncReplicaNetworkSimulatorLimits network_limits_;
    std::map<std::string, Node> nodes_;
    std::map<std::uint64_t, SyncReplicaNetworkMessage> messages_;
    std::size_t pending_message_semantic_bytes_ = 0;
    std::set<DirectionKey, DirectionLess> partitioned_directions_;
    std::uint64_t next_message_id_ = 1;
};

}  // namespace anonsync
