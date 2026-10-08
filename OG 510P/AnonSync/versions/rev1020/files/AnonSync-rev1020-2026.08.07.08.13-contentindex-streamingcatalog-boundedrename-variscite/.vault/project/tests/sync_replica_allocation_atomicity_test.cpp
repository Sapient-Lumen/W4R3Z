#include "sha256_digest.hpp"
#include "sync_replica_model.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <new>
#include <stdexcept>
#include <string>
#include <utility>

namespace {

struct AllocationFaultState final {
    std::size_t attempts = 0U;
    std::size_t fail_at = 0U;
    bool armed = false;
};

AllocationFaultState g_allocation_fault;

bool allocation_should_fail() noexcept {
    if (!g_allocation_fault.armed) return false;
    ++g_allocation_fault.attempts;
    return g_allocation_fault.fail_at != 0U &&
           g_allocation_fault.attempts == g_allocation_fault.fail_at;
}

void* allocate_or_throw(std::size_t size) {
    if (allocation_should_fail()) throw std::bad_alloc();
    void* const memory = std::malloc(size == 0U ? 1U : size);
    if (memory == nullptr) throw std::bad_alloc();
    return memory;
}

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

anonsync::SyncReplicaActor actor(
    const std::string& device_id,
    std::uint64_t epoch) {
    return {device_id, epoch};
}

anonsync::SyncReplicaOperation independent_root(
    const std::string& folder,
    const std::string& device_id,
    std::uint64_t epoch,
    const std::string& payload) {
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = "fault/root.bin";
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = static_cast<std::uint64_t>(payload.size());
    operation.content_sha256 = anonsync::sha256_hex(payload);
    operation.dot = {actor(device_id, epoch), 1U};
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

class AllocationArm final {
public:
    explicit AllocationArm(std::size_t fail_at) noexcept {
        g_allocation_fault.attempts = 0U;
        g_allocation_fault.fail_at = fail_at;
        g_allocation_fault.armed = true;
    }

    AllocationArm(const AllocationArm&) = delete;
    AllocationArm& operator=(const AllocationArm&) = delete;

    ~AllocationArm() {
        g_allocation_fault.armed = false;
    }

    void disarm() noexcept {
        g_allocation_fault.armed = false;
    }

    [[nodiscard]] std::size_t attempts() const noexcept {
        return g_allocation_fault.attempts;
    }
};

struct SweepResult final {
    std::size_t injected_failures = 0U;
    std::size_t successful_path_allocations = 0U;
};

struct RetainedCounters final {
    std::uint64_t canonical_bytes = 0U;
    std::uint64_t context_entries = 0U;
    std::uint64_t predecessor_ids = 0U;
};

RetainedCounters retained_counters(
    const anonsync::SyncReplicaDurableState& durable,
    const anonsync::SyncReplicaModelLimits& limits) {
    RetainedCounters counters;
    for (const auto& operation : durable.operations) {
        counters.canonical_bytes +=
            anonsync::sync_replica_operation_canonical_size_or_throw(
                operation, limits);
        counters.context_entries += static_cast<std::uint64_t>(
            operation.causal_context.size());
        counters.predecessor_ids += static_cast<std::uint64_t>(
            operation.predecessor_operation_ids.size());
    }
    return counters;
}

SweepResult sweep_local_mint(
    const anonsync::SyncReplicaDurableState& baseline,
    const anonsync::SyncReplicaModelLimits& limits,
    const std::string& path,
    const std::string& content_sha256,
    std::size_t& checks) {
    constexpr std::size_t kMaxFailpoint = 4096U;
    SweepResult result;
    const RetainedCounters baseline_counters =
        retained_counters(baseline, limits);
    for (std::size_t fail_at = 1U;
         fail_at <= kMaxFailpoint; ++fail_at) {
        anonsync::SyncReplicaModel model =
            anonsync::SyncReplicaModel::restore_or_throw(baseline, limits);
        bool allocation_failed = false;
        std::size_t attempts = 0U;
        anonsync::SyncReplicaOperation minted;
        {
            AllocationArm arm(fail_at);
            try {
                minted = model.create_local_file_or_throw(
                    path, 17U, content_sha256);
            } catch (const std::bad_alloc&) {
                allocation_failed = true;
            } catch (...) {
                arm.disarm();
                throw;
            }
            attempts = arm.attempts();
            arm.disarm();
        }

        if (allocation_failed) {
            ++result.injected_failures;
            require(
                model.durable_state() == baseline,
                "allocation-failed local mint changed durable semantics",
                checks);
            require(
                !model.local_actor_compromised() &&
                    model.last_local_counter() == baseline.last_local_counter &&
                    model.evidence_count() == baseline.operations.size() &&
                    model.retained_canonical_bytes() ==
                        baseline_counters.canonical_bytes &&
                    model.retained_context_entry_count() ==
                        baseline_counters.context_entries &&
                    model.retained_predecessor_id_count() ==
                        baseline_counters.predecessor_ids,
                "allocation-failed local mint changed live authority",
                checks);
            continue;
        }

        result.successful_path_allocations = attempts;
        require(
            fail_at == attempts + 1U,
            "local allocation sweep did not cover every successful-path allocation",
            checks);
        require(
            model.last_local_counter() == baseline.last_local_counter + 1U &&
                model.evidence_count() == baseline.operations.size() + 1U &&
                !model.local_actor_compromised() &&
                model.retained_canonical_bytes() ==
                    baseline_counters.canonical_bytes +
                        anonsync::sync_replica_operation_canonical_size_or_throw(
                            minted, limits) &&
                model.retained_context_entry_count() ==
                    baseline_counters.context_entries +
                        minted.causal_context.size() &&
                model.retained_predecessor_id_count() ==
                    baseline_counters.predecessor_ids +
                        minted.predecessor_operation_ids.size(),
            "successful local mint did not publish one complete operation",
            checks);
        return result;
    }
    throw std::runtime_error(
        "local allocation sweep exceeded its failpoint bound");
}

SweepResult sweep_remote_admission(
    const anonsync::SyncReplicaDurableState& baseline,
    const anonsync::SyncReplicaModelLimits& limits,
    const anonsync::SyncReplicaOperation& incoming,
    std::size_t& checks) {
    constexpr std::size_t kMaxFailpoint = 4096U;
    SweepResult result;
    const RetainedCounters baseline_counters =
        retained_counters(baseline, limits);
    const std::uint64_t incoming_canonical_bytes =
        anonsync::sync_replica_operation_canonical_size_or_throw(
            incoming, limits);
    for (std::size_t fail_at = 1U;
         fail_at <= kMaxFailpoint; ++fail_at) {
        anonsync::SyncReplicaModel model =
            anonsync::SyncReplicaModel::restore_or_throw(baseline, limits);
        bool allocation_failed = false;
        std::size_t attempts = 0U;
        anonsync::SyncReplicaAdmission admission =
            anonsync::SyncReplicaAdmission::Duplicate;
        {
            AllocationArm arm(fail_at);
            try {
                admission = model.accept_remote_or_throw(incoming);
            } catch (const std::bad_alloc&) {
                allocation_failed = true;
            } catch (...) {
                arm.disarm();
                throw;
            }
            attempts = arm.attempts();
            arm.disarm();
        }

        if (allocation_failed) {
            ++result.injected_failures;
            require(
                model.durable_state() == baseline,
                "allocation-failed remote admission retained partial evidence",
                checks);
            require(
                !model.evidence_operation_by_id(incoming.operation_id)
                     .has_value() &&
                    model.retained_canonical_bytes() ==
                        baseline_counters.canonical_bytes &&
                    model.retained_context_entry_count() ==
                        baseline_counters.context_entries &&
                    model.retained_predecessor_id_count() ==
                        baseline_counters.predecessor_ids,
                "allocation-failed remote admission leaked the candidate ID",
                checks);
            continue;
        }

        result.successful_path_allocations = attempts;
        require(
            fail_at == attempts + 1U,
            "remote allocation sweep did not cover every successful-path allocation",
            checks);
        require(
            admission == anonsync::SyncReplicaAdmission::InsertedActive &&
                model.evidence_count() == baseline.operations.size() + 1U &&
                model.operation_by_id(incoming.operation_id).has_value() &&
                model.retained_canonical_bytes() ==
                    baseline_counters.canonical_bytes +
                        incoming_canonical_bytes &&
                model.retained_context_entry_count() ==
                    baseline_counters.context_entries +
                        incoming.causal_context.size() &&
                model.retained_predecessor_id_count() ==
                    baseline_counters.predecessor_ids +
                        incoming.predecessor_operation_ids.size(),
            "successful remote admission did not publish one active operation",
            checks);
        return result;
    }
    throw std::runtime_error(
        "remote allocation sweep exceeded its failpoint bound");
}

}  // namespace

int main() {
    using namespace anonsync;

    try {
        std::size_t checks = 0U;
        const std::string folder = "folder-allocation-atomicity";
        SyncReplicaModelLimits limits;
        limits.max_operations = 64U;
        limits.max_context_entries = 32U;
        limits.max_predecessor_ids = 32U;
        limits.max_canonical_operation_bytes = 64U * 1024U;

        SyncReplicaModel seed(
            folder,
            actor("device-allocation-local", 501U),
            limits);
        for (std::size_t index = 0U; index < 4U; ++index) {
            const SyncReplicaOperation root = independent_root(
                folder,
                "device-allocation-root-" + std::to_string(index),
                510U + index,
                "root-payload-" + std::to_string(index));
            require(
                seed.accept_remote_or_throw(root) ==
                    SyncReplicaAdmission::InsertedActive,
                "allocation fixture root did not activate",
                checks);
        }
        const SyncReplicaOperation first_local =
            seed.create_local_file_or_throw(
                "fault/local.bin",
                16U,
                sha256_hex("first-local"));
        require(
            seed.causal_head_operation_ids() ==
                std::vector<std::string>{first_local.operation_id},
            "allocation fixture did not collapse to one local head",
            checks);

        const SyncReplicaDurableState baseline = seed.durable_state();

        // Idempotent anti-entropy replay must not repeatedly materialize and
        // hash an envelope that this immutable evidence owner already holds.
        SyncReplicaModel duplicate_probe =
            SyncReplicaModel::restore_or_throw(baseline, limits);
        SyncReplicaAdmission duplicate_admission =
            SyncReplicaAdmission::InsertedActive;
        std::size_t duplicate_attempts = 0U;
        {
            AllocationArm arm(1U);
            duplicate_admission =
                duplicate_probe.accept_remote_or_throw(first_local);
            duplicate_attempts = arm.attempts();
            arm.disarm();
        }
        require(
            duplicate_admission == SyncReplicaAdmission::Duplicate &&
                duplicate_attempts == 0U &&
                duplicate_probe.durable_state() == baseline,
            "exact duplicate replay allocated or changed retained evidence",
            checks);

        const std::string next_path = "fault/local.bin";
        const std::string next_digest = sha256_hex("second-local");
        const SweepResult local = sweep_local_mint(
            baseline, limits, next_path, next_digest, checks);
        require(
            local.injected_failures == local.successful_path_allocations &&
                local.injected_failures > 20U,
            "local mint allocation sweep was unexpectedly shallow",
            checks);

        SyncReplicaOperation incoming;
        incoming.folder_id = folder;
        incoming.canonical_path = "fault/remote.bin";
        incoming.kind = SyncReplicaValueKind::File;
        incoming.size_bytes = 19U;
        incoming.content_sha256 = sha256_hex("remote-candidate");
        incoming.dot = {actor("device-allocation-remote", 601U), 1U};
        incoming.causal_context = seed.observed_context();
        incoming.predecessor_operation_ids =
            seed.causal_head_operation_ids();
        incoming.operation_id =
            make_sync_replica_operation_id_or_throw(incoming, limits);

        const SweepResult remote = sweep_remote_admission(
            baseline, limits, incoming, checks);
        require(
            remote.injected_failures ==
                    remote.successful_path_allocations &&
                remote.injected_failures > 20U,
            "remote admission allocation sweep was unexpectedly shallow",
            checks);

        std::cout
            << "sync replica allocation atomicity tests passed ("
            << checks << " checks, "
            << local.injected_failures
            << " local and "
            << remote.injected_failures
            << " remote allocation cutpoints)\n";
        return 0;
    } catch (const std::exception& error) {
        g_allocation_fault.armed = false;
        std::cerr
            << "sync replica allocation atomicity tests failed: "
            << error.what() << '\n';
        return 1;
    }
}
