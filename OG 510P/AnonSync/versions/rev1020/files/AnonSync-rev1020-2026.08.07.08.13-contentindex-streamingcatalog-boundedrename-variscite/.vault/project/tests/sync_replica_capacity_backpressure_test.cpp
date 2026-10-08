#include "sha256_digest.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_network_simulator.hpp"

#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <new>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

struct AllocationProbe final {
    std::size_t attempts = 0U;
    std::size_t fail_at = 0U;
    bool armed = false;
};

AllocationProbe g_allocation_probe;

[[nodiscard]] bool allocation_should_fail() noexcept {
    if (!g_allocation_probe.armed) return false;
    ++g_allocation_probe.attempts;
    return g_allocation_probe.fail_at != 0U &&
           g_allocation_probe.attempts == g_allocation_probe.fail_at;
}

[[nodiscard]] void* allocate_or_throw(std::size_t size) {
    if (allocation_should_fail()) throw std::bad_alloc();
    void* const memory = std::malloc(size == 0U ? 1U : size);
    if (memory == nullptr) throw std::bad_alloc();
    return memory;
}

class AllocationArm final {
public:
    explicit AllocationArm(std::size_t fail_at) noexcept {
        g_allocation_probe.attempts = 0U;
        g_allocation_probe.fail_at = fail_at;
        g_allocation_probe.armed = true;
    }

    AllocationArm(const AllocationArm&) = delete;
    AllocationArm& operator=(const AllocationArm&) = delete;

    ~AllocationArm() { g_allocation_probe.armed = false; }

    void disarm() noexcept { g_allocation_probe.armed = false; }

    [[nodiscard]] std::size_t attempts() const noexcept {
        return g_allocation_probe.attempts;
    }
};

}  // namespace

void* operator new(std::size_t size) {
    return allocate_or_throw(size);
}

void* operator new[](std::size_t size) {
    return allocate_or_throw(size);
}

void operator delete(void* memory) noexcept {
    std::free(memory);
}

void operator delete[](void* memory) noexcept {
    std::free(memory);
}

void operator delete(void* memory, std::size_t) noexcept {
    std::free(memory);
}

void operator delete[](void* memory, std::size_t) noexcept {
    std::free(memory);
}

