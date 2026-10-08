#include "sha256_digest.hpp"
#include "sync_replica_model.hpp"
#include "sync_replica_network_simulator.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace {

void require(bool condition, const std::string& message, int& checks) {
    if (!condition) throw std::runtime_error(message);
    ++checks;
}

template <typename Fn>
void require_throws(Fn&& fn, const std::string& message, int& checks) {
    bool threw = false;
    try {
        fn();
    } catch (const std::exception&) {
        threw = true;
    }
    require(threw, message, checks);
}

template <typename Fn>
void require_throws_containing(
    Fn&& fn,
    std::string_view expected_fragment,
    const std::string& message,
    int& checks) {
    bool matched = false;
    try {
        fn();
    } catch (const std::exception& error) {
        matched = std::string_view(error.what()).find(expected_fragment) !=
                  std::string_view::npos;
    }
    require(matched, message, checks);
}

anonsync::SyncReplicaActor actor(
    const std::string& device_id,
    std::uint64_t epoch = 1U) {
    return {device_id, epoch};
}

std::string payload_digest(const std::string& material) {
    return anonsync::sha256_hex(material);
}

void overwrite_u64_big_endian(
    std::string& bytes,
    std::size_t offset,
    std::uint64_t value) {
    if (offset > bytes.size() || bytes.size() - offset < 8U) {
        throw std::runtime_error("canonical test offset is out of range");
    }
    for (std::size_t index = 0; index < 8U; ++index) {
        const unsigned shift = static_cast<unsigned>((7U - index) * 8U);
        bytes[offset + index] =
            static_cast<char>((value >> shift) & 0xffU);
    }
}

std::size_t canonical_context_count_offset(
    const anonsync::SyncReplicaOperation& operation) {
    constexpr std::string_view magic =
        "anonsync-sync-replica-operation-v2";
    constexpr std::size_t framed_length_bytes = 8U;
    std::size_t offset = magic.size();
    const auto skip_string = [&](const std::string& value) {
        offset += framed_length_bytes + value.size();
    };
    skip_string(operation.folder_id);
    skip_string(operation.canonical_path);
    offset += 1U + 8U;
    skip_string(operation.content_sha256);
    skip_string(operation.dot.actor.device_id);
    offset += 8U + 8U;
    return offset;
}

anonsync::SyncReplicaOperation detached_file_operation(
    const std::string& folder,
    const std::string& path,
    const anonsync::SyncReplicaActor& operation_actor,
    std::uint64_t counter,
    std::vector<anonsync::SyncReplicaClockEntry> context,
    std::vector<std::string> predecessors,
    const std::string& payload) {
    std::sort(predecessors.begin(), predecessors.end());
    anonsync::SyncReplicaOperation operation;
    operation.folder_id = folder;
    operation.canonical_path = path;
    operation.kind = anonsync::SyncReplicaValueKind::File;
    operation.size_bytes = payload.size();
    operation.content_sha256 = payload_digest(payload);
    operation.dot = {operation_actor, counter};
    operation.causal_context = std::move(context);
    operation.predecessor_operation_ids = std::move(predecessors);
    operation.operation_id =
        anonsync::make_sync_replica_operation_id_or_throw(operation);
    return operation;
}

std::uint64_t message_for_operation_to_or_throw(
    const anonsync::SyncReplicaNetworkSimulator& simulator,
    const std::string& operation_id,
    const std::string& destination) {
    for (const std::uint64_t message_id : simulator.pending_message_ids()) {
        const auto message = simulator.message_by_id(message_id);
        if (message.has_value() &&
            message->operation.operation_id == operation_id &&
            message->destination_device_id == destination) {
            return message_id;
        }
    }
    throw std::runtime_error("expected queued operation message was absent");
}

struct XorShift64 final {
    std::uint64_t state = 0x9e3779b97f4a7c15ULL;

    std::uint64_t next() noexcept {
        std::uint64_t value = state;
        value ^= value << 13U;
        value ^= value >> 7U;
        value ^= value << 17U;
        state = value;
        return value;
    }

    std::size_t index(std::size_t bound) noexcept {
        return static_cast<std::size_t>(next() % bound);
    }
};

}  // namespace

