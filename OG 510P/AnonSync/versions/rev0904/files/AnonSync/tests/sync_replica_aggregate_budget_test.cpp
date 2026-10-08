#include "sha256_digest.hpp"
#include "sync_replica_model.hpp"

#include <algorithm>
#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

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

anonsync::SyncReplicaOperation pending_operation(
    const std::string& folder,
    const anonsync::SyncReplicaActor& operation_actor,
    const anonsync::SyncReplicaActor& missing_actor,
    const std::string& path,
    const std::string& label) {
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = path;
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = static_cast<std::uint64_t>(label.size());
    operation.content_sha256 = anonsync::sha256_hex("pending:" + label);
    operation.dot = {operation_actor, 1U};
    operation.causal_context = {{missing_actor, 1U}};
    operation.predecessor_operation_ids = {
        anonsync::sha256_hex("missing-parent:" + label)};
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

anonsync::SyncReplicaOperation same_dot_fork(
    const std::string& folder,
    const anonsync::SyncReplicaActor& fork_actor,
    const std::string& payload) {
    return root_operation(
        folder, fork_actor, "budget/fork.bin", payload);
}

std::uint64_t canonical_size(
    const anonsync::SyncReplicaOperation& operation) {
    return anonsync::sync_replica_operation_canonical_size_or_throw(operation);
}

std::uint64_t sum_canonical_sizes(
    const std::vector<anonsync::SyncReplicaOperation>& operations) {
    std::uint64_t total = 0U;
    for (const auto& operation : operations) {
        total += canonical_size(operation);
    }
    return total;
}

anonsync::SyncReplicaModelLimits base_limits() {
    anonsync::SyncReplicaModelLimits limits;
    limits.max_operations = 32U;
    limits.max_context_entries = 4U;
    limits.max_predecessor_ids = 4U;
    limits.max_canonical_operation_bytes = 64U * 1024U;
    limits.max_retained_canonical_bytes = 4U * 1024U * 1024U;
    limits.max_retained_context_entries = 64U;
    limits.max_retained_predecessor_ids = 64U;
    return limits;
}

}  // namespace