namespace {

void require(bool condition, const std::string& message, std::size_t& checks) {
    ++checks;
    if (!condition) throw std::runtime_error(message);
}

template <typename ExpectedException, typename Callable>
void require_throws(
    Callable&& callable,
    const std::string& message,
    std::size_t& checks) {
    bool threw_expected = false;
    try {
        std::forward<Callable>(callable)();
    } catch (const ExpectedException&) {
        threw_expected = true;
    } catch (...) {
    }
    require(threw_expected, message, checks);
}

anonsync::SyncReplicaActor actor(
    const std::string& device_id,
    std::uint64_t epoch) {
    return {device_id, epoch};
}

anonsync::SyncReplicaOperation root_operation(
    const std::string& folder,
    const anonsync::SyncReplicaActor& operation_actor,
    const std::string& path,
    const std::string& payload) {
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = path;
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = static_cast<std::uint64_t>(payload.size());
    operation.content_sha256 = anonsync::sha256_hex(payload);
    operation.dot = {operation_actor, 1U};
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

anonsync::SyncReplicaModelLimits model_limits(
    std::uint64_t max_operations) {
    anonsync::SyncReplicaModelLimits limits;
    limits.max_operations = max_operations;
    limits.max_context_entries = 64U;
    limits.max_predecessor_ids = 64U;
    limits.max_canonical_operation_bytes = 256U * 1024U;
    limits.max_retained_canonical_bytes = 16U * 1024U * 1024U;
    limits.max_retained_context_entries = 4096U;
    limits.max_retained_predecessor_ids = 4096U;
    return limits;
}

std::vector<std::uint64_t> matching_message_ids(
    const anonsync::SyncReplicaNetworkSimulator& simulator,
    const std::string& source,
    const std::string& destination,
    const std::string& operation_id) {
    std::vector<std::uint64_t> matches;
    for (const std::uint64_t message_id : simulator.pending_message_ids()) {
        const std::optional<anonsync::SyncReplicaNetworkMessage> message =
            simulator.message_by_id(message_id);
        if (message.has_value() &&
            message->source_device_id == source &&
            message->destination_device_id == destination &&
            message->operation.operation_id == operation_id) {
            matches.push_back(message_id);
        }
    }
    return matches;
}

}  // namespace

int main() {
    using namespace anonsync;

    try {
        std::size_t checks = 0U;
        const std::string folder = "folder-capacity-backpressure";
        const SyncReplicaActor local = actor("device-capacity-local", 801U);
        const SyncReplicaOperation retained = root_operation(
            folder,
            actor("device-capacity-retained", 802U),
            "capacity/retained.bin",
            "retained");
        const SyncReplicaOperation blocked = root_operation(
            folder,
            actor("device-capacity-blocked", 803U),
            "capacity/blocked.bin",
            "blocked");

        const SyncReplicaModelLimits one_operation = model_limits(1U);
        SyncReplicaModel model(folder, local, one_operation);
        require(
            model.accept_remote_or_throw(retained) ==
                SyncReplicaAdmission::InsertedActive,
            "capacity fixture did not retain its first valid envelope",
            checks);

        const SyncReplicaRemoteAdmissionPreflight duplicate_preflight =
            model.preflight_remote_admission_or_throw(retained);
        require(
            duplicate_preflight.readiness ==
                    SyncReplicaRemoteReadiness::Duplicate &&
                duplicate_preflight.operations.retained == 1U &&
                duplicate_preflight.operations.incoming == 0U &&
                !duplicate_preflight.operations.would_exceed() &&
                duplicate_preflight.canonical_bytes.incoming == 0U &&
                duplicate_preflight.context_entries.incoming == 0U &&
                duplicate_preflight.predecessor_ids.incoming == 0U,
            "exact replay did not report zero-charge duplicate readiness at capacity",
            checks);

        const SyncReplicaRemoteAdmissionPreflight blocked_preflight =
            model.preflight_remote_admission_or_throw(blocked);
        require(
            blocked_preflight.readiness ==
                    SyncReplicaRemoteReadiness::CapacityBlocked &&
                blocked_preflight.operations == SyncReplicaResourceBudget{
                    1U, 1U, 1U} &&
                blocked_preflight.operations.would_exceed() &&
                blocked_preflight.canonical_bytes.incoming ==
                    sync_replica_operation_canonical_size_or_throw(
                        blocked, one_operation) &&
                !blocked_preflight.canonical_bytes.would_exceed() &&
                !blocked_preflight.context_entries.would_exceed() &&
                !blocked_preflight.predecessor_ids.would_exceed(),
            "preflight did not expose the exact operation-count capacity reason",
            checks);

        const SyncReplicaDurableState capacity_baseline = model.durable_state();
        const std::string evidence_digest = model.evidence_set_digest();
        const std::string visible_digest = model.visible_state_digest();
        require(
            model.accept_remote_or_throw(blocked) ==
                SyncReplicaAdmission::CapacityBlocked,
            "valid evidence at local capacity was not returned as retryable backpressure",
            checks);
        require(
            model.durable_state() == capacity_baseline &&
                model.evidence_set_digest() == evidence_digest &&
                model.visible_state_digest() == visible_digest &&
                model.evidence_count() == 1U &&
                !model.evidence_state(blocked.operation_id).has_value(),
            "capacity-blocked evidence mutated or became quarantined retained state",
            checks);

        SyncReplicaOperation malformed = blocked;
        malformed.canonical_path = "../escape";
        require_throws<std::invalid_argument>(
            [&] {
                (void)model.preflight_remote_admission_or_throw(malformed);
            },
            "full capacity masked malformed evidence as backpressure",
            checks);
        const SyncReplicaOperation other_folder = root_operation(
            "folder-capacity-other",
            actor("device-capacity-other", 804U),
            "capacity/other.bin",
            "other");
        require_throws<std::invalid_argument>(
            [&] {
                (void)model.preflight_remote_admission_or_throw(other_folder);
            },
            "full capacity masked a valid envelope from another folder",
            checks);

        SyncReplicaModel retriable = SyncReplicaModel::restore_or_throw(
            capacity_baseline, model_limits(2U));
        require(
            retriable.accept_remote_or_throw(blocked) ==
                    SyncReplicaAdmission::InsertedActive &&
                retriable.evidence_state(blocked.operation_id) ==
                    SyncReplicaEvidenceState::Active,
            "the same valid envelope did not succeed after local capacity expansion",
            checks);

        const std::string source_id = "device-capacity-source";
        const std::string destination_id = "device-capacity-destination";
        SyncReplicaNetworkSimulator simulator(folder, model_limits(2U));
        simulator.add_replica_or_throw(actor(source_id, 810U));
        simulator.add_replica_or_throw(actor(destination_id, 811U));
        simulator.partition_direction_or_throw(destination_id, source_id);

        const SyncReplicaOperation shared =
            simulator.create_local_file_or_throw(
                source_id,
                "network/shared.bin",
                6U,
                sha256_hex("shared"));
        const std::vector<std::uint64_t> initial_shared_messages =
            matching_message_ids(
                simulator, source_id, destination_id, shared.operation_id);
        require(
            initial_shared_messages.size() == 1U &&
                simulator.deliver_message_or_throw(
                    initial_shared_messages.front()) ==
                    SyncReplicaAdmission::InsertedActive,
            "network fixture did not establish one shared retained envelope",
            checks);

        (void)simulator.create_local_file_or_throw(
            destination_id,
            "network/destination.bin",
            11U,
            sha256_hex("destination"));
        const SyncReplicaOperation unique =
            simulator.create_local_file_or_throw(
                source_id,
                "network/unique.bin",
                6U,
                sha256_hex("unique"));
        require(
            simulator.replica_or_throw(destination_id).evidence_count() == 2U,
            "network destination did not reach its configured evidence capacity",
            checks);
        require(
            simulator.enqueue_anti_entropy_or_throw(
                source_id, destination_id) == 2U,
            "network anti-entropy did not enqueue shared and unique evidence",
            checks);

        std::vector<std::uint64_t> shared_duplicates = matching_message_ids(
            simulator, source_id, destination_id, shared.operation_id);
        std::vector<std::uint64_t> blocked_unique_messages =
            matching_message_ids(
                simulator, source_id, destination_id, unique.operation_id);
        require(
            shared_duplicates.size() == 1U &&
                blocked_unique_messages.size() == 2U,
            "network queue did not contain one duplicate and two capacity-blocked retries",
            checks);
        const std::uint64_t second_duplicate =
            simulator.duplicate_message_or_throw(shared_duplicates.front());
        shared_duplicates.push_back(second_duplicate);

        const SyncReplicaDurableState network_baseline =
            simulator.durable_state_or_throw(destination_id);
        std::optional<SyncReplicaAdmission> zero_allocation_duplicate_result;
        std::size_t duplicate_allocation_attempts = 0U;
        {
            AllocationArm arm(1U);
            zero_allocation_duplicate_result =
                simulator.deliver_message_or_throw(
                    shared_duplicates.front());
            duplicate_allocation_attempts = arm.attempts();
            arm.disarm();
        }
        require(
            zero_allocation_duplicate_result ==
                    SyncReplicaAdmission::Duplicate &&
                duplicate_allocation_attempts == 0U &&
                simulator.durable_state_or_throw(destination_id) ==
                    network_baseline,
            "exact duplicate delivery allocated, cloned the graph, or rewrote durable state",
            checks);

        const std::size_t queue_count_before_block =
            simulator.pending_message_count();
        const std::size_t queue_bytes_before_block =
            simulator.pending_message_semantic_bytes();
        require(
            simulator.deliver_message_or_throw(
                blocked_unique_messages.front()) ==
                    SyncReplicaAdmission::CapacityBlocked &&
                simulator.pending_message_count() ==
                    queue_count_before_block &&
                simulator.pending_message_semantic_bytes() ==
                    queue_bytes_before_block &&
                simulator.message_by_id(
                    blocked_unique_messages.front()).has_value() &&
                simulator.durable_state_or_throw(destination_id) ==
                    network_baseline,
            "network capacity block consumed the queued retry or changed destination durability",
            checks);

        shared_duplicates = matching_message_ids(
            simulator, source_id, destination_id, shared.operation_id);
        require(
            shared_duplicates.size() == 1U,
            "zero-allocation duplicate retirement did not leave exactly one drainable duplicate",
            checks);
        const std::optional<SyncReplicaNetworkMessage> drainable_duplicate =
            simulator.message_by_id(shared_duplicates.front());
        require(
            drainable_duplicate.has_value(),
            "drainable duplicate disappeared before the fairness check",
            checks);
        const std::size_t bytes_before_drain =
            simulator.pending_message_semantic_bytes();
        require(
            simulator.drain_deliverable_or_throw(
                SyncReplicaDeliveryOrder::OldestFirst, 100U) == 1U,
            "drain did not skip capacity-blocked messages and retire the later duplicate",
            checks);
        require(
            matching_message_ids(
                simulator, source_id, destination_id, shared.operation_id)
                    .empty() &&
                matching_message_ids(
                    simulator, source_id, destination_id, unique.operation_id)
                    .size() == 2U &&
                simulator.pending_message_semantic_bytes() ==
                    bytes_before_drain -
                        drainable_duplicate->semantic_byte_weight &&
                simulator.durable_state_or_throw(destination_id) ==
                    network_baseline,
            "capacity-aware drain lost a retry, retained a duplicate, or rewrote destination state",
            checks);
        require(
            simulator.drain_deliverable_or_throw(
                SyncReplicaDeliveryOrder::NewestFirst, 100U) == 0U,
            "newest-first drain counted or spun over capacity-blocked retries",
            checks);

        std::cout
            << "sync replica capacity backpressure tests passed ("
            << checks
            << " checks, validity separation, zero-clone duplicate, and drain fairness)\n";
        return 0;
    } catch (const std::exception& error) {
        g_allocation_probe.armed = false;
        std::cerr
            << "sync replica capacity backpressure tests failed: "
            << error.what() << '\n';
        return 1;
    }
}