int main() {
    using namespace anonsync;

    try {
        int checks = 0;
        const std::string folder = "folder-alpha";
        const std::string path = "docs/shared.txt";
        const SyncReplicaActor alpha = actor("device-alpha", 17U);
        const SyncReplicaActor bravo = actor("device-bravo", 23U);
        const SyncReplicaActor charlie = actor("device-charlie", 31U);
        const SyncReplicaActor delta = actor("device-delta", 41U);

        // Canonical bytes are the operation identity boundary. Decoding must
        // consume one exact bounded envelope and reproduce the same value.
        const SyncReplicaOperation canonical_root = detached_file_operation(
            folder, path, alpha, 1U, {}, {}, "canonical-root");
        const std::string canonical_bytes =
            encode_sync_replica_operation_canonical_or_throw(canonical_root);
        require(
            decode_sync_replica_operation_canonical_or_throw(canonical_bytes) ==
                canonical_root,
            "canonical operation encoding must round-trip exactly", checks);
        require(canonical_root.operation_id == sha256_hex(canonical_bytes),
                "operation identity must hash exact canonical bytes", checks);
        require_throws(
            [&] {
                (void)decode_sync_replica_operation_canonical_or_throw(
                    canonical_bytes.substr(0U, canonical_bytes.size() - 1U));
            },
            "truncated canonical envelopes must fail closed", checks);
        require_throws(
            [&] {
                (void)decode_sync_replica_operation_canonical_or_throw(
                    canonical_bytes + "x");
            },
            "canonical decoder must reject trailing bytes", checks);

        // Count fields are untrusted before allocation. Even permissive caller
        // limits must not let a tiny truncated envelope reserve a huge vector.
        SyncReplicaModelLimits hostile_count_limits;
        hostile_count_limits.max_operations = 100001U;
        hostile_count_limits.max_context_entries = 100000U;
        hostile_count_limits.max_predecessor_ids = 100000U;
        std::string impossible_context_count = canonical_bytes;
        const std::size_t context_count_offset =
            canonical_context_count_offset(canonical_root);
        overwrite_u64_big_endian(
            impossible_context_count, context_count_offset, 100000U);
        require_throws_containing(
            [&] {
                (void)decode_sync_replica_operation_canonical_or_throw(
                    impossible_context_count, hostile_count_limits);
            },
            "cannot fit in the remaining canonical bytes",
            "decoder must reject impossible context counts before vector reserve",
            checks);
        std::string impossible_predecessor_count = canonical_bytes;
        overwrite_u64_big_endian(
            impossible_predecessor_count,
            context_count_offset + 8U,
            100000U);
        require_throws_containing(
            [&] {
                (void)decode_sync_replica_operation_canonical_or_throw(
                    impossible_predecessor_count, hostile_count_limits);
            },
            "cannot fit in the remaining canonical bytes",
            "decoder must reject impossible predecessor counts before vector reserve",
            checks);
        SyncReplicaModelLimits tiny_envelope_limit;
        tiny_envelope_limit.max_canonical_operation_bytes =
            canonical_bytes.size() - 1U;
        require_throws(
            [&] {
                (void)encode_sync_replica_operation_canonical_or_throw(
                    canonical_root, tiny_envelope_limit);
            },
            "canonical encoding must enforce its byte budget before publication",
            checks);

        SyncReplicaOperation parent_identity_variant = canonical_root;
        parent_identity_variant.predecessor_operation_ids = {
            payload_digest("invented-parent")};
        parent_identity_variant.operation_id =
            make_sync_replica_operation_id_or_throw(parent_identity_variant);
        require(parent_identity_variant.operation_id !=
                    canonical_root.operation_id,
                "exact predecessor IDs must participate in operation identity",
                checks);
        SyncReplicaOperation unsorted_parents = parent_identity_variant;
        unsorted_parents.predecessor_operation_ids = {
            payload_digest("z-parent"), payload_digest("a-parent")};
        std::sort(
            unsorted_parents.predecessor_operation_ids.begin(),
            unsorted_parents.predecessor_operation_ids.end(),
            std::greater<>());
        require_throws(
            [&] {
                (void)make_sync_replica_operation_id_or_throw(
                    unsorted_parents);
            },
            "predecessor IDs must be canonical sorted unique hashes", checks);
        SyncReplicaOperation impossible_parent_cardinality = canonical_root;
        impossible_parent_cardinality.predecessor_operation_ids = {
            payload_digest("first-parent"), payload_digest("second-parent")};
        SyncReplicaModelLimits two_operation_limit;
        two_operation_limit.max_operations = 2U;
        two_operation_limit.max_predecessor_ids = 4U;
        require_throws(
            [&] {
                (void)make_sync_replica_operation_id_or_throw(
                    impossible_parent_cardinality, two_operation_limit);
            },
            "an operation must not name more exact parents than its retained-history budget can hold",
            checks);

        // Local minting binds the exact active graph heads, not merely a vector
        // summary. The second operation therefore carries the first operation's
        // hash as its immediate dependency.
        SyncReplicaModel alpha_model(folder, alpha);
        const SyncReplicaOperation alpha_first =
            alpha_model.create_local_file_or_throw(
                path, 5U, payload_digest("alpha"));
        const SyncReplicaOperation alpha_second =
            alpha_model.create_local_file_or_throw(
                path, 6U, payload_digest("alpha2"));
        require(alpha_first.dot.counter == 1U &&
                    alpha_first.causal_context.empty() &&
                    alpha_first.predecessor_operation_ids.empty(),
                "first local operation must be a canonical graph root", checks);
        require(alpha_second.dot.counter == 2U &&
                    alpha_second.causal_context ==
                        std::vector<SyncReplicaClockEntry>{{alpha, 1U}} &&
                    alpha_second.predecessor_operation_ids ==
                        std::vector<std::string>{alpha_first.operation_id},
                "successive local operation must bind its exact active head",
                checks);
        require(alpha_model.causal_head_operation_ids() ==
                    std::vector<std::string>{alpha_second.operation_id},
                "active graph must expose only maximal causal heads", checks);

        // Receiving a successor first retains evidence but does not grant the
        // absent predecessor's vector summary any active authority.
        SyncReplicaModel bravo_model(folder, bravo);
        require(bravo_model.accept_remote_or_throw(alpha_second) ==
                    SyncReplicaAdmission::InsertedPending,
                "successor without exact predecessor bytes must remain pending",
                checks);
        require(bravo_model.evidence_count() == 1U &&
                    bravo_model.operation_count() == 0U &&
                    bravo_model.pending_operation_count() == 1U &&
                    bravo_model.observed_context().empty() &&
                    bravo_model.missing_predecessor_operation_ids() ==
                        std::vector<std::string>{alpha_first.operation_id},
                "pending evidence must not contaminate the active frontier",
                checks);
        require(!bravo_model.visible_path(path).has_value(),
                "pending evidence must not enter visible state", checks);
        require(bravo_model.accept_remote_or_throw(alpha_second) ==
                    SyncReplicaAdmission::Duplicate,
                "pending evidence admission must remain idempotent", checks);
        require(bravo_model.accept_remote_or_throw(alpha_first) ==
                    SyncReplicaAdmission::InsertedActive,
                "late exact predecessor must be admitted as active", checks);
        require(bravo_model.operation_count() == 2U &&
                    bravo_model.pending_operation_count() == 0U &&
                    bravo_model.visible_path(path)->primary_operation_id ==
                        alpha_second.operation_id,
                "late predecessor must deterministically activate its successor",
                checks);

        // Crash/restart retains unresolved evidence and recomputes the same pure
        // projection rather than erasing inconvenient graph state.
        SyncReplicaModel pending_model(folder, delta);
        (void)pending_model.accept_remote_or_throw(alpha_second);
        const SyncReplicaDurableState pending_durable =
            pending_model.durable_state();
        SyncReplicaModel pending_restored =
            SyncReplicaModel::restore_or_throw(pending_durable);
        require(pending_restored.evidence_set_digest() ==
                    pending_model.evidence_set_digest() &&
                    pending_restored.pending_operation_count() == 1U &&
                    pending_restored.operation_count() == 0U,
                "durable restore must preserve pending exact evidence", checks);
        (void)pending_restored.accept_remote_or_throw(alpha_first);
        require(pending_restored.operation_count() == 2U,
                "restored pending graph must activate after dependency arrival",
                checks);

        // A coherent three-node graph must project identically under every
        // delivery permutation, including when the merge arrives first.
        const SyncReplicaOperation permutation_alpha =
            detached_file_operation(
                folder, "docs/permutation.txt", alpha, 1U, {}, {}, "pa");
        const SyncReplicaOperation permutation_bravo =
            detached_file_operation(
                folder, "docs/permutation.txt", bravo, 1U, {}, {}, "pb");
        const SyncReplicaOperation permutation_charlie =
            detached_file_operation(
                folder, "docs/permutation.txt", charlie, 1U,
                {{alpha, 1U}, {bravo, 1U}},
                {permutation_alpha.operation_id,
                 permutation_bravo.operation_id},
                "pc");
        const std::vector<SyncReplicaOperation> coherent_set = {
            permutation_alpha, permutation_bravo, permutation_charlie};
        std::vector<std::size_t> admission_order = {0U, 1U, 2U};
        std::optional<std::string> expected_evidence_digest;
        std::optional<std::string> expected_operation_digest;
        std::optional<std::string> expected_visible_digest;
        std::size_t permutations_checked = 0U;
        do {
            SyncReplicaModel model(folder, delta);
            for (const std::size_t index : admission_order) {
                (void)model.accept_remote_or_throw(coherent_set[index]);
            }
            require(model.evidence_count() == 3U &&
                        model.operation_count() == 3U &&
                        model.pending_operation_count() == 0U &&
                        model.quarantined_operation_count() == 0U,
                    "coherent graph must fully activate under every permutation",
                    checks);
            if (!expected_evidence_digest.has_value()) {
                expected_evidence_digest = model.evidence_set_digest();
                expected_operation_digest = model.operation_set_digest();
                expected_visible_digest = model.visible_state_digest();
            }
            require(model.evidence_set_digest() ==
                            expected_evidence_digest.value() &&
                        model.operation_set_digest() ==
                            expected_operation_digest.value() &&
                        model.visible_state_digest() ==
                            expected_visible_digest.value(),
                    "same exact graph must project independently of arrival order",
                    checks);
            ++permutations_checked;
        } while (std::next_permutation(
            admission_order.begin(), admission_order.end()));
        require(permutations_checked == 6U,
                "all three-operation delivery permutations must execute", checks);

        // Same-dot forks are retained as evidence and both sides are excluded.
        // The result must be the same even though each replica initially saw a
        // different side as active.
        SyncReplicaOperation alpha_fork = permutation_alpha;
        alpha_fork.content_sha256 = payload_digest("forked-alpha");
        alpha_fork.operation_id =
            make_sync_replica_operation_id_or_throw(alpha_fork);
        require(alpha_fork.operation_id != permutation_alpha.operation_id &&
                    alpha_fork.dot == permutation_alpha.dot,
                "fork fixture must bind different bytes under one dot", checks);

        SyncReplicaModel fork_left(folder, delta);
        SyncReplicaModel fork_right(folder, delta);
        require(fork_left.accept_remote_or_throw(permutation_alpha) ==
                    SyncReplicaAdmission::InsertedActive &&
                    fork_left.accept_remote_or_throw(alpha_fork) ==
                    SyncReplicaAdmission::InsertedQuarantined,
                "late fork must revoke first-observed active selection", checks);
        require(fork_right.accept_remote_or_throw(alpha_fork) ==
                    SyncReplicaAdmission::InsertedActive &&
                    fork_right.accept_remote_or_throw(permutation_alpha) ==
                    SyncReplicaAdmission::InsertedQuarantined,
                "opposite fork arrival must reach the same quarantine", checks);
        require(fork_left.operation_count() == 0U &&
                    fork_left.evidence_count() == 2U &&
                    fork_left.quarantined_operation_count() == 2U &&
                    fork_left.evidence_state(permutation_alpha.operation_id) ==
                        SyncReplicaEvidenceState::QuarantinedDotFork &&
                    fork_left.evidence_state(alpha_fork.operation_id) ==
                        SyncReplicaEvidenceState::QuarantinedDotFork,
                "both same-dot envelopes must be retained but inactive", checks);
        require(fork_left.operation_set_digest() ==
                        fork_right.operation_set_digest() &&
                    fork_left.evidence_set_digest() ==
                        fork_right.evidence_set_digest() &&
                    fork_left.visible_state_digest() ==
                        fork_right.visible_state_digest(),
                "same fork evidence must converge despite opposite first observation",
                checks);

        const SyncReplicaOperation fork_descendant = detached_file_operation(
            folder, "docs/permutation.txt", bravo, 1U,
            {{alpha, 1U}}, {permutation_alpha.operation_id}, "descendant");
        (void)fork_left.accept_remote_or_throw(fork_descendant);
        (void)fork_right.accept_remote_or_throw(fork_descendant);
        require(fork_left.evidence_state(fork_descendant.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDependency &&
                    fork_right.evidence_state(fork_descendant.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDependency,
                "descendants of quarantined evidence must fail closed", checks);

        // A known bad parent dominates an unrelated absent parent. Otherwise a
        // child that can never activate would remain "pending" and make a
        // dependency fetcher chase attacker-chosen hashes forever.
        const std::string never_needed_parent =
            payload_digest("never-needed-after-fork");
        const SyncReplicaOperation fork_and_missing_child =
            detached_file_operation(
                folder, "docs/mixed-dependency.txt", charlie, 1U,
                {{alpha, 1U}},
                {permutation_alpha.operation_id, never_needed_parent},
                "mixed-dependency");
        std::vector<std::string> initially_missing = {
            never_needed_parent, permutation_alpha.operation_id};
        std::sort(initially_missing.begin(), initially_missing.end());
        SyncReplicaModel mixed_dependency_guard(folder, delta);
        require(
            mixed_dependency_guard.accept_remote_or_throw(
                fork_and_missing_child) ==
                    SyncReplicaAdmission::InsertedPending &&
                mixed_dependency_guard.missing_predecessor_operation_ids() ==
                    initially_missing,
            "fully absent mixed dependency must begin pending with exact requests",
            checks);
        (void)mixed_dependency_guard.accept_remote_or_throw(permutation_alpha);
        require(
            mixed_dependency_guard.evidence_state(
                fork_and_missing_child.operation_id) ==
                    SyncReplicaEvidenceState::PendingMissingDependency &&
                mixed_dependency_guard.missing_predecessor_operation_ids() ==
                    std::vector<std::string>{never_needed_parent},
            "one remaining viable dependency must keep the child pending", checks);
        (void)mixed_dependency_guard.accept_remote_or_throw(alpha_fork);
        require(
            mixed_dependency_guard.evidence_state(
                fork_and_missing_child.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDependency &&
                mixed_dependency_guard.pending_operation_count() == 0U &&
                mixed_dependency_guard.missing_predecessor_operation_ids()
                    .empty(),
            "known fork quarantine must dominate absence and suppress impossible dependency requests",
            checks);

        // A fork in this process's own minting namespace closes local authority,
        // survives restart, and requires explicit epoch rotation to resume.
        SyncReplicaModel local_guard(folder, alpha);
        const SyncReplicaOperation authorized_local =
            local_guard.create_local_file_or_throw(
                "docs/local.txt", 5U, payload_digest("local"));
        SyncReplicaOperation local_fork = authorized_local;
        local_fork.content_sha256 = payload_digest("local-fork");
        local_fork.operation_id =
            make_sync_replica_operation_id_or_throw(local_fork);
        require(local_guard.accept_remote_or_throw(local_fork) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                    local_guard.local_actor_compromised(),
                "observed local-dot fork must fail minting authority closed",
                checks);
        require_throws(
            [&] {
                (void)local_guard.create_local_tombstone_or_throw(
                    "docs/blocked.txt");
            },
            "compromised local actor epoch must not mint again", checks);
        SyncReplicaModel local_guard_restored =
            SyncReplicaModel::restore_or_throw(local_guard.durable_state());
        require(local_guard_restored.local_actor_compromised() &&
                    local_guard_restored.quarantined_operation_count() == 2U,
                "local fork evidence and fail-closed authority must survive restart",
                checks);

        // Local authority is an evidence namespace, not an applicability test.
        // A forged future/local dot cannot remain harmless merely because its
        // invented predecessor is absent and therefore keeps it pending.
        const SyncReplicaOperation pending_local_namespace_reuse =
            detached_file_operation(
                folder, "docs/local-pending.txt", alpha, 1U, {},
                {payload_digest("missing-local-predecessor")},
                "foreign-local-dot");
        SyncReplicaModel pending_local_guard(folder, alpha);
        require(
            pending_local_guard.accept_remote_or_throw(
                pending_local_namespace_reuse) ==
                    SyncReplicaAdmission::InsertedPending &&
                pending_local_guard.local_actor_compromised(),
            "any unrecognized retained envelope in the local actor epoch must close minting authority",
            checks);
        require_throws(
            [&] {
                (void)pending_local_guard.create_local_file_or_throw(
                    "docs/must-not-mint.txt", 1U, payload_digest("blocked"));
            },
            "pending local-namespace reuse must block minting before a dot collision",
            checks);
        require(
            SyncReplicaModel::restore_or_throw(
                pending_local_guard.durable_state())
                .local_actor_compromised(),
            "pending local-namespace compromise must survive restart", checks);
        SyncReplicaModel rotated(folder, actor("device-alpha", 18U));
        require(rotated.create_local_tombstone_or_throw("docs/resumed.txt")
                        .dot.counter == 1U,
                "explicit epoch rotation must create a disjoint minting namespace",
                checks);

        // Vector summaries that cannot be derived exactly from immediate active
        // parents are retained but quarantined. They never become frontiers by
        // virtue of sounding causally plausible.
        const SyncReplicaOperation extra_context = detached_file_operation(
            folder, "docs/envelope.txt", charlie, 1U,
            {{alpha, 1U}, {bravo, 1U}},
            {permutation_alpha.operation_id}, "extra-context");
        SyncReplicaModel envelope_guard(folder, delta);
        (void)envelope_guard.accept_remote_or_throw(permutation_alpha);
        require(envelope_guard.accept_remote_or_throw(extra_context) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                    envelope_guard.evidence_state(extra_context.operation_id) ==
                        SyncReplicaEvidenceState::QuarantinedCausalEnvelope &&
                    envelope_guard.operation_count() == 1U,
                "unearned vector context must be quarantined", checks);

        const SyncReplicaOperation no_parent_claim = detached_file_operation(
            folder, "docs/envelope.txt", actor("device-echo", 51U), 1U,
            {{alpha, 1U}}, {}, "no-parent-claim");
        require(envelope_guard.accept_remote_or_throw(no_parent_claim) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                    envelope_guard.evidence_state(no_parent_claim.operation_id) ==
                        SyncReplicaEvidenceState::QuarantinedCausalEnvelope,
                "causal claims without exact parent hashes must not activate",
                checks);

        const SyncReplicaOperation dependent_on_quarantine =
            detached_file_operation(
                folder, "docs/envelope.txt", delta, 1U,
                {{alpha, 1U}, {bravo, 1U}, {charlie, 1U}},
                {extra_context.operation_id}, "dependent");
        require(
            envelope_guard.accept_remote_or_throw(dependent_on_quarantine) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                envelope_guard.evidence_state(
                    dependent_on_quarantine.operation_id) ==
                    SyncReplicaEvidenceState::QuarantinedDependency,
            "quarantine must propagate through exact dependency edges", checks);

        const SyncReplicaOperation transitive_child = detached_file_operation(
            folder, "docs/minimal.txt", bravo, 1U,
            {{alpha, 1U}}, {permutation_alpha.operation_id}, "child");
        const SyncReplicaOperation redundant_merge = detached_file_operation(
            folder, "docs/minimal.txt", charlie, 1U,
            {{alpha, 1U}, {bravo, 1U}},
            {permutation_alpha.operation_id, transitive_child.operation_id},
            "redundant");
        SyncReplicaModel minimal_guard(folder, delta);
        (void)minimal_guard.accept_remote_or_throw(permutation_alpha);
        (void)minimal_guard.accept_remote_or_throw(transitive_child);
        require(minimal_guard.accept_remote_or_throw(redundant_merge) ==
                    SyncReplicaAdmission::InsertedQuarantined &&
                    minimal_guard.evidence_state(redundant_merge.operation_id) ==
                        SyncReplicaEvidenceState::QuarantinedCausalEnvelope,
                "immediate predecessor set must contain only causal heads",
                checks);

        const std::string before_wrong_folder =
            minimal_guard.evidence_set_digest();
        SyncReplicaOperation wrong_folder = permutation_bravo;
        wrong_folder.folder_id = "folder-other";
        wrong_folder.operation_id =
            make_sync_replica_operation_id_or_throw(wrong_folder);
        require_throws(
            [&] {
                (void)minimal_guard.accept_remote_or_throw(wrong_folder);
            },
            "cross-folder evidence must be rejected", checks);
        require(minimal_guard.evidence_set_digest() == before_wrong_folder,
                "failed envelope admission must be failure-atomic", checks);

        // Network delivery may reorder a local chain. The destination retains
        // the child pending, then activates it when the parent arrives. Durable
        // crash/restart in between must not change that result.
        SyncReplicaNetworkSimulator network("folder-network");
        network.add_replica_or_throw(actor("device-a", 101U));
        network.add_replica_or_throw(actor("device-b", 102U));
        const SyncReplicaOperation network_first =
            network.create_local_file_or_throw(
                "device-a", "docs/ordered.txt", 1U, payload_digest("one"));
        const SyncReplicaOperation network_second =
            network.create_local_file_or_throw(
                "device-a", "docs/ordered.txt", 2U, payload_digest("two"));
        const std::uint64_t second_message =
            message_for_operation_to_or_throw(
                network, network_second.operation_id, "device-b");
        require(network.deliver_message_or_throw(second_message) ==
                    SyncReplicaAdmission::InsertedPending &&
                    network.replica_or_throw("device-b").operation_count() == 0U,
                "reordered child delivery must remain pending", checks);
        network.crash_or_throw("device-b");
        network.restart_or_throw("device-b");
        require(network.replica_or_throw("device-b")
                        .pending_operation_count() == 1U,
                "network durable cutpoint must retain pending evidence", checks);
        const std::uint64_t first_message =
            message_for_operation_to_or_throw(
                network, network_first.operation_id, "device-b");
        require(network.deliver_message_or_throw(first_message) ==
                    SyncReplicaAdmission::InsertedActive &&
                    network.replica_or_throw("device-b").operation_count() == 2U,
                "parent delivery must activate reordered network chain", checks);
        (void)network.enqueue_full_mesh_anti_entropy_or_throw();
        (void)network.drain_deliverable_or_throw(
            SyncReplicaDeliveryOrder::NewestFirst);
        require(network.all_evidence_sets_equal_or_throw() &&
                    network.all_operation_sets_equal_or_throw() &&
                    network.all_visible_states_equal_or_throw(),
                "anti-entropy must converge evidence, projection, and visibility",
                checks);

        // Deterministic generated history combines partitions, loss, duplicate
        // frames, reorder, and crash/restart. Eventual all-evidence anti-entropy
        // must converge every live replica on every generated operation.
        const std::vector<std::string> devices = {
            "device-a", "device-b", "device-c", "device-d"};
        const std::vector<std::string> paths = {
            "docs/a.txt", "docs/b.txt", "docs/c.txt",
            "images/d.bin", "notes/e.md"};
        SyncReplicaModelLimits stress_limits;
        stress_limits.max_operations = 600U;
        stress_limits.max_context_entries = 32U;
        stress_limits.max_predecessor_ids = 32U;
        SyncReplicaNetworkSimulator stress(
            "folder-stress", stress_limits);
        for (std::size_t index = 0; index < devices.size(); ++index) {
            stress.add_replica_or_throw(
                actor(devices[index], 200U + index));
        }

        XorShift64 random;
        std::set<std::string> generated_operation_ids;
        for (std::size_t step = 0; step < 420U; ++step) {
            const std::size_t action = random.index(9U);
            const std::size_t selected_index =
                random.index(devices.size());
            const std::string& selected = devices[selected_index];
            const std::size_t other_offset =
                1U + random.index(devices.size() - 1U);
            const std::string& other =
                devices[(selected_index + other_offset) % devices.size()];

            if (action <= 2U) {
                if (!stress.replica_is_live(selected)) continue;
                const std::string& selected_path =
                    paths[random.index(paths.size())];
                SyncReplicaOperation operation;
                if (action == 2U) {
                    operation = stress.create_local_tombstone_or_throw(
                        selected, selected_path);
                } else {
                    const std::string material =
                        selected + ":" + std::to_string(step) + ":" +
                        std::to_string(random.next());
                    operation = stress.create_local_file_or_throw(
                        selected, selected_path, material.size(),
                        payload_digest(material));
                }
                generated_operation_ids.insert(operation.operation_id);
            } else if (action == 3U) {
                stress.partition_direction_or_throw(selected, other);
            } else if (action == 4U) {
                stress.heal_direction_or_throw(selected, other);
            } else if (action == 5U) {
                const std::vector<std::uint64_t> pending =
                    stress.pending_message_ids();
                if (!pending.empty()) {
                    const std::uint64_t message_id =
                        pending[random.index(pending.size())];
                    if ((random.next() & 1U) == 0U) {
                        (void)stress.duplicate_message_or_throw(message_id);
                    } else {
                        (void)stress.drop_message(message_id);
                    }
                }
            } else if (action == 6U) {
                const std::vector<std::uint64_t> pending =
                    stress.pending_message_ids();
                if (!pending.empty()) {
                    const std::uint64_t message_id =
                        pending[random.index(pending.size())];
                    (void)stress.deliver_message_or_throw(message_id);
                }
            } else if (action == 7U) {
                if (stress.replica_is_live(selected)) {
                    stress.crash_or_throw(selected);
                } else {
                    stress.restart_or_throw(selected);
                }
            } else {
                (void)stress.drain_deliverable_or_throw(
                    (random.next() & 1U) == 0U
                        ? SyncReplicaDeliveryOrder::OldestFirst
                        : SyncReplicaDeliveryOrder::NewestFirst,
                    3U);
            }
        }

        for (const std::string& device : devices) {
            if (!stress.replica_is_live(device)) {
                stress.restart_or_throw(device);
            }
        }
        stress.heal_all();
        (void)stress.enqueue_full_mesh_anti_entropy_or_throw();
        (void)stress.drain_deliverable_or_throw(
            SyncReplicaDeliveryOrder::NewestFirst);
        (void)stress.enqueue_full_mesh_anti_entropy_or_throw();
        (void)stress.drain_deliverable_or_throw(
            SyncReplicaDeliveryOrder::OldestFirst);
        require(stress.all_replicas_live() &&
                    stress.pending_message_count() == 0U,
                "stress convergence must finish live with an empty queue", checks);
        require(stress.all_evidence_sets_equal_or_throw() &&
                    stress.all_operation_sets_equal_or_throw() &&
                    stress.all_visible_states_equal_or_throw(),
                "faulted exact-evidence history must converge after healing",
                checks);
        require(generated_operation_ids.size() >= 40U,
                "stress history must generate a nontrivial operation graph",
                checks);
        for (const std::string& device : devices) {
            const SyncReplicaModel& replica =
                stress.replica_or_throw(device);
            require(replica.evidence_count() ==
                            generated_operation_ids.size() &&
                        replica.operation_count() ==
                            generated_operation_ids.size() &&
                        replica.pending_operation_count() == 0U &&
                        replica.quarantined_operation_count() == 0U,
                    "every stress replica must retain and activate every honest generated operation",
                    checks);
        }

        std::cout << "sync replica network model tests passed (" << checks
                  << " checks, " << generated_operation_ids.size()
                  << " generated operations)\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "sync replica network model tests failed: "
                  << error.what() << '\n';
        return 1;
    }
}