int main() {
    using namespace anonsync;

    try {
        std::size_t checks = 0U;
        const std::string folder = "folder-aggregate-budget";
        const SyncReplicaActor local_actor =
            actor("device-budget-local", 701U);

        SyncReplicaOperation measured;
        measured.folder_id = folder;
        measured.canonical_path = "budget/measured.bin";
        measured.kind = SyncReplicaValueKind::File;
        measured.size_bytes = 8U;
        measured.content_sha256 = sha256_hex("measured");
        measured.dot = {actor("device-budget-measured", 702U), 1U};
        const std::uint64_t measured_size = canonical_size(measured);
        require(
            measured_size ==
                encode_sync_replica_operation_canonical_or_throw(measured)
                    .size(),
            "exact canonical-size API disagrees with canonical encoding",
            checks);
        measured.operation_id =
            make_sync_replica_operation_id_or_throw(measured);
        require(
            canonical_size(measured) == measured_size,
            "operation_id unexpectedly changed canonical envelope size",
            checks);

        SyncReplicaModelLimits invalid = base_limits();
        invalid.max_retained_canonical_bytes =
            invalid.max_canonical_operation_bytes - 1U;
        require_throws<std::invalid_argument>(
            [&] { SyncReplicaModel model(folder, local_actor, invalid); },
            "limits admitted an envelope larger than the aggregate byte budget",
            checks);
        invalid = base_limits();
        invalid.max_retained_context_entries =
            invalid.max_context_entries - 1U;
        require_throws<std::invalid_argument>(
            [&] { SyncReplicaModel model(folder, local_actor, invalid); },
            "limits admitted a context larger than its aggregate entry budget",
            checks);
        invalid = base_limits();
        invalid.max_retained_predecessor_ids =
            invalid.max_predecessor_ids - 1U;
        require_throws<std::invalid_argument>(
            [&] { SyncReplicaModel model(folder, local_actor, invalid); },
            "limits admitted a predecessor set larger than its aggregate budget",
            checks);

        const SyncReplicaOperation active = root_operation(
            folder,
            actor("device-budget-active", 710U),
            "budget/active.bin",
            "active");
        const SyncReplicaOperation pending = pending_operation(
            folder,
            actor("device-budget-pending", 711U),
            actor("device-budget-missing", 712U),
            "budget/pending.bin",
            "pending");
        const SyncReplicaActor fork_actor =
            actor("device-budget-fork", 713U);
        const SyncReplicaOperation fork_one =
            same_dot_fork(folder, fork_actor, "fork-one");
        const SyncReplicaOperation fork_two =
            same_dot_fork(folder, fork_actor, "fork-two");
        const SyncReplicaOperation overflow = root_operation(
            folder,
            actor("device-budget-overflow", 714U),
            "budget/overflow.bin",
            "overflow");
        const std::vector<SyncReplicaOperation> retained = {
            active, pending, fork_one, fork_two};

        SyncReplicaModelLimits byte_limits = base_limits();
        byte_limits.max_canonical_operation_bytes = std::max({
            canonical_size(active),
            canonical_size(pending),
            canonical_size(fork_one),
            canonical_size(fork_two),
            canonical_size(overflow)});
        byte_limits.max_retained_canonical_bytes =
            sum_canonical_sizes(retained);
        SyncReplicaModel byte_model(folder, local_actor, byte_limits);
        require(
            byte_model.accept_remote_or_throw(active) ==
                SyncReplicaAdmission::InsertedActive,
            "active evidence did not enter the aggregate-byte fixture",
            checks);
        require(
            byte_model.accept_remote_or_throw(pending) ==
                SyncReplicaAdmission::InsertedPending,
            "missing-parent evidence was not retained pending",
            checks);
        require(
            byte_model.accept_remote_or_throw(fork_one) ==
                SyncReplicaAdmission::InsertedActive,
            "first same-dot envelope did not initially activate",
            checks);
        require(
            byte_model.accept_remote_or_throw(fork_two) ==
                SyncReplicaAdmission::InsertedQuarantined,
            "second same-dot envelope did not quarantine the fork",
            checks);
        require(
            byte_model.operation_count() == 1U &&
                byte_model.pending_operation_count() == 1U &&
                byte_model.quarantined_operation_count() == 2U,
            "mixed retained evidence did not cover active, pending, and quarantine states",
            checks);
        require(
            byte_model.retained_canonical_bytes() ==
                byte_limits.max_retained_canonical_bytes &&
                byte_model.retained_context_entry_count() == 1U &&
                byte_model.retained_predecessor_id_count() == 1U,
            "mixed evidence aggregate charges were not exact",
            checks);
        require(
            byte_model.accept_remote_or_throw(fork_two) ==
                    SyncReplicaAdmission::Duplicate &&
                byte_model.retained_canonical_bytes() ==
                    byte_limits.max_retained_canonical_bytes,
            "duplicate evidence consumed aggregate budget",
            checks);
        const SyncReplicaDurableState byte_baseline =
            byte_model.durable_state();
        const SyncReplicaRemoteAdmissionPreflight byte_preflight =
            byte_model.preflight_remote_admission_or_throw(overflow);
        require(
            byte_preflight.readiness ==
                    SyncReplicaRemoteReadiness::CapacityBlocked &&
                byte_preflight.canonical_bytes.retained ==
                    byte_limits.max_retained_canonical_bytes &&
                byte_preflight.canonical_bytes.incoming ==
                    canonical_size(overflow) &&
                byte_preflight.canonical_bytes.would_exceed(),
            "aggregate canonical-byte preflight did not expose the exact local capacity block",
            checks);
        require(
            byte_model.accept_remote_or_throw(overflow) ==
                SyncReplicaAdmission::CapacityBlocked,
            "aggregate canonical-byte ceiling did not return retryable backpressure",
            checks);
        require(
            byte_model.durable_state() == byte_baseline &&
                byte_model.evidence_count() == retained.size() &&
                byte_model.retained_canonical_bytes() ==
                    byte_limits.max_retained_canonical_bytes,
            "rejected byte-budget admission changed retained semantics",
            checks);

        SyncReplicaDurableState move_restore_state = byte_baseline;
        SyncReplicaModel restored = SyncReplicaModel::restore_or_throw(
            std::move(move_restore_state), byte_limits);
        require(
            restored.durable_state() == byte_baseline &&
                restored.retained_canonical_bytes() ==
                    byte_model.retained_canonical_bytes() &&
                restored.retained_context_entry_count() ==
                    byte_model.retained_context_entry_count() &&
                restored.retained_predecessor_id_count() ==
                    byte_model.retained_predecessor_id_count(),
            "move-based restore did not reconstruct exact aggregate charges",
            checks);

        std::vector<SyncReplicaOperation> pending_set;
        for (std::uint64_t index = 0U; index < 3U; ++index) {
            pending_set.push_back(pending_operation(
                folder,
                actor(
                    "device-context-op-" + std::to_string(index),
                    720U + index),
                actor(
                    "device-context-missing-" + std::to_string(index),
                    730U + index),
                "budget/context-" + std::to_string(index) + ".bin",
                "context-" + std::to_string(index)));
        }
        SyncReplicaModelLimits context_limits = base_limits();
        context_limits.max_context_entries = 1U;
        context_limits.max_retained_context_entries = 2U;
        SyncReplicaModel context_model(folder, local_actor, context_limits);
        require(
            context_model.accept_remote_or_throw(pending_set[0]) ==
                    SyncReplicaAdmission::InsertedPending &&
                context_model.accept_remote_or_throw(pending_set[1]) ==
                    SyncReplicaAdmission::InsertedPending,
            "context-budget fixture did not retain its first two envelopes",
            checks);
        const SyncReplicaDurableState context_baseline =
            context_model.durable_state();
        require(
            context_model.accept_remote_or_throw(pending_set[2]) ==
                SyncReplicaAdmission::CapacityBlocked,
            "aggregate context-entry ceiling did not return retryable backpressure",
            checks);
        require(
            context_model.durable_state() == context_baseline &&
                context_model.retained_context_entry_count() == 2U,
            "context-budget rejection partially retained an envelope",
            checks);
        SyncReplicaModelLimits context_restore_limits = context_limits;
        context_restore_limits.max_retained_context_entries = 1U;
        require_throws<std::length_error>(
            [&] {
                (void)SyncReplicaModel::restore_or_throw(
                    context_baseline, context_restore_limits);
            },
            "restore ignored the aggregate context-entry ceiling",
            checks);

        SyncReplicaModelLimits predecessor_limits = base_limits();
        predecessor_limits.max_predecessor_ids = 1U;
        predecessor_limits.max_retained_predecessor_ids = 2U;
        SyncReplicaModel predecessor_model(
            folder, local_actor, predecessor_limits);
        require(
            predecessor_model.accept_remote_or_throw(pending_set[0]) ==
                    SyncReplicaAdmission::InsertedPending &&
                predecessor_model.accept_remote_or_throw(pending_set[1]) ==
                    SyncReplicaAdmission::InsertedPending,
            "predecessor-budget fixture did not retain its first two envelopes",
            checks);
        const SyncReplicaDurableState predecessor_baseline =
            predecessor_model.durable_state();
        require(
            predecessor_model.accept_remote_or_throw(pending_set[2]) ==
                SyncReplicaAdmission::CapacityBlocked,
            "aggregate predecessor-ID ceiling did not return retryable backpressure",
            checks);
        require(
            predecessor_model.durable_state() == predecessor_baseline &&
                predecessor_model.retained_predecessor_id_count() == 2U,
            "predecessor-budget rejection partially retained an envelope",
            checks);
        SyncReplicaModelLimits predecessor_restore_limits = predecessor_limits;
        predecessor_restore_limits.max_retained_predecessor_ids = 1U;
        require_throws<std::length_error>(
            [&] {
                (void)SyncReplicaModel::restore_or_throw(
                    predecessor_baseline, predecessor_restore_limits);
            },
            "restore ignored the aggregate predecessor-ID ceiling",
            checks);

        SyncReplicaModelLimits probe_limits = base_limits();
        const SyncReplicaActor mint_actor =
            actor("device-budget-mint", 740U);
        SyncReplicaModel probe(folder, mint_actor, probe_limits);
        const SyncReplicaOperation first_local =
            probe.create_local_file_or_throw(
                "budget/local.bin", 1U, sha256_hex("local-one"));
        const SyncReplicaDurableState first_local_state =
            probe.durable_state();
        const SyncReplicaOperation second_local =
            probe.create_local_file_or_throw(
                "budget/local.bin", 2U, sha256_hex("local-two"));

        SyncReplicaModelLimits local_limits = base_limits();
        local_limits.max_canonical_operation_bytes = std::max(
            canonical_size(first_local), canonical_size(second_local));
        local_limits.max_retained_canonical_bytes =
            local_limits.max_canonical_operation_bytes;
        SyncReplicaModel local_model = SyncReplicaModel::restore_or_throw(
            first_local_state, local_limits);
        const SyncReplicaDurableState local_baseline =
            local_model.durable_state();
        const std::uint64_t local_bytes =
            local_model.retained_canonical_bytes();
        const std::uint64_t local_contexts =
            local_model.retained_context_entry_count();
        const std::uint64_t local_predecessors =
            local_model.retained_predecessor_id_count();
        require_throws<std::length_error>(
            [&] {
                (void)local_model.create_local_file_or_throw(
                    "budget/local.bin", 2U, sha256_hex("local-two"));
            },
            "local mint crossed the aggregate canonical-byte ceiling",
            checks);
        require(
            local_model.durable_state() == local_baseline &&
                local_model.last_local_counter() == 1U &&
                local_model.retained_canonical_bytes() == local_bytes &&
                local_model.retained_context_entry_count() == local_contexts &&
                local_model.retained_predecessor_id_count() == local_predecessors,
            "rejected local mint changed authority or aggregate counters",
            checks);

        std::cout
            << "sync replica aggregate budget tests passed ("
            << checks
            << " checks, mixed-state exact bytes, restore, and local atomicity)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr
            << "sync replica aggregate budget tests failed: "
            << error.what() << '\n';
        return 1;
    }
}
